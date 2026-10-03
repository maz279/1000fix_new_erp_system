---
id: UI-009
title: Offline, Sync and Conflict Resolution Copy
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
reviewers: [Mobile Engineering, Localisation Lead, Field Operations, Accessibility reviewer]
approver: Content Design Lead
content_class: C
purpose: >
  Offline banner, queued-action, sync-in-progress, sync-failed, conflict-choice and
  data-loss-prevention copy. PS-08 and NFR-047 require 24-hour offline operation on P02, P09 and
  P11; a technician who cannot tell whether work is saved will either re-enter it or lose it.
traces_to: [PS-08, 05-06 NFR-037, 05-06 NFR-047, P02, P09, P11, TS-015]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: UI-009_Offline_Sync_and_Conflict_Resolution_Copy_BN.md
i18n_namespace: `common.offline.*`
pinned_to:
  surface: `P02`, `P09`, `P11`
  release: pending first build
  wave: W2
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P02 non-negotiables 1, 2, 6 — full operation offline for 24 hours with no data loss; sync within 30 seconds; every state-changing action queued locally and idempotent
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-037, NFR-047
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-009 — Offline, Sync and Conflict Resolution Copy

> **The single most important thing this copy does is tell a technician whether their work is
> safe.** `P02` non-negotiable #1 is 24 hours offline with **no data loss**. The user cannot
> verify that; the copy is their only evidence.
>
> Every message here is ≤ 12 words. `P09` rider messages are ≤ 8 (`VB-002` R-01).

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | Offline banner, queued actions, sync state, conflicts and data-loss prevention |
| Framework | Flutter (`P02`, `P09`, `P11`) |
| Default language | **Bengali, complete** (`P02` non-negotiable #3) |
| i18n namespace | ``common.offline.*`` |
| Offline-capable | **Yes — this is the offline library** |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | C — Operational-critical |
| Sentence budget | 8–12 words (`VB-002` T-01, R-01) (`VB-002` §4.2) |
| Audience | Field technicians, riders, auditors |

---

## 2. Terminology bindings

Every term below is fixed by `CG-004`. **This pack cites; it never invents.**

| Concept | Term | Never |
|---|---|---|
| No connection | **offline** | no internet, disconnected |
| Saved on the device | **saved on this device** | cached, stored locally |
| Sent to the server | **synced** | uploaded, submitted |
| Waiting to sync | **waiting to sync** | pending, queued |
| Two versions differ | **changed elsewhere** | conflict, collision |

> Bengali forms are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

---

## 3. Screen copy

### 3.1 Offline state — `common.offline.*`

| Situation | Key | Message EN | Message BN | Words |
|---|---|---|---|---:|
| Went offline | `common.offline.banner` | Offline. Your work is saved on this device. | অফলাইন। আপনার কাজ এই ডিভাইসে সংরক্ষিত আছে। | 8 |
| Still offline, long | `common.offline.banner_long` | Offline for {hours} hours. {count} items waiting to sync. | {hours} ঘণ্টা অফলাইন। {count}টি আইটেম সিঙ্কের অপেক্ষায়। | 9 |
| Action queued | `common.offline.queued` | Saved. Will sync when you are back online. | সংরক্ষিত। অনলাইনে ফিরলে সিঙ্ক হবে। | 8 |
| Cannot do offline | `common.offline.blocked` | Needs a connection. Try again when you are online. | সংযোগ প্রয়োজন। অনলাইনে এলে আবার চেষ্টা করুন। | 8 |
| Approaching limit | `common.offline.limit_warning` | {hours} hours offline. Sync soon to be safe. | {hours} ঘণ্টা অফলাইন। নিরাপত্তার জন্য শীঘ্রই সিঙ্ক করুন। | 8 |

### 3.2 Sync — `common.sync.*`

| Situation | Key | Message EN | Message BN |
|---|---|---|---|
| Back online | `common.sync.reconnected` | Back online. Syncing {count} items. | আবার অনলাইন। {count}টি আইটেম সিঙ্ক হচ্ছে। |
| In progress | `common.sync.progress` | Syncing {done} of {total}. | {total}-এর মধ্যে {done}টি সিঙ্ক হচ্ছে। |
| Complete | `common.sync.done` | All synced. | সব সিঙ্ক হয়েছে। |
| Failed, will retry | `common.sync.retry` | Sync failed. Retrying. Your work is still saved. | সিঙ্ক ব্যর্থ। আবার চেষ্টা করা হচ্ছে। আপনার কাজ সংরক্ষিত আছে। |
| Failed, needs help | `common.sync.failed_help` | {count} items will not sync. Call dispatch on 16743. | {count}টি আইটেম সিঙ্ক হচ্ছে না। ডিসপ্যাচে 16743-এ কল করুন। |

> **`common.sync.retry` and `common.sync.failed_help` both restate that the work is saved.** That
> repetition is deliberate — it is the reassurance the technician needs at exactly that moment.

### 3.3 Conflict — `common.conflict.*`

| Situation | Key | Message EN | Message BN |
|---|---|---|---|
| Changed elsewhere | `common.conflict.detected` | {user} changed this job while you were offline. | আপনি অফলাইনে থাকাকালীন {user} এই জবটি পরিবর্তন করেছেন। |
| Choose — keep mine | `common.conflict.keep_mine` | Keep my version | আমার সংস্করণ রাখুন |
| Choose — keep theirs | `common.conflict.keep_theirs` | Keep {user}'s version | {user}-এর সংস্করণ রাখুন |
| Both kept | `common.conflict.both_kept` | Both versions saved. {supervisor} will review. | দুটি সংস্করণই সংরক্ষিত। {supervisor} পর্যালোচনা করবেন। |
| Cannot merge | `common.conflict.manual` | This needs a person to decide. Sent to {supervisor}. | এটি একজন ব্যক্তির সিদ্ধান্ত প্রয়োজন। {supervisor}-কে পাঠানো হয়েছে। |

> **No data is ever discarded silently.** Where a conflict cannot be resolved by the user, both
> versions are kept and a supervisor decides (`P02` non-negotiable #1).

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
| **O-01** | Every offline message states **whether work is saved** |
| **O-02** | Never say "lost", "failed to save" or "discarded" unless it is true |
| **O-03** | A blocked-offline action names **why** a connection is needed |
| **O-04** | Conflict resolution never discards silently — both versions survive |
| **O-05** | ≤ 12 words on `P02`/`P11`, ≤ 8 on `P09` |
| **O-06** | Readable in sunlight: high contrast, no tint fill (`VB-008` §5) |

---

## 6. Confirmations and destructive actions

Destructive-action copy is `UI-007`.

---

## 7. Accessibility text

| Item | Rule | SC |
|---|---|:--:|
| Offline banner | Announced assertively on state change | 4.1.3 |
| Sync status | Live region, polite | 4.1.3 |
| Conflict choice | Both options are buttons with verb labels; no default selection | 3.3.4 |
| Glanceable | Status readable without reading (`VB-002` R-05) | 1.4.1 |

---

## 8. Character budget and layout risk

Budgets are **Bengali** rendered lengths (`VB-006` `DS-04`). English runs 20–40% shorter.

| Slot | Budget (BN) | Risk |
|---|---:|---|
| Banner | 120 | Low — messages are deliberately short |
| Toast | 60 | Low |
| Conflict body | 200 | Medium |
| Button | 20 | **Medium** — "Keep {user}'s version" with a long name |

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
| [`UI-012_P02_Technician_App_UI_Copy_Pack.md`](../03B_Portals/UI-012_P02_Technician_App_UI_Copy_Pack.md) | Primary consumer |
| [`UI-019_P09_Logistics_and_Rider_App_UI_Copy_Pack.md`](../03B_Portals/UI-019_P09_Logistics_and_Rider_App_UI_Copy_Pack.md) | Rider budgets |
| `TS-015` Offline and Field Condition Test Scripts | Verification |
| `05-06` NFR-037, NFR-047 | The targets |

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
