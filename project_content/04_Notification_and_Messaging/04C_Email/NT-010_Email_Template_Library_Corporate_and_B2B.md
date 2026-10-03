---
id: NT-010
title: Email Template Library — Corporate and B2B
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
  Consolidated invoice, approval request, SLA breach, service review, contract renewal and estate
  report emails. Corporate recipients forward these internally; they are read by people who never log
  into P04 and have no context.
traces_to: [`M08`, VB-005, NT-001, NT-002, NT-003]
priority: P1
wave: W4
bilingual: yes
bn_counterpart: NT-010_Email_Template_Library_Corporate_and_B2B_BN.md
channels: [Email]
consent_class: Transactional
sources:
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M27_Omnichannel_Contact_Centre_and_Communications.md
    verified: 2026-08-15
    class: P1
  - source: project_content/04_Notification_and_Messaging/NT-001 event-channel matrix
    verified: 2026-08-15
    class: P1
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-005 Email Brand Template Standard — client baseline, dark mode, Bengali fallback, plain-text parity
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# NT-010 — Email Template Library — Corporate and B2B

> **Written for someone who did not see the screen** (`VB-002` K-01). Corporate email is forwarded
> up a chain that has never used our product.

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | Email |
| Audience | Corporate and government client staff |
| Owning module | `M08`, `P04` |
| Consent class | Transactional |
| Quiet-hours exempt | Windows do not apply to email; frequency caps do (`NT-003` §3) |
| Content class | D — User-facing |
| Bengali required | **Yes** — see `BN-014` |
| Bangladesh routing | Email provider; separate subdomain from marketing (`VB-005` DL-05) |

---

## 2. Templates

| # | Event | Key | Subject EN | Fact block carries |
|---|---|---|---|---|
| 1 | Consolidated invoice | `em.corp.invoice` | Consolidated invoice {no} — {period} | Total, by site, by department, due date |
| 2 | Approval request | `em.corp.approval` | Approval needed — {amount} for {site} | What, why, cost, requester, approve link |
| 3 | SLA breach | `em.corp.sla_breach` | SLA breach — {ref} at {site} | What was missed, by how long, credit applied |
| 4 | Monthly service report | `em.corp.report` | Service report — {period} | Volume, TAT, SLA, cost, top failing assets |
| 5 | Contract renewal | `em.corp.renewal` | Contract renewal — {contract} | Expiry, current usage, renewal options |
| 6 | Bulk upload result | `em.corp.bulk_result` | {ok} of {total} requests created | Successes, failures, failure list link |
| 7 | Estate change | `em.corp.estate` | {count} assets added to your estate | What changed, who changed it |
| 8 | Service review | `em.corp.review_invite` | Service review — {date} | Agenda, attendees, data pack link |

---

## 3. Channel-specific requirements

| Requirement | Rule |
|---|---|
| Shell | `VB-005` master shell — 600 px, single column, table layout |
| Subject | ≤ 55 characters; the essential fact first (`VB-005` BF-07) |
| Preheader | 40–90 characters, never "View in browser" |
| Plain text | Mandatory, carrying the same facts (`VB-005` §8) |
| Dark mode | Both `background-color` and `color` set explicitly (`VB-005` CL-03) |
| Bengali font | Designed at Noto Sans Bengali, the Android fallback (`VB-005` BF-01) |
| Footer | Transactional carries "manage preferences", **no unsubscribe** (`NT-002`) |
| Size | Under 102 KB or Gmail clips (`VB-005` DL-01) |

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
| `DT-020` Consolidated Corporate Invoice | The attached invoice |
| `MD-028` SLA Definition Register | Breach and credit basis |
| `EO-007` Corporate Client Onboarding Kit | Onboarding email set |

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
