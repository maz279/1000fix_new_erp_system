---
id: HC-002
title: Help Article Template and Style Rules
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design
author: Content Design with Customer Experience and Localisation
reviewers: [Customer Service Manager, Knowledge Manager, Localisation Lead, Accessibility reviewer, Legal Counsel, Programme Content Lead]
approver: Content Design Lead
content_class: E
purpose: >
  The task-article structure, screenshot rules, step numbering, prerequisite and outcome statements
  and bilingual pairing rules that make help maintainable across nine waves of UI change. Help
  written to no template cannot be maintained: every release orphans it, every author restructures
  it, and the translation cost is paid again each time because nothing about it is predictable.
traces_to: [M61, M32, P01, P02, P09, HC-001, HC-015, HC-016, HC-020, CG-003, CG-004, CG-008, CG-011, CG-014, VB-009, BN-003, UI-002, UI-003, MM-002, TR-003]
priority: P2
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/_templates/TPL_Help_Article.md — the enforced authoring template for the 15 help-article files in this category (CG-009 §3)
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md — WCAG 2.1 AA is contractual under 04-00 PS-04 and 05-06; most WCAG failures are content failures
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §5.2 FR-KMS-022 — customer self-help served with symptom-led navigation, in Bengali, on a 3G connection
    verified: 2026-08-18
    class: P1
  - source: project_content/08_Training_and_Enablement/08A_Framework/TR-003_Course_Design_Standard_and_Storyboard_Template.md DS-12…DS-16 — the screenshot maintenance trap and the rules that contain it across nine waves of UI change
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# HC-002 — Help Article Template and Style Rules

> **`HC-001` says how help is structured and found. This file says what an article looks like** —
> so that fifteen help sets written by several authors over five waves can be reviewed, translated,
> measured and updated by someone who wrote none of them.

---

## 1. Purpose

Nine waves of UI change over thirty-six months will pass through this content. The register's own
justification is exact: *"Help written to no template cannot be maintained across nine waves of UI
change."*

The failure is cumulative and quiet:

| Without a standard | Consequence by W5 |
|---|---|
| Structure per author | Nothing can be reviewed against anything; QA becomes opinion |
| Screenshots used freely | Most articles show a UI that no longer exists |
| Steps written as prose | Translation cost doubles; the reader loses their place |
| Outcomes unstated | The reader completes the steps and does not know whether it worked |
| Bengali produced by handing text to a translator | Translated concepts, not the task (`CG-010`) |
| No reading-level discipline | `CG-011` fails, and the customers who most need help are the ones who cannot use it |

**Consequence of absence (`CP-03`).** Fifteen help sets that cannot be maintained, cannot be
consistently translated, and degrade into a liability the contact centre works around.

---

## 2. Scope

**In scope:** the article skeleton and what each block is for; step-writing rules; prerequisite and
outcome statements; the screenshot regime; troubleshooting-block construction; reading level and
plain language; bilingual pairing; accessibility; the exit-to-human rule; versioning and currency;
and rules `HS-01`…`HS-24`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Architecture, facets, category tree, findability | [`HC-001_Help_Centre_Information_Architecture.md`](HC-001_Help_Centre_Information_Architecture.md) |
| The help content itself | `HC-003`…`HC-014` |
| FAQ item construction | [`HC-015_FAQ_Bank_by_Audience.md`](HC-015_FAQ_Bank_by_Audience.md) |
| In-product tip and coach-mark copy | [`HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md`](HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md) |
| Conversational AI response copy | `HC-018`, `HC-019` |
| Video scripts | [`HC-020_Video_Tutorial_Script_Library.md`](HC-020_Video_Tutorial_Script_Library.md) |
| Product voice, tense, person, capitalisation | [`../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md`](../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md) |
| Approved terminology and banned synonyms | [`../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) |
| Bengali typography and numerals | `VB-009` · `BN-003` |
| Screenshot and media production specs | `MM-002` |
| UI labels themselves | `UI-002`, `UI-003` — **help quotes them, never invents them** |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Content designers** | Author help that passes review first time |
| **Portal owners contributing content** | Contribute in a usable shape |
| **Localisation Lead** | Receive predictable, translatable structure |
| **Accessibility reviewer** | Check against `CG-011` at draft, not after publication |
| **Reviewers** | Review against something specific (§4.10) |
| **`M32` team** | Understand the shape of the corpus they ground on |

---

## 4. Content

### 4.1 The article skeleton

Every `HLP-` article carries these blocks in this order. The skeleton **is**
`TPL_Help_Article.md`; this section states what each block is for and what makes it wrong.

| # | Block | Purpose | Fails when |
|---:|---|---|---|
| 1 | **Identity table** | Portal, audience, article type, reading level, languages, related UI copy | Facets missing (`IA-18`) |
| 2 | **Title** | States the task from the reader's point of view | Written as a feature name — *"Order management"* rather than *"Track your repair"* |
| 3 | **Before you start** | Prerequisites, each with **why** | Lists prerequisites without reasons, so the reader skips them |
| 4 | **Steps** | Numbered, one action each | Written as prose; or mixes what to do with what it means |
| 5 | **What happens next** | System response, notifications, who is told, expected timing | Absent — the commonest defect (§4.4) |
| 6 | **If it does not work** | Symptom → cause → what to do | Lists errors without causes, or without an action |
| 7 | **Related** | At most five (`IA-10`) | Becomes a category listing |
| 8 | **Feedback** | Helpfulness capture (`CG-014`) | — |

**`HS-01`: no block is removed.** A task with no prerequisites states *"Nothing — you can start
straight away."* An empty block is information; a missing block is an unanswered question.

### 4.2 Titles

**`HS-02`: titles are the reader's task in the reader's words, in the second person.**

| ✅ | ❌ | Why |
|---|---|---|
| "Track your repair" | "Order status enquiry" | The reader does not know they have an "order" |
| "Change your appointment time" | "Appointment rescheduling module" | Feature name, not task |
| "Your device isn't cooling" | "AC troubleshooting" | Symptom-led (`IA-08`); matches how they search |
| "Approve a repair estimate over BDT 5,000" | "Estimate approval" | States the case that actually applies |
| "Why we need your device's serial number" | "Serial number" | A concept article answers a *question* |

**`HS-03`: a troubleshooting article's title is the symptom, not the fault.** The customer knows
what they observe, not what is wrong — the same distinction `MD-024` draws between `SYM-` and `FLT-`.

### 4.3 Steps

| # | Rule |
|---|---|
| **HS-04** | **One action per step.** A step containing "and" is usually two steps |
| **HS-05** | Steps are numbered. Sub-steps go one level deep only; a second level means the task should be split |
| **HS-06** | **Maximum nine steps.** More than nine and the article is two tasks (`HS-07`) or a video (`HC-020`) |
| **HS-07** | A task with a natural pause — waiting for approval, waiting for collection — is **two articles** linked in sequence, not one long one |
| **HS-08** | Every step names the **exact UI label** quoted from `UI-002`/`UI-003`, in the interface language | 
| **HS-09** | Steps describe **what the reader does**, never what the system does. System behaviour belongs in block 5 |
| **HS-10** | No step contains a warning; warnings go **before** the step they protect (`AU-06a` pattern) |
| **HS-11** | A step that can fail states the failure inline only if the recovery is one action; otherwise it goes to block 6 |

> **`HS-08` is what makes the whole set maintainable.** A label quoted from `UI-002` is a
> find-and-replace when the label changes. A label transcribed from a screenshot is a hunt through
> fifteen help sets — the same reasoning as `TR-003` `DS-16`.

### 4.4 "What happens next" — the block that is always missing

**`HS-12`: every task article states what happens after the last step.**

| Element | Example of what must be answerable |
|---|---|
| System response | Does anything visibly change? |
| Confirmation | Will they get a message? On which channel? |
| **Who else is told** | Does the technician know? The branch? |
| **Timing** | Immediately? Within a day? By the next working day? |
| What the reader should do now | Wait? Watch for something? Nothing? |

**Why this block matters more than the steps.** A customer who completed the steps and does not know
whether it worked **contacts support to check** — which is the exact contact `KPI-025` exists to
deflect. The steps prevent the first call; this block prevents the second.

**`HS-13`: timing is stated as an expectation, never as a promise.** *"Usually within one working
day"* is help. *"Within 24 hours"* is an SLA, and SLAs live in `LG-015` (`IA-15`).

### 4.5 Troubleshooting blocks

**`HS-14`: every row is symptom → cause → action, and the action is something the reader can do.**

| ❌ Common failure | ✅ Correct |
|---|---|
| "Error E-4021 — contact support" | "You see *Payment not confirmed*. Your bank may still be processing it. Wait 10 minutes and refresh. If it is still there after an hour, [contact us](…)" |
| Lists every possible error | Lists the five that actually occur, ranked by frequency |
| "Check your internet connection" as the first row for everything | Ranked by real frequency from `M27` disposition data |

**`HS-15`: troubleshooting content is ranked by observed frequency**, sourced from contact-centre
disposition data (`M27`) once it exists, and marked `provisional` before then.

**`HS-16`: a customer troubleshooting article never instructs a consumer to perform a
competence-gated hazardous procedure** (`IA-07`). It says what to do instead — stop using it,
isolate it, bring it in.

### 4.6 Screenshots — the nine-wave problem

Nine waves of UI change will orphan any article built on screenshots. `HS-17`…`HS-21` contain it,
mirroring `TR-003` `DS-12`…`DS-16` so that help and training age at the same rate.

| # | Rule |
|---|---|
| **HS-17** | **Teach the task and the decision, not the screen.** "Find your repair, open it, choose *Reschedule*" survives a redesign |
| **HS-18** | **Maximum one screenshot per article**, and only where the visual *is* the answer — a status colour, a warning state, a location that cannot be described |
| **HS-19** | Screenshots come from the **sandbox** (`TS-002`), never production. Sample data only, personal data redacted (`MM-002`) |
| **HS-20** | Every screenshot is registered with the release it was captured against and reviewed at each release (`TR-024` `RL-04`) |
| **HS-21** | Screenshots carry alt text in both languages — required by `CG-011`, and it is also what the search index reads |

**`HS-22`: an article that cannot be written without three screenshots is a video** (`HC-020`) **or a
task that is too complex and should be simplified in the product.** Say so as product feedback
rather than absorbing it into help.

### 4.7 Reading level and plain language

`CG-011` sets the reading-level target. For customer-facing help the practical rules:

| # | Rule |
|---|---|
| **HS-23** | Short sentences, one idea each. If a sentence needs a comma to hold two clauses, it is two sentences |
| **HS-24** | **No internal vocabulary.** The reader does not know what a *service order*, a *disposition*, an *entitlement* or a *rate card* is. `CG-004` gives the approved internal term; help gives the customer's word and, where the internal term is unavoidable, defines it once |
| **HS-25** | No unexplained acronyms; expand on first use per article, not per set |
| **HS-26** | Active voice, second person, present tense (`CG-003`) |
| **HS-27** | Numbers as digits; measurements and currency as `VB-009` sets them |
| **HS-28** | **No hedging that removes the answer.** "You may be able to…" tells the reader nothing. State the condition, then the answer |

> **`HS-24` is the rule most often broken by contributors who know the system well.** The words that
> feel precise internally — *entitlement*, *disposition*, *consignment* — are the words that make a
> customer close the page. The internal term stays in `CG-004` and in `UI-*`; help says what the
> customer would say.

### 4.8 Bilingual pairing

`CG-010` places 18 of 20 `HC` files bilingual, and for customer- and field-facing audiences Bengali
is the primary reading language.

| # | Rule |
|---|---|
| **HS-29** | Customer-, technician- and rider-facing help is **authored in Bengali** and rendered in English — not translated into Bengali (`LS-07`, `DS-17` pattern) |
| **HS-30** | Internal and partner-facing help (`P03`, `P05`, `P06`, `P08`) may be authored in English with in-context Bengali sign-off (`BN-018`) |
| **HS-31** | UI labels quoted in steps appear **in the language of the interface the reader is using** — a Bengali article quotes the Bengali label |
| **HS-32** | Codes, order numbers, model names, serials, IMEI and amounts are never translated |
| **HS-33** | Layout is designed for the **Bengali** length, 20–40% longer (`VB-007`) |
| **HS-34** | The two language versions are **one article with two renderings**, not two articles — they share an `HLP-` code, a version and a review date |

**`HS-35`: an article is not `Published` until both renderings exist**, for any audience where
`CG-010` requires bilingual. A half-published article sends the Bengali-reading customer to an
English page, which is worse than sending them to nothing.

### 4.9 Accessibility

| Requirement | Applied to help |
|---|---|
| Text alternatives | Every image and screenshot, both languages (`HS-21`) |
| Headings | Real heading structure, not bold text — screen readers and translation memory both depend on it |
| Link text | Describes the destination; never "click here" |
| Colour | Never the sole carrier of meaning |
| Contrast and size | Readable on a low-end Android in sunlight |
| **Page weight** | **Usable on 3G** (`IA-09`, `FR-KMS-022`) — this is an accessibility issue in this market, not a performance nicety |
| Tables | Used for data, not for layout |
| Reading level | `CG-011` target |

### 4.10 Review gates

**`HS-36`: four reviews, and the reviewer is never the author.**

| Gate | Reviewer | Checks |
|---|---|---|
| **1 — Editorial** | Content Design peer | Skeleton complete; steps; "what happens next"; reading level; `CG-004` terms |
| **2 — Domain** | The portal or process owner | Is it correct? Does it match the `SP`/`MD`/`UI` source? |
| **3 — Localisation** | Localisation Lead with a domain reviewer | Bengali authored not translated; terms per `BN-003`; layout for length |
| **4 — Accessibility** | Accessibility reviewer | `CG-011`, including page weight |
| **5 — Customer approval** *(customer-facing derivatives only)* | **Quality Manager + Customer Service Manager** | `BRU-KMS-11` |

### 4.11 Currency

| # | Rule |
|---|---|
| **HS-37** | Every article carries a version and the release it describes | 
| **HS-38** | A release that changes a task triggers review of its articles (`TR-024` `RL-04`) |
| **HS-39** | An article whose source `KNW-` article is superseded or retired is **flagged, not auto-changed** (`IA-06`, `BRU-KMS-11`) |
| **HS-40** | Review cadence: **6 months** for customer-facing, 12 months for internal and partner-facing |
| **HS-41** | An article with no measured use across two cycles is reviewed for retirement (`IA-20`) |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`HC-001_Help_Centre_Information_Architecture.md`](HC-001_Help_Centre_Information_Architecture.md) | Facets, object types, `IA-07`, `IA-10`, `IA-13`, `IA-15` |
| `_templates/TPL_Help_Article.md` | The skeleton this file explains |
| [`../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md`](../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md) · [`../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) · [`../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) | Voice, terms, accessibility |
| `UI-002`, `UI-003` | Quoted labels (`HS-08`) |
| `VB-009`, `BN-003`, `BN-018` | Bengali typography, terms, in-context sign-off |
| `MM-002` | Screenshot production spec |
| `TS-002` | Sandbox for screenshots (`HS-19`) |
| [`../08_Training_and_Enablement/08B_Course_Packs/TR-024_Release_Training_and_Refresher_Standard.md`](../08_Training_and_Enablement/08B_Course_Packs/TR-024_Release_Training_and_Refresher_Standard.md) | Release-triggered review (`HS-38`) |

| Depended on by |
|---|
| `HC-003`…`HC-016`, `HC-020` · `M32` corpus content shape · translation planning · help QA |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Annual**, and after the first help set is published — the first set will show what this standard got wrong |
| Trigger for out-of-cycle review | Helpfulness below target · translation rework above threshold · articles orphaned by a release (`HS-17`…`HS-21` failing) · an accessibility finding |
| Owner | Content Design |
| Change log | `RF-006` |
| Enforcement | `HS-01`…`HS-41`; the five review gates; `CG-008` Definition of Done |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`MM-002` is written** — Category 19 completed 2026-08-18 — and `HS-19`/`HS-21` now resolve to a real standard. **`MM-002` `SC-01` prohibits production capture without a waiver and `TS-002` still does not exist**, so the operative blocker moves to `O-02` and is unchanged in substance: no screenshot may lawfully be produced | Content Design | **W2 — superseded by `O-02`** |
| **O-02** | `TS-002` sandbox does not exist (Category 13 unstarted); `HS-19` prohibits production screenshots and provides no alternative source | Test Lead with Content Design | **W2 — blocking screenshots** |
| **O-03** | **`M27` disposition data does not exist pre-go-live**, so `HS-15` frequency ranking is unavailable for the first help sets. They must be marked `provisional` and re-ranked after six months of live data | Content Design with Contact Centre | W3 review |
| **O-04** | No accessibility reviewer is named for help content — the same gap `TR-003` `O-02` records for training. Gate 4 has no owner | Content Design Lead | **W2** |
| **O-05** | **Bengali authoring capability** (`HS-29`) requires domain-competent Bengali-native writers, the same constraint `TR-001` `O-05` and `KB-002` `O-05` record | Localisation Lead | **W2** |
| **O-06** | The page-weight budget for 3G usability (`HS-42` accessibility row) is not specified. "Usable on 3G" is unenforceable without a number | CTO with Content Design | W2 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — all six sections present, §7 added per category convention
- [x] Skeleton explained block by block, with the failure mode for each
- [x] Titles specified as reader-task, symptom-led for troubleshooting (`HS-02`, `HS-03`)
- [x] Step rules bound labels to `UI-002`/`UI-003` rather than to screenshots (`HS-08`)
- [x] **"What happens next" identified as the block that prevents the second contact**
- [x] Timing stated as expectation, never as an SLA promise (`HS-13`, `IA-15`)
- [x] Troubleshooting ranked by real frequency, with the consumer-hazard prohibition carried through (`HS-16`, `IA-07`)
- [x] Screenshot regime contains the nine-wave maintenance trap, aligned with `TR-003` `DS-12`…`DS-16`
- [x] Internal vocabulary prohibited in customer help (`HS-24`)
- [x] Bengali authored rather than translated, with both renderings a publication condition (`HS-29`, `HS-35`)
- [x] Page weight treated as an accessibility requirement in this market
- [x] Five review gates with reviewer ≠ author, including the `BRU-KMS-11` customer approval
- [x] All internal links resolve
- [x] `BRU-KMS-11` cited to `M61` §9; `FR-KMS-022` to `M61` §5.2
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-02` sandbox for screenshots — outstanding**
- [ ] **`O-05` Bengali authoring capability — outstanding**
- [ ] Named approver recorded — **pending Content Design Lead**
- [x] English-only, per `CG-010` §3.2 — template and style content

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
