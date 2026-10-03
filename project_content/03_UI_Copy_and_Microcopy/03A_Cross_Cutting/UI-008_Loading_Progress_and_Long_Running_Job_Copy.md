---
id: UI-008
title: Loading, Progress and Long-Running Job Copy
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
reviewers: [Localisation Lead, Design System, Accessibility reviewer, portal owner]
approver: Content Design Lead
content_class: D
purpose: >
  Skeleton, spinner, progress, queued, retrying and partial-result copy, including bulk operations.
  NFR-041 requires bulk operations on 1,000 records to give progress feedback, and that feedback is
  words, not a spinner.
traces_to: [05-06 NFR-041, VB-006 §7.2, CG-011, UI-009]
priority: P2
wave: W1
bilingual: yes
bn_counterpart: UI-008_Loading_Progress_and_Long_Running_Job_Copy_BN.md
i18n_namespace: `common.progress.*`
pinned_to:
  surface: All surfaces
  release: pending first build
  wave: W1
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-041 — bulk operation on 1,000 records within 60 s with progress feedback
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-008 — Loading, Progress and Long-Running Job Copy

> **Above two seconds, say what is happening.** A bare spinner tells the user nothing and gives
> them no basis to decide whether to wait (`VB-006` PR-01).

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | Skeleton, spinner, progress, queued, retrying and partial-result copy |
| Framework | All |
| Default language | Bengali default on customer and field surfaces |
| i18n namespace | ``common.progress.*`` |
| Offline-capable | `UI-009` covers offline |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | Per surface (`VB-002` §4.2) |
| Audience | All surfaces |

---

## 2. Terminology bindings

Every term below is fixed by `CG-004`. **This pack cites; it never invents.**

| Concept | Term | Never |
|---|---|---|
| Work in progress | **{verb}ing…** present continuous | "Please wait" |
| A queued task | **queued** | pending, waiting |
| A retry | **retrying** | reconnecting |

> Bengali forms are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

---

## 3. Screen copy

| Situation | Key | Message EN | Message BN | Detail |
|---|---|---|---|---|
| Loading a list | `common.progress.loading_list` | Loading {object}… | {object} লোড হচ্ছে… | Skeleton rows, not a spinner |
| Saving | `common.progress.saving` | Saving… | সংরক্ষণ করা হচ্ছে… | |
| Saved | `common.progress.saved` | Saved | সংরক্ষিত | Toast, 5 s (`VB-006` TO-04) |
| Bulk in progress | `common.progress.bulk` | {done} of {total} {object} updated | {total}-টির মধ্যে {done}টি {object} হালনাগাদ হয়েছে | `NFR-041` |
| Bulk — may leave | `common.progress.bulk_leave` | This continues if you leave the page. We will notify you when it finishes. | আপনি পাতা ছেড়ে গেলেও এটি চলতে থাকবে। শেষ হলে আমরা জানাব। | `VB-006` PR-03 |
| Partial failure | `common.progress.bulk_partial` | {done} of {total} succeeded. {failed} failed. Download the failure list to see why. | {total}-টির মধ্যে {done}টি সফল, {failed}টি ব্যর্থ। কারণ দেখতে ব্যর্থতার তালিকা ডাউনলোড করুন। | `VB-006` PR-05 |
| Queued | `common.progress.queued` | Queued. It will start when {n} jobs ahead of it finish. | সারিতে আছে। সামনের {n}টি কাজ শেষ হলে শুরু হবে। | |
| Retrying | `common.progress.retrying` | Connection lost. Retrying — attempt {n} of {max}. | সংযোগ বিচ্ছিন্ন। আবার চেষ্টা করা হচ্ছে — {max}-এর মধ্যে {n}। | |
| Report generating | `common.progress.report` | Building your report. Large reports take up to {seconds} seconds. | আপনার রিপোর্ট তৈরি হচ্ছে। বড় রিপোর্টে {seconds} সেকেন্ড পর্যন্ত লাগতে পারে। | `NFR-005` ≤ 20 s |

---

## 4. Field labels and help text

Field copy is `UI-003`; this pack adds only surface-specific fields where noted.

---

## 5. Validation and error messages

> `BR-STD-04` and `PS-09`: every message states **what is wrong and what to do**, in the user's
> language. Three-part structure per `CG-003` §3.1. Client-side validation is **format only** —
> business rules are server-side (`PS-11`).

| # | Rule |
|---|---|
| **PR-01** | Above 2 seconds, name the operation (`VB-006` PR-01) |
| **PR-02** | Bulk operations show count and progress (`NFR-041`) |
| **PR-03** | State whether the user may leave |
| **PR-04** | **Never estimate a time the system cannot predict** (`VB-006` PR-04) |
| **PR-05** | On partial failure, state what completed and what did not |

---

## 6. Confirmations and destructive actions

Destructive-action copy is `UI-007`.

---

## 7. Accessibility text

| Item | Rule | SC |
|---|---|:--:|
| Progress | `role="progressbar"` with accessible name and value | 4.1.2 |
| Completion | Announced politely | 4.1.3 |
| Skeleton | Marked decorative; not announced as content | 1.1.1 |
| Long operation | No time limit that cannot be extended | 2.2.1 |

---

## 8. Character budget and layout risk

Budgets are **Bengali** rendered lengths (`VB-006` `DS-04`). English runs 20–40% shorter.

| Slot | Budget (BN) | Risk |
|---|---:|---|
| Progress message | 60 | Low |
| Detail | 90 | Medium — partial-failure message has three placeholders |

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
| [`UI-009_Offline_Sync_and_Conflict_Resolution_Copy.md`](UI-009_Offline_Sync_and_Conflict_Resolution_Copy.md) | Offline states |
| `VB-006` §7.2 | Component contract |
| `05-06` NFR-041, NFR-005 | The targets this serves |

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
