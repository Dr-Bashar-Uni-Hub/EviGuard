#!/usr/bin/env python3
"""E5 (Requirement 4): spoofing adversary on a shared bridged segment. Policy A = IP-only accept rule (as in the
   EviGuard testbed); Policy B = infrastructure-anchored IP+MAC rule (SAVI-style binding of IP to the DHCP-observed MAC)."""
import sys, json, time, random, subprocess, os
from common import *
R = int(sys.argv[1]); OUT = "results/e5"; os.makedirs(OUT, exist_ok=True)
SW, S, V, A = "e5w", "e5s", "e5v", "e5a"; SIP, VIP, AIP = "10.95.0.1", "10.95.0.2", "10.95.0.3"
for nsn in (SW, S, V, A): sh(f"ip netns del {nsn}", check=False); sh(f"ip netns add {nsn}"); sh(f"ip -n {nsn} link set lo up")
sh(f"ip -n {SW} link add br0 type bridge"); sh(f"ip -n {SW} link set br0 up")
for nsn, ifc, ip in ((S, "e5s0", SIP), (V, "e5v0", VIP), (A, "e5a0", AIP)):
    sh(f"ip link add {ifc} type veth peer name {ifc}p"); sh(f"ip link set {ifc} netns {nsn}"); sh(f"ip link set {ifc}p netns {SW}")
    sh(f"ip -n {SW} link set {ifc}p master br0"); sh(f"ip -n {SW} link set {ifc}p up")
    sh(f"ip -n {nsn} addr add {ip}/24 dev {ifc}"); sh(f"ip -n {nsn} link set {ifc} up")
m = lambda nsn, ifc: json.loads(sh(f"ip -n {nsn} -j link show dev {ifc}"))[0]["address"]
SM, VM, AM = m(S, "e5s0"), m(V, "e5v0"), m(A, "e5a0")
recf = f"{OUT}/received.txt"; open(recf, "w").close(); rx = start_receiver(S, recf); time.sleep(0.5)
base = "flush ruleset\nadd table inet t\nadd chain inet t input { type filter hook input priority 0; policy accept; }\n"
POL = {"A_ip_only": f"add rule inet t input ip saddr {VIP} udp dport 9900 accept\n",
       "B_ip_mac": f"add rule inet t input ether saddr {VM} ip saddr {VIP} udp dport 9900 accept\n"}
def neigh():
    for e in json.loads(sh(f"ip -n {S} -j neigh show dev e5s0")):
        if e.get("dst") == VIP: return e.get("lladdr", "").lower(), e.get("state")
    return None, None
def restore():
    sh(f"ip -n {S} neigh del {VIP} dev e5s0", check=False)
    subprocess.run(["ip", "netns", "exec", S, "ping", "-c1", "-W1", VIP], capture_output=True)
rows = []
for pol, rule in POL.items():
    for state in ("authorized", "revoked"):
        nft(S, base + (rule if state == "authorized" else "") + "add rule inet t input udp dport 9900 drop\n")
        for rep in range(R):
            for scen in ("legit", "spoof_ip", "spoof_ip_mac"):
                lab = f"e5_{pol}_{state}_{scen}_{rep}"; sf = f"/tmp/{lab}.json"
                if scen == "legit":
                    subprocess.run(["ip", "netns", "exec", V, "python3", "sender.py", lab, SIP, "2", "100", sf])
                else:
                    src = AM if scen == "spoof_ip" else VM
                    subprocess.run(["ip", "netns", "exec", A, "python3", "rawsend.py", "udp", "e5a0", src, SM, VIP, SIP, lab, "50", "2", sf])
                time.sleep(0.05); rec = received(recf); sent = json.load(open(sf)); os.remove(sf)
                rows.append(dict(policy=pol, state=state, scenario=scen, rep=rep, sent=len(sent), delivered=sum(f"{lab}:{i}" in rec for i, _ in sent)))
# ARP poisoning of the server's neighbour table (affects any controller that uses neighbour evidence)
arp = []
for rep in range(R):
    restore(); time.sleep(1.2)
    before = neigh()
    subprocess.run(["ip", "netns", "exec", A, "python3", "rawsend.py", "arp", "e5a0", AM, SM, VIP, SIP])
    time.sleep(0.2); after = neigh()
    arp.append(dict(rep=rep, before=before, after=after, overwritten=after[0] == AM.lower(), victim_mac_lost=after[0] != VM.lower()))
envd = env(); envd.update(R=R, macs=dict(server=SM, victim=VM, attacker=AM))
json.dump(dict(env=envd, rows=rows, arp=arp), open(f"{OUT}/trials.json", "w"), indent=1)
rx.kill(); [sh(f"ip netns del {x}", check=False) for x in (SW, S, V, A)]; print("finished e5", len(rows), len(arp))
