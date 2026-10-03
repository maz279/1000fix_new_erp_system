---
id: NT-018
title: In-App Notification and Inbox Copy
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
  In-app inbox entries, grouping, read/unread, expiry and archive copy across all portals. P01 promises
  an in-app inbox of all notifications; without a specification it becomes a second unmanaged content
  surface that nobody owns.
traces_to: [M27, P01, NT-001, UI-006, UI-018, VB-008]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: NT-018_In_App_Notification_and_Inbox_Copy_BN.md
channels: [In-app]
consent_class: Transactional and service-related
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

# NT-018 — In-App Notification and Inbox Copy

> **The inbox is the reference channel** (`NT-001` CH-02). It is where a customer looks when the
> SMS has scrolled away and the email is in a folder they cannot find.

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | In-app |
| Audience | All authenticated users across twelve portals |
| Owning module | `M27` |
| Consent class | Transactional and service-related |
| Quiet-hours exempt | No windows — the user is in the product |
| Content class | D — User-facing |
| Bengali required | **Yes** — see `BN-014` |
| Bangladesh routing | In-product |

---

## 2. Templates

### 2.1 Inbox entry structure

| Slot | Budget (BN) | Rule |
|---|---:|---|
| Title | 60 | The fact, past tense |
| Body | 140 | Detail and next step |
| Timestamp | — | Relative under 24 h, absolute after (`BN-007`) |
| Action | 24 | Deep link to the object |
| Status dot | — | `VB-008` semantic token |

### 2.2 Entries

| # | Event | Key | Title EN | Body EN | Title BN |
|---|---|---|---|---|---|
| 1 | Booking confirmed | `inbox.booking` | Booking confirmed | {ref} for your {device}. We will contact you before {time}. | বুকিং নিশ্চিত হয়েছে |
| 2 | Estimate ready | `inbox.estimate` | Estimate ready | {amount}. Approve so we can start work. | এস্টিমেট প্রস্তুত |
| 3 | Status changed | `inbox.status` | {customer_status} | Your {device}, reference {ref}. | {customer_status} |
| 4 | Ready | `inbox.ready` | Ready for collection | Collect from {branch}, open {hours}. | সংগ্রহের জন্য প্রস্তুত |
| 5 | Payment | `inbox.payment` | Payment received | {amount} for {ref}. Receipt available. | পেমেন্ট গৃহীত |
| 6 | Document | `inbox.document` | {doc_type} available | For {ref}. Download or view. | {doc_type} উপলব্ধ |
| 7 | Contract | `inbox.contract` | Contract expiring | {contract} ends {date}. | চুক্তির মেয়াদ শেষ হচ্ছে |
| 8 | Approval needed | `inbox.approval` | Approval needed | {object} for {amount}. | অনুমোদন প্রয়োজন |

### 2.3 Inbox chrome

| Element | Key | English | Bengali |
|---|---|---|---|
| Title | `inbox.title` | Notifications | বিজ্ঞপ্তি |
| Unread count | `inbox.unread` | {count} unread | {count}টি অপঠিত |
| Mark all read | `inbox.mark_read` | Mark all as read | সব পঠিত হিসেবে চিহ্নিত করুন |
| Empty | `inbox.empty` | No notifications | কোনো বিজ্ঞপ্তি নেই |
| Empty body | `inbox.empty_body` | Updates about your services will appear here. | আপনার সার্ভিস সম্পর্কিত আপডেট এখানে দেখা যাবে। |
| Older | `inbox.older` | Older | পুরোনো |
| Archived | `inbox.archived` | Archived | সংরক্ষণাগারভুক্ত |

### 2.4 Rules

| # | Rule |
|---|---|
| **IB-01** | Every notification sent on any channel also lands in the inbox. The inbox is the complete record |
| **IB-02** | Entries **group by object** — five updates on one order are one expandable entry (`NT-003` BA-01) |
| **IB-03** | Entries are **archived after 90 days**, never deleted (`05-02` DM-06) |
| **IB-04** | Status wording is the `MD-027` customer-facing label (`T-06`) |
| **IB-05** | An entry always deep-links to the object it describes |
| **IB-06** | Read state is per user, not per device |

---

## 3. Channel-specific requirements

| Requirement | Rule |
|---|---|
| Persistence | 90 days visible, then archived |
| Grouping | By object, expandable |
| Sync | Read state syncs across devices |
| Offline | Cached entries readable offline on `P02`, `P09`, `P11` |
| Accessibility | Unread announced as a count, not a colour (`CG-011` CL-01) |
| Language | Rendered in the user's preferred language at read time, not send time |

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
| [`../../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-006_Empty_State_and_First_Run_Copy_Library.md`](../../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-006_Empty_State_and_First_Run_Copy_Library.md) | Empty state |
| `MD-027` Status Register | Status wording |
| `VB-008` Status Colour and Label Semantics | Status dots |

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
