---
id: FIX-ERP2-CAT-G
category: G
category_name: Finance & Treasury
module_count: 8
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT
---

# Category G — Finance & Treasury

**8 modules · Category owner: Chief Financial Officer**

---

## 1. What Belongs in This Category

Money — recorded, collected, paid, held, planned, taxed and reported.

If a capability answers *"what is the financial consequence, and can we prove it to an
auditor or the NBR"*, it belongs here. If it answers *"what should we charge"*, that is
Category C.

**The governing principle:** other modules raise *billable events* and *cost events*.
Only Category G creates journal entries.

---

## 2. Modules

| ID | Module | Status | Priority | Wave | One-Line Definition |
|---|---|---|:--:|:--:|---|
| **M19** | Financial Accounting & General Ledger | Re-scoped | P0 | W3 | The statutory ledger: chart of accounts, journals, periods, multi-entity, consolidation, financial statements |
| **M20** | Accounts Receivable, Invoicing & Collections | Re-scoped | P0 | W3 | Customer invoicing, receipts, matching, ageing, dunning, credit notes and refunds |
| **M52** | Accounts Payable & Employee Expense ★ | New | P1 | W3 | Vendor invoices, three-way-matched approval, payment runs, advances, staff expense claims |
| **M50** | Treasury, Cash & Banking ★ | New | P1 | W3 | Bank accounts, branch cash across 51+ counters, gateway settlement, cash-flow forecasting, LC and facilities |
| **M51** | Tax & Regulatory Compliance (Bangladesh) ★ | New | P0 | W4 | Mushak VAT, VAT sub-ledgers and returns, TDS/VDS, challans and certificates, income-tax schedules |
| **M53** | Revenue Recognition, Commission & Settlement ★ | New | P1 | W4 / W7 | Revenue schedules, deferral, performance obligations, commission ledgers, seller and partner payouts, escrow |
| **M49** | Fixed Assets & Capital Investment ★ | New | P2 | W5 | Asset register, capitalisation, depreciation, disposal, CWIP, impairment, capital approval |
| **M54** | Cost Accounting, Budgeting & FP&A ★ | New | P2 | W6 | Cost allocation, job and contract costing, budgets, variance, forecasting, business-line profitability |

★ = new in v2.1 after enterprise benchmarking.

---

## 3. Why Eight Finance Modules

Because every tier-one ERP has them, and because a company with **14 revenue streams, 51+
cash-handling branches, imports, a marketplace with third-party payouts, and Bangladesh
statutory obligations** cannot run finance as one module.

| Benchmark | Equivalent Modules |
|---|---|
| **Oracle Fusion Financials** | General Ledger · Payables · Receivables · Fixed Assets · Cash Management & Treasury · Expenses · Tax |
| **SAP S/4HANA Finance** | FI-GL · FI-AP · FI-AR · FI-AA · Treasury & Cash Management · Tax · Controlling (CO) · Revenue Accounting (RAR) |
| **Dynamics 365 Finance** | General ledger · Accounts payable · Accounts receivable · Fixed assets · Cash and bank management · Tax · Budgeting · Cost accounting |
| **1000FiX v2.1** | M19 · M52 · M20 · M49 · M50 · M51 · M53 · M54 |

The mapping is one-to-one with the enterprise standard. The v2.0 draft compressed all of it
into two modules, which would have made the ledger unstable every time a commercial model
changed.

---

## 4. The Money Flow

```
  OPERATIONAL MODULES                 CATEGORY G                     OUTPUT
  ───────────────────                 ──────────                     ──────

  M01/M31 job closed ──┐
  M08 contract cycle ──┤
  M39 subscription ────┼──► billable events ──► M20 AR ──► invoice ──► customer
  M38/M12 orders ──────┤                          │
  M13 rental period ───┘                          ├──► receipt ──► M50 cash/bank
                                                  │
  M09 warranty claim ──────► reimbursement ───────┘

  M16 goods received ──┐
  M52 vendor invoice ──┼──► three-way match ──► M52 AP ──► payment ──► M50
  M21 payroll ─────────┘

  M12 commission ──────────► M53 settlement ──► seller payout ──► M50

  ALL POSTINGS ─────────────────► M19 GENERAL LEDGER ◄──── M49 depreciation
                                        │                  M51 tax
                                        ├──► statutory financial statements
                                        ├──► M51 VAT return, TDS challans
                                        └──► M54 costing, budget variance, business-line P&L
```

---

## 5. Category Boundary Map

| Capability | Owned By | Not Owned By |
|---|---|---|
| Chart of accounts, journals, periods, consolidation | **M19** | All others post to it |
| Customer invoice creation and delivery | **M20** | M36 (quotes), M39 (schedules) |
| Recurring billing schedule and proration | **M39** (Category C) | M20 (issues the resulting invoice) |
| Price determination | **M11** (Category C) | M20 |
| Receipt capture and matching | **M20** | M50 (holds the bank position) |
| Bank accounts, balances, reconciliation | **M50** | M19 (posts the result) |
| Branch cash drawer operation | **M04** (Category A) | M50 (consolidates the position) |
| Vendor invoice approval and payment | **M52** | M16 (matches PO/GRN) |
| Staff expense claims | **M52** | M21 (owns the employee) |
| VAT, TDS, Mushak, statutory returns | **M51** | M19 (holds the postings) |
| Revenue schedules and deferral | **M53** | M19 (posts the release) |
| Commission calculation scheme | **M12** defines; **M53** calculates and pays | — |
| Fixed asset capitalisation and depreciation | **M49** | M17, M45, M46 (operational views) |
| Job, contract and business-line costing | **M54** | M19 |
| Budgeting and forecasting | **M54** | M19 |
| Financial dashboards | **M25** (Category J) | M19, M54 (supply the data) |

---

## 6. Bangladesh Statutory Obligations (M51)

These are not features; they are conditions of operating.

| Obligation | Requirement | Frequency |
|---|---|---|
| Mushak 6.3 tax invoice | NBR-prescribed format, sequence, BIN, Bengali | Every taxable sale |
| Mushak 6.1 / 6.2 / 6.2.1 / 6.5 / 6.6 registers | Maintained and reconcilable | Continuous |
| Mushak 9.1 VAT return | Compiled from the ledger, reconciled | Monthly |
| Input VAT credit | Tracked and offset | Monthly |
| TDS / VDS deduction | Correct rate by category, at source | Every applicable payment |
| TDS challan and certificate | Deposited and issued to the vendor | Per deduction |
| Corporate income tax schedules | Prepared from the ledger | Annual |
| Fiscal year | July–June | Structural |
| High-value cash NID capture | Above the statutory threshold | Every occurrence |
| Import duty and VAT at import | Accounted into landed cost | Per shipment |

**Marketplace VAT treatment (principal vs agent) is an open decision — D-03 — and blocks
Wave 7.** Getting it wrong is the highest-rated commercial risk in the programme.

---

## 7. Cash Control Across 51+ Branches

The largest day-to-day financial control risk in the business.

| Control | Mechanism | Module |
|---|---|---|
| Every counter opens a shift with a counted float | Shift open | M04 |
| Every cash movement is recorded at the point it happens | Cash drawer | M04 |
| Every shift closes with a counted balance and explained variance | Shift close | M04 |
| An unclosed shift blocks the next shift's opening | Hard rule BRU-FIN-10 | M04 / M50 |
| Field cash is reconciled per technician per day | Field reconciliation | M02 / M50 |
| Rider cash-on-delivery is reconciled per shift | Rider reconciliation | M03 / M50 |
| Branch deposits are matched to bank statement lines | Bank reconciliation | M50 |
| Consolidated cash position is visible daily | Treasury dashboard | M50 |
| Cash handling and reconciliation are segregated duties | SOD-12 | M29 |

---

## 8. Category KPIs

| KPI | Baseline | Target | Owning Module |
|---|---|---|---|
| Month-end close cycle | 15–20 days | ≤ 3 days | M19 |
| Audit adjustments at year end | unmeasured | < 0.5% of revenue | M19 |
| Invoices auto-generated from operations | 0% | 100% | M20 |
| Invoice issued within 1 hour of job closure | 3–7 days | > 97% | M20 |
| Days sales outstanding | unmeasured | < 32 days | M20 |
| Billing accuracy (credit notes as % of invoices) | unmeasured | < 1.5% |M20 |
| Revenue leakage (delivered but unbilled) | unknown | < 0.5% | M20 / M53 |
| Bank reconciliation auto-match rate | manual | > 94% | M50 |
| Unreconciled gateway settlements > 7 days | unmeasured | 0 | M50 |
| Branch cash variance incidents | unmeasured | < 1 per branch per month | M50 |
| Three-way match exception rate | n/a | < 5% | M52 |
| Vendor payment on terms | unmeasured | > 95% | M52 |
| VAT returns filed on time with zero adjustment | manual | 100% | M51 |
| Tax compliance findings | unmeasured | **Zero** | M51 |
| Seller and partner payout accuracy | n/a | **100%** | M53 |
| Deferred revenue reconciled to contracts | n/a | 100% | M53 |
| Fixed asset register reconciled to GL | manual | 100% | M49 |
| Budget variance explained within 3 days of close | n/a | 100% | M54 |
| Contracts with negative margin identified | unknown | 100% visible | M54 |

---

## 9. Category Delivery Sequence

```
W3   M19 General Ledger ──┐
     M20 Receivables ─────┤
     M52 Payables ────────┤
     M50 Treasury & Cash ─┴──► money is recorded, collected and paid
W4   M51 Tax & Compliance ──┐
     M53 Revenue & Settlement┴──► statutory compliance and revenue integrity
W5   M49 Fixed Assets ─────────► capital under control
W6   M54 Costing & FP&A ───────► profitability by business line
W7   M53 (marketplace settlement extension) ──► seller payouts
```

M19, M20, M52 and M50 must go live together. A ledger without receivables, payables and cash
is not a ledger.

---

## 10. Category Risks

| Risk | Impact | Mitigation | Owning Module |
|---|---|---|---|
| Marketplace VAT treatment incorrect | **Critical** — restatement, penalty | External tax opinion before Wave 7 build; decision D-03 | M51 |
| Financial history migration does not reconcile | High — opening balances wrong forever | Trial balance reconciliation signed off before cutover; one full parallel month-end | M19 |
| Branch cash controls not adopted | High — direct loss | Shift discipline is a hard system rule, not a policy; unclosed shift blocks operations | M50 / M04 |
| Revenue recognised in the wrong period | High — misstatement | Schedules generated from contracts, not entered manually; manual release requires CFO approval | M53 |
| Seller payouts wrong or late | High — marketplace collapses | 100% payout accuracy is a Wave 7 gate criterion | M53 |
| Costing never implemented, so margin stays unknown | Medium — pricing decisions made blind | M54 is P2 but its absence is visible in KPI reporting from Wave 4 | M54 |
| Statutory change mid-programme | Medium | Tax rules are configuration in a country pack, not code | M51 / M65 |

---

*Category G · 1000FiX ERP System v2.0*
