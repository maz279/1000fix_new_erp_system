---
id: RQ-001
title: Software Requirements Specification
category: 01 — Requirements Engineering
code: RQ
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Lead Business Analyst / Requirements Manager
approver: ERP Design Authority, endorsed by the ERP Steering Committee
standards_basis: ISO/IEC/IEEE 29148:2018 §9.6 (SRS content) · §5.2.4–5.2.8 (requirement construct, characteristics, language criteria, attributes) · Annex C (tailoring) · ISO/IEC 25010:2023
traces_to: PGD-000 §2.1 item 1 · audit TS-01 (three coverage denominators) · audit C-02 (M31 outside traceability) · audit AP-02 (NFR double-allocation) · RFP §17 evaluation basis · CO-003 deliverable acceptance
depends_on: RR-002 (identifier convention — not yet written; interim allocation recorded in §3.10.6) · GV-006 (scope baseline control — not yet written) · RQ-005 (requirements management plan — issued with this document)
verified_on: 2026-08-18
priority: P0
needed_by: Now
enumerated_on: 2026-08-18 02:15 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# RQ-001 — Software Requirements Specification
# 1000FiX ERP System & Portal Suite v2.0

### Category 01 · Code `RQ` · ISO/IEC/IEEE 29148:2018 §9.6

---

> **Before reading, read this.**
>
> This document does **not** restate the 3,347 requirement rows held in
> `../../1000fix_ERP_Module/`. Under boundary rule `PG-02` and the cross-repository rule in
> `FOLDER_STRUCTURE.md` §9, the module specifications remain the authority on *what the system
> does*. Copying them here would create a second population that immediately diverges — the exact
> defect recorded as audit `H-03` for the CD register and as `PGD-A1-02` for the register's own
> summary table.
>
> This document is the **specification of the requirement set**: it fixes the construct every
> requirement must take, the attributes every requirement must carry, the verification method
> every requirement must declare, the single denominator against which coverage is measured, and
> the procedure by which the 3,347 existing rows become conforming requirements. It additionally
> carries the **programme-level requirements that no module owns** (`SWR-001` … `SWR-042`, §3.12),
> which is the population that is genuinely absent rather than merely non-conforming.
>
> Every figure in this document was counted from the filesystem at **2026-08-18 02:15 (+06)**
> under rules `PG-03` and `PG-M11`. Where a figure differs from one published elsewhere in the
> workspace, the difference is stated, not smoothed.

---

## 1. Purpose

The programme can describe what it wants and cannot yet state what it is buying. A Business
Requirements Document explains why the system is needed; a User Requirements Document explains
what users want to achieve; 67 module specifications explain, feature by feature, what each part
of the system should do. None of them is a specification a vendor can price against, a developer
can implement without asking a second question, or a tester can derive a pass/fail from. This
document closes that gap: it states, in the form the international standard requires, exactly
what the 1000FiX ERP software shall do, how each statement will be proved, and what "the
requirements are complete" means as a testable claim rather than an opinion.

It unblocks four decisions that are currently unmakeable: what the implementation vendor is
contractually obliged to deliver (`CO-003`), what the QA function derives its test cases from
(`QA-001`, `QA-003`), what percentage of the requirement set Odoo 19 CE already satisfies
(`RQ-003`), and what number appears in the denominator when anyone reports coverage (`RQ-004`).

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The requirement **construct** — the syntactic form every requirement statement shall take (§3.10.2) |
| 2 | The requirement **attribute set** — the 13 attributes every requirement shall carry (§3.10.3) |
| 3 | The **verification method** taxonomy and the rule allocating one to every requirement (§3.19) |
| 4 | The **well-formedness standard** and the automated conformance checks that enforce it (§3.10.4) |
| 5 | The **single requirement denominator** and the counting rule that produces it (§3.10.5) |
| 6 | The **adoption by reference** of the 3,347 module and portal requirement rows, and the conversion procedure that makes them conforming (§3.10.7) |
| 7 | The **programme-level software requirements** `SWR-001` … `SWR-042` that no module specification owns (§3.12) |
| 8 | The 29148 §9.6 contextual content — product perspective, functions, user characteristics, limitations, assumptions, apportioning, external interfaces, usability, performance, logical database, design constraints, standards compliance, software system attributes |
| 9 | The **baseline definition** — what it means for the requirement set to be baselined, and what changes afterwards require |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The 3,347 module and portal requirement statements themselves | `../../1000fix_ERP_Module/03_Modules/` | The module specifications win on *what the system does* (`FOLDER_STRUCTURE.md` §9). Restating them creates a divergent second population |
| Requirements on hardware, network, devices, field conditions and third parties | `RQ-002` SyRS | Those sit **above** the software boundary. 29148 distinguishes SyRS (§9.5) from SRS (§9.6); this document is the SRS |
| Whether Odoo 19 CE already satisfies a requirement | `RQ-003` Fit-Gap & FDS | A fit-gap determination is a *disposition of* a requirement, not part of its statement |
| The bidirectional trace from objective to evidence | `RQ-004` RTM | This document defines the attributes that make tracing possible; `RQ-004` holds the links |
| How requirements are elicited, changed, versioned and retired | `RQ-005` Requirements Management Plan | Process, not content |
| Quality-attribute targets and their measurement methods | `RQ-006` NFR Specification | 29148 §9.6.13, §9.6.14 and §9.6.18 are **satisfied by reference** to `RQ-006` — see the tailoring declaration in §2.1.2 |
| Given/When/Then acceptance criteria per story | `RQ-008` | A requirement's verification method is not the same artefact as a story's acceptance criteria |
| Enforced business rules and their classification | `RQ-009` | A rule constrains many requirements; it is not a requirement |
| Architecture, design, schema and API contracts | `AR-001`, `AR-003`, `DA-001`, `IN-002` | 29148 §5.2.5 *Appropriate* forbids design content in a requirement |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Implementation vendor** | The contractual statement of what is being bought. Priced against, and accepted against, per `CO-003` |
| **Developers** | The authority on what a requirement means and when it is satisfied. The construct in §3.10.2 tells them where the ambiguity has been removed |
| **QA engineers** | The derivation source for every test case (`QA-003`), and the verification-method allocation that determines *which level* tests it |
| **Business owners** | The record of what they accepted at UAT. §3.10.3 attribute `owner` names them per requirement |
| **Architects** | The stable requirement set from which `AR-001` (SAD) is derived, and the constraint set in §3.16 that bounds it |
| **PMO and auditors** | The single denominator (§3.10.5) that makes coverage reporting possible, and the baseline rule (§3.10.8) that makes scope movement visible |
| **Data Protection Officer** | The functional realisation of the PDPA 2026 obligations — reallocated from `05-06` §6.3 to `SWR-018` … `SWR-029` in §3.12.4 |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

#### 2.1.1 Conformance claim

This document claims **tailored conformance** to ISO/IEC/IEEE 29148:2018 under clause 4.5.2 and
Annex C (normative, *Tailoring policies*). The tailoring is declared in §2.1.2; nothing is
omitted silently.

| Standard | Clause | How this document conforms | Departure and rationale |
|---|---|---|---|
| ISO/IEC/IEEE 29148:2018 | §9.6.1–9.6.20 | §3.1–§3.20 map one-to-one onto the twenty SRS content clauses, in the standard's order and under the standard's names | None in structure |
| ISO/IEC/IEEE 29148:2018 | §5.2.4 Requirements construct | §3.10.2 adopts the `[Condition][Subject][Action][Object][Constraint of Action]` construct verbatim as the mandatory form | None |
| ISO/IEC/IEEE 29148:2018 | §5.2.5 Characteristics of individual requirements | §3.10.4 makes all nine characteristics — necessary, appropriate, unambiguous, complete, singular, feasible, verifiable, correct, conforming — testable checks | None |
| ISO/IEC/IEEE 29148:2018 | §5.2.6 Characteristics of a set of requirements | §3.10.9 applies all five set characteristics — complete, consistent, feasible, comprehensible, able to be validated — as baseline entry criteria | None |
| ISO/IEC/IEEE 29148:2018 | §5.2.7 Requirement language criteria | §3.10.4 table B is the banned-construct list, enforced by the automated check in §3.10.10 | None |
| ISO/IEC/IEEE 29148:2018 | §5.2.8 Requirements attributes | §3.10.3 defines 13 attributes; the standard's examples are a superset of 9 of them | 4 attributes added — `layer`, `wave`, `residency`, `fit_gap` — required by this programme's delivery model. Addition is permitted; omission is not |
| ISO/IEC/IEEE 29148:2018 | §6.6 Requirements management | Delegated in full to `RQ-005` | Permitted: 29148 separates process (§6) from information item content (§9) |
| ISO/IEC 25010:2023 | Product quality model, 9 characteristics | Quality-of-service requirements are specified in `RQ-006` against the **2023** revision | See §2.1.3 — the estate cites the superseded 2011 model |
| ISO/IEC/IEEE 12207:2017 | Annex H | Agile formulations (user stories) are permitted as an *additional* representation, never as the requirement of record | Recorded as decision `D-03` |

#### 2.1.2 Tailoring declaration (Annex C)

| Clause | Treatment | Justification |
|---|---|---|
| §9.6.13 Usability requirements | **Satisfied by reference** to `RQ-006` §Interaction capability | Placing usability targets in two documents guarantees divergence. `RQ-006` is the single home for every measurable quality target |
| §9.6.14 Performance requirements | **Satisfied by reference** to `RQ-006` §Performance efficiency | As above |
| §9.6.18 Software system attributes | **Satisfied by reference** to `RQ-006` | As above |
| §9.6.15 Logical database requirements | **Stated at constraint level only** (§3.15); the model itself is `DA-001` | 29148 §5.2.5 *Appropriate* forbids design detail in requirements. A logical data model is design |
| §9.6.12 Functions | **Adopted by reference** to the 67 module and 12 portal specifications, under the conversion procedure in §3.10.7; supplemented by `SWR-001` … `SWR-042` | Restating 3,347 statements would create a divergent second population. The reference is controlled: §3.10.7 states exactly which files, at which version, constitute the adopted set |

**No clause of §9.6 is omitted.** Two clauses (§9.6.13, §9.6.14) that a reader might expect to
find populated here are deliberately empty of content and carry a pointer instead; that is a
tailoring decision, recorded, not an oversight.

#### 2.1.3 Standards currency — verified

Rule `PG-M4` requires a verification date on every standard, statute and vendor version cited.
Audit `H-01` (NIST SP 800-88 r1 withdrawn) and `C-04` (Digital Security Act 2018 repealed twice)
are both stale-citation failures.

| Citation | Status at verification | Verified on | Note |
|---|---|---|---|
| ISO/IEC/IEEE 29148:2018 | **Current.** Second edition; cancels and replaces ISO/IEC/IEEE 29148:2011 | 2026-08-18 | Revised in response to the revision of 15288 and 12207 |
| **ISO/IEC 25010:2023** | **Current.** Revises the product quality model of ISO/IEC 25010:2011 | 2026-08-18 | **Nine** characteristics. *Safety* added; *Usability* → *Interaction capability*; *Portability* → *Flexibility*. See finding `RQA-05` |
| IEEE 1016-2009 | Current for design description | 2026-08-18 | Cited for the boundary with `AR-003`, not applied here |
| ISO/IEC/IEEE 12207:2017 | Current | 2026-08-18 | Annex H, agile formulations |
| Personal Data Protection Act 2026 (Law 63 of 2026) | **In force.** Enforcement mechanisms activate ~13 May 2027 | 2026-08-12 (`05-06` §6.1) | Re-verification due at the Wave 1 gate |
| Odoo 19 Community Edition | Baseline platform per `02-05` §2 | 2026-08-12 (`02-05`) | Version claim inherited, not independently re-verified here — recorded as open question `Q-05` |

> **Correction issued.** `PGD-000` §0.5 and `_templates/TPL_Guiding_Document.md` §3 both state that
> an SRS follows *ISO/IEC/IEEE 29148:2018 **§9.5***. §9.5 is the **System** Requirements
> Specification (SyRS). The Software Requirements Specification is **§9.6**. Recorded as finding
> `RQA-01`; the template is corrected as part of this issue.

### 2.2 Source material relied on

| Source | Location | What it establishes | Measured at 02:15 (+06) |
|---|---|---|---|
| Module specifications | `../../1000fix_ERP_Module/03_Modules/*/M*.md` | Functional requirement statements, module-local business rules, automations, entities, interfaces | **67 files · 2,989 FR rows** |
| Portal specifications | `../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P*.md` | Portal-surface requirements | **12 files · 358 FR rows** (`FR-POR-001…358`) |
| Feature & Function Register | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-01` | Identifier allocation authority (§1.3), deferred requirement blocks (§3), portal allocation (§4), v1.0 traceability (§5), requirement governance (§6) | 34 KB |
| NFR & Standards | `.../05-06` | 104 unique NFR identifiers across 109 rows; architecture standards `AS-01…15`; data integrity `DI-01…08`; operability `OPS-01…08` | See `RQ-006` |
| Business Rules & Automation Catalogue | `.../05-05` | 140 `BRU` identifiers across 20 module codes | See `RQ-009` |
| Role, Permission & Access Matrix | `.../05-04` | `R01`–`R38` registered; `SOD-01`–`SOD-12` registered | See §3.6 |
| Data Model & Entity Catalogue | `.../05-02` | 434 distinct `fix.*` entity references | See `DA-001` |
| Integration & API Catalogue | `.../05-03` | Integration inventory, endpoint tables, event names | See `IN-002` |
| Technology Stack & Build-vs-Buy | `../../1000fix_ERP_Module/02_Architecture/02-05` | Six delivery layers L1–L6 with coverage percentages; 80 custom deliverables; `CD-001…138` | See `RQ-003` |
| Implementation Roadmap | `.../06_Delivery_and_Implementation/06-01` | Nine waves, months 1–36, wave content and gate criteria | See §3.9 |
| KPI, Benefits & Acceptance Criteria | `.../06-02` | 18 business objectives `BO-01…BO-18`; gate acceptance criteria `G1`–`G9` | See `RQ-010` |
| Business Requirements Document | `../../primary-doc/…BRD.md` | §3 objectives, §8 business requirements, §10 business rules, §12 process flows, §13 use cases `UC-nnn`, §20 acceptance criteria | 336 KB |
| User Requirements Document | `../../primary-doc/…URD.md` | **245 user stories** `US-<CODE>-nnn` with acceptance criteria in two formats | 284 KB — see `RQ-008` |
| Request for Proposal | `../../primary-doc/…RFP.md` | 405+ procurement requirements; §17 evaluation methodology | 276 KB |
| Sibling programme SRS | `../../../Intergrated_web_portal/project_requirement_document/04_SRS_…` | Proven in-house SRS pattern, January 2026 | Referenced as precedent; **not** verified line by line — open question `Q-06` |

### 2.3 Audit findings this document closes

| Finding | Source | How this document closes it | Residual |
|---|---|---|---|
| `TS-01` (critical) | `AUDIT-014` | §3.10.5 fixes **one** denominator — 3,347 requirement rows — with the counting rule that produces it and the command that reproduces it | Closes on `RQ-004` publishing the first coverage report against it |
| `C-02` (critical) | `00-06` | §3.10.7 adopts **all** 67 module files and 12 portal files by name, so no module — `M31` included — can sit outside the requirement set | Closes fully when `RQ-004` issues |
| `AP-02` | `00-07` | §3.12.4 reallocates the misclassified obligations of `05-06` §6.3 to functional requirements `SWR-018…SWR-029`, removing the reason the NFR space was overloaded | `RQ-006` resolves the identifier collision itself |
| `H-02` (partial) | `00-06` | §3.10.5 states the measured requirement population, replacing the ~2,352 estimate on which the effort model rests | Closes with `RQ-003` and `GV-007` |
| **`RQA-01`** *(raised here)* | This document | The `§9.5` / `§9.6` citation error in `PGD-000` and the house template is corrected | Corrected at issue |
| **`RQA-02`** *(raised here)* | This document | **Zero** of 3,347 requirement rows contain a modal verb. §3.10.2 makes the construct mandatory and §3.10.7 states the conversion procedure | Open until conversion completes at the Wave 1 gate |

---

# 3. Software Requirements Specification

*Structured per ISO/IEC/IEEE 29148:2018 §9.6. Clause numbers are given against each heading.*

## 3.1 SRS overview *(§9.6.1)*

This SRS specifies the software requirements for the 1000FiX Enterprise Platform — an
after-sales service ERP and a suite of twelve portals and applications, built on Odoo 19
Community Edition with OCA modules, standalone open-source systems and custom development, for
1000FiX Services Limited, Bangladesh.

The software is delivered in **nine waves over 36 months**. This SRS is baselined once and
amended by controlled change; it is **not** re-issued per wave. Wave allocation is a requirement
*attribute* (§3.10.3), not a document boundary — that is what allows one coverage denominator to
survive nine waves.

**Document map**

| §9.6 clause | This document | Content |
|---|---|---|
| 9.6.1 | §3.1 | This overview |
| 9.6.2 | §3.2 | Purpose |
| 9.6.3 | §3.3 | Scope |
| 9.6.4 | §3.4 | Product perspective |
| 9.6.5 | §3.5 | Product functions |
| 9.6.6 | §3.6 | User characteristics |
| 9.6.7 | §3.7 | Limitations |
| 9.6.8 | §3.8 | Assumptions and dependencies |
| 9.6.9 | §3.9 | Apportioning of requirements |
| 9.6.10 | §3.10 | Specified requirements — construct, attributes, well-formedness, denominator, adoption |
| 9.6.11 | §3.11 | External interfaces |
| 9.6.12 | §3.12 | Functions — including `SWR-001` … `SWR-042` |
| 9.6.13 | §3.13 | Usability requirements *(by reference)* |
| 9.6.14 | §3.14 | Performance requirements *(by reference)* |
| 9.6.15 | §3.15 | Logical database requirements |
| 9.6.16 | §3.16 | Design constraints |
| 9.6.17 | §3.17 | Standards compliance |
| 9.6.18 | §3.18 | Software system attributes *(by reference)* |
| 9.6.19 | §3.19 | Verification |
| 9.6.20 | §3.20 | Supporting information |

## 3.2 Purpose *(§9.6.2)*

The software exists to replace an operating model in which a fourteen-revenue-stream after-sales
business is coordinated by telephone, spreadsheet and paper across 51+ branches. Its purpose is
to be the **single system of record for operational and financial truth** in that business, and
the single source from which twelve customer-, partner- and staff-facing surfaces are served.

The boundary is fixed by `00-01` §5 and restated here as a requirement on the software rather
than as a principle: **the ERP owns state and truth; portals own experience and reach**. No
portal holds a record the ERP does not hold; no portal enforces a business rule
(`SWR-009`, §3.12.1).

## 3.3 Scope *(§9.6.3)*

| Attribute | Value | Measured |
|---|---|---|
| Software name | 1000FiX Enterprise Platform (ERP System & Portal Suite) v2.0 | — |
| Functional modules | **67** | 67 files, 02:15 (+06) |
| Portals and applications | **12** | 12 files |
| Module categories | **11** (A–K) | 11 directories |
| Requirement rows adopted | **3,347** | 2,989 module + 358 portal |
| Programme-level requirements specified here | **42** (`SWR-001` … `SWR-042`) | §3.12 |
| Delivery waves | **9** (months 1–36) | `06-01` §3 |
| Custom deliverables | **80** — 58 Odoo modules, 12 services, 4 mobile apps, 6 web applications | `02-05` §5.1 |
| Languages | Bengali (bn-BD) primary, English (en) secondary | `05-06` §9 |
| Legal entity scope at go-live | 1000FiX Services Limited, Bangladesh | `M65` provides multi-entity capability from W9 |

**What the software is not.** It is not the corporate website, not the pre-existing portal
platform that `CON-03` states cannot be replaced, and not a general-purpose BPM engine — no
diagram in this programme executes (`SP-003` rule `PD-01`).

## 3.4 Product perspective *(§9.6.4)*

The software is a **replacement system** for 48 legacy sources (`DM-002`) and a **new system**
for eleven capability areas that have no incumbent — marketplace, rental, trade-in, e-waste,
managed services, conversational AI, IoT telemetry, subscription revenue, partner channel,
multi-entity localisation and internal ITSM.

### 3.4.1 System context

```
        ┌──────────────────────────────────────────────────────────────────┐
        │  Customers · Corporate clients · Brand partners · Marketplace    │
        │  sellers · Vendors · Couriers · Regulators (NBR, NDMA)           │
        └───────┬──────────────────────────────────────────────┬───────────┘
                │                                              │
        ┌───────▼───────────────────────┐          ┌───────────▼───────────┐
        │  12 PORTALS & APPLICATIONS    │          │  EXTERNAL SERVICES    │
        │  P01…P12 — experience & reach │          │  bKash · Nagad ·      │
        │  6 Next.js · 4 Flutter        │          │  SSLCOMMERZ · BEFTN · │
        │  No business rule executes    │          │  NBR VAT Online · SMS │
        │  here (SWR-009)               │          │  · WhatsApp · courier │
        └───────┬───────────────────────┘          └───────────┬───────────┘
                │  API gateway only (SWR-002)                  │
        ┌───────▼──────────────────────────────────────────────▼───────────┐
        │            1000FiX ERP — SYSTEM OF RECORD (this SRS)             │
        │   67 modules · Odoo 19 CE + OCA + custom · PostgreSQL 16         │
        │   State · truth · rules · ledger · audit · events                │
        └───────┬──────────────────────────────────────────────┬───────────┘
                │                                              │
        ┌───────▼───────────────┐                  ┌───────────▼───────────┐
        │  PLATFORM SERVICES    │                  │  ANALYTICAL ESTATE    │
        │  Keycloak · Kong ·    │                  │  ClickHouse · Metabase│
        │  n8n · Novu · Redis · │                  │  TimescaleDB · MLflow │
        │  Redpanda · MinIO     │                  │  (read-only replicas) │
        └───────────────────────┘                  └───────────────────────┘
```

### 3.4.2 Interface classes *(§9.6.4)*

| Class | Summary | Specified in |
|---|---|---|
| User interfaces | 12 portal surfaces plus the Odoo back office | §3.11.1 · `UX-001`, `UX-003` |
| Hardware interfaces | Thermal and label printers, barcode/QR scanners, biometric devices, signature pads, queue displays, kiosks, GPS | §3.11.2 · `RQ-002` §4.11 |
| Software interfaces | Payment rails, NBR VAT Online, BEFTN, SMS and WhatsApp gateways, courier APIs, brand claim portals | §3.11.3 · `IN-004` |
| Communications interfaces | HTTPS/TLS 1.2+ REST via Kong; asynchronous events via the outbox and Redpanda; SMTP; SMPP | §3.11.4 · `IN-001` |
| Memory and storage constraints | Field devices: 3 GB RAM, 32 GB storage minimum | `RQ-002` §4.11 |
| Operations | 24×7 with a Bangladesh-business-hours availability tier; 24-hour offline field operation | `RQ-006` |
| Site adaptation | Per-branch configuration without code change; per-entity and per-country packs from W9 | §3.16 constraint `CN-07` |

## 3.5 Product functions *(§9.6.5)*

The software's functions are organised in **eleven categories** containing 67 modules. This table
is the top-level function inventory; the requirement rows beneath each module are adopted by
reference under §3.10.7.

| Cat | Category | Modules | FR rows | Modules in W1–W2 |
|:--:|---|---:|---:|---:|
| A | Service Delivery & Operations | 7 | 359 | 4 |
| B | Customer Engagement & Experience | 7 | 320 | 3 |
| C | Commercial, Pricing & Revenue | 9 | 494 | 1 |
| D | Circular & Asset-Based Business | 3 | 109 | 0 |
| E | Supply Chain & Inventory | 6 | 235 | 1 |
| F | Asset, Equipment & Facilities | 5 | 232 | 1 |
| G | Finance & Treasury | 8 | 333 | 0 |
| H | People & Workforce | 7 | 310 | 0 |
| I | Governance, Risk, Quality & Knowledge | 4 | 170 | 0 |
| J | Data, Analytics & Intelligence | 4 | 146 | 0 |
| K | Platform & Technology | 7 | 281 | 4 |
| — | **Module subtotal** | **67** | **2,989** | **14** |
| P | Portals & Applications | 12 | 358 | 3 |
| — | **Total adopted** | **79** | **3,347** | **17** |
| — | Programme-level (`SWR`), specified in §3.12 | — | **42** | 42 |
| — | **Requirement set** | | **3,389** | |

> **Counted, not consulted.** The per-category FR totals above were produced by counting rows
> matching `^\| *FR-[A-Z0-9]+-[0-9]+[a-z]?` in each module file at 02:15 (+06). They do not agree
> with `05-01` §1.3a, which estimates ~2,352 across the same 67 modules. Measured **2,989** against
> an estimated **~2,352** is a variance of **+27%** — squarely inside the +23% / +32% / +52%
> category variances `05-01` itself records, and confirming that its estimate for the unmeasured
> categories is low. The portal estate's 358 rows sit outside `05-01` §1.3a's scope entirely and
> are excluded from this comparison. See `RQ-003` §5 for the effort consequence and finding
> `RQA-03`.

## 3.6 User characteristics *(§9.6.6)*

| Class | Population | Characteristics that shape requirements | Consequence |
|---|---:|---|---|
| Field technicians | 200–400 | Android device, outdoors, gloves, sunlight, intermittent 3G/4G, Bengali-first, variable literacy in English | 24-hour offline operation is functional, not a nicety (`SWR-030`); Bengali is the default, not a toggle (`SWR-013`) |
| Branch counter agents | ~250 across 51+ branches | High-throughput walk-in intake, queue pressure, customer waiting | Intake in ≤ 3 minutes is a gate criterion (`G1-03`), which makes keystroke count a requirement input |
| Riders / logistics | ~100 | Motorcycle, one-handed, cash handling, no desk | Offline plus cash reconciliation as a first-class flow |
| Workshop technicians | ~150 | Bench-bound, barcode scanning, multi-job parallelism | Custody chain and job-state accuracy over convenience |
| Contact centre agents | ~40 | Screen-dense console, telephony coupling, bilingual | Console composition is a portal requirement (`P10`), not an ERP screen |
| Finance and back office | ~60 | Statutory forms, decimal precision, period close | No floating point in money paths (`SWR-034`) |
| Managers and executives | ~50 | Read-mostly, dashboard, exception-driven | Analytical estate is read-only and replica-served |
| Corporate clients | 500+ organisations | Their own approval chains, their own reporting formats | Approval-chain configuration is a customer-configurable requirement |
| Marketplace sellers | 500–2,000 | External, untrusted, commercially motivated, self-service onboarding | Every seller-facing surface is an abuse surface — `SC-002` threat model is a prerequisite for W7 |
| Customers | 250,000+/month | Low digital literacy assumed, Bengali-first, low-end Android, data-cost sensitive | ≤ 400 KB first load on critical paths; no portal may require an app install |
| Auditors and regulators | — | Evidence, immutability, retention | Audit trail completeness is a requirement, not a logging convention (`SWR-032`) |

**Access profiles.** `05-04` registers roles `R01`–`R38`. Measurement at 02:15 (+06) finds
**twelve further role identifiers — `R39` through `R50` — in use across 15 module files and not
registered**. Until `SC-004` registers them, a requirement referencing `R43` cannot be verified,
because the role has no definition. Recorded as `RQA-04`; the same applies to `SOD-13` … `SOD-30`
(18 segregation-of-duties identifiers used and unregistered).

## 3.7 Limitations *(§9.6.7)*

| # | Limitation | Source | Effect on the requirement set |
|---|---|---|---|
| L-01 | Odoo 19 CE is the mandated foundation; Enterprise Edition is excluded | `02-05` §2, decision inherited from v1.0 | A requirement may not assume an Enterprise-only capability |
| L-02 | Extensions are separate modules; core is never modified | `02-05` §9, `AS-05` | A requirement may not be satisfied by a core fork |
| L-03 | The pre-existing portal platform cannot be replaced | `CON-03` (`00-04`) | Portal requirements must be satisfiable through integration, not replacement |
| L-04 | Sensitive personal data must remain Bangladesh-resident | `NFR-086`, PDPA 2026 | Requirements touching NID, TIN, passport, biometric templates or recovered customer data carry a `residency` attribute (§3.10.3) |
| L-05 | Software licence cost for the ERP core is $0; L6 commercial components require CFO approval each | `02-05` §6 | A requirement may not be satisfied by unapproved commercial software |
| L-06 | Field devices are Android 11+ with 3 GB RAM on 3G/4G | `05-06` §10 | Client-side requirements are bounded by that envelope |
| L-07 | Bengali strings run 15–30% longer than English | `UX-007` | Any requirement specifying a fixed layout is not implementable |
| L-08 | The programme has no requirements-management tool; requirements live in markdown | Measured: zero `.yaml`, `.json`, `.sql`, `.py` files in 601 | The attribute set in §3.10.3 must be expressible in a markdown table until `RQ-005` §7 procures a tool |

## 3.8 Assumptions and dependencies *(§9.6.8)*

| # | Assumption or dependency | If it fails | Owner |
|---|---|---|---|
| A-01 | The 67 module specifications are substantively correct on *what the system does* | The conversion in §3.10.7 propagates the error into the baseline | Lead BA |
| A-02 | `RR-002` will register the identifier spaces reserved in §3.10.6 | The `SWR` and `SYR` spaces remain provisional and cannot be used in build tickets | Enterprise Architecture |
| A-03 | A legal opinion confirms the split-residency design (`DEP-31`, decision `D-13`) | `SWR-015`–`SWR-017` are unimplementable and Wave 1 architecture cannot be fixed | CTO / Legal |
| A-04 | `SC-004` registers `R39`–`R50` and `SOD-13`–`SOD-30` before Wave 1 build | Requirements referencing those roles cannot be verified | CISO |
| A-05 | Odoo 19 CE remains supported through the 36-month programme | `L-01` becomes an upgrade requirement mid-programme | CTO |
| A-06 | The business can release named owners to accept requirements at UAT | The `owner` attribute is unpopulated and acceptance has no signatory | Programme Director |
| A-07 | Bengali translation capacity exists for 100% string coverage before each wave gate | `SWR-013` blocks every gate | Change Lead |
| D-01 | `RQ-006` issues before the SAD (`AR-001`) is drafted | `AR-001` has no quality-attribute scenarios to design against | Requirements Manager |
| D-02 | `RQ-003` issues before `GV-008` budget baseline | The cost baseline rests on a layer-level estimate rather than a requirement-level determination | CFO |

## 3.9 Apportioning of requirements *(§9.6.9)*

Requirements are apportioned across nine delivery waves. Apportionment is an **attribute of the
requirement** (`wave`), not a separate document — so the denominator is stable while the
allocation moves.

| Wave | Months | Theme | Modules | Portals |
|:--:|---|---|---|---|
| W1 | 1–4 | Foundation & Service Core | M29, M28, M30, M07, M17, M01 (core), M04, M33, M37 | P03 |
| W2 | 5–8 | Field Operations & Inventory | M02, M15, M31, M10, M64, M01 (complete) | P01 (web), P02 |
| W3 | 9–13 | Money, Movement & Documents | M03, M11 (core), M16, M19, M20, M24, M41, M50, M52, M63 | P05, P09 |
| W4 | 14–18 | Agreements, Billing & Contact | M08, M09, M25, M27, M32, M34, M39, M42, M51, M53, M62 | P04, P06, P08, P10 |
| W5 | 19–22 | People, Quality & Managed Services | M05, M21, M22, M23, M45, M46, M49, M55, M56, M57 | P11 |
| W6 | 23–26 | New Asset Businesses | M06, M13, M14, M43, M44, M54, M58, M59, M60, M61, M66, M26 (start) | P01 (native) |
| W7 | 27–30 | Marketplace & Settlement | M12, M38, M40, M47, M67, M11 (dynamic), M53 (settlement) | P07, P12 |
| W8 | 31–34 | Intelligence & Sustainability | M18, M48, M26 (complete), M62 (warehouse) | — |
| W9 | 35–36 | Expansion Readiness | M65 | — |

**Apportionment rules**

| # | Rule |
|---|---|
| AP-01 | Every adopted requirement carries exactly one `wave` value. A requirement in no wave is not in the baseline |
| AP-02 | A requirement may not be scheduled in a wave earlier than the wave of any requirement it declares in `depends_on`. Verified mechanically by `RQ-004` |
| AP-03 | Moving a requirement to a later wave is a **change**, recorded under `RQ-005` §5 with a reason and a new target. Silent deferral is a defect (`05-01` §6) |
| AP-04 | Two modules deliver across a wave boundary (`M01` W1→W2, `M11` W3→W7, `M53` W4→W7, `M26` W6→W8, `M62` W4→W8). For these, `wave` is allocated **per requirement**, never per module |

## 3.10 Specified requirements *(§9.6.10)*

This is the normative core of the document.

### 3.10.1 What a requirement is, in this programme

A requirement is a **single, verifiable statement of something the software shall do or shall
be**, carrying the thirteen attributes in §3.10.3, expressed in the construct in §3.10.2, and
satisfying all nine characteristics in §3.10.4.

A feature name is not a requirement. A user story is not a requirement — it is an additional
representation of one (`RQ-008`). A business rule is not a requirement — it is a constraint that
many requirements must respect (`RQ-009`). A design statement is not a requirement; 29148 §5.2.5
*Appropriate* excludes it.

### 3.10.2 The requirement construct *(mandatory)*

Every requirement shall be expressed in the ISO/IEC/IEEE 29148:2018 §5.2.4 construct:

```
[Condition] [Subject] [Action] [Object] [Constraint of Action]
```

| Element | Rule | Example |
|---|---|---|
| **Condition** | Optional. States when the requirement applies. Measurable | *When a device serial is scanned at intake,* |
| **Subject** | **Mandatory.** Names the entity that shall act — the system, a named module, a named portal, or a service | *the ERP* |
| **Action** | **Mandatory.** A single active verb preceded by **`shall`** | *shall determine* |
| **Object** | **Mandatory.** What the action acts on | *the device's warranty and contract entitlement* |
| **Constraint of Action** | Mandatory where the requirement is otherwise unverifiable | *within 2 seconds, returning exactly one of: manufacturer warranty, extended warranty, protection product, AMC/RAMC coverage, or none.* |

**Modal vocabulary** — 29148 §5.2.4:

| Verb | Meaning | Is it a requirement? |
|---|---|---|
| **shall** | Mandatory binding provision | **Yes** — the only verb that creates one |
| will | Statement of fact, futurity or purpose; establishes context | No |
| should | Goal or preference | No |
| may | Allowance or suggestion | No |
| **must** | **Prohibited** in this programme — ambiguous between obligation and inference | — |

### 3.10.3 Requirement attributes *(mandatory — §5.2.8)*

Thirteen attributes. Nine derive from 29148 §5.2.8; four are added for this programme's delivery
model, which is permitted (addition) where omission is not.

| # | Attribute | Rule | Source |
|---|---|---|---|
| 1 | `id` | Unique, permanent, never reused even if the requirement is deleted. Format per §3.10.6 | 29148 |
| 2 | `statement` | The construct in §3.10.2 | 29148 |
| 3 | `title` | ≤ 8 words, a noun phrase, unique within its module | 29148 |
| 4 | `rationale` | Why the requirement exists. **Mandatory for every P0** — a P0 with no rationale cannot be descoped rationally | 29148 |
| 5 | `source` | The BRD §, URD story, RFP §, statute, audit finding or decision it derives from. **Mandatory** | 29148 |
| 6 | `owner` | The business **role** that accepts it at UAT. Never a personal name | 29148 |
| 7 | `priority` | `P0` / `P1` / `P2` / `P3` per §3.10.11. One scale programme-wide | 29148 |
| 8 | `verification_method` | Exactly one of Inspection / Analysis / Demonstration / Test — §3.19. **Mandatory** | 29148 |
| 9 | `status` | Proposed → Approved → Allocated → Built → Verified → Accepted; or Deferred / Superseded / Retired | 29148 |
| 10 | `wave` | `W1`–`W9`. Exactly one | **Added** — `06-01` |
| 11 | `layer` | `L1`–`L6` delivery layer. Provisional until `RQ-003` determines it | **Added** — `02-05` |
| 12 | `residency` | `resident` / `regional` / `n-a`. Mandatory where the requirement touches personal data | **Added** — `NFR-086a` |
| 13 | `fit_gap` | `fit` / `configure` / `extend` / `build` / `undetermined`. Owned by `RQ-003` | **Added** — `RQ-003` |

> **`verification_method` is the attribute the estate is missing entirely.** Measurement at
> 02:15 (+06): the string "verification method" occurs in **one** file across the 79 module and
> portal specifications, and **zero** requirement rows carry a verification vocabulary term. Until
> this attribute is populated, "the requirement is met" is an opinion.

### 3.10.4 Well-formedness standard

**Table A — the nine characteristics of an individual requirement (§5.2.5), as tests**

| # | Characteristic | The test applied at review |
|---|---|---|
| W-01 | **Necessary** | Delete it. Does a capability gap appear that no other requirement fills? If not, it is not necessary |
| W-02 | **Appropriate** | Does it constrain the architecture or name a design solution? If yes, move the design content to `AR-003` |
| W-03 | **Unambiguous** | Can two competent readers derive two different implementations? Tested by the language check in Table B |
| W-04 | **Complete** | Can it be implemented without opening another document? Cross-references are permitted; missing information is not |
| W-05 | **Singular** | Does it contain "and" joining two verbs, or a list of behaviours? If yes, split it |
| W-06 | **Feasible** | Realisable within cost, schedule and the `L-01`–`L-08` limitations, at acceptable risk |
| W-07 | **Verifiable** | Can `verification_method` be allocated and executed? If no method can be named, the requirement is not verifiable |
| W-08 | **Correct** | Does `source` resolve, and does the cited source actually say this? |
| W-09 | **Conforming** | Does it use the §3.10.2 construct and the §3.10.3 attributes? |

**Table B — banned language constructs (§5.2.7)**

| Class | Banned | Why |
|---|---|---|
| Superlatives | best, most, optimal, maximum possible | Unbounded |
| Subjective language | user-friendly, easy to use, intuitive, seamless, robust, efficient | Unverifiable |
| Vague pronouns | it, this, that — where the antecedent is not in the same sentence | Ambiguous |
| Ambiguous adverbs/adjectives | quickly, appropriately, significant, minimal, adequate, sufficient, reasonable | Unmeasurable |
| Ambiguous logic | and/or | Two requirements wearing one identifier |
| Open-ended terms | support for, including but not limited to, as a minimum, etc. | Unclosable set |
| Comparatives | better than, faster than, higher quality | No datum |
| Loopholes | if possible, as appropriate, as applicable, where feasible | Removes the obligation |
| Totality terms | all, always, never, every, any | Very difficult to verify; use an enumerated or bounded set |
| Incomplete references | a standard cited without version, edition or clause | Unbounded verification scope |
| Negative form | shall not | Prefer a positive statement of the enforced behaviour |
| Passive voice | it is required that; shall be able to | No subject; no obligation holder |

**Measured conformance of the existing estate — 3,347 rows, 02:15 (+06)**

| Check | Result | Assessment |
|---|---:|---|
| Rows containing `shall` | **0** | **Total non-conformance.** The modal is in the column header, not the statement |
| Rows containing `must` (prohibited verb) | 13 | Minor |
| Rows containing `should` in an obligation position | 1 | Minor |
| Loophole terms (*as appropriate, as applicable, where possible, if possible*) | 6 | **Very low** — the estate is unusually disciplined here |
| Superlative and subjective terms (*best, minimal, significant, sufficient, able to*) | 11 | **Very low** |
| Totality terms (*all, always, never, every, any*) | 636 | The dominant defect class by volume |
| Requirement tables with a modal prompt in the header | 78 of 431 | **353 tables give the author no prompt at all** |
| Distinct requirement-table header formats | **7** | The row schema itself is not standardised |

> **Interpretation, stated fairly.** On the *lexical* criteria of §5.2.7 the estate performs
> better than most enterprise requirement sets: 17 loophole-and-subjective occurrences in 3,347
> rows is roughly 0.5%. The failure is structural, not editorial — the rows are well-written
> *phrases* rather than badly-written *requirements*. That is a materially cheaper problem to fix
> than the reverse, and it is the basis for the conversion estimate in §3.10.7.

### 3.10.5 The single denominator *(closes audit `TS-01`)*

Four figures for "the number of requirements" are in circulation. This clause ends that.

| Figure | Where it appears | What it actually counts | Authoritative? |
|---:|---|---|:--:|
| 1,180 | `05-01` §1.3 total row | The superseded **30-module** allocation | No — self-declared superseded |
| ~2,352 | `05-01` §1.3a, `05-01` title | 7 categories measured, 4 estimated | No — mixed basis, prohibited for commitment by `RG-05` |
| 2,930 | `PGD-000`, `README.md` | Provenance not stated | No |
| 3,343 | audit `TS-01` | Provenance not stated | No |
| **3,347** | **This clause** | **Requirement rows counted on disk at 2026-08-18 02:15 (+06)** | **Yes** |

**Counting rule `CR-01`.** The requirement population is the number of **requirement rows**, not
the highest allocated identifier and not the sum of allocated ranges. A row is a line in a
module or portal specification matching `^\| *FR-[A-Z0-9]+-[0-9]+[a-z]?` inside a §5 functional
area table.

**Reproduction command** *(recorded so this figure is reproducible rather than assertable)*:

```bash
cd 1000fix_ERP_Module/03_Modules
grep -h -oE '^\| *FR-[A-Z0-9]+-[0-9]+[a-z]?' */M*.md | wc -l    # → 2989
grep -h -oE '^\| *FR-[A-Z0-9]+-[0-9]+[a-z]?' */P*.md | wc -l    # → 358
grep -h -oE '^\| *FR-[A-Z0-9]+-[0-9]+[a-z]?' */[MP]*.md \
  | sed 's/^| *//' | sort | uniq -d | wc -l                     # → 0 duplicates
```

**Rule `CR-02`.** No coverage percentage, effort figure or completeness claim may be published
against any denominator other than the one produced by `CR-01` at a stated timestamp. A figure
without a timestamp is not a figure (`PG-M11`).

**Rule `CR-03`.** The denominator moves only when the requirement set changes under `RQ-005`
change control. It is re-counted and re-stamped at every wave gate.

### 3.10.6 Identifier spaces *(provisional until `RR-002`)*

`PG-05` makes identifiers permanent, so allocation is the one act that cannot be corrected later.
Before reserving any space, all four repositories were swept for prefix collisions at
02:15 (+06).

| Space | Scope | Allocating authority | Status |
|---|---|---|---|
| `FR-<CODE>-nnn` | Module-local functional requirement | `05-01` §1.3 | **In use — 3,347 rows.** Defects recorded in §3.10.7 |
| `FR-POR-nnn` | Portal requirement, one flat sequence | `05-01` §4 | **In use — 001…358.** `05-01` §4 still records 001…140; superseded, see `RQA-06` |
| **`SWR-nnn`** | **Programme-level software requirement** | **This document** | **Reserved.** Sweep returns **0** prior occurrences across all four repositories |
| **`SYR-nnn`** | System requirement above the software boundary | `RQ-002` | **Reserved.** Sweep returns **0** prior occurrences |
| `NFR-nnn` | Quality-attribute requirement | `05-06`, re-based by `RQ-006` | In use — cite, do not invent |
| `BRU-<CODE>-nn` | Business rule | Module file; catalogued by `RQ-009` | In use |
| `AUT-<CODE>-nn` | Automation | Module file | In use |
| `UC-nnn` | Use case | BRD §13 | In use — `RQ-008` cites, does not reallocate |
| `US-<CODE>-nnn` | User story | URD §6–17 | In use — 245 stories |
| `R nn`, `SOD-nn` | Role, segregation of duties | `05-04` / `SC-004` | In use; `R39`–`R50` and `SOD-13`–`SOD-30` **unregistered** |
| `CD-nnn` | Custom development item | `02-05` §5.2, to be re-based by `BE-005` | **Colliding — do not use.** §3.10.7 |

> **Collision found and referred — finding `RQA-07`.** `PGD-000` allocates **`RQ`** as this
> category's code. The sweep finds `RQ-01` … `RQ-14` already in use as local rule identifiers in
> `../../project_content/10_Legal_Policy_and_Compliance/LG-010`. This is finding `PGD-A1-01` (the
> `RF`→`RR` collision) recurring, **undetected by the audit that closed it**.
>
> **Disposition.** The category code is *not* changed: `PGD-000` is issued, `PG-05` makes
> identifiers permanent, and the two spaces are distinguishable by width — `RQ-nnn` (three
> digits, a document identifier in this repository) versus `RQ-nn` (two digits, a rule identifier
> local to `LG-010`). An interim disambiguation rule is published as `ID-01` below. The permanent
> ruling belongs to `RR-002`, and the `LG-010` local space is referred to the Programme Content
> Lead for renaming, on the precedent of `PGD-A1-10` (this repository does not act on another
> repository's working tree).
>
> **`ID-01`.** A three-digit `RQ-nnn` denotes a Category 01 guiding document. A two-digit `RQ-nn`
> denotes a data-subject-request rule in `LG-010` and has no meaning outside that file. No new
> two-digit `RQ-` identifier may be allocated anywhere.

### 3.10.7 Adoption of the existing requirement set

**Rule `AD-01` — controlled adoption.** The 3,347 requirement rows in the 67 module files and 12
portal files listed in Appendix A are **adopted into this SRS by reference**, at the file versions
and modification timestamps recorded in Appendix A. A row not in Appendix A is not in the
baseline. A file changed after that timestamp re-enters the baseline only through `RQ-005` change
control.

**Rule `AD-02` — conversion.** Each adopted row shall be converted to a conforming requirement by
applying, without changing its meaning:

1. Prefix the statement with its subject and the modal `shall` (the header's implied subject
   becomes explicit).
2. Split any row containing "and" joining two verbs into two requirements, allocating a new
   identifier to the second and retiring nothing.
3. Replace each totality term with an enumerated or bounded set, or with an explicit exception
   clause.
4. Populate the thirteen attributes of §3.10.3, of which `verification_method`, `source`,
   `owner` and `rationale` (P0 only) are the four currently absent everywhere.
5. Re-run the Table B language check; a row failing it is returned to its module author, not
   silently edited.

**Worked example** — `FR-DTS-008`, `M06` §5, as it exists and as converted:

| | |
|---|---|
| **As written** | *Time-boxed retention · Hold recovered data only for the agreed window, then purge verifiably and issue a purge certificate · P0 · L5* |
| **Defects** | No subject; no modal; two verbs joined by "and" (W-05 singular); "the agreed window" unbounded (W-03); "verifiably" unmeasurable (W-03); no verification method; no source; no owner |
| **Converted** | `FR-DTS-008` — *When a data-recovery case reaches the retention date recorded on its custody record, the ERP shall purge the recovered customer data from the resident store and from every backup generation that contains it, and shall record the purge as an immutable event carrying the case identifier, the operator, the UTC timestamp and the media-sanitisation technique applied.* |
| | `FR-DTS-008d` *(new — split from the second verb)* — *On completion of the purge recorded by `FR-DTS-008`, the ERP shall issue a purge certificate carrying the case identifier, the customer identity, the data categories purged, the technique applied per IEEE 2883, and the verifying operator's identity.* |
| **Attributes added** | `verification_method: Demonstration` · `source: M06 §5, LG-009, PDPA 2026 s.erasure` · `owner: Data Services Manager` · `rationale: The destruction certificate is the commercial product; its evidentiary quality is the value sold` · `residency: resident` · `wave: W6` · `layer: L5` |

**Conversion effort — measured basis, not an estimate from intent**

| Input | Measured |
|---|---:|
| Rows to convert | 3,347 |
| Rows failing the singularity check (contain "and" joining verbs) — sampled | ~18% |
| Rows containing a totality term | 636 |
| Rows with zero of the four missing attributes populated | 3,347 |

Conversion is a **bounded, mechanical exercise on a set of good source material**, not a rewrite.
It is not estimated here: producing a fourth uncontrolled estimate is the error recorded as
`PGD-A1-05`. Sizing belongs to `GV-007`; this clause supplies the measured inputs it needs.

**Defects found in the adopted set, at adoption**

| # | Defect | Measured | Disposition |
|---|---|---|---|
| `RQA-06` | `05-01` §4 allocates `FR-POR-001…140` across 12 portals; the portal files actually use a contiguous `FR-POR-001…358`, and every per-portal range in §4 is wrong | 358 rows vs 140 allocated | The **portal files govern** (`FOLDER_STRUCTURE.md` §9). `05-01` §4 is superseded; referred to the module repository owner |
| `RQA-08` | `05-01` §1.3 allocates `FR-ECM-001…079` to **M12 Marketplace**. `M38 E-Commerce` actually holds `FR-ECM-001…056`. `M12` uses `FR-MKP-`. A consumer resolving `FR-ECM-014` gets a different requirement depending on which document they open | Confirmed both ways | **Critical.** `M38` governs; `05-01` §1.3 must be corrected. Referred, and registered for `RR-002` |
| `RQA-09` | Four prefixes allocated in `05-01` §1.3 are used by no module file: `SLS` (M11 — actually `PRC`), `SCM` (M16 — actually `PRO`), `BIL` (M20 — actually `ARB`), `HRM` (M21 — actually `HCM`). `05-01` §1.3b retires only `FR-BFO-` | 4 unregistered retirements | Retire all four explicitly; they are still cited by the BRD §10, the URD and `05-05` |
| `RQA-10` | `CD` identifiers `CD-059` … `CD-090` — a contiguous block of **31** — are each claimed by two module files. Modules `M31`–`M67` self-allocated from a sequence `02-05` had already issued to `M13`–`M20`. Highest identifier in use is `CD-214`; `02-05` registers only `CD-001…138` | 31 collisions; 108 distinct IDs in 139 rows | **Build backlog creation remains blocked** (`BE-005`). This SRS allocates no `CD` identifier and forbids deriving one from an adopted row |
| `RQA-11` | Four requirement identifiers use an alphabetic suffix (`FR-DTS-008b`, `-020a`, `-020b`, `-020c`), a form no register defines | 4 | Legitimise in `RR-002` as the *insertion* form, or renumber. Do not leave undefined |

> The `48 colliding CD identifiers` figure quoted in `_MODULE_TEMPLATE` §0 does not reproduce.
> Counting at 02:15 (+06) returns **31**. Both figures are recorded; the counted one governs
> (`PG-03`). This is exactly the class of discrepancy `RQ-004` exists to make impossible.

### 3.10.8 Baseline

| # | Rule |
|---|---|
| `BL-01` | The requirement set is baselined when §6 acceptance criteria `AC-01` … `AC-09` are met and the ERP Design Authority signs. Until `GV-002` constitutes that body, no baseline exists — `PGD-A1-09` applies to this document as it does to all 601 files |
| `BL-02` | After baseline, adding, deleting or materially changing a **P0 or P1** requirement requires Steering Committee approval; **P2 or P3** requires PMO approval (`05-01` §6, retained) |
| `BL-03` | The baseline is versioned as a whole. A requirement's own version is not tracked separately; its `status` and change history are (`RQ-005` §5) |
| `BL-04` | Each wave gate re-counts the denominator (`CR-03`) and records the delta since the previous gate. A delta with no approved change record is a scope-control failure and is raised to `GV-005` RAID |

### 3.10.9 Set characteristics *(§5.2.6 — baseline entry criteria)*

| # | Characteristic | Test | Position at issue |
|---|---|---|---|
| S-01 | **Complete** | Zero `TBD` / `TBS` / `TBR` clauses; every module and portal represented; every business objective `BO-01`–`BO-18` traced to ≥ 1 requirement | **Not met** — `RQ-004` must produce the objective trace |
| S-02 | **Consistent** | No two requirements conflict; one term means one thing (`CG-004` controlled vocabulary); units homogeneous | **Not met** — "job card", "service order", "work order" and "repair order" are used across `M01`/`M02`/`M04`/`M31` without an adjudicated definition (`RR-001`) |
| S-03 | **Feasible** | The whole set is realisable within cost, schedule and `L-01`–`L-08` | **Unknown** — depends on `RQ-003` and `GV-007`. 1,513 PW measured against 834 PW approved (`AF-08`) |
| S-04 | **Comprehensible** | A competent reader outside the authoring function can state what is expected | **Partially met** — the module specifications read well; the identifier collisions in §3.10.7 defeat resolution |
| S-05 | **Able to be validated** | Satisfying the set achieves the business need within legal and regulatory constraints | **Not met** — no lawful DR path for resident personal data (`OP-01`), no DPIA (`SC-003`) |

**Stated plainly: the requirement set does not yet satisfy any of the five set characteristics
without qualification.** That is the honest position at first issue, and each failing test names
the document that closes it.

### 3.10.10 Automated conformance checks

`RQ-005` §7 procures the tooling. Until then these run as shell checks in review and, from Wave 1,
in CI as a documentation gate:

| # | Check | Fails when |
|---|---|---|
| `CK-01` | Modal present | A requirement statement contains no `shall` |
| `CK-02` | Prohibited modal | A statement contains `must` |
| `CK-03` | Singularity | A statement contains ` and ` between two verbs |
| `CK-04` | Banned language | A statement matches any Table B term |
| `CK-05` | Attribute completeness | Any of the 13 attributes is empty |
| `CK-06` | Verification method | `verification_method` is not one of the four permitted values |
| `CK-07` | Identifier uniqueness | The same identifier appears in two files |
| `CK-08` | Identifier registration | A prefix is used that no register allocates |
| `CK-09` | Source resolution | `source` names a file, section or story that does not resolve |
| `CK-10` | Wave ordering | A requirement's wave precedes the wave of a requirement it depends on |
| `CK-11` | Role registration | A referenced `Rnn` or `SOD-nn` is unregistered |
| `CK-12` | Denominator stamp | A published coverage figure carries no enumeration timestamp |

### 3.10.11 Priority scale

**One scale, programme-wide.** Audit `AF-11` records two colliding scales (`P0–P3` for the ERP,
`P1–P4` for the website content set). This document uses only the ERP scale, and a document that
uses the other shall say so explicitly.

| Priority | Definition | Descope rule |
|:--:|---|---|
| **P0** | Regulatory, safety, financial-integrity or go-live blocking | **Cannot be descoped.** Removing one requires a Steering Committee decision recorded in `GV-003` |
| **P1** | Core business capability. The wave's benefit case depends on it | Descope moves the benefit; requires the benefit owner's agreement (`BM-004`) |
| **P2** | Important; deferrable by exactly one wave without benefit loss | PMO approval |
| **P3** | Desirable; opportunistic | PMO approval |

## 3.11 External interfaces *(§9.6.11)*

### 3.11.1 User interfaces

| # | Requirement | Detail owner |
|---|---|---|
| UI-R1 | Twelve portal surfaces plus the Odoo back office. Every surface uses the single shared design system | `UX-001` |
| UI-R2 | Bengali is the default for customer-, technician-, rider- and branch-facing surfaces; English is the default for finance, platform administration and executive surfaces | `UX-007` |
| UI-R3 | Layout shall accommodate Bengali string expansion of up to 30% without truncation or reflow failure | `UX-007` |
| UI-R4 | Every web portal shall meet WCAG 2.2 AA | `UX-005`, `QA-008` |

> **Currency note.** `05-06` `NFR-073` specifies **WCAG 2.1 AA**; `PGD-000` `UX-005` specifies
> **WCAG 2.2 AA**. Two conformance targets are in force simultaneously. This SRS adopts **2.2 AA**
> as the later and superset target, and records the conflict as `RQA-12` for `RQ-006` to resolve
> formally.

### 3.11.2 Hardware interfaces

Thermal receipt printers · label printers · barcode and QR scanners · biometric attendance
devices · signature capture pads · queue displays · self-service kiosks · GPS receivers in field
devices · IoT telemetry endpoints. Each is specified as a **system** requirement in `RQ-002`
§4.11; this SRS carries only the software's obligation to interface with them.

### 3.11.3 Software interfaces

| Class | Counterparties | Contract owner |
|---|---|---|
| Payment | bKash, Nagad, SSLCOMMERZ | `IN-007` |
| Banking | BEFTN | `IN-004` |
| Tax | NBR VAT Online (vat.gov.bd) — Mushak 6.3 and 9.1 | `IN-004` |
| Messaging | SMS gateways, WhatsApp Business, email | `IN-004` |
| Logistics | Courier APIs | `IN-004` |
| Brand partners | 17+ claim portals | `IN-004` |
| Identity | Keycloak; corporate federation for B2B clients | `SC-004` |

**`SWR-002` applies to all of them**: no portal, application or external party reaches the ERP
except through the API gateway with a party-specific credential.

### 3.11.4 Communications interfaces

Synchronous: HTTPS, TLS 1.2 minimum with TLS 1.3 preferred, REST through Kong, OpenAPI 3.1
contracts (`IN-002`). Asynchronous: transactional outbox → Redpanda, at-least-once delivery with
idempotent consumption (`DI-05`). No module reads another module's tables (`AS-01`).

## 3.12 Functions *(§9.6.12)*

Module and portal functions are adopted by reference under §3.10.7. This clause specifies the
**42 programme-level requirements that no module specification owns** — the population that is
genuinely absent rather than merely non-conforming.

Each is written in the §3.10.2 construct with its verification method allocated.

### 3.12.1 Cross-surface obligations

*Derived from `05-01` §4 "Cross-Portal Requirements", which are stated there as `FR-POR-X01`…`X10`
— an identifier form outside the `FR-POR-nnn` sequence and registered nowhere. They are reissued
here in the `SWR` space so they carry identifiers that resolve.*

| ID | Requirement | Pri | Verif. | Owner |
|---|---|:--:|:--:|---|
| `SWR-001` | Every portal and application shall authenticate its users through the central identity provider, and shall hold no local credential store. | **P0** | Inspection | CISO |
| `SWR-002` | Every portal, application and external party shall reach the ERP only through the API gateway, using a credential issued to that party alone. | **P0** | Inspection | Platform Lead |
| `SWR-003` | Every portal and application shall present its interface in Bengali and English, defaulting to the language recorded for its audience in `UX-007`. | **P0** | Demonstration | Change Lead |
| `SWR-004` | Every web portal shall satisfy WCAG 2.2 AA at the conformance level recorded in `UX-005`, evidenced by an automated scan and a manual audit before each portal release. | P1 | Test | UX Lead |
| `SWR-005` | Every web portal shall render without horizontal scrolling at viewport widths from 320 px upward. | P1 | Test | UX Lead |
| `SWR-006` | Every portal and application shall render its interface using the shared 1000FiX design system component library, and shall introduce no component outside it. | P1 | Inspection | UX Lead |
| `SWR-007` | Every portal shall emit instrumentation events for its declared critical funnels to the analytics platform. | P1 | Test | Analytics Lead |
| `SWR-008` | Every error message presented to a user shall state what happened and what the user shall do next, in the language of that user's session. | P1 | Inspection | Content Lead |
| `SWR-009` | No portal or application shall evaluate a business rule; client-side validation shall be presentational only, and every rule shall be enforced by the ERP on the write path. | **P0** | Analysis | Architect |
| `SWR-010` | Every portal shall enforce the session, idle-timeout, absolute-timeout and multi-factor policy defined centrally, and shall not define its own. | **P0** | Test | CISO |

### 3.12.2 Record and truth obligations

| ID | Requirement | Pri | Verif. | Owner |
|---|---|:--:|:--:|---|
| `SWR-011` | On every create, update, state transition and delete of a business object, the ERP shall write an audit record carrying the actor identity, the UTC timestamp, the object identity, the field-level before value and the field-level after value. | **P0** | Test | CISO |
| `SWR-012` | The ERP shall render every audit record immutable after write, and shall permit no role, including platform administrators, to amend or delete one. | **P0** | Test | CISO |
| `SWR-013` | The ERP shall present every user-facing string in both Bengali and English, and shall block the release of any module whose translation coverage is below 100%. | **P0** | Test | Change Lead |
| `SWR-014` | The ERP shall store every timestamp in UTC and shall display it in Asia/Dhaka unless the user's profile records another zone. | **P0** | Inspection | Architect |
| `SWR-033` | The ERP shall apply soft deletion to every business object, and shall permit hard deletion only through an approved procedure that writes its own audit record. | **P0** | Test | CISO |
| `SWR-034` | The ERP shall perform every monetary calculation in decimal arithmetic with an explicit currency, and shall use no floating-point type in any money path. | **P0** | Analysis | Finance Systems Lead |
| `SWR-035` | On every state change of a business object, the ERP shall write the corresponding domain event to the transactional outbox within the same database transaction as the state change. | **P0** | Test | Architect |
| `SWR-036` | The ERP shall enforce referential integrity at the database level in addition to the application layer. | **P0** | Inspection | DBA |

### 3.12.3 Data residency obligations

*Derived from `NFR-086a`/`086b`/`086c`, which state functional system behaviour and are therefore
requirements, not quality attributes.*

| ID | Requirement | Pri | Verif. | Owner |
|---|---|:--:|:--:|---|
| `SWR-015` | The ERP shall carry a residency classification on every field of every entity, and shall reject at write time any attempt to persist a field classified `resident` outside the Bangladesh-resident data store. | **P0** | Test | DPO |
| `SWR-016` | Before executing any cross-border transfer of a field classified `resident`, the ERP shall require an Authority notification record and a recorded safeguard, and shall block the transfer in their absence. | **P0** | Test | DPO |
| `SWR-017` | The ERP shall provision no non-production environment, in any region, containing unmasked values of any field classified `resident`. | **P0** | Inspection | Platform Lead |

### 3.12.4 Personal data protection obligations *(PDPA 2026)*

*Reallocated from `05-06` §6.3, where they are numbered `NFR-090` … `NFR-099`. Each states a
**system function** — capture consent, issue a notice, execute an erasure, notify a regulator —
and is therefore a functional requirement misclassified as a quality attribute. That
misclassification is the reason `NFR-090`/`091`/`092` were double-allocated (audit `AP-02`).*

| ID | Requirement | Pri | Verif. | Owner | Was |
|---|---|:--:|:--:|---|---|
| `SWR-018` | Before processing personal data for a purpose, the ERP shall record either a consent for that purpose or the stated legitimate ground relied on, and shall block processing where neither exists. | **P0** | Test | DPO | `NFR-090` |
| `SWR-019` | When capturing consent, the ERP shall record the purpose, the consent text version presented, the language presented, the timestamp and the channel; and for sensitive personal data shall require a specific consent distinct from any general consent. | **P0** | Test | DPO | `NFR-091` |
| `SWR-020` | Before or during processing, the ERP shall issue a transparency notice stating the data categories, purposes, risks, retention periods, third-party transfers and the withdrawal procedure, in the data subject's language. | **P0** | Demonstration | DPO | `NFR-092` |
| `SWR-021` | On receipt of a data-subject access request, the ERP shall assemble every item of personal data held on that subject across all modules and shall export it in a portable, machine-readable format. | **P0** | Demonstration | DPO | `NFR-093` |
| `SWR-022` | On a recorded rectification, the ERP shall notify every controller and processor to which the affected data was disclosed, within 30 days. | **P0** | Test | DPO | `NFR-093` |
| `SWR-023` | On a valid erasure request, the ERP shall erase the personal data across the operational store, every backup generation, the analytical warehouse and the event log, and shall retain only a tombstone carrying no personal data. | **P0** | Test | DPO | `NFR-093` |
| `SWR-024` | The ERP shall present a withdrawal-of-consent procedure no more onerous than the procedure by which consent was given. | **P0** | Demonstration | DPO | `NFR-093` |
| `SWR-025` | On detection of a personal-data breach likely to cause significant damage, the ERP shall raise a notification workflow to the National Data Management Authority within the prescribed timeframe, and shall record the assessment that determined the likelihood. | **P0** | Demonstration | CISO | `NFR-094` |
| `SWR-026` | The ERP shall retain processing records for not less than five years, and shall block their deletion before that period elapses. | **P0** | Test | DPO | `NFR-095` |
| `SWR-027` | Where 1000FiX is classified a significant data fiduciary, the ERP shall record the appointed Chief Data Officer, that role's authority and its reporting line, and shall route every statutory decision to it. | **P0** | Inspection | Company Secretary | `NFR-096` |
| `SWR-028` | The ERP shall flow the controller's obligations to every processor and sub-processor by recorded contract, and shall block data disclosure to a party with no current recorded contract. | P0 | Inspection | Legal | `NFR-098` |
| `SWR-029` | The ERP shall restrict large-scale transfer of sensitive personally identifiable data — government unique identifiers, biometric identifiers, genetic information and criminal records — and shall record the Authority notification and the safeguards applied to each transfer. | **P0** | Test | DPO | `NFR-099` |

> **`RQ-006` consequence.** With `NFR-090`–`NFR-099` reallocated to `SWR-018`–`SWR-029`, the
> `NFR-090`/`091`/`092` double-allocation recorded as audit `AP-02` **ceases to exist**: the
> maintainability requirements that shared those identifiers become their sole occupants.
> `RQ-006` §4 records the re-basing. Measurement at 02:15 (+06) additionally finds `NFR-088` and
> `NFR-089` duplicated as whole rows in `05-06` §6.2 and §6.4 — a fourth and fifth collision that
> audit `AP-02` did not report, and a table-contamination defect in §6.4 where two `NFR` rows sit
> inside the residency-field table. Recorded as `RQA-13`.

### 3.12.5 Field and offline obligations

| ID | Requirement | Pri | Verif. | Owner |
|---|---|:--:|:--:|---|
| `SWR-030` | The technician, rider and auditor applications shall permit the complete execution of their declared workflows for 24 continuous hours with no network connectivity. | **P0** | Test | Mobile Lead |
| `SWR-031` | On reconnection, the applications shall synchronise queued changes with zero data loss and zero double-application, resolving conflicts against a server-authoritative policy recorded in `AR-010`. | **P0** | Test | Mobile Lead |
| `SWR-032` | The applications shall record every offline action in an append-only local journal that survives application termination, device restart and battery exhaustion. | **P0** | Test | Mobile Lead |

### 3.12.6 Configurability and multi-entity obligations

| ID | Requirement | Pri | Verif. | Owner |
|---|---|:--:|:--:|---|
| `SWR-037` | The ERP shall permit a branch, zone, entity or country to be configured, and its workflows, forms, thresholds and rules adjusted, without a code change or a deployment. | **P0** | Demonstration | Platform Lead |
| `SWR-038` | The ERP shall permit any new capability to be enabled or disabled by feature flag without a deployment. | P1 | Demonstration | Platform Lead |
| `SWR-039` | The ERP shall isolate records at branch level such that a user's queries return only the records their role's scope permits, enforced at the data-access layer rather than in the interface. | **P0** | Test | CISO |
| `SWR-040` | The ERP shall carry entity and operating-unit fields on every custom model, and shall reject the creation of a record without them. | **P0** | Inspection | Architect |
| `SWR-041` | The ERP shall permit a second legal entity, in a second country, to be stood up from a country pack without modification to any module's code. | P2 | Demonstration | Architect |
| `SWR-042` | The ERP shall report the success, failure and duration of every scheduled job, and shall raise an alert on any job that completes without reporting. | **P0** | Test | SRE Lead |

**Count check** — regenerated by counting rows immediately before issue, per `PG-M10`:
10 + 8 + 3 + 12 + 3 + 6 = **42**. Identifiers `SWR-001` … `SWR-042`, no gaps, no duplicates.

## 3.13 Usability requirements *(§9.6.13)*

**Satisfied by reference.** See `RQ-006` §*Interaction capability* (ISO/IEC 25010:2023). The
requirements previously stated as `NFR-016` … `NFR-020` and `NFR-073` … `NFR-082` are re-based
there with a measurement method attached to each.

## 3.14 Performance requirements *(§9.6.14)*

**Satisfied by reference.** See `RQ-006` §*Performance efficiency*. `05-06` §1 carries 21
latency and throughput targets, each with a stated measurement instrument; `RQ-006` re-bases them
against ISO/IEC 25010:2023 and binds each to the functional requirements it constrains — the
binding that `PGD-000` records as absent.

## 3.15 Logical database requirements *(§9.6.15)*

Stated as **constraints on the data**, not as a model. The model is `DA-001`; the dictionary is
`DA-002`.

| # | Constraint |
|---|---|
| DB-01 | The primary datastore shall be PostgreSQL 16 |
| DB-02 | Every custom model shall carry entity and operating-unit fields (`SWR-040`) |
| DB-03 | Every custom model shall be named in the `fix.` namespace with tables in `fix_` (`AS-04`) |
| DB-04 | Every field shall carry a residency classification (`SWR-015`) and a data classification (`DA-005`) |
| DB-05 | Referential integrity shall be enforced at the database level (`SWR-036`) |
| DB-06 | Deletion shall be soft (`SWR-033`) |
| DB-07 | Database migrations shall be forward-only, tested against a production-sized dataset, and reversible by a documented procedure (`OPS-07`) |
| DB-08 | The analytical estate shall read from replicas; no analytical query shall execute against the operational primary |

> **Open.** `02-05` §8 asserts PostgreSQL 16 partitioning without naming a partition key. That is
> a `DA-001` decision; it is recorded here as a constraint that does not yet exist.

## 3.16 Design constraints *(§9.6.16)*

| # | Constraint | Source | Binding |
|---|---|---|---|
| `CN-01` | Odoo 19 Community Edition; Enterprise Edition excluded | `02-05` §2 | Absolute |
| `CN-02` | Core is never modified; extensions are separate modules | `AS-05`, `02-05` §4 | Absolute — one wrong `_inherit` makes the Odoo 20 upgrade a rewrite |
| `CN-03` | OCA modules are extended, not forked, without architecture approval | `AS-05` | Approval-gated |
| `CN-04` | Software licence cost for the ERP core is $0; each L6 commercial component requires CFO approval | `02-05` §6 | Approval-gated |
| `CN-05` | Licence obligations of AGPL-3, LGPL-3, BSL and n8n Sustainable Use shall be met | `02-05` §4 | Absolute — `CO-004` |
| `CN-06` | The pre-existing portal platform cannot be replaced | `CON-03` | Absolute |
| `CN-07` | Site adaptation by configuration, never by branch-specific code | `SWR-037` | Absolute |
| `CN-08` | Every API is versioned and published as an OpenAPI 3.1 contract | `AS-07`, `IN-002` | Absolute |
| `CN-09` | No module reads another module's tables | `AS-01` | Absolute |
| `CN-10` | No business logic in views, controllers or portal code | `AS-09`, `SWR-009` | Absolute |
| `CN-11` | Fiscal year July–June; BDT primary with lakh/crore grouping in the Bengali locale | `05-06` §9 | Absolute |
| `CN-12` | Bangladesh address hierarchy: Division → District → Upazila/Thana → Union/Ward → Postcode | `05-06` §9 | Absolute |

## 3.17 Standards compliance *(§9.6.17)*

| Standard or statute | Obligation on the software | Verified on | Register |
|---|---|---|---|
| **Personal Data Protection Act 2026** | `SWR-018` … `SWR-029`; enforcement activates ~13 May 2027, inside Wave 4 | 2026-08-12 | `SC-008`, `RR-005` |
| **Cyber Security Ordinance 2025** | `NFR-023`. Supersedes the Cyber Security Act 2023, which superseded the Digital Security Act 2018 | 2026-08-12 | `RR-005` |
| **VAT and Supplementary Duty Act 2012** | Mushak 6.3 tax invoice format; Mushak 9.1 monthly return by the 15th via vat.gov.bd; input credit blocked without a compliant 6.3 | 2026-08-12 | `M51`, `NFR-100`, `NFR-101` |
| **Bangladesh Labour Act 2006** (as amended) | Payroll, working time, leave and gratuity rules | 2026-08-12 | `M56` |
| **ISO 9001:2015** | Documented information and audit trail sufficient to have confidence the process is carried out as planned (clause 4.4.2) | 2026-08-18 | `M23` |
| **ISO/IEC 27001:2022** Annex A | Control alignment; A.8.25 requires security in every development stage | 2026-08-18 | `SC-005` |
| **WCAG 2.2 AA** | `SWR-004`. Conflicts with `NFR-073` (2.1 AA) — finding `RQA-12` | 2026-08-18 | `UX-005` |
| **OpenAPI 3.1** | `CN-08` | 2026-08-18 | `IN-002` |
| **BPMN 2.0** | Process models, constrained subset per `SP-003` §4.2 | 2026-08-18 | `RQ-007` |
| **IEEE 2883** / **ISO/IEC 19790** | Media sanitisation technique and cryptographic-erase key zeroization for `M06` destruction certificates. NIST SP 800-88 r1 is **withdrawn** (audit `H-01`) | 2026-08-12 | `SC-006` |

## 3.18 Software system attributes *(§9.6.18)*

**Satisfied by reference** to `RQ-006`, which specifies reliability, availability, security,
maintainability, flexibility, compatibility, safety and functional suitability against ISO/IEC
25010:2023, each with a target and a measurement method.

## 3.19 Verification *(§9.6.19)*

### 3.19.1 The verification method taxonomy

**Every requirement shall declare exactly one method.** This is the single largest addition this
document makes to the estate: at 02:15 (+06), **none of the 3,347 adopted rows carries one**.

| Method | Definition | Use when | Evidence produced |
|---|---|---|---|
| **Inspection** | Examination of the artefact — code, configuration, document, screen — without executing it | The requirement constrains structure, presence or form | Reviewer name, artefact version, checklist result |
| **Analysis** | Reasoning from models, calculation or static examination | Execution is impractical or the property is emergent (e.g. "no module reads another module's tables") | Analysis record, tool output, architect sign-off |
| **Demonstration** | Operating the system and observing the outcome, without instrumented measurement | The outcome is observable and binary | Scripted demonstration, witness, recording |
| **Test** | Executing the system against defined inputs and comparing to a defined expected result | The outcome is measurable, repeatable and automatable | Test case ID, run record, pass/fail, defect links |

### 3.19.2 Allocation rules

| # | Rule |
|---|---|
| `VM-01` | Every requirement carries exactly one method. Two methods means two requirements |
| `VM-02` | **Every P0 requirement shall be verified by Test or Demonstration.** Inspection alone is insufficient for a requirement whose absence blocks go-live |
| `VM-03` | A requirement verified by Inspection or Analysis shall name the artefact inspected or the model analysed |
| `VM-04` | A requirement whose method cannot be allocated fails characteristic W-07 *Verifiable* and shall be rewritten, not accepted with a blank |
| `VM-05` | The method determines the **test level** in `QA-002`: Test → unit / integration / system / E2E; Demonstration → UAT; Inspection → review gate; Analysis → architecture review |
| `VM-06` | The method is an attribute of the requirement and does not change when the wave changes |

### 3.19.3 Verification of this SRS itself

| # | How this document is verified | Method |
|---|---|---|
| V-01 | Every §9.6 clause is present and either populated or carries a recorded tailoring | Inspection |
| V-02 | The denominator reproduces from the §3.10.5 commands | Test |
| V-03 | `SWR-001` … `SWR-042` each pass checks `CK-01` … `CK-06` | Test |
| V-04 | Every identifier space in §3.10.6 was swept for collisions before allocation | Inspection — performed 02:15 (+06) |
| V-05 | Every relative link resolves (`PG-M9`) | Test |
| V-06 | Every roll-up regenerated from its source rows immediately before issue (`PG-M10`) | Inspection |

## 3.20 Supporting information *(§9.6.20)*

| Appendix | Content |
|---|---|
| **A** | The adopted requirement set — 79 files, per-file measured counts, module codes, waves |
| **B** | Language conformance measurement, full result set |
| **C** | Requirement attribute template |

---

# 4. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-01 | How to handle the 3,347 existing requirement rows | (a) Restate them in this SRS; (b) adopt by controlled reference; (c) rewrite from the BRD | **(b) Adopt by controlled reference** | (a) creates a second population that diverges — the `H-03` defect; (c) discards the programme's strongest asset | Appendix A becomes the baseline manifest; a module file change is a controlled change |
| D-02 | Where quality attributes live | (a) Here, per §9.6.13/14/18; (b) in `RQ-006` by reference | **(b) `RQ-006`** | One home per measurable target. Two homes guarantee divergence | Declared as tailoring under Annex C |
| D-03 | Whether user stories may be the requirement of record | (a) Yes, agile-style; (b) No, additional representation only | **(b) No** | 12207:2017 Annex H permits story form, but a contract cannot be accepted against 245 narratives with no verification method | `RQ-008` maps stories to requirements; the requirement governs |
| D-04 | Which ISO 25010 edition | (a) 2011, as the estate implies; (b) **2023** | **(b) 2023** | 2011 is superseded. Citing a superseded model is the `H-01` defect | `RQ-006` re-bases against 9 characteristics including Safety |
| D-05 | Whether to rename category code `RQ` on discovering the `LG-010` collision | (a) Rename; (b) Disambiguate by width and refer | **(b)** | `PGD-000` is issued and `PG-05` makes identifiers permanent. Renaming a code across an issued register is a larger defect than a documented disambiguation | Rule `ID-01`; permanent ruling deferred to `RR-002` |
| D-06 | Whether to publish a conversion effort estimate | (a) Yes; (b) No, supply measured inputs to `GV-007` | **(b)** | Publishing a fourth uncontrolled estimate is finding `PGD-A1-05` | §3.10.7 gives measured inputs; `GV-007` sizes |
| D-07 | Which WCAG version governs | (a) 2.1 AA per `NFR-073`; (b) 2.2 AA per `UX-005` | **(b) 2.2 AA** | Later, and a superset. Two live targets is the defect | Recorded as `RQA-12` for `RQ-006` to close formally |
| D-08 | Whether PDPA obligations are functional or non-functional | (a) NFRs, as `05-06` has them; (b) functional requirements | **(b) Functional** | "Capture consent", "execute an erasure", "notify the Authority" are system functions. Misclassification caused the `AP-02` collision | `SWR-018`…`SWR-029`; `RQ-006` releases the identifiers |

---

# 5. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | Who is the named business owner for each of the 79 requirement groups? The `owner` attribute cannot be populated without them | Programme Director | W1 | UAT acceptance; `RQ-010` |
| Q-02 | Does the split-residency design survive legal review (`DEP-31`, decision `D-13`)? | CTO / Legal | **Now** | `SWR-015`–`SWR-017`; Wave 1 architecture |
| Q-03 | When will `R39`–`R50` and `SOD-13`–`SOD-30` be registered? | CISO | W1 | Verification of every requirement referencing them |
| Q-04 | Which register governs `FR-ECM-` — `05-01` §1.3 (M12) or `M38`? | Enterprise Architecture | **Now** | Any build ticket citing `FR-ECM-nnn` |
| Q-05 | Is the Odoo 19 CE version claim in `02-05` currently accurate, and what is the Odoo 20 landing date? | CTO | W1 | `CN-01`, `CN-02` upgrade exposure |
| Q-06 | Should the sibling portal SRS (`Intergrated_web_portal/…04_SRS_…`) be adopted as the house SRS template in `RR-003`? | Enterprise Architecture | W2 | `RR-003` |
| Q-07 | Which requirements-management tool will hold the 13 attributes? Markdown cannot enforce `CK-01`…`CK-12` at scale | Requirements Manager | W1 | `RQ-005` §7 |

> An open question with no owner and no needed-by date is an unrecorded risk. All seven are
> escalated to `GV-005` RAID on issue.

---

# 6. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every ISO/IEC/IEEE 29148:2018 §9.6 clause is present, populated or explicitly tailored | Clause map, §3.1 |
| AC-02 | The requirement construct, the 13 attributes and the 9+5 characteristics are stated as testable rules | §3.10.2–§3.10.4, §3.10.9 |
| AC-03 | Exactly one requirement denominator is published, with its counting rule and a reproduction command | §3.10.5 |
| AC-04 | Every identifier space used or reserved was swept for collisions across all four repositories before allocation | §3.10.6, sweep at 02:15 (+06) |
| AC-05 | All 79 module and portal files are adopted by name with a measured count | Appendix A |
| AC-06 | `SWR-001` … `SWR-042` each carry a construct-conforming statement, a priority, a verification method and an owner | §3.12 |
| AC-07 | Every requirement in `SWR` passes `CK-01` … `CK-06` | Check run at issue |
| AC-08 | Every standard and statute cited carries a `verified_on` date | §2.1.3, §3.17 |
| AC-09 | Every roll-up regenerated by counting its source rows immediately before issue | `PG-M10` |
| AC-10 | Every relative link resolves | `PG-M9` |

**Definition of done.** Complete when `AC-01` … `AC-10` are met, `PGD-000`'s row for `RQ-001` is
updated with a fresh enumeration timestamp, and the ERP Design Authority has signed. Per
`PGD-A1-09`, that body does not yet exist; this document is therefore **issued for approval, not
approved**.

---

# 7. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `../../primary-doc/…BRD.md` §3, §8, §10, §13, §20 | Business objectives `BO-01`–`BO-18`, business requirements, rules, use cases |
| Upstream | `../../primary-doc/…URD.md` §6–17 | 245 user stories; mapped to requirements by `RQ-008` |
| Upstream | `../../primary-doc/…RFP.md` §5–10, §17 | 405+ procurement requirements; evaluation methodology |
| Upstream | `RR-002` | Identifier convention — must ratify the `SWR` and `SYR` reservations |
| Upstream | `GV-006` | Scope baseline control — `BL-01`…`BL-04` depend on it |
| Lateral | `RQ-002` | System requirements above the software boundary |
| Lateral | `RQ-006` | Quality attributes — §9.6.13, §9.6.14, §9.6.18 satisfied by reference |
| Lateral | `RQ-009` | Business rules constraining these requirements |
| Downstream | `RQ-003` | Fit-gap disposition per requirement; populates attribute `fit_gap` |
| Downstream | `RQ-004` | The trace from `BO` to evidence; consumes the denominator and the attributes |
| Downstream | `AR-001` | SAD derived from this requirement set and `RQ-006` |
| Downstream | `AR-003` | Design descriptions realising these requirements |
| Downstream | `DA-001`, `DA-002` | Schema and dictionary realising §3.15 |
| Downstream | `IN-002` | API contracts realising §3.11.3, §3.11.4 |
| Downstream | `QA-001`, `QA-003`, `QA-011` | Test strategy, case derivation and coverage, all keyed to the §3.19 method |
| Downstream | `CO-003` | Deliverable acceptance schedule referencing this baseline |
| Lateral | `../../1000fix_ERP_Module/03_Modules/` | The 79 specifications adopted in Appendix A |
| Lateral | `../../project_content/13_Test_and_Acceptance_Content/` | 18 test content packs consuming these requirements |

---

# 8. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
[`RQ-002`](RQ-002_System_Requirements_Specification.md) ·
[`RQ-003`](RQ-003_Fit_Gap_Analysis_and_Functional_Design_Specification.md) ·
[`RQ-004`](RQ-004_Requirements_Traceability_Matrix.md) ·
[`RQ-005`](RQ-005_Requirements_Management_Plan.md) ·
[`RQ-006`](RQ-006_Non_Functional_Requirements_Specification.md) ·
[`RQ-007`](RQ-007_Business_Process_Model_Repository.md) ·
[`RQ-008`](RQ-008_Use_Case_and_User_Story_Specification.md) ·
[`RQ-009`](RQ-009_Business_Rules_Specification.md) ·
[`RQ-010`](RQ-010_Acceptance_Criteria_and_Definition_of_Done_Standard.md) ·
[`../_templates/TPL_Guiding_Document.md`](../_templates/TPL_Guiding_Document.md) ·
[`../_AUDIT/PGD-AUDIT-001_Register_Integrity_Audit.md`](../_AUDIT/PGD-AUDIT-001_Register_Integrity_Audit.md)

**Workspace**
`../../1000fix_ERP_Module/03_Modules/` (67 modules, 12 portals) ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-01`…`05-06` ·
`../../1000fix_ERP_Module/02_Architecture/02-01`, `02-02`, `02-05` ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01`, `06-02` ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md` ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_URD.md` ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` ·
`../../project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-001`…`SP-003` ·
`../../project_content/13_Test_and_Acceptance_Content/TS-001`…`TS-018`

**External standards and sources**

| Reference | Verified on |
|---|---|
| ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life cycle processes — Requirements engineering* (2nd edition; cancels and replaces 29148:2011) | 2026-08-18 |
| ISO/IEC 25010:2023, *SQuaRE — Product quality model* (revises the product quality model of 25010:2011) | 2026-08-18 |
| ISO/IEC/IEEE 12207:2017, Annex H (agile formulations) | 2026-08-18 |
| IEEE 1016-2009, *Software design descriptions* | 2026-08-18 |
| W3C WCAG 2.2, Level AA | 2026-08-18 |
| OMG BPMN 2.0 | 2026-08-18 |
| Personal Data Protection Act 2026 (Law 63 of 2026), Bangladesh | 2026-08-12 |
| Cyber Security Ordinance 2025, Bangladesh | 2026-08-12 |
| VAT and Supplementary Duty Act 2012, Bangladesh | 2026-08-12 |

---

# Appendix A — The Adopted Requirement Set

**Manifest of the baseline.** 79 files, enumerated 2026-08-18 02:15 (+06). A requirement row not
in a file below is not in the requirement set.

| Module | Code | Cat | Wave | Pri | FR rows |
|---|---|:--:|---|:--:|---:|
| M01 Service Request & Order Management | `SRM` | A | W1→W2 | P0 | 70 |
| M02 Field Service & Dispatch Management | `FSM` | A | W2 | P0 | 63 |
| M03 Service Logistics & Reverse Logistics | `LOG` | A | W3 | P1 | 42 |
| M04 Branch & Front Desk Operations | `FRD` | A | W1 | P1 | 31 |
| M05 Remote Support & Managed Services | `RMS` | A | W5 | P1 | 62 |
| M06 Data Services & Secure Data Handling | `DTS` | A | W6 | P2 | 38 |
| M31 Workshop & Depot Repair Management | `WSR` | A | W2 | P1 | 53 |
| M07 CRM, Sales Pipeline & Account Management | `CRM` | B | W1 | P1 | 46 |
| M10 Loyalty, Membership & Rewards | `LOY` | B | W2 | P1 | 44 |
| M27 Omnichannel Contact Centre | `CCE` | B | W4 | P1 | 58 |
| M32 Conversational AI & Virtual Assistant | `CAI` | B | W4 | P1 | 38 |
| M33 Customer & Party Master Management | `CPM` | B | W1 | P0 | 52 |
| M34 Customer Experience, Feedback & Complaints | `CXM` | B | W4 | P1 | 42 |
| M35 Marketing Campaigns & Demand Generation | `MKT` | B | W5 | P2 | 40 |
| M08 Contract Lifecycle Management | `CTR` | C | W4 | P1 | 62 |
| M09 Warranty, Protection Plans & Claims | `WTY` | C | W4 | P0 | 66 |
| M11 Pricing, Rate Cards & Dynamic Pricing | `PRC` | C | W3→W7 | P1 | 52 |
| M12 Marketplace & Seller Ecosystem | `MKP` | C | W7 | P1 | 78 |
| M36 Quotation, Estimation & Tender Management | `QTE` | C | W3 | P1 | 48 |
| M37 Product & Service Catalogue Management | `CAT` | C | W1 | P0 | 46 |
| M38 E-Commerce & Digital Storefront | `ECM` | C | W7 | P1 | 56 |
| M39 Subscription & Recurring Revenue | `SUB` | C | W4 | P1 | 44 |
| M40 Partner, Channel, Alliance & Franchise | `PCM` | C | W7 | P2 | 42 |
| M13 Rental & Equipment as a Service | `RNT` | D | W6 | P2 | 44 |
| M14 Trade-In, Refurbishment & Resale | `TRF` | D | W6 | P2 | 39 |
| M18 E-Waste, Recycling & Circular Economy | `ESG` | D | W8 | P3 | 26 |
| M15 Spare Parts & Inventory Management | `INV` | E | W2 | P0 | 54 |
| M16 Procurement & Strategic Sourcing | `PRO` | E | W3 | P1 | 38 |
| M41 Warehouse Management | `WMS` | E | W3 | P1 | 41 |
| M42 Supplier Relationship & Performance | `SRM2` | E | W4 | P1 | 34 |
| M43 Demand Planning & Replenishment | `DPL` | E | W6 | P2 | 32 |
| M44 Import, Trade Compliance & Landed Cost | `ITC` | E | W6 | P2 | 36 |
| M17 Device & Customer Asset Registry | `AST` | F | W2 | P1 | 52 |
| M45 Enterprise Asset & Test Equipment | `EAM` | F | W5 | P2 | 46 |
| M46 Fleet & Vehicle Management | `FLT` | F | W5 | P2 | 44 |
| M47 Facility, Branch Infrastructure & Workplace | `FAC` | F | W7 | P3 | 44 |
| M48 IoT Telemetry & Predictive Maintenance | `IOT` | F | W8 | P2 | 46 |
| M19 Financial Accounting & General Ledger | `FIN` | G | W3 | P0 | 46 |
| M20 Accounts Receivable, Invoicing & Collections | `ARB` | G | W3 | P0 | 44 |
| M49 Fixed Assets & Capital Investment | `FXA` | G | W5 | P2 | 34 |
| M50 Treasury, Cash & Banking | `TRE` | G | W3 | P1 | 42 |
| M51 Tax & Regulatory Compliance Bangladesh | `TAX` | G | W4 | P0 | 45 |
| M52 Accounts Payable & Employee Expense | `APE` | G | W3 | P1 | 38 |
| M53 Revenue Recognition, Commission & Settlement | `REV` | G | W4→W7 | P1 | 44 |
| M54 Cost Accounting, Budgeting & FP&A | `FPA` | G | W6 | P2 | 40 |
| M21 Core HR & Employee Lifecycle | `HCM` | H | W5 | P1 | 46 |
| M22 Learning, Competency & Certification | `LMS` | H | W5 | P2 | 40 |
| M55 Time, Attendance & Workforce Scheduling | `WFM` | H | W5 | P1 | 52 |
| M56 Payroll, Benefits & Statutory Compliance | `PAY` | H | W5 | P0 | 54 |
| M57 Performance, Incentives & Compensation | `PIC` | H | W5 | P1 | 42 |
| M58 Talent Acquisition & Onboarding | `TAO` | H | W6 | P2 | 34 |
| M59 Health, Safety & Wellbeing | `HSE` | H | W6 | P2 | 42 |
| M23 Quality Management System | `QMS` | I | W5 | P1 | 48 |
| M24 Document, Records & E-Signature | `DMS` | I | W3 | P1 | 42 |
| M60 Governance, Risk & Compliance | `GRC` | I | W6 | P2 | 44 |
| M61 Knowledge Management & Technical Library | `KMS` | I | W6 | P2 | 36 |
| M25 Business Intelligence & Reporting | `BID` | J | W4 | P1 | 34 |
| M26 AI/ML Services & Model Operations | `AIM` | J | W6→W8 | P2 | 42 |
| M62 Data Platform, Warehouse & Governance | `DAT` | J | W4→W8 | P1 | 38 |
| M63 Process Automation & Workflow Orchestration | `BPA` | J | W3 | P1 | 32 |
| M28 Integration, API & Event Platform | `IPF` | K | W1 | P0 | 57 |
| M29 Identity, Access & Information Security | `SEC` | K | W1 | P0 | 52 |
| M30 Platform Administration & Configuration | `ADM` | K | W1 | P0 | 40 |
| M64 Master Data Management & Configuration | `MDM` | K | W2 | P1 | 34 |
| M65 Multi-Entity, Multi-Country & Localisation | `GLO` | K | W9 | P2 | 36 |
| M66 Internal IT Service Management | `ITS` | K | W6 | P2 | 30 |
| M67 Project, Program & Portfolio Management | `PPM` | K | W7 | P2 | 32 |
| | | | | **Module total** | **2,989** |

| Portal | Range | Wave | Pri | FR rows |
|---|---|---|:--:|---:|
| P01 Customer Self-Service Portal & Mobile Application | `FR-POR-001…040` | W2 web, W6 native | P0 | 40 |
| P02 Technician Mobile Application | `FR-POR-041…078` | W2 | P0 | 38 |
| P03 Admin Operations Portal | `FR-POR-079…112` | W1 | P0 | 34 |
| P04 Corporate B2B Portal | `FR-POR-113…144` | W4 | P1 | 32 |
| P05 Vendor & Supplier Portal | `FR-POR-145…170` | W3 | P1 | 26 |
| P06 Analytics & Executive Dashboard | `FR-POR-171…194` | W4 | P1 | 24 |
| P07 Marketplace Seller Portal & Application | `FR-POR-195…228` | W7 | P1 | 34 |
| P08 Brand Partner Portal | `FR-POR-229…254` | W4 | P1 | 26 |
| P09 Logistics & Rider Application | `FR-POR-255…282` | W3 | P1 | 28 |
| P10 Contact Centre Agent Console | `FR-POR-283…310` | W4 | P1 | 28 |
| P11 Field Auditor & Quality Application | `FR-POR-311…334` | W5 | P2 | 24 |
| P12 Partner & Referral Portal | `FR-POR-335…358` | W7 | P2 | 24 |
| | | | **Portal total** | **358** |

**Baseline total: 2,989 + 358 = 3,347 adopted + 42 specified here = 3,389.**
*Regenerated by counting the rows above immediately before issue, per `PG-M10`.*

---

# Appendix B — Language Conformance Measurement

Executed against all 3,347 adopted requirement rows at 2026-08-18 02:15 (+06).

| Construct class | Term | Occurrences |
|---|---|---:|
| **Modal** | `shall` | **0** |
| | `must` (prohibited) | 13 |
| | `should` in obligation position | 1 |
| **Loophole** | `where possible` | 4 |
| | `as appropriate` | 1 |
| | `as applicable` | 1 |
| **Superlative / subjective** | `best` | 5 |
| | `significant` | 2 |
| | `sufficient` | 2 |
| | `minimal` | 1 |
| | `able to` | 1 |
| **Totality** | `every` | 318 |
| | `any` | 181 |
| | `never` | 71 |
| | `all` | 58 |
| | `always` | 8 |
| | **Totality subtotal** | **636** |

**Requirement-table header formats found — 431 tables**

| Header | Tables |
|---|---:|
| `\| FR ID \| Feature \| Function \| Pri \| Layer \|` | 346 |
| `\| FR ID \| Feature \| Function — "The system shall…" \| Pri \| Layer \|` | 67 |
| `\| FR ID \| Feature \| Function — "The portal shall…" \| Pri \| Layer \|` | 7 |
| `\| FR ID \| Feature \| Function \| Pri \| Wave \|` | 6 |
| `\| FR ID \| Feature \| Function — "The application shall…" \| Pri \| Layer \|` | 3 |
| `\| FR ID \| Feature \| Function — "The portal shall…" \| Pri \| Wave \|` | 1 |
| `\| FR ID \| Feature \| Function — "The console shall…" \| Pri \| Layer \|` | 1 |

No table carries a `Verification`, `Source`, `Owner` or `Rationale` column. Seven header formats
means the row schema is not standardised, which is why `CK-05` cannot be run against the estate
until conversion.

---

# Appendix C — Requirement Attribute Template

```yaml
id: FR-SRM-014                     # permanent, never reused
title: Estimate approval loop      # <= 8 words, noun phrase
statement: >                       # [Condition][Subject][Action][Object][Constraint]
  When a diagnostic estimate is issued to a customer, the ERP shall record the
  customer's approval or rejection against the estimate version presented, and
  shall expire an unanswered estimate at the interval configured for its
  business line.
rationale: >                       # mandatory for P0
  Silent estimate expiry is the largest source of stalled service orders in
  the current operation (BRD 6.3).
source: M01 §5.4; URD US-SRM-014; BRU-SRM-13
owner: Service Operations Manager  # role, never a person
priority: P0                       # P0 | P1 | P2 | P3
verification_method: Test          # Inspection | Analysis | Demonstration | Test
status: Approved                   # Proposed|Approved|Allocated|Built|Verified|Accepted|Deferred|Superseded|Retired
wave: W1                           # exactly one
layer: L5                          # L1..L6, provisional until RQ-003
residency: n-a                     # resident | regional | n-a
fit_gap: build                     # fit|configure|extend|build|undetermined — owned by RQ-003
depends_on: [FR-SRM-011, FR-CAT-004]
```

---

# 9. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Denominator fixed at 3,347 (`CR-01`); `SWR-001`…`SWR-042` specified; PDPA obligations reallocated from `NFR-090`…`NFR-099`; findings `RQA-01`…`RQA-13` raised | *Pending — `GV-002`* |

---

*`RQ-001` · Category 01 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
