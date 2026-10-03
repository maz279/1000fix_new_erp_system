---
id: TS-013
title: Regression Pack and Smoke Test Checklist
project: 1000FiX ERP System v2.0
content_type: Test script
template: TPL_Test_Script.md
template_version: 1.0
version: 1.0
date: 2026-08-19
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: QA Lead
author: QA Lead with test analysts and Platform Engineering
reviewers: [Solution Architect, DevOps lead, Operations Director, Support Lead, Business Owners Forum representative]
approver: QA Lead with CTO delegate
content_class: E
purpose: >
  The regression suite content and the per-portal post-deployment smoke checklist. Nine waves of
  change are pushed into a live 67-module system on a monthly production cadence, and every one of
  those releases touches modules that other modules depend on. Without a regression pack derived from
  change impact, and a smoke checklist that runs in minutes after every deployment, defects that were
  found and fixed in wave three reappear in wave six, and the first person to notice is a branch agent
  with a customer at the counter.
traces_to: [05-05, 05-06 §11, 05-06 §12, 06-01 §5, 06-01 §6, 06-02 §4, M28, M30, M63, M66, OP-002, OP-004, OP-014, SP-031, TS-001, TS-002, TS-003, TS-004, TS-005, TS-006, TS-009, TS-012, TS-014, TS-017, TS-018]
priority: P1
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md §5 Delivery Method — fortnightly releases to staging, monthly to production within a wave, hotfixes as needed; zero-downtime deployment standard (NFR-008); four weeks of hypercare after every wave go-live
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md §11 Testing Standards — end-to-end automated and run nightly; §7 OPS-01 every deployment automated, repeatable and reversible; OPS-06 feature flags allow any new capability to be disabled without a deployment; §12 AS-01…AS-15
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §4 — every gate from G1 to G9 is reached through releases into a system already carrying the previous waves' scope
    verified: 2026-08-19
    class: P1
supersedes: none
review_due: 2027-02-19
---

# Regression Pack and Smoke Test Checklist

| Item | Value |
|---|---|
| Test level | **Regression** and **Smoke** — `TS-001` §4.1 level 9 by derivation |
| Role executing | Automation for regression; `R33` IT Administrator plus one business role per portal for smoke |
| Modules covered | All modules in scope at the release under test |
| Portals covered | All 12, one smoke checklist each |
| Environment | `SIT` for regression; **production** for smoke, immediately post-deployment |
| Test data set | `TS-002` — regression uses the `SIT` profile; smoke uses a designated production-safe set (§2.1 `RS-09`) |
| Wave | W2 · **but production releases begin in W1** — open item `O-01` |

> **Template conformance.** `TPL_Test_Script.md` at pack level. All six sections retained in order;
> §3 carries two distinct artefacts — the regression pack and the smoke checklists — and the split is
> the addition, justified because they differ in every dimension: environment, executor, duration and
> what a failure means.

---

## 1. Traceability

### 1.1 Two artefacts, deliberately different

| | **Regression pack** | **Smoke checklist** |
|---|---|---|
| Question | Did this change break something that used to work? | Is the thing we just deployed actually alive? |
| When | Before a release ships | Within minutes of it shipping |
| Where | `SIT` | **Production** |
| Who | Automation, with a human reviewing failures | `R33` plus one business role per portal |
| Duration | Hours; a full pass is a scheduled activity | **Under 15 minutes per portal** |
| Scope | Derived from change impact (`RS-01`) | Fixed, short, unchanging between releases |
| A failure means | The release does not ship | **Roll back** — `OP-002` |

**They are in one file because they share a derivation and must not diverge.** A smoke check that
tests something the regression pack does not cover is testing an unowned path; a regression pack
that omits something the smoke checklist watches has the wrong scope.

### 1.2 Why change-impact derivation, not accumulation

`RS-01` requires regression scope to be derived from change impact. The alternative — run everything
every time — fails predictably: the suite grows with every wave until a full pass no longer fits the
release window, and then it is skipped under pressure. That is `TX-17`, and it is the failure mode
this file exists to prevent.

The derivation has three inputs, all of which already exist:

| Input | Source | Gives |
|---|---|---|
| **Changed modules** | The release manifest | The direct blast radius |
| **Event and integration dependencies** | Module event tables; `05-03` integration catalogue | The indirect blast radius — who consumes what changed |
| **Shared master data and rules** | `MD` files touched; `05-05` rules whose thresholds moved | The configuration blast radius, which is the one teams forget |

### 1.3 Traceability obligation

| Field | Source |
|---|---|
| Source test | Every regression case is a **promoted** case from `TS-003`–`TS-012`, never newly authored (`RS-02`) |
| Defect origin | Where a case exists because a defect was found, the `TS-018` defect identifier (`RS-03`) |
| Change trigger | The release and the changed component that put the case in scope for this pass |
| Portal | For smoke cases, the `Pnn` and its owning business role |

---

## 2. Preconditions

### 2.1 Rules

| # | Rule |
|---|---|
| **RS-01** | **Regression scope is derived from change impact for every release** (§1.2), never from habit and never by running everything |
| **RS-02** | **A regression case is a promoted case, not a new one.** Every case originates in `TS-003`–`TS-012`; the regression pack is a selection, so a case cannot exist here without an owner there |
| **RS-03** | **Every defect fixed at Critical or High severity promotes its reproducing case into the permanent core** (§3.2). A defect that recurs after being fixed is a process failure, not bad luck |
| **RS-04** | The **permanent core runs on every release**, regardless of change impact. It is small by design and its size is reported (§3.2) |
| **RS-05** | Every class `H` rule in `05-05` has a permanent-core negative case. **Hard rules are the requirements most likely to be relaxed by an unrelated change**, and a relaxed hard rule is silent |
| **RS-06** | A regression pass is **only valid on a single release**, and a re-run after a fix is a new pass (`TX-15`) |
| **RS-07** | **A smoke checklist completes in under 15 minutes per portal.** A checklist that takes longer will not be run at 02:00 after a deployment, and one that is not run is worse than one that does not exist |
| **RS-08** | **A smoke failure triggers rollback, not investigation.** Investigation happens after the rollback (`OP-002`, `OPS-01` reversible deployments) |
| **RS-09** | **Smoke checks run in production and must therefore be non-mutating or self-cleaning.** A designated production-safe data set is used, its records are marked as test records, and they are excluded from every operational and financial report |
| **RS-10** | Every smoke checklist includes **one bilingual check and one authentication check**, because those are the two failures a deployment causes most often and the two that are least visible from a health endpoint |
| **RS-11** | **Feature flags are part of regression scope.** `OPS-06` requires every new capability to be disableable without a deployment; the disabled state is a state the system can be in, and it is tested (`RS-14`) |
| **RS-12** | Regression coverage is **counted, with its derivation stated** — which cases were in scope for this release and which were deliberately excluded (`TX-24`, `CP-11`) |
| **RS-13** | **No silent truncation.** Where a pass was reduced for time, the excluded set is listed in the release record. A reduced pass reported as a full pass is the defect this rule prevents |
| **RS-14** | Every release exercises the **rollback path itself** at least once per wave, not only the forward path (`OPS-01`, `OPS-07`) |

### 2.2 Preconditions

| # | Precondition | How to establish |
|---|---|---|
| 1 | Release manifest naming every changed component, event schema and `MD` file | `OPS-02`; without it `RS-01` cannot be applied |
| 2 | Event and integration dependency map current | `05-03`; module event tables |
| 3 | Regression cases tagged in their source packs and promotable | `RS-02`; requires a test-management tool — `TS-001` `O-01` |
| 4 | Automation harness able to execute the pack | `06-04` — **does not exist** |
| 5 | Production-safe smoke data set defined, marked and report-excluded | `RS-09` — **does not exist**, `O-03` |
| 6 | `R33` plus a named business role per portal available at deployment time | `06-01` §5 monthly production cadence |
| 7 | Rollback procedure documented and rehearsed | `OP-002`; `RS-08`, `RS-14` |
| 8 | Feature-flag inventory for the release | `OPS-06`; `RS-11` |

---

## 3. Scripts

### 3.1 Regression pack structure

| Tier | Content | When it runs | Size |
|---|---|---|---|
| **T1 Permanent core** | Every class `H` rule negative case; every `P0` `E2E` scenario's critical path; the ten highest-value `UAT` `P0` scripts; every previously fixed Critical or High defect case | **Every release** | Target ≤ 220 cases; reported per wave |
| **T2 Impacted** | Cases for the modules the release changed, plus their event consumers and shared-`MD` dependants | Per release, derived (`RS-01`) | Varies |
| **T3 Full** | Every promotable case from `TS-003`–`TS-012` | **Before every wave gate** | Grows per wave |
| **T4 Statutory** | `TS-009`'s Mushak, register and return cases; `TS-010`'s payroll cases | **Before every wave gate, and before any release touching tax, price or payroll** | ~40 cases |

> **`T4` is separated from `T1` deliberately.** Statutory cases are expensive — they need rendered
> artefacts inspected (`UA-28`) and cannot be fully automated — but they cannot be omitted when a
> tax-relevant change ships. Putting them in `T1` would make every release expensive; leaving them
> only in `T3` would let a price-change release ship without them.

### 3.2 Permanent core composition

| Source | Cases | Why permanent |
|---|---:|---|
| Class `H` rule negative cases (`05-05` §2–§11) | **~130** | `RS-05`; a relaxed hard rule is silent and cumulative |
| `SOD-01`…`SOD-12` assignment blocks | 12 | `NFR-064`; a re-opened SoD combination is a fraud exposure |
| `EA-01`…`EA-12` external scope refusals | 12 | A scope leak is a breach (`TS-011` §5) |
| `P0` `E2E` critical paths (`TS-012`) | 11 | Each is a revenue stream |
| Highest-value `P0` UAT scripts | 10 | Intake, dispatch, part issue, invoice, payment, shift close, claim submission, payroll approval, seller payout, customer booking |
| Previously fixed Critical / High defect cases | grows | `RS-03` |
| Authentication, session and MFA paths | 8 | The most common casualty of an unrelated platform change |
| Bilingual rendering spot set | 6 | `KPI-092` is 100%, and translation coverage regresses invisibly |
| **Target total** | **~189 + fixed-defect cases** | Reported per wave under `RS-04` |

### 3.3 Change-impact derivation procedure

| Step | Action |
|---|---|
| 1 | Take the changed components from the release manifest |
| 2 | Add every module consuming an event whose **schema or semantics** changed |
| 3 | Add every module reading a `MD` file that changed, and every `05-05` rule whose threshold moved |
| 4 | Add every portal surfacing a changed module (`04-00` §4 coverage matrix) |
| 5 | Add every `E2E` scenario whose chain includes anything from steps 1–4 |
| 6 | Add the permanent core (`RS-04`) |
| 7 | Record the derived set, **and the set consciously excluded**, in the release record (`RS-12`, `RS-13`) |

**Step 3 is the step that gets skipped.** A rate-card change is not a code change and does not appear
in a build manifest, which is exactly why `BRU-` threshold moves and `MD` edits are named as
first-class regression triggers here.

### 3.4 Smoke checklists — 12 portals

Every checklist has the same six-item shape (`RS-07`, `RS-10`), with portal-specific content. Each
completes in under 15 minutes.

| # | Item | Applies to |
|---|---|---|
| S1 | **Reach and authenticate** — the portal loads and a real account signs in; MFA where the role requires it | All |
| S2 | **Read** — the portal's opening view renders with real data | All |
| S3 | **Write** — one non-mutating-or-self-cleaning transaction completes (`RS-09`) | All |
| S4 | **Integrate** — one outbound dependency responds: payment, notification, map, gateway | Where the portal has one |
| S5 | **Bilingual** — one screen renders correctly in Bengali (`RS-10`) | All |
| S6 | **Portal-specific canary** — the one thing that must work for this portal to be useful | All |

| Portal | `S3` write check | `S4` integration | `S6` canary |
|---|---|---|---|
| `P01` Customer | Create a booking on the `TS-002` smoke account | bKash sandbox; SMS | **Booking completes in ≤ 3 steps and the tracking link resolves** |
| `P02` Technician | Accept and start a smoke job | Sync endpoint | **Offline mode engages and the job list is available with the network off** |
| `P03` Admin | Create and cancel a smoke intake | Print service | **All 14 workspaces open from the home screen in one click** |
| `P04` Corporate | Raise and withdraw a smoke request | — | Contract-coverage validation returns a result |
| `P05` Vendor | Acknowledge a smoke PO | — | PO list scoped to the vendor only |
| `P06` Analytics | Open the executive dashboard | Warehouse | **Dashboard loads in under 5 s and shows a freshness timestamp** |
| `P07` Seller | Open a smoke listing | Payout service | Broadcast job list renders |
| `P08` Brand | Open a smoke claim | — | Evidence pack opens and renders photographs |
| `P09` Rider | Open a smoke manifest | GPS | **Offline mode engages; queued handover survives a restart** |
| `P10` Contact centre | Open a smoke conversation | Telephony | **Screen pop fires on caller identification** |
| `P11` Auditor | Open a smoke checklist | — | Offline checklist opens and accepts evidence |
| `P12` Partner | Generate a referral link | — | Link resolves and attributes |

### 3.5 Hypercare and rollback

`06-01` §5 sets four weeks of hypercare after every wave go-live and `06-01` §6 sets parallel-run
periods per process. Two additional obligations follow:

| # | Obligation |
|---|---|
| H-01 | During hypercare, the **permanent core runs daily**, not per release |
| H-02 | During a parallel run, the parallel comparison is itself a regression check: divergence between legacy and new is treated as a regression finding (`TS-010` `UA-32` for payroll; `06-01` §6 for orders, inventory, finance and claims) |
| H-03 | **The rollback path is exercised once per wave** (`RS-14`), in a scheduled window, and its evidence is part of the gate pack |
| H-04 | A smoke failure escalates to the `OP-002` incident procedure and to `M66`, **not** to the defect queue first (`TS-001` §4.10) |

### 3.6 Negative and edge cases

| # | Condition | Expected behaviour |
|---|---|---|
| N-01 | Deployment succeeds; one portal fails smoke | Roll back the release, not the portal — `OPS-01` reversibility is release-level (`RS-08`) |
| N-02 | Smoke data set records appear in a financial report | **Defect** — `RS-09` requires exclusion, and a test invoice in a VAT register is a compliance exposure |
| N-03 | A feature flag is off in production and on in `SIT` | Both states are in regression scope (`RS-11`); a pass in one state is not a pass |
| N-04 | A `MD` change ships with no code change | Still triggers derivation step 3; **the most commonly missed trigger** |
| N-05 | Event schema changed additively | Consumers tested for tolerance of the unknown field (`TS-003` `E-03`) |
| N-06 | Regression pass reduced for time | Excluded set listed in the release record (`RS-13`); **never reported as a full pass** |
| N-07 | A previously fixed defect recurs | `RS-03` case should have caught it; if it did not, the case was wrong — **both the defect and the case are raised** |
| N-08 | Rollback leaves migrated data forward-only | `OPS-07` forward-only migrations with a documented reverse procedure; exercised under `H-03` |

---

## 4. Exit Criteria

### 4.1 Per release

| Criterion | Threshold |
|---|---|
| Permanent core (`T1`) | **100% pass** |
| Impacted set (`T2`) | 100% pass |
| Statutory set (`T4`), where the release touches tax, price or payroll | **100% pass** |
| Change-impact derivation recorded, with exclusions | 100% (`RS-12`, `RS-13`) |
| Feature-flag states covered | Both states for every flag in the release |
| Smoke, all deployed portals | **100% pass within 15 minutes each** |
| Smoke failure | **Rollback executed** (`RS-08`) |

### 4.2 Per wave gate

| Criterion | Threshold |
|---|---|
| Full set (`T3`) | 100% of `P0`; ≥ 98% of `P1` |
| Nightly `E2E` suite | Green 5 consecutive nights (`TS-012` `EE-10`) |
| Rollback path exercised | **Once, with evidence** (`H-03`) |
| Permanent core size reported | Yes (`RS-04`) — growth without pruning is itself a finding |
| Recurring defects (`N-07`) | **Zero** |

---

## 5. Defects Raised

| Defect ID | Script | Severity (`TS-018`) | Status |
|---|---|---|---|
| *(populated at execution)* | | | |

**A regression failure is severity-escalated by one level** above the same failure found in a first
pass, and the reason is recorded in `TS-018` §4: a defect in new code is expected work, while a
defect in code that previously worked means the change-impact derivation was wrong, and the wrong
derivation will keep being wrong until it is corrected.

**A smoke failure is not a defect first.** It is a production incident under `M66` and `OP-002`
(`H-04`), and it becomes a defect after the rollback.

---

## 6. Sign-off

| Event | Signatory | Record |
|---|---|---|
| Per-release regression pass | QA Lead | Release record with the derived and excluded sets |
| Per-release smoke, per portal | `R33` IT Administrator with the portal's business role | Deployment record |
| Rollback exercise, per wave | DevOps lead with QA Lead | Gate evidence pack |
| Wave-gate full pass | QA Lead with CTO delegate | Gate evidence pack (`TS-018`) |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **Production releases begin in W1 and this pack is registered at W2.** `06-01` §5 sets a monthly production cadence *within* a wave, `P03` goes live at W1 with 150–250 users, and `06-02` `G1` falls at Month 4. **The first four months of production deployments would have no smoke checklist and no regression pack** — the sixth instance of this sequencing shape in Category 13 | Programme Content Lead with QA Lead | **W1 — register correction** |
| **O-02** | **`RS-02` requires promotable cases and there is no test-management tool.** Cases live in seventeen markdown packs; promotion, tagging and per-release selection are tool functions. `TS-001` `O-01` (`06-04` absent) and `O-02` (`RF-003` unwritten) both bite here | CTO with QA Lead | **W1** |
| **O-03** | **The production-safe smoke data set does not exist** (`RS-09`). Smoke runs in production, so it needs marked records excluded from every operational and financial report — and `N-02` makes a test invoice in a VAT register a compliance exposure. `TS-002` specifies synthetic data for non-production and **says nothing about production**, deliberately; this is the gap between them | QA Lead with Finance Manager and MDM Lead | **W1 — before the first production deployment** |
| **O-04** | **No rollback procedure exists to rehearse.** `RS-08` and `H-03` both depend on it, `OPS-01` requires deployments to be reversible, and `OP-002` is unwritten (Category 17 unstarted). **A smoke checklist whose failure action is "roll back" is incomplete without it** | DevOps lead with Support Lead | **W1** |
| **O-05** | **`RS-05` claims ~130 class `H` negative cases and the figure is derived, not counted.** `05-05` §2–§11 carries the rules; the count here is an estimate from the rule tables and **must be enumerated before `T1` is built**, because `RS-04` reports the core's size and `RS-12` requires counted coverage (`CP-11`) | QA Lead | **W2 — before the first `T1` build** |
| **O-06** | **Feature-flag inventory does not exist** (`RS-11`, precondition 8). `OPS-06` requires every new capability to be disableable, which means the system has two states per flag and regression covers one of them today | Platform Engineering | **W2** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Test_Script.md` at pack level; the two-artefact split in §3 justified
- [x] **Regression and smoke distinguished across all seven dimensions, and the reason they share one file stated**
- [x] Change-impact derivation specified as a seven-step procedure, with the commonly skipped step named
- [x] Fourteen rules stated, including no-silent-truncation and rollback-not-investigation
- [x] **Four-tier pack structure, with statutory cases separated and the reason recorded**
- [x] Permanent-core composition enumerated by source, with a target size that is reported rather than assumed
- [x] Twelve per-portal smoke checklists with a fixed six-item shape and a portal-specific canary each
- [x] Bilingual and authentication checks made mandatory in every smoke run, with the reason
- [x] Hypercare and parallel-run obligations derived from `06-01` §5 and §6
- [x] Eight edge cases stated, including `MD`-only changes and test records reaching a VAT register
- [x] Regression failures severity-escalated by one level, with the reasoning recorded
- [x] Smoke failures routed as incidents under `M66`/`OP-002`, not as defects
- [x] All internal links resolve
- [x] Six open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The permanent core built and its class `H` case count enumerated — outstanding (`O-05`)**
- [ ] **`O-01` W1 production releases against a W2 pack — outstanding**
- [ ] **`O-03` production-safe smoke data set absent — outstanding; blocks the first deployment**
- [ ] **`O-04` no rollback procedure — outstanding; `RS-08` incomplete without it**
- [ ] Named approvers recorded — **pending QA Lead and CTO delegate**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
