---
id: NT-015
title: Push Notification Library — P01 Customer App
project: 1000FiX ERP System v2.0
content_type: Notification template library
template: TPL_Notification_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design Lead
author: Content Design
reviewers: [Localisation Lead, Platform Engineering, Accessibility reviewer, owning business function]
approver: Content Design Lead
content_class: D
purpose: >
  Push copy for every customer-relevant event, with deep links and Bengali versions. Push has a hard
  character budget and one chance; poorly written push drives permission revocation, after which the
  channel is gone for that customer.
traces_to: [`M27`, NT-001, NT-003, UI-009, P01]
priority: P2
wave: W6
bilingual: yes
bn_counterpart: NT-015_Push_Notification_Library_P01_Customer_App_BN.md
channels: [Push]
consent_class: Transactional
sources:
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M27_Omnichannel_Contact_Centre_and_Communications.md
    verified: 2026-08-15
    class: P1
  - source: project_content/04_Notification_and_Messaging/NT-001 event-channel matrix
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# NT-015 — Push Notification Library — P01 Customer App

> **Permission revocation is permanent in practice.** A customer who turns push off rarely turns
> it back on. Every push must be worth the interruption.

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | Push |
| Audience | Customers with the app installed |
| Owning module | `M27`, `P01` |
| Consent class | Transactional |
| Quiet-hours exempt | Exempt for transactional; content push respects `NT-003` |
| Content class | D — User-facing |
| Bengali required | **Yes** — see `BN-014` |
| Bangladesh routing | Device push, not SMS |

---

## 2. Templates

| # | Event | Key | Title EN | Body EN | Title BN | Deep link |
|---|---|---|---|---|---|---|
| 1 | Technician on the way | `push.p01.on_way` | {tech} is on the way | About {minutes} minutes. Tap to track. | {tech} আসছেন | Order tracking |
| 2 | Estimate ready | `push.p01.estimate` | Your estimate is ready | {amount}. Approve so we can start. | আপনার এস্টিমেট প্রস্তুত | Estimate approval |
| 3 | Ready for collection | `push.p01.ready` | Your {device} is ready | Collect from {branch}, open {hours}. | আপনার {device} প্রস্তুত | Order detail |
| 4 | Out for delivery | `push.p01.delivery` | On the way to you | Your {device} arrives today. | আপনার কাছে আসছে | Order tracking |
| 5 | Payment received | `push.p01.paid` | Payment received | {amount}. Receipt in your inbox. | পেমেন্ট গৃহীত | Receipt |
| 6 | Service complete | `push.p01.complete` | Service complete | {months} months repair warranty. | সার্ভিস সম্পন্ন | Order detail |
| 7 | Delayed | `push.p01.delayed` | Running late | New date {date}. Sorry for the wait. | দেরি হচ্ছে | Order detail |
| 8 | Contract expiring | `push.p01.contract` | Your contract ends {date} | Renew to keep your cover. | আপনার চুক্তি {date}-এ শেষ | Contract |

---

## 3. Channel-specific requirements

| Requirement | Rule |
|---|---|
| Title budget | 40 characters Bengali; body 120 |
| Deep link | Every push opens the exact record, never the home screen |
| Permission | Push requires device permission plus `NT-002` preference |
| Silent push | Background sync only, never content (`NT-003` §3) |
| Grouping | Multiple pushes for one object collapse into one (`NT-003` BA-01) |
| Language | From `fix.party.preferred_language`, defaulting to Bengali |
| Fallback | SMS where the event is `CH-04` action-required (`NT-001` §2.2) |

---

## 4. Failure and fallback

| Failure | Behaviour | Reference |
|---|---|---|
| Undeliverable | Retry once, then fall back per the `NT-001` matrix | `NT-025` |
| Provider down | Secondary provider; if both fail, raise an operational task | `IP-09`, `OP-014` |
| Suppressed by policy | Logged as suppressed, not failed | `NT-003` |
| All channels exhausted | Becomes a human task; never silently dropped | `NT-001` §4 |

---

## 5. Change log and governance

| Item | Value |
|---|---|
| Who may add a template | Content Design with the owning business owner |
| Who may change wording | Content Design Lead; Legal where class A or B |
| Version and approval | Recorded in `NT-026` |
| Review | Per wave |

---

## 6. Related documents

| Document | Relationship |
|---|---|
| [`../NT-001_Notification_Strategy_and_Event_Channel_Matrix.md`](../NT-001_Notification_Strategy_and_Event_Channel_Matrix.md) | Channel assignment |
| [`../04A_SMS_and_OTP/NT-005_SMS_Template_Library_Technician_and_Field.md`](../04A_SMS_and_OTP/NT-005_SMS_Template_Library_Technician_and_Field.md) | The SMS fallback |
| `P01` | The consuming surface |

---

## 7. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Content Design Lead (pending) |

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
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
