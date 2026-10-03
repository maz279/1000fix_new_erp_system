---
id: TR-004
title: Assessment and Certification Policy
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Quality with Learning & Development
author: Quality Management with Learning & Development and HR
reviewers: [HR Director, Quality Manager, Technical Director, HSE Lead, Legal Counsel, Operations Director, Warranty Claims Officer, Programme Content Lead]
approver: Quality Manager with HR Director
content_class: E
purpose: >
  Pass marks, attempts, re-certification intervals, evidence, consequences of failure and appeal.
  Technician certification gates brand warranty work through a hard business rule that blocks
  assignment; the policy behind that block must be defensible to a brand partner auditing our
  competence records and to an ISO 9001 auditor testing clause 7.2. A certification regime that
  cannot survive either audit is a liability rather than a control.
traces_to: [M22, M23, M02, M09, M29, M57, M59, 05-04, MD-010, MD-011, TR-001, TR-002, TR-003, TR-005, TR-006, TR-024, LG-022, SP-029]
priority: P1
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M22 §5.2 FR-LMS-009…016 certification register, evidence, expiry tracking, renewal workflow, lapse handling with automatic suspension of assignment eligibility, statutory certification, internal certification
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M22 §5.4 FR-LMS-038 competence evidence file produced on demand per employee or per role for ISO 9001 and brand audits; FR-LMS-039 eligibility service to M02; FR-LMS-040 override logging
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-09 a service order cannot be assigned to a technician lacking a current certification for that brand's warranty work; BRU-HRM-01 a technician cannot be assigned brand warranty work once their certification for that brand has expired; BRU-LMS-01 overdue mandatory training restricts the affected work types; BRU-LMS-02 a marketplace engineer cannot be activated in a category without passing that category's qualification
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 — KPI-062 certifications current no lapses 100%, KPI-063 claims rejected for uncertified technician zero, KPI-064 mandatory training completion on time
    verified: 2026-08-17
    class: P1
  - source: ISO 9001:2015 clause 7.2 competence — determine the necessary competence of persons whose work affects quality performance, ensure competence on the basis of education, training or experience, take action where needed and evaluate its effectiveness, and retain documented information as evidence of competence
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# TR-004 — Assessment and Certification Policy

> **This policy is read by people who do not work here.** A brand partner auditing why we assigned
> a technician to their warranty work, and an ISO 9001 auditor testing clause 7.2, both arrive at
> this document. It is written to be defensible to them, not to be comfortable for us.

---

## 1. Purpose

`BRU-SRM-09` is a **hard block**: a service order cannot be assigned to a technician lacking a
current certification for that brand's warranty work. `BRU-HRM-01` restates it for expiry.
`M22` FR-LMS-013 makes the suspension automatic on lapse.

A hard block of that kind is only as good as the certification behind it. If certification means
"attended a session", the block prevents nothing — it simply records that an unqualified person
attended something before being assigned. **This policy is what makes the block meaningful.**

Three audiences test it:

| Who | Tests | Consequence of failing the test |
|---|---|---|
| **Brand partner** | Were the technicians who worked on our products actually qualified, and can you show me? | Claim rejection (`KPI-063` targets zero), authorisation withdrawal, revenue loss |
| **ISO 9001 auditor** | Clause 7.2 — did you determine competence, ensure it, evaluate the action, and retain evidence? | Non-conformance against the certification the company markets as its differentiator (`LG-022`) |
| **The company itself, after an incident** | Was this person competent to do what they did? | The answer must exist before the question is asked |

**Consequence of absence (`CP-03`).** Certification becomes attendance; `BRU-SRM-09` blocks on a
record that means nothing; `M22` FR-LMS-038 produces an evidence file with no evidence in it; and
`KPI-062`'s 100% target is met by issuing certificates that would not survive being looked at.

---

## 2. Scope

**In scope:** what assessment establishes; assessment methods by competence type; how pass marks
are set; attempts, remediation and failure; certification types, validity and renewal; lapse
handling and its operational consequence; override logging; evidence and retention; assessment
integrity; appeal; and rules `AS-01`…`AS-22`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Learning model and competency levels | [`TR-001_Training_Strategy_and_Competency_Framework.md`](TR-001_Training_Strategy_and_Competency_Framework.md) |
| Who must be certified in what | [`TR-002_Role_Based_Curriculum_Map.md`](TR-002_Role_Based_Curriculum_Map.md) |
| Item writing and bank construction | [`TR-005_Question_Bank_Technician_Certification.md`](TR-005_Question_Bank_Technician_Certification.md) · [`TR-006_Question_Bank_Functional_Roles.md`](TR-006_Question_Bank_Functional_Roles.md) |
| Course design and assessment placement in the design sequence | [`TR-003_Course_Design_Standard_and_Storyboard_Template.md`](TR-003_Course_Design_Standard_and_Storyboard_Template.md) `DS-01` |
| The certification register as master data | [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md) |
| Competency taxonomy and proficiency scale | [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-010_Competency_and_Skill_Taxonomy.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-010_Competency_and_Skill_Taxonomy.md) |
| Performance management and disciplinary process | HR policy · `M57` — **`AS-14` keeps them separate from assessment** |
| Marketplace seller qualification | `BRU-LMS-02` · `TR-019` · Category 18 `EO` |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Quality Manager** | Own the regime; defend it at brand and ISO audit |
| **L&D** | Set pass marks, run assessment, manage remediation |
| **Assessors** — `R09`, `R12`, `R32`, trainers | Know what they are certifying and on what basis |
| **Line managers** | Understand what a lapse does to their team's assignability |
| **`R28` Warranty Claims Officer** | Evidence technician certification on claims |
| **HR** | Operate renewal, records and appeal |
| **Brand partners and auditors** | Assess whether the regime is credible |

---

## 4. Content

### 4.1 What assessment establishes

**`AS-01`: assessment establishes fitness to perform, not exposure to content.**

| Assessment establishes | Assessment does not establish |
|---|---|
| The person can perform the task to the stated standard under the stated conditions | The person attended |
| Under conditions resembling the job | Under conditions resembling a classroom |
| With evidence retained per learner (`AS-16`) | With a signature on a register |
| Repeatably, by different assessors reaching the same result | By whoever happened to run the session |

### 4.2 Method by competence type

**`AS-02`: the method matches what the competence actually is.**

| Competence type | Method | Assessor | Evidence retained |
|---|---|---|---|
| **Procedural — system transaction** | Sandbox transaction completed to criterion (`TS-002`) | System-scored | Transaction record + score |
| **Procedural — physical repair** | **Practical demonstration** on a real or representative unit | `R12` / `R09` qualified above the level being assessed | Assessor sign-off + photographs |
| **Judgement** — dispatch, escalation, override, complaint | Scenario items with defensible reasoning | L&D with domain owner | Item responses |
| **Knowledge — codes, rules, thresholds** | Item bank, rotating (`TR-005`, `TR-006`) | System-scored | Response set |
| **Safety and statutory** | Item bank **plus** practical where physical, **plus** supervisor confirmation | HSE-approved assessor | Full record — **retained longest** |
| **Behavioural — customer interaction** | Role play or live-call observation against a rubric | Supervisor with L&D | Rubric score + notes |
| **Applied competence on the job** | Structured OJT sign-off (`M22` FR-LMS-027) | Supervising technician or line manager | Task list + sign-off |

**`AS-03`: no certification that gates work is granted on a written item bank alone.** Every
gating certification requires at least one non-written component — practical, observation or OJT
sign-off. A person who can answer questions about a refrigerant recovery has not recovered a charge.

### 4.3 Pass marks

**`AS-04`: a pass mark is set from consequence, not from convention.** 70% is a convention, not a
standard, and it means different things on a 10-item and a 60-item assessment.

| Consequence class | Pass standard | Rationale |
|---|---|---|
| **Safety / statutory** | **100% on all safety-critical items**, 80% overall | There is no acceptable proportion of safety items a person may get wrong |
| **Money, stock or customer commitment** | 80% overall, **100% on the items covering hard business rules** (`BRU-*`) | A person who does not know a hard rule will breach it |
| **Brand warranty work** | Per the brand's stated requirement where one exists; otherwise 80% overall + practical pass | The brand's standard governs its own authorisation |
| Judgement-based roles | 75% overall with **no single competence area below 60%** | Prevents a strong area masking a weak one |
| General system competence | 75% overall | |
| Awareness-level content | Comprehension check, pass/fail | Not a certification |

**`AS-05`: critical items are declared before the assessment is used, not after results are seen.**
Deciding which items were critical once you know who failed is not assessment.

**`AS-06`: a first-attempt pass rate at or near 100% triggers a review of the assessment, not
celebration.** It indicates the assessment is not discriminating, which means it is evidencing
nothing.

### 4.4 Attempts, remediation and failure

| Element | Standard | Exception |
|---|---|---|
| Attempts | **Three**, with mandatory remediation between attempts 2 and 3 | Safety and statutory: **two**, then a full re-take of the course |
| Interval between attempts | Minimum 24 hours; after attempt 2, minimum 5 working days with remediation completed | |
| Remediation | Targeted at the failed competence area, not a repeat of the whole course | |
| After the final attempt | **Role review**, not automatic dismissal (`AS-14`) | Statutory competence that is a condition of the work — the person cannot perform that work |
| Practical failure | Re-attempt after supervised practice; the assessor records what was deficient | |
| Record | **Every attempt is recorded, including failures** (`AS-16`) | |

**`AS-07`: failure is a development event.** The exception is narrow and stated: where competence is
a statutory or contractual condition of the work, the person cannot do that work until they are
competent. That is a fact about the work, not a judgement about the person, and it is communicated
that way.

**`AS-08`: failure records are visible to HR and the line manager, and are not used as the sole
basis for a performance rating.** `M57` may take competence into account; assessment is not a
performance-management instrument (`AS-14`).

### 4.5 Certification types

`M22` FR-LMS-009 registers four types. Each behaves differently and the differences matter.

| Type | Issued by | Validity | On lapse | Register |
|---|---|---|---|---|
| **Internal** | 1000FiX (`M22` FR-LMS-016) | 24 months default | Suspends the internal competence claim | `MD-011` |
| **Brand / manufacturer** | The brand | **Per the brand's terms** | **Suspends assignment to that brand's warranty work** (`BRU-SRM-09`, `BRU-HRM-01`) | `MD-011` |
| **Statutory** | The issuing authority | Per the instrument | **Suspends the regulated activity entirely** | `MD-011` |
| **Safety** | 1000FiX or an external body | **Annual** minimum (`LS-10`) | **Restricts the affected work types** (`BRU-LMS-01`) | `MD-011` + HSE |

**`AS-09`: 1000FiX never issues a certification it is not authorised to issue.** An internal
certificate that resembles a brand authorisation, or implies statutory competence the company
cannot confer, is a misrepresentation to the technician and to the customer.

### 4.6 Validity, renewal and lapse

`M22` FR-LMS-011 tracks expiry with configurable alerts; FR-LMS-012 raises and escalates a renewal
task; FR-LMS-013 **automatically suspends assignment eligibility on lapse**.

| Stage | Timing | Action | Owner |
|---|---|---|---|
| Alert 1 | **90 days** before expiry | Renewal task raised; learner and line manager notified | `M22` |
| Alert 2 | 45 days | Escalation to line manager | `M22` |
| Alert 3 | 14 days | Escalation to Quality Manager; **scheduling becomes mandatory** | `M22` |
| **Expiry** | Day 0 | **Assignment eligibility suspended automatically** (FR-LMS-013) | `M22` → `M02` |
| Post-lapse | +30 days | HR and Quality review; the person is not assignable to that work throughout | Quality with HR |

**`AS-10`: there is no grace period on a gating certification.** A brand does not recognise our
grace period, `BRU-HRM-01` does not contain one, and `KPI-062` targets **100% current, zero
lapses**. The 90-day alert exists precisely so that a grace period is never needed.

**`AS-11`: a lapse is a management failure before it is an individual one.** Three escalations
fired and nobody acted. The post-lapse review looks at the scheduling, not only at the person.

### 4.7 Override

`M22` FR-LMS-040 requires that where dispatch overrides an eligibility rule, the override, the
approver and the reason are recorded and reported.

| # | Rule | Class |
|---|---|:--:|
| **AS-12** | **`BRU-SRM-09` brand-warranty certification cannot be overridden.** The block is absolute; a brand's authorisation is not ours to waive | **H** |
| **AS-13** | Where an override of a non-brand eligibility rule is permitted, it is approved at Operations Director level, recorded with a reason from `MD-026`, and **reported monthly to Quality** | **A** |
| — | Statutory competence cannot be overridden by anyone | **H** |
| — | Safety competence cannot be overridden by anyone | **H** |

> **`AS-12` is the rule most likely to be pressed on a busy day**, when a certified technician is
> unavailable and a customer is waiting. The correct answer is to reschedule or route to an
> equipped site (`BRU-SRM-14` pattern), and the cost of that is far below a rejected claim plus a
> damaged authorisation.

### 4.8 Evidence and audit defensibility

`M22` FR-LMS-038 must produce, on demand, a complete competence evidence file per employee or per
role for ISO 9001 and brand audits.

**`AS-15`: the evidence file is assembled continuously, not on request.** An evidence file
constructed the week a brand audit is announced is exactly what an auditor is looking for.

| Evidence element | Retained | Why |
|---|---|---|
| Curriculum assigned and completed | Permanently (`M22` FR-LMS-037) | Clause 7.2 — competence determined and ensured |
| **Every assessment attempt, including failures** | Permanently | An evidence file with no failures in it is not credible |
| Practical demonstration record with assessor identity | Permanently | Who certified, and were they qualified to |
| OJT sign-off, tasks observed | Permanently | Applied competence |
| Certificate documents and verification status | Per validity + 6 years | `M22` FR-LMS-010 |
| Renewal history and lapse events | Permanently | Shows the control operating, including when it did not |
| Override records | Permanently | FR-LMS-040 |
| **Effectiveness evaluation** | Per cycle | Clause 7.2 requires evaluating the effectiveness of the action taken — **not just that training happened** |

**`AS-16`: assessors are themselves qualified, and their qualification is recorded.** An assessor
certifying at a level they do not hold is the single fastest way to invalidate an entire
certification population.

### 4.9 Integrity

| Risk | Control |
|---|---|
| **Item exposure** — questions circulate | Rotating banks with calibrated difficulty (`TR-005`, `TR-006`); items retired on exposure |
| Assessment taken by someone else | Identity confirmed at practical and observed components; system assessments tied to the individual's authenticated session (`M29`) |
| Assessor leniency | Assessor calibration; second-assessor sampling on gating certifications; `AS-06` pass-rate monitoring |
| Assessor conflict | **The assessor is not the person's direct line manager for gating certifications** where an alternative exists |
| Answer sharing in a cohort | Item rotation; varied scenario data |
| Pressure to pass | `AS-12` absolutes; override reporting; `AS-11` treating lapses as management failures removes the incentive to fudge |

**`AS-17`: an integrity breach invalidates the certification, and the affected work is reviewed.**
Not only the certification — the work done under it.

### 4.10 Appeal

**`AS-18`: every assessment decision may be appealed, and the appeal is heard by someone who was
not involved in it.**

| Stage | Who | Within |
|---|---|---|
| 1 — Review | L&D reviews the record and the marking | 5 working days of the result |
| 2 — Re-assessment | A different assessor, where the ground is assessor judgement | 10 working days |
| 3 — Panel | Quality Manager with HR and a domain expert, none previously involved | 20 working days |
| Outcome | Upheld, amended, or confirmed — **recorded either way** | |

**`AS-19`: an upheld appeal triggers a review of the item or the rubric, not only the individual
result.** If one person was marked wrongly, the instrument probably marked others wrongly too.

### 4.11 Governing rules

| # | Rule | Class |
|---|---|:--:|
| **AS-01** | Assessment establishes fitness to perform, not exposure to content | **H** |
| **AS-02** | Method matches the competence type | **H** |
| **AS-03** | No gating certification on a written bank alone | **H** |
| **AS-04** | Pass marks are set from consequence | **H** |
| **AS-05** | Critical items are declared before use | **H** |
| **AS-06** | Near-100% first-attempt pass rates trigger assessment review | **C** |
| **AS-07** | Failure is a development event, except where competence is a condition of the work | **H** |
| **AS-08** | Failure records are not the sole basis of a performance rating | **H** |
| **AS-09** | 1000FiX never issues a certification it is not authorised to issue | **H** |
| **AS-10** | No grace period on a gating certification | **H** |
| **AS-11** | A lapse is reviewed as a management failure first | **C** |
| **AS-12** | Brand-warranty certification cannot be overridden | **H** |
| **AS-13** | Permitted overrides are approved at Operations Director level, reasoned and reported | **A** |
| **AS-14** | Assessment is not a performance-management instrument | **H** |
| **AS-15** | The competence evidence file is assembled continuously | **C** |
| **AS-16** | Assessors are qualified above the level they assess, and it is recorded | **H** |
| **AS-17** | An integrity breach invalidates the certification and triggers review of the work done under it | **H** |
| **AS-18** | Every decision is appealable to someone not involved | **H** |
| **AS-19** | An upheld appeal triggers instrument review | **C** |
| **AS-20** | Re-certification intervals are per §4.5, and safety is annual (`LS-10`) | **H** |
| **AS-21** | Every certification maps to a `MD-011` register entry; none exists only in a course record | **H** |
| **AS-22** | Assessment results publish to `M22` so eligibility (FR-LMS-039) is answered from one source | **C** |

### 4.12 What is measured

| Measure | Target | Source |
|---|---|---|
| **Certifications current, no lapses** | **100%** | `KPI-062` |
| **Claims rejected for an uncertified technician** | **Zero** | `KPI-063` |
| **Mandatory training completed on time** | 95% W7, 98% W9 | `KPI-064` |
| First-attempt pass rate per assessment | Monitored; near-100% investigated (`AS-06`) | L&D |
| Lapses reaching day 0 | **Zero** (`AS-10`) | `M22` |
| Overrides raised and approved | Reported monthly; trending down | FR-LMS-040 |
| Evidence files producible on demand | 100% within one working day | `AS-15` |
| Appeals raised, upheld | Reported; a zero-appeal regime is a warning sign, not a success | `AS-18` |
| Assessor qualification currency | 100% | `AS-16` |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `M22` §5.2 and §5.4 | Certification register, expiry, lapse suspension, evidence file, eligibility service, override logging |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md) | `AS-21` — every certification maps here |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-010_Competency_and_Skill_Taxonomy.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-010_Competency_and_Skill_Taxonomy.md) | Proficiency and repair levels |
| [`TR-005_Question_Bank_Technician_Certification.md`](TR-005_Question_Bank_Technician_Certification.md) · [`TR-006_Question_Bank_Functional_Roles.md`](TR-006_Question_Bank_Functional_Roles.md) | The instruments this policy governs |
| `M02` Field Service and Dispatch | Consumes eligibility; enforces `BRU-SRM-09` |
| `M29` Identity and Access | Authenticated session for assessment integrity; access gating |
| `M23` · [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) | ISO clause 7.2 evidence; audit programme |
| `TS-002` | Sandbox for procedural assessment |
| `LG-022` Quality Policy and ISO 9001 Statement Set | The certification the company markets |

| Depended on by |
|---|
| Every course pack's §7 Assessment section · `M22` configuration · `MD-011` · `M02` dispatch eligibility · `M09` claim evidence |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Annual**, and after the first brand or ISO audit that tests it |
| Trigger for out-of-cycle review | Any claim rejected for an uncertified technician (`KPI-063` breach) · a lapse reaching day 0 · an integrity breach · a brand changing its certification terms · a statutory change |
| Owner | Quality Manager with L&D |
| Change log | `RF-006` |
| Enforcement | `AS-01`…`AS-22`; `M22` FR-LMS-013 automatic suspension; `BRU-SRM-09` hard block |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **Brand-specific certification requirements are unknown.** §4.5 defers to "the brand's stated requirement where one exists"; `MD-017` records the "17+ brands" figure as unverified (`00-07` H2-12) and no brand's competence terms are held. **`BRU-SRM-09` cannot be configured without them** | Commercial with Quality Manager | **W2 — blocking for brand warranty work** |
| **O-02** | **The refrigerant certification regime is unconfirmed** (`KB-005` `O-02`, `KB-013` `O-05`). §4.5 lists statutory certification as a type; for refrigerant there may be no issuing authority identified | HSE Lead with Legal Counsel | **W2** |
| **O-03** | Whether `M29` can gate system access on an `M22` competence signal is unconfirmed — the same question `TR-002` `O-07` raises. If it cannot, `AS-22` and `CU-05` are manual controls across 800+ users | CTO with Security Lead | **Before W1 go-live** |
| **O-04** | The assessor population does not exist. `AS-16` requires assessors qualified above the level they assess; for `L3_board` that is the 15–30 `R12` specialists, who are also the scarcest resource in the company | Technical Director with Quality Manager | **W2** |
| **O-05** | Evidence retention periods in §4.8 are stated as "permanently" and "validity + 6 years". **These must be reconciled with `LG-009` Data Retention and Deletion Schedule**, which owns retention, and with any statutory minimum | Legal Counsel with Quality Manager | W2 |
| **O-06** | Proctoring arrangements for system-delivered assessment across 51+ branches are unspecified. §4.9 states the risks; the operating answer is undecided | L&D with `R33` | W2 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §7 added per category convention
- [x] Written for the external audiences that actually test it — brand partner and ISO auditor
- [x] Assessment method bound to competence type (`AS-02`), with written-only certification prohibited for gating (`AS-03`)
- [x] Pass marks derived from consequence rather than convention, with 100% required on safety-critical items
- [x] Near-perfect pass rates treated as an instrument defect (`AS-06`)
- [x] Failure treated as developmental, with the statutory exception stated precisely (`AS-07`)
- [x] Lapse handling with no grace period, and lapse framed as a management failure first
- [x] Brand-warranty override declared absolute and non-waivable (`AS-12`)
- [x] Evidence assembled continuously, including failures, with assessor qualification recorded
- [x] Integrity risks and appeal route specified, with instrument review on upheld appeal
- [x] All internal links resolve
- [x] `BRU-SRM-09`, `BRU-HRM-01`, `BRU-LMS-01`, `BRU-LMS-02` cited to `05-05`; `FR-LMS-*` to `M22`; `KPI-062`/`-063`/`-064` to `06-02`
- [x] ISO 9001:2015 clause 7.2 cited with its four obligations, not paraphrased as "training records"
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` brand certification requirements obtained — outstanding; `BRU-SRM-09` cannot be configured**
- [ ] **`O-04` assessor population established — outstanding**
- [ ] Named approvers recorded — **pending Quality Manager and HR Director**
- [x] English-only, per `CG-010` §3.2 — framework content

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
