---
id: FIX-ERP2-M59
module_id: M59
module_code: HSE
module_name: Health, Safety & Wellbeing
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

# M59 — Health, Safety & Wellbeing
### Category H · Code `HSE` · ★ New module in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M59 |
| **Module code** | `HSE` |
| **Category** | H — People & Workforce |
| **Status** | ★ **New** — absent from the v1.0 plan entirely |
| **Priority** | P2 |
| **Delivery wave** | W6 (Months 23–26) |
| **Business owner** | HR Director · **HSE Officer** (operational) |
| **System owner** | People Squad |
| **Delivery layers** | L2 (OCA maintenance/incident patterns) + L5 (custom HSE) |
| **Custom modules** | `cd_hse`, `cd_incident`, `cd_wellbeing` |
| **Requirement range** | FR-HSE-001 … FR-HSE-042 |
| **Requirement count** | 42 |
| **Effort estimate** | 14 person-weeks |
| **Depends on** | M21 Core HR · M22 Competency · M02 Field Service · M55 Workforce · M17 Assets · M23 Quality |
| **Depended on by** | M02 · M22 · M55 · M56 · M23 · M60 GRC |

---

## 2. Purpose

M59 keeps people safe, records what happens when they are not, and proves that the Company
discharged its duty.

### Why It Exists

1000FiX employs a **mobile technician workforce that travels Bangladeshi roads daily** and a
**workshop workforce that handles lithium-ion batteries, mains electricity, soldering
equipment and solvents**. These are the two highest-consequence risk profiles a service company
can carry, and neither is currently managed in any system.

The specific hazards are not abstract:

| Hazard | Where | Why It Matters Here |
|---|---|---|
| **Road traffic** | Field technicians travelling between jobs | **The dominant fatal and serious-injury risk in field service anywhere, and materially higher on Bangladeshi urban roads** |
| **Lithium-ion battery thermal runaway** | Workshop, van stock, customer premises | Damaged and swollen batteries are routine in device repair; a thermal event in a van or workshop is a fire, not an incident |
| **Electrical** | Workshop and customer premises | Mains testing, faulty appliances, unfamiliar customer wiring |
| **Lone working** | Field technicians at customer premises | No colleague present; assault, accident and medical emergency all unwitnessed |
| **Chemical** | Workshop | Solvents, isopropyl alcohol, flux, adhesives |
| **Ergonomic and thermal** | Workshop and field | Repetitive fine work; outdoor work in Bangladeshi heat |

**Regulatory basis.** The Bangladesh Labour Act 2006 and the Labour Rules 2015 place duties on
the employer for safety, health, first aid, safety committees, accident notification and
maternity protection. The Company holds ISO 9001:2015; **ISO 45001** is the corresponding
occupational health and safety management system standard and is the framework this module
follows, whether or not certification is pursued.

**The honest position on P2.** M59 is priority P2 and wave W6 because it is not required for
the ERP to transact. That is a sequencing judgement, not a statement of importance. A serious
injury is not deferred to W6. Two things follow: the interim manual process must be adequate
in the meantime, and safety induction and hazard reporting are the first capabilities to land.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.6 | HR scope; safety not addressed in v1.0 |
| ERP BRD §5 | Field workforce; workshop operations |
| **Bangladesh Labour Act 2006, Chapters V–VIII** *(verified 2026-08-12)* | Employer duties on **safety, health and hygiene, first aid, safety committees, accident notification and compensation**; provisions for hazardous work |
| **Bangladesh Labour Rules 2015** *(verified 2026-08-12)* | Implementation detail on safety committees, safety officers, first-aid provision and accident reporting |
| **Bangladesh Labour Act — maternity provisions** *(verified 2026-08-12)* | Maternity benefit and protection obligations *(entitlement administered in M55/M56; health protection here)* |
| **ISO 45001:2018** | OH&S management system — hazard identification, risk assessment, worker participation and consultation, incident investigation, emergency preparedness, competence |
| **ISO 9001:2015 clause 7.1.4** | Environment for the operation of processes |
| **PDPA 2026** *(verified 2026-08-12)* | **Health data is sensitive personal data** — the most restricted classification in the estate |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Hazard register and risk assessment |
| 2 | Job safety analysis for field and workshop tasks |
| 3 | Safe work procedures and permits |
| 4 | Incident, accident and near-miss reporting |
| 5 | Incident investigation, root cause and corrective action |
| 6 | Statutory accident notification |
| 7 | Injury, treatment and return-to-work management |
| 8 | Workers' compensation claim support |
| 9 | Personal protective equipment issue, use and replacement |
| 10 | Safety inspection and audit |
| 11 | **Road and vehicle safety for the mobile workforce** |
| 12 | **Lone-worker safety and emergency response** |
| 13 | **Battery, electrical and chemical hazard controls** |
| 14 | Safety training requirements and competence *(delivered by M22)* |
| 15 | Emergency preparedness and drills |
| 16 | Safety committee, worker consultation and observations |
| 17 | Occupational health — medical examinations, fitness for work |
| 18 | Employee wellbeing and assistance |
| 19 | Safety performance reporting and leading indicators |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Safety training delivery and competence records** | **M22** | M59 defines the requirement; M22 delivers and certifies |
| **Product and service quality non-conformance** | **M23** | Different failure domain, though investigation methods are shared |
| **Vehicle maintenance and fleet management** | **M17** | M59 owns driver and journey safety; M17 owns the vehicle |
| **Attendance, leave and working hours** | **M55** | Sick leave and maternity leave are M55 entitlements |
| **Medical insurance premium, payroll deduction, injury payment** | **M56** | M59 records the medical event; M56 pays |
| **Employee master and emergency contact** | **M21** | Referenced |
| **Environmental compliance and e-waste disposal** | **M06 / M23** | Data destruction and waste handling sit elsewhere |
| **Customer premises safety obligations** | **M08** | Contractual, not employment |
| **Building and facilities maintenance** | **M17** | M59 raises the safety finding; facilities remedy it |
| Information security incidents | **M28** | Different incident domain |

### 3.3 Shared Concepts

| Concept | M59's Role | Owning Module |
|---|---|---|
| Employee, emergency contact | References | M21 |
| Safety competence requirement | **Defines**; M22 delivers and certifies | M59 / M22 |
| Incident investigation | **Owns safety incidents**; M23 owns quality non-conformances | M59 / M23 |
| Job and location | Consumes for lone-worker and journey context | M02 |
| Vehicle | References; owns driver safety | M17 / M59 |
| Sick and maternity leave | Provides the medical basis; M55 holds the entitlement | M59 / M55 |
| PPE as an asset | **Owns issue and compliance**; M17 holds the stock | M59 / M17 |
| Health data | **Owns** — most restricted classification | M59 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP EHS Management** | Incident management, risk assessment, safety observations, regulatory reporting | **Incident-to-investigation-to-corrective-action as one closed chain**; leading and lagging indicator separation | Its full chemical inventory and emissions management |
| **ISO 45001:2018** | The management system framework | **The complete framework** — hazard identification, risk assessment, **worker participation**, incident investigation, emergency preparedness, competence | Nothing — it is the reference model |
| **Enablon / Intelex / Cority** | HSE platforms with mobile hazard reporting and observation programmes | **Mobile hazard and near-miss reporting from the technician app** — the single highest-value HSE capability for a mobile workforce | Standalone platform adoption; the data belongs with the workforce data |
| **Field-service lone-worker practice** | Check-in/check-out, panic alert, journey management, escalation on missed check-in | **Lone-worker protection built on M02's existing job and location flow** | A separate lone-worker device programme, at least initially |
| **Fleet and driver safety practice** | Licence validity, journey risk, driver behaviour, incident recording | **Licence validity as an eligibility gate; journey and driver incident recording** | Telematics-based behavioural scoring — a later addition |

**Design position.** Five deliberate differences.

First, **near-miss and hazard reporting is on the technician's phone, and it takes under
thirty seconds**. Every HSE system fails the same way: reporting is a form nobody fills in.
For a workforce that is never at a desk, if it is not in P02 and it is not fast, it does not
exist.

Second, **lone-worker protection reuses M02's job flow rather than adding a separate system**.
The technician already checks in and out of jobs with location. A missed check-out beyond an
expected duration is a signal the system already has; it needs an escalation path, not new
hardware.

Third, **road safety is treated as the primary risk, not a footnote**. Licence validity gates
assignment of vehicle-based work. Road incidents are recorded as safety incidents, not as
vehicle damage. This is where the serious injuries in this business will occur.

Fourth, **battery and electrical hazards are handled as explicit named controls**. Damaged
lithium-ion batteries pass through this business daily. Handling, storage, transport and
disposal need procedures, and the procedures need to be enforceable at the point of work.

Fifth, **health data is the most restricted data in the estate**. It is S3, it is resident in
Bangladesh, HR generalists do not see medical detail, and the manager sees a fitness-for-work
status, never a diagnosis.

---

## 5. Functional Areas & Features

### 5.1 Hazard, Risk & Safe Work

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-HSE-001 | **Hazard register** | Maintain a register of hazards by location, activity and role, with source, category and status | **P1** | L5 |
| FR-HSE-002 | **Risk assessment** | Assess each hazard for likelihood and severity, produce a risk rating, and record existing and required controls | **P1** | L5 |
| FR-HSE-003 | Control hierarchy | Record controls against the hierarchy — elimination, substitution, engineering, administrative, PPE — and require justification where PPE is the only control | **P1** | L5 |
| FR-HSE-004 | Risk review cycle | Review risk assessments on a defined cycle and on trigger events — new activity, new equipment, incident, legal change | **P1** | L5 |
| FR-HSE-005 | **Job safety analysis** | Maintain job safety analyses for field and workshop task types, accessible at the point of work on **P02** | **P1** | L5 |
| FR-HSE-006 | Safe work procedures | Publish safe work procedures linked to task types, equipment and hazards | **P1** | L5 |
| FR-HSE-007 | Permit to work | Operate a permit system for defined high-risk activities, with authorisation and closure | P2 | L5 |
| FR-HSE-008 | **Pre-job safety check** | Present a task-appropriate safety check on P02 before high-risk work commences and record the response | **P1** | L5 |

### 5.2 Incidents & Investigation

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-HSE-009 | **Mobile incident and near-miss reporting** | **Report an incident, near miss or hazard from P02 in under 30 seconds, with photograph, location and voice note, online or offline** | **P0** | L5 |
| FR-HSE-010 | Incident classification | Classify by type, severity and consequence — near miss, first aid, medical treatment, lost time, serious, fatal, property damage, environmental | **P1** | L5 |
| FR-HSE-011 | **Immediate response** | On a serious incident, alert the HSE Officer, branch manager and HR Director immediately, with the escalation path | **P0** | L5 |
| FR-HSE-012 | **Investigation** | Conduct an investigation proportionate to severity, with evidence, witness statements, timeline and contributing factors | **P1** | L5 |
| FR-HSE-013 | **Root cause analysis** | Apply structured root cause analysis and record findings, using the same method vocabulary as M23 | **P1** | L5 |
| FR-HSE-014 | **Corrective and preventive action** | Raise CAPAs with owner and due date, and track to verified closure | **P1** | L5 |
| FR-HSE-015 | Action effectiveness | Verify that corrective actions were effective, and reopen where they were not | **P1** | L5 |
| FR-HSE-016 | **Statutory notification** | Identify notifiable incidents under the **Labour Act and Labour Rules**, prompt notification within the statutory period, and record the submission | **P1** | L5 |
| FR-HSE-017 | Incident trend analysis | Analyse incidents by type, cause, location, activity, role and time, and identify emerging patterns | **P1** | L5 |
| FR-HSE-018 | Cross-domain linkage | Link a safety incident to a quality non-conformance (M23), an asset (M17) or a job (M02) where related | P2 | L5 |

### 5.3 Field & Mobile Workforce Safety

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-HSE-019 | **Driving licence validity** | Record driving licence type and expiry and **block assignment of vehicle-based work on lapse**, through the M22 eligibility service | **P1** | L5 |
| FR-HSE-020 | **Road incident recording** | Record road traffic incidents as safety incidents with vehicle, journey, injury and third-party detail | **P1** | L5 |
| FR-HSE-021 | Journey risk | Flag higher-risk journeys — night travel, long distance, adverse weather, unfamiliar area — and apply the associated controls | P2 | L5 |
| FR-HSE-022 | **Lone-worker check-in** | Use M02 job check-in and check-out as the lone-worker signal, with expected durations by task type | **P1** | L5 |
| FR-HSE-023 | **Missed check-out escalation** | **Escalate automatically when a technician does not check out within the expected window plus tolerance**, with a defined contact chain | **P1** | L5 |
| FR-HSE-024 | **Panic alert** | Provide a panic alert on P02 that raises an immediate alarm with location to the branch and HSE Officer | **P1** | L5 |
| FR-HSE-025 | Customer premises hazard | Allow a technician to record a hazard at a customer location, flagging it for future visits | **P1** | L5 |
| FR-HSE-026 | Right to stop work | Provide a recorded mechanism for a technician to decline unsafe work without penalty, with review | **P1** | L5 |
| FR-HSE-027 | Heat and environmental controls | Apply controls for outdoor work in extreme heat, linked to scheduling in M55 | P2 | L5 |

### 5.4 Workshop, Equipment & PPE

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-HSE-028 | **Battery hazard control** | Maintain and enforce procedures for handling, storing, transporting and disposing of damaged and swollen lithium-ion batteries, including quarantine and incident response | **P1** | L5 |
| FR-HSE-029 | **Electrical safety** | Maintain electrical safety procedures, equipment testing records and isolation requirements for workshop and field work | **P1** | L5 |
| FR-HSE-030 | Chemical safety | Maintain a register of chemicals with safety data sheets, storage requirements and handling procedures | **P1** | L5 |
| FR-HSE-031 | **PPE issue and compliance** | Record PPE issued per employee by role, with issue date, replacement due date and acknowledgement | **P1** | L5 |
| FR-HSE-032 | PPE replacement | Track PPE condition and replacement, and alert on overdue replacement | **P1** | L5 |
| FR-HSE-033 | **Safety inspection** | Schedule and record safety inspections of workshops, branches, vehicles and stores, with findings and actions | **P1** | L5 |
| FR-HSE-034 | Equipment safety register | Record safety-critical equipment with inspection, calibration and test due dates *(coordinated with M17)* | P2 | L5 |
| FR-HSE-035 | **Emergency preparedness** | Maintain emergency plans, evacuation procedures, first-aid provision and fire equipment records per site, and record drills | **P1** | L5 |

### 5.5 Health, Wellbeing & Governance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-HSE-036 | **Occupational health record** | Maintain medical examination and fitness-for-work records with the **strictest access control in the estate** | **P1** | L5 |
| FR-HSE-037 | **Fitness for work** | Record fitness status and restrictions, and publish **only the restriction, never the medical detail**, to scheduling and dispatch | **P1** | L5 |
| FR-HSE-038 | **Injury and return to work** | Manage injury cases from treatment through absence to phased return, coordinating with M55 leave and M56 payment | **P1** | L5 |
| FR-HSE-039 | Workers' compensation | Support compensation claims under the **Labour Act**, with the record, calculation basis and correspondence | **P1** | L5 |
| FR-HSE-040 | **Safety committee and worker consultation** | Support the statutory safety committee — membership, meetings, minutes, actions — and record worker consultation as required by **ISO 45001** | **P1** | L5 |
| FR-HSE-041 | Wellbeing and assistance | Provide access to wellbeing resources and a confidential assistance route, with anonymous usage reporting only | P2 | L5 |
| FR-HSE-042 | **Safety performance reporting** | Report leading indicators (observations, inspections, training, actions closed) and lagging indicators (incident rates, lost-time injury frequency, severity) | **P1** | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Offline-first mobile reporting** | Incident, near-miss and hazard reports capture and queue offline on P02 and synchronise on reconnection. Connectivity is never a reason a hazard goes unreported |
| T-02 | **Under 30 seconds to report** | Photograph, location and voice note with minimal typing. Classification is done later by the HSE Officer, not by the reporter |
| T-03 | **Panic alert priority path** | The panic alert bypasses normal queuing and delivers through multiple channels simultaneously (push, SMS, voice) with location |
| T-04 | **Missed check-out detection** | A scheduled evaluator compares actual check-out against expected duration plus tolerance and escalates through a defined contact chain |
| T-05 | **Health data isolation** | Medical records are **S3 with a dedicated access-control boundary**, resident in Bangladesh, encrypted, access-logged, and inaccessible to HR generalists and managers |
| T-06 | **Restriction without diagnosis** | The scheduling interface receives a fitness status and restrictions only. Diagnosis, treatment and medical history never cross this boundary |
| T-07 | **Eligibility integration** | Driving licence validity and safety competence publish to the M22 eligibility service, so a lapse blocks assignment through the existing control |
| T-08 | **Statutory clock tracking** | Notifiable incidents start a statutory notification clock with escalating alerts; a missed notification is a compliance breach, not a task |
| T-09 | **Immutable incident record** | The original report is never edited. Classification, investigation and findings are added; the reporter's account is preserved verbatim |
| T-10 | **Anonymous reporting supported** | Hazards and safety concerns can be reported anonymously; the system does not resolve the reporter's identity |
| T-11 | **Shared RCA vocabulary with M23** | Root cause categories are common across safety and quality, so cross-domain patterns are visible |
| T-12 | **Performance envelope** | Mobile report submission ≤ 3 s online, immediate offline · panic alert delivery ≤ 10 s · missed check-out evaluation every 5 minutes |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M59 |
|---|---|---|
| **Field technician** | No way to report a hazard; unsafe work is declined informally or not at all | Reports a hazard in seconds; has a panic alert; can decline unsafe work on record |
| **Workshop technician** | Battery and chemical handling by convention | Documented procedures, PPE tracked, quarantine process for damaged batteries |
| **Branch manager** | Learns of incidents by word of mouth | Notified immediately; sees branch safety performance and open actions |
| **HSE Officer** *(role may not yet exist)* | No system, no data | Hazard register, incident pipeline, inspection schedule, statutory clock |
| **HR Director** | Cannot demonstrate the Company discharged its duty | Complete record: assessments, training, PPE, inspections, investigations |
| **Dispatcher** | Cannot know a technician's licence lapsed or that they are on restricted duty | Assignment blocked or restricted through the M22 eligibility service |
| **Injured employee** | Case handled ad hoc | Treatment, absence, compensation and return to work managed as one case |
| **Labour inspector** | Records incomplete or absent | Complete statutory record produced from the system |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Injury reduction** | Hazards reported and controlled; near misses acted on before they become injuries | **The primary purpose — every avoided serious injury is the whole module paid for** |
| **Lost time reduction** | Fewer injuries; managed return to work | Direct saving in lost capacity and replacement cost |
| **Road incident reduction** | Licence gating, journey risk controls, incident analysis | Addresses the highest-consequence risk in the business |
| **Fire and property loss** | Lithium-ion battery controls, quarantine, electrical safety | **A single van or workshop battery fire exceeds this module's cost** |
| **Statutory compliance** | Notification, safety committee, first aid, records | Removes a Labour Act exposure and inspection risk |
| **Compensation cost control** | Faster response, managed return to work, documented investigation | Reduces claim duration and cost |
| **Insurance position** | Documented HSE management with evidence | Supports better terms and defensible claims |
| **ISO 45001 readiness** | The framework implemented as designed | Certification becomes achievable if the Company chooses to pursue it |
| **Retention** | Technicians who feel unsafe leave | Safety is a retention factor in field workforces, and technicians are expensive to replace |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **The duty of care becomes demonstrable** | The Company's obligation to its people is currently discharged in practice but not in evidence. If something serious happens, the difference matters enormously |
| **Near misses become information** | A near miss is a free lesson. Today those lessons are lost entirely |
| **The lone technician is not alone** | A missed check-out that nobody notices is the scenario that ends badly. This closes it |
| **Workers get a voice** | ISO 45001 requires worker participation. The safety committee and observation programme give technicians a channel that is recorded and answered |
| **Right to stop work becomes real** | Declining unsafe work informally depends on the relationship with the supervisor. Recorded, reviewed and protected, it becomes a right |
| **Health privacy is respected** | A manager knowing an employee's restriction without knowing their diagnosis is the correct outcome, and one most organisations get wrong |
| **The ISO 9001 posture is complete** | Quality certification with unmanaged safety is a gap that auditors and corporate customers both notice |

---

## 8. Lifecycle & State Model

### 8.1 Incident

```
   +--------------------+
   |  REPORTED          |  from P02: photo, location, voice, offline-capable
   |  (original record  |  <-- IMMUTABLE from this point
   |   never edited)    |
   +---------+----------+
             |
   +---------v----------+   serious/fatal --> IMMEDIATE ALERT
   |   CLASSIFIED       |   HSE Officer, branch manager, HR Director
   +---------+----------+   + statutory notification clock STARTS
             |
   +---------v----------+
   |  INVESTIGATING     |  evidence, witnesses, timeline, contributing factors
   +---------+----------+
             |
   +---------v----------+
   |  ROOT CAUSE        |  shared RCA vocabulary with M23
   |  DETERMINED        |
   +---------+----------+
             |
   +---------v----------+
   |  ACTIONS RAISED    |  CAPA with owner and due date
   +---------+----------+
             |
   +---------v----------+   not effective --> REOPENED
   |  ACTIONS VERIFIED  |
   +---------+----------+
             |
   +---------v----------+
   |      CLOSED        |  findings published; risk assessment reviewed;
   +--------------------+  training need raised in M22 where competence-related

   Parallel where injury occurred:
     INJURY CASE ──► TREATMENT ──► ABSENCE (M55) ──► COMPENSATION (M56)
                                       └──► PHASED RETURN ──► FULL DUTY
```

### 8.2 Lone-Worker Protection

```
   TECHNICIAN CHECKS IN TO JOB (M02, with location)
        │
        ▼
   EXPECTED DURATION SET  (by task type, from M02 job data)
        │
        ├── checks out within window ──────────► NORMAL, no action
        │
        ├── panic alert pressed ───────────────► IMMEDIATE ALARM
        │                                        branch + HSE + defined chain
        │                                        location attached
        │
        └── no check-out beyond window + tolerance
                 │
                 ▼
            AUTOMATED CONTACT ATTEMPT (call, message)
                 │
                 ├── responds ──► extend or resolve
                 │
                 └── no response
                          │
                          ▼
                 ESCALATION CHAIN
                 branch manager → HSE Officer → emergency contact (M21)
                          │
                          ▼
                 INCIDENT OPENED AUTOMATICALLY
```

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-HSE-01 | **Any employee may report a hazard, near miss or incident, at any time, including anonymously, without penalty** | **H** | HR Director |
| BRU-HSE-02 | **The original incident report is immutable; investigation is added, never substituted** | **H** | HSE Officer |
| BRU-HSE-03 | **A serious or fatal incident alerts the HSE Officer, branch manager and HR Director immediately** | **H** | HSE Officer |
| BRU-HSE-04 | **A notifiable incident must be notified to the authority within the statutory period** *(Labour Act / Labour Rules)* | **H** | HR Director |
| BRU-HSE-05 | Every lost-time and serious incident requires a documented investigation with root cause | **H** | HSE Officer |
| BRU-HSE-06 | Corrective actions must be verified for effectiveness before closure | **H** | HSE Officer |
| BRU-HSE-07 | **A lapsed driving licence blocks assignment of vehicle-based work** *(via M22 eligibility)* | **H** | COO |
| BRU-HSE-08 | **A lapsed statutory or safety certification blocks the associated work** *(via M22 eligibility)* | **H** | HSE Officer |
| BRU-HSE-09 | **A missed check-out beyond the expected window plus tolerance triggers the escalation chain automatically** | **H** | COO |
| BRU-HSE-10 | **A technician may decline unsafe work; the refusal is recorded, reviewed and carries no penalty** | **H** | COO |
| BRU-HSE-11 | Safety induction must be complete before a new employee performs field or workshop work | **H** | HSE Officer |
| BRU-HSE-12 | **Required PPE must be issued and acknowledged before the associated work is performed** | **H** | HSE Officer |
| BRU-HSE-13 | **Damaged or swollen lithium-ion batteries must be quarantined per procedure and never carried in general van stock** | **H** | HSE Officer |
| BRU-HSE-14 | **Health and medical data is S3 with dedicated access control, resident in Bangladesh; HR generalists and managers have no access** | **H** | CDO |
| BRU-HSE-15 | **Scheduling and dispatch receive fitness status and restrictions only — never diagnosis** | **H** | CDO |
| BRU-HSE-16 | Risk assessments are reviewed on the defined cycle and on trigger events | **H** | HSE Officer |
| BRU-HSE-17 | Safety committee meetings are held at the statutory frequency with recorded minutes and actions | **H** | HR Director |
| BRU-HSE-18 | Wellbeing and assistance usage is reported in aggregate only, never by individual | **H** | CDO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.hazard` | `fix_hazard` | Identified hazard | category, description, location_ref, activity, role_ids, identified_by, identified_on, state |
| `fix.risk.assessment` | `fix_risk_assessment` | Risk evaluation | hazard_id, likelihood, severity, rating, existing_controls, required_controls, residual_rating, assessor_id, review_due |
| `fix.control` | `fix_control` | Control measure | risk_assessment_id, hierarchy_level, description, owner_id, implemented_on, verified |
| `fix.job.safety.analysis` | `fix_job_safety_analysis` | JSA by task type | task_type, steps_json, hazards_json, controls_json, ppe_required, version, effective_from |
| `fix.safe.work.procedure` | `fix_safe_work_procedure` | Procedure | code, title, scope, content_ref, hazards_json, version, approved_by |
| `fix.permit` | `fix_permit` | Permit to work | type, activity, location, requested_by, authorised_by, valid_from, valid_to, state, closure_ref |
| **`fix.hse.incident`** | `fix_hse_incident` | Incident, near miss, hazard report | type, severity, classification, reported_by, anonymous, reported_at, location, description, photos_ref, voice_ref, job_ref, vehicle_ref, state, **original_record_hash** |
| `fix.incident.investigation` | `fix_incident_investigation` | Investigation | incident_id, investigator_id, timeline_json, witnesses_json, evidence_ref, contributing_factors, root_causes_json, completed_on |
| `fix.hse.action` | `fix_hse_action` | CAPA | incident_id / assessment_id, description, type, owner_id, due_date, state, completed_on, effectiveness_verified, verified_by |
| `fix.statutory.notification` | `fix_statutory_notification` | Regulatory notification | incident_id, authority, due_by, submitted_on, reference, evidence_ref, state |
| **`fix.injury.case`** | `fix_injury_case` | Injury management | incident_id, employee_id, injury_type, treatment, absence_from, absence_to, m55_leave_ref, restrictions, return_plan_json, state |
| `fix.compensation.claim` | `fix_compensation_claim` | Workers' compensation | injury_case_id, basis, calculated_amount, submitted_on, state, m56_payment_ref |
| **`fix.health.record`** | `fix_health_record` | **Occupational health — highest restriction** | employee_id, examination_type, date, provider, outcome, **fitness_status**, restrictions, next_due, document_ref |
| `fix.fitness.status` | `fix_fitness_status` | Publishable status only | employee_id, status, restrictions_summary, valid_from, valid_to |
| `fix.ppe.item` | `fix_ppe_item` | PPE type | code, name, roles_json, replacement_interval, standard_ref, m17_product_ref |
| `fix.ppe.issue` | `fix_ppe_issue` | Issued to employee | employee_id, ppe_item_id, issued_on, acknowledged_on, replacement_due, condition, returned_on |
| `fix.safety.inspection` | `fix_safety_inspection` | Inspection record | type, location_ref, scheduled_for, inspector_id, checklist_ref, findings_json, actions_json, completed_on |
| `fix.emergency.plan` | `fix_emergency_plan` | Site emergency arrangements | location_ref, plan_ref, wardens_json, first_aiders_json, equipment_json, last_reviewed |
| `fix.drill` | `fix_drill` | Emergency drill | location_ref, type, date, participants, evacuation_time, findings, actions_json |
| `fix.driver.record` | `fix_driver_record` | Driver safety | employee_id, licence_type, licence_number, expires_on, verified_by, incidents_count, state |
| `fix.lone.worker.event` | `fix_lone_worker_event` | Check-out breach or panic | employee_id, job_ref, type, triggered_at, location, contact_attempts_json, escalation_json, resolution, resolved_at |
| `fix.location.hazard` | `fix_location_hazard` | Customer premises hazard | party_id, address_ref, hazard_description, reported_by, reported_on, active |
| `fix.work.refusal` | `fix_work_refusal` | Right to stop work | employee_id, job_ref, ground, recorded_at, reviewed_by, outcome |
| `fix.safety.committee` | `fix_safety_committee` | Committee and meetings | location_ref, members_json, meeting_date, minutes_ref, actions_json |
| `fix.chemical` | `fix_chemical` | Chemical register | name, classification, sds_ref, storage_requirements, locations_json, quantity |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.employee`, emergency contact | M21 | Population; escalation chain |
| `fix.competency.assessment`, eligibility service | **M22** | **Safety competence; licence-based assignment blocking** |
| `fix.work.order`, check-in / check-out, location | **M02** | **Lone-worker signal** |
| `fix.attendance.record`, `fix.leave.request` | M55 | Injury absence |
| `fix.asset`, vehicle, van stock | M17 / M49 | Vehicle, equipment, PPE stock |
| `fix.nonconformance` | M23 | Cross-domain linkage and shared RCA |
| `fix.document` | M24 | Procedures, SDS, evidence, minutes |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-HSE-01 | Incident reported from P02 | Acknowledge to the reporter; route to the HSE Officer and branch manager by severity | **Queue offline; never lose a report** |
| AUT-HSE-02 | **Serious or fatal incident classified** | **Immediate multi-channel alert to HSE Officer, branch manager, HR Director and CEO; start the statutory notification clock** | **Escalate through every channel until acknowledged** |
| AUT-HSE-03 | **Statutory notification due** | **Alert at intervals before the deadline; escalate to HR Director and CEO as it approaches** | **Hard escalation — a missed notification is a statutory breach** |
| AUT-HSE-04 | **Panic alert pressed on P02** | **Immediate alarm with location to branch, HSE Officer and the escalation chain, through push, SMS and voice simultaneously** | **All channels attempted; failure escalates further** |
| AUT-HSE-05 | **Check-out not recorded within expected duration plus tolerance** | **Automated contact attempt; on no response, escalate through branch manager, HSE Officer and emergency contact; open an incident** | **Escalate — silence is the failure mode this exists to catch** |
| AUT-HSE-06 | **Driving licence expiring or expired** | **Alert the employee and manager; on expiry, publish the eligibility block to M22** | **Escalate to Operations Manager** |
| AUT-HSE-07 | Safety certification expiring | Raise a renewal need in M22; escalate statutory certifications | Escalate to HSE Officer |
| AUT-HSE-08 | Incident investigation identifies a competence cause | **Raise a mandatory training need in M22 for the affected population** | Log and alert |
| AUT-HSE-09 | Incident closed | Trigger review of the related risk assessment and JSA | Flag for HSE Officer |
| AUT-HSE-10 | Corrective action overdue | Notify the owner; escalate to the branch manager and HSE Officer | Escalate to HR Director |
| AUT-HSE-11 | PPE replacement due | Notify the employee and manager; raise an issue request to M17 | Alert HSE Officer |
| AUT-HSE-12 | Safety inspection due | Schedule and notify the inspector; escalate if overdue | Escalate to HSE Officer |
| AUT-HSE-13 | Risk assessment review due, or a trigger event occurs | Raise a review task | Escalate |
| AUT-HSE-14 | Injury absence recorded | Coordinate the M55 leave record and the M56 payment treatment; open a return-to-work plan | Alert HR |
| AUT-HSE-15 | **Fitness status or restriction changes** | **Publish the restriction — not the medical detail — to M55 and M02 for scheduling** | **Block assignment on failure; alert HSE Officer** |
| AUT-HSE-16 | New employee joining (event from M58) | Schedule safety induction; **block field and workshop work until complete** | **Hard block** |
| AUT-HSE-17 | Customer location hazard recorded | Flag the location so future visits surface the hazard to the assigned technician | Log |
| AUT-HSE-18 | Monthly | Compute leading and lagging safety indicators; publish the safety performance report | Alert People Squad |

---

## 12. Interfaces

### 12.1 Upstream — M59 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M02 Field Service** | **Job check-in and check-out with location, task type, customer address** | **Event — lone-worker signal** |
| **M21 Core HR** | Employee, role, branch, **emergency contact** | REST + event |
| **M22 Competency** | Safety competence and certification status | REST + event |
| **M58 Talent** | New joiners requiring safety induction | Event |
| M55 Workforce | Working hours, absence, schedule | REST |
| M17 Assets | Vehicles, equipment, PPE stock | REST |
| M23 Quality | Non-conformances with a safety dimension | Event |
| M31 Workshop | Workshop activity and battery handling events | Event |

### 12.2 Downstream — M59 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M22 Competency** | **Safety training requirements; licence validity for the eligibility service** | **Command** |
| **M02 Field Service** | **Fitness restrictions, JSA at point of work, location hazards, assignment blocks** | **REST + event** |
| **M55 Workforce** | Injury absence, fitness restrictions affecting scheduling | Command |
| **M56 Payroll** | Injury absence treatment; workers' compensation payment | Command |
| M23 Quality | Cross-domain incident linkage; shared root cause data | Event |
| M17 Assets | PPE issue requests; equipment safety findings | Command |
| M60 GRC | Safety compliance evidence, statutory notifications, committee records | Event |
| M24 Documents | Procedures, SDS, investigations, minutes, evidence | Command |
| M25 BI | Safety indicators, incident facts, inspection compliance | Warehouse extract |
| **P02 Technician App** | **Reporting, panic alert, JSA, safety checks, PPE, location hazards** | **REST** |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| **`hse.incident_reported`** | **type, severity, location, reporter, job ref** | **HSE, branch manager, M25** |
| **`hse.serious_incident`** | **incident, severity, injury, location** | **HSE, HR Director, CEO, M60** |
| **`hse.panic_alert`** | **employee, location, job, timestamp** | **Branch, HSE, escalation chain** |
| **`hse.checkout_overdue`** | **employee, job, location, elapsed** | **Branch, HSE, escalation chain** |
| `hse.statutory_notification_due` | incident, authority, deadline | HR Director, CEO, M60 |
| `hse.action_raised` / `hse.action_overdue` | action, owner, due date | Owner, HSE, manager |
| `hse.licence_lapsed` | employee, licence, eligibility blocked | **M22, M02** |
| `hse.fitness_changed` | employee, status, restrictions *(no diagnosis)* | **M55, M02** |
| `hse.training_need_raised` | population, competency, ground | **M22** |
| `hse.work_refused` | employee, job, ground | Branch manager, HSE |
| `hse.location_hazard_flagged` | party, address, hazard | **M02** |
| `hse.ppe_due` | employee, item, due date | Employee, manager, M17 |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| **`/api/v1/hse/report`** | **POST** | **Incident, near miss or hazard — offline-capable** | **P02** |
| **`/api/v1/hse/panic`** | **POST** | **Panic alert with location** | **P02** |
| `/api/v1/hse/jsa/{task_type}` | GET | Job safety analysis at point of work | **P02** |
| `/api/v1/hse/safety-check/{job}` | POST | Pre-job safety check response | P02 |
| `/api/v1/hse/incidents` | GET / POST | Incident register and investigation | P03 |
| `/api/v1/hse/incidents/{id}/investigation` | GET / POST | Investigation and root cause | P03 |
| `/api/v1/hse/actions` | GET / POST | CAPA register | P03 |
| `/api/v1/hse/hazards` | GET / POST | Hazard register and risk assessment | P03 |
| `/api/v1/hse/ppe/{employee}` | GET / POST | PPE issue and acknowledgement | P02, P03 |
| `/api/v1/hse/inspections` | GET / POST | Inspection scheduling and findings | P03 |
| **`/api/v1/hse/fitness/{employee}`** | **GET** | **Fitness status and restrictions only — no medical detail** | **M55, M02, P03** |
| `/api/v1/hse/health/{employee}` | GET / POST | **Occupational health — restricted access, step-up required** | P03 (HSE only) |
| `/api/v1/hse/performance` | GET | Leading and lagging indicators | P03, P06 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| **Every employee** | **C** R | **Report a hazard, near miss or incident; panic alert; view own PPE and safety training; view JSA** |
| R47 Team Leader | R U | Team incidents, actions and PPE |
| R06 Branch Manager | R U **A** | Branch incidents, investigations, inspections, actions |
| **R44 HSE Officer** *(new role)* | C R U **A** | **All HSE — hazards, incidents, investigations, actions, inspections, committee** |
| R30 HR Manager | R A | All HSE; statutory notification authority |
| R05 Operations Director | R A | Operational safety, eligibility blocks, work refusal review |
| **R46 Occupational Health** *(new role, restricted)* | **C R U** | **Medical records only — the only role with access to diagnosis and treatment detail** |
| R32 Quality Manager / ISO Coordinator | R | Cross-domain incidents and shared root cause |
| **R40 Chief Data Officer** | R A | Health data access governance and audit |
| R49 GRC / Internal Audit | R | Compliance evidence, notifications, committee records |
| R31 HR Officer | R | **Fitness status and restrictions only — no medical detail** |

**The health-data boundary is the strictest in the ERP.** `fix.health.record` is accessible
only to R46 Occupational Health and, under audit, the CDO. Everyone else — including the HR
Director, the branch manager and the HSE Officer — sees `fix.fitness.status`: a status and a
restriction, never a diagnosis. Wellbeing and assistance usage is reported in aggregate only.

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| **Safety performance dashboard** | **HR Director, COO, CEO** | **Monthly** | Lagging: incident rate, lost-time injury frequency, severity. Leading: observations, inspections, training, actions closed |
| **Incident register** | **HSE Officer, branch managers** | **Live** | All incidents by type, severity, location, state |
| **Open incidents and investigations** | **HSE Officer** | **Daily** | Investigations in progress, overdue |
| **Statutory notification status** | **HR Director, CEO, GRC** | **Live** | Notifiable incidents, deadlines, submissions |
| **Near-miss and hazard reporting rate** | **HSE Officer, COO** | **Monthly** | Reports per employee per month, by branch — **a low rate is a warning, not good news** |
| **CAPA register** | **HSE Officer, branch managers** | **Weekly** | Open actions, overdue, effectiveness verification |
| Risk assessment currency | HSE Officer | Monthly | Assessments overdue for review |
| **Lone-worker events** | **HSE Officer, COO** | **Weekly** | Overdue check-outs, panic alerts, resolution and response time |
| **Road incident analysis** | **COO, HSE Officer** | **Monthly** | Incidents by branch, journey type, time of day, cause |
| **Licence and safety certification validity** | **HSE Officer, Operations Manager** | **Weekly** | Expiring and lapsed, with eligibility impact |
| PPE compliance | HSE Officer, branch managers | Monthly | Issued, acknowledged, overdue for replacement |
| Inspection compliance | HSE Officer | Monthly | Scheduled, completed, overdue, findings open |
| **Injury and return to work** | **HR Director, HSE Officer** | **Monthly** | Active cases, absence days, return-to-work progress |
| Safety committee | HR Director, GRC | Quarterly | Meetings held, attendance, actions raised and closed |
| **Work refusal register** | **COO, HR Director** | **Monthly** | Refusals, grounds, outcomes — **reviewed for pattern, not for penalty** |
| Wellbeing usage | HR Director | Quarterly | **Aggregate only** — uptake, no individual data |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W7 Target | W8 Target |
|---|---|---|---|---|
| KPI-288 | **Lost-time injury frequency rate** | unmeasured | measured | **reducing year on year** |
| KPI-289 | **Serious and reportable incidents** | unmeasured | measured | **0 tolerance target** |
| KPI-290 | **Near-miss reports per employee per month** | 0 | > 0.3 | **> 0.6** *(higher is better)* |
| KPI-291 | **Statutory notifications made within the deadline** | unmeasured | **100%** | **100%** |
| KPI-292 | **Investigations completed within target** | n/a | 90% | **> 98%** |
| KPI-293 | **Corrective actions closed by due date** | n/a | 85% | **> 95%** |
| KPI-294 | Corrective actions verified effective | n/a | 90% | **100%** |
| KPI-295 | **Overdue check-outs detected and escalated** | 0% | **100%** | **100%** |
| KPI-296 | **Panic alert response time** | n/a | < 3 min | **< 90 s** |
| KPI-297 | **Employees working with a lapsed licence or safety certification** | unmeasured | **0** | **0** |
| KPI-298 | **Safety induction completed before first field or workshop work** | unmeasured | **100%** | **100%** |
| KPI-299 | PPE issued and acknowledged where required | unmeasured | 95% | **100%** |
| KPI-300 | Risk assessments current | 0% | 90% | **100%** |
| KPI-301 | Safety inspections completed on schedule | unmeasured | 90% | **> 98%** |
| KPI-302 | **Road traffic incidents per 100,000 km** | unmeasured | measured | **reducing** |
| KPI-303 | **Battery-related fire or thermal events** | unmeasured | **0** | **0** |
| KPI-304 | Return to work within the planned period | unmeasured | 85% | **> 92%** |
| KPI-305 | **Unauthorised access to health records** | n/a | **0** | **0** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L2 | OCA incident and maintenance patterns — record structure, scheduling | 15% |
| L5 | `cd_hse`, `cd_incident`, `cd_wellbeing` | 85% |

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 2 of 3 identifiers below are claimed by another module: **CD-089** also claimed by M19; **CD-090** also claimed by M20. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID *(provisional)* | Component | Type | Effort |
|---|---|---|---|
| CD-089 | **`cd_hse`** — hazard register, risk assessment, JSA, safe work procedures, permits, PPE, inspections, emergency preparedness, chemical register, safety committee, performance reporting | Odoo module | **6 PW** |
| CD-090 | **`cd_incident`** — incident capture *(offline mobile)*, classification, investigation, root cause, CAPA, statutory notification, **lone-worker detection and panic alert**, driver and road safety | Odoo module | **6 PW** |
| CD-091 | `cd_wellbeing` — occupational health records with dedicated access control, fitness status publication, injury case and return to work, compensation claims, wellbeing | Odoo module | 2 PW |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M02 Field Service** | **Blocking for lone-worker protection** — check-in and check-out are the signal |
| **M21 Core HR** | **Blocking** — employee and emergency contact |
| **M22 Competency** | **Blocking for eligibility blocking** — licence and certification gate assignment through M22 |
| **P02 Technician App** | **Blocking for reporting and panic alert** — the module's highest-value capability lives here |
| M17 Assets | Vehicles, equipment, PPE stock |
| M55 Workforce | Injury absence |
| M23 Quality | Shared root cause vocabulary |
| **HSE Officer appointed** | **Blocking, non-technical — the module needs an owner who does not currently exist** |

> **Recommendation: bring the reporting capability forward.** FR-HSE-009 (mobile incident and
> near-miss reporting) and FR-HSE-011 (immediate serious-incident alert) depend only on P02 and
> M21. They could ship in **W3 alongside the technician app** at low cost. The remaining 40
> requirements can stay in W6. **A workforce that can report a hazard three waves earlier is a
> materially better outcome than a complete HSE module in W6**, and this is a wave-plan decision
> for `06-01`.

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Existing safety procedures, if documented | Few | `fix.safe.work.procedure` | W6 |
| Historical incidents, if recorded | Unknown — likely minimal | `fix.hse.incident` (reference) | W6 |
| Driving licence records | Per driver | `fix.driver.record` | **W6 — or earlier, with M22** |
| Chemical inventory and SDS | Per workshop | `fix.chemical` | W6 |
| PPE issue records, if any | Variable | `fix.ppe.issue` | W6 |

> **There is likely almost nothing to migrate.** That is itself the finding: the hazard
> register, risk assessments and JSAs must be **authored**, not imported. This is a substantial
> HSE exercise with a long lead time and it requires the HSE Officer to be in post first.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **A technician can report an incident, near miss or hazard from P02 in under 30 seconds, with photograph and location, while offline** | **Field test with connectivity disabled, timed** |
| AC-02 | **The original report is immutable; investigation is added without altering it** | **Negative test** |
| AC-03 | **A serious incident alerts HSE Officer, branch manager and HR Director immediately through multiple channels** | **Alert test with acknowledgement tracking** |
| AC-04 | **The panic alert delivers with location within 90 seconds through push, SMS and voice** | **Timed field test** |
| AC-05 | **A missed check-out beyond the window plus tolerance triggers automated contact and escalation** | **Scripted test with a deliberately unclosed job** |
| AC-06 | **A lapsed driving licence blocks assignment of vehicle-based work through the M22 eligibility service** | **Negative test** |
| AC-07 | Safety induction incomplete blocks field and workshop work for a new joiner | Negative test |
| AC-08 | **A notifiable incident starts the statutory clock and escalates as the deadline approaches** | **Time-based test** |
| AC-09 | Investigation, root cause and CAPA close as one chain, with effectiveness verified | Three incidents end to end |
| AC-10 | Investigation identifying a competence cause raises a training need in M22 | End-to-end trace |
| AC-11 | **Medical detail is accessible only to Occupational Health; all other roles see fitness status and restrictions only** | **Permission audit across every role** |
| AC-12 | **A fitness restriction reaches scheduling and dispatch without any medical detail** | **Data-flow audit** |
| AC-13 | Health records reside only in the Bangladesh-resident store | Data-flow audit |
| AC-14 | A technician can decline unsafe work; the refusal is recorded and reviewed | Test case with review |
| AC-15 | Anonymous reporting works and the system does not resolve the reporter's identity | Technical audit |
| AC-16 | Safety performance reports separate leading and lagging indicators | Report review |
| AC-17 | HR Director, HSE Officer and COO sign off UAT | Signed UAT record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Is an HSE Officer appointed, and is a safety committee constituted as the Labour Rules require?** The module has no operational owner without this | **HR Director / CEO** | **Immediately — before W6 design** |
| Q-02 | **Do documented risk assessments, JSAs or safe work procedures exist?** If not, authoring them is a multi-month exercise preceding the build | HR Director / HSE Officer | **W6 minus 5 months** |
| Q-03 | **What is the current incident rate?** There is no baseline. Without one, no target is meaningful | HR Director | **W6 minus 4 months** |
| Q-04 | **What incidents are notifiable, to which authority, and within what period under the Labour Act and Labour Rules?** Must be confirmed with legal counsel, not assumed | HR Director / legal | **W6 minus 4 months** |
| Q-05 | **Should mobile hazard and incident reporting ship in W3 with P02 rather than W6?** *(recommendation: yes)* | COO / HR Director | **W3 planning — decide now** |
| Q-06 | **What are the current lithium-ion battery handling, storage, transport and disposal practices?** This is the highest-consequence workshop hazard | Service Head / HSE Officer | **W6 minus 4 months** |
| Q-07 | What PPE is currently issued, to whom, and is it adequate for the assessed risks? | HSE Officer | W6 design |
| Q-08 | Are occupational health services engaged — pre-employment medicals, periodic examinations, injury treatment? | HR Director | W6 design |
| Q-09 | **Who may access medical records? Is an occupational health function available, or must medical data be held by an external provider?** | **HR Director / CDO** | **W6 minus 3 months** |
| Q-10 | Is workers' compensation insured, self-funded, or handled per the Labour Act schedule? | CFO / HR Director | W6 design |
| Q-11 | Does the Company intend to pursue **ISO 45001** certification? If so, the design should target certification rather than framework alignment | CEO / HR Director | W6 design |
| Q-12 | What is the lone-worker escalation chain and its out-of-hours arrangement? | COO / HSE Officer | **W6 design** |

**Q-01 and Q-05 are the ones to act on now.** The module needs an owner who does not appear to
exist, and its highest-value capability could ship three waves earlier at low cost.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §3, §5 (boundary map), §10 (risks) ·
`M21_Core_HR_and_Employee_Lifecycle.md` · `M22_Learning_Competency_and_Certification.md` ·
`M55_Time_Attendance_and_Workforce_Scheduling.md` ·
`M58_Talent_Acquisition_and_Onboarding.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M02_Field_Service_and_Dispatch_Management.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M31_Workshop_and_Depot_Repair_Management.md` ·
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` (P02)

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §5, §8.6 ·
`1000FiX_ERP_System_Comprehensive_URD.md` Persona 3 (Field Technician)

**External standards and regulation** *(verified 2026-08-12)*
**Bangladesh Labour Act 2006, Chapters V–VIII** — employer duties on **safety, health and
hygiene, first aid, safety committees, accident notification and compensation**; hazardous work
provisions; maternity protection ·
**Bangladesh Labour Rules 2015** — safety committee constitution, safety officer requirements,
first-aid provision, accident reporting procedure ·
**ISO 45001:2018** — occupational health and safety management system: hazard identification,
risk assessment, **worker participation and consultation**, incident investigation, emergency
preparedness, competence *(clause 7.2, shared with M22)* ·
**ISO 9001:2015 clause 7.1.4** — environment for the operation of processes ·
SAP EHS Management — incident-to-CAPA chain, leading and lagging indicators ·
Enablon / Intelex / Cority — mobile hazard reporting and observation programmes ·
Field-service lone-worker practice — check-in/check-out, panic alert, escalation on missed
check-in · **Bangladesh Personal Data Protection Act 2026** — **health data as sensitive
personal data** with residency restriction and the strictest access controls

---

*Module M59 · Category H · 1000FiX ERP System v2.0 · CONFIDENTIAL*
