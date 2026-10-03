---
id: <CODE>-<nnn>
title: <Human readable title>
project: 1000FiX ERP System v2.0
content_type: Document / print
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

# <Document Name> — Print & Output Template

## 1. Document Summary
| Item | Value |
|---|---|
| Document type | |
| Owning module | `Mnn` |
| Statutory | yes / no — if yes, name the instrument |
| Recipient(s) | |
| Languages | EN / BN / bilingual side-by-side |
| Output formats | PDF / thermal print / A4 / A5 / email attachment |
| Numbering mask | `MD-040` reference |
| Retention period | `LG-009` reference |

## 2. Statutory Requirements
> Complete only for statutory documents. Every mandated element must be listed with its source
> and a verification date (`CG-012`).

| Mandated element | Source | Verified | Where it appears |
|---|---|---|---|

## 3. Layout
| Zone | Content | Bilingual treatment |
|---|---|---|
| Header | | |
| Party block | | |
| Body / line items | | |
| Totals / summary | | |
| Statutory block | | |
| Signature / stamp zone | | |
| Footer | | |
| Machine-readable (QR / barcode) | | `DT-044` |

## 4. Field Mapping
| Label EN | Label BN | Source field | Format | Required | Conditional |
|---|---|---|---|:--:|---|

## 5. Business Rules Affecting Output
| Rule ID | Effect on this document |
|---|---|

## 6. Variants
| Variant | When used | Difference |
|---|---|---|

## 7. Worked Example
> A completed specimen is held in `RF-009`. Link it here.

## 8. Approval
| Role | Name | Date | Signature evidence |
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

*Template: TPL_Document_Print_Template.md · 1000FiX ERP Programme · CONFIDENTIAL*
