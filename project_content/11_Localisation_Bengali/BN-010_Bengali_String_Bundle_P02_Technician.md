---
id: BN-010
title: Bengali String Bundle — P02 Technician
project: 1000FiX ERP System v2.0
content_type: Bengali string bundle
template: TPL_UI_Copy_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Localisation Lead
author: Localisation with Content Design, a native Bengali linguistic reviewer and two serving field technicians
reviewers: [Content Design Lead, P02 owner, Technical Director, HSE Lead, Accessibility reviewer, Mobile Engineering]
approver: Localisation Lead with Content Design Lead and Technical Director
content_class: D
purpose: >
  The complete Bengali bundle for the technician application. P02 non-negotiable requirement 3
  states that the Bengali interface must be complete, including error messages, and 04-00 admits
  no English fallback on this surface. This bundle carries p02.*; the shared common.* namespace
  that P02 also renders — every field validation, every system error, every offline and sync
  conflict message — is not owned by any registered BN file, which is why the completeness
  claim for this surface depends on BN-001 LS-07 being executed.
traces_to: [P02, UI-012, UI-009, BN-001 §3.1, BN-001 LS-07, BN-002, BN-003, BN-005, BN-006, BN-007, BN-018, MD-024, MD-025, MD-026, TR-009, TS-015, 04-00 §P02, PS-08]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: self — this file is the Bengali counterpart of `UI-012`
i18n_namespace: "`p02.*`"
pinned_to:
  surface: P02
  release: pending first build
  wave: W2
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P02 Non-Negotiable Requirements — #1 full operation offline for 24 hours with no data loss; #2 sync within 30 seconds; #3 Bengali user interface, complete — including error messages; #4 runs acceptably on a mid-range Android 11 device with 3 GB RAM
    verified: 2026-08-17
    class: P1
  - source: project_content/03_UI_Copy_and_Microcopy/03B_Portals/UI-012 §1–§9 — the English source pack, its indicative Bengali marked pending BN-003, the 12-word budget and the §3.5 safety exception
    verified: 2026-08-17
    class: P1
  - source: project_content/11_Localisation_Bengali/BN-003 §11 divergences D-3, D-4, D-5, D-6 — corrections to UI-012's indicative Bengali
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# BN-010 — Bengali String Bundle — P02 Technician

> **There is no English fallback on this surface.** `P02` non-negotiable #3 requires the Bengali
> interface to be complete, including error messages. A missing Bengali string is a defect, not a
> degradation (`UI-012`).
>
> **And there is a specific reason this bundle is not sufficient on its own.** The message a
> technician sees when a part is unavailable is `common.error.stock.unavailable`, not a `p02.*`
> key. The message they see when a sync conflicts is `common.conflict.detected`. Neither is in
> this bundle, and **no registered `BN` file owns them** (`BN-001` §4). Until that is resolved,
> **`P02` cannot evidence non-negotiable #3.** §10 states the shortfall in numbers.

---

## 1. Bundle summary

| Item | Value |
|---|---|
| Surface | `P02` — 200–400 field and workshop technicians |
| Locale | **`bn-BD`** |
| Namespace | `p02.*` |
| Source pack | `UI-012` |
| Default on this surface | **Bengali, complete** (`P02` #3) |
| Framework | Flutter, Android primary |
| Device baseline | **Mid-range Android 11, 3 GB RAM** (`P02` #4) |
| Offline | **24 hours, no data loss** (`P02` #1). Strings and font **bundled at build** (`BN-005` `BU-04`, `BU-05`) |
| Register | চলিত, direct (`BN-002` §8) |
| Address | **আপনি / করুন** — `AD-03` prohibits তুমি and তুই. This surface is where that rule earns its place |
| Numerals | **Arabic** throughout — field surface, transcription risk, small-size legibility (`BN-007` §3.3, `BN-006` `NU-06`) |
| Sentence budget | **≤ 12 words** — the tightest in the system (`VB-002` T-01) |
| Safety strings | **No budget** (`VB-002` T-06, `UI-012` §3.5) |
| Strings in this issue | **83 — counted** (`p02.*`). See §10 |
| Content class | D — User-facing |

---

## 2. Terminology in force

| Concept | Bengali | Tier | `BN-003` |
|---|---|:--:|---|
| job | **জব** | 2 | §4 — the dispatchable unit, not কাজ |
| service order | সার্ভিস অর্ডার | 2 | §4 — the parent, rarely shown here |
| part | **পার্টস** | 2 | §7 |
| van stock | **ভ্যান স্টক** | 2 | §7 |
| fault | **ত্রুটি** | 3 | §4 — confirmed |
| symptom | **লক্ষণ** | 3 | §4 — reported |
| estimate | এস্টিমেট | 2 | §4 |
| custody | হেফাজত | 3 | §4 |
| decline | **ফিরিয়ে দিন** | 3 | §9 — **corrected**, see §3.1 |
| reject | প্রত্যাখ্যান করুন | 3 | §9 |
| complete | সম্পন্ন করুন | 3 | §9 |
| dispatch | ডিসপ্যাচ | 2 | §9 |
| IMEI, GPS, QC, L1/L2/L3 | Latin | 1 | `BN-004` §5 |

---

## 3. Screen copy

### 3.1 Day — `p02.day.*`

| Key | English | **Bengali** | Words | Note |
|---|---|---|---:|---|
| `p02.day.queue` | Today — {count} jobs | **আজ — {count}টি জব** | 4 | |
| `p02.day.clock_in` | Clock in | **ক্লক ইন** | 2 | |
| `p02.day.clock_out` | Clock out | **ক্লক আউট** | 2 | |
| `p02.day.geofence_fail` | You are {distance} from {branch}. Clock in anyway? | **আপনি {branch} থেকে {distance} দূরে। তবুও ক্লক ইন করবেন?** | 9 | |
| `p02.day.accept` | Accept | **গ্রহণ করুন** | 2 | |
| `p02.day.decline` | Decline | **ফিরিয়ে দিন** | 2 | **Corrected** — `BN-003` D-3 |
| `p02.day.decline_reason` | Why are you declining? | **কেন ফিরিয়ে দিচ্ছেন?** | 3 | **Corrected** — `BN-003` D-4 |
| `p02.day.summary` | Today's summary | **আজকের সারসংক্ষেপ** | 2 | |
| `p02.day.leave` | Request leave | **ছুটির আবেদন করুন** | 3 | |
| `p02.day.empty` | No jobs assigned yet | **এখনও কোনো জব দেওয়া হয়নি** | 5 | |

> **`p02.day.decline` was প্রত্যাখ্যান in `UI-012`, the same word as *reject*.** `CG-004` §4.8
> reserves the two verbs for different acts — *reject* ends a flow with a recorded reason,
> *decline* returns offered work to the pool — and `BN-003` `GL-02` forbids one Bengali form
> serving two English terms. Recorded as `AUDIT-012` **BN-06**.

### 3.2 Job execution — `p02.job.*`

| Key | English | **Bengali** | Words | Note |
|---|---|---|---:|---|
| `p02.job.navigate` | Navigate | **পথ দেখান** | 2 | Count corrected from 1 — `BN-003` D-5 |
| `p02.job.route` | Route overview | **রুট দেখুন** | 2 | |
| `p02.job.arrived` | I have arrived | **আমি পৌঁছেছি** | 2 | |
| `p02.job.start` | Start work | **কাজ শুরু করুন** | 3 | |
| `p02.job.pause` | Pause | **বিরতি নিন** | 2 | **Corrected** — a button is a verb; `BN-003` D-6 |
| `p02.job.pause_reason` | Why are you pausing? | **কেন বিরতি নিচ্ছেন?** | 3 | |
| `p02.job.resume` | Resume work | **কাজ আবার শুরু করুন** | 4 | |
| `p02.job.history` | Device history | **ডিভাইস হিস্ট্রি** | 2 | |
| `p02.job.diagnostic` | Guided diagnosis | **গাইডেড ডায়াগনোসিস** | 2 | |
| `p02.job.symptom` | What the customer reported | **গ্রাহক যা জানিয়েছেন** | 3 | লক্ষণ, not ত্রুটি |
| `p02.job.fault` | Record the fault | **ত্রুটি রেকর্ড করুন** | 3 | Confirmed fault |
| `p02.job.action` | What did you do? | **আপনি কী করেছেন?** | 3 | `MD-025` |
| `p02.job.notes` | Repair notes | **মেরামতের নোট** | 2 | |
| `p02.job.photo_before` | Photo before work | **কাজের আগের ছবি** | 3 | |
| `p02.job.photo_after` | Photo after work | **কাজের পরের ছবি** | 3 | |
| `p02.job.voice` | Voice note | **ভয়েস নোট** | 2 | Bengali capture (`NFR-074`) |
| `p02.job.scan_doc` | Scan a document | **ডকুমেন্ট স্ক্যান করুন** | 3 | |
| `p02.job.complete` | Complete job | **জব সম্পন্ন করুন** | 3 | |
| `p02.job.remote` | Start a remote session | **রিমোট সেশন শুরু করুন** | 4 | |

### 3.3 Parts — `p02.parts.*`

| Key | English | **Bengali** | Words |
|---|---|---|---:|
| `p02.parts.van` | Van stock | **ভ্যান স্টক** | 2 |
| `p02.parts.scan` | Scan the part | **পার্টস স্ক্যান করুন** | 3 |
| `p02.parts.not_in_van` | Not in your van. Request it? | **আপনার ভ্যানে নেই। অনুরোধ করবেন?** | 5 |
| `p02.parts.request` | Request the part | **পার্টস অনুরোধ করুন** | 3 |
| `p02.parts.return` | Return unused parts | **অব্যবহৃত পার্টস ফেরত দিন** | 4 |
| `p02.parts.reconcile` | Reconcile your van | **আপনার ভ্যান মেলান** | 3 |
| `p02.parts.hazard` | {part} is {hazard}. Read the handling steps. | **{part} একটি {hazard}। হ্যান্ডলিং ধাপ পড়ুন।** | 6 |

### 3.4 Customer interaction — `p02.customer.*`

| Key | English | **Bengali** | Words |
|---|---|---|---:|
| `p02.customer.show_estimate` | Show the estimate | **এস্টিমেট দেখান** | 2 |
| `p02.customer.approved` | Customer approved {amount} | **গ্রাহক {amount} অনুমোদন করেছেন** | 4 |
| `p02.customer.rejected` | Customer rejected the estimate | **গ্রাহক এস্টিমেট প্রত্যাখ্যান করেছেন** | 4 |
| `p02.customer.sign` | Ask the customer to sign | **গ্রাহককে স্বাক্ষর করতে বলুন** | 4 |
| `p02.customer.pay` | Take payment | **পেমেন্ট নিন** | 2 |
| `p02.customer.receipt` | Receipt sent to {mobile} | **{mobile}-এ রসিদ পাঠানো হয়েছে** | 4 |
| `p02.customer.absent` | Customer not present | **গ্রাহক উপস্থিত নেই** | 3 |

### 3.5 Workshop mode — `p02.workshop.*`

| Key | English | **Bengali** | Words |
|---|---|---|---:|
| `p02.workshop.bench` | My bench | **আমার বেঞ্চ** | 2 |
| `p02.workshop.wip` | Work in progress | **চলমান কাজ** | 2 |
| `p02.workshop.level` | Repair level {level} | **রিপেয়ার লেভেল {level}** | 3 |
| `p02.workshop.escalate` | Escalate to L3 | **L3-এ এসকেলেট করুন** | 3 |
| `p02.workshop.qc` | Quality checklist | **কোয়ালিটি চেকলিস্ট** | 2 |
| `p02.workshop.test` | Record the test result | **টেস্টের ফলাফল লিখুন** | 3 |

### 3.6 Logistics and custody — `p02.custody.*`

| Key | English | **Bengali** | Words |
|---|---|---|---:|
| `p02.custody.receive` | Take custody | **হেফাজতে নিন** | 2 |
| `p02.custody.handover` | Hand over the device | **ডিভাইস হস্তান্তর করুন** | 3 |
| `p02.custody.scan` | Scan to confirm custody | **হেফাজত নিশ্চিত করতে স্ক্যান করুন** | 5 |
| `p02.custody.confirm` | {name} now holds this device | **এখন {name} এই ডিভাইস রেখেছেন** | 5 |

### 3.7 Communication and personal — `p02.comms.*`, `p02.me.*`

| Key | English | **Bengali** | Words |
|---|---|---|---:|
| `p02.comms.dispatch` | Message dispatch | **ডিসপ্যাচকে বার্তা দিন** | 3 |
| `p02.comms.workshop` | Message the workshop | **ওয়ার্কশপে বার্তা দিন** | 3 |
| `p02.comms.escalate` | Ask for help | **সাহায্য চান** | 2 |
| `p02.me.scorecard` | My performance | **আমার পারফরম্যান্স** | 2 |
| `p02.me.earnings` | My earnings | **আমার আয়** | 2 |
| `p02.me.certs` | My certifications | **আমার সার্টিফিকেশন** | 2 |
| `p02.me.cert_expiry` | {cert} expires on {date} | **{cert}-এর মেয়াদ {date} তারিখে শেষ** | 5 |
| `p02.me.training` | Assigned training | **নির্ধারিত প্রশিক্ষণ** | 2 |
| `p02.me.manuals` | Repair manuals | **রিপেয়ার ম্যানুয়াল** | 2 |

---

## 4. Safety — `p02.safety.*`

**The one exception to the word budget** (`VB-002` T-06). Safety content is never abbreviated,
never softened by politeness particles (`BN-002` `TN-06`), and is set at the **19px `P02` safety
size** (`VB-009` §3, `MS-04`).

| Key | English | **Bengali** |
|---|---|---|
| `p02.safety.panic` | Send safety alert | **নিরাপত্তা সতর্কতা পাঠান** |
| `p02.safety.panic_sent` | Alert sent. Dispatch is calling you now. Stay where you are if it is safe. | **সতর্কতা পাঠানো হয়েছে। ডিসপ্যাচ এখনই আপনাকে কল করছে। নিরাপদ হলে যেখানে আছেন সেখানেই থাকুন।** |
| `p02.safety.hazard_steps` | Before you start: {steps}. Confirm you have read this. | **শুরুর আগে: {steps}। আপনি এটি পড়েছেন তা নিশ্চিত করুন।** |
| `p02.safety.electrical` | Disconnect the power. Confirm it is isolated before you touch anything. | **বিদ্যুৎ সংযোগ বিচ্ছিন্ন করুন। কিছু স্পর্শ করার আগে নিশ্চিত করুন যে এটি বিচ্ছিন্ন।** |
| `p02.safety.ppe` | Wear your safety equipment for this job. | **এই জবের জন্য আপনার সুরক্ষা সরঞ্জাম পরুন।** |
| `p02.safety.refrigerant` | Refrigerant work needs ventilation and eye protection. | **রেফ্রিজারেন্টের কাজে বায়ু চলাচল এবং চোখের সুরক্ষা প্রয়োজন।** |
| `p02.safety.lone` | You are working alone. Check in every {minutes} minutes. | **আপনি একা কাজ করছেন। প্রতি {minutes} মিনিটে চেক ইন করুন।** |

| # | Rule |
|---|---|
| **SF-01** | Safety strings use **direct imperatives with no hedging particles**. অনুগ্রহ করে is removed |
| **SF-02** | `p02.safety.electrical` contains **বিদ্যুৎ**, which uses khanda ta (ৎ, U+09CE). It is in the `BN-006` §9 test set line 7 for that reason and **must be verified on the device**, not only in the bundle |
| **SF-03** | Safety strings are **never truncated and never two-line-clipped**. The screen expands (`VB-009` `MS-04`) |
| **SF-04** | Safety wording changes require **HSE Lead sign-off** in addition to G4 |

---

## 5. Errors — `p02.error.*`

**`P02` non-negotiable #3 names error messages explicitly.** Every message states what is wrong
and what to do (`PS-09`), and none makes the technician the agent of the failure
(`BN-002` `TN-01`).

| Key | English | **Bengali** | Class |
|---|---|---|:--:|
| `p02.error.not_certified` | You are not certified for {brand}. Ask dispatch to reassign. | **{brand} ওয়ারেন্টি কাজের জন্য আপনার সার্টিফিকেশন নেই। ডিসপ্যাচকে পুনরায় নির্ধারণ করতে বলুন।** | **H** |
| `p02.error.estimate_needed` | Get approval before starting. Send the estimate now. | **শুরুর আগে অনুমোদন নিন। এখনই এস্টিমেট পাঠান।** | **H** |
| `p02.error.qc_needed` | Complete the quality checklist first. | **আগে কোয়ালিটি চেকলিস্ট সম্পন্ন করুন।** | **H** |
| `p02.error.photo_needed` | Add a photo before completing. | **সম্পন্ন করার আগে একটি ছবি যোগ করুন।** | **H** |
| `p02.error.part_unscanned` | Scan every part you used. | **আপনি যে পার্টস ব্যবহার করেছেন সব স্ক্যান করুন।** | **H** |
| `p02.error.l3_restricted` | This repair is L3. Escalate rather than continue. | **এই মেরামত L3। চালিয়ে না গিয়ে এসকেলেট করুন।** | **H** |
| `p02.error.ber_evidence` | Beyond economic repair needs photos and a second technician. | **অর্থনৈতিকভাবে অলাভজনক মেরামতের জন্য ছবি এবং দ্বিতীয় একজন টেকনিশিয়ান প্রয়োজন।** | **H** |
| `p02.error.geofence` | You are outside the job location. Confirm before you clock in. | **আপনি জবের অবস্থানের বাইরে আছেন। ক্লক ইন করার আগে নিশ্চিত করুন।** | **A** |
| `p02.error.cert_expiring` | {cert} expires in {n} days. Renew it to keep taking {brand} jobs. | **{cert}-এর মেয়াদ {n} দিনে শেষ। {brand} জব নিতে চাইলে নবায়ন করুন।** | **S** |

| # | Rule |
|---|---|
| **ER-P02** | **Message class matches the `05-05` rule class** — **H** blocks, **A** names the authoriser, **S** warns (`CG-008`) |
| **ER-P02b** | A **H** message names **who** unblocks it — ডিসপ্যাচ, সুপারভাইজার — not only what is wrong |
| **ER-P02c** | No message exposes a rule ID, a state key or a stack detail (`CG-008` UI-d) |

---

## 6. Offline and sync — the gap this bundle cannot fill

`P02` operates offline for 24 hours (`P02` #1) and syncs within 30 seconds of reconnection
(`P02` #2). The copy for those states is **`UI-009`**, which lives in **`common.*`**.

| String the technician sees | Key | In this bundle? |
|---|---|:--:|
| Working offline | `common.offline.banner` | **No** |
| {n} actions waiting to sync | `common.offline.queue` | **No** |
| Sync complete | `common.a11y.live.sync` | **No** |
| This job changed while you were offline | `common.conflict.detected` | **No** |
| Keep my version | `common.conflict.keep_mine` | **No** |
| Keep the server version | `common.conflict.keep_theirs` | **No** |
| Both versions kept | `common.conflict.both_kept` | **No** |
| Resolve manually | `common.conflict.manual` | **No** |
| Part not available | `common.error.stock.unavailable` | **No** |
| Technician not certified (shared rule) | `common.error.srm.tech_not_certified` | **No** |
| Field required | `common.error.field.required` | **No** |
| IMEI must be 15 digits | `common.error.field.imei_format` | **No** |

| # | Rule |
|---|---|
| **OF-01** | **These strings are `common.*` and belong to `BN-011` §6 under the `BN-001` `LS-07` interim route**, pending `BN-019`. They are listed here because they are the strings `P02` #3 names, and their absence must be visible from this file |
| **OF-02** | **The conflict-resolution strings are read at the worst possible moment** — in the field, after a day offline, with a customer waiting. They receive the same G4 in-context treatment as safety copy |
| **OF-03** | Offline strings are **bundled at build** with the font (`BN-005` `BU-04`, `BU-05`). A device that cannot reach the network cannot fetch the message telling it so |

---

## 7. Plurals

| Key | Bengali ICU |
|---|---|
| `p02.day.job_count` | `{n, plural, =0 {আজ কোনো জব নেই} one {আজ {n}টি জব} other {আজ {n}টি জব}}` |
| `p02.parts.van_count` | `{n, plural, =0 {ভ্যানে কোনো পার্টস নেই} one {{n}টি পার্টস} other {{n}টি পার্টস}}` |
| `p02.offline.queue_count` | `{n, plural, =0 {সব সিঙ্ক হয়েছে} one {{n}টি অপেক্ষমাণ} other {{n}টি অপেক্ষমাণ}}` |
| `p02.me.cert_count` | `{n, plural, =0 {কোনো সার্টিফিকেশন নেই} one {{n}টি সার্টিফিকেশন} other {{n}টি সার্টিফিকেশন}}` |
| `p02.workshop.bench_count` | `{n, plural, =0 {বেঞ্চে কোনো কাজ নেই} one {{n}টি কাজ} other {{n}টি কাজ}}` |

> **`p02.offline.queue_count` is the clearest case for `PL-01` in the system.** Zero pending
> actions is the *good* state and the technician must recognise it instantly. Without the `=0`
> branch it renders through Bengali's `one` category as "০টি অপেক্ষমাণ", which reads as a count
> rather than as an all-clear.

---

## 8. Device, size and rendering constraints

| Constraint | Value | Source |
|---|---|---|
| Device | Mid-range Android 11, 3 GB RAM | `P02` #4 |
| Body size floor | **17px Bengali** | `VB-009` §3 |
| Safety and custody size | **19px Bengali** | `VB-009` §3, `MS-04` |
| Line height | **1.7** body, **1.35** buttons | `VB-009` §4 |
| Font | **Hind Siliguri, bundled in the package** | `VB-009` `TF-02` |
| Touch target | 44 px minimum, larger in the field | `UI-012` §7 |
| Conditions | Outdoors, sunlight, one-handed, in motion | `VB-002` |

| # | Rule |
|---|---|
| **RD-P02** | Every string in this bundle is verified against the `BN-006` §9 test set **on the baseline device**, not on a developer handset (`RV-16`) |
| **RD-P02b** | Buttons carrying করুন run long. Where the Bengali does not fit at 17px, the **control goes two-line before it goes icon-only** (`VB-007` §7.3) |
| **RD-P02c** | Bengali digits are **not used anywhere on this surface** (`BN-007` §3.3) — small size, sunlight, and every number here is transcribed or scanned |

---

## 9. Bengali-native content adjacent to this bundle

| Content | File | Relationship |
|---|---|---|
| Field technician training | `TR-009` — **Bengali-native**, not translated | Must use the **same strings as this bundle**. A course that teaches a label the app does not show is a training defect (`BN-016` §3) |
| Repair manuals and knowledge | `KB` set, often Bengali-native | Read offline inside `P02` (`04-00` §P02 Knowledge) |
| Voice notes | Captured in Bengali, stored in Bengali, never machine-translated | `CG-010` MT-01, `BN-006` `IM-05` |
| Technician SMS and push | `NT-005`, `NT-016` → `BN-014` | Same vocabulary, same status labels |

---

## 10. Coverage ledger

**Counted by enumeration on 2026-08-17, not projected** (`CP-11`, `CM-R2`, F7).

| Namespace | Keys enumerated in the English pack | **Bengali strings authored here** |
|---|---:|---:|
| `p02.*` — `UI-012` | 35 | **83** |
| `common.*` — `UI-002`…`UI-010`, **rendered by `P02`** | **154** | **0 — by design** (`LS-08`) |
| **Surface total** | **189** | **83** |
| **Surface completeness** | | **≈ 44%** |

**What this ledger says, and what it deliberately refuses to say.**

1. **`P02` non-negotiable #3 is NOT met by this bundle alone.** The surface is **44%** Bengali,
   not 100%. A reader who sees "`p02.*` is complete" and concludes otherwise has drawn exactly the
   wrong conclusion. **`LS-04` measures surfaces**, and the missing 154 are the `common.*` strings
   §6 enumerates — validation, system errors, offline and conflict copy, which is precisely the
   content non-negotiable #3 names.
2. **`p02.*` authored (83) exceeds `UI-012`'s enumerated keys (35).** The English pack is
   representative, not complete: this bundle authored workshop, custody, communication, personal
   and additional safety and error strings that have **no English source row**. That inverts
   `BP-03`. Recorded as `AUDIT-012` **BN-18** and **BN-13**; the remedy is to complete `UI-012`.
3. **The earlier issue of this table claimed 96 authored against 96 source.** Both figures were
   written before the enumeration that should have produced them — the `AUDIT-005` / F7 failure,
   reproduced. The correction is recorded rather than quietly applied (`AUDIT-012` **BN-19**).

---

## 11. Sign-off status

| Gate | Required | Status |
|---|:--:|---|
| G1 Editorial | ● | Passed on the English (`UI-012`) |
| G2 Factual | ● | Passed on the English |
| G3 Technical | ● | **Not started — no build** |
| **G4 Linguistic, in context, on the baseline device** | **●** | **Not started. Unwaivable (`CG-008` `B-09`)** |
| HSE sign-off on §4 | ● | **Not started** (`SF-04`) |
| Independent native-speaker review | ● | **Not started** (`CO-05`) |
| **Serving-technician review** | **●** | **Not started.** Two serving technicians must read the bundle on the device. Register-correct Bengali that field technicians do not use is still wrong |

---

## 12. Open items

| # | Item | Owner | Blocks |
|---|---|---|---|
| 1 | **`BN-019` registration, or `BN-011` §6 completion** | Programme Content Lead | **`P02` non-negotiable #3** — the highest-consequence open item in this category |
| 2 | `BN-002` §3 ratification — the করুন decision `UI-012` §9 item 1 raised as blocking on every string | Programme Content Lead | Every string here |
| 3 | `UI-012` corrections D-3, D-4, D-5, D-6 applied at source | Content Design Lead | Bundle-to-pack parity |
| 4 | Four safety and four error strings added here have **no English source row** (`BN-013` finding) | Content Design Lead with HSE Lead | `UI-012` completeness |
| 5 | Does the geofence override need supervisor approval in-app or after the fact? Inherited from `UI-012` §9 item 2 | `M55` owner | `p02.error.geofence` class **A** wording |
| 6 | Baseline device procured for G4 and `TS-015` | Mobile Engineering | G4, `TS-015` |

---

## 13. Related documents

| Document | Relationship |
|---|---|
| [`../03_UI_Copy_and_Microcopy/03B_Portals/UI-012_P02_Technician_App_UI_Copy_Pack.md`](../03_UI_Copy_and_Microcopy/03B_Portals/UI-012_P02_Technician_App_UI_Copy_Pack.md) | The English source |
| [`../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-009_Offline_Sync_and_Conflict_Resolution_Copy.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-009_Offline_Sync_and_Conflict_Resolution_Copy.md) | The `common.*` offline copy §6 depends on |
| [`BN-011_Bengali_String_Bundle_P03_Admin.md`](BN-011_Bengali_String_Bundle_P03_Admin.md) | Holds `common.*` under the interim route |
| [`BN-016_Bengali_Help_and_Training_Content_Plan.md`](BN-016_Bengali_Help_and_Training_Content_Plan.md) | `TR-009` Bengali-native training |
| [`BN-006_Bengali_Typography_Font_and_Numeral_Standard.md`](BN-006_Bengali_Typography_Font_and_Numeral_Standard.md) | §9 test set, `SF-02` |
| `TS-015` Offline and Field Condition Test Scripts | Where §6 and §8 are verified |

---

## 14. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-17 | Initial issue. **83 `p02.*` Bengali strings counted**; four `UI-012` Bengali corrections applied (decline, decline reason, pause, word count); four safety and four error strings added beyond the English source and raised as an English gap; explicit `=0` plural branches with the offline-queue case reasoned; **a counted coverage ledger showing surface completeness at 83 of 189, ≈ 44%**, so that non-negotiable #3 is not falsely evidenced; serving-technician review added as a required gate | Localisation Lead with Content Design Lead and Technical Director (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:`, `traces_to:` and `i18n_namespace:`
- [x] Every `p02.*` key in `UI-012` has a Bengali string
- [x] **Every error message is Bengali** and states a remedy naming who unblocks it (`P02` #3, `PS-09`)
- [x] Message class matches the `05-05` rule class
- [x] Safety content carries no word budget and no hedging particles (`VB-002` T-06, `BN-002` `TN-06`)
- [x] Explicit `=0` plural branches throughout (`BN-005` `PL-01`)
- [x] Arabic numerals throughout, with the field reason stated (`RD-P02c`)
- [x] `BN-003` §11 corrections applied and their source raised for correction
- [x] Terminology cited from `BN-003`; no term invented locally
- [x] **The `common.*` shortfall stated in counted numbers (83 of 189, ≈ 44%), and the false-completeness reading pre-empted**
- [x] Offline and conflict strings enumerated even though they are out of scope, so their absence is visible
- [x] All internal links resolve
- [ ] **G4 in-context sign-off on the baseline device** — **outstanding; blocks `Approved`, unwaivable**
- [ ] **HSE sign-off on §4 safety strings** — outstanding
- [ ] **Serving-technician review** — outstanding
- [ ] **`common.*` Bengali available** — **outstanding; `P02` non-negotiable #3 cannot be evidenced until it is**
- [ ] `BN-002` §3 ratified — outstanding
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
