---
id: MD-035
title: Chart of Accounts (Bangladesh)
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance
author: Finance with external tax adviser
reviewers: [Tax, External adviser, Audit, Enterprise Architecture]
approver: Chief Financial Officer
content_class: A
purpose: >
  The full chart of accounts aligned to Bangladesh statutory reporting, with account types, control
  accounts and posting rules. No transaction can post until the CoA exists; it is the first
  configuration object of any ERP finance go-live.
traces_to: [M19, M51, M54, MD-002, MD-036, MD-037, DT-014, RP-009]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
data_file: MD-035_Chart_of_Accounts_Bangladesh.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M19_Financial_Accounting_and_General_Ledger.md
    verified: 2026-08-15
    class: P1
  - source: Bangladesh statutory financial reporting requirements — to be verified against the enacted framework by the external adviser at gate G6
    verified: 2026-08-15
    class: P2
supersedes: none
review_due: 2027-02-15
---

# MD-035 — Chart of Accounts (Bangladesh)

> ⚠ **Class A — statutory.** Gate **G6** applies: this file is verified against the enacted
> reporting framework by a named external adviser before it may be approved (`CG-007` §3.6,
> unwaivable under `WV-02`).
>
> **Nothing in the finance stream can start until this loads.**

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Finance & statutory |
| Owning module | `M19` |
| Data steward | Finance systems analyst |
| Golden source | CFO-approved chart, verified against statutory reporting requirements |
| Refresh cadence | Annual; on any statutory reporting change |
| Environments | Dev · SIT · UAT · Prod |
| Content class | A — Statutory |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `account_code` | char(10) | ✔ | Structured — see §3 | — |  |
| `entity_code` | fk | ✔ | → `MD-002` | — | Chart is per entity |
| `account_name` | text(160) | ✔ |  | — |  |
| `account_type` | enum | ✔ | asset / liability / equity / income / expense | — |  |
| `account_subtype` | enum | ✔ | current_asset / fixed_asset / receivable / payable / bank / cash / stock / tax / revenue / cogs / opex / payroll | — | Drives statutory grouping |
| `parent_account_code` | fk |  | Self-reference; max depth 4 | — |  |
| `is_postable` | bool | ✔ |  | — | Only leaves are postable |
| `is_control_account` | bool | ✔ |  | — | Reconciled to a subledger |
| `control_subledger` | enum |  | receivable / payable / stock / fixed_asset / tax | — | Required when control |
| `requires_dimension` | multi-enum | ✔ | cost_centre / business_line / branch | — | → `MD-036` (`05-02` DM-03) |
| `currency_restriction` | char(3) |  |  | — | Null = any |
| `reconciliation_required` | bool | ✔ |  | — |  |
| `statutory_group` | text(80) | ✔ | Line in the statutory report | — | **Verified at G6** |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `entity_code` + `account_code` |
| Surrogate key | `account_code` |
| Code format | Four-block structure: `T-GG-SS-NNN` — type, group, subgroup, sequence |
| Reuse policy | **Never reused.** Postings five years old reference it and VAT records are retained at least five years |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| COA-01 | Only leaf accounts may be postable | **H** | `ERR-COA-001` |
| COA-02 | A control account may not be posted to directly — only through its subledger | **H** | `ERR-COA-002` |
| COA-03 | Every posting must carry the dimensions in `requires_dimension` (`05-02` DM-03) | **H** | `ERR-COA-003` |
| COA-04 | An account may not be archived with a non-zero balance or open items | **H** | `ERR-COA-004` |
| COA-05 | `statutory_group` is mandatory and verified at G6 | **H** | `ERR-COA-005` |
| COA-06 | Changing an account type after any posting is prohibited | **H** | `ERR-COA-006` |
| COA-07 | A postable account unused for two years warns for review | **S** | `WRN-COA-007` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-002` Legal entity | **Before** |
| `MD-036` Dimensions | Before or same load |

| Depended on by |
|---|
| `MD-037` tax codes · `MD-043` payroll elements · `MD-044` asset classes · **every financial posting in the system** |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | CFO-approved chart, drafted against statutory reporting requirements |
| Who supplies it | CFO with the external tax adviser |
| Collection method | Drafted, then **verified against the enacted framework by the external adviser (G6)** |
| Known quality issues | The legacy chart is not aligned to a dimension model and mixes cost centres into account codes |
| Cleansing rules | `DM-011`. **Opening balances must reconcile exactly** before go-live (`DM-008`, `DM-013`) |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 600–1,200 accounts per entity | Low |
| SIT / UAT | Full chart — finance testing requires it | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Finance systems analyst |
| Who may deactivate | CFO, after COA-04 |
| Approval required | **CFO**; external adviser re-verification for any `statutory_group` change |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
account_code,entity_code,account_name,account_type,account_subtype,is_postable,is_control_account,control_subledger,requires_dimension,statutory_group,active
1-10-10-000,EN-01,Cash and cash equivalents,asset,cash,FALSE,FALSE,,branch,Current assets,TRUE
1-10-10-010,EN-01,Cash in hand - branch,asset,cash,TRUE,FALSE,,branch;cost_centre,Current assets,TRUE
1-20-10-000,EN-01,Trade receivables,asset,receivable,FALSE,TRUE,receivable,,Current assets,TRUE
4-10-10-010,EN-01,Service revenue - out of warranty repair,income,revenue,TRUE,FALSE,,cost_centre;business_line;branch,Revenue,TRUE
2-30-10-010,EN-01,VAT payable - output,liability,tax,TRUE,TRUE,tax,,Current liabilities,TRUE
```

---

## 10. Migration notes

`DM-008` finance migration. Legacy accounts are **mapped**, not carried across; opening balances load against the new chart and must balance exactly.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-036_Cost_Centre_Business_Line_and_Dimension_Register.md`](MD-036_Cost_Centre_Business_Line_and_Dimension_Register.md) | Required dimensions |
| [`MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md`](MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md) | Tax account binding |
| `RP-009` Statutory and Regulatory Report Format Register | Where `statutory_group` is consumed |
| `M19` Financial Accounting and General Ledger | The implementing module |

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
- [ ] G6 statutory verification against the enacted instrument — **outstanding, unwaivable (`WV-02`)**
- [ ] `statutory_pin` fiscal year confirmed (`CG-006` §4.1)
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
