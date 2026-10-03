---
id: NT-019
title: IVR and Voice Prompt Scripts
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
reviewers: [Contact Centre, Localisation Lead, Legal & Compliance, Accessibility reviewer]
approver: Content Design Lead
content_class: D
purpose: >
  Hotline 16743 IVR tree, prompts, menus, hold, callback and after-hours messages, bilingual, with
  recording direction. The hotline is the highest-trust channel for a large share of 250,000+ monthly
  customers and predates the portal by years.
traces_to: [M27, P10, NT-001, BN-017, SP-034, MD-041]
priority: P1
wave: W4
bilingual: yes
bn_counterpart: NT-019_IVR_and_Voice_Prompt_Scripts_BN.md
channels: [Voice (IVR)]
consent_class: Transactional — inbound
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

# NT-019 — IVR and Voice Prompt Scripts

> **Spoken content, not read content.** Every prompt is heard once, without the ability to scan
> back. Sentences are short, the option comes **after** the description, and the menu never
> exceeds four options at one level.
>
> Bengali is authored natively here, not translated (`CG-010` §4.2).

---

## 1. Set summary

| Item | Value |
|---|---|
| Channel(s) | Voice (IVR) |
| Audience | Every caller to 16743 |
| Owning module | `M27`, `P10` |
| Consent class | Transactional — inbound |
| Quiet-hours exempt | n/a — the caller initiates |
| Content class | D — User-facing |
| Bengali required | **Yes** — see `BN-014` |
| Bangladesh routing | Hotline 16743 |

---

## 2. Templates

### 2.1 The tree

```
16743
├─ Language: 1 বাংলা · 2 English
├─ 1  Track my service        → reference or mobile → status readback
├─ 2  Book a service          → transfer to agent
├─ 3  Payment and invoices    → 1 balance · 2 how to pay · 3 agent
├─ 4  Something is wrong      → complaint → agent (priority queue)
└─ 0  Speak to someone
```

Four options at the top level plus zero. `SP-034` carries the agent scripts that follow.

### 2.2 Prompts

| # | Prompt | Key | English | Bengali |
|---|---|---|---|---|
| 1 | Greeting | `ivr.greeting` | Welcome to 1000FiX. | 1000FiX-এ স্বাগতম। |
| 2 | Language | `ivr.language` | For Bengali press 1. For English press 2. | বাংলার জন্য ১ চাপুন। For English press 2. |
| 3 | Main menu | `ivr.menu` | To track a service, press 1. To book, press 2. For payments, press 3. To report a problem, press 4. To speak to someone, press 0. | সার্ভিস ট্র্যাক করতে ১ চাপুন। বুক করতে ২। পেমেন্টের জন্য ৩। সমস্যা জানাতে ৪। কারো সাথে কথা বলতে ০। |
| 4 | Reference prompt | `ivr.ref_prompt` | Enter your reference number, or press hash to use your mobile number. | আপনার রেফারেন্স নম্বর দিন, অথবা মোবাইল নম্বর ব্যবহার করতে হ্যাশ চাপুন। |
| 5 | Status readback | `ivr.status` | Your {device}, reference {ref}, is {customer_status}. | আপনার {device}, রেফারেন্স {ref}, {customer_status}। |
| 6 | Not found | `ivr.not_found` | We could not find that reference. Press 0 to speak to someone. | সেই রেফারেন্স পাওয়া যায়নি। কারো সাথে কথা বলতে ০ চাপুন। |
| 7 | Hold | `ivr.hold` | All our agents are busy. Your call is important and we will answer as soon as we can. | আমাদের সব এজেন্ট ব্যস্ত। আপনার কল গুরুত্বপূর্ণ, আমরা যত দ্রুত সম্ভব উত্তর দেব। |
| 8 | Queue position | `ivr.position` | You are number {position} in the queue. | আপনি সারিতে {position} নম্বরে আছেন। |
| 9 | Callback offer | `ivr.callback` | To keep your place and receive a call back, press 1. | আপনার স্থান রেখে কলব্যাক পেতে ১ চাপুন। |
| 10 | Callback confirmed | `ivr.callback_ok` | We will call you back on this number within {minutes} minutes. | আমরা {minutes} মিনিটের মধ্যে এই নম্বরে কল করব। |
| 11 | After hours | `ivr.after_hours` | Our lines are open {hours}. Book online at any time, or leave a message after the tone. | আমাদের লাইন {hours} খোলা থাকে। যেকোনো সময় অনলাইনে বুক করুন, অথবা টোনের পরে বার্তা রাখুন। |
| 12 | Holiday | `ivr.holiday` | We are closed today for {holiday}. We reopen {date}. | {holiday} উপলক্ষে আজ আমরা বন্ধ। {date}-এ খুলব। |
| 13 | Recording notice | `ivr.recording` | This call may be recorded for quality and training. | মান ও প্রশিক্ষণের জন্য এই কল রেকর্ড করা হতে পারে। |

### 2.3 Recording direction

| Item | Direction |
|---|---|
| Voice | One female and one male voice, consistent across the whole tree |
| Bengali pronunciation | Standard Bengali; place names as locally pronounced |
| Pace | Slower than conversational, especially for digits |
| Digits | Read individually with a pause — reference numbers are transcribed by hand |
| Latin terms | `Mushak`, `bKash`, brand names spoken as in Bengali usage (`BN-004`) |
| Re-record trigger | Any wording change; never splice a new phrase into an old recording |

### 2.4 Rules

| # | Rule |
|---|---|
| **IV-01** | Description first, option second: "To track a service, press 1" — never "Press 1 to track" |
| **IV-02** | Maximum four options plus zero at any level |
| **IV-03** | Zero always reaches a human, at every level |
| **IV-04** | The recording notice plays before any data is taken (`LG-008`) |
| **IV-05** | Holiday and after-hours messages read from `MD-041`, including provisional Eid dates |
| **IV-06** | No option loops back to the main menu more than once — the third failure transfers to an agent |

---

## 3. Channel-specific requirements

| Requirement | Rule |
|---|---|
| Language | Bengali-native authoring; English is the translation (`CG-010` §4.2) |
| Terminology | Customer-facing labels only; never an internal state name (`T-06`) |
| Accessibility | DTMF and speech both supported; no time-out under 8 seconds |
| Calendar | Holiday messages from `MD-041` with `date_confirmed` respected |
| Recording | Notice before data capture; retention per `LG-009` |

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
| `SP-034` Call and Conversation Script Library | Agent scripts after transfer |
| `BN-017` Bengali Voice, IVR and Speech Prompt Pack | Recording pack |
| `MD-041` Holiday Calendar | Holiday and after-hours logic |
| `P10` Contact Centre Agent Console | Where the call lands |

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
