#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
if [[ $# -lt 1 ]]; then echo "Usage: bash run.sh /path/to/EviGuard_v1_2_Results_20261109T200649Z.tar.gz"; exit 2; fi
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$HERE/results/$STAMP"
python3 "$HERE/run_campaign.py" --v12-results "$1" --out "$OUT"
(cd "$HERE" && tar -czf "EviGuard_Final_Campaign_Results_${STAMP}.tar.gz" "results/$STAMP")
echo "Results archive: $HERE/EviGuard_Final_Campaign_Results_${STAMP}.tar.gz"
