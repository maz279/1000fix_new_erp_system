---
id: UI-041
title: Search, Filter and Bulk Action Copy
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
  Search scope, filter, saved-view, selection-count, bulk-action and undo copy. Bulk actions on every
  list view are a P03 design requirement, and unclear selection scope in a bulk action causes mass
  data damage.
traces_to: [P03, VB-006 §6.1, §7.3, UI-006, UI-007, 05-06 NFR-041]
priority: P2
wave: W1
bilingual: yes
bn_counterpart: UI-041_Search_Filter_and_Bulk_Action_Copy_BN.md
i18n_namespace: `flow.search.*`
pinned_to:
  surface: All list-bearing surfaces
  release: pending first build
  wave: W1
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

# UI-041 — Search, Filter and Bulk Action Copy

> **Unclear selection scope in a bulk action causes mass data damage.** The count and the scope
> are always stated together (`VB-006` TB-07).

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | Cross-surface flow — All list-bearing surfaces |
| Framework | All surfaces carrying this flow |
| Default language | Bengali default on customer and field surfaces |
| i18n namespace | ``flow.search.*`` |
| Offline-capable | Where the carrying surface is offline-capable |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | Per surface (`VB-002` §4.2) (`VB-002` §4.2) |
| Audience | All list-bearing surfaces |

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

### 3.1 Search

| Element | Key | Wording EN | Bengali |
|---|---|---|---|
| Placeholder | `flow.search.placeholder` | Search {scope} | {scope} অনুসন্ধান করুন |
| Searching | `flow.search.searching` | Searching… | অনুসন্ধান হচ্ছে… |
| Count | `flow.search.count` | {count} results for "{query}" | "{query}"-এর জন্য {count}টি ফলাফল |
| Suggestion | `flow.search.suggest` | Did you mean {suggestion}? | আপনি কি {suggestion} বোঝাতে চেয়েছেন? |
| Bengali phonetic | `flow.search.phonetic_hint` | You can type in Bengali or English. | আপনি বাংলা বা ইংরেজিতে লিখতে পারেন। |

### 3.2 Filter

| Element | Key | Wording EN | Bengali |
|---|---|---|---|
| Applied | `flow.filter.applied` | {count} filters applied | {count}টি ফিল্টার প্রয়োগ করা হয়েছে |
| Clear one | `flow.filter.clear_one` | Remove {filter} | {filter} সরান |
| Clear all | `flow.filter.clear_all` | Clear all filters | সব ফিল্টার মুছুন |
| Saved view | `flow.filter.save_view` | Save this view | এই ভিউ সংরক্ষণ করুন |

### 3.3 Selection and bulk action

| Element | Key | Wording EN | Bengali |
|---|---|---|---|
| Selected | `flow.bulk.selected` | {n} selected of {total} | {total}-এর মধ্যে {n}টি নির্বাচিত |
| Select all on page | `flow.bulk.select_page` | Select all {n} on this page | এই পাতার সব {n}টি নির্বাচন করুন |
| Select all matching | `flow.bulk.select_all` | Select all {total} matching your filters | ফিল্টারের সাথে মিলে যাওয়া সব {total}টি নির্বাচন করুন |
| Action | `flow.bulk.action` | {action} {n} {object} | {n}টি {object} {action} |
| In progress | `flow.bulk.progress` | {done} of {total} done | {total}-এর মধ্যে {done}টি সম্পন্ন |
| Undo | `flow.bulk.undo` | Undo | পূর্বাবস্থায় ফেরান |

> **`flow.bulk.select_page` and `flow.bulk.select_all` are deliberately different strings.**
> Selecting 50 on a page and selecting 4,000 matching a filter are different acts and must not
> share wording.

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
| Over bulk limit | `flow.bulk.error.limit` | Bulk actions apply to at most {max}. Narrow your filter. | বাল্ক অ্যাকশন সর্বোচ্চ {max}-এ প্রযোজ্য। ফিল্টার সংকুচিত করুন। | **H** |
| Mixed states | `flow.bulk.error.mixed` | {n} of the selected records cannot have {action} applied. Continue with the other {ok}? | নির্বাচিত {n}টি রেকর্ডে {action} প্রয়োগ করা যাবে না। বাকি {ok}টির সঙ্গে চালিয়ে যাবেন? | **A** |
| Nothing selected | `flow.bulk.error.none` | Select at least one record. | অন্তত একটি রেকর্ড নির্বাচন করুন। | **H** |

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
| [`../03A_Cross_Cutting/UI-006_Empty_State_and_First_Run_Copy_Library.md`](../03A_Cross_Cutting/UI-006_Empty_State_and_First_Run_Copy_Library.md) | No-results states |
| `VB-006` §6.1, §7.3 | Component contracts |
| `05-06` NFR-041 | Bulk progress feedback |

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
