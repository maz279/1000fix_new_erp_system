---
id: UI-015
title: P05 Vendor and Supplier Portal UI Copy Pack
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
  Screen copy for the vendor portal. Targets are more than 90% of POs acknowledged and 85% of
  invoices submitted through the portal, with a 60% reduction in vendor phone and email queries.
  Every ambiguity here is a phone call we are trying to eliminate.
traces_to: [P05, UI-001, UI-003, UI-004, MD-027, VB-002]
priority: P1
wave: W3
bilingual: yes
bn_counterpart: UI-015_P05_Vendor_and_Supplier_Portal_UI_Copy_Pack_BN.md
i18n_namespace: `p05.*`
pinned_to:
  surface: P05
  release: pending first build
  wave: W3
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §2 suite overview and the per-portal capability sets
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-015 — P05 Vendor and Supplier Portal UI Copy Pack

> **Every screen answers one question: what do you need from me, and by when?** (`VB-002` V-01).
> A rejection with no reason becomes a call, and the 60% query-reduction target is missed.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | P05 — parts vendors, couriers, sub-contractors (200–500) |
| Framework | Odoo Portal + Next.js |
| Default language | English |
| i18n namespace | ``p05.*`` |
| Offline-capable | No |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | ≤ 20 words (`VB-002` V-01) (`VB-002` §4.2) |
| Audience | parts vendors, couriers, sub-contractors (200–500) |

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

### 3.1 Orders — `p05.po.*`

| Element | Key | English | Max |
|---|---|---|---:|
| Title | `p05.po.title` | Purchase orders | 50 |
| Acknowledge | `p05.po.ack` | Acknowledge | 20 |
| Query | `p05.po.query` | Query this order | 20 |
| Confirm date | `p05.po.confirm_date` | Confirm delivery date | 24 |
| Overdue ack | `p05.po.ack_overdue` | {count} orders need acknowledgement. The oldest is {days} days old. | 200 |

### 3.2 Delivery — `p05.delivery.*`

| Element | Key | English |
|---|---|---|
| Expected | `p05.delivery.expected` | Expected receipts |
| Rejected | `p05.delivery.rejected` | {qty} of {total} rejected at inspection. Reason: {reason}. Collect or replace by {date}. |
| ASN | `p05.delivery.asn` | Submit advance shipping notice |

### 3.3 Invoicing — `p05.invoice.*`

| Element | Key | English |
|---|---|---|
| Submit | `p05.invoice.submit` | Submit invoice |
| Match status | `p05.invoice.match` | {status} — matched against {po} and receipt {grn} |
| Payment date | `p05.invoice.pay_date` | Scheduled for payment on {date} |
| Mismatch | `p05.invoice.mismatch` | The invoice does not match the order. Invoice {inv_amount}, order {po_amount}. Correct and resubmit. |

### 3.4 Scorecard — `p05.score.*`

| Element | Key | English |
|---|---|---|
| Title | `p05.score.title` | Your performance |
| On-time | `p05.score.on_time` | On-time delivery {pct}% over {period} |
| How to improve | `p05.score.improve` | {metric} is below target. {improvement_action} |

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
| Licence expired | `p05.error.licence_expired` | Your trade licence expired on {date}. Upload a current licence to receive new orders. | **H** |
| Bank change | `p05.error.bank_change` | Bank detail changes are verified before payment resumes. We will contact you on {phone}. | **H** |
| Late RFQ | `p05.error.rfq_closed` | This request closed on {date}. Watch for the next one. | **H** |

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
| `EO-005` Vendor and Supplier Onboarding Pack | Onboarding |
| `EO-006` Supplier Performance Scorecard Explanation | How the score moves |
| `MD-016` Vendor and Supplier Master Standard | The record behind it |

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
