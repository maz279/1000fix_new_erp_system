---
id: MD-024
title: Fault, Symptom and Diagnostic Code Taxonomy
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Technical with Quality
author: Technical with Quality and BI
reviewers: [Quality, Operations, BI Lead, Localisation Lead, Warranty]
approver: Technical Director
content_class: C
purpose: >
  Structured customer-reported symptom codes and technician-confirmed fault codes by device family.
  Free-text fault capture makes first-time-fix measurement, failure-pattern analytics, brand quality
  reporting and AI triage impossible — all four at once.
traces_to: [M01, M31, M26, MD-021, MD-025, KB-008, SP-033, RP-001]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy_BN.md
data_file: MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/J_Data_Analytics_and_Intelligence/M26_AIML_Services_and_Model_Operations.md
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-024 — Fault, Symptom and Diagnostic Code Taxonomy

> **Symptom and fault are different things and must never share a code.**
>
> - A **symptom** is what the customer reports before anyone looks: "it does not turn on".
> - A **fault** is what the technician confirms: "power rail short on the mainboard".
>
> Conflating them destroys first-time-fix measurement, because you can no longer tell whether the
> diagnosis changed or the customer described it differently.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Catalogue & technical |
| Owning module | `M01` |
| Data steward | Technical analyst |
| Golden source | Technical fault definition workshops, validated against service history |
| Refresh cadence | Quarterly |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `code` | char(10) | ✔ | `SYM-nnnnn` or `FLT-nnnnn`, permanent | — |  |
| `code_type` | enum | ✔ | **symptom / fault** | — | Never mixed |
| `device_family_code` | fk | ✔ | → `MD-021` | — |  |
| `category_code` | fk | ✔ | Sub-family scope | — |  |
| `description_en` | text(200) | ✔ |  | — |  |
| `description_bn` | text(200) | ✔ |  | **✔** | Customer selects the symptom in `P01` |
| `parent_code` | fk |  | Self-reference; max depth 3 | — | Taxonomy tree |
| `severity` | enum |  | low / medium / high / safety | — | Faults only |
| `typical_repair_level` | enum |  | L1 / L2 / L3_board | — | Faults only; drives skill matching |
| `typical_resolution_codes` | multi-fk |  | → `MD-025` | — | Seeds guided repair |
| `typical_part_families` | multi-fk |  | → `MD-022` | — | Seeds parts forecasting |
| `is_customer_selectable` | bool | ✔ |  | — | Symptoms shown in the booking flow |
| `warranty_relevant` | bool | ✔ |  | — | Whether this fault is typically claimable |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `code_type` + `device_family_code` + `description_en` |
| Surrogate key | `code` |
| Code format | `SYM-nnnnn` / `FLT-nnnnn` |
| Reuse policy | Never reused; analytics depend on stable codes |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| FLT-01 | A service order must carry at least one symptom code at intake | **H** | `ERR-FLT-001` |
| FLT-02 | A service order may not be completed without a confirmed fault code | **H** | `ERR-FLT-002` |
| FLT-03 | `description_bn` is mandatory for customer-selectable symptoms | **H** | `ERR-FLT-003` |
| FLT-04 | A safety-severity fault triggers the HSE process (`SP-030`) and blocks routine closure | **H** | `ERR-FLT-004` |
| FLT-05 | Creating a fault code at job level is permitted but flags it for taxonomy review | **A** | `ERR-FLT-005` |
| FLT-06 | A fault used more than 50 times with no typical parts or resolution warns | **S** | `WRN-FLT-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-021` Device families | **Before** |
| `MD-025` Resolution codes | Bind after |
| `MD-022` Part families | Bind after |

| Depended on by |
|---|
| `M01` intake · `M31` workshop · `M26` AI triage · `SP-033` diagnostic decision trees · `KB-008` fault code library · `RP-001` first-time-fix |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Technical workshops per device family, validated against free-text history |
| Who supplies it | Technical Director with senior technicians |
| Collection method | Text-mining of legacy free-text fault notes to identify the real distribution, then structured definition |
| Known quality issues | Legacy fault data is free text in Bengali and English mixed; the top 100 strings cover most volume and are the starting point |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 1,500–4,000 codes across five families | Slow after initial build |
| SIT / UAT | 300 including the top symptom set for `P01` | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Technical analyst; technicians may propose at job level |
| Who may deactivate | Technical Director |
| Approval required | Technical Director; BI Lead consulted — code changes break trend series |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
code,code_type,device_family_code,description_en,description_bn,severity,typical_repair_level,is_customer_selectable,warranty_relevant,active
SYM-00101,symptom,DF-IT,Does not power on,চালু হচ্ছে না,,,TRUE,TRUE,TRUE
SYM-00220,symptom,DF-HA,Not cooling,ঠান্ডা হচ্ছে না,,,TRUE,TRUE,TRUE
FLT-01044,fault,DF-IT,Mainboard power rail short circuit,মেইনবোর্ড পাওয়ার রেইল শর্ট সার্কিট,high,L3_board,FALSE,TRUE,TRUE
FLT-02310,fault,DF-HA,Refrigerant leak at evaporator joint,ইভাপোরেটর জয়েন্টে রেফ্রিজারেন্ট লিক,medium,L2,FALSE,TRUE,TRUE
```

---

## 10. Migration notes

`DM-006`. Legacy free text is mapped to the new taxonomy where the top strings allow, and loaded as unmapped with the original text retained where not.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md`](MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md) | What was done about the fault |
| `SP-033` Diagnostic and Triage Decision Tree Library | Guided diagnosis |
| `KB-008` Fault Code Library and Interpretation Guide | Manufacturer code mapping |
| `M26` AI/ML Services and Model Operations | AI triage training data |

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
