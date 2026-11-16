#!/usr/bin/env python3
"""Aggregates results/*/trials.json into summary.json, tables (markdown) and figures."""
import json, os, random, statistics as st, collections
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
random.seed(1)
def ci(v, f=st.median, B=2000):
    v = [x for x in v if x is not None]
    if not v: return None
    bs = sorted(f(random.choices(v, k=len(v))) for _ in range(B))
    return dict(n=len(v), med=f(v), lo=bs[int(.025 * B)], hi=bs[int(.975 * B)], min=min(v), max=max(v))
def fmt(c, d=1): return "—" if not c else f"{c['med']:.{d}f} [{c['lo']:.{d}f}, {c['hi']:.{d}f}]"
S = {}; md = []
def L(p): return json.load(open(p)) if os.path.exists(p) else None
plt.rcParams.update({"font.size": 9})
# E1
d = L("results/e1/trials.json")
if d:
    R = d["rows"]; g = collections.defaultdict(list); [g[r["delay_ms"]].append(r) for r in R]
    S["e1"] = dict(env=d["env"], n=len(R), monotone=sum(r["monotone"] for r in R), post_ack_sent=sum(r["post_ack_sent"] for r in R),
                   post_ack_deliv=sum(r["post_ack_deliv"] for r in R), win_sent=sum(r["win_sent"] for r in R), win_deliv=sum(r["win_deliv"] for r in R),
                   pre_sent=sum(r["pre_sent"] for r in R), pre_deliv=sum(r["pre_deliv"] for r in R), by_delay={})
    md.append("E1 | delay | n | stale median [95% CI] | cutover hi after t_r | ack after t_r | ack lag | read-back after ack")
    for k in sorted(g):
        v = g[k]; e = dict(stale=ci([r["stale"] for r in v]), cut=ci([r["cut_hi_ms"] for r in v]), ack=ci([r["ack_ms"] for r in v]),
                           lag=ci([r.get("ack_lag_ms") for r in v]), rb=ci([r["readback_ms"] - r["ack_ms"] for r in v]),
                           cut_minus_delay=ci([r["cut_hi_ms"] - k for r in v if r["cut_hi_ms"] is not None]))
        S["e1"]["by_delay"][k] = e
        md.append(f"| {k} | {len(v)} | {fmt(e['stale'],0)} | {fmt(e['cut'])} | {fmt(e['ack'])} | {fmt(e['lag'])} | {fmt(e['rb'])} |")
    S["e1"]["lag_all"] = ci([r.get("ack_lag_ms") for r in R]); S["e1"]["rb_all"] = ci([r["readback_ms"] - r["ack_ms"] for r in R])
# E4
d = L("results/e4/trials.json")
if d:
    R = d["rows"]; S["e4"] = dict(n=len(R), monotone=sum(r["monotone"] for r in R), post_ack_deliv=sum(r["post_ack_deliv"] for r in R),
                                 post_ack_sent=sum(r["post_ack_sent"] for r in R), cells={})
    md.append("\nE4 | structure | N | load | n | ack after t_r | cutover hi | ack lag | stale")
    g = collections.defaultdict(list); [g[(r["struct"], r["N"], r["load"])].append(r) for r in R]
    for k in sorted(g):
        v = g[k]; e = dict(ack=ci([r["ack_ms"] for r in v]), cut=ci([r["cut_hi_ms"] for r in v]), lag=ci([r.get("ack_lag_ms") for r in v]), stale=ci([r["stale"] for r in v]),
                           post_ack=sum(r["post_ack_deliv"] for r in v), mono=sum(r["monotone"] for r in v))
        S["e4"]["cells"]["|".join(map(str, k))] = e
        md.append(f"| {k[0]} | {k[1]} | {k[2]} | {len(v)} | {fmt(e['ack'])} | {fmt(e['cut'])} | {fmt(e['lag'])} | {fmt(e['stale'],0)} |")
# E3
d = L("results/e3/trials.json")
if d:
    R = d["rows"]; S["e3"] = {}; md.append("\nE3 | tau | n | cutover after last refresh | cutover after kill | max(after refresh - tau) | unbounded")
    for t in sorted({r["tau_ms"] for r in R}):
        v = [r for r in R if r["tau_ms"] == t]
        e = dict(n=len(v), unbounded=sum(r["delivered_until_end"] for r in v), after_ref=ci([r.get("cut_after_last_refresh_ms") for r in v]),
                 after_kill=ci([r["cut_hi_ms"] for r in v]), excess_max=max([r["cut_after_last_refresh_ms"] - t for r in v if r.get("cut_after_last_refresh_ms") is not None], default=None),
                 stale=ci([r["stale"] for r in v]), mono=sum(r["monotone"] for r in v))
        S["e3"][t] = e
        md.append(f"| {t} | {len(v)} | {fmt(e['after_ref'])} | {fmt(e['after_kill'])} | {e['excess_max']} | {e['unbounded']} |")
# E2
d = L("results/e2/trials.json")
if d:
    R = d["rows"]; S["e2"] = dict(errors=sum("error" in r for r in R)); md.append("\nE2 | kind | poll | n | metric medians")
    for kind in ("release", "link_down"):
        for P in (80, 20):
            v = [r for r in R if r.get("kind") == kind and r["poll_ms"] == P and "error" not in r]
            if kind == "release":
                e = dict(n=len(v), sig_to_wire=ci([r["sig_to_wire_ms"] for r in v]), detect=ci([r["wire_to_detect_ms"] for r in v]), ack=ci([r["wire_to_ack_ms"] for r in v]),
                         cut=ci([r["cut_hi_ms"] for r in v]), stale=ci([r["stale"] for r in v]), post_ack=sum(r["post_ack_deliv"] for r in v),
                         post_ack_sent=sum(r["post_ack_sent"] for r in v), mono=sum(r["monotone"] for r in v))
                md.append(f"| release | {P} | {len(v)} | detect {fmt(e['detect'])} | ack {fmt(e['ack'])} | cut {fmt(e['cut'])} | stale {fmt(e['stale'],0)} | post-ack {e['post_ack']}/{e['post_ack_sent']} |")
            else:
                e = dict(n=len(v), detect=ci([r["down_to_detect_ms"] for r in v]), ack=ci([r["down_to_ack_ms"] for r in v]))
                md.append(f"| link_down | {P} | {len(v)} | detect {fmt(e['detect'])} | ack {fmt(e['ack'])} |")
            S["e2"][f"{kind}_{P}"] = e
# E5
d = L("results/e5/trials.json")
if d:
    R = d["rows"]; S["e5"] = {"cells": {}, "arp": None}; md.append("\nE5 | policy | state | scenario | delivered/sent")
    g = collections.defaultdict(lambda: [0, 0])
    for r in R: c = g[(r["policy"], r["state"], r["scenario"])]; c[0] += r["delivered"]; c[1] += r["sent"]
    for k in sorted(g): S["e5"]["cells"]["|".join(k)] = g[k]; md.append(f"| {k[0]} | {k[1]} | {k[2]} | {g[k][0]}/{g[k][1]} |")
    a = d["arp"]; S["e5"]["arp"] = dict(n=len(a), overwritten=sum(x["overwritten"] for x in a), lost=sum(x["victim_mac_lost"] for x in a))
    md.append(f"ARP poisoning: neighbour entry overwritten in {S['e5']['arp']['overwritten']}/{len(a)}")
json.dump(S, open("results/summary.json", "w"), indent=1, default=str); open("results/tables.md", "w").write("\n".join(md)); print("\n".join(md))
