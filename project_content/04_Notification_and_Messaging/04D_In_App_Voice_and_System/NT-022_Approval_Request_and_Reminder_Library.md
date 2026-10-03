---
id: NT-022
title: Approval Request and Reminder Library
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
  Approval requests, delegation, reminders, escalation-on-timeout and expiry notices across all
  approval chains. Approval chains span estimates, discounts, purchases, payroll, leave and corporate
  delegation; an unclear request stalls the whole flow behind it.
traces_to: [M63, SP-004, MD-008, UI-007, NT-001, NT-003]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: NT-022_Approval_Request_and_Reminder_Library_BN.md
channels: [Push, email, in-app]
consent_class: Transactional — internal and corporate
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

# NT-022 — Approval Request and Reminder Library

> **An approval sitting in someone's inbox is a customer waiting.** Every request states what is
> being approved, how much, who asked, and what happens if nobody acts.

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | Push, email, in-app |
| Audience | Approvers across every approval chain |
| Owning module | `M63`, `M30` |
| Consent class | Transactional — internal and corporate |
| Quiet-hours exempt | Business hours for reminders; requests sent immediately |
| Content class | C — Operational-critical |
| Bengali required | **Yes** — see `BN-014` |
| Bangladesh routing | Internal and corporate channels |

---

## 2. Templates

### 2.1 Templates

| # | Event | Key | Subject / title EN | Body EN | Bengali title |
|---|---|---|---|---|---|
| 1 | Approval requested | `appr.request` | Approval needed — {object} {amount} | {requester} asks you to approve {object} for {amount}. {context} Approve by {deadline}. | অনুমোদন প্রয়োজন |
| 2 | Reminder 1 | `appr.reminder_1` | Still waiting — {object} | {requester} is waiting on {object} for {amount}. {consequence} | এখনও অপেক্ষমাণ |
| 3 | Reminder 2 | `appr.reminder_2` | {object} waiting {hours} hours | {consequence} Approve, decline, or delegate to {delegate}. | {hours} ঘণ্টা অপেক্ষমাণ |
| 4 | Escalated | `appr.escalated` | Escalated to you — {object} | {original_approver} did not respond within {hours} hours. {context} | আপনার কাছে এস্কেলেট হয়েছে |
| 5 | Delegated | `appr.delegated` | {delegator} delegated this to you | {object} for {amount}. Their authority applies. | {delegator} আপনাকে দায়িত্ব দিয়েছেন |
| 6 | Approved — requester | `appr.approved` | Approved — {object} | {approver} approved {amount}. You can proceed. | অনুমোদিত |
| 7 | Declined — requester | `appr.declined` | Declined — {object} | {approver} declined. Reason: {reason}. | প্রত্যাখ্যাত |
| 8 | Expired | `appr.expired` | Approval request expired — {object} | Nobody responded within {hours} hours. {requester} must raise it again. | অনুমোদনের অনুরোধ মেয়াদোত্তীর্ণ |

### 2.2 The consequence line

`{consequence}` is not decoration. It is what makes an approver act.

| Approval type | Consequence text EN |
|---|---|
| Repair estimate | The customer's repair has not started and their device is waiting. |
| Purchase order | The part cannot be ordered and {count} jobs are waiting on it. |
| Discount | The customer is at the counter waiting for a price. |
| Leave | {employee} cannot plan and the roster is unconfirmed. |
| Payroll | Payroll cannot be disbursed for {count} employees. |
| Corporate service request | Work on {site} has not started. |

### 2.3 Rules

| # | Rule |
|---|---|
| **AP-01** | Every request names **what**, **how much**, **who asked** and **by when** |
| **AP-02** | Every reminder carries the **consequence**, not just the elapsed time |
| **AP-03** | Reminders escalate at the timeouts in `SP-004`, not on an arbitrary schedule |
| **AP-04** | The approver is always offered **delegate** as well as approve and decline |
| **AP-05** | An expired request notifies the **requester**, not silently vanishes |
| **AP-06** | Approval limits and routing come from `SP-004` and `MD-008`; this library never invents a route |
| **AP-07** | A request is never sent to someone who cannot approve it — that is a routing defect, not a copy one |

---

## 3. Channel-specific requirements

| Requirement | Rule |
|---|---|
| Channel | Push for immediacy, email for the record, in-app for reference |
| Timing | Request immediate; reminders in business hours (`NT-003`) |
| Escalation | On timeout per `SP-004`, with the original approver informed |
| Deep link | Straight to the approval action, never the home screen |
| Delegation | Pre-registered deputies only (`CG-007` §8) |

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
| `SP-004` Approval Matrix and Delegation of Authority | Limits, routing, timeouts |
| `MD-008` Organisation Structure and Position Master | Approver positions |
| [`../../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-007_Confirmation_Warning_and_Destructive_Action_Library.md`](../../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-007_Confirmation_Warning_and_Destructive_Action_Library.md) | The in-product approval dialog |

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
