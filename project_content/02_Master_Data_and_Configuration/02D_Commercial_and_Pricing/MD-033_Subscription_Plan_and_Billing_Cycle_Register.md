---
id: MD-033
title: Subscription Plan and Billing Cycle Register
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
reviewers: [Finance, Legal, Revenue, Account Management]
approver: Chief Financial Officer
content_class: C
purpose: >
  Subscription products, cycles, proration, dunning ladders and pause and resume rules. M39
  recurring revenue cannot be configured or revenue-recognised without plan definitions, and
  proration errors compound silently across every renewal.
traces_to: [M39, M53, M20, MD-019, MD-029, MD-032, DT-018]
priority: P2
wave: W4
bilingual: no
bn_counterpart: n/a
data_file: MD-033_Subscription_Plan_and_Billing_Cycle_Register.csv
effective_dated: yes
sources:
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M39_Subscription_and_Recurring_Revenue.md
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-033 — Subscription Plan and Billing Cycle Register

> Recurring revenue is recognised over the service period, not on invoice. The plan definition is
> what `M53` recognises against.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Commercial & pricing |
| Owning module | `M39` |
| Data steward | Revenue analyst |
| Golden source | CCO and CFO approved plan set |
| Refresh cadence | Quarterly |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `plan_code` | char(9) | ✔ | `SUB-nnnnn`, permanent | — |  |
| `plan_name` | text(120) | ✔ | Registered name (`VB-010`) | — |  |
| `item_code` | fk | ✔ | → `MD-019` | — |  |
| `billing_cycle` | enum | ✔ | monthly / quarterly / half_yearly / annual | — |  |
| `billing_day` | int | ✔ | 1–28, or `anniversary` | — | 28 avoids month-end failures |
| `proration_method` | enum | ✔ | daily / none / full_period | — | **Drives revenue recognition** |
| `trial_days` | int | ✔ | 0 for none | — |  |
| `commitment_months` | int | ✔ | Minimum term | — |  |
| `cancellation_notice_days` | int | ✔ |  | — |  |
| `pause_allowed` | bool | ✔ |  | — |  |
| `max_pause_days` | int |  |  | — |  |
| `dunning_ladder_code` | fk | ✔ | → `DT-018` | — | Overdue escalation |
| `auto_renew` | bool | ✔ |  | — |  |
| `revenue_recognition_method` | enum | ✔ | straight_line / on_delivery / milestone | — | → `M53` |
| `effective_from` | date | ✔ |  | — |  |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `plan_name` |
| Surrogate key | `plan_code` |
| Code format | `SUB-nnnnn` |
| Reuse policy | Never reused |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| SUB-01 | `billing_day` above 28 is rejected — months without that day fail silently | **H** | `ERR-SUB-001` |
| SUB-02 | `proration_method` must be consistent with `revenue_recognition_method` | **H** | `ERR-SUB-002` |
| SUB-03 | `pause_allowed` TRUE requires `max_pause_days` | **H** | `ERR-SUB-003` |
| SUB-04 | Cancellation inside the commitment requires an approved variation | **A** | `ERR-SUB-004` |
| SUB-05 | Changing a plan with active subscribers is prohibited — issue a new plan and migrate | **H** | `ERR-SUB-005` |
| SUB-06 | A plan with no dunning ladder warns | **S** | `WRN-SUB-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-019` Catalogue | Before |
| `MD-029` Pricing | Before |

| Depended on by |
|---|
| `M39` subscriptions · `M53` revenue recognition · `M20` invoicing · `DT-018` dunning letters |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Commercial plan design with Finance revenue treatment |
| Who supplies it | CCO and CFO |
| Collection method | Workshop; revenue treatment confirmed by Finance before launch |
| Known quality issues | No subscription products exist today beyond AMC; this is a new revenue stream |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 15–40 plans | Low |
| SIT / UAT | 12 across all cycles and proration methods | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Revenue analyst |
| Who may deactivate | CFO |
| Approval required | **CFO** — revenue recognition consequence |
| Effective dating | **Yes** |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
plan_code,plan_name,item_code,billing_cycle,billing_day,proration_method,trial_days,commitment_months,cancellation_notice_days,pause_allowed,auto_renew,revenue_recognition_method,effective_from,active
SUB-00101,Data Backup Essential,ITM-007101,monthly,1,daily,14,12,30,TRUE,TRUE,straight_line,2027-01-01,TRUE
SUB-00210,Managed IT Standard,ITM-007210,monthly,1,daily,0,12,60,FALSE,TRUE,straight_line,2027-01-01,TRUE
```

---

## 10. Migration notes

Not migrated — new revenue stream.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-032_Contract_and_AMC_Template_Catalogue.md`](MD-032_Contract_and_AMC_Template_Catalogue.md) | Contract-based recurring revenue |
| `M53` Revenue Recognition, Commission and Settlement | Recognition method |
| `DT-018` Dunning and Collection Letter Series | Overdue handling |

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
