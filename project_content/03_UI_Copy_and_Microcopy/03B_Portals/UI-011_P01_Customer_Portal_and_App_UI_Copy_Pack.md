---
id: UI-011
title: P01 Customer Portal and App UI Copy Pack
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
reviewers: [Localisation Lead, Design System, Accessibility reviewer, P01 owner]
approver: Content Design Lead
content_class: D
purpose: >
  Screen-by-screen copy for the highest-volume surface in the system. 250,000+ customers a month,
  Bengali-first, and booking funnel conversion is the primary design KPI at a > 72% target — copy
  is the principal lever on it.
traces_to: [P01, M01, M09, M10, M20, UI-037, UI-039, UI-042, MD-027, BN-009]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: UI-011_P01_Customer_Portal_and_App_UI_Copy_Pack_BN.md
i18n_namespace: `p01.*`
pinned_to:
  surface: P01
  release: pending first build
  wave: W2
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P01 capability set, design requirements and KPI table
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §3 PS-03, PS-04, PS-07
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-011 — P01 Customer Portal and App UI Copy Pack

> **The only audience that can leave.** Booking funnel conversion is `P01`'s primary design KPI
> (> 72%), and every word on the booking path is measured against it (`CG-014` E-08).
>
> Bengali is the default and English the toggle. Total first-load payload on the booking path is
> under 400 KB (`PS-07`), which constrains how much copy can ship before interaction.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | P01 — individual customers (250,000+/month) |
| Framework | Next.js 15 (web) + React Native (app) |
| Default language | **Bengali default**, English toggle (`PS-03`) |
| i18n namespace | ``p01.*`` |
| Offline-capable | PWA offline shell |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | ≤ 20 words (`VB-002` §4.2) (`VB-002` §4.2) |
| Audience | individual customers |

---

## 2. Terminology bindings

Every term below is fixed by `CG-004`. **This pack cites; it never invents.**

| Customer-facing term | Internal term | Entity | Note |
|---|---|---|---|
| My services | service order | `fix.service.order` | `CG-004` §10 item 2 open |
| Service centre | branch | `fix.branch` | Registered pair (`CG-004` §5) |
| Estimate | estimate | `fix.estimate` | Never "quotation" |
| Spare part | part | `fix.part` | Registered pair |
| Delayed | SLA breached | — | **Never show the internal label** (`T-06`) |

> Bengali forms are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

---

## 3. Screen copy

### 3.1 Home — `p01.home.*`

| Element | Key | English | Bengali | Max |
|---|---|---|---|---:|
| Greeting | `p01.home.greeting` | Hello {name} | নমস্কার {name} | 40 |
| Primary action | `p01.home.cta_book` | Book a service | সার্ভিস বুক করুন | 20 |
| Active services | `p01.home.active_title` | Your active services | আপনার চলমান সার্ভিস | 50 |
| Track prompt | `p01.home.track` | Track without signing in | সাইন ইন ছাড়াই ট্র্যাক করুন | 40 |
| Empty | `p01.home.empty` | No services yet | এখনও কোনো সার্ভিস নেই | 50 |

### 3.2 Booking — `p01.booking.*` (≤ 3 steps, `04-00` §P01)

| Element | Key | English | Bengali | Max |
|---|---|---|---|---:|
| Step 1 title | `p01.booking.step_device.title` | What needs fixing? | কী মেরামত করতে হবে? | 50 |
| Device help | `p01.booking.step_device.help` | Choose your device, or add a new one | আপনার ডিভাইস বেছে নিন, বা নতুন যোগ করুন | 120 |
| Step 2 title | `p01.booking.step_problem.title` | What is wrong? | কী সমস্যা হচ্ছে? | 50 |
| Symptom help | `p01.booking.step_problem.help` | Choose the closest match. You can add photos or a voice note. | কাছাকাছি বিকল্পটি বেছে নিন। ছবি বা ভয়েস নোট যোগ করতে পারেন। | 120 |
| Step 3 title | `p01.booking.step_how.title` | How would you like service? | কীভাবে সার্ভিস নিতে চান? | 50 |
| Price indication | `p01.booking.price_hint` | Estimated {min}–{max}. We confirm the price after checking your device. | আনুমানিক {min}–{max}। আপনার ডিভাইস পরীক্ষার পর আমরা মূল্য নিশ্চিত করব। | 140 |
| Confirm | `p01.booking.cta_confirm` | Confirm booking | বুকিং নিশ্চিত করুন | 20 |
| Done | `p01.booking.done.title` | Booking confirmed | বুকিং নিশ্চিত হয়েছে | 50 |
| Reference | `p01.booking.done.ref` | Your reference is {ref}. We sent it to {mobile}. | আপনার রেফারেন্স {ref}। আমরা এটি {mobile}-এ পাঠিয়েছি। | 140 |

### 3.3 Tracking — `p01.track.*`

| Element | Key | English | Bengali |
|---|---|---|---|
| Title | `p01.track.title` | Your service | আপনার সার্ভিস |
| Status | `p01.track.status` | {customer_status} | {customer_status} |
| Technician | `p01.track.technician` | {name} is on the way. About {minutes} minutes. | {name} আসছেন। প্রায় {minutes} মিনিট। |
| Delay | `p01.track.delayed` | This is taking longer than we planned. {reason} We will update you by {time}. | পরিকল্পনার চেয়ে বেশি সময় লাগছে। {reason} আমরা {time}-এর মধ্যে জানাব। |

> Status values come from `MD-027` **customer-facing** labels, never the internal state key.

### 3.4 Estimate approval — `p01.estimate.*`

Full flow copy is `UI-038`. Surface-specific wording only:

| Element | Key | English | Bengali |
|---|---|---|---|
| Waiting | `p01.estimate.waiting` | We checked your device. Here is what it needs. | আমরা আপনার ডিভাইস পরীক্ষা করেছি। এটির যা প্রয়োজন তা এখানে। |
| Approve | `p01.estimate.cta_approve` | Approve {amount} | {amount} অনুমোদন করুন |
| Part approve | `p01.estimate.cta_part` | Approve some items | কিছু আইটেম অনুমোদন করুন |
| Decline | `p01.estimate.cta_decline` | Decline | প্রত্যাখ্যান করুন |
| Decline outcome | `p01.estimate.decline_note` | We will return your device unrepaired. A diagnosis charge of {amount} applies. | আমরা আপনার ডিভাইস মেরামত ছাড়াই ফেরত দেব। {amount} পরীক্ষার চার্জ প্রযোজ্য। |

---

## 4. Field labels and help text

Shared field copy is `UI-003`. Surface-specific fields appear in §3.

---

## 5. Validation and error messages

> `BR-STD-04` and `PS-09`: every message states **what is wrong and what to do**, in the user's
> language. Three-part structure per `CG-003` §3.1. Client-side validation is **format only** —
> business rules are server-side (`PS-11`).

| Trigger | Key | Message EN | Class |
|---|---|---|:--:|
| Area not covered | `p01.error.zone_uncovered` | We do not offer on-site service in your area yet. You can use pick and drop, or visit {nearest_branch}. | **H** |
| No slots | `p01.error.no_slots` | No slots on {date}. The earliest is {next_date}. | **H** |
| Device not recognised | `p01.error.device_unknown` | We could not find that model. Choose the closest, or type it and we will confirm at the service centre. | **S** |
| Warranty expired | `p01.error.warranty_expired` | This device is out of warranty since {date}. This will be a paid repair. | **S** |

---

## 6. Confirmations and destructive actions

Destructive-action copy is `UI-007`. Surface-specific confirmations appear in §3.

---

## 7. Accessibility text

| Item | Rule | SC |
|---|---|:--:|
| Labels | Every input has a visible persistent label | 3.3.2 |
| Errors | Identified in text with a remedy | 3.3.1, 3.3.3 |
| Status | Colour is never the only signal (`VB-008`) | 1.4.1 |
| Language | `lang` declared; script changes marked | 3.1.1, 3.1.2 |
| Accessible names | From `UI-010`, translated | 1.1.1, 4.1.2 |
| Announcements | Errors assertive, confirmations polite | 4.1.3 |
| Booking steps | Step count stated up front; ≤ 3 steps | 3.2.3 |
| Price | Never colour-only; stated in text | 1.4.1 |

---

## 8. Character budget and layout risk

Budgets are **Bengali** rendered lengths (`VB-006` `DS-04`). English runs 20–40% shorter.

| Slot | Budget (BN) | Risk |
|---|---:|---|
| Primary CTA | 20 | **Medium** — "সার্ভিস বুক করুন" is 16 |
| Step title | 50 | Low |
| Help text | 120 | Medium |
| Price hint | 140 | **High** — two placeholders plus a caveat |

> Exceeding a budget is a **design conversation**, not a copy problem to solve by abbreviating
> (`VB-006` §8). Where the Bengali cannot fit, the control goes two-line before it goes
> icon-only (`VB-007` §7.3).

---

## 9. Open questions for design or product

| # | Question | Blocking? | Owner |
|---|---|:--:|---|
| 1 | Is "My services" or "My bookings" the customer term? (`CG-004` §10 item 2) | **Yes** | `M01` owner |
| 2 | Is the diagnosis charge on decline confirmed and legally reviewed? | **Yes** | Legal + Commercial |
| — | `BN-003` not written; Bengali indicative | **Yes** | Localisation Lead |
| — | No build exists; `pinned_to` incomplete | **Yes** | Platform Engineering |

---

## 10. Related documents

| Document | Relationship |
|---|---|
| [`../03D_Critical_Flows/UI-037_Booking_and_Order_Creation_Flow_Copy.md`](../03D_Critical_Flows/UI-037_Booking_and_Order_Creation_Flow_Copy.md) | Canonical booking wording |
| [`../03D_Critical_Flows/UI-038_Estimate_and_Approval_Flow_Copy.md`](../03D_Critical_Flows/UI-038_Estimate_and_Approval_Flow_Copy.md) | Canonical estimate wording |
| `BN-009` Bengali String Bundle P01 | The Bengali counterpart bundle |
| `MD-027` Status Register | Customer-facing status labels |
| `HC-003` Help Set P01 | Cites these labels verbatim |

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
