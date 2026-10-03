---
id: DT-033
title: Warranty Claim Evidence Pack
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Warranty
author: Warranty with Technical, Finance and Content Design
reviewers: [Technical, Quality, Finance, Brand Partnerships, Internal Audit]
approver: Chief Operating Officer with Chief Financial Officer
content_class: C
purpose: >
  The assembled pack submitted to a brand partner — diagnosis, photographs, parts, technician
  certification and purchase proof. Claim approval-rate target is above 92% and decision time
  under 10 days; both depend on evidence completeness at submission, because an incomplete pack
  is not rejected, it is queued behind an information request that nobody chases.
traces_to: [M09, M31, M23, P08, DT-001, DT-004, DT-007, DT-008, DT-032, MD-011, MD-017, MD-022, MD-040, BRU-WTY-01, BRU-WTY-02, BRU-WTY-03, BRU-WTY-04, BRU-WTY-05, BRU-WTY-08, BRU-SRM-17]
priority: P1
wave: W4
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-WTY-01 — a warranty claim cannot be submitted without a completed work order, device serial, at least one before-photo, a technician diagnosis and the replaced-parts list
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-WTY-08 — a claim not submitted within the brand's stated window is escalated as revenue leakage before it expires
    verified: 2026-08-15
    class: P1
  - source: 1000FiX_ERP_Content_Master_Index CATEGORY 05 DT-033 — approval-rate target above 92%, decision time under 10 days
    verified: 2026-08-15
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-010 §3.2 — brand-facing claim documents remain English
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-033 — Warranty Claim Evidence Pack

> **A claim is money the company has already spent.** Parts were fitted, labour was performed,
> and the customer paid nothing. The claim is how that cost is recovered, and an incomplete pack
> is the difference between recovery and a write-off.
>
> **`BRU-WTY-01` defines the minimum.** This document defines what a **good** pack contains — the
> difference between the 92% approval target and the rate an ad-hoc submission achieves.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Assembled evidence pack for a brand warranty claim |
| Owning module | `M09` Warranty, Protection Plans and Claims, submitted via `P08` |
| Statutory | No — **contractually binding under the brand agreement** |
| Recipient(s) | Brand partner claims team, internal warranty officer, finance, audit |
| Languages | **English only** (`CG-010` §3.2) — brand partners are corporate counterparties |
| Output formats | `P08` portal submission (primary) · brand-specific portal or API (`M28`) · PDF pack · A4 print for brands requiring paper |
| Numbering mask | `MD-040` — `CLM-{entity}-{yy}-{seq:06d}` |
| Retention period | `LG-009`; **claim decision plus the brand agreement's audit window**, minimum the tax retention |

### 1.1 The pack

| # | Component | Source | `BRU-WTY-01` minimum | Good practice |
|---:|---|---|:--:|:--:|
| 1 | Claim header and summary | `M09` | ✔ | ✔ |
| 2 | Completed work order | `DT-007` | ✔ | ✔ |
| 3 | Device serial and identity | `M17` | ✔ | ✔ |
| 4 | **Before photographs** | `M24` | ✔ (≥1) | Multiple angles + fault detail |
| 5 | **After photographs** | `M24` | — | ✔ (`BRU-SRM-17`) |
| 6 | Technician diagnosis | `DT-004` | ✔ | With fault codes mapped to the brand's taxonomy |
| 7 | **Replaced-parts list with serials** | `DT-007` | ✔ | With defective-part return reference |
| 8 | Technician certification | `MD-011` | — | ✔ — brands check it |
| 9 | Purchase proof / warranty validation | `M17`, customer | — | ✔ — the most common rejection cause |
| 10 | Quality checklist | `DT-008` | — | ✔ where the brand requires it |
| 11 | Cost breakdown | `MD-029`, brand rate card | — | ✔ — in the agreed currency at the agreed rate |
| 12 | Defective part return evidence | `DT-025` / `DT-027` | — | ✔ where the brand requires return |

> **Components 8–12 are why a 92% approval rate is achievable.** The `BRU-WTY-01` minimum gets a
> claim submitted. The full pack gets it approved without an information request.

---

## 2. Statutory Requirements

Not statutory. Four contractual constraints, all from the brand agreements in `MD-017`:

| Constraint | Source | Effect |
|---|---|---|
| Submission window | Brand agreement; `BRU-WTY-08` | A claim submitted late is a claim not paid |
| Evidence specification | Brand agreement | Each brand's requirements differ and are held in `MD-017` |
| Authorised technician requirement | Brand agreement; `BRU-SRM-09` | Work by an uncertified technician voids the claim |
| Defective-part return | Brand agreement | Some brands require the part back before approval |

---

## 3. Layout

**Pack, not page.** Component 1 is a cover summary; the rest are attachments in a fixed order.

| Zone | Content |
|---|---|
| Header | Claim number, brand, brand claim reference, submission date, submission window remaining |
| Party block | Brand and their claims contact left; our entity, authorised service centre code and warranty officer right |
| Body | Claim summary → device and warranty validation → fault and diagnosis → work performed → parts → cost → evidence index |
| Totals | Claimed value by component: parts, labour, transport, in the agreed currency |
| Statutory block | Not used. The **completeness declaration** occupies this zone |
| Signature | Warranty officer; technician certification reference |
| Footer | Claim reference, `page n of m`, evidence-index item count |

| # | Rule |
|---|---|
| **L-33-a** | The **evidence index** lists every attachment with its type and a checksum or reference. A pack that loses an attachment in transmission must be detectable as incomplete |
| **L-33-b** | Component order is fixed across all claims and all brands. Claims assessors process volume; a predictable pack is assessed faster |
| **L-33-c** | The **submission window remaining** prints on the cover. It is the field that prevents `BRU-WTY-08` leakage |
| **L-33-d** | Brand-specific fault codes print alongside ours where `MD-017` holds a mapping |
| **L-33-e** | Photographs are embedded at a resolution the brand can assess. A compressed thumbnail is not evidence of a hairline crack |

---

## 4. Field Mapping

### 4.1 Claim header

| Label | Source field | Format | Required |
|---|---|---|:--:|
| Claim no. | `MD-040` sequence | Monospace | ✔ |
| Brand | `MD-017.brand_name` | Text | ✔ |
| Brand claim reference | `claim.brand_ref` | Monospace | Once issued |
| Authorised service centre code | `MD-017.asc_code` | Monospace | ✔ |
| Submission date | `claim.submitted_at` | `DD/MM/YYYY` | ✔ |
| Service completion date | `DT-007` date | `DD/MM/YYYY` | ✔ |
| **Days to window expiry** | Computed from `MD-017.claim_window` | Integer | ✔ **`BRU-WTY-08`** |
| Warranty officer | `employee.display_name` + ID | Text | ✔ |

### 4.2 Device, fault and work

| Label | Source field | Format | Required |
|---|---|---|:--:|
| Device make / model | `MD-021` | Text | ✔ |
| **Serial / IMEI** | `device.serial_no` | Monospace | ✔ |
| Date of purchase | `M17.purchase_date` | `DD/MM/YYYY` | ✔ |
| Purchase proof type | `claim.purchase_proof_type` | Enum: invoice / warranty card / brand registry | ✔ |
| Warranty valid at service date | Computed | Bool | ✔ **`BRU-SRM-02`** |
| Service order no. | `service_order.order_ref` | Monospace | ✔ |
| Reported fault | `DT-002` | Text | ✔ |
| **Diagnosis** | `DT-004` findings | Text + codes | ✔ |
| Our fault code | `MD-024` | Code | ✔ |
| **Brand fault code** | `MD-017` mapping | Code | ✔ where mapped |
| Cause category | `DT-004.cause_category` | Enum | ✔ **determines eligibility** |
| Work performed | `DT-007` actions | Text + codes | ✔ |
| Technician | `employee.display_name` + ID | Text | ✔ |
| **Technician certification** | `MD-011.certification_code` + validity | Code + date | ✔ **`BRU-SRM-09`** |
| Repair level | `service_order.repair_level` | Enum | ✔ |
| Quality checklist reference | `DT-008` | Monospace | ✔ where required |

### 4.3 Parts, cost and evidence

| Label | Source field | Format | Required |
|---|---|---|:--:|
| Part fitted — our code | `MD-022.part_code` | Monospace | ✔ |
| Part fitted — **brand part number** | `MD-022.brand_part_no` | Monospace | ✔ |
| Quantity | `stock_issue.qty` | Number | ✔ |
| New part serial | `stock_issue.serial_no` | Monospace | ✔ serialised |
| **Removed part serial** | `stock_return.serial_no` | Monospace | ✔ serialised |
| Part source | `stock_issue.part_origin` | Enum: brand-supplied / own stock / purchased | ✔ **`BRU-WTY-04`** |
| Defective part returned | `DT-025` / `DT-027` reference | Monospace | ✔ where required |
| Parts value | Brand rate card | Currency, 2 dp | ✔ |
| Labour value | Brand rate card | Currency, 2 dp | ✔ |
| Transport value | Brand rate card | Currency, 2 dp | Where claimable |
| **Total claimed** | Computed | Currency, 2 dp | ✔ |
| Currency and rate | `MD-039`, `BRU-WTY-05` | Code + rate + date | ✔ |
| Before photo count | `M24` | Integer | ✔ **≥1 (`BRU-WTY-01`)** |
| After photo count | `M24` | Integer | ✔ (`BRU-SRM-17`) |
| Evidence index | `M24` references | Table | ✔ |
| Duplicate check | `BRU-WTY-03` result | Pass/blocked | ✔ |

| # | Rule |
|---|---|
| **FM-33-a** | The claim is **valued in the agreed currency at the rate prevailing on the service completion date** (`BRU-WTY-05`), not at submission or settlement |
| **FM-33-b** | Brand-supplied warranty parts cannot appear on a non-warranty job (`BRU-WTY-04`); conversely a claim using own-stock parts states so, because reimbursement differs |
| **FM-33-c** | A duplicate claim for the same serial and fault within 90 days is blocked before submission (`BRU-WTY-03`) |
| **FM-33-d** | Technician certification validity is checked **at the service date**, not at submission. A certification that lapsed afterwards does not invalidate the work |
| **FM-33-e** | Purchase proof is the most common rejection cause. Where it is weak, the claim is flagged **before** submission so it can be strengthened rather than rejected |
| **FM-33-f** | Every claim is auto-created within 24 hours of a warranty work order closing (`BRU-WTY-02`); this document is assembled from that record, not built from scratch |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-WTY-01` | The five mandatory components; submission blocked without them |
| `BRU-WTY-02` | Auto-creation within 24 hours of closure |
| `BRU-WTY-03` | Duplicate blocking on serial + fault within 90 days |
| `BRU-WTY-04` | Brand-part consumption restricted to warranty jobs |
| `BRU-WTY-05` | Currency valuation at completion date |
| `BRU-WTY-08` | Unsubmitted claims escalate as revenue leakage before the window expires |
| `BRU-SRM-02` | Warranty-type orders require active warranty at the service request date |
| `BRU-SRM-09` | Certification requirement for brand warranty work |
| `BRU-SRM-17` | Before/after photographs mandatory on warranty jobs |

### 5.1 Achieving the 92% approval rate

| # | Control |
|---|---|
| **AR-33-a** | **Completeness is checked before submission, not after rejection.** The pack cannot submit with a missing mandatory component |
| **AR-33-b** | Brand-specific requirements from `MD-017` are applied as a pre-submission checklist per brand |
| **AR-33-c** | Weak purchase proof is flagged pre-submission (`FM-33-e`) |
| **AR-33-d** | Rejection reasons are coded and analysed **by brand and by cause**. A rejection cause appearing repeatedly is a process defect, not bad luck |
| **AR-33-e** | An information request from a brand is treated as a **near-miss**: the pack should have contained it, and the checklist is updated |
| **AR-33-f** | Approval rate and decision time are reported per brand. A brand with a structurally lower rate needs a conversation, not more submissions |
| **AR-33-g** | Claims approaching the window expiry escalate daily, not weekly (`BRU-WTY-08`) |

> **AR-33-e is the compounding one.** Every information request that changes the checklist stops
> a class of future requests. Treating them as routine correspondence keeps the rate where it is.

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Standard brand claim** | Authorised warranty repair | The full pack |
| **Brand-portal submission** | Brand has its own portal | Same content, mapped to their fields (`M28`); our pack is retained as the record of what was submitted |
| **API submission** | Integrated brand (`05-03`) | Structured payload; the PDF pack is generated and archived regardless |
| **Bulk / batch claim** | Periodic settlement brands | Multiple claims with one cover summary; each claim complete in itself |
| **Resubmission** | After an information request | References the original claim, states what was added, retains the original |
| **Goodwill / out-of-warranty request** | Brand goodwill outside strict cover | Marked as such; approval basis is discretionary and tracked separately |
| **Consignment-stock claim** | Repair using brand consignment stock | Part reimbursement differs; `BRU-INV-04` valuation treatment stated |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-033-S1` | Handset main-board replacement, complete pack | All 12 components, evidence index |
| `DT-033-S2` | `BRU-WTY-01` minimum only | The difference from a good pack |
| `DT-033-S3` | Weak purchase proof flagged pre-submission | `FM-33-e` and `AR-33-c` |
| `DT-033-S4` | Duplicate blocked | `BRU-WTY-03` |
| `DT-033-S5` | Resubmission after an information request | `AR-33-e` checklist update |
| `DT-033-S6` | Claim 3 days from window expiry | `AR-33-g` escalation |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Warranty with Technical and Finance | 2026-08-15 | Draft issue |
| Reviewer — Technical | *pending* | | |
| Reviewer — Quality | *pending* | | |
| Reviewer — Brand Partnerships | *pending* | | |
| Reviewer — Finance | *pending* | | |
| Approver — COO with CFO | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `CLM-{entity}-{yy}-{seq:06d}`; resubmissions suffix `/R{n}` |
| Gap policy | `gaps_recorded`; a blocked or abandoned claim retains its number with a reason |
| Archive format | **PDF/A-3 of the pack as submitted**, plus the structured payload where an API was used |
| Retention | `LG-009`; **decision plus the brand agreement's audit window**, minimum the tax retention. Brand partners audit historic claims |
| Re-render | **Prohibited.** The pack as submitted is what the decision was made on |
| Reprint | Watermarked **COPY**, logged |
| Evidence artefacts | Photographs and documents retained in `M24` with the claim's retention, at the resolution submitted |
| Settlement linkage | Claim → decision → reconciliation → remittance, retrievable as one chain (`DT-017` brand variant) |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`../05A_Service_and_Operations/DT-004_Diagnostic_and_Condition_Report.md`](../05A_Service_and_Operations/DT-004_Diagnostic_and_Condition_Report.md) | The diagnosis component |
| [`../05A_Service_and_Operations/DT-007_Service_Completion_Report.md`](../05A_Service_and_Operations/DT-007_Service_Completion_Report.md) | The work order and parts components |
| [`../05A_Service_and_Operations/DT-008_Quality_Checklist_Record.md`](../05A_Service_and_Operations/DT-008_Quality_Checklist_Record.md) | Where the brand requires QC evidence |
| [`DT-032_Warranty_Certificate_and_Extension_Document.md`](DT-032_Warranty_Certificate_and_Extension_Document.md) | Our own warranty obligations — a different thing |
| [`../05C_Supply_Chain_and_Logistics/DT-025_Return_to_Vendor_and_Debit_Advice.md`](../05C_Supply_Chain_and_Logistics/DT-025_Return_to_Vendor_and_Debit_Advice.md) | Defective-part return where required |
| [`../05B_Finance_and_Statutory/DT-017_Customer_Statement_of_Account.md`](../05B_Finance_and_Statutory/DT-017_Customer_Statement_of_Account.md) | Brand reconciliation variant |
| [`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md) | Per-brand requirements, windows, rate cards and code mappings |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md) | Technician certification |
| `UI-018` P08 Brand Partner Portal UI Copy Pack | The submission experience |
| [`NT-013_Email_Template_Library_Brand_Partner_Claims.md`](../../04_Notification_and_Messaging/04C_Email/NT-013_Email_Template_Library_Brand_Partner_Claims.md) | Submission, information request and decision messages |
| [`SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md) | How a pack is assembled |
| `RP-002` Report Catalogue by Role and Module | Approval rate, decision time and rejection-cause reporting |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Twelve-component pack distinguishing the `BRU-WTY-01` minimum from a good pack, evidence index with integrity references, seven approval-rate controls including near-miss handling of information requests, window-expiry escalation | COO with CFO (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Minimum versus good pack distinguished explicitly
- [x] Evidence index required with integrity references (`L-33-a`)
- [x] Approval-rate controls tied to the stated 92% target
- [x] Currency valuation rule bound to `BRU-WTY-05`
- [x] All internal links resolve
- [x] Bengali counterpart — n/a per `CG-010` §3.2
- [ ] Per-brand requirements, windows, rate cards and fault-code mappings populated in `MD-017` — **outstanding, dependency for all 17+ brands**
- [ ] Brand portal and API mappings specified with `M28` — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
