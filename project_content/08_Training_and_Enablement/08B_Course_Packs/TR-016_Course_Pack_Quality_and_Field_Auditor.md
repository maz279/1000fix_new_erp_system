---
id: TR-016
title: Course Pack — Quality and Field Auditor
project: 1000FiX ERP System v2.0
content_type: Training course pack
template: TPL_Training_Course_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Development with Quality
author: Learning & Development with Quality Management
reviewers: [Quality Manager, Operations Director, Technical Director, HSE Lead, Legal Counsel, Data Services Lead, Localisation Lead]
approver: Quality Manager with Operations Director
content_class: D
purpose: >
  Trains quality staff and field auditors to classify findings consistently. Consistent
  classification across many auditors is what makes audit data usable — twenty auditors each
  classifying by personal judgement produce a dataset that cannot be aggregated, trended or acted
  on, and an ISO surveillance audit that tests the process directly will find it.
traces_to: [M23, M22, M06, M59, M61, P03, P11, MD-026, MD-046, TR-001, TR-002, TR-004, TR-006, TR-022, UI-031, UI-021, SP-012, SP-029, SP-030, KB-011, KB-012, LG-022]
priority: P2
wave: W5
bilingual: yes
bn_counterpart: TR-016_Course_Pack_Quality_and_Field_Auditor_BN.md
sources:
  - source: project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md — audit programme, execution, finding classification, CAPA assignment, verification, closure; finding-to-CAPA cycle-time target under 5 days
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-QMS-01 a checklist cannot be marked complete with unanswered mandatory items; BRU-QMS-02 every non-conformance requires a root cause and a CAPA before closure; BRU-QMS-03 CAPA closure requires effectiveness verification; BRU-QMS-05 repeated non-conformance triggers a management review item
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 — KPI-066 CAPA closed on time 90% then 95%; KPI-067 ISO major non-conformances zero; KPI-068 internal audit plan completion 100%
    verified: 2026-08-17
    class: P1
  - source: ISO 9001:2015 clauses 7.2 competence, 9.2 internal audit and 10.2 nonconformity and corrective action
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# Course Pack — Quality and Field Auditor

| Item | Value |
|---|---|
| Audience role(s) | `R32` Quality Manager / ISO Coordinator · **field auditors using `P11` — see §1.1** · **`R14` Data Services Technician (delta, `TR-002` §7.4)** |
| Headcount | `R32` 2–4 · field auditors 20–60 *(population unregistered — `TR-002` `O-05`)* · `R14` 5–12 |
| Duration | **Core 8 hours** · auditor calibration 4 h · **data-services delta 4 h** |
| Delivery mode | Classroom with `P11` sandbox; calibration workshop |
| Language | Bengali primary for field auditors; English acceptable for `R32` |
| Prerequisites | Layer 1 universal core |
| Certification outcome | Functional competence record (`TR-006` cell 10) |
| Wave | W5 |

## 1.1 A register discrepancy carried into this pack

**The register describes this pack's audience as "20–60 auditors", but `05-04` registers only
`R32` Quality Manager at 2–4 people.** The 20–60 field auditors who use `P11` are not a registered
role — the same `00-07` H2-07 defect `MD-009` exists to resolve. `CU-01` prevents `TR-002` from
assigning them a curriculum. This pack is written for both populations, and the register gap is
raised as `TR-002` `O-05` and audit finding **TR-07**.

> **This pack also carries `R14` Data Services Technician** as an interim route under `TR-002`
> §7.4, because no pack exists for `SP-012`. `CU-16` requires the compromise to be declared; §3.4
> declares it.

---

## 1. Learning Objectives

| # | On completion the learner can… | Assessed by |
|---|---|---|
| 1 | Execute an audit to the programme plan, on `P11`, with evidence captured | Practical |
| 2 | **Classify a finding consistently with other auditors** | **Calibration exercise — the pack's core purpose** |
| 3 | Distinguish a non-conformance from an observation from an opportunity | Calibration + items |
| 4 | Establish root cause rather than restating the symptom | Practical — `BRU-QMS-02` |
| 5 | Assign a CAPA that is specific, owned and verifiable | Practical |
| 6 | **Verify CAPA effectiveness before closure** | Items — `BRU-QMS-03` |
| 7 | Recognise a repeated non-conformance and escalate to management review | Items — `BRU-QMS-05` |
| 8 | Complete a checklist correctly, with no unanswered mandatory item | Practical — `BRU-QMS-01` |
| 9 | Recognise when a quality finding is a **safety** matter and route it immediately | **Critical items** — `SP-030` |
| 10 | Distinguish a device defect (`KB-011`) from our own practice failure (`M23`) | Scenario — `KW-05` |
| 11 | *(Data services delta)* Operate chain of custody, isolated environment and destruction certification to `SP-012` | **Critical practical** |

---

## 2. Curriculum Position

| Precedes | Follows | Refreshed every |
|---|---|---|
| Audit authority · CAPA assignment · `P11` access | Layer 1 core | On release; **calibration every 6 months** (§3.3) |

---

## 3. Module Outline

### 3.1 Core — 8 hours

| # | Module | Duration | Method |
|---:|---|---|---|
| 1 | Why classification consistency is the whole value of audit data | 30 min | Facilitated |
| 2 | The audit programme, `P11` and evidence capture | 75 min | Walkthrough — `UI-021` |
| 3 | **Finding classification — the definitions and the boundaries** | 90 min | Practice |
| 4 | **Root cause — techniques and the restatement trap** | 90 min | Practice — `BRU-QMS-02` |
| 5 | CAPA — specific, owned, dated, verifiable | 60 min | Practice |
| 6 | **Effectiveness verification before closure** | 45 min | Items — `BRU-QMS-03` |
| 7 | Repeated non-conformance and management review | 30 min | Items — `BRU-QMS-05` |
| 8 | Checklists and mandatory items | 30 min | Practical — `BRU-QMS-01` |
| 9 | **When a quality finding is a safety finding** | 45 min | Scenario — `SP-030` |
| 10 | Device defect vs our practice — `KB-011` and `M23` | 45 min | Scenario — `KW-05` |
| 11 | Quality console and reporting | 30 min | Walkthrough — `UI-031` |
| | **Total** | **~8 hours** | |

### 3.2 Auditor calibration workshop — 4 hours

**`PK-07`: calibration is not optional and is not a one-off.** Auditors classify the same twelve
prepared cases independently, then reconcile. **Agreement is measured**, and the exercise repeats
every six months.

### 3.3 Data services delta — 4 hours (`R14`) — *declared interim route*

Chain of custody · isolated environment and access restriction (`05-04` T5) · evidence handling ·
**certified destruction and the certificate** (`BRU-ESG-01`) · customer consent · what may never be
accessed. **`PK-08`: this is an interim control, not equivalence** — `R14` handles the most
sensitive data in the company and a quality pack is not designed for it. Gap: `TR-002` `O-03`.

---

## 4. Facilitator Guide

| Module | Talking points | Common misconceptions |
|---|---|---|
| 1 | Twenty auditors classifying by instinct produce twenty datasets. **The classification standard is the deliverable, not the audit** | *"I know a non-conformance when I see one."* |
| 3 | The boundary between non-conformance and observation is where consistency fails first | *"If it's minor I'll call it an observation."* |
| 4 | "Operator error" is a symptom restated, not a root cause. Ask why the process permitted it | *"Root cause: the technician didn't follow the SOP."* |
| 6 | A CAPA closed without effectiveness verification is a CAPA that will recur (`BRU-QMS-03`). **ISO surveillance tests this directly** | *"They said they fixed it."* |
| 9 | A quality finding that is also a safety hazard goes to HSE **immediately**, not at report issue | *"It'll be in the report."* |
| 10 | If the fault is in the device, it is `KB-011`. If the fault is in what we did, it is a non-conformance. **Confusing them sends the wrong evidence to the wrong place** | *"Same model keeps failing, so it's a supplier issue."* — sometimes it is us |

---

## 5. Participant Workbook Contents

Audit programme and plan · **finding classification definitions with boundary examples** · root
cause techniques and the restatement trap · CAPA quality criteria · effectiveness verification
guide · repeated-NC escalation · checklist rules · **safety-routing card** · `KB-011` vs `M23`
decision aid · *(delta)* **custody and destruction checklist** · **my access scope**.

---

## 6. Exercises

| # | Exercise | System | Test data (`TS-002`) | Success criterion |
|---|---|---|---|---|
| 1 | Conduct a branch audit on `P11` | `P11` sandbox | Seeded branch | Evidence captured; checklist complete |
| 2 | **Classify twelve prepared findings independently** | Calibration | Prepared case set | **Agreement with the reference classification and with peers measured** |
| 3 | Root cause on three findings | Practice | NC set | No symptom restatement |
| 4 | Write three CAPAs | Practice | From exercise 3 | Specific, owned, dated, verifiable |
| 5 | **Effectiveness verification** | Scenario | CAPA claimed complete | Verifies rather than accepts; closes or reopens correctly |
| 6 | Repeated NC recognition | Scenario | Pattern across three audits | Escalates to management review |
| 7 | **Safety routing** | Scenario | Quality finding that is a hazard | Routed to HSE immediately |
| 8 | Device defect vs practice failure | Scenario | Recurring model failure | Correct routing to `KB-011` or `M23` |
| 9 | *(Delta)* Custody and destruction | Practical | Device with customer data | Custody unbroken; certificate produced |

---

## 7. Assessment

| Item | Weight | Pass mark | Attempts | Re-certification |
|---|---:|---:|---:|---|
| `TR-006` cell 10 form, 30 items | 25% | 80%, **100% on safety-routing items** | 3 | 24 months |
| **Calibration agreement (exercise 2)** | 30% | **Agreement above the declared threshold** | Repeat until met | **Every 6 months** |
| Root cause and CAPA (3, 4, 5) | 25% | All passed | 3 | 24 months |
| Audit execution (1), routing (7, 8) | 20% | All passed | 3 | 24 months |
| *(Delta)* exercise 9 | Gate for `R14` | Passed | 2 | Annual |
| **OJT sign-off — 3 audits observed** | Gate | Quality Manager | — | — |

---

## 8. Job Aids Produced

**Finding classification card with boundary examples** · root cause prompt card · CAPA quality
checklist · effectiveness verification guide · **safety-routing card** · `KB-011` vs `M23` decision
aid · *(delta)* custody and destruction checklist. All in `TR-022`.

---

## 9. Trainer Requirements

L&D with **Quality Manager delivering modules 1, 3, 4 and 6** · HSE for module 9 · **Data Services
Lead and Legal for the delta** · `P11` sandbox with seeded branches · **prepared calibration case
set — the most important training asset in this pack** · cohort maximum 15.

---

## 10. Evaluation

| Level | Measure | Target |
|---|---|---|
| **Reaction** | Confidence classifying a borderline finding | Diagnostic only (`LS-02`) |
| **Learning** | Assessment and **calibration agreement rate** | Agreement above threshold; **rising across cycles** |
| **Behaviour** | Classification consistency across auditors in live audits · root-cause quality · CAPA reopen rate · safety findings routed same-day | Consistency rising; reopens falling |
| **Result** | **`KPI-066` CAPA closed on time 90% then 95%** · **`KPI-067` ISO major non-conformances zero** · `KPI-068` audit plan completion 100% · finding-to-CAPA cycle under 5 days | Per `06-02`, `SP-029` |

**Required Drivers** (`LS-04`): reinforce — classification card in the field · encourage —
**six-monthly calibration is itself the encouragement mechanism** · monitor — inter-auditor
consistency measured on live findings · reward — competence record; audit data that is actually
used.

---

## 11. Related Documents

[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md) *(delta)* ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md) ·
`KB-011` known issues — `KW-05` boundary · `KB-012` equipment calibration ·
`UI-031` quality console · `UI-021` `P11` auditor app · `LG-022` quality policy ·
[`../08A_Framework/TR-006_Question_Bank_Functional_Roles.md`](../08A_Framework/TR-006_Question_Bank_Functional_Roles.md) cell 10.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The calibration case set does not exist** and is the single most important asset in this pack. It requires twelve prepared findings with reference classifications agreed by the Quality Manager | Quality Manager with L&D | **W5 — blocking module 3.2** |
| **O-02** | **The 20–60 field auditors are not a registered role** (`TR-002` `O-05`, finding TR-07). `CU-01` blocks curriculum assignment; they can be trained but not systematically assigned | MDM with Quality Manager | **W5** |
| **O-03** | **The `R14` delta (§3.4) is an interim control** covering the most sensitive data the company handles. A proper route is needed (`TR-002` `O-03`) | Training Lead with Data Services and Legal | W2 — **`R14` works from W2, not W5** |
| **O-04** | `TS-002` and a `P11` sandbox with seeded branches do not exist | Test Lead with Quality | W5 |
| **O-05** | The calibration agreement threshold is undeclared. `AS-05` requires standards to be declared before use | Quality Manager | Before first calibration |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Training_Course_Pack.md` — all ten sections in order; §11 and Open Items added per category convention
- [x] Objectives observable (`DS-02`); Level 4 KPIs named (`LS-01`)
- [x] **Classification consistency identified as the pack's core purpose, with calibration as a recurring assessed component (`PK-07`)**
- [x] Root-cause restatement trap taught explicitly
- [x] CAPA effectiveness verification taught as the ISO-tested control
- [x] Safety routing made a critical, immediate-action competence
- [x] `KB-011` versus `M23` boundary taught (`KW-05`)
- [x] **`R14` interim route declared (`PK-08`, `CU-16`); register discrepancy on the auditor population declared in §1.1**
- [x] OJT sign-off gate present (`LS-03`); all four Required Drivers named (`LS-04`)
- [x] All internal links resolve
- [x] `BRU-QMS-01`…`-05`, `BRU-ESG-01` cited to `05-05`; `KPI-066`…`-068` to `06-02`; ISO clauses cited specifically
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` calibration case set — outstanding; the pack's core exercise cannot run**
- [ ] **`O-03` `R14` needs a route at W2, not W5 — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Quality Manager and Operations Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
