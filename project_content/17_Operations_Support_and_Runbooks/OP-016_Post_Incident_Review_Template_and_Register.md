---
id: OP-016
title: Post-Incident Review Template and Register
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Support with Quality
author: Support Lead with Quality Manager and Platform Engineering
reviewers: [Chief Technology Officer, Quality Manager, Operations Director, Security Lead, Data Protection Officer, Internal Audit, HR Director]
approver: Quality Manager
content_class: C
purpose: >
  The blameless review structure, the timeline and contributing-factor method, the action model and
  the register of every review — so that incidents produce change rather than relief. Incidents
  that are not reviewed recur; reviews that are not registered are not actioned; and actions that
  are not tracked into the quality system are opinions with a due date.
traces_to: [M23, M66, M60, 05-06 NFR-072, OPS-03, KPI-085, KPI-088, OP-002, OP-004, OP-007, OP-008, OP-009, OP-010, OP-011, OP-012, OP-013, OP-014, SP-031, TS-018, LG-024, CG-014]
priority: P2
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M23_Quality_Management_System.md §5, §9 — non-conformance, root cause and CAPA required before closure (BRU-QMS-02), recurrence escalates severity (BRU-QMS-09)
    verified: 2026-08-20
    class: P1
  - source: project_content/04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-021 §2.3 AL-07 — every Sev1 and Sev2 produces a post-incident review
    verified: 2026-08-20
    class: P1
  - source: project_content/13_Test_and_Acceptance_Content/TS-018_Defect_Taxonomy_Triage_and_Signoff_Forms.md §4.3 TR-07 — a recurring defect is reopened one severity higher and raises a non-conformance
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-072 security incident response with defined severities and breach-notification assessment; OPS-03 every alert has a runbook entry
    verified: 2026-08-20
    class: P1
  - source: ISO 9001:2015 clause 10.2 — nonconformity and corrective action, including evaluating the need to eliminate causes so that it does not recur
    verified: 2026-08-20
    class: P2
  - source: Google SRE — blameless postmortem practice; the review examines the system and the conditions, not the individual. https://sre.google/workbook/incident-response/
    verified: 2026-08-20
    class: P3
supersedes: none
review_due: 2027-02-20
---

# OP-016 — Post-Incident Review Template and Register

> **The purpose of a review is not to explain the incident. It is to change something.**
>
> A review that ends with a shared understanding and no owned, dated, tracked action has produced
> a feeling, not an improvement — and the same incident will be explained again in six months by
> different people who were not there the first time.

---

## 1. Purpose

**What stops without this file:**

| Absent | Consequence |
|---|---|
| A required trigger | Reviews happen for the incidents someone felt bad about, not the ones that matter |
| A blameless structure | People manage their exposure instead of describing what happened, and the review learns the wrong thing |
| A timeline method | The narrative is assembled from memory a week later and is wrong in the details that matter |
| An action model | "We should improve monitoring" is written down and nothing changes |
| A register | Recurrence is invisible; the fourth occurrence is experienced as the first |
| A link to the quality system | `M23` `BRU-QMS-02` requires root cause and CAPA before a non-conformance closes; without the link, incident actions live outside the only tracking system with teeth |

**Who requires it:** [`NT-021`](../04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-021_System_Integration_and_Job_Failure_Alert_Library.md) `AL-07` (every `Sev1` and `Sev2`), [`OP-013`](OP-013_On_Call_Escalation_and_Handover_Content.md) §4.1, every runbook §11,
[`OP-002`](OP-002_Hypercare_Plan_and_Exit_Criteria.md) `HX-17` (hypercare exit), [`OP-012`](OP-012_Disaster_Recovery_and_Continuity_Playbook.md) §11 (after a disaster), and `ISO 9001:2015` cl. 10.2.

---

## 2. Scope

**In scope:** when a review is required; the blameless principle and what it does and does not
mean; the timeline method; contributing-factor analysis; the review meeting; the report template;
the action model and its route into `M23`; the register; publication; recurrence detection; and the
measures that show whether reviews are working.

**Out of scope:**

| Situation | Owned by |
|---|---|
| Running the incident itself | `OP-013` |
| Incident communication, including the customer-facing summary | [`OP-004`](OP-004_Incident_Communication_Template_Set.md) |
| Defect triage and severity | [`TS-018`](../13_Test_and_Acceptance_Content/TS-018_Defect_Taxonomy_Triage_and_Signoff_Forms.md) |
| Problem management (the ongoing investigation a review may open) | [`SP-031`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) §8 |
| Non-conformance and CAPA mechanics | `M23` |
| Regulatory notification decisions | [`LG-024`](../10_Legal_Policy_and_Compliance/LG-024_Regulatory_Disclosure_and_Statutory_Notice_Register.md), `OP-004` §2.6 |
| Disciplinary process | HR — deliberately and completely separate (§4.2) |
| Service complaints from customers | [`SP-028`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md) / complaint handling |

---

## 3. Audience

| Reader | Uses this file to |
|---|---|
| Incident Commanders | Know what to capture during the incident, so the review is possible afterwards |
| Review facilitators | Run a review that produces change |
| Engineers and branch staff involved | Know they are describing a system, not defending themselves |
| Quality Manager | Route actions into `M23` and evidence `ISO 9001` cl. 10.2 |
| CTO and Operations Director | See recurrence and act on it |
| Internal Audit | Evidence that incidents are learned from |
| Steering Committee | Read the quarterly pattern, not individual reports |

---

## 4. Content

### 4.1 When a review is required

| Trigger | Review type | Deadline | Facilitator |
|---|---|---|---|
| **Any `Sev1`** | Full | **5 working days** | Independent facilitator — not the Incident Commander |
| **Any `Sev2`** | Full | 10 working days | Independent facilitator |
| Any incident with suspected personal-data involvement | Full, **with the DPO** | 5 working days | Facilitator + DPO |
| Any use of break-glass access | Full or focused, by judgement | 5 working days | Security |
| Any rollback of a wave or release (`OP-002` `RB-04`) | Full | 10 working days | Programme Office |
| Any invoked disaster (`OP-012`) | Full, extended | 10 working days | Risk |
| **A third occurrence of the same cause in 90 days** | Full, escalated to problem management | 5 working days | Quality Manager |
| A near miss that would have been `Sev1` | Focused | 10 working days | Facilitator |
| `Sev3` recurring | Focused | 20 working days | Team lead |
| A false-green monitoring failure ([`OP-010`](OP-010_Runbook_Data_Platform_and_Warehouse.md) §5) | Focused | 10 working days | Platform |
| A failed DR or fallback drill | Focused | 10 working days | Risk / Operations |

| # | Rule |
|---|---|
| **RV-01** | The review is scheduled **when the incident is declared**, not when it is resolved. A meeting nobody has booked is a meeting that slips past the point of memory |
| **RV-02** | **Near misses are reviewed.** The best incidents to learn from are the ones that did not become incidents, because nobody is defensive about them |
| **RV-03** | A review may be **waived only by the CTO**, in writing, with the reason recorded in the register. The register shows waivers, so a pattern of waivers is visible |
| **RV-04** | The facilitator is **not** the person who ran or fixed the incident |

### 4.2 Blameless — what it means and what it does not

| Blameless **means** | Blameless does **not** mean |
|---|---|
| The review asks how the system allowed a reasonable action to have a bad outcome | That nothing was done wrong |
| People describe what they did and why it made sense **at the time** | That performance issues are never addressed — they are, **separately**, through HR, never through this document |
| Names appear in the timeline as roles ("the on-call engineer"), not as accountability | That the incident record is anonymous to the participants; they know who was there |
| Findings attach to conditions: alerting, documentation, access, training, time pressure, tooling | That "human error" is an acceptable conclusion — it is a **starting point**, never a finding |
| The report is **published internally without names** | That the report is hidden |

> **`BL-01`.** If a review's output would change depending on who is in the room, the review is not
> blameless yet. The test is applied by the facilitator before the report is issued.
>
> **`BL-02`.** The single sentence that makes this real, and which the facilitator says at the start
> of every review: *"We are here to find out what made this outcome likely, not who produced it. If
> the answer is that a person made a mistake, the question becomes what made that mistake easy."*

### 4.3 Evidence — captured during, not after

The Scribe's timeline (`OP-013` §4.6) is the primary evidence. The review additionally collects:

| Evidence | Source | Captured by |
|---|---|---|
| Timeline of actions and decisions | Incident record / Scribe | During |
| Alerts fired, and when | `NT-021` alerting system | During |
| Monitoring data across the window | Grafana / logs | **During — retention windows expire** |
| Deployment and change history, 24 h before | Change register (`SP-031`) | After |
| Communications sent and their timings | `OP-004` message log | After |
| Fallback invoked, and how it performed | [`OP-014`](OP-014_Manual_Fallback_Procedure_Set.md) closure record | After |
| Business impact — jobs, money, customers, SLA | Operations + Finance | After |
| Customer contacts arising | [`OP-001`](OP-001_Support_Model_Tiering_and_Routing_Content.md) ticket system | After |
| What responders believed at each point | Interviews | Within 3 working days, **while memory is accurate** |

**`EV-01`.** Diagnostic evidence is captured **before** remediation destroys it ([`OP-007`](OP-007_Runbook_Core_ERP_Platform.md) §6 step
3). This is the single most common regret in incident reviews and the reason it appears in every
runbook's first-five-minutes list.

### 4.4 Contributing factors, not a root cause

Complex systems fail for several reasons at once. A single "root cause" is almost always the last
thing that changed, which is rarely the thing worth fixing.

| Layer | Question |
|---|---|
| **Trigger** | What changed or happened immediately before? |
| **Technical conditions** | What in the design or configuration made this failure possible or its impact wide? |
| **Detection** | How was it noticed? Monitoring or a human? How long did that take, and why? |
| **Response** | What slowed the response — access, knowledge, authority, tooling, availability of a person? |
| **Organisational** | What decisions, priorities or constraints made this state likely — deferred work, an unfunded control, a rota gap? |
| **Mitigation** | What limited the damage? **Name it — it is as important as the cause and it is what must be protected** |

| # | Rule |
|---|---|
| **CF-01** | At least **three** contributing factors are recorded, across at least two layers. One factor means the analysis stopped early |
| **CF-02** | "Human error" is never a factor. The factor is what made the error likely and undetected |
| **CF-03** | "Third-party failure" is never a complete factor. The factor is **our** exposure to it and the state of our fallback (`OP-014`) |
| **CF-04** | Every review names **what went well**. Reviews that only find faults stop being attended honestly |

### 4.5 The review meeting

| Item | Value |
|---|---|
| Timing | Within the §4.1 deadline; ideally 2–4 working days after resolution |
| Duration | 60 minutes (`Sev2`), 90 minutes (`Sev1`) |
| Chair | Independent facilitator |
| Attendees | Everyone who acted, the service owner, Support, and the business owner of the affected process. **`Sev1`: the CTO** |
| Preparation | Timeline circulated **beforehand** — the meeting corrects and interprets it, it does not build it |
| Structure | 10 min timeline walk-through · 25 min contributing factors · 10 min what went well · 25 min actions and owners · 10 min publication and follow-up |
| Output | Draft report within 2 working days; final within the §4.1 deadline |

### 4.6 The report template

```
POST-INCIDENT REVIEW                                    PIR-YYYY-nnn
Incident: INC-YYYY-nnnn      Severity: Sev_      Review type: Full / Focused
Occurred: ____ to ____ (duration ____)           Facilitator: ____________
Service(s): ______________________               Report date: ____________

1. SUMMARY  (five sentences, readable by someone outside engineering)
   What happened, who was affected, how long, how it was resolved, what is changing.

2. IMPACT
   Customers affected: ____        Jobs affected: ____
   Revenue at risk / lost: ____    SLA breaches: ____
   Statutory or contractual obligation affected: ____
   Personal data involved:  ☐ No  ☐ Yes → DPO assessment ref: ______ (OP-004 §2.6)
   Internal effort consumed: ____ person-hours

3. TIMELINE   (times in BST; roles not names)
   HH:MM  Event / action / decision                                  Source
   -----  -------------------------------------------------------  --------

4. DETECTION
   How detected: ☐ Monitoring  ☐ User report  ☐ Customer  ☐ Third party  ☐ Chance
   Time from onset to detection: ____     to declaration: ____     to first comms: ____
   Did an alert exist for this condition?  ☐ Yes, fired  ☐ Yes, did not fire  ☐ No alert

5. CONTRIBUTING FACTORS   (minimum three, across at least two layers — CF-01)
   Trigger:
   Technical conditions:
   Detection:
   Response:
   Organisational:
   Mitigations that limited the damage:

6. WHAT WENT WELL   (CF-04)

7. WHAT MADE IT HARDER
   (Missing runbook step, unclear authority, absent access, unreachable person, noisy alerts)

8. ACTIONS
   #  Action                        Type        Owner      Due       Tracked in
   -- ----------------------------- ----------- ---------- --------- --------------
   Type: Prevent / Detect / Mitigate / Respond / Document
   Every action is one of those five. "Discuss", "consider" and "review" are not actions.

9. RECURRENCE
   Has this or a similar cause occurred before?  ☐ No  ☐ Yes → PIR refs: ______
   If yes, is a problem record open (SP-031 §8)?  ☐ Yes ref ____  ☐ Opening now
   Non-conformance raised in M23?  ☐ Yes ref ____  ☐ Not required, because ______

10. RUNBOOK AND CONTENT CHANGES        (RC-01: within 2 working days)
    Runbook(s) changed: ______   Alert(s) added/removed (NT-021): ______
    Macros or help content (OP-003 / HC): ______   Fallback (OP-014): ______

11. PUBLICATION
    Internal publication date: ______
    Customer summary required (Sev1)?  ☐ Yes → OP-004 template 21, issued ______  ☐ No
    Corporate client notification?      ☐ Yes → refs ______   ☐ No

SIGN-OFF   Facilitator ________  Service owner ________  Quality Manager ________
           CTO (Sev1) ________
```

### 4.7 Actions

| Rule | Detail |
|---|---|
| **AC-01** | Every action has **one named owner** — never a team, never "Platform" |
| **AC-02** | Every action has a **date**, and the date is realistic. A deliberately generous date that is met beats an optimistic one that is not |
| **AC-03** | Every action is classified **Prevent / Detect / Mitigate / Respond / Document**. A review whose actions are all *Document* has not changed the system |
| **AC-04** | **At least one action must be *Detect* or *Prevent*** for any `Sev1`. If the honest answer is that neither is possible, that is recorded explicitly and escalated — it means the exposure remains |
| **AC-05** | Actions are tracked in **`M23`** as corrective actions, not in a private list. `BRU-QMS-02` requires root cause and CAPA before closure |
| **AC-06** | An action still open at its due date is **escalated to the CTO**, not silently extended |
| **AC-07** | Actions are closed with **evidence** — the alert exists, the runbook says it, the test passes — not with an assertion |
| **AC-08** | **Actions that will not be done are closed as "accepted risk"**, with a named accepter, and recorded in the risk register (`M60`). This is honest; an action left open for a year is not |

### 4.8 The register

Every review, whether or not it produced actions.

| Field | Notes |
|---|---|
| PIR reference | `PIR-YYYY-nnn` |
| Incident reference | `INC-YYYY-nnnn` |
| Date of incident / of review / of report | Three dates — the gaps between them are a measure |
| Severity | `OP-013` §4.1 |
| Service(s) affected | For pattern analysis |
| Detection method | Monitoring / user / customer / third party / chance |
| Duration and impact summary | |
| Contributing factor tags | Controlled vocabulary (§4.9) |
| Personal data involved | Yes/No + DPO assessment reference |
| Actions: total / open / overdue / accepted-risk | Live |
| Recurrence link | Prior PIRs with the same tags |
| Problem record | `SP-031` §8 reference |
| Non-conformance | `M23` reference |
| Published internally | Date |
| Customer summary published | Date or n/a |
| Waived | Only with a CTO reason (`RV-03`) |

**`RG-01`.** The register is reviewed **monthly** by the Quality Manager and the CTO, and reported
**quarterly** to the Steering Committee as a pattern — top contributing-factor tags, action
closure rate, recurrence count — not as a list of incidents.

### 4.9 Contributing-factor tags

A controlled vocabulary, because free text cannot be counted and patterns are the entire value of
the register.

| Tag | Meaning |
|---|---|
| `capacity` | Resource exhaustion — connections, storage, workers, queue |
| `config` | Configuration error or drift |
| `deploy` | Introduced by a release or change |
| `migration` | Schema or data migration |
| `dependency-3p` | Third-party service failure |
| `integration` | Contract, schema, idempotency or replay |
| `identity` | Authentication, authorisation, session, access |
| `data-quality` | Wrong or stale data, reconciliation divergence |
| `monitoring-gap` | No alert, or an alert that did not fire |
| `alert-noise` | The signal existed and was lost in noise |
| `runbook-gap` | No procedure, or a procedure that was wrong |
| `access-gap` | The responder lacked the access to act (`OP-013` `RT-07`) |
| `authority-gap` | The responder lacked the authority, or could not find who had it |
| `single-person` | Only one person could do it |
| `fallback-failure` | The manual fallback did not work (`OP-014`) |
| `comms-gap` | The affected population was not told, or told late or wrongly |
| `capacity-human` | Fatigue, rota load, concurrent incidents |
| `deferred-work` | A known, recorded risk that had not been funded or scheduled |
| `training-gap` | The action was reasonable but uninformed |
| `vendor-contract` | The remedy depended on a contract we do not hold |

**`TG-01`.** `deferred-work`, `single-person` and `authority-gap` are the three tags that indicate
an **organisational** rather than technical cause. If they dominate a quarter, the report goes to
the Steering Committee with that stated plainly, because no engineering action will address them.

### 4.10 Publication

| Audience | What | When |
|---|---|---|
| Internal, all staff | The full report **without names**, in the knowledge base | Within 2 working days of sign-off |
| Affected population | A short summary through the channel that carried the incident (`OP-004` template 20) | With publication |
| Customers (`Sev1`) | `OP-004` template 21 — plain language, no technical detail that assists an attacker | Within the §4.1 deadline |
| Status page | Summary appended to the incident record ([`OP-005`](OP-005_Status_Page_and_Maintenance_Notice_Copy.md) `SP-07`) | With publication |
| Corporate clients with contractual rights | The report or an agreed extract, by the account manager | Per contract |
| Steering Committee | Quarterly pattern, not individual reports | Quarterly |

**`PB-01`.** Reviews are published **by default**. A review withheld requires a stated reason
(security detail, legal privilege, personal data) recorded in the register — and even then, a
redacted version is published, because a culture that reviews privately stops reviewing honestly.

### 4.11 Measurement

| Measure | Target | Why |
|---|---|---|
| Reviews completed within deadline | ≥ 95% | Late reviews are inaccurate reviews |
| `Sev1`/`Sev2` with a review | **100%** (`AL-07`) | The trigger is not discretionary |
| Actions closed by due date | ≥ 85% | Below this, reviews are theatre |
| Actions overdue > 30 days | Zero | `AC-06` |
| `Prevent`/`Detect` actions per `Sev1` | ≥ 1 | `AC-04` |
| Recurrence within 90 days | Declining; each occurrence is a failure of a previous review | The measure that matters most |
| Detection by monitoring | ≥ 90% | `KPI-088` context |
| Runbook updates within 2 working days | 100% | `RC-01`, `OP-002` `HX-14` |
| Waived reviews | Zero, or explained | `RV-03` |

### 4.12 Open decisions

| # | Decision required | Owner | Needed by | Consequence if unresolved |
|---|---|---|---|---|
| **OP-016-OI-01** | **Wave conflict.** This file is `W2`, but `NT-021` `AL-07` requires a review for every `Sev1`/`Sev2` from `W1`, and `OP-002` `HX-17` makes reviews a W1 hypercare exit criterion. **It is needed at W1** | Programme Office | W1 | The first wave's incidents are reviewed without a method, or not reviewed |
| **OP-016-OI-02** | `M23` is the action tracker (`AC-05`), but confirm its delivery wave — if it is later than W1, actions need an interim register | Quality Manager + CTO | W1 | Actions live in a spreadsheet with no escalation |
| **OP-016-OI-03** | Independent facilitators (`RV-04`) require people who were not involved. In a small platform team, that pool may be one person | CTO | W1 | Independence is nominal |
| **OP-016-OI-04** | Confirm with HR that the separation in §4.2 is formally endorsed — blamelessness fails the first time a review is used in a performance conversation | HR Director + CTO | W1 | Responders manage exposure and reviews learn nothing |
| **OP-016-OI-05** | Publication default (`PB-01`) needs Legal's agreement on what may be published where a customer or a vendor is identifiable | Legal Counsel | W2 | Publication stalls case by case |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `OP-013` | Severity, the incident record and the Scribe's timeline |
| `NT-021` `AL-07` | The trigger for every review |
| `OP-004` | Communication of the summary, internal and customer |
| `OP-007`…`OP-012` §11 | Each runbook's standing review questions |
| `OP-014` | Fallback performance is reviewed here |
| `M23` | Non-conformance and CAPA tracking (`AC-05`) |
| `M60` | Risk register for accepted risks (`AC-08`) |
| `SP-031` §8 | Problem management for recurring causes |
| `TS-018` | Defects arising from an incident |
| `LG-024`, `OP-004` §2.6 | Regulatory assessment where personal data is involved |
| [`CG-014`](../00_Content_Governance_and_Standards/CG-014_Content_Metrics_and_Effectiveness_Measurement.md) | Content-effectiveness measures that consume review findings |

**Depended on by:** `OP-002` (`HX-17`) · `OP-007`…`OP-012` · `OP-013` · `NT-021` · [`SP-005`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md) ·
`M23` · Internal Audit · the Steering Committee's quarterly pack.

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Annually; the tag vocabulary (§4.9) quarterly for the first year |
| Trigger for out-of-cycle review | Action closure rate below 85% for two quarters · any recurrence at a fourth occurrence · a review found to have been shaped by blame · `M23` go-live |
| Owner | Support with Quality |
| Retention | Reviews and the register retained **7 years** (`NFR-088`); they are quality records under `ISO 9001:2015` cl. 7.5.3 |
| Change route | [`CG-006`](../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md); changes to the template require Quality Manager approval |

---

## Open Items

1. **OP-016-OI-01** — required at W1, registered at W2.
2. **OP-016-OI-02** — `M23` availability at W1 unconfirmed; actions may have no tracker.
3. **OP-016-OI-03** — facilitator independence may not be achievable in a small team.
4. **OP-016-OI-04** — HR endorsement of blamelessness not formalised.
5. **OP-016-OI-05** — publication default needs Legal agreement.
6. The contributing-factor tag vocabulary (§4.9) is new to the programme and will need one
   revision after the first quarter of real use — a vocabulary that no incident matches is as
   useless as free text.

---

## Definition of Done

Tick every box before setting `status: Approved`. Full checklist in [`CG-008`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md).

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — all six sections present; `Open Items` added, justified
- [x] Every factual, statutory, pricing or capability claim carries a source and a verification date
- [x] Terminology matches [`CG-004`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md)
- [x] All internal links resolve
- [ ] Accessibility standard [`CG-011`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) — n/a; internal governance
- [x] Bengali counterpart — n/a; English-only by [`CG-010`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) §3.2
- [ ] Named approver recorded — Quality Manager; CTO co-approval for §4.1 and §4.7
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] Decision(s) taken while authoring logged in `RF-006` — five open decisions pending

**Gates required (Class C):** G1 ●, G2 ●, G3 ●. G4 n/a.

---

*`OP-016` · 1000FiX ERP Programme · CONFIDENTIAL — Internal Use Only*
