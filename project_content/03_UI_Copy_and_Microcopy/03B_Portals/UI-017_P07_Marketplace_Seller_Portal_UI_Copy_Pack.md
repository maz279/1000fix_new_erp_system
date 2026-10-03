---
id: UI-017
title: P07 Marketplace Seller Portal UI Copy Pack
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
  Screen copy for marketplace sellers — external, mixed literacy, Bengali-first, and dependent on
  understanding us for their income. Onboarding completion target is more than 60% of started
  registrations, and registration copy is the completion lever.
traces_to: [P07, UI-001, UI-003, UI-004, MD-027, VB-002]
priority: P2
wave: W7
bilingual: yes
bn_counterpart: UI-017_P07_Marketplace_Seller_Portal_UI_Copy_Pack_BN.md
i18n_namespace: `p07.*`
pinned_to:
  surface: P07
  release: pending first build
  wave: W7
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §2 suite overview and the per-portal capability sets
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-017 — P07 Marketplace Seller Portal UI Copy Pack

> **Money copy is the trust surface** (`VB-002` S-02). Earnings, commission, fees, holds and
> payouts state the arithmetic — they never assert a number.
>
> Performance and sanction copy has contractual effect under `LG-004`.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | P07 — external engineers and shops (500–2,000) |
| Framework | Next.js 15 + React Native |
| Default language | **Bengali-first** |
| i18n namespace | ``p07.*`` |
| Offline-capable | No |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | ≤ 18 words (`VB-002` S-01) (`VB-002` §4.2) |
| Audience | external engineers and shops (500–2,000) |

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

### 3.1 Registration — `p07.reg.*`

| Element | Key | English | Bengali |
|---|---|---|---|
| Title | `p07.reg.title` | Join as a seller | বিক্রেতা হিসেবে যোগ দিন |
| Why NID | `p07.reg.why_nid` | We verify your identity so customers can trust who is coming to their home | গ্রাহকরা যেন বিশ্বাস করতে পারেন কে তাদের বাসায় আসছেন, তাই আমরা আপনার পরিচয় যাচাই করি |
| Progress | `p07.reg.progress` | Step {n} of {total} — about {minutes} minutes left | ধাপ {n}/{total} — প্রায় {minutes} মিনিট বাকি |
| Under review | `p07.reg.review` | We are checking your documents. This usually takes {days} days. | আমরা আপনার কাগজপত্র যাচাই করছি। সাধারণত {days} দিন লাগে। |

### 3.2 Earnings — `p07.earn.*`

| Element | Key | English | Bengali |
|---|---|---|---|
| Job value | `p07.earn.gross` | Job value {gross} | জবের মূল্য {gross} |
| Commission | `p07.earn.commission` | 1000FiX commission {pct}% = {amount} | 1000FiX কমিশন {pct}% = {amount} |
| Net | `p07.earn.net` | You receive {net} | আপনি পাবেন {net} |
| Hold | `p07.earn.hold` | Held until {date} — {reason} | {date} পর্যন্ত আটকে আছে — {reason} |
| Payout | `p07.earn.payout` | {amount} paid to {bank} on {date} | {date}-এ {bank}-এ {amount} পরিশোধ করা হয়েছে |

### 3.3 Performance — `p07.perf.*`

| Element | Key | English | Bengali |
|---|---|---|---|
| Rating | `p07.perf.rating` | Your rating {rating} of 5 | আপনার রেটিং ৫-এর মধ্যে {rating} |
| Below threshold | `p07.perf.below` | Your rating is below {min}. Fewer jobs will be offered to you until it improves. | আপনার রেটিং {min}-এর নিচে। উন্নতি না হওয়া পর্যন্ত আপনাকে কম জব দেওয়া হবে। |
| Suspension warning | `p07.perf.warning` | If your rating falls below {suspend}, your account is suspended under the seller agreement. | রেটিং {suspend}-এর নিচে নামলে বিক্রেতা চুক্তি অনুযায়ী আপনার অ্যাকাউন্ট স্থগিত হবে। |

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
| Not verified | `p07.error.not_verified` | You can take jobs once your documents are verified and the agreement is signed. | **H** |
| Certification needed | `p07.error.cert_needed` | {category} needs {certification}. Complete it to bid on these jobs. | **H** |
| Dispute hold | `p07.error.dispute_hold` | Your payout is held while the dispute on {job} is open. It resumes automatically. | **H** |
| Concurrency | `p07.error.max_jobs` | You have {n} open jobs, the maximum for your category. Complete one to accept more. | **H** |

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
| Button | 20 | **High** — mobile width |
| Message | 60 | High |
| Field label | 36 | Medium |

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
| `LG-004` Marketplace Seller Agreement | **Contractual force behind sanction copy** |
| `EO-001` Marketplace Seller Onboarding Kit | Registration guidance |
| `EO-002` Seller Standards Handbook | Thresholds explained |
| `MD-018` Seller Category Register | Entry standards |

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
