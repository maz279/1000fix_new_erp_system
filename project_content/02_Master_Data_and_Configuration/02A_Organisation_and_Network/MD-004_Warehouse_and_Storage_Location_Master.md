---
id: MD-004
title: Warehouse and Storage Location Master
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Inventory
author: Inventory with Warehouse Operations
reviewers: [Finance, Operations, Data Migration Lead, Enterprise Architecture]
approver: Inventory Manager
content_class: C
purpose: >
  Defines the full storage-location tree — warehouses, branch stores, van stock, bins and quarantine.
  M41 and M15 cannot transact without a location tree, and van-stock reconciliation is impossible
  without every technician vehicle appearing as a location.
traces_to: [M41, M15, MD-003, MD-045, SP-016, SP-018]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
data_file: MD-004_Warehouse_and_Storage_Location_Master.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M41_Warehouse_Management.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M15_Spare_Parts_and_Inventory_Management.md
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-004 — Warehouse and Storage Location Master

> **Van stock is the least-controlled inventory in field service.** It is controlled here or
> nowhere: every technician vehicle is a location with a named custodian, or parts consumed in
> the field cannot be reconciled at all.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Organisation & network |
| Owning module | `M41` |
| Data steward | Inventory analyst |
| Golden source | Physical site survey per location |
| Refresh cadence | On any physical layout change; full count reconciliation quarterly |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `location_code` | char(9) | ✔ | `LOC-nnnnn`, unique, permanent | — | |
| `parent_location_code` | fk | | Self-reference; max depth 4 | — | Tree structure |
| `location_type` | enum | ✔ | central_warehouse / branch_store / van / bin / quarantine / transit / scrap / consignment | — | |
| `branch_code` | fk | ✔ | → `MD-003` | — | Owning site |
| `name` | text(120) | ✔ | | — | |
| `custodian_position_code` | fk | ✔ | → `MD-008` | — | **Position, not person** |
| `vehicle_code` | fk | | → `MD-045`; required when type = `van` | — | |
| `is_stockable` | bool | ✔ | | — | FALSE for view-only tree nodes |
| `allows_negative` | bool | ✔ | Must be FALSE except `transit` | — | |
| `is_quarantine` | bool | ✔ | | — | Received-but-uninspected and defective stock |
| `cycle_count_frequency` | enum | ✔ | weekly / monthly / quarterly / annual | — | |
| `capacity_units` | int | | | — | |
| `active` | bool | ✔ | | — | |

### 2.1 The four-level tree

```
Central warehouse (LOC-00001)
└── Zone / aisle (LOC-00010)
    └── Rack (LOC-00110)
        └── Bin (LOC-01100)          ← stockable leaf

Branch (BR-0002)
├── Branch store (LOC-02000)          ← stockable
├── Quarantine (LOC-02001)            ← stockable, is_quarantine
└── Van — technician vehicle (LOC-02010) ← stockable, custodian = technician position
```

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `branch_code` + `name` within a parent |
| Surrogate key | `location_code` |
| Code format | `LOC-nnnnn`; **no meaning encoded** — a bin renumbered on a warehouse re-layout keeps its code |
| Reuse policy | Never reused; historical stock movements reference it |

> **Odoo binding.** Extends `stock.location`; `05-02` names it `fix.stock.location`.

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| LOC-01 | Only leaf locations may be `is_stockable` | **H** | `ERR-LOC-001` |
| LOC-02 | Tree depth may not exceed 4 | **H** | `ERR-LOC-002` |
| LOC-03 | `allows_negative` TRUE is permitted only for `transit` | **H** | `ERR-LOC-003` |
| LOC-04 | A `van` location must reference a vehicle and a technician position | **H** | `ERR-LOC-004` |
| LOC-05 | A location may not be archived while it holds stock | **H** | `ERR-LOC-005` |
| LOC-06 | Every branch with the `parts_stock` capability must have at least one stockable location | **H** | `ERR-LOC-006` |
| LOC-07 | Reassigning a custodian requires a stock handover record | **A** | `ERR-LOC-007` |
| LOC-08 | A stockable location with no cycle-count frequency warns | **S** | `WRN-LOC-008` |

---

## 5. Relationships and load dependencies

| Depends on | Cardinality | Load order |
|---|---|---|
| `MD-003` Branch master | n : 1 | **Before** |
| `MD-008` Position master | n : 1 | Before |
| `MD-045` Fleet and vehicle | 1 : 1 for vans | Before, or bind after |

| Depended on by |
|---|
| `MD-022` part stock rules · `DM-007` inventory migration · every stock movement, reservation and count |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Physical site survey; warehouse layout drawings; vehicle register |
| Who supplies it | Warehouse Manager (central), Store Keeper (branch), Fleet (vans) |
| Collection method | Walk the site and record what exists. **Not** transcribed from the legacy system |
| Known quality issues | Legacy systems typically hold one location per branch, hiding quarantine and van stock entirely |
| Cleansing rules | `DM-011`. Opening stock must reconcile to the general ledger before load (`DM-013`) |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 1,500–3,000 — 51+ branches × store + quarantine, plus 200–400 vans, plus central warehouse bins | With network and headcount |
| SIT / UAT | 60 minimum — full tree for two branches plus central warehouse | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Inventory analyst |
| Who may deactivate | Inventory Manager, after LOC-05 |
| Approval required | Inventory Manager; Finance for any change affecting valuation |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change; the dataset's own audit trail for row change |

---

## 9. Sample rows

```csv
location_code,parent_location_code,location_type,branch_code,name,custodian_position_code,is_stockable,allows_negative,is_quarantine,cycle_count_frequency,active
LOC-00001,,central_warehouse,BR-0001,Central Warehouse Mirpur,POS-0142,FALSE,FALSE,FALSE,monthly,TRUE
LOC-01100,LOC-00110,bin,BR-0001,CW-A-01-03,POS-0142,TRUE,FALSE,FALSE,monthly,TRUE
LOC-02000,,branch_store,BR-0002,Agrabad Branch Store,POS-0311,TRUE,FALSE,FALSE,weekly,TRUE
LOC-02001,,quarantine,BR-0002,Agrabad Quarantine,POS-0311,TRUE,FALSE,TRUE,weekly,TRUE
LOC-02010,,van,BR-0002,Van CTG-11-4471,POS-0480,TRUE,FALSE,FALSE,weekly,TRUE
```

---

## 10. Migration notes

Legacy stock is typically held at branch level with no sub-location. Migration must **allocate** opening stock to specific locations, which requires a physical count at cutover — see `DM-007` and `DM-014`.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-003_Branch_and_Service_Centre_Master.md`](MD-003_Branch_and_Service_Centre_Master.md) | Owning site |
| [`MD-008_Organisation_Structure_and_Position_Master.md`](MD-008_Organisation_Structure_and_Position_Master.md) | Custodian positions |
| `MD-045` Fleet and Vehicle Master | Van locations |
| `SP-016` SOP Spare Parts Issue, Return and Van Stock | The process this enables |
| `M41` Warehouse Management | The implementing module |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Inventory Manager (pending) |

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
