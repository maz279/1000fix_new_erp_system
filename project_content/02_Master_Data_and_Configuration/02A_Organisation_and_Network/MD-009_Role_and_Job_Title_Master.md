---
id: MD-009
title: Role and Job Title Master
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: HR with Security
author: HR and Security with Enterprise Architecture
reviewers: [Enterprise Architecture, Security, Operations, Localisation Lead]
approver: HR Director and CTO jointly
content_class: C
purpose: >
  Registers every access and responsibility role, with its portals, data scope and MFA requirement.
  05-04 registers 38 roles; audit 00-07 finding H2-07 found R39-R46 used in module files but never
  registered, and R54, R57 and R60 used and undefined anywhere. This dataset resolves that before
  access control is configured.
traces_to: [05-04, M29, M21, 00-07 H2-07, MD-008, OP-015, TS-017]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: MD-009_Role_and_Job_Title_Master_BN.md
data_file: MD-009_Role_and_Job_Title_Master.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §1 role register R01–R38 with headcount, portals, MFA and data scope
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-07 finding H2-07 — roles R39–R46 used but unregistered; R54, R57, R60 used and undefined
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-009 — Role and Job Title Master

> ⚠ **This dataset carries an open audit finding.** `05-04` registers **R01–R38**. Audit `00-07`
> H2-07 found:
>
> - **R39–R46** used in module specifications but never registered
> - **R54, R57, R60** used in module specifications and **undefined anywhere**
>
> Roles cannot be controlled terminology (`CG-004` `T-11`) until they are registered, and access
> control cannot be configured against roles that do not exist. **Resolving this is a
> prerequisite for W1 access configuration**, not a documentation tidy-up.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Workforce identity |
| Owning module | `M29` |
| Data steward | Security analyst |
| Golden source | `05-04` Role, Permission and Access Matrix |
| Refresh cadence | Per wave; immediately on a new role appearing in any module file |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `role_code` | char(3) | ✔ | `Rnn`, matches `05-04` | — | |
| `role_name_en` | text(120) | ✔ | Exactly as `05-04` registers it | — | Controlled term (`CG-004` `T-11`) |
| `role_name_bn` | text(120) | ✔ | | **✔** | Shown to Bengali-language users |
| `role_group` | enum | ✔ | executive / service_ops / logistics_scm / commercial / finance_people_gov / technology / external | — | `05-04` §1.1–§1.7 |
| `headcount_min` / `headcount_max` | int | ✔ | | — | From `05-04` |
| `portals` | multi-fk | ✔ | `P01`…`P12` | — | |
| `mfa_required` | bool | ✔ | | — | From `05-04` |
| `data_scope` | enum | ✔ | all_entities / all_branches / own_branch / own_zone / assigned_jobs / assigned_accounts / own_manifest / assigned_cases | — | Row-level security binding |
| `is_external` | bool | ✔ | | — | Sellers, vendors, brand partners, riders on contract |
| `registration_status` | enum | ✔ | **registered / used_unregistered / undefined** | — | Tracks the H2-07 finding |
| `sod_conflicts` | multi-fk | | → `SP-006` | — | |
| `active` | bool | ✔ | | — | |

### 2.1 Registration status — the H2-07 tracker

| Status | Meaning | Count at issue |
|---|---|---:|
| `registered` | Present in `05-04` §1 | 38 |
| `used_unregistered` | Used in module files, absent from `05-04` — **R39–R46** | 8 |
| `undefined` | Used in module files and defined nowhere — **R54, R57, R60** | 3 |
| | **Total to resolve** | **49** |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `role_name_en` |
| Surrogate key | `role_code` |
| Code format | `Rnn`, allocated **only** by `05-04` — this dataset cites, never allocates (`CG-005` `ID-07`) |
| Reuse policy | Never reused. `05-04` owns the space |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| ROL-01 | `role_code` must exist in `05-04`. A role with `registration_status` other than `registered` **may not be granted in production** | **H** | `ERR-ROL-001` |
| ROL-02 | `role_name_bn` is mandatory | **H** | `ERR-ROL-002` |
| ROL-03 | Every role must have at least one portal and a data scope | **H** | `ERR-ROL-003` |
| ROL-04 | A role with `data_scope = all_entities` must have `mfa_required = TRUE` | **H** | `ERR-ROL-004` |
| ROL-05 | An external role may not have a data scope broader than `assigned_accounts` | **H** | `ERR-ROL-005` |
| ROL-06 | A role may not be archived while any position references it | **H** | `ERR-ROL-006` |
| ROL-07 | Granting two roles that form an SoD conflict requires CFO or CTO approval, time-boxed (`00-04` §5.2) | **A** | `ERR-ROL-007` |
| ROL-08 | A role with `registration_status = undefined` blocks any configuration referencing it | **H** | `ERR-ROL-008` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `05-04` Role, Permission and Access Matrix | **Must be extended to 67-module scope first — audit finding AF-07** |
| `SP-006` Segregation of Duties Register | Before, for conflict pairs |

| Depended on by |
|---|
| `MD-008` positions · `MD-012` employees · `M29` access control · `OP-015` joiner-mover-leaver · `TS-017` security test cases · every `UI` role-scoped surface |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | `05-04` for registered roles; module-file extraction for the unregistered ones |
| Who supplies it | Security analyst, by extracting every `Rnn` citation across all 67 module and 12 portal files |
| Collection method | **Enumeration, not consultation** (`RG-06`) — grep every module file for role citations and reconcile |
| Known quality issues | 11 of 49 roles are unregistered or undefined (§2.1). Bengali role names do not exist anywhere yet |
| Cleansing rules | Each unregistered role is either registered in `05-04` with a definition, or the citing module file is corrected |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 49 to resolve; expected 42–46 after consolidation | Low |
| SIT / UAT | All roles — role-scoped access is tested exhaustively (`TS-017`) | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Security analyst, only after `05-04` registration |
| Who may deactivate | HR Director and CTO jointly |
| Approval required | **Both** HR Director and CTO |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
role_code,role_name_en,role_name_bn,role_group,headcount_min,headcount_max,portals,mfa_required,data_scope,is_external,registration_status,active
R01,Chief Executive Officer,প্রধান নির্বাহী কর্মকর্তা,executive,1,1,P03;P06,TRUE,all_entities,FALSE,registered,TRUE
R08,Service Centre Agent,সার্ভিস সেন্টার এজেন্ট,service_ops,150,250,P03,FALSE,own_branch,FALSE,registered,TRUE
R10,Senior Technician,সিনিয়র টেকনিশিয়ান,service_ops,80,150,P02,FALSE,assigned_jobs,FALSE,registered,TRUE
R16,Rider / Delivery Agent,রাইডার,logistics_scm,50,150,P09,FALSE,own_manifest,FALSE,registered,TRUE
R39,<to be defined>,<to be defined>,<tbd>,,,,,,,used_unregistered,FALSE
```

---

## 10. Migration notes

Not migrated. Authored from `05-04` and from module-file enumeration. Legacy access groups are **mapped to** these roles in `DM-009`, not the reverse.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-008_Organisation_Structure_and_Position_Master.md`](MD-008_Organisation_Structure_and_Position_Master.md) | Positions carry roles |
| [`../../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | `T-11` role names are controlled terms |
| `05-04` Role, Permission and Access Matrix | The allocating register |
| `SP-006` Segregation of Duties Register | Conflict pairs |
| `TS-017` Security and Privacy Test Case Pack | Verifies data scope |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | HR Director and CTO jointly (pending) |

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
