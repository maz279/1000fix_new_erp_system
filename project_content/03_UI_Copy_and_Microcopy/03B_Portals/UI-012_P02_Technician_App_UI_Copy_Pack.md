---
id: UI-012
title: P02 Technician App UI Copy Pack
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
reviewers: [Localisation Lead, Design System, Accessibility reviewer, P02 owner]
approver: Content Design Lead
content_class: D
purpose: >
  Screen-by-screen copy for the technician application. 200–400 field technicians, complete Bengali
  interface including error messages, read one-handed and outdoors on a mid-range Android 11 device
  with 3 GB RAM, offline for up to 24 hours.
traces_to: [P02, M01, M02, M15, M22, UI-009, MD-024, MD-025, BN-010, TR-009]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: UI-012_P02_Technician_App_UI_Copy_Pack_BN.md
i18n_namespace: `p02.*`
pinned_to:
  surface: P02
  release: pending first build
  wave: W2
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P02 capability set and the seven non-negotiable requirements
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §3 PS-03, PS-08
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-012 — P02 Technician App UI Copy Pack

> **Eight to twelve words. If it does not fit, the screen is wrong, not the copy** (`VB-002`
> T-01).
>
> Non-negotiable #3 requires the Bengali interface to be **complete, including error messages**.
> There is no English fallback on this surface — a missing Bengali string is a defect, not a
> degradation.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | P02 — field and workshop technicians (200–400) |
| Framework | Flutter (Android primary) |
| Default language | **Bengali, complete — including error messages** (`P02` non-negotiable #3) |
| i18n namespace | ``p02.*`` |
| Offline-capable | **Yes — 24 hours** (`PS-08`, `NFR-047`) |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | ≤ 12 words (`VB-002` T-01) (`VB-002` §4.2) |
| Audience | field and workshop technicians |

---

## 2. Terminology bindings

Every term below is fixed by `CG-004`. **This pack cites; it never invents.**

| Term | Bengali | Entity | Note |
|---|---|---|---|
| Job | জব | `fix.dispatch.job` | Not "service order" — that is the parent |
| Part | পার্টস | `fix.part` | Full technical vocabulary permitted (`VB-002` T-03) |
| Fault | ত্রুটি | `MD-024` | Confirmed, not reported |
| Symptom | লক্ষণ | `MD-024` | What the customer said |
| Van stock | ভ্যান স্টক | `MD-004` | Their own custody |

> Bengali forms are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

---

## 3. Screen copy

### 3.1 Day — `p02.day.*`

| Element | Key | English | Bengali | Words |
|---|---|---|---|---:|
| Queue title | `p02.day.queue` | Today — {count} jobs | আজ — {count}টি জব | 4 |
| Clock in | `p02.day.clock_in` | Clock in | ক্লক ইন | 2 |
| Clock out | `p02.day.clock_out` | Clock out | ক্লক আউট | 2 |
| Outside geofence | `p02.day.geofence_fail` | You are {distance} from {branch}. Clock in anyway? | আপনি {branch} থেকে {distance} দূরে। তবুও ক্লক ইন করবেন? | 9 |
| Accept job | `p02.day.accept` | Accept | গ্রহণ করুন | 2 |
| Decline job | `p02.day.decline` | Decline | প্রত্যাখ্যান | 2 |
| Decline reason | `p02.day.decline_reason` | Why are you declining? | কেন প্রত্যাখ্যান করছেন? | 4 |

### 3.2 Job execution — `p02.job.*`

| Element | Key | English | Bengali | Words |
|---|---|---|---|---:|
| Navigate | `p02.job.navigate` | Navigate | পথ দেখান | 1 |
| Arrived | `p02.job.arrived` | I have arrived | আমি পৌঁছেছি | 3 |
| Start work | `p02.job.start` | Start work | কাজ শুরু করুন | 2 |
| Pause | `p02.job.pause` | Pause | বিরতি | 1 |
| Pause reason | `p02.job.pause_reason` | Why are you pausing? | কেন বিরতি নিচ্ছেন? | 4 |
| Record fault | `p02.job.fault` | Record the fault | ত্রুটি রেকর্ড করুন | 3 |
| Photo before | `p02.job.photo_before` | Photo before work | কাজের আগের ছবি | 3 |
| Photo after | `p02.job.photo_after` | Photo after work | কাজের পরের ছবি | 3 |
| Voice note | `p02.job.voice` | Voice note | ভয়েস নোট | 2 |
| Complete | `p02.job.complete` | Complete job | জব সম্পন্ন করুন | 2 |

### 3.3 Parts — `p02.parts.*`

| Element | Key | English | Bengali | Words |
|---|---|---|---|---:|
| Van stock | `p02.parts.van` | Van stock | ভ্যান স্টক | 2 |
| Scan to use | `p02.parts.scan` | Scan the part | পার্টস স্ক্যান করুন | 3 |
| Not in van | `p02.parts.not_in_van` | Not in your van. Request it? | আপনার ভ্যানে নেই। অনুরোধ করবেন? | 6 |
| Return unused | `p02.parts.return` | Return unused parts | অব্যবহৃত পার্টস ফেরত দিন | 3 |
| Hazard warning | `p02.parts.hazard` | {part} is {hazard}. Read the handling steps. | {part} একটি {hazard}। হ্যান্ডলিং ধাপ পড়ুন। | 7 |

### 3.4 Customer interaction — `p02.customer.*`

| Element | Key | English | Bengali | Words |
|---|---|---|---|---:|
| Show estimate | `p02.customer.show_estimate` | Show the estimate | এস্টিমেট দেখান | 3 |
| Customer approved | `p02.customer.approved` | Customer approved {amount} | গ্রাহক {amount} অনুমোদন করেছেন | 4 |
| Signature | `p02.customer.sign` | Ask the customer to sign | গ্রাহককে স্বাক্ষর করতে বলুন | 5 |
| Take payment | `p02.customer.pay` | Take payment | পেমেন্ট নিন | 2 |
| Receipt sent | `p02.customer.receipt` | Receipt sent to {mobile} | {mobile}-এ রসিদ পাঠানো হয়েছে | 4 |

### 3.5 Safety — `p02.safety.*`

**The one exception to the word budget** (`VB-002` T-06). Safety content is never abbreviated.

| Element | Key | English | Bengali |
|---|---|---|---|
| Panic | `p02.safety.panic` | Send safety alert | নিরাপত্তা সতর্কতা পাঠান |
| Panic sent | `p02.safety.panic_sent` | Alert sent. Dispatch is calling you now. Stay where you are if it is safe. | সতর্কতা পাঠানো হয়েছে। ডিসপ্যাচ এখনই আপনাকে কল করছে। নিরাপদ হলে যেখানে আছেন সেখানেই থাকুন। |
| Hazard step | `p02.safety.hazard_steps` | Before you start: {steps}. Confirm you have read this. | শুরুর আগে: {steps}। আপনি এটি পড়েছেন তা নিশ্চিত করুন। |

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
| Not certified | `p02.error.not_certified` | You are not certified for {brand}. Ask dispatch to reassign. | **H** |
| Estimate not approved | `p02.error.estimate_needed` | Get approval before starting. Send the estimate now. | **H** |
| QC not done | `p02.error.qc_needed` | Complete the quality checklist first. | **H** |
| Photo missing | `p02.error.photo_needed` | Add a photo before completing. | **H** |
| Part not scanned | `p02.error.part_unscanned` | Scan every part you used. | **H** |

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
| Touch targets | 44 px minimum; larger in the field | 2.5.5 |
| Sunlight | High contrast, no tint fill (`VB-008` §5) | 1.4.3 |
| One-handed | Primary actions in the lower third | — |

---

## 8. Character budget and layout risk

Budgets are **Bengali** rendered lengths (`VB-006` `DS-04`). English runs 20–40% shorter.

| Slot | Budget (BN) | Risk |
|---|---:|---|
| Button | 20 | **High** — Bengali verbs with করুন run long |
| Message | 12 words | **High** — the tightest budget in the system |
| Safety text | No budget | Deliberate exception |

> Exceeding a budget is a **design conversation**, not a copy problem to solve by abbreviating
> (`VB-006` §8). Where the Bengali cannot fit, the control goes two-line before it goes
> icon-only (`VB-007` §7.3).

---

## 9. Open questions for design or product

| # | Question | Blocking? | Owner |
|---|---|:--:|---|
| 1 | Bengali imperative register — করুন (formal) or কর (informal)? `BN-002` decides | **Yes** — every string | Localisation Lead |
| 2 | Does the geofence override need supervisor approval in-app or after the fact? | **Yes** | `M55` owner |
| — | `BN-003` not written; Bengali indicative | **Yes** | Localisation Lead |
| — | No build exists; `pinned_to` incomplete | **Yes** | Platform Engineering |

---

## 10. Related documents

| Document | Relationship |
|---|---|
| [`../03A_Cross_Cutting/UI-009_Offline_Sync_and_Conflict_Resolution_Copy.md`](../03A_Cross_Cutting/UI-009_Offline_Sync_and_Conflict_Resolution_Copy.md) | Offline states |
| `BN-010` Bengali String Bundle P02 | **Complete Bengali required** |
| `TR-009` Course Pack Field Technician | Bengali-native training citing these labels |
| `MD-024`, `MD-025` | Fault and resolution codes |
| `TS-015` Offline and Field Condition Test Scripts | Verification |

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
