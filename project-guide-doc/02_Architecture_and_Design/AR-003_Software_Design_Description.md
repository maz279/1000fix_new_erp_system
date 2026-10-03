---
id: AR-003
title: Software Design Description (SDD) — Method, Viewpoints and Worked Exemplar
category: 02 — Architecture & Design
code: AR
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Solution Architect
approver: Chief Architect
standards_basis: IEEE 1016-2009 (Software Design Descriptions) · ISO/IEC/IEEE 42010:2022 · Odoo 19 ORM conventions
traces_to: PGD-000 AR-003 · AR-001 §6.4 · AS-01…AS-15 · DM-01…DM-15 · DoD-01…DoD-17
depends_on: AR-001 · AR-007 (module anatomy) · AR-008 (aggregates) · DA-001 (schema)
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 02:05 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# AR-003 — Software Design Description (SDD)

### Category 02 · Code `AR` · IEEE 1016-2009 — Design Descriptions

---

> **Read this before using this document.**
>
> **`AR-003` is not one document; it is a method plus a growing set.** There are 67 modules,
> 16 domain services and 10 applications. A single file describing all of them would be unreadable,
> unreviewable and permanently out of date.
>
> This document establishes: **(a)** the mandatory design-viewpoint set every module SDD must
> contain, **(b)** the production rule that ties SDD authoring to the wave plan, **(c)** the design
> patterns that are decided once and reused rather than re-decided per module, and **(d)** one
> **fully worked exemplar — `SDD-M01`** — so that "conforms to `AR-003`" has a referent rather than
> being a matter of opinion.
>
> Per-module SDDs are issued as `AR-003-M<nn>` and `AR-003-APP<nn>` into
> `02_Architecture_and_Design/SDD/`, one wave ahead of the wave that builds them.

---

## 1. Purpose

This document closes the gap between a requirement and a file of code. Between
`FR-SRM-014` — *"The system shall reserve a spare part against a job card"* — and a developer
opening `cd_service_order/models/service_order.py`, four decisions must already have been made:
which model holds the reservation, what the method contract is, what happens under concurrency, and
what event it emits. None of those is a requirement. All of them are design.

**Why this matters at 67 modules.** Without a design description, two developers implement the same
requirement two incompatible ways, and the incompatibility is discovered in integration testing in a
later wave, when both are in production. The purpose of an SDD is not documentation — it is
**forcing the design decision to happen before the code, once, in a place a reviewer can see it.**

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The mandatory design-viewpoint set (IEEE 1016 §5), tailored to an Odoo-based system |
| 2 | The SDD production rule — what is written, by whom, when, relative to the wave plan |
| 3 | Design patterns decided once for the whole estate (§5) — state machines, reservations, approvals, extensions, concurrency, outbox emission |
| 4 | The design review procedure and its exit criteria |
| 5 | **`SDD-M01`** — a complete worked design for M01 Service Request & Order Management |
| 6 | The design-completeness register across all 67 modules, 16 services and 10 applications |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| System-level structure, views, quality scenarios | `AR-001` | An SDD describes a module; a SAD describes the system |
| The mandatory *anatomy* of a `cd_*` module — directory layout, manifest, inheritance rules | `AR-007` | `AR-007` says how a module is **shaped**; `AR-003` says what it **does** |
| Physical schema, DDL, indexes, constraints | `DA-001` | An SDD states the model and its fields; the schema specification states the physical realisation |
| Aggregate boundaries and invariants | `AR-008` | An SDD *applies* the aggregate model; it does not define it |
| Event catalogue and payload schemas | `AR-009`, `IN-003` | An SDD names the events a module emits; the catalogue is the registry |
| Offline engine internals | `AR-010` | One shared engine; designed once |
| UI layout and screen design | `UX-003`, `UX-004` | An SDD describes behaviour, not pixels |
| Test cases | `QA-003` | Derived *from* the SDD |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Developers** | The primary consumer. This is what you read before writing the module |
| **Solution Architect** | The artefact reviewed at the design gate |
| **QA engineers** | State machines, guards and failure behaviours are the direct source of negative tests |
| **The next maintainer, in 2029** | The record of why the module is shaped this way |
| Implementation vendor | The standard their design deliverables must meet to be accepted |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | Conformance | Departure and rationale |
|---|---|---|---|
| **IEEE 1016-2009** | §5 Design viewpoints | All ten design viewpoints are addressed; §4 maps each to a mandatory SDD section | **Departure:** the *Resource* viewpoint is addressed at system level in `AR-001` §8.6 rather than per module, because in a shared Odoo application tier a single module does not own resources. Stated here rather than silently omitted |
| IEEE 1016-2009 | §4 Design description contents | Identification, stakeholders, design concerns, viewpoints, views, rationale | Full |
| IEEE 1016-2009 | §6 Conformance | This document conforms as an SDD *organisation*; each `AR-003-M<nn>` conforms as an SDD *instance* | The standard permits a design description to be distributed across documents provided the set is identified. §7 is that identification |
| ISO/IEC/IEEE 42010:2022 | Viewpoint declaration | §4 declares each design viewpoint with concerns and model kinds | Full |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| All 67 module specifications, §5 (requirements), §8 (state model), §9 (business rules), §10 (entities), §11 (automations), §12 (interfaces) | **The input to every SDD.** A module specification with a complete §8–§12 makes its SDD substantially derivable |
| `../../1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md` | The 19-section structure every specification conforms to — which is why a uniform SDD method is possible |
| `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02` §1, §3 | DM-01…DM-15 modelling standards; M01's 26 entities |
| `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md` | Rule classification H / A / S / C |
| `../../primary-doc/…Technology_Stack_Specification.md` §8.2, §8.3 | The 248-item CD register and standards L5-01…L5-10 |
| `M01_Service_Request_and_Order_Management.md` §8, §9 | The state model and business rules realised in §6 |

### 2.3 Audit findings this document contributes to closing

| Finding | How |
|---|---|
| `PGD-000` §0.2 — *"2,930 requirements and zero design specifications"* | Establishes the method and issues the first design specification |
| `H-03` Two incompatible CD registers | §3.3 binds each SDD to a CD identifier and refuses to accept an SDD citing an unissued one — making `BE-005` a hard prerequisite rather than an aspiration |
| `EO-02` `05-05` carries no business rule for M40 or M42 | §4.9 makes the business-rule view mandatory, so the omission fails the design gate rather than reaching build |
| `TS-01` Coverage has three denominators | §7 states the design-completeness denominator explicitly (67 + 16 + 10 = **93 design units**) and counts against it |

---

## 3. The SDD Production Rule

### 3.1 What is written, and when

> **The rule: a module's SDD is issued and design-gated one wave before the wave that builds it.**

Not all at once, and not just-in-time. Both extremes fail:

| Approach | Why it fails |
|---|---|
| Write all 93 SDDs up front | ~18–24 months of design before the first line of code; most would be stale before use; the estimate for it is in no plan |
| Write each SDD at the start of its own sprint | Design and build compress into the same box; the design gate becomes a formality; cross-module contracts are discovered late |
| **One wave ahead** | Design is reviewable while the previous wave builds; cross-module contracts surface a wave early, when they are still cheap; the design author is available to the builder |

### 3.2 Production schedule

| SDD set | Design wave | Build wave | Units |
|---|:--:|:--:|---:|
| Platform: M28, M29, M30, M33, M37 + CD-233 residency, CD-234 notification | **W0** | W1 | 7 |
| Service core: M01, M04, M17 + APP-05 | W0 | W1 | 4 |
| Field: M02, M31, M15, M10, M64 + APP-01 | W1 | W2 | 6 |
| Money & movement: M19, M20, M52, M50, M11, M36, M03, M16, M41, M24, M63 + APP-02, CD-238…241 | W2 | W3 | 17 |
| Agreements: M08, M09, M39, M51, M53, M27, M32, M34, M25, M62, M42 + APP-06…08, CD-242, CD-243, CD-248 | W3 | W4 | 17 |
| People & MSP: M21, M55, M56, M57, M22, M23, M05, M45, M46, M49 + APP-03, CD-244 | W4 | W5 | 12 |
| New lines: M13, M14, M06, M26, M43, M44, M54, M58, M59, M60, M61, M66 + APP-04, CD-245, CD-247 | W5 | W6 | 15 |
| Marketplace: M38, M12, M40, M47, M67 + APP-09, APP-10 | W6 | W7 | 7 |
| Intelligence: M48, M18 + CD-246 | W7 | W8 | 3 |
| Expansion: M65 | W8 | W9 | 1 |
| | | **Total** | **89** |

*(89 rather than 93: M01, M11, M17, M25, M26, M53, M62 span two waves and their SDD is issued once at
the earlier wave and amended at the later one. `AR-006` §6 holds the split-wave register.)*

### 3.3 Entry conditions — an SDD may not begin until all four are true

| # | Condition | Why |
|---|---|---|
| **E-01** | The module specification exists, with §8 state model, §9 business rules, §10 entities and §12 interfaces complete | An SDD derived from an incomplete specification invents requirements |
| **E-02** | The module's **CD identifiers are issued by `BE-005`**, not provisional | `H-03`: two incompatible CD registers exist and 48 identifiers collide. **A build backlog item created from a provisional identifier is a defect** — `_MODULE_TEMPLATE` §16.2 says so explicitly |
| **E-03** | `AR-005` has adjudicated every boundary this module contests | Designing a capability another module also claims produces duplicate implementation |
| **E-04** | `AR-008` has fixed the aggregates this module touches, and `DA-001` the schema for entities it owns | An SDD cannot define its own aggregate boundary |

> **E-02 is currently unsatisfiable.** `BE-005` does not exist; the CD register is split between
> `02-05` §5.2 (138 items, 30 modules) and the Technology Stack Specification §8.2 (248 items, 67
> modules), and the latter is unratified. **No SDD may be design-gated until `BE-005` is issued.**
> This is the single hardest dependency in Category 02 and is raised as `PGD-A3-07`.

### 3.4 Exit criteria — the design gate

| # | Criterion | Assessor |
|---|---|---|
| X-01 | All ten design viewpoints (§4) present; where one does not apply, the heading is kept and the reason stated in one line | Solution Architect |
| X-02 | Every P0 and P1 requirement in the module's §5 maps to at least one design element | Solution Architect |
| X-03 | Every state transition in the module's §8 has a guard, an actor and a declared side effect | Solution Architect |
| X-04 | Every **H**-class business rule is enforced at the **model layer**, and its negative test is named | QA lead |
| X-05 | Every published event names its aggregate, its payload fields and at least one consumer | Chief Architect |
| X-06 | Every automation names a **failure behaviour**. A blank is a gate failure, not a to-do | Solution Architect |
| X-07 | Concurrency behaviour is stated for every contended resource the module touches | Solution Architect |
| X-08 | Every referenced entity appears **verbatim** in its owning module's §10.1 | Automated check |
| X-09 | No design element requires reading another module's tables (AS-01) | Automated check + review |
| X-10 | Design decisions that diverge from §5's estate patterns are recorded as ADRs, not made silently | Chief Architect |

> **X-08 is not a formality.** The August 2026 audit found **255 entity references across the estate
> naming entities their declared owner does not define** — the single largest technical defect found.
> An SDD that references a non-existent entity produces code against a table that will never exist.

---

## 4. Design Viewpoints — the mandatory SDD structure

IEEE 1016-2009 §5 defines design viewpoints. Every `AR-003-M<nn>` contains these ten sections, in
this order, with these numbers. **Do not renumber, merge or omit.**

| § | Viewpoint (IEEE 1016) | What it must contain | Concerns addressed |
|:--:|---|---|---|
| **1** | **Context** | Module identity, CD allocation, boundary restatement, upstream/downstream actors, the requirements it realises | What is this, and where does it sit |
| **2** | **Composition** | Model inventory: every `fix.*` model, its base (`_name` or `_inherit`), its purpose, its owning CD item | What are the parts |
| **3** | **Logical** | Per model: fields with type, required/computed/stored/related, selection domains, `ondelete` policy, constraints. Class relationships | What is the structure |
| **4** | **Dependency** | Modules and services depended on, and the **mechanism** for each — published API, event projection or shared kernel. **Never a table** | What must exist first |
| **5** | **Information** | Persistence: tables, ownership, data classification S0–S3, residency classification, retention class, index and partition needs referred to `DA-001` | Where does the data live, and how sensitive is it |
| **6** | **Interface** | Public method contracts — signature, preconditions, postconditions, exceptions, idempotency; REST endpoints; consumed interfaces | What may be called, and what does it promise |
| **7** | **Structure** | Layering within the module: models / services / wizards / controllers / reports, and the rule that keeps business logic out of the last two (AS-09) | How is the module internally organised |
| **8** | **Interaction** | Sequence traces for the module's significant flows, including the failure branches | How do the parts collaborate |
| **9** | **State dynamics** | The state machine: states, transitions, guards, actors, side effects, and the **transition map declared in one place** (AS-06) | How does it behave over time |
| **10** | **Design rationale** | Options considered and rejected; patterns applied from §5; deviations recorded as ADRs | Why is it like this |

*Plus two mandatory annexes:* **A — Business rule realisation** (each `BRU-` rule → enforcement point
→ negative test) and **B — Automations** (each `AUT-` → trigger → action → **failure behaviour**).

---

## 5. Estate Design Patterns — decided once, applied everywhere

**These exist so that 67 SDDs do not make 67 different decisions about the same problem.** A module
that deviates records an ADR; a module that deviates silently fails gate criterion X-10.

### 5.1 DP-01 — Explicit state machine

**Problem.** State scattered across booleans and conditionals is untestable and unauditable.

**Pattern.** One `state = fields.Selection(...)` per aggregate root. The **transition map is a single
declared structure** on the model — `_TRANSITIONS = {from: {to: guard_method}}` — and **all** state
change flows through one `_do_transition(target)` method that: checks the guard, writes the state,
writes the outbox row and posts to the chatter, **in one transaction**.

**Why it is worth the ceremony.** AS-06 requires the transition map to be declared in one place. More
practically: a state machine expressed as scattered `if` statements cannot be exhaustively tested,
and an ERP's audit value is precisely its ability to answer *"how did this record get into this
state?"*

**Forbidden.** `record.state = 'done'` anywhere outside `_do_transition`. Enforced by `AR-012` `FF-06`.

### 5.2 DP-02 — Business-line extension by 1:1 composition

**Problem.** Nine business lines share the service order (`AR-001` §6.6).

**Pattern.** Thin core (`fix.service.order`) + one-to-one extension model per line
(`fix.service.order.rental`, `.msp`, `.data`, `.marketplace`), each **owned, versioned and deployed
by that line's module**. The core knows nothing about the extensions; the extensions know the core.

**Forbidden.** Adding a line-specific field to the core model. A tenth business line adds a module,
not a core migration.

### 5.3 DP-03 — Reservation and concurrency on contended resources

**Problem.** Two technicians consume the last part; two dispatchers assign the same technician; two
sessions approve the same estimate.

**Pattern**, in order of preference:

| Situation | Mechanism |
|---|---|
| Stock, van stock, consignment stock | **Odoo reservation** via `stock.move` + `fix.stock.reservation`, `SELECT … FOR UPDATE` on the quant |
| Assignment (technician, bench, rider, courier slot) | **Optimistic concurrency** — version check on read-modify-write; loser is re-scored, not failed |
| Financial posting, sequence allocation | **Pessimistic row lock** on the sequence or the period |
| Cross-service coordination (settlement, DSR erasure) | **Saga with compensating actions**, never a distributed transaction |
| Anything reachable from an offline client | **Idempotency by client command UUID**, server-side ledger of processed UUIDs |

**Every SDD must state, in §6, which of these applies to every contended resource it touches.** A
blank is a gate failure, because "we did not think about concurrency" is the most common source of
defects that only appear under production load.

### 5.4 DP-04 — Outbox emission

**Pattern.** Every state-changing method writes its domain event **into the same transaction** via
the shared `emit_event()` helper from CD-125. Never after commit. Never from a `@api.onchange`.
Never from a view.

**The rule that makes it verifiable:** an SDD's §9 transition table and its §6 event list must agree.
A transition with no event, or an event with no transition, is a design defect that CI catches
(`AR-012` `FF-04`).

### 5.5 DP-05 — Approval

**Problem.** Nineteen modules need an approval step, and nineteen bespoke approval implementations is
a maintenance disaster and a segregation-of-duties hole.

**Pattern.** One polymorphic `fix.approval.request` (model, `res_id`, approver, level, state,
decision, reason) plus per-module **policy configuration**, never per-module approval code. SoD is
evaluated by CD-132 at role-assignment time (`AR-001` §10 QAS-08).

### 5.6 DP-06 — Odoo extension

**Pattern.** In strict order of preference:

1. **Configuration** — no code.
2. **`_inherit` an existing model** and add fields or override methods with `super()`.
3. **New `fix.*` model** with a many-to-one to the Odoo model.
4. **Fork an OCA module** — requires **named Design Authority approval** and an entry in the fork register.

**(4) is the upgrade-safety cliff.** One fork done casually makes the Odoo 20 upgrade a manual merge
across 140+ modules (`AR-001` QAS-11, `TR-04`). `AR-007` makes this mechanically checkable.

### 5.7 DP-07 — Residency-classified field access

**Pattern.** A model **never** declares a residency-classified field directly. It declares a
**resident key** and reads the value through the residency service (CD-233). Every read is logged;
human reads require step-up.

**Forbidden, absolutely:** a residency-classified value in a regional table, a cache, a log line, a
search index, a report or a migration script (`AR-001` LB-08).

### 5.8 DP-08 — Money

`Monetary` field with an explicit `currency_id`, decimal arithmetic, **never float** (AS-10, DI-01).
Rounding is applied once, at the declared point, and the point is stated in the SDD. **100% unit-test
coverage on financial and tax calculation paths** (DoD-03).

### 5.9 DP-09 — Multi-dimensional context

Every transactional model carries `company_id` and `operating_unit_id`, and where relevant `zone_id`,
`cost_center_id`, `business_line_id` (DM-03, AS-03) — **from Wave 1, even while one entity operates**.
This is `AR-001` QAS-03: the alternative is retrofitting a dimension across 1,335 entities of live data.

### 5.10 DP-10 — Soft delete

Business records are archived (`active = False`), never hard-deleted (DM-06, DI-08). **The one
exception is PDPA erasure**, which is a saga with an approved, logged procedure (CD-248) — and which
is why erasure is architecturally hard, not a `DELETE`.

---

## 6. Worked Exemplar — `SDD-M01` Service Request & Order Management

**Why M01.** It is P0, W1–W2, carries 88 requirements and 26 entities, is the most-referenced object
in the estate, and exercises eight of the ten design patterns. If the method works here, it works.

*This is an abridged exemplar showing every viewpoint at demonstrative depth. The issued
`AR-003-M01` carries all 88 requirements and all 26 entities at this depth.*

### 6.1 Context viewpoint

| Attribute | Value |
|---|---|
| Module | M01 · `SRM` · Category A · P0 · W1 (core) + W2 (complete) |
| CD allocation | CD-001…008 — `cd_service_order`, `cd_diagnostic`, `cd_estimate`, `cd_qc`, `cd_sla`, `cd_rework`, `cd_workshop`, `cd_service_ext` **⚠ provisional pending `BE-005` (E-02)** |
| Requirements realised | `FR-SRM-001`…`FR-SRM-088` |
| Layer allocation | L1 Odoo `repair`, `project`, `calendar` · L2 `OCA/field-service`, `OCA/helpdesk` · L5 CD-001…008 |
| Owns | The service order aggregate and its lifecycle |
| Does not own | Dispatch and assignment (**M02**) · parts and stock (**M15**) · pricing (**M11**) · estimate authoring (**M36**) · invoicing (**M20**) · customer master (**M33**) · device registry (**M17**) · workshop bench (**M31**) |

### 6.2 Composition viewpoint — selected models

| Model | Base | Purpose | CD |
|---|---|---|---|
| `fix.service.order` | `_name` (new) | **Aggregate root.** The unit of customer promise | CD-001 |
| `fix.service.order.rental` / `.msp` / `.data` / `.marketplace` | `_name`, 1:1 to root | Business-line extension (DP-02) — **each owned by M13 / M05 / M06 / M12, not M01** | CD-059 / 024 / 030 / 052 |
| `fix.work.order` | `_name` | Unit of technician execution; N:1 to root | CD-001 |
| `fix.work.order.task` | `_name` | Task within a work order | CD-001 |
| `fix.diagnostic.template` / `.result` | `_name` | Guided diagnostic tree and its answers | CD-002 |
| `fix.fault.code` | `_name` | Controlled fault taxonomy | CD-002 |
| `fix.estimate` / `.line` | `_name` | Priced estimate; **authored by M36, held here** | CD-003 |
| `fix.qc.checklist` / `.result` | `_name` | Quality gate | CD-004 |
| `fix.sla.policy` / `.clock` / `fix.escalation.rule` | `_name` | SLA measurement and escalation | CD-005 |
| `fix.hold.reason` | `_name` | Controlled hold reasons; declares SLA suspension | CD-005 |
| `fix.rework.link` | `_name` | Links an order to the order it reworks | CD-006 |
| `fix.approval.request` | shared (DP-05) | Polymorphic approval | CD-001 |
| `fix.custody.event` | shared with M03 | Chain-of-custody record | CD-017 |
| `fix.service.report` | `_name` | Customer-facing service report | CD-008 |
| `fix.repair.warranty` | `_name` | The repair warranty this order creates | CD-008 |

### 6.3 Logical viewpoint — `fix.service.order` (selected fields)

| Field | Type | Notes |
|---|---|---|
| `name` | Char, required, readonly | Branch- and business-line-aware sequence (DM-11) |
| `partner_id` | Many2one `res.partner`, required, `ondelete='restrict'` | **M33-owned.** Restrict, never cascade — an order outlives a customer-record merge |
| `asset_id` | Many2one `fix.asset`, required, `ondelete='restrict'` | **M17-owned.** Required by `BRU-SRM-01` |
| `order_type` | Selection `[warranty, paid, amc, msp, data, rental, tradein, marketplace, recycling]`, required | Drives which 1:1 extension applies (DP-02) |
| `channel` | Selection `[walkin, portal, app, phone, chat, whatsapp, corporate, marketplace, field]` | Intake channel; a KPI dimension |
| `state` | Selection, required, default `draft` | See §6.9. **Written only by `_do_transition`** (DP-01) |
| `priority` | Selection `[low, normal, high, critical]` | Feeds SLA policy selection |
| `company_id`, `operating_unit_id`, `zone_id`, `cost_center_id`, `business_line_id` | Many2one, required | DP-09 — from W1 |
| `sla_policy_id` | Many2one `fix.sla.policy`, computed **stored** | Computed at `received`, then frozen. A policy change must not silently re-baseline a live clock |
| `promised_date` | Datetime, computed stored | Derived from the SLA clock; **customer-visible, therefore never recomputed after issue** |
| `total_cost`, `total_price` | Monetary with `currency_id` | DP-08 |
| `hold_reason_id` | Many2one `fix.hold.reason` | Non-null only in `on_hold` — SQL constraint |
| `rework_of_id` | Many2one self, computed | `BRU-SRM-06`: same device + fault category within 30 days |

**Constraints declared at the database level (DI-03):**

| Constraint | Statement |
|---|---|
| `chk_hold_reason` | `state = 'on_hold'` ⟺ `hold_reason_id IS NOT NULL` |
| `chk_monetary_nonneg` | `total_price >= 0 AND total_cost >= 0` |
| `uniq_name_company` | `(name, company_id)` unique |
| `fk_partner_restrict`, `fk_asset_restrict` | `ON DELETE RESTRICT` |

### 6.4 Dependency viewpoint

| Depends on | What | **Mechanism** |
|---|---|---|
| M33 CPM | Customer identity | Shared kernel (`res.partner`) |
| M17 AST | Device registry, warranty status | Live read via published API |
| M08 CTR | Entitlement check at intake | Synchronous API call — **must answer or the order cannot be typed** |
| M11 PRC / M36 QTE | Estimate pricing and authoring | API call; estimate held here |
| M15 INV | Part reservation and consumption | API call (reservation), event (`part.consumed`) |
| M02 FSM | Assignment | **Event out, event in.** M01 never assigns |
| M20 ARB | Invoice raising | Event `service_order.delivered` → billable event |
| M23 QMS | Quality signals | Event out only |
| M28 IPF | Outbox, gateway | Shared platform |
| M29 SEC | Every authorisation decision | Delegated (LB-05) |

**No dependency is on a table.** Nine dependencies, nine declared mechanisms — AS-01 verified.

### 6.5 Information viewpoint

| Table | Classification | Residency | Retention |
|---|---|---|---|
| `fix_service_order` | **S1 Internal**; `complaint_text` may contain S2 | None | Statutory schedule (`LG-009`) |
| `fix_work_order`, `_task` | S1 | None | With parent |
| `fix_diagnostic_result` | S1 | None | With parent |
| `fix_estimate`, `_line` | **S2 Confidential** — margin visible | None | 7 years (financial) |
| `fix_qc_result` | S1 + evidence attachments | None | ISO 9001 evidence period |
| `fix_custody_event` | S1 + GPS + party identity | None | Evidence period |
| `fix_service_report` | S1; customer-visible | None | With parent |

**Notably: M01 owns no residency-classified field.** Customer identifiers live in M33 and are reached
through the residency service. This is DP-07 working correctly — the highest-volume table in the
system carries no Z4 obligation. Index and partition design is `DA-001`'s; the drivers are in
`05-02` §11 (`(operating_unit_id, state, create_date DESC)` for the branch board;
`(asset_id, create_date DESC)` for rework detection; GIN on complaint text for Bengali search).

### 6.6 Interface viewpoint — selected method contracts

```
action_confirm(self) -> bool
  Pre :  state == 'draft'; partner_id and asset_id set; entitlement evaluated
  Post:  state == 'received'; sla_policy_id and promised_date computed and frozen;
         outbox row 'service_order.created'
  Raise: ValidationError if BRU-SRM-01/02/03 fails
  Idem : Yes — returns True without side effect if already 'received'

action_approve_estimate(self, decision, approver_id, reason=None) -> bool
  Pre :  state == 'awaiting_approval'; a current estimate exists
  Post:  approved -> state 'approved' + outbox 'service_order.approved'
         declined -> state 'declined' + outbox 'service_order.cancelled'
  Raise: AccessError if approver lacks authority for the estimate value
         ValidationError if BRU-SRM-07 (> BDT 5,000 requires documented approval) unmet
  Idem : Yes, by (order, estimate_version, decision)
  Concurrency: optimistic — estimate_version checked; stale decision rejected with a
               user-visible "the estimate changed" message, never silently applied

action_hold(self, reason_id) -> bool
  Pre :  state in ACTIVE_STATES; reason_id is an active fix.hold.reason
  Post:  state 'on_hold'; if reason.suspends_sla then sla_clock.pause();
         outbox 'service_order.on_hold'
  Note:  SLA suspension is a property of the REASON, not of the hold. A hold for a
         cause within our control must not stop our own clock.
```

**REST surface** (`/api/v1/customer/*`, `/api/v1/ops/*`): create, read, status, reschedule, cancel,
estimate decision. All state-changing calls require `Idempotency-Key` (API-07) and are scoped
server-side (API-10).

### 6.7 Structure viewpoint

```
cd_service_order/
├── models/        service_order.py · work_order.py · sla.py · hold_reason.py · rework.py
│                  ALL business logic lives here (AS-09)
├── services/      sla_calculator.py · rework_detector.py   ← pure, unit-testable, no ORM writes
├── wizards/       intake_wizard.py · bulk_hold_wizard.py    ← orchestration only
├── controllers/   api_v1.py                                 ← marshalling only, ZERO logic
├── views/ · data/ · security/ · tests/ · i18n/ (bn_BD complete before acceptance)
└── README.md · runbook.md · openapi.yaml                    ← L5-01, DoD-06, DoD-11
```

**The single most-violated rule, stated explicitly:** `controllers/` marshals and delegates. A
business rule in a controller is enforced for API callers and not for UI users — which is precisely
the defect DoD-04's *"negative-tested through both UI and API"* exists to catch.

### 6.8 Interaction viewpoint — intake to release

```
Agent/Portal    M01              M33      M17      M08       M11/M36   Outbox    M02
    │            │                │        │        │           │         │        │
    │─create────►│                │        │        │           │         │        │
    │            │─resolve party─►│        │        │           │         │        │
    │            │─resolve device─────────►│        │           │         │        │
    │            │   └─ not found → BRU-SRM-01 blocks; register device inline       │
    │            │─entitlement check──────────────►│           │         │        │
    │            │   └─ warranty inactive → BRU-SRM-02 blocks warranty typing       │
    │            │─select SLA policy · compute promised_date (FROZEN)                │
    │            │─rework check: same asset + fault ≤ 30 d → BRU-SRM-06 flag         │
    │            │═══ TRANSACTION: state='received' + outbox row ═══════►│         │
    │◄─order id + promised date                                          │─created─►│
    │            │                                                        │         │
    │            │  [diagnosis → estimate: M36 authors, M11 prices]      │         │
    │            │─issue estimate ─────────────────────────────►│        │         │
    │            │═══ state='awaiting_approval' + outbox ═══════════════►│         │
    │─decision──►│  optimistic check on estimate_version                  │         │
    │            │═══ state='approved' + outbox ═══════════════════════►│─approved►│
```

**Failure branches that must be designed, not discovered:** M08 entitlement unavailable → the order
is created as `paid` with a flag and a reconciliation task, **never blocked** (a customer at a counter
cannot wait for a service to recover); M17 device unknown → inline registration; duplicate submit →
`Idempotency-Key` returns the original order.

### 6.9 State-dynamics viewpoint

States and transitions are taken **verbatim** from `M01` §8 — an SDD may not invent a state.

```
DRAFT ─confirm─► RECEIVED ─assign─► DIAGNOSING ─complete─► ESTIMATE_PENDING
   ─issue─► AWAITING_APPROVAL ─approve─► APPROVED ─release─► IN_PROGRESS
                    └─reject─► DECLINED ─► RETURN
   (warranty/AMC: RECEIVED ─────────────────────────────────► IN_PROGRESS)
IN_PROGRESS ⇄ ON_HOLD (SLA clock suspended iff reason.suspends_sla)
IN_PROGRESS ─complete─► QC ─fail─► IN_PROGRESS
                          └─pass─► READY ─handover─► DELIVERED ─billable─► INVOICED
                                                        ─settled/claimed─► CLOSED ─► ARCHIVED
CLOSED ─reopen within repair-warranty window─► RECEIVED  (auto-flagged rework)
Terminal exceptions: CANCELLED · UNREPAIRABLE · ABANDONED
```

| From | To | Guard | Actor | **Event emitted** |
|---|---|---|---|---|
| draft | received | Customer and device identified; entitlement evaluated | Agent / portal / API | `service_order.created` |
| received | diagnosing | Assigned to technician or workshop | Dispatcher | — |
| diagnosing | estimate_pending | Diagnostic complete; fault code assigned | Technician | `service_order.classified` |
| estimate_pending | awaiting_approval | Estimate issued to customer | System | `service_order.estimated` |
| awaiting_approval | approved | Customer decision + internal threshold approval (`BRU-SRM-07`) | Customer + approver | `service_order.approved` |
| awaiting_approval | declined | Rejection recorded with reason | Customer | `service_order.cancelled` |
| approved / received | in_progress | Required parts reserved or confirmed available | System | — |
| any active | on_hold | Approved hold reason selected | Technician / dispatcher | `service_order.on_hold` |
| in_progress | qc | Work complete; time and parts posted | Technician | — |
| **qc** | **ready** | **Quality checklist passed — hard gate `BRU-SRM-04`** | QC inspector | — |
| ready | delivered | Identity verified; accessories confirmed; signature captured | Agent / technician / rider | `service_order.completed` |
| delivered | invoiced | Billable event accepted by M20 (`BRU-SRM-05`) | System | — |
| invoiced | closed | Payment settled, credit applied, or claim raised | System | `service_order.closed` |
| closed | received | Reopen within repair-warranty window | Agent / manager | `rework.detected` |

**All transitions flow through `_do_transition` (DP-01). No other code writes `state`.**

### 6.10 Design rationale

| Decision | Options | Chosen | Why |
|---|---|---|---|
| Order/work-order split | Single object; **two-level**; three-level | **Two-level** | A customer promise (one order) frequently needs several technician visits. One object cannot carry both without ambiguity about what "complete" means |
| SLA policy timing | Live lookup; **frozen at `received`** | **Frozen** | `promised_date` is customer-visible and often contractual. A policy edit must not silently re-baseline live orders |
| SLA suspension | Property of the hold action; **property of the reason** | **Property of the reason** | A hold for a cause within our control must not stop our own clock — otherwise the SLA measures our patience, not our performance |
| Rework detection | Manual flag; **automatic within 30 days**; ML | **Automatic** (`BRU-SRM-06`, class **C**) | Manual flagging under-reports systematically, and rework rate is a headline quality KPI |
| Entitlement unavailable at intake | Block; **create as paid + reconcile**; queue | **Create as paid + reconcile** | A customer at a counter cannot wait for a service to recover. Availability beats precision at the intake point, and the reconciliation task makes it recoverable |

**Annex A — business rule realisation** (extract):

| Rule | Class | Enforcement point | Negative test |
|---|:--:|---|---|
| `BRU-SRM-01` device required | **H** | `_check_device` constraint on `fix.service.order` | Create without `asset_id` via **UI and API** → both rejected |
| `BRU-SRM-02` warranty active | **H** | Guard on `action_confirm` when `order_type='warranty'` | Warranty order on an expired device → rejected |
| `BRU-SRM-04` QC gate | **H** | Guard on `qc → ready` | Force `ready` with a failed checklist → rejected |
| `BRU-SRM-05` invoice only when delivered | **H** | Guard on billable-event emission | Billable event from `in_progress` → rejected |
| `BRU-SRM-06` rework within 30 days | **C** | `rework_detector` service, computed stored | Second order, same asset and fault, day 29 → flagged; day 31 → not |
| `BRU-SRM-07` estimate > BDT 5,000 | **H** | Guard on `awaiting_approval → approved` | Approve BDT 6,000 estimate with no documented approval → rejected |

---

## 7. Design Completeness Register

**The denominator, stated so that coverage has one meaning** (closing `TS-01`'s three-denominator
problem for design):

| Design unit class | Count | Basis |
|---|---:|---|
| Module SDDs (`AR-003-M01`…`M67`) | 67 | Counted from disk 2026-08-18 02:05 — 67 of 67 specifications exist |
| Domain service SDDs (`AR-003-CD233`…`CD248`) | 16 | Technology Stack Specification §8.2 Block 3 |
| Application SDDs (`AR-003-APP01`…`APP10`) | 10 | Ibid., APP register |
| **Total design units** | **93** | |

| Status | Count | Detail |
|---|---:|---|
| Issued | **1** | `SDD-M01` (this document §6, exemplar depth; full issue at W0) |
| Design-gated | 0 | **Blocked on `BE-005`** (E-02) |
| Not started | 92 | Scheduled per §3.2 |

> **Design coverage is 1 of 93 (1.1%), measured 2026-08-18.** Stated plainly because the register's
> §0.5 counts `AR-003` as a single ⛔ row, which understates the work by roughly two orders of
> magnitude. The **effort to produce 93 design units is not in `GV-004` or `CO-005`** — this
> materially extends open finding `PGD-A1-05`, and is raised as `PGD-A3-08`.

---

## 8. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-A3-01 | SDD granularity | One document; per category; **per module/service/app** | **Per design unit** | 93 reviewable documents beat one unreviewable one | 93 units to schedule, hence §3.2 |
| D-A3-02 | Authoring timing | All up front; just-in-time; **one wave ahead** | **One wave ahead** | Cross-module contracts surface a wave early, while still cheap | The SDD author must be available during the build wave |
| D-A3-03 | Patterns | Per-module; **estate-wide with ADR for deviation** | **Estate-wide (§5)** | Ten patterns decided once removes ~670 repeated decisions | A deviation is visible, because it needs an ADR |
| D-A3-04 | Exemplar | None; abstract template; **fully worked M01** | **Worked M01** | "Conforms to `AR-003`" needs a referent, or it is opinion | M01's SDD must be kept current as the reference |

---

## 9. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | **When is `BE-005` (CD master register) issued?** No SDD can be design-gated until it is (E-02) | CTO / `BE-005` owner | **W0 — blocking** | All 93 design units |
| Q-02 | **Who authors 93 SDDs, and is the effort funded?** Not in `GV-004` or `CO-005` | Programme Director | W0 | The whole production schedule |
| Q-03 | Is `AR-003-M<nn>` a vendor deliverable or a 1000FiX deliverable? | CTO / `CO-003` owner | Before contract award | Statement of Work; acceptance criteria |
| Q-04 | Do the 12 portal specifications need SDDs, or are they covered by `APP-05`…`APP-10` + `UX-003`? | Chief Architect | W1 | Denominator in §7 |

---

## 10. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | All ten IEEE 1016-2009 design viewpoints are mapped to mandatory SDD sections | §4 |
| AC-02 | Entry and exit conditions are stated and testable | §3.3, §3.4 |
| AC-03 | Estate-wide design patterns are decided, with deviation requiring an ADR | §5 — 10 patterns |
| AC-04 | A complete worked exemplar exists covering all ten viewpoints | §6 |
| AC-05 | The design-completeness denominator is stated and counted | §7 — 93 units |
| AC-06 | Every open question has an owner and a needed-by date | §9 |
| AC-07 | The exemplar's state model and business rules are taken **verbatim** from the module specification, not invented | §6.9 vs `M01` §8, §9 |

**Definition of done.** Complete when every criterion is met, `PGD-000`'s `AR-003` row is updated
with a fresh enumeration timestamp, and the Chief Architect has signed. **`AR-003` reaches ✅ only
when the design-completeness register in §7 shows all 93 units issued** — that is, at the end of
Wave 8. Until then its status is ◐ against a stated and counted denominator, which is materially
more honest than a binary status on a document that is inherently incremental.

---

## 11. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `AR-001` §6.4 | Component structure this design realises |
| Upstream | `AR-005`, `AR-006` | Boundary and sequence — entry conditions E-03 |
| Upstream | `AR-007` | Module anatomy an SDD's §7 must conform to |
| Upstream | `AR-008`, `DA-001` | Aggregates and schema — entry condition E-04 |
| Upstream | **`BE-005`** | **CD identifiers — entry condition E-02, currently unsatisfiable** |
| Downstream | `QA-003` | Test cases derived from §9 state machines and Annex A rules |
| Downstream | `AR-012` | Fitness functions `FF-04`, `FF-06`, `FF-13` enforce DP-01 and DP-04 |
| Downstream | `IN-002` | Endpoint contracts refine §6 interface viewpoints |
| Lateral | `../../1000fix_ERP_Module/03_Modules/**/M*.md` §8, §9, §10, §12 | The direct input to every SDD |

---

## 12. References

**Within this repository**
`../PGD-000_*.md` · `./_CATEGORY_OVERVIEW.md` · `./AR-001`, `./AR-005`, `./AR-006`, `./AR-007`,
`./AR-008`, `./AR-009`, `./AR-010`, `./AR-012` · `../_AUDIT/PGD-AUDIT-003_*.md`

**Workspace**
`../../1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md` ·
`../../1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md` §5, §8, §9, §10, §12 ·
`.../05_Cross_Cutting_Specifications/05-02` §1, §3, §11, `05-05` ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §8.2, §8.3, §18.6

**External standards**

| Standard | Version | Verified |
|---|---|---|
| IEEE 1016 — Software Design Descriptions | 2009 | 2026-08-18 |
| ISO/IEC/IEEE 42010 | 2022 | 2026-08-18 |
| Odoo 19.0 ORM and inheritance model | 19.0 (released 18 Sept 2025) | 2026-08-18 |

---

## 13. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Establishes the SDD method, ten estate design patterns and the `SDD-M01` exemplar. States the 93-unit denominator. Raises `PGD-A3-07` (`BE-005` blocks all design gates) and `PGD-A3-08` (93 design units unfunded) | *Pending — Chief Architect* |

---

*`AR-003` · Category 02 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
