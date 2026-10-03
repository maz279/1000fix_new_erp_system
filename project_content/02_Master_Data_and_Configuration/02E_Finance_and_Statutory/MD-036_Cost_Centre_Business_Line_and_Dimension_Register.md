---
id: MD-036
title: Cost Centre, Business Line and Dimension Register
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance
author: Finance with Enterprise Architecture
reviewers: [Operations, Commercial, BI Lead, Enterprise Architecture]
approver: Chief Financial Officer
content_class: C
purpose: >
  Cost centres, the fourteen revenue-stream business lines, and the zone and branch analytic
  dimensions. 05-02 DM-03 requires every transactional model to carry these; profitability by
  revenue stream is a board-level commitment that cannot be met without them.
traces_to: [05-02 DM-03, M54, M19, MD-002, MD-003, MD-008, MD-019, RP-001]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
data_file: MD-036_Cost_Centre_Business_Line_and_Dimension_Register.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §1 DM-03 — every transactional model carries company_id, operating_unit_id, and where relevant zone_id, cost_center_id, business_line_id
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/README.md — the fourteen revenue streams
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-036 — Cost Centre, Business Line and Dimension Register

> **Fourteen revenue streams is the commitment.** `business_line` is the dimension that makes it
> measurable. A transaction posted without it is revenue that cannot be attributed to a stream.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Finance & statutory |
| Owning module | `M54` |
| Data steward | Finance systems analyst |
| Golden source | CFO-approved dimension model |
| Refresh cadence | Annual; on any organisational or revenue-stream change |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `dimension_code` | char(10) | ✔ | `CC-nnnn` / `BL-nn` / `ZN-nnn`, permanent | — |  |
| `dimension_type` | enum | ✔ | cost_centre / business_line / zone / branch | — |  |
| `name` | text(120) | ✔ |  | — |  |
| `parent_code` | fk |  | Self-reference; cost centres only | — |  |
| `entity_code` | fk | ✔ | → `MD-002` | — |  |
| `revenue_stream_no` | int |  | 1–14; business lines only | — | **Binds to the fourteen** |
| `owner_position_code` | fk |  | → `MD-008` | — | Accountable for the P&L |
| `is_profit_centre` | bool | ✔ |  | — | Carries revenue as well as cost |
| `budget_owner_position` | fk |  | → `MD-008` | — |  |
| `mandatory_on` | multi-enum | ✔ | revenue / cogs / opex / payroll / capex | — | Where posting requires it |
| `effective_from` | date | ✔ |  | — |  |
| `active` | bool | ✔ |  | — |  |

### 2.1 The fourteen business lines

`BL-01` authorised brand warranty service · `BL-02` out-of-warranty paid repair ·
`BL-03` AMC/RAMC contracts · `BL-04` warranty extension and protection ·
`BL-05` spare parts and accessories · `BL-06` corporate managed IT services ·
`BL-07` equipment rental · `BL-08` data recovery · `BL-09` data backup subscriptions ·
`BL-10` refurbished device resale · `BL-11` trade-in margin · `BL-12` e-waste recovery ·
`BL-13` marketplace commission · `BL-14` advertising and lead placement

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `dimension_type` + `name` |
| Surrogate key | `dimension_code` |
| Code format | Prefixed by type |
| Reuse policy | Never reused; postings reference it |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| DIM-01 | A posting to an account with `requires_dimension` must carry every listed dimension | **H** | `ERR-DIM-001` |
| DIM-02 | Exactly fourteen active business lines; adding a fifteenth requires Board approval | **H** | `ERR-DIM-002` |
| DIM-03 | A profit centre must have an owner position | **H** | `ERR-DIM-003` |
| DIM-04 | A dimension may not be archived with open postings in the current period | **H** | `ERR-DIM-004` |
| DIM-05 | Reassigning a cost-centre parent mid-year requires CFO approval — it breaks comparatives | **A** | `ERR-DIM-005` |
| DIM-06 | A business line with no revenue in a quarter warns | **S** | `WRN-DIM-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-002` Legal entity | Before |
| `MD-003` Branches | Before |
| `MD-008` Positions | Before or bind after |

| Depended on by |
|---|
| `MD-035` chart of accounts · `MD-019` catalogue revenue-stream binding · `M54` FP&A · `RP-001` KPI dictionary · every posting |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | CFO-approved dimension model; the fourteen streams from the business plan |
| Who supplies it | CFO with Enterprise Architecture |
| Collection method | Design workshop; business lines taken directly from the approved revenue-stream list |
| Known quality issues | Legacy accounting has no dimension model; cost centres are embedded in account codes |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 200–500 cost centres; exactly 14 business lines; 60–150 zones | Low |
| SIT / UAT | All business lines plus 30 cost centres | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Finance systems analyst |
| Who may deactivate | CFO |
| Approval required | CFO; **Board for a business line** |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
dimension_code,dimension_type,name,entity_code,revenue_stream_no,is_profit_centre,mandatory_on,effective_from,active
BL-02,business_line,Out-of-warranty paid repair,EN-01,2,TRUE,revenue;cogs,2026-07-01,TRUE
BL-13,business_line,Marketplace commission and settlement,EN-01,13,TRUE,revenue,2027-01-01,TRUE
CC-2020,cost_centre,Agrabad Service Centre,EN-01,,TRUE,revenue;cogs;opex;payroll,2026-07-01,TRUE
CC-4200,cost_centre,Central Warehouse,EN-01,,FALSE,opex;payroll,2026-07-01,TRUE
```

---

## 10. Migration notes

`DM-008`. Legacy postings are mapped to dimensions where derivable; historical comparatives are restated once and the restatement retained.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`MD-035_Chart_of_Accounts_Bangladesh.md`](MD-035_Chart_of_Accounts_Bangladesh.md) | Which accounts require which dimensions |
| `RP-001` KPI Dictionary and Metric Definition Standard | Dimension-keyed metrics |
| `M54` Cost Accounting, Budgeting and FP&A | The implementing module |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Chief Financial Officer (pending) |

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
