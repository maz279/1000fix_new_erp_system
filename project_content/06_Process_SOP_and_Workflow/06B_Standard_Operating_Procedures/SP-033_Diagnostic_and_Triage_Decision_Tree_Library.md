---
id: SP-033
title: Diagnostic and Triage Decision Tree Library
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Technical
author: Business Process Lead with Technical Services
reviewers: [Operations Director, Quality Manager, CTO, Contact Centre Supervisors, Knowledge Manager, Localisation Lead]
approver: Operations Director with Quality Manager
content_class: C
purpose: >
  Structured decision trees by device family for intake triage, remote triage and bench
  diagnosis. They drive the guided diagnostic in the technician application, the AI triage model,
  and consistent fault coding by 200–400 technicians. Without them, the same symptom is coded
  five ways, the fault taxonomy becomes unusable for analysis, and first-time fix depends on who
  happens to take the job.
traces_to: [P02, M26, M31, M01, M32, M61, MD-024, MD-025, MD-021, KB-001, SP-004, SP-005, SP-007, SP-008, SP-010, SP-034]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: SP-033_Diagnostic_and_Triage_Decision_Tree_Library_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P02_Technician_Mobile_Application.md — guided diagnostic tree and offline knowledge pack
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/J_Data_Analytics_and_Intelligence/M26_AIML_Services_and_Model_Operations.md — BRU-AIM-01 human confirmation for material recommendations, BRU-AIM-02 guard rails
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-12 beyond economic repair requires photographic evidence and a second technician; BRU-SRM-14 L3 restrictions
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-004 first-time fix 70% baseline, KPI-013 automatic assignment rate, KPI-026 AI first-contact resolution
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 8.5.1 controlled conditions, and clause 7.2 competence
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# Diagnostic and Triage Decision Tree Library

| Item | Value |
|---|---|
| SOP ID | `SP-033` |
| Process owner | Operations Director (R05) with Quality Manager (R32); technical authorship by Specialist Technicians (R12) |
| Roles performing | `R08` Service Centre Agent (intake triage) · `R34` Contact Centre Agent (remote triage) · `R13` Remote Support Engineer · `R10`–`R12` Technicians (bench and field) |
| Systems used | `P02` guided diagnostic · `P03` (`UI-023`) · `P10` · `M26` · `M31` |
| Frequency / volume | Every service order is triaged; 200–400 technicians consume the trees daily |
| ISO 9001 clause reference | 8.5.1 controlled conditions · 7.2 competence · 8.5.2 traceability (fault coding) |

---

## 1. Purpose and Outcome

**Purpose.** To take a customer's description of a problem and convert it, consistently, into a
coded fault, a service route and a first action — whoever is doing the triage, wherever they are,
and whether or not they are the most experienced person available.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| The same symptom produces the same fault code across agents and branches | Coding consistency analysis |
| Triage routes the job correctly first time — remote, on-site, bench, L3 | Re-routing rate |
| First-time fix rises from 70% toward 88% | `KPI-004` |
| Estimates draft accurately from the fault code | `AUT-004`, `SP-013` |
| The AI triage model has a consistent, human-authored ground truth | `M26`, `KPI-026` |
| Technicians in the field can use the tree offline | `P02` offline pack |

---

## 2. Scope

**Applies to:** structured decision trees for the device families 1000FiX services, at three
depths — **intake triage** (counter and contact centre), **remote triage** (before dispatch), and
**bench diagnosis** (workshop and field) — plus the routing and safety rules embedded in them.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Repair procedures once the fault is known | `KB-*` technical library |
| The fault and repair taxonomies themselves | `MD-024`, `MD-025` |
| Conversation wording at the counter or on a call | `SP-007`, `SP-034` |
| The AI model's training, evaluation and guard rails | `M26`; this library is its ground truth, not its implementation |
| Estimate construction | `SP-013` |
| Safety response to a hazardous device | `SP-030`; this library routes to it |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Tree | An ordered set of questions and observations leading to a coded outcome |
| Node | A single question or check |
| Outcome | A fault code from `MD-024` plus a route and a first action |
| Route | Remote resolution, on-site visit, bench repair, L3 specialist, or not-a-fault |
| Confidence | The tree's own statement of how certain the outcome is |
| Stop node | A node that halts the tree for safety or for a mandatory escalation |
| Ground truth | The human-authored outcome the AI model is measured against |
| Offline pack | The version of the trees cached on `P02` for disconnected use |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Fault symptom taxonomy | `MD-024` | Every outcome maps to a registered code; **the tree may not invent one** |
| Repair action taxonomy | `MD-025` | First actions map to registered repair actions |
| Device catalogue | `MD-021` | Trees are scoped by device family, make and model generation |
| Competence levels | `MD-010` | Trees state the level required to act on the outcome |
| Certification requirements | `MD-011` | Brand warranty routes check certification (`BRU-SRM-09`) |
| Safety rules | `SP-030` | Stop nodes for battery, electrical, water and thermal risk |
| Knowledge articles | `KB-*` | Outcomes link to the repair procedure |

---

## 5. Procedure

### 5.1 Rules that govern every tree

| # | Rule |
|---|---|
| **DT-01** | **Every outcome is a registered `MD-024` fault code.** A tree may not create a code (`RG-01`) |
| **DT-02** | **Every tree has a "cannot determine" outcome.** Forcing a code produces false data, which is worse than an honest unknown |
| **DT-03** | **Safety stop nodes come first**, before any diagnostic question. Swelling, burning smell, heat, liquid ingress, exposed conductor |
| **DT-04** | **Each node is one observable check**, answerable by the person at that depth without training they do not have |
| **DT-05** | **Intake trees never require opening the device.** The customer is present and the device is theirs |
| **DT-06** | **Every tree states the competence level** required to act on its outcome (L1/L2/L3) |
| **DT-07** | **Maximum depth of eight nodes at intake**, twelve at remote, unbounded at bench. A counter triage that takes longer than the intake target is not usable (`KPI-010`) |
| **DT-08** | **Bilingual**, with the Bengali version signed off in context (`BN-018`) — most triage happens in Bengali |
| **DT-09** | **Every tree names its author and its technical reviewer**, and carries a review date |
| **DT-10** | **Outcomes link to a `KB-*` article** where a repair procedure exists |
| **DT-11** | **The tree is the AI's ground truth.** Where the model disagrees with the tree, the tree governs until a human changes the tree (`BRU-AIM-01`) |
| **DT-12** | **Trees are versioned; outcomes recorded against the tree version in force** — so that coding drift is explainable |

### 5.2 The three depths

| Depth | Used by | Purpose | Max nodes | Ends with |
|---|---|---|---:|---|
| **Intake triage** | `R08` at the counter, `R34` on a call, customer self-service in `P01` | Route correctly and set expectation | 8 | Fault code, route, indicative time band |
| **Remote triage** | `R34`, `R13`, AI assistant (`M32`) | Resolve without a visit where possible | 12 | Resolved, or a route with a prepared job context |
| **Bench / field diagnosis** | `R10`–`R12` on `P02` or `P03` | Confirm the fault and select the repair action | unbounded | Confirmed fault code + `MD-025` action |

### 5.3 Library structure — trees by device family

The library is organised by the device families in `MD-021`. Each family carries the three
depths. **This file specifies the structure and the governing rules; the populated trees are
authored per family and held as versioned content beside it.**

| # | Device family | Intake | Remote | Bench | Technical author | Priority |
|---:|---|:--:|:--:|:--:|---|:--:|
| 1 | Smartphone and tablet | ✔ | ✔ | ✔ | R12 mobile specialist | **P0 for W2** |
| 2 | Laptop and desktop | ✔ | ✔ | ✔ | R12 computing specialist | **P0 for W2** |
| 3 | Printer and imaging | ✔ | ✔ | ✔ | R12 | P1 |
| 4 | Television and display | ✔ | ✔ | ✔ | R12 | P1 |
| 5 | Refrigeration and cooling | ✔ | ✔ | ✔ | R12 refrigerant-certified | **P0 — safety-critical** |
| 6 | Air conditioning | ✔ | ✔ | ✔ | R12 refrigerant-certified | **P0 — safety-critical** |
| 7 | Washing machine and laundry | ✔ | ✔ | ✔ | R12 | P1 |
| 8 | Small kitchen appliance | ✔ | ✔ | ✔ | R12 | P2 |
| 9 | Networking and connectivity | ✔ | ✔ | ✔ | R13 | P1 |
| 10 | Server and enterprise IT | — | ✔ | ✔ | R13 | P2 |
| 11 | Medical and laboratory equipment | ✔ | ✔ | ✔ | R12 with calibration competence | **P0 — calibration and safety** |
| 12 | Power and UPS | ✔ | ✔ | ✔ | R12 | **P0 — battery safety** |

> Twelve families × three depths = **36 trees to author**. Five families are marked P0 because
> they are either the highest-volume (1, 2) or carry a safety or calibration consequence
> (5, 6, 11, 12). Authoring effort is a technical-specialist task, not a content task, and is
> not currently resourced — raised in §14.

### 5.4 Worked example — the shape every tree takes

Illustrating `DT-01` … `DT-07` on a smartphone intake tree. **This is the pattern, not the
content**; the authored trees carry the full node set.

| Node | Question / check | Answers | Then |
|---:|---|---|---|
| **S1** | **Safety stop.** Is the device swollen, hot, leaking, burnt or liquid-damaged? | Yes | **Stop.** Isolate per `SP-030`; do not place in the standard bin; inform the customer of special handling |
| | | No | Continue |
| 1 | Does the device power on? | Yes → node 4 · No → node 2 · Intermittently → code `FLT-PWR-INT`, route bench | |
| 2 | Does it respond to a known-good charger for 15 minutes? | Yes → code `FLT-PWR-CHG`, route bench, L1 · No → node 3 | |
| 3 | Any physical damage or liquid indicator triggered? | Yes → code `FLT-PHY-LIQ`, route bench L2, **advise the customer that data recovery is a separate service** (`SP-012`) · No → code `FLT-PWR-DEAD`, route bench L2 | |
| 4 | Is the reported problem display, audio, camera, charging, network, software or performance? | Branch per answer to nodes 5–8 | |
| 5 | Display: is it cracked, blank, discoloured or touch-unresponsive? | Each maps to a distinct `MD-024` code; route bench; L1 for panel replacement, L2 for touch controller | |
| 6 | Network: does it fail on all networks or one? | One → likely SIM or carrier, may be **not-a-fault**; All → code, route bench L2 | |
| 7 | Software: does the fault persist after a restart? | No → **not-a-fault**, resolve at the counter, no order raised · Yes → code, route remote first | |
| 8 | **Cannot determine** | — | Code `FLT-UNK`, route bench for diagnosis, set expectation that diagnosis precedes any estimate (`DT-02`) |

**Note the four things this example demonstrates and every authored tree must reproduce:**
a safety stop before any diagnosis; codes drawn from the registry; an honest "cannot determine";
and a **not-a-fault** outcome that closes the interaction without raising a service order.

### 5.5 Authoring and maintaining a tree

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 1 | R12 specialist | Draft from actual fault distribution, not from the manufacturer's manual alone | `M31` history |
| 2 | R12 | Map every outcome to `MD-024` and `MD-025` | `DT-01` |
| 3 | R32 | Technical review: is each node observable at that depth, are branches exhaustive (`PD-10`) | `SP-003` |
| 4 | HSE | Safety review of the stop nodes | `SP-030` |
| 5 | Localisation | Bengali version, translated in context, technical terms per `BN-003` | `DT-08` |
| 6 | R32 | Pilot with a sample of agents and technicians before publication | — |
| 7 | R32 | Publish with a version; push to the `P02` offline pack | `DT-12` |
| 8 | R32 | Review quarterly against coding accuracy, re-routing rate and first-time fix | §10 |

### 5.6 Feedback loop — how trees improve

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 9 | System | Compare triage code against confirmed bench code for every order | `M31` |
| 10 | R32 | Where they diverge systematically, the tree is wrong at that node | Coding accuracy |
| 11 | R32 | Where "cannot determine" dominates a family, the tree is too shallow | `DT-02` |
| 12 | R32 | Where re-routing is high, the routing rule is wrong, not the technician | Re-routing rate |
| 13 | `M26` | The model learns from confirmed outcomes; **the tree remains the ground truth** (`DT-11`) | `BRU-AIM-01` |
| 14 | R32 | Update the tree; version it; re-publish; retrain where the change is material | `DT-12` |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| S1 | Any safety indicator present | **Stop the tree.** Safety routing precedes diagnosis, always (`DT-03`) | Any person; `SP-030` |
| — | The agent believes they know the answer without the tree | Use the tree anyway. Consistency is the purpose; expert shortcuts are exactly what produces five codes for one symptom | R08/R34 |
| — | The tree's outcome contradicts the technician's judgement at the bench | The technician's confirmed diagnosis governs at the bench, and the divergence is captured as tree feedback (§5.6) | R10–R12 |
| — | The outcome requires L3 and no certified specialist is available | Route to an equipped workshop (`BRU-SRM-14`); do not attempt at a lower level | R09 |
| — | The outcome is brand warranty work | Check technician certification before promising a date (`BRU-SRM-09`) | R08 |
| — | The tree produces "cannot determine" | That is a valid outcome. Route to bench diagnosis and tell the customer honestly that diagnosis precedes the estimate | R08 |
| — | The tree produces "not-a-fault" | Resolve at the counter or on the call. **Do not raise a service order to justify the contact** | R08/R34 |
| — | The AI proposes an outcome the tree does not | Human confirmation is required for any material recommendation (`BRU-AIM-01`); the tree governs (`DT-11`) | R32 |
| — | A node needs a tool or a measurement the person does not have | The node is wrong for that depth (`DT-04`). Report it as tree feedback | R32 |
| — | Beyond economic repair appears likely at triage | Do not state it as a conclusion at intake. BER requires photographic evidence and a second technician's confirmation (`BRU-SRM-12`) | R09 + second technician |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Publish a new or amended tree | Any | R32 Quality Manager, on R12 technical authorship | R05 |
| Add a fault code | Any | **Not here.** Registered in `MD-024` first (`DT-01`, `RG-01`) | MDM + R32 |
| Approve a safety stop node | Any | HSE Lead | R05 |
| Approve the Bengali version | Any | Localisation Lead with a technical reviewer (`BN-018`) | R32 |
| Deploy a tree change to the `P02` offline pack | Any | R32 with R33 | CTO |
| Allow the AI to act on a tree outcome without human confirmation | **None where the impact is material** (`BRU-AIM-01`) | — | — |
| Remove a "cannot determine" outcome from a tree | **None — prohibited** (`DT-02`) | — | — |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Tree outcome maps to an unregistered fault code | Blocked; register the code in `MD-024` first | MDM, R32 | Register change |
| Systematic divergence between triage and bench codes | The tree is wrong; fix the node, do not retrain the agents | R32 | Tree feedback |
| "Cannot determine" dominates a family | The tree is too shallow for that family; deepen it | R32 | Tree review |
| Safety stop node missed and a hazardous device entered the bin | Safety incident (`SP-030`); review the node's wording and its position | HSE, R32 | Incident + tree change |
| Offline pack out of date on a technician's device | Sync enforcement; a technician working from a superseded tree codes inconsistently | R33, R32 | Sync exception |
| Bengali tree diverges from English after a change | Suspend the changed node until the Bengali is signed off | Localisation Lead | Translation exception |
| AI model output conflicts with the tree repeatedly | Investigate both; the tree may be stale or the model may be drifting | R32, CTO | Model review |
| A branch uses its own informal triage sheet | Withdraw it; capture anything useful into the library | R32 | Library change |
| Tree unavailable during an outage | Printed pack per §9 | R06, R33 | Manual record |

---

## 9. Manual Fallback

| Step | Manual action |
|---|---|
| 1 | Every branch holds a **printed triage pack** — the intake trees for the families it services, in both languages, current version |
| 2 | Technicians carry the printed bench trees for their assigned families, or rely on the `P02` offline pack, which is the primary offline path |
| 3 | Fault codes are written on the paper job card from the printed tree's outcome column |
| 4 | **Back-enter codes within 24 hours** so that coding analysis is not distorted by the outage |
| 5 | The printed pack is reissued on every tree version change — the same distribution discipline as `SP-032` §9 and `SP-013` §9 |

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Outcomes restricted to registered `MD-024` codes | Preventive (`DT-01`) | Per outcome | Hard block |
| "Cannot determine" outcome present in every tree | Preventive (`DT-02`) | Per tree | Publication check |
| Safety stop nodes precede diagnosis | Preventive (`DT-03`) | Per tree | HSE review |
| Node depth bounded at intake and remote | Preventive (`DT-07`) | Per tree | Publication check |
| Competence level stated per outcome | Preventive (`DT-06`) | Per outcome | Routing rule |
| Certification checked on brand warranty routes | Preventive (`BRU-SRM-09`) | Per assignment | Hard block |
| AI requires human confirmation for material outcomes | Preventive (`BRU-AIM-01`) | Per recommendation | Confirmation record |
| Trees versioned; outcomes stamped with the version | Preventive (`DT-12`) | Per outcome | Version stamp |
| Triage-to-bench code accuracy | Detective | Monthly | Coding accuracy report |
| Re-routing rate by tree and family | Detective | Monthly | Routing report |
| "Cannot determine" rate by family | Detective | Monthly | Tree depth review |
| First-time fix by fault code | Detective | Monthly | `KPI-004` |
| Offline pack currency across devices | Detective | Weekly | Sync report |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Author a tree | Be its sole technical reviewer (`SOD-13` pattern — author cannot approve) | Hard block | R32 reviews; HSE reviews safety nodes |
| Author a fault code in `MD-024` | Approve the tree that uses it | Hard block | MDM registers; R32 approves the tree |
| Perform the repair | Confirm the beyond-economic-repair conclusion alone (`BRU-SRM-12`) | Hard block | Second technician confirms |
| Author an AI guard rail | Be sole approver of its removal (`SOD-36`) | Hard block | CTO countersign |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-004` | First-time fix rate | 70% | 82%; stretch 88% |
| `KPI-013` | Automatic assignment rate — depends on reliable coding | 0% | 20%; stretch 70% |
| `KPI-026` | AI first-contact resolution | 0% | 40%; stretch 55% |
| `KPI-025` | Status enquiries deflected to self-service | 0% | 60%; stretch 80% |
| Triage-to-bench code accuracy | Triage code confirmed at bench | untracked | To be set; rising |
| Re-routing rate | Jobs routed incorrectly at triage | untracked | Falling |
| "Cannot determine" rate | Proportion of triages ending unresolved | untracked | Low, but never zero (`DT-02`) |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `KB-001` Knowledge Architecture and Tagging Standard | Outcomes link to `KB-*` repair procedures |
| `UI-012` `P02` Technician App UI Copy Pack · `UI-023` Workspace — Service Intake Copy | The screens the trees render in |
| [`SP-007_SOP_Walk_In_Intake_and_Front_Desk.md`](SP-007_SOP_Walk_In_Intake_and_Front_Desk.md) | Intake triage at step 6 |
| [`SP-008_SOP_On_Site_Field_Service_Visit.md`](SP-008_SOP_On_Site_Field_Service_Visit.md) | Field diagnosis at step 9 |
| [`SP-010_SOP_Workshop_and_Depot_Repair.md`](SP-010_SOP_Workshop_and_Depot_Repair.md) | Bench diagnosis at step 5 |
| [`SP-034_Call_and_Conversation_Script_Library.md`](SP-034_Call_and_Conversation_Script_Library.md) | Remote triage on a call |
| [`SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](SP-030_SOP_Health_Safety_and_Incident_Reporting.md) | Every safety stop node routes here |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md) | The registered fault codes |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md) | First actions |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-010_Competency_and_Skill_Taxonomy.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-010_Competency_and_Skill_Taxonomy.md) | L1/L2/L3 levels |
| `TR-009` Course Pack — Field Technician · `TR-005` Question Bank — Technician Certification | Train the use of the trees |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue — library structure, governing rules `DT-01`…`DT-12`, and the authoring and feedback processes | Operations Director with Quality Manager (pending) |

**Open items**

| # | Item | Owner | Needed by |
|---|---|---|---|
| O-01 | **The 36 trees (12 families × 3 depths) are not yet authored.** This file specifies the structure and the rules; the technical content is a specialist authoring task requiring R12 time that is not currently allocated. The five P0 families are needed for W2 | R32 with R12 specialists; resourcing by PMO | **P0 families before W2; remainder before W4** |
| O-02 | Confirm the twelve device families against `MD-021` once that catalogue is populated with the actual serviced range | R32 with MDM | Before authoring begins |
| O-03 | Agree the coding-accuracy measurement method with `RP-001` so the feedback loop in §5.6 has a defined metric | R32 with Analytics | Before W2 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] Governing rules stated, including the prohibition on minting fault codes (`DT-01`, `RG-01`)
- [x] "Cannot determine" mandated as an outcome in every tree, and its removal prohibited
- [x] Safety stop nodes placed before diagnosis
- [x] The tree stated as the AI's ground truth, with human confirmation required
- [x] Worked example demonstrates the required shape
- [x] Feedback loop defined so trees improve from confirmed outcomes
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **O-01 the 36 trees authored — outstanding; this file is the specification, the trees are the deliverable**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approvers recorded — **pending Operations Director and Quality Manager**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
