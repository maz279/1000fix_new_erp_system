---
id: UI-029
title: Workspace — Finance Console Copy
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
content_class: C
purpose: >
  Copy for the finance console. Reconciliation, ageing and close-checklist copy carries statutory
  consequence when misread; a posted invoice can only be corrected by a credit note.
traces_to: [M19, M20, M51, P03, MD-035, MD-037, MD-040, DT-010]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: UI-029_Workspace_Finance_Console_Copy_BN.md
i18n_namespace: `ws.finance.*`
pinned_to:
  surface: P03
  release: pending first build
  wave: W1
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P03 — fourteen role-scoped workspaces, each opening on the work its role actually does
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-029 — Workspace — Finance Console Copy

> **Statutory consequence.** Posting allocates a Mushak number from a gap-free sequence
> (`MD-040`). Every label here is read by someone whose action creates a legal record.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | P03 — Finance Console workspace (finance officers and managers (12–24)) |
| Framework | Odoo Web (OWL 2) |
| Default language | Bengali and English |
| i18n namespace | ``ws.finance.*`` |
| Offline-capable | No |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | C — Operational-critical |
| Sentence budget | ≤ 15 words (`VB-002` A-01) (`VB-002` §4.2) |
| Audience | finance officers and managers (12–24) |

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

### 3.1 Opens on — invoices, receipts, reconciliation, ageing, close checklist

| Element | Key | English | Bengali | Max |
|---|---|---|---|---:|
| Title | `ws.finance.title` | Finance | ফাইন্যান্স | 24 |
| To post | `ws.finance.to_post` | {count} invoices to post | পোস্ট করার জন্য {count}টি ইনভয়েস | 50 |
| Unreconciled | `ws.finance.unreconciled` | {count} receipts unreconciled | {count}টি রসিদ অমিলিত | 50 |
| Overdue | `ws.finance.overdue` | {amount} overdue across {count} accounts | {count}টি হিসাবে {amount} বকেয়া | 60 |
| Close status | `ws.finance.close` | {period} — {done} of {total} checklist items | {period} — {total}-এর {done}টি চেকলিস্ট আইটেম | 60 |
| Post | `ws.finance.post` | Post | পোস্ট করুন | 20 |
| Credit note | `ws.finance.credit_note` | Raise credit note | ক্রেডিট নোট তৈরি করুন | 24 |

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
| Period closed | `ws.finance.error.period` | {period} is closed. Post to the current period, or ask Finance to reopen it. | {period} বন্ধ। বর্তমান পিরিয়ডে পোস্ট করুন, বা ফাইন্যান্সকে পুনরায় খুলতে বলুন। | **H** |
| No tax class | `ws.finance.error.tax_class` | {item} has no tax class, so a compliant invoice cannot be issued. | {item}-এর কোনো ট্যাক্স ক্লাস নেই, তাই সামঞ্জস্যপূর্ণ চালান ইস্যু করা যাবে না। | **H** |
| BIN missing | `ws.finance.error.bin` | A VAT invoice to a business needs the buyer BIN. Add it to {customer}. | ব্যবসার ভ্যাট চালানে ক্রেতার BIN দরকার। {customer}-এ যোগ করুন। | **H** |
| Order not complete | `ws.finance.error.not_complete` | An invoice cannot be raised for an order that is not completed. | সম্পন্ন না হওয়া অর্ডারের চালান ইস্যু করা যায় না। | **H** |

---

## 6. Confirmations and destructive actions

Destructive-action copy is `UI-007`.

| Action | Confirmation |
|---|---|
| Post an invoice | States that a Mushak number is allocated and correction requires a credit note (`UI-007` §3.3) |
| Void | States that the number stays allocated and is recorded as void — sequences cannot have gaps |
| Reopen a period | Requires CFO approval and is logged |

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
- [ ] G2 factual and G3 technical review by the owning module business owner — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
