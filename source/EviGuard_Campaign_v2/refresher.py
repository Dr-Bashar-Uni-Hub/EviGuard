#!/usr/bin/env python3
"""Controller heartbeat: atomically re-adds the client's set element with timeout tau every period."""
import sys, time, subprocess
ns, cip, tau, period, log = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]) / 1000, sys.argv[5]
tx = (f"add element inet t allowed {{ {cip} timeout {tau}ms }}\ndelete element inet t allowed {{ {cip} }}\n"
      f"add element inet t allowed {{ {cip} timeout {tau}ms }}\n")
f = open(log, "a", buffering=1)
while True:
    p = subprocess.run(["ip", "netns", "exec", ns, "nft", "-f", "-"], input=tx, text=True, capture_output=True)
    f.write(f"{time.monotonic_ns()} {p.returncode}\n"); time.sleep(period)
