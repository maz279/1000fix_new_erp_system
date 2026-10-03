---
id: NT-008
title: WhatsApp Business Template Library
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
  Every WhatsApp template in the format Meta requires for pre-approval, with variables, categories
  and Bengali versions. Templates must be submitted and approved **before** use; approval lead time
  makes this a schedule dependency, not a content nicety.
traces_to: [M27, 05-03, NT-001, NT-002, NT-003, BN-014]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: NT-008_WhatsApp_Business_Template_Library_BN.md
channels: [WhatsApp]
consent_class: Transactional (Utility) and Marketing — separately categorised
sources:
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M27_Omnichannel_Contact_Centre_and_Communications.md
    verified: 2026-08-15
    class: P1
  - source: project_content/04_Notification_and_Messaging/NT-001 event-channel matrix
    verified: 2026-08-15
    class: P1
  - source: WhatsApp Business Platform template categories 2026 — Marketing, Utility, Authentication and Service; Service replies inside the customer-initiated 24-hour window are free. Templates require Meta approval before use, typically within 24 hours and up to 48 for Marketing in high-demand periods
    verified: 2026-08-15
    class: P3
  - source: Meta template categorisation policy effective April 2025 — a utility template detected as marketing may be recategorised with no advance notice; per-message billing effective July 2025 with rates varying by category and recipient country code
    verified: 2026-08-15
    class: P3
supersedes: none
review_due: 2027-02-15
---

# NT-008 — WhatsApp Business Template Library

> ⚠ **Templates must be approved by Meta before a single message can be sent.** Review is
> typically under 24 hours and up to 48 for Marketing in busy periods.
>
> **The category matters commercially and operationally.** Since 2025 Meta bills per delivered
> message with rates varying by category, and a Utility template detected as Marketing can be
> **recategorised with no advance notice**. A template that smuggles a promotion into a service
> update will be reclassified and repriced.

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | WhatsApp |
| Audience | Customers who have opted into WhatsApp |
| Owning module | `M27` |
| Consent class | Transactional (Utility) and Marketing — separately categorised |
| Quiet-hours exempt | Utility exempt; Marketing per `NT-003` |
| Content class | D — User-facing |
| Bengali required | **Yes** — see `BN-014` |
| Bangladesh routing | Meta Business Platform, not SMS |

---

## 2. Templates

### 2.1 Category assignment

| Meta category | Use | Our templates |
|---|---|---|
| **Utility** | Transactional updates tied to a customer action | Order status, estimate, collection, payment |
| **Authentication** | OTP and login codes | Handled by SMS (`NT-007`); WhatsApp OTP is a future option |
| **Marketing** | Business-initiated promotion | `NT-023` campaigns only |
| **Service** | Replies inside the customer-initiated 24-hour window | Free-form agent replies (`P10`) |

| # | Rule |
|---|---|
| **WA-01** | **Never put promotional content in a Utility template.** It will be recategorised, repriced and possibly warned — the same failure mode as `NT-001` BD-03 |
| **WA-02** | Every template records its submitted category, submission date, approval date and Meta status |
| **WA-03** | A wording change requires **re-approval**. Plan the lead time |
| **WA-04** | Agent replies within the 24-hour service window are free-form and free; use them rather than a template where the customer wrote first |

### 2.2 Utility templates

| # | Name | Category | Body EN | Body BN |
|---|---|---|---|---|
| 1 | `fix_booking_received` | Utility | Your booking is confirmed. Reference {{1}}. We will contact you before {{2}}. | আপনার বুকিং নিশ্চিত হয়েছে। রেফারেন্স {{1}}। আমরা {{2}}-এর আগে যোগাযোগ করব। |
| 2 | `fix_tech_on_way` | Utility | {{1}} is on the way to you. About {{2}} minutes. | {{1}} আপনার কাছে আসছেন। প্রায় {{2}} মিনিট। |
| 3 | `fix_estimate_ready` | Utility | Your repair estimate is {{1}}. Reply APPROVE to start, or call 16743 to discuss. Reference {{2}}. | আপনার মেরামতের এস্টিমেট {{1}}। শুরু করতে APPROVE লিখুন, বা 16743-এ কল করুন। রেফারেন্স {{2}}। |
| 4 | `fix_ready_collect` | Utility | Your {{1}} is ready. Collect from {{2}}, open {{3}}. Reference {{4}}. | আপনার {{1}} প্রস্তুত। {{2}} থেকে সংগ্রহ করুন, খোলা {{3}}। রেফারেন্স {{4}}। |
| 5 | `fix_payment_received` | Utility | We have received {{1}}. Thank you. Reference {{2}}. | আমরা {{1}} পেয়েছি। ধন্যবাদ। রেফারেন্স {{2}}। |
| 6 | `fix_delayed` | Utility | Your repair is taking longer than planned. New expected date {{1}}. Reference {{2}}. | আপনার মেরামত পরিকল্পনার চেয়ে বেশি সময় নিচ্ছে। নতুন প্রত্যাশিত তারিখ {{1}}। রেফারেন্স {{2}}। |

### 2.3 Submission register

| Template | Category submitted | Submitted | Approved | Meta status | Quality rating |
|---|---|---|---|---|---|
| `fix_booking_received` | Utility | *pending* | — | Not submitted | — |
| `fix_tech_on_way` | Utility | *pending* | — | Not submitted | — |
| `fix_estimate_ready` | Utility | *pending* | — | Not submitted | — |
| `fix_ready_collect` | Utility | *pending* | — | Not submitted | — |
| `fix_payment_received` | Utility | *pending* | — | Not submitted | — |
| `fix_delayed` | Utility | *pending* | — | Not submitted | — |

> **Nothing here is approved.** All six are outstanding, and W2 depends on them. Submission is a
> scheduling item, not a launch-week task.

---

## 3. Channel-specific requirements

| Requirement | Rule |
|---|---|
| Approval | Every template pre-approved by Meta before use |
| Variables | Positional `{{1}}`, `{{2}}` — Meta's format, not our named-placeholder standard |
| Named mapping | Each positional variable maps to a named field, documented in §2.2 |
| Quality rating | Monitored; a falling rating restricts sending |
| Opt-in | Required before any template is sent (`NT-002`) |
| 24-hour window | Free-form replies permitted; templates not needed |
| Language | Separate template per language, each approved separately |

> **Meta's positional variables conflict with `UI-001` P-01**, which requires named placeholders.
> The mapping in §2.2 is the bridge; the conflict is recorded rather than resolved, because
> Meta's format is not ours to change.

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
| [`../NT-002_Notification_Preference_and_Consent_Copy.md`](../NT-002_Notification_Preference_and_Consent_Copy.md) | WhatsApp opt-in |
| [`../NT-023_Marketing_and_Lifecycle_Campaign_Message_Library.md`](../NT-023_Marketing_and_Lifecycle_Campaign_Message_Library.md) | Marketing-category templates |
| `05-03` §2.2 | The WhatsApp integration |

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
