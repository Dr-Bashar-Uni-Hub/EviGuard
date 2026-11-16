#!/usr/bin/env python3
"""E2 (Requirement 1): protocol-driven revocation. (a) real DHCPRELEASE captured on the wire;
   (b) client link-down. Infrastructure-only controller (lease AND neighbour AND link) at poll P ms."""
import sys, json, time, random, subprocess, os, signal
from common import *
n_rel, n_link = int(sys.argv[1]), int(sys.argv[2]); OUT = "results/e2"; os.makedirs(OUT, exist_ok=True)
S, C, SIP, CIP, VS, VC = "e2s", "e2c", "10.92.0.1", "10.92.0.2", "e2vs", "e2vc"
pair(S, C, VS, VC, SIP, CIP); sh(f"ip -n {C} addr flush dev {VC}")
MAC = json.loads(sh(f"ip -n {C} -j link show dev {VC}"))[0]["address"]
nft(S, "add table inet t\nadd chain inet t input { type filter hook input priority 0; policy accept; }\nadd rule inet t input udp dport 9900 drop\n")
LF = os.path.abspath(f"{OUT}/dnsmasq.leases"); open(LF, "w").close()
dn = subprocess.Popen(["ip", "netns", "exec", S, "dnsmasq", "--no-daemon", "--conf-file=/dev/null", f"--interface={VS}", "--bind-interfaces",
                       "--port=0", f"--dhcp-range={CIP},{CIP},255.255.255.0,2m", f"--dhcp-leasefile={LF}", "--dhcp-authoritative", "--no-ping"],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
snf = os.path.abspath(f"{OUT}/dhcp_wire.txt"); open(snf, "w").close()
sn = subprocess.Popen(["ip", "netns", "exec", S, "python3", os.path.abspath("sniffer.py"), VS, snf])
recf = f"{OUT}/received.txt"; open(recf, "w").close(); rx = start_receiver(S, recf); time.sleep(0.5)
uc = subprocess.Popen(["ip", "netns", "exec", C, "busybox", "udhcpc", "-f", "-i", VC, "-s", os.path.abspath("hook_sticky.sh"), "-t", "10", "-T", "1", "-A", "1"],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def lines(p): return [json.loads(l) for l in open(p)] if os.path.exists(p) else []
def wire(t_after, typ):
    return min([int(a) for a, b in (l.split() for l in open(snf)) if int(b) == typ and int(a) >= t_after], default=None)
def wait_allow(clog, want, t_after=0, timeout=6):
    end = time.time() + timeout
    while time.time() < end:
        L = [x for x in lines(clog) if x["t_a"] >= t_after]
        if L and L[-1]["allow"] == want: return L[-1]
        if want: subprocess.run(["ip", "-n", S, "neigh", "replace", CIP, "lladdr", MAC, "dev", VS, "nud", "reachable"], capture_output=True)
        time.sleep(0.05)
    return None
rows = []
for P in (80, 20):
    clog = os.path.abspath(f"{OUT}/controller_P{P}.jsonl"); open(clog, "w").close()
    ctl = subprocess.Popen(["python3", "controller_infra.py", S, VS, LF, CIP, MAC, str(P), clog])
    assert wait_allow(clog, True, timeout=20), "initial allow failed"
    for i in range(n_rel):
        lab = f"e2rel_P{P}_{i}"; sf = f"/tmp/{lab}.json"
        sp = start_sender(C, lab, SIP, 2.0, 150 + 3 * P + 600, sf); time.sleep(0.15 + random.uniform(0, P) / 1000)
        t_sig = time.monotonic_ns(); uc.send_signal(signal.SIGUSR2)
        sp.wait(); time.sleep(0.05)
        tw = wire(t_sig, 7); dec = next((x for x in lines(clog) if x["t_a"] >= t_sig and not x["allow"]), None)
        sent = json.load(open(sf)); os.remove(sf)
        if tw and dec:
            r = analyse(lab, sent, received(recf), tw, dec["t_a"])
            r.update(kind="release", poll_ms=P, sig_to_wire_ms=(tw - t_sig) / 1e6, wire_to_detect_ms=(dec["t_obs"] - tw) / 1e6,
                     wire_to_ack_ms=(dec["t_a"] - tw) / 1e6, install_ms=(dec["t_a"] - dec["t_install"]) / 1e6)
            rows.append(r)
        else: rows.append(dict(label=lab, kind="release", poll_ms=P, error="no wire release or no decision"))
        t_rg = time.monotonic_ns(); uc.send_signal(signal.SIGUSR1)
        if not wait_allow(clog, True, t_rg, 10): print("regrant timeout", lab, flush=True)
        time.sleep(0.1)
    for i in range(n_link):
        lab = f"e2link_P{P}_{i}"; time.sleep(random.uniform(0, P) / 1000)
        t_dn = time.monotonic_ns(); sh(f"ip -n {C} link set {VC} down")
        dec = wait_allow(clog, False, t_dn, 3)
        rows.append(dict(label=lab, kind="link_down", poll_ms=P, down_to_detect_ms=(dec["t_obs"] - t_dn) / 1e6 if dec else None,
                         down_to_ack_ms=(dec["t_a"] - t_dn) / 1e6 if dec else None))
        sh(f"ip -n {C} link set {VC} up"); time.sleep(0.1)
        if not wait_allow(clog, True, t_dn, 10): print("link regrant timeout", lab, flush=True)
    ctl.kill(); print("P", P, "done", flush=True)
envd = env(); json.dump(dict(env=envd, rows=rows), open(f"{OUT}/trials.json", "w"), indent=1)
for p in (uc, dn, sn, rx): p.kill()
sh(f"ip netns del {S}", check=False); sh(f"ip netns del {C}", check=False); print("finished e2", len(rows))
