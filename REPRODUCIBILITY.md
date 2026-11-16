# Reproducibility and evidence manifest

All source code, raw results and checksums used in the manuscript are hosted in this repository and its releases.

| Evidence | Location | Integrity check |
|---|---|---|
| v1.0.0 frozen archives (Experiments A–C) | Release v1.0.0 asset | `ARCHIVE_SHA256SUMS.md`; `SHA256SUMS.txt` inside the asset |
| v1.0.0 source | `source/EviGuard_Research_Suite_v1_2/`, `source/EviGuard_Final_Campaign_v1_0/` | `docs/SOURCE_SHA256SUMS.txt` |
| Campaign v2 (Experiments D–H) | `source/EviGuard_Campaign_v2/`; release v1.1.0 asset | `cd source/EviGuard_Campaign_v2 && sha256sum -c SHA256SUMS.txt` |

## Evidence categories

1. **Linux kernel measurements:** Experiments A–C (host H1) and D–H (host H2), all using namespaces, veth links and nftables with packet-level verification.
2. **Analytic model:** the Final Campaign v1.0 exposure grid (manuscript Appendix B). It is not a measurement of fault injection; real controller-crash measurements are Experiment F.
3. **Negative results:** no decision advantage over an equally informed reference; IP-only rules admit spoofed traffic; neighbour evidence can be poisoned by forged ARP replies.

## Safe reproduction

Requires root in an isolated, disposable VM. Review scripts before running.

## Release checklist

- [x] Frozen executable sources and raw results uploaded (v1.0.0)
- [x] Campaign v2 sources and raw results uploaded (v1.1.0)
- [x] Checksums for all archives and files
- [x] Software versions recorded (H2: in every `results/*/trials.json`)
- [x] Licence (MIT) and citation metadata
