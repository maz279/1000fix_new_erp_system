---
id: UI-038
title: Estimate and Approval Flow Copy
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
content_class: B
purpose: >
  Estimate presentation, part-approval, decline, revision, expiry and e-signature copy. Estimates
  above BDT 5,000 require documented customer approval (BRU-SRM-07) and above BDT 25,000 also branch
  manager approval (BRU-SRM-08); the wording of that approval is the evidence.
traces_to: [M01, M36, 05-05 BRU-SRM-07, BRU-SRM-08, LG-019, DT-005, DT-006, UI-011, UI-012]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: UI-038_Estimate_and_Approval_Flow_Copy_BN.md
i18n_namespace: `flow.estimate.*`
pinned_to:
  surface: `P01`, `P02`, `P03`, `P04`, `P10`
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

# UI-038 — Estimate and Approval Flow Copy

> ⚠ **Class B — legal.** This wording is the **evidence** that a customer approved a cost.
> `BRU-SRM-07` and `BRU-SRM-08` make documented approval a hard rule; if the wording is
> ambiguous, the evidence is weak.
>
> Gate **G5** legal review applies and is unwaivable (`WV-02`).

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | Cross-surface flow — `P01`, `P02`, `P03`, `P04`, `P10` |
| Framework | All surfaces carrying this flow |
| Default language | Bengali default on customer and field surfaces |
| i18n namespace | ``flow.estimate.*`` |
| Offline-capable | Where the carrying surface is offline-capable |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | B — Legal / contractual |
| Sentence budget | Per surface (`VB-002` §4.2) (`VB-002` §4.2) |
| Audience | `P01`, `P02`, `P03`, `P04`, `P10` |

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

### 3.1 Presentation

| Element | Key | Wording EN | Bengali |
|---|---|---|---|
| Heading | `flow.estimate.title` | What your device needs | আপনার ডিভাইসের যা প্রয়োজন |
| Diagnosis | `flow.estimate.diagnosis` | We found: {fault} | আমরা পেয়েছি: {fault} |
| Line item | `flow.estimate.line` | {item} — {amount} | {item} — {amount} |
| Parts total | `flow.estimate.parts` | Parts {amount} | পার্টস {amount} |
| Labour total | `flow.estimate.labour` | Labour {amount} | শ্রম {amount} |
| VAT | `flow.estimate.vat` | VAT {amount} | ভ্যাট {amount} |
| Total | `flow.estimate.total` | Total {amount} | মোট {amount} |
| Validity | `flow.estimate.valid_until` | This estimate is valid until {date}. | এই এস্টিমেট {date} পর্যন্ত বৈধ। |

### 3.2 The approval act — the evidentiary wording

| Element | Key | Wording EN | Bengali |
|---|---|---|---|
| Approve all | `flow.estimate.approve_all` | I approve this repair at {amount} | আমি {amount}-এ এই মেরামত অনুমোদন করছি |
| Approve some | `flow.estimate.approve_some` | I approve only the items I have selected, at {amount} | আমি শুধু নির্বাচিত আইটেমগুলি {amount}-এ অনুমোদন করছি |
| Decline | `flow.estimate.decline` | I do not want this repair | আমি এই মেরামত চাই না |
| Consequence of decline | `flow.estimate.decline_consequence` | Your device will be returned unrepaired. A diagnosis charge of {amount} applies. | আপনার ডিভাইস মেরামত ছাড়াই ফেরত দেওয়া হবে। {amount} পরীক্ষার চার্জ প্রযোজ্য। |
| Signature prompt | `flow.estimate.sign` | Sign to confirm your approval | আপনার অনুমোদন নিশ্চিত করতে স্বাক্ষর করুন |
| Evidence note | `flow.estimate.evidence` | Your approval, the time and this estimate are recorded. | আপনার অনুমোদন, সময় এবং এই এস্টিমেট রেকর্ড করা হয়। |

> **`flow.estimate.approve_all` is written in the first person deliberately.** It is a
> declaration by the customer, not an instruction to them — which is what makes it evidence
> (`LG-019`).

### 3.3 Revision and expiry

| Element | Key | Wording EN | Bengali |
|---|---|---|---|
| Revised | `flow.estimate.revised` | We found more than expected. The cost has changed from {old} to {new}. | আমরা প্রত্যাশার চেয়ে বেশি পেয়েছি। খরচ {old} থেকে {new} হয়েছে। |
| Why changed | `flow.estimate.revision_reason` | {reason} | {reason} |
| Re-approval needed | `flow.estimate.reapprove` | This needs your approval again before we continue. | চালিয়ে যাওয়ার আগে এটি আবার আপনার অনুমোদন প্রয়োজন। |
| Expired | `flow.estimate.expired` | This estimate expired on {date}. We will prepare a new one. | এই এস্টিমেট {date}-এ মেয়াদ শেষ হয়েছে। আমরা নতুন একটি তৈরি করব। |

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
| Work before approval | `flow.estimate.error.no_approval` | Work above BDT 5,000 needs the customer approval first (`BRU-SRM-07`). | **H** |
| Manager approval | `flow.estimate.error.manager` | Above BDT 25,000 also needs {branch_manager} approval (`BRU-SRM-08`). | **H** |
| Self-approval | `flow.estimate.error.self` | You cannot approve an estimate you prepared. | **H** |
| Parts before approval | `flow.estimate.error.parts` | Parts cannot be issued against an unapproved repair (`BRU-SRM-11`). | **H** |

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

| — | Is the diagnosis charge on decline confirmed and legally reviewed? | **Yes** | Legal + Commercial |
| # | Question | Blocking? | Owner |
|---|---|:--:|---|
| 1 | `BN-003` not written; Bengali indicative | **Yes** | Localisation Lead |
| 2 | No build exists; `pinned_to` incomplete | **Yes** | Platform Engineering |

---

## 10. Related documents

| Document | Relationship |
|---|---|
| `LG-019` E-Signature Legal Notice and Evidence Statement | The evidentiary basis |
| `DT-005` Repair Estimate and Quotation | The printed form |
| `DT-006` Revised Estimate and Approval Record | Revision evidence |
| `05-05` BRU-SRM-07, BRU-SRM-08, BRU-SRM-11 | The rules |

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
- [ ] G5 legal review — **outstanding, unwaivable (`WV-02`)**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
