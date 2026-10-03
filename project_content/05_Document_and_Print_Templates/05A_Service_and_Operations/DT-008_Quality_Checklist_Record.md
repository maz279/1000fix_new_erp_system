---
id: DT-008
title: Quality Checklist Record
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Quality
author: Quality with Operations and Content Design
reviewers: [Operations, Technical, Warranty, Internal Audit, Localisation Lead]
approver: Quality Manager
content_class: C
purpose: >
  The per-category quality checklist, its pass/fail evidence and the inspector's identity. A
  service order cannot reach Completed unless this record shows a pass (BRU-SRM-04). It is also
  the artefact an ISO 9001:2015 certification body samples, and the first thing examined when a
  rework rate moves.
traces_to: [M23, M01, M31, P11, DT-001, DT-003, DT-007, DT-043, MD-025, MD-026, BRU-SRM-04, BRU-SRM-18, BRU-QMS-01, BRU-QMS-05, 05-05 BRU-SRM-04]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: DT-008_Quality_Checklist_Record_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-04 — a service order cannot reach Completed unless its quality checklist is recorded as passed
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-QMS-01 — a quality checklist cannot be marked complete with unanswered mandatory items
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-18 — independent QC by a second person is mandatory for repairs above BDT 25,000
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 8.6 release of products and services, and clause 7.5 documented information — retained documented information on release, and traceability to the releasing authority
    verified: 2026-08-15
    class: P2
supersedes: none
review_due: 2027-02-15
---

# DT-008 — Quality Checklist Record

> **`BRU-SRM-04` is a hard rule: no pass, no completion.** That makes this the most frequently
> executed control in the business — one per service order, hundreds of thousands a year.
>
> A checklist that can be ticked without looking is worse than no checklist, because it produces
> evidence of a control that did not happen. Everything in §5.1 exists to prevent that.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Inspection record |
| Owning module | `M23` Quality Management System, with `M01` |
| Statutory | No — ISO 9001:2015 certification evidence, which is the company's core differentiator |
| Recipient(s) | Internal quality, certification auditor, brand partner (on request inside `DT-033`), corporate client under contract |
| Languages | **Bilingual — stacked labels.** Inspectors work in Bengali |
| Output formats | A4 portrait · A5 (attached to `DT-003`) · PDF · embedded in `DT-007` and `DT-033` |
| Numbering mask | `MD-040` — `QCR-{entity}-{branch}-{yy}-{seq:06d}` |
| Retention period | `LG-009`; **not less than the ISO certification cycle plus one**, so a surveillance audit can sample the prior cycle |

### 1.1 Where checklists come from

| Source | What it supplies |
|---|---|
| `MD-025` | The action and test codes each checklist item is built from |
| `MD-021` device category | Which checklist template applies |
| `MD-019` service type | Category-specific additions (data services, rental return, refurbishment) |
| `MD-017` brand partner | Brand-mandated additional checks for authorised warranty work |
| [`SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md) | The QC inspection SOP the inspector follows |

> **Checklists are master-data-driven, not authored per job.** A branch that invents its own
> checklist has created an unauditable control. Requests for new items go to `M23`, which
> versions the checklist template — never to the inspector.

---

## 2. Statutory Requirements

Not statutory. Certification-binding:

| Requirement | Source | Effect |
|---|---|---|
| Retained documented information on release of product/service | ISO 9001:2015 §8.6 — *to be confirmed against the standard text by the certification consultant* | This record is that documented information |
| Traceability to the person authorising release | ISO 9001:2015 §8.6 | Inspector identity is mandatory, never a shared branch login |
| Control of nonconforming output | ISO 9001:2015 §8.7 | A fail routes to `DT-043` NCR, not back to the bench informally |
| Evidence of monitoring and measurement | ISO 9001:2015 §9.1 | Pass/fail rates feed `RP-012` and management review |

---

## 3. Layout

**Primary format: A4 portrait.** The A5 variant attaches to the job card.

| Zone | Content | Bilingual treatment |
|---|---|---|
| Header | Record number, checklist template ID and version, order reference | Title stacked |
| Party block | Device and order left; inspection metadata right | Labels stacked |
| Body | **Checklist items** — one row per item, with result, evidence and note | Item text stacked BN over EN |
| Totals | Item counts: passed / failed / not applicable, and the **overall result** | — |
| Statutory block | Not used. The **inspector declaration** occupies this zone | Parallel columns |
| Signature | Inspector with ID; second inspector where `BRU-SRM-18` applies; supervisor on a fail | Labels stacked |
| Footer | Record reference, page n of m, checklist template version | English reference |

| # | Rule |
|---|---|
| **L-08-a** | The **checklist template ID and version** print in the header. A record that cannot be tied to the checklist version it used is not evidence |
| **L-08-b** | Every item prints its own row with an explicit result. There is no "tick all" and no blank-means-pass |
| **L-08-c** | The overall result prints as a single unambiguous word — **PASS** or **FAIL** — in the largest type on the page |
| **L-08-d** | A failed item prints its `MD-026` reason code and the NCR reference raised for it |
| **L-08-e** | Where a checklist exceeds one page, the overall result never appears alone on a continuation page (`VB-004` G-05) |

---

## 4. Field Mapping

### 4.1 Header and context

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| QC record no. | মান রেকর্ড নং | `MD-040` sequence | Monospace | ✔ |
| Checklist template | তালিকা টেমপ্লেট | `M23.checklist_template_id` | Monospace | ✔ |
| Template version | সংস্করণ | `M23.checklist_version` | `v{n}.{n}` | ✔ |
| Service order no. | সার্ভিস অর্ডার নং | `service_order.order_ref` | Monospace | ✔ |
| Device | ডিভাইস | `MD-021` make + model | Text | ✔ |
| Serial / IMEI | সিরিয়াল | `device.serial_no` | Monospace | ✔ |
| Service category | সেবার শ্রেণি | `MD-019.service_code` | Code + label | ✔ |
| Repair value | মেরামত মূল্য | `service_order.total_value` | BDT | ✔ — **drives `BRU-SRM-18`** |
| Inspected at | পরিদর্শনের সময় | `qc.inspected_at` | `DD/MM/YYYY HH:mm` | ✔ |
| Inspector | পরিদর্শক | `employee.display_name` + ID | Text | ✔ |
| Technician who performed the work | কাজ সম্পাদনকারী | `employee.display_name` + ID | Text | ✔ |

### 4.2 Checklist items

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Item no. | ক্রমিক | Template order | Integer | ✔ |
| Check description | পরীক্ষার বিবরণ | `M23.checklist_item.text_en` / `.text_bn` | Text | ✔ |
| Mandatory | বাধ্যতামূলক | `M23.checklist_item.mandatory` | Bool | ✔ |
| Result | ফলাফল | `qc.item_result` | Enum: pass / fail / **n/a with reason** | ✔ |
| Measured value | পরিমাপ | `qc.item_value` | Number + unit | Where the item is a measurement |
| Tolerance | সহনসীমা | `M23.checklist_item.tolerance` | Range | Where measured |
| Instrument | যন্ত্র | `MD-046.equipment_code` | Code | Where measured |
| Evidence | প্রমাণ | `qc.item_evidence_count` | Integer | **✔ on every fail** |
| Reason code | কারণ কোড | `MD-026.reason_code` | Code + label | **✔ on every fail and every n/a** |
| Note | মন্তব্য | `qc.item_note` | Free text | Where reason code is insufficient |

### 4.3 Result and declaration

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Items passed | উত্তীর্ণ | Computed | Integer | ✔ |
| Items failed | ব্যর্থ | Computed | Integer | ✔ |
| Items not applicable | প্রযোজ্য নয় | Computed | Integer | ✔ |
| **Overall result** | **সামগ্রিক ফলাফল** | Computed | **PASS / FAIL** | ✔ |
| NCR raised | এনসিআর | `DT-043` reference | Monospace | ✔ on FAIL |
| Independent inspector | স্বতন্ত্র পরিদর্শক | `employee.display_name` + ID | Text | **✔ above BDT 25,000** |
| Inspector declaration | পরিদর্শকের ঘোষণা | Static | Text, both languages | ✔ |
| Re-inspection of | পুনঃপরিদর্শন | Prior `QCR-` reference | Monospace | ✔ where applicable |

| # | Rule |
|---|---|
| **FM-08-a** | **A mandatory item cannot be left unanswered** (`BRU-QMS-01`). The record cannot be submitted, let alone printed |
| **FM-08-b** | `n/a` requires a reason code. Unreasoned `n/a` is the most common way a checklist is defeated, and the second most common certification finding |
| **FM-08-c** | **Any** mandatory item failing makes the overall result FAIL. There is no weighted score and no supervisor discretion at the item level |
| **FM-08-d** | Every fail carries evidence. A fail with no evidence cannot support the NCR that must follow it (`BRU-QMS-02`) |
| **FM-08-e** | Where the item is a measurement, the value, tolerance and instrument all print. "Pass" with no reading is an opinion |
| **FM-08-f** | The inspector must be a **different person** from the technician on every job, not only above BDT 25,000. `BRU-SRM-18` raises the bar to a second *independent* inspector above that value |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-SRM-04` | The order cannot reach Completed without a PASS on this record |
| `BRU-SRM-18` | Above BDT 25,000 an independent second inspector signs; the system blocks the same user in both roles |
| `BRU-QMS-01` | Unanswered mandatory items block completion of the checklist |
| `BRU-QMS-02` | Every non-conformance requires a root cause and a CAPA before closure — the FAIL path routes to `DT-043` |
| `BRU-QMS-05` | Repeated non-conformance in the same process triggers a mandatory management-review item |
| `BRU-INV-07` | Goods failing inspection go to quarantine, never to available stock — the parts equivalent of this control |
| `BRU-SEC-07` | Incompatible duty combinations are blocked; technician and inspector cannot be the same identity |
| `BRU-LMS-01` | An inspector with overdue mandatory training is restricted from the affected work types |

### 5.1 Anti-rubber-stamp controls

The controls that make the record evidence rather than a formality.

| # | Control |
|---|---|
| **AR-01** | Inspector ≠ technician, enforced by identity, not by policy (`BRU-SEC-07`) |
| **AR-02** | Timestamps are captured per item, not per record. A 30-item checklist completed in 40 seconds is flagged for review |
| **AR-03** | Measured items require a value. A tick alone is rejected |
| **AR-04** | `n/a` requires a reason code, and `n/a` rates per inspector are reported in `RP-012` |
| **AR-05** | A sample of PASS records is re-inspected independently each period; the re-inspection cites the original record |
| **AR-06** | Pass rates of 100% sustained by an inspector are an audit signal, not an achievement — surfaced in `RP-012` |
| **AR-07** | The rework rate (`BRU-SRM-06`) is reconciled against QC pass rates. Rework on a passed job is a checklist failure, not only a repair failure |

> **AR-07 is the one that matters.** Every rework on a job that passed QC is either an item the
> checklist does not contain or an item that was not really checked. Both are findings, and both
> are actionable — which is why `RP-012` reports them together.

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Standard A4** | Bench and field repair | The base record |
| **A5 job-card attachment** | Printed with `DT-003` | Same items, compressed; transcribed into the system before completion |
| **Brand-mandated** | Authorised warranty work | Adds the brand's required items from `MD-017`; brand item numbering preserved so the brand can read it |
| **Data services** | `M06` cases | Adds chain-of-custody verification and the wipe/destruction verification step |
| **Rental return** | `M13` | Adds the inbound condition comparison against the outbound report (`DT-037`, `BRU-RNT-03`) |
| **Refurbishment** | `M14` | The grading protocol; feeds `DT-036` (`BRU-TRF-03`) |
| **Re-inspection** | Sample audit (`AR-05`) or post-fail re-check | Cites the original record and prints both results side by side |
| **Corporate contract** | Where the contract requires QC evidence | Released to the client with technician identity present but internal notes suppressed |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-008-S1` | Handset repair, 18-item checklist, PASS | Base bilingual rendition |
| `DT-008-S2` | One mandatory item FAIL | FAIL result, NCR reference, evidence requirement |
| `DT-008-S3` | BDT 31,000 repair | Independent second inspector block |
| `DT-008-S4` | Measured items with tolerances and instrument | `FM-08-e` |
| `DT-008-S5` | Three items marked n/a with reasons | `FM-08-b` |
| `DT-008-S6` | Re-inspection of a passed job that later reworked | `AR-05` / `AR-07` |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Quality with Operations | 2026-08-15 | Draft issue |
| Reviewer — Operations | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| Reviewer — ISO certification consultant | *pending* | | |
| Approver — Quality Manager | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `QCR-{entity}-{branch}-{yy}-{seq:06d}` |
| Gap policy | `gaps_recorded` — an abandoned inspection is recorded, never deleted |
| Reset | Fiscal year |
| Archive format | PDF/A-3 where the record supports a brand claim or a contractual QC obligation; standard PDF otherwise |
| Retention | `LG-009`; **not less than one full ISO certification cycle plus one**, so a surveillance audit can sample the prior cycle |
| Re-render | Prohibited. Checklist templates are versioned; a re-render would apply today's template to yesterday's inspection (`DT-001` §9.3) |
| Template versioning | Every checklist template version is retained for as long as any record cites it. **A retired template is archived, never deleted** (`CP-10`) |
| Reprint | Watermarked **COPY**, logged |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-003_Job_Card_and_Work_Order_Print.md`](DT-003_Job_Card_and_Work_Order_Print.md) | Carries the A5 attachment variant |
| [`DT-007_Service_Completion_Report.md`](DT-007_Service_Completion_Report.md) | Cites this record's PASS; cannot render without it |
| [`../05E_People_Quality_and_Labelling/DT-043_NCR_CAPA_and_Internal_Audit_Report_Forms.md`](../05E_People_Quality_and_Labelling/DT-043_NCR_CAPA_and_Internal_Audit_Report_Forms.md) | Where a FAIL routes |
| [`../05D_Commercial_and_Contract/DT-036_Refurbishment_Grading_and_Certification_Record.md`](../05D_Commercial_and_Contract/DT-036_Refurbishment_Grading_and_Certification_Record.md) | The refurbishment variant feeds it |
| [`../05D_Commercial_and_Contract/DT-037_Rental_Agreement_and_Asset_Handover_Record.md`](../05D_Commercial_and_Contract/DT-037_Rental_Agreement_and_Asset_Handover_Record.md) | The rental-return variant compares against it |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md) | Where checklist items are built from |
| [`../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-046_Test_Equipment_and_Calibration_Master.md`](../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-046_Test_Equipment_and_Calibration_Master.md) | Instruments for measured items |
| `RP-012` Alert Threshold and Anomaly Rule Register | Where `AR-04`, `AR-06` and `AR-07` are reported |
| [`SP-032_Operational_Checklist_Library.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-032_Operational_Checklist_Library.md) | How an inspector performs it |
| `TS-012` End-to-End Business Scenario Pack | Where the `BRU-SRM-04` block is tested |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Template-version binding, per-item result discipline, seven anti-rubber-stamp controls, FAIL-to-NCR routing, eight variants, ISO retention rule | Quality Manager (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Checklist template ID and version bound into the record (`L-08-a`)
- [x] Anti-rubber-stamp controls stated as enforceable rules, not aspirations
- [x] FAIL routing to `DT-043` specified
- [x] Retention tied to the certification cycle
- [x] All internal links resolve
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] ISO 9001:2015 clause citations confirmed by the certification consultant — **outstanding**
- [ ] Brand-mandated checklist items collected per partner (`MD-017`) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
