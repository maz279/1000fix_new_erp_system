---
id: BN-014
title: Bengali Notification and SMS Pack
project: 1000FiX ERP System v2.0
content_type: Notification template library
template: TPL_Notification_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Localisation Lead
author: Localisation with Content Design, Platform Engineering and Finance
reviewers: [Content Design Lead, Platform Engineering, Finance Controller, Contact Centre Manager, Legal & Compliance, Accessibility reviewer]
approver: Localisation Lead with Content Design Lead
content_class: D
purpose: >
  The Bengali counterpart of every bilingual notification template in Category 04, with
  Unicode segment counts and the send-cost consequence stated per template. Bengali SMS is UCS-2
  and segments at 70 characters, not 160, so a template that costs one segment in English can
  cost three in Bengali. At 250,000+ customers a month this is a seven-figure annual line that is
  set by wording decisions, and it must be budgeted rather than discovered. The pack also covers
  WhatsApp, push, email and in-app Bengali, whose failure modes are different and none of which
  is a character-count problem.
traces_to: [NT-001, NT-002, NT-004, NT-005, NT-006, NT-007, NT-008, NT-009, NT-010, NT-012, NT-014, NT-015, NT-016, NT-017, NT-018, NT-020, NT-022, NT-023, NT-024, NT-025, CG-010 BC-05, BN-002, BN-003, BN-005, BN-007, BN-017, MD-027, VB-005, CG-014]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: self — this file is the Bengali counterpart of the twenty bilingual `NT` template libraries
channels: [SMS, WhatsApp, Push, Email, In-app]
consent_class: Per source template — transactional, service-related or marketing
pinned_to:
  surface: All notification channels
  release: pending first build
  wave: W2
sources:
  - source: project_content/04_Notification_and_Messaging/NT-004 §2.1 and §2.3 — fifteen customer SMS templates with EN and BN segment counts; nine of fifteen Bengali templates run to two segments and one to three; library averages 1.9 Bengali segments against 1.0 English
    verified: 2026-08-17
    class: P1
  - source: SMS technical standard — a single GSM-7 message holds 160 characters; a single UCS-2 (Unicode) message holds 70; in a concatenated message the User Data Header reduces these to 153 and 67 respectively, and each segment bills separately
    verified: 2026-08-17
    class: P2
  - source: project_content/00_Content_Governance_and_Standards/CG-010 BC-05 — Bengali SMS segments at 70 characters, not 160; a 150-character English template is one segment and its Bengali equivalent may be three
    verified: 2026-08-17
    class: P1
  - source: project_content/04_Notification_and_Messaging — front matter of all 26 NT files; twenty are bilingual: yes, six are bilingual: no (NT-001, NT-003, NT-011, NT-013, NT-021, NT-026)
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# BN-014 — Bengali Notification and SMS Pack

> **Two things about this pack are commonly got wrong, and both are recorded here rather than
> discovered later.**
>
> **Its scope is twenty files, not sixteen.** The Master Index describes this file as covering
> `NT-004` … `NT-019`. Enumerating the `NT` front matter gives **twenty** bilingual files, and
> **six of them fall outside that range** — `NT-002`, `NT-020`, `NT-022`, `NT-023`, `NT-024` and
> `NT-025`. `NT-019` is inside the range but belongs to **`BN-017`**, not here. Recorded as
> `AUDIT-012` **BN-04**; the scope below is the enumerated one.
>
> **Its `P0` content is needed at W1, not W2.** `NT-007` OTP and security messages is `P0` at
> **W1** and bilingual. Authentication is the first thing a Bengali user meets, and it ships a
> wave before this pack's registered wave. §3 delivers it early; `AUDIT-012` **BN-02** records it.

---

## 1. Scope — enumerated, not quoted

| `NT` file | Channel | Bilingual | Wave | Covered here |
|---|---|:--:|:--:|:--:|
| `NT-002` Preference and consent copy | All | Yes | W2 | **✔ §7** |
| `NT-004` SMS — customer | SMS | Yes | W2 | ✔ §3 |
| `NT-005` SMS — technician and field | SMS | Yes | W2 | ✔ §3 |
| `NT-006` SMS — finance and collections | SMS | Yes | W3 | ✔ §3 |
| `NT-007` OTP and security | SMS | Yes | **W1** | ✔ §3 — **early** |
| `NT-008` WhatsApp Business | WhatsApp | Yes | W2 | ✔ §4 |
| `NT-009` Email — customer transactional | Email | Yes | W2 | ✔ §6 |
| `NT-010` Email — corporate and B2B | Email | Yes | W4 | ✔ §6 |
| `NT-012` Email — seller and partner | Email | Yes | W7 | ✔ §6 |
| `NT-014` Email — internal and HR | Email | Yes | W5 | ✔ §6 |
| `NT-015` Push — `P01` | Push | Yes | W6 | ✔ §5 |
| `NT-016` Push — `P02` | Push | Yes | W2 | ✔ §5 |
| `NT-017` Push — `P09` | Push | Yes | W3 | ✔ §5 |
| `NT-018` In-app and inbox | In-app | Yes | W2 | ✔ §7 |
| `NT-020` Escalation and SLA breach | Multi | Yes | W2 | **✔ §8** |
| `NT-022` Approval request and reminder | Multi | Yes | W2 | **✔ §8** |
| `NT-023` Marketing and lifecycle | Multi | Yes | W4 | **✔ §9** |
| `NT-024` Survey, feedback and NPS | Multi | Yes | W2 | **✔ §9** |
| `NT-025` Failure and fallback copy | All | Yes | W2 | **✔ §10** |
| `NT-011` Email — vendor | Email | **No** | W3 | Out of scope by `CG-010` §3.2 |
| `NT-013` Email — brand partner | Email | **No** | W4 | Out of scope |
| `NT-001`, `NT-003`, `NT-021`, `NT-026` | — | **No** | — | Governance and internal alerting |
| **`NT-019` IVR and voice** | **Voice** | **Yes** | **W4** | **→ `BN-017`, not here** |

**Nineteen bilingual template libraries are covered here; `NT-019` is covered by `BN-017`.**
Twenty bilingual `NT` files in total, reconciling to `CG-010` §3.2.

---

## 2. The SMS economics

### 2.1 The encoding facts

| | GSM-7 (English) | **UCS-2 (Bengali)** |
|---|---:|---:|
| Single message | **160** characters | **70** characters |
| Each segment of a concatenated message | 153 | **67** |
| Why the drop | — | The User Data Header consumes payload in every segment |

**A single Bengali character costs the same as a Bengali sentence's worth of English.** There is
no partial encoding: **one** Bengali character in an otherwise-English message switches the whole
message to UCS-2 and drops it from 160 to 70.

| # | Rule |
|---|---|
| **SM-01** | **Segment count is recorded for both languages on every template** (`CG-008` NT-e) |
| **SM-02** | Segment count is measured at the **realistic maximum placeholder length**, not at the example value (`BN-005` §8). A `{branch}` of "আগ্রাবাদ সার্ভিস সেন্টার" is 23 characters, a third of a segment |
| **SM-03** | **Never mix a single English word into a Bengali SMS to save space.** It does not save space; UCS-2 is already in force |
| **SM-04** | Conversely, **a Tier 1 item in an otherwise Bengali message costs nothing extra** — the message is UCS-2 regardless. `Mushak 6.3` and `bKash` stay Latin (`BN-004`) without a cost argument against them |
| **SM-05** | **No emoji in any Bengali SMS.** They inflate UCS-2 segments and render inconsistently on feature phones (`NT-004` §3) |
| **SM-06** | A wording change that **moves a template across a segment boundary** requires Content Design Lead approval and is logged in `NT-026` (`NT-004` `CS-06`) |
| **SM-07** | **Shortening Bengali below the point of clarity to save a segment is prohibited.** The remedy for a three-segment message is to remove a fact, decided by the owner, not to compress the language |

### 2.2 The cost consequence

`NT-004` measures its own library at **1.9 Bengali segments against 1.0 English** — Bengali SMS
costs roughly **1.9×** the English equivalent at the same volume.

| Driver | Value |
|---|---|
| Customers | 250,000+ per month |
| Messages per service order | Several (`NT-001` matrix) |
| Bengali share of sends | **Majority** — Bengali is the default (`PS-03`) |
| Multiplier vs English | **≈ 1.9×** on the customer library |
| Where it is tracked | `CG-014`; template-level changes in `NT-026` |

> **This is the correct trade and it must be an explicit one.** `PS-03` makes Bengali the default
> and reach is the point. The failure mode is not the cost; it is the cost being **discovered**
> in month 14 and answered by silently switching templates to English.

| # | Rule |
|---|---|
| **SM-08** | **Bengali is never downgraded to English to reduce send cost.** That decision is a `PS-03` breach and requires Steering Committee authority, not an operations decision |
| **SM-09** | The Bengali SMS multiplier is **stated in the notification budget** at W1, before the first bulk send |

---

## 3. SMS — Bengali templates

### 3.1 Customer — `NT-004`

Bengali templates as approved in `NT-004` §2.1, with the corrections this pack applies.

| # | Template ID | **Bengali** | BN seg |
|---|---|---|:--:|
| 1 | `sms.cust.booked` | 1000FiX: বুকিং গৃহীত। রেফ {ref}। আমরা {time}-এর আগে যোগাযোগ করব। | 1 |
| 2 | `sms.cust.assigned` | 1000FiX: {date} তারিখে {from}–{to} সময়ে {tech} আসবেন। রেফ {ref}। | 2 |
| 3 | `sms.cust.on_way` | 1000FiX: {tech} আসছেন। প্রায় {minutes} মিনিট। | 1 |
| 4 | `sms.cust.received` | 1000FiX: আপনার {device} আমরা পেয়েছি। রেফ {ref}। ট্র্যাক করুন {link}। | 2 |
| 5 | `sms.cust.estimate` | 1000FiX: আপনার মেরামতের এস্টিমেট {amount}। শুরু করতে {link}-এ অনুমোদন দিন। রেফ {ref}। | 2 |
| 6 | `sms.cust.approved` | 1000FiX: ধন্যবাদ। আপনার {device}-এর কাজ শুরু করেছি। রেফ {ref}। | 2 |
| 7 | `sms.cust.awaiting_part` | 1000FiX: আপনার {device}-এর একটি পার্টসের অপেক্ষায় আছি। প্রত্যাশিত {date}। রেফ {ref}। | 2 |
| 8 | `sms.cust.ready` | 1000FiX: আপনার {device} প্রস্তুত। {branch} থেকে সংগ্রহ করুন, {hours}। রেফ {ref}। | 2 |
| 9 | `sms.cust.out_delivery` | 1000FiX: আপনার {device} আজ ডেলিভারির পথে। রেফ {ref}। | 2 |
| 10 | `sms.cust.delivered` | 1000FiX: পৌঁছে দেওয়া হয়েছে। 1000FiX বেছে নেওয়ার জন্য ধন্যবাদ। রেফ {ref}। | 2 |
| 11 | `sms.cust.completed` | 1000FiX: সার্ভিস সম্পন্ন। মেরামত ওয়ারেন্টি {months} মাস। রেফ {ref}। | 2 |
| 12 | `sms.cust.delayed` | 1000FiX: আপনার মেরামত পরিকল্পনার চেয়ে বেশি সময় নিচ্ছে। নতুন তারিখ {date}। রেফ {ref}। | 3 |
| 13 | `sms.cust.cancelled` | 1000FiX: অর্ডার {ref} বাতিল। কোনো পেমেন্ট {days} দিনের মধ্যে ফেরত দেওয়া হবে। | 2 |
| 14 | `sms.cust.paid` | 1000FiX: {amount} গৃহীত। ধন্যবাদ। রেফ {ref}। | 1 |
| 15 | `sms.cust.uncollected` | 1000FiX: {date} থেকে আপনার {device} প্রস্তুত আছে। {branch} থেকে সংগ্রহ করুন। রেফ {ref}। | 3 |

**Variable formatting corrections applied** (`BN-007` §3.4):

| Variable | `NT-004` example | **Corrected** | Reason |
|---|---|---|---|
| `{amount}` | `৳ ৩,২০০.০০` | **`৳ 3,200.00`** | Money is Arabic digits (`BN-007` `NM-A`, §3.3) |
| `{device}` | `ল্যাপটপ` | Unchanged | Tier 2, correct |
| `{branch}` | `আগ্রাবাদ সার্ভিস সেন্টার` | Unchanged, but **23 characters — a third of a segment** (`SM-02`) |
| `{ref}` | `SR-2026-114882` | Unchanged | Tier 1, Arabic digits (`BN-004` `DN-04`) |

| # | Rule |
|---|---|
| **CS-B01** | Every message opens `1000FiX:` in Latin, so the sender is identifiable even where masking is stripped (`NT-004` `CS-01`) |
| **CS-B02** | Every message carries `{ref}` — it is what the customer quotes on the hotline, and the IVR asks for it (`BN-017`) |
| **CS-B03** | **Status wording is `MD-027` `customer_label_bn`.** `sms.cust.delayed` says **বিলম্বিত**, never এসএলএ লঙ্ঘিত (`BN-003` `ST-03`, `NT-004` `CS-04`) |
| **CS-B04** | **No promotional content** in a transactional template. One promotional line reclassifies the whole message and changes its routing (`NT-001` BD-03) |

### 3.2 Technician and field — `NT-005`

| Template ID | **Bengali** | BN seg |
|---|---|:--:|
| `sms.tech.assigned` | 1000FiX: নতুন জব {ref}, {area}, {time}। অ্যাপে দেখুন। | 1 |
| `sms.tech.urgent` | 1000FiX: জরুরি জব {ref}, {area}। এখনই অ্যাপে গ্রহণ করুন। | 2 |
| `sms.tech.cancelled` | 1000FiX: জব {ref} বাতিল হয়েছে। যাবেন না। | 1 |
| `sms.tech.part_ready` | 1000FiX: {part} {branch}-এ প্রস্তুত। জব {ref}। | 2 |
| `sms.tech.cert_expiry` | 1000FiX: আপনার {cert} সার্টিফিকেশনের মেয়াদ {date} তারিখে শেষ। নবায়ন করুন। | 2 |
| `sms.tech.roster` | 1000FiX: আগামীকালের শিফট {from}–{to}, {branch}। | 1 |

### 3.3 Finance and collections — `NT-006`

| Template ID | **Bengali** | BN seg |
|---|---|:--:|
| `sms.fin.invoice` | 1000FiX: ইনভয়েস {inv}, {amount}। প্রদেয় {date}। {link} | 2 |
| `sms.fin.due_soon` | 1000FiX: {amount} {date} তারিখে প্রদেয়। ইনভয়েস {inv}। | 2 |
| `sms.fin.overdue` | 1000FiX: ইনভয়েস {inv}-এর {amount} {days} দিন বকেয়া। পরিশোধ করুন {link}। | 3 |
| `sms.fin.received` | 1000FiX: {amount} পেয়েছি। ধন্যবাদ। রসিদ {rec}। | 2 |
| `sms.fin.refund` | 1000FiX: {amount} ফেরত পাঠানো হয়েছে। {days} কার্যদিবসে পৌঁছাবে। | 2 |

| # | Rule |
|---|---|
| **FN-B01** | Dunning messages are **firm and unambiguous, never threatening** (`BN-002` `TN-08`, `DT-018`) |
| **FN-B02** | **কার্যদিবস (working day), never দিন**, wherever a payment or refund window is stated (`BN-007` `FM-26`, `BD-04`) |
| **FN-B03** | Amounts are Arabic digits with the `৳` prefix (`BN-007` `FM-07`) |

### 3.4 OTP and security — `NT-007`, needed at **W1**

**Short by design.** OTP messages are read under time pressure and must be single-segment.

| Template ID | **Bengali** | BN seg | Note |
|---|---|:--:|---|
| `sms.otp.login` | 1000FiX: আপনার কোড {otp}। {minutes} মিনিটে শেষ। কাউকে দেবেন না। | **1** | 62 characters |
| `sms.otp.register` | 1000FiX: রেজিস্ট্রেশন কোড {otp}। {minutes} মিনিটে শেষ। | **1** | |
| `sms.otp.transaction` | 1000FiX: {amount} অনুমোদনের কোড {otp}। কাউকে দেবেন না। | **1** | |
| `sms.sec.new_device` | 1000FiX: নতুন ডিভাইস থেকে সাইন ইন। আপনি না করলে 16743-এ কল করুন। | 2 | |
| `sms.sec.password` | 1000FiX: আপনার পাসওয়ার্ড পরিবর্তন হয়েছে। আপনি না করলে 16743-এ কল করুন। | 2 | |

| # | Rule |
|---|---|
| **OT-B01** | **The OTP itself is always Arabic digits** (`BN-007` `NM-D`). A Bengali-digit OTP cannot be typed on a Latin keypad, cannot be pasted reliably, and cannot be read back over a phone |
| **OT-B02** | **"কাউকে দেবেন না" appears in every code-bearing message.** It is the anti-fraud line and it is not dropped to save characters |
| **OT-B03** | Every OTP template must fit **one segment**. A two-segment OTP can arrive out of order and be unreadable |
| **OT-B04** | OTP and security messages route **masked** and deliver to DND numbers (`NT-004` §3) |
| **OT-B05** | **These templates are needed at W1**, one wave before this pack's registered wave (`AUDIT-012` **BN-02**) |

---

## 4. WhatsApp — `NT-008`

WhatsApp is not SMS with a different pipe. Its constraint is **template approval**, not segments.

| # | Rule |
|---|---|
| **WA-01** | **Each language is a separate template submission.** The Bengali template is approved independently and can be rejected independently. A template live in English and pending in Bengali is a **partial-bilingual surface** (`BP-05`) and must not be enabled |
| **WA-02** | **Category matters.** A Utility template carrying a promotional line is rejected or reclassified, and reclassification changes both cost and consent basis (`NT-002`) |
| **WA-03** | Variables are positional in WhatsApp's own format. The **Bengali word order will differ from the English** (`BN-002` `SC-01`), so the variable **mapping is verified per language**, not copied |
| **WA-04** | Bengali renders reliably in the WhatsApp client; **the failure mode is template rejection, not rendering** |
| **WA-05** | Button and quick-reply labels are **strings with their own length limits** and are translated, not left in English |
| **WA-06** | Template changes require re-approval. **The Bengali and English versions must be re-approved together**, or the pair drifts (`LC-08`) |

| Template | **Bengali body** |
|---|---|
| `wa.cust.booked` | 1000FiX: বুকিং গৃহীত। রেফ {1}। {2}-এর আগে আমরা যোগাযোগ করব। |
| `wa.cust.estimate` | 1000FiX: আপনার এস্টিমেট {1} প্রস্তুত। অনুমোদন দিতে নিচের বাটনে চাপুন। |
| `wa.cust.ready` | 1000FiX: আপনার {1} প্রস্তুত। {2} থেকে সংগ্রহ করুন। |
| `wa.cust.feedback` | 1000FiX: আপনার সার্ভিস কেমন ছিল? এক মিনিটে জানান। |
| Button — approve | **অনুমোদন করুন** |
| Button — track | **ট্র্যাক করুন** |
| Button — talk to us | **কথা বলুন** |

---

## 5. Push — `NT-015`, `NT-016`, `NT-017`

| Constraint | Value |
|---|---|
| Title | **≤ 30 Bengali characters** — Android and iOS truncate around 40; Bengali needs headroom |
| Body | **≤ 100 Bengali characters** visible before expansion |
| Locale | Follows the app's language, not the device's (`BN-001` `LR-01`) |
| Font | The system Bengali face renders the notification shade, **not the bundled app font** (`VB-009` rank 2) |

| Surface | Key | **Bengali title** | **Bengali body** |
|---|---|---|---|
| `P01` | `push.p01.estimate` | **এস্টিমেট প্রস্তুত** | আপনার {device}-এর এস্টিমেট {amount}। অনুমোদন দিন। |
| `P01` | `push.p01.on_way` | **টেকনিশিয়ান আসছেন** | {tech} প্রায় {minutes} মিনিটে পৌঁছাবেন। |
| `P01` | `push.p01.ready` | **ডিভাইস প্রস্তুত** | {branch} থেকে সংগ্রহ করুন। |
| `P02` | `push.p02.new_job` | **নতুন জব** | {area}, {time}। গ্রহণ করুন বা ফিরিয়ে দিন। |
| `P02` | `push.p02.urgent` | **জরুরি জব** | {area}। এখনই সাড়া দিন। |
| `P02` | `push.p02.sync_failed` | **সিঙ্ক হয়নি** | {n}টি কাজ পাঠানো যায়নি। সেগুলো নিরাপদে আছে। |
| `P09` | `push.p09.route` | **আজকের রুট প্রস্তুত** | {n}টি স্টপ। শুরু করুন। |
| `P09` | `push.p09.cod` | **ক্যাশ জমা দিন** | {amount} {branch}-এ জমা দিন। |

| # | Rule |
|---|---|
| **PU-01** | **The notification shade uses the system Bengali font, not the bundled one.** A push title verified only in-app is not verified (`VB-009` `MM-04`, `BN-006` `RV-12`) |
| **PU-02** | Titles are **nouns or short states**, not sentences — the truncation point is unpredictable across launchers |
| **PU-03** | `push.p02.sync_failed` **reassures in the body** because the technician's first fear is lost work (`BN-011` `OF-B01`) |
| **PU-04** | Push is a **duplicate of a durable message**, never the only delivery of a fact (`NT-001`) |

---

## 6. Email — `NT-009`, `NT-010`, `NT-012`, `NT-014`

Email's Bengali failure mode is **font fallback**, not length.

| # | Rule |
|---|---|
| **EM-01** | Email is **designed at rank 2 — Noto Sans Bengali** (`VB-005` BF-01, `VB-009` `TF-04`). Custom web fonts load reliably only in Apple Mail |
| **EM-02** | **Bengali is never rendered as an image to guarantee a font** (`VB-009` `BR-06`, `CG-011` AT-07). It breaks accessibility, search, copy and image-blocked clients |
| **EM-03** | **Subject and preview text are strings** and are translated. A Bengali email with an English subject line looks like phishing |
| **EM-04** | **Plain-text parity.** The plain-text part carries the same Bengali, UTF-8 encoded, not an English summary (`VB-005`) |
| **EM-05** | Alt text on every image is Bengali (`CG-011`) |
| **EM-06** | Verified in **Gmail Android, Gmail web, Outlook desktop and Apple Mail iOS** (`VB-009` §7) — Outlook desktop uses Nirmala UI, rank 3 |
| **EM-07** | Attachment **file names are Latin** (`BN-004` §7); the **link text** is Bengali |
| **EM-08** | **`NT-011` vendor and `NT-013` brand-partner email remain English** (`CG-010` §3.2). Declared, not omitted |

| Key | **Bengali subject** | **Bengali preview** |
|---|---|---|
| `email.cust.booking` | বুকিং নিশ্চিত — রেফ {ref} | {date} তারিখে {time} সময়ে আমরা আসছি |
| `email.cust.estimate` | আপনার এস্টিমেট প্রস্তুত — {amount} | অনুমোদন দিলে আমরা কাজ শুরু করব |
| `email.cust.invoice` | ইনভয়েস {inv} — {amount} | প্রদেয় {date} |
| `email.cust.completed` | সার্ভিস সম্পন্ন — রেফ {ref} | মেরামত ওয়ারেন্টি {months} মাস |
| `email.hr.payslip` | {month} মাসের পে-স্লিপ | সংযুক্ত ফাইলটি পাসওয়ার্ড দিয়ে সুরক্ষিত |
| `email.corp.statement` | {month} মাসের হিসাব বিবরণী | {n}টি ইনভয়েস, সর্বমোট {amount} |

---

## 7. In-app, preference and consent — `NT-018`, `NT-002`

| Key | **Bengali** |
|---|---|
| `inbox.title` | **নোটিফিকেশন** |
| `inbox.empty` | **কোনো নোটিফিকেশন নেই** |
| `inbox.mark_read` | **পঠিত হিসেবে চিহ্নিত করুন** |
| `inbox.older` | **পুরোনো** |
| `pref.title` | **নোটিফিকেশন পছন্দ** |
| `pref.channel.sms` | **SMS** |
| `pref.channel.whatsapp` | **WhatsApp** |
| `pref.channel.email` | **ইমেইল** |
| `pref.channel.push` | **পুশ** |
| `pref.transactional` | **সার্ভিস সংক্রান্ত বার্তা** |
| `pref.transactional.note` | **এগুলো বন্ধ করা যায় না — আপনার সার্ভিসের জন্য প্রয়োজনীয়।** |
| `pref.marketing` | **অফার ও খবর** |
| `pref.marketing.note` | **আপনি যেকোনো সময় বন্ধ করতে পারেন।** |
| `pref.quiet` | **রাত ৯টা থেকে সকাল ৮টা পর্যন্ত জরুরি নয় এমন বার্তা পাঠানো হয় না।** |
| `pref.language` | **বার্তার ভাষা** |

| # | Rule |
|---|---|
| **PR-B01** | `pref.transactional.note` states plainly that service messages cannot be switched off. **Presenting a toggle that does nothing is worse than presenting none** (`NT-002`) |
| **PR-B02** | `pref.language` writes to **`fix.party.preferred_language`**, the source of truth for outbound messaging (`BN-001` `LR-01`) |
| **PR-B03** | Quiet hours are **08:00–21:00 Asia/Dhaka** (`NT-003`, `BN-007` `BD-08`) and are stated in the Bengali using **day-period words**, not AM/PM (`BN-007` `FM-20`) |

---

## 8. Escalation, SLA and approvals — `NT-020`, `NT-022`

| Key | **Bengali** | Audience |
|---|---|---|
| `esc.sla_risk` | {ref} SLA ঝুঁকিতে। {minutes} মিনিট বাকি। | Internal |
| `esc.sla_breached` | {ref}-এ SLA লঙ্ঘিত হয়েছে। {role}-কে জানানো হয়েছে। | **Internal only** |
| `esc.customer_delay` | আপনার মেরামত পরিকল্পনার চেয়ে বেশি সময় নিচ্ছে। নতুন তারিখ {date}। | **Customer** |
| `esc.complaint_open` | অভিযোগ {ref} খোলা হয়েছে। {hours} ঘণ্টার মধ্যে সাড়া দিতে হবে। | Internal |
| `appr.requested` | {requester} {amount} অনুমোদনের জন্য পাঠিয়েছেন। | Internal |
| `appr.override` | {requester} {rule}-এর ওভাররাইড অথরাইজ করতে বলেছেন। | Internal |
| `appr.reminder` | {n}টি অনুমোদন {hours} ঘণ্টা ধরে অপেক্ষমাণ। | Internal |
| `appr.escalated` | অনুমোদন {ref} {role}-এর কাছে এসকেলেট করা হয়েছে। | Internal |

| # | Rule |
|---|---|
| **ES-B01** | **`esc.sla_breached` is internal.** The customer message is `esc.customer_delay` and says **বিলম্বিত**, never SLA লঙ্ঘিত (`BN-003` `ST-03`) — the internal and customer messages for one event use different Bengali by design |
| **ES-B02** | `appr.override` uses **অথরাইজ**, not অনুমোদন (`BN-003` §9, `BN-011` `CE-02`). The audit trail must distinguish them in Bengali |
| **ES-B03** | SLA timing is computed against the **`MD-041` business calendar with a Friday–Saturday weekend** (`BN-007` `BD-01`). A breach notification fired against the wrong weekend is a false breach with a financial tail |

---

## 9. Marketing, survey and feedback — `NT-023`, `NT-024`

| # | Rule |
|---|---|
| **MK-B01** | Marketing SMS routes **non-masking** and does **not** deliver to DND numbers (`NT-001` §3.1). The Bengali content does not change that; the classification does |
| **MK-B02** | **A transactional template that gains a promotional line is reclassified** and loses DND delivery. In Bengali this is easy to do accidentally — a warm closing line can read as promotional |
| **MK-B03** | Marketing Bengali may use **Bengali digits in prose** (`BN-007` §3.2) but **never in a price or a discount amount** |
| **MK-B04** | Survey invitations are **short and state the time cost**: "এক মিনিটে জানান" |
| **MK-B05** | Marketing consent is separate from service consent (`NT-002`, `LG-008`) and the Bengali must not blur them |

| Key | **Bengali** |
|---|---|
| `mkt.offer` | 1000FiX: {offer}। {date} পর্যন্ত। বিস্তারিত {link}। বন্ধ করতে STOP লিখে পাঠান। |
| `svy.nps` | 1000FiX: ১ থেকে ১০-এ, আপনি কি 1000FiX অন্যদের সুপারিশ করবেন? উত্তর দিন {link} |
| `svy.csat` | 1000FiX: আপনার সার্ভিস কেমন ছিল? এক মিনিটে জানান {link} |
| `svy.thanks` | 1000FiX: ধন্যবাদ। আপনার মতামত আমরা কাজে লাগাব। |

---

## 10. Failure and fallback — `NT-025`

| Key | **Bengali** |
|---|---|
| `fb.sms_failed` | আমরা আপনাকে SMS পাঠাতে পারিনি। ইমেইলে পাঠানো হয়েছে। |
| `fb.email_failed` | আমরা আপনাকে ইমেইল পাঠাতে পারিনি। নম্বরটি দেখে নিন। |
| `fb.number_invalid` | এই নম্বরে বার্তা পৌঁছাচ্ছে না। আপনার নম্বর হালনাগাদ করুন। |
| `fb.channel_down` | কিছু বার্তা দেরিতে পৌঁছাতে পারে। আপনার সার্ভিস স্বাভাবিকভাবে চলছে। |

| # | Rule |
|---|---|
| **FB-B01** | A fallback message **names the channel that was used instead**, so the customer knows where to look |
| **FB-B02** | `fb.channel_down` **separates the messaging failure from the service** — the customer's first fear is that the repair has stopped |

---

## 11. Governance

| Item | Position |
|---|---|
| Who may add a Bengali template | Localisation with the owning `NT` file's business owner |
| Who may change Bengali wording | Localisation Lead; Legal where the class is A or B |
| **Segment-boundary changes** | Content Design Lead approval, logged in `NT-026` (`SM-06`) |
| Version and approval | `NT-026`; the English and Bengali pair versions together (`LC-08`) |
| WhatsApp re-approval | Both languages together (`WA-06`) |
| Review | Per wave; immediately on a rule, rate or route change |

---

## 12. Coverage ledger

**Counted by enumeration on 2026-08-17** (`CP-11`, `CM-R2`, F7).

| Channel | `NT` files covered | **Bengali template IDs authored here** |
|---|---:|---:|
| SMS — customer, technician, finance, OTP | 4 | 31 |
| WhatsApp | 1 | 4 + 3 button labels |
| Push | 3 | 8 |
| Email — subject and preview pairs | 4 | 6 |
| In-app, preference, consent | 2 | 16 |
| Escalation and approval | 2 | 8 |
| Marketing and survey | 2 | 4 |
| Failure and fallback | 1 | 4 |
| **Total** | **19** | **80 template IDs** |
| Voice — `NT-019` | 1 | **→ `BN-017`, not here** |
| **Bilingual `NT` files reconciled** | **20** | ✔ matches `CG-010` §3.2 |

| Measure | Counted |
|---|---:|
| Template IDs authored in this pack | **80** |
| Template IDs enumerated across all of Category 04 | **117** |
| **Remaining to author** | **37** — the six English-only files account for part of it; the balance is unauthored Bengali |

> **The earlier issue of this table said "84 templates". The counted figure is 80**, and the
> 117-against-80 comparison it omitted is the more useful number. Recorded as `AUDIT-012`
> **BN-19**.

---

## 13. Open items

| # | Item | Owner | Blocks |
|---|---|---|---|
| 1 | **`NT-007` OTP Bengali needed at W1**, a wave before this pack (`OT-B05`) | Programme Content Lead | W1 authentication |
| 2 | **`NT-019` is mislabelled as `BN-014`'s counterpart**; correct it to `BN-017` (`BN-003` §11 D-7) | `NT-019` owner | `BN-017` scope clarity |
| 3 | **`NT-004` `{amount}` example uses Bengali digits** and must be corrected (`BN-007` §3.4) | `NT-004` owner | Money formatting consistency |
| 4 | Bengali SMS multiplier entered in the notification budget (`SM-09`) | Finance with Platform Engineering | W1 budget |
| 5 | WhatsApp Bengali templates submitted and approved by Meta before `P01` go-live (`WA-01`) | Platform Engineering | W2 |
| 6 | `BN-002` and `BN-007` ratification | Programme Content Lead | Every template |

---

## 14. Related documents

| Document | Relationship |
|---|---|
| [`../04_Notification_and_Messaging/04A_SMS_and_OTP/NT-004_SMS_Template_Library_Customer.md`](../04_Notification_and_Messaging/04A_SMS_and_OTP/NT-004_SMS_Template_Library_Customer.md) | The English source and the segment analysis |
| [`../04_Notification_and_Messaging/NT-001_Notification_Strategy_and_Event_Channel_Matrix.md`](../04_Notification_and_Messaging/NT-001_Notification_Strategy_and_Event_Channel_Matrix.md) | Which events send which channel |
| [`BN-017_Bengali_Voice_IVR_and_Speech_Prompt_Pack.md`](BN-017_Bengali_Voice_IVR_and_Speech_Prompt_Pack.md) | `NT-019`, which is **not** in this pack |
| [`BN-007_Date_Time_Number_Currency_and_Address_Formats.md`](BN-007_Date_Time_Number_Currency_and_Address_Formats.md) | Amount, date and working-day formatting |
| [`../01_Voice_Brand_and_Design_Content/VB-005_Email_Brand_Template_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-005_Email_Brand_Template_Standard.md) | Email font fallback |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-027_Status_and_Lifecycle_State_Label_Register.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-027_Status_and_Lifecycle_State_Label_Register.md) | Customer status wording |

---

## 15. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-17 | Initial issue. **Scope enumerated to nineteen bilingual `NT` libraries rather than the register's `NT-004`–`NT-019` range**, with `NT-019` routed to `BN-017`; UCS-2 economics stated with the 70/67 segment facts and the 1.9× multiplier, and the never-downgrade-to-English rule; **80 Bengali template IDs counted** across five channels; OTP templates delivered early for W1 with the single-segment and Arabic-digit rules; WhatsApp per-language approval risk; push notification-shade font rule; email rank-2 design and plain-text parity; internal-versus-customer SLA wording separated | Localisation Lead with Content Design Lead (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:`, `traces_to:`, `channels:` and `consent_class:`
- [x] **Scope enumerated from the `NT` front matter, not quoted from the register**, and reconciled to `CG-010` §3.2
- [x] Bengali segment counts recorded for every SMS template (`CG-008` NT-e)
- [x] Segment measurement rule stated against the realistic maximum, not the example
- [x] **The cost consequence stated, with the never-downgrade-to-English rule that protects `PS-03`**
- [x] Status wording quoted from `MD-027` `customer_label_bn`, with the internal/customer split held
- [x] OTP rules cover the Arabic-digit and single-segment requirements
- [x] WhatsApp treated as a template-approval problem, not a length problem
- [x] Push treated as a system-font problem, email as a fallback-font problem
- [x] Consent and preference copy states plainly what cannot be turned off
- [x] Variables declared with their source field and their Bengali length impact
- [x] All internal links resolve
- [ ] **G4 in-context sign-off — on a real handset, in a real inbox** — outstanding; blocks `Approved`
- [ ] **`NT-007` Bengali delivered at W1** — outstanding; §13 item 1
- [ ] **WhatsApp Bengali templates approved by Meta** — outstanding; §13 item 5
- [ ] Corrections to `NT-004` and `NT-019` applied at source — outstanding
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
