---
id: VB-001
title: ERP Product Voice and Tone Guide
project: 1000FiX ERP System v2.0
content_type: Standard
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design Lead
author: Content Design
reviewers: [Brand, Programme Content Lead, Localisation Lead, Business Owners Forum]
approver: Content Design Lead
content_class: E
purpose: >
  Defines how the ERP sounds. Marketing voice applied to a dispatch console produces cheerful
  ambiguity in a time-critical workflow; an unvoiced ERP produces twelve portals that each sound
  like the team that built them. This guide fixes the voice once, for every surface, and states
  how tone shifts by situation without the voice changing.
traces_to: [04-00 PS-06, 04-00 PS-09, CG-003, VB-002, VB-006]
priority: P0
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §3 PS-06 (one design system), PS-09 (every error states what happened and what to do)
    verified: 2026-08-15
    class: P1
  - source: 1000_fix_corporate_website project_content CB-005 Brand Voice Guidelines v1.0 — professional, trustworthy, helpful, friendly
    verified: 2026-08-15
    class: P1
  - source: 1000_fix_corporate_website project_content CB-001 Brand Guidelines Document v1.0 §1 brand personality
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# VB-001 — ERP Product Voice and Tone Guide

> **The company already has a brand voice.** `CB-005` defines it for marketing: *"the trusted
> friend who also happens to be a tech expert — knowledgeable without being condescending,
> professional without being cold, and helpful without being pushy."*
>
> **That voice is correct, and it is not sufficient here.** It was written for a person choosing
> whether to trust us. This guide is for a person who has already trusted us and is now trying
> to get something done — often quickly, often under pressure, sometimes at 11pm with a
> customer waiting.

---

## 1. Purpose

| | |
|---|---|
| **What this governs** | The voice of every word the ERP and its twelve portals produce |
| **What it does not govern** | Mechanics — spelling, case, punctuation, numbers (`CG-003`); which word (`CG-004`); tone per audience (`VB-002`); component copy (`VB-006`) |
| **Who uses it** | Anyone writing UI copy, notifications, help, training, documents or system messages |
| **What breaks without it** | Twelve portals built by five teams in five frameworks, each sounding like its authors |

---

## 2. Scope

**In scope:** the voice of all ERP-produced content — `UI`, `NT`, `DT`, `SP`, `KB`, `TR`, `HC`,
`OP`, `EO` and `RP` categories.

**Out of scope:** the corporate website and marketing content, which retain `CB-005`. The two
content sets are deliberately separate (Master Index §11). Where they meet — the four interface
points — the ERP voice governs, because the user is transacting, not evaluating.

---

## 3. Voice: the four principles

Voice does not change. Tone does. These four hold on every surface, in every situation, in both
languages.

### 3.1 Clear before clever

The reader is mid-task. Every word they must decode is a word that delays them.

| Write | Not |
|---|---|
| The estimate is waiting for the customer to approve it. | The estimate is pending customer disposition. |
| This part is not in stock at Shewrapara. | Part availability could not be confirmed at this location. |
| You cannot issue parts until the estimate is approved. | Parts issuance is contingent upon estimate approval status. |

**Test:** could a service centre agent in their first week act on this without asking anyone?

### 3.2 Specific before general

A vague message is a message the reader must investigate. Naming the thing is the whole job.

| Write | Not |
|---|---|
| 3 parts are on hold for job SR-2026-114882. | Some parts are unavailable. |
| Rahim Uddin declined the estimate on 14 August. | The estimate was declined. |
| This device has been in the workshop for 9 days. The target is 5. | This device is overdue. |

**Test:** does the reader know **which** thing, **whose** thing, and **how much**?

### 3.3 Honest before comfortable

The system will lose a part, miss an SLA, fail a payment and hold a device too long. When it
does, the content says so.

| Write | Not |
|---|---|
| We could not collect your device today. We will call you before 11am tomorrow to rebook. | Your collection has been rescheduled for your convenience. |
| Payment failed. Your card issuer declined it. Try another method or pay at the service centre. | Something went wrong. Please try again. |
| This repair is 4 days past its target. The delay is a part we are waiting for from the supplier. | Your repair is in progress. |

**Test:** if the reader later learns what actually happened, would they feel the content had been
straight with them?

### 3.4 Calm under failure

The moments that most define how the system feels are the moments it is not working. The voice
does not become apologetic, panicked, jokey or defensive.

| Write | Not |
|---|---|
| The payment gateway is not responding. Take payment at the counter and record it here when the gateway returns. | Oops! Something went wrong on our end. Sorry about that! |
| You cannot approve your own estimate. Send it to your branch manager. | Error: Unauthorised operation. |
| The app is offline. Your last 6 actions are saved and will sync when you reconnect. | Connection lost!! |

**Test:** would a person under time pressure feel steadier, or worse, after reading this?

---

## 4. What 1000FiX never sounds like

| Never | Why | Instead |
|---|---|---|
| **Chirpy** — "Great news!", "Woohoo!", exclamation marks | At the thousandth repetition it reads as insincere; in a failure it reads as mockery | State the fact |
| **Apologetic** — "Sorry", "We apologise for any inconvenience" | An apology in a system message is evasion dressed as courtesy | State what happened and the remedy |
| **Deferential** — "Please", "Kindly", "If you would" | Adds a word to every label; in Bengali it also forces a register choice on every string | Imperative: "Select a technician" |
| **Blaming** — "You entered an invalid date" | The user did what the interface allowed | "Enter the date as DD/MM/YYYY" |
| **Minimising** — "simply", "just", "easily", "quick" | Tells a struggling reader their difficulty is their own fault | Remove the word |
| **Corporate** — "leverage", "utilise", "facilitate", "going forward" | Longer, vaguer, and untranslatable into plain Bengali | Use the plain verb |
| **Legalistic in UI** — "The Company shall not be liable" | Terms belong in `LG` content, cited from the UI, not restated in it | Link to the term |
| **Technical about itself** — "NullReferenceException", "sync token mismatch" | Exposes internals and helps nobody. Also a security rule (`CG-003` E-02) | Say what the user should do |
| **Falsely certain** — "instantly", "guaranteed", "always", "never fails" | The system will contradict it, and some of these are legal claims (`CG-013` §2.4) | State the actual behaviour |
| **Jokey** — puns, wordplay, personality asides | Does not survive translation, does not survive a complaint, does not survive the tenth reading | Remove |

> **The "please" decision, stated once.** `CB-005` uses "please" for the marketing voice and that
> is right for marketing. It is banned in ERP UI, notifications and documents (`CG-003` §8.1).
> It is permitted in help articles, training and change communications, where a conversational
> register aids comprehension. This is a deliberate divergence, not an inconsistency.

---

## 5. Tone: five situations

Tone is voice adapted to the moment. The four principles never bend; their proportions shift.

| Situation | Dominant principle | Length | Register | Never |
|---|---|---|---|---|
| **Routine** — a normal action completing | Clear | Shortest possible | Neutral, factual | Celebration |
| **Instructional** — the user must do something | Clear + specific | As long as needed, no longer | Direct, imperative | Hedging |
| **Failure** — something did not work | Calm + honest | Enough for cause and remedy | Level, unhurried | Apology, blame, jargon |
| **Consequential** — an irreversible or costly action | Specific + honest | Long enough to state the consequence in full | Deliberate, slightly formal | Speed, reassurance |
| **Recognition** — genuine achievement | Clear | Brief | Warm but plain | Confetti |

### 5.1 Routine

The commonest tone and the easiest to get wrong by overwriting it.

> Service order created. SR-2026-114882.
> Estimate sent to the customer.
> 4 parts issued to Karim Hossain.

Not: "Success! Your service order has been created successfully."

### 5.2 Instructional

> Scan the device barcode, then confirm the accessories the customer has left with it.

> To release this device, take the outstanding payment of BDT 3,200 or record an approved
> payment exception.

### 5.3 Failure

Three parts, in order: **what happened · why, if it is not obvious · what to do next**
(`CG-003` §3).

> The bKash payment did not complete. bKash reported that the customer's balance is
> insufficient. Ask the customer to top up and retry, or take payment by another method.

> This job cannot be assigned to Karim Hossain. His Samsung warranty certification expired on
> 31 July. Assign a certified technician, or ask the Quality Manager to renew the certification.

### 5.4 Consequential

The user is about to do something they cannot undo, or something that costs money, or something
a customer will feel. Slow the moment down.

> **Cancel this service order**
>
> The customer will be notified by SMS. The 4 reserved parts will be returned to stock. The
> device is still at the branch and must be returned to the customer or the order re-raised.
>
> This cannot be undone.
>
> Reason for cancellation (required): ______
>
> [Cancel order] [Keep order]

### 5.5 Recognition

Rare, brief, and only where the achievement is real.

> Karim Hossain — 40 jobs completed this month, first-time fix on 38.

Not: "🎉 Amazing work! You're crushing it!"

---

## 6. Voice in the two languages

The voice is one voice. It is not "English voice, translated".

| # | Rule |
|---|---|
| **VL-01** | The four principles apply identically in Bengali. Bengali content that is polite but vague fails `3.2`; Bengali content that is precise but cold fails nothing — precision is the courtesy |
| **VL-02** | Bengali register is decided once in `BN-002`, not per string. `CG-010` §7 records the open decision and the proposed position |
| **VL-03** | Bengali honorifics are a register decision, not a voice decision. Whatever `BN-002` decides applies everywhere, including error messages |
| **VL-04** | Where an English phrase carries the voice through idiom, the Bengali conveys the **meaning**, not the idiom (`CG-010` BP-07) |
| **VL-05** | Bengali-native content (`CG-010` §4.2) — field technician training, contact centre scripts, chatbot utterances — is written to this voice in Bengali first, then translated to English for governance |

---

## 7. Voice by surface

Detailed calibration is `VB-002`. This is the one-line summary.

| Surface | Voice emphasis | Note |
|---|---|---|
| `P01` Customer | Clear, honest | Bengali-first. The customer has our device and their money at stake |
| `P02` Technician | Specific, calm | Bengali, complete. Read one-handed, outdoors, sometimes offline |
| `P03` Admin | Clear, specific | Dense, fast, keyboard-first. Brevity is the courtesy |
| `P04` Corporate | Specific, honest | Forwarded internally to people who never log in |
| `P05` Vendor | Clear, specific | Every ambiguity becomes a phone call we are trying to eliminate |
| `P06` Analytics | Specific | A metric name that is imprecise produces a confidently wrong decision |
| `P07` Seller | Clear, honest | External workforce; payout and performance language is where trust lives |
| `P08` Brand | Specific, honest | International audience reading our evidence |
| `P09` Rider | Clear | Shortest content in the system. One-handed, moving |
| `P10` Contact centre | Specific, calm | Read aloud, or read while a customer waits |
| `P11` Auditor | Specific | Classification language *is* the standard |
| `P12` Partner | Clear, honest | Attribution and commission wording is a trust surface |

---

## 8. Applying the voice — a worked rewrite

The same message, wrong and right, showing each principle doing work.

**Before**

> ⚠️ Oops! It seems there was a problem processing your request. Unfortunately, we were unable
> to complete the operation at this time. Please try again later or kindly contact our support
> team for further assistance. We apologise for any inconvenience caused!

Failures: chirpy ("Oops!"), apologetic (twice), deferential ("kindly", "please"), vague (which
request? what problem?), no remedy ("try again later" is not an action), exclamation mark,
53 words.

**After**

> The warranty claim was not submitted. Samsung's system rejected it because the purchase proof
> is missing. Attach the purchase invoice and submit again.

Clear, specific, honest, calm. 27 words. States what, why and what next.

---

## 9. Dependencies

| Depends on | Why |
|---|---|
| `CG-003` ERP Product Content Style Guide | Voice is expressed through mechanics; the two must not contradict |
| `CG-004` Terminology Standard | "Specific" is impossible without one approved word per thing |
| `CG-010` Bilingual Content Policy | Which surfaces carry the voice in Bengali |
| `BN-002` Bengali Translation Standard | The register the voice takes in Bengali |
| `04-00` PS-06, PS-09 | The design-system and error-message obligations the voice serves |

---

## 10. Enforcement

| Mechanism | How |
|---|---|
| Gate G1 Editorial (`CG-007`) | Voice is a named check at editorial review |
| Automated | The `CG-003` §8.1 banned-word list covers the mechanical half — "please", "oops", "simply", "sorry", exclamation marks in UI |
| Rewrite test | Any reviewer may apply §8: does the message state what, why and what next? |
| Sampling | `CG-014` Q-02 terminology and style defect rate, target under 2% |
| Content metrics | `CG-014` E-06 error-message abandonment and E-07 error recurrence measure whether the voice is working, not whether it was followed |

---

## 11. Maintenance

| Item | Value |
|---|---|
| Review cadence | Every two waves (Class E, `CG-006` §5) |
| Out-of-cycle trigger | A `CB-005` revision; a portal launching with a materially different register; sustained `E-06`/`E-07` degradation |
| Owner | Content Design Lead |
| Deputy | Programme Content Lead |

---

## 12. Related documents

| Document | Relationship |
|---|---|
| [`VB-002_Persona_and_Portal_Tone_Matrix.md`](VB-002_Persona_and_Portal_Tone_Matrix.md) | Tone calibration per audience |
| [`VB-006_Design_System_Content_Standards.md`](VB-006_Design_System_Content_Standards.md) | Voice bound to components |
| [`../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md`](../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md) | Mechanics |
| [`../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | Which word |
| [`../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) | Bilingual coverage |
| `UI-004` Validation & Error Message Library | Where §5.3 is applied at scale |
| `BN-002` Bengali Translation Standard | The Bengali register |
| `CB-005` Brand Voice Guidelines (website set) | The marketing voice this one diverges from, deliberately |

---

## 13. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Four voice principles with tests, ten "never" patterns, five tonal situations with examples, bilingual voice rules, per-surface emphasis, worked rewrite | Content Design Lead (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` with the `VB` additions from `CG-009` §3
- [x] Divergence from `CB-005` stated explicitly rather than left as a contradiction
- [x] Every principle carries a decidable test, not only an example
- [x] All internal links resolve
- [x] Accessibility — n/a, internal governance document
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [x] Decisions logged in `RF-006`

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
