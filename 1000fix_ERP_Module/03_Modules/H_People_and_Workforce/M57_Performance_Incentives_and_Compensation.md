---
id: FIX-ERP2-M57
module_id: M57
module_code: PIC
module_name: Performance, Incentives & Compensation
category: H — People & Workforce
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: HR Director
system_owner: People Squad
priority: P1
wave: W5
regulatory_verified: 2026-08-12
---

# M57 — Performance, Incentives & Compensation
### Category H · Code `PIC` · ★ New module in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M57 |
| **Module code** | `PIC` |
| **Category** | H — People & Workforce |
| **Status** | ★ **New** — the v1.0 plan had no performance module at all |
| **Priority** | **P1** |
| **Delivery wave** | W5 (Months 19–22) |
| **Business owner** | HR Director (process) · COO (service KPIs) · CFO (incentive cost) |
| **System owner** | People Squad |
| **Delivery layers** | L2 (OCA appraisal) + L5 (custom KPI and incentive engine) |
| **Custom modules** | `cd_performance`, `cd_incentive_engine`, `cd_compensation` |
| **Requirement range** | FR-PIC-001 … FR-PIC-042 |
| **Requirement count** | 42 |
| **Effort estimate** | 16 person-weeks |
| **Depends on** | M21 Core HR · M55 Workforce · **M25 BI (KPI facts)** · M01/M02/M31 (job outcomes) · M34 (CSAT) |
| **Depended on by** | **M56 Payroll** · M21 · M22 Learning · M58 Talent · M54 FP&A |

---

## 2. Purpose

M57 measures how well people perform, and converts that measurement into money and development.

It is the module that makes the productivity target of the whole programme achievable. Every
other module can make it *possible* for a technician to complete 8–9 jobs a day instead of 4–5.
Only M57 makes it *worth their while*, and only if the measurement is one they trust.

### Why It Exists

The v1.0 BRD identifies "no performance-linked incentive calculation" as a gap and specifies
technician performance tracking against KPIs. The v1.0 plan then folded this into a general HR
module, where it would have been implemented as an annual appraisal form.

That is the wrong shape for this business. In a field-service operation the meaningful
performance signal is **operational and continuous** — jobs completed, first-time fix rate,
SLA compliance, customer satisfaction, rework, parts accuracy — not an annual conversation.

### The Design Problem This Module Must Solve

An incentive scheme fails in one of two ways, and both are fatal:

| Failure | What Happens |
|---|---|
| **Not trusted** | The technician cannot reproduce the calculation, believes it is arbitrary, and stops responding to it. The incentive becomes a cost with no behavioural return |
| **Gamed** | The measure is optimised at the expense of the outcome — jobs closed without a real fix, easy jobs cherry-picked, quality sacrificed for volume |

The design response to both is the same: **the incentive is calculated from operational
evidence that the employee can see, and it is balanced so that no single measure can be
optimised alone**.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.6 (BR-HRM-008) | "Track technician performance against KPIs: jobs completed, first-time fix rate, customer rating, SLA compliance" |
| ERP BRD §8.6 (BR-HRM-012) | "Calculate performance-based incentives per approved scheme" |
| ERP BRD §5 pain point | "No performance-linked incentive calculation" |
| ERP BRD KPI targets | Technician productivity 4–5 → 8–9 jobs/day; first-time fix > 85%; CSAT 3.8 → 4.7 |
| ERP URD Persona 3 (Technician) | Wants to see own performance and earned incentive |
| **Bangladesh Labour Act 2006** *(verified 2026-08-12)* | Performance-based termination requires documented process; incentive forms part of wages for certain statutory calculations |
| **PDPA 2026** *(verified 2026-08-12)* | Performance data is personal data; automated evaluation affecting employment carries transparency obligations |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Goal and objective setting, cascaded from company to individual |
| 2 | Operational KPI definition, measurement and attribution to individuals and teams |
| 3 | Continuous performance dashboards for employee and manager |
| 4 | Performance review cycles — probation, periodic, annual |
| 5 | Multi-source feedback (manager, peer, customer, self) |
| 6 | Performance rating and calibration |
| 7 | Performance improvement plans |
| 8 | Incentive scheme design, versioning and approval |
| 9 | Incentive calculation, adjustment, approval and publication to payroll |
| 10 | Recognition and non-monetary reward |
| 11 | Compensation review and salary revision proposals |
| 12 | Compensation banding and internal equity analysis |
| 13 | Succession and readiness identification |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Incentive payment, taxation and disbursement** | **M56** | M57 calculates the amount; M56 pays it |
| **Salary structure of record and contract amendment** | **M21** | M57 proposes a revision; M21 records the approved change |
| **Hours, attendance and overtime** | **M55** | An input, not a performance measure in itself |
| **Job execution, SLA measurement, first-time fix determination** | **M01 / M02 / M31** | The operational systems own the fact; M57 attributes it to a person |
| **Customer satisfaction survey and score** | **M34** | M34 owns CSAT; M57 attributes the score to the technician |
| **Sales commission on revenue** | **M53** | Different mechanism, different governance |
| **Training delivery and competency assessment** | **M22** | M57 identifies the gap; M22 closes it |
| **Recruitment and internal hiring** | **M58** | M57 identifies readiness; M58 runs the process |
| Loyalty points and customer rewards | **M10** | Customer-facing, not employee |
| KPI warehouse, fact storage, BI platform | **M25** | M57 defines the employee KPI; M25 stores and serves the facts |

### 3.3 Shared Concepts

| Concept | M57's Role | Owning Module |
|---|---|---|
| Employee, position, manager | References | M21 |
| Job outcome facts | Consumes | M01 / M02 / M31 |
| CSAT score | Consumes and attributes | M34 |
| KPI fact store | Consumes | M25 |
| Incentive amount | **Owns the calculation** | M57 |
| Incentive payment | Hands off | M56 |
| Salary revision | **Proposes**; M21 records | M57 / M21 |
| Competency gap | **Identifies**; M22 closes | M57 / M22 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP SuccessFactors Performance & Goals** | Cascaded goal management, continuous performance, calibration sessions, 360 feedback | **Goal cascade** and **calibration** — a rating that is not calibrated across managers is not comparable | The heavyweight annual form-driven cycle as the primary mechanism |
| **SAP SuccessFactors Compensation** | Compensation planning worksheets, budget guardrails, internal equity views | **Budget-constrained compensation planning** with equity analysis | Full long-term-incentive and equity modelling — not applicable |
| **Oracle HCM Compensation & Workforce Rewards** | Rule-based variable compensation plans with eligibility and proration | **Plan versioning with eligibility rules and proration** | — |
| **Workday Talent** | Continuous feedback, talent pools, succession readiness | Continuous feedback; lightweight succession readiness | Full talent-review ceremony framework |
| **Field-service performance practice** *(ServiceMax, Salesforce Field Service, IFS)* | Technician scorecards on first-time fix, SLA, utilisation, CSAT | **The field-service scorecard as the primary performance artefact** for technicians | Vendor-specific metric definitions |
| **OCA `hr_appraisal`** | Basic appraisal cycle | The L2 substrate for review cycles | Its lack of any KPI or incentive capability |

**Design position.** Five deliberate differences.

First, **the scorecard is the performance system, not the appraisal form**. For a technician,
performance is visible daily in M02 and M31 data. The annual review confirms what the scorecard
already showed; it does not discover it.

Second, **the incentive calculation is reproducible by the person it pays**. Every technician
can open their app, see each job that counted, see each KPI value, see the scheme rule that
applied, and arrive at the same number the system did. An incentive that cannot be reproduced
by its recipient will not change behaviour.

Third, **schemes are versioned and effective-dated, and a period always calculates on the
version that applied then**. Retrospective scheme changes are how incentive programmes lose
trust permanently.

Fourth, **balanced scorecards, never a single measure**. A technician incentive weighted only
on job volume produces closed jobs that were not fixed. Volume is always paired with
first-time fix, CSAT and rework. A quality gate can reduce the volume component to zero.

Fifth, **the incentive is calculated from operational truth, not from self-reported data**.
Jobs come from M02 and M31, first-time fix from the job record, CSAT from M34, rework from the
warranty and return path. No employee reports their own performance input.

---

## 5. Functional Areas & Features

### 5.1 Goals & Objectives

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PIC-001 | Goal library | Maintain a library of goal templates by role, with measure, target and weight | P1 | L5 |
| FR-PIC-002 | Goal cascade | Cascade goals from company to department to team to individual, preserving the linkage | P1 | L5 |
| FR-PIC-003 | Individual goal setting | Set individual goals with target, weight, measurement basis and period, agreed between employee and manager | **P1** | L2 |
| FR-PIC-004 | Goal progress | Track goal progress from operational data where the measure is system-derived, and from manual update where it is not | P1 | L5 |
| FR-PIC-005 | Mid-period revision | Revise goals mid-period under approval, retaining the original for audit | P2 | L5 |

### 5.2 Operational KPIs & Scorecards

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PIC-006 | **KPI definition** | Define employee KPIs with formula, source module, unit, direction, target and threshold, as **versioned configuration** | **P0** | L5 |
| FR-PIC-007 | **KPI attribution** | Attribute each operational fact to the responsible individual and team, with defined rules for shared and reassigned jobs | **P0** | L5 |
| FR-PIC-008 | Technician scorecard | Compute the field technician scorecard: jobs completed, first-time fix rate, SLA compliance, CSAT, rework rate, parts accuracy, utilisation, travel efficiency | **P0** | L5 |
| FR-PIC-009 | Workshop scorecard | Compute the workshop technician scorecard: throughput, turnaround time, first-time fix, rework, quality-check pass rate | **P1** | L5 |
| FR-PIC-010 | Branch and front-desk scorecard | Compute front-desk and branch scorecards: intake accuracy, queue time, customer satisfaction, collection accuracy | P1 | L5 |
| FR-PIC-011 | Contact centre scorecard | Compute agent scorecards: handled volume, first-contact resolution, CSAT, quality score | P1 | L5 |
| FR-PIC-012 | **Employee-visible scorecard** | Present each employee their own scorecard with **the underlying jobs and events that produced each value** | **P0** | L5 |
| FR-PIC-013 | Manager team view | Present managers their team's scorecards with distribution, outliers and trend | **P1** | L5 |
| FR-PIC-014 | KPI dispute | Allow an employee to dispute a KPI value with evidence, route it for review, and correct with an audit trail | **P1** | L5 |
| FR-PIC-015 | Peer and benchmark comparison | Compare against team, branch and company distribution, anonymised | P2 | L5 |

### 5.3 Review Cycles & Feedback

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PIC-016 | Review cycle configuration | Configure review cycles — probation, quarterly, half-yearly, annual — by population, with stages and deadlines | **P1** | L2 |
| FR-PIC-017 | **Probation review** | Run the probation review before the confirmation date and drive the M21 confirmation decision | **P1** | L5 |
| FR-PIC-018 | Self-assessment | Capture employee self-assessment against goals and competencies | P1 | L2 |
| FR-PIC-019 | Manager assessment | Capture manager assessment, incorporating scorecard evidence automatically | **P1** | L2 |
| FR-PIC-020 | Multi-source feedback | Collect peer, subordinate, cross-functional and customer feedback where configured | P2 | L5 |
| FR-PIC-021 | **Rating and calibration** | Produce a rating and support a calibration session where managers compare ratings across teams before finalisation | **P1** | L5 |
| FR-PIC-022 | Review meeting record | Record the review discussion, agreed actions and employee acknowledgement | **P1** | L2 |
| FR-PIC-023 | **Performance improvement plan** | Create a PIP with objectives, support, review points and outcome, and track it to conclusion | **P1** | L5 |
| FR-PIC-024 | Continuous feedback | Capture in-the-moment feedback and recognition outside the formal cycle | P2 | L5 |
| FR-PIC-025 | Development plan linkage | Convert identified gaps into development actions and publish them to M22 | **P1** | L5 |

### 5.4 Incentive Engine

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PIC-026 | **Scheme definition** | Define incentive schemes with population, period, components, weights, thresholds, caps and payout curve, as **versioned, effective-dated configuration** | **P0** | L5 |
| FR-PIC-027 | Scheme approval | Require formal approval of a scheme and each version by HR Director and CFO before it can calculate | **P0** | L5 |
| FR-PIC-028 | Eligibility rules | Determine eligibility by employment status, tenure, attendance qualification and disciplinary standing | **P1** | L5 |
| FR-PIC-029 | **Balanced components** | Support multiple weighted components with **quality gates that can reduce or eliminate the volume component** | **P0** | L5 |
| FR-PIC-030 | **Calculation** | Calculate incentive per employee per period from operational KPI values, using the **scheme version effective for that period** | **P0** | L5 |
| FR-PIC-031 | **Calculation transparency** | Show the employee every component, value, weight, rule and contributing job that produced the amount | **P0** | L5 |
| FR-PIC-032 | Proration | Prorate for partial periods, joiners, leavers, transfers and long absence | **P1** | L5 |
| FR-PIC-033 | Adjustment | Allow a manual adjustment with reason and approval, always visible on the employee's statement | **P1** | L5 |
| FR-PIC-034 | Clawback and correction | Reverse or adjust an incentive where the underlying job is later found to be rework or fraudulent, under approval | **P1** | L5 |
| FR-PIC-035 | **Approval and publication** | Route the calculated incentive for approval and publish the approved amount to **M56** for payment | **P0** | L5 |
| FR-PIC-036 | Incentive cost analysis | Report incentive cost by scheme, branch, role and period against budget | **P1** | L5 |
| FR-PIC-037 | **Scheme simulation** | Simulate a scheme against historical data before approval, showing cost and distribution | **P1** | L5 |

### 5.5 Compensation & Succession

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PIC-038 | Compensation review cycle | Run a salary review cycle with budget, guidelines, manager proposals and approval | **P1** | L5 |
| FR-PIC-039 | Salary band and equity | Maintain salary bands by grade and analyse internal equity, compression and outliers | P2 | L5 |
| FR-PIC-040 | Revision proposal to M21 | Publish approved salary revisions to M21 as contract amendments with effective dates | **P1** | L5 |
| FR-PIC-041 | Recognition | Operate non-monetary recognition — awards, badges, published commendations | P2 | L5 |
| FR-PIC-042 | Succession readiness | Identify successors and readiness levels for critical positions, and feed internal candidates to M58 | P2 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Scheme and KPI definitions are versioned data** | A scheme change is configuration with an effective date; a period always calculates on the version that applied then |
| T-02 | **Deterministic, reproducible calculation** | Same facts, same scheme version, same result — reproducible line by line, months later |
| T-03 | **Full traceability to source facts** | Every KPI value traces to the specific job, event or survey response that produced it |
| T-04 | **Attribution rules are explicit** | Shared jobs, reassignments and escalations have defined attribution rules; no fact is silently dropped or double-counted |
| T-05 | **KPI facts read from M25** | M57 does not maintain its own copy of operational facts; it reads the warehouse and stores only the derived score |
| T-06 | **Immutability after publication** | A published incentive period is locked; change requires an approved correction with an audit trail |
| T-07 | **Segregation from payroll** | M57 publishes an amount; it has no ability to pay. Payment authority is entirely in M56 |
| T-08 | **PDPA transparency for automated evaluation** | Where a calculation materially affects pay or employment, the logic is disclosed to the employee and human review is available |
| T-09 | **S2 data classification** | Performance ratings, reviews and PIPs are restricted to employee, manager chain and HR |
| T-10 | **Anonymisation in comparison** | Peer comparison shows distribution, never another named individual's score |
| T-11 | **Performance envelope** | Scorecard refresh nightly for the full population · employee scorecard load ≤ 2 s · incentive calculation for 500+ employees ≤ 10 minutes · simulation ≤ 15 minutes |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M57 |
|---|---|---|
| **Field technician** | No visibility of performance; incentive unexplained or absent | Sees the scorecard daily, sees every job that counted, sees the incentive accumulate through the month |
| **Workshop technician** | Throughput invisible | Turnaround, rework and quality-check performance visible |
| **Team leader** | Manages by impression | Sees team distribution, identifies the outlier before it becomes a problem |
| **Branch manager** | Cannot compare technicians objectively | Compares on a common, calibrated basis |
| **HR Director** | Annual appraisal exercise disconnected from operations | Continuous evidence; the annual review confirms rather than discovers |
| **COO** | Cannot link productivity targets to individual behaviour | Scheme design directly targets first-time fix, SLA and CSAT |
| **CFO** | Incentive cost unpredictable | Scheme simulated before approval; cost tracked against budget |
| **Contact centre agent** | Quality assessed subjectively | Volume, resolution and CSAT measured consistently |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Technician productivity** | Incentive directly linked to completed, correctly-fixed jobs, made visible daily | **4–5 → 8–9 jobs/day** — the single largest operational gain in the programme |
| **First-time fix rate** | Quality gate prevents volume being earned at the expense of the fix | **> 85%** |
| **Customer satisfaction** | CSAT weighted in the technician scorecard | **3.8 → 4.7** |
| **Rework reduction** | Rework carries a direct negative weight and a clawback path | Material reduction in the cost of repeat visits |
| **Incentive administration** | Calculated automatically instead of assembled manually | Removes a recurring manual exercise and its error rate |
| **Incentive cost control** | Simulation before approval; cost tracked by scheme and branch | Prevents a scheme costing materially more than intended |
| **Attrition among high performers** | Performance recognised and paid; development gaps addressed | Retains the technicians most expensive to replace |
| **Fair, defensible people decisions** | Calibrated ratings on documented evidence | Reduces dispute risk on promotion, PIP and termination |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Effort becomes visible** | In the current system a technician who works harder is indistinguishable from one who does not. That is corrosive well beyond its cost |
| **Pay becomes explicable** | A technician can reconstruct their own incentive. This is the difference between a scheme that motivates and one that breeds suspicion |
| **Managers are held to a common standard** | Calibration exposes the lenient manager and the harsh one, and makes ratings comparable across branches |
| **Development is evidence-based** | The training plan follows from the measured gap, not from a manager's impression |
| **Difficult decisions are documented** | A PIP with objectives, support and review points is both fairer to the employee and defensible under the Labour Act |
| **The ISO 9001 competence requirement is served** | Documented evaluation of personnel performance is a standing certification obligation |

---

## 8. Lifecycle & State Model

### 8.1 Incentive Period

```
   SCHEME VERSION APPROVED (HR Director + CFO)   <-- before any calculation
        |
   +----v-----------+
   |  PERIOD OPEN   |  facts accumulate from M02, M31, M34, M25
   +----+-----------+
        |
   +----v-----------+
   | SCORECARD LIVE |  employee sees running position, job by job
   +----+-----------+
        | period ends; M55 attendance period locked
   +----v-----------+
   |   CALCULATED   |  scheme version effective for the period is applied
   +----+-----------+
        |
   +----v-----------+     dispute raised --> INVESTIGATION --> corrected or upheld
   | REVIEW WINDOW  |  employee may dispute a KPI value with evidence
   +----+-----------+
        |
   +----v-----------+
   |   APPROVED     |  manager, HR Director, CFO by threshold
   +----+-----------+
        |
   +----v-----------+
   |   PUBLISHED    |  locked; amount handed to M56
   +----+-----------+
        |
   +----v-----------+
   |     PAID       |  by M56 in the payroll run; visible on the payslip
   +----------------+

   CLAWBACK -- underlying job later found to be rework or invalid;
               approved reversal applied to a later period, never silently
```

### 8.2 Performance Review

```
   NOT STARTED ──► SELF-ASSESSMENT ──► MANAGER ASSESSMENT ──► CALIBRATION
                                                                  │
                        ┌─────────────────────────────────────────┘
                        ▼
                    FINALISED ──► DISCUSSED ──► ACKNOWLEDGED ──► CLOSED
                        │
                        └──► outcome routes to:  M22 (development)
                                                 M57 (compensation proposal)
                                                 M21 (confirmation / movement)
                                                 PIP (where below standard)
```

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-PIC-01 | **An incentive scheme cannot calculate until the version is approved by HR Director and CFO** | **H** | CFO |
| BRU-PIC-02 | **A period calculates on the scheme version effective for that period; retrospective scheme change never applies** | **H** | HR Director |
| BRU-PIC-03 | **Incentive is calculated from operational facts only; no self-reported input contributes** | **H** | COO |
| BRU-PIC-04 | **Every technician scorecard pairs a volume measure with at least one quality measure** | **H** | COO |
| BRU-PIC-05 | **A quality gate below threshold reduces or eliminates the volume component** | **H** | COO |
| BRU-PIC-06 | **The employee can see every job and event contributing to their KPI values** | **H** | HR Director |
| BRU-PIC-07 | An incentive period cannot be calculated before the M55 attendance period is locked | **H** | HR Director |
| BRU-PIC-08 | **A published incentive period is immutable; change requires an approved correction** | **H** | CFO |
| BRU-PIC-09 | **M57 publishes an amount to M56; it never initiates payment** *(SOD-30)* | **H** | CFO |
| BRU-PIC-10 | A manual adjustment requires a reason and approval, and is shown to the employee | **H** | HR Director |
| BRU-PIC-11 | A clawback requires evidence, approval, and notification to the employee before it is applied | **H** | HR Director |
| BRU-PIC-12 | A KPI dispute must be answered with evidence within the configured review window | **H** | HR Director |
| BRU-PIC-13 | **Ratings must be calibrated across managers before finalisation** | **H** | HR Director |
| BRU-PIC-14 | Performance ratings, reviews and PIPs are S2 — visible to employee, manager chain and HR only | **H** | CDO |
| BRU-PIC-15 | **A performance-based employment decision requires a documented review history and, where applicable, a completed PIP** | **H** | HR Director |
| BRU-PIC-16 | Peer comparison is anonymised; no employee sees another's individual score | **H** | CDO |
| BRU-PIC-17 | A compensation proposal exceeding the cycle budget requires CFO approval | **H** | CFO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.goal` | `fix_goal` | Goal or objective | employee_id, parent_goal_id, description, measure, target, weight, period, progress, state |
| `fix.kpi.definition` | `fix_kpi_definition` | Employee KPI | code, name, formula, source_module, unit, direction, target, threshold, version, effective_from |
| `fix.kpi.value` | `fix_kpi_value` | Measured value | kpi_definition_id, employee_id, team_id, period, value, fact_count, computed_at, source_ref |
| `fix.scorecard` | `fix_scorecard` | Composite scorecard | employee_id, role_profile, period, components_json, composite_score, rank_band |
| `fix.kpi.dispute` | `fix_kpi_dispute` | Disputed value | kpi_value_id, employee_id, raised_at, ground, evidence_ref, reviewer, outcome, corrected_value |
| `fix.review.cycle` | `fix_review_cycle` | Review cycle | name, type, population, period, stages_json, state |
| `fix.review` | `fix_review` | One employee's review | cycle_id, employee_id, manager_id, self_assessment, manager_assessment, rating, calibrated_rating, state, acknowledged_at |
| `fix.review.feedback` | `fix_review_feedback` | Multi-source input | review_id, respondent_id, relationship, responses_json, submitted_at |
| `fix.calibration.session` | `fix_calibration_session` | Rating calibration | cycle_id, scope, participants, distribution_before, distribution_after, decided_at |
| `fix.pip` | `fix_pip` | Improvement plan | employee_id, raised_by, objectives_json, support_json, review_points, start, end, outcome, state |
| **`fix.incentive.scheme`** | `fix_incentive_scheme` | Scheme definition | code, name, population_rule, period_type, components_json, caps, gates_json, version, effective_from, effective_to, approved_by_hr, approved_by_cfo |
| `fix.incentive.eligibility` | `fix_incentive_eligibility` | Eligibility per period | scheme_id, employee_id, period, eligible, reason, proration_factor |
| **`fix.incentive.calculation`** | `fix_incentive_calculation` | Calculated amount | scheme_id, scheme_version, employee_id, period, components_json, gross_amount, adjustments, final_amount, state, published_at, payroll_ref |
| `fix.incentive.component` | `fix_incentive_component` | One component line | calculation_id, kpi_definition_id, value, target, weight, achievement, amount, contributing_facts_ref |
| `fix.incentive.adjustment` | `fix_incentive_adjustment` | Manual change | calculation_id, amount, reason, approved_by, visible_to_employee |
| `fix.incentive.clawback` | `fix_incentive_clawback` | Reversal | original_calculation_id, amount, ground, evidence_ref, approved_by, applied_in_period |
| `fix.compensation.cycle` | `fix_compensation_cycle` | Salary review | name, period, budget, guidelines_json, state |
| `fix.compensation.proposal` | `fix_compensation_proposal` | Proposed revision | cycle_id, employee_id, current, proposed, percent, justification, approved_by, effective_from, m21_ref |
| `fix.salary.band` | `fix_salary_band` | Band by grade | grade, min, mid, max, currency, effective_from |
| `fix.recognition` | `fix_recognition` | Award or commendation | employee_id, type, citation, awarded_by, awarded_on, published |
| `fix.succession.plan` | `fix_succession_plan` | Readiness | position_id, candidate_employee_id, readiness, development_actions, reviewed_on |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.employee`, `fix.position`, `fix.salary.structure` | M21 | Population, manager chain, current pay |
| `fix.attendance.period`, `fix.time.valuation` | M55 | Eligibility qualification, utilisation |
| `fix.service.order`, `fix.service.order` | M01 | **Primary KPI fact source** |
| `fix.survey.response` | M34 | CSAT attribution |
| `fix.brand.claim`, `fix.rework.link` | M01 / M09 | Rework and quality signal |
| KPI fact tables | M25 | Warehouse-served facts |
| `fix.competency`, `fix.training.plan` | M22 | Development linkage |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-PIC-01 | Nightly | Refresh KPI values and scorecards for the full population from M25 facts | Alert People Squad; retain prior values with a staleness marker |
| AUT-PIC-02 | Job completed (event from M02 / M31) | Attribute the outcome to the responsible technician; update the running scorecard | Queue for reprocessing |
| AUT-PIC-03 | CSAT response received (event from M34) | Attribute the score to the technician and job | Log unattributed responses for review |
| AUT-PIC-04 | Rework or warranty claim confirmed | Apply the negative signal; flag the original incentive for possible clawback | Escalate to HR |
| AUT-PIC-05 | Period end + M55 lock confirmed | Calculate incentive for all eligible employees using the effective scheme version | **Block and escalate if the attendance period is unlocked** |
| AUT-PIC-06 | Calculation complete | Open the employee review window; notify employees through M27 | Retry notification |
| AUT-PIC-07 | Dispute raised | Route to the manager and HR with the underlying facts attached; enforce the response deadline | Escalate on breach |
| AUT-PIC-08 | Review window closed | Route the calculation for approval by threshold | Escalate on delay |
| AUT-PIC-09 | Incentive approved | Lock the period and publish the amount to **M56** | **Block payroll inclusion; alert HR Director and CFO** |
| AUT-PIC-10 | Probation end approaching (from M21) | Open the probation review 30 days before the confirmation date | Escalate to HR |
| AUT-PIC-11 | Review cycle stage deadline | Remind participants; escalate overdue reviews to the next manager level | — |
| AUT-PIC-12 | Rating below standard finalised | Prompt a PIP; block promotion and compensation increase eligibility | — |
| AUT-PIC-13 | Review finalised | Publish identified gaps to **M22** as development actions | Log and alert |
| AUT-PIC-14 | Compensation proposal approved | Publish the revision to **M21** as a contract amendment with an effective date | Escalate to HR Director |
| AUT-PIC-15 | Scheme version submitted | Run simulation against the last three periods; present cost and distribution to CFO before approval | Block approval |

---

## 12. Interfaces

### 12.1 Upstream — M57 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M01 / M02 / M31** | **Job completion, first-time fix, SLA outcome, turnaround, parts usage** | **Event → M25 → M57** |
| **M34 Customer Experience** | CSAT, NPS and complaint attribution | Event |
| **M25 Business Intelligence** | KPI fact serving layer | Warehouse query |
| **M55 Workforce** | Attendance qualification, utilisation, period lock | Event + REST |
| **M21 Core HR** | Employee, position, manager chain, probation dates, current salary | REST + event |
| M09 / M23 | Rework, warranty claims, non-conformance | Event |
| M22 Learning | Competency and certification status | REST |
| M54 FP&A | Incentive and compensation budget | REST |

### 12.2 Downstream — M57 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M56 Payroll** | **Approved incentive amount with supporting detail for the payslip** | **Command** |
| **M21 Core HR** | Approved salary revisions, confirmation recommendations, rating record | Command |
| **M22 Learning** | Identified competency gaps as development actions | Event |
| M58 Talent | Internal candidates, succession readiness | REST |
| M54 FP&A | Incentive and compensation cost by scheme, branch and role | Warehouse extract |
| M25 BI | Performance and incentive facts | Warehouse extract |
| M60 GRC | Approval trail, scheme governance evidence | Event |
| **P02 Technician App** | **Personal scorecard, contributing jobs, running incentive** | **REST** |
| P03 Admin Portal | Manager team views, review cycles, calibration, compensation planning | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `scorecard.refreshed` | employee, period, composite, components | P02, M25 |
| `kpi.disputed` | employee, KPI, ground | HR, manager |
| `incentive.calculated` | scheme, period, employee count, total | HR, CFO |
| `incentive.disputed` | employee, period, ground | HR |
| **`incentive.published`** | **employee, period, amount, components** | **M56, M54** |
| `incentive.clawback_applied` | employee, amount, ground | M56, HR |
| `review.finalised` | employee, cycle, rating | M21, M22 |
| `pip.raised` / `pip.closed` | employee, objectives, outcome | M21, HR |
| `compensation.approved` | employee, new salary, effective from | **M21**, M56, M54 |
| `succession.identified` | position, candidate, readiness | M58 |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/scorecards/{employee}` | GET | Personal scorecard with contributing facts | **P02** |
| `/api/v1/scorecards/team/{manager}` | GET | Team view | P03 |
| `/api/v1/kpi/{value_id}/facts` | GET | The jobs and events behind a KPI value | P02, P03 |
| `/api/v1/kpi/dispute` | POST | Raise a dispute | P02 |
| `/api/v1/incentive/schemes` | GET / POST | Scheme definition and versioning | P03 |
| `/api/v1/incentive/schemes/{id}/simulate` | POST | Simulation before approval | P03 |
| `/api/v1/incentive/calculations/{period}` | GET / POST | Calculate and retrieve | P03 |
| `/api/v1/incentive/calculations/{id}/publish` | POST | Publish to payroll | P03 |
| `/api/v1/incentive/{employee}/{period}` | GET | Personal incentive statement | **P02** |
| `/api/v1/reviews/{cycle}` | GET / POST | Review cycle operation | P03 |
| `/api/v1/compensation/cycles/{id}/proposals` | GET / POST | Compensation planning | P03 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| **Employee (self)** | R + dispute | **Own scorecard, own contributing facts, own incentive, own review** |
| R47 Team Leader | R U | Team scorecards, reviews, feedback |
| R06 Branch Manager | R U A | Branch scorecards, reviews, calibration participation, compensation proposals |
| R30 HR Manager | C R U **A** | All — schemes, cycles, calibration, PIP, compensation |
| R03 Chief Financial Officer | R **A** | Scheme approval, incentive approval above threshold, compensation budget |
| R05 Operations Director | R U **A** | Operational KPI definitions and scheme design for service roles; scheme design input |
| R31 HR Officer | C R U | Cycle administration; no approval authority |
| R49 GRC / Internal Audit | R | Governance evidence, approval trail |
| **R41 Payroll Officer** | R | **Published incentive amounts only** — no access to ratings or reviews |

**Boundaries.** Ratings, reviews and PIPs are **S2** — employee, manager chain and HR only.
A manager sees their own reporting line, never a peer's team. Peer comparison is anonymised.
**M57 has no payment authority**; SOD-30 separates calculation from disbursement.

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| **Technician scorecard** | **Technician, team leader** | **Daily** | Jobs, first-time fix, SLA, CSAT, rework, utilisation, running incentive |
| **Personal incentive statement** | **Employee** | **Per period** | Every component, value, weight, rule, contributing job, adjustments |
| Team performance distribution | Team leader, branch manager | Weekly | Distribution, outliers, trend |
| Branch performance comparison | Operations Manager, COO | Monthly | Branch-level scorecards, ranked and normalised |
| **Incentive cost by scheme** | **CFO, HR Director** | **Per period** | Cost by scheme, branch, role against budget |
| **Scheme simulation report** | **CFO** | **Before approval** | Projected cost and payout distribution against historical data |
| Quality gate impact | COO, HR Director | Per period | Employees whose volume component was gated, and why |
| KPI dispute register | HR Director | Monthly | Disputes raised, upheld, corrected, response time |
| Review cycle progress | HR Director, HR Officer | During cycle | Completion by stage, overdue reviews |
| **Rating distribution and calibration** | **HR Director** | **Per cycle** | Distribution by manager, before and after calibration |
| PIP register | HR Director | Monthly | Active PIPs, review points, outcomes |
| Compensation planning | HR Director, CFO | Per cycle | Proposals against budget, equity and compression analysis |
| Succession coverage | HR Director, CEO | Half-yearly | Critical positions with and without ready successors |
| Clawback register | CFO, HR Director | Monthly | Clawbacks applied, ground, value |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| KPI-248 | **Technician productivity (jobs/day)** | 4–5 | 7 | **8–9** |
| KPI-249 | **First-time fix rate** | ~70% | 80% | **> 85%** |
| KPI-250 | **Technician CSAT** | 3.8 / 5 | 4.4 | **4.7** |
| KPI-251 | Rework rate | unmeasured | < 6% | **< 3%** |
| KPI-252 | **Employees with a live scorecard** | 0% | 90% | **100%** |
| KPI-253 | **Incentive calculations disputed** | n/a | < 5% | **< 2%** |
| KPI-254 | **Disputes upheld (calculation error)** | n/a | < 1% | **0** |
| KPI-255 | Incentive published to payroll on schedule | n/a | 95% | **100%** |
| KPI-256 | Incentive cost variance to budget | unmeasured | ± 10% | **± 5%** |
| KPI-257 | Review cycle completion on time | unmeasured | 90% | **> 98%** |
| KPI-258 | Ratings calibrated before finalisation | 0% | 100% | **100%** |
| KPI-259 | **Employees who can reproduce their own incentive** *(survey)* | n/a | > 80% | **> 95%** |
| KPI-260 | Performance-based decisions with documented history | unmeasured | 100% | **100%** |
| KPI-261 | Scheme versions simulated before approval | 0% | **100%** | **100%** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L2 | OCA `hr_appraisal` — review cycles, assessment forms | 20% |
| L5 | `cd_performance`, `cd_incentive_engine`, `cd_compensation` | 80% |

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 3 of 3 identifiers below are claimed by another module: **CD-081** also claimed by M18; **CD-082** also claimed by M18; **CD-083** also claimed by M51. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID *(provisional)* | Component | Type | Effort |
|---|---|---|---|
| CD-081 | **`cd_performance`** — KPI definition, attribution, scorecards, disputes, review extension, calibration, PIP | Odoo module | **7 PW** |
| CD-082 | **`cd_incentive_engine`** — scheme versioning, eligibility, calculation, gates, simulation, adjustment, clawback, publication | Odoo module | **6 PW** |
| CD-083 | `cd_compensation` — compensation cycles, bands, equity analysis, proposals, succession | Odoo module | 3 PW |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M02 / M31 live with clean job outcome data** | **Blocking** — without reliable operational facts there is nothing to measure |
| **M34 live with CSAT capture** | **Blocking for the CSAT component** — the scheme can launch without it, but the quality balance is weaker |
| **M25 KPI facts available** | **Blocking** — M57 reads facts from the warehouse |
| **M55 Workforce** | Attendance qualification and period lock |
| **M21 Core HR** | Employee, manager chain, salary |
| **Incentive scheme designed and approved by the business** | **Blocking, non-technical** — the Company must decide what it wants to reward before it can be built |
| **M56 Payroll** | Same wave — the incentive must land somewhere |

> **The binding constraint is not technical.** M57 can only calculate what the business has
> decided to reward. Scheme design — components, weights, gates, caps — is a business decision
> requiring COO, HR Director and CFO agreement, and it must be settled before build.

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Existing incentive scheme rules (if documented) | Few | `fix.incentive.scheme` | W5 |
| Historical appraisal records | Variable | `fix.review` (reference only) | W5 optional |
| Salary bands (if defined) | Few | `fix.salary.band` | W5 |
| Historical KPI baselines | Derived from M02/M31 post-go-live | `fix.kpi.value` | **Not migrated — accumulated** |

> KPI history is not migrated. It accumulates from live operational data, which means the
> first incentive period requires either a baseline built during the M02 stabilisation window
> or a launch period run in parallel with no payment.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **A technician can open their scorecard and see every job that contributed to every KPI value** | **Technician walkthrough with reconciliation to the job list** |
| AC-02 | **A technician can reproduce their incentive amount from the statement** | **Sample of 20 technicians independently reproduce the calculation** |
| AC-03 | **A period calculates on the scheme version effective for that period, not the current one** | **Scripted test across a version change** |
| AC-04 | **A quality gate below threshold reduces or eliminates the volume component** | **Test across gate boundaries** |
| AC-05 | Incentive cannot be calculated before the M55 attendance period is locked | Negative test |
| AC-06 | **A published incentive period is immutable; change requires an approved correction** | **Negative test** |
| AC-07 | **M57 cannot initiate payment; the amount reaches the employee only through M56** | **Permission audit** |
| AC-08 | A dispute routes with underlying facts attached and is answered within the review window | Three dispute cases end to end |
| AC-09 | Scheme simulation projects cost and distribution against historical data before approval | Simulation of a live scheme against three prior periods |
| AC-10 | Ratings are calibrated across managers before finalisation | One full review cycle with calibration record |
| AC-11 | Review outcomes publish development actions to M22 and compensation proposals to M21 | End-to-end trace |
| AC-12 | Ratings, reviews and PIPs are visible only to employee, manager chain and HR | Permission test across roles |
| AC-13 | Peer comparison is anonymised | UI review |
| AC-14 | Incentive calculation for 500+ employees completes in ≤ 10 minutes | Load test |
| AC-15 | HR Director, COO and CFO sign off scheme configuration and UAT | Signed UAT record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **What is the incentive scheme?** Components, weights, thresholds, caps and gates must be decided by the business. **Nothing can be built until this is settled.** | **COO / HR Director / CFO** | **W5 minus 4 months** |
| Q-02 | Does an incentive scheme exist today, in any form, that employees currently expect? Changing an existing scheme is materially harder than introducing one | HR Director | W5 minus 4 months |
| Q-03 | What is the annual incentive budget, and what proportion of total compensation should be variable? | CFO | W5 minus 3 months |
| Q-04 | **How are shared, reassigned and escalated jobs attributed?** This is the most common source of incentive disputes | COO / Operations Manager | **W5 design** |
| Q-05 | Is the incentive period monthly or quarterly? Monthly is more motivating; quarterly is less volatile and cheaper to administer | HR Director / CFO | W5 design |
| Q-06 | Are salary bands defined, or is compensation currently set individually? | HR Director | W5 design |
| Q-07 | Will a launch period run with calculation but no payment, to validate before money moves? **Strongly recommended** | HR Director / CFO | W5 minus 2 months |
| Q-08 | Does the Company intend to link performance rating to termination decisions? If so, the PIP process must be legally reviewed under the Labour Act | HR Director / legal | W5 design |
| Q-09 | Is CSAT response volume sufficient to attribute fairly at individual level, or will low-volume technicians be unfairly affected by a small sample? | COO / M34 owner | W5 design |

**Q-01 is the critical path.** It is a business decision, not a technical one, and it has a
four-month lead time because it requires agreement between three executives and, realistically,
consultation with the workforce it will pay.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §3, §6 (performance data ownership), §10 (risks) ·
`M21_Core_HR_and_Employee_Lifecycle.md` · `M55_Time_Attendance_and_Workforce_Scheduling.md` ·
`M56_Payroll_Benefits_and_Statutory_Compliance.md` ·
`M22_Learning_Competency_and_Certification.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M02_Field_Service_and_Dispatch_Management.md` ·
`03_Modules/B_Customer_Engagement_and_Experience/M34_Customer_Experience_Feedback_and_Complaints.md`

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-HRM-008/012, §5 pain points,
KPI targets · `1000FiX_ERP_System_Comprehensive_URD.md` Persona 3 (Field Technician)

**External benchmark and regulation** *(verified 2026-08-12)*
SAP SuccessFactors Performance & Goals — goal cascade, continuous performance, calibration ·
SAP SuccessFactors Compensation — budget-constrained planning, equity analysis ·
Oracle HCM Workforce Rewards — rule-based variable compensation with eligibility and proration ·
Workday Talent — continuous feedback and succession readiness ·
Field-service performance practice (ServiceMax, Salesforce Field Service, IFS) — technician
scorecards on first-time fix, SLA, utilisation and CSAT · OCA `hr_appraisal` ·
**Bangladesh Labour Act 2006** — documented process requirement for performance-based decisions ·
**Bangladesh Personal Data Protection Act 2026** — transparency obligations where automated
evaluation materially affects employment or pay

---

*Module M57 · Category H · 1000FiX ERP System v2.0 · CONFIDENTIAL*
