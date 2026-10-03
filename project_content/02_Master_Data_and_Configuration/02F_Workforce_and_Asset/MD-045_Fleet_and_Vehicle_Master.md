---
id: MD-045
title: Fleet and Vehicle Master
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Facilities
author: Facilities with Field Operations
reviewers: [Finance, HSE, Logistics, Operations]
approver: Operations Director
content_class: C
purpose: >
  Vehicles, assignment, fuel policy, service schedule and telematics device binding. M46 fleet and
  P09 rider assignment require a vehicle register, and van stock in MD-004 binds to it.
traces_to: [M46, P09, M03, MD-004, MD-008, MD-044, SP-030]
priority: P2
wave: W3
bilingual: no
bn_counterpart: n/a
data_file: MD-045_Fleet_and_Vehicle_Master.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/F_Asset_Equipment_and_Facilities/M46_Fleet_and_Vehicle_Management.md
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-045 — Fleet and Vehicle Master

> A vehicle is simultaneously a fixed asset, a stock location and a safety obligation. All three
> bind to this record.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Workforce & asset |
| Owning module | `M46` |
| Data steward | Fleet analyst |
| Golden source | Vehicle registration documents and the fleet register |
| Refresh cadence | On acquisition or disposal; document expiry checked monthly |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `vehicle_code` | char(8) | ✔ | `VEH-nnnn`, permanent | — |  |
| `registration_no` | text(20) | ✔ | BRTA registration | — | Natural key |
| `vehicle_type` | enum | ✔ | motorcycle / van / pickup / car / truck | — |  |
| `make_model` | text(120) | ✔ |  | — |  |
| `year_of_manufacture` | int | ✔ |  | — |  |
| `branch_code` | fk | ✔ | → `MD-003` | — | Home base |
| `assigned_position_code` | fk |  | → `MD-008` | — | Custodian position |
| `asset_class_code` | fk | ✔ | → `MD-044` | — |  |
| `stock_location_code` | fk |  | → `MD-004` | — | **Van stock binding** |
| `telematics_device_id` | text(60) |  |  | — | GPS tracking |
| `fitness_expiry` | date | ✔ |  | — | **Blocks dispatch when expired** |
| `tax_token_expiry` | date | ✔ |  | — |  |
| `insurance_expiry` | date | ✔ |  | — |  |
| `route_permit_expiry` | date |  |  | — |  |
| `service_interval_km` | int | ✔ |  | — |  |
| `last_service_km` | int |  |  | — |  |
| `fuel_type` | enum | ✔ | petrol / octane / diesel / cng / electric | — |  |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `registration_no` |
| Surrogate key | `vehicle_code` |
| Code format | `VEH-nnnn` |
| Reuse policy | Never reused |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| VEH-01 | A vehicle with expired fitness, tax token or insurance may not be dispatched | **H** | `ERR-VEH-001` |
| VEH-02 | A vehicle carrying van stock must have a stock location and a custodian | **H** | `ERR-VEH-002` |
| VEH-03 | A document expiring within 30 days raises a notification to Facilities | **C** | `—` |
| VEH-04 | Overdue service by more than 2,000 km blocks dispatch | **A** | `ERR-VEH-004` |
| VEH-05 | A vehicle may not be archived while it holds stock | **H** | `ERR-VEH-005` |
| VEH-06 | A vehicle with no telematics device warns — routing and custody cannot be evidenced | **S** | `WRN-VEH-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-003` Branches | Before |
| `MD-044` Asset classes | Before |
| `MD-008` Positions | Before |
| `MD-004` Stock locations | Bind after |

| Depended on by |
|---|
| `M46` fleet · `P09` rider assignment · `MD-004` van locations · `M49` fixed assets · `SP-030` HSE |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Vehicle registration documents and the fleet register |
| Who supplies it | Facilities |
| Collection method | Document transcription and physical verification |
| Known quality issues | Legacy fleet records commonly omit document expiry dates |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 80–250 vehicles | Low |
| SIT / UAT | 20 including expired-document scenarios | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Fleet analyst |
| Who may deactivate | Operations Director |
| Approval required | Operations Director; Finance for capitalisation |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
vehicle_code,registration_no,vehicle_type,make_model,branch_code,assigned_position_code,asset_class_code,stock_location_code,fitness_expiry,insurance_expiry,service_interval_km,fuel_type,active
VEH-0001,DHAKA-METRO-LA-11-4471,motorcycle,Honda CB Shine,BR-0002,POS-0480,AC-030,LOC-02010,2027-03-31,2027-01-15,3000,octane,TRUE
VEH-0020,DHAKA-METRO-GA-22-8890,van,Toyota HiAce,BR-0001,POS-0500,AC-030,LOC-01500,2027-06-30,2027-05-20,10000,diesel,TRUE
```

---

## 10. Migration notes

`DM-008` asset scope. Document expiry dates must be **re-captured from the documents**, not migrated.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`../02A_Organisation_and_Network/MD-004_Warehouse_and_Storage_Location_Master.md`](../02A_Organisation_and_Network/MD-004_Warehouse_and_Storage_Location_Master.md) | Van stock locations |
| [`MD-044_Asset_Class_and_Depreciation_Schedule_Register.md`](MD-044_Asset_Class_and_Depreciation_Schedule_Register.md) | Capitalisation |
| `M46` Fleet and Vehicle Management | The implementing module |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Operations Director (pending) |

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
