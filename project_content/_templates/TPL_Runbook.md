---
id: <CODE>-<nnn>
title: <Human readable title>
project: 1000FiX ERP System v2.0
content_type: Runbook
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

# Runbook — <System / Component>

| Item | Value |
|---|---|
| System | |
| Owner team | |
| Criticality | P0 / P1 / P2 |
| Availability target | `05-06` NFR reference |
| On-call rota | `OP-013` |
| Escalation path | |

## 1. What This System Does
<Two or three sentences. What breaks downstream if it stops.>

## 2. Architecture Summary
| Component | Purpose | Depends on |
|---|---|---|

## 3. Health Checks
| Check | Command / dashboard | Healthy looks like |
|---|---|---|

## 4. Routine Operations
| Operation | Steps | Risk | Approval needed |
|---|---|---|:--:|

## 5. Common Failure Modes
| Symptom | Likely cause | Diagnosis | Fix | Escalate if |
|---|---|---|---|---|

## 6. Incident Response
| Severity | Response time | First actions | Who to notify | Comms template (`OP-004`) |
|---|---|---|---|---|

## 7. Manual Fallback
> Required for every P0 integration (`IP-09`). Describe how the business keeps trading.

| Scenario | Fallback procedure | Duration tolerable | Reconciliation on recovery |
|---|---|---|---|

## 8. Backup and Recovery
| Item | RPO | RTO | Procedure | Last tested |
|---|---|---|---|---|

## 9. Break-Glass Access
| Scenario | Who may authorise | Procedure | Audit record |
|---|---|---|---|

## 10. Change and Rollback
| Change type | Approval | Rollback procedure | Verification |
|---|---|---|---|

## 11. Post-Incident
> Every Sev1 and Sev2 requires a review recorded in `OP-016`.

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

*Template: TPL_Runbook.md · 1000FiX ERP Programme · CONFIDENTIAL*
