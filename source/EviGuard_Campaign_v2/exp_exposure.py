#!/usr/bin/env python3
"""E1: Phase 5.1 replication with separate ack and read-back stamps.
   E4: rule-set size (chain rules / set elements) and load scaling (Requirement 2)."""
import sys, json, time, random, subprocess, os
from common import *
mode, n = sys.argv[1], int(sys.argv[2]); ONE = sys.argv[3:5] if len(sys.argv) > 4 else None; OUT = "results/e4" if mode == "e4" else f"results/{mode}"; os.makedirs(OUT, exist_ok=True)
S, C, SIP, CIP = "e1s", "e1c", "10.91.0.1", "10.91.0.2"
pair(S, C, "e1vs", "e1vc", SIP, CIP)
recf = f"{OUT}/received_{'_'.join(ONE) if ONE else mode}.txt"; open(recf, "w").close(); rx = start_receiver(S, recf); time.sleep(0.5)
off = [0]; rec = {}
def pull():
    with open(recf) as f:
        f.seek(off[0])
        for line in f:
            p = line.split()
            if len(p) >= 2: rec[p[0]] = int(p[1])
        off[0] = f.tell()
BASE = f"add table inet t\nadd chain inet t input {{ type filter hook input priority 0; policy accept; }}\n"
def trial(label, revoke, d_ms, do_rb, sender_dur):
    sf = f"/tmp/{label}.json"
    sp = start_sender(C, label, SIP, 2.0, sender_dur, sf)
    time.sleep(0.15)
    t_r = time.monotonic_ns()
    if d_ms: time.sleep(d_ms / 1000)
    _, t_a = nft(S, revoke)
    t_rb = readback(S) if do_rb else None
    sp.wait(); time.sleep(0.05); pull()
    sent = json.load(open(sf)); os.remove(sf)
    return analyse(label, sent, rec, t_r, t_a, t_rb)
rows = []; envd = env(); envd["mode"] = mode; envd["n_per_condition"] = n
if mode == "e1":
    conds = [d for d in (0, 20, 100, 300) for _ in range(n)]; random.seed(7); random.shuffle(conds)
    nft(S, BASE)
    allow = f"flush chain inet t input\nadd rule inet t input ip saddr {CIP} udp dport 9900 accept\nadd rule inet t input udp dport 9900 drop\n"
    deny = "flush chain inet t input\nadd rule inet t input udp dport 9900 drop\n"
    for i, d in enumerate(conds):
        nft(S, allow); time.sleep(0.03)
        r = trial(f"e1_{i}", deny, d, True, 150 + d + 300); r.update(delay_ms=d); rows.append(r)
elif mode == "e4":
    sizes = [0, 100, 1000, 10000]; random.seed(11)
    combos = [(ONE[0], int(ONE[1]))] if ONE else [(a, b) for a in ("chain", "set") for b in sizes]
    for struct, N in combos:
        if True:
            sh(f"ip netns exec {S} nft flush ruleset")
            fill = [f"172.{16 + (j >> 16)}.{(j >> 8) & 255}.{j & 255}" for j in range(N)]
            if struct == "chain":
                txt = BASE + "".join(f"add rule inet t input ip saddr {a} udp dport 9900 drop\n" for a in fill)
                txt += "add rule inet t input udp dport 9900 drop\n"
                nft(S, txt)
                import re
                dh = re.findall(r"# handle (\d+)", sh(f"ip netns exec {S} nft -a list chain inet t input"))[-1]
                def grant():
                    o = sh(f"ip netns exec {S} nft -e -a insert rule inet t input position {dh} ip saddr {CIP} udp dport 9900 accept")
                    return re.findall(r"# handle (\d+)", o)[-1]
                h = [grant()]
                def revoke_txt(): return f"delete rule inet t input handle {h[0]}\n"
                def regrant(): h[0] = grant()
            else:
                txt = BASE + "add set inet t allowed { type ipv4_addr; }\n"
                for k in range(0, N, 2000):
                    txt += "add element inet t allowed { " + ", ".join(fill[k:k + 2000]) + " }\n"
                txt += f"add element inet t allowed {{ {CIP} }}\nadd rule inet t input ip saddr @allowed udp dport 9900 accept\nadd rule inet t input udp dport 9900 drop\n"
                nft(S, txt)
                def revoke_txt(): return f"delete element inet t allowed {{ {CIP} }}\n"
                def regrant(): nft(S, f"add element inet t allowed {{ {CIP} }}\n")
            for load in ("none", "cpu+traffic"):
                procs = []
                if load != "none":
                    procs.append(subprocess.Popen(["python3", "-c", "while True: pass"]))
                    procs.append(start_sender(C, "bg", SIP, 0.5, 10**9, "/dev/null", 9901))
                    time.sleep(0.5)
                for i in range(n):
                    lab = f"e4_{struct}_{N}_{load[0]}_{i}"
                    r = trial(lab, revoke_txt(), 0, False, 300)
                    r.update(struct=struct, N=N, load=load); rows.append(r); regrant(); time.sleep(0.03)
                for p in procs: p.kill()
                print(struct, N, load, "done", flush=True)
json.dump(dict(env=envd, rows=rows), open(f"{OUT}/trials_{'_'.join(ONE)}.json" if ONE else f"{OUT}/trials.json", "w"), indent=1)
rx.kill(); sh(f"ip netns del {S}", check=False); sh(f"ip netns del {C}", check=False)
print("finished", mode, len(rows))
