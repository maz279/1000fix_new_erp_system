---
id: TR-005
title: Question Bank — Technician Certification
project: 1000FiX ERP System v2.0
content_type: Training course pack
template: TPL_Training_Course_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Technical with Learning & Development
author: Technical Services with L&D and Specialist Technicians (R12)
reviewers: [Quality Manager, Technical Director, HSE Lead, HR Director, Localisation Lead, Warranty Claims Officer]
approver: Technical Director with Quality Manager
content_class: C
purpose: >
  The item bank for L1, L2 and L3 technician certification by device family, with difficulty
  calibration, exposure control and rotation. Certification with a small static question set is
  certification in name only — and this certification gates brand warranty work through a hard
  business rule, so a bank that can be memorised in a week makes that block worthless.
traces_to: [M22, M02, M09, M31, MD-010, MD-011, MD-021, MD-024, MD-025, TR-001, TR-003, TR-004, TR-009, KB-004, KB-005, KB-006, KB-007, KB-013, SP-033]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: TR-005_Question_Bank_Technician_Certification_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M22 §5.2 FR-LMS-009…016 certification register and lapse handling; §5.3 FR-LMS-026 assessment delivery with pass criteria, attempt limits and result recording
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-09 assignment blocked without current brand certification; BRU-SRM-14 L3 board-level repairs only at an equipped workshop by a certified specialist; BRU-HRM-01 expiry blocks assignment
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 — KPI-062 certifications current 100%, KPI-063 claims rejected for uncertified technician zero
    verified: 2026-08-17
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md §2.1 — five device families DF-IT, DF-HA, DF-MB, DF-SRV, DF-SEC; repair_level_required enum L1 / L2 / L3_board
    verified: 2026-08-17
    class: P1
  - source: Classical item-analysis practice — item difficulty (proportion answering correctly) and item discrimination (whether an item separates stronger from weaker candidates) are computed from live response data; items that do not discriminate are revised or retired regardless of how reasonable they appear
    verified: 2026-08-17
    class: P3
supersedes: none
review_due: 2027-02-17
---

# Course Pack — Question Bank: Technician Certification

| Item | Value |
|---|---|
| Audience role(s) | `R10` Senior Technician · `R11` Junior Technician · `R12` Specialist Technician |
| Headcount | **200–400 technicians** |
| Duration | Assessment 45–90 minutes per certification attempt; the bank itself is not a taught course |
| Delivery mode | System-delivered assessment, `M22` FR-LMS-026 · mobile-capable for field technicians |
| Language | **Bengali primary**, English parallel (`LS-07`, `DS-17`) |
| Prerequisites | `TR-009` Field Technician pack · Layer 1 universal core (`TR-002` §4.2) · practical component per `AS-03` |
| Certification outcome | Internal technical certification at `L1` / `L2` / `L3_board` per device family, registered in `MD-011` |
| Wave | W2 |

> **Template conformance.** This file uses `TPL_Training_Course_Pack.md` as `CG-009` §3 requires,
> applied to an **assessment instrument rather than a taught course**. All ten template sections are
> retained in order and answered at bank level — §3 becomes the bank blueprint, §4 the item-writing
> guide, §6 the practical components. Sections 11–13 are justified additions. The underlying issue —
> that the template has no assessment-instrument variant — is the same defect `AUDIT-008` KB-10
> raised for `TPL_Knowledge_Article.md`, and is reported rather than resolved here.

---

## 1. Learning Objectives

**An item bank has no learning objectives of its own; it evidences the objectives of the courses it
assesses.** The objectives below are what the bank must be able to *discriminate on* — the ability
to separate a technician who holds the competence from one who does not.

| # | The bank must discriminate whether the technician can… | Assessed by |
|---|---|---|
| 1 | Identify a hazard before diagnosis and take the correct isolation action | Safety items — **100% required** (`AS-04`) |
| 2 | Select the correct diagnostic path for a presented symptom on a given device family | Scenario items keyed to `SP-033` and `KB-004`…`KB-007` |
| 3 | Interpret a manufacturer code and map it to the internal taxonomy | Items keyed to `KB-008` and `MD-024` |
| 4 | Decide whether a part substitution is permitted on this job | Items keyed to `KB-009` §5 and §6.4 |
| 5 | Apply the correct `MD-025` resolution coding to a completed repair | Coding items |
| 6 | Recognise when to stop and escalate, and with what evidence | Escalation items keyed to `SP-005` |
| 7 | Apply the business rules that block or gate their work | Items keyed to `BRU-SRM-06`/`-07`/`-09`/`-11`/`-12`/`-14` |
| 8 | Perform the repair to standard | **Practical demonstration** — not an item (`AS-03`) |
| 9 | Handle customer data and device identity lawfully | Items keyed to `SP-012`, `KB-006` §6.1 |
| 10 | Work within their level and recognise its boundary | Level-boundary items |

**`QB-01`: every item traces to a governing `KB`, `SP`, `MD` or `05-05` source.** An item with no
source is an opinion, and a technician who fails it has been failed by an opinion.

---

## 2. Curriculum Position

| Precedes | Follows | Refreshed every |
|---|---|---|
| `MD-011` certification record · assignment eligibility (`M22` FR-LMS-039) · brand warranty work | `TR-009` Field Technician pack · Layer 1 core · supervised practice | **Bank reviewed every 6 months; certification re-taken every 24 months** (`AS-20`) |

**Certification is per (device family × level).** A technician certified `L2` on `DF-MB` is not
thereby certified `L1` on `DF-HA` — the families are genuinely different work.

---

## 3. Module Outline — *the bank blueprint*

**`QB-02`: the bank is organised as a blueprint of cells, and every assessment form is drawn to the
blueprint, never assembled ad hoc.**

### 3.1 Cells

| Device family | `L1` | `L2` | `L3_board` | Cells |
|---|:--:|:--:|:--:|---:|
| `DF-IT` IT and computing | ✔ | ✔ | ✔ | 3 |
| `DF-HA` Home appliance | ✔ | ✔ | — *(board-level appliance work is out of the serviced range)* | 2 |
| `DF-MB` Mobile and tablet | ✔ | ✔ | ✔ | 3 |
| `DF-SRV` Server, storage and network | — *(no `L1` entry point)* | ✔ | ✔ | 2 |
| `DF-SEC` CCTV and security | — | ✔ | ✔ | 2 |
| | | | **Total** | **12** |

### 3.2 Form composition per cell

| Competence area | Share of form | Items on a 40-item form | Critical? |
|---|---:|---:|:--:|
| **Safety and hazard** | 20% | 8 | **✔ 100% required** |
| Diagnosis and symptom-to-fault | 25% | 10 | |
| Repair procedure and technique | 15% | 6 | |
| Parts, compatibility and substitution | 10% | 4 | **Prohibited-substitution items critical** |
| Codes — fault, resolution, manufacturer | 10% | 4 | |
| **Business rules and escalation** | 10% | 4 | **✔ hard-rule items critical** |
| Customer, data and device identity | 10% | 4 | **✔ IMEI item critical on `DF-MB`** |

**Form length: 40 items. Pass: 80% overall, 100% on every declared critical item** (`AS-04`,
`AS-05`).

### 3.3 Bank size — the honest arithmetic

**`QB-03`: a bank must be large enough that a form cannot be reconstructed from experience.** The
register's own justification says a small static set is "certification in name only". The size that
follows is uncomfortable and is stated rather than avoided:

| Driver | Value |
|---|---|
| Form length | 40 items |
| Exposure ratio required for meaningful rotation | **6× to 8× form length per cell** |
| Items per cell | **240–320** |
| Cells | 12 |
| **Total bank at steady state** | **~2,900–3,800 items** |
| Plus retired/replacement churn at ~15% a year | ~450–570 items a year |

**This is a very large authoring commitment and it is not resourced.** §12 states the position.

**`QB-04`: a minimum viable bank is 3× form length per cell (120 items), and a cell below that
threshold cannot issue a gating certification.** Below 3× the same items recur within a cohort and
the assessment measures recall of the form rather than competence.

---

## 4. Facilitator Guide — *item-writing rules*

There is no facilitator. This section carries the rules for the people who write items.

| # | Rule | Class |
|---|---|:--:|
| **QB-01** | Every item traces to a governing `KB`, `SP`, `MD` or `05-05` source | **H** |
| **QB-05** | Items test **application, not recall of wording**. "What does `BRU-SRM-12` say?" is a bad item; "A device appears beyond economic repair. What must happen before you tell the customer?" is a good one | **H** |
| **QB-06** | Every distractor is **plausible to someone who half-knows the material** — drawn from real errors in `M31` rework and `M09` claim-rejection data where available | **H** |
| **QB-07** | No trick items, no double negatives, no "all of the above", no items whose difficulty comes from the wording | **H** |
| **QB-08** | Safety items have **one unambiguously correct answer**; no "best answer" judgement on a hazard | **H** |
| **QB-09** | Items are written in **Bengali first** by a Bengali-speaking technical author, then rendered in English (`DS-17`) | **H** |
| **QB-10** | Codes, part numbers, model names, measurements and error IDs are never translated (`DS-20`) | **H** |
| **QB-11** | An item is scoped to a device family and a level, and is not reused across cells without re-calibration | **H** |
| **QB-12** | Item length is bounded — a technician reads on a phone; a scenario longer than a short paragraph is testing reading, not competence | **S** |
| **QB-13** | No item depends on a model-specific value (a torque figure, a rail voltage) unless that value is in the offline pack the technician carries | **H** |
| **QB-14** | Items are reviewed by an `R12` who did not write them, and safety items additionally by HSE (`DS-26`, `BRU-KMS-03` pattern) | **H** |
| **QB-15** | Every item carries its author, reviewer, source, cell, and first-use date | **H** |

> **`QB-06` deserves emphasis.** The quality of a multiple-choice item lives entirely in its
> distractors. Distractors invented at the desk are obviously wrong and the item tests nothing.
> Distractors drawn from **what technicians actually got wrong** — the rework records, the rejected
> claims, the known-issue register — produce items that discriminate. `KB-011` and `M09` are the
> two richest sources the company has, and they cost nothing to mine.

---

## 5. Participant Workbook Contents

| Section | Purpose |
|---|---|
| What the certification covers and does not | Sets expectation; states the (family × level) scope |
| The competence areas and their weights (§3.2) | A candidate should know what is being assessed |
| **The declared critical areas** | `AS-05` requires critical items to be declared before use — the *areas* are published even though the items are not |
| Practical component — what will be observed | `AS-03` |
| Pass standard, attempts, remediation | From `TR-004` §4.3–§4.4 |
| Re-certification interval and renewal alerts | `AS-10` — no grace period |
| Appeal route | `AS-18` |
| Preparation guidance — which `KB` and `SP` files to work through | Links to the governing library |

**`QB-16`: the workbook publishes the blueprint but never the items.** Publishing weights and areas
makes the assessment fair; publishing items makes it worthless.

---

## 6. Exercises — *the practical component*

`AS-03` prohibits a gating certification on a written bank alone. Every technician certification
therefore has a practical component, assessed by a qualified assessor (`AS-16`).

| # | Practical | System / sandbox | Test data (`TS-002`) | Success criterion |
|---|---|---|---|---|
| 1 | **Hazard identification and isolation** on a presented device | Bench | Prepared units including a swollen cell and a liquid-damaged unit | Correct hazard identified and isolated **before** any diagnostic action — `KB-013` §4 |
| 2 | Diagnose a seeded fault to a coded outcome | Bench + `P02` sandbox | Seeded fault units per family | Correct `FLT-` code, or an honest `FLT-UNK` with a route (`SP-033` `DT-02`) |
| 3 | Complete the repair to the article's verification criterion | Bench | Parts issued from sandbox stock | Verification test passed and recorded (`KB-004`…`KB-007` §8) |
| 4 | Record the job — codes, parts, evidence, time | `P02` sandbox | Sandbox job | Complete and correct; `RES-01`/`RES-02` satisfied |
| 5 | **Escalation decision** on an out-of-level fault | Scenario + `P02` | Seeded L3 fault presented to an L1/L2 candidate | **Escalates rather than attempts** — `BRU-SRM-14` |
| 6 | Substitution decision under stock-out pressure | Scenario | Parts scenario | Applies `KB-009` §5 sequence; refuses a prohibited substitution |

**`QB-17`: exercise 5 is the single most important practical item.** A technician who attempts work
above their level is the failure mode `BRU-SRM-14` exists to prevent, and it cannot be assessed by
asking whether they know the rule.

---

## 7. Assessment

| Item | Weight | Pass mark | Attempts | Re-certification interval |
|---|---:|---:|---:|---|
| Written form, 40 items | 60% | **80% overall, 100% on critical** | 3 (2 for safety-critical failure) | 24 months |
| Practical, 6 components | 40% | **All six passed** | 3, with supervised practice between | 24 months |
| **Both must pass independently** | — | — | — | — |

> Conforms to [`TR-004_Assessment_and_Certification_Policy.md`](TR-004_Assessment_and_Certification_Policy.md). Brand certification, where a brand
> states its own requirement, **overrides these figures for that brand's warranty work** (`AS-04`,
> `TR-004` `O-01`).

### 7.1 Calibration and item analysis

**`QB-18`: every item carries a live difficulty and discrimination statistic, and items that do not
discriminate are revised or retired regardless of how reasonable they look.**

| Statistic | Computed as | Action threshold |
|---|---|---|
| **Difficulty** | Proportion of candidates answering correctly | Below 0.20 or above 0.95 → review. **An item everyone passes measures nothing** |
| **Discrimination** | Whether stronger candidates outperform weaker ones on the item | Negative or near-zero → **retire**; the item is measuring something other than competence |
| Distractor performance | How often each wrong option is chosen | A distractor never chosen is dead weight — replace it |
| Exposure count | Times served | Above the cell threshold → rotate out |
| Time to answer | Median seconds | Outliers indicate ambiguity |

**`QB-19`: no item enters live gating use until it has been piloted** — carried unscored on a form
until it has enough responses to calibrate.

### 7.2 Exposure control and rotation

| Control | Rule |
|---|---|
| Form generation | Drawn to the §3.2 blueprint at attempt time; **no two candidates in a cohort receive the same form** |
| Rotation | Items rotate out at the cell exposure threshold |
| Retirement on exposure | An item found circulating is retired immediately, not at review (`AS-17`) |
| Re-attempt forms | **A re-attempt draws a different form** — otherwise attempt 2 measures memory of attempt 1 |
| Integrity breach | Invalidates the certification and triggers review of the work done under it (`AS-17`) |

---

## 8. Job Aids Produced

| Job aid | Format | Where it lives |
|---|---|---|
| Certification scope card — what my level permits | One screen, bilingual | `P02` offline pack via `KB-016` |
| Renewal timeline — the 90/45/14-day alerts | One page | `TR-022` |
| Escalation boundary card — when I must not proceed | One screen | `KB-016` layer 2 |

**`QB-20`: the bank produces no job aid containing item content.** A revision aid built from the
bank is the bank, published.

---

## 9. Trainer Requirements

| Requirement | Detail |
|---|---|
| **Item authors** | `R12` Specialist Technicians with current competence in the cell they write for |
| **Item reviewers** | A different `R12`; HSE additionally for safety items (`QB-14`) |
| **Practical assessors** | Qualified **above** the level being assessed (`AS-16`); for `L3_board` this is the `R12` population |
| Bengali authoring | Technical author who is Bengali-native (`QB-09`) — capability gap, `TR-001` `O-05` |
| Psychometric support | Someone must own difficulty and discrimination analysis (§7.1). **No such role exists** — §12 `O-03` |
| Assessor calibration | Annual; second-assessor sampling on gating certifications (`TR-004` §4.9) |

---

## 10. Evaluation

| Level | Measure | Target |
|---|---|---|
| **Reaction** | Candidate perception of fairness and relevance | Collected; **diagnostic only** (`LS-02`) |
| **Learning** | First-attempt pass rate per cell | Monitored; **near-100% triggers instrument review** (`AS-06`) |
| **Behaviour** | Rework rate and escalation-appropriateness of newly certified technicians vs the population | Newly certified not materially worse |
| **Result** | **`KPI-063` claims rejected for an uncertified technician — target zero** · `KPI-062` certifications current 100% · contribution to `KPI-004` first-time fix | Per `06-02` |

**Required Drivers** (`LS-04`): reinforce — `KB-016` scope card · encourage — supervisor practice
time before re-attempt · monitor — item analysis and rework linkage · reward — `MD-011` record
unlocking brand assignment.

---

## 11. Bank Governance *(addition — justified: `AS-21` requires every certification to map to `MD-011` and the bank's own lifecycle has no home in the template)*

| Aspect | Rule |
|---|---|
| Item code | `ITM-nnnnn`, permanent, never reused |
| Ownership | Technical Director owns content; L&D owns instrument quality |
| Change control | An item may be edited before pilot; **after live use it is retired and replaced, not edited** — editing invalidates its statistics |
| Review cadence | **6-monthly** per cell, and immediately on: a `KB-010` bulletin affecting the content, a `KB-011` known issue, an `MD-024`/`MD-025` taxonomy change, a safety incident, or a `KB-013` hazard-control change |
| Retirement | On exposure, on failed discrimination, on source supersession, or on device-family withdrawal |
| Bengali parity | An item is not live until both languages are signed off in context (`BN-018`) |
| Storage | In `M22`; **the bank is never held in a document, a spreadsheet or a shared drive** |
| Access | Item authors and reviewers only; **not visible to trainers who prepare candidates** |

---

## 12. Effort, Coverage and the Resourcing Position *(addition — justified: consistent with the `KB` category convention; a bank of this size cannot be assumed)*

| Item | Position |
|---|---|
| Items required, steady state | **~2,900–3,800** across 12 cells |
| **Minimum viable to issue any gating certification** | **120 per cell × 12 = ~1,440** (`QB-04`) |
| Items written | **0** |
| Authoring rate, realistic | 4–8 calibrated items per `R12` hour including review |
| **Effort to minimum viable** | **~180–360 `R12` hours**, plus HSE review on safety items and Bengali authoring |
| Effort to steady state | ~360–950 `R12` hours |
| Annual churn | ~450–570 items, ~60–140 hours a year, **perpetual** |
| Author population | **15–30 `R12` specialists** (`05-04`) — the same people authoring 160 `KB` articles (`AUDIT-008` R-07) and doing the hardest repairs |

> **The collision is worth stating plainly.** `AUDIT-008` R-07 already records 775–1,545 specialist
> hours owed to Category 07. This file adds 180–360 hours minimum. **The same 15–30 people owe both,
> and they are also the company's board-level repair capability.** No plan that treats these as
> independent commitments is real.

---

## 13. Related Documents *(addition — justified: category convention)*

| Document | Relationship |
|---|---|
| [`TR-004_Assessment_and_Certification_Policy.md`](TR-004_Assessment_and_Certification_Policy.md) | The policy this instrument implements |
| [`TR-003_Course_Design_Standard_and_Storyboard_Template.md`](TR-003_Course_Design_Standard_and_Storyboard_Template.md) | `DS-01` — assessment designed before content |
| [`../08B_Course_Packs/TR-009_Course_Pack_Field_Technician.md`](../08B_Course_Packs/TR-009_Course_Pack_Field_Technician.md) | The course this bank certifies |
| [`TR-006_Question_Bank_Functional_Roles.md`](TR-006_Question_Bank_Functional_Roles.md) | The parallel bank for non-technical roles |
| `KB-004`…`KB-007` troubleshooting guide sets | Item sources for diagnosis and repair |
| `KB-008` fault codes · `KB-009` parts · `KB-011` known issues · `KB-013` safety data | Item sources; `KB-011` and `M09` supply distractors (`QB-06`) |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md) | Where the outcome is registered (`AS-21`) |
| [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md) | Diagnostic scenario source |
| `M22` FR-LMS-026 | Assessment delivery |
| `M02` | Consumes eligibility; enforces `BRU-SRM-09` |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The bank is empty.** ~1,440 items minimum before any gating certification can be issued, and `BRU-SRM-09` blocks brand warranty assignment without one. **W2 is not achievable at current resourcing** | Technical Director with PMO | **W2 — and it will slip** |
| **O-02** | **The `KB` guide sets that supply item content are themselves unwritten** (`AUDIT-008` KB-04, O-01 across `KB-004`…`KB-007`). `QB-01` requires every item to trace to a source; the sources do not exist | Technical Director | **Before item authoring** |
| **O-03** | **Nobody owns item analysis.** §7.1 requires difficulty and discrimination statistics; no role in `05-04` has psychometric responsibility and `M22` FR-LMS-026 does not state that it computes them | L&D with CTO | **W2 — `QB-18` is inoperable without it** |
| **O-04** | Whether `M22` supports blueprint-driven form generation with exposure control (§7.2) is unconfirmed. If it serves a fixed form, rotation is impossible and `QB-03` cannot be met | CTO with L&D | **Before `M22` build** |
| **O-05** | The `DF-HA` `L3_board` cell is excluded on the assumption that board-level appliance work is out of the serviced range. **`MD-021` is unpopulated** (`AUDIT-008` KB-11), so the assumption is unverified | Technical Director with MDM | Before blueprint is fixed |
| **O-06** | Practical assessment (§6) requires prepared fault units, including deliberately hazardous ones. **Sourcing, storing and safely presenting a swollen cell for assessment has no procedure** | HSE Lead with Technical Director | **W2 — before practical assessment runs** |
| **O-07** | Bengali item authoring (`QB-09`) depends on the technical terminology gap `TR-001` `O-05` and `KB-002` `O-05` record | Localisation Lead with Technical Director | **W2** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Training_Course_Pack.md` — all ten sections retained in order, bank-level interpretation stated, additions §11–§13 justified
- [x] Blueprint defined as cells (device family × level) with form composition and weights
- [x] **Bank size computed honestly rather than asserted**, with a minimum viable threshold (`QB-04`)
- [x] Item-writing rules test application not recall, and require distractors drawn from real error data
- [x] Safety items required to have one unambiguously correct answer (`QB-08`)
- [x] Practical component mandatory, with the out-of-level escalation exercise identified as the most important
- [x] Difficulty and discrimination made live controls, with retirement on failed discrimination
- [x] Exposure control and different-form re-attempt specified
- [x] Bengali-first authoring required (`QB-09`)
- [x] Effort stated and the collision with the Category 07 specialist commitment named
- [x] All internal links resolve
- [x] `BRU-SRM-09`/`-14`, `BRU-HRM-01` cited to `05-05`; `FR-LMS-*` to `M22`; `KPI-062`/`-063` to `06-02`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` bank authored to minimum viable — outstanding; blocks brand warranty certification**
- [ ] **`O-03` item analysis ownership — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Technical Director and Quality Manager**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
