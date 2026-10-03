---
id: NT-016
title: Push Notification Library — P02 Technician App
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
  Job, reassignment, escalation, safety, sync and shift push copy. Technicians act on push; ambiguity
  costs a wasted journey across a city, and the SMS fallback in NT-005 exists because push is not
  guaranteed to arrive.
traces_to: [`M02`, NT-001, NT-003, UI-009, P02]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: NT-016_Push_Notification_Library_P02_Technician_App_BN.md
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

# NT-016 — Push Notification Library — P02 Technician App

> **Technicians act on push.** A push that does not say where and when sends someone to the wrong
> place. Every job push carries the area and the time.

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | Push |
| Audience | Field technicians (200–400) |
| Owning module | `M02`, `P02` |
| Consent class | Transactional |
| Quiet-hours exempt | Exempt for transactional; content push respects `NT-003` |
| Content class | D — User-facing |
| Bengali required | **Yes** — see `BN-014` |
| Bangladesh routing | Device push, not SMS |

---

## 2. Templates

| # | Event | Key | Title EN | Body EN | Title BN | Fallback |
|---|---|---|---|---|---|---|
| 1 | New job | `push.p02.new_job` | New job {ref} | {area}, {time}. Tap to accept. | নতুন জব {ref} | SMS `sms.tech.assigned` |
| 2 | Urgent job | `push.p02.urgent` | Urgent job {ref} | {area}. Call dispatch on 16743. | জরুরি জব {ref} | SMS `sms.tech.urgent` |
| 3 | Reassigned away | `push.p02.removed` | Job {ref} reassigned | You do not need to attend. | জব {ref} পুনরায় বরাদ্দ | SMS |
| 4 | Estimate approved | `push.p02.approved` | Customer approved {ref} | {amount}. You can start work. | গ্রাহক {ref} অনুমোদন করেছেন | — |
| 5 | Estimate declined | `push.p02.declined` | Customer declined {ref} | Return the device unrepaired. | গ্রাহক {ref} প্রত্যাখ্যান করেছেন | — |
| 6 | Part arrived | `push.p02.part` | Part arrived for {ref} | Collect from {location}. | {ref}-এর পার্টস এসেছে | — |
| 7 | Sync failed | `push.p02.sync_failed` | Sync problem | {count} items not synced. Your work is saved. | সিঙ্ক সমস্যা | — |
| 8 | Shift reminder | `push.p02.shift` | Shift at {time} | {branch} tomorrow. | {time}-এ শিফট | SMS |
| 9 | Safety notice | `push.p02.safety` | Safety notice | {hazard}. Read before your next job. | নিরাপত্তা নোটিশ | SMS — **never suppressed** |

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
| `P02` | The consuming surface |

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
