---
id: MD-039
title: Currency, FX and Rounding Standard
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance
author: Finance
reviewers: [Treasury, Tax, Enterprise Architecture, Procurement]
approver: Chief Financial Officer
content_class: C
purpose: >
  BDT as functional currency, foreign-currency handling for imports, FX source, revaluation and
  rounding policy. 05-02 DM-07 mandates monetary fields with an explicit currency, and import
  landed cost (M44) requires an FX policy or landed cost cannot be computed consistently.
traces_to: [05-02 DM-07, M19, M44, M50, MD-002, 05-06 §9]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
data_file: MD-039_Currency_FX_and_Rounding_Standard.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §1 DM-07 — Monetary fields with an explicit currency_id; never floats
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §9 — BDT primary, two decimal places, multi-currency supported
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-039 — Currency, FX and Rounding Standard

> **Never floats.** `05-02` DM-07 is explicit, and `05-06` DI-01 requires decimal arithmetic with
> no floating point in money paths. Rounding differences in a repair business compound across
> hundreds of thousands of transactions.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Finance & statutory |
| Owning module | `M19` |
| Data steward | Finance systems analyst |
| Golden source | CFO-approved FX policy |
| Refresh cadence | Annual; rates daily |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `currency_code` | char(3) | ✔ | ISO 4217 | — |  |
| `currency_name` | text(60) | ✔ |  | — |  |
| `symbol` | text(6) | ✔ | `৳` for BDT in the Bengali locale | — | `05-06` §9 |
| `decimal_places` | int | ✔ | 2 for BDT | — |  |
| `rounding_method` | enum | ✔ | half_up / half_even / down | — | **half_up for customer-facing amounts** |
| `rounding_precision` | decimal(10,4) | ✔ | 0.01 for BDT | — |  |
| `is_functional` | bool | ✔ |  | — | TRUE for BDT only |
| `fx_source` | enum |  | central_bank / bank_rate / contracted | — | Non-functional currencies |
| `fx_rate_type` | enum |  | spot / monthly_average / period_close | — | Per use |
| `revaluation_account` | fk |  | → `MD-035` | — | Unrealised gain/loss |
| `active` | bool | ✔ |  | — |  |

### 2.1 Rounding rules by context

| Context | Rule |
|---|---|
| Line amount | Round at the line, two decimals |
| Tax amount | Computed on the rounded line, then rounded |
| Invoice total | Sum of rounded lines — **never re-rounded from an unrounded total** |
| Cash payment | Rounded to the nearest BDT 1 where coinage requires; the difference posts to a rounding account |
| Report aggregation | Never re-round; aggregate the rounded values |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `currency_code` |
| Surrogate key | `currency_code` |
| Code format | ISO 4217 |
| Reuse policy | Never reused |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| FX-01 | Exactly one currency may be `is_functional` | **H** | `ERR-FX-001` |
| FX-02 | Every monetary field must carry an explicit currency (`05-02` DM-07) | **H** | `ERR-FX-002` |
| FX-03 | Float arithmetic in a money path is prohibited (`05-06` DI-01) | **H** | `ERR-FX-003` |
| FX-04 | A non-functional currency requires an FX source and a revaluation account | **H** | `ERR-FX-004` |
| FX-05 | An invoice total must equal the sum of its rounded lines | **H** | `ERR-FX-005` |
| FX-06 | An FX rate older than one business day warns for transaction use | **S** | `WRN-FX-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-035` Chart of accounts | Before — revaluation account |

| Depended on by |
|---|
| **Every monetary field in the system** · `M44` landed cost · `M50` treasury |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | CFO-approved FX policy |
| Who supplies it | CFO |
| Collection method | Policy decision; rates fed daily from the declared source |
| Known quality issues | Legacy imports are recorded at the invoice rate with no consistent policy |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 1 functional plus 3–6 foreign currencies | Low |
| SIT / UAT | BDT plus USD and CNY for import testing | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Finance systems analyst |
| Who may deactivate | CFO |
| Approval required | **CFO** — rounding changes affect every posting |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
currency_code,currency_name,symbol,decimal_places,rounding_method,rounding_precision,is_functional,fx_source,fx_rate_type,active
BDT,Bangladeshi Taka,৳,2,half_up,0.0100,TRUE,,,TRUE
USD,United States Dollar,$,2,half_up,0.0100,FALSE,central_bank,spot,TRUE
CNY,Chinese Yuan,¥,2,half_up,0.0100,FALSE,central_bank,spot,TRUE
```

---

## 10. Migration notes

Not migrated — authored.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-035_Chart_of_Accounts_Bangladesh.md`](MD-035_Chart_of_Accounts_Bangladesh.md) | Revaluation accounts |
| `M44` Import, Trade Compliance and Landed Cost | FX on imports |
| `BN-007` Date, Time, Number, Currency and Address Formats | Presentation |

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
