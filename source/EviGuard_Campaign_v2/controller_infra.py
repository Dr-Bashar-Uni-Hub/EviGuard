#!/usr/bin/env python3
"""Infrastructure-only controller: allow = unexpired dnsmasq lease (MAC, IP) AND usable server neighbour entry
   AND server-side link up. Polls every P ms; logs each decision change with observation and ack times."""
import sys, json, time, subprocess
srv, vs, leases, ip, mac, P, log = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5].lower(), int(sys.argv[6]) / 1000, sys.argv[7]
def run(*a): return subprocess.run(a, text=True, capture_output=True).stdout
def obs():
    t = time.monotonic_ns()
    try: L = open(leases).read().splitlines()
    except FileNotFoundError: L = []
    lease = any(len(p := l.split()) >= 3 and p[1].lower() == mac and p[2] == ip and (p[0] == "0" or int(p[0]) > time.time()) for l in L)
    nb = json.loads(run("ip", "-n", srv, "-j", "neigh", "show", "dev", vs) or "[]")
    arp = any(n.get("dst") == ip and str(n.get("lladdr", "")).lower() == mac and not set(n.get("state", [])) & {"FAILED", "INCOMPLETE"} for n in nb)
    lk = json.loads(run("ip", "-n", srv, "-j", "link", "show", "dev", vs) or "[{}]")[0]
    up = lk.get("operstate") == "UP"
    return t, lease, arp, up
f = open(log, "a", buffering=1); cur = None
while True:
    t, lease, arp, up = obs(); allow = lease and arp and up
    if allow != cur:
        s = "flush chain inet t input\n" + (f"add rule inet t input ip saddr {ip} udp dport 9900 accept\n" if allow else "") + "add rule inet t input udp dport 9900 drop\n"
        t0 = time.monotonic_ns(); subprocess.run(["ip", "netns", "exec", srv, "nft", "-f", "-"], input=s, text=True); t1 = time.monotonic_ns()
        f.write(json.dumps(dict(t_obs=t, allow=allow, lease=lease, arp=arp, up=up, t_install=t0, t_a=t1)) + "\n"); cur = allow
    time.sleep(P)
