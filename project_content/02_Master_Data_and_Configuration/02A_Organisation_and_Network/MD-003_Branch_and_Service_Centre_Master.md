---
id: MD-003
title: Branch and Service Centre Master
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Operations
author: Operations with MDM
reviewers: [Finance, Inventory, Dispatch, Localisation Lead, Marketing]
approver: Operations Director
content_class: C
purpose: >
  Registers all 51+ service centres with their code, bilingual name, location, capabilities,
  capacity and hours. Dispatch, routing, stock, cash, SLA, capacity, reporting and the public
  locator all key off this table; nothing operational works without it.
traces_to: [M04, M02, M41, MD-002, MD-005, MD-006, MD-040, P01, P03]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: MD-003_Branch_and_Service_Centre_Master_BN.md
data_file: MD-003_Branch_and_Service_Centre_Master.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/README.md — 51+ service centres across all 8 administrative divisions
    verified: 2026-08-15
    class: P3
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M04_Branch_and_Front_Desk_Operations.md
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-003 — Branch and Service Centre Master

> **The most widely referenced dataset in the system.** A service order, a technician, a stock
> location, a cash drawer, an invoice sequence and a customer's locator search all resolve
> through a branch code.
>
> ⚠ The figure "51+ service centres" is class **P3** (company profile) until this dataset is
> populated and confirmed. `CG-012` §7 requires it to be converted to P1 here.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Organisation & network |
| Owning module | `M04` |
| Data steward | Operations MDM analyst |
| Golden source | Operations branch register, confirmed by each Branch Manager |
| Refresh cadence | On opening, closing, relocation or capability change; full review quarterly |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `branch_code` | char(7) | ✔ | `BR-nnnn`, unique, permanent | — | |
| `entity_code` | fk | ✔ | → `MD-002` | — | Owning legal entity |
| `name_en` | text(120) | ✔ | | — | English name |
| `name_bn` | text(120) | ✔ | | **✔** | Bengali name — customer-facing |
| `branch_type` | enum | ✔ | service_centre / workshop / depot / kiosk / head_office / warehouse | — | |
| `division_code` | fk | ✔ | → `MD-006` | — | |
| `district_code` | fk | ✔ | → `MD-006` | — | |
| `upazila_code` | fk | ✔ | → `MD-006` | — | |
| `address_line_bn` | text(300) | ✔ | | **✔** | |
| `address_line_en` | text(300) | ✔ | | — | |
| `postcode` | char(4) | ✔ | 4-digit | — | |
| `latitude` / `longitude` | decimal(9,6) | ✔ | Within Bangladesh bounds | — | Drives routing and locator |
| `zone_code` | fk | ✔ | → `MD-005` | — | Dispatch zone |
| `phone` | text(20) | ✔ | | — | |
| `opening_time` / `closing_time` | time | ✔ | | — | Local, Asia/Dhaka |
| `weekly_closed_days` | text(20) | | e.g. `FRI` | — | |
| `capabilities` | multi-enum | ✔ | See §2.1 | — | What this site can actually do |
| `bench_capacity` | int | | Workshop only | — | Concurrent work orders |
| `daily_intake_capacity` | int | ✔ | | — | Drives booking availability |
| `has_cash_drawer` | bool | ✔ | | — | |
| `stock_location_id` | fk | | → `MD-004` | — | |
| `is_public` | bool | ✔ | | — | Appears in the customer locator |
| `opened_on` / `closed_on` | date | ✔ / | | — | |
| `active` | bool | ✔ | | — | |

### 2.1 Capability values

`walk_in` · `on_site_dispatch` · `pick_and_drop` · `workshop_l1` · `workshop_l2` ·
`workshop_l3_board` · `data_recovery` · `parts_stock` · `cash_collection` · `refurbishment` ·
`ewaste_collection` · `kiosk_dropoff`

> A capability the site cannot actually perform is worse than a missing one: booking will route
> work to it. Capabilities are confirmed by the Branch Manager, not assumed from the branch type.

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | None reliable — branch names repeat across districts |
| Surrogate key | `branch_code` |
| Code format | `BR-nnnn`, sequential, **no geographic meaning encoded** (`CF-03`) |
| Reuse policy | **Never reused.** A closed branch keeps its code; its transaction history depends on it |

> **Odoo binding.** Extends OCA `operating_unit`; `05-02` names it `fix.branch`.

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| BRN-01 | `name_bn` is mandatory. A branch with no Bengali name cannot be published to `P01` | **H** | `ERR-BRN-001` |
| BRN-02 | Latitude 20.5–26.7, longitude 88.0–92.7 (Bangladesh bounds) | **H** | `ERR-BRN-002` |
| BRN-03 | `upazila_code` must belong to `district_code`, which must belong to `division_code` | **H** | `ERR-BRN-003` |
| BRN-04 | A branch with `walk_in` capability must have opening and closing times | **H** | `ERR-BRN-004` |
| BRN-05 | A branch with `parts_stock` must have a `stock_location_id` | **H** | `ERR-BRN-005` |
| BRN-06 | A branch may not be archived while it holds open service orders, stock or uncollected devices | **H** | `ERR-BRN-006` |
| BRN-07 | Removing a capability requires Operations approval and a recorded reason | **A** | `ERR-BRN-007` |
| BRN-08 | `daily_intake_capacity` of zero warns — the branch will accept no bookings | **S** | `WRN-BRN-008` |
| BRN-09 | `is_public` TRUE with no phone number warns | **S** | `WRN-BRN-009` |

---

## 5. Relationships and load dependencies

| Depends on | Cardinality | Load order |
|---|---|---|
| `MD-002` Legal entity | n : 1 | Before |
| `MD-006` Geographic hierarchy | n : 1 | **Before** |
| `MD-005` Dispatch zone | n : 1 | Before or same load, then bind |
| `MD-004` Stock location | 1 : n | After — locations reference the branch |

| Depended on by |
|---|
| `MD-004`, `MD-008`, `MD-012`, `MD-040` sequences, and every transactional entity through `operating_unit_id` (`05-02` DM-03) |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Operations branch register; each Branch Manager confirms their own row |
| Who supplies it | Operations Director, per branch |
| Collection method | Structured confirmation form per branch, including a GPS reading taken on site |
| Known quality issues | GPS coordinates in legacy records are frequently the district centroid, not the shop front. Capability lists are aspirational in several sites |
| Cleansing rules | `DM-011`. **GPS must be re-captured on site**, not copied |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 51+ at go-live | Network expansion is a stated business objective |
| SIT / UAT | 8 minimum — one per division, covering every branch type | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Operations MDM analyst, on Ops Director approval |
| Who may deactivate | Operations Director, and only after BRN-06 passes |
| Approval required | Yes for add, close, relocate or capability change |
| Effective dating | Capability and hours changes are effective-dated |
| Archive rule | Archived, never deleted (`05-02` DM-06) |

---

## 9. Sample rows

```csv
branch_code,entity_code,name_en,name_bn,branch_type,division_code,district_code,postcode,latitude,longitude,zone_code,capabilities,daily_intake_capacity,has_cash_drawer,is_public,active
BR-0001,EN-01,Shewrapara Head Office,শেওড়াপাড়া প্রধান কার্যালয়,head_office,DHA,DHAKA,1216,23.7900,90.3700,ZN-001,"walk_in;workshop_l1;workshop_l2;workshop_l3_board;parts_stock;cash_collection;data_recovery",40,TRUE,TRUE,TRUE
BR-0002,EN-01,Agrabad Service Centre,আগ্রাবাদ সার্ভিস সেন্টার,service_centre,CTG,CHATTOGRAM,4100,22.3300,91.8100,ZN-020,"walk_in;on_site_dispatch;pick_and_drop;workshop_l1;parts_stock;cash_collection",25,TRUE,TRUE,TRUE
```

---

## 10. Migration notes

Migrated from the operations branch list. Field mapping in `DM-004`-adjacent scope; branch is
referenced by nearly every migrated transaction, so **it loads before all transactional
migration**. Legacy branch names are English-only — Bengali names must be authored, not
translated mechanically (`CG-010` BP-04).

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-005_Dispatch_Zone_and_Territory_Master.md`](MD-005_Dispatch_Zone_and_Territory_Master.md) | Zone assignment |
| [`MD-006_Bangladesh_Geographic_Hierarchy.md`](MD-006_Bangladesh_Geographic_Hierarchy.md) | Geographic parents |
| [`MD-004_Warehouse_and_Storage_Location_Master.md`](MD-004_Warehouse_and_Storage_Location_Master.md) | Stock locations |
| `M04` Branch and Front-Desk Operations | The implementing module |
| `SC-001`…`SC-053` (website content set) | Public branch pages — must reconcile to this register |

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
