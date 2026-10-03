---
id: TR-020
title: Course Pack — Rider and Logistics
project: 1000FiX ERP System v2.0
content_type: Training course pack
template: TPL_Training_Course_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Development
author: Learning & Development with Logistics Operations
reviewers: [Logistics Manager, Operations Director, Finance Manager, HSE Lead, Quality Manager, Localisation Lead]
approver: Operations Director with Logistics Manager
content_class: D
purpose: >
  Trains 50–150 riders and 10–25 logistics coordinators on custody, proof of delivery and cash
  handling. A mobile, high-turnover, Bengali-speaking workforce carrying the company's
  highest-value uninsured exposure — devices in transit — and collecting cash at the door, with no
  supervisor present at any point in the transaction.
traces_to: [M03, M46, M50, M22, M59, P09, MD-005, MD-026, MD-045, TR-001, TR-002, TR-004, TR-006, TR-022, UI-019, SP-009, SP-019, SP-030, KB-013, KB-016, DT-005]
priority: P2
wave: W3
bilingual: yes
bn_counterpart: TR-020_Course_Pack_Rider_and_Logistics_BN.md
sources:
  - source: project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md — booking, packing standard, seal, custody transfer, transit exception handling, return; devices in transit are the company's highest-value uninsured exposure
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P09 riders operate one-handed, outdoors, offline, in Bengali; custody-break prevention depends on unambiguous scan and handover copy
    verified: 2026-08-17
    class: P1
  - source: project_content/07_Knowledge_Base_and_Technical_Library/KB-013_ESD_Chemical_and_Battery_Safety_Data.md §4.4 — damaged, defective or recalled lithium batteries are forbidden for transport by air and require controlled handling by road
    verified: 2026-08-17
    class: P1
  - source: project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-019_SOP_Cash_Collection_and_Banking.md — cash across 51+ branches and 50–150 riders is the highest fraud-risk process in the business
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# Course Pack — Rider and Logistics

| Item | Value |
|---|---|
| Audience role(s) | `R16` Rider / Delivery Agent · `R15` Logistics Coordinator |
| Headcount | **`R16` 50–150** · `R15` 10–25 |
| Duration | **Rider 4 hours** (on-device + practical) · **coordinator 6 hours** · plus 5 days supervised OJT |
| Delivery mode | **On-device microlearning in `P09`** plus branch practical; coordinator classroom |
| Language | **Bengali, authored in Bengali** (`LS-07`, `DS-17`) |
| Prerequisites | Layer 1 universal core — **including safety** · valid licence for `R16` |
| Certification outcome | Functional competence record (`TR-006` cell 13) |
| Wave | W3 |

> **The rider curriculum follows the `TR-009` model, not the classroom model.** High turnover, 51+
> locations, mixed literacy and a mobile workforce make cohort-based classroom delivery
> impractical. `PK-02` applies.

---

## 1. Learning Objectives

| # | On completion the learner can… | Assessed by |
|---|---|---|
| 1 | **Maintain unbroken custody** — scan, seal, transfer, record — for every device carried | Practical |
| 2 | Pack and seal to the standard for the device class, including hazard classes | **Critical practical** — `SP-009`, `KB-013` |
| 3 | Capture proof of delivery correctly, every time | Practical — `DT-005` |
| 4 | Work the manifest offline and know what has and has not synced | Offline practical |
| 5 | Handle a transit exception — damage, refusal, absence, wrong address, accident | Scenario |
| 6 | **Collect and reconcile cash to `SP-019`, and understand why the procedure protects them** | **Critical practical** |
| 7 | **Recognise a damaged battery consignment and apply the transport constraint** | **Critical items** — `KB-013` §4.4 |
| 8 | Conduct themselves at a customer's door to the standard expected | Role play |
| 9 | Report a safety incident, a vehicle defect or a road accident correctly | Items — `SP-030` |
| 10 | *(Coordinator)* Plan a manifest, manage exceptions and reconcile the day | Sandbox |

---

## 2. Curriculum Position

| Precedes | Follows | Refreshed every |
|---|---|---|
| Manifest assignment · cash-carrying authority · `P09` access | Layer 1 core including safety | On release (`TR-024`); **safety and cash annually** |

---

## 3. Module Outline

### 3.1 Rider — ~4 hours, ~28 on-device items plus practical

| Block | Items | Duration | Focus |
|---|---:|---|---|
| **A — Custody** | 6 | 40 min | Scan, seal, transfer, the unbroken chain |
| **B — Packing and hazard** | 5 | 35 min | Standards by device class; **damaged-battery constraint** |
| **C — The app offline** | 5 | 30 min | Manifest, sync, what is and is not saved |
| **D — Proof of delivery** | 4 | 25 min | Capture, signature, photograph, refusal |
| **E — Exceptions** | 4 | 30 min | Damage, absence, refusal, wrong address, accident |
| **F — Cash** | 5 | 35 min | Collection, limits, reconciliation, banking, shortfall |
| **G — Conduct and safety** | 4 | 30 min | At the door; road safety; incident reporting |
| | **~33 items** | **~3 h 45 min** | Plus a half-day branch practical |

### 3.2 Coordinator — 6 hours (`R15`)

Manifest planning and zone logic (`MD-005`) · capacity and vehicle assignment (`MD-045`) ·
exception management · custody oversight · **cash reconciliation across riders** · reverse-logistics
routing including the damaged-battery constraint · reporting.

---

## 4. Facilitator Guide

| Block | Talking points | Common misconceptions |
|---|---|---|
| A | **A custody break is not paperwork — it is the moment the company can no longer prove where a customer's device was.** Every scan is that proof | *"I know I had it."* |
| B | A swollen or damaged battery consignment cannot go by air and needs controlled handling by road (`KB-013` §4.4). **If you are unsure, do not carry it — ask** | *"It's just a phone."* |
| C | The sync indicator is the difference between a delivery recorded and a delivery disputed. **Check it before you leave the door** | *"It'll upload later."* |
| F | The cash procedure exists to protect **you**. A rider who follows it and is short is a process problem; one who does not is a suspicion | *"I'll settle it at the end of the week."* |
| G | You are alone at a customer's door. The conduct standard is what makes that safe for both of you | |
| G | A road accident is reported the same day, however minor. **Late reporting is the failure, not the accident** | *"It was only a scratch."* |

---

## 5. Participant Workbook Contents

**Delivered on-device** with a printed fallback. Custody scan sequence · **packing and seal standard
by device class** · **damaged-battery transport card** (from `KB-013`) · offline sync card ·
POD capture standard · exception decision aid · **cash limits and reconciliation card** · door
conduct card · incident reporting card · **my limits — what I may and may not accept**.

---

## 6. Exercises

| # | Exercise | System | Test data (`TS-002`) | Success criterion |
|---|---|---|---|---|
| 1 | **Custody chain on five consignments** | `P09` sandbox + physical | Manifest set | Chain unbroken; all scans present |
| 2 | **Pack and seal, including a hazard consignment** | Practical | Device set incl. an inert damaged-battery unit | Correct standard; **hazard consignment correctly refused or handled** |
| 3 | POD capture with a refusal | Sandbox | Delivery scenarios | Correct capture on both |
| 4 | **Full offline run then sync** | Sandbox, airplane mode | 6-stop manifest | All captured; rider can state what had not synced |
| 5 | Transit exception set | Scenario | Damage, absence, wrong address | Correct action and record on each |
| 6 | **Cash collection and reconciliation with a shortfall** | Practical | Cash scenario | Procedure followed; shortfall reported |
| 7 | Door conduct role play | Role play | Two customer types | Rubric pass |
| 8 | Incident reporting | Scenario | Minor road incident | Reported same day, correct route |
| 9 | *(Coordinator)* Plan and reconcile a day | Sandbox | Full day manifest | Manifest efficient; day reconciled |

---

## 7. Assessment

| Item | Weight | Pass mark | Attempts | Re-certification |
|---|---:|---:|---:|---|
| On-device block checks | 15% | 80% per block | Unlimited within block | On release |
| `TR-006` cell 13 form, 20 items | 15% | 80%, **100% on hazard and cash items** | 3 | 24 months |
| **Custody and packing practicals (1, 2)** | 25% | Both passed | 3 | 24 months |
| **Cash practical (6)** | 20% | Passed | 2 | **Annual** |
| Offline, POD, exceptions (3, 4, 5) | 15% | All passed | 3 | 24 months |
| Conduct and incident (7, 8) | 10% | Both passed | 3 | **Safety annually** |
| **OJT sign-off — 5 days, 20 consignments** | Gate | Logistics Coordinator | — | — |

---

## 8. Job Aids Produced

Custody scan sequence · **packing and seal standard card** · **damaged-battery transport card**
(sourced from `KB-013`, `CP-01`) · offline sync card · POD standard · exception decision aid ·
**cash limits and reconciliation card** · door conduct card · incident card. Rider cards live in the
`P09` offline pack; the hazard card is sourced from `KB-016`.

---

## 9. Trainer Requirements

**Bengali-native authors** for on-device content (`DS-17`) · branch practical assessor · **HSE
approval for blocks B and G** · Finance for the cash practical · `P09` sandbox · physical: sealable
packaging, an inert damaged-battery unit, cash scenario materials · **51+ locations means practicals
run regionally**.

---

## 10. Evaluation

| Level | Measure | Target |
|---|---|---|
| **Reaction** | Confidence handling an exception alone at a door | Diagnostic only (`LS-02`) |
| **Learning** | Block checks, practicals, cash practical | > 85% first attempt |
| **Behaviour** | **Custody breaks** · POD completeness · offline sync failures · **cash variance per rider** · incident reporting timeliness | **Custody breaks zero**; variance falling |
| **Result** | Transit loss and damage rate · **cash variance** · POD dispute rate · on-time delivery | Per `RP-001`, `SP-009` |

**Required Drivers** (`LS-04`): reinforce — offline cards in `P09` · encourage — coordinator rides
with each new rider on day one · monitor — custody, POD and cash telemetry per rider · reward —
competence record; cash-carrying authority.

---

## 11. Related Documents

[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md) ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-019_SOP_Cash_Collection_and_Banking.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-019_SOP_Cash_Collection_and_Banking.md) ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md) ·
`KB-013` §4.4 damaged-battery transport · `KB-016` offline cards · `UI-019` `P09` rider app copy ·
`DT-005` proof of delivery · [`../08A_Framework/TR-006_Question_Bank_Functional_Roles.md`](../08A_Framework/TR-006_Question_Bank_Functional_Roles.md) cell 13 ·
[`TR-009_Course_Pack_Field_Technician.md`](TR-009_Course_Pack_Field_Technician.md) — the on-device delivery model this pack follows.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The damaged-battery road-transport packaging standard does not exist** (`KB-013` `O-03`, `KB-006` `O-04`). Block B and exercise 2 teach a constraint with no defined compliant method | HSE Lead with Logistics | **W3 — blocking** |
| **O-02** | **`M22` mobile learning must be available inside `P09`**, as `TR-009` `O-02` requires for `P02`. Whether `P09` supports it is unconfirmed | CTO with L&D | **W3** |
| **O-03** | Bengali authoring capability (`TR-001` `O-05`) — same gap as `TR-009` | Localisation Lead | W3 |
| **O-04** | `TS-002` sandbox and physical practical materials do not exist | Test Lead with Logistics | W3 |
| **O-05** | **High rider turnover makes continuous intake essential**, but no continuous-enrolment process exists; the OJT demand on coordinators is uncosted | Logistics Manager with HR | W3 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Training_Course_Pack.md` — all ten sections in order; §11 and Open Items added per category convention
- [x] Objectives observable (`DS-02`); Level 4 measures named (`LS-01`)
- [x] On-device delivery model adopted for the rider population (`PK-02`), consistent with `TR-009`
- [x] Custody taught as evidence rather than paperwork
- [x] Damaged-battery transport constraint carried from `KB-013` as a critical item
- [x] Cash procedure framed as protecting the rider
- [x] Job-aid boundary respected — hazard card sourced from `KB-013`/`KB-016` (`CP-01`)
- [x] OJT sign-off gate present (`LS-03`); all four Required Drivers named (`LS-04`)
- [x] All internal links resolve
- [x] `P09` targets cited to `04-00`; `KB-013` §4.4 cited for the transport constraint
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` damaged-battery transport standard — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Operations Director and Logistics Manager**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
