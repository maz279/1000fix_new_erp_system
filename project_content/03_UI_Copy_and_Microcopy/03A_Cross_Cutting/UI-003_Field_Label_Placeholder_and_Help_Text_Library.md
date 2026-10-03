---
id: UI-003
title: Field Label, Placeholder and Help Text Library
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
reviewers: [Localisation Lead, Design System, Accessibility reviewer, portal owners]
approver: Content Design Lead
content_class: D
purpose: >
  Label, placeholder, hint, unit and inline-help text for every field of every governed entity.
  225+ entities with unlabelled or inconsistently labelled fields makes data entry the largest
  single source of data-quality defects.
traces_to: [05-02, CG-004, VB-006 §6.2, CG-011 EA-05, MD-013, MD-021]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: UI-003_Field_Label_Placeholder_and_Help_Text_Library_BN.md
i18n_namespace: `common.field.*`
pinned_to:
  surface: All surfaces
  release: pending first build
  wave: W1
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 Data Model and Entity Catalogue
    verified: 2026-08-15
    class: P1
  - source: W3C WCAG 2.1 SC 3.3.2 Labels or Instructions
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-003 — Field Label, Placeholder and Help Text Library

> **A placeholder is not a label.** It disappears on focus, so a form labelled only by
> placeholders is unusable for anyone who pauses (WCAG SC 3.3.2, `VB-006` `FF-01`).
>
> Labels here are the **canonical** wording. Help articles and training cite them verbatim in
> bold (`CG-003` X-03).

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | Every field of every governed entity |
| Framework | All — Odoo OWL, Next.js, React Native, Flutter |
| Default language | Bengali default on customer and field surfaces (`PS-03`) |
| i18n namespace | ``common.field.*`` |
| Offline-capable | Applies to `P02`, `P09`, `P11` (`PS-08`) |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | D — User-facing |
| Sentence budget | Per surface — see `VB-002` §4.2 (`VB-002` §4.2) |
| Audience | All surfaces |

---

## 2. Terminology bindings

Every term below is fixed by `CG-004`. **This pack cites; it never invents.**

| Field concept | Label | Entity | Never |
|---|---|---|---|
| Service order reference | Reference | `fix.service.order` | Job no., ticket no. |
| Device serial | Serial number | `fix.asset` | S/N, serial no. |
| Mobile IMEI | IMEI | `fix.asset` | Device ID |
| Party mobile | Mobile number | `fix.party` | Phone, contact no. |
| Business ID | BIN | `fix.entity` | VAT number |
| Taxpayer ID | TIN | `fix.party` | Tax number |

> Bengali forms are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

---

## 3. Screen copy

Field copy is organised by entity, not by screen — one label per field, used everywhere.

### 3.1 Party fields — `common.field.party.*`

| Field | Key | Label EN | Label BN | Placeholder | Help | Req |
|---|---|---|---|---|---|:--:|
| Mobile | `common.field.party.mobile` | Mobile number | মোবাইল নম্বর | 01712345678 | We send your service updates to this number | ✔ |
| Name | `common.field.party.name` | Full name | পুরো নাম | — | As it should appear on your invoice | ✔ |
| Email | `common.field.party.email` | Email | ইমেইল | name@example.com | Optional. Used for invoices and receipts | |
| BIN | `common.field.party.bin` | BIN | বিআইএন | 13 digits | Required to issue a VAT invoice to a business | |
| Preferred language | `common.field.party.language` | Preferred language | পছন্দের ভাষা | — | We contact you in this language | ✔ |

### 3.2 Device fields — `common.field.device.*`

| Field | Key | Label EN | Label BN | Placeholder | Help | Req |
|---|---|---|---|---|---|:--:|
| Brand | `common.field.device.brand` | Brand | ব্র্যান্ড | — | — | ✔ |
| Model | `common.field.device.model` | Model | মডেল | — | Start typing to search | ✔ |
| Serial number | `common.field.device.serial` | Serial number | সিরিয়াল নম্বর | — | Usually on a sticker under the device | |
| IMEI | `common.field.device.imei` | IMEI | আইএমইআই | 15 digits | Dial \*#06# to see it on your phone | |
| Purchase date | `common.field.device.purchase_date` | Purchase date | ক্রয়ের তারিখ | DD/MM/YYYY | Helps us check your warranty | |

### 3.3 Service order fields — `common.field.order.*`

| Field | Key | Label EN | Label BN | Placeholder | Help | Req |
|---|---|---|---|---|---|:--:|
| Reference | `common.field.order.reference` | Reference | রেফারেন্স | — | Quote this when you contact us | ✔ |
| Symptom | `common.field.order.symptom` | What is wrong? | কী সমস্যা হচ্ছে? | — | Choose the closest match (`MD-024`) | ✔ |
| Description | `common.field.order.description` | Describe the problem | সমস্যাটি বর্ণনা করুন | — | Add photos or a voice note if it helps | |
| Delivery mode | `common.field.order.mode` | How would you like service? | কীভাবে সার্ভিস নিতে চান? | — | `MD-020` | ✔ |
| Accessories | `common.field.order.accessories` | Accessories left with the device | ডিভাইসের সাথে দেওয়া আনুষঙ্গিক | — | Charger, bag, SIM tray — we record and return these | |

### 3.4 Money and quantity fields — `common.field.amount.*`

| Field | Key | Label EN | Label BN | Format | Note |
|---|---|---|---|---|---|
| Amount | `common.field.amount.value` | Amount | পরিমাণ | `BDT 12,500.00` | Tabular figures, right-aligned (`VB-003` TY-03) |
| Quantity | `common.field.qty.value` | Quantity | পরিমাণ | Integer | UoM shown as a suffix (`MD-023`) |
| Discount | `common.field.amount.discount` | Discount | ছাড় | % or BDT | Ceiling from `MD-030` |

---

## 4. Field labels and help text

### 4.1 Rules

| # | Rule | Source |
|---|---|---|
| **F-01** | Every field has a **visible, persistent label**. Placeholder is never the label | WCAG SC 3.3.2, `VB-006` FF-01 |
| **F-02** | Required is marked in **text**, not only by an asterisk or colour | `VB-006` FF-02, `CG-011` CL-05 |
| **F-03** | Format requirements appear **before** submission, not only on failure | `CG-011` EA-06 |
| **F-04** | Help text explains **why** the field exists or **what format** it needs — never restates the label | `VB-006` FF-04 |
| **F-05** | Placeholder shows an **example**, never an instruction | `VB-006` FF-05 |
| **F-06** | Labels come from `CG-004`; a field naming a business object uses that object's approved term | `CG-004` |
| **F-07** | Where most fields are required, mark the **optional** ones instead | `VB-006` FF-07 |
| **F-08** | Units are a suffix, not part of the label. "Amount" + `BDT`, never "Amount (BDT)" in the label slot | `VB-003` TY-03 |

### 4.2 Sensitive fields

Fields classified **S3** in `05-02` §10 — NID, TIN, passport, bank account, biometric reference
— carry an additional disclosure line, authored in `UI-042`, explaining why the field is needed
and where the data is held (`NFR-086`, `NFR-092`).

---

## 5. Validation and error messages

> `BR-STD-04` and `PS-09`: every message states **what is wrong and what to do**, in the user's
> language. Three-part structure per `CG-003` §3.1. Client-side validation is **format only** —
> business rules are server-side (`PS-11`).

| Trigger | Key | Message EN | Remedy? | Class |
|---|---|---|---|:--:|
| Required field empty | `common.error.field.required` | Enter {field}. | ✔ | **H** |
| Mobile format | `common.error.field.mobile_format` | Enter the mobile number as 11 digits starting 01. | ✔ | **H** |
| IMEI format | `common.error.field.imei_format` | Enter the IMEI as 15 digits with no spaces. | ✔ | **H** |
| BIN format | `common.error.field.bin_format` | Enter the BIN as 13 digits. | ✔ | **H** |
| Date format | `common.error.field.date_format` | Enter the date as DD/MM/YYYY. | ✔ | **H** |
| Future date not allowed | `common.error.field.date_future` | The purchase date cannot be in the future. | ✔ | **H** |
| Amount precision | `common.error.field.amount_precision` | Enter the amount with up to two decimal places. | ✔ | **H** |
| Text too long | `common.error.field.max_length` | Shorten this to {max} characters. You have {current}. | ✔ | **S** |

> These are **format** rules only — client-side validation never evaluates a business rule
> (`PS-11`). Business-rule messages are `UI-004`.

---

## 6. Confirmations and destructive actions

No destructive actions in this library. Destructive-action copy is `UI-007`.

---

## 7. Accessibility text

| Item | Rule | SC |
|---|---|:--:|
| Label association | Every input is programmatically associated with its visible label | 1.3.1 |
| Required state | Announced as required, not only shown | 3.3.2 |
| Help text | Associated with the field so it is announced on focus | 3.3.2 |
| Error association | The message is programmatically linked to the field | 3.3.1 |
| Format hint | Present **before** input, not only after failure | 3.3.2 |
| Bengali labels | Marked `lang="bn"`; embedded Latin (IMEI, BIN) marked `lang="en"` | 3.1.2 |

---

## 8. Character budget and layout risk

Budgets are **Bengali** rendered lengths (`VB-006` `DS-04`). English runs 20–40% shorter.

| Slot | Budget (BN) | Longest BN here | Risk |
|---|---:|---|---|
| Label | 36 | কী সমস্যা হচ্ছে? (16) | Low |
| Help text | 120 | ডিভাইসের সাথে দেওয়া আনুষঙ্গিক… | Medium — help wraps to two lines on mobile |
| Placeholder | 40 | — | Low |
| Validation message | 90 | 11 ডিজিটের মোবাইল নম্বর লিখুন… | Medium |

> Exceeding a budget is a **design conversation**, not a copy problem to solve by abbreviating
> (`VB-006` §8). Where the Bengali cannot fit, the control goes two-line before it goes
> icon-only (`VB-007` §7.3).

---

## 9. Open questions for design or product

| # | Question | Blocking? | Owner |
|---|---|:--:|---|
| 1 | `BN-003` terminology is not yet written; Bengali here is indicative | **Yes** | Localisation Lead |

---

## 10. Related documents

| Document | Relationship |
|---|---|
| [`UI-004_Validation_and_Error_Message_Library.md`](UI-004_Validation_and_Error_Message_Library.md) | Business-rule messages |
| [`UI-042_Consent_Privacy_and_Preference_Centre_Copy.md`](../03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md) | S3 field disclosure |
| `05-02` Data Model and Entity Catalogue | The fields this labels |
| `CG-004` Terminology Standard | Approved field terms |

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
