---
id: NT-026
title: Message Template Governance and Change Log
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
reviewers: [Platform Engineering, Legal & Compliance, Security, Localisation Lead]
approver: Content Design Lead
content_class: E
purpose: >
  Template ownership, version history, approval record, WhatsApp re-approval triggers and retirement.
  Templates are edited by many hands under commercial pressure; an unlogged change to an OTP or an
  invoice message is a security and audit incident.
traces_to: [M27, CG-006, CG-007, NT-001, NT-007, NT-008, RF-006]
priority: P1
wave: W2
bilingual: no
bn_counterpart: n/a
channels: [All channels]
consent_class: n/a — governance
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

# NT-026 — Message Template Governance and Change Log

> **Every message this company sends is a template with an owner and a version.** Without that,
> nobody can answer "what did we actually send that customer, and who approved it?"
>
> This file is the register. It is English-only internal governance (`CG-010` §3.2).

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | All channels |
| Audience | Content Design, Platform Engineering, Legal |
| Owning module | `M27` |
| Consent class | n/a — governance |
| Quiet-hours exempt | n/a |
| Content class | E — Internal governance |
| Bengali required | No — internal governance (`CG-010` §3.2) |
| Bangladesh routing | Records the masking sender registration |

---

## 2. Templates

### 2.1 What is registered

Every template in `NT-004`…`NT-024` carries a row here:

| Field | Purpose |
|---|---|
| `template_id` | The key, e.g. `sms.cust.ready` |
| `library` | Owning `NT` file |
| `channel` | SMS, WhatsApp, email, push, in-app, voice |
| `consent_class` | Transactional, service-related, marketing, security |
| `sms_route` | Masking or non-masking, where applicable |
| `version` | Per `CG-006` §2 |
| `approved_by` / `approved_on` | Per `CG-007` |
| `bn_signed_off_by` / `bn_signed_off_on` | Per `BN-018` |
| `meta_category` / `meta_status` | WhatsApp only |
| `en_segments` / `bn_segments` | SMS only |
| `first_sent` / `retired_on` | Lifecycle |

### 2.2 Change triggers

| Change | Consequence |
|---|---|
| Any wording change | New version; re-approval per content class |
| A change to a **security** template (`NT-007`) | Security review **and** Content Design Lead approval. Never a routine edit |
| A change to a **Class B** template (`NT-006`, `NT-012`) | G5 legal review, unwaivable |
| A change crossing an **SMS segment boundary** | Content Design Lead approval; cost impact recorded |
| Any change to a **WhatsApp** template | **Meta re-approval required.** Plan the lead time (`NT-008` WA-03) |
| A change to `consent_class` | Legal and DPO review; the SMS route changes with it |
| Retirement | Template marked retired; the ID is never reused (`CG-005` `ID-03`) |

### 2.3 The change log

| Date | Template | From → to | Reason | Approved by | Segment impact |
|---|---|---|---|---|---|
| 2026-08-15 | — | Initial issue of all libraries | Category 04 authoring | *pending* | Baseline recorded in `NT-004` §2.3 |

> The log starts empty by design. Every subsequent change adds a row.

### 2.4 Governance rules

| # | Rule |
|---|---|
| **TG-01** | A template not registered here **may not be sent**. Register-first (`CM-R1`) |
| **TG-02** | A template's `consent_class` determines its SMS route; changing one changes the other (`NT-001` BD-01) |
| **TG-03** | Security templates (`NT-007`) are change-controlled as security artefacts, not as copy |
| **TG-04** | WhatsApp templates track Meta status separately from our approval status — both must be current |
| **TG-05** | Retired template IDs are never reused |
| **TG-06** | The masking sender ID registration and its renewal date are recorded here |
| **TG-07** | Every change is also logged in `RF-006` |

### 2.5 Sender registrations

| Item | Value | Status |
|---|---|---|
| Masking sender ID | `1000FiX` *(to confirm)* | **Registration status outstanding** — `NT-001` §5.1 open decision 2 |
| Non-masking sender | Numeric, aggregator-allocated | Outstanding |
| WhatsApp Business number | — | Outstanding |
| Email sending domain — transactional | Separate subdomain (`VB-005` DL-05) | Outstanding |
| Email sending domain — marketing | Separate subdomain and IP | Outstanding |

---

## 3. Channel-specific requirements

| Item | Rule |
|---|---|
| Ownership | Content Design Lead owns the register; each library owner owns their templates |
| Audit | Verified at every wave audit against the libraries on disk |
| Retention | Retired templates retained for the retention period of the records they produced (`LG-009`) |
| Evidence | Approval evidence per `CG-007` §4.2 |

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
| `CG-006` Content Lifecycle and Versioning Policy | Version rules |
| `CG-007` Review, Approval and Sign-off Workflow | Approval gates |
| [`04B_WhatsApp_and_Push/NT-008_WhatsApp_Business_Template_Library.md`](04B_WhatsApp_and_Push/NT-008_WhatsApp_Business_Template_Library.md) | Meta status tracking |
| `RF-006` Content Decision Log | Where changes are also logged |

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
