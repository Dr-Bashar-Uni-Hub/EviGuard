import subprocess, json, time, os, random, statistics as st
def sh(c, check=True, inp=None):
    p = subprocess.run(c, shell=True, text=True, capture_output=True, input=inp)
    if check and p.returncode: raise RuntimeError(f"{c}\n{p.stderr}")
    return p.stdout
def nft(ns, script):
    """Apply an nft transaction in namespace ns. Returns (t_before, t_after_return)."""
    t0 = time.monotonic_ns()
    p = subprocess.run(["ip", "netns", "exec", ns, "nft", "-f", "-"], input=script, text=True, capture_output=True)
    t1 = time.monotonic_ns()
    if p.returncode: raise RuntimeError(p.stderr + script[:300])
    return t0, t1
def readback(ns, table="t"):
    sh(f"ip netns exec {ns} nft list table inet {table} >/dev/null"); return time.monotonic_ns()
def pair(srv, cli, vs, vc, sip, cip):
    for n in (srv, cli): sh(f"ip netns del {n}", check=False); sh(f"ip netns add {n}"); sh(f"ip -n {n} link set lo up")
    sh(f"ip link add {vs} type veth peer name {vc}")
    sh(f"ip link set {vs} netns {srv}"); sh(f"ip link set {vc} netns {cli}")
    sh(f"ip -n {srv} addr add {sip}/24 dev {vs}"); sh(f"ip -n {cli} addr add {cip}/24 dev {vc}")
    sh(f"ip -n {srv} link set {vs} up"); sh(f"ip -n {cli} link set {vc} up")
def start_receiver(ns, out, port=9900):
    return subprocess.Popen(["ip", "netns", "exec", ns, "python3", os.path.abspath("receiver.py"), out, str(port)])
def start_sender(ns, label, dst, iv, dur, out, port=9900):
    return subprocess.Popen(["ip", "netns", "exec", ns, "python3", os.path.abspath("sender.py"), label, dst, str(iv), str(dur), out, str(port)])
def received(path):
    d = {}
    if os.path.exists(path):
        for line in open(path):
            p = line.split()
            if len(p) >= 2: d[p[0]] = int(p[1])
    return d
def analyse(label, sent, rec, t_r, t_a, t_rb=None):
    """Probe-bracketing analysis for one trial (all times monotonic ns)."""
    flags = [(t, f"{label}:{i}" in rec) for i, t in sent]
    pre = [f for t, f in flags if t < t_r]; post = [(t, f) for t, f in flags if t >= t_r]
    win = [f for t, f in post if t < t_a]; aft = [f for t, f in post if t >= t_a]
    k = next((j for j, (t, f) in enumerate(post) if not f), None)
    mono = k is None or not any(f for t, f in post[k:])
    hi = (post[k][0] - t_r) / 1e6 if k is not None else None
    lo = (post[k - 1][0] - t_r) / 1e6 if k else 0.0
    r = dict(label=label, pre_sent=len(pre), pre_deliv=sum(pre), win_sent=len(win), win_deliv=sum(win),
             post_ack_sent=len(aft), post_ack_deliv=sum(aft), stale=sum(f for t, f in post),
             cut_lo_ms=lo, cut_hi_ms=hi, ack_ms=(t_a - t_r) / 1e6, monotone=mono)
    if hi is not None: r["ack_lag_ms"] = r["ack_ms"] - hi
    if t_rb: r["readback_ms"] = (t_rb - t_r) / 1e6
    return r
def env():
    return dict(kernel=sh("uname -r").strip(), nft=sh("nft --version").strip(), dnsmasq=sh("dnsmasq --version").splitlines()[0],
                busybox=sh("busybox | head -1").strip(), python=sh("python3 --version").strip(),
                os=sh(". /etc/os-release; echo $PRETTY_NAME").strip(), cpus=os.cpu_count(),
                mem_mb=int(sh("free -m | awk '/Mem/{print $2}'")), virt=sh("systemd-detect-virt 2>/dev/null || echo unknown", check=False).strip())
