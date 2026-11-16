#!/usr/bin/env python3
"""Root-only independent namespace kernel-enforcement replay of recorded live snapshots.
Not concurrent live-controller comparison; snapshots are collected in a preceding live run.
"""
import argparse, json, os, subprocess, time, signal, hashlib, statistics
from pathlib import Path
from collections import defaultdict
from live_phase6_5.shadow_baseline import SnapshotTemporalReference

def run(*cmd, input=None):
    p=subprocess.run(cmd,input=input,text=True,capture_output=True)
    if p.returncode: raise RuntimeError(f'{cmd}: {p.stderr}')
    return p.stdout

def eviguard(s):
    return bool(s.get('bound') and s.get('lease_present') and s.get('ip_present') and s.get('arp_present'))

def nft_set(ns, allow, addr):
    script='flush chain inet compare input\n'
    if allow: script+=f'add rule inet compare input ip saddr {addr} udp dport 9900 counter accept\n'
    script+='add rule inet compare input udp dport 9900 counter drop\n'
    start=time.monotonic_ns()
    run('ip','netns','exec',ns,'nft','-f','-',input=script)
    ack=time.monotonic_ns()
    rules=run('ip','netns','exec',ns,'nft','-j','list','chain','inet','compare','input')
    return ack-start, json.loads(rules)

def count_packets(ns):
    obj=json.loads(run('ip','netns','exec',ns,'nft','-j','list','chain','inet','compare','input'))
    totals={'accept':0,'drop':0}
    for entry in obj.get('nftables',[]):
        rule=entry.get('rule',{})
        expr=rule.get('expr',[])
        verdict=next((k for e in expr for k in ('accept','drop') if k in e),None)
        if verdict:
            totals[verdict]+=sum(e['counter'].get('packets',0) for e in expr if 'counter' in e)
    return totals

def main():
    a=argparse.ArgumentParser();a.add_argument('--snapshots',required=True);a.add_argument('--out',required=True);a.add_argument('--limit',type=int,default=0);args=a.parse_args()
    if os.geteuid(): raise SystemExit('Run with sudo')
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    source=Path(args.snapshots).resolve()
    raw=[json.loads(line) for line in source.read_text().splitlines() if line.strip()]
    # Keep all transitions in the captured stream; optional cap for debugging.
    if args.limit: raw=raw[:args.limit]
    if not raw: raise RuntimeError('No live observations')
    records=[]; ref=SnapshotTemporalReference()
    for idx,entry in enumerate(raw):
        obs=entry['observation']; canonical=json.dumps(obs,sort_keys=True,separators=(',',':'))
        if hashlib.sha256(canonical.encode()).hexdigest()!=entry['snapshot_sha256']:
            raise RuntimeError(f'Snapshot hash mismatch {idx}')
        records.append((obs,eviguard(obs),ref.evaluate(obs)))
    # Reduce redundant observations for kernel tests; preserve every state transition,
    # plus first and last observation, while audit checks ALL snapshots above.
    selected=[];prev=None
    for i,(obs,x,y) in enumerate(records):
        key=(x,y,obs.get('event_count'),obs.get('lease_present'),obs.get('ip_present'),obs.get('arp_present'))
        if i==0 or key!=prev or i==len(records)-1:selected.append((i,obs,x,y))
        prev=key
    (out/'selection.json').write_text(json.dumps({'source':str(source),'snapshots':len(records),'selected':len(selected),'selected_indices':[x[0] for x in selected]},indent=2))
    token=str(os.getpid()%100000)
    specs=[('eviguard',f'e{token}c',f'e{token}s',f'e{token}a',f'e{token}b','10.88.1.2','10.88.1.1'),('temporal',f't{token}c',f't{token}s',f't{token}a',f't{token}b','10.88.2.2','10.88.2.1')]
    created=[];procs=[];logs={};errors=[];rows=[]
    try:
        for name,client,server,vc,vs,src,dst in specs:
            for ns in (client,server):run('ip','netns','add',ns);created.append(ns);run('ip','-n',ns,'link','set','lo','up')
            run('ip','link','add',vc,'type','veth','peer','name',vs)
            run('ip','link','set',vc,'netns',client);run('ip','link','set',vs,'netns',server)
            for ns,dev,ip in ((client,vc,src),(server,vs,dst)):
                run('ip','-n',ns,'addr','add',ip+'/24','dev',dev)
                run('ip','-n',ns,'link','set',dev,'up')
            run('ip','netns','exec',server,'nft','-f','-',input='add table inet compare\nadd chain inet compare input { type filter hook input priority 0; policy accept; }\nadd rule inet compare input udp dport 9900 counter drop\n')
            logfile=(out/f'{name}_received.jsonl').open('w',buffering=1);logs[name]=logfile
            # Python receiver uses fixed port and server address supplied via -c.
            code='import socket,sys,json,time\ns=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.bind((sys.argv[1],9900))\nwhile True:\n data,addr=s.recvfrom(4096);print(json.dumps({"time_ns":time.monotonic_ns(),"message":data.decode(),"source":addr[0]}),flush=True)'
            procs.append(subprocess.Popen(['ip','netns','exec',server,'python3','-u','-c',code,dst],stdout=logfile,stderr=subprocess.PIPE))
        time.sleep(.4)
        for trial,(idx,obs,eg,tf) in enumerate(selected):
            # Alternate execution order to reduce systematic order bias.
            order=specs if trial%2==0 else list(reversed(specs))
            for name,client,server,vc,vs,src,dst in order:
                decision=eg if name=='eviguard' else tf
                latency,rules=nft_set(server,decision,src)
                before=count_packets(server)
                label=f'{name}_{trial:04d}'
                code='import socket,sys,time\ns=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)\nfor i in range(3):s.sendto((sys.argv[1]+":"+str(i)).encode(),(sys.argv[2],9900));time.sleep(.015)'
                run('ip','netns','exec',client,'python3','-c',code,label,dst)
                time.sleep(.08)
                after=count_packets(server)
                delta={k:after[k]-before[k] for k in before}
                rows.append({'snapshot_index':idx,'trial':trial,'policy':name,'allow':decision,'rule_ack_latency_ns':latency,'kernel_accept_delta':delta['accept'],'kernel_drop_delta':delta['drop'],'label':label,'snapshot_hash':raw[idx]['snapshot_sha256']})
        time.sleep(.3)
    finally:
        for p in procs:
            p.terminate()
            try:p.wait(timeout=2)
            except subprocess.TimeoutExpired:p.kill();p.wait()
        for f in logs.values():f.close()
        for ns in reversed(created):subprocess.run(['ip','netns','del',ns],capture_output=True)
    received={name:[json.loads(line) for line in (out/f'{name}_received.jsonl').read_text().splitlines() if line.strip()] for name,*_ in specs}
    for row in rows:
        n=row['policy'];actual=sum(r['message'].startswith(row['label']+':') for r in received[n]);row['received']=actual
        expected=3 if row['allow'] else 0
        if actual!=expected:errors.append(f"{n} trial {row['trial']}: delivered {actual}, expected {expected}")
        if row['kernel_accept_delta']!=(3 if row['allow'] else 0) or row['kernel_drop_delta']!=(0 if row['allow'] else 3):
            errors.append(f"{n} trial {row['trial']}: unexpected kernel counters")
    mismatches=sum(x!=y for _,x,y in records)
    if mismatches:errors.append(f'{mismatches} decision disagreements in live snapshots')
    by=defaultdict(list)
    for row in rows:by[row['policy']].append(row['rule_ack_latency_ns'])
    result={'status':'PASS' if not errors else 'FAIL','live_snapshots':len(records),'decision_disagreements':mismatches,'selected_kernel_checkpoints':len(selected),'kernel_trials':len(rows),'packets_sent':len(rows)*3,'packets_delivered':sum(r['received'] for r in rows),'per_policy':{k:{'trials':len(v),'median_rule_ack_ns':statistics.median(v)} for k,v in by.items()},'errors':errors,'limitations':['Recorded real observations are replayed at checkpoints, not concurrently processed by two independent live polling controllers','The independently enforced policies are logically equivalent by design','Synthetic matched policy rules, not a published versioned-fencing protocol','Rule acknowledgments and kernel counters do not establish exact boundary safety','No originality or security advantage demonstrated by agreement']}
    (out/'kernel_trials.json').write_text(json.dumps(rows,indent=2)+'\n')
    (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
