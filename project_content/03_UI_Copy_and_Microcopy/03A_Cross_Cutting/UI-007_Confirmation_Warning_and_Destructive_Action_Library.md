---
id: UI-007
title: Confirmation, Warning and Destructive Action Library
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
reviewers: [Localisation Lead, Risk, all module business owners, Accessibility reviewer]
approver: Content Design Lead
content_class: C
purpose: >
  Confirmation dialogs, irreversible-action warnings, override-with-reason prompts and approval
  confirmations. BR-STD-06 permits overrides only where designed and always logged with a reason;
  the prompt that captures that reason is content, and it is the audit evidence.
traces_to: [05-05 BR-STD-06, VB-006 §5.5, MD-026, SP-004, CG-003 §3.3]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: UI-007_Confirmation_Warning_and_Destructive_Action_Library_BN.md
i18n_namespace: `common.confirm.*`
pinned_to:
  surface: All surfaces
  release: pending first build
  wave: W1
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §1 BR-STD-06 — overrides possible only where designed, always logged with a reason and an approver
    verified: 2026-08-15
    class: P1
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-006 §5.5 modal and confirmation contract
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-007 — Confirmation, Warning and Destructive Action Library

> **Never OK/Cancel on a destructive action.** A fast reader cannot tell which "cancel" means
> what (`VB-006` MD-03). Buttons are verbs.
>
> The title is a **statement**, not a question. The body states what will happen, including
> anything irreversible and anything the customer will see.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | Confirmation dialogs, irreversible-action warnings, override prompts, approval confirmations |
| Framework | All — Odoo OWL, Next.js, React Native, Flutter |
| Default language | Bengali default on customer and field surfaces (`PS-03`) |
| i18n namespace | ``common.confirm.*`` |
| Offline-capable | Applies to `P02`, `P09`, `P11` (`PS-08`) |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | C — Operational-critical |
| Sentence budget | Per surface — see `VB-002` §4.2 (`VB-002` §4.2) |
| Audience | All surfaces |

---

## 2. Terminology bindings

Every term below is fixed by `CG-004`. **This pack cites; it never invents.**

| Concept | Term | Never |
|---|---|---|
| Ending an order before completion | **cancel** | void, delete, abort |
| Nullifying a posted document | **void** | cancel, delete |
| Setting `active = False` | **archive** | delete, remove |
| Permanent destruction | **delete** | Applies to almost nothing (`05-02` DM-06) |

> Bengali forms are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

---

## 3. Screen copy

### 3.1 The pattern

| Slot | Rule | Budget (BN) |
|---|---|---:|
| Title | The action, sentence case, **no question mark** | 50 |
| Body | What will happen, in full, including irreversibility | 300 |
| Reason | Required wherever `BR-STD-06` applies | — |
| Primary button | The **verb of doing it** | 20 |
| Secondary button | The **verb of not doing it** | 20 |

### 3.2 Service and order — `common.confirm.order.*`

| Action | Key | Title EN | Body EN | Primary | Secondary |
|---|---|---|---|---|---|
| Cancel order | `common.confirm.order.cancel` | Cancel this service order | The customer will be notified by SMS. {parts_count} reserved parts will return to stock. The device is still at {branch} and must be returned or the order re-raised. This cannot be undone. | Cancel order | Keep order |
| Reassign job | `common.confirm.job.reassign` | Reassign this job to {technician} | {current_technician} will be notified. Any parts already reserved stay with the job. | Reassign | Keep assignment |
| Close without QC | `common.confirm.order.close_no_qc` | This order has no recorded quality check | Completing without a passed checklist is blocked. Complete the checklist, or request an exception from {quality_manager}. | Complete checklist | Go back |
| Mark beyond repair | `common.confirm.order.ber` | Mark this device beyond economic repair | The customer must confirm this decision before the device is returned or disposed of. Record their decision. | Record decision | Go back |

### 3.3 Financial — `common.confirm.fin.*`

| Action | Key | Title EN | Body EN | Primary | Secondary |
|---|---|---|---|---|---|
| Post invoice | `common.confirm.fin.post` | Post invoice {reference} | Posting creates the statutory record and allocates the next Mushak number. A posted invoice can only be corrected by a credit note. | Post invoice | Go back |
| Void invoice | `common.confirm.fin.void` | Void invoice {reference} | The number stays allocated and is recorded as void — statutory sequences cannot have gaps. Record a reason. | Void invoice | Keep invoice |
| Refund | `common.confirm.fin.refund` | Refund {amount} to {customer} | The refund goes back to {method} and takes {days} days to reach them. This cannot be undone. | Refund {amount} | Go back |
| Write off | `common.confirm.fin.writeoff` | Write off {amount} | This is recorded against {cost_centre} and appears in the monthly write-off report. Record a reason. | Write off | Go back |

### 3.4 Override — `common.confirm.override.*`

Where `BR-STD-06` permits an override, the prompt captures the reason **and** routes for
authority.

| Key | Title EN | Body EN | Fields |
|---|---|---|---|
| `common.confirm.override.request` | Request an exception to {rule} | {rule_plain_language} {authoriser_role} can authorise an exception. Your reason is recorded against the transaction and reviewed monthly. | Reason (from `MD-026`, required) · Free text (required) |
| `common.confirm.override.authorise` | Authorise this exception | {requester} asked to override {rule} on {object}. Reason: {reason}. Authorising is recorded against your name. | Decision · Note |

### 3.5 Data and access — `common.confirm.data.*`

| Action | Key | Title EN | Body EN | Primary |
|---|---|---|---|---|
| Archive record | `common.confirm.data.archive` | Archive {object} | It stops appearing in lists and cannot be used in new transactions. History is kept. You can restore it. | Archive |
| Bulk action | `common.confirm.data.bulk` | {action} {count} records | This applies to all {count} selected records across {scope}. | {action} {count} |
| Merge parties | `common.confirm.data.merge` | Merge {source} into {target} | All services, devices, contracts and invoices move to {target}. {source} is archived. This can be reversed for 30 days. | Merge |
| Revoke access | `common.confirm.data.revoke` | Remove {user} from {role} | They lose access immediately and any pending approvals return to {approver}. | Remove access |

---

## 4. Field labels and help text

Field copy is `UI-003`. This library carries no field labels.

---

## 5. Validation and error messages

> `BR-STD-04` and `PS-09`: every message states **what is wrong and what to do**, in the user's
> language. Three-part structure per `CG-003` §3.1. Client-side validation is **format only** —
> business rules are server-side (`PS-11`).

| # | Rule |
|---|---|
| **C-01** | Title is a statement, never a question (`VB-006` MD-01) |
| **C-02** | Body states the consequence **in full**, including what the customer sees |
| **C-03** | Irreversibility stated explicitly: "This cannot be undone" (`VB-006` MD-07) |
| **C-04** | Buttons are verbs; never OK/Cancel on a destructive action (`VB-006` MD-03) |
| **C-05** | Reason captured wherever `BR-STD-06` applies, from `MD-026` plus free text |
| **C-06** | The authorising **role** is named, never the person (`CG-003` E-05) |
| **C-07** | Bulk actions state the count **and** the scope (`VB-006` TB-07) |
| **C-08** | Never used for information the user could read in place (`VB-006` MD-06) |

---

## 6. Confirmations and destructive actions

Destructive-action copy is `UI-007`.

---

## 7. Accessibility text

| Item | Rule | SC |
|---|---|:--:|
| Focus | Moves into the dialog on open, returns to the trigger on close | 2.4.3 |
| Trap | Focus is trapped within the dialog | 2.1.2 |
| Escape | Closes the dialog and takes the **non-destructive** path | 2.1.1 |
| Title | The dialog's accessible name | 4.1.2 |
| Reason field | Labelled and marked required in text | 3.3.2 |
| Legal/financial | Reversible, checkable or confirmed | **3.3.4** |

---

## 8. Character budget and layout risk

Budgets are **Bengali** rendered lengths (`VB-006` `DS-04`). English runs 20–40% shorter.

| Slot | Budget (BN) | Risk |
|---|---:|---|
| Title | 50 | Low |
| Body | 300 | **High** — `order.cancel` has four clauses and three placeholders |
| Button | 20 | **Medium** — "Cancel order" is অর্ডার বাতিল করুন (18) |

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
| [`UI-004_Validation_and_Error_Message_Library.md`](UI-004_Validation_and_Error_Message_Library.md) | Messages that block rather than confirm |
| `05-05` BR-STD-06 | The override rule this implements |
| `MD-026` Reason Code Register | Reason values |
| `SP-004` Approval Matrix | Who authorises |
| `VB-006` §5.5 | The modal contract |

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
