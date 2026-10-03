---
id: <CODE>-<nnn>
title: <Human readable title>
project: 1000FiX ERP System v2.0
content_type: Master data
version: 0.1
date: <YYYY-MM-DD>
status: Draft            # Draft | Review | Approved | Published | Superseded
classification: CONFIDENTIAL — Internal Use Only
owner: <Accountable function>
author: <Name>
reviewers: [<function>, <function>]
approver: <Named approver>            # required for statutory/legal content (CG-007)
purpose: >
  <One sentence: what stops working if this file does not exist. Required by CP-03.>
traces_to: [<Mnn>, <Pnn>, <05-0n §n>, <FR-XXX-nnn>]   # Required by CP-04
priority: <P0|P1|P2|P3>
wave: <W0-W9>
bilingual: <yes|no>
bn_counterpart: <FILE_BN.md|n/a>
sources:
  - source: <primary source>
    verified: <YYYY-MM-DD>            # Required by CG-012 / CM-R8
supersedes: <file|none>
review_due: <YYYY-MM-DD>
---

# <Dataset Name> — Master Data Specification

> Governs `<CODE>-<nnn>_<Name>.csv` (or `.xlsx`). The markdown governs; the data file loads.

## 1. Purpose and Ownership
| Item | Value |
|---|---|
| Data domain | |
| Owning module | `Mnn` |
| Data steward | |
| Golden source | |
| Refresh cadence | |
| Environments | Dev / SIT / UAT / Prod |

## 2. Record Structure
| Column | Type | Required | Constraint | Bengali required | Description |
|---|---|:--:|---|:--:|---|

## 3. Keys and Identifiers
| Item | Rule |
|---|---|
| Natural key | |
| Surrogate key | |
| Code format | |
| Reuse policy | Codes are never reused (`CP-02` equivalent for data) |

## 4. Validation Rules
| # | Rule | Class (H/A/S/C) | Error message ID (`UI-004`) |
|---|---|:--:|---|

## 5. Relationships and Load Dependencies
| Depends on | Cardinality | Load order |
|---|---|---|

> Load order is consolidated in `MD-048`. Update both together.

## 6. Source of Truth and Acquisition
| Item | Value |
|---|---|
| Where the data comes from | |
| Who supplies it | |
| Collection method | |
| Known quality issues | |
| Cleansing rules applied | `DM-011` |

## 7. Volumes
| Environment | Expected rows | Growth |
|---|---:|---|

## 8. Change Control
| Item | Value |
|---|---|
| Who may add a record | |
| Who may deactivate | |
| Approval required | |
| Archive rule | Records are archived (`active = False`), never deleted (`05-02` DM-06) |

## 9. Sample Rows
```csv
```

## 10. Migration Notes
<Mapping to the corresponding `DM` workbook, if the dataset is migrated rather than authored.>

---

## Definition of Done

Tick every box before setting `status: Approved`. Full checklist in `CG-008`.

- [ ] Front matter complete, including `purpose:` and `traces_to:`
- [ ] Conforms to this template — no sections removed, none added without justification
- [ ] Every factual, statutory, pricing or capability claim carries a source and a verification date
- [ ] Terminology matches `CG-004`; Bengali terms match `BN-003`
- [ ] All internal links resolve
- [ ] Accessibility standard `CG-011` applied where user-facing
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — if `bilingual: yes`
- [ ] Named approver recorded — if statutory or legal (`CG-007`, `LG-001`)
- [ ] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] Decision(s) taken while authoring logged in `RF-006`

---

*Template: TPL_Master_Data_Specification.md · 1000FiX ERP Programme · CONFIDENTIAL*
