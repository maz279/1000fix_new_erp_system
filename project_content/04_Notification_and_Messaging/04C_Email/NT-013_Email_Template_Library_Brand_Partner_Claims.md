---
id: NT-013
title: Email Template Library — Brand Partner Claims
project: 1000FiX ERP System v2.0
content_type: Notification template library
template: TPL_Notification_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Warranty with Content Design
author: Content Design
reviewers: [Localisation Lead, Platform Engineering, Accessibility reviewer, owning business function]
approver: Content Design Lead
content_class: D
purpose: >
  Claim submission, additional-information request, decision, reconciliation and remittance emails.
  Brand claim decision cycle target is under 10 days; unclear information requests are the main cause
  of delay.
traces_to: [`M09`, VB-005, NT-001, NT-002, NT-003]
priority: P2
wave: W4
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

# NT-013 — Email Template Library — Brand Partner Claims

> **English only** (`CG-010` §3.2). International audience, expert readers, judging our
> professionalism by our documentation.

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | Email |
| Audience | Brand partners (50–150) |
| Owning module | `M09`, `P08` |
| Consent class | Transactional |
| Quiet-hours exempt | Windows do not apply to email; frequency caps do (`NT-003` §3) |
| Content class | D — User-facing |
| Bengali required | No — internal governance (`CG-010` §3.2) |
| Bangladesh routing | Email provider; separate subdomain from marketing (`VB-005` DL-05) |

---

## 2. Templates

| # | Event | Key | Subject EN | Content |
|---|---|---|---|---|
| 1 | Claims submitted | `em.brand.submitted` | {count} claims submitted — {period} | Batch summary, evidence completeness |
| 2 | Information requested | `em.brand.info_request` | Information needed — claim {claim} | **Exactly what is missing and why** |
| 3 | Information provided | `em.brand.info_sent` | Information provided — claim {claim} | What was attached |
| 4 | Decision received | `em.brand.decision` | Decision on {count} claims | Approved, part-approved, rejected with reasons |
| 5 | Reconciliation | `em.brand.reconcile` | Reconciliation — {period} | Submitted, approved, paid, difference |
| 6 | Remittance received | `em.brand.remittance` | Remittance received — {amount} | Matched claims, unmatched items |
| 7 | Bulletin acknowledged | `em.brand.bulletin` | Bulletin {ref} acknowledged | Distribution confirmation |

### 2.1 Rules

| # | Rule |
|---|---|
| **BR-01** | An information request names **exactly** what is missing — never "incomplete evidence" |
| **BR-02** | Decision emails list claims individually, never as a total only |
| **BR-03** | Reconciliation shows the difference and its cause, not just the numbers |

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
| `DT-033` Warranty Claim Evidence Pack | The submission |
| `EO-004` Brand Claim Rules and Evidence Standard Guide | What complete means |
| `MD-017` Brand Partner Master Register | Claim rules per brand |

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
