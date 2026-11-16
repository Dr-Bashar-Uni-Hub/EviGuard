# EviGuard Campaign v2 (Experiments D–H)

Scripts and raw results for Experiments D–H of the revised manuscript. Executed on host H2
(Firecracker microVM, 1 vCPU, Ubuntu 24.04.5, Linux 6.18.44, nftables 1.0.9, dnsmasq 2.91, BusyBox 1.36.1,
Python 3.12.3); each `results/*/trials.json` embeds its environment record.

| Experiment | Paper | Command (run as root in a disposable VM) |
|---|---|---|
| D replication, separated read-back | 4.7, 5.5 | `python3 exp_exposure.py e1 100` |
| E protocol-driven revocation | 4.8, 5.6 | `python3 exp_protocol.py 100 50` |
| F set-element timeouts under crash | 4.9, 5.7 | `python3 exp_timeout.py 100` |
| G rule-set size and load | 4.10, 5.8 | `python3 exp_exposure.py e4 100 <chain|set> <N>` for N in 0 100 1000 10000 |
| H spoofing adversary, ARP poisoning | 4.11, 5.9 | `python3 exp_adversary.py 20` |

Then `python3 analyze.py` writes `results/summary.json` and `results/tables.md`.
Requirements: iproute2, nftables, dnsmasq, busybox, iputils-ping, Python 3. Results directory names e1..e5
correspond to Experiments D, E, F, G, H respectively (e1=D, e2=E, e3=F, e4=G, e5=H).
The scripts create namespaces and nftables rules; never run them on a production host.
