#!/usr/bin/env python3
"""Paced, sequence-numbered UDP probe sender. Logs (seq, send monotonic_ns)."""
import socket, sys, time, json
label, dst, interval_ms, dur_ms, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
port = int(sys.argv[6]) if len(sys.argv) > 6 else 9900
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
iv = int(interval_ms * 1e6); n = int(dur_ms / interval_ms); log = []
t0 = time.monotonic_ns()
for i in range(n):
    tgt = t0 + i * iv
    while True:
        now = time.monotonic_ns()
        if now >= tgt: break
        if tgt - now > 600_000: time.sleep((tgt - now - 400_000) / 1e9)
    t = time.monotonic_ns()
    try: s.sendto(f"{label}:{i}".encode(), (dst, port))
    except OSError: pass
    log.append((i, t))
json.dump(log, open(out, "w"))
