---
id: OP-004
title: Incident Communication Template Set
project: 1000FiX ERP System v2.0
content_type: Notification template library
template: TPL_Notification_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Support Lead with Communications
author: Content Design with Support Lead, Platform Engineering and Legal
reviewers: [Chief Technology Officer, Operations Director, Legal Counsel, Data Protection Officer, Contact Centre Supervisor, Account Management, Change Lead, Localisation Lead]
approver: Content Design Lead
content_class: D
purpose: >
  The pre-written notices for every phase of an incident — declaration, update, workaround,
  resolution and post-incident summary — at each severity, for internal staff, customers,
  corporate clients, ecosystem partners and, where the law requires it, the authorities. During an
  outage there is no time to compose, and every minute spent drafting is a minute the affected
  population spends inventing an explanation. Templates are written when calm.
traces_to: [M27, M29, M60, P10, 05-06 NFR-072, NFR-094, OP-005, OP-013, OP-016, OP-012, LG-010, LG-024, NT-021, NT-025]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: OP-004_Incident_Communication_Template_Set_BN.md
sources:
  - source: project_content/04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-021_System_Integration_and_Job_Failure_Alert_Library.md §2.1 severity and routing, §2.3 AL-01…AL-07
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-072 security incident response with defined severities and breach-notification assessment; NFR-094 notify the National Data Management Authority of a breach likely to cause significant damage, within the prescribed timeframe
    verified: 2026-08-20
    class: P1
  - source: Personal Data Protection Act 2026 (Bangladesh) — breach notification to the Authority where significant damage is likely; **the notification period is set by regulations, which are not yet published**. Overview: https://securiti.ai/bangladesh-personal-data-protection-act-overview/
    verified: 2026-08-20
    class: P3
  - source: Cyber Security Ordinance 2025 (Bangladesh), in force 21 May 2025 — declared Critical Information Infrastructure must operate its own incident response capability and report through the national CIRT/NCERT structure. https://www.mondaq.com/new-technology/1659100/cyber-security-ordinance-2025-implications-for-businesses-in-bangladesh
    verified: 2026-08-20
    class: P3
  - source: Atlassian, "Learn incident communication with Statuspage" — investigating/identified/monitoring/resolved lifecycle and update cadence practice. https://www.atlassian.com/incident-management/tutorials/incident-communication
    verified: 2026-08-20
    class: P3
supersedes: none
review_due: 2027-02-20
---

# OP-004 — Incident Communication Template Set

> **The first message sets the tone for the whole incident.** If it is late, people invent an
> explanation; if it speculates, the correction is remembered longer than the incident; if it
> comes from four people, nobody believes any of them.
>
> **One voice, one channel of record, one next-update time — always stated.**

---

## 1. Set Summary

| Item | Value |
|---|---|
| Channel(s) | Internal broadcast · email · SMS · push · in-app banner · status page ([`OP-005`](OP-005_Status_Page_and_Maintenance_Notice_Copy.md)) · WhatsApp · voice (`P10` hold message) · formal letter (regulator, corporate client) |
| Audience | Internal staff · consumers · corporate clients · sellers, vendors, brand and referral partners · regulators and the Authority |
| Owning module | `M27` (delivery), `M29`/`M60` (security and regulatory judgement) |
| Consent class | Service-critical — exempt from marketing consent, **not** exempt from channel rules |
| Quiet-hours exempt | **Yes for `Sev1`**; `Sev2` and below observe [`NT-003`](../04_Notification_and_Messaging/NT-003_Quiet_Hours_Throttling_and_Frequency_Policy.md) quiet hours unless the recipient is on-call |
| Content class | **D — User-facing** |
| Bengali required | **Yes** for every internal, customer, technician, branch, rider and seller notice |
| Bangladesh routing | SMS masked `1000FiX`; WhatsApp session rules per [`NT-008`](../04_Notification_and_Messaging/04B_WhatsApp_and_Push/NT-008_WhatsApp_Business_Template_Library.md) |

**Template ID format:** `inc.<audience>.<phase>` where phase ∈ `declare`, `update`, `workaround`,
`resolve`, `summary`, `notify`.

---

## 2. Templates

### 2.0 The communication matrix

Who is told, by whom, on what channel, at what point. **This matrix is the file.** The wording
that follows is the execution of it.

| Severity ([`OP-013`](OP-013_On_Call_Escalation_and_Handover_Content.md) §4.1) | Internal staff | Affected customers | Corporate clients | Ecosystem partners | Status page | Authority / regulator |
|:--:|---|---|---|---|---|---|
| **Sev1** | Immediately on declaration (≤ 15 min) | ≤ 30 min from declaration where customer-facing | ≤ 60 min, by account manager, **named** | ≤ 60 min if their flow is affected | **Yes**, ≤ 15 min | Only on assessment (§2.6) |
| **Sev2** | ≤ 30 min | Only if customer-visible | Only if their service is affected | Only if their flow is affected | Yes, if customer-visible | On assessment |
| **Sev3** | Ticket update only | No | No | No | Only if a workaround is user-visible | No |
| **Sev4** | No | No | No | No | No | No |
| **Any, with personal data involvement** | Per above **plus** DPO immediately | Per DPO instruction only — **never by support judgement** | Per DPO and Legal | Per DPO and Legal | Per DPO | **Assessment mandatory** (§2.6) |

| # | Rule |
|---|---|
| **IC-01** | **One sender.** During an incident, the Communications Owner ([`OP-002`](OP-002_Hypercare_Plan_and_Exit_Criteria.md) §4.5) is the only person who issues external messages, and the Incident Commander is the only source of fact. Everyone else links to the status page |
| **IC-02** | **Every message states the time of the next message.** This is the single most effective practice in incident communication and it is mandatory here |
| **IC-03** | **No speculation about cause.** Until the cause is confirmed, the message says what is affected and what to do, not why it happened |
| **IC-04** | **No blame** — not the vendor, not a named engineer, not "a third party" in a way that identifies one before the facts are settled |
| **IC-05** | **No ETA unless it is known.** "We do not yet have a restoration time; the next update is at {time}" is always better than a guess that passes |
| **IC-06** | **Bengali and English are issued together**, not English first. A Bengali-reading branch that receives English 20 minutes early has been told nothing |
| **IC-07** | The status page (`OP-005`) is the **single source of truth**. Every other channel points at it rather than restating detail that will change |
| **IC-08** | **Customer notification of a personal-data incident is never a support decision.** It is the DPO's, on Legal's advice ([`LG-010`](../10_Legal_Policy_and_Compliance/LG-010_Data_Subject_Request_Handling_Content.md)) |
| **IC-09** | Resolution is announced **once the fix is verified**, not when it is deployed |
| **IC-10** | Every `Sev1` and `Sev2` produces a post-incident summary ([`OP-016`](OP-016_Post_Incident_Review_Template_and_Register.md)), and the summary is published to the audience that received the declaration |

### 2.1 Declaration

| # | Template ID | Audience | English | Bengali |
|---:|---|---|---|---|
| 1 | `inc.int.declare_sev1` | All internal | **Sev1 incident {inc_ref} declared {time}.** Affected: {affected}. Not affected: {unaffected}. What to do now: {action}. Manual fallback: {fallback_ref}. Incident Commander: {ic}. Updates every 30 minutes here and at {status_link}. Next update {next}. | **সেভ১ ইনসিডেন্ট {inc_ref} ঘোষিত {time}।** প্রভাবিত: {affected}। প্রভাবিত নয়: {unaffected}। এখন যা করবেন: {action}। বিকল্প পদ্ধতি: {fallback_ref}। ইনসিডেন্ট কমান্ডার: {ic}। প্রতি ৩০ মিনিটে এখানে ও {status_link}-এ আপডেট। পরবর্তী আপডেট {next}। |
| 2 | `inc.int.declare_sev2` | Affected internal teams | **Sev2 incident {inc_ref}.** {affected} is degraded — it works but is {symptom}. Keep working; if you cannot complete {task}, use {fallback_ref}. Next update {next}. | **সেভ২ ইনসিডেন্ট {inc_ref}।** {affected} ধীর/আংশিক কাজ করছে — চালু আছে তবে {symptom}। কাজ চালিয়ে যান; {task} সম্পন্ন করতে না পারলে {fallback_ref} ব্যবহার করুন। পরবর্তী আপডেট {next}। |
| 3 | `inc.cust.declare` | Consumers | We are having a problem with {service} and are working on it now. You can still {alternative}. Your bookings and payments already made are safe. Live updates: {status_link}. Next update by {next}. | {service}-এ আমাদের একটি সমস্যা হচ্ছে এবং আমরা এখনই কাজ করছি। আপনি এখনও {alternative} করতে পারেন। আপনার করা বুকিং ও পেমেন্ট নিরাপদ আছে। সরাসরি আপডেট: {status_link}। পরবর্তী আপডেট {next}-এর মধ্যে। |
| 4 | `inc.tech.declare` | Field technicians | {service} is down. **Keep working — the app stores everything offline.** Do not reinstall the app and do not sign out; signing out loses unsynced work. {action}. Next update {next}. | {service} বন্ধ আছে। **কাজ চালিয়ে যান — অ্যাপ সব কিছু অফলাইনে জমা রাখে।** অ্যাপ আবার ইনস্টল করবেন না এবং সাইন আউট করবেন না; সাইন আউট করলে সিঙ্ক না হওয়া কাজ হারিয়ে যাবে। {action}। পরবর্তী আপডেট {next}। |
| 5 | `inc.branch.declare` | Branch and front desk | {service} is unavailable at all branches. Switch to {fallback_ref} now — the forms are in the branch fallback pack. Keep serving customers. Record every transaction on paper with the customer's mobile number. Next update {next}. | সব শাখায় {service} বন্ধ আছে। এখনই {fallback_ref}-এ যান — ফর্মগুলি শাখার ফলব্যাক প্যাকে আছে। গ্রাহকদের সেবা দেওয়া চালিয়ে যান। প্রতিটি লেনদেন গ্রাহকের মোবাইল নম্বরসহ কাগজে লিখুন। পরবর্তী আপডেট {next}। |
| 6 | `inc.corp.declare` | Corporate clients (account manager sends) | {client}, we are managing an incident affecting {service} since {time}. Your open tickets are {status}. Our commitment to you under {contract_ref} is unaffected in respect of {unaffected}. I will update you personally at {next} whether or not there is news. — {am}, Account Manager, {phone} | {client}, {time} থেকে {service}-এ একটি ইনসিডেন্ট আমরা সামলাচ্ছি। আপনার চলমান টিকিটের অবস্থা {status}। {contract_ref} অনুযায়ী {unaffected} বিষয়ে আমাদের প্রতিশ্রুতি অপরিবর্তিত। খবর থাকুক বা না থাকুক, {next}-এ আমি নিজে আপনাকে জানাব। — {am}, অ্যাকাউন্ট ম্যানেজার, {phone} |
| 7 | `inc.sell.declare` | Marketplace sellers | {service} is affected since {time}. Your jobs in progress are safe and your payouts are unaffected. Do not resubmit anything — duplicates take longer to clear. Updates: {status_link}. Next update {next}. | {time} থেকে {service} প্রভাবিত। আপনার চলমান কাজ নিরাপদ এবং পে-আউট অপরিবর্তিত। কিছু আবার জমা দেবেন না — ডুপ্লিকেট ঠিক করতে বেশি সময় লাগে। আপডেট: {status_link}। পরবর্তী আপডেট {next}। |
| 8 | `inc.vend.declare` | Vendors, brand partners | We are managing an incident affecting {service} since {time}. Purchase orders and claims already submitted are held safely and will process when service resumes. No action is needed from you. Next update {next}. | *English only ([`CG-010`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) §3.3)* |

### 2.2 Update

| # | Template ID | Audience | English | Bengali |
|---:|---|---|---|---|
| 9 | `inc.int.update` | All internal | **{inc_ref} update {time}.** State: {state}. What we know: {known}. What we are doing: {doing}. What has changed since the last update: {delta}. Still use {fallback_ref}. Next update {next}. | **{inc_ref} আপডেট {time}।** অবস্থা: {state}। যা জানি: {known}। যা করছি: {doing}। গত আপডেটের পর যা বদলেছে: {delta}। এখনও {fallback_ref} ব্যবহার করুন। পরবর্তী আপডেট {next}। |
| 10 | `inc.int.update_nonews` | All internal | **{inc_ref} update {time}.** No change since {last}. The team is still working on {doing}; we are not yet able to give a restoration time. Next update {next}. | **{inc_ref} আপডেট {time}।** {last} থেকে কোনো পরিবর্তন নেই। টিম এখনও {doing} নিয়ে কাজ করছে; পুনরুদ্ধারের সময় এখনও বলতে পারছি না। পরবর্তী আপডেট {next}। |
| 11 | `inc.cust.update` | Consumers | Update {time}: we have found what is causing this and are fixing it. {impact_now}. You can still {alternative}. Next update by {next}. | আপডেট {time}: সমস্যার কারণ আমরা খুঁজে পেয়েছি এবং সমাধান করছি। {impact_now}। আপনি এখনও {alternative} করতে পারেন। পরবর্তী আপডেট {next}-এর মধ্যে। |
| 12 | `inc.int.escalate_notice` | Leadership | {inc_ref} has been running {duration} and is now escalated to {level} per `OP-013`. Business impact so far: {impact}. Decisions needed from you: {decisions}. Joining details: {bridge}. | {inc_ref} {duration} ধরে চলছে এবং `OP-013` অনুযায়ী এখন {level}-এ এসকেলেট করা হয়েছে। এ পর্যন্ত ব্যবসায়িক প্রভাব: {impact}। আপনার কাছ থেকে যে সিদ্ধান্ত দরকার: {decisions}। যোগ দেওয়ার তথ্য: {bridge}। |

### 2.3 Workaround and degraded operation

| # | Template ID | Audience | English | Bengali |
|---:|---|---|---|---|
| 13 | `inc.int.workaround` | Affected staff | While we fix this, do it this way: {steps}. This is temporary and safe — the records you create now are reconciled automatically when service returns. Do **not** {prohibited}, because that creates duplicates we then have to unpick. | সমাধান না হওয়া পর্যন্ত এভাবে করুন: {steps}। এটি সাময়িক ও নিরাপদ — এখন তৈরি করা রেকর্ড সেবা ফিরলে স্বয়ংক্রিয়ভাবে মিলিয়ে নেওয়া হবে। {prohibited} **করবেন না**, এতে ডুপ্লিকেট তৈরি হয় যা পরে আমাদের ঠিক করতে হয়। |
| 14 | `inc.cust.workaround` | Consumers | While we fix this you can {alternative} — it works normally. If you prefer to wait, nothing is lost and your place is kept. | সমাধানের সময় পর্যন্ত আপনি {alternative} করতে পারেন — এটি স্বাভাবিকভাবে কাজ করছে। অপেক্ষা করতে চাইলে কিছুই হারাবে না, আপনার স্থান সংরক্ষিত থাকবে। |
| 15 | `inc.int.payment_fallback` | Branch and cashier | Card and mobile payments are unavailable. Take **cash at counter only**, issue the manual money receipt from the fallback pack, record the receipt number against the job, and hand the customer the carbon copy. Do not promise a digital receipt today. | কার্ড ও মোবাইল পেমেন্ট বন্ধ আছে। **কেবল কাউন্টারে নগদ** নিন, ফলব্যাক প্যাক থেকে ম্যানুয়াল মানি রসিদ দিন, কাজের বিপরীতে রসিদ নম্বর লিখুন এবং গ্রাহককে কার্বন কপি দিন। আজ ডিজিটাল রসিদের প্রতিশ্রুতি দেবেন না। |

### 2.4 Resolution

| # | Template ID | Audience | English | Bengali |
|---:|---|---|---|---|
| 16 | `inc.int.resolve` | All internal | **{inc_ref} resolved {time}.** {service} is working normally and has been verified. Duration {duration}. What you need to do: {catchup_action}. Anything queued during the incident has been processed — check {check}. A post-incident review will be published by {pir_date}. | **{inc_ref} সমাধান হয়েছে {time}।** {service} স্বাভাবিকভাবে কাজ করছে এবং যাচাই করা হয়েছে। স্থায়িত্ব {duration}। আপনাকে যা করতে হবে: {catchup_action}। ইনসিডেন্টের সময় জমে থাকা কাজ প্রক্রিয়া করা হয়েছে — {check} দেখে নিন। {pir_date}-এর মধ্যে পোস্ট-ইনসিডেন্ট রিভিউ প্রকাশ করা হবে। |
| 17 | `inc.cust.resolve` | Consumers | This is now working again. It was affected from {start} to {end}. Anything you tried during that time may need doing once more — {what_to_retry}. Thank you for your patience, and we are sorry it happened. | এটি এখন আবার কাজ করছে। {start} থেকে {end} পর্যন্ত এটি প্রভাবিত ছিল। ওই সময়ে আপনি যা চেষ্টা করেছেন তা হয়তো আরেকবার করতে হবে — {what_to_retry}। ধৈর্যের জন্য ধন্যবাদ, এবং এটি ঘটার জন্য আমরা দুঃখিত। |
| 18 | `inc.corp.resolve` | Corporate clients | {client}, {service} was restored at {end}. Total duration {duration}. Effect on your service: {client_impact}. Against {contract_ref} this {does/does not} constitute a service credit event; {finance_action}. The post-incident review will be sent to you by {pir_date}. — {am} | {client}, {end}-এ {service} পুনরুদ্ধার হয়েছে। মোট স্থায়িত্ব {duration}। আপনার সেবায় প্রভাব: {client_impact}। {contract_ref} অনুযায়ী এটি সার্ভিস ক্রেডিট ঘটনা {does/does not}; {finance_action}। {pir_date}-এর মধ্যে পোস্ট-ইনসিডেন্ট রিভিউ আপনাকে পাঠানো হবে। — {am} |
| 19 | `inc.int.partial_resolve` | All internal | **{inc_ref} partially resolved {time}.** {restored} is working. {still_affected} is still affected and is now tracked as {new_ref}. Keep using {fallback_ref} for that part only. Next update {next}. | **{inc_ref} আংশিক সমাধান {time}।** {restored} কাজ করছে। {still_affected} এখনও প্রভাবিত এবং এখন {new_ref} হিসেবে ট্র্যাক হচ্ছে। কেবল ওই অংশের জন্য {fallback_ref} ব্যবহার করুন। পরবর্তী আপডেট {next}। |

### 2.5 Post-incident summary

| # | Template ID | Audience | English | Bengali |
|---:|---|---|---|---|
| 20 | `inc.int.summary` | All internal | **{inc_ref} — what happened.** On {date}, {plain_cause} meant that {impact} for {duration}. We fixed it by {fix}. To stop it recurring we are {actions}, owned by {owners}, by {dates}. Full review: {pir_link}. Nobody is named in this summary and nobody will be — the review is blameless by policy. | **{inc_ref} — কী ঘটেছিল।** {date} তারিখে {plain_cause}-এর কারণে {duration} সময় ধরে {impact}। আমরা {fix} করে ঠিক করেছি। যাতে আবার না ঘটে সেজন্য {dates}-এর মধ্যে {owners}-এর দায়িত্বে {actions} করা হচ্ছে। পূর্ণ রিভিউ: {pir_link}। এই সারাংশে কারও নাম নেই এবং থাকবে না — নীতি অনুযায়ী রিভিউ দোষারোপমুক্ত। |
| 21 | `inc.cust.summary` | Consumers (`Sev1` only) | On {date}, {service} was unavailable for {duration}. The cause was {plain_cause}. We have {actions} so that this does not happen again. If this affected a booking or a payment of yours and it has not been put right, contact us at {route} quoting {inc_ref}. | {date} তারিখে {duration} সময় ধরে {service} ব্যবহার করা যায়নি। কারণ ছিল {plain_cause}। যাতে এটি আর না ঘটে সেজন্য আমরা {actions} করেছি। এতে আপনার কোনো বুকিং বা পেমেন্ট প্রভাবিত হয়ে থাকলে এবং তা ঠিক না হয়ে থাকলে {inc_ref} উল্লেখ করে {route}-এ যোগাযোগ করুন। |

### 2.6 Regulatory and authority notification

> **These templates are drafted by Legal and issued by the Data Protection Officer or the CTO.
> Support never issues them and never adapts them.** They exist here so that the *timing* is
> operationally visible during an incident, not so that support can send them.

| # | Template ID | Recipient | Trigger | Content skeleton |
|---:|---|---|---|---|
| 22 | `inc.notify.authority_assess` | Internal — DPO, Legal, CTO | Any incident with possible personal-data exposure | Incident reference · data categories possibly affected · population and estimated count · whether the data includes Sensitive Personally Identifiable Data (`NFR-099`: NID, passport, TIN, biometric) · residency of the affected store (`NFR-086`) · containment state · **assessment of whether significant damage is likely** · decision and decision-maker · time of decision |
| 23 | `inc.notify.authority` | National Data Management Authority | DPO assesses that significant damage is likely (`NFR-094`) | Controller identity and contact · nature of the breach · categories and approximate number of data subjects and records · likely consequences · measures taken and proposed · DPO contact · **submitted within the period prescribed by regulations** |
| 24 | `inc.notify.cirt` | BGD e-GOV CIRT / national CERT structure | A cyber incident within the Cyber Security Ordinance 2025 reporting expectation | Incident classification · systems affected · detection time and method · indicators · containment · assistance requested |
| 25 | `inc.notify.subject` | Affected data subjects | On DPO instruction only, following `LG-010` | What happened in plain language · what data · what it means for them · what we have done · what they should do · a named contact · **no technical detail that assists a further attack** |
| 26 | `inc.notify.client_contract` | Corporate client (contractual duty) | Where the client contract requires incident notification | Per the notification clause of the executed agreement — periods vary per contract and are held in [`LG-003`](../10_Legal_Policy_and_Compliance/LG-003_Portal_Terms_of_Use_Corporate.md) |

| # | Rule |
|---|---|
| **RN-01** | The **assessment** in template 22 is mandatory for every incident involving personal data, whether or not it results in a notification. The record of a decision *not* to notify is as important as a notification |
| **RN-02** | **The clock starts at detection, not at confirmation.** Any delay in assessment is itself recorded |
| **RN-03** | The PDPA 2026 notification period is **set by regulations that are not yet published** (verified 2026-08-20). Until Legal confirms it, the programme's working assumption is stated in [`LG-024`](../10_Legal_Policy_and_Compliance/LG-024_Regulatory_Disclosure_and_Statutory_Notice_Register.md) and is treated as **72 hours from detection** — a conservative planning figure, **not a legal statement**. This assumption must be replaced, not inherited |
| **RN-04** | Notification templates are Class A/B content owned by Legal (`LG-024`), reproduced here as skeletons only. **Nothing in §2.6 may be sent from this file** |
| **RN-05** | Where the Company is (or becomes) declared Critical Information Infrastructure under the Cyber Security Ordinance 2025, template 24 becomes a standing obligation with its own SOC reporting cadence — currently **not determined**; open item OI-03 |

### 2.7 Variables

| Variable | Source | Notes |
|---|---|---|
| `{inc_ref}` | Incident register (`OP-013`) | `INC-YYYY-nnnn` |
| `{ic}` | Incident Commander on the rota | Named person, always |
| `{state}` | Status-page state (`OP-005`) | Investigating / Identified / Monitoring / Resolved |
| `{next}` | Absolute time, never "shortly" | e.g. `16:30 BST` |
| `{fallback_ref}` | [`OP-014`](OP-014_Manual_Fallback_Procedure_Set.md) procedure code | e.g. `FB-07` |
| `{status_link}` | `OP-005` status page | — |
| `{pir_link}`, `{pir_date}` | `OP-016` register | — |
| `{contract_ref}` | Client agreement (`LG-003`) | Corporate templates only |
| `{plain_cause}` | Written for a non-technical reader | Never a stack trace, never a vendor name before facts settle |

---

## 3. Channel-Specific Requirements

| Channel | Requirement |
|---|---|
| Internal broadcast | Primary internal channel; must not depend on the failing system. If the incident affects the ERP itself, the broadcast goes by SMS and the out-of-band channel named in `OP-013` §4.10 |
| SMS | `Sev1` only. Bengali segments at 70 characters (UCS-2) — declaration templates have 2-segment short forms held in [`NT-025`](../04_Notification_and_Messaging/NT-025_Notification_Failure_and_Fallback_Copy.md) |
| Push | Title ≤ 40 characters, body ≤ 120; deep-links to the in-app incident banner, not to a broken screen |
| In-app banner | Persistent while the incident is open; the only surface that must be updated at every state change |
| Email | Plain-text parity mandatory; subject carries `{inc_ref}` and severity |
| WhatsApp | Only within an open 24-hour session, or via an approved template (`NT-008`). **`Sev1` customer notices cannot rely on WhatsApp** for this reason |
| Voice (`P10`) | Hold message updated at declaration and at resolution; script in [`NT-019`](../04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-019_IVR_and_Voice_Prompt_Scripts.md) |
| Status page (`OP-005`) | The system of record for external state. Every other channel links to it |
| Letter | Regulator and corporate contractual notices only; issued by Legal on letterhead |

**Accessibility ([`CG-011`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md)):** severity is never conveyed by colour alone; every banner carries the
severity word and the state word.

---

## 4. Failure and Fallback

| Failure mode | User-visible behaviour | Fallback |
|---|---|---|
| The incident affects the notification platform itself (`M27`/Novu) | No messages send | Out-of-band channel per `OP-013` §4.10 — SMS via the failover gateway (`INT-011`), then telephone tree to branch managers |
| Status page is hosted on the affected infrastructure | The page is down during the incident it exists for | **Design requirement:** the status page must be hosted independently of the ERP estate (`OP-005` §3). Until confirmed, `Sev1` external comms fall back to SMS and the public website |
| Bengali message fails to render | Boxes or mojibake in a `Sev1` notice | Send English immediately, Bengali within 10 minutes with an apology line; log as a `Sev2` in its own right |
| Incident Commander unreachable mid-incident | Communication stops | `OP-013` §4.6 succession; the Communications Owner may issue the "no change" template (10) on their own authority for one cycle only |
| Conflicting message already sent by a manager | Two versions circulating | Correction template, issued once, without naming the sender; `IC-01` reinforced in the PIR |

---

## 5. Change Log

| Version | Date | Change | Approver | WhatsApp re-approval needed |
|---|---|---|---|:--:|
| 1.0 | 2026-08-20 | Initial set — 26 templates across six phases and six audiences, plus the communication matrix | Content Design Lead (pending) | Yes — customer declaration and resolution templates need WhatsApp template approval before they can be used outside a session (`NT-008`) |

---

## Open Items

1. **OP-004-OI-01** — Bengali requires **G4 in-context review** ([`BN-018`](../11_Localisation_Bengali/BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md)) before use.
2. **OP-004-OI-02** — WhatsApp template pre-approval for templates 3, 11, 17 has not been
   submitted; without it, customer `Sev1` notice by WhatsApp is unavailable outside an open session.
3. **OP-004-OI-03** — Whether 1000FiX is or will be declared Critical Information Infrastructure
   under the Cyber Security Ordinance 2025 is **undetermined**; it changes template 24 from
   optional to mandatory and adds a standing SOC reporting duty.
4. **OP-004-OI-04** — The PDPA 2026 breach-notification period is not yet prescribed by regulation.
   `RN-03`'s 72-hour planning assumption must be replaced by Legal, not carried forward.
5. **OP-004-OI-05** — Status-page hosting independence (§4) is a technical requirement this file
   depends on and does not control; confirm with Platform Engineering before W2.
6. **OP-004-OI-06** — Corporate contractual notification periods vary per agreement and are not yet
   consolidated in `LG-003`; template 26 cannot be operationalised until they are.

---

## Definition of Done

Tick every box before setting `status: Approved`. Full checklist in [`CG-008`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md).

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Notification_Template.md` — all five sections present; `Open Items` added, justified
- [x] Every factual, statutory, pricing or capability claim carries a source and a verification date
- [x] Terminology matches [`CG-004`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md); Bengali terms follow [`BN-003`](../11_Localisation_Bengali/BN-003_Bilingual_Terminology_Glossary.md)
- [x] All internal links resolve
- [x] Accessibility standard `CG-011` applied
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **open, OI-01**
- [ ] Named approver recorded — §2.6 additionally requires **Legal Counsel** sign-off ([`CG-007`](../00_Content_Governance_and_Standards/CG-007_Review_Approval_and_Signoff_Workflow.md) G5) because it reproduces statutory notification skeletons
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] Decision(s) taken while authoring logged in `RF-006` — six open items pending

**Gates required:** G1 ●, G2 ●, G3 ●, G4 ● (bilingual). **§2.6 additionally requires G5 Legal** —
declared here because that section is Class B content held inside a Class D file, which is a
deliberate departure recorded in `RF-006`.

---

*`OP-004` · 1000FiX ERP Programme · CONFIDENTIAL — Internal Use Only*
