---
id: OP-005
title: Status Page and Maintenance Notice Copy
project: 1000FiX ERP System v2.0
content_type: Notification template library
template: TPL_Notification_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Support Lead
author: Content Design with Support Lead and Platform Engineering
reviewers: [Content Design Lead, Chief Technology Officer, Operations Director, Contact Centre Supervisor, Account Management, Marketplace Ops, Localisation Lead, Legal Counsel]
approver: Content Design Lead
content_class: D
purpose: >
  Names every component that appears on the public and internal status page in the words users
  use, fixes the component and incident states, and provides the planned-maintenance notice copy
  that NFR-049 requires 72 hours in advance. Without it, the status page either says nothing
  useful ("API degraded") or says too much, and planned maintenance is announced differently by
  each team — which trains 51+ branches and 250,000+ customers to ignore the announcement.
traces_to: [05-06 NFR-049, NFR-006, NFR-045, NFR-046, NFR-048, M27, M28, P01, P02, P04, P05, P07, P08, P09, P12, OP-004, OP-011, OP-013, HC-015, UI-005]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: OP-005_Status_Page_and_Maintenance_Notice_Copy_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-049 — planned maintenance outside 08:00–23:00 BST, ≤ 4 h per month, announced 72 h ahead
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-006 uptime ≥ 99.9% (09:00–22:00 BST), NFR-045 24×7 ≥ 99.7%, NFR-046 customer portal ≥ 99.9%, NFR-048 payment path ≥ 99.95%, NFR-008 zero-downtime deployment as the standard
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — the twelve portals and their audiences
    verified: 2026-08-20
    class: P1
  - source: Atlassian Statuspage — incident lifecycle states (investigating, identified, monitoring, resolved) and component status hierarchy (operational, degraded performance, partial outage, major outage, under maintenance). https://support.atlassian.com/statuspage/docs/top-level-status-and-incident-impact-calculations/
    verified: 2026-08-20
    class: P3
  - source: PagerDuty, "Status page best practices" — acknowledge within 10–15 minutes of detection; always state the next update time. https://www.pagerduty.com/resources/outages/learn/status-page-best-practices/
    verified: 2026-08-20
    class: P3
supersedes: none
review_due: 2027-02-20
---

# OP-005 — Status Page and Maintenance Notice Copy

> **A status page is a promise that you will tell people before they have to ask.** It is read
> at the worst moment, usually on a phone, often on 3G, frequently in Bengali. Every word on it
> must be understandable by someone who does not know what an API is and does not care.

---

## 1. Set Summary

| Item | Value |
|---|---|
| Channel(s) | Public status page · internal status page · email and SMS subscription · in-app banner ([`UI-005`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-005_System_Permission_and_Session_Message_Library.md)) · portal login-screen notice |
| Audience | Consumers, branch and field staff, corporate clients, sellers, vendors, brand and referral partners — **eleven external populations plus internal** ([`OP-001`](OP-001_Support_Model_Tiering_and_Routing_Content.md) §4.1) |
| Owning module | `M28` (health signals), `M27` (subscriber delivery) |
| Consent class | Service-critical; subscription is opt-in and is **not** marketing consent |
| Quiet-hours exempt | Incident notices yes; maintenance reminders no (sent 09:00–20:00 BST) |
| Content class | **D — User-facing** |
| Bengali required | **Yes** — every component name, state, incident and maintenance notice |
| Bangladesh routing | SMS masked `1000FiX`; page served over the public website domain |

---

## 2. Templates

### 2.1 The component register

Components are named for **what a user is trying to do**, never for the technology behind it. The
right-hand column is what must *not* appear.

| # | Component (English) | Component (Bengali) | Covers | Never displayed as |
|---:|---|---|---|---|
| 1 | Booking a service | সার্ভিস বুকিং | `P01` booking, availability, slot selection | "Booking API", "M01" |
| 2 | Customer app and website | গ্রাহক অ্যাপ ও ওয়েবসাইট | `P01` sign-in, order history, tracking | "Next.js frontend" |
| 3 | Payments | পেমেন্ট | All gateways (`INT-001`…`INT-004`), payment links | Gateway brand names, unless one specific gateway is affected |
| 4 | Job tracking and technician location | কাজের ট্র্যাকিং ও টেকনিশিয়ানের অবস্থান | Tracking page, live map (`INT-023`) | "Traccar" |
| 5 | Technician app | টেকনিশিয়ান অ্যাপ | `P02`, offline sync | "Flutter app" |
| 6 | Rider and delivery app | রাইডার ও ডেলিভারি অ্যাপ | `P09` | — |
| 7 | Branch and workshop systems | শাখা ও ওয়ার্কশপ সিস্টেম | `P03`, intake, job cards, printing | "Odoo" |
| 8 | Invoices and receipts | ইনভয়েস ও রসিদ | Document generation, Mushak output | "Document service" |
| 9 | Notifications — SMS, WhatsApp, email | নোটিফিকেশন — এসএমএস, হোয়াটসঅ্যাপ, ইমেল | `M27` outbound | "Novu", gateway names |
| 10 | Corporate portal | কর্পোরেট পোর্টাল | `P04` | — |
| 11 | Vendor portal | ভেন্ডর পোর্টাল | `P05` | — |
| 12 | Marketplace seller portal | মার্কেটপ্লেস সেলার পোর্টাল | `P07` | — |
| 13 | Brand partner portal | ব্র্যান্ড পার্টনার পোর্টাল | `P08` | — |
| 14 | Partner and referral portal | পার্টনার ও রেফারেল পোর্টাল | `P12` | — |
| 15 | Contact centre and hotline 16743 | কন্টাক্ট সেন্টার ও হটলাইন ১৬৭৪৩ | `P10`, telephony (`INT-015`) | "CPaaS" |
| 16 | Reports and dashboards | রিপোর্ট ও ড্যাশবোর্ড | `P06`, Metabase-served reporting | "Metabase", "ClickHouse" |
| 17 | Sign-in and accounts | সাইন-ইন ও অ্যাকাউন্ট | Identity, OTP, MFA (`M29`) | "Keycloak" |

> **`SC-01`.** A component appears on the **public** page only if an external population uses it
> directly. Components 7 and 16 appear on the **internal** page only. The two pages share this
> register and differ only in which rows they render.

### 2.2 Component states

| State (English) | State (Bengali) | Means | Set by |
|---|---|---|---|
| **Operational** | স্বাভাবিক | Working as expected | Automatic health check (`M28`) |
| **Degraded performance** | ধীরগতি | Working, but slower than normal or with retries | Automatic threshold (`05-03` §7) or Incident Commander |
| **Partial outage** | আংশিক বিভ্রাট | Some users or some functions cannot complete the task | Incident Commander |
| **Major outage** | সম্পূর্ণ বিভ্রাট | The component cannot be used | Incident Commander |
| **Under maintenance** | রক্ষণাবেক্ষণ চলছে | Planned, announced work | Scheduled, automatic |

**Overall page state** is the worst state of any displayed component; it is never softened.
"Degraded" while payments are in major outage is a false statement, and it is the specific
failure that makes users stop trusting status pages.

### 2.3 Incident states

| State (English) | State (Bengali) | Says to the reader |
|---|---|---|
| **Investigating** | অনুসন্ধান চলছে | We can see the symptom; we do not yet know the cause |
| **Identified** | কারণ শনাক্ত | We know the cause and are working on the fix |
| **Monitoring** | পর্যবেক্ষণে | The fix is in and we are watching to be sure |
| **Resolved** | সমাধান হয়েছে | Verified working; the record stays published |

These four map one-to-one to `{state}` in [`OP-004`](OP-004_Incident_Communication_Template_Set.md) templates 9 and 11. **No fifth state exists.**

### 2.4 Incident notices

| # | Template ID | Phase | English | Bengali |
|---:|---|---|---|---|
| 1 | `st.inc.investigating` | Investigating | **{component} — investigating.** Some users cannot {action}. We are investigating and will update by {next}. | **{component} — অনুসন্ধান চলছে।** কিছু ব্যবহারকারী {action} করতে পারছেন না। আমরা খুঁজে দেখছি এবং {next}-এর মধ্যে জানাব। |
| 2 | `st.inc.identified` | Identified | **{component} — cause identified.** {plain_cause}. We are applying a fix. In the meantime you can {alternative}. Next update {next}. | **{component} — কারণ শনাক্ত।** {plain_cause}। আমরা সমাধান প্রয়োগ করছি। এর মধ্যে আপনি {alternative} করতে পারেন। পরবর্তী আপডেট {next}। |
| 3 | `st.inc.monitoring` | Monitoring | **{component} — fix applied, monitoring.** {component} should now work normally. We are watching it for {duration} before calling it resolved. | **{component} — সমাধান প্রয়োগ, পর্যবেক্ষণে।** {component} এখন স্বাভাবিকভাবে কাজ করার কথা। সমাধান ঘোষণার আগে আমরা {duration} সময় পর্যবেক্ষণ করছি। |
| 4 | `st.inc.resolved` | Resolved | **{component} — resolved.** Affected from {start} to {end} ({duration}). {retry_advice}. A summary will be published here by {pir_date}. | **{component} — সমাধান হয়েছে।** {start} থেকে {end} পর্যন্ত ({duration}) প্রভাবিত ছিল। {retry_advice}। {pir_date}-এর মধ্যে এখানে একটি সারাংশ প্রকাশ করা হবে। |
| 5 | `st.inc.partial` | Partial | **{component} — partial outage.** {who_affected} are affected; {who_not} are not. {alternative}. Next update {next}. | **{component} — আংশিক বিভ্রাট।** {who_affected} প্রভাবিত; {who_not} প্রভাবিত নন। {alternative}। পরবর্তী আপডেট {next}। |
| 6 | `st.inc.degraded` | Degraded | **{component} — slower than usual.** Everything works but may take longer. No action is needed. Next update {next}. | **{component} — স্বাভাবিকের চেয়ে ধীর।** সবকিছু কাজ করছে তবে সময় বেশি লাগতে পারে। কিছু করার দরকার নেই। পরবর্তী আপডেট {next}। |
| 7 | `st.inc.summary` | Post-incident | **{date} — what happened.** {plain_cause} meant {impact} for {duration}. We have {actions}. | **{date} — কী ঘটেছিল।** {plain_cause}-এর কারণে {duration} সময় {impact}। আমরা {actions} করেছি। |

### 2.5 Planned maintenance notices

`NFR-049` sets three constraints that the copy must honour every time: **outside 08:00–23:00 BST**,
**no more than 4 hours in a calendar month**, and **announced 72 hours ahead**. `NFR-008` makes
zero-downtime deployment the standard, so a maintenance window that takes the service down is
itself an exception worth explaining.

| # | Template ID | When | English | Bengali |
|---:|---|---|---|---|
| 8 | `st.mnt.notice_72h` | 72 h before | **Planned maintenance — {date}, {start}–{end} (about {duration}).** {component} will be unavailable. During this time you can {alternative}, and anything you submit afterwards will process normally. We schedule this outside working hours to affect as few people as possible. | **নির্ধারিত রক্ষণাবেক্ষণ — {date}, {start}–{end} (প্রায় {duration})।** এই সময়ে {component} ব্যবহার করা যাবে না। আপনি {alternative} করতে পারেন, এবং পরে জমা দেওয়া সবকিছু স্বাভাবিকভাবে প্রক্রিয়া হবে। যত কম মানুষ প্রভাবিত হন সেজন্য আমরা কাজের সময়ের বাইরে এটি রাখি। |
| 9 | `st.mnt.reminder_24h` | 24 h before | **Reminder: maintenance tomorrow {start}–{end}.** {component} will be unavailable. If you need to {critical_task}, do it before {start}. | **মনে করিয়ে দিচ্ছি: আগামীকাল {start}–{end} রক্ষণাবেক্ষণ।** {component} বন্ধ থাকবে। {critical_task} করার প্রয়োজন হলে {start}-এর আগে সেরে নিন। |
| 10 | `st.mnt.started` | At start | **Maintenance in progress.** {component} is unavailable until about {end}. | **রক্ষণাবেক্ষণ চলছে।** প্রায় {end} পর্যন্ত {component} বন্ধ থাকবে। |
| 11 | `st.mnt.completed` | At end | **Maintenance complete.** {component} is back and has been checked. It finished {early_late}. {what_changed}. | **রক্ষণাবেক্ষণ সম্পন্ন।** {component} ফিরে এসেছে এবং যাচাই করা হয়েছে। এটি {early_late} শেষ হয়েছে। {what_changed}। |
| 12 | `st.mnt.overrun` | If the window overruns | **Maintenance is taking longer than planned.** {component} is still unavailable. We now expect it back by {new_end}. Next update {next}. | **রক্ষণাবেক্ষণে পরিকল্পনার চেয়ে বেশি সময় লাগছে।** {component} এখনও বন্ধ। আমরা এখন {new_end}-এর মধ্যে ফিরে আসার আশা করছি। পরবর্তী আপডেট {next}। |
| 13 | `st.mnt.cancelled` | If cancelled | **Maintenance on {date} is cancelled.** No action is needed and nothing will be unavailable. It will be rescheduled and re-announced with 72 hours' notice. | **{date}-এর রক্ষণাবেক্ষণ বাতিল করা হয়েছে।** কিছু করার দরকার নেই এবং কিছুই বন্ধ থাকবে না। এটি পুনঃনির্ধারিত হবে এবং ৭২ ঘণ্টা আগে আবার জানানো হবে। |
| 14 | `st.mnt.emergency` | Emergency maintenance (< 72 h notice) | **Emergency maintenance — {date}, {start}–{end}.** We are making an urgent change to {reason_category}. We would normally give 72 hours' notice; this cannot wait. {component} will be unavailable. | **জরুরি রক্ষণাবেক্ষণ — {date}, {start}–{end}।** {reason_category}-এর জন্য আমরা একটি জরুরি পরিবর্তন করছি। সাধারণত আমরা ৭২ ঘণ্টা আগে জানাই; এটি অপেক্ষা করতে পারে না। {component} বন্ধ থাকবে। |
| 15 | `st.mnt.app_release` | Mobile release with forced upgrade | **App update required — {date}.** Version {version} of the {app} must be installed to keep working. Update from {store} before {date}; the app will prompt you. The update takes about {minutes} minutes and can be done on mobile data. | **অ্যাপ আপডেট প্রয়োজন — {date}।** কাজ চালিয়ে যেতে {app}-এর {version} সংস্করণ ইনস্টল করতে হবে। {date}-এর আগে {store} থেকে আপডেট করুন; অ্যাপ নিজেই মনে করিয়ে দেবে। আপডেটে প্রায় {minutes} মিনিট লাগে এবং মোবাইল ডেটাতেই করা যায়। |

> **`MN-01`.** Emergency maintenance (template 14) states a **reason category** — "a security fix",
> "a fault that is losing data", "a supplier requirement" — never the vulnerability, never the
> defect detail. Publishing the specific reason for an urgent security change is publishing the
> exploit window.

### 2.6 Subscription and audience copy

| # | Template ID | Surface | English | Bengali |
|---:|---|---|---|---|
| 16 | `st.sub.invite` | Status page header | Get told before you notice. Subscribe for {component} updates by SMS or email — incidents and planned maintenance only, never marketing. | সমস্যা টের পাওয়ার আগেই জেনে নিন। এসএমএস বা ইমেলে {component}-এর আপডেট নিন — কেবল সমস্যা ও নির্ধারিত রক্ষণাবেক্ষণ, কখনও বিজ্ঞাপন নয়। |
| 17 | `st.sub.confirm` | On subscribe | You will now receive updates about {component}. Unsubscribe any time from the link in every message. | এখন থেকে {component} সম্পর্কে আপডেট পাবেন। প্রতিটি বার্তার লিঙ্ক থেকে যেকোনো সময় বন্ধ করতে পারেন। |
| 18 | `st.page.allclear` | No open incidents | All services are operating normally. Last checked {time}. | সব সেবা স্বাভাবিকভাবে চলছে। সর্বশেষ যাচাই {time}। |
| 19 | `st.page.history` | History section | We publish every incident, including the ones nobody noticed. Ninety days of history is below. | আমরা প্রতিটি ঘটনা প্রকাশ করি — যেগুলি কেউ খেয়ালও করেনি সেগুলিও। নিচে নব্বই দিনের ইতিহাস। |

### 2.7 Rules

| # | Rule |
|---|---|
| **SP-01** | **The status page never contains a technology name, a hostname, an error code or a vendor name** — except where naming one gateway (e.g. "bKash payments") is the only accurate description of what is affected |
| **SP-02** | **Every incident notice states what the user can still do.** A notice with no alternative is an announcement of helplessness |
| **SP-03** | **Every open notice states the next update time**, and that time is met. A missed update time damages trust more than the outage |
| **SP-04** | Bengali and English publish **simultaneously**. The page renders both; it does not choose based on browser locale alone ([`BN-013`](../11_Localisation_Bengali/BN-013_Bengali_String_Bundle_P07_to_P12.md) locale rules) |
| **SP-05** | **The page is updated by the Incident Commander or the Communications Owner only** (`OP-004` `IC-01`) |
| **SP-06** | An incident visible to users is published **even if it lasted four minutes**. Selective publication is discovered and is worse than the incident |
| **SP-07** | Resolved incidents remain published for **90 days minimum**; the post-incident summary is added when [`OP-016`](OP-016_Post_Incident_Review_Template_and_Register.md) completes |
| **SP-08** | Uptime figures are published **only** against the definitions in `05-06` (`NFR-006` business hours, `NFR-045` 24×7, `NFR-046` customer portal, `NFR-048` payment path). A single blended "uptime" figure is prohibited — it is not comparable to any commitment the company has made |
| **SP-09** | **Maintenance is never described as an "improvement" if it is a fix.** Users can tell |
| **SP-10** | The page must be **hosted independently of the ERP estate**. A status page that shares infrastructure with the system it reports on is unavailable exactly when it is needed (`OP-004` §4) |
| **SP-11** | Corporate clients with contractual notification rights are told **directly by their account manager as well** (`OP-004` template 6); the page does not discharge a contractual duty |
| **SP-12** | The internal page shows the same states in the same words as the public page. Two vocabularies produce two beliefs |

---

## 3. Channel-Specific Requirements

| Channel | Requirement |
|---|---|
| Public status page | Must load under 400 KB (`NFR-081`) and render on 3G. No fonts, images or scripts from the ERP estate. Bengali renders with the standard web font stack ([`VB-006`](../01_Voice_Brand_and_Design_Content/VB-006_Design_System_Content_Standards.md)) |
| Internal status page | Adds components 7 and 16; otherwise identical |
| SMS subscription | Bengali segments at 70 characters (UCS-2). Only templates 1, 4, 8, 10, 11 have SMS short forms |
| Email subscription | Plain-text parity; the unsubscribe link in every message |
| In-app banner | Sourced from the same state feed as the page, never hand-written twice (`CP-01`) |
| Login-screen notice | Shown before authentication, so users locked out by an identity incident can still read it ([`OP-009`](OP-009_Runbook_Identity_and_Access.md) §5) |
| Voice hold message (`P10`) | Updated at declaration and resolution only; script per [`NT-019`](../04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-019_IVR_and_Voice_Prompt_Scripts.md) |

**Accessibility ([`CG-011`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md)):** each component row carries the state **as text**, not colour alone;
state icons carry text alternatives; the page is operable at 200% zoom and by keyboard.

---

## 4. Failure and Fallback

| Failure mode | User-visible behaviour | Fallback |
|---|---|---|
| Status page host unavailable | No status information anywhere | Public website banner (`P01` marketing site) + SMS to subscribers + hotline hold message |
| Automatic health feed wrong (page green, service down) | Users are told nothing is wrong while it is | The Incident Commander overrides state manually; the false-green condition is itself a `Sev2` and a mandatory PIR item (`OP-016`) |
| Subscription delivery fails (`M27` affected) | Subscribers not notified | Page remains authoritative; branch telephone tree for internal ([`OP-013`](OP-013_On_Call_Escalation_and_Handover_Content.md) §4.10) |
| Bengali fails to render | Boxes on the page in an incident | Publish English immediately with a Bengali follow-up within 10 minutes; log as a defect against `BN-013` |
| Maintenance overruns the `NFR-049` monthly budget | Users experience unannounced-feeling downtime | Template 12, and the overrun is recorded against the monthly 4-hour allowance in the change record ([`SP-031`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md)) |

---

## 5. Change Log

| Version | Date | Change | Approver | WhatsApp re-approval needed |
|---|---|---|---|:--:|
| 1.0 | 2026-08-20 | Initial set — 17 components, 5 component states, 4 incident states, 19 templates | Content Design Lead (pending) | No — status notices are not WhatsApp templates |

---

## Open Items

1. **OP-005-OI-01** — Bengali requires **G4 in-context review** on the rendered page ([`BN-018`](../11_Localisation_Bengali/BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md)),
   not on this table.
2. **OP-005-OI-02** — **Status page independence (`SP-10`) is unconfirmed.** No hosting decision
   exists; `02-05` §8 does not provision it. Until it does, the page is a dependency of the estate
   it reports on.
3. **OP-005-OI-03** — Component 3 "Payments" aggregates nine integrations. Confirm with Finance
   whether a single gateway outage should be published per gateway (more honest, more alarming) or
   as degraded payments (calmer, less precise). Recommendation: **per gateway**, because customers
   experience gateways by name.
4. **OP-005-OI-04** — `SP-08` prohibits a blended uptime figure. Confirm that Marketing and Sales
   accept this before any uptime figure appears in a proposal or on the website.
5. **OP-005-OI-05** — The 4-hour monthly maintenance allowance (`NFR-049`) has no owner tracking it
   across teams. Proposed owner: change manager under `SP-031`; unconfirmed.
6. **OP-005-OI-06** — Wave alignment: this file is `W2`, but `OP-004` (W1) and [`OP-014`](OP-014_Manual_Fallback_Procedure_Set.md) (W1) both
   depend on a status page existing. Either the page is needed at W1, or W1 incident comms run
   without it. Raised in the Category 17 audit.

---

## Definition of Done

Tick every box before setting `status: Approved`. Full checklist in [`CG-008`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md).

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Notification_Template.md` — all five sections present; `Open Items` added, justified
- [x] Every factual, statutory, pricing or capability claim carries a source and a verification date
- [x] Terminology matches [`CG-004`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md); component names follow [`BN-003`](../11_Localisation_Bengali/BN-003_Bilingual_Terminology_Glossary.md)
- [x] All internal links resolve
- [x] Accessibility standard `CG-011` applied — states as text, zoom and keyboard operable
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **open, OI-01**
- [ ] Named approver recorded — Content Design Lead, appointment pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] Decision(s) taken while authoring logged in `RF-006` — six open items pending

**Gates required (Class D):** G1 ●, G2 ●, G3 ●, G4 ● (bilingual).

---

*`OP-005` · 1000FiX ERP Programme · CONFIDENTIAL — Internal Use Only*
