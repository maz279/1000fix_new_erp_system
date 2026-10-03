---
id: MD-018
title: Marketplace Seller Category and Standard Register
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Marketplace Operations
author: Marketplace Operations with Legal and Quality
reviewers: [Legal & Compliance, Quality, Finance, Commercial]
approver: Chief Commercial Officer
content_class: C
purpose: >
  Defines seller categories with their certification and document requirements, commission bands and
  scorecard thresholds. P07 cannot open registration until categories and their entry standards are
  defined, and a seller cannot transact until verified and approved.
traces_to: [M12, P07, LG-004, EO-001, EO-002, MD-029, MD-013]
priority: P2
wave: W7
bilingual: no
bn_counterpart: n/a
data_file: MD-018_Marketplace_Seller_Category_and_Standard_Register.csv
effective_dated: yes
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P07 governance requirements — a seller cannot transact until documents are verified, the agreement is signed and admin approval is granted
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-018 — Marketplace Seller Category and Standard Register

> **Entry standards are a commercial and a liability decision.** A category that admits sellers
> we cannot hold to our quality standard exposes the brand on every job they take.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Party & ecosystem |
| Owning module | `M12` |
| Data steward | Marketplace Operations officer |
| Golden source | Marketplace policy approved by CCO and Legal |
| Refresh cadence | Per wave during W7–W9; annually thereafter |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `category_code` | char(8) | ✔ | `SLC-nnn`, permanent | — |  |
| `category_name` | text(120) | ✔ |  | — |  |
| `seller_type` | enum | ✔ | freelance_engineer / shop | — |  |
| `device_family_code` | fk | ✔ | → `MD-021` | — |  |
| `required_documents` | multi-enum | ✔ | nid / trade_licence / tin / references / work_samples / bank_proof | — | Verified before transacting |
| `required_certifications` | multi-fk |  | → `MD-011` | — |  |
| `commission_band_code` | fk | ✔ | → `MD-029` | — |  |
| `registration_fee_bdt` | decimal(10,2) | ✔ | May be zero | — |  |
| `min_rating_to_operate` | decimal(2,1) | ✔ | e.g. 4.0 | — | Below this, visibility reduces |
| `suspension_rating` | decimal(2,1) | ✔ | e.g. 3.5 | — | Automatic suspension threshold |
| `max_open_jobs` | int | ✔ |  | — | Concurrency cap |
| `payout_hold_days` | int | ✔ |  | — | Held before release |
| `effective_from` | date | ✔ |  | — |  |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `seller_type` + `device_family_code` |
| Surrogate key | `category_code` |
| Code format | `SLC-nnn` |
| Reuse policy | Never reused |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| SLC-01 | A seller may not transact until every `required_documents` item is verified and the agreement is signed | **H** | `ERR-SLC-001` |
| SLC-02 | `suspension_rating` must be below `min_rating_to_operate` | **H** | `ERR-SLC-002` |
| SLC-03 | A category requiring certification must name at least one certification in `MD-011` | **H** | `ERR-SLC-003` |
| SLC-04 | Payout is blocked while a dispute is open, regardless of `payout_hold_days` | **H** | `ERR-SLC-004` |
| SLC-05 | Lowering `suspension_rating` requires CCO and Legal approval — it changes contractual grounds | **A** | `ERR-SLC-005` |
| SLC-06 | A category with no active sellers after one wave warns | **S** | `WRN-SLC-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-021` Device catalogue | Before |
| `MD-011` Certifications | Before |
| `MD-029` Commission bands | Before |

| Depended on by |
|---|
| `P07` seller registration · `M12` marketplace · `LG-004` seller agreement · `EO-002` standards handbook · `DT-039` payout statement |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Marketplace policy workshop with Legal and Quality |
| Who supplies it | CCO |
| Collection method | Policy workshop; thresholds validated against pilot data before W7 launch |
| Known quality issues | No precedent — the marketplace does not exist yet. Thresholds are initial estimates and must be recalibrated after the first quarter |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 12–25 categories | Low |
| SIT / UAT | All categories — registration gating is tested exhaustively | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Marketplace Operations officer |
| Who may deactivate | CCO |
| Approval required | CCO **and** Legal for any threshold with contractual effect |
| Effective dating | **Yes** — thresholds are effective-dated; a seller is judged by the version in force |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
category_code,category_name,seller_type,device_family_code,required_documents,required_certifications,commission_band_code,registration_fee_bdt,min_rating_to_operate,suspension_rating,payout_hold_days,effective_from,active
SLC-001,Freelance Mobile Engineer,freelance_engineer,DF-MB,nid;tin;references;work_samples;bank_proof,,CB-MP-15,500.00,4.0,3.5,7,2027-01-01,TRUE
SLC-010,Partner Repair Shop — IT,shop,DF-IT,trade_licence;bin;tin;bank_proof;work_samples,CRT-00204,CB-MP-12,2000.00,4.2,3.7,14,2027-01-01,TRUE
```

---

## 10. Migration notes

Not migrated — authored before W7 marketplace launch.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| `LG-004` Marketplace Seller Agreement and Policy Handbook | Contractual force behind these thresholds |
| `EO-001` Marketplace Seller Onboarding Kit | Registration content |
| `EO-002` Seller Standards, Scoring and Sanctions Handbook | How thresholds are explained |
| `P07` Marketplace Seller Portal | The consuming surface |

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
