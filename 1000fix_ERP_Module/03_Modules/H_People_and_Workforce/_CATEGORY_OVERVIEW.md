---
id: FIX-ERP2-CAT-H
category: H
category_name: People & Workforce
module_count: 7
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT
---

# Category H — People & Workforce

**7 modules · Category owner: HR Director**

---

## 1. What Belongs in This Category

Employing, scheduling, paying, developing and protecting 500+ people — of whom 200–400 work
in the field, on customer premises, on performance-linked pay, under brand certifications
that expire.

If a capability answers *"who works here, when do they work, what are they paid, what are
they qualified to do, and are they safe"*, it belongs here.

---

## 2. Modules

| ID | Module | Status | Pri | Wave | Reqs | Effort | One-Line Definition |
|---|---|---|:--:|:--:|---:|---:|---|
| **M21** | [Core HR & Employee Lifecycle](M21_Core_HR_and_Employee_Lifecycle.md) | Re-scoped | P1 | W5 | 46 | 18 PW | The employee master: personal data, contracts, organisation structure, movements, exit, self-service |
| **M55** | [Time, Attendance & Workforce Scheduling](M55_Time_Attendance_and_Workforce_Scheduling.md) ★ | New | P1 | W5 | 52 | 22 PW | Biometric and GPS attendance, exceptions, leave, shifts, rosters and available capacity by skill and zone |
| **M56** | [Payroll, Benefits & Statutory Compliance](M56_Payroll_Benefits_and_Statutory_Compliance.md) ★ | New | **P0** | W5 | 54 | 26 PW | Gross-to-net payroll with Bangladesh tax slabs, provident fund, gratuity, BEFTN files and payslips |
| **M57** | [Performance, Incentives & Compensation](M57_Performance_Incentives_and_Compensation.md) ★ | New | P1 | W5 | 42 | 16 PW | Technician KPI capture, incentive schemes, appraisal, compensation review and pay transparency |
| **M22** | [Learning, Competency & Certification](M22_Learning_Competency_and_Certification.md) | Re-scoped | P2 | W5 | 40 | 16 PW | Competency framework, brand certification tracking with dispatch enforcement, training and assessment |
| **M58** | [Talent Acquisition & Onboarding](M58_Talent_Acquisition_and_Onboarding.md) ★ | New | P2 | W6 | 34 | 12 PW | Requisition to hire: vacancies, candidates, assessment, offer, and structured onboarding to productivity |
| **M59** | [Health, Safety & Wellbeing](M59_Health_Safety_and_Wellbeing.md) ★ | New | P2 | W6 † | 42 | 14 PW | Incidents, near-misses, risk assessment, PPE, lone-worker safety, electrical and chemical safety, wellbeing |
| | | | | **Total** | **310** | **124 PW** | **All 7 specifications written** |

★ = new in v2.1 after enterprise benchmarking. Rows are ordered by delivery sequence.

> **Requirement variance.** The category estimate before specification was 204 requirements;
> the measured total is **310 — a variance of +52%**, the largest of any category specified so
> far (A +23%, B +32%). The cause is **statutory density**: Bangladesh tax, provident fund,
> gratuity, Labour Act and PDPA obligations produce requirements that operational categories do
> not carry. The programme-level correction factor is revised in `02-02` and flagged for review.

### One Sequencing Issue Raised During Specification

**† M59's mobile reporting capability should move from W6 to W3.** FR-HSE-009 (incident, near
miss and hazard reporting from the technician app) and FR-HSE-011 (immediate serious-incident
alert) depend only on **P02** and **M21** — not on the rest of M59. They could ship alongside
the technician app in W3 at low incremental cost. A workforce able to report a hazard three
waves earlier is a materially better outcome than a complete HSE module in W6. See `M59` §16.3
and Q-05. This is a **wave-plan decision for `06-01`**, not a design question.

---

## 3. Why Payroll Is Its Own Module

Payroll is the one system in the company where an error is **immediately visible to every
employee and immediately damaging to trust**. It also carries the densest statutory logic in
the estate.

| Reason | Detail |
|---|---|
| Statutory complexity | Bangladesh income-tax slabs, investment rebate, provident fund, gratuity provision, festival bonus, BEFTN file format |
| Change cadence | Tax parameters change annually and independently of everything else in HR |
| Blast radius | A payroll defect affects 500+ people in one run |
| Segregation of duties | Processing and approval must be separable (SOD-03) |
| Benchmark | SAP *Payroll* · Oracle *Global Payroll* · Dynamics *Payroll* are all separate modules |

**Rule:** M21 owns the employee; M55 owns the hours; M57 owns the incentive; M56 turns all
three into net pay and posts it to M19.

---

## 4. Why Competency Enforcement Is a Service-Delivery Control

M22 is filed under People, but its most important consumer is **dispatch**.

> 1000FiX is an authorised service partner for 17+ brands. Every brand warranty job requires
> a currently certified technician. If a certification lapses unnoticed, the claim is
> rejected **after the work is done** — the labour and parts are spent and the revenue is
> gone.

| Control | Enforcement | Module |
|---|---|---|
| Certification register with issue and expiry dates | FR-LMS-009 | M22 |
| Alerts at the configured lead time before expiry | AUT-LMS-01 | M22 |
| Re-certification scheduled before expiry | FR-LMS-012 | M22 |
| **On expiry, assignment eligibility is suspended automatically** | **Hard block** BRU-LMS-03 · AUT-LMS-02 · FR-LMS-013 | M22 → M02 |
| Override at dispatch requires an authorised approver and a logged reason | BRU-LMS-02 · FR-LMS-040 | M22 → M02 |
| Certificate evidence retrievable for brand audit | FR-LMS-038 | M22 / M24 |
| Claims rejected for uncertified technician | KPI-265 target: **zero** | M09 |

> **Identifier note.** Requirement, rule and automation identifiers in this table are the
> module-scoped IDs adopted in the v2.1 register (`02-02` rule RG-02). The v1.0 references
> `BRU-HRM-01` and `AUT-041` are superseded.

> **Figure to verify.** The "17+ brands" figure is carried from the v1.0 BRD and is marked
> **provisional** under RG-05 until confirmed against the current principal agreement list.
> M22 Q-02 requires written confirmation from each principal of its certification requirement.

This single control is the clearest example in the programme of an HR capability protecting
revenue.

---

## 5. Category Boundary Map

| Capability | Owned By | Not Owned By |
|---|---|---|
| Employee master, contract, organisation structure | **M21** | All others reference |
| Identity and system access provisioning | **M29** triggered by **M21** events | M21 |
| Recruitment, candidates, offers | **M58** | M21 (receives the hire) |
| Attendance capture, leave, shifts, rosters | **M55** | M21, M56 (both consume) |
| Technician availability for dispatch | **M55** publishes; **M02** consumes | M02 does not maintain rosters |
| Job assignment | **M02** | M55 |
| Gross-to-net calculation, statutory deduction, BEFTN | **M56** | M21, M57 |
| Incentive scheme definition and calculation | **M57** | M56 (pays it) |
| Technician performance KPI capture | **M01**, **M02** emit; **M57** aggregates | — |
| Sales commission | **M53** (Category G) | M57 |
| Competency framework and certification | **M22** | M21 |
| Training delivery and assessment | **M22** | M61 (owns technical knowledge content) |
| **Assignment eligibility service** (is this person qualified?) | **M22** publishes; **M02** / **M31** enforce | M02 does not hold competency data |
| Safety incidents and risk assessment | **M59** | M23 (owns quality non-conformance) |
| Lone-worker check-in signal | **M02** emits; **M59** evaluates and escalates | — |
| Panic alert surface | **P02** presents; **M59** owns the capability and escalation | M02 |
| Driving licence validity | **M59** records; **M22** publishes as eligibility; **M02** enforces | — |
| PPE issue and compliance | **M59** | M17 (holds the stock) |
| **Occupational health and medical data** | **M59** — strictest access boundary in the estate | M21, M56, managers |
| Fitness-for-work restriction *(status only, never diagnosis)* | **M59** publishes; **M55** / **M02** consume | — |
| Candidate data and consent | **M58** | M21 (receives only the hired employee) |
| Statutory withholding return preparation | **M56** prepares; **M51** files | — |
| Gratuity provision | **M56** calculates; **M19** posts | — |
| Staff expense claims | **M52** (Category G) | M21 |
| Employee self-service portal | **M21** | P03 hosts it |

---

## 6. Why HSE Is Separate from Quality

Both manage "things that went wrong", and merging them is a common and costly mistake.

| | M23 Quality (Category I) | M59 Health & Safety |
|---|---|---|
| Protects | The customer and the certification | The employee and the public |
| Trigger | Defect, rework, complaint, audit finding | Injury, near-miss, hazard, unsafe act |
| Standard | ISO 9001:2015 | Bangladesh Labour Act; ISO 45001 direction |
| Reporting | Brand partners, certification body | Labour authority, insurer, board |
| Confidentiality | Low | High — medical information is S3-classified |
| Investigation | Root cause of a process failure | Root cause of harm, with legal implications |

They share the *shape* of an investigation but not its content, its confidentiality, or its
regulator. They stay separate and cross-reference.

---

## 7. Bangladesh Statutory Obligations

**Regulatory currency verified: 2026-08-12** *(DoD-17 — re-verify at each wave gate)*

| Obligation | Module | Detail *(as verified)* |
|---|---|---|
| **Income tax deduction at source** | **M56** | Slab-based, with **category thresholds**: BDT 375,000 general · **BDT 425,000** women and 65+ · **BDT 500,000** persons with disabilities and third gender · **BDT 525,000** war-wounded freedom fighters and July Warriors 2024 *(AY 2026–27)* |
| **Minimum tax** | M56 | **BDT 5,000**; BDT 1,000 for first-time registrants |
| **Investment rebate** | M56 | Reduced to **10%**, eligible investment capped at **BDT 750,000** |
| **Withholding tax return** | **M56** → M51 | **Frequency moved from monthly to quarterly** — deadlines **25 October, 25 January, 25 April, 25 July** |
| Annual tax statement and salary certificate | M56 | Per employee |
| **Provident fund** | M56 | Employer and employee contribution; **Labour Act requires formation where three-quarters of workers demand it in writing** |
| **Gratuity** | **M56** | **Wages of at least 30 days at the last-drawn rate for every completed year of service** — accrued monthly, provisioned to M19 |
| Festival bonus | M56 | Per policy and statute |
| Workers' Participation Fund / Workers' Welfare Fund | M56 | Where applicable to the Company |
| Bank salary transfer in BEFTN format | M56 | Per pay cycle · **format must be confirmed with the banking partner (DEP-07)** |
| Leave entitlement and encashment | M55 | Annual, sick, casual, maternity, paternity |
| Working-hour and overtime limits | M55 | Pre-approval required before overtime counts |
| Public holiday calendar including moon-dependent dates | M55 | Applied automatically |
| **Appointment letter and identity card at appointment** | **M58** → M21 | **Mandatory under the Labour Act**; system-generated |
| Service book | M21 | Per Labour Act |
| Probation period limits by worker class | M21 / M58 | Per Labour Act |
| **Workplace safety, health and hygiene, first aid** | **M59** | Labour Act Chapters V–VIII; Labour Rules 2015 |
| **Safety committee and safety officer** | **M59** | Constitution and frequency per Labour Rules 2015 |
| **Accident notification to the authority** | **M59** | Within the statutory period — statutory clock tracked, escalating |
| Workers' compensation | M59 → M56 | Per Labour Act schedule |
| Employee record retention | M24 | **10 years after termination**; payroll and tax records **7 years** |
| **Personal data protection (PDPA 2026)** | **All** | Employees, candidates and their health data are data subjects; **NID, TIN, biometric and health data are sensitive personal data subject to the residency restriction — see NFR-086 series** |

> **Q-01 on M56 is open and material.** Sources conflict on the final AY 2026–27 slab structure,
> specifically whether the 5% introductory slab survives. **The statutory pack must be built
> from the enacted Finance Act, not from press reporting.** All figures above are marked
> provisional under RG-05 until verified against the enacted text by the CFO or a tax advisor.

---

## 8. Category KPIs

| KPI | Baseline | Target | Owning Module |
|---|---|---|---|
| Employee record completeness | manual files | > 98% | M21 |
| Employee self-service adoption | 0% | > 85% | M21 |
| Time to fill a technician vacancy | unmeasured | < 30 days | M58 |
| New technician time to productivity | unmeasured | < 21 days | M58 |
| Attendance capture completeness | sign-in books | > 99% | M55 |
| Leave balance disputes | frequent | < 5 per year | M55 |
| Roster published before the week starts | ad hoc | 100% | M55 |
| Payroll processing time | 3 days | < 4 hours | M56 |
| Payroll corrections per run | unmeasured | < 0.3% | M56 |
| Statutory filings on time | manual | 100% | M56 |
| Technician incentive disputes | n/a | < 2% of calculations | M57 |
| Technicians who can see their own live scorecard | 0% | 100% | M57 |
| Certifications lapsed before renewal | unknown | **Zero** *(KPI-263)* | M22 |
| Claims rejected for uncertified technician | unknown | **Zero** | M22 / M09 |
| Jobs assigned to unqualified technicians without override | unmeasured | **Zero** *(KPI-265)* | M22 |
| Mandatory training completion on time | unmeasured | 100% *(KPI-268)* | M22 |
| Competence evidence file produced within 24 h | manual, days | 100% *(KPI-273)* | M22 |
| Day-one readiness complete for new joiners | unmeasured | 100% *(KPI-277)* | M58 |
| Early attrition within 90 days | unmeasured | < 8% *(KPI-280)* | M58 |
| Candidate records erased on schedule *(PDPA)* | 0% | 100% *(KPI-285)* | M58 |
| Lost-time injury frequency rate | untracked | Baselined, then reducing *(KPI-288)* | M59 |
| Near-miss reports per employee per month | 0 | **> 0.6** (higher is healthier) *(KPI-290)* | M59 |
| Statutory accident notifications within deadline | unmeasured | 100% *(KPI-291)* | M59 |
| Overdue check-outs detected and escalated | 0% | 100% *(KPI-295)* | M59 |
| Safety induction before first field or workshop work | unmeasured | 100% *(KPI-298)* | M59 |

> **KPI identifier range for Category H: KPI-212 … KPI-305.** Individual module targets and
> wave phasing are in each module's §15. Where this table and a module file differ, the module
> file governs.
>
> **One reconciliation applied.** The v1.0 overview target *"new technician time to
> productivity < 21 days"* was an absolute figure with no baseline behind it. It is restated in
> M58 (KPI-279) and M22 (KPI-271) as a **relative reduction of 35%** against a baseline to be
> measured, because no current measurement exists to make an absolute target meaningful.

---

## 9. Category Delivery Sequence

```
W5   M21 Core HR ────────┐
     M55 Time & Scheduling┤
     M56 Payroll ─────────┤   all four must land together —
     M57 Performance ─────┤   payroll cannot run without attendance,
     M22 Competency ──────┘   and dispatch cannot gate without competency
W6   M58 Talent Acquisition ──┐
     M59 Health & Safety ─────┴──► growth and duty of care
```

Wave 5 is the largest single-wave people change in the programme: 500+ employees move from
sign-in books and Excel payroll to a system, in one wave, across 51+ branches.

---

## 10. Category Risks

| Risk | Impact | Mitigation | Owning Module |
|---|---|---|---|
| A payroll error in the first live run | **Critical** — trust in the entire programme collapses | Two full parallel pay cycles before cutover; zero-tolerance gate criterion | M56 |
| Attendance data incomplete, so payroll is wrong | High | Biometric plus GPS fallback; exception regularisation workflow; 99% completeness gate | M55 |
| Technicians distrust incentive calculation | High — the productivity benefit does not materialise | Full transparency: technician sees the same calculation the system used, live, in the app | M57 |
| Certification data migrated incompletely | High — silent dispatch blocks or silent claim rejections | Certificate-by-certificate verification against brand records before Wave 5 gate | M22 |
| Safety incidents under-reported | Medium — hidden risk | Near-miss reporting is measured as a *positive* KPI, never punished | M59 |
| Personal and medical data insufficiently protected | High — legal | Payroll and health data classified S3: encrypted, access-logged, step-up authentication | M29 |
| Managers resist workforce visibility | Medium | Position scheduling and scorecards as management tools, co-designed with branch managers | M55 / M57 |

### Risks Surfaced During Specification

| Risk | Impact | Mitigation | Owning Module |
|---|---|---|---|
| **Year-to-date payroll balances wrong at cutover** | **Critical** — every subsequent calculation compounds the error and every year-end tax certificate is wrong | Cut over at the **start of an assessment year** if possible; otherwise reconcile employee by employee with HR Director and CFO sign-off *(AC-14)* | **M56** |
| **The statutory tax pack is built from press reporting rather than the enacted Finance Act** | **Critical** — systematically wrong tax for every employee | Pack authored from the enacted text; tax advisor validation before go-live *(M56 Q-01, Q-10)* | **M56** |
| **The gratuity liability is currently unrecorded in the accounts** | High — a material unrecorded balance-sheet obligation across 500+ staff | Quantify before W5; monthly accrual and provision to M19 thereafter *(M56 Q-05)* | M56 / M19 |
| **The incentive scheme is not designed** | **High — blocking** | Scheme design is a **business decision with a four-month lead time** requiring COO, HR Director and CFO agreement; nothing can be built until settled *(M57 Q-01)* | **M57** |
| **No skill matrix exists to migrate** | High — M22 cannot enforce eligibility without one | The initial matrix must be **constructed** through supervisor assessment of 500+ employees; **start before W5 as a standalone exercise** *(M22 Q-09)* | **M22** |
| **The eligibility check must be built into M02 at W2, three waves before M22 lands** | High — retrofitting a blocking check into a live assignment path is materially riskier | Build the interface as a stub returning "eligible" in W2; connect it in W5 *(M22 §16.3)* | M22 / M02 |
| **No HSE Officer is appointed and no safety committee is constituted** | High — the module has no operational owner, and the Labour Rules require both | Appoint before W6 design; this is a Labour Rules obligation independent of the ERP *(M59 Q-01)* | **M59** |
| **No hazard register, risk assessments or JSAs exist to migrate** | High — they must be authored, a multi-month HSE exercise | Begin authoring once the HSE Officer is in post, well before W6 *(M59 Q-02)* | M59 |
| **Mobile hazard reporting is three waves later than it needs to be** | Medium — the highest-value HSE capability sits behind an unnecessary dependency | Move FR-HSE-009 and FR-HSE-011 to W3 with P02 *(M59 Q-05, wave-plan decision for `06-01`)* | M59 |
| **Candidate data retained without a lawful basis** | Medium — PDPA 2026 exposure imported into the new system | Retention policy set before W6; **historical applications are not migrated**; automatic erasure at expiry *(M58 Q-05, BRU-TAO-14)* | **M58** |
| **Health and medical data reachable by HR generalists or managers** | High — PDPA sensitive-data breach | Dedicated access boundary: only Occupational Health sees diagnosis; everyone else sees fitness status and restrictions *(BRU-HSE-14/15, AC-11)* | M59 |
| **Biometric device procurement not started** | High — blocks M55, which blocks M56 and M02 | ASM-11; procurement lead time must be confirmed against the W5 gate | M55 |
| **The Bangladesh-resident store does not yet exist** | **Critical** — blocks M21, M55, M56, M58 and M59, all of which hold sensitive personal data | **DEP-31 / decision D-13** — the most urgent open decision in the programme | Cross-cutting |

---

*Category H · 1000FiX ERP System v2.0*
