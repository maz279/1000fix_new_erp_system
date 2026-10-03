---
id: UI-014
title: P04 Corporate B2B Portal UI Copy Pack
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
  Screen copy for corporate client users. They are unpaid users of our system, answerable to their
  own management, and the audience most likely to forward our content to people who never log in.
  Invoice-dispute target is under 3%.
traces_to: [P04, UI-001, UI-003, UI-004, MD-027, VB-002]
priority: P1
wave: W4
bilingual: yes
bn_counterpart: UI-014_P04_Corporate_B2B_Portal_UI_Copy_Pack_BN.md
i18n_namespace: `p04.*`
pinned_to:
  surface: P04
  release: pending first build
  wave: W4
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §2 suite overview and the per-portal capability sets
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-014 — P04 Corporate B2B Portal UI Copy Pack

> **Every message must make sense to someone who did not see the screen it came from**
> (`VB-002` K-01). Corporate users forward our content internally.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | P04 — corporate and government client staff (500–2,000) |
| Framework | Next.js 15 |
| Default language | English-comfortable; Bengali available |
| i18n namespace | ``p04.*`` |
| Offline-capable | No |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | ≤ 25 words (`VB-002` K-01) (`VB-002` §4.2) |
| Audience | corporate and government client staff (500–2,000) |

---

## 2. Terminology bindings

Every term below is fixed by `CG-004`. **This pack cites; it never invents.**

| Term | Entity | Note |
|---|---|---|
| Per `CG-004` §4 | — | This pack cites approved terms; it never invents |

> Bengali forms are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

---

## 3. Screen copy

### 3.1 Estate — `p04.estate.*`

| Element | Key | English | Max |
|---|---|---|---:|
| Title | `p04.estate.title` | Your asset estate | 50 |
| Bulk upload | `p04.estate.bulk_upload` | Upload assets | 20 |
| Upload result | `p04.estate.upload_result` | {ok} of {total} assets added. {failed} failed — download the list to see why. | 200 |
| Assign site | `p04.estate.assign_site` | Assign to site | 20 |

### 3.2 Bulk request — `p04.request.*`

| Element | Key | English | Max |
|---|---|---|---:|
| Title | `p04.request.bulk_title` | Raise service requests | 50 |
| Coverage check | `p04.request.coverage` | {covered} of {total} assets are covered by {contract}. {uncovered} will be chargeable. | 200 |
| Approval needed | `p04.request.approval` | This needs approval from {approver} before we start. | 140 |

### 3.3 Billing — `p04.billing.*`

| Element | Key | English | Max |
|---|---|---|---:|
| Consolidated | `p04.billing.consolidated` | Consolidated invoice {ref} | 50 |
| Breakdown | `p04.billing.breakdown` | By site, department and asset | 60 |
| Dispute | `p04.billing.dispute` | Dispute a line | 20 |
| Dispute help | `p04.billing.dispute_help` | Tell us which line and why. We respond within {days} working days. | 140 |

### 3.4 SLA — `p04.sla.*`

| Element | Key | English |
|---|---|---|
| Status | `p04.sla.status` | {met} of {total} within SLA this period |
| Breach | `p04.sla.breach` | {count} breaches. Service credits of {amount} have been applied to your next invoice. |

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
| Asset not found | `p04.error.asset_unknown` | We could not find asset tag {tag}. Check the tag, or add the asset first. | **H** |
| Outside delegation | `p04.error.over_delegation` | This is above your approval limit of {limit}. It has been sent to {approver}. | **A** |
| Not covered | `p04.error.not_covered` | {asset} is not on {contract}. This will be chargeable at {rate}. Continue? | **S** |

---

## 6. Confirmations and destructive actions

Destructive-action copy is `UI-007`.

---

## 7. Accessibility text

| Item | Rule | SC |
|---|---|:--:|
| Labels | Every input has a visible persistent label | 3.3.2 |
| Errors | Identified in text, with a remedy | 3.3.1, 3.3.3 |
| Status | Colour is never the only signal (`VB-008`) | 1.4.1 |
| Language | `lang` declared; script changes marked | 3.1.1, 3.1.2 |
| Accessible names | From `UI-010`, translated | 1.1.1, 4.1.2 |
| Tables | Real header cells; data not layout | 1.3.1 |

---

## 8. Character budget and layout risk

Budgets are **Bengali** rendered lengths (`VB-006` `DS-04`). English runs 20–40% shorter.

| Slot | Budget (BN) | Risk |
|---|---:|---|
| Button | 20 | Medium — Bengali verbs run long |
| Column header | 24 | **High** at 1366×600 density |
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
| `EO-007` Corporate Client Onboarding Kit | Onboarding content |
| `EO-008` Corporate Admin Setup Guide | Configuration |
| `MD-015` Corporate Account Hierarchy Standard | The tree behind approvals |
| `DT-020` Consolidated Corporate Invoice | The invoice this displays |

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
