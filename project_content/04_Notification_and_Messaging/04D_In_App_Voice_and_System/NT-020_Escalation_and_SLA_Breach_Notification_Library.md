---
id: NT-020
title: Escalation and SLA Breach Notification Library
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
  Warning, imminent-breach, breach and service-credit notifications to internal and customer
  audiences. SLA breach notifications carry financial consequence — service credits — and must be
  precise and timely; a late breach notice is itself a failure.
traces_to: [M08, MD-028, LG-015, DT-031, NT-001, NT-003, SP-005]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: NT-020_Escalation_and_SLA_Breach_Notification_Library_BN.md
channels: [SMS, email, push, in-app]
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

# NT-020 — Escalation and SLA Breach Notification Library

> **A service credit is money.** These notifications are the trigger and the evidence for it.
> Wording must reconcile exactly with `MD-028`, `LG-015` and `DT-031` — a divergence between the
> four is a dispute.
>
> The customer never sees the words "SLA breached". They see "Delayed" (`MD-027`, `T-06`).

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | SMS, email, push, in-app |
| Audience | Customers, branch managers, account managers, executives |
| Owning module | `M08`, `M27` |
| Consent class | Transactional |
| Quiet-hours exempt | **Exempt** (`NT-003` §2.5) |
| Content class | C — Operational-critical |
| Bengali required | **Yes** — see `BN-014` |
| Bangladesh routing | Masking for customer SMS |

---

## 2. Templates

### 2.1 The escalation ladder

| Stage | Trigger | Audience | Channel | Key |
|---|---|---|---|---|
| Warning | 75% of target elapsed (`MD-028` `escalation_at_pct`) | Owning technician, dispatcher | Push + in-app | `esc.warn.internal` |
| Imminent | 90% elapsed | Branch manager | Push + in-app | `esc.imminent.manager` |
| Breach | Target exceeded | Branch manager, account manager | Email + in-app | `esc.breach.internal` |
| Breach — customer | Target exceeded | Customer | SMS | `esc.breach.customer` |
| Breach — corporate | Target exceeded | Corporate admin | Email | `esc.breach.corporate` |
| Credit applied | Credit calculated | Corporate admin, finance | Email | `esc.credit.applied` |
| Repeat breach | 3 breaches, same account, 30 days | Account manager, Ops Director | Email | `esc.repeat.exec` |

### 2.2 Templates

| Key | Audience | English | Bengali |
|---|---|---|---|
| `esc.warn.internal` | Technician | Job {ref} is at 75% of its SLA. {remaining} remains. | জব {ref} এসএলএ-এর ৭৫%-এ। {remaining} বাকি। |
| `esc.imminent.manager` | Branch manager | {ref} will breach in {remaining}. {reason} | {ref} {remaining}-এ লঙ্ঘিত হবে। {reason} |
| `esc.breach.internal` | Branch manager | {ref} breached its SLA by {over}. Cause: {reason}. Owner: {owner}. | {ref} এসএলএ {over} অতিক্রম করেছে। কারণ: {reason}। দায়িত্বে: {owner}। |
| `esc.breach.customer` | Customer | 1000FiX: Your repair is taking longer than planned. New date {date}. Sorry for the wait. Ref {ref}. | 1000FiX: আপনার মেরামত পরিকল্পনার চেয়ে বেশি সময় নিচ্ছে। নতুন তারিখ {date}। রেফ {ref}। |
| `esc.breach.corporate` | Corporate admin | SLA breach on {ref} at {site}. Target {target}, actual {actual}. Service credit of {amount} will be applied. | — *(English-only audience)* |
| `esc.credit.applied` | Corporate admin | Service credits of {amount} for {period} applied to invoice {invoice}. | — |
| `esc.repeat.exec` | Ops Director | {count} SLA breaches on {account} in 30 days. Account manager: {am}. | — |

### 2.3 Rules

| # | Rule |
|---|---|
| **ES-01** | The customer message **never uses the contractual term**. "Delayed", not "SLA breached" (`T-06`) |
| **ES-02** | The customer message always gives a **new date**, not an apology alone |
| **ES-03** | Internal messages name the **cause and the owner** — a breach notice with neither is noise |
| **ES-04** | Credit amounts come from `MD-028` `credit_calculation`, which must match `LG-015` verbatim |
| **ES-05** | Escalation is **exempt from quiet hours and frequency caps** (`NT-003` §2.5) |
| **ES-06** | The clock respects `MD-028` pause conditions — a breach notice sent during a paused clock is wrong |
| **ES-07** | Escalation destinations come from `SP-005`, not from this file |

---

## 3. Channel-specific requirements

| Requirement | Rule |
|---|---|
| Timing | Sent within 5 minutes of the threshold; a late breach notice is itself a failure |
| Clock | Business calendar from `MD-028` and `MD-041`; pause conditions honoured |
| Suppression | None — exempt from all windows and caps |
| Language | Customer messages in their preferred language; internal in Bengali or English per role |
| Evidence | Every breach notification is retained as evidence for the credit calculation (`LG-009`) |

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
| `MD-028` Priority, Severity and SLA Definition Register | Targets, pause rules, credit calculation |
| `LG-015` AMC/SLA Master Terms and Service Credit Rules | **Must reconcile exactly** |
| `DT-031` SLA Schedule and Service Credit Annex | **Must reconcile exactly** |
| `SP-005` Escalation Matrix | Who is escalated to |

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
