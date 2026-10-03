---
id: <CODE>-<nnn>
title: <Human readable title>
project: 1000FiX ERP System v2.0
content_type: Generic
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

# <Title>

> **Generic template.** Use a content-type-specific template from `_templates/` where one
> exists. Use this one only for content types with no dedicated template.

## 1. Purpose
<Why this file exists and what stops working without it. Expand the `purpose:` front-matter line.>

## 2. Scope
**In scope:** <what this file covers>
**Out of scope:** <what it does not, and which file owns that — principle CP-01>

## 3. Audience
<Who reads or consumes this, and in what situation.>

## 4. Content
<The substance.>

## 5. Dependencies
| Depends on | Why |
|---|---|
| | |

## 6. Maintenance
| Item | Value |
|---|---|
| Review cadence | |
| Trigger for out-of-cycle review | |
| Owner | |

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

*Template: TPL_Content_File_Front_Matter.md · 1000FiX ERP Programme · CONFIDENTIAL*
