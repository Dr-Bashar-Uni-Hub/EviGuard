#!/usr/bin/env python3
"""Logs DHCP message types seen on an interface with monotonic_ns (run inside the server namespace)."""
import socket, sys, time
ifc, out = sys.argv[1], sys.argv[2]
s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0800)); s.bind((ifc, 0))
f = open(out, "a", buffering=1)
while True:
    pkt = s.recv(4096); t = time.monotonic_ns()
    ip = pkt[14:]; ihl = (ip[0] & 15) * 4
    if ip[9] != 17: continue
    udp = ip[ihl:]
    if int.from_bytes(udp[2:4], "big") not in (67, 68): continue
    d = udp[8:]; o = 240
    if d[236:240] != b"\x63\x82\x53\x63": continue
    while o < len(d) and d[o] != 255:
        if d[o] == 0: o += 1; continue
        if d[o] == 53: f.write(f"{t} {d[o + 2]}\n"); break
        o += 2 + d[o + 1]
