---
id: CH-002
title: Training Plan and Delivery Schedule
category: 13 — Training, Change & Adoption
code: CH
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Training Lead / Head of Learning & Development
approver: HR Director with the Operations Director
standards_basis: >
  ISO 10015:2019 (second edition, 2019-12) — Quality management: guidelines for competence
  management and people development · ISO 9001:2015 clause 7.2 (competence) and clause 7.5.3
  (documented information) · ISO 10018:2020 (people engagement; ISO 10018:2012 withdrawn) ·
  New World Kirkpatrick four levels with Required Drivers · ISO 21502:2020 §7.6 (resources) ·
  Bangladesh Labour Act 2006 as amended by the Bangladesh Labour (Amendment) Ordinance 2025 and
  the Bangladesh Labour (Amendment) Act 2026, with the Bangladesh Labour Rules 2015 (amended 2022)
traces_to: >
  PGD-000 CH-002 · 06-05_Change_Management_and_Training_Plan.md (planned, never written —
  superseded by this document for the training half) · AUDIT-009 TR-01 (CRITICAL), TR-02, TR-03,
  TR-04, TR-06, TR-07, TR-09, TR-10, R-01…R-08 · TR-001 LS-01…LS-18 · TR-002 CU-01…CU-15 ·
  TR-004 · KPI-062, KPI-063, KPI-064 · BRU-LMS-01, BRU-LMS-02, BRU-SRM-09 · G1-11, G1-12, G2-01
depends_on: CH-001 · GV-004 · GV-007 · QA-004 (test data) · UX-003 · MG-005 · CH-005
verified_on: 2026-08-19
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-19 01:20 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# CH-002 — Training Plan and Delivery Schedule

### Category 13 · Code `CH` · ISO 10015:2019 · ISO 9001:2015 §7.2 · ISO 10018:2020 · New World Kirkpatrick

---

> **Local rule prefix: `TPD-nn`.** Verified to return **zero** occurrences workspace-wide before
> allocation, at 2026-08-19 01:20 (+06). See [`CH-001`](CH-001_Organisational_Change_Management_Plan.md)
> header note for why no document in this category uses `CH-nn`.

---

## 1. Purpose

`TR-001`…`TR-024` supply an excellent training **system**: a strategy, a competency framework, a
role-to-curriculum map, an assessment and certification policy, two question banks, fifteen role
packs, a job-aid library, a train-the-trainer kit and a release-training standard. Twenty-four
files, all written, all audited.

**What no file supplies is the arithmetic.** Nobody has counted how many hours of training this
programme requires, how many trainers deliver them, in which weeks, at which of 51+ sites, in which
language, against how many rooms and devices, and what the learners' time costs. `TR-001` `LS-11`
requires exactly that count and `TR-001` `O-04` records that **no trainer establishment exists**.

This document counts it.

> **The result, computed in §4 and §6 from `05-04` headcounts and the durations declared in
> `TR-007`…`TR-023` — not quoted from any register:**
>
> | | Low | High |
> |---|---:|---:|
> | People requiring a curriculum | **752** | **1,428** |
> | **Formal learner-hours, whole programme** | **12,306** | **21,759** |
> | — as production time (8 h day, 5-day week) | **308 PW** | **544 PW** |
> | Share falling in **W1 and W2** | **75.3%** | **67.0%** |
> | **Trainer-days, delivery + preparation** | **380** | **525** |
> | Peak trainer establishment required in W1–W2 | **2.8 FTE** | **3.5 FTE** |
> | Trainers currently established | **0** | **0** |
> | Trainer FTE in `06-01` §4 | **0.5–1.0**, *combined with the Change Lead role* | |
>
> **Supervised on-the-job training is additional and larger**: `3,665 – 7,325` supervised
> learner-days are declared in the packs, requiring **733 – 1,465 supervisor-days** — and
> **fourteen of thirty roles carry an `LS-03` OJT obligation with no stated period at all** (§4.6).

### 1.1 Scope

**In scope:**

| # | Covered |
|:--:|---|
| 1 | The **counted** learner-hour model: population × curriculum × wave |
| 2 | The trainer establishment, cohort model, venues, devices and language split |
| 3 | The delivery schedule anchored to `06-01` §3 wave months and `06-01` §6 site offsets |
| 4 | The **statutory induction curriculum** — the `AUDIT-009` `TR-01` CRITICAL finding — and how it is delivered while `TR-025` is unregistered |
| 5 | Certification tracking, competence evidence and the `M22` dependency |
| 6 | The assessment-sequencing defect (`AUDIT-009` `TR-04`) and its resolution |
| 7 | Training environment and data (`TS-002`, `QA-004`) as a hard precondition |
| 8 | Refresh, release training and the perpetual (non-project) cost |
| 9 | The resource, budget and learner-time position, stated whether or not it is funded |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Curriculum content, learning objectives, exercises, question items | `TR-001`…`TR-024` | `CP-01`: content is authored once. This plan schedules and resources it; it does not rewrite it |
| Competency framework and proficiency scale | `TR-001` §4.4 | Cited, never restated |
| Pass marks, attempts, appeal, override | `TR-004` | Cited, never restated |
| Change impact, sponsorship, resistance, saturation | [`CH-001`](CH-001_Organisational_Change_Management_Plan.md) | Training is a change lever; the change plan owns the lever set |
| Champion selection, released time, charter | [`CH-005`](CH-005_Super_User_and_Champion_Network_Charter.md) | `TR-023` trains them; `CM-008` defines the change role; `CH-005` releases the time |
| Adoption measurement | [`CH-004`](CH-004_Adoption_Measurement_and_Reinforcement_Plan.md) | Kirkpatrick Level 3/4 measurement is adoption, not delivery |
| External-party enablement | Category 18 `EO` | `CU-04`: external parties are enabled, not trained (no ISO 9001 §7.2 competence obligation) |
| `M22` LMS build | `M22` specification; `RQ-003` fit-gap | This plan is a consumer of the LMS, not its specification |
| Test data and anonymisation | `QA-004` | The training sandbox consumes `QA-004`'s masked data set; it does not define it |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **HR Director** | The establishment being asked for, the statutory exposure, and the certification obligation |
| **Training Lead** *(a post nobody holds — `CH-001` `OCM-Q-01`)* | The operating plan |
| CFO | §7 — the cost of learner time, which is the largest line and the one never counted |
| Operations Director | Which of their people are away from the floor, in which week, at which site |
| Branch managers | The site-level delivery obligation and the room, device and connectivity requirement |
| Quality Manager | The ISO 9001 clause 7.2 competence evidence position |
| PMO | The schedule lines and the `G1-12` gate criterion |
| Implementation vendor | The training environment, data and access preconditions they must deliver |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / element | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO 10015:2019** *(second edition, 2019-12; supersedes ISO 10015:1999)* | Competence management and people development as a **planned and systematic process** at organisational, team and individual levels | §3 competence need → §4 curriculum and volume → §5–§6 delivery → §8 evaluation. The four-stage cycle (define needs, design and plan, provide, evaluate outcomes) is the section order | None. **This is the governing standard for this document** and the category overview did not name it |
| " | *"does not add to, change or otherwise modify requirements for the ISO 9000 family"* | Cited as guidance; the binding requirement remains ISO 9001 clause 7.2 | None |
| **ISO 9001:2015 clause 7.2** | Determine necessary competence · ensure competence · take actions and evaluate their effectiveness · **retain documented information as evidence** | §3.2 competence determination; §8.3 evidence via `M22` FR-LMS-038 | None. `KPI-067` targets zero major non-conformances and clause 7.2 is the clause a surveillance audit tests against a training function |
| **ISO 9001:2015 clause 7.5.3** | Control of documented information | Certification records are controlled in `M22`, not in spreadsheets | None |
| **ISO 10018:2020** *(current; 2012 edition withdrawn)* | Guidance for people engagement, with a competence section aligned to ISO 9001:2015 | §5.2 delivery-mode selection and §9 champion-delivered model | None |
| **New World Kirkpatrick** | Four levels, planned in reverse from Level 4; **Required Drivers** sustain Level 3 | Inherited wholesale from `TR-001` §4.1 and §4.3 (`LS-01`, `LS-04`); §8 schedules the measurement | **Declared limitation, inherited from `TR-001`:** no causal attribution is claimed at Level 4 (`LS-16`) |
| **ISO 21502:2020 §7.6** | Resources — planning, establishing the team, managing resources | §7 | None |
| **Bangladesh Labour Act 2006**, as amended by the **Bangladesh Labour (Amendment) Ordinance 2025** *(Ordinance No. 65 of 2025, gazetted 17 November 2025)* and the **Bangladesh Labour (Amendment) Act 2026**; **Bangladesh Labour Rules 2015 (amended 2022)** | Safety committee in establishments with **50 or more workers** (§90A as amended); annual safety training; accident reporting; the new §61A right to refuse dangerous work | §3.3 statutory floor; §5.5 delivery of the Layer 1 safety module | **⚠ Currency correction.** `TR-001` §4.9 and `AUDIT-009` `TR-01` cite *"Bangladesh Labour Act 2006 with Labour Rules 2015"* with **no amendment and no verification date**. Approximately **ninety changes** were made between 2025 and 2026 by the two instruments above. §3.3 and `TPD-Q-01` carry the consequence |

> **`TPD-01` — the statutory basis of mandatory training carries an instrument name, an amendment
> and a verification date, and is re-verified before every annual refresh cycle.** The estate has
> three critical findings that were stale citations (`C-04`, `H-01`, `M-01`); a training obligation
> resting on the pre-2025 text of the Labour Act is the same defect with a statutory consequence.
> **`RR-005` — the Standards & Regulatory Currency Register — is ⛔ and unwritten**, and this is the
> fourth category to need it.

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `TR-001` §4.1–4.12 | `../../project_content/08_Training_and_Enablement/08A_Framework/TR-001_Training_Strategy_and_Competency_Framework.md` | Kirkpatrick model, 70-20-10 delivery mix, five proficiency levels, the four-hour target, Bengali-first position, the statutory floor, the budget basis, and rules `LS-01`…`LS-18` |
| `TR-002` §4–§7 | `.../TR-002_Role_Based_Curriculum_Map.md` | Four curriculum layers, the **Layer 1 universal core at ~5.5 h**, the role-to-pack map for all 38 roles, prerequisite rules `CU-01`…`CU-15`, and the coverage gap |
| `TR-004` | `.../TR-004_Assessment_and_Certification_Policy.md` | Pass marks, attempts, validity, lapse, override, appeal, evidence |
| `TR-007`…`TR-021` | `.../08B_Course_Packs/` | **The fifteen role packs, each declaring a duration** — the primary input to §4 |
| `TR-022`, `TR-023`, `TR-024` | " | Job aids; the 16-hour train-the-trainer kit; the release-training standard |
| `05-04` §5 | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` | Registered roles `R01`–`R38` with headcount — the population input to §4 |
| `06-01` §3, §4, §6 | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` | Wave months, the business-side commitment table, the per-location T−4→T+4 rollout pattern |
| `06-02` §2.8, §4 | `.../06-02_KPI_Benefits_and_Acceptance_Criteria.md` | `KPI-062`, `KPI-063`, `KPI-064`; gate criteria `G1-11`, `G1-12`, `G2-01` |
| `AUDIT-009` | `../../project_content/_AUDIT/AUDIT-009_Category_08_TR_Content_Audit.md` | Eleven findings, one CRITICAL; nine open; nine recommendations |
| `M22` | `../../1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M22_Learning_Competency_and_Certification.md` | `FR-LMS-001`…`040` — competency catalogue, certification register, lapse handling, automatic assignment, OJT sign-off (`FR-LMS-027`), evidence file (`FR-LMS-038`), eligibility service to `M02` (`FR-LMS-039`) |

**Enumeration.** Every figure in §4 and §6 is computed at **2026-08-19 01:20 (+06)** from the two
primary tables named above. **No figure is taken from `TR-002` §6.2's wave summary** — §4.5 records
why.

### 2.3 Audit findings this document closes

| Finding | Source | Severity | Treatment here |
|---|---|:--:|---|
| **`TR-01`** — 800+ employees have a statutory curriculum no file owns | `AUDIT-009` | **CRITICAL** | **Treated, not closed.** §3.3 and §5.5 deliver the Layer 1 curriculum from `TR-002` §4.2's specification and assign interim ownership, resourcing and a schedule. **Closure requires registering `TR-025`, which is a Steering Committee decision under `CM-R1` that no plan can take** (`R-01`) |
| `TR-02` — six roles with no pack; four on interim routes; two blocked | `AUDIT-009` | High | §5.4 costs and schedules the four interim deltas; `CH-001` §9.6 forces the `R13` decision; the two blocked roles are `TPD-Q-05` |
| `TR-03` — the competence gate cannot be enforced | `AUDIT-009` | High | §8.4 states both branches and requires the manual-control restatement if the integration is absent. Confirmation is `AUDIT-009` `R-02`, CTO-owned |
| **`TR-04`** — assessment instruments land after the packs that assess against them | `AUDIT-009` | High | **Closed in specification.** §8.2 brings the minimum-viable `TR-005`/`TR-006` cell set to W1 for the nine affected packs, and defines what "minimum viable" means |
| `TR-06` — `TR-017` states a contact-centre population 33% larger than `05-04` | `AUDIT-009` | Medium | §4.2 uses `05-04`'s **30–60**, records the divergence, and routes it to `TPD-Q-02` |
| `TR-07` — 20–60 field auditors are not a registered role | `AUDIT-009` | Medium | §4.2 includes them as an **unregistered population** with their hours counted; `CU-01` still blocks their curriculum assignment. `TPD-Q-05` |
| `TR-09` — the release-training standard arrives after the releases it governs | `AUDIT-009` | Medium | §10.2 brings `TR-024`'s tiering model and the CAB arrangement forward to W1 |
| `TR-10` — twenty of twenty-four files depend on sandbox data that does not exist | `AUDIT-009` | Low | §9 makes the training environment and data a **hard precondition** with a named owner and a date, per `R-08` |
| `R-07` — resource the training function | `AUDIT-009` | — | §7 — the establishment, counted |

---

## 3. Competence Need — What the Business Requires

ISO 10015:2019 stage 1. **`TPD-02`: a curriculum exists because a competence is required to
perform a specified task to a specified standard — never because a module exists.**

### 3.1 The six populations

| Population | Count | Training implication |
|---|---:|---|
| Internal employees, all registered roles | **732 – 1,368** | Layer 1 statutory core for every one; Layer 2 by role |
| Field technicians (`R10`–`R12`) | 215 – 430 | Mobile microlearning, Bengali-native, offline discipline, 10 days OJT |
| Branch sites | **51+** | Delivery scheduled around live operations; the counter cannot close |
| Corporate portal users (`R37`) | 500 – 2,000 | **Out of scope** — Category 18 `EO` (`CU-04`) |
| Marketplace sellers and external parties (`R38`) | 1,000 – 3,000 | **Out of scope** — Category 18 `EO` |
| **Marketplace seller technicians** | **1,000 – 4,000** | **Out of scope of this plan, and the largest population in the estate.** `OP-001` §4.1 enumerates them; `CM-002` §4.3 omits them entirely (`AUDIT-019` `CM-08`). `BRU-LMS-02` gates their category activation on a qualification — **which no `TR` or `EO` file specifies**. `TPD-Q-06` |

### 3.2 Determining competence — ISO 9001 clause 7.2

| Clause 7.2 requirement | How it is met | Evidence |
|---|---|---|
| (a) Determine the necessary competence | `TR-001` §4.4 proficiency scale bound to `MD-010`; `TR-002` §5 role map | `MD-010`, `TR-002` |
| (b) Ensure competence on the basis of education, training or experience | Layer 1–4 curriculum; `TR-004` assessment; `M22` FR-LMS-027 OJT sign-off | `M22` |
| (c) Where applicable, take actions to acquire competence and **evaluate the effectiveness** of those actions | §8 Kirkpatrick Levels 2–4; `LS-17` retires a course whose measure does not move within two evaluation cycles | `CH-004` |
| (d) **Retain appropriate documented information as evidence of competence** | `M22` FR-LMS-038 competence evidence file, retrievable per learner and per role | `M22`, `LS-13` |

> **`TPD-03` — competence evidence is retrievable per learner on demand, for ISO and brand audit,
> before the first certification is issued.** If `M22` FR-LMS-038 is not available at W1, evidence
> is held in a controlled register under `GV-011` and migrated — **not** improvised in spreadsheets,
> which fails clause 7.5.3.

### 3.3 The statutory floor — the CRITICAL finding

`AUDIT-009` `TR-01` is the most serious finding in any content audit: **a statutory training
curriculum for 800+ employees that no file in a 452-file register owns.** `TR-002` §4.2 specifies
it — seven modules, ~5.5 hours — and the register has no `TR-025` to deliver it.

**Three dependencies rest on it:**

| Dependency | Consequence of the gap |
|---|---|
| `BRU-LMS-01` — overdue mandatory training restricts affected work types | A Class `H` hard rule operating on an undefined set |
| `KPI-064` — mandatory training completion, 95% at W7 rising to 98% | A KPI measuring completion of a curriculum with no safety course in it |
| `CU-03` — no production access before Layer 1 is complete | An access gate whose precondition has no deliverable |

**And the statutory basis is stronger and more recent than `AUDIT-009` recorded.**

| Instrument | Position at 2026-08-19 |
|---|---|
| Bangladesh Labour Act 2006 | In force, **substantially amended** |
| **Bangladesh Labour (Amendment) Ordinance 2025** — Ordinance No. 65 of 2025, gazetted **17 November 2025** | Amends the 2006 Act; **§90A** requires a safety committee in establishments with **50 or more workers**; **§61A** introduces a worker's right to refuse dangerous work without retaliation; **§332/§332A** require a five-member complaint committee on violence and harassment in every establishment |
| **Bangladesh Labour (Amendment) Act 2026** | Parliamentary enactment following the Ordinance; approximately **ninety changes** across the two instruments |
| Bangladesh Labour Rules 2015 **(amended 2022)** | Implementation detail; 99 rule modifications |

**Consequences this plan must carry:**

1. **`TR-001` §4.9's statutory table is out of date.** It cites the 2006 Act and the 2015 Rules
   without the 2025/2026 amendments. It is not wrong about the *duty*; it is unverified about the
   *text*, and `LS-10` makes statutory training non-deferrable.
2. **The complaint-committee obligation (§332/§332A) is a training obligation this estate has not
   registered at all.** A five-member committee in every establishment, with a female chairperson
   and a majority of women members, requires trained committee members. **No `TR` module, no
   Layer 1 module and no `SP` procedure covers it.** Recorded as `CHA-06`.
3. **`AUDIT-009` `R-06` — confirm the statutory obligations with Legal — is now more urgent, not
   less.** It was raised against the 2006/2015 text. The text has moved twice since.

**`TPD-04`: statutory training is delivered on the current text of the instrument, and the text is
verified with Legal before each annual cycle.** Owner: HSE Lead with Legal Counsel. Needed by:
**W0** — `TPD-Q-01`.

---

## 4. The Learner-Hour Model — Counted

ISO 10015:2019 stage 2. **`TPD-05`: the training volume is computed from population × declared
duration, and every input is cited to the file that declares it.**

### 4.1 Method

| Step | Input | Source |
|:--:|---|---|
| 1 | Population per role, low and high bound | `05-04` §5 headcount column |
| 2 | Layer 1 duration, universal | `TR-002` §4.2 — seven modules totalling **~5.5 h** |
| 3 | Layer 2 duration per role | The **Duration** line of each of `TR-007`…`TR-021` |
| 4 | Layer 4 duration for champions and super-users | `TR-023` — **16 h over four days** |
| 5 | Wave assignment per role | `TR-002` §5 |
| 6 | Cohort size and delivery day | §6.1, declared assumptions |

**Excluded from the formal total and counted separately in §4.6:** supervised on-the-job training,
Layer 3 specialisation of unstated duration, and release/refresher training (§10).

### 4.2 Population and Layer 2 duration, per role

Durations are quoted from the pack's own **Duration** line. Where a pack declares a core plus a
module or delta, both are shown and the applicable sum is used.

| Role | Pop. low | Pop. high | Pack | Declared duration | L2 hours used |
|---|---:|---:|---|---|---:|
| `R01` CEO | 1 | 1 | **none registered** | `P06` orientation only | 2 |
| `R02` CTO | 1 | 1 | **none registered** | orientation | 2 |
| `R03` CFO | 1 | 1 | **none registered** | orientation | 2 |
| `R04` CCO | 1 | 1 | **none registered** | orientation | 2 |
| `R05` Operations Director | 1 | 2 | **none registered** | orientation | 2 |
| `R06` Branch Manager | 51 | 60 | `TR-011` | **12 h** over three days + 10 d OJT | 12 |
| `R07` Dispatch Manager | 3 | 8 | `TR-008` | **8 h** over two days + 5 d OJT | 8 |
| `R08` Service Centre Agent | 150 | 250 | `TR-007` | **4 h to Competent on the core task set**, + 2 h deferred | 6 |
| `R09` Workshop Supervisor | 20 | 40 | `TR-010` | **8 h** + 5 d OJT | 8 |
| `R10` Senior Technician | 80 | 150 | `TR-009` | **6 h core** as ~40 microlearning items + 10 d OJT | 6 |
| `R11` Junior Technician | 120 | 250 | `TR-009` | as above | 6 |
| `R12` Specialist Technician L3 | 15 | 30 | `TR-009` + **L3 extension** | 6 h core; **extension duration not stated** — `TPD-Q-04` | 6 |
| `R13` Remote Support Engineer | 15 | 40 | `TR-021` + MSP delta | 12 h core + **6 h delta** | 18 |
| `R14` Data Services Technician | 5 | 12 | `TR-016` + delta | 8 h core + **4 h data-services delta** | 12 |
| `R15` Logistics Coordinator | 10 | 25 | `TR-020` | **coordinator 6 h** + 5 d OJT | 6 |
| `R16` Rider / Delivery Agent | 50 | 150 | `TR-020` | **rider 4 h** on-device + practical, + 5 d OJT | 4 |
| `R17` Inventory Manager | 5 | 10 | `TR-012` + manager module | 6 h core + **3 h manager** | 9 |
| `R18` Branch Store Keeper | 51 | 60 | `TR-012` | **core 6 h** | 6 |
| `R19` Procurement Officer | 4 | 8 | `TR-013` | **8 h** + 5 d OJT | 8 |
| `R20` Warehouse Operative | 15 | 30 | `TR-012` + warehouse module | 6 h core + **3 h warehouse** | 9 |
| `R21` Sales Manager | 3 | 6 | `TR-018` | **core 8 h** | 8 |
| `R22` Account Manager | 8 | 20 | `TR-018` | **core 8 h** | 8 |
| `R23` Marketing Manager | 2 | 4 | `TR-018` + marketing delta | 8 h + **3 h delta** | 11 |
| `R24` Marketplace Ops Officer | 4 | 10 | `TR-019` | **6 h** + 5 d OJT | 6 |
| `R25` Retail / Refurbishment | 5 | 15 | `TR-012` + refurbishment delta | 6 h + **3 h delta** | 9 |
| `R26` Finance Manager | 2 | 4 | `TR-014` | **core 10 h** over three days | 10 |
| `R27` Finance Officer | 10 | 20 | `TR-014` | **core 10 h** | 10 |
| `R28` Warranty Claims Officer | 4 | 10 | `TR-014` + warranty module | 10 h + **4 h warranty** | 14 |
| **`R29` Cashier / Counter Finance** | **51** | **60** | `TR-014` + counter cash | 10 h core + **3 h counter cash** | **13** |
| `R30` HR Manager | 1 | 2 | `TR-015` | **10 h** + 5 d OJT | 10 |
| `R31` HR Officer | 3 | 6 | `TR-015` | **10 h** | 10 |
| `R32` Quality Manager | 2 | 4 | `TR-016` + calibration | 8 h core + **4 h auditor calibration** | 12 |
| `R33` IT / System Administrator | 4 | 8 | `TR-021` | **core 12 h** + 10 d OJT | 12 |
| `R34` Contact Centre Agent | 30 | 60 | `TR-017` | **core 12 h** over three days + 10 d OJT | 12 |
| `R35` Contact Centre Supervisor | 4 | 10 | `TR-017` + supervisor extension | 12 h + **4 h extension** | 16 |
| **Field auditor** *(unregistered — `TR-07`)* | 20 | 60 | `TR-016` + calibration | 8 h + 4 h | 12 |
| **Registered + unregistered total** | **752** | **1,428** | | | |

> **⚠ `CHA-03` — the cashier route is the plan's largest single misallocation.** `R29` is **51–60
> people**, one per branch, routed to `TR-014` — a **10-hour finance core designed for the 16–34
> head-office finance staff in `R26`–`R28`** — plus a 3-hour counter-cash module. That is
> **663–780 learner-hours** to teach counter cash handling. A dedicated 3–4 hour counter-cash route
> would deliver the same competence in roughly a quarter of the time. Recorded as `TPD-Q-03`, owned
> by the Training Lead with the Finance Manager, needed by **W1 − 8 weeks**. This plan schedules
> the route as declared, because `CP-01` forbids inventing curriculum here, and flags it.

> **`CHA-04` — `TR-017` states a contact-centre audience of "30–80 agents"; `05-04` registers `R34`
> at 30–60.** `AUDIT-009` `TR-06` raised it; it is unresolved. **This plan uses `05-04`'s 30–60**
> (`CU-01`, `SK-02`: the role register governs) and records that at a cohort of 12, 60 agents is 5
> cohorts and 80 is 7 — **a 40% delivery-effort difference for a 12-hour course**. `TPD-Q-02`.

### 4.3 Layer 1 — the universal core

`TR-002` §4.2, seven modules, applicable to **every one of 752–1,428 people**:

| Module | Duration | Statutory | Delivery mode (§5.2) |
|---|---:|:--:|---|
| Health, safety and incident reporting | 90 min | **✔ Labour Act §90A as amended** | **Facilitated, at the site** — §5.5 |
| Information security and acceptable use | 45 min | | E-learning |
| Data protection and customer confidentiality | 45 min | | E-learning |
| Anti-bribery, ethics and speaking up | 30 min | | E-learning |
| Quality system and your part in it | 30 min | **✔ ISO 9001 §7.2** | E-learning |
| System basics and navigation | 60 min | | E-learning |
| Terminology — what we call things | 30 min | | E-learning |
| **Total** | **5.5 h** | | **4.0 h e-learning + 1.5 h facilitated** |

**Layer 1 volume: 752 × 5.5 = 4,136 h (low) · 1,428 × 5.5 = 7,854 h (high).**

### 4.4 The total, computed

| Component | Low (h) | High (h) | Basis |
|---|---:|---:|---|
| **Layer 1** universal core | **4,136** | **7,854** | 752 / 1,428 × 5.5 h |
| **Layer 2** role packs | **5,898** | **11,025** | Σ (population × declared duration), §4.2 |
| **Layer 4** `TR-023` for champions, **deputies** and super-users | **2,272** | **2,880** | (51+51+40) / (60+60+60) people × 16 h — deputies included per `CNC-13` |
| **Total formal learner-hours** | **12,306** | **21,759** | |
| — as person-days at 8 h | **1,538** | **2,720** | |
| — **as person-weeks of production time** | **308** | **544** | `LS-12`: learner time is costed and reported |

> **This is the figure `TR-001` `LS-11` and `LS-12` require and nobody had produced.** For scale:
> `GV-007` §7 places the entire **content workstream at 477 files** and the **guiding-document
> workstream at 352 PW**. The *learner time alone* for this programme's training is
> **308–544 person-weeks**, and it appears in no estimate, no budget and no plan.

### 4.5 By wave

| Wave | People | Learner-hours (L1+L2) | Share of L1+L2 | Wave months (`06-01` §3) |
|:--:|---|---:|---:|---|
| **W1** | 350 – 524 | **4,809 – 7,060** | **47.9% – 37.4%** | 1–4 |
| **W2** | 234 – 473 | **2,749 – 5,580** | 27.4% – 29.6% | 5–8 |
| W3 | 79 – 213 | 862 – 2,256 | 8.6% – 11.9% | 9–13 |
| W4 | 54 – 121 | 1,049 – 2,408 | 10.5% – 12.8% | 14–18 |
| W5 | 31 – 87 | 520 – 1,462 | 5.2% – 7.7% | 19–22 |
| W7 | 4 – 10 | 46 – 115 | 0.5% – 0.6% | 27–30 |
| **Total** | **752 – 1,428** | **10,034 – 18,879** | | |
| *(+ `TR-023`, delivered W0–W1 per site)* | 142 – 180 | 2,272 – 2,880 | | |

**`W1 + W2 carry 7,558 – 12,640 learner-hours — 75.3% at the low bound and 67.0% at the high.`**

> **⚠ `CHA-07` — `TR-002` §6.2's wave learner-hours cannot be reproduced from the durations its own
> packs declare.** `TR-002` states W1 at *"~3,000–4,500"* and W2 at *"~4,000–7,000"*. Computed from
> `05-04` populations and the `TR-007`…`TR-021` Duration lines, W1 is **4,809–7,060** and W2 is
> **2,749–5,580** — and the model puts **W1 above W2**, which `TR-002` reverses. Neither candidate
> reconciliation works: excluding Layer 1 gives W2 = 1,398–3,978, and including the declared 10-day
> OJT gives W2 = 20,000+. **`TR-002`'s figures are unreproducible.** Its qualitative conclusion —
> *"W1 and W2 together carry roughly 80% of the load"* — survives and is confirmed at **67%–75%**.
> Recorded as an audit finding; remediation is `TR-002`'s, not this plan's (`CP-01`).

### 4.6 On-the-job training — the load nobody has counted

`LS-03` and `CU-05` make OJT sign-off mandatory for **every operational role**. The packs declare
the periods:

| Roles with a declared OJT period | 16 of 30 operational roles |
|---|---|
| **Declared OJT volume** | **3,665 – 7,325 supervised learner-days** |
| **Supervisor time at 20% of the period** *(declared planning assumption)* | **733 – 1,465 supervisor-days** |
| **Roles carrying an `LS-03` obligation with no stated OJT period** | **14** — `R08`, `R14`, `R17`, `R18`, `R20`, `R21`, `R22`, `R23`, `R25`, `R26`, `R27`, `R28`, `R29`, `R32` |
| Population in those 14 roles | **313 – 505 people** |
| If those carry the 5-day minimum used elsewhere | **+1,565 – 2,525 learner-days** |

> **`TPD-06` — an operational role with no stated OJT period is not exempt from `LS-03`; it is
> unspecified.** Fourteen roles covering 313–505 people are in that position, including `R08`
> Service Centre Agent — the largest single population and the one carrying the `G1-03`
> three-minute intake bar. **The supervisor time is the real constraint**: 733–1,465 supervisor-days
> fall on workshop supervisors, branch managers and finance managers who are themselves learners in
> the same wave. Escalated to `CH-001` §8 saturation and recorded as `TPD-Q-07`.

> **OJT is productive work under supervision, not lost time**, which is why it is counted
> separately from the formal total rather than added to it. The **supervisor's** time is the cost,
> and it is the cost that has never appeared in an estimate.

---

## 5. Delivery Design

ISO 10015:2019 stage 3.

### 5.1 The layered curriculum, inherited

`TR-002` §4.1's four layers govern and are not restated. **`TPD-07`: this plan schedules layers; it
does not re-define them.** `CU-02` (layers in order) and `CU-03` (no production access before Layer
1) are the two rules that constrain every date in §6.

### 5.2 Delivery mode by population

Applying `TR-001` §4.2's mode-selection table to the counted populations:

| Population | Mode | Cohort | Why |
|---|---|---:|---|
| **All 752–1,428 — Layer 1 (4.0 h)** | **E-learning, self-paced, bilingual** | n/a | Statutory, repeatable, must be evidenced identically for every learner (`TR-001` §4.2) |
| **All — Layer 1 safety module (1.5 h)** | **Facilitated at the site** | 20 | §5.5 — a statutory safety duty is not discharged by a click-through |
| `R10`–`R12` Technicians (215–430) | **Mobile microlearning in `P02`**, Bengali-native | n/a | `M22` FR-LMS-025; ~40 items under 3 minutes (`TR-009`); 51+ sites and no classroom will hold them |
| `R16` Riders (50–150) | Mobile + practical | n/a | Short-form, on-device |
| `R08` Agents (150–250) | **Blended: classroom at the branch + sandbox practice** | 12 | The four-hour target depends on practice with realistic data (`LS-06`) |
| `R06`, `R18`, `R29` branch-resident (153–180) | Classroom at branch or regional hub | 12 | One per site; regional aggregation avoids 51 separate deliveries |
| Finance, procurement, HR, quality, admin, dispatch, commercial | Classroom | 12 | High-consequence, small populations, discussion needed |
| `R34`, `R35` Contact centre (34–70) | Classroom + console practice | 12 | Six channels; scripted handling |
| `R01`–`R05` Executives (5–6) | Briefing | 6 | `P06` orientation |
| Champions, **deputies** and super-users (142–180) | **`TR-023`, 16 h over four days** | 15 | Train-the-trainer; the mechanism that scales everything else. Deputies are trained, not merely named (`CNC-13`) |

### 5.3 Language

`TR-001` `LS-07`, `LS-08` and `CG-010` govern. The delivery consequence:

| Population | Language of delivery | Volume implication |
|---|---|---|
| Technicians, riders (265–580) | **Bengali-native, authored not translated** | The largest content-authoring burden, and `KB-002` `O-05` records that **Bengali technical terminology for board-level electronics does not substantially exist** |
| Branch agents, store keepers, cashiers (252–370) | Bengali primary, English technical terms retained | Bilingual delivery at 51+ sites |
| Head office — finance, HR, quality, IT (~24–46) | English acceptable | Minimal |
| **Layer 1, all 752–1,428** | **Bilingual, both versions available** | Statutory content in a language the learner does not read is not training |

> **`TPD-08` — a Bengali-first population trained in English has not been trained.** `SK-08` states
> it for communication; `LS-07` states it for content; this plan states it for **delivery**. A
> trainer who cannot teach in Bengali cannot deliver to `R08`–`R20`, and the trainer establishment
> in §7 is specified in **Bengali-capable FTE**, not FTE.

### 5.4 The four interim routes — costed

`AUDIT-009` `TR-02` routes four roles with declared deltas. The delivery consequence:

| Role | Pop. | Route | Delta | Delta hours | Declared in |
|---|---:|---|---:|---:|---|
| `R13` Remote Support Engineer | 15 – 40 | `TR-021` + MSP delta | 6 h | **90 – 240** | `TR-021` §3.2, `PK-10` |
| `R14` Data Services Technician | 5 – 12 | `TR-016` + delta | 4 h | 20 – 48 | `TR-016` §3.3, `PK-08` |
| `R23` Marketing Manager | 2 – 4 | `TR-018` + delta | 3 h | 6 – 12 | `TR-018` §3.2, `PK-09` |
| `R25` Retail / Refurbishment | 5 – 15 | `TR-012` + delta | 3 h | 15 – 45 | `TR-012` §3.4, `PK-05` |

**A dedicated `R13` pack, if the `CH-001` §9.6 decision goes that way**, is estimated at **12–18
person-days of specialist authoring** on the `TR-021` precedent, requiring `R12`/`R13` technical
time that competes directly with MSP delivery capacity — the same constraint `AUDIT-008` `R-07`
records for `KB`.

### 5.5 Delivering the statutory core while `TR-025` does not exist

**The gap is real and the training cannot wait for a register decision.** `LS-10`: statutory
training is not subject to prioritisation or deferral.

| Element | Position |
|---|---|
| **Specification** | `TR-002` §4.2 — seven modules, ~5.5 h. **It is a complete specification; what is missing is an owning deliverable** |
| **Interim ownership** | **HR with the HSE Lead**, per `AUDIT-009`'s own remediation instruction for `TR-025` |
| **Safety module delivery** | **Facilitated, at the site, 90 minutes, in the working language**, by a person who has completed a train-the-trainer route. Not e-learning: §90A as amended contemplates a functioning safety committee and actual training, and a click-through is not defensible to a labour inspector |
| **Volume** | 752 – 1,428 people × 1.5 h facilitated = **10 – 18 trainer-days** at a cohort of 20 |
| **Refresh** | **Annual minimum**, and on any change of procedure or equipment (`LS-10`, Labour Rules 2015) — **perpetual, not project** |
| **Evidence** | `M22` completion record; the ISO 9001 §7.2(d) evidence file |
| **Blocked on** | Registering `TR-025` (`AUDIT-009` `R-01`, Steering Committee, `CM-R1`) and confirming the current statutory text with Legal (`R-06`, `TPD-Q-01`) |

> **`TPD-09` — Layer 1 is delivered whether or not `TR-025` is registered, and the gap between the
> specification and the deliverable is reported at every Steering meeting until it closes.** A
> statutory obligation cannot be held open by a register decision. What a plan *can* do is refuse
> to let the absence become invisible.

### 5.6 Venues, devices and connectivity

**`TPD-10`: a training session with no confirmed room, device set and connectivity is not
scheduled; it is aspirational.**

| Requirement | Specification | Owner | Status |
|---|---|---|---|
| Classroom per regional hub | 1 room, 12 seats, projector, 12 devices | Operations | ⬜ Unconfirmed |
| Branch delivery space | The branch itself, outside counter hours or in shifts | Branch manager | ⬜ Unconfirmed |
| **Learner devices** | 12 per hub for classroom; **`P02` devices for 215–430 technicians** | IT with Operations | ⬜ `RSK-008` mitigation includes *"Company-provided devices"*; procurement is `CO-006` ⬜ |
| Connectivity for virtual delivery | Above `05-06` threshold at the delivery site | IT | ⬜ Unconfirmed — and sub-threshold sites are exactly where classroom is required instead |
| **Training environment** | §9 | CTO | ⚠ [`PE-002`](../10_Infrastructure_DevOps_and_Environments/PE-002_Environment_Strategy_and_Specification.md) and [`PE-007`](../10_Infrastructure_DevOps_and_Environments/PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md) were **issued 2026-08-19**, concurrently with this document. The *environment* is now specified; **no training environment has been built or loaded**, and §9 is unchanged in substance |
| Bengali-capable trainers | §7 | HR | ⬜ Establishment does not exist |

---

## 6. The Delivery Schedule

### 6.1 Declared planning assumptions

**`TPD-11`: every planning assumption in this section is declared, and a figure derived from an
undeclared assumption is not a plan.**

| # | Assumption | Value | Basis |
|:--:|---|---|---|
| A1 | Classroom cohort size | **12** | `TR-001` §4.2 — classroom is for small populations needing discussion |
| A2 | Facilitated safety cohort size | 20 | Toolbox-talk format |
| A3 | `TR-023` cohort size | 15 | Train-the-trainer with practice |
| A4 | Trainer delivery day | **6 contact hours** | Allows travel, setup and reset |
| A5 | Preparation ratio | **2 h preparation : 1 h delivery** | First-delivery ratio for new material; falls to 0.5:1 on repeat |
| A6 | Trainer delivery utilisation | **60%** | The remainder is travel across 51+ sites, administration and content maintenance |
| A7 | Working days per month | 21 | |
| A8 | OJT supervisor time | 20% of the OJT period | §4.6 |

> **A5 and A6 are the two assumptions that most change the answer.** At a 1:1 preparation ratio the
> trainer-day total falls by roughly a quarter; at 80% utilisation the FTE requirement falls by a
> quarter. Both are stated so that a reviewer can disagree with the number rather than with the
> plan.

### 6.2 Trainer-days by wave

Layer 2 classroom and blended delivery only; e-learning and mobile microlearning consume authoring
effort, not trainer-days.

| Wave | Learner-hours | **Trainer-days, Layer 2 delivery** |
|:--:|---:|---:|
| **W1** | 4,809 – 7,060 | **50 – 62** |
| W2 | 2,749 – 5,580 | 6 – 8 |
| W3 | 862 – 2,256 | 5 – 9 |
| W4 | 1,049 – 2,408 | 17 – 27 |
| W5 | 520 – 1,462 | 11 – 18 |
| W7 | 46 – 115 | 1 |
| **Subtotal, Layer 2** | | **90 – 125** |

> **W2 carries 27%–30% of the learner-hours and only 6–8 trainer-days**, because the technician
> population is delivered by mobile microlearning. That is the delivery model working as designed —
> **and it means W2's risk is not trainer capacity but content authoring, device provision and
> Bengali-native authoring**, all of which are `TPD-Q-08`.

### 6.3 The trainer establishment

| Component | Trainer-days low | Trainer-days high |
|---|---:|---:|
| Layer 2 classroom and blended delivery | 90 | 125 |
| Layer 1 facilitated safety module (1.5 h, cohort 20) | 10 | 18 |
| `TR-023` train-the-trainer (16 h, cohort 15; **142–180 people, 10–12 cohorts**) | 27 | 32 |
| **Delivery subtotal** | **127** | **175** |
| Preparation at 2:1 (A5) | 253 | 350 |
| **Total trainer effort** | **380** | **525** |

**Peak establishment.** W1 and W2 carry 75.3%–67.0% of the load across 8 months = 168 working days
(A7). At 60% delivery utilisation (A6):

| | Low | High |
|---|---:|---:|
| Trainer-days falling in W1–W2 | 286 | 352 |
| **Bengali-capable trainer FTE required** | **2.8** | **3.5** |
| **Established today** | **0** | **0** |
| In `06-01` §4 | **0.5–1.0 FTE**, and that post is *"Change & Training Lead"* — **one person for two functions** | |

> **`TPD-12` — the plan requires 2.8–3.5 Bengali-capable trainer FTE at peak and the programme has
> established a fraction of one, shared with the change function.** `AUDIT-009` `R-07` is dated
> **W0 — "it precedes everything"** — and states the position exactly: *"the delivery model
> currently rests on people who have not been asked."* Options are §7.3.

### 6.4 The per-site schedule

Anchored to `06-01` §6, which this plan does not re-time:

| Offset | Activity | Population | Owner |
|---|---|---|---|
| **T−8 weeks** | Champion nominated; **4 h/week release confirmed in writing** | Branch manager | `CH-005` §5 |
| T−6 weeks | Site training logistics confirmed: room, devices, connectivity, shift cover | Branch manager with L&D | `TPD-10` |
| **T−4 weeks** | Site readiness assessment; **Layer 1 e-learning opens for the site** | All site staff | L&D |
| T−3 weeks | Layer 1 facilitated safety session at the site | All site staff | HSE-trained facilitator |
| **T−2 weeks** | **`TR-023` champion training** (16 h) | Champion + deputy | L&D |
| **T−1 week** | **Layer 2 all-staff training in Bengali; access provisioned on completion** | Role populations | L&D + champion |
| T−0 | Go-live; floor-walking | All | Champion, super-user, support |
| T−0 → T+2 weeks | **OJT sign-off period begins** (`FR-LMS-027`) | Operational roles | Line supervisors |
| T+4 weeks | Hypercare exit; **Level 3 behaviour observation** | Sample per role | L&D with line managers |

> **`TPD-13` — Layer 1 opens at T−4 weeks and must be complete before Layer 2 starts** (`CU-02`),
> which means the site has **three weeks** to move 6–9 resident staff through 5.5 hours each while
> running a live branch. At the high bound that is **87–123 learner-hours per site** (computed:
> branch-resident roles `R06`, `R08`, `R09`, `R18`, `R29` = 4,418–6,265 hours over 51 sites).
> **This is the single tightest constraint in the schedule** and it is why shift-cover confirmation
> at T−6 weeks is a hard precondition rather than an administrative step.

### 6.5 The W1 concentration

| Fact | Figure |
|---|---:|
| W1 learner-hours | **4,809 – 7,060** |
| W1 people | 350 – 524 |
| W1 trainer-days | **50 – 62** |
| W1 duration | 4 months = **84 working days** |
| Trainer FTE required in W1 alone, at 60% utilisation | **1.0 – 1.2** for delivery, **3.0 – 3.7** including preparation |
| W1 sites | Dhaka HQ + **5 pilot centres** |

**W1 is simultaneously the wave with the least mature product, the least mature support model, the
most defects, and 38%–48% of the entire programme's training load.** `CH-001` §8.2 records the same
population as over-saturated. The plan states it; the sequencing decision belongs to the Steering
Committee.

---

## 7. Resources, Budget and the Cost of Learner Time

ISO 21502:2020 §7.6.

### 7.1 What is required

| Resource | Requirement | In `GV-007` §8? | Funded? |
|---|---|:--:|:--:|
| **Bengali-capable trainers** | 2.8 – 3.5 FTE at W1–W2 peak; 1.0 – 1.5 FTE steady | ✘ | ✘ |
| Training Lead | 1.0 FTE, 36 months | ✘ — `06-01` §4's 0.5–1.0 is shared with Change | ✘ |
| Instructional design / content maintenance | 0.5 – 1.0 FTE, perpetual | ✘ | ✘ |
| **Specialist authorship** (`TR-005`, `TR-009`, an `R13` pack) | `R12`/`R13` technical time, competing with repair and MSP capacity | ✘ | ✘ |
| Translation and in-context sign-off (`BN-018`) | 20 bilingual `TR` files + all Layer 1 | ✘ | ✘ |
| **Training environment and data** | §9 | ⚠ `PE-002`/`PE-007` **issued 2026-08-19**; specified, not built | ✘ |
| Learner devices | 12/hub + `P02` devices for 215–430 technicians | `CO-006` ⬜ | ✘ |
| LMS (`M22`) | Build and licence | Build squad | Partially — as a module, not as a training cost |
| **Champion released time** | `CH-005` §5 | ✘ | ✘ |
| **Learner time** | **308 – 544 person-weeks** | ✘ | ✘ |

### 7.2 The cost of learner time — `LS-12`

**`TPD-14`: learner time is costed and reported alongside delivery cost.** `TR-001` `LS-12`
requires it and states why: *"a training plan that shows only trainer cost understates the true
figure by an order of magnitude and invites decisions that look cheap."*

| Line | Low | High |
|---|---:|---:|
| Trainer effort | **380 – 525 trainer-days** | |
| **Learner time** | **1,538 person-days** | **2,720 person-days** |
| **Ratio, learner time : trainer time** | **4.0 : 1** | **5.2 : 1** |
| OJT supervisor time (§4.6) | 733 supervisor-days | 1,465 supervisor-days |

> **For every trainer-day this programme buys, it spends four to five learner-days and one to three
> supervisor-days.** A budget that shows only the trainer line understates the training cost by
> roughly **80%**. `AUDIT-015` `AF-09` already records that 520–775 PW of content work sits outside
> the business case; **308–544 PW of learner time is a second, separate omission of the same
> class**, and `CO-005`'s TCO — already declared *"materially wrong"* by audit `H-02` — does not
> contain it either.

### 7.3 The options, since the establishment does not exist

| Option | What it means | Consequence |
|:--:|---|---|
| **A** | **Hire 3 Bengali-capable trainers.** `GV-007` §8.3 gives content authors a **4–8 week** lead time; trainers are comparable | Must start **before charter approval** to be in post for W1 |
| **B** | **Contract delivery to the implementation vendor** | Vendor trainers are rarely Bengali-native for field content (`LS-07`), and `CG-010` forbids machine translation on field-facing content |
| **C** | **Shift the load to the champion network** — 142–180 people already trained by `TR-023` | **This is already the design** (70-20-10; `CM-008`). It does not remove the trainer requirement; it removes the *scaling* requirement. And `CH-005` records that the champions' time is itself unreleased and unfunded |
| **D** | Deliver less | `LS-10` forbids it for statutory content; `CU-03`/`CU-05` forbid it for access-gated content. **Available only for Layer 3** |

> **`TPD-15` — option C is not a substitute for options A or B, and treating it as one is how a
> training plan fails silently.** The champion network multiplies a trainer; it does not replace
> one. `CH-005` §5 shows the network's own time is unreleased, which means the current plan of
> record rests on **two** unfunded populations, not one. Escalated as `TPD-Q-09` and to `GV-005`.

---

## 8. Assessment, Certification and Evidence

ISO 10015:2019 stage 4; `TR-004` governs the policy and is not restated.

### 8.1 What this plan owns

| Owned here | Owned by `TR-004` |
|---|---|
| **When** an assessment is available relative to the pack that needs it | Pass marks, attempts, remediation |
| **How many** assessment events, and their delivery logistics | Validity, renewal, lapse |
| Certification **tracking** and the evidence route | Override, appeal, integrity |
| The consequence if the system gate does not exist | The gate's policy basis |

### 8.2 `AUDIT-009` `TR-04` — the sequencing defect, resolved

**The finding.** `TR-005` (technician question bank) and `TR-006` (functional question bank) are
scheduled at **W2**. Nine packs deliver at **W1** and assess against `TR-006`. Six of the nine
record it independently as an open item. The consequence: **W1 users are trained and granted
production access before the gate exists at all.**

**The resolution.** `AUDIT-009` `R-04` offers two options and requires that the second be a
decision rather than a default. This plan takes the first.

| # | Requirement | Detail |
|:--:|---|---|
| 1 | **A minimum-viable cell set from `TR-005`/`TR-006` is delivered at W1** for the nine affected packs — `TR-007`, `TR-008`, `TR-010`, `TR-011`, `TR-012`, `TR-014`, `TR-021`, `TR-022`, `TR-023` | |
| 2 | **"Minimum viable" is defined**, so it cannot be negotiated downward | Per pack: **≥ 3 items per learning objective**, covering **every** money-, stock- or customer-affecting task in the pack, drawn from a bank of **≥ 3× the items presented** so that no two learners see an identical paper (`TR-005`'s own "large, rotating bank or no bank at all" principle) |
| 3 | The full bank follows at W2 as scheduled | The W1 set is a subset, not a different instrument |
| 4 | **If requirement 1 is not met**, W1 access is granted on **completion rather than competence**, recorded as a **knowing exception with an end date** in `GV-003`, naming the roles and the populations affected | `TPD-16` |

> **`TPD-16` — granting W1 access on completion rather than competence is a decision that is
> recorded, dated and ended.** It is not a default, and it is not silent. `LS-14`, `CU-05`, `QB-27`
> and `PK-11` all state the competence condition; a programme that quietly fails to meet them at
> W1 has four rules it is already not honouring before the first gate.

### 8.3 Certification tracking

| Element | Mechanism | Dependency |
|---|---|---|
| Certification register | `M22` FR-LMS-009…016 | `M22` at W1 |
| Expiry and renewal workflow | `M22`; `MD-011` brand validity | `MD-011` |
| **Lapse suspends assignment eligibility** | `M22` FR-LMS-013 → `BRU-SRM-09`, `BRU-HRM-01` | `M02` dispatch integration |
| Overdue mandatory training restricts work types | `BRU-LMS-01` | `M55` scheduling (`FR-LMS-022`, `CU-10`) |
| **Evidence file per learner** | `M22` FR-LMS-038 | ISO 9001 §7.2(d); brand audit |
| Reporting | `KPI-062` certifications current 100% · `KPI-063` claims rejected for an uncertified technician: zero · `KPI-064` mandatory completion 95% W7 / 98% W8 | `06-02` §2.8 |

### 8.4 If the competence gate cannot be automated — `AUDIT-009` `TR-03`

Whether `M29` can gate production access on an `M22` competence signal is **unconfirmed**, and four
files in two categories state the rule as though it can.

| Branch | Consequence for this plan |
|---|---|
| Integration exists | `CU-03`/`CU-05` are enforced by the system. Nothing further is required |
| **Integration does not exist** | `CU-03`, `CU-05`, `LS-14`, `QB-27` and `PK-11` become **manual controls across 752–1,428 users and nine waves**. This plan then requires: a named access-approval operator per site; a **10% monthly sample audit** by the Quality Manager; and the residual risk recorded in `GV-005`. See `CH-001` §10.5 and `OCM-31` |

**Confirmation is `AUDIT-009` `R-02`, owned by the CTO with the Security Lead, needed by W1.**
`M22` `FR-LMS-039` already exposes an eligibility service to `M02` for dispatch, which establishes
the pattern is technically intended — **but `M02` dispatch eligibility is not the same integration
as `M29` access provisioning**, and the audit is explicit about the distinction.

### 8.5 Effectiveness evaluation

| Level | What is measured | Cadence | Owner |
|:--:|---|---|---|
| 1 Reaction | Relevance and usability. **Diagnostic only — never reported as a training outcome** (`LS-02`) | Per cohort | L&D |
| 2 Learning | Assessment result; first-attempt pass rate. **A rate near 100% means the assessment is too easy** (`TR-004`) | Per cohort | L&D |
| **3 Behaviour** | OJT sign-off completion before production access (target 100%); on-the-job observation against the pack's behaviour criteria; system signals — override rates, error rates, help-desk topics | Per pack schedule | Line managers with L&D |
| **4 Results** | The `RP-001` / `06-02` KPI each pack names (`LS-01`) | Per `CH-004` §5 | Business owner |

> **`TPD-17` — a course whose target measure does not move is revised or retired within two
> evaluation cycles** (`LS-17`), and the retirements are reported, not zero. A training catalogue
> that only ever grows is a catalogue nobody evaluates.

---

## 9. Training Environment and Data — A Hard Precondition

`AUDIT-009` `TR-10`: **`TS-002` — the training and test data set — is cited as a dependency in the
exercise tables of 20 of the 24 `TR` files.**

### 9.1 The dependency chain

| Requirement | Owning document | Status at 2026-08-19 |
|---|---|---|
| A training environment | [`PE-002`](../10_Infrastructure_DevOps_and_Environments/PE-002_Environment_Strategy_and_Specification.md), [`PE-007`](../10_Infrastructure_DevOps_and_Environments/PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md) | **⚠ Corrected at issue — both were written on 2026-08-19, during this document's authoring window.** The environment is now **specified**; it is not built, not provisioned and not loaded. `PGD-AUDIT-CAT-09` `MGA-01` recorded the same gap for migration against the same two documents. **`TPD-Q-11`: confirm that `PE-002`'s environment set includes a training environment sized for 12-seat cohorts with a 30-minute reset** |
| Masked, realistic training data | `QA-004` Test Data Management & Anonymisation Plan | ✅ Issued |
| The training data **set** | `TS-002` (Category 13 `TS`, `project_content`) | Registered; sequencing is `AUDIT-009` `R-08` |
| Loaded before the training invitation goes out | `CA-04` `M4` blocking dependency: *"course pack approved; training environment loaded"* | ⬜ |

### 9.2 The rule

**`TPD-18`: no training session is scheduled against an environment that is not loaded and
verified.** `TR-003` `O-01` states the design consequence plainly: *without a sandbox, packs are
built on demonstration rather than practice*. And `TR-001` §4.2 is explicit that
simulation/sandbox is the **wrong** mode *"where no sandbox with realistic data exists"* — which
means that without it, every money-, stock- and customer-affecting course reverts to a mode its own
strategy rejects.

| Control | Requirement |
|---|---|
| Environment | Available and stable **6 weeks before the first W1 cohort** |
| Data | Loaded, masked per `QA-004`, and **representative of the site's own data** where practicable |
| Reset | Between cohorts, automated, within 30 minutes |
| Verification | A named L&D person completes one full exercise set per pack before the cohort opens |
| **Escalation** | Environment not available at T−6 weeks → the cohort is re-scheduled, and the slip is reported to the Steering Committee as a **training-readiness breach**, not absorbed |

---

## 10. Refresh, Release Training and the Perpetual Cost

### 10.1 Refresh obligations

`TR-001` §4.8 governs and is not restated. The **volume** consequence:

| Content class | Cycle | Population | Recurring learner-hours/year |
|---|---|---:|---:|
| **Statutory and safety (Layer 1 safety module)** | **Annual minimum**, and on any change of procedure or equipment | 752 – 1,428 | **1,128 – 2,142** |
| Full Layer 1 | Annual (`TR-002` §4.1) | 752 – 1,428 | 4,136 – 7,854 |
| Brand certification | Per `MD-011` validity | Technicians on warranty work | Per brand |
| Technician technical | 24 months, or on device-family change | 215 – 430 | ~645 – 1,290 |
| System / role training | **On each release affecting the role** (`TR-024`) | Varies | §10.2 |
| Regulatory and tax | On each Finance Act or NBR change | Finance | Unpredictable |

> **`TPD-19` — refresh is perpetual and is budgeted as an operating cost, not a project cost.**
> Layer 1 alone recurs at **4,136–7,854 learner-hours every year, for ever**, of which
> **1,128–2,142 hours** are the statutory safety minimum. `TR-001` §4.10's budget table names it —
> *"Refresh: perpetual, not project"* — and no operating budget contains it.

### 10.2 `AUDIT-009` `TR-09` — release training arrives after the releases

`TR-024` is `P2`/`W2`. `06-01` places the first release at **W1**, and nine `TR` packs deliver at
W1. **The standard governing how a release is trained arrives after the first releases it should
have governed.**

| # | Requirement | Detail |
|:--:|---|---|
| 1 | **`TR-024`'s change-class tiering model (§3.2) is applied from W1**, even though the full standard issues at W2 | Tier by change class: 5 minutes to 4 hours |
| 2 | **`RL-08` — L&D sits at the Change Advisory Board — is in place from the first W1 release** | Retrospective CAB attendance is not possible |
| 3 | `RL-03`/`RL-05` — the training artefact exists **before** the release | A release with no training artefact is not approved for deployment |
| 4 | If 1–3 are not met, W1 changes reach users unannounced | Which is the failure `TR-024` exists to prevent, **and the first impression the workforce forms of the system** |

> The release cadence is *"fortnightly to staging; monthly to production within a wave"* (`06-01`
> §5). At one release per month across 36 months, that is **36 release-training events**, each
> tiered, each bilingual, and none of them in any estimate.

---

## 11. Governing Rules

| # | Rule | Class |
|---|---|:--:|
| `TPD-01` | The statutory basis of mandatory training carries an instrument name, an amendment and a verification date, re-verified before every annual cycle | **H** |
| `TPD-02` | A curriculum exists because a competence is required to perform a specified task to a specified standard | **H** |
| `TPD-03` | Competence evidence is retrievable per learner on demand, before the first certification is issued | **H** |
| `TPD-04` | Statutory training is delivered on the current text of the instrument, verified with Legal | **H** |
| `TPD-05` | Training volume is computed from population × declared duration, with every input cited to the file that declares it | **H** |
| `TPD-06` | An operational role with no stated OJT period is unspecified, not exempt from `LS-03` | **H** |
| `TPD-07` | This plan schedules the four curriculum layers; it does not re-define them | **H** |
| `TPD-08` | A Bengali-first population trained in English has not been trained; the establishment is specified in Bengali-capable FTE | **H** |
| `TPD-09` | Layer 1 is delivered whether or not `TR-025` is registered, and the gap is reported at every Steering meeting until it closes | **H** |
| `TPD-10` | A session with no confirmed room, device set and connectivity is not scheduled | **H** |
| `TPD-11` | Every planning assumption is declared; a figure derived from an undeclared assumption is not a plan | **H** |
| `TPD-12` | The trainer establishment is stated as a requirement even when unfunded, and the shortfall is reported | **H** |
| `TPD-13` | Layer 1 completes before Layer 2 starts (`CU-02`); the site's shift cover is confirmed at T−6 weeks | **H** |
| `TPD-14` | Learner time is costed and reported alongside delivery cost (`LS-12`) | **H** |
| `TPD-15` | The champion network multiplies a trainer; it never substitutes for one | **H** |
| `TPD-16` | Granting access on completion rather than competence is a recorded, dated, ended decision — never a default | **A** |
| `TPD-17` | A course whose target measure does not move is revised or retired within two evaluation cycles (`LS-17`) | **A** |
| `TPD-18` | No training session is scheduled against an environment that is not loaded and verified | **H** |
| `TPD-19` | Refresh is perpetual and budgeted as an operating cost | **H** |
| `TPD-20` | Training commitments publish to `M55` so committed learners are unavailable for assignment (`LS-18`, `CU-10`) | **C** |
| `TPD-21` | A role trained more than one wave before it uses the system is retrained, not counted (`CU-14`) | **C** |
| `TPD-22` | Delivery figures are recomputed at every wave boundary from a fresh `05-04` enumeration; populations are never carried forward (`SK-17`) | **H** |
| `TPD-23` | No cohort is scheduled into a quiet period listed in `CH-001` §8.3 | **H** |
| `TPD-24` | A pack may not be substituted for another without a recorded gap analysis (`CU-11`) | **A** |

> Class: **H** hard block · **A** approved override · **S** soft warning · **C** computed.

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `TPD-Q-01` | **Confirm the current statutory training obligations** against the Labour (Amendment) Ordinance 2025 and Act 2026, including the §332/§332A complaint-committee training this estate has not registered | **HSE Lead with Legal Counsel** | **W0** | `AUDIT-009` `TR-01`'s severity; every Layer 1 delivery; `CHA-06` |
| `TPD-Q-02` | `TR-017` states 30–80 contact-centre agents; `05-04` registers 30–60. Which is the planning population? | Contact Centre Manager with MDM | W4 − 12 weeks | Cohort count; a 40% delivery-effort difference |
| `TPD-Q-03` | Should `R29` cashiers (51–60) take the 10-hour `TR-014` finance core, or a dedicated 3–4 hour counter-cash route? | Training Lead with Finance Manager | **W1 − 8 weeks** | 663–780 learner-hours; `CHA-03` |
| `TPD-Q-04` | `TR-009`'s L3 extension for `R12` declares no duration | Training Lead with Technical Director | W2 − 8 weeks | 15–30 specialists' curriculum volume |
| `TPD-Q-05` | Register the roles for Sustainability (`SP-026`), Rental Operations (`SP-027`) and the 20–60 field auditors in `MD-009` | MDM with HR Director | **W1** | `CU-01` blocks curriculum assignment; `AUDIT-009` `R-03` |
| `TPD-Q-06` | **1,000–4,000 marketplace seller technicians** must pass a category qualification under `BRU-LMS-02`, and **no `TR` or `EO` file specifies it** | CCO with Marketplace Ops and Training Lead | W7 − 20 weeks | `P07` activation; the largest population in the estate |
| `TPD-Q-07` | Fourteen roles carry an `LS-03` OJT obligation with no stated period, covering 313–505 people | Training Lead with business owners | W1 − 6 weeks | 733–1,465 supervisor-days; `CH-001` §8 saturation |
| `TPD-Q-08` | Who authors the Bengali-native technician content, given `KB-002` `O-05` — that Bengali technical terminology for board-level electronics does not substantially exist? | Localisation Lead with Technical Director | **W2 − 16 weeks** | 215–430 technicians; `RSK-008` |
| `TPD-Q-09` | **Is the trainer establishment funded?** 2.8–3.5 Bengali-capable FTE at peak against 0 established | **HR Director with CFO** | **W0 — it precedes everything** (`AUDIT-009` `R-07`) | Every date in §6 |
| `TPD-Q-10` | Is the W1 minimum-viable assessment set (§8.2) funded and scheduled, or is `TPD-16`'s exception invoked? | Training Lead with the Steering Committee | **W1 − 8 weeks** | `AUDIT-009` `TR-04`; nine packs |
| `TPD-Q-11` | **Does `PE-002`'s environment set include a training environment** — sized for 12-seat cohorts, with `QA-004`-masked data and a 30-minute automated reset? `PE-002` was issued 2026-08-19, concurrently with this document, and has not been read against §9's requirements | Training Lead with Platform Engineering | **W1 − 10 weeks** | Every date in §6.4; `TPD-18`; audit finding `CHA-12` |

---

## 13. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `CH-002-D-01` | Governing standard | ISO 10015:2019 · ISO 9001 §7.2 alone · no standard | **ISO 10015:2019 as the process standard, ISO 9001:2015 §7.2 as the binding requirement** | ISO 10015 is the only ISO standard specifically for competence management and people development, and its four-stage cycle maps to this document's sections. It explicitly does not modify ISO 9001, so both are cited with their correct force | The category overview's standards line is corrected to include it — `CHA-05` |
| `CH-002-D-02` | Whether to use `TR-002` §6.2's wave learner-hours or recompute | Use them · **recompute from primary sources** | **Recompute** | `PG-03`/`RG-06`: count, do not consult. The recomputation found `TR-002`'s figures unreproducible and reversed on W1 vs W2 (`CHA-07`) | This plan's figures differ from `TR-002`'s and the difference is explained, not hidden |
| `CH-002-D-03` | Whether to include supervised OJT in the formal learner-hour total | Include · **count separately** | **Count separately (§4.6)** | OJT is productive work under supervision; adding it to the formal total would overstate lost production by a factor of three. The *supervisor's* time is the real cost and is stated as such | Two figures, each honest, neither concealing the other |
| `CH-002-D-04` | Layer 1 safety module delivery mode | E-learning for all 5.5 h · **4.0 h e-learning + 1.5 h facilitated** | **Facilitated safety module** | §90A as amended contemplates a functioning safety committee and actual training. A click-through is not defensible to a labour inspector, and `TR-001` §4.2 lists on-the-job-only delivery as the *wrong* choice for statutory topics | +10–18 trainer-days; a defensible statutory position |
| `CH-002-D-05` | `AUDIT-009` `TR-04` resolution | Bring the bank forward · accept completion-based access | **Bring a defined minimum-viable set forward**, with the exception route recorded if it fails | `R-04` requires that the second option be a decision, not a default. Defining "minimum viable" is what stops it being negotiated to nothing | §8.2; `TPD-Q-10` |
| `CH-002-D-06` | Whether to specify the cashier route differently from `TR-014` | Specify a new route here · **schedule as declared and flag** | **Schedule as declared, flag as `TPD-Q-03`** | `CP-01`: curriculum content is authored in Category 08, not here. A guiding document that invents curriculum creates the duplication `AUDIT-009` `TR-08` warns about | 663–780 learner-hours are scheduled at the declared duration, with the finding visible |
| `CH-002-D-07` | Trainer establishment expressed in FTE or in Bengali-capable FTE | FTE · **Bengali-capable FTE** | **Bengali-capable FTE** | `LS-07` and `SK-08` make Bengali the delivery language for the majority of the population. An establishment counted in undifferentiated FTE can be met on paper and fail in the branch | §6.3, §7.1 and `TPD-08` |

---

## 14. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | The learner-hour total is computed, not quoted, and its inputs are traceable per role | §4.2, §4.4 — 36 rows, each citing the pack that declares the duration |
| `AC-02` | The trainer establishment is stated as a number with declared assumptions | §6.1 (eight assumptions), §6.3 — **2.8–3.5 Bengali-capable FTE** |
| `AC-03` | Every `AUDIT-009` finding is treated, referred or declared out of scope | §2.3 — nine findings and one recommendation |
| `AC-04` | The statutory position is stated on the **current** text of the instrument | §2.1, §3.3 — Ordinance 2025 / Act 2026 / Rules 2015 (amended 2022), verified 2026-08-19 |
| `AC-05` | Learner time is costed and reported (`LS-12`) | §7.2 — 308–544 PW; a 4.0:1 to 5.2:1 learner-to-trainer ratio |
| `AC-06` | The delivery schedule anchors to `06-01` §6 offsets, not to dates | §6.4 |
| `AC-07` | Every open question has an owner and a needed-by date | §12 — ten of ten |
| `AC-08` | Preconditions that are absent are named as absent | §5.6, §7.1, §9 — environment ⛔, trainers 0, devices ⬜ |
| `AC-09` | The document declares what it does not own | §1.1 — nine boundaries |
| `AC-10` | Approval record | ⬜ **Cannot be met** — `PGD-A2-25` |

**Definition of done.** Complete when `AC-01`–`AC-09` are met, the `PGD-000` row is updated with a
fresh enumeration timestamp, and the approver has signed.

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | [`CH-001`](CH-001_Organisational_Change_Management_Plan.md) | Capability treatment for every `Capability` classification; saturation limits constrain §6 |
| Upstream | `GV-004` Integrated Programme Plan | Where §6's dates must appear as schedule lines |
| Upstream | `GV-007` Estimation Model & Resource Plan | Where §7's establishment must appear |
| Upstream | `QA-004` Test Data Management & Anonymisation Plan | The masked data the training sandbox consumes |
| Upstream | `UX-003` Wireframe & Screen Inventory | Training material depends on screens existing |
| Lateral | [`CH-005`](CH-005_Super_User_and_Champion_Network_Charter.md) | `TR-023` trains the network this plan depends on to scale |
| Lateral | [`CH-004`](CH-004_Adoption_Measurement_and_Reinforcement_Plan.md) | Kirkpatrick Levels 3 and 4 measurement |
| Downstream | [`RL-003`](../12_Release_Deployment_and_Transition/RL-003_Go_Live_Readiness_Assessment_and_Gate_Criteria.md) *(issued 2026-08-19)* | `PR-2`/`PR-3` training completion is a readiness criterion |
| Downstream | [`RL-004`](../12_Release_Deployment_and_Transition/RL-004_Rollout_and_Branch_Wave_Deployment_Plan.md) *(issued 2026-08-19)* | Per-site readiness includes `CH-002` completion — the register's own words |
| Downstream | `SV-005` Hypercare & Transition-to-Support ⛔ | Floor-walking and refresher demand during hypercare |
| Lateral | `../../project_content/08_Training_and_Enablement/` | All 24 `TR` files — the curriculum this plan schedules |
| Lateral | `../../1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M22...` | `FR-LMS-001`…`040` — the LMS this plan consumes |
| Lateral | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04...` | The population input |

---

## 16. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
[`CH-001`](CH-001_Organisational_Change_Management_Plan.md) ·
[`CH-003`](CH-003_Stakeholder_Engagement_and_Communication_Plan.md) ·
[`CH-004`](CH-004_Adoption_Measurement_and_Reinforcement_Plan.md) ·
[`CH-005`](CH-005_Super_User_and_Champion_Network_Charter.md) ·
[`../08_Quality_Engineering_and_Test/QA-004_Test_Data_Management_and_Anonymisation_Plan.md`](../08_Quality_Engineering_and_Test/QA-004_Test_Data_Management_and_Anonymisation_Plan.md) ·
[`../00_Programme_Governance_and_Control/GV-007_Estimation_Model_and_Resource_Plan.md`](../00_Programme_Governance_and_Control/GV-007_Estimation_Model_and_Resource_Plan.md)

**Workspace**
[`../../project_content/08_Training_and_Enablement/08A_Framework/TR-001_Training_Strategy_and_Competency_Framework.md`](../../project_content/08_Training_and_Enablement/08A_Framework/TR-001_Training_Strategy_and_Competency_Framework.md) ·
[`../../project_content/08_Training_and_Enablement/08A_Framework/TR-002_Role_Based_Curriculum_Map.md`](../../project_content/08_Training_and_Enablement/08A_Framework/TR-002_Role_Based_Curriculum_Map.md) ·
[`../../project_content/08_Training_and_Enablement/08A_Framework/TR-004_Assessment_and_Certification_Policy.md`](../../project_content/08_Training_and_Enablement/08A_Framework/TR-004_Assessment_and_Certification_Policy.md) ·
[`../../project_content/_AUDIT/AUDIT-009_Category_08_TR_Content_Audit.md`](../../project_content/_AUDIT/AUDIT-009_Category_08_TR_Content_Audit.md) ·
[`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md`](../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md) ·
[`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md`](../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md) ·
[`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md`](../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md)

**External standards and sources** *(all verified 2026-08-19)*

| Source | Edition / date | Verified |
|---|---|---|
| **ISO 10015:2019** | Second edition, 2019-12. Quality management — Guidelines for competence management and people development | 2026-08-19 |
| ISO 9001:2015 | Clause 7.2 competence; clause 7.5.3 documented information | 2026-08-19 |
| ISO 10018:2020 | Guidance for people engagement. ISO 10018:2012 withdrawn | 2026-08-19 |
| New World Kirkpatrick Model | Four levels with Required Drivers; results-first design | 2026-08-19 |
| ISO 21502:2020 | §7.6 resources | 2026-08-19 |
| **Bangladesh Labour (Amendment) Ordinance 2025** | Ordinance No. 65 of 2025, gazetted 17 November 2025; §90A safety committee at 50+ workers; §61A right to refuse dangerous work; §332/§332A complaint committee | 2026-08-19 |
| **Bangladesh Labour (Amendment) Act 2026** | Parliamentary enactment; ~90 changes across the two instruments | 2026-08-19 |
| Bangladesh Labour Act 2006 | As amended by the above | 2026-08-19 |
| Bangladesh Labour Rules 2015 | **As amended 2022** | 2026-08-19 |

> **⚠ The four Bangladesh entries above supersede the citation carried by `TR-001` §4.9 and
> `AUDIT-009` `TR-01`.** Neither is wrong about the duty; both are unverified about the text.
> `TPD-Q-01` requires Legal confirmation before W0.

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Enterprise Architecture with Learning & Development | Initial issue. Supersedes `06-05` for the training half. First counted learner-hour and trainer-establishment model in the estate | ⬜ Blocked — `GV-001` `CC-01` |

---

*`CH-002` · Category 13 · 1000FiX ERP System v2.0 · CONFIDENTIAL — Internal Use Only*
