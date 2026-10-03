---
id: FIX-ERP2-P03
portal_id: P03
portal_code: AOP
portal_name: Admin Operations Portal
type: Internal Web Application (role-scoped workspaces)
category: Portal & Application Suite (filed under K — Platform & Technology)
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Operations Director
system_owner: Core Platform Squad
priority: P0
wave: W1
---

# P03 — Admin Operations Portal
### Portal Suite · Code `AOP` · Existing (expanded in v2.1)

---

## 1. Portal Identity

| Attribute | Value |
|---|---|
| **Portal ID** | P03 |
| **Portal code** | `AOP` |
| **Type** | Internal web application delivered as **role-scoped workspaces** |
| **Status** | Existing (expanded in v2.1 — from 8 to **14 workspaces**, adding marketplace, managed services, contract, warranty, procurement and system consoles) |
| **Priority** | **P0** — the first surface built; nothing else can be operated without it |
| **Delivery wave** | **W1** (Months 1–4), extended each wave as modules land |
| **Users** | Service agents, dispatchers, branch managers, operations, finance, HR, inventory, procurement, quality, marketplace, MSP and IT |
| **Volume** | **150–250 concurrent internal users** |
| **Business owner** | Operations Director |
| **System owner** | Core Platform Squad |
| **Technology** | Odoo Web Client (OWL 2 / TypeScript) — the ERP's own presentation layer |
| **Custom development** | `CD-203` (workspace framework and console shells; per-workspace content ships with its owning module) |
| **Requirement range** | FR-POR-079 … FR-POR-112 |
| **Requirement count** | **34** *(measured — supersedes the 18 allocation in `05-01` §4)* |
| **Effort estimate** | **30 person-weeks** (framework and shells only; workspace content is costed within each module) |
| **Backing modules** | **All 67** |
| **Platform dependencies** | M29 Identity · M28 Integration Gateway · M30 Platform Admin · M64 MDM · M65 Localisation |

---

## 2. Purpose

P03 is **where the Company is run**. It is the only surface with access to all 67 modules, the
only one where a record can be corrected, approved, overridden or reversed, and the one on
which 150–250 people spend their entire working day.

Its design problem is the opposite of P01's. P01 must be learnable in thirty seconds by someone
who will use it twice a year. P03 must be *fast* for someone who will use it eight hours a day
for five years — which means keyboard operation, dense screens, bulk actions and no decorative
motion between a user and their work.

P03 differs from every other portal in one structural respect: **it is not a separate
application.** It is the Odoo web client, configured into role-scoped workspaces. There is no
API boundary, no second data model and no synchronisation problem, because there is nothing to
synchronise. This is deliberate and it is the reason P03 can cover 67 modules at a cost eleven
other portals could not.

### Why It Exists

**Every other surface delegates its exceptions here.** A customer who cannot complete a
booking phones the contact centre, whose agent works in P10 and escalates into P03. A
technician whose sync conflicts needs a supervisor in P03. A vendor whose invoice will not
match needs a procurement officer in P03. P03 is where every other portal's unhappy path
terminates, which makes its completeness a precondition for all of them.

**Role-scoped workspaces, not a menu tree.** A service centre agent and a finance officer use
the same system and share almost no screens. The v1.0 design exposed one navigation structure
to everyone and relied on permissions to hide the rest, which produces a system where every
user sees mostly things they cannot use. `04-00` specifies fourteen workspaces, each *opening
on the work its role actually does* — a dispatch manager on the live map and the unassigned
queue, a branch manager on today's numbers and uncollected devices.

**Speed is the adoption mechanism.** `04-00` sets walk-in intake under 3 minutes, a full
morning dispatch queue under 10 minutes, page load under 2 seconds, and training to competence
under 4 hours. Those are not comfort targets. At 51+ branches and 250,000+ monthly customers, a
30-second delay per intake is measured in staff-years.

**The branch hardware is the constraint.** `04-00` names a 1366×768 laptop as the most common
branch hardware. Screen density is designed for that, not for a developer's monitor.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §4.1 Portal 3 | "Admin Operations Portal — 100-150 back-office users — service dispatch, inventory, customer management, system configuration" |
| ERP BRD BR-SRM-001 | Service orders created by an agent from phone and walk-in channels — the intake workspace |
| ERP BRD BR-FSM-002 | "Visual dispatch board (calendar + map view) with drag-and-drop assignment capability" |
| ERP BRD BR-FSM-003 | "Real-time GPS location of all active field technicians on a live map" |
| ERP BRD BR-INV-003 | "Single dashboard showing real-time stock levels at all locations" |
| ERP BRD BR-BI-002 | Branch performance dashboards comparing all 51+ locations |
| ERP BRD BR-SRM-011 | Configurable approval workflows for repairs exceeding a cost threshold |
| ERP BRD BR-CWM-007 | Warranty claim lifecycle tracking — the warranty console |
| ERP BRD BR-QMS-002 | Complaint management with root cause and CAPA — the quality console |
| ERP BRD NFR-001 | Page load ≤ 3 seconds for all ERP screens under normal load |
| ERP BRD NFR-003 | "500+ concurrent internal users without degradation" |
| `04-00` §P03 | **Fourteen named workspaces**, four design requirements and four KPIs, adopted verbatim |
| `04-00` §3 PS-01…PS-12 | Twelve cross-portal standards, all binding |
| `02-05` §2 | Odoo 19 CE with OWL 2 frontend is the L1 foundation; P03 is its presentation layer |
| `05-04` §2 | **32 of 38 roles hold P03 access** — more than any other portal by an order of magnitude |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** P03's boundary is the inverse of every other portal's:
> it can reach everything, so the discipline is stating what it must *not* do and where a user
> must go instead.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The workspace framework: role-scoped entry points, each opening on that role's actual work |
| 2 | The fourteen consoles named in `04-00` §P03, and the pattern by which a fifteenth is added |
| 3 | Global search across every object a user's role permits |
| 4 | Universal record navigation: any record reachable in ≤ 4 clicks from any starting point |
| 5 | Bulk actions on every list view |
| 6 | Keyboard-first operation for high-volume roles: intake, dispatch, finance, contact handling |
| 7 | Approval inboxes: every pending approval for a user, in one place, from every module |
| 8 | Exception queues: work that has failed, stalled, breached or conflicted, routed to a role |
| 9 | Inline record creation and editing under the owning module's rules |
| 10 | Override and reversal actions, each with a mandatory reason and an audit entry |
| 11 | Document generation, preview and reprint |
| 12 | Attachment, note and activity handling on every record (Odoo chatter) |
| 13 | Saved filters, personal views and list configuration per user |
| 14 | Export to PDF, Excel and CSV within the user's data scope |
| 15 | Notification centre and task inbox for internal users |
| 16 | Impersonation-free supervision: viewing another user's work under one's own identity |
| 17 | Screen density and layout tuned for a 1366×768 display |
| 18 | Bengali and English throughout, per role preference |
| 19 | Session, MFA and idle-timeout behaviour inherited from M29 |
| 20 | Instrumentation of task completion time for the four `04-00` speed KPIs |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Every business rule, calculation, state machine and validation** | **The owning module** (all 67) | P03 renders and invokes. It contains no business logic of its own (**PS-11**) |
| **The data model** | The owning module | P03 adds no table and no field. A field that exists only for a screen is a design defect |
| **Customer-facing surfaces** | **P01** | An agent acting for a customer does so in P03 under their own identity — never by logging into P01 as the customer |
| **Field execution and offline work** | **P02** | Anything a technician must do without connectivity belongs in P02. P03 assumes a connection |
| **Corporate client self-service** | **P04** | A corporate user manages their own estate in P04; P03 is where 1000FiX staff act on it |
| **Vendor self-service** | **P05** | A vendor submits their own invoice in P05; P03 is where it is matched |
| **Executive and analytical dashboards** | **P06** | P03 shows operational lists and work queues; P06 shows analysis. A console is for acting, a dashboard is for deciding |
| **Marketplace seller self-service** | **P07** | P03 hosts the Marketplace Console where 1000FiX governs sellers; sellers act in P07 |
| **Brand partner claim decisions** | **P08** | P03 prepares and submits; the brand decides in P08 |
| **Rider and courier execution** | **P09** | P03 hosts the coordinator view; riders work in P09 |
| **Contact handling, telephony and conversation state** | **P10** | An agent handles conversations in P10 and jumps into P03 for the action (`04-00` §P10) |
| **Mobile audit execution** | **P11** | Audits are executed on device; P03 shows the programme and the findings |
| **Identity, roles, permissions and record rules** | **M29** | P03 renders the System Console; M29 owns the engine |
| **Organisation structure, environments, jobs, feature flags** | **M30** | The System Console is a surface onto M30 |
| **Master data governance and stewardship workflow** | **M64** | P03 presents the stewardship queue; M64 owns the rules |
| **Workflow and approval orchestration** | **M63** | P03 shows an approval inbox; M63 routes and executes |

### 3.3 Shared Concepts

| Concept | P03's Role | Owning Module |
|---|---|---|
| The internal working surface | **Owns** — the defining concern of this portal | P03 |
| Workspace and console definition | **Owns** the framework; each module supplies its content | P03 / owning module |
| Every business object | Renders, creates, edits, approves under the owner's rules | All 67 modules |
| Approval inbox | Aggregates and presents | M63 routes |
| Exception queue | Aggregates and presents | The module that raised it |
| Search | Owns the surface; each module supplies its index | P03 |
| Permission | Enforces what M29 decides; never decides | M29 |
| Document rendering | Presents and reprints | M24 |
| Notification and task inbox | Presents | M27 / M63 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP Fiori launchpad and role-based spaces** | Role-based entry with task-oriented tiles; each business role sees a curated space rather than a full menu; overview pages combining KPIs, work lists and actions | **The role-space model is the single most influential external reference for P03.** A user's home is their *work*, not a navigation tree. `04-00`'s fourteen consoles are Fiori spaces by another name, and the pattern's value is proven at exactly this scale | Fiori's design-system weight and its separation of analytical, transactional and factsheet app types — over-structured for 250 users |
| **Microsoft Dynamics 365 Unified Interface — app modules** | One platform split into role-scoped *apps* (Sales, Field Service, Customer Service) over a shared data model, each with its own sitemap | **Role-scoped apps over one shared model** — exactly P03's structure, and the reason no synchronisation problem exists. Also adopted: dense list views with inline editing and bulk action as the default interaction | Its licence-tier-driven app boundaries |
| **Odoo 19 Web Client (OWL 2)** | List, form, kanban, calendar, pivot and map views; chatter on every record; saved filters; bulk actions; keyboard shortcuts; developer-free view configuration | **The whole substrate, adopted as intended.** This is the single largest cost avoidance in the portal suite: P03 covers 67 modules because it does not build a presentation layer, it configures one | Odoo's default menu-tree navigation, which is replaced by the console model. And Odoo's default screen density, which is tuned for a larger display than branch hardware |
| **ServiceNow Agent Workspace** | A single pane combining queue, record, context and action, with contextual side panels rather than page navigation | **Contextual side panels for context, page navigation for action.** A dispatcher looking at a job should see the technician's load without leaving the job | Its platform and licensing model |
| **Dispatch board practice (Salesforce FSL Gantt, ServiceMax)** | Combined map and Gantt with drag-and-drop assignment, SLA countdown, technician load, and re-optimisation on change | **The combined map-plus-list dispatch console with drag-and-drop and live SLA risk**, which is the direct implementation of BR-FSM-002 and the workspace with the tightest speed KPI (a full morning queue in under 10 minutes) | Full Gantt scheduling; a service business dispatching same-day work needs a map and a queue, not a project timeline |
| **High-volume back-office practice (banking, airline, telco desks)** | Keyboard-first operation, no mouse dependency on the critical path, screen density accepted as a virtue, muscle-memory stability across releases | **Keyboard-first for intake, dispatch and finance**, and **layout stability as a release constraint** — moving a control that 250 people have memorised costs more than the improvement gains. Changes to high-volume screens require an explicit adoption plan | Terminal-style interfaces; the workforce is not trained on them and turnover is real |

**Design position.** Five deliberate differences from the benchmark.

First, **P03 is configuration, not construction.** It is the Odoo web client with a workspace
framework on top. Every temptation to build a bespoke internal front end is refused, because
the moment P03 becomes a separate application it acquires an API boundary, a cache, a
synchronisation problem and a second permission implementation — for 250 internal users. The
custom effort here is the console framework and a small number of purpose-built consoles
(dispatch, branch, system); everything else is view configuration owned by its module.

Second, **the console opens on work, never on a menu.** `04-00` requires every workspace
reachable in one click and any record in four. A console whose landing page is a list of links
has failed its purpose. Each of the fourteen opens on a queue, a board or a set of numbers with
actions attached.

Third, **speed is a specified requirement with a number.** Intake under 3 minutes, morning
dispatch under 10, page load under 2 seconds, competence in under 4 hours. These are measured
in production, not assumed at design, and a regression against them is a defect.

Fourth, **there is no impersonation.** A supervisor may see another user's work; they act under
their own identity and the audit trail says so. `05-04` §6 SOD-09 blocks self-approval of
access, and impersonation would defeat every segregation-of-duties control in the estate.

Fifth, **every override carries a reason.** P03 is the only surface that can override, reverse
or force. Each such action requires a reason code, is separately reportable, and appears on a
standing exception report. The power to override is what makes P03 useful and what makes it
dangerous; the reason code is what keeps it accountable.

---

## 5. Capability Areas & Functions

### 5.1 Workspace Framework

| FR ID | Feature | Function — "The portal shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-079 | Role-scoped workspaces | Present each user a home composed of the consoles their roles permit, with no console visible that the user cannot use | **P0** | L5 |
| FR-POR-080 | Console landing | Open every console directly on that role's live work — a queue, a board or a set of actionable numbers — never on a menu or a link list | **P0** | L5 |
| FR-POR-081 | One-click reach | Make every permitted console reachable in one click from the home screen (`04-00` design requirement 1) | **P0** | L5 |
| FR-POR-082 | Four-click rule | Make any permitted record reachable in no more than four clicks from any starting point (`04-00` design requirement 2) | **P0** | L5 |
| FR-POR-083 | Global search | Search across every object type the user's role permits, ranked, with type-ahead, returning in under one second | **P0** | L5 |
| FR-POR-084 | Console extension pattern | Provide a declarative pattern by which a module contributes a console, a queue or a panel without modifying the framework | **P0** | L5 |
| FR-POR-085 | Layout stability | Treat the position of controls on high-volume screens as a release constraint, requiring an explicit adoption plan for any change | **P0** | L5 |

### 5.2 The Fourteen Consoles

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-086 | Service Intake Console | Open on the branch queue with quick intake and customer search; support walk-in intake end to end in under three minutes including device identification and estimate initiation | **P0** | L5 |
| FR-POR-087 | Dispatch Console | Present a live map and unassigned queue with technician load and SLA risk, supporting drag-and-drop assignment and re-optimisation, and dispatch of a full morning queue in under ten minutes (BR-FSM-002, BR-FSM-003) | **P0** | L5 |
| FR-POR-088 | Branch Console | Open on today's numbers, WIP ageing, cash position, staff presence and uncollected devices for the user's branch | **P0** | L5 |
| FR-POR-089 | Workshop Console | Present the bench board, WIP by state, parts holds and repair-level distribution | **P0** | L5 |
| FR-POR-090 | Inventory Console | Present network stock, replenishment alerts, transfers, counts and van variance (BR-INV-003) | **P0** | L5 |
| FR-POR-091 | Procurement Console | Present requisitions, purchase orders, receipts, RTVs and vendor performance | P1 | L5 |
| FR-POR-092 | Finance Console | Present invoices, receipts, reconciliation, ageing and the period-close checklist | P1 | L5 |
| FR-POR-093 | HR Console | Present attendance exceptions, leave, the payroll run and incentive calculations | P1 | L5 |
| FR-POR-094 | Quality Console | Present non-conformances, CAPAs, complaints, audit programme and checklist compliance | P1 | L5 |
| FR-POR-095 | Contract Console | Present the contract base, renewals, entitlement consumption and contract profitability | P1 | L5 |
| FR-POR-096 | Warranty Console | Present the claim pipeline, ageing, rejections and reconciliation against brand remittances (BR-CWM-007) | P1 | L5 |
| FR-POR-097 | Marketplace Console | Present seller approvals, disputes, performance scores and payout holds | P2 | L5 |
| FR-POR-098 | Managed Services Console | Present client estate health, open alerts, tickets, SLA attainment and patch compliance | P2 | L5 |
| FR-POR-099 | System Console | Present users, roles, configuration, scheduled jobs, integration health and platform status | **P0** | L5 |

### 5.3 Work Handling & Speed

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-100 | Approval inbox | Aggregate every approval pending for a user, from every module, into one prioritised inbox with the context needed to decide without navigating away | **P0** | L5 |
| FR-POR-101 | Exception queues | Route failed, stalled, breached and conflicted work to the accountable role as a worked queue with ageing, never as a report nobody opens | **P0** | L5 |
| FR-POR-102 | Bulk actions | Provide bulk action on every list view, with a confirmation showing exactly what will change and how many records (`04-00` design requirement 3) | **P0** | L5 |
| FR-POR-103 | Keyboard-first operation | Support complete keyboard operation without mouse dependency on the intake, dispatch, finance and cashier paths (`04-00` design requirement 4) | **P0** | L5 |
| FR-POR-104 | Saved views | Allow each user to save filters, column sets and sort orders as personal views, and a role owner to publish a shared view | P1 | L5 |
| FR-POR-105 | Inline creation | Permit creation and editing of related records inline without losing the parent context | P1 | L5 |
| FR-POR-106 | Export | Export any permitted list or record set to PDF, Excel and CSV within the user's data scope, with the export logged | P1 | L2 |
| FR-POR-107 | Document handling | Generate, preview, print and reprint any document through M24, with reprints marked and logged | **P0** | L5 |

### 5.4 Control, Supervision & Accountability

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-108 | Override with reason | Require a reason code on every override, reversal, force-close and manual adjustment, write it to the audit trail, and include it on a standing exception report | **P0** | L5 |
| FR-POR-109 | No impersonation | Provide supervision by visibility — a supervisor sees another user's work under their own identity — and provide **no impersonation capability at any privilege level** | **P0** | L5 |
| FR-POR-110 | Activity and audit view | Present the full activity, note and audit history on every record through chatter, showing who changed what and when (AS-02) | **P0** | L1 |
| FR-POR-111 | Notification and task inbox | Present a single internal inbox of notifications, assigned tasks and mentions across every module | P1 | L1/L5 |
| FR-POR-112 | Screen density and language | Render at a density suited to a 1366×768 display without horizontal scrolling, in Bengali or English per user preference (`04-00` design requirement 5, **PS-03**) | **P0** | L5 |

> **Cross-cutting.** Each console's *content* — which columns, which actions, which rules — is
> specified by the module that owns the data and is costed within that module. P03 specifies the
> framework, the landing behaviour, the speed budget and the accountability controls.

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **No separate application** | P03 is the Odoo web client with a workspace framework. It introduces no second data model, no API boundary, no cache of business data and no second permission implementation |
| T-02 | **No business logic in the presentation layer** | Views invoke module methods. No calculation, validation or state transition is implemented in a view, a widget or a controller (AS-09, **PS-11**) |
| T-03 | **No schema additions** | P03 adds no table and no field. A field that exists only to satisfy a screen belongs to the module that owns the object, or it does not exist |
| T-04 | **Page load budget** | Standard screen load ≤ 2 seconds (`04-00` KPI); no screen exceeds NFR-001's 3 seconds under normal load. Enforced by synthetic monitoring per console |
| T-05 | **List performance** | A list view over a million-row table returns the first page in ≤ 1.5 seconds with the user's default filter applied; unfiltered full-table views are not offered |
| T-06 | **Concurrency envelope** | 500+ concurrent internal users without degradation (NFR-003), against a working population of 150–250 |
| T-07 | **Search performance** | Global search returns ranked results in ≤ 1 second across permitted object types |
| T-08 | **Permission enforcement at the record layer** | Every list, form and export is filtered by M29 record rules at the ORM layer, never by hiding controls in the view. A hidden button is not a permission |
| T-09 | **Multi-branch and multi-entity scoping** | Every screen inherits `company_id` and `operating_unit_id` context; a branch user cannot see another branch's records through any view, filter or export (AS-03) |
| T-10 | **Audit by default** | Every model carries `mail.thread` and `mail.activity.mixin`; no module writes audit code and no change is unattributed (AS-02) |
| T-11 | **Session and MFA inherited** | Session lifetime, idle timeout and MFA are M29 policy, applied identically to every console (**PS-12**) |
| T-12 | **Keyboard accessibility** | Every action on the intake, dispatch, finance and cashier paths is reachable and operable by keyboard, with a discoverable shortcut map |
| T-13 | **Screen density target** | Designed and tested at 1366×768 with no horizontal scrolling; larger displays gain more rows, not larger controls |
| T-14 | **Bengali and English** | Complete translation of every label, message and error, switchable per user (**PS-03**, AS-12) |
| T-15 | **Accessibility** | WCAG 2.1 AA on internal surfaces, with keyboard navigation and contrast as the primary criteria (**PS-04**) |
| T-16 | **Export governance** | Every export is logged with user, scope, row count and timestamp; bulk export beyond a threshold requires a reason |
| T-17 | **Console extension without core change** | A module contributes a console, queue or panel through a declarative registry; adding the fifteenth console requires no framework change |
| T-18 | **Instrumentation** | Task completion time is measured in production for intake, dispatch, approval and close, feeding the four `04-00` KPIs (**PS-10**) |
| T-19 | **Layout stability** | Control positions on high-volume screens are treated as an interface contract; a change requires an adoption plan and a communication step |
| T-20 | **Graceful degradation** | Where a module is unavailable, its console shows the outage and the alternative, and the rest of P03 continues to work (**PS-09**) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With P03 |
|---|---|---|
| **Service centre agent** | Types the same customer into two systems, hunts for device history | Intake console: search, identify, create, estimate — under three minutes |
| **Dispatch manager** | Assigns by phone, whiteboard and memory | Live map with technician load, SLA risk and drag-and-drop; a morning queue in ten minutes |
| **Branch manager** | Compiles today's numbers from three places at 6 p.m. | Opens on today's numbers, WIP ageing, cash and uncollected devices |
| **Workshop supervisor** | Runs the bench from a whiteboard | Bench board with WIP state, parts holds and repair levels |
| **Inventory manager** | Reconstructs the network position from 51 spreadsheets | One console showing network stock, alerts, transfers and van variance |
| **Finance officer** | Chases documents to close the period | Close checklist as a worked queue with ageing |
| **Quality manager** | Learns of an NCR when someone mentions it | NCRs, CAPAs and complaints as an owned queue with due dates |
| **Warranty officer** | Tracks claims in a spreadsheet beside the ERP | Claim pipeline with ageing, rejections and reconciliation |
| **HR officer** | Compiles attendance exceptions manually | Exceptions arrive as a queue |
| **IT administrator** | Diagnoses by log file | System console: users, jobs, integration health, platform status |
| **Any approver** | Approvals arrive by email and get lost | One approval inbox across all 67 modules, with the context to decide |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Administrative labour savings** | One system, role-scoped, no re-keying, no cross-system reconciliation, bulk actions, worked queues instead of compiled reports | The principal delivery mechanism for the **BDT 62 lac/year** cross-module administrative saving in Scope Charter §6.2 |
| **Intake throughput** | Walk-in intake under 3 minutes against an unmeasured baseline widely reported as 8–12 | At 51+ branches and 250,000+ monthly customers this is the largest single labour recovery in the estate |
| **Dispatch throughput** | Morning queue dispatched in under 10 minutes | Releases dispatcher capacity and improves SLA attainment by starting the day earlier |
| **Technician productivity** | Better dispatch decisions from load and SLA visibility | Contributes to the **BDT 130 lac/year** productivity benefit attributed to M02 + M26 |
| **Financial close** | Close checklist as a worked queue with ageing and ownership | Supports the **BDT 26 lac/year** close and cash-flow benefit attributed to M19 + M20, and KPI-050 (close ≤ 3 days) |
| **Warranty recovery** | Claim pipeline visible with ageing and rejection reasons worked as a queue | Supports the **BDT 100 lac/year** warranty recovery attributed to M09 |
| **Training cost** | Competence in under 4 hours for a new agent, against a system with 67 modules | At the turnover rates of a 500+ person service organisation this is a continuous saving |
| **Inventory accuracy** | Network position and van variance visible and worked daily | Supports M15's 75% → 98% accuracy target |
| **Cost avoidance — no bespoke front end** | Odoo web client configured rather than a custom internal application built | Avoids an estimated 150–250 PW of construction and its permanent maintenance |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **One system of record, visibly** | Staff see one system. The fragmentation the programme exists to remove is removed where people actually experience it |
| **Accountability by construction** | Chatter on every record, a reason on every override, and no impersonation means every action has a name against it |
| **Segregation of duties is real** | The twelve SOD rules in `05-04` §6 are enforced in the surface where the incompatible actions would otherwise be taken |
| **Bengali as a working language internally** | Branch staff work in Bengali. A system that forces English on 250 daily users produces workarounds and errors |
| **Institutional knowledge retention** | A departing branch manager's knowledge lives in queues, notes and history rather than in their head |
| **Auditability** | An ISO or brand auditor can be shown any record's full history from the same surface staff use daily |
| **Scalability of the operating model** | A new branch is a configuration change; its staff open the same consoles on day one |

---

## 8. User Journeys & State Models

### 8.1 The Workspace Model

```
   LOGIN (M29 · SSO · MFA per role policy)
        │
   ┌────▼──────────────────────────────────────────────────────┐
   │  HOME — composed of the consoles this user's roles permit  │
   │  No console shown that the user cannot use                 │
   └────┬──────────────────────────────────────────────────────┘
        │ one click (FR-POR-081)
   ┌────▼──────────────────────────────────────────────────────┐
   │  CONSOLE — opens on live work, never on a menu             │
   │                                                            │
   │   ┌──────────────┬───────────────┬─────────────────────┐  │
   │   │ WORK QUEUE   │ APPROVAL      │ EXCEPTION QUEUE     │  │
   │   │ today's work │ INBOX         │ failed · stalled ·  │  │
   │   │              │ all modules   │ breached · conflict │  │
   │   └──────────────┴───────────────┴─────────────────────┘  │
   └────┬──────────────────────────────────────────────────────┘
        │ ≤ 4 clicks to any record (FR-POR-082)
   ┌────▼──────────────────────────────────────────────────────┐
   │  RECORD — form · chatter · activity · related records      │
   │  actions invoke the owning module; no logic lives here     │
   └───────────────────────────────────────────────────────────┘

   Cross-cutting from anywhere:  GLOBAL SEARCH · NOTIFICATION INBOX
```

### 8.2 The Fourteen Consoles and What Each Opens On

| Console | Primary role | Opens on | Speed commitment |
|---|---|---|---|
| **Service Intake** | R08 Service Centre Agent | Branch queue · quick intake · customer search | **Walk-in intake < 3 min** |
| **Dispatch** | R07 Dispatch Manager | Live map · unassigned queue · technician load · SLA risk | **Morning queue < 10 min** |
| **Branch** | R06 Branch Manager | Today's numbers · WIP ageing · cash · staff · uncollected devices | Load < 2 s |
| **Workshop** | R09 Workshop Supervisor | Bench board · WIP by state · parts holds | Load < 2 s |
| **Inventory** | R17 Inventory Manager | Network stock · alerts · transfers · counts · van variance | Load < 2 s |
| **Procurement** | R19 Procurement Officer | Requisitions · POs · receipts · vendor performance | Load < 2 s |
| **Finance** | R26/R27 Finance | Invoices · receipts · reconciliation · ageing · close checklist | Load < 2 s |
| **HR** | R30/R31 HR | Attendance exceptions · leave · payroll run · incentives | Load < 2 s |
| **Quality** | R32 Quality Manager / ISO Coordinator | NCRs · CAPAs · complaints · audits · checklists | Load < 2 s |
| **Contract** | R22 Account Manager (Corporate) | Contract base · renewals · entitlements · profitability | Load < 2 s |
| **Warranty** | R28 Warranty Officer | Claim pipeline · ageing · rejections · reconciliation | Load < 2 s |
| **Marketplace** | R24 Marketplace Ops | Seller approvals · disputes · scores · payouts | Load < 2 s |
| **Managed Services** | R13 Remote Support | Estate health · alerts · tickets · SLA · patch compliance | Load < 2 s |
| **System** | R33 IT / System Administrator | Users · roles · configuration · jobs · integrations · health | Load < 2 s |

### 8.3 Override — the accountability path

```
   USER ATTEMPTS AN ACTION THE RULES REFUSE
        │
   ┌────▼─────────────────────────────────┐
   │  Is an override permitted for this   │
   │  rule at this user's authority?      │
   └────┬────────────────────┬────────────┘
        │ no                 │ yes
   ┌────▼──────────┐   ┌─────▼────────────────────────────┐
   │  HARD BLOCK   │   │  REASON CODE REQUIRED (mandatory)│
   │  explain why  │   │  + free-text justification       │
   │  + who can    │   └─────┬────────────────────────────┘
   └───────────────┘         │
                       ┌─────▼────────────────────────────┐
                       │  AUDIT ENTRY written (AS-02)     │
                       │  actor · rule · reason · before  │
                       │  and after · timestamp           │
                       └─────┬────────────────────────────┘
                             │
                       ┌─────▼────────────────────────────┐
                       │  STANDING EXCEPTION REPORT        │
                       │  reviewed by the rule's owner     │
                       └──────────────────────────────────┘
```

> **Rule.** A hard block (class **H**) has no override path in P03 at any privilege level,
> including CTO. Only class **A** rules present the override path above. This distinction is
> what makes the module-level rule classifications meaningful rather than advisory.

---

## 9. Portal Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| PRU-P03-01 | P03 implements no business rule, calculation or state transition; it renders and invokes (AS-09, **PS-11**) | **H** | CTO |
| PRU-P03-02 | P03 adds no table and no field to the data model | **H** | CTO |
| PRU-P03-03 | **No impersonation capability exists at any privilege level**; supervision is by visibility under one's own identity | **H** | CTO |
| PRU-P03-04 | Every override, reversal, force-close and manual adjustment requires a reason code and appears on a standing exception report | **H** | Operations Director |
| PRU-P03-05 | A class-H rule has no override path in P03 at any authority level | **H** | CTO |
| PRU-P03-06 | Permission is enforced at the record layer, not by hiding controls; a hidden button is not a permission | **H** | CTO |
| PRU-P03-07 | A user cannot see or export another branch's or entity's records through any view, filter or export (AS-03) | **H** | CTO |
| PRU-P03-08 | Every export is logged with user, scope, row count and timestamp; bulk export beyond threshold requires a reason | **H** | CFO |
| PRU-P03-09 | Every console opens on live work, never on a menu or a link list | **C** | Operations Director |
| PRU-P03-10 | No console is visible to a user who cannot act in it | **C** | Operations Director |
| PRU-P03-11 | Every record carries chatter and activity history; no change is unattributed (AS-02) | **H** | CTO |
| PRU-P03-12 | Segregation-of-duties rules are enforced at the point of action, not detected afterwards (`05-04` §6) | **H** | CFO |
| PRU-P03-13 | Every screen is complete in Bengali and English before release (**PS-03**, AS-12) | **H** | Operations Director |
| PRU-P03-14 | Screens are designed and tested at 1366×768 with no horizontal scrolling | **C** | Operations Director |
| PRU-P03-15 | Control positions on high-volume screens are an interface contract; a change requires an adoption plan | **C** | Operations Director |
| PRU-P03-16 | Every bulk action shows exactly what will change and how many records before it executes | **H** | Operations Director |
| PRU-P03-17 | A reprinted document is marked as a reprint and the reprint is logged | **H** | CFO |
| PRU-P03-18 | Where a module is unavailable, its console shows the outage and the alternative; the rest of P03 continues (**PS-09**) | **H** | CTO |
| PRU-P03-19 | Task completion time for intake, dispatch, approval and close is instrumented in production | **C** | Operations Director |
| PRU-P03-20 | An exception is a worked queue with an owner and ageing, never a report | **C** | Operations Director |

---

## 10. Data, Caching & State Model

> **P03 is unique in the suite: it has no data boundary.** It is the ERP's own presentation
> layer, operating directly on the ORM within M29's record rules. There is no projection, no
> cache of business data and no synchronisation.

### 10.1 What P03 Holds

| Object | Purpose | Ownership |
|---|---|---|
| Console and workspace definitions | Which console exists, what it opens on, which roles see it | **P03** — the only configuration it owns |
| Personal saved views | Filters, columns, sort order per user | **P03** |
| Shared published views | Role-level standard views | **P03**, published by a role owner |
| Keyboard shortcut map | Per-console shortcut definitions | **P03** |
| Session and UI preference | Language, density, last console | M29 (session) / P03 (preference) |

### 10.2 What P03 Never Holds

| Item | Reason |
|---|---|
| Any business object or field | PRU-P03-02; every object belongs to its module |
| A cache or projection of business data | It reads the ORM directly; there is nothing to cache |
| A second permission model | M29 is the only permission engine |
| Business rules or thresholds | M64 stores them; M63 executes them |

### 10.3 Referenced Entities

P03 reads and writes **every entity in the estate**, always through the owning module's model
and always within M29's record rules. The consoles map to owners as follows:

| Console | Primary modules |
|---|---|
| Service Intake | M01, M04, M17, M33, M11, M37 |
| Dispatch | M02, M01, M55, M15, M46 |
| Branch | M04, M01, M15, M19, M21, M47 |
| Workshop | M31, M01, M15, M45, M23 |
| Inventory | M15, M41, M43, M37 |
| Procurement | M16, M42, M44, M52 |
| Finance | M19, M20, M50, M51, M52, M53, M54 |
| HR | M21, M55, M56, M57, M22, M59 |
| Quality | M23, M60, M24, M61 |
| Contract | M08, M39, M07, M36 |
| Warranty | M09, M17, M15 |
| Marketplace | M12, M53, M34 |
| Managed Services | M05, M48, M17 |
| System | M29, M30, M28, M64, M63, M66, M65 |

---

## 11. Automations & Notifications

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-P03-01 | An approval is raised by any module | Place it in the approver's single approval inbox with the context needed to decide, and notify per their preference | Approval remains pending and visible; escalation per M63 |
| AUT-P03-02 | Work fails, stalls, breaches SLA or raises a conflict | Route it to the accountable role's exception queue with ageing and an owner | Exception remains open and reportable |
| AUT-P03-03 | A user logs in | Compose the home from their permitted consoles and open on the one they used last | Fall back to a default console; never a blank home |
| AUT-P03-04 | A high-volume screen changes control positions | Require an adoption plan and notify affected users before release | Release blocked pending the plan |
| AUT-P03-05 | An override is recorded | Write the audit entry and add it to the standing exception report for the rule's owner | Override blocked if the audit write fails |
| AUT-P03-06 | A bulk export exceeds the configured row threshold | Require a reason, log it, and notify the data owner | Export blocked pending reason |
| AUT-P03-07 | A module becomes unavailable | Mark its console degraded with an explanation and alternative, and raise a platform alert to M30 | Fail visible, never silent |
| AUT-P03-08 | A record is mentioned or assigned to a user | Deliver to the internal notification and task inbox | Retry; inbox entry always written |
| AUT-P03-09 | A SoD-incompatible action is attempted | Block at the point of action, name the conflicting duty, and log the attempt | Hard block |
| AUT-P03-10 | Page load or task time regresses against the `04-00` KPI budget | Raise a performance defect against the owning console | Alert to the Core Platform Squad |

---

## 12. Module Interfaces

### 12.1 What P03 Consumes

P03 consumes **all 67 modules** directly through the ORM. It is not an API client. The
platform dependencies that govern it are:

| Module | What | Mechanism |
|---|---|---|
| M29 Identity, Access & Security | Authentication, roles, record rules, field permissions, SoD enforcement, audit | ORM / framework |
| M30 Platform Administration | Organisation structure, users, environments, feature flags, jobs, health | ORM |
| M64 Master Data Management | Stewardship queues, reference data, rule parameters | ORM |
| M63 Process Automation | Approval routing, workflow state, task assignment | ORM |
| M28 Integration Platform | Integration health surfaced in the System Console | ORM + REST |
| M24 Documents | Document generation, preview, print, retention | ORM |
| M27 Communications | Internal notification and task inbox | ORM |
| M65 Localisation | Bengali and English translation bundles | Framework |
| M25 Business Intelligence | Embedded operational panels within consoles | Embed |
| All other modules | Their objects, views, actions and consoles | ORM |

### 12.2 What P03 Provides

| Consumer | What | Mechanism |
|---|---|---|
| Every internal role | The working surface for all 67 modules | Web |
| P10 Contact Centre Console | Deep links into any P03 record with the conversation context preserved (`04-00` §P10) | Deep link |
| P06 Analytics | Drill-through from a dashboard figure to the underlying records | Deep link |
| P11 Field Auditor | The audit programme, findings and CAPA surfaces that P11 syncs into | ORM |
| P02 Technician App | Supervisor visibility of sync health, queues and conflicts | ORM |
| P09 Logistics | The coordinator web view (`04-00` §P09 coordinator view) | Web |
| M25 / M62 | Task completion time, console usage and error instrumentation | Event stream |

### 12.3 Events P03 Consumes

| Event | Source | Effect in P03 |
|---|---|---|
| `approval.requested` | M63 | Approval inbox entry |
| `*.exception_raised` | Any module | Exception queue entry with owner and ageing |
| `sla.at_risk` / `sla.breached` | M01 / M08 | Dispatch and branch console alerting |
| `integration.degraded` | M28 | System Console health indicator |
| `stock.van_variance_detected` | M15 | Inventory and branch console queue |
| `equipment.out_of_service` | M45 | Workshop and quality console alert |
| `site.compliance_expired` | M47 | Branch and quality console alert |
| `telemetry.pipeline_degraded` | M48 | System and managed-services console alert |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-P03-01 | Thermal and document printers at branches | Outbound | Job sheets, receipts, labels, service reports |
| INT-P03-02 | Barcode and QR scanners at counters and stores | Inbound | Device, part and location scanning at intake and issue |
| INT-P03-03 | Biometric attendance devices | Inbound | Attendance capture surfaced in the HR console (BR-HRM-004) |
| INT-P03-04 | Cash drawers and POS peripherals | Local | Counter cash handling in the branch console |
| INT-P03-05 | Google Maps Platform | Outbound | Dispatch console live map |

### 12.5 API Surface

P03 exposes **no API**. It is a consumer of the ERP's own model layer. Where an external
system needs P03-equivalent capability, it uses the module APIs through the M28 gateway, and
that is a deliberate constraint: an internal portal with its own API becomes a second
integration surface with a second permission model.

---

## 13. Roles & Permissions

**32 of the 38 roles in `05-04` §1 hold P03 access** — more than any other portal.

| Role group | Roles | Console access |
|---|---|---|
| Executive | R01 Chief Executive Officer, R02 Chief Technology Officer, R03 Chief Financial Officer, R04 Chief Commercial Officer, R05 Operations Director | All consoles, read and approve; System Console for R02 |
| Branch operations | R06 Branch Manager, R08 Service Centre Agent, R09 Workshop Supervisor, R29 Cashier / Counter Finance | Intake, Branch, Workshop, Finance (cashier scope) |
| Dispatch and field | R07 Dispatch Manager, R12 Specialist Technician | Dispatch, Workshop |
| Remote and data | R13 Remote Support Engineer, R14 Data Services Technician | Managed Services; data-services scope (T5 isolation) |
| Supply chain | R15 Logistics Coordinator, R17 Inventory Manager, R18 Store Keeper, R19 Procurement Officer, R20 Warehouse Operative | Inventory, Procurement, Logistics coordinator view |
| Commercial | R21 Sales Manager, R22 Account Manager (Corporate), R23 Marketing Manager, R24 Marketplace Ops, R25 Retail/Refurb Officer | Contract, Marketplace |
| Finance and governance | R26 Finance Manager, R27 Finance Officer, R28 Warranty Officer, R32 Quality Manager / ISO Coordinator | Finance, Warranty, Quality |
| People | R30 HR Manager, R31 HR Officer | HR |
| Technology | R33 IT / System Administrator | **System Console** |
| Contact centre | R35 Contact Centre Supervisor | Read across operational consoles |

> **Roles without P03 access:** R10 and R11 Technicians (P02 only), R16 Rider / Delivery Agent (P09 only),
> R34 Contact Centre Agent (P10 only), R36 Customer (P01), R37 Corporate Portal User (P04),
> R38 External Party (P05, P07, P08, P09, P12). **No external party has any P03 access under
> any circumstance.**

**Field-level restrictions.** Every restriction in `05-04` §5 is enforced at the record layer:
`unit_cost` and `margin` to R01–R05, R06, R17, R21, R22, R26, R27; `salary` and `deductions` to
R03, R26, R30, R31 and the employee; `nid_number` and `bank_account` to the named finance and
HR roles; `call_recording_url` to R35, R32 and R02; `model_confidence` to R02, R33 and model
owners. A restricted field is absent from the response, not merely hidden in the view.

**Segregation of duties.** All twelve SOD rules in `05-04` §6 are enforced at the point of
action in P03, because P03 is the surface where the incompatible actions would otherwise be
taken. **SOD-09 is enforced structurally**: a user administering access cannot approve their
own access request, and no impersonation path exists to circumvent it.

---

## 14. Analytics & Instrumentation

| Instrumentation | What Is Captured | Consumer |
|---|---|---|
| **Task completion time** | Intake, dispatch, approval, close — measured in production per user and per branch | M25 — **the four `04-00` KPIs** |
| Console usage | Which consoles are opened, how often, by whom; consoles never opened | M25, Operations Director |
| Page and list performance | Load time per console and per list view, at p50/p95, by branch hardware class | M30 |
| Search | Queries, result relevance proxies, searches returning nothing | M25 |
| Approval throughput | Time in the approval inbox, by approver and approval type | M63, M25 |
| Exception queues | Queue depth, ageing, resolution time, queues growing faster than they are worked | M25, Operations Director |
| Override register | Every override by rule, reason, user and frequency | Internal Audit, rule owners |
| Export register | Every export by user, scope and row count | CFO, M29 |
| SoD blocks | Attempted incompatible actions, by rule and user | M60, Internal Audit |
| Training and competence | Time from first login to independent task completion, per role | HR, M22 |
| Error rate | User-visible errors by console, screen and frequency | M30 |
| Bulk action usage | Bulk operations by type and record count | M25 |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W2 Target | W8 Target |
|---|---|---|---|---|
| — | **Walk-in intake time** | unmeasured | < 4 min | **< 3 min** |
| — | **Dispatch of a full morning queue** | unmeasured | < 15 min | **< 10 min** |
| — | **Page load (standard screen)** | n/a | < 2.5 s | **< 2 s** |
| — | **Training time to competence (new agent)** | unmeasured | < 6 h | **< 4 h** |
| — | Concurrent internal users without degradation | n/a | 300 | **500+** |
| — | Global search response (p95) | n/a | ≤ 1.5 s | **≤ 1 s** |
| — | Approval inbox median time to decision | unmeasured | < 8 h | **< 4 h** |
| — | Exception queue items aged beyond SLA | n/a | < 8% | **< 2%** |
| — | Overrides per 1,000 transactions | unmeasured | baselined | **falling trend** |
| — | Consoles opened at least weekly by their role | n/a | 85% | **> 95%** |
| — | Bengali completeness on internal screens | partial | **100%** | **100%** |
| — | Screens requiring horizontal scroll at 1366×768 | unmeasured | **0** | **0** |
| — | SoD-incompatible actions completed | unknown | **0** | **0** |
| **KPI-050** *(supported)* | Financial close duration | unmeasured | ≤ 5 days | **≤ 3 days** |

> **Register note.** The first four metrics are adopted verbatim from `04-00` §P03. P03 has
> **no KPI-0nn identifiers allocated**; all thirteen unnumbered metrics require allocation in
> `06-02` (not yet issued). Recorded as an audit action. KPI-050 is owned by M19 and is shown as
> *supported*.

---

## 16. Delivery

### 16.1 Technology & Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | **Odoo 19 CE web client (OWL 2)** — list, form, kanban, calendar, pivot, map and graph views; chatter; saved filters; bulk actions; export | 58% |
| L2 | OCA UI and reporting modules — view enhancements, `web_*` family, `reporting-engine` for embedded panels | 14% |
| L5 | **Workspace and console framework** (`CD-203`) plus purpose-built consoles: Dispatch, Branch, System | 28% |

> This allocation is the single largest cost avoidance in the portal suite. P03 covers all 67
> modules at 30 PW because it configures a presentation layer rather than building one. Every
> other portal in the suite is a separate application with its own API surface; P03 deliberately
> is not.

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-203** | `p03_workspace_framework` — role-scoped console registry and composition, console landing behaviour, global search, approval inbox aggregation, exception queue routing, keyboard shortcut framework, override-with-reason control, export governance, density and layout standards, task-time instrumentation; plus the three purpose-built consoles (Dispatch, Branch, System) | Odoo module (OWL 2) | 30 PW |

> **Effort note — important.** 30 PW covers the **framework and three purpose-built consoles
> only**. The content of the other eleven consoles — which columns, which actions, which
> validations — is specified and costed within each owning module's effort estimate. Treating
> P03 as a 30 PW deliverable that produces fourteen complete consoles would understate the work
> by an order of magnitude and is the most likely estimating error in this portal.
>
> **CD register.** One ID, **CD-203**, claimed following CD-202 (P02). All CD IDs remain
> provisional pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M29 Identity, Access & Security | Roles, record rules and field permissions are the substrate of every console |
| M30 Platform Administration | Organisation structure and users must exist before a console can be scoped |
| M28 Integration Platform | System Console integration health; event consumption for exception queues |
| M64 Master Data Management | Stewardship queues; reference data behind every list |
| M63 Process Automation | Approval routing behind the approval inbox — **available W3**; until then approvals are per-module |
| The owning module of each console | A console cannot precede the module whose work it shows |

**Wave progression.** P03 is not delivered once. The framework and the W1 consoles ship in
Wave 1; each subsequent wave adds the consoles for the modules it delivers.

| Wave | Consoles delivered |
|---|---|
| **W1** | Framework · Service Intake · Branch · System |
| **W2** | Dispatch · Workshop · Inventory |
| **W3** | Procurement · Finance |
| **W4** | Contract · Warranty |
| **W5** | HR · Quality · Managed Services |
| **W7** | Marketplace |

### 16.4 Adoption & Training

| Activity | Scope | Wave |
|---|---|---|
| Role-based training curricula | One per console, in Bengali | W1 onward, per console |
| Branch champion programme | 1 per branch, 4 hours/week during rollout (`06-01` §4) | W1–W5 |
| Competence assessment | New agent independent within 4 hours | Continuous |
| Layout change protocol | Adoption plan and communication before any high-volume screen change | Continuous |

> **Adoption position.** `06-01` §7 identifies branch managers as a medium adoption risk because
> "visibility cuts both ways". The mitigation applies directly to P03: the Branch Console is
> positioned as the branch manager's own instrument — their numbers, their queue, their
> exceptions — before it is positioned as a reporting surface for head office. A console
> experienced as surveillance is a console worked around.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A new service centre agent completes a walk-in intake in under 3 minutes, median, including device identification | Timed observation of 30 intakes across 3 branches |
| AC-02 | A dispatcher assigns a full morning queue in under 10 minutes | Timed observation across 5 branches over 5 days |
| AC-03 | Every standard screen loads in under 2 seconds on 1366×768 branch hardware | Synthetic monitoring per console over 30 days |
| AC-04 | A new agent reaches independent competence in under 4 hours of training | Competence assessment for 20 new agents |
| AC-05 | The system supports 500+ concurrent internal users without degradation | Load test at NFR-003 volume |
| AC-06 | Every permitted console is reachable in one click and every permitted record in four | Navigation audit across all 14 consoles |
| AC-07 | Global search returns ranked results in ≤ 1 second at p95 | Performance test at production data volume |
| AC-08 | P03 contains no business logic: no calculation, validation or state transition in any view or controller | Code review and static analysis (AS-09) |
| AC-09 | P03 adds no table and no field to the data model | Schema diff against the module-owned schema |
| AC-10 | **No impersonation capability exists**, verified by attempting it at every privilege level including CTO | Privilege-escalation negative test |
| AC-11 | Every override records a reason code, writes an audit entry, and appears on the standing exception report | Scripted override across five rule types |
| AC-12 | A class-H rule cannot be overridden in P03 at any authority level | Negative test against five class-H rules from different modules |
| AC-13 | A restricted field is absent from the response payload, not merely hidden in the view | Payload inspection for every field in `05-04` §5 |
| AC-14 | A branch user cannot see or export another branch's records through any view, filter, search or export | Isolation test including direct URL and export paths |
| AC-15 | All twelve SOD rules are blocked at the point of action, with the attempt logged | Twelve negative tests, one per SOD rule |
| AC-16 | Every export is logged with user, scope, row count and timestamp | Export register review |
| AC-17 | Every bulk action shows exactly what will change and how many records before executing | Bulk-action review across all list views |
| AC-18 | Complete keyboard operation on the intake, dispatch, finance and cashier paths, with no mouse dependency | Keyboard-only task completion test |
| AC-19 | No screen requires horizontal scrolling at 1366×768 | Responsive audit across all 14 consoles |
| AC-20 | Every label, message and error renders in Bengali | Translation coverage report at 100% |
| AC-21 | With a module deliberately unavailable, its console degrades with an explanation and the rest of P03 continues | Chaos test per console |
| AC-22 | Every record shows full chatter and audit history with attributed changes | Audit trail review |
| AC-23 | Operations Director and one branch manager per zone sign off UAT | Signed UAT record |

**Definition of done:** the four design requirements in `04-00` §P03, the twelve cross-portal
standards in `04-00` §3, plus the 23 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Is the branch hardware baseline confirmed as 1366×768, and what is the actual estate — screen sizes, browser versions, RAM? | CTO / Branch Operations Lead | **W1 minus 2 months** |
| Q-02 | Do branch staff work primarily in Bengali? If so, Bengali is the default for internal roles, which changes the translation critical path | Operations Director / HR Director | **W1 design** |
| Q-03 | Which console does each role open on by default where a user holds several roles? | Operations Director | W1 design |
| Q-04 | Who owns each console's content — the module squad or a central UX function? Without a named owner, consoles drift into inconsistency | CTO / Operations Director | **W1 design** |
| Q-05 | What is the override authority matrix per rule class, and who reviews the standing exception report? | CFO / Operations Director | W1 design |
| Q-06 | Is the bulk-export row threshold set, and who is notified above it? | CFO / CTO | W1 build |
| Q-07 | How is the "no impersonation" position reconciled with support cases where an agent must reproduce a customer's problem? | CTO / Customer Service Manager | W1 design |
| Q-08 | What is the layout-change protocol — who approves a change to a high-volume screen, and what notice do users receive? | Operations Director | W1 design |
| Q-09 | Are the eleven module-owned consoles costed inside their modules' estimates? If not, the programme is under-estimated by a material amount | CTO / Programme Manager | **W1 planning** |
| Q-10 | Does the Cashier role need a dedicated console, or is it a scoped view of the Finance and Branch consoles? | CFO / Branch Operations Lead | W1 design |
| Q-11 | Is a fifteenth console needed for Facilities (M47) and Fleet (M46) in Wave 5–7, or do they sit inside the Branch Console? | Operations Director / Branch Operations Lead | W5 planning |
| Q-12 | What browser support floor applies, given the branch estate and Odoo 19's OWL 2 requirements? | CTO | W1 build |

---

## 19. References

**Internal**
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` §1, §P03 (fourteen workspaces,
design requirements, KPIs), §3 PS-01…PS-12, §4 ·
`P01_Customer_Self_Service_Portal_and_Mobile_Application.md` ·
`P02_Technician_Mobile_Application.md` · `P06_Analytics_and_Executive_Dashboard.md` ·
`P09_Logistics_and_Rider_Application.md` · `P10_Contact_Centre_Agent_Console.md` ·
`P11_Field_Auditor_and_Quality_Application.md` ·
`03_Modules/K_Platform_and_Technology/_CATEGORY_OVERVIEW.md` §6 (boundary map), §7 (platform contract) ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §5, §10 (AS-01, **AS-02**, AS-03, AS-09, AS-12) ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §2 (Odoo 19 CE, OWL 2), §3 (OCA) ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` §4 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md`
§1, §2 (32 of 38 roles), §5, §6 (all twelve SOD rules), §7 ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` §4, §6, §7

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §4.1 Portal 3, BR-SRM-001,
BR-SRM-011, BR-FSM-002, BR-FSM-003, BR-INV-003, BR-CWM-007, BR-QMS-002, BR-BI-002,
BR-HRM-004, NFR-001, NFR-003 ·
`1000FiX_Services_Company_Profile.md` §Service Infrastructure

**External benchmark**
[SAP Fiori launchpad and role-based spaces](https://help.sap.com/docs/SAP_S4HANA_CLOUD) —
role-scoped entry with task-oriented tiles and overview pages ·
[Microsoft Dynamics 365 Unified Interface app modules](https://learn.microsoft.com/en-us/power-apps/maker/model-driven-apps/) —
role-scoped apps over one shared data model ·
[Odoo 19 web client and OWL 2 framework](https://www.odoo.com/documentation/19.0/developer/reference/frontend.html) ·
[ServiceNow Agent Workspace patterns](https://www.servicenow.com/products/agent-workspace.html) —
single pane with contextual side panels ·
[Enterprise UI design principles 2026](https://hashbyt.com/blog/enterprise-ui-design) ·
[UI/UX design for enterprise web portals](https://www.aixtor.com/blog/ui-ux-web-portal-design/) ·
[Accessible design systems at scale](https://humanmade.com/accessibility/accessible-design-systems-scaling-inclusive-design/) ·
[WCAG 2.1 AA success criteria](https://www.levelaccess.com/blog/wcag-2-1-exploring-new-success-criteria/)

---

*Portal P03 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
