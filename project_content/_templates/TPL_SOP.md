---
id: <CODE>-<nnn>
title: <Human readable title>
project: 1000FiX ERP System v2.0
content_type: SOP
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

# SOP — <Process Name>

| Item | Value |
|---|---|
| SOP ID | `SP-nnn` |
| Process owner | |
| Roles performing | `Rnn`, `Rnn` |
| Systems used | `Pnn`, `Mnn` |
| Frequency / volume | |
| ISO 9001 clause reference | |

## 1. Purpose and Outcome
<What this process achieves and how you know it succeeded.>

## 2. Scope
**Applies to:** <sites, business lines, service types>
**Does not apply to:** <and which SOP covers those instead>

## 3. Definitions
| Term | Meaning |
|---|---|

## 4. Inputs and Preconditions
| Input | Source | Must be true before starting |
|---|---|---|

## 5. Procedure
| Step | Who | Action | System / screen | Evidence produced | Time |
|---:|---|---|---|---|---|
| 1 | | | | | |

## 6. Decision Points
| At step | Condition | Then | Authority |
|---|---|---|---|

## 7. Approvals and Authority Limits
| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|

> Must reconcile exactly with `SP-004` Approval Matrix.

## 8. Exceptions and Failure Handling
| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|

## 9. Manual Fallback
> Required if this process depends on a P0 integration (`IP-09`). Cross-reference `OP-014`.

## 10. Controls
| Control | Type | Frequency | Evidence |
|---|---|---|---|

## 11. Segregation of Duties
| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|

## 12. KPIs
| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|

## 13. Related Documents
| Document | Relationship |
|---|---|

## 14. Revision History
| Version | Date | Change | Approver |
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

*Template: TPL_SOP.md · 1000FiX ERP Programme · CONFIDENTIAL*
