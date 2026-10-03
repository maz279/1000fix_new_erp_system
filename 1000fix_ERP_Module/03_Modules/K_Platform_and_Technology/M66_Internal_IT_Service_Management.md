---
id: FIX-ERP2-M66
module_id: M66
module_code: ITS
module_name: Internal IT Service Management
category: K — Platform & Technology
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Technology Officer
system_owner: Platform Squad
priority: P2
wave: W6
---

# M66 — Internal IT Service Management
### Category K · Code `ITS` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M66 |
| **Module code** | `ITS` |
| **Category** | K — Platform & Technology |
| **Status** | ★ **New** in v2.1 — the Company's own IT, previously not modelled at all |
| **Priority** | **P2** |
| **Delivery wave** | W6 (Months 23–26) |
| **Business owner** | Chief Technology Officer |
| **System owner** | Platform Squad |
| **Delivery layers** | L2 OCA `helpdesk`, `management-system` · L5 custom ITSM process, CMDB and IT asset modules |
| **Custom modules** | `cd_itsm`, `cd_it_asset` |
| **Requirement range** | FR-ITS-001 … FR-ITS-030 |
| **Requirement count** | **30** *(measured — supersedes the 22 estimate in `02-02`; **new range allocation** under `05-01` §1.3a)* |
| **Effort estimate** | **14 person-weeks** *(measured — supersedes the 11 PW estimate)* |
| **Depends on** | M29 Identity · M30 Platform Admin · M21 Core HR · M28 Integration · M16 Procurement · M24 Documents |
| **Depended on by** | M30, M28, M29, M23, M60, M61 — and **every employee in the Company** |

---

## 2. Purpose

M66 is **the Company's own IT service desk, asset register and change process**.

1000FiX employs somewhere between 500 and 1,000 people across 51+ branches, workshops, a
central warehouse and a corporate office. Every one of them depends on a laptop, a phone, a
scanner, a network connection, a printer, an email account and a set of application logins.
When one of those fails, the person stops working. Today that is resolved by calling or
messaging whoever in IT answers first, and nothing about it is recorded — not the problem, not
the fix, not how long it took, and not the fact that the same fault has occurred eleven times
this month.

The category overview makes the second point sharply: *"Internal IT support runs on WhatsApp
while clients get a portal — Medium risk to credibility and productivity. M66 delivered in
Wave 6; the Company uses its own product."* A service company that cannot run its own service
desk has a credibility problem it will eventually be asked about by a client.

M66 also owns **the Company's IT assets** — the laptops, phones, scanners, printers, network
equipment and software licences — and **the change process** by which the platform is altered.

### Why It Exists

**Because internal IT support is currently invisible.** No ticket, no SLA, no trend, no
problem management. A recurring fault is experienced as bad luck rather than as a problem with
a root cause.

**Because company IT assets are untracked.** The category KPI is **100% of company IT assets
tracked**, against "manual" today. Every laptop is a capital item, a data-protection exposure
and a leaver-recovery obligation. An untracked laptop that leaves with a departing employee is
a PDPA incident waiting to be discovered.

**Because software licences are a compliance and cost exposure.** Unused licences are wasted
money; unlicensed installations are a legal exposure and an audit finding.

**Because change needs a process, not just a record.** M30 holds the configuration change
*trail*; M66 runs the change *process* — assessment, approval, scheduling, implementation and
review. A 67-module estate deployed weekly needs both.

**Because platform alerts need somewhere to go.** M28 detects an integration failure and M30
fires an alert. Without M66 those become messages in a channel. With it they become incidents
with an owner, an SLA and a post-incident review.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| `_CATEGORY_OVERVIEW.md` §2 | M66 owns "the Company's own IT: employee helpdesk, internal asset and licence management, change and incident management" |
| `_CATEGORY_OVERVIEW.md` §3 | **The M66/M05 boundary** — serves, revenue model, SLA type, assets, failure cost and analogue, with the conclusion that "they share a ticket shape and nothing else" and that merging them would put internal helpdesk noise in a system audited by paying clients |
| `_CATEGORY_OVERVIEW.md` §6 | M66 owns internal employee IT support and company IT assets; **not M05, not M45** |
| `_CATEGORY_OVERVIEW.md` §9 | **Internal IT tickets resolved within SLA > 92%**; **company IT assets tracked 100%** |
| `_CATEGORY_OVERVIEW.md` §11 | Risk: "Internal IT support runs on WhatsApp while clients get a portal — Medium, credibility and productivity". Mitigation: "M66 delivered in Wave 6; **the Company uses its own product**" |
| `05-04` §1 | Population served: 38 roles, headcounts summing to several hundred internal staff across 51+ branches |
| `05-06` NFR-003 | 800+ concurrent internal users without degradation |
| `05-06` OPS-01, OPS-03, OPS-05 | Deployments automated and reversible; every alert has a runbook; every job reports its outcome — the operational disciplines M66's change and incident processes wrap |
| `05-06` NFR-062, NFR-063, NFR-066 | Secrets, malware scanning and vulnerability scanning — security operations that raise incidents into M66 |
| `05-06` NFR-072 | Security incident response with defined severities — M29 owns the security judgement, M66 runs the process |
| `05-06` NFR-086c, NFR-071 | Non-production masking — a change-control concern |
| `02-05` §9 | Development environment and practice: branching, CI/CD, deployment gates — the release discipline M66's change process governs |

---

## 3. Scope Boundary

> **The rule:** M66 serves **1000FiX's own employees and 1000FiX's own IT estate**. The moment
> the customer is a paying client, it is M05. The moment the asset is a customer's device, it is
> M17. The moment the asset is a workshop tool, it is M45.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | **IT service catalogue** — what internal IT provides, to whom, with what SLA |
| 2 | Employee self-service portal for requests, incidents and status |
| 3 | **Request fulfilment**: standard requests with defined approval and delivery workflows |
| 4 | **Incident management**: logging, categorisation, prioritisation, assignment, resolution, closure |
| 5 | Major incident handling with communication and escalation |
| 6 | Internal SLA definition, measurement, breach warning and reporting |
| 7 | Tiered support model with escalation paths |
| 8 | **Problem management**: recurring-incident detection, root cause analysis, known errors, workarounds, permanent fixes |
| 9 | **Change management**: request, risk and impact assessment, approval, scheduling, implementation, verification, review |
| 10 | Change types: standard (pre-approved), normal, emergency |
| 11 | Change calendar, collision detection and freeze-period enforcement |
| 12 | Release coordination and post-implementation review |
| 13 | **IT asset management**: laptops, desktops, phones, tablets, scanners, printers, network equipment, servers |
| 14 | Asset lifecycle: request, procure, receive, allocate, transfer, service, recover, dispose |
| 15 | **Employee onboarding and offboarding IT workflows**, driven by M21 events |
| 16 | Asset allocation to employees with acceptance and accountability |
| 17 | **Software asset management**: entitlements, installations, reconciliation, compliance position |
| 18 | Licence optimisation: unused and under-used licence identification and reallocation |
| 19 | Subscription and renewal management for IT services |
| 20 | Shadow-IT detection and the governed software request path |
| 21 | **Configuration management database (CMDB)**: configuration items and their relationships |
| 22 | Service mapping: which configuration items support which business service |
| 23 | IT knowledge base with self-service articles and deflection measurement |
| 24 | IT budget consumption and cost transparency by branch and cost centre |
| 25 | Vendor and support-contract register for IT services |
| 26 | IT service reporting and employee satisfaction measurement |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Client-facing managed services, RMM, client tickets, client SLAs with service credits** | **M05** Remote Support & Managed Services | **The defining boundary.** M05 is billable revenue with contractual SLAs and client audits; M66 is an internal cost centre. `_CATEGORY_OVERVIEW.md` §3 sets out the six-dimension comparison. Merging them puts internal helpdesk noise into a system paying clients audit |
| Customer devices under repair | **M17** Device & Customer Asset Registry | A customer's laptop is never a company IT asset |
| **Workshop tools, test equipment, calibrated instruments** | **M45** Enterprise Asset & Test Equipment | A multimeter and an oscilloscope are workshop assets with calibration obligations, not IT assets |
| Vehicles | **M46** Fleet | — |
| Branch premises, fit-out, utilities, physical infrastructure | **M47** Facility | M66 owns the network switch; M47 owns the room it is in |
| Spare parts and consumable stock | **M15** Inventory | An IT asset is allocated and recovered; a part is consumed |
| Fixed-asset accounting, depreciation, capitalisation | **M49** Fixed Assets | M66 tracks the asset operationally; M49 accounts for it |
| Purchase requisition, PO, receipt, three-way match | **M16** Procurement | M66 raises the need; M16 buys it |
| Identity, roles, permissions, access provisioning | **M29** | M66 *requests* access through its onboarding workflow; M29 decides and grants |
| Security judgement, breach assessment, vulnerability triage | **M29** | **M29 owns the security decision; M66 runs the incident process around it** |
| Platform health monitoring, alerting, job registry, configuration change trail | **M30** | **M30 detects and records; M66 responds and governs the process** |
| Integration health and dead letters | **M28** | M28 detects; M66 runs the incident |
| Employee record, contract, roster, payroll | **M21** / **M55** / **M56** | M66 consumes joiner and leaver events |
| Quality management system, ISO audits, CAPA | **M23** | M66 raises quality signals; M23 owns the QMS |
| Enterprise risk, compliance obligations, GRC | **M60** | — |
| Knowledge management for **technical repair** knowledge | **M61** Knowledge Management | M66's knowledge base covers internal IT only |
| IT projects with phases, budget and milestones | **M67** PPM | M66 runs changes; M67 runs projects |
| E-waste disposal and recycling compliance | **M18** | M66 retires the asset; M18 disposes of it lawfully |
| Data destruction before disposal | **M06** Data Services | A retired laptop must be wiped before it leaves |

### 3.3 Shared Concepts

| Concept | M66's Role | Owning Module |
|---|---|---|
| Ticket | **Owns** the internal ticket; M05 owns the client ticket; M01 owns the service order | M66 / M05 / M01 |
| SLA | **Owns** internal targets; M08 owns contractual SLAs | M66 / M08 |
| Incident | **Owns** the IT incident process; M29 owns the security judgement within a security incident | M66 / M29 |
| Change | **Owns** the ITIL change process; M30 owns the configuration change trail | M66 / M30 |
| Configuration item | **Owns** the CMDB; M30 owns the platform objects it describes | M66 / M30 |
| IT asset | **Owns** operationally; M49 accounts for it; M16 buys it; M18 disposes of it | M66 / M49 / M16 / M18 |
| Software licence | **Owns** employee software; M30 owns platform component licences | M66 / M30 |
| Employee | Reads identity and joiner/leaver events | M21 |
| Knowledge article | **Owns** internal IT knowledge; M61 owns technical repair knowledge | M66 / M61 |
| Alert | Receives and converts to an incident; M30 and M28 raise them | M66 / M30 / M28 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **ServiceNow ITSM** | The four core processes — **incident, problem, change and request fulfilment** — on one platform with a CMDB, automated workflows, centralised records and cross-process visibility | **The four-process core is M66's structure**, and the CMDB as the connective tissue between them. Also adopted: **a tiered support structure with defined escalation paths**, workflow automation for common incidents, and an updated knowledge base as first-line deflection | ServiceNow's platform scale, its licensing, and its process configurability. 1000FiX has one internal IT team; a configurable process engine would cost more to configure than to use |
| **ITIL 4 practice** | Incident restores service; problem removes cause; change controls risk; request fulfils standard need. Problem management is both **reactive** (after incidents) and **proactive** (identifying potential incidents before they occur) | **The reactive/proactive split in problem management**, and the discipline that an incident is closed when service is restored while the *problem* stays open until the cause is removed. This is the difference between a helpdesk and an IT function | ITIL certification as an objective, and the full 34-practice framework. Four processes done properly beats thirty-four done nominally |
| **ITIL 4 / ServiceNow change management** | CAB workflow, **risk assessment**, approval routing, standard changes pre-approved, change calendar, all changes and approvals logged for compliance | **Three change types — standard, normal, emergency — with standard changes pre-approved**, because a change process that treats a routine password reset like a database migration will be bypassed. Also adopted: the change calendar with **collision detection** | A formal Change Advisory Board meeting cadence; approval is routed by risk, and a weekly meeting would delay more than it protects at our change volume |
| **CMDB practice** | Configuration items and relationships; asset management integrated with ITSM so assets support service delivery and compliance | **A deliberately shallow CMDB**: configuration items and the service mapping that answers "what breaks if this fails", populated by discovery rather than by hand | Deep CMDB modelling. An over-modelled CMDB that nobody maintains is worse than none, because it is trusted and wrong |
| **Software Asset Management (SAM) / ITAM practice** | SAM as the discipline for software compliance, usage transparency and cost control; **a live inventory updated on every install and removal**; a **clear request process with approvals to prevent unauthorised software and shadow IT**; identification of unused or under-used licences for reallocation | **The full pattern.** Entitlement-versus-installation reconciliation as the compliance position; **unused licence identification as an ongoing cost lever**; and a governed software request path as the practical answer to shadow IT | Automated software metering on every endpoint at Wave 6; discovery starts with the estate that can be inventoried cheaply |
| **ITAM lifecycle practice** | Clear policies with roles and responsibilities; automated discovery and tracking; regular audits; cross-department collaboration; proper records | **Employee onboarding and offboarding as the primary asset control point** — allocation is recorded at joining and recovery is enforced at leaving. Most asset loss happens at the leaver event, and M21's event is what makes it enforceable | Annual physical audit as the primary control; continuous discovery plus leaver enforcement is cheaper and more accurate |

**Design position.** Five deliberate differences.

First, **M66 and M05 are separate systems that share a shape**. The temptation to reuse the MSP
ticketing engine for internal support is strong and would be a mistake. M05 carries contractual
SLAs with service credits, is audited by paying clients, and its data is client-confidential.
Internal helpdesk noise inside it degrades a revenue-generating system. They share a ticket
shape and nothing else.

Second, **the Company uses its own product, and that is a stated design intent**. The category
mitigation is explicit. There is a credibility argument — a service company whose own staff
support each other on WhatsApp is vulnerable to an obvious question — and a practical one: the
internal team experiences the service-desk pattern before selling it.

Third, **the leaver event is the asset control point**. Asset registers decay because
allocation is recorded and recovery is not. M21's `employee.left` event drives a mandatory
recovery workflow — device returned, wiped through M06, reallocated or retired through M18 —
and an outstanding recovery blocks final settlement. This is what makes 100% asset tracking
achievable rather than aspirational.

Fourth, **the CMDB is deliberately shallow**. It answers one question well: *what breaks if
this fails?* Deep configuration modelling is expensive to build, expensive to maintain, and
becomes unreliable within a year — at which point it is trusted and wrong, which is worse than
absent.

Fifth, **M66 receives platform signals rather than generating them**. M28 detects an integration
failure; M30 fires an alert; M29 judges a security event. M66 turns each into an incident with
an owner, an SLA and a review. It does not monitor, and it does not decide whether something is
a security breach. This keeps detection with the modules that own the domain and process with
the module that owns the discipline.

---

## 5. Functional Areas & Features

### 5.1 Service Catalogue & Request Fulfilment

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ITS-001 | IT service catalogue | Maintain the catalogue of internal IT services with description, eligibility, approval requirement, fulfilment steps, target time and owner, in Bengali and English | **P0** | L5 |
| FR-ITS-002 | Employee self-service portal | Provide a self-service surface where any employee can raise a request or an incident, track it, and find knowledge articles — accessible on desktop and mobile | **P0** | L2/L5 |
| FR-ITS-003 | Request fulfilment | Fulfil standard requests — new device, software access, peripheral, network access, printer setup, mailbox change — through a defined approval and delivery workflow | **P0** | L2/L5 |
| FR-ITS-004 | Request approval routing | Route requests for approval by type, cost and role, with line-manager approval by default and additional approval above a cost threshold | **P0** | L5 |
| FR-ITS-005 | Catalogue-driven automation | Automate fulfilment where the steps are deterministic — account creation requests to M29, software allocation from an available licence pool, standard device build | P1 | L5 |

### 5.2 Incident Management

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ITS-006 | **Incident logging** | Log an incident from any channel — self-service portal, email, phone, or automatically from an M28, M29 or M30 signal — with category, affected service, affected user and configuration item | **P0** | L2/L5 |
| FR-ITS-007 | Categorisation and prioritisation | Prioritise by impact and urgency against a defined matrix, so that a branch offline outranks a single user's printer | **P0** | L5 |
| FR-ITS-008 | **Tiered assignment and escalation** | Assign to the correct support tier with defined escalation paths, and escalate automatically on SLA threshold breach | **P0** | L5 |
| FR-ITS-009 | **Internal SLA measurement** | Define response and resolution targets per priority and service, measure attainment, warn before breach, and report — **target > 92% resolved within SLA** | **P0** | L5 |
| FR-ITS-010 | Major incident handling | Declare a major incident with a named incident manager, a communication cadence to affected users through M27, and a mandatory post-incident review | **P0** | L5 |
| FR-ITS-011 | Incident linkage | Link an incident to its configuration item, to a problem, to a change that caused it, and to other incidents with the same symptom | **P0** | L5 |
| FR-ITS-012 | Resolution and closure | Record the resolution, confirm restoration with the affected user, capture satisfaction, and close — **with the underlying problem remaining open if the cause is unresolved** | **P0** | L5 |

### 5.3 Problem Management

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ITS-013 | **Reactive problem detection** | Detect recurring incidents by symptom, configuration item and category, and propose a problem record automatically above a recurrence threshold | **P0** | L5 |
| FR-ITS-014 | **Proactive problem identification** | Identify potential incidents before they occur from trend, capacity, error rate and asset-age signals supplied by M30 and M28 | P1 | L5 |
| FR-ITS-015 | Root cause analysis | Record the investigation, method and root cause, with evidence and the incidents it explains | **P0** | L5 |
| FR-ITS-016 | Known errors and workarounds | Publish a known error with its workaround to the knowledge base, so first line can restore service before the cause is fixed | **P0** | L5 |
| FR-ITS-017 | Permanent fix and verification | Drive the permanent fix through a change, verify that recurrence stops, and close the problem only on verified effectiveness | **P0** | L5 |

### 5.4 Change & Release Management

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ITS-018 | **Change request and types** | Raise a change with description, justification, affected configuration items, implementation plan, test plan and back-out plan, classified as **standard (pre-approved), normal or emergency** | **P0** | L5 |
| FR-ITS-019 | **Risk and impact assessment** | Assess risk and impact from the affected configuration items and their service mapping, and route approval by the assessed risk rather than by a fixed hierarchy | **P0** | L5 |
| FR-ITS-020 | Change calendar and collision detection | Maintain a forward change calendar, detect collisions between changes affecting the same configuration items, and enforce the freeze periods declared in M30 | **P0** | L5 |
| FR-ITS-021 | Emergency change | Provide an expedited path with post-implementation approval and mandatory review, mirroring M30's configuration emergency discipline | **P0** | L5 |
| FR-ITS-022 | **Implementation and verification** | Record implementation, verify success against the test plan, and trigger the back-out plan on failure | **P0** | L5 |
| FR-ITS-023 | Post-implementation review | Review every emergency change, every failed change and every major change, and feed findings to problem management | **P0** | L5 |
| FR-ITS-024 | Change–incident correlation | Correlate incidents arising shortly after a change to the change that caused them, and report change-caused incident rate | P1 | L5 |

### 5.5 IT Asset & Software Asset Management

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ITS-025 | **IT asset register** | Maintain every company IT asset — laptop, desktop, phone, tablet, scanner, printer, network device, server — with serial, specification, purchase reference, warranty, location, cost centre, status and allocated employee | **P0** | L5 |
| FR-ITS-026 | **Asset lifecycle** | Manage request, procurement through M16, receipt, build, allocation with employee acceptance, transfer, service, recovery and disposal through M18 — **with data destruction via M06 before any device leaves** | **P0** | L5 |
| FR-ITS-027 | **Onboarding and offboarding workflows** | On `employee.joined`, allocate the standard asset set for the role and raise the access requests to M29; on `employee.left`, **drive mandatory asset recovery, block final settlement while an asset is outstanding**, and confirm wipe and reallocation or retirement | **P0** | L5 |
| FR-ITS-028 | **Software asset management** | Maintain software entitlements and installations, reconcile them to a compliance position, identify unused and under-used licences for reallocation, manage subscriptions and renewals, and detect unauthorised software with a governed request path | **P0** | L5 |
| FR-ITS-029 | **Configuration management database** | Maintain configuration items and their relationships, populated by discovery where possible, with **service mapping answering "what breaks if this fails"** | **P0** | L5 |
| FR-ITS-030 | **Knowledge base, reporting and cost transparency** | Maintain internal IT knowledge articles in Bengali and English with self-service deflection measurement; report service performance, SLA attainment, asset position, licence compliance and IT cost consumption by branch and cost centre; and maintain the IT vendor and support-contract register | **P0** | L5 |

> **Note on grouping.** FR-ITS-028, FR-ITS-029 and FR-ITS-030 each aggregate a coherent
> discipline rather than a single feature, in proportion to M66's P2 priority and 14 PW envelope.
> Every sub-obligation is separately testable and appears individually in §17.

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Separation from M05** | M66 and M05 share no database tables and no ticket model. Verified by dependency analysis. Internal ticket data never appears in a client-facing view |
| T-02 | **Signal ingestion** | Alerts from M30, integration failures from M28 and security events from M29 arrive as events and create incidents automatically, with de-duplication so one outage produces one incident, not two hundred |
| T-03 | **Incident de-duplication and correlation** | Incidents with the same configuration item and symptom within a window correlate to a parent, so a branch outage is one major incident with many affected users |
| T-04 | **SLA clock accuracy** | SLA clocks respect working calendars from M30 and holiday sets from M65, pause on customer-awaited status, and are auditable |
| T-05 | **CMDB discovery over declaration** | Configuration items are populated by discovery where technically possible; manually declared items carry a review date and decay to unverified |
| T-06 | **Service mapping depth limit** | Service mapping is limited to two relationship levels. Deeper modelling is not maintained and therefore not trusted |
| T-07 | **Asset–employee integrity** | An asset allocation requires an active employee; a leaver event with an outstanding allocation raises a blocking recovery task |
| T-08 | **Wipe-before-disposal gate** | An asset cannot move to disposal without an M06 destruction record. Enforced, not procedural |
| T-09 | **Licence reconciliation** | Entitlement and installation reconciliation runs on a schedule and produces a compliance position with a variance explanation per product |
| T-10 | **Change–incident correlation window** | Incidents within a configurable window after a change on the same configuration item are automatically proposed as change-caused, for confirmation |
| T-11 | **Freeze enforcement** | Change implementation during an M30-declared freeze is blocked, with only the emergency path available |
| T-12 | **Bilingual employee surface** | The self-service portal, catalogue, knowledge base and notifications are complete in Bengali and English (AS-12). Branch staff will not use an English-only helpdesk |
| T-13 | **Scale envelope** | 500–1,000 employees; ~8,000 tickets per year; ~2,500 IT assets; ~60 software products; ~1,200 configuration items at Wave 8 |
| T-14 | **Mobile-first access** | Branch staff and technicians raise tickets from a phone on a 3G connection; the portal meets the NFR-081 400 KB first-load budget |
| T-15 | **No security judgement** | M66 runs the process around a security incident; the classification, breach assessment and notification decision remain M29's and M60's |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M66 |
|---|---|---|
| **Branch staff** | Messages someone in IT and hopes; no idea whether it was seen | Raises a ticket from their phone in Bengali, sees its status and its target time |
| **Technician** | A broken scanner stops the branch and nobody records it | Logged, prioritised by impact, escalated automatically if it is not fixed |
| **IT administrator** | Interrupt-driven; the same fault fixed repeatedly without noticing | A prioritised queue, and a problem record when a fault recurs |
| **CTO** | Cannot say what internal IT spends its time on, or what it costs | Ticket volume, SLA attainment, recurring problems, asset position and IT cost by branch |
| **HR** | A leaver's laptop is chased by email | Recovery is a workflow, and final settlement is blocked while an asset is outstanding |
| **Finance** | IT spend is a line in a budget | Asset register, licence position and IT cost by cost centre |
| **Branch manager** | Does not know whether their IT issue is being worked on | Sees their branch's open tickets and their targets |
| **New employee** | Waits days for a laptop and accounts, chasing each separately | One onboarding workflow: assets allocated, access requested, ready on day one |
| **Auditor** | No evidence of change control over the platform | Every change assessed, approved, implemented and reviewed |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Employee productivity recovery** | Faster restoration through prioritisation, tiering and knowledge-based first-line resolution | At 500–1,000 employees, even 30 minutes of IT downtime per person per month is thousands of productive hours a year. **> 92% within SLA** converts an unmeasured loss into a managed one |
| **Recurring fault elimination** | Problem management removes causes rather than repeating fixes | The compounding benefit: each permanent fix removes all its future incidents |
| **Asset loss prevention** | Leaver-driven recovery with settlement blocking | **100% of company IT assets tracked**, against manual today. Each unrecovered laptop is a capital loss *and* a data-protection exposure |
| **PDPA exposure reduction** | Wipe-before-disposal enforced through M06; asset location and custody known | An untracked device holding customer data is a **BDT 25 lakh** class of exposure under the PDPA. This is the highest-value risk M66 addresses |
| **Licence cost reduction** | Unused and under-used licences identified and reallocated; renewals managed rather than auto-renewed | Typical SAM programmes recover 10–25% of software spend in the first year, and prevent the audit-penalty exposure of unlicensed installation |
| **Change-caused incident reduction** | Risk assessment, collision detection, back-out plans and post-implementation review | A 67-module estate deployed weekly will cause incidents; measuring and reviewing them is how the rate falls |
| **Onboarding speed** | Automated asset allocation and access request on the joiner event | A new branch agent productive on day one rather than day three — material in a business with high turnover and continuing branch expansion |
| **IT cost transparency** | Consumption by branch and cost centre | Turns IT from an unallocated overhead into a managed cost, supporting M54 |
| **Credibility** | The Company runs its own service desk on its own platform | Removes an obvious and awkward question from client conversations and tenders — the explicit category risk |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **The Company uses its own product** | The stated category mitigation. The internal team experiences the service-desk pattern before selling it, and finds its weaknesses first |
| **ISO 27001 alignment** | Asset management, change control and incident management are explicit Annex A control areas |
| **ISO 9001 evidence** | Documented, measured, reviewed processes with corrective action |
| **Employee experience** | Being able to report a broken laptop and see it acknowledged is a small thing that shapes how staff feel about the whole system |
| **Institutional memory** | Known errors and workarounds captured rather than held by whoever solved it last time |
| **Change discipline** | A platform changed weekly by a growing team needs assessed, approved, reviewed change — and the discipline transfers to how the business thinks about risk |
| **Foundation for M05 credibility** | An MSP that runs its own IT well has a reference; one that does not has a liability |

---

## 8. Lifecycle & State Models

### 8.1 Incident Lifecycle

```
   Channels: self-service · email · phone ·
             **automatic from M28 integration failure, M30 alert, M29 security event**
        │
   ┌────▼─────┐
   │  LOGGED  │  category · affected service · affected user · configuration item
   └────┬─────┘
        │ impact × urgency → priority (FR-ITS-007)
        │ de-duplicated and correlated (T-03)
   ┌────▼──────────┐
   │ PRIORITISED   │──► major impact ──► **MAJOR INCIDENT**
   └────┬──────────┘                      named incident manager ·
        │                                 communication cadence via M27 ·
        │                                 mandatory post-incident review
   ┌────▼──────────┐
   │  ASSIGNED     │  tier 1 / 2 / 3 by category and skill
   └────┬──────────┘
        │
   ┌────▼──────────┐        ┌──────────────────┐
   │ IN PROGRESS   │───────►│ AWAITING USER    │ SLA clock paused (T-04)
   └────┬──────────┘◄───────└──────────────────┘
        │
        ├──► SLA threshold reached ──► **ESCALATED** (automatic, FR-ITS-008)
        │
        ├──► known error found ──► workaround applied from the knowledge base
        │
   ┌────▼──────────┐
   │   RESOLVED    │  service restored; resolution recorded
   └────┬──────────┘
        │ user confirms restoration; satisfaction captured
   ┌────▼──────────┐
   │    CLOSED     │
   └────┬──────────┘
        │
        │ **cause not removed**
   ┌────▼──────────────────────────┐
   │ PROBLEM REMAINS OPEN          │ ──► §8.2
   │ (an incident closes on        │
   │  restoration; a problem       │
   │  closes on cause removal)     │
   └───────────────────────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Logged | Raised by a user or created automatically from a platform signal | Employee / system |
| Logged | Prioritised | Impact and urgency assessed; de-duplicated against open incidents | System / service desk |
| Prioritised | Major incident | Impact meets the major threshold | Service desk / CTO |
| Prioritised | Assigned | Tier and assignee determined by category and skill | System |
| Assigned | In progress | Assignee accepts | IT staff |
| In progress | Awaiting user | Information or action required from the affected user — **SLA clock pauses** | IT staff |
| Any | Escalated | SLA threshold reached — automatic | System |
| In progress | Resolved | Service restored; resolution recorded | IT staff |
| Resolved | Closed | User confirms; satisfaction captured; auto-closes after a defined period | User / system |
| Closed | (problem opens) | Root cause not removed; recurrence threshold met | System / problem manager |

### 8.2 Problem Lifecycle

```
   Reactive: recurring incidents above threshold (FR-ITS-013)
   Proactive: trend, capacity, error rate, asset age (FR-ITS-014)
        │
   ┌────▼──────────┐
   │  IDENTIFIED   │  incidents linked; impact quantified
   └────┬──────────┘
        │
   ┌────▼──────────┐
   │ INVESTIGATING │  root cause analysis with evidence
   └────┬──────────┘
        │ cause found
   ┌────▼──────────────┐
   │   KNOWN ERROR     │ ──► **workaround published to the knowledge base**
   └────┬──────────────┘      first line can now restore service immediately
        │ permanent fix designed
   ┌────▼──────────────┐
   │ FIX IN CHANGE     │ ──► §8.3 change process
   └────┬──────────────┘
        │ change implemented
   ┌────▼──────────────┐
   │ VERIFYING         │  recurrence monitored over a defined period
   └────┬──────────┬───┘
        │          │ recurrence continues
        │          └──► returns to INVESTIGATING
        │ recurrence stopped
   ┌────▼──────────┐
   │    CLOSED     │  effectiveness verified; known error retired
   └───────────────┘
```

### 8.3 Change Lifecycle

```
                     ┌──────────────────────────────────────┐
   STANDARD ────────►│ pre-approved · scheduled · implemented│──► REVIEWED
   (low risk,        │ (no per-instance approval)            │
    pre-assessed)    └──────────────────────────────────────┘

   NORMAL
   ┌──────────┐
   │ REQUESTED│ description · justification · affected CIs ·
   └────┬─────┘ implementation · test · **back-out plan**
        │
   ┌────▼──────────────┐
   │ RISK ASSESSED     │ from CIs and service mapping (FR-ITS-019)
   └────┬──────────────┘
        │ approval routed **by risk**, not by fixed hierarchy
   ┌────▼──────────┐        ┌───────────┐
   │  APPROVED     │◄──────►│ REJECTED  │
   └────┬──────────┘        └───────────┘
        │ calendar slot; **collision check**; freeze check (M30)
        │  ✖ freeze active ──► BLOCKED (emergency path only)
   ┌────▼──────────┐
   │  SCHEDULED    │
   └────┬──────────┘
        │
   ┌────▼──────────┐
   │ IMPLEMENTING  │
   └────┬──────┬───┘
        │      │ failure
        │  ┌───▼──────────┐
        │  │ BACKED OUT   │ ──► mandatory review
        │  └──────────────┘
        │ verified against the test plan
   ┌────▼──────────┐
   │  IMPLEMENTED  │
   └────┬──────────┘
        │ incidents within the correlation window checked (T-10)
   ┌────▼──────────┐
   │   REVIEWED    │ mandatory for emergency, failed and major changes
   └───────────────┘

   EMERGENCY ──► implemented first · post-implementation approval ·
                 **mandatory review** (FR-ITS-021)
```

### 8.4 IT Asset Lifecycle

```
   REQUESTED ──► approved ──► **PROCURED (via M16)** ──► RECEIVED
       │                                                    │
       │                                              built and configured
       │                                                    ▼
       │                                              ┌───────────┐
       │                                              │ AVAILABLE │
       │                                              └─────┬─────┘
       │                                                    │ allocated;
       │                                                    │ employee accepts
       │                                              ┌─────▼─────┐
       │                                              │ ALLOCATED │◄──┐
       │                                              └──┬──┬──┬──┘   │
       │                                    transfer ────┘  │  │      │
       │                                                    │  │ fault│
       │                                          ┌─────────▼┐ │      │
       │                                          │ IN REPAIR│─┼──────┘
       │                                          └──────────┘ │
       │                                                       │
       │                    **employee.left from M21** ─────────┤
       │                                                       ▼
       │                                              ┌────────────────┐
       │                                              │ RECOVERY DUE   │
       │                                              │ **blocks final │
       │                                              │  settlement**  │
       │                                              └────────┬───────┘
       │                                                       │ returned
       │                                              ┌────────▼───────┐
       │                                              │   RECOVERED    │
       │                                              └────┬──────┬────┘
       │                                    reallocated ───┘      │ end of life
       │                                                          ▼
       │                                              ┌──────────────────────┐
       │                                              │ **DATA DESTRUCTION** │
       │                                              │ via M06 — mandatory  │
       │                                              │ gate (T-08)          │
       │                                              └──────────┬───────────┘
       │                                                         │ certificate issued
       │                                              ┌──────────▼───────────┐
       │                                              │ DISPOSED via M18     │
       │                                              │ e-waste compliance   │
       │                                              └──────────────────────┘
```

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-ITS-01 | **Internal IT tickets never enter M05; client tickets never enter M66.** The two share no ticket data | **H** | CTO |
| BRU-ITS-02 | Every internal IT request and incident is recorded; support provided outside the system is a process failure | **H** | CTO |
| BRU-ITS-03 | An incident closes when service is restored; **the problem stays open until the cause is removed** | **C** | CTO |
| BRU-ITS-04 | Recurring incidents above the configured threshold automatically raise a problem record | **C** | CTO |
| BRU-ITS-05 | A problem closes only on verified absence of recurrence over the defined period | **H** | CTO |
| BRU-ITS-06 | Every change carries an implementation plan, a test plan and a **back-out plan**; a change without one cannot be approved | **H** | CTO |
| BRU-ITS-07 | Change approval is routed by assessed risk, not by a fixed hierarchy | **C** | CTO |
| BRU-ITS-08 | A change cannot be implemented during an M30-declared freeze except through the emergency path | **H** | CTO |
| BRU-ITS-09 | Colliding changes on the same configuration item cannot both be scheduled in the same window | **H** | CTO |
| BRU-ITS-10 | Every emergency change, failed change and major change receives a post-implementation review | **H** | CTO |
| BRU-ITS-11 | Every company IT asset is registered before it is allocated | **H** | CTO |
| BRU-ITS-12 | An asset allocation requires an active employee and their recorded acceptance | **H** | CTO |
| BRU-ITS-13 | **A leaver with an outstanding asset blocks final settlement until recovery or written-off approval** | **H** | HR Director / CFO |
| BRU-ITS-14 | **An asset cannot be disposed of without an M06 data destruction certificate** | **H** | CTO / Quality Manager |
| BRU-ITS-15 | Asset disposal occurs only through M18's certified e-waste route | **H** | Quality Manager |
| BRU-ITS-16 | Software may only be installed from an approved catalogue entry with an available entitlement | **H** | CTO |
| BRU-ITS-17 | Installations exceeding entitlements are a compliance exception requiring remediation or purchase within a defined period | **H** | CTO / CFO |
| BRU-ITS-18 | A configuration item declared manually carries a review date and decays to unverified if not reviewed | **C** | CTO |
| BRU-ITS-19 | SLA clocks respect working calendars and holidays and pause while awaiting the user | **C** | CTO |
| BRU-ITS-20 | A major incident requires a named incident manager and a communication cadence to affected users | **H** | CTO |
| BRU-ITS-21 | **M66 makes no security classification decision**; breach assessment and notification remain M29's and M60's | **H** | CTO |
| BRU-ITS-22 | The self-service portal and knowledge base are complete in Bengali and English | **H** | CTO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.it.service` | `fix_it_service` | The IT service catalogue | code, name_bn, name_en, description, category, eligibility, approval_required, cost_threshold, fulfilment_steps, target_response, target_resolution, owner_user_id, active |
| `fix.it.ticket` | `fix_it_ticket` | **The internal ticket** (request or incident) | number, type (request/incident), service_id, category, subject, description, raised_by, raised_via (portal/email/phone/auto), affected_user_id, branch_id, ci_id, impact, urgency, priority, tier, assigned_to, state, sla_id, response_due, resolution_due, resolved_at, closed_at, satisfaction, parent_ticket_id, problem_id, caused_by_change_id |
| `fix.it.ticket.activity` | `fix_it_ticket_activity` | Work log and communication | ticket_id, actor_id, activity_type, note, visible_to_user, occurred_at, time_spent_min, clock_paused |
| `fix.it.sla` | `fix_it_sla` | Internal SLA definition | service_id, priority, response_minutes, resolution_minutes, working_calendar_id, pause_on_awaiting_user, warning_thresholds |
| `fix.it.sla.measurement` | `fix_it_sla_measurement` | Attainment record | ticket_id, sla_id, response_due, responded_at, resolution_due, resolved_at, response_met, resolution_met, paused_minutes, breach_reason |
| `fix.it.major.incident` | `fix_it_major_incident` | Major incident handling | ticket_id, declared_at, declared_by, incident_manager_id, affected_scope, communication_log, restored_at, review_ref, closed_at |
| `fix.it.problem` | `fix_it_problem` | **Problem record** | number, title, origin (reactive/proactive), linked_ticket_ids, incident_count, impact_estimate, state, investigator_id, root_cause, evidence_ref, known_error_id, fix_change_id, verification_period, verified_at, closed_at |
| `fix.it.known.error` | `fix_it_known_error` | Workaround before permanent fix | problem_id, symptom, workaround_bn, workaround_en, affected_cis, published_at, retired_at, use_count |
| `fix.it.change` | `fix_it_change` | **Change record** | number, title, type (standard/normal/emergency), justification, affected_ci_ids, implementation_plan, test_plan, **back_out_plan**, risk_score, risk_factors, state, requested_by, approvers, scheduled_from, scheduled_to, implemented_at, verified, backed_out, review_ref, m30_config_change_ref |
| `fix.it.change.calendar` | `fix_it_change_calendar` | Forward schedule and collisions | change_id, window_from, window_to, affected_cis, collision_with_change_ids, freeze_conflict, approved_slot |
| `fix.it.review` | `fix_it_review` | Post-implementation and post-incident review | subject_type (change/major_incident), subject_id, held_at, participants, findings, actions, problem_raised_id, capa_ref |
| `fix.it.asset` | `fix_it_asset` | **Company IT asset register** | asset_tag, type (laptop/desktop/phone/tablet/scanner/printer/network/server), make, model, serial, specification, purchase_po_ref, purchase_date, cost, warranty_until, supplier_id, branch_id, cost_center_id, state, allocated_to_user_id, allocated_at, accepted_at, ci_id, fixed_asset_ref |
| `fix.it.asset.movement` | `fix_it_asset_movement` | Allocation, transfer and recovery | asset_id, movement_type (allocate/transfer/repair/recover/dispose), from_user_id, to_user_id, from_branch_id, to_branch_id, occurred_at, actor_id, acceptance_ref, condition_note |
| `fix.it.asset.recovery` | `fix_it_asset_recovery` | Leaver recovery control | asset_id, employee_id, leaver_event_at, due_by, state, recovered_at, condition, **destruction_certificate_ref**, write_off_approved_by, blocks_settlement |
| `fix.software.product` | `fix_software_product` | Software catalogue | name, vendor, version, licence_model (per-user/per-device/subscription/perpetual), approved, request_path, security_reviewed_at, owner_user_id |
| `fix.software.entitlement` | `fix_software_entitlement` | What is owned | product_id, quantity, purchase_ref, cost, start_date, end_date, renewal_date, auto_renew, contract_ref, cost_center_id |
| `fix.software.installation` | `fix_software_installation` | What is deployed | product_id, asset_id, user_id, installed_at, last_used_at, discovered, authorised, removal_requested_at |
| `fix.software.compliance` | `fix_software_compliance` | Reconciled position | product_id, period, entitled, installed, in_use, variance, compliance_state, unused_count, reclaim_value, reconciled_at |
| `fix.cmdb.item` | `fix_cmdb_item` | **Configuration item** | code, name, type (application/server/database/network/service/device/integration), owner_user_id, environment, criticality, source (discovered/declared), last_verified_at, verified_state, asset_id, m30_object_ref |
| `fix.cmdb.relationship` | `fix_cmdb_relationship` | CI relationships (two levels max) | from_ci_id, to_ci_id, relationship_type (depends_on/runs_on/connects_to/supports), discovered, verified_at |
| `fix.it.knowledge` | `fix_it_knowledge` | Internal IT knowledge base | title_bn, title_en, body_bn, body_en, category, related_cis, related_known_error_id, author_id, reviewed_at, view_count, deflection_count, published |
| `fix.it.vendor.contract` | `fix_it_vendor_contract` | IT support contracts | vendor_party_id, service, contract_ref, start, end, renewal_notice_days, support_sla, annual_cost, owner_user_id |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.employee`, **`employee.joined` / `employee.left`** | **M21** | Events — the asset control point |
| `fix.identity`, access requests | **M29** | M66 raises access requests; M29 decides and grants |
| `fix.security.incident`, security events | **M29** | **M29 classifies; M66 runs the process** |
| `fix.platform.alert`, `fix.job.run`, `fix.change.freeze`, `fix.config.version` | **M30** / **M63** | Alerts and job failures create incidents; freezes block changes |
| `fix.integration.health`, dead letters | **M28** | Integration failures create incidents |
| `fix.working.calendar` | M30 / M63 | SLA clock |
| Holiday sets | M65 | SLA clock |
| `fix.purchase.requisition`, `fix.purchase.order` | **M16** | Asset and software procurement |
| `fix.destruction.certificate` | **M06** | **Mandatory gate before disposal** |
| `fix.recycling.batch` | **M18** | Certified disposal route |
| `fix.asset` (fixed asset accounting) | M17 / M49 | Cost and depreciation linkage |
| `fix.cost.center`, `fix.branch` | M30 / M54 | Cost attribution |
| `fix.nonconformance`, CAPA | M23 | Quality signals from reviews |
| Notification channels | M27 | Major incident communication |
| `fix.document` | M24 | Attachments and evidence |
| `fix.knowledge.article` (technical repair) | M61 | Boundary reference — M66 covers internal IT only |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-ITS-01 | Employee raises a request or incident | Categorise, prioritise by impact and urgency, apply the SLA, assign to the correct tier, acknowledge to the user | Route to the service-desk queue unassigned; alert |
| AUT-ITS-02 | **M30 alert, M28 integration failure, or M29 security event** | Create an incident automatically with the source, configuration item and severity; **de-duplicate against open incidents** | Create individually; alert on duplicate storm |
| AUT-ITS-03 | Multiple incidents share a configuration item and symptom within the window | Correlate to a parent incident; propose major-incident declaration if scope warrants | Handle individually |
| AUT-ITS-04 | Major incident declared | Assign an incident manager, open the communication cadence through M27, notify affected users and management, schedule the review | Escalate to CTO |
| AUT-ITS-05 | SLA warning threshold reached | Notify the assignee and their supervisor; escalate a tier at breach | Escalate further |
| AUT-ITS-06 | Incident resolved | Notify the user, request confirmation and satisfaction, auto-close after the defined period | Remain resolved; remind |
| AUT-ITS-07 | Incidents recur above the threshold for the same symptom and configuration item | **Raise a problem record automatically** with the linked incidents and quantified impact | Report on the recurrence dashboard |
| AUT-ITS-08 | Trend, capacity, error rate or asset age signals a likely failure | Raise a **proactive** problem candidate for investigation | Report only |
| AUT-ITS-09 | Known error published | Surface the workaround to first line and in the self-service knowledge base for the matching symptom | Publish without linkage |
| AUT-ITS-10 | Problem's fix change implemented | Monitor recurrence over the verification period; close on verified absence, reopen on recurrence | Hold in verifying |
| AUT-ITS-11 | Change requested | Assess risk from affected configuration items and service mapping; route approval by risk; check the calendar for collisions and freezes | Route to CTO for manual assessment |
| AUT-ITS-12 | Change scheduled in a declared freeze window | **Block**; offer only the emergency path | Hard block |
| AUT-ITS-13 | Colliding change detected on the same configuration item | Block the second scheduling; notify both change owners | Hard block |
| AUT-ITS-14 | Change implemented | Verify against the test plan; on failure trigger the back-out plan and open a review | Escalate; force back-out decision |
| AUT-ITS-15 | Incident raised within the correlation window after a change on the same configuration item | Propose it as change-caused for confirmation; feed the change-caused incident rate | Report only |
| AUT-ITS-16 | Emergency, failed or major change completes | Schedule the mandatory post-implementation review; raise a problem where a pattern emerges | Escalate the overdue review |
| AUT-ITS-17 | **`employee.joined` from M21** | Allocate the standard asset set for the role, raise access requests to M29, create the onboarding checklist, target readiness by day one | Alert the IT administrator and the line manager |
| AUT-ITS-18 | **`employee.left` from M21** | Create recovery tasks for every allocated asset, set the due date, **flag final settlement as blocked**, notify HR and the line manager | Escalate to HR Director and CTO |
| AUT-ITS-19 | Asset recovered at leaver | Verify condition, route to M06 for data destruction, then reallocate or retire | Hold in recovered; alert |
| AUT-ITS-20 | Asset disposal requested | **Verify the M06 destruction certificate exists**; block without it; route to M18 for certified disposal | **Hard block**; alert Quality Manager |
| AUT-ITS-21 | Scheduled (monthly) | Reconcile software entitlements against installations; produce the compliance position; identify unused and under-used licences | Report last known position; alert |
| AUT-ITS-22 | Installations exceed entitlements | Raise a compliance exception with a remediation deadline; notify CTO and CFO | Escalate |
| AUT-ITS-23 | Unauthorised software discovered | Raise an incident, notify the user with the governed request path, and flag for removal | Report on the shadow-IT dashboard |
| AUT-ITS-24 | Software subscription or support contract approaching renewal | Notify the owner at the configured lead time with usage data to inform the decision | Escalate at expiry |
| AUT-ITS-25 | Scheduled (weekly) | Run CMDB discovery; update items and relationships; mark unverified declared items past their review date | Retain the previous state; alert |
| AUT-ITS-26 | Knowledge article resolves a self-service search | Record the deflection; report the deflection rate | — |

---

## 12. Interfaces

### 12.1 Upstream — M66 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M21 Core HR** | **`employee.joined` and `employee.left`** — the onboarding and asset-recovery triggers | Events |
| **M30 Platform Admin** | Platform alerts, job failures, change freezes, configuration change records, working calendars | Events + REST |
| **M28 Integration** | Integration failures, dead letters, webhook endpoint disablement | Events |
| **M29 Identity** | Security incidents and events; access request outcomes | Events + REST |
| **M16 Procurement** | Asset and software purchase orders and receipts | Events |
| **M06 Data Services** | **Data destruction certificates — the disposal gate** | REST |
| **M18 E-Waste** | Certified disposal batches and certificates | Events |
| M65 Localisation | Holiday sets for SLA clocks; Bengali translations | REST |
| M49 Fixed Assets | Capitalisation and depreciation linkage | REST |
| M27 Contact Centre | Notification channels for major incident communication | Command |
| Discovery agents / network scanning | CMDB and software installation data | Connector (M28) |

### 12.2 Downstream — M66 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **All employees** | Self-service portal, service catalogue, ticket status, knowledge base | REST / P03 |
| **M29 Identity** | Access requests raised by onboarding and offboarding workflows | Commands |
| **M30 Platform Admin** | Change records that configuration changes reference; incident outcomes | REST + events |
| **M21 Core HR** | **Asset recovery status blocking final settlement**; onboarding readiness | Events |
| **M06 Data Services** | Devices requiring data destruction before disposal | Commands |
| **M18 E-Waste** | Retired IT assets entering the certified disposal route | Commands |
| M16 Procurement | Asset and software purchase requirements | Commands |
| M49 Fixed Assets | Asset acquisition, transfer and disposal events | Events |
| M23 Quality | Review findings and recurring problems as quality signals | Events |
| M60 GRC | Change control and asset management evidence; licence compliance position | Events |
| M54 FP&A | IT cost consumption by branch and cost centre | Warehouse extract |
| M25 BI | Service performance, asset and licence facts | Warehouse extract |
| M61 Knowledge | Boundary reference; no content flows | — |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `it.ticket_raised` | ticket, type, service, priority, affected user, branch | M25 |
| `it.sla_breached` | ticket, SLA, breach minutes, assignee | CTO, supervisor |
| `it.major_incident_declared` | incident, scope, manager, affected users | **M27**, CTO, management |
| `it.major_incident_resolved` | incident, duration, cause, review scheduled | M23, M60 |
| `it.problem_raised` | problem, linked incidents, impact estimate, origin | CTO, M23 |
| `it.known_error_published` | problem, symptom, workaround | service desk, knowledge base |
| `it.problem_closed` | problem, root cause, fix, verification result | M23, M60 |
| `it.change_approved` | change, type, risk, window, affected CIs | **M30**, affected teams |
| `it.change_implemented` | change, verified, backed out, incidents correlated | M30, M60 |
| `it.change_caused_incident` | change, incident, correlation basis | CTO, M23 |
| `it.asset_registered` | asset, type, serial, cost, cost centre | **M49**, M54 |
| `it.asset_allocated` | asset, employee, branch, accepted at | M21, M49 |
| `it.asset_recovery_due` | asset, leaver, due by, **settlement blocked** | **M21**, HR, CFO |
| `it.asset_recovered` | asset, condition, destruction required | M06 |
| `it.asset_disposed` | asset, destruction certificate, disposal batch | **M18**, M49, M60 |
| `it.software_compliance_exception` | product, entitled, installed, variance, deadline | **CTO, CFO**, M60 |
| `it.unauthorised_software_detected` | product, asset, user | M29, CTO |
| `it.licence_renewal_due` | product, contract, renewal date, usage, cost | CTO, CFO, M16 |
| `it.ci_unverified` | configuration item, last verified, owner | CTO |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-ITS-01 | Endpoint discovery and inventory agent | Inbound | CMDB population and software installation discovery |
| INT-ITS-02 | Network discovery / SNMP scanning | Inbound | Network device and topology discovery |
| INT-ITS-03 | Email ingestion | Inbound | Ticket creation from employee email |
| INT-ITS-04 | Microsoft 365 / Google Workspace admin | Bidirectional | Mailbox, licence and account state for software asset management |
| INT-ITS-05 | IT vendor support portals | Outbound | Warranty and support case escalation for hardware faults |
| INT-ITS-06 | Mobile device management *(optional, W8)* | Bidirectional | Company phone and tablet inventory, compliance and remote wipe |

> **Note.** M66 uses **no client-facing RMM tooling**. The monitoring agents in `05-03` §2.4
> (INT-028…INT-033) belong to **M05** and serve paying clients. Sharing them would breach the
> M66/M05 boundary and place internal telemetry inside a client-audited system.

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/it/catalogue` | GET | The IT service catalogue | Employee portal |
| `/api/v1/it/tickets` | GET/POST | Raise and track a request or incident | **All employees**, P03 |
| `/api/v1/it/tickets/{id}` | GET/PATCH | Ticket detail, work log, status | Employee, IT staff |
| `/api/v1/it/tickets/{id}/escalate` | POST | Escalate a tier | IT staff |
| `/api/v1/it/tickets/auto` | POST | **Create an incident from a platform signal** | **M28, M29, M30** |
| `/api/v1/it/major-incidents` | GET/POST | Declare and manage a major incident | P03, CTO |
| `/api/v1/it/problems` | GET/POST | Problem record and root cause | P03 |
| `/api/v1/it/known-errors` | GET | Workarounds for first line and self-service | Employee portal, IT staff |
| `/api/v1/it/changes` | GET/POST | Raise a change with plans | P03, module teams |
| `/api/v1/it/changes/{id}/assess` | POST | Risk and impact assessment | P03 |
| `/api/v1/it/changes/{id}/approve` | POST | Approve by risk-routed authority | P03 |
| `/api/v1/it/change-calendar` | GET | Forward schedule, collisions, freezes | P03, module teams |
| `/api/v1/it/assets` | GET/POST | IT asset register | P03, M49 |
| `/api/v1/it/assets/{id}/allocate` | POST | Allocate with employee acceptance | P03 |
| `/api/v1/it/assets/{id}/recover` | POST | Record leaver recovery | P03, HR |
| `/api/v1/it/assets/recovery-status/{employee}` | GET | **Outstanding assets blocking settlement** | **M21**, HR, Finance |
| `/api/v1/it/software/compliance` | GET | Entitlement versus installation position | P03, CTO, CFO |
| `/api/v1/it/software/request` | POST | Governed software request | Employee portal |
| `/api/v1/it/cmdb/items` | GET | Configuration items and relationships | P03, M30, module teams |
| `/api/v1/it/cmdb/impact/{ci}` | GET | **What breaks if this fails** | P03, change assessment |
| `/api/v1/it/knowledge` | GET | Knowledge base search with deflection tracking | Employee portal |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R02 Chief Technology Officer | C R U D A | All; approves high-risk changes, licence exceptions and asset write-offs |
| R33 IT / System Administrator | C R U D A | All operational functions: tickets, changes, assets, software, CMDB |
| **IT Service Desk agent** *(a grant on R33 — see the note below)* | C R U | Ticket handling, tier 1 resolution, asset allocation |
| R30 HR Manager | R U | Onboarding and offboarding workflows; **asset recovery status blocking settlement** |
| R31 HR Officer | R | Onboarding readiness for their scope |
| R03 Chief Financial Officer | R A | IT asset value, licence compliance and cost; approves asset write-offs above threshold |
| R26 Finance Manager | R | IT cost by cost centre; asset register for M49 reconciliation |
| R32 Quality Manager / ISO Coordinator | R | Reviews, recurring problems, disposal compliance as ISO evidence |
| R06 Branch Manager | R | **Own branch's** open tickets, allocated assets and outstanding recoveries |
| R05 Operations Director | R | Service performance and branch IT availability |
| **All employees** | C R | **Raise a ticket; track their own tickets; search knowledge; view their own allocated assets** |

> **Role gap — audit action.** `05-04` §1 has **no IT Service Desk agent role**. M66 currently
> models it as a grant on R33 IT / System Administrator, which conflates a first-line agent with
> a full system administrator and weakens least privilege. Whether a distinct role is required is
> an open question (Q-06) and an audit action against `05-04` — the third such gap recorded, after
> Demand Planner (Category E) and Data Steward (M64).

**Field-level restrictions.** Asset cost and licence cost are visible to R02, R03, R26 and R33
only. Ticket content may contain personal or security-sensitive information; **security incident
detail is masked** to all but R02, R33 and R32, with M29 holding the authoritative record.

**Segregation of duties.**
- The requester of a change cannot be its sole approver for normal or high-risk changes.
- The implementer of a change cannot be the sole verifier of its success.
- Asset write-off requires an approver distinct from the person recording the loss.
- A software compliance exception cannot be closed by the person who created the installation.
- M66 staff cannot grant access — they raise the request; **M29 decides** (SOD-09 protected).

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **IT service desk board** | IT Administrator, CTO | Real time | Open tickets by priority, tier, age and SLA state; queue depth; breach risk |
| **SLA attainment** | CTO, Operations Director | Monthly | Response and resolution attainment by service, priority and branch — **against > 92%** |
| Ticket volume and trend | CTO | Monthly | Volume by category, service, branch and channel; seasonality; growth against headcount |
| **Recurring incident and problem register** | CTO, Quality Manager | Monthly | Problems open, root causes found, known errors published, incidents eliminated by permanent fix |
| Major incident review | CTO, CEO, Quality Manager | Per incident | Timeline, impact, cause, actions, recurrence prevention |
| **Change performance** | CTO, Quality Manager, Internal Audit | Monthly | Changes by type, success rate, back-outs, emergency share, **change-caused incident rate** |
| Change calendar | CTO, all module teams | Real time | Forward schedule, collisions, freeze periods |
| **IT asset register and coverage** | CTO, CFO, Finance Manager | Monthly | Every asset by type, state, location, allocation — **against 100% tracked** |
| **Leaver asset recovery** | HR Director, CTO, CFO | Weekly | Outstanding recoveries by leaver, age, value, settlement blocks |
| **Software licence compliance** | CTO, CFO, Internal Audit | Monthly | Entitled versus installed versus in use; exceptions; **reclaimable unused licences and their value** |
| Renewal calendar | CTO, CFO, Procurement | Monthly | Subscriptions and support contracts due, with usage data to inform renewal |
| Shadow IT | CTO, M29 | Monthly | Unauthorised software detected, users, remediation status |
| **CMDB health** | CTO, IT Administrator | Monthly | Items discovered versus declared, unverified items, service mapping coverage |
| Knowledge and deflection | CTO | Monthly | Articles published, views, self-service deflection rate |
| **IT cost by branch and cost centre** | CFO, Finance Manager, branch managers | Monthly | Asset, licence, support and consumable cost attributed |
| Employee IT satisfaction | CTO, HR Director | Quarterly | Satisfaction by service and branch; drivers of dissatisfaction |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W7 Target | W8+ Target |
|---|---|---|---|---|
| — | **Internal IT tickets resolved within SLA** | unmeasured | 88% | **> 92%** |
| — | **Company IT assets tracked** | manual | 98% | **100%** |
| — | Internal IT support handled outside the system | ~100% | < 10% | **< 2%** |
| — | Leaver assets recovered within the due period | unknown | 92% | **98%** |
| — | Assets disposed without a data destruction certificate | unknown | **Zero** | **Zero** |
| — | Software licence compliance position | unknown | Compliant | **Compliant** |
| — | Unused licences identified and reclaimed | 0% | tracked | **> 85% of identified** |
| — | Recurring incidents converted to problem records | 0% | 80% | **95%** |
| — | Incidents eliminated by permanent fix *(problem effectiveness)* | n/a | tracked | **rising trend** |
| — | Change success rate (no back-out, no caused incident) | unmeasured | 92% | **97%** |
| — | Emergency changes as a share of all changes | unmeasured | < 15% | **< 8%** |
| — | Post-implementation reviews completed for emergency, failed and major changes | 0% | **100%** | **100%** |
| — | Self-service deflection rate | 0% | 25% | **40%** |
| — | New employee IT-ready on day one | unmeasured | 85% | **97%** |
| — | CMDB items verified within their review period | n/a | 90% | **97%** |
| — | Employee IT satisfaction | unmeasured | 3.8/5 | **4.3/5** |

> **Register note.** `_CATEGORY_OVERVIEW.md` §9 names **internal IT tickets resolved within SLA
> (> 92%)** and **company IT assets tracked (100%)** as the category KPIs owned by M66. **Neither
> has a canonical `KPI-0nn` identifier** — `06-02` §2.6 ends at KPI-049. Allocation for all
> sixteen metrics is an audit action.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `base`, `mail` — chatter, activities, portal foundation | 8% |
| L2 | **OCA `helpdesk`** (ticketing and SLA foundation), **OCA `management-system`** (process, review, corrective action), `server-tools` | 34% |
| L5 | `cd_itsm`, `cd_it_asset` | 58% |

> OCA `helpdesk` provides the ticket, SLA and portal substrate already deployed for M01, M05 and
> M27. **M66 uses a separate instance with separate data**, satisfying BRU-ITS-01 while reusing
> the component.

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 2 of 2 identifiers below are claimed by another module: **CD-163** also claimed by M20, M46; **CD-164** also claimed by M46, M52. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-163** | `cd_itsm` — service catalogue, employee self-service portal, incident management with **automatic creation from platform signals**, de-duplication and correlation, major incident handling, internal SLA engine, problem management (reactive and proactive), known errors, **change management with risk-routed approval, calendar, collision detection and back-out**, post-implementation review, knowledge base and deflection | Odoo module + frontend | 9 PW |
| **CD-164** | `cd_it_asset` — IT asset register and lifecycle, **onboarding and offboarding workflows with settlement blocking**, allocation and acceptance, **wipe-before-disposal gate**, software asset management with entitlement reconciliation and unused-licence identification, subscription and renewal management, shadow-IT detection, **CMDB with discovery and service mapping**, vendor contract register, IT cost attribution | Odoo module + service | 5 PW |

> CD-163 and CD-164 are claimed from the extension block for modules M31–M67. **All CD IDs remain
> provisional** pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M29 Identity (W1)** | Employee identity; access requests raised by onboarding; security incidents entering the process |
| **M30 Platform Admin (W1)** | Alerts, job failures, change freezes, working calendars, configuration change records |
| **M28 Integration (W1)** | Integration failure signals; discovery connectors |
| **M21 Core HR (W5)** | **`employee.joined` and `employee.left` — without these the asset control point does not exist.** M66 cannot deliver 100% asset tracking before M21 |
| **M16 Procurement (W3)** | Asset and software purchasing |
| **M06 Data Services (W6)** | **The destruction certificate gate before disposal.** Same wave as M66 — sequence M06's certificate capability ahead of M66's disposal flow |
| **M18 E-Waste (W8)** | Certified disposal route. **Until W8, retired assets are held in a retired-pending-disposal state rather than disposed of** |
| M49 Fixed Assets (W5) | Capitalisation and depreciation linkage |
| M65 Localisation (W9) | Holiday sets for SLA clocks; **until W9 the Bangladesh holiday set is held in M30** |
| M27 Contact Centre (W4) | Major incident communication channels |

> **Why Wave 6 and not earlier.** M66 depends on M21 (W5) for the joiner and leaver events that
> make asset tracking enforceable, and on M06 (W6) for the destruction gate. Delivering M66
> earlier would produce a ticketing system without the asset control that is half its value.
> **The cost of the W6 placement is that internal IT runs on WhatsApp for five waves** — the
> explicit category risk, accepted with eyes open.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| IT asset inventory | ~2,500 assets, **currently manual or absent** | `fix.it.asset` | W6, **physical audit required — see below** |
| Software entitlements | Purchase records and vendor portals | `fix.software.entitlement` | W6, collected |
| Software installations | Discovery | `fix.software.installation` | W6, discovered not migrated |
| Existing tickets | None recorded | — | **Not migrated** |
| Knowledge articles | None exist | `fix.it.knowledge` | W6 onward, authored |
| Configuration items | Discovery plus M30 platform objects | `fix.cmdb.item` | W6, discovered |
| IT vendor contracts | Paper and email | `fix.it.vendor.contract` | W6, collected |
| Service catalogue | Authored | `fix.it.service` | W6, authored |

> **Position — the asset audit is the real work.** There is no reliable IT asset register today.
> Establishing one requires a **physical audit across 51+ branches, the workshop, the warehouse
> and the corporate office**, reconciling every device to an employee and a cost centre. This
> mirrors M15's cutover count in character if not in scale, and it is the precondition for the
> 100% tracking KPI. It is a business commitment, not a software task, and it should be planned
> alongside a branch visit cycle rather than as a standalone exercise.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | M66 and M05 share no ticket data; internal tickets never appear in a client-facing view | Dependency analysis plus negative test on the M05 client portal |
| AC-02 | An employee raises a ticket from a phone on 3G, in Bengali, and tracks it to closure | Field test across three branches |
| AC-03 | An M30 alert, an M28 integration failure and an M29 security event each create an incident automatically | Scripted scenario per source |
| AC-04 | A single outage affecting many users produces one correlated major incident, not many duplicates | Duplicate-storm injection test |
| AC-05 | SLA clocks respect working calendars and holidays and pause while awaiting the user | Time-shifted scenario across a weekend and a public holiday |
| AC-06 | SLA attainment exceeds 92% | Twelve weeks of production measurement |
| AC-07 | Recurring incidents above threshold raise a problem record automatically | Scripted recurrence |
| AC-08 | A problem closes only after verified absence of recurrence over the defined period | Scripted scenario with an induced recurrence |
| AC-09 | A change without a back-out plan cannot be approved | Negative test |
| AC-10 | A change is blocked during an M30-declared freeze, and only the emergency path is available | Negative test |
| AC-11 | Colliding changes on the same configuration item cannot both be scheduled | Negative test |
| AC-12 | Every emergency, failed and major change receives a post-implementation review | Twelve weeks of change records |
| AC-13 | Incidents arising after a change on the same configuration item are correlated and reported | Scripted scenario |
| AC-14 | 100% of company IT assets are registered and reconciled to an employee or a location | Post-audit reconciliation, then twelve weeks of drift measurement |
| AC-15 | **A leaver with an outstanding asset blocks final settlement** | Negative test with M21 |
| AC-16 | **An asset cannot be disposed of without an M06 data destruction certificate** | Negative test |
| AC-17 | Asset disposal routes only through M18's certified e-waste process | Negative test (from W8) |
| AC-18 | A new employee has assets allocated and access requested automatically on the joiner event, and is IT-ready on day one | Ten consecutive joiners measured |
| AC-19 | Software installations reconcile to entitlements monthly, with exceptions raised and unused licences identified | Three monthly reconciliations |
| AC-20 | Unauthorised software is detected and the user directed to the governed request path | Scripted detection |
| AC-21 | The CMDB answers "what breaks if this fails" for every critical business service | Service mapping review |
| AC-22 | The self-service portal, catalogue, knowledge base and notifications are complete in Bengali | Translation coverage report (AS-12) |
| AC-23 | M66 makes no security classification decision; breach assessment remains with M29 | Code review plus process test |
| AC-24 | CTO and HR Director sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 24 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Is the IT asset physical audit approved and resourced?** Without it the 100% tracking KPI is unachievable, and it requires visits to 51+ branches. This is the largest non-software commitment M66 asks for. | CTO / Operations Director | **W6 minus 4 months** |
| Q-02 | **How many IT staff are there, and what is the intended tier structure?** A tiered model with escalation paths requires enough people to have tiers. | CTO / HR Director | W6 design |
| Q-03 | Are internal SLA targets agreed with the business, and what are they per service and priority? An SLA IT sets alone is a target, not an agreement. | CTO / Operations Director | W6 build |
| Q-04 | **What happens between Wave 1 and Wave 6?** Internal IT runs on WhatsApp for five waves while the ERP programme itself generates significant IT demand. Is a lightweight interim measure warranted, or is the risk accepted as stated? | CTO | **W2** |
| Q-05 | Is the change process for **ERP platform changes** the same as for general IT changes, and how does it relate to the CI/CD deployment gates in `02-05` §9? Two change processes would be worse than one. | CTO | W6 design |
| Q-06 | **Is IT Service Desk agent a distinct role in `05-04`**, or a grant on R33? Modelling a first-line agent as a full system administrator weakens least privilege. | HR Director / CTO | W6 design |
| Q-07 | What is the asset write-off policy and threshold when a leaver's device is not recovered? Blocking settlement indefinitely is not viable. | CFO / HR Director | W6 build |
| Q-08 | Is endpoint discovery agent deployment acceptable on employee devices under the PDPA, and what is the lawful basis and notice? | Legal / CTO | W6 build |
| Q-09 | Are company mobile phones in scope for MDM (INT-ITS-06), and is remote wipe of an employee device permissible and notified? | Legal / HR Director / CTO | W8 |
| Q-10 | **Until M18 lands in W8, where do retired IT assets physically go**, and who holds the liability for stored end-of-life devices containing customer data? | Quality Manager / CTO | W6 build |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §2, **§3 (the M66/M05 boundary — six dimensions)**, §6 (boundary map —
not M05, not M45), §9 (category KPIs), §11 (**the WhatsApp risk and "the Company uses its own
product"**) ·
`M30_Platform_Administration_and_Configuration.md` (**alerts, job failures, freezes, configuration
change trail — M30 detects, M66 responds**) ·
`M29_Identity_Access_and_Information_Security.md` (**M29 owns the security judgement; M66 runs
the process**) · `M28_Integration_API_and_Event_Platform.md` (integration failure signals) ·
`M64_Master_Data_Management_and_Configuration.md` (the role-gap precedent) ·
`M65_Multi_Entity_Multi_Country_and_Localisation.md` (holiday sets for SLA clocks) ·
`M05` Remote Support & Managed Services *(Category A — **client-facing, billable, separate**)* ·
`M45` Enterprise Asset & Test Equipment *(Category F — workshop tools, not IT assets)* ·
`M06` Data Services & Secure Data Handling *(Category A — **the destruction gate**)* ·
`M18` E-Waste, Recycling & Circular Economy *(Category D — certified disposal)* ·
`M21` Core HR & Employee Lifecycle *(Category H — **the joiner and leaver events**)* ·
`M61` Knowledge Management & Technical Library *(Category I — technical repair knowledge)* ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §1 (**no IT Service
Desk role — audit action**), §6 SOD-09 ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md`
NFR-003, NFR-062, NFR-063, NFR-066, NFR-071, NFR-072, NFR-081, NFR-086c; OPS-01, OPS-03, OPS-05; AS-12 ·
`05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md` §2.4 (**INT-028…033 belong to M05, not M66**) ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §3 (OCA `helpdesk`, `management-system`), §9 (CI/CD and deployment gates)

**Workspace evidence**
`1000FiX_Services_Company_Profile.md` §Service Infrastructure (51+ branches, corporate office) ·
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` (internal operations requirements)

**External benchmark**
[ServiceNow ITSM — incident, problem, change and request fulfilment as the core process set](https://dss.bg/news/core-itsm-processes-in-servicenow) ·
[ServiceNow ITSM beginner's guide — CMDB integration and cross-process visibility](https://www.jitendrazaa.com/blog/servicenow/servicenow-itsm-complete-beginners-guide-december-2025/) ·
[ITSM best practices — tiered support, escalation paths, workflow automation, knowledge base](https://infobeans.ai/mastering-servicenow-itsm-best-practices/) ·
[ITIL problem management — reactive and proactive](https://www.servicenow.com/community/itsm-articles/itil-problem-management-best-practices/ta-p/2299572) ·
[ITIL 4 change management — risk assessment, approval workflows, standard change templates, logging for compliance](https://pdcaconsulting.com/comprehensive-guide-to-itil-change-management/) ·
[ITIL best practices 2025](https://invgate.com/itsm/itil/itil-best-practices) ·
[Software Asset Management — ITIL definition, compliance, usage transparency, cost control](https://www.matrix42.com/en/software-asset-management-sam) ·
[SAM best practices — live inventory, governed request process, shadow IT prevention](https://www.manageengine.com/products/service-desk/it-asset-management/what-is-software-asset-management.html) ·
[ITAM best practices — policies, roles, automated discovery, regular audits](https://www.device42.com/blog/2023/11/29/the-role-of-it-asset-management-in-ensuring-regulatory-compliance/) ·
[SAM — unused licence identification and reallocation](https://invgate.com/itsm/it-asset-management/software-asset-management) ·
ISO/IEC 27001:2022 Annex A — asset management, change management, incident management

---

*Module M66 · Category K · 1000FiX ERP System v2.0 · CONFIDENTIAL*
