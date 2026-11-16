#!/usr/bin/env python3
"""UDP receiver: appends 'message t_recv_ns' per datagram."""
import socket, sys, time
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 << 20)
s.bind(("0.0.0.0", int(sys.argv[2]) if len(sys.argv) > 2 else 9900))
f = open(sys.argv[1], "a", buffering=1)
while True:
    d, a = s.recvfrom(2048); f.write(f"{d.decode(errors='replace')} {time.monotonic_ns()} {a[0]}\n")
