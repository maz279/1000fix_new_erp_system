---
id: AR-001
title: Software Architecture Document (SAD)
category: 02 — Architecture & Design
code: AR
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Architect
approver: Design Authority (constituted under GV-002)
standards_basis: ISO/IEC/IEEE 42010:2022 · ISO/IEC 25010:2023 · arc42 7.0 · C4 model · TOGAF 10 ADM Phases B–D
traces_to: >
  PGD-000 AR-001 · audit findings C-01, C-05, AP-01, AP-02, OP-01, OP-02, H2-02 ·
  NFR-001…NFR-101 (05-06) · AS-01…AS-15 · CON-03 · DEP-31 / D-13
depends_on: RQ-006 (NFR set) · AR-002 (enterprise position) · AR-008 (domain model)
verified_on: 2026-08-18
priority: P0
needed_by: Now
enumeration_timestamp: 2026-08-18 02:05 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# AR-001 — Software Architecture Document (SAD)

### Category 02 · Code `AR` · ISO/IEC/IEEE 42010:2022 — Architecture Description

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** This document's row exists in `PGD-000` Category 02 as `AR-001`.
> 2. **`PG-03` Count, do not consult.** Every figure describing the estate in this document was
>    counted from the filesystem at **2026-08-18 02:05 (+06)**. Where a counted figure disagrees
>    with a figure published in `02-02`, `02-05` or the Technology Stack Specification, the counted
>    figure is used and the disagreement is recorded in §2.4.
> 3. **`PG-06` Cite standards.** Conformance and departures are stated in §2.1.
> 4. **`PG-M4` Verify citations.** Statutory and vendor-version claims carry `verified_on: 2026-08-18`.

---

## 1. Purpose

This document is the **controlling architecture description** for the 1000FiX ERP System v2.0. It
states who the architecture must satisfy, what concerns it must answer, and it answers them through
a set of coherent **views**, each governed by a declared **viewpoint**. It exists so that eighty-plus
build deliverables across five technology stacks, produced over thirty-six months by a changing team,
assemble into one system rather than eighty.

It unblocks four things that cannot start without it: the detailed design (`AR-003`), the threat
model (`SC-002`, which needs trust boundaries), the network and environment design (`PE-001`,
`PE-002`, which realise the deployment view), and the repository structure (`BE-004`, which realises
the development view).

**What makes this document different from what already exists.** `02-01` is a *system map*: it shows
what the parts are. The Technology Stack Specification is a *stack specification*: it shows what each
part is built from. Neither states **whose concerns the structure serves**, **what quality-attribute
scenario each structural decision was chosen to satisfy**, or **what would have to be true for the
structure to be wrong**. That is what an architecture description under ISO/IEC/IEEE 42010 adds, and
it is the whole of the gap `PGD-000` §0.2 names.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | Stakeholders, their concerns, and the traceability from concern to view |
| 2 | Seven architecture viewpoints and the seven views that conform to them |
| 3 | The system context — what is inside the system boundary and what is outside it |
| 4 | Component and connector structure across 67 modules, 12 experience surfaces, 16 domain services and 24 standalone open-source systems |
| 5 | Runtime behaviour for the six architecturally significant scenarios |
| 6 | The physical/deployment structure, including the split-residency topology and six trust zones |
| 7 | **Quality-attribute scenarios** derived from `05-06` NFRs, in six-part form, with the architectural tactic that satisfies each |
| 8 | Architecturally significant requirements (ASRs) and constraints |
| 9 | Architecture rationale — why this structure, and what was rejected |
| 10 | Correspondence rules that keep the seven views consistent with each other |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Per-module class, method and algorithm design | `AR-003` SDD | A SAD describes the system; an SDD describes a module. Mixing them makes the SAD unmaintainable at 67 modules |
| The full rationale record for each decision, with rejected options | `AR-004` ADR Library | §11 of this document is an index; the durable record is one ADR per decision |
| Physical schema, DDL, column types, indexes | `DA-001` | The data **view** here states stores, ownership and residency; the **schema** is a data-architecture artefact |
| OpenAPI contracts | `IN-002` | The interface **view** states families, boundaries and rules; the contract is machine-readable and separately versioned |
| Event payload schemas and the full catalogue | `AR-009`, `IN-003` | This document fixes the messaging *architecture*; `AR-009` designs it and `IN-003` registers the events |
| Network CIDR, VPC, security-group and DNS design | `PE-001` | The deployment view states zones and adjacency; the network design realises them |
| Threat enumeration and mitigations | `SC-002` | The security view states trust boundaries; STRIDE enumeration is performed against them |
| Module boundary adjudication | `AR-005` | The logical view states the decomposition; contested boundaries are adjudicated in a register |
| Technology selection and currency | `AR-013`, `02-05`, Technology Stack Specification | This document records architecturally significant selections only, as ASR constraints |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Implementation vendor / bid respondent** | To understand what must be assembled, at what boundaries, against what quality targets — before pricing |
| **Solution Architect, lead developers** | As the authority on structure. Where a design decision is not in `AR-003`, it is decided here or escalated |
| **Design Authority (`GV-002`)** | As the artefact against which architecture change requests are assessed |
| **Head of InfoSec, DPO** | §8 trust boundaries and §9.4 residency are the inputs to `SC-002` and `SC-003` |
| **Platform engineers** | §8 deployment view and §9 quality scenarios are the inputs to `PE-001`…`PE-005` |
| **QA lead** | §10 quality-attribute scenarios are directly testable; each names its measurement method |
| **CTO, Steering Committee** | §12 rationale and §13 open questions state what is decided, what is assumed, and what still needs a decision |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / concept | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO/IEC/IEEE 42010:2022** | Architecture description contents | §3 identifies stakeholders and concerns; §4 declares viewpoints; §5–§9 are views governed by them; §9.6 records correspondences; §12 records rationale | **None.** The 2022 revision's `architecture description` conformance requirements are met in full |
| ISO/IEC/IEEE 42010:2022 | §5.4 Architecture viewpoints | Seven viewpoints declared with stakeholders, concerns, model kinds and notation | The standard permits reuse of library viewpoints. We reuse arc42/4+1 names because the vendor market recognises them, rather than inventing local names |
| **ISO/IEC 25010:2023** | Product quality model | §10 quality-attribute scenarios are grouped by the 25010 characteristics; each NFR in `05-06` is mapped to one | `05-06` predates this mapping and groups NFRs by an informal scheme. §10.1 provides the crosswalk rather than renumbering `05-06`, because NFR identifiers are permanent under `RG-02` |
| **arc42 7.0** | Template sections 3, 5, 6, 8, 9, 11 | Context, building-block, runtime, cross-cutting-concept, decision and risk sections are present | arc42 sections 1, 2, 4, 7, 10 are covered by `RQ-001`, `AR-013`, `AR-004`, `PE-001` and `AR-012` respectively and are cross-referenced, not duplicated (`PG-02`) |
| **C4 model** | Levels 1–3 | §5 context (L1), §6 containers (L2), §6.4 components (L3) | Level 4 (code) is `AR-003`'s. C4 is used as a *notation*, not as the conformance standard |
| **TOGAF 10 ADM** | Phases B, C, D | Business, information-systems and technology architecture content is present | TOGAF's full artefact set is not produced. The programme is a single-system build, not an enterprise-transformation portfolio; `AR-002` carries the enterprise-level content |
| **ISO/IEC 27001:2022** | Annex A.8.25–A.8.27 | Secure architecture principles are stated in §8 and enforced in `AR-012` | The ISMS itself is `LG-021`/`SC-005`'s |

### 2.2 Source material relied on

Every source was opened and read; none is cited from a register entry.

| Source | Location | What it establishes for this document |
|---|---|---|
| Technology Stack Specification v2.0 §3, §12, §14, §16, §23, §24, §25 | `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` | **The single richest input.** Trust zones Z0–Z6, split-residency topology, four data-flow traces, 27-entry decision log, 18-entry technology risk register, five version-currency findings verified 2026-08-13 |
| ERP Module Architecture & System Map | `../../1000fix_ERP_Module/02_Architecture/02-01_*.md` | Layer model L1–L6, shared kernel, data isolation tiers T0–T5, nine business lines, architecture standards AS-01…AS-15 |
| Module Catalogue Master Register v2.3 | `../../1000fix_ERP_Module/02_Architecture/02-02_*.md` | 67 modules in 11 categories; register rules RG-01…RG-06; DoD-01…DoD-17; wave allocation |
| Technology Stack & Build-vs-Buy | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` | Layer allocation percentages, licence obligations, TD-01…TD-15 |
| Data Model & Entity Catalogue | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_*.md` | 225 entities, DM-01…DM-15, classification S0–S3, index and partition design |
| Integration & API Catalogue | `.../05-03_*.md` | 47 integrations, 12 API families, API-01…API-12, IP-01…IP-10, event envelope, offline protocol |
| Role, Permission & Access Matrix | `.../05-04_*.md` | Role register R01–R38 (+8 unregistered), SOD-01…SOD-12 (+18 unregistered) |
| Non-Functional Requirements | `.../05-06_*.md` | NFR-001…NFR-101, split residency NFR-086/086a/086b/086c, PDPA obligations NFR-090…NFR-099 |
| Portal & Application Suite | `../../1000fix_ERP_Module/04_Portals_and_Applications/04-00_*.md` | P01–P12 users, volumes, technology, cross-portal standards PS-01…PS-12 |
| All 67 module specifications §3, §10, §12 | `../../1000fix_ERP_Module/03_Modules/**/M*.md` | Scope boundaries, owned entities, published events — the extraction in §7.4 and §2.4 |
| Implementation Roadmap | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_*.md` | Nine waves, team model, gate criteria — the constraint on incremental architecture delivery |
| Category 15 `AP` Content Audit | `../../project_content/_AUDIT/AUDIT-016_*.md` | Findings `AP-01` (21 unregistered events) and `AP-02` (NFR identifier collision) |
| Register Integrity Audit | `../_AUDIT/PGD-AUDIT-001_*.md` | The evidence standard this document's status claim must meet |

### 2.3 Audit findings this document closes, or contributes to closing

| Finding | Source | How this document contributes |
|---|---|---|
| `C-01` Two architectures described simultaneously | `00-06` | §6.2 states the 11-category decomposition as the single logical decomposition and formally retires the 5-pillar view. Closed |
| `C-05` Single-region topology conflicts with NFR-099 | `00-06` | §8.3 makes split residency the deployment view, with the residency service as the single enforcement point. Contributes; closes with `SC-007` |
| `AP-01` 21 event names consumed and unregistered | `AUDIT-016` | §7.4 measures the true gap (**988 declared vs 64 registered**) and §7.3 fixes the naming convention that caused it. Contributes; closes with `AR-009` + `IN-003` |
| `AP-02` `NFR-090/091/092` each carry two requirements | `AUDIT-016` | §10.1 uses the `-M` disambiguation suffix consistently and lists the collision as ASR-blocking. Contributes; closes in `05-06` |
| `OP-01` No lawful DR path for resident personal data | `AUDIT-017` | §8.4 requires a Bangladesh-resident DR target as a deployment-view constraint, not an operations decision. Contributes; closes with `PE-007` + `SC-007` |
| `OP-02` `dr` named in architecture, sized nowhere | `AUDIT-017` | §8.5 gives `dr` a sizing basis derived from RPO/RTO in QAS-06. Contributes; closes with `PE-002` |
| `H2-02` M66/M67 specifications do not exist | `00-07`, `02-02` §3 | **Now factually stale — both exist on disk.** Recorded in §2.4 and referred for register correction |
| `M-09` Wave capacity never validated against effort | `02-02` §4.2 | §11.3 states the architectural consequence: W1 carries 15 infrastructure components regardless of module count. Contributes; closes with `GV-004` |

### 2.4 Enumeration — counted figures, and where they disagree with published ones

Counted from the filesystem at **2026-08-18 02:05 (+06)**, per `PG-03` and `RG-06`. Rule `RG-08`
(timestamped enumeration, proposed twice and never ratified) is applied here voluntarily.

| Figure | Published | **Counted 2026-08-18 02:05** | Disposition |
|---|---|---|---|
| Module specification files on disk | 65 of 67 (`02-02` §3, 2026-08-13) | **67 of 67** | **Published figure is stale.** `M66_Internal_IT_Service_Management.md` (86,888 bytes) and `M67_Project_Program_and_Portfolio_Management.md` (82,463 bytes) were written 2026-08-13 17:27. Referred to Enterprise Architecture as finding `PGD-A3-01` |
| Portal specification files | 12 | **12** | ✓ |
| Technology Stack Spec §25.1.1 "two specifications do not exist" | Stated 2026-08-14 | **False at time of writing** | Both files predate the TSS by ~22 hours. Referred as finding `PGD-A3-01` |
| `project_content/` files | 468 (`PGD-000`, 01:39) | **476** | **Baseline moved again — third independent occurrence** of `PGD-A1-03` / `AP-17`. Referred as finding `PGD-A3-02` |
| Workspace total excluding `project-guide-doc/` | 601 | **609** | As above |
| Machine-readable engineering artefacts (`*.yaml,yml,json,sql,tf,py`) | 0 | **0** | ✓ — the register's central claim holds |
| Domain events registered in `05-03` §4.2 | "Principal events" | **64 rows** | Not 70 as the TSS §3.1 states. Referred as finding `PGD-A3-03` |
| Domain events declared published in module §12.3 tables | not stated anywhere | **988 distinct** | See §7.4. This is the true event surface |
| Events declared published but not registered | 21 (`AP-01`) | **953** | `AP-01` compared three files; this extraction covers all 67. Referred as finding `PGD-A3-04` |
| Events registered but published by no module §12.3 | not stated | **29** | Naming-convention divergence, not absence. See §7.3 |
| Entities catalogued in `05-02` | 225 (for 30 modules) | **1,335 distinct declared owned across 67** | `05-02` covers ~17% of the current model. Referred as finding `PGD-A3-13`; see `AR-008` §2.3. **Every entity figure in this document set uses the counted 1,335** |
| Entities declared owned by **more than one** module | not stated | **34** | Adjudicated in `AR-008` §7 |

> **Why this section exists at the front of a SAD.** Two of the estate's three repository audits found
> that the largest defect class was a summary written before the thing it summarised was finished.
> An architecture description that opens by asserting counts it did not take would reproduce that
> defect at the top of the document that everything else inherits from.

---

## 3. Stakeholders and Concerns

ISO/IEC/IEEE 42010 §5.3 requires that an architecture description identify the stakeholders it
serves and the concerns it addresses, and that every concern be **framed by at least one
viewpoint**. The matrix in §4.2 discharges that requirement.

### 3.1 Stakeholder register

| # | Stakeholder | Represented by | Primary concerns |
|---|---|---|---|
| SH-01 | **Executive sponsor / Board** | CEO, Steering Committee | Does the structure deliver the benefit case at the funded cost? Is the programme recoverable if a wave fails? |
| SH-02 | **CTO / Design Authority** | CTO | Is the system changeable over 36 months and three Odoo major versions? Is drift detectable? |
| SH-03 | **Implementation vendor** | Bid respondent, delivery partner | What exactly must be built, at what boundaries, to what acceptance standard? |
| SH-04 | **Solution Architect and lead developers** | Delivery squads | Where does my code go, what may it call, what must it emit? |
| SH-05 | **Head of InfoSec** | InfoSec function | Where are the trust boundaries? What is inside which zone? What is the blast radius of a compromise? |
| SH-06 | **Data Protection Officer / Chief Data Officer** | DPO (role R40, unregistered — see §13 Q-04) | Where does residency-classified personal data live, and can that be proved to the National Data Management Authority? |
| SH-07 | **CFO / Finance** | CFO, Finance Manager | Is financial truth single-sourced and reconcilable? Is licence cost genuinely $0 at the core? |
| SH-08 | **Service Operations Director** | Branch and field leadership | Does the field keep working when connectivity does not? |
| SH-09 | **Platform engineers / SRE** | Platform squad | Can this be deployed repeatably, observed, recovered and scaled? |
| SH-10 | **QA lead** | QA function | Which architectural claims are testable, and by what method? |
| SH-11 | **Brand partners (17+), corporate clients, marketplace sellers** | Partner-facing surfaces P04, P07, P08 | Are the contracts we integrate against stable and versioned? |
| SH-12 | **Regulators** — NBR, National Data Management Authority | Compliance function | Are statutory records produced, retained, and are transfers lawful and evidenced? |
| SH-13 | **Portal platform owner** | Digital team | Does the ERP respect `CON-03` — the platform exists and cannot be replaced? |

### 3.2 Concern register

| # | Concern | Raised by | Framed in view |
|---|---|---|---|
| CN-01 | **Boundary integrity** — 67 modules must not become one entangled system | SH-02, SH-04 | Logical (§6), Development (§7) |
| CN-02 | **Upgrade survivability** — Odoo 19 → 20 → 21 across 36 months | SH-02, SH-03 | Development (§7), Rationale (§12) |
| CN-03 | **Single source of financial truth** | SH-07, SH-12 | Logical (§6), Information (§7.5) |
| CN-04 | **Field operation without connectivity** — 24 hours, zero data loss | SH-08 | Runtime (§7), and in full in `AR-010` |
| CN-05 | **Lawful residency of sensitive personal data** | SH-06, SH-12 | Deployment (§8), Security (§8.3) |
| CN-06 | **Blast-radius containment** — marketplace, remote support, recovered customer data | SH-05 | Security (§8.3) |
| CN-07 | **Contract stability for 12 surfaces and external consumers** | SH-03, SH-11, SH-13 | Interface (§7.3), Logical (§6.5) |
| CN-08 | **Reliable state propagation** — every state change produces exactly one event | SH-04, SH-09 | Runtime (§7.4) |
| CN-09 | **Deployability, observability, recoverability** | SH-09 | Deployment (§8), Operational (§9) |
| CN-10 | **Performance and scale headroom** — 5× users, 10× data over 5 years | SH-01, SH-09 | Deployment (§8.5), Quality scenarios (§10) |
| CN-11 | **Testable architecture** — claims that can fail a build | SH-10, SH-02 | Quality scenarios (§10), and in full in `AR-012` |
| CN-12 | **Cost discipline** — $0 licence at the core, bounded L6 | SH-01, SH-07 | Rationale (§12), and in full in `AR-013` |
| CN-13 | **Bengali-first behaviour is structural, not cosmetic** | SH-08, SH-12 | Cross-cutting concepts (§9.3) |
| CN-14 | **Multi-entity and multi-country readiness without a rebuild** | SH-01, SH-02 | Logical (§6.6), Information (§7.5) |

---

## 4. Viewpoints

### 4.1 Viewpoint catalogue

Each viewpoint declares the stakeholders it serves, the concerns it frames, its model kinds and its
notation. This is the ISO/IEC/IEEE 42010 §5.4 obligation that `02-01` does not discharge.

| # | Viewpoint | Stakeholders | Concerns framed | Model kinds | Notation |
|---|---|---|---|---|---|
| **VP-1 Context** | SH-01, SH-03, SH-11, SH-13 | CN-07, CN-12 | System context diagram; external-entity register | C4 Level 1; table |
| **VP-2 Logical** | SH-03, SH-04, SH-07 | CN-01, CN-03, CN-14 | Module decomposition; layer allocation; shared-kernel model; business-line specialisation | C4 Level 2–3; table; text |
| **VP-3 Interface** | SH-03, SH-04, SH-11, SH-13 | CN-07, CN-08 | API family map; event catalogue structure; integration pattern register | Table; envelope schema |
| **VP-4 Runtime / Process** | SH-04, SH-08, SH-09 | CN-04, CN-08 | Scenario traces; concurrency and transaction model; failure and degradation model | Sequence trace; table |
| **VP-5 Development** | SH-02, SH-03, SH-04 | CN-01, CN-02 | Repository structure; layer-extension rules; build sequence; dependency constraint set | Table; dependency graph |
| **VP-6 Deployment** | SH-05, SH-06, SH-09, SH-12 | CN-05, CN-06, CN-09, CN-10 | Trust-zone model; environment ladder; residency topology; sizing basis | Zone diagram; table |
| **VP-7 Operational** | SH-09, SH-10 | CN-09, CN-11 | Observability model; job and schedule model; degradation and fallback register | Table |

### 4.2 Concern-to-view coverage — the 42010 conformance check

**Every concern is framed by at least one viewpoint, and every viewpoint frames at least one
concern.** Verified by construction; re-verify at every architecture change.

| Concern | VP-1 | VP-2 | VP-3 | VP-4 | VP-5 | VP-6 | VP-7 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| CN-01 Boundary integrity | | ● | ○ | | ● | | |
| CN-02 Upgrade survivability | | ○ | | | ● | ○ | |
| CN-03 Financial single truth | | ● | ○ | ○ | | | |
| CN-04 Offline field operation | | ○ | ○ | ● | | ○ | ○ |
| CN-05 Lawful residency | | ○ | | ○ | | ● | ○ |
| CN-06 Blast-radius containment | ○ | ○ | | | | ● | ○ |
| CN-07 Contract stability | ● | ○ | ● | | ○ | | |
| CN-08 Reliable state propagation | | | ● | ● | ○ | | ○ |
| CN-09 Deploy / observe / recover | | | | ○ | ○ | ● | ● |
| CN-10 Performance and scale | | | ○ | ○ | | ● | ○ |
| CN-11 Testable architecture | | ○ | ○ | | ● | | ● |
| CN-12 Cost discipline | ● | ○ | | | ○ | ○ | |
| CN-13 Bengali-first structural | ○ | ○ | ○ | | ○ | | |
| CN-14 Multi-entity readiness | | ● | | | | ○ | |

● primary · ○ contributing

---

## 5. Context View (VP-1)

### 5.1 System boundary

```
                      ┌──────────────────────── OUTSIDE THE BOUNDARY ────────────────────────┐
                      │                                                                       │
  Individual          │  17+ brand      500–2,000        3 payment      NBR VAT Online       │
  customers           │  partners       marketplace      rails          (vat.gov.bd)          │
  250,000+/mo         │                 sellers          bKash·Nagad·                         │
                      │                                  SSLCOMMERZ     National Data         │
  Corporate &         │  Courier        Banks            Bangladesh     Management Authority  │
  government          │  partners       (BEFTN,          SMS gateways   (breach notification) │
  clients             │  Pathao·RedX·   statements)      ×2                                   │
  500–2,000           │  Steadfast                       WhatsApp       Payload CMS portal    │
                      │                 KYC / NID        Business       platform (CON-03 —    │
  500+ employees      │  Recycling      verification     Cloud API      exists, cannot be     │
  51+ branches        │  partners       provider                        replaced)             │
  200–400 field       │                                  Cloud                                │
  technicians         │  Client ITSM    Qualified        telephony      Google Maps           │
                      │  (ServiceNow,   e-signature      / CPaaS        Platform              │
                      │   Jira)         trust service                                         │
                      └───────────────────────────┬───────────────────────────────────────────┘
                                                  │
   ═══════════════════════════════════════════════▼═══════════════════════════════════════════
                          1000FiX ERP SYSTEM v2.0 — SYSTEM BOUNDARY
   ═════════════════════════════════════════════════════════════════════════════════════════════
     Inside: 67 modules · 12 experience surfaces (P01–P12) · 16 domain services (CD-233…248) ·
     10 applications (APP-01…10) · 24 standalone open-source systems · 6 environments ·
     2 data residencies · 47 integration endpoints, of which 12 are P0
```

### 5.2 External entity register — and the architectural obligation each creates

| # | External entity | Direction | Architectural obligation it creates |
|---|---|---|---|
| EX-01 | **Portal platform (Next.js + Payload CMS 3)** | Bidirectional | `CON-03` — cannot be replaced. The ERP must expose a **versioned, dual-version contract** and degrade gracefully when the portal is unavailable. This is why the interface view (§7.3) is a first-class view, not an appendix |
| EX-02 | **Payment rails** — bKash, Nagad, SSLCOMMERZ, Rocket | Bidirectional | Money movement must be **idempotent, reconcilable and fallback-capable** (QAS-09). Three rails means the failure of one must not stop collection |
| EX-03 | **Banks — BEFTN, statement import** | Batch | Payroll and vendor disbursement leave the system as **files**, not API calls. A batch boundary is an architectural boundary: it has a freeze point, a control total and a manual fallback |
| EX-04 | **NBR VAT Online** | Outbound, statutory | Mushak 6.3 issuance and 9.1 monthly return. The **generated return must be filable manually** if the integration fails — a statutory deadline cannot depend on an API |
| EX-05 | **National Data Management Authority** | Notification | Breach notification and cross-border transfer notification. Creates an obligation to be **able to enumerate what personal data exists and where** — which is why residency is a data-model property, not a hosting choice |
| EX-06 | **17+ brand partners** | Bidirectional | Each has a different claim format. Handled by **orchestration configuration (n8n), not code** — see ADR-025 |
| EX-07 | **500–2,000 marketplace sellers** | Inbound, untrusted | The largest **untrusted-actor surface** in the estate. Drives zone separation and the abuse-case work in `SC-002` |
| EX-08 | **Corporate client identity providers** | Federation | SAML/OIDC brokering per client (INT-046). Forces identity to be a **separate system (Keycloak)**, not an ERP feature |
| EX-09 | **Customer-managed IT estates** (remote support) | Outbound into customer premises | Remote desktop into third-party estates. A **reverse blast-radius** concern: our compromise becomes theirs |
| EX-10 | **Couriers, recycling partners, KYC providers, mapping, telephony** | Mixed | Each declares one of five integration patterns (§7.2) and, if P0, a tested manual fallback (NFR-050) |

### 5.3 What the boundary deliberately excludes

| Excluded | Why |
|---|---|
| Marketing content, pages, blog, SEO | Owned by the portal platform's CMS. The ERP owns **state and truth**; the portal owns **experience and reach** (`AR-002` §3) |
| Carrier interconnect for hotline 16743 | Licensed activity in Bangladesh. L6 CPaaS, never built |
| Qualified e-signature trust services | Legal enforceability requires accreditation. L6 for contracts; L5 for operational signatures (ADR-019) |
| Payment processing itself | Regulated. Integrate, never build (TD-17) |
| Identity data sources for KYC | Requires accredited data source. L6 |

---

## 6. Logical View (VP-2)

### 6.1 The layered structure

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ EXPERIENCE            12 surfaces · 10 applications                              │
│                       Next.js 15 ×6 · Flutter ×4 · Odoo Web OWL 2 · Odoo Portal  │
│                       · Metabase/Grafana embedded                                │
│                       NO STATE · NO BUSINESS RULES · PS-01…PS-12                 │
├──────────────────────────────────────────────────────────────────────────────────┤
│ EXPERIENCE API        Kong 3.x · 12 API families · OAuth2/OIDC via Keycloak 26.x │
│ GATEWAY               versioning · rate limits · idempotency enforcement ·        │
│                       correlation-id injection · BFF per portal                   │
├──────────────────────────────────────────────────────────────────────────────────┤
│ SYSTEM OF RECORD      67 modules in 11 categories                                 │
│                       ┌────────────────────────────────────────────────────────┐ │
│                       │ SHARED KERNEL — party · catalogue · location ·         │ │
│                       │ legal entity · document · event                         │ │
│                       │ Modelled once. Change requires Design Authority review. │ │
│                       └────────────────────────────────────────────────────────┘ │
│                       L1 Odoo 19 CE ~28% · L2 OCA ~24% · L3 free 3rd-party ~4%   │
│                       L4 standalone OSS ~17% · L5 custom ~25% · L6 commercial ~2%│
├──────────────────────────────────────────────────────────────────────────────────┤
│ DOMAIN SERVICES       16 stateless services outside the Odoo process             │
│ (L5, CD-233…248)      residency · notification · dispatch scoring · routing ·    │
│                       telemetry · document generation · pricing · OCR ·          │
│                       reconciliation · settlement · warehouse ETL · RMM ·        │
│                       ML gateway · STT · event replay · DSR orchestrator          │
├──────────────────────────────────────────────────────────────────────────────────┤
│ MESSAGING             Transactional outbox (in-transaction, AS-08)               │
│                       → Redis Streams (W1–W5) → Redpanda/Kafka (W6+)             │
│                       → idempotent consumers · DLQ · replay-from-timestamp        │
├──────────────────────────────────────────────────────────────────────────────────┤
│ DATA                  PostgreSQL 16 (regional) ‖ PostgreSQL 16 (BD-resident)     │
│                       TimescaleDB · ClickHouse (W8) · Redis 7 · MinIO · MLflow   │
└──────────────────────────────────────────────────────────────────────────────────┘
   CROSS-CUTTING: identity (Keycloak) · observability (OTel→Prom/Loki/Tempo→Grafana)
                  · secrets (Vault) · localisation · residency enforcement
```

### 6.2 The decomposition — 11 categories, 67 modules

> **`C-01` closed here.** The repository has described two decompositions simultaneously: five
> pillars (`02-01` §2) and eleven categories (`02-02` §2). **The eleven-category decomposition in
> `02-02` is the single logical decomposition of this system.** The five-pillar view is formally
> retired as an architecture artefact and survives only as history in `99_Reference/_Superseded/`.
> Any document that says "pillar" means "category" and should be corrected at next revision.

| Cat | Name | Modules | Count | Architectural character |
|:--:|---|---|---:|---|
| **A** | Service Delivery & Operations | M01, M31, M02, M03, M04, M05, M06 | 7 | **The core transactional aggregate cluster.** Owns the service order, the single most-referenced object in the system |
| **B** | Customer Engagement & Experience | M33, M07, M10, M34, M27, M32, M35 | 7 | Owns the **party master** (M33) — a kernel concept, therefore change-controlled |
| **C** | Commercial, Pricing & Revenue | M37, M11, M36, M08, M09, M39, M38, M12, M40 | 9 | Owns **catalogue** (M37, kernel) and the highest-consequence external surface (M12 marketplace) |
| **D** | Circular & Asset-Based Business | M13, M14, M18 | 3 | Asset-lifecycle specialisations; late waves; low coupling inward |
| **E** | Supply Chain & Inventory | M15, M41, M16, M42, M43, M44 | 6 | Owns stock truth. M15 is a W2 hard dependency for every repair path |
| **F** | Asset, Equipment & Facilities | M17, M45, M46, M47, M48 | 5 | Owns the **asset/device registry** — the second most-referenced object |
| **G** | Finance & Treasury | M19, M20, M52, M50, M51, M53, M49, M54 | 8 | **Terminal in the dependency graph.** Nothing may post to the ledger except through it (§6.5 rule LB-04) |
| **H** | People & Workforce | M21, M55, M56, M57, M22, M58, M59 | 7 | Statutorily dense; supplies the **dispatch-eligibility gate** consumed by M02 |
| **I** | Governance, Risk, Quality & Knowledge | M23, M60, M24, M61 | 4 | Owns `fix.document` (kernel) and the evidence chain |
| **J** | Data, Analytics & Intelligence | M62, M25, M26, M63 | 4 | **Read-only downstream** of everything. Never writes to a transactional aggregate except as an advisory record |
| **K** | Platform & Technology | M28, M29, M64, M65, M66, M30, M67 | 7 | **The foundation every other category depends on.** M28/M29/M30 are non-descopable |
| | | **Total** | **67** | 67 of 67 specifications exist on disk (counted 2026-08-18 02:05) |

### 6.3 The shared kernel

Six concepts are modelled once and consumed by all. **Changing a kernel concept is an architecture
change requiring Design Authority approval**, not a module change.

| Kernel concept | Odoo basis (L1) | OCA (L2) | Custom (L5) | Owning module | Consumed by |
|---|---|---|---|---|---|
| **Party** | `res.partner` | `OCA/partner-contact` | `fix.party.role`, `fix.party.hierarchy`, `fix.identity.document` (CD-145…148) | **M33** | All 67 |
| **Catalogue** | `product.template` / `product.product` | `OCA/product-attribute` | `fix.catalogue.item`, service kits, rental SKUs, refurb grades (CD-158…160) | **M37** | M01, M11, M12, M13, M14, M15, M38 |
| **Location & geography** | `res.country`, `res.country.state` | address tools | `fix.bd.address` — 8 divisions / 64 districts / ~495 upazilas / unions; `fix.zone`, `fix.geofence` | **M30 / M65** | M02, M03, M04, M12, M65 |
| **Legal entity & operating unit** | `res.company` | **`OCA/operating-unit`** | `fix.entity`, `fix.branch`, `fix.cost.center` | **M30** | All — this is the multi-branch isolation mechanism |
| **Document** | `ir.attachment` | `OCA/dms` | `fix.document`, retention class, signature envelope | **M24** | All; Mayan EDMS from W5 |
| **Event** | — | — | **`fix.domain.event` — transactional outbox** | **M28** | All (AS-08 makes it non-optional) |

> **The design rule that is easiest to violate and most expensive to recover.** A single party holds
> multiple roles simultaneously. A marketplace seller may also be a customer; a corporate client may
> also be a referral partner. **Seller, customer, vendor and partner are not separate master records
> joined by reference — they are one `res.partner` with multiple `fix.party.role` records.** Violating
> this reproduces exactly the duplicate-identity problem the programme exists to remove, and it is
> unrecoverable once transaction volume accrues against the duplicates. This is enforced as a fitness
> function in `AR-012` (`FF-08`).

### 6.4 Component structure — what a "module" actually is

At C4 Level 3, a module is not one thing. It is a consistent assembly of parts, and the assembly
rules are what make 67 of them tractable:

| Part | Realised as | Governed by |
|---|---|---|
| **Models** (aggregates, entities, value objects) | Odoo models prefixed `fix.`, tables `fix_` | `AR-007` §3; DM-01…DM-15 |
| **State machine** | Explicit `state` selection with the transition map declared in exactly one place | AS-06; `AR-003` §5 |
| **Business rules** | Enforced at the **model layer**, negative-tested through both UI and API | DoD-04; AS-09 |
| **Security artefacts** | Record rules, field permissions, SoD entries | DoD-07; `SC-004` |
| **Published interface** | REST endpoints in an API family + domain events through the outbox | AS-07, AS-08 |
| **Consumed interface** | Published APIs and events of other modules — **never their tables** | AS-01 |
| **Automations** | Declared with a **mandatory failure behaviour** | `_MODULE_TEMPLATE` §11 |
| **Instrumentation** | KPI metrics with allocated `KPI-nnn`, visible in M25 | AS-15, DoD-09 |

### 6.5 Logical boundary rules

These replace `02-01` §2's "pillar boundary rules", restated for the category decomposition and made
verifiable. Each names its enforcement mechanism; a rule with no mechanism is an aspiration and is
marked as such.

| # | Rule | Enforcement |
|---|---|---|
| **LB-01** | A module may read another module's data **only** through that module's published API, a published event projection, or the shared kernel. Never its tables | CI static analysis (`AR-012` `FF-01`); AS-01 |
| **LB-02** | Cross-module **writes** occur only via a domain event consumed by the owner, or an explicit orchestrated command exposed by the owner | Code review + contract test |
| **LB-03** | Each category owns its scheduled jobs. **No cross-category cron dependency** — a job in category A may not assume a job in category G has run | Job registry review at wave gate |
| **LB-04** | **Financial postings originate only in category G.** Other categories raise *billable events*; they never write journal entries | CI check on `account.move` write paths (`FF-05`) |
| **LB-05** | Identity and permission decisions are **always** delegated to M29. No module implements its own authentication or authorisation logic | CI check; PS-01, PS-12 |
| **LB-06** | Category J (analytics) is **read-only** with respect to transactional aggregates. An ML output is written as an advisory record (`fix.ml.prediction.log`), never as a state mutation | Model registry check (`FF-07`) |
| **LB-07** | Experience surfaces hold **no authoritative state and implement no business rule**. A portal may cache for performance, never for truth | Portal contract test PS-11 — an invalid payload posted directly to the API must be rejected |
| **LB-08** | The **residency-classified field set** is read and written only through the residency service (CD-233). Never by direct query, not even in a migration or a backfill | ORM guard + negative test + log scrubbing (`FF-09`) |
| **LB-09** | Where two modules contest a capability, the contest is adjudicated in **`AR-005`**, not settled locally in either specification | Register-first; RG-04 reciprocity check |

### 6.6 Business-line specialisation — how nine lines share one order object

Nine business lines run through shared modules. The architectural problem is that the service order
must be **polymorphic by line without becoming a god object**.

| Business line | Order object | Work object | Billing model | Categories engaged |
|---|---|---|---|---|
| Warranty repair | Service Order (type=warranty) | Work Order | Brand claim | A, C, E, G |
| Paid repair | Service Order (type=paid) | Work Order | Invoice on completion | A, C, E, G |
| AMC / RAMC | Contract | Scheduled Work Order | Recurring subscription | C, A, G |
| Managed services | MSP Contract | MSP Ticket / Patch Job | Per-seat or per-asset recurring | A, C, G, B |
| Data services | Data Case | Recovery / Backup Job | Fixed fee or subscription | A, G, I |
| Rental | Rental Agreement | Delivery / Collection / Service | Period + usage + damages | D, A, F, G |
| Trade-in & resale | Trade-In Offer / Sales Order | Refurb Work Order | Purchase then margin on resale | D, C, E, G |
| Marketplace | Marketplace Order | Seller Job | Commission + fees | C, G, I |
| Recycling | Collection Event | Recycling Batch | Fee or material-recovery credit | D, A, G |

**The chosen structure.** A thin `fix.service.order` core plus **one-to-one line-specific extension
models**, each owned by its business-line module: `fix.service.order.rental` (M13),
`fix.service.order.msp` (M05), `fix.service.order.data` (M06), `fix.service.order.marketplace` (M12).

| Option | Assessment |
|---|---|
| One wide table with nullable columns per line | **Rejected.** Nine lines × ~8 fields each makes the core table unreadable and every line's change a core change |
| Separate order table per line | **Rejected.** Breaks the "one queue, one SLA clock, one customer history" requirement that the whole intake design rests on |
| **Thin core + 1:1 extensions** | **Chosen.** The core carries what every line has (party, asset, state, SLA, branch, money); each extension carries only its own line's fields and is owned, versioned and deployed by that line's module. Adding a tenth line adds a module, not a core migration |

This is recorded as **ADR-002** in `AR-004`.

---

## 7. Interface and Runtime Views (VP-3, VP-4)

### 7.1 Interface view — the twelve API families

Twelve families, each with a base path, a declared consumer set and a scoping rule. **The family is
the unit of contract, versioning and rate limiting** — not the endpoint, and not the module.

| Family | Base path | Consumers | Auth and scope |
|---|---|---|---|
| Customer | `/api/v1/customer/*` | P01, P04, assistant | OAuth 2.0 user token, customer-scoped |
| Technician | `/api/v1/technician/*` | P02 | OAuth 2.0 + PKCE, technician-scoped |
| Operations | `/api/v1/ops/*` | P03, P10 | OAuth 2.0 staff token, role-scoped |
| Corporate | `/api/v1/corporate/*` | P04 | OAuth 2.0, corporate-account-scoped |
| Vendor | `/api/v1/vendor/*` | P05 | OAuth 2.0, vendor-scoped |
| Seller | `/api/v1/seller/*` | P07 | OAuth 2.0, seller-scoped |
| Brand | `/api/v1/brand/*` | P08 | OAuth 2.0, brand-scoped |
| Logistics | `/api/v1/logistics/*` | P09 | OAuth 2.0, rider/coordinator-scoped |
| Analytics | `/api/v1/analytics/*` | P06, embedded dashboards | OAuth 2.0 + row-level security context |
| Admin | `/api/v1/admin/*` | P03 system console | OAuth 2.0 + MFA + step-up |
| Partner | `/api/v1/partner/*` | P12, external partners | OAuth 2.0 client credentials |
| Webhook receiver | `/hooks/v1/*` | External systems | Signature verification |

**Architecturally significant interface rules** (the full set is API-01…API-12 in `05-03` §5.2; these
three are the ones that constrain *structure*, not style):

| Rule | Architectural consequence |
|---|---|
| **API-07** `Idempotency-Key` required on every state-changing operation, rejected at the gateway if absent | Makes every write path safely retryable, which is what allows the offline engine (§7.5) and every integration retry ladder to exist at all |
| **API-10** No endpoint returns data outside the caller's authorisation scope, **enforced server-side** | Forbids the common shortcut of scoping in the BFF. Scope is a record-rule property, so a new surface cannot widen it |
| **API-02** Minimum two concurrent versions, six months' deprecation notice | Makes `CON-03` survivable: the portal platform can upgrade on its own schedule |

### 7.2 Integration patterns — five, and every integration declares one

| Pattern | When used | Transport | Failure semantics |
|---|---|---|---|
| **Synchronous request/response** | Caller needs the answer now | REST/JSON over HTTPS | Timeout + circuit breaker; caller degrades visibly |
| **Asynchronous command** | Work can be queued | Message → worker | At-least-once; idempotent by command UUID |
| **Domain event (pub/sub)** | Others react to a state change | Transactional outbox → bus | At-least-once; idempotent consumption; DLQ after 3 retries |
| **Webhook (in/outbound)** | Third-party notification | Signed HTTPS POST, replay-protected | Retry ladder; endpoint disabled after 5 consecutive failures |
| **Batch file exchange** | Bulk, scheduled or regulator-mandated | SFTP / signed drop | Control totals; freeze point; manual fallback |

All 47 integrations carry a declared pattern; all 12 P0 integrations carry a **tested manual
fallback** (NFR-050, IP-09). A P0 integration whose fallback has not been exercised is a wave-gate
failure, not a risk.

### 7.3 The messaging architecture — and the convention conflict it must resolve

The **transactional outbox is non-negotiable (AS-08)**, and the reason is worth stating because it is
the decision most likely to be quietly skipped under delivery pressure:

- Publishing an event *after* commit means a crash between the two **loses the event silently**.
- Publishing *before* commit means an event can describe **a state that never existed**.
- The outbox writes the event **into the same database transaction** as the state change; a separate
  relay publishes from the outbox table.

This is the only pattern that makes *"every state change produces exactly one event"* **true** rather
than **usually true**, and across 67 modules the difference between "usually" and "always" is a
permanent, silently accumulating source of data divergence (risk `TR-12`).

> **A naming conflict this document must adjudicate, because `AR-009` cannot proceed without it.**
> The estate uses **two incompatible event-naming conventions**:
>
> | Convention | Form | Where used | Example |
> |---|---|---|---|
> | **A — aggregate-scoped** | `<aggregate>.<past_tense_verb>` | `05-03` §4.1 and its 64-row inventory; `02-01` §7 | `service_order.completed` |
> | **B — module-scoped** | `<module_code_lower>.<noun>_<past_tense_verb>` | The §12.3 tables of the later module specifications | `ap.invoice_received`, `ar.credit_note_issued` |
>
> **Ruling — ASR-11.** Convention **A is normative**: `<aggregate>.<past-tense-verb>`, where the
> aggregate is the **domain aggregate root**, not the owning module's code. An event is a fact about
> a *thing*, and the thing outlives the module boundary that currently owns it. Convention B couples
> the event name to the org chart of the module register: if M52 is later split, every consumer of
> `ap.*` breaks for a reason that has nothing to do with the domain.
>
> **Migration is `AR-009`'s to execute**, before any consumer is built. It is cheap now (no code
> exists) and unrecoverable later (events are contracts, and `05-03` §4.3 forbids breaking changes
> within a `schema_version`).

**Event envelope** — every event, without exception:

```json
{
  "event_id": "uuid",
  "event_type": "service_order.completed",
  "schema_version": "1.2",
  "occurred_at": "2026-08-18T09:14:22Z",
  "company_id": 1,
  "operating_unit_id": 17,
  "actor": { "type": "user", "id": 442 },
  "correlation_id": "uuid",
  "causation_id": "uuid",
  "aggregate": { "type": "service_order", "id": 918234 },
  "payload": { }
}
```

**Delivery semantics fixed here, designed in `AR-009`:**

| Property | Position |
|---|---|
| Delivery | **At-least-once.** Exactly-once is not offered; idempotent consumption is mandatory instead |
| Ordering | **Per aggregate id only, never globally.** Partition key = aggregate id |
| Failure | Three retries, exponential backoff, then dead-letter with alert |
| Replay | Any consumer replayable from a point in time with **no side effect on other consumers** (CD-247) |
| Schema evolution | Additive only within a `schema_version`; breaking change requires a new version and a dual-publish period |
| Latency | 95% of events consumed within 5 s of publication (NFR-043) |

### 7.4 The measured event surface — the finding that sizes `AR-009`

Extraction performed **2026-08-18 02:05 (+06)** across all 67 module specification files, taking the
first column of each `### 12.3 Domain Events Published` table:

| Measure | Count | Method |
|---|---:|---|
| Distinct events **declared published** in module §12.3 tables | **988** | `awk` range extraction, §12.3 → §12.4, first table column |
| Events **registered** in `05-03` §4.2 | **64** | Table row count |
| Declared but **not registered** | **953** | Set difference |
| Registered but **published by no module §12.3** | **29** | Set difference (mostly convention-A names whose producers now use convention B) |
| Consumed in a §12.1 table with **no producer anywhere** | **4** | Set difference |

**What this changes.** Audit `AP-01` compared three files and found 21 unregistered event names,
correctly classing 14 as genuinely missing. That finding is sound but its *scale* was set by its
sample. `05-03` §4.2 is headed *"Event Inventory (Principal Events)"* — "principal" is carrying
**93.5% of the event surface**. The consequences are architectural, not clerical:

1. **`IN-003` (schema registry) is a much larger deliverable than the register assumes.** 988 events
   at even a small schema each is a substantial artefact, and it is a Wave 1 blocker for every
   consumer.
2. **A hand-maintained catalogue will not survive.** `AR-009` must specify the catalogue as
   **generated from the outbox registry**, with `05-03` §4.2 demoted to a curated cross-cutting
   subset. A living catalogue is `M28` `FR-IPF-032`; this measurement is the evidence that it is
   mandatory rather than desirable.
3. **The naming ruling in §7.3 must be executed before, not after, registration** — otherwise 953
   registrations are made under a convention that then changes.

Recorded as finding **`PGD-A3-04`** in `_AUDIT/PGD-AUDIT-002`.

### 7.5 Runtime view — six architecturally significant scenarios

The scenarios below are chosen because each exercises a part of the architecture where the most
components interact and where a defect would be most expensive.

#### RS-01 — Service request to cash *(M01 → M02 → M15 → M20 → M19)*

```
Customer   P01 Portal    Kong      Odoo/M01     Outbox    Dispatch svc   P02 App    M20/M19
   │            │          │           │           │           │            │          │
   │─book──────►│          │           │           │           │            │          │
   │            │─POST /api/v1/service-orders  [Idempotency-Key]            │          │
   │            │          │──────────►│           │           │            │          │
   │            │          │           │─entitlement check (M08)            │          │
   │            │          │           │─SLA policy assignment (M01)        │          │
   │            │          │           │─WRITE state + outbox row IN ONE TRANSACTION   │
   │            │◄─201 + tracking token─│           │           │            │          │
   │            │          │           │           │─service_order.created─►│          │
   │            │          │           │           │           │─score: skill·cert·   │
   │            │          │           │           │           │  van stock·zone·SLA  │
   │            │          │           │◄─assignment────────────┤            │          │
   │            │          │           │           │─work_order.assigned───►│─push────►│
   │            │          │           │           │           │            │          │
   │            │          │           │       [technician works OFFLINE up to 24 h]    │
   │            │          │           │◄─sync: append-only journal, per-command UUID──┤
   │            │          │           │─parts consumed (M15) · time · evidence        │
   │            │          │           │─work_order.completed──►│            │          │
   │            │          │           │─QC pass (M23) → invoice (M20) ≤ 5 s (NFR-040)─►│
   │─pay bKash─►│─POST /api/v1/payments/confirm──►│           │            │          │
   │            │          │           │─post to GL (M19) + Mushak 6.3 register (M51)  │
   │            │          │           │   ── ATOMIC: both, or neither ──               │
   │            │          │           │─invoice.paid──────────►│            │─receipt─►│
```

**The three fragile points, and the tactic that holds each:**

| Point | Failure if unprotected | Tactic |
|---|---|---|
| Order creation retried | Two orders for one booking | `Idempotency-Key` required at gateway (API-07); duplicate key returns the original result |
| Offline sync reconciliation | Queued actions applied twice, or lost | Client-generated command UUID + **server-side idempotency ledger** (DI-04) |
| Invoice → GL → Mushak register | VAT return will not reconcile to the ledger | Single transaction across posting and register write; reconciliation service (CD-241) detects divergence nightly (DI-07) |

#### RS-02 — GPS to live customer ETA *(P02 → Traccar → TimescaleDB → M02 → P01)*

400 technicians × one position / 30 s = **800 positions/minute sustained** (NFR-056) ≈ 1.15 M/day
≈ 420 M/year.

**The architectural consequence, stated because it is the clearest example of a sizing driver forcing
a structure:** at that volume, GPS in the primary OLTP database would dominate the write-ahead log
and degrade every other write in the system. Time-series data therefore lives in **TimescaleDB**, and
`fix.location.ping` is a hypertable, not a table. TimescaleDB rather than InfluxDB because it is the
same engine and the same operational skill set (ADR-013).

The customer-facing path is **event with polling fallback** — `technician.location_updated`
(throttled) to the portal webhook, and `GET /api/v1/technicians/{id}/location` if the webhook path
fails. A live map that silently stops updating is worse than one that visibly polls.

#### RS-03 — Warranty claim to reimbursement *(M09 → n8n → P08 → M20/M19)*

17+ brand partners, each with a different submission format and portal. The claim record, the
evidence pack and the reconciliation stay in Odoo where the ledger is; **only the per-brand
transformation is externalised to n8n** (ADR-025), because a brand changing its template must be a
configuration change, not a release.

**The control that this scenario exists to protect:** `claim.evidence_incomplete` **suppresses
submission** when the evidence pack is incomplete against the brand's rules. `P08` `T-05` depends on
it and the W4 gate's 90%-first-submission-approval target rests on it. It is one of the 14 events
audit `AP-01` found genuinely missing. **An architectural control that is documented and unpublished
is not a control.**

#### RS-04 — PDPA data-subject erasure *(M33 → residency service → both stores)*

**The hard part is not the export; it is the erasure.** An erasure must remove personal data from
the regional primary, the resident store, **every read replica, the warehouse, the object store, the
search index and the backups in scope**, while *preserving* the processing record that NFR-095
requires be kept five years.

That is a **saga with compensating actions, not a `DELETE`** — CD-248, and it is P0 because PDPA
enforcement activates around **13 May 2027, inside Wave 4** (verified 2026-08-18).

#### RS-05 — Degraded mode: a P0 integration fails

Every P0 integration has a fallback (`05-03` §7). Architecturally the requirement is that the
fallback is reachable **without a deployment**: it is a feature-flag state (CD-135, OPS-06), and the
switch is operable by the on-call engineer named in `SV-004`. A fallback that requires a release is
not available during the incident that needs it.

#### RS-06 — Wave gate: adding a module to a live system

Nine waves means the architecture is **deployed 9 times into a running business**, not once.

| Requirement | Architectural consequence |
|---|---|
| Zero-downtime deployment (NFR-008) | **Forward-only, backward-compatible migrations** (OPS-07): a release adds a column before code uses it and removes a column only after no code references it — **two releases, never one** |
| A new module consumes existing events | Consumers are added without touching producers. This is the payoff of the outbox/event structure and the reason it is worth its cost in W1 |
| A new module needs a not-yet-built dependency | **Build the seam, stub the answer** (ADR-023 — M02's certification check is a stub returning "eligible" in W2, connected in W5). Retrofitting a blocking check into a live assignment path is materially riskier |

---

## 8. Deployment and Security Views (VP-6)

### 8.1 Trust zones

Six zones. The zone model is the **input to `SC-002`** (threat model) and to `PE-001` (network
design); neither can start without it, which is why it is here and not there.

| Zone | Contents | Ingress from | Egress to | Controls |
|---|---|---|---|---|
| **Z0 Public edge** | CDN, WAF (OWASP CRS), DDoS, bot management | Internet | Z1 only | Rate limiting, bot management, geo rules |
| **Z1 Ingress** | Kong 3.x, Nginx 1.27 | Z0 | Z2, Z3 | TLS 1.3 termination, OAuth2 introspection, per-consumer quotas, correlation-id injection |
| **Z2 Application** | Odoo nodes, Next.js nodes, 16 domain services | Z1 | Z3, Z4, Z6 | Service identity, mTLS between services, **no direct internet egress** |
| **Z3 Data — regional** | PostgreSQL primary + 2 replicas, TimescaleDB, ClickHouse, Redis, MinIO | Z2 only | none | Private network only, no public endpoint, encryption at rest |
| **Z4 Data — Bangladesh resident** | Sensitive-data PostgreSQL store, separate key material | **Z2 via the residency service (CD-233) only** | none | Per-read access logging, step-up authentication for human access |
| **Z5 Management** | CI/CD runners, bastion, Vault, observability | Restricted source ranges + MFA | Z2, Z3 | Privileged session recording (NFR-070); **no standing access** |
| **Z6 Egress** | Outbound proxy to third-party APIs | Z2 | **Named allow-list only** | Credential injection from Vault; every outbound call logged (IP-10) |

**Two rules follow, and they are the reason the zone model is worth its operational cost:**

1. **No application node reaches the internet except through Z6, to an allow-listed destination.**
   This is what converts IP-10 (*"data leaving the Company is minimised and logged"*) from an
   aspiration into a mechanism.
2. **Z4 is reachable only through the residency service.** The residency rule is implemented in
   exactly one place and can therefore be **audited in exactly one place** — which is what a
   regulator will ask for.

### 8.2 Data isolation tiers

Orthogonal to the zones: zones separate *networks*, tiers separate *records*.

| Tier | Visibility | Mechanism | Examples |
|---|---|---|---|
| **T0 Global** | All authenticated internal users | No record rule | Service and parts catalogue, brand/model master, checklist templates, branch directory |
| **T1 Company** | Within the legal entity | `company_id` rule | Chart of accounts, tax configuration, payroll structures |
| **T2 Operating unit** | Within the branch | `operating_unit_id` rule via `OCA/operating-unit` | Branch service orders, branch stock, branch cash |
| **T3 Team / zone** | Within the assigned zone or team | `zone_id` / membership rule | Dispatch zone queues, van stock, team scorecards |
| **T4 Owner** | Record owner + management line | Owner + hierarchy rule | Own jobs, own leave, own expenses, own performance |
| **T5 Restricted** | Explicit grant only, **access logged, step-up authenticated** | Named allow-list + audit + step-up (NFR-065) | Individual payroll, NID, bank details, recovered customer data, call recordings, audit logs, biometric templates, seller KYC |

**T5 and Z4 coincide almost exactly, and that is deliberate.** Nearly every T5 class is also
residency-classified under NFR-086. The architectural consequence: **a T5 read is a call to the
residency service, never a direct database read.** One enforcement point, one audit point.

### 8.3 Split-residency topology

```
   REGIONAL PRIMARY                          BANGLADESH-RESIDENT STORE (Z4)
   PostgreSQL 16 + 2 replicas                PostgreSQL 16, separate key material
   TimescaleDB · ClickHouse (W8)             NID · passport · TIN ·
   Redis 7 · MinIO                           biometric templates ·
                                             recovered customer data ·
   Everything about a customer               seller KYC · criminal records
   EXCEPT the classified fields
                    └────── joined by resident key only ──────┘
                    ▲
              residency service (CD-233) — the ONLY path
```

**The boundary is a data-model boundary, not a network boundary.** A record about a customer exists
in the regional primary; the customer's NID exists only in Z4; the two are joined by a resident key.
The sensitive field is **never duplicated into the regional store — not transiently, not in a cache,
not in a log**. This is enforced by field-level residency classification checked at write time
(NFR-086a), not by developer discipline.

| Constraint | Statement |
|---|---|
| **NFR-086** | Sensitive Personally Identifiable Data per PDPA 2026 is stored in a Bangladesh-resident store |
| **NFR-086a** | Every field carries a residency classification; the platform enforces it **at write time** |
| **NFR-086b** | Cross-border transfer of a classified field requires an Authority notification record and a documented safeguard **before** the transfer executes |
| **NFR-086c** | **Absolute** — non-production environments never contain unmasked classified data in any region. Masking runs **inside** the clone job, so an unmasked clone cannot exist even briefly |

> **The dependency this rests on.** A **legal opinion on the split-residency design is required
> before the Wave 1 architecture is fixed** — dependency `DEP-31`, decision `D-13`. §13 Q-01.
> **The architectural response to that uncertainty is to build the mechanism regardless**: the
> residency service and field-level classification are built in Wave 1 whatever the opinion says,
> because classification is *data*, so a change of opinion is a **reclassification, not a redesign**
> (risk `TR-02`). This is the single most important risk-absorbing decision in the deployment view.

### 8.4 Disaster recovery — and the finding it must close

Audit **`OP-01` (critical)** records that *there is no lawful DR path for Bangladesh-resident
personal data*, and **`OP-02`** that the `dr` environment is *"named in the architecture and sized
nowhere"*.

**Position taken here, as a deployment-view constraint rather than an operations decision:**

| # | Constraint |
|---|---|
| DR-01 | The regional tier fails over to a warm standby meeting RPO ≤ 15 min, RTO ≤ 2 h (NFR-007) |
| DR-02 | **Z4 fails over to a Bangladesh-resident standby.** A regional DR target for Z4 data is not available as an option — NFR-086b makes it a notifiable regulatory act, not a recovery step |
| DR-03 | The DR drill (NFR-051, twice yearly) **exercises both tiers and the residency service**, and exercises the ML fallbacks (`TR-17`) |
| DR-04 | `dr` is sized from QAS-06, not from spare capacity. Sizing is `PE-002`'s to publish; the **basis** is fixed here |

### 8.5 Environment ladder

| Environment | Purpose | Data | Refresh | Residency-classified data |
|---|---|---|---|---|
| `local` | Developer workstation, Docker Compose | Synthetic fixtures | On demand | **Never** |
| `dev` | CI target | Synthetic + anonymised sample | Every merge to `develop` | **Never** |
| `staging` | UAT, performance, security testing | Production clone, PII-masked | Weekly | **Never — masked in-job** (NFR-071, NFR-086c) |
| `training` | Super-user and end-user training | Curated scenario data | Per training cycle | **Never** |
| `prod` | Live | Live | — | Yes, **in Z4 only** |
| `dr` | Warm standby | Streaming replica | Continuous | Yes, in a **Bangladesh-resident** standby |

### 8.6 Sizing basis — steady state (Wave 8)

Sizing is `PE-006`'s deliverable. The **architecturally significant** part is which component's size
is driven by which requirement, because that is what tells a platform engineer what to scale when:

| Component | Sizing driver | Requirement |
|---|---|---|
| PostgreSQL primary | 5 M service orders/year; 5 M assets | NFR-053, NFR-054 |
| Read replicas ×2 | Analytical read isolation before ClickHouse arrives in W8 | `TR-14` |
| **Bangladesh-resident store** | **Regulatory, not volume** — small, but availability-critical | NFR-086 |
| TimescaleDB | 800 GPS/min + 50,000 telemetry points/min | NFR-055, NFR-056 |
| ClickHouse (W8) | Analytical query ≤ 10 s p95 | NFR-039 |
| Redis | 800+ concurrent internal users | NFR-003 |
| Object storage | 50 TB, sub-10-second retrieval | NFR-060 |
| Odoo app nodes | 800 internal + 75,000 portal concurrent | NFR-003, NFR-004 |

> **Finding for `PE-006`.** The sizing table in `02-05` §8.1 predates the split-residency decision and
> **carries no line for the Bangladesh-resident store** — raised as change `25.3.6` in the Technology
> Stack Specification and still open. Recorded here as `PGD-A3-05`.

---

## 9. Cross-Cutting Concepts and the Operational View (VP-7)

### 9.1 Identity and access

| Concern | Realisation |
|---|---|
| Identity provider, SSO, MFA, step-up, federation | Keycloak 26.x (L4) |
| Odoo authentication bridge | `OCA/web` OIDC modules (L2) |
| Record-level access | Odoo `ir.rule` + `OCA/operating-unit` |
| Field-level permission | CD-130 `cd_rbac_ext` |
| Segregation of duties | CD-132 `cd_sod` — **evaluated at role-assignment time, not transaction time**, so a conflicting assignment is refused rather than a conflicting transaction being blocked afterwards |
| Immutable audit | `OCA/server-tools` `auditlog` + CD-131 |
| Secrets | Vault — never in code, configuration or logs |

**Access lifecycle** — the mover case is the one that silently accumulates privilege:

| Event | Trigger | Target |
|---|---|---|
| Joiner | `employee.joined` (M21) | Access active day one |
| **Mover** | Role change in M21 | **Old role revoked and new granted in one transaction — never additive** |
| Leaver | `employee.left` (M21) | Keycloak deprovisioning ≤ 1 hour; **zero orphaned accounts beyond 24 h** |
| Recertification | Quarterly | Every privileged role re-attested by its owner |

> **A live architectural defect this document must not paper over.** `05-04` registers **R01–R38**;
> **R39–R46 are in use and unregistered**; **R60 is a duplicate identity for R32 Quality Manager**;
> R54 and R57 are referenced with no definition. **An access rule written against R32 does not apply
> to a user granted R60.** Keycloak realm roles and Odoo groups must be built on **46 roles with R60
> eliminated and R54/R57 resolved, as Wave 0/Wave 1 scope** — building on 38 and adding eight later
> means retrofitting record rules and field permissions across live data (`TR-13`). Registered as
> `PGD-A3-06`; owned by `SC-004`.

### 9.2 Observability

```
Odoo · Next.js · Flutter · 16 domain services
   │  OpenTelemetry SDK — traces, metrics, logs, ONE correlation id
   ▼
OpenTelemetry Collector ──► Prometheus (metrics, alert rules)
                        ──► Loki       (structured logs, personal data scrubbed)
                        ──► Tempo      (distributed traces)
                              └──► Grafana ──► dashboards · alerting · on-call routing via Novu
```

**One correlation id spans the whole journey** — injected by Kong, propagated through Odoo, the
domain services, the event bus and back into the portal response. A support engineer takes a
correlation id from a user's error message and sees the entire request path. This is NFR-092-M, and
it is the difference between a 20-minute diagnosis and a 2-day one across a 5-stack estate.

**Alert discipline is architectural, not operational.** OPS-03: *every alert has a runbook entry;
alerts without an action are removed.* OPS-05: *every scheduled job reports success, failure and
duration — a job that fails silently is a defect.* At 67 modules with hundreds of scheduled jobs,
silent failure is the default outcome unless it is designed against.

### 9.3 Localisation as a structural concern

Bengali is not a font setting. Four structural consequences:

| Concern | Structural consequence |
|---|---|
| Text expansion | Bengali strings run 15–30% longer than English. **A layout constraint, not a copy constraint** — `UX-007`'s to design; the architecture's obligation is that no component assumes fixed-width labels |
| Rendering | OpenType shaping in the document generation service (CD-238). **Bengali print verified on every supported printer as a wave-gate item** — a Mushak 6.3 that renders wrongly is a compliance defect, not a cosmetic one (`TR-07`) |
| Collation | ICU `bn-BD` for sorting and comparison; UTF-8 throughout |
| Numerals and dates | Lakh/crore grouping in the Bengali locale; DD/MM/YYYY; **stored UTC, presented Asia/Dhaka** (AS-11) |

### 9.4 Failure and degradation model

| Level | Behaviour |
|---|---|
| **A domain service fails** | The calling path degrades to a **defined fallback**; no service failure blocks a P0 business path (L5-09, IP-05). Every ML model has a deterministic fallback (`ML-01`, `TR-17`) |
| **A P0 integration fails** | Feature-flag switch to the tested manual fallback (NFR-050); user-visible message stating what happened and what to do next (NFR-078) |
| **The event bus is degraded** | Outbox rows accumulate; state is still correct because it was committed in the same transaction. **This is why the outbox is the resilience mechanism, not just the correctness mechanism** |
| **Connectivity fails at the edge** | Field applications continue for 24 hours; portals degrade to cached read with writes queued or blocked-with-a-message, never silently dropped |
| **A region fails** | DR-01/DR-02 |

---

## 10. Quality-Attribute Scenarios

**This section is the largest single thing this document adds.** `05-06` states 101 NFR identifiers
carrying 104 requirements. What it does not state is, for any of them, **the architectural tactic
that satisfies it** and **the structure that would have to change if the target moved**. A
quality-attribute scenario in six-part form makes an NFR into an architectural test.

### 10.1 ISO/IEC 25010 crosswalk

| 25010 characteristic | `05-06` NFR range | Scenario |
|---|---|---|
| Performance efficiency | NFR-001…005, 031…044 | QAS-01, QAS-02 |
| Reliability (availability, fault tolerance, recoverability) | NFR-006…008, 045…052 | QAS-05, QAS-06 |
| Scalability *(25010:2023 addition)* | NFR-009, 010, 053…060 | QAS-03 |
| Security | NFR-011…015, 061…072 | QAS-07, QAS-08 |
| Interaction capability (usability, accessibility) | NFR-016…020, 073…082 | QAS-10 |
| Compliance / legal | NFR-021…025, 083…101 | QAS-04 |
| Maintainability | NFR-026…028, 090-M…092-M | QAS-11 |
| Data integrity | NFR-029, 030, DI-01…DI-08 | QAS-09 |

> **`AP-02` handling.** `NFR-090`, `NFR-091` and `NFR-092` each carry **two different requirements** —
> a PDPA obligation in `05-06` §6.3 and a maintainability requirement in §7. This document uses the
> **`-M` suffix** for the §7 sense (`NFR-090-M` = unit test coverage ≥ 80%) throughout. That is a
> *disambiguation convention, not a fix*: the collision must be resolved in `05-06`, which owns the
> identifier space. Until it is, *"satisfy NFR-092"* is ambiguous between distributed tracing and a
> statutory transparency notice.

### 10.2 The scenarios

Six-part form: **source · stimulus · artefact · environment · response · response measure**.

---

**QAS-01 — Interactive latency under normal load**

| Part | Value |
|---|---|
| Source | A branch service agent |
| Stimulus | Opens the Customer 360 view during the morning intake peak |
| Artefact | Odoo application tier + PostgreSQL primary |
| Environment | Normal operation, 800 concurrent internal users, W5+ data volume |
| Response | The view renders complete |
| **Measure** | **≤ 2 s at p95** (NFR-001, NFR-031); API component ≤ 400 ms p95 (NFR-002) |

**Tactics:** read replicas from W3 so analytical load never touches the primary (`TR-14`); the index
set in `05-02` §11 — `fix_service_order (partner_id, create_date DESC)` is the Customer 360 index;
PgBouncer connection pooling; cursor pagination (API-05) so a large history cannot be requested whole.

**What would have to change if the target moved to ≤ 1 s:** materialised customer-summary projection
maintained by event consumption. Not built now — it adds a consistency problem for a target already
met.

---

**QAS-02 — Dispatch board refresh at scale**

| Part | Value |
|---|---|
| Source | Dispatch manager |
| Stimulus | Refreshes the dispatch board with 500 open jobs and 400 technicians on the live map |
| Artefact | Odoo M02 + TimescaleDB + Traccar |
| Environment | Peak morning dispatch, all Dhaka centres |
| Response | Board and map render current state |
| **Measure** | **≤ 1 s for 500 open jobs** (NFR-033); live map update **≤ 5 s from GPS emission** (NFR-034) |

**Tactics:** GPS separated into TimescaleDB (RS-02) so board queries never scan position history;
`fix_sla_clock (breach_at) WHERE NOT breached` partial index for escalation scanning; throttled
`technician.location_updated` rather than per-ping propagation.

---

**QAS-03 — Growth headroom without re-architecture**

| Part | Value |
|---|---|
| Source | Business growth |
| Stimulus | 5× users and 10× data over five years; 200 branches; 10 legal entities in 5 countries |
| Artefact | The whole system |
| Environment | Steady-state production |
| Response | Capacity added without structural change |
| **Measure** | **No re-architecture required** (NFR-009, NFR-058, NFR-059); a test entity in a second country stood up **in under 12 weeks using only configuration** (W9 gate) |

**Tactics — and this is the one that must be paid for on day one:** **every transactional record
carries the full dimensional context from Wave 1** — `company_id`, `operating_unit_id`, `zone_id`,
`cost_center_id`, `business_line_id`, `currency_id`, `lang` (DM-03, AS-03) — even while a single
Bangladesh entity operates. This is what makes Wave 9 expansion a configuration exercise rather than
a rebuild. Retrofitting a dimension onto live transactional data across 1,335 entities is the kind of
change that does not get funded.

---

**QAS-04 — PDPA erasure request**

| Part | Value |
|---|---|
| Source | A data subject |
| Stimulus | Exercises the right to erasure under PDPA 2026 |
| Artefact | M33 + residency service + regional primary + Z4 + replicas + warehouse + object store + search index + in-scope backups |
| Environment | Production, after enforcement activation (~13 May 2027, inside Wave 4) |
| Response | Personal data erased across **all** stores; **the statutory processing record is preserved**; controller-side consumers notified |
| **Measure** | Completed within the statutory window; **notification to consumers within 30 days** (NFR-093); processing record retained **5 years** (NFR-095) |

**Tactics:** CD-248 saga with compensating actions; single residency service so Z4 has one write
path; log scrubbing (OPS-04) so a log line is not an uncontrolled copy; classification at field
level (NFR-086a) so the set of things to erase is **computable rather than remembered**.

**The failure mode this is designed against:** an erasure that succeeds in the primary and silently
misses the warehouse. Penalty exposure is up to **BDT 25 lakh**, or **BDT 50 lakh** for a significant
data fiduciary (verified 2026-08-18).

---

**QAS-05 — 24-hour offline field operation**

| Part | Value |
|---|---|
| Source | A field technician |
| Stimulus | Loses connectivity for 24 hours while completing jobs, consuming parts and capturing evidence |
| Artefact | APP-01 (Flutter) + offline engine + sync endpoint + idempotency ledger |
| Environment | Rural Bangladesh, mid-range Android 11 device, 3 GB RAM, intermittent 3G |
| Response | Full operation offline; on reconnection all work is applied **exactly once**; conflicts are resolved by declared authority and **shown to the user** |
| **Measure** | **24 h offline** (NFR-047); **sync ≤ 30 s on 3G** (NFR-037); **zero data loss and zero double-application** (DI-04); battery ≤ 12%/8 h shift (NFR-082) |

**Tactics:** encrypted local store; **append-only action journal** with client-generated command UUID
(AS-13); server-side idempotency ledger; per-batch checksums with whole-batch retry (never partial
application); **one shared offline engine** across APP-01/02/03 (ADR-024 — three implementations
produce three sets of conflict-resolution bugs); evidence uploaded on a deferred low-priority channel
so photo upload never delays state sync.

**This is the highest-risk requirement in the programme (`TR-01`), and its failure mode is social,
not technical:** technicians who stop trusting the app revert to paper, and the field data model
becomes permanently incomplete. Designed in full in **`AR-010`**.

---

**QAS-06 — Region loss and recovery**

| Part | Value |
|---|---|
| Source | Infrastructure failure |
| Stimulus | Primary region becomes unavailable |
| Artefact | Regional tier + Z4 resident tier + residency service |
| Environment | Production, business hours |
| Response | Failover to warm standby; **Z4 fails over to a Bangladesh-resident standby**; residency enforcement continues |
| **Measure** | **RPO ≤ 15 min, RTO ≤ 2 h** (NFR-007); drill twice yearly with documented results (NFR-051); weekly automated restore verification (NFR-052) |

**Tactics:** streaming replication; hourly WAL + daily/weekly/monthly backup ladder, AES-256; DR-02's
resident standby. **The architecturally significant point is DR-02**: a regional DR target for Z4
data is not a cheaper option, it is a notifiable regulatory act under NFR-086b. Closes `OP-01`.

---

**QAS-07 — Compromise of an untrusted external actor**

| Part | Value |
|---|---|
| Source | A marketplace seller account (one of 500–2,000 untrusted external actors) |
| Stimulus | Account is compromised and attempts lateral movement and data exfiltration |
| Artefact | Z0–Z2, seller API family, record rules, Z6 egress |
| Environment | Production |
| Response | Blast radius contained to that seller's own scope; attempt detected |
| **Measure** | **No endpoint returns data outside the caller's scope, ever** (API-10); T4/T5 record rules hold; anomalous export alerts (§9.2); no reachable path to Z3 or Z4 |

**Tactics:** scope enforced **server-side as a record rule**, never in the BFF; per-consumer rate
limits; Z2 has no direct internet egress; T5 reads go through the residency service with per-read
logging and step-up.

**Threat enumeration against these boundaries is `SC-002`'s** — and it cannot begin until this zone
model exists, which is the dependency this document discharges.

---

**QAS-08 — Privileged insider action**

| Part | Value |
|---|---|
| Source | An internal user holding a privileged role |
| Stimulus | Attempts an action that violates segregation of duties |
| Artefact | CD-132 `cd_sod` + Keycloak + Odoo groups |
| Environment | Production |
| Response | **The role assignment is refused at assignment time**, not the transaction at execution time |
| **Measure** | All **30** SoD controls enforced (SOD-01…SOD-30); override requires named approval and is logged; privileged sessions recorded (NFR-070) |

**Open defect:** only SOD-01…SOD-12 are registered in `05-04`; **SOD-13…SOD-30 are in use and
unregistered**. Building 12 leaves **18 segregation-of-duties conflicts unenforced**. Wave 0 blocking
(`PGD-A3-06`, `TR-13`).

---

**QAS-09 — Payment received twice**

| Part | Value |
|---|---|
| Source | A payment gateway |
| Stimulus | Sends a duplicate webhook callback for one payment |
| Artefact | Webhook receiver + M20 + M19 ledger |
| Environment | Production |
| Response | The payment is applied **exactly once**; the ledger reconciles |
| **Measure** | Zero double-application (DI-05); every posting reconcilable to its source (DI-02); nightly cross-system reconciliation with divergence alerting (DI-07) |

**Tactics:** signature verification and replay protection at `/hooks/v1/*`; idempotency by gateway
transaction id; reconciliation service (CD-241); **decimal arithmetic with explicit currency, never
float, in every money path** (AS-10, DI-01).

**Money movement across three rails with marketplace split settlement is the highest-consequence
integration in the programme**, and it is `IN-007`'s to design in full.

---

**QAS-10 — First load on a rural 3G connection**

| Part | Value |
|---|---|
| Source | A customer in a district town |
| Stimulus | Opens the booking path on a mid-range phone over 3G |
| Artefact | P01 (Next.js PWA) + Kong + M01/M02 |
| Environment | 3G, first visit, cold cache |
| Response | The booking path is usable |
| **Measure** | **First load < 400 KB** on critical customer paths (NFR-081, PS-07); booking availability ≤ 800 ms p95 (NFR-032); WCAG 2.2 AA (`UX-005`) |

**Tactic worth naming because it is enforced rather than intended:** the **bundle budget is a CI gate**
that blocks merge (`AR-012` `FF-11`). A performance budget that is not a build failure is a
suggestion.

---

**QAS-11 — Odoo major-version upgrade mid-programme**

| Part | Value |
|---|---|
| Source | Odoo release cadence |
| Stimulus | Odoo 20 lands (expected Sept–Oct 2026); the programme runs 36 months on 19.0 (released 18 Sept 2025, supported to ~Sept 2028) |
| Artefact | 232 custom Odoo modules, 140+ OCA modules across 18 repositories |
| Environment | Between Wave 5 and Wave 6, in the baselined plan |
| Response | The upgrade is executed as planned work, not as a rewrite |
| **Measure** | **Zero forked OCA modules** without Design Authority approval; extension-only custom modules; upgrade slot completed inside its wave allocation |

**Tactics — and this is the single most important upgrade-safety rule in the programme:**
**AS-05 — OCA modules are extended via `_inherit`, never forked.** One `_inherit` done wrong makes
the Odoo 20 upgrade a rewrite across 140+ modules for 34 months (`TR-04`). Enforced by CI
(`AR-012` `FF-03`), a named-approval fork register reviewed at every wave gate, and made mechanically
checkable by **`AR-007`**.

**Scheduled, not hoped for:** one major-version upgrade slot between W5 and W6, in the plan rather
than in contingency (ADR-027, decision **D-025**, unratified — §13 Q-02).

---

## 11. Architecturally Significant Requirements and Constraints

### 11.1 ASRs — the requirements that shaped the structure

An ASR is a requirement whose removal would change the architecture. There are eleven.

| # | ASR | Structure it forced |
|---|---|---|
| **ASR-01** | 24-hour offline field operation, zero data loss | Append-only journal + idempotency ledger + one shared offline engine (§10 QAS-05) |
| **ASR-02** | Sensitive personal data must be Bangladesh-resident (NFR-086/099) | Split-residency data model, Z4, residency service as sole path |
| **ASR-03** | The portal platform exists and cannot be replaced (`CON-03`) | API-first, dual-version contract, event + polling fallback, BFF per portal |
| **ASR-04** | Every state change must produce exactly one event | Transactional outbox in every write path (AS-08) |
| **ASR-05** | $0 licence at the ERP core | Odoo CE + OCA + OSS; L6 bounded, individually CFO-approved |
| **ASR-06** | 36-month life across Odoo major versions | Extension-only inheritance (AS-05); planned upgrade slot |
| **ASR-07** | Nine waves into a live business | Forward-only backward-compatible migrations; feature flags; stub-the-seam |
| **ASR-08** | Multi-entity / multi-country without a rebuild | Full dimensional context on every transactional record from W1 |
| **ASR-09** | Financial truth single-sourced and reconcilable | Category G terminal in the dependency graph (LB-04); billable events, not journal entries |
| **ASR-10** | 500–2,000 untrusted external actors | Zone model; server-side scope enforcement; no Z2 internet egress |
| **ASR-11** | One event naming convention across 67 modules | Convention A normative (§7.3); catalogue generated, not maintained |

### 11.2 Constraints — given, not chosen

| # | Constraint | Source | Consequence |
|---|---|---|---|
| **CON-01** | Odoo 19 CE is the ERP core | v1.0 decision, carried | Every extension respects the Odoo inheritance model |
| **CON-02** | PostgreSQL 16 shared with the portal platform | TD-02 | One operational skill set |
| **CON-03** | **The Next.js + Payload CMS portal platform exists and cannot be replaced** | Programme constraint | The most important integration in the estate; it has its own contract |
| **CON-04** | Bengali-first, bilingual throughout | Business, adoption | Structural (§9.3), not cosmetic |
| **CON-05** | Bangladesh statutory regime — VAT/Mushak, Labour Act, PDPA 2026, Cyber Security Ordinance 2025 | Law, verified 2026-08-18 | The compliance pack is L5 by necessity; no OSS equivalent exists |
| **CON-06** | 51+ branches, 500+ staff, absorption ~one major process change per quarter | `06-01` §1 | **Business absorption, not developer capacity, is the binding constraint** on wave size |
| **CON-07** | Field devices: Android 11+, 3 GB RAM, intermittent 4G | NFR-017 | Sets the ceiling on client-side ambition |

### 11.3 Wave 1 is an infrastructure wave, and must be resourced as one

Wave 1 shows **8 modules** in `02-02` §4.2 — the lowest count of any wave. It is nonetheless the
heaviest wave in the programme, because it stands up the platform every later wave assumes:

| Wave 1 platform content | Why it cannot wait |
|---|---|
| Keycloak realm on **46 roles**, R60 eliminated | Retrofitting roles across live record rules is materially riskier (`TR-13`) |
| Kong, 12 API families, idempotency enforcement | Every surface depends on it |
| **Transactional outbox (CD-125)** | AS-08 applied unevenly produces silent divergence (`TR-12`) |
| **Residency service (CD-233) and field-level classification** | Built regardless of `DEP-31`'s outcome (`TR-02`) |
| Notification platform (Novu + CD-234) **ahead of M27 in W4** | Otherwise every W1–W3 module builds its own send path (ADR-022) |
| Vault, ClamAV, observability stack, CI pipeline with all fitness functions | A gate added later does not retro-check what shipped before it |
| Next.js 15 → 16 platform upgrade | Six portals otherwise built on a version leaving support, then migrated together (`TR-06`) |

> **Resource Wave 1 on infrastructure content, not module count** (`TR-11`). This is the architectural
> input to `GV-004` and to the capacity re-plan that audit `M-09` requires.

---

## 12. Rationale

ISO/IEC/IEEE 42010 requires rationale. Six decisions carry most of the structure; each is an ADR in
`AR-004`.

| Decision | Chosen | Rejected | Why it holds |
|---|---|---|---|
| **Odoo 19 CE as system of record** (ADR-001) | Extend a mature ERP | Odoo Enterprise; ERPNext; full custom build | $0 licence vs $45–90K/3yr; **52% of requirements met at L1+L2** before writing code; Odoo talent available locally at sustainable rates. The risk — annual major versions — is answered by AS-05 and a planned upgrade slot, not by hoping |
| **Thin order core + 1:1 line extensions** (ADR-002) | Polymorphism by composition | Wide table; table per line | Nine business lines share one queue, one SLA clock and one customer history without a god object. A tenth line is a module, not a core migration |
| **Transactional outbox everywhere** (ADR-016) | Outbox + relay | Post-commit publish; direct calls | The only pattern making "exactly one event per state change" **true** rather than usually true. At 67 modules, "usually" is a permanent divergence source |
| **Split residency** (ADR-018) | Field-level classification + resident store + single service | Single region; full record residency | PDPA NFR-099 restricts transfer of sensitive identifiers. Classification is *data*, so a change of legal opinion is reclassification, not redesign — this is what absorbs `DEP-31` risk |
| **Self-hosted LLM** (ADR-006) | Ollama, self-hosted | Hosted LLM API; Rasa 3.6 | **Hosted APIs send customer data offshore, breaching PDPA transfer restrictions.** Rasa OSS is in maintenance mode. Also removes per-query cost at 250,000 customers/month |
| **One offline engine across three apps** (ADR-024) | Shared engine | Per-application implementation | Three implementations produce three sets of conflict-resolution bugs, in the highest-risk area of the programme |

### 12.1 What would make this architecture fail

Stated plainly, because each failure mode is known and each has a named control. Absorbed from
Technology Stack Specification §25.5 and extended.

| # | Failure mode | Control | Owner |
|---|---|---|---|
| 1 | **OCA modules forked instead of extended** — every upgrade becomes a manual merge across 140+ modules for 34 months | AS-05 in CI (`FF-03`); fork register; wave-gate review | Solution Architect |
| 2 | **The offline engine loses or double-applies field data** — technicians revert to paper and the field data model is permanently incomplete | `AR-010`; append-only journal; idempotency ledger; dedicated test harness as a release gate; field pilot | Solution Architect |
| 3 | **Residency enforced by convention rather than mechanism** — one bulk loader or one log line puts NID data in the regional store | ORM guard; single residency service; negative tests; log scrubbing; migration path through CD-233 | Head of InfoSec |
| 4 | **Wave 1 resourced by module count** — the platform wave slips and every later wave inherits the slip | §11.3; `GV-004` capacity re-plan | Programme Manager |
| 5 | **The permission model built on 38 roles** — retrofitting 8 roles and eliminating R60 across live record rules | `SC-004`; Wave 0 blocking gate | CTO |
| 6 | **The outbox applied unevenly** — some modules emit reliably, others best-effort; divergence discovered months later in reconciliation | AS-08 CI coverage test (`FF-04`); DoD-05 acceptance gate | Solution Architect |
| 7 | **Bengali treated as a font setting** — invoices and payslips render wrongly to readers while passing automated tests | CD-238 OpenType shaping; per-printer verification at every wave gate | Solution Architect |
| 8 | **The event catalogue maintained by hand** — 988 events cannot be hand-maintained; consumers are built against a 64-row subset that describes 6.5% of the surface | `AR-009` generated catalogue; `IN-003` schema registry | Chief Architect |

---

### 12.2 Decisions Recorded

*The house-template "Decisions Recorded" section is intentionally not duplicated here.* §12 above is
this document's local decision record; the **durable** record — with options considered, rejection
analysis, negative consequences and revisit triggers — is `AR-004`, which holds all 30 ADRs. A second
local table would create a divergent copy of the same decisions, which is the defect class `H-03`
(two incompatible CD registers) describes.

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **Split-residency legal opinion (`DEP-31` / `D-13`)** — does the Authority accept a resident-key join, or is full record residency required? | CFO / Legal / DPO | **Before the Wave 1 architecture is fixed** | Nothing structurally — the mechanism is built either way (`TR-02`) — but a "full record residency" answer materially enlarges `PE-001` and `DA-001` |
| **Q-02** | **Odoo version baseline and upgrade slot (`D-025`)** — ratify one major-version upgrade between W5 and W6? | CTO / Steering | Wave 0 | QAS-11; `GV-004` schedule |
| **Q-03** | **Next.js 15 → 16 timing (`D-026`)** — Wave 1 platform activity, or migrate six portals together later? | CTO | Wave 0 | `TR-06`; six applications' foundation |
| **Q-04** | **Role register completion to R46, R60 eliminated, R54/R57 resolved** — who owns the correction, and by when? | CTO / `SC-004` owner | **Wave 0, blocking** | QAS-08; Keycloak realm design; every record rule |
| **Q-05** | **`NFR-090/091/092` collision (`AP-02`)** — resolve in `05-06`, or is the `-M` suffix adopted permanently? | Enterprise Architecture | Wave 0 | Unambiguous NFR citation across every downstream document |
| **Q-06** | **Event naming convention (ASR-11)** — this document rules for convention A. Ratify, and authorise the rename of ~953 declarations before consumers exist? | Design Authority | **Wave 1, before `IN-003`** | `AR-009`, `IN-003`, every consumer |
| **Q-07** | **P07 mobile surface (`D-027`)** — PWA in W7, or a second mobile framework? | CTO | Wave 6 | Prevents a second mobile framework entering the estate by default |
| **Q-08** | **Is 1000FiX a "significant data fiduciary" under PDPA 2026?** At 250,000+ customers/month it almost certainly is, which mandates a Chief Data Officer (NFR-096) and raises penalty exposure to BDT 50 lakh | DPO / Legal | Before W4 | `SC-003` DPIA scope; role R40 |

> An open question with no owner and no needed-by date is not an open question — it is an unrecorded
> risk. All eight are escalated to `GV-005` RAID on issue of this document.

---

## 14. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every stakeholder concern in §3.2 is framed by at least one viewpoint | §4.2 matrix — 14 concerns, 14 framed |
| AC-02 | Every viewpoint in §4.1 has a conforming view in §5–§9 | VP-1→§5, VP-2→§6, VP-3→§7.1–7.4, VP-4→§7.5, VP-5→§6.4/§11, VP-6→§8, VP-7→§9 |
| AC-03 | At least six views are present with rationale | Seven views present; rationale in §12 |
| AC-04 | Every quality-attribute scenario is in six-part form with a measurable response measure and a named tactic | §10.2 — 11 scenarios |
| AC-05 | Every figure describing the estate is counted, with an enumeration timestamp | §2.4 |
| AC-06 | Every architecturally significant decision has an ADR reference | §12 and §11.1 → `AR-004` |
| AC-07 | Trust boundaries are stated in a form `SC-002` can perform STRIDE against | §8.1 — six zones with ingress, egress and controls |
| AC-08 | Every open question has an owner and a needed-by date | §13 — eight questions |
| AC-09 | No content is duplicated from `1000fix_ERP_Module` or `project_content`; both are referenced | `PG-02` compliance; §2.2 |
| AC-10 | Correspondence rules keep views consistent | §14.1 below |

### 14.1 Correspondence rules — ISO/IEC/IEEE 42010 §5.6

A view set that can disagree with itself is not an architecture description. Six rules, each
mechanically checkable:

| # | Correspondence | Check |
|---|---|---|
| **CR-01** | Every module in the logical view (§6.2) appears in the development view's build sequence (`AR-006`) | Set equality, 67 = 67 |
| **CR-02** | Every component in the deployment view (§8) is produced by a deliverable in the development view | Set inclusion |
| **CR-03** | Every interface in §7.1 is exposed by exactly one module in §6.2 | Uniqueness of owner |
| **CR-04** | Every event in the runtime view is registered in `IN-003` and produced by exactly one module | **Currently fails — 953 unregistered (§7.4).** Tracked as `PGD-A3-04`; closes with `AR-009` |
| **CR-05** | Every quality-attribute scenario names a tactic realised in at least one view | Manual at review; 11 of 11 hold |
| **CR-06** | Every trust zone in §8.1 has at least one enforcement control in `AR-012` | 6 of 6 |

**Definition of done.** Complete when every criterion above is met, `PGD-000`'s `AR-001` row is
updated with a fresh enumeration timestamp, and the Design Authority has signed. **`AR-001` cannot
reach ✅ under `PGD-000` §0.3 test (c) until `RR-003` publishes the section set for an architecture
description** — until then it is ✅-candidate, and this document says so rather than asserting ✅.

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `RQ-001` SRS | Requirements this architecture must satisfy — **not yet written**; §10 uses `05-06` NFRs directly as the interim source |
| Upstream | `RQ-006` NFR Specification | Quality-attribute scenarios derive from it |
| Upstream | `AR-002` | Enterprise position and system-of-record boundary |
| Downstream | `AR-003` SDD | Realises §6.4 component structure at module level |
| Downstream | `AR-004` ADR Library | Holds the durable record of every decision indexed in §12 |
| Downstream | `AR-005`, `AR-006` | Adjudicate §6.5 boundaries and realise CR-01 |
| Downstream | `AR-007` | Makes AS-05 / QAS-11 mechanically enforceable |
| Downstream | `AR-008` | Details the §6.3 kernel as aggregates and invariants |
| Downstream | `AR-009` | Designs §7.3–§7.4 messaging; executes the ASR-11 ruling |
| Downstream | `AR-010` | Designs QAS-05 in full |
| Downstream | `AR-011` | Designs the LB-06 advisory-write model |
| Downstream | `AR-012` | Converts §6.5, §8.1 and §10 into fitness functions |
| Downstream | `DA-001`, `DA-002`, `DA-005` | Realise the information view and residency classification |
| Downstream | `IN-001`, `IN-002`, `IN-003` | Realise §7.1–§7.3 |
| Downstream | `SC-001`, `SC-002`, `SC-004`, `SC-007` | Consume §8.1 zones and §8.3 residency |
| Downstream | `PE-001`, `PE-002`, `PE-004`, `PE-007` | Realise §8 deployment view |
| Downstream | `BE-004` | Realises the development view repository structure |
| Downstream | `QA-001`, `QA-006` | Derive test levels and performance tests from §10 |
| Lateral | `../../1000fix_ERP_Module/02_Architecture/02-01`, `02-02`, `02-05` | Sources; superseded as *architecture description* by this document, retained as catalogue and stack authority |
| Lateral | `../../primary-doc/…Technology_Stack_Specification.md` | Technology authority. Where it and this document disagree on **structure**, this document wins; on **technology selection or version**, it wins |
| Lateral | `../../1000fix_ERP_Module/03_Modules/**/M*.md` | 67 specifications realised by this structure |

---

## 16. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./AR-002` … `./AR-013` · `../_AUDIT/PGD-AUDIT-001_Register_Integrity_Audit.md` ·
`../_AUDIT/PGD-AUDIT-003_Category_02_Architecture_and_Design_Audit.md` · `../_templates/TPL_Guiding_Document.md`

**Workspace**
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §3, §8, §12, §14, §16, §17, §18, §23, §24, §25 ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` ·
`../../1000fix_ERP_Module/02_Architecture/02-01`, `02-02`, `02-05` ·
`../../1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02`, `05-03`, `05-04`, `05-06` ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01`, `06-02` ·
`../../1000fix_ERP_Module/03_Modules/**/M*.md` (67 files) · `../../project_content/_AUDIT/AUDIT-016`, `AUDIT-017`

**External standards and sources**

| Standard / source | Version | Verified |
|---|---|---|
| ISO/IEC/IEEE 42010 — Architecture description | 2022 | 2026-08-18 |
| ISO/IEC 25010 — Product quality model | 2023 | 2026-08-18 |
| IEEE 1016 — Software design descriptions | 2009 | 2026-08-18 |
| ISO/IEC 27001 Annex A | 2022 | 2026-08-18 |
| arc42 | 7.0 | 2026-08-18 |
| Personal Data Protection Act 2026 (Law 63 of 2026), Bangladesh | In force; enforcement ~13 May 2027 | 2026-08-18 |
| Cyber Security Ordinance 2025, Bangladesh | In force (21 May 2025) | 2026-08-18 |
| VAT and Supplementary Duty Act 2012 — Mushak 6.3, 9.1 | In force | 2026-08-18 |
| Odoo 19.0 | Released 18 September 2025; supported to ~September 2028 | 2026-08-18 |

> Every relative path above was resolved against the filesystem at 2026-08-18 02:05 (+06) before issue,
> per rule `PG-M9`. Paths to `AR-002`…`AR-013` and `PGD-AUDIT-002` resolve on completion of this
> category's authoring set, which is issued together.

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. First architecture description for the ERP. Closes `C-01`; contributes to `C-05`, `AP-01`, `AP-02`, `OP-01`, `OP-02`. Raises `PGD-A3-01`…`PGD-A3-06` | *Pending — Design Authority not yet constituted (`PGD-A1-09`)* |

---

*`AR-001` · Category 02 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
