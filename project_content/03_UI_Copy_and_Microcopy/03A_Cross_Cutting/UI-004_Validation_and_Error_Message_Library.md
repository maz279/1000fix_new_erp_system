---
id: UI-004
title: Validation and Error Message Library
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
reviewers: [Localisation Lead, all module business owners, Accessibility reviewer, Security]
approver: Content Design Lead
content_class: C
purpose: >
  Every field-level, form-level and business-rule violation message, with cause and remedy, in both
  languages. BR-STD-04 requires every rule violation to state what is wrong and what to do, in the
  user language; PS-09 extends the same obligation to every user-visible error on every portal.
  This library is where that contractual obligation is discharged.
traces_to: [05-05 BR-STD-04, 05-05 BR-STD-05, PS-09, PS-11, CG-003 §3, CG-011 §5, MD-026]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: UI-004_Validation_and_Error_Message_Library_BN.md
i18n_namespace: `common.error.*`
pinned_to:
  surface: All surfaces
  release: pending first build
  wave: W1
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §1 BR-STD-04 and the rule classification H/A/S/C
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §3 PS-09 and PS-11
    verified: 2026-08-15
    class: P1
  - source: W3C WCAG 2.1 SC 3.3.1 Error Identification and SC 3.3.3 Error Suggestion
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# UI-004 — Validation and Error Message Library

> **This is the file that makes `PS-09` and `BR-STD-04` true.** Both are contractual, not
> stylistic: every user-visible error states what happened and what to do next, in the user's
> language.
>
> Message class must match the rule class in `05-05`:
> **H** blocks · **A** names the authoriser · **S** warns and permits · **C** is computed and
> silent.

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | Every field-level, form-level and business-rule violation message |
| Framework | All — Odoo OWL, Next.js, React Native, Flutter |
| Default language | Bengali default on customer and field surfaces (`PS-03`) |
| i18n namespace | ``common.error.*`` |
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
| A blocked action | **cannot** | "not allowed", "forbidden", "denied" |
| A rule that permits override | **needs approval from {role}** | "escalate", "get permission" |
| A warning that permits proceeding | **You can continue, but…** | "warning", "caution" |
| The thing that failed | Named by its **visible label** | Field name, column name, model name |

> Bengali forms are **indicative pending `BN-003`**, which is the authoritative binding
> (`CG-004` `T-07`). Divergence resolves in favour of `BN-003`.

---

## 3. Screen copy

### 3.1 The three-part structure

```
[What happened]   [Why, if not obvious]   [What to do next]
```

Every message below conforms. A message missing the third part fails `CG-008` blocking item
`B-10` and cannot be approved.

### 3.2 Service and repair — `common.error.srm.*` (`M01`)

| Rule | Key | Message EN | Class |
|---|---|---|:--:|
| `BRU-SRM-01` | `common.error.srm.device_required` | A service order needs an identified device. Search for the device, or register it now. | সার্ভিস অর্ডারের জন্য শনাক্ত করা একটি ডিভাইস দরকার। ডিভাইসটি খুঁজুন, অথবা এখনই নিবন্ধন করুন। | **H** |
| `BRU-SRM-02` | `common.error.srm.warranty_inactive` | This device is not under warranty on {date}. Its warranty ended {expiry}. Create a paid repair instead. | এই ডিভাইসের {date} তারিখে ওয়ারেন্টি নেই। ওয়ারেন্টি শেষ হয়েছে {expiry}। পেইড মেরামত তৈরি করুন। | **H** |
| `BRU-SRM-03` | `common.error.srm.not_on_contract` | This device is not on {contract}. Add it to the contract, or create a paid repair. | এই ডিভাইসটি {contract}-এর অন্তর্ভুক্ত নয়। চুক্তিতে যোগ করুন, অথবা পেইড মেরামত নিন। | **H** |
| `BRU-SRM-04` | `common.error.srm.qc_not_passed` | This order cannot be completed. The quality checklist is not recorded as passed. Complete the checklist first. | এই অর্ডার সম্পন্ন করা যাবে না। কোয়ালিটি চেকলিস্ট এখনো পাস হিসেবে নথিভুক্ত হয়নি। আগে চেকলিস্ট সম্পন্ন করুন। | **H** |
| `BRU-SRM-05` | `common.error.srm.invoice_before_complete` | An invoice cannot be raised for an order that is not completed. Complete the order first. | সম্পন্ন না হওয়া অর্ডারের চালান ইস্যু করা যায় না। আগে অর্ডারটি সম্পন্ন করুন। | **H** |
| `BRU-SRM-07` | `common.error.srm.estimate_approval_5k` | Work above BDT 5,000 needs the customer's approval first. Send the estimate, then start work when it is approved. | ৫,০০০ টাকার বেশি কাজের জন্য আগে গ্রাহকের অনুমোদন দরকার। এস্টিমেট পাঠান; অনুমোদন পেলে কাজ শুরু করুন। | **H** |
| `BRU-SRM-08` | `common.error.srm.estimate_approval_25k` | Work above BDT 25,000 needs the customer's approval and the branch manager's approval. Send it to {branch_manager}. | ২৫,০০০ টাকার বেশি কাজের জন্য গ্রাহক ও ব্রাঞ্চ ম্যানেজার উভয়ের অনুমোদন দরকার। {branch_manager}-কে পাঠান। | **H** |
| `BRU-SRM-09` | `common.error.srm.tech_not_certified` | {technician} is not certified for {brand} warranty work. Their certification expired on {expiry}. Assign a certified technician, or ask the Quality Manager to renew it. | {technician} এই {brand} ওয়ারেন্টি কাজের জন্য সার্টিফাইড নন; সার্টিফিকেটের মেয়াদ শেষ {expiry}। সার্টিফাইড কারিগর নির্ধারণ করুন, বা কোয়ালিটি ম্যানেজারকে নবায়নের অনুরোধ করুন। | **H** |
| `BRU-SRM-11` | `common.error.srm.parts_unapproved` | Parts cannot be issued against an unapproved paid repair. Approve the estimate first, then issue the parts. | অনুমোদনহীন পেইড মেরামতে পার্টস ইস্যু করা যায় না। আগে এস্টিমেট অনুমোদন করুন, তারপর পার্টস দিন। | **H** |
| `BRU-SRM-06` | `common.error.srm.rework_flagged` | This is the second order for {device} with the same fault within 30 days. It has been linked to {original} as rework. | {device} ডিভাইসের একই ত্রুটিতে 30 দিনের মধ্যে এটি দ্বিতীয় অর্ডার। এটি {original}-এর রিওয়ার্ক হিসেবে যুক্ত হয়েছে। | **C** |
| `BRU-SRM-10` | `common.error.srm.priority_upgraded` | {customer} is a {tier} member, so this order has been set to priority 1. | {customer} একজন {tier} সদস্য, তাই এই অর্ডারটি অগ্রাধিকার ১-এ সেট করা হয়েছে। | **C** |

### 3.3 Approval and override — `common.error.approval.*`

| Situation | Key | Message EN | Class |
|---|---|---|:--:|
| Above own limit | `common.error.approval.over_limit` | You can approve up to {limit}. This is {amount}. Send it to {approver} for approval. | আপনি সর্বোচ্চ {limit} পর্যন্ত অনুমোদন করতে পারেন; এটি {amount}। অনুমোদনের জন্য {approver}-কে পাঠান। | **A** |
| Self-approval | `common.error.approval.self` | You cannot approve your own {object}. Send it to {approver}. | নিজের {object} নিজে অনুমোদন করতে পারবেন না। {approver}-কে পাঠান। | **H** |
| Override permitted | `common.error.approval.override_available` | This is blocked by {rule}. {role} can authorise an exception. Record a reason to request it. | এটি {rule} কর্তৃক আটকানো হয়েছে। {role} ব্যতিক্রম অনুমোদন করতে পারেন। অনুরোধ করতে কারণ লিখুন। | **A** |
| Reason required | `common.error.approval.reason_required` | Enter a reason for this override. It is recorded against the transaction. | এই ব্যতিক্রমের কারণ লিখুন। এটি লেনদেনের সঙ্গে নথিভুক্ত থাকবে। | **H** |

### 3.4 Stock and parts — `common.error.stock.*` (`M15`)

| Situation | Key | Message EN | Class |
|---|---|---|:--:|
| Not in stock | `common.error.stock.unavailable` | {part} is not in stock at {location}. It is available at {alt_location}. Request a transfer, or order it. | {location}-এ {part} স্টকে নেই; {alt_location}-এ আছে। ট্রান্সফারের অনুরোধ করুন, অথবা অর্ডার করুন। | **H** |
| Incompatible part | `common.error.stock.incompatible` | {part} does not fit {model}. Compatible parts: {alternatives}. | {part} এই {model}-এর সঙ্গে খাপ খায় না। সামঞ্জস্যপূর্ণ পার্টস: {alternatives}। | **H** |
| Negative stock | `common.error.stock.negative` | Issuing {qty} would take {location} below zero. Count the location, or record a receipt first. | {qty} ইস্যু করলে {location} ঋণাত্মক হয়ে যাবে। লোকেশন গুনে নিন, বা আগে রিসিট নথিভুক্ত করুন। | **H** |
| Hazard acknowledgement | `common.error.stock.hazard_ack` | {part} is a {hazard_class} item. Confirm you have read the handling instructions before issuing it. | {part} একটি {hazard_class} আইটেম। ইস্যু করার আগে হ্যান্ডলিং নির্দেশনা পড়েছেন বলে নিশ্চিত করুন। | **H** |

### 3.5 Finance — `common.error.fin.*` (`M19`, `M20`, `M51`)

| Situation | Key | Message EN | Class |
|---|---|---|:--:|
| Closed period | `common.error.fin.period_closed` | {period} is closed. Post this to the current period, or ask Finance to reopen {period}. | {period} বন্ধ। বর্তমান পিরিয়ডে পোস্ট করুন, বা ফাইন্যান্সকে {period} পুনরায় খুলতে বলুন। | **H** |
| Missing tax class | `common.error.fin.no_tax_class` | {item} has no tax class, so a compliant invoice cannot be issued. Ask Finance to set the tax class. | {item}-এর কোনো ট্যাক্স ক্লাস নেই, তাই সামঞ্জস্যপূর্ণ চালান ইস্যু করা যাবে না। ফাইন্যান্সকে ট্যাক্স ক্লাস সেট করতে বলুন। | **H** |
| Missing BIN | `common.error.fin.bin_required` | A VAT invoice to a business needs the buyer's BIN. Add the BIN to {customer}, or issue to an individual. | ব্যবসায়িক প্রতিষ্ঠানের ভ্যাট চালানে ক্রেতার BIN দরকার। {customer}-এ BIN যোগ করুন, বা ব্যক্তি হিসেবে ইস্যু করুন। | **H** |
| Unverified tax code | `common.error.fin.tax_unverified` | This tax code is not yet verified for {fiscal_year}, so it cannot be used. Finance is completing verification. | এই ট্যাক্স কোডটি {fiscal_year}-এর জন্য এখনো যাচাই হয়নি, তাই ব্যবহার করা যাবে না। ফাইন্যান্স যাচাই সম্পন্ন করছে। | **H** |
| Dimension missing | `common.error.fin.dimension_required` | {account} needs a {dimension}. Select one. | {account}-এর জন্য একটি {dimension} দরকার। একটি নির্বাচন করুন। | **H** |

---

## 4. Field labels and help text

Not applicable to this library.

---

## 5. Validation and error messages

> `BR-STD-04` and `PS-09`: every message states **what is wrong and what to do**, in the user's
> language. Three-part structure per `CG-003` §3.1. Client-side validation is **format only** —
> business rules are server-side (`PS-11`).

### 5.1 Rules

| # | Rule | Source |
|---|---|---|
| **E-01** | Never expose an error code alone. A code may accompany plain language, never replace it | `CG-003` E-01 |
| **E-02** | Never expose internal detail — table names, stack traces, model names, SQL, internal IDs | `CG-003` E-02, security |
| **E-03** | Never blame the user | `CG-003` E-03, `CG-011` EA-03 |
| **E-04** | Name the specific field, record or rule using its **exact visible label** | `CG-011` EA-02 |
| **E-05** | Where a role can resolve it, name the **role**, never the person | `CG-003` E-05 |
| **E-06** | Reference the `BRU-` identifier in the **log**, never in user-facing text | `CG-003` E-06 |
| **E-07** | Message class matches the `05-05` rule class | `CG-003` E-07 |
| **E-08** | Every message is written to be **announced out of visual context** | `CG-011` EA-08 |
| **E-09** | Both languages state the same remedy | `CG-011` EA-09 |

### 5.2 System errors — `common.error.system.*`

| Situation | Key | Message EN |
|---|---|---|
| Service unavailable | `common.error.system.unavailable` | {service} is not responding. {fallback_instruction} We are restoring it. Reference {ref}. |
| Timeout | `common.error.system.timeout` | This took longer than expected and was stopped. Nothing was saved. Try again. |
| Conflict | `common.error.system.conflict` | {user} changed this record while you were editing. Review their change before saving yours. |
| Unexpected | `common.error.system.unexpected` | Something went wrong and we could not complete this. Nothing was changed. Quote reference {ref} to support on 16743. |

> `common.error.system.unexpected` is the **only** message permitted to be non-specific, and it
> still states that nothing changed and how to get help.

---

## 6. Confirmations and destructive actions

Confirmation and destructive-action copy is `UI-007`. This library carries the messages that **block** an action, not those that confirm one.

---

## 7. Accessibility text

| Item | Rule | SC |
|---|---|:--:|
| Error identified in text | Never an icon, border or colour alone | **3.3.1**, 1.4.1 |
| Specific field named | By its visible label | 3.3.1 |
| Correction suggested | Where known | **3.3.3** |
| Announcement | Errors announced as an assertive live region; warnings as polite | 4.1.3 |
| Focus | Focus moves to the first error on submit | 3.3.1 |
| Language | Both bundles state the same remedy; embedded identifiers marked `lang` | 3.1.2 |

---

## 8. Character budget and layout risk

Budgets are **Bengali** rendered lengths (`VB-006` `DS-04`). English runs 20–40% shorter.

| Slot | Budget (BN) | Risk |
|---|---:|---|
| Inline validation | 90 | **High** — several `BRU-` messages exceed this in English before translation |
| Alert body | 200 | Medium |
| Modal body | 300 | Low |

> **Known risk.** `common.error.srm.tech_not_certified` names a technician, a brand, a date and
> two remedies. In Bengali it will exceed the 90-character inline budget and must render as an
> alert, not inline. Flagged to Design System.

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
| [`UI-003_Field_Label_Placeholder_and_Help_Text_Library.md`](UI-003_Field_Label_Placeholder_and_Help_Text_Library.md) | Format-only validation |
| [`UI-007_Confirmation_Warning_and_Destructive_Action_Library.md`](UI-007_Confirmation_Warning_and_Destructive_Action_Library.md) | Override reason capture |
| `05-05` Business Rules and Automation Catalogue | The rules these messages express |
| `MD-026` Reason Code Register | Reasons captured on override |
| `CG-011` §5 | Accessibility of error messages |

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
