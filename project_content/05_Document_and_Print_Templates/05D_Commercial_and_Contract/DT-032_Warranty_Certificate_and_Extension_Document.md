---
id: DT-032
title: Warranty Certificate and Extension Document
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Warranty with Legal & Compliance
author: Warranty with Legal & Compliance and Content Design
reviewers: [Legal Counsel, Finance, Service Operations, Quality, Localisation Lead]
approver: Legal Counsel with Chief Commercial Officer
content_class: B
purpose: >
  The repair warranty and the purchased extension certificate, stating coverage, exclusions and
  how to claim. It is simultaneously the customer's proof of entitlement and the company's limit
  of liability, and those two functions must both be legible on one page — a certificate that is
  clear about coverage and vague about exclusions is a liability, not a product.
traces_to: [M09, M39, M01, P01, P08, DT-001, DT-007, DT-033, DT-036, LG-013, MD-031, MD-033, MD-040, BRU-WTY-06, BRU-WTY-07, BRU-SRM-19]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: DT-032_Warranty_Certificate_and_Extension_Document_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-WTY-07 — a warranty product cannot be sold on a device that fails the eligibility assessment
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-19 — a closed order may be reopened only within the repair warranty period, and reopening links it as rework
    verified: 2026-08-15
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-031 Warranty Type and Coverage Term Catalogue — the coverage definitions this certificate prints
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-032 — Warranty Certificate and Extension Document

> ⚠ **Class B — legal.** A warranty certificate creates an obligation that outlives the
> transaction, sometimes by years. The exclusions are as much a part of the product as the
> coverage, and if they are not read they will not be enforceable.
>
> **Three different things are called "warranty" in this business and they must never be
> conflated on a document:** the manufacturer's warranty (not ours), the warranty on our repair
> (granted by `DT-007`), and a purchased extended-warranty product (sold by us, priced, and
> carrying a reserve).

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Warranty certificate / extended-warranty product document |
| Owning module | `M09` Warranty, Protection Plans and Claims |
| Statutory | No — **legally binding entitlement and liability limit** |
| Recipient(s) | Customer, service operations, claims handling, brand partner where relevant |
| Languages | **Bilingual — parallel columns for coverage and exclusions** |
| Output formats | A4 portrait · PDF for portal and email · wallet-format summary card |
| Numbering mask | `MD-040` — `WTY-{entity}-{yy}-{seq:06d}` |
| Retention period | `LG-009`; **warranty term plus the limitation period** |

### 1.1 The three warranties

| Type | Whose obligation | Issued by | This document? |
|---|---|---|:--:|
| **Manufacturer warranty** | The brand's | The brand, at purchase | **No** — we record it (`M17`), we do not certify it |
| **Repair warranty** | **Ours** | Granted on `DT-007` at completion | ✔ Certificate issued where the term or value warrants one |
| **Extended warranty / protection plan** | **Ours**, as a sold product | Sold and certificated here | ✔ The primary use of this document |
| Brand-authorised repair under warranty | The brand's, performed by us | `DT-033` claim | No — the repair warranty above still applies to our work |

| # | Rule |
|---|---|
| **WT-01** | The certificate states **explicitly** which of the three it is. A customer holding a repair-warranty certificate must not believe they hold a device warranty |
| **WT-02** | Coverage language never implies cover the company has not sold. "Comprehensive" is banned unless every exclusion is on the same page |
| **WT-03** | A repair warranty covers **the repair**, not the device. That distinction is stated in plain language in both languages |

---

## 2. Statutory Requirements

Not statutory. Five constraints:

| Constraint | Source | Effect |
|---|---|---|
| Exclusions must be brought to the customer's attention | Consumer Rights Protection Act 2009 — **pending G6** | Exclusions buried in small print may be unenforceable |
| No misleading description of cover | Consumer Rights Protection Act 2009 — **pending G6** | Overstated cover is a misrepresentation |
| Statutory rights are not diminished | Consumer protection — **pending G6** | The certificate states that statutory rights are unaffected |
| Extended warranty may be a regulated product | **Pending G6 — insurance regulation question** | If an extended warranty is insurance, it is regulated. **This must be answered before `M39` sells one** |
| Financial provisioning | Accounting standards; `M19` | A sold warranty carries a liability and a reserve |

### 2.1 G6 questions

| # | Question |
|---|---|
| **WY1** | **Is a paid extended warranty an insurance product under Bangladeshi law, and does it require authorisation?** |
| **WY2** | What exclusions are enforceable in a consumer warranty, and how must they be presented? |
| **WY3** | What statutory rights must be preserved and stated? |
| **WY4** | Is a transfer of warranty on device resale permitted, restricted, or required? |
| **WY5** | What is the position where the covered device is repaired by a third party during the term? |

> **WY1 is a gating question, not a detail.** If an extended warranty is a regulated insurance
> product, selling one without authorisation is a regulatory breach. It must be answered before
> the product is offered, not before it is renewed.

---

## 3. Layout

| Zone | Content | Bilingual |
|---|---|---|
| Header | **Certificate type stated plainly**, certificate number, issue date | Title stacked, type prominent |
| Party block | Customer left; device, serial and covered-item details right | Labels stacked |
| Body | **What is covered** → **what is not covered** → term → claim process | **Parallel columns** |
| Totals | Cover limit and any excess, where applicable | Arabic numerals |
| Statutory block | Statutory-rights statement and the transfer position | Parallel columns |
| Signature | Issued under company authority; e-signature where a purchased product | — |
| Footer | Certificate reference, `page n of m`, hotline 16743, portal link | English |
| Machine-readable | QR: certificate reference, resolving to the portal record (`DT-044`) | — |

| # | Rule |
|---|---|
| **L-32-a** | **Coverage and exclusions are the same size, in the same weight, on the same page.** Exclusions in smaller type is the single most common reason a warranty exclusion fails |
| **L-32-b** | The certificate type is in the header, not inferred from the body (`WT-01`) |
| **L-32-c** | The claim process is on the certificate — not only in terms referenced elsewhere. A customer needing to claim is a customer under stress |
| **L-32-d** | The exclusions block never splits across a page |
| **L-32-e** | The wallet card carries the certificate number, device, term end and hotline only, and states that full terms are on the certificate |

---

## 4. Field Mapping

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| **Certificate type** | সনদের ধরন | `warranty.type` | Enum: repair warranty / extended warranty / protection plan | ✔ |
| Certificate no. | সনদ নং | `MD-040` sequence | Monospace | ✔ |
| Issue date | ইস্যুর তারিখ | `warranty.issued_at` | `DD/MM/YYYY` | ✔ |
| Customer name | গ্রাহকের নাম | `party.display_name` | Text | ✔ |
| Customer mobile | মোবাইল | `party.mobile_primary` | Masked | ✔ |
| Device | ডিভাইস | `MD-021` make + model | Text | ✔ |
| Serial / IMEI | সিরিয়াল | `device.serial_no` | Monospace | ✔ |
| Related service order | সার্ভিস অর্ডার | `service_order.order_ref` | Monospace | ✔ repair warranty |
| Completion report | সমাপ্তি রিপোর্ট | `DT-007` reference | Monospace | ✔ repair warranty |
| Product / plan | পণ্য / পরিকল্পনা | `MD-033.plan_code` | Code + name | ✔ extended warranty |
| **Cover starts / ends** | কভার শুরু / শেষ | Computed | `DD/MM/YYYY` | ✔ |
| Term | মেয়াদ | `MD-031.term` | Months | ✔ |
| **What is covered** | যা অন্তর্ভুক্ত | `MD-031.coverage_text_en` / `_bn` | Text, itemised | ✔ |
| Parts covered | অন্তর্ভুক্ত যন্ত্রাংশ | `MD-031.parts_covered` | List | ✔ |
| Labour covered | অন্তর্ভুক্ত শ্রম | `MD-031.labour_covered` | Bool + terms | ✔ |
| **What is not covered** | যা অন্তর্ভুক্ত নয় | `MD-031.exclusion_text_en` / `_bn` | Text, **numbered list** | ✔ |
| Cover limit | কভারের সীমা | `MD-031.cover_limit` | BDT or "no limit" | ✔ |
| Excess / deductible | কর্তনযোগ্য | `MD-031.excess` | BDT | ✔ where any |
| Claim limit per term | মেয়াদে দাবির সীমা | `MD-031.claim_limit` | Count | ✔ where limited |
| **How to claim** | দাবি করার পদ্ধতি | Static: hotline 16743, portal, branch | Text | ✔ |
| Claim evidence required | দাবির প্রমাণ | Static | Text | ✔ |
| Transferable | হস্তান্তরযোগ্য | `MD-031.transferable` | Bool + conditions | ✔ **per G6 WY4** |
| Statutory rights | আইনি অধিকার | Static, per **G6 WY3** | Text | ✔ |
| Eligibility assessment | যোগ্যতা মূল্যায়ন | `M09` assessment ref | Monospace | ✔ **extended warranty (`BRU-WTY-07`)** |
| Purchase reference | ক্রয় সূত্র | `DT-010` reference | Monospace | ✔ where purchased |

| # | Rule |
|---|---|
| **FM-32-a** | Coverage and exclusion text comes from `MD-031`, **never typed per certificate**. A warranty the company has not defined cannot be granted |
| **FM-32-b** | Exclusions print as a **numbered list**. Each is separately arguable and must be separately citable in a claim decision |
| **FM-32-c** | An extended warranty requires a recorded eligibility assessment (`BRU-WTY-07`). A certificate cannot issue without its reference |
| **FM-32-d** | A repair warranty excludes customer-supplied parts (`DT-005` term Q-6) and says so explicitly |
| **FM-32-e** | Privilege discounts apply to labour only (`BRU-WTY-06`); where a plan interacts with Privilege, the interaction is stated, not left to be discovered at claim time |
| **FM-32-f** | The reopening window for rework (`BRU-SRM-19`) is the repair-warranty term. The certificate is what the customer produces to reopen |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-WTY-07` | Eligibility assessment required before a warranty product may be sold |
| `BRU-WTY-06` | Privilege discounts on labour only |
| `BRU-SRM-19` | Reopening within the repair warranty period links as rework |
| `BRU-SRM-06` | A repeat fault within 30 days is auto-flagged as rework, regardless of warranty |
| `BRU-WTY-02` | Warranty claims are auto-created within 24 hours of a warranty work order closing |
| `BRU-BIL-06` | Deferred revenue on a sold warranty is released per the recognition schedule |
| `BRU-DMS-03` | An issued certificate is not edited; a correction is a reissue with the original voided |

### 5.1 Claim decisions rest on this document

| # | Rule |
|---|---|
| **CD-01** | A claim is decided against **the certificate the customer holds**, in the version issued — not against the current `MD-031` definitions |
| **CD-02** | Certificate terms are therefore **pinned at issue** and the pinned version is retrievable (`CG-006`) |
| **CD-03** | A rejection cites the **numbered exclusion** relied on. "Not covered" is not a decision |
| **CD-04** | Where a claim is rejected on an exclusion that the customer plausibly could not have understood, the decision escalates before it is communicated |
| **CD-05** | Exclusion-based rejection rates by exclusion number are reported. **An exclusion doing most of the rejecting is either a badly drawn product or a badly explained one** |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Repair warranty certificate** | Issued with `DT-007` where term or value warrants | Covers the repair, references the completion report |
| **Extended warranty / protection plan** | Sold product (`M39`) | Eligibility assessment, purchase reference, cover limit, excess, deferred-revenue linkage |
| **Wallet card** | Accompanies either | Short form (`L-32-e`) |
| **Corporate estate** | `P04` covered assets | Issued per asset or as a schedule against the contract; interacts with `DT-030` Schedule B |
| **Refurbished device warranty** | Refurbished resale (`M14`) | References the `DT-036` grading record; disclosure of refurbished status is mandatory |
| **Rental cover** | `M13` rental assets | Cover is on the rented asset, terms in `DT-037`, not a separate warranty |
| **Renewal** | Extended warranty renewed | New certificate, references the prior, re-assesses eligibility |
| **Transfer** | Device sold to a new owner | Per **G6 WY4**; new certificate to the new owner, original voided |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-032-S1` | 90-day repair warranty on a screen replacement | Base bilingual, `WT-03` repair-not-device language |
| `DT-032-S2` | 12-month extended warranty on a laptop | Eligibility assessment, cover limit, excess |
| `DT-032-S3` | Certificate with 11 numbered exclusions | `L-32-a` equal prominence, `FM-32-b` numbering |
| `DT-032-S4` | Refurbished device | `DT-036` linkage and status disclosure |
| `DT-032-S5` | Claim rejected on exclusion 7 | `CD-03` citation |
| `DT-032-S6` | Wallet card | `L-32-e` |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Warranty with Legal & Compliance | 2026-08-15 | Draft issue |
| Reviewer — Finance (reserve and revenue recognition) | *pending* | | |
| Reviewer — Service Operations | *pending* | | |
| Reviewer — Quality | *pending* | | |
| **Legal Counsel — coverage, exclusions and G6 WY1** | *pending* | | **Required** |
| Approver — Legal Counsel with CCO | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `WTY-{entity}-{yy}-{seq:06d}` |
| Gap policy | `gaps_recorded`; a voided certificate retains its number |
| Archive format | **PDF/A-3 at issue** — it must be producible years later |
| Retention | `LG-009`; **warranty term plus the limitation period** |
| Term pinning | `MD-031` coverage and exclusion text **pinned at issue** (`CD-02`) |
| Re-render | **Prohibited.** `MD-031` will change; a re-render would restate today's cover under yesterday's certificate |
| Reprint | Watermarked **COPY**, logged; **a lost certificate is replaced with a copy, never a new original** |
| Portal availability | Available in `P01` for the full term, so a lost paper certificate does not defeat a valid claim |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`../05A_Service_and_Operations/DT-007_Service_Completion_Report.md`](../05A_Service_and_Operations/DT-007_Service_Completion_Report.md) | Grants the repair warranty this certifies |
| [`DT-033_Warranty_Claim_Evidence_Pack.md`](DT-033_Warranty_Claim_Evidence_Pack.md) | Brand claims — a different obligation |
| [`DT-036_Refurbishment_Grading_and_Certification_Record.md`](DT-036_Refurbishment_Grading_and_Certification_Record.md) | Refurbished-device cover |
| [`DT-030_Contract_and_AMC_Agreement_Template_Set.md`](DT-030_Contract_and_AMC_Agreement_Template_Set.md) | Where cover is contractual rather than a warranty |
| [`DT-037_Rental_Agreement_and_Asset_Handover_Record.md`](DT-037_Rental_Agreement_and_Asset_Handover_Record.md) | Rental asset cover |
| [`../../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-031_Warranty_Type_and_Coverage_Term_Catalogue.md`](../../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-031_Warranty_Type_and_Coverage_Term_Catalogue.md) | **Coverage and exclusion source; never typed** |
| [`../../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-033_Subscription_Plan_and_Billing_Cycle_Register.md`](../../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-033_Subscription_Plan_and_Billing_Cycle_Register.md) | Protection-plan products |
| `LG-013` Service Terms, Warranty Terms and Exclusions | The full terms this certificate summarises |
| `UI-040` Registration and Onboarding Flow Copy | Warranty registration journey |
| `HC-003` Help Set — P01 Customer Portal and App | Customer self-service |
| `RP-002` Report Catalogue by Role and Module | `CD-05` exclusion-rejection reporting |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Three-warranty distinction with anti-conflation rules, equal-prominence exclusion rule, numbered exclusions cited in claim decisions, term pinning at issue, insurance-regulation question raised as gating G6 WY1 | Legal Counsel with CCO (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] The three warranty types distinguished with explicit anti-conflation rules
- [x] Exclusions given equal typographic prominence and numbered for citation
- [x] Terms pinned at issue so claims are decided against the certificate held
- [x] All internal links resolve
- [ ] **G6 WY1 — whether an extended warranty is a regulated insurance product** — **outstanding; gating, must precede any sale**
- [ ] G6 WY2/WY3 — enforceable exclusions and statutory-rights statement — **outstanding**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] `MD-031` coverage and exclusion text authored bilingually — **outstanding, dependency**
- [ ] Financial reserve and revenue-recognition treatment confirmed with Finance — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
