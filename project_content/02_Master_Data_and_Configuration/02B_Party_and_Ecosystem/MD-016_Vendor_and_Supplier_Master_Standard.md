---
id: MD-016
title: Vendor and Supplier Master Standard
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Procurement
author: Procurement with Finance
reviewers: [Finance, Tax, Legal & Compliance, Inventory]
approver: Chief Financial Officer
content_class: C
purpose: >
  The vendor record schema with category, banking, tax status, compliance documents and approval
  state. Procurement, payables, VAT deduction at source and vendor-portal access all depend on a
  governed vendor record; an unapproved vendor must not be payable.
traces_to: [M16, M42, M52, P05, MD-038, MD-037, EO-005]
priority: P1
wave: W3
bilingual: no
bn_counterpart: n/a
data_file: MD-016_Vendor_and_Supplier_Master_Standard.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M16_Procurement_and_Strategic_Sourcing.md
    verified: 2026-08-15
    class: P1
  - source: VAT deduction at source obligations — specified entities must deduct VAT when paying for services and remit to NBR
    verified: 2026-08-15
    class: P2
supersedes: none
review_due: 2027-02-15
---

# MD-016 — Vendor and Supplier Master Standard

> **A vendor record is a payment instruction.** The most common procurement fraud is a changed
> bank account on an existing vendor. Bank-detail changes are therefore treated as high-risk
> events, not routine edits.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Party & ecosystem |
| Owning module | `M16` |
| Data steward | Procurement analyst |
| Golden source | Vendor onboarding pack with verified trade licence, BIN and bank details |
| Refresh cadence | On onboarding; compliance documents re-verified annually |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `vendor_code` | char(8) | ✔ | `VND-nnnn`, permanent | — |  |
| `party_id` | fk | ✔ | → `MD-013` | — |  |
| `vendor_category` | enum | ✔ | parts / consumables / services / logistics / subcontract / recycling / facilities / it | — |  |
| `trade_licence_no` | text(40) | ✔ |  | — | Verified against the document |
| `bin` | text(20) |  | Required where VAT-registered | — | Drives input-VAT claim |
| `tin` | text(20) |  | **S3** | — |  |
| `is_vat_registered` | bool | ✔ |  | — |  |
| `vds_applicable` | bool | ✔ |  | — | **Whether we must deduct VAT at source** |
| `vds_rate_code` | fk |  | → `MD-037`; required when `vds_applicable` | — |  |
| `bank_account_name` | text(160) | ✔ | Must match the legal name | — |  |
| `bank_account_no` | text(34) | ✔ | **S3** | — |  |
| `bank_routing_no` | text(20) | ✔ | BEFTN routing | — |  |
| `payment_term_code` | fk | ✔ | → `MD-038` | — |  |
| `approval_state` | enum | ✔ | draft / submitted / verified / approved / suspended / blacklisted | — | **Gates payability** |
| `portal_enabled` | bool | ✔ |  | — | `P05` access |
| `scorecard_id` | fk |  | → `M42` | — |  |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `bin` where present; otherwise `trade_licence_no` |
| Surrogate key | `vendor_code` |
| Code format | `VND-nnnn` |
| Reuse policy | Never reused; payment history references it |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| VND-01 | A purchase order may not be raised against a vendor whose `approval_state` is not `approved` | **H** | `ERR-VND-001` |
| VND-02 | `bank_account_name` must match the legal name; a mismatch requires CFO approval | **A** | `ERR-VND-002` |
| VND-03 | **A bank-detail change resets `approval_state` to `verified` and requires re-approval** | **H** | `ERR-VND-003` |
| VND-04 | `vds_applicable` TRUE requires a `vds_rate_code` | **H** | `ERR-VND-004` |
| VND-05 | An expired trade licence blocks new purchase orders | **H** | `ERR-VND-005` |
| VND-06 | A blacklisted vendor may not be reactivated without CFO approval | **A** | `ERR-VND-006` |
| VND-07 | Two vendors sharing a bank account number warn — a duplicate or a fraud signal | **S** | `WRN-VND-007` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-013` Party standard | Before |
| `MD-037` Tax codes | Before — VDS rates |
| `MD-038` Payment terms | Before |

| Depended on by |
|---|
| `M16` procurement · `M52` accounts payable · `M42` supplier performance · `P05` vendor portal · `DT-023` purchase order |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Vendor onboarding pack |
| Who supplies it | Procurement, verified against original documents |
| Collection method | Onboarding form via `P05`, or manual for legacy vendors |
| Known quality issues | Legacy vendor lists commonly contain duplicates, closed vendors and unverified bank details |
| Cleansing rules | `DM-011`. **Bank details are re-confirmed with the vendor directly**, never migrated on trust |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 200–500 vendors | Low |
| SIT / UAT | 40 across all categories and approval states | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Procurement analyst |
| Who may deactivate | CFO for blacklist; Procurement Manager for suspend |
| Approval required | CFO for approval and for any bank-detail change |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
vendor_code,party_id,vendor_category,trade_licence_no,bin,is_vat_registered,vds_applicable,payment_term_code,approval_state,portal_enabled,active
VND-0001,a11b22c3,parts,TL-DHK-000123,000000000000,TRUE,TRUE,PT-30,approved,TRUE,TRUE
VND-0042,d44e55f6,logistics,TL-CTG-000876,,FALSE,TRUE,PT-15,approved,TRUE,TRUE
```

---

## 10. Migration notes

`DM-004` party scope plus a vendor-specific extension. **All vendors load as `verified`, not `approved`** — approval requires a positive confirmation after migration.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-013_Customer_and_Party_Master_Standard.md`](MD-013_Customer_and_Party_Master_Standard.md) | Vendor as a party role |
| `MD-037` Tax Code, VAT Rate and Mushak Mapping Register | VDS rates |
| `EO-005` Vendor and Supplier Onboarding Pack | Onboarding content |
| `M42` Supplier Relationship and Performance | Scorecards |

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
