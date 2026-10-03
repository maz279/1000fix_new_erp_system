---
id: QA-006
title: Performance and Load Test Plan
category: 08 — Quality Engineering & Test
code: QA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering Lead with the QA Lead
approver: Chief Architect with the Chief Technology Officer
standards_basis: >
  ISO/IEC/IEEE 29119-3:2021 §8 (test plan) · ISO/IEC 25010:2023 (performance efficiency) ·
  ISO/IEC 25023:2016 (measurement of product quality) · ITU-T / percentile reporting practice
traces_to: >
  PGD-000 QA-006 · 05-06 §1 (19 performance targets) · §2 (11 availability) · §3 (10 scalability) ·
  05-06 §11 (performance at 1.5× expected peak, before each wave gate) · 06-02 G1-10, G9-03 ·
  TS-014 (37 scenarios) · AUDIT-014 TS-04 (NFR identifier defects)
depends_on: QA-001 (levels, environments) · QA-004 §8 (volume generation) · QA-005 (runner, result shape) · RQ-006 (NFR baseline) · PE-002, PE-006 (unwritten)
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 22:01 (+06)
priority: P1
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# QA-006 — Performance and Load Test Plan

### Category 08 · Code `QA` · ISO/IEC/IEEE 29119-3:2021 §8 · ISO/IEC 25010:2023 · ISO/IEC 25023:2016

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `QA-006` exists in `PGD-000` Category 08, status ◐ `P1` `W3`.
>    **This document is issued at `W1`, not `W3`** — see §1.2 and `QA-001` `MTS-R6`.
> 2. **`PG-03` Count, do not consult.** Every target below is counted from `05-06` §1–§3 at
>    **2026-08-18 22:01 (+06)**: **19 performance targets, 11 availability, 10 scalability**.
> 3. **`PG-06` Cite standards.** §2.1, including why percentiles are reported and means are not.
> 4. **`PG-M4` Verify citations.** k6 2.0 released 11 May 2026, verified 2026-08-18.

---

## 1. Purpose

`05-06` sets **19 numeric performance targets**, and `05-06` §11 requires every one of them verified
**at 1.5× expected peak, before each wave gate**. `TS-014` supplies 37 scenarios naming those
targets. **What has never existed is the statement of how 250,000 customers a month and 51+ branches
are simulated, and on what hardware.**

That is what this document supplies: the workload models, the volumetric basis, the environment the
tests need, the assertion rules, and the position on the two things the estate has never had — a
**production baseline** and a **capacity model**.

> **A number with no scenario behind it is unverifiable, which means it is not a requirement but an
> aspiration.** `TS-014` states this and is right. Nine wave gates and the expansion-readiness gate
> are all claimed against these figures.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **The measurable target set** — 19 performance, 11 availability, 10 scalability, and which are testable when (§3) |
| 2 | **The volumetric model** — where 250,000 customers/month, 51+ branches and 400 technicians turn into requests per second, **and the finding that `NFR-004` is 3,000× above what they support** (§4) |
| 3 | **The six workload profiles** — normal, peak, 1.5× peak, soak, spike, breakpoint (§5) |
| 4 | **Scenario design** — think time, pacing, ramp, data variety, and the four things that invalidate a run (§6) |
| 5 | **The `PERF` environment** — sizing, the production-parity rule, and what a non-parity result may be used for (§7) |
| 6 | **Assertion and reporting** — percentiles, not means; the distribution rule (§8) |
| 7 | **The wave schedule** — what is tested at each gate, and `G9-03` full-scale (§9) |
| 8 | **Client-side and field performance** — the targets no server-side load test can prove (§10) |
| 9 | **Diagnosis** — what a failed run must produce to be actionable (§11) |
| 10 | **The two gaps this document cannot close** (§12) |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| The NFR targets themselves | `05-06`, `RQ-006` | Consumed. This document verifies; it does not set |
| Capacity planning, sizing, scaling triggers, cost-per-transaction | `PE-006` ◐ | **A capacity plan predicts; a performance test measures.** §12.1 states the dependency |
| Infrastructure design and provisioning | `PE-001`, `PE-002` ⛔ | §7 states the requirement |
| Production monitoring and synthetic checks | `SV-*` | `NFR-001` is *"measured by synthetic monitoring"* in production; this plan covers pre-production |
| Test data volume generation | `QA-004` §8 | Consumed |
| The runner, fixtures, result shape | `QA-005` §12.1 | Consumed |
| Availability and DR failover exercises | `PE-007` ⛔ | §3.3 — `NFR-051`, `NFR-052` are DR drills, not load tests |

### 1.2 Why this is issued at `W1` and not `W3`

`PGD-000` registers `QA-006` as `W3`. **`G1-10` requires *"performance targets met for delivered
screens"* at Month 4**, evidenced by a load test report. Under `QA-001` `MTS-R6` — a test artefact is
due at `wave(earliest consuming gate) − 1` — a plan first consumed at `G1` is due **`Now`**.

This is the same defect `AUDIT-014` `TS-02` found in nine content packs, appearing here in the
*guiding* register. It is recorded as **`QAA-10`** and corrected in `PGD-000` at this issue.

### 1.3 Intended audience

| Audience | Use |
|---|---|
| **Platform Engineering** | §4, §5, §7 — the workload model and the environment they must build |
| **QA engineers** | §6, §8 — scenario design and assertion rules |
| Chief Architect | §11, §12 — diagnosis, and the two gaps |
| Wave-gate assessors | §8, §9 — what a performance result must contain to be `E2`/`E5` evidence |
| CFO | §7.4 — the `PERF` environment is the most expensive environment in the estate, and why |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure and rationale |
|---|---|---|
| **ISO/IEC/IEEE 29119-3:2021 §8** | This is a level test plan under `QA-002` `LP-6`; the §8 elements not restated here are inherited from `QA-002` §2.1 | None |
| **ISO/IEC 25010:2023** | *Performance efficiency* — time behaviour, resource utilisation, capacity — is the characteristic under test | None |
| **ISO/IEC 25023:2016** | Measurement functions for performance efficiency: response time, throughput, turnaround time, utilisation | **Departure:** 25023's mean-based measures are **not** used for user-facing targets. §8.1 states why |
| **Percentile reporting** | p50, p95, p99 reported for every response-time target; **the mean is never the headline** | The estate's own targets are stated as p95 (`NFR-001`, `NFR-002`, `NFR-032`, `NFR-035`, `NFR-039`, `NFR-042`), so mean-based reporting would not even answer them |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `05-06` §1 | **19 performance targets** — `NFR-001`…`005` and `NFR-031`…`044` — each with a target, a measurement method and a priority |
| `05-06` §2 | **11 availability and continuity targets** — `NFR-006`…`008`, `NFR-045`…`052` |
| `05-06` §3 | **10 scalability targets** — `NFR-009`, `NFR-010`, `NFR-053`…`060` |
| `05-06` §11 | *"Performance: every NFR performance target, at **1.5× expected peak**. Before each wave gate"* |
| `06-02` `G1-10`, `G9-03` | *"Performance targets met for delivered screens"* (M4) · *"Full-scale load test passed at 1.5× projected peak"* (M36) |
| `TS-014` | 37 scenarios; identifiers `PERF-NFR-nnn-nn`; **38 distinct identifiers counted** at 22:01 (+06) |
| `AUDIT-014` `TS-04` | Four defects in the `NFR` identifier space, including the `NFR-090` triple-use and the Master Index's wrong `TS-014` trace |
| `QA-004` §8 | Volume generation from statistics — 5M orders, 5M assets, with distribution |
| `QA-005` §12.1 | k6 2.0 as the runner; shared fixtures and result normalisation |
| `02-05` §8 | Production hardware sizing — *"a shopping list, not an infrastructure design"* (`PGD-000` Category 10) |
| `06-01` §6 | Rollout: pilot → Dhaka (~20 centres) → major cities → national (51+) |

### 2.3 What this document closes

| Finding | Source | How | Residual |
|---|---|---|---|
| `QA-006` register row ◐ | `PGD-000` | *"Nothing states how 250,000 customers/month and 51 branches are simulated, or on what hardware"* — §4 and §7 | `PERF` environment funding — `Q-01` |
| `TS-014` `O-02` | `AUDIT-014` `TS-04` | §3.4 states the identifier position: `NFR-090` is never cited bare | `RQ-006` renumbering |
| `TS-014` `O-07` | `AUDIT-014` `TS-04` | The `NFR-090` §7 coverage gate has **no gate criterion in `06-02` §4**; `QA-010` §6 adds it | — |
| `M-09` | prior audit | *"Wave capacity was never validated against effort"* — out of scope here, but §12.1 records that `PE-006` `NFR` volumetrics have the same unvalidated shape | `PE-006` |

---

## 3. The Target Set

### 3.1 Performance — 19 targets, `05-06` §1

*Counted at 2026-08-18 22:01 (+06). Every one is verified by this plan.*

| ID | Target | Type | Method | Pri | First testable |
|---|---|---|---|:--:|:--:|
| `NFR-001` | ERP screen load ≤ **2 s p95** | Response | Synthetic monitoring | P0 | **W1** |
| `NFR-002` | API response ≤ **400 ms p95** | Response | Gateway metrics | P0 | **W1** |
| `NFR-003` | **800+ concurrent internal users** | Concurrency | Load test | P0 | W2 |
| `NFR-004` | **75,000+ concurrent portal users** | Concurrency | Load test | P0 | W2 |
| `NFR-005` | Standard report ≤ 20 s | Response | Report timing log | P1 | W1 |
| `NFR-031` | Customer 360 view ≤ 2 s | Response | Instrumentation | P0 | **W1** |
| `NFR-032` | Booking availability ≤ 800 ms p95 | Response | API metrics | P0 | **W1** |
| `NFR-033` | Dispatch board refresh ≤ 1 s **for 500 open jobs** | Response @ volume | Instrumentation | P1 | **W1** |
| `NFR-034` | Live map update ≤ 5 s from GPS emission | End-to-end latency | Trace | P1 | W2 |
| `NFR-035` | Search ≤ 600 ms p95, **any entity, including Bengali text** | Response | Instrumentation | P1 | **W1** |
| `NFR-036` | Technician app job list on 3G ≤ 8 s cold / ≤ 2 s warm | **Client + network** | **Field test** | P0 | W2 — §10 |
| `NFR-037` | Offline sync after 24 h ≤ 30 s on 3G | **Client + network** | **Field test** | P0 | W2 — §10 |
| `NFR-038` | Executive dashboard ≤ 5 s | Response | Instrumentation | P1 | W4 |
| `NFR-039` | Warehouse analytical query ≤ 10 s p95 | Response | Warehouse metrics | P2 | W8 |
| `NFR-040` | Invoice generation from closure ≤ 5 s | Response | Instrumentation | P0 | W3 |
| `NFR-041` | Bulk operation, 1,000 records ≤ 60 s **with progress feedback** | Throughput | Load test | P1 | W2 |
| `NFR-042` | Payment confirmation round trip ≤ 3 s p95 | Response | Gateway metrics | P0 | W3 |
| `NFR-043` | Event delivery to consumer ≤ 5 s p95 | Latency | Event platform | P1 | W1 |
| `NFR-044` | Nightly route optimisation, **all technicians** ≤ 20 min | Batch | Job monitor | P1 | W2 |

**Ten are `P0`.** Six are p95-stated, which fixes the reporting form (§8.1).

### 3.2 Scalability — 10 targets, `05-06` §3

| ID | Target | How this plan verifies it |
|---|---|---|
| `NFR-009` | 5× users and 10× data over 5 years without re-architecture | **Not a load test.** An architecture assertion — `AR-001` quality-attribute scenario; §12.2 |
| `NFR-010` | Elastic capacity for seasonal and promotional peaks | Spike profile `WP-5` (§5) |
| `NFR-053` | **5M service orders/year by year 5** | `QA-004` §8 generates the volume; every response target is re-run at it |
| `NFR-054` | **5M assets** in the device registry | Same; `NFR-031`, `NFR-035` re-run at it |
| `NFR-055` | Telemetry 50,000 points/minute | Ingestion profile, W8 |
| `NFR-056` | GPS: **400 technicians at 30-second intervals sustained** | Ingestion profile, W2 — 13.3 events/s sustained, and it feeds `NFR-034` |
| `NFR-057` | 5,000 sellers, 50,000 listings | W7 |
| `NFR-058` | **200 branches** without configuration redesign | W9 — 4× the current 51+ |
| `NFR-059` | 10 legal entities, 5 countries | W9; `G9-01`, `G9-02` |
| `NFR-060` | **50 TB document store, sub-10-second retrieval** | W8; retrieval time at volume is a load test, storage capacity is `PE-006` |

### 3.3 Availability — 11 targets, and why most are not load tests

| ID | Target | Verified by |
|---|---|---|
| `NFR-006`, `NFR-045`, `NFR-046`, `NFR-048` | Uptime 99.9% / 99.7% / 99.9% / **99.95% payment path** | **Production measurement over time.** No pre-production test can prove an availability percentage — §12.3 |
| `NFR-007` | **RPO ≤ 15 min, RTO ≤ 2 h** | `PE-007` DR design and drill — **not this plan** |
| `NFR-008` | Zero-downtime deployment | `PE-004` deployment test; measured by this plan as **error rate during a deployment under load** (§5, `WP-6`) |
| `NFR-047` | Technician app functional offline for 24 h | L12 field — §10 |
| `NFR-049` | Maintenance window ≤ 4 h/month, outside 08:00–23:00 BST | Operational policy |
| `NFR-050` | **Every P0 integration has a documented, tested manual fallback** | `SV-*`; **this plan supplies the degradation test** — §5 `WP-7` |
| `NFR-051`, `NFR-052` | DR drill twice yearly; weekly automated restore test | `PE-007` |

> **`PLT-01`.** An availability percentage is **never claimed from a load test**. A soak run showing
> zero errors over 12 hours is evidence of stability, not of 99.9% over a year. `GA-06` and
> `MTS-R1` both apply: the claim states what was measured and over what window.

### 3.4 The identifier position

> **`AUDIT-014` `TS-04`:** `NFR-090`, `NFR-091` and `NFR-092` are each used twice for unrelated
> requirements; `05-06`'s own title says *"NFR-001 … NFR-092"* while the document holds **101**;
> `NFR-088` and `NFR-089` appear a second time as strays in §6.4; and the Master Index traces
> `TS-014` to *"`05-06` NFR-001…044"*, implying 44 requirements when the performance section is
> `NFR-001`…`005` **plus** `NFR-031`…`044`.

| # | Position |
|---|---|
| `PLT-02` | **Every scenario identifier in this plan names the target it verifies with its section** — `PERF-NFR-037-02` is unambiguous, but a bare `NFR-090` is not. This plan cites `NFR-090` §7 or §6.3, never bare |
| `PLT-03` | **This plan's target set is the 19 counted in §3.1**, not the 44 the Master Index's trace implies. The trace is wrong and is corrected as part of `QAA-10` |

---

## 4. The Volumetric Model

### 4.1 Why a volumetric model, and not a concurrency number

`NFR-003` says 800 concurrent internal users and `NFR-004` says 75,000 concurrent portal users. **A
concurrency number alone is not a workload**: 800 users reading a dashboard and 800 users creating
service orders differ by orders of magnitude in load. The model converts business volumes into a
**request mix**.

### 4.2 The business inputs, counted

| Input | Value | Source |
|---|---|---|
| Customers served per month | **250,000+** | BRD; `PGD-000` |
| Service centres | **51+**, rising to 200 (`NFR-058`) | `06-02` `G5-06` |
| Dhaka centres | **~20** | `06-01` §6 |
| Internal users | **500+ employees**, 800+ concurrent target | `NFR-003` |
| Technicians emitting GPS | **400 at 30-second intervals** | `NFR-056` |
| Service orders per year, year 5 | **5,000,000** | `NFR-053` |
| Assets in registry | **5,000,000** | `NFR-054` |
| Portals and applications | **12** | `IN-008` |
| Marketplace sellers | 500–2,000, to 5,000 | `NFR-057` |

### 4.3 Derivation to a request rate

**Rule `PLT-04`: every load figure in this plan is derived, and its derivation is shown**, so a
reviewer can disagree with an assumption rather than with a number.

| Step | Derivation | Result |
|:--:|---|---|
| 1 | 5,000,000 orders/year ÷ 300 working days | **~16,700 orders/day** |
| 2 | Concentrated into a **10-hour** operating day, with a **2.5× peak-hour factor** | **~4,175 orders in the peak hour ≈ 1.16 orders/s** |
| 3 | Each order generates ~14 write operations across its lifecycle (intake, estimate, approval, parts, closure, invoice, payment, survey) | **~16 writes/s at peak** |
| 4 | Read:write ratio observed in service-desk systems ≈ **8:1** | **~130 reads/s at peak** |
| 5 | GPS ingestion: 400 technicians ÷ 30 s | **13.3 events/s sustained** |
| 6 | Portal traffic: 250,000 customers/month × 30% self-service × 6 page views ÷ 30 days ÷ 10 hours × 3 peak factor | **1.25 page views/s at peak** |
| 7 | **Sum at expected peak** — 130 reads + 16.2 writes + 13.3 GPS + 1.25 portal | **≈ 161 requests/s**, of which **~16 are writes** |
| 8 | **× 1.5 per `05-06` §11** | **≈ 241 requests/s, ~24 writes/s** — *the number every gate tests at* |

> **The portal figure is the one that will look wrong, and it is worth pausing on.** 1.25 page
> views/s from a customer base served at 250,000/month is small — and it follows directly from
> `PLT-A6`'s 30% self-service assumption and `PLT-A7`'s 6 views per session. **It is also the figure
> that exposes §4.6's finding**, because `NFR-004` asks for 75,000 *concurrent* portal users.

### 4.4 The assumptions, stated so they can be challenged

| # | Assumption | Value | Sensitivity |
|:--:|---|---|---|
| `PLT-A1` | Working days per year | 300 | Linear |
| `PLT-A2` | Operating hours per day | 10 | Linear |
| `PLT-A3` | **Peak-hour concentration factor** | **2.5×** | **High — this is the least evidenced figure in the model** |
| `PLT-A4` | Write operations per order lifecycle | 14 | Moderate |
| `PLT-A5` | Read:write ratio | 8:1 | Moderate |
| `PLT-A6` | Self-service adoption | 30% | **`G2-08` targets ≥ 60% online booking at pilot sites — at 60% the portal figure doubles, to 2.5 views/s. Even at 100% it is 4.2 views/s** (§4.6) |
| `PLT-A7` | Portal page views per session | 6 | Low |

> **`PLT-05`.** The model is **re-derived at every wave gate against observed production data** once
> W1 is live, and the delta reported. `PLT-A3` and `PLT-A6` are the two that will move most, and
> `PLT-A6` moves *against* the programme's own success — `G2-08`'s 60% target doubles the portal
> load the model assumes.

### 4.5 The transaction mix

**Derived from §4.3, not asserted** (`PLT-04`). The four components of the 161 req/s peak, and how
each is distributed across the transactions that produce it.

| Component | req/s | Share | Distributed across | Targets verified |
|---|---:|---:|---|---|
| **Internal reads** | **129.6** | **81%** | Customer 360 (16%), dispatch board refresh (14%), search (13%), work lists (16%), reporting and dashboards (8%), technician app sync reads (14%) | `NFR-001`, `-005`, `-031`, `-033`, `-035`, `-036`, `-038` |
| **Internal writes** | **16.2** | **10%** | Service order lifecycle (43%), stock movement (21%), invoice and payment (14%), notification dispatch (14%), marketplace (8%) | `NFR-002`, `-040`, `-041`, `-042`, `-043`, `-057` |
| **GPS ingest** | **13.3** | **8%** | Machine-generated, fixed rate, no think time | `NFR-034`, `NFR-056` |
| **Customer portal** | **1.25** | **0.8%** | Browse, search, booking availability lookup | `NFR-032`, `NFR-035`, `NFR-004` |
| **Total** | **160.4** | **100%** | | |

> **`PLT-A8`.** The read:write split of 8:1 (`PLT-A5`) is the assumption that decides 81% of this
> model. It is drawn from service-desk practice rather than from any 1000FiX measurement, and
> `PLT-05` re-derives it against observed production data from the first wave. **A model in which
> four fifths of the load rests on an unmeasured ratio states that plainly rather than burying it.**

### 4.6 Finding — `NFR-004` has no volumetric basis

**This is what deriving the model rather than asserting it surfaced**, and it is the most consequential
thing in this document after the target set itself.

| Source | Figure |
|---|---|
| `NFR-004`, **`P0`** | *"Concurrent customer portal users: **75,000+**"*, measured by load test |
| **§4.3 step 6, derived** | **1.25 page views/s at peak**, which at a 20-second think time is **~25 concurrent portal users** |

> **75,000 concurrent users at a 20-second think time is ~3,750 requests/s — roughly 3,000× the
> portal load the stated business volumes support, and roughly 23× the load of the entire rest of
> the system combined.**

Three readings are possible, and the estate does not say which is intended:

| # | Reading | Consequence |
|:--:|---|---|
| 1 | **`NFR-004` is a headroom target, not a demand forecast** — a deliberate over-provision | Legitimate, but then it is a **scalability** requirement belonging with `NFR-009`/`NFR-010`, not a performance target, and `WP-4` should not be sized from it |
| 2 | **The registered customer base is far larger than 250,000/month** and a promotional peak could bring 75,000 of them in at once | Plausible — **but no registered-base figure exists anywhere in the estate**, so the requirement rests on an unstated number |
| 3 | **The figure is an error**, inherited from *"was 50,000"* in `05-06` §1 without derivation | Also plausible, and `NFR-003` (*"800+, was 500"*) has the same shape |

| # | Position |
|---|---|
| `PLT-37` | **This plan tests `NFR-004` as written**, at 75,000 concurrent, because it is a `P0` requirement and a test plan does not descope a requirement. **It also reports the derivation gap on every performance report**, so the cost of the requirement is visible next to its basis |
| `PLT-38` | **The `PERF` environment is sized for `NFR-004`, not for the derived 161 req/s.** That is a material cost difference — §7.4's ephemeral-parity option becomes the only affordable one — and it is caused by a requirement with no derivation |
| `PLT-39` | **`NFR-004` is referred to `RQ-006` for a stated basis**, under `RQ-005` change control. Recorded as **`QAA-11b`** and `Q-07` |

> **Why this matters beyond one requirement.** `05-06` §1 raises six targets with the annotation
> *"(was N)"* — `NFR-001` 3 s→2 s, `NFR-002` 500→400 ms, `NFR-003` 500→800, `NFR-004` 50,000→75,000,
> `NFR-005` 30→20 s, `NFR-007` 1 h/4 h→15 min/2 h. **None of the six states what changed to justify
> the tightening.** A target tightened without a basis is as unverifiable as one set without one, and
> the programme pays for the difference in `PERF` hardware. Recorded as **`QAA-13`**.

---

## 5. Workload Profiles

Seven profiles. Each has a purpose, a shape, a duration and a pass condition.

| # | Profile | Shape | Duration | Purpose | Pass condition |
|:--:|---|---|---|---|---|
| **`WP-1`** | **Baseline** | 1 virtual user, no contention | 10 min | Establishes the floor, and detects a regression before load is even applied | Every response target met with margin |
| **`WP-2`** | **Normal load** | Expected average — ~64 req/s (40% of peak) | 1 h | The everyday position | All targets met |
| **`WP-3`** | **Expected peak** | ~161 req/s per §4.3 | 1 h, 15-min ramp | The busiest realistic hour | All targets met |
| **`WP-4`** | **1.5× peak** | **~241 req/s**, **plus `NFR-004` concurrency as written** (§4.6) | 1 h, 20-min ramp | **The gate profile — `05-06` §11, `G9-03`** | **All targets met. This is the criterion** |
| **`WP-5`** | **Spike** | Normal → 1.5× peak in **60 s**, hold 10 min, drop | 30 min | `NFR-010` elastic capacity; promotional and seasonal peaks | No error-rate excursion above 0.1%; recovery to baseline within 5 min |
| **`WP-6`** | **Soak** | Expected peak sustained | **12 h**, and **24 h before `G4` and `G9`** | Leaks, connection exhaustion, unbounded growth, log volume | **No degradation trend**: p95 at hour 12 within 10% of hour 1 |
| **`WP-7`** | **Degradation** | Peak load with a P0 integration failed | 30 min | `NFR-050` — every P0 integration has a *tested* manual fallback | The system degrades as designed; no cascade; the fallback is usable |
| **`WP-8`** | **Breakpoint** | Ramp until failure | until failure | Finds the actual ceiling, so headroom is a measurement rather than a hope | **Reported, not passed.** The ceiling is recorded and fed to `PE-006` |

> **`PLT-06`. `WP-8` has no pass condition and that is deliberate.** A breakpoint test that "passes"
> was not run to breakpoint. Its output is a number — the ceiling — and `PE-006` consumes it. Running
> only to 1.5× tells the programme it is above the bar; it never tells it how far above.

### 5.1 Ramp and steady state

| # | Rule |
|---|---|
| `PLT-07` | **Measurements are taken from the steady state only.** Ramp-up and ramp-down are excluded, and the exclusion window is stated in the report |
| `PLT-08` | **Steady state is at least 30 minutes** for `WP-3` and `WP-4`. Shorter runs measure cache warm-up |
| `PLT-09` | **Caches are warmed identically before every run**, and the warm-up procedure is part of the scenario, not a manual step |

---

## 6. Scenario Design

### 6.1 The four things that invalidate a run

Recorded first, because each produces a green result that means nothing.

| # | Invalidator | Rule |
|:--:|---|---|
| 1 | **No think time.** Virtual users hammering with zero pause produce a load shape no human population produces, usually failing on a bottleneck real users never reach | `PLT-10`: every user-facing scenario has think time drawn from a **distribution**, not a constant |
| 2 | **One data value.** Every virtual user requesting customer 4471 tests the cache, not the database | `PLT-11`: **every scenario draws parameters from the full `QA-004` generated set**, with the production-shaped skew of `QA-004` §8.3 |
| 3 | **A non-parity environment.** A result from hardware unlike production is not evidence (`GA-02`) | `PLT-12`: §7.2 |
| 4 | **Reporting the mean.** A 2 s p95 target cannot be assessed from an average | `PLT-13`: §8.1 |

### 6.2 Think time and pacing

| Population | Think time | Basis |
|---|---|---|
| Branch agent at the counter | 5–20 s, log-normal | `G1-03` targets a 3-minute walk-in intake |
| Dispatcher | 2–10 s | Continuous board monitoring |
| Technician on the app | 10–60 s | Between job steps in the field |
| Customer on the portal | 8–45 s, long tail | Browsing, comparing, reading |
| Finance user | 15–90 s | Reviewing before posting |
| System-to-system (GPS, events, integrations) | **None — fixed rate** | Machines do not think |

### 6.3 Scenario inventory

`TS-014` supplies 37 scenarios; **38 distinct `PERF-NFR-nnn-nn` identifiers were counted** at
22:01 (+06). They are adopted, and this plan adds the profiles, mix and derivation they lack.

| # | Rule |
|---|---|
| `PLT-14` | **Every `05-06` §1 target has at least one scenario.** 19 of 19 — verified in §3.1's *first testable* column |
| `PLT-15` | **A scenario names its target in its identifier** (`PERF-NFR-037-02`), so a result maps to a criterion without a lookup |
| `PLT-16` | **Scenarios run in a mix, not in isolation**, at `WP-3` and above. A target met in isolation and missed in the mix is missed |
| `PLT-17` | **Bengali text is in every search and text-entry scenario**, because `NFR-035` explicitly includes it and Bengali collation and indexing behave differently |

### 6.4 What must be in the mix that usually is not

| Element | Why it changes the result |
|---|---|
| **Nightly batch overlapping the tail of the day** | `NFR-044`'s 20-minute route optimisation runs while late jobs are still closing |
| **Month-end close** | `G3-05` requires close within 5 days; it is the heaviest read pattern in the system |
| **Notification storms** | An SLA breach cascade generates a burst of `NFR-043` deliveries |
| **Report generation during peak** | `NFR-005` and `NFR-038` are usually tested quiet; managers run them at peak |
| **Offline sync reconnection burst** | 400 technicians reconnecting after an outage is `NFR-037` × 400 simultaneously — **the most under-tested burst in the system** |

---

## 7. The `PERF` Environment

### 7.1 The requirement

| Element | Requirement |
|---|---|
| Compute | **Production-parity**, per §7.2 |
| Data | **5M orders, 5M assets**, production-shaped distribution (`QA-004` §8) |
| Topology | Same tiers, same replica counts, same connection pooling, same caching, same gateway |
| Network | Representative latency between tiers; **3G emulation available** for client-side scenarios |
| Isolation | **Not shared with any other level** (`QA-001` §7.2) |
| Observability | Full instrumentation — traces, DB statistics, queue depth, resource utilisation |
| Load generators | **Outside** the system under test, with their own headroom |

### 7.2 The parity rule

> **`PLT-12`.** A performance result is evidence **only** for the environment it was produced in
> (`GA-02`). Three positions, and each must be stated on the report:
>
> | Parity | What the result may claim |
> |---|---|
> | **Full parity** — same shape, same sizing, same topology | **The target is met.** This is what a gate requires |
> | **Scaled-down parity** — same shape and topology, proportionally smaller | **A trend and a comparison.** Never an absolute target claim |
> | **Non-parity** | **A regression detector only.** It may show something got worse; it may never show something is fast enough |

**`G1-10` and `G9-03` require full parity.** A gate cannot be passed on a scaled-down result, because
the criterion is an absolute.

### 7.3 The scaled-down interim

`PE-002` is unwritten and **0 of 7 environments are provisioned**. Until `PERF` exists at parity:

| # | Rule |
|---|---|
| `PLT-18` | A scaled-down `PERF` may be stood up for **`WP-1` baseline and regression detection only**, and every result carries the scaled-down label |
| `PLT-19` | **`G1-10` is not evidenceable from a scaled-down environment.** If parity does not exist by T−4 of `G1`, that is a gate entry failure under `EN-06`, recorded at T−6 — not a discovery at the gate |

### 7.4 Cost, stated plainly

**`PERF` at full parity is the most expensive environment in the estate**, and it is used for a few
days per wave. Three options, with the position:

| Option | Assessment |
|---|---|
| Permanent parity environment | Correct and expensive; utilised perhaps 10% of the time |
| **Ephemeral parity environment, stood up from IaC per gate** | **Recommended.** Requires `PE-003` IaC, which records **zero occurrences of "Terraform"** in the estate. It is also the strongest argument for `PE-003` |
| Scaled-down permanent | Cheapest; **cannot evidence `G1-10` or `G9-03`** (§7.2) |

> Recorded as `QA-006-D-04`, and raised as `Q-01`. **The performance environment is the clearest
> case in the programme for infrastructure-as-code**: it is needed nine times, identically, for a few
> days each.

---

## 8. Assertion and Reporting

### 8.1 Percentiles, never means *(`PLT-13`)*

> **A mean response time is compatible with any distribution.** A 1.2 s mean can be 100% of users at
> 1.2 s, or 90% at 0.4 s and 10% at 8 s. The second is a broken product and the first is a good one,
> and the mean does not distinguish them. **Six of this estate's targets are stated as p95**, which
> makes mean reporting not merely weak but non-responsive.

| # | Rule |
|---|---|
| `PLT-20` | **Every response-time result reports p50, p95, p99 and max**, with the sample size |
| `PLT-21` | **The pass/fail assertion is against the percentile the target names.** Where a target names none, **p95 is assumed** and the assumption is stated |
| `PLT-22` | **p99 and max are reported even where not targeted.** A p95 that passes with a 40 s max is a real user experience nobody has agreed to |
| `PLT-23` | **The distribution is published**, not just the summary. `GA-03`'s evidence standard and `E3`'s *"distribution — not just a mean"* both require it |

### 8.2 Assertions live in the scenario

| # | Rule |
|---|---|
| `PLT-24` | **Thresholds are asserted in the script**, so a run fails on its own criteria. A run whose pass/fail depends on a human reading a chart is a run that passes under schedule pressure |
| `PLT-25` | **Error rate is asserted alongside latency.** A fast response that is a 500 is not a pass. Ceiling: **< 0.1% at `WP-4`**, **0% for payment and statutory paths** |
| `PLT-26` | **Resource utilisation is asserted**: a run meeting its targets at 98% CPU has no headroom and is reported as a **conditional pass** with the utilisation stated |
| `PLT-27` | **Saturation is reported**: queue depth, connection pool usage, lock waits, cache hit ratio. These predict the next wave's failure |

### 8.3 The report

Every run produces one, and it is `E2` + `E5` gate evidence.

| Field | Content |
|---|---|
| Profile | `WP-n`, ramp, steady-state window, duration |
| Environment | **Parity statement per §7.2**, sizing, topology, dataset version |
| Workload | Transaction mix, virtual users, achieved request rate |
| Results per target | p50/p95/p99/max, sample size, **pass/fail against the named percentile** |
| Error rate | Overall and per transaction |
| Resource utilisation | CPU, memory, IO, connections, queue depth, at steady state |
| Saturation indicators | §8.2 `PLT-27` |
| **Comparison to previous run** | Delta per target — a regression is visible without re-reading history |
| Diagnosis | For every failure, §11 |
| Tooling | k6 version, script version, seed |

---

## 9. The Wave Schedule

| Wave | Gate | Profiles | Targets added | Note |
|:--:|:--:|---|---|---|
| **W1** | `G1-10` | `WP-1`, `WP-3`, **`WP-4`** | `NFR-001`, `-002`, `-005`, `-031`, `-032`, `-033`, `-035`, `-043` | **Scoped to delivered screens.** Requires parity `PERF` — `PLT-19` |
| **W2** | `G2` | + `WP-5`, `WP-6` 12 h | `NFR-003`, `-004`, `-034`, `-041`, `-044`, `-056` | GPS ingest and the **reconnection burst**; `NFR-036`/`-037` are field — §10 |
| **W3** | `G3` | + `WP-7` | `NFR-040`, `-042` | Payment path at **0% error tolerance** |
| **W4** | `G4` | **`WP-6` at 24 h** | `NFR-038` | v1.0 scope complete — the first full-system peak |
| **W5** | `G5` | as W4 | payroll batch window | |
| **W6** | `G6` | as W4 | rental and refurbishment volume | |
| **W7** | `G7` | as W4 | `NFR-057` | Marketplace at 5,000 sellers / 50,000 listings |
| **W8** | `G8` | + ingestion profile | `NFR-039`, `-055`, `-060` | Warehouse, telemetry, 50 TB document store |
| **W9** | **`G9-03`** | **`WP-4` full-scale + `WP-6` 24 h + `WP-8`** | `NFR-058`, `-059`, `NFR-009` | *"Full-scale load test passed at 1.5× projected peak"*; **`WP-8` establishes the actual ceiling** |

> **`PLT-28`.** Every wave re-runs **every previously verified target**, not only the new ones.
> Performance regression is the most common form of silent regression, and a target verified at W2
> and never re-run is a target that was true once.

---

## 10. Client-Side and Field Performance

### 10.1 The four targets no server-side load test can prove

| ID | Target | Why load testing cannot prove it |
|---|---|---|
| `NFR-036` | Technician app job list on 3G ≤ 8 s cold / ≤ 2 s warm | **Client rendering + real network.** `05-06` §1 states the method: **Field test** |
| `NFR-037` | Offline sync after 24 h ≤ 30 s on 3G | Same; and 24 h of accumulated queue is a client-side state |
| `NFR-001` | ERP screen load ≤ 2 s p95 | Server response is a *component*. A 400 ms API behind a 3 s render is a 3 s screen |
| `NFR-004` | 75,000 concurrent portal users | Server concurrency is testable; **the experience at that concurrency on a real 3G device is not** |

### 10.2 The three-part measurement

| Part | Measures | Where |
|---|---|---|
| **Server-side load** (§5) | Response time under concurrency | `PERF` |
| **Client-side rendering** | Time to interactive, layout stability, main-thread blocking — on the **floor-spec device**, mid-range Android 11 / 3 GB | Device lab, per release |
| **Field measurement** | The two together, on a real network, in a real location | **The field** — `MTS-D5`; `QA-002` §10.2 |

| # | Rule |
|---|---|
| `PLT-29` | **A server-side result is never reported as a screen-load result.** `NFR-001` is a user-observed target; its evidence combines all three parts |
| `PLT-30` | **`NFR-036` and `NFR-037` are `E3` timed observations in the field**, not `E5` test reports. `05-06` §1 says *"Field test"* and `GA-02` makes that binding |
| `PLT-31` | **The reconnection burst is server-side and field-side**: 400 technicians reconnecting simultaneously loads the server *and* each device |

---

## 11. Diagnosis

A performance failure that produces only *"the target was missed"* generates a week of guessing.

| # | Rule |
|---|---|
| `PLT-32` | **Every run captures distributed traces** for a sampled set of each transaction, so a slow transaction is decomposed into its tiers without re-running |
| `PLT-33` | **Database statistics are captured** — slow query log, lock waits, index usage, plan changes. A plan flip at volume is the single most common cause of a target passing at W2 and failing at W4 |
| `PLT-34` | **A failed target names the tier**, not just the number: application, database, queue, gateway, network or client |
| `PLT-35` | **A performance defect is a defect** and enters `TS-018` triage with a severity from `QA-010`. It is not held in a performance report nobody triages |
| `PLT-36` | **A regression is bisected against the previous passing run** using the retained result history and the recorded seed (`PLT-24`, `QA-005` `TAF-35`) |

---

## 12. The Two Gaps This Document Cannot Close

### 12.1 There is no capacity model to test against

`PE-006` is ◐, citing `02-05` §8.1 — *"a Wave 8 steady state with no derivation from volumetrics"*,
and prior audit finding **`M-09`: wave capacity was never validated against effort.**

> **A performance test measures; a capacity plan predicts.** This document derives a workload model
> (§4) because it needs one, and that model is **the first volumetric derivation in the estate**.
> **`PE-006` should adopt §4 as its input rather than deriving a second, different one** — two
> volumetric models would be `TS-08`'s defect repeated on the infrastructure side. Raised as
> **`QAA-11`** and `Q-02`.

### 12.2 `NFR-009` is not testable by this plan

*"5× users and 10× data over 5 years without re-architecture"* is an **architecture** claim, not a
load claim. `WP-8`'s breakpoint gives the current ceiling; whether the architecture scales 5× without
redesign is an `AR-001` quality-attribute scenario assessed by architecture review (`E6`), and the
load test supplies one input to it.

### 12.3 An availability percentage cannot be pre-production evidence

`NFR-006`'s 99.9% is measured over a period in production. `WP-6`'s soak evidences **stability**, and
`WP-7` evidences **graceful degradation**. Neither evidences an annual percentage, and `PLT-01`
forbids claiming it.

---

## 13. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `QA-006-D-01` | Reporting statistic | (a) mean per ISO/IEC 25023; (b) **p50/p95/p99/max** | **(b)** | Six targets are stated as p95; a mean is compatible with any distribution and cannot answer them | Declared departure, §2.1; `PLT-20`…`PLT-23` |
| `QA-006-D-02` | Whether to derive a volumetric model here | (a) wait for `PE-006`; (b) **derive it, show the derivation, offer it to `PE-006`** | **(b)** | `PE-006` is ◐ and `M-09` records capacity was never validated. Waiting means `G1-10` has no basis at Month 4 | §4; `QAA-11` asks `PE-006` to adopt rather than re-derive |
| `QA-006-D-03` | Breakpoint testing | (a) test only to 1.5×; (b) **add `WP-8` with no pass condition** | **(b)** | Testing only to the bar tells the programme it is above the bar and never how far. The ceiling is a number `PE-006` needs | `PLT-06`; reported, not passed |
| `QA-006-D-04` | `PERF` environment model | (a) permanent parity; (b) **ephemeral parity from IaC per gate**; (c) permanent scaled-down | **(b)** | Needed nine times, identically, for a few days each — the clearest IaC case in the programme. (c) cannot evidence `G1-10` or `G9-03` | Depends on `PE-003`, which records **zero "Terraform"** occurrences. `Q-01` |
| `QA-006-D-05` | Client-side targets | (a) treat `NFR-001` as a server target; (b) **three-part measurement, server + client + field** | **(b)** | A 400 ms API behind a 3 s render is a 3 s screen, and `05-06` §1 already names *"Field test"* for `NFR-036`/`-037` | §10; `PLT-29`, `PLT-30` |
| `QA-006-D-06` | Issue wave | (a) `W3` per `PGD-000`; (b) **`Now`** | **(b)** | `G1-10` consumes it at Month 4; `MTS-R6` applies to guiding documents as it applies to content packs | `QAA-10`; `PGD-000` row corrected |

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Is an ephemeral parity `PERF` environment funded, and does `PE-003` IaC exist to build it?** | CTO with CFO and Platform Engineering | **T−6 of `G1`** | `G1-10`; every subsequent gate; `PLT-19` |
| `Q-02` | Does `PE-006` adopt §4's volumetric model, or derive its own? | Platform Engineering with Enterprise Architecture | **W1** | `QAA-11`; avoiding a second, conflicting model |
| `Q-03` | Is `PLT-A3`'s 2.5× peak-hour factor validated against any observed data? | Operations Director | **W2**, once W1 is live | §4.4; the whole model scales with it |
| `Q-04` | At `G2-08`'s ≥ 60% online booking target, `PLT-A6` doubles. Is the model re-derived at W2? | Platform Engineering with QA Lead | **W2** | `NFR-004` sizing |
| `Q-05` | Who owns client-side performance measurement, and is a device lab funded? | Mobile Lead with CFO | **W2** | §10; `NFR-036`, `NFR-037`; shared with `QA-005` `Q-04` |
| `Q-06` | Does `RQ-006` renumber `NFR-090`/`091`/`092` and correct `05-06`'s title and §6.4 strays? | Enterprise Architecture | **W1** | `PLT-02`; `TS-014` `O-02` |
| `Q-07` | **What is `NFR-004`'s basis — headroom target, an unstated registered base, or an error?** And do the other five *"(was N)"* tightenings have one? | Enterprise Architecture with the CCO | **W1** | §4.6; `PERF` sizing and therefore its cost; `QAA-11b`, `QAA-13` |

---

## 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every `05-06` §1 performance target has a scenario and a first-testable wave | §3.1 — **19 of 19** |
| `AC-02` | Scalability and availability targets are allocated to a verifier, including those this plan does not verify | §3.2, §3.3 — 10 and 11 |
| `AC-03` | A volumetric model derives a request rate from business volumes, showing every step | §4.3 — 8 steps to **~241 req/s at 1.5×**, and §4.6's finding that `NFR-004` is 3,000× above it |
| `AC-04` | Every assumption in the model is stated with its sensitivity | §4.4 — 7 assumptions |
| `AC-05` | Workload profiles cover normal, peak, 1.5×, spike, soak, degradation and breakpoint | §5 — 8 profiles |
| `AC-06` | The four run-invalidating conditions are stated with a preventing rule each | §6.1 |
| `AC-07` | The environment parity rule states what each parity level may claim | §7.2 — 3 levels |
| `AC-08` | Reporting is percentile-based, with distribution published | §8.1 — `PLT-20`…`PLT-23` |
| `AC-09` | Client-side and field targets are separated from server-side | §10 — 4 targets, 3-part measurement |
| `AC-10` | Diagnosis requirements make a failure actionable without a re-run | §11 — 5 rules |
| `AC-11` | The gaps this plan cannot close are named rather than implied | §12 — 3 gaps |
| `AC-12` | Where a target and the volumetrics disagree, the disagreement is measured and reported, not resolved by descoping | §4.6 — `PLT-37`…`PLT-39` |

**Definition of done.** Complete when every criterion is met, the `PERF` environment exists at
parity, `WP-1` and `WP-4` run against the W1 scope, and the approver has signed. Approval carries the
`PGD-A1-09` qualification.

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `05-06` §1, §2, §3, §11 | The targets and the 1.5× rule |
| Upstream | `RQ-006` | The NFR baseline and its renumbering |
| Upstream | `QA-001` §7 | The `PERF` environment definition |
| Upstream | `QA-004` §8 | Volume generation from statistics |
| Upstream | `QA-005` §12.1 | k6 2.0 runner, fixtures, result normalisation |
| Downstream | `PE-006` | §4's volumetric model, offered as input; `WP-8`'s ceiling |
| Downstream | `PE-002`, `PE-003` | §7 is their requirement input |
| Downstream | `QA-010` | Performance defects enter triage with a severity |
| Downstream | `QA-011` | Target coverage reported as part of NFR coverage |
| Downstream | `RL-003` | Go-live readiness consumes the gate performance report |
| Lateral | `../../project_content/13_Test_and_Acceptance_Content/TS-014` | The 37 scenarios adopted |

---

## 17. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./QA-001_Master_Test_Strategy.md` · `./QA-002_Test_Plans_per_Level.md` ·
`./QA-004_Test_Data_Management_and_Anonymisation_Plan.md` · `./QA-005_Test_Automation_Framework_Specification.md` ·
`./QA-010_Defect_Management_and_Quality_Gate_Standard.md` · `./QA-011_Requirements_to_Test_Coverage_Standard_and_Report.md` ·
`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md` ·
`../01_Requirements_Engineering/RQ-006_Non_Functional_Requirements_Specification.md` ·
`../02_Architecture_and_Design/AR-001_Software_Architecture_Document.md`

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` §1–§3, §11 ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` §6 ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` §4 ·
`../../project_content/13_Test_and_Acceptance_Content/TS-014_Performance_and_Load_Test_Scenario_Pack.md` ·
`../../project_content/_AUDIT/AUDIT-014_Category_13_TS_Content_Audit.md`

**External — verified 2026-08-18**
ISO/IEC/IEEE 29119-3:2021 §8 · ISO/IEC 25010:2023 · ISO/IEC 25023:2016 ·
Grafana k6 2.0, released 11 May 2026

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Platform Engineering with Quality Engineering | Initial issue. All **19 performance, 11 availability and 10 scalability** targets allocated to a verifier, including the eleven this plan explicitly cannot verify; **the estate's first volumetric derivation** — 250,000 customers/month and 5M orders/year to **~241 requests/s at 1.5× peak** — with all seven assumptions and their sensitivities stated, and a transaction mix derived from the model rather than asserted; **§4.6's finding that `NFR-004`'s 75,000 concurrent portal users is ~3,000× the load the stated business volumes support**, tested as written but reported with its derivation gap (`QAA-11b`), together with the observation that **none of `05-06` §1's six *"(was N)"* tightenings states what justified it** (`QAA-13`); eight workload profiles including a **breakpoint profile with no pass condition**; the four run-invalidating conditions; a three-level environment parity rule stating what each level may claim; **percentile-only reporting with the distribution published**; the three-part client/server/field measurement for the four targets no server-side test can prove; and diagnosis requirements that make a failure actionable without a re-run. Corrects the register's `W3` to `Now` (`QAA-10`) and offers §4's model to `PE-006` rather than letting a second one be derived (`QAA-11`) | *Pending — `GV-002`* |

---

*`QA-006` · Category 08 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
