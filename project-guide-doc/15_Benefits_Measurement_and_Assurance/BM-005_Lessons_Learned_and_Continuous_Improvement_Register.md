---
id: BM-005
title: Lessons Learned and Continuous Improvement Register
category: 15 — Benefits, Measurement & Assurance
code: BM
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Management Office, under the Programme Director
approver: ERP Steering Committee, with the Head of Internal Audit consulted
standards_basis: >
  ISO 9001:2015 §10.2 (nonconformity and corrective action) and §9.3 (management review) ·
  PRINCE2 7 (lessons: the Learn from Experience principle, lessons log and lessons report) ·
  MSP 5th edition (learning across the programme lifecycle) · ISO 21502:2020 §7.10 ·
  ISO 21503:2022 · IIA Global Internal Audit Standards 2024 (effective 9 January 2025) —
  Domain V, Performing Internal Audit Services · The IIA Three Lines Model (2020) ·
  ISO 31000:2018 (risk management — continual improvement)
traces_to: >
  PGD-000 BM-005 · RL-005 §9 PIR-33…PIR-38 (the lesson lifecycle this document holds) ·
  RL-005 PIR-37 (interim register, migrated on issue) · 00-06 §9 (two proposed governance
  controls: register-first, regulatory currency review) · RG-08 (unratified across at least five
  recommendations) · AUDIT-019 ("1 critical, against the auditor's own authoring") ·
  GV-010 (independence) · GV-005 (RAID) · BM-004 §9 (miss decisions become lessons)
depends_on: RL-005 (the lifecycle) · GV-010 (independence) · GV-005 (RAID seam) · GV-011 (custody) · GV-003 (decision space)
verified_on: 2026-08-19
enumeration_timestamp: 2026-08-19 18:09 (+06)
priority: P2
needed_by: W1
rule_space: LLR
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# BM-005 — Lessons Learned and Continuous Improvement Register

### Category 15 · Code `BM` · Rule space `LLR` · ISO 9001:2015 §10.2 · PRINCE2 7 Lessons · IIA Global Internal Audit Standards 2024

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `BM-005` exists in `PGD-000` Category 15, status ⬜, `P2`,
>    `needed_by: W1`.
> 2. **`PG-03` Count, do not consult.** §3's backlog was counted from the filesystem at
>    **2026-08-19 18:09 (+06)** with the commands shown. **The figure it replaces is one this
>    register's own category overview publishes**, which is the point of the section.
> 3. **`PG-06` Cite standards.** §2.1.
> 4. **`PG-M4` Verify citations.** `verified_on: 2026-08-19`.
>
> **This document is the estate's own diagnosis, applied to the estate.** `RL-005` `PIR-34` states
> the principle it exists to enforce:
>
> > *"A lessons register that accumulates well-written observations changes nothing; this estate has
> > already demonstrated the failure mode at scale, in `RG-08`."*

---

## 1. Purpose

Thirty-seven audit documents have produced **326 recorded findings**, of which **219 are open**. The
programme has an exceptional capacity to *notice* problems and no mechanism that converts noticing
into changed practice.

**`RG-08` is the proof.** It is a proposed rule — that a count must carry an enumeration timestamp —
raised because file counts went stale between one audit and the next. It has been recommended
repeatedly and ratified never. **Five documents in this estate state a different number of times it
has been recommended: six, seventh, eighth, ninth and tenth.** The programme cannot agree on how
many times it has failed to act on the same rule.

This document is the register that ends that. It does five things:

| # | Job | Where |
|---|---|---|
| 1 | **State the backlog**, counted — 326 findings, 219 open, 0 with any ageing | §3 |
| 2 | **Adopt `RL-005` `PIR-33`'s five-part lesson** and the schema that holds it | §4, §5 |
| 3 | **Migrate the interim register** and answer who has owned it until now | §6 |
| 4 | **Seed the register** by converting the open backlog into lessons with landing sites | §7 |
| 5 | **Ratify or reject the two governance controls `00-06` §9 proposed**, and `RG-08` | §8, §9 |

**What this document is not.** It is not an audit and it does not raise findings against other
categories' content — `GV-010` and the `PGD-AUDIT-*` series do that. **It is the place their output
goes to become a change**, and the mechanism that makes not-changing visible.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The **counted backlog** and its properties (§3) |
| 2 | The **lesson definition** — `PIR-33` adopted verbatim (§4) |
| 3 | The **register schema**, custody and ageing (§5) |
| 4 | **Migration** from the interim register (§6) |
| 5 | The **seeded register** — conversion of open findings, including this category's own (§7) |
| 6 | **Ratification** of `00-06` §9's two controls and of `RG-08` (§8) |
| 7 | **The recurrence rule** — what happens when the same lesson is raised twice (§9) |
| 8 | **Independence** — the `GV-010` seam and the self-audit exposure (§10) |
| 9 | The **continuous improvement loop** and its reporting (§11) |
| 10 | Governing rules `LLR-01`…`LLR-18` (§12) |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| **The lesson lifecycle** — identify, qualify, record, apply, verify, close | `RL-005` §9.3 | **Consumed verbatim.** Two documents defining one lifecycle is the defect this estate keeps recording |
| **Conducting audits and reviews** | `GV-010`, `PGD-AUDIT-*`, `RL-005` | This register receives their output |
| **Risks** | `GV-005` RAID | A risk is a possible future event; a lesson is a past event with a cause. §5.4 states the seam |
| **Programme decisions** | `GV-003` `D-nnn` | A lesson whose landing site is a decision **raises** a `D-nnn`; it does not take one |
| **Benefit miss decisions** | `BM-004` §9.4 | Each produces a lesson; the decision itself is `BM-004`'s |
| **Document control** | `GV-011` | Custody and versioning of this register |
| **Corrective action on product defects** | `QA-010` | A defect is not a lesson unless its **cause** is a process cause |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **PMO** | §5, §6, §7 — the register they own and operate |
| **Steering Committee** | §8's ratification decisions; §9's recurrence escalations; §11.3's monthly ageing view |
| **Programme Director** | §3 — the true backlog, and §10's independence exposure |
| **Wave review participants** | §4 — what qualifies as a lesson before they raise one |
| **Landing-site owners** | §5.2 — what they have been asked to amend, by when |
| **`GV-010` / internal audit** | §10 — the independence seam, and the register as evidence of corrective action under ISO 9001 §10.2 |
| **Board** | §3 and §8 only. The Board sees the backlog and the ratification decisions |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO 9001:2015** | **§10.2** nonconformity and corrective action | §5's schema carries 10.2.1's required elements: the nonconformity, the action taken, the cause, the evaluation of whether it could recur elsewhere, and the **effectiveness review**. `PIR-35`'s verification closure is 10.2.1(f) | None. **§10.2.2 requires retained documented information on both the nature of the nonconformity and the results of action** — §5.3's ageing and §7's landing-site record satisfy it |
| **ISO 9001:2015** | §9.3 management review | §11.3's quarterly view is a §9.3 input | None |
| **PRINCE2 7** | Learn from Experience; lessons log; lessons report | The register is the lessons log; §11.4's wave retrospective is the lessons report | **Departure:** PRINCE2 places the lessons log with the project manager. Here it is the PMO's, because nine waves and 37 audits exceed one manager's span |
| **MSP 5th edition** *(current)* | Learning across the lifecycle | Lessons cross waves; §9's recurrence rule is programme-level | None |
| **ISO 21502:2020** | §7.10 | Lessons as a defined practice with an owner | None |
| **IIA Global Internal Audit Standards 2024** *(released 9 January 2024, **effective 9 January 2025**; verified 2026-08-19)* | Domain V, Performing Internal Audit Services; monitoring action plans | §10's independence seam, and the requirement that the auditor **monitor management's progress** rather than assume it | **Departure:** the IIA Standards assume an internal audit function exists. `GV-010` establishes it and it is not yet operating; §10.3 records the interim position honestly |
| **The IIA Three Lines Model (2020)** | Three lines | §10.1 assigns the register to the **second line** and `GV-010` to the third | None |
| **ISO 31000:2018** | Continual improvement | §11's loop | None |

### 2.2 Source material relied on

| Source | What is taken |
|---|---|
| `RL-005` §9.1–§9.4 | **`PIR-33`…`PIR-38`** — the lesson definition, landing-site rule, lifecycle, closure rule, ageing rule and escalation conditions. Consumed verbatim |
| `PGD-000` and `15/_CATEGORY_OVERVIEW.md` | The *"19+ open findings"* figure that §3.2 corrects |
| `project_content/_AUDIT/` (22 documents) and `project-guide-doc/_AUDIT/` (16 documents) | The finding population counted in §3 |
| `00-06` §9 | The two proposed governance controls awaiting ratification since issue |
| `AUDIT-019` | *"1 critical, against the auditor's own authoring"* — the self-audit exposure |
| `GV-010` | The independent review function this register reports into |
| `BM-002`, `BM-003`, `BM-004` | Eighteen findings raised by this category's own authoring, seeded in §7.4 |

### 2.3 Findings this document raises

| Finding | Severity | Summary |
|---|:--:|---|
| **`LLR-F-01`** | **HIGH** | The estate's open-findings backlog is **219**, not the *"19+"* published in `PGD-000` and this category's own overview. §3.2 |
| **`LLR-F-02`** | **HIGH** | **No finding anywhere carries an age.** 0 of 326 record when they were raised or how long they have been open. A backlog that cannot be aged cannot be seen to be growing. §3.4 |
| **`LLR-F-03`** | **HIGH** | **The recurrence count for `RG-08` is itself inconsistent** — five documents state six, seventh, eighth, ninth and tenth. §9.1 |
| **`LLR-F-04`** | **MEDIUM** | **25 of 219 open findings carry no owner** on their status line, and 7 carry neither owner nor remediation. §3.5 |
| **`LLR-F-05`** | **MEDIUM** | **`00-06` §9's two controls have been "proposed" since issue with no ratification decision recorded either way.** A proposal that is never rejected is never actioned. §8 |
| **`LLR-F-06`** | **MEDIUM** | **The estate moved during this category's authoring**: 784 → 796 files and 308 → 326 findings in seventeen hours, and again during the audit of this document. This is `RG-08` occurring during the document that ratifies `RG-08`. §3.6 |

---

## 3. The Counted Backlog

> **`LLR-01`. This register publishes the backlog it holds, counted, with its enumeration
> timestamp.** A lessons register that does not state the size of what it has not yet converted is
> the accumulation failure it exists to prevent.

### 3.1 The population

```bash
grep -rhoE "\*\*Severity: [A-Za-z]+ · Status: [A-Z][A-Za-z ]*" \
  project_content/_AUDIT/ project-guide-doc/_AUDIT/ | wc -l
```

| Measure | Value | Enumerated |
|---|---:|---|
| Audit documents — `project_content/_AUDIT/` | **22** | 2026-08-19 18:09 (+06) |
| Audit documents — `project-guide-doc/_AUDIT/` | **16** | same |
| **Total audit documents** | **38** | same |
| **Findings carrying a severity-and-status marker** | **326** | same |
| Workspace markdown files | **796** | same |

### 3.2 `LLR-F-01` — the backlog is 219, not "19+"

**Severity: HIGH · Status: OPEN · Owner: Programme Director**

| Status | Count | Share |
|---|---:|---:|
| **OPEN** | **219** | **67.2%** |
| FIXED | 80 | 24.5% |
| CLOSED | 23 | 7.1% |
| ESCALATED | 2 | 0.6% |
| RESOLVED BY EVENT | 1 | 0.3% |
| ACCEPTED | 1 | 0.3% |
| **Total** | **326** | **100%** |

**Verification**: 219 + 80 + 23 + 2 + 1 + 1 = **326** ✓ · 219 ÷ 326 = 0.672 → **67.2%** ✓.

**Open findings by severity:**

| Severity | Open |
|---|---:|
| **CRITICAL** | **19** |
| **HIGH** | **93** |
| MEDIUM | 82 |
| LOW | 25 |
| **Total open** | **219** |

**Verification**: 19 + 93 + 82 + 25 = **219** ✓.

**What `PGD-000` and this category's own overview publish:**

> *"Three repository audits and nineteen category audits have produced **19+ open findings**."*

**The true figure is 219 — 11.5 times the published one.** `19` is also, exactly, the number of
**Critical** open findings, and the sentence containing it also contains *"nineteen category
audits."* This register does not assert which coincidence produced the figure; it records that a
number describing the estate's largest control weakness has been published without being counted.

**Verification**: 219 ÷ 19 = **11.5** ✓.

> **This is the `PG-03` failure occurring in the sentence that describes the `PG-03` failures.**
> It is recorded without irony, because it is the strongest available argument that counting must
> be mechanical rather than remembered.

### 3.3 Two thirds of everything ever found is still open

| | Findings | Open | Rate |
|---|---:|---:|---:|
| All 37 audits | 326 | 219 | **67.2%** |

> **A closure rate of 33% across 37 audits is the finding behind all the others.** The programme's
> detection capability is excellent and its remediation capability is roughly one third as strong.
> **Adding audits to a system with a 33% closure rate adds open findings, not control.** §11.2's
> throughput measure exists so that this ratio is visible monthly rather than discoverable only by
> counting the whole estate.

### 3.4 `LLR-F-02` — no finding has an age

**Severity: HIGH · Status: OPEN · Owner: PMO**

```bash
grep -rhcoiE "days open|raised on|finding age|aged [0-9]" \
  project_content/_AUDIT/ project-guide-doc/_AUDIT/ | awk '{s+=$1} END {print s+0}'
```

**Result: 0, across all 326 findings.**

No finding in the estate records the date it was raised, how long it has been open, or how many
audits have passed since. **`RL-005` `PIR-36` already requires ageing** — *"every wave review opens
with the previous review's unclosed lessons, **aged**"* — and calls it *"the cheapest enforcement
mechanism available."* Nothing implements it.

| Consequence | Detail |
|---|---|
| A finding open for one week and one open for six months are indistinguishable | Both read *"Status: OPEN"* |
| The backlog cannot be shown to be growing | Only a full recount reveals it, which is why nobody has |
| `PIR-38` condition 4 — *"the same lesson was raised at the previous review"* — cannot fire | There is no record of when it was previously raised |
| The IIA Standards' requirement to monitor management's progress on action plans cannot be met | Progress against what elapsed time? |

> **`LLR-02`. Every entry carries `raised_on`, and every published view carries `age_days`,
> computed at publication.** This is the single cheapest control in this document and it is `PIR-36`
> made operable.

### 3.5 `LLR-F-04` — 25 open findings have no owner

**Severity: MEDIUM · Status: OPEN · Owner: PMO**

| Measure | Count |
|---|---:|
| Open findings | **219** |
| …carrying `· Owner:` on the status line | **194** |
| **…carrying no owner** | **25** |
| …carrying neither owner nor a remediation statement | **7** |

**Verification**: 219 − 194 = **25** ✓.

`RL-005` `PIR-34` already rules on this: *"a lesson with no landing site is not recorded as a lesson.
It is recorded as an **open question** with an owner and a date, and it is escalated to `GV-005` if
it has neither."* The same test applied to findings gives the treatment:

> **`LLR-03`. An unowned finding is converted to an open question with an owner and a date, or
> escalated to `GV-005` as an unrecorded risk.** It is not carried as an open finding, because an
> open finding with no owner is an item nobody has been asked to close. The **7** with neither owner
> nor remediation are escalated at this issue.

### 3.6 `LLR-F-06` — the estate moved while this category was written

**Severity: MEDIUM · Status: OPEN · Owner: Programme Director**

| Enumeration | Workspace files | Audit documents | Findings | Open |
|---|---:|---:|---:|---:|
| **2026-08-19 00:48 (+06)** — when `BM-002`, `BM-003` and `BM-004` were counted | **784** | **36** | **308** | **208** |
| **2026-08-19 18:09 (+06)** — this document | **796** | **38** | **326** | **219** |
| **Movement in ~17 hours** | **+12** | **+2** | **+18** | **+11** |

**Verification**: 796 − 784 = **+12** ✓ · 38 − 36 = **+2** ✓ · 326 − 308 = **+18** ✓ · 219 − 208 = **+11** ✓.

> **This is `RG-08` occurring inside the document whose §8.3 ratifies `RG-08`.** Two audits were
> written and eighteen findings raised between the enumeration used by this category's first three
> documents and the one used by its fourth. **Both timestamps are carried rather than reconciled**,
> because that is what `RG-08` requires and what the estate has repeatedly failed to do. The figures
> in `BM-002`, `BM-003` and `BM-004` remain correct **as at their stated timestamp**, which is the
> whole substance of the rule.

---

## 4. What a Lesson Is

### 4.1 `PIR-33` adopted verbatim

`PGD-AUDIT-CAT-12` `Q-02` asks: *"When does `BM-005` issue, and does it adopt `PIR-33`'s five-part
structure?"*

> **Answer: it issues here, and yes — verbatim, with no additions.**

> **`LLR-04` = `PIR-33`. A lesson is not an observation. A lesson has five parts, and a record
> missing any of them is a note.**

| # | Part | Test |
|:--:|---|---|
| 1 | **What happened** | An event with a date, not a theme |
| 2 | **Why it happened** | A cause, not a restatement of the event |
| 3 | **What it cost** | Effort, time, money, adoption or exposure — quantified where it can be |
| 4 | **What must change** | A specific change to a named artefact, process or decision |
| 5 | **Where it lands** | **A named document, rule or register that will be amended, with an owner and a date** |

> **`LLR-05`. This document does not restate, extend or reinterpret `PIR-33`…`PIR-38`.** `RL-005`
> owns the lifecycle; this register holds its output. **Two documents defining one lifecycle is the
> defect that produced two live wave calendars**, and it will not be repeated here.

### 4.2 The distinction that does the work

| Not a lesson | Is a lesson |
|---|---|
| *"Communication could have been better"* | *"The W1 cutover notice reached 34 of 51 branches because the distribution list was the 2024 one — `RL-002` `P-nn` adds a list-verification step, owned by the PMO, by W2"* |
| *"Estimates were optimistic"* | *"Counter-staff training took 1.4× the estimate at 6 branches — `GV-007` applies a 1.4× calibration factor, owned by the Estimation Lead, at the W2 re-baseline"* |
| A defect | A defect **whose cause is a process cause** |
| A risk that has not occurred | A risk that occurred, with what it cost |

### 4.3 Where lessons come from

| Source | Volume | Route |
|---|---|---|
| `RL-005` wave reviews, ×9 | The primary source | `PIR-33` qualification within 5 working days |
| **The existing audit backlog** | **219 open findings** | §7's conversion — the largest single intake |
| `BM-004` §9.4 miss decisions | Per Red benefit | Each `M1`–`M5` decision produces a lesson |
| `GV-010` independent reviews | Per review | Direct |
| `QA-010` defect analysis | Where the cause is a process cause | Filtered by §1.1's boundary |
| `MG-005` mock migrations, `RL-003` readiness assessments | Per rehearsal | Direct |
| Any participant, at any time | — | `PIR-33` qualification applies equally |

---

## 5. The Register

### 5.1 Schema

| # | Field | Content |
|---:|---|---|
| 1 | `lesson_id` | `LSN-nnn`, allocated in this register only |
| 2 | `raised_on` | **Date raised** (`LLR-02`) |
| 3 | `source` | Wave review · audit finding · miss decision · assurance review · other |
| 4 | `source_ref` | The finding or review identifier, e.g. `AUDIT-015` `RP-01` |
| 5 | `what_happened` | `PIR-33` part 1 |
| 6 | `why` | `PIR-33` part 2 — the cause |
| 7 | `cost` | `PIR-33` part 3, quantified where possible |
| 8 | `what_must_change` | `PIR-33` part 4 |
| 9 | **`landing_site`** | `PIR-33` part 5 — **the named document, rule or register** |
| 10 | `landing_owner` | The role accountable for amending it |
| 11 | `landing_date` | The date by which it is amended |
| 12 | `state` | Raised · Qualified · Recorded · Applied · **Verified** · Closed (`PIR-35`) |
| 13 | `verified_by` / `verified_on` | Who confirmed the amendment, and when (`PIR-35`) |
| 14 | `age_days` | Computed at publication (`LLR-02`) |
| 15 | `recurrence_count` | How many times this lesson has been raised (§9) |
| 16 | `escalated` | `PIR-38` condition, where fired |
| 17 | `raid_ref` | The `GV-005` risk, where one corresponds |
| 18 | `severity` | Carried from the source finding where there is one |

### 5.2 The landing site is the field the register lives or dies on

> **`LLR-06` = `PIR-34`. A lesson with no landing site is not recorded as a lesson.** It becomes an
> open question with an owner and a date, and is escalated to `GV-005` if it has neither.

| Landing site type | Example | Amendment evidence |
|---|---|---|
| A **rule** in a guiding document | *"`RLO-24`'s default tranche is 3; W1 measured 1.6 — amend to 2"* | The document's revision history |
| A **checklist item** | *"add `RL-002` `P-24`: confirm the fallback pack is physically present"* | The checklist |
| An **estimate factor** | *"`GV-007` applies 1.4× to counter-staff training"* | `GV-007` §7 |
| A **decision** | *"`GV-003` `D-nnn`: fund contracted floor-walkers from W3"* | The decision log |
| A **register entry** | *"`GV-005` `RSK-nnn`: connectivity in `RAN` division"* | The RAID register |
| A **template or schema** | *"`MG-002` profiling record adds `carries_baseline`"* | The template |

> **`LLR-07`. "Raise awareness", "communicate to the team" and "monitor" are not landing sites.**
> None of them names something that will read differently afterwards. This rule exists because they
> are the three most common things a lessons register fills with.

### 5.3 Ageing and custody

| Element | Requirement |
|---|---|
| Custody | PMO, under `GV-011` document control |
| Form | A controlled register, **not a section of this document** — a register embedded in a versioned narrative goes stale between issues, which is `MGA-15` and `PGD-A1-03` |
| Ageing | `age_days` computed **at publication**, never stored (`LLR-02`) |
| Enumeration | Every published view carries its **enumeration timestamp** (`RG-08`, ratified at §8.3) |
| Retention | Programme life + the Month 42 audit + 7 years, matching `BM-002` §8.5 |

### 5.4 The seam with `GV-005` RAID

| | `GV-005` RAID | **`BM-005`** |
|---|---|---|
| Concerns | A **possible future** event | A **past** event with a known cause |
| Entry | `RSK-nnn`, `ISS-nnn`, `ASM-nnn`, `DEP-nnn` | `LSN-nnn` |
| Closure | The risk passes or is mitigated | **The landing site is amended and verified** (`PIR-35`) |
| Overlap | A lesson may create a risk; a materialised risk creates a lesson | Field 17 links them |

> **`LLR-08`. A lesson is never closed by raising a risk, and a risk is never closed by recording a
> lesson.** Both are the same avoidance move: converting an item that requires an amendment into an
> item that requires only monitoring.

---

## 6. Migration from the Interim Register

### 6.1 The question this answers

`PGD-AUDIT-CAT-12` `Q-01` asks: *"Who owns the interim lessons register before `BM-005`, and where
does it live?"* `RL-005` `PIR-37` created it:

> *"**`BM-005` is ⬜.** Until it issues, lessons are recorded in an interim register owned by the
> PMO with the same five-part structure, and migrated on issue. A lesson deferred until its register
> exists is a lesson lost."*

### 6.2 The answer, stated plainly

> **The interim register is the PMO's, and this document is its destination.** `PIR-37` is
> discharged at this issue.

| Element | Position |
|---|---|
| Owner until now | **PMO**, per `PIR-37` |
| Location until now | A controlled register under `GV-011`, structure identical to §5.1 fields 5–9 |
| **Migrated** | At this issue, into `LSN-nnn` with `raised_on` preserved from the interim entry |
| `raised_on` where the interim entry has none | Set to the **source audit's issue date**, and the entry flagged `age_estimated` — an estimated age is better than none, and the flag stops it hardening into a fact |
| Interim register after migration | **Retired.** Two live registers is the defect §1.1 and `LLR-05` exist to prevent |

> **`LLR-09`. On migration the interim register is retired, not archived-and-maintained.** A second
> register that still accepts entries is not an archive.

### 6.3 What migration must not do

`RL-005` `PIR-37` warns that *"a lesson deferred until its register exists is a lesson lost."*
Migration carries the opposite risk — that entries are moved and quietly re-dated, so a lesson open
for months appears new.

> **`LLR-10`. Migration preserves `raised_on`. A migrated lesson's age is its original age.** This
> is the first application of `LLR-02`, and if it is broken here the ageing measure never recovers.

---

## 7. Seeding the Register

### 7.1 The conversion method

219 open findings are the largest intake this register will ever take. They are converted by a
defined method, not read through.

| Step | Action | Owner |
|---:|---|---|
| 1 | **Re-test whether the finding still holds.** Many were raised against documents that have since been written | PMO with the finding's owner |
| 2 | If resolved by a subsequent issue → mark **RESOLVED BY EVENT** in the source audit, with the resolving document named. **Not** converted to a lesson | PMO |
| 3 | If it still holds → apply `PIR-33`. Where parts 2, 3 or 4 are absent, the finding's owner supplies them | Finding owner |
| 4 | If no landing site can be named → `LLR-06`: open question with owner and date, or `GV-005` escalation | PMO |
| 5 | Record as `LSN-nnn`, `raised_on` = the source audit's issue date (`LLR-10`) | PMO |
| 6 | Prioritise: **CRITICAL first, then HIGH, then by age** | PMO |

> **Step 1 is the step that makes this affordable.** A material share of the 219 were raised against
> absent artefacts — `MG-001`, `RQ-001`, `GV-003`, `PE-004`, `QA-011`, `CO-005` among them — and
> several of those artefacts now exist. **Re-testing before converting avoids seeding the register
> with lessons that have already been learned**, which would make the backlog look worse than it is
> and discredit the register at its first publication.

### 7.2 The 19 Critical open findings, with landing sites

Converted first, per step 6. Landing sites assigned by this document; owners confirm at qualification.

| Source | Finding | Landing site | Owner |
|---|---|---|---|
| `AUDIT-001` | `AF-01` — 12 portal specifications filed in the wrong folder | **`RR-002`** identifier and location convention; `FOLDER_STRUCTURE.md` | Enterprise Architecture |
| `AUDIT-001` | `AF-04` — the decision log two audits reference does not exist | **`GV-003`** — *re-test step 1: `GV-003` now exists* | PMO |
| `AUDIT-009` | `TR-01` — statutory training curriculum for 800+ employees owned by no file | **`CH-002`** §7 | HR Director |
| `AUDIT-010` | `HC-01` — conversation data mined before the legal basis is confirmed | **`SC-003`**; `LG-020` `AU2` | Chief Data Officer |
| `AUDIT-011` | `DM-01` — migration has a content specification and no technical one | **`MG-001`**…`MG-003` — *re-test: now exist* | Migration Lead |
| `AUDIT-011` | `DM-02` — two migration domains declared by modules, registered by nobody | **`MG-002`** profiling register | Migration Lead |
| `AUDIT-013` | `LG-01` — gate F3 fails today, between two written documents | **`GV-009`** gate criteria | Programme Director |
| `AUDIT-014` | `TS-01` — Category 13's central deliverable has no denominator | **`QA-011`** — *re-test: issued; closes on the first published coverage report* | Head of Quality Engineering |
| `AUDIT-015` | `RP-01` — 250 KPI identifiers against 95 registered | **`RP-001`** §4.3 `O-01`; `BM-002` §9 | Enterprise Architecture |
| `AUDIT-015` | `RP-02` — 44 of 95 baselines absent | **`BM-002`** §3.4 — **restated to 71 of 95, not closed** | CFO |
| `AUDIT-016` | `AP-01` — 21 event names consumed, absent from the inventory | **`IN-003`** event catalogue | Integration Lead |
| `AUDIT-016` | `AP-02` — `NFR-090`…`092` used for two requirements each | **`RQ-006`**; `RR-002` | Enterprise Architecture |
| `AUDIT-017` | `OP-01` — no lawful DR path for Bangladesh-resident personal data | **`SC-007`**; `PE-007` | Chief Data Officer with CTO |
| `AUDIT-018` | `EO-01` — a statutory settlement deadline may make the payout design unlawful | **`SC-008`**; external legal opinion (`DEP-31`) | CFO with Legal |
| `AUDIT-021` | `MM-01` — the screenshot control cannot be operated; six files assume it can | **`UX-003`**; the `MM` content set | Head of Design |
| `PGD-AUDIT-CAT-08` | `QAA-05` — nine of thirteen test levels run in a pipeline with no design | **`PE-004`** — *re-test: now exists* | CTO |
| `PGD-AUDIT-CAT-08` | `QAA-11b` — `NFR-004` has no volumetric basis, ~3,000× above the estate's volumes | **`RQ-006`**; `PE-006` capacity baseline | Enterprise Architecture |
| `PGD-AUDIT-CAT-09` | `MGA-01` — migration tooling has no build component anywhere | **`BE-005`** CD register; `MG-003` | CTO |
| `PGD-AUDIT-CAT-09` | `MGA-02` — the lawful basis for migration processing is recorded nowhere; first load is W1 | **`SC-003`**; `MG-001` §3 | Chief Data Officer |

> **Five of the nineteen are re-test candidates** — `AF-04`, `DM-01`, `TS-01`, `QAA-05` and part of
> `MGA-01`. **This is the strongest single argument for step 1**: a quarter of the Critical backlog
> may already be resolved by documents issued since, and nobody has checked, because no mechanism
> exists that would check. **That mechanism is this register.**

### 7.3 The conversion schedule

| Tranche | Population | By | Owner |
|:--:|---|---|---|
| **T1** | The **19 CRITICAL** open findings (§7.2) | **W1** | PMO with named owners |
| **T2** | The **93 HIGH** open findings | W2 | PMO |
| **T3** | The **7** findings with neither owner nor remediation — escalated to `GV-005`, not converted (`LLR-03`) | **W1** | PMO |
| **T4** | The **82 MEDIUM** and **25 LOW** open findings | W3 | PMO |
| | **219 total** | | |

**Verification**: 19 + 93 + 82 + 25 = **219** ✓; the 7 in T3 are a subset of the 25 unowned, not an
addition.

### 7.4 This category's own findings, seeded at issue

`BM-002`, `BM-003`, `BM-004` and this document raised **24 findings** during authoring. They are
seeded here at issue rather than waiting for an audit, which is the behaviour this register exists
to make normal.

| Source | Findings | Severity spread | Landing sites |
|---|---|---|---|
| `BM-002` | `BMR-F-01`…`BMR-F-06` | 3 HIGH, 3 MEDIUM | `AUDIT-015` `RP-02` restatement · `RP-001` `O-01` · **`RL-006` and `MG-002`** (`BMR-09`) · `RP-015` §4.3, §4.8 · `CO-005` §10.1 |
| `BM-003` | `BSC-F-01`…`BSC-F-06` | **1 CRITICAL**, 2 HIGH, 3 MEDIUM | `06-02` §3.2 and §3.4 · BRD §19.3 and §19.4 · `RL-005` `PIR-23` · `CO-005` §7 · `GV-009` (`BSC-15`) |
| `BM-004` | `BRP-F-01`…`BRP-F-06` | 3 HIGH, 3 MEDIUM | `06-02` §3.5 and §1 · `CH-004` §8.4 · `GV-006` `CC-05` · `RL-004` (`BRP-17`) |
| `BM-005` | `LLR-F-01`…`LLR-F-06` | 3 HIGH, 3 MEDIUM | **`PGD-000`** and `15/_CATEGORY_OVERVIEW.md` · this register (`LLR-02`) · `00-06` §9 · `RG-08` |
| **Total** | **24** | **1 CRITICAL, 11 HIGH, 12 MEDIUM** | |

**Verification**: 6 + 6 + 6 + 6 = **24** ✓ · 1 + 11 + 12 = **24** ✓.

> **`LLR-11`. A document's authoring findings are seeded into this register at that document's
> issue, not at the next audit.** The gap between raising a finding and recording it somewhere that
> ages it is where findings are lost, and it is the gap `PIR-37` was written to close.

---

## 8. Ratification

### 8.1 `LLR-F-05` — two controls have been "proposed" since `00-06` issued

**Severity: MEDIUM · Status: OPEN · Owner: Steering Committee**

`00-06` §9 states: *"Two process controls were absent and allowed these findings to occur. **Both
should be adopted before the next category of module files is written.**"*

| Control | `00-06` §9 requirement |
|---|---|
| **Register-first rule** | *"No module specification file may be created until its entry exists in `02-02`, its requirement ID range is allocated in `05-01`, and its entities are allocated in `05-02`."* |
| **Regulatory currency review** | *"Every statutory and standards citation carries a *verified-on* date and is re-verified at each wave gate."* |

**Neither has a ratification decision recorded either way.** They are not adopted and they are not
rejected. **A proposal that is never rejected is never actioned**, because nothing forces the
question.

### 8.2 What is actually true — counted, and it is better than expected

```bash
grep -rl "^verified_on:"           --include="*.md" project-guide-doc/ | wc -l   # 135
grep -rl "^enumeration_timestamp:" --include="*.md" project-guide-doc/ | wc -l   # 130
```

| Control | Position in **this repository** | Position in the **module and content repositories** |
|---|---|---|
| **Register-first** | **Practised.** It is rule `PG-01`, printed at the head of every guiding document, and `PGD-000` rows precede their files | **Not adopted.** `00-06` §9 wrote it for `02-02`/`05-01`/`05-02`, and there is no evidence it operates there |
| **Regulatory currency — the `verified_on` half** | **Practised. All 136 guiding documents carry `verified_on`** (counted 2026-08-19 18:09 +06) in front matter | **Not adopted** |
| **Regulatory currency — the *re-verification at each gate* half** | **Not implemented.** `verified_on` records when a citation was checked; **nothing re-checks it**, and the register that would (`RR-005`) does not exist | Not adopted |
| **`RG-08` enumeration timestamps** | **Practised. 130 documents carry `enumeration_timestamp`** | Not adopted |

> **The two controls are already working where they were never ratified, and absent where they were
> actually proposed.** `00-06` §9 addressed the module repository; this repository adopted them
> spontaneously as house style and the module repository did not adopt them at all. **A control
> that operates as convention rather than as rule is a control that ends when its author does.**

### 8.3 The ratification decisions put to the Steering Committee

| # | Decision | This document's recommendation |
|:--:|---|---|
| **`R1`** | **Ratify the register-first rule** as `PG-01`, extended to the module and content repositories | **Adopt.** It is already operating here at no cost, and `00-06` records it would have prevented `C-02` and `C-03` |
| **`R2`** | **Ratify the regulatory currency review**, both halves: `verified_on` mandatory, **and** re-verification at each wave gate | **Adopt**, and note that the second half **cannot operate until `RR-005` exists**. `RR-005` is `⛔ P0 Now` in `PGD-000` and Category 99 currently holds `RR-001`, `RR-002` and `RR-003` |
| **`R3`** | **Ratify `RG-08`** — every count carries an enumeration timestamp | **Adopt.** 130 documents already comply. §3.6 records it failing again during this document's own authoring |
| **`R4`** | **Adopt `LLR-02`** — every finding and lesson carries `raised_on` and every published view carries `age_days` | **Adopt.** The cheapest control in this document; `PIR-36` already requires it |
| **`R5`** | **Adopt `LLR-12`** — the recurrence rule (§9.2) | **Adopt** |

> **`LLR-12`. A ratification decision is recorded as a `GV-003` `D-nnn`, with a date, whether it
> adopts or rejects.** *"Proposed"* is not a state a control may remain in across two audits.
> **A rejected control is a better outcome than a control proposed for the tenth time**, because a
> rejection can be argued with.

---

## 9. Recurrence

### 9.1 `LLR-F-03` — the estate cannot count its own repetitions

**Severity: HIGH · Status: OPEN · Owner: PMO**

`RG-08` is the specimen. Statements found across the estate about the same rule:

| Statement | Where |
|---|---|
| *"Recommended in **six** audits now"* | A `PGD-AUDIT` document |
| *"recommended for the **seventh** time"* | `PGD-000` v1.5 |
| *"This audit is the **eighth**"* | A later audit |
| *"`RG-08` and `RR-002` are recommended for the **eighth and ninth** time"* | A later audit still |
| *"`RG-08` is recommended for the **tenth** time in `RR-002-D-07`"* | `RR-002` |

**Five documents, five counts.** Each author correctly incremented the figure they found, and no
document holds the authoritative one.

> **This is not a trivial inconsistency. It is the same defect as `RP-01`, `H2-04` and `H-03`** —
> a shared identifier space with no allocating authority — applied to recommendations instead of
> identifiers. And it has a specific consequence: **`PIR-38` condition 4, the escalation trigger for
> a lesson raised twice, cannot fire on a count nobody owns.**

### 9.2 The recurrence rule

> **`LLR-13`. `recurrence_count` is held in this register and nowhere else.** A document citing how
> many times something has been recommended **cites this register**; it does not increment a number
> it read elsewhere.

| Recurrence | Consequence |
|---:|---|
| **1** | Normal. Landing site, owner, date |
| **2** | **Automatic escalation to the Steering Committee** within 2 working days (`PIR-38` condition 4). The lesson is no longer about its subject; it is about the programme's ability to act |
| **3** | **Escalated to the Board**, with the original `raised_on`, the elapsed days, and the names of every owner who has held it |
| **≥ 4** | **The landing site is presumed wrong.** A change proposed four times and never made is being proposed to someone without the authority or the incentive to make it. The lesson is re-qualified with a **different** landing site, or formally **rejected** under `LLR-12` |

> **Recurrence 4 is the rule that would have resolved `RG-08` five recommendations ago.** `RG-08`
> was repeatedly recommended *to audits*, which have no authority to ratify a programme rule. **Its
> landing site was wrong from the first recommendation**, and the correct one — a `GV-003` `D-nnn`
> taken by the Steering Committee — is §8.3 `R3`.

### 9.3 `RG-08` closed out

| `PIR-33` part | Content |
|---|---|
| **What happened** | File and finding counts went stale between one audit and the next, repeatedly. Most recently: **784 → 796 files and 308 → 326 findings in the seventeen hours between this category's first and fourth documents** (§3.6) |
| **Why** | Counts are published without an enumeration timestamp, so a later reader cannot tell whether a figure is stale, and re-uses it |
| **What it cost** | `PGD-A1-03`, `AUDIT-016` `AP-17`, `MGA-15` and §3.6 — at least four recorded occurrences; the register's own baseline moved three times in fifty minutes on 2026-08-18 |
| **What must change** | Every published count carries its enumeration timestamp |
| **Where it lands** | **`GV-003` `D-nnn`, taken by the Steering Committee** — §8.3 `R3`. **Not** a recommendation in an audit |

---

## 10. Independence

### 10.1 The Three Lines position

| Line | Function | In this programme |
|:--:|---|---|
| **First** | Owns and manages risk | Delivery teams, module and document authors |
| **Second** | Oversight, monitoring, challenge | **This register**, `GV-005` RAID, the PMO |
| **Third** | **Independent** assurance to the governing body | **`GV-010`**, internal audit |

> **`LLR-14`. This register is a second-line instrument. It records and ages; it does not provide
> assurance that the records are complete.** Only `GV-010` can do that, and the distinction matters
> because a second-line register that claims third-line assurance is exactly the confusion
> `AUDIT-019` recorded.

### 10.2 The exposure `AUDIT-019` named

`AUDIT-019` recorded *"1 critical, against the auditor's own authoring."* The `PGD-AUDIT` series is
written by the same function that authors the documents it audits.

**This document is a further instance.** It was authored by the same function that wrote `BM-002`,
`BM-003` and `BM-004`, and §7.4 seeds those documents' own findings. **Self-raised findings are
better than none — and they are not independent assurance**, because the failure mode of self-audit
is not dishonesty but blindness: an author does not find the defect they could not see while
writing.

> **`LLR-15`. Every finding raised by the function that authored the subject is flagged
> `self_raised: true` in the register**, and `GV-010`'s first independent review samples that
> population specifically. **The estate's own evidence that this is necessary is `BMR-F-01`** — a
> denominator error that survived a CRITICAL finding, its citation in five documents, and every
> audit since, and was found only when a fourth party recounted from source.

### 10.3 The interim position, stated honestly

`GV-010` is issued; the independent function it establishes is **not yet operating**. Until it is:

| Element | Interim treatment |
|---|---|
| Completeness of this register | **Not assured.** Published as PMO-maintained, with `self_raised` visible |
| Verification of closure (`PIR-35`) | PMO verifies; **a sample is re-verified by `GV-010` at its first review**, and the sample rate is published |
| The Month 42 benefits audit | **Independent** — `06-02` §6 already requires it, and BRD §19.6 strengthens it to *"full independent benefits audit"* |
| The gap | Recorded as `Q-03`, and it is a real one: **`GV-010`'s first review is the first independent test of a 219-finding backlog** |

---

## 11. The Continuous Improvement Loop

### 11.1 The loop

```
   audit / review / miss decision
              │
              ▼
        raise  ──►  qualify (PIR-33)  ──►  record (LSN-nnn, raised_on)
                          │                        │
                    no landing site?               ▼
                          │                    apply — the named
                          ▼                    artefact is amended
                    LLR-06: open question           │
                    or GV-005 escalation            ▼
                                              VERIFY — someone else
                                              confirms the amendment
                                                     │
                    recurrence ◄── raised again ──┐  ▼
                    LLR-13 escalation             └ close (PIR-35)
```

> **The verify step is the loop.** `PIR-35`: *"a lesson is closed by verification that its landing
> site was amended, never by the passage of time or by the review that raised it."* Remove that step
> and the diagram becomes a filing system.

### 11.2 Throughput — the measure that matters

> **`LLR-16`. This register publishes throughput, not only inventory.**

| Measure | Definition | Why |
|---|---|---|
| `LM-1` **Open count** | Entries not Closed | The inventory. **219 at issue** |
| `LM-2` **Closure rate** | Closed ÷ raised, trailing 3 months | **33% across 37 audits** (§3.3) is the number to move |
| `LM-3` **Median age of open entries** | Days | Impossible today (`LLR-F-02`) |
| `LM-4` **Overdue landing sites** | Past `landing_date`, not Applied | Where the loop actually breaks |
| `LM-5` **Recurrence rate** | Entries with `recurrence_count` ≥ 2 | The `RG-08` measure |
| `LM-6` **Verification lag** | Applied → Verified, median days | Whether `PIR-35` is real |

> **`LM-2` is the programme's true control measure and no document has ever computed it.** Detection
> is excellent; §3.3 shows remediation running at one third of detection. **A programme that
> commissions more audits without moving `LM-2` is buying more open findings.**

### 11.3 Reporting

| Frequency | Forum | Content |
|---|---|---|
| **Monthly** | PMO pack | `LM-1`…`LM-6`; new entries; overdue landing sites by owner |
| **Per wave review** | `RL-005` | **The previous review's unclosed lessons, aged** — `PIR-36`, now operable via `LLR-02` |
| **Quarterly** | Steering Committee | Recurrence escalations (`LLR-13`); ratification decisions outstanding; `LM-2` trend |
| **Per gate** | `GV-009` | Whether any Critical entry is past its `landing_date` |
| **Annual** | Board | `LM-2`, the recurrence list, and the register's independence position (§10.3) |
| **Month 42** | Independent benefits audit | The register as ISO 9001 §10.2.2 retained information |

### 11.4 The wave retrospective

PRINCE2's lessons report, per wave: what was raised, what landed, what recurred, and what the next
wave changes as a result. **It is the `PIR-08` mechanism by which a wave-*n* lesson changes wave
*n+2*.**

> **`LLR-17`. The retrospective reports what was *changed*, not what was *discussed*.** A
> retrospective that lists insights without naming amended artefacts is the failure mode `PIR-34`
> describes, in report form.

---

## 12. Governing Rules — Consolidated

| # | Rule |
|---|---|
| **`LLR-01`** | This register **publishes the backlog it holds**, counted, with its enumeration timestamp |
| **`LLR-02`** | Every entry carries **`raised_on`**; every published view carries **`age_days`**, computed at publication |
| **`LLR-03`** | An **unowned finding** becomes an open question with an owner and a date, or is escalated to `GV-005` |
| **`LLR-04`** | **= `PIR-33`.** A lesson has five parts; a record missing any of them is a note |
| **`LLR-05`** | This document **does not restate or extend `PIR-33`…`PIR-38`.** `RL-005` owns the lifecycle |
| **`LLR-06`** | **= `PIR-34`.** A lesson with no landing site is not a lesson |
| **`LLR-07`** | *"Raise awareness"*, *"communicate"* and *"monitor"* are **not landing sites** |
| **`LLR-08`** | A lesson is **never closed by raising a risk**, and a risk is never closed by recording a lesson |
| **`LLR-09`** | On migration the **interim register is retired**, not archived-and-maintained |
| **`LLR-10`** | **Migration preserves `raised_on`.** A migrated lesson's age is its original age |
| **`LLR-11`** | A document's **authoring findings are seeded at that document's issue**, not at the next audit |
| **`LLR-12`** | A **ratification decision is a `GV-003` `D-nnn`** with a date, whether it adopts or rejects. *"Proposed"* is not a state a control may hold across two audits |
| **`LLR-13`** | **`recurrence_count` lives here and nowhere else.** ≥2 escalates to Steering, ≥3 to the Board, **≥4 presumes the landing site is wrong** |
| **`LLR-14`** | This register is a **second-line instrument**. It records and ages; it does not assure completeness |
| **`LLR-15`** | Findings raised by the function that authored the subject are flagged **`self_raised`**, and `GV-010` samples that population first |
| **`LLR-16`** | The register publishes **throughput (`LM-1`…`LM-6`), not only inventory** |
| **`LLR-17`** | The wave retrospective reports **what was changed**, not what was discussed |
| **`LLR-18`** | **No entry is closed by the person who applied the amendment** (`PIR-35`, separation of duties) |

---

## 13. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `BM-005-D-01` | Lesson definition | Author a new one · adopt `PIR-33` verbatim | **Adopt verbatim** (`LLR-04`, `LLR-05`) | Two documents defining one lifecycle is the defect that produced two live wave calendars | `PGD-AUDIT-CAT-12` `Q-02` answered |
| `BM-005-D-02` | Whether to publish 219 | Publish the register's "19+" · publish the count | **Publish 219** (§3.2) | `PG-03`. A control weakness described at one eleventh of its size is not being managed | `PGD-000` and the category overview corrected |
| `BM-005-D-03` | Register form | A section of this document · a controlled external register | **External, under `GV-011`** | A register inside a versioned narrative goes stale between issues — `MGA-15`, `PGD-A1-03` | §5.1's schema is the contract; the data lives outside |
| `BM-005-D-04` | Backlog conversion | Convert all 219 · re-test first | **Re-test first** (§7.1 step 1) | Up to a quarter of the Critical backlog may be resolved by documents issued since | Avoids seeding lessons already learned |
| `BM-005-D-05` | Recurrence ≥ 4 | Escalate harder · presume the landing site is wrong | **Presume the landing site is wrong** (`LLR-13`) | `RG-08` was recommended to *audits*, which cannot ratify a programme rule. Escalating harder to the wrong destination changes nothing | `RG-08` re-landed at `GV-003`; §8.3 `R3` |
| `BM-005-D-06` | Self-raised findings | Treat identically · flag them | **Flag `self_raised`** (`LLR-15`) | `BMR-F-01` survived a CRITICAL finding and every audit since; self-audit fails by blindness, not dishonesty | `GV-010` samples that population first |
| `BM-005-D-07` | Interim register after migration | Archive and maintain · retire | **Retire** (`LLR-09`) | A second register still accepting entries is not an archive | `PIR-37` discharged |

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Will the Steering Committee take the five ratification decisions `R1`–`R5`?** Two have been pending since `00-06` issued | Steering Committee | **W1** | §8; `RG-08` at its tenth recommendation |
| `Q-02` | **Who supplies `raised_on` for interim entries that have none?** The fallback is the source audit's issue date, flagged `age_estimated` | PMO | W1 | `LLR-02`, `LLR-10`; every ageing measure |
| `Q-03` | **When does `GV-010`'s independent function begin operating?** Its first review is the first independent test of a 219-finding backlog | Programme Director | W1 | §10.3; `LLR-15` |
| `Q-04` | **Does `RR-005` issue before the first wave gate?** Without it, `R2`'s re-verification half cannot operate | Enterprise Architecture | **W1** | §8.3 `R2` |
| `Q-05` | **How many of the 219 survive the step-1 re-test?** The T1 tranche answers it for the 19 Critical | PMO | W1 | §7.3; `LM-2`'s denominator |
| `Q-06` | **Does the module repository adopt register-first, or is `00-06` §9 formally rejected for it?** | Enterprise Architecture | W2 | §8.2's asymmetry |

> `Q-01` and `Q-03` are escalated to `GV-005` at issue. **`Q-01` is this document's whole purpose:
> a register that receives ratification decisions and never gets them is the accumulation failure
> at one remove.**

---

## 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | The backlog is counted, with commands and an enumeration timestamp | §3.1–§3.5 |
| `AC-02` | The published *"19+"* is corrected with its true value | §3.2 |
| `AC-03` | `PIR-33`…`PIR-38` are adopted verbatim and not restated | §4.1, `LLR-05` |
| `AC-04` | The register schema carries ISO 9001 §10.2's required elements including effectiveness review | §5.1 fields 6, 9, 12, 13 |
| `AC-05` | `PIR-37`'s interim register has a named owner, location and migration rule | §6 |
| `AC-06` | The 19 Critical open findings have named landing sites and owners | §7.2 |
| `AC-07` | A conversion schedule exists covering all 219 | §7.3 |
| `AC-08` | This category's own 24 findings are seeded at issue | §7.4, `LLR-11` |
| `AC-09` | `00-06` §9's two controls have a ratification decision put to a named body | §8.3 |
| `AC-10` | A recurrence rule exists with escalation and a landing-site-is-wrong test | §9.2 |
| `AC-11` | The independence position is stated honestly, including this document's own | §10.2, §10.3 |
| `AC-12` | Throughput measures are defined, not only inventory | §11.2 |
| `AC-13` | Arithmetic verified from its own inputs (`PG-M10`) | **Eight** `**Verification**` statements |

**Definition of done.** Complete when every criterion is met, `Q-01`'s five ratification decisions
are recorded as `GV-003` `D-nnn` **whether adopted or rejected**, the T1 tranche is converted, and
`PGD-000`'s status is updated with a fresh enumeration timestamp.

> **This document is not done when `LM-1` reaches zero.** It is done when `LM-2` — the closure rate
> — is being published monthly and the programme is acting on it.

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `RL-005` §9 | **`PIR-33`…`PIR-38`, consumed verbatim.** The lifecycle this register holds |
| Upstream | `project_content/_AUDIT/` (22), `project-guide-doc/_AUDIT/` (15) | The 326-finding population |
| Upstream | `00-06` §9 | The two controls ratified at §8.3 |
| Upstream | `BM-002`, `BM-003`, `BM-004` | 18 of the 24 findings seeded at §7.4 |
| Upstream | `BM-004` §9.4 | Miss decisions become lessons |
| Downstream | `GV-003` | Ratification decisions and landing sites that are decisions (`LLR-12`) |
| Downstream | `GV-005` | Unowned findings and escalations (`LLR-03`) |
| Downstream | **`PGD-000`**, `15/_CATEGORY_OVERVIEW.md` | The *"19+"* correction (`LLR-F-01`) |
| Downstream | `GV-009` | Critical entries past `landing_date` at each gate |
| Downstream | `RL-005` | Aged unclosed lessons opening every wave review (`PIR-36`, operable via `LLR-02`) |
| Lateral | `GV-010` | Third-line independence; samples `self_raised` first (`LLR-15`) |
| Lateral | `GV-011` | Register custody and retention |
| Lateral | `RR-002` | Identifier convention — `LSN-nnn` registered there |
| Lateral | `RR-005` ⛔ | Required for §8.3 `R2`'s re-verification half |
| Lateral | `QA-010` | Defects enter only where the cause is a process cause |

---

## 17. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./BM-002_KPI_Baseline_Measurement_Report.md` · `./BM-003_Business_Case_and_ROI_Model.md` ·
`./BM-004_Benefits_Realisation_Plan.md` ·
`../00_Programme_Governance_and_Control/GV-003_Decision_Log_and_Change_Control_Procedure.md` ·
`../00_Programme_Governance_and_Control/GV-005_RAID_Register.md` ·
`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md` ·
`../00_Programme_Governance_and_Control/GV-010_Programme_Assurance_and_Independent_Review_Plan.md` ·
`../00_Programme_Governance_and_Control/GV-011_Documentation_Control_and_Configuration_Management_Plan.md` ·
`../12_Release_Deployment_and_Transition/RL-005_Post_Implementation_Review_Standard.md` ·
`../99_Reference_Registers_and_Glossary/RR-002_Identifier_Convention_Standard.md` · `../_AUDIT/`

**Workspace**
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-06_Documentation_Audit_Report.md` §9 ·
`../../project_content/_AUDIT/` (22 documents) · `../../project_content/_AUDIT/AUDIT_Checklist_Recurring.md`

**External standards and sources**

| Source | Edition relied on | Verified |
|---|---|---|
| ISO 9001 — Quality management systems, **§10.2** and §9.3 | **2015** | 2026-08-19 |
| PRINCE2 — Learn from Experience; lessons log and report | **7th edition (PRINCE2 7)** | 2026-08-19 |
| MSP — Managing Successful Programmes | **5th edition**, PeopleCert | 2026-08-19 |
| ISO 21502 — Guidance on project management | **2020** | 2026-08-19 |
| ISO 21503 — Guidance on programme management | **2022** | 2026-08-19 |
| **IIA Global Internal Audit Standards** | **2024** — released 9 January 2024, **effective 9 January 2025**; 5 domains, 15 principles, 52 standards | **2026-08-19** |
| The IIA **Three Lines Model** | **2020** *(supersedes the 2013 Three Lines of Defence)* | 2026-08-19 |
| ISO 31000 — Risk management | **2018** | 2026-08-19 |

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | PMO for the Programme Director | Initial issue. Counts the backlog at **326 findings, 219 open (67.2%)** against a published figure of *"19+"* (`LLR-F-01`). Establishes that **no finding in the estate carries an age** (`LLR-F-02`) and that **the `RG-08` recurrence count is itself inconsistent across five documents** (`LLR-F-03`). Adopts `PIR-33`…`PIR-38` verbatim; discharges `PIR-37` by naming and migrating the interim register. Seeds the 19 Critical open findings with landing sites and owners, and seeds this category's own **24** authoring findings at issue. Puts **five ratification decisions** `R1`–`R5` to the Steering Committee, including `RG-08` at its tenth recommendation, and re-lands it at `GV-003` where it can actually be ratified. Six new findings `LLR-F-01`…`LLR-F-06` | ERP Steering Committee |

---

*`BM-005` · Category 15 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
