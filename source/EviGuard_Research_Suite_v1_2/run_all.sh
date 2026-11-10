#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
[[ $(id -u) -eq 0 ]] || { echo 'Run: sudo bash run_all.sh'; exit 2; }
for tool in ip nft python3 dnsmasq busybox tcpdump ping; do command -v "$tool" >/dev/null || { echo "Missing dependency: $tool"; exit 2; }; done
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
OUT="$(pwd)/results/$STAMP";mkdir -p "$OUT"
exec > >(tee "$OUT/console.log") 2>&1
echo '=== Step 1: capture real DHCP/ARP observations and verify EviGuard live enforcement ==='
# Live testbed writes its own timestamped result folder.
BEFORE=$(find live_phase6_5/results -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort || true)
bash live_phase6_5/run.sh
LIVE=$(find live_phase6_5/results -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' | sort -nr | head -1 | cut -d' ' -f2-)
[[ -f "$LIVE/verification.json" && -f "$LIVE/shadow_comparison.jsonl" ]] || { echo 'Live artifacts missing'; exit 1; }
cp "$LIVE/verification.json" "$OUT/live_verification.json"
cp "$LIVE/shadow_comparison.jsonl" "$OUT/live_observations.jsonl"
echo '=== Step 2: replay matched live snapshots through TWO independently enforced kernel namespaces ==='
python3 kernel_compare.py --snapshots "$OUT/live_observations.jsonl" --out "$OUT/kernel_compare"
echo '=== Step 3: archive ==='
python3 - "$OUT" <<'PY'
import json,sys,pathlib
p=pathlib.Path(sys.argv[1]);live=json.loads((p/'live_verification.json').read_text());comp=json.loads((p/'kernel_compare/verification.json').read_text())
s={'status':'PASS' if live['status']=='PASS' and comp['status']=='PASS' else 'FAIL','live':live['status'],'kernel_comparison':comp['status'],'novelty':'NOT ESTABLISHED','comparison_kind':'matched live snapshot replay with separate kernel enforcement'}
(p/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
PY
ARCHIVE="$(pwd)/EviGuard_v1_2_Results_${STAMP}.tar.gz"
tar -czf "$ARCHIVE" -C "$(dirname "$OUT")" "$(basename "$OUT")"
echo "Upload this archive: $ARCHIVE"
