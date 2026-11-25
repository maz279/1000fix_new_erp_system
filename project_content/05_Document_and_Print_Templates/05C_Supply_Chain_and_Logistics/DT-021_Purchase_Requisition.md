---
id: DT-021
title: Purchase Requisition
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Procurement
author: Procurement with Finance and Content Design
reviewers: [Finance, Internal Audit, Inventory, Platform Engineering]
approver: Chief Financial Officer
content_class: C
purpose: >
  The internal request format carrying justification, budget reference and the approval chain.
  The audit trail for spend authorisation begins here, not at the purchase order — a PO with no
  requisition behind it is a commitment nobody asked for, and it is the point at which
  unbudgeted spend enters an organisation.
traces_to: [M16, M54, M43, M15, DT-001, DT-022, DT-023, MD-019, MD-022, MD-026, MD-036, MD-040, BRU-INV-03, BRU-SCM-02, BRU-ADM-01]
priority: P2
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/00_Content_Governance_and_Standards/CG-010 Bilingual Content Policy §3.2 — vendor- and B2B-facing procurement documents remain English
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-INV-03 — a purchase order cannot be raised for an item whose network-wide stock already exceeds the maximum level
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SCM-03 — the same user cannot create a vendor and approve that vendor's invoice
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-021 — Purchase Requisition

> **The requisition is where "we need this" becomes "we are committing money".** Everything
> downstream — the RFQ, the order, the receipt, the payment — inherits its justification, its
> budget line and its approval from this document.
>
> **English only** (`CG-010` §3.2). It is an internal and procurement-facing document in a
> function that operates in English with suppliers.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Internal spend request |
| Owning module | `M16` Procurement and Strategic Sourcing |
| Statutory | No |
| Recipient(s) | Budget holder, approver chain, procurement, internal audit |
| Languages | **English only** (`CG-010` §3.2) |
| Output formats | A4 portrait · PDF · primarily a **screen artefact**; printed for audit and offline approval |
| Numbering mask | `MD-040` — `PR-{entity}-{yy}-{seq:06d}` |
| Retention period | `LG-009`; retained with the PO and payment it leads to |

### 1.1 What a requisition must answer

| Question | Field |
|---|---|
| What is being bought? | Line items, from `MD-019` / `MD-022` where catalogued |
| Why? | Justification, mandatory, free text plus a `MD-026` category |
| Who wants it? | Requester, cost centre, site |
| Who pays? | Budget line, `MD-036` cost centre and dimension |
| Is there budget? | Available-budget check at submission (`M54`) |
| Is it already in stock? | Network-wide stock position at submission (`M15`) |
| When is it needed? | Required-by date, and the consequence of missing it |
| Who approved? | The chain, with names, roles and timestamps |

---

## 2. Statutory Requirements

Not statutory. Two governance constraints:

| Constraint | Source | Effect |
|---|---|---|
| Segregation of duties | `BRU-SCM-03`, `BRU-SEC-07` | The requester, the approver and the receiver cannot be the same person |
| Traceable change authorisation | `BRU-ADM-01` | An approved requisition that is subsequently amended requires re-approval, and the change is logged |

---

## 3. Layout

| Zone | Content |
|---|---|
| Header | Requisition number, date, requester, urgency |
| Party block | Requester, cost centre and site left; approval status and required-by date right |
| Body | Line items → justification → stock and budget position → attachments |
| Totals | Estimated value, by line and in total, with the budget impact |
| Statutory block | Not used. The **approval chain** occupies this zone |
| Signature | Approval chain — name, role, decision, timestamp per level |
| Footer | Requisition reference, `page n of m`, **INTERNAL** |

| # | Rule |
|---|---|
| **L-21-a** | The approval chain prints **in full**, including levels not yet reached, so a reader can see where the request stands |
| **L-21-b** | Justification is never truncated in print. A justification that does not fit is a justification that will be questioned |
| **L-21-c** | The stock and budget position **as at submission** prints, with its timestamp. Both move; the decision was made against a specific state |
| **L-21-d** | Marked **INTERNAL** in the footer of every page |

---

## 4. Field Mapping

| Label | Source field | Format | Required |
|---|---|---|:--:|
| Requisition no. | `MD-040` sequence | Monospace | ✔ |
| Raised date | `requisition.created_at` | `DD/MM/YYYY` | ✔ |
| Requester | `employee.display_name` + ID | Text | ✔ |
| Department / site | `MD-008`, `MD-003` | Text | ✔ |
| Cost centre | `MD-036.cost_centre_code` | Monospace | ✔ |
| Budget line | `M54.budget_line_ref` | Monospace | ✔ |
| Budget available at submission | `M54` | BDT, 2 dp | ✔ |
| Urgency | `requisition.urgency` | Enum: routine / expedited / emergency | ✔ |
| Required by | `requisition.required_by` | `DD/MM/YYYY` | ✔ |
| Consequence if late | `requisition.impact_note` | Text | ✔ **for expedited and emergency** |
| Item code | `MD-022.part_code` / `MD-019.item_code` | Monospace | ✔ where catalogued |
| Non-catalogue description | `requisition.line.description` | Text | ✔ where not catalogued |
| Quantity / unit | `requisition.line.qty`, `MD-023` | Number + UoM | ✔ |
| Estimated unit price | `MD-029` or last purchase price | BDT, 2 dp | ✔ |
| Estimated line value | Computed | BDT, 2 dp | ✔ |
| Network stock on hand | `M15` at submission | Number | ✔ for stock items |
| Stock at maximum level | `M15` flag | Bool | ✔ **`BRU-INV-03`** |
| Preferred supplier | `MD-016.vendor_code` | Monospace | Where stated |
| Preference justification | Text | Text | **✔ where a supplier is named** |
| Justification | `requisition.justification` | Free text | ✔ |
| Justification category | `MD-026.reason_code` | Code + label | ✔ |
| Attachments | `M24` references | List | Where held |
| Approval level / approver / decision / timestamp | `M63` workflow | Table | ✔ |

| # | Rule |
|---|---|
| **FM-21-a** | A named preferred supplier requires a justification. Naming a supplier at requisition stage pre-empts the RFQ and is the most common route to a single-source purchase nobody chose |
| **FM-21-b** | `BRU-INV-03` blocks a PO where network-wide stock exceeds maximum. The requisition **shows the position** so the requester sees it before submitting, not after rejection |
| **FM-21-c** | Emergency urgency requires an impact statement and escalates the approval level. Urgency without consequence is preference |
| **FM-21-d** | Non-catalogue lines are permitted but flagged. A rising non-catalogue rate is a catalogue-maintenance problem (`MD-022`), reported monthly |
| **FM-21-e** | Amending an approved requisition resets the approval chain from the level at which the change becomes material (`BRU-ADM-01`) |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-INV-03` | Stock-above-maximum position displayed and carried to the PO gate |
| `BRU-SCM-02` | A PO cannot be issued to an inactive or unapproved vendor — a preferred supplier who is not approved is flagged here |
| `BRU-SCM-03` | Segregation of duties across requisition, approval and receipt |
| `BRU-ADM-01` | Material change requires re-approval |
| `BRU-SEC-07` | Incompatible duty combinations blocked |
| `BRU-INV-05` | Expired shelf-life stock cannot be issued — relevant where a requisition is raised because on-hand stock is expired, and the reason should say so |

### 5.1 The approval matrix

Thresholds are held in `M63` workflow configuration, not in this document. What this document
guarantees is that the matrix is **visible on the artefact**.

| # | Rule |
|---|---|
| **AP-21-a** | Every level in the applicable chain prints, with its threshold basis |
| **AP-21-b** | An approver may approve, reject or return with a comment. **Return-with-comment is a distinct outcome** and prints as such — a rejected requisition and a returned one have different meanings |
| **AP-21-c** | Delegation prints as delegation, naming both the delegate and the principal (`NT-022`) |
| **AP-21-d** | Approval timestamps are recorded and printed. An approval chain with no times cannot be audited for sequence |
| **AP-21-e** | An emergency purchase made before approval — which happens — is recorded as a **retrospective approval** with that status visible, never backdated |

> **AP-21-e is the honest rule.** Emergency purchases happen in a 51-branch operation. Pretending
> otherwise produces backdated approvals, which is a far worse audit finding than a recorded
> retrospective one.

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Standard** | Routine purchasing | The base document |
| **Emergency** | Operational stoppage risk | Impact statement mandatory; shortened chain, higher level; retrospective approval path (`AP-21-e`) |
| **Replenishment-generated** | `M43` demand planning proposes it | System-raised, with the forecast basis printed; still requires human approval |
| **Capital** | Fixed-asset purchase (`M49`) | Adds asset class, depreciation schedule (`MD-044`) and capital-budget line |
| **Service / contractor** | Non-goods purchase | Scope of work, duration and rate basis replace quantity and unit price |
| **Blanket / call-off** | Framework agreement | Total ceiling with call-off tracking; approval is on the ceiling, not per call-off |
| **Consignment replenishment** | Brand consignment stock (`BRU-INV-04`) | Zero value; approval is operational, not financial |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-021-S1` | Spare parts, catalogued, routine | Base rendition with stock and budget position |
| `DT-021-S2` | Emergency, retrospective approval | `AP-21-e` |
| `DT-021-S3` | Named preferred supplier | `FM-21-a` justification requirement |
| `DT-021-S4` | Item at maximum stock level | `BRU-INV-03` visibility |
| `DT-021-S5` | Capital purchase | Asset class and capital budget line |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Procurement with Finance | 2026-08-15 | Draft issue |
| Reviewer — Finance | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| Reviewer — Inventory | *pending* | | |
| Approver — Chief Financial Officer | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `PR-{entity}-{yy}-{seq:06d}` |
| Gap policy | `gaps_recorded` — a cancelled requisition retains its number with a reason |
| Archive format | Standard PDF; the `M16` record is the retained artefact |
| Retention | `LG-009`; **retained as long as the PO and payment it leads to**, because it is the authorisation evidence for that spend |
| Re-render | Permitted before approval; **prohibited after**, because the stock and budget position printed was a decision input |
| Reprint | Unwatermarked before approval; watermarked **COPY** after |
| Chain | Requisition → `DT-022` RFQ → `DT-023` PO → `DT-024` GRN → payment, retrievable as one file |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-022_Request_for_Quotation.md`](DT-022_Request_for_Quotation.md) | What an approved requisition becomes |
| [`DT-023_Purchase_Order.md`](DT-023_Purchase_Order.md) | The commitment this authorises |
| [`DT-024_Goods_Receipt_Note_and_Inspection_Record.md`](DT-024_Goods_Receipt_Note_and_Inspection_Record.md) | Closes the loop |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md) | Catalogued item source |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-036_Cost_Centre_Business_Line_and_Dimension_Register.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-036_Cost_Centre_Business_Line_and_Dimension_Register.md) | Cost centre and dimensions |
| [`NT-022_Approval_Request_and_Reminder_Library.md`](../../04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-022_Approval_Request_and_Reminder_Library.md) | The approval messages |
| [`SP-017_SOP_Procurement_to_Payment.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-017_SOP_Procurement_to_Payment.md) | How it is raised and approved |
| `UI-028` Workspace — Procurement Console Copy | The on-screen form |
| `RP-002` Report Catalogue by Role and Module | Non-catalogue rate and emergency-purchase reporting |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Eight-question content test, preferred-supplier justification rule, stock-and-budget-as-at-submission rule, five approval-matrix rules including recorded retrospective approval | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] English-only status justified against `CG-010` §3.2
- [x] Preferred-supplier justification required, with the reason stated
- [x] Retrospective approval handled honestly rather than by backdating
- [x] All internal links resolve
- [x] Bengali counterpart — n/a per `CG-010` §3.2
- [ ] Approval thresholds configured in `M63` and reconciled with `MD-036` — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
