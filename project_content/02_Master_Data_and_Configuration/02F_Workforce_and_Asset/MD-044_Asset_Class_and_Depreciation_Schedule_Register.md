---
id: MD-044
title: Asset Class and Depreciation Schedule Register
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance
author: Finance with Facilities
reviewers: [Tax, Audit, Facilities, Quality]
approver: Chief Financial Officer
content_class: C
purpose: >
  Fixed-asset classes, useful lives, depreciation methods and capitalisation thresholds. M49 cannot
  post depreciation and M45 cannot value test equipment without it; book and tax depreciation may
  differ and both must be held.
traces_to: [M49, M45, M46, M47, MD-035, MD-036, MD-046]
priority: P2
wave: W5
bilingual: no
bn_counterpart: n/a
data_file: MD-044_Asset_Class_and_Depreciation_Schedule_Register.csv
effective_dated: yes
sources:
  - source: 1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M49_Fixed_Assets_and_Capital_Investment.md
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-044 — Asset Class and Depreciation Schedule Register

> Book depreciation and tax depreciation are different calculations on the same asset. Holding
> only one produces a deferred-tax error that compounds annually.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Workforce & asset |
| Owning module | `M49` |
| Data steward | Fixed asset analyst |
| Golden source | CFO-approved capitalisation policy, adviser-reviewed for tax depreciation |
| Refresh cadence | Annual |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `asset_class_code` | char(8) | ✔ | `AC-nnn`, permanent | — |  |
| `class_name` | text(120) | ✔ |  | — |  |
| `parent_class_code` | fk |  | Self-reference | — |  |
| `capitalisation_threshold_bdt` | decimal(14,2) | ✔ | Below this, expensed | — |  |
| `book_useful_life_months` | int | ✔ |  | — |  |
| `book_method` | enum | ✔ | straight_line / reducing_balance | — |  |
| `book_residual_pct` | decimal(5,2) | ✔ |  | — |  |
| `tax_rate_pct` | decimal(5,2) |  | Tax depreciation rate | — | May differ from book |
| `tax_method` | enum |  |  | — |  |
| `asset_account_code` | fk | ✔ | → `MD-035` | — |  |
| `depreciation_account_code` | fk | ✔ | → `MD-035` | — |  |
| `accumulated_account_code` | fk | ✔ | → `MD-035` | — |  |
| `requires_calibration` | bool | ✔ |  | — | → `MD-046` |
| `requires_insurance` | bool | ✔ |  | — |  |
| `effective_from` | date | ✔ |  | — |  |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `class_name` |
| Surrogate key | `asset_class_code` |
| Code format | `AC-nnn` |
| Reuse policy | Never reused; asset history references it |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| AST-01 | Expenditure below the capitalisation threshold may not be capitalised | **H** | `ERR-AST-001` |
| AST-02 | Every class must have asset, depreciation and accumulated accounts | **H** | `ERR-AST-002` |
| AST-03 | Changing a useful life on a class with depreciating assets requires CFO approval and prospective treatment | **A** | `ERR-AST-003` |
| AST-04 | `requires_calibration` TRUE requires a matching entry in `MD-046` | **H** | `ERR-AST-004` |
| AST-05 | A class with no tax rate warns — deferred tax cannot be computed | **S** | `WRN-AST-005` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-035` Chart of accounts | **Before** |
| `MD-036` Dimensions | Before |

| Depended on by |
|---|
| `M49` fixed assets · `M45` test equipment · `M46` fleet · `M47` facilities · `MD-046` calibration |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | CFO-approved capitalisation policy |
| Who supplies it | CFO with the external adviser for tax rates |
| Collection method | Policy decision plus adviser review of tax depreciation |
| Known quality issues | Legacy fixed-asset register is a spreadsheet with inconsistent lives |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 30–60 classes | Low |
| SIT / UAT | 20 across all methods | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Fixed asset analyst |
| Who may deactivate | CFO |
| Approval required | **CFO**; adviser for tax rates |
| Effective dating | **Yes** |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
asset_class_code,class_name,capitalisation_threshold_bdt,book_useful_life_months,book_method,book_residual_pct,asset_account_code,depreciation_account_code,requires_calibration,effective_from,active
AC-010,IT equipment,25000.00,36,straight_line,5.00,1-50-10-010,6-40-10-010,FALSE,2026-07-01,TRUE
AC-020,Test and repair equipment,25000.00,60,straight_line,10.00,1-50-10-020,6-40-10-020,TRUE,2026-07-01,TRUE
AC-030,Motor vehicles,100000.00,84,reducing_balance,15.00,1-50-10-030,6-40-10-030,FALSE,2026-07-01,TRUE
```

---

## 10. Migration notes

`DM-008`. Assets migrate at net book value with accumulated depreciation, and must reconcile to the ledger.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-046_Test_Equipment_and_Calibration_Master.md`](MD-046_Test_Equipment_and_Calibration_Master.md) | Calibrated assets |
| [`MD-045_Fleet_and_Vehicle_Master.md`](MD-045_Fleet_and_Vehicle_Master.md) | Vehicles |
| `M49` Fixed Assets and Capital Investment | The implementing module |

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
