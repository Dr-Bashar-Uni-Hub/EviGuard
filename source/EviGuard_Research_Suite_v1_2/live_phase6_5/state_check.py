import json,sys
from pathlib import Path
p=Path(sys.argv[1]); want=sys.argv[2].lower()=='true'
if not p.exists(): sys.exit(1)
try:
    last=json.loads(p.read_text().splitlines()[-1]); sys.exit(0 if last['allow'] is want else 1)
except (IndexError,ValueError,KeyError): sys.exit(1)
