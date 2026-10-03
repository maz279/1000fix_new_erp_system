---
id: FIX-ERP2-M23
module_id: M23
module_code: QMS
module_name: Quality Management System
category: I — Governance, Risk, Quality & Knowledge
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Quality Manager
system_owner: Governance Squad
priority: P1
wave: W5
---

# M23 — Quality Management System
### Category I · Code `QMS` · Existing module, re-scoped in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M23 |
| **Module code** | `QMS` |
| **Category** | I — Governance, Risk, Quality & Knowledge |
| **Status** | Existing (re-scoped — enterprise risk and control moved to M60; document control moved to M24; safety moved to M59) |
| **Priority** | **P1** |
| **Delivery wave** | W5 (Months 19–22) |
| **Business owner** | Quality Manager / ISO Coordinator |
| **System owner** | Governance Squad |
| **Delivery layers** | L2 (OCA `management-system` family) + L5 (custom) |
| **Custom modules** | `cd_qms_process`, `cd_checklist_authoring`, `cd_nonconformance`, `cd_capa`, `cd_internal_audit`, `cd_quality_analytics` |
| **Requirement range** | FR-QMS-001 … FR-QMS-048 |
| **Requirement count** | **48** *(measured; register estimate 32)* |
| **Effort estimate** | **21 person-weeks** *(measured; register estimate 16 PW)* |
| **Depends on** | M24 Document · M29 Identity · M28 Integration · M30 Platform Admin · M33 Party Master · M01 SRM · M21 Core HR |
| **Depended on by** | M01, M31, M02, M03, M04, M05, M06, M09, M12, M14, M15, M17, M18, M22, M34, M42, M45, M59, M60, M61, M25 · Portal **P11** |

> **Register note.** Measured scope exceeds the pre-specification estimate by 50% in
> requirements and 31% in effort. The increase is concentrated in checklist authoring and
> internal audit, both of which the estimate treated as configuration and which are in fact
> substantial build. `02-02` §3 must be restated when all four Category I specifications are
> complete.

---

## 2. Purpose

M23 is **the operating system of the management system**.

1000FiX is Bangladesh's only ISO 9001:2015 certified IT service provider. That certificate is
quoted in every corporate tender and is a precondition for several brand authorisations. It is
also an obligation: it requires documented processes, controlled records, measured performance,
investigated failures, verified corrective action, planned internal audits and a management
review that actually reviews something.

M23 makes those obligations mechanical rather than heroic. It owns the process register and
policies, authors the quality checklists that M01 and M31 execute, captures every
non-conformance from every source, drives root-cause analysis and corrective action to verified
effectiveness, plans and executes the internal audit programme, and assembles the management
review from live data rather than from a scramble of spreadsheets three weeks before the
surveillance visit.

It is deliberately **not** the enterprise risk and control module. That is M60. The category
overview draws the line: M23 asks *"is the work right, and are our processes improving?"*; M60
asks *"is the enterprise controlled, compliant and protected?"*

### Why It Exists

Today the QMS is a set of Word documents and a filing cabinet. ISO records are on paper.
Non-conformances are recorded when someone remembers. Root cause is a sentence written to close
a form. There is no CAPA effectiveness verification, so the same failure recurs and nobody
notices. The internal audit plan is completed manually, if at all. Rework — the single clearest
measure of quality in a repair business — is **unmeasured**.

The consequence is not merely administrative. The category risk register rates *"ISO
certification jeopardised during transition"* as **Critical**: an ERP programme that changes
every process while the QMS documentation stands still is precisely how a surveillance audit
produces a major non-conformance. M23 exists to keep the management system in step with the
business as the business changes, and to make the evidence a by-product of work rather than a
separate act of preparation.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.21 (BR-QMS-001…020) | Quality checklists, non-conformance, CAPA, audit, management review |
| ERP BRD §10.1 BRU-SRM-04, 17, 18 | QC gate before Ready; mandatory warranty evidence; independent QC above threshold |
| ERP URD §14 (US-QMS-*) | Quality manager and auditor user stories |
| Company Profile §Certifications | ISO 9001:2015 certification as a commercial differentiator |
| `_CATEGORY_OVERVIEW.md` §6 | Clause-by-clause coverage map; M23 is the module that *proves* compliance, not the one that does all of it |
| `_CATEGORY_OVERVIEW.md` §8, §10 | Category KPIs and the Critical certification risk |
| `04-00` P11 Field Auditor & Quality Application | Mobile audit execution, findings, CAPA verification, branch and seller audits |
| M01 §5.5, §12 | QC gate, rework detection and quality events raised into M23 |
| M09 §5.4 FR-WTY-048, §12 | Systemic claim-rejection causes escalated to M23 |
| M12 §5.4 FR-MKP-048 | Marketplace seller audits against platform standards |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** Both sides of every boundary must agree. Where this
> table assigns a capability to another module, that module's specification must claim it.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The quality policy, quality objectives and their cascade to measurable targets |
| 2 | The **process register** — every defined process, its owner, inputs, outputs, controls and interactions |
| 3 | Process maps, work instructions and their linkage to the ISO clause they satisfy |
| 4 | **Checklist and inspection-plan authoring** — templates, criteria, sampling, pass/fail logic, evidence requirements |
| 5 | Checklist applicability rules: which checklist applies to which device class, repair level, value band and delivery mode |
| 6 | Inspection points and quality gates declared to the executing modules |
| 7 | **Non-conformance management** — capture from every source, classification, severity, containment, disposition |
| 8 | Root-cause analysis: 5-Why, Ishikawa, and structured 8D for major and systemic failures |
| 9 | **Corrective and preventive action (CAPA)** — action planning, ownership, due dates, closure and **effectiveness verification** |
| 10 | Repeat-failure detection and escalation when the same root cause recurs |
| 11 | **Internal audit programme for processes** — annual plan, scope, auditor assignment, independence rules, execution, findings, closure *(control audits belong to M60; the two programmes are coordinated but separately owned)* |
| 12 | Audit checklist libraries by process, branch, workshop, supplier and marketplace seller |
| 13 | **Management review** — scheduled cycle, mandated ISO inputs assembled automatically, decisions, actions, minutes |
| 14 | Certification management: certificates held, scope, surveillance calendar, certification-body interaction, audit readiness |
| 15 | External audit hosting: brand-partner audits, customer audits, certification-body audits, findings and responses |
| 16 | Quality-event intake from operations: rework, QC failure, complaint-linked, claim-rejection, seller and supplier failures |
| 17 | Supplier and marketplace-seller quality: qualification criteria, performance thresholds, quality incidents *(execution shared with M42 and M12)* |
| 18 | **Cost of poor quality** — rework cost, scrap, warranty rejection, service credits, goodwill, attributed to cause |
| 19 | Quality risks and opportunities under ISO 9001 clause 6, and their escalation into M60's risk register |
| 20 | Statistical analysis: trend, Pareto, control limits and repeat-failure clustering |
| 21 | Quality KPI definition and instrumentation across the estate |
| 22 | Calibration status oversight — the QMS view of M45's calibration records for clause 7.1.5 |
| 23 | Competency oversight — the QMS view of M22's certification records for clause 7.2 |
| 24 | The P11 Field Auditor & Quality Application domain logic |
| 25 | The quality API and events consumed across the estate |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Enterprise risk register, internal control framework, control testing | **M60** GRC | Enterprise control answers to the Board; process quality answers to the certification body *(category overview §3)* |
| Compliance obligation register, legal matters, insurance, licences | **M60** GRC | — |
| Segregation-of-duties definition and testing | **M60** defines and tests; **M29** enforces | M23 neither defines nor enforces |
| Document storage, versioning, retention, disposal, legal hold | **M24** Document | M23 authors controlled documents; M24 controls them |
| E-signature envelopes | **M24** Document | — |
| Repair procedures, wiring diagrams, solution articles | **M61** Knowledge | Knowledge of *how to do it* is not a quality record *(category overview §4)* |
| Training courses, assessment and certification of employees | **M22** Competency | M23 states the competence requirement; M22 delivers and evidences it |
| Calibration execution and records | **M45** Enterprise Asset & Test Equipment | M23 sees the status; M45 owns the record |
| Checklist **execution** and its result | **M01** / **M31** / **M02** / **P11** | M23 defines and analyses; operations execute *(category boundary map)* |
| Customer-facing complaint handling and resolution communication | **M34** Customer Experience | M34 owns the customer relationship; M23 owns the underlying non-conformance |
| Safety incidents, investigations and occupational health | **M59** Health, Safety & Wellbeing | Safety is a separate discipline with separate statutory obligations |
| Environmental and e-waste compliance evidence | **M18** E-Waste & Circular Economy | M18 holds the certificates; M23 audits the process |
| Supplier scorecards and commercial performance | **M42** Supplier Relationship | M23 sets the quality criteria; M42 manages the relationship |
| Marketplace seller onboarding, scoring and consequence | **M12** Marketplace | M23 audits sellers; M12 acts commercially |
| KPI dashboards and business intelligence delivery | **M25** BI & Reporting | M23 defines quality KPIs; M25 renders them |
| Warranty claim processing | **M09** Warranty | M23 receives rejection-cause patterns |

### 3.3 Shared Concepts

| Concept | M23's Role | Owning Module |
|---|---|---|
| Checklist template | **Owner** | M23 |
| Checklist result | Consumes and analyses | M01 / M31 / M02 |
| Non-conformance | **Owner** | M23 |
| CAPA | **Owner** | M23 |
| Internal audit (process) | **Owner** | M23 |
| Internal audit (control) | Not owned | M60 |
| Management review | **Owner** | M23 |
| Controlled document | Authors and approves content; M24 controls the artefact | M23 (content) / M24 (control) |
| Quality risk | Identifies; escalates systemic exposure | M23 → M60 |
| Complaint | Owns the non-conformance behind it | M34 (customer relationship) |
| Rework | Consumes the detection; owns the analysis | M01 (detection) / M23 (analysis) |
| Calibration status | Reads for clause 7.1.5 | M45 |
| Competence evidence | Reads for clause 7.2 | M22 |
| Cost of poor quality | **Owner** of the measure; M54 owns cost accounting | M23 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP QM** — inspection plans, inspection lots, quality notifications, defect recording, **Nonconformance Management** (S/4HANA 1809+) and **system-based 8D** (S/4HANA 2020+) | Structured defect recording with images across all areas, escalating to a formal 8D problem-solving process for complex defects | **The two-tier model**: lightweight non-conformance capture everywhere, escalating to structured 8D only for major and systemic failures. This is the single most important design decision in the module — it is what stops a quality system collapsing under its own paperwork | SAP's inspection-lot and sampling-procedure machinery, which is built for manufacturing batch acceptance, not for one-off repairs |
| **SAP QM** — quality notification types | Different notification types for internal defect, customer complaint and supplier complaint | The **typed non-conformance** with a common core and type-specific fields | Notification-type proliferation |
| **IFS Quality Management** | Quality management integrated with service execution rather than bolted alongside it | **Quality events raised from the work itself**, not re-entered afterwards — the reason every operational module emits quality events into M23 | IFS's manufacturing quality depth |
| **Dedicated eQMS platforms** (ComplianceQuest, MasterControl, Qualio, Greenlight Guru class) | NC→CAPA workflow, root-cause tooling, effectiveness checks, audit management, management review, training linkage, validated document control | **CAPA effectiveness verification as a mandatory, separately-scheduled step**, and **audit management with independence rules**. Industry practice is unambiguous that a CAPA closed without effectiveness verification is not closed | Buying an eQMS: the licence cost breaches the zero-licence-cost principle, and integration of quality with service execution matters more here than validated-environment features designed for pharmaceutical regulation |
| **ISO 9001:2015 itself** | Clauses 4–10 | **Clause-by-clause traceability as a first-class feature** — every process, document, control and record declares the clause it satisfies, so audit readiness is queryable rather than assembled | Treating ISO as a documentation exercise separate from the operating system |
| **ISO 19011** — auditing management systems | Audit programme, competence of auditors, audit independence, evidence-based approach | **Auditor independence enforced by the system** — an auditor cannot audit their own area, mechanised rather than trusted | — |
| **8D / Ford problem-solving discipline** | D1–D8 with containment, root cause, permanent corrective action and verification | The **8D structure for major non-conformance**, including interim containment as a distinct, time-bound step | Mandatory 8D for every defect |
| **Odoo 19 + OCA `management-system` family** — `mgmtsystem`, `mgmtsystem_nonconformity`, `mgmtsystem_action`, `mgmtsystem_audit`, `mgmtsystem_review`, `mgmtsystem_quality`, `mgmtsystem_kpi`, `mgmtsystem_manual` | A genuine ISO 9001/14001/27001 management-system framework: non-conformity with cause analysis and immediate/preventive/corrective actions, audits, reviews, manual | **The whole family as the L2 base.** This is one of the strongest open-source fits in the entire programme — OCA `management-system` is purpose-built for ISO management systems and maps almost directly onto M23's core objects | Its assumption that document control lives inside the same modules — M24 owns document control here, and the bridge must be built |

**Design position.** 1000FiX differs from the benchmarks in five deliberate ways.

First, **the quality record is a by-product of the work, never a separate act**. A technician
completing a QC checklist on the P02 app is producing the ISO 8.6 release record, the warranty
evidence and the quality dataset in one action. Benchmarks that treat quality as a parallel
system guarantee that the parallel system falls behind reality — and a QMS that has fallen
behind reality is worse than none, because it produces false assurance at audit.

Second, **rework is the primary quality metric, and it is currently unmeasured**. Most quality
systems lead with defect rates from inspection. In a repair business the customer-visible truth
is whether the device comes back. M01 detects rework; M23 attributes it, analyses it and drives
it down. The company-wide target is **< 3%**, from an unmeasured baseline — meaning the first
job of M23 is honest measurement, and the first reported figure will be uncomfortable.

Third, **CAPA effectiveness verification is a hard gate, not a courtesy**. A CAPA moves to
Closed only after a scheduled verification confirms the failure has not recurred within a
declared observation window. The category risk register names the failure mode explicitly — *"quality
module becomes a document graveyard"* — and this is the control against it.

Fourth, **the management review assembles itself**. ISO 9001 clause 9.3 mandates specific
inputs: audit results, customer feedback, process performance, non-conformity and corrective
action status, monitoring results, external provider performance, resource adequacy, risk and
opportunity actions, and improvement opportunities. Every one of those exists in the ERP. M23
assembles the review pack automatically and refuses to schedule a review whose mandated inputs
are absent.

Fifth, **marketplace sellers and suppliers are audited to the same standard as owned
operations**. The company's quality exposure now extends beyond its own staff. M12's sellers and
M42's suppliers are inside the audit programme, using the same checklist engine and the same
finding and CAPA machinery.

---

## 5. Functional Areas & Features

### 5.1 Management System Framework

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-QMS-001 | Quality policy and objectives | Hold the quality policy and quality objectives with owners, targets, measurement basis, review cycle and approval history | P0 | L2 |
| FR-QMS-002 | Objective cascade | Cascade quality objectives to measurable targets by branch, workshop, process and role, and track attainment | P1 | L5 |
| FR-QMS-003 | Process register | Maintain every defined process with owner, purpose, inputs, outputs, interactions, controls, measures and the ISO clause it satisfies | P0 | L5 |
| FR-QMS-004 | Process map and work instruction | Attach process maps and work instructions, controlled through M24, with version and approval state visible from the process | P0 | L5 |
| FR-QMS-005 | Clause traceability | Map every process, controlled document, control, record type and audit to the ISO 9001:2015 clause (and ISO 27001 control) it satisfies, and report coverage and gaps | P0 | L5 |
| FR-QMS-006 | Interested parties and context | Record organisational context, interested parties and their requirements under clause 4, with review dates | P1 | L2 |
| FR-QMS-007 | Quality risks and opportunities | Record clause 6 risks and opportunities with treatment actions, and escalate systemic exposures into M60's risk register | P1 | L5 |
| FR-QMS-008 | Certification register | Hold certificates (ISO 9001, ISO 27001, brand authorisations relevant to quality) with scope, validity, certification body and surveillance calendar | P0 | L5 |
| FR-QMS-009 | Audit readiness dashboard | Report readiness for a named audit: clause coverage, open findings, overdue CAPAs, missing records, calibration and competence gaps | P0 | L5 |
| FR-QMS-010 | Change impact on the QMS | On any registered process change, require assessment of QMS impact and update of affected documents, checklists and training before the change is released | P0 | L5 |

### 5.2 Checklists, Inspection Plans & Quality Gates

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-QMS-011 | Checklist authoring | Author checklist templates with sections, items, response types, acceptance criteria, evidence requirements, conditional logic and scoring | P0 | L5 |
| FR-QMS-012 | Checklist versioning and approval | Version every template, require approval before release, and bind an executed checklist permanently to the version used | P0 | L5 |
| FR-QMS-013 | Applicability rules | Declare which checklist applies by device category, brand, repair level, value band, delivery mode, branch and customer type | P0 | L5 |
| FR-QMS-014 | Quality gate declaration | Declare which lifecycle transitions in M01, M31 and M02 are gated by a passed checklist, and publish the gate to those modules | P0 | L5 |
| FR-QMS-015 | Independent inspection rule | Declare where a second person must perform the inspection, by value or risk threshold, and publish it for enforcement *(BRU-SRM-18, SOD-07)* | P0 | L5 |
| FR-QMS-016 | Evidence requirements | Declare the mandatory evidence per checklist item — photograph, measurement, reading, signature — and its capture constraints | P0 | L5 |
| FR-QMS-017 | Sampling plans | Define sampling rules where 100% inspection is disproportionate, with the basis recorded | P2 | L5 |
| FR-QMS-018 | Checklist result intake | Receive executed checklist results from every executing module and portal, and retain them as quality records | P0 | L5 |
| FR-QMS-019 | Failure routing | Route a failed checklist item automatically to a non-conformance where the item is classified as reportable | P0 | L5 |
| FR-QMS-020 | Checklist analytics | Analyse pass rates, failing items, failure clusters by technician, branch, model and template version | P1 | L5 |

### 5.3 Non-Conformance & Root Cause

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-QMS-021 | Multi-source capture | Capture non-conformances from QC failure, rework detection, customer complaint, internal audit, external audit, brand claim rejection, supplier failure, marketplace seller failure, safety near-miss referral and direct staff report | P0 | L2 |
| FR-QMS-022 | Typed non-conformance | Type each non-conformance (internal, customer, supplier, seller, audit, systemic) with a common core and type-specific fields | P0 | L2 |
| FR-QMS-023 | Classification and severity | Classify by category, severity and ISO clause affected, and derive the required response path from that classification | P0 | L5 |
| FR-QMS-024 | Immediate containment | Record interim containment action with owner and deadline, distinct from corrective action, and track it to completion | P0 | L2 |
| FR-QMS-025 | Disposition of nonconforming output | Record the disposition — rework, repair, regrade, scrap, return, concession — with approval where required *(clause 8.7)* | P0 | L5 |
| FR-QMS-026 | Root-cause tooling | Provide 5-Why and Ishikawa tooling with structured capture, and require root cause to be distinguished from symptom | P0 | L5 |
| FR-QMS-027 | 8D for major failures | Run a structured 8D process for major and systemic non-conformances, with all eight disciplines tracked and evidenced | P1 | L5 |
| FR-QMS-028 | Repeat-failure detection | Detect the same root cause recurring within a declared window across any source, and escalate automatically | P0 | L5 |
| FR-QMS-029 | Attribution | Attribute a non-conformance to process, person, supplier, seller, model, part or training gap, with the basis recorded | P1 | L5 |
| FR-QMS-030 | Cost of poor quality | Compute the cost of each non-conformance — rework labour and parts, scrap, logistics, claim rejection, service credit, goodwill — and aggregate by cause | P1 | L5 |
| FR-QMS-031 | Non-conformance from the field | Allow any employee to raise a non-conformance from mobile in Bengali, in under 60 seconds, with photographic evidence | P1 | L5 |

### 5.4 CAPA

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-QMS-032 | CAPA creation | Create corrective and preventive actions from a non-conformance, an audit finding, a management review decision, a risk treatment or a trend | P0 | L2 |
| FR-QMS-033 | Action planning | Break a CAPA into actions with owner, due date, dependency, resource and expected outcome | P0 | L2 |
| FR-QMS-034 | CAPA workflow | Enforce the CAPA lifecycle with named guards from raised through analysis, planning, implementation, verification and closure | P0 | L5 |
| FR-QMS-035 | **Effectiveness verification** | Schedule a mandatory effectiveness check a declared interval after implementation, evaluate recurrence within an observation window, and refuse closure without a passed verification | P0 | L5 |
| FR-QMS-036 | Failed verification handling | On failed verification, reopen the CAPA, escalate its severity and require a revised root-cause analysis | P0 | L5 |
| FR-QMS-037 | Cross-module action execution | Raise the resulting work in the owning module — training in M22, document change in M24, process change in M23, control change in M60, supplier action in M42, seller action in M12 — and track it to completion there | P1 | L5 |
| FR-QMS-038 | Overdue escalation | Escalate overdue CAPA actions through owner, manager and Quality Manager on a declared schedule | P0 | L5 |
| FR-QMS-039 | CAPA analytics | Report CAPA volume, cycle time, on-time closure, effectiveness pass rate and repeat-cause rate | P0 | L5 |

### 5.5 Internal & External Audit

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-QMS-040 | Audit programme | Maintain the annual internal audit plan covering every process, branch, workshop, supplier class and seller class at its declared frequency | P0 | L2 |
| FR-QMS-041 | Auditor competence and independence | Maintain the auditor register with competence evidence from M22, and block assignment of an auditor to their own area or their own prior work | P0 | L5 |
| FR-QMS-042 | Audit execution | Execute audits from the P11 mobile application, offline, against a checklist, capturing observations, evidence and clause references | P0 | L5 |
| FR-QMS-043 | Findings | Raise findings classified as major non-conformity, minor non-conformity, observation or opportunity for improvement, each linked to the clause and the evidence | P0 | L2 |
| FR-QMS-044 | Auditee acknowledgement | Capture the auditee's acknowledgement signature on device at closing, and issue the report from the device | P1 | L5 |
| FR-QMS-045 | External audit hosting | Manage certification-body, brand-partner and customer audits: scope, schedule, evidence requests, findings, responses, closure and follow-up | P0 | L5 |
| FR-QMS-046 | Evidence request fulfilment | Assemble and release the evidence an external auditor requests, through M24, with an access log and a release approval | P0 | L5 |
| FR-QMS-047 | Management review | Schedule the review cycle, assemble every ISO 9001 clause 9.3 mandated input automatically, refuse to convene without them, and record decisions, actions and minutes as controlled records | P0 | L2 |
| FR-QMS-048 | Quality analytics and reporting | Provide trend, Pareto and control-limit analysis over non-conformance, rework, checklist failure, complaint and audit data, by every operational dimension | P0 | L5 |

*(Full requirement text is mirrored in `05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md`.)*

---

## 6. Technical Functions

Engineering behaviours the module must exhibit. Not user-visible; decisive for audit
defensibility.

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Template version binding** | An executed checklist binds permanently to the template version used. A later template change never alters a historical record — the difference between a defensible record and a worthless one |
| T-02 | **Append-only quality records** | Non-conformances, findings, CAPA decisions and verification outcomes are append-only. Correction is a new entry with a reason, never an overwrite |
| T-03 | **Evidence by reference with hashing** | Evidence artefacts live in M24 and are referenced with a content hash, so tampering is detectable and storage is not duplicated |
| T-04 | **Independence enforced in data** | Auditor-to-scope independence and inspector-to-technician separation are evaluated at assignment time against organisational data, not by policy reminder |
| T-05 | **Gate publication** | Quality gates are published as configuration consumed by M01, M31 and M02; the executing module enforces, M23 declares. No duplicated rule logic |
| T-06 | **Event-driven intake** | Every quality event arrives through the outbox from its source module; M23 never polls and never scrapes another module's tables |
| T-07 | **Idempotent event handling** | A redelivered rework or QC-failure event produces exactly one non-conformance |
| T-08 | **Scheduled verification engine** | Effectiveness verifications are scheduled at CAPA implementation and fire independently of anyone remembering; the scheduler is restartable and never silently drops one |
| T-09 | **Offline audit capability** | P11 audits execute fully offline for a working day, with idempotent replay and no evidence loss on reconnection |
| T-10 | **Clause index** | Clause coverage is a queryable index, not a document. "Show me the evidence for clause 8.5.1" resolves in under two seconds |
| T-11 | **Retention alignment** | ISO management-system records are retained for three certification cycles under M24's schedule, and cannot be disposed while a certificate is live |
| T-12 | **Statistical correctness** | Control limits, Pareto ranking and trend significance are computed with declared methods and stated sample sizes; no chart is published without its n |
| T-13 | **Localisation** | Checklists, findings and non-conformance capture are complete in Bengali, including on the mobile audit and technician surfaces |
| T-14 | **Audit trail of the auditor** | Every action within M23 is itself audited — who changed a template, who closed a CAPA, who signed a review — because the QMS is the first thing an external auditor tests |
| T-15 | **Performance envelope** | Checklist template resolution ≤ 150 ms p95 · non-conformance creation ≤ 500 ms p95 · audit readiness dashboard ≤ 3 s · management review pack assembly ≤ 60 s |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M23 |
|---|---|---|
| **Quality Manager** | Spends the month before a surveillance audit assembling paper | Sees audit readiness live, with clause coverage, open findings and missing records named |
| **Technician** | Ticks a paper checklist that nobody reads | Completes the checklist on the app; failures route themselves; the record is the evidence |
| **Workshop supervisor** | Knows which technician "has problems" by impression | Sees checklist failure and rework attribution on evidence |
| **Branch manager** | Learns of a quality problem when a customer escalates | Sees non-conformance and CAPA status for the branch, and is escalated to before it becomes a complaint |
| **Internal auditor** | Carries paper checklists and types the report afterwards | Audits offline on P11, captures evidence in place, issues the report and signature on the day |
| **Warranty officer** | Sees claims rejected for reasons nobody investigates | Systemic rejection causes become non-conformances with owners |
| **Operations Director** | Cannot say what poor quality costs | Sees cost of poor quality attributed to cause, monthly |
| **Brand partner auditor** | Is handed a folder | Is given a scoped evidence pack, logged and released under approval |
| **CEO** | Trusts that the certificate is safe | Sees the readiness position and the open major findings |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Protection of ISO 9001 certification** | Live clause coverage, controlled documents in step with process change, verified CAPA, completed audit programme | **Zero major non-conformances at surveillance** *(category KPI)*. The certificate is quoted in every corporate tender; its loss would remove 1000FiX from institutional bidding entirely |
| **Rework reduction** | Rework becomes measured, attributed and driven by CAPA to verified effectiveness | Company-wide rework **< 3%** *(category KPI)*. Each percentage point avoided is roughly 1% of job volume not redone. **The monetary value cannot be stated until the baseline is measured in Wave 2** — no figure should enter the business case before then *(consistent with M01 §7.2)* |
| **First-time fix improvement** | Checklist discipline, failure analysis and knowledge feedback into M61 | Supports the M01 first-time-fix target of **88%** |
| **Warranty claim acceptance** | Systemic rejection causes investigated and corrected rather than absorbed | Protects the **BDT 100 lac/year** warranty recovery owned by M09 by removing recurring rejection causes |
| **Cost of poor quality visibility** | Rework, scrap, claim rejection, service credits and goodwill attributed to cause | Converts an invisible cost into a managed one; the first credible COPQ figure the company will have |
| **Corporate tender eligibility** | Demonstrable, evidenced quality system with traceability | A precondition for the corporate and government growth the business plan assumes |
| **Brand authorisation retention** | Passing brand-partner quality audits with evidence | Protects revenue streams 1 and 4 in their entirety, alongside M40's authorisation management |

> **Discipline note.** M23 is a protective and enabling module. Its dominant benefit is
> **avoided loss** — of certification, of authorisations, of tender eligibility — not incremental
> revenue. Avoided-loss benefits are real but must not be double-counted against the revenue
> lines they protect, and none is claimed as new revenue here.

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Evidence replaces opinion** | Disputes about whether work was done properly are settled by record, not by seniority. This changes how the organisation argues with itself |
| **Fair attribution** | Technicians are measured on evidence rather than impression, which is a precondition for the performance and incentive schemes in M57 |
| **Systemic learning** | Root cause distinguished from symptom, and repeat-cause detection, mean the organisation stops solving the same problem repeatedly |
| **Defensibility** | A regulator, a brand partner, a court or a customer can be shown exactly what was checked, by whom, against which version of which standard |
| **Continuity through change** | An ERP programme rewrites every process. A QMS that changes in step is the only way certification survives the transition |
| **Extension of standards beyond the payroll** | Auditing 500 marketplace sellers and the supplier base to the same standard raises quality across a market, not just a company |
| **A basis for improvement culture** | Improvement that is measured, verified and visible is repeatable; improvement that is asserted is not |

---

## 8. Lifecycle & State Model

M23 owns three lifecycles. **Non-conformance → CAPA** is shown in full because it carries the
module's purpose.

### 8.1 Non-Conformance

```
              ┌──────────┐
              │  RAISED  │ from QC failure, rework, complaint, audit,
              └────┬─────┘ claim rejection, supplier/seller, or staff report
                   │ triage: classify, severity, clause
              ┌────▼──────────┐
              │   TRIAGED     │──── not a non-conformance ──► REJECTED (reason)
              └────┬──────────┘
                   │ severity requires containment
              ┌────▼──────────┐
              │  CONTAINED    │ interim action recorded, owner, deadline
              └────┬──────────┘
                   │ disposition of nonconforming output decided (clause 8.7)
              ┌────▼──────────┐
              │ INVESTIGATING │ 5-Why / Ishikawa; 8D if major or systemic
              └────┬──────────┘
                   │ root cause established and distinguished from symptom
              ┌────▼──────────┐
              │  CAPA RAISED  │────────────────────────┐
              └────┬──────────┘                        │
                   │ no CAPA required (isolated,       │
                   │ contained, justified)             │
              ┌────▼──────────┐                        │
              │    CLOSED     │◄───────────────────────┘ CAPA verified effective
              └───────────────┘

  Cross-cutting: REPEAT flag set automatically when the same root cause recurs
  within the declared window; a repeat escalates severity and forces management
  review attention (category risk mitigation).
```

### 8.2 CAPA

```
   RAISED ──► ANALYSIS ──► PLANNED ──► IN IMPLEMENTATION ──► IMPLEMENTED
                                                                  │
                                        (verification scheduled at implementation)
                                                                  ▼
                                                        ┌──────────────────┐
                                                        │ AWAITING         │
                                                        │ VERIFICATION     │
                                                        └────────┬─────────┘
                                                                 │ observation window elapsed
                                                        ┌────────▼─────────┐
                                                        │   VERIFICATION   │
                                                        └────────┬─────────┘
                                          ┌──────────────────────┴─────────┐
                                    passed│                                │failed
                                    ┌─────▼─────┐                   ┌──────▼───────┐
                                    │  CLOSED   │                   │  REOPENED    │
                                    │ EFFECTIVE │                   │ severity ↑,  │
                                    └───────────┘                   │ re-analyse   │
                                                                    └──────┬───────┘
                                                                           └──► ANALYSIS

   A CAPA can never reach Closed without a passed verification (BRU-QMS-05).
```

### 8.3 Internal Audit

```
PLANNED ──► SCHEDULED ──► AUDITOR ASSIGNED (independence check) ──► IN PROGRESS
IN PROGRESS ──► FINDINGS RAISED ──► REPORT ISSUED (auditee acknowledged)
REPORT ISSUED ──► FINDINGS IN CAPA ──► FOLLOW-UP VERIFIED ──► CLOSED
```

### Transition Guards

| From | To | Guard | Actor |
|---|---|---|---|
| Raised | Triaged | Classification, severity and affected clause assigned | Quality Officer |
| Triaged | Contained | Severity requires containment; interim action, owner and deadline recorded | Quality Officer, line manager |
| Any | Investigating | Investigation owner assigned; method selected (5-Why, Ishikawa, 8D) | Quality Manager |
| Investigating | CAPA Raised | Root cause established and explicitly distinguished from symptom | Quality Manager |
| Investigating | Closed | No CAPA required — isolated, contained, and the justification recorded and approved | Quality Manager |
| Raised | In Implementation *(CAPA)* | Actions planned with owners, dates and expected outcomes | Action owners |
| In Implementation | Implemented | All actions complete with evidence | Action owners |
| Implemented | Awaiting Verification | Verification scheduled with observation window and criteria | System |
| Awaiting Verification | Verification | Observation window elapsed | System |
| Verification | Closed Effective | No recurrence within the window; verifier ≠ action owner | Quality Manager |
| Verification | Reopened | Recurrence observed or criteria unmet; severity escalated | Quality Manager |
| Planned | Auditor Assigned | Auditor competent per M22 **and** independent of the scope | Quality Manager |
| Findings Raised | Report Issued | Auditee acknowledgement captured | Auditor + auditee |
| — | Management Review convened | All clause 9.3 mandated inputs present | Quality Manager |

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-QMS-01 | An order cannot reach Ready without a passed quality checklist *(BRU-SRM-04; declared here, enforced in M01/M31)* | **H** | Quality Manager |
| BRU-QMS-02 | Independent QC by a second person is mandatory above the declared value or risk threshold *(BRU-SRM-18, SOD-07)* | **H** | Quality Manager |
| BRU-QMS-03 | An executed checklist binds permanently to the template version used; a template change never alters a historical record | **H** | CTO |
| BRU-QMS-04 | Root cause must be recorded and explicitly distinguished from symptom before a CAPA may be raised | **H** | Quality Manager |
| BRU-QMS-05 | A CAPA cannot be closed without a passed effectiveness verification | **H** | Quality Manager |
| BRU-QMS-06 | The person who performed a CAPA action cannot verify its effectiveness | **H** | Quality Manager |
| BRU-QMS-07 | An auditor may not audit their own area, their own prior work, or a process they own | **H** | Quality Manager |
| BRU-QMS-08 | A management review cannot be convened without every ISO 9001 clause 9.3 mandated input present | **H** | Quality Manager |
| BRU-QMS-09 | The same root cause recurring within the declared window escalates severity automatically and is tabled at management review | **C** | Quality Manager |
| BRU-QMS-10 | Every registered process change requires a QMS impact assessment before release; affected documents, checklists and training must be updated first | **H** | Quality Manager |
| BRU-QMS-11 | Quality records are append-only; corrections are new entries with a reason and never overwrite | **H** | CTO |
| BRU-QMS-12 | Nonconforming output requires a recorded disposition with approval where the classification demands it *(clause 8.7)* | **H** | Quality Manager |
| BRU-QMS-13 | ISO management-system records are retained for three certification cycles and cannot be disposed while a certificate is live | **H** | Quality Manager |
| BRU-QMS-14 | A major non-conformance requires containment within the declared interval and an 8D investigation | **H** | Quality Manager |
| BRU-QMS-15 | Evidence released to an external auditor requires a release approval and is logged | **H** | Quality Manager |
| BRU-QMS-16 | A quality risk assessed as a systemic enterprise exposure is escalated into M60's risk register and cannot be closed in M23 alone | **H** | Quality Manager / CFO |
| BRU-QMS-17 | Marketplace sellers and suppliers are audited against the same standards as owned operations | **H** | Quality Manager |
| BRU-QMS-18 | A CAPA action owned by another module is not complete until that module records its completion | **C** | Quality Manager |
| BRU-QMS-19 | An overdue CAPA escalates on the declared schedule and cannot be silently extended; extension requires approval and a reason | **A** | Quality Manager |
| BRU-QMS-20 | No published quality statistic omits its sample size and method | **H** | Quality Manager |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.qms.process` | `fix_qms_process` | Process register | code, name, owner_id, purpose, inputs, outputs, interactions, controls, measures, clause_refs, state, review_due |
| `fix.qms.policy` | `fix_qms_policy` | Policy and objectives | type, statement, owner_id, approved_by, version, effective_from, review_cycle, document_id |
| `fix.qms.objective` | `fix_qms_objective` | Quality objectives and cascade | policy_id, parent_id, scope, target, measure_ref, owner_id, period, attainment |
| `fix.qms.clause.map` | `fix_qms_clause_map` | Clause traceability index | standard, clause, subject_type, subject_id, evidence_ref, coverage_state |
| `fix.qms.certificate` | `fix_qms_certificate` | Certification register | standard, scope, body, number, issued_at, expires_at, surveillance_dates, document_id, state |
| `fix.checklist.template` | `fix_checklist_template` | Checklist definitions | code, name_bn, name_en, type, version, state, approved_by, scoring_rule, applicability_json |
| `fix.checklist.item` | `fix_checklist_item` | Template items | template_id, section, sequence, text_bn, text_en, response_type, acceptance_criteria, evidence_required, reportable, conditional_json |
| `fix.checklist.result` | `fix_checklist_result` | Executed results (received) | template_id, template_version, subject_type, subject_id, executed_by, executed_at, outcome, item_results_json, evidence_refs |
| `fix.quality.gate` | `fix_quality_gate` | Declared gates | module, object_type, from_state, to_state, template_id, independence_required, threshold_json |
| `fix.nonconformance` | `fix_nonconformance` | Non-conformance record | number, type, source, source_ref, raised_by, raised_at, category, severity, clause_ref, state, repeat_of_id, cost_of_quality, owner_id |
| `fix.nc.containment` | `fix_nc_containment` | Interim containment | nc_id, action, owner_id, due_at, completed_at, evidence_ref |
| `fix.nc.disposition` | `fix_nc_disposition` | Clause 8.7 disposition | nc_id, disposition, quantity, approved_by, justification, at |
| `fix.rca` | `fix_rca` | Root-cause analysis | nc_id, method (5why/ishikawa/8d), structure_json, root_cause, symptom, contributing_factors, completed_by, completed_at |
| `fix.eight.d` | `fix_eight_d` | 8D record | nc_id, team_ids, d1…d8_json, state, champion_id |
| `fix.capa` | `fix_capa` | CAPA record | number, source_type, source_id, type (corrective/preventive), description, owner_id, state, raised_at, due_at, closed_at, effectiveness_state |
| `fix.capa.action` | `fix_capa_action` | CAPA actions | capa_id, sequence, description, owner_id, executing_module, external_ref, due_at, completed_at, evidence_ref, state |
| `fix.capa.verification` | `fix_capa_verification` | Effectiveness verification | capa_id, scheduled_at, observation_window_days, criteria, verified_by, verified_at, outcome, evidence_ref |
| `fix.audit.programme` | `fix_audit_programme` | Annual plan | year, scope_json, frequency_rules_json, approved_by, state |
| `fix.audit` | `fix_audit` | Audit instance | programme_id, type (internal/external), standard, scope, auditee_type, auditee_id, auditor_ids, planned_at, executed_at, state, report_document_id |
| `fix.audit.finding` | `fix_audit_finding` | Findings | audit_id, classification (major/minor/observation/OFI), clause_ref, statement, evidence_refs, owner_id, capa_id, state, closed_at |
| `fix.auditor` | `fix_auditor` | Auditor register | employee_id, standards, competence_ref, independence_exclusions_json, active |
| `fix.management.review` | `fix_management_review` | Review record | period, scheduled_at, held_at, attendees, inputs_json, decisions_json, actions_ids, minutes_document_id, state |
| `fix.quality.event` | `fix_quality_event` | Raw intake ledger | source_module, event_type, source_ref, payload_json, received_at, processed_state, nc_id |
| `fix.copq` | `fix_copq` | Cost of poor quality | nc_id, cost_type, amount, source_module, source_ref, attributed_cause, period |
| `fix.quality.risk` | `fix_quality_risk` | Clause 6 risks and opportunities | description, type, process_id, likelihood, impact, treatment, owner_id, escalated_to_grc_ref, review_due |

### 10.2 Referenced Entities

| Entity | Owned By | Access Pattern |
|---|---|---|
| `fix.document`, versions, retention, legal hold | M24 | Service call; evidence by reference |
| `fix.service.order`, QC result, rework link | M01 | Event intake + live read |
| `fix.repair.order`, bench evidence | M31 | Event intake |
| `fix.work.order`, field evidence | M02 | Event intake |
| `fix.employee`, org structure, position | M21 | Live read — independence and ownership |
| `fix.competency`, competence records | M22 | Live read — clause 7.2 and auditor competence |
| `fix.calibration.record` | M45 | Live read — clause 7.1.5 |
| `fix.complaint` | M34 | Event intake |
| `fix.brand.claim` rejection causes | M09 | Event intake |
| `fix.supplier.profile`, scorecards | M42 | Live read + event |
| `fix.seller`, scores, audits | M12 | Live read + event |
| `fix.risk` (enterprise register) | M60 | Escalation target |
| `fix.knowledge.article` | M61 | Bidirectional reference |
| `fix.incident.investigation` (safety) | M59 | Referral only |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-QMS-01 | QC checklist failed in M01/M31/M02 | Create a non-conformance where the failed item is classified reportable; attach evidence by reference | Queue the event; alert the Quality Officer if unprocessed after 1 hour |
| AUT-QMS-02 | Rework detected in M01 | Create a non-conformance with attribution to the original order, technician, branch and fault code | Queue; alert |
| AUT-QMS-03 | Customer complaint classified as a quality failure in M34 | Create a non-conformance linked to the complaint, without duplicating the customer conversation | Queue; alert |
| AUT-QMS-04 | Brand claim rejected for a quality-related cause in M09 | Create or increment a non-conformance for that cause | Queue; alert |
| AUT-QMS-05 | Non-conformance triaged as major | Start the containment clock, require an 8D, and notify the Quality Manager and process owner | Escalate to Operations Director |
| AUT-QMS-06 | Same root cause recurs within the declared window | Set the repeat flag, escalate severity, notify the process owner and table it for management review | Log; repeat |
| AUT-QMS-07 | Root cause established | Prompt CAPA creation with the analysis attached; block closure without either a CAPA or an approved no-CAPA justification | — |
| AUT-QMS-08 | CAPA implemented | Schedule the effectiveness verification at the declared interval with its observation window and criteria | Block CAPA progression; alert |
| AUT-QMS-09 | Verification window elapsed | Evaluate recurrence within the window, assign the verification task to a verifier who is not an action owner | Escalate to the Quality Manager |
| AUT-QMS-10 | Verification failed | Reopen the CAPA, escalate severity, require revised root-cause analysis, notify management | — |
| AUT-QMS-11 | CAPA action overdue | Escalate to owner, then line manager, then Quality Manager on the declared schedule | Repeat escalation |
| AUT-QMS-12 | Audit due per the programme | Create the audit, propose competent and independent auditors, and notify the auditee | Escalate to the Quality Manager |
| AUT-QMS-13 | Auditor assignment breaches independence | Block the assignment and propose alternatives | — |
| AUT-QMS-14 | Audit report issued | Convert findings to CAPAs, assign owners, set due dates by classification | Create a manual conversion task |
| AUT-QMS-15 | Management review due | Assemble every clause 9.3 mandated input, produce the review pack, and block scheduling if any input is missing | Alert the Quality Manager with the missing list |
| AUT-QMS-16 | Certificate surveillance date approaching (T−120, T−60, T−30 days) | Produce the readiness assessment and escalate open majors and overdue CAPAs to the CEO | Repeat escalation |
| AUT-QMS-17 | Process change registered in M23 or M30 | Require a QMS impact assessment and block release until affected documents, checklists and training are updated | Block the change; escalate |
| AUT-QMS-18 | Non-conformance closed | Compute and post the cost of poor quality from the linked operational records | Flag for manual costing |
| AUT-QMS-19 | Quality risk assessed as systemic enterprise exposure | Create the linked risk in M60 and prevent closure in M23 until M60 accepts it | Escalate to CFO |
| AUT-QMS-20 | Supplier or seller quality threshold breached | Raise a non-conformance and notify M42 or M12 for commercial consequence | Queue; alert |

---

## 12. Interfaces

### 12.1 Upstream — M23 Consumes

| Source | What | Mechanism |
|---|---|---|
| M01 SRM | QC results, rework detection, quality events, job cost for COPQ | Events `service_order.qc_failed`, `rework.detected` + REST |
| M31 Workshop · M02 Field Service | Bench and field checklist results, evidence | Events |
| M34 Customer Experience | Complaints classified as quality failures | Event `complaint.quality_classified` |
| M09 Warranty | Claim rejection causes and failure patterns | Events |
| M42 Supplier · M12 Marketplace | Supplier and seller quality failures and audit outcomes | Events |
| M21 Core HR | Organisational structure, employment status, ownership | Live read |
| M22 Competency | Auditor and technician competence evidence (clause 7.2) | Live read |
| M45 Enterprise Asset | Calibration status of test equipment (clause 7.1.5) | Live read |
| M24 Document | Controlled documents, versions, approval state, evidence storage | Service call |
| M59 Health & Safety | Safety near-misses referred where a quality process is implicated | Event |
| M18 E-Waste | Disposal compliance evidence for audit | Live read |
| M30 Platform Admin | Branch, workshop and process configuration; registered changes | Configuration read + events |
| M25 BI | Monitoring and measurement results for clause 9.1 inputs | Warehouse read |

### 12.2 Downstream — M23 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M01 SRM · M31 · M02 | Checklist templates, applicability rules, quality gates, independence rules | Master data projection |
| P11 Field Auditor App | Audit checklists, findings, CAPA verification, branch and seller audit execution | REST |
| M22 Competency | Training needs arising from CAPA and audit findings | Command |
| M24 Document | Controlled-document change requests arising from CAPA | Command |
| M60 GRC | Systemic quality exposures escalated as enterprise risks; process-control weaknesses | Command + projection |
| M61 Knowledge | Failure patterns and verified fixes worth documenting as articles | Events |
| M42 Supplier · M12 Marketplace | Quality findings requiring commercial consequence | Events |
| M34 Customer Experience | Non-conformance status behind a complaint | REST |
| M57 Performance | Quality attribution feeding technician performance *(summary only)* | Projection |
| M09 Warranty | Evidence-standard definitions and quality confirmation for claims | Projection |
| M25 BID · M26 AIM | Quality fact stream: NC, CAPA, audit, checklist, COPQ | Warehouse extract |
| P08 Brand Partner Portal | Quality performance and CAPA responses for the brand's own audits | REST via M09 |
| Executive dashboards | Audit readiness, open majors, COPQ | Projection |

### 12.3 Domain Events Published

| Event | Payload Summary | Principal Consumers |
|---|---|---|
| `quality.nc_raised` | nc id, type, source, severity, clause, subject | M60, M34, M42, M12, M25 |
| `quality.nc_major` | nc id, containment deadline, process owner | Executive alerting, M60 |
| `quality.repeat_cause_detected` | root cause, occurrences, window, affected scope | M60, M25, management review |
| `quality.capa_raised` | capa id, source, owner, due | M22, M24, M42, M12 |
| `quality.capa_action_assigned` | action id, executing module, owner, due | M22, M24, M60 |
| `quality.capa_verified` | capa id, outcome, verifier | M25, M60 |
| `quality.capa_failed_verification` | capa id, reason, escalated severity | Executive alerting, M60 |
| `quality.audit_finding_raised` | finding id, classification, clause, auditee | M42, M12, M60 |
| `quality.audit_completed` | audit id, findings summary, auditee | M25, M60 |
| `quality.management_review_held` | period, decisions, actions | M60, M25, executive |
| `quality.gate_definition_changed` | gate, module, template version | M01, M31, M02 |
| `quality.checklist_template_released` | template id, version, applicability | M01, M31, M02, P11 |
| `quality.certificate_at_risk` | certificate, cause, days to surveillance | CEO, CCO alerting |
| `quality.copq_posted` | nc id, cost type, amount, cause | M54, M25 |
| `quality.ncr_raised` | NCR id, source document, part or operation implicated, severity, containment state | M37, M15, M42, M31, M60 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-QMS-01 | Certification body (ISO 9001 / ISO 27001) | Bidirectional (document) | Surveillance scheduling, audit reports, non-conformity responses, certificate issue |
| INT-QMS-02 | Brand partner audit programmes | Bidirectional | Audit scheduling, evidence release, CAPA responses *(surface shared with P08)* |
| INT-QMS-03 | Corporate customer audit requests | Inbound | Customer-initiated quality audits and evidence packs |
| INT-QMS-04 | Accreditation and standards references | Inbound | Current clause text and standard revisions |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/quality/checklists` | GET | Applicable checklist templates for a subject | M01, M31, M02, P02, P11 |
| `/api/v1/quality/checklists/results` | POST | Submit an executed checklist result | M01, M31, M02, P02, P11 |
| `/api/v1/quality/gates` | GET | Declared quality gates and independence rules | M01, M31, M02 |
| `/api/v1/quality/nonconformances` | GET/POST | Raise and query non-conformances | All modules, P03, P11 |
| `/api/v1/quality/nonconformances/{id}/rca` | POST | Record root-cause analysis | P03 |
| `/api/v1/quality/capas` | GET/POST | CAPA register and creation | P03, P11 |
| `/api/v1/quality/capas/{id}/verify` | POST | Record an effectiveness verification | P03, P11 |
| `/api/v1/quality/audits` | GET/POST | Audit programme and instances | P03, P11 |
| `/api/v1/quality/audits/{id}/findings` | POST | Raise findings with evidence | P11 |
| `/api/v1/quality/management-review/{period}` | GET | Assembled review pack | P03, P06 |
| `/api/v1/quality/clause-coverage` | GET | Clause coverage and gaps for a standard | P03, external auditor (scoped) |
| `/api/v1/quality/readiness` | GET | Audit readiness assessment | P03, P06 |
| `/api/v1/quality/copq` | GET | Cost of poor quality by cause and period | P03, P06 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R32 Quality Manager / ISO Coordinator | C R U D A | All — the module's principal owner |
| R05 Operations Director | R A | All — process ownership and major NC escalation |
| R02 Chief Technology Officer | R | All — clause coverage for ISO 27001 controls |
| R03 Chief Financial Officer | R | COPQ, systemic exposures escalating to M60 |
| R06 Branch Manager | C R U | Own branch — NCs, CAPAs, audit responses |
| R09 Workshop Supervisor | C R U | Own workshop |
| R07 Dispatch Manager | R | Assigned zones |
| R08 Service Centre Agent | C R | Own branch — raise NCs |
| R10 / R11 / R12 Technician | C R | Own jobs — execute checklists, raise NCs |
| R28 Warranty Claims Officer | C R | Claim-related quality causes |
| R17 Inventory Manager · R19 Procurement Officer | R U | Supplier quality findings |
| R24 Marketplace Operations Officer | R U | Seller quality findings |
| R30 HR Manager | R | Training needs from CAPA; competence evidence |
| R33 IT / System Administrator | R U | Configuration only |
| R38 External Party — brand partner / certification body / external auditor | R | **Scoped evidence release only**, under approval, logged *(EA-01, EA-10)* |
| — Quality Officer *(new position under R32)* | C R U | All operational quality records; cannot approve own CAPA verification |
| — Internal Auditor *(role, drawn from trained staff)* | C R U | Assigned audits only, subject to independence exclusions |

**Field-level restrictions.** Cost of poor quality at record level is visible to R01–R05, R26,
R27 and R32. Individual technician attribution is visible to R32, R05, the technician's own line
manager and the technician themselves; it is never exposed to any external portal.
`internal_note` is never exposed externally.

**Segregation of duties.** **SOD-07** — the technician who performed the repair cannot record the
independent QC above the threshold *(`05-04` §6, enforced in M01)*. **SOD-19** *(to be registered
in `05-04` §6)* — the person who performed a CAPA action cannot verify its effectiveness.
**SOD-20** — an auditor cannot audit their own area or their own prior work.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| Audit readiness dashboard | Quality Manager, CEO, Ops Director | Real time | Clause coverage, open majors, overdue CAPAs, missing records, calibration and competence gaps, days to surveillance |
| Non-conformance register and trend | Quality Manager, Ops Director | Weekly | NCs by type, source, severity, process, branch and model; trend against control limits |
| Pareto of failure causes | Quality Manager, Ops Director | Monthly | Ranked root causes by frequency and by cost, with the vital few identified |
| Rework analysis | Quality Manager, HR, Ops Director | Weekly | Rework rate by technician, branch, model, fault code and repair level *(shared definition with M01 §14)* |
| CAPA status and effectiveness | Quality Manager, CEO | Monthly | Open, overdue, closed, verification pass rate, repeat-cause rate |
| Repeat non-conformance register | Quality Manager, management review | Monthly | Same root cause recurring, with prior CAPA and why it failed |
| Internal audit programme status | Quality Manager, CEO | Monthly | Plan completion, findings by classification, closure ageing |
| External audit and certification status | CEO, Quality Manager, CCO | Per event | Findings, responses, closure, certificate validity and scope |
| Cost of poor quality | CFO, Ops Director, Quality Manager | Monthly | COPQ by cause, process, branch and category, trended |
| Checklist performance | Quality Manager, Workshop Supervisors | Weekly | Pass rates, most-failed items, template versions in use, execution compliance |
| Supplier and seller quality | Procurement, Marketplace Operations, Quality Manager | Monthly | Quality incidents, audit outcomes and CAPA status by external party |
| Management review pack | Executive team | Per review cycle | Every clause 9.3 mandated input, assembled with source references |
| Quality objectives attainment | Quality Manager, CEO | Quarterly | Objectives against target by scope, with variance explanation |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| KPI-C23-01 | ISO 9001 surveillance major non-conformances | unknown | 0 | **0** |
| KPI-C23-02 | CAPA closed on time | unmeasured | 88% | **> 95%** |
| KPI-C23-03 | CAPA effectiveness verified | unmeasured | 80% | **> 90%** |
| KPI-C23-04 | Repeat non-conformance from the same root cause | unmeasured | < 10% | **< 5%** |
| KPI-C23-05 | Internal audit plan completion | manual | 95% | **100%** |
| KPI-C23-06 | Rework rate (company-wide) | unmeasured | < 5% | **< 3%** |
| KPI-C23-07 | Non-conformances raised from the field (vs back-office only) | 0% | 40% | **> 60%** |
| KPI-C23-08 | Quality gates enforced without bypass | unknown | 100% | **100%** |
| KPI-C23-09 | Clause coverage with current evidence | unmeasured | 95% | **100%** |
| KPI-C23-10 | Management reviews held with all mandated inputs | unmeasured | 100% | **100%** |
| KPI-C23-11 | Median time from NC raised to root cause established | unmeasured | < 10 days | **< 5 days** |
| KPI-C23-12 | Audits completed on mobile rather than paper | 0% | 100% | **100%** |
| KPI-C23-13 | Cost of poor quality as a share of revenue | unmeasured | measured | **declining trend** |
| KPI-C23-14 | Suppliers and sellers audited to plan | 0% | 80% | **100%** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `mail`, `calendar`, `hr` linkage | 6% |
| L2 | OCA `mgmtsystem`, `mgmtsystem_nonconformity`, `mgmtsystem_action`, `mgmtsystem_audit`, `mgmtsystem_review`, `mgmtsystem_quality`, `mgmtsystem_kpi`, `mgmtsystem_manual` | 38% |
| L5 | `cd_qms_process`, `cd_checklist_authoring`, `cd_nonconformance`, `cd_capa`, `cd_internal_audit`, `cd_quality_analytics` | 56% |

> **Layer note.** The OCA `management-system` family is the strongest open-source fit in
> Category I and covers the non-conformity, action, audit and review objects directly. The
> custom build concentrates on what OCA does not provide: checklist authoring with applicability
> and gates, effectiveness verification scheduling, clause traceability, independence
> enforcement, and the cross-module event intake.

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-C23-01 | `cd_qms_process` — process register, policy and objectives, clause traceability index, certification register, readiness | Odoo module | 4 PW |
| CD-C23-02 | `cd_checklist_authoring` — template authoring, versioning, applicability rules, gate declaration, evidence requirements | Odoo module | 5 PW |
| CD-C23-03 | `cd_nonconformance` — multi-source intake, typing, containment, disposition, RCA tooling, 8D, repeat detection, COPQ | Odoo module | 5 PW |
| CD-C23-04 | `cd_capa` — CAPA lifecycle, cross-module action dispatch, verification scheduler, escalation | Odoo module + service | 3 PW |
| CD-C23-05 | `cd_internal_audit` — programme, independence engine, P11 mobile execution, findings, external audit hosting | Odoo module + service | 3 PW |
| CD-C23-06 | `cd_quality_analytics` — trend, Pareto, control limits, management review pack assembly | Odoo module | 1 PW |
| | | **Total** | **21 PW** |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M24 Document *(W3)*** | Controlled documents, evidence storage and retention are the substrate; a QMS without document control is not a QMS |
| M01 SRM *(W1–W2)* · M31 *(W2)* · M02 *(W2)* | Quality events originate there; checklists are executed there |
| M21 Core HR *(W5)* | Organisational structure drives ownership and auditor independence |
| M22 Competency *(W5)* | Auditor competence and clause 7.2 evidence — delivered in the same wave |
| M45 Enterprise Asset *(W5)* | Calibration status for clause 7.1.5 — delivered in the same wave |
| M34 Customer Experience *(W4)* | Complaint intake into non-conformance |
| M29 Identity · M28 Integration *(W1)* | Independence is identity; every intake is an event |

**Wave 5 gate condition.** The QMS must be demonstrably current with every process changed in
Waves 1–4 before the gate is passed. This is a substantial catch-up exercise and must be planned
as such — the category risk register rates certification jeopardy as **Critical**, and the
window between Wave 1 go-live and M23 delivery in Wave 5 is precisely where that risk lives.

> **Interim control, stated explicitly.** Between Wave 1 and Wave 5 the QMS remains on the
> current manual system while processes change underneath it. That gap is a live risk, not an
> accepted condition. The programme must maintain a manual QMS change log from Wave 1 and inform
> the certification body of the transition — a governance action outside this module's build,
> flagged here because M23 is the module that inherits the consequence.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| ISO 9001 documented procedures and work instructions | ~80–150 documents | `fix.qms.process` + M24 controlled documents | W5 |
| Paper QC checklists in use | ~30–60 variants | `fix.checklist.template` (after rationalisation) | W5 |
| Paper ISO records (audits, reviews, NCs, CAPAs) | 3 certification cycles | `fix.audit`, `fix.management.review`, `fix.nonconformance` (archive state) | W5 |
| Open CAPAs and audit findings | To be profiled | Live records | W5 |
| Certificates and surveillance history | ISO 9001 + ISO 27001 | `fix.qms.certificate` | W5 |

**Migration rule.** Historical ISO records migrate as **archive**: retrievable for the
certification body, excluded from KPI computation, and clearly marked. Only open CAPAs and open
findings migrate as live records, and each requires the Quality Manager's confirmation that it
is genuinely open. Checklist templates are **rationalised before migration, not after** — thirty
to sixty branch variants of the same inspection must become one governed set, and that is a
quality decision exercise with a Wave 4 lead time, not a data task.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every ISO 9001:2015 clause resolves to current evidence through the clause index in under two seconds | Clause-by-clause demonstration with the Quality Manager |
| AC-02 | An executed checklist remains bound to its template version after that template is revised | Version-boundary test |
| AC-03 | A quality gate cannot be bypassed in M01, M31 or M02 through UI, API or direct call | Negative test per module and per channel |
| AC-04 | Independent inspection above the threshold cannot be performed by the repairing technician | SOD-07 negative test |
| AC-05 | A CAPA cannot reach Closed without a passed effectiveness verification, by any route | Negative test via UI, API and ORM |
| AC-06 | The person who performed a CAPA action cannot verify its effectiveness | SOD-19 negative test |
| AC-07 | An auditor cannot be assigned to their own area or their own prior work | SOD-20 negative test |
| AC-08 | A repeat root cause within the window is detected automatically and escalates without human action | Scripted scenario across sources |
| AC-09 | A management review cannot be convened with a missing clause 9.3 input, and the missing input is named | Negative test |
| AC-10 | A field audit executes fully offline for a working day and synchronises with complete evidence integrity | Offline field test at a branch |
| AC-11 | A non-conformance can be raised from mobile in Bengali in under 60 seconds with photographic evidence | Timed observation, twenty samples |
| AC-12 | Quality events from all sources create exactly one non-conformance under duplicate delivery and retry | Chaos test with duplicated events |
| AC-13 | Cost of poor quality reconciles to the source operational cost records | Reconciliation report with M54 |
| AC-14 | Named business super-users — including the Quality Manager and at least two branch managers — sign off UAT for all P0 and P1 requirements | Signed UAT record |
| AC-15 | Zero critical or high security findings, with particular attention to scoped external-auditor evidence release | Security review record |

**Definition of done:** all 17 criteria in `02-02` §8 plus the criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Has the certification body been formally informed of the ERP programme, and does the transition require a scope change or an extraordinary audit? | Quality Manager / CEO | **W3 — blocking for the Critical risk** |
| Q-02 | Who maintains the manual QMS change log between Wave 1 and Wave 5, and who verifies it is complete at M23 cutover? | Quality Manager | **W1 — blocking** |
| Q-03 | Is ISO 27001 certification held, sought, or only operationally applied? The clause map treats it as operational controls; certification would add scope | CTO / Quality Manager | W5 build |
| Q-04 | What is the declared observation window for CAPA effectiveness verification, and does it vary by severity? | Quality Manager | W5 build |
| Q-05 | What is the repeat-cause detection window — 30, 90 or 180 days — and is it the same across sources? | Quality Manager | W5 build |
| Q-06 | Who are the trained internal auditors, and is there sufficient auditor capacity to cover 51+ branches, workshops, suppliers and 500 marketplace sellers annually? | Quality Manager / HR Director | **W5 — capacity risk** |
| Q-07 | Should technician-level quality attribution feed M57 incentives directly, or only as an input to management judgement? The design supplies summary only | Quality Manager / HR Director | W5 build |
| Q-08 | What is the rationalised target number of checklist templates, and who decides which branch variants survive? | Quality Manager / Ops Director | **W4 — precedes migration** |
| Q-09 | Do brand partners accept 1000FiX's internal audit evidence in place of their own audits, in whole or part? | Finance Director / Quality Manager | W5 |

---

## 19. References

**Internal**
`03_Modules/I_Governance_Risk_Quality_and_Knowledge/_CATEGORY_OVERVIEW.md` §3, §5, §6, §8, §10 ·
`M24_Document_Records_and_ESignature.md` §3, §12 ·
`M60_Governance_Risk_and_Compliance.md` §3 ·
`M61_Knowledge_Management_and_Technical_Library.md` §3 ·
`03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md` §5.5, §5.6, §9, §12 ·
`03_Modules/C_Commercial_Pricing_and_Revenue/M09_Warranty_Protection_Plans_and_Claims.md` §5.4, §12 ·
`03_Modules/C_Commercial_Pricing_and_Revenue/M12_Marketplace_and_Seller_Ecosystem.md` §5.4 ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2, §8 ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` ·
`05-04_Role_Permission_and_Access_Matrix.md` §5, §6 SOD-07, §8 ·
`05-05_Business_Rules_and_Automation_Catalogue.md` ·
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` P11 ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md`

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §8.21, §10.1 ·
`1000FiX_ERP_System_Comprehensive_URD.md` §14 ·
`1000FiX_Services_Company_Profile.md` §Certifications

**External benchmark**
ISO 9001:2015 clauses 4–10 · ISO 19011 auditing guidance ·
SAP QM — inspection plans, quality notifications, Nonconformance Management (S/4HANA 1809+), system-based 8D (S/4HANA 2020+) ·
IFS Quality Management — quality integrated with service execution ·
eQMS practice (ComplianceQuest, MasterControl, Qualio) — NC→CAPA workflow, effectiveness verification, audit management ·
8D problem-solving discipline ·
Odoo 19 / OCA `management-system` module family (`mgmtsystem_nonconformity`, `mgmtsystem_action`, `mgmtsystem_audit`, `mgmtsystem_review`)

---

*Module M23 · Category I · 1000FiX ERP System v2.0 · CONFIDENTIAL*
