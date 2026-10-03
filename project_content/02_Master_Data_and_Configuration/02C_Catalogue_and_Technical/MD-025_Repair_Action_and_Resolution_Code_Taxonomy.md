---
id: MD-025
title: Repair Action and Resolution Code Taxonomy
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Technical with Quality
author: Technical with Quality
reviewers: [Quality, Warranty, Finance, Localisation Lead, BI Lead]
approver: Technical Director
content_class: C
purpose: >
  What was actually done: action codes, parts-versus-labour resolution and rework classification.
  Warranty claims are rejected without standard resolution coding, and repair-time norms and job
  costing both depend on it.
traces_to: [M31, M09, MD-024, MD-022, KB-014, RP-001, DT-007]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: MD-025_Repair_Action_and_Resolution_Code_Taxonomy_BN.md
data_file: MD-025_Repair_Action_and_Resolution_Code_Taxonomy.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M31_Workshop_and_Depot_Repair_Management.md
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-025 — Repair Action and Resolution Code Taxonomy

> A brand partner does not reimburse "fixed". They reimburse a named action against a named fault
> with named parts. This taxonomy is what makes a claim payable.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Catalogue & technical |
| Owning module | `M31` |
| Data steward | Technical analyst |
| Golden source | Technical action definition, validated against completed jobs |
| Refresh cadence | Quarterly |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `resolution_code` | char(10) | ✔ | `RES-nnnnn`, permanent | — |  |
| `action_class` | enum | ✔ | repair / replace_part / replace_unit / configure / clean / calibrate / no_fault_found / customer_declined / beyond_economic_repair | — |  |
| `description_en` | text(200) | ✔ |  | — |  |
| `description_bn` | text(200) | ✔ |  | **✔** | Appears on `DT-007` service report |
| `device_family_code` | fk | ✔ | → `MD-021` | — |  |
| `applicable_fault_codes` | multi-fk |  | → `MD-024` | — |  |
| `requires_part` | bool | ✔ |  | — | Blocks closure without a part issue |
| `standard_minutes` | int | ✔ |  | — | **Labour norm — feeds `KB-014` and costing** |
| `repair_level` | enum | ✔ | L1 / L2 / L3_board | — |  |
| `warranty_claimable` | bool | ✔ |  | — | Whether a brand claim may cite it |
| `grants_repair_warranty` | bool | ✔ |  | — | Triggers `MD-031` repair warranty |
| `is_rework_eligible` | bool | ✔ |  | — | Counts toward `BRU-SRM-06` rework detection |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `action_class` + `device_family_code` + `description_en` |
| Surrogate key | `resolution_code` |
| Code format | `RES-nnnnn` |
| Reuse policy | Never reused |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| RES-01 | A job may not be completed without at least one resolution code | **H** | `ERR-RES-001` |
| RES-02 | `requires_part` TRUE blocks completion until a part is issued against the job | **H** | `ERR-RES-002` |
| RES-03 | A warranty claim may only cite resolutions with `warranty_claimable` TRUE | **H** | `ERR-RES-003` |
| RES-04 | `no_fault_found` requires a supervisor countersignature | **A** | `ERR-RES-004` |
| RES-05 | `beyond_economic_repair` requires a recorded customer decision | **H** | `ERR-RES-005` |
| RES-06 | Actual time exceeding `standard_minutes` by more than 100% warns for norm review | **S** | `WRN-RES-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-021` Device families | Before |
| `MD-024` Fault codes | **Before** |
| `MD-022` Parts | Before |

| Depended on by |
|---|
| `M31` workshop · `M09` claims · `DT-007` service report · `KB-014` repair time standards · `RP-001` first-time-fix and rework metrics |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Technical action definition workshops |
| Who supplies it | Technical Director with workshop supervisors |
| Collection method | Workshop; standard minutes derived from observed job durations, not estimated |
| Known quality issues | Legacy resolution data is free text; standard times do not exist anywhere |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 800–2,500 codes | Low |
| SIT / UAT | 200 across all action classes | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Technical analyst |
| Who may deactivate | Technical Director |
| Approval required | Technical Director; Finance for a `standard_minutes` change — it drives costing |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
resolution_code,action_class,description_en,description_bn,device_family_code,requires_part,standard_minutes,repair_level,warranty_claimable,grants_repair_warranty,is_rework_eligible,active
RES-00101,replace_part,Display panel replaced,ডিসপ্লে প্যানেল প্রতিস্থাপন করা হয়েছে,DF-IT,TRUE,60,L2,TRUE,TRUE,TRUE,TRUE
RES-00455,clean,AC jet wash and coil clean,এসি জেট ওয়াশ ও কয়েল পরিষ্কার,DF-HA,FALSE,90,L1,FALSE,FALSE,FALSE,TRUE
RES-00990,no_fault_found,No fault found on inspection,পরীক্ষায় কোনো ত্রুটি পাওয়া যায়নি,DF-IT,FALSE,30,L1,FALSE,FALSE,TRUE,TRUE
```

---

## 10. Migration notes

`DM-006`. Same approach as `MD-024` — map the top free-text strings, retain the original where unmapped.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md`](MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md) | The fault this resolves |
| `KB-014` Repair Time Standards and Labour Norms | Standard minutes |
| `DT-007` Service Completion Report | Where the resolution is printed |
| `M09` Warranty, Protection Plans and Claims | Claim citation |

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
