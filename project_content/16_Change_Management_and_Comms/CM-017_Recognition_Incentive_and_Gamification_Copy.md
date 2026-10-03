---
id: CM-017
title: Recognition, Incentive and Gamification Copy
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Change Lead with HR
author: Change Lead with the HR Director and Content Design
reviewers: [HR Director, CFO, Operations Director, COO, Chief Data Officer or delegate, Legal & Compliance, L&D Lead, Localisation Lead, Content Design Lead, Programme Content Lead]
approver: Content Design Lead, with the HR Director approving every recognition and incentive statement
content_class: D
purpose: >
  Supplies the copy that acknowledges adoption and performance — milestone messages, scorecard
  and incentive-visibility wording, recognition announcements and champion acknowledgements — and
  states the boundaries that keep it lawful and honest, including the M57 rule that no employee
  sees another employee's individual score. Behaviour change in a 500-person workforce responds
  to recognition more reliably than to mandate, and recognition copy written without the
  monitoring and privacy boundaries is the fastest route from motivation to grievance.
traces_to: [M57, M56, M21, M55, M22, CM-001, CM-002, CM-008, CM-009, CM-011, CM-016, TR-004, LG-020, MD-009, 05-04, 00-04]
priority: P3
wave: W2
bilingual: yes
bn_counterpart: CM-017_Recognition_Incentive_and_Gamification_Copy_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M57 §9 BRU-PIC-16 — peer comparison is anonymised; no employee sees another employee's individual score. Class H, owned by the CDO
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M57 §9 BRU-PIC-06 — the employee can see every job and event contributing to their KPI values. Class H
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M57 §9 BRU-PIC-03, BRU-PIC-04, BRU-PIC-05 — incentive calculated from operational facts only; every technician scorecard pairs a volume measure with at least one quality measure; a quality gate below threshold reduces or eliminates the volume component
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M57 §9 BRU-PIC-14 — performance ratings, reviews and PIPs are sensitivity class S2, visible to employee, manager chain and HR only
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M57 §5.4 and §3.2 — M57 calculates; M56 pays; M21 records the approved salary change; M57 never initiates payment (SOD-30, BRU-PIC-09)
    verified: 2026-08-20
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §21.5 — incentive visibility as an immediate personal benefit, named as a mitigation for the Critical technician-adoption risk
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# CM-017 — Recognition, Incentive and Gamification Copy

> **Scope note.** This file owns **wording**. It does not own the incentive scheme (`M57` and HR),
> the calculation (`M57`), the payment (`M56`), the salary of record (`M21`), the competency
> framework (`M22`, `TR-004`) or any performance policy. **A copy file cannot create an
> entitlement**, and `RN-01` says so in the strongest terms available.
>
> **Constraint note — read before writing any leaderboard.** `M57` `BRU-PIC-16` is a **Class H
> hard block**: *"peer comparison is anonymised; no employee sees another employee's individual
> score."* Several conventional gamification patterns — a named ranking, a top-ten board, a public
> percentile — **breach it**. §4.5 states what is permitted instead.

---

## 1. Purpose

The register's justification is exact: *"Behaviour change in a 500-person workforce responds to
recognition more reliably than to mandate."*

The BRD makes the same point in a harder form: for the population that decides `RSK-008`, a
Critical risk, the named mitigation is *"earnings and incentive visibility as an immediate
personal benefit."* Not a poster. Not a message. The technician seeing their own money accumulate
on the same screen that asks them to record the work.

**Consequence of absence (`CP-03`).**

| Failure | Consequence |
|---|---|
| No recognition copy | Adoption is driven by instruction alone, and instruction produces compliance, not use |
| Recognition written without the `M57` boundaries | A leaderboard is published that breaches a Class H rule and has to be withdrawn |
| Incentive copy written by the programme | The programme appears to be making a pay commitment it cannot make |
| Scorecard wording without the evidence link | A number a technician cannot trace is a number they dispute |
| Champion recognition unspecified | The most-relied-upon volunteers in the programme are thanked generically or not at all |
| Milestone copy tied to volume alone | The system rewards throughput and quality falls — which `BRU-PIC-04` exists to prevent |
| English-only | The audience that most needs incentive visibility is Bengali-first |
| No withdrawal rule | A recognition mechanic that stops working continues running |

---

## 2. Scope

**In scope:** the four recognition surfaces; the `M57` boundaries expressed as copy rules; scorecard
and incentive-visibility wording; milestone and streak copy; champion and team recognition; the
anonymised-comparison patterns that are permitted; the prohibited patterns; the monitoring
boundary; and rules `RN-01`…`RN-18`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| The incentive scheme, its measures, weights and thresholds | `M57` §5.4; HR Director and CFO (`BRU-PIC-01`) |
| Incentive calculation | `M57` |
| Incentive payment, taxation, disbursement | `M56` — `M57` publishes an amount and never initiates payment (`BRU-PIC-09`, `SOD-30`) |
| Salary structure and contract amendment | `M21` |
| Attendance and overtime | `M55` |
| Competency, certification and assessment | `M22`; `TR-004` |
| Customer loyalty points and rewards | `M10` — **employee recognition and customer loyalty are different systems and never share copy** |
| Adoption measurement and campaigns | [`CM-016_Adoption_Campaign_Content.md`](CM-016_Adoption_Campaign_Content.md) |
| Champion role and network health | [`CM-008_Champion_and_Super_User_Network_Kit.md`](CM-008_Champion_and_Super_User_Network_Kit.md) §4.8 |
| In-product microcopy and UI strings | `UI-*`; Bengali in `BN-*` |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Change Lead** | Write recognition that does not create an obligation |
| **HR Director** | Approve every statement that touches pay or performance |
| **L&D** | Recognise certification without implying a pay consequence |
| **Content Design** | Review recognition copy against the `M57` boundaries |
| **Portal squads** | Take scorecard and incentive-visibility wording that is already cleared |
| **Branch managers** | Recognise their own people in the same terms the programme uses |
| **Localisation Lead** | Translate copy that will be quoted back in a pay conversation |

---

## 4. Content

### 4.1 The four surfaces

**`RN-02`: recognition lives on four surfaces and nowhere else.** A fifth surface is a new
mechanic and requires HR approval, not a copy decision.

| # | Surface | Reaches | Owner of the mechanic | Owner of the copy |
|:--:|---|---|---|---|
| **S1** | **The person's own scorecard and earnings view** (`FR-PIC-012`) | Individual, private | `M57` | This file |
| **S2** | **Milestone and progress messages** in the product | Individual, private | Portal squad | This file |
| **S3** | **Named public recognition** — forum, newsletter, site notice | Everyone | Change Lead / HR | This file, with `CM-009` §4.1 section 5 |
| **S4** | **Team and site recognition** — branch, workshop, zone | Everyone | Change Lead | This file |

> **`RN-03` — S1 and S2 are private; S3 and S4 are public and are the only ones that name a
> person.** S3 names a person for something they **did**, never for where they **ranked**. That
> distinction is what keeps S3 outside `BRU-PIC-16`.

### 4.2 What copy may not do

| # | Rule |
|---|---|
| **`RN-01`** | **Recognition copy never creates or implies an entitlement.** No message states, implies or estimates a payment, a bonus, a grade or a promotion. `M57` calculates and `M56` pays; a communication does neither |
| **`RN-04`** | No copy states an incentive figure other than **the person's own, sourced from `M57`** |
| **`RN-05`** | No copy compares a named person to another named person (`BRU-PIC-16`) |
| **`RN-06`** | No copy reproduces a rating, review outcome or PIP status — those are sensitivity class `S2` (`BRU-PIC-14`) |
| **`RN-07`** | No copy attaches recognition to a **volume measure alone** (`BRU-PIC-04`) |
| **`RN-08`** | **No individual leaderboard is published**, on any surface, in any language |
| **`RN-09`** | No adoption metric is used to name an individual negatively, ever (`NL-09`) |
| **`RN-10`** | Recognition copy for customers and recognition copy for employees are never shared or adapted between systems |

### 4.3 S1 — scorecard and earnings visibility

The single highest-value copy in this file, because it is the `RSK-008` mitigation.

| Element | Copy rule | Why |
|---|---|---|
| **Framing** | *"Your work this month"* — the person's, not the company's | `FR-PIC-012` presents the employee their own scorecard |
| **Traceability** | Every value is a link: *"12 jobs — see them"* | **`BRU-PIC-06`**: the employee can see every job and event contributing to their KPI values |
| **Quality alongside volume** | Volume and quality shown **together, never volume alone** | `BRU-PIC-04` |
| **Quality gate** | Where a quality threshold reduces the volume component, the copy says so **before** the period closes, not after | `BRU-PIC-05` |
| **Accrual** | *"Accruing — this period is not final"* on every in-period figure | `BRU-PIC-08`: a published period is immutable; an in-period figure is not a published one |
| **Dispute** | *"Something look wrong? Raise it — you will get an answer with the evidence."* | `BRU-PIC-12` requires a dispute answered with evidence within the review window |
| **Adjustment** | A manual adjustment is **shown with its reason** | `BRU-PIC-10` |
| **Clawback** | Notified **before** it is applied, with the evidence | `BRU-PIC-11` |
| **Language** | **Bengali-first for `R10`–`R12`, `R16`, `R08`, `R18`, `R29`** | `CG-010` §3.3 |

> **`RN-11` — the word "estimated" never appears next to money.** An in-period figure is
> *accruing*; a closed figure is *final*. "Estimated" invites the reading that the final figure is
> negotiable, which it is not (`BRU-PIC-08`).

### 4.4 S2 — milestone and progress copy

Private, in-product, individual. **`RN-12`: a milestone marks a behaviour that the programme
genuinely wants repeated, and each one is retired when it is universal.**

| Milestone | Copy pattern | Retired when |
|---|---|---|
| First job completed in the app | *"First job recorded. Everything you entered is already with dispatch."* | After the person's first week |
| First offline job synced | *"You worked with no signal and nothing was lost."* | After first occurrence |
| First estimate approved on site | *"Approved on site — the customer did not have to wait for a call."* | After first occurrence |
| Evidence complete on ten consecutive jobs | *"Ten jobs with complete evidence. That is what gets a warranty claim paid."* | **When the site average passes the threshold** |
| Certification achieved (`M22`) | *"[Certification] recorded. You can now be assigned [work type]."* | Never — this is a capability fact |
| First month with the scorecard | *"Your first full month is visible, job by job."* | After first occurrence |

> **`RN-13` — a milestone that everyone has achieved is noise and is withdrawn.** A recognition
> mechanic left running past its usefulness trains people to ignore the channel it runs on.

### 4.5 The permitted comparison patterns

`BRU-PIC-16` blocks individual peer comparison. What remains, and what it is good for:

| Pattern | Permitted? | Form |
|---|:--:|---|
| Named individual ranking | **No** | — |
| Top-ten board with names | **No** | — |
| *"You are 4th of 22"* | **No** — this is an individual peer comparison | — |
| **Own trend over time** | **Yes** | *"Your first-time fix rate is up from 71% to 78% since March."* |
| **Own position against an anonymised distribution** | **Yes** — `BRU-PIC-16` requires anonymisation, not absence | *"Your turnaround time is in the fastest third of technicians on your device category."* |
| **Own position against a target** | **Yes** | *"Target is 95% evidence completeness. You are at 91%."* |
| **Team, site or zone comparison** | **Yes** | *"Mirpur branch: 96% intake within 3 minutes."* — sites are compared in `P06`'s branch league by design |
| Manager's view of their own team | **Yes**, to the manager only | `FR-PIC-013`; `BRU-PIC-14` scope |

> **`RN-14` — team recognition is the substitute for individual ranking, and it is a better one
> here.** The behaviours this programme needs — complete evidence, accurate counts, timely
> closure — are collective at a branch. A site-level board is permitted, motivating, and does not
> touch `BRU-PIC-16`.

### 4.6 S3 — named public recognition

| Element | Rule |
|---|---|
| **Basis** | **What the person did**, described specifically. Never a rank, a score or a percentile |
| Approval | **HR Director**, for every instance |
| Consent | The person is asked before they are named publicly |
| Channels | Champion forum · `CM-009` section 5 · site notice · wave exit notice |
| Frequency | Enough that it is not rare; not so much that it is routine |
| **Spread** | Across sites and roles. Recognition concentrated in one branch reads as favouritism and demotivates the rest |
| Prohibited | Naming a person in connection with an adoption *metric* (`RN-09`) |
| Language | The person's own language, and both where it is published widely |

**`RN-15`: champion recognition is a standing category.** `CM-008` §4.8 sets the forms; this file
sets the words. The wording states **what the champion did for their colleagues**, not how many
questions they answered.

### 4.7 The monitoring boundary

Recognition copy and monitoring copy sit adjacent to each other and are read together by the
audience most sensitive to both.

| Rule | Detail |
|---|---|
| **`RN-16`** | Recognition copy never references data the person has not been told is collected. `CM-011` `OJ-11` requires a written disclosure of what the technician app records; **recognition that surfaces an unmentioned data point discloses the collection by accident** |
| **`RN-17`** | No recognition is derived from location, movement or timing data unless that use is in the `OJ-11` disclosure |
| **`RN-18`** | A recognition mechanic proposed after the disclosure is issued requires the disclosure to be updated **before** the mechanic runs |

> **This is not a theoretical constraint.** `P02` records GPS, geofenced clock-in, time tracking
> and automatic arrival detection. A message reading *"you arrived on site within 5 minutes of
> your ETA on every job this week"* is recognition built from movement data, and if the disclosure
> did not say that was being used to assess performance, the message is the disclosure.

### 4.8 Audience · channel · timing · message · call-to-action

| Audience | Channel | Timing | Message | Call to action |
|---|---|---|---|---|
| `R10`–`R12` technicians | **In-app, private, BN** | Daily, in-period | S1 scorecard and accruing earnings, job by job | Check your jobs; raise anything wrong |
| `R08`, `R18`, `R29` branch roles | In-app, private, BN | Per shift or period | S1 own measures against target | — |
| Any individual | In-app, private | On the event | S2 milestone | None |
| All staff | `CM-009` section 5, forum, site notice | Monthly | S3 named recognition, with consent | None |
| A site or team | Site notice, forum, `P06` branch view | Monthly | S4 team and site achievement | — |
| Champions | **Champion forum** | **Monthly** | S3 champion recognition, specific | — |
| Managers | Manager view (`FR-PIC-013`) | Per period | Their team's distribution and outliers | Coach; do not publish |
| HR Director | Approval queue | Per instance | Every S1, S3 wording | Approve, amend or refuse |

### 4.9 Governing rules

| # | Rule | Class |
|---|---|:--:|
| `RN-01` | Recognition copy never creates or implies an entitlement | **H** |
| `RN-02` | Recognition lives on four surfaces; a fifth requires HR approval | **H** |
| `RN-03` | S1 and S2 are private; only S3 and S4 are public, and S3 names a deed, not a rank | **H** |
| `RN-04` | No copy states an incentive figure other than the person's own, sourced from `M57` | **H** |
| `RN-05` | No copy compares a named person to another named person (`BRU-PIC-16`) | **H** |
| `RN-06` | No copy reproduces a rating, review outcome or PIP status (`BRU-PIC-14`) | **H** |
| `RN-07` | Recognition never attaches to a volume measure alone (`BRU-PIC-04`) | **H** |
| `RN-08` | **No individual leaderboard, on any surface, in any language** | **H** |
| `RN-09` | No adoption metric names an individual negatively | **H** |
| `RN-10` | Employee recognition and customer loyalty copy are never shared between systems | **H** |
| `RN-11` | In-period figures are "accruing"; closed figures are "final"; "estimated" is never used of money | **H** |
| `RN-12` | Every milestone marks a behaviour worth repeating and carries a retirement condition | **H** |
| `RN-13` | A universally achieved milestone is withdrawn | **S** |
| `RN-14` | Team and site comparison substitutes for individual ranking | **H** |
| `RN-15` | Champion recognition is a standing category worded on what they did for colleagues | **H** |
| `RN-16` | Recognition never references data the person has not been told is collected | **H** |
| `RN-17` | No recognition derives from location, movement or timing data outside the `OJ-11` disclosure | **H** |
| `RN-18` | A new mechanic requires the disclosure updated before it runs | **H** |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `M57` §5.2, §5.4, §9 | The scorecard, the incentive engine, and `BRU-PIC-03`…`BRU-PIC-16`, which set every boundary in this file |
| `M57` `FR-PIC-012`, `FR-PIC-013`, `FR-PIC-041` | Employee-visible scorecard, manager team view, non-monetary recognition |
| `M56`, `M21`, `M55`, `M22` | Payment, salary of record, attendance, competency — the four things this copy must not appear to decide |
| [`CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md`](CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md) `OJ-11` | The monitoring disclosure `RN-16`…`RN-18` depend on |
| [`CM-008_Champion_and_Super_User_Network_Kit.md`](CM-008_Champion_and_Super_User_Network_Kit.md) §4.8 | The champion recognition forms this file words |
| [`CM-009_Internal_Newsletter_and_Update_Template.md`](CM-009_Internal_Newsletter_and_Update_Template.md) §4.1 | Section 5 is the standing S3 channel |
| [`CM-016_Adoption_Campaign_Content.md`](CM-016_Adoption_Campaign_Content.md) | Adoption measurement, and the `RN-09` prohibition on using it against a person |
| `LG-020` | Employee-facing privacy position |
| `05-04` §1 · `MD-009` | The roles S1 copy is written for |
| `UI-*`, `BN-*` | Where this copy is implemented as product strings |

| Depended on by |
|---|
| `P02` earnings and scorecard screens · `CM-009` section 5 · the champion forum · `CM-007` exit notice thanks · `RSK-008` mitigation evidence |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Every wave boundary**, and whenever `M57` scheme versions change (`BRU-PIC-02`) |
| Trigger for out-of-cycle review | A scheme change · a `BRU-PIC` rule change · a monitoring-disclosure change · a milestone reaching universality |
| Owner | Change Lead; **every instance approved by the HR Director** |
| Change log | `RF-006`; changes to S1 wording are MAJOR because they are quoted in pay conversations |
| Enforcement | `RN-01`…`RN-18`; HR approval gate on every instance; Content Design checks §4.2 before publication |
| Improvement loop | **Dispute volume on the scorecard is this file's KPI.** Rising disputes with stable data means the wording is unclear, not that employees are unreasonable — `BRU-PIC-06` traceability is what the copy must be making visible |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **The incentive scheme does not exist yet.** `BRU-PIC-01` blocks calculation until a scheme version is approved by the HR Director and CFO; `M57` and `M21` land at **W5**, while this file is registered `W2` and the `RSK-008` mitigation it serves is needed at **W2**. **Incentive visibility — the named mitigation for a Critical risk — is three waves later than the risk.** This is the wave-sequencing defect recorded across four prior categories (`AUDIT-014` TS-02), appearing here in its most consequential form | HR Director with CFO and the PMO | **W2 — the risk date, not the module date** |
| **`O-02`** | **The monitoring disclosure exists but its central question is unanswered** (`CM-011` `O-02`). `LG-020` §4.6 discloses continuous location tracking; its gate question `AU2` — whether that tracking is lawful and proportionate, and whether it must stop outside shift hours — is open and `LG-020` `O-02` records it as **blocking `P02` go-live disclosure**. `RN-16`…`RN-18` make the disclosure a precondition for recognition derived from app data, so **until `AU2` is answered, S1 and S2 copy is limited to job and quality facts the technician records themselves** | Legal Counsel with the HR Director | **W2 minus 2 months** |
| **`O-03`** | **`RN-08` will be contested.** A named leaderboard is the most requested gamification pattern and it is prohibited by a Class H rule owned by the CDO. This file records the prohibition and the permitted alternatives so that the request is answered once with a rule rather than repeatedly with an opinion. **No `M57` waiver route exists for `BRU-PIC-16`** | Chief Data Officer (or delegate under `D-15`) with HR Director | **Recorded; enforced from W2** |
| **`O-04`** | **The Bengali counterpart does not exist**, and S1 is Bengali-first for 200–400 technicians plus 51+ cashiers and storekeepers. Copy about someone's money, in a language they do not read fluently, is the worst possible combination | Localisation Lead | **W2 minus 6 weeks** |
| **`O-05`** | **`D-15` significant-data-fiduciary classification is open**, so the Chief Data Officer role that owns `BRU-PIC-16` and `BRU-PIC-14` may not be filled. The approval route for §4.5 and §4.7 currently terminates in an unappointed role | CEO with Legal | **W4 minus 3 months** |
| **`O-06`** | **The interim recognition period is unaddressed.** From W1 to W5 there is no scorecard and no incentive engine, but there is a workforce being asked to change. §4.6 S3 and §4.5 S4 are the only surfaces available in that window, and neither has a budget or an owner beyond the Change Lead | Change Lead with HR Director | **W1** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §7 Open Items added per category convention
- [x] Category-standard audience · channel · timing · message · call-to-action table present (`CG-009` §3)
- [x] Four recognition surfaces defined, with private and public separated
- [x] **Every copy boundary traced to a named `M57` business rule**, not asserted
- [x] **`BRU-PIC-16` identified as blocking individual leaderboards, with the permitted anonymised and team patterns supplied in their place**
- [x] Scorecard and earnings copy bound to `BRU-PIC-06` traceability, `BRU-PIC-04` quality pairing and `BRU-PIC-08` immutability
- [x] Milestone copy carries a retirement condition
- [x] Named public recognition based on deeds, consented, HR-approved and spread across sites
- [x] **Monitoring boundary stated**, tying recognition to the `CM-011` `OJ-11` disclosure
- [x] Eighteen governing rules with enforcement classes
- [x] All internal links resolve
- [ ] **`O-01` the incentive scheme lands at W5 while the risk it mitigates is at W2**
- [ ] **`O-02` monitoring disclosure does not exist; S1 and S2 copy is constrained until it does**
- [ ] **`O-04` Bengali counterpart not written**
- [ ] **`O-05` the CDO approval route terminates in an unappointed role**
- [ ] **`O-06` no recognition mechanism exists between W1 and W5**
- [ ] Named approver recorded — **pending Content Design Lead with the HR Director**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
