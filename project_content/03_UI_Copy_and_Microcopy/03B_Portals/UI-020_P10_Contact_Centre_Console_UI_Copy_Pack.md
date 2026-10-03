---
id: UI-020
title: P10 Contact Centre Console UI Copy Pack
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
  Screen copy for the contact centre console — the only surface whose content is read **aloud**
  while a customer waits. Targets are fewer than three screen switches per contact and 100%
  disposition-coding completeness; both are copy and labelling outcomes.
traces_to: [P10, UI-001, UI-003, UI-004, MD-027, VB-002]
priority: P1
wave: W4
bilingual: yes
bn_counterpart: UI-020_P10_Contact_Centre_Console_UI_Copy_Pack_BN.md
i18n_namespace: `p10.*`
pinned_to:
  surface: P10
  release: pending first build
  wave: W4
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §2 suite overview and the per-portal capability sets
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-020 — P10 Contact Centre Console UI Copy Pack

> **Read every string aloud before approving it** (`VB-002` G-01). This is the only surface where
> the content is spoken to a customer in real time.
>
> Where the internal term differs from the customer-safe one, both appear (`VB-002` G-02).

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | P10 — contact centre agents, team leaders, quality analysts (30–80) |
| Framework | Next.js 15 |
| Default language | Bengali and English |
| i18n namespace | ``p10.*`` |
| Offline-capable | No |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | ≤ 12 words (`VB-002` G-01) (`VB-002` §4.2) |
| Audience | contact centre agents, team leaders, quality analysts (30–80) |

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

### 3.1 Queue and context — `p10.queue.*`

| Element | Key | English | Bengali |
|---|---|---|---|
| Waiting | `p10.queue.waiting` | {count} waiting, longest {minutes} min | {count}টি অপেক্ষমাণ, দীর্ঘতম {minutes} মিনিট |
| Screen pop | `p10.queue.pop` | {name} — {open_orders} open services | {name} — {open_orders}টি চলমান সার্ভিস |
| Channel | `p10.queue.channel` | {channel} | {channel} |

### 3.2 Customer-safe paraphrases — `p10.say.*`

| Internal term | Key | Say to the customer EN | Say BN |
|---|---|---|---|
| SLA breached | `p10.say.sla_breach` | Your repair is running late | আপনার মেরামত দেরি হচ্ছে |
| Awaiting parts | `p10.say.awaiting_parts` | We are waiting for a part to arrive | আমরা একটি পার্টসের জন্য অপেক্ষা করছি |
| Rework | `p10.say.rework` | We are checking it again at no charge | আমরা বিনামূল্যে এটি আবার পরীক্ষা করছি |
| Beyond economic repair | `p10.say.ber` | Repairing it would cost more than the device is worth | মেরামতের খরচ ডিভাইসের মূল্যের চেয়ে বেশি হবে |
| Estimate declined | `p10.say.declined` | You chose not to go ahead with the repair | আপনি মেরামত না করার সিদ্ধান্ত নিয়েছেন |

> **This table is the single most-used content on this surface.** It prevents an agent reading an
> internal state name to a customer (`CG-004` `T-06`).

### 3.3 Actions in conversation — `p10.action.*`

| Element | Key | English |
|---|---|---|
| Create order | `p10.action.create_order` | Create a service order |
| Reschedule | `p10.action.reschedule` | Reschedule the visit |
| Take payment | `p10.action.payment` | Take payment |
| Raise complaint | `p10.action.complaint` | Raise a complaint |
| Escalate | `p10.action.escalate` | Escalate to {role} |

### 3.4 Wrap-up — `p10.wrap.*`

| Element | Key | English |
|---|---|---|
| Disposition | `p10.wrap.disposition` | What was this about? |
| Outcome | `p10.wrap.outcome` | What happened? |
| Follow-up | `p10.wrap.followup` | Does anything need following up? |
| Incomplete | `p10.wrap.incomplete` | Disposition is required before you take the next contact. |

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
| Not verified | `p10.error.identity` | Verify the caller before discussing account details. | **H** |
| No consent | `p10.error.no_consent` | This customer has not consented to marketing contact. | **H** |
| Recording | `p10.error.recording_off` | Recording is not running. Do not take payment details. | **H** |

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
| `SP-034` Call and Conversation Script Library | Full scripts |
| `OP-003` Service Desk Macro and Canned Response Library | Canned responses |
| `MD-027` Status Register | Internal versus customer-facing labels |

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
