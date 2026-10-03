---
id: <CODE>-<nnn>
title: <Human readable title>
project: 1000FiX ERP System v2.0
content_type: Test script
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

# <Test Pack Name>

| Item | Value |
|---|---|
| Test level | SIT / UAT / Regression / Performance / Accessibility / Security |
| Role executing | `Rnn` |
| Modules covered | `Mnn` … |
| Portals covered | `Pnn` … |
| Environment | |
| Test data set | `TS-002` reference |
| Wave | |

## 1. Traceability
| Script ID | Requirement (`FR-XXX-nnn`) | Acceptance criterion (module §15) | Business rule |
|---|---|---|---|

## 2. Preconditions
| # | Precondition | How to establish |
|---|---|---|

## 3. Scripts
Repeat per script.

### `<SCRIPT-ID>` — <Title>
| Step | Action | Test data | Expected result | Actual | Pass/Fail | Evidence |
|---:|---|---|---|---|:--:|---|
| 1 | | | | | | |

**Negative and edge cases**
| # | Condition | Expected system behaviour |
|---|---|---|

**Bilingual check**
| Element | EN correct | BN correct | Truncation |
|---|:--:|:--:|:--:|

## 4. Exit Criteria
| Criterion | Threshold |
|---|---|

## 5. Defects Raised
| Defect ID | Script | Severity (`TS-018`) | Status |
|---|---|---|---|

## 6. Sign-off
| Role | Name | Date | Signature |
|---|---|---|---|

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

*Template: TPL_Test_Script.md · 1000FiX ERP Programme · CONFIDENTIAL*
