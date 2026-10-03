---
id: MD-022
title: Spare Part Catalogue and Compatibility Matrix
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Inventory
author: Inventory with Technical
reviewers: [Technical, Procurement, Finance, Warranty, Localisation Lead]
approver: Inventory Manager
content_class: C
purpose: >
  The part master with OEM/compatible flag, model compatibility, substitution rules, warranty class
  and hazard class. Parts issue, van stock, procurement, claim reimbursement and estimating all
  break on an ungoverned part master.
traces_to: [M15, M43, MD-019, MD-021, MD-023, KB-009, DM-007]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix_BN.md
data_file: MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M15_Spare_Parts_and_Inventory_Management.md
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-022 — Spare Part Catalogue and Compatibility Matrix

> Wrong-part fitting is a leading cause of rework **and** of brand warranty claim rejection.
> Compatibility is a data question, not a technician memory question.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Catalogue & technical |
| Owning module | `M15` |
| Data steward | Parts catalogue analyst |
| Golden source | Manufacturer parts lists and brand consignment schedules |
| Refresh cadence | Monthly; on any new model |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `part_code` | char(10) | ✔ | `PRT-nnnnnn`, permanent | — |  |
| `item_code` | fk | ✔ | → `MD-019` | — | Every part is also a catalogue item |
| `manufacturer_part_no` | text(60) | ✔ |  | — | OEM number |
| `part_name_en` | text(160) | ✔ |  | — |  |
| `part_name_bn` | text(160) | ✔ |  | **✔** | Shown on `P02` and estimates |
| `part_class` | enum | ✔ | oem / oem_equivalent / compatible / refurbished | — | **Affects warranty and claim eligibility** |
| `parts_family_code` | fk | ✔ |  | — | Compatibility root |
| `compatible_models` | multi-fk | ✔ | → `MD-021` | — | The compatibility matrix |
| `supersedes_part_code` | fk |  | Self-reference | — | Supersession chain |
| `substitutes` | multi-fk |  | Self-reference | — | Approved alternatives |
| `hazard_class` | enum | ✔ | none / lithium / refrigerant / chemical / sharp / esd_sensitive | — | Drives handling and transport |
| `warranty_months` | int | ✔ |  | — | Warranty on the part itself |
| `is_consignment` | bool | ✔ |  | — | Brand-owned stock (`MD-017`) |
| `brand_code` | fk |  | → `MD-017` | — | Required when consignment |
| `uom_code` | fk | ✔ | → `MD-023` | — |  |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `manufacturer_part_no` + `brand_code` |
| Surrogate key | `part_code` |
| Code format | `PRT-nnnnnn` |
| Reuse policy | Never reused; stock movements reference it |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| PRT-01 | A part may not be issued to a job whose device model is not in `compatible_models` | **H** | `ERR-PRT-001` |
| PRT-02 | A brand warranty claim may only consume parts of class `oem` or `oem_equivalent` | **H** | `ERR-PRT-002` |
| PRT-03 | `is_consignment` TRUE requires a `brand_code` | **H** | `ERR-PRT-003` |
| PRT-04 | A lithium or refrigerant part requires a hazard-handling acknowledgement at issue (`KB-013`) | **H** | `ERR-PRT-004` |
| PRT-05 | Substituting a part outside the approved list requires supervisor approval and a reason | **A** | `ERR-PRT-005` |
| PRT-06 | A part with no compatible model warns — it can never be issued | **S** | `WRN-PRT-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-019` Catalogue | **Before** |
| `MD-021` Device models | **Before** |
| `MD-023` UoM | Before |
| `MD-017` Brands | Before for consignment |

| Depended on by |
|---|
| `M15` stock · `M43` demand planning · `DT-005` estimates · `DT-033` claim evidence · `KB-009` compatibility notes |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Manufacturer parts lists; brand consignment schedules; observed consumption |
| Who supplies it | Parts catalogue analyst |
| Collection method | Bulk load per brand, then continuous addition |
| Known quality issues | Legacy part records lack compatibility entirely — parts are matched by technician knowledge |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 30,000–120,000 parts | Continuous |
| SIT / UAT | 2,000 across all classes and hazard types | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Parts catalogue analyst |
| Who may deactivate | Inventory Manager |
| Approval required | Inventory Manager; Warranty for a `part_class` change |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
part_code,item_code,manufacturer_part_no,part_name_en,part_name_bn,part_class,hazard_class,warranty_months,is_consignment,brand_code,uom_code,active
PRT-004120,ITM-004120,LTN140AT31-001,Display panel 14in FHD,ডিসপ্লে প্যানেল ১৪ ইঞ্চি,oem_equivalent,esd_sensitive,6,FALSE,,UOM-EA,TRUE
PRT-011044,ITM-011044,EB-BA546ABY,Battery pack 5000mAh,ব্যাটারি প্যাক ৫০০০mAh,oem,lithium,6,TRUE,BRD-005,UOM-EA,TRUE
```

---

## 10. Migration notes

`DM-007`. Compatibility must be **built**, not migrated — it does not exist in legacy data.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-021_Device_Category_Make_and_Model_Catalogue.md`](MD-021_Device_Category_Make_and_Model_Catalogue.md) | Compatibility target |
| `KB-009` Parts Compatibility and Substitution Notes | Technician-facing guidance |
| `KB-013` ESD, Chemical and Battery Safety Data | Hazard handling |
| `M15` Spare Parts and Inventory Management | The implementing module |

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
- [ ] Bengali name columns populated and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
