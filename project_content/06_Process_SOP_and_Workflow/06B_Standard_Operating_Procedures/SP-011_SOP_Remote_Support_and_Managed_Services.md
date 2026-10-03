---
id: SP-011
title: SOP — Remote Support and Managed Services
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: MSP Operations
author: Business Process Lead with Managed Services
reviewers: [CTO, Operations Director, Legal Counsel, Data Protection Officer, Quality Manager, Account Management, Localisation Lead]
approver: Chief Technology Officer
content_class: C
purpose: >
  Remote access to a customer's estate has security, contractual and legal consequence. This SOP
  makes consent, session control, evidence and change approval mandatory rather than
  conventional, and defines when a remote session must stop and become an on-site visit. Without
  it, engineers hold privileged access to client environments under no defined standard, and the
  company cannot evidence what was done in someone else's network.
traces_to: [M05, M27, P03, P10, LG-016, LG-009, MD-028, SP-004, SP-005, SP-008, SP-031, BRU-RMS-08]
priority: P2
wave: W4
bilingual: yes
bn_counterpart: SP-011_SOP_Remote_Support_and_Managed_Services_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M05_Remote_Support_and_Managed_Services.md — including BRU-RMS-08, the engineer executing a change cannot be its sole approver
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §4 tiering and §8 external-party access rules EA-01…EA-07
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-070 MSP SLA attainment 98%, KPI-071 remote resolution rate 65%
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 8.5.1 controlled conditions, and clause 8.5.3 property belonging to external providers (including a customer's data and systems)
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Remote Support and Managed Services

| Item | Value |
|---|---|
| SOP ID | `SP-011` |
| Process owner | Chief Technology Officer; executed under MSP Operations |
| Roles performing | `R13` Remote Support Engineer · `R35` Contact Centre Supervisor · `R22` Account Manager · `R33` IT / System Administrator |
| Systems used | `P03` Managed Services console (`UI-035`) · `P10` · `M05` · `M27` |
| Frequency / volume | Continuous during contracted hours; 15–40 engineers; scales with the monitored-asset base (`KPI-069` target 5,000 assets) |
| ISO 9001 clause reference | 8.5.1 controlled conditions · **8.5.3** external provider property · 7.5 documented information · 8.5.5 post-delivery activities |

---

## 1. Purpose and Outcome

**Purpose.** To resolve a customer's issue remotely — or decide promptly that it cannot be — with
recorded consent, a controlled session, a full evidence trail, and change approval separated from
change execution.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| The customer consented to the session, to its scope, and to recording | Consent record bound to the session |
| Every action in the customer's environment is logged and attributable | Session log and recording |
| Any change was approved by someone other than the engineer who made it | `BRU-RMS-08`, `SOD-59` |
| The issue was resolved without a site visit, or escalated cleanly to one | `KPI-071` remote resolution rate |
| The contracted SLA was met | `KPI-070`, `MD-028` band |
| Access ended when the session ended | Session terminated; credentials not retained |

---

## 2. Scope

**Applies to:** remote diagnostic and support sessions on customer devices and estates; managed
monitoring and alert handling; scheduled patching and maintenance windows; and remote assistance
to a technician in the field.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Attendance at the customer's premises | `SP-008` |
| Internal 1000FiX IT support and change | `SP-031` |
| Data recovery from a customer's storage media | `SP-012` |
| Contract scoping, entitlement and renewal | `SP-015` |
| Contact-centre enquiry handling with no remote access | `SP-034` |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Session | A time-bounded, consented, logged remote connection to a customer system |
| Attended session | The customer is present and watching |
| Unattended session | Access to a monitored endpoint without a person present — permitted only where the contract grants it in writing |
| Maintenance window | A contractually agreed period in which changes may be applied |
| Change | Any action altering configuration, software state or data in the customer's environment |
| Break-glass | Emergency privileged access outside the normal path, time-boxed and reviewed |
| Alert | A monitoring event raised by `M05` against a managed asset |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Active contract with a remote-support entitlement | `M08` | Scope, hours and permitted access type are contractually defined (`BRU-CTR-02` — out-of-scope work is billed, never absorbed) |
| Customer's written consent framework | `LG-016` | Signed at contract, not improvised per session |
| Engineer authorised for that client | `05-04` T5 scoping, `M29` | Access limited to assigned clients (`EA-01`) |
| MFA and step-up authentication | `BRU-SEC-01`, `BRU-SEC-02` | Privileged remote action requires step-up |
| Session recording capability available | `M05` | An unrecorded privileged session is not permitted |
| SLA band identified | `MD-028` | The response clock is running from the contracted band |

---

## 5. Procedure

### 5.1 Reactive session — customer-raised issue

| Step | Who | Action | System / screen | Evidence produced | Time |
|---:|---|---|---|---|---|
| 1 | R13 | Acknowledge within the SLA response target; confirm the caller's identity against the authorised-contact list | `P03` · `P10` | Identity verified | 2 min |
| 2 | R13 | Confirm entitlement and scope. Out-of-scope work is quoted, not performed silently (`BRU-CTR-02`) | `P03` · `M08` | Scope confirmed | 2 min |
| 3 | R13 | **Obtain and record session consent**: purpose, systems in scope, the fact of recording, and the right to end the session at any time | `P03` consent panel | Consent record | 1 min |
| 4 | R13 | Start the recorded session. State your name and the ticket reference aloud at the start | `M05` | Session start, recording | 30 s |
| 5 | R13 | Diagnose using read-only actions first. **Do not change anything while still diagnosing** | Customer system | Diagnostic log | 10–30 min |
| 6 | R13 | Where a change is needed, raise it and obtain approval per §7 before applying it | `P03` change record | Approved change | 5 min |
| 7 | R13 | Apply the change. Record the exact commands or steps, the before state and the after state | `P03` | Change record with evidence | Varies |
| 8 | R13 | Test with the customer. Confirm the reported symptom is gone, not merely that the system responds | Customer system | Test result | 5 min |
| 9 | R13 | End the session explicitly. Confirm the connection is closed and no credential is retained | `M05` | Session ended | 1 min |
| 10 | R13 | Summarise to the customer: what was wrong, what changed, what to watch. Record the summary on the ticket | `P03` | Ticket summary | 3 min |
| 11 | R13 | Close or escalate per §6 | `P03` | Closure or escalation | 2 min |

### 5.2 Proactive alert handling

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 12 | `M05` | Alert raised against a monitored asset (`AUT-038`) | `NT-021` |
| 13 | R13 | Triage: correlate, confirm it is not a known false positive, classify severity | `MD-028` |
| 14 | R13 | Where the contract permits unattended remediation, apply the pre-approved runbook action only | Contract + `OP-*` runbook |
| 15 | R13 | Where it does not, contact the customer and follow §5.1 from step 3 | — |
| 16 | R13 | Record the alert, the action and the outcome — including where the action was "none, monitored" | `P03` |

### 5.3 Scheduled maintenance

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 17 | R13 | Confirm the maintenance window and the customer's notified acceptance | Contract |
| 18 | R13 | Pre-flight: backup or rollback point verified **before** any change | `SP-031` change discipline |
| 19 | R13 | Apply changes per the approved plan; record each | `SOD-59` |
| 20 | R13 | Post-check; confirm service restored; notify the customer with the outcome | `NT-*` |
| 21 | R13 | Where rollback was used, record it as a failed change, not as a completed one | `SP-031` |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 1 | Caller is not on the authorised-contact list | Do not proceed. Verify through the account contact | R22 Account Manager |
| 3 | Customer will not consent to recording | **Do not run a privileged session.** Offer a guided-instruction call instead, where the customer performs the actions | R13; R35 if disputed |
| 5 | Diagnosis requires access beyond the consented scope | Stop, seek fresh consent for the wider scope, record it | R13 |
| 5 | Personal data is visible that is not needed for the task | Do not view, copy or export it. Record that it was encountered (`EA-02`, `LG-009`) | R13; DPO if exposure occurred |
| 6 | Change is outside the maintenance window and is not urgent | Schedule it. Do not apply changes opportunistically because you are already connected | R22 + customer |
| 6 | Change is urgent and the approver is unavailable | Break-glass per §7, time-boxed, with retrospective approval within one business day | CTO |
| 8 | Issue is not resolvable remotely | Convert to an on-site visit (`SP-008`); do not keep trying past the point of value | R13 → R07 Dispatch Manager |
| 8 | Root cause is a defect in the customer's own environment outside contract scope | Report it, quote for remediation, do not fix it unpaid (`BRU-CTR-02`) | R22 |
| — | The engineer suspects malicious activity in the customer's environment | Stop changing anything. Preserve state. **Escalate immediately** — evidence is destroyed by remediation | CTO + Legal (`SP-005` TE-E9 pattern) |
| — | The customer asks the engineer to do something outside the agreement, on the call | Politely decline and route through the account manager. Verbal scope extension is not scope | R22 |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Change in a client environment | Any | **Not the executing engineer** (`BRU-RMS-08`, `SOD-59`) — a second engineer or R33 | CTO |
| Unattended access to a customer estate | Any | Contractually granted in writing; no operational override | R22 → CTO |
| Break-glass privileged access | Any | CTO or delegate, time-boxed, reviewed within 1 business day | CTO only |
| Out-of-scope work | ≤ BDT 10,000 | R22 Account Manager with customer agreement | R21 Sales Manager |
| Out-of-scope work | > BDT 10,000 | Quotation and approval per `SP-013` and `SP-004` | — |
| Extending a maintenance window | Any | Customer's authorised contact, recorded | R22 |
| Retaining a customer credential between sessions | **None — prohibited** | — | — |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Change causes an outage in the customer's environment | Roll back if a rollback point exists; if not, restore service by the fastest safe route. Tell the customer immediately | R22, CTO | Incident + change record; `SP-028` if a complaint follows |
| Session recording failed | End the session. Do not continue a privileged session unrecorded | R35, CTO | Session exception |
| Suspected personal-data exposure | **L4-direct: CTO + DPO + Legal** within the hour (`SP-005` TE-E9) | As stated | Breach register (`LG-009`) |
| Suspected compromise of the customer's environment | Preserve state; do not remediate before evidence is captured | CTO + Legal + R22 | Security incident |
| Engineer accesses a client they are not assigned to | Access blocked; treated as a control violation, not an error | CTO | `SP-006` exception report |
| Customer refuses to end a session that is out of scope | End it from the 1000FiX side and record why | R35 → R22 | Session record |
| Monitoring alert storm | Suppress with an expiry and an owner (`ES-09`); never indefinitely | CTO | Suppression register |
| Contracted SLA at risk | Escalate per `SP-005` CO-E2; service credit exposure to Finance | R22, R26 | SLA breach record |

---

## 9. Manual Fallback

Remote support depends on connectivity to the customer, which is frequently the thing that has
failed. Cross-reference `OP-014` and `IP-09`.

| Situation | Fallback |
|---|---|
| Remote tooling unavailable | **Guided-instruction call**: the customer performs the actions while the engineer instructs. Consent and evidence rules still apply; the engineer records the steps dictated |
| Customer's connectivity down | Telephone triage to determine whether it is a network fault or a system fault; dispatch an on-site visit (`SP-008`) rather than waiting |
| `P03` unavailable | Record the session on the **pre-numbered manual support log**: ticket reference, customer, consent obtained, actions, outcome, times. Back-enter within 24 hours |
| Monitoring platform down | Customers on 24×7 monitoring are informed that monitoring is degraded — **silence must not be read as health** | 
| Recording unavailable | No privileged session proceeds. This has no fallback by design |

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Session cannot start without a recorded consent | Preventive | Per session | Hard block |
| Privileged session requires step-up authentication | Preventive (`BRU-SEC-02`) | Per session | Auth log |
| Engineer access limited to assigned clients | Preventive (`EA-01`, T5) | Continuous | Record rules |
| Change execution and change approval separated | Preventive (`BRU-RMS-08`, `SOD-59`) | Per change | Hard block |
| All privileged sessions recorded | Preventive | Per session | Recording store |
| Credentials never retained between sessions | Preventive | Per session | Vault policy |
| Break-glass access time-boxed and reviewed | Detective | Per use, reviewed within 1 business day | Break-glass register |
| Session log sampled against the ticket record | Detective | Weekly, 5% | Quality review |
| Out-of-scope work performed without quotation | Detective | Monthly | Revenue leakage report |
| SLA attainment per contract | Detective | Monthly | `KPI-070` |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Execute a change in a client environment | Be its sole approver (`SOD-59`) | Hard block | Out of hours, break-glass with retrospective CTO approval within 1 business day |
| Administer users | Approve access requests for self (`SOD-09`) | Hard block | — |
| Grant an SoD exception | Be its beneficiary (`SOD-22`) | Hard block | — |
| Author a monitoring guard rail | Be sole approver of its removal (`SOD-36`) | Hard block | CTO countersign |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-070` | MSP SLA attainment | no baseline stated in `06-02` | 98% |
| `KPI-071` | Remote resolution rate — resolved with no site visit | no baseline stated in `06-02` | 65% |
| `KPI-069` | Monitored assets under management | no baseline stated in `06-02` | 5,000 |
| `KPI-072` | MSP gross margin | no baseline stated in `06-02` | 55% |
| Unrecorded privileged sessions | Sessions run without recording | untracked | **Zero** |
| Changes applied without separate approval | Violations of `SOD-59` | untracked | **Zero** |

> Four of these KPIs are listed in `06-02` with a target and a wave but **no baseline field at
> all** — the `SP-002` §1 finding E-04. Improvement here will be stated as an absolute, not as a
> delta, until a baseline is acquired.

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `LG-016` Remote Access and Managed Services Terms | The consent framework signed at contract |
| `LG-009` Data Protection and Privacy Policy | Personal-data handling during a session |
| `UI-035` Workspace — Managed Services Console Copy | The screens used |
| [`SP-008_SOP_On_Site_Field_Service_Visit.md`](SP-008_SOP_On_Site_Field_Service_Visit.md) | Escalation destination when remote fails |
| [`SP-015_SOP_Contract_and_AMC_Lifecycle.md`](SP-015_SOP_Contract_and_AMC_Lifecycle.md) | Scope and entitlement |
| [`SP-031_SOP_IT_Service_Desk_and_Change_Management.md`](SP-031_SOP_IT_Service_Desk_and_Change_Management.md) | Change discipline this SOP mirrors for customer estates |
| [`../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md`](../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md) | `SOD-59` |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md) | Response and resolution bands |
| `TR-002` Role-Based Curriculum Map | **No course pack exists for R13 Remote Support Engineer** — gap raised in `AUDIT-006` |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Chief Technology Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] Consent, recording and scope limits stated as preconditions, not conventions
- [x] Change execution separated from change approval, with a break-glass path
- [x] The "stop and preserve evidence" path for suspected compromise is present
- [x] §7 reconciles with `SP-004`
- [x] Manual fallback states where there is deliberately none
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] `LG-016` written and cross-checked against §7 — **outstanding; `LG` category not yet authored**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approver recorded — **pending CTO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
