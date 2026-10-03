---
id: TS-005
title: SIT Scenario Library — Module Categories H to K
project: 1000FiX ERP System v2.0
content_type: Test script
template: TPL_Test_Script.md
template_version: 1.0
version: 1.0
date: 2026-08-19
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: QA Lead
author: QA Lead with test analysts, HR, Quality, BI and Platform business owners
reviewers: [Solution Architect, CTO delegate, HR Manager, Quality Manager, BI Lead, Security Lead, Knowledge Manager]
approver: QA Lead with CTO delegate
content_class: E
purpose: >
  The system integration scenarios that cross the boundaries between the twenty-two modules of
  categories H to K — people and workforce, governance and knowledge, data and analytics, platform
  and technology. These are the modules whose defects do not present as their own failures: an
  identity provisioned with the wrong role surfaces as a dispatcher who cannot dispatch; a stale
  master data value surfaces as a rejected warranty claim; an undelivered event surfaces as a
  dashboard that was quietly wrong for a week. Every one of those is diagnosed in the wrong module
  first, and the time lost is the cost of not testing the platform boundaries directly.
traces_to: [M21, M22, M23, M24, M25, M26, M28, M29, M30, M55, M56, M57, M58, M59, M60, M61, M62, M63, M64, M65, M66, M67, 05-04, 05-05, 05-06 §4, 05-06 §6, 05-06 §11, 05-06 §12, 06-02 §4, MD-009, MD-010, MD-011, MD-042, MD-043, TS-001, TS-002, TS-003, TS-004, TS-010, TS-017, TS-018, RP-001]
priority: P1
wave: W4
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/ — category folders H (7 modules), I (4), J (4), K (7); M66 and M67 exist and are complete, contrary to the README statement corrected as audit finding AF-03
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md §9 Access Lifecycle (provision on employee.joined, deprovision within 1 hour on employee.left, quarterly review, zero orphaned accounts beyond 24 hours measured weekly); §6 SOD-01…SOD-12
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md §10 BRU-HRM-*/BRU-LMS-*/BRU-QMS-*, §11 BRU-SEC-*/BRU-DMS-*/BRU-ADM-*/BRU-AIM-*, §12.4 AUT-041…AUT-052, §12.5 AUT-053…AUT-060
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md §12 AS-01…AS-15 architecture standards restated as testable rules, and §6.3 NFR-090…NFR-099 PDPA 2026 obligations
    verified: 2026-08-19
    class: P1
supersedes: none
review_due: 2027-02-19
---

# SIT Scenario Library — Module Categories H to K

| Item | Value |
|---|---|
| Test level | **SIT** — method defined in `TS-003` §2.1 and §3.1 |
| Role executing | Test analysts, with `R02`, `R30`, `R31`, `R32`, `R33` as scenario witnesses |
| Modules covered | **22** — `H` (`M21`, `M22`, `M55`–`M59`) · `I` (`M23`, `M24`, `M60`, `M61`) · `J` (`M25`, `M26`, `M62`, `M63`) · `K` (`M28`–`M30`, `M64`–`M67`) |
| Portals covered | `P03` (System Console), `P06`, `P11`; all portals as identity consumers |
| Environment | `SIT` (`TS-001` §4.7) |
| Test data set | `TS-002` — personas 2, 3, 10; employee set, `B-08` collation set |
| Wave | W4 · **but `M29` identity and `M64` master data are W1 foundations** — open item `O-01` |

> **Template conformance.** As `TS-003`: `TPL_Test_Script.md` applied at library level, all six
> sections retained in order with library-level interpretation.

> **Method by reference.** `SL-01`…`SL-16` and the eight-phase step pattern are in
> [`TS-003_SIT_Scenario_Library_Categories_A_to_D.md`](TS-003_SIT_Scenario_Library_Categories_A_to_D.md)
> §2.1 and §3.1. `SL-17`…`SL-22` in [`TS-004`](TS-004_SIT_Scenario_Library_Categories_E_to_G.md) §2.1
> apply to the payroll and cost scenarios here. This file adds `SL-23`…`SL-27` (§2.1).

> **Boundary against `TS-017`.** This library proves that platform boundaries produce the **right
> business outcome**; `TS-017` proves that access **cannot be obtained where it must not be**. The
> same `05-04` matrix is the source for both and neither restates the other: here, `R07` gets the
> dispatch console the position profile grants; there, `R07` is proved unable to reach `P05`.
> Recorded once, so the 379 denied cells are counted in one place only (`CP-01`).

---

## 1. Traceability

### 1.1 The boundary map

Twenty-two modules, **eighteen boundaries that carry an identity, control, data-quality or
observability obligation**.

| # | Boundary | Obligation crossing it | Scenarios |
|---:|---|---|---|
| BD-35 | `M21` → `M29` | Joiner, mover and leaver become identity and access, on time | `SIT-H-001`…`004` |
| BD-36 | `M22` → `M02`/`M09` | Certification currency gates dispatch and claim eligibility | `SIT-H-005`…`007` |
| BD-37 | `M55` → `M56` | Attendance verified and locked before payroll can calculate | `SIT-H-008`, `009` |
| BD-38 | `M56` → `M19`/`M50` | Payroll posts, BEFTN file generated, payslips distributed | `SIT-H-010`…`012` |
| BD-39 | `M57` → `M56`/`M02` | Incentive derived from measured performance thresholds | `SIT-H-013` |
| BD-40 | `M59` → `M23`/`M02` | Safety incident becomes a non-conformance and affects assignment | `SIT-H-014` |
| BD-41 | `M23` → `M60` | Non-conformance, CAPA and control effectiveness | `SIT-I-001`…`003` |
| BD-42 | `M24` → all | Document retention, legal hold, signature immutability | `SIT-I-004`…`007` |
| BD-43 | `M60` → `M29`/`M42` | Risk, control testing, processor obligations | `SIT-I-008`, `009` |
| BD-44 | `M61` → `M02`/`M22` | Knowledge reaches the technician, offline, and staleness is visible | `SIT-I-010`…`012` |
| BD-45 | `M62` → `M25` | Warehouse load, data-quality gate, certified dataset | `SIT-J-001`…`004` |
| BD-46 | `M25` → `P06` | Metric definition, row-level security, drill integrity | `SIT-J-005`…`007` |
| BD-47 | `M26` → `M02`/`M11` | Model output constrained by guard rails and human confirmation | `SIT-J-008`, `009` |
| BD-48 | `M63` → all | Orchestrated workflow, escalation, and failure visibility | `SIT-J-010` |
| BD-49 | `M28` → all | Event delivery, idempotency, dead letter, circuit breaker, fallback | `SIT-K-001`…`005` |
| BD-50 | `M29` → all portals | One identity, one session policy, one audit trail | `SIT-K-006`…`010` |
| BD-51 | `M64` → all | Golden record, survivorship, change control on master data | `SIT-K-011`…`013` |
| BD-52 | `M30`/`M65`/`M66`/`M67` → all | Configuration, country pack, ITSM linkage, project delivery | `SIT-K-014`…`016` |

### 1.2 Traceability obligation

As `TS-003` §1.3, plus:

| Field | Source of truth |
|---|---|
| Architecture standard exercised | `05-06` §12 `AS-01`…`AS-15` — these are the only requirements in the repository already written as testable rules, and this library is where most of them are proven |
| Statutory obligation exercised | `05-06` §6.3 `NFR-090`…`NFR-099` PDPA 2026 · §6.2 `NFR-083` Labour Act |

---

## 2. Preconditions

### 2.1 Additional rules for platform boundaries

| # | Rule |
|---|---|
| **SL-23** | An identity or permission outcome is verified **by acting as the user**, never by reading a configuration screen. A role that looks correct and cannot open its console is the defect this rule exists to catch |
| **SL-24** | A **time-bounded** obligation is tested against the clock, not against intent: leaver access revoked within **one hour** (`BRU-SEC-06`, `05-04` §9), zero orphaned accounts beyond **24 hours** (`KPI-090`), rectification notified within **30 days** (`NFR-093`) |
| **SL-25** | Every architecture standard in `05-06` §12 that this library touches is **asserted explicitly** and its verification method recorded, because `AS-01`…`AS-15` already state how each is verified |
| **SL-26** | A data or analytics outcome is verified **against an independently computed figure**, never against another report. Two reports agreeing proves they share a defect |
| **SL-27** | An observability obligation is tested by **inducing the failure**: break the integration, fill the dead-letter queue, expire the certificate. An alert that has never fired is an untested alert (`OPS-03`) |

### 2.2 Environment and data preconditions

| # | Precondition | How to establish |
|---|---|---|
| 1 | `SIT` at a single declared release across all 22 modules; `TS-003` preconditions 1–4 met | Release manifest |
| 2 | `MD-008`/`MD-009` position and role master loaded, so a joiner can inherit a role from a position profile (`AUT-047`) | Load log |
| 3 | `MD-010` competency taxonomy and `MD-011` certification register loaded, with **one certification expiring inside the test window** | `TS-002` persona 2 |
| 4 | `MD-042` shift and roster patterns, `MD-043` payroll elements, `MD-041` holiday calendar loaded | Load log |
| 5 | Two employees in `TS-002` with a full attendance period, one with an unapproved-overtime case | `TS-002` employee set |
| 6 | Event platform observable: outbox, dead-letter queue, correlation ids, and a way to **stop and restart a consumer** | `NFR-092`; `SL-27` |
| 7 | Warehouse (`M62`) loading from `SIT`, with a data-quality test configured to fail on demand | `AUT-059` |
| 8 | Retention schedule configured with one document inside and one outside its period, and one under legal hold | `BRU-DMS-01`, `BRU-DMS-02` |
| 9 | A certificate or credential with an expiry inside the test window | `AUT-060` |
| 10 | Role accounts for `R02`, `R30`–`R33`, plus one account per role under test for `SL-23` | **Does not exist** — `TS-002` `O-04` |
| 11 | **`RP-001` KPI dictionary** for `SIT-J-005`…`007` | **Unwritten** — `O-04` |

---

## 3. Scripts

### 3.1 Category H — People & Workforce · 14 scenarios

`M21` `M22` `M55` `M56` `M57` `M58` `M59`

| Script | Scenario | Boundary | Rules and automations | Pri |
|---|---|---|---|:--:|
| `SIT-H-001` | Employee joins: identity created, role assigned **from the position profile**, portal access granted, onboarding and mandatory training assigned — verified by logging in as them (`SL-23`) | BD-35 | `AUT-047`; `05-04` §9 | **P0** |
| `SIT-H-002` | Employee transfers: old permissions revoked and new granted on the effective date, **with no accumulation** | BD-35 | `05-04` §9 Modify | **P0** |
| `SIT-H-003` | **Employee leaves: all access revoked within one hour**, devices deregistered, delegated authority reassigned | BD-35 | `BRU-SEC-06`(H) `AUT-048` `SL-24` | **P0** |
| `SIT-H-004` | Quarterly access review: unconfirmed access is revoked at the deadline, and **zero accounts remain orphaned beyond 24 hours** | BD-35 | `AUT-052` `KPI-090` `SL-24` | P1 |
| `SIT-H-005` | **Technician cannot be assigned brand warranty work once their certification for that brand has expired**; expiry removes them from that pool automatically | BD-36 | `BRU-HRM-01`(H) `BRU-SRM-09`(H) `AUT-042` | **P0** |
| `SIT-H-006` | Certification expiry notices fire at −90/−60/−30/−15 days to technician, manager and HR, and re-certification is scheduled | BD-36 | `AUT-041` | P1 |
| `SIT-H-007` | **Overdue mandatory training restricts the affected work types**, and the restriction lifts on completion | BD-36 | `BRU-LMS-01`(H) | P1 |
| `SIT-H-008` | **Payroll cannot be finalised until attendance for the period is verified and locked** | BD-37 | `BRU-HRM-05`(H) `AUT-045` | **P0** |
| `SIT-H-009` | **Unapproved overtime does not count for payroll**; approved overtime does, and the approval is traceable | BD-37 | `BRU-HRM-02`(H) | **P0** |
| `SIT-H-010` | **Payroll requires two approvals — HR Manager and CFO** — and the processor cannot approve | BD-38 | `BRU-HRM-06`(H) `SOD-03` | **P0** |
| `SIT-H-011` | Approved payroll generates the BEFTN file, distributes payslips and posts to the ledger with the expected journal | BD-38 | `AUT-046`; `SL-17` | **P0** |
| `SIT-H-012` | **An employee's payroll record is visible to them and to HR/finance, never to peers or to a line manager below HR Manager** | BD-38 | `BRU-HRM-07`(H); `05-04` §5 | **P0** |
| `SIT-H-013` | Incentive calculates only after the minimum monthly job threshold is met, from `M02`-measured jobs, and the technician can see the derivation | BD-39 | `BRU-HRM-03`(C) `SL-26` | P1 |
| `SIT-H-014` | Safety incident reported from `P02` raises a non-conformance, and where the finding requires it **removes the technician or the site from assignment** | BD-40 | `BRU-QMS-02`(H) `AUT-049`; `NFR-083` | P1 |

### 3.2 Category I — Governance, Risk, Quality & Knowledge · 12 scenarios

`M23` `M24` `M60` `M61`

| Script | Scenario | Boundary | Rules and automations | Pri |
|---|---|---|---|:--:|
| `SIT-I-001` | **Non-conformance cannot be closed without a root cause and a CAPA** | BD-41 | `BRU-QMS-02`(H) | **P0** |
| `SIT-I-002` | **CAPA cannot be closed without effectiveness verification after the defined interval**; failed verification reopens it and escalates severity | BD-41 | `BRU-QMS-03`(H) `AUT-050` `AUT-QMS-10` | **P0** |
| `SIT-I-003` | Control test failure in `M60` raises a finding that ties to the `M23` non-conformance it came from, without creating a duplicate record | BD-41, BD-43 | `BRU-GRC-*` (`M60` §9) | P1 |
| `SIT-I-004` | **A document cannot be deleted before its retention period expires** | BD-42 | `BRU-DMS-01`(H) | **P0** |
| `SIT-I-005` | **A document under legal hold cannot be disposed of regardless of retention**; end-of-retention presents for review instead | BD-42 | `BRU-DMS-02`(H) `AUT-051` | **P0** |
| `SIT-I-006` | **A signed document cannot be modified**; a change produces a new version and a new signature | BD-42 | `BRU-DMS-03`(H) | **P0** |
| `SIT-I-007` | Soft deletion only; a hard deletion requires the approved, logged procedure | BD-42 | `DI-08`; `AS-*` | P1 |
| `SIT-I-008` | Processor obligations flow to a vendor by contract, and a vendor without them cannot be activated for personal-data processing | BD-43 | `NFR-098`; `BRU-SCM-02`(H) | P1 |
| `SIT-I-009` | Breach assessment path: a qualifying breach produces the **Authority notification record** within the prescribed timeframe | BD-43 | `NFR-094`; `AUT-058` | **P0** |
| `SIT-I-010` | Knowledge article published in `M61` reaches the technician's `P02` offline set, and **its staleness is visible offline** | BD-44 | `FR-KMS-017`/`-018`; `M61` T-01, T-03 | P1 |
| `SIT-I-011` | Technician's three-minute capture in `P02` becomes a reviewable knowledge candidate, attributed, without leaving the job | BD-44 | `FR-KMS-024` | P2 |
| `SIT-I-012` | A withdrawn article disappears from the offline set on next sync and **cannot be reached from a cached link** | BD-44 | `M61` T-03; `CP-10` | P1 |

### 3.3 Category J — Data, Analytics & Intelligence · 10 scenarios

`M25` `M26` `M62` `M63`

| Script | Scenario | Boundary | Rules and automations | Pri |
|---|---|---|---|:--:|
| `SIT-J-001` | Warehouse load completes; **data-quality tests run on every load** and pass | BD-45 | `DI-06`; `KPI-093` | **P0** |
| `SIT-J-002` | **A failing data-quality test blocks the dependent dashboard refresh** and alerts the data owner; the dashboard shows last-known-good **with a staleness warning**, never stale data presented as current | BD-45 | `AUT-059`; `DI-06` | **P0** |
| `SIT-J-003` | A certified dataset's freshness guarantee is breached and **every view depending on it is flagged** | BD-45 | `AUT-P06-04` (`P06`) | P1 |
| `SIT-J-004` | A `MD` code change propagates to the warehouse and historical rows retain the code in force at the time | BD-45, BD-51 | `CG-006` §5; `SL-26` | P1 |
| `SIT-J-005` | A KPI on the executive dashboard is **independently recomputed from source and matches to the stated precision** | BD-46 | `RP-001`; `SL-26` | **P0** |
| `SIT-J-006` | **Row-level security derived from `M29` is applied to every dataset**; a branch manager's dashboard shows their branch only, and column-level restrictions are enforced by exclusion from the dataset, not by hiding in a view | BD-46 | `PRU-P06-03`(H) `PRU-P06-04`(H); `05-04` §5 | **P0** |
| `SIT-J-007` | Drill from a group figure to a single job returns the records that sum to it — **no more, no fewer** | BD-46 | `SL-26` | P1 |
| `SIT-J-008` | **A model recommendation with material customer or financial impact requires human confirmation**, and the confirmation is recorded | BD-47 | `BRU-AIM-01`(H) | **P0** |
| `SIT-J-009` | **No model output crosses a business guard rail** — price floor or ceiling, certification requirement, safety rule; and recovered `M06` data is never used as training data | BD-47 | `BRU-AIM-02`(H) `BRU-AIM-03`(H) | **P0** |
| `SIT-J-010` | An orchestrated multi-module workflow escalates on timeout and **fails visibly**; a scheduled job reports success, failure and duration | BD-48 | `OPS-05`; `M63` | P1 |

### 3.4 Category K — Platform & Technology · 16 scenarios

`M28` `M29` `M30` `M64` `M65` `M66` `M67`

| Script | Scenario | Boundary | Rules and automations | Pri |
|---|---|---|---|:--:|
| `SIT-K-001` | **Every write path emits its domain event through the outbox**; the event arrives at every registered consumer within 5 s p95 | BD-49 | `AS-08`; `NFR-043` `SL-25` | **P0** |
| `SIT-K-002` | Consumer stopped, events accumulate, consumer restarted: **all events delivered, none lost, none applied twice** | BD-49 | `DI-05`; `SL-11` `SL-27` | **P0** |
| `SIT-K-003` | **An event in the dead-letter queue for more than an hour alerts and creates a triage task** | BD-49 | `AUT-054` `SL-27` | P1 |
| `SIT-K-004` | Integration error rate above threshold **opens the circuit breaker and activates the documented fallback**; the fallback is exercised end to end | BD-49 | `AUT-053`; `NFR-050` `SL-12` | **P0** |
| `SIT-K-005` | An event carrying a field the consumer does not recognise is consumed without failure and the unknown field is logged | BD-49 | `TS-003` `E-03` | P1 |
| `SIT-K-006` | **Single sign-on across all delivered portals**; one identity, one session policy, one audit trail; no portal holds its own credential store | BD-50 | `PS-01`; `NFR-069` `SL-23` | **P0** |
| `SIT-K-007` | **MFA is enforced at every login for admin, finance and HR roles**, and cannot be bypassed by a direct URL | BD-50 | `BRU-SEC-01`(H) `NFR-012` | **P0** |
| `SIT-K-008` | **Step-up authentication is required for a payout, a payroll finalisation, a data-case access and a bulk export** | BD-50 | `BRU-SEC-02`(H) `NFR-065` | **P0** |
| `SIT-K-009` | **Incompatible duty combinations cannot be assigned**; an exception is time-boxed, logged and appears on the standing exception report | BD-50 | `BRU-SEC-07`(H) `NFR-064`; `05-04` §6 | **P0** |
| `SIT-K-010` | Session idle timeout applies at 30 minutes external and 60 internal with a 12-hour absolute maximum; **the policy comes from `M29`, not from the portal** | BD-50 | `NFR-069`; `PS-12` | P1 |
| `SIT-K-011` | **Master data change above the defined significance requires approval before taking effect**, and the pre-approval value remains in force until then | BD-51 | `BRU-ADM-01`(H) | **P0** |
| `SIT-K-012` | Golden record and survivorship: two source records merge under `M64` rules and **every dependent module resolves to the surviving record** | BD-51 | `M64`; `DM-011` | **P0** |
| `SIT-K-013` | Every custom model carries entity and operating-unit fields, and chatter and activity mixins | BD-51 | `AS-02` `AS-03` `SL-25` | P1 |
| `SIT-K-014` | **A production configuration change is traceable to an approved change record**, and an untraceable change is blocked or flagged | BD-52 | `BRU-ADM-02`(H) `OPS-02` | **P0** |
| `SIT-K-015` | A second-entity country pack is applied by **configuration only**, and entity-scoped data does not leak across entities | BD-52 | `NFR-059`; `T1` isolation; `G9-01` | P1 |
| `SIT-K-016` | An `M30` alert, an `M28` integration failure and an `M29` security event each create an `M66` incident automatically, **de-duplicated against open incidents** | BD-52, BD-49 | `AUT-ITS-02`; `TS-001` §4.10 boundary | P1 |

**Library total: 52 scenarios · 31 at `P0` · 18 at `P1` · 3 at `P2`.**

### 3.5 Negative and edge cases

`TS-003` §3.6 applies. These are specific to identity, data and platform:

| # | Condition | Expected system behaviour |
|---|---|---|
| G-01 | Leaver event arrives while the user holds an active session | Session terminated, not merely prevented at next login (`BRU-SEC-06`) |
| G-02 | Two role assignments granted that are individually valid and jointly an SoD breach | Second assignment refused at assignment time, not detected in a later report (`NFR-064`) |
| G-03 | A permission is changed while the user is mid-transaction | New scope applies to the next action; the in-flight action completes or fails atomically, never partially |
| G-04 | Master data value retired while referenced by an in-flight record | In-flight record retains it; new records cannot select it (`TS-003` `E-06`) |
| G-05 | Warehouse load runs while a source system is mid-transaction | Load is transactionally consistent or is rejected; **a partially loaded fact table is a Critical defect** |
| G-06 | Dashboard queried during a failed refresh | Last-known-good with a staleness warning (`AUT-059`); never a blank chart implying zero |
| G-07 | Model called with an input outside its training distribution | Falls back to rules, logs the condition, does not silently extrapolate (`AUT-057`) |
| G-08 | Certificate expires unnoticed | Alert at −30 days, escalation at −7 (`AUT-060`, `SL-27`) |
| G-09 | Backup completes with a corrupt artefact | Integrity verification fails and escalates immediately (`AUT-055`) |
| G-10 | A residency-classified field is written to a non-resident store | **Refused at write time, not corrected later** (`NFR-086a`) |
| G-11 | Personal data appears in an application log | Detected and treated as a defect (`OPS-04`) |
| G-12 | A module attempts to read another module's tables directly | Caught by static analysis in CI and by architecture review (`AS-01`, `SL-25`) |

### 3.6 Bilingual check

English-only library (`CG-010` §3.2). It asserts bilingual behaviour where an employee is the reader:

| Element | EN | BN | Truncation |
|---|:--:|:--:|:--:|
| Payslip rendering, `SIT-H-011` — bilingual per `DT-041` and `BN-015` | ● | ● | ● |
| Assigned-training and certification-expiry notices, `SIT-H-006`/`007` | ● | ● | ● |
| Bengali collation in a sorted employee or knowledge list, `SIT-I-010` — against the `TS-002` `B-08` answer key | ● | ● | — |

---

## 4. Exit Criteria

`TS-003` §4 applies. Additional and stricter:

| Criterion | Threshold |
|---|---|
| Identity and permission outcomes verified **by acting as the user** | 100% (`SL-23`) |
| Time-bounded obligations measured against the clock | 100% (`SL-24`) — leaver revocation inside one hour, orphaned accounts zero beyond 24 hours |
| Architecture standards touched and asserted with their verification method | 100% of `AS-*` in scope (`SL-25`) |
| Analytics outcomes independently recomputed | 100% (`SL-26`); **agreement between two reports is not evidence** |
| Observability obligations tested by inducing the failure | 100% (`SL-27`) |
| SoD assignment blocks | 12 of 12 (`SOD-01`…`SOD-12`) |
| Payroll scenarios `SIT-H-008`…`012` | **100%, no tolerance** — `G5-01` requires a first payroll run with zero errors |
| PDPA scenarios `SIT-I-008`, `-009`, `SIT-J-009`, `G-10`, `G-11` | **100%, no tolerance** — penalty exposure to `BDT 50 lakh`, risk `RSK-032` |
| Open Critical defects | Zero |

---

## 5. Defects Raised

| Defect ID | Script | Severity (`TS-018`) | Status |
|---|---|---|---|
| *(populated at execution)* | | | |

**Three automatic escalations in this library:**

| Trigger | Escalation |
|---|---|
| Any defect where a user obtains access they should not hold, or retains it after a leaver event | **Critical** to CTO and Security Lead — `NFR-011`…`-015` are `P0` and the exposure is a breach, not a bug |
| Any defect where residency-classified data is written outside the Bangladesh-resident store | **Critical** to Chief Data Officer — `NFR-086`, `NFR-099`, statutory |
| Any defect where a payroll figure is wrong | **Critical** to HR Manager and CFO — `KPI-060` targets under 0.5% corrections per run and a wrong payslip is an employment-law matter (`NFR-083`) |

---

## 6. Sign-off

| Role | Name | Date | Signature |
|---|---|---|---|
| QA Lead | | | |
| Solution Architect | | | |
| CTO delegate — categories J, K | | | |
| HR Manager (`R30`) — category H | | | |
| Quality Manager (`R32`) — category I | | | |
| BI Lead — category J | | | |
| Security Lead — identity and PDPA scenarios | | | |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This library is registered at W4 and its two most consumed modules are W1 foundations.** `06-02` `G1-06` requires single sign-on and the role framework operating for all delivered roles at **Month 4**, and `G1-07` requires a complete audit trail; `M64` master data governs every `MD` load from W0. The `SIT-K-006`…`010` and `SIT-K-011`…`013` scenarios are consumed three waves before the file exists. **This is the fourth consecutive category in which the register is sequenced by subject maturity rather than consumer need** | Programme Content Lead with QA Lead | **W1 — register correction** |
| **O-02** | **`M66` and `M67` were recorded as unwritten in `README.md` and both exist and are complete** (audit finding `AF-03`, marked Fixed). `SIT-K-016` and the ITSM boundary were derived from the files, not from the README. **Any coverage statement built from the README's module status will under-count this library** | Enterprise Architecture | W4 |
| **O-03** | **The `M61` offline knowledge mechanism arrives at W6** (`FR-KMS-017`/`-018`, T-01, T-03) while `SIT-I-010` and `SIT-I-012` are W4 scenarios that depend on it. This is the same `M61` sequencing exposure recorded in `AUDIT-008` KB-05, `AUDIT-010` HC-05 and `HC-004` `O-01`; **it should be folded into `AUDIT-008` R-03, not resolved separately** | Quality Manager with CTO | Next Steering Committee |
| **O-04** | **`RP-001` KPI Dictionary is unwritten** (Category 14 unstarted), so `SIT-J-005` and `SIT-J-007` have no definition to recompute against. `SL-26` requires an independent computation, and "independent of what?" has no answer. `HC-008` `O-01` and `TR-011` `O-01` record the same dependency | BI Lead | **W1 — precedes this library and two others** |
| **O-05** | **`NFR-090`, `NFR-091` and `NFR-092` are each used twice in `05-06`** — once in §6.3 as PDPA obligations (consent, consent standard, transparency notice) and once in §7 as maintainability requirements (unit-test coverage, module runbook, distributed tracing). `SIT-I-008`/`-009` and `SL-25` both cite them and **the citation is ambiguous**. The document's own title also says "NFR-001 … NFR-092" while 101 identifiers exist, and `NFR-088`/`NFR-089` appear a second time inside the §6.4 residency table | Enterprise Architecture with CTO | **W1 — before any pack cites an NFR by number** |
| **O-06** | **No specification defines the nightly cross-system reconciliation (`DI-07`) or the standing SoD exception report** (`05-04` §6). `SIT-K-009` asserts the exception appears on a report that no document defines | Solution Architect with CFO | W4 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Test_Script.md` at library level; interpretation declared
- [x] **Method taken by reference from `TS-003` and `TS-004` rather than restated (`CP-01`)**
- [x] **The boundary against `TS-017` stated explicitly, so the 379 denied portal cells are counted in one place only**
- [x] Five additional rules stated, covering act-as-the-user verification, clock-measured obligations, architecture standards, independent recomputation and induced failure
- [x] Eighteen identity, control, data-quality and observability boundaries derived and mapped
- [x] 52 scenarios enumerated with boundary, rule class, automation and priority
- [x] Twelve platform edge cases stated, including partial warehouse loads and residency write violations
- [x] Three automatic Critical escalations defined — access, residency, payroll
- [x] `AS-01`…`AS-15` treated as the testable rules they already are, rather than restated
- [x] All internal links resolve
- [x] Six open items recorded, including the `NFR-090`/`091`/`092` collision found while citing them
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 52 per-step grids instantiated — outstanding**
- [ ] **`O-01` W1/W4 sequencing — outstanding; blocking `G1-06` and `G1-07` evidence**
- [ ] **`O-04` `RP-001` unwritten — outstanding; blocks `SIT-J-005` and `SIT-J-007`**
- [ ] **`O-05` `NFR-090`/`091`/`092` identifier collision — outstanding; affects every pack that cites an NFR**
- [ ] Named approvers recorded — **pending QA Lead and CTO delegate**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
