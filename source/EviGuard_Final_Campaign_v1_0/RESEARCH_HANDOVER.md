# EviGuard research continuity (2026-11-09)

Frozen v1.2 results: 158 live observation snapshots, 0 policy disagreements, 20 independent namespace kernel trials, 60 comparison packets, 12 delivered; live and kernel verifiers passed. The independent kernel reference uses matched replay snapshots and equivalent logic, not a faithful published SAVI/temporal protocol. Median nft rule acknowledgment approx. 15.01 ms EviGuard and 11.17 ms reference (small n, not causal superiority).

Phase 1.3: SHA-256 checks passed; bounded revocation model has 4 valid interleavings, 2 unsafe. No reactive controller can prevent delivery in an unobserved revocation interval under model assumptions.
Phase 1.4: acknowledgment, versions, leases studied; all conditional/established patterns; no new mechanism.
Phase 1.5: 64 synthetic states, 7 differences versus incomplete baseline, 0 versus equally informed reference; no novelty.
Phase 1.6: targeted published baseline audit (SAVI RFC 7039/7513, consistent network updates); NO-GO for current CACV algorithmic novelty. Not exhaustive literature proof.

Manuscript feasibility: CONDITIONAL systems-evaluation study, not yet JISA ready. Need faithful baseline, real failure injection, multi-client/load trials, exact timing and statistical repeats, fuller related work.

This final bounded campaign v1.0 is an **offline pilot** only, preserving a preregistered protocol and demonstrating reproducible fault-model analysis. It cannot substitute for the still-required privileged Linux fault campaign. Stop novelty search unless distinct guarantee survives published-baseline scrutiny.
