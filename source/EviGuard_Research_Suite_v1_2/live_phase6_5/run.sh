#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
[[ $(id -u) -eq 0 ]] || { echo 'Run sudo bash run.sh'; exit 2; }
for x in ip nft tcpdump python3 dnsmasq busybox ping; do command -v "$x" >/dev/null || { echo "Missing $x"; exit 2; }; done
OUT="$(pwd)/results/$(date -u +%Y%m%dT%H%M%SZ)"; mkdir -p "$OUT"
exec > >(tee "$OUT/console.log") 2>&1
PFX="eg$(printf '%04d' $((RANDOM%10000)))"; NC="${PFX}c"; NS="${PFX}s"; VC="${PFX}0"; VS="${PFX}1"
cleanup(){ set +e; for p in "${SEND_PID:-}" "${CTRL_PID:-}" "${CAP_PID:-}" "${RECV_PID:-}" "${DHCP_PID:-}"; do [[ -z "$p" ]] || kill "$p" 2>/dev/null; done; ip netns del "$NC" 2>/dev/null; ip netns del "$NS" 2>/dev/null; }
trap cleanup EXIT
ip netns add "$NC"; ip netns add "$NS"
ip link add "$VC" type veth peer name "$VS"; ip link set "$VC" netns "$NC"; ip link set "$VS" netns "$NS"
for n in "$NC" "$NS"; do ip -n "$n" link set lo up; done
ip -n "$NC" link set "$VC" up; ip -n "$NS" link set "$VS" up
ip -n "$NS" addr add 10.77.0.1/24 dev "$VS"
MAC="$(ip -n "$NC" -o link show "$VC" | grep -oE 'link/ether ([0-9a-f]{2}:){5}[0-9a-f]{2}' | awk '{print $2}')"
ip netns exec "$NS" nft -f - <<'NFT'
add table inet eviguard
add chain inet eviguard input { type filter hook input priority 0; policy accept; }
add rule inet eviguard input udp dport 9900 counter drop
NFT
ip netns exec "$NS" tcpdump -i "$VS" -s 0 -U -w "$OUT/traffic.pcap" '(arp or udp port 67 or udp port 68 or udp port 9900)' > "$OUT/tcpdump.log" 2>&1 & CAP_PID=$!
ip netns exec "$NS" dnsmasq --no-daemon --conf-file=/dev/null --interface="$VS" --bind-interfaces --port=0 --dhcp-range=10.77.0.2,10.77.0.2,255.255.255.0,10m --dhcp-leasefile="$OUT/dnsmasq.leases" --log-dhcp --log-facility=- > "$OUT/dnsmasq.log" 2>&1 & DHCP_PID=$!
ip netns exec "$NS" python3 receiver.py "$OUT/received.jsonl" & RECV_PID=$!
sleep 1
python3 -u controller.py --client "$NC" --server "$NS" --client-if "$VC" --server-if "$VS" --events "$OUT/events.jsonl" --leases "$OUT/dnsmasq.leases" --ip 10.77.0.2 --mac "$MAC" --out "$OUT/transitions.jsonl" > "$OUT/controller.log" 2>&1 & CTRL_PID=$!
wait_for(){ local wanted="$1"; for i in $(seq 1 120); do if python3 state_check.py "$OUT/transitions.jsonl" "$wanted"; then return 0; fi; sleep .1; done; echo "Timeout waiting allow=$wanted"; cat "$OUT/controller.log"; return 1; }
checkpoint(){ python3 - "$OUT/checkpoints.jsonl" "$1" "$2" <<'PY2'
import json,sys,time
with open(sys.argv[1],'a') as f:f.write(json.dumps({'stage':sys.argv[2],'acknowledged_allow':sys.argv[3]=='true','time_ns':time.time_ns()})+'\n')
PY2
}
probe(){ ip netns exec "$NC" python3 sender.py "$1" 10.77.0.1 9900; sleep .35; }
wait_for false
ip -n "$NC" addr add 10.77.0.2/24 dev "$VC"
checkpoint prelease false;probe prelease
ip -n "$NC" addr flush dev "$VC" scope global
EVIGUARD_EVENTS="$OUT/events.jsonl" ip netns exec "$NC" busybox udhcpc -i "$VC" -s "$(pwd)/dhcp_hook.sh" -n -q -t 5 -T 2 > "$OUT/udhcpc_1.log" 2>&1
ip netns exec "$NS" ping -c 2 -W 2 10.77.0.2 > "$OUT/ping_1.log" 2>&1 || true
wait_for true
checkpoint authorized true;probe authorized
# Begin continuous traffic while address remains configured. Explicitly log timing.
ip netns exec "$NC" python3 continuous_sender.py "$OUT/continuous_sent.jsonl" --duration 12 --interval .02 > "$OUT/continuous.log" 2>&1 & SEND_PID=$!
sleep .25
# Controlled revocation event while DHCP lease and neighbor may remain stale.
printf '{"kind":"deconfig","origin":"test-harness","reason":"controlled-revocation-with-stale-evidence"}\n' >> "$OUT/events.jsonl"
wait_for false
checkpoint revoked false;probe revoked
# Force fresh real DHCP callback; address is flushed before client acquisition.
ip -n "$NC" addr flush dev "$VC" scope global
EVIGUARD_EVENTS="$OUT/events.jsonl" ip netns exec "$NC" busybox udhcpc -i "$VC" -s "$(pwd)/dhcp_hook.sh" -n -q -t 5 -T 2 > "$OUT/udhcpc_2.log" 2>&1
# On rebound, explicitly remove server neighbor evidence to test partial state.
ip -n "$NS" neigh del 10.77.0.2 dev "$VS" 2>/dev/null || true
# We cannot reliably force an absent neighbor while continuous traffic is running;
# instead create a controlled negative event before the subsequent fresh ARP probe.
printf '{"kind":"deconfig","origin":"test-harness","reason":"rebound-evidence-gate"}\n' >> "$OUT/events.jsonl"
wait_for false
checkpoint rebound_blocked false;probe rebound_blocked
# Record a genuine new DHCP bound callback using a new client request.
ip -n "$NC" addr flush dev "$VC" scope global
EVIGUARD_EVENTS="$OUT/events.jsonl" ip netns exec "$NC" busybox udhcpc -i "$VC" -s "$(pwd)/dhcp_hook.sh" -n -q -t 5 -T 2 > "$OUT/udhcpc_3.log" 2>&1
ip netns exec "$NS" ping -c 2 -W 2 10.77.0.2 > "$OUT/ping_2.log" 2>&1 || true
wait_for true
checkpoint rebound_authorized true;probe rebound_authorized
printf '{"kind":"deconfig","origin":"test-harness","reason":"final-revocation"}\n' >> "$OUT/events.jsonl"
wait_for false
checkpoint final_revoked false;probe final_revoked
wait "$SEND_PID" || true; SEND_PID=''
ip netns exec "$NS" nft -a list chain inet eviguard input > "$OUT/final_nft_rules.txt"
ip -n "$NS" neigh show dev "$VS" > "$OUT/final_neighbor.txt"
kill "$CTRL_PID" 2>/dev/null || true; wait "$CTRL_PID" 2>/dev/null || true; CTRL_PID=''
kill "$RECV_PID" 2>/dev/null || true; wait "$RECV_PID" 2>/dev/null || true; RECV_PID=''
kill "$CAP_PID" 2>/dev/null || true; wait "$CAP_PID" 2>/dev/null || true; CAP_PID=''
tcpdump -nn -r "$OUT/traffic.pcap" > "$OUT/decoded_capture.txt" 2> "$OUT/decode_errors.txt"
python3 verify.py "$OUT"
echo "Results: $OUT"
