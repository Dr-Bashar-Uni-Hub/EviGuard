# EviGuard

**Integrated Linux-based cross-mechanism authorization consistency and experimental evaluation.**

EviGuard connects DHCP-derived binding evidence, IP/interface configuration, ARP neighbor observations, controller authorization decisions, and Linux `nftables` enforcement. Its demonstrated contributions are **engineering integration, executable Linux implementation, experimental validation, and reproducible failure analysis**. This work does **not** claim a fundamentally new source-validation primitive or policy superiority over an equally informed reference.

## Frozen research evidence (November 2026)

| Experiment | Scope | Finding |
|---|---|---|
| Linux Phase 4.1 | 120 UDP packets | 40 delivered; 80 blocked |
| Linux Phase 5.1 | 18 trials, 2,880 packets | 1,112 delivered; no blocked-window deliveries in tested post-ack windows |
| Linux Phase 6 | 72 checkpoints, 144 kernel trials | 432 packets, 102 delivered; no policy disagreements |
| Research Suite v1.2 | 158 live observation snapshots | Zero matched-policy disagreements |
| Research Suite v1.2 | 20 kernel trials | 60 probes, 12 delivered |
| Final Campaign v1.0 | 180 **synthetic** scenarios | Zero paired-policy disagreements; fault exposure under delayed or missing enforcement updates |

**Scope limits:** Matched observation replay does not constitute a simultaneous independent production deployment. The temporal reference is not a faithful published SAVI implementation. The 180-scenario fault campaign is synthetic, **not** real Linux fault injection. Revocation is not instantaneous when notifications or rule installation are delayed. The study reports negative findings as well as successful enforcement tests.

## Linux test environment

Ubuntu 24.04; Linux network namespaces, veth, `dnsmasq`, BusyBox DHCP client, `iproute2`, `tcpdump`, Python 3 and `nftables`. Run only in an isolated testbed with network-administration privileges; never on a production network.

## Reproducibility status

The original source and result archives are preserved separately and are being prepared for release. **Executable source code and raw experimental result archives have not yet been uploaded here.** This README reports results from the frozen archives, not newly rerun experiments. See `REPRODUCIBILITY.md` for the artifact manifest.

## Prior work

The framework builds on established source-validation and consistent-update ideas, including RFC 7039, RFC 7513, Reitblatt et al. (2012), VeriFlow (2013), and NetPlumber (2013). Its engineering contribution is the integrated, inspectable Linux evaluation workflow, not algorithmic priority over these systems.

## Publication and licensing

A systems-evaluation manuscript is in preparation. No license is selected yet; public visibility does not itself grant reuse rights. A software release tag and citation metadata will be added after verification.
