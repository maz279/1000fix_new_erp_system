---
id: FIX-ERP2-M60
module_id: M60
module_code: GRC
module_name: Governance, Risk & Compliance
category: I — Governance, Risk, Quality & Knowledge
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Financial Officer
system_owner: Governance Squad
priority: P2
wave: W6
---

# M60 — Governance, Risk & Compliance
### Category I · Code `GRC` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M60 |
| **Module code** | `GRC` |
| **Category** | I — Governance, Risk, Quality & Knowledge |
| **Status** | ★ New — created in v2.1 after enterprise benchmarking found that no module owned enterprise risk, internal control, compliance obligations, legal matters, insurance or licences |
| **Priority** | **P2** |
| **Delivery wave** | W6 (Months 23–26) |
| **Business owner** | Chief Financial Officer |
| **System owner** | Governance Squad |
| **Delivery layers** | L2 (OCA `management-system`, `mgmtsystem_hazard`, `contract`/`agreement`) + L5 (custom) |
| **Custom modules** | `cd_risk_register`, `cd_control_framework`, `cd_control_testing`, `cd_obligation_register`, `cd_legal_matter`, `cd_policy_governance` |
| **Requirement range** | FR-GRC-001 … FR-GRC-044 |
| **Requirement count** | **44** *(measured; register estimate 34)* |
| **Effort estimate** | **22 person-weeks** *(measured; register estimate 18 PW)* |
| **Depends on** | M24 Document · M23 Quality · M29 Identity · M28 Integration · M19 Financial Accounting · M21 Core HR · M33 Party Master |
| **Depended on by** | M19, M20, M29, M23, M51, M59, M12, M42, M13, M46, M06, M18, M62, M25 · executive and Board reporting · M24 |

> **Register note.** Measured scope exceeds the pre-specification estimate by 29% in
> requirements and 22% in effort. `02-02` §3 must be restated when all four Category I
> specifications are complete.

---

## 2. Purpose

M60 answers a different question from every other module in the ERP. Every other module asks
*"how do we do the work?"* M60 asks **"can we prove the enterprise is controlled, compliant and
protected?"**

It owns five things that currently exist nowhere in the company as a system:

- The **enterprise risk register** — what could go wrong, how badly, who owns it, what is being
  done and when it was last honestly reviewed
- The **internal control framework** — which controls exist, what risk each mitigates, who
  operates it, and evidence that it actually operated
- The **compliance obligation register** — every statutory, regulatory, contractual and
  certification obligation the company carries, with an owner and evidence of discharge
- **Legal matters, licences and intellectual property** — disputes, litigation, trade licences,
  regulatory registrations, trademarks
- **Insurance** — policies held, cover, exclusions, renewal dates, and claims made against them

The category overview draws the boundary with M23 precisely: M23 owns *process quality* and
answers to the certification body; M60 owns *enterprise control* and answers to the Board,
auditors, regulators and insurers. A repeated quality failure that becomes a systemic exposure
escalates from M23 into M60's register.

### Why It Exists

The v1.0 plan had no GRC module, and at eleven modules that was defensible. At 67 modules,
fourteen revenue streams, a marketplace carrying two Critical risks, split data residency under
PDPA 2026, and multi-entity readiness, it is not.

The specific pressures that created this module:

- **Bangladesh's Personal Data Protection Act 2026** came into force on 15 April 2026. It
  requires lawful-processing records, retention schedules and deletion procedures, records of
  processing activities retained for at least five years, data-subject rights, cross-border
  transfer governance and Chief Data Officer obligations. The programme's split-residency
  decision derives from it. None of that is tracked anywhere today.
- **The marketplace principal/agent determination (RSK-022)** is a Critical risk with
  restatement exposure. Risks of that severity need a register with an owner and a review
  cadence, not a paragraph in a document.
- **Segregation of duties** — twelve SoD rules are defined in `05-04` §6 and enforced by M29.
  Nobody currently *tests* that the enforcement works, and an untested control is not a control.
- **ISO 9001 clause 6** requires risks and opportunities to be addressed. M23 identifies quality
  risks; something has to hold the enterprise view they escalate into.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| `_CATEGORY_OVERVIEW.md` §3 | The M23/M60 boundary: process quality vs enterprise control, with objects, cadence and audience differentiated |
| `_CATEGORY_OVERVIEW.md` §5 | Boundary map assigning risk register, control definition and testing, obligation register, legal matters and insurance to M60 |
| `_CATEGORY_OVERVIEW.md` §8, §10 | Category KPIs and the "risk register written once and never revisited" risk |
| `00-04_Risks_Assumptions_Dependencies_and_Governance.md` | The programme risk register — the seed content and the governance model M60 institutionalises |
| `05-04` §6 SOD-01…SOD-12 | Twelve segregation-of-duties rules requiring definition, testing and exception governance |
| `05-04` §7 Approval Authority Matrix | Delegated authority requiring registration and testing |
| `00-02` §2 | Split data residency driven by PDPA 2026 — a compliance obligation with an architectural consequence |
| `00-02` §7 principle 8 | "Compliance is a feature, not a project" — ISO 9001, ISO 27001, NBR, Labour Act, e-waste rules modelled as enforced system behaviour |
| Bangladesh PDPA 2026 (in force 15 April 2026) | Retention schedules, records of processing retained ≥ 5 years, data-subject rights, cross-border transfer governance |
| M12 §18 Q-01, `RSK-022` | The Critical marketplace principal/agent risk requiring registered ownership and review |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** Both sides of every boundary must agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The **enterprise risk register** — identification, description, categorisation, causes and consequences |
| 2 | Risk assessment: inherent and residual likelihood and impact, scoring methodology, risk appetite and tolerance |
| 3 | Risk ownership, treatment strategy (accept, mitigate, transfer, avoid), treatment actions and review cadence |
| 4 | Risk aggregation: heat maps, top-risk reporting, risk by category, entity and business line |
| 5 | Emerging-risk capture and horizon scanning |
| 6 | The **internal control framework** — control definition, objective, type, frequency, owner and the risk it mitigates |
| 7 | Control-to-risk and control-to-obligation mapping, with coverage and gap reporting |
| 8 | **Control testing** — test plans, sampling, execution, evidence, effectiveness conclusion, deficiency rating |
| 9 | Deficiency remediation and retest |
| 10 | **Segregation-of-duties rule definition and testing**, and SoD exception governance *(M29 enforces)* |
| 11 | Delegated authority register and its testing against actual approvals |
| 12 | **Compliance obligation register** — statutory, regulatory, contractual, certification and licence obligations |
| 13 | Obligation ownership, recurrence, due dates, evidence of discharge and escalation |
| 14 | Regulatory change monitoring and impact assessment |
| 15 | **Policy governance** — the policy library, approval, publication, attestation and exception management |
| 16 | **Legal matters** — disputes, claims, litigation, regulatory actions, counsel, exposure and provisions |
| 17 | **Licence and registration register** — trade licence, VAT/BIN, TIN, environmental, import, sector registrations |
| 18 | **Intellectual property register** — trademarks, domains, software licences held |
| 19 | **Insurance register** — policies, cover, exclusions, sums insured, renewals, and claims made |
| 20 | **Data-protection governance** — records of processing activities, lawful basis, data-subject requests, cross-border transfer register, breach register *(PDPA 2026)* |
| 21 | Third-party and outsourcing risk: due diligence, risk rating and periodic reassessment for suppliers, sellers, partners and processors |
| 22 | Business continuity and disaster-recovery governance: plans, dependencies, test schedule and test evidence |
| 23 | Whistleblowing and speak-up case management with confidentiality controls |
| 24 | Board and audit-committee reporting: risk, control, compliance and legal position |
| 25 | Annual control attestation and management assertion |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Process quality, non-conformance, CAPA, quality audit | **M23** Quality | Process quality answers to the certification body; enterprise control answers to the Board *(category overview §3)* |
| Quality checklists and QC gates | **M23** Quality | — |
| **Enforcement** of access rules, SoD and permissions at runtime | **M29** Identity & Security | M60 defines and tests; M29 enforces *(category boundary map)* |
| Security operations, vulnerability management, incident response | **M29** Identity & Security | Security operations are technical execution; M60 governs the framework |
| Tax computation, VAT return preparation and NBR filing | **M51** Tax | M60 registers the obligation; M51 discharges it |
| Financial control **execution** — reconciliations, approvals, close checklist | **M19** Financial Accounting | M60 defines the control; M19 operates it |
| Statutory financial reporting and audit of the accounts | **M19** / external auditor | — |
| Health, safety and occupational incidents | **M59** Health, Safety & Wellbeing | Safety has its own statutory regime and module |
| Environmental and e-waste disposal compliance evidence | **M18** E-Waste | M60 registers the obligation; M18 holds the certificates |
| Employment law compliance in HR processes | **M21** / **M56** | Executed there; registered here |
| Contract terms, obligations and renewals | **M08** Contract | M08 tracks contractual obligations per contract; M60 tracks the enterprise obligation set and escalates systemic contractual exposure |
| Document storage, retention execution, legal hold execution | **M24** Document | M60 sets retention policy from obligations; M24 enforces it |
| Data classification and encryption implementation | **M62** Data Platform / **M29** | M60 governs; they implement |
| Marketplace seller conduct, disputes and consequence | **M12** Marketplace | M60 holds the enterprise risk; M12 runs the platform |
| Programme delivery risk during implementation | `00-04` programme governance | The programme risk register seeds M60 but is a programme artefact until handover |

### 3.3 Shared Concepts

| Concept | M60's Role | Owning Module |
|---|---|---|
| Enterprise risk | **Owner** | M60 |
| Quality risk | Receives escalated systemic exposures | M23 |
| Internal control | **Owner** of definition and testing | M60 |
| Control execution | Consumes evidence | M19, M29, M15, M20, others |
| SoD rule | **Owner** of definition and testing | M60 (define/test) / M29 (enforce) |
| Compliance obligation | **Owner** | M60 |
| Obligation discharge | Consumes evidence | M51, M19, M18, M56, M23 |
| Policy | **Owner** of governance; M24 controls the artefact | M60 (governance) / M24 (document) |
| Legal matter, licence, IP | **Owner** | M60 |
| Insurance policy | **Owner**; claims raised by the affected module | M60 |
| Records of processing (PDPA) | **Owner** | M60 |
| Retention schedule | **Owner** of the policy; M24 enforces | M60 (policy) / M24 (enforcement) |
| Third-party risk rating | **Owner**; M42 and M12 manage the relationship | M60 |
| Business continuity plan | **Owner** of governance; M29/M62 execute technical DR | M60 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP GRC** — Risk Management, Process Control, Access Control, Audit Management, Fraud Management | An integrated framework aligning objectives, risks and controls; automated control testing and reporting to cut audit cost and cycle time; risk registers and obligation maps aligned to ISO 31000 or COSO | **The integrated spine**: objective → risk → control → test → evidence, with controls mapped to both risks and obligations so a single test satisfies several assurance needs. Also **automated control testing** wherever the evidence is already in the ERP | SAP GRC's Access Control product — M29 already enforces access and SoD; duplicating enforcement would create two authorities. M60 tests M29's enforcement rather than replacing it |
| **Oracle Risk Management Cloud** | Risk and control registers with embedded transaction monitoring and advanced access controls | **Continuous control monitoring against transaction data** as an aspiration for high-value controls, implemented selectively where the ERP already holds the evidence | Full transaction-monitoring analytics at launch; disproportionate at our transaction profile and better delivered by M26 later |
| **COSO 2013 Internal Control — Integrated Framework** | Five components, seventeen principles; control environment, risk assessment, control activities, information and communication, monitoring | **The control-activity and monitoring discipline**, and the principle that a control not evidenced is not a control | Full COSO attestation machinery designed for SOX-registrant scale |
| **ISO 31000** — risk management | Risk process, appetite, criteria, treatment, monitoring and review; risk as an owned, reviewed object | **Risk appetite and tolerance declared before assessment**, and **mandatory periodic review** — the direct control against the category risk "register written once and never revisited" | ISO 31000's full maturity model |
| **ISO 27001 Annex A / ISO 27005** | Information-security control set and risk treatment | **Security controls registered alongside operational controls**, so one framework covers both, and clause coverage is shared with M23 | Separate security GRC tooling |
| **Enterprise GRC platforms** (LogicGate, ServiceNow IRM, Diligent, AuditBoard class) | Obligation libraries, regulatory change feeds, policy attestation, issue management, board reporting | **Policy attestation with tracked acknowledgement**, **issue and deficiency management**, and **board-pack assembly from live data** | Regulatory-change content subscriptions — no vendor covers Bangladeshi regulation adequately, so the obligation register is maintained locally with external counsel |
| **Odoo 19 + OCA** — `management-system` family, `mgmtsystem_hazard`, `agreement` | Risk-like objects, action management, agreement records | The **action and review machinery shared with M23**, avoiding two incompatible action engines in one category | Treating enterprise risk as a quality non-conformity; the objects, cadence and audience differ |

**Design position.** 1000FiX differs from the benchmarks in five ways, and every one of them is a
consequence of being a mid-sized Bangladeshi service company rather than a listed multinational.

First, **proportionality is a design requirement, not a compromise**. A GRC module that demands
a control-testing bureaucracy will be abandoned within two quarters. M60 therefore concentrates
on a **small set of key controls tested well** — the category KPI is *100% of key controls tested
per cycle*, deliberately scoped to *key*, not *all*. Everything else is registered but not
tested.

Second, **the ERP is the evidence source, so testing is largely automatic**. Where a control is
"every purchase order above BDT 500,000 is approved by the Procurement Manager", the test is a
query, not a sample of paper. Controls whose evidence already exists in the ERP are tested
continuously; only controls with external or judgemental evidence require manual testing. This
is the single largest efficiency decision in the module.

Third, **M60 tests M29's enforcement rather than duplicating it**. The twelve SoD rules in
`05-04` §6 are enforced by the permission engine. M60's job is to prove periodically that the
enforcement works — including by attempting violations in a controlled test — and to govern the
time-boxed exceptions the CFO or CTO approves. Two enforcement points would be worse than one.

Fourth, **data-protection governance is built in from the start, not retrofitted**. PDPA 2026 is
in force now. Records of processing activities, lawful basis per processing purpose, the
cross-border transfer register and the data-subject request workflow are P0 within this module,
because the split-residency architecture the programme has already committed to is meaningless
without the governance that justifies it. Bangladesh's Act notably lacks a mandatory breach
notification requirement; M60 nonetheless maintains a breach register, because contractual
obligations to corporate customers and brand partners will require disclosure even where statute
does not.

Fifth, **the risk register inherits the programme's own register**. `00-04` already contains a
live, owned, rated risk set including RSK-022. M60's first act is not to invent a register but
to **institutionalise the one that exists**, converting programme risks that outlive the
programme into enterprise risks with permanent owners.

---

## 5. Functional Areas & Features

### 5.1 Enterprise Risk Management

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-GRC-001 | Risk register | Maintain every enterprise risk with description, category, causes, consequences, owner, entity, business line and status | P0 | L5 |
| FR-GRC-002 | Risk appetite and criteria | Declare risk appetite and tolerance per category, and the likelihood and impact scales used, before any risk is scored | P0 | L5 |
| FR-GRC-003 | Inherent and residual assessment | Score inherent risk, record the controls relied upon, and score residual risk, showing the difference the controls make | P0 | L5 |
| FR-GRC-004 | Treatment strategy and actions | Record the treatment decision (accept, mitigate, transfer, avoid) with rationale, and manage treatment actions to completion | P0 | L5 |
| FR-GRC-005 | Mandatory periodic review | Require each risk to be reviewed at its declared cadence, escalate overdue reviews, and report review currency as a governance KPI | P0 | L5 |
| FR-GRC-006 | Risk aggregation and heat map | Aggregate risks by category, entity, business line and owner, and present heat maps and top-risk reporting | P1 | L5 |
| FR-GRC-007 | Risk-event linkage | Link realised events — incidents, losses, claims, non-conformances, breaches — to the risk that materialised, and use them to challenge the assessment | P1 | L5 |
| FR-GRC-008 | Escalation from quality | Accept systemic quality exposures escalated from M23 as enterprise risks, preserving the linkage in both directions | P0 | L5 |
| FR-GRC-009 | Emerging risk and horizon scanning | Capture emerging risks with a lighter assessment, and promote them to the main register when criteria are met | P2 | L5 |
| FR-GRC-010 | Programme risk handover | Import and reconcile the programme risk register from `00-04`, converting surviving risks to enterprise risks with permanent owners | P0 | L5 |

### 5.2 Internal Control Framework & Testing

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-GRC-011 | Control register | Maintain every internal control with objective, description, type (preventive/detective/corrective), nature (manual/automated/hybrid), frequency, owner and operating unit | P0 | L5 |
| FR-GRC-012 | Key control designation | Designate key controls, and scope the testing programme to them explicitly | P0 | L5 |
| FR-GRC-013 | Control-to-risk and control-to-obligation mapping | Map each control to the risks it mitigates and the obligations it discharges, and report coverage and gaps in both directions | P0 | L5 |
| FR-GRC-014 | Automated control testing | Test controls whose evidence exists in the ERP by query, continuously, and record the result as test evidence | P0 | L5 |
| FR-GRC-015 | Manual control testing | Plan and execute manual tests with sampling method, sample size, evidence capture and conclusion | P0 | L5 |
| FR-GRC-016 | Test evidence and retention | Retain test evidence through M24 for the required period, immutably and retrievably | P0 | L5 |
| FR-GRC-017 | Deficiency rating and remediation | Rate deficiencies (deficiency, significant deficiency, material weakness), assign remediation with owner and date, and require retest before closure | P0 | L5 |
| FR-GRC-018 | SoD rule register | Register every segregation-of-duties rule with its risk, enforcement point and test method | P0 | L5 |
| FR-GRC-019 | SoD testing | Test periodically that M29 actually enforces each SoD rule, including by controlled violation attempt, and report failures as deficiencies | P0 | L5 |
| FR-GRC-020 | SoD exception governance | Manage time-boxed SoD exceptions with CFO or CTO approval, expiry, and a standing quarterly exception report *(`05-04` §6)* | P0 | L5 |
| FR-GRC-021 | Delegated authority register | Register the approval authority matrix and test actual approvals against it, reporting approvals made outside authority | P1 | L5 |
| FR-GRC-022 | Annual control attestation | Run an annual attestation cycle in which control owners confirm operation, and produce the management assertion | P2 | L5 |

### 5.3 Compliance, Obligations & Policy

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-GRC-023 | Obligation register | Maintain every statutory, regulatory, contractual, certification and licence obligation with source, requirement text, owner, recurrence and consequence of breach | P0 | L5 |
| FR-GRC-024 | Obligation discharge and evidence | Track each obligation occurrence to discharge with evidence, and report obligations discharged without evidence as a control failure | P0 | L5 |
| FR-GRC-025 | Obligation calendar and escalation | Drive an obligation calendar with advance notice, escalation before due date, and breach recording after | P0 | L5 |
| FR-GRC-026 | Regulatory change monitoring | Record regulatory changes, assess their impact on obligations, controls and processes, and drive the resulting actions | P1 | L5 |
| FR-GRC-027 | Licence and registration register | Maintain trade licence, VAT/BIN, TIN, environmental, import and sector registrations with validity, renewal lead time and evidence | P0 | L5 |
| FR-GRC-028 | Intellectual property register | Maintain trademarks, domains and software licences held, with renewal and infringement tracking | P2 | L5 |
| FR-GRC-029 | Policy library and governance | Maintain the policy set with owner, approval, version, effective date and review cycle, controlled through M24 | P0 | L5 |
| FR-GRC-030 | Policy attestation | Require named populations to acknowledge policies, track acknowledgement, and escalate non-acknowledgement | P1 | L5 |
| FR-GRC-031 | Policy exception management | Record, approve, time-box and review exceptions to policy, and report standing exceptions | P1 | L5 |
| FR-GRC-032 | Retention policy definition | Define the statutory retention schedule from obligations and publish it to M24 for enforcement | P0 | L5 |

### 5.4 Data Protection, Legal, Insurance & Third Parties

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-GRC-033 | Records of processing activities | Maintain the PDPA 2026 record of processing activities — purpose, lawful basis, data categories, subjects, recipients, retention, safeguards — retained for at least five years | P0 | L5 |
| FR-GRC-034 | Cross-border transfer register | Register every cross-border transfer of personal data with its basis, safeguards and destination, consistent with the split-residency architecture | P0 | L5 |
| FR-GRC-035 | Data-subject request workflow | Receive, verify, route, fulfil and evidence data-subject requests within the statutory period, across every module holding personal data | P0 | L5 |
| FR-GRC-036 | Breach register and response | Maintain a breach register with assessment, containment, notification decision and evidence — including contractual notifications where statute is silent | P0 | L5 |
| FR-GRC-037 | Privacy impact assessment | Require and record a privacy impact assessment for new processing of higher-risk personal data | P1 | L5 |
| FR-GRC-038 | Legal matter register | Maintain disputes, claims, litigation and regulatory actions with counsel, status, exposure, provision and next action | P1 | L5 |
| FR-GRC-039 | Legal hold instruction | Instruct M24 to place and release legal holds arising from a matter, and evidence the instruction | P0 | L5 |
| FR-GRC-040 | Insurance register | Maintain policies with insurer, cover, sums insured, exclusions, excess, premium and renewal date, with advance renewal alerting | P1 | L5 |
| FR-GRC-041 | Insurance claim tracking | Track claims made against policies from notification to settlement, linked to the originating event or module | P1 | L5 |
| FR-GRC-042 | Third-party risk assessment | Risk-rate suppliers, marketplace sellers, partners and data processors, require due diligence proportionate to the rating, and reassess periodically | P1 | L5 |
| FR-GRC-043 | Business continuity governance | Maintain continuity and disaster-recovery plans with dependencies, recovery objectives, test schedule and test evidence | P2 | L5 |
| FR-GRC-044 | Whistleblowing case management | Receive speak-up reports through a confidential channel, manage investigation with restricted access, and report anonymised outcomes to the audit committee | P2 | L5 |

*(Full requirement text is mirrored in `05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md`.)*

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Assessment history, never overwrite** | Every risk and control assessment is a new dated version. "What did we think the residual risk was last March, and who said so" is always answerable |
| T-02 | **Automated test as a declarative query** | Automated control tests are declared as parameterised queries with an expected result, versioned, and executed by a scheduler — not written as bespoke code per control |
| T-03 | **Test evidence immutability** | Evidence is sealed with a content hash at test conclusion and stored through M24; a later data change cannot silently alter a past test result |
| T-04 | **Read-only assurance access** | M60's automated tests read from source modules through APIs and the warehouse; the module has no write access to the data it tests |
| T-05 | **Independence of testing** | The system prevents a control owner from recording the test conclusion for their own control |
| T-06 | **Review scheduler** | Risk and obligation review dates are evaluated continuously and escalate independently of anyone remembering; the scheduler is restartable and drops nothing |
| T-07 | **Obligation calendar correctness** | Recurring obligations honour statutory calendars, working days and Bangladeshi public holidays |
| T-08 | **Data-subject request fan-out** | A data-subject request enumerates every module holding that subject's personal data through a registered data map, and tracks each module's response |
| T-09 | **Confidentiality tiering** | Whistleblowing cases, legal matters and breach records are tier T5: named allow-list, step-up authentication, every access logged *(`05-04` §4)* |
| T-10 | **Legal hold propagation** | A hold instruction reaches M24 transactionally; a hold is never partially applied |
| T-11 | **Board pack reproducibility** | A board report can be regenerated exactly as issued at a past date, from versioned assessments |
| T-12 | **Separation from enforcement** | M60 holds no runtime enforcement path. It cannot block a transaction; it can only report that a control failed — deliberate, so governance never becomes an availability risk |
| T-13 | **Retention policy publication** | The retention schedule is published to M24 as versioned configuration, never re-keyed |
| T-14 | **Audit trail of the governance module** | Every change to a risk, control, obligation, exception or attestation is audited with actor and reason, append-only |
| T-15 | **Performance envelope** | Risk register view ≤ 1.5 s · heat map over 500 risks ≤ 2 s · automated control test batch within its nightly window · board pack assembly ≤ 90 s |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M60 |
|---|---|---|
| **CFO** | Carries the company's risk position in their head and in a slide deck | Sees a register with owners, review currency, control coverage and tested effectiveness |
| **CEO / Board** | Is briefed on risk when something has already gone wrong | Receives a reproducible quarterly position on risk, control, compliance and legal exposure |
| **CTO** | Enforces twelve SoD rules and hopes they work | Sees them tested, including by controlled violation attempt, with failures raised as deficiencies |
| **Quality Manager** | Escalates systemic quality problems verbally | Escalates them into a register where they acquire an enterprise owner and a review date |
| **Finance Manager** | Operates controls without knowing which risk they mitigate | Sees the control's purpose, its test result and its deficiency status |
| **Legal / external counsel** | Matters tracked in email | Matters registered with exposure, provision, next action and holds instructed to M24 |
| **HR Director** | Employment obligations tracked by memory and calendar | Obligations registered with owners, evidence and escalation |
| **Data protection owner** | Role effectively unstaffed; PDPA 2026 obligations untracked | Records of processing, transfer register, subject requests and breach register maintained as a system |
| **External auditor / insurer** | Requests evidence and waits days | Is given a scoped, evidenced position from live data |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Risk ownership and currency** | Mandatory review cadence with escalation | **100% of enterprise risks with a current owner and review date** *(category KPI)* — from a baseline where no enterprise register exists |
| **Control assurance** | Key controls tested, largely automatically, every cycle | **100% of key controls tested per cycle** *(category KPI)* |
| **Compliance discharge evidence** | Obligation register with evidence requirement | **100% of compliance obligations with evidence of discharge** *(category KPI)* |
| **Licences and insurance currency** | Renewal lead times and escalation | **100% current** *(category KPI)* — a lapsed trade licence or import registration halts operations; a lapsed insurance policy converts a manageable loss into an unmanageable one |
| **Avoided regulatory penalty and restatement** | Registered ownership of Critical risks including the marketplace principal/agent determination (RSK-022) | The marketplace VAT exposure is rated **Critical — restatement or regulatory action**. Avoiding it is not an efficiency gain; it is the difference between a functioning marketplace and a material adverse event |
| **PDPA 2026 readiness** | Records of processing, transfer register, subject-request workflow, breach register | Statutory compliance from the Act's in-force date, and a precondition for corporate and government contracts that require processor assurances |
| **Audit efficiency** | Evidence assembled from live data rather than prepared for each audit | Materially reduces the internal cost of the statutory audit, the ISO surveillance and brand-partner audits — the same evidence serves all three |
| **Insurance premium and claim outcomes** | Demonstrable control environment and complete claim records | Insurers price demonstrated control; a company that can evidence its controls negotiates differently |

> **Discipline note.** M60's benefit is almost entirely **avoided loss and preserved optionality**.
> No revenue line should be attributed to it, and none is claimed. Its business case rests on the
> severity of what it prevents, and the honest statement of that severity is in `00-04` and the
> category risk register — not in a benefit number invented here.

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Institutional memory of risk** | Risk knowledge stops being personal to the CFO and becomes a corporate asset that survives succession |
| **Board-level credibility** | A company that can produce a reproducible control position is governed differently, and is treated differently by lenders, insurers and acquirers |
| **Honest self-assessment** | A register with mandatory review forces the organisation to periodically say out loud what it is worried about — a discipline no informal process produces |
| **Proportionate, not performative** | Scoping testing to key controls keeps governance credible; a bureaucracy that everyone works around provides negative assurance |
| **Regulatory relationship** | Being able to evidence compliance changes the character of any regulatory interaction, including one that begins badly |
| **Expansion readiness** | Multi-entity and multi-country expansion multiplies obligations. A register that already exists scales; one that does not becomes the constraint |
| **Ethical infrastructure** | A confidential speak-up channel with protected handling is what makes an ethics policy real rather than decorative |

---

## 8. Lifecycle & State Model

M60 owns three lifecycles: the **risk**, the **control test**, and the **obligation occurrence**.

### 8.1 Risk

```
   ┌────────────┐
   │ IDENTIFIED │ from any source: escalation, event, audit, horizon scan
   └─────┬──────┘
         │ owner assigned; category and appetite applied
   ┌─────▼──────┐
   │  ASSESSED  │ inherent score, controls relied upon, residual score
   └─────┬──────┘
         │ treatment decision recorded with rationale
   ┌─────┼──────────────┬──────────────┬──────────────┐
   ▼     ▼              ▼              ▼              ▼
┌──────────┐  ┌──────────────┐  ┌───────────┐  ┌──────────┐
│ ACCEPTED │  │  MITIGATING  │  │TRANSFERRED│  │ AVOIDED  │
│(within   │  │ (treatment   │  │(insurance/│  │(activity │
│ appetite)│  │  actions     │  │ contract) │  │ ceased)  │
└────┬─────┘  │  in flight)  │  └─────┬─────┘  └────┬─────┘
     │        └──────┬───────┘        │             │
     └───────────────┴────────────────┴─────────────┤
                                                     │
                              ┌──────────────────────▼──────┐
                              │      UNDER REVIEW           │◄── review cadence due
                              │ (re-assessed; residual score│
                              │  confirmed or changed)      │
                              └──────────────┬──────────────┘
                                             │
                    ┌────────────────────────┼──────────────────┐
                    ▼                        ▼                  ▼
             ┌─────────────┐        ┌────────────────┐  ┌──────────────┐
             │  MONITORED  │        │   ESCALATED    │  │    CLOSED    │
             │ (returns to │        │ (outside       │  │ (no longer   │
             │  its state) │        │  appetite →    │  │  applicable; │
             └─────────────┘        │  Board)        │  │  evidenced)  │
                                    └────────────────┘  └──────────────┘

  Cross-cutting: OVERDUE REVIEW is a flag, not a state. It escalates and is
  reported as a governance KPI — the direct control against the category risk
  "risk register written once and never revisited".
```

### 8.2 Control Test

```
PLANNED ──► SCHEDULED ──► IN EXECUTION ──► CONCLUDED
                                              │
                    ┌─────────────────────────┼──────────────────┐
                    ▼                         ▼                  ▼
             ┌─────────────┐         ┌────────────────┐  ┌──────────────┐
             │  EFFECTIVE  │         │   DEFICIENT    │  │ NOT TESTABLE │
             └─────────────┘         └───────┬────────┘  │ (evidence    │
                                             │           │  unavailable │
                                    ┌────────▼────────┐  │  — itself a  │
                                    │  REMEDIATION    │  │  finding)    │
                                    └────────┬────────┘  └──────────────┘
                                             │ remediation complete
                                    ┌────────▼────────┐
                                    │     RETEST      │──► EFFECTIVE / DEFICIENT
                                    └─────────────────┘

  A deficiency cannot be closed without a passed retest (BRU-GRC-08).
```

### 8.3 Obligation Occurrence

```
SCHEDULED ──► DUE ──► DISCHARGED (evidence attached) ──► VERIFIED ──► CLOSED
     │          │
     │          └──► OVERDUE ──► BREACHED (recorded, assessed, escalated)
     └──► NOT APPLICABLE (justified and approved)
```

### Transition Guards

| From | To | Guard | Actor |
|---|---|---|---|
| Identified | Assessed | Owner assigned; category and appetite scale applied | Risk owner |
| Assessed | Accepted | Residual score within declared appetite; acceptance approved at the required authority | CFO / CEO / Board by threshold |
| Assessed | Mitigating | Treatment actions defined with owners and dates | Risk owner |
| Assessed | Transferred | Transfer instrument evidenced — insurance policy or contractual term | CFO |
| Any | Under Review | Review cadence reached | System |
| Under Review | Escalated | Residual score outside appetite after review | System → CFO → Board |
| Any | Closed | Risk no longer applicable, with evidence and approval | CFO |
| Planned | In Execution | Tester assigned who is not the control owner | Control testing officer |
| In Execution | Concluded | Evidence captured and sealed; conclusion recorded with rationale | Tester |
| Concluded | Deficient | Test criteria not met | System |
| Deficient | Retest | Remediation evidenced complete | Control owner |
| Retest | Effective | Retest criteria met | Tester |
| Due | Discharged | Evidence of discharge attached | Obligation owner |
| Discharged | Verified | Evidence reviewed against the obligation's requirement | Compliance officer |
| Overdue | Breached | Due date passed with no discharge; breach assessed and escalated | System + CFO |

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-GRC-01 | Every enterprise risk has exactly one named owner and a declared review cadence at all times | **H** | CFO |
| BRU-GRC-02 | A risk cannot be scored before risk appetite and the scoring scales are declared | **H** | CFO |
| BRU-GRC-03 | Risk and control assessments are versioned; a prior assessment is never overwritten | **H** | CTO |
| BRU-GRC-04 | An overdue risk review escalates automatically and is reported as a governance KPI; it cannot be silently extended | **C** | CFO |
| BRU-GRC-05 | A residual risk outside appetite is escalated to the Board and cannot be closed below that authority | **H** | CFO |
| BRU-GRC-06 | A control owner cannot record the test conclusion for their own control | **H** | CFO |
| BRU-GRC-07 | A control asserted as operating without evidence is a deficiency, not a pass | **H** | CFO |
| BRU-GRC-08 | A deficiency cannot be closed without a passed retest | **H** | CFO |
| BRU-GRC-09 | Every SoD rule in `05-04` §6 is tested at least once per cycle, including by controlled violation attempt | **H** | CTO |
| BRU-GRC-10 | An SoD exception is time-boxed, approved by the CFO or CTO, and appears on the standing quarterly exception report *(`05-04` §6)* | **H** | CFO / CTO |
| BRU-GRC-11 | M60 defines and tests controls; it never enforces them at runtime | **H** | CTO |
| BRU-GRC-12 | An obligation discharged without evidence is recorded as a control failure | **H** | CFO |
| BRU-GRC-13 | A breached obligation is recorded, assessed for consequence and escalated; it is never quietly closed | **H** | CFO |
| BRU-GRC-14 | The statutory retention schedule is defined here and published to M24; retention is never configured independently in M24 | **H** | CFO / Quality Manager |
| BRU-GRC-15 | A legal hold instructed by M60 overrides every retention rule until released by M60 | **H** | CFO |
| BRU-GRC-16 | Every processing of personal data has a recorded lawful basis in the record of processing activities before it begins | **H** | CFO / CTO |
| BRU-GRC-17 | Records of processing activities are retained for at least five years *(PDPA 2026)* | **H** | CFO |
| BRU-GRC-18 | A cross-border transfer of personal data cannot occur without a registered basis and safeguards | **H** | CTO |
| BRU-GRC-19 | A data-subject request is fulfilled and evidenced within the statutory period, across every module holding that subject's data | **H** | CFO |
| BRU-GRC-20 | Whistleblowing cases, legal matters and breach records are tier T5: allow-list access, step-up authentication, every access logged | **H** | CFO / CTO |
| BRU-GRC-21 | A systemic quality exposure escalated from M23 cannot be closed in M23 alone; M60 must accept or decline it explicitly | **H** | Quality Manager / CFO |
| BRU-GRC-22 | A licence, registration or insurance policy approaching expiry escalates on the declared lead time; lapse generates a mandatory incident record | **H** | CFO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.risk` | `fix_risk` | Enterprise risk register | code, title, description, category, causes, consequences, owner_id, entity_id, business_line, state, review_cadence, next_review_at, source, escalated_from_ref |
| `fix.risk.assessment` | `fix_risk_assessment` | Versioned assessments | risk_id, version, assessed_at, assessed_by, inherent_likelihood, inherent_impact, inherent_score, controls_relied_on_ids, residual_likelihood, residual_impact, residual_score, within_appetite |
| `fix.risk.appetite` | `fix_risk_appetite` | Appetite and scales | category, appetite_statement, tolerance_threshold, likelihood_scale_json, impact_scale_json, approved_by, effective_from |
| `fix.risk.treatment` | `fix_risk_treatment` | Treatment decisions and actions | risk_id, strategy, rationale, approved_by, action_ids, target_residual_score, target_date |
| `fix.risk.event` | `fix_risk_event` | Realised events linked to risks | risk_id, event_type, source_module, source_ref, occurred_at, loss_amount, description |
| `fix.control` | `fix_control` | Internal control register | code, objective, description, type, nature, frequency, owner_id, operating_unit_id, is_key, state, source_framework |
| `fix.control.mapping` | `fix_control_mapping` | Control ↔ risk / obligation | control_id, target_type (risk/obligation), target_id, coverage_note |
| `fix.control.test.plan` | `fix_control_test_plan` | Test definitions | control_id, method (automated/manual), query_ref, sampling_method, sample_size, criteria, frequency, tester_role_id |
| `fix.control.test` | `fix_control_test` | Test executions | plan_id, period, executed_at, executed_by, sample_json, evidence_refs, conclusion, evidence_hash |
| `fix.control.deficiency` | `fix_control_deficiency` | Deficiencies | test_id, rating, description, root_cause, owner_id, remediation_plan, due_at, retest_id, state |
| `fix.sod.rule` | `fix_sod_rule` | SoD rule register | code, incompatible_duties, risk_ref, enforcement_point, test_method, severity |
| `fix.sod.test` | `fix_sod_test` | SoD test results | rule_id, period, method, attempted_violation, blocked, exceptions_found_json, conclusion |
| `fix.sod.exception` | `fix_sod_exception` | Time-boxed exceptions | rule_id, user_id, justification, approved_by, valid_from, valid_to, state, review_ref |
| `fix.authority.register` | `fix_authority_register` | Delegated authority | transaction_type, threshold, approver_role_id, effective_from, source_ref |
| `fix.obligation` | `fix_obligation` | Compliance obligation register | code, source_type (statutory/regulatory/contractual/certification/licence), source_ref, requirement_text, owner_id, recurrence, lead_days, consequence_of_breach, state |
| `fix.obligation.occurrence` | `fix_obligation_occurrence` | Each due instance | obligation_id, period, due_at, state, discharged_at, discharged_by, evidence_document_id, verified_by, breach_ref |
| `fix.regulatory.change` | `fix_regulatory_change` | Regulatory change log | source, description, published_at, effective_at, impact_assessment, affected_obligation_ids, affected_control_ids, actions_ids |
| `fix.licence` | `fix_licence` | Licences and registrations | type, number, issuer, scope, entity_id, issued_at, expires_at, renewal_lead_days, document_id, state |
| `fix.ip.asset` | `fix_ip_asset` | Intellectual property | type (trademark/domain/software licence), identifier, jurisdiction, registered_at, renews_at, owner_id, document_id |
| `fix.policy` | `fix_policy` | Policy library | code, title, owner_id, version, approved_by, effective_from, review_cycle, document_id, attestation_population |
| `fix.policy.attestation` | `fix_policy_attestation` | Acknowledgements | policy_id, version, user_id, acknowledged_at, method |
| `fix.policy.exception` | `fix_policy_exception` | Policy exceptions | policy_id, requester_id, justification, approved_by, valid_from, valid_to, compensating_control_id, state |
| `fix.processing.record` | `fix_processing_record` | PDPA records of processing | purpose, lawful_basis, data_categories, subject_categories, recipients, retention_ref, safeguards, owner_id, entity_id, created_at |
| `fix.transfer.register` | `fix_transfer_register` | Cross-border transfers | processing_record_id, destination_country, recipient, basis, safeguards, volume_class, approved_by, effective_from |
| `fix.subject.request` | `fix_subject_request` | Data-subject requests | subject_ref, request_type, received_at, verified_at, due_at, module_responses_json, fulfilled_at, evidence_ref, state |
| `fix.privacy.impact` | `fix_privacy_impact` | Privacy impact assessments | processing_record_id, risk_summary, mitigations, residual_risk, approved_by, at |
| `fix.breach` | `fix_breach` | Breach register (T5) | detected_at, description, data_categories, subjects_affected, containment, assessment, notification_decision, notified_parties, closed_at |
| `fix.legal.matter` | `fix_legal_matter` | Legal matters (T5) | reference, type, counterparty, counsel, opened_at, status, exposure_estimate, provision_amount, next_action_at, hold_refs |
| `fix.insurance.policy` | `fix_insurance_policy` | Insurance register | type, insurer, policy_number, cover_summary, sum_insured, excess, exclusions, premium, period_from, period_to, document_id |
| `fix.insurance.claim` | `fix_insurance_claim` | Claims against policies | policy_id, event_ref, source_module, notified_at, claimed_amount, settled_amount, state |
| `fix.third.party.risk` | `fix_third_party_risk` | Third-party risk ratings | party_id, party_type, rating, due_diligence_ref, assessed_at, reassess_at, findings |
| `fix.continuity.plan` | `fix_continuity_plan` | BCP / DR governance | scope, dependencies_json, rto, rpo, plan_document_id, last_tested_at, test_evidence_ref, next_test_at |
| `fix.speakup.case` | `fix_speakup_case` | Whistleblowing (T5) | reference, received_at, channel, category, anonymised_summary, investigator_id, state, outcome, reported_to_committee_at |

### 10.2 Referenced Entities

| Entity | Owned By | Access Pattern |
|---|---|---|
| `fix.document`, versions, retention, legal hold | M24 | Service call; retention published, holds instructed |
| `fix.nonconformance`, `fix.capa`, `fix.quality.risk` | M23 | Escalation intake + live read |
| Access rules, role assignments, SoD enforcement outcomes | M29 | Live read — the subject of testing |
| Transaction data for automated control tests | M19, M20, M15, M16, M52, others | Read-only API and warehouse |
| `fix.employee`, org structure | M21 | Live read — ownership and attestation populations |
| `fix.contract` obligations | M08 | Live read — contractual obligation source |
| `fix.supplier.profile`, `fix.seller`, `fix.partner.profile` | M42 / M12 / M40 | Live read — third-party risk subjects |
| Tax obligations and filings | M51 | Live read — obligation discharge evidence |
| E-waste and environmental certificates | M18 | Live read |
| Safety incidents | M59 | Live read — risk events |
| Data map and classification | M62 | Live read — data-subject request fan-out |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-GRC-01 | Risk review date reached | Create the review task for the owner, escalate on the declared ladder, and flag the risk as overdue in governance reporting | Repeat escalation; overdue is never cleared automatically |
| AUT-GRC-02 | Residual score assessed outside appetite | Escalate to CFO and Board reporting with the assessment attached | Repeat until acknowledged |
| AUT-GRC-03 | Systemic quality exposure escalated from M23 | Create a linked enterprise risk in Identified state and notify the CFO; hold the M23 record open until accepted or declined | Escalate to CFO |
| AUT-GRC-04 | Realised event in any module (loss, incident, breach, claim, major NC) | Link to the relevant risk and prompt reassessment where the event exceeds the assumed impact | Queue; alert |
| AUT-GRC-05 | Automated control test scheduled | Execute the declared query, evaluate against criteria, seal the evidence, record the conclusion | Record "not testable" as a finding; never record a pass on failure to execute |
| AUT-GRC-06 | Manual control test due | Assign to a tester who is not the control owner, with sampling method and criteria | Escalate to CFO |
| AUT-GRC-07 | Test concludes deficient | Raise the deficiency, rate it, assign remediation with a due date, schedule the retest | Escalate |
| AUT-GRC-08 | Remediation overdue | Escalate through owner, manager and CFO on the declared schedule | Repeat |
| AUT-GRC-09 | SoD test cycle due | Execute rule-by-rule tests against M29, including controlled violation attempts in a non-production context, and report results | Escalate to CTO |
| AUT-GRC-10 | SoD exception approaching expiry | Notify the approver; expire automatically on the date; report in the standing quarterly exception report | Expire regardless; never auto-extend |
| AUT-GRC-11 | Obligation occurrence due | Notify the owner at the declared lead time; escalate at due date; record breach after | Repeat escalation |
| AUT-GRC-12 | Obligation discharged | Verify evidence is attached; where absent, record a control failure rather than a discharge | Block verification; alert |
| AUT-GRC-13 | Licence, registration or insurance approaching expiry | Escalate on the lead-time ladder to owner, CFO and CEO | Repeat; lapse raises a mandatory incident |
| AUT-GRC-14 | Policy version published | Assign attestation to the declared population, track acknowledgement, escalate non-acknowledgement | Repeat; report outstanding |
| AUT-GRC-15 | Data-subject request received | Verify identity, fan out to every module in the data map, track each response, and drive to fulfilment within the statutory period | Escalate to CFO; the statutory clock does not pause |
| AUT-GRC-16 | Cross-border transfer detected without a registered basis | Raise a compliance breach and notify the CTO and CFO | — |
| AUT-GRC-17 | Breach detected or reported | Open the breach record at tier T5, start the assessment clock, and drive the notification decision with contractual obligations evaluated | Escalate immediately to CFO and CTO |
| AUT-GRC-18 | Legal matter opened requiring preservation | Instruct M24 to place legal holds on the identified scope and evidence the instruction | Block matter progression; escalate |
| AUT-GRC-19 | Third-party reassessment due | Create the reassessment task proportionate to the party's rating, and notify M42, M12 or M40 | Escalate |
| AUT-GRC-20 | Continuity plan test due | Create the test, require evidence of execution, and record the outcome and recovery objectives achieved | Escalate to CTO |
| AUT-GRC-21 | Quarter end | Assemble the board and audit-committee pack from versioned assessments, control results, obligation status and legal exposure | Retry; escalate to CFO |
| AUT-GRC-22 | Retention schedule changed | Publish the new versioned schedule to M24 and record the change with its obligation basis | Block publication; alert |

---

## 12. Interfaces

### 12.1 Upstream — M60 Consumes

| Source | What | Mechanism |
|---|---|---|
| M23 Quality | Systemic quality exposures escalated as enterprise risks; process-control weaknesses; audit findings of enterprise significance | Events + REST |
| M29 Identity & Security | Role assignments, permission grants, SoD enforcement outcomes, access review results, security incidents | Read-only API |
| M19 · M20 · M15 · M16 · M52 · M56 | Transaction data as automated control-test evidence | Read-only API + warehouse |
| M21 Core HR | Organisational structure, employment status, attestation populations | Live read |
| M24 Document | Controlled documents, evidence storage, retention enforcement status, hold status | Service call |
| M08 Contract | Contractual obligations of enterprise significance | Live read |
| M42 · M12 · M40 | Suppliers, sellers and partners as third-party risk subjects | Live read + events |
| M51 Tax | Tax obligation discharge and filing evidence | Live read |
| M18 E-Waste · M59 Safety | Environmental and safety compliance evidence; incidents as risk events | Live read + events |
| M62 Data Platform | The data map used for data-subject request fan-out; data classification | Live read |
| M13 Rental · M46 Fleet | Insurance claim originations | Events |
| `00-04` programme register | The seed risk set at handover | One-time import |

### 12.2 Downstream — M60 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M24 Document | The statutory retention schedule as versioned configuration; legal hold instructions | Command |
| M29 Identity & Security | SoD rule definitions and test outcomes; access-governance findings | Projection + events |
| M23 Quality | Acceptance or decline of escalated exposures; enterprise risks relevant to quality processes | Events |
| M19 Financial Accounting | Control definitions the finance function operates; deficiency status for the close | Projection |
| M51 Tax | Registered tax obligations and their calendar | Projection |
| M42 · M12 · M40 | Third-party risk ratings and due-diligence requirements | Projection |
| M13 · M46 · M09 | Insurance cover position relevant to claims | REST |
| M62 Data Platform | Records of processing, lawful basis and transfer register governing data movement | Projection |
| M59 Safety · M18 E-Waste | Registered obligations they discharge | Projection |
| M25 BID | Risk, control, obligation and legal fact streams | Warehouse extract |
| Board / audit committee | Quarterly governance pack, reproducible as issued | Report generation |
| External auditor / insurer / regulator | Scoped, evidenced assurance positions | Controlled release via M24 |

### 12.3 Domain Events Published

| Event | Payload Summary | Principal Consumers |
|---|---|---|
| `grc.risk_registered` | risk id, category, owner, initial score | M23, M25 |
| `grc.risk_outside_appetite` | risk id, residual score, appetite threshold | CFO, Board reporting |
| `grc.risk_review_overdue` | risk id, owner, days overdue | CFO alerting, M25 |
| `grc.control_deficiency_raised` | control id, rating, owner, due | M19, M29, M23, executive |
| `grc.sod_test_failed` | rule id, enforcement point, findings | **M29**, CTO, CFO |
| `grc.sod_exception_granted` / `expired` | rule, user, validity, approver | M29, quarterly report |
| `grc.obligation_due` / `grc.obligation_breached` | obligation, owner, consequence | Owning module, CFO |
| `grc.retention_schedule_published` | version, classes, effective_from | **M24** |
| `grc.legal_hold_instructed` / `released` | scope, matter ref | **M24** |
| `grc.licence_expiring` | licence, days remaining, consequence | CFO, CEO, owning module |
| `grc.subject_request_received` | request id, subject, type, due | All modules holding personal data |
| `grc.breach_registered` | breach id, categories, notification decision | CTO, CFO (T5 restricted) |
| `grc.third_party_rating_changed` | party, rating, required diligence | M42, M12, M40 |
| `grc.policy_published` | policy, version, attestation population | M21, M24 |
| `grc.governance_pack_issued` | period, contents hash | Board, audit committee |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-GRC-01 | External legal counsel | Bidirectional (document) | Matter status, advice, opinions — including the RSK-022 principal/agent opinion |
| INT-GRC-02 | Insurers and brokers | Bidirectional (document) | Policy documents, renewals, claim notification and settlement |
| INT-GRC-03 | Regulators (NBR, RJSC, environmental, sector) | Outbound / document | Registrations, renewals, filings evidence |
| INT-GRC-04 | Certification bodies | Inbound | Certificate status feeding the obligation register *(shared with M23)* |
| INT-GRC-05 | Regulatory update sources and counsel briefings | Inbound | Regulatory change monitoring |
| INT-GRC-06 | External auditors | Outbound (controlled release) | Evidence packs for the statutory audit |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/grc/risks` | GET/POST | Risk register | P03, P06 |
| `/api/v1/grc/risks/{id}/assess` | POST | Record a versioned assessment | P03 |
| `/api/v1/grc/risks/escalate` | POST | Escalate a systemic exposure into the register | M23 |
| `/api/v1/grc/controls` | GET/POST | Control register and mapping | P03 |
| `/api/v1/grc/controls/{id}/test` | POST | Record or trigger a control test | P03, scheduler |
| `/api/v1/grc/deficiencies` | GET | Deficiency register and remediation status | P03, P06 |
| `/api/v1/grc/sod/rules` | GET | SoD rule definitions | M29 |
| `/api/v1/grc/sod/exceptions` | GET/POST | Exception grant and register | P03, M29 |
| `/api/v1/grc/obligations` | GET/POST | Obligation register and calendar | P03, owning modules |
| `/api/v1/grc/obligations/{id}/discharge` | POST | Record discharge with evidence | Owning modules, P03 |
| `/api/v1/grc/retention-schedule` | GET | Current versioned retention schedule | **M24** |
| `/api/v1/grc/legal-holds` | POST/DELETE | Instruct and release legal holds | P03 → M24 |
| `/api/v1/grc/processing-records` | GET/POST | PDPA records of processing | P03, M62 |
| `/api/v1/grc/subject-requests` | GET/POST | Data-subject request lifecycle | P01, P03, all modules |
| `/api/v1/grc/insurance` | GET | Cover position and claims | P03, M13, M46, M09 |
| `/api/v1/grc/third-party/{id}/rating` | GET | Third-party risk rating and diligence requirement | M42, M12, M40 |
| `/api/v1/grc/governance-pack/{period}` | GET | Assembled board and audit-committee pack | P06, Board |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R03 Chief Financial Officer | C R U D A | All — the module's principal owner |
| R01 Chief Executive Officer | R A | All — appetite approval, Board escalation |
| R02 Chief Technology Officer | C R U A | Security controls, SoD testing, data protection, continuity |
| R32 Quality Manager / ISO Coordinator | C R U | Escalated quality exposures; shared obligations; audit interface |
| R26 Finance Manager | C R U | Financial controls, obligation discharge, insurance |
| R27 Finance Officer | R U | Assigned control tests and obligation occurrences |
| R30 HR Manager | R U | Employment obligations, attestation populations, speak-up interface |
| R33 IT / System Administrator | R U | Automated test configuration and scheduling |
| R05 Operations Director | R U | Operational risks and controls owned by operations |
| R19 Procurement Officer · R24 Marketplace Operations Officer | R U | Third-party risk assessments in their domain |
| R38 External Party — external auditor | R | **Scoped, approved, logged evidence release only** *(EA-01, EA-10)* |
| — Compliance Officer *(new position under R03)* | C R U | Obligations, policies, data protection, control testing coordination |
| — Control Testing Officer *(new position under R03)* | C R U | Test execution; cannot test a control they own |
| — Data Protection Owner *(designated under PDPA 2026)* | C R U A | Processing records, transfers, subject requests, breach register |

**Field-level restrictions and tiering.** Legal matters, breach records and whistleblowing cases
are **tier T5**: named allow-list, step-up authentication, every access logged *(`05-04` §4)*.
Exposure estimates and provisions are visible only to R01, R03 and R26. Third-party risk ratings
are visible to the managing module's owner but the underlying diligence findings are restricted.
`internal_note` is never exposed externally.

**Segregation of duties.** **SOD-21** *(to be registered in `05-04` §6)* — a control owner cannot
record the test conclusion for their own control. **SOD-22** — the person who grants an SoD
exception cannot be its beneficiary. Existing **SOD-01…SOD-12** are the *subject* of M60's
testing, not new rules created here.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| Enterprise risk dashboard | CEO, CFO, Board | Quarterly (live view continuous) | Heat map, top risks, movement since last review, risks outside appetite, review currency |
| Risk review currency | CFO | Monthly | Risks overdue for review, by owner and days overdue |
| Control effectiveness summary | CFO, CEO, audit committee | Quarterly | Key controls tested, effective, deficient, not testable; trend |
| Deficiency and remediation register | CFO, control owners | Monthly | Open deficiencies by rating, age and owner; overdue remediation |
| SoD testing report | CTO, CFO, audit committee | Quarterly | Rule-by-rule test result, violations found, standing exceptions *(`05-04` §6 requires this)* |
| Compliance obligation status | CFO, Compliance Officer | Monthly | Obligations due, discharged with evidence, overdue, breached |
| Licence, registration and insurance currency | CFO, CEO | Monthly | Items expiring within lead time; any lapsed |
| Regulatory change log and impact | CFO, CEO, affected owners | Per change | Change, effective date, affected obligations and controls, actions |
| Data protection position | CTO, CFO, Data Protection Owner | Quarterly | Processing records currency, transfer register, subject requests within period, breach register |
| Legal matter and exposure summary | CEO, CFO, Board | Quarterly | Matters by status, exposure, provision, next action *(restricted distribution)* |
| Third-party risk profile | CFO, Procurement, Marketplace Operations | Quarterly | Parties by rating, diligence currency, overdue reassessments |
| Business continuity test status | CTO, CFO | Semi-annual | Plans, last tested, objectives achieved, gaps |
| Policy attestation status | CFO, HR Director | Quarterly | Acknowledgement rates by policy and population; outstanding |
| **Board and audit-committee governance pack** | Board, audit committee | Quarterly | The consolidated position on risk, control, compliance, legal and insurance, reproducible as issued |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W7 Target | W9 Target |
|---|---|---|---|---|
| KPI-C60-01 | Enterprise risks with a current owner and review date | n/a *(no register exists)* | 100% | **100%** |
| KPI-C60-02 | Key controls tested per cycle | n/a | 100% | **100%** |
| KPI-C60-03 | Compliance obligations with evidence of discharge | n/a | 95% | **100%** |
| KPI-C60-04 | Licences and insurance current | manual | 100% | **100%** |
| KPI-C60-05 | Risk reviews completed on schedule | n/a | 90% | **> 98%** |
| KPI-C60-06 | Controls tested automatically rather than manually | 0% | 55% | **> 70%** |
| KPI-C60-07 | SoD rules tested per cycle | 0% | 100% | **100%** |
| KPI-C60-08 | Standing SoD exceptions | unknown | measured | **declining trend** |
| KPI-C60-09 | Deficiencies remediated within due date | n/a | 85% | **> 95%** |
| KPI-C60-10 | Obligations breached | unknown | < 3 per year | **0** |
| KPI-C60-11 | Data-subject requests fulfilled within the statutory period | n/a | 100% | **100%** |
| KPI-C60-12 | Records of processing activities current | 0% | 100% | **100%** |
| KPI-C60-13 | Cross-border transfers with a registered basis | unknown | 100% | **100%** |
| KPI-C60-14 | Policy attestation completion | n/a | 90% | **> 98%** |
| KPI-C60-15 | Continuity plans tested within schedule | 0% | 100% | **100%** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `mail`, `calendar`, `base` multi-company | 6% |
| L2 | OCA `mgmtsystem`, `mgmtsystem_action`, `mgmtsystem_hazard`, `mgmtsystem_review`, `agreement`, `queue_job` | 22% |
| L5 | `cd_risk_register`, `cd_control_framework`, `cd_control_testing`, `cd_obligation_register`, `cd_legal_matter`, `cd_policy_governance` | 72% |

> **Layer note.** The OCA `management-system` action and review machinery is reused so that M23
> and M60 share one action engine rather than two incompatible ones. Everything else is custom:
> no open-source Odoo component models an enterprise risk register, a control-testing programme
> or a PDPA records-of-processing register.

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-C60-01 | `cd_risk_register` — risk objects, appetite and scales, versioned assessment, treatment, review scheduler, heat maps, escalation from M23 | Odoo module | 5 PW |
| CD-C60-02 | `cd_control_framework` — control register, key designation, risk/obligation mapping, coverage reporting, authority register | Odoo module | 4 PW |
| CD-C60-03 | `cd_control_testing` — declarative automated test engine, manual test workflow, evidence sealing, deficiency and retest, SoD testing against M29 | Odoo module + service | 5 PW |
| CD-C60-04 | `cd_obligation_register` — obligations, calendar, discharge and evidence, regulatory change, licences, retention schedule publication | Odoo module | 4 PW |
| CD-C60-05 | `cd_legal_matter` — legal matters, holds, insurance register and claims, third-party risk, continuity governance *(all T5-aware)* | Odoo module | 2 PW |
| CD-C60-06 | `cd_policy_governance` — policy library, attestation, exceptions; PDPA processing records, transfer register, subject-request fan-out, breach register; board pack assembly | Odoo module + service | 2 PW |
| | | **Total** | **22 PW** |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M24 Document *(W3)*** | Evidence, controlled policies, retention enforcement and legal holds are the substrate |
| **M29 Identity & Security *(W1)*** | M60 tests M29's enforcement; the enforcement must exist first |
| M19 Financial Accounting *(W3)* | The largest population of testable controls |
| M23 Quality *(W5)* | The escalation source and the shared action engine |
| M21 Core HR *(W5)* | Ownership, attestation populations, employment obligations |
| M62 Data Platform *(W4/W8)* | The data map for subject-request fan-out — partial at W6, complete at W8 |
| M51 Tax *(W4)* | Tax obligations as a major register population |
| `00-04` programme register handover | The seed risk content |

> **Sequencing concern, stated plainly.** M60 is scheduled P2 in W6, yet three of its
> capabilities are needed earlier than that:
>
> - **The PDPA 2026 records of processing and transfer register** — the Act is in force *now*, and
>   the split-residency architecture is being built in Waves 1–4 without the governance artefact
>   that justifies it.
> - **The retention schedule** — M24 lands in W3 and needs a retention policy to enforce. Until
>   M60 exists, that schedule lives in `_CATEGORY_OVERVIEW.md` §7 as a document, not as versioned
>   configuration.
> - **SoD testing** — twelve rules are enforced from W1 and untested until W6.
>
> The recommendation to the programme board is to advance a **W3 slice** of CD-C60-04 (retention
> schedule publication) and CD-C60-06 (processing records and transfer register), roughly 3 PW,
> leaving the remainder in W6. This is a recommendation, not a unilateral re-plan; `02-02`
> remains authoritative until the board decides.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| `00-04` programme risk register | ~25–40 risks | `fix.risk` (those surviving programme close) | W6 |
| Trade licence, VAT/BIN, TIN, sector registrations | ~10–20 | `fix.licence` | **W3 if advanced** / W6 |
| Insurance policies in force | ~5–15 | `fix.insurance.policy` | W6 |
| Existing policies and codes of conduct | ~15–30 | `fix.policy` + M24 controlled documents | W6 |
| Statutory retention schedule | `_CATEGORY_OVERVIEW.md` §7 (14 classes) | `fix.obligation` + published retention schedule | **W3** |
| SoD rules | `05-04` §6 (12 rules) | `fix.sod.rule` | W6 |
| Approval authority matrix | `05-04` §7 (~28 thresholds) | `fix.authority.register` | W6 |
| Open legal matters | To be profiled | `fix.legal.matter` (T5) | W6 |

**Migration rule.** The programme risk register is not copied wholesale. Each risk is explicitly
triaged at handover into *closed with the programme*, *transferred to an enterprise owner*, or
*superseded*. A risk transferred without a named permanent owner and a review cadence fails
BRU-GRC-01 and cannot be migrated — which is the point.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every enterprise risk has a named owner and a future review date at all times; the system prevents saving one without both | Negative test via UI, API and ORM |
| AC-02 | A risk assessment is versioned; the prior assessment is retrievable exactly as recorded | Version-history demonstration |
| AC-03 | An overdue risk review escalates automatically and cannot be cleared without a recorded review | Compressed-timeline test |
| AC-04 | A control owner cannot record the test conclusion for their own control | SOD-21 negative test |
| AC-05 | An automated control test executes as a declared query, seals its evidence with a hash, and records "not testable" rather than a pass when evidence is unavailable | Test with induced evidence unavailability |
| AC-06 | A deficiency cannot be closed without a passed retest | Negative test |
| AC-07 | All twelve SoD rules from `05-04` §6 are tested, including by controlled violation attempt, and failures raise deficiencies | Full SoD test cycle with a deliberately mis-provisioned account |
| AC-08 | An SoD exception expires automatically on its date and appears in the quarterly standing report | Timed test + report inspection |
| AC-09 | The retention schedule published by M60 is the schedule M24 enforces; M24 has no independent retention configuration | Joint test with M24 + schema inspection |
| AC-10 | A legal hold instructed by M60 is applied by M24 transactionally and overrides retention until released | Joint test with M24 |
| AC-11 | A data-subject request fans out to every module holding that subject's personal data and is fulfilled and evidenced within the statutory period | End-to-end test across at least six modules |
| AC-12 | A cross-border transfer without a registered basis raises a compliance breach | Negative test |
| AC-13 | Legal matters, breach records and speak-up cases are inaccessible outside the allow-list, and every access is logged | T5 security test |
| AC-14 | A past quarterly board pack regenerates exactly as issued | Reproducibility test on a prior period |
| AC-15 | Named business super-users — including the CFO and CTO — sign off UAT for all P0 and P1 requirements; zero critical or high security findings | Signed UAT record + security review record |

**Definition of done:** all 17 criteria in `02-02` §8 plus the criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Should the retention-schedule publication and PDPA processing register be advanced to W3, given that M24 lands in W3 and PDPA 2026 is already in force? | CFO / CTO / Programme Board | **W2 — roadmap decision** |
| Q-02 | Who is the designated Data Protection Owner under PDPA 2026, and does the Act's Chief Data Officer obligation apply to 1000FiX at its scale? | CEO / CFO / Legal | **W3 — statutory** |
| Q-03 | Is there a Board or audit committee that will actually receive the quarterly pack, and at what cadence does it meet? A governance module without a governance body is theatre | CEO | **W5 — blocking for §5.1 and the board-pack scope** |
| Q-04 | What is the declared risk appetite per category, and who approves it — CEO, or Board? | CEO / CFO | W6 build |
| Q-05 | Which controls are designated *key*? The testing programme's cost and credibility both depend on this list being short and defensible | CFO | W6 build |
| Q-06 | Has external counsel been engaged for the RSK-022 marketplace principal/agent opinion, and where will that opinion be registered? *(cross-reference M12 Q-01)* | CFO / CEO | **W6 — blocking for M12** |
| Q-07 | Does 1000FiX carry professional indemnity and cyber cover, and what are the notification obligations under those policies? | CFO | W6 build |
| Q-08 | Is a whistleblowing channel legally required, contractually required by corporate customers, or discretionary? | CEO / Legal | W6 build |
| Q-09 | What is the statutory response period for a data-subject request under PDPA 2026, and does it differ by request type? | Legal / CFO | **W6 — statutory** |
| Q-10 | Who owns third-party risk assessment operationally — Procurement, Marketplace Operations, or a central Compliance Officer? | CFO / CCO | W6 build |

---

## 19. References

**Internal**
`03_Modules/I_Governance_Risk_Quality_and_Knowledge/_CATEGORY_OVERVIEW.md` §3, §5, §7, §8, §10 ·
`M23_Quality_Management_System.md` §3, §12 ·
`M24_Document_Records_and_ESignature.md` §3, §12 ·
`M61_Knowledge_Management_and_Technical_Library.md` §3 ·
`00_Governance_and_Charter/00-04_Risks_Assumptions_Dependencies_and_Governance.md` — the seed register, including RSK-022 ·
`00-02_Executive_Summary_and_Scope_Charter.md` §2 (split residency), §7 principle 8 ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2, §8 ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` ·
`05-04_Role_Permission_and_Access_Matrix.md` §4 (T5), §6 SOD-01…SOD-12, §7, §8 ·
`05-06_NonFunctional_Requirements_and_Standards.md` ·
`03_Modules/C_Commercial_Pricing_and_Revenue/M12_Marketplace_and_Seller_Ecosystem.md` §18 Q-01 ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md`

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §8.21, §11 ·
`1000FiX_ERP_System_Comprehensive_URD.md` §14 ·
`1000FiX_Services_Company_Profile.md` §Certifications

**External benchmark**
SAP GRC — Risk Management, Process Control, Audit Management; risk registers and obligation maps aligned to ISO 31000 / COSO; automated control testing to reduce audit cost and cycle time ·
Oracle Risk Management Cloud — embedded transaction monitoring and advanced access controls ·
COSO 2013 Internal Control — Integrated Framework ·
ISO 31000 risk management · ISO 27001 Annex A / ISO 27005 ·
Enterprise GRC platform practice (LogicGate, ServiceNow IRM, AuditBoard, Diligent) — obligation libraries, policy attestation, issue management, board reporting ·
**Bangladesh Personal Data Protection Act 2026** (in force 15 April 2026) — retention schedules and deletion procedures, records of processing retained ≥ 5 years, data-subject rights, cross-border transfer governance, Chief Data Officer obligations; note the absence of a mandatory statutory breach-notification requirement ·
Odoo 19 / OCA `management-system` action and review machinery

---

*Module M60 · Category I · 1000FiX ERP System v2.0 · CONFIDENTIAL*
