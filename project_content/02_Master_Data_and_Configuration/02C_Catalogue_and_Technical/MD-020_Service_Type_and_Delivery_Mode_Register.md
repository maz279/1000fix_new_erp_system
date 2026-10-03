---
id: MD-020
title: Service Type and Delivery Mode Register
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Operations
author: Operations with Commercial
reviewers: [Commercial, Finance, Logistics, Localisation Lead]
approver: Operations Director
content_class: C
purpose: >
  Walk-in, on-site, pick and drop, remote, workshop and kiosk modes with their eligibility, charging
  and SLA implications. Delivery mode changes price, promise, routing and staffing; encoding it in
  the catalogue alone is insufficient because eligibility depends on zone and device.
traces_to: [M01, M02, M03, M05, MD-005, MD-019, MD-028, MD-029, UI-037]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: MD-020_Service_Type_and_Delivery_Mode_Register_BN.md
data_file: MD-020_Service_Type_and_Delivery_Mode_Register.csv
effective_dated: yes
sources:
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P01 booking — choose delivery mode (walk-in, on-site, pick and drop, remote)
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-020 — Service Type and Delivery Mode Register

> Delivery mode is the first branching decision in every booking. It determines the price, the
> SLA, who does the work and whether we ever touch the device.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Catalogue & technical |
| Owning module | `M01` |
| Data steward | Operations analyst |
| Golden source | Operations service-model decision |
| Refresh cadence | Per wave |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `mode_code` | char(8) | ✔ | `DMD-nnn`, permanent | — |  |
| `mode_name_en` | text(80) | ✔ |  | — |  |
| `mode_name_bn` | text(80) | ✔ |  | **✔** | Shown in the `P01` booking flow |
| `mode_class` | enum | ✔ | walk_in / on_site / pick_drop / remote / workshop / kiosk / courier | — |  |
| `device_families` | multi-fk | ✔ | → `MD-021` | — | Where the mode is offered |
| `requires_zone_coverage` | bool | ✔ |  | — | Checks `MD-005` |
| `requires_technician_travel` | bool | ✔ |  | — | Drives capacity and cost |
| `customer_present_required` | bool | ✔ |  | — |  |
| `base_charge_item_code` | fk |  | → `MD-019` | — | Call-out or collection fee |
| `zone_surcharge_applies` | bool | ✔ |  | — |  |
| `default_sla_band_code` | fk | ✔ | → `MD-028` | — |  |
| `booking_lead_time_hours` | int | ✔ | Minimum notice | — |  |
| `cancellation_window_hours` | int | ✔ |  | — | Free cancellation window |
| `evidence_required` | multi-enum | ✔ | photo_before / photo_after / otp / signature / seal | — | Custody and QC evidence |
| `effective_from` | date | ✔ |  | — |  |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `mode_class` + `mode_name_en` |
| Surrogate key | `mode_code` |
| Code format | `DMD-nnn` |
| Reuse policy | Never reused |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| DMD-01 | `requires_zone_coverage` TRUE blocks booking where the address resolves to an uncovered zone | **H** | `ERR-DMD-001` |
| DMD-02 | A mode with `requires_technician_travel` must have a default SLA band and a lead time | **H** | `ERR-DMD-002` |
| DMD-03 | `pick_drop` and `courier` modes must require custody evidence — OTP or signature | **H** | `ERR-DMD-003` |
| DMD-04 | `mode_name_bn` is mandatory | **H** | `ERR-DMD-004` |
| DMD-05 | Waiving a base charge requires branch manager approval | **A** | `ERR-DMD-005` |
| DMD-06 | A mode offered in a device family with no capable branch warns | **S** | `WRN-DMD-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-021` Device families | Before |
| `MD-028` SLA bands | Before |
| `MD-005` Zones | Before |
| `MD-019` Charge items | Before or bind after |

| Depended on by |
|---|
| `M01` order creation · `M02` dispatch · `UI-037` booking flow copy · `MD-029` zone surcharges |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Operations service-model definition |
| Who supplies it | Operations Director with CCO |
| Collection method | Workshop; validated against current practice at a sample of branches |
| Known quality issues | Current modes are described in marketing content, not in an operational register; eligibility rules exist only as branch knowledge |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 8–14 modes | Low |
| SIT / UAT | All modes | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Operations analyst |
| Who may deactivate | Operations Director |
| Approval required | Operations Director; CCO for a charging change |
| Effective dating | **Yes** |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
mode_code,mode_name_en,mode_name_bn,mode_class,requires_zone_coverage,requires_technician_travel,customer_present_required,zone_surcharge_applies,default_sla_band_code,booking_lead_time_hours,cancellation_window_hours,evidence_required,effective_from,active
DMD-001,Walk-in at service centre,সার্ভিস সেন্টারে সরাসরি,walk_in,FALSE,FALSE,TRUE,FALSE,SLA-P3,0,0,photo_before;signature,2026-07-01,TRUE
DMD-002,On-site visit,বাসায় সার্ভিস,on_site,TRUE,TRUE,TRUE,TRUE,SLA-P2,4,2,photo_before;photo_after;signature,2026-07-01,TRUE
DMD-003,Pick and drop,পিক অ্যান্ড ড্রপ,pick_drop,TRUE,FALSE,TRUE,TRUE,SLA-P3,12,4,photo_before;otp;seal,2026-07-01,TRUE
```

---

## 10. Migration notes

Not migrated — authored.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-019_Product_and_Service_Catalogue_Seed.md`](MD-019_Product_and_Service_Catalogue_Seed.md) | Charge items |
| [`../02A_Organisation_and_Network/MD-005_Dispatch_Zone_and_Territory_Master.md`](../02A_Organisation_and_Network/MD-005_Dispatch_Zone_and_Territory_Master.md) | Coverage |
| `UI-037` Booking and Order Creation Flow Copy | The consuming surface |
| `M01` Service Request and Order Management | The implementing module |

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
- [ ] Bengali name columns populated and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
