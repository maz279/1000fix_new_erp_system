---
id: MD-008
title: Organisation Structure and Position Master
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: HR
author: HR with Finance
reviewers: [Finance, Operations, Security, Enterprise Architecture]
approver: HR Director
content_class: C
purpose: >
  Defines the organisation tree to position level, with reporting lines and cost-centre binding.
  Approvals, delegation, payroll, headcount and access control all resolve through position, not
  person — a leaver must not take an approval authority with them.
traces_to: [M21, M57, MD-002, MD-003, MD-036, SP-004, OP-015]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
data_file: MD-008_Organisation_Structure_and_Position_Master.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M21_Core_HR_and_Employee_Lifecycle.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §1 role register
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-008 — Organisation Structure and Position Master

> **Positions, not people.** A position is a seat with authority, a cost centre and a reporting
> line. People occupy positions and leave; the seat and its authority persist. Every approval
> limit in `SP-004` attaches here, not to a name.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Workforce identity |
| Owning module | `M21` |
| Data steward | HR systems analyst |
| Golden source | HR organisation chart, approved by the HR Director |
| Refresh cadence | Monthly; immediately on a restructure |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `position_code` | char(7) | ✔ | `POS-nnnn`, unique, permanent | — | |
| `entity_code` | fk | ✔ | → `MD-002` | — | |
| `org_unit_code` | fk | ✔ | → §2.1 | — | Department or team |
| `position_title` | text(120) | ✔ | | — | |
| `role_code` | fk | ✔ | → `MD-009` | — | Access and responsibility profile |
| `reports_to_position` | fk | | Self-reference; no cycles | — | |
| `branch_code` | fk | | → `MD-003` | — | Null for central positions |
| `cost_centre_code` | fk | ✔ | → `MD-036` | — | Payroll and cost attribution |
| `headcount_budgeted` | int | ✔ | ≥ 0 | — | |
| `is_approver` | bool | ✔ | | — | |
| `approval_limit_bdt` | decimal(14,2) | | Required when `is_approver` | — | Reconciles to `SP-004` |
| `delegate_position` | fk | | Self-reference | — | Pre-registered deputy |
| `employment_type` | enum | ✔ | permanent / contract / temporary | — | |
| `active` | bool | ✔ | | — | |

### 2.1 Organisation unit levels

`entity` → `division` → `department` → `team`. Maximum four levels; a fifth is a sign the tree
is modelling people rather than structure.

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `org_unit_code` + `position_title` + `branch_code` |
| Surrogate key | `position_code` |
| Reuse policy | Never reused. A deleted position's approval history references it |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| POS-01 | `reports_to_position` may not create a cycle | **H** | `ERR-POS-001` |
| POS-02 | An `is_approver` position must have an `approval_limit_bdt` | **H** | `ERR-POS-002` |
| POS-03 | The approval limit must not exceed the limit of `reports_to_position` | **H** | `ERR-POS-003` |
| POS-04 | Every position must have a `cost_centre_code` | **H** | `ERR-POS-004` |
| POS-05 | A position may not be archived while occupied | **H** | `ERR-POS-005` |
| POS-06 | Segregation-of-duties pairs from `SP-006` may not be held by one position | **H** | `ERR-POS-006` |
| POS-07 | Exceeding budgeted headcount requires HR Director approval | **A** | `ERR-POS-007` |
| POS-08 | An approver position with no registered delegate warns (`CG-007` §8) | **S** | `WRN-POS-008` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-002` Legal entity | Before |
| `MD-003` Branch master | Before |
| `MD-009` Role master | **Before** |
| `MD-036` Cost centre register | Before |

| Depended on by |
|---|
| `MD-004` custodians · `MD-012` employees · `SP-004` approval matrix · `OP-015` joiner-mover-leaver · every approval workflow |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | HR organisation chart |
| Who supplies it | HR, confirmed by each department head |
| Collection method | Structured extract from the HR system plus department-head confirmation |
| Known quality issues | Legacy HR systems commonly hold employees without positions, so reporting lines exist only in the chart |
| Cleansing rules | `DM-011`. Every employee in `MD-012` must resolve to a position here before payroll can run |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 600–800 positions for 500+ employees, including vacancies | With headcount |
| SIT / UAT | 60 — full approval chain from technician to CFO | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | HR systems analyst |
| Who may deactivate | HR Director, after POS-05 |
| Approval required | HR Director; CFO for any approval-limit change |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
position_code,entity_code,org_unit_code,position_title,role_code,reports_to_position,branch_code,cost_centre_code,headcount_budgeted,is_approver,approval_limit_bdt,employment_type,active
POS-0001,EN-01,OU-EXEC,Chief Executive Officer,R01,,,CC-1000,1,TRUE,99999999.00,permanent,TRUE
POS-0142,EN-01,OU-SCM,Warehouse Manager,R17,POS-0030,BR-0001,CC-4200,1,TRUE,500000.00,permanent,TRUE
POS-0311,EN-01,OU-OPS,Branch Store Keeper,R18,POS-0250,BR-0002,CC-2020,1,FALSE,,permanent,TRUE
POS-0480,EN-01,OU-OPS,Senior Technician,R10,POS-0250,BR-0002,CC-2020,4,FALSE,,permanent,TRUE
```

---

## 10. Migration notes

`DM-009` HR migration. Positions must be **created** from the org chart; they do not exist as records in most legacy HR systems.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-009_Role_and_Job_Title_Master.md`](MD-009_Role_and_Job_Title_Master.md) | Access profile per position |
| [`MD-012_Employee_Master_Data_Template.md`](MD-012_Employee_Master_Data_Template.md) | People occupying positions |
| `MD-036` Cost Centre and Dimension Register | Cost attribution |
| `SP-004` Approval Matrix and Delegation of Authority | Must reconcile exactly with `approval_limit_bdt` |
| `SP-006` Segregation of Duties Register | `POS-06` |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | HR Director (pending) |

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
