---
id: MD-034
title: Loyalty Tier, Point and Benefit Register
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Commercial
author: Commercial with Marketing and Finance
reviewers: [Finance, Marketing, Legal, Service Operations, Localisation Lead]
approver: Chief Commercial Officer
content_class: C
purpose: >
  Privilege tiers, earn and burn rates, benefit schedules, expiry and tier-movement rules.
  A computed rule grants Gold and Diamond members priority-1 SLA (BRU-SRM-10); the tiers must be
  defined for it to fire.
traces_to: [M10, 05-05 BRU-SRM-10, MD-014, MD-028, MD-030, VB-010]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: MD-034_Loyalty_Tier_Point_and_Benefit_Register_BN.md
data_file: MD-034_Loyalty_Tier_Point_and_Benefit_Register.csv
effective_dated: yes
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-10 — Privilege Gold and Diamond members automatically receive priority-1 SLA
    verified: 2026-08-15
    class: P1
  - source: 1000_fix_corporate_website project_content VP-003 Privileged Program — 50% off service charges membership, in market
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-034 — Loyalty Tier, Point and Benefit Register

> ⚠ **Blocked by an open naming decision.** `VB-010` §13 decision 1 records that the in-market
> name **"Privileged Program"** should be renamed to **"Privilege"** — and that the decision must
> be taken **before this register is authored**, because once the name is a master-data row
> referenced by transactions, `NM-01` makes the change a migration.
>
> **This file is drafted with "Privilege" assumed.** If Commercial rules otherwise, every row
> changes.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Commercial & pricing |
| Owning module | `M10` |
| Data steward | Loyalty analyst |
| Golden source | CCO-approved programme design |
| Refresh cadence | Quarterly |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `tier_code` | char(8) | ✔ | `LTR-nnn`, permanent | — |  |
| `tier_name_en` | text(80) | ✔ | Registered name (`VB-010`) | — |  |
| `tier_name_bn` | text(80) | ✔ |  | **✔** | Shown in `P01` |
| `tier_rank` | int | ✔ | 1 = lowest | — |  |
| `qualification_rule` | text(400) | ✔ | Machine-evaluable | — | Spend, frequency or purchase |
| `is_purchased` | bool | ✔ |  | — | Membership bought, not earned |
| `membership_item_code` | fk |  | → `MD-019`; when purchased | — |  |
| `validity_months` | int | ✔ |  | — |  |
| `points_earn_rate` | decimal(6,2) | ✔ | Points per BDT 100 | — |  |
| `points_burn_value` | decimal(6,4) | ✔ | BDT per point | — | **Financial liability** |
| `points_expiry_months` | int | ✔ |  | — |  |
| `benefit_discount_code` | fk |  | → `MD-030` | — |  |
| `sla_band_override` | fk |  | → `MD-028` | — | **`BRU-SRM-10` binding** |
| `downgrade_rule` | text(300) | ✔ |  | — | What happens at non-renewal |
| `effective_from` | date | ✔ |  | — |  |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `tier_name_en` |
| Surrogate key | `tier_code` |
| Code format | `LTR-nnn` |
| Reuse policy | Never reused |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| LTR-01 | Tier ranks must be contiguous with no gaps | **H** | `ERR-LTR-001` |
| LTR-02 | `is_purchased` TRUE requires a `membership_item_code` with an active price | **H** | `ERR-LTR-002` |
| LTR-03 | Points liability must be recognised in the ledger at issue, not redemption | **H** | `ERR-LTR-003` |
| LTR-04 | A tier with `sla_band_override` must reference an active band (`BRU-SRM-10`) | **H** | `ERR-LTR-004` |
| LTR-05 | Changing `points_burn_value` on issued points is prohibited — it is a liability restatement | **H** | `ERR-LTR-005` |
| LTR-06 | `tier_name_bn` is mandatory | **H** | `ERR-LTR-006` |
| LTR-07 | A tier with no distinct benefit warns | **S** | `WRN-LTR-007` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-014` Segments | Before |
| `MD-028` SLA bands | Before |
| `MD-030` Discount rules | Before |
| `MD-019` Catalogue | Before for purchased tiers |

| Depended on by |
|---|
| `M10` loyalty · `MD-028` SLA override · `P01` membership display · `NT-023` lifecycle campaigns |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | CCO-approved programme design; the in-market Privileged Program |
| Who supplies it | CCO with Marketing and Finance |
| Collection method | Programme design workshop; points liability treatment confirmed by Finance |
| Known quality issues | ⚠ The in-market programme name is defective (`VB-010` §9.1) and the decision is open. Benefit terms in marketing content have not been reconciled with what the system will enforce |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 3–5 tiers | Low |
| SIT / UAT | All tiers | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Loyalty analyst |
| Who may deactivate | CCO |
| Approval required | **CCO and CFO** — points are a balance-sheet liability |
| Effective dating | **Yes** |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
tier_code,tier_name_en,tier_name_bn,tier_rank,is_purchased,validity_months,points_earn_rate,points_burn_value,points_expiry_months,sla_band_override,effective_from,active
LTR-001,Privilege Silver,প্রিভিলেজ সিলভার,1,TRUE,12,1.00,0.5000,24,,2026-07-01,TRUE
LTR-002,Privilege Gold,প্রিভিলেজ গোল্ড,2,TRUE,12,1.50,0.5000,24,SLA-P1,2026-07-01,TRUE
LTR-003,Privilege Diamond,প্রিভিলেজ ডায়মন্ড,3,TRUE,12,2.00,0.5000,36,SLA-P1,2026-07-01,TRUE
```

---

## 10. Migration notes

Existing Privileged Program members migrate with their remaining validity. **Points balances, if any exist, must be reconciled and recognised as a liability before load** (`DM-008`).

---

## 11. Related documents

| Document | Relationship |
|---|---|
| `VB-010` Product, Plan and Programme Naming Standard | **§13 decision 1 blocks this file** |
| [`MD-030_Discount_Promotion_and_Voucher_Rule_Register.md`](MD-030_Discount_Promotion_and_Voucher_Rule_Register.md) | Benefit discounts |
| [`../02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md`](../02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md) | SLA override |
| `M10` Loyalty, Membership and Rewards | The implementing module |

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
- [ ] Bengali name columns populated and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
