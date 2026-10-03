---
id: MD-023
title: Unit of Measure and Packaging Register
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Inventory
author: Inventory with Logistics
reviewers: [Procurement, Finance, Logistics]
approver: Inventory Manager
content_class: C
purpose: >
  The unit-of-measure set with conversions, packaging levels and weight and volume for logistics.
  Stock accuracy, landed cost and courier rating all require consistent UoM; a part bought by the
  box and issued by the piece with no conversion produces silent stock error.
traces_to: [M15, M41, M44, MD-019, MD-022]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
data_file: MD-023_Unit_of_Measure_and_Packaging_Register.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M41_Warehouse_Management.md
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-023 — Unit of Measure and Packaging Register

> Small register, silent failures. Every conversion error is a stock discrepancy that surfaces at
> count, months later, with no traceable cause.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Catalogue & technical |
| Owning module | `M15` |
| Data steward | Inventory analyst |
| Golden source | This register |
| Refresh cadence | Annual |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `uom_code` | char(7) | ✔ | `UOM-nn`, permanent | — |  |
| `uom_name` | text(60) | ✔ |  | — |  |
| `uom_category` | enum | ✔ | unit / weight / volume / length / time | — | Conversion is only valid within a category |
| `base_uom_code` | fk | ✔ | Self-reference; the category base | — |  |
| `conversion_factor` | decimal(18,6) | ✔ | To the base UoM | — |  |
| `decimal_precision` | int | ✔ | 0 for discrete units | — |  |
| `is_purchase_uom` | bool | ✔ |  | — |  |
| `is_stock_uom` | bool | ✔ |  | — | Exactly one per category |
| `is_sale_uom` | bool | ✔ |  | — |  |
| `packaging_level` | enum |  | each / inner / carton / pallet | — |  |
| `gross_weight_kg` | decimal(10,3) |  |  | — | Courier rating |
| `volume_cm3` | decimal(12,2) |  |  | — | Volumetric weight |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `uom_name` |
| Surrogate key | `uom_code` |
| Code format | `UOM-nn` |
| Reuse policy | Never reused |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| UOM-01 | Conversion is only permitted within one `uom_category` | **H** | `ERR-UOM-001` |
| UOM-02 | Exactly one `is_stock_uom` per category | **H** | `ERR-UOM-002` |
| UOM-03 | `decimal_precision` must be 0 for discrete units | **H** | `ERR-UOM-003` |
| UOM-04 | A UoM may not be archived while any item references it | **H** | `ERR-UOM-004` |
| UOM-05 | Changing a conversion factor after any stock movement is prohibited | **H** | `ERR-UOM-005` |
| UOM-06 | A packaging level with no weight warns — courier rating will estimate | **S** | `WRN-UOM-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| Nothing | **Loads very early** |

| Depended on by |
|---|
| `MD-019` catalogue · `MD-022` parts · every stock movement, purchase order and shipment |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Authored from procurement and warehouse practice |
| Who supplies it | Inventory Manager |
| Collection method | Workshop |
| Known quality issues | Legacy systems commonly use one UoM (each) and handle boxes by convention |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 25–50 units | Low |
| SIT / UAT | All | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Inventory analyst |
| Who may deactivate | Inventory Manager |
| Approval required | Inventory Manager; **conversion factors may not change after first use** |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
uom_code,uom_name,uom_category,base_uom_code,conversion_factor,decimal_precision,is_purchase_uom,is_stock_uom,is_sale_uom,packaging_level,active
UOM-EA,Each,unit,UOM-EA,1.000000,0,TRUE,TRUE,TRUE,each,TRUE
UOM-BX,Box of 10,unit,UOM-EA,10.000000,0,TRUE,FALSE,FALSE,inner,TRUE
UOM-KG,Kilogram,weight,UOM-KG,1.000000,3,TRUE,TRUE,TRUE,,TRUE
UOM-LT,Litre,volume,UOM-LT,1.000000,3,TRUE,TRUE,TRUE,,TRUE
```

---

## 10. Migration notes

Not migrated — authored. Legacy quantities are converted to the stock UoM during `DM-007` with the conversion recorded.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md`](MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md) | Parts UoM |
| `M44` Import, Trade Compliance and Landed Cost | Volumetric weight |
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
