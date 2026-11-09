# Reproducibility and evidence manifest

The original frozen experiments were executed in an isolated Ubuntu 24.04 Linux VM. The files below identify the preserved source and result archives. These artifacts are **not yet hosted in this repository**; do not treat this manifest as an executable release.

## Source bundles

- `EviGuard_Research_Suite_v1_2.zip` — includes `run_all.sh`, `kernel_compare.py`, and `live_phase6_5/` scripts (`controller.py`, `run.sh`, `verify.py`, `dhcp_hook.sh`, UDP sender/receiver, and reference comparison)
- `EviGuard_Final_Campaign_v1_0.zip` — includes `run_campaign.py`, `run.sh`, `PROTOCOL.md`, and `RESEARCH_HANDOVER.md`
- Earlier CACV/EviGuard Linux phase bundles, including corrected Phase 4.1, Phase 5.1, and Phase 6

## Frozen result archives

- `EviGuard_v1_2_Results_20261109T200649Z.tar.gz` — `summary.json`, `live_verification.json`, `live_observations.jsonl`, `kernel_compare/verification.json`, `kernel_compare/kernel_trials.json`, packet receipt records and logs
- `EviGuard_Final_Campaign_Results_20261109T203315Z.tar.gz` — offline synthetic campaign results
- `CACV_Linux_Phase4_1_Results.tar.gz`
- `CACV_Linux_Phase5_1_Results.tar.gz`
- `CACV_Linux_Phase6_Results.tar.gz`

## Evidence categories

1. **Actual Linux kernel experiments:** namespace/veth/nftables packet-delivery tests, DHCP and ARP state collection, and separately installed matched reference policies.
2. **Synthetic/model-based analysis:** bounded event-ordering and the 180-scenario fault campaign. These are not measurements of Linux fault injection.
3. **Negative results:** no general policy superiority versus an equally informed reference; asynchronous notification/install delay prevents an instantaneous revocation guarantee.

## Safe reproduction

Reproduction requires Linux network-administration privileges and may modify firewall rules and virtual interfaces. Run only in an isolated disposable VM. Review shell scripts before execution. The repository is **not yet an independently executable release** until the source bundles, outputs, environment versions, and checksums have been uploaded and validated.

## Release checklist

- [x] Public project repository and evidence overview
- [x] Historical numerical audit documented
- [ ] Upload frozen executable sources
- [ ] Upload raw results and checksums
- [ ] Confirm software versions and end-to-end replay
- [ ] Select license and add citation metadata
- [ ] Create immutable versioned release
