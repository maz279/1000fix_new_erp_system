---
id: MD-012
title: Employee Master Data Template
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: HR
author: HR with Security and Payroll
reviewers: [Security, Finance, Legal & Compliance, DPO, Data Migration Lead]
approver: HR Director
content_class: C
purpose: >
  The employee record schema with mandatory fields, sensitivity classification and the joiner data
  pack. 500+ employees must be loaded before payroll, attendance, dispatch or access control can
  run, and several fields are Sensitive Personally Identifiable Data under the residency rule.
traces_to: [M21, M56, M29, 05-06 NFR-086, MD-008, MD-009, DM-009, LG-009]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
data_file: MD-012_Employee_Master_Data_Template.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-086 — split-residency; NID, passport, TIN and biometric templates are Bangladesh-resident
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M21_Core_HR_and_Employee_Lifecycle.md
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-012 — Employee Master Data Template

> ⚠ **This dataset carries residency-classified data.** `05-06` NFR-086 requires NID, passport,
> TIN and biometric templates to be held in a **Bangladesh-resident** store, with the residency
> classification carried on the field and enforced at write time (NFR-086a).
>
> `NFR-086c` additionally requires that **non-production environments never contain unmasked
> residency-classified data**. Test data comes from `TS-002`, never from a production extract.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Workforce identity |
| Owning module | `M21` |
| Data steward | HR systems analyst |
| Golden source | Signed employment contract and joiner data pack |
| Refresh cadence | On joiner, mover, leaver; annual data-accuracy review |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Sens | BN | Description |
|---|---|:--:|:--:|:--:|---|
| `employee_code` | char(8) | ✔ | S0 | — | `EMP-nnnn`, permanent |
| `entity_code` | fk | ✔ | S0 | — | → `MD-002` |
| `position_code` | fk | ✔ | S0 | — | → `MD-008` |
| `role_code` | fk | ✔ | S0 | — | → `MD-009` |
| `full_name_en` | text(160) | ✔ | S1 | — | As on NID |
| `full_name_bn` | text(160) | ✔ | S1 | — | As on NID, Bengali script |
| `date_of_birth` | date | ✔ | S2 | — | |
| `gender` | enum | ✔ | S2 | — | |
| `nid_number` | text(20) | ✔ | **S3** | — | **Bangladesh-resident (NFR-086)** |
| `tin_number` | text(20) | | **S3** | — | **Bangladesh-resident** |
| `passport_number` | text(20) | | **S3** | — | **Bangladesh-resident** |
| `biometric_template_ref` | text(64) | | **S3** | — | **Bangladesh-resident**; reference only, never the template |
| `mobile` | text(20) | ✔ | S2 | — | Primary contact and OTP channel |
| `personal_email` | text(120) | | S2 | — | |
| `present_address_id` / `permanent_address_id` | fk | ✔ | S2 | — | → `MD-007` |
| `emergency_contact_name` / `_phone` | text | ✔ | S2 | — | |
| `blood_group` | enum | | S2 | — | Field-safety relevant |
| `join_date` | date | ✔ | S0 | — | |
| `confirmation_date` | date | | S0 | — | |
| `employment_type` | enum | ✔ | S0 | — | permanent / contract / temporary |
| `branch_code` | fk | ✔ | S0 | — | → `MD-003` |
| `bank_account_no` / `bank_routing_no` | text | | **S3** | — | BEFTN disbursement |
| `pf_membership_no` | text(20) | | S2 | — | Provident fund |
| `leave_date` / `leave_reason_code` | date / fk | | S1 | — | → `MD-026` |
| `active` | bool | ✔ | S0 | — | |

> Sensitivity classes S0–S3 are defined in `05-02` §10. S3 fields are encrypted and
> access-logged.

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `nid_number` — one NID, one employee |
| Surrogate key | `employee_code` |
| Reuse policy | **Never reused.** A rejoiner receives a new code and is linked to the prior record; reusing a code corrupts payroll and access history |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| EMP-01 | `nid_number` must be unique across active and archived employees | **H** | `ERR-EMP-001` |
| EMP-02 | Every employee must resolve to an active position (`MD-008`) | **H** | `ERR-EMP-002` |
| EMP-03 | S3 fields must be written to the Bangladesh-resident store; a write to another region is rejected (`NFR-086a`) | **H** | `ERR-EMP-003` |
| EMP-04 | A non-production environment may not receive unmasked S3 data (`NFR-086c`) | **H** | `ERR-EMP-004` |
| EMP-05 | A technician role requires `blood_group` and an emergency contact | **H** | `ERR-EMP-005` |
| EMP-06 | Payroll disbursement requires bank account and routing number | **H** | `ERR-EMP-006` |
| EMP-07 | A leaver must have `leave_date` and `leave_reason_code`, and access is revoked the same day (`OP-015`) | **H** | `ERR-EMP-007` |
| EMP-08 | Two employees sharing a mobile number warn — common but a duplicate-record signal | **S** | `WRN-EMP-008` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-002`, `MD-003`, `MD-007`, `MD-008`, `MD-009` | **All before** |
| `MD-026` Reason codes | Before, for leave reasons |

| Depended on by |
|---|
| `M56` payroll · `M55` attendance · `M02` dispatch · `M29` access provisioning · `MD-011` certifications held · `DT-041` payslip |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Signed employment contract and the joiner data pack |
| Who supplies it | HR, at onboarding |
| Collection method | Structured joiner form; NID verified against the physical document |
| Known quality issues | Legacy HR data commonly lacks NID for long-tenured staff, and bank details are held in a separate payroll spreadsheet |
| Cleansing rules | `DM-011`. **NID is verified, not transcribed from a spreadsheet** — it is the natural key |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 500+ active; 800–1,200 including leavers within retention | With headcount; technician turnover is material |
| SIT / UAT | 30 with **synthetic** NIDs from `TS-002` — never a production extract | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | HR systems analyst on a signed joiner pack |
| Who may deactivate | HR Director on a recorded leaver |
| Approval required | HR Director; DPO for any change to an S3 field definition |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
employee_code,entity_code,position_code,role_code,full_name_en,full_name_bn,mobile,branch_code,employment_type,join_date,blood_group,active
EMP-0001,EN-01,POS-0480,R10,Karim Hossain,করিম হোসেন,01712000000,BR-0002,permanent,2021-03-14,B+,TRUE
EMP-0002,EN-01,POS-0311,R18,Nasrin Akter,নাসরিন আক্তার,01812000000,BR-0002,permanent,2023-08-01,O+,TRUE
```

---

## 10. Migration notes

`DM-009` HR and payroll migration. **YTD payroll figures cannot be recomputed after the fact** — migrating them wrongly misstates every employee's tax position. Reconciliation is mandatory (`DM-013`).

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-008_Organisation_Structure_and_Position_Master.md`](MD-008_Organisation_Structure_and_Position_Master.md) | Positions occupied |
| [`MD-009_Role_and_Job_Title_Master.md`](MD-009_Role_and_Job_Title_Master.md) | Access roles |
| `LG-009` Data Retention and Deletion Schedule | Leaver record retention |
| `OP-015` Access Request and Joiner-Mover-Leaver Content | Provisioning and revocation |
| `TS-002` Test Data Pack and Persona Set | Synthetic employee data |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | HR Director (pending) |

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
