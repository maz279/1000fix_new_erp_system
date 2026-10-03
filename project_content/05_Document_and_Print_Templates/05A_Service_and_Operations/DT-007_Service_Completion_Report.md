---
id: DT-007
title: Service Completion Report
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Operations with Quality
author: Operations with Quality and Content Design
reviewers: [Quality, Warranty, Technical, Legal & Compliance, Localisation Lead]
approver: Chief Operating Officer with Quality Manager
content_class: C
purpose: >
  The record of what was actually done: work performed, parts replaced with serials, tests
  passed, warranty granted on the repair, and the identity and certification of the technician
  who did it. It is given to the customer, submitted to the brand, and cited in any warranty
  claim on the repair itself.
traces_to: [M01, M23, M09, M31, P08, DT-001, DT-003, DT-004, DT-008, DT-009, DT-032, DT-033, MD-025, MD-031, BRU-SRM-04, BRU-SRM-17, BRU-SRM-18, BRU-INV-08]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: DT-007_Service_Completion_Report_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-04 — a service order cannot reach Completed unless its quality checklist is recorded as passed
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-17 — before/after photographs mandatory on every warranty job; the job cannot close without them
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-06 — a new order for the same device and fault category within 30 days is flagged as rework
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-INV-08 — serialised parts must have their serial captured at both receipt and issue
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-007 — Service Completion Report

> **This is the document the company is judged by.** The customer reads it to know what they
> paid for. The brand reads it to decide a claim. A future technician reads it to know what was
> already tried. An auditor reads it to confirm the quality gate was passed.
>
> **`BRU-SRM-04`: an order cannot reach Completed unless its quality checklist is recorded as
> passed.** This report prints that fact, or it does not print.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Work completion record |
| Owning module | `M01`, with `M23` Quality Management |
| Statutory | No — but it is the evidence base for the repair warranty in `DT-032` and the claim in `DT-033` |
| Recipient(s) | Customer, brand partner, quality, future technician, auditor |
| Languages | **Bilingual — stacked labels, parallel columns for the warranty statement** |
| Output formats | A4 portrait · PDF for portal and email · embedded in `DT-033` |
| Numbering mask | `MD-040` — `SCR-{entity}-{branch}-{yy}-{seq:06d}` |
| Retention period | `LG-009`; **not less than the repair warranty period plus the limitation period** |

### 1.1 Preconditions — the report cannot print without these

| # | Precondition | Rule |
|---|---|---|
| 1 | Quality checklist recorded as **passed** | `BRU-SRM-04` |
| 2 | Before and after photographs present on warranty jobs | `BRU-SRM-17` |
| 3 | Serials captured for every serialised part fitted | `BRU-INV-08` |
| 4 | Independent second-person QC where the repair exceeds BDT 25,000 | `BRU-SRM-18` |
| 5 | Technician certification current for brand warranty work | `BRU-SRM-09` |
| 6 | Every approved estimate line either performed or explicitly not performed with a reason | `DT-005`, `DT-006` |

> These are not "should"s. Each is a hard rule in `05-05`, and the report is the place where
> their satisfaction becomes visible to someone outside the company.

---

## 2. Statutory Requirements

Not a statutory document. Three binding constraints:

| Constraint | Source | Effect |
|---|---|---|
| Truthful description of services performed | Consumer Rights Protection Act 2009 — **pending G6** | A report claiming work not done is a misrepresentation |
| Brand claim evidence sufficiency | `BRU-WTY-01`, brand agreements (`MD-017`) | An incomplete report is a rejected claim |
| Warranty statement accuracy | `DT-032`, `MD-031` | The warranty stated here is the warranty the company is bound to honour |

---

## 3. Layout

**Primary format: A4 portrait**, geometry per `VB-004` §4.

| Zone | Content | Bilingual treatment |
|---|---|---|
| Header | Report number, service order reference, completion date, branch | Title stacked |
| Party block | Customer left; device, order, estimate and diagnostic references right | Labels stacked |
| Body | Work performed → parts replaced → tests passed → out-of-scope items not performed → technician and certification | Labels stacked |
| Totals | Not used. Money is on `DT-010` | — |
| Statutory block | **Warranty granted on this repair** — coverage, term, exclusions, how to claim | Parallel columns |
| Signature | Technician + certification; QC inspector; supervisor where `BRU-SRM-18` applies | Labels stacked |
| Footer | Report reference, page n of m, hotline | English reference |
| Machine-readable | QR: report reference + device serial, resolving to the portal record (`DT-044`) | — |

| # | Rule |
|---|---|
| **L-07-a** | Work performed cites the `DT-004` finding number and the `DT-005` estimate line it discharges. The three documents are readable as one chain |
| **L-07-b** | The warranty block never splits across a page |
| **L-07-c** | Approved lines **not** performed print in their own block with a reason. Silence about an unperformed line is how billing disputes begin |
| **L-07-d** | Photograph evidence is referenced by count and case ID; thumbnails appear only in the PDF rendition |

---

## 4. Field Mapping

### 4.1 Header and linkage

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Completion report no. | সমাপ্তি রিপোর্ট নং | `MD-040` sequence | Monospace | ✔ |
| Service order no. | সার্ভিস অর্ডার নং | `service_order.order_ref` | Monospace | ✔ |
| Diagnostic report no. | নির্ণয় রিপোর্ট নং | `DT-004` reference | Monospace | ✔ |
| Estimate no. (+ revisions) | প্রাক্কলন নং | `DT-005` / `DT-006` refs | Monospace | ✔ |
| Intake reference | গ্রহণ রসিদ নং | `DT-002` reference | Monospace | ✔ |
| Completed at | সমাপ্তির সময় | `service_order.completed_at` | `DD/MM/YYYY HH:mm` | ✔ |
| Total time on job | মোট সময় | Computed from `time_log[]` | Hours, 1 dp | ✔ |
| Branch / workshop | শাখা / ওয়ার্কশপ | `MD-003` | Text | ✔ |
| Rework of | পুনঃকাজ | Prior `service_order.order_ref` | Monospace | ✔ where `BRU-SRM-06` flagged |

### 4.2 Work and parts

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Action performed | সম্পাদিত কাজ | `MD-025.repair_action_code` | Code + label | ✔ |
| Discharges finding | সম্পর্কিত পর্যবেক্ষণ | `DT-004` `F{n}` | Monospace | ✔ |
| Discharges estimate line | প্রাক্কলন লাইন | `DT-005` line no. | Integer | ✔ where chargeable |
| Outcome | ফলাফল | `work.outcome` | Enum: resolved / partially resolved / not resolved | ✔ |
| Part fitted | সংযোজিত যন্ত্রাংশ | `MD-022.part_code` + name | Monospace + text | ✔ where parts used |
| Part origin | যন্ত্রাংশের উৎস | `stock_issue.part_origin` | Enum per `DT-005` FM-05-c | ✔ with part |
| New part serial | নতুন সিরিয়াল | `stock_issue.serial_no` | Monospace | **✔ serialised parts (`BRU-INV-08`)** |
| Removed part serial | অপসারিত সিরিয়াল | `stock_return.serial_no` | Monospace | ✔ where captured |
| Old part disposition | পুরাতন যন্ত্রাংশের গতি | `stock_return.disposition` | Enum: returned to customer / retained for brand claim / scrapped / e-waste | ✔ |
| Line not performed | সম্পাদিত হয়নি | `estimate.line` + `MD-026.reason_code` | Text + code | ✔ where applicable |

### 4.3 Tests, quality and warranty

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Test performed | সম্পাদিত পরীক্ষা | `MD-025.test_code` | Code + label | ✔ |
| Result | ফলাফল | `test.result` | Enum: pass / fail | ✔ — **all must be pass** |
| Instrument | যন্ত্র | `MD-046.equipment_code` | Code | Where used |
| Quality checklist | মান পরীক্ষা তালিকা | `DT-008` reference | Monospace + PASSED | ✔ **`BRU-SRM-04`** |
| QC inspector | পরিদর্শক | `employee.display_name` + ID | Text | ✔ |
| Independent QC | স্বতন্ত্র মান পরীক্ষা | `qc.independent` | Bool + inspector | **✔ above BDT 25,000 (`BRU-SRM-18`)** |
| Before photos | পূর্বের ছবি | `evidence.before_count` | Integer | **✔ warranty jobs ≥ 1 (`BRU-SRM-17`)** |
| After photos | পরের ছবি | `evidence.after_count` | Integer | **✔ warranty jobs ≥ 1** |
| Technician | টেকনিশিয়ান | `employee.display_name` + ID | Text | ✔ |
| Certification | সনদ | `MD-011.certification_code` + expiry | Code + date | ✔ on brand warranty work |
| Repair warranty | মেরামতের ওয়ারেন্টি | `MD-031.warranty_type_code` | Code + term | ✔ |
| Warranty from / to | ওয়ারেন্টি শুরু / শেষ | Computed | `DD/MM/YYYY` | ✔ |
| Warranty covers | যা অন্তর্ভুক্ত | `MD-031.coverage_text` | Text | ✔ |
| Warranty excludes | যা অন্তর্ভুক্ত নয় | `MD-031.exclusion_text` | Text | ✔ |
| How to claim | দাবি করার পদ্ধতি | Static + hotline 16743 | Text | ✔ |

| # | Rule |
|---|---|
| **FM-07-a** | Every test result must be `pass`. A `fail` blocks completion; the order returns to work (`BRU-QMS-01`) |
| **FM-07-b** | The warranty statement is generated from `MD-031`, never typed. A technician cannot grant a warranty the company has not defined |
| **FM-07-c** | Warranty on a **customer-supplied part** is excluded and prints as such (`DT-005` term Q-6) |
| **FM-07-d** | `Old part disposition` is mandatory. A removed part with no recorded destination is either a customer complaint or an inventory loss |
| **FM-07-e** | A `partially resolved` or `not resolved` outcome prints prominently with the reason and the recommended next step. Reporting a partial fix as a completion is the fastest route to a rework and a lost customer |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-SRM-04` | The quality checklist reference and its PASSED state are mandatory fields; without them the report cannot render |
| `BRU-SRM-05` | An invoice cannot be raised until the order is Completed — this report is what Completed means in evidence |
| `BRU-SRM-06` | A rework link prints prominently, with the original order reference |
| `BRU-SRM-17` | Before/after photo counts are validated at render on warranty jobs |
| `BRU-SRM-18` | Above BDT 25,000 an independent QC inspector block prints and must be populated by a **different person** |
| `BRU-SRM-19` | Reopening within the repair warranty period links as rework and cites this report |
| `BRU-SRM-20` | Any access note provided at intake is confirmed purged; the report prints the purge confirmation, never the value |
| `BRU-WTY-01` | This report plus `DT-004` and the parts list form the mandatory claim components |
| `BRU-WTY-04` | Brand-supplied warranty parts cannot appear on a non-warranty completion report |
| `BRU-QMS-04` | Where a complaint is linked, closure requires confirmation with the customer; this report is the basis of that conversation |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Customer A4** | The default, handed over at collection with `DT-009` | Plain-language actions from `MD-025`; warranty block prominent; no internal cost |
| **Brand rendition** | Inside `DT-033` | Brand fault codes where mapped (`MD-017`); parts with brand part numbers; certification foremost; English where the agreement requires |
| **Internal / audit** | Quality, `P11` | Adds time breakdown, rework linkage, QC evidence, instrument calibration, cost |
| **Corporate estate** | `P04` | Adds asset tag, site, department, cost centre; feeds the estate report |
| **Field completion** | On-site (`M02`, `P02`) | Signed on the technician app at the customer's location; combines with `DT-009` into a single handover rendition |
| **Marketplace** | `P07` seller job | Seller identity disclosed; the same QC and warranty standards apply (`BRU-ECM-03`) |
| **Not-repaired** | Device returned unrepaired | Prints findings, why no repair was performed, what was and was not charged, and the device's condition at return |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-007-S1` | Screen + battery replaced, paid, 90-day warranty | Base bilingual rendition, chain to `DT-004`/`DT-005` |
| `DT-007-S2` | Warranty job, brand rendition | `BRU-WTY-01` completeness and photo evidence |
| `DT-007-S3` | BDT 31,000 repair | Independent QC block, different inspector |
| `DT-007-S4` | One approved line not performed | `L-07-c` not-performed block with reason |
| `DT-007-S5` | Partially resolved outcome | `FM-07-e` prominence and next-step statement |
| `DT-007-S6` | Rework of a prior order | `BRU-SRM-06` linkage |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Operations with Quality | 2026-08-15 | Draft issue |
| Reviewer — Quality | *pending* | | |
| Reviewer — Warranty | *pending* | | |
| Reviewer — Legal & Compliance | *pending* | | |
| Approver — COO with Quality Manager | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `SCR-{entity}-{branch}-{yy}-{seq:06d}` |
| Gap policy | `gaps_recorded` |
| Reset | Fiscal year |
| Archive format | **PDF/A-3 at issue** — it evidences a warranty the company must honour years later |
| Retention | `LG-009`; not less than the repair warranty term **plus the limitation period**, because a claim on our own repair is decided against this document |
| Re-render | **Prohibited.** `MD-031` warranty terms change; a re-render would restate today's warranty under yesterday's report (`DT-001` §9.3) |
| Reprint | Watermarked **COPY**, logged (`RC-01`, `RC-03`) |
| Evidence linkage | Before/after photographs and test traces live in `M24` under the report's case ID and inherit its retention |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-003_Job_Card_and_Work_Order_Print.md`](DT-003_Job_Card_and_Work_Order_Print.md) | The working record this report is built from |
| [`DT-004_Diagnostic_and_Condition_Report.md`](DT-004_Diagnostic_and_Condition_Report.md) | The findings each action discharges |
| [`DT-005_Repair_Estimate_and_Quotation.md`](DT-005_Repair_Estimate_and_Quotation.md) | The lines each action discharges |
| [`DT-008_Quality_Checklist_Record.md`](DT-008_Quality_Checklist_Record.md) | The `BRU-SRM-04` gate this report cites |
| [`DT-009_Device_Release_and_Collection_Receipt.md`](DT-009_Device_Release_and_Collection_Receipt.md) | Handed over together at collection |
| [`../05D_Commercial_and_Contract/DT-032_Warranty_Certificate_and_Extension_Document.md`](../05D_Commercial_and_Contract/DT-032_Warranty_Certificate_and_Extension_Document.md) | The formal certificate where one is issued |
| [`../05D_Commercial_and_Contract/DT-033_Warranty_Claim_Evidence_Pack.md`](../05D_Commercial_and_Contract/DT-033_Warranty_Claim_Evidence_Pack.md) | Embeds this report |
| [`../../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-031_Warranty_Type_and_Coverage_Term_Catalogue.md`](../../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-031_Warranty_Type_and_Coverage_Term_Catalogue.md) | Where the warranty statement is generated from |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md) | Action and test codes |
| [`SP-010_SOP_Workshop_and_Depot_Repair.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-010_SOP_Workshop_and_Depot_Repair.md) | How a person completes it |
| [`NT-004_SMS_Template_Library_Customer.md`](../../04_Notification_and_Messaging/04A_SMS_and_OTP/NT-004_SMS_Template_Library_Customer.md) | The ready-for-collection message that follows it |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Six render preconditions, action-to-finding-to-estimate-line chain, warranty statement generated from `MD-031`, old-part disposition mandatory, seven renditions | COO with Quality Manager (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Render preconditions enumerated and bound to `05-05` rules
- [x] Warranty statement sourced from `MD-031`, never typed (`FM-07-b`)
- [x] Not-performed lines and partial outcomes given explicit treatment
- [x] Retention tied to the warranty term plus limitation period
- [x] All internal links resolve
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Plain-language action descriptions authored per `MD-025` code — **outstanding, dependency on `MD-025`**
- [ ] Brand part-number and fault-code mappings confirmed per partner (`MD-017`) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
