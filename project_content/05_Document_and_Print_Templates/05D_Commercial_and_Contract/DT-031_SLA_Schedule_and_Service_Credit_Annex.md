---
id: DT-031
title: SLA Schedule and Service Credit Annex
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance with Service Operations
author: Legal & Compliance with Service Operations, Finance and Content Design
reviewers: [Legal Counsel, Finance, Service Operations, Account Management, Platform Engineering]
approver: Legal Counsel with Chief Operating Officer
content_class: B
purpose: >
  Response and resolution commitments, the measurement method, the exclusions and the service
  credit calculation. Service credits are a direct financial liability, so the calculation must be
  unambiguous and must match MD-028 exactly — a contractual commitment the system cannot measure
  is a liability with no control.
traces_to: [M08, M01, M02, M19, P04, P11, DT-001, DT-020, DT-030, MD-028, MD-026, MD-041, LG-015, BRU-CTR-08, BRU-SRM-15, BRU-SRM-10, NT-020]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: DT-031_SLA_Schedule_and_Service_Credit_Annex_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-CTR-08 — service credits are calculated automatically from measured SLA breach; manual credits require CFO approval
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-15 — the SLA clock is suspended only by an approved hold reason and resumes automatically when the hold is released
    verified: 2026-08-15
    class: P1
  - source: project_content/_AUDIT/AUDIT_Checklist_Recurring.md check F3 — SLA definitions identical across MD-028, DT-031 and LG-015; zero divergence required because these carry financial liability
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-031 — SLA Schedule and Service Credit Annex

> ⚠ **Class B — legal, with direct financial consequence.**
>
> **Audit check F3 exists because of this document.** SLA definitions must be identical across
> `MD-028` (the register the system measures against), this annex (the contractual commitment)
> and `LG-015` (the master terms). Zero divergence. Not "broadly aligned" — identical.
>
> A response time promised here that `MD-028` does not define is a promise the system cannot
> measure. A promise the system cannot measure is either never honoured or never enforced, and
> both outcomes cost the company.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Contract annex — service levels and credits |
| Owning module | `M08` Contract Lifecycle, measured by `M01` and `M02` |
| Statutory | No — **directly financially binding** |
| Recipient(s) | Customer signatory, account manager, service operations, finance, `P11` quality |
| Languages | **Bilingual — parallel columns for the credit calculation** |
| Output formats | A4 portrait, attached to `DT-030` as Schedule C · PDF · portal (`P04`) |
| Numbering mask | None of its own — carries the parent contract reference plus `/SCH-C` |
| Retention period | With the parent contract: **term plus limitation period** |

### 1.1 The four things an SLA annex must be unambiguous about

| # | Element | The ambiguity it removes |
|---|---|---|
| 1 | **What is measured** | Response? Arrival? Resolution? Restoration? These are different events |
| 2 | **When the clock starts and stops** | Ticket creation, first contact, or customer report? |
| 3 | **What pauses the clock** | Customer unavailability, parts lead time, third-party dependency |
| 4 | **What is excluded entirely** | Out-of-scope work, force majeure, customer-caused failure |

> Every SLA dispute the company will ever have is about one of these four. A contract that is
> vague on any of them concedes the argument in advance.

---

## 2. Statutory Requirements

Not statutory. Four constraints:

| Constraint | Source | Effect |
|---|---|---|
| Enforceability of the credit mechanism | Contract Act — **pending G6** | A credit that reads as a penalty may be unenforceable; a liquidated-damages framing is usually safer |
| Consistency with `MD-028` | Audit check **F3** | Divergence is a financial-control failure |
| Measurability | `05-06` NFR set | A commitment the platform cannot measure cannot be honoured or defended |
| Consumer fairness in RAMC | Consumer Rights Protection Act 2009 — **pending G6** | Consumer contracts cannot exclude core obligations |

### 2.1 G6 questions for Legal Counsel

| # | Question |
|---|---|
| **SL1** | Is our service-credit mechanism enforceable as drafted, or should it be framed as liquidated damages? |
| **SL2** | Is a cap on aggregate credits enforceable, and at what level? |
| **SL3** | Can credits be the **sole remedy** for a service-level failure, and is that enforceable for consumers? |
| **SL4** | What exclusions are permissible, particularly force majeure and third-party dependency? |
| **SL5** | Are the RAMC service levels compatible with consumer protection obligations? |

---

## 3. Layout

| Zone | Content | Bilingual |
|---|---|---|
| Header | Parent contract reference, annex designation, effective dates | Title stacked |
| Party block | Inherited from the parent contract | — |
| Body | Priority definitions → commitments table → measurement method → clock rules → exclusions → credit calculation | **Parallel columns** |
| Totals | Credit rates and the aggregate cap | Arabic numerals |
| Statutory block | The credit mechanism clause and remedy statement | Parallel columns |
| Signature | Initialled with the parent contract | — |
| Footer | Contract reference `/SCH-C`, `page n of m`, `MD-028` version | English |

| # | Rule |
|---|---|
| **L-31-a** | The **`MD-028` version reference prints in the footer**. When a dispute arises, the first question is which SLA definitions applied, and the answer must be on the page |
| **L-31-b** | The commitments table uses the same priority codes, names and target values as `MD-028` — **copied, not paraphrased** |
| **L-31-c** | The credit calculation is shown with a **worked example** on the annex itself. A formula without an example is a formula two parties will compute differently |
| **L-31-d** | Exclusions are a numbered list, not prose. Each is separately arguable and must be separately identifiable |
| **L-31-e** | The credit block never splits across a page |

---

## 4. Field Mapping

### 4.1 Commitments

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Priority code | অগ্রাধিকার কোড | `MD-028.priority_code` | Code | ✔ |
| Priority name | অগ্রাধিকারের নাম | `MD-028.priority_name_en` / `_bn` | Text | ✔ |
| Definition / trigger | সংজ্ঞা | `MD-028.definition` | Text | ✔ |
| **Response target** | **সাড়া দেওয়ার লক্ষ্য** | `MD-028.response_target` | Duration | ✔ |
| **Resolution target** | **সমাধানের লক্ষ্য** | `MD-028.resolution_target` | Duration | ✔ |
| Hours of cover | সেবার সময় | `MD-028.coverage_window` | Text + `MD-041` | ✔ |
| Measurement basis | পরিমাপের ভিত্তি | `MD-028.measurement_basis` | Enum: calendar hours / business hours | ✔ |
| Target attainment % | লক্ষ্য অর্জনের হার | `contract.sla_attainment_pct` | %, 1 dp | ✔ |
| Measurement period | পরিমাপের মেয়াদ | `contract.sla_period` | Enum: monthly / quarterly | ✔ |

### 4.2 Clock, exclusions and credits

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Clock start event | ঘড়ি শুরুর ঘটনা | `MD-028.clock_start_event` | Enum | ✔ |
| Clock stop event | ঘড়ি থামার ঘটনা | `MD-028.clock_stop_event` | Enum | ✔ |
| **Approved hold reasons** | **অনুমোদিত বিরতির কারণ** | `MD-026` hold reasons | Coded list | ✔ **`BRU-SRM-15`** |
| Maximum hold duration | সর্বোচ্চ বিরতি | `contract.max_hold` | Duration | Where capped |
| Exclusion | ব্যতিক্রম | Numbered approved list | Text | ✔ |
| **Credit trigger** | **ক্রেডিটের শর্ত** | `contract.credit_trigger` | Text | ✔ |
| Credit rate | ক্রেডিটের হার | `contract.credit_rate` | % of period charge or fixed | ✔ |
| Credit basis | ক্রেডিটের ভিত্তি | `contract.credit_basis` | Enum: per breach / per period attainment | ✔ |
| **Aggregate cap** | **সর্বোচ্চ সীমা** | `contract.credit_cap_pct` | % of period charge | ✔ **per G6 SL2** |
| Claim requirement | দাবির শর্ত | `contract.credit_claim_required` | Bool + window | ✔ |
| Application method | প্রয়োগের পদ্ধতি | Enum: credit note / next invoice offset | Label | ✔ |
| Sole remedy statement | একমাত্র প্রতিকার | Per **G6 SL3** | Text | ✔ |
| Worked example | নমুনা হিসাব | Static, per credit basis | Table | ✔ |

| # | Rule |
|---|---|
| **FM-31-a** | Every value in §4.1 is **read from `MD-028`**, not entered. A contract cannot promise a target the register does not contain |
| **FM-31-b** | Hold reasons are the `MD-026` approved set. **A hold reason not in the set does not stop the clock** (`BRU-SRM-15`), and the customer can see the list |
| **FM-31-c** | Credits are calculated automatically from measured breach (`BRU-CTR-08`). A manual credit requires CFO approval and appears on `DT-020` with the approver named |
| **FM-31-d** | Where a claim is required within a window, the window is stated and the customer is notified of breaches as they occur (`NT-020`) — **requiring a claim the customer cannot know to make is not a defensible position** |
| **FM-31-e** | Privilege tier auto-upgrades (`BRU-SRM-10`) are reflected in the priority applied, and the annex says so |
| **FM-31-f** | The aggregate cap and the sole-remedy statement are the two clauses Legal must confirm; both are marked pending until G6 answers SL2 and SL3 |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-CTR-08` | Automatic credit calculation; manual credits need CFO approval |
| `BRU-SRM-15` | The clock suspends only on an approved hold reason and resumes automatically |
| `BRU-SRM-10` | Privilege Gold and Diamond receive priority-1 SLA regardless of service type |
| `BRU-CTR-02` | Out-of-scope work is outside the SLA as well as outside the price |
| `BRU-CTR-04` | Entitlement over-consumption does not suspend the SLA unless the annex says so |
| `BRU-QMS-04` | A complaint linked to a breach is closed with the customer, not internally |

### 5.1 Measurement integrity

The annex is only worth what the measurement behind it is worth.

| # | Rule |
|---|---|
| **MI-01** | Clock events are **system events**, not human judgements. "Responded" means a recorded event, not a belief that someone called |
| **MI-02** | Holds require a coded reason and are visible to the customer on the portal. A hidden hold is an unmeasurable SLA |
| **MI-03** | Hold duration is reported alongside SLA attainment. **A 100% attainment achieved through extensive holds is a reporting artefact, not performance** |
| **MI-04** | Attainment is calculated on the contract's measurement period and basis, not on a convenient one |
| **MI-05** | Breaches are notified as they occur (`NT-020`), not discovered at period end |
| **MI-06** | The customer sees the same measurement we do, in `P04`. Two versions of the truth is how SLA relationships fail |
| **MI-07** | Where a measurement is disputed, the underlying event log is producible |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Standard corporate** | AMC and MSP contracts | Full annex with credits |
| **RAMC consumer** | Residential | Simplified targets, plainer language, no credit mechanism unless offered; consumer protections retained (**G6 SL5**) |
| **Healthcare / critical** | Hospitals, diagnostics | Tighter targets, escalation contacts, calibration-linked commitments (`BRU-CTR-07`) |
| **Enterprise multi-service** | Framework agreements | One annex per service schedule; targets differ by service |
| **Government / tender** | Public procurement | Prescribed service levels where the tender mandates them; **those override ours and Legal confirms each** |
| **Pilot / trial** | Evaluation period | Targets stated as measured but with no credit liability, explicitly |
| **Marketplace-delivered** | Seller-fulfilled jobs (`P07`) | Same customer-facing commitment; the seller's obligation is in the seller agreement, not here (`BRU-ECM-03`) |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-031-S1` | Corporate AMC, 4 priority tiers | Base annex, `MD-028` values copied exactly |
| `DT-031-S2` | Period with 2 breaches and a credit | `L-31-c` worked calculation |
| `DT-031-S3` | Job with an approved hold | `BRU-SRM-15` clock suspension and `MI-03` reporting |
| `DT-031-S4` | Privilege Gold customer | `BRU-SRM-10` auto-upgrade reflected |
| `DT-031-S5` | Credits reaching the aggregate cap | Cap application |
| `DT-031-S6` | RAMC consumer annex | Simplified variant |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Legal & Compliance with Service Operations | 2026-08-15 | Draft issue |
| Reviewer — Service Operations | *pending* | | |
| Reviewer — Finance (credit liability) | *pending* | | |
| Reviewer — Platform Engineering (measurability) | *pending* | | |
| **Legal Counsel — credit mechanism and remedy** | *pending* | | **Required** |
| Approver — Legal Counsel with COO | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | None; carries the parent contract reference plus `/SCH-C` |
| Archive format | **PDF/A-3 with the parent contract** |
| Retention | With the parent contract: term plus limitation period |
| Re-render | Prohibited |
| `MD-028` pinning | The **`MD-028` version in force at signature is recorded and pinned** to the contract. A later register change does not alter a signed commitment (`CG-006`) |
| Measurement evidence | Event logs supporting attainment are retained for the credit-claim window plus the dispute period |
| Reprint | Watermarked **COPY**, logged |

> **The pinning rule in §9 is the one people forget.** `MD-028` will change. Contracts signed
> under an earlier version keep the earlier commitments, and the system must measure each contract
> against the version it was signed under — not against today's register.

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-030_Contract_and_AMC_Agreement_Template_Set.md`](DT-030_Contract_and_AMC_Agreement_Template_Set.md) | The parent contract; this is Schedule C |
| [`../05B_Finance_and_Statutory/DT-020_Consolidated_Corporate_Invoice.md`](../05B_Finance_and_Statutory/DT-020_Consolidated_Corporate_Invoice.md) | Where credits are applied, in Schedule D |
| [`../05B_Finance_and_Statutory/DT-015_Credit_Note_and_Debit_Note.md`](../05B_Finance_and_Statutory/DT-015_Credit_Note_and_Debit_Note.md) | The instrument where a credit note is issued |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md) | **The source of truth; check F3 compares them** |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md) | Approved hold reasons |
| `LG-015` AMC, SLA Master Terms and Service Credit Rules | The third document in check F3 |
| [`NT-020_Escalation_and_SLA_Breach_Notification_Library.md`](../../04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-020_Escalation_and_SLA_Breach_Notification_Library.md) | Breach notification (`FM-31-d`, `MI-05`) |
| `RP-004` Dashboard Specification Pack — Operational Consoles | Attainment and hold reporting (`MI-03`) |
| `UI-014` P04 Corporate B2B Portal UI Copy Pack | Customer-visible SLA measurement (`MI-06`) |
| [`SP-015_SOP_Contract_and_AMC_Lifecycle.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-015_SOP_Contract_and_AMC_Lifecycle.md) | Operating the mechanism |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Four-ambiguity framework, values copied from `MD-028` rather than paraphrased, seven measurement-integrity rules including hold-adjusted attainment, `MD-028` version pinning at signature | Legal Counsel with COO (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Values sourced from `MD-028`, not restated (`FM-31-a`, `L-31-b`)
- [x] Check **F3** named as the governing consistency control
- [x] Measurement integrity rules stated, including hold-adjusted attainment (`MI-03`)
- [x] `MD-028` version pinning at signature specified
- [x] Worked credit example required on the annex itself
- [x] All internal links resolve
- [ ] **Check F3 run against `MD-028` and `LG-015` — zero divergence** — **outstanding; blocks `Approved`**
- [ ] **Legal Counsel confirmation of the credit mechanism, cap and sole-remedy statement (SL1–SL3)** — **outstanding**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Platform confirmation that every committed target is measurable as specified — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
