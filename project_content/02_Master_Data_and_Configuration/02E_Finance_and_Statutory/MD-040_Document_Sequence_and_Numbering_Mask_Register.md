---
id: MD-040
title: Document Sequence and Numbering Mask Register
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance with Enterprise Architecture
author: Finance with Enterprise Architecture
reviewers: [Tax, Legal, Audit, Platform Engineering]
approver: Chief Financial Officer
content_class: C
purpose: >
  Numbering masks for every document type, branch- and business-line-aware, with reset policy and
  statutory continuity rules. 05-02 DM-11 requires branch-aware sequences; statutory documents must
  be gap-free and auditable, and numbering cannot be retrofitted after go-live.
traces_to: [05-02 DM-11, M30, M19, MD-002, MD-003, DT-001, DT-010]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
data_file: MD-040_Document_Sequence_and_Numbering_Mask_Register.csv
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §1 DM-11 — branch- and business-line-aware sequences with configurable masks
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# MD-040 — Document Sequence and Numbering Mask Register

> **A gap in a statutory sequence is an audit finding.** Every Mushak challan number must be
> accounted for — issued, cancelled or void — with no unexplained gaps, for at least the
> five-year retention period.
>
> Sequences cannot be retrofitted. This loads before the first transaction.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Finance & statutory |
| Owning module | `M30` |
| Data steward | Finance systems analyst |
| Golden source | CFO-approved numbering policy |
| Refresh cadence | Annual; reset policy at fiscal year end |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |

---

## 2. Record structure

| Column | Type | Req | Constraint | BN | Description |
|---|---|:--:|---|:--:|---|
| `sequence_code` | char(10) | ✔ | `SEQ-nnnnn`, permanent | — |  |
| `document_type` | fk | ✔ | → `DT-nnn` | — | Which document it numbers |
| `entity_code` | fk | ✔ | → `MD-002` | — |  |
| `branch_code` | fk |  | → `MD-003`; null = entity-wide | — | **Branch-aware (`DM-11`)** |
| `business_line_code` | fk |  | → `MD-036` | — |  |
| `mask` | text(80) | ✔ | e.g. `INV-{entity}-{branch}-{yy}-{seq:06d}` | — |  |
| `current_value` | bigint | ✔ |  | — | Never decremented |
| `padding` | int | ✔ |  | — |  |
| `reset_policy` | enum | ✔ | never / fiscal_year / calendar_year / monthly | — |  |
| `is_statutory` | bool | ✔ |  | — | **Gap-free required** |
| `gap_policy` | enum | ✔ | no_gaps / gaps_recorded | — | Statutory must be `no_gaps` |
| `prefix_reserved` | bool | ✔ |  | — | Prefix may not be reused across entities |
| `active` | bool | ✔ |  | — |  |

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `document_type` + `entity_code` + `branch_code` |
| Surrogate key | `sequence_code` |
| Code format | `SEQ-nnnnn` |
| Reuse policy | **Never reused.** A retired sequence prefix is never reissued — a duplicate document number is unresolvable in an audit |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| SEQ-01 | A statutory sequence must be `no_gaps`; a cancelled number is recorded as cancelled, never skipped | **H** | `ERR-SEQ-001` |
| SEQ-02 | `current_value` may never be decremented or manually set backwards | **H** | `ERR-SEQ-002` |
| SEQ-03 | A mask must produce a unique value across all entities and branches | **H** | `ERR-SEQ-003` |
| SEQ-04 | Changing a mask mid-period is prohibited for statutory sequences | **H** | `ERR-SEQ-004` |
| SEQ-05 | Reset policy for a statutory sequence requires CFO and adviser confirmation | **A** | `ERR-SEQ-005` |
| SEQ-06 | A sequence approaching its padding ceiling warns at 90% | **S** | `WRN-SEQ-006` |

---

## 5. Relationships and load dependencies

| Depends on | Load order |
|---|---|
| `MD-002` Legal entity | **Before** |
| `MD-003` Branches | **Before** |

| Depended on by |
|---|
| **Every document the system issues** · `DT-001`…`DT-044` · `M19` postings · audit trail |

> Load order is consolidated in `MD-048`. Update both together (`CM-R1`).

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | CFO-approved numbering policy |
| Who supplies it | Finance with Enterprise Architecture |
| Collection method | Design workshop; statutory sequences confirmed with the tax adviser |
| Known quality issues | Legacy numbering is per-branch spreadsheets with known gaps and at least one duplicate range |
| Cleansing rules | `DM-011` |

---

## 7. Volumes

| Environment | Rows | Growth |
|---|---:|---|
| Prod | 300–800 sequences — document type × entity × branch | Low |
| SIT / UAT | All statutory sequences plus a representative operational set | |

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add | Finance systems analyst |
| Who may deactivate | CFO |
| Approval required | **CFO**; adviser confirmation for statutory sequences |
| Effective dating | Not effective-dated |
| Archive rule | Archived (`active = False`), never deleted (`05-02` DM-06) |
| Logged in | `RF-006` for structural change |

---

## 9. Sample rows

```csv
sequence_code,document_type,entity_code,branch_code,mask,current_value,padding,reset_policy,is_statutory,gap_policy,active
SEQ-00101,DT-010,EN-01,BR-0001,MUSHAK-{entity}-{branch}-{fy}-{seq},0,6,fiscal_year,TRUE,no_gaps,TRUE
SEQ-00250,DT-002,EN-01,BR-0002,INT-{branch}-{yy}-{seq},0,6,calendar_year,FALSE,gaps_recorded,TRUE
SEQ-00410,DT-016,EN-01,BR-0002,RCP-{branch}-{yy}-{seq},0,6,calendar_year,TRUE,no_gaps,TRUE
```

---

## 10. Migration notes

Sequences start at the legacy high-water mark plus a safety margin, **never at 1**, to avoid colliding with migrated documents (`DM-014`).

---

## 11. Related documents

| Document | Relationship |
|---|---|
| `DT-001` Document Template Standard and Branding Rules | Where the number is printed |
| `DT-010` Tax Invoice Mushak 6.3 | The primary statutory sequence |
| [`MD-003_Branch_and_Service_Centre_Master.md`](../02A_Organisation_and_Network/MD-003_Branch_and_Service_Centre_Master.md) | Branch awareness |

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
