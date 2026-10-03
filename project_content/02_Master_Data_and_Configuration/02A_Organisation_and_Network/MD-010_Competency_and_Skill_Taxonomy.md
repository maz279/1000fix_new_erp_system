---
id: MD-010
title: Competency and Skill Taxonomy
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Quality
author: Learning & Development with Technical
reviewers: [Quality, Operations, HR, Dispatch]
approver: Quality Manager
content_class: C
purpose: >
  The skill tree by device family and repair level, with proficiency scale and expiry rules.
  Skill-based dispatch (M02), certification gating (BRU-SRM-09) and training design (M22) all
  consume it; without it dispatch cannot tell a board-level specialist from a first-line technician.
traces_to: [M22, M02, MD-011, MD-021, TR-002, TR-005]
priority: P1
wave: W2
bilingual: no
bn_counterpart: n/a
data_file: MD-010_Competency_and_Skill_Taxonomy.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M22_Learning_Competency_and_Certification.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-09 — certification gate on brand warranty work
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-010 — Competency and Skill Taxonomy

> A skill is what dispatch matches on and what training produces. If the two use different
> vocabularies, skill-based dispatch cannot work and training cannot be shown to have worked.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Workforce identity |
| Owning module | `M22` |
| Data steward | L&D analyst |
| Golden source | Technical Director skill definition, validated against actual repair practice |
| Refresh cadence | Per wave; on any new device family or repair level |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `skill_code` | char(9) | ✔ | `SKL-nnnnn`, permanent | — | |
| `skill_name` | text(120) | ✔ | | — | |
| `device_family_code` | fk | ✔ | → `MD-021` | — | IT, appliance, mobile, server, CCTV |
| `repair_level` | enum | ✔ | L1 / L2 / L3_board | — | |
| `skill_type` | enum | ✔ | technical / diagnostic / safety / process / soft | — | |
| `proficiency_scale` | enum | ✔ | aware / assisted / independent / expert / trainer | — | Five levels |
| `min_proficiency_for_dispatch` | enum | ✔ | | — | Dispatch gate |
| `requires_certification` | bool | ✔ | | — | Links to `MD-011` |
| `expiry_months` | int | | Required when `requires_certification` | — | |
| `assessment_required` | bool | ✔ | | — | |
| `prerequisite_skill_code` | fk | | Self-reference, no cycles | — | |
| `active` | bool | ✔ | | — | |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `device_family_code` + `skill_name` + `repair_level` |
| Surrogate key | `skill_code` |
| Reuse policy | Never reused; competency history references it |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| SKL-01 | `requires_certification` TRUE requires `expiry_months` | **H** | `ERR-SKL-001` |
| SKL-02 | A prerequisite chain may not contain a cycle | **H** | `ERR-SKL-002` |
| SKL-03 | An L3 board-level skill must require certification | **H** | `ERR-SKL-003` |
| SKL-04 | A skill may not be archived while any employee competency references it | **H** | `ERR-SKL-004` |
| SKL-05 | A safety skill may not have `min_proficiency_for_dispatch` below `independent` | **H** | `ERR-SKL-005` |
| SKL-06 | A skill with no assessment and no certification warns — it cannot be evidenced | **S** | `WRN-SKL-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-021` Device catalogue | Before — device families |
| `MD-011` Certification register | Same load, then bind |

| Depended on by |
|---|
| `MD-012` employee competency · `M02` skill-based dispatch · `TR-002` curriculum map · `TR-005` question bank |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Technical Director skill definition workshops |
| Who supplies it | Technical Director and senior technicians (L2/L3) |
| Collection method | Workshop per device family; validated against actual repair records |
| Known quality issues | No structured skill data exists today; skills are known informally by branch and workshop supervisors |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 200–400 skills across 5 device families × 3 levels | With device families |
| SIT / UAT | 40 — one family fully decomposed | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | L&D analyst |
| Who may deactivate | Quality Manager |
| Approval required | Quality Manager; Technical Director for a new repair level |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
skill_code,skill_name,device_family_code,repair_level,skill_type,proficiency_scale,min_proficiency_for_dispatch,requires_certification,expiry_months,active
SKL-00101,Laptop display assembly replacement,DF-IT,L1,technical,independent,independent,FALSE,,TRUE
SKL-00212,Laptop mainboard BGA rework,DF-IT,L3_board,technical,expert,expert,TRUE,24,TRUE
SKL-00330,Refrigerant handling and recovery,DF-HA,L2,safety,independent,independent,TRUE,36,TRUE
SKL-00501,Lithium battery safe handling,DF-MB,L1,safety,independent,independent,TRUE,12,TRUE
```

---

## 10. Migration notes

Not migrated — authored. `DM-009` maps existing technician grades to an initial proficiency, which is then verified by assessment rather than accepted.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-011_Certification_and_Brand_Authorisation_Register.md`](MD-011_Certification_and_Brand_Authorisation_Register.md) | Certification binding |
| `MD-021` Device Category, Make and Model Catalogue | Device families |
| `TR-002` Role-Based Curriculum Map | Training that produces these skills |
| `M02` Field Service and Dispatch Management | Skill-based assignment |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Quality Manager (pending) |

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
