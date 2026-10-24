---
id: CM-010
title: Town Hall and Roadshow Content
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Change Lead
author: Change Lead with Content Design and Brand
reviewers: [CEO, Operations Director, HR Director, Branch Operations Lead, L&D Lead, Localisation Lead, Content Design Lead, Brand, Programme Content Lead]
approver: Content Design Lead
content_class: D
purpose: >
  Supplies the spoken content for every all-staff town hall, divisional briefing and branch
  roadshow — one deck skeleton, four audience variants, a fixed question-handling method, and the
  rules that keep a live delivery inside the approved narrative. Field and branch staff will not
  read documents; they attend briefings, and a briefing is the one channel in the programme where
  the message is improvised in front of the audience unless something prevents it.
traces_to: [CM-001, CM-002, CM-003, CM-005, CM-008, CM-011, CM-018, 06-01, 00-04, TR-002, VB-002, CG-003, CG-011, BN-002, MM-003]
priority: P2
wave: W1
bilingual: yes
bn_counterpart: CM-010_Town_Hall_and_Roadshow_Content_BN.md
sources:
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §7 — monthly all-staff update, wave-specific briefings, visible executive sponsorship
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §1.2 RSK-009 — branch staff resistance mitigated by involving resistors in design and UAT, with visible executive sponsorship
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §5.3 — Steering monthly, Board quarterly; the governance rhythm town halls are scheduled against
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P02 non-negotiable requirement 3 — Bengali user interface, complete; the audience standard a briefing must match
    verified: 2026-08-20
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §21.5 — training volumes by group, including field technicians 200–400 delivered in Bengali in batches of 30
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §5 — demo discipline; every sprint review demonstrates working software to the business owner, never slides
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# CM-010 — Town Hall and Roadshow Content

> **Scope note.** This file owns **what is said aloud and how questions are handled**. It does not
> own the story (`CM-001`), the schedule (`CM-003`), the wave assets a roadshow distributes
> (`CM-005`), the objection answers (`CM-011`) or any training delivery (`TR-002`, `TR-023`).
> **A roadshow is not training.** §4.7 states the difference and why it matters.
>
> **Delivery note.** Every deck in this file is a **speaking aid**. `06-01` §5 sets the house
> position on slides in the strongest available terms — *"every sprint review demonstrates working
> software to the business owner, never slides."* `RD-06` carries that discipline into briefings.

---

## 1. Purpose

The register's justification is exact: *"Field and branch staff will not read documents; they
attend briefings."*

Across 51+ branches and 8 divisions, the spoken briefing is the only channel that reaches
technicians, counter staff, storekeepers and riders reliably, in their own language, with the
chance to ask. It is also the only channel with no draft, no editorial gate and no version
control — a person stands up and speaks. Everything in this file exists to close that gap.

**Consequence of absence (`CP-03`).**

| Failure | Consequence |
|---|---|
| No deck | Each speaker builds their own, and the programme has 51 stories |
| No audience variants | The technician briefing is the executive briefing with the numbers left in |
| No question method | The hardest question is answered by the least prepared person, live, and that answer becomes policy |
| No "I don't know" script | Speakers invent, and the invention is quoted back for months |
| No Bengali deck and speaker | The briefing that matters most is delivered in the language that reaches fewest of its audience |
| Slides in place of demonstration | Staff conclude the system does not exist yet |
| No record of what was asked | `CM-002` §4.7 resistance tracking has no input from its richest source |
| No executive presence | `RSK-009`'s mitigation — *"visible executive sponsorship"* — is unmet |

---

## 2. Scope

**In scope:** the four briefing types; the deck skeleton and its audience variants; the speaker
rules; the demonstration requirement; the question-handling method and its logging; the "I do not
know" script; language and interpreter rules; accessibility of delivery; the roadshow logistics
content; and rules `RD-01`…`RD-17`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| The narrative, claim schedule and prohibited claims | [`CM-001_Programme_Narrative_and_Change_Story.md`](CM-001_Programme_Narrative_and_Change_Story.md) |
| When briefings happen | [`CM-003_Communication_Calendar_by_Wave.md`](CM-003_Communication_Calendar_by_Wave.md) |
| The handouts distributed at a roadshow | [`CM-005_Wave_Launch_Communication_Kit.md`](CM-005_Wave_Launch_Communication_Kit.md) K1–K4 |
| Objections and their approved responses | [`CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md`](CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md) |
| Per-role change detail | [`CM-018_Change_Impact_Statement_Template.md`](CM-018_Change_Impact_Statement_Template.md) |
| Training courses, exercises and assessment | `TR-002`, `TR-007`…`TR-021` |
| Champion facilitation capability | `TR-023`; role boundary in [`CM-008_Champion_and_Super_User_Network_Kit.md`](CM-008_Champion_and_Super_User_Network_Kit.md) §4.2 |
| Slide visual design and diagram notation | `VB-004`, `MM-003` — **written 2026-08-18**; `MM-003` §4.7 sets the slide type floor and the one-diagram-per-slide rule |
| Bengali register and spoken conventions | `BN-002`, `BN-017` |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **CEO and executives** | Deliver the sponsorship briefing without a bespoke deck |
| **Change Lead** | Run a roadshow across 51+ sites with one set of content |
| **Branch managers (`S05`)** | Deliver a branch briefing they did not have to write |
| **Champions (`S06`)** | Support a session and take the questions afterwards |
| **Content Design** | Review a deck against a fixed skeleton |
| **Localisation Lead** | Supply a Bengali deck and confirm speaker capability |
| **L&D** | Keep the boundary between briefing and training intact |

---

## 4. Content

### 4.1 The four briefing types

**`RD-01`: four types, each with a defined purpose, length and speaker.** A session that does not
match one of these is not scheduled.

| # | Type | Audience | Length | Speaker | Frequency |
|:--:|---|---|---|---|---|
| **T1** | **All-staff town hall** | Everyone | 45 min: 20 speak, 25 questions | **CEO**, with the Change Lead | **Quarterly, plus one per wave gate** |
| **T2** | **Divisional briefing** | One of 8 divisions | 40 min: 20 speak, 20 questions | Division head with the Change Lead | Per wave affecting the division |
| **T3** | **Branch roadshow** | One site, all staff | 30 min: 12 speak, 18 questions | **Branch manager with the champion** | **T−3 weeks per site** |
| **T4** | **Toolbox talk** | Technicians and riders, at shift start | **10 min** | Supervisor | Fortnightly in W2 and W3 |

> **`RD-02` — questions get more time than speaking in every format.** A briefing where the
> speaker uses 40 of 45 minutes has not briefed anyone; it has broadcast in a room. The ratio is
> the design, not the aspiration.

> **`RD-03` — T1 is delivered by the CEO.** `RSK-009`'s mitigation names *"visible executive
> sponsorship"* explicitly. A programme town hall delivered only by the Change Lead communicates
> that the programme is a project, not a decision.

### 4.2 The deck skeleton

**`RD-04`: one skeleton, seven slides, four variants.** The skeleton never changes; the variant
changes what goes on each slide.

| # | Slide | Content rule | Never |
|:--:|---|---|---|
| **1** | **Why** | `CM-001` §4.1, in the speaker's own words | An org chart, a module map, a programme logo slide |
| **2** | **Where we are** | Wave, month, sites live — counted | A percentage without a denominator |
| **3** | **What arrives for you** | The audience's own change, from `CM-018` | Twenty features |
| **4** | **What does not change** | `NR-05` — **mandatory slide** | Omitted for time |
| **5** | **What we need from you** | One or two asks, named | A list of eight |
| **6** | **Where to get help** | `CM-005` K4 | A URL nobody can type |
| **7** | **Your questions** | Blank; the slide is a prompt to stop talking | Content |

### 4.3 The four audience variants

| Variant | For | Slide 3 says | Slide 5 asks | Tone |
|---|---|---|---|---|
| **V-EXEC** | `S01`, `S02`, division heads | Capability, gate position, benefit tracking | Protect super-user time (`RSK-001`); take the open decisions | Numbers, decisions |
| **V-OFFICE** | Head office, finance, HR, commercial | Process and control change | Attend UAT; capture the baseline before your wave | Process |
| **V-BRANCH** | `S08`–`S09` counter, workshop, store | The screen, the token, the count, the drawer | Attend training; use your champion | **Concrete, task-level** |
| **V-FIELD** | `S07`, `S10` technicians and riders | **The phone.** The job, the parts, the photo, the signature, the earnings | Join the pilot; bring the device to training | **Bengali, spoken, short, demonstrated** |

> **`RD-05` — V-FIELD is delivered in Bengali by a Bengali speaker, or it is not delivered.** It
> is the variant reaching the population whose refusal is `RSK-008`, a Critical risk. An
> interpreter is acceptable; an English deck read aloud is not.

### 4.4 Demonstration, not description

**`RD-06`: from W1 onward, every V-BRANCH and V-FIELD session includes a live demonstration of a
real task on a real device.** Slide 3 is spoken over the demonstration, not instead of it.

| Variant | Demonstration | Duration |
|---|---|---|
| V-BRANCH | One walk-in intake, start to token print | 3 min |
| V-FIELD | **One job on a phone**, including a photo and a signature, **with the network switched off** | 4 min |
| V-OFFICE | One approval or one invoice from a closed job | 3 min |
| V-EXEC | One dashboard, drilled from group to a single job | 2 min |

> **`RD-07` — the offline demonstration is the single most persuasive thing available to this
> programme with field staff.** `P02`'s first non-negotiable requirement is 24 hours of offline
> operation with no data loss. Showing it, on a phone in aeroplane mode, answers the objection
> before it is raised. Where the capability is not yet built, **the demonstration is not faked** —
> the speaker says it is not built yet and gives the wave.

### 4.5 Question handling

**`RD-08`: every question is answered, deferred with a date, or escalated. There is no fourth
option.**

| Question type | Response | Owner |
|---|---|---|
| Answerable from `CM-001` or `CM-011` | Answer, in the approved form | Speaker |
| Answerable but not by this speaker | *"[Name] owns that. I will have an answer to you by [date]."* | Speaker logs; Change Lead answers within **3 working days** |
| **About pay, grading, headcount or appraisal** | *"That is an HR matter, not a programme matter. [HR name] will respond."* — **and it is genuinely routed** | HR Director |
| An `Interest` objection (`SK-15`) | Acknowledged honestly; **not argued with**; escalated | Change Lead → Steering |
| Hostile or personal | Taken offline, respectfully, immediately | Speaker with the branch manager |
| **Unknown** | **The `RD-09` script** | Speaker |

**`RD-09` — the script for what you do not know**, learned verbatim by every speaker:

> *"I don't know. I'm not going to guess, because a wrong answer here costs more than a slow one.
> I'll find out and [name] will come back to you by [date]."*

**`RD-10`: every question asked is logged**, with the site, the date, the audience group and
whether it was answered. The log feeds `CM-005` `V6` top-ten questions, `CM-009` section 3, and
`CM-002` §4.7 resistance tracking. **A roadshow that logs no questions did not happen as
designed.**

### 4.6 Language and delivery

| # | Rule |
|---|---|
| **`RD-11`** | **V-BRANCH and V-FIELD are delivered in Bengali.** The deck exists in both languages; the delivery is in the audience's language |
| **`RD-12`** | Where a speaker cannot deliver in Bengali, a **named interpreter** is arranged in advance — never a colleague volunteered on the day |
| **`RD-13`** | Questions are taken **in whichever language the questioner uses**, and answered in that language |
| **`RD-14`** | Technical terms follow `BN-003`; where no approved Bengali term exists, the English term is used untranslated (`BN-004`) rather than coined live |
| **`RD-15`** | Sessions are held **on shift, on paid time, at the site** — never as an after-hours voluntary event. A briefing staff must attend unpaid is a briefing about how the programme values them |
| **`RD-16`** | Slides meet `CG-011` — minimum 24 pt on screen, 4.5:1 contrast, no meaning carried by colour alone, no text smaller than the back row can read |
| **`RD-17`** | T1 and T2 sessions are **recorded and made available**, with the Bengali track, for staff on shift |

### 4.7 Briefing is not training

**`RD-18` (recorded in §4.9): a briefing tells people what is changing; training teaches them to
do it.** The distinction matters because attendance at one is routinely recorded as satisfying the
other.

| | Briefing (this file) | Training (`TR-002`, `TR-007`…`TR-021`) |
|---|---|---|
| Purpose | Understand what and why | Be able to do it |
| Length | 10–45 minutes | Hours to days |
| Assessment | None | **Required** (`TR-004`) |
| Gates access | **No** | **Yes** — training precedes access |
| Delivered by | Manager, champion, executive | Certified trainer |
| Evidence | Attendance, questions logged | Assessment result in `M22` |

> **A branch that has been briefed is not a branch that has been trained**, and `CM-012` readiness
> counts them separately for exactly this reason.

### 4.8 Roadshow logistics content

For 51+ sites the logistics are content, because they are what a branch manager must arrange.

| Item | Rule |
|---|---|
| Notice to the site | **10 working days**, so cover can be arranged |
| Session count per site | Enough that **every shift is covered** — typically two |
| Room and equipment | A screen or a large phone-mirroring device; branch hardware is 1366×768 (`04-00` §P03) |
| **Handouts** | `CM-005` K1, K3, K4 — in Bengali, one per person, **counted before the session** |
| Attendance record | Name, role, shift — feeds `CM-012` readiness |
| Question log | Completed by the champion during the session, submitted same day |
| Accessibility | Seating with sightlines; the deck available on paper for anyone who needs it close |
| Cover | **Arranged by the branch manager before the session is confirmed**, not on the day |

### 4.9 Governing rules

| # | Rule | Class |
|---|---|:--:|
| `RD-01` | Four briefing types; a session outside them is not scheduled | **H** |
| `RD-02` | Questions receive more time than speaking, in every format | **H** |
| `RD-03` | The all-staff town hall is delivered by the CEO | **H** |
| `RD-04` | One seven-slide skeleton, four variants; the skeleton does not change | **H** |
| `RD-05` | V-FIELD is delivered in Bengali by a Bengali speaker or interpreter | **H** |
| `RD-06` | V-BRANCH and V-FIELD include a live demonstration on a real device | **H** |
| `RD-07` | A capability not yet built is never demonstrated as if it were; the wave is stated instead | **H** |
| `RD-08` | Every question is answered, deferred with a date, or escalated | **H** |
| `RD-09` | The "I don't know" script is learned verbatim and used | **H** |
| `RD-10` | Every question is logged with site, date and audience group | **H** |
| `RD-11` | Branch and field sessions are delivered in Bengali | **H** |
| `RD-12` | Interpreters are named and arranged in advance | **H** |
| `RD-13` | Questions are answered in the language they were asked in | **H** |
| `RD-14` | Terminology from `BN-003`; no live coinage | **H** |
| `RD-15` | Sessions are on shift, on paid time, at the site | **H** |
| `RD-16` | Slides meet `CG-011` legibility and contrast minimums | **H** |
| `RD-17` | Town halls and divisional briefings are recorded, with the Bengali track | **S** |
| `RD-18` | A briefing is not training and never satisfies a training prerequisite | **H** |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`CM-001_Programme_Narrative_and_Change_Story.md`](CM-001_Programme_Narrative_and_Change_Story.md) | Slides 1 and 4; the claim and vocabulary discipline |
| [`CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md`](CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md) | The approved responses `RD-08` draws on |
| [`CM-018_Change_Impact_Statement_Template.md`](CM-018_Change_Impact_Statement_Template.md) | Slide 3 content per audience |
| [`CM-005_Wave_Launch_Communication_Kit.md`](CM-005_Wave_Launch_Communication_Kit.md) | K1, K3, K4 handouts; K5 is the manager's version of this content |
| [`CM-008_Champion_and_Super_User_Network_Kit.md`](CM-008_Champion_and_Super_User_Network_Kit.md) | The champion who co-delivers T3 and logs the questions |
| [`CM-012_Branch_Readiness_Communication_Checklist.md`](CM-012_Branch_Readiness_Communication_Checklist.md) | Attendance feeds readiness; `RD-18` keeps briefing and training separate there |
| `06-01` §5, §7 | Demo discipline and the executive-sponsorship requirement |
| `04-00` §P02 | The offline capability `RD-07` demonstrates |
| `BN-002`, `BN-003`, `BN-004`, `BN-017` | Spoken register, terminology, do-not-translate list |
| `CG-011` · `VB-004` · `MM-003` | Accessibility, slide design, diagram notation — **`MM-003` written 2026-08-18**; `DG-33` prohibits shrinking a diagram below its type floor to fit a slide |

| Depended on by |
|---|
| Every wave's site roadshows across 51+ branches · `CM-009` section 3 question source · `CM-002` §4.7 resistance input · `CM-005` `V6` top-ten questions · `RSK-009` mitigation evidence |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Every wave boundary**; variants refreshed from the previous wave's question log |
| Trigger for out-of-cycle review | A demonstration that cannot be performed · a repeated unanswerable question · an accessibility finding · a change to `CM-001` §4.1 or §4.3 |
| Owner | Change Lead; V-EXEC co-owned with the Programme Office |
| Change log | `RF-006`; a skeleton change is MAJOR and re-translates all four variants |
| Enforcement | `RD-01`…`RD-18`; question logs reconciled monthly; a session with no log is treated as not held |
| Improvement loop | **The same question appearing at more than three sites means slide 3 or 4 is wrong**, not that staff are inattentive. The deck is corrected before the next site |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **The demonstration in `RD-06` requires a stable demonstration environment and data.** `TS-002` specifies a test data pack and persona set; BRD §21.5 names a dedicated `training` environment with curated scenario data. Neither is confirmed as available for roadshow use, and demonstrating on production at a branch is not acceptable | CTO with L&D | **W1 minus 4 weeks** |
| **`O-02`** | **Roadshow delivery across 51+ sites is unresourced.** T3 is 30 minutes, twice per site, at T−3 weeks, for every wave that touches the site. `06-01` §4 budgets 0.5–1.0 FTE of a Change & Training Lead. The arithmetic does not close without branch managers and champions delivering it — which is the design, and which depends on `CM-008` `O-01` | Change Lead with Operations Director | **W1 minus 6 weeks** |
| **`O-03`** | **The Bengali counterpart does not exist**, and `RD-05` and `RD-11` make Bengali delivery mandatory for the two variants reaching the largest and highest-risk audiences | Localisation Lead | **W1 minus 4 weeks** |
| **`O-04`** | **The CEO commitment in `RD-03` is 4 hours per month of steering** (`06-01` §4), which does not obviously include quarterly town halls plus one per gate — thirteen wave-gate town halls plus twelve quarterly sessions over 36 months. The commitment has not been confirmed | CEO with Programme Director | **W0** |
| **`O-05`** | **No question log system exists.** `RD-10` makes the log the input to three other files, and `CM-002` `O-05` records the same absence for the communication log generally | Change Lead with PMO | **W1** |
| **`O-06`** | **`RD-15` requires sessions on paid time with cover arranged.** For 51+ branches at two sessions per wave, this is a real operational cost that appears in no plan, and a branch that cannot arrange cover will hold the session after hours or not at all | Operations Director with HR Director | **W1** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §7 Open Items added per category convention
- [x] Category-standard audience · channel · timing · message · call-to-action table present (`CG-009` §3) — expressed as §4.8 logistics and the four-type table in §4.1
- [x] Four briefing types with speaker, length and frequency; questions given more time than speaking
- [x] **CEO delivery of the town hall bound to the `RSK-009` mitigation**
- [x] One seven-slide skeleton with four audience variants and a mandatory "what does not change" slide
- [x] **Live demonstration required, including the offline demonstration for field audiences, with an explicit prohibition on faking unbuilt capability**
- [x] Question handling defined with three outcomes and a verbatim "I don't know" script
- [x] Question logging made the input to three downstream files
- [x] Bengali delivery, interpreter and terminology rules stated
- [x] **Briefing distinguished from training**, with the access-gating consequence made explicit
- [x] Eighteen governing rules with enforcement classes
- [x] All internal links resolve
- [ ] **`O-01` no confirmed demonstration environment or data**
- [ ] **`O-02` roadshow delivery across 51+ sites unresourced**
- [ ] **`O-03` Bengali counterpart not written; two variants require Bengali delivery**
- [ ] **`O-04` CEO town-hall commitment unconfirmed**
- [ ] **`O-05` no question log system**
- [ ] Named approver recorded — **pending Content Design Lead**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
