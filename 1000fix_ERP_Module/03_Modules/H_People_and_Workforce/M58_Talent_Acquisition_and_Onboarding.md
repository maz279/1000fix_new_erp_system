---
id: FIX-ERP2-M58
module_id: M58
module_code: TAO
module_name: Talent Acquisition & Onboarding
category: H — People & Workforce
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: HR Director
system_owner: People Squad
priority: P2
wave: W6
regulatory_verified: 2026-08-12
---

# M58 — Talent Acquisition & Onboarding
### Category H · Code `TAO` · ★ New module in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M58 |
| **Module code** | `TAO` |
| **Category** | H — People & Workforce |
| **Status** | ★ **New** — absent from the v1.0 plan entirely |
| **Priority** | P2 |
| **Delivery wave** | W6 (Months 23–26) |
| **Business owner** | HR Director |
| **System owner** | People Squad |
| **Delivery layers** | L2 (OCA / Odoo Recruitment) + L5 (custom onboarding orchestration) |
| **Custom modules** | `cd_recruitment_bd`, `cd_onboarding` |
| **Requirement range** | FR-TAO-001 … FR-TAO-034 |
| **Requirement count** | 34 |
| **Effort estimate** | 12 person-weeks |
| **Depends on** | **M21 Core HR** · M22 Competency · M57 Succession · M54 Headcount budget · M29 Identity · M24 Documents |
| **Depended on by** | M21 · M22 · M55 · M56 · M59 |

---

## 2. Purpose

M58 covers everything from *"we need someone"* to *"they are productive"* — and hands a
complete, verified employee to M21 at the point of hire.

### Why It Exists

1000FiX is a **growing service network with a technician workforce**, which means recruitment
is not an occasional event. It is a continuous operation with a characteristic problem:
technician attrition and network expansion create a steady demand for people whose competence
must be verified before they touch a customer's device.

Two specific business pressures make this module worth building rather than continuing on
email and spreadsheets:

**The onboarding gap costs money directly.** A new technician who takes twelve weeks to reach
full productivity instead of eight costs four weeks of subsidised capacity, multiplied by every
hire. Structured onboarding with a defined learning path (M22) and a defined competence gate
compresses that.

**Nothing currently connects hiring to headcount control.** A requisition raised without an
approved position and budget is how headcount drifts. The approval chain must sit in the system
that also holds the position and the budget.

### The Design Position That Matters

**M58 hands over a complete employee, not a name.** By the time M21 creates the employee record,
identity documents are verified, the appointment letter is issued, the competency baseline is
recorded, the equipment and system access are provisioned, and the onboarding plan is running.
The most common onboarding failure is the technician who arrives on day one with no ID, no
tools, no system access and no assigned mentor.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.6 | HR module scope includes employee lifecycle from hire |
| ERP BRD §5 | Manual HR processes; no structured onboarding |
| ERP URD | Branch expansion plan implies continuous technician recruitment |
| **Bangladesh Labour Act 2006** *(verified 2026-08-12)* | **Appointment letter and identity card mandatory at appointment**; service book; probation period limits by worker class; minimum age provisions |
| **Personal Data Protection Act 2026** *(verified 2026-08-12)* | Candidate data is personal data; **applicants who are not hired are data subjects with retention limits and erasure rights** |
| **ISO 9001:2015 clause 7.2** | Competence must be ensured on the basis of education, training or experience — verified at hire |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Workforce planning input and headcount requisition |
| 2 | Requisition approval against position and budget |
| 3 | Job profile and job posting |
| 4 | Sourcing — internal, external, referral, agency |
| 5 | Application capture and candidate record |
| 6 | Screening, shortlisting and pipeline management |
| 7 | Interview scheduling, panels and structured evaluation |
| 8 | Practical and technical assessment for technician roles |
| 9 | Reference and background verification |
| 10 | Offer generation, approval and acceptance |
| 11 | Pre-boarding — document collection and verification |
| 12 | **Handover to M21 at hire** |
| 13 | Onboarding orchestration across HR, IT, facilities, safety and operations |
| 14 | Structured induction and first-90-days plan |
| 15 | Recruitment analytics, cost and source effectiveness |
| 16 | Candidate data protection and retention |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Employee master record, contract, confirmation, exit** | **M21** | M58 ends at hire; M21 begins at hire |
| **Training delivery and competency assessment post-hire** | **M22** | M58 assigns the onboarding learning path; M22 delivers it |
| **Performance review, including probation review** | **M57** | Probation review is a performance process |
| **Payroll setup and first pay** | **M56** | M58 supplies the data; M56 pays |
| **Position and organisation structure definition** | **M21** | M58 requisitions against a position; it does not create one |
| **Headcount budget** | **M54** | M58 checks against it; M54 owns it |
| **User account provisioning** | **M29** | M58 raises the request; M29 provisions |
| **Asset and tool issue** | **M17 / M03** | M58 raises the request; the asset modules issue |
| **Safety induction content and statutory safety training** | **M59** | M58 sequences it; M59 owns it |
| Vendor and contractor engagement | **M40 / M41** | Not employment |
| Recruitment agency payment | **M20** | M58 records cost; Finance pays |

### 3.3 Shared Concepts

| Concept | M58's Role | Owning Module |
|---|---|---|
| Position and org structure | References | M21 |
| Headcount budget | Checks against | M54 |
| Candidate | **Owns** | M58 |
| Employee | **Creates through handover**; M21 owns thereafter | M58 → M21 |
| Competency requirement | Consumes for the job profile | M22 |
| Onboarding learning path | Assigns; M22 delivers | M58 / M22 |
| Internal candidate and succession readiness | Consumes | M57 |
| System access | Requests; M29 provisions | M58 / M29 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP SuccessFactors Recruiting & Onboarding** | Requisition approval, candidate pipeline, offer approval, **cross-functional onboarding task orchestration** | **Requisition-to-position-to-budget control** and **onboarding as orchestrated cross-team tasks, not an HR checklist** | Career-site marketing and CRM-style candidate nurturing |
| **Oracle Recruiting Cloud** | Structured hiring with job requisition templates and interview feedback capture | Structured, scored interview evaluation | — |
| **Workday Recruiting** | Internal mobility integrated with talent and succession | **Internal candidates sourced from M57 succession readiness** | — |
| **Field-service hiring practice** | Practical trade assessment before offer | **Mandatory practical assessment for technician roles** | — |
| **Odoo Recruitment (L1/L2)** | Applicant pipeline, stages, evaluation | The substrate | Its lack of approval control, verification and onboarding orchestration |

**Design position.** Four deliberate differences.

First, **a requisition cannot be raised without an approved position and available budget**.
This is the single control that separates managed headcount from drift.

Second, **technician hiring includes a practical assessment**. A CV and an interview do not
establish whether someone can repair a device. The assessment result becomes the initial
competency baseline in M22, so the assessment is not discarded after the hiring decision.

Third, **onboarding is orchestrated across functions with owners and due dates, and it is
tracked to completion**. HR, IT, facilities, safety, the branch and the mentor each hold tasks.
A technician who cannot start work on day one because a task was missed is a measured failure,
not an anecdote.

Fourth, **candidate data is retained under an explicit policy with erasure**. Under PDPA 2026
an unsuccessful applicant remains a data subject. Applications retained indefinitely "in case
something comes up" are a compliance exposure that most recruitment systems accumulate by
default.

---

## 5. Functional Areas & Features

### 5.1 Requisition & Sourcing

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TAO-001 | **Headcount requisition** | Raise a requisition against an approved position, with justification, role, grade, location and target start date | **P1** | L5 |
| FR-TAO-002 | **Budget and position check** | **Block a requisition with no approved position or no available headcount budget** | **P1** | L5 |
| FR-TAO-003 | Requisition approval | Route the requisition through an approval chain by grade and cost, with SLA and escalation | **P1** | L5 |
| FR-TAO-004 | Job profile | Maintain job profiles with responsibilities, required competencies *(from M22)*, qualifications and experience | **P1** | L5 |
| FR-TAO-005 | Job posting | Publish approved openings internally and to external channels | **P1** | L2 |
| FR-TAO-006 | **Internal sourcing** | Present internal candidates from M57 succession readiness and employee applications, and require internal consideration before external posting where policy requires | **P1** | L5 |
| FR-TAO-007 | Employee referral | Capture referrals with the referring employee, track the outcome, and trigger a referral reward where applicable | P2 | L5 |
| FR-TAO-008 | Agency and channel management | Manage recruitment agencies and sourcing channels with cost and performance | P2 | L5 |
| FR-TAO-009 | Talent pool | Maintain a pool of previously assessed candidates, **within the retention policy** | P2 | L5 |

### 5.2 Selection & Assessment

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TAO-010 | Application capture | Capture applications with CV, contact details and declared qualifications, from all sourcing channels | **P1** | L2 |
| FR-TAO-011 | Candidate record | Maintain a single candidate record, deduplicated across applications and channels | **P1** | L5 |
| FR-TAO-012 | Screening | Screen against mandatory criteria with automatic filtering and recorded rejection reasons | **P1** | L2 |
| FR-TAO-013 | Pipeline management | Move candidates through configurable stages with visibility of the pipeline per requisition | **P1** | L2 |
| FR-TAO-014 | Interview scheduling | Schedule interviews with panel members, checking availability, and notify all parties | **P1** | L5 |
| FR-TAO-015 | **Structured evaluation** | Capture structured, scored interview evaluation against defined criteria from each panel member independently | **P1** | L5 |
| FR-TAO-016 | **Practical assessment** | **Record practical and technical assessment for technician roles, with the assessor, tasks, result and evidence** | **P1** | L5 |
| FR-TAO-017 | Comparison | Compare shortlisted candidates on evaluation scores and assessment results | P2 | L5 |
| FR-TAO-018 | **Reference and background verification** | Record reference checks, previous-employment verification, NID verification and, where required, police verification, with the outcome | **P1** | L5 |
| FR-TAO-019 | Rejection and communication | Record the decision and communicate the outcome to every candidate | **P1** | L5 |

### 5.3 Offer & Pre-boarding

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TAO-020 | **Offer generation** | Generate an offer with salary, grade, benefits, probation period and start date, against the approved requisition | **P1** | L5 |
| FR-TAO-021 | **Offer approval** | Route the offer for approval by grade and salary band, blocking offers outside the band without CFO approval | **P1** | L5 |
| FR-TAO-022 | Offer communication and acceptance | Issue the offer, track its status, and record acceptance, decline or lapse | **P1** | L5 |
| FR-TAO-023 | **Document collection** | Collect required pre-joining documents — NID, academic certificates, experience letters, photographs, bank details — with a completeness check | **P1** | L5 |
| FR-TAO-024 | Document verification | Verify submitted documents and record the verifier and outcome | **P1** | L5 |
| FR-TAO-025 | **Appointment letter** | Generate the appointment letter meeting **Labour Act** requirements, with the correct terms, and record its issue | **P1** | L5 |
| FR-TAO-026 | **Handover to M21** | **On joining, create the employee in M21 with verified identity, contract terms, documents and the competency baseline** | **P1** | L5 |

### 5.4 Onboarding

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TAO-027 | **Onboarding orchestration** | Generate the onboarding task set by role, with owners, due dates and dependencies, across HR, IT, facilities, safety, branch and mentor | **P1** | L5 |
| FR-TAO-028 | **Provisioning requests** | Raise requests to **M29** for system access, **M17/M03** for tools, equipment and van stock, and facilities for workspace and ID card | **P1** | L5 |
| FR-TAO-029 | Induction programme | Schedule induction — company, policy, safety *(M59)*, systems, brand and product | **P1** | L5 |
| FR-TAO-030 | **Learning path assignment** | Assign the role onboarding learning path in **M22** and track completion | **P1** | L5 |
| FR-TAO-031 | Mentor assignment | Assign a mentor or buddy and record structured check-ins | P2 | L5 |
| FR-TAO-032 | **First-90-days plan** | Define and track a first-90-days plan with milestones, competence gates and check-in points, feeding the M57 probation review | **P1** | L5 |
| FR-TAO-033 | **Day-one readiness gate** | Report and enforce day-one readiness — access, equipment, ID, safety induction — and escalate incomplete items **before** the start date | **P1** | L5 |
| FR-TAO-034 | Recruitment analytics | Report time to hire, cost per hire, source effectiveness, offer acceptance, funnel conversion and early attrition | **P1** | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Requisition gated on position and budget** | Enforced at the service layer against M21 position data and M54 budget |
| T-02 | **Clean handover to M21** | The employee record is created from verified candidate data in a single transaction; no re-keying, no partial state |
| T-03 | **Candidate data retention and erasure** | Candidate records are retained under an explicit, configurable policy with automatic anonymisation or deletion at expiry, and an erasure path on request *(PDPA 2026)* |
| T-04 | **Sensitive candidate data residency** | NID and other sensitive identifiers reside in the **Bangladesh-resident store**, both for candidates and for employees |
| T-05 | **Consent for candidate processing** | Consent to processing and retention is captured at application and is auditable |
| T-06 | **Independent evaluation capture** | Panel members' evaluations are captured independently and are not visible to each other before submission |
| T-07 | **Onboarding tasks as first-class objects** | Tasks have owners, due dates, dependencies and states, and are visible to the hiring manager — not an HR-only checklist |
| T-08 | **Document integrity** | Verified documents are stored in M24 with hash, verifier and timestamp |
| T-09 | **S3 classification for candidate identity** | NID, academic certificates and bank details carry the same protection as employee data |
| T-10 | **Performance envelope** | Pipeline view ≤ 2 s · onboarding task generation ≤ 5 s · analytics refresh nightly |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M58 |
|---|---|---|
| **Branch manager** | Requests a technician by email, then chases | Raises a requisition, sees its approval status and pipeline position |
| **HR Officer** | Tracks candidates across email and spreadsheets | Single pipeline, structured evaluations, automated communication |
| **HR Director** | Cannot report time to hire or cost per hire | Full recruitment analytics with source effectiveness |
| **CFO** | Headcount grows without a control point | Requisitions blocked without position and budget |
| **New technician** | Arrives with no access, no tools, no plan | Arrives with access provisioned, tools issued, mentor assigned, learning path running |
| **IT administrator** | Learns of a new joiner on their first day | Receives a provisioning task with a due date before the start date |
| **Service Head** | Competence of new hires unknown until they fail a job | Practical assessment result carried into the M22 competency baseline |
| **Unsuccessful candidate** | Never hears back; data retained indefinitely | Receives an outcome; data retained under policy and erasable |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Time to hire** | Structured pipeline, scheduled interviews, approval SLAs | Materially shorter; measurable for the first time |
| **Time to full productivity** | Structured onboarding, learning path, mentor, competence gates | **Compresses the new-technician ramp, the largest hidden cost of attrition** |
| **Day-one readiness** | Orchestrated provisioning with escalation before the start date | **Eliminates lost first days** |
| **Headcount control** | Requisition blocked without position and budget | Prevents unbudgeted headcount growth |
| **Cost per hire** | Source and agency effectiveness measured | Spend shifted to channels that actually deliver |
| **Early attrition** | Better selection, structured onboarding, mentoring | Reduces the most expensive attrition — the hire who leaves within 90 days |
| **Competence at hire** | Practical assessment recorded and carried into M22 | Reduces first-time-fix failures from under-qualified new hires |
| **Referral hiring** | Referral tracking with reward | Referred hires typically arrive faster and stay longer |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **The first impression of the Company is competent** | An organisation that cannot get someone a desk and a login on day one signals something about how it operates |
| **Hiring decisions become defensible** | Structured evaluation and recorded assessment protect against both bias and challenge |
| **Labour Act obligations are met at appointment** | Appointment letter and ID card are generated as part of the process, not remembered afterwards |
| **Candidate data stops accumulating silently** | Retention policy and erasure address a PDPA exposure that most organisations never notice |
| **Internal mobility becomes real** | Internal candidates from M57 succession are considered before external posting |
| **Recruitment becomes measurable** | Time to hire, cost per hire and source effectiveness cannot currently be stated at all |

---

## 8. Lifecycle & State Model

### 8.1 Requisition to Hire

```
   NEED IDENTIFIED
        │
   +----v-----------+
   |  REQUISITION   |  position check + headcount budget check   <-- HARD GATE
   |    RAISED      |
   +----+-----------+
        | approved (chain by grade and cost)
   +----v-----------+
   |     OPEN       |  internal consideration --> external posting
   +----+-----------+
        │
   ┌────▼─────────────────────────────────────────────┐
   │  CANDIDATE PIPELINE                              │
   │  APPLIED → SCREENED → SHORTLISTED → INTERVIEWED  │
   │      → ASSESSED (practical, technician roles)    │
   │      → VERIFIED (reference, background, NID)     │
   └────┬─────────────────────────────────────────────┘
        │ selected
   +----v-----------+
   |     OFFER      |  salary band check; out-of-band needs CFO
   |    APPROVED    |
   +----+-----------+
        | issued
   +----v-----------+   declined / lapsed --> pipeline reopens
   |    ACCEPTED    |
   +----+-----------+
        │
   +----v-----------+
   |  PRE-BOARDING  |  documents collected and verified;
   |                |  appointment letter issued (Labour Act)
   +----+-----------+
        │
   +----v-----------+
   |   ONBOARDING   |  tasks orchestrated: HR, IT, facilities,
   |    RUNNING     |  safety, branch, mentor
   +----+-----------+
        │ day-one readiness gate  <-- escalates BEFORE the start date
   +----v-----------+
   |     JOINED     |  ─────► EMPLOYEE CREATED IN M21
   +----+-----------+          competency baseline → M22
        │                      payroll setup → M56
   +----v-----------+
   |  FIRST 90 DAYS |  milestones, competence gates, check-ins
   +----+-----------+
        │
        └──────────► PROBATION REVIEW (M57) ──► CONFIRMATION (M21)
```

### 8.2 Candidate Data

```
   APPLIED (consent captured)
      │
      ├── HIRED ──────► converted to employee (M21); candidate record retained as hire evidence
      │
      └── NOT HIRED ──► RETAINED (policy period, talent pool if consented)
                             │
                             ├── erasure requested ──► ERASED
                             └── retention expired ──► ANONYMISED or DELETED (automatic)
```

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-TAO-01 | **A requisition cannot be raised without an approved position and available headcount budget** | **H** | CFO |
| BRU-TAO-02 | A requisition must be approved before any posting or candidate contact | **H** | HR Director |
| BRU-TAO-03 | **An offer outside the approved salary band requires CFO approval** | **H** | CFO |
| BRU-TAO-04 | An offer cannot be issued against an unapproved or filled requisition | **H** | HR Director |
| BRU-TAO-05 | **Technician roles require a practical assessment before offer** | **H** | Service Head |
| BRU-TAO-06 | **Reference and identity verification must be complete before the appointment letter is issued** | **H** | HR Director |
| BRU-TAO-07 | Panel evaluations are submitted independently and are not visible to other panel members beforehand | **H** | HR Director |
| BRU-TAO-08 | **The appointment letter must meet Labour Act requirements and be issued at appointment** | **H** | HR Director |
| BRU-TAO-09 | **The employee record is created in M21 from verified candidate data; no manual re-keying** | **H** | HR Director |
| BRU-TAO-10 | **Day-one readiness incomplete within the configured lead time escalates before the start date** | **H** | HR Director |
| BRU-TAO-11 | Safety induction must be complete before a technician performs field or workshop work *(M59)* | **H** | HSE Officer |
| BRU-TAO-12 | The practical assessment result is recorded as the initial competency baseline in M22 | **C** | HR Director |
| BRU-TAO-13 | **Candidate consent to processing and retention is captured at application** *(PDPA)* | **H** | CDO |
| BRU-TAO-14 | **Candidate data is deleted or anonymised at the end of the retention period, automatically** *(PDPA)* | **H** | CDO |
| BRU-TAO-15 | Candidate NID and sensitive identifiers reside in the **Bangladesh-resident store** | **H** | CDO |
| BRU-TAO-16 | Every candidate who reaches interview stage receives an outcome communication | **H** | HR Director |
| BRU-TAO-17 | Minimum age and other Labour Act employment eligibility conditions are verified before offer | **H** | HR Director |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.requisition` | `fix_requisition` | Headcount request | position_id, department_id, branch_id, count, grade, justification, target_start, budget_ref, state, approvals_json |
| `fix.job.profile` | `fix_job_profile` | Role definition | role_id, responsibilities, competencies_json, qualifications, experience, salary_band_ref |
| `fix.job.posting` | `fix_job_posting` | Published opening | requisition_id, channels_json, published_on, closes_on, internal_only_until |
| **`fix.candidate`** | `fix_candidate` | Person | name, contact, nid_ref *(resident store)*, source, consent_ref, retention_until, state |
| `fix.application` | `fix_application` | Candidate on a requisition | candidate_id, requisition_id, stage, applied_on, cv_ref, screening_result, rejection_reason |
| `fix.interview` | `fix_interview` | Scheduled interview | application_id, panel_json, scheduled_at, mode, state |
| `fix.evaluation` | `fix_evaluation` | Panel member score | interview_id, evaluator_id, criteria_scores_json, recommendation, comments, submitted_at |
| **`fix.practical.assessment`** | `fix_practical_assessment` | Technical assessment | application_id, assessor_id, tasks_json, result, score, evidence_ref, date |
| `fix.verification` | `fix_verification` | Reference and background | application_id, type, referee, outcome, verified_by, date, evidence_ref |
| `fix.offer` | `fix_offer` | Employment offer | application_id, grade, salary, benefits_json, probation_months, start_date, approvals_json, state, issued_on, responded_on |
| `fix.preboarding.document` | `fix_preboarding_document` | Required document | candidate_id, document_type, submitted, verified_by, verified_on, document_ref |
| **`fix.onboarding.plan`** | `fix_onboarding_plan` | Orchestration | candidate_id, employee_id, role, start_date, tasks_json, readiness_state |
| **`fix.onboarding.task`** | `fix_onboarding_task` | One task | plan_id, function, description, owner_id, due_date, depends_on, state, completed_on |
| `fix.induction.schedule` | `fix_induction_schedule` | Induction sessions | plan_id, session_type, scheduled_at, owner, attended |
| `fix.first90.plan` | `fix_first90_plan` | Ramp plan | employee_id, milestones_json, competence_gates_json, checkins_json, state |
| `fix.referral` | `fix_referral` | Employee referral | referring_employee_id, candidate_id, outcome, reward_state, reward_ref |
| `fix.recruitment.channel` | `fix_recruitment_channel` | Source | name, type, cost_model, contract_ref, performance_json |
| `fix.recruitment.cost` | `fix_recruitment_cost` | Cost record | requisition_id, channel_id, cost_type, amount, invoice_ref |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.position`, `fix.org.unit`, `fix.job.profile` | **M21** | **Requisition target; employee creation** |
| Headcount budget | **M54** | **Requisition gate** |
| `fix.competency`, `fix.role.competency`, learning path | **M22** | Job profile requirements; onboarding path |
| `fix.succession.plan`, `fix.salary.band` | M57 | Internal candidates; offer band check |
| User account provisioning | M29 | Access request |
| `fix.asset`, van stock | M17 / M49 | Equipment issue |
| Safety induction requirement | M59 | Induction sequencing |
| `fix.document` | M24 | Document retention |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-TAO-01 | Requisition submitted | Check position approval and headcount budget; route the approval chain with SLA | **Block on failed check; notify the requester with the reason** |
| AUT-TAO-02 | Requisition approved | Publish internally; hold external posting for the configured internal-consideration period; surface internal candidates from M57 | Alert HR on publication failure |
| AUT-TAO-03 | Application received | Deduplicate against existing candidates; screen against mandatory criteria; capture consent | Route to manual screening |
| AUT-TAO-04 | Candidate shortlisted | Propose interview slots from panel availability; notify all parties | Escalate to HR Officer |
| AUT-TAO-05 | Interview completed | Request evaluations from each panel member independently; chase after the deadline | Escalate to hiring manager |
| AUT-TAO-06 | Candidate selected (technician role) | **Require the practical assessment before offer generation** | **Block offer** |
| AUT-TAO-07 | Offer prepared | Check against the salary band; route approval, escalating out-of-band to CFO | Block issue |
| AUT-TAO-08 | Offer accepted | Open pre-boarding; issue the document checklist to the candidate with deadlines | Escalate on non-response |
| AUT-TAO-09 | Documents complete and verified | Generate the **Labour Act** appointment letter for issue | Block joining; escalate |
| AUT-TAO-10 | Start date confirmed | **Generate the onboarding task set; raise provisioning requests to M29, M17/M03 and facilities with due dates before the start date** | **Escalate to HR Director** |
| AUT-TAO-11 | **7 days before start date** | **Report day-one readiness; escalate every incomplete task to its owner's manager** | **Escalate to HR Director and branch manager** |
| AUT-TAO-12 | Joining date reached | **Create the employee in M21; carry the competency baseline to M22; trigger payroll setup in M56; assign the learning path and mentor** | **Hard escalation — manual creation is a control failure** |
| AUT-TAO-13 | Onboarding task overdue | Notify the owner; escalate on continued breach | — |
| AUT-TAO-14 | Day 30 / 60 / 90 | Trigger check-ins and competence gate reviews; feed the M57 probation review | Escalate to manager |
| AUT-TAO-15 | Candidate not selected | Record the outcome; send the communication; set the retention date | Log for HR review |
| AUT-TAO-16 | **Candidate retention period expired** | **Anonymise or delete the candidate record automatically** *(PDPA)* | **Escalate to CDO — retention breach** |
| AUT-TAO-17 | Referred candidate hired and confirmed | Trigger the referral reward through M56 | Alert HR |

---

## 12. Interfaces

### 12.1 Upstream — M58 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M21 Core HR** | Positions, org structure, role profiles, vacancy from exits | REST + event |
| **M54 FP&A** | **Headcount budget — requisition gate** | REST |
| **M22 Competency** | Required competencies for the job profile; onboarding learning paths | REST |
| M57 Performance | Internal candidates, succession readiness, salary bands | REST |
| M59 HSE | Safety induction requirements by role | REST |
| M29 Identity | Provisioning capability | Service |
| M24 Documents | Document storage and retention | Service |

### 12.2 Downstream — M58 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M21 Core HR** | **Verified new employee with contract terms, documents and identity — at joining** | **Command** |
| **M22 Competency** | Initial competency baseline from the practical assessment; onboarding path assignment | Command |
| **M56 Payroll** | New employee payroll setup data; referral reward | Command |
| **M29 Identity** | User account and access provisioning requests | Command |
| **M17 / M03** | Tool, equipment and van stock issue requests | Command |
| M59 HSE | Safety induction scheduling | Command |
| M57 Performance | First-90-days plan feeding the probation review | Event |
| M55 Workforce | New employee for scheduling from the start date | Event |
| M54 FP&A | Headcount consumption against budget; recruitment cost | Event |
| M25 BI | Recruitment funnel, time to hire, cost per hire, source effectiveness | Warehouse extract |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `requisition.approved` | position, count, branch, target start | M54, HR |
| `requisition.blocked` | reason, position, budget state | Requester, CFO |
| `candidate.applied` | candidate, requisition, source | M25 |
| `assessment.completed` | candidate, result, competencies demonstrated | M22 |
| `offer.issued` / `offer.accepted` / `offer.declined` | candidate, terms, state | HR, M54 |
| **`onboarding.started`** | **candidate, start date, task set** | **M29, M17, M59, facilities** |
| **`readiness.incomplete`** | **candidate, outstanding tasks, days to start** | **HR Director, branch manager** |
| **`employee.joined`** | **employee, position, start date, terms** | **M21, M22, M55, M56** |
| `probation.plan_created` | employee, milestones, gates | M57 |
| `candidate.erased` | candidate ref, ground | M60, CDO |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/requisitions` | GET / POST | Raise and track requisitions | P03 |
| `/api/v1/requisitions/{id}/approve` | POST | Approval | P03 |
| `/api/v1/postings` | GET / POST | Job postings | P03, careers channel |
| `/api/v1/applications` | GET / POST | Application capture and pipeline | P03, careers channel |
| `/api/v1/interviews` | GET / POST | Scheduling | P03 |
| `/api/v1/evaluations` | POST | Panel evaluation submission | P03 |
| `/api/v1/assessments/practical` | POST | Practical assessment | P03 |
| `/api/v1/offers` | GET / POST | Offer generation and approval | P03 |
| `/api/v1/onboarding/{candidate}` | GET | Onboarding plan and task status | P03 |
| `/api/v1/onboarding/readiness` | GET | Day-one readiness report | P03 |
| `/api/v1/recruitment/analytics` | GET | Funnel, time to hire, cost per hire | P03, P06 |
| `/api/v1/candidates/{id}/erase` | POST | PDPA erasure | P03 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R06 Branch Manager / hiring manager | C R U | **Own requisitions**, own pipeline, own evaluations, onboarding tasks |
| **R45 Recruiter** *(new role)* | C R U | Pipeline, scheduling, communication; **no offer approval** |
| R31 HR Officer | C R U | Pre-boarding, documents, onboarding coordination |
| R30 HR Manager | C R U **A** | All — requisition, offer, appointment, policy |
| R03 Chief Financial Officer | R **A** | **Headcount budget; out-of-band offer approval** |
| R48 Service Head | R **U** | **Practical assessment for technician roles** |
| R43 Competency Assessor | R U | Practical assessment recording |
| R33 IT / System Administrator | R U | **Own provisioning tasks only** — no candidate data |
| R44 HSE Officer | R U | Safety induction tasks |
| **R40 Chief Data Officer** | R A | Candidate consent, retention and erasure governance |
| R49 GRC / Internal Audit | R | Approval trail, retention compliance |

**Boundaries.** A hiring manager sees only their own requisitions and candidates.
**Candidate NID and identity documents are S3** with the same protection as employee data,
resident in the Bangladesh store. Panel evaluations are private until submitted. The recruiter
cannot approve an offer.

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| Requisition status | Hiring managers, HR Director | Weekly | Open, approved, blocked, filled, ageing |
| **Recruitment funnel** | **HR Director** | **Weekly** | Applied → screened → interviewed → assessed → offered → joined, with conversion |
| **Time to hire** | **HR Director, CFO** | **Monthly** | By role, grade, branch and channel |
| **Cost per hire and source effectiveness** | **CFO, HR Director** | **Monthly** | Cost and quality of hire by channel and agency |
| Offer acceptance | HR Director | Monthly | Acceptance, decline reasons, lapse |
| **Day-one readiness** | **HR Director, branch managers** | **Daily for upcoming joiners** | Outstanding tasks by owner, days to start |
| Onboarding completion | HR Director | Monthly | Task completion by function; overdue by owner |
| **First-90-days progression** | **Branch managers, HR Director** | **Monthly** | Milestone and competence gate status per new joiner |
| **Early attrition** | **HR Director, COO** | **Quarterly** | Leavers within 90 / 180 days, by source, role and branch |
| Internal mobility | HR Director | Quarterly | Internal versus external fill rate |
| Referral programme | HR Director | Quarterly | Referrals, hires, retention, reward cost |
| **Candidate retention compliance** | **CDO, GRC** | **Monthly** | Records due for erasure, erased, overdue |
| Headcount against budget | CFO, HR Director | Monthly | Approved, filled, in pipeline, budget consumed |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W7 Target | W8 Target |
|---|---|---|---|---|
| KPI-275 | **Time to hire (days)** | unmeasured | measured | **< 30 for technician roles** |
| KPI-276 | Cost per hire | unmeasured | measured | **reducing year on year** |
| KPI-277 | **Day-one readiness complete** | unmeasured | 90% | **100%** |
| KPI-278 | Onboarding tasks completed by due date | n/a | 90% | **> 97%** |
| KPI-279 | **New technician time to full productivity** | unmeasured | −20% | **−35%** *(with M22)* |
| KPI-280 | **Early attrition (within 90 days)** | unmeasured | measured | **< 8%** |
| KPI-281 | Offer acceptance rate | unmeasured | 80% | **> 88%** |
| KPI-282 | **Requisitions raised without position or budget** | unmeasured | **0** | **0** |
| KPI-283 | **Technician offers without a practical assessment** | unmeasured | **0** | **0** |
| KPI-284 | Candidates receiving an outcome communication | unmeasured | 95% | **100%** |
| KPI-285 | **Candidate records erased on schedule** | 0% | 100% | **100%** |
| KPI-286 | Internal fill rate | unmeasured | 15% | **> 25%** |
| KPI-287 | **Employees created in M21 manually rather than through handover** | n/a | **0** | **0** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1/L2 | Odoo Recruitment + OCA extensions — pipeline, stages, applications | 35% |
| L5 | `cd_recruitment_bd`, `cd_onboarding` | 65% |

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 2 of 2 identifiers below are claimed by another module: **CD-087** also claimed by M50; **CD-088** also claimed by M49. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID *(provisional)* | Component | Type | Effort |
|---|---|---|---|
| CD-087 | **`cd_recruitment_bd`** — requisition with position and budget gate, structured evaluation, practical assessment, verification, offer approval, appointment letter, candidate retention and erasure | Odoo module | **7 PW** |
| CD-088 | **`cd_onboarding`** — onboarding orchestration, provisioning requests, readiness gate, induction, first-90-days plan, **M21 handover** | Odoo module | **5 PW** |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M21 Core HR** | **Blocking, absolute** — positions to requisition against and an employee record to hand over to |
| **M22 Competency** | **Blocking for job profiles and the competency baseline** — same category, one wave earlier |
| **M29 Identity** | Provisioning target — live from W1 |
| **M54 FP&A headcount budget** | **Blocking for the requisition gate** |
| M17 / M03 | Equipment and van stock issue |
| M59 HSE | Safety induction — same wave |
| M57 Performance | Internal candidates, salary bands, probation review |

> **W6 placement is correct.** M58 depends on M21, M22 and M57, all of which land in W5.
> Attempting M58 earlier produces a recruitment system that cannot check budget, cannot state
> required competencies, and cannot hand over to an employee master.

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Open requisitions in flight | Few | `fix.requisition` | W6 |
| Candidates in active pipelines | Variable | `fix.candidate`, `fix.application` — **with consent captured** | W6 |
| Recruitment agency contracts | Few | `fix.recruitment.channel` | W6 |
| Historical applications | **Not migrated** | — | — |

> **Do not migrate historical applications.** Under PDPA 2026 they are personal data with no
> lawful retention basis and no consent on record. Migrating them imports a compliance problem
> into a new system on day one.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **A requisition cannot be raised without an approved position and available headcount budget** | **Negative test against both conditions** |
| AC-02 | An offer outside the salary band cannot be issued without CFO approval | Negative test |
| AC-03 | **A technician offer cannot be generated without a recorded practical assessment** | **Negative test** |
| AC-04 | An appointment letter cannot be issued before verification is complete | Negative test |
| AC-05 | **The appointment letter meets Labour Act requirements** | **Legal review sign-off** |
| AC-06 | **The employee is created in M21 automatically at joining, from verified candidate data, with no re-keying** | **End-to-end trace for five hires** |
| AC-07 | The practical assessment result becomes the initial competency baseline in M22 | End-to-end trace |
| AC-08 | **Onboarding tasks generate with owners and due dates across all functions, and provisioning requests reach M29, M17/M03 and facilities** | **End-to-end trace** |
| AC-09 | **Day-one readiness reports 7 days before start and escalates incomplete items** | **Test with a deliberately incomplete plan** |
| AC-10 | Panel evaluations are independent and not visible before submission | Permission test |
| AC-11 | **Candidate consent is captured at application and is auditable** | **Record review** |
| AC-12 | **Candidate records are anonymised or deleted automatically at retention expiry, and on erasure request** | **Time-based test and erasure test** |
| AC-13 | Candidate NID resides only in the Bangladesh-resident store | Data-flow audit |
| AC-14 | Recruitment analytics report time to hire, cost per hire and source effectiveness | Report review |
| AC-15 | HR Director, CFO and a hiring manager sign off UAT | Signed UAT record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **What is the requisition approval chain by grade and cost?** | HR Director / CFO | W6 design |
| Q-02 | Is there an internal-consideration policy requiring internal posting before external? | HR Director | W6 design |
| Q-03 | **What practical assessment is used for technician roles, and who administers it?** | Service Head / COO | **W6 minus 3 months** |
| Q-04 | Is police or background verification required for any role — particularly roles with customer premises access or data access? | HR Director / legal | **W6 minus 3 months** |
| Q-05 | **What is the candidate data retention period, and has it been set under PDPA 2026?** | **CDO / legal** | **W6 minus 3 months** |
| Q-06 | Does an employee referral programme exist, and what is the reward mechanism? | HR Director | W6 design |
| Q-07 | Which recruitment channels and agencies are used, and under what commercial terms? | HR Director | W6 design |
| Q-08 | **Is the appointment letter template legally reviewed against the Labour Act?** | HR Director / legal | **W6 minus 2 months** |
| Q-09 | Will a public careers channel be built, and if so is it part of P01 or a separate property? *(scope question for `04-00`)* | HR Director / CMO | W6 design |
| Q-10 | What are the probation periods by role class, and do they comply with the Labour Act limits? *(links to M21 Q-04)* | HR Director / legal | W6 design |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §3, §5 (boundary map) · `M21_Core_HR_and_Employee_Lifecycle.md` ·
`M22_Learning_Competency_and_Certification.md` ·
`M57_Performance_Incentives_and_Compensation.md` · `M59_Health_Safety_and_Wellbeing.md` ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` §6.3

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §8.6, §5 pain points ·
`1000FiX_ERP_System_Comprehensive_URD.md` branch expansion plan

**External benchmark and regulation** *(verified 2026-08-12)*
SAP SuccessFactors Recruiting & Onboarding — requisition approval and **cross-functional
onboarding orchestration** · Oracle Recruiting Cloud — structured evaluation capture ·
Workday Recruiting — internal mobility integrated with succession ·
Odoo Recruitment (L1/L2 substrate) ·
**Bangladesh Labour Act 2006** — **appointment letter and identity card mandatory at
appointment**; service book; probation limits; minimum age ·
**Bangladesh Personal Data Protection Act 2026** — candidate data as personal data, consent,
retention limits, erasure rights, cross-border restriction on sensitive identifiers ·
**ISO 9001:2015 clause 7.2** — competence ensured on the basis of education, training or experience

---

*Module M58 · Category H · 1000FiX ERP System v2.0 · CONFIDENTIAL*
