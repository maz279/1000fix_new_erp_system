---
id: <CODE>-<nnn>
title: <Human readable title>
project: 1000FiX ERP System v2.0
content_type: UI copy
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

# <Portal / Workspace / Flow> — UI Copy Pack

## 1. Surface Summary
| Item | Value |
|---|---|
| Portal / workspace | `Pnn` / <workspace> |
| Framework | Odoo OWL / Next.js / React Native / Flutter |
| Default language | Bengali / English (`PS-03`) |
| Offline-capable | yes / no (`PS-08`) |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |

## 2. Terminology Bindings
| UI term | Canonical term (`CG-004`) | Bengali (`BN-003`) | Entity |
|---|---|---|---|

## 3. Screen Copy
Repeat this block per screen.

### <Screen name> — `<i18n namespace>`
| Element | Key | English | Bengali | Max chars | Notes for translator |
|---|---|---|---|---:|---|
| Page title | | | | | |
| Description | | | | | |
| Primary action | | | | | |
| Secondary action | | | | | |
| Empty state | | | | | See `UI-006` |
| Loading state | | | | | See `UI-008` |

## 4. Field Labels and Help Text
| Field | Key | Label EN | Label BN | Placeholder | Help text | Required |
|---|---|---|---|---|---|:--:|

## 5. Validation and Error Messages
| Trigger | Key | Message EN | Message BN | Remedy stated? | Rule ID |
|---|---|---|---|:--:|---|

> `BR-STD-04`: every message must state what is wrong **and** what to do, in the user's language.

## 6. Confirmations and Destructive Actions
| Action | Reversible | Confirmation copy | Override reason captured (`BR-STD-06`) |
|---|:--:|---|:--:|

## 7. Accessibility Text
| Element | Alt / ARIA label EN | BN | Live-region behaviour |
|---|---|---|---|

## 8. Character Budget and Layout Risk
| Key | EN chars | BN chars | Expansion % | Layout risk |
|---|---:|---:|---:|---|

> Bengali commonly runs 20–40% longer. Flag anything above the surface's stated maximum.

## 9. Open Questions for Design or Product
| # | Question | Blocking? | Owner |
|---|---|:--:|---|

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

*Template: TPL_UI_Copy_Pack.md · 1000FiX ERP Programme · CONFIDENTIAL*
