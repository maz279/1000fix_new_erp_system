---
id: DT-036
title: Refurbishment Grading and Certification Record
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Refurbishment
author: Refurbishment with Quality, Legal & Compliance and Content Design
reviewers: [Quality, Legal Counsel, Commercial, Data Services, Localisation Lead]
approver: Chief Operating Officer with Legal Counsel
content_class: A
purpose: >
  The grade definition applied, tests performed, parts replaced, warranty granted and the
  disclosure statement. Refurbished resale without a defensible grading record produces returns,
  disputes and consumer-protection exposure — the grade is a representation about the goods, and
  a representation that cannot be evidenced is a misrepresentation waiting to be alleged.
traces_to: [M14, M23, M38, M06, DT-001, DT-008, DT-032, DT-034, DT-038, MD-021, MD-025, MD-040, BRU-TRF-01, BRU-TRF-03, BRU-TRF-04, BRU-TRF-05, BRU-QMS-01]
priority: P2
wave: W5
bilingual: yes
bn_counterpart: DT-036_Refurbishment_Grading_and_Certification_Record_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-TRF-03 — a refurbished unit cannot be listed for sale without a completed QA test protocol and an assigned grade
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-TRF-04 — battery health and known defects must be disclosed on every refurbished listing
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-TRF-05 — a supervisor grade override requires a recorded justification
    verified: 2026-08-15
    class: P1
  - source: Consumer Rights Protection Act 2009 — prohibition on misleading description of goods. **To be verified against the enacted text at G6**
    verified: 2026-08-15
    class: P2
supersedes: none
review_due: 2027-02-15
---

# DT-036 — Refurbishment Grading and Certification Record

> ⚠ **Class A — statutory consequence.** A grade is a **representation about goods offered for
> sale**. Consumer-protection law does not care whether the grade was assigned carelessly or
> dishonestly; it cares whether the goods matched the description.
>
> **`BRU-TRF-03`: no listing without a completed QA protocol and an assigned grade.**
> **`BRU-TRF-04`: battery health and known defects disclosed on every listing.**
> **`BRU-TRF-01`: no refurbishment at all without a `DT-034` data destruction record.**

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Grading and refurbishment certification record |
| Owning module | `M14` Trade-In, Refurbishment and Resale, with `M23` |
| Statutory | No prescribed form. **Class A** — consumer-protection representation |
| Recipient(s) | Buyer of the refurbished unit, listing systems (`M38`, `P07`), quality, internal audit |
| Languages | **Bilingual — stacked labels, parallel columns for the disclosure** |
| Output formats | A4 portrait · PDF supplied with the unit · **listing data feed to `M38` / storefront** |
| Numbering mask | `MD-040` — `RGC-{entity}-{yy}-{seq:06d}` |
| Retention period | `LG-009`; **warranty term plus the limitation period**, because a return or claim is decided against it |

### 1.1 Grade definitions

Grades are defined once, here and in `MD-021`, and used identically in every listing, contract and
conversation. **A grade whose meaning varies by channel is not a grade.**

| Grade | Cosmetic | Functional | Battery (where applicable) | Typical disclosure |
|:--:|---|---|---|---|
| **A — As new** | No visible marks at normal viewing distance | Fully functional, all features | ≥ 90% of design capacity | Original or equivalent accessories |
| **B — Excellent** | Light marks not visible in use | Fully functional | ≥ 85% | Marks described |
| **C — Good** | Visible marks, no cracks | Fully functional | ≥ 80% | Marks photographed |
| **D — Fair** | Significant marks, may include minor cracks not affecting use | Fully functional | ≥ 75% | Every defect photographed and described |
| **F — Functional / parts** | Any condition | May have known functional limitations | Any | **Sold as described only, with limitations stated** |

| # | Rule |
|---|---|
| **GR-01** | Thresholds above are **indicative and must be ratified by Quality and Commercial** before first use. They are stated here so that ratification is a decision, not a drafting exercise |
| **GR-02** | The grade is assigned by the QA protocol, **not by the person listing the item** |
| **GR-03** | A supervisor override requires a recorded justification (`BRU-TRF-05`) and is reported |
| **GR-04** | Where cosmetic and functional assessments disagree, **the lower grade applies** |
| **GR-05** | Grade definitions are versioned. A unit sold under version 1 is judged against version 1 |

---

## 2. Statutory Requirements

Not a prescribed form. Four constraints:

| Constraint | Source | Effect |
|---|---|---|
| No misleading description | Consumer Rights Protection Act 2009 — **pending G6** | The grade and disclosures must match the goods |
| Goods must match description | Sale of Goods Act — **pending G6** | A grade is part of the description |
| Data erasure before resale | `BRU-TRF-01`, `DT-034` | Selling a device with prior owner data is a data-protection breach |
| Warranty statement accuracy | `DT-032`, `MD-031` | The warranty offered on a refurbished unit binds us |

### 2.1 G6 questions

| # | Question |
|---|---|
| **RF1** | What must be disclosed when selling refurbished goods to a consumer, and how prominently? |
| **RF2** | What statutory rights attach to refurbished goods, and can any be limited? |
| **RF3** | Is the term "refurbished" itself regulated or defined anywhere applicable? |
| **RF4** | What is the return-rights position for refurbished goods sold online (`M38`)? |
| **RF5** | Where a grade proves wrong, what is the remedy, and does a documented grading process limit exposure? |

---

## 3. Layout

| Zone | Content | Bilingual |
|---|---|---|
| Header | Record number, **grade assigned**, unit identity, date | Title stacked, grade prominent |
| Party block | Unit and provenance left; refurbishment centre, technician and QA inspector right |
| Body | Provenance → data destruction → work performed → parts replaced → QA test results → cosmetic assessment → battery health → known defects | Labels stacked |
| Totals | Not used | — |
| Statutory block | **The disclosure statement** — what the buyer is told | **Parallel columns** |
| Signature | Refurbishment technician and QA inspector, both named | Labels stacked |
| Footer | Record reference, `page n of m`, grade-definition version | English |
| Machine-readable | QR: record reference resolving to the buyer-facing record (`DT-044`) | — |

| # | Rule |
|---|---|
| **L-36-a** | **The grade appears in the header, at the largest size on the page.** It is the single fact the buyer relies on |
| **L-36-b** | The **grade-definition version** prints in the footer (`GR-05`) |
| **L-36-c** | Known defects are a numbered list with photographs referenced. "Minor cosmetic wear" is not a disclosure |
| **L-36-d** | Battery health prints as a **figure**, not a description (`BRU-TRF-04`) |
| **L-36-e** | The disclosure block never splits across a page |
| **L-36-f** | The listing feed carries the **same** grade, battery figure and defect list as this record. A listing that says less than the record is the exposure this document exists to prevent |

---

## 4. Field Mapping

### 4.1 Unit, provenance and preparation

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Record no. | রেকর্ড নং | `MD-040` sequence | Monospace | ✔ |
| **Grade assigned** | নির্ধারিত গ্রেড | `refurb.grade` | A / B / C / D / F | ✔ |
| Grade definition version | গ্রেড সংস্করণ | `MD-021.grade_def_version` | `v{n}.{n}` | ✔ |
| Date graded | গ্রেডিংয়ের তারিখ | `refurb.graded_at` | `DD/MM/YYYY` | ✔ |
| Make / model | মেক / মডেল | `MD-021` | Text | ✔ |
| **Serial / IMEI** | সিরিয়াল | `device.serial_no` | Monospace | ✔ |
| Provenance | উৎস | `refurb.source` | Enum: trade-in / unclaimed / returned / stock | ✔ |
| Trade-in reference | ট্রেড-ইন সূত্র | `DT-038` reference | Monospace | Where trade-in |
| **Data destruction certificate** | ডেটা ধ্বংস সনদ | `DT-034` reference | Monospace | ✔ **`BRU-TRF-01`** |
| Provenance / stolen-device check | উৎস যাচাই | `BRU-TRF-02` result | Pass/fail + reference | ✔ |
| Refurbishment centre | কেন্দ্র | `MD-003` / `MD-004` | Text | ✔ |
| Technician | টেকনিশিয়ান | `employee.display_name` + ID | Text | ✔ |

### 4.2 Work, tests and condition

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Work performed | সম্পাদিত কাজ | `MD-025.repair_action_code` | Code + label | ✔ |
| Part replaced | প্রতিস্থাপিত যন্ত্রাংশ | `MD-022.part_code` + name | Monospace + text | ✔ where any |
| Part origin | যন্ত্রাংশের উৎস | `stock_issue.part_origin` | Enum: OEM / OEM-equivalent / harvested | ✔ **disclosed** |
| **QA protocol** | কিউএ প্রোটোকল | `DT-008` reference | Monospace | ✔ **`BRU-TRF-03`** |
| QA result | ফলাফল | `DT-008` overall | PASS required | ✔ |
| Functional test | কার্যকারিতা পরীক্ষা | `MD-025.test_code` per feature | Table pass/fail | ✔ |
| Feature limitation | সীমাবদ্ধতা | `refurb.limitation[]` | Text | ✔ grade F, where any |
| Cosmetic assessment | বাহ্যিক মূল্যায়ন | `DT-002` §6.1 attributes | Enum per attribute | ✔ |
| Cosmetic photographs | ছবি | `M24` count | Integer | ✔ **minimum per grade** |
| **Battery health** | ব্যাটারির স্বাস্থ্য | `refurb.battery_health_pct` | %, integer | ✔ **`BRU-TRF-04`** |
| Battery cycle count | চার্জ চক্র | `refurb.battery_cycles` | Integer | Where available |
| Battery replaced | ব্যাটারি প্রতিস্থাপিত | Bool | Bool | ✔ |
| **Known defects** | জ্ঞাত ত্রুটি | `refurb.defect[]` numbered | Numbered list + photo ref | ✔ (prints "None") |
| Accessories included | অন্তর্ভুক্ত আনুষঙ্গিক | `refurb.accessories[]` | List | ✔ |
| Accessory origin | আনুষঙ্গিকের উৎস | Enum: original / equivalent / none | ✔ |
| **Warranty offered** | প্রদত্ত ওয়ারেন্টি | `MD-031` + `DT-032` | Term + reference | ✔ |
| QA inspector | কিউএ পরিদর্শক | `employee.display_name` + ID | Text | ✔ **different from the technician** |
| Grade override | গ্রেড পরিবর্তন | `refurb.override_by` + justification | Text | ✔ where overridden (`BRU-TRF-05`) |

| # | Rule |
|---|---|
| **FM-36-a** | The record **cannot be created** without a `DT-034` reference (`BRU-TRF-01`) and a passed QA protocol (`BRU-TRF-03`) |
| **FM-36-b** | Battery health is a measured figure. "Good" is not a battery health value |
| **FM-36-c** | Harvested parts — taken from another unit — are disclosed as such. A buyer who discovers this later reasonably feels misled |
| **FM-36-d** | Defects are numbered so that a return claim can cite one, and so that "you didn't tell me" is answerable |
| **FM-36-e** | An override to a **higher** grade requires the justification and a second approver; an override downward requires only the justification |
| **FM-36-f** | The photograph minimum rises as the grade falls. A grade D unit needs its defects visible, not described |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-TRF-01` | Data destruction before refurbishment or resale |
| `BRU-TRF-02` | Provenance and stolen-device screening before a trade-in offer is paid |
| `BRU-TRF-03` | QA protocol and grade before listing |
| `BRU-TRF-04` | Battery health and known defects disclosed on every listing |
| `BRU-TRF-05` | Supervisor override requires recorded justification |
| `BRU-QMS-01` | Checklists cannot be completed with unanswered mandatory items |
| `BRU-ECM-06` | Promotion disclosure on marketplace listings is separate from, and additional to, grade disclosure |
| `BRU-SEC-07` | Technician and QA inspector are different identities |

### 5.1 Grade integrity

| # | Rule |
|---|---|
| **GI-01** | Grade distribution by centre and by inspector is reported. A centre producing markedly more grade A units than its peers is either better or wrong |
| **GI-02** | Return and complaint rates are analysed **by grade**. A grade with a high return rate is mis-defined or mis-applied |
| **GI-03** | Overrides are reported by approver and direction (`FM-36-e`) |
| **GI-04** | A sample of graded units is re-inspected independently each period, and the re-inspection cites the original record |
| **GI-05** | Where a return is upheld on condition grounds, the original record is reviewed and, if the grading was wrong, the batch graded by the same inspector that period is re-checked |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Standard grading record** | Any refurbished unit for resale | The base record |
| **Grade F / parts** | Sold as functional-with-limitations or for parts | Limitations foremost; warranty position stated explicitly |
| **Trade-in reject** | Unit not viable for refurbishment | Records the assessment and routes to `DT-035` e-waste |
| **Marketplace listing feed** | `P07` / `M38` | Structured data carrying grade, battery figure and defect list (`L-36-f`) |
| **Corporate bulk refurbishment** | Client's own estate refurbished and returned | No resale; the record evidences the work to the client |
| **Re-grade** | Unit re-assessed after a return | New record referencing the original; both retained |
| **Warranty-bearing** | Where an extended warranty is sold with the unit | `DT-032` certificate issued alongside |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-036-S1` | Handset graded B, battery 88%, 3 defects | Base bilingual record and disclosure |
| `DT-036-S2` | Grade F laptop with two feature limitations | Limitation disclosure |
| `DT-036-S3` | Harvested display fitted | `FM-36-c` origin disclosure |
| `DT-036-S4` | Grade overridden upward from C to B | `FM-36-e` justification and second approver |
| `DT-036-S5` | Listing feed compared to the record | `L-36-f` parity |
| `DT-036-S6` | Return upheld, unit re-graded | `GI-05` review path |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Refurbishment with Quality | 2026-08-15 | Draft issue |
| Reviewer — Quality (grade thresholds) | *pending* | | |
| Reviewer — Commercial | *pending* | | |
| Reviewer — Data Services (`DT-034` linkage) | *pending* | | |
| **Legal Counsel — disclosure statement and RF1–RF5** | *pending* | | **Required** |
| Approver — COO with Legal Counsel | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `RGC-{entity}-{yy}-{seq:06d}` |
| Gap policy | `gaps_recorded` |
| Archive format | **PDF/A-3 at issue** — it is the evidence in a return or a consumer complaint |
| Retention | `LG-009`; **warranty term plus the limitation period** |
| Grade-definition versioning | Every version retained while any unit sold under it remains within its warranty and limitation period (`GR-05`) |
| Re-render | **Prohibited.** Grade definitions change; the buyer's record must remain as issued |
| Reprint | Watermarked **COPY**, logged |
| Buyer access | The record is available to the buyer by QR and in `P01` for the retention period |
| Photographs | Retained with the record at the resolution assessed |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-034_Data_Destruction_Certificate.md`](DT-034_Data_Destruction_Certificate.md) | **Prerequisite (`BRU-TRF-01`)** |
| [`DT-038_TradeIn_Offer_and_Acceptance_Record.md`](DT-038_TradeIn_Offer_and_Acceptance_Record.md) | Where most units originate |
| [`DT-032_Warranty_Certificate_and_Extension_Document.md`](DT-032_Warranty_Certificate_and_Extension_Document.md) | Warranty offered on the unit |
| [`DT-035_EWaste_Disposal_and_Material_Recovery_Certificate.md`](DT-035_EWaste_Disposal_and_Material_Recovery_Certificate.md) | Where a unit is not viable |
| [`../05A_Service_and_Operations/DT-008_Quality_Checklist_Record.md`](../05A_Service_and_Operations/DT-008_Quality_Checklist_Record.md) | The QA protocol |
| [`../05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md`](../05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md) | §6.1 condition enumeration reused for cosmetic assessment |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md) | Grade definitions and model data |
| `LG-013` Service Terms, Warranty Terms and Exclusions | The full consumer terms |
| `UI-017` P07 Marketplace Seller Portal UI Copy Pack | Listing presentation |
| [`SP-025_SOP_TradeIn_Refurbishment_and_Resale.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-025_SOP_TradeIn_Refurbishment_and_Resale.md) | The operational process |
| `RP-002` Report Catalogue by Role and Module | `GI-01`…`GI-03` reporting |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Five-grade definition with indicative thresholds flagged for ratification, grade-assigned-by-protocol rule, numbered defect disclosure, battery health as a figure, listing-parity rule, five grade-integrity controls | COO with Legal Counsel (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Grade definitions stated in one place, versioned, with thresholds marked as requiring ratification
- [x] Grade assigned by protocol, not by the lister (`GR-02`)
- [x] Defects numbered and battery health stated as a figure
- [x] Listing-parity rule stated (`L-36-f`)
- [x] All internal links resolve
- [ ] **Grade thresholds ratified by Quality and Commercial (`GR-01`)** — **outstanding; blocks first use**
- [ ] G6 RF1–RF5 answered by Legal — **outstanding**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Grade definitions published in `MD-021` and version-controlled — **outstanding, dependency**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
