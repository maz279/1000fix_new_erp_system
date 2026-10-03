---
id: NT-024
title: Survey, Feedback and NPS Invitation Library
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
  Post-service rating, NPS, technician rating, complaint-follow-up and closure-confirmation messages.
  CSAT and NPS are board-level KPIs, and response rate is driven almost entirely by invitation wording
  and timing rather than by the survey itself.
traces_to: [M34, NT-001, NT-003, CG-014, 06-02, SP-028]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: NT-024_Survey_Feedback_and_NPS_Invitation_Library_BN.md
channels: [SMS, email, push, in-app]
consent_class: Service-related
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

# NT-024 — Survey, Feedback and NPS Invitation Library

> **Ask once, ask soon, ask short.** Response rate collapses with delay and with length. One
> question in the message itself beats a link to five questions.

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | SMS, email, push, in-app |
| Audience | Customers who completed a service |
| Owning module | `M34` |
| Consent class | Service-related |
| Quiet-hours exempt | 08:00–21:00; delayed 2 hours after completion |
| Content class | D — User-facing |
| Bengali required | **Yes** — see `BN-014` |
| Bangladesh routing | Masking (service-related) |

---

## 2. Templates

### 2.1 Templates

| # | Event | Key | Timing | English | Bengali |
|---|---|---|---|---|---|
| 1 | Post-service rating | `fb.rating` | 2 h after completion | 1000FiX: How was your service? Reply 1–5, where 5 is excellent. Ref {ref}. | 1000FiX: আপনার সার্ভিস কেমন ছিল? ১–৫ উত্তর দিন, ৫ মানে চমৎকার। রেফ {ref}। |
| 2 | Low rating follow-up | `fb.low_followup` | Immediately on 1–2 | 1000FiX: Sorry we fell short. We will call you within {hours} hours. Ref {ref}. | 1000FiX: দুঃখিত আমরা প্রত্যাশা পূরণ করতে পারিনি। {hours} ঘণ্টার মধ্যে কল করব। রেফ {ref}। |
| 3 | High rating follow-up | `fb.high_followup` | On 5 | 1000FiX: Thank you. Tell others at {review_link} if you have a moment. | 1000FiX: ধন্যবাদ। সময় থাকলে {review_link}-এ অন্যদের জানান। |
| 4 | Technician rating | `fb.technician` | With `fb.rating` | How was {tech}? | {tech} কেমন ছিলেন? |
| 5 | NPS | `fb.nps` | 30 days after first service | How likely are you to recommend 1000FiX? 0–10. | 1000FiX সুপারিশ করার সম্ভাবনা কতটা? ০–১০। |
| 6 | Complaint closure | `fb.complaint_closed` | On closure | 1000FiX: We have closed your complaint {ref}. Are you satisfied with the outcome? Reply YES or NO. | 1000FiX: আমরা আপনার অভিযোগ {ref} বন্ধ করেছি। ফলাফলে আপনি সন্তুষ্ট? YES বা NO লিখুন। |
| 7 | Corporate service review | `fb.corp_review` | Quarterly | Your quarterly service review — {date} | — |

### 2.2 Rules

| # | Rule |
|---|---|
| **FB-01** | **The question is in the message.** A link-only invitation halves response rate |
| **FB-02** | Sent **2 hours after completion** — long enough that the customer has the device, short enough to remember |
| **FB-03** | **One reminder maximum**, after 48 hours. Then never again for that service |
| **FB-04** | A rating of 1–2 triggers a human follow-up within the stated time — the promise is kept or not made |
| **FB-05** | The high-rating review request is a **separate, later** message, never bundled with the rating request |
| **FB-06** | NPS once per customer per 6 months, maximum |
| **FB-07** | A customer with an open complaint is not asked for NPS |
| **FB-08** | Counts against the service-related cap (`NT-003` §2.2) |

> **`FB-04` is a commitment.** "We will call you within {hours} hours" is a promise made on the
> company's behalf by an automated message. If the follow-up does not happen, the low rating
> becomes a complaint.

---

## 3. Channel-specific requirements

| Requirement | Rule |
|---|---|
| Reply handling | SMS replies parsed for 1–5, 0–10, YES/NO; anything else routes to an agent |
| Timing | 2 hours after completion; one reminder at 48 hours |
| Suppression | Open complaint, recent survey, or opted out of service-related messages |
| Language | Customer's preferred language |
| Measurement | Response rate and score feed `CG-014` and `06-02` |

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
| `M34` Customer Experience, Feedback and Complaints | The implementing module |
| `SP-028` SOP Complaint, Escalation and Compensation | Low-rating follow-up |
| `CG-014` Content Metrics | Where response rate is measured |
| `06-02` KPI, Benefits and Acceptance Criteria | CSAT and NPS targets |

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
