---
id: UX-008
title: Usability Test Plan & Findings Log
category: 06 — Experience & Interface Design
code: UX
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Head of Product Design
approver: Design Authority (constituted under GV-002)
standards_basis: >
  ISO 9241-11:2018 (usability — effectiveness, efficiency, satisfaction in a context of use) ·
  ISO 9241-210:2019 §5.7 (evaluate designs against requirements) ·
  ISO 25062:2025 (CIF for reporting usability evaluations; cancels and replaces ISO/IEC 25062:2006) ·
  ISO/IEC 25066:2016 (CIF — evaluation report content items) · ISO/IEC 25010:2023 interaction capability
traces_to: >
  PGD-000 UX-008 · NFR-075 (≤ 4 h to competence), NFR-076 (≤ 3 min intake) ·
  04-00 KPI sets P01…P12 · URD §2 (the user-experience vision), §25 (user acceptance criteria) ·
  UX-004 IXN-86 (the prototype evaluation gate) · UX-005 §10 (assisted-user testing) ·
  GV-009 (wave gate evidence classes) · BM-001 (KPI and benefits)
depends_on: UX-003 (task selection from the Class B register) · UX-004 (the eight prototypes) · UX-005 (assisted-user protocol) · UX-006 (field conditions)
verified_on: 2026-08-18
priority: P2
needed_by: W2
enumeration_timestamp: 2026-08-18 14:45 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# UX-008 — Usability Test Plan & Findings Log

### Category 06 · Code `UX` · ISO 9241-11:2018 · ISO 9241-210:2019 · ISO 25062:2025

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `UX-008` exists in `PGD-000` Category 06.
> 2. **`PG-03` Count, do not consult.** Counted at **2026-08-18 14:45 (+06)**: **9 of 621 files**
>    mention "usability test"; **0** mention "prototype".
> 3. **`PG-06` Cite standards.** §2.1.
> 4. **`PG-M4` Verify citations.** ISO 25062's 2025 revision status verified 2026-08-18; §17.

---

## 1. Purpose

The `URD` opens Part C with an executive summary titled **"The User Experience Vision"** and closes
with user acceptance criteria. Between the vision and the acceptance there is **no instrument**: no
plan for putting the product in front of a real technician, a real rider, a real branch agent or a
real customer and finding out whether they can do their job with it.

The programme serves **500+ employees, 200–400 technicians, 250,000+ customers per month and
2,000+ external sellers and partners**. That is a large population to be wrong about, and the design
decisions in `UX-001`…`UX-007` are, however carefully reasoned, **hypotheses until someone tests
them.**

This document is the test instrument. It defines what is measured, on whom, with what tasks,
against what criteria, how often, and what happens to a finding once it exists.

It unblocks the `UX-004` `IXN-86` prototype evaluation gate, the `UX-005` assisted-user obligation
that `TS-016` cannot discharge alone, and the `GV-009` wave-gate readiness dimension that currently
has no user-facing evidence class.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The measurement model — effectiveness, efficiency and satisfaction, per context of use |
| 2 | Evaluation types and when each is used |
| 3 | The participant model: personas, roles, sample sizes, recruitment, consent |
| 4 | The task set, derived from the 15 critical journeys and the 130 bespoke screens |
| 5 | Success criteria, tied to the KPIs and NFRs that already exist |
| 6 | Cadence — per prototype, per release, per wave gate |
| 7 | **Field-condition testing** — the protocol for sunlight, gloves, one hand, weak signal |
| 8 | The findings log: schema, severity, ownership, remediation loop |
| 9 | Reporting to ISO 25062:2025 |
| 10 | Ethics and personal-data handling under PDPA 2026 |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| Functional acceptance testing | `TS-006`…`TS-011` UAT packs, `QA-*` | UAT asks *does it work*; this asks *can they use it* |
| Accessibility conformance testing | `TS-016`, `UX-005` | Conformance is a standard; usability is an outcome. §5.5 states the join |
| Performance measurement | `QA-*`, `NFR-001`…`041` | Server metrics; §6.3 uses the **perceived** thresholds |
| Training effectiveness | `CH-*`, `TR-*` | `NFR-075` is measured here **and** there; §6.4 states which |
| Benefits realisation | `BM-001` | This document feeds it |
| Content effectiveness measurement | `CG-014` | Peer instrument; §6.5 states the overlap |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| Designers | The evaluation their work must pass, and the criteria |
| Product and business owners | What their KPI targets are being measured against |
| `GV-009` gate assessors | The user-readiness evidence class |
| Change and training (`CH-*`) | Findings that indicate a training need rather than a design defect |
| `BM-001` owner | Baseline data for benefit claims |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Status at verification | How this document conforms | Departure |
|---|---|---|---|
| **ISO 9241-11:2018** | Current | Usability is defined as **effectiveness, efficiency and satisfaction in a specified context of use** — an outcome of interaction, not a property of the product. §3 is the measurement model; the contexts are `UX-006` §3 and §4.2 here | None |
| **ISO 9241-210:2019** | Current | §5.7 requires evaluation against user requirements throughout the lifecycle, not once. §7 cadence | None |
| **ISO 25062:2025** — CIF for reporting usability evaluations | **Current. Released 4 February 2025; cancels and replaces ISO/IEC 25062:2006**, with scope expanded beyond summative test reports to evaluation reports generally | §10 report structure | None |
| **ISO/IEC 25066:2016** — CIF, evaluation report content items | Current | Its content-item classification (required / recommended / optional) drives §10.2 | Where 25066 and 25062:2025 overlap, **25062:2025 governs** as the later and broader instrument. Recorded as `UX-008-D-05` |
| ISO/IEC 25010:2023 | Current | Interaction capability and **inclusivity** are the quality characteristics evaluated | None |
| `GV-009` | Programme | Evidence classes and named assessors | This document supplies the user-readiness dimension |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `URD` §2 | The user-experience vision this instrument tests |
| `URD` §3, §4 | **36 personas, 46 roles** — the participant frame |
| `URD` §18 | **15 critical journeys** — the task frame |
| `URD` §25 | User acceptance criteria |
| `04-00` §P01…§P12 | Per-portal KPI sets — **the targets, several with the baseline stated as "unmeasured"** |
| `05-06` `NFR-075`, `NFR-076` | ≤ 4 h to competence; ≤ 3 min walk-in intake |
| `UX-003` §5.4 | The 130 bespoke screens — the task-selection pool |
| `UX-004` §10 | The eight prototypes and the evaluation gate |
| `UX-006` §3 | The context-of-use specification ISO 9241-11 requires |
| `TS-002` | Test data pack and persona set, including the `B-01`…`B-11` Bengali stress set |
| `CG-014` | Content effectiveness measurement — the peer instrument |

### 2.3 Findings this document addresses

| Finding | Source | How addressed |
|---|---|---|
| Register row `UX-008` ⬜ | `PGD-000` | Authored |
| `UXA-09` | `UX-004` §10.1 | The evaluation gate that makes prototypes worth building |
| `UX-005` §10 | `UX-005` | Assisted-user testing is specified here as a protocol, with participants |
| **New — `UXA-18`** | This category | **Counted: 9 of 621 files mention "usability test"; none specifies a participant, a task, a criterion or a cadence.** The programme has the word and not the practice |
| **New — `UXA-19`** | This category | **Several `04-00` KPI baselines are stated as "unmeasured"** — booking funnel conversion, self-service status checks, portal MAU, app store rating. A target with no baseline cannot demonstrate improvement, and `BM-001` and `GV-008` payback both rest on these. §6.6 |

---

# 3. The Measurement Model

## 3.1 ISO 9241-11 applied

> **Usability is an outcome of interaction, not a property of the product.** The same screen is
> usable for a branch agent at a desk and unusable for the same person on a phone in the rain.
> Every measure below is therefore reported **with its context**.

| Dimension | Measure | Instrument |
|---|---|---|
| **Effectiveness** | Task completion rate · error rate · assists required · data accuracy of the result | Observation |
| **Efficiency** | Time on task · steps taken versus optimal · rework rate | Timing + interaction log |
| **Satisfaction** | Post-task ease rating (SEQ) · post-session usability score · qualitative comment | Instrument §3.3 |

## 3.2 The four counted quantities per task

| # | Quantity | Definition |
|---|---|---|
| `UTP-01` | **Completion** | Participant reached the correct end state **unaided**. Aided completion is recorded separately and never counted as completion |
| `UTP-02` | **Time on task** | First deliberate action to correct end state, excluding facilitator interruption |
| `UTP-03` | **Errors** | Any action that moves away from the end state, classified as slip, mistake or system-induced |
| `UTP-04` | **Assists** | Any facilitator intervention. **An assist is a design defect until proven a training gap** |

| # | Rule |
|---|---|
| `UTP-05` | A participant who fails is **never described as having failed**. The design failed the participant. This is a reporting rule, not a courtesy — the alternative biases the analysis toward training remedies |
| `UTP-06` | Aided completion is reported as a distinct outcome. Merging it with completion inflates every result and is the most common misreport in usability practice |

## 3.3 Satisfaction instruments

| Instrument | When | Note |
|---|---|---|
| **Single Ease Question** (7-point), post-task | Every task | Short enough to answer honestly on a phone, in the field |
| Post-session usability score (10-item, 5-point) | Every summative session | **Administered in Bengali** for Bengali-speaking participants; the translation is validated once by Localisation and then held fixed |
| Open comment | Every session | The source of most actionable findings |

| # | Rule |
|---|---|
| `UTP-07` | Satisfaction instruments are administered in the **participant's language**, and the Bengali translation is fixed after validation. Changing the wording between waves destroys comparability |
| `UTP-08` | A satisfaction score is **never reported without its completion and time data**. A satisfied participant who could not finish is a specific and important finding, and a score alone hides it |

---

# 4. Participants

## 4.1 The frame

| Population | Size | Represented by |
|---|---:|---|
| Field & workshop technicians | 200–400 | `P-03` Kabir, `A-02` |
| Riders & logistics | 50–200 | `P-10` Jasim, `A-03` |
| Branch and back-office staff | 150–250 | `P-08` service agent, dispatcher, branch manager |
| Contact centre agents | 30–80 | agent, team leader |
| Field auditors | 20–60 | quality auditor |
| **Individual customers** | **250,000+/month** | `P-34c` Abdul (`A-01`), plus digitally confident segments |
| Corporate client staff | 500–2,000 | corporate admin, site manager |
| Marketplace sellers | 500–2,000 | freelance engineer, shop |
| Vendors, brand partners, referral partners | 350–2,650 | vendor clerk, claims officer |
| **Accessibility personas** | — | `A-01`…`A-07` (`URD` §3) |

## 4.2 Sample sizes

| Evaluation type | Participants per segment | Rationale |
|---|---:|---|
| **Formative** (prototype, iterative) | **5–7** | Detects the large majority of severe issues per round; more participants per round buys less than more rounds |
| **Summative** (pre-release benchmark) | **12–20** | Needed for a defensible completion-rate and time estimate |
| **Field-condition** | **6–10** | Logistically bounded; variance comes from conditions, not participants |
| **Assisted-user** | **3–5 per assistive technology** | Small but non-negotiable; `UX-005` §10 |
| **Bengali linguistic** | **5** | Combined with formative sessions |

| # | Rule |
|---|---|
| `UTP-09` | **Formative testing is iterative.** Three rounds of 5 find far more than one round of 15, because rounds 2 and 3 test the fix |
| `UTP-10` | Sample sizes are per **segment**, not per session. A technician round and a customer round are separate |
| `UTP-11` | Summative results are reported with confidence intervals. A completion rate of "80%" from 15 participants has an interval wide enough to matter, and reporting the point estimate alone overstates it |

## 4.3 Recruitment

| # | Rule |
|---|---|
| `UTP-12` | **Participants are real users, never programme staff.** A technician who has attended a requirements workshop is not a naïve participant | `IXN-87` |
| `UTP-13` | Internal participants are drawn from **branches not involved in the programme**, rotated so no branch is over-sampled |
| `UTP-14` | Customer participants are recruited to reflect the actual base: **Bengali-first, mixed digital literacy, mid- and low-end Android devices**. A panel of digitally confident Dhaka smartphone users is not the customer base |
| `UTP-15` | `A-01` (age 62, low tech literacy, Bengali only, presbyopia) and `A-04` (low literacy, both hands full) are **quota-protected**: at least one of each in every customer round |
| `UTP-16` | Participants are compensated for their time. Unpaid participation biases the panel toward the enthusiastic |
| `UTP-17` | Recruitment has a **named owner**. `UX-004` `Q-02` records that nobody currently owns it, and that is the single largest execution risk in this plan |

## 4.4 Ethics and personal data

| # | Rule | Basis |
|---|---|---|
| `UTP-18` | Informed consent in the participant's language, covering recording, retention and use, and separable — a participant may decline recording and still take part | PDPA 2026, `LG-008` |
| `UTP-19` | Recordings are personal data: encrypted, access-controlled, **retained no longer than the remediation cycle needs**, and deleted on schedule | `LG-009` |
| `UTP-20` | **No production customer data** is used in a session; `TS-002` supplies the test data pack | `NFR-071` |
| `UTP-21` | Withdrawal is possible at any point without consequence, and the participant's data is destroyed |
| `UTP-22` | Employee participants are protected: **results are never attributable to an individual** in any report, and never reach a line manager. Otherwise employees optimise for looking competent, which is the opposite of what a session needs | `UTP-05` |

---

# 5. Evaluation Types

## 5.1 Formative — during design

| Attribute | Value |
|---|---|
| Purpose | Find and fix problems while changing them is cheap |
| Subject | The eight `UX-004` prototypes; F2 wireframes for high-consequence screens |
| Method | Moderated, think-aloud, task-based |
| Output | Findings log entries; a design iteration |
| Gate | **`IXN-86` — a prototype's screens do not enter build until it has been evaluated** |

## 5.2 Summative — before release

| Attribute | Value |
|---|---|
| Purpose | Establish whether the built product meets its criteria |
| Subject | The release candidate for a surface |
| Method | Moderated or unmoderated, benchmark tasks, full instrument set |
| Output | An ISO 25062:2025 evaluation report (§10) |
| Gate | `GV-009` wave gate — user-readiness evidence |

## 5.3 Field-condition — the one that cannot be simulated

| Attribute | Value |
|---|---|
| Purpose | Determine whether the design works where the work happens |
| Subject | `P02`, `P09`, `P11`, and `P01` on a low-end device |
| Method | Shadowing a real shift, with structured observation |
| Conditions | **Direct sunlight · gloves · one hand · helmet · rain where it occurs · genuine connectivity loss** |
| Output | Findings log entries, condition-tagged |
| Gate | **Before every mobile release** (`URD` §21.5, `FV-08`) |

| # | Rule |
|---|---|
| `UTP-23` | Field sessions run on the **reference device** — mid-range Android 11, 3 GB RAM (`IXN-83`) |
| `UTP-24` | The network is **genuinely lost**, not simulated: a real basement, a real rural site, a real four-hour disconnection (`IXN-84`) |
| `UTP-25` | The facilitator does not carry the device. The participant does, in their own working posture |
| `UTP-26` | A field session that produces no findings is **evidence the protocol failed**, not that the design succeeded. Real shifts always produce findings |

## 5.4 Assisted-user — with assistive technology

| Attribute | Value |
|---|---|
| Purpose | Determine whether an assisted user can complete the task at all |
| Subject | Every customer-facing surface and `P03` |
| Method | Participant's own assistive technology, own configuration |
| Technologies | **TalkBack (Bengali and English)** · VoiceOver · screen magnification to 200% · keyboard-only · switch access where available |
| Output | Findings log; input to the ACR (`UX-005` §11) |
| Gate | Per wave gate (`ACD-26`) |

| # | Rule |
|---|---|
| `UTP-27` | Participants use **their own** assistive technology at their own settings. A facilitator's laptop with a screen reader they do not use daily measures nothing |
| `UTP-28` | **Bengali assistive-technology sessions are mandatory, not a variant** — `CG-011` §8.3's bilingual trap: a screen that passes in English is not tested |

## 5.5 The join with `TS-016`

| `TS-016` (conformance) | `UX-008` (usability) |
|---|---|
| Asks *does this meet the criterion* | Asks *can this person complete the task* |
| Produces a pass/fail per success criterion | Produces a completion rate and a findings log |
| Executed by the accessibility reviewer | Facilitated by a designer or researcher |
| Feeds the ACR's per-criterion table | Feeds the ACR's evaluation-evidence section |

| # | Rule |
|---|---|
| `UTP-29` | **Both are required.** A surface can pass all 55 criteria and still be unusable, and `TS-016` §1.1's last row — *"whether the task can actually be completed by an assisted user, start to finish"* — is this document's, not `TS-016`'s |
| `UTP-30` | Sessions may be **combined** to reduce participant burden, with the outputs recorded separately |

## 5.6 Benchmark — establishing the baselines that do not exist

See §6.6. Run **once per surface before its first release**, to create the baseline `04-00` records
as "unmeasured".

---

# 6. Tasks and Criteria

## 6.1 Task selection

| # | Rule |
|---|---|
| `UTP-31` | Tasks are drawn from the **15 critical journeys** (`URD` §18) and the **130 bespoke screens** (`UX-003` §5.4). A task that exercises only Class G screens tests the Odoo conventions, not the design |
| `UTP-32` | A task is phrased as a **goal in the participant's own language**, never as an instruction: *"A customer has brought in a laptop that will not charge. Book it in."* — not *"click Service Intake, then New"* |
| `UTP-33` | Tasks are ordered by frequency, and the highest-frequency task is tested first while attention is highest |
| `UTP-34` | Each session runs **5–8 tasks maximum**. Longer sessions produce fatigue data |

## 6.2 The core task set

| # | Task | Surface | Journey | Criterion source |
|---:|---|---|:--:|---|
| `T-01` | Book a service for your own device | `P01` | 1 | Booking funnel conversion **> 72%** |
| `T-02` | Track a service without signing in | `track` | 1 | Self-service status checks **> 80%** of enquiries |
| `T-03` | Review and part-approve an estimate | `P01` | 1, 2 | — |
| `T-04` | Pay an invoice by bKash | `P01` | 1 | — |
| `T-05` | **Complete a walk-in intake** | `P03` intake | 2 | **`NFR-076` ≤ 3 minutes** |
| `T-06` | **Dispatch a morning queue of 20 jobs** | `P03` dispatch | 1 | **< 10 minutes** for a full queue |
| `T-07` | **Execute a job end to end, offline** | `P02` | 1 | **Job documentation < 5 minutes** |
| `T-08` | Consume a van part by scan, and handle a rejection | `P02` | 1 | — |
| `T-09` | **Resolve a sync conflict disclosure** | `P02` | — | Comprehension: participant states correctly what happened to their work |
| `T-10` | Collect a consignment with seal, OTP and signature | `P09` | 3 | **POD completeness 100%**, zero custody breaks |
| `T-11` | Handle a customer contact with a screen pop | `P10` | 14 | **Agent screen switches < 3** |
| `T-12` | Submit a bulk service request by CSV | `P04` | — | **< 5 minutes** |
| `T-13` | Decide a warranty claim from the evidence pack | `P08` | 4 | — |
| `T-14` | Register as a marketplace seller | `P07` | 7 | **Onboarding completion > 60%** |
| `T-15` | Complete an audit checklist offline | `P11` | — | — |

## 6.3 Success criteria

**Criteria are taken from targets that already exist.** Inventing a usability target beside an
existing KPI produces two numbers for one thing, which is the defect class `RQA-12` and `AP-02`
record elsewhere in this estate.

| Class | Criterion | Source |
|---|---|---|
| **Completion** | ≥ 90% unaided for `T-05`, `T-06`, `T-07`, `T-09`, `T-10` — the operational tasks | Set here; these are trained daily tasks |
| | ≥ 80% unaided for customer tasks `T-01`…`T-04` | Below this, the > 72% conversion target is not reachable |
| **Time** | `T-05` ≤ 3 min · `T-06` < 10 min · `T-07` < 5 min documentation · `T-12` < 5 min | `NFR-076`, `04-00` §P03, §P02, §P04 |
| **Comprehension** | `T-09`: the participant states correctly, unprompted, what happened to their work | `AR-010` §6, `MOB-75` |
| **Errors** | Zero errors with a money, custody or consent consequence | `IXN-08` |
| **Assists** | Zero assists on any task a user performs daily | `UTP-04` |
| **Satisfaction** | Post-task ease ≥ 5.5 / 7 on operational tasks | Set here |
| **Learnability** | A new service agent reaches `T-05` criterion within **4 hours of training** | **`NFR-075`** |

| # | Rule |
|---|---|
| `UTP-35` | A criterion missed in **formative** testing triggers iteration. A criterion missed in **summative** testing is a `GV-009` gate finding, and the gate assessor — not the design team — decides whether it blocks |
| `UTP-36` | `NFR-075` is measured **here** for the design's contribution and in `CH-*` for the training's. A single number cannot separate them; the two instruments together can |

## 6.4 What a failure means

| Signal | Likely cause | Owner |
|---|---|---|
| Fails for everyone, first attempt | **Design** | `UX-003`/`UX-004` |
| Fails for everyone, improves fast with repetition | **Learnability** — acceptable for daily tasks, not for occasional ones | Design + Training |
| Fails only for `A-01`, `A-04` | **Inclusivity** — an accessibility or literacy defect | `UX-005` |
| Fails only in Bengali | **Layout or terminology** | `UX-007` / `BN-003` |
| Fails only in the field | **Context** | `UX-006` |
| Fails only for new users | **Onboarding** | Design + `HC-016` |
| Succeeds but with high effort | **Efficiency** — often invisible in completion data | Design |

| # | Rule |
|---|---|
| `UTP-37` | **The default attribution is design.** Attributing a failure to training requires evidence that the design is sound — usually a later round showing the same participants succeeding after instruction with no design change |

## 6.5 Overlap with `CG-014`

`CG-014` measures content effectiveness. Where a task fails because of wording, the finding belongs
to `CG-014`; where it fails because of layout or flow, to this document.

| # | Rule |
|---|---|
| `UTP-38` | A finding is filed **once**, in the log of the document that owns the remedy, and cross-referenced. Dual-filing produces two owners and no fix |

## 6.6 `UXA-19` — the missing baselines

`04-00` states several KPI baselines as **"unmeasured"**:

| KPI | Baseline in `04-00` | Target |
|---|---|---|
| Booking funnel conversion (`P01`) | **unmeasured** | > 72% |
| Self-service status checks vs hotline | **~0** | > 80% of status enquiries |
| Portal monthly active users | **—** | > 120,000 |
| App store rating | **—** | > 4.5 |
| Average handling time (`P10`) | **"vs baseline once established"** | −25% |

> **A target with no baseline cannot demonstrate improvement.** `BM-001` claims benefit against
> several of these, and `GV-008` finds the benefit side already overstated 2.2×–3.3×
> (`PGD-A2-10`). **Measuring the baseline is cheap now and impossible after go-live**, because the
> pre-system behaviour will no longer exist to measure.

| # | Rule |
|---|---|
| `UTP-39` | A **benchmark evaluation (§5.6) runs before each surface's first release** and records the baseline for every KPI marked unmeasured |
| `UTP-40` | Where a baseline can only be measured on the legacy process — hotline call volume, manual booking rate, current intake time — it is measured **in the field, before cutover**, and the measurement is a `MG-*` / `BM-001` obligation this document flags rather than owns |
| `UTP-41` | A KPI that reaches go-live with no baseline is reported to `GV-005` as a benefits risk, not quietly carried |

---

# 7. Cadence

| When | Evaluation | Participants | Gate |
|---|---|---|---|
| Each prototype, before its screens enter build | Formative, 2–3 rounds of 5–7 | Segment-specific | **`IXN-86`** |
| Each Class B screen set, mid-build | Formative, 1 round of 5 | Segment-specific | Design review |
| Before each surface's first release | **Benchmark + summative**, 12–20 | Segment-specific | `GV-009` |
| Before each mobile release | **Field-condition**, 6–10 | Technicians / riders / auditors | **`FV-08`** |
| Each wave gate | **Assisted-user**, 3–5 per technology | `A-01`…`A-07` | `GV-009`, `ACD-26` |
| Quarterly after go-live | Continuous — analytics + 5 sessions | Rotating | `BM-001` |

| # | Rule |
|---|---|
| `UTP-42` | **Evaluation is scheduled in the plan, with named participants and dates, or it does not happen.** `GV-004` finds Wave 1 at 5.33× capacity; unscheduled work in an over-committed wave is not deferred, it is dropped |
| `UTP-43` | Sessions have a **lead time**: recruiting five real technicians from non-programme branches takes 2–3 weeks. Booking evaluation the week it is needed guarantees the panel is whoever is available, which is the panel that biases the result |

---

# 8. The Findings Log

## 8.1 Schema

```yaml
id: UF-0042
date: 2026-11-14
evaluation: PR-4 formative round 2
surface: P02
screen: SCN-P02-021          # UX-003 §7
task: T-07
participant: P-14            # pseudonymous; never a name (UTP-22)
segment: field technician
language: bn
condition: direct sunlight, gloves, one hand
observation: >
  Participant attempted to confirm part consumption three times. Each tap registered on the
  adjacent row. Participant removed their glove to continue.
interpretation: >
  Row targets are 44 px with 4 px separation. UX-006 MOB-03 requires 56 px on P02 and MOB-04
  requires >= 12 px separation. The screen was designed before UX-006 was issued.
severity: 2                   # §8.2
frequency: 5 of 6 participants
criterion_affected: [T-07 time, zero assists]
wcag: ["2.5.8"]
owner: Design — field applications
remedy: Apply size.target.field and MOB-04 separation to all P02 list rows
status: open
verified_in: —                # the round or release that confirms the fix
```

| # | Rule |
|---|---|
| `UTP-44` | **Observation and interpretation are separate fields.** Merging them buries the evidence and makes a wrong interpretation unfalsifiable |
| `UTP-45` | Frequency is recorded as *n* of *N*. "Some participants" is not a finding |
| `UTP-46` | A finding names the **criterion it affects**, or it is an opinion |
| `UTP-47` | Participants are **pseudonymous** (`UTP-22`) |

## 8.2 Severity

| Level | Definition | Response |
|:--:|---|---|
| **1 — Critical** | Prevents task completion, or causes an error with a money, custody, consent or safety consequence | **Blocks release.** Fixed and re-tested before the surface ships |
| **2 — Major** | Completion possible but with significant effort, error or assistance; or fails a stated criterion | Fixed before the surface's wave gate |
| **3 — Moderate** | Noticeable friction; task completes | Scheduled; fixed within the wave |
| **4 — Minor** | Cosmetic or preference | Backlog |

| # | Rule |
|---|---|
| `UTP-48` | Severity is assigned by the **facilitator**, not by the team that owns the remedy. Self-assessed severity drifts downward |
| `UTP-49` | A severity 1 finding **cannot be closed by a decision to accept it**. It is fixed, or the release is deferred, or the Design Authority records a formal deviation with a named accepting owner |
| `UTP-50` | Severity is raised by **frequency**: an issue affecting 5 of 6 participants is at least severity 2 regardless of its individual impact |

## 8.3 Remediation

| Step | Owner | Rule |
|:--:|---|---|
| 1 | Facilitator | Finding logged within **2 working days** of the session, while the recording is fresh |
| 2 | Design owner | Remedy proposed within 5 working days for severity 1–2 |
| 3 | Design owner | Remedy applied to the artefact (`UX-001`, `UX-003`, `UX-004`, `UX-006`) |
| 4 | Facilitator | **Verified in a later round or release** — `verified_in` populated |
| 5 | — | Closed |

| # | Rule |
|---|---|
| `UTP-51` | **A finding is closed only when the fix has been observed to work with users**, not when the code merges. This is the step that is always cut and always costs more than it saved |
| `UTP-52` | A remedy that changes a **component or a token** is applied at `UX-001`, not at the screen — otherwise the same defect recurs on every surface |
| `UTP-53` | Open severity 1 and 2 findings are reported at every `GV-009` gate and are visible in `GV-005` where they carry a delivery consequence |

## 8.4 The log itself

| # | Rule |
|---|---|
| `UTP-54` | Identifiers are **`UF-nnnn`**, allocated sequentially, never reused. An identifier sweep returns **zero** matches for `UF-` across the whole workspace, re-verified at **2026-08-18 21:40 (+06)** over 731 files |
| `UTP-55` | The log is a single register for the whole programme, not one per surface. Cross-surface patterns — the same component failing on four surfaces — are only visible in one log |
| `UTP-56` | The log is reviewed monthly by Design, Content Design and the accessibility reviewer together. Most severity 1 findings touch all three |

---

# 9. Facilitation

| # | Rule |
|---|---|
| `UTP-57` | The facilitator **does not design the thing being tested** where a neutral facilitator is available. Where one is not, the conflict is recorded in the report (`GV-010` independence classes) |
| `UTP-58` | Sessions with Bengali-speaking participants are facilitated **in Bengali**, by a Bengali speaker. A translated session measures the translation |
| `UTP-59` | The facilitator does not explain, defend, or lead. The strongest instinct in a session is to help; it destroys the data |
| `UTP-60` | Think-aloud is prompted once and not enforced. A technician working with one hand in sunlight cannot narrate |
| `UTP-61` | Two observers maximum, and none of them the participant's manager (`UTP-22`) |

---

# 10. Reporting

## 10.1 Per session

A short record within 2 working days: tasks, participants, completion, time, findings logged. **Not
a formal report** — speed matters more than form at this stage.

## 10.2 Per evaluation — ISO 25062:2025

Summative and benchmark evaluations produce a full report to the CIF, using ISO/IEC 25066's
required / recommended / optional content-item classification.

| Section | Content |
|---|---|
| 1 | Product and version evaluated |
| 2 | **Evaluation approach** — formative / summative / benchmark / field / assisted |
| 3 | **Context of use** — users, tasks, equipment, environment (`UX-006` §3) |
| 4 | Participants: how recruited, how many, characteristics, **and how they differ from the target population** |
| 5 | Tasks, with the exact wording used |
| 6 | Method: setting, equipment, facilitation, instruments |
| 7 | **Results**: completion, time, errors, assists, satisfaction — with confidence intervals |
| 8 | Findings, with severity and frequency |
| 9 | **Limitations** — what this evaluation could not determine |
| 10 | Evaluator identity and **independence class** (`GV-010`) |

| # | Rule |
|---|---|
| `UTP-62` | Section 9 is mandatory. **An evaluation report with no stated limitations is not credible** — and `GV-010` records the programme at 29 of 29 audit reports at independence class I0, so limitations are the honest counterweight |
| `UTP-63` | Section 4 states how the panel differs from the real population. A panel of Dhaka smartphone users tested against a national customer base is a limitation, not a detail |
| `UTP-64` | Reports are written for the people who must act on them, not to demonstrate rigour |

## 10.3 To the gates

| Consumer | What it gets |
|---|---|
| `GV-009` wave gate | User-readiness evidence: completion rates against criteria, open severity 1–2 findings |
| `GV-005` RAID | Severity 1 findings with a delivery consequence |
| `BM-001` | Baselines (§6.6) and post-go-live measurement |
| `CO-003` | Acceptance evidence where a contract references usability |
| `UX-005` ACR | Assisted-user session records |

---

# 11. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `UX-008-D-01` | Success criteria | (a) invent usability targets; (b) **use existing KPIs and NFRs** | **(b)** | Two numbers for one thing is the defect class `RQA-12` and `AP-02` record | Some tasks have no numeric criterion; a qualitative one is stated instead |
| `UX-008-D-02` | Formative sample size | (a) one round of 15; (b) **three rounds of 5–7** | **(b)** | Rounds 2 and 3 test the fix; a single large round tests the same untested design fifteen times | More scheduling overhead, more lead time (`UTP-43`) |
| `UX-008-D-03` | Field testing | (a) laboratory simulation; (b) **real shifts, real conditions, real network loss** | **(b)** | Sunlight, gloves, helmets and basements cannot be simulated usefully | Logistically expensive; `UTP-26` guards against a token exercise |
| `UX-008-D-04` | Failure attribution | (a) case by case; (b) **design by default, training on evidence** | **(b)** | The opposite default is the standard way a design defect becomes a permanent training cost | `UTP-37` requires evidence to reattribute |
| `UX-008-D-05` | CIF standard | (a) ISO/IEC 25066:2016 alone; (b) **ISO 25062:2025 governing, with 25066's content-item classification** | **(b)** | 25062:2025 cancels and replaces the 2006 edition with a scope broadened beyond test reports; 25066's required/recommended/optional classification remains the practical checklist | §10.2 uses both, with precedence stated |
| `UX-008-D-06` | Participant anonymity | (a) attributable internally; (b) **pseudonymous, never reaching a line manager** | **(b)** | Attributable results make employees optimise for looking competent | Some diagnostic detail is lost; the honesty is worth more |

---

# 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Who owns participant recruitment?** `UX-004` `Q-02` raises the same gap. Without an owner, every session in §7 is unscheduled | HR + Change Lead | **W1 — blocking** | All evaluation |
| `Q-02` | Is there a budget line for participant compensation (`UTP-16`)? `GV-008` does not carry one | Programme Manager | **W1** | `UTP-16` |
| `Q-03` | Who facilitates? Neutral facilitation (`UTP-57`) requires someone who is not the designer, and the team is 2–3 designers (`GV-007` §7) | Head of Product Design | **W1** | `UTP-57`, independence class |
| `Q-04` | Who measures the pre-cutover baselines (`UTP-40`) — hotline volume, manual booking rate, current intake time? They cease to exist after go-live | `BM-001` owner + `MG-*` | **W1 — irreversible if missed** | `UXA-19`, `BM-001` |
| `Q-05` | Is the post-session usability instrument's Bengali translation validated, and by whom? | Localisation Lead | W2 | `UTP-07` |
| `Q-06` | Where does the findings log live so that Design, Content and QA can all write to it? | Head of Product Design | W1 | `UTP-55` |
| `Q-07` | Does `CO-003` reference usability acceptance? If a vendor contract does, its criteria govern | Commercial | W2 | §10.3 |

---

# 13. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Usability is defined per ISO 9241-11 with all three dimensions measured in a stated context | §3 |
| `AC-02` | A participant model exists with sample sizes, recruitment rules and quota-protected accessibility personas | §4 |
| `AC-03` | Tasks are derived from the 15 journeys and the bespoke screen register, with exact criteria | §6.2, §6.3 |
| `AC-04` | **Criteria are taken from existing KPIs and NFRs**, not invented alongside them | §6.3, `UX-008-D-01` |
| `AC-05` | Field-condition and assisted-user protocols exist and are distinguishable from conformance testing | §5.3, §5.4, §5.5 |
| `AC-06` | A findings-log schema exists with severity, frequency, ownership and a closure rule requiring re-observation | §8 |
| `AC-07` | Reporting conforms to ISO 25062:2025 with mandatory limitations | §10.2 |
| `AC-08` | The missing-baseline problem is quantified and given an irreversible deadline | §6.6, `Q-04` |

**Definition of done.** Complete when every criterion is met, `Q-01` and `Q-04` have owners, the
first benchmark evaluation is scheduled, and `PGD-000`'s `UX-008` row is updated with a fresh
enumeration timestamp.

---

# 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `URD` §2, §3, §18, §25 | The vision, personas, journeys and acceptance criteria evaluated |
| Upstream | `UX-003` §5.4 | The Class B register — the task pool |
| Upstream | `UX-004` §10 | The eight prototypes and gate `IXN-86` |
| Upstream | `UX-006` §3 | The context of use ISO 9241-11 requires |
| Downstream | `UX-001`…`UX-007` | Findings return as design changes (`UTP-52`) |
| Downstream | `GV-009` | User-readiness evidence at each gate |
| Downstream | `GV-005` | Severity 1 findings with delivery consequence |
| Downstream | `BM-001` | Baselines and post-go-live measurement |
| Downstream | `UX-005` §11 | Assisted-user records in the ACR |
| Lateral | `TS-016` | Conformance; §5.5 states the join |
| Lateral | `CG-014` | Content effectiveness; §6.5 states the boundary |
| Lateral | `TS-002` | Test data pack and the Bengali stress set |

---

# 15. References

**Within this repository**
`../PGD-000_…` · `./_CATEGORY_OVERVIEW.md` · `./UX-001`…`./UX-007` ·
`../00_Programme_Governance_and_Control/GV-005`, `GV-008`, `GV-009`, `GV-010` ·
`../15_Benefits_Measurement_and_Assurance/` (`BM-001`)

**Workspace**
`../../1000fix_ERP_Module/04_Portals_and_Applications/04-00` KPI sets ·
`../../project_content/13_Test_and_Acceptance_Content/TS-002`, `TS-015`, `TS-016` ·
`../../project_content/00_Content_Governance_and_Standards/CG-011`, `CG-014` ·
`../../project_content/10_Legal_Policy_and_Compliance/LG-008`, `LG-009` ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_URD.md` §2, §3, §18, §21.5, §25

**External standards and sources**

| Source | Status at verification | Verified |
|---|---|---|
| **ISO 9241-11:2018** — Ergonomics of human-system interaction — Usability: definitions and concepts | Current | 2026-08-18 |
| **ISO 9241-210:2019** §5.7 — evaluate designs against requirements | Current | 2026-08-18 |
| **ISO 25062:2025** — SQuaRE — Common Industry Format (CIF) for reporting usability evaluations. **Released 4 February 2025; cancels and replaces ISO/IEC 25062:2006**, scope expanded beyond usability test reports | Current | 2026-08-18 |
| **ISO/IEC 25066:2016** — SQuaRE — CIF for Usability — Evaluation Report; content items classified required / recommended / optional | Current | 2026-08-18 |
| ISO/IEC 25010:2023 — interaction capability, inclusivity | Current | 2026-08-18 |

---

# 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Head of Product Design | Initial issue. Supplies the validation instrument the `URD`'s user-experience vision has never had (`UXA-18` — 9 of 621 files mention usability testing, none specifies a participant, task, criterion or cadence). Takes every success criterion from **existing** KPIs and NFRs rather than inventing parallel targets. Specifies field-condition and assisted-user protocols, a findings log closed only by re-observation, and ISO 25062:2025 reporting. Raises `UXA-19` — **several `04-00` KPI baselines are "unmeasured" and become unmeasurable after cutover**, while `BM-001` and `GV-008` payback rest on them | *(pending — `PGD-A1-09`)* |

---

*`UX-008` · Category 06 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
