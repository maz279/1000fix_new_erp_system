---
id: DT-020
title: Consolidated Corporate Invoice
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance with Account Management
author: Finance with Account Management, Tax and Content Design
reviewers: [External tax adviser, Tax, Legal & Compliance, Account Management, Internal Audit, Localisation Lead]
approver: Chief Financial Officer
content_class: A
statutory_tier: S
statutory_pin: FY2026-27
purpose: >
  Multi-site, multi-department, multi-asset billing for corporate accounts, with an itemised
  breakdown and the approval trail. P04 commits to consolidated invoices itemised by site,
  department and asset, and to an invoice-dispute rate below 3%. Both commitments are met or
  missed in this document's structure, and it must simultaneously satisfy the Mushak 6.3
  obligation on every underlying supply.
traces_to: [M20, M08, M51, M19, P04, DT-001, DT-010, DT-011, DT-015, DT-017, DT-031, MD-015, MD-036, MD-037, MD-040, BRU-BIL-07, BRU-CTR-02, BRU-CTR-04, BRU-CTR-08, 04-00 §P04]
priority: P1
wave: W4
bilingual: yes
bn_counterpart: DT-020_Consolidated_Corporate_Invoice_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P04 — consolidated invoices with itemised breakdown by site, department and asset; invoice-dispute rate below 3%
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-BIL-07 — a consolidated corporate invoice cannot be issued until every constituent job is Completed and priced
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-CTR-02 and BRU-CTR-04 — out-of-scope work billed separately; entitlement over-consumption never invisible
    verified: 2026-08-15
    class: P1
  - source: project_content/05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-010 — the Mushak 6.3 obligation this document must satisfy
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-020 — Consolidated Corporate Invoice

> ⚠ **Tier S — it must be, or must be accompanied by, conforming Mushak 6.3 challans. Gate G6
> mandatory and unwaivable (`WV-02`).**
>
> **Two obligations meet here and they pull in opposite directions.** The tax instrument wants
> one challan per supply, in a prescribed form. The corporate customer wants one document a
> month, broken down by site, department and asset, that their AP team can approve in a single
> pass. **G6 CI1 decides how both are satisfied**, and the answer shapes `M20`'s billing design.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Consolidated period invoice for a corporate account |
| Owning module | `M20` Accounts Receivable, with `M08` Contract Lifecycle |
| Statutory | **Yes — Tier S.** Must satisfy the Mushak 6.3 obligation on every underlying supply |
| Recipient(s) | Corporate AP, account manager, procurement approver, auditor |
| Languages | **Bilingual — stacked labels**, English-dominant for corporate AP (`VB-002`) |
| Output formats | A4 portrait (summary) + A4 landscape (schedules) · PDF · `P04` portal · **structured export for AP ingestion** · PDF/A-3 archive |
| Numbering mask | `MD-040` — statutory sequence, `no_gaps`, per **entity + account** |
| Retention period | **At least 5 years** from the end of the tax period — confirmed at G6 |
| Fiscal pin | **FY2026-27** |

### 1.1 The structural requirement from `P04`

| Requirement | Consequence in this document |
|---|---|
| Itemised by **site** | Level-1 grouping; every line carries a site from `MD-015` |
| Itemised by **department** | Level-2 grouping; department from `MD-015` / `MD-036` |
| Itemised by **asset** | Every service line names the device or asset tag |
| **Dispute rate below 3%** | Drives the whole design: a line an approver cannot verify is a line they will query |
| Single approval pass | Summary first, detail after; sub-totals at every level the customer budgets at |

---

## 2. Statutory Requirements

The prescribed Mushak 6.3 elements (`DT-010` §2) apply to every underlying supply. This
document adds no elements of its own; it must **not remove any**.

| Obligation | Source | Verified | Effect |
|---|---|---|---|
| Every supply is evidenced by a conforming challan | VAT & SD Rules 2016 — **pending G6** | pending | Either this document is a compliant challan, or conforming challans accompany it |
| VAT presented by rate band | `MD-037`; `DT-010` FM-10-b | pending | Band subtotals at every grouping level |
| Buyer BIN present | `DT-010` FM-10-d | pending | Corporate buyers claim input VAT; omission is an immediate dispute |
| Gap-free statutory sequence | `SEQ-01` | 2026-08-15 | Whichever document carries the challan number |
| Adjustment by note only | `BRU-DMS-03`, `DT-015` | 2026-08-15 | A consolidated invoice is never edited after issue |

### 2.1 G6 questions

| # | Question |
|---|---|
| **CI1** | **May a single Mushak 6.3 cover multiple supplies to one buyer over a period, or must one challan issue per supply?** |
| **CI2** | If one per supply, may they be delivered as an annexure to a consolidated summary, and does the summary itself need a form? |
| **CI3** | Does a consolidated document change the tax point of the individual supplies? |
| **CI4** | How must credit notes against a consolidated invoice reference the underlying supplies? (paired with `DT-015` C5) |
| **CI5** | For a corporate group, may supplies to multiple legal entities appear on one invoice? (`MD-015` hierarchy) |

> **CI1 is the design question.** If one challan per supply is mandatory, this document becomes a
> **summary wrapper** over an annexure of challans, and `M20` must generate and number every one
> of them. If a period challan is permitted, this document **is** the challan. The two designs
> are materially different and the answer is needed before W4 build.

---

## 3. Layout

**Summary: A4 portrait. Schedules: A4 landscape.**

```
┌──────────────────────────────────────────────────┐
│ [LOGO]  CONSOLIDATED INVOICE   INV-C-…-000318    │  Summary page
│ 1000FiX Services Limited · BIN ############      │
│ Period 01/07/2026 – 31/07/2026                   │
├───────────────────────────┬──────────────────────┤
│ BILL TO                   │ ACCOUNT              │
│ Corporate entity, BIN     │ Contract · PO ref    │
│ AP contact                │ Account manager      │
├───────────────────────────┴──────────────────────┤
│ SUMMARY BY SITE                                  │
│ Site │ Jobs │ Value │ VAT │ Total                │
├──────────────────────────────────────────────────┤
│ SUMMARY BY SERVICE TYPE                          │
├──────────────────────────────────────────────────┤
│ CONTRACT ENTITLEMENT POSITION                    │
│ Included · Consumed · Over-consumption billed    │
├──────────────────────────────────────────────────┤
│ SERVICE CREDITS APPLIED (DT-031)                 │
├──────────────────────────────────────────────────┤
│                 Value · VAT by band · TOTAL DUE  │
├──────────────────────────────────────────────────┤
│ Payment terms · Dispute route · Approval trail   │
└──────────────────────────────────────────────────┘
   Schedule A — Detail by site / department / asset  (landscape)
   Schedule B — Underlying challans                  (per G6 CI1/CI2)
   Schedule C — Entitlement consumption detail
   Schedule D — Service credit calculation (DT-031)
```

| # | Rule |
|---|---|
| **L-20-a** | **Summary before detail, always.** An AP approver reads one page and drills only where a number surprises them |
| **L-20-b** | Sub-totals appear at every level the customer budgets at — site, department, cost centre — from `MD-015` and `MD-036` |
| **L-20-c** | VAT subtotals **by rate band** at the invoice level, and at each grouping level where the bands differ |
| **L-20-d** | Every detail line names the **asset or device** and its service order reference. A line without them is unverifiable and will be disputed |
| **L-20-e** | Service credits (`DT-031`) appear as a **distinct, labelled block**, never netted invisibly into a line value |
| **L-20-f** | Schedules carry the invoice number and period in their own headers; each is separately paginated **and** part of a whole-pack `page n of m` |

---

## 4. Field Mapping

### 4.1 Header and account

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Invoice no. | চালান নং | `MD-040` statutory sequence | Monospace | ✔ |
| Invoice date | তারিখ | `invoice.issued_at` | `DD/MM/YYYY` | ✔ |
| Billing period | বিলিং মেয়াদ | `MD-041` period | Date range | ✔ |
| Entity name / BIN | প্রতিষ্ঠান / বিআইএন | `MD-002` | Text + monospace | ✔ |
| Bill-to entity | বিল প্রাপক | `MD-015.account_legal_name` | Text | ✔ |
| **Buyer BIN** | **ক্রেতার বিআইএন** | `MD-015.bin` | Monospace | ✔ |
| Buyer address | ঠিকানা | `MD-015.registered_address` | Text | ✔ |
| AP contact | হিসাব যোগাযোগ | `MD-015.ap_contact` | Text | ✔ |
| Contract reference | চুক্তি সূত্র | `M08.contract_ref` | Monospace | ✔ |
| Buyer PO reference | ক্রয়াদেশ সূত্র | `MD-015.po_ref` | Monospace | **✔ where required by the buyer** |
| Account manager | হিসাব ব্যবস্থাপক | `employee.display_name` + contact | Text | ✔ |

### 4.2 Summary and detail

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Site | সাইট | `MD-015.site_code` + name | Text | ✔ |
| Department | বিভাগ | `MD-015.department` | Text | ✔ where used |
| Cost centre | ব্যয় কেন্দ্র | `MD-036.cost_centre_code` | Monospace | ✔ where used |
| Asset / device | সম্পদ / ডিভাইস | `device.asset_tag` or serial | Monospace | ✔ per detail line |
| Service order no. | সার্ভিস অর্ডার নং | `service_order.order_ref` | Monospace | ✔ per detail line |
| Completion date | সমাপ্তির তারিখ | `service_order.completed_at` | `DD/MM/YYYY` | ✔ |
| Service description | সেবার বিবরণ | `MD-019.item_name` | Text | ✔ |
| Coverage | আওতা | Enum: in-contract / out-of-scope / over-consumption / chargeable extra | Label | ✔ |
| Quantity / rate | পরিমাণ / দর | `MD-029` | Number, BDT | ✔ |
| Value excl. VAT | মূল্য | Computed | BDT, 2 dp | ✔ |
| VAT rate / amount | ভ্যাট হার / পরিমাণ | `MD-037` | %, BDT | ✔ |
| Line total | লাইন মোট | Computed | BDT, 2 dp | ✔ |
| Underlying challan no. | মূল চালান নং | `DT-010` reference | Monospace | **✔ per G6 CI1/CI2** |

### 4.3 Entitlement, credits and totals

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Entitlement included | অন্তর্ভুক্ত সুবিধা | `M08.entitlement` | Count / value | ✔ |
| Entitlement consumed | ব্যবহৃত | Computed | Count / value | ✔ |
| Over-consumption billed | অতিরিক্ত ব্যবহারের বিল | Computed | BDT, 2 dp | ✔ **`BRU-CTR-04`** |
| Out-of-scope billed | পরিধি-বহির্ভূত বিল | Computed | BDT, 2 dp | ✔ **`BRU-CTR-02`** |
| **Service credits applied** | **সেবা ক্রেডিট** | `DT-031` calculation | BDT, 2 dp, negative | ✔ where any |
| Credit calculation reference | ক্রেডিট গণনা সূত্র | `DT-031` schedule D | Monospace | ✔ with credits |
| Advance applied | প্রযোজ্য অগ্রিম | `DT-019` / `DT-016` | BDT, 2 dp | Where any |
| Value excl. VAT | মোট মূল্য | Computed | BDT, 2 dp | ✔ |
| VAT by band | হার অনুযায়ী ভ্যাট | Computed | BDT, 2 dp | ✔ |
| **Total due** | **মোট প্রদেয়** | Computed | BDT, 2 dp, largest type | ✔ |
| Amount in words | কথায় | Computed | Text | ✔ |
| Payment terms / due date | শর্ত / নির্ধারিত তারিখ | `MD-038` | Label + date | ✔ |
| Dispute route and deadline | বিরোধ জানানোর পথ | `M34` route | Text | ✔ |
| Approval trail | অনুমোদনের ধারা | `M63` workflow | Names + timestamps | ✔ |

| # | Rule |
|---|---|
| **FM-20-a** | **Every constituent job must be Completed and priced** before issue (`BRU-BIL-07`). A single unpriced job blocks the run — it does not silently drop out |
| **FM-20-b** | Out-of-scope and over-consumption lines are **labelled as such on the line**, not only in a summary. `BRU-CTR-02` and `BRU-CTR-04` require visibility, and visibility means at the point the approver reads |
| **FM-20-c** | Service credits are calculated by the system from measured SLA breach (`BRU-CTR-08`) and cross-reference `DT-031`. A manual credit requires CFO approval and prints the approver |
| **FM-20-d** | The approval trail prints — who priced, who reviewed, who released. Corporate AP teams reconcile against their own approvals, and this is what they match to |
| **FM-20-e** | The structured export contains **exactly** the printed data, at line level. An export that differs from the print is the fastest route to a dispute |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-BIL-07` | No issue until every constituent job is Completed and priced |
| `BRU-CTR-02` | Out-of-scope service billed separately and never silently absorbed |
| `BRU-CTR-04` | Entitlement over-consumption blocked or billed per configuration, never invisible |
| `BRU-CTR-08` | Service credits calculated automatically from measured breach; manual credits require CFO approval |
| `BRU-SRM-05` | Invoice only for Completed orders |
| `BRU-FIN-01` | VAT at the applicable rate and the company BIN displayed |
| `BRU-DMS-03` | Never edited after issue; correction by `DT-015` |
| `TAX-01`, `TAX-04` | Rate resolution per line at its own tax point — **lines in one consolidated invoice may carry different tax points** |
| `SEQ-01` | Gap-free statutory numbering |

### 5.1 Dispute prevention — how the 3% target is actually met

The `P04` dispute-rate commitment is a **document design** problem before it is a billing problem.

| # | Control |
|---|---|
| **DP-01** | Every line is verifiable by the approver **without contacting us** — asset, date, order reference, coverage |
| **DP-02** | Grouping matches the customer's own budget structure, taken from `MD-015` at onboarding, not assumed |
| **DP-03** | Anything unusual — out-of-scope, over-consumption, a manual credit — is labelled at the line |
| **DP-04** | A pre-invoice **draft is released to the account manager** before issue, and to the customer where the contract provides for it |
| **DP-05** | The structured export matches the print exactly (`FM-20-e`) |
| **DP-06** | Dispute reasons are coded (`MD-026`) and reported monthly by cause. **A dispute rate is not managed by chasing disputes; it is managed by removing their causes** |
| **DP-07** | A line disputed once for a given reason triggers a check of every similar line before the next run |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Standard consolidated** | Monthly corporate billing | Summary + schedules A–D |
| **Wrapper over challans** | If **G6 CI1** requires one challan per supply | Schedule B becomes the challan annexure; the summary is not itself the tax document |
| **Period challan** | If G6 CI1 permits a period challan | This document **is** the Mushak 6.3 and carries the statutory sequence |
| **Multi-entity group** | Per **G6 CI5** | One invoice per legal entity, with a group summary that is not itself an invoice |
| **AMC / subscription cycle** | `M39` recurring billing | Recurring charge plus usage; `BRU-BIL-02` missed-cycle exception rules apply |
| **Zero-value period** | Fully covered by contract | Still issued, showing entitlement consumed and value delivered (`BRU-CTR-04`) |
| **Credit-heavy period** | Service credits exceed charges | Net credit position; issued as a `DT-015` credit note, **not** as a negative invoice |
| **Structured export only** | Where AP ingests machine-readable data | The print remains the record; the export accompanies it |

---

## 7. Worked Example

> **Specimens produced only after G6 CI1 determines the structure.**

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-020-S1` | 6 sites, 3 departments, 140 jobs | Base structure and grouping |
| `DT-020-S2` | Period with out-of-scope and over-consumption | `FM-20-b` line labelling |
| `DT-020-S3` | Period with SLA service credits | `DT-031` schedule D linkage |
| `DT-020-S4` | Mixed VAT rate bands | `L-20-c` band subtotals at every level |
| `DT-020-S5` | Wrapper-over-challans structure | G6 CI1 alternative design |
| `DT-020-S6` | Net credit period | Issued as a credit note, not a negative invoice |

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Finance with Account Management | 2026-08-15 | Draft issue |
| Reviewer — Tax | *pending* | | |
| Reviewer — Account Management | *pending* | | |
| Reviewer — Legal & Compliance | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| **G6 — external tax adviser (CI1–CI5)** | *pending* | | **Unwaivable (`WV-02`); required before W4 build** |
| Approver — Chief Financial Officer | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — statutory where this document is the challan; otherwise a distinct consolidated-summary sequence with the challans numbered separately. **Determined by G6 CI1** |
| Gap policy | `no_gaps` on any statutory sequence involved |
| Archive format | **PDF/A-3 at issue, summary and all schedules as one file** |
| Retention | **At least 5 years** from the end of the tax period |
| Re-render | **Prohibited.** Rate cards, entitlements and site structures change; a re-render would not reconcile to the customer's copy |
| Reprint | Watermarked **COPY**, logged |
| Correction | `DT-015` credit or debit note referencing this invoice **and** the underlying lines (`G6 CI4`) |
| Export retention | The structured export is archived with the invoice, so a later dispute can be answered against what the customer actually ingested |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-010_Tax_Invoice_Mushak_6_3.md`](DT-010_Tax_Invoice_Mushak_6_3.md) | The statutory obligation this must satisfy |
| [`DT-011_Sales_Register_Mushak_6_2.md`](DT-011_Sales_Register_Mushak_6_2.md) | Where the constituent challans appear |
| [`DT-015_Credit_Note_and_Debit_Note.md`](DT-015_Credit_Note_and_Debit_Note.md) | The only correction route |
| [`DT-017_Customer_Statement_of_Account.md`](DT-017_Customer_Statement_of_Account.md) | Appears as a single line; multi-site variant mirrors this structure |
| [`DT-019_Proforma_Invoice_and_Advance_Request.md`](DT-019_Proforma_Invoice_and_Advance_Request.md) | Advances applied here |
| [`../05D_Commercial_and_Contract/DT-031_SLA_Schedule_and_Service_Credit_Annex.md`](../05D_Commercial_and_Contract/DT-031_SLA_Schedule_and_Service_Credit_Annex.md) | **Schedule D calculation must match it exactly** |
| [`../05D_Commercial_and_Contract/DT-030_Contract_and_AMC_Agreement_Template_Set.md`](../05D_Commercial_and_Contract/DT-030_Contract_and_AMC_Agreement_Template_Set.md) | Entitlements, billing frequency, notice terms |
| [`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-015_Corporate_Account_Hierarchy_Standard.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-015_Corporate_Account_Hierarchy_Standard.md) | Site, department and hierarchy — the grouping source |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-036_Cost_Centre_Business_Line_and_Dimension_Register.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-036_Cost_Centre_Business_Line_and_Dimension_Register.md) | Cost-centre dimension |
| `RP-005` Dashboard Specification Pack — External Audiences | The estate report this invoice complements |
| [`SP-020_SOP_Month_End_and_Year_End_Close.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-020_SOP_Month_End_and_Year_End_Close.md) | How the run is executed and released |
| [`NT-010_Email_Template_Library_Corporate_and_B2B.md`](../../04_Notification_and_Messaging/04C_Email/NT-010_Email_Template_Library_Corporate_and_B2B.md) | Delivery and approval-request emails |
| `UI-014` P04 Corporate B2B Portal UI Copy Pack | The portal presentation |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. The two-obligation tension raised as G6 CI1 with both design outcomes described, summary-before-detail structure, seven dispute-prevention controls tied to the `P04` 3% target, net-credit-period treatment | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `statutory_tier:` and `statutory_pin:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] The single-challan-versus-consolidated tension raised explicitly as G6 CI1, with both designs described
- [x] `P04` structural requirements mapped to document features
- [x] Dispute-prevention controls tied to the stated 3% commitment
- [x] Service credits linked to `DT-031` rather than restated (`CP-01`)
- [x] All internal links resolve
- [ ] **G6 CI1 — one challan per supply, or a period challan** — **outstanding, unwaivable; material `M20` design dependency needed before W4 build**
- [ ] G6 CI5 — multi-entity group billing — **outstanding; affects `MD-015` and `M65`**
- [ ] Service-credit calculation reconciled line-by-line with `DT-031` and `MD-028` (check **F3**) — **outstanding**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
