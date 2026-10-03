---
id: FIX-ERP2-M67
module_id: M67
module_code: PPM
module_name: Project, Program & Portfolio Management
category: K — Platform & Technology
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Technology Officer
system_owner: Platform Squad
priority: P2
wave: W7
---

# M67 — Project, Program & Portfolio Management
### Category K · Code `PPM` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M67 |
| **Module code** | `PPM` |
| **Category** | K — Platform & Technology |
| **Status** | ★ **New** in v2.1 — professional services automation, previously not modelled |
| **Priority** | **P2** |
| **Delivery wave** | W7 (Months 27–30) |
| **Business owner** | Chief Technology Officer *(with delivery ownership per project type — see §13)* |
| **System owner** | Platform Squad |
| **Delivery layers** | L1 Odoo `project`, `timesheet` · L2 OCA `project-*`, `management-system` · L5 custom WBS, resource, costing and milestone-billing modules |
| **Custom modules** | `cd_project`, `cd_project_resource`, `cd_project_billing` |
| **Requirement range** | FR-PPM-001 … FR-PPM-032 |
| **Requirement count** | **32** *(measured — supersedes the 26 estimate in `02-02`; **new range allocation** under `05-01` §1.3a)* |
| **Effort estimate** | **17 person-weeks** *(measured — supersedes the 14 PW estimate)* |
| **Depends on** | M30 Platform Admin · M29 Identity · M21 Core HR · M55 Workforce · M54 FP&A · M20 Receivable · M08 Contracts |
| **Depended on by** | M30, M05, M08, M12, M14, M18, M20, M54, M65, M66 |

---

## 2. Purpose

M67 exists because **1000FiX runs real projects that are not service orders**, and a service
order cannot model them.

The category overview lists five kinds:

| Project Type | Example |
|---|---|
| **Corporate rollout** | Registering and commissioning **400 devices for a new AMC client across 12 sites** |
| **IT infrastructure engagement** | Designing and installing a client's server and network refresh under an MSP contract |
| **Branch opening** | Standing up a new 1000FiX Station: premises, fit-out, stock, staffing, systems, licences |
| **Bulk decommission** | A corporate client retiring **300 assets** with data destruction and buy-back |
| **Internal initiative** | **The ERP programme itself, and each of its nine waves** |

A service order is one job, one device, one promise, closed in hours or days. A corporate
rollout is a six-month engagement with phases, a budget, a resource plan, dependencies, risks
and milestone billing. Forcing the second into the shape of the first produces either a
distorted service order or — far more likely — a spreadsheet running alongside the ERP, which
is precisely the fragmentation the programme exists to remove.

That is a recognised ERP module in every benchmark system: Oracle **Project Portfolio
Management**, SAP **Project System**, Dynamics 365 **Project Operations**, Odoo **Project +
Timesheets**.

### Why It Exists

**Because corporate work is where the growth is.** BO-11 targets managed services at ≥ 12% of
revenue and BO-12 targets marketplace at ≥ 25% of job volume. Corporate rollouts and
infrastructure engagements are how AMC and MSP contracts actually begin. Winning a 400-device
AMC and then commissioning it on a spreadsheet is how a good contract becomes an unprofitable
one.

**Because branch openings are recurring and expensive.** The 1000FiX Station programme is a
stated growth initiative. M30 provisions a branch in the system in under a day; the *project*
around it — premises, fit-out, stock, staffing, licences, launch — runs for weeks and involves
six departments.

**Because project profitability is currently unknowable.** Without a project object carrying
its own cost and revenue, the margin on a six-month engagement is an estimate made afterwards.

**Because the programme itself needs managing.** Nine waves, 67 modules, ~1,302 person-weeks
and a $455K–780K budget. The category is explicit that the ERP programme is itself a project
M67 should model — which it can only do from Wave 7 onward, an irony worth stating plainly.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| `_CATEGORY_OVERVIEW.md` §4 | **The five project types with concrete examples**, the argument that "a service order cannot model a six-month engagement with phases, a budget, a resource plan and milestone billing", and the four benchmark analogues |
| `_CATEGORY_OVERVIEW.md` §6 | M67 owns "project structure, budget, resource plan, milestone billing" — **not M01 (service orders), not M20 (invoicing)** |
| `_CATEGORY_OVERVIEW.md` §9 | **Projects delivered on time and on budget > 80%** |
| `_CATEGORY_OVERVIEW.md` §11 | Risk: "Corporate rollouts run on spreadsheets alongside the ERP — Medium, **the exact fragmentation the programme exists to remove**". Mitigation: "M67 delivered before the marketplace and expansion waves" |
| `02-01` §9 | The nine business lines and their order/work/billing objects — M67 supplies the missing project shape for engagement-based work |
| `06-02` BO-11, BO-12, BO-13, BO-14 | Managed services, marketplace, rental and circular-business objectives, all of which involve engagement-shaped corporate work |
| `06-01` | The nine-wave implementation roadmap — the internal programme M67 models from W7 |
| `05-06` NFR-058 | 200 branches without configuration redesign — implying a continuing branch-opening pipeline |
| `05-04` §7 | Approval authority matrix — project budgets and change requests route through it |
| `02-05` §5.1 | ~1,302 person-weeks across 80 custom deliverables — the internal programme's scale |

---

## 3. Scope Boundary

> **The rule:** M67 owns **work organised as a project** — bounded by a start and an end, with
> phases, a budget, a resource plan and a defined outcome. It does not own repeatable
> operational work, and it does not create financial documents.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Project object with type, sponsor, manager, client, contract reference, dates and status |
| 2 | **Project templates per type** — corporate rollout, IT infrastructure engagement, branch opening, bulk decommission, internal initiative |
| 3 | **Work breakdown structure**: phases, work packages, tasks, deliverables and acceptance criteria |
| 4 | Scheduling with dependencies, critical path, baselines and rescheduling |
| 5 | **Milestones** with acceptance criteria and evidence |
| 6 | Task assignment, progress capture and completion evidence |
| 7 | **Resource planning**: role-based demand, named assignment, availability and capacity |
| 8 | Resource conflict detection across projects and against operational commitments |
| 9 | Skill and certification matching for project roles |
| 10 | Effort recording against project tasks |
| 11 | **Project budget**: labour, parts, subcontract, travel, equipment and overhead |
| 12 | **Project cost capture** from every contributing module — time, parts, logistics, subcontract, expenses |
| 13 | Committed, incurred and forecast cost tracking |
| 14 | **Earned value and progress measurement** against baseline |
| 15 | **Milestone and progress billing**: raising billable events to M20 on milestone acceptance |
| 16 | Fixed-price, time-and-materials and internal (non-billable) project types |
| 17 | **Project profitability**: revenue, cost and margin per project |
| 18 | Risk register per project with likelihood, impact, owner and mitigation |
| 19 | Issue log with escalation |
| 20 | **Project change control**: scope change with cost, schedule and approval consequence |
| 21 | Dependency management between projects and on operational modules |
| 22 | **Programme grouping**: related projects managed together with shared milestones and reporting |
| 23 | **Portfolio view**: all projects with status, budget, resource demand and health |
| 24 | Stage gates with go/no-go decisions and evidence |
| 25 | Project documents, plans and deliverable register through M24 |
| 26 | Client-facing project status for the corporate portal |
| 27 | Project closure: acceptance, lessons learned, benefit realisation, resource release |
| 28 | Portfolio-level resource capacity planning and pipeline demand |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Service orders, work orders, repair jobs** | **M01** / **M31** / **M02** | The defining boundary. A project *generates* service orders — a 400-device rollout creates 400 commissioning jobs — but the jobs remain M01's, executed and measured as service work |
| **Invoice creation, credit notes, revenue recognition** | **M20** Receivable / **M53** Revenue | **M67 raises a billable event on milestone acceptance; M20 invoices.** Only Category G creates financial documents |
| Journal posting, cost accounting, budget ownership | **M19** / **M54** | M67 captures project cost and raises cost events; M19 posts, M54 owns the budget framework |
| Contract negotiation, terms, entitlements, renewal | **M08** Contract Lifecycle | A project delivers against a contract; it does not own it |
| **MSP contract, monitoring, client tickets, client SLA** | **M05** | An infrastructure engagement is a project; the ongoing managed service that follows it is M05 |
| Employee record, employment, roster, payroll, leave | **M21** / **M55** / **M56** | M67 plans resource demand; M55 owns the roster and availability |
| Technician dispatch to a job | **M02** | Project tasks are not dispatched jobs |
| **Branch provisioning in the system** | **M30** | **M30 provisions the branch in under a day; M67 manages the weeks-long project around it** |
| Premises, fit-out, utilities, physical infrastructure | **M47** Facility | M67 tracks the fit-out as a work package; M47 executes it |
| Stock for a new branch | **M15** | M67 tracks the opening-stock milestone; M15 owns the stock |
| **IT change management** | **M66** | A change is a controlled alteration; a project is bounded work with a budget. M66 runs changes, including those a project requires |
| Country onboarding as a system capability | **M65** | M65 makes the system ready; **M67 manages the market-entry programme around it** |
| Data destruction and disposal certification | **M06** / **M18** | A bulk decommission project *sequences* them; it does not perform them |
| Trade-in valuation and buy-back pricing | **M14** | — |
| Marketplace seller job allocation | **M12** | Buying delivery capacity is not project resourcing |
| Quality management system, audits, CAPA | **M23** | M67 raises quality signals from lessons learned |
| Enterprise risk register | **M60** GRC | **M67 owns project risk; M60 aggregates enterprise risk** |

### 3.3 Shared Concepts

| Concept | M67's Role | Owning Module |
|---|---|---|
| Project | **Owns** | M67 |
| Service order generated by a project | Creates and tracks; M01 owns its lifecycle | M67 / M01 |
| Contract | Reads as the commercial basis and billing terms | M08 |
| Milestone | **Owns**; raises a billable event to M20 on acceptance | M67 / M20 |
| Billable event | **Raises**; M20 invoices | M67 / M20 |
| Resource and availability | Owns project demand and assignment; M55 owns the roster and true availability | M67 / M55 |
| Timesheet | **Owns** project effort; M55 owns attendance | M67 / M55 |
| Project cost | **Owns** the aggregation; contributing modules own their source records | M67 / M15, M03, M16, M52 |
| Budget | Owns the project budget; M54 owns the budget framework and cost centres | M67 / M54 |
| Risk | Owns project risk; M60 aggregates | M67 / M60 |
| Branch opening | Owns the project; **M30 provisions the system** | M67 / M30 |
| Change | Owns project scope change; **M66 owns IT change** | M67 / M66 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Microsoft Dynamics 365 Project Operations** | Work breakdown structures, task assignment, milestone tracking, real-time progress; **multiple project types — time-and-materials, fixed-price and internal**; resource management showing availability, skills and current allocation; project financials tracking cost, revenue and profitability through the life of the project, with **automated billing milestones and real-time cost tracking** | **Project Operations is the primary reference for M67.** Adopted directly: the **three project types**; **resource management by availability, skill and current allocation** — which is what prevents overbooking and idle capacity; and **milestone-driven billing with live cost tracking**, so profitability is known during delivery rather than reconstructed after it | The full opportunity-to-cash professional-services suite. 1000FiX's engagements are won through M07 and M36, not through a PSA pipeline |
| **Oracle Project Portfolio Management** — Project Management, Costing, Billing | The three-part decomposition: manage the work, capture the cost, bill the client | **The three-part decomposition is M67's structure** — and it maps cleanly onto our boundary, because **Billing raises the event and Category G creates the document** | Oracle's project accounting depth and its costing-rule engine; ours aggregates cost from source modules rather than re-deriving it |
| **SAP Project System (PS) / Commercial Project Management** | WBS as the cost-collection spine; network activities; milestone billing plans | **The WBS as the cost-collection object** — every cost, from a technician hour to a part to a courier movement, attaches to a work package, which is what makes project profitability real rather than allocated | SAP PS's network and activity model; a task-and-dependency model is sufficient at our project sizes |
| **NetSuite SuiteProjects / PSA practice** | Projects, billing and finance in one system for services firms | The principle that **project, cost and billing must be in the same system as operations** — the alternative is the spreadsheet the category risk names | — |
| **Earned value management (PMI practice)** | Planned value, earned value and actual cost giving objective progress and forecast | **Earned value as the progress measure**, because "80% done" reported by the person doing the work is not a measurement. Applied to fixed-price and internal projects where it earns its keep | Full EVM formalism with CPI/SPI-driven contract mechanics on every project; disproportionate for a two-week branch opening |
| **Stage-gate practice** | Go/no-go decisions at defined points with evidence | **Stage gates on project types with material commitment** — corporate rollout, branch opening, country entry — so that a project can be stopped at a defined point rather than only when the money runs out | Stage gates on every project type; a bulk decommission does not need four gates |

**Design position.** Five deliberate differences.

First, **a project generates service orders; it does not replace them**. A 400-device rollout
creates 400 commissioning jobs in M01, each dispatched, executed, evidenced and QC'd exactly
like any other job. M67 owns the *engagement* — the phases, the budget, the resource plan, the
milestones — and tracks the jobs as deliverables within it. This keeps operational execution in
one place and avoids a second, parallel work-management system.

Second, **M67 raises billable events and never creates a financial document**. Milestone
acceptance produces an event; M20 turns it into an invoice. This is the same rule Category A
follows, and it exists so that revenue recognition, tax treatment and credit control stay in
one place.

Third, **the branch-opening boundary with M30 is drawn deliberately**. M30 provisions the
*system* side of a branch in under a day. M67 manages the *project* — premises, fit-out, stock,
staffing, licences, launch — which runs for weeks across six departments. Both are needed, and
conflating them would either make M30 a project tool or make M67 a provisioning tool.

Fourth, **project resource planning defers to operational reality**. M67 plans demand by role
and skill; **M55 owns the roster and what people are actually available to do**. A project plan
that assumes a technician is free while M02 has dispatched them is a plan that fails on contact
with a Tuesday. M67 therefore reads availability rather than asserting it, and conflict
detection spans both project and operational commitments.

Fifth, **M67 arrives late and models the programme that built it**. Wave 7 placement means the
ERP programme itself runs on other tools for six waves. The category positions M67 *before* the
marketplace and expansion waves, which is the right trade — corporate rollouts and branch
openings are happening now — but the irony should be recorded rather than glossed: the module
that would have managed the programme arrives in its seventh wave.

---

## 5. Functional Areas & Features

### 5.1 Project Structure & Templates

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PPM-001 | Project object | Create a project with type, name, sponsor, manager, client party, contract reference, business line, cost centre, planned dates, budget and status | **P0** | L1/L5 |
| FR-PPM-002 | **Project templates by type** | Provide templates for the five project types — corporate rollout, IT infrastructure engagement, branch opening, bulk decommission, internal initiative — each carrying its standard phases, work packages, milestones, roles and stage gates | **P0** | L5 |
| FR-PPM-003 | **Work breakdown structure** | Model a project as phases → work packages → tasks, each with owner, effort estimate, dates, dependencies, deliverables and acceptance criteria | **P0** | L1/L5 |
| FR-PPM-004 | Deliverable register | Register every deliverable with its acceptance criteria, evidence requirement, reviewer and acceptance status | **P0** | L5 |
| FR-PPM-005 | Project classification | Classify as fixed-price, time-and-materials or internal (non-billable), driving the costing and billing model | **P0** | L5 |
| FR-PPM-006 | **Programme grouping** | Group related projects into a programme with shared milestones, consolidated reporting and cross-project dependencies | P1 | L5 |
| FR-PPM-007 | Stage gates | Define go/no-go gates per project type with required evidence, decision authority and recorded outcome | P1 | L5 |

### 5.2 Scheduling, Progress & Change

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PPM-008 | Scheduling and dependencies | Schedule tasks with finish-to-start and other dependency types, compute the critical path, and reschedule downstream work when a predecessor moves | **P0** | L5 |
| FR-PPM-009 | Baseline | Baseline the schedule and budget at approval, and measure all subsequent variance against it | **P0** | L5 |
| FR-PPM-010 | **Milestones and acceptance** | Define milestones with acceptance criteria and evidence; record client or sponsor acceptance; **raise the billable event on acceptance where the project is billable** | **P0** | L5 |
| FR-PPM-011 | Progress capture | Capture task progress with completion evidence, and roll it up through work package, phase and project | **P0** | L5 |
| FR-PPM-012 | **Earned value** | Compute planned value, earned value and actual cost, and report schedule and cost variance and forecast at completion | P1 | L5 |
| FR-PPM-013 | **Project change control** | Raise a scope change with its cost, schedule and resource consequence; route for approval against the `05-04` §7 authority matrix; re-baseline on approval | **P0** | L5 |
| FR-PPM-014 | Risk register | Maintain project risks with likelihood, impact, owner, mitigation and status; escalate material risks to M60 | **P0** | L2/L5 |
| FR-PPM-015 | Issue log | Log issues with owner, severity and escalation path, and link them to tasks, risks and changes | **P0** | L5 |
| FR-PPM-016 | Cross-module dependency | Track dependencies on operational modules — stock availability from M15, provisioning from M30, certificates from M06, disposal from M18 — and surface a blocked project task when the dependency is not met | P1 | L5 |

### 5.3 Resource Management

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PPM-017 | **Role-based resource demand** | Plan demand by role, skill and certification over time, before named people are assigned | **P0** | L5 |
| FR-PPM-018 | **Named assignment against real availability** | Assign named resources using **availability from M55 and current allocation from M02 and other projects** — never an assumption of freedom | **P0** | L5 |
| FR-PPM-019 | Skill and certification matching | Match candidates by skill and current certification from M22, and prevent assignment where a required certification has lapsed | **P0** | L5 |
| FR-PPM-020 | **Conflict detection** | Detect and surface conflicts across projects and against operational commitments, with the competing demand named | **P0** | L5 |
| FR-PPM-021 | Effort recording | Record effort against project tasks, from the technician application, the portal or bulk entry, and reconcile it with M55 attendance | **P0** | L1/L5 |
| FR-PPM-022 | Subcontract and partner resource | Plan and track subcontracted resource procured through M16 or allocated through M12, with its cost attaching to the work package | P2 | L5 |
| FR-PPM-023 | **Portfolio capacity planning** | Aggregate committed and pipeline demand by role across the portfolio against available capacity, and forecast shortfalls ahead of commitment | P1 | L5 |

### 5.4 Cost, Billing & Profitability

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PPM-024 | **Project budget** | Budget by cost category — labour, parts, subcontract, travel, equipment, overhead — at work-package level, approved against the `05-04` §7 authority matrix | **P0** | L5 |
| FR-PPM-025 | **Cost capture from source modules** | Attach cost to the work package from every contributing source: effort valued at role cost, parts from M15, logistics from M03, subcontract and purchases from M16 and M52, expenses from M52 | **P0** | L5 |
| FR-PPM-026 | Committed, incurred and forecast | Track committed cost (raised, not yet incurred), incurred cost and forecast at completion, against budget | **P0** | L5 |
| FR-PPM-027 | Budget control | Warn at configurable consumption thresholds and require approval for a project to exceed its approved budget | **P0** | L5 |
| FR-PPM-028 | **Milestone and progress billing** | Raise billable events to M20 on milestone acceptance for fixed-price projects, and on approved effort and cost for time-and-materials projects, per the contract's billing schedule in M08 | **P0** | L5 |
| FR-PPM-029 | **Project profitability** | Report revenue, cost and margin per project, work package and project type, in real time rather than at closure | **P0** | L5 |

### 5.5 Portfolio, Reporting & Closure

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PPM-030 | **Portfolio dashboard** | Present every project with status, health, schedule and budget variance, resource demand, open risks and issues, and stage-gate position | **P0** | L5 |
| FR-PPM-031 | Client-facing project view | Expose project status, milestones, deliverables and acceptance requests to the corporate client through P04, scoped to their own project | P1 | L5 |
| FR-PPM-032 | **Project closure and benefit realisation** | Close a project with final acceptance, financial closure, resource release, deliverable handover, **lessons learned fed to M23**, and — for internal initiatives — benefit realisation measured against the case that justified it | **P0** | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Project generates, never replaces, operational work** | Service orders created from a project remain M01 objects with M01's lifecycle. M67 holds the reference and tracks completion; it does not own the job |
| T-02 | **Billable event, never a financial document** | M67 emits `project.milestone_billable`; M20 creates the invoice. M67 has no invoice model and no posting path |
| T-03 | **Cost aggregation, not re-derivation** | Project cost aggregates source records by reference. The source module remains authoritative; a correction at source flows through rather than being re-entered |
| T-04 | **Availability is read, never asserted** | Resource availability resolves from M55 rosters and M02 dispatch commitments at assignment time. M67 holds no independent calendar |
| T-05 | **Certification gate at assignment** | Assignment checks current certification with M22 and blocks where it has lapsed, mirroring M02's dispatch eligibility rule |
| T-06 | **Baseline immutability** | An approved baseline is immutable. Re-baselining creates a new version with the approved change that caused it; variance is always measurable against the original |
| T-07 | **Critical path performance** | Schedule and critical-path recomputation for a 500-task project completes in ≤ 2 s; a portfolio-wide resource conflict scan in ≤ 30 s |
| T-08 | **Earned value determinism** | Earned value uses a declared measurement method per work package — milestone, percent complete, or units delivered — recorded on the package so the number can be explained |
| T-09 | **Cross-module dependency observation** | Dependencies on M15 stock, M30 provisioning, M06 certificates and M18 disposal are observed through events rather than polled, and a blocked task surfaces within minutes |
| T-10 | **Multi-entity and cost-centre scoping** | Projects carry `company_id`, `operating_unit_id`, `cost_center_id` and `business_line_id` (AS-03), so portfolio reporting works across entities from day one |
| T-11 | **Client-scope isolation** | A corporate client sees only their own project, with no cost, margin or internal note exposure (EA-01, EA-02) |
| T-12 | **Scale envelope** | ~60 concurrent projects, ~15,000 tasks, ~400 resources, ~2,000 timesheet entries per week at Wave 8 |
| T-13 | **Template versioning** | A project instantiated from a template records the template version, so a template improvement does not retrospectively alter a running project |
| T-14 | **Bilingual delivery surface** | Task lists, acceptance requests and the client view are complete in Bengali and English (AS-12) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M67 |
|---|---|---|
| **Account manager** | Wins a 400-device AMC and hands it to operations with an email | Hands over a structured rollout project with phases, milestones and a resource plan |
| **Project / delivery lead** | Runs the engagement on a spreadsheet alongside the ERP | Runs it in the system, with cost and progress live |
| **Operations director** | Cannot see how many engagements are running or what they demand | A portfolio view with resource demand and health |
| **Technician** | Receives rollout work indistinguishable from ordinary jobs | Same job experience; the effort attributes to the project automatically |
| **Branch opening lead** | Coordinates six departments by phone and checklist | One project with dependencies, owners and a stage gate before launch |
| **Finance** | Learns a project's margin months after it ends | Sees committed, incurred and forecast cost against budget during delivery |
| **CFO** | Cannot answer which project types are profitable | Margin by project, work package and type |
| **Corporate client** | Asks for a progress update by email | Sees status, milestones and acceptance requests in P04 |
| **CEO / programme sponsor** | Tracks the ERP programme outside the ERP | The programme modelled as a programme, with benefit realisation measured |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Corporate engagement profitability** | Budget, live cost capture and margin per project | **The primary benefit.** A 400-device rollout delivered 15% over an unmeasured budget converts a won contract into a loss. Directly protects **BO-11 (MSP ≥ 12% of revenue)** and the **BDT 95 lac/year** managed services contribution |
| **Spreadsheet elimination** | Projects run in the system, not beside it | The explicit category risk — "the exact fragmentation the programme exists to remove". Every parallel spreadsheet is a divergence waiting to be discovered |
| **On-time, on-budget delivery** | Baseline, earned value, change control and stage gates | **> 80% of projects delivered on time and on budget** — the category KPI, against an unmeasured baseline |
| **Branch opening reliability** | A template with dependencies, owners and a launch gate | With the 1000FiX Station programme active, each opening delayed by a missed dependency is lost revenue days and a compressed launch |
| **Resource utilisation** | Named assignment against real availability, with conflict detection | Prevents both overbooking (a technician double-committed) and idle capacity (a specialist unassigned) — the Dynamics 365 pattern applied to a 400-technician workforce |
| **Billing accuracy and speed** | Milestone acceptance raises the billable event immediately | Removes the delay and dispute of reconstructing what was delivered. Supports **KPI-054 (invoice within 1 hour)** and **KPI-056 (revenue leakage < 0.5%)** for engagement work |
| **Bulk decommission delivery** | Sequenced project across M06 destruction, M14 buy-back and M18 disposal | A 300-asset decommission touches four modules and a client's compliance obligations; it is a project or it is a mess. Supports **BO-14 (circular business)** |
| **Scope change capture** | Scope change priced, approved and re-baselined | Uncaptured scope creep is the standard failure mode of fixed-price engagements |
| **Portfolio capacity foresight** | Pipeline demand against capacity by role | Prevents committing to an engagement the Company cannot resource — a commercial decision currently made on instinct |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Corporate and government tender credibility** | Larger clients ask how an engagement will be governed, resourced and reported. A demonstrable PPM capability is a bid differentiator |
| **Delivery discipline** | Stage gates, baselines and change control transfer a way of thinking beyond the projects themselves |
| **Institutional learning** | Lessons learned captured and fed to M23 rather than lost when the team disperses |
| **ISO 9001 evidence** | Planning, resource provision, change control and review are explicit clauses |
| **Benefit realisation honesty** | Internal initiatives measured against the case that justified them — including the ERP programme itself |
| **Career structure** | A project-management discipline gives operations staff a progression route beyond branch and workshop roles |
| **Expansion capability** | Country entry (M65) is a programme. Without M67 it is run on a spreadsheet, which is how the 12-week gate gets missed |

---

## 8. Lifecycle & State Models

### 8.1 Project Lifecycle

```
   Origin: M07 opportunity won · M08 contract activated ·
           branch opening approved · internal initiative sponsored
        │
   ┌────▼──────────┐
   │   PROPOSED    │  type · sponsor · outline scope · indicative budget
   └────┬──────────┘
        │ **stage gate 1 — proceed to plan?** (FR-PPM-007)
   ┌────▼──────────┐
   │   PLANNING    │  template instantiated · WBS · schedule ·
   └────┬──────────┘  resource demand · budget · risks
        │ **stage gate 2 — approve budget and baseline**
        │ routed by the `05-04` §7 authority matrix
        │  ✖ resource shortfall unresolved ──► held
   ┌────▼──────────┐
   │   APPROVED    │  **baseline set and immutable** (T-06)
   └────┬──────────┘
        │ resources assigned against real availability (T-04)
   ┌────▼──────────┐
   │  IN DELIVERY  │◄─────────────────────┐
   └──┬──┬──┬──┬───┘                      │
      │  │  │  │                          │ approved change
      │  │  │  └──► scope change raised ──┤ **re-baselined**
      │  │  │                             │ (new version; original retained)
      │  │  │ dependency unmet            │
      │  │  └──► **BLOCKED** ─────────────┘ (M15 stock · M30 provisioning ·
      │  │                                   M06 certificate · M18 disposal)
      │  │ sponsor decision
      │  └──► ON HOLD ──────────────────► resumed
      │
      │ all deliverables accepted
   ┌──▼────────────┐
   │  DELIVERED    │  final milestone accepted; billable events raised
   └──┬────────────┘
      │ financial closure: all cost captured, all billing raised
   ┌──▼────────────┐
   │    CLOSING    │  resource release · deliverable handover ·
   └──┬────────────┘  **lessons learned → M23** · benefit realisation
      │
   ┌──▼────────────┐
   │    CLOSED     │  final margin recorded; retained for reporting
   └───────────────┘

   ┌───────────────┐
   │  CANCELLED    │  ◄── from any state at a stage gate or sponsor decision:
   └───────────────┘      cost captured to date · resources released ·
                          billing position settled · reason recorded
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Proposed | Opportunity won, contract activated, branch approved, or initiative sponsored | Account manager / sponsor |
| Proposed | Planning | Stage gate 1 passed | Sponsor / delivery owner |
| Planning | Approved | **Budget approved per `05-04` §7; baseline set; resource demand satisfiable** | Approver per matrix |
| Approved | In delivery | Resources assigned against real availability; certifications current | Project manager |
| In delivery | Blocked | A cross-module dependency is unmet | System |
| In delivery | On hold | Sponsor decision | Sponsor |
| In delivery | In delivery *(re-baselined)* | Scope change approved with cost and schedule consequence | Approver per matrix |
| In delivery | Delivered | Every deliverable accepted; final milestone signed | Client / sponsor |
| Delivered | Closing | All cost captured; all billable events raised | Project manager + Finance |
| Closing | Closed | Financial closure, resource release, handover, lessons learned, benefit realisation | Sponsor + Finance |
| Any | Cancelled | Stage gate failed or sponsor decision; cost and billing settled | Sponsor + CFO |

### 8.2 Milestone & Billing

```
   MILESTONE DEFINED ──► acceptance criteria · evidence requirement · reviewer
        │
   ┌────▼──────────┐
   │  IN PROGRESS  │  dependent tasks executing
   └────┬──────────┘
        │ all dependent tasks complete; evidence attached
   ┌────▼──────────┐
   │ READY FOR     │ ──► acceptance requested from client (P04) or sponsor
   │ ACCEPTANCE    │
   └──┬─────────┬──┘
      │         │ rejected with reason
      │    ┌────▼──────────┐
      │    │   REWORK      │ ──► returns to in progress
      │    └───────────────┘
      │ accepted with evidence
   ┌──▼────────────┐
   │   ACCEPTED    │
   └──┬────────────┘
      │ project is billable (fixed-price milestone, or T&M approved cost)
   ┌──▼──────────────────────┐
   │ **BILLABLE EVENT RAISED**│ ──► **M20 creates the invoice**
   │ (M67 raises; M20 invoices)│      M67 never creates a financial document
   └──┬──────────────────────┘
      │ M20 confirms invoiced
   ┌──▼────────────┐
   │    BILLED     │ ──► project revenue recognised by M53
   └───────────────┘
```

### 8.3 Resource Assignment

```
   ROLE DEMAND ──► by role, skill, certification, over a period (FR-PPM-017)
        │
   ┌────▼──────────────────────────┐
   │  CANDIDATE RESOLUTION         │
   │  skills + current certification (M22)                 │
   │  + roster availability (M55)                          │
   │  + operational commitments (M02)                      │
   │  + other project assignments                          │
   └────┬──────────────────────┬───┘
        │ candidate available  │ **conflict** — competing demand named
        │                 ┌────▼──────────────┐
        │                 │  CONFLICT RAISED  │ ──► resolved by priority
        │                 └────┬──────────────┘      or re-planned
        │◄─────────────────────┘
   ┌────▼──────────┐
   │   ASSIGNED    │  ✖ blocked if a required certification has lapsed (T-05)
   └────┬──────────┘
        │ work performed; effort recorded
   ┌────▼──────────┐
   │   ENGAGED     │  effort valued at role cost → work package
   └────┬──────────┘
        │ work package complete, or project closes
   ┌────▼──────────┐
   │   RELEASED    │  capacity returns to the pool
   └───────────────┘
```

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-PPM-01 | **A project generates service orders; it never replaces them.** Operational work executes and is measured in M01, M02 and M31 | **H** | CTO |
| BRU-PPM-02 | **M67 raises billable events; only M20 creates invoices.** M67 has no invoice model | **H** | CFO |
| BRU-PPM-03 | A project cannot enter delivery without an approved budget and a set baseline | **H** | CFO |
| BRU-PPM-04 | Project budget approval follows the `05-04` §7 authority matrix by value | **H** | CFO |
| BRU-PPM-05 | An approved baseline is immutable; re-baselining creates a new version linked to the approved change | **H** | CTO |
| BRU-PPM-06 | A scope change is priced for cost and schedule consequence and approved before work proceeds on it | **H** | CFO |
| BRU-PPM-07 | Exceeding the approved budget requires approval at the band of the new total | **H** | CFO |
| BRU-PPM-08 | **Resource assignment uses availability from M55 and commitments from M02; M67 holds no independent calendar** | **H** | CTO |
| BRU-PPM-09 | A resource whose required certification has lapsed cannot be assigned to a task requiring it | **H** | Quality Manager |
| BRU-PPM-10 | A resource conflict must be surfaced with the competing demand named; silent double-booking is a defect | **H** | Operations Director |
| BRU-PPM-11 | A billable event is raised only on recorded milestone acceptance with its evidence | **H** | CFO |
| BRU-PPM-12 | Project cost aggregates from source modules by reference; cost is never re-entered in M67 | **H** | CFO |
| BRU-PPM-13 | A project cannot close with uncaptured cost or unraised billable events | **H** | CFO |
| BRU-PPM-14 | A project cannot close without lessons learned recorded and passed to M23 | **H** | Quality Manager |
| BRU-PPM-15 | An internal initiative cannot close without benefit realisation measured against its business case | **H** | CFO / CEO |
| BRU-PPM-16 | A stage gate decision is recorded with its evidence and decision authority; a gate cannot be passed implicitly | **H** | Sponsor |
| BRU-PPM-17 | A task blocked by an unmet cross-module dependency is surfaced, not silently delayed | **C** | CTO |
| BRU-PPM-18 | A corporate client sees only their own project, and never cost, margin or internal notes (EA-01, EA-02) | **H** | CTO |
| BRU-PPM-19 | A project instantiated from a template records the template version; a template change never alters a running project | **C** | CTO |
| BRU-PPM-20 | Material project risks are escalated to M60's enterprise risk register | **C** | CFO |
| BRU-PPM-21 | Effort recorded against a project reconciles with M55 attendance; an unreconcilable variance is reported | **C** | HR Director / CFO |
| BRU-PPM-22 | A cancelled project settles its billing position and releases its resources before closure | **H** | CFO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.project` | `fix_project` | **The project** | number, name, type (corporate_rollout/it_infrastructure/branch_opening/bulk_decommission/internal), template_id, template_version, classification (fixed_price/time_and_materials/internal), sponsor_id, manager_id, client_party_id, contract_id, programme_id, company_id, operating_unit_id, cost_center_id, business_line_id, planned_start, planned_end, baseline_id, state, health, budget_total, forecast_total |
| `fix.project.template` | `fix_project_template` | Template per type | type, name, version, phases, work_packages, milestones, roles, stage_gates, default_duration, active |
| `fix.project.phase` | `fix_project_phase` | Phase within a project | project_id, sequence, name, planned_start, planned_end, actual_start, actual_end, state, gate_id |
| `fix.project.work.package` | `fix_project_work_package` | **The cost-collection object** | project_id, phase_id, code, name, owner_id, effort_estimate, budget_by_category_json, ev_measurement_method, planned_value, earned_value, actual_cost, state |
| `fix.project.task` | `fix_project_task` | Task within a work package | work_package_id, name, assignee_id, role_required, skill_required, certification_required, effort_estimate, planned_start, planned_end, actual_start, actual_end, percent_complete, state, blocked_by_dependency_id |
| `fix.project.dependency` | `fix_project_dependency` | Task and cross-module dependencies | predecessor_type (task/module_event), predecessor_ref, successor_task_id, dependency_type, lag, satisfied, satisfied_at |
| `fix.project.deliverable` | `fix_project_deliverable` | Deliverable register | project_id, work_package_id, name, acceptance_criteria, evidence_requirement, reviewer_id, submitted_at, accepted_at, accepted_by, rejection_reason, document_ids |
| `fix.project.milestone` | `fix_project_milestone` | **Milestone and billing trigger** | project_id, name, acceptance_criteria, planned_date, dependent_task_ids, state, evidence_ids, accepted_at, accepted_by, billable, billing_amount, billable_event_raised_at, m20_invoice_ref |
| `fix.project.baseline` | `fix_project_baseline` | Immutable approved plan | project_id, version, schedule_snapshot, budget_snapshot, approved_by, approved_at, superseded_by_change_id |
| `fix.project.change` | `fix_project_change` | Scope change control | project_id, number, description, justification, cost_impact, schedule_impact_days, resource_impact, requested_by, approvers, decision, decided_at, new_baseline_id |
| `fix.project.stage.gate` | `fix_project_stage_gate` | Go/no-go decision | project_id, gate_name, criteria, evidence_ids, decision (go/no_go/conditional), conditions, decided_by, decided_at |
| `fix.project.risk` | `fix_project_risk` | Project risk register | project_id, description, likelihood, impact, score, owner_id, mitigation, state, escalated_to_m60_ref, reviewed_at |
| `fix.project.issue` | `fix_project_issue` | Issue log | project_id, description, severity, owner_id, raised_at, escalation_level, linked_task_id, linked_risk_id, resolved_at, resolution |
| `fix.project.resource.demand` | `fix_project_resource_demand` | Role-based demand | project_id, work_package_id, role, skill_required, certification_required, quantity, period_from, period_to, hours_required, fulfilled |
| `fix.project.assignment` | `fix_project_assignment` | Named assignment | demand_id, task_id, employee_id, allocation_pct, period_from, period_to, availability_source, conflict_ref, certification_verified_at, state |
| `fix.project.conflict` | `fix_project_conflict` | Detected resource conflict | employee_id, period, competing_demands_json, competing_source (project/dispatch/roster), severity, resolution, resolved_at |
| `fix.project.timesheet` | `fix_project_timesheet` | Effort against tasks | task_id, employee_id, date, hours, description, source (app/portal/bulk), role_cost_rate, cost_value, approved_by, m55_attendance_ref, reconciled |
| `fix.project.cost` | `fix_project_cost` | **Aggregated cost by reference** | project_id, work_package_id, category (labour/parts/subcontract/travel/equipment/overhead), source_module, source_document_type, source_document_id, amount, currency, committed, incurred, occurred_at |
| `fix.project.budget` | `fix_project_budget` | Budget by category | project_id, work_package_id, category, budgeted_amount, committed_amount, incurred_amount, forecast_amount, variance, threshold_warned_at, approved_by |
| `fix.project.billable.event` | `fix_project_billable_event` | **Raised to M20, never invoiced here** | project_id, milestone_id, type (milestone/progress/time_and_materials), amount, currency, contract_id, billing_schedule_ref, raised_at, m20_acknowledged_at, invoice_ref |
| `fix.project.profitability` | `fix_project_profitability` | Margin position | project_id, period, revenue_recognised, revenue_billed, cost_incurred, cost_forecast, margin, margin_pct, computed_at |
| `fix.programme` | `fix_programme` | Programme grouping | name, sponsor_id, project_ids, shared_milestones, objective, business_case_ref, state, start, end |
| `fix.project.lessons` | `fix_project_lessons` | Lessons learned | project_id, category, observation, recommendation, recorded_by, m23_reference, actioned |
| `fix.project.benefit` | `fix_project_benefit` | Benefit realisation for internal initiatives | project_id, benefit_description, business_case_target, measurement_method, measured_value, measured_at, realised_pct, owner_id |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.service.order`, `fix.work.order` | **M01** / **M02** | **Created by a project; owned and executed by them** |
| `fix.contract`, billing schedule, entitlements | **M08** | Read as the commercial basis |
| `fix.opportunity` | M07 | Read as project origin |
| `fix.employee`, roles, cost rates | **M21** | Read |
| **Roster and availability** | **M55** | **Read — the authoritative availability source** |
| Dispatch commitments | **M02** | Read for conflict detection |
| `fix.competency` | **M22** | **Read — assignment gate** |
| `fix.stock.quant`, reservations | M15 | Dependency observation |
| `fix.branch` provisioning status | **M30** | **Branch-opening dependency** |
| `fix.destruction.certificate` | M06 | Bulk-decommission dependency |
| `fix.recycling.batch` | M18 | Bulk-decommission dependency |
| `fix.consignment` | M03 | Logistics cost source |
| `fix.purchase.order`, vendor bills, expenses | M16 | Cost source |
| `fix.ar.invoice` | **M20** | **M20 creates it; M67 references it** |
| `fix.budget`, cost centres | M54 | Budget framework |
| `fix.risk` | M60 | Material risk escalation |
| `fix.nonconformance`, CAPA | M23 | Lessons learned destination |
| `fix.document` | M24 | Plans, evidence, deliverables |
| `fix.country.onboarding` | M65 | Country entry as a programme |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-PPM-01 | Opportunity won (M07) or contract activated (M08) with engagement scope | Propose a project from the matching template, pre-populated from the contract | Manual project creation |
| AUT-PPM-02 | Branch opening approved | Create a branch-opening project from the template, with the M30 provisioning task as a tracked dependency | Manual creation |
| AUT-PPM-03 | Project template instantiated | Generate phases, work packages, milestones, role demand and stage gates; record the template version | Present the template for manual adjustment |
| AUT-PPM-04 | Budget submitted | Route for approval by value per `05-04` §7 | Hold; escalate on SLA |
| AUT-PPM-05 | Project approved | Set the baseline, lock it, and open resource assignment | Hold in approved |
| AUT-PPM-06 | Resource demand raised | Resolve candidates by skill, **current certification (M22), roster availability (M55) and operational commitments (M02)**; propose assignments | Present the unfulfilled demand as a shortfall |
| AUT-PPM-07 | Assignment attempted with a lapsed certification | **Block**; name the certification and its expiry | Hard block |
| AUT-PPM-08 | Assignment creates a conflict with another project or an operational commitment | Raise the conflict naming the competing demand; route for priority resolution | Hard surface; no silent double-booking |
| AUT-PPM-09 | Project task requires operational work | Create the service order in M01 with the project reference; track its completion as the task's evidence | Manual service order creation |
| AUT-PPM-10 | Service order completed with a project reference | Update the linked task's progress and attach the job evidence | Manual progress update |
| AUT-PPM-11 | Cost incurred in a source module against a project reference | Attach it to the work package by reference; update incurred and forecast | Queue and retry; report unattributed cost |
| AUT-PPM-12 | Budget consumption crosses a warning threshold | Notify the project manager and sponsor with the forecast at completion | Report only |
| AUT-PPM-13 | Forecast exceeds approved budget | **Block further committed spend**; require approval at the band of the new total | Hard block |
| AUT-PPM-14 | Milestone dependent tasks complete with evidence | Move the milestone to ready for acceptance; request acceptance from the client (P04) or sponsor | Notify the project manager |
| AUT-PPM-15 | **Milestone accepted on a billable project** | **Raise the billable event to M20** with amount, contract and billing schedule reference | Retry; report unraised billing |
| AUT-PPM-16 | Scope change raised | Compute cost, schedule and resource impact; route for approval; **re-baseline on approval** | Hold the change; work does not proceed on it |
| AUT-PPM-17 | Cross-module dependency unmet at its due date | **Mark the task blocked**; notify the owner and the dependency's owning module | Report on the blocked-task list |
| AUT-PPM-18 | Cross-module dependency satisfied (stock reserved, branch provisioned, certificate issued, disposal complete) | Unblock the task; recompute the schedule | Report only |
| AUT-PPM-19 | Timesheet submitted | Value at role cost, attach to the work package, and reconcile against M55 attendance | Report unreconciled variance |
| AUT-PPM-20 | Nightly | Recompute critical path, earned value, forecast at completion and project health across the portfolio | Retain the previous values; alert |
| AUT-PPM-21 | Project risk scores above the escalation threshold | Escalate to M60's enterprise risk register | Report only |
| AUT-PPM-22 | Stage gate reached | Assemble the evidence, notify the decision authority, and block progression until decided | Hold at the gate |
| AUT-PPM-23 | Project closure initiated | Verify all cost captured and all billable events raised; block closure otherwise; release resources; require lessons learned | **Hard block** on unresolved cost or billing |
| AUT-PPM-24 | Internal initiative closed | Schedule benefit realisation measurement against the business case at the defined interval | Report as unmeasured |

---

## 12. Interfaces

### 12.1 Upstream — M67 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M07 CRM / M08 Contracts** | Won opportunities and activated contracts as project origins; billing schedules | Events + REST |
| **M55 Workforce Scheduling** | **Roster and true availability — the authoritative source** | REST |
| **M02 Field Service** | Operational dispatch commitments for conflict detection | REST |
| **M22 Learning & Certification** | **Current certification status — the assignment gate** | REST |
| **M21 Core HR** | Employees, roles, cost rates | REST |
| **M30 Platform Admin** | Branch provisioning status; cost centres; business lines; calendars | Events + REST |
| M15 Inventory | Stock availability and reservation for rollout dependencies | Events |
| M06 Data Services | Destruction certificates for bulk-decommission dependencies | Events |
| M18 E-Waste | Disposal completion for bulk-decommission dependencies | Events |
| M03 Logistics | Movement cost attributable to a project | Events |
| M16 / M52 | Purchases, subcontract and expenses attributable to a project | Events |
| M01 / M31 | Service order completion for project-generated work | Events |
| M20 Receivable | Invoice confirmation against billable events | Events |
| M54 FP&A | Budget framework and cost-centre structure | REST |
| M65 Localisation | Country onboarding phases where a country entry is a programme | Events |

### 12.2 Downstream — M67 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M01 Service Order** | **Service orders created from project tasks, carrying the project reference** | Commands |
| **M20 Receivable** | **Billable events on milestone acceptance and approved T&M cost** | Events |
| **M30 Platform Admin** | Branch-opening project status triggering provisioning | Events |
| **M54 FP&A** | Project cost, budget consumption, forecast and margin | Warehouse extract + events |
| **M19 Financial Accounting** | Project cost events for posting | Events |
| M55 Workforce | Project resource commitments feeding capacity planning | Events |
| M60 GRC | Escalated project risks | Events |
| M23 Quality | Lessons learned and project non-conformances | Events |
| M66 ITSM | IT changes required by a project | Commands |
| M65 Localisation | Country-entry programme progress | Events |
| M05 Managed Services | Handover of a completed infrastructure engagement into ongoing service | Events |
| M25 BI / M62 | Project, portfolio, resource and profitability facts | Warehouse extract |
| **P04 Corporate Portal** | **Client-scoped project status, milestones and acceptance requests** | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `project.created` | project, type, client, contract, sponsor, manager | M08, M54, M25 |
| `project.approved` | project, budget, baseline, approver | M54, M19, M55 |
| `project.state_changed` | project, from, to, reason, health | M54, M25, P04 |
| `project.blocked` | project, task, unmet dependency, owning module | dependency owner, sponsor |
| `project.service_order_required` | project, task, service scope, location, target date | **M01** |
| `project.milestone_ready` | project, milestone, evidence, acceptance requested from | **P04**, sponsor |
| `project.milestone_accepted` | project, milestone, accepted by, evidence | M20, M53, P04 |
| **`project.milestone_billable`** | project, milestone, amount, contract, billing schedule | **M20** |
| `project.cost_incurred` | project, work package, category, source, amount | M19, M54 |
| `project.budget_threshold_breached` | project, budget, forecast, variance | sponsor, CFO, M54 |
| `project.change_approved` | project, change, cost impact, schedule impact, new baseline | M54, M20, M55 |
| `project.resource_assigned` | project, employee, allocation, period | M55, M21 |
| `project.resource_conflict` | employee, period, competing demands, severity | **M55**, M02, Operations Director |
| `project.resource_released` | project, employee, effective from | M55 |
| `project.risk_escalated` | project, risk, score, mitigation | **M60** |
| `project.stage_gate_decided` | project, gate, decision, conditions, authority | sponsor, CFO |
| `project.delivered` | project, final acceptance, deliverables | M20, M05, P04 |
| `project.closed` | project, final cost, final margin, lessons learned | M54, M23, M25 |
| `project.benefit_measured` | project, business case target, measured value, realised % | **CFO, CEO**, M54 |
| `programme.milestone_reached` | programme, milestone, constituent projects | sponsor, CEO |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-PPM-01 | **P04 Corporate B2B Portal** | Bidirectional | Client-scoped project status, milestone acceptance and deliverable review |
| INT-PPM-02 | Client project tooling *(MS Project, Jira, Smartsheet)* | Outbound, optional | Schedule export for corporate clients running their own programme office |
| INT-PPM-03 | Document and plan storage | Bidirectional | Plans, evidence and deliverables through M24 |
| **INT-047** | Client ITSM (ServiceNow / Jira) | Bidirectional | Where an infrastructure engagement interfaces with an enterprise client's own change process (`05-03` §2.7, W7) |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/projects` | GET/POST | Project register and creation | P03, M07, M08, M30 |
| `/api/v1/projects/{id}` | GET | Full project: WBS, schedule, budget, risks, resources | P03 |
| `/api/v1/projects/{id}/wbs` | GET/POST | Work breakdown structure | P03 |
| `/api/v1/projects/{id}/baseline` | POST | Set or re-baseline on approved change | P03 |
| `/api/v1/projects/{id}/milestones` | GET | Milestones with acceptance state | P03, **P04** |
| `/api/v1/projects/{id}/milestones/{mid}/accept` | POST | **Record acceptance — raises the billable event** | **P04**, P03 |
| `/api/v1/projects/{id}/changes` | GET/POST | Scope change with impact and approval | P03 |
| `/api/v1/projects/{id}/risks` | GET/POST | Project risk register | P03, M60 |
| `/api/v1/projects/{id}/cost` | GET | Budget, committed, incurred, forecast, margin | P03, P06, M54 |
| `/api/v1/projects/{id}/status` | GET | **Client-scoped status view** | **P04** |
| `/api/v1/resources/demand` | GET/POST | Role-based demand | P03 |
| `/api/v1/resources/candidates` | POST | **Resolve candidates by skill, certification and real availability** | P03 |
| `/api/v1/resources/assign` | POST | Assign, with conflict and certification checks | P03 |
| `/api/v1/resources/conflicts` | GET | Open conflicts with competing demand named | P03, M55 |
| `/api/v1/resources/capacity` | GET | Portfolio capacity against committed and pipeline demand | P03, P06 |
| `/api/v1/projects/{id}/timesheets` | POST | Record effort against a task | P02, P03 |
| `/api/v1/portfolio` | GET | **All projects with health, variance, demand and gates** | P03, P06 |
| `/api/v1/programmes/{id}` | GET | Programme view with constituent projects | P03, P06 |
| `/api/v1/projects/{id}/close` | POST | Closure with the cost and billing completeness gate | P03 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R02 Chief Technology Officer | C R U D A | All; owner of internal initiative projects |
| R05 Operations Director | C R U A | Corporate rollout and branch-opening projects; resource conflict resolution |
| **Project Manager** *(a grant, not a distinct `05-04` role — see the note below)* | C R U | **Own projects**: WBS, schedule, assignment, progress, risks, issues, change proposal |
| R22 Account Manager (Corporate) | C R | Projects for own accounts; raises the project from a won opportunity |
| R03 Chief Financial Officer | R A | Budgets, changes above threshold, project profitability, closure |
| R26 Finance Manager | R A | Cost capture, billable events, financial closure |
| R13 Remote Support Engineer | R U | Own tasks on IT infrastructure engagements |
| R10 / R11 / R12 Technician | R U | Own project tasks and timesheets |
| R30 HR Manager | R | Resource demand and utilisation for workforce planning |
| R32 Quality Manager / ISO Coordinator | R U | Stage gate evidence, lessons learned, project non-conformances |
| R06 Branch Manager | R U | Own branch-opening project tasks |
| R01 Chief Executive Officer | R A | Portfolio; programme sponsorship; internal initiative benefit realisation |
| R37 Corporate Portal User | R U | **Own company's project only** — status, milestones, acceptance (P04) |

> **Role gap — audit action.** `05-04` §1 contains **no Project Manager role**, and M67 is built
> around one. It is currently modelled as a **project-scoped grant on R05, R22 or R13 depending
> on project type**, which is workable but leaves accountability for delivery unnamed in the role
> register. This is the **fourth role gap** recorded across the two categories written so far —
> after Demand Planner (Category E), Data Steward (M64) and IT Service Desk agent (M66) — and the
> pattern itself is an audit finding: `05-04` was written for a 30-module architecture and does
> not carry the roles the 67-module architecture implies.

**Field-level restrictions.** Project cost, margin and role cost rates are visible to R01–R05,
R26, R27 and the project manager only. **Corporate portal users see status, milestones and
deliverables — never cost, margin, resource names, internal notes or another client's project**
(EA-01, EA-02).

**Segregation of duties.**
- The project manager cannot approve their own budget or their own scope change.
- The person who accepts a milestone on behalf of 1000FiX cannot be the person who raises its billable event where the value exceeds a threshold.
- Timesheet approval is by the work-package owner, not the submitter.
- Project closure requires both the sponsor and Finance.
- A resource conflict cannot be resolved by the project manager who created it where the competing demand is operational — Operations Director arbitrates.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Portfolio dashboard** | CEO, CTO, Operations Director, CFO | Real time | Every project: type, state, health, schedule and budget variance, open risks, gate position |
| **Project health** | Project manager, sponsor | Real time | Milestones, critical path, blocked tasks, earned value, forecast at completion |
| **On-time, on-budget delivery** | CEO, CFO, Operations Director | Monthly | Projects delivered within baseline schedule and budget — **against the > 80% target** |
| **Project profitability** | CFO, CEO, Account Manager | Monthly | Revenue, cost and margin by project, work package and project type; loss-making projects flagged early |
| Budget consumption and forecast | Project manager, sponsor, Finance | Weekly | Budgeted, committed, incurred, forecast, variance by category |
| **Resource utilisation and conflicts** | Operations Director, HR Director, project managers | Weekly | Utilisation by role and person; open conflicts; unfulfilled demand |
| **Portfolio capacity** | CEO, Operations Director, CCO | Monthly | Committed and pipeline demand by role against capacity; forecast shortfalls before commitment |
| Milestone and billing status | Finance Manager, Account Manager | Weekly | Milestones due, accepted, billable events raised, invoiced, unbilled |
| Scope change register | CFO, sponsors | Monthly | Changes by project, cost and schedule impact, approval status, cumulative scope growth |
| Project risk and issue register | Sponsors, M60, Quality Manager | Monthly | Open risks by score, escalated risks, overdue issues |
| Stage gate register | CEO, sponsors, Internal Audit | Per gate | Decisions, evidence, conditions, projects stopped |
| Blocked task register | Operations Director, dependency owners | Daily | Tasks blocked by stock, provisioning, certificates or disposal, with the owning module |
| **Branch opening performance** | Operations Director, CEO | Per opening | Elapsed time, cost against budget, dependency delays, launch readiness |
| Lessons learned register | Quality Manager, project managers | Quarterly | Recurring themes across closed projects, actions taken |
| **Benefit realisation** | CEO, CFO | Per internal initiative | Business case target versus measured outcome — **including the ERP programme itself** |
| Client project view *(P04)* | Corporate client | Real time | Their own project's status, milestones, deliverables and acceptance requests |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W8 Target | W9+ Target |
|---|---|---|---|---|
| — | **Projects delivered on time and on budget** | unmeasured | 72% | **> 80%** |
| — | Projects run outside the ERP (on spreadsheets) | ~100% | < 15% | **< 5%** |
| — | Schedule variance against baseline | unmeasured | ± 12% | **± 7%** |
| — | Cost variance against baseline | unmeasured | ± 10% | **± 5%** |
| — | Project margin known during delivery rather than after closure | 0% | **100%** | **100%** |
| — | Loss-making projects identified before 50% completion | unknown | 80% | **95%** |
| — | Milestone billable events raised within 24 hours of acceptance | n/a | 95% | **99%** |
| — | Unbilled delivered project value | unknown | < 3% | **< 1%** |
| — | Scope changes priced and approved before work proceeds | unmeasured | 90% | **98%** |
| — | Resource conflicts detected before assignment rather than discovered | 0% | 90% | **98%** |
| — | Assignments blocked for lapsed certification | n/a | tracked | **Zero reaching site** |
| — | Resource utilisation on billable projects | unmeasured | 68% | **76%** |
| — | Branch opening elapsed time against template | unmeasured | baselined | **−20%** |
| — | Projects closed with lessons learned recorded | 0% | **100%** | **100%** |
| — | Internal initiatives with benefit realisation measured | 0% | **100%** | **100%** |
| — | Stage gates decided with recorded evidence | 0% | **100%** | **100%** |

> **Register note.** `_CATEGORY_OVERVIEW.md` §9 names **projects delivered on time and on budget
> (> 80%)** as the category KPI owned by M67. **It has no canonical `KPI-0nn` identifier** —
> `06-02` §2.6 ends at KPI-049. Allocation for all sixteen metrics is an audit action.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `project`, `timesheet` — project, task, timesheet substrate | 22% |
| L2 | OCA `project-*` (WBS, stages, risk), `management-system` (review, lessons learned), `server-tools` | 20% |
| L5 | `cd_project`, `cd_project_resource`, `cd_project_billing` | 58% |

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 3 of 3 identifiers below are claimed by another module: **CD-165** also claimed by M46, M52; **CD-166** also claimed by M46, M52; **CD-167** also claimed by M47, M50. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-165** | `cd_project` — project object and the five templates, **work breakdown structure**, scheduling and critical path, baselines, milestones and acceptance, deliverable register, **earned value**, scope change control, risk and issue registers, stage gates, cross-module dependency observation, programme grouping, portfolio dashboard, closure with lessons learned and benefit realisation | Odoo module + frontend | 8 PW |
| **CD-166** | `cd_project_resource` — role-based demand, **candidate resolution against M55 availability, M02 commitments and M22 certification**, conflict detection, assignment, effort recording and M55 reconciliation, subcontract resource, portfolio capacity planning | Odoo module + service | 5 PW |
| **CD-167** | `cd_project_billing` — project budget by category, **cost aggregation from source modules by reference**, committed/incurred/forecast tracking, budget control, **milestone and progress billable events to M20**, project profitability, client-facing P04 view | Odoo module | 4 PW |

> CD-165…167 are claimed from the extension block for modules M31–M67. **All CD IDs remain
> provisional** pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M30 Platform Admin (W1)** | Cost centres, business lines, calendars; **branch provisioning as a tracked project dependency** |
| **M29 Identity (W1)** | Project-scoped access; client isolation in P04 |
| **M21 Core HR (W5)** | Employees, roles and cost rates for resource planning and effort valuation |
| **M55 Workforce Scheduling (W5)** | **The authoritative availability source.** Without it, M67 would assert availability rather than read it — the design position forbids that |
| **M22 Learning & Certification (W5)** | The certification gate on assignment |
| **M08 Contract Lifecycle (W4)** | Billing schedules and the commercial basis for engagement projects |
| **M20 Receivable (W3)** | **The recipient of billable events** |
| **M54 FP&A (W6)** | Budget framework and cost-centre structure |
| **P04 Corporate Portal (W4)** | The client-facing project view and milestone acceptance |
| M01 / M02 / M31 (W1–W2) | Service orders generated from project tasks |
| M06 (W6) / M18 (W8) | Bulk-decommission dependencies; **until M18 lands, a decommission project completes to disposal-pending** |

> **Why Wave 7, and what it costs.** M67 depends on M55 and M22 (both W5) for resource planning
> and on M54 (W6) for the budget framework. W7 is therefore the earliest coherent placement, and
> the category positions it *before* the marketplace and expansion waves deliberately.
>
> **The cost is six waves of corporate rollouts and branch openings run on spreadsheets** — the
> exact risk the category names. If the corporate pipeline grows faster than expected, a **W5
> slice covering project structure, WBS, milestones and cost capture** (roughly 8 PW of CD-165
> and CD-167, without resource optimisation) would be the pragmatic answer. Raised as Q-01.
>
> **The ERP programme itself** is a project M67 should model. It cannot, until Wave 7. From W7,
> the remaining waves should be brought into M67 — both for the management value and as the
> most demanding possible test of the module. Raised as Q-02.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| In-flight corporate rollouts | Spreadsheets, current only | `fix.project` | W7, current engagements only |
| In-flight branch openings | Checklists | `fix.project` | W7 |
| The ERP programme (waves 7–9) | The roadmap in `06-01` | `fix.programme`, `fix.project` | W7, authored |
| Project templates | **Authored from the five types** | `fix.project.template` | W7 |
| Role cost rates | Finance and HR | Referenced from M21 | W7 |
| Historical project outcomes | Not recorded | — | **Not migrated** |

> **Position.** M67 migrates only live work. There is no historical project data because there
> has been no project system, which means the on-time/on-budget KPI baseline is established from
> W7 rather than measured against history. **The template authoring is the real preparation
> work**: five templates capturing how 1000FiX actually runs a rollout, an engagement, a branch
> opening, a decommission and an internal initiative — knowledge that currently exists only in
> the people who have done it.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A project generates service orders in M01 carrying the project reference, and those orders follow M01's lifecycle unchanged | End-to-end corporate rollout scenario |
| AC-02 | M67 creates no financial document; milestone acceptance raises a billable event and M20 invoices | Code review plus end-to-end billing scenario |
| AC-03 | A project cannot enter delivery without an approved budget and a set baseline | Negative test |
| AC-04 | An approved baseline is immutable; re-baselining creates a new version linked to its approved change | Negative test plus versioning test |
| AC-05 | Budget approval routes by value per `05-04` §7 | Test matrix across bands |
| AC-06 | Forecast exceeding the approved budget blocks further committed spend until re-approved | Negative test |
| AC-07 | **Resource assignment uses M55 availability and M02 commitments; M67 holds no independent calendar** | Code review plus scenario with a dispatched technician |
| AC-08 | An assignment requiring a lapsed certification is blocked | Negative test with M22 |
| AC-09 | A conflict across projects or against an operational commitment is surfaced with the competing demand named | Scripted double-booking scenario |
| AC-10 | Project cost aggregates from M15, M03, M16, M52 and timesheets by reference, and a correction at source flows through | End-to-end cost scenario with an induced correction |
| AC-11 | Milestone acceptance raises a billable event to M20 within 24 hours, with contract and schedule reference | Twelve weeks of measurement |
| AC-12 | A scope change cannot be worked on before it is priced and approved | Negative test |
| AC-13 | A task blocked by an unmet cross-module dependency is surfaced within minutes and unblocks automatically when satisfied | Scripted scenario for stock, provisioning and certificate dependencies |
| AC-14 | Earned value, schedule variance and forecast at completion compute correctly against a known test project | Computation test |
| AC-15 | Critical-path recomputation for a 500-task project completes in ≤ 2 seconds | Performance test |
| AC-16 | A project cannot close with uncaptured cost or unraised billable events | Negative test |
| AC-17 | A project cannot close without lessons learned recorded and passed to M23 | Negative test |
| AC-18 | An internal initiative cannot close without benefit realisation measured against its business case | Negative test |
| AC-19 | A stage gate cannot be passed implicitly; the decision, authority and evidence are recorded | Negative test |
| AC-20 | A corporate client in P04 sees only their own project and no cost, margin, resource name or internal note | Penetration test against EA-01 and EA-02 |
| AC-21 | A branch-opening project tracks M30 provisioning as a dependency and completes end to end | One real branch opening |
| AC-22 | Task lists, acceptance requests and the client view are complete in Bengali | Translation coverage report (AS-12) |
| AC-23 | Projects delivered on time and on budget exceed 80% | Twelve months of closed projects |
| AC-24 | Operations Director, CFO and one corporate client sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 24 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Is a W5 slice of M67 required** — project structure, WBS, milestones and cost capture without resource optimisation (≈8 PW pulled forward)? Six waves of corporate rollouts on spreadsheets is the accepted cost of W7 placement, and it may not remain acceptable if the corporate pipeline grows. | CEO / CCO / CTO | **W5 minus 3 months** |
| Q-02 | **Should the remaining ERP programme waves be modelled in M67 from W7?** The category names the programme as a project type. Doing so is both useful and the most demanding possible test of the module. | CTO / programme sponsor | W7 |
| Q-03 | **Who authors the five project templates**, and from whose experience? This is the main preparation work and the knowledge exists only in people who have run these engagements. | Operations Director / CCO | **W7 minus 3 months** |
| Q-04 | **Is Project Manager a distinct role in `05-04`**, or a project-scoped grant? This is the fourth role gap identified across two categories; a broader `05-04` refresh may be the better answer than four individual additions. | HR Director / CTO | W7 design |
| Q-05 | Are project managers a dedicated function or an additional responsibility for branch and operations managers? The resource model and the utilisation KPI both depend on the answer. | Operations Director / HR Director | W7 design |
| Q-06 | What are the role cost rates used to value project effort, and are they standard, actual or blended? Project margin is only as good as this number. | CFO / HR Director | W7 build |
| Q-07 | Which project types require stage gates, and how many? A branch opening and a 300-asset decommission do not warrant the same governance. | Operations Director / CFO | W7 build |
| Q-08 | Do corporate clients want a project view in P04, and will they use it to accept milestones? Milestone acceptance is the billing trigger, so client adoption directly affects cash flow. | CCO / Account Managers | W7 design |
| Q-09 | How is a resource conflict between a project commitment and an operational dispatch resolved, and by whom in real time? The rule cannot be "escalate to the Operations Director" for every occurrence. | Operations Director | W7 build |
| Q-10 | Is subcontracted delivery capacity procured through M16 or allocated through M12 marketplace? This is the reciprocal of **M16 Q-08**, and both modules currently defer to the other. | CCO / Procurement Manager | W7 design |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` **§4 (why project management belongs here — the five project types and
the four benchmark analogues)**, §6 (boundary map — **not M01, not M20**), §9 (category KPI),
§11 (**the spreadsheet-fragmentation risk**) ·
`M30_Platform_Administration_and_Configuration.md` §3.2, §8.1 (**branch provisioning in a day
versus the branch-opening project**) · `M66_Internal_IT_Service_Management.md` (**change versus
project**) · `M65_Multi_Entity_Multi_Country_and_Localisation.md` (**country entry as a
programme**) · `M29_Identity_Access_and_Information_Security.md` (client scope isolation) ·
`M01` Service Request & Order Management *(Category A — **projects generate service orders**)* ·
`M08` Contract Lifecycle Management *(Category C — the commercial basis and billing schedule)* ·
`M20` Accounts Receivable, Invoicing & Collections *(Category G — **creates the invoice**)* ·
`M55` Time, Attendance & Workforce Scheduling *(Category H — **the authoritative availability source**)* ·
`M22` Learning, Competency & Certification *(Category H — the assignment gate)* ·
`M54` Cost Accounting, Budgeting & FP&A *(Category G — the budget framework)* ·
`M60` Governance, Risk & Compliance *(Category I — enterprise risk escalation)* ·
`M05` Remote Support & Managed Services *(Category A — engagement handover into ongoing service)* ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §9 (business lines and their
order/work/billing objects) ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §7 (approval
authority), §8 EA-01/EA-02, §1 (**no Project Manager role — audit action**) ·
`05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md` §2.7 (INT-047) ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` NFR-058, AS-03, AS-12 ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` (**the nine-wave
programme M67 should model**) ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` BO-11, BO-12, BO-13, BO-14 ·
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` P04

**Workspace evidence**
`1000FiX_Services_Company_Profile.md` §Service Infrastructure (1000FiX Station expansion),
§Corporate Service Capability · `ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md`
(corporate and project requirements) · Executive Summary §6.2 (MSP, rental and refurbishment
contributions delivered through engagement work)

**External benchmark**
[Microsoft Dynamics 365 Project Operations — WBS, milestones, resource management by availability and skill, project financials with automated billing milestones and real-time cost tracking](https://reachinternational.ai/dynamics-365-project-operations/) ·
[Dynamics 365 Project Operations — project types, resource allocation, profitability](https://www.randgroup.com/insights/microsoft/dynamics-365/customer-engagement/project-operations/what-is-dynamics-365-project-operations/) ·
[Dynamics 365 Project Operations features](https://learn.microsoft.com/en-us/training/paths/get-started-features-project-operations) ·
[ERP for project management — vendor comparison](https://www.erpresearch.com/erp-modules/project-management) ·
[ERP software for project management](https://www.erpresearch.com/en-us/erp-for-project-management) ·
Oracle Project Portfolio Management — Project Management, Costing and Billing ·
SAP Project System (PS) — WBS as the cost-collection spine; milestone billing plans ·
NetSuite SuiteProjects — projects, billing and finance in one system ·
PMI earned value management practice · Stage-gate governance practice

---

*Module M67 · Category K · 1000FiX ERP System v2.0 · CONFIDENTIAL*
