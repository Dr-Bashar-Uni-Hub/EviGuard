# EviGuard Research Suite v1.2 — Independently Kernel-Enforced Matched Replay

## Scope

1. Reruns the **working Phase 6.5** real DHCP/ARP EviGuard-Live testbed, including the v1.1 shadow reference.
2. Verifies its six live packet-delivery checkpoints.
3. Saves **the same live observation stream** (with snapshot hashes).
4. Replays selected state-change snapshots to two independently provisioned **Linux namespace pairs**, one per policy. Each pair has its own veth, IPv4 configuration, UDP receiver, and nftables rules. The two controllers are separately coded; both install independently acknowledged nftables rules.
5. Alternates policy execution order, sends three UDP packets per checkpoint per policy, compares receiver delivery with nftables counters, and measures rule installation acknowledgment time.

This is a **live-observation matched replay**, not two continuously running live event-driven controllers. The baseline is an independent prototype of the same predicate, **not** a published versioned-fencing implementation. Therefore, equivalence is expected and cannot establish CACV originality or superiority.

## Ubuntu requirements

Dedicated Ubuntu VirtualBox VM with sudo. `iproute2 nftables tcpdump python3 dnsmasq busybox iputils-ping`.

```bash
sudo apt update
sudo apt install -y iproute2 nftables tcpdump python3 dnsmasq busybox iputils-ping
sudo bash run_all.sh
```

A successful run creates `EviGuard_v1_2_Results_<UTC>.tar.gz` next to `run_all.sh`. Copy it to `/media/sf_cascade_backup/` and upload it for review. All namespaces are cleaned up on success or failure.

## What PASS means

The live checkpoint verifier passes; all recorded live observations are hash-checked and evaluated by both policies; each selected snapshot is independently enforced by nftables in both namespace pairs; packet delivery and kernel counters match each policy's decisions. No guarantee is claimed about packets at instantaneous rule-transition boundaries, real DAI/IPSG, cryptographic provenance, or originality.

## Research integrity

Do not edit the frozen Phase 6.4.1 baseline or earlier archives. Preserve failures. A zero-disagreement result is evidence of equivalence under tested observations, not novelty. Further comparison against faithful published algorithms and simultaneous asynchronous event handling is still required.
