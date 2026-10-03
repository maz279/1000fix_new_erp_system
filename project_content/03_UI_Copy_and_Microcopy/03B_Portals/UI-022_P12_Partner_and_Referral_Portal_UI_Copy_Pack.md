---
id: UI-022
title: P12 Partner and Referral Portal UI Copy Pack
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
  Screen copy for the partner and referral portal. Attribution disputes are the normal failure mode
  of referral programmes; commission accuracy target is 100%, and disputes start with wording.
  Commission arithmetic is shown, never asserted.
traces_to: [P12, UI-001, UI-003, UI-004, MD-027, VB-002]
priority: P2
wave: W7
bilingual: yes
bn_counterpart: UI-022_P12_Partner_and_Referral_Portal_UI_Copy_Pack_BN.md
i18n_namespace: `p12.*`
pinned_to:
  surface: P12
  release: pending first build
  wave: W7
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §2 suite overview and the per-portal capability sets
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-022 — P12 Partner and Referral Portal UI Copy Pack

> **Attribution rules are stated plainly and identically in the portal, the agreement and the
> statement** (`VB-002` P-01). A partner who cannot reconcile their own commission will dispute
> it.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | P12 — alliance partners, referral partners, corporate resellers (100–500) |
| Framework | Next.js 15 |
| Default language | Bengali and English |
| i18n namespace | ``p12.*`` |
| Offline-capable | No |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | ≤ 20 words (`VB-002` P-01) (`VB-002` §4.2) |
| Audience | alliance partners, referral partners, corporate resellers (100–500) |

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

### 3.1 Referral — `p12.referral.*`

| Element | Key | English | Bengali |
|---|---|---|---|
| Link | `p12.referral.link` | Your referral link | আপনার রেফারেল লিংক |
| How it works | `p12.referral.how` | You earn when a customer you refer completes their first paid service | আপনি যাকে রেফার করেন তিনি প্রথম পেইড সার্ভিস সম্পন্ন করলে আপনি আয় করেন |
| Attribution window | `p12.referral.window` | Attribution lasts {days} days from the first click | প্রথম ক্লিক থেকে {days} দিন পর্যন্ত অ্যাট্রিবিউশন থাকে |
| Submit lead | `p12.referral.submit` | Submit a lead | লিড জমা দিন |

### 3.2 Lead status — `p12.lead.*`

| Element | Key | English | Bengali |
|---|---|---|---|
| Submitted | `p12.lead.submitted` | Submitted | জমা দেওয়া হয়েছে |
| Contacted | `p12.lead.contacted` | We have contacted them | আমরা যোগাযোগ করেছি |
| Converted | `p12.lead.converted` | Converted — commission {amount} | রূপান্তরিত — কমিশন {amount} |
| Not converted | `p12.lead.lost` | Not converted — {reason} | রূপান্তরিত হয়নি — {reason} |

### 3.3 Commission — `p12.commission.*`

| Element | Key | English | Bengali |
|---|---|---|---|
| Service value | `p12.commission.base` | Service value {amount} | সার্ভিসের মূল্য {amount} |
| Rate | `p12.commission.rate` | Your rate {pct}% | আপনার হার {pct}% |
| Earned | `p12.commission.earned` | You earned {amount} | আপনি {amount} আয় করেছেন |
| Payout | `p12.commission.payout` | Paid on {date} to {bank} | {date}-এ {bank}-এ পরিশোধ |

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
| Outside window | `p12.error.window_expired` | This customer first came to us {days} days ago, beyond the {window}-day window. | **H** |
| Already attributed | `p12.error.already_attributed` | This customer is already attributed to another partner. | **H** |
| Agreement not signed | `p12.error.no_agreement` | Sign the partner agreement to start earning commission. | **H** |

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
| Button | 20 | Medium — Bengali verbs run long |
| Column header | 24 | **High** at 1366×600 density |
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
| `LG-007` Referral and Alliance Partner Agreement | Attribution rules |
| `EO-009` Referral and Alliance Partner Kit | Onboarding |
| `DT-040` Partner Commission Statement | The statement this mirrors |

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
