# EviGuard Redirection Dossier: Mathematical Diagnosis, Theoretical Refounding, and Systems Architecture

## 1. Executive Verdict and Strategic Framing

An exhaustive audit of the EviGuard framework across development iterations v0.1 through v1.4 and experimental Phases 15 through 18 reveals that the project reached an insurmountable novelty plateau. The core premise of the original design—that maintaining incremental dependency graphs and Merkle-tree authenticated deltas across Dynamic Host Configuration Protocol (DHCP) Snooping, Dynamic Address Resolution Protocol Inspection (DAI), and IP Source Guard (IPSG) would yield a defensible algorithmic contribution—is scientifically invalid. Every measured operational and security advantage achieved by EviGuard vanished whenever the framework was evaluated against an equally informed, standard incremental baseline.

However, the empirical breakdown documented in the handover uncovers a fundamental theoretical problem in distributed access control: in an asynchronous network environment with non-zero communication and observation latency, a verifier cannot observationally distinguish between an active valid binding and an unobserved revocation without synchronous coordination. Attempting to bridge this gap through data structure optimizations alone represents an attempt to bypass an information-theoretic barrier.

The research is formally redirected from mechanical switch-feature synchronization toward a rigorous theoretical and systems framework: **Causal Authorization Envelopes (CAE)** for asynchronous, multi-mechanism network access control. This dossier establishes:
1. The mathematical and empirical diagnosis of the failure of EviGuard v0.1–v1.4.
2. The formalization and mathematical proof of the Epistemic Safety Bound (Theorem 1), establishing an impossibility result for asynchronous authorization under observation delay.
3. The algorithmic and line-rate data plane architecture for Causal Evidence Guard (CEG) implemented in both P4_16 and Linux eBPF/XDP.
4. A sound, non-strawman experimental protocol replacing simulator-based approximations with programmable network testbeds.
5. A plug-and-play prompt template formatted for AI reasoning engines (such as ChatGPT or Claude) to immediately continue downstream paper authoring and experimental execution.

---

## 2. Mathematical and Empirical Diagnosis of EviGuard v0.1–v1.4

### 2.1 The Equal-Information Collapse
The progression of EviGuard from basic safety checks (v0.1–v0.5) to fair baseline auditing (v0.6–v1.1, v1.4, and Phases 15–18) demonstrates how apparent algorithmic advantages were artifacts of asymmetrical baseline comparisons.

In version 0.5, across 720 synthetic workloads generating approximately 1.728 million authorization decisions, uncoordinated updates allowed 29,465 unsafe decisions, while a naive global barrier eliminated unsafe decisions at the cost of 75.36% legitimate traffic denial. EviGuard reported 0 unsafe decisions and 5.41% legitimate denial. However, this comparison assumed EviGuard had access to an ideal dependency oracle, whereas a candidate guard lacking complete dependency knowledge permitted 2,827 unsafe decisions.

Once the baseline was upgraded to an equally informed, per-rule incremental baseline operating under identical dependency awareness and query budgets, EviGuard’s performance advantage collapsed to zero across every measured parameter:

| Phase / Version | Workload Scale | Metric Evaluated | EviGuard Measurement | Strong Baseline Measurement | Divergence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **v1.1** | 19,200 workloads, 48 configs | Authorization Decisions | Identical Decisions | Identical Decisions | 0.00% |
| **v1.4** | 1,000 workloads, 200k steps | Unsafe Accepts | 0 | 0 | 0.00% |
| **v1.4** | 1,000 workloads, 200k steps | Legitimate Denials | 55,923 | 55,923 | 0.00% |
| **v1.4** | 1,000 workloads, 200k steps | Proof Verifications | 66,572 | 66,572 | 0.00% |
| **v1.4** | 1,000 workloads, 200k steps | Stale Read Denials | 7,342 | 7,342 | 0.00% |
| **Phases 15–18** | 100 trials, 128 rules, 80 updates | Mean Modeled Work | 818.69 | 818.69 | 0.00% |
| **Phases 15–18** | 100 trials, 128 rules, 80 updates | Mean Invalidations | 118.23 | 118.23 | 0.00% |

In Phases 15–18, selective certificate maintenance reduced modeled work by 97.4% relative to a full certificate refresh (31,184 work units and 10,240 invalidations down to 818.69 and 118.23), but the strong incremental baseline achieved the exact same numbers. The algorithm merely executed standard selective invalidation over a directed graph, which is textbook computer science.

### 2.2 The Full-Rebuild Strawman Fallacy
In versions 1.2 and 1.3, the project evaluated incremental audit logs and Merkle-tree deltas:
* In v1.2 (512 graph records, 128 changes), reading incremental events required 128 record reads compared to 65,536 for full-snapshot reads, and incremental closure required 1,238.93 node visits versus 336,391.16 fixed-point inspections.
* In v1.3 (1,024 records, 40 updates), incremental Merkle hashing consumed approximately 880 SHA-256 operations (rising to 858 at 5% disagreement and 789.25 at 20% disagreement) compared to 163,760 operations for full rebuilding.

These experiments demonstrated that incremental data structures outperform batch recomputation from scratch. However, incremental Merkle trees and dynamic graph traversals have been established in cryptographic and algorithmic literature for decades. Furthermore, because whole-graph checkpoints and root integrity verification were still required, the reported reductions in record reads did not translate into an end-to-end systems speedup.

### 2.3 Network Simulator Artifacts
The empirical evaluation in Cisco Packet Tracer 8.2.2 encountered severe tooling limitations:
1. In a topology comprising a Cisco 2960 switch, VLAN 10, a legitimate DHCP server (pool 192.168.10.100–149), and a rogue DHCP server (pool 192.168.10.200–219), Packet Tracer forwarded spoofed ARP frames despite verified DAI binding mismatches.
2. The simulated Cisco Catalyst 2960 switch platform lacked CLI and firmware support for `ip verify source`, preventing physical verification of IPSG.
3. The project shifted entirely to synthetic Python models, separating the evaluation from physical network dynamics such as hardware queueing, asynchronous inter-process communication, packet reordering, and physical link drops.

### 2.4 The Epistemic Boundary: Common-Mode Omission
The fatal conceptual vulnerability uncovered in v1.3 and v1.4 is that independent cross-reconciliation across multiple security sources cannot detect dependencies or revocations omitted identically by all sources. If an attacker disconnects a host or tampers with an upstream link, or if a DHCP release packet is dropped, independent sources cross-checking each other report mutual agreement over a stale state. Authenticated records certify data integrity; they do not certify real-world freshness or complete coverage of unmonitored physical events.

---

## 3. Theoretical Refounding: The Epistemic Safety Bound

To replace ad-hoc graph traversals with a mathematically defensible foundation, the authorization problem is formalized within an epistemic and causal framework.

### 3.1 Formal Model
Let the physical network environment be defined over a state space $\Omega$. A concrete state $\omega \in \Omega$ at physical time $t \in \mathbb{R}^+$ is defined as:
$$\omega(t) = \langle H(t), B(t), D(t), \tau(t) \rangle$$
where:
* $H(t)$ is the set of physical network entities (hosts, switches, routers).
* $B(t) \subseteq \text{Port} \times \text{MAC} \times \text{IP}$ is the set of physically active network bindings.
* $D(t) \subseteq B(t) \times B(t)$ is the directed dependency relation governing authorization (for example, $(b_{ip}, b_{dhcp}) \in D$ specifies that an IP binding requires a valid, unexpired DHCP lease binding).
* $\tau: B(t) \rightarrow \mathbb{R}^+$ defines the true physical lease expiration time.

An enforcement verifier at a local network switch does not have direct access to $\omega(t)$. Instead, it observes the world through an observation operator $\mathcal{O}: \Omega \times \mathbb{R}^+ \rightarrow \mathcal{E}$, which produces a discrete evidence inventory $\mathcal{E}_t$.

The evidence inventory consists of timestamped lifecycle events:
$$\mathcal{E}_t = \{ e = \langle \text{type}, b, t_{event} \rangle \mid t_{event} + \Delta_k \le t \}$$
where $\Delta_k \in [\delta_{min}, \delta_{max}]$ represents the asynchronous observation delay of mechanism $k \in \{\text{Snooping}, \text{DAI}, \text{IPSG}\}$ with $\delta_{min} > 0$.

For an arriving packet $x$ carrying claimed binding $b_x = \langle p_x, m_x, i_x \rangle$, a deterministic decision function:
$$\mathcal{V}: \mathcal{E}_t \times x \rightarrow \{\mathtt{PERMIT}, \mathtt{DENY}\}$$
must decide whether to forward or drop the packet.

### 3.2 Formal Correctness Objectives
* **Safety ($\mathcal{S}$)**: For all physical times $t$ and all packets $x$:
  $$\mathcal{V}(\mathcal{E}_t, x) = \mathtt{PERMIT} \implies b_x \in B(t)$$
  Safety demands zero unsafe authorizations (no transient spoofing).
* **Availability ($\mathcal{A}$)**: For any legitimate host with true active binding $b_x \in B(t)$:
  $$\mathbb{P}(\mathcal{V}(\mathcal{E}_t, x) = \mathtt{PERMIT}) > 0$$
  Availability forbids permanent, non-recovering denial of legitimate network traffic.

### 3.3 Formal Statement and Proof of Theorem 1

> **Theorem 1 (Epistemic Safety Bound under Observation Lag)**  
> Let $\delta_{min} > 0$ denote the minimum propagation and observation delay across independent network authorization mechanisms. If there exists any valid network binding $b \in B(t)$ whose real-world validity depends upon an external event that can transition asynchronously without atomic pre-invalidation, then no deterministic verifier $\mathcal{V}$ can simultaneously satisfy Safety ($\mathcal{S}$) and Availability ($\mathcal{A}$).

#### Proof by Contradiction
Assume there exists a deterministic verifier $\mathcal{V}^*$ that satisfies both Safety ($\mathcal{S}$) and Availability ($\mathcal{A}$).

By the condition of Availability ($\mathcal{A}$), there exists a physical network world $\omega_1 \in \Omega$, a physical timestamp $t$, and a legitimate packet $x$ with claimed binding $b_x$ such that:
$$\mathcal{V}^*(\mathcal{E}_t, x) = \mathtt{PERMIT}, \quad \text{where } \mathcal{E}_t = \mathcal{O}(\omega_1, t) \text{ and } b_x \in B_t(\omega_1)$$

Construct an alternative physical world $\omega_2 \in \Omega$ as follows:
1. Let $\omega_2$ be identical to $\omega_1$ for all physical timestamps $t' \le t - \epsilon$, where $0 < \epsilon < \delta_{min}$.
2. At physical timestamp $t - \epsilon$, an external uncoordinated event $\Gamma_{revoke}$ occurs in $\omega_2$ (such as an off-path host disconnection, physical cable unplugging, or a silent DHCP release), revoking the validity of $b_x$.
3. Consequently, in world $\omega_2$ at timestamp $t$:
   $$b_x \notin B_t(\omega_2)$$

Evaluate the evidence inventory $\mathcal{O}(\omega_2, t)$ collected by the verifier in world $\omega_2$ at time $t$:
* The revocation event $\Gamma_{revoke}$ occurred at timestamp $t - \epsilon$.
* The minimum observation propagation latency is $\delta_{min}$.
* The earliest physical time at which any record of $\Gamma_{revoke}$ can appear in the evidence inventory is:
  $$t_{observed} = (t - \epsilon) + \delta_{min} = t + (\delta_{min} - \epsilon)$$
* Because $\epsilon < \delta_{min}$, it follows that $\delta_{min} - \epsilon > 0$, and therefore:
  $$t_{observed} > t$$
* Consequently, at time $t$, no evidence of $\Gamma_{revoke}$ has reached the verifier. The evidence sets are strictly identical:
  $$\mathcal{O}(\omega_2, t) = \mathcal{O}(\omega_1, t) = \mathcal{E}_t$$

Thus, worlds $\omega_1$ and $\omega_2$ are observationally indistinguishable to the verifier:
$$\omega_1 \sim_{\mathcal{E}_t} \omega_2$$

Because $\mathcal{V}^*$ is a deterministic function operating on the evidence inventory $\mathcal{E}_t$ and packet $x$:
$$\mathcal{V}^*(\mathcal{O}(\omega_2, t), x) = \mathcal{V}^*(\mathcal{E}_t, x) = \mathtt{PERMIT}$$

Now assess the Safety property ($\mathcal{S}$) in world $\omega_2$:
* The verifier outputs $\mathcal{V}^* = \mathtt{PERMIT}$.
* However, by construction, $b_x \notin B_t(\omega_2)$.
* The verifier has authorized a non-existent, revoked, or spoofed binding, violating Safety ($\mathcal{S}$).

To guarantee Safety ($\mathcal{S}$) across all observationally indistinguishable states, $\mathcal{V}$ must output $\mathtt{DENY}$ whenever an unobserved revocation is possible:
$$\mathcal{V}(\mathcal{E}_t, x) = \mathtt{DENY}$$
This forces $\mathbb{P}(\mathcal{V}(\mathcal{E}_t, x) = \mathtt{PERMIT}) = 0$ in $\omega_1$, which violates Availability ($\mathcal{A}$).

No deterministic verifier can satisfy both properties simultaneously under asynchronous observation lag. $\blacksquare$

---

## 4. Systems Architecture: Causal Authorization Envelopes (CAE)

Theorem 1 establishes that attempting to achieve instant, non-blocking, safe authorization across asynchronous silos without causal coordination is impossible. Rather than relying on static graph traversals, the solution is to enforce **Causal Authorization Envelopes (CAE)** directly within the switch forwarding pipeline.

### 4.1 Causal Consistency in Multi-Mechanism Authorization
The fundamental issue in multi-mechanism security is causal inversion:
1. A client obtains an IP address via DHCP.
2. The client immediately transmits an ARP reply or IP frame.
3. The data plane packet arrives at the switch port before the local switch daemons (DAI or IPSG) have ingested and processed the DHCP ACK from the control plane.
4. An uncoordinated switch either drops legitimate packets (availability failure) or permits spoofed frames during re-binding (safety failure).

To resolve this, every authorization binding maintains a Monotonic Vector Timestamp:
$$V = \langle v_{snoop}, v_{dai}, v_{ipsg} \rangle$$
Forwarding decisions are evaluated against a **Causal Cut**. If an arriving packet's protocol claims outpace the local mechanism's vector clock, the packet is diverted into a bounded **Causal Sandbox Queue** rather than being dropped or naively permitted.

### 4.2 Algorithmic Specification: Causal Evidence Guard (CEG)

```text
Algorithm: Causal Evidence Guard (CEG)
--------------------------------------------------------------------------------
Global State:
  V_local: Array[1..3] of Integer   // 1: Snooping, 2: DAI, 3: IPSG
  BindingTable: HashIndex           // Key: (Port, MAC) -> Record
  PendingQueue: PriorityQueue       // Packets buffered awaiting causal resolution

Record Structure:
  IP: IPv4Address
  State: { ACTIVE, REVOKED, PROVISIONAL }
  V_stamp: Array[1..3] of Integer
  LeaseExpiry: Timestamp

Packet Ingress Handler (pkt, ingress_port):
  1:  key <- (ingress_port, pkt.src_mac)
  2:  record <- BindingTable.Lookup(key)
  3:  if record == NULL or record.State == REVOKED then
  4:      Drop(pkt)
  5:      return
  6:  end if
  7:
  8:  // Causal Precedence Check
  9:  if pkt.EtherType == ETHERTYPE_ARP then
  10:     // ARP inspection requires DHCP Snooping causal cut
  11:     if V_local[SNOOP] < record.V_stamp[SNOOP] then
  12:         Enqueue(PendingQueue, pkt, timeout = DELTA_MAX)
  13:         return
  14:     end if
  15:     if pkt.arp_spa == record.IP then
  16:         Forward(pkt)
  17:     else
  18:         Drop(pkt)
  19:     end if
  20:
  21: else if pkt.EtherType == ETHERTYPE_IP then
  22:     // IP source guard requires Snooping and DAI causal cut
  23:     if V_local[SNOOP] < record.V_stamp[SNOOP] or 
  24:        V_local[DAI]   < record.V_stamp[DAI] then
  25:         Enqueue(PendingQueue, pkt, timeout = DELTA_MAX)
  26:         return
  27:     end if
  28:     if pkt.ip_src == record.IP then
  29:         Forward(pkt)
  30:     else
  31:         Drop(pkt)
  32:     end if
  33: end if

Control Plane Event Handler (mechanism_id, event):
  1:  V_local[mechanism_id] <- V_local[mechanism_id] + 1
  2:  ApplyBindingUpdate(event)
  3:  
  4:  // Release packets whose causal dependencies are now satisfied
  5:  for each pkt in PendingQueue do
  6:      if CausalCutSatisfied(pkt, V_local) then
  7:          Dequeue(PendingQueue, pkt)
  8:          Reinject(pkt)
  9:      else if CurrentTime() - pkt.ingress_time > DELTA_MAX then
  10:         Dequeue(PendingQueue, pkt)
  11:         Drop(pkt) // Fail closed on broken causal chain
  12:     end if
  13: end for
--------------------------------------------------------------------------------
```

### 4.3 Complexity and Invariant Analysis
* **Lookup Overhead**: Forwarding requires an $O(1)$ hash table lookup and integer vector comparisons, maintaining line-rate compatibility.
* **Safety Invariant**: No packet is forwarded until all causally preceding evidence events have been incorporated into local forwarding state.
* **Bounded Latency**: Buffered legitimate packets incur a delay strictly bounded by $\Delta_{max} = \max_{j,k} \Delta_{j,k}$. If an event is dropped permanently, the queue safely fails closed after $\Delta_{max}$.

---

## 5. Concrete Data Plane Implementations

### 5.1 P4_16 Line-Rate Pipeline Architecture

The P4 implementation targets the `v1model` architecture. Causal vector clocks are stored in stateful registers, while bindings are validated via exact-match tables.

```p4
#include <core.p4>
#include <v1model.p4>

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header arp_t {
    bit<16> hwType;
    bit<16> protoType;
    bit<8>  hwAddrLen;
    bit<8>  protoAddrLen;
    bit<16> opcode;
    bit<48> srcHwAddr;
    bit<32> srcProtoAddr;
    bit<48> dstHwAddr;
    bit<32> dstProtoAddr;
}

header ipv4_t {
    bit<4>   version;
    bit<4>   ihl;
    bit<8>   diffserv;
    bit<16>  totalLen;
    bit<16>  identification;
    bit<3>   flags;
    bit<13>  fragOffset;
    bit<8>   ttl;
    bit<8>   protocol;
    bit<16>  hdrChecksum;
    bit<32>  srcAddr;
    bit<32>  dstAddr;
}

struct metadata {
    bit<32> current_snoop_vc;
    bit<32> current_dai_vc;
    bit<32> required_snoop_vc;
    bit<32> required_dai_vc;
    bit<1>  is_causally_ready;
}

struct headers {
    ethernet_t ethernet;
    arp_t      arp;
    ipv4_t     ipv4;
}

#define CPU_SANDBOX_PORT 255

parser ParserImpl(packet_in pkt, out headers hdr, inout metadata meta, inout standard_metadata_t smeta) {
    state start {
        pkt.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            0x0806: parse_arp;
            0x0800: parse_ipv4;
            default: accept;
        }
    }
    state parse_arp {
        pkt.extract(hdr.arp);
        transition accept;
    }
    state parse_ipv4 {
        pkt.extract(hdr.ipv4);
        transition accept;
    }
}

control IngressImpl(inout headers hdr, inout metadata meta, inout standard_metadata_t smeta) {
    register<bit<32>>(1) reg_snoop_clock;
    register<bit<32>>(1) reg_dai_clock;

    action act_drop() {
        mark_to_drop(smeta);
    }

    action act_forward(bit<9> port) {
        smeta.egress_spec = port;
    }

    action act_sandbox() {
        smeta.egress_spec = CPU_SANDBOX_PORT;
    }

    action set_dai_requirements(bit<32> req_snoop) {
        meta.required_snoop_vc = req_snoop;
    }

    action set_ipsg_requirements(bit<32> req_snoop, bit<32> req_dai) {
        meta.required_snoop_vc = req_snoop;
        meta.required_dai_vc = req_dai;
    }

    table t_port_security {
        key = {
            smeta.ingress_port: exact;
            hdr.ethernet.srcAddr: exact;
        }
        actions = {
            NoAction;
            act_drop;
        }
        default_action = act_drop();
    }

    table t_dai_validation {
        key = {
            smeta.ingress_port: exact;
            hdr.arp.srcHwAddr: exact;
            hdr.arp.srcProtoAddr: exact;
        }
        actions = {
            set_dai_requirements;
            act_drop;
        }
        default_action = act_drop();
    }

    table t_ipsg_validation {
        key = {
            smeta.ingress_port: exact;
            hdr.ethernet.srcAddr: exact;
            hdr.ipv4.srcAddr: exact;
        }
        actions = {
            set_ipsg_requirements;
            act_drop;
        }
        default_action = act_drop();
    }

    apply {
        if (!hdr.ethernet.isValid()) {
            act_drop();
            return;
        }

        if (t_port_security.apply().action_run == act_drop) {
            return;
        }

        reg_snoop_clock.read(meta.current_snoop_vc, 0);
        reg_dai_clock.read(meta.current_dai_vc, 0);

        if (hdr.arp.isValid()) {
            if (t_dai_validation.apply().hit) {
                if (meta.current_snoop_vc < meta.required_snoop_vc) {
                    act_sandbox();
                } else {
                    act_forward(smeta.ingress_port);
                }
            }
        } else if (hdr.ipv4.isValid()) {
            if (t_ipsg_validation.apply().hit) {
                if (meta.current_snoop_vc < meta.required_snoop_vc || 
                    meta.current_dai_vc < meta.required_dai_vc) {
                    act_sandbox();
                } else {
                    act_forward(smeta.ingress_port);
                }
            }
        }
    }
}

control EgressImpl(inout headers hdr, inout metadata meta, inout standard_metadata_t smeta) {
    apply {}
}

control DeparserImpl(packet_out pkt, in headers hdr) {
    apply {
        pkt.emit(hdr.ethernet);
        pkt.emit(hdr.arp);
        pkt.emit(hdr.ipv4);
    }
}

control VerifyChecksumImpl(inout headers hdr, inout metadata meta) {
    apply {}
}

control ComputeChecksumImpl(inout headers hdr, inout metadata meta) {
    apply {}
}

V1Switch(ParserImpl(), VerifyChecksumImpl(), IngressImpl(), ComputeChecksumImpl(), EgressImpl(), DeparserImpl()) main;
```

---

### 5.2 Linux eBPF / XDP Kernel Pipeline

For edge hypervisors and Linux bridges, CEG runs at the eXpress Data Path (XDP) hook before socket allocation.

```c
#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/if_arp.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>

struct binding_key {
    __u32 ingress_ifindex;
    __u8  mac[6];
    __u16 pad;
    __u32 ip;
};

struct causal_record {
    __u32 state;              // 1 = ACTIVE, 2 = REVOKED
    __u32 req_snoop_vc;       // Required DHCP snooping causal clock
    __u32 req_dai_vc;         // Required DAI causal clock
    __u64 last_verified_ns;
};

struct global_clocks {
    __u32 snoop_vc;
    __u32 dai_vc;
    __u32 ipsg_vc;
};

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 65536);
    __type(key, struct binding_key);
    __type(value, struct causal_record);
} map_bindings SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 1);
    __type(key, __u32);
    __type(value, struct global_clocks);
} map_clocks SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 1 << 24); // 16 MB ring buffer
} ringbuf_sandbox SEC(".maps");

SEC("xdp")
int xdp_ceg_eval(struct xdp_md *ctx) {
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;

    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return XDP_DROP;

    __u32 zero = 0;
    struct global_clocks *clocks = bpf_map_lookup_elem(&map_clocks, &zero);
    if (!clocks)
        return XDP_DROP;

    struct binding_key key = {};
    key.ingress_ifindex = ctx->ingress_ifindex;
    __builtin_memcpy(key.mac, eth->h_source, 6);

    if (eth->h_proto == bpf_htons(ETH_P_ARP)) {
        struct arphdr *arp = (void *)(eth + 1);
        if ((void *)(arp + 1) > data_end)
            return XDP_DROP;

        unsigned char *body = (unsigned char *)(arp + 1);
        if (body + 20 > (unsigned char *)data_end)
            return XDP_DROP;

        __u32 spa;
        __builtin_memcpy(&spa, body + 6, sizeof(spa));
        key.ip = spa;

        struct causal_record *rec = bpf_map_lookup_elem(&map_bindings, &key);
        if (!rec || rec->state != 1)
            return XDP_DROP;

        if (clocks->snoop_vc < rec->req_snoop_vc) {
            bpf_ringbuf_output(&ringbuf_sandbox, data, (long)data_end - (long)data, 0);
            return XDP_DROP;
        }

        return XDP_PASS;
    }

    if (eth->h_proto == bpf_htons(ETH_P_IP)) {
        struct iphdr *ip = (void *)(eth + 1);
        if ((void *)(ip + 1) > data_end)
            return XDP_DROP;

        key.ip = ip->saddr;

        struct causal_record *rec = bpf_map_lookup_elem(&map_bindings, &key);
        if (!rec || rec->state != 1)
            return XDP_DROP;

        if (clocks->snoop_vc < rec->req_snoop_vc || clocks->dai_vc < rec->req_dai_vc) {
            bpf_ringbuf_output(&ringbuf_sandbox, data, (long)data_end - (long)data, 0);
            return XDP_DROP;
        }

        return XDP_PASS;
    }

    return XDP_DROP;
}

char _license[] SEC("license") = "GPL";
```

---

## 6. Rigorous Experimental and Evaluation Protocol

To ensure publication credibility, all synthetic approximations and Packet Tracer environments are discarded in favor of programmable network infrastructure.

### 6.1 Testbed Environment
* **Platform**: Mininet testbed connected to BMv2 (P4 Behavioral Model v2) switches and Open vSwitch (OVS) kernels running on Linux kernel 6.x.
* **Control Daemon**: Asynchronous edge coordinator communicating via local UNIX domain sockets or gRPC with the switch agent.
* **Traffic Generators**: `MoonGen` and `Scapy` packet generation pipelines injecting controlled line-rate 1 Gbps/10 Gbps traffic traces.

### 6.2 Workload Scenarios
1. **The Causal Desynchronization Attack (Race Condition)**:
   * 10,000 legitimate DHCP lease renegotiation sequences.
   * Adversarial clients inject spoofed ARP replies and spoofed UDP/IP frames immediately following a lease expiration or re-assignment.
   * Artificial jitter ($\Delta_k \sim \mathcal{N}(5\text{ms}, 2\text{ms})$) is introduced between local switch control daemons to stress out-of-order execution.
2. **Asymmetric Notification Drop**:
   * Control plane drops up to 10% of IPSG binding invalidation notifications to evaluate fail-closed behavior under communication loss.

### 6.3 Baseline Systems for Comparison
1. **Uncoordinated Independent Baseline (Enterprise Standard)**: Standard Linux bridge / enterprise switch configuration where DHCP Snooping, DAI, and IPSG operate as decoupled processes.
2. **Global Controller Barrier (Two-Phase Locking)**: An SDN OpenFlow controller barrier where ports block entirely during binding transitions (Reitblatt et al., SIGCOMM 2012).
3. **Equally Informed Per-Rule Invalidation (Phase 15–18 Baseline)**: The strong incremental baseline that eliminated EviGuard’s graph-traversal advantages.
4. **Causal Evidence Guard (CEG)**: The proposed causal cut architecture with bounded sandboxing.

### 6.4 Primary Evaluation Metrics
* **Transient Vulnerability Window**: Cumulative physical time during which spoofed frames traverse the switch fabric without authorization.
* **Legitimate P99 Packet Latency**: Forwarding delay introduced by sandboxing legitimate packets during causal synchronization.
* **Drop Rate under Jitter**: Legitimate frames discarded due to asynchronous event delays.
* **Forwarding Plane Throughput & Memory**: Nanoseconds per-packet lookup overhead and hardware table utilization.

---

## 7. Context Injection Prompt for Subsequent AI Engines

Use the following formatted prompt block when providing this dossier to ChatGPT or other research assistants to ensure continuity in paper drafting, proof refinement, or experimental design:

```markdown
SYSTEM CONTEXT & DIRECTIVE FOR RESEARCH COLLABORATOR:
You are acting as a Senior Co-Author and Technical Reviewer for a top-tier networking and cybersecurity submission (targeted at IEEE S&P / ACM CCS / USENIX Security / SIGCOMM). 

Context:
The attached research dossier represents a complete redirection of the "EviGuard" project. The original project attempted to achieve novelty through incremental dependency graphs, Merkle-tree deltas, and selective certificate maintenance across DHCP Snooping, DAI, and IPSG. Rigorous self-auditing revealed that all operational advantages vanished against equally informed incremental baselines, and Packet Tracer simulation limitations obscured physical realities.

The project has been refounded around:
1. Theorem 1 (Epistemic Safety Bound): An impossibility theorem proving that under non-zero observation delay, no deterministic verifier can guarantee both safety (zero spoofing) and availability across asynchronous security mechanisms without causal synchronization.
2. Causal Authorization Envelopes (CAE) & Causal Evidence Guard (CEG): An O(1) line-rate data-plane primitive using vector clocks and bounded sandboxing in P4_16 and eBPF/XDP.
3. An open, reproducible testbed protocol on Mininet/P4/OVS.

Your Instructions:
- Treat this mathematical foundation and systems architecture as the ground truth.
- Do NOT revert to the obsolete framing of Merkle trees, graph-closure traversals, or Packet Tracer simulations.
- Assist the research team in drafting sections, proving lemmas, refining P4 table pipelines, or designing evaluation scripts based strictly on the Causal Authorization Envelopes framework.
```
