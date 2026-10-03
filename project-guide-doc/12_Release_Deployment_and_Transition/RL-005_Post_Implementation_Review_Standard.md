---
id: RL-005
title: Post-Implementation Review Standard
category: 12 — Release, Deployment & Transition
code: RL
project: 1000FiX ERP System v2.0
version: 1.1
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Management Office
approver: Programme Director, endorsed by the ERP Steering Committee
standards_basis: >
  ISO 21502:2020 §7.10 (managing lessons) and §6.6 (closing a project or phase) ·
  PRINCE2 7th Edition (2023) — End Stage Report, Lessons Log, Lessons Report ·
  PMBOK Guide 7th Edition — Measurement performance domain and retrospectives ·
  ISO 9001:2015 §9.3 management review and §10.2 nonconformity and corrective action ·
  AACE International RP 17R-97 (cost estimate classification) applied to estimate-accuracy reporting
traces_to: >
  PGD-000 RL-005 row (⬜) · 06-01 §8 (benefits realisation review, Month 42) ·
  06-02 §6 (benefit tracking discipline) · GV-007 §4, §8 (834 / 1,513 / 1,842 / 3,022 PW) ·
  GV-007 EM-03 (re-estimate at every scope baseline change) · QA-010 §7 (escape analysis) ·
  OP-002 §4.8 HX-01…HX-18 and §4.11 · RQ-010 (E-8 criteria) · BM-004 ◐ · BM-005 ⬜ ·
  RL-001 RMP-11, RMP-M1…M7 · RL-004 RLO-23, RLO-27
depends_on: >
  RL-001, RL-002, RL-003, RL-004 (issued) · GV-007, GV-009 (issued) · QA-010 (issued) ·
  OP-002 (content, issued) · BM-002 KPI Baseline Measurement Report (ABSENT ⛔) ·
  BM-004 Benefits Realisation Plan (ABSENT ◐) · BM-005 Lessons Learned Register (ABSENT ⬜) ·
  SV-005 Hypercare & Transition-to-Support (ISSUED 2026-08-19) · CH-004, CH-005 (ISSUED 2026-08-19)
verified_on: 2026-08-19
enumeration_timestamp: 2026-08-19 01:40 (+06)
rule_prefix: PIR — verified unused across all 777 markdown files of the workspace, re-verified at audit 2026-08-19 02:10 (+06)
priority: P2
needed_by: W2
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# RL-005 — Post-Implementation Review Standard

### Category 12 · Code `RL` · Rule space `PIR` · ISO 21502:2020 §7.10 · PRINCE2 7 Lessons · ISO 9001:2015 §9.3

---

> **`PGD-000` records this document as ⬜ with the note:** *"Without it, nine waves repeat the same
> mistakes nine times. **Estimate accuracy in particular is the only defence against the
> 834-vs-1,513 PW problem recurring.**"*
>
> That sentence is the specification, and §5 is written to it. The register understates the figure
> by one degree: `GV-007` records **four** effort figures, not two, and the widest ratio between
> them is **4.7×**.

---

## 1. Purpose

Nine waves over thirty-six months is nine chances to learn the same lesson. This standard states
**what is reviewed after each wave, when, by whom, against what evidence, and — the part that
decides whether a review is worth holding — where each lesson has to land before it counts as
learned.**

Its central measurement is **estimate accuracy**, because that is the one number that, tracked
honestly from Wave 1, would have surfaced the programme's largest known variance before it became a
4.7× ratio rather than after.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | **Three artefacts called "PIR"**, disambiguated from the other side of `RMP-11` (§3.2) |
| 2 | **Timing** — why the review is after hypercare exit and not at the gate, derived (§4) |
| 3 | **Estimate accuracy** — the measurement, its denominators, and the four-figure problem (§5) |
| 4 | **Defect escape** — the seam with `QA-010` §7 (§6) |
| 5 | **Benefits achieved** — what a wave PIR can and cannot claim (§7) |
| 6 | **Delivery and rollout performance** — including `RL-004`'s rate (§8) |
| 7 | **The lesson lifecycle** — and the rule that a lesson must have a landing site (§9) |
| 8 | **The review itself** — participants, agenda, duration, and what it produces (§10) |
| 9 | **The programme PIR at Month 42**, and how it differs from the nine (§11) |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Post-**incident** review | `OP-016`, `SP-031` §8 | §3.2. A different artefact with a different trigger |
| Post-implementation review **of a change** | `M66` `CD-163`, `AC-12` | §3.2. Per change, owned by the Change Manager |
| The wave **gate** decision and its report | `GV-009` §6 | A gate decides the next wave; a PIR reviews the last one |
| Hypercare **exit** criteria and the exit form | `OP-002` §4.8, §4.9 | Consumed as the PIR's entry condition (§4.2), not restated |
| The benefits **plan**, ownership and realisation curve | `BM-004` ◐, `06-02` §3, §6 | §7 measures against them; it does not set them |
| The lessons **register** itself | `BM-005` ⬜ | §9 defines what a lesson must contain and where it lands; `BM-005` holds them |
| The estimation **model** and its assumptions | `GV-007` | §5 measures actuals against it; `EM-03` already requires re-estimation |
| KPI baselines | `BM-002` ⛔ | §7.3 records what their absence costs |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| Programme Management Office | The whole document. The PMO runs the review |
| Programme Manager | §5 estimate accuracy; §10 the review itself |
| Head of Quality Engineering | §6 — the escape-analysis seam |
| Benefit owners (`06-02` §3.5) | §7 — what may be claimed at a wave PIR and what may not |
| Change Lead and Branch Operations Lead | §8 — rollout rate actual versus `RL-004`'s derived rate |
| Steering Committee | §9.4 — the lessons that require a decision they alone can take |
| Estimators and the vendor | §5.4 — the accuracy record that calibrates the next wave's estimate |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO 21502:2020** | **§7.10** managing lessons; **§6.6** closing a project or phase | §9's lesson lifecycle is §7.10's *identify → record → analyse → apply*, with the fourth step made enforceable by `PIR-19` | **Departure:** ISO 21502 places lessons capture at phase close. §4 places it after **hypercare exit**, which is later — the reason is derived in §4.1 |
| **PRINCE2 7 (2023)** | End Stage Report; Lessons Log; Lessons Report | §10's review produces the equivalent of an End Stage Report; §9's register is the Lessons Log | PRINCE2 places the End Stage Assessment at the stage boundary, which here is the wave gate. §4.3 explains why the PIR follows it rather than being it |
| **PMBOK Guide 7th Edition** | Measurement performance domain; retrospectives | §5, §6 and §8 are measurement; §10's conduct is a retrospective with a fixed agenda | None |
| **ISO 9001:2015** | **§9.3** management review; **§10.2** nonconformity and corrective action | §9's landing-site rule is §10.2's *"take action to control and correct it"* made specific | None |
| **AACE RP 17R-97** | Cost estimate classification; expected accuracy ranges by class | §5.3 reports estimate accuracy **against a declared class**, so a −20%/+30% variance on a Class 4 estimate is read as expected rather than as failure | Adopted as the reporting frame only. `GV-007` owns the estimating method |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `06-01` §8 | The milestone schedule, and **"Benefits realisation review — Month 42"** |
| `06-02` §6 | Benefit tracking discipline: baseline before the wave; monthly dashboard; quarterly Steering review; attribution discipline; **"full benefits audit at Month 42"**; honest reporting |
| `06-02` §3.2 | The benefit realisation curve — Y1 45, Y2 310, Y3 645, Y4 876, Y5 920 (BDT lac cumulative) |
| **`GV-007` §4, §8** | **Four effort figures**: 834 PW approved, 1,513 PW counted at 65 module files, 1,842 PW at 79 files including portals, 3,022 PW programme total expected (band 2,537–3,931). Ratios to the approved figure: **2.2×, 3.0×, 3.6×, 4.7×** |
| `GV-007` `EM-03` | *"Re-estimate at every scope baseline change"* — the control whose absence produced the four figures |
| `QA-010` §7 | Escape analysis, triggered by `DMG-T9` (> 3 reopens in a window) |
| `OP-002` §4.8, §4.11 | Eighteen `HX` exit criteria; **"what hypercare must produce for the next wave"** |
| `RQ-010` | `E-8` acceptance criteria confirmed post-implementation |
| `RL-001` §12.1 | `RMP-M1`…`RMP-M7` release metrics |
| `RL-004` §7 | The derived rollout rate — 2–3 sites/week — and `RLA-07`'s elapsed-time consequence |
| `CH-004` | Adoption measurement, metrics and intervention triggers |

### 2.3 Register gaps and audit findings this document closes or raises

| Finding | Source | Position |
|---|---|---|
| `RL-005` ⬜ | `PGD-000` | Closed in specification |
| Three artefacts abbreviated "PIR" | `RL-001` `RMP-11` | Closed from both sides. §3.2 |
| Estimate accuracy has never been measured | This document, §5 | The measurement, its four denominators and its reporting form are defined |
| `BM-005` (Lessons Learned Register) is ⬜ | `PGD-000` | §9 defines what it must hold; **it cannot be populated until `BM-005` exists.** Raised as `Q-02` |
| `BM-002` (KPI Baseline Measurement Report) is ⛔ and needed **Now** | `PGD-000` | **New finding `RLA-09`.** `06-02` §6 states *"a KPI without a baseline cannot claim a benefit."* `BM-002` is absent, so **no wave PIR before it issues can claim any benefit at all** — §7.3 |
| `RL-004` `RLA-07` — rollout outlasts its wave | `RL-004` §7.6 | §8.2 makes rollout-rate variance a standing PIR measure so the error is detected at W2, not at W5 |

### 2.4 The rule space

Rules carry the prefix **`PIR`**, verified at **zero** occurrences across all markdown files of the
workspace before allocation, re-verified at 2026-08-19 01:40 (+06).

> **`PIR` is used here as a rule prefix and as the abbreviation §3.2 disambiguates. That is
> deliberate and it is safe**: rule identifiers are always `PIR-nn` with a number, and the
> abbreviation never carries one. Where ambiguity is possible in prose, this document writes
> *"wave review"* rather than *"PIR"*.

---

## 3. What a Post-Implementation Review Is

### 3.1 The definition

> **`PIR-01`. A post-implementation review asks one question: *did this wave deliver what it
> promised, at the cost and in the time it promised, and what does that tell us about the next
> one?*** It is not a retrospective on team process, not a defect review and not a gate.

### 3.2 Three artefacts, one abbreviation

`RL-001` `RMP-11` records this from the release side. Recorded here from the review side, because
this is the document a reader will reach when they search for "PIR".

| Artefact | Trigger | Scope | Owner | Cadence |
|---|---|---|---|:--:|
| **Post-incident review** (`OP-016`, `SP-031` §8, `OP-002` `HX-17`) | Every `Sev1`/`Sev2` incident; every rollback (`RB-04`) | One incident | Incident Commander | Per incident, within 5 working days |
| **Change review** (`M66` `CD-163`, `AC-12`) | Every emergency, failed or major change | One change | Change Manager | Per change |
| **Wave review — this document** | Hypercare exit | One wave | **PMO** | **Nine times, plus Month 42** |

| # | Rule |
|---|---|
| **`PIR-02`** | In Category 12 the unqualified term **"PIR" means this document's wave review**. An incident review is written *"post-incident review"*; a change review is written *"change review"* |
| **`PIR-03`** | The three **feed each other and are never merged.** A wave review consumes the wave's post-incident reviews (§6.2) and its failed-change reviews (§8.1) as inputs; it does not repeat them |

### 3.3 What a wave review measures

Six measurement areas. Each has a number, a source and a comparison; none is an opinion.

| # | Area | Question | § |
|:--:|---|---|:--:|
| **`A1`** | **Estimate accuracy** | What did it cost against what we said it would? | 5 |
| **`A2`** | **Defect escape** | What reached production that testing should have caught? | 6 |
| **`A3`** | **Benefits** | Which KPIs moved, against which baselines? | 7 |
| **`A4`** | **Delivery and rollout performance** | Did it land when and how it was planned to? | 8 |
| **`A5`** | **Operational transition** | Did it hand over to support cleanly? | 8.3 |
| **`A6`** | **Assessment accuracy** | Did the readiness assessment predict what actually happened? | 8.4 |

> **`PIR-04`. `A6` is the measure that keeps every other instrument honest.** `RL-003` produces
> seven readiness statuses before every go-live. If a dimension was GREEN and the wave then failed
> on exactly that dimension, the instrument is miscalibrated, and nothing else in this estate will
> detect that.

---

## 4. Timing

### 4.1 The derivation

Three candidate moments exist, and the estate points at two of them.

| Candidate | Argument for | Why it is wrong |
|---|---|---|
| **At the wave gate** | It is when the Steering Committee is assembled and `GV-009` §6.2 already reports cost and benefit | The wave has been in production for days, not months. `06-02` §3.2's curve puts Year 1 benefit at **45 BDT lac against a Year 4 run rate of 876** — 5% — so a benefit measured at the gate measures noise |
| **At hypercare exit** | `OP-002` `HD-02` guarantees **one full instance of every business cycle** the wave touches has completed inside hypercare — month-end, payroll, settlement, statutory filing | — |
| At +6 months | Benefits are visible | Too late to change the next wave, which started at the gate |

> **`PIR-05`. The wave review is held within **10 working days of hypercare exit**.** The derivation
> is `HD-02`'s: hypercare cannot exit until one full instance of every business cycle the wave
> touches has completed inside it. **That is the earliest moment at which a wave's finance,
> payroll, settlement and statutory behaviour have each been exercised once in production**, and a
> review held before it is reviewing a system that has not yet done its job.

### 4.2 Entry condition

| # | Rule |
|---|---|
| **`PIR-06`** | The wave review's entry condition is a **signed `OP-002` §4.9 hypercare exit form**. A review held during hypercare is measuring a decaying population and will read it as a level (`RMP-29`'s reasoning, applied to measurement rather than release) |
| **`PIR-07`** | Where hypercare is **extended** beyond 150% of its baseline (`HD-04`), the review is held at the extension decision **as well as** at exit. An extension of that size means something failed before go-live rather than during it, and that is precisely a wave-review finding arriving early |

### 4.3 The relationship with the wave gate

| | Wave gate (`GV-009`) | Wave review (this document) |
|---|---|---|
| When | At the milestone | **Hypercare exit + ≤ 10 working days** |
| Decides | Next wave's scope and funding | **Nothing.** It measures and it produces lessons |
| Authority | ERP Steering Committee | PMO convenes; Programme Director owns the output |
| Looks | Forward | **Backward, for the benefit of forward** |
| Output | Gate decision, `D-nnn` in `GV-003` | Wave review report; lessons in `BM-005`; landing-site actions |

> **`PIR-08`. The gate precedes the review, and this is a known cost.** By the time a wave's review
> is held, the next wave is already scoped and funded. **The review therefore changes wave *n+2*,
> not wave *n+1*** — except through §9.4's escalation route, which exists for exactly the lessons
> that cannot wait a wave. This is stated plainly because a reader who assumes otherwise will be
> surprised, and because `RQ-010` already records the tension: *"otherwise every wave gate waits for
> a quarter of production."*

### 4.4 The nine reviews and their dates

Derived from `06-01` §8 go-live months plus `OP-002` §4.3 hypercare durations.

| Wave | Go-live month | Hypercare | Earliest exit | **Wave review** |
|:--:|:--:|:--:|:--:|:--:|
| W1 | 4 | 8 weeks | ~M6 | **~M6** |
| W2 | 8 | 6 weeks | ~M9.5 | **~M9.5** — but see `RLO-27` |
| W3 | 13 | 8 weeks | ~M15 | **~M15** |
| W4 | 18 | 6 weeks | ~M19.5 | **~M19.5** |
| W5 | 22 | 8 weeks | ~M24 | **~M24** |
| W6 | 26 | 4 weeks | ~M27 | **~M27** |
| W7 | 30 | 6 weeks | ~M31.5 | **~M31.5** |
| W8 | 34 | 4 weeks | ~M35 | **~M35** |
| W9 | 36 | 6 weeks | ~M37.5 | **~M37.5** |
| — | — | — | — | **Programme review — M42** (§11) |

> **`PIR-09`.** These dates are **earliest**, not planned. `HD-01` makes hypercare duration a
> minimum and exit criterion-driven; `RL-004` `RLO-27` records that with a tranched rollout the
> wave clock runs from the **last** tranche, which moves W2's exit — and therefore its review —
> materially later than the table shows. The table is a floor and is labelled as one.

---

## 5. `A1` — Estimate Accuracy

### 5.1 Why this is the flagship measure

`PGD-000` names it: *"the only defence against the 834-vs-1,513 PW problem recurring."*

`GV-007` records not two figures but **four**, all describing the same programme's build effort:

| Figure | Source | Basis | Ratio to approved |
|---:|---|---|:--:|
| **834 PW** | Approved business case | 30 modules, estimated | 1.0× |
| **1,513 PW** | `00-07` `H2-08` | **65 module files, counted** | **2.0×** *(build alone: 1.8×)* |
| **1,842 PW** | `GV-007` §8 | **79 files** including 12 portals, counted | **2.2×** |
| **3,022 PW** | `GV-007` §8 | **Programme total expected**, band 2,537–3,931 | **3.6×** *(band 3.0× – 4.7×)* |

> **`PIR-10`. The problem is not that the estimate was wrong. It is that nothing measured it being
> wrong.** `GV-007` `EM-03` — *"re-estimate at every scope baseline change"* — is the preventive
> control and it was not operating while scope moved 11 → 30 → 67 modules against one 834 PW model.
> This section is the **detective** control that would have raised it at Wave 1.

### 5.2 What is measured

> **`PIR-11`. Estimate accuracy is measured per wave, at three levels, and each level names its
> denominator.**

| # | Level | Numerator | Denominator | Reported as |
|:--:|---|---|---|---|
| `EA-1` | **Wave effort** | Actual person-weeks consumed in the wave | The wave's effort estimate **at wave scope lock** (`GV-006` §6.3) | Variance %, signed |
| `EA-2` | **Component effort** | Actual PW per delivered component (`BE-005` `CD-<UNIT>-<nn>`) | The component's estimate at lock | Distribution, not a mean |
| `EA-3` | **Scope drift** | Components delivered in the wave | Components in the locked wave scope | Count added, count removed, count deferred |

| # | Rule |
|---|---|
| **`PIR-12`** | **The denominator is the estimate at wave scope lock, not the original business case and not the latest re-estimate.** `GA-04`'s discipline — *a percentage carries its denominator* — is why four PW figures coexist in this estate, and it is the failure this measure exists to prevent |
| **`PIR-13`** | `EA-2` is reported as a **distribution with its spread**, never as a mean. A wave in which half the components came in at 50% and half at 200% has a mean of 125% and a problem the mean conceals — the `PGD-A2-24` / `QAA-12` defect class |
| **`PIR-14`** | `EA-3` reports **added, removed and deferred separately**. A net-zero scope change with 12 components added and 12 removed is not a stable scope |

### 5.3 Reporting against an estimate class

AACE RP 17R-97 classifies estimates and gives each an expected accuracy range. An estimate made at
concept stage is not wrong because it moved; it is wrong if it moved outside its class's range.

| # | Rule |
|---|---|
| **`PIR-15`** | Every estimate entering `EA-1` or `EA-2` carries its **class** and the class's declared accuracy range. A variance inside the range is reported as **conforming**; outside it, as a **miss** |
| **`PIR-16`** | **The 834 PW figure is a concept-class estimate against a scope that has since tripled in module count.** Reporting the 3.6× ratio as an "overrun" against it is not an accuracy finding — it is a scope finding, and `GV-006` owns it. §5.4's table keeps the two separate |

### 5.4 The accuracy record

Maintained cumulatively across the nine reviews. **This table is the document's most durable
output.**

| Wave | Estimate at lock (PW) | Class | Actual (PW) | `EA-1` variance | Inside class range? | Scope added / removed / deferred |
|:--:|---:|:--:|---:|---:|:--:|---|
| W1 | *(to be recorded)* | | | | | |
| W2 | | | | | | |
| … | | | | | | |
| W9 | | | | | | |

| # | Rule |
|---|---|
| **`PIR-17`** | **From W2 onward, the next wave's estimate is calibrated against the accuracy record**, and the calibration factor applied is stated in `GV-007`'s re-estimate. An estimating model that never learns from its own record is the model that produced four figures |
| **`PIR-18`** | Where two consecutive waves miss their class range in the **same direction**, the estimating method is reviewed, not the estimate. `DMG-T9`'s logic — *"three recurrences in one window is a process signal, not three coincidences"* — applied to estimating |

---

## 6. `A2` — Defect Escape

### 6.1 The measure

| # | Measure | Definition | Source |
|:--:|---|---|---|
| `DE-1` | **Escape count** | Defects found in production during hypercare that were in scope for a test level executed before go-live | Defect register + `QA-011` coverage |
| `DE-2` | **Escape rate** | `DE-1` ÷ total defects found in the wave | Defect register |
| `DE-3` | **Escape by level** | Which of `QA-001`'s thirteen levels should have caught each escape | `QA-001` §4 |
| `DE-4` | **`RC-A` escapes** | Escapes on an `RC-A` population | `QA-001` §5.4 — **target zero** |

### 6.2 The seam with `QA-010` §7

`QA-010` §7 already owns **escape analysis**, triggered by `DMG-T9` (more than three reopens in a
gate window).

> **`PIR-19`. This document does not perform escape analysis; it consumes `QA-010`'s.** What it adds
> is the **wave-level aggregation** `QA-010` does not do: `DE-3`'s distribution across thirteen test
> levels, tracked across nine waves, is what shows a level that is systematically under-testing —
> and no single escape analysis can see that.

| # | Rule |
|---|---|
| **`PIR-20`** | Every `Sev1`/`Sev2` post-incident review in the wave (`OP-016`) is an input to `DE-1`. The wave review reads them; it does not re-hold them (`PIR-03`) |
| **`PIR-21`** | **`DE-4` is reported even when it is zero**, with the scope it was measured over. `GA-06`: *"zero findings from a test that did not run is not zero findings"* |

---

## 7. `A3` — Benefits

### 7.1 What a wave review may claim

`06-02` §6 sets the discipline and this document adds nothing to it except restraint.

| # | Rule |
|---|---|
| **`PIR-22`** | A benefit is claimed only where **(a)** the KPI has a signed baseline captured **before** the wave began, **(b)** the movement is measured from the system, and **(c)** a **causal mechanism is documented** (`06-02` §6 attribution discipline) |
| **`PIR-23`** | **`06-02` §3.2's curve puts Year 1 cumulative benefit at 45 BDT lac against a Year 4 run rate of 876 — about 5%.** A wave review in Year 1 that reports a large benefit is reporting a measurement error, and this rule exists so it is read that way |
| **`PIR-24`** | **Missed benefits are reported as missed, with the reason** (`06-02` §6, verbatim). A wave review that reports only realised benefits is not a review |

### 7.2 What it may not claim

| # | Rule |
|---|---|
| **`PIR-25`** | A wave review does **not** re-forecast the benefit case. `BM-003`/`BM-004` own the forecast; a review that adjusts the forecast to match the actual has removed the variance it exists to expose |
| **`PIR-26`** | General market growth, seasonal variation and price change are **excluded** from attribution (`06-02` §6) |

### 7.3 The blocker: `BM-002` does not exist

`06-02` §6 is unambiguous: *"Every KPI's baseline is measured and signed off **before** the relevant
wave begins. **A KPI without a baseline cannot claim a benefit.**"*

`BM-002` (KPI Baseline Measurement Report) is **⛔** in `PGD-000` and registered `needed_by: Now`.

> **`PIR-27`. Until `BM-002` issues, no wave review can claim any benefit at all.** Not a reduced
> benefit, not a provisional one — none, because `06-02` §6's rule is a precondition rather than a
> quality standard. **`A3` is therefore reported as *"not claimable — no baseline"* at every review
> held before `BM-002` exists**, and that statement is itself the finding.
>
> Recorded as `RLA-09`. It is raised as `Q-01` and escalated to `GV-005`, because `BM-002` is needed
> **before W1 begins** and every month it slips permanently forecloses a wave's benefit claim —
> a baseline cannot be captured retrospectively once the system that would change it is live.

---

## 8. `A4`–`A6` — Delivery, Transition and Assessment

### 8.1 `A4` Delivery and rollout performance

| # | Measure | Source | Comparison |
|:--:|---|---|---|
| `DP-1` | Wave delivered on its `06-01` §8 milestone month | `GV-004` | Planned vs actual, in weeks |
| `DP-2` | **Rollout rate achieved**, sites per week | `RL-004` §7 | Against `RLO-23`'s derived 2–3/week |
| `DP-3` | **Floor-walker hours actually consumed per site** | `OP-002` `FW-01` tickets | Against §7.3's ratio-derived estimate |
| `DP-4` | Sites failing `C2`, by domain | `CM-012` §4.6 dashboard | Trend across waves |
| `DP-5` | Release metrics `RMP-M1`…`RMP-M7` | `RL-001` §12 | Baseline at W1–W4; target from `G4` |
| `DP-6` | Failed and emergency changes in the wave | `RMP-M3`, `RMP-M6` | Against `RMP-M6`'s < 10% |
| `DP-7` | Deployments aborted, and at which `DA-n` trigger | `RL-002` §9.2 | Trend |

> **`PIR-28`. `DP-2` and `DP-3` are the two measures that close `RL-004`'s largest open question.**
> `RLO-23`'s rate of 2–3 sites per week is **derived from ratios, not measured**, and `RLO-25`
> requires it to be recomputed after the pilot. The W1 review is where that recomputation is
> recorded, and it is the earliest moment at which `RLA-07` — the rollout outlasting its wave —
> becomes a fact rather than a projection.

### 8.2 `A5` Operational transition

| # | Measure | Source |
|:--:|---|---|
| `OT-1` | Hypercare duration actual vs `OP-002` §4.3 baseline | Hypercare exit form |
| `OT-2` | `HX` criteria waived, and which (`HX-01`, `09`, `12`, `17` are **not waivable**) | Exit form |
| `OT-3` | Known issues handed to BAU, open at exit | `OP-002` §4.6 log |
| `OT-4` | Runbooks changed by what hypercare taught | `HX-14` |
| `OT-5` | Support contact volume at exit vs modelled BAU | `HX-06` |
| `OT-6` | Adoption at exit, per role and site | `HX-08`; `CH-004` |

> **`PIR-29`** — `OP-002` §4.11 already specifies *"what hypercare must produce for the next wave"*.
> The wave review is where that production is **checked**, and an unproduced item is a lesson with
> an owner rather than an observation.

### 8.3 `A6` Assessment accuracy

> **`PIR-30`. For each of `RL-003`'s seven dimensions, the review records the status assessed before
> go-live and what actually happened.** Four outcomes:

| Assessed | Outcome | Reading |
|---|---|---|
| GREEN | No related failure | Correct |
| GREEN | **Related failure occurred** | **False negative — the instrument missed it.** The dimension's evidence set is reviewed |
| AMBER / RED | Related failure occurred | Correct; the remediation was insufficient or too late |
| AMBER / RED | No related failure | **False positive** — tolerable, but a pattern of them teaches assessors that RED is cheap |

| # | Rule |
|---|---|
| **`PIR-31`** | A **false negative on `RD-2`, `RD-4` or `RD-7`** — the programme-wide veto dimensions — triggers a mandatory review of that dimension's evidence set in `RL-003` §5 before the next go-live. These are the three that stop `C7`, and a veto that does not fire when it should is worse than no veto |
| **`PIR-32`** | Assessment accuracy is reported **per assessor role**, not per person. The purpose is to calibrate the instrument, and naming individuals converts a calibration exercise into a performance review — after which every assessor records AMBER |

---

## 9. The Lesson Lifecycle

### 9.1 What a lesson is

> **`PIR-33`. A lesson is not an observation. A lesson has five parts, and a record missing any of
> them is a note.**

| # | Part | Test |
|:--:|---|---|
| 1 | **What happened** | Stated as an event with a date, not as a theme |
| 2 | **Why it happened** | A cause, not a restatement of the event |
| 3 | **What it cost** | Effort, time, money, adoption or exposure — quantified where it can be |
| 4 | **What must change** | A specific change to a named artefact, process or decision |
| 5 | **Where it lands** | **A named document, rule or register that will be amended, with an owner and a date** |

### 9.2 The landing-site rule

> **`PIR-34`. A lesson with no landing site is not recorded as a lesson.** It is recorded as an
> **open question** with an owner and a date, and it is escalated to `GV-005` if it has neither.

This is the rule the whole section exists for. A lessons register that accumulates well-written
observations changes nothing; this estate has already demonstrated the failure mode at scale, in
`RG-08`, which `PGD-000` records as *"recommended for the seventh time"* and never ratified.

| Landing site | Example |
|---|---|
| A **rule** in a guiding document | *"`RLO-24`'s default tranche is 3; W1 measured 1.6 — amend to 2"* |
| A **checklist item** | *"add `RL-002` `P-24`: confirm the site's fallback pack is physically present"* |
| An **estimate factor** | *"`GV-007` applies a 1.4× calibration to counter-staff training effort"* |
| A **decision** | *"`GV-003` `D-nnn`: fund contracted floor-walkers from W3"* |
| A **register entry** | *"`GV-005` `RSK-nnn`: connectivity in `RAN` division"* |

### 9.3 The lifecycle

| Stage | Action | Owner | Timing |
|---|---|---|---|
| **Identify** | Any participant may raise a candidate at the review | Any | At the review |
| **Qualify** | The five parts are completed, or it becomes an open question (`PIR-34`) | PMO | Within 5 working days |
| **Record** | Entered in `BM-005` with its landing site, owner and date | PMO | Within 5 working days |
| **Apply** | The landing site is amended | Named owner | By the stated date |
| **Verify** | The **next** wave review confirms the amendment was made | PMO | Next review |
| **Close** | Only after verification | PMO | Next review |

| # | Rule |
|---|---|
| **`PIR-35`** | **A lesson is closed by verification that its landing site was amended, never by the passage of time or by the review that raised it.** `ISO 9001:2015` §10.2 requires action to be *taken*, and taken is a state someone else confirms |
| **`PIR-36`** | Every wave review opens with the **previous review's unclosed lessons**, aged. An ageing list read aloud at the start of nine consecutive meetings is the cheapest enforcement mechanism available |
| **`PIR-37`** | **`BM-005` is ⬜.** Until it issues, lessons are recorded in an interim register owned by the PMO with the same five-part structure, and migrated on issue. A lesson deferred until its register exists is a lesson lost — the estate's own `MGA` findings record this pattern repeatedly |

### 9.4 Escalation — the lessons that cannot wait a wave

`PIR-08` records that a wave review normally changes wave *n+2*. Some cannot wait.

> **`PIR-38`.** A lesson is escalated to the Steering Committee **within 2 working days** of the
> review, outside the normal cycle, when any of the following holds:

| # | Condition |
|:--:|---|
| 1 | It concerns a statutory exposure, a personal-data exposure or a financial control |
| 2 | It is a **false negative on `RD-2`, `RD-4` or `RD-7`** (`PIR-31`) |
| 3 | Its landing site is a **funding or schedule decision** — as `RL-004` `Q-02` already is |
| 4 | The same lesson was raised at the **previous** review and its landing site was not amended |
| 5 | It concerns an `RC-A` escape (`DE-4` > 0) |

> **Condition 4 is the one that matters most.** A lesson raised twice is no longer a lesson about
> the wave; it is a lesson about the programme's ability to act on lessons, and that is a Steering
> Committee question.

---

## 10. The Review Itself

### 10.1 Participants

| Role | Why present | Contributes |
|---|---|---|
| **PMO** | Convenes, chairs, records | `A1`, `A4`, `A6`; the lessons |
| Programme Manager | Accountable for delivery | `A1`, `A4` |
| Head of Quality Engineering | | `A2` |
| Benefit owners for the wave's KPIs (`06-02` §3.5) | | `A3` |
| Support Lead / Service Manager | | `A5` |
| Change Lead | | `A4` rollout, `A5` adoption |
| Business owner(s) for the wave's primary modules | The people who now run on it | All |
| **At least two people who were on a branch floor** — a champion and a floor-walker | | The half of the truth no register holds |
| Vendor delivery lead | Estimate accuracy is a shared measurement | `A1` |

| # | Rule |
|---|---|
| **`PIR-39`** | **The champion and floor-walker attendance is not optional and is not a courtesy.** Every other participant experienced the wave through a report. `OP-002` `FW-01` requires every floor-walker intervention to become a ticket precisely so that this experience is countable — and the review is where the count and the experience are put next to each other |
| **`PIR-40`** | The vendor delivery lead attends `A1` and leaves before §9's lesson qualification if any lesson concerns vendor performance. `CO-003`'s acceptance process, not this review, is where vendor performance is adjudicated |

### 10.2 Agenda and duration

| # | Item | Time | Output |
|:--:|---|---|---|
| 1 | Previous review's unclosed lessons, aged (`PIR-36`) | 15 min | Verified / still open |
| 2 | `A1` estimate accuracy, with the cumulative record | 30 min | The `EA-1`…`EA-3` figures |
| 3 | `A2` defect escape, by level | 20 min | `DE-1`…`DE-4` |
| 4 | `A3` benefits, or the statement that none is claimable | 20 min | Claimed / missed / not claimable |
| 5 | `A4` delivery and rollout | 30 min | `DP-1`…`DP-7` |
| 6 | `A5` operational transition | 20 min | `OT-1`…`OT-6` |
| 7 | `A6` assessment accuracy | 20 min | Per-dimension outcome |
| 8 | Lesson identification | 45 min | Candidates |
| 9 | Escalations under `PIR-38` | 10 min | Escalation list |
| | **Total** | **~3.5 hours** | |

| # | Rule |
|---|---|
| **`PIR-41`** | **Items 2–7 are presented as numbers before item 8 opens.** A review that begins with discussion produces the lessons its most confident participant already believed |
| **`PIR-42`** | Every figure in items 2–7 is circulated **3 working days ahead**, matching `GA-10`'s gate-report discipline. A number seen for the first time in the room is a number nobody has checked |

### 10.3 The report

| Section | Content |
|---|---|
| 1 | Wave identity, scope delivered, dates, sites |
| 2 | `A1` estimate accuracy, with the cumulative record (§5.4) |
| 3 | `A2` defect escape by level, with `DE-4` stated even at zero |
| 4 | `A3` benefits claimed, missed, or **not claimable and why** |
| 5 | `A4` delivery and rollout performance |
| 6 | `A5` operational transition |
| 7 | `A6` assessment accuracy per dimension |
| 8 | **Lessons**, each with its five parts and landing site |
| 9 | Escalations under `PIR-38` |
| 10 | Previous lessons verified closed, and those still open with their age |

| # | Rule |
|---|---|
| **`PIR-43`** | The report is issued **within 10 working days** of the review and is a configuration item under `GV-011` |
| **`PIR-44`** | The report is **circulated to every branch that went live in the wave**, in summary and in Bengali. The sites that did the work are the last to hear what it showed, in every programme, unless a rule says otherwise |

---

## 11. The Programme Review — Month 42

`06-01` §8 and `06-02` §6 both place a **full benefits audit at Month 42**, six months after
programme closure at Month 36.

### 11.1 How it differs from the nine

| | Wave review | **Programme review (M42)** |
|---|---|---|
| Scope | One wave | The whole programme |
| Benefits | What can be claimed this early | **The full benefits audit** — `06-02` §3.2's curve against actual, at a point where Year 3 cumulative (645 BDT lac) is measurable |
| Estimate accuracy | One wave's variance | **The nine-wave record**, and what it says about the 834 → 3,022 PW trajectory |
| Lessons | Applied to wave *n+2* | Applied to the **next programme**, and to steady-state operation |
| Audience | PMO and delivery | **Steering Committee, Audit Committee and the Board** |
| Independence | Cross-assessment (`GA-09`) | **Independent**, per `GV-010` programme assurance |

### 11.2 What it must answer

| # | Question | Evidence |
|:--:|---|---|
| 1 | Did the programme deliver the benefit case? | `06-02` §3.2 curve vs actual; `BM-004` |
| 2 | What did it actually cost, against 834 PW and against 3,022 PW? | §5.4's cumulative record |
| 3 | Which of `06-02` §5's programme success criteria were met? | `06-02` §5 |
| 4 | Are all 48 legacy sources retired, or accounted for? | **`RL-006`**'s decommission register |
| 5 | Did the support model reach steady state? | `GV-001` §12.1; `SV-005` |
| 6 | Which lessons were raised and never landed? | `BM-005`, aged |
| 7 | Was the estimating model ever calibrated? | `PIR-17`, `PIR-18` |

> **`PIR-45`. Question 6 is the one that measures this document.** Nine wave reviews producing
> lessons that never reached a landing site would make this standard an expensive meeting series.
> The M42 review reports the **proportion of lessons verified closed**, and that proportion is the
> standard's own accuracy measure.

---

## 12. Governing Rules — Consolidated

| # | Rule | § |
|---|---|:--:|
| `PIR-01` | A wave review asks whether the wave delivered what it promised, at the cost and time promised | 3.1 |
| `PIR-02` | Unqualified "PIR" in Category 12 means the wave review | 3.2 |
| `PIR-03` | The three reviews feed each other and are never merged | 3.2 |
| `PIR-04` | `A6` assessment accuracy keeps every other instrument honest | 3.3 |
| `PIR-05` | The review is within 10 working days of hypercare exit | 4.1 |
| `PIR-06` | Entry condition is a signed hypercare exit form | 4.2 |
| `PIR-07` | A hypercare extension beyond 150% triggers a review at the extension too | 4.2 |
| `PIR-08` | The gate precedes the review; the review changes wave *n+2* | 4.3 |
| `PIR-09` | §4.4's dates are earliest, not planned | 4.4 |
| `PIR-10` | The problem was not a wrong estimate; it was that nothing measured it | 5.1 |
| `PIR-11` | Estimate accuracy is measured at three levels, each naming its denominator | 5.2 |
| `PIR-12` | The denominator is the estimate at wave scope lock | 5.2 |
| `PIR-13` | `EA-2` is a distribution with its spread, never a mean | 5.2 |
| `PIR-14` | `EA-3` reports added, removed and deferred separately | 5.2 |
| `PIR-15` | Every estimate carries its class and the class's accuracy range | 5.3 |
| `PIR-16` | The 834 PW ratio is a scope finding, not an accuracy finding | 5.3 |
| `PIR-17` | From W2, the next estimate is calibrated against the accuracy record | 5.4 |
| `PIR-18` | Two consecutive same-direction misses review the method, not the estimate | 5.4 |
| `PIR-19` | This document consumes `QA-010`'s escape analysis and aggregates it per wave | 6.2 |
| `PIR-20` | Post-incident reviews are inputs, not repeated | 6.2 |
| `PIR-21` | `DE-4` is reported even at zero, with its scope | 6.2 |
| `PIR-22` | A benefit needs a signed pre-wave baseline, a measured movement and a documented mechanism | 7.1 |
| `PIR-23` | A large Year 1 benefit is a measurement error | 7.1 |
| `PIR-24` | Missed benefits are reported as missed, with the reason | 7.1 |
| `PIR-25` | A review never re-forecasts the benefit case | 7.2 |
| `PIR-26` | Market growth, seasonality and price change are excluded from attribution | 7.2 |
| `PIR-27` | **Until `BM-002` issues, no wave review can claim any benefit at all** | 7.3 |
| `PIR-28` | `DP-2`/`DP-3` close `RL-004`'s largest open question at W1 | 8.1 |
| `PIR-29` | `OP-002` §4.11's outputs are checked at the review; an unproduced one is a lesson | 8.2 |
| `PIR-30` | Each `RL-003` dimension's assessed status is compared with what happened | 8.3 |
| `PIR-31` | A false negative on `RD-2`, `RD-4` or `RD-7` triggers an evidence-set review | 8.3 |
| `PIR-32` | Assessment accuracy is reported per role, never per person | 8.3 |
| `PIR-33` | A lesson has five parts; missing one makes it a note | 9.1 |
| `PIR-34` | **A lesson with no landing site is recorded as an open question, not a lesson** | 9.2 |
| `PIR-35` | A lesson closes on verification that its landing site was amended | 9.3 |
| `PIR-36` | Every review opens with the previous review's unclosed lessons, aged | 9.3 |
| `PIR-37` | Until `BM-005` issues, lessons go to an interim PMO register with the same structure | 9.3 |
| `PIR-38` | Five conditions escalate a lesson within 2 working days | 9.4 |
| `PIR-39` | A champion and a floor-walker attend; it is not a courtesy | 10.1 |
| `PIR-40` | The vendor lead attends `A1` and leaves before vendor-performance lessons | 10.1 |
| `PIR-41` | Numbers are presented before discussion opens | 10.2 |
| `PIR-42` | Every figure is circulated 3 working days ahead | 10.2 |
| `PIR-43` | The report issues within 10 working days and is a `GV-011` configuration item | 10.3 |
| `PIR-44` | The report is circulated to every branch that went live, in summary and in Bengali | 10.3 |
| `PIR-45` | M42's question 6 — lessons raised and never landed — measures this standard | 11.2 |

**Forty-five rules.** Counted from this table at 2026-08-19 01:40 (+06).

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **When does `BM-002` (KPI Baseline Measurement Report) issue?** Every month it slips permanently forecloses a wave's benefit claim | Programme Director with benefit owners | **Before W1 begins** | `PIR-27`; `A3` at every review |
| `Q-02` | When does `BM-005` issue, and does it adopt `PIR-33`'s five-part structure? | PMO | **W1** | `PIR-37` |
| `Q-03` | Which AACE estimate class do `GV-007`'s figures carry? None is currently labelled | Programme Manager with `GV-007`'s owner | **W1** | `PIR-15`, `PIR-16` |
| `Q-04` | Does the vendor contract oblige the vendor to supply actual effort per component for `EA-2`? | PMO with Legal Counsel | **W1** | `PIR-11` `EA-2`; `CO-003` ⛔ |
| `Q-05` | Who owns the interim lessons register before `BM-005`, and where does it live? | PMO | **W1** | `PIR-37` |
| `Q-06` | Does `GV-010` (Programme Assurance) provide the independent reviewer for M42? | Audit Committee | W8 | §11.1 |
| `Q-07` | Is the M42 review funded, given programme closure at M36? | Programme Director | **M30** | §11; a review six months after the team disbands has no participants |

---

## 14. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `RL-005-D-01` | When to hold the review | (a) At the wave gate · (b) At hypercare exit · (c) +6 months | **(b)** | `HD-02` guarantees one full instance of every business cycle has completed inside hypercare; that is the earliest honest measurement point | The review changes wave *n+2*, not *n+1* (`PIR-08`), with §9.4 as the escape route |
| `RL-005-D-02` | Estimate-accuracy denominator | (a) The 834 PW business case · (b) The latest re-estimate · (c) The estimate at wave scope lock | **(c)** | (a) measures scope growth and calls it overrun; (b) has no memory. (c) measures the estimate that was actually committed to | `EA-1` reports against a figure `GV-006` §6.3 already fixes |
| `RL-005-D-03` | Whether a lesson may be recorded without a landing site | (a) Record all observations · (b) Landing site mandatory | **(b)** | `RG-08` — *"recommended for the seventh time"* — is this estate's own demonstration that recorded-and-unactioned is the default outcome | Fewer recorded lessons, and each one is an amendment somebody owes |
| `RL-005-D-04` | Whether to report benefits before `BM-002` exists | (a) Report provisional benefits · (b) Report "not claimable — no baseline" | **(b)** | `06-02` §6 makes a baseline a precondition, not a quality standard. A provisional benefit becomes a quoted benefit within one reporting cycle | Early reviews report no benefit at all, which is the finding (`RLA-09`) |
| `RL-005-D-05` | Whether `A6` names individuals | (a) Per assessor · (b) Per assessor **role** | **(b)** | Naming individuals converts calibration into performance review, after which every assessor records AMBER | Miscalibration is attributable to a role and fixable by changing its evidence set |
| `RL-005-D-06` | Rule prefix `PIR`, which is also the abbreviation being disambiguated | (a) A different prefix to avoid any overlap · (b) `PIR-nn` with the numeric form as the discriminator | **(b)** | The prefix is verified unused; rule identifiers always carry a number and the abbreviation never does | §2.4 states the convention; prose uses *"wave review"* where ambiguity is possible |

---

## 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | The register's stated purpose — estimate accuracy as the defence against recurrence — is the document's centre | §5, six rules, a cumulative record table |
| `AC-02` | The `834`-versus-`1,513` framing is corrected to the four figures actually recorded | §5.1 — 834 / 1,513 / 1,842 / 3,022, ratios 1.0× / 2.0× / 2.2× / 3.6× |
| `AC-03` | Review timing is **derived**, not chosen | `PIR-05`, from `OP-002` `HD-02` |
| `AC-04` | The three artefacts called "PIR" are disambiguated from this side too | §3.2, `PIR-02` |
| `AC-05` | Every measurement area has numbered measures with sources and comparisons | §5–§8 — `EA`, `DE`, `A3` rules, `DP`, `OT`, `A6` |
| `AC-06` | A lesson cannot be recorded without a landing site | `PIR-34`, `RL-005-D-03` |
| `AC-07` | A lesson cannot close without verification by a later review | `PIR-35` |
| `AC-08` | The benefits blocker is stated rather than worked around | `PIR-27`, `RLA-09`, `Q-01` |
| `AC-09` | The review has an agenda, a duration and a circulation rule | §10.2, §10.3 |
| `AC-10` | The M42 programme review is specified and differentiated | §11 |
| `AC-11` | The standard states how its own effectiveness is measured | `PIR-45` |
| `AC-12` | No rule identifier collides with any existing identifier | §2.4 |

**Definition of done.** As `RL-001` §16, subject to the same `PGD-A2-25` qualification.

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `GV-007` §4, §8, `EM-03` | The four effort figures; the preventive control this document detects against |
| Upstream | `GV-009` | The gate this review follows; `GA-10`'s circulation discipline adopted at `PIR-42` |
| Upstream | `OP-002` §4.3, §4.8, §4.11 | Hypercare durations, exit criteria and required outputs |
| Upstream | `QA-010` §7 | Escape analysis, consumed and aggregated |
| Upstream | `06-02` §3.2, §5, §6 | The benefit curve, programme success criteria and tracking discipline |
| Upstream | `RL-001` §12 | `RMP-M1`…`RMP-M7` become `DP-5`, `DP-6` |
| Upstream | `RL-002` §9 | Aborts become `DP-7` |
| Upstream | `RL-003` | Seven dimension statuses become `A6` |
| Upstream | `RL-004` §7 | The derived rollout rate becomes `DP-2`/`DP-3`'s comparison |
| Downstream | `BM-005` ⬜ | Holds the lessons; `PIR-33` defines their structure |
| Downstream | `BM-004` ◐ | Consumes `A3`; owns the forecast this review does not adjust |
| Downstream | `GV-007` | Consumes §5.4's accuracy record as calibration (`PIR-17`) |
| Downstream | `GV-003` | Escalated lessons become `D-nnn` decisions |
| Downstream | `GV-005` | Unlanded lessons become risks or issues |
| Downstream | **`RL-006`** | M42 question 4 — the decommission register — is `RL-006`'s output |
| Lateral | `OP-016`, `M66` `CD-163` | The other two "PIR"s; inputs, never merged |
| Lateral | `GV-010` | Independence for the M42 review |

---

## 17. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`RL-001`](RL-001_Release_Management_and_Versioning_Policy.md) ·
[`RL-002`](RL-002_Deployment_Plan_and_Go_Live_Checklist.md) ·
[`RL-003`](RL-003_Go_Live_Readiness_Assessment_and_Gate_Criteria.md) ·
[`RL-004`](RL-004_Rollout_and_Branch_Wave_Deployment_Plan.md) ·
[`RL-006`](RL-006_Legacy_Decommissioning_Plan.md) ·
[`../00_Programme_Governance_and_Control/GV-007_Estimation_Model_and_Resource_Plan.md`](../00_Programme_Governance_and_Control/GV-007_Estimation_Model_and_Resource_Plan.md) ·
[`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md`](../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md) ·
[`../08_Quality_Engineering_and_Test/QA-010_Defect_Management_and_Quality_Gate_Standard.md`](../08_Quality_Engineering_and_Test/QA-010_Defect_Management_and_Quality_Gate_Standard.md) ·
[`../13_Training_Change_and_Adoption/CH-004_Adoption_Measurement_and_Reinforcement_Plan.md`](../13_Training_Change_and_Adoption/CH-004_Adoption_Measurement_and_Reinforcement_Plan.md)

**Workspace**
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` §8 ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` §3.2, §5, §6 ·
`../../project_content/17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md` §4.3, §4.8, §4.11 ·
`../../project_content/17_Operations_Support_and_Runbooks/OP-016_Post_Incident_Review_Template_and_Register.md` ·
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66_Internal_IT_Service_Management.md` `CD-163`, `AC-12`

**External standards** *(verified 2026-08-19)*

| Source | Edition | Used for |
|---|---|---|
| ISO 21502:2020 | Current | §7.10 lessons; §6.6 closing |
| PRINCE2 | **7th Edition (2023)** | End Stage Report; Lessons Log |
| PMBOK Guide | **7th Edition** | Measurement performance domain |
| ISO 9001:2015 | §9.3, §10.2 | `PIR-35`'s closure-by-verification |
| AACE International | **RP 17R-97** | §5.3's estimate-class reporting frame |

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| **1.1** | 2026-08-19 | Programme Management Office | **Audit refresh, `PGD-AUDIT-CAT-12`.** Dependency statuses re-verified against a re-enumerated estate (777 markdown files). `CH-004` and `CH-005` confirmed issued; **`BM-002`, `BM-004` and `BM-005` re-verified as still absent**, so `PIR-27` — no wave review may claim a benefit — stands unchanged and is the category's longest-lived open exposure | *Pending — `GV-001` `CC-01`* |
| 1.0 | 2026-08-19 | Programme Management Office | Initial issue. Forty-five `PIR` rules; six measurement areas; a five-part lesson definition with a mandatory landing site; nine wave reviews plus the M42 programme review. **Corrects the register's own framing**: `GV-007` records four effort figures, not two, with a widest ratio of 4.7×. Derives review timing from `OP-002` `HD-02` rather than choosing it. **Records that no wave review can claim any benefit until `BM-002` issues** (`RLA-09`), and that a baseline cannot be captured retrospectively | *Pending — `GV-001` `CC-01`* |

---

*`RL-005` · Category 12 · Rule space `PIR` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
