---
id: <CODE>-<nnn>
title: <Human readable title>
project: 1000FiX ERP System v2.0
content_type: Legal / policy
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

# <Document Title>

| Item | Value |
|---|---|
| Document class | Terms / Policy / Notice / Agreement |
| Counterparty | |
| Governing law | Bangladesh |
| Effective date | |
| Acceptance capture method | Click-wrap / e-signature / offline (`LG-019`) |
| Version accepted by users | Recorded in `LG-001` |
| External counsel review | Required — name and date below |
| Bengali version | Required / not required (`CG-010`) |

## 1. Approval Record
| Role | Name | Date | Evidence |
|---|---|---|---|
| Drafted by | | | |
| Internal legal review | | | |
| External counsel | | | |
| Approved by | | | |

> No file of this class may reach `status: Approved` without every row completed (`CG-007`).

## 2. Scope and Parties

## 3. Definitions

## 4. Terms
<Numbered clauses. Each clause independently referenceable.>

## 5. Liability, Exclusions and Limits

## 6. Data Protection
> Must reconcile with `LG-008` privacy notice, `LG-009` retention schedule and `LG-012`
> residency statement. Contradiction between them is a compliance defect.

## 7. Termination and Consequences

## 8. Dispute Resolution

## 9. Change Control
| Version | Date | Change | Notice given to users | Re-acceptance required |
|---|---|---|---|:--:|

## 10. Cross-References
| Document | Relationship | Must not contradict |
|---|---|---|

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

*Template: TPL_Legal_Document.md · 1000FiX ERP Programme · CONFIDENTIAL*
