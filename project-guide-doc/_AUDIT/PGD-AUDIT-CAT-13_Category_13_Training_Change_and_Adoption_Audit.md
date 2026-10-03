---
id: PGD-AUDIT-CAT-13
title: Category 13 — Training, Change & Adoption Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Enterprise Architecture (self-audit — see §1.3 on independence)
scope: >
  The five Category 13 CH documents, the five identifier spaces they allocate, every figure they
  compute, every absence they assert, their citations into the four source repositories and into
  Categories 00–12, the PGD-000 register rows they change, and the concurrent-authoring condition
  observed during the audit window.
mandate: Audit required on completion of a category
extends: PGD-AUDIT-001 … PGD-AUDIT-009, PGD-AUDIT-CAT-07, PGD-AUDIT-CAT-08, PGD-AUDIT-CAT-09
enumeration_timestamp: 2026-08-19 02:10 (+06)
method: >
  Filesystem enumeration and identifier extraction only (RG-06, PG-03). No figure in this report is
  projected, and none is taken from what a document says about itself — including this category's
  own files, and including what PGD-000 says about categories this one depends on. Every command is
  stated so the result can be reproduced.
---

# Category 13 `CH` — Training, Change & Adoption Audit
### 5 documents · 3,829 lines · 128 governing rules · 42 open questions · 15 findings, 1 critical

---

## 1. Method and result

### 1.1 What was run

Fifteen extractions, by direct enumeration, never by reading what a document says about itself.
**Enumeration timestamp 2026-08-19 02:10 (+06).**

| # | Extraction | What was compared |
|:--:|---|---|
| **X1** | File and structure | Files on disk against the `PGD-000` Category 13 rows, both directions |
| **X2** | Front matter | All 20 required keys of `_templates/TPL_Guiding_Document.md` in all five files |
| **X3** | Section conformance | Purpose · Scope · Audience · Basis · Governing Rules · Open Questions · Decisions Recorded · Acceptance Criteria · Traceability · References · Revision History |
| **X4** | **Rule-prefix collision** | Each allocated prefix against every `[A-Z]{2,3}-nn` occurrence in all five repositories |
| **X5** | Rule-ID contiguity and uniqueness | Within each prefix, `01`…`nn`, no gaps, no duplicates |
| **X6** | Relative links | Every markdown link with a `.md` target, resolved with `test -e` |
| **X7** | **Identifier resolution** | Every `RSK-`, `KPI-`, `BRU-`, `Gn-nn`, `FR-LMS-`, `CU-`, `LS-`, `PK-`, `SK-`, `CA-`, `UP-`, `NW-`, `RN-`, `HD-`, `QB-`, `ASM-`, `DEP-`, `CON-` cited, against its owning file |
| **X8** | Document-ID resolution | Every `TR-`, `CM-`, `OP-`, `SP-`, `KB-`, `LG-`, `MD-`, `DM-`, `RP-`, `TS-`, `EO-`, `BN-`, `CG-`, `NT-` against `project_content`; every `GV-`, `RQ-`, `AR-`, `SC-`, `UX-`, `QA-`, `MG-`, `RL-`, `SV-`, `CH-`, `CO-`, `BM-`, `RR-`, `PE-` against `PGD-000` |
| **X9** | Module and portal IDs | Every `Mnn` and `Pnn` against the filesystem |
| **X10** | **Every absence assertion** | Each statement that a document does not exist, tested with `find` |
| **X11** | **Arithmetic reproduction** | Every computed figure re-derived from `05-04` headcounts and `TR-007`…`TR-023` Duration lines |
| **X12** | **Cross-document figure consistency** | Every figure appearing in more than one `CH` document |
| **X13** | Standards currency | Every standard, statute and vendor version cited, against its current published edition |
| **X14** | Register reflection | `PGD-000`, `README.md`, `FOLDER_STRUCTURE.md` Category 13 rows against disk |
| **X15** | Baseline movement | The whole estate re-enumerated at the start and end of the audit window |

### 1.2 Result

**Fifteen findings — 1 critical, 5 high, 6 medium, 3 low. Four were remediated during the audit;
eleven are open, and eight of those are owned outside this category.**

| Severity | Count | Fixed | Open |
|---|---:|---:|---:|
| **Critical** | 1 | **1** | 0 |
| High | 5 | 0 | 5 |
| Medium | 6 | 3 | 3 |
| Low | 3 | 0 | 3 |
| **Total** | **15** | **4** | **11** |

> **The Critical finding is against the auditor's own authoring, and it is the reason this report
> exists in the form it does.** `CHA-12` records that seven absence assertions written into these
> five documents were **false by the time the documents were finished**, because Categories 10, 11
> and 12 were authored by other sessions inside the same two-hour window. It is `AUDIT-019` `CM-01`
> occurring again, in a different repository, to the author who wrote the control against it.

### 1.3 Independence

This is a **self-audit**. Enterprise Architecture authored the five documents and audited them, as
Category 09 and Category 10 did before it. The mitigation is method, not independence: every check
is an extraction with a stated command, and §7 lists every change made during the audit. Where the
auditor's own work produced a finding, the convention inherited from `00-07` applies — **the cause
is stated, not only the fix**.

---

## 2. Checks that passed

| Check | Result |
|---|---|
| **X1** File count | **5 of 5** registered documents on disk; zero files with no register row; zero rows with no file ✅ |
| **X1** File name matches ID | 5 of 5 ✅ |
| **X2** Front matter | **All 20 required keys present in all 5 files** ✅ |
| **X3** Section conformance | All eleven required sections present in all five, in order ✅ |
| **X4** Rule-prefix collision | **`OCM`, `TPD`, `SEP`, `ADP`, `CNC` — all five return zero occurrences outside this category, across all five repositories** ✅ |
| **X5** Rule-ID integrity | **128 rules, 5 prefixes, contiguous `01`…`nn` with no gaps and no duplicates**: `OCM` 33, `TPD` 24, `SEP` 24, `ADP` 24, `CNC` 23 ✅ |
| **X6** Relative links | **37 distinct links, zero broken** (36 before this report existed) ✅ |
| **X7** Rule-identifier resolution | **134 distinct identifiers across 18 spaces, all 134 resolve** ✅ |
| **X8** Document-ID resolution | **64 content IDs and 39 PGD IDs, all resolve**; every PGD ID appears as a registered row in `PGD-000` ✅ |
| **X9** Module and portal IDs | **9 modules and 11 portals, all on disk** ✅ |
| **X11** Arithmetic reproduction | Every figure re-derived; **one defect found and fixed** — `CHA-08` |
| **X13** Standards currency | 16 standards and statutes; **all carry an edition and a verification date of 2026-08-19**; four inherited undated citations corrected — `CHA-05` |
| Open questions | **42, every one with a named owner and a needed-by date** ✅ |
| Decisions recorded | **31 local decisions**, all in the `CH-00n-D-nn` form; **no bare `D-nn`** — rule `DL-06` held ✅ |

### 2.1 What the category contains

| Measure | Value | Command |
|---|---:|---|
| Documents | 5 | `ls CH-*.md` |
| Lines | **3,829** | `wc -l CH-*.md` |
| Bytes | **276 KB** (282,196) | `cat CH-*.md \| wc -c` |
| Governing rules | **128** across 5 prefixes | `grep -ho "<PRE>-[0-9][0-9]" \| sort -u \| wc -l` |
| Open questions | **42** | `grep -ho "<PRE>-Q-[0-9][0-9]" \| sort -u \| wc -l` |
| Local decisions | **31** | `grep -ho "CH-00[0-9]-D-[0-9][0-9]" \| sort -u \| wc -l` |
| Relative links | 37, all resolving | X6 |
| Distinct identifiers cited | **257**, all resolving | X7 + X8 + X9 |

### 2.2 What the category established that did not exist before

**`PG-03` requires figures to be counted at the time of writing. These nine were.**

| Fact | Low | High | Derivation |
|---|---:|---:|---|
| People requiring a curriculum | **752** | **1,428** | Σ `05-04` §5 headcount bounds + 20–60 unregistered field auditors |
| **Formal learner-hours** | **12,306** | **21,759** | (pop × 5.5 h Layer 1) + Σ(pop × declared pack duration) + (142–180 × 16 h `TR-023`) |
| — as production time | **308 PW** | **544 PW** | ÷ 8 h/day ÷ 5 days |
| W1 + W2 share | **75.3%** | **67.0%** | Wave assignment from `TR-002` §5 |
| **Trainer-days incl. preparation** | **380** | **525** | Cohort 12 · 6 h delivery day · 2:1 preparation |
| Bengali-capable trainer FTE at peak | **2.8** | **3.5** | W1–W2 trainer-days ÷ 168 working days ÷ 60% utilisation |
| — established today | **0** | **0** | `TR-001` `O-04`; `GV-007` §8.1 |
| Declared OJT supervision | **733** | **1,465** supervisor-days | Σ(pop × declared OJT days) × 20% |
| **Champion + super-user released time** | **1,190 PW** | **1,622 PW** | `06-01` §4 × `06-01` §3 wave months |

> **Every one of these numbers is new.** No file in the 772-file estate contained any of them
> before 2026-08-19, and `TR-001` `LS-11`, `LS-12` and `AUDIT-009` `R-07` had all required them.

---

## 3. Findings

### CHA-12 — Seven absence assertions were false by the time the documents were finished

**Severity: CRITICAL · Status: FIXED during the audit · Owner: Enterprise Architecture — the
auditor's own authoring**

**What was found.** Extraction **X10** tested every statement in the five documents that a document
does not exist. Seven were false:

| Assertion as drafted | Reality at 02:10 |
|---|---|
| *"`RL-003` (Go-Live Readiness Assessment) is ⛔ and unwritten"* — stated **five times** in `CH-001` | `RL-003_Go_Live_Readiness_Assessment_and_Gate_Criteria.md` **exists** |
| *"`RL-001` (⛔ unwritten)"* | `RL-001` **exists** |
| *"`RL-002` Deployment Plan ⛔"* | `RL-002` **exists** |
| *"`RL-004` Rollout & Branch Wave Deployment Plan ⛔"* — stated **four times** | `RL-004` **exists** |
| *"⛔ `PE-002`, `PE-007` absent"* — stated **three times** in `CH-002` | Both **exist** |
| *"DPIA `SC-003` ⛔ unwritten"* | `SC-003_Data_Protection_Impact_Assessment_PDPA_2026.md` **exists** |
| *"`12_Release` ⛔"* in the category overview | Four `RL` documents on disk |

**How it happened, stated plainly.** The first enumeration of this authoring session ran at
**2026-08-19 01:20 (+06)** and returned `project-guide-doc` at **131 `.md` files**, with Categories
10, 11 and 12 holding **only their `_CATEGORY_OVERVIEW.md`**. That enumeration was correct. The
re-enumeration at **02:08** returned **151 `.md` files**: Category 10 had gained **nine `PE`
documents and an audit**, Category 11 `SV-001`, and Category 12 **four `RL` documents**. **Twenty
files were written by other sessions in forty-eight minutes**, while this category was being
authored.

**Why it is Critical.** The recurring checklist defines Critical as *"work done against the wrong
artefact, or a required artefact assumed present when absent."* This is the mirror image and no
less damaging — and `AUDIT-019` `CM-01` already established that:

- `CH-001` §7 was written on the premise that **no document held go-live gate authority**, and
  designed itself around that absence. `RL-003` now holds it. The design decision (`CH-001-D-04`)
  turns out to have been **right for a reason that had not happened yet**, but the seven
  people-readiness criteria have **never been read against `RL-003`'s gate criteria**.
- `CH-002` §9 declared the training environment blocked on two documents that **now exist**. The
  substance is unchanged — an environment specified is not an environment built — but the
  *statement* was wrong.
- `CH-004` §9 recorded the DPIA as unwritten while `SC-003` was on disk, which is exactly
  `AUDIT-019`'s `OJ-11` case: *"the monitoring disclosure does not exist"* against a written file.

**And the control this category wrote is what caught it.** `OCM-02` requires a category author to
enumerate every category they cite, at the moment of authoring, and record the timestamp.
**The timestamp is what made the staleness visible**: without it, the 131 figure would have been
undated and unfalsifiable. The rule worked. **What it does not do is stop the estate moving**, and
nothing a document can contain will.

**Remediation applied.** All seven assertions corrected; **eight relative links added** into
Categories 05, 10 and 12; three new open questions raised where the correction opened a real
question rather than closing one — `OCM-Q-09` (reconcile `CH-001` §7.2 with `RL-003`),
`TPD-Q-11` (does `PE-002`'s environment set include a training environment?), `ADP-Q-08` (does
`SC-003` cover workforce adoption telemetry?). **Each of the three is a better question than the
absence claim it replaced**, which is the same pattern `AUDIT-019` §5 recorded.

**This is at least the ninth recorded instance of a baseline moving during authoring** —
`PGD-A1-03`, `AUDIT-016` `AP-17`, `AUDIT-014` `TS-11`, `AUDIT-019` `CM-14`, `MGA-15`, and the four
recorded in `PGD-000` §0.5. **Proposed rule `RG-08` has now been recommended eight times and never
ratified**, and `RR-002` (Identifier Convention Standard) with it.

---

### CHA-13 — The statutory basis of mandatory training has moved twice and the estate cites the unamended text

**Severity: HIGH · Status: OPEN · Owner: HSE Lead with Legal Counsel**

**What was found.** `TR-001` §4.9 and `AUDIT-009` `TR-01` — the estate's **only CRITICAL content
finding** — rest their severity on *"Bangladesh Labour Act 2006 with Labour Rules 2015"*, cited with
no amendment and no verification date.

| Instrument | Position, verified 2026-08-19 |
|---|---|
| Bangladesh Labour Act 2006 | In force, **substantially amended** |
| **Bangladesh Labour (Amendment) Ordinance 2025** | **Ordinance No. 65 of 2025, gazetted 17 November 2025** |
| **Bangladesh Labour (Amendment) Act 2026** | Parliamentary enactment following the Ordinance |
| Bangladesh Labour Rules 2015 | **As amended 2022** — 99 rule modifications |
| Scale of change | **Approximately ninety changes** across the two 2025/2026 instruments |

**Substantive changes that touch training obligations:**

- **§90A as amended** — safety committee required in establishments with **50 or more workers**.
- **§61A, new** — a worker's right to **refuse dangerous work without retaliation**. A right the
  workforce has not been told it holds is a right that does not operate; it is a training item.
- **§332 and §332A** — a **five-member complaint committee** on violence and harassment in **every
  establishment**, with a female chairperson and a majority of women members. See `CHA-06`.

**Why it matters.** `LS-10` makes statutory training non-deferrable and `AUDIT-009` `TR-01` is
Critical *because* the obligation is statutory. **A Critical finding whose statutory basis is cited
from a superseded text is a Critical finding nobody can act on with confidence.** This is the
`C-04` defect class — DSA 2018 recorded as current after two repeals — with a labour-law
consequence.

**Remediation instruction.** `AUDIT-009` `R-06` (*confirm the statutory training obligations with
Legal*) is **re-dated to W0 and re-scoped to the current text**. `CH-002` §2.1 and §3.3 carry the
corrected citation; `TR-001` §4.9 has not been corrected and is outside this category's authority.
**`RR-005` — the Standards & Regulatory Currency Register — is the durable fix, is ⛔, and is now
needed by a fourth category.**

---

### CHA-06 — The complaint-committee training obligation is registered nowhere in the estate

**Severity: HIGH · Status: OPEN · Owner: HR Director with Legal Counsel**

**What was found.** The Labour (Amendment) Ordinance 2025 §332/§332A require **every establishment**
to constitute a five-member complaint committee on violence and harassment, with a female
chairperson and a majority of women members. With **51+ sites**, that is **255+ committee members**.

Extraction against `project_content` returns **zero** files covering complaint-committee
constitution, member training or case handling:

| Candidate owner | Position |
|---|---|
| `TR-002` §4.2 Layer 1 universal core | Seven modules; **none covers it** |
| `TR-015` HR and Payroll pack | Covers payroll, attendance, leave, onboarding |
| `SP-*` procedure set | No complaint-committee SOP |
| `LG-023` anti-bribery, ethics and speaking up | The nearest, and it is a **content** file about ethics, not a committee constitution or a member curriculum |

**Why it matters.** It is the same defect as `AUDIT-009` `TR-01` — a statutory training obligation
with no owning file — **discovered in the same category, one instrument later**, and it was not
findable before November 2025 because the obligation did not exist.

**Remediation instruction.** Register the obligation, decide its owner, and decide whether it
belongs in Layer 1 (all employees, awareness) with a separate committee-member curriculum
(255+ people). It is a Steering decision of the same class as `TR-025`.

---

### CHA-10 — `06-01` §4's champion commitment is ambiguous by a factor of 4.5, and it is the line the document calls the binding constraint

**Severity: HIGH · Status: OPEN · Owner: Programme Director with the Operations Director**

**What was found.** `06-01` §4 commits *"Branch Champions (1 per branch) — **4 hours/week during
rollout** — W1–W5"* and states, in the same section, *"**this is the binding constraint on the
programme**."*

| Reading | Basis | Per champion | × 51 | × 60 |
|---|---|---:|---:|---:|
| **Broad** — 4 h/week across the whole W1–W5 period (months 1–22 = 95.3 weeks) | 95.3 × 4 h | **381 h** | **486 PW** | **572 PW** |
| **Narrow** — 4 h/week inside the site's own 12-week window, plus a monthly forum for 36 months | (12 × 4) + 36 | **84 h** | **107 PW** | **126 PW** |

**Why it is High.** Nothing in the estate resolves it, and **no release letter can be written until
it is resolved** — `CH-005` §5.4 item 3 requires the hours and the period in the letter. The
difference is **379–446 person-weeks**, which is larger than the entire 140-document Engineering
Definition workstream (`GV-007` §8.1: 352 PW).

**Remediation instruction.** `CNC-Q-01`. A `GV-003` `D-nnn` by **W1 − 10 weeks**.

---

### CHA-11 — Data owners are committed by `06-01` §4 at 381–972 person-weeks and owned by no document in the estate

**Severity: HIGH · Status: OPEN · Owner: Data Migration Lead with the Operations Director**

**What was found.** `06-01` §4's business-side commitment table has three rows. Two are owned:
super-users by `CH-005` and `QA-009`, champions by `CH-005` and `CM-008`. The third —
**"Data Owners — 20% during migration — W1–W5"** — is owned by nothing.

| Population | Commitment | Computed |
|---|---|---:|
| Data owners, 20 people | 20% × 22 months | **88 person-months = 381 PW** |
| Data owners, 51 people (one per site) | 20% × 22 months | **224 person-months = 972 PW** |

`MG-004`'s reconciliation cannot be signed by anyone else, and `CH-001` `PR-6` makes the data
owner's signature a **site readiness criterion**. `MG-001`…`MG-007` specify the migration; none
releases the people.

**Remediation instruction.** `CNC-Q-06`. Either `MG-001` or `CH-005` takes ownership, or a new
register row is raised. **The population is not even enumerated** — 20 or 51 is a 2.5× range.

---

### CHA-15 — 1,000–4,000 marketplace seller technicians must pass a qualification that no file specifies

**Severity: HIGH · Status: OPEN · Owner: CCO with Marketplace Operations and the Training Lead**

**What was found.** `OP-001` §4.1 enumerates **marketplace seller technicians at 1,000–4,000** —
**the largest external population in the estate**. `BRU-LMS-02` gates their category activation on
passing that category's qualification.

| Question | Answer |
|---|---|
| Which file specifies the qualification? | **None.** `TR-019` prepares the *operations officer* to administer it |
| Which file specifies its content? | **None** in `TR` or `EO` |
| Which file registers them as a stakeholder group? | **None.** `CM-002` §4.3 omits them entirely (`AUDIT-019` `CM-08`) |
| Who owns their communication? | **Nobody** |

`CU-04` correctly places external parties in Category 18 `EO`, and `EO` has not specified it either.
**A Class-`H` business rule gates an activation on an artefact that does not exist, for a
population 1.4× the size of the entire internal workforce.**

**Remediation instruction.** `CH-002` `TPD-Q-06` and `CH-003` `SEP-Q-05`. Needed by W7 − 20 weeks,
which given a 1,000–4,000-person population is not generous.

---

### CHA-01 — The role register's population bounds sum to 1,368 against a workforce described as 500–900

**Severity: MEDIUM · Status: OPEN · Owner: HR Director with MDM**

**What was found.** Summing the headcount column of `05-04` §5 across all 35 internal roles:

| | Low | High |
|---|---:|---:|
| Σ registered internal role bounds | **732** | **1,368** |
| Estate's stated workforce (`TR-001`, `CM-002` `S17`, `M66` §2) | 500 | 900–1,000 |

**The upper bounds cannot all be true simultaneously.** Every downstream figure — cohort count,
trainer-days, translation volume, learner-time cost, licence count — is driven by them, and the
high case is **87% larger** than the low case.

**Why it is Medium rather than High.** Both bounds are stated and this category's figures are given
as ranges, so nothing is concealed. It becomes High the moment a budget is set from either end.

**Remediation instruction.** `CH-001` `OCM-Q-02`. Reconcile in `MD-009` and `05-04`.

---

### CHA-03 — 51–60 cashiers are routed to a 10-hour finance core built for 16–34 head-office staff

**Severity: MEDIUM · Status: OPEN · Owner: Training Lead with the Finance Manager**

**What was found.** `TR-002` §5.5 routes `R29` Cashier / Counter Finance to `TR-014` — *"Course Pack
Finance Officer and Manager"* — plus a 3-hour counter-cash module. `TR-014`'s core is **10 hours
over three days**.

| | Population | Route | Hours each | Total |
|---|---:|---|---:|---:|
| `R26`–`R28` head-office finance | 16 – 34 | `TR-014` core (+ modules) | 10 – 14 | 176 – 452 |
| **`R29` Cashiers** | **51 – 60** | **`TR-014` core + counter cash** | **13** | **663 – 780** |

**The cashier population is 1.8× to 3.2× the size of the population the pack was designed for, and
consumes more learner-hours than that population does.** A dedicated 3–4 hour counter-cash route
would deliver the same competence in roughly a quarter of the time.

**Why it is Medium.** It is an efficiency finding, not a competence gap: a cashier who completes
`TR-014` is over-trained, not under-trained. It becomes material at 51+ sites and at
`CHA-10`-scale released time.

**Remediation instruction.** `CH-002` `TPD-Q-03`, by W1 − 8 weeks. `CH-002` schedules the route
**as declared** — `CP-01` forbids inventing curriculum in a guiding document — and flags it.

---

### CHA-07 — `TR-002` §6.2's wave learner-hours cannot be reproduced from the durations its own packs declare

**Severity: MEDIUM · Status: OPEN · Owner: Programme Content Lead with L&D**

**What was found.** Extraction **X11** re-derived the wave load from `05-04` populations and the
`TR-007`…`TR-021` **Duration** lines:

| Wave | `TR-002` §6.2 states | **Computed 2026-08-19** |
|:--:|---|---|
| W1 | ~3,000 – 4,500 | **4,809 – 7,060** |
| W2 | ~4,000 – 7,000 | **2,749 – 5,580** |

**`TR-002` puts W2 above W1; the computation reverses it**, because the technician population takes
a 6-hour microlearning pack while W1 carries branch managers (12 h), cashiers (13 h) and 150–250
agents. Neither candidate reconciliation produces `TR-002`'s figures: **excluding Layer 1** gives
W2 = 1,398–3,978; **including the declared 10-day OJT** gives W2 above 20,000.

**Why it matters, and why it is only Medium.** `TR-002`'s qualitative conclusion — *"W1 and W2
together carry roughly 80% of the total learner load"* — **survives and is confirmed at 67%–75%**.
The defect is in the components, not the conclusion, which is the `PGD-A2-24` pattern: *a correct
total concealing wrong components*.

**Remediation instruction.** `TR-002` §6.2 to be regenerated by its owner from the pack durations,
not adjusted. Outside this category's authority (`CP-01`).

---

### CHA-05 — Four undated standards citations, inherited from this category's own overview

**Severity: MEDIUM · Status: FIXED during the audit · Owner: Enterprise Architecture**

**What was found.** The previous `_CATEGORY_OVERVIEW.md` cited *"Prosci ADKAR · Kotter 8-step ·
Kirkpatrick training evaluation · ISO 30401 (knowledge management)"* — four citations, **no edition
and no verification date on any of them**, in an estate with three critical findings caused by
stale citations.

| Citation as written | Position verified 2026-08-19 |
|---|---|
| *"Kotter 8-step"* | The **1995 linear model**. Kotter evolved it into the **8 Accelerators and dual operating system** (*Accelerate*, HBR 2012 / book 2014; *CHANGE*, 2021) — which is the model a nine-wave, 36-month programme actually needs |
| *"ISO 30401"* | Current is **ISO 30401:2018 + Amd 1:2022 + Amd 2:2024**, and **ISO/DIS 30401 is in the enquiry phase and will replace the 2018 edition** |
| *"Kirkpatrick"* | The **New World Kirkpatrick** model, with Required Drivers, is what `TR-001` §4.1–4.3 actually implements |
| *(absent)* | **The ACMP Standard for Change Management Version 2 was released 26 August 2025** — the professional standard for `CH-001` — and was cited nowhere |
| *(absent)* | **ISO 10015:2019**, the ISO standard for competence management and people development — the governing standard for `CH-002` — was cited nowhere |

**Remediation applied.** The overview's standards line now carries **16 standards, each with an
edition and a verification date of 2026-08-19**, and `CH-001-D-01` and `CH-001-D-02` record the two
substantive choices with rationale.

---

### CHA-02 — `CH-nnn` document identifiers collide by digit count with `CH-nn` rule prefixes in three files

**Severity: MEDIUM · Status: OPEN (contained) · Owner: Programme Content Lead**

**What was found.** Extraction **X4** found `CH-nn` already in use as a **rule** prefix:

| Owner | Rules | Meaning |
|---|---|---|
| `NT-001` §4 | `CH-01`…`CH-06` | Notification **channel** rules |
| `RP-007` | `CH-01`…`CH-05` | **Chart** rules |
| `OP-001` | `CH-01` | Support **channel** rule |

The register allocated `CH` as Category 13's document code, giving `CH-001`…`CH-005`. **A
`CH-\d{2,3}` sweep returns both spaces**, exactly as `MG-nn`/`MG-nnn` did in Category 09 (`MGA-04`)
and `MIG-nn`/`MIG-nnn` before it. It is the **third** recorded instance of this collision class.

**How it is contained.** **No document in Category 13 uses `CH-nn` as a local rule prefix**, and all
five allocated prefixes (`OCM`, `TPD`, `SEP`, `ADP`, `CNC`) were verified to return **zero**
workspace-wide occurrences before allocation. The containment is identical to Category 09's.

**Remediation instruction.** **`RR-002` — the Identifier Convention Standard — is the fix, and this
is the ninth time it has been recommended.** It is ⛔, `P0`, `needed_by: Now`.

---

### CHA-08 — A rule in one document invalidated a total in another; found by self-audit and corrected before issue

**Severity: MEDIUM · Status: FIXED during the audit · Owner: Enterprise Architecture**

**What was found.** Extraction **X12** compared every figure appearing in more than one `CH`
document. One disagreed with itself:

- `CH-005` `CNC-13` requires that **deputies are trained, not merely named** — 51+ deputies each
  taking the 16-hour `TR-023`.
- `CH-002` §4.4 had costed `TR-023` at **91–120 people** (51–60 champions + 40–60 super-users),
  **with no deputies**, and `CH-005` §7.1 asserted that `CH-002` *"already counts 91–120 people on
  the assumption that deputies are included"* — which was simply untrue.

**Effect of the error.**

| Figure | As drafted | Corrected |
|---|---:|---:|
| `TR-023` population | 91 – 120 | **142 – 180** |
| `TR-023` learner-hours | 1,456 – 1,920 | **2,272 – 2,880** |
| Total formal learner-hours | 11,490 – 20,799 | **12,306 – 21,759** |
| — as production time | 287 – 520 PW | **308 – 544 PW** |
| `TR-023` trainer-days | 19 – 21 | **27 – 32** |
| Total trainer effort | 356 – 493 | **380 – 525** |
| Peak trainer FTE | 2.7 – 3.3 | **2.8 – 3.5** |

**Why it is worth a finding rather than a silent fix.** It is a **new instance of a known defect
class in this estate**: a figure that is right in the document that computes it and wrong in the
document that consumes it, because a rule changed on one side. `PG-M10` exists for exactly this and
says **regenerate, do not adjust** — which is what was done: the totals were recomputed from the
inputs, not patched by the delta.

**Remediation applied.** Twelve figures corrected across `CH-001`, `CH-002` and `CH-005`, and the
false claim in `CH-005` §7.1 rewritten to state the arithmetic rather than assert it.

---

### CHA-04 — `TR-017` states a contact-centre population 33% larger than the role register

**Severity: LOW · Status: OPEN (inherited) · Owner: Programme Content Lead with the Contact Centre**

**What was found.** `TR-017`'s register row states *"30–80 agents"*; `05-04` registers **`R34` at
30–60**. `AUDIT-009` `TR-06` raised it on 2026-08-17 and it is unresolved.

`CH-002` §4.2 uses `05-04`'s figure, because `CU-01` and `SK-02` make the role register govern, and
records the divergence. At a cohort of 12, **60 agents is 5 cohorts and 80 is 7 — a 40% delivery
effort difference for a 12-hour course**.

**Why it is Low here.** It is an inherited open finding correctly handled, not a new defect.

---

### CHA-09 — `PGD-000`'s enumeration timestamp postdates its own file modification time by ten and a half hours

**Severity: LOW · Status: OPEN · Owner: Enterprise Architecture**

**What was found.**

| Attribute | Value |
|---|---|
| `PGD-000` front matter | `enumeration_timestamp: 2026-08-19 09:40 (+06)` |
| §3 Register Control | *"Enumeration timestamp **2026-08-19 09:40 (+06)**"* |
| **File modification time on disk** | **2026-08-18 23:05** |

**A file cannot record an enumeration taken ten and a half hours after it was last written.** Every
other session in this repository has stamped `(+06)` from the same machine clock — the Category 09
documents carry `2026-08-18 22:55 (+06)` against mtimes of 22:37–22:41, which is consistent.

**Consequences that follow from it.** The register also states `project-guide-doc` at **136** files
in §3 and **133** in the front-matter revision note. Enumeration at **01:20** returned **131**, and
at **02:08** returned **151**. **Neither 133 nor 136 is reproducible at any point in the window**,
and the timestamp that would let a reader tell which is a floor is itself wrong.

**Why it is Low.** No downstream figure depends on it. It matters because `PG-M11` and `RG-08` exist
precisely so that a stale figure can be told from a fresh one, and a timestamp that cannot be true
disables the control it belongs to.

**Remediation instruction.** Re-stamp at the next issue of `PGD-000` from the same clock used to
enumerate. This report's own stamp, **2026-08-19 02:10 (+06)**, is within four minutes of the
enumeration and two of the write.

---

### CHA-14 — The register, README and folder structure did not reflect this category, and their counts were stale

**Severity: LOW · Status: FIXED during the audit · Owner: Enterprise Architecture**

**What was found.** Before remediation:

| Artefact | Stated | Actual at 02:10 |
|---|---|---|
| `PGD-000` §0.5 Category 13 row | 0 ✅ / 4 ◐ / 0 ⬜ / 1 ⛔ | **5 ✅** |
| `PGD-000` §0.5 total | 99 ✅ / 18 ◐ / 7 ⬜ / 16 ⛔ | Regenerated in §7 |
| `PGD-000` §3 documents authored | 99 | Regenerated |
| `README.md` | *"140 registered · 45 written (register) · 51 on disk"* | Long stale — **written by an authoring session on 2026-08-18 17:20** |
| `FOLDER_STRUCTURE.md` Category 13 | *"CH — 5 documents"*, no status | Updated |

**Remediation applied.** §7. The `PGD-000` totals were **regenerated by recounting all seventeen
category rows** (`PG-M10`), not by applying a delta — and the recount is stated with its arithmetic
so that a wrong component cannot hide inside a correct total (`PGD-A2-24`).

---

## 4. Findings summary

| ID | Severity | Finding | Owner | Status |
|---|:--:|---|---|:--:|
| **`CHA-12`** | **CRITICAL** | Seven absence assertions false by the time the documents were finished; 20 files written by other sessions in 48 minutes | Enterprise Architecture | **Fixed** |
| `CHA-13` | High | The statutory basis of mandatory training has moved twice; the estate cites the unamended 2006/2015 text | HSE Lead with Legal | Open |
| `CHA-06` | High | The Ordinance 2025 §332/§332A complaint-committee training obligation (255+ people) is registered nowhere | HR Director with Legal | Open |
| `CHA-10` | High | `06-01` §4's champion commitment is ambiguous by 4.5× — a 379–446 PW difference | Programme Director | Open |
| `CHA-11` | High | Data owners, 381–972 PW, committed by `06-01` §4 and owned by no document | Data Migration Lead | Open |
| `CHA-15` | High | 1,000–4,000 seller technicians gated by `BRU-LMS-02` on a qualification no file specifies | CCO with Marketplace Ops | Open |
| `CHA-01` | Medium | Role-register upper bounds sum to 1,368 against a workforce of 500–900 | HR Director with MDM | Open |
| `CHA-03` | Medium | 51–60 cashiers on a 10-hour head-office finance core — 663–780 learner-hours | Training Lead with Finance | Open |
| `CHA-07` | Medium | `TR-002` §6.2's wave learner-hours are unreproducible from its own packs | Programme Content Lead | Open |
| `CHA-05` | Medium | Four undated standards citations inherited from the category overview | Enterprise Architecture | **Fixed** |
| `CHA-02` | Medium | `CH-nnn` collides by digit count with `CH-nn` rule prefixes in three files | Programme Content Lead | Open *(contained)* |
| `CHA-08` | Medium | `CNC-13` invalidated `CH-002`'s `TR-023` total; twelve figures recomputed | Enterprise Architecture | **Fixed** |
| `CHA-04` | Low | `TR-017` states 30–80 agents against `05-04`'s 30–60 | Programme Content Lead | Open *(inherited)* |
| `CHA-09` | Low | `PGD-000`'s enumeration timestamp postdates its own mtime by 10.5 hours | Enterprise Architecture | Open |
| `CHA-14` | Low | Register, README and folder structure did not reflect this category | Enterprise Architecture | **Fixed** |

---

## 5. Inbound findings — position after this category

### 5.1 Discharged at the specification layer

| Finding | Source | Severity | How |
|---|---|:--:|---|
| **`CM-01`** — the `CM` set authored against a stale register | `AUDIT-019` | **CRITICAL** | `OCM-02` makes the register non-authoritative for existence; `OCM-13` expires an impact assessment twelve weeks after its sources' enumeration stamp. **`CHA-12` demonstrates that the control makes staleness visible and does not prevent it** — which is the honest limit of a documentary control |
| **`TR-04`** — assessment instruments after the packs that assess against them | `AUDIT-009` | High | `CH-002` §8.2 brings a **defined** minimum-viable `TR-005`/`TR-006` cell set to W1 for the nine affected packs, and `TPD-16` makes the alternative a recorded, dated, ended exception |
| **`CM-03`** — two current wave calendars | `AUDIT-019` | High | `CH-003` §3 declares `06-01` §3/§8 with `06-02` §4, quantifies the divergence wave by wave (**+2 to +6 months**), and assigns four named corrections |
| **`CM-08`** — divergent external enumerations | `AUDIT-019` | Medium | `CH-003` §4.1 adopts `OP-001` §4.1 and reconciles five rows, **one of them running the other way** so that "adopt `OP-001`" is not read as "delete `S25`" |
| **`CM-09`** / `AUDIT-018` `R-07` | `AUDIT-019` | Medium | `CH-003` §5's twelve-row boundary table, with three assigned actions |

### 5.2 Treated but not closed — closure requires a decision no document can take

| Finding | Severity | What is treated | What closure needs |
|---|:--:|---|---|
| **`TR-01`** — 800+ employees, statutory curriculum, no owning file | **CRITICAL** | `CH-002` §5.5 delivers the Layer 1 curriculum from `TR-002` §4.2's specification, assigns interim ownership to **HR with HSE**, sets the delivery mode, and costs it at **10–18 trainer-days** plus a perpetual **1,128–2,142 h/year** refresh | **`TR-025` registered** — a Steering decision under `CM-R1`. And now also **`CHA-13`'s Legal confirmation on the current statutory text** |
| `RSK-008` untreated | **Critical** | `CH-001` §9.2 — a dated field pilot: 8–12 senior technicians, 4 weeks, W2 − 8 weeks, with a paper baseline, exit criteria and a fail condition that stops the rollout | The pilot being scheduled and funded |
| `RSK-001` untreated | **Critical** | `CH-005` §9 — eight steps with owners and dates | Three signatures: `CNC-Q-01`, `CNC-Q-02`, `CNC-Q-03` |
| `CM-05` — the register commissions a prohibited leaderboard | High | `CH-004` §7.3 adopts `BRU-PIC-16` and the four permitted patterns as governing rules | **The register row corrected** — `AUDIT-019` `R-04` |
| `CM-06` — a Critical-risk mitigation three waves late | High | `CH-001` §9.2.4 — options A and B with a recommendation | An HR/CFO/PMO decision |
| `TR-02`, `TR-03`, `TR-07`, `TR-09`, `TR-10` | High–Low | `CH-002` §2.3 | Owners outside this category |

### 5.3 The seven findings this report hands to the Steering Committee

None can be resolved by writing:

1. **No Change Lead and no Training Lead exist** (`AUDIT-019` `R-11`) — CEO with HR Director, **W0**.
2. **The champion commitment is ambiguous by 4.5×** (`CHA-10`) — Programme Director, W1 − 10 weeks.
3. **Backfill: A, B or C** (`CNC-Q-02`) — CFO with HR Director, W1 − 10 weeks. The programme is on D.
4. **The statutory text has moved twice** (`CHA-13`) — HSE Lead with Legal, **W0**.
5. **The complaint-committee obligation is unregistered** (`CHA-06`) — HR Director with Legal.
6. **`TR-025` must be registered** (`AUDIT-009` `R-01`) — Steering, `CM-R1`.
7. **The `CM-017` register row commissions a prohibited artefact** (`CM-05`) — Content Lead with CDO.

---

## 6. Operational executability

`PGD-AUDIT-CAT-09` added a seventh audit method — asking whether what a category specifies can
actually be executed today — because a category that specifies an *operation* rather than a *design*
is not tested by conformance alone. Category 13 specifies operations. **Six of the seven rule
classes are inexecutable today, and the reasons are not documentary.**

| Rule class | Executable? | Why not |
|---|:--:|---|
| Change impact assessment at role × site (`OCM-06`) | **✘** | **No Change Lead.** 110–165 person-days unfunded |
| Sponsorship roadmap (`OCM-14`) | **✘** | Sponsors are named by post, not by person; two of the five questions in `CH-001` §5.3 have no company answer |
| Training delivery (`TPD-05`…`TPD-13`) | **✘** | **0 trainers established** against 2.8–3.5 FTE required; no training environment built; `TS-002` unsequenced |
| Statutory Layer 1 delivery (`TPD-09`) | **✘** | No `TR-025`, no confirmed statutory text (`CHA-13`), no HSE facilitator establishment |
| Adoption measurement (`ADP-05`…`ADP-09`) | **✘** | **44 of 95 baselines absent**; `BM-002` ⛔; and `ADP-21` blocks technician telemetry until `LG-020` `AU2` is answered |
| Champion and super-user network (`CNC-07`…`CNC-11`) | **✘** | **Not one person nominated. `D-002` open since 2026-08-12** |
| Wave calendar declaration (`SEP-01`) | **✔ partially** | The declaration stands; the four corrections in `CH-003` §3.4 have not been executed |

> **Read the ✅ narrowly.** Category 13 is complete as a **specification**. **Not one champion has
> been nominated, not one trainer has been hired, not one baseline has been captured, not one
> release letter has been signed, and not one change impact statement exists.** The category's
> central output is a set of numbers that make those absences expensive to ignore — which is what a
> plan can do, and the limit of what it can do.

---

## 7. Remediation applied during this audit

Every change is listed. Nothing was changed silently.

| # | Change | Files | Finding |
|---:|---|---|---|
| 1 | Seven false absence assertions corrected — `RL-001`, `RL-002`, `RL-003`, `RL-004`, `PE-002`, `PE-007`, `SC-003` | `CH-001`, `CH-002`, `CH-003`, `CH-004`, `CH-005`, `_CATEGORY_OVERVIEW` | `CHA-12` |
| 2 | **Eight relative links added** into Categories 05, 10 and 12; link count 29 → **37** | as above | `CHA-12` |
| 3 | Three new open questions raised where the correction opened a real question — `OCM-Q-09`, `TPD-Q-11`, `ADP-Q-08` | `CH-001`, `CH-002`, `CH-004` | `CHA-12` |
| 4 | `CH-001-D-04` rationale rewritten: the decision was taken while `RL-003` was ⛔, and `RL-003`'s subsequent issue **vindicates** it — had §7 claimed the gate there would now be two | `CH-001` | `CHA-12` |
| 5 | `CH-002` §9.1's environment row rewritten: **specified, not built** — the substance is unchanged and the statement is now true | `CH-002` | `CHA-12` |
| 6 | **Twelve figures recomputed** after `CNC-13` was found to invalidate the `TR-023` population: 91–120 → **142–180**; 11,490–20,799 → **12,306–21,759**; 287–520 PW → **308–544 PW**; 356–493 → **380–525** trainer-days; 2.7–3.3 → **2.8–3.5** FTE | `CH-001`, `CH-002`, `CH-005` | `CHA-08` |
| 7 | The false claim in `CH-005` §7.1 — *"`CH-002` §4.4 already counts 91–120 people on the assumption that deputies are included"* — rewritten to state the arithmetic | `CH-005` | `CHA-08` |
| 8 | `CH-005` §9 step 6 corrected from 102–120 to **142–180** (champions + deputies + super-users) | `CH-005` | `CHA-08` |
| 9 | `CH-001` §4.3, §7.2, §8 and §10.5 population rounding corrected from *"750–1,400"* to the counted **752–1,428** | `CH-001` | `CHA-08` |
| 10 | Category overview rewritten: standards line from four undated citations to **16 with editions and verification dates** | `_CATEGORY_OVERVIEW` | `CHA-05` |
| 11 | Category overview line and rule counts regenerated by recount — **3,823 lines, 128 rules** at the time of writing; **3,829** after this report's links were added | `_CATEGORY_OVERVIEW` | `CHA-14` |
| 12 | `PGD-000` §0.5 Category 13 row: **0 ✅ / 4 ◐ / 0 ⬜ / 1 ⛔ → 5 ✅**; five per-document rows rewritten from *"why it is essential"* to *"what it delivered"* | `PGD-000` | `CHA-14` |
| 13 | `PGD-000` §0.5 totals **regenerated by recounting all seventeen category rows**, not by delta | `PGD-000` | `CHA-14`, `PG-M10` |
| 14 | `PGD-000` §3 Register Control: version, authored count, audit list, enumeration timestamp | `PGD-000` | `CHA-14`, `CHA-09` |
| 15 | `README.md` and `FOLDER_STRUCTURE.md` Category 13 rows and counts | `README`, `FOLDER_STRUCTURE` | `CHA-14` |

---

## 8. Recommendations

| # | Recommendation | Owner | By |
|---|---|---|---|
| **R-01** | **Appoint the Change Lead and the Training Lead.** Twelve `CM` files and all five `CH` documents name posts nobody holds. Every date in this category is owned by a vacancy | **CEO with HR Director** | **W0** |
| **R-02** | **Confirm the current statutory training obligations with Legal** against the Labour (Amendment) Ordinance 2025 and Act 2026 — including the §332/§332A complaint-committee duty this estate has never registered | **HSE Lead with Legal Counsel** | **W0** |
| **R-03** | **Decide the champion commitment reading** (`CHA-10`). No release letter can be written until it is decided | Programme Director with Ops Director | **W1 − 10 weeks** |
| **R-04** | **Take the backfill decision — A, B or C.** The programme is on option D and `RSK-001` is Critical and untreated with `D-002` open since 2026-08-12 | **CFO with HR Director** | **W1 − 10 weeks** |
| **R-05** | **Register `TR-025`** (`AUDIT-009` `R-01`, now recommended for the second time) | Programme Content Lead | **Next Steering** |
| **R-06** | **Capture the six W1 baselines**, two of which expire permanently at go-live and one of which is `RSK-008`'s own trigger | PMO with Ops Director | **W1 − 8 weeks; measure 2 by W2 − 12 weeks** |
| **R-07** | **Fund the trainer establishment** — 2.8–3.5 Bengali-capable FTE against 0. `AUDIT-009` `R-07` dated it *"W0 — it precedes everything"* and it is now recommended for the second time | HR Director with CFO | **W0** |
| **R-08** | **Reconcile `CH-001` §7.2 with `RL-003`**, issued in the same window (`OCM-Q-09`), and `CH-002` §9 with `PE-002` (`TPD-Q-11`) | Change Lead with PMO and Platform Engineering | **W1 − 4 weeks** |
| **R-09** | **Own the marketplace seller-technician qualification** (`CHA-15`) — 1,000–4,000 people gated by a Class-`H` rule on an artefact that does not exist | CCO with Marketplace Ops | **W7 − 20 weeks** |
| **R-10** | **Own the data owners** (`CHA-11`) — 381–972 PW committed by `06-01` §4 and in no document | Data Migration Lead with Ops Director | **W1 − 8 weeks** |
| **R-11** | **Execute the `CH-003` §3.4 calendar corrections** — once, register-wide, never file by file | PMO with Enterprise Architecture | **W0** |
| **R-12** | **Correct the `CM-017` register row** to remove or qualify *"leaderboards"* (`AUDIT-019` `R-04`) | Programme Content Lead with CDO | **W2** |
| **R-13** | **Write `RR-002` (Identifier Convention Standard) and ratify `RG-08` (timestamped enumeration).** This is the **ninth** recommendation of `RR-002` and the **eighth** of `RG-08`. `CHA-02`, `CHA-09` and `CHA-12` are all instances that neither would have prevented, but both would have made cheap to detect | Enterprise Architecture | **Now** |

---

## 9. Closure

Category 13 is **complete on disk at 5 of 5**, template-conformant on all eleven sections, with
**128 governing rules across five prefixes that collide with nothing in a 772-file estate**, **257
distinct identifiers all resolving**, **37 relative links all resolving**, and **42 open questions
each with a named owner and a date**.

**Three things belong in front of the Steering Committee rather than the change function.**

**First, the category's central number.** `06-01` §4 calls the business-side commitment *"the
binding constraint on the programme"*. Counted for the first time, it is **1,190–1,622 person-weeks
of champion and super-user time**, plus **381–972 person-weeks of data-owner time** — against 298 PW
for all twelve portals and 352 PW for all 140 guiding documents. **`GV-007` §8.1 lists ten squads
and none of them is this.** It is not understated in the resource plan; it is absent from it, and
so is the **308–544 person-weeks of learner time** and the **380–525 trainer-days** that go with it.

**Second, the estate moved under the auditor mid-audit, for at least the ninth recorded time.**
Twenty files appeared in forty-eight minutes. Seven statements in these documents were true when
written and false when read, and **the control this category wrote against that exact failure is
what caught them** — a timestamped enumeration makes staleness visible at the moment someone relies
on it, and does nothing else. That is the honest limit of a documentary control, and `RG-08` and
`RR-002` remain unratified after eight and nine recommendations.

**Third, the ✅ is a specification, not a capability.** Section 6 finds six of seven rule classes
inexecutable today. Not one champion has been nominated, not one trainer hired, not one baseline
captured, not one release letter signed, not one change impact statement written. The programme now
knows precisely what its people-side costs and precisely who has to sign for it — which is the
whole of what this category could deliver, and none of what it needs next.

| Rule | Status |
|---|---|
| `PG-01` register-first | ✅ All five rows were in `PGD-000` before authoring |
| `PG-03` / `RG-06` count, do not consult | ✅ Every figure counted at a stated timestamp with a stated command |
| `PG-06` cite standards | ✅ 16 standards, all with edition and verification date |
| `PG-M4` verify citations | ✅ `verified_on: 2026-08-19` in all five; four inherited undated citations corrected |
| `PG-M10` regenerate, do not adjust | ✅ Totals recomputed from inputs at `CHA-08`; `PGD-000` §0.5 recounted across seventeen rows |
| `DL-06` no bare `D-nn` | ✅ 31 local decisions, all `CH-00n-D-nn` |
| `CP-01` author once | ✅ No `TR` or `CM` content restated; four out-of-scope tables state the boundaries |
| Proposed `RG-08` timestamped enumeration | ✅ **Held — and `CHA-12` is the evidence that holding it is not sufficient** |

> **Audit identifier note.** This report is filed as **`PGD-AUDIT-CAT-13`**, following
> `PGD-AUDIT-CAT-07`, `-CAT-08` and `-CAT-09`. The numeric space moved during this audit window —
> `PGD-AUDIT-009` was claimed by Category 10 at **02:06**, four minutes before this enumeration —
> which is the **ninth identifier event** in this repository and the reason the category-keyed form
> is used: it is the only form computable without reference to another session's work. A
> `PGD-AUDIT-\d{3}` sweep now misses **four of thirteen** reports.

---

*1000FiX Services Limited · ERP Programme · Enterprise Architecture · CONFIDENTIAL — Internal Use Only*
*Enumerated 2026-08-19 02:10 (+06) · Next audit: the next category on completion*
