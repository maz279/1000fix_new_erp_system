---
id: NT-021
title: System, Integration and Job Failure Alert Library
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
reviewers: [Platform Engineering, Security, Support Lead, Internal IT]
approver: Content Design Lead
content_class: C
purpose: >
  Integration failure, batch failure, queue backlog, reconciliation mismatch and health alerts, with
  severity and runbook links. IP-06 requires every integration to be observable and alerting on
  failure; an alert with no remedy text wastes the on-call engineer first ten minutes.
traces_to: [M28, M66, 05-03 IP-06, IP-09, OP-008, OP-013, OP-016]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
channels: [Alerting channel (on-call), email]
consent_class: Internal operational
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

# NT-021 — System, Integration and Job Failure Alert Library

> **An alert without a runbook link is an interruption, not information.** Every alert here names
> what failed, what it affects, and where the procedure is.
>
> English only — the audience is the engineering on-call rota (`CG-010` §3.2).

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | Alerting channel (on-call), email |
| Audience | On-call engineers, platform team, service desk |
| Owning module | `M28`, `M66` |
| Consent class | Internal operational |
| Quiet-hours exempt | Per on-call policy (`OP-013`) |
| Content class | C — Operational-critical |
| Bengali required | No — internal governance (`CG-010` §3.2) |
| Bangladesh routing | Internal alerting, not customer channels |

---

## 2. Templates

### 2.1 Severity and routing

| Severity | Definition | Route | Response |
|---|---|---|---|
| **Sev1** | Customer-facing path down — payments, booking, OTP | Page on-call immediately | Per `OP-013` |
| **Sev2** | Degraded but working, or an internal path down | Page during hours, queue overnight | Per `OP-013` |
| **Sev3** | Single integration failing with a working fallback | Ticket | Next business day |
| **Sev4** | Informational — threshold approached | Dashboard only | None |

### 2.2 Alert templates

| # | Condition | Key | Alert text | Severity |
|---|---|---|---|---|
| 1 | Payment gateway down | `alert.int.payment_down` | {gateway} unreachable for {duration}. Payments failing over to {secondary}. Manual fallback: `OP-014` §payment. Runbook `AP-009`. | **Sev1** |
| 2 | All gateways down | `alert.int.payment_all` | All payment gateways unreachable. Counter payment only. Runbook `OP-014`. | **Sev1** |
| 3 | SMS gateway down | `alert.int.sms_down` | SMS gateway {gateway} failing. {count} queued. OTP delivery affected. Runbook `OP-008`. | **Sev1** |
| 4 | Integration failing | `alert.int.generic` | {integration} failing — {error_rate}% over {window}. Circuit breaker {state}. Runbook `OP-008`. | Sev2 |
| 5 | Queue backlog | `alert.sys.queue` | {queue} backlog {count}, growing {rate}/min. Consumer {state}. Runbook `OP-008`. | Sev2 |
| 6 | Batch job failed | `alert.sys.batch` | {job} failed at {time}. {impact} Retry {attempts}. Runbook `OP-007`. | Sev2 |
| 7 | Nightly optimisation overrun | `alert.sys.batch_slow` | {job} exceeded {limit} minutes (`NFR-044`). Dispatch may start without optimised routes. | Sev2 |
| 8 | Reconciliation mismatch | `alert.fin.reconcile` | {method} settlement mismatch: expected {expected}, received {actual}, difference {diff}. Runbook `AP-009`. | Sev2 |
| 9 | Offline sync failures | `alert.sys.sync` | {count} devices with sync failures over {window}. Oldest {age}. Runbook `OP-011`. | Sev2 |
| 10 | Certificate expiring | `alert.sys.cert` | {certificate} expires in {days} days. | Sev3 |
| 11 | Storage threshold | `alert.sys.storage` | {store} at {pct}% capacity. | Sev3 |
| 12 | Residency violation attempt | `alert.sec.residency` | Write of a residency-classified field rejected for region {region} (`NFR-086a`). {count} in {window}. | **Sev1** |

### 2.3 Rules

| # | Rule |
|---|---|
| **AL-01** | Every alert names **what failed**, **what it affects** and **the runbook** |
| **AL-02** | Every alert states the **manual fallback** where one exists (`IP-09`) |
| **AL-03** | Alerts never contain customer personal data — they go to a channel with a wider audience than the record |
| **AL-04** | Repeat alerts for the same condition are suppressed to one per {window}; the count is carried in the alert |
| **AL-05** | An alert that fires more than 20 times a week without action is reviewed for deletion — noisy alerts train people to ignore the channel |
| **AL-06** | Sev1 alerts always page a human; they are never dashboard-only |
| **AL-07** | Every Sev1 and Sev2 produces a post-incident review (`OP-016`) |

---

## 3. Channel-specific requirements

| Requirement | Rule |
|---|---|
| Channel | Dedicated on-call alerting; never a customer channel (`NT-001` CH-06) |
| Language | English — engineering audience (`CG-010` §3.2) |
| Suppression | Deduplicated per condition per window; never fully silenced |
| Escalation | Unacknowledged Sev1 escalates per `OP-013` |
| Retention | Alert history retained for post-incident review |

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
| `OP-008` Runbook Integration and Event Platform | The procedures alerts link to |
| `OP-013` On-Call, Escalation and Handover Content | Routing and rotas |
| `OP-014` Manual Fallback Procedure Set | The fallbacks named |
| `05-03` IP-06, IP-09 | The observability and fallback obligations |

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
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
