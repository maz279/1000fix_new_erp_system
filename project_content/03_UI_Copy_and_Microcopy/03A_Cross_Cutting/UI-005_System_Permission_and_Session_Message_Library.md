---
id: UI-005
title: System, Permission and Session Message Library
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
reviewers: [Security, Platform Engineering, Localisation Lead, Accessibility reviewer]
approver: Content Design Lead
content_class: D
purpose: >
  Access denied, session expiry, MFA prompts, rate limit, maintenance, version-mismatch and
  service-unavailable copy. Security messages that leak internals are a vulnerability; messages
  that explain nothing generate hotline calls.
traces_to: [M29, PS-01, PS-12, CG-003 E-02, UI-002, OP-005]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: UI-005_System_Permission_and_Session_Message_Library_BN.md
i18n_namespace: `common.session.*`, `common.access.*`
pinned_to:
  surface: All surfaces
  release: pending first build
  wave: W1
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §3 PS-01 single sign-on, PS-12 session and MFA policy inherited from M29
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §1 role register — MFA required per role
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-005 — System, Permission and Session Message Library

> **A permission message must be useful without being informative.** It tells the user what to
> do next without confirming that the record they cannot see exists (`UI-006` ES-05).

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | Access, session, MFA, rate-limit, maintenance and version messages |
| Framework | All — Odoo OWL, Next.js, React Native, Flutter |
| Default language | Bengali default on customer and field surfaces (`PS-03`) |
| i18n namespace | ``common.session.*`, `common.access.*`` |
| Offline-capable | Applies to `P02`, `P09`, `P11` (`PS-08`) |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | Per surface — see `VB-002` §4.2 (`VB-002` §4.2) |
| Audience | All surfaces |

---

## 2. Terminology bindings

Every term below is fixed by `CG-004`. **This pack cites; it never invents.**

| Concept | Term | Never |
|---|---|---|
| Signing in | **sign in** | log in, login |
| The active period | **session** | connection |
| Second factor | **verification code** | OTP in customer content; OTP permitted internally |
| Access profile | **role** | permission group, profile |

> Bengali forms are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

---

## 3. Screen copy

### 3.1 Access — `common.access.*`

| Situation | Key | Message EN | Message BN | Class |
|---|---|---|---|:--:|
| No access to a feature | `common.access.denied_feature` | You do not have access to {feature}. Ask your manager if you need it. | আপনার {feature}-এ প্রবেশাধিকার নেই। প্রয়োজন হলে আপনার ম্যানেজারকে জানান। | **H** |
| No access to a record | `common.access.denied_record` | You do not have access to this record. | এই রেকর্ডে আপনার প্রবেশাধিকার নেই। | **H** |
| Read-only | `common.access.read_only` | You can view this but not change it. {role} can make changes. | আপনি এটি দেখতে পারবেন, পরিবর্তন করতে পারবেন না। {role} পরিবর্তন করতে পারবেন। | **S** |
| Out of data scope | `common.access.out_of_scope` | This record belongs to {branch}. You can see records for {your_scope}. | এই রেকর্ডটি {branch}-এর। আপনি {your_scope}-এর রেকর্ড দেখতে পারবেন। | **H** |

> `common.access.denied_record` deliberately does **not** say whether the record exists.

### 3.2 Session — `common.session.*`

| Situation | Key | Message EN | Message BN |
|---|---|---|---|
| Idle warning | `common.session.idle_warning` | You will be signed out in {minutes} minutes. Select Stay signed in to continue. | {minutes} মিনিটের মধ্যে আপনি সাইন আউট হয়ে যাবেন। চালিয়ে যেতে "সাইন ইন রাখুন" নির্বাচন করুন। |
| Expired | `common.session.expired` | Your session ended. Sign in again to continue. Your unsaved work on this page was not kept. | আপনার সেশন শেষ হয়েছে। চালিয়ে যেতে আবার সাইন ইন করুন। এই পাতার অসংরক্ষিত কাজ রাখা হয়নি। |
| Signed out elsewhere | `common.session.elsewhere` | You signed in on another device, so this session ended. | আপনি অন্য ডিভাইসে সাইন ইন করেছেন, তাই এই সেশনটি শেষ হয়েছে। |
| Sign out confirm | `common.session.signout_confirm` | Sign out of 1000FiX? | 1000FiX থেকে সাইন আউট করবেন? |

### 3.3 Verification — `common.mfa.*`

| Situation | Key | Message EN | Message BN |
|---|---|---|---|
| Prompt | `common.mfa.prompt` | Enter the 6-digit code we sent to {masked_mobile}. | {masked_mobile}-এ পাঠানো ৬ সংখ্যার কোডটি লিখুন। |
| Wrong code | `common.mfa.wrong_code` | That code is not correct. You have {attempts} attempts left. | কোডটি সঠিক নয়। আপনার আর {attempts} বার চেষ্টা বাকি। |
| Expired code | `common.mfa.expired` | That code has expired. Request a new one. | কোডটির মেয়াদ শেষ হয়েছে। নতুন কোড নিন। |
| Resend cooldown | `common.mfa.resend_wait` | You can request a new code in {seconds} seconds. | {seconds} সেকেন্ড পরে নতুন কোড নিতে পারবেন। |
| Locked | `common.mfa.locked` | Too many incorrect codes. Your account is locked for {minutes} minutes. Call 16743 if you need help sooner. | অনেকবার ভুল কোড দেওয়া হয়েছে। আপনার অ্যাকাউন্ট {minutes} মিনিটের জন্য লক করা হয়েছে। দ্রুত সাহায্যের জন্য 16743-এ কল করুন। |

### 3.4 Availability — `common.system.*`

| Situation | Key | Message EN | Note |
|---|---|---|---|
| Planned maintenance | `common.system.maintenance` | 1000FiX is unavailable until {time} for planned maintenance. Call 16743 for urgent service. | Window constrained by `NFR-049` |
| Degraded | `common.system.degraded` | {feature} is not working right now. {fallback} Everything else is working normally. | `IP-09` fallback named |
| Rate limited | `common.system.rate_limited` | Too many requests. Wait {seconds} seconds and try again. | `PS-02` |
| Version mismatch | `common.system.version_old` | Update the app to continue. This version is no longer supported. | `OP-011` forced upgrade |

---

## 4. Field labels and help text

Field copy is `UI-003`. This library carries no field labels.

---

## 5. Validation and error messages

> `BR-STD-04` and `PS-09`: every message states **what is wrong and what to do**, in the user's
> language. Three-part structure per `CG-003` §3.1. Client-side validation is **format only** —
> business rules are server-side (`PS-11`).

| # | Rule |
|---|---|
| **S-01** | Never confirm whether a record the user cannot access exists |
| **S-02** | Never name the missing permission technically. Name the **feature** and the **role** |
| **S-03** | Never expose a stack trace, internal ID or service name (`CG-003` E-02) |
| **S-04** | Session expiry states **whether unsaved work was kept**. On `P02` and `P09` it always was (`UI-009`) |
| **S-05** | Every degraded-service message names the manual fallback (`IP-09`, `OP-014`) |
| **S-06** | Lockout messages give a route to help — the hotline, always |

---

## 6. Confirmations and destructive actions

Destructive-action copy is `UI-007`.

---

## 7. Accessibility text

| Item | Rule | SC |
|---|---|:--:|
| Session warning | Announced as an assertive live region with enough time to act | 2.2.1 |
| Idle timeout | Extendable without losing data | **2.2.1** |
| Verification code field | Labelled, numeric input mode, autocomplete `one-time-code` | 1.3.5 |
| Masked mobile | Announced as a masked value, not read digit by digit as if complete | 1.3.1 |

---

## 8. Character budget and layout risk

Budgets are **Bengali** rendered lengths (`VB-006` `DS-04`). English runs 20–40% shorter.

| Slot | Budget (BN) | Risk |
|---|---:|---|
| Banner | 120 | Medium — maintenance message with time and fallback |
| Modal body | 300 | Low |
| Inline | 90 | Medium — MFA lockout message |

> Exceeding a budget is a **design conversation**, not a copy problem to solve by abbreviating
> (`VB-006` §8). Where the Bengali cannot fit, the control goes two-line before it goes
> icon-only (`VB-007` §7.3).

---

## 9. Open questions for design or product

| # | Question | Blocking? | Owner |
|---|---|:--:|---|
| 1 | `BN-003` is not written; Bengali here is indicative | **Yes** | Localisation Lead |
| 2 | No build exists, so `pinned_to` cannot be completed (`CG-006` §3) | **Yes** | Platform Engineering |

---

## 10. Related documents

| Document | Relationship |
|---|---|
| [`UI-006_Empty_State_and_First_Run_Copy_Library.md`](UI-006_Empty_State_and_First_Run_Copy_Library.md) | `ES-05` no-permission empty state |
| `M29` Identity, Access and Information Security | The implementing module |
| `OP-005` Status Page and Maintenance Notice Copy | Maintenance messaging |
| `MD-009` Role and Job Title Master | The roles named in messages |

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
