#!/usr/bin/env python3
"""E3 (Requirement 3): exposure bound under controller crash with kernel-enforced set-element timeouts."""
import sys, json, time, random, subprocess, os, signal
from common import *
n = int(sys.argv[1]); OUT = "results/e3"; os.makedirs(OUT, exist_ok=True)
S, C, SIP, CIP = "e3s", "e3c", "10.93.0.1", "10.93.0.2"
pair(S, C, "e3vs", "e3vc", SIP, CIP)
recf = f"{OUT}/received.txt"; open(recf, "w").close(); rx = start_receiver(S, recf); time.sleep(0.5)
rows = []; random.seed(13); HORIZON = 1500
conds = [t for t in (250, 500, 1000) for _ in range(n)] + [0] * max(10, n // 10); random.shuffle(conds)
def setup(timeout):
    sh(f"ip netns exec {S} nft flush ruleset")
    flags = "flags timeout; " if timeout else ""
    nft(S, "add table inet t\nadd chain inet t input { type filter hook input priority 0; policy accept; }\n"
           f"add set inet t allowed {{ type ipv4_addr; {flags}}}\n"
           "add rule inet t input ip saddr @allowed udp dport 9900 accept\nadd rule inet t input udp dport 9900 drop\n")
for i, tau in enumerate(conds):
    lab = f"e3_{tau}_{i}"; logf = f"/tmp/{lab}.ref"; sf = f"/tmp/{lab}.json"
    setup(tau > 0)
    if tau:
        period = tau // 4
        ref = subprocess.Popen(["python3", "refresher.py", S, CIP, str(tau), str(period), logf])
    else:
        period = 100; nft(S, f"add element inet t allowed {{ {CIP} }}\n")
        ref = subprocess.Popen(["python3", "-c", "import time; time.sleep(60)"])
    time.sleep(max(0.4, 2.5 * period / 1000))
    dur = 150 + period + (tau or HORIZON) + 400
    sp = start_sender(C, lab, SIP, 2.0, dur, sf); time.sleep(0.15)
    time.sleep(random.uniform(0, period) / 1000)
    t_kill = time.monotonic_ns(); ref.send_signal(signal.SIGKILL); ref.wait()
    sp.wait(); time.sleep(0.05)
    rec = received(recf); sent = json.load(open(sf)); os.remove(sf)
    refs = [int(l.split()[0]) for l in open(logf)] if tau else []
    if tau: os.remove(logf)
    last = max([t for t in refs if t <= t_kill], default=None)
    r = analyse(lab, sent, rec, t_kill, t_kill + (tau or HORIZON) * 10**6 * 3)
    r.update(tau_ms=tau, period_ms=period, last_refresh_before_kill_ms=((t_kill - last) / 1e6) if last else None)
    if r["cut_hi_ms"] is not None and last:
        r["cut_after_last_refresh_ms"] = r["cut_hi_ms"] + (t_kill - last) / 1e6
    r["delivered_until_end"] = r["cut_hi_ms"] is None
    rows.append(r)
envd = env(); envd["n_per_condition"] = n
json.dump(dict(env=envd, rows=rows), open(f"{OUT}/trials.json", "w"), indent=1)
rx.kill(); sh(f"ip netns del {S}", check=False); sh(f"ip netns del {C}", check=False); print("finished e3", len(rows))
