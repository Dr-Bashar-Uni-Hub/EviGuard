# Reproducing the frozen EviGuard experiments

## Linux environment

Use a disposable Ubuntu 24.04 VM with sudo. Install:

```bash
sudo apt update
sudo apt install -y iproute2 nftables tcpdump python3 dnsmasq busybox iputils-ping
```

## Kernel experiment

```bash
cd source/EviGuard_Research_Suite_v1_2
sudo bash run_all.sh
```

Read the included original `README.md` and scripts before execution. The suite produces a timestamped `EviGuard_v1_2_Results_<UTC>.tar.gz`. A fresh run may differ from archived timing measurements.

## Offline synthetic campaign

```bash
cd source/EviGuard_Final_Campaign_v1_0
bash run.sh /absolute/path/to/EviGuard_v1_2_Results_20261109T200649Z.tar.gz
```

The second command requires the frozen v1.2 results archive from the v1.0.0 release asset. This is a deterministic *offline* campaign, not Linux fault injection.

## Verification

Check original archived file integrity against `ARCHIVE_SHA256SUMS.md` and source-file integrity against `docs/SOURCE_SHA256SUMS.txt`. Inspect output logs and JSON reports; do not interpret PASS as proof of instantaneous revocation, new algorithmic novelty, or a faithful SAVI baseline.

## Safety and permissions

The scripts create Linux namespaces, veth interfaces, and nftables rules, requiring elevated permissions. Run in an isolated disposable VM, never on a production host or network.
