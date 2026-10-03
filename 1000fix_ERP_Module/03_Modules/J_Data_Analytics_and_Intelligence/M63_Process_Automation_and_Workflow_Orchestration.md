---
id: FIX-ERP2-M63
module_id: M63
module_code: BPA
module_name: Process Automation & Workflow Orchestration
category: J — Data, Analytics & Intelligence
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Technology Officer
system_owner: Platform Squad
priority: P1
wave: W3
---

# M63 — Process Automation & Workflow Orchestration
### Category J · Code `BPA` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M63 |
| **Module code** | `BPA` |
| **Category** | J — Data, Analytics & Intelligence |
| **Status** | ★ New in v2.1 — extracted from the v2.0 integration platform scope after enterprise benchmarking |
| **Priority** | **P1** |
| **Delivery wave** | **W3** (Months 11–14) — the earliest of the four Category J modules |
| **Business owner** | Chief Technology Officer *(process ownership sits with each functional head)* |
| **System owner** | Platform Squad |
| **Delivery layers** | L1 (Odoo activities and server actions) · L3 (workflow engine, n8n) · L5 (custom) |
| **Custom modules** | `cd_workflow_engine`, `cd_approval_matrix`, `cd_business_rules`, `cd_job_scheduler` |
| **Requirement range** | FR-BPA-001 … FR-BPA-032 |
| **Requirement count** | **32** *(register `02-02` estimated 28 — measured supersession, see §16.5)* |
| **Effort estimate** | **19 person-weeks** *(register estimated 16)* |
| **Depends on** | M28 Integration & Event Platform · M29 Identity & Security · M64 Master Data Management · M27 Contact Centre (delivery) · M30 Platform Administration |
| **Depended on by** | **Every module with an approval, an escalation, a scheduled job or a configurable threshold** — in practice all 66 others · M25 (schedule execution) · M26 (human confirmation routing) · all portals |

---

## 2. Purpose

M63 is **how work moves through the Company**. It executes the approval chains, the escalations,
the scheduled jobs and the business rules that every other module declares but none of them
should implement.

The distinction that justifies its existence is stated plainly in the category overview:
**M28 guarantees the message arrives; M63 decides what happens next and who must approve it.**
They look similar and are not. One is a transport problem solved by engineers and changed when a
system changes. The other is a policy problem owned by business people and changed whenever
policy changes — which is far more often.

The module's single most important property follows from that: **a change to an approval
threshold must never require an integration release.** Discount limits, credit thresholds,
write-off ceilings, escalation timings and routing rules are configuration held by the business,
versioned and approved, and changed without a developer.

### Why It Exists

Sixty-six other modules in this programme declare approvals, escalations, scheduled jobs and
thresholds. Every one of them, implemented locally, would mean a different approval mechanism,
a different escalation timer, a different audit trail and a different place to look when
something did not happen. It would also mean that a decision to raise the discount-approval
limit from 10% to 15% would touch a dozen codebases.

The benefit case makes it sharper still. Overview §9 targets **overall automation of routine
operational work rising from ~20% to 85%**, and **approval cycle time falling from days to under
four working hours**. Neither is achievable by automating each module separately; both are
achievable by automating once, centrally, with the rules held where the business can change them.

M63 lands in **W3 — before the finance modules go live** — because the first thing a money
module needs is a working approval chain.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| **Category J Overview §4** | The M28/M63 split: M28's concern is *moving data reliably between systems*, audience developers, artefacts connectors and retry policy, changing on system change. M63's concern is *advancing a business process through steps and approvals*, audience business analysts and process owners, artefacts approval chains, escalation rules, scheduled jobs and business-rule sets, changing on **policy change — far more frequent**. **"A change to an approval threshold must never require an integration release."** Analogues: SAP Business Workflow, Oracle BPM, n8n / Camunda |
| Category J Overview §5 | Boundary map: approval chains and escalation rules → **M63** (*every module declares its need; M63 executes*); scheduled and event-driven job execution → **M63** (M28 transports the event); business-rule configuration → **M63** (M64 stores the parameter); notification delivery → **M27** (M63 triggers it) |
| Category J Overview §9 | KPIs owned here: **approval cycle time < 4 working hours** (from days), **workflow changes made without a code release > 95%**, **overall automation of routine operational work ~20% → 85%** |
| Category J Overview §11 | The risk owned here: *automation encodes a wrong rule at scale — errors multiply faster than humans catch them*. Mitigation: rules are configuration with approval; every automation has a defined failure behaviour and an audit trail |
| Category J Overview §10 | Delivery sequence: **W3 M63 — "approvals and workflow from the first money module"** |
| `02-05` §Technology Stack | **n8n 1.x** (Sustainable Use licence, self-hosted, W1) — *"used only for internal orchestration"* |
| Written module specifications (40+) | Each declares approvals, escalations, scheduled jobs and thresholds in its §9 business rules and §11 automations. M63 is the execution engine for all of them |
| `05-04` §6 | Twelve enterprise segregation-of-duties rules that approval routing must enforce |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** Both sides of every boundary must agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The workflow engine — process definitions, state, human tasks, service tasks, timers and events |
| 2 | Approval chains: sequential, parallel, quorum and conditional |
| 3 | The delegation-of-authority matrix — who may approve what, up to what value, in what scope |
| 4 | Approval routing by decision table, so routing logic is business-readable |
| 5 | Substitution, delegation and out-of-office reassignment |
| 6 | Escalation on time, on absence and on value |
| 7 | Segregation-of-duties enforcement within approval routing |
| 8 | The business-rule repository — thresholds, tolerances, limits and conditions as governed configuration |
| 9 | Rule versioning, approval, effective dating, simulation and rollback |
| 10 | Scheduled job definition and execution across every module |
| 11 | Event-driven automation triggered by domain events from M28 |
| 12 | Straight-through processing paths, with defined exception routing |
| 13 | Compensation and rollback for multi-step processes that fail part-way |
| 14 | The task inbox — one place where a person sees everything waiting on them |
| 15 | Mobile and portal approval surfaces |
| 16 | Complete audit trail: what ran, on what rule version, who approved, when, and why |
| 17 | Process performance measurement, bottleneck analysis and automation-rate reporting |
| 18 | The citizen-development governance model — who may author a workflow and how it is released |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Message transport, connectors, delivery guarantees, retry policy, API gateway, event schemas** | **M28** Integration & Event Platform | Category J overview §4. **M28 guarantees the message arrives; M63 decides what happens next.** Mixing them means a policy change becomes an integration release |
| **Notification delivery — email, SMS, WhatsApp, push, in-app** | **M27** Contact Centre & Communications | M63 decides *that* someone must be told and *who*; M27 delivers it. One delivery estate, one preference model, one suppression policy |
| **The business decision itself and its record** | **Owning module** | M63 routes the approval and records that it happened; the approved artefact — the credit note, the purchase order, the write-off — belongs to its module |
| **Parameter storage and master data** | **M64** Master Data Management | Overview §5: M63 owns business-rule *configuration*; M64 *stores the parameter*. M63 holds the rule that uses it |
| **Model scoring, prediction and explanation** | **M26** AI/ML Services | M63 may route a decision that a model informed; it never produces the score |
| **Dashboards and reporting on process performance** | **M25** Business Intelligence | M63 emits process facts; M25 presents them |
| **Data pipeline scheduling** | **M62** Data Platform | A pipeline run is not a business event. M62 schedules its own loads with dependency awareness |
| **Identity, roles, entitlements and the SoD rule set** | **M29** Identity & Security | M29 defines who someone is and what they may do; M63 *enforces SoD within routing* using M29's definitions |
| **Contract clause approval workflow content** | **M08** Contract Lifecycle | M08 declares what needs approving; M63 executes the chain |
| **Field workforce scheduling and dispatch** | **M02** / **M55** | Scheduling people to jobs is an optimisation problem, not a workflow one |
| **Document generation, e-signature and retention** | **M24** Documents | An approval may produce a document; M24 owns it |
| **Infrastructure job scheduling (backups, patching)** | **M30** Platform Administration | Technical operations, not business process |

### 3.3 Shared Concepts

| Concept | M63's Role | Owning Module |
|---|---|---|
| Approval | **Owns the chain, routing and record of approval** | Owning module owns the approved artefact |
| Delegation of authority | **Owns the matrix** | Board / CFO own the policy |
| Business rule (threshold, tolerance, limit) | **Owns the rule and its lifecycle** | M64 stores the parameter; the function owns the value |
| Escalation | **Owns** | Receiving role owns the response |
| Scheduled job | **Owns business-process schedules** | M62 owns pipeline schedules; M30 owns infrastructure schedules |
| Domain event | Consumes as a trigger | M28 transports |
| Notification | **Triggers** | M27 delivers |
| Task | **Owns the task and the inbox** | Owning module owns the underlying work |
| Segregation of duties | **Enforces in routing** | M29 defines |
| Process performance fact | Produces | M25 presents |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP Business Workflow / Flexible Workflow** | Centrally-defined approval processes with agent determination rules, deadline monitoring, escalation and substitution, decoupled from the transactional application | **The central pattern**: one workflow estate serving every application, with agent determination as configuration and substitution as a first-class concept | SAP's organisational-model dependency. Agent determination here resolves against M29 roles and M21 reporting lines directly |
| **Oracle BPM / Approval Management Extensions (AME)** | Rule-driven approval list generation — the approver chain is *derived* from attributes of the transaction rather than hard-coded per document type | **Derived approval chains.** A purchase requisition's approvers are computed from value, category, cost centre and scope at submission time, not stored on a form. This is what makes a policy change a configuration change | AME's rule-authoring complexity, which needs specialists — the opposite of the objective |
| **Microsoft Dynamics 365 workflow + Power Automate** | Business-user-authored automation with a governed release path, plus prebuilt approval experiences and a unified task inbox | **The unified task inbox** and the business-author-plus-governed-release model | Unrestricted citizen development. Overview §11 names *automation encoding a wrong rule at scale* as a High risk; ungoverned authoring is precisely how that happens |
| **Camunda (BPMN 2.0 + DMN)** | A stateful, event-sourced engine executing BPMN 2.0 process models with service tasks, user tasks, business-rule tasks and message/signal events; **DMN decision tables** managing elaborate task-assignment and routing rules in a business-readable form; orchestration across APIs, microservices, human work and bots | **BPMN as the process notation and DMN decision tables as the routing and threshold mechanism.** A decision table is readable by a finance manager, reviewable in a change request, and testable — which is what turns "the rule" from tribal knowledge into an artefact | Running the full Camunda platform as a second engine alongside n8n. The BPMN/DMN *semantics* are adopted; the engine choice is settled in §16 |
| **n8n** *(selected in `02-05`, Sustainable Use licence, self-hosted)* | Visual workflow automation with a large connector library, event and schedule triggers, and self-hosted deployment | **The execution substrate for integration-adjacent and scheduled automation**, already deployed from W1 | n8n as the *approval* engine. It has no delegation-of-authority model, no SoD enforcement, no effective-dated rule versioning and no approval audit trail. Approvals are custom (CD-197) for exactly those reasons. **Licence note:** the Sustainable Use licence permits internal business use only — see §18 Q-05 |
| **Saga / compensation patterns** | Long-running multi-step processes with explicit compensating actions when a later step fails | **Compensation as a required property of any multi-step process that changes state in more than one module.** Without it, a failure half-way leaves the business in a state no module owns | Distributed two-phase commit |
| **Process mining practice** | Discovering the real process from event logs, exposing variants, rework loops and bottlenecks against the intended model | **Process performance and bottleneck analysis from the workflow event log** — the intended model and the actual execution compared | A commercial process-mining platform at W3 |
| **Delegation-of-authority practice** | A matrix of who may approve what, to what value, in what scope, with substitution and escalation; reviewed periodically and audited | **The matrix as a governed, effective-dated, versioned artefact** rather than a policy document nobody can enforce | — |
| **Straight-through processing practice** | Defining the happy path that requires no human, and measuring what proportion of volume achieves it | **STP rate as the headline automation measure**, per process — the honest version of the 85% automation target | Automating exceptions. Exceptions are where judgement lives; the objective is to route them well, not to remove the human |

**Design position.** Six deliberate differences.

**First, rules are configuration with an approval workflow of their own.** The Category J risk
register names the failure mode: *automation encodes a wrong rule at scale, and errors multiply
faster than humans catch them.* The mitigation implemented here is that a business rule is a
versioned, effective-dated, approved artefact; it can be **simulated against historical
transactions before activation**; and it can be **rolled back to its prior version in one
action**. A rule change is treated with the seriousness of a code change, because it has the same
blast radius and reaches production faster.

**Second, approval chains are derived, never drawn.** Nobody maintains a diagram per document
type. The chain is computed at submission from the transaction's own attributes — value,
category, cost centre, entity, scope, risk class — against a decision table. Raising a discount
limit is one cell in one table, effective-dated, approved, and applied everywhere that limit
appears.

**Third, every automation has a declared failure behaviour, and there is no default.** Each
automation states what happens when it cannot complete: block, retry, escalate, fall back, or
compensate. An automation without one cannot be activated. This is the same discipline the
finance modules apply to posting and the AI module applies to model unavailability, and it is
the reason automation at 85% is safe rather than reckless.

**Fourth, one inbox.** A branch manager should not have to remember that leave approvals live in
one place, purchase approvals in another and write-off approvals in a third. Every task waiting
on a person appears in one list, on mobile, with the context needed to decide and the ability to
act. Approval cycle time collapses because approvals stop being hunted for.

**Fifth, segregation of duties is enforced in routing, not detected afterwards.** The twelve
enterprise SoD rules in `05-04` are evaluated when the approver list is generated. If the only
eligible approver would breach SoD, the request escalates rather than routing to them. Detecting
a violation after the fact is an audit finding; preventing it is a control.

**Sixth, authoring is governed, and the governance is proportionate.** Business analysts author
and change rules and routing within their own domain, through review and effective dating.
Process *definitions* — new BPMN processes with service tasks that change data — require
platform review. The overview's target of **>95% of workflow changes without a code release**
is met by the first category, which is where nearly all real change happens.

---

## 5. Functional Areas & Features

### 5.1 Workflow Engine & Process Definition

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-BPA-001 | Process definition | Define business processes as executable models with human tasks, service tasks, decision points, timers, and message and signal events | P1 | L3 |
| FR-BPA-002 | Process instance state | Maintain durable, recoverable state for every running instance, surviving restart without loss or duplication | P1 | L3 |
| FR-BPA-003 | Process versioning | Version every process definition, with running instances completing on the version they started under | P1 | L3 |
| FR-BPA-004 | **Declared failure behaviour** | Require every automation and process step to declare its failure behaviour — block, retry, escalate, fall back or compensate — and refuse to activate one that does not | **P0** | L5 |
| FR-BPA-005 | Compensation and rollback | Define compensating actions for multi-step processes that change state in more than one module, and execute them when a later step fails | P1 | L3 |
| FR-BPA-006 | Sub-processes and reuse | Compose processes from reusable sub-processes so a common pattern is defined once | P2 | L3 |
| FR-BPA-007 | Process simulation | Simulate a process or rule change against historical transactions before activation, reporting what would have changed | P1 | L5 |
| FR-BPA-008 | Manual intervention | Allow an authorised operator to inspect, retry, skip or terminate a stuck instance, with every intervention recorded | P1 | L5 |

### 5.2 Approvals & Delegation of Authority

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-BPA-009 | **Delegation-of-authority matrix** | Maintain who may approve what, to what value, in what scope and entity, as a governed, versioned, effective-dated artefact | **P0** | L5 |
| FR-BPA-010 | **Derived approval chains** | Compute the approver list at submission from the transaction's own attributes against a decision table, rather than storing a chain per document type | **P0** | L5 |
| FR-BPA-011 | Chain patterns | Support sequential, parallel, quorum-based and conditional approval, with any-one and all-of semantics | P1 | L5 |
| FR-BPA-012 | **Segregation-of-duties enforcement in routing** | Evaluate the enterprise SoD rules when generating the approver list, and escalate rather than route to an approver whose involvement would breach one | **P0** | L5 |
| FR-BPA-013 | Substitution and delegation | Allow a named, time-boxed delegation of approval authority, recorded and visible on the approval, with the delegator remaining accountable | P1 | L5 |
| FR-BPA-014 | Out-of-office reassignment | Reassign tasks automatically during a recorded absence, without silently widening authority | P1 | L5 |
| FR-BPA-015 | Approval with context | Present the approver everything needed to decide — the artefact, its history, the rule that routed it, prior approvals, and any model recommendation with its explanation | P1 | L5 |
| FR-BPA-016 | Reject, return and request-information | Support reject with reason, return for amendment, and request-for-information without losing the instance | P1 | L5 |
| FR-BPA-017 | Bulk approval | Allow bulk action on homogeneous low-value items, while forbidding it above a configured threshold | P2 | L5 |
| FR-BPA-018 | Approval audit trail | Record every approval, rejection, delegation, escalation and intervention with actor, time, rule version and reason, immutably | **P0** | L5 |

### 5.3 Escalation & Task Management

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-BPA-019 | Time-based escalation | Escalate a task unactioned beyond its target, on a working-hours calendar with Bangladeshi holidays and branch-specific shifts | P1 | L5 |
| FR-BPA-020 | Value and risk escalation | Escalate automatically where value, risk class or exception type exceeds a threshold, regardless of elapsed time | P1 | L5 |
| FR-BPA-021 | **Unified task inbox** | Present each person one list of everything waiting on them across all modules, with priority, age, due time and the ability to act | P1 | L5 |
| FR-BPA-022 | Mobile and portal approval | Allow approval, rejection and return from mobile and from the corporate portal, with the same context and audit trail | P1 | L5 |
| FR-BPA-023 | Reminder and nudge | Remind ahead of a deadline through M27 on the recipient's preferred channel, with suppression to prevent notification fatigue | P2 | L5 |
| FR-BPA-024 | Workload visibility | Show a manager the tasks pending across their team, their ages, and where the queue is building | P2 | L5 |

### 5.4 Business Rules & Configuration Governance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-BPA-025 | **Business-rule repository** | Hold every threshold, tolerance, limit and condition used in routing and automation as governed configuration, in business-readable decision tables | **P0** | L5 |
| FR-BPA-026 | **Rule change control** | Version every rule, require approval by its owning function, effective-date the change, and record the reason | **P0** | L5 |
| FR-BPA-027 | Rule rollback | Restore a rule to its prior version in one action, with the rollback recorded | P1 | L5 |
| FR-BPA-028 | Rule impact analysis | Show, before activation, every process, automation and module affected by a rule change | P1 | L5 |
| FR-BPA-029 | Authoring governance | Restrict who may author or change rules, routing and process definitions by domain, and require review before release | **P0** | L5 |

### 5.5 Scheduling, Event Automation & Measurement

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-BPA-030 | Scheduled job execution | Define, schedule, execute and monitor recurring business jobs across every module, with a working-hours calendar, dependency awareness, missed-run detection and catch-up policy | P1 | L3 |
| FR-BPA-031 | Event-driven automation | Trigger automation from domain events delivered by M28, with idempotent handling so a redelivered event does not act twice | **P0** | L3 |
| FR-BPA-032 | **Process performance and automation measurement** | Measure cycle time, wait time, touch count, straight-through-processing rate, escalation rate and bottlenecks per process, and report the **overall automation rate of routine operational work** | P1 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Durable, recoverable state** | Process state survives restart, failover and redeployment; no instance is lost and none resumes twice |
| T-02 | **Idempotent event handling** | Every event handler carries an idempotency key; a redelivered event from M28's at-least-once transport produces one effect |
| T-03 | **Rules as data, not code** | Thresholds, limits and routing conditions are evaluated from stored decision tables. **No rule value is compiled into a deployed artefact** — this is what makes >95% of changes release-free |
| T-04 | **Effective dating** | Every rule and matrix entry carries a validity period; evaluation uses the version in force at the transaction's own timestamp, not today's |
| T-05 | **Version pinning for running instances** | An instance completes on the process and rule versions it started under, so a mid-flight policy change cannot alter a decision already in progress |
| T-06 | **Approver derivation at submission** | The approver list is computed at submission and frozen on the instance, with the deriving rule version recorded — so the chain is reconstructable years later |
| T-07 | **SoD evaluation before routing** | Enterprise SoD rules are evaluated during approver derivation; a candidate whose involvement would breach one is excluded and the request escalated |
| T-08 | **Immutable audit trail** | Approvals, rejections, delegations, escalations and manual interventions are append-only and retained for the statutory period |
| T-09 | **Compensation guarantees** | A multi-module process that fails after partial completion executes its declared compensating actions, or halts in a named, alertable state — never silently |
| T-10 | **No direct writes** | M63 advances processes by invoking owning modules' APIs and commands. It does not write into another module's tables |
| T-11 | **Working-hours calendar** | Deadlines, escalations and cycle-time measurement use a working-hours calendar with Bangladeshi public holidays, Ramadan hours and branch-specific shift patterns |
| T-12 | **Simulation isolation** | Simulation executes against historical data in a sandbox with no side effects — no notification, no posting, no state change |
| T-13 | **Notification via M27 only** | M63 emits a notification intent; it holds no channel credentials and sends nothing directly |
| T-14 | **Performance** | Approver derivation ≤ 500 ms; task inbox load ≤ 2 s; rule evaluation ≤ 100 ms; scheduled job dispatch within 60 s of its due time |
| T-15 | **Throughput and back-pressure** | Event-driven automation absorbs burst load with queueing and back-pressure rather than dropping triggers |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M63 |
|---|---|---|
| **Branch manager** | Approvals arrive by phone, WhatsApp and paper; some are forgotten | One inbox on the phone, with context, deadlines and an audit trail |
| **Finance Manager** | Chases approvals; cannot say where a request is stuck | Sees every pending item, its age and its bottleneck |
| **CFO** | Delegation of authority is a policy document nobody can enforce | A matrix the system enforces, versioned and audited |
| **Requester (any)** | Submits and waits, with no visibility | Sees the derived chain, the current approver and the expected time |
| **Business analyst** | Raises a change request and waits for a release to change a threshold | Changes the decision table, simulates it, submits it for approval, and it takes effect on its date |
| **Developer** | Implements a slightly different approval mechanism in every module | Implements none; modules declare, M63 executes |
| **Quality Manager** | Cannot evidence that approvals followed policy | Complete, immutable trail per transaction with the rule version applied |
| **Auditor** | Samples approvals manually | Queries the trail; reconstructs any chain, including which rule version applied at the time |
| **Operations Director** | Suspects a process is slow but cannot prove where | Cycle time, wait time and touch count per step, with bottlenecks identified |
| **Employee waiting on something** | Does not know who is holding it up | Sees where it is; escalation happens without them chasing |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Approval cycle time** | Unified inbox, derived chains, deadline escalation, mobile approval | **Days → under 4 working hours** |
| **Overall automation of routine operational work** | Straight-through processing paths with exception routing, across every module | **~20% → 85%** |
| **Workflow change without a release** | Rules as governed configuration rather than code | **0% → > 95%** of workflow changes |
| **Administrative labour recovered** | Chasing, forwarding, re-keying and status-hunting eliminated across every function | Principal contributor to the **BDT 62 lac/year** administrative saving |
| **Cash-cycle acceleration** | Faster approval of invoices, credit notes, payments and purchase orders | Contributes to the **BDT 26 lac/year** financial close and cash-flow benefit |
| **Avoided leakage and control failures** | SoD enforced at routing; thresholds enforced consistently; every exception recorded | Protects warranty recovery, procurement and settlement lines |
| **Faster change** | A policy decision reaches production in hours instead of a release cycle | Removes the standard reason policy changes are deferred |
| **Reduced development cost across the programme** | Sixty-six modules do not build their own approval, escalation and scheduling machinery | Avoids an estimated 1–2 PW of duplicated effort per module |
| **Compliance evidence** | Immutable trail with rule versions supports ISO, tax, regulator and brand-partner audit | Removes recurring manual evidence assembly |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Policy becomes real** | A delegation-of-authority policy that the system enforces is a control. The same policy in a PDF is a document |
| **Accountability is visible** | Everyone can see who is holding a decision. That alone changes behaviour more than any escalation rule |
| **Institutional knowledge captured** | Approval logic that lives in a manager's head becomes a decision table anyone can read and a successor can inherit |
| **Change stops being frightening** | Simulation before activation and one-action rollback mean a rule change can be tried rather than agonised over |
| **Fairness and consistency** | The same request gets the same treatment regardless of who submits it or which branch it comes from |
| **The failure mode is designed for** | Overview §11 names automation-at-scale error as a High risk. Declared failure behaviour, simulation, versioning and rollback are the answer, and they are built in from W3 rather than added after the first incident |
| **Business ownership of business logic** | The people accountable for a threshold can change it. That is the difference between a system the business owns and a system it is subject to |

---

## 8. Lifecycle & State Models

### 8.1 Approval Request

```
   SUBMITTED
      │  attributes: value · category · cost centre · entity · scope · risk class
      ▼
   ┌────────────────────────────────────────────────────────────┐
   │  APPROVER DERIVATION                                        │
   │  decision table + delegation-of-authority matrix            │
   │  + SoD evaluation (M29 rules)                               │
   │  → chain frozen on the instance, rule version recorded      │
   └───────────────────────┬────────────────────────────────────┘
                           │  no eligible approver without an SoD breach
                           ├──────────────────────────────► ESCALATED
                           ▼                                  (up a level)
                     ┌───────────────┐
        ┌───────────►│   PENDING     │◄──── returned for amendment
        │            └───┬───┬───┬───┘
        │                │   │   │
        │      approve ──┘   │   └── request information ──► AWAITING INFO ──┐
        │                    │                                               │
        │                 reject                                             │
        │                    │                                               │
        │                    ▼                                               │
        │              ┌──────────┐                                          │
        │              │ REJECTED │  reason recorded, returned to requester   │
        │              └──────────┘                                          │
        │                                                                    │
        │      ┌─────────────────────────────────────────────────────────────┘
        │      │
        │      ▼
        │   deadline passes (working-hours calendar)
        │      │
        │      ▼
        │  ESCALATED ──► next level in the matrix ──┐
        │                                            │
        └────────────────────────────────────────────┘
                           │  all required approvals obtained
                           ▼
                     ┌───────────┐
                     │ APPROVED  │──► owning module notified; it performs the action
                     └───────────┘    and owns the resulting artefact
                           │
                           ▼
                     ┌───────────┐
                     │  CLOSED   │  immutable trail retained
                     └───────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| Submitted | Approver Derivation | Required attributes present | Requester |
| Approver Derivation | Pending | At least one eligible approver exists who does not breach SoD | System |
| Approver Derivation | Escalated | **Every eligible approver would breach SoD** | System — never routes the breach |
| Pending | Approved | All required approvals per the chain pattern obtained | Approvers |
| Pending | Rejected | Any required approver rejects, with a reason | Approver |
| Pending | Awaiting Info | Approver requests information | Approver |
| Pending | Escalated | Deadline passed on the working-hours calendar, or value/risk threshold met | System |
| Approved | Closed | Owning module confirms the action | Owning module |

### 8.2 Business Rule Change — The Control That Makes 85% Automation Safe

```
   DRAFT ──► SIMULATED ──► IN APPROVAL ──► SCHEDULED ──► ACTIVE
     │       (against       (owning         (effective     │
     │        historical     function        date set)      │
     │        transactions;  approves;                      │
     │        "what would    impact                         │
     │        have changed") analysis                       │
     │                       attached)                      │
     │                            │ rejected                │
     │                            ▼                         │
     └──────────────────────► REWORK                        │
                                                            │
                          unintended consequence observed   │
                                    ┌───────────────────────┘
                                    ▼
                              ROLLED BACK  ──► prior version restored in one action,
                                               rollback recorded, owner notified
                                    │
                                    ▼
                              SUPERSEDED  (retained for audit; still used to evaluate
                                           transactions dated within its validity period)
```

### 8.3 Process Instance with Compensation

```
   STARTED ──► STEP 1 ──► STEP 2 ──► STEP 3 ──► COMPLETED
                  │          │          │
                  │          │          └── fails
                  │          │               │
                  │          │               ▼
                  │          │        COMPENSATING
                  │          └──────► undo step 2 ──┐
                  └─────────────────► undo step 1 ──┤
                                                     ▼
                                              COMPENSATED
                                              (business state restored,
                                               event published, owner alerted)
                                                     │
                        compensation itself fails    │
                                                     ▼
                                              HALTED — NAMED STATE
                                              (never silent; manual
                                               intervention required
                                               and recorded)
```

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-BPA-01 | **Every automation and process step declares its failure behaviour; one that does not cannot be activated** | **H** | CTO |
| BRU-BPA-02 | **A change to an approval threshold, limit or routing rule must not require a code release** | **H** | CTO |
| BRU-BPA-03 | Every business rule is versioned, effective-dated, approved by its owning function, and carries a recorded reason | **H** | CTO |
| BRU-BPA-04 | A rule change must be simulated against historical transactions before activation | **H** | CTO |
| BRU-BPA-05 | A rule can be rolled back to its prior version in one action, and the rollback is recorded | **C** | CTO |
| BRU-BPA-06 | Rule evaluation uses the version in force at the transaction's own date, not today's | **C** | CTO |
| BRU-BPA-07 | A running instance completes on the process and rule versions it started under | **C** | CTO |
| BRU-BPA-08 | The approver chain is derived at submission and frozen on the instance with its deriving rule version | **H** | CFO |
| BRU-BPA-09 | **Approval authority is governed solely by the delegation-of-authority matrix; no module grants approval rights independently** | **H** | CFO |
| BRU-BPA-10 | **Segregation-of-duties rules are evaluated during approver derivation; a request that could only route to a breaching approver escalates instead** | **H** | CFO / CTO |
| BRU-BPA-11 | A requester cannot approve their own request at any level | **H** | CFO |
| BRU-BPA-12 | Delegation of authority is named, time-boxed and recorded; the delegator remains accountable | **H** | CFO |
| BRU-BPA-13 | Out-of-office reassignment must not widen authority beyond the substitute's own matrix entry | **H** | CFO |
| BRU-BPA-14 | Bulk approval is permitted only for homogeneous items below a configured value threshold | **H** | CFO |
| BRU-BPA-15 | Every approval, rejection, delegation, escalation and manual intervention is recorded immutably with actor, time, rule version and reason | **H** | CTO |
| BRU-BPA-16 | **M63 does not write into another module's data; it invokes that module's API and the module performs the action** | **H** | CTO |
| BRU-BPA-17 | Event handlers are idempotent; a redelivered event produces one effect | **H** | CTO |
| BRU-BPA-18 | A multi-module process that fails part-way executes its compensating actions or halts in a named, alertable state | **H** | CTO |
| BRU-BPA-19 | Deadlines, escalations and cycle-time measurement use the working-hours calendar including Bangladeshi holidays and branch shift patterns | **C** | HR Director |
| BRU-BPA-20 | Notifications are emitted as intents to M27; M63 sends nothing directly | **H** | CTO |
| BRU-BPA-21 | Authoring of rules, routing and process definitions is restricted by domain and requires review before release | **H** | CTO |
| BRU-BPA-22 | Simulation executes with no side effects — no notification, no posting, no state change | **H** | CTO |
| BRU-BPA-23 | A manual intervention on a stuck instance is permitted only to an authorised operator and is always recorded | **A** | CTO |
| BRU-BPA-24 | An approval presented to a human includes the artefact, its history, the routing rule, prior approvals and any model recommendation with its explanation | **H** | CTO |
| BRU-BPA-25 | Straight-through processing is measured per process; an exception is routed to a human, never suppressed | **C** | CTO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.process.definition` | `fix_process_definition` | An executable process model | code, name_en, name_bn, owning_module, version, model_definition, steps, author_id, reviewed_by, effective_from, effective_to, state |
| `fix.process.instance` | `fix_process_instance` | One running or completed execution | process_definition_id, definition_version, business_object_ref, started_at, ended_at, current_step, state, correlation_id, started_by |
| `fix.process.step.log` | `fix_process_step_log` | Step-level execution record | process_instance_id, step_code, step_type, started_at, ended_at, outcome, actor_id, failure_behaviour_applied, retry_count, error_ref |
| `fix.compensation.action` | `fix_compensation_action` | Declared and executed compensation | process_definition_id, step_code, compensating_command, executed_for_instance_id, executed_at, outcome |
| `fix.approval.request` | `fix_approval_request` | An approval in flight | business_object_ref, owning_module, request_type, attributes_snapshot, submitted_by, submitted_at, derived_chain, deriving_rule_version, state, decided_at, outcome |
| `fix.approval.step` | `fix_approval_step` | One node of a derived chain | approval_request_id, sequence, pattern (sequential / parallel / quorum / conditional), required_count, candidate_approver_ids, assigned_to, due_at, decided_by, decision, reason, decided_at, delegated_from, escalated_from |
| `fix.authority.matrix` | `fix_authority_matrix` | **The delegation-of-authority matrix** | role_or_person_ref, request_type, value_from, value_to, currency, scope (own / branch / zone / entity / all), entity_id, conditions, effective_from, effective_to, version, approved_by |
| `fix.delegation` | `fix_delegation` | Time-boxed delegation | delegator_id, delegate_id, request_types, value_cap, valid_from, valid_to, reason, recorded_at, active |
| `fix.absence` | `fix_absence` | Out-of-office reassignment basis | person_id, from_date, to_date, substitute_id, source (M21 leave / manual) |
| `fix.business.rule` | `fix_business_rule` | **A governed threshold, limit or condition** | code, name_en, name_bn, rule_type, owning_function, decision_table, parameters, parameter_source (M64 ref), version, effective_from, effective_to, approved_by, change_reason, simulation_ref, superseded_by, state |
| `fix.rule.simulation` | `fix_rule_simulation` | Pre-activation evidence | business_rule_id, candidate_version, historical_period, transactions_evaluated, outcomes_changed, sample_differences, run_by, run_at |
| `fix.rule.impact` | `fix_rule_impact` | What a change affects | business_rule_id, candidate_version, affected_processes, affected_automations, affected_modules, generated_at |
| `fix.escalation.rule` | `fix_escalation_rule` | Escalation configuration | applies_to (request_type / process / step), trigger (time / value / risk / absence), threshold, calendar_id, escalate_to_basis, notify, version, effective_from |
| `fix.task` | `fix_task` | An item awaiting a person | assignee_id, source_type (approval / process step / exception / review), source_ref, title_en, title_bn, priority, created_at, due_at, context_payload, state, actioned_at |
| `fix.working.calendar` | `fix_working_calendar` | Working-hours basis | name, branch_id, shift_pattern, weekly_off, public_holidays, ramadan_hours, effective_from |
| `fix.scheduled.job` | `fix_scheduled_job` | A recurring business job | code, owning_module, command, schedule, calendar_id, dependencies, catch_up_policy, failure_behaviour, owner_id, active |
| `fix.job.run` | `fix_job_run` | One execution | scheduled_job_id, due_at, started_at, ended_at, outcome, records_processed, error_ref, missed_run_flag |
| `fix.event.subscription` | `fix_event_subscription` | Event-driven trigger | event_type, filter_condition, target_process_or_command, idempotency_key_expression, failure_behaviour, owner_id, active |
| `fix.process.performance` | `fix_process_performance` | Measurement | process_definition_id, period, instances, cycle_time_avg, cycle_time_p95, wait_time_avg, touch_count_avg, stp_rate, escalation_rate, bottleneck_step |
| `fix.automation.register` | `fix_automation_register` | The automation-rate denominator | process_area, routine_task_description, volume_per_period, automated_flag, stp_rate, owning_module, last_reviewed |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.role` / `fix.record.rule` / SoD rule set | **M29** | Approver eligibility and SoD evaluation |
| `fix.employee` / reporting line / leave | M21 | Approver derivation and absence-based reassignment |
| `fix.business.parameter` | **M64** | Parameter values used by rules |
| `fix.domain.event` | M28 | Automation triggers |
| `fix.notification` | M27 | Notification delivery |
| `fix.inference.request` | M26 | Recommendation shown with an approval, including its explanation |
| Owning modules' business objects | Each module | Referenced by approval and process instances; **never written directly** |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-BPA-01 | Approval request submitted | Derive the approver chain from attributes, matrix and decision table; evaluate SoD; freeze the chain with its rule version; create tasks | **Block submission** if no eligible approver exists without an SoD breach — and escalate instead |
| AUT-BPA-02 | Task created | Place it in the assignee's inbox; emit a notification intent to M27 on their preferred channel | Retry notification; the task remains visible in the inbox regardless |
| AUT-BPA-03 | Approval deadline approaching | Emit a reminder intent, suppressed against fatigue thresholds | Log; do not spam |
| AUT-BPA-04 | Deadline passed on the working-hours calendar | Escalate to the next matrix level; record the escalation; notify both parties | Escalate again at the next threshold; never silently expire |
| AUT-BPA-05 | Value or risk threshold met | Escalate immediately regardless of elapsed time | Escalate |
| AUT-BPA-06 | Approver recorded absent (M21 leave or manual) | Reassign to the recorded substitute **within the substitute's own authority**; record the reassignment | Escalate to the manager if the substitute lacks authority |
| AUT-BPA-07 | All required approvals obtained | Notify the owning module to perform the action; close the request | Retry; halt in a named state and alert if the module rejects |
| AUT-BPA-08 | Approval rejected | Return to the requester with the reason; close the instance | — |
| AUT-BPA-09 | Domain event received from M28 | Evaluate subscriptions; trigger the matching process or command with an idempotency key | Apply the subscription's declared failure behaviour; never drop silently |
| AUT-BPA-10 | Duplicate event redelivered | Detect by idempotency key; acknowledge without re-executing | Log |
| AUT-BPA-11 | Scheduled job due | Execute in dependency order on the working-hours calendar; record the run | Apply declared failure behaviour; alert the owner |
| AUT-BPA-12 | Scheduled job missed | Detect the missed run; apply the catch-up policy; alert the owner | Escalate on repeated misses |
| AUT-BPA-13 | Process step fails | Apply its declared failure behaviour — block, retry, escalate, fall back or compensate | **Halt in a named, alertable state; never silent** |
| AUT-BPA-14 | Multi-module process fails after partial completion | Execute declared compensating actions in reverse order; publish the compensation event | Halt in a named state; require recorded manual intervention |
| AUT-BPA-15 | Instance stuck beyond threshold | Raise it on the operations board with its current step and last error | Escalate to the process owner |
| AUT-BPA-16 | Business-rule change proposed | Run impact analysis; require simulation against historical transactions; attach both to the approval | **Block activation** without simulation and impact analysis |
| AUT-BPA-17 | Rule change approved | Activate on its effective date; notify affected process owners and modules | Do not activate early; do not activate without notification |
| AUT-BPA-18 | Unintended consequence reported after a rule change | Support one-action rollback to the prior version; record it; notify | Escalate to the owning function |
| AUT-BPA-19 | Delegation period expires | Revoke automatically; return authority to the delegator; notify | Revoke regardless — an expired delegation is not extended silently |
| AUT-BPA-20 | Period close | Compute process performance — cycle time, wait time, touch count, STP rate, escalation rate, bottleneck — and publish to M25 | Alert; do not publish partial figures |
| AUT-BPA-21 | Monthly | Recompute the overall automation rate against the automation register and report progress toward 85% | Log for the CTO review |
| AUT-BPA-22 | Model-informed decision requires human confirmation (M26 BRU-AIM-01) | Route the confirmation as an approval task carrying the prediction and its explanation | Block the decision; never auto-confirm |

---

## 12. Interfaces

### 12.1 Upstream — M63 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M28 Integration & Event Platform** | Domain events as automation triggers; event schemas and delivery | Event subscription |
| **M29 Identity & Security** | Roles, scopes, entitlements and the enterprise SoD rule set for approver derivation | Service |
| M21 Core HR / M55 Workforce | Reporting lines, positions, leave and absence for approver derivation and reassignment | REST + event |
| M64 Master Data Management | Parameter values used by business rules | REST |
| **All 66 modules** | Declared approval needs, escalation requirements, scheduled jobs and thresholds | Design declaration + command |
| M26 AI/ML Services | Recommendations with explanations, presented with the approval; human-confirmation requests | REST |
| M30 Platform Administration | Runtime, queueing and monitoring | Service |

### 12.2 Downstream — M63 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **All 66 modules** | Approval chain execution, escalation, scheduled job execution, event-driven automation, business-rule evaluation | Service + command + callback |
| M27 Contact Centre & Communications | Notification intents for tasks, reminders, escalations and outcomes | Command |
| M25 Business Intelligence | Process performance facts, automation rate, approval cycle time, bottlenecks | Warehouse extract + events |
| M62 Data Platform | Workflow event log for process analysis | Extract |
| M60 GRC | SoD escalations, authority-matrix changes, manual interventions, rule changes | Events |
| M23 Quality | Process conformance evidence and exception records | Extract |
| M24 Documents | Approval trails attached to documents requiring them | Command |
| All portals (P01–P12) | Task inbox and approval surfaces for internal, corporate and partner users | REST |
| Mobile applications | Task inbox, approval, rejection and return | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `approval.requested` | request, type, value, derived chain, rule version | owning module, M27 |
| `approval.granted` | request, approvers, elapsed time | **owning module**, M25 |
| `approval.rejected` | request, approver, reason | owning module, requester |
| `approval.escalated` | request, from, to, trigger (time / value / risk / SoD) | **M60**, management |
| `approval.sod_blocked` | request, breaching rule, escalation taken | **M60**, M29 |
| `task.created` / `task.completed` | assignee, source, due, elapsed | M27, M25 |
| `delegation.recorded` / `delegation.expired` | delegator, delegate, scope, period | **M60**, M29 |
| `authority_matrix.changed` | entry, old, new, approved by, effective date | **M60**, CFO |
| `rule.changed` | rule, version, effective date, simulation reference, impact list | affected modules, **M60** |
| `rule.rolled_back` | rule, from version, to version, reason | affected modules, M60 |
| `process.instance_halted` | instance, step, failure behaviour, error | process owner, M30 |
| `process.compensated` | instance, steps compensated, outcome | owning modules, M60 |
| `job.missed` / `job.failed` | job, due time, catch-up applied, error | owning module, M30 |
| `automation.rate_published` | period, rate, by process area | M25, CTO |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-BPA-01 | n8n (self-hosted) | Bidirectional | Integration-adjacent and scheduled automation flows |
| INT-BPA-02 | Odoo activities and server actions | Bidirectional | Native task surfacing inside ERP screens |
| INT-BPA-03 | M27 delivery channels | Outbound | Notification intents only — **no channel credentials held here** |
| INT-BPA-04 | Bangladesh public holiday calendar | Inbound | Working-hours calendar maintenance |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/workflow/approvals` | POST | Submit an approval request with its attributes | All modules |
| `/api/v1/workflow/approvals/{id}` | GET | Request state, derived chain, current approver, history | Modules, requester, portals |
| `/api/v1/workflow/approvals/{id}/decide` | POST | Approve, reject, return or request information | Approvers, mobile, portals |
| `/api/v1/workflow/tasks` | GET | **The unified inbox for the caller** | Web, mobile, portals |
| `/api/v1/workflow/tasks/{id}/action` | POST | Act on a task | Web, mobile, portals |
| `/api/v1/workflow/rules/{code}/evaluate` | POST | Evaluate a business rule for given inputs at a given date | All modules |
| `/api/v1/workflow/rules/{code}` | GET / PUT | Read or propose a change to a rule | Business analysts |
| `/api/v1/workflow/rules/{code}/simulate` | POST | Simulate a candidate version against historical transactions | Business analysts |
| `/api/v1/workflow/authority-matrix` | GET / PUT | Read or amend the delegation-of-authority matrix | CFO, Finance |
| `/api/v1/workflow/jobs` | GET / POST | Define and monitor scheduled business jobs | Module owners |
| `/api/v1/workflow/processes/{id}/intervene` | POST | Authorised manual intervention on a stuck instance | Platform Squad |
| `/api/v1/workflow/performance` | GET | Cycle time, wait time, STP rate, bottlenecks, automation rate | M25, CTO |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| **R02 Chief Technology Officer** | C R U D A | Process definitions, engine operation, authoring governance, interventions |
| **R26 Finance Manager / CFO** | R U A | **The delegation-of-authority matrix**, value thresholds, bulk-approval limits |
| Business Analyst *(by domain)* | C R U | Rules, routing and escalation configuration in own domain, through review |
| Process Owner *(functional head)* | R U A | Own processes, their targets, escalation timings and performance |
| Platform Squad | C R U A | Engine operation, stuck-instance intervention, job monitoring |
| Any employee | R U | **Own task inbox**; act on tasks assigned to them |
| Approver *(any role in the matrix)* | R U | Approve, reject, return within their matrix entry only |
| R30/R31 HR | R U | Absence and substitution records feeding reassignment |
| R32 Quality Manager / ISO Coordinator | R | Process conformance, exceptions, audit trail |
| R49 GRC / Internal Audit | R | Authority matrix history, SoD escalations, rule changes, interventions |
| R37 Corporate Portal User | R U | Own organisation's approval tasks (e.g. corporate requisition approval) |
| R38 External Party | R U | Own tasks only, where a partner or seller process requires an action |
| R33 IT / System Administrator | — | Runtime operation only; **cannot approve, and cannot amend the authority matrix** |

**Field-level restrictions.** Value thresholds and the authority matrix are visible to Finance,
GRC and the CTO; an approver sees only their own entry. Task context is limited to what the
assignee is entitled to see in the owning module — a task never becomes a route to data the
person could not otherwise open.

**Segregation of duties.**

| Incompatible combination | Why |
|---|---|
| Requester **and** approver of the same request | BRU-BPA-11 — the most basic control in the module |
| Authority matrix amendment **and** approval within it | Nobody grants themselves authority |
| Rule author **and** sole approver of that rule change | A rule change has the blast radius of a code change |
| Platform administration **and** business approval | The engine operator does not decide business outcomes |
| Manual intervention **and** approval of the intervened instance | An operator cannot unstick a process into an outcome they wanted |

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| Task and approval board | Every manager | Real time | Pending tasks by assignee, age, due time, escalation status |
| **Approval cycle time** | CFO, COO, CTO | Daily | Cycle time by request type, function and branch against the **< 4 working hours** target |
| Bottleneck analysis | Process owners, COO | Weekly | Where time is spent per process — wait versus work, touch count, longest steps |
| **Automation rate report** | CEO, CTO | Monthly | Routine operational work automated, by process area, against the **85%** target, with the register denominator |
| Straight-through processing | Process owners | Weekly | STP rate per process; exception volume and reasons |
| Escalation report | Functional heads, GRC | Weekly | Escalations by trigger, role and process — persistent escalation means a threshold or a resourcing problem |
| **SoD escalation report** | GRC, CFO, Internal Audit | Monthly | Requests that could not route without a breach, and how each was resolved |
| Authority matrix register | CFO, GRC, auditor | On change + quarterly | Every entry, its history, who approved each change and when |
| **Rule change log** | CTO, GRC, owning functions | On change | Every rule change, its simulation result, impact list, approver, effective date, and any rollback |
| Release-free change rate | CTO | Monthly | **Workflow changes made without a code release, against the > 95% target** |
| Job execution report | Module owners, Platform Squad | Daily | Scheduled job runs, failures, missed runs, catch-ups |
| Halted and compensated instances | Platform Squad, process owners | Daily | Instances halted or compensated, cause, age, intervention taken |
| Manual intervention log | GRC, CTO | Monthly | Every intervention, operator, instance, reason |
| Delegation register | HR, CFO, GRC | Monthly | Active and expired delegations, scope and value caps |
| Notification fatigue report | CTO, functional heads | Monthly | Reminder and escalation volume per recipient — the early warning that the inbox is being ignored |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W3 Target | W8 Target |
|---|---|---|---|---|
| — | **Approval cycle time (all approvals)** | manual, days | < 8 working hours | **< 4 working hours** |
| — | **Workflow changes made without a code release** | 0% | 85% | **> 95%** |
| — | **Overall automation of routine operational work** | ~20% | 45% | **85%** |
| — | Straight-through processing rate on target processes | ~0% | 40% | **> 70%** |
| — | Approvals escalated for deadline breach | n/a | < 20% | **< 10%** |
| — | **Automations activated without a declared failure behaviour** | n/a | **0** | **0** |
| — | **Rule changes activated without simulation and impact analysis** | n/a | **0** | **0** |
| — | **Requests routed to an approver in breach of SoD** | n/a | **0** | **0** |
| — | Self-approved requests | n/a | **0** | **0** |
| — | Instances halted without a named state | n/a | **0** | **0** |
| — | Scheduled jobs missed without detection | n/a | **0** | **0** |
| — | Duplicate effects from redelivered events | n/a | **0** | **0** |
| — | Approver derivation p95 latency | n/a | < 800 ms | **< 500 ms** |
| — | Task inbox load p95 | n/a | < 3 s | **< 2 s** |
| — | Mobile approval share of all approvals | 0% | 40% | **> 65%** |
| — | Rule rollbacks per quarter *(a health signal, not a failure)* | n/a | tracked | tracked |

**Seven of these targets are zero.** Declared failure behaviour, simulation, SoD, self-approval,
named halt states, missed-job detection and idempotency are the controls that make automation at
85% safe rather than reckless. The overview names automation-at-scale error as a High risk; these
seven are the mitigation, expressed as measurements.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo activities, server actions, automated actions — native task surfacing inside ERP screens | 12% |
| L3 | Workflow engine runtime, n8n for integration-adjacent and scheduled flows, event subscription handling | 26% |
| L5 | `cd_workflow_engine`, `cd_approval_matrix`, `cd_business_rules`, `cd_job_scheduler` | 62% |

**Engine decision.** n8n is already deployed from W1 and carries integration-adjacent and
scheduled automation well. It is **not** used for approvals: it has no delegation-of-authority
model, no SoD enforcement, no effective-dated rule versioning and no approval audit trail.
Approvals, the authority matrix and the rule repository are custom, built on BPMN/DMN semantics
rather than on a second engine — adopting Camunda alongside n8n would mean operating two workflow
runtimes for one company.

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-196** | `cd_workflow_engine` — process definition and versioning, durable instance state, step execution, **declared failure behaviour**, compensation and rollback, simulation sandbox, manual intervention, event subscription with idempotency, process performance measurement | Service + Odoo surface | **6 PW** |
| **CD-197** | `cd_approval_matrix` — delegation-of-authority matrix, derived approval chains, chain patterns, **SoD enforcement in routing**, delegation and substitution, absence reassignment, approval audit trail, **unified task inbox**, mobile and portal approval | Odoo module + service | **5 PW** |
| **CD-198** | `cd_business_rules` — decision-table repository, versioning and effective dating, change control and approval, simulation against history, impact analysis, one-action rollback, authoring governance by domain | Odoo module + service | **4 PW** |
| **CD-199** | `cd_job_scheduler` — scheduled business jobs, working-hours calendar with Bangladeshi holidays and shift patterns, dependency ordering, missed-run detection and catch-up, escalation rules, automation register and rate measurement | Odoo module + service | **4 PW** |
| | **Total** | | **19 PW** |

> **CD allocation.** M63 is new in v2.1 and had no allocation in `02-05` §5.2. **CD-196…199 are
> claimed from the Category J extension block** (CD-187 onward, following Category G's block
> ending at CD-186). Raised as an audit action against `02-05`.

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M63 is scheduled in **W3** (P1) but declares a dependency on 1 module(s) that land later: **M27** (W4). One of three things must be true before the W3 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W3 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M63 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W3 plan for M63 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| **M28 Integration & Event Platform (W1)** | Domain events are the primary automation trigger |
| **M29 Identity & Security (W1)** | Approver eligibility, scopes and the enterprise SoD rule set |
| M30 Platform Administration (W1) | Runtime, queueing and monitoring |
| M64 Master Data Management (W2) | Parameter values consumed by rules |
| M21 Core HR (W5) — **partial dependency** | Reporting lines and leave records improve approver derivation and absence reassignment. **W3 launches with matrix-based derivation only**; reporting-line derivation is added when M21 lands |
| M27 Contact Centre (W4) — **partial dependency** | Notification delivery. **At W3, task visibility is inbox-based**; push notification arrives with M27 |
| **M63 must land in W3, before the finance modules** | Overview §10: *"approvals and workflow from the first money module."* M19, M20, M52 and M50 all go live in W3–W4 and each needs a working approval chain on day one |

**Dependency note.** M63 is scheduled *earlier* than two modules it benefits from (M21 W5, M27
W4). This is deliberate and the degraded W3 mode is specified rather than assumed: matrix-based
approver derivation without reporting-line inference, and inbox-based task visibility without
push notification. Both upgrade in place when their dependencies land.

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| **The existing delegation-of-authority policy** | All approval limits currently in force | `fix.authority.matrix` | W3 cutover |
| Approval thresholds embedded in current practice | Discount limits, credit limits, write-off ceilings, purchase limits | `fix.business.rule` decision tables | W3 cutover |
| Existing recurring manual routines | Every recurring operational task | `fix.automation.register` — **the denominator for the 85% target** | W3 |
| Existing scheduled scripts and reminders | All in use | `fix.scheduled.job` | W3 cutover |
| In-flight approvals at cutover | Open items only | `fix.approval.request` | W3 cutover |
| Historical approval records | **Not migrated** — no consistent trail exists | — | — |

**Migration note.** As with M25, the migration here is **organisational, not technical**. Two
artefacts must be produced before W3, and neither exists today in usable form: a complete,
agreed **delegation-of-authority matrix**, and a complete **register of routine operational
work** — because without the latter, the 85% automation target has no denominator and cannot be
measured, only claimed.

### 16.5 Register Variance

| Figure | `02-02` Estimate | Measured | Note |
|---|---:|---:|---|
| Requirements | 28 | **32** | +14% — simulation, impact analysis, compensation and the automation register were not separable in the estimate |
| Effort | 16 PW | **19 PW** | +19% — concentrated in SoD-aware approver derivation and the rule-simulation sandbox |

Both require `02-02` §2 Category J to be updated. An FR prefix (`BPA`) must also be allocated in
`05-01` §1.3. Raised as audit actions.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **An approval threshold can be changed, simulated, approved and made effective without a code release or deployment** | End-to-end test on a live threshold |
| AC-02 | **An automation or process step cannot be activated without a declared failure behaviour** | Negative test |
| AC-03 | **A rule change cannot be activated without simulation against historical transactions and an impact analysis** | Negative test |
| AC-04 | A rule can be rolled back to its prior version in one action, with the rollback recorded | Rollback test |
| AC-05 | Rule evaluation for a back-dated transaction uses the version in force at that transaction's date | Effective-dating test across three versions |
| AC-06 | A running instance completes on the process and rule versions it started under, despite a mid-flight change | Concurrency test |
| AC-07 | The approver chain is derived from transaction attributes, frozen on the instance with its rule version, and reconstructable afterwards | Derivation and reconstruction test |
| AC-08 | **A request that could only route to an approver in breach of SoD escalates instead of routing** | Negative test against all twelve `05-04` §6 SoD rules |
| AC-09 | **A requester cannot approve their own request at any level** | Negative test |
| AC-10 | Out-of-office reassignment does not widen authority beyond the substitute's own matrix entry | Negative test |
| AC-11 | An expired delegation revokes automatically and authority returns to the delegator | Timed scenario |
| AC-12 | Bulk approval is refused above the configured value threshold | Boundary test |
| AC-13 | Every approval, rejection, delegation, escalation and intervention is recorded immutably with actor, time, rule version and reason | Audit trail review and tamper test |
| AC-14 | A task appears in exactly one unified inbox regardless of which module raised it, and can be actioned from mobile | Cross-module test across eight source modules |
| AC-15 | Deadlines and escalations respect the working-hours calendar including a Bangladeshi public holiday and a branch shift pattern | Calendar test |
| AC-16 | **A redelivered domain event produces one effect, not two** | Duplicate-delivery test |
| AC-17 | **A multi-module process that fails part-way executes its compensating actions, or halts in a named alertable state — never silently** | Injected-failure test on a three-module process |
| AC-18 | **M63 cannot write into another module's tables** | Code and connection-layer audit |
| AC-19 | Simulation produces no side effects — no notification, no posting, no state change | Side-effect audit during simulation |
| AC-20 | A missed scheduled job is detected and its catch-up policy applied | Injected-outage test |
| AC-21 | An approval presented to a human includes the artefact, its history, the routing rule, prior approvals and any model recommendation with its explanation | Content review across five request types |
| AC-22 | A human-confirmation request from M26 (BRU-AIM-01) routes as an approval task and cannot auto-confirm | Integration test |
| AC-23 | M63 holds no notification channel credentials; all delivery is via M27 | Configuration audit |
| AC-24 | Approver derivation and task inbox load meet their p95 targets under production-scale load | Load test |
| AC-25 | The automation register produces a defensible denominator, and the automation rate reconciles to it | Register audit |
| AC-26 | CTO, CFO and two functional heads sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 26 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Does a complete, agreed delegation-of-authority matrix exist?** If not, it must be produced and board-approved before W3. The module cannot route an approval against a policy that has not been written down | **CFO / Board** | **W3 minus 3 months** |
| Q-02 | **What is the register of routine operational work that forms the denominator of the 85% automation target?** Without it the target cannot be measured | COO / CTO | **W3 minus 2 months** |
| Q-03 | Who may author business rules, in which domains, and who reviews? The governance model determines whether >95% release-free change is achievable or dangerous | CTO / functional heads | **W3 minus 2 months** |
| Q-04 | What are the approval cycle-time targets per request type? A four-hour target is an average; a payment run and a leave request are not the same problem | CFO / COO | W3 build |
| Q-05 | **Does n8n's Sustainable Use licence — internal business purposes only — cover workflow that surfaces approval tasks to corporate portal and marketplace-seller users?** `02-05` records it as *"used only for internal orchestration"*, and portal-facing tasks may test that boundary | CTO / Legal | **W3 minus 2 months** |
| Q-06 | What is the working-hours calendar — branch shift patterns, weekly off days, Ramadan hours, and the public holiday source? Every deadline in the ERP depends on it | HR Director | **W3 minus 2 months** |
| Q-07 | At W3, M21 (W5) and M27 (W4) are not live. Is the specified degraded mode — matrix-only derivation, inbox-only visibility — acceptable, or should M63 move to W4? | Programme Director | **W3 minus 3 months** |
| Q-08 | Which processes are targeted for straight-through processing first, and what exception rate is acceptable for each? | COO / functional heads | W3 build |
| Q-09 | What is the escalation path when the escalation target is themselves absent or the matrix has no next level? | CFO | W3 build |
| Q-10 | Do corporate clients and marketplace sellers approve anything within their own organisation through the portals? If so, their internal authority model must be represented | Chief Commercial Officer | W4 |
| Q-11 | **Reciprocity gap (audit finding).** Forty-plus written module specifications declare approvals, escalations, scheduled jobs and thresholds, but only two name **M63** as the executor. Each of those modules' §3.2 and §12.1 should delegate to M63 explicitly, or this module's claim is one-sided | CTO | **W3 minus 2 months** |
| Q-12 | Is the FR prefix `BPA` accepted, given M63 was not in the 30-module allocation in `05-01` §1.3? | Programme Director | W3 build |

**Q-01 and Q-02 are not design questions.** They are governance artefacts that must exist before
the module can be configured, and producing them is a business exercise with a real lead time.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` (Category J **§4 the M28/M63 split**, §5 boundary map, §9 KPIs,
§10 delivery sequence, §11 the automation-at-scale risk) ·
`M62_Data_Platform_Warehouse_and_Governance.md` (pipeline scheduling boundary) ·
`M25_Business_Intelligence_and_Reporting.md` (schedule execution for subscriptions and alerts) ·
`M26_AIML_Services_and_Model_Operations.md` §9 BRU-AIM-01 *(human confirmation routed here)* ·
`03_Modules/K_Platform_and_Technology/_CATEGORY_OVERVIEW.md` *(M28 boundary)* ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` (n8n, licence compliance notes) ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §6
*(the twelve enterprise SoD rules enforced in routing)* ·
`05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md` ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` ·
§9 and §11 of every written module specification — the approvals, escalations, jobs and
thresholds this module executes

**Workspace evidence**
`ERP system for 1000 fix/project_implementation_doc/14_n8n_Workflow_Specifications.md` ·
`00_Governance_and_Charter/00-02_Executive_Summary_and_Scope_Charter.md` §Benefit Register

**External benchmark**
**SAP Business Workflow / Flexible Workflow** — centrally-defined approval processes with agent
determination, deadline monitoring, escalation and substitution, decoupled from the transactional
application ·
**Oracle BPM / Approval Management Extensions** — rule-driven derivation of the approver list from
transaction attributes rather than a chain stored per document type ·
**Microsoft Dynamics 365 workflow + Power Automate** — business-user authoring with a governed
release path and a unified approval inbox ·
**Camunda (BPMN 2.0 + DMN)** — a stateful, event-sourced engine executing BPMN 2.0 with service
tasks, user tasks, business-rule tasks and message/signal events; **DMN decision tables** managing
elaborate assignment and routing rules in a business-readable form; orchestration across APIs,
microservices, human work and bots ·
**n8n** — self-hosted visual workflow automation, Sustainable Use licence permitting internal
business use ·
**Saga and compensation patterns** — explicit compensating actions for long-running multi-step
processes ·
**Process mining practice** — discovering the actual process from event logs and comparing it with
the intended model to expose variants, rework and bottlenecks ·
**Delegation-of-authority practice** — a governed, versioned matrix of who may approve what, to
what value, in what scope, with substitution, escalation and periodic review ·
**Straight-through processing practice** — defining the no-human happy path and measuring the
proportion of volume that achieves it

**Sources consulted**
- [Camunda — BPMN workflow engine](https://camunda.com/products/camunda-bpm/bpmn-engine)
- [Camunda — user task assignment based on a DMN decision table](https://camunda.com/blog/2020/05/camunda-bpm-user-task-assignment-based-on-a-dmn-decision-table/)
- [Camunda BPM guide — BPMN 2.0, DMN and process orchestration](https://eitt.academy/knowledge-base/camunda-bpm-complete-business-process-management-guide/)
- [n8n — licence and self-hosting terms](https://docs.n8n.io/sustainable-use-license/)
- [Oracle — Approval Management and rule-based approver derivation](https://docs.oracle.com/en/cloud/saas/index.html)

---

*Module M63 · Category J · 1000FiX ERP System v2.0 · CONFIDENTIAL*
