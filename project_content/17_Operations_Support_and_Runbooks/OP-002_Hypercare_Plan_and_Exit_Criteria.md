---
id: OP-002
title: Hypercare Plan and Exit Criteria
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Support Lead with Programme Office
author: Support Lead with Programme Office and Change Lead
reviewers: [Chief Technology Officer, Operations Director, Programme Manager, QA Lead, Change Lead, Data Migration Lead, CFO, Contact Centre Supervisor]
approver: Programme Manager
content_class: C
purpose: >
  Defines what hypercare is for each of the nine waves — its duration, staffing, floor-walking
  coverage, triage cadence, decision authority and, above all, the measured criteria that end it.
  Hypercare that ends by exhaustion rather than by criteria leaves unresolved adoption problems
  that are then mistaken for permanent system limitations, and the next wave inherits them.
traces_to: [06-01, 06-02, M66, M23, OP-001, OP-013, OP-016, TS-013, TS-018, DM-014, CM-007, CM-012, TR-024]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md — nine waves, wave months and scope
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §4 — wave gate criteria G1-01…G1-12, G2-01…G2-10, G3-01…G3-09, G4-01…G4-09
    verified: 2026-08-20
    class: P1
  - source: project_content/13_Test_and_Acceptance_Content/TS-018_Defect_Taxonomy_Triage_and_Signoff_Forms.md §4.1 S1–S4, §4.3 triage rules TR-01…TR-09, §4.4 deferral rules DF-01…DF-05
    verified: 2026-08-20
    class: P1
  - source: project_content/13_Test_and_Acceptance_Content/TS-013_Regression_Pack_and_Smoke_Test_Checklist.md — post-deployment smoke checklist
    verified: 2026-08-20
    class: P1
  - source: project_content/12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md — cutover freeze, parallel run, fallback trigger
    verified: 2026-08-20
    class: P1
  - source: Panorama Consulting, "ERP Hypercare Checklist and Post-Go-Live Support Plan" — hypercare duration, elevated staffing, exit-criteria practice (https://www.panorama-consulting.com/erp-hypercare-checklist/)
    verified: 2026-08-20
    class: P3
  - source: Flectic, "ERP Go-Live Checklist: Cutover, Go/No-Go, Hypercare (2026)" — quantified exit thresholds (P1 volume, MTTR, adoption, reconciliation variance, integration health) (https://flectic.com/learn/erp-go-live-checklist)
    verified: 2026-08-20
    class: P3
supersedes: none
review_due: 2027-02-20
---

# OP-002 — Hypercare Plan and Exit Criteria

> **Hypercare ends on evidence or it does not end.** Every wave in this programme will reach a
> point where the hypercare team is tired, the next wave is late, and somebody proposes that
> hypercare "wind down". This file exists so that proposal has to be answered with numbers.
>
> English only — programme and support audience ([`CG-010`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) §3.2). What users are *told* during
> hypercare is [`CM-007`](../16_Change_Management_and_Comms/CM-007_Hypercare_Communication_Pack.md), which is bilingual.

---

## 1. Purpose

Hypercare is the deliberately elevated support posture immediately after a wave goes live. It is
not "the first few weeks of support"; it is a different operating model with different staffing,
different cadence, different authority and a defined end.

**What stops without this file:**

| Absent | Consequence |
|---|---|
| Defined duration and staffing | Hypercare is resourced by whoever is available, which is the delivery team, which delays the next wave |
| Defined exit criteria | Hypercare ends when attention moves on. Open adoption problems are re-labelled "how the system works" and become permanent |
| Defined triage cadence | Defects and incidents mix in one queue and the loudest requester sets priority ([`TS-018`](../13_Test_and_Acceptance_Content/TS-018_Defect_Taxonomy_Triage_and_Signoff_Forms.md) `TR-09` guards the same failure in testing) |
| Defined authority | Nobody can decide, in the first 48 hours, whether to roll back — the one decision that has to be made fast ([`DM-014`](../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) fallback trigger) |
| A hypercare record | [`OP-016`](OP-016_Post_Incident_Review_Template_and_Register.md) has no source for the recurring causes that hypercare surfaces, and the next wave repeats them |

> **Upstream gap, stated.** The Master Index traces this file to `06-06_Deployment_and_Operations_Plan.md`,
> which **does not exist on disk** — `06_Delivery_and_Implementation/` contains only `06-01` and
> `06-02` (enumerated 2026-08-20). This file therefore stands alone rather than elaborating a plan,
> and where it makes an operational assumption that `06-06` would properly own, it is marked
> **[assumes 06-06]**. Raised as a finding in the Category 17 audit; the same pattern as
> `AUDIT-011`'s missing `06-03`.

---

## 2. Scope

**In scope:** hypercare entry conditions; duration per wave; the hypercare organisation and its
authority; floor-walking and branch coverage; the daily and weekly cadence; the defect and
incident split; the known-issue log; the rollback decision; exit criteria and their measurement;
the exit sign-off; and the transition to business-as-usual support.

**Out of scope:**

| Situation | Owned by |
|---|---|
| The standing support model hypercare temporarily amplifies | [`OP-001`](OP-001_Support_Model_Tiering_and_Routing_Content.md) |
| Cutover itself — freeze, last transaction, parallel run | `DM-014` |
| Branch readiness before cutover | [`CM-012`](../16_Change_Management_and_Comms/CM-012_Branch_Readiness_Communication_Checklist.md) |
| What users are told during hypercare | `CM-007` |
| Defect severity, triage and deferral rules | `TS-018` |
| Wave gate criteria and Go/No-Go | `06-02` §4 |
| Platform incident severity and the on-call rota | [`OP-013`](OP-013_On_Call_Escalation_and_Handover_Content.md) |
| Post-incident review | `OP-016` |
| Release notes for the wave | [`OP-006`](OP-006_Release_Notes_Standard_and_Wave_Note_Set.md) |
| Refresher training during hypercare | [`TR-024`](../08_Training_and_Enablement/08B_Course_Packs/TR-024_Release_Training_and_Refresher_Standard.md) |

---

## 3. Audience

| Reader | Uses this file to |
|---|---|
| Programme Manager | Decide entry, extension and exit |
| Support Lead | Staff and run the hypercare desk |
| Change Lead | Schedule floor-walking and champion cover ([`CM-008`](../16_Change_Management_and_Comms/CM-008_Champion_and_Super_User_Network_Kit.md)) |
| QA Lead | Route defects out of hypercare into `TS-018` triage |
| Operations Director | Decide fallback and rollback for the business |
| Branch managers and champions | Know what cover exists, for how long, and what happens when it ends |
| Steering Committee | Read one evidenced exit decision per wave, not nine subjective ones |

---

## 4. Content

### 4.1 What hypercare is, precisely

| Dimension | Business as usual (`OP-001`) | **Hypercare** |
|---|---|---|
| T1 staffing | Per §4.7 of `OP-001` | **2× baseline**, plus floor-walkers on site |
| Triage cadence | Daily breach review | **Twice daily**, 09:30 and 17:30 BST |
| Defect route | Ticket → backlog → release | **Ticket → same-day triage → hotfix path** where `S1`/`S2` |
| Authority to change production | Normal change (CAB) | **Standing emergency-change authority** for the incident commander, reviewed within 2 working days ([`SP-031`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) §5) |
| Presence | Remote | **On-site at every site cutting over**, for the floor-walking period in §4.4 |
| Communication | Standing channels | **Daily bulletin** to all affected users (`CM-007`) |
| Measurement | Monthly | **Daily**, against §4.8 exit criteria |
| Delivery team | On the next wave | **Ring-fenced** for the hypercare period; this is a planning constraint, not a favour |

### 4.2 Entry conditions

Hypercare begins at the moment the wave's cutover completes — but it may only begin if these are
true. If they are not, the wave has not gone live; it has been abandoned into production.

| # | Entry condition | Evidence | Owner |
|---|---|---|---|
| **HE-01** | The wave gate criteria in `06-02` §4 are signed | Signed gate record | Programme Manager |
| **HE-02** | Post-deployment smoke checklist passed ([`TS-013`](../13_Test_and_Acceptance_Content/TS-013_Regression_Pack_and_Smoke_Test_Checklist.md)) | Smoke run record | QA Lead |
| **HE-03** | Cutover reconciliation signed (`DM-014`) | Control totals, signed | Data Migration Lead |
| **HE-04** | The hypercare roster is published, named, and every named person has confirmed | Roster | Support Lead |
| **HE-05** | The rollback decision path in §4.7 is confirmed with the named decision-makers reachable | Contact sheet | Programme Manager |
| **HE-06** | `CM-007` hypercare communications have been issued to every affected population, in both languages | Send record | Change Lead |
| **HE-07** | Known issues at go-live are published (§4.6) — **the list is never empty, and an empty list means it was not compiled** | Known-issue log v1 | QA Lead |
| **HE-08** | The service desk queues for the wave's new populations exist and are staffed (`OP-001` §4.3) | Queue configuration | Support Lead |
| **HE-09** | On-call rota covers the hypercare period with **no gaps and no single-person weeks** | `OP-013` rota | Platform Engineering |
| **HE-10** | Branch readiness confirmed for every site in the wave (`CM-012`) | Readiness checklist | Change Lead |

### 4.3 Duration by wave

Baseline durations are set from the size and risk of each wave, not from a single programme
default. Industry practice for ERP hypercare is 2–8 weeks, extending to around 12 for complex
phased rollouts; the durations below sit inside that range and are lengthened where a statutory
or financial cycle must complete inside the window.

| Wave | Scope | Months (`06-01`) | **Hypercare duration** | Why this length |
|:--:|---|---|:--:|---|
| **W1** | Core platform, Admin Portal `P03` | 3–8 | **8 weeks** | First live wave; nothing about the operating model has been proven. Must contain one full month-end |
| **W2** | Customer `P01`, Technician `P02` | 8–14 | **6 weeks** | 200–400 field technicians and the first customer-facing surface; field conditions cannot be simulated ([`TS-015`](../13_Test_and_Acceptance_Content/TS-015_Offline_and_Field_Condition_Test_Scripts.md)) |
| **W3** | Logistics `P09`, Vendor `P05`, Payments | 14–18 | **8 weeks** | Money movement. Must contain a full settlement and reconciliation cycle for every live gateway |
| **W4** | Corporate `P04`, Brand `P08`, Contact Centre `P10`, Analytics `P06` | 18–23 | **6 weeks** | Four external populations at once; contractual clients |
| **W5** | Quality `P11`, Finance depth, HR depth | 23–27 | **8 weeks** | Must contain one full payroll run **and** one statutory filing |
| **W6** | Native apps, AI assistant, **`M66` ITSM** | 27–30 | **4 weeks** | Additive capability; `M66` go-live additionally migrates the support model itself (`OP-001` §4.9) |
| **W7** | Marketplace `P07`, Partner `P12` | 30–33 | **6 weeks** | New external populations with money flows (payouts) |
| **W8** | Scale, optimisation | 33–36 | **4 weeks** | Mostly non-functional |
| **W9** | Multi-entity | 33–36 | **6 weeks** | Multi-entity and cross-border introduce statutory surfaces (`NFR-086`, `NFR-099`) |

**Rules**

| # | Rule |
|---|---|
| **HD-01** | Duration is a **minimum**, not a target. Hypercare ends on §4.8 criteria, never on the calendar alone |
| **HD-02** | Hypercare may not exit before **one full instance of every business cycle it touches** has completed inside it — month-end (W1, W3, W5), payroll (W5), settlement (W3, W7), statutory filing (W5, W9) |
| **HD-03** | Where a wave rolls out to branches in tranches, **each tranche gets its own floor-walking period** (§4.4); the wave-level hypercare clock runs from the **last** tranche |
| **HD-04** | An extension beyond 150% of the baseline duration is escalated to the Steering Committee with a root-cause statement — it means something failed before go-live, not during it |

### 4.4 Floor-walking and site coverage

Floor-walking is a person standing beside the user doing the work for the first time. It is the
single highest-yield hypercare activity and the first one cut when resourcing is short.

| Site type | Coverage | Duration | Ratio |
|---|---|---|---|
| Pilot branch (first of a wave) | On-site, full opening hours | First **10 working days** | 1 floor-walker per 8–10 users |
| Subsequent branch | On-site | First **5 working days** | 1 per 12–15 users |
| Central warehouse | On-site | First **10 working days** | 1 per shift |
| Workshop / depot | On-site | First **5 working days** | 1 per 12–15 users |
| Field technicians | **Ride-along**, not desk cover | First **5 shifts** per technician cohort | 1 per 6 technicians |
| Contact centre (`P10`) | On-site, deskside | First **10 working days** | 1 per 10 agents |
| Head office functions | Remote + scheduled clinics | First **10 working days** | Daily 60-minute clinic per function |

| # | Rule |
|---|---|
| **FW-01** | A floor-walker's first duty is to **record**, not to fix. Every intervention becomes a ticket, even when it took 30 seconds — otherwise the volume that justifies training or a fix is invisible |
| **FW-02** | Floor-walkers are drawn from the **champion network** (`CM-008`) plus the project team, never solely from the project team; the champion is who remains after exit |
| **FW-03** | Ride-alongs are with the technician on real jobs, in real network conditions. A ride-along in the branch car park does not count |
| **FW-04** | Floor-walking observations feed `TR-024` refresher content **within the hypercare period**, not after it |

### 4.5 Cadence and the hypercare organisation

| Meeting | When | Duration | Chair | Attendees | Output |
|---|---|---|---|---|---|
| **Morning triage** | 09:30 BST daily | 30 min | Support Lead | T1 supervisor, QA Lead, Platform on-call, Change Lead, domain leads | Prioritised list, owners, targets |
| **Evening triage** | 17:30 BST daily | 30 min | Support Lead | Same | Overnight actions, on-call briefing |
| **Command call** | On declaration of any `Sev1` | Until stood down | Incident Commander (`OP-013`) | Per incident | Incident record |
| **Daily bulletin** | 18:30 BST | — | Change Lead | To all affected users | `CM-007` bulletin, both languages |
| **Weekly hypercare review** | Weekly | 60 min | Programme Manager | Support Lead, QA Lead, CTO, Operations Director, Finance where money is affected | Exit-criteria dashboard, extension decision |
| **Exit review** | At criteria attainment | 90 min | Programme Manager | Signatories in §4.9 | Signed exit or extension |

**Hypercare roles**

| Role | Held by | Authority |
|---|---|---|
| **Hypercare Manager** | Support Lead | Runs the desk, triage and the exit dashboard |
| **Incident Commander** | Rotating, per `OP-013` §4.6 | Declares severity, directs response, requests emergency change |
| **Business Decision Owner** | Operations Director (or CFO where financial) | Decides workaround acceptability and business fallback ([`OP-014`](OP-014_Manual_Fallback_Procedure_Set.md)) |
| **Rollback Authority** | Programme Manager **jointly with** CTO | The §4.7 decision |
| **Defect Router** | QA Lead | Moves defects into `TS-018` triage with severity |
| **Communications Owner** | Change Lead | Owns every message out; nobody else sends one ([`OP-004`](OP-004_Incident_Communication_Template_Set.md) §3) |

### 4.6 The known-issue log

| Field | Rule |
|---|---|
| Issue reference | Links the defect (`TS-018`), the incident (`OP-013`) or both |
| Symptom in user language | Written as the user experiences it, not as the system reports it |
| Affected population | Which of the `OP-001` §4.1 populations, and how many |
| Workaround | **Mandatory.** An entry with no workaround is escalated, not published |
| Target | Fix wave or release |
| Communication state | Published in `CM-007` bulletin / status page ([`OP-005`](OP-005_Status_Page_and_Maintenance_Notice_Copy.md)) / not published, with reason |
| Owner | Named |

| # | Rule |
|---|---|
| **KI-01** | Published at go-live (`HE-07`) and updated at every evening triage |
| **KI-02** | An issue in the log for **more than 20 working days** becomes a problem record (`SP-031` §8), not a standing entry |
| **KI-03** | Issues affecting customers are mirrored to `OP-005` and to `HC` content; a known issue the customer meets but cannot read about generates a contact |
| **KI-04** | The log is **handed to BAU at exit**, not closed at exit |

### 4.7 The rollback decision

The decision that must be fast. `DM-014` defines the data fallback trigger; this section defines
who decides and against what.

| Trigger | Assessment window | Decision | Authority |
|---|---|---|---|
| Data integrity failure — reconciliation cannot be made to balance | 4 hours | Roll back to legacy for the affected domain | Programme Manager + CFO |
| A `P0` business process cannot be completed by any route, including manual fallback (`OP-014`) | 4 hours | Roll back | Programme Manager + Operations Director |
| Statutory output cannot be produced (Mushak, payroll, filing) | 8 hours | Roll back **or** invoke the manual statutory route | CFO |
| Customer-facing outage exceeding RTO with no restoration path | 2 hours | Invoke [`OP-012`](OP-012_Disaster_Recovery_and_Continuity_Playbook.md), not rollback | CTO |
| Volume of `S1` defects exceeding 5 open with no fix path | 1 working day | Roll back the affected scope | Programme Manager + CTO |
| Adoption failure (users refusing or unable to use the system, working around it on paper) | 5 working days | **Not a rollback.** Extend hypercare, escalate to Change | Change Lead + Operations Director |

| # | Rule |
|---|---|
| **RB-01** | Rollback is a **business decision with a technical execution**, never the reverse |
| **RB-02** | The rollback path is only credible if it was rehearsed in the cutover rehearsal (`DM-014`). An unrehearsed rollback is a second incident |
| **RB-03** | **Rollback windows close.** Once a wave has produced transactions that legacy cannot accept — typically 5–10 working days — rollback ceases to be an option and the wave must be fixed forward. The closing date is stated in the wave's cutover plan and repeated in the daily bulletin |
| **RB-04** | Rollback always triggers a `Sev1` post-incident review (`OP-016`) regardless of how smoothly it executed |

### 4.8 Exit criteria

Every criterion is measured, has a source, and must hold for a **stated consecutive period**. A
criterion met once is not met.

| # | Criterion | Threshold | Sustained for | Source |
|---|---|---|---|---|
| **HX-01** | Open `S1` defects (`TS-018`) | **Zero** | 10 consecutive working days | Defect register |
| **HX-02** | Open `S2` defects | ≤ 3, each with an accepted workaround and a target release | 10 working days | Defect register |
| **HX-03** | New `S1`/`S2` defect arrival rate | ≤ 1 per week combined | 2 consecutive weeks | Defect register |
| **HX-04** | `Sev1` platform incidents (`OP-013`) | **Zero** | 10 consecutive working days | Incident register |
| **HX-05** | `Sev2` platform incidents | ≤ 1 per week | 2 consecutive weeks | Incident register |
| **HX-06** | Support contact volume | Declining week on week, and ≤ 1.5× the modelled BAU volume for the population | 2 consecutive weeks | Ticket system |
| **HX-07** | First-contact resolution at T1 | ≥ 50% (rising to the `OP-001` 60% target in BAU) | 2 consecutive weeks | Ticket system |
| **HX-08** | Adoption of the wave's primary transactions | ≥ 90% of expected volume transacting in the system, not on paper or in legacy | 10 consecutive working days | Transaction counts vs. plan |
| **HX-09** | Financial reconciliation variance | < 0.5% and falling; **zero unexplained** items | 10 consecutive working days | Finance reconciliation |
| **HX-10** | Integration health | ≤ 2 failed jobs/day, zero dead-letter items older than 24 h | 10 consecutive working days | [`OP-008`](OP-008_Runbook_Integration_and_Event_Platform.md) dashboards |
| **HX-11** | The wave's `06-02` gate criteria still hold in production (not only at gate) | 100% | Re-verified once, in week 3+ | Gate re-verification |
| **HX-12** | Every business cycle in `HD-02` completed inside hypercare | 100% | — | Cycle sign-off |
| **HX-13** | Known-issue log: every entry has a workaround and an owner | 100% | At exit | Known-issue log |
| **HX-14** | Runbooks updated with what hypercare actually taught ([`OP-007`](OP-007_Runbook_Core_ERP_Platform.md)…[`OP-011`](OP-011_Runbook_Portal_and_Mobile_App_Operations.md)) | 100% of runbooks touched by an incident | At exit | Runbook change log |
| **HX-15** | BAU support model staffed and briefed (`OP-001`) | Roster published, handover complete | At exit | Support Lead |
| **HX-16** | Refresher training issued for the top 5 observed error patterns (`TR-024`) | Issued | At exit | L&D |
| **HX-17** | Post-incident reviews complete for every `Sev1`/`Sev2` in the period (`OP-016`) | 100% | At exit | PIR register |
| **HX-18** | Champion network active at every live site (`CM-008`) | 100% of sites with a named, trained champion | At exit | Change Lead |

**Waiver rule.** `HX-01`, `HX-09`, `HX-12` and `HX-17` are **not waivable**. Any other criterion may
be waived once, by the Programme Manager and the accountable business owner jointly, with the
waiver, its reason and its compensating control recorded in the exit form and in `RF-006`.

### 4.9 Exit form

```
HYPERCARE EXIT — WAVE ___          Cutover date: ______   Exit date proposed: ______
Baseline duration: ___ weeks       Actual: ___ weeks      Extensions: ___ (reasons attached)

CRITERIA          HX-01 ☐  HX-02 ☐  HX-03 ☐  HX-04 ☐  HX-05 ☐  HX-06 ☐
                  HX-07 ☐  HX-08 ☐  HX-09 ☐  HX-10 ☐  HX-11 ☐  HX-12 ☐
                  HX-13 ☐  HX-14 ☐  HX-15 ☐  HX-16 ☐  HX-17 ☐  HX-18 ☐
Waivers granted:  ______________________________  (HX-01, 09, 12, 17 not waivable)

HANDOVER TO BAU
  Known-issue log handed to Support Lead ............... ☐   Entries open: ___
  Open S2 defects with target release .................. ☐   Count: ___
  Problem records raised (SP-031 §8) ................... ☐   Count: ___
  Runbook changes merged ............................... ☐
  Floor-walking withdrawn, champions confirmed ......... ☐

SIGNATURES
  Hypercare Manager (Support Lead) ......... _______________  Date ______
  QA Lead .................................. _______________  Date ______
  Operations Director ...................... _______________  Date ______
  CFO (waves touching money or statutory) .. _______________  Date ______
  CTO ...................................... _______________  Date ______
  Programme Manager (decision) ............. _______________  Date ______

DECISION:  ☐ EXIT   ☐ EXTEND ___ weeks — reason: ______________________________
```

### 4.10 Transition to business as usual

| Element | During hypercare | At exit |
|---|---|---|
| Staffing | 2× T1, floor-walkers on site | `OP-001` §4.7 baseline; champions remain |
| Triage | Twice daily | Daily breach review (`OP-001` §4.9) |
| Comms | Daily bulletin | Standing channels; release notes (`OP-006`) |
| Emergency change | Standing authority to the Incident Commander | Normal `SP-031` CAB path |
| Known issues | Hypercare log | Known-error records + `HC`/`KB` content |
| Delivery team | Ring-fenced | Released to the next wave |
| Reporting | Daily exit dashboard | Monthly support report ([`CG-014`](../00_Content_Governance_and_Standards/CG-014_Content_Metrics_and_Effectiveness_Measurement.md)) |

**Rule `TX-01`:** exit is announced to every affected population (`CM-007`), stating what changes
about getting help. An unannounced exit is experienced as support being withdrawn.

### 4.11 What hypercare must produce for the next wave

| Artefact | Consumer | Why |
|---|---|---|
| Top 10 observed error patterns | `TR-024`, `HC`, [`OP-003`](OP-003_Service_Desk_Macro_and_Canned_Response_Library.md) | The next wave's users make the same mistakes |
| Runbook deltas | `OP-007`…`OP-011` | The runbook that survived contact with an incident is the true one |
| Support volume actuals per population | `OP-001` §4.7 | Staffing the next wave on evidence, not estimate |
| Cutover lessons | `DM-014`, `CM-012` | Branch readiness definitions improve per wave |
| Every PIR | `OP-016` register | Recurrence detection across waves |
| Adoption barriers | [`CM-011`](../16_Change_Management_and_Comms/CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md) | Objections are wave-specific and repeat |

### 4.12 Open decisions

| # | Decision required | Owner | Needed by | Consequence if unresolved |
|---|---|---|---|---|
| **OP-002-OI-01** | Ring-fencing of the delivery team during hypercare must be accepted as a schedule cost in `06-01` | Programme Manager + CTO | Before W1 cutover | Hypercare is staffed by borrowing from the next wave, and both slip |
| **OP-002-OI-02** | `06-06_Deployment_and_Operations_Plan.md` does not exist; confirm whether it will be written or whether Category 17 is the operational plan of record | CTO | W1 | Operational decisions marked **[assumes 06-06]** have no owning specification |
| **OP-002-OI-03** | Confirm the rollback window per wave (`RB-03`) with Finance and Operations | Programme Manager | Each cutover | The rollback option is assumed available past the point it exists |
| **OP-002-OI-04** | Floor-walker headcount — 1 per 8–15 users implies 20–40 people at a full branch tranche | Change Lead + HR | Before W1 | The coverage ratios in §4.4 are aspirational |
| **OP-002-OI-05** | Confirm that `HX-08` adoption can actually be measured per wave (requires a modelled expected volume per population) | BI Lead + Programme | W1 | The most important exit criterion is unmeasurable |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `06-01` Implementation Roadmap | Wave scope and months |
| `06-02` §4 gate criteria | `HE-01` entry and `HX-11` re-verification |
| `TS-013` Regression and smoke pack | `HE-02` |
| `TS-018` Defect taxonomy | `HX-01`…`HX-03` depend on the `S1`–`S4` scale |
| `DM-014` Cutover checklist | `HE-03`, and the rollback trigger |
| `CM-012` Branch readiness | `HE-10` |
| `CM-007` Hypercare communication | `HE-06`, the daily bulletin, `TX-01` |
| `CM-008` Champion network | Floor-walking supply and `HX-18` |
| `OP-001` Support model | The baseline hypercare amplifies |
| `OP-013` On-call and severity | `HX-04`, `HX-05`, Incident Commander |
| `OP-016` Post-incident review | `HX-17` |
| `TR-024` Release training | `HX-16` |
| `OP-014` Manual fallback | The rollback alternative in §4.7 |

**Depended on by:** `CM-007` · [`DM-001`](../12_Data_Migration_Content/DM-001_Data_Migration_Strategy_and_Scope_Register.md) · [`DM-003`](../12_Data_Migration_Content/DM-003_Entity_Migration_Priority_and_Sequencing_Plan.md) · `DM-014` · `TS-013` · `TS-018` ·
[`CG-006`](../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md) (lifecycle states during hypercare) · `OP-006`.

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **After every wave exit** — this file is revised nine times by design |
| Trigger for out-of-cycle review | Any rollback · any wave extending beyond 150% of baseline · any exit later found premature (recurrence within 30 days of exit) · publication of `06-06` |
| Owner | Support Lead with Programme Office |
| Evidence retained | Exit form, criteria dashboard, waivers, known-issue log at exit — 7 years (`NFR-088` schedule) |
| Change route | `CG-006`; duration and criteria changes require Programme Manager approval, not Content Design |

---

## Open Items

1. **OP-002-OI-01** — delivery-team ring-fencing not accepted in the schedule.
2. **OP-002-OI-02** — `06-06` missing; operational plan of record undecided.
3. **OP-002-OI-03** — rollback window per wave unconfirmed.
4. **OP-002-OI-04** — floor-walker headcount unresourced.
5. **OP-002-OI-05** — `HX-08` adoption baseline may not be measurable.
6. Durations in §4.3 are content-proposed and require Programme Manager ratification; they are
   not in `06-01`.

---

## Definition of Done

Tick every box before setting `status: Approved`. Full checklist in [`CG-008`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md).

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — all six sections present; `Open Items` added, justified
- [x] Every factual, statutory, pricing or capability claim carries a source and a verification date
- [x] Terminology matches [`CG-004`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md)
- [x] All internal links resolve — except `06-06`, which is declared missing in §1
- [ ] Accessibility standard [`CG-011`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) — n/a; not user-facing
- [x] Bengali counterpart — n/a; English-only by `CG-010` §3.2
- [ ] Named approver recorded — Programme Manager named by role; appointment pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] Decision(s) taken while authoring logged in `RF-006` — five open decisions pending

**Gates required (Class C):** G1 ●, G2 ●, G3 ●. G4 not applicable.

---

*`OP-002` · 1000FiX ERP Programme · CONFIDENTIAL — Internal Use Only*
