---
id: BE-008
title: Sprint Model, Estimation & Backlog Management Standard
category: 07 — Build Engineering & Development Standards
code: BE
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Engineering Lead
approver: Programme Director
standards_basis: >
  Scrum Guide 2020 · Disciplined Agile / SAFe wave-gated hybrid · PMBOK 7 (agile performance domain) ·
  AACE 17R-97 estimate classes (via GV-007) · ISO 21502:2020 §7
traces_to: >
  PGD-000 BE-008 · old-primary-doc Missing-Documents checklist Document 5 · RQ-008 SU-10…SU-14 ·
  RQ-010 §4.2 · GV-004 §5.2 · GV-007 §3, §7 · GV-006 (descope hierarchy) · BE-005 §7.5 · PGD-A2-04
depends_on: BE-005 (the epic layer) · RQ-008 (the unit and scale) · RQ-010 (Definition of Done) · GV-004
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 13:06 (+06)
priority: P0
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# BE-008 — Sprint Model, Estimation & Backlog Management Standard

### Category 07 · Code `BE` · Scrum Guide 2020 · wave-gated hybrid · ISO 21502:2020 §7

---

## 1. Purpose

The phrase **"story point" occurs zero times** in the 621-file source estate. Verified 2026-08-18
13:06 (+06) across `primary-doc/`, `old-primary-doc/`, `1000fix_ERP_Module/` and `project_content/`;
the only occurrences anywhere in the workspace are in the guiding documents written on this date.

Against that absence sits **1,842 person-weeks of build demand across 331 custom-development items**,
which must be decomposed into iterations by some method, executed by a team growing from 3 to 12
build FTE, and assessed at nine funded wave gates.

`RQ-008` `SU-10`…`SU-14` has already set the **unit** — the story point, on a modified Fibonacci
scale, estimated against squad reference stories — and has explicitly deferred *"velocity, capacity
and the conversion from points to the person-week estimate"* to this document and to `GV-007`. This
document supplies exactly that, plus the sprint mechanics, the backlog structure and the procedure
for a sprint that cannot fit.

> **It also has to say something uncomfortable.** §6 shows that with all 79 delivery units placed in
> their own declared waves, the programme's demand is **1.69× its effective capacity**, and **no wave
> before W8 is under capacity**. A sprint model cannot fix that. What it can do is make each sprint's
> shortfall visible in two weeks rather than at a wave gate eighteen months later, and §8 is the
> procedure for what to do when it is.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | Sprint length, cadence and the ceremony set, scaled to a team of 3 to 12 |
| 2 | The **backlog hierarchy** — wave, epic, feature, story — and its identifiers |
| 3 | **Definition of Ready**, and its relationship to `RQ-008` §4.3 |
| 4 | Estimation — unit, scale, reference stories, and the **person-week conversion `RQ-008` defers here** |
| 5 | Velocity, capacity and forecasting |
| 6 | The **capacity position**, recomputed against all 79 delivery units |
| 7 | Sprint planning, commitment and the treatment of carry-over |
| 8 | What happens when a sprint or a wave does not fit |
| 9 | Standing capacity allowances — review, dependency updates, debt, support |
| 10 | Metrics, and their misuse |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| The estimation **method** and its calibration | `GV-007` §3 | This document consumes `GV-007`'s figures and converts them; it does not re-estimate |
| The **unit** and its scale | `RQ-008` `SU-10`…`SU-13` | Set there; not re-decided |
| Story form and acceptance criteria | `RQ-008` §4.1, §4.2 | |
| The Definition of Done | `RQ-010` §4.2, `BE-006` §5 | Cited, not restated |
| Wave content and the master schedule | `GV-004` | This document plans inside a wave |
| Wave gates and exit criteria | `GV-009` | |
| The descope hierarchy | `GV-006` §7 | Invoked by §8.3, not redefined |
| Team structure and hiring | `GV-007` §8 | Consumed as a capacity input |
| Tooling selection | `PE-009` | This document states what the tool must hold |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Engineering Lead / squad leads** | §4–§7 — how a sprint is planned, committed and closed |
| Product owner | §3's backlog structure; §5's Definition of Ready |
| **Every developer** | §5 estimation; §7 commitment; what "done" means for a story |
| Programme Director / PMO | §6's capacity position and §9's metrics |
| Business owners and super-users | §9.3 — the demand this places on them, quantified |
| Wave-gate assessors | §8's escalation record as gate evidence |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure and rationale |
|---|---|---|
| **Scrum Guide 2020** | Sprint, sprint planning, daily scrum, review, retrospective, product backlog, increment | **Departure:** the Sprint Goal is subordinate to the wave gate. Scrum assumes the team decides what "valuable increment" means; here `GV-009` decides, and funding follows |
| **Wave-gated hybrid** | Nine gated waves with an agile cadence inside each | This is not textbook Scrum and is not pretended to be. §2.3 states the shape honestly |
| **PMBOK 7** — agile performance domain | Delivery cadence, measurement, uncertainty | Full |
| **AACE 17R-97** estimate classes | Consumed from `GV-007` §3.2 | This document does not create estimates; it converts and tracks them |
| **ISO 21502:2020** §7 | Integrated planning, control and reporting | Full |

### 2.2 Source material relied on

| Source | Contribution |
|---|---|
| `RQ-008` §4.4 `SU-10`…`SU-14` | The unit (story point), the scale (1–13, split above 8), reference stories, the "a fit is not free" rule, and the **explicit deferral of the conversion factor to this document** |
| `RQ-010` §4.2 | `SD-01`…`SD-11`, the story-level Definition of Done |
| `BE-006` §5 | The 23-criterion component Definition of Done |
| `BE-005` §6, §7.5 | 331 CD items, their effort and their wave placement |
| `GV-004` §5.2 | Wave lengths, build FTE ramp, the 0.78 delivery factor, and effective capacity per wave |
| `GV-007` §3.4, §7 | The person-week as the unit of estimate; the consolidated 3,022 PW position |
| `GV-006` §7 | The descope hierarchy invoked by §8.3 |
| `old-primary-doc/…Missing_Implementation_Documents.md` §3 Document 5 | The original requirement: re-baselined timeline, sprint breakdown, ownership and parallelisation, per-task Definition of Done, lean ceremonies, per-sprint risk, milestone gates |
| **`../../../AGENTS.md`** | Confirms `pnpm test`, `pnpm test:coverage` and the in-house 80% / 70% coverage targets that `SD-04` inherits |

### 2.3 What this model actually is

Stated plainly, because calling a wave-gated programme "Scrum" and then overriding it at every gate
is how teams stop believing the process.

| Layer | Cadence | Decides | Authority |
|---|---|---|---|
| **Programme** | 36 months, 9 waves | What is built, in what order, for what money | Steering Committee (`GV-002`) |
| **Wave** | 4–5 months | Which modules and portals; the gate criteria | `GV-004`, `GV-009` |
| **Sprint** | **2 weeks** | Which stories, and how they are built | The squad |
| **Day** | Daily | Impediments and sequencing | The squad |

> **The sprint is genuinely autonomous inside a wave and genuinely not autonomous about the wave.**
> A squad chooses its stories, its sequence and its design; it does not choose whether M01 ships in
> Wave 1. Pretending otherwise produces a sprint review where the team's decisions are silently
> reversed, which is worse than saying so up front.

---

## 3. The Backlog

### 3.1 Hierarchy

Four levels, each with an existing identifier space. **No new identifier space is created** — the
estate's largest recurring defect is identifier proliferation (`PGD-A2-17`, `H-03`, `H2-04`).

| Level | Object | Identifier | Count | Owner |
|---|---|---|---:|---|
| **Wave** | A funded, gated delivery period | `W1`…`W9` | 9 | Steering |
| **Epic** | A delivery unit — module or portal | `M01`…`M67`, `P01`…`P12` | **79** | Business owner |
| **Feature** | A custom-development item | **`CD-<UNIT>-<nn>`** from `BE-005` | **331** | Squad |
| **Story** | A sprint-sized slice | `ST-<CD-ID>-<nn>` | ~4,500 est. | Developer |

| # | Rule |
|---|---|
| **`SPR-01`** | Every backlog item resolves to exactly one **issued** `BE-005` identifier. An item with no CD identifier does not enter the backlog |
| **`SPR-02`** | Story identifiers are **derived**, never centrally allocated: `ST-CD-M01-03-04`. Derivation is what stops the collision class that produced 48 colliding CD identifiers (`BE-005` §4) |
| **`SPR-03`** | The backlog holds **work**, not requirements. A requirement lives in `RQ-001`; a story references it. Conflating them produces a backlog nobody can prioritise |
| **`SPR-04`** | Configuration work is a story. `RQ-008` `SU-13` — *"a fit is not free"* — applies: a requirement dispositioned `fit` or `configure` in `RQ-003` still consumes configuration, test, Bengali content, documentation and data effort |

### 3.2 The backlog could not lawfully exist until now

`_MODULE_TEMPLATE` §16.2 instructs every module author:

> **"Do not create a build backlog item from an identifier in this table until 02-05 has issued it."**

`02-05` never issued them, so under the programme's own rule **no backlog item could be created for
any of 331 components**. `BE-005` issues them at the same date as this document, which is why both
are `P0`. Recorded here so the sequence is understood: the backlog does not start on the day someone
opens the tool, it starts on the day the identifiers exist.

### 3.3 Decomposition

| # | Rule |
|---|---|
| **`SPR-05`** | A CD item is decomposed into stories **one wave before** the wave it is delivered in. Decomposing everything up front produces 4,500 stories that are stale before they are read |
| **`SPR-06`** | A story is **vertical** — it delivers observable behaviour end to end. "Build the model" and "build the view" are tasks, not stories |
| **`SPR-07`** | A story is sized ≤ **8** points (`SU-11`). A 13 that cannot be split is an epic and is decomposed |
| **`SPR-08`** | Every story names the requirement, business rule or NFR it satisfies, and the reference is reciprocal (`RQ-004` `T-04`, `T-07`) |
| **`SPR-09`** | Non-functional work is a story with acceptance criteria, not a footnote — performance, accessibility, Bengali completeness, security negative tests |

### 3.4 The unallocated-requirement problem

`GV-004` `PGD-A2-04` records **1,816 requirements not allocated to any wave**, against a measured
population of 3,347 requirement rows (`RQA-02`). Roughly **54% of the requirement estate has no wave**,
and therefore no sprint and no backlog position.

| # | Rule |
|---|---|
| **`SPR-10`** | A requirement with no wave cannot be decomposed into a story, and a CD item whose requirements are unallocated **cannot be planned**. This is reported at sprint planning as an impediment, not absorbed by guessing |
| **`SPR-11`** | The unallocated population is reported at every wave gate with its trend. A number that does not fall is a planning failure that sprints cannot repair |

---

## 4. The Sprint

### 4.1 Shape

| Attribute | Value | Reasoning |
|---|---|---|
| Length | **2 weeks**, fixed | Short enough to correct within a wave; long enough to complete a vertical Odoo story including Bengali content and negative tests |
| Sprints per wave | W1 9 · W2 9 · W3 11 · W4 11 · W5 9 · W6 9 · W7 9 · W8 9 · W9 4 | Wave weeks (`GV-004` §5.2) ÷ 2 |
| **Total sprints** | **80** | 156.5 programme weeks ÷ 2 = 78.25; rounded per wave, 9+9+11+11+9+9+9+9+4 = 80 |
| Start day | Wednesday | A Monday start loses a day to the previous sprint's close; a Wednesday close leaves Thursday and Friday for the review to be acted on |
| Sprints are **never** extended | — | A sprint that does not fit is closed and re-planned (§8.1). Extending hides the signal |

**Verification** *(`PG-M10`)*: 9 + 9 + 11 + 11 + 9 + 9 + 9 + 9 + 4 = **80** ✓ against 156.5 weeks ÷ 2
= 78.25, the difference arising from per-wave rounding.

### 4.2 Ceremonies, scaled

`GV-004` §5.2 staffs the programme at **3 build FTE in W1** rising to **12 by W6**. A ceremony set
designed for twelve is unaffordable for three; one designed for three does not coordinate twelve.

| Ceremony | 3–5 FTE (W1–W2) | 6–12 FTE (W3–W9) | Purpose |
|---|---|---|---|
| Sprint planning | 1 h | 2 h, two-part | Commitment |
| Daily scrum | **10 min, asynchronous** in writing | 15 min, in person or on call | Impediments only |
| Backlog refinement | 30 min weekly | 1 h weekly | Ready items for the next sprint |
| Sprint review | 30 min | 1 h, with business owners | Demonstrate the increment |
| Retrospective | 20 min | 45 min | One improvement, owned |
| **Wave-gate assessment** | — | Per `GV-009` | Not a sprint ceremony |

| # | Rule |
|---|---|
| **`SPR-12`** | The daily scrum is **impediments only**. Status is in the tool; reading it aloud is the most expensive way to distribute information the tool already holds |
| **`SPR-13`** | A retrospective produces **one** improvement with a named owner and a next-sprint checkpoint. Three improvements with no owner produce none |
| **`SPR-14`** | The sprint review demonstrates working software in an environment, not slides. `SD-11` requires business-owner acceptance, and a business owner cannot accept a screenshot |
| **`SPR-15`** | Ceremony time is capacity. §7.2's allowance accounts for it explicitly rather than treating it as free |

---

## 5. Estimation

### 5.1 What is already decided

`RQ-008` `SU-10`…`SU-13` set the unit, the scale, the reference stories and the fit-is-not-free rule.
They are not re-decided here. This section supplies what `SU-14` deferred.

### 5.2 The conversion `RQ-008` deferred

The programme carries two units. `GV-007` estimates in **person-weeks**, at estimate class 2 against a
79-file count. Squads estimate in **story points**, relatively, against reference stories. Both are
needed and they must be reconciled without corrupting either.

| # | Rule |
|---|---|
| **`SPR-16`** | **The conversion is one-directional and empirical.** Velocity in points is measured, then converted to person-weeks for programme reporting. **Person-weeks are never converted into points to set a sprint commitment** |
| **`SPR-17`** | The conversion factor is a **measurement, not a constant**. Each squad's factor is computed from its own delivered work over the previous three sprints |
| **`SPR-18`** | The factor is **per squad**, never programme-wide. A programme-wide factor turns points into disguised hours and destroys relative estimation |
| **`SPR-19`** | Until a squad has three sprints of history, planning uses the **provisional factor** in §5.3, marked as such, and the fact that it is provisional is stated in every report that uses it |

**How the factor is computed.**

```
squad effective PW in a sprint = FTE × 2 weeks × 0.78            (GV-004's delivery factor)
squad conversion factor        = mean points delivered ÷ effective PW
```

For a 4-FTE squad delivering a mean of 30 points per two-week sprint:

```
effective PW  = 4 × 2 × 0.78 = 6.24
factor        = 30 ÷ 6.24    = 4.8 points per effective PW
```

> **`SPR-16` is the rule that protects the estimate.** The tempting move is to take a CD item's 16 PW
> from `BE-005`, multiply by the factor, and hand the squad 77 points as a target. That converts a
> class-2 programme estimate into a sprint commitment, which is precisely the error `GV-007` §4.4
> diagnosed: *"a correction factor was applied to estimates instead of counting."*

### 5.3 The provisional factor, and its basis

| Input | Value | Source |
|---|---|---|
| Total CD effort | **1,850 PW** | `BE-005` §6 |
| CD items | **331** | `BE-005` §6 |
| Mean effort per CD item | **5.59 PW** | 1,850 ÷ 331 |
| Assumed mean story size | **3 points** | Midpoint of the 1–8 usable range (`SU-11`) |
| Assumed stories per PW | **2.5** | A 2-day vertical story including tests, Bengali content and documentation |
| **Implied story population** | **~4,600** | 1,850 × 2.5 |
| **Provisional factor** | **7.5 points per effective PW** | 2.5 stories × 3 points |

| # | Rule |
|---|---|
| **`SPR-20`** | The provisional factor is **estimate class 5** — an order-of-magnitude figure on an assumption, not a measurement. It is replaced by each squad's measured factor after three sprints and is never used for a commitment |
| **`SPR-21`** | The implied ~4,600-story population is a **planning signal, not a target**. Its purpose is to show that the backlog is an order of magnitude larger than the 245 user stories the URD holds (`RQA-24`), and that story authoring is itself unbudgeted work |

> **~4,600 stories against 245 in the URD is a 19× gap, and it is nobody's line item.** `GV-007` §7.3
> lists seven work streams excluded from the estimate; story authoring and backlog refinement are not
> among them. At 15 minutes per story to author, refine and link, 4,600 stories is roughly **1,150
> hours — about 29 person-weeks** of product-owner and business-analyst time that appears in no plan.
> Raised as **`BEA-17`**.

### 5.4 Estimating

| # | Rule |
|---|---|
| **`SPR-22`** | Estimation is done **by the people who will do the work**, together, by comparison to the squad's reference stories (`SU-12`) |
| **`SPR-23`** | An estimate is a **size**, not a commitment and not a promise. A story that turns out larger is re-estimated at the next refinement, not defended |
| **`SPR-24`** | Uncertainty is resolved by a **spike** — time-boxed, on a `spike/*` branch that is never merged (`BE-003` §4.2) — not by inflating the estimate |
| **`SPR-25`** | The first three sprints of any squad are **explicitly calibration sprints**. Their velocity is not used for forecasting, and this is stated in the reporting rather than discovered later |

---

## 6. Capacity — the Recomputed Position

### 6.1 Why this section exists

`GV-004` §5.3 concludes that *"the plan balances in aggregate and fails in shape"* — 1,079 PW of
demand against 1,088 PW of effective capacity, 0.99×. That conclusion rests on the 42 delivery units
in the programme's wave model: M01–M30 and the twelve portals.

`BE-005` §6 covers **all 79 units**, and every one of the 37 modules M31–M67 declares a delivery wave
in its own §1 Identity table. Placing each unit in the wave it declares:

| Wave | `GV-004` demand (42 units) | **All-79 demand** | Effective capacity | **Ratio** | Sprints |
|:--:|---:|---:|---:|---:|:--:|
| W1 | 217 | **239** | 40.7 | **5.87×** | 9 |
| W2 | 167 | **240** | 95.0 | **2.53×** | 9 |
| W3 | 153 | **281** | 152.3 | **1.85×** | 11 |
| W4 | 224 | **353** | 169.3 | **2.09×** | 11 |
| W5 | 108 | **247** | 135.7 | **1.82×** | 9 |
| W6 | 99 | **235** | 162.9 | **1.44×** | 9 |
| W7 | 98 | **185** | 162.9 | **1.14×** | 9 |
| W8 | 13 | **39** | 135.7 | 0.29× | 9 |
| W9 | 0 | **23** | 33.9 | 0.68× | 4 |
| **Total** | **1,079** | **1,842** | **1,088.4** | **1.69×** | **80** |

**Verification** *(`PG-M10`)*: 239 + 240 + 281 + 353 + 247 + 235 + 185 + 39 + 23 = **1,842** ✓,
matching `GV-007` §4.1's counted build total.

### 6.2 What it means for a sprint

| Finding | Sprint consequence |
|---|---|
| **The plan does not balance in aggregate.** 1.69×, not 0.99× | A sprint model cannot absorb a 69% overload. §8's escalation is the operative section, not the exception |
| **Wave 1 is 5.87× over.** 239 PW against 40.7 effective, across 9 sprints | ~4.5 effective PW per sprint against ~26.6 PW of demand per sprint. **Wave 1 as scoped is undeliverable by roughly a factor of six** |
| **No wave before W8 is under capacity** | There is no later wave with spare room to absorb a slip. `GV-004` §5.3's *"Waves 6–9 are half empty"* holds only for the 42-unit view |
| **Wave 1 has the smallest team and the heaviest infrastructure load** (TSS §20.3, fifteen components) | The first nine sprints are the ones most likely to teach the wrong lesson about velocity — hence `SPR-25` |

### 6.3 The honest statement

> **This document cannot make Wave 1 fit, and it does not pretend to.** What it does is guarantee the
> shortfall is visible at the end of **sprint 1** rather than at the Wave 1 gate: a squad with a
> measured velocity and a sized backlog can state, in week two, how many sprints the wave actually
> needs. That is the single most valuable thing a sprint model contributes to a programme in this
> position.
>
> This is **`BEA-06`**, raised in `BE-005` §12 and referred to `GV-004` §7.2's options, `GV-006`'s
> descope hierarchy and `GV-007` §9.2's re-estimation triggers. *(A second identifier, `BEA-18`, was
> allocated to this same finding at first issue and is **retired, never reissued** under `RG-02` —
> audit finding `BEA-22`.)*

---

## 7. Planning, Commitment and Capacity Allowances

### 7.1 Definition of Ready

`RQ-008` §4.3 sets the Definition of Ready. This document adds only the sprint-entry rule.

| # | Rule |
|---|---|
| **`SPR-26`** | A story enters a sprint only if it meets `RQ-008` §4.3, is sized ≤ 8, has no unresolved external dependency, and its acceptance criteria are in Given/When/Then form |
| **`SPR-27`** | **`RQA-25` is a live blocker**: 237 of 255 existing acceptance criteria are run-on prose that cannot be decomposed. Converting them is refinement work and is **sized**, not absorbed |
| **`SPR-28`** | A story that is not Ready is not negotiated into the sprint. It goes back to refinement, and the gap is recorded as an impediment |

### 7.2 Standing capacity allowances

The 0.78 delivery factor in `GV-004` covers general non-delivery time. Four draws on a sprint are
large enough here to be reserved explicitly rather than hidden inside it.

| Allowance | Reserve | Basis |
|---|---:|---|
| **Code review** | **15%** in W1–W2, 10% thereafter | `BE-003` §6.4 — with 3 FTE the reviewer pool for any change is two, and R3 review comes from outside the build team |
| **Dependency and security updates** | **5%** | `BE-007` `LX-10`'s fixed monthly batch |
| **Technical debt repayment** | **10%** | `BE-009` `DBT-08`'s standing allocation |
| **Support and defect response** | **10%** from the first go-live | Rising through the waves as live surface grows |
| **Total reserved** | **25% W1–W2 · 35% from first go-live** | |

| # | Rule |
|---|---|
| **`SPR-29`** | Reserved capacity is **removed before commitment**, not deducted after a shortfall. A sprint that commits 100% and delivers 70% teaches the team that commitments are fiction |
| **`SPR-30`** | An allowance that is not consumed is **not backfilled with feature work mid-sprint**. Unused review capacity in a sprint is a signal that review is not happening |

### 7.3 The business-side draw

`GV-007` §7.5 sizes the business-side commitment nobody has planned: **134–201 super-users**, at 30%
during UAT — **40–60 FTE-equivalents concentrated in UAT windows** — plus 11 category business owners
at 20%, roughly 3.3% of each owner's time per module.

| # | Rule |
|---|---|
| **`SPR-31`** | Every sprint that requires business-owner acceptance (`SD-11`) or super-user validation books that time **in the sprint plan**, with a named person. A sprint that ends with an unaccepted increment has not finished |
| **`SPR-32`** | Business-side unavailability is a **first-class impediment**, reported like any other. `CON-12` and `RSK-001` both state that UAT capacity, not developer capacity, paces the programme |

### 7.4 Commitment

| # | Rule |
|---|---|
| **`SPR-33`** | The squad commits; nobody commits on its behalf |
| **`SPR-34`** | The commitment is bounded by **measured velocity minus reserved capacity**, using the lower of the last three sprints while a squad is calibrating (`SPR-25`) |
| **`SPR-35`** | **Scope does not enter a sprint after it starts**, except by removing an equivalent amount. The exception is a P1 production incident, which is not sprint work |
| **`SPR-36`** | Carry-over is **re-estimated, not carried at its original size**. A story that was 5 and is half done is not 2.5; it is re-sized |
| **`SPR-37`** | Carry-over above 20% of committed points for two consecutive sprints triggers a review of the Definition of Ready, not of the team |

---

## 8. When It Does Not Fit

The section this programme will use most.

### 8.1 Within a sprint

| Step | Action |
|:--:|---|
| 1 | The squad states the shortfall **at the daily scrum on which it becomes visible**, not at the review |
| 2 | Stories are removed from the sprint, lowest business priority first, by the product owner |
| 3 | The sprint is **not extended** and its end date does not move |
| 4 | The removal is recorded with its reason; the reasons are reviewed in the retrospective |

### 8.2 Within a wave

| Step | Action | Owner |
|:--:|---|---|
| 1 | After **three** sprints, project the wave's remaining scope at measured velocity | Engineering Lead |
| 2 | If the projection exceeds the wave's remaining sprints, escalate **immediately** — not at the gate | Engineering Lead → Programme Director |
| 3 | Present three options with quantified consequences: extend the wave · reduce wave scope · add capacity (`GV-007` §8.3: **10–16 weeks** hiring lead time for the scarcest roles) | Programme Director |
| 4 | Decide at the Steering Committee; record as a `D-nnn` in `GV-003` and a `CR-nnn` if scope moves | Steering |

| # | Rule |
|---|---|
| **`SPR-38`** | **The three-sprint projection is mandatory and is a wave-gate evidence item.** A wave that reaches its gate with a shortfall that was projectable in sprint 3 is a governance failure, not a delivery failure |
| **`SPR-39`** | Adding capacity is rarely the answer inside a wave. `GV-007` §8.3's 10–16 week lead time means a hire decided in sprint 3 of a 9-sprint wave arrives after the gate |

### 8.3 Descope

`GV-006` §7 publishes the descope hierarchy **before it is needed**, precisely so that a descope under
pressure is not decided by whoever argues hardest (`GV-006-D-05`).

| # | Rule |
|---|---|
| **`SPR-40`** | Descope follows `GV-006` §7's published hierarchy. This document does not create a second one |
| **`SPR-41`** | Statutory and regulatory scope — Mushak, TDS, PDPA, BEFTN, payroll compliance — is **never** descoped by a sprint or wave decision. It is descoped, if at all, by the Board against a stated legal position |
| **`SPR-42`** | A descoped item returns to the backlog with its CD identifier intact (`CDR-04`) and a stated wave. Descoped work that leaves the backlog is work that silently disappears from the scope baseline — which is how the estate reached 56 modules with zero change requests (`GV-006`) |

---

## 9. Metrics

### 9.1 What is measured

| Metric | Purpose | Cadence |
|---|---|---|
| **Velocity** (points delivered) | Forecasting only | Per sprint, per squad |
| Conversion factor (points ÷ effective PW) | Programme reporting (`SPR-17`) | Rolling three sprints |
| Commitment reliability (delivered ÷ committed) | Health of estimation and the Definition of Ready | Per sprint |
| Carry-over % | `SPR-37` trigger | Per sprint |
| Wave burn-up against remaining sprints | `SPR-38` projection | Weekly |
| Ready-backlog depth in sprints | Whether refinement is keeping ahead | Weekly |
| Unallocated requirements (`SPR-11`) | Whether the planning gap is closing | Per wave gate |
| Reserved capacity actually consumed | Whether review and debt work is really happening | Per sprint |
| Business-side availability against plan | `CON-12`'s pacing constraint | Per sprint |

### 9.2 What must not be done with them

| # | Rule |
|---|---|
| **`SPR-43`** | **Velocity is never compared between squads.** Points are calibrated to a squad's own references (`SU-12`); a cross-squad comparison compares reference stories, not productivity |
| **`SPR-44`** | Velocity is never a target. A team asked to raise velocity raises estimates, and the measurement stops meaning anything within two sprints |
| **`SPR-45`** | Individual velocity is not measured. The unit of delivery is the squad |
| **`SPR-46`** | Commitment reliability is a signal about **the Definition of Ready and the estimate**, not about effort |

> **`SPR-43` and `SPR-44` are load-bearing.** This programme is 1.69× over capacity, and the pressure
> to make the number look better will be continuous. The moment velocity becomes a target it stops
> being a measurement, and §8.2's three-sprint projection — the one mechanism that surfaces a wave
> shortfall early — stops working.

---

## 10. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `BE-008-D-01` | Sprint length | (a) 1 week; (b) **2 weeks**; (c) 3–4 weeks | **(b)** | A vertical Odoo story including negative tests, Bengali content and documentation does not fit a week; a month delays the signal too long against nine gated waves | 80 sprints across the programme |
| `BE-008-D-02` | Estimation unit | Set by `RQ-008` `SU-10` — story points | Adopted | Not re-decided | This document supplies only the conversion `SU-14` deferred |
| `BE-008-D-03` | Points ↔ person-weeks | (a) Fixed programme constant; (b) **measured per squad, one-directional** | **(b)** | A fixed constant turns points into hours and re-creates the error `GV-007` §4.4 diagnosed | A provisional class-5 factor is needed for the first three sprints, and must be labelled as such |
| `BE-008-D-04` | Capacity reserves | (a) Inside the 0.78 factor; (b) **explicit reserves for review, updates, debt and support** | **(b)** | 0.78 was not derived from a review model, and `BE-003` §6.4 shows review is ~a third of W1 throughput | Commitments fall by 25–35%; they become achievable |
| `BE-008-D-05` | Backlog identifiers | (a) A new `BL-` space; (b) **derive from `BE-005`** | **(b)** | The estate's largest defect class is identifier proliferation and collision | The backlog cannot be created before `BE-005` — which is why both are `P0` and same-dated |
| `BE-008-D-06` | Decomposition timing | (a) All 331 items up front; (b) **one wave ahead** | **(b)** | ~4,600 stories written in Wave 1 would be stale by Wave 4 and would consume the wave that is already 5.87× over | Refinement is a standing commitment, not a one-off project |
| `BE-008-D-07` | Reporting the capacity position | (a) Report `GV-004`'s 0.99×; (b) **recompute against all 79 units and report 1.69×** | **(b)** | Planning a sprint against a demand figure that excludes 37 modules produces a plan that is wrong by construction | `BEA-18`; the wave plan requires re-baselining before Wave 1 starts |

---

## 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Is the Wave 1 plan re-baselined before Wave 1 starts, or does Wave 1 start against a 5.87× position (`BEA-06`)? | Steering Committee | **W0 — blocking** | Every Wave 1 sprint |
| `Q-02` | Who authors ~4,600 stories, and where is that effort budgeted (`BEA-17`)? | Programme Director | **W0** | Refinement throughput from sprint 1 |
| `Q-03` | How many squads, and along which boundary — module category, layer, or wave? | Engineering Lead | **W0** | Reference stories, velocity, `CODEOWNERS` |
| `Q-04` | Are the 1,816 unallocated requirements allocated before Wave 1, or discovered sprint by sprint (`PGD-A2-04`)? | Programme Director | **W0** | `SPR-10`; wave scope integrity |
| `Q-05` | Who converts `RQA-25`'s 237 run-on acceptance criteria, and in which wave? | QA Lead / BA | W1 | `SPR-27`; Definition of Ready |
| `Q-06` | Does the implementation vendor run its own sprints under its own model, or inside this one? | CTO / Procurement | **W0** | Velocity comparability; `SPR-43` |
| `Q-07` | Is `BE-005` `BEA-04` — no configuration effort anywhere in the estate — resolved before sizing begins? | CTO / `GV-007` | **W0 — blocking** | Every estimate in every sprint |

---

## 12. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | The estimation unit is stated and the conversion `RQ-008` `SU-14` deferred is supplied | §5.2, §5.3 |
| `AC-02` | Backlog identifiers derive from existing spaces; no new space is created | §3.1, `SPR-02` |
| `AC-03` | Sprint count reconciles to the programme schedule | §4.1, 80 sprints against 156.5 weeks |
| `AC-04` | Capacity is recomputed against the full 79-unit estate, not the 42-unit wave model | §6.1 |
| `AC-05` | Capacity reserves are explicit and removed before commitment | §7.2, `SPR-29` |
| `AC-06` | There is a defined, owned procedure for a sprint and a wave that do not fit | §8 |
| `AC-07` | Metrics carry explicit prohibitions on misuse | §9.2 |
| `AC-08` | The business-side draw is quantified and booked into sprint plans | §7.3 |

**Definition of done.** Complete when every criterion is met, three sprints have produced a measured
conversion factor replacing §5.3's provisional figure, `Q-01` has a Steering decision, `PGD-000`'s
`BE-008` row moves to ✅ with a fresh timestamped enumeration, and the approver has signed.

---

## 13. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `RQ-008` `SU-10`…`SU-14` | The unit and scale; `SU-14`'s deferral discharged in §5.2 |
| Upstream | `RQ-010` §4.2 | Story-level Definition of Done |
| Upstream | `BE-005` | The epic and feature layers; §6's capacity recomputation |
| Upstream | `BE-006` §5 | The component Definition of Done a feature must reach |
| Upstream | `GV-004` §5.2 | Wave lengths, FTE ramp, 0.78 factor, effective capacity |
| Upstream | `GV-007` §3, §7 | The estimate this document converts and tracks |
| Upstream | `GV-006` §7 | The descope hierarchy invoked by §8.3 |
| Downstream | `GV-009` | §8.2's three-sprint projection is gate evidence |
| Downstream | `GV-003` | Wave re-plans become `D-nnn` and `CR-nnn` |
| Downstream | `BE-009` | §7.2's 10% debt allowance |
| Downstream | `PE-009` | The tool must hold the §3.1 hierarchy and the §9.1 metrics |
| Lateral | `BE-003` §6.4 | Review capacity feeding §7.2's reserve |
| Lateral | `RQ-004` | Story-to-requirement traceability (`SPR-08`) |

---

## 14. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` ·
[`_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
[`BE-003`](BE-003_Git_Workflow_Branching_and_Code_Review_Standard.md) ·
[`BE-005`](BE-005_Custom_Development_CD_Master_Register.md) ·
[`BE-006`](BE-006_Component_Build_Specification_Standard.md) ·
[`BE-009`](BE-009_Technical_Debt_Register_and_Refactoring_Policy.md) ·
`../01_Requirements_Engineering/RQ-008_Use_Case_and_User_Story_Specification.md` ·
`../01_Requirements_Engineering/RQ-010_Acceptance_Criteria_and_Definition_of_Done_Standard.md` ·
`../00_Programme_Governance_and_Control/GV-004_Integrated_Programme_Plan_and_Master_Schedule.md` ·
`../00_Programme_Governance_and_Control/GV-006_Scope_Management_and_Baseline_Control_Procedure.md` ·
`../00_Programme_Governance_and_Control/GV-007_Estimation_Model_and_Resource_Plan.md` ·
`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md`

**Workspace**
`../../old-primary-doc/1000FiX_ERP_Missing_Implementation_Documents.md` §3 Document 5 ·
`../../../AGENTS.md` §"Testing Instructions" ·
`../../1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md` §16.2 ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` §4

**External standards** *(all verified 2026-08-18)*
Scrum Guide 2020 · PMBOK 7 — agile performance domain ·
ISO 21502:2020 §7 — integrated planning and control ·
AACE 17R-97 — cost estimate classification *(applied by `GV-007`)*

---

## 15. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Sprint shape and 80-sprint schedule, four-level backlog on existing identifier spaces, the points-to-person-weeks conversion `RQ-008` deferred, explicit capacity reserves, the recomputed 1.69× capacity position, and the not-fitting procedure. Raises `BEA-17`; corroborates `BEA-06` | *(unsigned — no constituted body, `PGD-A1-09`)* |

---

*`BE-008` · Category 07 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
