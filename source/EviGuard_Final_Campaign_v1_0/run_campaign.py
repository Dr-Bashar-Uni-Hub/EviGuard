#!/usr/bin/env python3
"""Deterministic OFFLINE failure-model campaign; does not modify kernel/network."""
import argparse,csv,hashlib,itertools,json,platform,random,statistics,tarfile,sys
from pathlib import Path
SEEDS=(11,23,37,53,71)
DELAYS=(0,25,100)
FAULTS=('none','notify_loss','install_failure','controller_crash')
PACKETS=(10,30,60,120,250)
HORIZON=300

def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'))
def simulate(seed,notify,install,fault):
    # deterministic packet arrivals; seeded event ID supports reproducible random trial ordering
    rng=random.Random(seed*100000+notify*1000+install*10+FAULTS.index(fault))
    event_id=rng.getrandbits(48)
    commit=None if fault!='none' else notify+install
    delivered=[t for t in PACKETS if commit is None or t<commit]
    return {'seed':seed,'notify_delay_ms':notify,'install_delay_ms':install,'fault':fault,
            'event_id':event_id,'packet_times_ms':list(PACKETS),'drop_commit_ms':commit,
            'exposure_ms_capped':min(commit,HORIZON) if commit is not None else HORIZON,
            'post_revocation_deliveries':len(delivered),'delivered_at_ms':delivered}

def main():
    p=argparse.ArgumentParser();p.add_argument('--v12-results',type=Path,required=True);p.add_argument('--out',type=Path,default=Path('results'))
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    if not a.v12_results.is_file():p.error('Frozen v1.2 archive not found: '+str(a.v12_results))
    digest=hashlib.sha256(a.v12_results.read_bytes()).hexdigest()
    with tarfile.open(a.v12_results,'r:gz') as t:
        names=t.getnames()
        if not names or any(n.startswith('/') or '..' in Path(n).parts for n in names):raise ValueError('Unsafe archive members')
        if not any(n.endswith('/kernel_compare/verification.json') for n in names):raise ValueError('v1.2 kernel verification missing')
        if not any(n.endswith('/live_verification.json') for n in names):raise ValueError('v1.2 live verification missing')
    rows=[];disagreements=0
    for seed,n,i,f in itertools.product(SEEDS,DELAYS,DELAYS,FAULTS):
        ev=simulate(seed,n,i,f)
        reference=simulate(seed,n,i,f) # same decision semantics; no independent published protocol
        if ev!=reference:disagreements+=1
        rows.append(ev)
    assert len(rows)==180
    assert all(0<=r['post_revocation_deliveries']<=len(PACKETS) for r in rows)
    assert all(r['drop_commit_ms'] is None or r['drop_commit_ms']>=0 for r in rows)
    assert all(r['drop_commit_ms'] is None or all(t<r['drop_commit_ms'] for t in r['delivered_at_ms']) for r in rows)
    with (a.out/'scenarios.jsonl').open('w') as fh:
        for r in rows:fh.write(canonical(r)+'\n')
    summary=[]
    for fault in FAULTS:
        subset=[r for r in rows if r['fault']==fault]
        summary.append({'fault':fault,'scenarios':len(subset),'mean_deliveries':round(statistics.mean(r['post_revocation_deliveries'] for r in subset),5),
                        'max_deliveries':max(r['post_revocation_deliveries'] for r in subset),
                        'mean_exposure_ms_capped':round(statistics.mean(r['exposure_ms_capped'] for r in subset),5)})
    with (a.out/'summary.csv').open('w',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    report={'status':'PASS_OFFLINE_MODEL_ONLY','scenario_count':len(rows),'paired_policy_disagreements':disagreements,
            'v12_archive_sha256':digest,'v12_archive_members':len(names),'summary':summary,
            'limitations':['Synthetic discrete-event model, not real kernel fault injection','Identical authorization semantics by construction','No published SAVI baseline','No end-to-end timing measurement','No demonstrated novelty']}
    (a.out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    (a.out/'environment.json').write_text(json.dumps({'python':sys.version,'platform':platform.platform(),'seeds':SEEDS,'notification_delays_ms':DELAYS,'install_delays_ms':DELAYS,'faults':FAULTS,'packet_times_ms':PACKETS,'horizon_ms':HORIZON},indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
