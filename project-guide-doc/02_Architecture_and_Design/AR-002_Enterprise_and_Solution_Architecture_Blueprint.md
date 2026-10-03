---
id: AR-002
title: Enterprise & Solution Architecture Blueprint
category: 02 — Architecture & Design
code: AR
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Architect
approver: Chief Technology Officer
standards_basis: TOGAF 10 ADM Phases A–B · ISO/IEC/IEEE 42010:2022 · Business Capability Modelling
traces_to: PGD-000 AR-002 · CON-03 · 00-01 §5 (system-of-record boundary) · 02-01 §1 · audit finding C-01
depends_on: GV-001 (Programme Charter) · AR-001 (SAD)
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 02:05 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# AR-002 — Enterprise & Solution Architecture Blueprint

### Category 02 · Code `AR` · TOGAF 10 ADM Phases A–B · ISO/IEC/IEEE 42010:2022

---

## 1. Purpose

`AR-001` describes how **the ERP** is structured. This document describes **where the ERP sits in the
1000FiX digital estate** — what it owns, what it does not, and what the rule is when something new
arrives and nobody is sure which system should hold it.

It exists because the estate's most consequential architectural rule currently appears **once, as a
single sentence, in `00-01` §5**: *"ERP owns state and truth; portals own experience and reach."*
That sentence is correct and it is load-bearing, and it is enforced nowhere. A rule with 609 documents
resting on it and no enforcement mechanism will be broken by the first delivery deadline that makes
breaking it convenient.

It unblocks: the boundary adjudication in `AR-005`, the portal contract in `IN-001`/`IN-002`, and the
"who owns this field" question that `DA-003` data governance must answer for every one of the 1,335 entities measured in `AR-008` §2.2.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The 1000FiX digital estate — every system that holds business state, and its relationship to the ERP |
| 2 | The **system-of-record boundary rule**, stated as a decidable test rather than a slogan |
| 3 | Business capability map, and the allocation of each capability to a system |
| 4 | The `CON-03` portal-platform constraint, given an architecture treatment rather than a mention |
| 5 | Application, data, technology and integration positions at the estate level |
| 6 | Estate-level principles that bind every system, not only the ERP |
| 7 | The target-state roadmap and the transition states between today and Wave 9 |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Internal structure of the ERP | `AR-001` | This document stops at the ERP's boundary and looks outward |
| Portal internal architecture | Digital team | The portal platform is a constrained external system (`CON-03`), not ours to design |
| Contested capability boundaries **between ERP modules** | `AR-005` | Intra-system adjudication |
| Contract mechanics | `IN-001`, `IN-002` | This document fixes *who owns what*; the contract expresses it |
| Legacy retirement sequencing | `RL-006` | Named here as a target-state consequence; planned there |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| CTO, Steering Committee | The one-page answer to "what are we actually building, and what already exists" |
| Implementation vendor | The boundary they must not cross, and the platform they must integrate with |
| Digital / portal team | The contract's premise — what the ERP will and will not own |
| Data Protection Officer | Which system is *controller* for which personal data (§5.4) |
| Solution Architect | The escalation rule when a new capability has no obvious home (§4.3) |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | Conformance | Departure and rationale |
|---|---|---|---|
| TOGAF 10 ADM | Phase A — Architecture Vision | §3 estate context, §7 target state | Full Vision document deliverable is `GV-001`'s; not duplicated |
| TOGAF 10 ADM | Phase B — Business Architecture | §4 capability map and allocation | **Departure:** no value-stream or organisation-map artefacts. The programme is a single-system build; producing the full Phase B set would be ceremony |
| TOGAF 10 | Architecture Principles | §6 | Principles are stated with *implication* and *enforcement*, not only *rationale* — a TOGAF principle with no enforcement is the failure mode this document exists to prevent |
| ISO/IEC/IEEE 42010:2022 | Architecture description | Inherits `AR-001`'s viewpoint set at estate scope | Not re-declared; `PG-02` |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `../../1000fix_ERP_Module/00_Governance_and_Charter/00-01_Master_Index_and_Document_Map.md` §5 | The one-sentence boundary rule this document formalises |
| `../../1000fix_ERP_Module/02_Architecture/02-01_*.md` §1 | ERP as system of record; layer position |
| `../../1000fix_ERP_Module/04_Portals_and_Applications/04-00_*.md` §1, §3 | Portal principles PS-01…PS-12; the "surfaces, not systems" position |
| `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` §3 | The `CON-03` field-ownership table — the only place ownership is currently written down |
| `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §12.2.5 | `CON-03` contract rules, restated with enforcement |
| `../../1000fix_ERP_Module/02_Architecture/02-02_*.md` §9 | Legacy decommission map — 21 named legacy systems/practices |
| `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_*.md` §12 | 11 migration sources, feeding §7.3 |

### 2.3 Audit findings this document contributes to closing

| Finding | How |
|---|---|
| `C-01` Two architectures described simultaneously | §4.2 allocates capability to the eleven-category decomposition only |
| `AF-01` 12 portal specifications sit in the wrong folder | §3.3 records that portals are **experience surfaces of one system**, which is why filing them under `03_Modules/K_Platform_and_Technology/` is a filing defect and not an architectural statement |
| `PGD-A1-05` Unbudgeted work streams | §7.4 names the estate-level consequence: the portal-side work implied by `CON-03` is in nobody's estimate |

---

## 3. The 1000FiX Digital Estate

### 3.1 Estate map

```
                    ┌──────────────────────────────────────────────────────┐
                    │  CORPORATE WEB PRESENCE                              │
                    │  1000fix.com · marketing · blog · SEO · brand        │
                    │  Payload CMS 3 · OWNS: content. HOLDS NO BUSINESS    │
                    │  STATE                                                │
                    └───────────────────────┬──────────────────────────────┘
                                            │ shares platform, not data
                    ┌───────────────────────▼──────────────────────────────┐
                    │  PORTAL PLATFORM  (CON-03 — EXISTS, CANNOT BE        │
                    │  REPLACED)                                            │
                    │  Next.js 15/16 · React 19 · Payload CMS 3            │
                    │  Hosts 6 of the 12 experience surfaces               │
                    │  OWNS: presentation, session UX, content             │
                    │  OWNS NO BUSINESS STATE — may cache, never for truth │
                    └───────────────────────┬──────────────────────────────┘
                                            │ versioned API + events (IN-002)
   ╔════════════════════════════════════════▼══════════════════════════════════════╗
   ║  1000FiX ERP SYSTEM v2.0 — THE SYSTEM OF RECORD                               ║
   ║  67 modules · 1,335 entities · 12 surfaces · 16 domain services                 ║
   ║  OWNS: every business object with a lifecycle, a financial consequence        ║
   ║         or an audit obligation                                                 ║
   ╚════════════════════════════════════════┬══════════════════════════════════════╝
                                            │
      ┌─────────────────────────────────────┼──────────────────────────────────┐
      │                                     │                                  │
┌─────▼──────────────┐   ┌──────────────────▼──────────┐   ┌───────────────────▼───┐
│ IDENTITY           │   │ DATA & INTELLIGENCE          │   │ 48 LEGACY SOURCES     │
│ Keycloak 26.x      │   │ ClickHouse · Metabase ·      │   │ spreadsheets ·        │
│ OWNS: authentica-  │   │ MLflow · Grafana             │   │ station.1000fix.com · │
│ tion, federation,  │   │ OWNS: derived insight.       │   │ paper · legacy        │
│ session            │   │ OWNS NO SOURCE TRUTH         │   │ tracker · accounting  │
│ OWNS NO BUSINESS   │   │ (read-only downstream —       │   │ TO BE RETIRED (RL-006)│
│ DATA               │   │  AR-001 LB-06)                │   │                        │
└────────────────────┘   └──────────────────────────────┘   └───────────────────────┘
```

### 3.2 Systems register — and what each owns

| # | System | Status | **Owns** | **Must never own** |
|---|---|---|---|---|
| ES-01 | **1000FiX ERP v2.0** | To build | Every business object with a lifecycle, financial consequence or audit obligation; all master data; the ledger | Marketing content; authentication credentials |
| ES-02 | **Portal platform** (Next.js + Payload CMS 3) | **Exists — `CON-03`** | Presentation, navigation, content, SEO, session UX | **Any authoritative business state.** May cache for performance, never for truth |
| ES-03 | **Corporate web presence** | Exists | Brand, marketing, blog | Business state; customer records |
| ES-04 | **Keycloak** | To deploy (W1) | Authentication, MFA, federation, session, realm roles | Business data; authorisation *decisions* about records (those are Odoo record rules) |
| ES-05 | **Analytics estate** (ClickHouse, Metabase, Grafana, MLflow) | To deploy (W4–W8) | Derived insight, models, dashboards | Source truth. Writes back only as advisory records (`AR-001` LB-06) |
| ES-06 | **Bangladesh-resident store (Z4)** | To deploy (W1) | Residency-classified fields only | Anything not residency-classified — it is not a second general database |
| ES-07 | **48 legacy sources** | To retire | Nothing, at target state | — |
| ES-08 | **Third-party systems** (payments, couriers, brands, KYC, telephony) | External | Their own domain | Our system of record |

### 3.3 A note on where portal specifications are filed

`P01`–`P12` are filed in `1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/`, alongside
modules. Audit **`AF-01`** raised this as a misfiling, and it is one.

**The architectural statement, so that the filing defect is not mistaken for an architectural one:**
a portal is an **experience surface of the ERP**, not a module of it and not a separate system. It
has no data of its own, no rules of its own and no lifecycle of its own. That is why it can be built
by a different team on a different stack on a different release cadence — and why the contract between
them (`IN-002`) is the only thing that must be stable.

---

## 4. Business Capability Map and Allocation

### 4.1 Capability map — Level 1

Fourteen revenue streams and the shared operational spine beneath them.

| # | Capability | Level 2 | Owning system | ERP category |
|---|---|---|---|---|
| BC-01 | **Demand capture** | Marketing, campaigns, storefront, marketplace discovery, referral | ERP (transactional) + Portal (presentation) | B, C |
| BC-02 | **Customer and party management** | Identity, hierarchy, consent, segmentation, credit | **ERP** | B |
| BC-03 | **Commercial agreement** | Quotation, pricing, contract, warranty, subscription | **ERP** | C |
| BC-04 | **Service execution** | Intake, diagnosis, dispatch, field work, workshop, QC, handover | **ERP** | A |
| BC-05 | **Logistics and custody** | Pick & drop, courier, chain of custody, POD | **ERP** | A |
| BC-06 | **Supply** | Parts, warehouse, procurement, supplier, import | **ERP** | E |
| BC-07 | **Asset lifecycle** | Device registry, rental, trade-in, refurbishment, e-waste, fleet, facilities | **ERP** | D, F |
| BC-08 | **Money** | Billing, AR, AP, treasury, tax, revenue recognition, settlement, costing | **ERP** | G |
| BC-09 | **People** | HR, time, payroll, performance, learning, talent, safety | **ERP** | H |
| BC-10 | **Governance and evidence** | Quality, risk, documents, e-signature, knowledge | **ERP** | I |
| BC-11 | **Insight** | Warehouse, BI, ML, automation | ERP (instrumentation) + analytics estate (serving) | J |
| BC-12 | **Platform** | Integration, identity, configuration, MDM, localisation, ITSM, PPM | ERP + Keycloak | K |
| BC-13 | **Experience** | 12 surfaces, design system, content | **Portal platform + ERP-hosted surfaces** | — |
| BC-14 | **Trust and compliance** | Consent, residency, retention, audit, breach response | **ERP + Z4 + DPO function** | I, K |

### 4.2 Allocation rule — the boundary test

The `00-01` §5 sentence, converted into something a developer can apply on a Tuesday afternoon.

> **The system-of-record test.** A capability belongs to the ERP if **any** of the following is true:
>
> 1. It creates or changes an object with a **lifecycle** — something that has states and transitions.
> 2. It has a **financial consequence** — anything that eventually reaches the ledger.
> 3. It carries an **audit or statutory obligation** — anything a regulator, auditor or court could ask about.
> 4. It is **master data** — anything more than one consumer must agree on.
>
> If none is true, it belongs to the surface that presents it.

**Worked applications of the test, including the ones people get wrong:**

| Capability | Test result | Allocation |
|---|---|---|
| Service booking form layout and copy | None true | **Portal** |
| The service order the form creates | 1, 2, 3 | **ERP (M01)** |
| Blog article about laptop repair | None true | **Portal CMS** |
| Service catalogue and prices shown in that article | 4 (and 2) | **ERP (M37, M11)**, published to the portal |
| Customer's saved delivery address | 4 | **ERP (M33)** — because dispatch, invoicing and logistics must all agree on it |
| Customer's chosen UI theme | None true | **Portal** |
| Customer's **language preference** | 4 | **ERP (M33)** — it drives notifications and printed documents, not only the screen |
| Marketplace seller's public profile photo | None true | Portal presentation, **ERP-owned asset** (it is evidence in a dispute) |
| Seller's KYC documents | 3, 4 | **ERP → Z4 resident store** |
| "Recently viewed" list | None true | **Portal** |
| Loyalty points balance | 1, 2, 3 | **ERP (M10)** |

> **The rule that resolves the argument.** When the test is genuinely ambiguous, **the ERP wins**.
> Moving a field from the portal to the ERP later is a migration; moving it from the ERP to the portal
> later is a deletion of history. The asymmetry of the two mistakes decides the default.

### 4.3 Escalation

| Situation | Action |
|---|---|
| A capability is contested between the ERP and the portal | Apply §4.2. If still ambiguous, ERP owns it; record as an ADR in `AR-004` |
| A capability is contested between **two ERP modules** | `AR-005` — the module boundary register |
| A new external system is proposed that would hold business state | **Design Authority approval required.** Default position: no. The estate has 48 legacy sources precisely because this was never gated |

---

## 5. Estate-Level Architecture Positions

### 5.1 Application position

| Position | Statement |
|---|---|
| AP-01 | **One system of record.** There is exactly one. Everything else is a surface, a derivation or an external party |
| AP-02 | **Surfaces are replaceable; the record is not.** A portal may be rewritten in a different framework without a data migration. This is what the API contract buys |
| AP-03 | **The portal platform is a constraint, not a choice.** `CON-03`. The ERP adapts to it, not the reverse |
| AP-04 | **Twelve surfaces, one design system.** NFR-080 and PS-06. Twelve portals with twelve component libraries is twelve products — `UX-001`'s to prevent |

### 5.2 Data position

| Position | Statement |
|---|---|
| DP-01 | **Every field has exactly one owning system, declared.** IP-01. The `CON-03` ownership table (`05-03` §3.1) is the pattern; `DA-002` extends it to all 1,335 entities (`AR-008` §2.2) |
| DP-02 | **Integrations synchronise; they do not duplicate authority.** A cached copy is stale by definition and must be treated as such |
| DP-03 | **Residency is a property of the field, not of the system.** This is what makes the split-residency design survivable |
| DP-04 | **Analytics is downstream and read-only.** A warehouse that writes back is a second system of record with none of the controls |

### 5.3 Technology position

| Position | Statement |
|---|---|
| TP-01 | **$0 licence at the core**, with a bounded, individually CFO-approved L6 exception set. Currently four components, ~$0–36K over three years |
| TP-02 | **Shared technology across the estate where possible** — PostgreSQL is shared with the portal platform (TD-02) so there is one operational skill set |
| TP-03 | **Self-hosting where data would otherwise leave the country.** LLM inference, routing, BI, monitoring. This is a PDPA position before it is a cost position |
| TP-04 | **Every open-source component has a named fallback** against licence change — Kafka for Redpanda, Apache-only features for TimescaleDB (`TR-09`) |

### 5.4 Compliance position — who is controller for what

The PDPA 2026 question the estate has never answered, and which `SC-003`'s DPIA will require.

| Personal data | Controller | Processor | Residency |
|---|---|---|---|
| Customer identity, contact, service history | **1000FiX (ERP)** | Hosting provider | Regional; identifiers in Z4 |
| Customer NID / passport / TIN | **1000FiX (ERP → Z4)** | — | **Bangladesh-resident, mandatory** |
| Employee records, payroll, biometric templates | **1000FiX (ERP → Z4 for templates)** | — | Templates resident |
| Marketplace seller KYC | **1000FiX (ERP → Z4)** | KYC provider (processor) | **Resident** |
| Recovered customer data (M06) | **The customer is controller; 1000FiX is processor** | 1000FiX | **Resident, per-case keys, dual control** |
| Portal analytics / behavioural | **1000FiX** | Analytics provider | Regional; must not join to resident identifiers |
| Corporate client end-user identity (federated) | **The client** | 1000FiX | Per the client's own regime |

> **The M06 row is the one to notice.** For recovered customer data, **1000FiX is a processor, not a
> controller** — a different and in some respects stricter obligation set under PDPA 2026, flowed down
> by contract (NFR-098). No document in the estate currently states this. Escalated to `SC-003`.

---

## 6. Estate Architecture Principles

Seven principles. Each states its implication and — the part usually missing — **how it is enforced**.
A principle with no enforcement column is a preference.

| # | Principle | Implication | **Enforcement** |
|---|---|---|---|
| **EP-01** | **The ERP owns state and truth; surfaces own experience and reach** | No surface holds authoritative state or implements a business rule | Portal contract test PS-11 — an invalid payload posted directly to the API must be rejected (`AR-012` `FF-12`) |
| **EP-02** | **One owner per field, declared** | Every field in `DA-002` names an owning system and module | Data dictionary completeness gate; `DA-002` acceptance |
| **EP-03** | **Buy the regulated, build the differentiating, self-host the sensitive** | Payments and e-signature are bought; dispatch and settlement are built; LLM and BI are self-hosted | `AR-013` build-vs-buy register; CFO approval per L6 component |
| **EP-04** | **Interfaces are contracts, and contracts are versioned** | Two concurrent versions, six months' deprecation | `IN-005` governance standard; Kong route configuration |
| **EP-05** | **Residency is designed, not hosted** | Classification at field level, enforced at write time | ORM guard + `AR-012` `FF-09` |
| **EP-06** | **Nothing new holds business state without Design Authority approval** | The 48-legacy-source problem does not recur | `GV-002` Design Authority; architecture change request |
| **EP-07** | **Every capability retires something** | Each wave names what it switches off | `RL-006` decommissioning plan; wave-gate evidence |

> **EP-07 is the discipline the estate has never had.** `02-02` §9 names 21 legacy systems and
> practices to be replaced. Systems that are never formally switched off keep costing money and keep
> holding personal data — which after May 2027 is a statutory exposure, not an untidiness.

---

## 7. Target State and Transition

### 7.1 Target state (end of Wave 9, month 36)

| Dimension | Today | Target |
|---|---|---|
| Systems of record | 48 legacy sources + spreadsheets + paper | **1** |
| Customer-facing surfaces | Website + two legacy trackers | **12 surfaces on one contract** |
| Identity stores | Per-system, uncounted | **1 (Keycloak), federated to corporate clients** |
| Financial truth | Standalone accounting + manual preparation | **One ledger, statutory returns generated** |
| Personal data residency | Undesigned | **Classified at field level, resident store enforced** |
| Reporting | Excel packs | **Warehouse-served, no manual packs** (W8 gate) |
| Countries | 1 | **Configuration-ready for 5; 1 live** |

### 7.2 Transition states

Nine waves means nine transition states, each of which must be a **coherent system**, not a
half-migration. The estate-level rule is that at every wave boundary, for every business object,
**exactly one system is authoritative** — never two, never zero.

| Wave | Estate change | The "exactly one authority" risk it creates |
|---|---|---|
| W1 | Identity, integration, party, asset, service core live at 6 sites | Customer master exists in both ERP and spreadsheets at non-pilot branches — **mitigated by branch-scoped cutover, not date-scoped** |
| W2 | Field ops, inventory, P01/P02 live across Dhaka | Two order-tracking surfaces (`station.1000fix.com`, legacy tracker) must be **switched off at W2 gate**, not left running |
| W3 | Finance live; legacy accounting retired | One-month parallel run, then hard retirement. **Two ledgers is the worst state in the programme** |
| W4 | v1.0 scope complete; contracts, warranty, contact centre | Brand claim email path retired; P08 is the only channel |
| W5 | HR/payroll live; 51+ centres on platform | Two pay cycles parallel; **zero tolerance for pay errors** |
| W6–W8 | New business lines, marketplace, intelligence | Each new line is greenfield — low dual-authority risk |
| W9 | Multi-entity | Configuration, not migration |

### 7.3 Legacy retirement — the estate-level view

`02-02` §9 lists 21 named systems and practices; `05-02` §12 lists 11 migration sources; `DM-002`
inventories **48 legacy sources, all unprofiled** (`AUDIT-011`, critical).

**The estate-level requirement**, which `RL-006` and `MG-002` will execute: no legacy source is
declared retired until **(a)** its data is migrated and reconciled, **(b)** its access is revoked,
**(c)** its licence or hosting is terminated, and **(d)** the personal data it holds is disposed of
or transferred under the retention schedule. Retirement without (d) leaves a PDPA liability in a
system nobody administers any more.

### 7.4 The estate-level gap nobody owns

| Gap | Consequence | Referred to |
|---|---|---|
| **The portal-side work implied by `CON-03` is in no estimate.** Six Next.js applications consume 12 API families, must support two concurrent API versions, and must implement graceful degradation. The 1,513 PW measures **ERP** effort | The `CON-03` contract has two sides and one budget | `GV-007`, `CO-005`; extends `PGD-A1-05` |
| **48 legacy sources are unprofiled** | Every migration mapping is written against assumed structure | `MG-002` (P0, "Now") |
| **No system-of-record decision gate exists** | A 49th legacy source can be created by any team with a deadline | `GV-002` Design Authority; principle EP-06 |

---

## 8. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-PGD-A3-01 | Boundary rule formalisation | Keep the one-sentence rule; write a policy; write a **decidable test** | **Decidable test (§4.2)** with an ambiguity default | A rule that cannot be applied by a developer without escalating is not enforced | Every ambiguous case now resolves to the ERP, which is the conservative direction |
| D-PGD-A3-02 | Portal platform position | Replace; wrap; **accept as constraint** | **Accept as constraint (`CON-03`)** | It exists, it works, and replacing it is not funded | The API contract becomes the most important integration in the estate |
| D-PGD-A3-03 | Analytics write-back | Allow advisory writes; **read-only + advisory record**; full write-back | **Read-only, advisory record only** | A warehouse that writes to transactional aggregates is a second system of record with none of the controls | ML outputs are `fix.ml.prediction.log` rows, never state mutations (`AR-001` LB-06) |
| D-PGD-A3-04 | Controller/processor position for M06 recovered data | Unstated; controller; **processor** | **1000FiX is processor; the customer is controller** | The data is the customer's; 1000FiX holds it to perform a service | Stricter flow-down obligations (NFR-098); must be in `SC-003` and the M06 customer contract |

> Significant decisions are additionally recorded as ADRs in `AR-004`. This table is the local record.

---

## 9. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | **Who owns and funds the portal side of the `CON-03` contract?** Six applications, two API versions, graceful degradation — in no estimate | Programme Director / CTO | W1 | `GV-007`, `CO-005`; the contract itself |
| Q-02 | Is the corporate web presence (ES-03) in programme scope for the design system (NFR-080), or outside it? | CTO / Marketing | W1 | `UX-001` scope and cost |
| Q-03 | **Marketplace commercial model** — one of the five decisions `00-01` §6 records as open with no body empowered to close them | Steering Committee | W6 | M12 architecture; settlement design |
| Q-04 | Legal entity structure and country sequence | Steering Committee | W8 | M65; multi-entity configuration |
| Q-05 | Does the M06 processor position (§5.4) require a customer contract amendment? | Legal / DPO | W6 | M06 go-live |

---

## 10. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The system-of-record rule is stated as a decidable test with worked examples | §4.2 — 11 worked cases including the counter-intuitive ones |
| AC-02 | Every Level-1 business capability is allocated to exactly one owning system | §4.1 — 14 capabilities |
| AC-03 | `CON-03` has an architecture treatment, not a mention | §3.2 ES-02, §4.2, §5.1 AP-03, §7.4 |
| AC-04 | Every estate principle names its enforcement mechanism | §6 — 7 principles, 7 mechanisms |
| AC-05 | Controller/processor position stated per personal-data class | §5.4 |
| AC-06 | Target state and every transition state named, with the dual-authority risk each creates | §7.1, §7.2 |
| AC-07 | Every open question has an owner and a needed-by date | §9 |

**Definition of done.** Complete when every criterion is met, `PGD-000`'s `AR-002` row is updated
with a fresh enumeration timestamp, and the CTO has signed.

---

## 11. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `GV-001` Programme Charter | Authorises the target state — **not yet approved** |
| Upstream | `AR-001` SAD | This document sits above it and is consistent with its §5 context view |
| Downstream | `AR-005` | Intra-ERP boundary adjudication, using §4.3 escalation |
| Downstream | `IN-001`, `IN-002`, `IN-005` | Realise the `CON-03` contract |
| Downstream | `DA-002`, `DA-003` | Extend DP-01 field ownership to all 1,335 entities |
| Downstream | `SC-003` | Consumes §5.4 controller/processor positions |
| Downstream | `UX-001` | Realises AP-04 one design system |
| Downstream | `RL-006` | Executes EP-07 and §7.3 |
| Lateral | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-01` §5 | The sentence this document formalises |
| Lateral | `../../1000fix_ERP_Module/04_Portals_and_Applications/04-00` | Portal principles consistent with §3.3 |

---

## 12. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./AR-001_Software_Architecture_Document.md` · `./AR-004_Architecture_Decision_Record_Library.md` ·
`./AR-005_Module_Boundary_and_Overlap_Rules_Register.md`

**Workspace**
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-01` · `.../02_Architecture/02-01`, `02-02` §9 ·
`.../04_Portals_and_Applications/04-00` · `.../05_Cross_Cutting_Specifications/05-02` §12, `05-03` §3 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §12.2.5

**External standards**

| Standard | Version | Verified |
|---|---|---|
| TOGAF Standard, 10th Edition — ADM Phases A–B | 10 | 2026-08-18 |
| ISO/IEC/IEEE 42010 | 2022 | 2026-08-18 |
| Personal Data Protection Act 2026, Bangladesh — controller/processor obligations | In force | 2026-08-18 |

---

## 13. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Formalises the system-of-record boundary as a decidable test; gives `CON-03` an architecture treatment; states controller/processor positions | *Pending — CTO* |

---

*`AR-002` · Category 02 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
