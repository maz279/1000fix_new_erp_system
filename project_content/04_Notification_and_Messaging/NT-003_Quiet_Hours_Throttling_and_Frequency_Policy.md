---
id: NT-003
title: Quiet Hours, Throttling and Frequency Policy
project: 1000FiX ERP System v2.0
content_type: Policy
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design Lead with Operations
author: Content Design
reviewers: [Operations, Marketing, Legal & Compliance, Platform Engineering]
approver: Content Design Lead
content_class: E
purpose: >
  Send windows, per-customer frequency caps, batching, escalation exemptions and religious and
  public-holiday sensitivity. Messaging a customer at 03:00 or eleven times in a day destroys
  channel trust and triggers opt-outs the business cannot afford to lose.
traces_to: [M27, NT-001, NT-002, MD-041, CG-014 E-21]
priority: P1
wave: W2
bilingual: no
bn_counterpart: n/a
channels: [SMS, WhatsApp, email, push]
consent_class: Applies across all classes
sources:
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M27_Omnichannel_Contact_Centre_and_Communications.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03 §2.2 communications integrations
    verified: 2026-08-15
    class: P1
  - source: Bangladesh A2P SMS practice — masking (alphanumeric brand sender) carries transactional and OTP traffic; non-masking (numeric sender) carries promotional. Misclassification between the two is a common cause of route suspension. All traffic routes through BTRC-listed aggregators
    verified: 2026-08-15
    class: P3
  - source: BTRC Do Not Disturb service — promotional SMS may not be sent to DND-registered numbers and is time-restricted; transactional SMS is exempt and delivers 24/7
    verified: 2026-08-15
    class: P3
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §9 — Bangladesh public holidays including moon-dependent dates
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# NT-003 — Quiet Hours, Throttling and Frequency Policy

> **Every message spends trust.** The channel that reaches 250,000 customers a month only keeps
> working while people still read it.
>
> Two forces set the rules: **regulation** — promotional SMS is time-restricted and DND-bound in
> Bangladesh — and **judgement**, which is what the rest of this file is.

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | SMS, WhatsApp, email, push |
| Audience | All external audiences |
| Owning module | `M27` |
| Consent class | Applies across all classes |
| Quiet-hours exempt | **Defines the windows** |
| Content class | E — Internal governance |
| Bengali required | No — internal governance (`CG-010` §3.2) |
| Bangladesh routing | Promotional traffic is time-restricted in Bangladesh |

---

## 2. Templates

### 2.1 Send windows (Asia/Dhaka)

| Class | Window | Outside the window |
|---|---|---|
| **Security** (OTP, sign-in) | **24/7** | Always sent — never delayed |
| **Transactional** | **24/7** | Always sent |
| **Service-related** | 08:00–21:00 | Held to the next window |
| **Marketing** | **10:00–20:00** | Held to the next window |
| **Internal operational** | Per on-call policy (`OP-013`) | Sent — the recipient is on duty |

| # | Rule |
|---|---|
| **QH-01** | **Security and transactional messages are never delayed.** A customer waiting on an OTP at 02:00 asked for it |
| **QH-02** | Service-related and marketing messages are **held**, never dropped |
| **QH-03** | A held message that is stale by the time the window opens is **discarded**, not sent late. A collection reminder for a device collected yesterday is noise |
| **QH-04** | Windows are Asia/Dhaka; there is no per-customer timezone |

### 2.2 Frequency caps — per customer

| Class | Cap | Period |
|---|---:|---|
| Transactional | **Uncapped** | — |
| Security | Uncapped, but rate-limited per `NT-007` | — |
| Service-related | 3 | Rolling 7 days |
| Marketing | **2** | Rolling 7 days |
| **All non-transactional combined** | **4** | Rolling 7 days |

| # | Rule |
|---|---|
| **FR-01** | Transactional messages are uncapped. A customer with three open orders gets three sets of updates, and that is correct |
| **FR-02** | When a cap is reached, the lowest-priority pending message is dropped, not queued indefinitely |
| **FR-03** | Caps are per **party**, not per channel. Four messages across SMS, email and push is four |
| **FR-04** | A customer who has just complained is suppressed from marketing for 30 days |

### 2.3 Batching and deduplication

| # | Rule |
|---|---|
| **BA-01** | Two events for the same order within **10 minutes** produce one message covering both |
| **BA-02** | A corporate admin with 40 bulk requests receives **one** summary, not 40 messages |
| **BA-03** | Deduplication is by event + audience + object, over a 30-minute window |
| **BA-04** | Batching never delays a security or transactional message beyond 10 minutes |

### 2.4 Calendar sensitivity

Holiday dates come from `MD-041`, including the `date_confirmed` flag for moon-dependent
observances.

| Occasion | Marketing | Service-related | Transactional |
|---|---|---|---|
| Eid days (both) | **Suspended** | Suspended | Normal |
| Other public holidays | Suspended | Reduced window 10:00–18:00 | Normal |
| Ramadan | Window shifts to 10:00–16:00 and 20:00–22:00 | As marketing | Normal |
| Mourning days declared nationally | **Suspended** | Suspended | Normal |

> **Moon-dependent dates shift.** `MD-041` carries provisional dates with `date_confirmed = FALSE`;
> the suppression calendar re-evaluates when the date is confirmed. A campaign scheduled against
> a provisional Eid date must not send on the wrong day.

### 2.5 Exemptions

Only these override the windows and caps:

| Exemption | Authority |
|---|---|
| Security and OTP | Automatic |
| Transactional service updates | Automatic |
| SLA breach escalation (`NT-020`) | Automatic |
| Safety alert (`P02` panic) | Automatic |
| Recall or safety notice from a brand | Quality Manager |
| Regulatory or legal notice | Legal Counsel |

**No commercial exemption exists.** A campaign deadline is not a reason to message at 22:00.

---

## 3. Channel-specific requirements

| Channel | Additional constraint |
|---|---|
| SMS promotional | Regulatory time restriction plus DND exclusion (`NT-001` §3.1) |
| SMS transactional | Delivers 24/7 including to DND numbers |
| WhatsApp | Meta quality rating degrades on blocks; a suppressed message protects the number |
| Push | Silent push permitted outside windows for background sync only, never for content |
| Email | Windows do not apply; frequency caps do |

---

## 4. Failure and fallback

| Situation | Behaviour |
|---|---|
| Cap reached, high-value message pending | Drop the lowest-priority pending, send the higher |
| Holiday calendar unavailable | **Suppress marketing**, allow transactional. Fail closed |
| Window calculation fails | Fail closed for marketing, open for transactional |
| Batching window expires mid-batch | Send what is batched; do not hold for a later event |

---

## 5. Change log and governance

| Item | Value |
|---|---|
| Who may change a window or cap | Content Design Lead with Operations; Legal for regulatory windows |
| Who may grant an exemption | Only the authorities in §2.5 |
| Monitoring | Opt-out rate per message type (`CG-014` E-21, target under 2%) |
| Review | Quarterly, and after any opt-out spike |

---

## 6. Related documents

| Document | Relationship |
|---|---|
| [`NT-001_Notification_Strategy_and_Event_Channel_Matrix.md`](NT-001_Notification_Strategy_and_Event_Channel_Matrix.md) | What is sent |
| [`NT-002_Notification_Preference_and_Consent_Copy.md`](NT-002_Notification_Preference_and_Consent_Copy.md) | The classes |
| `MD-041` Fiscal and Bangladesh Holiday Calendar | Holiday and moon-dependent dates |
| `CG-014` E-21 | Opt-out rate as the effectiveness measure |

---

## 7. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Content Design Lead (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:`, `traces_to:`, `channels:` and `consent_class:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`
- [x] Every template names its trigger event, channel, audience and suppression rules (`CG-008` NT-a)
- [x] Every event exists in the `NT-001` channel matrix (`CG-008` NT-b)
- [x] Variables declared with their source field (`CG-008` NT-c)
- [x] Consent class stated — transactional or marketing (`CG-008` NT-d, `NT-002`)
- [x] Fallback defined for channel failure (`CG-008` NT-g, `IP-09`)
- [x] Quiet-hours and frequency treatment stated (`CG-008` NT-h, `NT-003`)
- [x] Status labels quoted from `MD-027` **customer-facing** column, never the internal state key (`T-06`)
- [x] All internal links resolve
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2
- [ ] Meta template category, submission and approval status recorded (`CG-008` NT-f)
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
