---
id: DT-040
title: Partner Commission Statement
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance with Partnerships
author: Finance with Partnerships, Tax and Content Design
reviewers: [External tax adviser, Tax, Legal & Compliance, Partnerships, Internal Audit]
approver: Chief Financial Officer
content_class: A
purpose: >
  Referrals, conversions, the attribution basis, commission rate, adjustments and the payment
  schedule. Partner commission accuracy target is 100%, and the statement is where accuracy is
  demonstrated — a partner cannot audit our attribution logic, so the statement must make the
  reasoning visible enough that they do not need to.
traces_to: [M40, M53, M20, M51, M35, P12, DT-001, DT-010, DT-013, DT-015, DT-039, MD-016, MD-038, MD-040, BRU-FIN-09, BRU-BIL-04, BRU-ECM-06]
priority: P2
wave: W7
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/00_Content_Governance_and_Standards/CG-010 §3.2 — DT-040 remains English
    verified: 2026-08-15
    class: P1
  - source: 1000FiX_ERP_Content_Master_Index CATEGORY 05 DT-040 — partner commission accuracy target 100%
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-FIN-09 — TDS is deducted at the correct rate on every applicable vendor payment; the payment cannot proceed otherwise
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-BIL-04 — commission is reversed automatically when the underlying transaction is refunded
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-040 — Partner Commission Statement

> ⚠ **Class A — statutory consequence.** Commission paid to a partner is a payment on which
> withholding may apply, and where the partner is VAT-registered their commission is a supply
> to us requiring their challan.
>
> **A 100% accuracy target is not achieved by careful calculation.** It is achieved by making the
> **attribution basis** visible, because attribution — not arithmetic — is where partner
> commission disputes actually arise. Two parties rarely disagree about 5% of BDT 40,000. They
> disagree about whether the referral was theirs.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Partner commission and settlement statement |
| Owning module | `M40` Partner, Channel, Alliance and Franchise, with `M53` |
| Statutory | No prescribed form. **Class A** — withholding on commission payments |
| Recipient(s) | Referral or channel partner, partnerships team, finance, internal audit |
| Languages | **English only** (`CG-010` §3.2) |
| Output formats | `P12` portal (primary) · PDF · structured export |
| Numbering mask | `MD-040` — `PCS-{entity}-{yy}-{seq:06d}` per partner per period |
| Retention period | **At least 5 years** where it evidences a taxable supply or a withholding — pending G6; otherwise `LG-009` |

### 1.1 Partner types and what they are paid for

| Partner type | Paid on | Attribution basis |
|---|---|---|
| **Referral partner** | A referred customer transacting | Referral code, link, or logged introduction |
| **Channel / reseller** | Volume of services sold | Contracted account list |
| **Franchise** | Territory revenue | Territory definition |
| **Alliance / technology** | Joint-solution revenue | Named opportunity registration |
| **Affiliate / digital** | Tracked conversion (`M35`) | Cookie, code or link with a stated window |

> **Each has a different attribution basis, and each basis has a different failure mode.** The
> statement states which basis applied to each line.

---

## 2. Statutory Requirements

No prescribed form. Three obligations:

| Obligation | Source | Verified | Effect |
|---|---|---|---|
| Withholding on commission | Income Tax Act 2023; `BRU-FIN-09` — **pending G6** | pending | Rate, deduction and the evidence the partner needs |
| VAT where the partner is registered | VAT & SD Act 2012 — **pending G6** | pending | The partner's challan to us; input claim in `DT-012` |
| VDS where applicable | `MD-037`, `DT-013` — **pending G6** | pending | Certificate to the partner |

### 2.1 G6 questions

| # | Question |
|---|---|
| **PA1** | Does withholding apply to commission payments to partners, at what rate, and what evidence must we give? |
| **PA2** | Where a partner is VAT-registered, must they issue us a Mushak 6.3 for their commission, and does that condition payment? |
| **PA3** | Does VDS apply, and is a `DT-013` due to the partner? |
| **PA4** | Is the treatment different for an individual partner versus a registered entity? |
| **PA5** | What retention applies to commission records? |

---

## 3. Layout

| Zone | Content |
|---|---|
| Header | Statement number, partner, period, payment date |
| Party block | Partner name, code, BIN/TIN and bank details left; our entity and partner manager right |
| Body | **Summary** → qualifying events → attribution → commission calculation → adjustments → tax |
| Totals | Gross commission, adjustments, withholding, **net payable**, payment reference |
| Statutory block | Not used. The **tax summary and query route** occupy this zone |
| Signature | Not signed; issued under system authority |
| Footer | Statement reference, `page n of m`, query route and deadline |

| # | Rule |
|---|---|
| **L-40-a** | **Every commission line names its attribution basis and the evidence** — code used, link, opportunity registration, account list entry |
| **L-40-b** | Summary first: qualifying events, gross commission, adjustments, withholding, net |
| **L-40-c** | Adjustments and reversals are itemised with reason and the transaction that caused them |
| **L-40-d** | The **rate applied prints per line**, because tiered and promotional rates change within a period |
| **L-40-e** | The tax summary is separate and complete |
| **L-40-f** | Excluded events — referrals that did not qualify — are shown **with the reason**, not silently omitted. This is the single most effective dispute-prevention feature of the statement |

---

## 4. Field Mapping

### 4.1 Header and summary

| Label | Source field | Format | Required |
|---|---|---|:--:|
| Statement no. | `MD-040` sequence | Monospace | ✔ |
| Statement date | `pcs.generated_at` | `DD/MM/YYYY` | ✔ |
| Period from / to | `MD-041` period | Date range | ✔ |
| Partner name and code | `MD-016` / `M40` | Text + monospace | ✔ |
| Partner type | `M40.partner_type` | Enum per §1.1 | ✔ |
| Partner BIN / TIN | `MD-016` | Monospace | ✔ where registered |
| Agreement reference | `M40.agreement_ref` | Monospace | ✔ |
| Bank account (masked) | `MD-038` | Masked | ✔ |
| Qualifying events | Computed | Integer | ✔ |
| **Gross commission** | Computed | BDT, 2 dp | ✔ |
| Adjustments | Computed | BDT, 2 dp, signed | ✔ |
| Withholding | Computed | BDT, 2 dp | ✔ where applicable |
| **Net payable** | Computed | BDT, 2 dp, largest type | ✔ |
| Payment reference / date | `payment.txn_ref`, `.paid_at` | Monospace + date | ✔ once paid |

### 4.2 Events, attribution and calculation

| Label | Source field | Format | Required |
|---|---|---|:--:|
| Event reference | `M40.event_ref` | Monospace | ✔ |
| Event date | `event.occurred_at` | `DD/MM/YYYY` | ✔ |
| Event type | Enum: referral / conversion / renewal / upsell | Label | ✔ |
| Customer reference (anonymised) | `party.masked_ref` | Monospace | ✔ |
| **Attribution basis** | `M40.attribution_basis` | Enum per §1.1 | ✔ **`L-40-a`** |
| **Attribution evidence** | Code, link, registration or list reference | Monospace + text | ✔ |
| Attribution window | `M40.attribution_window` | Days | ✔ where time-bound |
| Underlying transaction | `DT-010` reference | Monospace | ✔ |
| Transaction value | `invoice.total` | BDT, 2 dp | ✔ |
| Commissionable base | Computed per agreement | BDT, 2 dp | ✔ |
| **Rate applied** | `M40.commission_rate` | %, 2 dp | ✔ **per line (`L-40-d`)** |
| Rate basis | Enum: standard / tier / promotion | Label | ✔ |
| Commission amount | Computed | BDT, 2 dp | ✔ |
| **Excluded event** | `M40.excluded_event[]` | Reference | ✔ where any |
| **Exclusion reason** | `MD-026.reason_code` + text | Code + text | ✔ **`L-40-f`** |
| Reversal | `BRU-BIL-04` | BDT, 2 dp, negative | ✔ where any |
| Reversal cause | `DT-015` reference | Monospace | ✔ with a reversal |
| Clawback | `M40.clawback` + reason | BDT + text | ✔ where any |

### 4.3 Tax and settlement

| Label | Source field | Format | Required |
|---|---|---|:--:|
| Partner challan received | Partner's `Mushak 6.3` reference | Monospace | ✔ per G6 PA2 |
| VAT on commission | `MD-037` | BDT, 2 dp | ✔ where applicable |
| **Withholding rate and amount** | Per G6 PA1 | % + BDT | ✔ where applicable |
| Withholding evidence reference | Certificate reference | Monospace | ✔ with a deduction |
| VDS deducted / certificate | `DT-013` reference | Monospace | ✔ per G6 PA3 |
| Opening / closing balance | Computed | BDT, 2 dp | ✔ |
| Payment schedule | `M40.payment_terms` | Text | ✔ |
| Query route and deadline | `M34` / partner manager | Text | ✔ |

| # | Rule |
|---|---|
| **FM-40-a** | **Attribution evidence prints on every line.** A partner who can see why a line is theirs does not ask; a partner who cannot, does |
| **FM-40-b** | Excluded events print with reasons (`L-40-f`). Omitting them means the partner's own count will not match ours and they will assume under-reporting |
| **FM-40-c** | Rate and rate basis print per line, because a tier change mid-period otherwise looks like an error |
| **FM-40-d** | Reversals reference the credit note or dispute decision that caused them (`BRU-BIL-04`) |
| **FM-40-e** | Opening balance equals the prior statement's closing balance — the same continuity rule as `DT-017` and `DT-039` |
| **FM-40-f** | Where **G6 PA2** conditions payment on receiving the partner's challan, the statement shows the challan status per period and the payment is held until it arrives |
| **FM-40-g** | Customer identity is anonymised; a referral partner is not entitled to our customer's details (`BRU-SEC-05`) |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-FIN-09` | Withholding correctness; payment blocked otherwise |
| `BRU-BIL-04` | Automatic reversal on refund or adverse dispute |
| `BRU-BIL-06` | Deferred revenue and commission recognition alignment |
| `BRU-ECM-06` | Paid promotion never overrides disclosure — relevant where a partner's placement is promoted |
| `BRU-SEC-05` | Customer personal data not disclosed to partners |
| `BRU-ADM-01` | A commission-rate change is a controlled change with an effective date |

### 5.1 Achieving 100% accuracy

| # | Control |
|---|---|
| **AC-40-a** | Attribution is **deterministic and logged at the moment of the event**, not reconstructed at statement time |
| **AC-40-b** | Attribution windows and tie-break rules — last touch, first touch, priority order — are in the partner agreement and applied identically by the system |
| **AC-40-c** | Excluded events are surfaced, not suppressed (`L-40-f`) |
| **AC-40-d** | Rate changes are effective-dated and applied by event date, never by statement date |
| **AC-40-e** | A partner query is answered against the **issued** statement and the logged attribution evidence |
| **AC-40-f** | Query volume and cause are reported. **A recurring query cause is an accuracy defect even when every individual answer was correct** |
| **AC-40-g** | Reconciliation between commissions accrued in `M53` and paid in `M20` runs monthly; a difference blocks the next payment run |

> **AC-40-f is the one that gets the target to 100%.** A statement that is arithmetically perfect
> but generates fifty queries a month is not accurate in the sense the partner means.

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Referral partner** | Individual or small business referrers | Simple event list; attribution by code or link |
| **Channel / reseller** | Contracted resellers | Account-list attribution; volume tiers; larger values |
| **Franchise** | Territory franchisees | Territory revenue basis; franchise fee offsets |
| **Alliance** | Technology or solution partners | Registered-opportunity attribution; joint-deal splits |
| **Affiliate / digital** | `M35` tracked conversions | Window-based attribution; higher volume, lower values; exclusion reasons dominate |
| **Zero-commission period** | No qualifying events | Still issued, showing excluded events and why |
| **Final settlement** | Partnership ends | Full reconciliation, clawback window stated, closing statement |
| **Corrected statement** | Error found after issue | New statement referencing the original; the original retained |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-040-S1` | Referral partner, 12 conversions | Base statement with attribution evidence per line |
| `DT-040-S2` | Period with 5 excluded referrals | `L-40-f` exclusion reasons |
| `DT-040-S3` | Tier change mid-period | `FM-40-c` rate basis per line |
| `DT-040-S4` | Reversal after a customer refund | `BRU-BIL-04` linkage |
| `DT-040-S5` | Withholding deducted with evidence | `FM-40-f` and G6 PA1 |
| `DT-040-S6` | Final settlement with a clawback window | Closing variant |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Finance with Partnerships | 2026-08-15 | Draft issue |
| Reviewer — Tax | *pending* | | |
| Reviewer — Legal & Compliance | *pending* | | |
| Reviewer — Partnerships | *pending* | | |
| **G6 — external tax adviser (PA1–PA5)** | *pending* | | **Required before `P12` launch** |
| Approver — Chief Financial Officer | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `PCS-{entity}-{yy}-{seq:06d}` per partner per period |
| Gap policy | `gaps_recorded` |
| Archive format | **PDF/A-3 at issue**, plus the structured export |
| Retention | **At least 5 years** where it evidences a taxable supply or withholding — pending G6 PA5 |
| Attribution evidence | Logged at event time and retained with the statement (`AC-40-a`) |
| Re-render | **Prohibited.** Later adjustments would change a statement the partner already holds |
| Reprint | Watermarked **COPY**, logged |
| Continuity | Opening-to-closing continuity verified per partner each period |
| Partner access | Full history downloadable from `P12` for the retention period |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-039_Marketplace_Seller_Payout_Statement.md`](DT-039_Marketplace_Seller_Payout_Statement.md) | The seller counterpart; shared continuity and transparency discipline |
| [`../05B_Finance_and_Statutory/DT-010_Tax_Invoice_Mushak_6_3.md`](../05B_Finance_and_Statutory/DT-010_Tax_Invoice_Mushak_6_3.md) | The underlying customer transactions |
| [`../05B_Finance_and_Statutory/DT-013_VDS_Certificate_Mushak_6_6.md`](../05B_Finance_and_Statutory/DT-013_VDS_Certificate_Mushak_6_6.md) | Where VDS applies to commission |
| [`../05B_Finance_and_Statutory/DT-015_Credit_Note_and_Debit_Note.md`](../05B_Finance_and_Statutory/DT-015_Credit_Note_and_Debit_Note.md) | Refunds causing reversal |
| [`../05B_Finance_and_Statutory/DT-012_Purchase_Register_Mushak_6_1.md`](../05B_Finance_and_Statutory/DT-012_Purchase_Register_Mushak_6_1.md) | Where a partner's commission challan is registered |
| [`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md) | Partner identity, BIN and withholding applicability |
| `LG-007` Referral and Alliance Partner Agreement | Attribution rules, rates and clawback terms |
| `EO-009` Referral and Alliance Partner Kit | Where attribution is explained before a partner joins |
| `UI-022` P12 Partner and Referral Portal UI Copy Pack | Portal presentation |
| [`NT-012_Email_Template_Library_Seller_and_Partner.md`](../../04_Notification_and_Messaging/04C_Email/NT-012_Email_Template_Library_Seller_and_Partner.md) | Statement and payment notifications |
| `RP-005` Dashboard Specification Pack — External Audiences | Query-cause and accuracy reporting (`AC-40-f`) |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Five partner types with distinct attribution bases, attribution evidence printed per line, excluded events surfaced with reasons, rate basis per line, seven accuracy controls including query-cause reporting | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Attribution identified as the real dispute source and made visible per line
- [x] Excluded events surfaced with reasons (`L-40-f`)
- [x] Rate and rate basis printed per line
- [x] Accuracy controls tied to the stated 100% target, including query-cause reporting
- [x] All internal links resolve
- [x] Bengali counterpart — n/a per `CG-010` §3.2
- [ ] **G6 PA1–PA3 — withholding, partner challan and VDS on commission** — **outstanding; required before `P12` launch**
- [ ] Attribution rules, windows and tie-breaks published in `LG-007` and implemented identically in `M40` — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
