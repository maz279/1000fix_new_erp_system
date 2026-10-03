---
id: UI-034
title: Workspace — Marketplace Console Copy
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
  Copy for the marketplace console. Seller approval, dispute and payout language has contractual
  force under the seller agreement; a suspension worded loosely is a suspension that can be
  challenged.
traces_to: [M12, P03, P07, LG-004, MD-018, EO-002]
priority: P2
wave: W7
bilingual: yes
bn_counterpart: UI-034_Workspace_Marketplace_Console_Copy_BN.md
i18n_namespace: `ws.marketplace.*`
pinned_to:
  surface: P03
  release: pending first build
  wave: W7
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P03 — fourteen role-scoped workspaces, each opening on the work its role actually does
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-034 — Workspace — Marketplace Console Copy

> **Contractual force.** Approval, suspension and payout-hold wording here is governed by
> `LG-004`. This console governs an external workforce of 500–2,000 people.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | P03 — Marketplace Console workspace (marketplace operations officers (4–10)) |
| Framework | Odoo Web (OWL 2) |
| Default language | Bengali and English |
| i18n namespace | ``ws.marketplace.*`` |
| Offline-capable | No |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | ≤ 15 words (`VB-002` A-01) (`VB-002` §4.2) |
| Audience | marketplace operations officers (4–10) |

---

## 2. Terminology bindings

Every term below is fixed by `CG-004`. **This pack cites; it never invents.**

| Term | Entity | Note |
|---|---|---|
| Per `CG-004` §4 | — | This pack cites approved terms; it never invents |
| Status labels | `MD-027` | Internal labels here — never the customer-facing ones |

> Bengali forms are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

---

## 3. Screen copy

### 3.1 Opens on — seller approvals, disputes, scores, payouts

| Element | Key | English | Bengali | Max |
|---|---|---|---|---:|
| Title | `ws.marketplace.title` | Marketplace | মার্কেটপ্লেস | 24 |
| To verify | `ws.marketplace.to_verify` | {count} sellers awaiting verification | যাচাইয়ের অপেক্ষায় {count}জন বিক্রেতা | 60 |
| Below threshold | `ws.marketplace.below` | {count} below rating threshold | রেটিং সীমার নিচে {count}জন | 50 |
| Open disputes | `ws.marketplace.disputes` | {count} open disputes | {count}টি খোলা বিরোধ | 50 |
| Payouts held | `ws.marketplace.held` | {amount} held across {count} sellers | {count}জন বিক্রেতার {amount} আটকে আছে | 60 |
| Approve seller | `ws.marketplace.approve` | Approve seller | বিক্রেতা অনুমোদন করুন | 24 |

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
| Documents unverified | `ws.marketplace.error.docs` | {seller} cannot transact until every required document is verified. | **H** |
| Agreement unsigned | `ws.marketplace.error.agreement` | {seller} has not signed the agreement. Approval is blocked. | **H** |
| Suspension threshold | `ws.marketplace.error.threshold` | {seller} rating is {rating}, below the suspension threshold of {suspend}. | **S** |

---

## 6. Confirmations and destructive actions

Destructive-action copy is `UI-007`.

| Action | Confirmation |
|---|---|
| Suspend a seller | States the contractual ground from `LG-004`, the effect on open jobs and held payouts, and the appeal route |
| Release a held payout | States the dispute status and that release is recorded |

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
| [`../03B_Portals/UI-013_P03_Admin_Operations_Portal_UI_Copy_Pack.md`](../03B_Portals/UI-013_P03_Admin_Operations_Portal_UI_Copy_Pack.md) | Shared shell copy |
| [`../03A_Cross_Cutting/UI-004_Validation_and_Error_Message_Library.md`](../03A_Cross_Cutting/UI-004_Validation_and_Error_Message_Library.md) | Business-rule messages |
| `MD-027` Status and Lifecycle State Label Register | Internal state labels |
| `VB-008` Status Colour and Label Semantics Register | Status treatment |

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
