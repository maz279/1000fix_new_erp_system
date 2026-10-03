---
id: MD-001
title: Master Data Governance Charter
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: MDM Lead (`M64`)
author: Enterprise Architecture with MDM
reviewers: [Finance, Operations, HR, Data Migration Lead, Programme Content Lead]
approver: Architecture Review Board
content_class: E
purpose: >
  Assigns ownership, stewardship and change control for all 47 master datasets in this
  category. M64 requires single ownership per entity; without a charter, 47 datasets acquire 47
  conflicting owners and the golden-record rule cannot be enforced.
traces_to: [M64, 05-02, MD-048, CG-002, DM-011]
priority: P0
wave: W0
bilingual: no
bn_counterpart: n/a
data_file: n/a
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M64_Master_Data_Management_and_Configuration.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §1 modelling standards DM-01…DM-15
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-001 — Master Data Governance Charter

> **This file governs the other 47.** Read it before authoring any `MD` file.
>
> Master data is the only content class where a defect is silently amplified: a wrong branch
> code does not fail, it posts 40,000 transactions to the wrong place and is discovered at
> month-end close.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | All — this file governs the other 47 |
| Owning module | `M64` |
| Data steward | MDM Lead |
| Golden source | This charter |
| Refresh cadence | Reviewed every two waves |
| Environments | Dev · SIT · UAT · Prod |
| Content class | E — Internal governance |
| Effective-dated | no |

---

## 2. Record structure

This file is a charter, not a dataset. Its structure is the domain register below.

### 2.1 Data domain register

| Domain | Datasets | Data owner | Data steward | Approver |
|---|---|---|---|---|
| Organisation & network | `MD-002`…`MD-008` | Operations Director | Operations MDM analyst | Ops Director |
| Workforce identity | `MD-009`…`MD-012`, `MD-042` | HR Director | HR systems analyst | HR Director |
| Party & ecosystem | `MD-013`…`MD-018` | Chief Commercial Officer | MDM Lead | CCO |
| Catalogue & technical | `MD-019`…`MD-028` | Chief Commercial Officer / Technical Director | Catalogue analyst | CCO |
| Commercial & pricing | `MD-029`…`MD-034` | Chief Commercial Officer | Pricing analyst | CCO |
| Finance & statutory | `MD-035`…`MD-041` | Chief Financial Officer | Finance systems analyst | CFO |
| Asset & equipment | `MD-044`…`MD-047` | Operations Director | Facilities analyst | Ops Director |

### 2.2 Roles

| Role | Accountable for |
|---|---|
| **Data owner** | The business meaning of the domain. One executive, named, per domain |
| **Data steward** | Day-to-day quality, additions, corrections, exception handling |
| **Approver** | Signing that a dataset may be loaded to production |
| **MDM Lead** | The charter, the load sequence (`MD-048`), cross-domain arbitration |

---

## 3. Keys and identifiers

### 3.1 Golden-record rules

| # | Rule |
|---|---|
| **GR-01** | Every entity in `05-02` has exactly **one** owning dataset in this category. A field maintained in two datasets is a defect |
| **GR-02** | Where two systems hold the same attribute, one is declared authoritative and the other synchronises. `05-03` IP-01 already states this for integrations |
| **GR-03** | Survivorship on merge follows `DM-011`: most-recently-verified wins; a manually verified value beats an automatically derived one |
| **GR-04** | A code is **never reused**, even after archive. This mirrors `RG-02` and `CG-005` `ID-03` |
| **GR-05** | Records are **archived** (`active = False`), never hard-deleted (`05-02` DM-06) |

### 3.2 Code format standard

All master-data codes across the 47 datasets follow one form unless a statutory instrument
dictates otherwise:

```
<PREFIX>-<SEQ>          e.g. BR-0007, ZN-014, PT-000481
```

| # | Rule |
|---|---|
| **CF-01** | Upper-case Latin prefix, 2–4 characters, unique per dataset |
| **CF-02** | Zero-padded numeric sequence, width fixed at creation, never widened later |
| **CF-03** | No embedded meaning — a code never encodes a branch, a year or a category, because all three change |
| **CF-04** | ASCII only. Never Bengali script in a code (`CG-005` `ID-08`) |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| GOV-01 | A dataset without a named owner, steward and approver may not be loaded to production | **H** | `ERR-MDM-001` |
| GOV-02 | A record may not be created in a dataset whose load dependencies are unloaded | **H** | `ERR-MDM-002` |
| GOV-03 | A code matching a previously archived code is rejected | **H** | `ERR-MDM-003` |
| GOV-04 | A change to an effective-dated dataset without an effective date is rejected | **H** | `ERR-MDM-004` |
| GOV-05 | A bulk change above 500 records requires the data owner's approval | **A** | `ERR-MDM-005` |
| GOV-06 | A record with a data-quality score below threshold is flagged for stewardship | **S** | `WRN-MDM-006` |

---

## 5. Relationships and load dependencies

| This charter depends on | Why |
|---|---|
| `05-02` Data Model and Entity Catalogue | The entities `GR-01` assigns |
| `M64` Master Data Management | The module implementing this governance |
| `CG-002` Content Operating Model | The accountability model this specialises |

**Nothing depends on loading this file** — it is a charter, loaded before any dataset.

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | Authored by Enterprise Architecture with each domain owner |
| Who supplies it | Domain owners confirm their accountability in writing |
| Collection method | Workshop per domain, minuted, signed |
| Known quality issues | Several domain owner roles are not yet appointed — see §8 |
| Cleansing rules | n/a |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| All | 7 domains, 47 datasets | Grows only when a dataset is added to the register |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add a domain | MDM Lead with Architecture Review Board approval |
| Who may reassign an owner | Architecture Review Board |
| Approval required | Yes, for any ownership change |
| Archive rule | Records are archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` |

### 8.1 Open — domain owners not yet named

`CG-002` §3 rule `CO-01` requires no unassigned function. The **data owner** column in §2.1
names offices, not people. `RF-010` must name the individuals before W1 load.

---

## 9. Sample rows

```csv
domain_code,domain_name,dataset_range,data_owner_role,steward_role,approver_role,active
ORG,Organisation and network,MD-002..MD-008,Operations Director,Operations MDM analyst,Operations Director,TRUE
WFI,Workforce identity,MD-009..MD-012;MD-042,HR Director,HR systems analyst,HR Director,TRUE
PTY,Party and ecosystem,MD-013..MD-018,Chief Commercial Officer,MDM Lead,Chief Commercial Officer,TRUE
FIN,Finance and statutory,MD-035..MD-041,Chief Financial Officer,Finance systems analyst,Chief Financial Officer,TRUE
```

---

## 10. Migration notes

Not migrated. Authored at W0 before any dataset is designed.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-048_Master_Data_Seed_Load_Workbook_Index.md`](../02F_Workforce_and_Asset/MD-048_Master_Data_Seed_Load_Workbook_Index.md) | The load sequence this charter governs |
| [`../../00_Content_Governance_and_Standards/CG-002_Content_Operating_Model_and_RACI.md`](../../00_Content_Governance_and_Standards/CG-002_Content_Operating_Model_and_RACI.md) | The accountability model |
| `M64` Master Data Management and Configuration | The implementing module |
| `DM-011` Data Quality Rules, Cleansing and Deduplication Standard | Survivorship rules |
| `05-02` Data Model and Entity Catalogue | Entity ownership |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Architecture Review Board (pending) |

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
