---
id: PE-001
title: Infrastructure & Network Architecture Design
category: 10 — Infrastructure, DevOps & Environments
code: PE
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering Lead
approver: CTO with Design Authority (constituted under GV-002)
standards_basis: >
  ISO/IEC/IEEE 42010:2022 deployment viewpoint (via AR-001 §8) · NIST SP 800-207 zero trust ·
  RFC 1918 / RFC 6890 address planning · TLS 1.3 (RFC 8446) · DNSSEC (RFC 4033) ·
  CIS Benchmarks · Uptime Institute Tier topology · Bangladesh Bank Guideline on ICT Security v4.0
traces_to: >
  PGD-000 PE-001 · AR-001 §8.1 trust zones, §8.3 split residency, §8.5 environment ladder ·
  02-05 §8 · Technology Stack §21.3 · SC-001 §5.2 · SC-007 §5, §9 · IN-001 §3.2, §8 ·
  audit OP-01 (critical), OP-02 · NFR-006, NFR-007, NFR-045, NFR-046, NFR-048, NFR-086
depends_on: AR-001 · SC-001 · SC-007 · IN-001
verified_on: 2026-08-19
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-19 01:15 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# PE-001 — Infrastructure & Network Architecture Design

### Category 10 · Code `PE` · ISO/IEC/IEEE 42010:2022 deployment viewpoint · NIST SP 800-207

---

> **What was on disk before this document, enumerated 2026-08-19 01:15 (+06):**
>
> | Measure | Count |
> |---|---:|
> | Files in the four source repositories | **621** |
> | Of those, containing a **network diagram, address plan, subnet or security-group design** | **0** |
> | Occurrences of "Terraform" | **0** |
> | Occurrences of "VPC", "subnet" or "CIDR" | **0** |
> | Infrastructure content in `02-05` §8 | **one compute sizing table and a cost progression** |
> | Environments sized in `02-05` §8.1 | **five of the six `02-05` §9 names** — `dr` appears in no sizing table (`OP-02`) |
>
> `AR-001` §8.1 defines **six trust zones** and states that the zone model *"is the input to `SC-002`
> and to `PE-001`; neither can start without it."* `SC-001` §5.2 built the security architecture on
> those zones. **This document builds the network.** A shopping list of virtual machines is not an
> infrastructure design, and `02-05` §8 is a shopping list.

---

## 1. Purpose

This document specifies **where the system runs and how its parts reach each other**: regions and
sites, the network realisation of `AR-001`'s six trust zones, address planning, segmentation and
security-group policy, ingress and egress paths, DNS and TLS, private connectivity, the
split-residency topology and the cross-border link it does *not* have, branch and field
connectivity, and the high-availability topology that makes the estate's four different availability
targets achievable.

It exists because every other document in this category, and several outside it, are blocked on it:
`PE-002` cannot place an environment without a network to place it in, `PE-003` cannot write an IaC
module without a resource topology to encode, `PE-007` cannot design failover without a second site,
and `SC-002`'s threat model has been enumerating attack paths across a network nobody had drawn.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **Sites and regions** — how many, where, and why |
| 2 | The network realisation of `AR-001` §8.1's **six trust zones** |
| 3 | **Address planning** — a non-overlapping RFC 1918 allocation across all environments and sites |
| 4 | Segmentation, security groups and the **default-deny** posture |
| 5 | **Ingress** — CDN, WAF, load balancing, TLS termination, gateway placement |
| 6 | **Egress** — the Z6 outbound proxy and the allow-list that makes `IP-10` a mechanism |
| 7 | DNS, certificate management and rotation |
| 8 | **Private connectivity** — how sites, environments and the resident store reach one another |
| 9 | The **split-residency topology**, and the cross-border path that is deliberately absent |
| 10 | **Branch and field connectivity** — 51+ branches, 200–400 technicians on Android |
| 11 | High availability at the network tier |
| 12 | The **flow-down obligations** from Bangladesh Bank-regulated counterparties |
| 13 | Fitness functions `FF-101`…`FF-110` |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Environment inventory, purpose, data class, refresh | **`PE-002`** | This document says *where* an environment can exist; `PE-002` says *which* exist and *why* |
| The IaC that builds it | **`PE-003`** | Design vs encoding |
| Container and orchestration topology | **`PE-005`** | This document delivers the network a cluster sits in |
| Capacity, sizing and growth | **`PE-006`** | `AR-001` §8.6 fixes the sizing *basis*; `PE-006` publishes the numbers |
| Backup, DR procedure and drills | **`PE-007`** | This document provisions the **second site**; `PE-007` designs the failover |
| Monitoring, SLOs, alert rules | **`PE-008`** | |
| Secrets and configuration | **`PE-009`** | |
| Security control selection, threat model | `SC-001`, `SC-002` | `SC-001` §5.2 is the control set; this is the topology it runs on |
| The residency classification and transfer gate | `SC-007` | This document builds the two stores; `SC-007` rules what may cross |
| Identity, authentication, authorisation | `SC-004`, M29 | Network position never grants access (§4.6) |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **`PE-002`, `PE-003`, `PE-005`, `PE-007` authors** | §3 sites, §4 zones, §5 addressing are their substrate |
| Platform engineers | The whole document is the build specification |
| `SC-002` threat modeller | §4 and §6 are the attack surface, finally drawn |
| Network and security operations | §6, §7, §8 and §12 |
| CFO and CTO | §3.4 — the second site is the largest unbudgeted infrastructure decision |
| Auditors, and counterparty auditors | §12 — the right-to-audit and physical-security obligations |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Concept | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO/IEC/IEEE 42010:2022** | Deployment viewpoint | Realises `AR-001` VP-6; the zone and tier models are inherited, not re-derived | None |
| **NIST SP 800-207** zero trust | No implicit trust from network location | §4.6 — **network position never grants access**; every call authenticates and authorises regardless of zone | **Partial adoption, stated.** The estate retains network segmentation as defence in depth rather than adopting a purely identity-based perimeter. §4.6 says why |
| **RFC 1918 / RFC 6890** | Private address space | §5's allocation plan | None |
| **TLS 1.3 (RFC 8446)** | Transport security | §7.2 — TLS 1.3 at the edge, mTLS between services | TLS 1.2 permitted **only** where a named external counterparty cannot negotiate 1.3, recorded per counterparty in `IN-004` |
| **DNSSEC (RFC 4033)** | DNS integrity | §7.1 | |
| **CIS Benchmarks** | Host and network hardening | §11 baseline | Applied through `PE-003` modules, not by hand |
| **Uptime Institute Tier topology** | Facility resilience | §3.3 — the resident site's tier is a **selection criterion**, not an assumption | |
| **Bangladesh Bank, Guideline on ICT Security v4.0 (April 2023)** and *Guidelines on Cloud Computing* | Data-centre, outsourcing and audit obligations | §12 — **flow-down**, not direct applicability | 1000FiX is **not** a Bangladesh Bank-regulated entity. §12.1 states precisely why it is nonetheless bound |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `AR-001` §8.1 | `../02_Architecture_and_Design/AR-001_*.md` | **The six trust zones `Z0`–`Z6`** and the two rules that follow |
| Ibid. §8.2, §8.3 | | Six data isolation tiers `T0`–`T5`; the split-residency topology and `CD-233` |
| Ibid. §8.4, §8.5, §8.6 | | `DR-01`…`DR-04`; the environment ladder; the sizing basis |
| `SC-001` §5.2 | `../05_Security_Privacy_and_Compliance/SC-001_*.md` | The security control set this topology must carry |
| `SC-007` §5, §9 | Ibid. | The split-record design; **the three DR routes and the option A/B/C choice** |
| `IN-001` §3.2, §8 | `../04_Integration_and_API_Engineering/IN-001_*.md` | Component allocation; the anticorruption boundary; **Z6 egress allow-list** |
| Technology Stack §21.1, §21.3 | `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` | Steady-state sizing including the resident store; the HA design per tier |
| Ibid. §17.1 | | The observability data path this network must carry |
| `02-05` §8, §9 | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` | Compute sizing, cost progression, the six-environment name list |
| `AUDIT-017` `OP-01`, `OP-02` | `../../project_content/_AUDIT/AUDIT-017_*.md` | **The two findings this category exists to close** |
| `05-06` | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_*.md` | `NFR-006`, `-007`, `-045`, `-046`, `-048`, `-049`, `-061`, `-086` |

**Reproducible extraction**, run at **2026-08-19 01:15 (+06)**:

```bash
# What infrastructure design existed before this document
grep -ril 'terraform\|opentofu'  --include=*.md . | wc -l      # → 0
grep -ril '\bVPC\b\|subnet\|CIDR' --include=*.md . | wc -l      # → 0
grep -ril 'security group\|network diagram' --include=*.md . | wc -l   # → 0

# Environments named in 02-05 §9 vs sized in 02-05 §8.1
#   named: local dev staging training prod dr            (6)
#   sized: the §8.1 table carries no environment column   (0 by environment)
```

### 2.3 Audit findings this document closes or contributes to

| Finding | Source | Disposition |
|---|---|---|
| **`OP-02` (high)** — the `dr` environment is *"named in the architecture and provisioned nowhere"* | `AUDIT-017` | **Contributes decisively.** §3.2 provisions a second site and §3.4 costs it. **Closes with `PE-002` (sizing) and `PE-007` (procedure)** |
| **`OP-01` (critical)** — no lawful DR path for Bangladesh-resident personal data | `AUDIT-017` | **Contributes the missing half.** `SC-007` §9.4 recommended option A — *"provision a Bangladesh-resident DR target"* — and could not name one. **§3.3 names three candidate in-country facilities and the selection criteria.** Closes with `PE-007` and a CTO decision |
| `AR-001` §8.1 — *"the zone model is the input to `SC-002` and `PE-001`; neither can start without it"* | `AR-001` | §4 realises it |
| `SC-001` §5.2 — the control set requires a topology | `SC-001` | §4, §6, §7 |
| `GV-008` `Q-03` — *"What does a Bangladesh-resident data store cost?"* | `GV-008` | **Contributes the shape**; `PE-006` publishes the figure |
| `IN-001` `FF-44` — every outbound destination on the Z6 allow-list | `IN-001` | §6.3 builds the mechanism the check tests |

---

## 3. Sites and Regions

### 3.1 The decision

> **Ruling `PE-001-D-01`. Two sites, in two jurisdictions, with a third for backup custody.**

| Site | Role | Jurisdiction | Carries |
|---|---|---|---|
| **`RGN-P`** Regional primary | Production for everything except residency-classified data | Regional cloud (Singapore or equivalent, `Q-01`) | `Z0`–`Z3`, `Z5`, `Z6`; all environments except the resident tier |
| **`BD-R`** Bangladesh resident | **`Z4` only** — the residency-classified store and its key material | **Bangladesh, in country** | `Z4` production **and** `Z4` standby |
| **`RGN-S`** Regional standby | Warm standby for `RGN-P` | A **second failure domain** — a different availability zone or region from `RGN-P` | `dr` for the regional tier |
| **`BKP-3`** Backup custody | **Immutable backup copy outside the primary provider account** | A third party or a separate account | Backup objects only. No compute |

### 3.2 Why a warm standby and not a hot second region

| Option | Cost | RTO | Assessment |
|---|---|---|---|
| Single site, backups only | Lowest | **Days** | Fails `NFR-007` (RTO ≤ 2 h) by two orders of magnitude |
| **Warm standby** — replicated data, minimal compute, scaled on failover | Moderate | **≤ 2 h** achievable | ✅ **Chosen.** Matches `NFR-007` and Technology Stack §21.3's own DR row |
| Hot active-active | Highest | Minutes | Requires multi-master data resolution the domain model does not support (`AR-009` §4.2 ordering is per-aggregate, not global) |

**`BKP-3` is separate from `RGN-S` and is not optional.** `OP-02` records that *"an immutable backup
copy outside the primary provider account"* is unprovisioned, and that without it **the ransomware
and account-compromise scenarios in `OP-012` §5 have no assured recovery path**. A standby inside the
same provider account shares the blast radius of a credential compromise.

### 3.3 `BD-R` — the site `OP-01` and `SC-007` require and neither could name

`SC-007` §9.4 assessed three options and recommended **A + B**: provision a Bangladesh-resident DR
target, *and* obtain the Authority's written position for the residual case. It could go no further,
because *"`SC-007` cannot choose; it can only make the choice explicit."*

**This document makes option A concrete.** In-country facilities exist, and their existence is the
fact that converts option A from a proposal into a procurement. Verified **2026-08-19**:

| Candidate | Position | Relevance |
|---|---|---|
| **BDCCL National Data Center**, Kaliakoir Hi-Tech Park, Gazipur | **Tier IV**, with Uptime Institute *Tier Certification of Operational Sustainability*; state-owned; offers colocation, cloud and storage | The highest facility tier available in country. State ownership is a **consideration in both directions** — §3.5 |
| **BDCOLO** | Carrier-neutral **Tier III**, 2N redundancy; colocation, cloud, dedicated servers | Carrier neutrality matters for §8's connectivity |
| **Felicity IDC** | **Tier III**, **PCI-DSS certified**; private cloud marketed for BFSI data-residency needs | PCI-DSS certification is directly relevant to §12's flow-down |

> **`PE-001-F-01`. The absence of a named in-country facility was never a technical constraint.**
> `OP-01` has been open as **critical** since it was raised, and `SC-007` §9.5 states that until
> option A or B is in place *"`NFR-007` does not apply to residency-classified data, and the
> programme must say so."* Three certified facilities are available, one of them Tier IV. **The gap
> is a procurement decision that nobody has been asked to take**, not an unavailable capability.
> Raised to `GV-005` and the CTO; `Q-02`.

### 3.4 What `BD-R` costs, in shape

`GV-008` §4.3 carries infrastructure at **$52K–$96K over three years** and records explicitly that
the figure **excludes the Bangladesh-resident store**; `GV-008` `Q-03` asks what it costs and
`GV-008-D-03` says the answer requires `PE-001`–`PE-006`.

**The shape, stated here so `PE-006` can put numbers on it:**

| Element | Driver | Relative scale |
|---|---|---|
| `Z4` production HA pair | `AR-001` §8.6 — **"regulatory, not volume"**: a few hundred GB | Small compute, small storage |
| `Z4` **standby** | The same again, for DR | Small compute, small storage |
| In-country **key custody** (`SC-006` `ES-3`) | Separate key material, in country | HSM or managed KMS — **the disproportionate line** |
| Cross-border private link `RGN-P` ↔ `BD-R` | Every `CD-233` call traverses it | Bandwidth is low; **latency and availability are the constraints** |
| Facility, power, cooling, hands | Colocation or in-country cloud | Facility tier drives it |

> **The cost is dominated by availability and key custody, not by volume.** A design that sizes
> `BD-R` from data volume will under-provision it: `Z4` gates **every `T5` read in the system**
> (`AR-001` §8.2), so its availability requirement is at least that of the estate as a whole.

### 3.5 The two considerations `BD-R` selection must weigh

| # | Consideration |
|---|---|
| **SEL-01** | **Facility tier and certification.** Tier III minimum; Tier IV preferred. Uptime Institute certification of *operational sustainability*, not merely of design |
| **SEL-02** | **Carrier neutrality.** A single-carrier facility makes §8's private link a single point of failure |
| **SEL-03** | **Right of audit**, for 1000FiX and — under §12 — for a counterparty's regulator |
| **SEL-04** | **State ownership cuts both ways.** A state facility carries strong sovereignty alignment and may simplify the `NFR-086b` conversation; it also places the residency-classified store inside government-operated infrastructure, which is a matter for Legal Counsel and the DPO to assess against the same statute. **Recorded, not decided** |
| **SEL-05** | **Exit.** What it takes to leave, and how long the data takes to move, before it is entered |

---

## 4. The Six Trust Zones, Realised

`AR-001` §8.1 defines the zones. This section builds them.

### 4.1 The zone-to-network mapping

| Zone | `AR-001` contents | Network realisation | Ingress permitted from | Egress permitted to |
|---|---|---|---|---|
| **`Z0`** Public edge | CDN, WAF (OWASP CRS), DDoS, bot management | **Provider edge** — no 1000FiX-managed subnet | Internet | `Z1` **only** |
| **`Z1`** Ingress | Kong 3.x, Nginx 1.27 | Public subnets, one per availability zone, behind a load balancer | `Z0` only | `Z2`, `Z3` |
| **`Z2`** Application | Odoo nodes, Next.js nodes, 16 domain services | **Private** subnets, no public IP, no internet gateway route | `Z1` | `Z3`, `Z4` **via `CD-233` only**, `Z6` |
| **`Z3`** Data — regional | PostgreSQL primary + 2 replicas, TimescaleDB, ClickHouse, Redis, MinIO | **Isolated** subnets, no route to any gateway | `Z2` only | **Nothing** |
| **`Z4`** Data — Bangladesh resident | Resident PostgreSQL, separate key material | **A separate site** (`BD-R`), not a subnet | **`Z2` via `CD-233` only**, over the §8.2 private link | **Nothing** |
| **`Z5`** Management | CI/CD runners, bastion, Vault, observability | Restricted subnets, reachable only from named source ranges with MFA | Named ranges + MFA | `Z2`, `Z3` |
| **`Z6`** Egress | Outbound proxy to third-party APIs | An egress subnet with a NAT path and an **allow-list** | `Z2` | **Named allow-list only** |

### 4.2 The two rules that make the model worth its cost

`AR-001` §8.1 states them; this section makes them mechanisms.

| # | Rule | Mechanism |
|---|---|---|
| **NR-01** | **No application node reaches the internet except through `Z6`, to an allow-listed destination** | `Z2` subnets have **no default route to an internet gateway**. The only outbound path is the `Z6` proxy. An unlisted destination fails closed, and the failure is logged and alerted |
| **NR-02** | **`Z4` is reachable only through the residency service** | `Z4`'s network policy accepts connections from **`CD-233`'s service identity only**, not from the `Z2` CIDR. A compromised application node cannot reach `Z4` even from inside `Z2` |

> **`NR-01` is what converts `IP-10` — *"data leaving the Company is minimised and logged"* — from an
> aspiration into a mechanism**, and `NR-02` is what makes the residency rule auditable **in exactly
> one place**, which is what a regulator will ask for (`AR-001` §8.1).

### 4.3 Segmentation posture

| # | Rule |
|---|---|
| **SG-01** | **Default deny, both directions.** Every security group starts empty; every rule is added deliberately and carries a comment naming the flow it permits |
| **SG-02** | Rules reference **security groups or service identities, never CIDR ranges**, wherever the platform supports it. A CIDR rule survives a re-address; a group rule survives a re-IP |
| **SG-03** | **No `0.0.0.0/0` ingress rule exists anywhere except at `Z0`.** `FF-101` |
| **SG-04** | **No security group permits SSH from the internet.** Administrative access is `Z5` only, through the bastion, with MFA and session recording (`NFR-070`) |
| **SG-05** | Every rule is expressed in IaC (`PE-003`). **A rule added by hand is drift and is reverted** (`PE-003` §7) |
| **SG-06** | East-west traffic between `Z2` services uses **mTLS with service identity**, so a network-level compromise does not yield a service-level one |

### 4.4 What a compromised node can reach — stated, because that is the point

The zone model earns its operational cost only if this table is short. An attacker with code
execution on a `Z2` application node can reach:

| Target | Reachable? | Why |
|---|:--:|---|
| The internet, arbitrarily | **No** | `NR-01` — no gateway route; `Z6` allow-list |
| Another `Z2` service | Yes, **but must authenticate** | mTLS + service identity (`SG-06`); network position grants nothing (§4.6) |
| `Z3` PostgreSQL | Yes, **with credentials** | Credentials are Vault-issued, short-lived and per-service (`PE-009`) |
| **`Z4` resident store** | **No** | `NR-02` — `Z4` accepts `CD-233`'s identity only |
| `Z5` management, Vault, CI runners | **No** | `Z5` accepts named source ranges with MFA; `Z2` is not one |
| Backups in `BKP-3` | **No** | Separate account, separate credentials, **immutable** (§3.2) |

### 4.5 Where this design is weaker than it looks

Stated rather than discovered:

| # | Weakness | Compensating control |
|---|---|---|
| **W-01** | A compromise of **`CD-233` itself** reaches `Z4` by design | `CD-233` is the estate's highest-assurance component: minimal surface, per-read access logging (`AR-001` §8.1), and it is in `SC-002`'s threat model as a named asset |
| **W-02** | A compromise of **`Z5`** reaches everything, because `Z5` builds everything | No standing access (`AR-001` §8.1); MFA; privileged session recording (`NFR-070`); `PE-009` break-glass with an audit trail |
| **W-03** | The **`Z6` allow-list is only as good as its review** | `FF-104` checks the running allow-list against the `IN-001` §10.2 integration register; an entry with no integration row fails |
| **W-04** | **`BKP-3` immutability depends on the third party honouring it** | Retention lock verified quarterly by attempting a deletion that must fail (`PE-007` §6) |

### 4.6 Zero trust, adopted partially and deliberately

> **`PE-001-D-02`. Network position never grants access — but segmentation is retained.**

NIST SP 800-207 argues that network location should confer no trust. The estate **adopts that
principle for authorisation** — every call authenticates and authorises through M29 regardless of
zone (`AR-001` `LB-05`, `IN-001` `AA-01`) — and **retains segmentation as defence in depth** rather
than removing it.

**Why not go further.** A pure identity perimeter would put `Z3` and `Z4` on a routable network and
rely entirely on authorisation. For a store holding NID and biometric templates under a statute with
a notification obligation, **two independent controls that must both fail is worth the operational
cost of the second one.** `NR-02` is that second control.

---

## 5. Address Planning

### 5.1 Why this matters more than it appears

An address plan invented per environment produces overlapping ranges, and overlapping ranges make
**`dr` failover and `migration-staging` connectivity impossible to build later without renumbering
production**. The plan is therefore fixed before the first environment is created.

### 5.2 The allocation

A single RFC 1918 `/12` is reserved for the programme and subdivided so that **no two environments
and no two sites overlap**.

| Allocation | Range | Contents |
|---|---|---|
| Programme reservation | `10.64.0.0/12` | Everything below. Nothing outside it |
| **`RGN-P` production** | `10.64.0.0/16` | `Z1` public `/20` · `Z2` private `/18` · `Z3` isolated `/20` · `Z5` mgmt `/22` · `Z6` egress `/24` |
| **`RGN-S` standby** | `10.65.0.0/16` | Mirrors `RGN-P`'s internal structure, **different range** — so failover is a routing change, not a renumber |
| **`BD-R` resident** | `10.66.0.0/20` | `Z4` production `/24` · `Z4` standby `/24` · management `/26` |
| `staging` | `10.70.0.0/16` | |
| `uat` | `10.71.0.0/16` | |
| `sit` | `10.72.0.0/16` | |
| `perf` | `10.73.0.0/16` | **Production-shaped** — see `PE-002` |
| `training` | `10.74.0.0/16` | |
| `dev` / `ci` | `10.75.0.0/16` | Ephemeral CI namespaces carved from it |
| **`sandbox`** | `10.76.0.0/16` | **Externally reachable** — `IN-008` §6. Deliberately far from production in the plan as well as in policy |
| **`migration-staging`** | `10.77.0.0/16` | Production-class (`MG-005`), and therefore **not** adjacent to `staging` in the plan either |
| Reserved | `10.78.0.0/15` | Future environments, second regions, acquisitions |

| # | Rule |
|---|---|
| **AP-01** | **No environment overlaps another.** `FF-102` |
| **AP-02** | `local` (`BE-001`, Docker Compose) uses `172.20.0.0/16` — deliberately outside the programme reservation, so a developer's laptop can never route to a real environment |
| **AP-03** | Branch networks are **not** in this plan. Branches reach the system as internet clients (§8.1), not as extensions of the estate |
| **AP-04** | Every subnet is created by IaC with its CIDR **as an input variable, never a literal** (`PE-003`) |
| **AP-05** | IPv6 is **enabled at `Z0`/`Z1`** for client reachability and **not used internally** — dual-stack internal networking doubles the security-group surface for no requirement anyone has stated. Reviewed at the W5 gate |

---

## 6. Ingress and Egress

### 6.1 The ingress path

```
Internet
   │
   ▼  Z0 — provider edge: CDN · WAF (OWASP CRS) · DDoS · bot management (NFR-068)
   │        TLS 1.3 terminated here for cached/static; passed through for API
   ▼  Load balancer — one per AZ, health-checked
   ▼  Z1 — Kong 3.x + Nginx 1.27, HA pair
   │        OAuth introspection · per-consumer quota (IN-005 §9)
   │        correlation-id injection (API-09) · Idempotency-Key presence (API-07)
   │        payload ceiling
   ▼  Z2 — application
```

| # | Rule |
|---|---|
| **IN-01** | **`Z0` is the only zone with an internet-facing listener.** `FF-101` |
| **IN-02** | The WAF runs OWASP Core Rule Set in **blocking** mode in production, and in **detection** mode in `staging` for one wave before promotion, so a new rule set does not first block real traffic |
| **IN-03** | **Bot protection returns `403 auth.bot_blocked`, never `429`** — `AP-005` §4.10; the remedy is registration, not backoff |
| **IN-04** | `/hooks/v1/*` inbound webhooks (`IN-006`) traverse the same path and are **rate-limited per source**, because an inbound webhook flood is a denial-of-service vector that carries no bearer token to throttle on |
| **IN-05** | The **public tokenised tracking view** (`/api/v1/tracking/{token}`) is the only unauthenticated application route and is served through `Z0` caching with a short TTL |

### 6.2 Availability at the ingress tier

Technology Stack §21.3 states *"the components where a single node causes total outage are
PostgreSQL primary, Keycloak, Kong and Nginx — all four are HA from Wave 1."* This document makes
that a network fact:

| Component | Topology | Failure tolerated |
|---|---|---|
| Load balancer | Provider-managed, multi-AZ | AZ loss |
| Kong | **≥ 2 instances across ≥ 2 AZs** from W1 | Instance and AZ loss |
| Nginx | As above | As above |
| Keycloak (`Z2`, but a total-outage dependency) | **HA cluster from W1** — non-negotiable | Instance loss |

### 6.3 Egress — the `Z6` allow-list

**This is the mechanism `IN-001` `NR-01`, `IP-10` and `FF-44` all rest on.**

| # | Rule |
|---|---|
| **EG-01** | **All outbound traffic from `Z2` traverses the `Z6` proxy.** No node has a direct route out |
| **EG-02** | The proxy permits **named destinations only** — FQDN-based, not IP-based, because counterparty IPs change without notice |
| **EG-03** | Every allow-list entry names its **`INT-nnn` integration row** (`IN-001` §10.2). **An entry with no integration row fails `FF-104`** |
| **EG-04** | Every outbound call is logged with counterparty, endpoint, latency, outcome **and the field set sent** (`IN-001` `OB-02`, `AP-012` §4.8) |
| **EG-05** | Credentials are **injected at the proxy from Vault**, so an application node never holds a counterparty credential in memory longer than the call |
| **EG-06** | Adding an entry is a **recorded change** (`GV-003`), not a support action |
| **EG-07** | **`BD-R` egress is separately allow-listed and separately reviewed.** A destination reachable from `RGN-P` is not thereby reachable from `BD-R` |

> **`EG-07` exists because the residency rule is about where data *goes*, not only where it *rests*.**
> An unreviewed egress path from `BD-R` is a cross-border transfer channel that `SC-007`'s transfer
> gate never sees.

### 6.4 The forty-seven destinations

`IN-001` §10.3 counts **47 external integrations**, of which — **counted from `05-03` §2 at
2026-08-19 01:15 (+06), not taken from its summary** — **13 are P0**, 14 are P1, 12 are P2 and 8 are
P3.

> **`PE-001-F-02`. `05-03` §2's own priority summary states 12 / 17 / 12 / 6. Enumerating its rows
> returns 13 / 14 / 12 / 8.** `AUDIT-017` `OP-03` found this and it remains uncorrected in `05-03`.
> **`IN-001` §10.3 and `IN-004` §3 repeated the summary's "12 P0" rather than counting**, which is a
> defect in Category 04 that this document corrects — the same `PG-03` failure those documents
> themselves warn about. Corrected in Category 04 as part of this issue; recorded as `PE-A-01`.

---

## 7. DNS, Certificates and Time

### 7.1 DNS

| # | Rule |
|---|---|
| **DN-01** | **One authoritative zone per environment**, delegated: `prod.1000fix.example`, `staging.…`, `sandbox.…`. A record cannot be created in the wrong environment by typo |
| **DN-02** | **DNSSEC enabled** on every public zone |
| **DN-03** | **Split-horizon**: internal names resolve to private addresses and do not exist in the public zone at all |
| **DN-04** | `BD-R` has its **own zone**, and no public record resolves to any `Z4` address |
| **DN-05** | Records are created by IaC (`PE-003`). **A hand-created record is drift** |
| **DN-06** | **Registrar and DNS provider are covered by the break-glass procedure** (`PE-009`) — a locked-out registrar is a total outage with no technical remedy |

### 7.2 Certificates

| # | Rule |
|---|---|
| **CT-01** | **TLS 1.3** at every edge listener. TLS 1.2 only where a named counterparty cannot negotiate 1.3, recorded per counterparty in the `IN-004` ICD |
| **CT-02** | Public certificates are **automatically issued and renewed**; a manual renewal is a scheduled outage waiting for a holiday |
| **CT-03** | **Internal mTLS uses a private CA** with short-lived certificates (hours, not months), issued from Vault |
| **CT-04** | **Certificate expiry is alerted at 30 and 7 days** — the same cadence as credential expiry (`IN-001` `OB-06`) |
| **CT-05** | Certificate transparency logs are monitored for unexpected issuance against the estate's domains |

### 7.3 Time

| # | Rule |
|---|---|
| **TM-01** | Every host synchronises to a **redundant NTP source**, and clock drift beyond 500 ms alerts |
| **TM-02** | **All infrastructure runs UTC.** Bangladesh Standard Time (UTC+06) is a presentation concern (`IN-001` `AC-05`) |

> **`TM-01` is not housekeeping.** `IN-006` `SIG-05` rejects a webhook whose timestamp is more than
> **300 seconds** from the receiver's clock, and `AR-009`'s event ordering is by `occurred_at`. **A
> drifting clock silently rejects valid partner deliveries and reorders events**, and both failures
> present as something else entirely.

---

## 8. Private Connectivity

### 8.1 Branch and field connectivity

| Population | Connectivity | Design consequence |
|---|---|---|
| **51+ branches** | Commodity internet, variable quality | **Branches are internet clients, not network extensions** (`AP-03`). No site-to-site VPN, no branch subnet in the address plan |
| **200–400 field technicians** (P02) | Mobile data, frequently poor | The **24-hour offline guarantee** (`NFR-047`, `AR-010`) is the design response. Network design cannot fix Bangladeshi rural connectivity; the application absorbs it |
| Riders (P09), auditors (P11) | As above | As above |
| Contact centre (P10) | Branch or head-office internet | Telephony (`INT-015`) has its own path |

> **`PE-001-D-03`. No branch VPN.** Extending the estate's private network to 51 sites of variable
> physical security would put 51 uncontrolled ingress points inside the perimeter. **Branches
> authenticate like any other client**, which is also what `NIST SP 800-207` argues for and what
> `AR-001` `LB-05` already requires.

### 8.2 The `RGN-P` ↔ `BD-R` link

**The most consequential link in the estate**, because every `T5` read traverses it.

| Property | Position |
|---|---|
| Transport | **Private connectivity** — dedicated circuit or provider interconnect. **Not the public internet**, and not a site-to-site VPN over commodity broadband |
| Redundancy | **Two circuits, two carriers** where the facility's carrier neutrality permits (`SEL-02`) |
| Encryption | **Encrypted in transit regardless**, because a private circuit is not a trust boundary (`SC-006`) |
| Traffic | `CD-233` calls **only**. No replication, no backup traffic, no management traffic |
| Latency | Measured and alerted. **`CD-233` latency is on the critical path of every `T5` read**, so its budget is `PE-008`'s to publish |
| Failure | Link loss means `Z4` is **unreachable, not lost** — which is `SC-007` §9.2's route 1 degraded mode, and it must be exercised (`PE-007` §7) |

> **`PE-001-F-03`. `SC-007` §9.2 designs a degraded mode for an unreachable `Z4` and the estate has
> never tested the condition that triggers it.** `DG-1`…`DG-6` require that service orders,
> dispatch, invoicing, inventory and payroll calculation continue while NID verification, KYC,
> biometric attendance and `M06` case access fail **explicitly**. **A degraded mode nobody has
> induced is a degraded mode nobody knows works** — scheduled as a `PE-007` §7 drill.

### 8.3 Management access

| # | Rule |
|---|---|
| **MA-01** | **No standing administrative access** (`AR-001` §8.1). Access is requested, time-boxed and expires |
| **MA-02** | All administrative access traverses the **`Z5` bastion** with MFA |
| **MA-03** | **Privileged sessions are recorded** (`NFR-070`) |
| **MA-04** | `BD-R` administrative access is **separately granted** and separately logged. Holding `RGN-P` administrative access grants nothing in `BD-R` |
| **MA-05** | Break-glass is `PE-009`'s, and it is **the only path that bypasses `MA-01`** — with an audit trail and a mandatory post-hoc review |

---

## 9. High Availability

### 9.1 The four availability targets, and their scopes

The estate states four different availability numbers. They are **not in conflict — they have
different scopes** — but no document has previously said so, and an engineer reading `NFR-045`
without `NFR-006` will build to the wrong number.

| NFR | Target | Scope | Window |
|---|---|---|---|
| **`NFR-006`** | **≥ 99.9%** | System | **Bangladesh business hours, 09:00–22:00 BST** |
| **`NFR-045`** | **≥ 99.7%** | System | **24×7** — managed services requires it |
| **`NFR-046`** | **≥ 99.9%** | Customer portal | Presumed 24×7 |
| **`NFR-048`** | **≥ 99.95%** | Payment path | Presumed 24×7, **with multi-gateway failover** |

> **`PE-001-F-04`. `NFR-046` and `NFR-048` do not state their measurement window, and the difference
> between a 24×7 and a business-hours window is a factor of roughly 1.85 in permitted downtime.**
> `PE-008` §4 must fix the window per SLO or the numbers are not measurable. Referred to `RQ-006`.

**Infrastructure consequence:** the binding constraint is **`NFR-048`'s 99.95%** — about **22 minutes
per month** — and `IN-007` §9.3 records that for the **card** path it is unachievable at any
infrastructure quality, because `INT-003` is the only card acquirer. **Infrastructure can deliver
99.95% of the platform; it cannot deliver 99.95% of a single-supplier external dependency.**

### 9.2 HA by tier

Inherited from Technology Stack §21.3 and made a network design:

| Tier | Topology | Tolerates | From |
|---|---|---|:--:|
| `Z0` edge | Provider HA | Provider SLA | W1 |
| `Z1` ingress | Kong + Nginx, **≥ 2 AZs** | AZ loss | **W1** |
| **Identity** | **Keycloak HA cluster** | Node loss — *"non-negotiable, a total-outage dependency"* | **W1** |
| `Z2` application | **≥ 2 Odoo nodes**, rolling deploys | Node loss, zero-downtime deploy | **W1** |
| Portal | ≥ 2 Next.js instances | Node loss | W2 |
| **`Z3` primary data** | Streaming replication to a **hot standby** + 2 read replicas | **Automated failover, RPO ≤ 15 min** | W1 |
| **`Z4` resident** | **HA pair in Bangladesh**, encrypted replication | Node loss | **W1** |
| Time series | TimescaleDB replica | Node loss | W2 |
| Event bus | **3-node Redpanda** | Node loss, no message loss | W6 |
| Cache | Redis with persistence + replica | Node loss, session continuity | W1 |
| Object storage | Erasure coding across nodes | Multi-disk loss | W1 |
| **DR** | **Warm standby**, RPO ≤ 15 min, RTO ≤ 2 h, **drilled twice yearly** | Site loss | **W2** |

### 9.3 The rule

> **`HA-01`. No single-node critical component is acceptable in production.** The four that cause
> total outage — PostgreSQL primary, Keycloak, Kong, Nginx — are HA **from Wave 1**, before any
> feature depends on them. `FF-105`.

### 9.4 The maintenance window, reconciled

| Requirement | Statement |
|---|---|
| `NFR-008` | **Zero-downtime deployment** for planned changes |
| `NFR-049` | Planned maintenance **outside 08:00–23:00 BST**, ≤ 4 h/month, announced 72 h ahead |

**These coexist.** `NFR-008` is the standard for **releases**, achieved by rolling deploys and
forward-only migrations (`PE-004` §8). `NFR-049`'s window exists for changes that genuinely cannot be
zero-downtime — a major PostgreSQL version upgrade, a network re-address, a facility migration.

> **`MW-01`. Using the `NFR-049` window for an ordinary release is a defect, not a convenience.**
> The window is a scarce resource: **9 hours per night and 4 hours per month**, and it is the only
> capacity the estate has for changes that cannot be done live.

---

## 10. Environment Placement

`PE-002` owns the environment inventory. This document states **where each may sit**, because
placement is a network property.

| Environment | Site | Address block | Internet-reachable | Holds `Z4` data |
|---|---|---|:--:|:--:|
| `local` | Developer workstation | `172.20.0.0/16` | No | **Never** |
| `dev` / `ci` | `RGN-P`, isolated account | `10.75.0.0/16` | No | **Never** |
| `sit` | `RGN-P`, isolated account | `10.72.0.0/16` | No | **Never** |
| `uat` | `RGN-P`, isolated account | `10.71.0.0/16` | No | **Never** |
| `perf` | `RGN-P`, isolated account | `10.73.0.0/16` | No | **Never** |
| `training` | `RGN-P`, isolated account | `10.74.0.0/16` | No | **Never** |
| **`sandbox`** | `RGN-P`, **separate account** | `10.76.0.0/16` | **Yes — by design** | **Never.** Synthetic only (`IN-008` `SB-01`) |
| **`migration-staging`** | `RGN-P`, **production-class account** | `10.77.0.0/16` | No | **Masked in-job** (`NFR-086c`) |
| `staging` | `RGN-P`, production-class account | `10.70.0.0/16` | No | **Never — masked in-job** |
| **`prod`** | **`RGN-P` + `BD-R`** | `10.64.0.0/16` + `10.66.0.0/20` | Through `Z0` | **Yes, in `Z4` only** |
| **`dr`** | **`RGN-S` + `BD-R` standby** | `10.65.0.0/16` + `10.66.0.0/20` | On failover | **Yes, resident standby only** |

| # | Rule |
|---|---|
| **EP-01** | **Non-production environments live in separate cloud accounts or projects**, not merely separate subnets. An account boundary survives a misconfigured security group; a subnet boundary does not |
| **EP-02** | **`sandbox` is in its own account with no network path to any other environment.** It is externally reachable and externally credentialled, and it holds synthetic data only |
| **EP-03** | **No non-production environment has a route to `Z3` or `Z4` production.** `FF-103` |
| **EP-04** | **`NFR-086c` is absolute**: masking runs **inside** the clone job, so an unmasked clone cannot exist even briefly. This is a **network-enforced** property too — the clone job runs in `Z5` and writes only to the target environment's account |

---

## 11. Host and Platform Baseline

| # | Standard |
|---|---|
| **HB-01** | **CIS Benchmark** baseline for every host and container image, applied through `PE-003` modules — never by hand |
| **HB-02** | **Immutable infrastructure**: a host is replaced, never patched in place. A host that has been logged into for a change is rebuilt |
| **HB-03** | **No public IP on any `Z2`, `Z3` or `Z5` host.** `FF-101` |
| **HB-04** | Disk encryption at rest everywhere; **`Z4` with separate key material** (`NFR-061`, `SC-006`) |
| **HB-05** | Host-level intrusion detection (Wazuh, `INT-029`) from W5, and on `Z4` and `Z5` **from W1** |
| **HB-06** | **Malware scanning on every file upload before storage or serving** (`NFR-063`) — an infrastructure service, not a per-module concern |

---

## 12. Flow-Down Obligations from Regulated Counterparties

### 12.1 Why a non-regulated company is nonetheless bound

**1000FiX is not a bank, an NBFI, an MFSP, a PSP or a PSO**, and Bangladesh Bank's *Guideline on ICT
Security* v4.0 (April 2023) and *Guidelines on Cloud Computing* do not apply to it directly.

**They apply to its counterparties.** bKash is an MFSP; SSLCOMMERZ is a PSP/PSO; the BEFTN sponsoring
bank is a scheduled bank. Their obligations reach 1000FiX **through contract**, and the guidelines
are explicit about the mechanism: where a data centre is operated by an outsourced supplier, the
contract must require compliance with physical-security requirements, and **the bank — and Bangladesh
Bank — reserve the right to audit**.

> **`PE-001-F-05`. No document in the estate carries a right-to-audit or physical-security-review
> obligation, and three P0 integrations are with entities whose regulator asserts one.** `IN-004`
> §2.4 section 15 requires each ICD to state *their* change-control obligations to us; **none states
> our facility obligations to them.** This is a contract term (`CO-*`) with an infrastructure
> consequence, and it must be settled **before** the W3 payment integrations go live, not during a
> counterparty audit. Raised to Legal Counsel and the Commercial Director; `Q-04`.

### 12.2 What the estate must therefore be able to produce

| # | Obligation | Where it lands |
|---|---|---|
| **FD-01** | **Right of audit** for the counterparty and its regulator, over the facilities holding their data | `SEL-03`; every hosting contract |
| **FD-02** | **Physical-security review** of the facility on request | Facility certification (§3.5) plus a documented review path |
| **FD-03** | **Data classification before hosting**, and visibility and monitoring over the systems | `DA-005`, `SC-007`, `PE-008` |
| **FD-04** | **Sub-processor disclosure** — who else touches the data | `NFR-098`; `AP-012`'s processor inventory, **which does not exist** (`AP-08`) |
| **FD-05** | Incident notification to the counterparty within their window | `SV-*`, `SC-008` |

> **`FD-01` interacts with `SEL-04`.** A right-to-audit clause is straightforward to obtain from a
> commercial colocation provider and is a different conversation with a state-operated facility.
> **It belongs in the `BD-R` selection criteria, not discovered after signature.**

---

## 13. Fitness Functions

`AR-012` v1.1 registers `FF-01`…`FF-37`; Category 04 holds `FF-38`…`FF-100`. This document continues
the sequence. **Allocation was confirmed by enumerating every `FF-nn` definition across all authored
categories at 2026-08-19 01:15 (+06)**, per `PGD-AUDIT-007` `PGD-A7-01`'s interim rule.

| # | Check | Scope | Timing | Enforcement |
|---|---|---|---|---|
| **FF-101** | No security group permits `0.0.0.0/0` ingress outside `Z0`; no `Z2`/`Z3`/`Z5` host has a public IP | All | CI on IaC plan + runtime scan | **Fail** |
| **FF-102** | No two environments' CIDR allocations overlap | All | CI | **Fail** |
| **FF-103** | No non-production environment has a network route to `Z3` or `Z4` production | All | CI + runtime | **Fail** |
| **FF-104** | Every `Z6` egress allow-list entry names an `INT-nnn` row in the `IN-001` §10.2 register | All entries | CI + weekly | **Fail** |
| **FF-105** | Every component in the `HA-01` list runs ≥ 2 instances across ≥ 2 failure domains | 4 components | Runtime | **Fail** |
| **FF-106** | `Z4` network policy accepts `CD-233`'s service identity only — **not** the `Z2` CIDR | `Z4` | CI + runtime | **Fail** |
| **FF-107** | No host permits SSH from any source outside the `Z5` bastion range | All | CI + runtime | **Fail** |
| **FF-108** | Every public zone has DNSSEC enabled and no public record resolves to a `Z4` address | All zones | Weekly | **Fail** |
| **FF-109** | Every TLS listener negotiates 1.3; a 1.2 listener has a named counterparty exception in an `IN-004` ICD | All listeners | Weekly scan | **Fail** |
| **FF-110** | Clock drift on every host is under 500 ms | All hosts | Runtime | **Alert** |

---

## 14. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `PE-001-D-01` | Site topology | Single site · **two sites + resident site + backup custody** · active-active multi-region | **Two + `BD-R` + `BKP-3`** | Single site fails `NFR-007` by orders of magnitude; active-active needs multi-master resolution the domain model does not support | `RGN-S` and `BKP-3` are new budget lines; `OP-02` closes with `PE-002` and `PE-007` |
| `PE-001-D-02` | Zero trust | Full identity perimeter · **identity for authorisation + retained segmentation** · network trust | **Both** | Two independent controls that must both fail is worth the cost for a store holding NID and biometric templates | `NR-02`; `FF-106` |
| `PE-001-D-03` | Branch connectivity | Site-to-site VPN per branch · **internet clients** | **Internet clients** | 51 sites of variable physical security would be 51 uncontrolled ingress points | No branch subnets; `AP-03` |
| `PE-001-D-04` | Address planning | Per-environment, as created · **one `/12` planned up front** | **Planned up front** | Overlapping ranges make `dr` failover and `migration-staging` connectivity impossible without renumbering production | §5.2; `FF-102` |
| `PE-001-D-05` | Egress | Per-node internet access · **`Z6` proxy with an FQDN allow-list** | **`Z6` proxy** | Converts `IP-10` from an aspiration into a mechanism, and makes the egress log the record of what actually left | `EG-01`…`EG-07`; `FF-104` |
| `PE-001-D-06` | `Z4` reachability | `Z2` CIDR permitted · **`CD-233` service identity only** | **Service identity** | A compromised `Z2` node must not reach `Z4` from inside the network | `NR-02`; `FF-106` |
| `PE-001-D-07` | IPv6 | Dual-stack throughout · **`Z0`/`Z1` only** | **Edge only** | Dual-stack internal networking doubles the security-group surface for no stated requirement | `AP-05`; reviewed at W5 |
| `PE-001-D-08` | Host lifecycle | Patch in place · **immutable, rebuild** | **Immutable** | A host that has drifted cannot be reasoned about, and drift is what `PE-003` §7 exists to prevent | `HB-02` |

---

## 15. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **Which regional provider and region for `RGN-P`?** Everything in §5 and §10 is provider-agnostic by design, but `PE-003`'s modules and `PE-006`'s costs are not | CTO | **W0 — blocking** | `PE-003`, `PE-006`, `GV-008` |
| **Q-02** | **Is `BD-R` procured?** Three certified in-country facilities exist (§3.3). `SC-007` §9.4 option A is available and unchosen — and option C is the current position **by default, not by decision** | **CTO + CFO with Legal Counsel** | **W1** | `OP-01`, `OP-02`, `NFR-007` for `Z4`, `PE-007` |
| **Q-03** | **Does a state-operated facility change the `NFR-086b` position, in either direction?** (`SEL-04`) | Legal Counsel + DPO | **W1** | `BD-R` selection |
| **Q-04** | **Do the payment counterparties assert a right of audit over our facilities?** (`PE-001-F-05`) | Legal Counsel + Commercial Director | **W3 − 3 months** | `INT-001`…`003` go-live |
| Q-05 | Which environments genuinely need a **separate cloud account**, and what does the account structure cost to operate? | Platform Engineering Lead | W1 | `EP-01`, `PE-002` |
| Q-06 | Is the `RGN-P` ↔ `BD-R` link **dual-carrier**, or does the chosen facility's neutrality prevent it? (`SEL-02`) | Platform Engineering Lead | W1 | §8.2 |
| Q-07 | What is the **`CD-233` latency budget**, and does the private link meet it? Every `T5` read traverses it | Chief Architect + `PE-008` | W1 | §8.2, `PE-008` |

---

## 16. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The state of infrastructure design before this document is **measured**, not asserted | Opening table — 0 network artefacts in 621 files |
| AC-02 | `AR-001`'s six trust zones are realised as a network, with ingress and egress stated per zone | §4.1 |
| AC-03 | The two rules that justify the zone model are **mechanisms**, not statements | §4.2 `NR-01`, `NR-02`; `FF-104`, `FF-106` |
| AC-04 | **What a compromised node can reach is stated**, and so is where the design is weak | §4.4, §4.5 |
| AC-05 | A non-overlapping address plan exists **before** the first environment is built | §5.2; `FF-102` |
| AC-06 | The `BD-R` site is made **concrete** — named candidates, selection criteria, cost shape | §3.3, §3.4, §3.5 |
| AC-07 | The four availability targets are reconciled by **scope**, and the unmeasurable ones are flagged | §9.1; `PE-001-F-04` |
| AC-08 | `NFR-008` and `NFR-049` are reconciled | §9.4 |
| AC-09 | Environment placement is specified for every environment `PE-002` will inventory | §10 |
| AC-10 | **Flow-down obligations from regulated counterparties are identified** | §12; `PE-001-F-05` |
| AC-11 | Every standard, statute and vendor claim carries a verification date | §2.1, §17 — all 2026-08-19 |
| AC-12 | Fitness-function allocation was **enumerated before allocation**, per `PGD-A7-01` | §13 |

**Definition of done.** Complete when every criterion is met, **Q-01 and Q-02 are decided**,
`FF-101`…`FF-110` are enabled, and `PGD-000`'s `PE-001` row carries a fresh enumeration timestamp.
**`OP-01` and `OP-02` do not close on issue of this document** — they close when `BD-R` and `RGN-S`
are provisioned and `PE-007`'s first drill has run.

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | **`AR-001`** §8.1–§8.6 | Trust zones, isolation tiers, split residency, DR constraints, environment ladder, sizing basis |
| Upstream | **`SC-001`** §5.2 | The security control set this topology carries |
| Upstream | **`SC-007`** §5, §9 | The split-record design; **§9.4 option A, made concrete here** |
| Upstream | `IN-001` §3.2, §8 | Component allocation; the `Z6` egress requirement |
| Downstream | **`PE-002`** | §10 placement; the sites an environment may occupy |
| Downstream | **`PE-003`** | Every resource in §4–§11 is an IaC module |
| Downstream | **`PE-005`** | The network a cluster sits in |
| Downstream | **`PE-006`** | §3.4's cost shape; `Q-01`'s provider decision |
| Downstream | **`PE-007`** | `RGN-S`, `BD-R` standby and `BKP-3` are its failover targets |
| Downstream | **`PE-008`** | §8.2's link latency and §9.1's SLO scopes |
| Downstream | **`PE-009`** | `MA-05` break-glass; `EG-05` credential injection |
| Downstream | `SC-002` | The attack surface, now drawn |
| Downstream | `SV-*`, `RL-*` | Operations and release run on this topology |
| Lateral | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` §8 | Compute sizing — **a shopping list this document gives a shape to** |
| Lateral | `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §21.3 | HA per tier, realised in §9.2 |

---

## 18. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`./PE-002_Environment_Strategy_and_Specification.md`](./PE-002_Environment_Strategy_and_Specification.md) ·
[`./PE-003_Infrastructure_as_Code_Standard.md`](./PE-003_Infrastructure_as_Code_Standard.md) ·
[`./PE-005_Containerisation_and_Orchestration_Design.md`](./PE-005_Containerisation_and_Orchestration_Design.md) ·
[`./PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md`](./PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md) ·
[`./PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md`](./PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md) ·
[`./PE-008_Observability_and_Monitoring_Design.md`](./PE-008_Observability_and_Monitoring_Design.md) ·
[`./PE-009_Configuration_and_Secrets_Management_Standard.md`](./PE-009_Configuration_and_Secrets_Management_Standard.md) ·
[`../02_Architecture_and_Design/AR-001_Software_Architecture_Document.md`](../02_Architecture_and_Design/AR-001_Software_Architecture_Document.md) ·
[`../05_Security_Privacy_and_Compliance/SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md`](../05_Security_Privacy_and_Compliance/SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md) ·
[`../04_Integration_and_API_Engineering/IN-001_Integration_Architecture_Specification.md`](../04_Integration_and_API_Engineering/IN-001_Integration_Architecture_Specification.md)

**Workspace**
`../../1000fix_ERP_Module/02_Architecture/02-05_*.md` §8, §9 ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_*.md` ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §17.1, §21 ·
`../../project_content/_AUDIT/AUDIT-017_*.md` `OP-01`, `OP-02`, `OP-03` ·
`../../project_content/17_Operations_Support_and_Runbooks/OP-012_*.md`

**External sources**

| Source | What it establishes | Verified |
|---|---|---|
| NIST SP 800-207 *Zero Trust Architecture* | No implicit trust from network location | 2026-08-19 |
| RFC 8446 (TLS 1.3), RFC 4033 (DNSSEC), RFC 1918 / RFC 6890 | Transport, DNS integrity, private addressing | 2026-08-19 |
| CIS Benchmarks | Host and container hardening baselines | 2026-08-19 |
| **Bangladesh Bank, *Guideline on ICT Security* v4.0 (April 2023)** | Applies to banks, NBFIs, **MFSPs, PSPs, PSOs**; data-centre outsourcing requires contractual physical-security compliance and **a reserved right of audit for the institution and Bangladesh Bank** | 2026-08-19 |
| **Bangladesh Bank, *Guidelines on Cloud Computing*** | Data classification before hosting; complete visibility and monitoring; right to audit by internal, external and Bangladesh Bank auditors | 2026-08-19 |
| **BDCCL National Data Center**, Kaliakoir Hi-Tech Park | **Tier IV**, Uptime Institute *Tier Certification of Operational Sustainability*; colocation, cloud and storage services | 2026-08-19 |
| **BDCOLO** | Carrier-neutral **Tier III**, 2N redundancy | 2026-08-19 |
| **Felicity IDC** | **Tier III, PCI-DSS certified**; private cloud for BFSI data-residency needs | 2026-08-19 |
| Uptime Institute Tier Standard | Facility topology tiers I–IV | 2026-08-19 |

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Platform Engineering | Initial issue. Realises `AR-001`'s six trust zones as a network — the first network design in the estate, against **0 network artefacts in 621 files**. Fixes a non-overlapping address plan across twelve environments and three sites **before** the first is built. **Makes `SC-007` §9.4 option A concrete by naming three certified in-country facilities** and the selection criteria, converting `OP-01` from an unavailable capability into an untaken procurement decision (`PE-001-F-01`). Reconciles the four availability targets by scope and flags two as unmeasurable (`PE-001-F-04`). Identifies the **Bangladesh Bank right-to-audit flow-down** that no estate document carries (`PE-001-F-05`), and corrects the P0 integration count from 12 to **13** (`PE-A-01`) | *Pending — CTO; Design Authority not constituted (`PGD-A1-09`)* |

---

*`PE-001` · Category 10 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
