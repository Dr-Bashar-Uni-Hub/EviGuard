# EviGuard

**Measuring authorization-to-enforcement exposure for DHCP-derived source authorization on Linux nftables.**

EviGuard is an open Linux testbed that links DHCP lease state, interface configuration, neighbour (ARP)
observations, controller decisions and `nftables` enforcement, and records them together with
sequence-numbered packet probes on one monotonic clock. It is used to measure how long a revoked host keeps
passing a Linux packet filter. The contribution is measurement methodology and evidence; EviGuard does **not**
claim a new source-validation algorithm or superiority over SAVI (RFC 7039/7513) or SecureBinder.

## Releases

| Release | Contents | Experiments in the manuscript |
|---|---|---|
| [v1.0.0](https://github.com/Dr-Bashar-Uni-Hub/EviGuard/releases/tag/v1.0.0) | Frozen source and result archives (Research Suite v1.2, Final Campaign v1.0, Linux Phases 4.1/5.1/6) | A–C on host H1 |
| [v1.1.0](https://github.com/Dr-Bashar-Uni-Hub/EviGuard/releases/tag/v1.1.0) | `EviGuard_Campaign_v2.zip` (SHA-256 `dd61422cb2126efaaa473453366e00f641c0c1251a99ea606df74c02cb4dab4e`) | D–H on host H2 |

## Repository layout

| Path | Contents |
|---|---|
| `source/EviGuard_Research_Suite_v1_2/` | Live lifecycle run and matched-snapshot replay (Experiments A–B) |
| `source/EviGuard_Final_Campaign_v1_0/` | Analytic exposure grid (Appendix B; synthetic, not fault injection) |
| `source/EviGuard_Campaign_v2/` | Scripts and raw results for Experiments D–H, with `SHA256SUMS.txt` |
| `docs/` | Reproduction guide and source checksums for v1.0.0 |
| `historical-research/`, `packet-tracer-labs/` | Earlier prototypes and teaching labs; not evidence for the manuscript |
| `ARCHIVE_SHA256SUMS.md` | Checksums of the v1.0.0 archives |

## Principal results

| Experiment | Host | Trials | Finding |
|---|---|---|---|
| C: injected-delay revocation | H1 | 18 | 0/1,248 probes delivered after acknowledgment; acknowledgment lagged cutover by median 50 ms |
| D: replication with read-back | H2 | 400 | 0/61,701 delivered after acknowledgment; lag median 5.7 ms, read-back +5.2 ms |
| E: real DHCPRELEASE and link-down | H2 | 300 | Exposure set by controller polling interval; 0/70,680 delivered after acknowledgment |
| F: set-element timeouts under controller crash | H2 | 310 | Exposure from crash ≤ τ + 6.5 ms; unbounded without timeout |
| G: rule-set size (to 10,000) and load | H2 | 1,600 | Sets size-insensitive; load roughly doubles time to cutover |
| H: spoofing adversary, ARP poisoning | H2 | 260 | IP-only rule admits spoofed frames; IP+MAC rule fails only on MAC cloning |

**Scope limits.** Both hosts are virtual machines with veth links; one client address; lease expiry not
measured; the reference policy is logically equivalent to EviGuard's and is not a SAVI implementation.

## Running

Run only as root in an isolated, disposable Linux VM: the scripts create network namespaces and nftables
rules. See `docs/REPRODUCTION_GUIDE.md` (v1.0.0) and `source/EviGuard_Campaign_v2/README.md` (v1.1.0).

## Licence and citation

Released under the MIT Licence (see `LICENSE`). Please cite using `CITATION.cff`.
