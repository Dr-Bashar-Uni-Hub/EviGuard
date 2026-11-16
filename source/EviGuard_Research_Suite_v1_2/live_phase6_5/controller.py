#!/usr/bin/env python3
"""Live event-informed observer; deliberately not a claim of novel CACV logic."""
import argparse, json, os, subprocess, time, signal, hashlib
from shadow_baseline import SnapshotTemporalReference
from pathlib import Path

def cmd(*args):
    p=subprocess.run(args,text=True,capture_output=True)
    if p.returncode: raise RuntimeError(f'{args}: {p.stderr}')
    return p.stdout

def read_events(path):
    if not path.exists(): return []
    out=[]
    for line in path.read_text().splitlines():
        try: out.append(json.loads(line))
        except json.JSONDecodeError: pass
    return out

def observation(a):
    events=read_events(Path(a.events)); last=events[-1] if events else {}
    addrs=json.loads(cmd('ip','-n',a.client,'-j','addr','show','dev',a.client_if))
    ip_present=any(x.get('local')==a.ip for d in addrs for x in d.get('addr_info',[]))
    neigh=json.loads(cmd('ip','-n',a.server,'-j','neigh','show','dev',a.server_if))
    neighbor=[n for n in neigh if n.get('dst')==a.ip]
    def usable_neighbor(n):
        raw = n.get('state', '')
        states = [str(s).upper() for s in raw] if isinstance(raw, list) else [str(raw).upper()]
        return (str(n.get('lladdr') or '').lower() == a.mac.lower()
                and bool(states) and all(s not in ('FAILED', 'INCOMPLETE', '') for s in states))
    arp_present = any(usable_neighbor(n) for n in neighbor)
    leases=Path(a.leases).read_text().splitlines() if Path(a.leases).exists() else []
    lease_present=any(len(parts:=line.split())>=3 and parts[1].lower()==a.mac.lower() and parts[2]==a.ip and int(parts[0])>time.time() for line in leases)
    bound=last.get('kind') in ('bound','renew') and last.get('ip')==a.ip
    return {'time_ns':time.time_ns(),'last_event':last,'event_count':len(events),'bound':bound,'lease_present':lease_present,'ip_present':ip_present,'arp_present':arp_present,'neighbor':neighbor,'mac':a.mac,'ip':a.ip}

def install(a,allow):
    # Drop by default for the protected UDP service, then allow only a validated client.
    script='flush chain inet eviguard input\n'
    if allow: script+=f'add rule inet eviguard input ip saddr {a.ip} udp dport 9900 counter accept\n'
    script+='add rule inet eviguard input udp dport 9900 counter drop\n'
    p=subprocess.run(['ip','netns','exec',a.server,'nft','-f','-'],input=script,text=True,capture_output=True)
    if p.returncode: raise RuntimeError(p.stderr)
    rules=cmd('ip','netns','exec',a.server,'nft','-a','list','chain','inet','eviguard','input')
    return rules

def main():
    p=argparse.ArgumentParser()
    for name in ('client','server','client-if','server-if','events','leases','ip','mac','out'):
        p.add_argument('--'+name,required=True)
    p.add_argument('--interval',type=float,default=.08)
    a=p.parse_args(); out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    last=None
    shadow=SnapshotTemporalReference()
    shadow_path=out.parent / "shadow_comparison.jsonl"
    shadow_file=shadow_path.open("w", buffering=1)
    with out.open('w',buffering=1) as f:
        while True:
            o=observation(a)
            # Three observations must agree. No time/epoch originality is claimed.
            allow=all(o[k] for k in ('bound','lease_present','ip_present','arp_present'))
            reference_allow=shadow.evaluate(o)
            canonical=json.dumps(o,sort_keys=True,separators=(',',':'))
            shadow_file.write(json.dumps({'snapshot_sha256':hashlib.sha256(canonical.encode()).hexdigest(),
                'observation':o,'eviguard_allow':allow,'reference_allow':reference_allow,
                'agreement':allow==reference_allow,'recorded_ns':time.time_ns()})+'\n')
            state=(allow,o['event_count'],o['lease_present'],o['ip_present'],o['arp_present'])
            if state!=last:
                rules=install(a,allow) if last is None or allow!=last[0] else cmd('ip','netns','exec',a.server,'nft','-a','list','chain','inet','eviguard','input')
                f.write(json.dumps({'kind':'transition','observation':o,'allow':allow,'rules':rules,'ack_ns':time.time_ns()})+'\n')
                last=state
            time.sleep(a.interval)
if __name__=='__main__': main()
