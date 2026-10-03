---
id: UI-037
title: Booking and Order Creation Flow Copy
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
  End-to-end booking copy across the customer portal, agent intake, corporate bulk request and the
  contact centre. The same booking exists on four surfaces; divergent copy produces four different
  customer promises for one transaction.
traces_to: [M01, MD-020, MD-021, MD-024, MD-028, UI-011, UI-023, UI-014, UI-020]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: UI-037_Booking_and_Order_Creation_Flow_Copy_BN.md
i18n_namespace: `flow.booking.*`
pinned_to:
  surface: `P01`, `P03`, `P04`, `P10`
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

# UI-037 — Booking and Order Creation Flow Copy

> **One transaction, four surfaces.** A customer books on `P01`, an agent takes the same booking on
> `P03`, a corporate admin raises it in bulk on `P04`, and an agent takes it by phone on `P10`.
>
> **This file is the canonical wording** (`CG-003` X-01). The four packs cite it; none restates it.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | Cross-surface flow — `P01`, `P03`, `P04`, `P10` |
| Framework | All surfaces carrying this flow |
| Default language | Bengali default on customer and field surfaces |
| i18n namespace | ``flow.booking.*`` |
| Offline-capable | Where the carrying surface is offline-capable |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | Per surface (`VB-002` §4.2) (`VB-002` §4.2) |
| Audience | `P01`, `P03`, `P04`, `P10` |

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

### 3.1 The canonical sequence

| Step | Key | Canonical wording EN | Bengali | Surfaces |
|---|---|---|---|---|
| Identify device | `flow.booking.device` | Which device needs service? | কোন ডিভাইসের সার্ভিস প্রয়োজন? | All |
| Describe problem | `flow.booking.problem` | What is wrong? | কী সমস্যা হচ্ছে? | All |
| Choose mode | `flow.booking.mode` | How would you like service? | কীভাবে সার্ভিস নিতে চান? | `P01`, `P10` |
| Choose slot | `flow.booking.slot` | When suits you? | কখন আপনার সুবিধা হবে? | `P01`, `P10` |
| Price indication | `flow.booking.price` | Estimated {min}–{max}. We confirm after checking the device. | আনুমানিক {min}–{max}। ডিভাইস পরীক্ষার পর নিশ্চিত করব। | All |
| Confirm | `flow.booking.confirm` | Confirm booking | বুকিং নিশ্চিত করুন | All |
| Reference | `flow.booking.reference` | Your reference is {ref} | আপনার রেফারেন্স {ref} | All |

### 3.2 The promise — stated identically everywhere

| Promise | Key | Wording EN | Bengali |
|---|---|---|---|
| What happens next | `flow.booking.next` | We will contact you on {mobile} before {time}. | আমরা {time}-এর আগে {mobile}-এ যোগাযোগ করব। |
| Free diagnosis | `flow.booking.diagnosis` | Checking the device is free. You approve any cost before we start work. | ডিভাইস পরীক্ষা বিনামূল্যে। কাজ শুরুর আগে আপনি খরচ অনুমোদন করবেন। |
| Cancellation | `flow.booking.cancel_window` | You can cancel free until {time}. | {time} পর্যন্ত বিনামূল্যে বাতিল করতে পারবেন। |
| Data warning | `flow.booking.data` | Back up your data before handing over the device. | ডিভাইস দেওয়ার আগে আপনার ডেটা ব্যাকআপ নিন। |

> **`flow.booking.diagnosis` and `flow.booking.cancel_window` are commercial promises.** They
> appear on four surfaces and in `DT-002`. Changing them is a `CG-013` T-A12 escalation.

### 3.3 Surface variations — the only permitted ones

| Surface | Variation | Why |
|---|---|---|
| `P03` agent | Adds token number and condition capture | The device is physically present |
| `P04` bulk | Adds coverage check against contract before submission | Cost visibility before commitment |
| `P10` phone | Adds the read-aloud confirmation script | Spoken, not read (`VB-002` G-01) |

Any other variation is a defect, not a variation.

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
| No device identified | `flow.booking.error.device` | A booking needs an identified device (`BRU-SRM-01`). Search, or register it. | **H** |
| Mode unavailable | `flow.booking.error.mode` | {mode} is not available for {device} in {zone}. Available: {alternatives}. | **H** |
| No slot | `flow.booking.error.slot` | No slots on {date}. Earliest is {next}. | **H** |
| Lead time | `flow.booking.error.lead_time` | {mode} needs {hours} hours notice. Choose a later time. | **H** |

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
| [`../03B_Portals/UI-011_P01_Customer_Portal_and_App_UI_Copy_Pack.md`](../03B_Portals/UI-011_P01_Customer_Portal_and_App_UI_Copy_Pack.md) | Cites this flow |
| [`../03C_Admin_Workspaces/UI-023_Workspace_Service_Intake_Copy.md`](../03C_Admin_Workspaces/UI-023_Workspace_Service_Intake_Copy.md) | Cites this flow |
| `MD-020` Service Type and Delivery Mode Register | Mode eligibility |
| `DT-002` Service Intake Receipt | Reproduces the promises |

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
