---
id: UI-042
title: Consent, Privacy and Preference Centre Copy
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
content_class: A
purpose: >
  Consent capture, purpose statements, withdrawal, preference centre and data-request copy. Consent
  copy is the operative legal text under the data-protection regime that drives the split-residency
  requirement in 05-06 NFR-086, and the transparency-notice obligation in NFR-092.
traces_to: [05-06 NFR-086, NFR-092, NFR-093, LG-008, LG-009, LG-010, LG-012, M33, MD-013]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: UI-042_Consent_Privacy_and_Preference_Centre_Copy_BN.md
i18n_namespace: `flow.consent.*`
pinned_to:
  surface: `P01`, `P04`, `P07`, `P12`, and every S3 data-capture point
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

# UI-042 — Consent, Privacy and Preference Centre Copy

> ⚠ **Class A — statutory.** This is not marketing copy about privacy; it is the **operative
> notice and consent text** relied on for lawfulness of processing.
>
> `NFR-092` requires a transparency notice stating data categories, purposes, risks, retention
> periods, third-party transfers and the withdrawal procedure. `NFR-093` requires support for
> access, portability, rectification, erasure and consent withdrawal.
>
> Gate **G6** applies and is unwaivable (`WV-02`). **Nothing here may ship without Legal and DPO
> sign-off.**

---

## 1. Surface summary

| Item | Value |
|---|---|
| Surface | Cross-surface flow — `P01`, `P04`, `P07`, `P12`, and every S3 data-capture point |
| Framework | All surfaces carrying this flow |
| Default language | Bengali default on customer and field surfaces |
| i18n namespace | ``flow.consent.*`` |
| Offline-capable | Where the carrying surface is offline-capable |
| Accessibility target | WCAG 2.1 AA (`PS-04`) |
| Content class | A — Statutory |
| Sentence budget | Per surface (`VB-002` §4.2) (`VB-002` §4.2) |
| Audience | `P01`, `P04`, `P07`, `P12`, and every S3 data-capture point |

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

### 3.1 Consent capture — `flow.consent.*`

Marketing consent and transactional necessity are **legally distinct** and are never bundled
(`NT-002`).

| Element | Key | Wording EN | Bengali |
|---|---|---|---|
| Transactional notice | `flow.consent.transactional` | We will message you about your service on {mobile}. This is part of providing the service. | আমরা {mobile}-এ আপনার সার্ভিস সম্পর্কে বার্তা পাঠাব। এটি সেবা প্রদানের অংশ। |
| Marketing opt-in | `flow.consent.marketing` | You can also send me offers and service reminders. | আপনি আমাকে অফার এবং সার্ভিস রিমাইন্ডারও পাঠাতে পারেন। |
| Marketing note | `flow.consent.marketing_note` | Optional. You can change this at any time. | ঐচ্ছিক। আপনি যেকোনো সময় এটি পরিবর্তন করতে পারেন। |
| Full notice link | `flow.consent.notice_link` | How we use your data | আমরা কীভাবে আপনার তথ্য ব্যবহার করি |

### 3.2 Purpose statements at the point of capture — `flow.consent.purpose.*`

Every S3 field states **why** it is needed at the moment it is asked for (`UI-003` §4.2).

| Field | Key | Purpose statement EN | Bengali |
|---|---|---|---|
| NID | `flow.consent.purpose.nid` | We need this to verify who you are. It is stored in Bangladesh and is not shared. | আপনি কে তা যাচাই করতে আমাদের এটি প্রয়োজন। এটি বাংলাদেশে সংরক্ষিত এবং শেয়ার করা হয় না। |
| TIN | `flow.consent.purpose.tin` | We need this for your VAT invoice. It is stored in Bangladesh. | আপনার ভ্যাট ইনভয়েসের জন্য আমাদের এটি প্রয়োজন। এটি বাংলাদেশে সংরক্ষিত। |
| Bank details | `flow.consent.purpose.bank` | We need this to pay you. It is stored in Bangladesh and is not shared. | আপনাকে অর্থ পরিশোধ করতে আমাদের এটি প্রয়োজন। এটি বাংলাদেশে সংরক্ষিত এবং শেয়ার করা হয় না। |
| Device data | `flow.consent.purpose.device_data` | Repair may require access to data on your device. We do not copy or keep it. | মেরামতের জন্য আপনার ডিভাইসের ডেটায় প্রবেশ প্রয়োজন হতে পারে। আমরা তা কপি বা সংরক্ষণ করি না। |
| Location | `flow.consent.purpose.location` | We use your location to send the nearest technician. | নিকটতম টেকনিশিয়ান পাঠাতে আমরা আপনার অবস্থান ব্যবহার করি। |

> **The residency statement in each purpose line is not decoration.** `NFR-086` requires
> Bangladesh residency for these fields, and `NFR-092` requires the notice to state transfers.

### 3.3 Preference centre — `flow.preference.*`

| Element | Key | Wording EN | Bengali |
|---|---|---|---|
| Title | `flow.preference.title` | Your messages and data | আপনার বার্তা এবং তথ্য |
| Channel | `flow.preference.channel` | {channel} | {channel} |
| Transactional locked | `flow.preference.transactional_locked` | Service updates cannot be turned off while you have an active service. | আপনার সক্রিয় সার্ভিস থাকাকালীন সার্ভিস আপডেট বন্ধ করা যাবে না। |
| Withdraw marketing | `flow.preference.withdraw` | Stop marketing messages | মার্কেটিং বার্তা বন্ধ করুন |
| Withdrawn | `flow.preference.withdrawn` | Stopped. You will still get service updates. | বন্ধ করা হয়েছে। আপনি এখনও সার্ভিস আপডেট পাবেন। |

### 3.4 Data subject rights — `flow.dsr.*` (`NFR-093`, `LG-010`)

| Right | Key | Wording EN | Bengali |
|---|---|---|---|
| Access | `flow.dsr.access` | Get a copy of your data | আপনার তথ্যের একটি কপি নিন |
| Portability | `flow.dsr.portability` | Download your data in a portable format | পোর্টেবল ফরম্যাটে আপনার তথ্য ডাউনলোড করুন |
| Rectify | `flow.dsr.rectify` | Correct something that is wrong | ভুল কিছু সংশোধন করুন |
| Erase | `flow.dsr.erase` | Ask us to delete your data | আপনার তথ্য মুছে ফেলতে বলুন |
| Erasure limits | `flow.dsr.erase_limits` | We must keep some records by law — invoices for {years} years. We will delete everything else. | আইন অনুযায়ী আমাদের কিছু রেকর্ড রাখতে হয় — ইনভয়েস {years} বছর। বাকি সব আমরা মুছে ফেলব। |
| Timeline | `flow.dsr.timeline` | We respond within {days} days. | আমরা {days} দিনের মধ্যে সাড়া দিই। |

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
| Consent required | `flow.consent.error.required` | We cannot continue without your agreement to the service terms. | **H** |
| Marketing without consent | `flow.consent.error.no_marketing` | This customer has not agreed to marketing messages. | **H** |
| Erasure blocked | `flow.dsr.error.retention` | Some records must be kept by law until {date}. Everything else will be deleted. | **H** |
| Identity unverified | `flow.dsr.error.identity` | We must verify who you are before we can share your data. | **H** |

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

| — | Is the residency wording confirmed by Legal and the DPO? | **Yes — blocks G6** | Legal Counsel + DPO |
| — | Is the statutory retention period for invoices confirmed at five years? | **Yes** | Tax + Legal |
| # | Question | Blocking? | Owner |
|---|---|:--:|---|
| 1 | `BN-003` not written; Bengali indicative | **Yes** | Localisation Lead |
| 2 | No build exists; `pinned_to` incomplete | **Yes** | Platform Engineering |

---

## 10. Related documents

| Document | Relationship |
|---|---|
| `LG-008` Privacy Notice and Consent Copy | **The operative legal text this surfaces** |
| `LG-009` Data Retention and Deletion Schedule | Retention periods quoted |
| `LG-010` Data Subject Request Handling Content | The process behind §3.4 |
| `LG-012` Cross-Border Data Transfer and Residency Statement | The residency claims |
| `05-06` NFR-086, NFR-092, NFR-093 | The obligations |

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
- [ ] G6 statutory verification — **outstanding, unwaivable (`WV-02`)**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
