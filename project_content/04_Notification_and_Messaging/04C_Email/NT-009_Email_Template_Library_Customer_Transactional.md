---
id: NT-009
title: Email Template Library — Customer Transactional
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
  Welcome, confirmation, status, estimate, invoice, receipt, completion, feedback, cancellation and
  refund emails. The transactional email set is the customer written record of the transaction and
  the reference in any dispute.
traces_to: [`M01`, VB-005, NT-001, NT-002, NT-003]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: NT-009_Email_Template_Library_Customer_Transactional_BN.md
channels: [Email]
consent_class: Transactional — no unsubscribe
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

# NT-009 — Email Template Library — Customer Transactional

> **Email is the record channel** (`NT-001` CH-02). SMS tells them; email is what they still have
> six months later when they query the invoice.

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | Email |
| Audience | Individual customers |
| Owning module | `M01`, `M20` |
| Consent class | Transactional — no unsubscribe |
| Quiet-hours exempt | Windows do not apply to email; frequency caps do (`NT-003` §3) |
| Content class | D — User-facing |
| Bengali required | **Yes** — see `BN-014` |
| Bangladesh routing | Email provider; separate subdomain from marketing (`VB-005` DL-05) |

---

## 2. Templates

| # | Event | Key | Subject EN (≤ 55) | Fact block carries |
|---|---|---|---|---|
| 1 | Welcome | `em.cust.welcome` | Welcome to 1000FiX | Account, how to book, hotline |
| 2 | Booking confirmed | `em.cust.booked` | Booking confirmed — {ref} | Ref, device, mode, slot, branch |
| 3 | Estimate | `em.cust.estimate` | Your repair estimate — {ref} | Diagnosis, line items, total, validity, approve link |
| 4 | Estimate approved | `em.cust.approved` | Estimate approved — {ref} | What was approved, amount, next step |
| 5 | Status update | `em.cust.status` | Update on your repair — {ref} | Current status, expected date |
| 6 | Ready | `em.cust.ready` | Your {device} is ready — {ref} | Branch, hours, amount due, what to bring |
| 7 | Invoice | `em.cust.invoice` | Invoice {invoice_no} — {ref} | Itemised charges, VAT, total, PDF attached |
| 8 | Payment receipt | `em.cust.receipt` | Payment received — {amount} | Amount, method, receipt no., balance |
| 9 | Service complete | `em.cust.complete` | Service complete — {ref} | Work done, parts, warranty, service report |
| 10 | Cancellation | `em.cust.cancelled` | Order cancelled — {ref} | Reason, refund position, next step |
| 11 | Refund | `em.cust.refund` | Refund issued — {amount} | Amount, method, timeline |
| 12 | Feedback | `em.cust.feedback` | How did we do? — {ref} | One question, then optional detail |

### 2.1 Rules

| # | Rule |
|---|---|
| **EC-01** | The **fact block** carries the transactional facts as a table — it is the part that gets screenshotted and forwarded (`VB-005` SH-05) |
| **EC-02** | One primary action per email (`VB-005` SH-01) |
| **EC-03** | The email is comprehensible with images disabled (`VB-005` SH-02) |
| **EC-04** | Invoice emails attach the PDF; the email is never the only copy |
| **EC-05** | No unsubscribe link — a payment receipt is not optional (`NT-002`) |

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
| `VB-005` Email Brand Template Standard | The shell |
| `DT-010` Tax Invoice Mushak 6.3 | The attached invoice |
| `DT-007` Service Completion Report | The attached report |

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
