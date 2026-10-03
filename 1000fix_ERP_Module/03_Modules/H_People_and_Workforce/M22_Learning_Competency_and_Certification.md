---
id: FIX-ERP2-M22
module_id: M22
module_code: LMS
module_name: Learning, Competency & Certification
category: H — People & Workforce
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: HR Director
system_owner: People Squad
priority: P2
wave: W5
regulatory_verified: 2026-08-12
---

# M22 — Learning, Competency & Certification
### Category H · Code `LMS`

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M22 |
| **Module code** | `LMS` |
| **Category** | H — People & Workforce |
| **Status** | Re-scoped — narrowed to competency and learning; knowledge content moved to M61 |
| **Priority** | P2 |
| **Delivery wave** | W5 (Months 19–22) |
| **Business owner** | HR Director (process) · COO (technical competence) |
| **System owner** | People Squad |
| **Delivery layers** | L2 (OCA e-learning) + L4 (Moodle option) + L5 (competency and certification engine) |
| **Custom modules** | `cd_competency`, `cd_certification`, `cd_training_ops` |
| **Requirement range** | FR-LMS-001 … FR-LMS-040 |
| **Requirement count** | 40 |
| **Effort estimate** | 16 person-weeks |
| **Depends on** | M21 Core HR · M57 Performance · M61 Knowledge · M17 Assets · M08 Contracts |
| **Depended on by** | **M02 Dispatch (competency-based assignment)** · M55 · M57 · M58 · M59 · M23 Quality · M31 |

---

## 2. Purpose

M22 answers one question that the business currently cannot answer reliably: **is this person
qualified to do this job?**

It maintains the competency and certification record for every employee, closes gaps through
training, and — critically — makes that record enforceable at the point of work assignment.

### Why It Exists

1000FiX is an **authorised service provider for multiple brands**. Brand authorisation
frequently depends on certified technicians. A lapsed certification is not an HR
inconvenience; it can invalidate the authorisation, void a warranty claim, or breach a
service contract.

The Company is also **ISO 9001:2015 certified**. Clause 7.2 requires the organisation to
determine the necessary competence, ensure competence on the basis of education, training or
experience, take action to acquire it, and **retain documented information as evidence of
competence**. That evidence currently exists as certificates in files, if it exists at all.

The v1.0 BRD calls for technician skill and certification tracking and training management.
What it does not say — and what makes this module operationally significant — is that the
skill record must be **consumed by M02 at dispatch**. A skill matrix nobody enforces is a
document. A skill matrix the dispatcher cannot override is a control.

### Scope Change from v1.0

In v1.0 this module bundled learning management with organisational knowledge. Those are now
separate:

| | M22 Learning & Competency | M61 Knowledge Management |
|---|---|---|
| **Owns** | Who is qualified, what training they took, what certification they hold | Repair procedures, troubleshooting guides, technical documentation |
| **Audience** | HR, managers, dispatch | Technicians in the field, the AI assistant, customers |
| **Question answered** | *Can this person do it?* | *How is it done?* |

They interoperate — a knowledge article can be a training resource, and a course can teach a
procedure — but their ownership, governance and change cadence are different.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.6 (BR-HRM-013) | "Maintain technician skill matrix and certification records" |
| ERP BRD §8.6 (BR-HRM-014) | "Track training programmes, attendance and effectiveness" |
| ERP BRD BR-FSM-004 | Job assignment shall consider technician skill and certification |
| ERP BRD §5 pain point | "No structured skill and training tracking" |
| **ISO 9001:2015 clause 7.2** | Determine necessary competence · ensure competence · take action to acquire it · **retain documented information as evidence of competence** |
| **ISO 45001 clause 7.2** | Competence requirement for occupational health and safety roles *(links to M59)* |
| **Bangladesh Labour Act 2006** *(verified 2026-08-12)* | Apprenticeship provisions; obligations on training for hazardous work |
| **Brand authorisation practice** | Manufacturer-authorised service providers are commonly required to maintain certified technicians per product line |
| **PDPA 2026** *(verified 2026-08-12)* | Training and assessment records are personal data |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Competency framework — competencies, levels, role requirements |
| 2 | Skill matrix by employee, with proficiency and evidence |
| 3 | Competency assessment and verification |
| 4 | Certification register — internal, brand and statutory |
| 5 | Certification validity, expiry, renewal and re-certification |
| 6 | Training catalogue — courses, curricula, learning paths |
| 7 | Training scheduling, enrolment and attendance |
| 8 | Digital learning delivery and content assignment |
| 9 | Assessment, testing and pass criteria |
| 10 | On-the-job training and mentoring records |
| 11 | Training needs identification from performance, quality and safety signals |
| 12 | Training budget, cost and vendor management |
| 13 | Training effectiveness evaluation |
| 14 | **Competency publication to M02 for assignment eligibility** |
| 15 | Competence evidence for ISO 9001 and brand audits |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Repair procedures, troubleshooting guides, technical documentation** | **M61** | Knowledge content, not competence record |
| **Job assignment decision** | **M02** | M22 publishes eligibility; M02 decides who goes |
| **Performance measurement and rating** | **M57** | Competence is capability; performance is result |
| **Recruitment assessment and pre-hire testing** | **M58** | Pre-employment; M22 begins at onboarding |
| **Safety incident investigation** | **M59** | M22 delivers safety training; M59 owns the incident |
| **Employee master and position** | **M21** | Referenced |
| **Training expense payment** | **M52 / M20** | M22 records cost; Finance pays |
| **Customer-facing training and documentation** | **M12 / M61** | Different audience |
| Course content authoring at scale | **M61** / vendor | M22 assigns and tracks; it is not a content studio |

### 3.3 Shared Concepts

| Concept | M22's Role | Owning Module |
|---|---|---|
| Employee, position, role | References | M21 |
| Competency and certification | **Owns** | M22 |
| Assignment eligibility | **Publishes**; M02 enforces | M22 / M02 |
| Knowledge article | Consumes as a learning resource | M61 |
| Performance gap | Consumes as a training trigger | M57 |
| Quality non-conformance | Consumes as a training trigger | M23 |
| Safety training requirement | Consumes requirement; delivers training | M59 |
| Product and brand coverage | References | M17 / M08 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP SuccessFactors Learning** | Curricula, assignment profiles, certification with expiry, compliance training tracking | **Assignment profiles** — training assigned automatically by role, product and location; **certification expiry as a first-class object** | Its full content-authoring and commerce capability |
| **SAP Qualification Catalogue / Oracle HCM Talent Profile** | Competency framework with proficiency levels, job profile matching | **Competency levels tied to role requirements** with gap analysis | — |
| **Workday Learning** | Blended learning, campaigns, learning recommendations | Learning paths for role progression | Social learning and content recommendation engine |
| **Field-service practice** *(ServiceMax, IFS, Salesforce Field Service)* | **Technician skill matrix consumed directly by the scheduling engine** | **This is the central adoption** — competency governs assignment eligibility, not just reporting | — |
| **Moodle** *(L4 option)* | Full open-source LMS: courses, quizzes, SCORM, certificates | Considered as the delivery platform where digital learning volume justifies it | Adopted only if OCA e-learning proves insufficient — a second platform is a second integration |
| **OCA `hr_skills`, Odoo eLearning** | Skill tracking, course delivery | The L2 substrate | Its lack of certification expiry, assignment enforcement and ISO evidence |

**Design position.** Four deliberate differences.

First, **competency is enforced at dispatch, not reported monthly**. This is the difference
between a skill matrix and a control. M02 asks M22 whether a technician is eligible for a job
type, product line and brand; an ineligible assignment requires an explicit, logged override
by an authorised approver.

Second, **certification expiry drives action before it happens, not after**. A certification
approaching expiry generates a renewal task, and — where the certification is required for
brand authorisation — escalates. A lapsed certification suspends assignment eligibility
automatically.

Third, **training needs are generated from evidence, not from an annual survey**. A performance
gap in M57, a repeated quality non-conformance in M23, a safety incident in M59, a new product
line in M17, a new brand in M08 — each generates a training need automatically.

Fourth, **the competence evidence file is a system output, not a manual compilation**. When
an ISO auditor or a brand auditor asks for evidence of competence, it is produced from the
system, complete and current.

---

## 5. Functional Areas & Features

### 5.1 Competency Framework & Skill Matrix

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-LMS-001 | Competency catalogue | Maintain a catalogue of competencies — technical, product, brand, safety, behavioural, systems — with definitions and proficiency levels | **P1** | L5 |
| FR-LMS-002 | Role competency requirement | Define required competencies and minimum levels per role, grade and position | **P1** | L5 |
| FR-LMS-003 | **Employee skill matrix** | Maintain each employee's competencies with proficiency, evidence, assessor and date | **P0** | L5 |
| FR-LMS-004 | Product and brand coverage | Record which product lines, categories and brands each technician is qualified on | **P0** | L5 |
| FR-LMS-005 | **Gap analysis** | Compare employee competence against role requirement and produce a gap list by employee, team and branch | **P1** | L5 |
| FR-LMS-006 | Competency assessment | Assess competency through test, practical demonstration or supervisor verification, with evidence retained | **P1** | L5 |
| FR-LMS-007 | Proficiency progression | Progress proficiency levels on evidence, with re-assessment intervals where configured | P2 | L5 |
| FR-LMS-008 | Skill inventory reporting | Report competence coverage by branch, product line and brand, and identify single points of failure | **P1** | L5 |

### 5.2 Certification Management

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-LMS-009 | **Certification register** | Maintain certifications — internal, brand/manufacturer, statutory, safety — with issuer, scope, number, issue date and expiry | **P0** | L5 |
| FR-LMS-010 | Certificate evidence | Attach and retain the certificate document, with verification status | **P1** | L5 |
| FR-LMS-011 | **Expiry tracking** | Track validity and alert at configurable intervals before expiry | **P0** | L5 |
| FR-LMS-012 | **Renewal workflow** | Raise a renewal task, track it to completion, and escalate where the certification is required for authorisation or statutory compliance | **P0** | L5 |
| FR-LMS-013 | **Lapse handling** | On lapse, **automatically suspend assignment eligibility** for work requiring that certification | **P0** | L5 |
| FR-LMS-014 | Brand authorisation coverage | Report certified technician coverage against each brand's requirement and flag shortfalls | **P1** | L5 |
| FR-LMS-015 | Statutory certification | Track statutory and safety certifications with their own escalation path *(links to M59)* | **P1** | L5 |
| FR-LMS-016 | Internal certification | Issue internal certifications on completion of an internal curriculum and assessment | P2 | L5 |

### 5.3 Training Delivery

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-LMS-017 | Course catalogue | Maintain courses with objectives, competencies addressed, duration, delivery mode, prerequisites and cost | **P1** | L2 |
| FR-LMS-018 | Curriculum and learning path | Group courses into curricula and role-based learning paths with sequencing | **P1** | L2 |
| FR-LMS-019 | **Automatic assignment** | Assign training automatically by role, product line, brand, location and identified gap | **P1** | L5 |
| FR-LMS-020 | Session scheduling | Schedule classroom and practical sessions with trainer, venue, capacity and dates | **P1** | L2 |
| FR-LMS-021 | Enrolment | Enrol employees, manage waiting lists, and handle cancellation and substitution | **P1** | L2 |
| FR-LMS-022 | **Schedule coordination** | Publish training commitments to **M55** so scheduled training removes availability, and check for job conflicts | **P1** | L5 |
| FR-LMS-023 | Attendance | Record attendance and completion for scheduled sessions | **P1** | L2 |
| FR-LMS-024 | Digital learning | Deliver online content, track progress and completion, and support mobile access for technicians | **P1** | L2/L4 |
| FR-LMS-025 | **Mobile learning on the technician app** | Present assigned learning and short-form content within P02, usable in the field | **P1** | L5 |
| FR-LMS-026 | Assessment and testing | Deliver tests with pass criteria, attempt limits and result recording | **P1** | L2 |
| FR-LMS-027 | On-the-job training | Record structured OJT with a supervising technician, tasks observed and sign-off | **P1** | L5 |
| FR-LMS-028 | Mentoring | Assign mentors and record mentoring interactions for new technicians | P2 | L5 |
| FR-LMS-029 | External training | Record externally delivered training, its vendor, cost and outcome | P2 | L5 |
| FR-LMS-030 | Knowledge linkage | Link courses and competencies to the relevant M61 knowledge articles | P2 | L5 |

### 5.4 Needs, Budget & Effectiveness

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-LMS-031 | **Automatic needs identification** | Generate training needs from performance gaps (M57), quality non-conformances (M23), safety incidents (M59), new products (M17), new brands (M08) and competency gaps | **P1** | L5 |
| FR-LMS-032 | Training plan | Consolidate needs into an annual and quarterly training plan by branch and role | **P1** | L5 |
| FR-LMS-033 | Budget and cost | Maintain the training budget, record cost per course, session and employee, and track against budget | **P1** | L5 |
| FR-LMS-034 | Vendor management | Maintain training vendors and trainers with rates, evaluations and contracts | P2 | L5 |
| FR-LMS-035 | **Effectiveness evaluation** | Evaluate effectiveness by comparing the operational measure the training targeted, before and after | **P1** | L5 |
| FR-LMS-036 | Participant feedback | Collect participant feedback on content, trainer and applicability | P2 | L2 |
| FR-LMS-037 | Training history | Maintain a complete, permanent training history per employee | **P1** | L5 |
| FR-LMS-038 | **Competence evidence file** | Produce, on demand, a complete competence evidence file per employee or per role for **ISO 9001 and brand audits** | **P1** | L5 |
| FR-LMS-039 | **Eligibility service to M02** | Expose an authoritative service answering whether an employee is currently eligible for a job type, product line and brand | **P0** | L5 |
| FR-LMS-040 | Override logging | Where dispatch overrides an eligibility rule, record the override, the approver and the reason, and report it | **P0** | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Eligibility as a service** | Competency and certification status are exposed as a low-latency service consumed synchronously by M02 at assignment. Not a nightly extract |
| T-02 | **Automatic eligibility suspension** | Certification lapse suspends eligibility without human action; restoration requires a valid renewal record |
| T-03 | **Effective-dated competence** | Every competency and certification has validity dates; historical eligibility is reconstructable for any past date |
| T-04 | **Evidence retention** | Certificates, assessment results and OJT sign-offs are retained as documents in M24 for the certification lifetime plus the statutory retention period |
| T-05 | **Override audit** | Every eligibility override is recorded with approver, reason and job reference, and is reportable |
| T-06 | **Event-driven need generation** | Needs are created by subscription to M57, M23, M59, M17 and M08 events, not by periodic scanning |
| T-07 | **SCORM / xAPI support** | Where digital content is used, standard packaging is supported so content is portable between platforms |
| T-08 | **Offline mobile learning** | Assigned content is available offline on P02, with completion synchronised on reconnection |
| T-09 | **Bilingual delivery** | Course content, assessments and certificates support Bengali and English |
| T-10 | **S2 classification** | Assessment results and competency gaps are visible to the employee, manager chain and HR only |
| T-11 | **Performance envelope** | Eligibility check ≤ 300 ms · skill matrix load ≤ 2 s · evidence file generation ≤ 30 s per employee |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M22 |
|---|---|---|
| **Field technician** | Skills known informally by their supervisor | Skill profile visible; assigned learning on the app; certifications tracked and renewed before lapse |
| **Dispatcher** | Assigns from memory of who can do what | **Cannot assign an unqualified technician without a logged override** |
| **Branch manager** | Cannot see the branch's competence coverage | Sees coverage by product line and brand, and where the single points of failure are |
| **Service Head** | Discovers a certification lapsed when a claim is rejected | Alerted before expiry; escalated if brand authorisation is at risk |
| **HR Director** | Compiles training records manually for audits | Evidence file generated on demand |
| **Quality Manager** | Repeated non-conformances not linked to training | Non-conformance automatically raises a training need |
| **ISO auditor** | Finds certificates in files, incomplete | Finds a complete, current, system-produced competence record |
| **Brand principal auditor** | Certified technician count asserted, not evidenced | Coverage reported against their requirement |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **First-time fix rate** | Qualified technician assigned to the right job | Direct contributor to the **> 85%** target |
| **Rework and repeat visits** | Competence enforced at assignment | Reduces the most expensive form of failure in field service |
| **Brand authorisation protection** | Certification coverage monitored against brand requirements; lapse escalated | **Protects the authorisations the business depends on** |
| **Warranty claim rejection** | Certified technician evidence available per job | Reduces rejections on competence grounds |
| **ISO 9001 certification** | Clause 7.2 evidence produced from the system | **Protects a differentiating certification** |
| **Onboarding to productivity** | Structured learning path and OJT for new technicians | Materially shortens time to full productivity |
| **Training spend effectiveness** | Needs generated from evidence; effectiveness measured against operational outcomes | Training budget spent where it changes a measurable result |
| **Capacity planning** | Competence coverage visible by branch and product | Enables informed decisions on hiring and cross-training |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Competence stops being tribal knowledge** | Today, who can fix what lives in supervisors' heads. When they leave, it leaves |
| **The single point of failure becomes visible** | One certified technician for a major brand at a branch is a risk the business currently cannot see |
| **Career progression becomes visible to technicians** | A learning path from junior to senior to specialist is a retention mechanism as much as a training one |
| **Safety competence is provable** | ISO 45001 and Labour Act obligations on training for hazardous work are evidenced, not asserted |
| **Audits stop being fire drills** | Both ISO and brand audits are answered from the system |
| **Training is defensible** | Spend is traceable to a gap and evaluated against an outcome |

---

## 8. Lifecycle & State Model

### 8.1 Certification

```
   +---------------+
   |   REQUIRED    |  role or brand requires it; employee does not hold it
   +-------+-------+
           |
   +-------v-------+
   |  IN TRAINING  |  curriculum assigned, progress tracked
   +-------+-------+
           |
   +-------v-------+     fail --> retake (attempt limit) --> ESCALATED
   |   ASSESSED    |
   +-------+-------+
           | pass
   +-------v-------+
   |    VALID      |  eligibility granted; evidence retained
   +-------+-------+
           | expiry approaching (configurable lead time)
   +-------v-------+
   |    EXPIRING   |  renewal task raised; escalation if brand-critical
   +---+-------+---+
       |       |
 renewed|       | not renewed by expiry date
       |       |
   +---v---+ +-v-------------------+
   | VALID | |      LAPSED         |
   +-------+ | eligibility SUSPENDED|  <-- automatic, no human action
             +-+-------------------+
               | renewal completed
             +-v-----+
             | VALID |
             +-------+

   REVOKED -- withdrawn by issuer or by the Company; eligibility suspended immediately
```

### 8.2 Training Need → Outcome

```
   TRIGGER  (M57 gap · M23 non-conformance · M59 incident ·
             M17 new product · M08 new brand · role gap analysis)
        │
        ▼
   NEED IDENTIFIED ──► PLANNED ──► SCHEDULED ──► ENROLLED
                          │                          │
                     (budget check)                  ▼
                                                 ATTENDED
                                                     │
                                                     ▼
                                                 ASSESSED ──fail──► RETAKE
                                                     │ pass
                                                     ▼
                                          COMPETENCY UPDATED
                                                     │
                                                     ▼
                                        ELIGIBILITY REFRESHED (M02)
                                                     │
                                                     ▼
                                    EFFECTIVENESS EVALUATED
                                    (target measure, before vs after)
```

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-LMS-01 | **A technician may not be assigned work requiring a competency or certification they do not currently hold, except by logged override** | **H** | COO |
| BRU-LMS-02 | **An eligibility override requires an authorised approver and a recorded reason** | **H** | COO |
| BRU-LMS-03 | **A lapsed certification suspends eligibility automatically** | **H** | COO |
| BRU-LMS-04 | A certification cannot be recorded as valid without evidence attached | **H** | HR Director |
| BRU-LMS-05 | **Certification expiry alerts are raised at the configured lead time; brand-critical certifications escalate to the Service Head** | **H** | Service Head |
| BRU-LMS-06 | Competency may be recorded only by an authorised assessor, never self-declared | **H** | HR Director |
| BRU-LMS-07 | A statutory or safety certification lapse is an immediate escalation *(links to M59)* | **H** | HSE Officer |
| BRU-LMS-08 | Training scheduled for an employee removes their availability in M55 | **C** | HR Director |
| BRU-LMS-09 | Assessment attempts are limited per policy; exhausting attempts escalates to the manager and HR | **H** | HR Director |
| BRU-LMS-10 | Training exceeding the budget requires approval before enrolment | **H** | CFO |
| BRU-LMS-11 | Every employee has a training history retained for the employment record period | **H** | HR Director |
| BRU-LMS-12 | Assessment results and competency gaps are S2 — employee, manager chain and HR only | **H** | CDO |
| BRU-LMS-13 | A new product line or brand generates a competency requirement and a training need before service commences | **H** | COO |
| BRU-LMS-14 | **Competence evidence must be producible on demand for ISO 9001 and brand audits** | **H** | Quality Manager |
| BRU-LMS-15 | Training effectiveness must be evaluated against the operational measure the training targeted | **A** | HR Director |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.competency` | `fix_competency` | Competency definition | code, name, type, description, levels_json, assessment_method, revalidation_interval |
| `fix.role.competency` | `fix_role_competency` | Role requirement | role_id, competency_id, minimum_level, mandatory, effective_from |
| **`fix.employee.competency`** | `fix_employee_competency` | Held competency | employee_id, competency_id, level, assessed_by, assessed_on, evidence_ref, valid_from, valid_to, state |
| `fix.competency.assessment` | `fix_competency_assessment` | Assessment record | employee_id, competency_id, method, assessor_id, result, score, evidence_ref, date |
| **`fix.certification`** | `fix_certification` | Certification definition | code, name, type, issuer, scope_json, validity_months, brand_critical, statutory |
| **`fix.employee.certification`** | `fix_employee_certification` | Held certification | employee_id, certification_id, number, issued_on, expires_on, document_ref, verified_by, state |
| `fix.certification.renewal` | `fix_certification_renewal` | Renewal task | employee_certification_id, due_date, assigned_to, state, completed_on |
| `fix.course` | `fix_course` | Course | code, name, objectives, competencies_json, duration, mode, prerequisites, cost, vendor_id, language |
| `fix.curriculum` | `fix_curriculum` | Course grouping | code, name, courses_json, sequencing, target_roles, leads_to_certification_id |
| `fix.learning.path` | `fix_learning_path` | Role progression | role_from, role_to, curricula_json, expected_duration |
| `fix.training.session` | `fix_training_session` | Scheduled delivery | course_id, trainer_id, venue, start, end, capacity, state, cost |
| `fix.enrolment` | `fix_enrolment` | Employee on a session | session_id, employee_id, state, attendance, completion, score, feedback_ref |
| `fix.assessment` | `fix_assessment` | Test | course_id, questions_ref, pass_mark, attempt_limit, duration |
| `fix.assessment.attempt` | `fix_assessment_attempt` | One attempt | assessment_id, employee_id, attempt_number, score, passed, taken_at |
| `fix.ojt.record` | `fix_ojt_record` | On-the-job training | employee_id, supervisor_id, tasks_json, observations, signed_off_by, date |
| `fix.mentoring` | `fix_mentoring` | Mentor relationship | mentee_id, mentor_id, start, end, interactions_json |
| **`fix.training.need`** | `fix_training_need` | Identified need | employee_id, competency_id, source_module, source_ref, priority, raised_on, state, resolved_by_enrolment_id |
| `fix.training.plan` | `fix_training_plan` | Consolidated plan | period, branch_id, needs_json, budget, state, approved_by |
| `fix.training.cost` | `fix_training_cost` | Cost record | session_id, employee_id, cost_type, amount, budget_line, invoice_ref |
| `fix.training.vendor` | `fix_training_vendor` | Provider | name, courses_json, rates, evaluation_score, contract_ref |
| `fix.training.effectiveness` | `fix_training_effectiveness` | Outcome evaluation | session_id, target_measure, before_value, after_value, evaluated_on, conclusion |
| **`fix.eligibility.override`** | `fix_eligibility_override` | Dispatch override | job_id, employee_id, missing_requirement, approver_id, reason, timestamp |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.employee`, `fix.position`, `fix.job.profile` | M21 / M58 | Population and requirement mapping |
| `fix.work.order`, assignment request | **M02** | **Eligibility check at assignment** |
| `fix.scorecard`, `fix.review` | M34 / M57 | Performance-derived training needs |
| `fix.nonconformance` | M23 | Quality-derived training needs |
| `fix.incident.investigation`, safety competence requirement | M59 | Safety training triggers |
| `fix.catalogue.category`, `fix.brand` | M37 | Product and brand competency scope |
| `fix.knowledge.article` | M61 | Learning resource linkage |
| `fix.availability` | M55 | Training removes availability |
| `fix.document` | M24 | Certificate and evidence retention |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-LMS-01 | **Certification expiry within the configured lead time** | **Raise a renewal task; notify the employee and manager; escalate brand-critical and statutory certifications to the Service Head and HSE Officer** | **Escalate to HR Director** |
| AUT-LMS-02 | **Certification expiry date passed without renewal** | **Suspend assignment eligibility for work requiring it; notify dispatch, the manager and the employee** | **Hard escalation — no silent failure** |
| AUT-LMS-03 | Renewal completed and evidence verified | Restore eligibility; refresh the M02 eligibility cache | Alert on failure to restore |
| AUT-LMS-04 | Employee hired or role changed (event from M21) | Assign the role curriculum and generate needs for missing mandatory competencies | Escalate to HR |
| AUT-LMS-05 | Performance gap identified (event from M57) | Create a training need linked to the gap | Log and alert |
| AUT-LMS-06 | Quality non-conformance recorded (event from M23) | Create a training need where the cause is competence-related | Log for Quality Manager review |
| AUT-LMS-07 | Safety incident or near miss (event from M59) | Create a mandatory safety training need for the affected population | **Escalate to HSE Officer** |
| AUT-LMS-08 | New product line or brand added (event from M17 / M08) | Create competency requirements and a training plan before service commences | **Block service commencement flag; alert COO** |
| AUT-LMS-09 | Training session scheduled | Publish the commitment to M55; check for job assignment conflicts | Alert the scheduler on conflict |
| AUT-LMS-10 | Session completed and assessed | Update employee competency; refresh eligibility; close the originating need | Alert on unresolved needs |
| AUT-LMS-11 | Assessment failed at the attempt limit | Escalate to the manager and HR; retain eligibility suspension where applicable | — |
| AUT-LMS-12 | 90 days after a training session | Evaluate effectiveness against the target operational measure | Flag unevaluated sessions |
| AUT-LMS-13 | Monthly | Recompute competence coverage by branch, product line and brand; flag single points of failure | Alert People Squad |
| AUT-LMS-14 | Eligibility override recorded at dispatch | Log it and include it in the weekly override report to the Operations Manager and Quality Manager | — |

---

## 12. Interfaces

### 12.1 Upstream — M22 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M21 Core HR** | Employee, position, role, joiners, movements | REST + event |
| **M57 Performance** | Competency gaps identified in review | Event |
| **M23 Quality** | Non-conformances with competence-related cause | Event |
| **M59 HSE** | Safety incidents, statutory training requirements | Event |
| **M17 Assets / M08 Contracts** | New product lines, brands, service scopes | Event |
| M61 Knowledge | Articles used as learning resources | REST |
| M55 Workforce | Availability for scheduling | REST |
| M54 FP&A | Training budget | REST |

### 12.2 Downstream — M22 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M02 Field Service** | **Assignment eligibility by employee, job type, product line and brand — synchronous** | **REST (blocking check)** |
| **M31 Workshop** | Workshop technician eligibility by product and repair class | REST |
| **M55 Workforce** | Training commitments removing availability | Command |
| M57 Performance | Competency and certification status for review | REST |
| M58 Talent | Competency requirements for job profiles; internal readiness | REST |
| M59 HSE | Safety competence and training evidence | REST |
| M23 Quality | **Competence evidence for ISO 9001 audit** | REST |
| M21 Core HR | Training history for the employee record | Event |
| M24 Documents | Certificates and evidence retention | Command |
| M25 BI | Competence coverage, training cost and effectiveness facts | Warehouse extract |
| **P02 Technician App** | Skill profile, assigned learning, certifications, expiry warnings | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `competency.granted` | employee, competency, level, valid from | **M02**, M57, M55 |
| `competency.revoked` | employee, competency, reason | **M02**, HR |
| `certification.issued` | employee, certification, expiry | M02, M23, M59 |
| **`certification.expiring`** | **employee, certification, days remaining, brand critical** | **Service Head, HSE, HR, manager** |
| **`certification.lapsed`** | **employee, certification, eligibility suspended** | **M02, M31, Service Head** |
| `training.need_raised` | employee, competency, source | HR, manager |
| `training.completed` | employee, course, result | M21, M57, M55 |
| `eligibility.changed` | employee, scope, eligible | **M02, M31** |
| `eligibility.override_logged` | job, employee, missing requirement, approver | Operations Manager, Quality |
| `coverage.shortfall` | branch, product line, brand, certified count | COO, Service Head |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| **`/api/v1/eligibility/check`** | **POST** | **Is this employee eligible for this job type, product line and brand?** | **M02, M31** |
| `/api/v1/eligibility/override` | POST | Record an override with approver and reason | M02 |
| `/api/v1/competency/{employee}` | GET | Skill matrix | P02, P03 |
| `/api/v1/competency/gaps` | GET | Gap analysis by employee, team, branch | P03 |
| `/api/v1/certifications/{employee}` | GET / POST | Certification record | P02, P03 |
| `/api/v1/certifications/expiring` | GET | Expiry pipeline | P03 |
| `/api/v1/coverage` | GET | Competence coverage by branch, product, brand | P03, P06 |
| `/api/v1/courses` / `/api/v1/sessions` | GET / POST | Catalogue and scheduling | P03 |
| `/api/v1/enrolments/{employee}` | GET / POST | Assigned and completed learning | **P02**, P03 |
| `/api/v1/training/needs` | GET / POST | Need register | P03 |
| **`/api/v1/evidence/competence/{employee}`** | **GET** | **ISO / brand audit evidence file** | **P03** |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| **Employee (self)** | R | Own skill profile, certifications, assigned learning, expiry warnings |
| R47 Team Leader | R | Team competence and training status |
| R06 Branch Manager | R U | Branch coverage, training plan input, enrolment approval |
| **R42 Training Coordinator** *(new role)* | C R U | Catalogue, scheduling, enrolment, records |
| **R43 Competency Assessor** *(new role)* | R **U** | **Record competency assessments within their assessment scope only** |
| R30 HR Manager | C R U **A** | All — framework, plan, budget, evidence |
| R05 Operations Director | R **A** | **Eligibility rules and override authority** |
| R48 Service Head | R A | Brand certification coverage and escalation |
| R32 Quality Manager / ISO Coordinator | R | Competence evidence for ISO audit; non-conformance linkage |
| R44 HSE Officer | R U | Safety competence and statutory certification |
| R03 Chief Financial Officer | R A | Training budget approval |
| R49 GRC / Internal Audit | R | Evidence, overrides, governance |

**Boundaries.** An employee cannot record their own competency — **BRU-LMS-06**. Assessors
record only within their assessment scope. Assessment results and gaps are **S2**. Eligibility
override authority sits with operations management, not dispatch staff.

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| **Certification expiry pipeline** | **HR Director, Service Head, HSE** | **Weekly** | Expiring in 90 / 60 / 30 days, brand-critical and statutory highlighted |
| **Lapsed certification register** | **Service Head, COO** | **Daily** | Lapsed certifications and suspended eligibility |
| **Competence coverage** | **COO, Service Head, branch managers** | **Monthly** | Certified technicians by branch, product line and brand against requirement |
| **Single point of failure** | **COO** | **Monthly** | Product lines or brands covered by one technician at a branch |
| **Brand authorisation compliance** | **Service Head, CEO** | **Quarterly** | Coverage against each brand's stated requirement |
| Skill gap analysis | HR Director, branch managers | Quarterly | Gaps by employee, role and branch |
| Training plan and progress | HR Director, CFO | Monthly | Planned, scheduled, delivered, outstanding against budget |
| Training cost | CFO, HR Director | Monthly | Cost by course, branch, vendor and employee against budget |
| **Training effectiveness** | **HR Director, COO** | **Quarterly** | Target measure before and after, by course |
| **Eligibility override report** | **Operations Manager, Quality Manager** | **Weekly** | Overrides by dispatcher, technician, missing requirement and reason |
| Assessment outcomes | HR Director, Training Coordinator | Monthly | Pass rates, retakes, attempt-limit escalations |
| **Competence evidence file** | **ISO auditor, brand auditor** | **On demand** | Complete per-employee or per-role competence record |
| New technician progression | HR Director, branch managers | Monthly | Learning path progress and time to full productivity |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| KPI-262 | **Employees with a complete skill matrix** | 0% | 90% | **100%** |
| KPI-263 | **Certifications lapsed before renewal** | unmeasured | < 5% | **0** |
| KPI-264 | **Brand-critical certification coverage met** | unmeasured | 100% | **100%** |
| KPI-265 | **Jobs assigned to unqualified technicians without override** | unmeasured | **0** | **0** |
| KPI-266 | Eligibility overrides per month | n/a | < 5% of assignments | **< 2%** |
| KPI-267 | Training needs closed within the plan period | unmeasured | 80% | **> 92%** |
| KPI-268 | Mandatory training completion | unmeasured | 95% | **100%** |
| KPI-269 | **Training effectiveness evaluated** | 0% | 80% | **100%** |
| KPI-270 | Training spend variance to budget | unmeasured | ± 15% | **± 8%** |
| KPI-271 | **New technician time to full productivity** | unmeasured | −20% | **−35%** |
| KPI-272 | Product lines with single-technician coverage | unmeasured | reducing | **0 at branch level** |
| KPI-273 | **Competence evidence file produced within 24 h of request** | manual, days | 100% | **100%** |
| KPI-274 | Eligibility check response time | n/a | < 500 ms | **< 300 ms** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L2 | OCA `hr_skills`, Odoo eLearning — skills, courses, enrolment, content delivery | 30% |
| L4 | **Moodle** — optional, only if digital learning volume justifies a dedicated platform | conditional |
| L5 | `cd_competency`, `cd_certification`, `cd_training_ops` | 70% |

> **On Moodle.** It is the strongest open-source LMS available and is listed as an L4 option.
> It is also a second platform, a second identity integration and a second thing to operate.
> **Recommendation: start on the Odoo substrate.** Adopt Moodle only if content volume,
> SCORM requirements or assessment sophistication demonstrably exceed what L2 supports.

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 3 of 3 identifiers below are claimed by another module: **CD-084** also claimed by M51; **CD-085** also claimed by M51; **CD-086** also claimed by M51. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID *(provisional)* | Component | Type | Effort |
|---|---|---|---|
| CD-084 | **`cd_competency`** — competency framework, role requirements, skill matrix, assessment, gap analysis, coverage | Odoo module | **6 PW** |
| CD-085 | **`cd_certification`** — certification register, expiry, renewal, lapse handling, **eligibility service and override logging** | Odoo module | **6 PW** |
| CD-086 | `cd_training_ops` — needs generation, plan, budget, vendor, effectiveness, evidence file | Odoo module | 4 PW |

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M22 is scheduled in **W5** (P2) but declares a dependency on 1 module(s) that land later: **M61** (W6). One of three things must be true before the W5 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W5 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M22 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W5 plan for M22 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| **M21 Core HR** | **Blocking** — employee, role, position |
| **Competency framework defined by the business** | **Blocking, non-technical** — the competencies and role requirements must be authored before configuration |
| **M02 assignment engine** | The eligibility interface must be built into M02's assignment path; **coordinate across waves** |
| M17 / M08 | Product line and brand structure |
| M57 Performance | Same wave — gap-driven needs |
| M23 Quality, M59 HSE | Need-generation sources; can be connected after go-live |
| M61 Knowledge (W6) | Learning-resource linkage — optional, later |

> **Cross-wave coordination required.** M02 goes live in W2; M22 in W5. The eligibility check
> must either be built into M02 at W2 as a stub returning "eligible" until M22 is live, or M02
> must be modified in W5. **The stub approach is strongly preferable** — retrofitting a
> blocking check into a live assignment path is materially riskier.

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Existing certificates (physical or scanned) | Variable | `fix.employee.certification` + M24 documents | **W5 — long lead time** |
| Informal skill knowledge (supervisor interviews) | 500+ employees | `fix.employee.competency` | **W5 — the hard one** |
| Training records if any exist | Variable | `fix.enrolment` (history) | W5 |
| Brand certification lists from principals | Per brand | `fix.employee.certification` | W5 |

> **Migration warning.** There is no existing skill matrix to migrate. The initial matrix must
> be **constructed** — through supervisor assessment of every technician against every relevant
> competency. For 500+ employees this is a substantial exercise with a long lead time, and it
> must start well before W5. It is also an opportunity: the exercise itself will reveal
> coverage gaps the business does not currently know it has.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **M02 cannot assign a technician lacking a required competency or certification without a logged override** | **Negative test through UI and API** |
| AC-02 | **A certification lapse suspends eligibility automatically, with no human action** | **Time-based test across an expiry date** |
| AC-03 | **Renewal restores eligibility and refreshes the M02 view** | End-to-end test |
| AC-04 | Expiry alerts raise at the configured lead time; brand-critical and statutory certifications escalate | Alert test across all three certification classes |
| AC-05 | Every eligibility override records approver, reason and job, and appears in the weekly report | Three override cases |
| AC-06 | **Competence coverage by branch, product line and brand is reported and identifies single points of failure** | **Report review by COO** |
| AC-07 | Training needs generate automatically from M57, M23, M59, M17 and M08 events | One triggered case per source |
| AC-08 | Scheduled training removes availability in M55 and surfaces job conflicts | End-to-end test |
| AC-09 | An employee cannot record their own competency | Negative test |
| AC-10 | **A competence evidence file is produced on demand and accepted in an ISO 9001 internal audit** | **Internal audit dry run with the Quality Manager** |
| AC-11 | Training effectiveness is evaluated against the target operational measure 90 days after delivery | Three evaluated sessions |
| AC-12 | Assessment results and competency gaps are visible only to employee, manager chain and HR | Permission test |
| AC-13 | Assigned learning is accessible on P02 offline, with completion synchronised | Field test |
| AC-14 | Eligibility check responds within 300 ms under assignment load | Load test |
| AC-15 | HR Director, COO and Quality Manager sign off UAT | Signed UAT record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Does a competency framework exist, or must it be authored from scratch?** This is the critical path input | HR Director / COO | **W5 minus 5 months** |
| Q-02 | **What certifications does each brand principal require, and how many certified technicians per brand?** Written confirmation is needed from each principal | Service Head | **W5 minus 4 months** |
| Q-03 | **Where are existing certificates held, and are they complete?** The migration exercise depends on this | HR Director | **W5 minus 4 months** |
| Q-04 | Who is authorised to assess competency, and how are assessors themselves qualified? | HR Director / COO | W5 design |
| Q-05 | **Who may override an eligibility rule at dispatch, and does it require pre-approval or post-review?** | **COO** | **W5 design** |
| Q-06 | Is Moodle required, or is the Odoo substrate sufficient? Recommendation is to start on Odoo | HR Director / IT | W5 design |
| Q-07 | What is the annual training budget, and is it currently tracked at all? | CFO / HR Director | W5 design |
| Q-08 | Are statutory or safety certifications required under the Labour Act for any role in the Company (electrical, working at height, hazardous material)? | HSE Officer / legal | **W5 minus 3 months** |
| Q-09 | Should the initial skill matrix construction start before W5 as a standalone exercise? **Recommendation: yes** | HR Director | **Immediately** |

**Q-01 and Q-09 are the critical path.** Neither is technical. The competency framework and
the initial skill matrix are business artefacts with multi-month lead times, and the module
cannot deliver value without them.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §3, §5 (boundary map), §10 (risks) ·
`M21_Core_HR_and_Employee_Lifecycle.md` · `M55_Time_Attendance_and_Workforce_Scheduling.md` ·
`M57_Performance_Incentives_and_Compensation.md` · `M59_Health_Safety_and_Wellbeing.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M02_Field_Service_and_Dispatch_Management.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M31_Workshop_and_Depot_Repair_Management.md`

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-HRM-013/014, BR-FSM-004,
§5 pain points · `1000FiX_ERP_System_Comprehensive_URD.md` Persona 3

**External benchmark and standards** *(verified 2026-08-12)*
**ISO 9001:2015 clause 7.2 (Competence)** — determine necessary competence, ensure competence,
take action to acquire it, **retain documented information as evidence of competence** ·
**ISO 45001 clause 7.2** — competence for occupational health and safety roles ·
SAP SuccessFactors Learning — assignment profiles, curricula, certification with expiry ·
SAP Qualification Catalogue / Oracle HCM Talent Profile — competency levels and job matching ·
Workday Learning — blended learning and learning paths ·
Field-service practice (ServiceMax, IFS, Salesforce Field Service) — **skill matrix consumed by
the scheduling engine** · Moodle (L4 option) · OCA `hr_skills`, Odoo eLearning ·
**Bangladesh Labour Act 2006** — apprenticeship and hazardous-work training provisions ·
**Bangladesh Personal Data Protection Act 2026** — training and assessment records as personal data

---

*Module M22 · Category H · 1000FiX ERP System v2.0 · CONFIDENTIAL*
