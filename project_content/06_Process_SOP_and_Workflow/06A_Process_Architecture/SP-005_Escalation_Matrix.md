---
id: SP-005
title: Escalation Matrix
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Service Operations
author: Business Process Lead with Service Operations
reviewers: [Operations Director, Contact Centre Supervisor, Quality Manager, HSE Lead, CTO, CFO, Legal Counsel, Account Management]
approver: Operations Director
content_class: C
purpose: >
  Names the destination, the timer, the acknowledgement requirement and the out-of-hours cover
  for every escalation path in the company — operational, commercial, technical, safety, legal
  and security. NT-020 sends the escalation and AUT-009 fires it at 50/75/90/100% of SLA; this
  file decides who receives it and what must happen next. Without it, escalation notifications
  have no destination and an escalated event simply becomes a louder unowned event.
traces_to: [M27, MD-028, NT-020, NT-021, NT-022, 05-05 AUT-009, SP-004, SP-030, OP-008, LG-009]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §12.1 AUT-009 — escalate to defined roles at 50/75/90/100% of SLA with acknowledgement tracking
    verified: 2026-08-15
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md §2 — escalation_at_pct, pause_conditions, clock_runs
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §7 — SoD exception authority CFO or CTO; privileged access CTO
    verified: 2026-08-15
    class: P1
  - source: Bangladesh Labour Act 2006, Chapter XII (Accidents) — statutory duty to notify prescribed authorities of a notifiable workplace accident; section references to be confirmed by Legal Counsel against the consolidated Act before approval
    verified: 2026-08-15
    class: P3
supersedes: none
review_due: 2027-02-15
---

# SP-005 — Escalation Matrix

> **An escalation with no named destination is a notification.** `AUT-009` will fire at 50%, 75%,
> 90% and 100% of every SLA regardless of whether anyone is configured to receive it. This file
> is what turns those four events into four accountable people.

---

## 1. Purpose

Escalation is the company's response to something not working. It fails in exactly four ways,
and this file is structured to prevent each of them:

| Failure | Prevention |
|---|---|
| **No destination** — the alert fires into a group mailbox nobody owns | §4.3–4.8 name a role, not a team, for every path |
| **No timer** — "escalate if it takes too long" | Every path carries an explicit trigger and interval |
| **No acknowledgement** — the alert is sent, so the sender considers it handled | `ES-04`: an escalation is open until acknowledged, and re-fires |
| **No out-of-hours cover** — the path exists only between 09:00 and 18:00 | §4.9 defines the on-call ladder and the 24×7 paths |

---

## 2. Scope

**In scope:** operational (SLA, job, dispatch, logistics), commercial (contract, claim, dispute,
credit), technical (integration, platform, data), people (safety, HR, conduct), security and
privacy, and quality escalation paths — with timers, destinations, acknowledgement rules and
out-of-hours cover.

**Out of scope**

| Not covered here | Owned by |
|---|---|
| Who may *approve* a decision | `SP-004` |
| The wording of the escalation message | `NT-020`, `NT-021`, `NT-022` |
| SLA durations and pause conditions | `MD-028` |
| System incident severity classification and technical response | `OP-008` incident runbook |
| Safety incident investigation procedure | `SP-030` |
| Complaint investigation and compensation procedure | `SP-028` |
| Statutory breach notification content and timing | `LG-009` data protection; Legal Counsel |

---

## 3. Audience

Every role that can receive an escalation, the configuration engineers building the alerting in
`M27`/`M28`, the contact centre and dispatch supervisors who operate the paths daily, the on-call
roster owner, and the authors of the 28 SOPs in `06B` — whose §8 exception table cites a path here.

---

## 4. Content

### 4.1 Principles

| # | Principle | Consequence |
|---|---|---|
| **ES-01** | **Escalate to a role, never to a person or a mailbox** | People leave; positions persist. Resolved through `MD-008` to the current holder |
| **ES-02** | **Every path has a terminal level** | There is always someone the escalation stops at. A path that loops is a path that is ignored |
| **ES-03** | **Escalation raises visibility; it does not transfer ownership** | The original owner keeps the work unless the path explicitly reassigns it. Otherwise escalation becomes a way to hand off a problem |
| **ES-04** | **An escalation is open until acknowledged** | Unacknowledged, it re-fires at the interval and then rises a level (`AUT-009` acknowledgement tracking) |
| **ES-05** | **Acknowledgement is not resolution** | Acknowledging starts a resolution clock; it does not stop the escalation clock |
| **ES-06** | **Safety escalates immediately and unconditionally** | No timer, no threshold, no approval. Act first, record within 24 hours (`SP-030`) |
| **ES-07** | **The customer is told before they ask** | Where an escalation affects a promise made to a customer, the customer notification (`NT-020`) fires with the internal one, not after it |
| **ES-08** | **Escalation volume is a metric** | A path firing constantly is a broken process, not a working control. Reviewed monthly (§4.11) |
| **ES-09** | **Suppression is possible only with an expiry** | An alert may be muted for a stated period with a reason and an owner; never indefinitely |
| **ES-10** | **Out-of-hours paths are tested** | An on-call ladder that has never been exercised does not exist. Quarterly test in §4.9 |

### 4.2 Levels

| Level | Who | Typical response window | Reached when |
|---|---|---|---|
| **L1** | The person doing the work | Immediate | The exception occurs |
| **L2** | Their supervisor — R06 Branch Manager, R09 Workshop Supervisor, R07 Dispatch Manager, R35 Contact Centre Supervisor | Within the working shift | L1 cannot resolve, or the first timer expires |
| **L3** | Functional management — R05 Operations Director, R17 Inventory Manager, R26 Finance Manager, R30 HR Manager, R32 Quality Manager, R24 Marketplace Operations | Same business day | L2 cannot resolve, or the second timer expires |
| **L4** | Executive — CEO, CFO, CTO, CCO | Same business day, or immediately for L4-direct paths | L3 cannot resolve, or the matter is L4-direct by classification |
| **L5** | External — Legal Counsel, regulator, brand partner, insurer, statutory authority | Per the statutory or contractual clock, which is not ours to set | Classification requires it (§4.8) |

**Rule ES-11.** Some paths are **L4-direct**: they skip L1–L3 entirely. They are listed in §4.8
and are the only permitted exceptions to the ladder.

### 4.3 Operational escalation — service and SLA

Driven by `AUT-009` against the `MD-028` band's `escalation_at_pct`. The clock is the band's
clock (`clock_runs`) and pauses only on an approved `pause_condition`.

| # | Trigger | To | Interval | Acknowledge within | Also notify |
|---|---|---|---|---|---|
| OP-E1 | SLA at **50%** consumed | Assigned technician (R10–R12) and R07 Dispatch Manager | Once | 30 min | — |
| OP-E2 | SLA at **75%** consumed | R07 Dispatch Manager + R06 Branch Manager | Once | 20 min | Account Manager if under contract |
| OP-E3 | SLA at **90%** consumed | R06 Branch Manager + R05 Operations Director | Every 15 min until acknowledged | 10 min | **Customer** (`NT-020`, `ES-07`) |
| OP-E4 | SLA **breached (100%)** | R05 Operations Director; **CCO if a service credit is triggered** | Every 30 min until owned | 10 min | Customer, Account Manager, Finance (credit liability) |
| OP-E5 | Job unassigned beyond the configured queue age | R07 Dispatch Manager | Every 15 min | 15 min | R06 at the second interval |
| OP-E6 | Technician has not started an assigned job 30 min past the window start | R07 Dispatch Manager | Once, then every 15 min | 10 min | Customer if the arrival window is at risk |
| OP-E7 | Failed visit recorded (`BRU-FSM-09`) | R07 Dispatch Manager | Immediate | 30 min | Customer, with a rebooking offer |
| OP-E8 | Device uncollected at 30 days (`BRU-SRM-16`) | R06 Branch Manager | Weekly thereafter | 2 business days | Legal Counsel at 60 days (abandonment) |
| OP-E9 | Job held on parts beyond the configured hold | R17 Inventory Manager + R06 Branch Manager | Daily | 4 business hours | Customer with a revised ETA (`AUT-007`) |
| OP-E10 | Rework flagged (`BRU-SRM-06`) | R32 Quality Manager + the original technician's manager | Immediate | 1 business day | — |
| OP-E11 | Custody exception — seal break, weight discrepancy (`BRU-LOG-04`) | R15 Logistics Coordinator + R06 Branch Manager | **Immediate, movement blocked** | 30 min | R05 Operations Director; Security if theft suspected |
| OP-E12 | Consignment above declared-value threshold missing a dual signature (`BRU-LOG-03`) | R15 Logistics Coordinator | Immediate, blocked | 30 min | CFO |

### 4.4 Commercial escalation

| # | Trigger | To | Interval | Acknowledge within |
|---|---|---|---|---|
| CO-E1 | Estimate unanswered at 24h and 48h, then expiry (`AUT-005`) | R08 Service Centre Agent, then R06 Branch Manager | Per `AUT-005` | 1 business day |
| CO-E2 | Contract SLA attainment falls below the contracted level in-period | R22 Account Manager + R05 Operations Director | On detection, then weekly | 1 business day |
| CO-E3 | Service credit becomes payable | R22 Account Manager + R26 Finance Manager + CCO | Immediate | 1 business day |
| CO-E4 | Warranty claim rejected by a brand | R28 Warranty Claims Officer, then R26 Finance Manager at second rejection | On each rejection | 2 business days |
| CO-E5 | Warranty claim approaching the brand's submission window (`BRU-WTY-08`) | R28 Warranty Claims Officer + R26 Finance Manager | At 75% of the window, then daily | 1 business day |
| CO-E6 | Marketplace dispute opened | R24 Marketplace Operations Officer | On open, then every 2 business days | 1 business day |
| CO-E7 | Seller performance below the visibility-reduction threshold (`BRU-ECM-04`) | R24 Marketplace Operations Officer | Automatic action + notice | 2 business days |
| CO-E8 | Invoice unpaid at 30 days (`AUT-023`) | R27 Finance Officer → collections queue; R26 at 60 days; CFO at 90 | Per the dunning series (`DT-018`) | 2 business days |
| CO-E9 | Corporate invoice disputed | R22 Account Manager + R26 Finance Manager | On raise, then every 3 business days | 1 business day |
| CO-E10 | Contract at renewal T−30 with no customer response (`AUT-015`) | R22 Account Manager → R21 Sales Manager at T−15 | Per the renewal cadence | 1 business day |

### 4.5 Supply chain and finance escalation

| # | Trigger | To | Interval | Acknowledge within |
|---|---|---|---|---|
| SC-E1 | Stockout blocking a job | R18 Branch Store Keeper → R17 Inventory Manager | Immediate, then every 4h | 2 business hours |
| SC-E2 | Van stock variance beyond tolerance at shift end (`AUT-035`) | R06 Branch Manager | Daily | 1 business day |
| SC-E3 | Three-way match exception outside tolerance | R27 Finance Officer → R26 Finance Manager at 3 business days | Daily | 2 business days |
| SC-E4 | Vendor delivery overdue against PO | R19 Procurement Officer | On the promised date, then every 2 days | 1 business day |
| SC-E5 | Goods failed inspection into quarantine (`BRU-INV-07`) | R32 Quality Manager + R19 Procurement Officer | Immediate | 1 business day |
| SC-E6 | Cash shift not closed (`BRU-FIN-10`) | **Next shift blocked**; R06 Branch Manager + R26 Finance Manager | Immediate | 1 business hour |
| SC-E7 | Unexplained cash variance at any value | R06 Branch Manager + R26 Finance Manager; CFO above the configured threshold | Immediate | 1 business hour |
| SC-E8 | Rider cash not reconciled at shift end (`BRU-LOG-06`) | R15 Logistics Coordinator + R26 Finance Manager | Immediate | 1 business hour |
| SC-E9 | Period close task overdue against the close calendar | R26 Finance Manager → CFO at 2 days | Daily | 1 business day |
| SC-E10 | VAT return preparation not complete at the statutory date − 3 days | R26 Finance Manager + CFO | Daily, then twice daily | 4 business hours |

### 4.6 People and safety escalation

| # | Trigger | To | Interval | Acknowledge within |
|---|---|---|---|---|
| PE-E1 | **Injury, fire, electrical incident, road traffic accident, or any immediate danger** | **L4-direct: HSE Lead + R05 Operations Director + CEO.** Emergency services first | **Immediate, no timer** (`ES-06`) | **Immediate** |
| PE-E2 | Near miss or hazard reported | HSE Lead + R06 Branch Manager | Within the shift | 1 business day |
| PE-E3 | Payroll input cut-off missed | R30 HR Manager → CFO | Immediate | 4 business hours |
| PE-E4 | Payroll variance beyond tolerance against the prior run | R30 HR Manager + CFO — **run held** | Immediate | 4 business hours |
| PE-E5 | Certification expiring at 30/15 days (`AUT-041`) | Technician, line manager, R32 Quality Manager | Per `AUT-041` | 3 business days |
| PE-E6 | Certification expired — technician removed from that brand's pool (`AUT-042`) | R32 Quality Manager + R07 Dispatch Manager | Immediate | 1 business day |
| PE-E7 | Mandatory training overdue (`BRU-LMS-01`) | Line manager → R30 HR Manager at 14 days | Weekly | 3 business days |
| PE-E8 | Leaver access not revoked within one hour (`BRU-SEC-06`) | **L4-direct: CTO + R30 HR Manager** | Immediate, every 30 min | 30 min |
| PE-E9 | Grievance, harassment or conduct allegation | **L4-direct: R30 HR Manager only**, restricted distribution | Immediate | 1 business day |
| PE-E10 | Geofence exception pattern for a technician (`BRU-FSM-06`) | R07 Dispatch Manager → R06 Branch Manager on repetition | Weekly review | 3 business days |

> **PE-E9 is deliberately restricted.** Conduct and grievance matters do not follow the ordinary
> ladder because the ordinary ladder may include the subject of the allegation. This is the same
> reasoning as `SOD-22` — the grantor may not be the beneficiary.

### 4.7 Technical, data and security escalation

Severity classification and the technical response live in `OP-008`; this file states the
destination and the timer.

| # | Trigger | To | Interval | Acknowledge within |
|---|---|---|---|---|
| TE-E1 | P1 platform incident — business stopped | **L4-direct: CTO + R05 Operations Director + CEO** | Every 30 min until restored | **15 min, 24×7** |
| TE-E2 | P2 incident — a portal or major function degraded | R33 IT Administrator → CTO at 1 hour | Hourly | 30 min |
| TE-E3 | Integration failure or error rate above threshold (`AUT-053`) | Integration owner (`NT-021`), then CTO at 1 hour | Per `AUT-053`; circuit breaker opens | 30 min |
| TE-E4 | Undetected integration failure exceeding 5 minutes (`KPI-088` target zero) | CTO | Immediate | 15 min |
| TE-E5 | Event in dead letter > 1 hour (`AUT-054`) | Integration owner | Hourly | 2 business hours |
| TE-E6 | Batch or reconciliation job failure | Job owner → R26 Finance Manager where financial | Per run schedule | 2 business hours |
| TE-E7 | Backup or restore test failure (`KPI-091` target 100%) | R33 IT Administrator + CTO | Immediate | 4 business hours |
| TE-E8 | Critical vulnerability open beyond 7 days (`KPI-089` target zero) | CTO | Weekly, then daily past 7 days | 1 business day |
| TE-E9 | **Suspected personal-data breach** | **L4-direct: CTO + Data Protection Officer + Legal Counsel** | Immediate, then hourly | **1 hour** — the statutory clock in `LG-009` starts at discovery, not at confirmation |
| TE-E10 | Bulk personal-data export attempted without approval (`BRU-SEC-05`) | CTO + Data Protection Officer | Immediate, blocked | 1 hour |
| TE-E11 | Data-recovery case accessed by a non-assigned user (`BRU-SEC-03`) | **L4-direct: CTO**; access already blocked | Immediate | 1 hour |
| TE-E12 | SoD violation detected at role assignment (`BRU-SEC-07`) | CFO or CTO (`SP-004` A-87) | Immediate, blocked | 1 business day |

### 4.8 L4-direct and L5 paths

These skip the ladder. The list is closed: **nothing else is L4-direct.**

| Path | Why it skips the ladder |
|---|---|
| PE-E1 Safety incident | Time to treatment. `ES-06` |
| PE-E8 Leaver access not revoked | A live credential for a former employee |
| PE-E9 Grievance or conduct | The ladder may contain the subject |
| TE-E1 P1 platform incident | Business stopped; every minute is measurable revenue |
| TE-E9 Suspected data breach | A statutory clock starts at discovery |
| TE-E11 Unauthorised data-case access | Contractual and criminal exposure |
| **Suspected fraud or theft, any value** | The ladder may contain the subject. Direct to CFO + Internal Audit, restricted |
| **Regulator, tax authority or law-enforcement contact** | Direct to CFO + Legal Counsel. **No one else responds to a regulator** |
| **Media or public-safety enquiry about an incident** | Direct to CEO + CCO. No branch responds to media |

**L5 external escalation** — only these, and only by the named role:

| Situation | Who may escalate externally | To |
|---|---|---|
| Statutory personal-data breach notification | Data Protection Officer with Legal Counsel | Per `LG-009` and the applicable instrument |
| Notifiable workplace accident | HSE Lead with Legal Counsel | The prescribed authority under the Bangladesh Labour Act 2006, Chapter XII — **section reference to be confirmed by Legal Counsel before this file is approved** |
| Brand partner claim dispute beyond the portal process | R28 Warranty Claims Officer with CCO | Brand escalation contact in `MD-017` |
| Insurance claim | CFO | Insurer |
| Litigation threat received | Anyone receiving it, immediately, unanswered | Legal Counsel |
| Environmental non-compliance in disposal | Sustainability lead with Legal Counsel | Department of Environment, per the disposal authorisation held |

### 4.9 Out-of-hours and on-call

| Item | Rule |
|---|---|
| 24×7 paths | PE-E1 safety · TE-E1 P1 incident · TE-E9 data breach · TE-E11 unauthorised data access · fraud · regulator contact · media |
| Everything else | Business hours per the branch calendar in `MD-041`, resuming at the next business-hour boundary |
| On-call roster | Published weekly in `M55`; one primary and one secondary per domain (operations, platform, finance, HSE) |
| Primary unreachable | Secondary at 15 minutes. Both unreachable at 30 minutes → the domain executive, unconditionally |
| Roster gaps | A published roster with an unfilled slot is escalated to the domain executive on publication, not at the incident |
| Public holidays and Eid | Reduced but never absent cover; the roster is published before the holiday period, not during it |
| **Quarterly test** | Each 24×7 path is exercised with a live unannounced test call. An untested path is presumed broken (`ES-10`) |
| Language | On-call communication is in the responder's working language; customer-facing escalation follows `CG-010` |

### 4.10 What the escalation must contain

Wording is `NT-020`/`NT-021`; the **content contract** is here, because a message missing any of
these wastes the recipient's first ten minutes.

| Field | Why |
|---|---|
| What has happened, in one sentence | The recipient may be asleep |
| The record identifier and a direct link | Never make the recipient search |
| Severity and which path fired | So they know the clock they are on |
| What has already been tried | Prevents repetition |
| What is being asked of them — decide, act, or be aware | The most commonly omitted field, and the reason escalations are ignored |
| The acknowledgement deadline | `ES-04` |
| Who else has been told | Prevents duplicated response |
| For a customer-affecting event: what the customer has been told, and when | `ES-07` |

### 4.11 Measuring the paths

| Metric | Target | Reviewed |
|---|---|---|
| Acknowledgement within the stated window | > 95% | Weekly, by path owner |
| Escalations reaching L4 | Falling quarter on quarter | Monthly, Operations Director |
| Paths that fired zero times in a quarter | Investigated — either the risk is absent or the trigger is misconfigured | Quarterly |
| Paths firing more than the configured noise threshold | Root-caused as a process defect, not tuned away (`ES-08`) | Monthly |
| Repeat escalations on the same record | Feeds `SP-029` CAPA | Monthly |
| Quarterly on-call test results | 100% pass | Quarterly, CTO and Operations Director |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md) | Supplies `escalation_at_pct`, the clock and the pause conditions |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md) | Business-hour boundaries and holiday cover |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-008_Organisation_Structure_and_Position_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-008_Organisation_Structure_and_Position_Master.md) | Resolves a role to its current holder (`ES-01`) |
| [`SP-004_Approval_Matrix_and_Delegation_of_Authority.md`](SP-004_Approval_Matrix_and_Delegation_of_Authority.md) | The absence ladder (DL-09) uses these timers |
| `05-05` §12 `AUT-009`, `AUT-053`, `AUT-054` | The automations that fire these paths |
| `NT-020`, `NT-021`, `NT-022` | Message content |
| `OP-008` | Technical severity classification |

| Depended on by |
|---|
| All 28 SOPs in `06B` §8 exception tables · `M27` alerting configuration · `SP-028` complaints · `SP-030` safety · `SP-031` IT service desk · `TS-006` escalation test scripts · `RP-006` operational exception reporting |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Quarterly, with the on-call test results |
| Trigger for out-of-cycle review | A path firing with no recipient; an organisational change; a new statutory notification duty; a P1 incident post-mortem; a new SLA band in `MD-028` |
| Owner | Service Operations |
| Change control | Adding, removing or re-timing a path requires Operations Director approval; L4-direct and L5 changes additionally require CFO and Legal Counsel. Logged in `RF-006` |
| Closed-list rule | §4.8 is a **closed list**. Adding an L4-direct path is an executive decision, not an author's |

**Open items**

| # | Item | Owner | Needed by |
|---|---|---|---|
| O-01 | Confirm the Bangladesh Labour Act 2006 accident-notification section reference and the prescribed authority. Cited here at source class **P3** (secondary) and **not yet verified against the consolidated Act** | Legal Counsel | Before `Approved` |
| O-02 | Confirm the statutory personal-data breach notification clock applicable to 1000FiX, and reconcile with `LG-009` | Data Protection Officer + Legal Counsel | Before W2 |
| O-03 | Populate the numeric thresholds marked "configured" (queue age, hold duration, cash variance, noise threshold) from `SP-002` baseline data | Service Operations | Before W1 build |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3)
- [x] Every path names a role destination, a trigger, an interval and an acknowledgement window
- [x] L4-direct list is closed and justified path by path
- [x] Out-of-hours cover and on-call ladder specified, with a test regime
- [x] Escalation message content contract stated
- [x] Measurement defined, including the "fired zero times" check
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] O-01 statutory accident-notification reference verified by Legal Counsel — **outstanding; blocks `Approved`**
- [ ] O-02 breach-notification clock confirmed — **outstanding**
- [ ] O-03 configured thresholds populated — **outstanding, depends on `SP-002`**
- [ ] Named approver recorded — **pending Operations Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
