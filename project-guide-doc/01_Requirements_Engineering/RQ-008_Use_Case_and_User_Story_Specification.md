---
id: RQ-008
title: Use Case & User Story Specification with Acceptance Criteria
category: 01 — Requirements Engineering
code: RQ
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Lead Business Analyst / Requirements Manager
approver: ERP Design Authority
standards_basis: ISO/IEC/IEEE 29148:2018 §5.2.4–§5.2.7, §6.3 · ISO/IEC/IEEE 12207:2017 Annex H (agile formulations) · BABOK v3 (use cases and scenarios)
traces_to: PGD-000 RQ-008 row · URD §6–17 (245 user stories) · BRD §13 (30 use cases) · module §17 acceptance criteria
depends_on: RQ-001 (requirement set) · RQ-004 (link T-14) · RQ-010 (definition of done) · BE-008 (sprint model)
verified_on: 2026-08-18
priority: P1
needed_by: W1
enumerated_on: 2026-08-18 02:15 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# RQ-008 — Use Case & User Story Specification with Acceptance Criteria

### Category 01 · Code `RQ` · ISO/IEC/IEEE 29148:2018 · 12207:2017 Annex H · BABOK v3

---

> **The URD is better than the register credits it, and still cannot be built from.**
>
> Measured at 2026-08-18 02:15 (+06): the URD holds **245 user stories**, each with a header
> carrying the role and its `Rnn`, the priority, the wave, the owning modules and the business
> objective — five attributes most story sets never carry. Each has acceptance criteria. The
> `06-02` benefit case, the module allocation and the wave plan are all reachable from a story
> header. This is a good artefact.
>
> Four things stop it being a delivery instrument:
>
> | Measured | Count |
> |---|---:|
> | Occurrences of Given/When/Then anywhere in the URD | **0** |
> | Occurrences of "story point" anywhere in the 601-file estate | **0** |
> | Stories carrying a link to the requirement they represent | **0** |
> | Acceptance criteria written as a run-on prose sentence rather than discrete criteria | **237 of 255** |
>
> The last is the one that matters most and is least visible. Eighteen stories carry a numbered
> `**AC**` block that a tester can decompose one criterion at a time. The other 237 carry an inline
> `**AC:**` sentence with clauses separated by `·`. A tester cannot mark half a sentence passed.
>
> **A note on the "255 user stories" figure.** It appears in `PGD-000` and the category overview.
> Counting story headers returns **245**; counting `AC` markers returns **255**. The published
> figure is the acceptance-criteria-marker count, not the story count. Corrected here as `RQA-24`.

---

## 1. Purpose

A requirement states what the system shall do. It does not say who wanted it, why, or how a tester
knows it happened. A user story says who and why; a use case says how the interaction actually
runs, including the four ways it goes wrong. Neither replaces the requirement, and the programme
needs all three — related by a stated rule rather than by assumption.

This document fixes that relationship, specifies the acceptance-criteria form that makes a story
testable, defines Definition of Ready, sets the sizing method the estate does not have, and states
how the 245 existing stories are converted without being rewritten.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The **three-artefact model** — requirement, use case, user story — and the rule relating them (§3) |
| 2 | The **user story schema** and its mandatory attributes (§4.1) |
| 3 | The **acceptance criteria standard** — Given/When/Then, with the rules that keep it testable (§4.2) |
| 4 | **Definition of Ready** — what a story must have before it may enter a sprint (§4.3) |
| 5 | **Sizing** — the estimation unit, the scale, and the reference stories (§4.4) |
| 6 | The **use case standard** — BABOK form, extended for this programme (§5) |
| 7 | The **conversion** of the 245 URD stories and the 30 BRD use cases (§6) |
| 8 | **Coverage** — which requirements need a story, and which do not (§7) |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| The requirement statements | `RQ-001` | A story represents a requirement; it is not one |
| Sprint length, ceremonies, velocity, backlog refinement | `BE-008` | This document defines the *unit*; `BE-008` defines the *cadence* |
| Definition of Done at story, module, wave and programme level | `RQ-010` | DoR here, DoD there — §4.3 states the interface |
| Test case design | `QA-003` | Acceptance criteria are the input to case design, not the cases |
| Process flows | `RQ-007` | A use case describes an interaction; a process model describes an end-to-end path |
| UI design | `UX-003`, `UX-004` | A story states the need; the screen is designed separately |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| Business analysts | The story and use case they write, and the readiness bar |
| Product owners / business owners | What they accept, and the criteria they accept against |
| Developers | The unambiguous behaviour statement they build to |
| QA | The criteria from which cases derive, one criterion at a time |
| Scrum masters / delivery leads | The Definition of Ready that governs sprint entry |
| Vendor | The delivery unit and its sizing basis |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | Conformance | Departure |
|---|---|---|---|
| ISO/IEC/IEEE 29148:2018 | §5.2.4–5.2.7 | Requirements remain the normative artefact; stories are an additional representation | None |
| ISO/IEC/IEEE 12207:2017 | **Annex H** | The standard explicitly permits agile formulations such as user stories without the term "shall". This document uses that permission — and bounds it (§3.2) | None |
| BABOK v3 | Use cases and scenarios | §5 use case form: actors, preconditions, trigger, main flow, alternative flows, postconditions — the form the BRD §13 already uses | None |
| ISO/IEC/IEEE 29119-3:2021 | Test design | Acceptance criteria are written so that one criterion yields at least one test case (§4.2 rule `AC-04`) | None |

**Verified 2026-08-18.**

### 2.2 Source material relied on

| Source | What it provides | Measured 02:15 (+06) |
|---|---|---|
| `../../primary-doc/…URD.md` §6–17 | User stories, personas, goals, journeys | **245 story headers; 247 unique `US-` identifiers; 68 prefixes; 255 `AC` markers — 18 block, 237 inline** |
| `.../…URD.md` §17 | Portal stories | 36 story headers under `US-POR-` |
| `.../…URD.md` line 4601–4602 | The remapping table for stale prefixes `US-HRM-*` and `US-CWM-*` | 2 documented remappings — **not** defects |
| `../../primary-doc/…BRD.md` §13 | Use cases in BABOK form | **30 use cases `UC-001`…`UC-030`** |
| `../../1000fix_ERP_Module/03_Modules/*/[MP]*.md` §17 | Module-level acceptance criteria | **1,568 `AC-nn` rows across 79 specifications** |
| `RQ-001` §3.10.2, §3.19 | The requirement construct and the verification methods |
| `RQ-010` | The Definition of Done this document's DoR hands over to |

### 2.3 Findings this document addresses

| Finding | Source | Treatment |
|---|---|---|
| **`RQA-24`** *(raised here)* | This document | The "255 user stories" figure counts `AC` markers, not stories. **Measured: 245 stories** | Corrected at issue |
| **`RQA-25`** *(raised here)* | This document | **237 of 255 acceptance criteria are inline run-on prose** and cannot be decomposed into discrete test outcomes | Open — §6.2 |
| **`RQA-26`** *(raised here)* | This document | **No story carries a link to the requirement it represents.** Link `T-14` is unpopulated for all 245 | Open — §6.3 |
| `PGD-000` `RQ-008` row | Register | *"None carries Given/When/Then, story points, or a Definition of Ready."* Confirmed by measurement: 0, 0, and none defined | Addressed by §4.2–§4.4 |

---

# 3. The Three-Artefact Model

## 3.1 What each artefact is for

| Artefact | Answers | Authority | Count today | Identifier |
|---|---|---|---:|---|
| **Requirement** | *What shall the system do, and how is it proved?* | **Normative.** The contract is accepted against it (`CO-003`) | 3,347 + 42 | `FR-`, `SWR-`, `SYR-`, `NFR-` |
| **Use case** | *How does this interaction actually run, including every way it fails?* | Analysis artefact | 30 | `UC-nnn` |
| **User story** | *Who wants this, why, and when is it done?* | Delivery unit | 245 | `US-<CODE>-nnn` |

## 3.2 The relating rule

**Rule `SU-01`.** The **requirement is normative**. A story and a use case are representations of
requirements, and where a story and its requirement disagree, the requirement governs.

**Rule `SU-02`.** Every story represents **at least one** requirement. A story representing none is
either a new requirement — raise it under `RQ-005` §6 — or it is not in scope.

**Rule `SU-03`.** A requirement may be represented by zero, one or many stories. §7 states which
requirements need one.

**Rule `SU-04`.** A use case may span many requirements and many stories. It is written where the
*interaction* is complex enough that the requirements alone do not convey it — typically where
there are three or more alternative flows.

```
      UC-001  Log a service request (multi-channel)
        │  actors · preconditions · trigger · main flow · A1–A4 · postconditions
        │
        ├── US-SRM-001  identify returning customer      ──▶ FR-SRM-001, FR-CPM-004
        ├── US-SRM-002  determine entitlement on scan    ──▶ FR-SRM-002, FR-WTY-003, FR-CTR-011
        └── US-SRM-003  select service from catalogue    ──▶ FR-SRM-003, FR-CAT-007
                              │
                              └── acceptance criteria (GWT) ──▶ TC-nnn  (QA-003)
```

**Rule `SU-05` — the anti-duplication rule.** A story does not restate its requirement's statement,
and a requirement does not absorb its story's narrative. Where the same sentence appears in both,
one of them is wrong, and the requirement wins.

---

# 4. User Story Specification

## 4.1 Story schema

The URD's existing header already carries five of these. Fields marked **new** are the additions.

```yaml
id:             US-SRM-014
title:          Estimate approval loop
role:           R08 Service Centre Agent          # existing — with the Rnn, per SP-003 PD-06
narrative: >                                       # existing
  As a service centre agent, I want the customer's estimate decision recorded
  against the version they were shown, so that a later dispute has an answer.
priority:       P0                                 # existing
wave:           W1                                 # existing
modules:        [M01]                              # existing
objectives:     [BO-01, BO-05]                     # existing
# --- new -----------------------------------------------------------------
requirements:   [FR-SRM-014, FR-SRM-015]           # new — link T-14, reciprocal
rules:          [BRU-SRM-13]                       # new
nfrs:           [NFR-001, NFR-040]                 # new
process:        BPM-016                            # new — link to RQ-007
acceptance:     [AC-1, AC-2, AC-3]                 # new — GWT, §4.2
size:           5                                  # new — story points, §4.4
dependencies:   [US-SRM-011]                       # new
owner:          Service Operations Manager         # new — accepts at UAT
status:         Ready | In sprint | Done | Accepted
```

**Rule `SU-06`.** A story's `role` is a registered `Rnn` from `05-04`. *"A user"* is not a role.
The URD already does this well — its story headers name `R08`, `R27`, `R37` and so on — and the
practice is retained, subject to `SC-004` registering `R39`–`R50`.

**Rule `SU-07` — INVEST.** A story shall be Independent, Negotiable, Valuable, Estimable, Small
and Testable. The two that fail most often here are **Small** (a story spanning four modules is an
epic) and **Testable** (which §4.2 makes mechanical).

## 4.2 Acceptance criteria standard

### 4.2.1 The form

**Rule `AC-01`.** Every acceptance criterion is written in Given/When/Then:

```
Given  <the precondition, stated as observable system or data state>
When   <the single triggering action>
Then   <the single observable outcome, with its measurable bound>
And    <further outcomes of the same trigger, one per line>
```

**Rule `AC-02` — one criterion, one outcome.** A criterion asserts one outcome. Where a trigger
produces several, each is a separate `Then`/`And` line, and each is separately markable.

**Rule `AC-03` — no run-on criteria.** A criterion is never a prose sentence with clauses
separated by punctuation. **This is the single most consequential rule in this document**: 237 of
the estate's 255 criteria are in that form, and a tester cannot record half a sentence as passed.

**Rule `AC-04` — one criterion yields at least one test case.** If a criterion cannot yield a case,
it is not a criterion.

**Rule `AC-05` — bounds are numeric.** *"Quickly"*, *"correctly"* and *"appropriately"* are banned
in criteria exactly as they are banned in requirements (`RQ-001` §3.10.4 Table B).

**Rule `AC-06` — the negative case is mandatory.** Every story carries at least one criterion for
the path where the action is refused, times out, or receives no response. `SP-003` `PD-10` already
identifies "no response by expiry" as the branch everyone misses.

**Rule `AC-07` — rules are cited, not restated.** Where a criterion enforces a business rule, it
cites the `BRU-` identifier. The URD already does this well; the practice is retained.

**Rule `AC-08` — bilingual criteria.** A criterion asserting user-facing text asserts it in both
Bengali and English, or asserts translation coverage. `NFR-016` requires 100%.

### 4.2.2 Worked conversion

`US-ARB-002` as it exists in the URD, and as converted:

**As written** *(inline form — one sentence, six clauses)*

> **AC:** Mushak 6.3 format compliant with the VAT and SD Act 2012 · VAT at the applicable rate
> with the Company's BIN displayed *(BRU-FIN-01, hard)* · category-correct VAT treatment without
> manual mapping · Bengali renders correctly in print and PDF · zero NBR exceptions at Gate 3.

**Defects:** five assertions in one criterion (`AC-02`); "category-correct" undefined (`AC-05`);
"renders correctly" unmeasurable (`AC-05`); no negative case (`AC-06`); "zero NBR exceptions at
Gate 3" is a gate criterion, not a story criterion.

**Converted**

```
AC-1  Given a completed service order with a priced line set
      When  the finance officer issues the invoice
      Then  the invoice is produced in Mushak 6.3 format per the VAT and SD Act 2012
      And   the Company's BIN is displayed in the header
      And   VAT is applied at the rate mapped to the line's product tax category
            in MD-024, with no manual selection offered   [BRU-FIN-01, hard]

AC-2  Given an invoice rendered for print and for PDF
      When  it contains Bengali characters including conjuncts
      Then  every glyph renders without substitution or clipping on the approved
            thermal printer and in the generated PDF/A          [SYR-031, SYR-050]

AC-3  Given a service order line whose product has no tax category mapped
      When  the finance officer attempts to issue the invoice
      Then  issue is blocked with a message naming the unmapped product,
            in the user's language                              [AC-06 negative case]

AC-4  Given an issued Mushak 6.3 invoice
      When  it is submitted to the NBR VAT Online portal
      Then  the submission is accepted without exception, and the acceptance
            reference is recorded against the invoice           [NFR-116]
```

Four discrete, separately-markable criteria. The Gate 3 assertion moves to `RQ-010` where gate
criteria belong.

## 4.3 Definition of Ready

**Rule `SU-08`.** A story may not enter a sprint until every item below is true. `05-01` §6 already
requires a testable acceptance criterion; this is that rule made complete.

| # | Ready criterion | Checked by |
|---|---|---|
| `DR-01` | The story has an `id`, a registered `Rnn` role, a narrative and a title | BA |
| `DR-02` | It links to ≥ 1 requirement, reciprocally (`T-14`) | BA |
| `DR-03` | Every acceptance criterion is in GWT form and passes `AC-01`–`AC-08` | BA + QA |
| `DR-04` | At least one negative-case criterion exists | QA |
| `DR-05` | Every cited `BRU-`, `NFR-`, `MD-` and `Rnn` identifier resolves | Automated — `CT-08` |
| `DR-06` | Its fit-gap disposition is determined and is not `undetermined` | Solution Architect (`RQ-003`) |
| `DR-07` | It is sized, and the size is ≤ the sprint ceiling in §4.4 | Team |
| `DR-08` | Dependencies are identified and are either done or in the same sprint | Delivery Lead |
| `DR-09` | Its UI need is either designed (`UX-003`) or explicitly not required | UX Lead |
| `DR-10` | Its Bengali content exists or is commissioned (`NFR-016`) | Content Lead |
| `DR-11` | Its business owner is named and available to accept it | Product Owner |

**Rule `SU-09` — the interface with Done.** DoR is the entry gate; `RQ-010` owns the exit gate. A
story that satisfies DoR and is built is **not** done until `RQ-010`'s story-level Definition of
Done is met. The two documents are deliberately separate so that neither can be relaxed by
editing the other.

## 4.4 Sizing

**Measured: "story point" occurs zero times in the 601-file estate**, and 1,513 person-weeks of
work must be decomposed into sprints by some method.

**Rule `SU-10`.** The estimation unit is the **story point**, a relative measure of size,
complexity and uncertainty combined. It is not hours, and it is not converted to hours.

**Rule `SU-11`.** The scale is modified Fibonacci: **1, 2, 3, 5, 8, 13**. A story estimated above
**8** is split before it enters a sprint. A story estimated at 13 that cannot be split is an
epic and is decomposed.

**Rule `SU-12` — reference stories.** Each squad maintains three reference stories — one at 1, one
at 3, one at 8 — chosen from delivered work. Estimation is by comparison to references, not by
imagined effort. Without references, points drift and velocity becomes meaningless across waves.

**Rule `SU-13` — a fit is not free.** A story whose requirements are dispositioned `fit` or
`configure` (`RQ-003`) is still sized: configuration, test, Bengali content, documentation and
data all take time. Sizing a fit at zero is how a configuration-heavy ERP wave overruns.

**Rule `SU-14` — the sizing basis is recorded once.** Velocity, capacity and the conversion from
points to the 1,513 PW estimate belong to `BE-008` and `GV-007`. This document supplies the unit
and the scale only; publishing a conversion factor here would create a fifth estimate
(`PGD-A1-05`).

---

# 5. Use Case Specification

## 5.1 When a use case is written

**Rule `UC-01`.** A use case is written where **any** holds:

| # | Trigger |
|---|---|
| `UT-1` | The interaction has three or more alternative flows |
| `UT-2` | The interaction crosses a system boundary to an external party |
| `UT-3` | The interaction is one of the 15 critical journeys (`05-06` §11) |
| `UT-4` | The interaction has a statutory consequence — consent, tax, breach, destruction |
| `UT-5` | Two or more roles interact within a single transaction |

Otherwise the requirements and their stories suffice. A use case restating one story's happy path
is documentation for its own sake.

## 5.2 Use case form *(BABOK v3, as the BRD §13 already uses)*

| § | Element | Rule |
|---|---|---|
| 1 | **Identifier and name** | `UC-nnn`, `<Verb> <object>` |
| 2 | **Actors** | Registered `Rnn` roles plus external parties and *System* |
| 3 | **Preconditions** | Observable state, not intent |
| 4 | **Trigger** | The single event that starts it |
| 5 | **Main flow** | Numbered steps; each step names the module that performs it |
| 6 | **Alternative flows** | `A1`, `A2`…; each states its entry condition and its rejoin or termination point |
| 7 | **Exception flows** | Failure paths, distinguished from alternatives — an alternative succeeds differently; an exception does not succeed |
| 8 | **Postconditions** | The state each entity is left in, per terminal outcome |
| 9 | **Requirements realised** | Link `T-14` extended to use cases |
| 10 | **Rules applied** | `BRU-` identifiers |
| 11 | **Non-functional constraints** | `NFR-` identifiers |

**Rule `UC-02`.** A use case names the **module** performing each step. The BRD §13 already does
this — `UC-001` step 2 names `M33`, step 3 names `M17`, step 4 names `M09`/`M08`/`M11`. That
practice is what makes a use case reconcilable against a process model (`RQ-007` `PM-17`).

**Rule `UC-03`.** A use case is **not** a process model. `UC-nnn` describes one interaction with
the system; `BPM-nnn` describes an end-to-end business path that may include physical acts and
several interactions. Where both exist, the process model references the use case.

## 5.3 The existing use case set

`UC-001` … `UC-030` exist in BRD §13 in the correct form, with actors, preconditions, trigger,
main flow, alternatives and postconditions.

| Action | Detail |
|---|---|
| **Retain** | The set and its identifiers. `UC-nnn` is the BRD's allocated space (`RQ-005` §7.2) |
| **Extend** | Add §7 exception flows (currently merged into alternatives), §9 requirements realised, §10 rules, §11 NFRs |
| **Correct** | `UC-001` step 2 cites `NFR-090…092` for PDPA consent capture. Those identifiers are reallocated to `SWR-018`–`SWR-020` (`RQ-006` §3.4). This is one of the citations that must be updated before the retirements close — open item `OI-01` |
| **Assess coverage** | 30 use cases against the `UT-1`–`UT-5` triggers; the gap is measured in §6.4 |

---

# 6. Conversion

## 6.1 Principle

**Rule `SU-15`.** Conversion **preserves meaning**. A conversion that changes what a story asks for
is a change and takes the `RQ-005` §6 path. This is the same boundary `RQ-005` `RM-07` draws for
requirement conversion, and it exists for the same reason: conversion at this scale is otherwise
an unaudited opportunity to move scope.

## 6.2 Converting the acceptance criteria *(finding `RQA-25`)*

| Population | Count | Conversion |
|---|---:|---|
| Block-form criteria (`**AC**` + numbered list) | **18** | Reformat to GWT; add negative case where absent. **Low effort — the decomposition already exists** |
| Inline-form criteria (`**AC:**` + `·` separators) | **237** | Decompose each clause into a discrete criterion, then convert to GWT. **This is the bulk of the work** |
| Total | **255** | |

The 18 block-form stories are the model. `US-SRM-001` and `US-SRM-002` in URD §6.1 are already
close to conforming: numbered, discrete, bound (*"≤ 1 second"*, *"≤ 2 seconds"*), rule-citing
(`BRU-SRM-02`, `BRU-SRM-03`), and `US-SRM-002` even carries a negative case. **The programme knows
how to write these; it did so 18 times and then switched to prose.**

## 6.3 Establishing the requirement link *(finding `RQA-26`)*

**Rule `SU-16`.** Every story is linked to the requirements it represents, reciprocally (`T-14`).

The link is derivable, not guessed: a story header already names its modules and its role, and its
criteria already cite `BRU-`, `AUT-` and `NFR-` identifiers. Deriving the requirement set from
that, and confirming it with the module author, is bounded work — but it is **245 confirmations**,
not an algorithm, because a wrong link is worse than no link.

## 6.4 Coverage assessment

Two coverage questions must be answered during conversion, and both are open at issue:

| Question | Why it matters | Owner |
|---|---|---|
| Which of the 3,389 requirements have **no** story? | §7 states which need one; the rest are covered by module `AC` or by test alone | BA per category |
| Which interactions meeting `UT-1`–`UT-5` have **no** use case? | 30 use cases against 67 modules and 15 critical journeys is unlikely to be complete | Lead BA |

**Rule `SU-17`.** The coverage assessment is published as a count, not asserted as complete. A
conversion that reports full coverage of 3,389 requirements by 245 stories has not been done.

## 6.5 Where converted artefacts live

**Rule `SU-18`.** Converted stories and use cases remain in the URD and the BRD respectively —
those documents are their home, and `FOLDER_STRUCTURE.md` §9 gives the primary documents
precedence on user intent. This document specifies the **form**; it does not become the container.
Extracting 245 stories into a fourth location would create the divergent second population
`RQ-001` decision `D-01` refuses.

---

# 7. Story Coverage Rules

**Rule `SU-19`.** A requirement needs a story when it is delivered through a **user-visible
interaction**. It does not when it is not.

| Requirement class | Story required? | Verified by |
|---|:--:|---|
| User-facing functional behaviour | **✔** | Story acceptance criteria → UAT |
| Portal or application surface (`FR-POR-*`) | **✔** | As above |
| Programme-level cross-surface obligation (`SWR-001`–`SWR-010`) | **✔** — one story per portal per obligation, or one global story with per-portal criteria | As above |
| Record and truth obligations (`SWR-011`–`SWR-014`, `SWR-033`–`SWR-036`) | ✗ | Test and inspection; no user interacts with them directly |
| Residency and PDPA obligations (`SWR-015`–`SWR-029`) | **✔ where a data subject or an operator acts** — consent capture, DSR handling, withdrawal. ✗ for enforcement-layer behaviour | Mixed |
| System requirements (`SYR-*`) | ✗ | `RQ-002` §4.18 verification events |
| Quality requirements (`NFR-*`) | ✗ — but each **constrains** stories and appears in their criteria | `RQ-006` §3.5 measurement |
| Integration contracts | ✗ | Contract tests (`QA-005`) |
| Migration requirements | ✗ | Reconciliation (`MG-004`) |

**Rule `SU-20`.** A requirement with no story and no other verification route is a **coverage gap**,
reported by `RQ-004` `CV-M5`. "It has no story" is never itself a reason a requirement is untested.

---

# 8. Decisions Recorded

| # | Decision | Options | Chosen | Rationale |
|---|---|---|---|---|
| D-01 | Which artefact is normative | (a) Stories, agile-style; (b) requirements | **(b)** | `CO-003` accepts a contract against requirements. 12207 Annex H permits story form as a *representation*, not as the contract |
| D-02 | Acceptance criteria form | (a) Keep the inline `·` form; (b) Given/When/Then | **(b)** | A tester cannot mark half a sentence passed. 237 of 255 criteria are currently unmarkable |
| D-03 | Where converted stories live | (a) Extract to this repository; (b) stay in the URD | **(b)** | A fourth location for the same content diverges, per `RQ-001` `D-01` |
| D-04 | Estimation unit | (a) Person-days; (b) story points | **(b)** | Hours estimates become commitments and then become the plan. Points are relative and re-calibrate through velocity |
| D-05 | Whether to publish a points-to-PW conversion | (a) Yes; (b) no — `BE-008` and `GV-007` | **(b)** | It would be a fifth uncontrolled estimate (`PGD-A1-05`) |
| D-06 | Sizing a `fit` requirement | (a) Zero — the product already does it; (b) sized | **(b)** | Configuration, test, Bengali content and documentation are real work. Zero-sizing fits is a classic ERP overrun mechanism |
| D-07 | Negative-case criteria | (a) Optional; (b) mandatory — `AC-06` | **(b)** | `SP-003` `PD-10` already identifies the missing third branch as the commonest real-world defect |
| D-08 | Whether DoR and DoD live together | (a) One document; (b) DoR here, DoD in `RQ-010` | **(b)** | Separating entry and exit gates stops either being relaxed by editing the other |

---

# 9. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | Who confirms the 245 story-to-requirement links — module authors or the BA team? | Lead BA | W1 | `SU-16`, `T-14`, `DR-02` |
| Q-02 | Are the 30 BRD use cases sufficient against `UT-1`–`UT-5`, and who assesses? | Lead BA | W1 | §6.4 |
| Q-03 | Which tool holds stories, criteria, sizes and links, and does it satisfy `RQ-005` §9.3? | Delivery Lead | W1 | `DR-05` automation |
| Q-04 | When are the `NFR-090`–`NFR-099` citations in BRD §13 updated? | Requirements Manager | W1 | `OI-01`, use case correction |
| Q-05 | Are per-module business owners available at the rate `DR-11` requires? | Programme Director | W1 | Sprint entry for every story |
| Q-06 | Do the 36 `US-POR-` portal stories need splitting per portal, given 12 portals share one prefix? | Lead BA | W2 | Portal backlog construction |

---

# 10. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The three artefacts are distinguished with a stated normative rule | §3, `SU-01` |
| AC-02 | The story schema names every mandatory attribute, marking which are new | §4.1 |
| AC-03 | Given/When/Then is specified with eight rules that keep criteria testable | §4.2 |
| AC-04 | A worked conversion of a real estate criterion is given | §4.2.2 |
| AC-05 | Definition of Ready has eleven checkable items and names its checker | §4.3 |
| AC-06 | An estimation unit, scale, splitting threshold and calibration method are defined | §4.4 |
| AC-07 | The use case form matches the form the BRD already uses, extended not replaced | §5.2, §5.3 |
| AC-08 | Conversion preserves meaning, with the boundary to change stated | §6.1, `SU-15` |
| AC-09 | Story coverage rules state which requirements need a story and which do not | §7 |
| AC-10 | Counts are measured and the published "255" figure is corrected | §2.2, `RQA-24` |

---

# 11. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `RQ-001` | The normative requirements stories represent |
| Upstream | `../../primary-doc/…URD.md` §6–17 | The 245 stories converted |
| Upstream | `../../primary-doc/…BRD.md` §13 | The 30 use cases extended |
| Upstream | `05-04` / `SC-004` | The `Rnn` roles stories name |
| Lateral | `RQ-004` `T-14` | The reciprocal story link |
| Lateral | `RQ-007` | Process models the use cases reconcile against |
| Lateral | `RQ-009` | The rules criteria cite |
| Downstream | `RQ-010` | Definition of Done, which DoR hands over to |
| Downstream | `BE-008` | Sprint model, velocity and backlog consuming the sizing unit |
| Downstream | `QA-003` | Test cases derived one per criterion |
| Downstream | `QA-009` | UAT scripts derived from criteria |
| Downstream | `UX-003`, `UX-004` | Screens and flows designed for stories |

---

# 12. References

**Within this repository**
[`RQ-001`](RQ-001_Software_Requirements_Specification.md) ·
[`RQ-004`](RQ-004_Requirements_Traceability_Matrix.md) ·
[`RQ-005`](RQ-005_Requirements_Management_Plan.md) ·
[`RQ-006`](RQ-006_Non_Functional_Requirements_Specification.md) ·
[`RQ-007`](RQ-007_Business_Process_Model_Repository.md) ·
[`RQ-009`](RQ-009_Business_Rules_Specification.md) ·
[`RQ-010`](RQ-010_Acceptance_Criteria_and_Definition_of_Done_Standard.md) ·
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md)

**Workspace**
`../../primary-doc/1000FiX_ERP_System_Comprehensive_URD.md` §3, §5, §6–17 ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md` §13 ·
`../../1000fix_ERP_Module/03_Modules/*/[MP]*.md` §17 ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-01` §6 ·
`../../project_content/13_Test_and_Acceptance_Content/TS-006`…`TS-011`

**External**

| Reference | Verified on |
|---|---|
| ISO/IEC/IEEE 29148:2018 §5.2.4–§5.2.7, §6.3 | 2026-08-18 |
| ISO/IEC/IEEE 12207:2017 Annex H — agile formulations | 2026-08-18 |
| ISO/IEC/IEEE 29119-3:2021 — test design | 2026-08-18 |
| BABOK v3 (IIBA) — use cases and scenarios | 2026-08-18 |

---

# 13. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Three-artefact model; GWT standard with eight rules; eleven-item Definition of Ready; story-point sizing with a splitting threshold; conversion specified for 245 stories and 255 criteria; findings `RQA-24`, `RQA-25`, `RQA-26` raised | *Pending — `GV-002`* |

---

*`RQ-008` · Category 01 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
