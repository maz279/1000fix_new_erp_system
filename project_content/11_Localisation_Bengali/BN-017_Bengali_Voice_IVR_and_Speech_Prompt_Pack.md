---
id: BN-017
title: Bengali Voice, IVR and Speech Prompt Pack
project: 1000FiX ERP System v2.0
content_type: Notification template library
template: TPL_Notification_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Localisation Lead
author: Localisation with Contact Centre and a native Bengali voice director
reviewers: [Contact Centre Manager, Content Design Lead, Legal & Compliance, Platform Engineering, Accessibility reviewer, M27 owner]
approver: Localisation Lead with Contact Centre Manager
content_class: D
purpose: >
  The Bengali spoken content for hotline 16743, the IVR tree, agent-facing spoken guidance and
  the voice-note handling on P02. Spoken Bengali has a different rhythm from written translated
  Bengali, so this content is authored natively rather than translated, and the recording
  direction is part of the content rather than a production note. A prompt is heard once, without
  the ability to scan back, and a caller who mishears a reference number calls again — which is
  the outcome the self-service target exists to avoid.
traces_to: [NT-019, SP-034, P02, P10, M27, BN-001 §6, BN-002 §8, BN-003, BN-007, BN-016, BN-018, CG-010 §4.2, MD-027, MD-041, LG-008]
priority: P2
wave: W4
bilingual: yes
bn_counterpart: self — this pack is the Bengali voice artefact; its English is the translation (`BN-001` `NA-01`)
channels: [Voice (IVR), Voice (agent), Voice note]
consent_class: Transactional — inbound; recording notice required
pinned_to:
  surface: Hotline 16743, P10 console, P02 voice notes
  release: pending first build
  wave: W4
sources:
  - source: project_content/04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-019 §2.1 the IVR tree, §2.2 thirteen prompts with Bengali, §2.3 recording direction, §2.4 rules IV-01…IV-06
    verified: 2026-08-17
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-010 §4.2 — contact centre and IVR scripts are authored in Bengali first; spoken Bengali has a different rhythm and a translated script sounds wrong on a call
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P02 Evidence — voice notes in Bengali; §P01 Support — AI assistant in Bengali and English, call the hotline in-app
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-074 — Bengali input including phonetic typing and voice-to-text on mobile
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# BN-017 — Bengali Voice, IVR and Speech Prompt Pack

> **`NT-019` names its Bengali counterpart as `BN-014`. That is wrong: it is this file.**
> Recorded as `AUDIT-012` **BN-04**, with the correction routed to `NT-019`'s owner.
>
> **Spoken content is not written content read aloud.** A prompt is heard once. There is no
> scanning back, no re-reading, and no visual hierarchy. Bengali sentence structure puts the verb
> last, which means a caller hears the whole clause before learning what to do — so the **option
> comes after the description** (`IV-01`) and the sentences are short.
>
> This pack is **authored in Bengali; the English is the translation** (`CG-010` §4.2,
> `BN-001` `NA-01`).

---

## 1. Set summary

| Item | Value |
|---|---|
| Channels | Voice — IVR, agent-spoken, voice note |
| Audience | Every caller to **16743**; `P10` agents; `P02` technicians recording voice notes |
| Owning module | `M27`, `P10` |
| Consent class | Transactional — inbound. **Recording notice required before any data is taken** (`LG-008`, `IV-04`) |
| Language | **Bengali primary**, English on option 2 |
| Authoring route | **Native Bengali** (`CG-010` §4.2) |
| Register | চলিত, spoken (`BN-002` §8) |
| Address | আপনি, honorific throughout (`BN-002` `AD-01`) |
| Numerals | **Spoken, not displayed** — digits read individually (`VP-07`) |
| Prompt budget | **≤ 12 spoken words per prompt**; ≤ 4 options plus zero per level (`IV-02`) |
| Prompts in this issue | **33 — counted** (§9) |
| Content class | D — User-facing |

---

## 2. The tree

```
16743
├─ ভাষা / Language: ১ বাংলা · 2 English
├─ ১  সার্ভিস ট্র্যাক করুন       → রেফারেন্স বা মোবাইল → অবস্থা শোনানো
├─ ২  সার্ভিস বুক করুন           → এজেন্টে ট্রান্সফার
├─ ৩  পেমেন্ট ও ইনভয়েস          → ১ বকেয়া · ২ কীভাবে পেমেন্ট · ৩ এজেন্ট
├─ ৪  সমস্যা জানান               → অভিযোগ → এজেন্ট (অগ্রাধিকার সারি)
└─ ০  কারো সাথে কথা বলুন
```

Four options plus zero at the top level (`IV-02`). `SP-034` carries the agent scripts that follow.

---

## 3. IVR prompts

### 3.1 Entry and menu

| # | Key | **Bengali (spoken)** | English |
|---|---|---|---|
| 1 | `ivr.greeting` | **1000FiX-এ স্বাগতম।** | Welcome to 1000FiX. |
| 2 | `ivr.language` | **বাংলার জন্য ১ চাপুন। For English press 2.** | For Bengali press 1. For English press 2. |
| 3 | `ivr.menu` | **সার্ভিস ট্র্যাক করতে ১ চাপুন। বুক করতে ২। পেমেন্টের জন্য ৩। সমস্যা জানাতে ৪। কারো সাথে কথা বলতে ০।** | To track a service, press 1. To book, press 2. For payments, press 3. To report a problem, press 4. To speak to someone, press 0. |
| 4 | `ivr.menu_repeat` | **আবার শুনতে ৯ চাপুন।** | To hear that again, press 9. |
| 5 | `ivr.invalid` | **সেই বিকল্পটি নেই। আবার চেষ্টা করুন।** | That is not an option. Please try again. |
| 6 | `ivr.no_input` | **কিছু শোনা যায়নি। আবার চেষ্টা করুন।** | We did not hear anything. Please try again. |

> **`ivr.language` is deliberately bilingual within one prompt.** The caller who needs English
> must hear the English instruction. This is the **only** prompt in the pack that mixes languages,
> and the English half is spoken in English, not in Bengali-accented reading (`VP-05`).

### 3.2 Tracking

| # | Key | **Bengali** | English |
|---|---|---|---|
| 7 | `ivr.ref_prompt` | **আপনার রেফারেন্স নম্বর দিন, অথবা মোবাইল নম্বর ব্যবহার করতে হ্যাশ চাপুন।** | Enter your reference number, or press hash to use your mobile number. |
| 8 | `ivr.ref_confirm` | **আপনি দিয়েছেন {ref}। ঠিক হলে ১ চাপুন।** | You entered {ref}. If that is correct, press 1. |
| 9 | `ivr.status` | **আপনার {device}, রেফারেন্স {ref}, {customer_status}।** | Your {device}, reference {ref}, is {customer_status}. |
| 10 | `ivr.status_eta` | **আমরা {date} তারিখে প্রস্তুত হওয়ার আশা করছি।** | We expect it to be ready on {date}. |
| 11 | `ivr.status_ready` | **এটি {branch} থেকে সংগ্রহ করা যাবে, {hours}।** | It can be collected from {branch}, {hours}. |
| 12 | `ivr.not_found` | **সেই রেফারেন্স পাওয়া যায়নি। কারো সাথে কথা বলতে ০ চাপুন।** | We could not find that reference. Press 0 to speak to someone. |
| 13 | `ivr.multiple` | **আপনার {n}টি চলমান সার্ভিস আছে। কারো সাথে কথা বলতে ০ চাপুন।** | You have {n} active services. Press 0 to speak to someone. |

| # | Rule |
|---|---|
| **VP-01** | **`ivr.status` speaks the `MD-027` `customer_label_bn` value** — the same words the customer sees on the portal and receives by SMS (`BN-003` `ST-01`, `BN-014` `CS-B03`). A caller told one thing and shown another calls again |

### 3.3 Payment

| # | Key | **Bengali** | English |
|---|---|---|---|
| 14 | `ivr.pay.menu` | **বকেয়া জানতে ১ চাপুন। কীভাবে পেমেন্ট করবেন জানতে ২। এজেন্টের জন্য ৩।** | For your balance, press 1. For how to pay, press 2. For an agent, press 3. |
| 15 | `ivr.pay.balance` | **আপনার বকেয়া {amount}। ইনভয়েস {inv}।** | Your balance is {amount}. Invoice {inv}. |
| 16 | `ivr.pay.none` | **আপনার কোনো বকেয়া নেই।** | You have nothing outstanding. |
| 17 | `ivr.pay.how` | **আপনি bKash, Nagad, কার্ড বা ব্যাংক ট্রান্সফারে পেমেন্ট করতে পারেন। আমরা আপনাকে একটি লিংক SMS করব।** | You can pay by bKash, Nagad, card or bank transfer. We will send you a link by SMS. |
| 18 | `ivr.pay.link_sent` | **লিংক পাঠানো হয়েছে।** | The link has been sent. |

### 3.4 Complaint

| # | Key | **Bengali** | English |
|---|---|---|---|
| 19 | `ivr.complaint.intro` | **আমরা দুঃখিত। আপনাকে একজন এজেন্টের সাথে যুক্ত করছি।** | We are sorry. We are connecting you to an agent. |
| 20 | `ivr.complaint.priority` | **আপনার কল অগ্রাধিকার সারিতে রাখা হয়েছে।** | Your call is in the priority queue. |
| 21 | `ivr.complaint.ref` | **আপনার অভিযোগ নম্বর {ref}। আমরা এটি SMS করে পাঠাব।** | Your complaint number is {ref}. We will send it by SMS. |

> **`ivr.complaint.intro` is the one place দুঃখিত is used** (`BN-002` `TN-05`). An apology on every
> prompt devalues the one that matters.

### 3.5 Queue, callback and closure

| # | Key | **Bengali** | English |
|---|---|---|---|
| 22 | `ivr.hold` | **আমাদের সব এজেন্ট ব্যস্ত। আপনার কল গুরুত্বপূর্ণ, আমরা যত দ্রুত সম্ভব উত্তর দেব।** | All our agents are busy. Your call is important and we will answer as soon as we can. |
| 23 | `ivr.position` | **আপনি সারিতে {position} নম্বরে আছেন।** | You are number {position} in the queue. |
| 24 | `ivr.wait_estimate` | **প্রায় {minutes} মিনিট অপেক্ষা করতে হতে পারে।** | The wait is about {minutes} minutes. |
| 25 | `ivr.callback` | **আপনার স্থান রেখে কলব্যাক পেতে ১ চাপুন।** | To keep your place and receive a call back, press 1. |
| 26 | `ivr.callback_ok` | **আমরা {minutes} মিনিটের মধ্যে এই নম্বরে কল করব।** | We will call you back on this number within {minutes} minutes. |
| 27 | `ivr.after_hours` | **আমাদের লাইন {hours} খোলা থাকে। যেকোনো সময় অনলাইনে বুক করুন, অথবা টোনের পরে বার্তা রাখুন।** | Our lines are open {hours}. Book online at any time, or leave a message after the tone. |
| 28 | `ivr.holiday` | **{holiday} উপলক্ষে আজ আমরা বন্ধ। {date}-এ খুলব।** | We are closed today for {holiday}. We reopen {date}. |
| 29 | `ivr.weekend` | **শুক্র ও শনিবার আমাদের সীমিত সেবা চালু থাকে।** | We run a limited service on Friday and Saturday. |
| 30 | `ivr.goodbye` | **1000FiX-এ কল করার জন্য ধন্যবাদ।** | Thank you for calling 1000FiX. |

| # | Rule |
|---|---|
| **VP-02** | **`ivr.weekend` says শুক্র ও শনিবার.** The Bangladesh weekend is Friday and Saturday, which CLDR does not carry for `BD` (`BN-007` `BD-01`). A prompt generated from the locale would name the wrong days |
| **VP-03** | `ivr.holiday` reads from **`MD-041`**, including provisional Eid dates (`IV-05`, `BN-007` `BD-07`) |

### 3.6 Legal and consent

| # | Key | **Bengali** | English |
|---|---|---|---|
| 31 | `ivr.recording` | **মান ও প্রশিক্ষণের জন্য এই কল রেকর্ড করা হতে পারে।** | This call may be recorded for quality and training. |
| 32 | `ivr.identity` | **আপনার পরিচয় নিশ্চিত করতে আমরা কয়েকটি প্রশ্ন করব।** | We will ask a few questions to confirm your identity. |
| 33 | `ivr.ai_disclosure` | **আপনি একটি স্বয়ংক্রিয় সহকারীর সাথে কথা বলছেন। যেকোনো সময় একজন মানুষের জন্য ০ চাপুন।** | You are speaking to an automated assistant. Press 0 at any time for a person. |

| # | Rule |
|---|---|
| **VP-04** | **`ivr.recording` plays before any data is taken** (`IV-04`, `LG-008`). It is not moved later to shorten the call |
| **VP-05** | **`ivr.ai_disclosure` is mandatory wherever an automated assistant answers** (`HC-019`), and the route to a human is stated in the same prompt |

---

## 4. Recording direction

**Direction is content, not production.** A prompt recorded with the wrong pace or the wrong
place-name pronunciation is a defect in this pack.

| Item | Direction |
|---|---|
| Voice | **One female and one male voice**, consistent across the whole tree. A voice change mid-tree is heard as a transfer |
| Accent | **Standard Bangladeshi Bengali.** Not West Bengal Bengali, not a regional dialect (`BN-002` `RD-D`) |
| Pace | **Slower than conversational**, and slower again for digits |
| **Digits** | **Read individually with a pause.** "এস আর — দুই — শূন্য — দুই — ছয়…" Reference numbers are transcribed by hand |
| Amounts | Read as a **spoken figure**, not digit by digit: "তিন হাজার দুইশত টাকা" |
| Dates | Read with the **Bengali month name**: "সতেরোই আগস্ট" |
| Times | **Day-period word, not AM/PM**: "সকাল দশটা" (`BN-007` `FM-20`) |
| **Latin terms** | `Mushak`, `bKash`, `Nagad`, brand names spoken **as in Bengali usage** — not spelled out, not translated (`BN-004` `DN-06`) |
| `1000FiX` | Spoken as **"ওয়ান থাউজেন্ড ফিক্স"** — the established spoken form. Registered here so that every recording matches |
| `16743` | Read **digit by digit** |
| Tone | Calm, unhurried, not cheerful. A caller with a broken device is not in a good mood |
| Room | Consistent acoustic across all recordings; no splicing between sessions |

| # | Rule |
|---|---|
| **VP-06** | **Never splice a new phrase into an old recording.** The join is audible and reads as a system fault (`NT-019` §2.3) |
| **VP-07** | **Digits are always read individually in identifiers**, and always as a figure in money (`BN-006` `NU-08`) |
| **VP-08** | **A placeholder read by text-to-speech is verified with real values**, including the longest realistic branch name and a Bengali customer name |
| **VP-09** | **Any wording change requires a re-record** of the affected prompt (`NT-019` §2.3, `BN-003` §15.2). This is why prompts pass G4 **before** recording |
| **VP-10** | The **pronunciation of every place name is taken from local usage**, not from the spelling. `MD-006` carries the name; this pack carries how it is said |

### 4.1 Pronunciation register

Maintained alongside the recordings. One row per term whose pronunciation is not obvious from
its spelling.

| Term | Spoken as | Note |
|---|---|---|
| `1000FiX` | ওয়ান থাউজেন্ড ফিক্স | `VP-06` |
| `16743` | এক — ছয় — সাত — চার — তিন | Digit by digit |
| `Mushak 6.3` | মুশক ছয় দশমিক তিন | Spoken Bengali; **written form stays Latin** (`BN-004`) |
| `bKash` | বিকাশ | Spoken as Bangladeshis say it; **written form stays Latin** |
| `Nagad` | নগদ | As above |
| `VAT` | ভ্যাট | As above |
| `SR-2026-114882` | এস আর — দুই শূন্য দুই ছয় — এক এক চার আট আট দুই | `VP-07` |
| Chattogram | চট্টগ্রাম | `MD-006` |
| Cumilla | কুমিল্লা | `MD-006` |
| Jashore | যশোর | `MD-006` |

> **The written/spoken split is deliberate and is the one place `BN-004` `DN-02` is relaxed.**
> A do-not-translate item is never *written* in Bengali script; it is *spoken* the way
> Bangladeshis say it, because a voice prompt that spells out "b-K-a-s-h" is unusable.
> `BN-004` `DN-06` states the rule; this register implements it.

---

## 5. Agent-spoken content

The written agent scripts are `SP-034` and are **native Bengali** (`BN-016` §6). This section
covers the spoken discipline that sits on top of them.

| # | Rule |
|---|---|
| **AG-01** | **The agent says the `MD-027` customer label**, not the internal state (`VP-01`, `BN-011` `CC-01`) |
| **AG-02** | **The recording notice and the identity check are spoken before account details** (`VP-04`, `BN-013` `CC-02`) |
| **AG-03** | Agents use **আপনি** with every caller without exception (`BN-002` `AD-01`) |
| **AG-04** | **Reference numbers are read back digit by digit and confirmed** before the call ends |
| **AG-05** | Amounts are **stated and then confirmed**: "তিন হাজার দুইশত টাকা — ঠিক আছে?" |
| **AG-06** | An agent **never commits to a price, a date or a legal position** not shown on their screen (`HC-019`) |
| **AG-07** | Where the caller switches to English mid-call, **the agent follows**; the language is the caller's choice, per call (`BN-001` `LR-06`) |
| **AG-08** | Code-mixing is **natural in spoken Bengali and is permitted on calls**, unlike in written content. An agent saying "আপনার estimate টা approve করতে হবে" is speaking normally. The **written** note they then type follows `BN-002` §4 |

> **`AG-08` is a deliberate divergence between spoken and written policy**, and it is the only one
> in this category. Forcing an agent to speak strictly translated Bengali makes them sound like a
> recording and lengthens every call.

---

## 6. Voice notes on `P02`

| # | Rule |
|---|---|
| **VN-B01** | Technicians record voice notes **in Bengali** (`04-00` §P02 Evidence, `NFR-074`) |
| **VN-B02** | The **audio is the record.** A transcript is an aid, not a replacement |
| **VN-B03** | Voice-to-text output is **stored as Bengali** and is **never machine-translated** (`CG-010` MT-01, `BN-006` `IM-05`) |
| **VN-B04** | Transcripts are **NFC-normalised on write** so they are searchable (`BN-006` `EN-02`) |
| **VN-B05** | A transcript is marked as **machine-generated** wherever it is displayed, so no one relies on it as verbatim |
| **VN-B06** | Voice notes may contain **customer-identifiable audio** and are in scope for `05-06` NFR-086 residency and `LG-009` retention |
| **VN-B07** | **Voice notes are not used to train a speech model** without the basis `AUDIT-010` HC-01 leaves open (`BN-016` `AI-B05`) |

---

## 7. Accessibility

| # | Rule | Reference |
|---|---|---|
| **AC-V1** | **Zero always reaches a human, at every level** (`IV-03`). This is an accessibility control, not only a service one |
| **AC-V2** | **No option loops to the main menu more than once**; the third failure transfers to an agent (`IV-06`) |
| **AC-V3** | **Every prompt is repeatable** — `ivr.menu_repeat` (`WCAG` 2.2.1 analogue for voice) |
| **AC-V4** | **No time limit shorter than 10 seconds** for DTMF entry, and the timeout is announced |
| **AC-V5** | A caller who cannot use DTMF reaches an agent by **staying silent twice** — `ivr.no_input` then transfer |
| **AC-V6** | The IVR is usable **without any visual channel**, which is the baseline case, not an accommodation |

---

## 8. Verification

| Check | Mechanism | When |
|---|---|---|
| Prompt wording matches the approved script | Text diff | Before recording |
| **G4 in-context — listened to, not read** | **Human, on a phone call** | Before recording and after |
| Digit read-back intelligibility | Listening test with a hand transcription | Every reference-bearing prompt |
| Place-name pronunciation | Native speaker from the division concerned | Per place name |
| Placeholder rendering by TTS with real values | Automated playback plus listening | Every dynamic prompt |
| Status wording matches `MD-027` | Cross-check | Every release |
| Recording notice plays before data capture | Call-flow test | Every release |
| Holiday and after-hours prompts fire correctly | Call-flow test against `MD-041` | Before each holiday period |
| **Weekend prompt names Friday and Saturday** | Call-flow test | Every release |
| Line noise, level and consistency | Audio QA | Every recording session |

| # | Rule |
|---|---|
| **VF-01** | **G4 for voice is listening, not reading.** A script that reads well and sounds wrong has failed (`BN-018` §5) |
| **VF-02** | Verification uses a **real phone call over a real network**, not a local playback |

---

## 9. Coverage ledger

**Counted by enumeration on 2026-08-17** (`CP-11`, `CM-R2`, F7).

| Section | Prompts |
|---|---:|
| Entry and menu | 6 |
| Tracking | 7 |
| Payment | 5 |
| Complaint | 3 |
| Queue, callback and closure | 9 |
| Legal and consent | 3 |
| **Total `ivr.*` prompts authored** | **33** |

| Measure | Counted |
|---|---:|
| `ivr.*` prompts enumerated in `NT-019` | **13** |
| `ivr.*` prompts authored here | **33** |
| **Added beyond the English source** | **20** — `ivr.menu_repeat`, `ivr.invalid`, `ivr.no_input`, `ivr.ref_confirm`, `ivr.status_eta`, `ivr.status_ready`, `ivr.multiple`, `ivr.pay.*` ×5, `ivr.complaint.*` ×3, `ivr.wait_estimate`, `ivr.weekend`, `ivr.goodbye`, `ivr.identity`, `ivr.ai_disclosure` |

Non-prompt content: **8** agent-spoken rules (§5), **7** voice-note rules (§6), **10**
pronunciation-register entries (§4.1), **6** accessibility rules (§7).

> **The first issue of this table said 41 prompts in the summary, 33 in the total row and 28
> added — three figures that cannot all be right.** The counted figures are **33 authored, 13 in
> the source, 20 added**. Recorded as `AUDIT-012` **BN-19**. The 20 additions are still raised to
> `NT-019`'s owner as an English gap (`AUDIT-012` **BN-17**).

---

## 10. Open items

| # | Item | Owner | Blocks |
|---|---|---|---|
| 1 | **`NT-019` names `BN-014` as its Bengali counterpart; correct to `BN-017`** | `NT-019` owner | Register accuracy |
| 2 | **28 prompts here have no English source row in `NT-019`** | Content Design Lead with `M27` owner | `NT-019` completeness |
| 3 | Voice talent selected and a pronunciation session held before recording | Contact Centre Manager | All recordings |
| 4 | **`ivr.weekend` requires the `BN-007` `BD-01` weekend confirmation** | Service Operations | `VP-02` |
| 5 | `MD-041` business calendar populated with provisional Eid dates | MDM | `VP-03`, `ivr.holiday` |
| 6 | **PDPA basis for voice-note and call-recording reuse** (`VN-B07`, `AUDIT-010` HC-01) | Legal Counsel with CDO | `VN-B07` |
| 7 | `SP-034` native agent scripts written (`BN-016` §6) | Contact Centre Manager | §5 |
| 8 | `BN-002` and `BN-007` ratification | Programme Content Lead | All prompts |

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`../04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-019_IVR_and_Voice_Prompt_Scripts.md`](../04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-019_IVR_and_Voice_Prompt_Scripts.md) | The source pack — and the file whose counterpart pointer is wrong |
| [`BN-014_Bengali_Notification_and_SMS_Pack.md`](BN-014_Bengali_Notification_and_SMS_Pack.md) | The other channels; **`NT-019` is not in it** |
| [`BN-013_Bengali_String_Bundle_P07_to_P12.md`](BN-013_Bengali_String_Bundle_P07_to_P12.md) | The `P10` console the agent uses while speaking |
| [`BN-016_Bengali_Help_and_Training_Content_Plan.md`](BN-016_Bengali_Help_and_Training_Content_Plan.md) | `SP-034` native scripts |
| [`BN-007_Date_Time_Number_Currency_and_Address_Formats.md`](BN-007_Date_Time_Number_Currency_and_Address_Formats.md) | Weekend, day periods, spoken amounts |
| [`BN-004_Do_Not_Translate_and_Transliteration_Register.md`](BN-004_Do_Not_Translate_and_Transliteration_Register.md) | `DN-06`, which §4.1 implements |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-027_Status_and_Lifecycle_State_Label_Register.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-027_Status_and_Lifecycle_State_Label_Register.md) | The status wording spoken in `ivr.status` |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-17 | Initial issue. **33 Bengali prompts counted**, 20 of them beyond `NT-019`'s thirteen and raised as an English gap; **the `NT-019` counterpart mislabelling corrected**; recording direction treated as content, with a pronunciation register implementing the written/spoken split for do-not-translate items; the Friday–Saturday weekend prompt that the locale would get wrong; spoken code-mixing permitted for agents as a deliberate divergence from written policy; voice-note handling including the no-machine-translation and PDPA constraints; six voice accessibility rules; G4 defined as listening rather than reading | Localisation Lead with Contact Centre Manager (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:`, `traces_to:`, `channels:` and `consent_class:`
- [x] **Authored as native Bengali, with the English marked as the translation** (`CG-010` §4.2)
- [x] Every `NT-019` prompt carried, and the 28 additions itemised and routed to the English owner
- [x] Description-before-option and four-options-plus-zero held throughout
- [x] Status wording spoken from `MD-027`, matching the portal and the SMS
- [x] **Recording direction specified as content**, with a pronunciation register
- [x] The written/spoken divergence for do-not-translate items stated and reasoned
- [x] The Bangladesh weekend spoken correctly, against a locale that would get it wrong
- [x] Consent, recording notice and AI disclosure placed before data capture
- [x] Voice-note handling covers storage, transcription, translation prohibition and retention
- [x] Accessibility rules stated as controls, with zero always reaching a human
- [x] **G4 defined as listening on a real call**, not reading a script
- [x] All internal links resolve
- [ ] **G4 listening review** — outstanding; blocks `Approved`
- [ ] **Recordings produced** — outstanding; wording must pass G4 first (`VP-09`)
- [ ] **`NT-019` counterpart pointer corrected** — outstanding; §10 item 1
- [ ] **PDPA basis for voice-note reuse** — outstanding; §10 item 6
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
