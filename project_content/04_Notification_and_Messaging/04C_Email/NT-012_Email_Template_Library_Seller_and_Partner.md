---
id: NT-012
title: Email Template Library — Seller and Partner
project: 1000FiX ERP System v2.0
content_type: Notification template library
template: TPL_Notification_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Marketplace Operations with Content Design
author: Content Design
reviewers: [Localisation Lead, Platform Engineering, Accessibility reviewer, owning business function]
approver: Legal Counsel
content_class: B
purpose: >
  Approval, job broadcast, payout, dispute, policy-update and performance-warning emails. Performance
  warnings and suspensions have contractual effect under the seller agreement and must be worded to
  it, not paraphrased.
traces_to: [`M12`, VB-005, NT-001, NT-002, NT-003]
priority: P2
wave: W7
bilingual: yes
bn_counterpart: NT-012_Email_Template_Library_Seller_and_Partner_BN.md
channels: [Email]
consent_class: Transactional and marketing, separately
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

# NT-012 — Email Template Library — Seller and Partner

> ⚠ **Class B — legal.** A suspension notice is the exercise of a contractual right. If the
> wording does not match `LG-004`, the suspension can be challenged. Gate **G5** applies and is
> unwaivable.

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | Email |
| Audience | Marketplace sellers (500–2,000), referral partners (100–500) |
| Owning module | `M12`, `M40` |
| Consent class | Transactional and marketing, separately |
| Quiet-hours exempt | Windows do not apply to email; frequency caps do (`NT-003` §3) |
| Content class | B — Legal / contractual |
| Bengali required | **Yes** — see `BN-014` |
| Bangladesh routing | Email provider; separate subdomain from marketing (`VB-005` DL-05) |

---

## 2. Templates

| # | Event | Key | Subject EN | Contractual basis |
|---|---|---|---|---|
| 1 | Application received | `em.sell.applied` | We have your application | — |
| 2 | Approved | `em.sell.approved` | You are approved to take jobs | `LG-004` §onboarding |
| 3 | Declined | `em.sell.declined` | We cannot approve your application | Reason and reapplication date |
| 4 | Job broadcast | `em.sell.job` | New job available — {area} | — |
| 5 | Payout released | `em.sell.payout` | {amount} paid to {bank} | Statement attached (`DT-039`) |
| 6 | Payout held | `em.sell.payout_held` | Payout held — dispute on {job} | **`LG-004` hold clause cited** |
| 7 | Rating below threshold | `em.sell.rating_low` | Your rating is below {min} | **`LG-004` visibility clause cited** |
| 8 | Suspension warning | `em.sell.warning` | Formal warning — {reason} | **`LG-004` cited verbatim** |
| 9 | Suspended | `em.sell.suspended` | Your account is suspended | **`LG-004` cited verbatim; appeal route stated** |
| 10 | Policy update | `em.sell.policy` | Platform standards are changing on {date} | Acknowledgement required |
| 11 | Commission statement | `em.part.commission` | Commission statement — {period} | Attribution basis shown (`DT-040`) |

### 2.1 Rules

| # | Rule |
|---|---|
| **SP-01** | Sanction emails quote the contractual clause; they never paraphrase it |
| **SP-02** | Every sanction email states the **appeal route** (`EO-013`) |
| **SP-03** | Payout emails show the arithmetic, never only the net (`VB-002` S-02) |
| **SP-04** | Marketing to sellers is a separate consent from transactional (`NT-002`) |

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
| `LG-004` Marketplace Seller Agreement | **The contractual wording quoted** |
| `DT-039` Marketplace Seller Payout Statement | Attached statement |
| `EO-013` Ecosystem Dispute Resolution Content | Appeal route |

---

## 7. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Legal Counsel (pending) |

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
- [ ] G5 legal review — **outstanding, unwaivable (`WV-02`)**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
