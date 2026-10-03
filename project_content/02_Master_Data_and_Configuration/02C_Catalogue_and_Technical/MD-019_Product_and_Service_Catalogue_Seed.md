---
id: MD-019
title: Product and Service Catalogue Seed
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Commercial
author: Commercial with Technical and Finance
reviewers: [Finance, Tax, Operations, Localisation Lead, Marketing]
approver: Chief Commercial Officer
content_class: C
purpose: >
  Every sellable service and product with code, bilingual name, category, attributes, tax class and
  revenue-stream binding. Nothing can be booked, quoted, priced, invoiced or reported without the
  catalogue: it is the spine of all fourteen revenue streams.
traces_to: [M37, M11, M38, MD-020, MD-029, MD-037, VB-010, DT-010]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: MD-019_Product_and_Service_Catalogue_Seed_BN.md
data_file: MD-019_Product_and_Service_Catalogue_Seed.csv
effective_dated: yes
sources:
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M37_Product_and_Service_Catalogue_Management.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/README.md — the fourteen revenue streams and their owning modules
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-019 — Product and Service Catalogue Seed

> **The spine.** Fourteen revenue streams resolve to catalogue items. An item missing from here
> cannot be sold, and an item with the wrong tax class produces a non-compliant invoice.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Catalogue & technical |
| Owning module | `M37` |
| Data steward | Catalogue analyst |
| Golden source | Commercial catalogue decision, approved by CCO |
| Refresh cadence | Continuous; full review quarterly |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | yes |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `item_code` | char(10) | ✔ | `ITM-nnnnnn`, permanent | — |  |
| `item_type` | enum | ✔ | service / part / accessory / product / plan / fee / bundle | — |  |
| `name_en` | text(160) | ✔ | Registered name (`VB-010`) | — |  |
| `name_bn` | text(160) | ✔ |  | **✔** | Customer-facing on `P01` |
| `category_code` | fk | ✔ | → §2.1 | — |  |
| `device_family_code` | fk |  | → `MD-021` | — | Null for non-device items |
| `revenue_stream` | enum | ✔ | One of the fourteen | — | **Drives `MD-036` business line** |
| `uom_code` | fk | ✔ | → `MD-023` | — |  |
| `tax_class_code` | fk | ✔ | → `MD-037` | — | **Drives the VAT rate on the invoice** |
| `is_sellable` | bool | ✔ |  | — |  |
| `is_stockable` | bool | ✔ |  | — | TRUE for parts and products |
| `requires_serial` | bool | ✔ |  | — |  |
| `warranty_type_code` | fk |  | → `MD-031` | — | Warranty granted on sale or repair |
| `standard_duration_min` | int |  | Services only | — | Feeds slot and capacity planning |
| `skill_code` | fk |  | → `MD-010` | — | Skill required to deliver |
| `effective_from` | date | ✔ |  | — |  |
| `active` | bool | ✔ |  | — |  |

### 2.1 Category tree

`category` → `sub_category` → `item`. Maximum three levels. Categories are shared with the
customer-facing navigation in `UI-002`, so a category rename is a UI change.

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `item_type` + `name_en` + `device_family_code` |
| Surrogate key | `item_code` |
| Code format | `ITM-nnnnnn`; no meaning encoded |
| Reuse policy | Never reused — invoices five years old reference it (`LG-009`) |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| ITM-01 | Every sellable item must have a tax class; an item with none cannot be invoiced | **H** | `ERR-ITM-001` |
| ITM-02 | Every item must bind to exactly one of the fourteen revenue streams | **H** | `ERR-ITM-002` |
| ITM-03 | `name_bn` is mandatory for any item with `is_sellable` TRUE | **H** | `ERR-ITM-003` |
| ITM-04 | A stockable item must have a UoM and a part record in `MD-022` | **H** | `ERR-ITM-004` |
| ITM-05 | A service item must have a standard duration and a skill code | **H** | `ERR-ITM-005` |
| ITM-06 | An item may not be archived while it appears on an active price list or open order | **H** | `ERR-ITM-006` |
| ITM-07 | Changing a tax class requires Finance approval and is effective-dated | **A** | `ERR-ITM-007` |
| ITM-08 | A sellable item with no price on any active price list warns | **S** | `WRN-ITM-008` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-023` UoM | **Before** |
| `MD-037` Tax classes | **Before** |
| `MD-021` Device families | Before |
| `MD-036` Business lines | Before |
| `MD-010` Skills | Before or bind after |

| Depended on by |
|---|
| `MD-029` price lists · `MD-031` warranty · `M38` e-commerce · every quotation, order, invoice and revenue report |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Commercial catalogue build from the existing service and price lists |
| Who supplies it | CCO with Technical and Finance |
| Collection method | Structured build; each item confirmed for tax class by Finance before load |
| Known quality issues | Legacy service lists are free text on price sheets with no codes, no tax class and no revenue-stream binding |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 3,000–15,000 items including parts and accessories | Continuous |
| SIT / UAT | 400 covering every item type and tax class | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Catalogue analyst |
| Who may deactivate | CCO |
| Approval required | CCO; **Finance for any tax class** |
| Effective dating | **Yes** |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
item_code,item_type,name_en,name_bn,category_code,device_family_code,revenue_stream,uom_code,tax_class_code,is_sellable,is_stockable,requires_serial,standard_duration_min,effective_from,active
ITM-000101,service,Laptop screen replacement,ল্যাপটপ স্ক্রিন প্রতিস্থাপন,CAT-IT-REP,DF-IT,out_of_warranty_repair,UOM-EA,TAX-STD15,TRUE,FALSE,FALSE,60,2026-07-01,TRUE
ITM-000455,service,AC jet wash service,এসি জেট ওয়াশ সার্ভিস,CAT-HA-MNT,DF-HA,out_of_warranty_repair,UOM-EA,TAX-STD15,TRUE,FALSE,FALSE,90,2026-07-01,TRUE
ITM-004120,part,Laptop display panel 14in FHD,ল্যাপটপ ডিসপ্লে প্যানেল ১৪ ইঞ্চি,CAT-IT-PRT,DF-IT,spare_parts,UOM-EA,TAX-STD15,TRUE,TRUE,TRUE,,2026-07-01,TRUE
```

---

## 10. Migration notes

`DM-007` scope for parts; services authored. Legacy price sheets are the input, not the source of truth.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-021_Device_Category_Make_and_Model_Catalogue.md`](MD-021_Device_Category_Make_and_Model_Catalogue.md) | Device families |
| [`MD-023_Unit_of_Measure_and_Packaging_Register.md`](MD-023_Unit_of_Measure_and_Packaging_Register.md) | Units |
| [`../02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md`](../02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md) | Tax classes |
| `VB-010` Product, Plan and Programme Naming Standard | Naming rules |
| `M37` Product and Service Catalogue Management | The implementing module |

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
- [ ] Bengali name columns populated and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
