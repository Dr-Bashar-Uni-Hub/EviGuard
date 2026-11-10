import argparse,json,socket,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('out');p.add_argument('--duration',type=float,default=12);p.add_argument('--interval',type=float,default=.02);a=p.parse_args()
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.bind(('10.77.0.2',0))
end=time.monotonic()+a.duration
with Path(a.out).open('w',buffering=1) as f:
 i=0
 while time.monotonic()<end:
  now=time.time_ns();payload=f'continuous:{i}:{now}'.encode()
  try:s.sendto(payload,('10.77.0.1',9900));f.write(json.dumps({'seq':i,'sent_ns':now})+'\n')
  except OSError as e:f.write(json.dumps({'seq':i,'error':str(e),'sent_ns':now})+'\n')
  i+=1;time.sleep(a.interval)
