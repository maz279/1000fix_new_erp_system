---
id: SP-020
title: SOP — Month-End and Year-End Close
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance
author: Business Process Lead with Financial Control
reviewers: [CFO, Finance Manager, Tax Lead, External Auditor liaison, Internal Audit, Legal Counsel, CTO]
approver: Chief Financial Officer, with external verification of the statutory elements
content_class: A
purpose: >
  Statutory reporting and audit readiness depend on a repeatable close; ad-hoc close is where
  restatements originate. This SOP governs the close calendar, cut-off rules, accrual and
  provision policy, the reconciliation checklist and sign-off, and the statutory filing gates
  that sit inside the close. The close cycle today is 15–20 days against a target of 5 and a
  stretch of 3; that reduction comes from sequencing and pre-close discipline, not from software.
traces_to: [M19, M54, M51, M50, M20, M52, M53, DT-011, DT-012, DT-014, MD-035, MD-037, MD-039, MD-041, SP-004, SP-005, SP-014, SP-017, SP-019]
priority: P1
wave: W5
bilingual: yes
bn_counterpart: SP-020_SOP_Month_End_and_Year_End_Close_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §7 BRU-FIN-05, BRU-FIN-06, BRU-FIN-07; §12.4 AUT-043, AUT-044
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M19_Financial_Accounting_and_General_Ledger.md — BRU-FIN-11 journal preparer cannot approve, BRU-FIN-25 posting rights and posting-rule administration mutually exclusive
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-050 month-end close 15–20 days baseline, KPI-057 VAT returns filed on time with zero adjustment, KPI-058 tax compliance findings
    verified: 2026-08-15
    class: P1
  - source: Bangladesh Value Added Tax and Supplementary Duty Act 2012, administered by the National Board of Revenue — VAT return Mushak 9.1 filed by the 15th day of the following month, with online filing through the NBR portal and a late-filing penalty
    verified: 2026-08-15
    class: P2
  - source: ISO 9001:2015 clause 9.1.3 analysis and evaluation, and clause 7.5.3 control of documented information
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Month-End and Year-End Close

| Item | Value |
|---|---|
| SOP ID | `SP-020` |
| Process owner | Chief Financial Officer |
| Roles performing | `R27` Finance Officer · `R26` Finance Manager · Tax Lead · CFO · `R17` Inventory Manager · `R22` Account Managers (cut-off confirmations) |
| Systems used | `P03` Finance console (`UI-029`) · `M19` · `M50` · `M51` · `M54` |
| Frequency / volume | Monthly, quarterly and annually; the 30 June financial year end |
| ISO 9001 clause reference | **9.1.3** analysis and evaluation · 7.5.3 documented information · 5.3 assigned authorities |

> ⚠ **Class A — statutory content.** The VAT filing gates in §5.5 carry regulatory consequence.
> The statutory citations below are drawn from secondary sources and are marked **class P2**;
> `CG-012` requires a primary source. **Tax Lead and external verification are required before
> this file leaves `Draft`** — action O-01 in §14.

---

## 1. Purpose and Outcome

**Purpose.** To close each accounting period on a fixed calendar, with cut-off applied
consistently, every balance-sheet account reconciled, every judgement documented, and the
statutory filings made on time from the closed position.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| The period closed within the calendar | `KPI-050`, target 5 days, stretch ≤ 3 |
| No unposted entries remained in the period | `BRU-FIN-05` — hard block |
| Every balance-sheet account was reconciled and signed | Reconciliation pack |
| Every accrual and provision carries a documented basis | Judgement log |
| The VAT return was filed on time with zero adjustment | `KPI-057` |
| No journal was approved by the person who prepared it | `SOD-41` / `BRU-FIN-11` |
| The period was hard-closed and cannot be posted into | `BRU-FIN-06` |

---

## 2. Scope

**Applies to:** the monthly, quarterly and annual close for every legal entity in `MD-002` —
cut-off, accruals, provisions, reconciliations, intercompany, FX revaluation, statutory filing
preparation, and sign-off.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Daily cash reconciliation | `SP-019` |
| Payroll processing and its statutory filings | `SP-021` |
| Procure-to-pay transaction processing | `SP-017` |
| Warranty claim submission (though its accrual is closed here) | `SP-014` |
| Budgeting and forecasting | `M54` |
| The external audit itself | Managed by CFO; this SOP produces the evidence it consumes |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Cut-off | The rule determining which period a transaction belongs to |
| Soft close | Period closed to normal users; adjustments still possible by Finance |
| Hard close | Period locked; reopening requires CFO approval and is logged (`BRU-FIN-06`) |
| Accrual | Expense incurred but not invoiced |
| Provision | An estimated liability where timing or amount is uncertain |
| GRNI | Goods received, not invoiced |
| Judgement log | The record of every estimate, its basis and its preparer |
| Mushak 9.1 | The Bangladesh VAT return form (`DT-014`) |
| Close calendar | The dated task sequence, published before the period begins |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Published close calendar | CFO | Issued before the period begins, not during the close |
| All branch shifts closed | `SP-019` | An unclosed shift leaves cash unaccounted (`BRU-FIN-10`) |
| Inventory position | `SP-018` | Cycle counts current; year-end full count completed |
| Open POs and GRNs | `SP-017` | GRNI computable |
| Warranty claim position | `SP-014` | Unremitted claims accrued |
| Contract billing complete | `SP-015` | Deferred revenue schedule current |
| FX rates | `MD-039` | Official period-end rate loaded (`BRU-FIN-07`) |
| Fiscal calendar | `MD-041` | Period boundaries and the 30 June year end |
| Chart of accounts current | `MD-035` | No unmapped postings |

---

## 5. Procedure

### 5.1 Pre-close (working days −5 to −1)

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 1 | R26 | Publish the close calendar with named owners and dated tasks | `P03` | Calendar issued |
| 2 | R27 | Clear the exception queues: unmatched invoices, unallocated receipts, suspense balances | `P03` | Exception clearance |
| 3 | R22 | Confirm revenue cut-off with account managers: which delivered work is billable this period | `P03` | Cut-off confirmations |
| 4 | R17 | Confirm inventory cut-off: goods in transit, GRNI, quarantine | `M15` | Inventory cut-off |
| 5 | R27 | Chase missing supplier invoices for the accrual rather than accruing blind | `M52` | Invoice chase log |

### 5.2 Close — transactional (days 1–2)

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 6 | R26 | Soft-close the period to normal users | `M19` | Soft close |
| 7 | System | Run the close checklist: accruals, prepayment amortisation, FX revaluation, recurring journals (`AUT-043`) | `M19` | Automated postings |
| 8 | R27 | Post manual accruals with a documented basis; **the preparer never approves** (`SOD-41`, `BRU-FIN-11`) | `M19` | Journals with approval |
| 9 | R27 | Revalue foreign-currency balances at the official period-end rate (`BRU-FIN-07`) | `MD-039` | Revaluation posting |
| 10 | R27 | Recognise deferred revenue per the schedule; manual release requires CFO approval (`BRU-BIL-06`) | `M53` | Recognition posting |

### 5.3 Reconciliation (days 2–3)

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 11 | R27 | Reconcile every bank account; auto-match, investigate exceptions (`AUT-044`) | `M50` | Bank reconciliations |
| 12 | R27 | Reconcile AR to the sub-ledger and age it; confirm the bad-debt provision basis | `M20` | AR reconciliation |
| 13 | R27 | Reconcile AP and GRNI | `M52` | AP reconciliation |
| 14 | R17 + R27 | Reconcile inventory to the ledger; investigate differences before adjusting | `M15` | Inventory reconciliation |
| 15 | R27 | Reconcile the warranty claim receivable; accrue unremitted approved claims | `SP-014` | Warranty reconciliation |
| 16 | R27 | Reconcile intercompany balances between entities; they must agree before either closes | `MD-002` | Intercompany agreement |
| 17 | R27 | Reconcile tax accounts: output VAT, input VAT, TDS/VDS payable | `M51` | Tax reconciliations |
| 18 | R26 | Review every reconciliation; sign each. **An unsigned reconciliation is not a reconciliation** | `P03` | Signed pack |

### 5.4 Review and sign-off (day 3–4)

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 19 | R26 | Produce the trial balance and the variance analysis against budget and prior period | `M54` | Variance pack |
| 20 | R26 | Investigate every variance above the materiality threshold and document the explanation | `P03` | Variance explanations |
| 21 | CFO | Review the judgement log — every accrual, provision and estimate with its basis and preparer | `P03` | Judgement log reviewed |
| 22 | CFO | Approve the close | `P03` | Close approval |
| 23 | R26 | **Hard-close** the period. No posting is possible thereafter without CFO-approved reopening, which is logged (`BRU-FIN-06`) | `M19` | Hard close |

### 5.5 Statutory filing gates

| Step | Who | Action | Governed by | Evidence produced |
|---:|---|---|---|---|
| 24 | Tax Lead | Produce the statutory sales register from issued Mushak 6.3 challans | `DT-011` | Mushak 6.2 |
| 25 | Tax Lead | Produce the statutory purchase register from received challans | `DT-012` | Mushak 6.1 |
| 26 | Tax Lead | Reconcile the registers to the ledger. **A difference is resolved before filing, never after** | `M51` | Reconciliation |
| 27 | Tax Lead | Prepare the VAT return pack with its supporting schedules | `DT-014` | Mushak 9.1 pack |
| 28 | CFO | Review and approve the return | `SP-004` | Approval |
| 29 | Tax Lead | File through the NBR online portal **by the statutory date**, and retain the acknowledgement | `DT-014` | Filing acknowledgement |
| 30 | Tax Lead | Remit the tax due; match the payment to the filing | `M50` | Payment record |
| 31 | Tax Lead | Confirm VDS certificates (`DT-013`) were issued for every deduction in the period | `SP-017` | Certificate register |

> **Statutory dates are not set by this SOP.** They are set by the applicable instrument and are
> recorded in `MD-041` with a verification date. The close calendar is built backwards from them
> with the escalation in `SP-005` SC-E10 firing at statutory date − 3 days.

### 5.6 Year-end additions (30 June)

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 32 | R17 | Full physical inventory count with Internal Audit observation | `SP-018` §5.5 |
| 33 | R27 | Fixed-asset verification, depreciation review and impairment assessment | `MD-044` |
| 34 | R26 | Provision review: bad debt, warranty obligation, stock obsolescence, legal, employee benefits | Judgement log |
| 35 | CFO | External audit pack assembly and the audit timetable | External auditor |
| 36 | CFO | Statutory accounts preparation, board approval and filing | Legal Counsel |
| 37 | R26 | Roll forward: open the new year, carry balances, reset the close calendar | `M19` |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 2 | Exception queues not clear by day −1 | Escalate; do not carry unresolved exceptions into the close, they become audit findings | R26 → CFO |
| 5 | Supplier invoice unavailable | Accrue on the PO and GRN value with the basis documented, not on an estimate | R26 |
| 6 | Operations still transacting into the period | Soft close is enforced by the system, not by request | R26 |
| 8 | The preparer is the only qualified person available to approve | **The journal waits.** `BRU-FIN-11` is a hard block at any value | R26 or CFO |
| 11 | Bank balance does not reconcile | Do not force it with a plug. An unexplained difference stays visible in suspense with an owner | R26 |
| 14 | Inventory difference above the threshold | Investigate before adjusting (`SP-018` §5.4); an adjustment posted without investigation conceals the cause | R17 + CFO |
| 16 | Intercompany balances disagree | Neither entity closes until they agree | R26 → CFO |
| 20 | Variance cannot be explained | Escalate. "Timing" is not an explanation unless the timing item is identified | CFO |
| 22 | A material judgement is unsupported | The close does not complete. Documented judgement is the difference between an estimate and a guess | CFO |
| 23 | A late adjustment is needed after hard close | Reopening requires CFO approval and is logged. **The same person may not reopen and post** (`SOD-43`) | CFO |
| 26 | Statutory register does not reconcile to the ledger | **Do not file.** Resolve first; a filed return that disagrees with the books is the finding, not the difference | CFO + Tax Lead |
| 29 | Filing deadline at risk | Escalate at statutory date − 3 (`SP-005` SC-E10); file on the best available position and amend if the instrument permits, with legal advice | CFO |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Manual journal entry | ≤ BDT 100,000 | R26 Finance Manager (`SP-004` A-33) | CFO |
| Manual journal entry | > BDT 100,000 | CFO (`SP-004` A-34) | CEO |
| Journal preparer approving own journal | **None — hard block, any value** (`BRU-FIN-11`, `SOD-41`) | — | — |
| Reopen a hard-closed period | Any | CFO, logged (`SP-004` A-32, `BRU-FIN-06`) | Board |
| Reopen a period + post into it | **Incompatible** (`SOD-43`) | Different people | — |
| Manual deferred revenue release | Any | CFO (`SP-004` A-36, `BRU-BIL-06`) | — |
| Bad-debt write-off | ≤ 50,000 / > 50,000 / > 500,000 | R26 / CFO / CFO + CEO (`SP-004` A-30, A-31) | Board |
| Approve the VAT return | Any | CFO, on the Tax Lead's preparation | CEO |
| Close approval | Any | CFO (`SP-004` — no delegation below CFO) | Board |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Close task overdue | Escalate daily, then to CFO at 2 days (`SP-005` SC-E9) | R26 → CFO | Close tracker |
| Unposted entries block the close | Identify the owner and clear; `BRU-FIN-05` will not be overridden | R26 | Exception log |
| Suspense balance carried into the next period | Requires CFO acknowledgement and a named owner with a clearance date | CFO | Suspense register |
| Statutory filing at risk | Escalate at statutory date − 3 days | CFO, Tax Lead (`SP-005` SC-E10) | Filing risk log |
| Filing made and later found incorrect | Take legal and tax advice before amending; do not amend silently | CFO, Legal, Tax | Tax exception |
| Material error found after hard close | Assess materiality; correct in the current period or restate on advice | CFO + external auditor | Restatement record |
| Ledger and statutory register disagree | Filing is held until reconciled | CFO | Reconciliation record |
| System unavailable during the close window | Fallback in §9; the calendar is re-baselined and the statutory date is not | R26, CTO | Close exception |
| External auditor raises a control finding | Route to `SP-029` as a CAPA, not as a private correction | Quality Manager, CFO | CAPA |

---

## 9. Manual Fallback

Cross-reference `OP-014`.

| Step | Manual action |
|---|---|
| 1 | The close calendar and the reconciliation pack exist as controlled spreadsheets held by Finance, independent of the ERP |
| 2 | Reconciliations are performed from bank statements, sub-ledger extracts and the last available trial balance |
| 3 | Journals are prepared on the **manual journal voucher form**, sequentially numbered, prepared and approved by different people, and entered on restoration |
| 4 | **Statutory filing proceeds regardless of system availability.** The return is prepared from the registers and the manual reconciliation. The statutory date does not move because a system is down |
| 5 | **Back-enter every manual journal within 48 hours**, preserving voucher numbers and dates |
| 6 | CFO signs the manual close pack; the external auditor is informed that a manual close occurred |

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Period cannot close with unposted entries | Preventive (`BRU-FIN-05`) | Per close | Hard block |
| Hard-closed period cannot be posted into | Preventive (`BRU-FIN-06`) | Continuous | Hard block |
| Journal preparer cannot approve | Preventive (`BRU-FIN-11`, `SOD-41`) | Per journal | Hard block |
| Posting rights and posting-rule administration mutually exclusive | Preventive (`BRU-FIN-25`, `SOD-42`) | At assignment | Hard block |
| Reopen and post separated | Preventive (`SOD-43`) | Per reopening | Hard block |
| FX revalued at the official period-end rate | Preventive (`BRU-FIN-07`) | Per close | Computed |
| Every balance-sheet account reconciled and signed | Detective | Monthly | Reconciliation pack |
| Judgement log reviewed by CFO | Detective | Monthly | Signed log |
| Statutory register to ledger reconciliation | Preventive | Per filing | Reconciliation |
| Reopening log reviewed | Detective | Quarterly | Internal Audit |
| Close cycle time | Detective | Monthly | `KPI-050` |
| Filing timeliness and adjustment | Detective | Per filing | `KPI-057`, `KPI-058` |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Prepare a journal | Approve it (`SOD-41`) | Hard block, any value | **None. The journal waits for an approver** |
| Hold posting rights | Administer posting rules (`SOD-42`) | Hard block at assignment | CTO administers configuration; Finance posts |
| Reopen a period | Post into it (`SOD-43`) | Hard block | — |
| Perform the inventory count | Approve the adjustment (`SOD-05`) | Hard block | Adjustment approval sits with R17 and, above band, CFO |
| Prepare the VAT return | Approve it | Hard block | Tax Lead prepares; CFO approves |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-050` | Month-end close cycle | 15–20 days | 5 days; stretch ≤ 3 |
| `KPI-051` | Bank reconciliation auto-match | manual | 90%; stretch 94% |
| `KPI-057` | VAT returns filed on time with zero adjustment | manual | 100% |
| `KPI-058` | Tax compliance findings | unmeasured | **Zero** |
| `KPI-052` | Days sales outstanding | unmeasured | 38; stretch < 32 |
| Reconciliations signed on time | Completeness of the signed pack | untracked | 100% |
| Period reopenings | Count per year | untracked | Trend to zero |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-011` Sales Register Mushak 6.2 · `DT-012` Purchase Register Mushak 6.1 | Steps 24–25 |
| `DT-014` VAT Return Pack Mushak 9.1 | Steps 27–29 |
| `DT-013` VDS Certificate Mushak 6.6 | Step 31 |
| `UI-029` Workspace — Finance Console Copy | The screens used |
| [`SP-019_SOP_Cash_Collection_and_Banking.md`](SP-019_SOP_Cash_Collection_and_Banking.md) | Daily cash feeding the close |
| [`SP-017_SOP_Procurement_to_Payment.md`](SP-017_SOP_Procurement_to_Payment.md) | GRNI and AP |
| [`SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md`](SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md) | Warranty receivable accrual |
| [`SP-021_SOP_Payroll_Run_and_Statutory_Filing.md`](SP-021_SOP_Payroll_Run_and_Statutory_Filing.md) | Payroll postings and its own filings |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-035_Chart_of_Accounts_Bangladesh.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-035_Chart_of_Accounts_Bangladesh.md) | Account structure |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md) | Tax codes and Mushak mapping |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md) | Period boundaries and statutory dates |
| `TR-014` Course Pack — Finance Officer and Manager | Trains this SOP |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | CFO (pending) — statutory elements pending external verification |

**Open items**

| # | Item | Owner | Needed by |
|---|---|---|---|
| O-01 | **Verify every statutory reference in §5.5 against the enacted instrument.** The VAT return deadline cited here is drawn from secondary commentary (class **P2**) and `CG-012` requires a primary source for a Class A file. The applicable return frequency (monthly or quarterly) for each 1000FiX legal entity must also be confirmed | Tax Lead + external verifier | **Before `Approved`** |
| O-02 | Record the confirmed statutory dates in `MD-041` with their verification date, so that the close calendar is built from a single source | Tax Lead | Before W5 |
| O-03 | Confirm materiality thresholds for variance investigation with the external auditor | CFO | Before W5 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] Close calendar built backwards from statutory dates, with escalation before the deadline
- [x] "Do not file an unreconciled return" stated at the decision point
- [x] Journal preparer/approver separation stated as having **no** compensating control
- [x] Manual fallback preserves the statutory date as immovable
- [x] §7 reconciles with `SP-004`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **O-01 statutory citations verified against the enacted instrument — outstanding; blocks `Approved` for this Class A file (`CG-007`, `CG-012`)**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approver recorded with external verification — **pending CFO** (Class A: external verification is the gating control, `CG-002` §5.1)
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
