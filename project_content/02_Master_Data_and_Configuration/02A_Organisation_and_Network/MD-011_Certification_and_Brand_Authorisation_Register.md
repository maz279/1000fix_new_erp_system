---
id: MD-011
title: Certification and Brand Authorisation Register
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Quality
author: Quality with Commercial
reviewers: [Technical, HR, Commercial, Warranty, Legal]
approver: Quality Manager
content_class: C
purpose: >
  Records which certifications exist, which brand authorises what work, validity and evidence.
  BRU-SRM-09 blocks assigning a technician who lacks a current certification for that brand
  warranty work; the rule cannot execute without this register.
traces_to: [M22, M09, 05-05 BRU-SRM-09, MD-010, MD-017, P08, EO-004]
priority: P0
wave: W2
bilingual: no
bn_counterpart: n/a
data_file: MD-011_Certification_and_Brand_Authorisation_Register.csv
effective_dated: yes
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-09
    verified: 2026-08-15
    class: P1
  - source: Brand authorisation agreements held in `M24`
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-011 — Certification and Brand Authorisation Register

> **This register makes a hard business rule executable.** `BRU-SRM-09` blocks assignment of an
> uncertified technician to brand warranty work. Without the register the rule has nothing to
> evaluate, and the company performs warranty work it cannot claim for.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Workforce identity |
| Owning module | `M22` |
| Data steward | Quality analyst |
| Golden source | Executed brand authorisation agreements and issued certificates |
| Refresh cadence | On issue, renewal or withdrawal; expiry sweep daily |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `certification_code` | char(9) | ✔ | `CRT-nnnnn`, permanent | — | |
| `certification_name` | text(160) | ✔ | | — | |
| `issuing_body` | enum | ✔ | brand / internal / external_body / regulator | — | |
| `brand_code` | fk | | → `MD-017`; required when `issuing_body = brand` | — | |
| `device_family_code` | fk | | → `MD-021` | — | |
| `skill_codes` | multi-fk | ✔ | → `MD-010` | — | Skills this certification evidences |
| `authorises_warranty_work` | bool | ✔ | | — | **Drives `BRU-SRM-09`** |
| `validity_months` | int | ✔ | | — | |
| `renewal_requirement` | enum | ✔ | reassessment / refresher_course / evidence_only / brand_reissue | — | |
| `evidence_required` | text(300) | ✔ | Certificate scan, assessment record | — | Stored in `M24` |
| `grace_period_days` | int | ✔ | Default 0 | — | Days past expiry still permitted |
| `effective_from` / `effective_to` | date | ✔ / | | — | |
| `active` | bool | ✔ | | — | |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `issuing_body` + `brand_code` + `certification_name` |
| Surrogate key | `certification_code` |
| Reuse policy | Never reused; historical assignments reference it |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| CRT-01 | `issuing_body = brand` requires a `brand_code` | **H** | `ERR-CRT-001` |
| CRT-02 | `authorises_warranty_work` TRUE requires a brand issuer and recorded evidence | **H** | `ERR-CRT-002` |
| CRT-03 | An expired certification blocks assignment to warranty work (`BRU-SRM-09`) | **H** | `ERR-CRT-003` |
| CRT-04 | `grace_period_days` above 30 requires Quality Manager approval | **A** | `ERR-CRT-004` |
| CRT-05 | A certification may not be archived while any technician holds it and has open warranty jobs | **H** | `ERR-CRT-005` |
| CRT-06 | Certification expiring within 60 days raises a notification (`NT-014`) | **C** | — |
| CRT-07 | A brand with no certified technician at a branch offering that brand's warranty work warns | **S** | `WRN-CRT-007` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-017` Brand partner register | **Before** |
| `MD-010` Skill taxonomy | Before |
| `MD-021` Device catalogue | Before |

| Depended on by |
|---|
| `MD-012` employee certifications · `M02` dispatch eligibility · `M09` warranty claims · `DT-033` claim evidence pack · `P08` brand portal certification view |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Executed brand authorisation agreements; issued technician certificates |
| Who supplies it | Quality Manager, per brand |
| Collection method | Agreement review plus certificate register reconciliation |
| Known quality issues | ⚠ The "17+ brands" figure underpins this register and is recorded as **unverified** in audit `00-07` H2-12 and content risk `CR-05`. This dataset is where it is verified |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 60–150 certification types across 17+ brands | With brand partnerships |
| SIT / UAT | 25 — covering brand, internal and regulator issuers | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Quality analyst |
| Who may deactivate | Quality Manager |
| Approval required | Quality Manager; Commercial for a brand-issued certification |
| Effective dating | **Yes** — validity and authorisation scope are effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
certification_code,certification_name,issuing_body,brand_code,device_family_code,authorises_warranty_work,validity_months,renewal_requirement,grace_period_days,effective_from,active
CRT-00101,Samsung Mobile Level 2 Service,brand,BRD-005,DF-MB,TRUE,24,brand_reissue,0,2026-01-01,TRUE
CRT-00204,Internal L3 Board Repair Certification,internal,,DF-IT,FALSE,24,reassessment,30,2026-07-01,TRUE
CRT-00310,Refrigerant Handling Authorisation,regulator,,DF-HA,FALSE,36,refresher_course,0,2026-07-01,TRUE
```

---

## 10. Migration notes

`DM-009`. Legacy certification records are typically paper certificates held at branch level. Expect substantial manual capture; **any technician without verifiable evidence is loaded as uncertified**, not assumed certified.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-010_Competency_and_Skill_Taxonomy.md`](MD-010_Competency_and_Skill_Taxonomy.md) | Skills evidenced |
| [`../02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md`](../02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md) | Issuing brands |
| `M09` Warranty, Protection Plans and Claims | Claim eligibility |
| `EO-004` Brand Claim Rules and Evidence Standard Guide | Evidence expectations |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Quality Manager (pending) |

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
