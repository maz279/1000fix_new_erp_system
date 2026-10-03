---
id: NT-006
title: SMS Template Library — Finance and Collections
project: 1000FiX ERP System v2.0
content_type: Notification template library
template: TPL_Notification_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance with Content Design
author: Content Design
reviewers: [Legal Counsel, Finance, Localisation Lead, Customer Experience]
approver: Legal Counsel
content_class: B
purpose: >
  Payment reminder, overdue, receipt confirmation, refund and dunning-ladder SMS. Collections messaging
  carries legal tone constraints; ad-hoc wording creates harassment exposure and damages the
  relationship with a customer who may simply have forgotten.
traces_to: [M20, DT-018, LG-014, NT-001, NT-003]
priority: P1
wave: W3
bilingual: yes
bn_counterpart: NT-006_SMS_Template_Library_Finance_and_Collections_BN.md
channels: [SMS]
consent_class: Transactional
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

# NT-006 — SMS Template Library — Finance and Collections

> ⚠ **Class B — legal.** Collections wording is constrained by law and by decency. Gate **G5**
> applies and is unwaivable (`WV-02`).
>
> **The dunning ladder escalates in specificity, never in aggression.** Every message states the
> amount, the reference and a way to pay or to talk to us.

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | SMS |
| Audience | Customers with outstanding balances; corporate finance contacts |
| Owning module | `M20` |
| Consent class | Transactional |
| Quiet-hours exempt | Exempt for receipts; dunning held to 09:00–19:00 |
| Content class | B — Legal / contractual |
| Bengali required | **Yes** — see `BN-014` |
| Bangladesh routing | Masking |

---

## 2. Templates

### 2.1 The dunning ladder

| Stage | Days overdue | Template ID | English | Bengali | BN seg |
|---|---:|---|---|---|:--:|
| Reminder | −3 (before due) | `sms.fin.due_soon` | 1000FiX: {amount} for {ref} is due on {date}. Pay at {link}. | 1000FiX: {ref}-এর {amount} {date}-এ প্রদেয়। {link}-এ পরিশোধ করুন। | 2 |
| 1st | 1 | `sms.fin.overdue_1` | 1000FiX: {amount} for {ref} was due {date}. Pay at {link} or call 16743. | 1000FiX: {ref}-এর {amount} {date}-এ প্রদেয় ছিল। {link}-এ পরিশোধ করুন বা 16743-এ কল করুন। | 3 |
| 2nd | 7 | `sms.fin.overdue_2` | 1000FiX: {amount} for {ref} is 7 days overdue. Please pay or call 16743 to arrange terms. | 1000FiX: {ref}-এর {amount} ৭ দিন বকেয়া। পরিশোধ করুন বা শর্ত নির্ধারণে 16743-এ কল করুন। | 3 |
| 3rd | 21 | `sms.fin.overdue_3` | 1000FiX: {amount} for {ref} is 21 days overdue. Contact us on 16743 before {date}. | 1000FiX: {ref}-এর {amount} ২১ দিন বকেয়া। {date}-এর আগে 16743-এ যোগাযোগ করুন। | 3 |
| Final | 45 | `sms.fin.final` | 1000FiX: {amount} for {ref} remains unpaid. Please contact us on 16743 to resolve this. | 1000FiX: {ref}-এর {amount} এখনও অপরিশোধিত। সমাধানে 16743-এ যোগাযোগ করুন। | 3 |

### 2.2 Receipts and refunds

| Event | Template ID | English | Bengali |
|---|---|---|---|
| Payment received | `sms.fin.receipt` | 1000FiX: {amount} received for {ref}. Receipt {receipt_no}. | 1000FiX: {ref}-এর জন্য {amount} গৃহীত। রসিদ {receipt_no}। |
| Partial payment | `sms.fin.partial` | 1000FiX: {paid} received for {ref}. {remaining} remains. | 1000FiX: {ref}-এর জন্য {paid} গৃহীত। {remaining} বাকি। |
| Refund started | `sms.fin.refund_started` | 1000FiX: Refund of {amount} started. It reaches you in {days} days. | 1000FiX: {amount} ফেরত শুরু হয়েছে। {days} দিনে আপনার কাছে পৌঁছাবে। |
| Refund complete | `sms.fin.refund_done` | 1000FiX: {amount} refunded to {method}. | 1000FiX: {method}-এ {amount} ফেরত দেওয়া হয়েছে। |

### 2.3 Collections rules — the constraints that make this Class B

| # | Rule |
|---|---|
| **FN-01** | **Never threaten.** No reference to legal action, credit consequence, blacklisting or service refusal in SMS. Those, where lawful, belong in `DT-018` written correspondence under Legal review |
| **FN-02** | **Never disclose the debt to a third party.** The message goes to the party's registered mobile only |
| **FN-03** | Every message offers a route to talk to us, not only to pay |
| **FN-04** | Maximum **one** dunning message per 7 days per party (`NT-003` FR-03) |
| **FN-05** | Dunning is suppressed while a **dispute is open** on that invoice |
| **FN-06** | Dunning is suppressed on public holidays and during Eid (`NT-003` §2.4) |
| **FN-07** | The ladder stops immediately on payment or on an agreed payment plan |
| **FN-08** | Tone does not escalate. Stage 5 is no harsher than stage 1 — only more specific about time |

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
| `DT-018` Dunning and Collection Letter Series | The written escalation this precedes |
| `LG-014` Refund, Cancellation and Compensation Policy | Refund terms |
| `MD-038` Payment Method Master | Payment methods named |

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
- [ ] G5 legal review — **outstanding, unwaivable (`WV-02`)**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
