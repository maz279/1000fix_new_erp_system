---
id: MD-048
title: Master Data Seed Load Workbook Index
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: MDM Lead with Data Migration
author: MDM with Data Migration
reviewers: [All domain owners, Data Migration Lead, Platform Engineering, QA Lead]
approver: MDM Lead
content_class: E
purpose: >
  The index of all loadable data files, load order, dependency graph, environment targets and reload
  policy. Forty-seven datasets loaded in the wrong order fail on foreign keys; load sequence is
  itself a deliverable, not an operational detail.
traces_to: [M64, MD-001, DM-003, DM-012, DM-013, DM-014]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
data_file: MD-048_Load_Sequence.csv
effective_dated: no
sources:
  - source: project_content/02_Master_Data_and_Configuration/ — the 47 dataset specifications, enumerated 2026-08-15
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §1 DM-12 — foreign keys enforced at the database level
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-048 — Master Data Seed Load Workbook Index

> **`05-02` DM-12 enforces foreign keys at the database level.** That is correct, and it means a
> dataset loaded before its parent does not warn — it fails.
>
> This index is the load order. It is derived from the dependency declarations in §5 of each of
> the other 47 files, **by enumeration, not by recollection**.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Workforce & asset |
| Owning module | `M64` |
| Data steward | MDM Lead |
| Golden source | This index |
| Refresh cadence | Per wave; before every environment load |
| Environments | Dev · SIT · UAT · Prod |
| Content class | E — Internal governance |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `load_seq` | int | ✔ | Ascending; ties may load in parallel | — |  |
| `dataset_id` | fk | ✔ | → `MD-nnn` | — |  |
| `data_file` | text(120) | ✔ | The `.csv` or `.xlsx` to load | — |  |
| `load_wave` | enum | ✔ | W0…W9 | — |  |
| `depends_on` | multi-fk | ✔ | → `MD-nnn` | — | **From each file's §5** |
| `target_environments` | multi-enum | ✔ | dev / sit / uat / prod | — |  |
| `reload_policy` | enum | ✔ | full_replace / upsert / append_only / never_reload | — |  |
| `masking_required` | bool | ✔ |  | — | **S3 data in non-production (`NFR-086c`)** |
| `row_count_expected` | int |  |  | — | Reconciliation control |
| `validation_script` | text(120) |  |  | — | Post-load check |
| `owner_signoff_required` | bool | ✔ |  | — | Domain owner confirms before prod |
| `active` | bool | ✔ |  | — |  |

### 2.1 Load tiers

| Tier | Datasets | Rationale |
|---|---|---|
| **0 — Foundation** | `MD-001`, `MD-006`, `MD-023`, `MD-039` | No dependencies |
| **1 — Entity and chart** | `MD-002`, `MD-035`, `MD-036`, `MD-041` | Entity before everything financial |
| **2 — Network** | `MD-003`, `MD-005`, `MD-007`, `MD-004` | Branch before locations and zones |
| **3 — Workforce structure** | `MD-009`, `MD-008`, `MD-012`, `MD-042` | Roles before positions before people |
| **4 — Tax and finance config** | `MD-037`, `MD-038`, `MD-040`, `MD-044` | Chart before tax before sequences |
| **5 — Catalogue** | `MD-021`, `MD-019`, `MD-022`, `MD-024`, `MD-025`, `MD-026`, `MD-027`, `MD-020` | Devices before items before parts |
| **6 — Commercial** | `MD-014`, `MD-028`, `MD-029`, `MD-030`, `MD-031`, `MD-032` | Segments before SLA before pricing |
| **7 — Party and ecosystem** | `MD-013`, `MD-015`, `MD-016`, `MD-017` | After catalogue and commercial |
| **8 — Competency and asset** | `MD-010`, `MD-011`, `MD-045`, `MD-046`, `MD-047` | After workforce and asset classes |
| **9 — Deferred** | `MD-018`, `MD-033`, `MD-034`, `MD-043` | Later waves |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `dataset_id` |
| Surrogate key | `load_seq` |
| Code format | Integer sequence |
| Reuse policy | Sequence numbers may be renumbered; dataset IDs may not |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| LDX-01 | A dataset may not load before every entry in its `depends_on` has loaded successfully | **H** | `ERR-LDX-001` |
| LDX-02 | `masking_required` TRUE blocks an unmasked load to any non-production environment (`NFR-086c`) | **H** | `ERR-LDX-002` |
| LDX-03 | A production load requires the domain owner's recorded sign-off | **H** | `ERR-LDX-003` |
| LDX-04 | Row count must match `row_count_expected` within tolerance, or the load is rolled back | **H** | `ERR-LDX-004` |
| LDX-05 | `never_reload` datasets may not be reloaded to production without CFO or CTO approval | **A** | `ERR-LDX-005` |
| LDX-06 | A dataset in this index with no corresponding `MD` specification is rejected | **H** | `ERR-LDX-006` |
| LDX-07 | An `MD` specification with no entry in this index warns — it will never load | **S** | `WRN-LDX-007` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| Every `MD-002`…`MD-047` specification | **This index is derived from them** |

| Depended on by |
|---|
| `DM-003` entity migration sequencing · `DM-012` load templates · `DM-014` cutover checklist · every environment build |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | The §5 dependency declarations of all 47 dataset specifications |
| Who supplies it | MDM Lead |
| Collection method | **Enumeration** (`RG-06`) — extract every `Depends on` table and topologically sort it |
| Known quality issues | A dependency omitted from a source file produces a load failure that looks like a data problem |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 47 dataset entries | Low |
| SIT / UAT | All entries — the load sequence is exercised on every environment build | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | MDM Lead |
| Who may deactivate | MDM Lead |
| Approval required | MDM Lead; **domain owner sign-off per dataset before production** |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
load_seq,dataset_id,data_file,load_wave,depends_on,target_environments,reload_policy,masking_required,owner_signoff_required,active
10,MD-006,MD-006_Bangladesh_Geographic_Hierarchy.csv,W1,,dev;sit;uat;prod,full_replace,FALSE,TRUE,TRUE
20,MD-002,MD-002_Legal_Entity_and_Company_Master.csv,W1,MD-007,dev;sit;uat;prod,never_reload,FALSE,TRUE,TRUE
30,MD-035,MD-035_Chart_of_Accounts_Bangladesh.csv,W1,MD-002,dev;sit;uat;prod,never_reload,FALSE,TRUE,TRUE
90,MD-012,MD-012_Employee_Master_Data_Template.csv,W1,MD-002;MD-003;MD-008;MD-009,dev;sit;uat;prod,upsert,TRUE,TRUE,TRUE
```

---

## 10. Migration notes

This index governs both seed loading and migration loading. `DM-003` sequences the **transactional** migration that follows it.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`../02A_Organisation_and_Network/MD-001_Master_Data_Governance_Charter.md`](../02A_Organisation_and_Network/MD-001_Master_Data_Governance_Charter.md) | The charter governing all 47 |
| `DM-003` Entity Migration Priority and Sequencing Plan | Transactional sequencing |
| `DM-012` Migration Load Template Pack | The load templates |
| `DM-013` Reconciliation and Validation Report Specification | Post-load reconciliation |
| `M64` Master Data Management and Configuration | The implementing module |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | MDM Lead (pending) |

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
