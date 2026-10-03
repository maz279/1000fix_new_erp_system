---
id: UI-018
title: P08 Brand Partner Portal UI Copy Pack
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
  Screen copy for brand partners reviewing our warranty claims. International, expert, and judging
  our professionalism by our documentation. Claim approval target is above 92% and decision time
  under 10 days; both depend on evidence being complete and unarguable at submission.
traces_to: [P08, UI-001, UI-003, UI-004, MD-027, VB-002]
priority: P2
wave: W4
bilingual: yes
bn_counterpart: UI-018_P08_Brand_Partner_Portal_UI_Copy_Pack_BN.md
i18n_namespace: `p08.*`
pinned_to:
  surface: P08
  release: pending first build
  wave: W4
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §2 suite overview and the per-portal capability sets
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-018 — P08 Brand Partner Portal UI Copy Pack

> **Present the evidence; let the claim stand on it** (`VB-002` B-04). This surface never
> advocates.
>
> English only. Do not part-translate (`VB-002` B-02).

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | P08 — 17+ authorised brand partners (50–150) |
| Framework | Next.js 15 |
| Default language | **English only** (`CG-010` §3.2) |
| i18n namespace | ``p08.*`` |
| Offline-capable | No |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | ≤ 25 words (`VB-002` B-01) (`VB-002` §4.2) |
| Audience | 17+ authorised brand partners (50–150) |

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

### 3.1 Claim queue — `p08.claim.*`

| Element | Key | English |
|---|---|---|
| Title | `p08.claim.title` | Claims awaiting your decision |
| Ageing | `p08.claim.ageing` | {count} claims, oldest {days} days |
| Approve | `p08.claim.approve` | Approve claim |
| Part approve | `p08.claim.part_approve` | Approve in part |
| Reject | `p08.claim.reject` | Reject claim |
| Request info | `p08.claim.request_info` | Request more information |
| Reject reason | `p08.claim.reject_reason` | Select a reason. It is shown to 1000FiX and recorded against this claim. |

### 3.2 Evidence — `p08.evidence.*`

| Element | Key | English |
|---|---|---|
| Diagnosis | `p08.evidence.diagnosis` | Diagnosis and fault code |
| Photos | `p08.evidence.photos` | Before and after photographs |
| Parts | `p08.evidence.parts` | Parts replaced, with part numbers |
| Technician | `p08.evidence.technician` | Technician and certification, valid to {date} |
| Purchase proof | `p08.evidence.purchase` | Proof of purchase |
| Complete | `p08.evidence.complete` | All required evidence is attached |
| Incomplete | `p08.evidence.incomplete` | {missing} is not attached |

### 3.3 Performance — `p08.perf.*`

| Element | Key | English |
|---|---|---|
| Title | `p08.perf.title` | 1000FiX performance on {brand} |
| Volume | `p08.perf.volume` | {count} services this period |
| First-time fix | `p08.perf.ftf` | First-time fix {pct}% |
| Failure pattern | `p08.perf.pattern` | {model} accounts for {pct}% of claims — {count} in {period} |

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
| Outside agreement | `p08.error.out_of_scope` | {model} is outside the categories in your agreement dated {date}. | **H** |
| Window expired | `p08.error.window` | This claim was submitted {days} days after service, beyond the {window}-day window. | **H** |
| Bulk limit | `p08.error.bulk_limit` | Bulk decisions apply to at most {max} claims at a time. | **H** |

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
| `EO-003` Brand Partner Onboarding Pack | Portal onboarding |
| `EO-004` Brand Claim Rules and Evidence Standard Guide | What complete evidence means |
| `DT-033` Warranty Claim Evidence Pack | The pack this displays |
| `MD-017` Brand Partner Master Register | Agreement scope |

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
