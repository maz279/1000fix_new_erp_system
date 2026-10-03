---
id: NT-002
title: Notification Preference and Consent Copy
project: 1000FiX ERP System v2.0
content_type: Notification template library
template: TPL_Notification_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance with Content Design
author: Content Design with Legal and the DPO
reviewers: [Legal Counsel, DPO, Localisation Lead, Marketing, Platform Engineering]
approver: Legal Counsel
content_class: A
purpose: >
  Opt-in and opt-out copy per channel and event class, the marketing-versus-transactional
  distinction, and consent records. Marketing consent and transactional necessity are legally
  distinct; conflating them exposes the company under the data-protection regime and puts the
  Bangladesh masking SMS route at risk.
traces_to: [05-06 NFR-092, NFR-093, LG-008, LG-010, M33, UI-042, NT-001, NT-003]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: NT-002_Notification_Preference_and_Consent_Copy_BN.md
channels: [SMS, WhatsApp, email, push, in-app]
consent_class: **Defines the classes**
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-092 transparency notice and NFR-093 data-subject rights including withdrawal of consent through a simplified procedure
    verified: 2026-08-15
    class: P1
  - source: Bangladesh A2P SMS practice — masking (alphanumeric brand sender) carries transactional and OTP traffic; non-masking (numeric sender) carries promotional. Misclassification between the two is a common cause of route suspension. All traffic routes through BTRC-listed aggregators
    verified: 2026-08-15
    class: P3
  - source: BTRC Do Not Disturb service — promotional SMS may not be sent to DND-registered numbers and is time-restricted; transactional SMS is exempt and delivers 24/7
    verified: 2026-08-15
    class: P3
supersedes: none
review_due: 2027-02-15
---

# NT-002 — Notification Preference and Consent Copy

> ⚠ **Class A — statutory.** This is the operative consent text, not marketing copy about
> consent. Gate **G6** applies and is unwaivable (`WV-02`).
>
> **Two distinctions, both legally load-bearing:**
> 1. **Transactional** messages are part of delivering the service the customer asked for.
> 2. **Marketing** messages require consent, can be withdrawn, and — in Bangladesh — must travel
>    a different SMS route (`NT-001` §3.1).
>
> Bundling them is simultaneously a data-protection failure and a route-suspension risk.

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | SMS, WhatsApp, email, push, in-app |
| Audience | All external audiences |
| Owning module | `M33` |
| Consent class | **Defines the classes** |
| Quiet-hours exempt | Consent copy itself is not sent |
| Content class | A — Statutory |
| Bengali required | **Yes** — see `BN-014` |
| Bangladesh routing | Determines masking vs non-masking |

---

## 2. Templates

### 2.1 The consent classes

| Class | Definition | Consent needed | SMS route | DND |
|---|---|---|---|---|
| **Transactional** | Necessary to deliver the service the customer requested | No — necessity | Masking | Delivers |
| **Service-related** | Not strictly necessary but directly about their service — feedback, collection reminder | No, but suppressible by preference | Masking | Delivers |
| **Marketing** | Promotes a product or service the customer has not asked for | **Yes — explicit** | Non-masking | Blocked |
| **Security** | OTP, sign-in alerts, account changes | No — always sent | Masking | Delivers |

> **Security messages cannot be switched off.** That is stated to the customer, not hidden.

### 2.2 Consent capture copy — `flow.consent.*` (rendered by `UI-042`)

| Element | Key | English | Bengali |
|---|---|---|---|
| Transactional notice | `nt.consent.transactional` | We will message you about your service on {mobile}. This is part of providing the service. | আমরা {mobile}-এ আপনার সার্ভিস সম্পর্কে বার্তা পাঠাব। এটি সেবা প্রদানের অংশ। |
| Marketing opt-in | `nt.consent.marketing` | You can also send me offers and reminders. | আপনি আমাকে অফার এবং রিমাইন্ডারও পাঠাতে পারেন। |
| Optional note | `nt.consent.optional` | Optional. You can change this at any time. | ঐচ্ছিক। আপনি যেকোনো সময় এটি পরিবর্তন করতে পারেন। |
| Security note | `nt.consent.security` | Security messages are always sent. They cannot be turned off. | নিরাপত্তা বার্তা সবসময় পাঠানো হয়। এগুলি বন্ধ করা যায় না। |
| WhatsApp opt-in | `nt.consent.whatsapp` | You can also message me on WhatsApp. | আপনি আমাকে WhatsApp-এও বার্তা পাঠাতে পারেন। |

> **`nt.consent.marketing` is a separate, unticked control.** It is never pre-selected and never
> combined with the terms acceptance.

### 2.3 Preference centre — `nt.preference.*`

| Element | Key | English | Bengali |
|---|---|---|---|
| Title | `nt.preference.title` | Your messages | আপনার বার্তা |
| Per-channel | `nt.preference.channel` | {channel} | {channel} |
| Transactional locked | `nt.preference.locked` | Service updates cannot be turned off while you have an active service. | আপনার সক্রিয় সার্ভিস থাকাকালীন সার্ভিস আপডেট বন্ধ করা যাবে না। |
| Service-related toggle | `nt.preference.service_related` | Feedback requests and reminders | মতামতের অনুরোধ এবং রিমাইন্ডার |
| Marketing toggle | `nt.preference.marketing` | Offers and promotions | অফার এবং প্রচার |
| Save | `nt.preference.save` | Save preferences | পছন্দ সংরক্ষণ করুন |
| Saved | `nt.preference.saved` | Saved. Changes apply immediately. | সংরক্ষিত। পরিবর্তন এখনই কার্যকর হবে। |

### 2.4 Withdrawal — the simplified procedure (`NFR-093`)

| Element | Key | English | Bengali |
|---|---|---|---|
| SMS stop instruction | `nt.consent.stop_sms` | Reply STOP to stop offers. | অফার বন্ধ করতে STOP লিখে উত্তর দিন। |
| Stop confirmed | `nt.consent.stopped` | Stopped. You will still get service updates and security messages. | বন্ধ করা হয়েছে। আপনি এখনও সার্ভিস আপডেট এবং নিরাপত্তা বার্তা পাবেন। |
| Email unsubscribe | `nt.consent.unsub_email` | Stop these emails | এই ইমেইলগুলি বন্ধ করুন |
| Re-subscribe | `nt.consent.resub` | Start offers again | আবার অফার শুরু করুন |

| # | Rule |
|---|---|
| **CN-01** | Withdrawal is **one action**. STOP by reply, or one tap in the preference centre |
| **CN-02** | Withdrawal takes effect **immediately**, not at the next cycle |
| **CN-03** | Withdrawal confirmation always states **what continues** — service and security messages |
| **CN-04** | A withdrawal is never met with a retention offer |
| **CN-05** | Consent state, timestamp, channel and the wording version shown are all recorded (`LG-001`) |

---

## 3. Channel-specific requirements

| Channel | Consent requirement |
|---|---|
| SMS transactional | Necessity; masking route; delivers to DND |
| SMS marketing | **Explicit opt-in**; non-masking route; never to DND |
| WhatsApp | Opt-in required, plus Meta template category compliance (`NT-008`) |
| Email transactional | Necessity; **no unsubscribe link** — a payment receipt is not optional |
| Email marketing | Explicit opt-in; unsubscribe link mandatory |
| Push | Device permission plus preference |
| In-app | No consent needed; the user is in the product |

> `VB-005` §4 already fixes the footer rule: transactional email carries "manage preferences"
> and **no unsubscribe**.

---

## 4. Failure and fallback

| Situation | Behaviour |
|---|---|
| Consent state unknown | Treat as **not consented** for marketing; transactional proceeds |
| Preference save fails | Tell the user it did not save and that nothing changed. Never claim success |
| Withdrawal fails | Escalate immediately — a failed withdrawal is a compliance incident, not a bug |
| Consent record missing for a sent marketing message | Raise to the DPO; the message should not have been sent |

---

## 5. Change log and governance

| Item | Value |
|---|---|
| Version accepted by each user | Recorded in `LG-001` with date and wording version |
| Change requires | Legal Counsel and DPO approval; G6 verification |
| Re-consent on change | Required where the purpose changes; not where wording is clarified |
| Review | Annual, plus on any regulatory change (`CG-006` §4.2) |

---

## 6. Related documents

| Document | Relationship |
|---|---|
| `LG-008` Privacy Notice and Consent Copy | **The governing legal text** |
| `LG-010` Data Subject Request Handling Content | Withdrawal handling |
| [`../03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md) | The surface rendering this |
| [`NT-001_Notification_Strategy_and_Event_Channel_Matrix.md`](NT-001_Notification_Strategy_and_Event_Channel_Matrix.md) | Routes on these classes |
| `05-06` NFR-092, NFR-093 | The obligations |

---

## 7. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Legal Counsel (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:`, `traces_to:`, `channels:` and `consent_class:`
- [x] Conforms to `TPL_Notification_Template.md`
- [x] Every template names its trigger event, channel, audience and suppression rules (`CG-008` NT-a)
- [x] Every event exists in the `NT-001` channel matrix (`CG-008` NT-b)
- [x] Variables declared with their source field (`CG-008` NT-c)
- [x] Consent class stated — transactional or marketing (`CG-008` NT-d, `NT-002`)
- [x] Fallback defined for channel failure (`CG-008` NT-g, `IP-09`)
- [x] Quiet-hours and frequency treatment stated (`CG-008` NT-h, `NT-003`)
- [x] Status labels quoted from `MD-027` **customer-facing** column, never the internal state key (`T-06`)
- [x] All internal links resolve
- [ ] Bengali templates written and signed off **in context** (`BN-018`) — **outstanding; blocks `Approved`** (`CM-R6`)
- [ ] Bengali SMS segment count recorded — UCS-2 segments at **70 characters** (`CG-008` NT-e, `CG-010` BC-05)
- [ ] G6 statutory verification — **outstanding, unwaivable (`WV-02`)**
- [ ] Meta template category, submission and approval status recorded (`CG-008` NT-f)
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
