---
id: NT-004
title: SMS Template Library — Customer
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
  Booking, assignment, arrival, estimate, completion, ready-for-collection, delivery and feedback SMS,
  bilingual, with character-count and segment-cost analysis. SMS remains the highest-reach channel in
  Bangladesh; Bengali segments at 70 characters, so an unmanaged library triples send cost.
traces_to: [M01, M27, NT-001, NT-003, MD-027, CG-010 BC-05, BN-014]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: NT-004_SMS_Template_Library_Customer_BN.md
channels: [SMS]
consent_class: Transactional and service-related
sources:
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M27_Omnichannel_Contact_Centre_and_Communications.md
    verified: 2026-08-15
    class: P1
  - source: project_content/04_Notification_and_Messaging/NT-001 event-channel matrix
    verified: 2026-08-15
    class: P1
  - source: Bangladesh A2P SMS practice — masking (alphanumeric brand sender) carries transactional and OTP traffic; non-masking (numeric) carries promotional. Misclassification is a common cause of route suspension
    verified: 2026-08-15
    class: P3
supersedes: none
review_due: 2027-02-15
---

# NT-004 — SMS Template Library — Customer

> **The highest-volume content in the programme.** At 250,000+ customers a month with several
> messages each, this library is sent millions of times a year.
>
> Two consequences: every character costs money, and every wording error is repeated at scale.
> Status wording is quoted from the `MD-027` **customer-facing** column — never the internal state
> key (`T-06`).

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | SMS |
| Audience | Individual customers (250,000+/month) |
| Owning module | `M01`, `M27` |
| Consent class | Transactional and service-related |
| Quiet-hours exempt | Transactional exempt; service-related held to 08:00–21:00 |
| Content class | D — User-facing |
| Bengali required | **Yes** — see `BN-014` |
| Bangladesh routing | **Masking** (alphanumeric `1000FiX`) |

---

## 2. Templates

### 2.1 Template set

Segment counts: **EN** = GSM-7 at 160 characters; **BN** = UCS-2 at 70 characters.

| # | Event | Template ID | English | Bengali | EN seg | BN seg |
|---|---|---|---|---|:--:|:--:|
| 1 | Booking received | `sms.cust.booked` | 1000FiX: Booking received. Ref {ref}. We will contact you before {time}. | 1000FiX: বুকিং গৃহীত। রেফ {ref}। আমরা {time}-এর আগে যোগাযোগ করব। | 1 | 1 |
| 2 | Technician assigned | `sms.cust.assigned` | 1000FiX: {tech} will visit you on {date} between {from}–{to}. Ref {ref}. | 1000FiX: {date} তারিখে {from}–{to} সময়ে {tech} আসবেন। রেফ {ref}। | 1 | 2 |
| 3 | On the way | `sms.cust.on_way` | 1000FiX: {tech} is on the way. About {minutes} minutes. | 1000FiX: {tech} আসছেন। প্রায় {minutes} মিনিট। | 1 | 1 |
| 4 | Device received | `sms.cust.received` | 1000FiX: We have your {device}. Ref {ref}. Track at {link}. | 1000FiX: আপনার {device} আমরা পেয়েছি। রেফ {ref}। ট্র্যাক করুন {link}। | 1 | 2 |
| 5 | Estimate ready | `sms.cust.estimate` | 1000FiX: Your repair estimate is {amount}. Approve at {link} so we can start. Ref {ref}. | 1000FiX: আপনার মেরামতের এস্টিমেট {amount}। শুরু করতে {link}-এ অনুমোদন দিন। রেফ {ref}। | 1 | 2 |
| 6 | Estimate approved | `sms.cust.approved` | 1000FiX: Thank you. We have started work on your {device}. Ref {ref}. | 1000FiX: ধন্যবাদ। আপনার {device}-এর কাজ শুরু করেছি। রেফ {ref}। | 1 | 2 |
| 7 | Awaiting part | `sms.cust.awaiting_part` | 1000FiX: We are waiting for a part for your {device}. Expected {date}. Ref {ref}. | 1000FiX: আপনার {device}-এর একটি পার্টসের অপেক্ষায় আছি। প্রত্যাশিত {date}। রেফ {ref}। | 1 | 2 |
| 8 | Ready for collection | `sms.cust.ready` | 1000FiX: Your {device} is ready. Collect from {branch}, {hours}. Ref {ref}. | 1000FiX: আপনার {device} প্রস্তুত। {branch} থেকে সংগ্রহ করুন, {hours}। রেফ {ref}। | 1 | 2 |
| 9 | Out for delivery | `sms.cust.out_delivery` | 1000FiX: Your {device} is out for delivery today. Ref {ref}. | 1000FiX: আপনার {device} আজ ডেলিভারির পথে। রেফ {ref}। | 1 | 2 |
| 10 | Delivered | `sms.cust.delivered` | 1000FiX: Delivered. Thank you for choosing 1000FiX. Ref {ref}. | 1000FiX: পৌঁছে দেওয়া হয়েছে। 1000FiX বেছে নেওয়ার জন্য ধন্যবাদ। রেফ {ref}। | 1 | 2 |
| 11 | Completed | `sms.cust.completed` | 1000FiX: Service complete. Repair warranty {months} months. Ref {ref}. | 1000FiX: সার্ভিস সম্পন্ন। মেরামত ওয়ারেন্টি {months} মাস। রেফ {ref}। | 1 | 2 |
| 12 | Delayed | `sms.cust.delayed` | 1000FiX: Your repair is taking longer than planned. New date {date}. Sorry for the wait. Ref {ref}. | 1000FiX: আপনার মেরামত পরিকল্পনার চেয়ে বেশি সময় নিচ্ছে। নতুন তারিখ {date}। রেফ {ref}। | 1 | 3 |
| 13 | Cancelled | `sms.cust.cancelled` | 1000FiX: Order {ref} cancelled. Any payment will be refunded within {days} days. | 1000FiX: অর্ডার {ref} বাতিল। কোনো পেমেন্ট {days} দিনের মধ্যে ফেরত দেওয়া হবে। | 1 | 2 |
| 14 | Payment received | `sms.cust.paid` | 1000FiX: {amount} received. Thank you. Ref {ref}. | 1000FiX: {amount} গৃহীত। ধন্যবাদ। রেফ {ref}। | 1 | 1 |
| 15 | Uncollected reminder | `sms.cust.uncollected` | 1000FiX: Your {device} has been ready since {date}. Please collect from {branch}. Ref {ref}. | 1000FiX: {date} থেকে আপনার {device} প্রস্তুত আছে। {branch} থেকে সংগ্রহ করুন। রেফ {ref}। | 1 | 3 |

### 2.2 Variables

| Variable | Source field | Example |
|---|---|---|
| `{ref}` | `fix.service.order.name` | SR-2026-114882 |
| `{device}` | `MD-021` display name | ল্যাপটপ |
| `{tech}` | `fix.technician_profile.name` | করিম হোসেন |
| `{branch}` | `MD-003` `name_bn` | আগ্রাবাদ সার্ভিস সেন্টার |
| `{amount}` | Monetary, `BN-007` format | ৳ ৩,২০০.০০ |
| `{link}` | Shortened tracking link | fix.bd/t/xxxx |

### 2.3 Cost observation

**Nine of the fifteen Bengali templates run to two segments and one to three.** The library
averages **1.9 Bengali segments against 1.0 English**, so Bengali SMS costs roughly **1.9×** the
English equivalent at the same volume.

That is the correct trade — `PS-03` makes Bengali the default and the reach is the point — but it
must be budgeted rather than discovered. `CG-014` tracks it; `NT-026` records any wording change
that moves a template across a segment boundary.

### 2.4 Rules

| # | Rule |
|---|---|
| **CS-01** | Every message opens with `1000FiX:` so the sender is identifiable even where masking is stripped |
| **CS-02** | Every message carries `{ref}` — it is what the customer quotes on the hotline |
| **CS-03** | **No promotional content in any template here** (`NT-001` BD-03). One promotional line reclassifies the whole message |
| **CS-04** | Status wording comes from `MD-027` customer-facing labels. `sms.cust.delayed` never says "SLA breached" |
| **CS-05** | Links never carry the only copy of the information |
| **CS-06** | A wording change that moves a template to a higher segment count requires Content Design Lead approval |

---

## 3. Channel-specific requirements

| Requirement | Rule |
|---|---|
| Encoding | Bengali is **UCS-2 and segments at 70 characters**, not 160 (`CG-010` BC-05). English GSM-7 segments at 160 |
| Segment count | Recorded per template for **both** languages (`CG-008` NT-e) |
| Sender | Masking (alphanumeric `1000FiX`) for transactional and security; non-masking for promotional (`NT-001` §3.1) |
| DND | Transactional and security deliver to DND numbers; promotional does not |
| Links | Shortened, branded, and never the only route to the information |
| No emoji | Emoji inflate UCS-2 segments and render inconsistently on feature phones |
| Language | From `fix.party.preferred_language`, defaulting to Bengali (`MD-013`) |

---

## 4. Failure and fallback

| Failure | Behaviour | Reference |
|---|---|---|
| Undeliverable | Retry once after 5 minutes, then fall back per the `NT-001` matrix | `NT-025` |
| Gateway down | Secondary gateway; if both fail, raise an operational task | `IP-09`, `OP-014` |
| Number invalid | Flag on the party record; notify the owning function | `NT-025` |
| Suppressed by policy | Logged as suppressed, not as failed | `NT-003` |

---

## 5. Change log and governance

| Item | Value |
|---|---|
| Who may add a template | Content Design with the owning module business owner |
| Who may change wording | Content Design Lead; Legal where the class is A or B |
| Version and approval | Recorded in `NT-026` |
| Review | Per wave; immediately on a rule or rate change |

---

## 6. Related documents

| Document | Relationship |
|---|---|
| [`../NT-001_Notification_Strategy_and_Event_Channel_Matrix.md`](../NT-001_Notification_Strategy_and_Event_Channel_Matrix.md) | Which events send SMS |
| [`../NT-003_Quiet_Hours_Throttling_and_Frequency_Policy.md`](../NT-003_Quiet_Hours_Throttling_and_Frequency_Policy.md) | Windows and caps |
| `MD-027` Status Register | Customer-facing status wording |
| `BN-014` Bengali Notification and SMS Pack | The Bengali counterpart |

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
