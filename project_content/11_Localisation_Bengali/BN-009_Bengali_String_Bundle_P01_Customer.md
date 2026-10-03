---
id: BN-009
title: Bengali String Bundle — P01 Customer
project: 1000FiX ERP System v2.0
content_type: Bengali string bundle
template: TPL_UI_Copy_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Localisation Lead
author: Localisation with Content Design and a native Bengali linguistic reviewer
reviewers: [Content Design Lead, P01 owner, Accessibility reviewer, Design System, Legal & Compliance for consent strings]
approver: Localisation Lead with Content Design Lead
content_class: D
purpose: >
  The Bengali bundle for P01 — the default language of the surface, not its translation. It
  carries the p01.* namespace and the customer-facing flow.* copy, against the English source in
  UI-011 and UI-037 to UI-040 and UI-042. P01 serves 250,000+ customers a month with Bengali as
  the default and English as the toggle; the Bengali build is therefore the build. A missing
  Bengali string here is not a degradation to English, it is a build failure.
traces_to: [P01, UI-011, UI-037, UI-038, UI-039, UI-040, UI-042, BN-001 §3.1, BN-002, BN-003, BN-005, BN-006, BN-007, BN-018, MD-027, 04-00 PS-03, 04-00 §P01]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: self — this file is the Bengali counterpart of `UI-011` and the customer-facing `flow.*` packs
i18n_namespace: "`p01.*` and the customer-facing subset of `flow.*`"
pinned_to:
  surface: P01
  release: pending first build
  wave: W2
sources:
  - source: project_content/03_UI_Copy_and_Microcopy/03B_Portals/UI-011 §1–§8 — the English source pack, its indicative Bengali, slot budgets and terminology bindings marked pending BN-003
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P01 Capability Set and Design Requirements — Bengali-first with English toggle, professionally translated not machine-translated, booking in ≤ 3 steps, 3G with under 400 KB first load, WCAG 2.1 AA
    verified: 2026-08-17
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-027 §9 — customer_label_bn values, the authority for every status string in §5
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# BN-009 — Bengali String Bundle — P01 Customer

> **This is not a translation of `UI-011`. It is the shipping surface.**
>
> `PS-03` makes Bengali the default on `P01` and `04-00` §P01 makes English the toggle. The
> English bundle is the exception path (`BN-001` `LS-02`). Every string here is judged on whether
> a Bangladeshi customer would say it, not on whether it maps neatly to the English.
>
> **Status: authored, not signed off.** No string below is approved until it has passed G4
> in-context review on the built surface (`BN-018`). `CG-008` `B-09` makes that unwaivable.

---

## 1. Bundle summary

| Item | Value |
|---|---|
| Surface | `P01` — individual customers, 250,000+/month |
| Locale | **`bn-BD`** (`BN-005` `BU-07`) |
| Namespace | `p01.*`, plus the customer-facing subset of `flow.*` |
| Source pack | `UI-011`, `UI-037`, `UI-038`, `UI-039`, `UI-040`, `UI-042` |
| Default on this surface | **Bengali** |
| English bundle | `UI-011` — the toggle, not the baseline |
| Framework | Next.js 15 (web) + React Native (app) |
| Register | চলিত, warm (`BN-002` §8) |
| Address | আপনি / করুন (`BN-002` `AD-01`) |
| Numerals | **Arabic**, except in help prose (`BN-007` §3) |
| Sentence budget | **≤ 20 words**, measured in Bengali (`VB-002` §4.2, `BN-002` `SC-04`) |
| Strings in this issue | **126 — counted** (`p01.*` 104 · customer `flow.*` 22). See §10 |
| Completeness required | **100%** before the W2 gate (`BN-001` `LS-04`) |
| Content class | D — User-facing |

---

## 2. Namespace boundary

| Namespace | Where its Bengali lives | Rule |
|---|---|---|
| `p01.*` | **Here** | — |
| `flow.booking.*`, `flow.estimate.*`, `flow.payment.*`, `flow.register.*`, `flow.consent.*` | **Here** — the customer-facing flows | `BN-001` §8 |
| `flow.search.*` (`UI-041`) | `BN-011` — admin-facing | `BN-001` `LS-08` |
| **`common.*`** | **`BN-011` §6 — interim, pending `BN-019`** | `BN-001` `LS-07` |

| # | Rule |
|---|---|
| **SB-01** | **No `common.*` key appears in this file.** A shared string translated here would diverge from the same string on `P02` (`BN-001` `LS-08`) |
| **SB-02** | Status text is **quoted from `MD-027` `customer_label_bn`**, never re-translated (`BN-003` `ST-01`) |
| **SB-03** | Every string cites its `UI-011` source row. This bundle adds no string that the English pack does not have |

---

## 3. Terminology in force

From `BN-003`. **This bundle cites; it never invents** (`BN-003` `GL-06`).

| Concept | Bengali | Tier | Note |
|---|---|:--:|---|
| customer / you | গ্রাহক / আপনি | 3 | `AD-01` |
| service centre | সার্ভিস সেন্টার | 2 | Customer-facing pair of *branch* |
| my services | আমার সার্ভিস | — | Customer presentation of *service order* |
| estimate | এস্টিমেট | 2 | Never কোটেশন |
| spare part | পার্টস | 2 | Customer-facing pair of *part* |
| device | ডিভাইস | 2 | |
| warranty | ওয়ারেন্টি | 2 | Never গ্যারান্টি |
| AMC / RAMC | AMC / RAMC | 1 | Expanded on first use |
| receipt | রসিদ | 3 | |
| Privilege | Privilege | 1 | Never প্রিভিলেজ (`BN-004` §4.1) |
| bKash, Nagad | bKash, Nagad | 1 | Latin in ERP content (`BN-004` §4.2) |
| **Delayed** | **বিলম্বিত** | — | **Never এসএলএ লঙ্ঘিত** (`BN-003` `ST-03`) |

---

## 4. Screen copy

### 4.1 Home — `p01.home.*`

| Key | English (`UI-011`) | **Bengali** | Slot | Budget |
|---|---|---|---|---:|
| `p01.home.greeting` | Hello {name} | **স্বাগতম, {name}** | Heading | 40 |
| `p01.home.cta_book` | Book a service | **সার্ভিস বুক করুন** | Button | 20 |
| `p01.home.active_title` | Your active services | **আপনার চলমান সার্ভিস** | Section title | 50 |
| `p01.home.track` | Track without signing in | **সাইন ইন ছাড়াই ট্র্যাক করুন** | Link | 40 |
| `p01.home.empty` | No services yet | **এখনও কোনো সার্ভিস নেই** | Empty state | 50 |
| `p01.home.empty_cta` | Book your first service | **আপনার প্রথম সার্ভিস বুক করুন** | Button | 30 |
| `p01.home.devices` | My devices | **আমার ডিভাইস** | Nav | 20 |
| `p01.home.offers` | For you | **আপনার জন্য** | Section title | 20 |

> **`p01.home.greeting` is corrected.** `UI-011` carries **নমস্কার**, which is a Hindu greeting
> and is not religiously neutral in Bangladesh. **স্বাগতম** is neutral, warm and correct for every
> customer. Recorded as `AUDIT-012` **BN-11**; this is a cultural-appropriateness defect, not a
> style preference, and it appears on the first screen 250,000 customers see each month.

### 4.2 Booking — `p01.booking.*` and `flow.booking.*`

Three steps maximum (`04-00` §P01).

| Key | English | **Bengali** | Slot | Budget |
|---|---|---|---|---:|
| `p01.booking.step_device.title` | What needs fixing? | **কী মেরামত করতে হবে?** | Step title | 50 |
| `p01.booking.step_device.help` | Choose your device, or add a new one | **আপনার ডিভাইস বেছে নিন, বা নতুন যোগ করুন** | Help | 120 |
| `p01.booking.step_device.add` | Add a device | **ডিভাইস যোগ করুন** | Button | 25 |
| `p01.booking.step_problem.title` | What is wrong? | **কী সমস্যা হচ্ছে?** | Step title | 50 |
| `p01.booking.step_problem.help` | Choose the closest match. You can add photos or a voice note. | **কাছাকাছি বিকল্পটি বেছে নিন। ছবি বা ভয়েস নোট যোগ করতে পারেন।** | Help | 120 |
| `p01.booking.step_problem.photo` | Add photos | **ছবি যোগ করুন** | Button | 25 |
| `p01.booking.step_problem.voice` | Record a voice note | **ভয়েস নোট রেকর্ড করুন** | Button | 30 |
| `p01.booking.step_how.title` | How would you like service? | **কীভাবে সার্ভিস নিতে চান?** | Step title | 50 |
| `p01.booking.mode.walkin` | Visit a service centre | **সার্ভিস সেন্টারে আসুন** | Option | 35 |
| `p01.booking.mode.onsite` | We come to you | **আমরা আপনার কাছে আসব** | Option | 35 |
| `p01.booking.mode.pickdrop` | We collect and return | **আমরা নিয়ে যাব এবং ফেরত দেব** | Option | 35 |
| `p01.booking.mode.remote` | Remote support | **রিমোট সাপোর্ট** | Option | 35 |
| `p01.booking.slot` | Choose a time | **সময় বেছে নিন** | Field label | 30 |
| `p01.booking.price_hint` | Estimated {min}–{max}. We confirm the price after checking your device. | **আনুমানিক {min}–{max}। আপনার ডিভাইস পরীক্ষার পর আমরা দাম নিশ্চিত করব।** | Help | 140 |
| `p01.booking.cta_confirm` | Confirm booking | **বুকিং নিশ্চিত করুন** | Button | 20 |
| `p01.booking.done.title` | Booking confirmed | **বুকিং নিশ্চিত হয়েছে** | Title | 50 |
| `p01.booking.done.ref` | Your reference is {ref}. We sent it to {mobile}. | **আপনার রেফারেন্স {ref}। আমরা এটি {mobile}-এ পাঠিয়েছি।** | Body | 140 |
| `p01.booking.done.next` | What happens next | **এরপর কী হবে** | Section title | 30 |
| `flow.booking.progress` | Step {n} of 3 | **ধাপ {n} / ৩** | Progress | 20 |
| `flow.booking.back` | Back | **পেছনে** | Button | 12 |
| `flow.booking.save_exit` | Save and finish later | **সংরক্ষণ করে পরে শেষ করুন** | Link | 35 |

> **`p01.booking.price_hint` changes মূল্য to দাম.** `BN-003` §6 binds *price* to **দাম** on
> customer surfaces and reserves **মূল্য** for the Class A/B formal register (`BN-002` `RD-C`).
> `UI-011`'s indicative Bengali used মূল্য. Recorded as `AUDIT-012` **BN-12**.

### 4.3 Tracking — `p01.track.*`

| Key | English | **Bengali** | Note |
|---|---|---|---|
| `p01.track.title` | Your service | **আপনার সার্ভিস** | |
| `p01.track.status` | {customer_status} | **{customer_status}** | From `MD-027` `customer_label_bn` (`SB-02`) |
| `p01.track.technician` | {name} is on the way. About {minutes} minutes. | **{name} আসছেন। প্রায় {minutes} মিনিট।** | Honorific verb for a third person (`BN-002` §3.2) |
| `p01.track.tech_photo` | Your technician | **আপনার টেকনিশিয়ান** | |
| `p01.track.delayed` | This is taking longer than we planned. {reason} We will update you by {time}. | **পরিকল্পনার চেয়ে বেশি সময় লাগছে। {reason} আমরা {time}-এর মধ্যে জানাব।** | `{reason}` resolves to a translated `MD-026` sentence (`BN-005` `KP-08`) |
| `p01.track.timeline` | Progress | **অগ্রগতি** | |
| `p01.track.share` | Share this link | **এই লিংক শেয়ার করুন** | |
| `p01.track.contact` | Contact us | **যোগাযোগ করুন** | |

### 4.4 Estimate approval — `p01.estimate.*` and `flow.estimate.*`

| Key | English | **Bengali** | Note |
|---|---|---|---|
| `p01.estimate.waiting` | We checked your device. Here is what it needs. | **আমরা আপনার ডিভাইস পরীক্ষা করেছি। এটির যা প্রয়োজন তা এখানে।** | |
| `p01.estimate.total` | Total {amount} | **সর্বমোট {amount}** | Currency prefix (`BN-007` `FM-07`) |
| `p01.estimate.parts` | Parts | **পার্টস** | |
| `p01.estimate.labour` | Labour | **লেবার চার্জ** | |
| `p01.estimate.vat` | VAT | **VAT** | Tier 1 (`BN-004` §3.1) |
| `p01.estimate.cta_approve` | Approve {amount} | **{amount} অনুমোদন করুন** | |
| `p01.estimate.cta_part` | Approve some items | **কিছু আইটেম অনুমোদন করুন** | |
| `p01.estimate.cta_reject` | **Reject** | **প্রত্যাখ্যান করুন** | **English corrected from "Decline"** — `BN-003` §11 D-3 |
| `p01.estimate.reject_note` | We will return your device unrepaired. A diagnosis charge of {amount} applies. | **আমরা আপনার ডিভাইস মেরামত ছাড়াই ফেরত দেব। {amount} পরীক্ষার চার্জ প্রযোজ্য।** | Consequence before the button (`BN-002` `TN-07`) |
| `flow.estimate.sign` | Sign to approve | **অনুমোদনের জন্য স্বাক্ষর করুন** | |
| `flow.estimate.signed` | Approved on {date} | **{date} তারিখে অনুমোদিত** | |
| `flow.estimate.revised` | The estimate has changed | **এস্টিমেট পরিবর্তিত হয়েছে** | |
| `flow.estimate.revised_why` | {reason} The new total is {amount}. | **{reason} নতুন সর্বমোট {amount}।** | |

### 4.5 Payments — `p01.pay.*` and `flow.payment.*`

| Key | English | **Bengali** | Note |
|---|---|---|---|
| `p01.pay.title` | Payment | **পেমেন্ট** | |
| `p01.pay.due` | {amount} due | **{amount} বকেয়া** | |
| `p01.pay.method` | How would you like to pay? | **কীভাবে পেমেন্ট করতে চান?** | |
| `p01.pay.bkash` | bKash | **bKash** | Tier 1 |
| `p01.pay.nagad` | Nagad | **Nagad** | Tier 1 |
| `p01.pay.card` | Card | **কার্ড** | |
| `p01.pay.bank` | Bank transfer | **ব্যাংক ট্রান্সফার** | |
| `p01.pay.cash` | Pay at the service centre | **সার্ভিস সেন্টারে পেমেন্ট করুন** | |
| `p01.pay.cta` | Pay {amount} | **{amount} পেমেন্ট করুন** | |
| `flow.payment.processing` | Confirming your payment | **আপনার পেমেন্ট নিশ্চিত করা হচ্ছে** | |
| `flow.payment.done` | Payment received | **পেমেন্ট গৃহীত হয়েছে** | |
| `flow.payment.receipt` | Receipt sent to {mobile} | **{mobile}-এ রসিদ পাঠানো হয়েছে** | Hyphen detaches the suffix (`BN-005` `KP-12`) |
| `flow.payment.failed` | The payment did not go through. No money has left your account. Try again or choose another method. | **পেমেন্ট সম্পন্ন হয়নি। আপনার অ্যাকাউন্ট থেকে কোনো টাকা কাটা হয়নি। আবার চেষ্টা করুন বা অন্য পদ্ধতি বেছে নিন।** | Reassurance first (`BN-002` `TN-02`) |
| `p01.pay.invoices` | Invoices and receipts | **ইনভয়েস ও রসিদ** | |
| `p01.pay.refund_status` | Refund status | **রিফান্ডের অবস্থা** | |

### 4.6 Devices — `p01.device.*`

| Key | English | **Bengali** |
|---|---|---|
| `p01.device.title` | My devices | **আমার ডিভাইস** |
| `p01.device.add` | Add a device | **ডিভাইস যোগ করুন** |
| `p01.device.serial` | Serial or IMEI | **সিরিয়াল বা IMEI** |
| `p01.device.scan` | Scan the label | **লেবেল স্ক্যান করুন** |
| `p01.device.photo` | Take a photo instead | **এর বদলে ছবি তুলুন** |
| `p01.device.history` | Service history | **সার্ভিস হিস্ট্রি** |
| `p01.device.warranty_active` | Under warranty until {date} | **{date} পর্যন্ত ওয়ারেন্টির আওতায়** |
| `p01.device.warranty_expired` | Warranty ended on {date} | **{date} তারিখে ওয়ারেন্টি শেষ হয়েছে** |
| `p01.device.transfer` | Transfer ownership | **মালিকানা হস্তান্তর করুন** |

### 4.7 Contracts, warranty and loyalty — `p01.contract.*`, `p01.warranty.*`, `p01.loyalty.*`

| Key | English | **Bengali** |
|---|---|---|
| `p01.contract.title` | My contracts | **আমার চুক্তি** |
| `p01.contract.amc` | AMC | **AMC** |
| `p01.contract.ramc_first` | Residential Annual Maintenance Contract (RAMC) | **আবাসিক বার্ষিক রক্ষণাবেক্ষণ চুক্তি (RAMC)** |
| `p01.contract.balance` | {n} visits remaining | **{n}টি ভিজিট বাকি** |
| `p01.contract.renew` | Renew | **নবায়ন করুন** |
| `p01.contract.expires` | Expires {date} | **{date} তারিখে মেয়াদ শেষ** |
| `p01.warranty.check` | Check warranty | **ওয়ারেন্টি দেখুন** |
| `p01.warranty.buy` | Buy a protection plan | **প্রোটেকশন প্ল্যান কিনুন** |
| `p01.warranty.claim` | Submit a claim | **ক্লেইম জমা দিন** |
| `p01.warranty.claim_status` | Claim {ref} is {status} | **ক্লেইম {ref} — {status}** |
| `p01.loyalty.title` | Privilege | **Privilege** |
| `p01.loyalty.points` | {n} points | **{n} পয়েন্ট** |
| `p01.loyalty.redeem` | Redeem points | **পয়েন্ট রিডিম করুন** |
| `p01.loyalty.referral` | Invite a friend | **বন্ধুকে আমন্ত্রণ জানান** |

### 4.8 Support and feedback — `p01.support.*`, `p01.feedback.*`

| Key | English | **Bengali** |
|---|---|---|
| `p01.support.title` | Help | **সহায়তা** |
| `p01.support.chat` | Chat with us | **চ্যাট করুন** |
| `p01.support.ai` | Ask the assistant | **অ্যাসিস্ট্যান্টকে জিজ্ঞাসা করুন** |
| `p01.support.call` | Call 16743 | **16743-এ কল করুন** |
| `p01.support.inbox` | Notifications | **নোটিফিকেশন** |
| `p01.support.faq` | Common questions | **সাধারণ প্রশ্ন** |
| `p01.feedback.rate` | How was your service? | **আপনার সার্ভিস কেমন ছিল?** |
| `p01.feedback.rate_tech` | Rate your technician | **আপনার টেকনিশিয়ানকে রেটিং দিন** |
| `p01.feedback.comment` | Tell us more | **আরও কিছু জানান** |
| `p01.feedback.complaint` | Raise a complaint | **অভিযোগ উত্থাপন করুন** |
| `p01.feedback.thanks` | Thank you. Your feedback reaches the team that served you. | **ধন্যবাদ। আপনার মতামত সেই টিমের কাছে পৌঁছাবে যারা আপনাকে সেবা দিয়েছে।** |

### 4.9 Account, registration and consent — `p01.account.*`, `flow.register.*`, `flow.consent.*`

| Key | English | **Bengali** | Note |
|---|---|---|---|
| `flow.register.title` | Create your account | **আপনার অ্যাকাউন্ট তৈরি করুন** | |
| `flow.register.mobile` | Mobile number | **মোবাইল নম্বর** | Arabic digits (`BN-007` `NM-D`) |
| `flow.register.otp_sent` | We sent a code to {mobile} | **আমরা {mobile}-এ একটি কোড পাঠিয়েছি** | |
| `flow.register.otp_enter` | Enter the code | **কোডটি দিন** | |
| `flow.register.otp_resend` | Send it again | **আবার পাঠান** | |
| `flow.register.otp_wait` | You can ask for a new code in {n} seconds | **{n} সেকেন্ড পরে নতুন কোড চাইতে পারবেন** | |
| `p01.account.language` | Language | **ভাষা** | The toggle (`BN-001` `LR-02`) |
| `p01.account.language_bn` | বাংলা | **বাংলা** | Always in its own language |
| `p01.account.language_en` | English | **English** | Always in its own language |
| `p01.account.addresses` | My addresses | **আমার ঠিকানা** | |
| `p01.account.notifications` | Notification preferences | **নোটিফিকেশন পছন্দ** | |
| `flow.consent.title` | Your data | **আপনার তথ্য** | |
| `flow.consent.purpose` | We use your details to deliver the service you asked for. | **আপনি যে সেবা চেয়েছেন তা দিতে আমরা আপনার তথ্য ব্যবহার করি।** | Class B; formal sub-register does **not** apply on a UI surface (`BN-002` `FR-02`) |
| `flow.consent.marketing` | Send me offers and news | **আমাকে অফার ও খবর পাঠান** | Unticked by default (`UI-042`) |
| `flow.consent.withdraw` | You can change this at any time. | **আপনি যেকোনো সময় এটি পরিবর্তন করতে পারেন।** | |
| `flow.consent.read_policy` | Read the privacy notice | **প্রাইভেসি নোটিশ পড়ুন** | `LG-008` |

> **`flow.consent.*` strings are Class B and carry legal weight.** They are authored here for
> completeness but require **G5 legal review of the Bengali** in addition to G4, because the
> Bengali is what the customer actually consents against (`CG-007` §2.1, `LG-008`).

---

## 5. Status strings

**Quoted from `MD-027` `customer_label_bn`. Not translated here** (`SB-02`).

| State | `customer_label_bn` | Never show |
|---|---|---|
| `submitted` | **বুকিং গৃহীত হয়েছে** | জমা দেওয়া হয়েছে |
| `awaiting_parts` | **পার্টসের অপেক্ষায়** | — |
| `sla_breached` | **বিলম্বিত** | **এসএলএ লঙ্ঘিত** |
| `cancelled` | **বাতিল** | — |

| # | Rule |
|---|---|
| **ST-P01** | A status string appearing in this bundle rather than resolving from `MD-027` is a defect (`CG-008` UI-i) |
| **ST-P02** | The same customer label must appear in the SMS (`BN-014`), on the tracking page and in the IVR readback (`BN-017`). Checked at `AUDIT_Checklist_Recurring` F2 in both languages |

---

## 6. Errors — `p01.error.*`

Surface-specific only. Shared validation is `common.error.*` (`BN-011` §6 interim).

| Key | English | **Bengali** | Class |
|---|---|---|:--:|
| `p01.error.zone_uncovered` | We do not offer on-site service in your area yet. You can use pick and drop, or visit {nearest_branch}. | **আপনার এলাকায় এখনও অন-সাইট সার্ভিস নেই। আপনি পিক অ্যান্ড ড্রপ ব্যবহার করতে পারেন, অথবা {nearest_branch}-এ আসতে পারেন।** | **H** |
| `p01.error.no_slots` | No slots on {date}. The earliest is {next_date}. | **{date} তারিখে কোনো সময় খালি নেই। সবচেয়ে কাছের সময় {next_date}।** | **H** |
| `p01.error.device_unknown` | We could not find that model. Choose the closest, or type it and we will confirm at the service centre. | **সেই মডেলটি পাওয়া যায়নি। কাছাকাছিটি বেছে নিন, অথবা লিখে দিন — আমরা সার্ভিস সেন্টারে নিশ্চিত করব।** | **S** |
| `p01.error.warranty_expired` | This device is out of warranty since {date}. This will be a paid repair. | **{date} থেকে এই ডিভাইসের ওয়ারেন্টি নেই। এটি একটি পেইড মেরামত হবে।** | **S** |
| `p01.error.otp_wrong` | That code is not right. Check the message and try again. | **কোডটি সঠিক নয়। বার্তাটি দেখে আবার চেষ্টা করুন।** | **H** |
| `p01.error.otp_expired` | That code has expired. Ask for a new one. | **কোডটির মেয়াদ শেষ। নতুন কোড চান।** | **H** |

| # | Rule |
|---|---|
| **ER-P01** | Every error states **what is wrong and what to do** (`PS-09`, `NFR-078`, `BN-002` `TN-04`) |
| **ER-P02** | **No error makes the customer the agent of the failure** (`BN-002` `TN-01`) |
| **ER-P03** | No error exposes an internal state name, a rule ID or a system detail (`CG-008` UI-d, `BN-003` `ST-03`) |

---

## 7. Plurals

**Every count string carries an explicit `=0` branch, because Bengali's `one` category includes
zero** (`BN-005` `PL-01`).

| Key | Bengali ICU |
|---|---|
| `p01.home.active_count` | `{n, plural, =0 {কোনো চলমান সার্ভিস নেই} one {{n}টি চলমান সার্ভিস} other {{n}টি চলমান সার্ভিস}}` |
| `p01.contract.visits_left` | `{n, plural, =0 {কোনো ভিজিট বাকি নেই} one {{n}টি ভিজিট বাকি} other {{n}টি ভিজিট বাকি}}` |
| `p01.loyalty.points_count` | `{n, plural, =0 {কোনো পয়েন্ট নেই} one {{n} পয়েন্ট} other {{n} পয়েন্ট}}` |
| `p01.device.count` | `{n, plural, =0 {কোনো ডিভাইস যোগ করা হয়নি} one {{n}টি ডিভাইস} other {{n}টি ডিভাইস}}` |
| `p01.estimate.item_count` | `{n, plural, =0 {কোনো আইটেম নেই} one {{n}টি আইটেম} other {{n}টি আইটেম}}` |

| # | Rule |
|---|---|
| **PL-P01** | `one` and `other` carrying identical Bengali text is **correct**, not a copy error — Bengali nouns do not inflect for number (`BN-005` `PL-03`) |
| **PL-P02** | The classifier is **টি for things, জন for people** (`BN-005` `PL-06`) |

---

## 8. Accessibility strings

| Item | Rule |
|---|---|
| Accessible names | From `UI-010`, translated in `BN-011` §6 as `common.a11y.*` (`BN-001` `LS-08`) |
| Page language | `lang="bn-BD"` (`BN-005` `BU-07`, `VB-009` `AC-01`) |
| Script changes | Every Tier 1 item marked `lang="en"` — `bKash`, `Privilege`, `IMEI`, `VAT`, `AMC`, `16743` (`BN-004` `DN-03`) |
| Errors | Announced assertively; associated with the field (`CG-011`) |
| Status changes | Announced politely via `common.a11y.live.status` |
| Bengali screen reader | Known engine limitations recorded, not silently accepted (`CG-011` §8.2, `VB-009` `AC-07`) |

---

## 9. Budget and truncation risk

Budgets are **Bengali rendered widths** (`VB-006` `DS-04`, `BN-006` `LB-11`).

| Slot | Budget | Risk | Strings at risk |
|---|---:|---|---|
| Primary button | 20 | **High** — verbs ending in করুন run long | `p01.booking.cta_confirm`, `p01.estimate.cta_approve` |
| Mode option | 35 | Medium | `p01.booking.mode.pickdrop` |
| Status chip | 18 | **High** | `MD-027` labels |
| Step title | 50 | Low | |
| Help text | 120–140 | Low | |
| Notification preview | 60 | **High** | `BN-014` |

| # | Rule |
|---|---|
| **BG-P01** | Exceeding a budget is a **design conversation**, not an abbreviation exercise (`VB-006` §8) |
| **BG-P02** | Two lines before icon-only; **never truncate a label** (`VB-007` `BL-04`) |
| **BG-P03** | Truncation, where unavoidable, is on a **grapheme cluster boundary** (`BN-006` `LB-07`) |

---

## 10. Coverage ledger

**Regenerated by enumerating the files after authoring, never written ahead of them**
(`CP-11`, `CM-R2`, `AUDIT_Checklist_Recurring` F7). Both columns are counted, on 2026-08-17.

| Namespace | Keys enumerated in the English pack | **Bengali strings authored here** |
|---|---:|---:|
| `p01.*` — `UI-011` | 27 | **104** |
| Customer `flow.*` — `UI-037`, `UI-038`, `UI-039`, `UI-040`, `UI-042` | 96 | **22** |
| **Total** | **123** | **126** |
| `common.*` — `UI-002`…`UI-010`, rendered by `P01` | **154** | **0 — by design** (`LS-08`) |

**Three things this table says, none of which a single "148" would have said.**

1. **`p01.*` authored (104) exceeds the English pack's enumerated keys (27).** The `UI` packs are
   **representative, not complete** — `UI-011` §3 covers home, booking, tracking and estimate and
   defers the rest. This bundle authored Bengali for devices, contracts, warranty, loyalty,
   support, feedback and account, which have **no English source row**. That inverts `BP-03`,
   where English is the source of truth for structure. Recorded as `AUDIT-012` **BN-18**;
   the remedy is to complete `UI-011`, not to trim this bundle.
2. **Customer `flow.*` authored (22) is well below the English pack's 96.** The flow packs carry
   far more copy than the customer-facing subset this bundle reached. **74 `flow.*` strings remain
   unauthored in Bengali.**
3. **`common.*` is zero here by design**, and `P01` renders **154** of them. Surface completeness
   is therefore **126 of ~280 ≈ 45%**, not 100%. `LS-04` measures surfaces, and this bundle does
   not meet it alone.

---

## 11. Sign-off status

| Gate | Required | Status |
|---|:--:|---|
| G1 Editorial | ● | Passed on the English (`UI-011`) |
| G2 Factual | ● | Passed on the English |
| G3 Technical | ● | **Not started — no build exists** |
| **G4 Linguistic, in context** | **●** | **Not started. Blocks `Approved` and cannot be waived (`CG-008` `B-09`)** |
| G5 Legal — `flow.consent.*` only | ● | **Not started** |
| Native-speaker review, independent of author | ● | **Not started** (`CO-05`) |

---

## 12. Open items

| # | Item | Owner | Blocks |
|---|---|---|---|
| 1 | **`BN-002` §2–§3 ratification** — register and address | Programme Content Lead | Every string here |
| 2 | **`BN-007` §3 numeral ratification** | Localisation Lead | Every amount, date and count |
| 3 | **`BN-019` registration**, or `BN-011` §6 completion | Programme Content Lead | Surface completeness (§10) |
| 4 | `UI-011` corrections `BN-11` (নমস্কার) and `BN-12` (মূল্য → দাম) applied at source | Content Design Lead | Bundle-to-pack parity |
| 5 | `p01.estimate.cta_reject` — the **English** must change from "Decline" to "Reject" (`CG-004` §4.8) | Content Design Lead with `M01` owner | `UI-011`, `UI-038` |
| 6 | Is *service order* presented to customers as **আমার সার্ভিস**? `CG-004` §10 item 2 is open on the English side | Content Design Lead | `p01.home.active_title` |
| 7 | G4 in-context review requires a **built surface** | Platform Engineering | G4, and therefore `Approved` |

---

## 13. Related documents

| Document | Relationship |
|---|---|
| [`../03_UI_Copy_and_Microcopy/03B_Portals/UI-011_P01_Customer_Portal_and_App_UI_Copy_Pack.md`](../03_UI_Copy_and_Microcopy/03B_Portals/UI-011_P01_Customer_Portal_and_App_UI_Copy_Pack.md) | The English source |
| [`BN-011_Bengali_String_Bundle_P03_Admin.md`](BN-011_Bengali_String_Bundle_P03_Admin.md) | Holds `common.*` under the interim route |
| [`BN-014_Bengali_Notification_and_SMS_Pack.md`](BN-014_Bengali_Notification_and_SMS_Pack.md) | The same status labels in SMS |
| [`BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md`](BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md) | The G4 this bundle awaits |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-027_Status_and_Lifecycle_State_Label_Register.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-027_Status_and_Lifecycle_State_Label_Register.md) | The status authority |

---

## 14. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-17 | Initial issue. **126 Bengali strings counted** across `p01.*` (104) and the customer-facing `flow.*` (22); **নমস্কার corrected to স্বাগতম** on religious-neutrality grounds; মূল্য corrected to দাম per `BN-003`; the "Decline" English defect on the estimate flow raised; explicit `=0` plural branches throughout; coverage ledger showing the `common.*` gap that prevents a surface-completeness claim | Localisation Lead with Content Design Lead (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:`, `traces_to:` and `i18n_namespace:`
- [x] Every string carries a key conforming to `UI-001` (`CG-008` UI-a)
- [x] No string concatenated across a translatable boundary (`BN-005` `KP-05`)
- [x] Every error states a remedy and none blames the customer (`BN-002` `TN-01`, `TN-04`)
- [x] Status labels quoted from `MD-027` `customer_label_bn`, not re-translated (`CG-008` UI-i)
- [x] **Every count string carries an explicit `=0` branch** (`BN-005` `PL-01`)
- [x] Terminology cited from `BN-003`; no term invented locally
- [x] Tier 1 items left in Latin and marked for `lang` (`BN-004`)
- [x] Character budgets recorded as **Bengali** rendered widths
- [x] Empty, error, offline and consent states covered, not only the happy path
- [x] **Coverage ledger regenerated by enumeration on 2026-08-17, with the `common.*` shortfall and the 45% surface figure stated rather than hidden**
- [ ] **74 customer `flow.*` strings unauthored** — outstanding; §10 item 2
- [ ] **`UI-011` completed so that the 77 strings authored beyond it have an English source** — outstanding; `AUDIT-012` **BN-18**
- [x] Corrections to the English pack raised and routed to its owner, not applied unilaterally
- [x] All internal links resolve
- [ ] **G4 in-context linguistic sign-off** — **outstanding; blocks `Approved`, unwaivable (`CG-008` `B-09`)**
- [ ] **Independent native-speaker review** — outstanding (`CO-05`)
- [ ] **G5 legal review of `flow.consent.*` Bengali** — outstanding
- [ ] `BN-002` and `BN-007` ratified — outstanding; §12 items 1 and 2
- [ ] Pinned to a release and verified against the build — outstanding; no build exists
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
