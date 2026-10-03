---
id: DT-043
title: NCR, CAPA and Internal Audit Report Forms
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Quality
author: Quality with Internal Audit and Content Design
reviewers: [Internal Audit, Operations, ISO certification consultant, Legal & Compliance]
approver: Quality Manager with Chief Operating Officer
content_class: C
purpose: >
  The non-conformance report, the corrective and preventive action record, the internal audit
  report and the finding classification. ISO 9001:2015 certification is the company's core
  differentiator, and these are the forms the certification body inspects — an audit trail that
  cannot show cause, action and effectiveness is an audit trail that fails surveillance.
traces_to: [M23, M60, P11, DT-001, DT-008, DT-036, MD-026, MD-040, BRU-QMS-01, BRU-QMS-02, BRU-QMS-03, BRU-QMS-04, BRU-QMS-05, BRU-INV-07]
priority: P1
wave: W5
bilingual: yes
bn_counterpart: DT-043_NCR_CAPA_and_Internal_Audit_Report_Forms_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-QMS-02 — every non-conformance requires a root cause and a CAPA before it can be closed
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-QMS-03 — a CAPA cannot be closed without effectiveness verification after the defined interval
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-QMS-05 — repeated non-conformance in the same process triggers a mandatory management review item
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clauses 8.7 control of nonconforming outputs, 10.2 nonconformity and corrective action, 9.2 internal audit, 9.3 management review. **Clause references to be confirmed by the certification consultant**
    verified: 2026-08-15
    class: P2
supersedes: none
review_due: 2027-02-15
---

# DT-043 — NCR, CAPA and Internal Audit Report Forms

> **Three forms, one chain.** A non-conformance is raised (**NCR**), its cause is found and action
> taken (**CAPA**), and the whole system is periodically examined (**internal audit**) — which
> raises more NCRs. The chain is what a certification body follows, and it breaks at the same
> two places every time: **root cause that is not a cause**, and **effectiveness that was never
> verified**.
>
> **`BRU-QMS-02`: no closure without a root cause and a CAPA.**
> **`BRU-QMS-03`: no CAPA closure without effectiveness verification after the defined interval.**

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Quality management forms — NCR, CAPA, internal audit report |
| Owning module | `M23` Quality Management System, surfaced in `P11` |
| Statutory | No — **ISO 9001:2015 certification evidence** |
| Recipient(s) | Process owner, Quality, internal audit, management review, certification body |
| Languages | **Bilingual — stacked labels.** Process owners in branches and workshops read Bengali |
| Output formats | A4 portrait · PDF · `P11` portal (primary working surface) |
| Numbering mask | `MD-040` — `NCR-{entity}-{yy}-{seq:06d}`, `CPA-{entity}-{yy}-{seq:06d}`, `IAR-{entity}-{yy}-{seq:06d}` |
| Retention period | `LG-009`; **not less than one full certification cycle plus one** |

### 1.1 The chain

```
Source of a non-conformance
  ├── Internal audit finding (IAR)
  ├── Failed quality checklist (DT-008)
  ├── Customer complaint (M34)
  ├── Rework (BRU-SRM-06)
  ├── Supplier defect (DT-024)
  └── Process monitoring exception
                ↓
            NCR raised  →  Containment (immediate)
                ↓
            Root cause analysis
                ↓
            CAPA — corrective (this cause) + preventive (this class of cause)
                ↓
            Implementation
                ↓
            Effectiveness verification after the defined interval  (BRU-QMS-03)
                ↓
            Closure       →  Repeat in the same process?  →  Management review (BRU-QMS-05)
```

---

## 2. Statutory Requirements

Not statutory. ISO 9001:2015 certification requirements — **clause references to be confirmed by
the certification consultant**:

| Requirement | Clause (indicative) | Effect |
|---|---|---|
| Control of nonconforming outputs | 8.7 | The NCR records what was found, contained and dispositioned |
| Nonconformity and corrective action | 10.2 | Cause, action, effectiveness and any need to update risks |
| Internal audit | 9.2 | Planned programme, criteria, scope, objectivity, reporting |
| Management review | 9.3 | Inputs include audit results, nonconformities and corrective actions |
| Documented information | 7.5 | These forms are the retained evidence |

---

## 3. Layout

Three forms sharing a common header and identity block so they read as one system.

### 3.1 NCR

| Zone | Content | Bilingual |
|---|---|---|
| Header | NCR number, date raised, source, **classification** | Title stacked |
| Party block | Process and process owner left; raiser and Quality contact right | Labels stacked |
| Body | Description of the non-conformance → requirement not met → **immediate containment** → disposition | Labels stacked |
| Statutory block | Not used. The **containment and disposition record** occupies this zone | Parallel columns |
| Signature | Raiser, process owner acknowledgement, Quality | Labels stacked |

### 3.2 CAPA

| Zone | Content |
|---|---|
| Header | CAPA number, linked NCR(s), date, owner, due dates |
| Body | Root cause analysis and method → corrective action → **preventive action** → implementation record → **effectiveness verification** |
| Signature | CAPA owner, Quality verification, closure approval |

### 3.3 Internal audit report

| Zone | Content |
|---|---|
| Header | IAR number, audit scope, criteria, dates, auditor and auditee |
| Body | Scope and criteria → sample examined → findings by classification → positive observations → conclusion |
| Signature | Lead auditor, auditee acknowledgement, Quality Manager |

| # | Rule |
|---|---|
| **L-43-a** | **Every NCR states the requirement not met** — the clause, procedure, SOP or specification. A non-conformance without a requirement is an opinion |
| **L-43-b** | **Containment and correction are recorded separately from corrective action.** Fixing the affected product is containment; stopping recurrence is corrective action. Conflating them is the most common ISO finding |
| **L-43-c** | The CAPA form has **two distinct blocks — corrective and preventive**. A CAPA with an empty preventive block is a CAPA that will produce a repeat |
| **L-43-d** | The effectiveness verification block carries its own due date, set when the CAPA is raised (`BRU-QMS-03`) |
| **L-43-e** | Audit findings print with their classification and the evidence sampled |
| **L-43-f** | Positive observations are recorded in audit reports. An audit that only ever finds fault is an audit people learn to avoid |

---

## 4. Field Mapping

### 4.1 NCR

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| NCR no. | এনসিআর নং | `MD-040` sequence | Monospace | ✔ |
| Date raised | উত্থাপনের তারিখ | `ncr.raised_at` | `DD/MM/YYYY` | ✔ |
| Raised by | উত্থাপনকারী | `employee.display_name` + ID | Text | ✔ |
| **Source** | উৎস | `ncr.source` | Enum per §1.1 | ✔ |
| Source reference | উৎস সূত্র | `DT-008` / `M34` / `DT-024` ref | Monospace | ✔ where applicable |
| Process affected | প্রভাবিত প্রক্রিয়া | `M23.process_code` | Code + name | ✔ |
| Process owner | প্রক্রিয়ার মালিক | `employee.display_name` + ID | Text | ✔ |
| Location | স্থান | `MD-003` / `MD-004` | Text | ✔ |
| **Classification** | শ্রেণিবিন্যাস | `ncr.classification` | Enum: critical / major / minor / observation | ✔ |
| **Requirement not met** | লঙ্ঘিত শর্ত | Clause, SOP or spec reference | Text + reference | ✔ **`L-43-a`** |
| Description | বিবরণ | `ncr.description` | Free text, factual | ✔ |
| Evidence | প্রমাণ | `M24` references | Count + reference | ✔ |
| Extent | ব্যাপ্তি | `ncr.extent` | Text: units, period, sites affected | ✔ |
| **Immediate containment** | তাৎক্ষণিক নিয়ন্ত্রণ | `ncr.containment` | Text + timestamp | ✔ |
| Disposition of affected output | প্রভাবিত পণ্যের গতি | Enum: rework / regrade / scrap / concession / return | ✔ **(`BRU-INV-07`)** |
| Concession approved by | ছাড় অনুমোদনকারী | `employee` + role | Text | ✔ where concession |
| Customer notified | গ্রাহক অবহিত | Bool + reference | Bool | ✔ where the customer is affected |
| CAPA required | সিএপিএ প্রয়োজন | Computed | Bool — **always TRUE for critical and major** | ✔ |
| Linked CAPA | সংযুক্ত সিএপিএ | `CPA-…` | Monospace | ✔ where raised |

### 4.2 CAPA

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| CAPA no. | সিএপিএ নং | `MD-040` sequence | Monospace | ✔ |
| Linked NCR(s) | সংযুক্ত এনসিআর | `NCR-…` | Monospace list | ✔ |
| CAPA owner | মালিক | `employee.display_name` + ID | Text | ✔ |
| Date raised / due | তারিখ / নির্ধারিত | Dates | `DD/MM/YYYY` | ✔ |
| **Root cause method** | মূল কারণ পদ্ধতি | Enum: 5-why / fishbone / fault tree / other | ✔ |
| **Root cause** | মূল কারণ | `capa.root_cause` | Text | ✔ |
| Contributing factors | অবদানকারী কারণ | `capa.contributing[]` | Text | Where identified |
| **Corrective action** | সংশোধনমূলক পদক্ষেপ | `capa.corrective[]` | Action, owner, due date | ✔ |
| **Preventive action** | প্রতিরোধমূলক পদক্ষেপ | `capa.preventive[]` | Action, owner, due date | ✔ **`L-43-c`** |
| Systemic scope | ব্যবস্থাগত পরিধি | `capa.scope` | Text: other sites, processes, products checked | ✔ |
| Documents updated | হালনাগাদকৃত নথি | SOP, checklist, training references | List | ✔ where applicable |
| Training delivered | প্রদত্ত প্রশিক্ষণ | `M22` reference | Reference | ✔ where applicable |
| Implementation date | বাস্তবায়নের তারিখ | `capa.implemented_at` | `DD/MM/YYYY` | ✔ |
| **Effectiveness check due** | কার্যকারিতা যাচাইয়ের তারিখ | `capa.effectiveness_due` | `DD/MM/YYYY` | ✔ **`BRU-QMS-03`** |
| **Effectiveness method** | যাচাইয়ের পদ্ধতি | `capa.effectiveness_method` | Text: what will be measured | ✔ |
| **Effectiveness result** | ফলাফল | `capa.effectiveness_result` | Enum: effective / not effective / inconclusive | ✔ |
| Verified by | যাচাইকারী | `employee` — **not the CAPA owner** | Text | ✔ |
| Closure approved by | সমাপ্তি অনুমোদন | Quality Manager | Text + date | ✔ |
| Re-raised as | পুনরায় উত্থাপিত | New `CPA-…` | Monospace | ✔ where not effective |

### 4.3 Internal audit report

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| IAR no. | নিরীক্ষা নং | `MD-040` sequence | Monospace | ✔ |
| Audit dates | নিরীক্ষার তারিখ | `audit.from`, `.to` | Dates | ✔ |
| Scope | পরিধি | `audit.scope` | Text: processes, sites | ✔ |
| **Criteria** | মানদণ্ড | `audit.criteria` | ISO clauses, SOPs, contracts | ✔ |
| Lead auditor / team | নিরীক্ষক | `employee` + qualification | Text | ✔ |
| **Auditor independence** | নিরীক্ষকের স্বাধীনতা | Statement | Text | ✔ — auditor does not audit their own work |
| Auditee | নিরীক্ষিত | Process owner(s) | Text | ✔ |
| Sample examined | নমুনা | `audit.sample` | Text: records, quantity, period | ✔ |
| Finding | পর্যবেক্ষণ | Per finding | Classification + description + evidence + requirement | ✔ |
| NCR raised | উত্থাপিত এনসিআর | `NCR-…` | Monospace | ✔ per finding requiring one |
| Positive observation | ইতিবাচক পর্যবেক্ষণ | `audit.positive[]` | Text | ✔ (prints "None recorded") |
| Opportunity for improvement | উন্নয়নের সুযোগ | `audit.ofi[]` | Text | Where identified |
| Conclusion | উপসংহার | `audit.conclusion` | Text | ✔ |
| Auditee acknowledgement | নিরীক্ষিতের স্বীকৃতি | Signature + date | ✔ | ✔ |

| # | Rule |
|---|---|
| **FM-43-a** | **A root cause that is a restatement of the problem is rejected.** "The technician did not follow the procedure" is not a root cause; why they did not is |
| **FM-43-b** | The preventive block asks a different question from the corrective block: *where else could this happen?* A blank systemic scope means nobody asked |
| **FM-43-c** | Effectiveness is verified by **someone other than the CAPA owner**, after the defined interval — not on the day the action is implemented (`BRU-QMS-03`) |
| **FM-43-d** | `not effective` re-raises a new CAPA. **It does not extend the old one**, because an extended CAPA hides how long the problem has been open |
| **FM-43-e** | Repeated non-conformance in the same process automatically raises a management-review item (`BRU-QMS-05`) |
| **FM-43-f** | Auditor independence is stated, not assumed. An auditor auditing their own process is the finding most likely to be raised **against us** |
| **FM-43-g** | A customer complaint cannot be closed without confirming the outcome with the customer (`BRU-QMS-04`) — the NCR records that confirmation |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-QMS-01` | Checklists with unanswered mandatory items cannot complete — a common NCR source |
| `BRU-QMS-02` | Root cause and CAPA required before NCR closure |
| `BRU-QMS-03` | Effectiveness verification required before CAPA closure |
| `BRU-QMS-04` | Complaint closure requires customer confirmation |
| `BRU-QMS-05` | Repetition triggers a management-review item |
| `BRU-INV-07` | Failed goods to quarantine — a disposition option on the NCR |
| `BRU-SRM-06` | Rework flagging is an NCR source |
| `BRU-TRF-05` | Grade overrides are an NCR source where the justification is inadequate |

### 5.1 Where the chain actually breaks

| # | Failure | Control |
|---|---|---|
| **CB-01** | Root cause is the problem restated | Root-cause method recorded; Quality rejects restatements (`FM-43-a`) |
| **CB-02** | Corrective action is containment | Separate blocks (`L-43-b`) |
| **CB-03** | Preventive action is blank or copies the corrective | Distinct block with a systemic-scope question (`FM-43-b`) |
| **CB-04** | Effectiveness "verified" the day of implementation | Interval set at raise time; verification cannot be recorded before it (`FM-43-c`) |
| **CB-05** | Effectiveness verified by the person who did the work | Different verifier enforced by identity |
| **CB-06** | Ineffective CAPAs quietly extended | `not effective` re-raises (`FM-43-d`) |
| **CB-07** | NCRs raised and never closed | Open-NCR ageing reported weekly, by process owner |
| **CB-08** | Audit findings without evidence | Evidence mandatory per finding |

> **CB-04 and CB-06 are what a certification auditor looks for first**, because they are the two
> that make a CAPA system look functional while achieving nothing.

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Standard NCR** | Any non-conformance | The base form |
| **Critical NCR** | Safety, statutory or customer-impacting | Immediate escalation, containment within a defined time, senior sign-off |
| **Supplier NCR** | Defect attributable to a supplier | Issued to the supplier; feeds the scorecard (`M42`, `DT-024`) |
| **Customer complaint NCR** | From `M34` | Customer confirmation required at closure (`BRU-QMS-04`) |
| **Standard CAPA** | Following any NCR | The base form |
| **Preventive-only CAPA** | Raised from a risk or trend, no NCR | No linked NCR; the trigger is stated |
| **Internal audit report** | Planned programme (ISO 9.2) | Scope, criteria, sample, findings |
| **Surveillance / certification audit response** | External audit findings | Same CAPA discipline, external deadline, certification-body correspondence attached |
| **Management review pack input** | ISO 9.3 | Aggregated NCR/CAPA status, trends and repeat findings |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-043-S1` | Minor NCR from a failed QC checklist | NCR with requirement, containment and disposition |
| `DT-043-S2` | CAPA with 5-why root cause | `FM-43-a` genuine cause and distinct preventive action |
| `DT-043-S3` | CAPA verified ineffective, re-raised | `FM-43-d` |
| `DT-043-S4` | Internal audit of the workshop process | Scope, criteria, sample, findings, positive observations |
| `DT-043-S5` | Repeat non-conformance in one process | `BRU-QMS-05` management-review item |
| `DT-043-S6` | Supplier NCR | Scorecard linkage |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Quality with Internal Audit | 2026-08-15 | Draft issue |
| Reviewer — Operations | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| **Reviewer — ISO certification consultant** | *pending* | | **Required; clause references depend on it** |
| Approver — Quality Manager with COO | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequences | Three: `NCR-…`, `CPA-…`, `IAR-…` |
| Gap policy | `gaps_recorded`; a withdrawn NCR retains its number with a reason |
| Archive format | PDF/A-3 for audit reports and closed CAPAs; standard PDF for NCRs |
| Retention | `LG-009`; **not less than one full certification cycle plus one**, so a surveillance audit can examine the prior cycle |
| Linkage | NCR → CAPA → effectiveness verification retrievable as one chain; audit findings link to the NCRs they raised |
| Re-render | Prohibited after closure |
| Reprint | Watermarked **COPY** |
| Evidence | Photographs, records sampled and measurement data retained with the form |
| Certification body access | The full chain for any sampled finding is producible on request during an audit |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`../05A_Service_and_Operations/DT-008_Quality_Checklist_Record.md`](../05A_Service_and_Operations/DT-008_Quality_Checklist_Record.md) | A FAIL routes here; a primary NCR source |
| [`../05C_Supply_Chain_and_Logistics/DT-024_Goods_Receipt_Note_and_Inspection_Record.md`](../05C_Supply_Chain_and_Logistics/DT-024_Goods_Receipt_Note_and_Inspection_Record.md) | Supplier NCR source and scorecard |
| [`../05D_Commercial_and_Contract/DT-036_Refurbishment_Grading_and_Certification_Record.md`](../05D_Commercial_and_Contract/DT-036_Refurbishment_Grading_and_Certification_Record.md) | Grade-override NCR source |
| [`DT-042_HR_Letter_Template_Set.md`](DT-042_HR_Letter_Template_Set.md) | Where conduct is involved, the disciplinary process is separate from the quality process |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md) | Classification and reason vocabulary |
| [`SP-029_SOP_Internal_Quality_Audit_and_CAPA.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) | The process |
| [`SP-029_SOP_Internal_Quality_Audit_and_CAPA.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) | The audit programme (ISO 9.2) |
| `UI-021` P11 Field Auditor App UI Copy Pack | The working surface |
| `RP-012` Alert Threshold and Anomaly Rule Register | NCR ageing, repeat findings and CAPA effectiveness reporting |
| `TR-016` Course Pack — Quality and Field Auditor | Auditor qualification |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Three forms as one chain, containment separated from corrective action, distinct preventive block with systemic scope, effectiveness verified by a different person after an interval set at raise time, eight chain-break controls | Quality Manager with COO (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Containment and corrective action separated (`L-43-b`)
- [x] Preventive action given its own block and systemic-scope question
- [x] Effectiveness verification by a different person after a pre-set interval
- [x] Ineffective CAPAs re-raised rather than extended
- [x] Auditor independence stated on the report
- [x] All internal links resolve
- [ ] ISO 9001:2015 clause references confirmed by the certification consultant — **outstanding**
- [ ] Finding classification thresholds (critical / major / minor) agreed with Quality — **outstanding**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
