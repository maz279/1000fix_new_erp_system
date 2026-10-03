---
id: NT-023
title: Marketing and Lifecycle Campaign Message Library
project: 1000FiX ERP System v2.0
content_type: Notification template library
template: TPL_Notification_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Marketing with Content Design
author: Content Design
reviewers: [Marketing, Legal & Compliance, Localisation Lead, Commercial]
approver: Content Design Lead
content_class: D
purpose: >
  Lifecycle journeys — onboarding, reactivation, AMC renewal, seasonal, cross-sell — across email, SMS
  and push. M35 demand generation needs a governed message set that respects NT-002 consent and
  NT-003 frequency limits rather than competing with them.
traces_to: [M35, M10, NT-001, NT-002, NT-003, MD-030, MD-034, VB-010]
priority: P2
wave: W4
bilingual: yes
bn_counterpart: NT-023_Marketing_and_Lifecycle_Campaign_Message_Library_BN.md
channels: [SMS (non-masking), email, push, WhatsApp (Marketing category)]
consent_class: **Marketing — explicit consent required**
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

# NT-023 — Marketing and Lifecycle Campaign Message Library

> ⚠ **Non-masking route only.** Marketing SMS in Bangladesh travels the numeric-sender route and
> does not reach DND numbers. Sending marketing on the masking route risks the transactional route
> the whole business depends on (`NT-001` BD-01, BD-02).
>
> **Marketing never rides along on a transactional message** (`NT-001` BD-03).

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | SMS (non-masking), email, push, WhatsApp (Marketing category) |
| Audience | Customers who have opted into marketing |
| Owning module | `M35`, `M10` |
| Consent class | **Marketing — explicit consent required** |
| Quiet-hours exempt | 10:00–20:00; suspended on Eid and public holidays (`NT-003` §2.4) |
| Content class | D — User-facing |
| Bengali required | **Yes** — see `BN-014` |
| Bangladesh routing | **Non-masking SMS only** — never the transactional route |

---

## 2. Templates

### 2.1 Lifecycle journeys

| Journey | Trigger | Messages | Channel | Cap |
|---|---|---|---|---|
| Welcome | First service completed | 2 over 14 days | Email, push | Counts to the marketing cap |
| Reactivation | No service for 9 months | 2 over 30 days | SMS, email | 2 per 7 days |
| AMC renewal | 60, 30, 7 days before expiry | 3 | Email, SMS | Service-related, not marketing |
| Seasonal — pre-summer AC | Calendar | 1 | SMS, push | Marketing |
| Cross-sell — protection plan | Repair completed above threshold | 1 after 7 days | Email | Marketing |
| Loyalty tier | Tier achieved or at risk | 1 | Push, email | Service-related |
| Trade-in | Device age threshold | 1 | Email | Marketing |

> **AMC renewal and loyalty tier are classified service-related, not marketing.** They concern an
> agreement the customer already holds. That classification is a `NT-002` decision, not a
> convenience — and it means they reach DND numbers on the masking route.

### 2.2 Templates

| # | Key | Channel | English | Bengali |
|---|---|---|---|---|
| 1 | `mkt.welcome_1` | Email | Thank you for choosing 1000FiX | 1000FiX বেছে নেওয়ার জন্য ধন্যবাদ |
| 2 | `mkt.welcome_2` | Push | Your repair warranty is active for {months} months | আপনার মেরামত ওয়ারেন্টি {months} মাস সক্রিয় |
| 3 | `mkt.reactivate` | SMS | 1000FiX: It has been a while. Book a checkup for your {device} at {link}. Reply STOP to opt out. | 1000FiX: অনেকদিন হলো। {link}-এ আপনার {device}-এর চেকআপ বুক করুন। বন্ধ করতে STOP লিখুন। |
| 4 | `mkt.amc_renewal` | Email | Your {contract} ends on {date} | আপনার {contract} {date}-এ শেষ হচ্ছে |
| 5 | `mkt.seasonal_ac` | SMS | 1000FiX: Summer is coming. Book AC servicing at {link}. Reply STOP to opt out. | 1000FiX: গরম আসছে। {link}-এ এসি সার্ভিসিং বুক করুন। বন্ধ করতে STOP লিখুন। |
| 6 | `mkt.protection` | Email | Extend cover on your {device} | আপনার {device}-এর কভার বাড়ান |
| 7 | `mkt.loyalty_tier` | Push | You are now {tier} | আপনি এখন {tier} |

### 2.3 Rules

| # | Rule |
|---|---|
| **MK-01** | Every marketing SMS carries the **opt-out instruction** (`NT-002` CN-01) |
| **MK-02** | Marketing travels the **non-masking route**, always |
| **MK-03** | Product and plan names are the registered forms from `VB-010`; never invented for a campaign |
| **MK-04** | No superlatives or absolute claims (`CG-013` T-A13) |
| **MK-05** | A customer who complained in the last 30 days is suppressed (`NT-003` FR-04) |
| **MK-06** | A customer with an open service order is suppressed from cross-sell on that device |
| **MK-07** | Campaign names are time-boxed and never reused as product names (`VB-010` CM-02) |

---

## 3. Channel-specific requirements

| Requirement | Rule |
|---|---|
| Consent | Explicit marketing opt-in required (`NT-002`) |
| SMS route | Non-masking; does not reach DND numbers |
| WhatsApp | Marketing category; separately approved and separately priced (`NT-008`) |
| Email | Unsubscribe link mandatory |
| Windows | 10:00–20:00; suspended on Eid and public holidays |
| Cap | 2 per 7 days, within the combined non-transactional cap of 4 |

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
| [`NT-002_Notification_Preference_and_Consent_Copy.md`](NT-002_Notification_Preference_and_Consent_Copy.md) | Consent classes |
| [`NT-003_Quiet_Hours_Throttling_and_Frequency_Policy.md`](NT-003_Quiet_Hours_Throttling_and_Frequency_Policy.md) | Windows and caps |
| `VB-010` Product, Plan and Programme Naming Standard | Registered names |
| `MD-030` Discount, Promotion and Voucher Rule Register | Offer mechanics |

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
- [ ] Meta template category, submission and approval status recorded (`CG-008` NT-f)
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
