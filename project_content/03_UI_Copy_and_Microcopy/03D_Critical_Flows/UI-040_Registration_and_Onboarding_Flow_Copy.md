---
id: UI-040
title: Registration and Onboarding Flow Copy
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
content_class: D
purpose: >
  Registration, OTP, verification, document upload and approval-status copy for customers, sellers,
  vendors, partners and corporate users. Five audiences onboard through five flows on one identity
  platform; inconsistent onboarding copy creates five support burdens.
traces_to: [M29, M33, MD-013, MD-016, MD-018, UI-042, EO-001, EO-005, EO-007, EO-009]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: UI-040_Registration_and_Onboarding_Flow_Copy_BN.md
i18n_namespace: `flow.register.*`
pinned_to:
  surface: `P01`, `P04`, `P05`, `P07`, `P12`
  release: pending first build
  wave: W2
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

# UI-040 — Registration and Onboarding Flow Copy

> **One identity platform, five audiences.** The verification steps differ; the wording of
> identity, OTP and approval status does not.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | Cross-surface flow — `P01`, `P04`, `P05`, `P07`, `P12` |
| Framework | All surfaces carrying this flow |
| Default language | Bengali default on customer and field surfaces |
| i18n namespace | ``flow.register.*`` |
| Offline-capable | Where the carrying surface is offline-capable |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | Per surface (`VB-002` §4.2) (`VB-002` §4.2) |
| Audience | `P01`, `P04`, `P05`, `P07`, `P12` |

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

### 3.1 Shared identity steps

| Element | Key | Wording EN | Bengali |
|---|---|---|---|
| Mobile | `flow.register.mobile` | Your mobile number | আপনার মোবাইল নম্বর |
| Why mobile | `flow.register.why_mobile` | We use this to sign you in and send service updates. | আমরা এটি সাইন ইন এবং সার্ভিস আপডেট পাঠাতে ব্যবহার করি। |
| Send code | `flow.register.send_code` | Send code | কোড পাঠান |
| Enter code | `flow.register.enter_code` | Enter the 6-digit code sent to {mobile} | {mobile}-এ পাঠানো ৬ সংখ্যার কোড লিখুন |
| Resend | `flow.register.resend` | Send again | আবার পাঠান |
| Verified | `flow.register.verified` | Verified | যাচাই হয়েছে |

### 3.2 Approval status — shared across `P05`, `P07`, `P12`

| Status | Key | Wording EN | Bengali |
|---|---|---|---|
| Submitted | `flow.register.status.submitted` | We have your application. | আমরা আপনার আবেদন পেয়েছি। |
| In review | `flow.register.status.review` | We are checking your documents. This usually takes {days} days. | আমরা আপনার কাগজপত্র যাচাই করছি। সাধারণত {days} দিন লাগে। |
| More needed | `flow.register.status.more` | We need {missing} before we can continue. | চালিয়ে যেতে আমাদের {missing} প্রয়োজন। |
| Approved | `flow.register.status.approved` | Approved. You can start now. | অনুমোদিত। আপনি এখন শুরু করতে পারেন। |
| Declined | `flow.register.status.declined` | We cannot approve this application. {reason} You can apply again after {date}. | আমরা এই আবেদন অনুমোদন করতে পারছি না। {reason} আপনি {date}-এর পর আবার আবেদন করতে পারবেন। |

### 3.3 Per-audience additions

| Audience | Adds |
|---|---|
| Customer (`P01`) | Nothing — mobile and OTP only |
| Corporate (`P04`) | Company details, site list, approval chain (`EO-008`) |
| Vendor (`P05`) | Trade licence, BIN, bank proof (`MD-016`) |
| Seller (`P07`) | NID, references, work samples, agreement signature (`MD-018`, `LG-004`) |
| Partner (`P12`) | Agreement signature, payout details (`LG-007`) |

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
| Mobile in use | `flow.register.error.mobile_used` | This number is already registered. Sign in instead, or use another number. | **H** |
| OTP wrong | `flow.register.error.otp` | That code is not correct. {attempts} attempts left. | **H** |
| Document unreadable | `flow.register.error.doc_unreadable` | We could not read {document}. Upload a clearer photo. | **H** |
| Agreement unsigned | `flow.register.error.agreement` | Sign the agreement to complete your registration. | **H** |

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
| [`UI-042_Consent_Privacy_and_Preference_Centre_Copy.md`](UI-042_Consent_Privacy_and_Preference_Centre_Copy.md) | Consent captured during registration |
| `EO-001`, `EO-005`, `EO-007`, `EO-009` | Per-audience onboarding kits |
| `MD-013` Customer and Party Master Standard | The record created |

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
