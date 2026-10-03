---
id: BN-013
title: Bengali String Bundle — P07 to P12
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
reviewers: [Content Design Lead, P07–P12 owners, Marketplace Ops, Logistics Director, Contact Centre Manager, Quality Manager, Accessibility reviewer]
approver: Localisation Lead with Content Design Lead
content_class: D
purpose: >
  The Bengali bundles for the marketplace seller, brand partner, rider, contact centre, field
  auditor and partner surfaces. These six differ more from each other than any other group in the
  register: riders and sellers are predominantly Bengali-first, brand partners are international
  and English-first, and contact-centre agents work in spoken Bengali all day. This bundle records
  which is which, so that the language decision for each surface is a decision on the record
  rather than an assumption inherited from the portal next to it.
traces_to: [P07, P08, P09, P10, P11, P12, UI-017, UI-018, UI-019, UI-020, UI-021, UI-022, BN-001 §3.1, BN-001 LS-03, BN-002, BN-003, BN-005, BN-007, BN-011 §6, BN-017, BN-018, PS-08]
priority: P2
wave: W7
bilingual: yes
bn_counterpart: self — this file is the Bengali counterpart of `UI-017` … `UI-022`
i18n_namespace: "`p07.*` … `p12.*`"
pinned_to:
  surface: P07, P08, P09, P10, P11, P12
  release: pending first build
  wave: W7 for P07 and P12; earlier for P09, P10 and P11 — see §8
sources:
  - source: project_content/03_UI_Copy_and_Microcopy/03B_Portals/UI-017 … UI-022 — the English source packs
    verified: 2026-08-17
    class: P1
  - source: project_content/11_Localisation_Bengali/BN-001 §3.1 — per-surface defaults; LS-03 the P09 Bengali-only decision with the English toggle deferred to W8
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §3 PS-08 — offline-capable with queued sync for P02, P09, P11
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# BN-013 — Bengali String Bundle — P07 to P12

> **Six surfaces, four different language positions.** Grouping them in one register row does not
> make them one audience:
>
> | | Default | Why |
> |---|---|---|
> | `P07` seller, `P09` rider, `P10` agent, `P11` auditor | **Bengali** | Predominantly Bengali-first populations working at speed |
> | `P08` brand partner | **English** | 17+ international manufacturers |
> | `P12` partner | English | Alliance and referral partners contract in English |
>
> **`P09` ships Bengali-only at W3** (`BN-001` `LS-03`) — a declared decision with an identified
> deferral, not an omission.

---

## 1. Bundle summary

| Surface | Audience | Default | Toggle | Bengali required | Offline | Strings authored — **counted** |
|---|---|---|:--:|---|:--:|---:|
| `P07` Marketplace seller | 500–2,000 sellers | **Bengali** | Yes | **100%** | No | **27** |
| `P08` Brand partner | 17+ brands, international | **English** | Yes | Labels only | No | **18** |
| `P09` Logistics & rider | 50–200 riders | **Bengali** | **No — W8** | **100%** | **Yes** | **23** |
| `P10` Contact centre | Agents | **Bengali** | Yes | **100%** | No | **21** |
| `P11` Field auditor | Auditors | **Bengali** | Yes | **100%** | **Yes** | **14** |
| `P12` Partner & referral | Alliance partners | English | Yes | **100%** | No | **12** |
| | | | | | **Total** | **115** |

`common.*` is not repeated here (`BN-001` `LS-08`); it is carried in `BN-011` §6.

---

## 2. Terminology in force

| Concept | Bengali | Note |
|---|---|---|
| seller | **বিক্রেতা (seller)** | Tier 4, `BN-003` §3 |
| engineer | **ইঞ্জিনিয়ার** | **Reserved** — external marketplace freelancer only |
| rider | **রাইডার** | **Never ডেলিভারি বয়** (`BN-003` §3) |
| consignment | **কনসাইনমেন্ট** | Deliberately not চালান (`BN-003` §4) |
| custody | **হেফাজত** | |
| commission | **কমিশন** | |
| payout | **পে-আউট** | |
| brand partner | **ব্র্যান্ড পার্টনার** | |
| claim | **ক্লেইম** | |
| non-conformance | **অসঙ্গতি (NCR)** | |
| finding | **অডিট ফাইন্ডিং** | |
| partner | **পার্টনার** | **Reserved** — alliance/referral only |
| decline | **ফিরিয়ে দিন** | Sellers and riders decline offered work |

---

## 3. `P07` — Marketplace seller portal

**Bengali default.** Sellers are predominantly small independent shops and freelance engineers.

| Key | English | **Bengali** |
|---|---|---|
| `p07.nav.jobs` | Available jobs | **উপলব্ধ জব** |
| `p07.nav.mine` | My jobs | **আমার জব** |
| `p07.nav.earnings` | Earnings | **আয়** |
| `p07.nav.profile` | My shop | **আমার দোকান** |
| `p07.nav.docs` | My documents | **আমার ডকুমেন্ট** |
| `p07.nav.scorecard` | My rating | **আমার রেটিং** |
| `p07.job.accept` | Accept | **গ্রহণ করুন** |
| `p07.job.decline` | Decline | **ফিরিয়ে দিন** |
| `p07.job.decline_reason` | Why are you declining? | **কেন ফিরিয়ে দিচ্ছেন?** |
| `p07.job.commission` | You receive {net} after {rate} commission | **{rate} কমিশনের পর আপনি {net} পাবেন** |
| `p07.job.deadline` | Complete by {datetime} | **{datetime}-এর মধ্যে সম্পন্ন করুন** |
| `p07.job.evidence` | Add before and after photos | **আগের ও পরের ছবি যোগ করুন** |
| `p07.earn.pending` | Pending payout | **অপেক্ষমাণ পে-আউট** |
| `p07.earn.held` | {amount} held until {date} | **{date} পর্যন্ত {amount} আটকে রাখা হয়েছে** |
| `p07.earn.paid` | Paid on {date} to {method} | **{date} তারিখে {method}-এ পরিশোধিত** |
| `p07.earn.statement` | Payout statement | **পে-আউট স্টেটমেন্ট** |
| `p07.score.rating` | {score} out of 5 | **৫-এর মধ্যে {score}** |
| `p07.score.acceptance` | Acceptance rate | **গ্রহণের হার** |
| `p07.score.ontime` | On-time rate | **সময়মতো সম্পন্নের হার** |
| `p07.score.warning` | Your rating is below {threshold}. Fewer jobs will be offered until it improves. | **আপনার রেটিং {threshold}-এর নিচে। উন্নতি না হওয়া পর্যন্ত কম জব দেওয়া হবে।** |
| `p07.score.suspended` | Your account is suspended. {reason} Contact seller support. | **আপনার অ্যাকাউন্ট স্থগিত। {reason} সেলার সাপোর্টে যোগাযোগ করুন।** |
| `p07.docs.required` | {document} is required before you can take {category} jobs. | **{category} জব নিতে হলে {document} প্রয়োজন।** |
| `p07.docs.nid` | NID | **NID** |
| `p07.docs.trade_licence` | Trade Licence | **Trade Licence** |
| `p07.onboard.step` | Step {n} of {total} | **ধাপ {n} / {total}** |
| `p07.onboard.agreement` | Read and accept the seller agreement | **সেলার চুক্তি পড়ুন এবং গ্রহণ করুন** |

| # | Rule |
|---|---|
| **SL-01** | `p07.score.warning` and `p07.score.suspended` implement `P07` governance — automatic visibility reduction and suspension on performance failure. **They are enforceable only if the seller agreement says so** (`LG-004`), and the Bengali must state the consequence plainly, not soften it (`BN-002` `TN-08`) |
| **SL-02** | The seller agreement (`LG-004`) is **Class B and English-governing** (`CG-010` §4.1). `p07.onboard.agreement` links to a Bengali translation with a precedence clause; the Bengali is not an independent instrument |
| **SL-03** | Payout amounts use Arabic digits and the `৳` prefix (`BN-007` `FM-07`) |

---

## 4. `P08` — Brand partner portal

**English default.** Bengali labels exist for Bangladeshi brand staff; correspondence is English.

| Key | English | **Bengali** |
|---|---|---|
| `p08.nav.claims` | Claims | **ক্লেইম** |
| `p08.nav.rate_cards` | Rate cards | **রেট কার্ড** |
| `p08.nav.quality` | Quality reports | **কোয়ালিটি রিপোর্ট** |
| `p08.nav.technicians` | Authorised technicians | **অনুমোদিত টেকনিশিয়ান** |
| `p08.nav.parts` | Parts consumption | **পার্টস ব্যবহার** |
| `p08.claim.submitted` | {n} claims submitted this period | **এই সময়কালে {n}টি ক্লেইম জমা দেওয়া হয়েছে** |
| `p08.claim.approve` | Approve claim {ref} | **ক্লেইম {ref} অনুমোদন করুন** |
| `p08.claim.reject` | Reject with a reason | **কারণসহ প্রত্যাখ্যান করুন** |
| `p08.claim.evidence` | Evidence pack | **প্রমাণের প্যাক** |
| `p08.claim.reimbursed` | Reimbursed {amount} on {date} | **{date} তারিখে {amount} পরিশোধিত** |
| `p08.tech.certified` | {n} technicians certified for {product_line} | **{product_line}-এর জন্য {n} জন টেকনিশিয়ান সার্টিফাইড** |
| `p08.tech.expiring` | {n} certifications expire within 60 days | **{n}টি সার্টিফিকেশনের মেয়াদ ৬০ দিনের মধ্যে শেষ** |
| `p08.quality.ftf` | First-time fix for {brand} | **{brand}-এর জন্য প্রথমবারেই সমাধান** |
| `p08.quality.rework` | Rework rate | **রিওয়ার্ক হার** |
| `p08.quality.top_faults` | Most frequent faults | **সবচেয়ে ঘন ঘন ত্রুটি** |
| `p08.data.scope` | You see data for {brand} only. | **আপনি শুধু {brand}-এর ডেটা দেখতে পাচ্ছেন।** |

| # | Rule |
|---|---|
| **BP-B01** | `p08.data.scope` is a **data-protection boundary made visible** (`LG-005`, `05-04`). It must be present in both languages and must not be dismissible |
| **BP-B02** | Brand names, model names and part numbers stay Latin (`BN-004` §4.3, `BR-01`) |
| **BP-B03** | **Claim correspondence and evidence packs remain English** (`CG-010` §3.2, `NT-013`). Declared, not omitted |
| **BP-B04** | **`p08.tech.certified` counts people — জন, not টি** (`BN-005` `PL-06`) |

---

## 5. `P09` — Logistics and rider application

**Bengali only at W3.** Offline-capable (`PS-08`). Read in motion, on a phone, outdoors — the
**shortest budget in the system at ≤ 10 words**.

| Key | English | **Bengali** | Words |
|---|---|---|---:|
| `p09.day.route` | Today's route | **আজকের রুট** | 2 |
| `p09.day.stops` | {n} stops | **{n}টি স্টপ** | 2 |
| `p09.day.start` | Start route | **রুট শুরু করুন** | 3 |
| `p09.stop.navigate` | Navigate | **পথ দেখান** | 2 |
| `p09.stop.arrived` | I have arrived | **আমি পৌঁছেছি** | 2 |
| `p09.stop.collect` | Collect the device | **ডিভাইস সংগ্রহ করুন** | 3 |
| `p09.stop.deliver` | Deliver the device | **ডিভাইস পৌঁছে দিন** | 3 |
| `p09.stop.scan` | Scan to confirm | **নিশ্চিত করতে স্ক্যান করুন** | 4 |
| `p09.stop.photo` | Photo of the handover | **হস্তান্তরের ছবি** | 2 |
| `p09.stop.sign` | Ask for a signature | **স্বাক্ষর নিন** | 2 |
| `p09.stop.absent` | Nobody there | **কেউ নেই** | 2 |
| `p09.stop.refused` | Customer refused | **গ্রাহক নেননি** | 2 |
| `p09.stop.reschedule` | Reschedule | **পুনর্নির্ধারণ করুন** | 2 |
| `p09.cod.collect` | Collect {amount} | **{amount} সংগ্রহ করুন** | 3 |
| `p09.cod.collected` | {amount} collected | **{amount} সংগ্রহ করা হয়েছে** | 4 |
| `p09.cod.deposit` | Deposit cash at {branch} | **{branch}-এ ক্যাশ জমা দিন** | 4 |
| `p09.custody.holding` | You hold {n} devices | **আপনার কাছে {n}টি ডিভাইস আছে** | 5 |
| `p09.custody.handover` | Hand over to {name} | **{name}-কে হস্তান্তর করুন** | 3 |
| `p09.safety.helmet` | Wear your helmet. | **হেলমেট পরুন।** | 2 |
| `p09.safety.panic` | Send safety alert | **নিরাপত্তা সতর্কতা পাঠান** | 3 |
| `p09.error.wrong_device` | This is not the device for this stop. | **এই স্টপের জন্য এটি সঠিক ডিভাইস নয়।** | 6 |
| `p09.error.cod_mismatch` | The amount does not match. Call dispatch before you leave. | **পরিমাণ মিলছে না। যাওয়ার আগে ডিসপ্যাচকে কল করুন।** | 7 |

| # | Rule |
|---|---|
| **RD-01** | **≤ 10 words.** The rider reads at a stop, often standing, often in rain. Any string over budget is a design defect (`VB-002`) |
| **RD-02** | **রাইডার, never ডেলিভারি বয়** (`BN-003` §3) |
| **RD-03** | Cash strings are **unambiguous and unsoftened** — `p09.error.cod_mismatch` names the action before the rider leaves the customer (`BN-002` `TN-08`) |
| **RD-04** | Offline, sync and conflict strings are `common.*` (`BN-011` §6.9) and are **bundled at build** with the font (`BN-005` `BU-04`, `BU-05`) |
| **RD-05** | **No English toggle at W3** (`BN-001` `LS-03`). Deferred to W8, recorded as `BN-001` §12 item 7 |

---

## 6. `P10` — Contact centre console

**Bengali default.** The agent works in spoken Bengali all day and types in Bengali between calls.
The **spoken** scripts are `SP-034` and `BN-017`; this bundle is the **console**.

| Key | English | **Bengali** |
|---|---|---|
| `p10.nav.queue` | My queue | **আমার সারি** |
| `p10.nav.search` | Find a customer | **গ্রাহক খুঁজুন** |
| `p10.nav.knowledge` | Knowledge | **নলেজ** |
| `p10.nav.scripts` | Call guides | **কল গাইড** |
| `p10.call.incoming` | Incoming call from {mobile} | **{mobile} থেকে ইনকামিং কল** |
| `p10.call.identify` | Verify the caller | **কলারের পরিচয় যাচাই করুন** |
| `p10.call.history` | Their last {n} contacts | **তাঁদের শেষ {n}টি যোগাযোগ** |
| `p10.call.wrap` | Wrap up | **র‍্যাপ আপ** |
| `p10.call.disposition` | What was this call about? | **এই কলটি কী বিষয়ে ছিল?** |
| `p10.call.notes` | Call notes | **কলের নোট** |
| `p10.call.transfer` | Transfer to {team} | **{team}-এ ট্রান্সফার করুন** |
| `p10.call.escalate` | Escalate to a supervisor | **সুপারভাইজারের কাছে এসকেলেট করুন** |
| `p10.call.callback` | Schedule a callback | **কলব্যাক নির্ধারণ করুন** |
| `p10.case.create` | Create a service order | **সার্ভিস অর্ডার তৈরি করুন** |
| `p10.case.complaint` | Raise a complaint | **অভিযোগ উত্থাপন করুন** |
| `p10.case.status` | Tell the customer: {customer_status} | **গ্রাহককে বলুন: {customer_status}** |
| `p10.consent.recording` | Confirm the recording notice was played | **রেকর্ডিং নোটিশ শোনানো হয়েছে তা নিশ্চিত করুন** |
| `p10.consent.data` | Confirm identity before discussing account details | **অ্যাকাউন্টের তথ্য আলোচনার আগে পরিচয় নিশ্চিত করুন** |
| `p10.metric.aht` | Average handling time | **গড় হ্যান্ডলিং সময়** |
| `p10.metric.fcr` | First contact resolution | **প্রথম যোগাযোগেই সমাধান** |

| # | Rule |
|---|---|
| **CC-01** | `p10.case.status` **quotes the `MD-027` customer label**, so that the agent says on the phone exactly what the customer sees on the portal and in the SMS (`BN-003` `ST-01`) |
| **CC-02** | `p10.consent.recording` and `p10.consent.data` are **legal controls surfaced as UI** (`LG-008`, `NT-019` `IV-04`). They are not dismissible |
| **CC-03** | **The agent types Bengali notes.** `IN-02` phonetic input, `EN-02` NFC normalisation and `EN-07` collation all apply to this surface more than to any other (`BN-006`) |
| **CC-04** | `p10.call.wrap` uses **র‍্যাপ আপ**, which contains the ra-ya-phala sequence flagged at `BN-006` §3.1. **It is on the encoding watch list** and must be verified on the console's rendering engine, or replaced with **কল শেষ করুন** if `BN-006` §10 item 1 resolves against it |

---

## 7. `P11` auditor and `P12` partner

### 7.1 `P11` — Field auditor application

Bengali default, offline-capable (`PS-08`).

| Key | English | **Bengali** |
|---|---|---|
| `p11.nav.audits` | My audits | **আমার অডিট** |
| `p11.audit.checklist` | Checklist | **চেকলিস্ট** |
| `p11.audit.branch` | Auditing {branch} | **{branch} অডিট করা হচ্ছে** |
| `p11.audit.evidence` | Add evidence | **প্রমাণ যোগ করুন** |
| `p11.audit.finding` | Raise a finding | **অডিট ফাইন্ডিং উত্থাপন করুন** |
| `p11.audit.severity` | Severity | **তীব্রতা** |
| `p11.audit.ncr` | Raise an NCR | **NCR উত্থাপন করুন** |
| `p11.audit.capa` | CAPA required by {date} | **{date}-এর মধ্যে CAPA প্রয়োজন** |
| `p11.audit.conform` | Conforms | **সঙ্গতিপূর্ণ** |
| `p11.audit.nonconform` | Does not conform | **অসঙ্গতিপূর্ণ** |
| `p11.audit.na` | Not applicable | **প্রযোজ্য নয়** |
| `p11.audit.submit` | Submit the audit | **অডিট জমা দিন** |
| `p11.audit.offline` | This audit is saved on your device | **এই অডিট আপনার ডিভাইসে সংরক্ষিত** |

| # | Rule |
|---|---|
| **AU-01** | `NCR` and `CAPA` are **Tier 1** ISO 9001 terms and are never translated (`BN-004` §3.3, `BN-003` §8) |
| **AU-02** | `p11.audit.na` — **"প্রযোজ্য নয়", never "N/A"** in a Bengali interface (`BN-005` §8, `BN-012` `AN-02`) |
| **AU-03** | Audit findings feed `DT-043` and ISO surveillance. **Bengali wording changes require Quality Manager sign-off** in addition to G4 |

### 7.2 `P12` — Partner and referral portal

English default; full Bengali UI.

| Key | English | **Bengali** |
|---|---|---|
| `p12.nav.referrals` | My referrals | **আমার রেফারেল** |
| `p12.nav.commission` | Commission | **কমিশন** |
| `p12.nav.materials` | Marketing materials | **মার্কেটিং উপকরণ** |
| `p12.refer.new` | Refer a customer | **গ্রাহক রেফার করুন** |
| `p12.refer.link` | Your referral link | **আপনার রেফারেল লিংক** |
| `p12.refer.status` | Referral {ref} is {status} | **রেফারেল {ref} — {status}** |
| `p12.refer.attributed` | Attributed to you on {date} | **{date} তারিখে আপনার নামে গণ্য** |
| `p12.refer.not_attributed` | Not attributed: {reason} | **আপনার নামে গণ্য হয়নি: {reason}** |
| `p12.commission.earned` | {amount} earned | **{amount} অর্জিত** |
| `p12.commission.statement` | Commission statement | **কমিশন স্টেটমেন্ট** |
| `p12.commission.terms` | Commission is paid {days} days after the customer pays. | **গ্রাহক পেমেন্ট করার {days} দিন পর কমিশন পরিশোধ করা হয়।** |

| # | Rule |
|---|---|
| **PT-01** | `p12.refer.not_attributed` **always states the reason**. Attribution disputes are the normal failure mode of referral programmes (`LG-007`) and an unexplained refusal creates one |
| **PT-02** | The partner agreement (`LG-007`) is **English-governing**; its Bengali carries a precedence clause (`CG-010` §4.1) |

---

## 8. Wave alignment

**Three of the six surfaces need their Bengali before this file's registered wave of W7.**

| Surface | Portal wave | Bengali needed | `BN-013` registered |
|---|:--:|:--:|:--:|
| `P09` Rider | **W3** | **W3** | W7 ✘ |
| `P10` Contact centre | **W4** | **W4** | W7 ✘ |
| `P11` Field auditor | **W4** | **W4** | W7 ✘ |
| `P07` Seller | W7 | W7 | W7 ✔ |
| `P08` Brand partner | W4 | W4 | W7 ✘ |
| `P12` Partner | W7 | W7 | W7 ✔ |

> **Four of six sections are needed before the file's own wave**, and `P09`'s is needed four waves
> early — while also being **Bengali-only**, so there is no English fallback to ship in the
> meantime (`LS-03`). The register groups these six by portal number, not by wave, and the
> grouping conceals the sequencing.
>
> Recorded as `AUDIT-012` **BN-05**, with the remediation: **`BN-013` is delivered and signed off
> in sections, per surface, at each surface's own wave.** The file's registered wave marks its
> completion, not its start.

---

## 9. Plurals

| Key | Bengali ICU |
|---|---|
| `p07.count.jobs` | `{n, plural, =0 {এখন কোনো জব নেই} one {{n}টি জব} other {{n}টি জব}}` |
| `p08.count.claims` | `{n, plural, =0 {কোনো ক্লেইম নেই} one {{n}টি ক্লেইম} other {{n}টি ক্লেইম}}` |
| `p08.count.technicians` | `{n, plural, =0 {কোনো টেকনিশিয়ান নেই} one {{n} জন টেকনিশিয়ান} other {{n} জন টেকনিশিয়ান}}` — **জন** |
| `p09.count.stops` | `{n, plural, =0 {আজ কোনো স্টপ নেই} one {{n}টি স্টপ} other {{n}টি স্টপ}}` |
| `p10.count.queue` | `{n, plural, =0 {সারি খালি} one {{n}টি কল অপেক্ষমাণ} other {{n}টি কল অপেক্ষমাণ}}` |
| `p11.count.findings` | `{n, plural, =0 {কোনো ফাইন্ডিং নেই} one {{n}টি ফাইন্ডিং} other {{n}টি ফাইন্ডিং}}` |
| `p12.count.referrals` | `{n, plural, =0 {কোনো রেফারেল নেই} one {{n}টি রেফারেল} other {{n}টি রেফারেল}}` |

---

## 10. Coverage ledger

**Counted by enumeration on 2026-08-17** (`CP-11`, `CM-R2`, F7).

| Namespace | Keys enumerated in the English pack | **Bengali strings authored here** |
|---|---:|---:|
| `p07.*` — `UI-017` | 16 | **27** |
| `p08.*` — `UI-018` | 21 | **18** |
| `p09.*` — `UI-019` | 22 | **23** |
| `p10.*` — `UI-020` | 20 | **21** |
| `p11.*` — `UI-021` | 15 | **14** |
| `p12.*` — `UI-022` | 15 | **12** |
| **Total** | **109** | **115** |
| `common.*` — rendered by all six | **154** | 0 — by design (`LS-08`) |

> **`p08.*`, `p11.*` and `p12.*` are authored *below* their English source** — 18 of 21, 14 of 15
> and 12 of 15 respectively. Those bundles are **incomplete**, not merely representative, and
> cannot pass `LQ-28`. **`p07.*`, `p09.*` and `p10.*` are authored above their source**, which is
> the `BP-03` inversion recorded as `AUDIT-012` **BN-18**.
>
> **The earlier issue of this table claimed 242 authored against 242 source, neither counted** —
> the F7 failure, recorded as `AUDIT-012` **BN-19**.

---

## 11. Sign-off status

| Surface | G4 in context | Business-owner review | Additional |
|---|---|---|---|
| `P07` | Not started | Marketplace Ops — not started | Legal on `SL-01` consequences |
| `P08` | Not started | Commercial — not started | — |
| `P09` | **Not started — needed W3** | Logistics — not started | **Serving-rider review, on a phone, at a stop** |
| `P10` | **Not started — needed W4** | Contact Centre Manager — not started | `CC-04` encoding verification |
| `P11` | **Not started — needed W4** | Quality Manager — not started | `AU-03` Quality sign-off |
| `P12` | Not started | Commercial — not started | — |

---

## 12. Open items

| # | Item | Owner | Blocks |
|---|---|---|---|
| 1 | **Section-by-section delivery at each surface's own wave** (§8) | Programme Content Lead | `P09` at W3; `P08`, `P10`, `P11` at W4 |
| 2 | **`P09` English toggle deferral** — confirm with Logistics (`BN-001` §12 item 7) | `P09` owner | `BN-013` `P09` scope |
| 3 | `p10.call.wrap` — **র‍্যাপ আপ is on the `BN-006` §3.1 encoding watch list** (`CC-04`) | Platform Engineering | `p10.*` |
| 4 | `BN-002` and `BN-007` ratification | Programme Content Lead | Every string |
| 5 | `LG-004` seller agreement and `LG-007` partner agreement are **not yet written** — `SL-02` and `PT-02` reference documents that do not exist | Legal | `p07.onboard.agreement`, `p12.*` |
| 6 | Serving-rider and serving-agent reviews require access to real users at their place of work | Logistics and Contact Centre | G4 credibility |

---

## 13. Related documents

| Document | Relationship |
|---|---|
| [`BN-011_Bengali_String_Bundle_P03_Admin.md`](BN-011_Bengali_String_Bundle_P03_Admin.md) | Carries the `common.*` all six surfaces render |
| [`BN-017_Bengali_Voice_IVR_and_Speech_Prompt_Pack.md`](BN-017_Bengali_Voice_IVR_and_Speech_Prompt_Pack.md) | The spoken counterpart of `P10` |
| [`BN-010_Bengali_String_Bundle_P02_Technician.md`](BN-010_Bengali_String_Bundle_P02_Technician.md) | The offline pattern `P09` and `P11` share |
| [`BN-006_Bengali_Typography_Font_and_Numeral_Standard.md`](BN-006_Bengali_Typography_Font_and_Numeral_Standard.md) | §3.1 ra-ya-phala, `CC-04` |
| [`BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md`](BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md) | The G4 these bundles await |

---

## 14. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-17 | Initial issue. **115 Bengali strings counted** across six surfaces with four distinct language positions stated separately; rider vocabulary protected against ডেলিভারি বয়; seller performance consequences stated plainly and tied to `LG-004` enforceability; ISO terms held as Tier 1 on `P11`; "N/A" prohibited in a Bengali interface; **the four-of-six wave misalignment recorded with section-by-section delivery as the remediation**; `র‍্যাপ আপ` flagged against the `BN-006` encoding watch list | Localisation Lead with Content Design Lead (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:`, `traces_to:` and `i18n_namespace:`
- [ ] **Every key in `UI-017`…`UI-022` has a Bengali string** — **NOT met.** `p08.*`, `p11.*` and `p12.*` are authored below their English source (§10). Outstanding
- [x] **Four distinct language positions stated per surface rather than one position for the group**
- [x] Reserved-verb and reserved-noun discipline applied (`ফিরিয়ে দিন`, `রাইডার`, `ইঞ্জিনিয়ার`, `কনসাইনমেন্ট`)
- [x] Tier 1 items left in Latin (`NID`, `Trade Licence`, `NCR`, `CAPA`, `NPS`)
- [x] Consequence-bearing strings stated plainly and traced to the instrument that makes them enforceable
- [x] `জন` used for people, `টি` for things, with explicit `=0` branches
- [x] **Wave misalignment recorded with a stated remediation, not absorbed**
- [x] A string containing a known encoding risk flagged against `BN-006` §3.1 rather than shipped quietly
- [x] All internal links resolve
- [ ] **G4 in-context sign-off per surface** — outstanding; blocks `Approved`
- [ ] **`P09` Bengali at W3, `P08`/`P10`/`P11` at W4** — outstanding; §12 item 1
- [ ] **Serving-rider and serving-agent reviews** — outstanding
- [ ] `LG-004` and `LG-007` written, so their Bengali precedence clauses exist — outstanding
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
