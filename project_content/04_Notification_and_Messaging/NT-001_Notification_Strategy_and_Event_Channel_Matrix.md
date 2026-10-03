---
id: NT-001
title: Notification Strategy and Event-Channel Matrix
project: 1000FiX ERP System v2.0
content_type: Governance
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design Lead
author: Content Design
reviewers: [Platform Engineering, Legal & Compliance, Localisation Lead, Operations, Marketing]
approver: Content Design Lead
content_class: E
purpose: >
  Maps every notifiable domain event to audience, channel, priority, language, template ID and
  suppression rule. Without one matrix each module invents its own notifications, and a customer
  receives duplicates from three modules for one event.
traces_to: [M27, 05-03, NT-002, NT-003, MD-027, IP-09]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
channels: [all]
consent_class: n/a — governance
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
supersedes: none
review_due: 2027-02-15
---

# NT-001 — Notification Strategy and Event-Channel Matrix

> **One event, one decision.** A service order reaching *ready for collection* is one event. Left
> to each module, it becomes an SMS from `M01`, a push from `P01` and an email from `M20` — three
> messages for one fact.
>
> This matrix is the single place that decides who is told what, on which channel, in which
> language, and when they are not told at all.

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | all |
| Audience | All eleven audience types |
| Owning module | `M27` |
| Consent class | n/a — governance |
| Quiet-hours exempt | n/a |
| Content class | E — Internal governance |
| Bengali required | No — internal governance (`CG-010` §3.2) |
| Bangladesh routing | Defines the routing policy |

---

## 2. Templates

### 2.1 The routing decision

Every notifiable event resolves through five questions, in order.

| # | Question | Source |
|---|---|---|
| 1 | Who has a legitimate interest in knowing? | This matrix |
| 2 | Is this **transactional** or **marketing**? | `NT-002` — legally distinct, never bundled |
| 3 | Which channel reaches them, and what is the fallback? | §2.3 |
| 4 | Which language? | `CG-010` §3.2 |
| 5 | Is it suppressed — quiet hours, frequency cap, preference? | `NT-003` |

### 2.2 Channel selection rules

| # | Rule |
|---|---|
| **CH-01** | **One event, one primary channel per audience.** A second channel requires a stated reason — usually that the first is unreliable for that audience |
| **CH-02** | SMS is the reach channel; push is the speed channel; email is the record channel; in-app is the reference channel |
| **CH-03** | A message that must be **retrievable later** goes to email or in-app, never SMS alone |
| **CH-04** | A message that must be **acted on now** goes to push with an SMS fallback |
| **CH-05** | Where a customer has no smartphone, SMS carries everything. This is the default assumption, not the exception |
| **CH-06** | Internal alerts never go to a customer channel |

### 2.3 The event-channel matrix — service order lifecycle

Status wording is quoted from the `MD-027` **customer-facing** column (`T-06`).

| Event | Customer | Technician | Branch | Corporate admin | Template |
|---|---|---|---|---|---|
| Booking received | SMS + in-app | — | — | Email | `NT-004`, `NT-018`, `NT-010` |
| Technician assigned | SMS | Push | — | — | `NT-004`, `NT-016` |
| Technician on the way | SMS + push | — | — | — | `NT-004`, `NT-015` |
| Device received | SMS | — | — | Email | `NT-004`, `NT-010` |
| Estimate ready | **SMS + push + email** | — | — | Email | `NT-004`, `NT-009` |
| Estimate approved | SMS | Push | — | — | `NT-004`, `NT-016` |
| Estimate declined | SMS | Push | In-app | — | `NT-004`, `NT-016`, `NT-018` |
| Awaiting parts | SMS | — | In-app | Email | `NT-004`, `NT-010` |
| Ready for collection | **SMS + push + email** | — | In-app | Email | `NT-004`, `NT-009` |
| Completed | SMS + email | — | — | Email | `NT-004`, `NT-009` |
| Delayed *(internally `sla_breached`)* | SMS | — | In-app | Email + escalation | `NT-004`, `NT-020` |
| Cancelled | SMS + email | Push | In-app | Email | `NT-004`, `NT-009` |

> **Estimate ready** and **ready for collection** are the two events carrying three channels.
> Both require customer action and both cost money if missed — the estimate stalls the repair,
> and the uncollected device accrues storage liability.

### 2.4 Matrix — other domains

| Domain | Trigger | Audience | Channel | Template |
|---|---|---|---|---|
| Payment | Payment received | Customer | SMS + email | `NT-004`, `NT-009` |
| Payment | Payment overdue | Customer | SMS ladder | `NT-006` |
| Security | OTP requested | Any | SMS | `NT-007` |
| Security | New device sign-in | Any | SMS + email | `NT-007` |
| Contract | Renewal due | Corporate admin | Email | `NT-010` |
| Warranty | Claim decision | Warranty officer | In-app + email | `NT-013`, `NT-018` |
| Procurement | PO issued | Vendor | Email | `NT-011` |
| Marketplace | Job broadcast | Seller | Push + SMS | `NT-012` |
| Marketplace | Payout released | Seller | SMS + email | `NT-012` |
| Logistics | Manifest assigned | Rider | Push | `NT-017` |
| HR | Certification expiring | Employee + manager | Email | `NT-014` |
| Approval | Approval requested | Approver | Push + email | `NT-022` |
| System | Integration failure | On-call | Alert channel | `NT-021` |
| Feedback | Service completed | Customer | SMS *(delayed)* | `NT-024` |
| Marketing | Campaign | Customer | SMS/email per consent | `NT-023` |

---

## 3. Channel-specific requirements

### 3.1 Bangladesh routing — masking versus non-masking

**This is an operational constraint with commercial consequence, not a technical detail.**

| Traffic type | Route | Sender | Reaches DND numbers? |
|---|---|---|---|
| Transactional — order status, OTP, payment, security | **Masking** (alphanumeric brand sender) | `1000FiX` | **Yes** |
| Promotional — offers, campaigns, reminders to buy | **Non-masking** (numeric sender) | Numeric | **No** |

| # | Rule |
|---|---|
| **BD-01** | **Misclassifying promotional traffic as transactional is a route-suspension risk.** Every template in this category declares its `consent_class`, and the class determines the route |
| **BD-02** | A marketing message never uses the masking route, however useful it would be |
| **BD-03** | An order-status message never carries a promotional line — doing so reclassifies the whole message |
| **BD-04** | Traffic routes through BTRC-listed aggregators only |
| **BD-05** | The masking sender ID is registered and its registration is tracked in `NT-026` |

> **BD-03 is the rule most likely to be broken.** "Your device is ready — and get 20% off your
> next service" is a promotional message wearing a transactional coat. It reaches DND numbers it
> should not, and it puts the transactional route at risk.

### 3.2 Language routing

| Audience | Default | Source |
|---|---|---|
| Customer, seller, rider, technician, branch staff, employee | **Bengali** | `PS-03`, `CG-010` §3.2 |
| Corporate admin | English, Bengali on request | `CG-010` §3.2 |
| Vendor, brand partner, developer | English | `CG-010` §3.2 |

Language is taken from `fix.party.preferred_language` (`MD-013`), defaulting to Bengali.

### 3.3 Cost awareness

Bengali SMS is UCS-2 and segments at **70 characters**, not 160 (`CG-010` BC-05). A template that
is one segment in English may be three in Bengali. Every SMS template records both counts
(`NT-004` §2).

---

## 4. Failure and fallback

| Failure | Behaviour | Template |
|---|---|---|
| SMS undeliverable | Retry once, then fall back to the next channel in the matrix | `NT-025` |
| Push not delivered | Fall back to SMS for `CH-04` events | `NT-025` |
| Email bounces | Flag the address, notify the account owner, fall back to SMS | `NT-025` |
| All channels fail | Raise an operational task; do not silently drop | `NT-025`, `NT-021` |
| Gateway down | Manual fallback per `IP-09` and `OP-014` | `NT-025` |

> **No notifiable event is ever silently dropped.** Where every channel fails, the event becomes
> a task for a human.

---

## 5. Change log and governance

| Item | Value |
|---|---|
| Who may add an event to the matrix | Content Design Lead with the owning module business owner |
| Who may change a channel assignment | Content Design Lead; Legal for any consent-class change |
| Review cadence | Per wave |
| Logged in | `NT-026` and `RF-006` |

### 5.1 Open decisions

| # | Decision | Blocking | Owner |
|---|---|---|---|
| 1 | Is WhatsApp a primary channel or a customer-elected alternative to SMS? | `NT-008` | Content Design Lead + Ops |
| 2 | Masking sender ID registration status and the registered string | `NT-004`, `NT-007` | Platform Engineering |
| 3 | Does the feedback request (`NT-024`) count against the customer frequency cap? | `NT-003`, `NT-024` | Content Design Lead |

---

## 6. Related documents

| Document | Relationship |
|---|---|
| [`NT-002_Notification_Preference_and_Consent_Copy.md`](NT-002_Notification_Preference_and_Consent_Copy.md) | The consent classes this matrix routes on |
| [`NT-003_Quiet_Hours_Throttling_and_Frequency_Policy.md`](NT-003_Quiet_Hours_Throttling_and_Frequency_Policy.md) | Suppression rules |
| [`NT-025_Notification_Failure_and_Fallback_Copy.md`](NT-025_Notification_Failure_and_Fallback_Copy.md) | Fallback wording |
| [`NT-026_Message_Template_Governance_and_Change_Log.md`](NT-026_Message_Template_Governance_and_Change_Log.md) | Template governance |
| `MD-027` Status and Lifecycle State Label Register | Customer-facing status wording |
| `M27` Omnichannel Contact Centre and Communications | The implementing module |

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
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
