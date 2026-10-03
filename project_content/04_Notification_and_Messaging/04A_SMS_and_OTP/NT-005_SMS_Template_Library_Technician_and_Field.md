---
id: NT-005
title: SMS Template Library — Technician and Field
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
  Job assignment, reassignment, escalation, roster, safety and payout SMS for field staff. Technicians
  without data connectivity still receive SMS; it is the fallback channel for dispatch when the P02
  push path fails.
traces_to: [M02, M03, P02, P09, NT-001, NT-016, NT-017]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: NT-005_SMS_Template_Library_Technician_and_Field_BN.md
channels: [SMS]
consent_class: Transactional — internal
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

# NT-005 — SMS Template Library — Technician and Field

> **SMS is the dispatch fallback.** When `P02` push does not arrive — no data, dead battery,
> app not running — SMS is what still reaches a technician standing in a customer's hallway.

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | SMS |
| Audience | Field technicians (200–400), riders (50–200) |
| Owning module | `M02`, `M03` |
| Consent class | Transactional — internal |
| Quiet-hours exempt | Exempt; field staff are on duty |
| Content class | D — User-facing |
| Bengali required | **Yes** — see `BN-014` |
| Bangladesh routing | Masking |

---

## 2. Templates

### 2.1 Template set

| # | Event | Template ID | English | Bengali | BN seg |
|---|---|---|---|---|:--:|
| 1 | Job assigned | `sms.tech.assigned` | 1000FiX: New job {ref} at {area}, {time}. Open the app for details. | 1000FiX: নতুন জব {ref}, {area}, {time}। বিস্তারিত জানতে অ্যাপ খুলুন। | 2 |
| 2 | Job reassigned away | `sms.tech.removed` | 1000FiX: Job {ref} has been reassigned. You do not need to attend. | 1000FiX: জব {ref} পুনরায় বরাদ্দ হয়েছে। আপনাকে যেতে হবে না। | 2 |
| 3 | Urgent job | `sms.tech.urgent` | 1000FiX: URGENT job {ref} at {area}. Call dispatch on 16743 now. | 1000FiX: জরুরি জব {ref}, {area}। এখনই 16743-এ ডিসপ্যাচে কল করুন। | 2 |
| 4 | Escalation | `sms.tech.escalate` | 1000FiX: Job {ref} escalated to {level}. {action} | 1000FiX: জব {ref} {level}-এ এস্কেলেট হয়েছে। {action} | 2 |
| 5 | Roster published | `sms.tech.roster` | 1000FiX: Your roster for {period} is published. Check the app. | 1000FiX: {period}-এর আপনার রোস্টার প্রকাশিত হয়েছে। অ্যাপ দেখুন। | 2 |
| 6 | Shift reminder | `sms.tech.shift` | 1000FiX: Shift starts {time} at {branch} tomorrow. | 1000FiX: আগামীকাল {branch}-এ {time}-এ শিফট শুরু। | 2 |
| 7 | Certification expiring | `sms.tech.cert_expiring` | 1000FiX: Your {brand} certification expires {date}. Contact Quality to renew. | 1000FiX: আপনার {brand} সার্টিফিকেশন {date}-এ শেষ হবে। নবায়নে কোয়ালিটিতে যোগাযোগ করুন। | 3 |
| 8 | Certification expired | `sms.tech.cert_expired` | 1000FiX: Your {brand} certification has expired. You cannot take {brand} warranty jobs. | 1000FiX: আপনার {brand} সার্টিফিকেশন শেষ হয়েছে। আপনি {brand} ওয়ারেন্টি জব নিতে পারবেন না। | 3 |
| 9 | Payout | `sms.tech.payout` | 1000FiX: {amount} incentive paid for {period}. See the app for the breakdown. | 1000FiX: {period}-এর জন্য {amount} ইনসেনটিভ পরিশোধিত। বিস্তারিত অ্যাপে দেখুন। | 2 |
| 10 | Safety acknowledgement | `sms.tech.safety` | 1000FiX: Safety notice for {hazard}. Read it in the app before your next job. | 1000FiX: {hazard} সংক্রান্ত নিরাপত্তা নোটিশ। পরবর্তী জবের আগে অ্যাপে পড়ুন। | 3 |

### 2.2 Rules

| # | Rule |
|---|---|
| **TS-01** | SMS carries the **fact and the next action**, never the full job detail — that is in `P02` |
| **TS-02** | Urgent messages name the hotline, because a technician may not have data |
| **TS-03** | Certification messages are sent to the technician **and** their supervisor (`NT-014`) |
| **TS-04** | Safety messages are never batched or delayed (`NT-003` §2.5) |
| **TS-05** | Payout messages never state a bank account or full amount breakdown over SMS |

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
| [`../04B_WhatsApp_and_Push/NT-016_Push_Notification_Library_P02_Technician_App.md`](../04B_WhatsApp_and_Push/NT-016_Push_Notification_Library_P02_Technician_App.md) | The primary channel this backs up |
| `MD-011` Certification Register | Expiry triggers |
| `TR-009` Course Pack Field Technician | Where these messages are explained |

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
