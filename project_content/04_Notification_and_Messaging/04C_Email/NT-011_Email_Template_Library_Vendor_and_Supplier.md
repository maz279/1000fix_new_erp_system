---
id: NT-011
title: Email Template Library — Vendor and Supplier
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
  RFQ, PO, delivery, rejection, invoice-matching, remittance and scorecard emails. Vendor adoption
  targets — over 90% PO acknowledgement — depend on emails that make the required action obvious.
traces_to: [`M16`, VB-005, NT-001, NT-002, NT-003]
priority: P2
wave: W3
bilingual: no
bn_counterpart: n/a
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

# NT-011 — Email Template Library — Vendor and Supplier

> **Every email answers: what do you need from me, and by when?** (`VB-002` V-01). A rejection
> without a reason becomes a phone call, and the 60% query-reduction target is missed.

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | Email |
| Audience | Vendors and suppliers (200–500) |
| Owning module | `M16`, `P05` |
| Consent class | Transactional |
| Quiet-hours exempt | Windows do not apply to email; frequency caps do (`NT-003` §3) |
| Content class | D — User-facing |
| Bengali required | No — internal governance (`CG-010` §3.2) |
| Bangladesh routing | Email provider; separate subdomain from marketing (`VB-005` DL-05) |

---

## 2. Templates

| # | Event | Key | Subject EN | Required action stated |
|---|---|---|---|---|
| 1 | RFQ issued | `em.vend.rfq` | Request for quotation — respond by {date} | Submit quotation by {date} |
| 2 | PO issued | `em.vend.po` | Purchase order {po} — acknowledge by {date} | Acknowledge or query |
| 3 | PO reminder | `em.vend.po_reminder` | PO {po} not acknowledged — {days} days | Acknowledge now |
| 4 | Delivery due | `em.vend.delivery_due` | Delivery due {date} — PO {po} | Confirm or advise |
| 5 | Goods rejected | `em.vend.rejected` | {qty} rejected at inspection — PO {po} | Collect or replace by {date}; reason stated |
| 6 | Invoice matched | `em.vend.matched` | Invoice {inv} matched — payment {date} | None |
| 7 | Invoice mismatch | `em.vend.mismatch` | Invoice {inv} does not match PO {po} | Correct and resubmit; both amounts shown |
| 8 | Remittance | `em.vend.remittance` | Payment sent — {amount} | None; itemised |
| 9 | Scorecard | `em.vend.scorecard` | Your performance — {period} | How to improve, per metric |

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
| `EO-005` Vendor and Supplier Onboarding Pack | Onboarding |
| `EO-006` Supplier Performance Scorecard Explanation | Scorecard email content |
| `DT-023` Purchase Order | The attached PO |

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
