import json,sys
from pathlib import Path
p=Path(sys.argv[1]);read=lambda n:[json.loads(x) for x in (p/n).read_text().splitlines() if x.strip()]
events=read('events.jsonl'); trans=read('transitions.jsonl'); rec=read('received.jsonl'); sent=read('continuous_sent.jsonl'); checkpoints=read('checkpoints.jsonl')
counts={k:sum(r['message'].startswith(k+':') for r in rec) for k in ('prelease','authorized','revoked','rebound_blocked','rebound_authorized','final_revoked')}
expected={'prelease':0,'authorized':10,'revoked':0,'rebound_blocked':0,'rebound_authorized':10,'final_revoked':0}
errors=[f'{k}: expected {v}, observed {counts[k]}' for k,v in expected.items() if counts[k]!=v]
if sum(e.get('kind')=='bound' and e.get('origin')=='udhcpc-hook' for e in events)<2: errors.append('Fewer than two real DHCP bound callbacks')
if sum(t['allow'] for t in trans)<2: errors.append('Fewer than two allow transitions')
if len(sent)<30: errors.append('Insufficient continuous traffic')
if len(checkpoints)<6: errors.append('Missing checkpoints')
result={'status':'FAIL' if errors else 'PASS','probe_counts':counts,'continuous_sent_records':len(sent),'continuous_delivered':sum(r['message'].startswith('continuous:') for r in rec),'checkpoints':checkpoints,'errors':errors,'limitations':['Single client; controlled deconfig event','Continuous send/receive userspace timestamps cannot prove exact kernel boundary safety','No independently implemented matched-information baseline','ARP neighbor evidence is not authenticated','PASS validates checkpoint delivery, not asynchronous atomicity or novelty']}
(p/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));sys.exit(bool(errors))
