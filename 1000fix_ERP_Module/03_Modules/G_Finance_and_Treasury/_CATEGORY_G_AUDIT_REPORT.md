---
id: FIX-ERP2-CAT-G-AUDIT
category: G
category_name: Finance & Treasury
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: COMPLETE
classification: CONFIDENTIAL — Internal Use Only
scope: The 8 module specifications in 03_Modules/G_Finance_and_Treasury
---

# Category G — Module Specification Audit Report

**Audit of the 8 Finance & Treasury module specifications against
`_CATEGORY_OVERVIEW.md`, `03_Modules/_MODULE_TEMPLATE.md`, and the cross-cutting registers.**

---

## 1. Audit Result

**PASS with 3 findings** — 1 corrected during audit, 2 raised as actions on documents outside
this category.

| # | Dimension | Result |
|---|---|---|
| 1 | Module coverage vs `_CATEGORY_OVERVIEW.md` §2 | **PASS** — 8 of 8 |
| 2 | Structural conformance to `_MODULE_TEMPLATE.md` | **PASS** — 19 sections each |
| 3 | Front-matter vs overview §2 and `02-02` register | **PASS** — code, priority, wave, owner, category all match |
| 4 | FR identifier integrity | **PASS** — 333 requirements, no gaps, no duplicates |
| 5 | Declared vs measured requirement counts | **PASS** — all 8 match |
| 6 | CD identifier allocation | **PASS** — 41 IDs, no duplicates, contiguous new block |
| 7 | Business rule / automation / AC / technical ID sequences | **PASS** — no gaps in any own-prefix sequence |
| 8 | Scope boundary reciprocity (intra-category) | **PASS** — 51 delegations, all claimed by the named owner |
| 9 | Dependency reciprocity | **PASS** — 0 asymmetries |
| 10 | Overview §5 boundary map coverage | **PASS** — 16 of 16 rows, 1 alignment note (F-02) |
| 11 | Overview §6 statutory obligations coverage | **PASS** — 10 of 10, all in M51 |
| 12 | Overview §7 cash control coverage | **PASS** — 9 of 9, after correction F-01 |
| 13 | Overview §8 KPI coverage | **PASS** — 19 of 19 present in the owning module |
| 14 | KPI identifier consistency vs `06-02` | **PASS** — with re-ownership documented (F-03) |
| 15 | Posting invariant ("only M19 creates journal entries") | **PASS** — asserted in all 8 |
| 16 | Cross-file reference resolution | **PASS** — all 8 filenames resolve |

---

## 2. Deliverables

| Module | File | Lines | FRs | Effort |
|---|---|---:|---:|---:|
| M19 | `M19_Financial_Accounting_and_General_Ledger.md` | 933 | 46 | 28 PW |
| M20 | `M20_Accounts_Receivable_Invoicing_and_Collections.md` | 980 | 44 | 24 PW |
| M52 | `M52_Accounts_Payable_and_Employee_Expense.md` | 961 | 38 | 19 PW |
| M50 | `M50_Treasury_Cash_and_Banking.md` | 1,010 | 42 | 22 PW |
| M51 | `M51_Tax_and_Regulatory_Compliance_Bangladesh.md` | 1,003 | 45 | 26 PW |
| M53 | `M53_Revenue_Recognition_Commission_and_Settlement.md` | 1,005 | 44 | 28 PW |
| M49 | `M49_Fixed_Assets_and_Capital_Investment.md` | 934 | 34 | 16 PW |
| M54 | `M54_Cost_Accounting_Budgeting_and_FPA.md` | 1,007 | 40 | 22 PW |
| | **Total** | **7,833** | **333** | **185 PW** |

> **Effort variance.** `02-02` estimated **146 PW** across the eight modules. The measured total
> is **185 PW (+27%)**. The variance is concentrated in **M51 (+6 PW)**, **M50 (+6 PW)**,
> **M49 (+5 PW)** and **M53 (+4 PW)** — the four modules whose scope was least defined in the
> v2.0 draft. `02-02` §2 Category G requires updating. **Raised as action A-03.**
>
> Requirement counts likewise exceed the register estimates in every module (333 measured vs
> 258 estimated, +29%). Both figures are marked as measured supersessions in each module's §1.

---

## 3. Findings

### F-01 · Corrected during audit · Terminology traceability

`_CATEGORY_OVERVIEW.md` §7 names the daily cash-visibility control **"Treasury dashboard"**.
M50 delivered the capability (FR-TRE-013, and the §14 report) but under the label *Consolidated
cash position*, breaking literal traceability to the overview's control table.

**Action taken:** M50 §14 report renamed to *Treasury dashboard — consolidated cash position*
with an explicit reference to `_CATEGORY_OVERVIEW.md` §7. **Closed.**

### F-02 · Open · Boundary phrasing in `_CATEGORY_OVERVIEW.md` §5

Overview §5 row *"Vendor invoice approval and payment"* reads: owned by **M52**, not owned by
**M16 (matches PO/GRN)**. The parenthetical is ambiguous — it can be read as M16 owning the
three-way match.

**Position taken in the specifications:** **M52 owns the three-way match and its exceptions**
(FR-APE-003…008); **M16 owns the purchase order and the buying lifecycle**; **M15/M16 own the
goods receipt**. M52 matches against artefacts it does not create. This is consistent with the
BRD (BR-FIN-010 places three-way matching on vendor invoice processing) and with SAP's
Logistics Invoice Verification pattern.

**Action:** amend `_CATEGORY_OVERVIEW.md` §5 to read *"M16 (owns the PO and GRN being matched
against)"*. **Owner: Category owner (CFO). Raised as action A-04.**

### F-03 · Open · KPI ownership in `06-02` does not reflect the v2.1 re-scope

Three canonical KPIs are allocated to M19 in `06-02` §2.7 but are owned by other modules under
the v2.1 split, and one is jointly instrumented across categories:

| KPI | `06-02` owner | v2.1 owner | Rationale |
|---|---|---|---|
| KPI-051 Bank reconciliation auto-match | M19 | **M50** | Bank reconciliation moved to Treasury |
| KPI-057 VAT returns filed on time | M19 | **M51** | Tax compliance moved to M51 |
| KPI-058 Tax compliance findings | M19 | **M51** | Tax compliance moved to M51 |
| KPI-049 Three-way match exception rate | M16 | **M52 instruments; M16 co-owns** | The match executes in M52; the exception is resolved jointly |

Each is flagged in the owning module's §15 register note. **Raised as action A-01.**

---

## 4. Audit Actions Register

| ID | Action | Target Document | Owner | Priority |
|---|---|---|---|:--:|
| **A-01** | Re-own KPI-051 → M50, KPI-057/058 → M51; record KPI-049 as jointly owned M16/M52 | `06-02` §2.5, §2.7 | CFO | **High** |
| **A-02** | Allocate canonical identifiers to the **128 new metrics** introduced across the 8 modules, prioritising the six named in overview §8 that currently have none (payout accuracy, deferred revenue reconciled, fixed asset register reconciled, budget variance explained, negative-margin contracts, branch cash variance) | `06-02` §2.7 | CFO | **High** |
| **A-03** | Update Category G requirement counts (258 → 333) and effort (146 → 185 PW) | `02-02` §2 Category G | Programme Director | **High** |
| **A-04** | Clarify the M52/M16 three-way-match boundary phrasing | `_CATEGORY_OVERVIEW.md` §5 | CFO | Medium |
| **A-05** | Register the Category G CD block **CD-157…186** and the eleven reallocations (CD-083…090, 093, 094, 095) in the unified CD register | `02-05` §5.2 | CTO | **High** |
| **A-06** | Record BRU-FIN-11 … BRU-FIN-26 (new M19 rules) and the seven new module-prefix rule sets (ARB, APE, TRE, TAX, REV, FXA, FPA — 180 rules) | `05-05` | CFO | Medium |
| **A-07** | Register the 8 modules' owned entities (**196 tables**) in the entity catalogue | `05-02` | CTO | Medium |
| **A-08** | Register the API surfaces (**148 endpoints**) and domain events (**141 events**) | `05-03` | CTO | Medium |

---

## 5. Custom Development Allocation (verified — no duplicates)

**New contiguous block: CD-157 … CD-186 (30 IDs).** Category E's block ends at CD-156
(`M15` §16.2), so the Category G block starts cleanly at CD-157.

| Module | Reallocated from v2.0 | New | Total |
|---|---|---|---:|
| M19 | CD-089 | CD-157…160 | 5 |
| M20 | CD-090, CD-095 | CD-161…163 | 5 |
| M52 | — | CD-164…166 | 3 |
| M50 | CD-087 | CD-167…172 | 7 |
| M51 | CD-083, 084, 085, 086 | CD-173…175 | 7 |
| M53 | CD-093, CD-094 | CD-176…179 | 6 |
| M49 | CD-088 | CD-180…182 | 4 |
| M54 | — | CD-183…186 | 4 |
| | **11** | **30** | **41** |

**Leaving Category G:** CD-091 `cd_subscription` and CD-092 `cd_usage_billing` → **M39**
(Category C). Both reallocations are documented in `M20` §16.2.

---

## 6. Programme Risks Surfaced by This Specification Set

These are new or newly quantified. They are not defects in the documents; they are decisions
the programme must take.

| # | Risk | Severity | Where Raised |
|---|---|:--:|---|
| **R-1** | **Decision D-03 (marketplace principal vs agent) is unresolved and now blocks two modules, not one.** It determines M51's VAT base *and* M53's gross-vs-net revenue presentation. Both modules **refuse to process marketplace transactions** rather than defaulting — a deliberate hard block | **Critical** | `M51` §18 Q-02, `M53` §18 Q-01 |
| **R-2** | **M20 and M52 need tax determination in W3; M51 ships in W4.** Provisional stubs are specified for both, with W3 VAT registers **reconstructed** on M51 go-live as a defined migration task. This must be approved and resourced, or M51 pulled forward | **High** | `M20` §18 Q-03, `M52` §18 Q-02, `M51` §18 Q-01, `M51` §16.4 |
| **R-3** | **Three cutover physical counts are required** — cash at all locations (M50), fixed assets (M49), plus the existing inventory count (M15). Each is stated as non-negotiable for the same reason: an unproven opening balance makes the reconciliation KPI permanently unachievable. The combined operational commitment has not been costed | **High** | `M50` §16.4, `M49` §16.4 + §18 Q-08 |
| **R-4** | **Bank statement format availability is unverified.** The > 94% auto-match target (KPI-051) is unachievable against a bank that provides PDF statements only. This must be established per banking partner before W3 design | **High** | `M50` §18 Q-01, Q-02 |
| **R-5** | **The shift-open block (BRU-FIN-10) is the most likely point of operational adoption resistance.** M50 specifies it as failing closed, including offline. Whether an emergency override exists — and who holds it — is unresolved | **Medium** | `M50` §18 Q-12 |
| **R-6** | **M54's allocation policy is design work, not migration** — current practice is largely undocumented, and an allocation basis imposed without branch-manager agreement will be rejected the first time it produces an unwelcome result | **Medium** | `M54` §18 Q-01, Q-02, §16.4 |
| **R-7** | **Warranty classification (assurance vs service) is missing from the catalogue** and blocks every M53 revenue schedule for a warranty-bearing item. In a business whose core operation is warranty work, there is no safe default | **Medium** | `M53` §18 Q-02, AUT-REV-02 |
| **R-8** | **Vendor bank-detail re-verification at migration** is control-critical and currently has no procedure before M42 lands in W4 | **Medium** | `M52` §18 Q-13 |

---

## 7. Design Invariants Established Across the Category

Verified as consistently asserted in all eight specifications.

| # | Invariant | Enforcement |
|---|---|---|
| 1 | **Only M19 creates journal entries.** Every other module raises typed events | M19 §T-01…T-06; asserted in all 8 §3.2 tables |
| 2 | **Posting rules live in M19, versioned, never in the subledger** | M19 FR-FIN-008…010, BRU-FIN-17/18 |
| 3 | **Tax determination is a service that fails closed** — no default, no zero, no last-known value | M51 FR-TAX-008, BRU-TAX-03; contract-tested in M20 and M52 |
| 4 | **All outbound payment executes through M50** — no other module holds bank credentials | M50 BRU-TRE-11, T-01, T-10 |
| 5 | **Customer payment and merchant settlement are separate events** (channel clearing model) | M20 FR-ARB-020, M50 FR-TRE-024…026 |
| 6 | **Margin uses recognised revenue (M53), never billed revenue (M20)** | M54 BRU-FPA-03, T-02 |
| 7 | **M54 holds no actuals of its own** — the CO/FI reconciliation problem designed out | M54 BRU-FPA-02, T-01, AC-01 |
| 8 | **Every register, schedule and asset traces to a source; manual creation is an approved, reported exception** | M19 BRU-FIN-16, M20 BRU-ARB-02, M53 BRU-REV-01, M49 BRU-FXA-01 |
| 9 | **Money-path idempotency end to end** — a replay never double-pays | M52 T-04, M50 T-02/BRU-TRE-14, M53 T-07/BRU-REV-18 |
| 10 | **Opening balances are proven, not loaded** — count, statement or contract-level reconstruction | M50 §16.4, M49 §16.4, M53 §16.4, M20 §16.4, M19 §16.4 |

---

## 8. Segregation of Duties Coverage

All twelve `05-04` §6 SoD rules that touch Category G are enforced in a named module:

| SoD | Rule | Enforced In |
|---|---|---|
| SOD-01 | Create vendor + approve vendor invoice | **M52** BRU-APE-04, AC-05 |
| SOD-02 | Raise PO + receive goods + approve invoice | **M52** BRU-APE-05, AC-06 |
| SOD-04 | Create + approve credit note | **M20** BRU-ARB-09, AC-13 |
| SOD-06 | Approve seller + approve their payout | **M53** BRU-REV-23, AC-24 |
| SOD-12 | Handle cash + reconcile the cash book | **M50** BRU-TRE-05, AC-14 |
| — | Journal preparer ≠ approver *(new)* | **M19** BRU-FIN-11, AC-14 |
| — | Posting rights ≠ posting-rule administration *(new)* | **M19** BRU-FIN-25 |
| — | Payment preparer ≠ reviewer ≠ releaser *(new)* | **M52** BRU-APE-06 / **M50** BRU-TRE-12 |
| — | Verifier ≠ register-correction approver *(new)* | **M49** BRU-FXA-15, AC-18 |
| — | Cost centre owner ≠ own budget approver *(new)* | **M54** BRU-FPA-11, AC-19 |

**SOD-03, 05, 07, 08, 09, 10, 11** are enforced outside Category G (M21, M15, M23, M33, M29,
M14, M09) and are referenced where they intersect.

---

## 9. Benchmark Basis — Coverage Check

Every module benchmarks against the tier-one suites named in `_CATEGORY_OVERVIEW.md` §3, plus
specialist references appropriate to its domain.

| Module | Primary external references |
|---|---|
| M19 | SAP Universal Journal (ACDOCA) · Oracle Subledger Accounting · Dynamics financial dimensions · OCA account-financial-tools |
| M20 | SAP FI-AR + FSCM Collections/Dispute · Oracle Receivables · Dynamics AR · Bangladesh MFS settlement practice · NBR Mushak 6.3 |
| M52 | SAP MM-IV + F110 · Ariba/Concur · Oracle Payables · Dynamics Expense · Bangladesh TDS/VDS FY 2025-26 |
| M50 | SAP BAM + TRM · Oracle Cash Management · Dynamics Cash & Bank · TMS practice · Bangladesh Bank BD-RTGS / BEFTN · bKash/Nagad/SSLCOMMERZ |
| M51 | SAP ACR · Oracle Tax · Dynamics Electronic Reporting · Indian GST localisation analogue · VAT & SD Act 2012 / Rules 2016 · Income Tax Act 2023 · SRO 182-Ain/2025 |
| M53 | SAP RAR · Oracle Revenue Management · Zuora RevPro · marketplace settlement practice · **IFRS 15** (incl. the assurance-vs-service warranty distinction) · IFRS 16 |
| M49 | SAP FI-AA in ACDOCA · Oracle Assets · Dynamics Fixed Assets · **Income Tax Act 2023 Third Schedule** · IAS 16 / IAS 36 / IFRS 16 |
| M54 | SAP Controlling (CO) · Oracle Cost Management / PCM · Dynamics Cost Accounting & Budgeting · Anaplan/Adaptive FP&A practice · OCA mis-builder |

---

## 10. Audit Method

| Check | Method |
|---|---|
| Structure, front matter, section count | Automated parse of all 8 files |
| FR / BRU / AUT / AC / T identifier integrity | Automated extraction, uniqueness and gap detection |
| Declared vs measured requirement counts | Automated comparison against §1 declarations |
| CD identifier allocation | Automated extraction of all §16.2 tables, duplicate and gap detection across the category and against `02-05` §5.2 |
| Boundary reciprocity | Automated extraction of all 51 intra-category §3.2 delegations, each verified against the named owner's §3.1 |
| Dependency reciprocity | Automated comparison of every §1 *Depends on* / *Depended on by* pair |
| Overview §5 / §6 / §7 / §8 coverage | Term-by-term verification against the owning module |
| Cross-file references | Automated filename resolution |
| Design invariants, SoD, benchmark basis | Manual review against `05-04`, `05-05`, `02-01` AS-01…AS-15 |

---

*Category G Audit Report · 1000FiX ERP System v2.0 · CONFIDENTIAL*
