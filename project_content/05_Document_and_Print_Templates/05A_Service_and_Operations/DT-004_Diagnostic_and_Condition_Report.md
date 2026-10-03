---
id: DT-004
title: Diagnostic and Condition Report
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Technical
author: Technical with Quality and Content Design
reviewers: [Quality, Warranty, Operations, Legal & Compliance, Localisation Lead]
approver: Chief Technology Officer with Quality Manager
content_class: C
purpose: >
  The structured record of what was found: fault codes, evidence, root cause, recommendation and
  out-of-scope observations. It justifies the estimate to the customer, the claim to the brand
  and the decision to the auditor. Without it, an estimate is a number with no reasoning and a
  warranty claim has no technical basis.
traces_to: [M31, M01, M09, M23, P08, DT-001, DT-002, DT-005, DT-033, MD-024, MD-025, BRU-SRM-12, BRU-WTY-01, BRU-SRM-17]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: DT-004_Diagnostic_and_Condition_Report_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-WTY-01 — a warranty claim requires a completed work order, device serial, at least one before-photo, a technician diagnosis and the replaced-parts list
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-12 — beyond-economic-repair requires photographic evidence and a second technician's confirmation
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-17 — before/after photographs mandatory on every warranty job
    verified: 2026-08-15
    class: P1
  - source: project_content/05_Document_and_Print_Templates/05A_Service_and_Operations/DT-002 §6.1 — the intake condition enumeration this report measures against
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-004 — Diagnostic and Condition Report

> **One report, three audiences.** The customer needs to understand why the repair costs what it
> costs. The brand needs technical evidence that the fault is covered. The auditor needs to see
> that the recommendation followed from the findings.
>
> A report written for only one of them fails the other two. §6 defines how the same findings are
> presented to each without becoming three different documents.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Technical findings report |
| Owning module | `M31` Workshop and Depot Repair, with `M01` |
| Statutory | No — but it is the technical evidence inside `DT-033`, which a brand partner audits |
| Recipient(s) | Customer, brand partner (inside the claim pack), internal quality, auditor |
| Languages | **Bilingual — stacked labels, parallel columns for the recommendation** |
| Output formats | A4 portrait · PDF for portal download (`P01`, `P04`) · embedded in `DT-033` |
| Numbering mask | `MD-040` — `DIA-{entity}-{branch}-{yy}-{seq:06d}` |
| Retention period | `LG-009`; matched to the warranty period of the repair it justifies, minimum the tax period |

### 1.1 The chain it sits in

```
DT-002 intake condition  →  DT-004 findings  →  DT-005 estimate  →  work  →  DT-007 completion
                                    │
                                    └──────────→  DT-033 brand claim evidence pack
```

| Upstream | What it supplies |
|---|---|
| `DT-002` §6.1 | The condition **at intake**, which every finding is measured against |
| `DT-003` | The technician's raw working notes |
| `MD-024` | Symptom and diagnostic code taxonomy |

| Downstream | What it must supply |
|---|---|
| `DT-005` | A justification per estimate line. **An estimate line with no finding behind it is a defect** |
| `DT-033` | Diagnosis, evidence and parts list to `BRU-WTY-01` completeness |
| `DT-036` | Where the outcome is trade-in or refurbishment rather than repair |

---

## 2. Statutory Requirements

Not a statutory document. Two binding constraints:

| Constraint | Source | Effect |
|---|---|---|
| Truthful description of goods and services | Consumer Rights Protection Act 2009 — **pending G6** | A finding that overstates a fault to justify a larger estimate is a misrepresentation, not a commercial choice |
| Evidence sufficiency for a brand claim | `BRU-WTY-01`; brand partner agreements (`MD-017`) | An incomplete report is a rejected claim and unrecovered cost |

---

## 3. Layout

**Primary format: A4 portrait**, geometry per `VB-004` §4.

| Zone | Content | Bilingual treatment |
|---|---|---|
| Header | Report number, service order reference, date, branch | Title stacked |
| Party block | Customer left; device, report and technician metadata right | Labels stacked |
| Body | Condition comparison → tests performed → findings → root cause → recommendation → out-of-scope observations | Labels stacked, findings text parallel columns |
| Totals | Not used | — |
| Statutory block | Not used. The **technician declaration** occupies this zone | Parallel columns |
| Signature | Technician with certification ID; second technician where `BRU-SRM-12` applies; supervisor | Labels stacked |
| Footer | Report reference, page n of m, hotline | English reference |
| Machine-readable | QR: report reference + evidence-pack case ID (`DT-044`) | — |

| # | Rule |
|---|---|
| **L-04-a** | Findings are **numbered** `F1`, `F2`, … Every estimate line in `DT-005` cites a finding number. This is the mechanism that makes the estimate defensible |
| **L-04-b** | Evidence is referenced by **count and case ID**, and by thumbnail only in the PDF rendition. Printed photographs on a branch printer are not evidence (`DT-002` L-02-b) |
| **L-04-c** | The recommendation block never splits across a page |
| **L-04-d** | Out-of-scope observations print in a visually distinct block. They are not part of the quoted work and the document says so |

---

## 4. Field Mapping

### 4.1 Header and context

| Label EN | Label BN | Source field | Format | Required | Conditional |
|---|---|---|---|:--:|---|
| Report no. | রিপোর্ট নং | `MD-040` sequence | Monospace | ✔ | |
| Service order no. | সার্ভিস অর্ডার নং | `service_order.order_ref` | Monospace | ✔ | |
| Intake reference | গ্রহণ রসিদ নং | `DT-002` reference | Monospace | ✔ | |
| Report date | রিপোর্টের তারিখ | `diagnostic.completed_at` | `DD/MM/YYYY` | ✔ | |
| Device | ডিভাইস | `MD-021` make + model | Text | ✔ | |
| Serial / IMEI | সিরিয়াল / আইএমইআই | `device.serial_no` | Monospace | ✔ | |
| Technician | টেকনিশিয়ান | `employee.display_name` + ID | Text | ✔ | |
| Certification | সনদ | `MD-011.certification_code` | Code | | ✔ on warranty work |
| Repair level assessed | মূল্যায়িত স্তর | `diagnostic.repair_level` | Enum L1/L2/L3 | ✔ | |

### 4.2 Condition comparison

| Label EN | Label BN | Source field | Format | Required | Conditional |
|---|---|---|---|:--:|---|
| Attribute | বৈশিষ্ট্য | `DT-002` §6.1 attribute | Text | ✔ | One row per attribute |
| At intake | গ্রহণকালে | `intake.condition.*` | Enum | ✔ | |
| At diagnosis | পরীক্ষাকালে | `diagnostic.condition.*` | Enum | ✔ | |
| Changed | পরিবর্তিত | Computed | Bool | ✔ | **Any change is flagged and explained** |

| # | Rule |
|---|---|
| **FM-04-a** | Every condition attribute recorded at intake is reproduced here with its diagnosis-time value. A **changed** attribute that is not explained in the findings is a defect and, in a dispute, an admission |
| **FM-04-b** | Where the device could not be powered on at intake (`DT-002` CE-02), the comparison prints "unknown at intake" rather than a value, and the customer-facing note explains why |

### 4.3 Tests, findings and recommendation

| Label EN | Label BN | Source field | Format | Required | Conditional |
|---|---|---|---|:--:|---|
| Test performed | সম্পাদিত পরীক্ষা | `MD-025.diagnostic_action_code` | Code + label | ✔ | One row per test |
| Result | ফলাফল | `diagnostic.test_result` | Enum: pass / fail / inconclusive | ✔ | |
| Instrument used | ব্যবহৃত যন্ত্র | `MD-046.equipment_code` | Code | | ✔ where a calibrated instrument was used |
| Calibration valid to | ক্যালিব্রেশন মেয়াদ | `MD-046.calibration_due` | `DD/MM/YYYY` | | ✔ with instrument |
| Finding no. | পর্যবেক্ষণ নং | `F{n}` | Monospace | ✔ | |
| Symptom code | উপসর্গ কোড | `MD-024.symptom_code` | Code + label | ✔ | |
| Diagnostic code | নির্ণয় কোড | `MD-024.diagnostic_code` | Code + label | ✔ | |
| Finding description | পর্যবেক্ষণের বিবরণ | `diagnostic.finding[].text` | Free text | ✔ | |
| Evidence count | প্রমাণের সংখ্যা | `diagnostic.finding[].evidence_count` | Integer | ✔ | **Minimum 1 per finding** |
| Root cause | মূল কারণ | `diagnostic.root_cause` | Text + `MD-024` code | ✔ | |
| Cause category | কারণের শ্রেণি | `diagnostic.cause_category` | Enum: manufacturing / wear / misuse / liquid / impact / third-party repair / unknown | ✔ | **Drives warranty eligibility** |
| Recommended action | সুপারিশকৃত কার্যক্রম | `MD-025.repair_action_code` | Code + label | ✔ | |
| Parts indicated | প্রয়োজনীয় যন্ত্রাংশ | `MD-022.part_code[]` | List | ✔ | Prints "None" |
| Beyond economic repair | মেরামত অলাভজনক | `diagnostic.ber_flag` | Bool | | **`BRU-SRM-12` evidence + 2nd technician** |
| Out-of-scope observation | পরিধি-বহির্ভূত পর্যবেক্ষণ | `diagnostic.oos_note[]` | Free text | | Prints "None observed" |
| Data-loss risk | ডেটা হারানোর ঝুঁকি | `diagnostic.data_risk` | Enum: none / possible / certain | ✔ | |

| # | Rule |
|---|---|
| **FM-04-c** | `cause_category` is the field that decides whether the repair is a warranty claim or a paid job. It is a **technical determination**, never a commercial one, and the report records who made it |
| **FM-04-d** | Every finding carries at least one evidence item. A finding with zero evidence cannot support an estimate line or a claim (`BRU-WTY-01`) |
| **FM-04-e** | `data_risk` = `certain` prints the data-loss warning in bold in both languages and requires explicit customer acknowledgement on `DT-005` before work begins |
| **FM-04-f** | Out-of-scope observations are recorded because not recording them is how "you broke it" disputes start. They print as observations, never as recommendations to buy |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-SRM-12` | A beyond-economic-repair finding requires photographic evidence and a **second technician's confirmation**; the second signature block prints only when the flag is set, and is mandatory when it is |
| `BRU-SRM-17` | Warranty jobs require before photographs; the evidence count for the pre-work state is validated before the report can be issued |
| `BRU-SRM-14` | An `L3` assessment restricts where the work may be performed; the report carries the assessment even if the work moves to another site |
| `BRU-WTY-01` | The report is one of the five mandatory claim components; incompleteness here blocks claim submission |
| `BRU-WTY-03` | A duplicate claim check runs on serial + fault within 90 days; a matching prior report is cited in this one |
| `BRU-QMS-01` | Diagnostic checklists with unanswered mandatory items cannot be marked complete |
| `BRU-AIM-01` | Where `M26` proposes a diagnosis, the report records it as a **suggestion with confidence**, and the technician's confirmation is the finding. An AI suggestion never prints as a finding |

---

## 6. Variants

The same findings, three presentations. Content is identical; emphasis and vocabulary differ.

| Variant | Audience | Difference |
|---|---|---|
| **Customer report** | Customer, via `P01` or printed | Plain-language finding descriptions alongside the codes; cost implication stated; out-of-scope block prominent; no internal cost data, no supplier names |
| **Brand claim rendition** | Brand partner, inside `DT-033` | Codes and evidence foremost; brand's own fault taxonomy shown where `MD-017` maps to it; `cause_category` and warranty determination prominent; English only where the brand agreement requires it |
| **Internal / audit rendition** | Quality, internal audit, `P11` | Adds instrument calibration status, technician certification, time-to-diagnose, and any AI suggestion with its confidence and whether it was accepted |
| **Corporate estate rendition** | `P04` | Adds asset tag, site, department and cost-centre; aggregates into the estate report |
| **Second-opinion rendition** | Dispute or rework (`BRU-SRM-19`) | Prints the original report's findings in a comparison column against the second technician's |

| # | Rule |
|---|---|
| **V-04-a** | The three renditions are generated from **one record**. A finding cannot say one thing to the customer and another to the brand — that is the failure mode this rule exists to prevent |
| **V-04-b** | Plain-language descriptions are authored per diagnostic code in `MD-024`, not written per job. Free-text plain language is where inconsistency and over-claiming enter |
| **V-04-c** | Internal cost, margin and supplier identity never appear on the customer or brand renditions |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-004-S1` | Handset, screen assembly failure, paid | Base bilingual customer rendition, F-numbered findings |
| `DT-004-S2` | Manufacturing defect, warranty, brand rendition | `cause_category` determination and `BRU-WTY-01` completeness |
| `DT-004-S3` | Liquid damage with a disputed intake LCI reading | Condition-comparison change flag and explanation |
| `DT-004-S4` | Beyond economic repair | `BRU-SRM-12` second-technician block and evidence minimum |
| `DT-004-S5` | AI-suggested diagnosis, technician overrode it | `BRU-AIM-01` handling on the internal rendition |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Technical with Quality | 2026-08-15 | Draft issue |
| Reviewer — Quality | *pending* | | |
| Reviewer — Warranty | *pending* | | |
| Reviewer — Legal & Compliance (misrepresentation exposure) | *pending* | | |
| Approver — CTO with Quality Manager | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `DIA-{entity}-{branch}-{yy}-{seq:06d}` |
| Gap policy | `gaps_recorded` — not a statutory sequence, but an abandoned diagnosis is recorded, not deleted |
| Reset | Fiscal year |
| Archive format | PDF/A-3 at issue where the report supports a brand claim or a dispute; standard PDF otherwise |
| Retention | `LG-009`; **not less than the warranty period granted on the repair it justifies**, because a warranty claim on our own repair is decided against this report |
| Re-render | Prohibited once issued to a customer or a brand (`DT-001` §9.3). A revised diagnosis is a **new report** citing the prior one, never an edit |
| Evidence linkage | Photographs and instrument traces live in `M24` under the report's case ID and inherit its retention |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md`](DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md) | §6.1 condition enumeration this report compares against |
| [`DT-003_Job_Card_and_Work_Order_Print.md`](DT-003_Job_Card_and_Work_Order_Print.md) | Where findings are first written down |
| [`DT-005_Repair_Estimate_and_Quotation.md`](DT-005_Repair_Estimate_and_Quotation.md) | Every estimate line cites a finding number from here |
| [`DT-007_Service_Completion_Report.md`](DT-007_Service_Completion_Report.md) | Closes the loop: what was found, what was done |
| [`../05D_Commercial_and_Contract/DT-033_Warranty_Claim_Evidence_Pack.md`](../05D_Commercial_and_Contract/DT-033_Warranty_Claim_Evidence_Pack.md) | Embeds this report |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md) | Symptom, diagnostic and plain-language descriptions |
| [`../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-046_Test_Equipment_and_Calibration_Master.md`](../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-046_Test_Equipment_and_Calibration_Master.md) | Instrument identity and calibration validity |
| `KB-008` Fault Code Library and Interpretation Guide | The procedures the tests follow |
| [`SP-013_SOP_Estimate_Approval_and_Rework_Control.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-013_SOP_Estimate_Approval_and_Rework_Control.md) | How the report is produced |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. F-numbered findings bound to estimate lines, condition comparison against intake, `cause_category` as the warranty determinant, five renditions from one record, AI-suggestion handling | CTO with Quality Manager (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Findings are numbered and bound to downstream estimate lines (`L-04-a`)
- [x] Evidence minimum stated per finding (`FM-04-d`)
- [x] `cause_category` identified as the warranty determinant, with the technical/commercial boundary stated
- [x] One-record, multi-rendition rule stated (`V-04-a`)
- [x] All internal links resolve
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Plain-language descriptions authored per diagnostic code in `MD-024` — **outstanding, dependency on `MD-024`**
- [ ] Brand-specific fault-taxonomy mappings confirmed with each partner (`MD-017`) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
