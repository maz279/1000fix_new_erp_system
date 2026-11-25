---
id: OP-003
title: Service Desk Macro and Canned Response Library
project: 1000FiX ERP System v2.0
content_type: Notification template library
template: TPL_Notification_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Support Lead
author: Content Design with Support Lead and Contact Centre
reviewers: [Content Design Lead, Support Lead, Contact Centre Supervisor, Localisation Lead, Data Protection Officer, Marketplace Ops, Account Management, Procurement]
approver: Content Design Lead
content_class: D
purpose: >
  The written answers a support agent sends — acknowledgement, information request, known-issue
  notice, resolution and closure — in Bengali and English, for every population the support model
  serves. Without a macro library each agent invents the wording, so the same fault receives
  four different explanations, response time is spent typing rather than diagnosing, and no
  answer is reusable as self-service content later.
traces_to: [M66, M27, P10, OP-001, OP-004, OP-005, OP-013, OP-015, HC-015, UI-004, UI-005, VB-002, LG-010, BN-003]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: OP-003_Service_Desk_Macro_and_Canned_Response_Library_BN.md
sources:
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-002_Persona_and_Portal_Tone_Matrix.md — tone per audience and portal
    verified: 2026-08-20
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md §3.2 — OP-003 is one of four bilingual OP files; §3.3 audience rule
    verified: 2026-08-20
    class: P1
  - source: project_content/03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-004 error message standard and UI-005 system, permission and session message library
    verified: 2026-08-20
    class: P1
  - source: project_content/10_Legal_Policy_and_Compliance/LG-010_Data_Subject_Request_Handling_Content.md — DSR intake route and prohibition on informal handling
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66_Internal_IT_Service_Management.md §5 FR-ITS-030 — knowledge base with deflection measurement
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# OP-003 — Service Desk Macro and Canned Response Library

> **A macro is not a shortcut for the agent; it is a guarantee for the user.** It guarantees that
> the answer is accurate, that it is in the user's language, that it says what happens next, and
> that the fiftieth person to ask gets the same answer as the first.
>
> **68 macros.** Bengali is mandatory on every macro reaching a customer, technician, branch user,
> rider or seller ([`CG-010`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) §3.3). Macros addressed to vendors, brand partners and integration
> contacts are English-only, by the same rule.

---

## 1. Set Summary

| Item | Value |
|---|---|
| Channel(s) | Service desk portal reply · email · in-app support thread · WhatsApp (customer) · SMS (short forms only) |
| Audience | All eleven external populations and all internal staff ([`OP-001`](OP-001_Support_Model_Tiering_and_Routing_Content.md) §4.1) |
| Owning module | `M66` (internal), `M27` (customer channels) |
| Consent class | Transactional / service-related — **never marketing** |
| Quiet-hours exempt | Replies to a user-initiated contact are exempt ([`NT-003`](../04_Notification_and_Messaging/NT-003_Quiet_Hours_Throttling_and_Frequency_Policy.md)); proactive notices are not |
| Content class | **D — User-facing** |
| Bengali required | **Yes**, for the audiences named above |
| Bangladesh routing | Customer channels via `M27`; SMS masked as `1000FiX` |

**Macro ID format:** `mac.<audience>.<situation>` — `audience` ∈ `int` (internal), `cust`, `tech`,
`sell`, `corp`, `vend`, `brand`, `part`; matching the queue codes in `OP-001` §4.3.

---

## 2. Templates

### 2.1 Group A — Acknowledgement and triage

| # | Macro ID | Trigger | English | Bengali |
|---:|---|---|---|---|
| 1 | `mac.int.ack` | Any internal ticket accepted | Thank you — ticket {ref} is open with the service desk. We are looking at it now and will update you by {time}. If this is stopping you working right now, reply STOP-WORK and we will re-prioritise. | ধন্যবাদ — টিকিট {ref} সার্ভিস ডেস্কে খোলা হয়েছে। আমরা এখনই দেখছি এবং {time}-এর মধ্যে আপনাকে জানাব। এটি যদি এখনই আপনার কাজ বন্ধ করে রাখে, তাহলে STOP-WORK লিখে উত্তর দিন, আমরা অগ্রাধিকার বদলে দেব। |
| 2 | `mac.int.ack_p1` | Internal ticket triaged as work-stopping | Ticket {ref} is being treated as work-stopping. {owner} owns it now. Next update at {time}, and every {interval} after that until it is resolved. | টিকিট {ref} কাজ-বন্ধকারী হিসেবে গণ্য করা হচ্ছে। এখন এটি {owner}-এর দায়িত্বে। পরবর্তী আপডেট {time}-এ, এরপর সমাধান না হওয়া পর্যন্ত প্রতি {interval} অন্তর। |
| 3 | `mac.cust.ack` | Customer reports a portal or app problem | Thank you for telling us. We have logged this as {ref}. We will write to you by {time} with what we have found. Your service order {order} is not affected. | জানানোর জন্য ধন্যবাদ। আমরা এটি {ref} নম্বরে লিপিবদ্ধ করেছি। {time}-এর মধ্যে যা পেয়েছি তা আপনাকে জানাব। আপনার সার্ভিস অর্ডার {order} এতে ক্ষতিগ্রস্ত হয়নি। |
| 4 | `mac.tech.ack` | Technician reports an app fault from the field | Got it — {ref}. Keep working offline; the app stores your work and will sync when you have signal. We will tell you here when it is fixed. | পেয়েছি — {ref}। অফলাইনে কাজ চালিয়ে যান; অ্যাপ আপনার কাজ সংরক্ষণ করে রাখবে এবং নেটওয়ার্ক পেলে সিঙ্ক হবে। ঠিক হলে আমরা এখানেই জানাব। |
| 5 | `mac.sell.ack` | Seller support form submitted | Thank you. Reference {ref}. The marketplace team will reply by {time}. Your listings and open jobs are unaffected. | ধন্যবাদ। রেফারেন্স {ref}। মার্কেটপ্লেস টিম {time}-এর মধ্যে উত্তর দেবে। আপনার লিস্টিং ও চলমান কাজ অপরিবর্তিত আছে। |
| 6 | `mac.corp.ack` | Corporate user or admin contact | Thank you. Reference {ref}. Your account manager {am} has been copied and we will respond by {time}. | ধন্যবাদ। রেফারেন্স {ref}। আপনার অ্যাকাউন্ট ম্যানেজার {am}-কে অনুলিপি দেওয়া হয়েছে এবং আমরা {time}-এর মধ্যে উত্তর দেব। |
| 7 | `mac.vend.ack` | Vendor portal contact | Thank you. Reference {ref}. Procurement will respond by {time}. Purchase orders already acknowledged are unaffected. | *English only (`CG-010` §3.3)* |
| 8 | `mac.brand.ack` | Brand partner contact | Thank you. Reference {ref}. The warranty team will respond by {time}. Claims already submitted continue to process. | *English only* |

### 2.2 Group B — Access, password and account

| # | Macro ID | Trigger | English | Bengali |
|---:|---|---|---|---|
| 9 | `mac.int.pwd_self` | Password reset requested, self-service available | You can reset your own password in under a minute at {link} — it is faster than we can do it. If that does not work, reply here and we will reset it for you. | আপনি নিজেই {link}-এ এক মিনিটেরও কম সময়ে পাসওয়ার্ড রিসেট করতে পারেন — আমাদের চেয়ে দ্রুত। কাজ না করলে এখানে উত্তর দিন, আমরা রিসেট করে দেব। |
| 10 | `mac.int.pwd_reset` | Agent resets a password | Your password has been reset. You will be asked to set a new one at your next sign-in. We never send passwords by message — if anyone asks you for yours, tell the service desk. | আপনার পাসওয়ার্ড রিসেট করা হয়েছে। পরের বার সাইন-ইনে নতুন পাসওয়ার্ড দিতে বলা হবে। আমরা কখনও বার্তায় পাসওয়ার্ড পাঠাই না — কেউ আপনার পাসওয়ার্ড চাইলে সার্ভিস ডেস্ককে জানান। |
| 11 | `mac.int.mfa_reset` | MFA device lost or changed | Before we reset your second-factor device we must confirm it is you. Your line manager {mgr} will be asked to confirm, and you will be asked one question from your HR record. This takes about {minutes} minutes and it protects your account. | আপনার দ্বিতীয় ধাপের ডিভাইস রিসেট করার আগে আমাদের নিশ্চিত হতে হবে যে এটি আপনি। আপনার লাইন ম্যানেজার {mgr}-কে নিশ্চিত করতে বলা হবে এবং আপনাকে এইচআর রেকর্ড থেকে একটি প্রশ্ন করা হবে। এতে প্রায় {minutes} মিনিট লাগে এবং এটি আপনার অ্যাকাউন্ট সুরক্ষিত রাখে। |
| 12 | `mac.int.locked` | Account locked after failed attempts | Your account locked itself after several failed sign-ins — this is normal protection, not a fault. It unlocks automatically in {minutes} minutes, or reply here and we will unlock it now. | কয়েকবার ভুল সাইন-ইনের পর আপনার অ্যাকাউন্ট নিজে থেকেই লক হয়েছে — এটি স্বাভাবিক সুরক্ষা, কোনো ত্রুটি নয়। {minutes} মিনিটে নিজেই খুলে যাবে, অথবা এখানে উত্তর দিন, আমরা এখনই খুলে দেব। |
| 13 | `mac.int.access_route` | Access request arrives as an email or chat | Access is granted through the access request form at {link} so that the approval is recorded. I have started one for you — {ref} — and sent it to {approver}. I cannot grant it directly, and neither can anyone else in the service desk. | রেকর্ড রাখার জন্য অ্যাক্সেস কেবল {link}-এর অ্যাক্সেস রিকোয়েস্ট ফর্মের মাধ্যমে দেওয়া হয়। আমি আপনার জন্য একটি শুরু করেছি — {ref} — এবং {approver}-এর কাছে পাঠিয়েছি। আমি সরাসরি অ্যাক্সেস দিতে পারি না, সার্ভিস ডেস্কের অন্য কেউও পারেন না। |
| 14 | `mac.int.access_denied` | Requested access outside the role profile | The access you asked for is not in the standard profile for {role}, so it needs {approver}'s approval with a business reason. I have recorded your reason as: "{reason}". You will hear the outcome by {time}. | আপনি যে অ্যাক্সেস চেয়েছেন তা {role}-এর মানক প্রোফাইলে নেই, তাই এর জন্য {approver}-এর অনুমোদন ও ব্যবসায়িক কারণ প্রয়োজন। আমি আপনার কারণ লিখেছি: "{reason}"। {time}-এর মধ্যে ফলাফল জানবেন। |
| 15 | `mac.int.leaver` | Access revocation confirmed | {name}'s access was revoked at {time} across all systems. Their allocated equipment is listed as {assets} — please confirm what has been returned. | {time}-এ সব সিস্টেম থেকে {name}-এর অ্যাক্সেস প্রত্যাহার করা হয়েছে। তাঁর বরাদ্দ সরঞ্জাম হিসেবে {assets} তালিকাভুক্ত — কী কী ফেরত এসেছে তা নিশ্চিত করুন। |

### 2.3 Group C — Known issue and outage

| # | Macro ID | Trigger | English | Bengali |
|---:|---|---|---|---|
| 16 | `mac.int.known` | Ticket matches a published known issue | This is a known issue — {issue_ref}. Until it is fixed, do this instead: {workaround}. We expect a fix by {target}. You do not need to raise it again; we will tell you here when it is resolved. | এটি একটি পরিচিত সমস্যা — {issue_ref}। ঠিক না হওয়া পর্যন্ত এর বদলে এটি করুন: {workaround}। আমরা {target}-এর মধ্যে সমাধানের আশা করছি। আবার জানানোর দরকার নেই; সমাধান হলে আমরা এখানেই জানাব। |
| 17 | `mac.int.outage` | Ticket relates to a declared incident | {system} is currently affected — incident {inc_ref}, declared at {declared}. Live updates are at {status_link}. Until it is back, follow the fallback for your task: {fallback}. Nothing you have already entered is lost. | এই মুহূর্তে {system} প্রভাবিত — ইনসিডেন্ট {inc_ref}, {declared}-এ ঘোষিত। সরাসরি আপডেট {status_link}-এ। ফিরে না আসা পর্যন্ত আপনার কাজের বিকল্প পদ্ধতি অনুসরণ করুন: {fallback}। আপনি যা আগে লিখেছেন তার কিছুই হারায়নি। |
| 18 | `mac.cust.outage` | Customer contact during a customer-facing incident | We are having a problem with {service} at the moment and our team is working on it. You can still {alternative}. We will update {status_link} and will not close your request until it is working for you. | এই মুহূর্তে {service}-এ আমাদের একটি সমস্যা হচ্ছে এবং আমাদের টিম কাজ করছে। আপনি এখনও {alternative} করতে পারেন। আমরা {status_link}-এ আপডেট দেব এবং আপনার জন্য এটি কাজ না করা পর্যন্ত আপনার অনুরোধ বন্ধ করব না। |
| 19 | `mac.tech.offline` | Technician reports sync not completing | Your app works offline for 24 hours and holds everything you enter. Please keep working. When you reach signal, open the app and wait for the sync icon to stop moving before closing it. If it still fails after that, send us the sync log from Settings → Support. | আপনার অ্যাপ ২৪ ঘণ্টা অফলাইনে কাজ করে এবং আপনার লেখা সবকিছু ধরে রাখে। কাজ চালিয়ে যান। নেটওয়ার্ক পেলে অ্যাপ খুলুন এবং সিঙ্ক আইকন থামার আগে অ্যাপ বন্ধ করবেন না। তারপরেও না হলে Settings → Support থেকে সিঙ্ক লগ পাঠান। |
| 20 | `mac.int.resolved_outage` | Incident resolved | {system} is working again as of {time}. Anything queued while it was down has been processed — please check {check} and tell us if anything is missing. We will publish what happened at {pir_link}. | {time} থেকে {system} আবার কাজ করছে। বন্ধ থাকা অবস্থায় জমে থাকা কাজ প্রক্রিয়া করা হয়েছে — অনুগ্রহ করে {check} দেখে নিন এবং কিছু বাদ পড়লে জানান। কী ঘটেছিল তা আমরা {pir_link}-এ প্রকাশ করব। |

### 2.4 Group D — Information needed

| # | Macro ID | Trigger | English | Bengali |
|---:|---|---|---|---|
| 21 | `mac.int.need_info` | Cannot proceed without detail | To find this I need three things: what you were doing, what the screen said (a photo is fine), and the reference number if there was one. The ticket clock pauses until you reply, so please send when you can. | এটি খুঁজে পেতে আমার তিনটি জিনিস দরকার: আপনি কী করছিলেন, স্ক্রিনে কী লেখা ছিল (ছবি হলেই চলবে), এবং কোনো রেফারেন্স নম্বর থাকলে সেটি। আপনি উত্তর না দেওয়া পর্যন্ত টিকিটের সময় গণনা থেমে থাকে, তাই সুবিধামতো পাঠান। |
| 22 | `mac.int.need_ref` | Missing record reference | Please send me the reference number from the top of the screen — it starts with {prefix}. Without it I would be searching {count}+ records and might correct the wrong one. | স্ক্রিনের উপরে থাকা রেফারেন্স নম্বরটি পাঠান — এটি {prefix} দিয়ে শুরু হয়। এটি ছাড়া আমাকে {count}+ রেকর্ড খুঁজতে হবে এবং ভুলটি সংশোধন হয়ে যেতে পারে। |
| 23 | `mac.int.need_time` | Need the time window to search logs | What time did this happen, to the nearest ten minutes? That is what lets me find it in the system log rather than guess. | এটি কখন ঘটেছিল — দশ মিনিটের মধ্যে সময়টি বলুন? এটিই আমাকে অনুমান না করে সিস্টেম লগে খুঁজে পেতে সাহায্য করে। |
| 24 | `mac.int.no_reply` | Chased twice, no response | I have not been able to reach you about {ref}. I will hold it open until {date} and then close it. If it is still happening, reply any time and it reopens — you do not need to start again. | {ref} নিয়ে আপনার সঙ্গে যোগাযোগ করতে পারিনি। আমি এটি {date} পর্যন্ত খোলা রাখব, এরপর বন্ধ করে দেব। সমস্যা থাকলে যেকোনো সময় উত্তর দিন, এটি আবার খুলে যাবে — নতুন করে শুরু করতে হবে না। |
| 25 | `mac.cust.need_consent` | Need to view the customer's record to help | To look into this I need to open your service record. Reply YES and I will do that now; your record is only opened for this request and the access is logged. | এটি দেখতে হলে আমাকে আপনার সার্ভিস রেকর্ড খুলতে হবে। YES লিখে উত্তর দিন, আমি এখনই দেখব; আপনার রেকর্ড কেবল এই অনুরোধের জন্যই খোলা হবে এবং অ্যাক্সেসটি লিপিবদ্ধ থাকবে। |

### 2.5 Group E — Resolution and closure

| # | Macro ID | Trigger | English | Bengali |
|---:|---|---|---|---|
| 26 | `mac.int.fixed` | Resolved, cause known | Fixed at {time}. What happened: {cause}. What we changed: {fix}. Please try it and tell me if anything is still wrong — I will keep {ref} open until you confirm. | {time}-এ ঠিক করা হয়েছে। যা ঘটেছিল: {cause}। আমরা যা বদলেছি: {fix}। একবার দেখে নিন এবং কিছু ভুল থাকলে জানান — আপনি নিশ্চিত না করা পর্যন্ত আমি {ref} খোলা রাখব। |
| 27 | `mac.int.fixed_workaround` | Restored by workaround, root cause open | It is working again, but by a workaround rather than a fix — {workaround}. The underlying cause is recorded as problem {prob_ref} and is being worked on. If it comes back, quote {ref} and it will reach the same team. | এটি আবার কাজ করছে, তবে পূর্ণ সমাধান নয় — একটি বিকল্প ব্যবস্থায়: {workaround}। মূল কারণ {prob_ref} হিসেবে লিপিবদ্ধ এবং কাজ চলছে। আবার ঘটলে {ref} উল্লেখ করুন, একই টিমের কাছে পৌঁছাবে। |
| 28 | `mac.int.not_fault` | Working as designed | The system is behaving as it is meant to here: {explanation}. I understand that is not what you expected. If the design is wrong for how you work, I can raise it as a change request rather than a fault — tell me and I will. | এখানে সিস্টেম যেভাবে কাজ করার কথা সেভাবেই করছে: {explanation}। বুঝতে পারছি এটি আপনার প্রত্যাশা ছিল না। আপনার কাজের ধরনের জন্য যদি এই নকশাটিই ভুল হয়, আমি এটিকে ত্রুটি নয় বরং পরিবর্তনের অনুরোধ হিসেবে তুলতে পারি — বললেই করব। |
| 29 | `mac.int.defect` | Confirmed defect, fix scheduled | You have found a defect — thank you, genuinely. It is recorded as {defect_ref} at severity {sev} and scheduled for {release}. Until then: {workaround}. | আপনি একটি ত্রুটি খুঁজে পেয়েছেন — সত্যিই ধন্যবাদ। এটি {defect_ref} নম্বরে {sev} মাত্রায় লিপিবদ্ধ এবং {release}-এ সমাধানের জন্য নির্ধারিত। ততক্ষণ পর্যন্ত: {workaround}। |
| 30 | `mac.int.close` | Closing after confirmation | Closing {ref}. If the same thing happens again within {days} days, reply to this message rather than raising a new ticket — it keeps the history together and helps us find the cause. | {ref} বন্ধ করা হচ্ছে। {days} দিনের মধ্যে একই ঘটনা আবার ঘটলে নতুন টিকিট না খুলে এই বার্তার উত্তর দিন — এতে ইতিহাস একসঙ্গে থাকে এবং কারণ খুঁজে পেতে সাহায্য করে। |
| 31 | `mac.cust.fixed` | Customer-facing fix confirmed | This is now working. Sorry for the trouble it caused. If you would rather we did the {action} for you this time, tell us and we will. | এটি এখন কাজ করছে। অসুবিধার জন্য দুঃখিত। এবারের {action} যদি আপনি চান আমরা করে দিই, বললেই করে দেব। |

### 2.6 Group F — Deflection to self-service

> Deflection macros are the only macros permitted to end a contact without a human action, and
> only where the linked content genuinely answers the question. A deflection to content that does
> not answer it is measured as a failure, not a saving ([`CG-014`](../00_Content_Governance_and_Standards/CG-014_Content_Metrics_and_Effectiveness_Measurement.md)).

| # | Macro ID | Trigger | English | Bengali |
|---:|---|---|---|---|
| 32 | `mac.int.howto` | "How do I…" with existing guidance | Here is the step-by-step for that: {link}. It takes about {minutes} minutes. If any step does not match what you see on screen, tell me which step — that usually means the guide is out of date and I will get it corrected. | এর ধাপে ধাপে নির্দেশনা এখানে: {link}। প্রায় {minutes} মিনিট লাগে। কোনো ধাপ আপনার স্ক্রিনের সঙ্গে না মিললে কোন ধাপ তা জানান — সাধারণত এর মানে নির্দেশিকাটি পুরনো, আমি সংশোধন করিয়ে নেব। |
| 33 | `mac.cust.selfserve` | Customer asks something the portal answers | You can do this yourself in the app: {path}. It is available at any hour. If you would rather I did it for you now, just say so — both are fine. | আপনি এটি অ্যাপেই নিজে করতে পারেন: {path}। যেকোনো সময় পাওয়া যায়। আপনি চাইলে আমি এখনই করে দিতে পারি — দুটোই ঠিক আছে। |
| 34 | `mac.tech.kb` | Technician asks a repair-procedure question | The procedure is in the technical library: {kb_link}. It works offline once opened. If the procedure does not match the model in front of you, send a photo of the label and we will get the article corrected. | পদ্ধতিটি টেকনিক্যাল লাইব্রেরিতে আছে: {kb_link}। একবার খুললে অফলাইনেও কাজ করে। আপনার সামনের মডেলের সঙ্গে না মিললে লেবেলের ছবি পাঠান, আমরা আর্টিকেলটি সংশোধন করাব। |

### 2.7 Group G — Escalation and handover

| # | Macro ID | Trigger | English | Bengali |
|---:|---|---|---|---|
| 35 | `mac.int.escalate` | Passing to a higher tier | I have passed this to {team} because it needs {reason}. I have given them what I ruled out so they do not start again: {ruled_out}. I stay your point of contact — updates still come from me. | আমি এটি {team}-এর কাছে পাঠিয়েছি, কারণ এতে {reason} প্রয়োজন। আমি যা যা বাদ দিয়েছি তা তাঁদের জানিয়েছি যাতে নতুন করে শুরু করতে না হয়: {ruled_out}। আমিই আপনার যোগাযোগের ব্যক্তি থাকছি — আপডেট আমার কাছ থেকেই আসবে। |
| 36 | `mac.int.vendor` | Waiting on a third party | This is with {vendor} — their reference is {vendor_ref}. Their committed response is {sla}. I chase them every {interval} and will tell you each time there is news, including when there is none. | এটি {vendor}-এর কাছে আছে — তাঁদের রেফারেন্স {vendor_ref}। তাঁদের প্রতিশ্রুত উত্তর {sla}। আমি প্রতি {interval} অন্তর তাগাদা দিই এবং প্রতিবার খবর জানাব, খবর না থাকলেও জানাব। |
| 37 | `mac.int.handover` | Shift handover on an open ticket | {name} is handing this to {name2} at shift change. Everything so far is in the ticket; you do not need to explain it again. | শিফট পরিবর্তনে {name} এটি {name2}-এর কাছে হস্তান্তর করছেন। এ পর্যন্ত সবকিছু টিকিটে আছে; আপনাকে আবার ব্যাখ্যা করতে হবে না। |
| 38 | `mac.int.priority_change` | Priority raised or lowered | I have changed this to {priority} because {reason}. That changes the response time to {target}. If you disagree, say so and it goes to {escalation} — that is a normal request, not a complaint. | আমি এটি {priority}-তে বদলেছি, কারণ {reason}। এতে উত্তরের সময় {target} হয়ে যায়। আপনি একমত না হলে জানান, এটি {escalation}-এ যাবে — এটি স্বাভাবিক অনুরোধ, অভিযোগ নয়। |

### 2.8 Group H — Customer service situations (`P10` console)

| # | Macro ID | Trigger | English | Bengali |
|---:|---|---|---|---|
| 39 | `mac.cust.app_login` | Customer cannot sign in | Let us get you back in. Enter your mobile number at {link} and you will receive a one-time code. If the code does not arrive in two minutes, tell me and I will send it another way — do not request it repeatedly, as that can lock the number for {minutes} minutes. | চলুন আপনাকে আবার ঢোকাই। {link}-এ আপনার মোবাইল নম্বর দিন, একটি এককালীন কোড পাবেন। দুই মিনিটে কোড না এলে আমাকে জানান, আমি অন্যভাবে পাঠাব — বারবার অনুরোধ করবেন না, এতে নম্বরটি {minutes} মিনিটের জন্য বন্ধ হয়ে যেতে পারে। |
| 40 | `mac.cust.payment_pending` | Payment taken but not shown | Your payment of {amount} reached us at {time} and is confirmed — reference {txn}. It can take up to {minutes} minutes to appear against your order. If it has not appeared by {time2}, reply and I will match it manually today. | {time}-এ আপনার {amount} টাকার পেমেন্ট আমাদের কাছে পৌঁছেছে এবং নিশ্চিত হয়েছে — রেফারেন্স {txn}। অর্ডারে দেখাতে {minutes} মিনিট পর্যন্ত লাগতে পারে। {time2}-এর মধ্যে না দেখালে উত্তর দিন, আমি আজই মিলিয়ে দেব। |
| 41 | `mac.cust.payment_failed` | Payment failed at the gateway | The payment did not complete and **no money has left your account** — if it shows as deducted it will return within {days} days automatically. You can pay again here {link}, use another method, or pay at the branch. Your job is held for you either way. | পেমেন্টটি সম্পন্ন হয়নি এবং **আপনার অ্যাকাউন্ট থেকে কোনো টাকা যায়নি** — কেটে নেওয়া দেখালে তা {days} দিনের মধ্যে নিজেই ফেরত আসবে। আপনি এখানে {link}-এ আবার দিতে পারেন, অন্য মাধ্যম ব্যবহার করতে পারেন, বা শাখায় দিতে পারেন। যেভাবেই হোক আপনার কাজটি আপনার জন্য রাখা আছে। |
| 42 | `mac.cust.tracking` | Tracking page not updating | Tracking updates when the technician moves or changes the job status, so it can pause for a while. Right now: {status}, last updated {time}. If you want, I can call the technician and tell you directly. | টেকনিশিয়ান চলাচল করলে বা কাজের অবস্থা বদলালে ট্র্যাকিং হালনাগাদ হয়, তাই কিছুক্ষণ থেমে থাকতে পারে। এই মুহূর্তে: {status}, সর্বশেষ হালনাগাদ {time}। চাইলে আমি টেকনিশিয়ানকে ফোন করে আপনাকে সরাসরি জানাতে পারি। |
| 43 | `mac.cust.wrong_language` | Customer receiving messages in the wrong language | I have set your messages to {language}. You can change this yourself at any time in the app under {path}. Sorry that they came in the wrong one. | আমি আপনার বার্তার ভাষা {language} করে দিয়েছি। আপনি চাইলে যেকোনো সময় অ্যাপে {path}-এ নিজেই বদলাতে পারেন। ভুল ভাষায় যাওয়ার জন্য দুঃখিত। |
| 44 | `mac.cust.dsr` | Customer asks for their data, correction or deletion | That is a formal request under the data protection rules and it has its own process so that it is handled properly and on time. I am logging it now as {dsr_ref}; the data protection team will contact you within {days} days. I cannot action it here, and nor can any agent. | এটি ডেটা সুরক্ষা বিধির অধীনে একটি আনুষ্ঠানিক অনুরোধ এবং সঠিকভাবে ও সময়মতো নিষ্পত্তির জন্য এর নিজস্ব প্রক্রিয়া আছে। আমি এখনই এটি {dsr_ref} নম্বরে লিপিবদ্ধ করছি; ডেটা সুরক্ষা টিম {days} দিনের মধ্যে আপনার সঙ্গে যোগাযোগ করবে। আমি এখানে এটি করতে পারি না, কোনো এজেন্টই পারেন না। |
| 45 | `mac.cust.complaint` | Customer is dissatisfied and wants it recorded | I have recorded this as a complaint — {comp_ref} — not just a message, so it is reviewed by {owner} and answered within {days} days. You will get that answer whether or not we can give you the outcome you want. | আমি এটি কেবল বার্তা নয়, একটি অভিযোগ হিসেবে লিপিবদ্ধ করেছি — {comp_ref} — যাতে {owner} এটি পর্যালোচনা করেন এবং {days} দিনের মধ্যে উত্তর দেন। আপনি যে ফল চান তা দিতে পারি বা না পারি, উত্তর পাবেন। |

### 2.9 Group I — Ecosystem populations

| # | Macro ID | Trigger | English | Bengali |
|---:|---|---|---|---|
| 46 | `mac.sell.payout` | Seller asks about a held payout | Payout {payout_ref} is held because {reason}. Holds release automatically when {condition}. Nothing is deducted while it is held. You can see the current position at {link}. | পে-আউট {payout_ref} আটকে আছে কারণ {reason}। {condition} হলে আটক নিজে থেকেই ছেড়ে যায়। আটক থাকা অবস্থায় কিছুই কাটা হয় না। বর্তমান অবস্থা {link}-এ দেখতে পারেন। |
| 47 | `mac.sell.doc_reject` | Seller document rejected at verification | The document was not accepted because {reason}. Please upload a new one at {link} — it needs to show {requirement}. Verification usually completes within {hours} hours of a good upload. | নথিটি গ্রহণ করা হয়নি কারণ {reason}। {link}-এ নতুন একটি আপলোড করুন — এতে {requirement} দেখা যেতে হবে। ভালো আপলোডের {hours} ঘণ্টার মধ্যে যাচাই সাধারণত শেষ হয়। |
| 48 | `mac.sell.score` | Seller queries their score | Your score is {score}. It is made up of {components}. The two things that would move it most for you right now are {action1} and {action2}. The full method is at {link}. | আপনার স্কোর {score}। এটি গঠিত {components} দিয়ে। এই মুহূর্তে যে দুটি কাজ আপনার স্কোর সবচেয়ে বেশি বদলাবে তা হলো {action1} ও {action2}। পূর্ণ পদ্ধতি {link}-এ। |
| 49 | `mac.part.attribution` | Partner queries a referral not attributed | Referral {lead_ref} was not attributed because {reason}. Attribution rules are at {link}. If you believe this is wrong, reply with the date and the customer's mobile number and I will have it reviewed — reviews take {days} working days. | রেফারেল {lead_ref} গণনায় আসেনি কারণ {reason}। অ্যাট্রিবিউশন নিয়ম {link}-এ। এটি ভুল মনে হলে তারিখ ও গ্রাহকের মোবাইল নম্বর দিয়ে উত্তর দিন, আমি পুনর্বিবেচনা করাব — এতে {days} কর্মদিবস লাগে। |
| 50 | `mac.vend.po` | Vendor cannot see or acknowledge a PO | Purchase order {po} was issued to {vendor_user} on {date} and is awaiting your acknowledgement. If you cannot see it, check that you are signed in as the account that receives orders for {vendor}. I can move it to another user in your organisation if you tell me who. | *English only* |
| 51 | `mac.vend.invoice` | Vendor invoice rejected | Invoice {inv} was returned because {reason}. Our three-way match needs the PO number, the delivery reference and the tax details to agree. Resubmit at {link}; corrected invoices are normally processed in the next payment run on {date}. | *English only* |
| 52 | `mac.brand.claim` | Brand partner claim rejected or queried | Claim {claim} was {status} because {reason}. The evidence standard for this claim type is at {link}. If you resubmit with {missing}, it re-enters the queue at its original date rather than the resubmission date. | *English only* |
| 53 | `mac.corp.approval` | Corporate approval chain stuck | Request {req} is waiting on {approver}, who has been reminded {count} times. Your organisation's administrator can reassign the approval at {path}. We cannot reassign it for you — approval chains are yours to control, which is what keeps them valid. | অনুরোধ {req} {approver}-এর কাছে অপেক্ষমাণ, যাঁকে {count} বার মনে করিয়ে দেওয়া হয়েছে। আপনার প্রতিষ্ঠানের অ্যাডমিনিস্ট্রেটর {path}-এ অনুমোদন পুনর্বণ্টন করতে পারেন। আমরা আপনার হয়ে এটি করতে পারি না — অনুমোদনের শৃঙ্খল আপনার নিয়ন্ত্রণে থাকে, এতেই তা বৈধ থাকে। |

### 2.10 Group J — Refusal, out of scope and safety

> The hardest macros to write and the most damaging to improvise. Each says no, says why, and
> says what *can* happen instead.

| # | Macro ID | Trigger | English | Bengali |
|---:|---|---|---|---|
| 54 | `mac.int.no_direct_db` | Request to "just change it in the database" | I cannot change data directly — every correction has to go through the screen or an approved data-fix procedure so that it is recorded and reversible. What I can do is {alternative}, which gets you the same result today. | আমি সরাসরি ডেটা বদলাতে পারি না — প্রতিটি সংশোধন স্ক্রিনের মাধ্যমে বা অনুমোদিত ডেটা-ফিক্স পদ্ধতিতে হতে হয়, যাতে তা লিপিবদ্ধ ও ফেরানো যায়। আমি যা করতে পারি তা হলো {alternative}, আজই একই ফল পাবেন। |
| 55 | `mac.int.no_share_account` | Request to share or borrow a login | I cannot give you someone else's sign-in, and please do not use one you have been given — anything done with it is recorded against them, not you. Tell me what you need to do and I will get you the right access under your own name. | আমি আপনাকে অন্য কারও সাইন-ইন দিতে পারি না, এবং কেউ দিলেও তা ব্যবহার করবেন না — তা দিয়ে করা সবকিছু আপনার নয়, তাঁর নামে লিপিবদ্ধ হয়। আপনার কী করা দরকার বলুন, আমি আপনার নিজের নামেই সঠিক অ্যাক্সেসের ব্যবস্থা করব। |
| 56 | `mac.int.no_bypass` | Request to bypass an approval or control | That step is a control, not an obstacle — it exists because {reason}. I cannot remove it. If it is wrong for this situation, {authority} can approve an exception and I have started that request for you as {ref}. | ওই ধাপটি বাধা নয়, একটি নিয়ন্ত্রণ — এটি আছে কারণ {reason}। আমি এটি সরাতে পারি না। এই পরিস্থিতির জন্য এটি অনুপযুক্ত হলে {authority} ব্যতিক্রম অনুমোদন করতে পারেন, আমি আপনার জন্য {ref} নম্বরে সেই অনুরোধ শুরু করেছি। |
| 57 | `mac.cust.out_of_scope` | Request outside what support can do | This is outside what the support team can decide. The person who can is {owner}, and I have passed it to them with everything you have told me — reference {ref}. They will contact you by {time}. | এটি সাপোর্ট টিমের সিদ্ধান্তের বাইরে। যিনি পারেন তিনি {owner}, এবং আপনার বলা সবকিছু সহ আমি তাঁর কাছে পাঠিয়েছি — রেফারেন্স {ref}। তিনি {time}-এর মধ্যে যোগাযোগ করবেন। |
| 58 | `mac.int.safety` | Any contact disclosing a safety incident | Stop and make the area safe first — this needs the safety process, not the service desk. I am notifying {hse} now. Please report it as an incident at {link} as soon as you are able; that is a legal requirement, not paperwork. | আগে থামুন এবং জায়গাটি নিরাপদ করুন — এর জন্য সেফটি প্রক্রিয়া দরকার, সার্ভিস ডেস্ক নয়। আমি এখনই {hse}-কে জানাচ্ছি। যত দ্রুত সম্ভব {link}-এ ঘটনাটি রিপোর্ট করুন; এটি কাগুজে নিয়ম নয়, আইনি বাধ্যবাধকতা। |
| 59 | `mac.int.security` | Suspected security or data incident | Thank you for reporting it — that was the right thing to do. I am treating this as a security incident and the security team is being paged now. Please do not delete anything, do not forward it further, and do not investigate it yourself. Someone will contact you within {minutes} minutes. | জানানোর জন্য ধন্যবাদ — এটিই সঠিক কাজ ছিল। আমি এটিকে নিরাপত্তা ঘটনা হিসেবে নিচ্ছি এবং এখনই নিরাপত্তা টিমকে ডাকা হচ্ছে। অনুগ্রহ করে কিছু মুছবেন না, আর কাউকে ফরওয়ার্ড করবেন না, এবং নিজে তদন্ত করবেন না। {minutes} মিনিটের মধ্যে কেউ যোগাযোগ করবেন। |
| 60 | `mac.int.phishing` | User reports a suspicious message | You were right to check. Do not click anything in it. Forward it to {mailbox} and then delete it. If you already clicked or entered your password, tell me now — that is not a problem you will be blamed for, but it is one we must act on within minutes. | যাচাই করে আপনি ঠিক কাজ করেছেন। এর কোনো কিছুতে ক্লিক করবেন না। এটি {mailbox}-এ ফরওয়ার্ড করে মুছে ফেলুন। যদি ইতিমধ্যেই ক্লিক করে থাকেন বা পাসওয়ার্ড দিয়ে থাকেন, এখনই জানান — এর জন্য আপনাকে দোষ দেওয়া হবে না, তবে আমাদের কয়েক মিনিটের মধ্যে ব্যবস্থা নিতে হবে। |

### 2.11 Group K — Planned change and maintenance

| # | Macro ID | Trigger | English | Bengali |
|---:|---|---|---|---|
| 61 | `mac.int.maint` | Query about planned maintenance | Planned maintenance runs {window}. During it you will not be able to {affected}, and everything else keeps working. It is announced {notice} in advance every time — see {link}. | নির্ধারিত রক্ষণাবেক্ষণ চলবে {window}। এই সময়ে আপনি {affected} করতে পারবেন না, বাকি সব চালু থাকবে। প্রতিবারই {notice} আগে ঘোষণা করা হয় — দেখুন {link}। |
| 62 | `mac.int.release` | Query about a change users noticed | That changed in release {release} on {date}. What changed and why is in the release note: {link}. If it makes your work harder rather than easier, tell me — that is feedback we act on, and it is how the next release gets decided. | এটি {date} তারিখে {release} রিলিজে বদলেছে। কী বদলেছে ও কেন, তা রিলিজ নোটে আছে: {link}। এটি যদি আপনার কাজ সহজ না করে কঠিন করে, জানান — এই মতামত নিয়েই আমরা কাজ করি এবং পরের রিলিজ ঠিক হয়। |
| 63 | `mac.int.training` | User needs training, not support | This is a training gap rather than a fault, and that is not a criticism — the change was recent. The {minutes}-minute refresher is at {link} and your branch champion {champion} can sit with you. | এটি ত্রুটি নয়, প্রশিক্ষণের ঘাটতি — এবং এটি কোনো সমালোচনা নয়, পরিবর্তনটি সাম্প্রতিক। {minutes} মিনিটের রিফ্রেশার {link}-এ আছে এবং আপনার শাখার চ্যাম্পিয়ন {champion} পাশে বসে দেখিয়ে দিতে পারেন। |

### 2.12 Group L — Hypercare-specific ([`OP-002`](OP-002_Hypercare_Plan_and_Exit_Criteria.md))

| # | Macro ID | Trigger | English | Bengali |
|---:|---|---|---|---|
| 64 | `mac.int.hypercare` | Contact during hypercare | We are in the first {weeks} weeks after go-live, so support is on site and answering faster than normal. Your floor-walker today is {name}. Anything you tell us now shapes what gets fixed first. | চালু হওয়ার প্রথম {weeks} সপ্তাহে আমরা আছি, তাই সাপোর্ট সরাসরি উপস্থিত এবং স্বাভাবিকের চেয়ে দ্রুত উত্তর দিচ্ছে। আজ আপনার ফ্লোর-ওয়াকার {name}। আপনি এখন যা জানাবেন তাতেই ঠিক হবে কোনটি আগে সমাধান হবে। |
| 65 | `mac.int.hypercare_exit` | Hypercare ending | On-site support ends on {date}. From then, help comes from {route} with the same reference numbers — nothing you have open is lost. Your branch champion {champion} stays. | {date} তারিখে সরাসরি উপস্থিত সহায়তা শেষ হবে। এরপর একই রেফারেন্স নম্বরসহ {route} থেকে সহায়তা মিলবে — আপনার চলমান কিছুই হারাবে না। আপনার শাখার চ্যাম্পিয়ন {champion} থাকছেন। |
| 66 | `mac.int.fallback` | Directing a user to manual fallback | Use the paper procedure for this until the system is back: {fallback_ref}. Keep every form — they are entered into the system afterwards and that is how the record stays complete. Do not re-enter them yourself. | সিস্টেম ফিরে না আসা পর্যন্ত এর জন্য কাগজের পদ্ধতি ব্যবহার করুন: {fallback_ref}। প্রতিটি ফর্ম রেখে দিন — পরে সেগুলি সিস্টেমে তোলা হবে, এতেই রেকর্ড পূর্ণ থাকে। নিজে থেকে আবার এন্ট্রি করবেন না। |
| 67 | `mac.int.catchup` | After fallback, during catch-up entry | We are entering the forms from {date} now. Until that finishes, what you see on screen is behind what actually happened — please do not correct it yet. We will tell you when it is caught up, and then anything still wrong is worth reporting. | আমরা এখন {date} তারিখের ফর্মগুলি এন্ট্রি করছি। শেষ না হওয়া পর্যন্ত স্ক্রিনে যা দেখছেন তা বাস্তবের চেয়ে পিছিয়ে — এখনই সংশোধন করবেন না। শেষ হলে আমরা জানাব, তারপরও ভুল থাকলে তা জানানোর মতো। |
| 68 | `mac.int.satisfaction` | Closing, requesting feedback | One question, if you have ten seconds: was this resolved properly for you? Yes or No is enough. It is the only measure of support that we treat as real. | দশ সেকেন্ড সময় থাকলে একটি প্রশ্ন: আপনার সমস্যাটি কি ঠিকভাবে সমাধান হয়েছে? হ্যাঁ বা না লিখলেই হবে। সাপোর্টের এই একটিই মাপকাঠি আমরা সত্যিকারের বলে মানি। |

### 2.13 Variables

| Variable | Source | Example |
|---|---|---|
| `{ref}` | Ticket number (`M66` `fix.it.ticket.number`) | IT-2027-04812 |
| `{inc_ref}` | Incident number ([`OP-013`](OP-013_On_Call_Escalation_and_Handover_Content.md)) | INC-2027-0043 |
| `{issue_ref}` | Known-issue log (`OP-002` §4.6) | KI-W1-017 |
| `{defect_ref}` | Defect register ([`TS-018`](../13_Test_and_Acceptance_Content/TS-018_Defect_Taxonomy_Triage_and_Signoff_Forms.md)) | DEF-4471 |
| `{prob_ref}` | Problem record ([`SP-031`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) §8) | PRB-0112 |
| `{dsr_ref}` | Data subject request ([`LG-010`](../10_Legal_Policy_and_Compliance/LG-010_Data_Subject_Request_Handling_Content.md)) | DSR-2027-0031 |
| `{status_link}` | Status page ([`OP-005`](OP-005_Status_Page_and_Maintenance_Notice_Copy.md)) | status.1000fix… |
| `{fallback_ref}` | Manual fallback procedure ([`OP-014`](OP-014_Manual_Fallback_Procedure_Set.md)) | FB-07 Counter payment |
| `{workaround}` | Known-issue log, in user language | — |
| `{time}`, `{date}` | [`BN-007`](../11_Localisation_Bengali/BN-007_Date_Time_Number_Currency_and_Address_Formats.md) date/time formats per locale | ২০/০৮/২০২৬, বিকাল ৪:৩০ |
| `{amount}` | `BN-007` money format | ৳ ৩,২০০.০০ |
| `{champion}` | [`CM-008`](../16_Change_Management_and_Comms/CM-008_Champion_and_Super_User_Network_Kit.md) champion register | — |

### 2.14 Rules

| # | Rule |
|---|---|
| **MC-01** | **Every macro states what happens next and when.** A reply with no next step generates a second contact |
| **MC-02** | **No macro is sent unedited where it needs a fact.** The variables are mandatory; a macro sent with `{ref}` still in it is a defect in the reply, not a typo |
| **MC-03** | Bengali is not a translation of the English — both are authored, and the Bengali is the one most recipients read (`CG-010` §4). Where the two differ in nuance, the Bengali is corrected, not the meaning |
| **MC-04** | **No macro apologises without saying what changed.** "Sorry for the inconvenience" alone is prohibited ([`VB-001`](../01_Voice_Brand_and_Design_Content/VB-001_ERP_Product_Voice_and_Tone_Guide.md) tone rules) |
| **MC-05** | No macro blames the user, another team, a vendor, or "the system" |
| **MC-06** | No macro contains personal data of a third party, a password, a token, or a link that authenticates without challenge |
| **MC-07** | **No macro promises a date the sender does not control.** Where the date is the vendor's, it is attributed to the vendor (`mac.int.vendor`) |
| **MC-08** | A macro used more than 20 times in a month is a candidate for a help article and, if customer-facing, a product fix (`OP-001` `DF-01`) |
| **MC-09** | Macros are versioned with this file. An agent may not create a personal macro library; a proposed macro goes to the Support Lead and, if accepted, is added here |
| **MC-10** | Refusal macros (Group J) are **never softened in the moment**. If a refusal is wrong, the answer is an exception request, not a kinder refusal |
| **MC-11** | Every macro touching a security, safety or data-protection situation is reviewed by that function, not only by Content Design ([`CG-013`](../00_Content_Governance_and_Standards/CG-013_Content_Risk_and_Legal_Escalation_Rules.md)) |

---

## 3. Channel-Specific Requirements

| Channel | Requirement |
|---|---|
| Service desk portal / email | Full macro text. Plain-text parity for every HTML reply ([`VB-005`](../01_Voice_Brand_and_Design_Content/VB-005_Email_Brand_Template_Standard.md)). Reference number in the subject line |
| In-app support thread | Macro text truncated to the first sentence in the notification preview; the full text in the thread |
| WhatsApp (`INT-012`) | Session messages only — a macro sent outside a 24-hour session window must use an approved WhatsApp template ([`NT-008`](../04_Notification_and_Messaging/04B_WhatsApp_and_Push/NT-008_WhatsApp_Business_Template_Library.md)), which these are not. **Agents cannot open a conversation with a macro** |
| SMS | Only macros 3, 26, 39, 40, 41 have short forms; Bengali SMS is UCS-2 and segments at 70 characters (`CG-010` BC-05). Long macros are never sent by SMS |
| Voice (`P10`) | Macros are the *basis* of what the agent says, not a script to read aloud. Pronunciation guidance in [`BN-017`](../11_Localisation_Bengali/BN-017_Bengali_Voice_IVR_and_Speech_Prompt_Pack.md) |
| Print / handover sheet | `mac.int.fallback` and `mac.int.catchup` are also printed for branch use during an outage (`OP-014`) |

**Accessibility ([`CG-011`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md)):** no macro relies on colour, an image, or a link label such as "click
here"; every link is described by its destination.

---

## 4. Failure and Fallback

| Failure mode | User-visible behaviour | Fallback |
|---|---|---|
| Macro library unavailable (ticket system down) | Agents answer free-form | The 12 macros marked **essential** (1, 13, 16, 17, 21, 26, 30, 41, 44, 58, 59, 66) are printed and held at each service desk and branch — `OP-014` §Support |
| Bengali rendering fails in the channel | Text shows as boxes | Agent switches to the English macro **and says so**; the fault is a `Sev2` ([`NT-025`](../04_Notification_and_Messaging/NT-025_Notification_Failure_and_Fallback_Copy.md)) |
| Wrong language selected for the recipient | User receives a language they cannot read | `mac.cust.wrong_language`, and the preference is corrected at source ([`MD-005`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-005_Dispatch_Zone_and_Territory_Master.md)) |
| Macro contains an unfilled variable | User receives `{ref}` literally | Detected by the pre-send check in `M66`; until W6, by supervisor sampling of 10 replies/agent/week |
| Macro contradicts the status page | Two versions of the truth during an incident | [`OP-004`](OP-004_Incident_Communication_Template_Set.md) §3 — the status page is authoritative; macros link to it rather than restating it |

---

## 5. Change Log

| Version | Date | Change | Approver | WhatsApp re-approval needed |
|---|---|---|---|:--:|
| 1.0 | 2026-08-20 | Initial library — 68 macros, 12 groups, bilingual except vendor/brand/English-audience macros | Content Design Lead (pending) | No — no macro is a WhatsApp template |

---

## Open Items

1. **OP-003-OI-01** — Bengali text is authored, not yet through **G4 linguistic review in context**
   ([`BN-018`](../11_Localisation_Bengali/BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md)). No macro may be published to agents before G4.
2. **OP-003-OI-02** — Macro IDs assume `M66` supports a macro library with variable substitution
   (`FR-ITS-030` implies a knowledge base, not a macro engine). Confirm, or the W1–W5 interim is a
   shared document with copy-and-paste, which weakens `MC-02`.
3. **OP-003-OI-03** — `mac.cust.dsr` states a response period as `{days}`; the statutory period must
   be set from `LG-010` once the PDPA 2026 timeline is confirmed by Legal.
4. **OP-003-OI-04** — Macros 7, 8, 50, 51, 52 are English-only by `CG-010` §3.3. Confirm with
   Procurement and Commercial that no vendor or brand contact requires Bengali; the rule is an
   audience assumption, and a Bengali-only supplier would break it.
5. **OP-003-OI-05** — Contact Centre (`P10`) console macro storage may differ from the service desk;
   confirm one library serves both, or `CP-01` is breached by a second copy.

---

## Definition of Done

Tick every box before setting `status: Approved`. Full checklist in [`CG-008`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md).

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Notification_Template.md` — all five sections present; `Open Items` added, justified
- [x] Every factual, statutory, pricing or capability claim carries a source and a verification date
- [x] Terminology matches [`CG-004`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md); Bengali terms follow [`BN-003`](../11_Localisation_Bengali/BN-003_Bilingual_Terminology_Glossary.md)
- [x] All internal links resolve
- [x] Accessibility standard `CG-011` applied — link labels, no colour dependence
- [ ] Bengali counterpart complete and signed off **in context** (`BN-018`) — **open, OI-01**
- [ ] Named approver recorded — Content Design Lead, appointment pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] Decision(s) taken while authoring logged in `RF-006` — five open items pending

**Gates required (Class D):** G1 ●, G2 ●, G3 ●, G4 ● (bilingual).

---

*`OP-003` · 1000FiX ERP Programme · CONFIDENTIAL — Internal Use Only*
