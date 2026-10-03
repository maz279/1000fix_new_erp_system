---
id: MD-038
title: Payment Method, Term and Bank Master
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Treasury
author: Treasury with Finance
reviewers: [Finance, Security, Platform Engineering, Procurement]
approver: Chief Financial Officer
content_class: C
purpose: >
  Payment methods, terms, bank accounts and settlement and reconciliation keys. Nine payment
  integrations settle into accounts that must be pre-defined for automated reconciliation, and a
  mismatched settlement key means manual reconciliation forever.
traces_to: [M50, M20, M52, 05-03 INT-001..009, MD-002, MD-035, UI-039]
priority: P0
wave: W3
bilingual: no
bn_counterpart: n/a
data_file: MD-038_Payment_Method_Term_and_Bank_Master.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03 §2.1 payments — bKash, Nagad, SSLCOMMERZ, Rocket, BEFTN, bank statement import and others
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-038 — Payment Method, Term and Bank Master

> Nine payment integrations, one reconciliation problem. The settlement key defined here is what
> matches a gateway payout to our receipts; get it wrong and finance reconciles by hand.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Finance & statutory |
| Owning module | `M50` |
| Data steward | Treasury analyst |
| Golden source | Bank mandates and executed gateway agreements |
| Refresh cadence | On any new method, bank or gateway; annual review |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `method_code` | char(8) | ✔ | `PM-nnn`, permanent | — |  |
| `method_name` | text(80) | ✔ | Brand name as registered — bKash, Nagad | — | Do-not-translate (`BN-004`) |
| `method_class` | enum | ✔ | cash / mobile_money / card / bank_transfer / cheque / wallet_credit / bnpl | — |  |
| `integration_ref` | fk |  | → `05-03` `INT-nnn` | — |  |
| `gl_account_code` | fk | ✔ | → `MD-035` | — | Clearing account |
| `settlement_bank_account` | fk |  | → §2.1 | — |  |
| `settlement_lag_days` | int | ✔ |  | — | Gateway payout delay |
| `settlement_key_field` | text(60) | ✔ | **The field matched on reconciliation** | — |  |
| `mdr_pct` | decimal(5,3) |  | Merchant discount rate | — | Cost of acceptance |
| `refund_supported` | bool | ✔ |  | — |  |
| `refund_window_days` | int |  |  | — |  |
| `is_customer_facing` | bool | ✔ |  | — | Offered at `P01` checkout |
| `requires_otp` | bool | ✔ |  | — |  |
| `active` | bool | ✔ |  | — |  |

### 2.1 Bank account sub-register

`bank_account_code` · `entity_code` · `bank_name` · `branch_name` · `account_no` (**S3**) ·
`routing_no` · `account_type` · `currency` · `gl_account_code` · `is_beftn_enabled` ·
`statement_import_format` · `active`

### 2.2 Payment terms sub-register

`term_code` · `term_name` · `days_net` · `discount_pct` · `discount_days` · `applies_to`
(customer / vendor) · `active`

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `method_name` |
| Surrogate key | `method_code` |
| Code format | `PM-nnn` |
| Reuse policy | Never reused |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| PAY-01 | Every method must have a clearing account and a settlement key | **H** | `ERR-PAY-001` |
| PAY-02 | A customer-facing method must have an active integration or be cash | **H** | `ERR-PAY-002` |
| PAY-03 | Bank account numbers are S3 and Bangladesh-resident (`NFR-086`) | **H** | `ERR-PAY-003` |
| PAY-04 | A change to a settlement bank account requires CFO approval and dual control | **H** | `ERR-PAY-004` |
| PAY-05 | Refund is blocked where `refund_supported` is FALSE | **H** | `ERR-PAY-005` |
| PAY-06 | Unreconciled settlements older than the lag plus 2 days warn to Treasury | **S** | `WRN-PAY-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-002` Legal entity | Before |
| `MD-035` Chart of accounts | **Before** |

| Depended on by |
|---|
| `M20` receivables · `M50` treasury · `M52` payables · `UI-039` checkout copy · `AP-009` gateway runbooks |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Bank mandates and executed gateway agreements |
| Who supplies it | Treasury with Finance |
| Collection method | Agreement review; settlement key confirmed by a test settlement before go-live |
| Known quality issues | Legacy reconciliation is manual; settlement keys have never been formalised |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 15–30 methods; 10–25 bank accounts; 10–20 terms | Low |
| SIT / UAT | All methods — payment paths are tested exhaustively | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Treasury analyst |
| Who may deactivate | CFO |
| Approval required | **CFO, dual control for bank details** |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
method_code,method_name,method_class,integration_ref,gl_account_code,settlement_lag_days,settlement_key_field,mdr_pct,refund_supported,is_customer_facing,requires_otp,active
PM-001,Cash,cash,,1-10-10-010,0,receipt_no,0.000,TRUE,TRUE,FALSE,TRUE
PM-010,bKash,mobile_money,INT-001,1-10-20-010,1,trx_id,1.500,TRUE,TRUE,TRUE,TRUE
PM-011,Nagad,mobile_money,INT-002,1-10-20-020,1,payment_ref,1.400,TRUE,TRUE,TRUE,TRUE
PM-020,Card via SSLCOMMERZ,card,INT-003,1-10-20-030,2,val_id,2.300,TRUE,TRUE,TRUE,TRUE
```

---

## 10. Migration notes

`DM-008`. Open receipts must be matched to a method at cutover.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-035_Chart_of_Accounts_Bangladesh.md`](MD-035_Chart_of_Accounts_Bangladesh.md) | Clearing accounts |
| `AP-009` Payment Gateway Integration Runbook Content | Operational procedures |
| `UI-039` Payment and Checkout Flow Copy | Customer-facing method names |
| `M50` Treasury, Cash and Banking | The implementing module |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Master_Data_Specification.md`
- [x] Record structure names column, type, required flag, constraint and Bengali requirement
- [x] Keys, code format and reuse prohibition stated
- [x] Every validation rule carries a class and an error message ID
- [x] Load dependencies stated and reconciled with `MD-048`
- [x] Golden source and acquisition method named
- [x] Volumes stated per environment
- [x] Sample rows included and parse as CSV
- [x] Archive rule states records are archived, never deleted (`05-02` DM-06)
- [x] All internal links resolve
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
