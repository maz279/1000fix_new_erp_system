---
id: MD-017
title: Brand Partner Master Register
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Commercial
author: Commercial with Warranty and Legal
reviewers: [Legal & Compliance, Quality, Warranty, Finance]
approver: Chief Commercial Officer
content_class: C
purpose: >
  Registers the authorised brand partners, the scope of each authorisation, claim rules, rate-card
  ownership and contacts. Audit 00-07 H2-12 records the "17+ brands" figure as unverified while an
  M22 certification control depends on it; this dataset is where it is verified and closed.
traces_to: [M09, M22, P08, 00-07 H2-12, MD-011, MD-021, MD-029, EO-003, EO-004]
priority: P1
wave: W4
bilingual: no
bn_counterpart: n/a
data_file: MD-017_Brand_Partner_Master_Register.csv
effective_dated: yes
sources:
  - source: Executed brand authorisation agreements held in `M24`
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-07 finding H2-12 — the "17+ brands" figure is unverified and underpins an M22 control
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-017 — Brand Partner Master Register

> ⚠ **This dataset closes an open audit finding.** `00-07` H2-12 records that the "17+ brand
> partnerships" figure is used across the programme, underpins an `M22` certification control,
> and has **never been verified against the underlying agreements**.
>
> Until this register is populated from the executed agreements, every statement of the brand
> count in any content file must carry the provisional marking (`CG-012` §6.1). It is also
> content risk **`CR-05`**.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Party & ecosystem |
| Owning module | `M09` |
| Data steward | Commercial analyst |
| Golden source | Executed brand authorisation agreements |
| Refresh cadence | On signature, renewal or termination; full review annually |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `brand_code` | char(7) | ✔ | `BRD-nnn`, permanent | — |  |
| `party_id` | fk | ✔ | → `MD-013` | — |  |
| `brand_name` | text(120) | ✔ | As the brand writes it — do-not-translate (`BN-004`) | — |  |
| `agreement_ref` | text(60) | ✔ | `M24` document reference | — | **Evidence of authorisation** |
| `agreement_from` | date | ✔ |  | — |  |
| `agreement_to` | date |  | Null for evergreen | — |  |
| `authorised_categories` | multi-fk | ✔ | → `MD-021` device families | — | What we may service under warranty |
| `authorised_models` | multi-fk |  | → `MD-021`; null means all in category | — |  |
| `claim_submission_channel` | enum | ✔ | portal / api / email / brand_system | — | `P08` target is > 80% portal |
| `claim_window_days` | int | ✔ |  | — | Days from service to submission |
| `rate_card_owner` | enum | ✔ | brand / 1000fix / negotiated | — | Who sets labour and parts rates |
| `rate_card_code` | fk |  | → `MD-029` | — |  |
| `consignment_parts` | bool | ✔ |  | — | Brand supplies stock on consignment |
| `requires_certified_tech` | bool | ✔ |  | — | **Drives `BRU-SRM-09`** |
| `reimbursement_days_target` | int | ✔ |  | — | `P08` target < 45 |
| `primary_contact_name` | text(120) | ✔ |  | — |  |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `brand_name` |
| Surrogate key | `brand_code` |
| Code format | `BRD-nnn` |
| Reuse policy | Never reused; claim history references it |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| BRD-01 | `agreement_ref` must resolve to a document in `M24`. **No agreement, no authorisation** | **H** | `ERR-BRD-001` |
| BRD-02 | A warranty claim may not be raised against a brand outside its agreement dates | **H** | `ERR-BRD-002` |
| BRD-03 | `requires_certified_tech` TRUE requires at least one active certification in `MD-011` | **H** | `ERR-BRD-003` |
| BRD-04 | A device model may not be claimed under a brand that does not authorise its category | **H** | `ERR-BRD-004` |
| BRD-05 | An agreement expiring within 90 days raises a notification to Commercial | **C** | `—` |
| BRD-06 | Extending an authorisation scope without an agreement amendment requires CCO approval | **A** | `ERR-BRD-006` |
| BRD-07 | A brand with no certified technician at any branch warns | **S** | `WRN-BRD-007` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-013` Party standard | Before |
| `MD-021` Device catalogue | Before — authorised categories |
| `MD-011` Certification register | Same load, then bind |

| Depended on by |
|---|
| `M09` warranty claims · `MD-011` certifications · `P08` brand portal · `DT-033` claim evidence pack · `EO-004` claim rules guide |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Executed brand authorisation agreements |
| Who supplies it | Commercial, agreement by agreement |
| Collection method | **Read every agreement.** Count and scope are derived from the documents, not from the company profile |
| Known quality issues | ⚠ The count itself is unverified (`00-07` H2-12). Some authorisations may be informal or lapsed |
| Cleansing rules | `DM-011`. Any brand without a retrievable executed agreement is loaded as **inactive** pending Legal review |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 17+ claimed; **to be confirmed** by this exercise | Low |
| SIT / UAT | 6 brands across portal, API and email claim channels | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Commercial analyst on a signed agreement |
| Who may deactivate | CCO on termination |
| Approval required | CCO; Legal for any scope change |
| Effective dating | **Yes** — authorisation scope is effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
brand_code,party_id,brand_name,agreement_ref,agreement_from,agreement_to,authorised_categories,claim_submission_channel,claim_window_days,rate_card_owner,requires_certified_tech,reimbursement_days_target,active
BRD-005,b55c66d7,Samsung,DOC-BRAND-0005,2024-01-01,2027-12-31,DF-MB;DF-HA,portal,30,brand,TRUE,45,TRUE
BRD-011,c77d88e9,Dell,DOC-BRAND-0011,2023-06-01,,DF-IT,api,45,brand,TRUE,60,TRUE
```

---

## 10. Migration notes

Not migrated — built from agreements. This is a **verification exercise**, not a data load.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`../02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md`](../02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md) | Certifications this authorises |
| `M09` Warranty, Protection Plans and Claims | Claim eligibility |
| `EO-003` Brand Partner Onboarding Pack | Portal onboarding |
| `P08` Brand Partner Portal | The consuming surface |

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
