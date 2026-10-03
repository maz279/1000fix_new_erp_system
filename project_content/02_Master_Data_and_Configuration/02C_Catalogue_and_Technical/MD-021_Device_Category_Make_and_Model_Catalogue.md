---
id: MD-021
title: Device Category, Make and Model Catalogue
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: MDM with Technical
author: Technical with MDM
reviewers: [Commercial, Warranty, Inventory, Localisation Lead, BI Lead]
approver: Technical Director
content_class: C
purpose: >
  The device taxonomy to model level with brand, category, typical faults, parts family and service
  applicability. Device identity is mandatory at intake (BRU-SRM-01); free-text device entry destroys
  analytics, warranty matching and parts planning simultaneously.
traces_to: [M17, 05-05 BRU-SRM-01, MD-017, MD-022, MD-024, MD-031, DM-005]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: MD-021_Device_Category_Make_and_Model_Catalogue_BN.md
data_file: MD-021_Device_Category_Make_and_Model_Catalogue.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-01 — a service order cannot be created without an identified device
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/F_Asset_Equipment_and_Facilities/M17_Device_and_Customer_Asset_Registry.md
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-021 — Device Category, Make and Model Catalogue

> **`BRU-SRM-01` is a hard rule: no identified device, no service order.** This catalogue is what
> the rule identifies against. Its completeness directly limits how many orders can be created
> without an exception.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Catalogue & technical |
| Owning module | `M17` |
| Data steward | Technical catalogue analyst |
| Golden source | Manufacturer model lists plus observed service history |
| Refresh cadence | Monthly; new models added on first encounter |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `model_code` | char(10) | ✔ | `MDL-nnnnnn`, permanent | — |  |
| `device_family_code` | fk | ✔ | → §2.1 | — |  |
| `category_code` | fk | ✔ | Sub-family — laptop, split AC, smartphone | — |  |
| `brand_code` | fk |  | → `MD-017`; null for unbranded | — |  |
| `model_name` | text(160) | ✔ | As the manufacturer writes it — do-not-translate | — |  |
| `model_aliases` | text(400) |  | Semicolon-separated | — | Market names differ from official ones |
| `display_name_bn` | text(160) | ✔ |  | **✔** | Customer-facing device description |
| `serial_format_regex` | text(200) |  |  | — | Validates the serial at intake |
| `imei_applicable` | bool | ✔ |  | — | Mobile devices |
| `typical_fault_codes` | multi-fk |  | → `MD-024` | — | Seeds guided diagnosis |
| `parts_family_code` | fk |  | → `MD-022` | — | Compatibility root |
| `warranty_months_standard` | int |  |  | — | Manufacturer warranty |
| `service_applicable` | bool | ✔ |  | — | Whether we service it at all |
| `repair_level_required` | enum |  | L1 / L2 / L3_board | — | Minimum capability |
| `launch_year` | int |  |  | — | Drives obsolescence reporting |
| `active` | bool | ✔ |  | — |  |

### 2.1 Device families

| Code | Family |
|---|---|
| `DF-IT` | IT and computing — laptop, desktop, printer, monitor, projector, UPS |
| `DF-HA` | Home appliance — AC, refrigerator, washing machine, TV, oven, geyser |
| `DF-MB` | Mobile and tablet |
| `DF-SRV` | Server, storage and network |
| `DF-SEC` | CCTV, access control and security systems |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `brand_code` + `model_name` |
| Surrogate key | `model_code` |
| Code format | `MDL-nnnnnn` |
| Reuse policy | Never reused; device registry and service history reference it |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| MDL-01 | A service order requires a resolved `model_code`; an unresolved device requires a registration step (`BRU-SRM-01`) | **H** | `ERR-MDL-001` |
| MDL-02 | `imei_applicable` TRUE requires a 15-digit IMEI at intake | **H** | `ERR-MDL-002` |
| MDL-03 | Where `serial_format_regex` is present, the serial must match | **H** | `ERR-MDL-003` |
| MDL-04 | `display_name_bn` is mandatory | **H** | `ERR-MDL-004` |
| MDL-05 | A model with `service_applicable` FALSE cannot be booked | **H** | `ERR-MDL-005` |
| MDL-06 | Creating a model at intake is permitted but flags it for catalogue review | **A** | `ERR-MDL-006` |
| MDL-07 | A model with no parts family warns — parts cannot be planned for it | **S** | `WRN-MDL-007` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-017` Brand register | Before |
| `MD-024` Fault codes | Before or bind after |
| `MD-022` Parts families | Bind after |

| Depended on by |
|---|
| `M17` device registry · `MD-011` certifications · `MD-031` warranty · `M02` skill matching · `DM-005` device migration |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Manufacturer model lists; observed models in service history |
| Who supplies it | Technical catalogue analyst |
| Collection method | Bulk load from manufacturer lists, then continuous addition at intake with review |
| Known quality issues | Legacy device data is free text — "Dell laptop", "AC 1.5 ton". Expect low automated match rates on migration |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 20,000–60,000 models across five families | Continuous |
| SIT / UAT | 1,500 across all families, including deliberately ambiguous legacy strings | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Catalogue analyst; agents may create at intake with review flag |
| Who may deactivate | Technical Director |
| Approval required | Technical Director for family or applicability change |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
model_code,device_family_code,category_code,brand_code,model_name,display_name_bn,imei_applicable,warranty_months_standard,service_applicable,repair_level_required,active
MDL-000101,DF-IT,CAT-LAPTOP,BRD-011,Latitude 5420,ডেল ল্যাটিটিউড ৫৪২০,FALSE,36,TRUE,L2,TRUE
MDL-004512,DF-MB,CAT-SMARTPHONE,BRD-005,Galaxy A54 5G,স্যামসাং গ্যালাক্সি এ৫৪,TRUE,24,TRUE,L2,TRUE
MDL-009033,DF-HA,CAT-SPLIT-AC,BRD-022,Inverter Split 1.5 Ton,ইনভার্টার স্প্লিট এসি ১.৫ টন,FALSE,12,TRUE,L1,TRUE
```

---

## 10. Migration notes

`DM-005`. Legacy free-text device descriptions are matched where possible and loaded as unresolved where not; **unresolved devices are flagged, not discarded**.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md`](MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md) | Parts compatibility |
| [`MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md`](MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md) | Typical faults |
| `M17` Device and Customer Asset Registry | The implementing module |
| `KB-004`…`KB-007` Troubleshooting guide sets | Model-specific knowledge |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Technical Director (pending) |

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
