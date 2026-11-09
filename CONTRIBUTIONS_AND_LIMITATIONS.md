# Engineering and experimental contributions

EviGuard integrates DHCP-derived binding evidence, local IP/interface state, ARP neighbor observations, authorization decisions, and Linux nftables enforcement in an inspectable controller workflow.

## Demonstrated contributions

1. **Integrated architecture:** explicit evidence collection, policy decision, and kernel enforcement stages.
2. **Operational Linux testbed:** DHCP acquisition, authorization, revocation, reacquisition, and packet-level verification using namespaces and veth.
3. **Matched enforcement evaluation:** real observation snapshots replayed into separate EviGuard and reference kernel environments.
4. **Failure analysis:** bounded event-ordering and an offline synthetic fault campaign examining delayed notification, missing notification, failed installation, and controller interruption.
5. **Transparent reproducibility:** preservation of successful experiments, failed attempts, corrected scripts, assumptions, and negative findings.

## What the results do not show

- No demonstrated new authorization algorithm or superiority over an equally informed policy reference.
- No faithful published SAVI baseline implemented and benchmarked.
- No real Linux fault injection in the 180-scenario campaign.
- No instantaneous revocation guarantee or proof of zero in-flight packet deliveries at the exact revocation boundary.
- No claim that zero disagreements in the sampled tests proves universal equivalence.

## Related foundations

- RFC 7039 — Source Address Validation Improvement (SAVI) Framework.
- RFC 7513 — Source Address Validation Improvement (SAVI) Solution for DHCP.
- Reitblatt et al. (2012) — consistent network updates.
- VeriFlow (2013) — real-time network-wide invariant verification.
- NetPlumber (2013) — incremental network-policy verification.

The manuscript is a systems engineering and experimental evaluation study; its novelty must be assessed at the integration and evidence-methodology level, with appropriate prior-art qualifications.
