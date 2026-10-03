---
id: SP-028
title: SOP — Complaint, Escalation and Compensation
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Customer Experience
author: Business Process Lead with Customer Experience and Quality
reviewers: [CCO, Operations Director, Quality Manager, Legal Counsel, Finance Manager, Contact Centre Supervisors, Localisation Lead]
approver: Chief Commercial Officer
content_class: C
purpose: >
  Complaint handling is the most reputationally sensitive process in the company and the one most
  often improvised. A complaint cannot be closed without confirming the outcome with the
  customer, and every non-conformance requires a root cause and a CAPA before closure. This SOP
  governs intake, classification, investigation, resolution authority, compensation limits,
  closure and the learning loop — with compensation approval separated from complaint ownership
  so that a complaint is never quietly bought closed.
traces_to: [M34, M23, M27, P10, P01, MD-026, MD-028, SP-004, SP-005, SP-006, SP-013, SP-029, SP-034, LG-021]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: SP-028_SOP_Complaint_Escalation_and_Compensation_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M34_Customer_Experience_Feedback_and_Complaints.md — SOD-21 score anomaly subject cannot investigate; SOD-22 compensation approval separated from complaint ownership above the branch threshold
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §10 BRU-QMS-02, BRU-QMS-04 — a complaint cannot be closed without confirming the outcome with the customer
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-020 CSAT 3.8/5 baseline, KPI-021 NPS, KPI-024 complaint resolution within SLA
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 9.1.2 customer satisfaction, clause 10.2 nonconformity and corrective action, and clause 8.7 control of nonconforming outputs
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Complaint, Escalation and Compensation

| Item | Value |
|---|---|
| SOP ID | `SP-028` |
| Process owner | Chief Commercial Officer; executed under Customer Experience with Quality (R32) |
| Roles performing | `R34` Contact Centre Agent · `R35` Contact Centre Supervisor · `R08` Service Centre Agent · `R06` Branch Manager · `R32` Quality Manager · `R05` Operations Director · `R22` Account Manager |
| Systems used | `P10` Contact Centre Console · `P03` · `P01` · `M34` · `M23` · `M27` |
| Frequency / volume | Continuous, across every channel, for 250,000+ customers a month |
| ISO 9001 clause reference | **9.1.2** customer satisfaction · **10.2** nonconformity and corrective action · 8.7 nonconforming outputs |

---

## 1. Purpose and Outcome

**Purpose.** To receive a complaint on any channel, understand it, put it right, tell the
customer what happened, and make sure the same thing does not happen to the next customer.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| The complaint was logged, not just handled in a conversation | Complaint record |
| It was classified consistently, so trends are visible | `MD-026` classification |
| A root cause was identified, not just a symptom fixed | Root cause record |
| A CAPA exists where the cause is systemic | `BRU-QMS-02`, `SP-029` |
| The outcome was confirmed **with the customer** before closure | `BRU-QMS-04` — hard block |
| Compensation was approved by someone other than the complaint owner above the threshold | `SOD-38`, `SP-004` A-67 |
| Resolution was inside the SLA | `KPI-024` |

---

## 2. Scope

**Applies to:** every expression of dissatisfaction from a customer, corporate client, brand
partner, marketplace buyer or member of the public, on any channel — call, email, portal, app,
social, in branch, or through a technician — including service failure, damage, delay, billing,
conduct and privacy complaints.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| A routine enquiry or status request | `SP-034` scripts; only becomes a complaint if dissatisfaction is expressed |
| Employee grievances | HR policy; `SP-005` PE-E9 |
| Internal quality nonconformity with no customer impact | `SP-029` |
| Warranty claim rejection by a brand | `SP-014` |
| Marketplace seller disputes about their own treatment | `SP-024` appeal path |
| Litigation, regulator contact or media enquiry | `SP-005` §4.8 L4-direct paths |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Complaint | Any expression of dissatisfaction requiring a response, whether or not redress is sought |
| Severity | The classification driving the response clock and the escalation level |
| Owner | The named person accountable for resolving this complaint |
| Root cause | The reason the failure occurred, distinct from the failure itself |
| Redress | Putting the customer back in the position they should have been in |
| Compensation | Anything given beyond redress — goodwill, credit, discount, gift |
| Closure | Confirmed with the customer (`BRU-QMS-04`), not merely marked resolved |
| Learning loop | The path from a closed complaint to a changed process |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Complaint intake channels configured | `M27` | Every channel routes into one record, not five queues |
| Classification taxonomy | `MD-026` | Categories that support trend analysis, not free text |
| Response and resolution targets | `MD-028` | The complaint SLA band |
| Compensation authority | `SP-004` A-64…A-67 | Limits set before the first complaint, not negotiated per case |
| Redress catalogue | CX with Finance | What redress is standard for which failure |
| Bilingual capability | `CG-010` | A complaint answered in the wrong language is a second complaint |
| Legal position on liability | `LG-021` | What may and may not be admitted |

---

## 5. Procedure

### 5.1 Intake and classification

| Step | Who | Action | System / screen | Evidence produced | Time |
|---:|---|---|---|---|---|
| 1 | R34 / R08 / any employee | Log the complaint the moment it is expressed. **Anyone can receive one; nobody may leave one unlogged** | `P10` / `P03` | Complaint record | 3 min |
| 2 | R34 | Acknowledge to the customer immediately, in their language, with a reference | `NT-*` | Acknowledgement |
| 3 | R34 | Capture what happened in the customer's words before classifying | `P10` | Narrative |
| 4 | R34 | Classify: category from `MD-026`, severity, affected order, channel | `P10` | Classification |
| 5 | System | Assign the SLA band and the named owner from the classification | `MD-028` | Owner assigned |
| 6 | R34 | Where the customer is at immediate risk — safety, data, financial loss in progress — escalate at once, do not queue | `SP-005` | Immediate escalation |

### 5.2 Investigation

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 7 | Owner | Gather the evidence: order history, condition reports, photographs, call recordings, GPS, POD, chat logs | `P03` | Evidence pack |
| 8 | Owner | Speak to the staff involved. **Fact-finding, not blame** — a culture where staff conceal errors produces unresolvable complaints | — | Statements |
| 9 | Owner | Contact the customer to fill gaps and to keep them informed. Silence is the most common escalation trigger | `NT-*` | Contact log |
| 10 | Owner | Establish what happened and **why** — the root cause, not the symptom | `P03` | Root cause |
| 11 | Owner | Where a person's own score or conduct is under investigation, **that person does not participate in it** (`SOD-37`) | `P03` | Investigation integrity |

### 5.3 Resolution

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 12 | Owner | Decide redress: repair, replace, refund, re-do, apologise, correct the record | `P03` | Redress decision |
| 13 | Owner | Where compensation beyond redress is warranted, seek approval per `SP-004` A-64…A-66. **Above the branch threshold, the approver may not be the complaint owner** (`SOD-38`) | `P03` | Compensation approval |
| 14 | Owner | Deliver the resolution; do not promise a date the operation cannot meet | `P03` | Resolution delivered |
| 15 | Owner | Explain to the customer plainly what went wrong, what has been done, and what will change | `NT-*` | Explanation |
| 16 | Owner | **Confirm the outcome with the customer** (`BRU-QMS-04`) | `P03` | Customer confirmation |
| 17 | Owner | Close only after confirmation. A complaint marked resolved without confirmation reopens as a worse complaint | `P03` | Closure |

### 5.4 Learning loop

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 18 | R32 | Raise a nonconformity where the cause is systemic (`BRU-QMS-02`) | `SP-029` |
| 19 | R32 | Assign a CAPA; **the person who performed the action may not verify its effectiveness** (`SOD-19`) | `SP-029` |
| 20 | R32 | Trend complaints by category, branch, technician, device and process monthly | `M34` |
| 21 | R32 | Repeated nonconformance in the same process triggers a mandatory management review item (`BRU-QMS-05`) | `M23` |
| 22 | CX | Feed themes into training (`TR-*`), scripts (`SP-034`), UI copy and process change | `SP-029` |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 1 | Staff member is unsure whether it is a complaint | **Log it.** Over-logging costs a record; under-logging costs the trend | Any employee |
| 4 | Complaint concerns safety, data protection, or alleged criminal conduct | Escalate immediately on the appropriate `SP-005` path; the ordinary ladder does not apply | Per `SP-005` §4.8 |
| 6 | Customer is at immediate risk | Act first; log fully afterwards | Any employee |
| 8 | A staff member admits an error | Record it factually. **Do not conflate the complaint resolution with a disciplinary process** — they follow different paths and different rights | Owner; HR separately |
| 10 | Root cause cannot be determined | Say so honestly to the customer, resolve on the balance of evidence, and record the uncertainty | Owner → R32 |
| 12 | The customer's expectation exceeds what is fair or contractual | Explain the position clearly and calmly, and offer what is fair. **Do not escalate a payment to end a conversation** | R06 → R05 |
| 13 | Compensation is requested by the owner for their own branch's failure | Above the branch threshold, approval leaves the branch (`SOD-38`) | R05 / CCO |
| 13 | Legal liability may be admitted by the wording of an apology | Take legal advice on wording. **An apology for the experience is not an admission; a statement of fault may be** | Legal Counsel (`LG-021`) |
| 16 | Customer does not respond to the confirmation attempt | Attempt on the configured schedule across channels; after the final attempt, close with the attempts recorded. **Do not close silently at the first non-answer** | Owner |
| 16 | Customer says they are not satisfied | The complaint is not resolved. Escalate a level | Per `SP-005` |
| 18 | The cause is a single human error with no systemic component | Record it as such; not every complaint needs a CAPA, and manufacturing one dilutes the ones that matter | R32 |
| 20 | One branch, technician or device dominates the trend | That is the finding. Address it as a process or competence matter, not as a run of unlucky customers | R32 → R05 |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Compensation to a complainant | ≤ BDT 5,000 | R06 Branch Manager (`SP-004` A-64) | R05 |
| Compensation to a complainant | ≤ BDT 25,000 | R05 Operations Director (`SP-004` A-65) | CCO |
| Compensation to a complainant | > BDT 25,000 | CCO + CFO (`SP-004` A-66) | CEO |
| Compensation above the branch threshold — owner excluded | Any | Approver ≠ complaint owner (`SOD-38`, `SP-004` A-67) | — |
| Refund | ≤ 10,000 / > 10,000 | R26 Finance Manager / CFO (`SP-004` A-27/A-28) | CEO |
| Credit note | ≤ 10,000 / > 10,000 | R27 / R26; creator excluded (`SOD-04`) | CFO |
| Free re-do of the service | Any | R06 within the rework path (`SP-013`) | R05 |
| Admit fault in writing | Any | Legal Counsel | CCO |
| Close a complaint without customer confirmation | **None — class H, no override** (`BRU-QMS-04`) | — | — |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Complaint involves personal injury | Safety and medical first (`SP-030`); then legal and insurance | HSE, R05, CEO, Legal | Safety incident + claim |
| Complaint involves data protection | **L4-direct: CTO + DPO + Legal** within the hour (`SP-005` TE-E9) | As stated | Breach register |
| Complaint alleges staff dishonesty or theft | **L4-direct: CFO + Internal Audit**, restricted. The local manager may be implicated | As stated | Restricted record |
| Complaint escalates to media or social virality | **L4-direct: CEO + CCO** (`SP-005` §4.8). No branch responds publicly | As stated | Comms record |
| Litigation threatened | Do not respond substantively; route to Legal unanswered | Legal Counsel | Restricted record |
| Regulator or consumer body contacts the company | Direct to CFO + Legal Counsel only | As stated | Restricted record |
| Complaint SLA breached | Escalate per `SP-005`; the customer is informed before they chase (`ES-07`) | Owner → R35 → R05 | SLA breach record |
| Repeat complaint from the same customer | Review the whole relationship, not the latest incident; assign a single owner | R22 / R35 | Relationship review |
| Complaint reopened after closure | Treat the closure as a failure of the confirmation step and review it | R32 | Reopening analysis |
| Complaint volume rises sharply in one area | Treat as an incident, not a queue problem | R05, R32 | Incident review |

---

## 9. Manual Fallback

| Step | Manual action |
|---|---|
| 1 | Complaints are logged on the **pre-numbered manual complaint form** at the point of receipt, with the reference given to the customer |
| 2 | The branch or contact centre maintains a running paper log so that nothing is lost during the outage |
| 3 | Acknowledgement is given verbally or in writing at the time, with the reference |
| 4 | Compensation approvals are recorded on the form with the approver's signature at the correct band — **the band does not relax during an outage** |
| 5 | Customer confirmation of the outcome is obtained and recorded on the form; `BRU-QMS-04` still applies |
| 6 | **Back-enter every complaint within 24 hours**, preserving receipt dates so that SLA measurement is honest |
| 7 | R32 reconciles the paper log against the system and signs |

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Complaint cannot be closed without customer confirmation | Preventive (`BRU-QMS-04`) | Per complaint | Hard block |
| Nonconformance requires root cause and CAPA before closure | Preventive (`BRU-QMS-02`) | Per nonconformity | Hard block |
| CAPA performer cannot verify effectiveness | Preventive (`SOD-19`) | Per CAPA | Hard block |
| Compensation approval separated from complaint ownership above the branch threshold | Preventive (`SOD-38`) | Per case | Hard block |
| Investigation subject cannot participate in it | Preventive (`SOD-37`) | Per investigation | Hard block |
| Supervisor cannot evaluate their own handled conversations | Preventive (`SOD-35`) | Per evaluation | Hard block |
| Every channel routes into one complaint record | Preventive | Continuous | Channel configuration |
| Complaint SLA monitoring | Detective | Daily | `KPI-024` |
| Trend analysis by category, site, technician, device | Detective | Monthly | `M34` reporting |
| Compensation spend by branch and by approver | Detective | Monthly | Finance report |
| Reopened complaints | Detective | Monthly | Closure quality |
| Complaint-to-CAPA conversion and CAPA effectiveness | Detective | Monthly | `SP-029` |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Own a complaint | Approve compensation on it above the branch threshold (`SOD-38`) | Threshold block | Approval leaves the branch to R05 or CCO |
| Be the subject of a score-anomaly investigation | Participate in that investigation (`SOD-37`) | Hard block | — |
| Handle a conversation | Perform its quality evaluation (`SOD-35`) | Hard block | Evaluation performed by another supervisor or by Quality |
| Perform a CAPA action | Verify its effectiveness (`SOD-19`) | Hard block | Verification by R32 or an independent auditor |
| Create a credit note arising from a complaint | Approve it (`SOD-04`) | Hard block | — |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-024` | Complaint resolution within SLA | unmeasured | 90%; stretch 95% |
| `KPI-020` | CSAT | 3.8/5 | 4.4/5; stretch 4.7/5 |
| `KPI-021` | NPS | unmeasured | 42; stretch 55 |
| `KPI-005` | Rework rate — a leading indicator of complaints | unmeasured | < 5%; stretch < 3% |
| Complaints closed with confirmed outcome | Confirmation completeness | untracked | 100% |
| Reopened complaints | Closure quality | untracked | Falling |
| Complaint-to-CAPA conversion | Systemic causes converted to corrective action | untracked | To be set |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `UI-020` `P10` Contact Centre Console UI Copy Pack · `UI-011` `P01` Customer Portal Copy Pack | The screens used |
| `NT-024` Survey, Feedback and NPS Invitation Library | Feedback capture that surfaces complaints |
| `LG-021` Customer Complaint and Redress Policy | The published policy and liability position |
| [`SP-034_Call_and_Conversation_Script_Library.md`](SP-034_Call_and_Conversation_Script_Library.md) | The complaint and escalation scripts |
| [`SP-029_SOP_Internal_Quality_Audit_and_CAPA.md`](SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) | The CAPA path |
| [`SP-013_SOP_Estimate_Approval_and_Rework_Control.md`](SP-013_SOP_Estimate_Approval_and_Rework_Control.md) | Rework classification, a frequent complaint cause |
| [`../06A_Process_Architecture/SP-005_Escalation_Matrix.md`](../06A_Process_Architecture/SP-005_Escalation_Matrix.md) | Escalation paths and L4-direct routes |
| [`../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md`](../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md) | `SOD-35`, `SOD-37`, `SOD-38` |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md) | Complaint classification |
| `TR-017` Course Pack — Contact Centre Agent · `TR-011` Course Pack — Branch Manager | Train this SOP |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Chief Commercial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] Customer confirmation stated as a hard block on closure, with no override
- [x] "Do not escalate a payment to end a conversation" stated at the decision point
- [x] Fact-finding separated from disciplinary process
- [x] Apology wording routed to Legal where fault may be admitted
- [x] §7 reconciles with `SP-004`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] `LG-021` redress policy written and reconciled with §7 — **outstanding; `LG` category not yet authored**
- [ ] Redress catalogue agreed with Finance — **outstanding**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approver recorded — **pending CCO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
