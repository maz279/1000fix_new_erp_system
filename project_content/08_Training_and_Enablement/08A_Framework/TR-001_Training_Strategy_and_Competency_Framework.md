---
id: TR-001
title: Training Strategy and Competency Framework
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Development
author: Learning & Development with HR and Quality Management
reviewers: [HR Director, Quality Manager, Operations Director, Technical Director, CTO, Finance Manager, Localisation Lead, Programme Content Lead]
approver: HR Director with Operations Director
content_class: E
purpose: >
  The learning model, delivery mix, competency levels, assessment philosophy, refresh cadence and
  budget basis for training 800+ internal users across 38+ roles, 67 modules and 12 portals over
  nine waves in two languages. Without a strategy, training becomes a pre-go-live scramble that the
  business absorbs as post-go-live error — and the error lands on customers, on payroll and on
  statutory filings, not on the training function.
traces_to: [M22, M55, M57, M59, M23, P02, P03, 05-04, 06-01, 06-02, MD-009, MD-010, MD-011, TR-002, TR-003, TR-004, TR-022, TR-023, TR-024, CG-008, CG-010]
priority: P1
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M22_Learning_Competency_and_Certification.md §5.1–5.4 FR-LMS-001…040 — competency catalogue, skill matrix, certification register, lapse handling, automatic assignment, effectiveness evaluation, eligibility service to M02
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-LMS-01 — mandatory training must be completed within the assigned deadline; overdue mandatory training restricts the affected work types
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 — KPI-062 certifications current 100%, KPI-063 claims rejected for uncertified technician zero, KPI-064 mandatory training completion on time 95% then 98%
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P03 training-time-to-competence under four hours for a new agent; P02 daily active usage above 95% with a complete Bengali UI
    verified: 2026-08-17
    class: P1
  - source: Bangladesh Labour Act 2006 with Bangladesh Labour Rules 2015 — employers must constitute safety committees in establishments with 50 or more workers, provide regular safety training, and report accidents within the prescribed period; refresher training is expected at least annually or on any change of procedure or equipment
    verified: 2026-08-17
    class: P1
    note: Applicability to a multi-branch service business and the precise committee composition must be confirmed by Legal Counsel — see Open Item O-02
  - source: New World Kirkpatrick Model (Kirkpatrick and Kirkpatrick, 2016) — plan backwards from Level 4 results, define leading indicators, and sustain Level 3 behaviour through Required Drivers (reinforcement, monitoring, accountability). Reported industry practice is that only about a third of organisations evaluate at business-results level, and Level 4 attribution is the model's most-criticised claim
    verified: 2026-08-17
    class: P2
supersedes: none
review_due: 2027-02-17
---

# TR-001 — Training Strategy and Competency Framework

> **Read this before writing any other `TR` file.** Every course pack in `08B` inherits its
> competency levels, delivery mix, assessment philosophy and evaluation model from this document.
> `TR-002` turns it into a per-role plan; `TR-003` turns it into a design standard; `TR-004` turns
> it into a defensible certification regime.

---

## 1. Purpose

The scale is the argument. **800+ internal users · 38+ registered roles · 67 modules · 12 portals ·
9 delivery waves · 36 months · 2 languages · 51+ branches.** No organisation trains that
population by improvisation, and every organisation tries.

The failure mode is specific and predictable:

| Stage | What happens |
|---|---|
| 1 | Build consumes the budget and the calendar; training is scheduled "closer to go-live" |
| 2 | Two weeks before a wave, someone asks who is training 250 agents |
| 3 | A demonstration is recorded, a slide deck is written, and attendance is taken |
| 4 | Users arrive on day one able to recognise screens and unable to complete tasks |
| 5 | The business absorbs the shortfall as **error** — wrong dispatch, wrong stock, wrong pay, wrong tax treatment |
| 6 | The cost appears in operations, in rework and in support volume, never in the training line |

**Stage 6 is why this file exists at `W0`.** Training under-investment does not produce a training
problem; it produces an operations problem that nobody attributes to training. `M22` FR-LMS-035
requires effectiveness to be evaluated by comparing the operational measure the training targeted
before and after — this strategy is what makes that comparison possible rather than rhetorical.

**Consequence of absence (`CP-03`).** Without it: 24 `TR` files authored to no common model; course
packs that cannot be compared, sequenced or substituted; competency levels that mean different
things in `MD-010`, `M22` and each pack; no defensible basis for the certification that gates
warranty work under `BRU-SRM-09`; and no answer to "what does training cost and what does it buy?"

---

## 2. Scope

**In scope:** the learning model and its evaluation framework; competency levels and their binding
to master data; the delivery mix and why each mode is used; the four-hour competence target and
what it actually requires; the Bengali-first principle; assessment philosophy; refresh and decay
management; the statutory training floor; the budget basis; and the governing rules `LS-01`…`LS-18`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Which role takes which course, in what order | [`TR-002_Role_Based_Curriculum_Map.md`](TR-002_Role_Based_Curriculum_Map.md) |
| How a course is designed, storyboarded and scripted | [`TR-003_Course_Design_Standard_and_Storyboard_Template.md`](TR-003_Course_Design_Standard_and_Storyboard_Template.md) |
| Pass marks, attempts, re-certification, appeal | [`TR-004_Assessment_and_Certification_Policy.md`](TR-004_Assessment_and_Certification_Policy.md) |
| The courses themselves | `TR-007`…`TR-021` in `08B_Course_Packs/` |
| Competency and skill taxonomy as master data | [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-010_Competency_and_Skill_Taxonomy.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-010_Competency_and_Skill_Taxonomy.md) |
| Certification and brand authorisation records | [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md) |
| The LMS itself — catalogue, enrolment, tracking, eligibility service | `M22` |
| Technical knowledge content that training draws on | `KB-*` — **`M61` §3.2 places training with `M22`; `M61` does not deliver training** |
| Change communications, champion network as a comms structure | `CM-008` · `TR-023` covers the *training* half |
| Recruitment and onboarding process | [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-023_SOP_Recruitment_and_Onboarding.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-023_SOP_Recruitment_and_Onboarding.md) |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Learning & Development** | Own and operate the strategy; author `TR-002`…`TR-024` against it |
| **HR Director** | Approve; defend the budget; own the competency framework's link to `MD-009` positions |
| **Quality Manager** | Assure the certification regime is defensible to brands and ISO auditors |
| **Operations Director** | Understand what competence is being promised, and when |
| **Technical Director** | Supply the specialist authorship the technician curriculum needs |
| **Branch and workshop managers** | Understand their role in Level 3 transfer — the Required Drivers in §4.3 |
| **Training vendors** | Author interchangeable content to one model |
| **Finance** | Understand the budget basis and the effectiveness claim |

---

## 4. Content

### 4.1 Learning model — planned backwards from results

**The strategy adopts the New World Kirkpatrick model, and adopts it specifically for the parts
most organisations skip.**

| Level | Question | How it is used here |
|:--:|---|---|
| **4 — Results** | Did the business measure move? | **The starting point, not the end.** Every course pack names the `RP-001` KPI it targets *before* its objectives are written |
| **3 — Behaviour** | Is the new practice happening on the job? | Sustained by **Required Drivers** (§4.3), not by hoping |
| **2 — Learning** | Did they acquire the competence? | Assessment per `TR-004` |
| **1 — Reaction** | Did they find it relevant and usable? | Collected, but **never reported as a training outcome** (`LS-04`) |

**`LS-01`: every course pack is designed backwards from a named Level 4 measure.** The template's
§10 evaluation table is completed *first*, not last. A course that cannot name the operational
measure it exists to move is a course nobody can justify keeping.

**`LS-02`: Level 1 reaction data is diagnostic, never evaluative.** A well-liked course that
changes nothing is a failure, and a difficult course that changes practice is a success. Reporting
satisfaction as a training outcome is the single most common way a training function loses
credibility with an operations director.

> **An honest limitation, recorded under `CG-012`.** The Kirkpatrick model's most-criticised claim
> is that Level 4 results can be attributed to training. Industry practice bears the criticism out —
> reported evidence is that only around a third of organisations evaluate at business-results level
> at all. **This strategy does not claim attribution.** It claims *correlation with a stated
> method*, exactly as `M61` T-12 requires of knowledge attribution: state the method, and make no
> causal claim the data does not support (`LS-16`).

### 4.2 Delivery mix

Modelled on the 70-20-10 distribution — most capability is built doing the work, some from other
people, some from formal instruction. **The mix is a design constraint, not an observation.**

| Mode | Share | Used for | Cost driver |
|---|:--:|---|---|
| **On-the-job, structured** | ~70% | Applying the system to real work under supervision; `M22` FR-LMS-027 records OJT with a supervising technician and sign-off | Supervisor time, not trainer time |
| **Social — mentoring, champions, floor-walking** | ~20% | The first two weeks after go-live, when questions are constant and specific | Champion network (`TR-023`) |
| **Formal — classroom, virtual, e-learning** | ~10% | Concepts, rules, statutory content, and anything that must be evidenced identically for every learner | Trainer and content cost |

| Delivery mode | When it is the right choice | When it is the wrong one |
|---|---|---|
| **Classroom** | High-consequence roles, small populations, discussion needed — dispatch, finance, quality, administrators | 250 agents across 51 branches |
| **Virtual instructor-led** | Geographically distributed cohorts of the same role | Low-bandwidth branches; hands-on practice |
| **E-learning** | Consistent, repeatable, statutory, refreshable content for large populations | Anything requiring judgement or a sandbox |
| **Mobile microlearning** | Technicians and riders — `M22` FR-LMS-025 delivers learning inside `P02` | Anything longer than a few minutes |
| **On-the-job with sign-off** | Every operational role, always, after formal content | As a substitute for formal content on statutory topics |
| **Simulation / sandbox** | Anything that touches money, stock or a customer promise | Where no sandbox with realistic data exists (`TS-002`) |

**`LS-03`: no operational role is signed off on formal content alone.** Formal training establishes
that a person *can* do the task; on-the-job sign-off establishes that they *have*. `M22`
FR-LMS-027 provides the mechanism.

### 4.3 Required Drivers — how Level 3 is sustained

**This is the part of the model that is usually omitted, and it is the part that determines whether
any of the rest was worth doing.** Learning decays; the register's own justification for `TR-022`
says so. Four drivers are designed in, each with a named owner:

| Driver | Mechanism | Owner | File |
|---|---|---|---|
| **Reinforce** | Job aids at the point of work; in-app guidance; the technician card set | L&D with Content Design | [`TR-022_Job_Aid_and_Quick_Reference_Library.md`](../08B_Course_Packs/TR-022_Job_Aid_and_Quick_Reference_Library.md) · `KB-016` |
| **Encourage** | Champions and super-users on the floor in the two weeks after each wave | L&D with Change | [`TR-023_Train_the_Trainer_and_Super_User_Kit.md`](../08B_Course_Packs/TR-023_Train_the_Trainer_and_Super_User_Kit.md) · `CM-008` |
| **Monitor** | On-the-job observation against the pack's behaviour criteria; system-side signals — override rates, error rates, help-desk topics | Line managers with L&D | `TR-004` §evaluation · `M22` FR-LMS-035 |
| **Reward** | Certification recognised in `MD-011`; competence gating access and assignment; incentive linkage where `M57` provides it | HR with Quality | `TR-004` · `M57` |

**`LS-04`: a course pack without a named Required Driver for each of the four is not complete.**
The template's §10 Behaviour row is where it is recorded.

### 4.4 Competency levels

**One scale, bound to master data, used identically by every file in this category.**

| Level | Meaning | Bound to | Evidenced by |
|---|---|---|---|
| **Aware** | Knows the concept exists and when to ask | — | Completion |
| **Assisted** | Performs the task with reference material and supervision available | `MD-010` proficiency | Assessment + first OJT sign-off |
| **Competent** | Performs the task unsupervised to standard | `MD-010` proficiency; **the default target for production access** | Assessment + OJT sign-off + observation |
| **Proficient** | Handles exceptions and non-standard cases; can coach | `MD-010` proficiency | Observation over time |
| **Expert** | Sets the standard; authors content; resolves what others escalate | `MD-010`; the `R12`/`R13` population | Contribution and peer recognition |

**Technical repair levels are a separate, orthogonal scale** — `L1` / `L2` / `L3_board` in
`MD-010`, `MD-021`, `MD-025` and every `KB` file. A technician can be *Competent* at `L1` and
*Aware* at `L3_board`.

**`LS-05`: the two scales are never merged and never used as synonyms.** Conflating "L2" the repair
level with "level 2" the proficiency step is a defect that will propagate into dispatch eligibility,
because `M22` FR-LMS-039 exposes eligibility to `M02` from this data.

### 4.5 The four-hour target

`P03` targets **training-time-to-competence under four hours for a new Service Centre Agent** —
the largest single user population at 150–250 people, with continuous turnover.

Four hours is achievable only if it is understood correctly:

| What four hours **is** | What it **is not** |
|---|---|
| Time to *Competent* on the **core intake task set** — the twenty things an agent does every day | Time to competence on all fourteen `P03` workspaces |
| Formal + guided practice on a sandbox with realistic data | Formal instruction alone |
| Achieved because the **UI copy, job aids and error messages do the teaching** (`UI-013`, `UI-023`, `TR-022`) | Achieved by compressing a curriculum |
| Measured by assessment plus first-week observation | Measured by attendance |

**`LS-06`: the four-hour target is a joint commitment between L&D and product design, and it is
reported as such.** `P03`'s own justification says the target is met by copy, not features
(`UI-013`). If the interface is unclear, no curriculum recovers it inside four hours, and L&D must
be able to say so with evidence rather than absorb the shortfall.

### 4.6 Bengali is the delivery language, not a translation layer

`CG-010` places 20 of the 24 `TR` files as bilingual. For the field workforce it is stronger than
that:

| Population | Size | Position |
|---|---|---|
| Field technicians | 200–400 | **Bengali-native delivery.** `CG-010` records that *"translated training teaches translated concepts; native training teaches the job"* |
| Riders and logistics | 60–175 | Bengali-native, mobile, short-form |
| Branch agents, store keepers, cashiers | 250+ | Bengali primary, English technical terms retained |
| Head-office functions — finance, HR, quality, IT | ~80 | English acceptable; Bengali where the audience prefers it |

**`LS-07`: technician and rider content is authored in Bengali, not translated into it** — the same
rule `KB-016` `RC-09` applies to reference cards, and for the same reason.
**`LS-08`: codes, part numbers, model names, measurements and system field labels are never
translated** (`AU-31`, `KA-17`).

> **The capability gap this creates is real and is recorded.** `KB-002` `O-05` establishes that
> Bengali technical terminology for board-level electronics does not substantially exist. A
> curriculum that must teach in Bengali, using a technical vocabulary that has not been built, is
> constrained by the vocabulary work — not by the instructional design. `O-05` below.

### 4.7 Assessment philosophy

Detailed policy is `TR-004`. The philosophy it implements:

| Principle | Consequence |
|---|---|
| **Assessment establishes fitness to act, not attendance** | Certification gates warranty work through `BRU-SRM-09`; it must be defensible to a brand partner and an ISO auditor |
| **Assess what the job requires, in the form the job requires it** | Practical demonstration for technicians; scenario judgement for agents and dispatchers; system transaction for finance and inventory |
| **A large, rotating item bank or no bank at all** | A small static question set is certification in name only — the register's own words for `TR-005` |
| **Failure is a development event, not a disciplinary one** | With the exception of statutory and safety content, where competence is a condition of the work |
| **Evidence is retained per learner** | `M22` FR-LMS-038 must produce a competence evidence file on demand for ISO 9001 and brand audits |

### 4.8 Refresh, decay and re-certification

| Content class | Refresh | Trigger |
|---|---|---|
| **Statutory and safety** | **Annual minimum** | Bangladesh Labour Rules expectation; any change of procedure or equipment; any incident |
| Brand certification | Per the brand's stated validity in `MD-011` | Brand requirement; lapse suspends assignment (`M22` FR-LMS-013) |
| Technician technical | 24 months, or on device-family change | New model generation; rework pattern; `KB-010` bulletin |
| System / role training | On each release affecting the role | `TR-024` release-training standard |
| Regulatory and tax | On each Finance Act or NBR change | `MD-037`, `M51` |
| Everything else | 24 months | Gap analysis (`M22` FR-LMS-005) |

**`LS-09`: overdue mandatory training restricts the affected work types** (`BRU-LMS-01`). This is a
hard rule in `05-05`, not a training-function preference, and it means the training calendar has
operational consequences that must be planned with `M55` (`M22` FR-LMS-022).

### 4.9 The statutory floor

**`LS-10`: some training is a legal obligation and is not subject to prioritisation.**

| Obligation | Basis | Population |
|---|---|---|
| **Workplace safety training with annual refresher** | Bangladesh Labour Act 2006 with Labour Rules 2015 — regular safety training, refresher at least annually or on any change of procedure or equipment | **Every employee** |
| **Safety committee** | Required in establishments with 50 or more workers | Per qualifying establishment |
| Accident reporting | Prescribed reporting period | HSE with HR |
| Competence for ISO 9001:2015 | Clause 7.2 — determine necessary competence, ensure it, retain documented evidence | Anyone affecting quality performance |
| Brand authorisation | Brand agreements; `MD-011` | Technicians on warranty work |
| Refrigerant handling | Regime unconfirmed — `KB-005` `O-02`, `KB-013` `O-05` | Refrigerant-certified technicians |

> **This section resolves an open finding from another category, and it is worth stating plainly.**
> `AUDIT-006` **SP-02** recorded, as a HIGH finding, that *"no HSE course pack exists in a 452-file
> content register"* while `SP-030` states that safety overrides every performance target and
> `BRU-LMS-01` restricts work when mandatory training is overdue — leaving `KPI-064` measuring
> completion against a curriculum with no safety course in it.
>
> **The research position is worse than the audit assumed.** Safety training here is not merely a
> content gap; on the sources above it is a **statutory duty**. `TR-002` §7 carries the resolution
> and the register consequence; it is recorded here because the *strategy* is where a statutory
> floor belongs.

### 4.10 Budget basis

**`LS-11`: training effort is estimated from population × role complexity × refresh, and is stated
as a range with its assumptions visible.**

| Cost element | Driver | Note |
|---|---|---|
| Content authoring | 24 `TR` files; per-pack effort in each file's §12 | The dominant W0–W2 cost |
| **Specialist authorship** | `TR-005`, `TR-009` require `R12` technical time | Competes directly with repair capacity — the same constraint `AUDIT-008` R-07 records for `KB` |
| Translation and in-context sign-off | 20 bilingual files, `BN-018` | Not a line item anyone remembers to budget |
| Delivery — trainer days | Population ÷ cohort size × duration × waves | 800+ users over 9 waves means repeated delivery, not one pass |
| **Learner time away from work** | The largest cost, and the one never counted | 250 agents × 4 hours is 1,000 productive hours per pass |
| Champion network | `TR-023`; backfill for champion time | `CM-008` shares it |
| Sandbox and test data | `TS-002` | Shared with test |
| LMS | `M22` build and licence | Not L&D's budget line |
| Refresh | Annual statutory + release training (`TR-024`) | **Perpetual, not project** |

**`LS-12`: learner time is costed and reported.** A training plan that shows only trainer cost
understates the true figure by an order of magnitude and invites decisions that look cheap.

### 4.11 Governing rules

| # | Rule | Class |
|---|---|:--:|
| **LS-01** | Every course pack is designed backwards from a named `RP-001` Level 4 measure | **H** |
| **LS-02** | Level 1 reaction data is diagnostic, never reported as a training outcome | **H** |
| **LS-03** | No operational role is signed off on formal content alone; OJT sign-off is required | **H** |
| **LS-04** | Every pack names a Required Driver for reinforce, encourage, monitor and reward | **H** |
| **LS-05** | Proficiency levels and repair levels are separate scales and are never merged | **H** |
| **LS-06** | The four-hour target is a joint L&D and product commitment, reported jointly | **C** |
| **LS-07** | Technician and rider content is authored in Bengali, not translated | **H** |
| **LS-08** | Codes, part numbers, model names, measurements and field labels are never translated | **H** |
| **LS-09** | Overdue mandatory training restricts the affected work types (`BRU-LMS-01`) | **H** |
| **LS-10** | Statutory training is not subject to prioritisation or deferral | **H** |
| **LS-11** | Effort is estimated from population × complexity × refresh, with assumptions visible | **C** |
| **LS-12** | Learner time is costed and reported alongside delivery cost | **C** |
| **LS-13** | Competence is evidenced per learner and retrievable for ISO and brand audit (`M22` FR-LMS-038) | **H** |
| **LS-14** | Training that grants production access to money-, stock- or customer-affecting functions requires assessment, not attendance | **H** |
| **LS-15** | Course content cites the governing `SP`, `KB`, `MD` or `LG` file rather than restating it (`CP-01`) | **H** |
| **LS-16** | Effectiveness claims state their method and make no causal claim the data does not support | **H** |
| **LS-17** | A course whose target measure does not move is revised or retired within two evaluation cycles | **A** |
| **LS-18** | Training scheduling publishes to `M55` so that committed learners are unavailable for assignment (`M22` FR-LMS-022) | **C** |

> Class: **H** hard block · **A** approved override · **S** soft warning · **C** computed — the
> same scale as `05-05` §1.

### 4.12 What is measured

| Measure | Definition | Target | Source |
|---|---|---|---|
| **Mandatory training completed on time** | | **95% W7, 98% W9** | `KPI-064` |
| **Certifications current, no lapses** | | **100%** | `KPI-062` |
| **Claims rejected for an uncertified technician** | | **Zero** | `KPI-063` |
| Time-to-competence, Service Centre Agent | To *Competent* on the core task set | **< 4 hours** | `P03`, `LS-06` |
| Technician daily active usage of `P02` | Adoption as a proxy for enablement | **> 95%** | `P02` |
| Assessment pass rate at first attempt | Per pack | Set per pack; **a rate near 100% means the assessment is too easy** | `TR-004` |
| OJT sign-off completion before production access | | 100% (`LS-03`) | `M22` FR-LMS-027 |
| Level 3 observation completed per pack | | Per pack schedule | `LS-04` |
| **Level 4 measure movement per pack** | The `RP-001` KPI the pack targets | Stated per pack | `LS-01`, `LS-16` |
| Learner hours consumed | Against plan | Reported (`LS-12`) | L&D |
| Courses retired for non-effect | | Reported, not zero (`LS-17`) | L&D |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `M22` Learning, Competency and Certification | The system that operates everything here — catalogue, assignment, assessment, certification, eligibility |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-009_Role_and_Job_Title_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-009_Role_and_Job_Title_Master.md) | The roles `TR-002` maps courses to |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-010_Competency_and_Skill_Taxonomy.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-010_Competency_and_Skill_Taxonomy.md) | Proficiency levels in §4.4 |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md) | Certification validity and lapse |
| `05-04` Role, Permission and Access Matrix | The 38 roles and their populations |
| `06-01` Implementation Roadmap | Wave sequencing that drives the training calendar |
| `RP-001` KPI Dictionary | Level 4 measures under `LS-01` |
| [`../../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md`](../../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) | §4.6 language position |
| `M55` Time, Attendance and Workforce Scheduling | `LS-18` availability publishing |
| `M59` Health, Safety and Wellbeing | The statutory floor in §4.9 |
| `KB-*` Knowledge Base | Technical content courses draw on (`LS-15`); `M61` §3.2 keeps the boundary |

| Depended on by |
|---|
| `TR-002`…`TR-024` — every file in this category · `M22` configuration · `CM-008` champion network · `OP-006` release operations |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Annual**, and at every wave boundary that adds a portal or a role |
| Trigger for out-of-cycle review | `KPI-064` or `KPI-062` missed for two quarters · a statutory change affecting §4.9 · the four-hour target missed at W1 · a training-attributed operational failure |
| Owner | Learning & Development, with HR Director accountable |
| Change log | `RF-006` |
| Enforcement | `LS-01`…`LS-18`; `CG-008` Definition of Done; `TR-003` design standard |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The training budget is not in the approved business case.** The repository README records audit finding `AF-09` — content effort is unbudgeted programme-wide — and §4.10 shows learner time alone at roughly 1,000 productive hours per pass for agents. **A strategy at `W0` with no budget is a document, not a plan** | HR Director with Finance Manager | **W0 — this is the first thing that must be true** |
| **O-02** | **The statutory training obligations in §4.9 are stated from secondary sources and need Legal confirmation** — specifically which establishments qualify for a safety committee, the composition required, the refresher interval and the record-retention duty. `CG-013` escalation applies | Legal Counsel with HSE Lead | **W1 — `LS-10` is unenforceable until the floor is confirmed** |
| **O-03** | **`AUDIT-006` SP-02 is unresolved and this category cannot resolve it alone.** Six SOPs describe work by roles with no course pack, including `SP-030` HSE which applies to every employee. The register is fixed at 24 `TR` files (`CM-R1`); closing the gap requires either a register change or a named alternative route. `TR-002` §7 carries the analysis | Programme Content Lead with Training Lead and HR Director | **W1 — HSE before W2 field rollout** |
| **O-04** | No trainer establishment exists. §4.2 assumes classroom and virtual delivery to 800+ users over nine waves; the number of trainers, whether they are internal or contracted, and who backfills them is undecided | HR Director with L&D | **W0 — it drives the budget in `O-01`** |
| **O-05** | **Bengali technical terminology does not exist for the technician curriculum** (`KB-002` `O-05`). `LS-07` requires Bengali authoring; the vocabulary must be built first, with `R12` specialists, and that work is not scheduled | Localisation Lead with Technical Director | **W1 — it gates `TR-009`, the only `P0` file in this category** |
| **O-06** | The sandbox and training test data (`TS-002`) is a Category 13 deliverable that Category 08 depends on. **Every practical exercise in every pack assumes it exists.** Category 13 is unstarted | Test Lead with L&D | **W1 — before the first pack is delivered** |
| **O-07** | Whether `M22` is available to operate this strategy in W1 is unconfirmed. The `TR` register places twelve files at W1; if the LMS lands later, assignment, assessment, evidence and the `BRU-LMS-01` restriction are all manual | CTO with HR Director | **W1** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — all six sections present, §7 added per category convention
- [x] Learning model stated with its evaluation framework and its **acknowledged limitation** on Level 4 attribution
- [x] Required Drivers designed in, with named owners and named files, rather than assumed
- [x] Delivery mix stated as a design constraint with right-choice and wrong-choice guidance
- [x] Competency levels bound to `MD-010`, and kept explicitly separate from repair levels (`LS-05`)
- [x] The four-hour target defined precisely enough to be tested, and its joint ownership stated
- [x] Bengali stated as a delivery language with the capability gap it exposes recorded
- [x] Statutory floor identified and sourced, resolving the strategy half of `AUDIT-006` SP-02
- [x] Budget basis includes learner time, the cost most often omitted (`LS-12`)
- [x] Every factual and statutory claim carries a source and a verification date (`CG-012`)
- [x] `BRU-LMS-01` cited to `05-05`; `FR-LMS-*` cited to `M22`; `KPI-062`/`-063`/`-064` cited to `06-02`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` training budget approved — outstanding; the strategy is not executable without it**
- [ ] **`O-02` statutory obligations confirmed by Legal — outstanding**
- [ ] **`O-03` `AUDIT-006` SP-02 resolved — outstanding; carried into `TR-002`**
- [ ] Named approvers recorded — **pending HR Director and Operations Director**
- [x] English-only, per `CG-010` §3.2 — framework content, head-office audience

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
