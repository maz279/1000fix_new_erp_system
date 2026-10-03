---
id: <CODE>-<nnn>
title: <Human readable title>
project: 1000FiX ERP System v2.0
content_type: Help article
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

# <How to …>

| Item | Value |
|---|---|
| Portal | `Pnn` |
| Audience | |
| Article type | Task / Concept / Troubleshooting / Reference |
| Reading level target | `CG-011` |
| Languages | |
| Related UI copy | `UI-nnn` |

## Before you start
| Prerequisite | Why |
|---|---|

## Steps
1. <Action in the imperative. One action per step. Name the exact UI label from `UI-nnn`.>
2.
3.

> Screenshots follow `MM-002` — sample data only, personal data redacted.

## What happens next
<System response, notifications sent, who is notified, expected timing.>

## If it does not work
| Symptom | Cause | What to do |
|---|---|---|

## Related
| Article | Why relevant |
|---|---|

## Feedback
> Deflection and helpfulness are measured per `CG-014`.

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

*Template: TPL_Help_Article.md · 1000FiX ERP Programme · CONFIDENTIAL*
