---
id: OP-013
title: On-Call, Escalation and Handover Content
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering
author: Platform Engineering with Support Lead and HR
reviewers: [Chief Technology Officer, Operations Director, Security Lead, Support Lead, HR Director, Legal Counsel, Internal Audit]
approver: Chief Technology Officer
content_class: C
purpose: >
  Owns the platform incident severity scale for the whole programme, and defines the rota, the
  paging and acknowledgement rules, the declaration and Incident Commander roles, the escalation
  ladder, the authority each role holds, and the shift handover format. Escalation ambiguity at
  02:00 is the difference between a 20-minute incident and a four-hour one, and severity defined
  in four places is severity defined nowhere.
traces_to: [M66, M28, M29, SP-005, SP-031, MD-028, NT-021, TS-018, OP-001, OP-004, OP-007, OP-008, OP-009, OP-012, OP-014, OP-016, 05-06 NFR-045, NFR-072, KPI-085, KPI-088]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-021 §2.1 — Sev1–Sev4 definitions and routing, published 2026-08-15; §2.3 AL-06, AL-07
    verified: 2026-08-20
    class: P1
  - source: project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md §4, §5 — escalation destinations, acknowledgement, out-of-hours cover; and its cross-reference of technical severity to OP-008
    verified: 2026-08-20
    class: P1
  - source: project_content/13_Test_and_Acceptance_Content/TS-018_Defect_Taxonomy_Triage_and_Signoff_Forms.md §4.1, §4.5 — S1–S4 defect severity, and the statement that three severity scales exist and are linked, never merged
    verified: 2026-08-20
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028 — service priority and severity scales for service orders
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-045 24×7 availability ≥ 99.7%; NFR-072 security incident response with defined severities
    verified: 2026-08-20
    class: P1
  - source: Incident command practice — named Incident Commander, Communications Lead and Scribe; the commander coordinates and does not troubleshoot. https://www.atlassian.com/incident-management/incident-response/incident-commander
    verified: 2026-08-20
    class: P3
supersedes: none
review_due: 2027-02-20
---

# OP-013 — On-Call, Escalation and Handover

> **This file owns the platform incident severity scale.** Three other files currently point
> somewhere else for it (§4.2). If you take one thing from this document, take the severity table
> in §4.1 and the authority table in §4.8 — they are what an engineer needs at 02:00, and everything
> else here exists to make those two usable.

---

## 1. Purpose

At 02:00 the questions are always the same: *is this bad enough to wake someone? who? am I allowed
to restart it? who tells the customers? when do I hand over?* An organisation answers those
questions in advance or it answers them badly.

**What stops without this file:**

| Absent | Consequence |
|---|---|
| One severity scale | [`NT-021`](../04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-021_System_Integration_and_Job_Failure_Alert_Library.md) alerts fire at a severity no other document defines; [`OP-004`](OP-004_Incident_Communication_Template_Set.md) communication triggers on a scale nobody owns; two people classify the same event differently and one of them does not call anybody |
| A rota | Out-of-hours cover is "whoever answers", which in practice is the same two people every night until they leave |
| Acknowledgement rules | A page that nobody acknowledges looks identical to a page somebody is working |
| A declaration rule | Nobody declares, because declaring feels like escalating, and the incident runs for an hour as "an investigation" |
| An authority table | The engineer who can fix it waits for permission from someone asleep |
| A handover format | The night shift's knowledge evaporates at 08:00 and the day shift starts the diagnosis again |

---

## 2. Scope

**In scope:** the platform incident severity scale; the relationship between the programme's four
severity/priority scales; the on-call rota and its cover model; paging, acknowledgement and
auto-escalation; incident declaration; incident roles; the escalation ladder; authority to act;
shift and incident handover formats; out-of-band communications; on-call load limits; and the
measures that show whether on-call is working.

**Out of scope:**

| Situation | Owned by |
|---|---|
| Business, commercial, safety and legal escalation destinations | [`SP-005`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md) |
| Support tiers and routing of ordinary contacts | [`OP-001`](OP-001_Support_Model_Tiering_and_Routing_Content.md) |
| Service-order priority and SLA bands | [`MD-028`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md) |
| Defect severity `S1`–`S4` | [`TS-018`](../13_Test_and_Acceptance_Content/TS-018_Defect_Taxonomy_Triage_and_Signoff_Forms.md) |
| Incident communication wording | `OP-004` |
| Technical procedures for any component | [`OP-007`](OP-007_Runbook_Core_ERP_Platform.md)…[`OP-011`](OP-011_Runbook_Portal_and_Mobile_App_Operations.md) |
| Disaster declaration and crisis roles | [`OP-012`](OP-012_Disaster_Recovery_and_Continuity_Playbook.md) |
| Post-incident review | [`OP-016`](OP-016_Post_Incident_Review_Template_and_Register.md) |
| On-call allowance and employment terms | HR policy — referenced in §4.11, not set here |

---

## 3. Audience

| Reader | Uses this file to |
|---|---|
| On-call engineers | Know what to do when paged, and what they may do without asking |
| Incident Commanders | Run an incident |
| Support Lead and T1 | Know when to page rather than queue |
| Security | Know how a security event enters the same machinery |
| CTO and Operations Director | Know when they will be called, and for what |
| HR | Understand the rota's people implications |
| Internal Audit | Evidence that incidents are governed, not improvised |

---

## 4. Content

### 4.1 The platform incident severity scale — canonical

This scale describes **the system**. It is the scale referenced by `NT-021` alerts, `OP-004`
communications, every runbook's §6, and `OP-016`. The `Sev1`–`Sev4` definitions are carried forward
verbatim in intent from `NT-021` §2.1 (published 2026-08-15) and extended here with response,
authority and communication obligations.

| | **Sev1** | **Sev2** | **Sev3** | **Sev4** |
|---|---|---|---|---|
| **Definition** (`NT-021` §2.1) | Customer-facing path down — payments, booking, OTP | Degraded but working, **or** an internal path down | Single integration failing with a working fallback | Informational — a threshold approached |
| **Also Sev1, regardless of impact** | Suspected personal-data or security compromise · data loss or corruption in a system of record · a statutory output cannot be produced on its deadline · unsynced field work at risk (`OP-011` §6) | | | |
| **Examples** | All payment gateways unreachable · nobody can sign in · the technician app is losing work · the ERP is down in business hours | Dispatch board slow under load · one branch cannot print · invoicing delayed · warehouse loads failing during close | One courier integration down with manual booking available · a non-critical batch failed and can rerun | Disk at 70% · certificate expiring in 30 days · queue depth rising but draining |
| **Detection to page** | Immediate, 24×7 | Immediate in hours; queued 22:00–08:00 unless customer-affecting | Ticket | Dashboard only |
| **Acknowledge within** | **5 minutes** | 15 min in hours, 60 min out of hours | 4 working hours | — |
| **Declaration** | Mandatory, immediately | Mandatory | Ticket only | No |
| **Incident Commander** | **Required** | Required if it lasts > 60 min or spans teams | No | No |
| **Update cadence** | 30 minutes | 2 hours | Daily | — |
| **Communication** (`OP-004`) | Internal ≤ 15 min · status page ≤ 15 min · customers ≤ 30 min where customer-facing | Internal ≤ 30 min; external only if visible | Ticket | — |
| **Restoration target** | ≤ 2 h (`NFR-007` where failover applies) | ≤ 8 working hours | ≤ 5 working days | Next release |
| **Business escalation** | Operations Director + CTO at declaration | CTO at 2 h | — | — |
| **Post-incident review** | **Mandatory**, within 5 working days | **Mandatory**, within 10 working days (`NT-021` AL-07) | Only if recurring | No |
| **May be downgraded by** | Incident Commander **with** CTO agreement | Incident Commander | On-call engineer | — |

| # | Rule |
|---|---|
| **SV-01** | **Anyone may declare any severity.** Over-declaring is corrected in minutes; under-declaring is discovered in hours |
| **SV-02** | **Severity is set on impact, not on cause.** A one-line configuration error that stops payments is a `Sev1` |
| **SV-03** | Severity is **re-assessed as understanding changes**, and each change is timestamped in the incident record |
| **SV-04** | **Downgrade requires more authority than upgrade** (`SV-01` vs the table above). This asymmetry is deliberate |
| **SV-05** | Severity is **never adjusted to avoid a review, a metric or an awkward conversation** — the mirror of `TS-018` `TR-09` |
| **SV-06** | An incident affecting **multiple branches or the whole field fleet** is `Sev1` even where each individual effect looks minor |
| **SV-07** | A `Sev1` that turns out to have been over-declared is closed with a one-line note. **No review of the declarer, ever** |

### 4.2 The four scales — and which file owns each

The programme runs four distinct severity or priority scales. Confusing them is the most common
source of argument in an incident, and the register currently contains three conflicting pointers
to the owner of this one.

| Scale | Values | Measures | Owned by | Used in |
|---|---|---|---|---|
| **Platform incident severity** | `Sev1`–`Sev4` | The system's condition | **`OP-013` §4.1 — this file** | `NT-021`, `OP-004`, `OP-007`…`OP-012`, `OP-016` |
| **Defect severity** | `S1`–`S4` | How wrong the software is | `TS-018` §4.1 | Test, triage, deferral, wave gates |
| **Service priority and severity** | critical / high / medium / low, with SLA bands | The customer's service order | `MD-028` | Dispatch, SLA clocks, escalation timers |
| **Internal IT ticket priority** | Impact × urgency → priority | An employee's IT request or incident | `M66` (`FR-ITS-009`) | Service desk queues |

**Relationships, and only these:**

| From | To | Relationship |
|---|---|---|
| A `Sev1`/`Sev2` incident | A defect | An incident *may* produce a defect record (`TS-018`); the defect keeps its own severity |
| A `Sev1` affecting job delivery | Service SLA | May pause SLA clocks in bulk, on the Operations Director's decision, evidenced by the incident record (`OP-001` §4.6) |
| An internal IT ticket | An incident | A ticket becomes an incident when the cause is the platform, not the user. **The ticket does not change scale — a second record is created and linked** |
| A recurring incident | A problem | [`SP-031`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) §8; the problem record has no severity of its own |

> **Register conflict, recorded.** `SP-005` §5 and §12 and `SP-031` §2 both direct readers to
> **[`OP-008`](OP-008_Runbook_Integration_and_Event_Platform.md)** for "technical severity classification"; `TS-018` §2 names **`M66`, `SP-031`,
> [`OP-002`](OP-002_Hypercare_Plan_and_Exit_Criteria.md)**. None of those is correct: `OP-008` is a component runbook, `OP-002` is the hypercare
> plan, and `M66` owns *ticket* priority. **The scale lives here.** Three one-line corrections are
> required upstream, raised in the Category 17 audit. Until they are made, an engineer following
> `SP-005` reaches a runbook with no severity table in it.

### 4.3 The rota

| Rota | Covers | Hours | Minimum members |
|---|---|---|---|
| **Platform primary** | ERP core, integration, portals, apps | 24×7 | **6** |
| **Platform secondary** | Backup for primary; second pair of hands on `Sev1` | 24×7 | 6 (same pool, offset) |
| **Security on-call** | Identity, suspected compromise, data incidents ([`OP-009`](OP-009_Runbook_Identity_and_Access.md)) | 24×7 | **4** |
| **Business escalation** | Operations Director / duty manager for business decisions | 24×7 | 4 |
| **Executive escalation** | CTO, with a named deputy | 24×7 | 2 |
| **Data engineering** | Warehouse and pipelines ([`OP-010`](OP-010_Runbook_Data_Platform_and_Warehouse.md)) | **Business hours**, extended during close | 2 |

**The arithmetic that decides whether this is sustainable.** A 24×7 primary rota on one-week
shifts needs **six people** for a one-in-six rotation. At four it is one-in-four, which is the point
at which people leave; at three it is unsafe and the rota becomes two people plus a fiction.

> **Stated plainly:** the programme does not currently have six platform engineers identified for
> a rota, and `M66` §11 Q-02 records the same unanswered question for IT staffing. **Until the rota
> is staffed, `NFR-045`'s 24×7 availability target is not operationally supported** — open item
> OI-01.

**Rota rules**

| # | Rule |
|---|---|
| **RT-01** | The rota is published **at least four weeks ahead** and is visible to Support, Operations and the executive |
| **RT-02** | Every shift has a **named primary and a named secondary**. "The team" is not a rota entry |
| **RT-03** | Swaps are allowed and are **recorded before the shift**, not after the page |
| **RT-04** | Nobody is on call for more than **one week in three** sustained, or **two consecutive weeks** at all |
| **RT-05** | An engineer who worked a `Sev1` past 01:00 **does not start the next working day before 12:00**, and this is an instruction to their manager, not a request from them |
| **RT-06** | New joiners shadow **two full shifts** before holding a rota position |
| **RT-07** | The rota holder must have **the access needed to act** — an on-call engineer without production authority is a pager with no hands (`OP-009`, [`OP-015`](OP-015_Access_Request_and_Joiner_Mover_Leaver_Content.md)) |
| **RT-08** | Public holidays and Ramadan/Eid periods are planned **explicitly**, not inherited from the ordinary pattern |

### 4.4 Paging, acknowledgement and auto-escalation

| Step | Rule |
|---|---|
| 1 | Alerts route per `NT-021`: `Sev1` pages immediately (`AL-06`), `Sev2` pages in hours, `Sev3` creates a ticket, `Sev4` is dashboard only |
| 2 | A page **acknowledged** means "I am awake, I have seen it, I am acting" — it does not mean resolved |
| 3 | Unacknowledged `Sev1` after **5 minutes** → page the secondary. After **10 minutes** → page the platform lead. After **15 minutes** → page the CTO |
| 4 | Unacknowledged `Sev2` after **15 minutes** in hours → secondary; after 30 → lead |
| 5 | Repeat alerts for one condition are suppressed to one per window, with the count carried (`NT-021` `AL-04`); suppression **never silences a `Sev1`** |
| 6 | An alert that fires more than **20 times a week without action** is reviewed for deletion (`AL-05`) — noisy alerts are how real pages get missed |
| 7 | Every alert names its runbook (`AL-01`, `OPS-03`). **An alert without a runbook link is a defect in the alert** |
| 8 | Paging channels are tested **weekly** with a scheduled test page that must be acknowledged |

### 4.5 Declaration

| Question | Answer |
|---|---|
| Who may declare? | **Anyone** — on-call, T1, a branch manager, an executive (`SV-01`, `OP-001` `TR-07`) |
| How? | State: *"Declaring `Sev<n>`: `<what is affected>`, `<who is affected>`, `<what I have ruled out>`"* in the incident channel, and open the incident record |
| What happens automatically? | An incident reference is issued · the Incident Commander role is assigned · the communication clock starts (`OP-004`) · the status page is updated for `Sev1` |
| When is declaring wrong? | When the event is a **service** problem, not a platform problem — that follows `SP-005`. When in doubt, declare and let it be reclassified |
| What if the platform is down and the incident tooling with it? | Declare on the out-of-band channel (§4.10). The record is created afterwards, from the Scribe's timeline |

### 4.6 Incident roles

| Role | Who | Does | Does **not** do |
|---|---|---|---|
| **Incident Commander (IC)** | The on-call primary initially; handed to a senior engineer or the platform lead if it grows | Decides, coordinates, sets severity, assigns work, keeps the timeline moving, decides when to escalate | **Troubleshoot.** The moment the IC starts debugging, nobody is commanding |
| **Operations lead** | The engineer closest to the failing component | Diagnoses and fixes | Communicate externally |
| **Communications Owner** | Support Lead, Change Lead, or a delegate | Issues every message internal and external, updates the status page, holds the next-update commitment | Diagnose, or add facts the IC has not confirmed |
| **Scribe** | Named at declaration | Records every action, decision, time and owner | Anything else |
| **Business Decision Owner** | Operations Director or CFO by domain | Decides workaround acceptability, fallback invocation, customer impact acceptance | Direct technical work |
| **Subject-matter responders** | As paged | Their component | Change severity |

**Small-team reality.** Below `Sev1`, one person often holds IC, Ops and Comms. That is acceptable
and normal. **At `Sev1` the Scribe and the Communications Owner are always separate people from the
IC** — those are the two roles that fail silently when combined, and their failure is invisible
until the review.

### 4.7 Escalation ladder

| Level | Who | Triggered by | Time |
|:--:|---|---|---|
| L0 | On-call primary | The page | 0 |
| L1 | On-call secondary | Unacknowledged, or the primary asks | 5 min (`Sev1`) |
| L2 | Platform lead / Security Lead | `Sev1` at 30 min · any incident spanning two components · any suspected security event | 30 min |
| L3 | **CTO** | `Sev1` at 60 min · any data-loss or data-exposure suspicion · any decision above the on-call authority in §4.8 | 60 min |
| L4 | **Crisis Management Team** (`OP-012` §4.2) | `Sev1` at 2 h · RTO at risk · environment loss | 2 h |
| L5 | CEO / Board | Regulatory notification likely · material financial impact · media interest | On CTO judgement |

**Parallel escalations, which do not wait for the ladder:**

| Trigger | Goes immediately to |
|---|---|
| Suspected personal-data exposure | **DPO** (the `NFR-094` assessment clock runs from detection) |
| Suspected criminal act | Security Lead + Legal Counsel |
| Safety of a person | HSE, per [`SP-030`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md) — **before** any system consideration |
| Customer harm or statutory deadline at risk | Operations Director + CFO |
| Corporate client with contractual notification rights | Account Manager (`OP-004` template 6) |

### 4.8 Authority to act

The table an engineer reads at 02:00. **If it is in the "may act" column, act — do not wait for
permission and do not apologise for it afterwards.**

| Action | On-call may act | Needs platform lead | Needs CTO | Needs business (Ops Dir / CFO) |
|---|:--:|:--:|:--:|:--:|
| Restart a service or node | ✔ | | | |
| Scale a service within existing capacity | ✔ | | | |
| Fail over to a replica within the same environment | ✔ | | | |
| **Halt a mobile rollout** (`OP-011` `BG-20`) | ✔ | | | |
| Disable a feature flag | ✔ | | | |
| Open or close a circuit breaker | ✔ | | | |
| Invoke a manual fallback ([`OP-014`](OP-014_Manual_Fallback_Procedure_Set.md)) | ✔ | | | ✔ (informed immediately) |
| Suppress a noisy alert, time-boxed | ✔ | | | |
| Declare or upgrade severity | ✔ | | | |
| **Downgrade `Sev1`** | | ✔ | ✔ | |
| Emergency change to production (`SP-031`) | ✔ **as IC**, reviewed within 2 working days | ✔ | | |
| Roll back a deployment | ✔ | | | |
| Restore from backup (partial, isolated) | | ✔ | | |
| **Restore production from backup** (accepting data loss) | | | ✔ | ✔ CFO |
| **Invoke DR / declare a disaster** (`OP-012`) | | | ✔ | ✔ Ops Dir informed |
| Take a customer-facing service deliberately offline | | ✔ | ✔ | ✔ |
| Use break-glass access (`OP-009` §9) | | | ✔ | |
| Page a vendor under a support contract | ✔ | | | |
| Commit emergency spend | up to **BDT 25,000** | up to BDT 100,000 | above that | CFO above the CTO's limit |
| Contact a customer directly | | | | ✔ via Comms Owner only |
| Notify a regulator or the Authority | | | | **DPO/Legal only** |
| Decide SLA pauses for affected jobs | | | | ✔ Ops Dir |

> **`AU-01`.** The spend limits above are **proposed**; no delegated-authority schedule exists for
> operational emergency spend ([`SP-004`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md) covers procurement, not incident response). Open item OI-04.
> Until it is set, the CTO is the only spend authority, which is a single point of delay.

### 4.9 Handover

**Shift handover — used at every rota change, and at 08:00 after any overnight activity.**

```
ON-CALL HANDOVER            From: __________  To: __________   Time: ______ BST

OPEN INCIDENTS
  Ref | Sev | What is affected | State | Next action | Next update due | IC
  ----+-----+------------------+-------+-------------+-----------------+-----

WATCH LIST  (not an incident, but do not be surprised)
  • {system} — {symptom}, {since}, {what I checked}, {what would make it an incident}

CHANGES IN THE LAST 24 H
  • {release/change} at {time} by {who} — {rolled back? / stable?}

SUPPRESSED ALERTS AND THEIR EXPIRY
  • {alert} suppressed until {time} because {reason}     ← must expire, never open-ended

DEFERRED WORK
  • {what I chose not to do and why} — {who should pick it up}

ENVIRONMENT STATE
  • Anything non-standard: feature flags off, scaling changed, a node drained, a job paused

CONTACTS ENGAGED
  • Vendor {name}, ref {ref}, next chase {time}
  • Business contacts already spoken to, and what they were told

HANDOVER CONFIRMED BY RECEIVER:  ☐   (verbal or written acknowledgement required — silence is not handover)
```

**Incident handover — when an incident changes IC mid-flight.** The outgoing IC states, out loud
and in the record: current severity · what is confirmed · what is assumed · what has been ruled out
· who is doing what right now · when the next communication is due · what decision is pending and
who owns it. The incoming IC **repeats it back** before the handover completes.

| # | Rule |
|---|---|
| **HO-01** | Handover is **acknowledged**, never assumed. An unacknowledged handover leaves an incident with no owner |
| **HO-02** | **"Nothing happened" is a handover too**, and it is given in the same format |
| **HO-03** | Every suppressed alert has an expiry stated in the handover. Suppressions that outlive their incident are how the next incident is missed |
| **HO-04** | Handover is written **before** the outgoing engineer leaves, not from memory the next morning |

### 4.10 Out-of-band communications

The channel that must work when the estate does not. Referenced by `OP-004` §4, [`OP-005`](OP-005_Status_Page_and_Maintenance_Notice_Copy.md) §4 and
`OP-012` §2.

| Tier | Channel | Reaches | Independent of |
|:--:|---|---|---|
| 1 | Incident channel in the standard collaboration tool | Engineering, support, leadership | The ERP, but not the internet |
| 2 | **SMS via the failover gateway** (`INT-011`) | On-call, leadership, all branch managers | The primary SMS provider and the ERP |
| 3 | **Telephone tree** — CTO → leads → branch managers → branch staff | Everyone | All systems |
| 4 | Personal mobile numbers held for continuity, with a recorded lawful basis (`NFR-090`) | The named crisis roles | Everything |

| # | Rule |
|---|---|
| **OB-01** | The tier-3 telephone tree is **printed and held physically** at head office and at every branch. A tree stored only in the system it exists to survive is not a tree |
| **OB-02** | Contact details are verified **quarterly** (`OP-012` §3) |
| **OB-03** | The out-of-band channel is exercised in the DR communications drill (`OP-012` §11), target ≥ 90% of branches acknowledging within 30 minutes |
| **OB-04** | Personal numbers are used for continuity only, are held under a stated lawful basis, and are removed when someone leaves the role (`OP-015`) |

### 4.11 On-call load and welfare

On-call quality collapses when the load is unsustainable, and it collapses quietly — through
slower acknowledgement, then through resignations.

| Measure | Threshold | If exceeded |
|---|---|---|
| Pages per shift (week) | > 5 | Review alert quality (`AL-05`) and the underlying reliability; this is an engineering problem, not a staffing one |
| Pages outside 22:00–08:00 per shift | > 2 | Same, escalated to the CTO |
| Consecutive weeks on call | 2 | Rota breach — HR informed |
| `Sev1` past 01:00 | Any | `RT-05` late start applies automatically |
| Shifts covered by the same person in a quarter | > 5 | Rota is under-staffed; report to the Steering Committee |

**Compensation and time off in lieu are HR policy**, not set here. This file states only that **an
unpaid, unrecognised rota does not survive contact with the second month**, and that `NFR-045`'s
24×7 target depends on it.

### 4.12 Measurement

| Measure | Definition | Target | Source |
|---|---|---|---|
| Time to acknowledge (`Sev1`) | Page → acknowledgement | ≤ 5 min, 95th percentile | Paging system |
| Time to declare | First signal → declaration | ≤ 10 min | Incident record |
| Time to communicate | Declaration → first internal message | ≤ 15 min (`OP-004`) | Message log |
| Time to restore | Declaration → verified restoration | `Sev1` ≤ 2 h | Incident record |
| **Detection source** | Monitoring vs human report | ≥ 90% detected by monitoring (`KPI-088` context) | Incident record |
| Auto-escalations | Pages escalated because unacknowledged | < 5% | Paging system |
| Handover completeness | Handovers with every section completed | 100% | Handover log |
| Repeat incidents | Same cause within 90 days | Declining; each one is a `OP-016` failure to act | Incident register |
| Rota health | Members, one-in-N, breaches | ≥ 6 members, no breaches | Rota |

### 4.13 Open decisions

| # | Decision required | Owner | Needed by | Consequence if unresolved |
|---|---|---|---|---|
| **OP-013-OI-01** | **Staff the rota to six platform and four security members** | CTO + HR | Before W1 go-live | 24×7 cover (`NFR-045`) is a target with no rota behind it |
| **OP-013-OI-02** | Correct `SP-005` §5/§12 and `SP-031` §2 to point at `OP-013` §4.1 for severity, and `TS-018` §2 likewise | Business Process Lead + QA Lead | W1 | Engineers following the SOPs reach files that do not define severity |
| **OP-013-OI-03** | Agree on-call allowance and time-in-lieu with HR | CTO + HR Director | Before W1 | `RT-04`/`RT-05` are unenforceable and the rota erodes |
| **OP-013-OI-04** | Set an operational **emergency spend delegation** (§4.8) | CFO | W1 | Every emergency purchase waits for the CTO |
| **OP-013-OI-05** | Confirm paging tooling — `M66` does not arrive until W6 and no paging platform is named in `02-05` | CTO | **W1** | §4.4 describes paging the programme cannot perform |
| **OP-013-OI-06** | Confirm that branch managers accept being on the tier-2 SMS list and the tier-3 tree | Operations Director | W1 | The out-of-band channel is untested and possibly unwelcome |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `NT-021` | Alert routing and the original `Sev1`–`Sev4` wording |
| `SP-005` | Business, safety and legal escalation beyond the technical ladder |
| `SP-031` | Emergency change process the IC invokes |
| `MD-028`, `TS-018`, `M66` | The other three scales in §4.2 |
| `OP-001` | Which contacts reach the rota at all |
| `OP-004` | The words issued at each severity |
| `OP-007`…`OP-012` | The procedures the on-call executes |
| `OP-009`, `OP-015` | The access that makes `RT-07` true |
| `OP-016` | Where every `Sev1`/`Sev2` ends |
| HR policy | Rota terms, allowance, time in lieu |

**Depended on by:** every `OP` runbook §6 · `NT-021` · `OP-002` · `OP-004` · `OP-005` · `OP-012` ·
`OP-016` · `SP-005` (once corrected) · `TS-018`.

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Quarterly for the rota and thresholds; annually for the severity scale |
| Trigger for out-of-cycle review | Any `Sev1` where severity, authority or handover was disputed · a rota breach · a missed page · `M66` go-live at W6 · a change to `NFR-007` or `NFR-045` |
| Owner | Platform Engineering |
| Distribution | The severity table (§4.1), the authority table (§4.8) and the handover format (§4.9) are **printed and physically held** at head office and in the on-call pack |
| Change route | [`CG-006`](../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md); severity-scale changes require CTO approval and propagate to `NT-021`, `OP-004` and every runbook §6 |

---

## Open Items

1. **OP-013-OI-01** — rota unstaffed; 24×7 cover unsupported.
2. **OP-013-OI-02** — three upstream files point elsewhere for severity ownership.
3. **OP-013-OI-03** — on-call terms unagreed with HR.
4. **OP-013-OI-04** — no emergency spend delegation.
5. **OP-013-OI-05** — no paging platform exists before `M66` at W6, while this file is required at W1.
6. **OP-013-OI-06** — branch participation in out-of-band channels unconfirmed.

---

## Definition of Done

Tick every box before setting `status: Approved`. Full checklist in [`CG-008`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md).

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — all six sections present; `Open Items` added, justified
- [x] Every factual, statutory, pricing or capability claim carries a source and a verification date
- [x] Terminology matches [`CG-004`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md)
- [x] All internal links resolve
- [ ] Accessibility standard [`CG-011`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) — n/a; engineering audience
- [x] Bengali counterpart — n/a; English-only by [`CG-010`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) §3.2
- [ ] Named approver recorded — CTO; HR Director co-approval required for §4.3 and §4.11
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] Decision(s) taken while authoring logged in `RF-006` — six open decisions pending

**Gates required (Class C):** G1 ●, G2 ●, G3 ●. G4 n/a.

---

*`OP-013` · 1000FiX ERP Programme · CONFIDENTIAL — Internal Use Only*
