---
id: DT-022
title: Request for Quotation
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Procurement
author: Procurement with Content Design
reviewers: [Finance, Legal & Compliance, Technical, Internal Audit, Vendor Management]
approver: Chief Financial Officer
content_class: C
purpose: >
  The RFQ issued through the vendor portal P05 with specification, quantity, terms and response
  deadline. The RFQ response-rate target is above 75%, and response quality depends entirely on
  request clarity — an ambiguous RFQ produces incomparable quotations, which produces a decision
  made on price alone because nothing else can be compared.
traces_to: [M16, M42, P05, DT-001, DT-021, DT-023, MD-016, MD-019, MD-022, MD-023, MD-040, BRU-SCM-02, BRU-SCM-03]
priority: P2
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000FiX_ERP_Content_Master_Index CATEGORY 05 DT-022 — RFQ response-rate target above 75%
    verified: 2026-08-15
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-010 §3.2 — vendor-facing procurement documents remain English
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SCM-02 — a purchase order cannot be issued to a vendor who is not active and approved
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-022 — Request for Quotation

> **An RFQ is a specification, not a shopping list.** The response-rate target above 75% and the
> comparability of what comes back are both determined here.
>
> Two failures dominate: a specification so loose that suppliers quote different things, and a
> specification so tight that only one supplier can meet it. The first makes comparison
> impossible; the second makes competition impossible. §5.1 addresses both.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Request for quotation issued to suppliers |
| Owning module | `M16` Procurement, issued through `P05` Vendor Portal |
| Statutory | No |
| Recipient(s) | Invited suppliers, procurement file, internal audit |
| Languages | **English only** (`CG-010` §3.2) |
| Output formats | `P05` portal (primary) · PDF for email · A4 portrait |
| Numbering mask | `MD-040` — `RFQ-{entity}-{yy}-{seq:06d}` |
| Retention period | `LG-009`; retained with the resulting PO, and with the award decision |

### 1.1 What makes an RFQ answerable

| Element | Without it |
|---|---|
| Unambiguous specification | Suppliers quote different products |
| Quantity and unit | Prices cannot be compared |
| Delivery location and date | Freight and lead time are guessed |
| Payment and VDS terms | Quoted prices are not comparable net of tax |
| Response deadline and format | Late and unstructured responses |
| Award criteria | Suppliers optimise the wrong variable |
| Named contact for clarification | Suppliers guess rather than ask |
| Validity requirement | A quote that expires before award is useless |

---

## 2. Statutory Requirements

Not statutory. Four constraints:

| Constraint | Source | Effect |
|---|---|---|
| No commitment | Contract law | An RFQ is an invitation to treat and states so; a PO is the commitment |
| Confidentiality | `LG-006` supplier code of conduct | Specifications may disclose commercially sensitive detail; the RFQ states the confidentiality obligation |
| Equal treatment | Procurement governance | Every invited supplier receives the same information at the same time, including clarifications |
| VDS disclosure | `MD-037`, `DT-013` | Where we will withhold VAT at source, the RFQ says so, so quotes are comparable |

---

## 3. Layout

| Zone | Content |
|---|---|
| Header | RFQ number, issue date, **response deadline** in the largest header type |
| Party block | Supplier and contact left; buyer contact, entity and delivery location right |
| Body | Scope → line specification → terms → award criteria → response instructions |
| Totals | Not used. Suppliers supply the numbers |
| Statutory block | Not used. The **conditions of the RFQ** occupy this zone |
| Signature | Issuing officer |
| Footer | RFQ reference, `page n of m`, clarification contact |

| # | Rule |
|---|---|
| **L-22-a** | The **response deadline** — date, time and time zone — is the most prominent element after the RFQ number |
| **L-22-b** | Each line carries a full specification, not a catalogue code alone. A supplier does not hold our catalogue |
| **L-22-c** | A **response template** accompanies the RFQ — the structure the supplier fills in. Free-format responses cannot be compared |
| **L-22-d** | Award criteria print. A supplier who does not know how they will be judged optimises for price |
| **L-22-e** | The conditions block states clearly that the RFQ is not an order |

---

## 4. Field Mapping

| Label | Source field | Format | Required |
|---|---|---|:--:|
| RFQ no. | `MD-040` sequence | Monospace | ✔ |
| Issue date | `rfq.issued_at` | `DD/MM/YYYY` | ✔ |
| **Response deadline** | `rfq.response_deadline` | `DD/MM/YYYY HH:mm` + time zone | ✔ |
| Requisition reference | `DT-021` reference | Monospace | ✔ (internal copy only) |
| Supplier name and code | `MD-016.vendor_name`, `.vendor_code` | Text + monospace | ✔ |
| Supplier contact | `MD-016.contact_name`, email | Text | ✔ |
| Buyer contact | `employee.display_name` + email + phone | Text | ✔ |
| Delivery location | `MD-003` / `MD-004` | Text + address | ✔ |
| Required delivery date | `rfq.required_by` | `DD/MM/YYYY` | ✔ |
| Line no. | Computed | Integer | ✔ |
| Item specification | `MD-022.part_spec` or free text | Text | ✔ |
| Manufacturer part number | `MD-022.mpn` | Monospace | Where applicable |
| Acceptable equivalents | `rfq.line.equivalents_allowed` | Bool + criteria | ✔ |
| Quantity / unit | `rfq.line.qty`, `MD-023` | Number + UoM | ✔ |
| Quality / certification requirement | `rfq.line.quality_req` | Text | Where applicable |
| Warranty requirement | `rfq.line.warranty_req` | Text | ✔ |
| Payment terms offered | `MD-038.payment_term_code` | Label | ✔ |
| **VDS applicable** | `MD-037` VDS position | Bool + rate | ✔ **where we will withhold** |
| Incoterms / delivery basis | `rfq.delivery_basis` | Enum | ✔ |
| Quote validity required | `rfq.validity_days` | Days | ✔ |
| Award criteria | `rfq.award_criteria` | Weighted list | ✔ |
| Clarification deadline | `rfq.clarification_deadline` | `DD/MM/YYYY` | ✔ |
| Conditions | Static approved text | Text | ✔ |

| # | Rule |
|---|---|
| **FM-22-a** | Where an equivalent is acceptable, the RFQ says so **and states the equivalence criteria**. "Or equivalent" with no criteria produces unusable substitutions |
| **FM-22-b** | The VDS position is disclosed. A supplier quoting without knowing we withhold has quoted a different net price from one who knows |
| **FM-22-c** | Award criteria are weighted and printed. Where price is the sole criterion, that is stated plainly |
| **FM-22-d** | Clarifications and their answers are **circulated to every invited supplier**, not only to the one who asked |
| **FM-22-e** | Only active, approved suppliers are invited (`BRU-SCM-02`). Inviting a supplier who cannot receive a PO wastes their time and ours |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-SCM-02` | Invitation restricted to active, approved vendors |
| `BRU-SCM-03` | The person issuing the RFQ cannot also approve the resulting invoice |
| `BRU-INV-03` | An RFQ for an item already above maximum stock requires the `DT-021` override to have been approved first |
| `BRU-ADM-01` | A material change to an issued RFQ is an **amendment**, circulated to all invited suppliers with a revised deadline |

### 5.1 Specification discipline

| # | Rule |
|---|---|
| **SD-22-a** | A specification that only one supplier can meet requires a recorded **single-source justification**, approved a level above the normal threshold |
| **SD-22-b** | Manufacturer part numbers may be used for identification, with equivalents permitted unless a recorded technical reason prohibits them |
| **SD-22-c** | Brand-mandated parts for authorised warranty work are a legitimate single-source case (`BRU-WTY-04`) and are recorded as such, not disguised as open competition |
| **SD-22-d** | A minimum of three invitations for non-single-source purchases above the threshold; fewer requires a recorded reason |
| **SD-22-e** | Specifications are reviewed by Technical where the item affects repair quality. Procurement does not set technical specifications alone |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Standard RFQ** | Goods, catalogued or specified | The base document |
| **Technical RFQ** | Equipment, tooling, test instruments (`MD-046`) | Extended specification, evaluation and acceptance-test criteria |
| **Services RFQ** | Contractors, facilities, logistics | Scope of work, service levels, personnel qualifications, rate basis |
| **Framework / blanket** | Multi-period supply | Ceiling volume, price-hold period and call-off mechanics |
| **Urgent** | Emergency requisition | Compressed deadline, stated as such; still circulated to all invitees |
| **Reverse auction** | Where `M16` supports it | Rules of the auction and its close time replace a single deadline |
| **Amendment** | Material change to an issued RFQ | Marked **AMENDMENT n**, states what changed, revises the deadline |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-022-S1` | Spare parts, 4 suppliers invited | Base rendition and response template |
| `DT-022-S2` | Single-source brand part | `SD-22-c` recorded justification |
| `DT-022-S3` | VDS-applicable service purchase | `FM-22-b` disclosure |
| `DT-022-S4` | Amendment after a clarification | `BRU-ADM-01` handling and deadline revision |
| `DT-022-S5` | Technical RFQ with acceptance tests | Technical variant |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Procurement | 2026-08-15 | Draft issue |
| Reviewer — Technical | *pending* | | |
| Reviewer — Legal & Compliance (conditions text) | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| Approver — Chief Financial Officer | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `RFQ-{entity}-{yy}-{seq:06d}`; amendments suffix `/A{n}` |
| Gap policy | `gaps_recorded` |
| Archive format | Standard PDF, with the response set and the award decision |
| Retention | `LG-009`; **the RFQ, all responses and the award rationale are retained together** — an award decision without the alternatives it was chosen over is not auditable |
| Re-render | Prohibited after issue |
| Reprint | Watermarked **COPY** |
| Response confidentiality | Supplier responses are visible only to the evaluation team until award (`BRU-SEC-05`) |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-021_Purchase_Requisition.md`](DT-021_Purchase_Requisition.md) | The authorisation behind it |
| [`DT-023_Purchase_Order.md`](DT-023_Purchase_Order.md) | The commitment that follows an award |
| [`DT-024_Goods_Receipt_Note_and_Inspection_Record.md`](DT-024_Goods_Receipt_Note_and_Inspection_Record.md) | Where the specification is tested against what arrived |
| [`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md) | Who may be invited |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md) | Specifications and part numbers |
| `EO-005` Vendor and Supplier Onboarding Pack | How a supplier becomes eligible to be invited |
| [`NT-011_Email_Template_Library_Vendor_and_Supplier.md`](../../04_Notification_and_Messaging/04C_Email/NT-011_Email_Template_Library_Vendor_and_Supplier.md) | RFQ issue and reminder emails |
| [`SP-017_SOP_Procurement_to_Payment.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-017_SOP_Procurement_to_Payment.md) | The sourcing process |
| `UI-015` P05 Vendor and Supplier Portal UI Copy Pack | The supplier-side experience |
| `RP-002` Report Catalogue by Role and Module | Response-rate reporting against the 75% target |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Eight-element answerability test, mandatory response template, VDS disclosure rule, clarification-to-all rule, five specification-discipline rules | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Response template made mandatory, with the comparability reason stated
- [x] Single-source and equivalence handled explicitly (`SD-22-a`…`SD-22-c`)
- [x] VDS disclosure required so quotes are comparable
- [x] All internal links resolve
- [x] Bengali counterpart — n/a per `CG-010` §3.2
- [ ] Conditions-of-RFQ text drafted and legally reviewed — **outstanding**
- [ ] Award-criteria weighting framework agreed with Finance and Technical — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
