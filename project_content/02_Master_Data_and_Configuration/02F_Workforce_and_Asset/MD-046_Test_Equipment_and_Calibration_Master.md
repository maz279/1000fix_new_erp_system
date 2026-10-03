---
id: MD-046
title: Test Equipment and Calibration Master
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Quality with Facilities
author: Quality with Technical
reviewers: [Technical, Facilities, Finance, Audit]
approver: Quality Manager
content_class: C
purpose: >
  Test and repair equipment, calibration intervals, certificates, custody and ISO 9001 traceability.
  ISO 9001:2015 requires calibration control of measuring equipment, and audit evidence depends on
  the register — an uncalibrated instrument invalidates every measurement it produced.
traces_to: [M45, M23, MD-004, MD-008, MD-044, KB-012, DT-043]
priority: P1
wave: W5
bilingual: no
bn_counterpart: n/a
data_file: MD-046_Test_Equipment_and_Calibration_Master.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/F_Asset_Equipment_and_Facilities/M45_Enterprise_Asset_and_Test_Equipment.md
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 requirement for control of monitoring and measuring resources
    verified: 2026-08-15
    class: P2
supersedes: none
review_due: 2027-02-15
---

# MD-046 — Test Equipment and Calibration Master

> **An out-of-calibration instrument does not merely stop being usable — it casts doubt on every
> measurement it has produced since its last valid calibration.** The register must therefore
> record not only the next due date but the full certificate history.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Workforce & asset |
| Owning module | `M45` |
| Data steward | Quality analyst |
| Golden source | Calibration certificates issued by the accredited laboratory |
| Refresh cadence | Per calibration interval; register reviewed quarterly |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `equipment_code` | char(9) | ✔ | `EQP-nnnnn`, permanent | — |  |
| `equipment_name` | text(120) | ✔ |  | — |  |
| `equipment_type` | enum | ✔ | multimeter / oscilloscope / power_supply / rework_station / gauge / scale / thermometer / manifold / other | — |  |
| `serial_no` | text(60) | ✔ |  | — | Natural key with make |
| `make_model` | text(120) | ✔ |  | — |  |
| `branch_code` | fk | ✔ | → `MD-003` | — |  |
| `location_code` | fk |  | → `MD-004` | — |  |
| `custodian_position_code` | fk | ✔ | → `MD-008` | — |  |
| `asset_class_code` | fk | ✔ | → `MD-044` | — |  |
| `requires_calibration` | bool | ✔ |  | — |  |
| `calibration_interval_months` | int |  | Required when calibrated | — |  |
| `last_calibration_date` | date |  |  | — |  |
| `next_calibration_due` | date |  | **Computed** | — |  |
| `calibration_certificate_ref` | text(60) |  | `M24` reference | — | **ISO audit evidence** |
| `calibration_body` | text(120) |  | Accredited laboratory | — |  |
| `tolerance_spec` | text(200) |  |  | — | Acceptable measurement range |
| `status` | enum | ✔ | in_service / out_of_calibration / under_calibration / withdrawn | — |  |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `make_model` + `serial_no` |
| Surrogate key | `equipment_code` |
| Code format | `EQP-nnnnn` |
| Reuse policy | Never reused; calibration history references it |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| EQP-01 | Equipment past `next_calibration_due` is set `out_of_calibration` and **may not be used for a measurement recorded in a service report** | **H** | `ERR-EQP-001` |
| EQP-02 | `requires_calibration` TRUE requires an interval and a certificate reference | **H** | `ERR-EQP-002` |
| EQP-03 | `next_calibration_due` is computed from the last calibration plus the interval | **C** | `—` |
| EQP-04 | Using out-of-calibration equipment requires Quality Manager approval and triggers a review of affected jobs | **A** | `ERR-EQP-004` |
| EQP-05 | Equipment due within 30 days raises a notification | **C** | `—` |
| EQP-06 | A branch performing L3 board repair with no calibrated equipment warns | **S** | `WRN-EQP-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-003` Branches | Before |
| `MD-004` Locations | Before |
| `MD-008` Positions | Before |
| `MD-044` Asset classes | Before |

| Depended on by |
|---|
| `M45` enterprise asset · `M23` quality · `DT-043` audit forms · `KB-012` equipment operating guides · ISO surveillance audit |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Physical equipment survey plus calibration certificates |
| Who supplies it | Quality analyst with branch supervisors |
| Collection method | Physical survey — walk every workshop and record what is there |
| Known quality issues | Legacy calibration records are paper certificates held locally; several instruments are likely uncalibrated |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 400–1,200 items across 51+ sites | Low |
| SIT / UAT | 60 including out-of-calibration scenarios | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Quality analyst |
| Who may deactivate | Quality Manager |
| Approval required | Quality Manager; Finance for disposal |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
equipment_code,equipment_name,equipment_type,serial_no,make_model,branch_code,custodian_position_code,asset_class_code,requires_calibration,calibration_interval_months,last_calibration_date,next_calibration_due,status,active
EQP-00101,Bench multimeter,multimeter,MM-88214,Fluke 87V,BR-0001,POS-0142,AC-020,TRUE,12,2026-04-10,2027-04-10,in_service,TRUE
EQP-00220,Refrigerant manifold gauge,manifold,MG-33110,Testo 550,BR-0002,POS-0311,AC-020,TRUE,12,2025-11-02,2026-11-02,out_of_calibration,TRUE
```

---

## 10. Migration notes

`DM-008` asset scope. Calibration status must be **verified physically**; equipment with no retrievable certificate loads as `out_of_calibration`.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-044_Asset_Class_and_Depreciation_Schedule_Register.md`](MD-044_Asset_Class_and_Depreciation_Schedule_Register.md) | Capitalisation and calibration flag |
| `KB-012` Tool, Jig and Test Equipment Operating Guides | Operating guidance |
| `DT-043` NCR, CAPA and Internal Audit Report Forms | Audit evidence |
| `M23` Quality Management System | ISO 9001 control |

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
