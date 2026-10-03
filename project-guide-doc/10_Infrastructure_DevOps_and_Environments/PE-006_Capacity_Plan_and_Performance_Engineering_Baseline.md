---
id: PE-006
title: Capacity Plan & Performance Engineering Baseline
category: 10 — Infrastructure, DevOps & Environments
code: PE
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering Lead
approver: CTO with CFO and Design Authority (constituted under GV-002)
standards_basis: >
  ISO/IEC 25010 performance efficiency · ISO/IEC 25023 measurement ·
  Universal Scalability Law (Gunther) · Little's Law · USE method (Gregg) ·
  Google SRE capacity planning
traces_to: >
  PGD-000 PE-006 · AR-001 §8.6 sizing basis · 02-05 §8.1, §8.2 · Technology Stack §21 ·
  PE-001 §3.4 · PE-002 §9 · PE-005 §7 · GV-008 §4.3 line 3, Q-03 · audit M-09, OP-02 ·
  NFR-001…NFR-005, NFR-039, NFR-053…NFR-060
depends_on: PE-001 · PE-002 · PE-005 · AR-001 · DA-001
verified_on: 2026-08-19
priority: P1
needed_by: W2
enumeration_timestamp: 2026-08-19 01:15 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# PE-006 — Capacity Plan & Performance Engineering Baseline

### Category 10 · Code `PE` · ISO/IEC 25010 · Universal Scalability Law · Little's Law

---

> **`PGD-000`'s `PE-006` row: *"`02-05` §8.1 gives a Wave 8 steady state with no derivation from
> volumetrics. Audit `M-09`: wave capacity was never validated against effort."***
>
> **Confirmed at 2026-08-19 01:15 (+06).** `02-05` §8.1 and Technology Stack §21.1 give thirteen
> component sizes. `AR-001` §8.6 supplies the **sizing driver per component** — which requirement
> makes it big — and states *"sizing is `PE-006`'s deliverable."* **Nowhere does a number get
> derived from a volume.**
>
> **The three arithmetic results that change how the estate should be sized**, derived in §4:
>
> | Finding | Result |
> |---|---:|
> | `NFR-055` telemetry generates **63× the annual data points of `NFR-056` GPS** — and it is `P2` while GPS is `P1` | **26.3 bn vs 420 m points/year** |
> | The Wave 8 sizing target is a **year-5** volume in a **3-year** programme | `NFR-053` says *"by year 5"* |
> | Peak order-creation write rate at year-5 volume | **~1.1 orders/second** — the *order* rate is not the constraint; its **fan-out** is |

---

## 1. Purpose

A sizing table is an answer without a question. This document supplies the questions: the volumetric
model the estate's numbers must satisfy, the derivation from business volume to resource, the growth
projection across nine waves, the scaling trigger per tier, the headroom policy, the cost model with
the three lines `GV-008` excludes, and the performance-testing baseline that turns `DoD-14`'s *"1.5×
expected peak"* into a measurable target.

It does **not** replace `02-05` §8.1's numbers with different numbers invented differently. It
derives them, reports where derivation and assertion disagree, and states what must be **measured**
rather than calculated.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **The volumetric model** — every stated business volume, in one place, with its source |
| 2 | **Derivation** from volume to load: transactions, events, storage, connections |
| 3 | Where the estate's published sizing **agrees and disagrees** with derivation |
| 4 | Growth projection across the nine waves |
| 5 | **Scaling triggers** — the signal, the threshold and the action, per tier |
| 6 | **Headroom policy**, including the `N−1` rule |
| 7 | The three cost lines `GV-008` excludes, quantified in shape |
| 8 | **Cost per transaction** and its uses |
| 9 | The **performance-engineering baseline**: what is tested, at what load, against what |
| 10 | What must be **measured, not calculated**, and when |
| 11 | Fitness functions `FF-147`…`FF-154` |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Network topology and sites | **`PE-001`** | Consumed |
| Which environments exist | **`PE-002`** | This document sizes them |
| Container resource model | **`PE-005`** §7 | This document produces the values it consumes |
| Database schema, indexes, partitioning | `DA-001` | **§4.5 states what partitioning must achieve; `DA-001` designs it** |
| Test tooling and execution | `QA-005`, `PE-004` §4 | `gate` profile runs §9's tests |
| Programme budget and financial governance | `GV-008`, `CO-005` | §8 feeds them |
| Third-party API costs | `02-05` §8.3, `CO-*` | Referenced, not re-derived |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| Platform engineers | §4–§7 |
| **`PE-005`** | §5's per-component values are its requests and limits |
| **CFO and `GV-008`** | §8 answers `GV-008` `Q-03` in shape and names three excluded lines |
| QA Lead | §9 is the performance-test charter |
| Chief Architect | §4.6's fan-out finding and §10's measurement plan |
| Wave-gate assessors | §7's triggers are gate evidence |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Concept | Conformance | Departure and rationale |
|---|---|---|---|
| **ISO/IEC 25010** | Performance efficiency — time behaviour, resource utilisation, capacity | §4, §9 | None |
| **ISO/IEC 25023** | Measurement of quality characteristics | §9's metrics are measures, not adjectives | None |
| **Little's Law** | `L = λW` — concurrency = arrival rate × residence time | §4.3's connection and worker derivation | None |
| **Universal Scalability Law** | Throughput degrades with contention and coherency | §7.4's warning against linear scaling assumptions | **Applied qualitatively.** Fitting USL coefficients requires load-test data the estate does not yet have — §10 |
| **USE method** (Gregg) | Utilisation, saturation, errors per resource | §7.2's trigger design | None |
| Google SRE capacity planning | Headroom, `N−1`, organic vs inorganic growth | §6 | None |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `05-06` | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_*.md` | `NFR-001`…`NFR-005`, `NFR-039`, **`NFR-053`…`NFR-060`** — the volumetric requirements |
| **`AR-001` §8.6** | `../02_Architecture_and_Design/AR-001_*.md` | **The sizing driver per component** — and *"sizing is `PE-006`'s deliverable"* |
| Technology Stack §21.1, §21.2, §21.3 | `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` | Steady-state sizing with the resident store; **capacity progression by wave**; HA per tier |
| `02-05` §8.1, §8.2, §8.3 | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` | Production sizing; cost progression; third-party API costs |
| `GV-008` §4.3, `Q-03`, `GV-008-D-03` | `../00_Programme_Governance_and_Control/GV-008_*.md` | **$52K–$96K infrastructure, excluding the resident store**; the deferral to `PE-001`–`PE-006` |
| BRD / charter | `../../primary-doc/…BRD.md`, `../../1000fix_ERP_Module/00_Governance_and_Charter/00-02_*.md` | 250,000+ customers/month; 51+ branches; 200–400 technicians; 500–2,000 sellers |
| `AR-009` §10.1 | `../02_Architecture_and_Design/AR-009_*.md` | **988 declared events** — the fan-out multiplier in §4.6 |
| `PE-001`, `PE-002`, `PE-005` | `./` | Sites; twelve environments; the resource model |

### 2.3 Audit findings this document closes or contributes to

| Finding | Source | Disposition |
|---|---|---|
| `PGD-000` `PE-006` — *"a Wave 8 steady state with no derivation from volumetrics"* | `PGD-000` | **Closed.** §4 derives; §5 reconciles derivation against the published table |
| **`M-09`** — wave capacity never validated against effort | `00-06` | **Contributes.** §6's wave progression is derived from volume; effort validation remains `GV-004`'s |
| **`GV-008` `Q-03`** — *"What does a Bangladesh-resident data store cost?"* | `GV-008` | **§8.2 answers in shape and structure.** The figure needs `PE-001` `Q-01`'s provider decision |
| `GV-008-D-03` — re-deriving infrastructure requires `PE-001`–`PE-006` | `GV-008` | §8 supplies the derivation; **`CO-005` must publish the money** |
| **`PGD-A3-05`** — `02-05` §8.1 carries no line for the Bangladesh-resident store | `PGD-AUDIT-003` | **Confirmed and quantified in shape** — §5.3, §8.2 |
| `OP-02` — `dr` in no sizing table or cost progression | `AUDIT-017` | §5.4, §8.2 line 2 |
| `PE-005-F-02` — no connection pooler in any sizing table | `PE-005` | **Confirmed and sized** — §4.3, §5.5 |

---

## 3. Method

### 3.1 Three kinds of number

| Kind | Meaning | Treatment |
|---|---|---|
| **Stated** | A requirement or business figure from a source document | Cited, never adjusted |
| **Derived** | Arithmetic from stated numbers, with the arithmetic shown | Reproducible; recomputed when an input changes |
| **Assumed** | A value with no source, needed to complete a derivation | **Labelled, with its sensitivity stated** |

> **`PE-006-D-01`. Every number in this document carries its kind.** `GV-008-D-03` declined to
> re-derive infrastructure because *"inventing a figure would be worse"* than carrying one with
> caveats. **The answer to that is not to invent, but to label** — a derived number with a shown
> derivation and a flagged assumption is auditable in a way an asserted number is not.

### 3.2 What cannot be calculated

| Quantity | Why it must be measured |
|---|---|
| Odoo request cost in CPU-seconds | Depends on module composition, ORM behaviour and data shape |
| Rows written per service order | Depends on `DA-001`'s schema, which does not exist |
| Query cost at 5 M rows | Depends on indexes and partitioning (`DA-001`) |
| Actual event fan-out per transaction | `AR-009` counts 988 **declared**; how many fire per order is a runtime property |
| Cache hit ratio | Workload-dependent |

**These are §10's measurement plan.** A capacity plan that calculates them is a capacity plan that
will be wrong in a specific and confident way.

---

## 4. The Volumetric Model

### 4.1 Stated volumes

| # | Volume | Value | Source | Kind |
|---|---|---|---|---|
| V-01 | Service orders | **5 million per year by year 5** | `NFR-053` | Stated |
| V-02 | Device registry | **5 million assets** | `NFR-054` | Stated |
| V-03 | Telemetry ingestion | **50,000 points per minute** | `NFR-055` (`P2`) | Stated |
| V-04 | GPS ingestion | **400 technicians at 30-second intervals** | `NFR-056` (`P1`) | Stated |
| V-05 | Concurrent internal users | **800+** | `NFR-003` | Stated |
| V-06 | Concurrent portal users | **75,000+** | `NFR-004` | Stated |
| V-07 | Marketplace | **5,000 sellers, 50,000 listings** | `NFR-057` | Stated |
| V-08 | Branches | **200** without configuration redesign | `NFR-058` | Stated |
| V-09 | Legal entities | 10, across 5 countries | `NFR-059` | Stated |
| V-10 | Document store | **50 TB**, sub-10-second retrieval | `NFR-060` | Stated |
| V-11 | Customers | **250,000+ per month** | BRD, charter | Stated |
| V-12 | Branches today | **51+** | BRD, charter | Stated |
| V-13 | Field technicians | **200–400** | BRD, charter | Stated |

### 4.2 The horizon problem

> **`PE-006-F-01`. `NFR-053` targets 5 million service orders per year *by year 5*. The programme is
> 36 months — three years. The Wave 8 steady-state sizing in `02-05` §8.1 and Technology Stack §21.1
> is therefore sized against a volume the estate reaches roughly two years after the programme ends.**

| Reading | Consequence |
|---|---|
| The sizing is a **year-5 target** | The estate is **over-provisioned at go-live** by whatever the year-3-to-year-5 growth is, and the cost progression in §8 over-states early-wave spend |
| The sizing is a **year-3 target** and `NFR-053` is the horizon | Then Wave 8's numbers are **not** derived from `NFR-053`, and their basis is unstated |

**Neither reading is documented.** This document adopts the first — the numbers are a **year-5
capacity target**, reached progressively — and §6 therefore derives a wave progression that arrives
at the published Wave 8 figures rather than starting from them. **`Q-01` asks the programme to
confirm.**

### 4.3 Derivation — transactional tier

**Order arrival rate**, from V-01:

```
5,000,000 orders/year
  ÷ 300 operating days/year        [ASSUMED: six-day week, minus holidays]
  = 16,667 orders/day
  ÷ 11 operating hours/day         [ASSUMED: 09:00–20:00, NFR-006's window]
  = 1,515 orders/hour  average
  × 2.7 peak factor                [ASSUMED: intra-day peak, retail-service shape]
  = 4,091 orders/hour  peak
  ÷ 3,600
  ≈ 1.14 orders/second at peak     [DERIVED]
```

| Sensitivity | Effect |
|---|---|
| Operating days 250 vs 300 | ±20% on the daily figure |
| Peak factor 2.0 vs 4.0 | ±48% on the peak figure |
| **Both at the pessimistic end** | ≈ **2.0 orders/second** — still not the constraint |

> **The order rate is not the problem, and that is the useful result.** At ~1–2 writes per second,
> the primary database is not stressed by *order creation*. **What stresses it is the fan-out** —
> §4.6.

**Concurrency, by Little's Law** (`L = λW`), for internal users:

```
V-05: 800 concurrent internal users
  × 1 request per user per 20 s    [ASSUMED: interactive ERP usage]
  = 40 requests/second
  × 0.4 s mean residence           [NFR-002: ≤ 400 ms p95 → mean ≈ 0.15–0.4 s]
  ≈ 16 requests in flight          [DERIVED]
```

**Odoo workers:** Technology Stack §21.1 gives 4 nodes × 12 workers = **48 workers**. Against ~16
in-flight requests at the stated concurrency, that is **3× headroom** — appropriate, because a
worker is occupied for the whole request including database wait.

**Database connections** — the derivation `PE-005-F-02` requires:

```
48 Odoo workers                    (4 nodes × 12)
+ 2 cron nodes  × 4 workers  =  8
+ 2 long-polling × 4         =  8
+ 16 domain services × 10 pool = 160   [ASSUMED: 10 per service]
+ portals, jobs, tooling      ≈  40   [ASSUMED]
────────────────────────────────────
≈ 264 concurrent connections to the PostgreSQL primary   [DERIVED]
```

> **`PE-006-F-02`. ~264 direct connections against a 16 vCPU primary is beyond the point where
> PostgreSQL's per-connection overhead degrades throughput**, and it is why `PE-005-F-02` flagged
> the absence of a connection pooler. **A pooler is required, it is in no sizing table, and its
> absence is not a tuning detail** — with portal autoscaling (`PE-005` §7.2) the connection count is
> *unbounded*. Sized in §5.5; `Q-02`.

### 4.4 Derivation — time-series tier, and the finding

**GPS**, from V-04:

```
400 technicians ÷ 30 s = 13.3 points/second
  = 800 points/minute       [DERIVED — matches Technology Stack §21.1's "800 GPS/min"]
  = 1,152,000 points/day
  ≈ 420 million points/year [DERIVED]
```

**Telemetry**, from V-03:

```
50,000 points/minute
  = 72,000,000 points/day
  ≈ 26,280,000,000 points/year   [DERIVED — 26.3 billion]
```

> **`PE-006-F-03`. Telemetry generates 62.6× the annual data points of GPS — and `NFR-055` is `P2`
> while `NFR-056` is `P1`.**
>
> | | GPS (`NFR-056`, **P1**) | Telemetry (`NFR-055`, **P2**) |
> |---|---:|---:|
> | Points/minute | 800 | **50,000** |
> | Points/year | 420 m | **26.3 bn** |
> | Share of the time-series tier | **1.6%** | **98.4%** |
>
> **The `P2` requirement sizes the tier; the `P1` requirement is a rounding error in it.** Two
> consequences follow. First, **deferring or reducing `NFR-055` is the single largest capacity lever
> in the estate** — and as a `P2` it is legitimately deferrable. Second, **if `NFR-055` proceeds,
> compression and retention are not tuning, they are the design**: at ~100 bytes/point raw, 26.3 bn
> points is ≈ **2.6 TB/year uncompressed**, against a TimescaleDB allocation of **4 TB** (Technology
> Stack §21.1). Without aggressive compression and a stated retention policy, **the tier is full
> inside two years.**

**Storage, time-series** — derived at Timescale's typical 10–20× columnar compression:

| Scenario | Raw/year | Compressed/year | 4 TB lasts |
|---|---:|---:|---:|
| Telemetry at 10× | 2.6 TB | ~260 GB | ~15 years |
| Telemetry at 10×, **no retention policy**, plus indexes and WAL | 2.6 TB | ~400 GB | ~10 years |
| **Telemetry uncompressed** | 2.6 TB | 2.6 TB | **< 2 years** |

> **The allocation is adequate *if and only if* compression is enabled and a retention policy
> exists.** Neither is stated anywhere. **`Q-03`; referred to `DA-001` and `DA-006`.**

### 4.5 Derivation — storage

| Store | Driver | Derivation | Published |
|---|---|---|---|
| **PostgreSQL primary** | V-01, V-02 | 5 m orders/year × ~15 related rows [ASSUMED] ≈ 75 m rows/year, plus 5 m assets and their history | **2 TB** (Tech Stack §21.1) — plausible **with partitioning**; §4.5.1 |
| **Object storage** | V-10 | Evidence photographs dominate: 16,667 orders/day × ~4 photographs × ~500 KB [ASSUMED] ≈ **33 GB/day ≈ 12 TB/year** | **20 TB growing to 50 TB** — consistent with ~3–4 years of retention |
| **Resident store `Z4`** | Regulatory, not volume | 5 m parties × a few classified fields ≈ **a few hundred GB** | `AR-001` §8.6: *"regulatory, not volume"* ✓ |
| ClickHouse | `NFR-039` | Analytical copies of the above | 4 TB |

#### 4.5.1 The partitioning dependency

`02-05` §8 asserts PostgreSQL 16 partitioning; **`DA-001` is the design and `PGD-000` records that
`02-05` names no partition key.** At 5 m orders/year, an unpartitioned order table reaches 25 m rows
by year 5.

> **`PE-006-F-04`. The 2 TB primary allocation is only defensible with partitioning, and the
> partition key is unspecified.** Sizing cannot compensate for a missing schema decision — **an
> unpartitioned 25 m-row table with the estate's reporting patterns will not meet `NFR-005`'s 20-second
> report target regardless of hardware.** Referred to `DA-001`; `Q-04`.

### 4.6 Derivation — the event fan-out, which is the real load

`AR-009` §10.1 counts **988 declared events**. A single service order traverses M01's sixteen
`service_order.*` events, each with declared consumers.

```
1.14 orders/second at peak
  × ~16 lifecycle events per order         [STATED — M01 §12.3]
  ≈ 18 events/second from M01 alone        [DERIVED]
  × ~4 consumers per event (mean)          [ASSUMED — §12.3 tables]
  ≈ 73 consumer invocations/second         [DERIVED]
  + outbox writes, one per event, in the SAME transaction as the state change
```

> **`PE-006-F-05`. The transactional tier's write load is dominated by the outbox, not by orders.**
> Every state change writes a business row **and** an outbox row in one transaction (`AR-009` §5.2),
> and the relay then reads, publishes and marks each. **At ~18 events/second the outbox table is the
> hottest table in the estate**, and neither `02-05` §8.1 nor Technology Stack §21.1 mentions it.
>
> Its requirements — a `(published, occurred_at)` index, aggressive pruning of published rows at 7
> days (`AR-009` §5.3), and partitioning — are `DA-001`'s, and they are **capacity-critical rather
> than merely tidy.** Referred to `DA-001`; `Q-04`.

### 4.7 Derivation — portal tier

```
V-06: 75,000 concurrent portal users
  × 1 request per user per 60 s     [ASSUMED: browsing, not transacting]
  = 1,250 requests/second           [DERIVED]
```

Against **3 Next.js nodes** (Tech Stack §21.1) that is ~417 requests/second per node — **achievable
for cached and static-rendered content, and not achievable for uncached authenticated reads.**

| # | Consequence |
|---|---|
| The portal tier's sizing **depends entirely on cache hit ratio**, which is `PE-006`'s largest unmeasurable (§3.2) |
| `PE-005` §7.2 autoscales portals for exactly this reason |
| **Every autoscaled portal instance adds database connections** — which returns to `PE-006-F-02`'s pooler |

---

## 5. Reconciliation with the Published Sizing

### 5.1 Where derivation agrees

| Component | Published | Derived | Verdict |
|---|---|---|---|
| GPS ingestion | 800/min | **800/min** | ✅ Exact |
| Odoo workers vs concurrency | 48 workers | ~16 in flight | ✅ ~3× headroom, appropriate |
| Object storage | 20 TB → 50 TB | ~12 TB/year | ✅ Consistent with 3–4 years' retention |
| Resident store | Small, HA | *"Regulatory, not volume"* | ✅ |

### 5.2 Where derivation disagrees or extends

| # | Item | Published | This document |
|---|---|---|---|
| 1 | **Connection pooler** | **Absent** | **Required** — ~264 direct connections (§4.3); §5.5 |
| 2 | **Outbox as a sizing item** | **Absent** | **The hottest table in the estate** (§4.6) |
| 3 | **Time-series compression and retention** | **Absent** | **Determines whether 4 TB lasts 2 years or 15** (§4.4) |
| 4 | **Partition key** | **Absent** | The 2 TB primary is undefensible without it (§4.5.1) |
| 5 | Sizing horizon | Wave 8 steady state | **A year-5 target in a 3-year programme** (§4.2) |

### 5.3 The resident store line — `PGD-A3-05`

Technology Stack §21.1 **added** the resident store (4 vCPU / 16 GB / 500 GB, HA pair) and records
that *"the RFP §5.9 sizing table predates the split-residency decision."* **`02-05` §8.1 still does
not carry it**, and `02-05` §8.2's cost progression therefore excludes it — which is exactly what
`GV-008` §4.3's caveat says.

**Required lines, in shape:**

| Line | Shape |
|---|---|
| `Z4` production | HA pair, small compute, ~500 GB |
| **`Z4` standby (`dr`)** | **The same again** — `SC-007-DR-1`, `PE-002` §5.12 |
| **In-country key custody** | HSM or managed KMS (`SC-006` `ES-3`) — **the disproportionate line** |
| Cross-border private link | Low bandwidth; **latency and availability are the constraint** (`PE-001` §8.2) |
| Facility | Colocation at Tier III+ (`PE-001` §3.3) |

### 5.4 The `dr` line — `OP-02`

| Element | Shape |
|---|---|
| `RGN-S` standing compute | **Minimal** — replication and health checks only (`PE-002` §5.12.1) |
| Replicated storage | **Full size of `Z3`** — storage-dominated |
| Replication egress | Continuous, cross-failure-domain |
| **`BKP-3`** | Immutable object storage **outside the primary account**, plus egress |
| Failover capacity | **Zero standing cost** — scaled from IaC (`PE-003`) |

### 5.5 The pooler, sized

| Property | Value |
|---|---|
| Placement | `Z2`, in front of the primary and each replica |
| Mode | Transaction pooling for short OLTP work; **session pooling where the workload needs session state** |
| Target | **~264 client connections → 40–60 server connections** [DERIVED, §4.3] |
| HA | ≥ 2 instances (`PE-001` `HA-01` — it becomes a total-outage dependency the moment it exists) |
| Consequence | **Constrains ORM patterns**: session-scoped features must be identified before transaction pooling is enabled |

> **A pooler is not free.** It changes what the application may assume about connection state.
> **Introducing it in Wave 6 under load pressure is a far worse experience than designing for it in
> Wave 1**, which is why `Q-02` is a Wave 1 question.

---

## 6. Growth Across the Waves

### 6.1 The published progression

Technology Stack §21.2 gives per-wave sizing and cost from **$450–700/month (W1)** to
**$4,000–5,800/month (W9)**, cumulative **~$8K / ~$19K / ~$44K** for years 1–3.

### 6.2 What drives each step

| Wave | Capacity event | Volume driver |
|---|---|---|
| **W1** | Baseline + **`Z4` from day one** + HA for the four total-outage components | `NFR-086`; `PE-001` `HA-01` |
| W2 | TimescaleDB arrives | **GPS only** — 800/min (§4.4) |
| W3 | First read replica; payments | Reporting offload |
| W4 | Second replica; corporate portal | `NFR-039` before ClickHouse |
| W5 | Primary to 16 vCPU/64 GB | Order volume growth |
| **W6** | **Redpanda; ML inference** | Event volume (§4.6) crossing Redis Streams' comfort |
| W7 | Portal nodes ×3 | `NFR-004` — marketplace at W7 |
| **W8** | **ClickHouse** | `NFR-039` analytical query at volume |
| W9 | Steady state | — |

### 6.3 Two capacity events the progression does not carry

| # | Event | When | Why it is absent |
|---|---|---|---|
| **1** | **Telemetry at 50,000/minute** (`NFR-055`) | Whenever M48 IoT lands | §21.2 adds TimescaleDB at W2 for **GPS**. Telemetry is **62.6× larger** and appears in no wave row (§4.4) |
| **2** | **The connection pooler** | **W1**, before the connection count grows | Absent entirely (§5.5) |

> **`PE-006-F-06`. The wave progression sizes the time-series tier for GPS and never for telemetry.**
> Either `NFR-055` is deferred — legitimate, it is `P2` — **or a capacity event 62.6× larger than the
> one that was planned arrives in a wave nobody has identified.** `Q-05`.

---

## 7. Scaling Triggers

### 7.1 The principle

> **`PE-006-D-02`. Every tier has a stated signal, threshold and action. Scaling is a planned
> response to a measured signal, not a reaction to an outage.**

### 7.2 The triggers

| Tier | Signal (USE) | Threshold | Action | Lead time |
|---|---|---|---|---|
| **Odoo app** | Worker saturation | **> 70% sustained 15 min** | Add a node (12 workers) | Minutes — but see §7.3 |
| Odoo cron | Job queue depth / overrun | A job overruns its window | Add a cron node; **never autoscale** | Minutes |
| **Portals** | CPU and request latency | > 65% CPU or p95 approaching `NFR-001` | **Autoscale** (`PE-005` §7.2) | Seconds |
| Domain services | CPU, queue depth | > 70% | Autoscale | Seconds |
| **PostgreSQL primary** | **Connection saturation, replication lag, IOPS** | **> 70% connections** *(→ pooler first, §5.5)*; lag > 30 s | Pooler → vertical scale → **read offload** | **Hours to days — vertical scaling is a restart** |
| Read replicas | Replica CPU, replication lag | > 70% | Add a replica | Hours |
| **TimescaleDB** | **Ingest lag, disk growth rate** | Disk to 70%, or projected full within 90 days | **Compression policy → retention → capacity** | **Days** |
| ClickHouse | Query latency vs `NFR-039` | p95 > 8 s | Scale out | Days |
| Redis | Memory, evictions | **Any eviction on a session keyspace** | Scale up | Minutes |
| Event bus | Consumer lag, **outbox age** | **Outbox age > 60 s** (`AR-009` §5.4) | Scale consumers → relay → broker | Minutes |
| Object storage | Growth rate | Projected 80% within 90 days | Extend | Days |
| **`Z4` resident** | **Availability, `CD-233` latency** | **Any** availability event | **Escalate — it gates every `T5` read** | Immediate |

### 7.3 The trigger that is not what it appears

> **Adding an Odoo node adds 12 workers *and* 12 database connections.** Scaling the application tier
> under load therefore **increases pressure on the tier that cannot scale horizontally**. Without the
> §5.5 pooler, the app-tier trigger at 70% worker saturation can make the incident worse.
>
> **`SC-01`. The pooler is a prerequisite for the Odoo app-tier scaling trigger**, not an
> optimisation to be added later.

### 7.4 Why linear extrapolation is not used

Under the **Universal Scalability Law**, throughput does not scale linearly: contention and coherency
costs mean doubling nodes yields less than double, and beyond a point yields **less**. The estate's
coherency costs are real — a shared primary database, a shared cache, an outbox all nodes write.

> **`PE-006-D-03`. Capacity is projected from measurement, not from linear extrapolation**, and
> §10's `perf` runs at 1×, 1.5× and 2× exist to find where the curve bends. **A plan that assumes
> linearity will under-provision precisely at the point it matters.**

---

## 8. Cost

### 8.1 What the register carries

`GV-008` §4.3 line 3: **$52K–$96K over three years**, from `02-05` §8.2, with the caveat that it is
*"sized for the `SB-2` scope and for a single region"* and **excludes the resident store**.

### 8.2 The three excluded lines

| # | Line | Basis | Shape |
|---|---|---|---|
| **1** | **`BD-R`** — `Z4` production + standby + in-country key custody + private link + facility | `PGD-A3-05`; `GV-008` `Q-03` | Small compute; **key custody and facility dominate** |
| **2** | **`dr`** — `RGN-S` standing + replicated storage + egress + **`BKP-3`** | **`OP-02`** | **Storage- and egress-dominated**; compute near zero |
| **3** | **Eleven non-production environments** | `PE-002` §9.1 | Mostly small; **`perf` and `migration-staging` are the exceptions, made cheap by being ephemeral** (`PE-002` §9.3) |

> **`PE-006-F-07`. `02-05` §8.2 is a production-only progression being read as a total
> infrastructure figure.** `PE-002` §9.1 reached the same conclusion from the environment side.
> **Two documents now independently find that the estate's infrastructure budget covers one
> environment of twelve, one site of three, and excludes the resident store the architecture
> requires.** Referred to `GV-008` and `CO-005`.

### 8.3 Cost per transaction

| Measure | Derivation | Use |
|---|---|---|
| **Infrastructure cost per service order** | Monthly infrastructure ÷ orders/month | Trend, **not a target.** Falls with scale; a rise signals inefficiency |
| **Third-party cost per order** | `02-05` §8.3's $1,890–5,230/month ÷ orders | **Rises with volume** — SMS, WhatsApp and Maps are per-use |
| **Total cost per order** | Both | `GV-008`, `BM-*` benefit realisation |

> **The two move in opposite directions**, and reporting only the first flatters the picture as
> volume grows. **`PE-006-D-04`: both are reported, together, monthly.**

### 8.4 Cost controls

| # | Control |
|---|---|
| **CO-01** | Every resource carries a `cost-centre` tag (`PE-003` `NT-02`), so spend is attributable |
| **CO-02** | Cluster autoscaling is **bounded** (`PE-005` `CC-03`) |
| **CO-03** | `perf` and `migration-staging` are **ephemeral** (`PE-002` §9.3) |
| **CO-04** | Non-production environments **scale down or stop outside working hours** where their purpose permits |
| **CO-05** | **Monthly variance > 15% against the wave budget alerts** (Technology Stack §17.2) |
| **CO-06** | A plan whose cost delta exceeds a threshold requires CFO visibility (`PE-003` `PL-12`) |

---

## 9. The Performance-Engineering Baseline

### 9.1 What `DoD-14` requires

*"Performance tested against applicable NFRs **at 1.5× expected peak**."* This section makes "expected
peak" a number.

### 9.2 The load model

| Profile | Derived from | Load |
|---|---|---|
| **1× peak** | §4.3, §4.7 | 1.14 orders/s · 40 internal req/s · 1,250 portal req/s · 800 GPS/min |
| **1.5× peak** | **`DoD-14`** | 1.7 orders/s · 60 internal req/s · 1,875 portal req/s · 1,200 GPS/min |
| **2× peak** | §7.4 | Where the curve bends |
| **Soak** | 24 h at 1× | Leaks, connection exhaustion, disk growth |
| **Spike** | 0 → 1.5× in 60 s | Autoscaling and pooler behaviour |
| **Telemetry** | `NFR-055` | **50,000 points/min, separately** — it shares nothing with the OLTP path |

### 9.3 What is asserted

| NFR | Target | Where |
|---|---|---|
| `NFR-001` | ERP screen ≤ 2 s p95 | `perf` |
| `NFR-002` | API ≤ 400 ms p95 | `perf` |
| `NFR-003` | 800+ concurrent internal, no degradation | `perf` |
| `NFR-004` | 75,000+ concurrent portal | `perf` |
| `NFR-005` | Standard report ≤ 20 s | `perf`, **at year-5 data volume** |
| `NFR-039` | Analytical query ≤ 10 s p95 | `perf` with ClickHouse, W8 |
| `05-03` §5.3 | Six endpoint classes, p50/p95/p99 | `perf`, per `IN-002` `x-endpoint-class` |
| **`NFR-043`** | **Event delivery ≤ 5 s p95** | `perf` — **and it is the outbox that determines it** (§4.6) |

### 9.4 Rules

| # | Rule |
|---|---|
| **PT-01** | Tests run in **`perf`**, at production-shaped volume (`PE-002` §5.6) |
| **PT-02** | **Data volume matters more than request rate** for `NFR-005` and `NFR-039`. Testing against an empty database tests nothing |
| **PT-03** | A run reports **p50, p95, p99 and the error rate** — a mean hides everything |
| **PT-04** | **Results are compared against the previous run**, not only against the target. A 40% regression that still passes is a finding |
| **PT-05** | Every run captures **resource utilisation** (`USE`), so a pass with a saturated resource is visible |
| **PT-06** | **`perf` runs at every wave gate** (`PE-004` §4.2 `gate` profile) |
| **PT-07** | A test that cannot reach 1.5× is a **finding about the test harness or the system** — never a reduced target |

### 9.5 The measurement that must happen first

**Before Wave 1 sizing is fixed**, three numbers must be measured, because §3.2 says they cannot be
calculated:

| # | Measurement | Method |
|---|---|---|
| **M-01** | **CPU-seconds per representative Odoo request** | A small `perf` run on the W1 module set |
| **M-02** | **Rows and outbox rows written per service order** | Instrumented transaction on `staging` |
| **M-03** | **Mean event fan-out per order** | Event-registry counters (`IN-003`) under a synthetic order load |

> **These three convert every "ASSUMED" in §4 into a derived value**, and they are cheap — hours of
> work on an environment that must exist anyway. **`PE-006-D-05`: they are scheduled at W1, not at
> the W2 gate**, because they change what Wave 1 provisions.

---

## 10. What Must Be Measured, and When

| # | Quantity | Measured | Wave | Consumer |
|---|---|---|:--:|---|
| M-01 | CPU-seconds per request | Small `perf` run | **W1** | Odoo node count |
| M-02 | Rows + outbox rows per order | Instrumented `staging` | **W1** | Primary sizing, `DA-001` |
| M-03 | Event fan-out per order | `IN-003` counters | **W1** | Event bus, outbox |
| M-04 | Portal cache hit ratio | `staging` under synthetic load | W2 | Portal node count, `PE-005` autoscaling |
| M-05 | **Time-series compression ratio achieved** | TimescaleDB after 30 days | **W2** | **Whether 4 TB lasts 2 years or 15** |
| M-06 | Query cost at 5 m rows | `perf` at volume | W3 | `DA-001` partitioning |
| M-07 | USL coefficients (contention, coherency) | 1×, 1.5×, 2× runs | W3 | §7.4's projections |
| M-08 | Actual cost per transaction | Billing vs volume | W3 | §8.3 |

> **A capacity plan is a hypothesis until these are measured.** This document states its assumptions
> explicitly (§3.1) so that each measurement either confirms one or corrects it — which is the only
> honest way to size a system that does not yet exist.

---

## 11. Fitness Functions

Allocation confirmed by enumerating every `FF-nn` definition across all authored categories at
**2026-08-19 01:15 (+06)**, per `PGD-AUDIT-007` `PGD-A7-01`.

| # | Check | Scope | Timing | Enforcement |
|---|---|---|---|---|
| **FF-147** | Every tier has a defined scaling trigger with a signal, threshold and action, and it is instrumented in `PE-008` | 12 tiers | Wave gate | **Fail** |
| **FF-148** | No tier exceeds its trigger threshold for more than one review cycle without an action | All | Weekly | **Alert** → gate finding |
| **FF-149** | **`N−1` headroom holds**: losing one node in any pool leaves no pending workload | All pools | Continuous | **Fail** |
| **FF-150** | **A `perf` run at 1.5× exists for the current wave**, with p50/p95/p99 and utilisation | Per gate | Wave gate | **Fail** |
| **FF-151** | No `perf` result regresses more than 20% against the previous run without a recorded explanation | Per gate | Wave gate | **Fail** |
| **FF-152** | **Time-series compression and retention policies are configured and effective**, and projected disk-full is beyond 12 months | TimescaleDB | Monthly | **Fail** |
| **FF-153** | Direct database connections stay below the pooler's client limit; **no service bypasses the pooler** | All | Continuous | **Fail** |
| **FF-154** | **Cost per service order is reported monthly, both infrastructure and third-party** | Monthly | Monthly | **Fail** |

---

## 12. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `PE-006-D-01` | How numbers are presented | Assert · re-derive silently · **label every number stated / derived / assumed** | **Label** | `GV-008-D-03` declined to re-derive because *"inventing a figure would be worse."* The answer is to label, not to avoid | §3.1; every §4 derivation shows its arithmetic and its assumptions |
| `PE-006-D-02` | Scaling | React to incidents · **stated signal, threshold and action per tier** | **Stated triggers** | A trigger discovered during an outage is discovered too late | §7.2; `FF-147` |
| `PE-006-D-03` | Projection method | Linear extrapolation · **measurement plus USL awareness** | **Measurement** | Shared primary, shared cache and a shared outbox make coherency costs real; linearity under-provisions where it matters | §7.4; M-07 |
| `PE-006-D-04` | Cost reporting | Infrastructure per order · **both infrastructure and third-party** | **Both** | They move in opposite directions; reporting one flatters the picture as volume grows | §8.3; `FF-154` |
| `PE-006-D-05` | When the three unmeasurables are measured | At the W2 gate · **at W1, before sizing is fixed** | **W1** | They change what Wave 1 provisions, and they cost hours | §9.5 |
| `PE-006-D-06` | Sizing horizon | Year 3 · **year 5, reached progressively** | **Year 5** | It is what `NFR-053` states; the alternative leaves Wave 8's basis unstated | §4.2; `Q-01` confirms |
| `PE-006-D-07` | Connection pooler | Add when needed · **design in from W1** | **From W1** | Introducing a pooler under load changes ORM assumptions at the worst possible time | §5.5; `SC-01` |

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **Is the Wave 8 sizing a year-5 or a year-3 target?** (`PE-006-F-01`) One reading over-provisions at go-live; the other leaves the basis unstated | CTO + Chief Architect | **W1** | §6, §8 |
| **Q-02** | **Is a connection pooler in the design and the budget?** ~264 direct connections; absent from every sizing table (`PE-006-F-02`, `PE-005-F-02`) | Chief Architect + CTO | **W1** | Odoo scaling trigger, portal autoscaling |
| **Q-03** | **Are time-series compression and retention policies specified?** They decide whether 4 TB lasts 2 years or 15 (`PE-006-F-03`) | `DA-001` + `DA-006` owners | **W2** | TimescaleDB sizing |
| **Q-04** | **What is the partition key, and is the outbox partitioned and pruned?** (`PE-006-F-04`, `PE-006-F-05`) | `DA-001` owner | **W1** | Primary sizing, `NFR-005`, `NFR-043` |
| **Q-05** | **Is `NFR-055` telemetry in scope, and in which wave?** It is `P2` and **62.6× the GPS volume** (`PE-006-F-06`) | Chief Architect + Steering | **W2** | Time-series sizing and cost |
| **Q-06** | Does `CO-005` publish the three excluded cost lines, or does `GV-008` carry them? (`PE-006-F-07`) | CFO | **W2** | `GV-008` §4.3 |
| Q-07 | Are the §4 assumptions — 300 operating days, 2.7 peak factor, 4 photographs per order — accepted, or does the business have better figures? | Business Owners Forum | W1 | Every §4 derivation |

---

## 14. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every stated volume is collected in one place with its source | §4.1 — 13 volumes |
| AC-02 | Load is **derived with the arithmetic shown**, and assumptions are labelled with their sensitivity | §4.3, §4.4, §4.7 |
| AC-03 | Derivation is **reconciled against the published sizing**, agreements and disagreements both | §5.1, §5.2 |
| AC-04 | The **telemetry-vs-GPS asymmetry** is quantified | §4.4 — **62.6×**, `PE-006-F-03` |
| AC-05 | **The outbox is identified as the hottest table**, and its requirements referred to `DA-001` | §4.6, `PE-006-F-05` |
| AC-06 | The **connection pooler** is sized and made a prerequisite of the app-tier trigger | §5.5, `SC-01` |
| AC-07 | Every tier has a signal, threshold, action **and lead time** | §7.2 |
| AC-08 | Linear extrapolation is **rejected with a reason** | §7.4, `PE-006-D-03` |
| AC-09 | The **three excluded cost lines** are named and shaped | §8.2, `PE-006-F-07` |
| AC-10 | `DoD-14`'s *"1.5× expected peak"* is a **number** | §9.2 |
| AC-11 | What **cannot be calculated** is listed, with when it will be measured | §3.2, §10 |
| AC-12 | Fitness-function allocation was enumerated before allocation | §11 |

**Definition of done.** Complete when every criterion is met, **Q-01…Q-05 are answered**, `M-01`…
`M-03` are measured at W1, `FF-147`…`FF-154` are enabled, and `PGD-000`'s `PE-006` row carries a
fresh enumeration timestamp. **This plan is a hypothesis until §10's measurements land**, and it says
so rather than presenting derived numbers as facts.

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | **`AR-001`** §8.6 | The sizing **driver** per component; *"sizing is `PE-006`'s deliverable"* |
| Upstream | `05-06` | `NFR-053`…`NFR-060` and the performance NFRs |
| Upstream | Technology Stack §21 | The published sizing and wave progression |
| Upstream | **`PE-001`**, **`PE-002`**, **`PE-005`** | Sites; twelve environments; the resource model |
| Downstream | **`PE-005`** §7 | §5's values are its requests and limits |
| Downstream | **`PE-008`** | §7's triggers must be instrumented |
| Downstream | **`DA-001`** | **Partition key, outbox indexing and pruning, time-series compression and retention** — all capacity-critical |
| Downstream | `GV-008`, **`CO-005`** | §8's three excluded lines |
| Downstream | `QA-005`, `PE-004` `gate` | §9 is the performance-test charter |
| Lateral | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` §8.1, §8.2 | **Sizing without the resident store; cost without eleven environments and `dr`** |

---

## 16. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`./PE-001_Infrastructure_and_Network_Architecture_Design.md`](./PE-001_Infrastructure_and_Network_Architecture_Design.md) ·
[`./PE-002_Environment_Strategy_and_Specification.md`](./PE-002_Environment_Strategy_and_Specification.md) ·
[`./PE-005_Containerisation_and_Orchestration_Design.md`](./PE-005_Containerisation_and_Orchestration_Design.md) ·
[`./PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md`](./PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md) ·
[`./PE-008_Observability_and_Monitoring_Design.md`](./PE-008_Observability_and_Monitoring_Design.md) ·
[`../02_Architecture_and_Design/AR-001_Software_Architecture_Document.md`](../02_Architecture_and_Design/AR-001_Software_Architecture_Document.md) ·
[`../00_Programme_Governance_and_Control/GV-008_Programme_Budget_and_Cost_Baseline.md`](../00_Programme_Governance_and_Control/GV-008_Programme_Budget_and_Cost_Baseline.md)

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_*.md` ·
`../../1000fix_ERP_Module/02_Architecture/02-05_*.md` §8 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §21 ·
`../../project_content/_AUDIT/AUDIT-017_*.md` `OP-02`

**External sources**

| Source | Verified |
|---|---|
| ISO/IEC 25010 — performance efficiency | 2026-08-19 |
| ISO/IEC 25023 — measurement of quality characteristics | 2026-08-19 |
| Little's Law — `L = λW` | 2026-08-19 |
| Gunther, *Universal Scalability Law* — contention and coherency | 2026-08-19 |
| Gregg, *USE method* — utilisation, saturation, errors | 2026-08-19 |
| Google SRE — capacity planning, headroom, `N−1` | 2026-08-19 |

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Platform Engineering | Initial issue. **Derives load from volume with the arithmetic shown**, labelling every number stated, derived or assumed (`PE-006-D-01`). Finds that **telemetry generates 62.6× the annual data points of GPS while being `P2` to GPS's `P1`** (`PE-006-F-03`), that **the outbox is the hottest table in the estate and appears in no sizing table** (`PE-006-F-05`), that **~264 direct database connections require a pooler nobody has sized** (`PE-006-F-02`), and that **the Wave 8 target is a year-5 volume in a 3-year programme** (`PE-006-F-01`). Names the **three cost lines `02-05` §8.2 excludes** (`PE-006-F-07`), gives every tier a scaling trigger with a lead time, and states plainly that the plan is a **hypothesis until §10's eight measurements land** | *Pending — CTO, CFO; `GV-002` not constituted* |

---

*`PE-006` · Category 10 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
