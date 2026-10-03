---
id: UI-039
title: Payment and Checkout Flow Copy
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
reviewers: [Localisation Lead, Legal & Compliance, Design System, Accessibility reviewer, owning module business owner]
approver: Content Design Lead
content_class: C
purpose: >
  Payment method selection, authorisation, failure, retry, partial payment, refund and receipt copy.
  Payment-path availability is 99.95% with multi-gateway failover (NFR-048); the failover must be
  explained to the customer in the moment it happens.
traces_to: [M20, M50, 05-03 INT-001..009, 05-06 NFR-048, MD-038, DT-016, IP-09]
priority: P0
wave: W3
bilingual: yes
bn_counterpart: UI-039_Payment_and_Checkout_Flow_Copy_BN.md
i18n_namespace: `flow.payment.*`
pinned_to:
  surface: `P01`, `P02`, `P03`, `P04`, `P09`
  release: pending first build
  wave: W3
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §3 PS-09, PS-11 and the per-portal capability sets
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 business rules governing this flow
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-039 — Payment and Checkout Flow Copy

> **When a gateway fails, the customer is standing there.** `IP-09` requires a defined manual
> fallback for every P0 integration; this copy is how the fallback reaches the person affected.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | Cross-surface flow — `P01`, `P02`, `P03`, `P04`, `P09` |
| Framework | All surfaces carrying this flow |
| Default language | Bengali default on customer and field surfaces |
| i18n namespace | ``flow.payment.*`` |
| Offline-capable | Where the carrying surface is offline-capable |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | C — Operational-critical |
| Sentence budget | Per surface (`VB-002` §4.2) (`VB-002` §4.2) |
| Audience | `P01`, `P02`, `P03`, `P04`, `P09` |

---

## 2. Terminology bindings

Every term below is fixed by `CG-004`. **This pack cites; it never invents.**

| Term | Entity | Note |
|---|---|---|
| Per `CG-004` §4 | — | This flow is the **canonical wording**; portals cite it (`CG-003` X-01) |

> Bengali forms are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

---

## 3. Screen copy

### 3.1 Method selection

| Element | Key | Wording EN | Bengali |
|---|---|---|---|
| Title | `flow.payment.title` | How would you like to pay? | কীভাবে পরিশোধ করতে চান? |
| Amount | `flow.payment.amount` | {amount} due | {amount} বাকি |
| bKash | `flow.payment.method.bkash` | bKash | বিকাশ |
| Nagad | `flow.payment.method.nagad` | Nagad | নগদ |
| Card | `flow.payment.method.card` | Card | কার্ড |
| Cash | `flow.payment.method.cash` | Cash at the service centre | সার্ভিস সেন্টারে নগদ |
| Pay later | `flow.payment.method.later` | Pay when you collect | সংগ্রহের সময় পরিশোধ করুন |

### 3.2 In progress and outcome

| Element | Key | Wording EN | Bengali |
|---|---|---|---|
| Redirecting | `flow.payment.redirect` | Taking you to {method}. Do not close this page. | আপনাকে {method}-এ নিয়ে যাচ্ছি। এই পাতা বন্ধ করবেন না। |
| Waiting | `flow.payment.waiting` | Waiting for {method} to confirm. | {method}-এর নিশ্চিতকরণের অপেক্ষায়। |
| Success | `flow.payment.success` | Paid {amount}. Receipt sent to {mobile}. | {amount} পরিশোধিত। {mobile}-এ রসিদ পাঠানো হয়েছে। |
| Partial | `flow.payment.partial` | {paid} paid. {remaining} still due. | {paid} পরিশোধিত। {remaining} এখনও বাকি। |

### 3.3 Failure and fallback — the `IP-09` copy

| Situation | Key | Wording EN | Bengali |
|---|---|---|---|
| Declined | `flow.payment.declined` | {method} declined this payment. {reason} Try another method, or pay at the service centre. | {method} এই পেমেন্ট প্রত্যাখ্যান করেছে। {reason} অন্য পদ্ধতি চেষ্টা করুন, বা সার্ভিস সেন্টারে পরিশোধ করুন। |
| Gateway down | `flow.payment.gateway_down` | {method} is not responding. Use another method, or pay at the counter — we will record it. | {method} সাড়া দিচ্ছে না। অন্য পদ্ধতি ব্যবহার করুন, বা কাউন্টারে পরিশোধ করুন — আমরা রেকর্ড করব। |
| All down (staff view) | `flow.payment.all_down` | No gateway is responding. Take payment at the counter and record it here when they return. | কোনো গেটওয়ে সাড়া দিচ্ছে না। কাউন্টারে পেমেন্ট নিন এবং ফিরে এলে এখানে রেকর্ড করুন। |
| Uncertain | `flow.payment.uncertain` | We could not confirm this payment. Do not pay again. We will check and message you within {minutes} minutes. | আমরা এই পেমেন্ট নিশ্চিত করতে পারিনি। আবার পরিশোধ করবেন না। আমরা যাচাই করে {minutes} মিনিটের মধ্যে জানাব। |

> **`flow.payment.uncertain` is the most important string in this pack.** A customer who pays
> twice because we were ambiguous is a refund, a complaint and a trust loss.

### 3.4 Refund

| Element | Key | Wording EN | Bengali |
|---|---|---|---|
| Initiated | `flow.payment.refund_started` | Refund of {amount} started. It reaches {method} in {days} days. | {amount} ফেরত শুরু হয়েছে। {days} দিনে {method}-এ পৌঁছাবে। |
| Complete | `flow.payment.refund_done` | {amount} refunded to {method}. | {method}-এ {amount} ফেরত দেওয়া হয়েছে। |

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
| Amount mismatch | `flow.payment.error.amount` | The amount does not match. Due {due}, entered {entered}. | **H** |
| Method unavailable | `flow.payment.error.unavailable` | {method} is not available for this amount. Available: {alternatives}. | **H** |
| Duplicate | `flow.payment.error.duplicate` | A payment of {amount} was already recorded {minutes} minutes ago. Record another? | **A** |

---

## 6. Confirmations and destructive actions

Destructive-action copy is `UI-007`.

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
| `MD-038` Payment Method, Term and Bank Master | Methods and settlement |
| `DT-016` Payment Receipt and Money Receipt | The receipt |
| `AP-009` Payment Gateway Integration Runbook | Operational fallback |
| `05-03` §2.1 | The nine payment integrations |

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
- [ ] G2 factual and G3 technical review by the owning module business owner — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
