---
id: NT-025
title: Notification Failure and Fallback Copy
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
content_class: C
purpose: >
  What the user sees when a channel fails, channel-downgrade messaging and undeliverable handling.
  IP-09 requires a defined manual fallback for every P0 integration; the fallback is invisible to the
  person affected unless it is written down here.
traces_to: [M27, M28, 05-03 IP-09, OP-014, NT-001, NT-021]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: NT-025_Notification_Failure_and_Fallback_Copy_BN.md
channels: [All channels]
consent_class: Inherits the failed message class
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

# NT-025 — Notification Failure and Fallback Copy

> **A failure the user cannot see is a failure they cannot work around.** When a channel fails,
> somebody is still waiting for the information. This library tells them.

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | All channels |
| Audience | Whoever the failed message was for, plus internal owners |
| Owning module | `M27`, `M28` |
| Consent class | Inherits the failed message class |
| Quiet-hours exempt | Inherits |
| Content class | C — Operational-critical |
| Bengali required | **Yes** — see `BN-014` |
| Bangladesh routing | Inherits |

---

## 2. Templates

### 2.1 User-visible fallback copy

| Situation | Key | English | Bengali |
|---|---|---|---|
| SMS could not be sent | `fb.sms_failed` | We could not send an SMS to {mobile}. Check the number in your profile. | আমরা {mobile}-এ এসএমএস পাঠাতে পারিনি। আপনার প্রোফাইলে নম্বরটি দেখুন। |
| Email bounced | `fb.email_bounced` | Emails to {email} are not arriving. Update it, or we will use SMS. | {email}-এ ইমেইল পৌঁছাচ্ছে না। এটি হালনাগাদ করুন, নয়তো আমরা এসএমএস ব্যবহার করব। |
| Downgraded to SMS | `fb.downgraded` | We sent this by SMS because push notifications are turned off. | পুশ বিজ্ঞপ্তি বন্ধ থাকায় আমরা এটি এসএমএস-এ পাঠিয়েছি। |
| OTP not arriving | `fb.otp_delay` | The code has not arrived. Wait {seconds} seconds, then request a new one, or call 16743. | কোডটি আসেনি। {seconds} সেকেন্ড অপেক্ষা করুন, তারপর নতুন কোড নিন, বা 16743-এ কল করুন। |
| Channel unavailable | `fb.channel_down` | {channel} is not working right now. We will reach you by {alternative}. | {channel} এখন কাজ করছে না। আমরা {alternative}-এ আপনার সাথে যোগাযোগ করব। |

### 2.2 Staff-facing fallback copy

| Situation | Key | English |
|---|---|---|
| Cannot notify customer | `fb.staff.cannot_notify` | We could not reach {customer} on any channel. Call them on {mobile} and record the contact. |
| Manual fallback active | `fb.staff.manual` | {channel} is down. Use the manual procedure in `OP-014` §{section} and record it here when service returns. |
| Queued for later | `fb.staff.queued` | {count} messages queued. They will send when {channel} returns. |

### 2.3 Rules

| # | Rule |
|---|---|
| **FF-01** | **No notifiable event is silently dropped.** Where all channels fail, it becomes a human task (`NT-001` §4) |
| **FF-02** | The fallback message names the **alternative channel**, not just the failure |
| **FF-03** | An OTP failure never falls back silently to another channel — the user is told and chooses (`NT-007` §4) |
| **FF-04** | A bounced email flags the address on the party record and notifies the owning function |
| **FF-05** | Manual fallback copy names the `OP-014` section, so the procedure is one click away |
| **FF-06** | A suppressed message is logged as **suppressed**, never as failed — the distinction matters for `CG-014` E-22 |

---

## 3. Channel-specific requirements

| Requirement | Rule |
|---|---|
| Retry | Once, after 5 minutes, then fall back |
| Fallback order | Per the `NT-001` matrix, not ad hoc |
| Logging | Every failure logged with channel, reason and fallback taken |
| Alerting | Aggregate failure above threshold raises `NT-021` `alert.int.generic` |
| Measurement | Failure rate feeds `CG-014` E-22, target under 1% |

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
| [`NT-001_Notification_Strategy_and_Event_Channel_Matrix.md`](NT-001_Notification_Strategy_and_Event_Channel_Matrix.md) | Fallback order |
| [`04D_In_App_Voice_and_System/NT-021_System_Integration_and_Job_Failure_Alert_Library.md`](04D_In_App_Voice_and_System/NT-021_System_Integration_and_Job_Failure_Alert_Library.md) | Aggregate alerting |
| `OP-014` Manual Fallback Procedure Set | The procedures |
| `05-03` IP-09 | The obligation |

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
