---
id: FIX-ERP2-M21
module_id: M21
module_code: HCM
module_name: Core HR & Employee Lifecycle
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

# M21 — Core HR & Employee Lifecycle
### Category H · Code `HCM` · Existing module, re-scoped in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M21 |
| **Module code** | `HCM` |
| **Category** | H — People & Workforce |
| **Status** | Existing (re-scoped — time to M55, payroll to M56, performance to M57, talent to M58) |
| **Priority** | **P1** |
| **Delivery wave** | W5 (Months 19–22) |
| **Business owner** | HR Director |
| **System owner** | People Squad |
| **Delivery layers** | L1 (Odoo `hr`) + L2 (OCA `hr_*`) + L5 (custom) |
| **Custom modules** | `cd_hr_core`, `cd_org_structure`, `cd_employee_ess`, `cd_hr_documents` |
| **Requirement range** | FR-HCM-001 … FR-HCM-046 |
| **Requirement count** | 46 |
| **Effort estimate** | 18 person-weeks |
| **Depends on** | M29 Identity & Security · M33 Party Master · M30 Platform Admin · M24 Documents |
| **Depended on by** | **Every module in Category H** · M02 Field Service · M29 Identity · M31 Workshop · M52 Expenses · M60 GRC |

---

## 2. Purpose

M21 is the **employee master** — the single authoritative record of every person the Company
employs, their contract, their position in the organisation, and every movement through it
from hire to exit.

It is the People equivalent of M33: everything else in Category H references it and nothing
else holds a competing copy.

### Why It Exists

The Company employs 500+ people across 51+ branches. Their records live in paper files,
branch spreadsheets and the memory of long-serving managers. There is no reliable answer to
basic questions: how many technicians does the Company have, in which branches, on what
contracts, with what notice periods, and what does the organisation actually look like.

That matters more in v2.0 than it did before. Dispatch (M02) needs to know who is a technician
and where. Payroll (M56) needs contracts and structures. Competency (M22) needs positions.
Identity (M29) needs joiners, movers and leavers to provision and revoke system access. All of
that depends on one accurate employee record.

### Why It Was Re-Scoped

The v1.0 plan placed time, payroll, performance and training inside HR. Every tier-one HCM
platform separates them, because each has a different change cadence, a different blast
radius and a different regulatory regime. Payroll parameters change annually with the national
budget; the employee master does not. Merging them means every tax change is a change to the
employee record.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.6 (BR-HRM-001) | "Maintain employee master records with all personal, employment, and qualification data" |
| ERP BRD §6.2 Process 9 | Current state: attendance via manual sign-in book, leave in a spreadsheet, payroll calculated manually in Excel |
| ERP BRD §5.1 | 500+ employees: technicians, service centre staff, support, management |
| ERP BRD §11.4 | **Employee records retained 10 years after termination — Bangladesh Labour Act** |
| **Bangladesh Labour Act 2006 (as amended)** *(verified 2026-08-12)* | Employers must provide **appointment letters, identity cards and service books**; establish death, retirement and resignation benefits; a **Provident Fund must be formed if three-quarters of workers demand it in writing**; Workers' Participation Fund and Workers' Welfare Fund obligations |
| **Personal Data Protection Act 2026** *(verified 2026-08-12)* | Employee personal data is regulated; NID and TIN are Sensitive Personally Identifiable Data subject to residency restriction; consent, transparency notice and data-subject rights apply to employees as data subjects |
| ERP URD Personas 9, 10 | HR Officer and HR Manager needs |
| Company Profile §Career Opportunities | Regular hiring; growth in an expanding company |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Employee master record — personal, contact, identity, employment |
| 2 | Employment contract: type, terms, notice, probation, effective dating |
| 3 | Organisation structure: legal entity, division, department, branch, team |
| 4 | Position and job architecture: job, grade, reporting line, headcount |
| 5 | Employee lifecycle: hire, confirm, transfer, promote, suspend, exit |
| 6 | Movement history with effective dating and full audit |
| 7 | Employment documents: appointment letter, identity card, service book |
| 8 | Dependants, emergency contacts and nominees |
| 9 | Employee self-service and manager self-service |
| 10 | Organisation chart and headcount reporting |
| 11 | Employee data privacy: consent, notice, access and rectification |
| 12 | Joiner–mover–leaver events driving identity provisioning in M29 |
| 13 | Exit process: notice, clearance, final settlement trigger, knowledge handover |
| 14 | Workforce establishment and vacancy position tracking |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Attendance, leave, shifts, rosters** | **M55** | Different change cadence; consumed by payroll and dispatch |
| **Payroll calculation, statutory deduction, BEFTN** | **M56** | Annual statutory change; highest blast radius in the estate |
| **Performance, appraisal, incentive** | **M57** | Cyclical process with its own governance |
| **Competency, certification, training** | **M22** | A service-delivery control, not an HR record |
| **Recruitment, candidates, offers, onboarding** | **M58** | Pre-employment; different data subject status |
| **Safety incidents, medical records** | **M59** | S3 confidentiality; different regulator |
| System access provisioning and revocation | **M29** | M21 emits the event; M29 acts on it |
| Party record where an employee is also a customer | **M33** | One party master; employment is a role |
| Expense claims and reimbursement | **M52** | Financial transaction |
| Technician dispatch profile, skills for assignment | **M02** / **M22** | Operational, derived from HR data |
| Employee IT assets | **M66** | Internal ITSM |
| Sales commission | **M53** | Revenue-linked, not employment-linked |

### 3.3 Shared Concepts

| Concept | M21's Role | Owning Module |
|---|---|---|
| Employee | **Owns** | M21 |
| Party | References; an employee is a party role | M33 |
| Position | **Owns** | M21 |
| Organisation unit | **Owns the HR view**; M30 owns the operating unit | M21 / M30 |
| Contract | **Owns the employment contract**; M08 owns customer contracts | M21 |
| Identity | Triggers provisioning | M29 |
| Competency | References; M22 owns | M22 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP SuccessFactors Employee Central** | Core HR with effective-dated records, position management, organisation structures, and clean handoffs into payroll, learning, performance and workforce planning | **Effective dating on every employment attribute** and **position-based organisation structure** | Full SuccessFactors data model depth |
| **Oracle HCM Cloud — Global Human Resources** | Worker, assignment, position, organisation hierarchy; person-versus-worker separation | The **person/worker separation** — a person may have more than one employment relationship over time | Oracle's assignment complexity |
| **Workday HCM** | Integrated hire-to-retire with organisation, position and job architecture | Job architecture: job family, job profile, grade | Platform-specific business-object model |
| **Dynamics 365 Human Resources** | Employee record, position management, employee and manager self-service | Manager self-service as a first-class surface | — |
| **Odoo 19 HR** | Unified employee profiles with contracts merged into the employee record | The L1 substrate | Odoo's merged contract model — 1000FiX needs contract history separate from the employee record for Labour Act compliance |

**Design position.** Four deliberate differences.

First, **every employment attribute is effective-dated**. A transfer, promotion or salary change
has a date from which it applies. Without this, payroll cannot be recalculated correctly for a
prior period, and a Labour Act dispute cannot be answered with evidence.

Second, **the employee is a role of a party, not a separate identity**. A technician who is also
a customer is one person in M33 with two roles. This avoids the common ERP outcome where staff
purchase records and employment records cannot be connected.

Third, **the Labour Act artefacts are system-generated, not filed**. The appointment letter,
identity card and service book are statutory obligations. They are produced from the employee
record and retained in M24, not typed and stored in a drawer.

Fourth, **employees are data subjects under the PDPA**. Bangladesh's Personal Data Protection
Act 2026 does not exempt employment data. Consent, transparency notice, access and rectification
rights apply to staff, and NID and TIN are residency-restricted exactly as for customers.

---

## 5. Functional Areas & Features

### 5.1 Employee Master

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-HCM-001 | Employee record | Maintain one record per employee holding personal, contact, identity, employment, banking and emergency data | **P1** | L1 |
| FR-HCM-002 | Party linkage | Link the employee to a single party in M33, so a staff member who is also a customer is one person | **P1** | L5 |
| FR-HCM-003 | Employee numbering | Assign a permanent, non-reusable employee number independent of any external reference | P1 | L1 |
| FR-HCM-004 | Identity documents | Capture NID, TIN, passport and birth registration with format validation, **written to the Bangladesh-resident store** | **P0** | L5 |
| FR-HCM-005 | Bank account | Capture salary bank account with account name, number, bank and branch, validated for BEFTN format | **P1** | L5 |
| FR-HCM-006 | Dependants and nominees | Record dependants, nominees for statutory benefits, and emergency contacts | P1 | L1 |
| FR-HCM-007 | Photograph and biometric reference | Store a photograph for the identity card and a reference to the biometric template held in M55 | P1 | L5 |
| FR-HCM-008 | Employee status | Manage Applicant · Probation · Confirmed · Active · Suspended · Notice · Exited with effective dates | **P1** | L5 |
| FR-HCM-009 | Multiple employment periods | Support a rehired employee as the same person with a new employment period, preserving prior service history | P2 | L5 |
| FR-HCM-010 | Employee search | Search by name, number, NID, branch, position and status, in Bengali and English | P1 | L1 |

### 5.2 Employment Contract & Terms

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-HCM-011 | Contract record | Record contract type — permanent, probationary, contractual, casual, apprentice — with start, end, notice period and terms | **P1** | L2 |
| FR-HCM-012 | Contract history | Retain every contract version with effective dates; a change creates a new version, never an edit | **P1** | L5 |
| FR-HCM-013 | **Appointment letter** | Generate the statutory appointment letter from the contract, in Bengali and English, and retain it in M24 | **P1** | L5 |
| FR-HCM-014 | **Identity card** | Generate the statutory employee identity card with photograph, number and validity | **P1** | L5 |
| FR-HCM-015 | **Service book** | Maintain the statutory service book recording appointment, movements, leave, and disciplinary record | **P1** | L5 |
| FR-HCM-016 | Probation management | Track probation period, review due date, confirmation or extension, with alerts | P1 | L5 |
| FR-HCM-017 | Notice period | Record notice period per contract and apply it at resignation or termination | P1 | L5 |
| FR-HCM-018 | Compensation structure | Record the salary structure — basic, house rent, medical, conveyance, other allowances — with effective dating, consumed by M56 | **P1** | L5 |
| FR-HCM-019 | Contract expiry alerts | Alert before a fixed-term contract expires, at defined lead times | P1 | L5 |

### 5.3 Organisation & Position

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-HCM-020 | Organisation structure | Model legal entity → division → department → branch → team, effective-dated | **P1** | L5 |
| FR-HCM-021 | Branch alignment | Align the HR branch to the M30 operating unit so branch reporting reconciles across HR, finance and operations | **P1** | L5 |
| FR-HCM-022 | Job architecture | Define job family, job profile, grade and level, with a maintained catalogue | P1 | L5 |
| FR-HCM-023 | Position management | Define positions with job, grade, organisation unit, headcount and status — filled, vacant, frozen | P1 | L5 |
| FR-HCM-024 | Reporting line | Record the reporting manager per employee, effective-dated, supporting matrix and dotted-line relationships | P1 | L5 |
| FR-HCM-025 | Organisation chart | Present the organisation chart with drill-down, filtered by entity, branch and department | P2 | L5 |
| FR-HCM-026 | Establishment and vacancy | Report approved establishment against filled positions and open vacancies, feeding M58 | P2 | L5 |
| FR-HCM-027 | Delegation of authority | Record approval authority by position and value, consumed by M63 workflow | P1 | L5 |

### 5.4 Lifecycle Events

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-HCM-028 | Hire | Create the employee from an accepted offer in M58, with contract, position and start date | **P1** | L5 |
| FR-HCM-029 | Confirmation | Confirm an employee at the end of probation, with review evidence | P1 | L5 |
| FR-HCM-030 | Transfer | Transfer between branches, departments or positions with effective dating and full history | **P1** | L5 |
| FR-HCM-031 | Promotion and grade change | Record promotion with grade, position and compensation change, effective-dated | P1 | L5 |
| FR-HCM-032 | Suspension | Suspend with reason, effective dates and pay treatment, feeding M55 and M56 | P1 | L5 |
| FR-HCM-033 | Resignation | Record resignation with notice, last working day and reason | P1 | L5 |
| FR-HCM-034 | Termination | Record termination with type, reason, notice treatment and statutory grounds | **P1** | L5 |
| FR-HCM-035 | Retirement and death in service | Handle retirement and death-in-service with the statutory benefit path | P2 | L5 |
| FR-HCM-036 | **Exit clearance** | Run a structured clearance covering assets, van stock, tools, IT access, dues and knowledge handover | **P1** | L5 |
| FR-HCM-037 | Final settlement trigger | Trigger final settlement in M56 covering notice, leave encashment, gratuity and outstanding dues | **P1** | L5 |
| FR-HCM-038 | Exit interview | Record structured exit interview responses and reason-for-leaving analysis | P2 | L5 |
| FR-HCM-039 | **Joiner–mover–leaver events** | Emit JML events to M29 so system access is provisioned on hire, adjusted on movement and **revoked within 24 hours of exit** | **P0** | L5 |

### 5.5 Self-Service & Employee Data Rights

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-HCM-040 | Employee self-service | Let employees view and update permitted personal data, view their contract, payslips, leave balance and service record | **P1** | L5 |
| FR-HCM-041 | Manager self-service | Let managers view their team, approve requests, initiate movements and see team headcount and cost | P1 | L5 |
| FR-HCM-042 | Change request workflow | Route employee-initiated changes to permitted fields through approval where the field is controlled | P1 | L5 |
| FR-HCM-043 | Document access | Give the employee access to their own appointment letter, identity card, service book and certificates | P1 | L5 |
| FR-HCM-044 | **Employee privacy notice and consent** | Present the employment transparency notice, record acknowledgement, and support consent withdrawal where processing is consent-based | **P0** | L5 |
| FR-HCM-045 | **Employee data-subject rights** | Support employee access, rectification within 30 days, and erasure subject to the 10-year statutory retention override | **P0** | L5 |
| FR-HCM-046 | Employee directory | Provide an internal directory with name, position, branch and work contact, respecting privacy settings | P2 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Effective dating throughout** | Every employment attribute carries valid-from and valid-to dates. A query for any past date returns the state as it was on that date |
| T-02 | **Residency-classified fields** | NID, TIN and passport are written to the Bangladesh-resident store; the regional record holds a reference key only *(NFR-086, NFR-099)* |
| T-03 | **Sensitive-field access control** | Salary, bank account, identity documents, disciplinary record and exit reason are **S3-classified**: encrypted, access-logged, and requiring step-up authentication |
| T-04 | **JML event reliability** | Joiner, mover and leaver events publish through the transactional outbox; M29 provisioning failure escalates rather than failing silently |
| T-05 | **Immutable service book** | The service book is append-only. Corrections are compensating entries with a reason and an approver |
| T-06 | **Position–employee integrity** | An employee cannot occupy two positions in the same period without an explicit dual-role record |
| T-07 | **Organisation reconciliation** | The HR branch structure reconciles to the M30 operating unit structure; a mismatch is a reported exception |
| T-08 | **Bilingual document generation** | Appointment letters, identity cards and service books render correctly in Bengali and English with correct typography |
| T-09 | **Retention enforcement** | Employee records are retained 10 years after termination and disposed automatically thereafter, unless under legal hold |
| T-10 | **Audit completeness** | Every change to every employment attribute is audited with before value, after value, actor, timestamp and reason |
| T-11 | **Performance envelope** | Employee search ≤ 400 ms · employee record load ≤ 1.5 s · organisation chart for 500 employees ≤ 2 s |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M21 |
|---|---|---|
| **HR Officer** | Maintains paper files and branch spreadsheets; cannot answer headcount questions reliably | One record per employee; headcount, structure and movements answerable instantly |
| **Employee** | Requests a payslip or leave balance by asking someone | Self-service access to contract, payslips, leave, service record and documents |
| **Branch manager** | Does not know their own establishment against actual | Sees their team, vacancies, contract expiries and approvals in one place |
| **HR Director** | Cannot see the organisation as a whole | Organisation chart, headcount, attrition and structure across 51+ branches |
| **Dispatch (M02)** | Works from a technician list maintained separately | Consumes the authoritative employee and position record |
| **IT Administrator** | Learns about a leaver when someone mentions it | Receives a leaver event and revokes access within 24 hours |
| **Payroll (M56)** | Rebuilds employee data every run | Reads contract, structure and status from one source |
| **Compliance officer** | Cannot evidence appointment letters or service books | Statutory artefacts generated, retained and retrievable |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Payroll accuracy foundation** | Payroll errors overwhelmingly originate in wrong employee data, not wrong calculation | Precondition for the **< 0.3% payroll correction** target |
| **Access revocation on exit** | Automated leaver events closing system access | Closes a material security exposure — today a leaver's access may persist indefinitely |
| **Administrative labour saving** | Self-service replaces HR handling of routine requests | A material share of HR officer time released across 51+ branches |
| **Statutory compliance** | Appointment letters, identity cards and service books generated and retained | Removes a Labour Act exposure that is currently undocumented |
| **Dispatch reliability** | M02 assigns work from an accurate technician and position record | Supports the **8–9 jobs per technician per day** target |
| **Attrition visibility** | Exit reason analysis by branch, role and tenure | Makes retention actionable — technician attrition is a direct constraint on capacity |
| **Establishment control** | Approved positions versus filled and vacant | Prevents uncontrolled headcount growth as the Company scales |
| **PDPA compliance for staff** | Employee notice, consent, rights and residency handling | Avoids exposure of up to **BDT 25 lakh** per rights violation |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **The Company knows who works for it** | This sounds trivial and is not. At 500+ people across 51+ branches, no single person currently holds this |
| **Dignity in employment records** | An employee who can see their own contract, service record and payslip is treated as a party to an agreement, not a line in a spreadsheet |
| **Evidence in a dispute** | A Labour Act claim is decided on records. Effective-dated history and a service book are the evidence |
| **Foundation for growth** | Opening branches or entering a second country requires a repeatable employment structure, not a set of local arrangements |
| **Manager capability** | Manager self-service makes people management a defined activity rather than an informal one |
| **Employees are data subjects too** | Applying the same privacy standard internally as externally is both lawful and a signal about how the Company operates |

---

## 8. Lifecycle & State Model

### 8.1 Employee Lifecycle

```
   +-------------+
   |  APPLICANT  |  (record originates in M58; not yet an employee)
   +------+------+
          | offer accepted --> hire event
   +------v------+
   |  PROBATION  |  contract effective; JML joiner event to M29
   +---+-----+---+
       |     | probation review
       |     +--> EXTENDED --> back to PROBATION
       |
       | confirmed
   +---v---------+
   |  CONFIRMED  |<---------------------------+
   +---+--+--+---+                            |
       |  |  |                                | reinstated
       |  |  +--> SUSPENDED -------------------+
       |  |         (pay treatment defined)
       |  |
       |  +-----> TRANSFERRED / PROMOTED ------+  (mover event to M29)
       |          effective-dated, history kept
       |
       | resignation / termination / retirement
   +---v---------+
   |   NOTICE    |  last working day set; clearance begins
   +------+------+
          |
   +------v----------+
   |    CLEARANCE    |  assets, van stock, tools, IT access, dues, handover
   +------+----------+
          | clearance complete
   +------v------+
   |   EXITED    |  leaver event to M29 --> access revoked within 24 hours
   +------+------+     final settlement triggered in M56
          |
   +------v----------+
   |  ARCHIVED       |  retained 10 years, then disposed unless on legal hold
   +-----------------+

   REHIRED -- a new employment period on the same person record; prior service preserved
```

### 8.2 Contract Version

```
   DRAFT --> APPROVED --> ACTIVE --> SUPERSEDED (by a new version)
                             |
                             +--> EXPIRED (fixed-term, no renewal)
                             |
                             +--> TERMINATED

   A change never edits an active contract; it creates a new effective-dated version.
```

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-HCM-01 | Every employee is linked to exactly one party in M33 | **H** | HR Director |
| BRU-HCM-02 | Every employment attribute change is effective-dated; retrospective changes require approval | **H** | HR Director |
| BRU-HCM-03 | A contract change creates a new version; an active contract is never edited | **H** | HR Director |
| BRU-HCM-04 | **An appointment letter, identity card and service book must exist for every employee** *(Labour Act)* | **H** | HR Director |
| BRU-HCM-05 | The service book is append-only; corrections are compensating entries with an approver | **H** | HR Director |
| BRU-HCM-06 | **NID, TIN and passport are written only to the Bangladesh-resident store** | **H** | CTO |
| BRU-HCM-07 | Salary, bank account, identity documents, disciplinary record and exit reason are S3-classified with step-up authentication and access logging | **H** | CDO |
| BRU-HCM-08 | **A leaver event revokes all system access within 24 hours** | **H** | CTO |
| BRU-HCM-09 | Exit clearance must complete before final settlement is released | **H** | HR Director / CFO |
| BRU-HCM-10 | An employee cannot occupy two positions concurrently without an approved dual-role record | **H** | HR Director |
| BRU-HCM-11 | Employee records are retained 10 years after termination and disposed thereafter unless on legal hold | **H** | HR Director |
| BRU-HCM-12 | **The employment transparency notice is presented and acknowledged before employment data is processed** *(PDPA)* | **H** | CDO |
| BRU-HCM-13 | An employee rectification request is actioned and notified within 30 days *(PDPA)* | **H** | CDO |
| BRU-HCM-14 | Only HR may create or amend employment attributes; managers raise a request | **H** | HR Director |
| BRU-HCM-15 | A suspension must state its pay treatment, which flows to M55 and M56 | **H** | HR Director |

*Classification: **H** hard block · **A** approved override · **C** computed*

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.employee` | `fix_employee` | The employee master | employee_number, party_id, name_en, name_bn, dob, gender, status, joined_on, exited_on, entity_id |
| `fix.employment.period` | `fix_employment_period` | One period of employment | employee_id, started_on, ended_on, exit_reason, rehire_of |
| `fix.employee.identity` | `fix_employee_identity` **(resident store)** | Statutory identifiers | employee_id, doc_type, doc_number, issued, expiry, verified_by |
| `fix.employee.bank` | `fix_employee_bank` | Salary account | employee_id, bank, branch, account_name, account_number, beftn_validated, effective_from |
| `fix.employee.dependant` | `fix_employee_dependant` | Dependants and nominees | employee_id, name, relation, dob, is_nominee, nominee_share |
| `fix.employment.contract` | `fix_employment_contract` | Contract version | employee_id, version, contract_type, effective_from, effective_to, notice_days, probation_months, terms_ref, state |
| `fix.salary.structure` | `fix_salary_structure` | Compensation composition | contract_id, component, amount, effective_from, effective_to |
| `fix.org.unit` | `fix_org_unit` | Organisation node | code, name, type, parent_id, operating_unit_id, effective_from, effective_to |
| `fix.job.profile` | `fix_job_profile` | Job architecture | code, job_family, title_en, title_bn, grade, level, description_ref |
| `fix.position` | `fix_position` | An established post | code, job_profile_id, org_unit_id, headcount, status, effective_from |
| `fix.employee.assignment` | `fix_employee_assignment` | Employee to position | employee_id, position_id, manager_id, effective_from, effective_to, assignment_type |
| `fix.employee.movement` | `fix_employee_movement` | Lifecycle event | employee_id, movement_type, from_values, to_values, effective_from, approved_by, reason |
| `fix.service.book` | `fix_service_book` | Statutory service record (append-only) | employee_id, entry_type, entry_date, description, recorded_by |
| `fix.exit.clearance` | `fix_exit_clearance` | Clearance checklist | employee_id, item, owner_role, status, cleared_by, cleared_at, notes |
| `fix.delegation.authority` | `fix_delegation_authority` | Approval authority | position_id, authority_type, value_limit, effective_from |
| `fix.employee.document` | `fix_employee_document` | Generated statutory artefacts | employee_id, doc_type, version, document_ref, generated_at |
| `fix.employee.consent` | `fix_employee_consent` | PDPA acknowledgement | employee_id, notice_version, acknowledged_at, purposes |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.party` | M33 | Employee is a party role |
| `fix.branch`, `operating.unit` | M30 | Organisation alignment |
| `fix.document` | M24 | Statutory artefact storage and retention |
| `fix.competency`, `fix.competency.assessment` | M22 | Displayed on the employee record |
| `fix.attendance.record`, `fix.leave.request` | M55 | Displayed in self-service |
| `fix.payslip` | M56 | Displayed in self-service |
| `fix.application`, `fix.offer` | M58 | Source of a hire |
| `fix.incident.investigation` | M59 | **Not displayed** — S3, restricted to M59 |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-HCM-01 | Offer accepted in M58 | Create the employee, contract and assignment; generate the appointment letter and identity card; **emit the joiner event to M29** | Queue for manual creation; alert HR |
| AUT-HCM-02 | Employee created | Present the employment transparency notice; record acknowledgement | Block data processing beyond the statutory minimum; alert CDO |
| AUT-HCM-03 | Probation review due | Notify the manager and HR at 30 and 7 days before the confirmation date | Escalate to HR Director |
| AUT-HCM-04 | Probation date passes without decision | Default per policy; escalate to HR Director | — |
| AUT-HCM-05 | Transfer or promotion effective | Update assignment, **emit the mover event to M29**, notify M55, M56, M02 and M22 | Escalate; access may be wrong |
| AUT-HCM-06 | Fixed-term contract approaching expiry | Alert manager and HR at 90, 60 and 30 days | — |
| AUT-HCM-07 | Resignation or termination recorded | Set notice, calculate last working day, open the clearance checklist, notify all clearance owners | Manual clearance initiation |
| AUT-HCM-08 | Clearance item outstanding near last working day | Escalate to the item owner and then to HR Director | — |
| AUT-HCM-09 | **Last working day reached** | **Emit the leaver event to M29; access revocation must complete within 24 hours; confirm revocation back to HR** | **Escalate immediately — unrevoked access is a security incident** |
| AUT-HCM-10 | Clearance complete | Trigger final settlement in M56 covering notice, leave encashment, gratuity and dues | Hold settlement; alert HR and Finance |
| AUT-HCM-11 | Employee record incomplete against mandatory fields | Queue for HR completion; block payroll inclusion where a payroll-critical field is missing | — |
| AUT-HCM-12 | Employee data rectification request | Start the 30-day statutory clock; route for action; notify the employee on completion | Escalate at 50% and 75% of the clock |
| AUT-HCM-13 | 10 years after termination | Dispose the employee record per the retention schedule unless on legal hold | Alert on disposal failure |

---

## 12. Interfaces

### 12.1 Upstream — M21 Consumes

| Source | What | Mechanism |
|---|---|---|
| M58 Talent Acquisition | Accepted offer producing a hire | Command |
| M33 Party Master | Party record and identity; consent framework | REST |
| M30 Platform Admin | Legal entity, branch and operating unit structure | Master data |
| M29 Identity | Provisioning confirmation and access status | Event |
| M24 Documents | Statutory artefact storage and retention schedule | Service |
| M63 Process Automation | Approval workflow execution for movements and changes | Service |

### 12.2 Downstream — M21 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M29 Identity** | **Joiner, mover and leaver events driving provisioning and revocation** | **Event** |
| **M55 Workforce** | Employee, position, contract terms, status for attendance and rostering | REST + event |
| **M56 Payroll** | Employee, contract, salary structure, bank account, status, movements | REST + event |
| **M57 Performance** | Employee, position, grade, manager for appraisal and incentive | REST |
| **M22 Competency** | Employee, position, job profile for the competency requirement | REST |
| **M59 Health & Safety** | Employee, position, branch for incident and training attribution | REST |
| M02 Field Service | Technician identity, branch, position, status | REST + event |
| M31 Workshop | Technician identity for bench allocation | REST |
| M52 Expenses | Employee and approval authority | REST |
| M60 GRC | Delegation of authority for control testing | REST |
| M25 Business Intelligence | Headcount, structure, movement and attrition facts | Warehouse extract |
| P03 Admin Portal | Employee and manager self-service | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| **`employee.joined`** | employee, position, branch, start date, access profile | **M29**, M55, M56, M22, M02 |
| **`employee.moved`** | employee, from position, to position, effective date | **M29**, M55, M56, M22, M02 |
| **`employee.left`** | employee, last working day, exit type | **M29**, M55, M56, M02, M52 |
| `employee.confirmed` | employee, confirmation date | M56, M57 |
| `employee.suspended` | employee, effective dates, pay treatment | M55, M56, M02 |
| `contract.versioned` | employee, contract version, effective from | M56 |
| `salary_structure.changed` | employee, components, effective from | M56 |
| `position.created` / `position.vacant` | position, org unit, job profile | M58 |
| `clearance.completed` | employee, items, cleared by | M56 |
| `employee.rights_request` | employee, request type, statutory due | M60, M24 |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/employees` | GET / POST | Employee master | P03, M58 |
| `/api/v1/employees/{id}` | GET / PATCH | Record detail and amendment | P03 |
| `/api/v1/employees/search` | GET | Search across identifiers | P03, M02 |
| `/api/v1/employees/{id}/contract` | GET / POST | Contract versions | P03, M56 |
| `/api/v1/employees/{id}/movements` | GET / POST | Lifecycle events | P03 |
| `/api/v1/employees/{id}/service-book` | GET / POST | Statutory service record | P03 |
| `/api/v1/employees/{id}/clearance` | GET / PATCH | Exit clearance | P03 |
| `/api/v1/positions` | GET / POST | Position management | P03, M58 |
| `/api/v1/org-structure` | GET | Organisation chart and hierarchy | P03, P06 |
| `/api/v1/ess/me` | GET / PATCH | Employee self-service | P03, mobile |
| `/api/v1/mss/team` | GET | Manager self-service team view | P03 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R30 HR Manager | C R U D A | All employees, all entities |
| R31 HR Officer | C R U | Assigned scope — no salary or disciplinary access without grant |
| R06 Branch Manager | R U | Own branch team — no salary access |
| R05 Operations Director | R | All — structure and headcount, no personal data |
| R26 Finance Manager | R | Salary structure and bank details for payroll validation |
| **R40 Chief Data Officer** | R A | Employee consent, notices, rights requests |
| R33 IT / System Administrator | — | **No access to employee records**; receives JML events only |
| R32 Quality Manager / ISO Coordinator | R | Position and competency linkage only |
| **Employee (self)** | R U | **Own record only** — permitted fields, own documents |
| R01 Chief Executive Officer | R | Structure, headcount, attrition — not individual records |

**Field-level restrictions.** Salary, bank account, identity documents, disciplinary record and
exit reason are **S3**: encrypted, access-logged, step-up authentication required. Medical and
safety data is **not held here** — it is in M59 with tighter control.

**Segregation of duties.** The person who creates an employee record cannot approve their own
salary structure (SOD-25). HR cannot both process and approve a retrospective effective-date
change (SOD-26).

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| Headcount dashboard | HR Director, CEO | Daily | Headcount by entity, branch, department, job family, contract type |
| Establishment versus actual | HR Director, CFO | Monthly | Approved positions, filled, vacant, frozen |
| Organisation chart | All managers | On demand | Structure with drill-down and reporting lines |
| Movement report | HR Director | Monthly | Hires, confirmations, transfers, promotions, exits |
| **Attrition analysis** | **HR Director, Ops Director, CEO** | **Monthly** | Attrition by branch, role, tenure, reason — technician attrition tracked separately |
| Contract expiry | HR Officer, branch managers | Weekly | Fixed-term contracts expiring in 90 days |
| Probation pipeline | HR Officer, managers | Weekly | Probation reviews due, overdue, outcomes |
| **Exit clearance status** | **HR Director, IT, Finance** | **Daily** | Open clearances, overdue items, access-revocation confirmations |
| Data completeness | HR Officer | Weekly | Employees with missing mandatory or payroll-critical fields |
| Statutory artefact compliance | HR Director, GRC | Monthly | Employees with appointment letter, identity card and service book — target 100% |
| Self-service adoption | HR Director | Monthly | Employees using self-service; requests handled without HR involvement |
| Employee rights requests | CDO, GRC | Monthly | Requests by type, statutory clock performance |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| KPI-212 | Employee record completeness | manual files | 92% | **> 98%** |
| KPI-213 | Employee self-service adoption | 0% | 70% | **> 85%** |
| KPI-214 | **Access revoked within 24 hours of exit** | unknown | **100%** | **100%** |
| KPI-215 | **Employees with appointment letter, ID card and service book** | unknown | 95% | **100%** |
| KPI-216 | Exit clearance completed before final settlement | unmeasured | **100%** | **100%** |
| KPI-217 | Technician attrition rate | unmeasured | baselined | **−15%** |
| KPI-218 | Probation reviews completed on time | unmeasured | 90% | **> 97%** |
| KPI-219 | Employee data rectification within 30 days | n/a | **100%** | **100%** |
| KPI-220 | HR administrative requests handled by self-service | 0% | 60% | **> 78%** |
| KPI-221 | **NID or TIN found outside the resident store** | n/a | **0** | **0** |
| KPI-222 | Employee record load time | — | < 2 s | **< 1.5 s** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `hr`, `hr_contract` | 26% |
| L2 | OCA `hr_employee_*`, `hr_contract_type`, `hr_org_chart` | 14% |
| L5 | `cd_hr_core`, `cd_org_structure`, `cd_employee_ess`, `cd_hr_documents` | 60% |

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 3 of 4 identifiers below are claimed by another module: **CD-066** also claimed by M14; **CD-068** also claimed by M15; **CD-069** also claimed by M15. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID *(provisional)* | Component | Type | Effort |
|---|---|---|---|
| CD-066 | `cd_hr_core` — employee, contract versioning, effective dating, movements, lifecycle | Odoo module | 7 PW |
| CD-067 | `cd_org_structure` — org units, job architecture, positions, assignments, delegation | Odoo module | 4 PW |
| CD-068 | `cd_employee_ess` — employee and manager self-service | Frontend + module | 4 PW |
| CD-069 | **`cd_hr_documents`** — appointment letter, identity card, **service book**, bilingual generation | Odoo module | **3 PW** |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M33 Party Master** | **Blocking** — an employee is a party role |
| **M29 Identity** | **Blocking** — JML events drive provisioning; S3 field control depends on it |
| **Bangladesh-resident store** | **Blocking** — NID and TIN capture *(DEP-31)* |
| M30 Platform Admin | Entity, branch and operating unit structure |
| M24 Documents | Statutory artefact retention |
| **Employment transparency notice approved** | **Blocking** — employee data processing requires it *(DEP-34, extended to employees)* |
| M58 Talent Acquisition | Hire source — W6; until then hires are entered directly |

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Employee records (paper files and spreadsheets) | 500+ | `fix.employee` | W5 |
| Employment contracts | 500+ | `fix.employment.contract` | W5 |
| Organisation structure | 51+ branches, departments | `fix.org.unit`, `fix.position` | W5 |
| Salary structures | 500+ | `fix.salary.structure` | W5 |
| Bank account details | 500+ | `fix.employee.bank` | W5 |
| Service history | Variable, incomplete | `fix.service.book` (opening entry) | W5 |

> **Migration warning.** Historical service records are likely incomplete. The service book
> should be opened with a **single verified opening entry** stating service from the joining
> date, rather than a reconstructed history that cannot be evidenced. A fabricated service
> history is worse than an honest opening balance in a Labour Act dispute.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every employee record links to exactly one party in M33 | Reconciliation report |
| AC-02 | Every employment attribute is effective-dated; a query for a past date returns the historical state | Point-in-time query test across 20 employees with movements |
| AC-03 | A contract change creates a new version; the prior version is preserved unaltered | Negative test |
| AC-04 | **Appointment letter, identity card and service book generate correctly in Bengali and English** | **Visual review by HR Director; 100% coverage report** |
| AC-05 | The service book is append-only; a correction is a compensating entry | Negative test |
| AC-06 | **NID and TIN are absent from every regional store, cache, log and export** | **Data-flow audit** |
| AC-07 | **A leaver event revokes all system access within 24 hours, confirmed back to HR** | **Timed test across 10 exits, end-to-end with M29** |
| AC-08 | Final settlement cannot be released before clearance completes | Negative test |
| AC-09 | Salary, bank and disciplinary fields require step-up authentication and log every access | Access audit |
| AC-10 | Employee self-service allows view and permitted update without HR involvement | Usability test with 20 employees |
| AC-11 | The employment transparency notice is presented and acknowledged before processing | Negative test |
| AC-12 | An employee rectification request is actioned and notified within 30 days | Scripted test |
| AC-13 | Migration reconciles: source count, loaded, rejected, and mandatory-field completeness | Migration reconciliation report signed by HR Director |
| AC-14 | Organisation chart renders for 500 employees in ≤ 2 seconds | Load test |
| AC-15 | HR Director and two branch managers sign off UAT | Signed UAT record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Do appointment letters, identity cards and service books exist today for all 500+ employees?** If not, this is a live Labour Act exposure independent of the ERP. | HR Director / Legal | **Immediately** |
| Q-02 | **Has a Provident Fund been formed, and did three-quarters of workers demand it in writing?** This determines whether PF is optional or mandatory for the Company. | HR Director / Legal | **W5 minus 3 months** |
| Q-03 | Are Workers' Participation Fund and Workers' Welfare Fund obligations currently discharged? | CFO / Legal | W5 minus 3 months |
| Q-04 | What is the job architecture — how many job families, grades and levels? This does not exist and must be authored. | HR Director | **W5 minus 3 months** |
| Q-05 | Is position management adopted, or is headcount managed by employee count only? Position management is more control but more maintenance. | HR Director | W5 design |
| Q-06 | What contract types are in use, and are casual or daily-wage workers employed at branches? | HR Director | W5 design |
| Q-07 | Who receives the employment transparency notice for existing employees, and when? | CDO / HR Director | W5 build |
| Q-08 | Are any employees also registered customers or marketplace sellers? This determines party-merge handling. | HR Director / CCO | W5 design |

**Q-01 and Q-02 are compliance questions, not design questions.** Both should be assessed now.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §3 (why payroll is separate), §5 (boundary map), §7 (statutory
obligations) · `M55_Time_Attendance_and_Workforce_Scheduling.md` ·
`M56_Payroll_Benefits_and_Statutory_Compliance.md` ·
`M22_Learning_Competency_and_Certification.md` ·
`03_Modules/K_Platform_and_Technology/_CATEGORY_OVERVIEW.md` (M29 identity) ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` §6.3–6.4

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §8.6 BR-HRM-001, §6.2
Process 9, §5.1, §11.4 · `1000FiX_ERP_System_Comprehensive_URD.md` Personas 9–10 ·
`1000FiX_Services_Company_Profile.md` §Career Opportunities

**External benchmark and regulation** *(verified 2026-08-12)*
**Bangladesh Labour Act 2006 (as amended)** — employer obligation to provide **appointment
letters, identity cards and service books**; death, retirement and resignation benefits;
**Provident Fund formation where three-quarters of workers demand it in writing**; Workers'
Participation Fund and Workers' Welfare Fund ·
**Bangladesh Personal Data Protection Act 2026 (Law 63 of 2026)** — employees are data
subjects; NID and TIN are sensitive personal data with cross-border transfer restriction ·
SAP SuccessFactors Employee Central — effective-dated core HR with position management and
clean handoffs to payroll, learning, performance and workforce planning ·
Oracle HCM Cloud Global Human Resources — person and worker separation ·
Workday HCM — job architecture and organisation modelling ·
Odoo 19 HR — unified employee profiles

---

*Module M21 · Category H · 1000FiX ERP System v2.0 · CONFIDENTIAL*
