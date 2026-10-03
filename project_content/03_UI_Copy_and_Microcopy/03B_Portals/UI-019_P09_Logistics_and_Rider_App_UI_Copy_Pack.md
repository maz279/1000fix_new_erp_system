---
id: UI-019
title: P09 Logistics and Rider App UI Copy Pack
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
  Screen copy for the rider application — the shortest content in the system. One-handed, moving,
  often in poor light, offline. POD completeness target is 100% and custody breaks target zero;
  both depend on unambiguous scan and handover copy.
traces_to: [P09, UI-001, UI-003, UI-004, MD-027, VB-002]
priority: P1
wave: W3
bilingual: yes
bn_counterpart: UI-019_P09_Logistics_and_Rider_App_UI_Copy_Pack_BN.md
i18n_namespace: `p09.*`
pinned_to:
  surface: P09
  release: pending first build
  wave: W3
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §2 suite overview and the per-portal capability sets
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-019 — P09 Logistics and Rider App UI Copy Pack

> **Eight words maximum. Prefer four** (`VB-002` R-01).
>
> Custody and cash steps are the exception — they get the words they need (`VB-002` R-03). A
> rider guessing between two options at a customer's door is a custody break.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | P09 — riders, logistics coordinators, courier staff (50–200) |
| Framework | Flutter |
| Default language | **Bengali** |
| i18n namespace | ``p09.*`` |
| Offline-capable | **Yes** (`PS-08`) |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | **≤ 8 words** (`VB-002` R-01) (`VB-002` §4.2) |
| Audience | riders, logistics coordinators, courier staff (50–200) |

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

### 3.1 Manifest — `p09.manifest.*`

| Element | Key | English | Bengali | Words |
|---|---|---|---|---:|
| Title | `p09.manifest.title` | Today — {count} stops | আজ — {count}টি স্টপ | 4 |
| Next stop | `p09.manifest.next` | Next: {area} | পরবর্তী: {area} | 2 |
| Start route | `p09.manifest.start` | Start route | রুট শুরু করুন | 2 |

### 3.2 Collection — `p09.collect.*`

| Element | Key | English | Bengali | Words |
|---|---|---|---|---:|
| Scan | `p09.collect.scan` | Scan the item | আইটেম স্ক্যান করুন | 3 |
| Check items | `p09.collect.check` | Check against the list | তালিকার সাথে মিলিয়ে দেখুন | 4 |
| Photo | `p09.collect.photo` | Photo the item | আইটেমের ছবি তুলুন | 3 |
| Seal | `p09.collect.seal` | Enter the seal number | সিল নম্বর লিখুন | 4 |
| OTP | `p09.collect.otp` | Ask for the OTP | ওটিপি চান | 4 |
| Done | `p09.collect.done` | Collected | সংগ্রহ করা হয়েছে | 1 |

### 3.3 Delivery — `p09.deliver.*`

| Element | Key | English | Bengali | Words |
|---|---|---|---|---:|
| Verify | `p09.deliver.verify` | Check who you are handing to | কার কাছে দিচ্ছেন যাচাই করুন | 6 |
| Signature | `p09.deliver.sign` | Ask them to sign | স্বাক্ষর করতে বলুন | 4 |
| Cash | `p09.deliver.cash` | Collect {amount} | {amount} সংগ্রহ করুন | 2 |
| Done | `p09.deliver.done` | Delivered | পৌঁছে দেওয়া হয়েছে | 1 |

### 3.4 Exceptions — `p09.exception.*`

A **fixed list**, never free text (`VB-002` R-04).

| Key | English | Bengali |
|---|---|---|
| `p09.exception.absent` | Customer not present | গ্রাহক উপস্থিত নেই |
| `p09.exception.address` | Address wrong | ঠিকানা ভুল |
| `p09.exception.refused` | Customer refused | গ্রাহক প্রত্যাখ্যান করেছেন |
| `p09.exception.damaged` | Item damaged | আইটেম ক্ষতিগ্রস্ত |
| `p09.exception.unsafe` | Not safe to proceed | এগোনো নিরাপদ নয় |

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
| Wrong item | `p09.error.wrong_item` | Not on this manifest. Check again. | **H** |
| OTP wrong | `p09.error.otp` | Wrong code. {n} tries left. | **H** |
| Cash mismatch | `p09.error.cash` | Amount does not match. Expected {amount}. | **H** |
| Photo needed | `p09.error.photo` | Take a photo first. | **H** |

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
| Any message | **8 words** | **Highest in the system** |
| Button | 20 chars | High |
| Exception label | 24 chars | Medium |

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
| [`../03A_Cross_Cutting/UI-009_Offline_Sync_and_Conflict_Resolution_Copy.md`](../03A_Cross_Cutting/UI-009_Offline_Sync_and_Conflict_Resolution_Copy.md) | Offline states |
| `TR-020` Course Pack Rider and Logistics | Bengali training |
| `DT-028` Proof of Delivery and Custody Record | The evidence captured |

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
