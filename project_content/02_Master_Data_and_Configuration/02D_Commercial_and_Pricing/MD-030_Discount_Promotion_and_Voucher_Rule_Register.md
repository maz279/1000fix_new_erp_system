---
id: MD-030
title: Discount, Promotion and Voucher Rule Register
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Commercial with Finance
author: Commercial with Finance
reviewers: [Finance, Marketing, Legal, Service Operations]
approver: Chief Commercial Officer
content_class: C
purpose: >
  Discount ceilings by role, stacking rules, voucher types, campaign codes and approval thresholds.
  Uncontrolled discounting is the fastest margin leak in a service business; the rules must exist
  before the UI exposes a discount field.
traces_to: [M11, M35, M10, MD-029, SP-004, VB-010]
priority: P1
wave: W2
bilingual: no
bn_counterpart: n/a
data_file: MD-030_Discount_Promotion_and_Voucher_Rule_Register.csv
effective_dated: yes
sources:
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M11_Pricing_Rate_Cards_and_Dynamic_Pricing.md
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-030 — Discount, Promotion and Voucher Rule Register

> Every discount is margin given away. The question is only whether it was given away by a rule
> or by whoever happened to be at the counter.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Commercial & pricing |
| Owning module | `M11` |
| Data steward | Pricing analyst |
| Golden source | CCO and CFO joint approval |
| Refresh cadence | Per campaign; register reviewed quarterly |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `rule_code` | char(9) | ✔ | `DSC-nnnnn`, permanent | — |  |
| `rule_type` | enum | ✔ | role_ceiling / promotion / voucher / loyalty_benefit / goodwill | — |  |
| `name` | text(120) | ✔ | Registered name (`VB-010`) for customer-visible promotions | — |  |
| `applies_to` | enum | ✔ | item / category / order / labour_only / parts_only | — |  |
| `scope_codes` | multi-fk |  | → `MD-019` or category | — |  |
| `max_discount_pct` | decimal(5,2) | ✔ |  | — |  |
| `max_discount_bdt` | decimal(14,2) |  | Absolute cap | — |  |
| `role_code` | fk |  | → `MD-009`; for role_ceiling | — | **Who may grant this much** |
| `approval_role_code` | fk |  | → `MD-009` | — | Who approves beyond the ceiling |
| `stackable` | bool | ✔ |  | — | May combine with another rule |
| `stack_group` | text(20) |  | Rules in one group are mutually exclusive | — |  |
| `voucher_code_pattern` | text(40) |  | Vouchers only | — |  |
| `usage_limit_per_customer` | int |  |  | — |  |
| `effective_from` | date | ✔ |  | — |  |
| `effective_to` | date |  |  | — |  |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `rule_type` + `name` |
| Surrogate key | `rule_code` |
| Code format | `DSC-nnnnn` |
| Reuse policy | Never reused |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| DSC-01 | A discount above the granting role's ceiling is blocked pending the named approver | **H** | `ERR-DSC-001` |
| DSC-02 | Non-stackable rules in the same `stack_group` may not combine | **H** | `ERR-DSC-002` |
| DSC-03 | Total discount may never take the price below `min_price` on `MD-029` | **H** | `ERR-DSC-003` |
| DSC-04 | A voucher may not exceed `usage_limit_per_customer` | **H** | `ERR-DSC-004` |
| DSC-05 | Goodwill discounts require a reason code (`MD-026`) and are reported monthly | **A** | `ERR-DSC-005` |
| DSC-06 | A rule granting more than 25% warns to Finance regardless of role | **S** | `WRN-DSC-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-029` Price lists | **Before** |
| `MD-009` Roles | Before |
| `MD-026` Reason codes | Before |

| Depended on by |
|---|
| `M11` pricing · `M35` campaigns · `M10` loyalty benefits · `SP-004` approval matrix · `UI-039` checkout copy |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Commercial and Finance joint decision |
| Who supplies it | CCO and CFO |
| Collection method | Workshop; ceilings modelled against historical discount data where available |
| Known quality issues | No discount ceilings exist today; discretion sits with branch managers informally |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 60–200 rules | Low |
| SIT / UAT | 40 across all rule types | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Pricing analyst |
| Who may deactivate | CCO |
| Approval required | **CCO and CFO jointly** for any ceiling change |
| Effective dating | **Yes** |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
rule_code,rule_type,name,applies_to,max_discount_pct,role_code,approval_role_code,stackable,stack_group,effective_from,active
DSC-00101,role_ceiling,Service agent discretion,order,5.00,R08,R06,FALSE,ROLE,2026-07-01,TRUE
DSC-00102,role_ceiling,Branch manager discretion,order,15.00,R06,R05,FALSE,ROLE,2026-07-01,TRUE
DSC-00301,loyalty_benefit,Privilege Gold service discount,labour_only,50.00,,,TRUE,LOYALTY,2026-07-01,TRUE
```

---

## 10. Migration notes

Not migrated — authored.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-029_Price_List_and_Rate_Card_Seed.md`](MD-029_Price_List_and_Rate_Card_Seed.md) | Price floors |
| [`MD-034_Loyalty_Tier_Point_and_Benefit_Register.md`](MD-034_Loyalty_Tier_Point_and_Benefit_Register.md) | Loyalty benefits |
| `SP-004` Approval Matrix and Delegation of Authority | Approval routing |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Chief Commercial Officer (pending) |

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
