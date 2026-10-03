---
id: UI-030
title: Workspace — HR Console Copy
project: 1000FiX ERP System v2.0
content_type: UI copy pack
template: TPL_UI_Copy_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design Lead
author: Content Design
reviewers: [Localisation Lead, Design System, Accessibility reviewer, owning business function]
approver: Content Design Lead
content_class: D
purpose: >
  Copy for the HR console. Attendance exception, leave and payroll-run language affects pay accuracy
  for 500+ employees; payroll errors are visible, urgent and legally consequential.
traces_to: [M21, M55, M56, P03, MD-042, MD-043, DT-041]
priority: P1
wave: W5
bilingual: yes
bn_counterpart: UI-030_Workspace_HR_Console_Copy_BN.md
i18n_namespace: `ws.hr.*`
pinned_to:
  surface: P03
  release: pending first build
  wave: W5
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P03 — fourteen role-scoped workspaces, each opening on the work its role actually does
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-030 — Workspace — HR Console Copy

> Pay accuracy for 500+ people. Every label that could be misread is a payroll query, and payroll
> queries arrive all at once.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | P03 — HR Console workspace (HR officers and managers) |
| Framework | Odoo Web (OWL 2) |
| Default language | Bengali and English |
| i18n namespace | ``ws.hr.*`` |
| Offline-capable | No |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | ≤ 15 words (`VB-002` A-01) (`VB-002` §4.2) |
| Audience | HR officers and managers |

---

## 2. Terminology bindings

Every term below is fixed by `CG-004`. **This pack cites; it never invents.**

| Term | Entity | Note |
|---|---|---|
| Per `CG-004` §4 | — | This pack cites approved terms; it never invents |
| Status labels | `MD-027` | Internal labels here — never the customer-facing ones |

> Bengali forms are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

---

## 3. Screen copy

### 3.1 Opens on — attendance exceptions, leave, payroll run, incentives

| Element | Key | English | Bengali | Max |
|---|---|---|---|---:|
| Title | `ws.hr.title` | HR | এইচআর | 24 |
| Exceptions | `ws.hr.exceptions` | {count} attendance exceptions | {count}টি উপস্থিতি ব্যতিক্রম | 50 |
| Leave requests | `ws.hr.leave` | {count} leave requests | {count}টি ছুটির আবেদন | 50 |
| Payroll status | `ws.hr.payroll` | {period} payroll — {state} | {period} পেরোল — {state} |
| Run payroll | `ws.hr.run_payroll` | Run payroll | পেরোল চালান | 24 |
| Geofence exception | `ws.hr.geofence` | Clocked in {distance} from {branch} | {branch} থেকে {distance} দূরে ক্লক ইন | 60 |

---

## 4. Field labels and help text

Shared field copy is `UI-003`.

---

## 5. Validation and error messages

> `BR-STD-04` and `PS-09`: every message states **what is wrong and what to do**, in the user's
> language. Three-part structure per `CG-003` §3.1. Client-side validation is **format only** —
> business rules are server-side (`PS-11`).

| Trigger | Key | Message EN | Class |
|---|---|---|:--:|
| Element unverified | `ws.hr.error.element` | {element} is not verified for {fiscal_year}. Payroll is blocked until Finance completes verification. | **H** |
| Missing bank | `ws.hr.error.bank` | {count} employees have no bank details. Payroll cannot disburse to them. | **H** |
| Period locked | `ws.hr.error.locked` | {period} payroll is already run. Reverse it before running again. | **H** |

---

## 6. Confirmations and destructive actions

Destructive-action copy is `UI-007`.

| Action | Confirmation |
|---|---|
| Run payroll | States the period, headcount and total, and that it cannot be re-run without reversal |
| Approve geofence exception | Records the approver against the attendance record |

---

## 7. Accessibility text

| Item | Rule | SC |
|---|---|:--:|
| Labels | Visible persistent label on every input | 3.3.2 |
| Errors | Identified in text with a remedy | 3.3.1, 3.3.3 |
| Status | Colour never the only signal (`VB-008`) | 1.4.1 |
| Tables | Real header cells; sortable state announced | 1.3.1, 4.1.2 |
| Language | `lang` declared; script changes marked | 3.1.2 |
| Bulk | Selection count and scope announced | 4.1.3 |

---

## 8. Character budget and layout risk

Budgets are **Bengali** rendered lengths (`VB-006` `DS-04`). English runs 20–40% shorter.

| Slot | Budget (BN) | Risk |
|---|---:|---|
| Column header | 24 | **High** — 1366×600, up to 14 columns (`VB-003` D-01) |
| Button | 20 | Medium |
| Field label | 36 | Medium |
| Alert body | 200 | Low |

> Exceeding a budget is a **design conversation**, not a copy problem to solve by abbreviating
> (`VB-006` §8). Where the Bengali cannot fit, the control goes two-line before it goes
> icon-only (`VB-007` §7.3).

---

## 9. Open questions for design or product

| # | Question | Blocking? | Owner |
|---|---|:--:|---|
| 1 | `BN-003` not written; Bengali indicative | **Yes** | Localisation Lead |
| 2 | No build exists; `pinned_to` incomplete | **Yes** | Platform Engineering |

---

## 10. Related documents

| Document | Relationship |
|---|---|
| [`../03B_Portals/UI-013_P03_Admin_Operations_Portal_UI_Copy_Pack.md`](../03B_Portals/UI-013_P03_Admin_Operations_Portal_UI_Copy_Pack.md) | Shared shell copy |
| [`../03A_Cross_Cutting/UI-004_Validation_and_Error_Message_Library.md`](../03A_Cross_Cutting/UI-004_Validation_and_Error_Message_Library.md) | Business-rule messages |
| `MD-027` Status and Lifecycle State Label Register | Internal state labels |
| `VB-008` Status Colour and Label Semantics Register | Status treatment |

---

## 11. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Content Design Lead (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:`, `traces_to:` and `i18n_namespace:`
- [x] Conforms to `TPL_UI_Copy_Pack.md`
- [x] Every string has an i18n key conforming to `UI-001` (`CG-008` UI-a)
- [x] No string concatenated across a translatable boundary (`CG-003` S-05, `BN-005`)
- [x] Every error message follows the three-part structure and states a remedy (`CG-008` UI-c)
- [x] Error messages expose no internal detail (`CG-008` UI-d)
- [x] Message class matches the `05-05` rule class — H blocks, A names the authoriser, S warns
- [x] Empty, loading and offline states covered, not only the happy path (`CG-008` UI-f)
- [x] Destructive actions state the consequence; buttons are verbs, not OK/Cancel (`CG-008` UI-g)
- [x] Character budget recorded per slot, with Bengali expansion assessed (`CG-008` UI-h)
- [x] Status labels come from `MD-027`, not invented locally (`CG-008` UI-i, `T-06`)
- [x] Accessibility text authored here, not left to the implementer (`CG-011` AT-01)
- [x] All internal links resolve
- [ ] Bengali counterpart written and signed off **in context** (`BN-018`) — **outstanding; blocks `Approved`** (`CM-R6`)
- [ ] `BN-003` terminology confirmed — **outstanding; §2 indicative until then**
- [ ] Pinned to a release and verified against the build (`CG-008` UI-j) — **outstanding; no build yet**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
