---
id: NT-007
title: OTP and Security Message Library
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
reviewers: [Security, Localisation Lead, Platform Engineering, Legal & Compliance]
approver: Content Design Lead
content_class: C
purpose: >
  OTP, login alert, password change, new-device, MFA and suspicious-activity messages. OTP wording is
  an anti-phishing control: inconsistent OTP messages train customers to trust forgeries, and a
  leaked code is an account takeover.
traces_to: [M29, PS-01, PS-12, UI-005, NT-001, NT-003]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: NT-007_OTP_and_Security_Message_Library_BN.md
channels: [SMS]
consent_class: Security — always sent
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

# NT-007 — OTP and Security Message Library

> **This library is a security control, not a courtesy.** Customers learn what a genuine 1000FiX
> OTP looks like. Every variation makes a forgery easier to pass off.
>
> Security messages are **never suppressed, never delayed, never batched** (`NT-003` §2.5).

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | SMS |
| Audience | Every authenticated user across all portals |
| Owning module | `M29` |
| Consent class | Security — always sent |
| Quiet-hours exempt | **Exempt — 24/7** |
| Content class | C — Operational-critical |
| Bengali required | **Yes** — see `BN-014` |
| Bangladesh routing | Masking; never non-masking |

---

## 2. Templates

### 2.1 OTP templates

| Event | Template ID | English | Bengali | BN seg |
|---|---|---|---|:--:|
| Sign-in OTP | `sms.sec.otp_login` | 1000FiX: {code} is your sign-in code. Valid {minutes} minutes. Never share this code. | 1000FiX: {code} আপনার সাইন-ইন কোড। {minutes} মিনিট বৈধ। এই কোড কাউকে জানাবেন না। | 3 |
| Registration OTP | `sms.sec.otp_register` | 1000FiX: {code} is your verification code. Valid {minutes} minutes. Never share this code. | 1000FiX: {code} আপনার যাচাই কোড। {minutes} মিনিট বৈধ। এই কোড কাউকে জানাবেন না। | 3 |
| Transaction OTP | `sms.sec.otp_txn` | 1000FiX: {code} to confirm {action} of {amount}. Valid {minutes} minutes. Never share this code. | 1000FiX: {amount}-এর {action} নিশ্চিত করতে {code}। {minutes} মিনিট বৈধ। এই কোড কাউকে জানাবেন না। | 3 |
| Handover OTP | `sms.sec.otp_handover` | 1000FiX: {code} to confirm handover of your {device}. Give this to the rider only. | 1000FiX: আপনার {device} হস্তান্তর নিশ্চিত করতে {code}। শুধু রাইডারকে দিন। | 3 |

### 2.2 Security alerts

| Event | Template ID | English | Bengali |
|---|---|---|---|
| New device sign-in | `sms.sec.new_device` | 1000FiX: New sign-in from {device_type} at {time}. Not you? Call 16743 now. | 1000FiX: {time}-এ {device_type} থেকে নতুন সাইন-ইন। আপনি না হলে এখনই 16743-এ কল করুন। |
| Password changed | `sms.sec.password` | 1000FiX: Your password was changed at {time}. Not you? Call 16743 now. | 1000FiX: {time}-এ আপনার পাসওয়ার্ড পরিবর্তন হয়েছে। আপনি না হলে এখনই 16743-এ কল করুন। |
| Mobile changed | `sms.sec.mobile` | 1000FiX: Your registered mobile was changed at {time}. Not you? Call 16743 now. | 1000FiX: {time}-এ আপনার নিবন্ধিত মোবাইল পরিবর্তন হয়েছে। আপনি না হলে এখনই 16743-এ কল করুন। |
| Account locked | `sms.sec.locked` | 1000FiX: Your account is locked after too many incorrect codes. It unlocks in {minutes} minutes. | 1000FiX: অনেকবার ভুল কোডের পর আপনার অ্যাকাউন্ট লক হয়েছে। {minutes} মিনিটে খুলবে। |

### 2.3 Anti-phishing rules — the reason this is Class C

| # | Rule |
|---|---|
| **OT-01** | **The code comes first or immediately after the brand.** A user glancing at a notification preview must see it without opening the message |
| **OT-02** | **"Never share this code" appears in every OTP message**, in both languages, without exception |
| **OT-03** | **No link in any OTP message, ever.** A message containing both a code and a link is the exact shape of a phishing attack |
| **OT-04** | The action being authorised is **named** in transaction OTPs, so a user cannot be tricked into approving something else |
| **OT-05** | Alerts always give the hotline, never a link |
| **OT-06** | Codes are **6 digits**, numeric only, and never reused within the validity window |
| **OT-07** | Wording is **identical every time**. Variation is the vulnerability |
| **OT-08** | Sent on the **masking route only**. An OTP from a numeric sender is indistinguishable from a forgery |

> **OT-03 is the rule most often broken in practice**, usually to add "tap here to verify". It
> must never be added to these templates.

### 2.4 Rate limiting

| Control | Value | Message |
|---|---|---|
| Resend cooldown | 60 seconds | `UI-005` `common.mfa.resend_wait` |
| Max sends per hour per number | 5 | `sms.sec.locked` |
| Max incorrect attempts | 5 | `sms.sec.locked` |
| Lockout duration | 30 minutes | `sms.sec.locked` |

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

> **OTP messages route only through the masking sender.** `NT-001` BD-01 applies with no exception: an OTP on a non-masking route is indistinguishable from a phishing message.

---

## 4. Failure and fallback

| Failure | Behaviour |
|---|---|
| OTP undeliverable | **Do not fall back to email silently.** Offer the user an explicit alternative and log the failure |
| Gateway down | Secondary gateway immediately — OTP has no tolerance for delay |
| Both gateways down | Show the user that verification is unavailable and offer the hotline. **Never bypass verification** |
| Alert undeliverable | Retry, then raise a security task — an undelivered security alert is a security event |

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
| [`../../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-005_System_Permission_and_Session_Message_Library.md`](../../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-005_System_Permission_and_Session_Message_Library.md) | On-screen MFA copy |
| `M29` Identity, Access and Information Security | The implementing module |
| `TS-017` Security and Privacy Test Case Pack | Verification |

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
