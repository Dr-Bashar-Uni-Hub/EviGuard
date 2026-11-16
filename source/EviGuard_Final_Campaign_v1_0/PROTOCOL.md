# EviGuard bounded final campaign — preregistered protocol v1.0

## Status and purpose
Frozen EviGuard v1.2 and Phases 1.3–1.6 are historical evidence; this campaign never edits them. The goal is to evaluate failure exposure and determine whether a reproducible systems-evaluation paper is feasible. This is NOT an originality proof and NOT a faithful RFC 7513 SAVI implementation.

## Primary research questions
RQ1: In a transparent, event-driven abstraction, how does delay between external revocation and kernel drop installation affect post-revocation packet exposure?
RQ2: How do notification loss, failed installation, and controller unavailability change exposure and recovery?
RQ3: Does CACV differ from an equally informed temporal reference under exactly matched inputs and fault schedules?

## Predefined experiments
E0: validate integrity and schema of original v1.2 archive, without altering it.
E1: deterministic discrete-event fault-model simulation, 5 seeds [11,23,37,53,71], 3 notification delays [0, 25, 100] ms, 3 install delays [0, 25, 100] ms, and 4 fault types [none, notify_loss, install_failure, controller_crash]. 180 paired scenarios total. Packet arrivals at 10, 30, 60, 120, 250 ms relative to external revocation. If a notification is lost or the controller crashes before handling it, no drop is installed in the modeled 300 ms horizon. If installation fails, no retry is modeled. A zero-delay install can occur at t=0 and precedes packets.
E2: paired comparison of EviGuard and an equally informed reference with identical decision semantics. This tests implementation agreement under the model, not superiority.

## Measures
- `post_revocation_deliveries`: packets delivered at t>0 while stale allow remains installed.
- `drop_commit_ms`: time kernel drop would be installed; null means no drop within horizon.
- `exposure_ms_capped`: min(drop_commit_ms, 300), or 300 when no commit. This is a censored modeling metric, not a measured real latency.
- `policy_disagreements`: paired outcome differences.
- Report full per-scenario JSONL, aggregate CSV, verification JSON and environment manifest.

## Acceptance gates
G1 integrity: original results archive SHA-256 is recorded and tar member names pass safety checks; optional original source ZIP hash recorded.
G2 reproducibility: same seed and config give byte-identical scenario results; independent checks verify all model invariants.
G3 honesty: zero policy differences means no superiority claim. Any positive result from an intentionally weaker baseline is labeled information advantage, not novel algorithm.
G4 publication: even if G1–G3 pass, the manuscript remains CONDITIONAL until (a) an independently implemented published/properly scoped source-guard baseline, (b) real privileged fault-injection runs, (c) multi-client/load trials and measured kernel/packet timing, and (d) related-work comparison are completed. This package DOES NOT implement those items.

## Model boundaries and threats to validity
No Linux kernel enforcement in E1/E2; no real packet captures, no synchronized hardware timestamps, no distributed model checking, no authentic SAVI or versioned-fencing baseline, no retries, no recovery after crash, and no lease expiry. Ground truth changes at external revoke t=0. Packet delivery is modeled as permitted if the kernel has not yet installed drop. The model is intentionally simple and its agreement is unsurprising.

## Stop rule
If E2 yields no distinction and no additional systems question survives the literature review, stop algorithmic novelty exploration. Do not launch more equivalent-policy phases. For JISA, assess whether a failure-focused reproducible systems benchmark is sufficient before drafting submission claims.
