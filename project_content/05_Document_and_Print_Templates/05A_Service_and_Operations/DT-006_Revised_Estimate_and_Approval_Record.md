---
id: DT-006
title: Revised Estimate and Approval Record
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Operations
author: Operations with Commercial and Content Design
reviewers: [Commercial, Finance, Legal & Compliance, Quality, Localisation Lead]
approver: Chief Operating Officer with Chief Commercial Officer
content_class: C
purpose: >
  Records a variation from the approved estimate: what changed, why, the delta, the cumulative
  total and the re-approval capture. Scope growth mid-repair is the second most common dispute
  in device service, and an unlogged revision is unrecoverable — the company either absorbs the
  cost or charges an amount the customer never agreed to.
traces_to: [M36, M01, M20, DT-001, DT-004, DT-005, DT-010, MD-026, MD-040, BRU-SRM-07, BRU-SRM-08, BRU-SRM-13]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: DT-006_Revised_Estimate_and_Approval_Record_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-07 and BRU-SRM-08 — approval thresholds applied to the cumulative, not the incremental, total
    verified: 2026-08-15
    class: P1
  - source: project_content/05_Document_and_Print_Templates/05A_Service_and_Operations/DT-005 §1.1 and §6.2 term Q-3 — price certainty and the only lawful route past it
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-13 — expired estimates are re-issued, not extended
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-006 — Revised Estimate and Approval Record

> **This document exists because of one sentence in `DT-005`: term Q-3.** The final invoice will
> not exceed the approved estimate unless a revised estimate is approved. This is that revised
> estimate, and the record that it *was* approved.
>
> **The threshold test is applied to the cumulative total, not the increment.** An original of
> BDT 4,800 plus a revision of BDT 900 is a BDT 5,700 job and needs `BRU-SRM-07` approval, even
> though neither number on its own crosses the threshold.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Variation record and re-approval capture |
| Owning module | `M36` with `M01` |
| Statutory | No — but it is the control that keeps `DT-010` reconcilable to an approved offer |
| Recipient(s) | Customer, branch file, technician, `P01`/`P04` portal |
| Languages | **Bilingual — stacked labels, parallel columns for the delta explanation** |
| Output formats | A4 portrait · PDF · SMS/WhatsApp variation summary with approval link |
| Numbering mask | `MD-040` — `EST-{…}-{seq:06d}` **`/R{n}`** — a revision suffix on the original estimate number |
| Retention period | `LG-009`; identical to `DT-005` — the pair is read together or not at all |

### 1.1 The three situations this document covers

| Situation | Typical cause | Direction |
|---|---|---|
| **Scope increase** | Hidden damage found once the device is opened | Total rises |
| **Scope reduction** | A quoted part proves unnecessary, or the customer declines a line | Total falls |
| **Substitution** | A part is unavailable and an equivalent is proposed | Total may not change, but the offer does |

> All three are variations. A **reduction** is documented as rigorously as an increase, because
> an undocumented reduction is how "you charged me for a part you did not fit" begins.

---

## 2. Statutory Requirements

Not a statutory document. It carries the consumer-protection consequence of `DT-005`:

| Constraint | Source | Effect |
|---|---|---|
| No charge above the quoted price without agreement | Consumer Rights Protection Act 2009 — **pending G6** | An invoice exceeding the approved cumulative total without this record is unrecoverable and is a consumer-protection exposure |
| VAT presentation | `MD-037` | The revision recomputes VAT per rate band; the cumulative figures, not the delta, flow to `DT-010` |

---

## 3. Layout

**Primary format: A4 portrait.** The document is deliberately a **comparison**, not a fresh quote.

| Zone | Content | Bilingual treatment |
|---|---|---|
| Header | Revision number, original estimate number, date, validity | Title stacked, prominent `REVISION R{n}` marking |
| Party block | Customer left; device, order and original estimate reference right | Labels stacked |
| Body | **Three-column comparison** — original / change / revised — then the reason narrative | Labels stacked, narrative parallel columns |
| Totals | Original total, delta, **cumulative revised total** | Numerals per `BL-05` |
| Statutory block | Restated `DT-005` terms Q-1…Q-8, unchanged | Parallel columns |
| Signature | Customer re-approval; branch manager where the cumulative total crosses BDT 25,000 | Labels stacked |
| Footer | `EST-…/R{n}`, page n of m, hotline | English reference |

| # | Rule |
|---|---|
| **L-06-a** | The **original** estimate lines print alongside the revised ones. A revision that shows only the new position hides what changed, which is the entire point of the document |
| **L-06-b** | Changed lines are marked — `+` added, `−` removed, `Δ` amended. Colour is never the only signal (`CG-011` CL-01) |
| **L-06-c** | The cumulative revised total is the largest figure. The delta is secondary. Customers approve totals, not deltas |
| **L-06-d** | Where a revision follows a revision, **all prior revisions are listed** in a revision history block on the document itself |

---

## 4. Field Mapping

### 4.1 Header and linkage

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Revision no. | সংশোধন নং | `estimate.revision_seq` | `R{n}` | ✔ |
| Original estimate no. | মূল প্রাক্কলন নং | `DT-005` reference | Monospace | ✔ |
| Original estimate date | মূল তারিখ | `estimate.original_issued_at` | `DD/MM/YYYY` | ✔ |
| Revision date | সংশোধনের তারিখ | `estimate.revised_at` | `DD/MM/YYYY` | ✔ |
| Revised validity | নতুন মেয়াদ | `estimate.valid_to` | `DD/MM/YYYY` | ✔ |
| Prior revisions | পূর্ববর্তী সংশোধন | `estimate.revision_history[]` | List of refs + dates | ✔ (prints "None") |
| Work status at revision | কাজের অবস্থা | `service_order.status` | `MD-027` label | ✔ |

### 4.2 Line comparison

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Change marker | পরিবর্তন | Computed | `+` / `−` / `Δ` / blank | ✔ |
| Line description | বিবরণ | `MD-019` / `MD-022` | Text | ✔ |
| Finding ref. | পর্যবেক্ষণ সূত্র | `DT-004` `F{n}` | Monospace | ✔ on added lines |
| Original qty / amount | মূল পরিমাণ / মূল্য | `estimate.original.line` | Number, BDT | ✔ |
| Revised qty / amount | সংশোধিত পরিমাণ / মূল্য | `estimate.revised.line` | Number, BDT | ✔ |
| Line delta | পার্থক্য | Computed | BDT, signed | ✔ |
| Reason code | কারণ কোড | `MD-026.reason_code` | Code + label | ✔ **on every changed line** |

### 4.3 Totals and approval

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Original total | মূল মোট | `DT-005` total | BDT, 2 dp | ✔ |
| Net change | নিট পরিবর্তন | Computed | BDT, signed, 2 dp | ✔ |
| Change as % of original | শতাংশে পরিবর্তন | Computed | %, 1 dp | ✔ |
| **Revised total payable** | **সংশোধিত মোট প্রদেয়** | Computed | BDT, 2 dp, largest type | ✔ |
| Amount in words | কথায় | Computed | Both languages | ✔ |
| Customer decision | গ্রাহকের সিদ্ধান্ত | `estimate.revision_decision` | Enum: approved / declined / partially approved | ✔ |
| Decision evidence | সিদ্ধান্তের প্রমাণ | `M24` reference | Per `DT-005` §9.1 | ✔ |
| Branch manager approval | শাখা ব্যবস্থাপকের অনুমোদন | `employee.display_name` + timestamp | Text | **✔ where cumulative > BDT 25,000** |
| Work resumed at | কাজ পুনরায় শুরু | `service_order.resumed_at` | `DD/MM/YYYY HH:mm` | ✔ where approved |

| # | Rule |
|---|---|
| **FM-06-a** | **Every changed line carries a reason code from `MD-026`.** A change with no reason is a price change with no justification |
| **FM-06-b** | The approval test uses the **cumulative** revised total against `BRU-SRM-07` and `BRU-SRM-08` |
| **FM-06-c** | Work is **paused** from the moment the revision is raised until the decision is recorded. The document prints the pause start, and the SLA clock suspends under `BRU-SRM-15` with a hold reason |
| **FM-06-d** | A **partial approval** produces an explicit revised line set — never a note saying "customer approved some items" |
| **FM-06-e** | Where the customer declines, the document records what happens to the device: reassembled as found, work stopped at the approved scope, or returned unrepaired — and the charge position for each |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-SRM-07` / `BRU-SRM-08` | Applied to the cumulative total (`FM-06-b`) |
| `BRU-SRM-11` | Parts for added lines cannot be issued until this revision is approved |
| `BRU-SRM-13` | If the original estimate has already expired, this is not a revision — it is a **re-issue** under a new `DT-005` number |
| `BRU-SRM-15` | The approval wait is a hold with a reason code; the SLA clock suspends and resumes automatically |
| `BRU-SRM-19` | A revision raised after closure is not a revision; the order is reopened as rework or a new order is raised |
| `BRU-CTR-04` | For contract customers, over-consumption of entitlement appears here as a chargeable variation, visibly |
| `BRU-FIN-05` | A revision cannot be raised against a period already hard-closed with the invoice posted; that path is a credit note (`DT-015`) |

### 5.1 The boundary with `DT-015`

| Timing | Instrument |
|---|---|
| Before the invoice is issued | **`DT-006`** — this document |
| After the invoice is issued | **`DT-015`** credit or debit note. The invoice is never edited (`BRU-DMS-03`) |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Standard A4** | Any variation before invoicing | The base document |
| **Portal rendition** | `P01`, `P04` | Inline approve / decline / partially approve; same comparison view |
| **SMS / WhatsApp** | Low-value increments | Delta, revised total, one-line reason and an approval link. The full document is always available |
| **Corporate** | `P04` | Routed through the contract's delegation matrix; adds PO amendment reference |
| **Reduction-only** | Scope falls | Prints **"Revised amount is lower than the original"** prominently; still requires acknowledgement, not approval |
| **Substitution-only** | Part unavailable, equivalent proposed | Total may be unchanged; the `part_origin` change is the material fact and prints prominently (`DT-005` FM-05-c) |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-006-S1` | Hidden board damage, +BDT 6,200 | Base comparison rendition, reason codes |
| `DT-006-S2` | Original 4,800 + revision 900 | Cumulative threshold crossing (`FM-06-b`) |
| `DT-006-S3` | Second revision on the same order | Revision history block (`L-06-d`) |
| `DT-006-S4` | Customer declines; device reassembled | `FM-06-e` outcome and charge position |
| `DT-006-S5` | OEM part unavailable, equivalent substituted at same price | Substitution variant |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Operations with Commercial | 2026-08-15 | Draft issue |
| Reviewer — Commercial | *pending* | | |
| Reviewer — Finance | *pending* | | |
| Reviewer — Legal & Compliance | *pending* | | |
| Approver — COO with CCO | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | Suffix on the original: `EST-{entity}-{branch}-{yy}-{seq:06d}/R{n}`. **No independent sequence** — a revision that could be read without its original is a defect |
| Gap policy | Inherited from the parent estimate: `no_gaps`. A raised-then-abandoned revision keeps `R{n}` and records the abandonment |
| Reset | n/a — revision numbers restart per estimate |
| Archive format | PDF/A-3 at issue, archived **with** the original estimate as a single evidential set |
| Retention | Identical to `DT-005` |
| Re-render | Prohibited (`DT-001` §9.3) |
| Reprint | Watermarked **COPY**, logged |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-005_Repair_Estimate_and_Quotation.md`](DT-005_Repair_Estimate_and_Quotation.md) | The original this revises; term Q-3 is the reason this document exists |
| [`DT-004_Diagnostic_and_Condition_Report.md`](DT-004_Diagnostic_and_Condition_Report.md) | Added lines cite new findings from here |
| [`../05B_Finance_and_Statutory/DT-010_Tax_Invoice_Mushak_6_3.md`](../05B_Finance_and_Statutory/DT-010_Tax_Invoice_Mushak_6_3.md) | The cumulative revised total is what the invoice may charge |
| [`../05B_Finance_and_Statutory/DT-015_Credit_Note_and_Debit_Note.md`](../05B_Finance_and_Statutory/DT-015_Credit_Note_and_Debit_Note.md) | The instrument once the invoice has been issued (§5.1) |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md) | Reason codes on every changed line |
| `UI-038` Estimate and Approval Flow Copy | The on-screen variation journey |
| [`NT-022_Approval_Request_and_Reminder_Library.md`](../../04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-022_Approval_Request_and_Reminder_Library.md) | The messages that chase a pending revision |
| [`SP-013_SOP_Estimate_Approval_and_Rework_Control.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-013_SOP_Estimate_Approval_and_Rework_Control.md) | How a person raises and closes it |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Three-column comparison layout, cumulative threshold rule, mandatory reason codes, work-pause rule, decline-outcome capture, `DT-015` boundary | COO with CCO (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Cumulative-total threshold rule stated explicitly (`FM-06-b`)
- [x] Reductions and substitutions treated as variations, not exceptions
- [x] Boundary with `DT-015` stated (§5.1)
- [x] Numbering is a suffix on the parent, with the reason given
- [x] All internal links resolve
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Legal review of the decline-outcome charge positions (`FM-06-e`) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
