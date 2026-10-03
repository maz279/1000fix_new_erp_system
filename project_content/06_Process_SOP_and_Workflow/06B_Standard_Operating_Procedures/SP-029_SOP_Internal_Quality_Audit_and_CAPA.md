---
id: SP-029
title: SOP — Internal Quality Audit and CAPA
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Quality
author: Business Process Lead with Quality Management
reviewers: [Quality Manager, Operations Director, CFO, CTO, Internal Audit, Legal Counsel, Localisation Lead]
approver: Quality Manager with Operations Director
content_class: C
purpose: >
  ISO 9001:2015 certification is the company's core differentiator and the surveillance auditor
  tests this process directly. Every non-conformance requires a root cause and a CAPA before it
  can be closed, a CAPA cannot be closed without effectiveness verification, and an auditor may
  not audit their own area. This SOP governs the audit programme, execution, finding
  classification, CAPA assignment, verification and closure, against a finding-to-CAPA cycle-time
  target under five days.
traces_to: [M23, M60, P11, DT-043, DT-008, SP-004, SP-005, SP-006, SP-010, SP-013, SP-028, SP-030, SP-031]
priority: P1
wave: W5
bilingual: yes
bn_counterpart: SP-029_SOP_Internal_Quality_Audit_and_CAPA_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M23_Quality_Management_System.md — SOD-07, SOD-19 CAPA performer cannot verify effectiveness, SOD-20 auditor cannot audit their own area
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §10 BRU-QMS-01…BRU-QMS-05; §12.4 AUT-049, AUT-050
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-066 CAPA closed on time, KPI-067 ISO major non-conformances zero, KPI-068 internal audit plan completion
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 9.2 internal audit, clause 9.3 management review, clause 10.2 nonconformity and corrective action, and clause 8.7 control of nonconforming outputs
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Internal Quality Audit and CAPA

| Item | Value |
|---|---|
| SOP ID | `SP-029` |
| Process owner | Quality Manager / ISO Coordinator (R32) |
| Roles performing | `R32` Quality Manager · trained internal auditors · field auditors on `P11` · process owners · `R05` Operations Director |
| Systems used | `P03` Quality console (`UI-031`) · `P11` Field Auditor Application · `M23` · `M60` |
| Frequency / volume | Rolling annual audit programme across processes, sites and shifts |
| ISO 9001 clause reference | **9.2** internal audit · **10.2** corrective action · 9.3 management review · 8.7 nonconforming outputs |

---

## 1. Purpose and Outcome

**Purpose.** To test whether the company actually does what its SOPs say, to record what it finds
without softening it, to fix the causes rather than the instances, and to prove the fix worked.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| The audit programme was completed as planned | `KPI-068` target 100% |
| Auditors were independent of the areas they audited | `SOD-20` |
| Findings are classified consistently across auditors | Classification calibration |
| Every nonconformity has a root cause and a CAPA before closure | `BRU-QMS-02` |
| No CAPA closed without effectiveness verification | `BRU-QMS-03`, `SOD-19` |
| Finding-to-CAPA cycle time under five days | Cycle-time report |
| Zero major non-conformances at surveillance audit | `KPI-067` |

---

## 2. Scope

**Applies to:** the internal audit programme across all processes, branches, workshops,
warehouses and functions; nonconformities from any source — audit, complaint, rework, failed QC,
incident, or external audit; corrective and preventive action; effectiveness verification; and
management review input.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Financial internal audit and control testing | `M60`; this SOP shares the CAPA mechanism |
| The per-job quality checklist at release | `SP-010` §5.3, `DT-008` |
| Safety incident investigation | `SP-030`; its corrective actions enter this CAPA process |
| IT change and problem management | `SP-031`; its problem records may raise a CAPA |
| Complaint handling itself | `SP-028`; its systemic causes enter here |
| External certification audit | Managed by R32; this SOP produces the evidence it inspects |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Audit programme | The planned schedule of audits by process, site and period |
| Finding | An observed fact recorded during an audit |
| Nonconformity | A finding where a requirement is not met |
| Major NC | A systemic failure, an absent process, or a nonconformity with significant consequence |
| Minor NC | An isolated lapse against a defined requirement |
| Observation | A finding that is not a nonconformity but could become one |
| Root cause | The reason the nonconformity occurred, established by analysis rather than assumption |
| CAPA | Corrective action addressing the cause; preventive action addressing a risk not yet realised |
| Effectiveness verification | Evidence, after a defined interval, that the action worked |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Approved annual audit programme | R32 | Risk-based, covering every process at least annually |
| Trained, independent auditors | `M22` | Competence recorded; independence checked against `SOD-20` |
| Current SOPs to audit against | `06B` | You cannot audit against an unwritten standard |
| Audit checklists per process | `SP-032`, `M23` | Derived from the SOP's §10 controls |
| Finding classification criteria | This SOP §5.2 | Applied consistently, calibrated between auditors |
| Nonconformity sources connected | `M23` | Complaints, rework, failed QC and incidents raise nonconformities automatically (`AUT-049`) |
| Management review schedule | `M23` | The forum where repeated nonconformance lands (`BRU-QMS-05`) |

---

## 5. Procedure

### 5.1 Programme and preparation

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 1 | R32 | Build the annual programme, risk-weighted: high-risk and poorly performing processes and sites audited more often | `M23` | Audit programme |
| 2 | R32 | Assign auditors. **An auditor may not audit their own area or their own prior work** (`SOD-20`) | `M23` | Independence check |
| 3 | Auditor | Prepare: read the SOP, the prior findings, the KPI trend and the open CAPAs for that area | `P03` | Preparation record |
| 4 | R32 | Notify the area, except where an unannounced audit is the point — cash, stock and safety audits are more valuable unannounced | `NT-*` | Notification or unannounced flag |

### 5.2 Execution

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 5 | Auditor | Open with the area's manager: scope, method, duration, and that findings are about the process | — | Opening record |
| 6 | Auditor | **Audit against the SOP, sampling real records and observing real work** — not by interviewing about intentions | `P11` / `P03` | Evidence sampled |
| 7 | Auditor | Record each finding with objective evidence: the record examined, what was observed, which requirement was not met | `P11` | Findings |
| 8 | Auditor | Classify: major NC, minor NC, observation, or conformity with a good practice worth sharing | `P11` | Classification |
| 9 | Auditor | Close out with the manager: state the findings, hear the response, record disagreements without resolving them by seniority | — | Closing record |
| 10 | Auditor | Issue the report within the configured period. A report issued weeks later audits a situation that has moved | `DT-043` | Audit report |

### 5.3 Nonconformity and root cause

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 11 | System | Raise a nonconformity from any source — audit, complaint, rework, failed QC, incident (`AUT-049`) | `M23` | NCR (`DT-043`) |
| 12 | R32 | Route to the process owner, not to the individual who made the error | `M23` | Assignment |
| 13 | Process owner | Contain first: stop the immediate harm, quarantine affected output, protect the customer | `P03` | Containment |
| 14 | Process owner | Establish the root cause by analysis. **"Human error" is not a root cause** — ask why the process allowed it | `P03` | Root cause analysis |
| 15 | Process owner | Assess extent: has this happened elsewhere, to other customers, in other periods? | `P03` | Extent assessment |

### 5.4 CAPA

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 16 | Process owner | Define the corrective action addressing the **cause**, with an owner and a date | `M23` | CAPA record |
| 17 | Process owner | Where the same cause could produce failures elsewhere, define preventive action too | `M23` | Preventive action |
| 18 | R32 | Approve the CAPA as capable of addressing the cause. A CAPA of "retrain the staff member" for a systemic cause is rejected | `M23` | CAPA approval |
| 19 | CAPA owner | Implement; update the SOP, the checklist, the configuration or the training as required | `06B`, `TR-*` | Implementation evidence |
| 20 | System | At the CAPA due date plus the verification interval, prompt effectiveness verification (`AUT-050`) | `M23` | Verification task |
| 21 | **Verifier — not the person who performed the action** | Verify effectiveness with evidence, not with an assurance (`BRU-QMS-03`, `SOD-19`) | `M23` | Verification record |
| 22 | R32 | Close only on verified effectiveness. Where it did not work, reopen and re-analyse — the root cause was wrong | `M23` | Closure or reopening |

### 5.5 Reporting and review

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 23 | R32 | Report programme completion, findings by classification, CAPA ageing and cycle time monthly | `KPI-066`, `KPI-068` |
| 24 | R32 | Repeated nonconformance in the same process **triggers a mandatory management review item** (`BRU-QMS-05`) | `M23` |
| 25 | Management | Review at the planned interval: audit results, customer feedback, process performance, CAPA status, resource needs | ISO 9.3 |
| 26 | R32 | Feed the certification body's surveillance audit with the complete, unedited record | ISO 9.2 |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 2 | The only competent auditor for an area works in it | Use an auditor from another region, or an external auditor. **`SOD-20` has no compensating control** — an auditor auditing themselves produces no assurance | R32 |
| 4 | The audit concerns cash, stock or safety | Consider unannounced. An announced cash audit measures preparation | R32 |
| 6 | The area produces records specially for the audit | Note it. Audit the live process, not the display | Auditor |
| 7 | A finding is disputed by the area manager | Record both the finding and the response. **Seniority does not resolve evidence** | R32 |
| 8 | A finding might be a major NC | Classify on the criteria, not on the discomfort it will cause. Under-classification is the most common way an internal audit function becomes decorative | R32 |
| 9 | The auditor finds a safety risk | Stop the activity and escalate immediately (`SP-030`). Do not wait for the report | Auditor → HSE |
| 9 | The auditor finds suspected fraud | Do not investigate further. **L4-direct: CFO + Internal Audit**, restricted | Auditor → CFO |
| 14 | The proposed root cause is "human error" or "staff did not follow the process" | Rejected. Ask why the process permitted it, why it was not noticed, and why it was easier to do the wrong thing | R32 |
| 15 | The extent assessment shows other customers affected | Customer notification and redress follow (`SP-028`), before the CAPA is complete | R05, CCO |
| 18 | The CAPA is retraining alone for a systemic cause | Rejected. Retraining is a valid action only where competence was genuinely the cause | R32 |
| 21 | The verifier is the person who performed the action | **Blocked** (`SOD-19`) | — |
| 22 | Verification shows the action did not work | Reopen. The root cause analysis was wrong; do not close with a second action untested | R32 |
| 24 | The same nonconformance recurs a third time | Management review item, with a named executive owner, not another CAPA | R32 → R05 |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Approve the annual audit programme | Any | R32 with R05 Operations Director | CEO |
| Classify a finding as major | Any | R32 | — |
| Approve a CAPA | Any | R32 (`SP-004` A-68) | R05 |
| Verify CAPA effectiveness | Any | A person other than the one who performed the action (`SOD-19`) | R32 |
| Close a CAPA without verified effectiveness | **None — class H, no override** (`BRU-QMS-03`) | — | — |
| Close a nonconformity without a root cause | **None — class H, no override** (`BRU-QMS-02`) | — | — |
| Extend a CAPA due date | Once, with a recorded reason | R32 | R05 |
| Waive an audit in the programme | Any | R32 with R05, recorded; the audit is rescheduled, never deleted | CEO |
| Appoint an external auditor for an area | Any | R32 with CFO | CEO |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Safety risk found during an audit | Stop the activity; escalate immediately (`SP-005` PE-E1/PE-E2) | HSE, area manager, R05 | Safety incident |
| Suspected fraud found during an audit | Stop; preserve; **L4-direct: CFO + Internal Audit**, restricted | As stated | Restricted record |
| Area refuses access or records | Escalate to R05; refusal is itself a finding | R32 → R05 | Audit finding |
| Audit programme falling behind | Escalate; `KPI-068` targets 100% completion | R32 → R05 | Programme tracker |
| CAPA overdue | Escalate to the process owner's manager, then to R05 | R32 | CAPA ageing report |
| CAPA closed without verification | Control failure; reopen and investigate how it was possible | R32, CTO | Nonconformity on the QMS itself |
| Findings softened between draft and issued report | Serious integrity issue; the draft and issued versions are both retained | R32 → R05, Internal Audit | Restricted record |
| Major NC at surveillance audit | Immediate containment, root cause and CAPA on the certification body's timetable, which is shorter than ours | R32, R05, CEO | Certification record |
| Repeated nonconformance in one process | Management review item (`BRU-QMS-05`) | R32 → Management | Review record |
| `P11` unavailable during a field audit | Fallback in §9 | R32, R33 | Paper audit sheets |

---

## 9. Manual Fallback

| Step | Manual action |
|---|---|
| 1 | Audits are conducted on **pre-numbered paper audit checklists** derived from the SOP §10 control tables |
| 2 | Findings are recorded with the record reference, the observation and the requirement not met — the same content, on paper |
| 3 | Photographs are taken on an auditor-issued camera and referenced against the finding number |
| 4 | The closing meeting is minuted and signed by the auditor and the area manager |
| 5 | Nonconformities are raised on the **manual NCR form** (`DT-043`), with root cause and CAPA recorded by the process owner |
| 6 | **Back-enter every finding, NCR and CAPA within 48 hours**, preserving the audit and finding dates so cycle time is measured honestly |
| 7 | R32 reconciles the paper record against the system and signs |

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Auditor independence enforced | Preventive (`SOD-20`) | Per assignment | Independence check |
| Nonconformity requires root cause and CAPA before closure | Preventive (`BRU-QMS-02`) | Per NC | Hard block |
| CAPA requires effectiveness verification before closure | Preventive (`BRU-QMS-03`) | Per CAPA | Hard block |
| CAPA performer cannot verify effectiveness | Preventive (`SOD-19`) | Per verification | Hard block |
| Quality checklist cannot be completed with unanswered mandatory items | Preventive (`BRU-QMS-01`) | Per checklist | Hard block |
| Complaint cannot close without customer confirmation | Preventive (`BRU-QMS-04`) | Per complaint | Hard block |
| Repeated nonconformance triggers management review | Preventive (`BRU-QMS-05`) | Continuous | Review agenda |
| Nonconformities raised automatically from quality events | Detective → preventive (`AUT-049`) | Continuous | NC register |
| Audit programme completion | Detective | Monthly | `KPI-068` |
| CAPA ageing and cycle time | Detective | Weekly | `KPI-066` |
| Finding classification calibration between auditors | Detective | Quarterly | Calibration record |
| Draft-versus-issued report comparison | Detective | Sampled | Integrity check |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Audit an area | Be responsible for that area or its prior work (`SOD-20`) | Hard block at assignment | Cross-regional or external auditor. **No weaker alternative exists** |
| Perform a CAPA action | Verify its effectiveness (`SOD-19`) | Hard block | Verification by R32 or an independent auditor |
| Perform a repair | Record its independent QC (`SOD-07`) | Threshold block | Remote photographic review (`SP-010`) |
| Own a control | Record its test conclusion (`SOD-21`) | Hard block | Testing performed by `M60` GRC, independent of the control owner |
| Be the subject of an investigation | Participate in it (`SOD-37`) | Hard block | — |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-066` | CAPA closed on time | unmeasured | 90%; stretch 95% |
| `KPI-067` | ISO major non-conformances | unknown | **Zero** |
| `KPI-068` | Internal audit plan completion | manual | 100% |
| `KPI-005` | Rework rate — the largest single quality signal | unmeasured | < 5%; stretch < 3% |
| `KPI-007` | QC first-pass rate | unmeasured | 92%; stretch 95% |
| Finding-to-CAPA cycle time | Days from finding to approved CAPA | untracked | **< 5 days** |
| CAPA reopened after verification | Root cause accuracy | untracked | Falling |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-043` NCR, CAPA and Internal Audit Report Forms | The forms this SOP operates |
| `DT-008` Quality Checklist Record | The per-job gate audited here |
| `UI-031` Workspace — Quality Console Copy · `UI-021` `P11` Field Auditor App Copy Pack | The screens used |
| [`SP-032_Operational_Checklist_Library.md`](SP-032_Operational_Checklist_Library.md) | The checklists audits sample against |
| [`SP-028_SOP_Complaint_Escalation_and_Compensation.md`](SP-028_SOP_Complaint_Escalation_and_Compensation.md) | Feeds systemic causes into this process |
| [`SP-010_SOP_Workshop_and_Depot_Repair.md`](SP-010_SOP_Workshop_and_Depot_Repair.md) | Failed QC and rework as nonconformity sources |
| [`SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](SP-030_SOP_Health_Safety_and_Incident_Reporting.md) | Safety corrective actions enter this CAPA process |
| [`SP-031_SOP_IT_Service_Desk_and_Change_Management.md`](SP-031_SOP_IT_Service_Desk_and_Change_Management.md) | Problem records may raise a CAPA |
| [`../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md`](../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md) | `SOD-19`, `SOD-20`, `SOD-21` — and §4.8, which records that `M60` AC-07 tests only twelve of sixty controls |
| `TR-016` Course Pack — Quality and Field Auditor | Trains auditors for this SOP |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Quality Manager with Operations Director (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] Auditor independence stated as having no compensating control
- [x] "Human error is not a root cause" stated at the decision point
- [x] Retraining-alone CAPAs rejected for systemic causes
- [x] Draft-versus-issued report comparison included as an integrity control
- [x] §7 reconciles with `SP-004`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Audit checklists derived from every `06B` SOP §10 — **outstanding; depends on `SP-032`**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approvers recorded — **pending Quality Manager and Operations Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
