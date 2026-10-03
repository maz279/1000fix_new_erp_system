---
id: <CODE>-<nnn>
title: <Human readable title>
project: 1000FiX ERP System v2.0
content_type: Notification
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

# <Notification Set Name>

## 1. Set Summary
| Item | Value |
|---|---|
| Channel(s) | SMS / WhatsApp / Email / Push / In-app / Voice |
| Audience | |
| Owning module | `Mnn` |
| Consent class | Transactional / Marketing (`NT-002`) |
| Quiet-hours exempt | yes / no (`NT-003`) |

## 2. Templates
Repeat per message.

### <Message name> — `<template_id>`
| Attribute | Value |
|---|---|
| Trigger event | |
| Channel | |
| Priority | |
| Variables | `{{var}}` … |
| Fallback channel | |
| Suppression rules | |

**English**
```
```

**Bengali**
```
```

| Metric | EN | BN |
|---|---:|---:|
| Characters | | |
| SMS segments (GSM-7 / UCS-2) | | |
| Estimated cost per send | | |

> Bengali SMS is UCS-2 and segments at **70 characters**, not 160. Record the segment count for
> every Bengali SMS template.

## 3. Channel-Specific Requirements
| Channel | Requirement |
|---|---|
| WhatsApp | Category, pre-approval status, submission date, approval date (`NT-008`) |
| Push | Title/body limits per platform, deep link target |
| Email | Subject, preheader, plain-text parity (`VB-005`) |
| Voice | Recording direction, pronunciation notes (`BN-017`) |

## 4. Failure and Fallback
| Failure mode | User-visible behaviour | Fallback (`NT-025`) |
|---|---|---|

## 5. Change Log
| Version | Date | Change | Approver | WhatsApp re-approval needed |
|---|---|---|---|:--:|

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

*Template: TPL_Notification_Template.md · 1000FiX ERP Programme · CONFIDENTIAL*
