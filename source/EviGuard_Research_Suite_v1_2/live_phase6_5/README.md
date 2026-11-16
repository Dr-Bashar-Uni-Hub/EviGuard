# EviGuard-Live Phase 6.5 — Continuous traffic and controlled event races

Extends the frozen, successful Phase 6.4.1 controller without changing its policy logic. Uses real DHCP acquisitions, live Linux ARP observations, a 12-second concurrent UDP stream, three controlled revocation events, and six acknowledged probe checkpoints. The tests probe stale lease/neighbor evidence and rapid re-acquisition. A successful run is NOT evidence of exact kernel-boundary safety or algorithmic novelty. No independent matched-information baseline is included; do not present this as a comparative advantage.

## Run

Ubuntu 24.04 with `iproute2 nftables tcpdump python3 dnsmasq busybox iputils-ping` installed, root required. Extract ZIP and run `sudo bash run.sh`. Results appear in `results/<UTC timestamp>/`. If the script fails, preserve all logs and report the traceback; do not manually mark it PASS.

## Verification

Expected 60 checkpoint UDP probes, 20 delivered (authorized and rebound_authorized), 40 blocked. Continuous stream delivery is intentionally not predetermined. The `checkpoints.jsonl` timestamps are userspace acknowledgment times and cannot prove that in-flight packets were rejected at the exact nftables transition. Note that the rebound blocked checkpoint uses an explicit deconfig gate; it is NOT a pure ARP-only denial experiment. DHCP client callbacks are real; revocation triggers are harness-controlled. Baseline comparison is deferred to a later phase.

## Frozen reference

The original Phase 6.4.1 source and Ubuntu archive are preserved separately in `EviGuard_Live_Phase6_4_1_FROZEN` with SHA-256 hashes. This phase does not overwrite them.
