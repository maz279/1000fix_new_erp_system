---
id: TS-014
title: Performance and Load Test Scenario Pack
project: 1000FiX ERP System v2.0
content_type: Test script
template: TPL_Test_Script.md
template_version: 1.0
version: 1.0
date: 2026-08-19
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: QA Lead with Platform Engineering
author: QA Lead with Solution Architect and DevOps
reviewers: [CTO, Solution Architect, DevOps lead, Data / BI Engineer, Operations Director, Support Lead]
approver: CTO with QA Lead
content_class: E
purpose: >
  One defined scenario, one data volume and one peak profile for every numerically measurable
  non-functional target in the specification. The non-functional requirements set specific numbers —
  two-second screens, 400-millisecond APIs, 800 concurrent internal users, 75,000 concurrent
  customer-portal users, five million service orders a year, a twenty-minute nightly route
  optimisation — and a number with no scenario behind it is unverifiable, which means it is not a
  requirement but an aspiration. Nine wave gates and the final expansion-readiness gate are all
  claimed against these figures.
traces_to: [05-06, 05-06 §1, 05-06 §2, 05-06 §3, 05-06 §11, 05-06 §12, 06-02 §4, M25, M28, M29, M30, M62, M63, P01, P02, P03, P06, P09, TS-001, TS-002, TS-013, TS-015, TS-017, TS-018, OP-006, OP-011]
priority: P1
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md §1 Performance NFR-001…005 and NFR-031…044 (19 targets); §2 Availability and Continuity NFR-006…008 and NFR-045…052 (11); §3 Scalability NFR-009, NFR-010, NFR-053…060 (10); §5 NFR-081 400 KB first load, NFR-082 battery; §11 "Performance — every NFR performance target, at 1.5× expected peak, before each wave gate"
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §4 Gate 1 G1-10 performance targets met for delivered screens; Gate 9 G9-03 full-scale load test passed at 1.5× projected peak; §2.10 KPI-085, KPI-086
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P01 250,000+ customers a month and critical paths under 400 KB first load; P03 150–250 users on 1366×768; P06 dashboard under 5 s; PS-07 3G operation
    verified: 2026-08-19
    class: P1
supersedes: none
review_due: 2027-02-19
---

# Performance and Load Test Scenario Pack

| Item | Value |
|---|---|
| Test level | **Performance** — `05-06` §11 level 8; before every wave gate |
| Role executing | Platform Engineering with QA; no business executor |
| Modules covered | All, by load profile rather than by function |
| Portals covered | `P01` `P02` `P03` `P06` `P09` carry measurable targets; the rest inherit `NFR-001`/`002` |
| Environment | **`PERF`** — production-shaped volumes (`TS-001` §4.7) |
| Test data set | `TS-002` `PERF` profile: 500,000 parties, 750,000 devices, 3,000,000 historical jobs |
| Wave | W2 · **but `G1-10` is a W1 criterion** — open item `O-01` |

> **Template conformance.** `TPL_Test_Script.md` at pack level. All six sections retained in order;
> §3 is organised by target rather than by user journey, which is the addition and is justified —
> the unit of work here is an NFR, not a task.

---

## 1. Traceability

### 1.1 The register cites a range that does not exist

The Master Index traces this file to **`05-06` NFR-001…044**. Enumeration of `05-06` finds **101
distinct NFR identifiers**, `NFR-001` to `NFR-101`, and three further defects in the identifier
space:

| Finding | Detail |
|---|---|
| **The register's range is wrong** | "NFR-001…044" implies 44 requirements. There are 101. The performance section alone is `NFR-001`…`005` **plus** `NFR-031`…`044`, which is not a contiguous range |
| **The document's own title is wrong** | `05-06` is headed *"NFR-001 … NFR-092"* and contains 101 |
| **`NFR-090`, `NFR-091`, `NFR-092` are each used twice** | §6.3 assigns them to Personal Data Protection Act obligations (consent, consent standard, transparency notice); §7 assigns the same three to maintainability (unit-test coverage ≥ 80% and 100% on financial calculations, module runbook, distributed tracing). **`NFR-090` is simultaneously a `P0` data-protection duty and the unit-test coverage gate this pack's sibling depends on** |
| **`NFR-088` and `NFN-089` appear twice** | Once in §6.2, and again as two stray rows at the end of the §6.4 residency table |

**Why this matters here more than anywhere else.** This pack's scripts are *named after* NFR
identifiers (`PERF-NFR-037-02`). An ambiguous identifier produces an ambiguous script name, and a
gate claim of the form "`NFR-090` met" would be unfalsifiable. Recorded as `O-02`, and as a finding
in the Category 13 audit; `TS-005` `O-05` records the same collision from the SIT side.

### 1.2 Target ownership — 45 measurable targets, three owners

Not every measurable target belongs to this pack. The split is stated so no target is orphaned and
none is tested twice.

| Section | Targets | This pack | `TS-015` offline | `TS-006`/`TS-011` UAT | `TS-017` security |
|---|---:|---:|---:|---:|---:|
| §1 Performance | 19 | **16** | 3 (`NFR-036`, `-037`, and the 3G component of `-035`) | — | — |
| §2 Availability & continuity | 11 | **10** | 1 (`NFR-047` 24-hour offline) | — | — |
| §3 Scalability | 10 | **10** | — | — | — |
| §5 Usability numerics | 5 | **1** (`NFR-081` 400 KB) | 1 (`NFR-082` battery) | 3 (`NFR-075`, `-076`, `-077`) | — |
| §4 Security | — | — | — | — | All of §4 |
| **Total** | **45** | **37** | **5** | **3** | — |

**37 targets in this pack.** Every one has a scenario in §3; the count is the pack's coverage
denominator and is reported as such (`TX-24`).

### 1.3 Traceability obligation per scenario

| Field | Source |
|---|---|
| Target | The `NFR-nnn` identifier and its stated number, quoted verbatim |
| Measured by | `05-06`'s own "Measured By" column — synthetic monitoring, gateway metrics, load test, field test, instrumentation |
| Data volume | The `TS-002` `PERF` profile figure the scenario runs against |
| Peak profile | The concurrency and arrival rate, and its **1.5× multiplier** |
| Gate | `06-02` §4 |
| Degradation budget | What may **not** get worse while this target is met (`PF-05`) |

---

## 2. Preconditions

### 2.1 Rules

| # | Rule |
|---|---|
| **PF-01** | **Every scenario quotes its target verbatim from `05-06`.** A paraphrased target is a second definition, and `RP-001`'s existence proves what happens when metrics acquire second definitions |
| **PF-02** | **Every target is tested at 1.5× expected peak** (`05-06` §11). A target met at expected peak and reported without the multiplier is a partial result |
| **PF-03** | **Percentiles are honoured.** `p95` means the 95th percentile of the full run, not the mean and not the best window. A mean that meets a `p95` target is a failure |
| **PF-04** | **Load runs against production-shaped data volumes**, not production-shaped concurrency alone. A 400 ms API against 2,000 parties proves nothing about 500,000 |
| **PF-05** | **Every scenario declares a degradation budget.** No target may be met by degrading another: a dashboard made fast by starving the transactional database is a failure of both |
| **PF-06** | **Saturation is found, not avoided.** Every load scenario is run past its target until something breaks, and the breaking point and its failure mode are recorded. A test that stops at the target tells you nothing about the margin |
| **PF-07** | **Failure mode matters as much as the number.** Graceful degradation with a stated message (`NFR-050`, `PS-09`) and outright failure are different outcomes at the same load |
| **PF-08** | **Bengali is in the load profile.** `NFR-035` requires search at ≤ 600 ms p95 *including Bengali text*, and ICU `bn-BD` collation is more expensive than ASCII comparison. A load profile of English-only strings under-measures the real system |
| **PF-09** | **Availability and continuity targets are tested by inducing failure** — failover, restore, circuit break, region loss — not by reading an uptime figure (`SL-27`) |
| **PF-10** | **Results are pinned to a release and an infrastructure configuration.** A result obtained on a different instance size is not a result for this release (`TX-15`, `OPS-02`) |
| **PF-11** | **A target with no scenario is reported as uncovered**, by identifier, at every gate. Silence is not coverage (`TX-24`, `RS-13`) |
| **PF-12** | Batch and scheduled-job targets are tested with the **full population**, not a sample — `NFR-044` says "all technicians", so 400, not 40 |

### 2.2 Peak modelling — the basis of every profile

`05-06` states targets but no arrival rates. These are derived, and the derivation is stated so it
can be challenged rather than inherited.

| Input | Figure | Source |
|---|---|---|
| Customers per month | 250,000+ | `04-00` `P01` |
| Service orders per year, year 5 | 5,000,000 | `NFR-053` |
| Concurrent internal users | 800+ | `NFR-003` |
| Concurrent customer-portal users | 75,000+ | `NFR-004` |
| Business hours | 09:00–22:00 BST, 13 hours | `NFR-006` |
| Technicians emitting GPS | 400 at 30-second intervals | `NFR-056` |
| Branches | 51+ today, 200 without redesign | `NFR-058` |

| Derived | Value | Derivation |
|---|---:|---|
| Service orders per working day (year 5) | ~16,400 | 5,000,000 ÷ 305 working days |
| Peak-hour share | 18% | Bangladeshi retail service pattern: morning intake surge and post-work evening booking peak — **assumption, `O-05`** |
| **Peak-hour order creations** | **~2,950** | 16,400 × 18% |
| **1.5× test rate** | **~4,430 per hour ≈ 1.23 per second sustained** | `PF-02` |
| **GPS ingestion sustained** | **800 points per minute**; 1.5× = **1,200** | 400 technicians ÷ 30 s |
| **Peak concurrent internal** | **800**; 1.5× = **1,200** | `NFR-003` |
| **Peak concurrent customer** | **75,000**; 1.5× = **112,500** | `NFR-004` |
| Seasonal multiplier | ×2 on a promotional or festival peak | `NFR-010` elastic capacity — **assumption, `O-05`** |

### 2.3 Preconditions

| # | Precondition | How to establish |
|---|---|---|
| 1 | `PERF` environment sized as production, with the configuration recorded (`PF-10`) | Infrastructure manifest — **environment unspecified**, `TS-001` `O-03` |
| 2 | `TS-002` `PERF` profile generated: 500,000 parties, 750,000 devices, 3,000,000 jobs, internally consistent and reconciling | `TS-002` `O-05` — **generation tooling does not exist** |
| 3 | Load-generation tooling and a scripted user model per portal | `06-04` — **does not exist** |
| 4 | Full observability: `NFR-092` distributed tracing with one correlation id; database, queue, cache and gateway metrics | `M28`, `M30` |
| 5 | Bengali strings in the load profile, including the `TS-002` `B-08` collation set | `PF-08` |
| 6 | Ability to induce failure: kill a node, break an integration, fail over a region, trigger a restore | `PF-09`; `NFR-051`, `NFR-052` |
| 7 | A frozen release; no concurrent deployment during a run | `PF-10` |
| 8 | Agreed degradation budgets per scenario | `PF-05` — **not agreed**, `O-04` |

---

## 3. Scripts

### 3.1 Block A — Interactive performance · 16 scenarios

| Script | Target (verbatim) | Number | Profile at 1.5× | Pri |
|---|---|---|---|:--:|
| `PERF-NFR-001-01` | ERP screen load time under normal load | ≤ 2 s p95 | 1,200 concurrent internal users, 3 m jobs | **P0** |
| `PERF-NFR-002-01` | API response time | ≤ 400 ms p95 | 1.23 order-creations/s plus read traffic | **P0** |
| `PERF-NFR-003-01` | Concurrent internal users without degradation | 800+ | **1,200 sustained**, saturation found (`PF-06`) | **P0** |
| `PERF-NFR-004-01` | Concurrent customer portal users | 75,000+ | **112,500 sustained** | **P0** |
| `PERF-NFR-005-01` | Standard report generation | ≤ 20 s | 3 m jobs, 20 concurrent report requests | P1 |
| `PERF-NFR-031-01` | Customer 360 view load | ≤ 2 s | Party with 40 devices and 200 historical jobs | **P0** |
| `PERF-NFR-032-01` | Booking availability calculation | ≤ 800 ms p95 | 51 branches, 400 technicians, full roster | **P0** |
| `PERF-NFR-033-01` | Dispatch board refresh | ≤ 1 s for 500 open jobs | 500 open jobs, live GPS, 8 dispatchers | P1 |
| `PERF-NFR-034-01` | Live map update latency | ≤ 5 s from GPS emission | 1,200 GPS points/min end-to-end traced | P1 |
| `PERF-NFR-035-01` | Search results, any entity **including Bengali text** | ≤ 600 ms p95 | 500,000 parties; **`B-08` collation set** (`PF-08`) | P1 |
| `PERF-NFR-038-01` | Executive dashboard load | ≤ 5 s | Full warehouse, 60 concurrent managers | P1 |
| `PERF-NFR-039-01` | Warehouse query, analytical | ≤ 10 s p95 | 3 m jobs, 5 years of history | P2 |
| `PERF-NFR-040-01` | Invoice generation from job closure | ≤ 5 s | 1.23 closures/s sustained | **P0** |
| `PERF-NFR-041-01` | Bulk operation, 1,000 records | ≤ 60 s **with progress feedback** | `TS-002` `D-08` corporate estate; 1,500 records at 1.5× | P1 |
| `PERF-NFR-042-01` | Payment confirmation round trip | ≤ 3 s p95 | Gateway sandbox at 1.5× peak payment rate | **P0** |
| `PERF-NFR-081-01` | Critical customer paths first load | **< 400 KB** | `P01` booking path, cold cache, 3G | **P0** |

### 3.2 Block B — Throughput, batch and events · 4 scenarios

| Script | Target | Number | Profile at 1.5× | Pri |
|---|---|---|---|:--:|
| `PERF-NFR-043-01` | Event delivery to consumer | ≤ 5 s p95 | 1.5× peak write rate across all producers | P1 |
| `PERF-NFR-044-01` | Batch job — nightly route optimisation, **all technicians** | ≤ 20 minutes | **400 technicians**, full job set (`PF-12`) | P1 |
| `PERF-NFR-055-01` | Telemetry ingestion | 50,000 points per minute | **75,000/min**, saturation found | P2 |
| `PERF-NFR-056-01` | GPS ingestion | 400 technicians at 30-second intervals sustained | **1,200 points/min for a full shift** | P1 |

### 3.3 Block C — Availability and continuity · 10 scenarios

**All ten test by inducing failure** (`PF-09`).

| Script | Target | Number | Induced failure | Pri |
|---|---|---|---|:--:|
| `PERF-NFR-006-01` | Uptime during business hours | ≥ 99.9% | Measured over a wave, plus node loss under load | **P0** |
| `PERF-NFR-045-01` | Uptime 24×7 | ≥ 99.7% | Measured over a wave | P1 |
| `PERF-NFR-007-01` | DR objectives | **RPO ≤ 15 min, RTO ≤ 2 h** | Full region failover under load | **P0** |
| `PERF-NFR-008-01` | Zero-downtime deployment | Standard for all releases | Deploy during a 1.5× load run; **assert zero failed requests** | P1 |
| `PERF-NFR-046-01` | Customer portal availability | ≥ 99.9% | Measured; plus a portal-only node loss | **P0** |
| `PERF-NFR-048-01` | Payment path availability | ≥ 99.95% **with multi-gateway failover** | Kill the primary gateway mid-transaction | **P0** |
| `PERF-NFR-049-01` | Planned maintenance window | Outside 08:00–23:00 BST; ≤ 4 h/month; **announced 72 h ahead** | Procedural verification plus the announcement path (`OP-005`) | P2 |
| `PERF-NFR-050-01` | Graceful degradation | **Every `P0` integration has a documented, tested manual fallback** | Break each `P0` integration in turn; exercise its fallback | **P0** |
| `PERF-NFR-051-01` | DR drill | Full failover twice yearly with documented results | Scheduled drill; evidence retained | **P0** |
| `PERF-NFR-052-01` | Backup verification | **Automated restore test weekly** | Induce a restore; verify integrity (`AUT-055`, `AUT-056`) | **P0** |

> **`PERF-NFR-050-01` is the largest single scenario in this pack.** "Every `P0` integration" means
> every integration in `05-03` classified `P0` — payment gateways, SMS, WhatsApp, brand endpoints,
> banking, NBR. Each needs its fallback documented **before** it can be tested, and `OP-014` manual
> fallback content is unwritten. `O-06`.

### 3.4 Block D — Scalability and headroom · 7 scenarios

| Script | Target | Number | Profile | Pri |
|---|---|---|---|:--:|
| `PERF-NFR-009-01` | Growth headroom without re-architecture | **5× users, 10× data over 5 years** | Model and validate at 2× measured, extrapolate with the method stated | **P0** |
| `PERF-NFR-010-01` | Elastic capacity for demand peaks | Automatic scaling for seasonal and promotional peaks | ×2 seasonal multiplier applied to the 1.5× profile | P1 |
| `PERF-NFR-053-01` | Service order volume | 5 million per year by year 5 | `PERF` profile at 3 m historical + 1.5× creation rate | **P0** |
| `PERF-NFR-054-01` | Device registry | 5 million assets | 750,000 loaded; scaling method validated to 5 m | P1 |
| `PERF-NFR-057-01` | Marketplace scale | 5,000 sellers, 50,000 listings | Full listing set with search and broadcast | P2 |
| `PERF-NFR-058-01` | Branch scale | **200 branches without configuration redesign** | 200 branches configured; dispatch, stock and reporting exercised | P1 |
| `PERF-NFR-060-01` | Document store | 50 TB with sub-10-second retrieval | Retrieval at volume; ingestion rate measured | P2 |

**`NFR-059` multi-entity scale (10 entities, 5 countries)** is verified in `TS-005` `SIT-K-015` and
at `G9-01`, not here — a configuration-capability question rather than a load question. Recorded so
it is not counted as uncovered (`PF-11`).

**Pack total: 37 scenarios · 18 at `P0` · 13 at `P1` · 6 at `P2`.** Coverage: **37 of 37 owned
targets, 100%** — against the ownership split in §1.2, not against all 101 NFRs.

### 3.5 Degradation budgets

`PF-05` requires each scenario to declare what may not get worse. These are the cross-cutting ones;
per-scenario budgets are set at authoring.

| While meeting… | These may not degrade beyond… |
|---|---|
| `NFR-038` executive dashboard ≤ 5 s | `NFR-001` screens ≤ 2 s and `NFR-002` APIs ≤ 400 ms — the warehouse may not starve the transactional path |
| `NFR-044` nightly batch ≤ 20 min | Nothing; it runs at 05:00 outside business hours — **but it must finish before the 09:00 window opens** |
| `NFR-041` bulk 1,000 records ≤ 60 s | Other users' `NFR-001` — a bulk job may not lock interactive work |
| `NFR-055`/`056` ingestion | `NFR-033` dispatch board and `NFR-034` map latency |
| `NFR-004` 75,000 customer users | `NFR-003` 800 internal users — **a customer peak may not slow the branch counter** |

### 3.6 Negative and edge cases

| # | Condition | Expected behaviour |
|---|---|---|
| N-01 | Load applied past the target until saturation | Breaking point and failure mode recorded (`PF-06`, `PF-07`) |
| N-02 | Target met at the mean but not at `p95` | **Failure** (`PF-03`) |
| N-03 | Target met by degrading another | **Failure of both** (`PF-05`) |
| N-04 | Cache warm from a previous run | Cold-cache result required for first-load targets; both reported |
| N-05 | Bengali search slower than English | Reported separately; `NFR-035` covers both and the target is not language-conditional (`PF-08`) |
| N-06 | Deployment during a load run causes failed requests | `NFR-008` zero-downtime failure |
| N-07 | Failover succeeds but exceeds RTO | `NFR-007` failure even though the system recovered |
| N-08 | Restore test succeeds on a partial dataset | Not a pass; `NFR-052` is a full-integrity restore |
| N-09 | Result obtained on a larger instance than production | Void (`PF-10`) |
| N-10 | A target has no scenario | Reported as uncovered by identifier (`PF-11`) |

---

## 4. Exit Criteria

| Criterion | Threshold |
|---|---|
| Owned targets with a scenario | **37 of 37** (`PF-11`) |
| `P0` targets met **at 1.5× peak** | **100%** (`PF-02`) |
| `P1` targets met at 1.5× peak | ≥ 95% |
| Percentile discipline | 100%; no mean reported against a `p95` target (`PF-03`) |
| Production-shaped data volumes used | 100% (`PF-04`) |
| Degradation budgets declared and respected | 100% (`PF-05`) |
| Saturation point recorded per load scenario | 100% (`PF-06`) |
| Availability targets tested by induced failure | **10 of 10** (`PF-09`) |
| `P0` integrations with a tested manual fallback | **100%** (`NFR-050`) |
| Bengali in the load profile | Yes, with results reported separately (`PF-08`) |
| Results pinned to release and infrastructure configuration | 100% (`PF-10`) |
| **`G1-10`** | Performance targets met for delivered screens |
| **`G9-03`** | **Full-scale load test passed at 1.5× projected peak** |
| Open Critical defects | Zero |

---

## 5. Defects Raised

| Defect ID | Script | Severity (`TS-018`) | Status |
|---|---|---|---|
| *(populated at execution)* | | | |

**Severity here is derived from the target's own priority in `05-06`, not from the size of the miss.**
A `P0` target missed by 10% is Critical; a `P2` target missed by 200% is Medium. The reason is
recorded in `TS-018` §4: `05-06` already ranked these requirements against business consequence, and
re-ranking them by measurement magnitude would substitute the tester's judgement for the
architect's.

**One automatic escalation:** any scenario in which a target is met **by degrading another** is
**Critical** to the CTO, regardless of either target's priority. It indicates a capacity or
architecture problem that the individual numbers conceal.

---

## 6. Sign-off

| Event | Signatory | Record |
|---|---|---|
| Per-gate performance pass | QA Lead with DevOps lead | Gate evidence pack, with the infrastructure configuration recorded |
| DR drill (`PERF-NFR-051-01`) | CTO | Drill report, twice yearly |
| Backup restore verification (`PERF-NFR-052-01`) | DevOps lead | Weekly automated record |
| `G9-03` full-scale load test | **CTO with Programme Manager** | Programme closure pack |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`G1-10` requires performance targets met for delivered screens at Month 4, in W1, and this pack is registered at W2.** `05-06` §11 also requires performance testing *before each wave gate*, which includes `G1`. The seventh instance of the sequencing shape in this category | Programme Content Lead with QA Lead | **W1 — register correction** |
| **O-02** | **The NFR identifier space has four defects** (§1.1): the register cites a range of 44 against 101 identifiers; `05-06`'s own title says 92; `NFR-090`/`091`/`092` are each used twice for unrelated requirements; `NFR-088`/`089` are duplicated in §6.4. **This pack names its scripts after NFR identifiers, so the ambiguity is structural rather than cosmetic** | Enterprise Architecture with CTO | **W1 — before the first script is named** |
| **O-03** | **The `PERF` environment and its data do not exist.** `TS-001` `O-03` (no environment specification) and `TS-002` `O-05` (no generation tooling for 500,000 parties and 3 m jobs, internally consistent and reconciling). **This pack is entirely unexecutable until both are resolved**, and it gates `G1-10` and `G9-03` | CTO with Platform Engineering | **W2** |
| **O-04** | **No degradation budgets are agreed** (`PF-05`, precondition 8). §3.5 proposes five cross-cutting ones; they are this pack's proposal, not an architectural decision, and the customer-peak-versus-branch-counter trade-off in particular is a business decision about who gets the capacity | Solution Architect with Operations Director | **W2 — before the first run** |
| **O-05** | **Two figures in the peak model are assumptions, not measurements**: the 18% peak-hour share and the ×2 seasonal multiplier (§2.2). `06-02` §6 requires every baseline measured and signed off before the wave begins. **Every number in this pack scales off those two assumptions**, so a wrong peak-hour share invalidates 37 scenarios at once | Operations Director with BI Lead | **W2 — measure from the current business before W2 closes** |
| **O-06** | **`NFR-050` requires every `P0` integration to have a documented, tested manual fallback, and the documentation does not exist.** `OP-014` manual fallback content is unwritten (Category 17 unstarted) and `05-03` classifies the integrations but does not describe fallbacks. **`PERF-NFR-050-01` cannot be written, let alone run** | Support Lead with Solution Architect | **W2** |
| **O-07** | **`NFR-090` §7's unit-test coverage gate — ≥ 80% of custom code and 100% of financial and tax calculations — has no owner in Category 13 and no owner anywhere else.** `TS-001` §4.1 correctly places unit testing with engineering, but *nothing verifies the coverage figure at a gate*, and `G1`…`G9` never mention it. It is the only `05-06` §11 coverage standard with no gate criterion | CTO with QA Lead | **W1** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Test_Script.md` at pack level; the by-target organisation justified
- [x] **The register's `NFR-001…044` citation checked against `05-06` and found wrong; four identifier defects reported**
- [x] **Target ownership split across four packs so all 45 measurable targets have exactly one owner**
- [x] Twelve rules stated, including saturation-finding, degradation budgets and Bengali in the load profile
- [x] **Peak model derived and its two assumptions flagged rather than presented as fact**
- [x] 37 scenarios enumerated, each quoting its target verbatim with a 1.5× profile
- [x] All ten availability targets tested by inducing failure rather than by reading an uptime figure
- [x] `NFR-059` explicitly delegated to `TS-005` and `G9-01` so it is not counted as uncovered
- [x] Five cross-cutting degradation budgets proposed, including the customer-versus-counter trade-off
- [x] Ten edge cases stated, including mean-versus-`p95` and oversized-instance results
- [x] Severity derived from the target's own `05-06` priority, with the reasoning recorded
- [x] Automatic Critical escalation where one target is met by degrading another
- [x] All internal links resolve
- [x] Seven open items recorded, including an unowned unit-test coverage gate
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 37 per-scenario profiles and harness scripts — outstanding**
- [ ] **`O-02` NFR identifier collisions — outstanding; blocks script naming**
- [ ] **`O-03` `PERF` environment and data absent — outstanding; the pack is unexecutable**
- [ ] **`O-05` peak-hour share and seasonal multiplier unmeasured — outstanding; every scenario scales off them**
- [ ] **`O-06` `NFR-050` fallbacks undocumented — outstanding; the largest scenario cannot be written**
- [ ] Named approvers recorded — **pending CTO and QA Lead**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
