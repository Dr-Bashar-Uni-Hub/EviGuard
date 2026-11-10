# EviGuard-CAE research campaign — CAE-01 audit (2026-11-08)

## Status
The causal-evidence direction has been adopted as a **hypothesis**, not a proven novel contribution. This package is a first executable formal-model audit and synthetic experiment, **not** a complete P4/XDP implementation, independent proof assistant, or publication-ready result.

## Phase A: Definitions and correction of the uploaded dossier
The dossier's Theorem 1 uses a weak existential/probabilistic availability statement and its proof silently assumes a stronger per-history guarantee. A defensible finite-history proposition is:

**Indistinguishability proposition.** Let H1 and H2 be admissible histories with the same verifier observation and same packet request at time t. If the packet is authorized in H1 and unauthorized in H2, any deterministic verifier using only that observation and request must either (i) deny the request in both histories or (ii) authorize the request in both histories, violating safety in H2. Thus no verifier can guarantee both universal safety and authorization of this request in H1.

Proof: the deterministic verifier's inputs are equal; hence its outputs are equal. If output=allow, unsafe in H2; if output=deny, the H1 request is not admitted. This is a simple indistinguishability argument, **not claimed original**.

This does not imply impossibility under all delayed observations: trusted leases, fencing, synchronous revocation, and different validity definitions change admissible histories.

## Phase B: Counterexample
World A: active binding; clocks (1,1,1). World B: revoked binding, with unobserved revocation; clocks (1,1,1). Causal vector test permits both; knowledge-based safe test denies. Vector clocks order *observed* events; they do not establish completeness of physical events.

## Phase C: Synthetic coordinated-revocation experiment
- Seed: 20261108; 300 trials, 100 ticks/trial, 64 rules.
- 25% per-tick probability of scheduling one rule update; delay uniform 1–5 ticks.
- Pending rules denied by selective and fair incremental methods; global barrier denies all rules during pending changes.
- Restrictive changes become effective at the modeled acknowledgment/commit tick. The model deliberately makes the authoritative `active` state available to the simulation; this is **not** an implementation of an independently auditable coordinator.
- Each tick evaluates all 64 rules; only active rules count toward legitimate-denial metrics.
- Results: see summary.json and results.csv.
- The fair incremental baseline uses exactly the same knowledge, rule footprint, and policy as selective CAE. Equality is intentional and scientifically important.
- Zero unsafe accepts are conditional on this simplified coordinator semantics, not a real-world guarantee.
- The simulator has no independent data-plane, packet traces, malicious coordinator, crash-recovery, unbounded network partitions, clock drift, proof sizes, or end-to-end costs.

## Phase D: Prior-art screening
1. Reitblatt, Foster, Rexford, Schlesinger, Walker, *Abstractions for Network Update*, SIGCOMM 2012, DOI 10.1145/2377677.2377748 — consistent per-packet/per-flow updates and safety-preserving transition mechanisms. https://doi.org/10.1145/2377677.2377748
2. Kazemian et al., *Real Time Network Policy Checking Using Header Space Analysis*, NSDI 2013 — NetPlumber incrementally checks policy using rule dependency graphs. https://www.usenix.org/conference/nsdi13/technical-sessions/presentation/kazemian

This is a **targeted screening**, not a systematic originality review. Causal clocks, buffering, and conditional fencing have substantial prior-art risk. More work is needed on distributed revocation, causal consistency, authorization, and P4/XDP enforcement.

## Phase E: Decision gate
**Current result: REDIRECT / CONDITIONAL CONTINUE.**
- Epistemic indistinguishability is useful for threat-model clarity but not yet novel.
- Simple causal vectors fail the unobserved-revocation counterexample.
- Coordinated selective authorization ties an equally informed baseline.
- Do not claim a new algorithm, line-rate throughput, or a novel impossibility theorem.

## Next falsifiable technical question
Can an **auditable revocation-fencing protocol with explicitly specified trust roots** bound stale authorizations and recover efficiently when evidence sources disagree, while outperforming equally informed fencing/consistent-update baselines in a defined failure model? If not, the contribution should shift to an empirically validated systems case study or be discontinued.

Next required work: protocol state machine (prepare, fence, acknowledge, commit, reconcile), explicit source-authority and Byzantine/non-Byzantine assumptions, exhaustive small-state model checking, crash/replay/drop faults, comparable existing protocols, and then an actual Linux testbed. Real-world zero-unsafe-accept claims require implementation validation beyond these experiments.
