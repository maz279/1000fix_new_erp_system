# TECHNOLOGY STACK SPECIFICATION

# Comprehensive ERP System & Smart Portal Suite — Version 2.0

## 1000FiX Services Limited

---

| **Document Information** | |
|---|---|
| **Document Title** | Technology Stack Specification — Comprehensive ERP System & Smart Portal Suite |
| **Organisation** | 1000FiX Services Limited |
| **Document Version** | **2.0** |
| **Date** | 13 August 2026 |
| **Reference Number** | **1000FIX-ERP-TECHSTACK-2026-002** |
| **Supersedes** | 1000FIX-ERP-TECHSTACK-2026-001 (v1.0, 18 March 2026) |
| **Derived From** | **1000FIX-ERP-RFP-2026-002** (RFP v2.0) — governing commercial and architectural authority |
| **Companion Documents** | 1000FIX-ERP-BRD-2026-002 (BRD v2.0) · 1000FIX-ERP-URD-2026-002 (URD v2.0) |
| **Authoritative Register** | `02-02_Module_Catalogue_Master_Register.md` (67 modules, 11 categories) |
| **Classification** | **CONFIDENTIAL** — Technical Specification Document |
| **Status** | **DRAFT FOR APPROVAL** — Architecture Board and CTO |
| **Prepared By** | Enterprise Architecture, 1000FiX Services Limited |

---

**CONFIDENTIALITY NOTICE**

This Technology Stack Specification and all accompanying materials are the confidential property of
1000FiX Services Limited. The information is intended solely for authorised implementation teams,
evaluated technology partners under executed non-disclosure agreement, and internal stakeholders of
the ERP programme. Recipients must not disclose, reproduce or distribute any part of this document
without prior written consent. This document contains the Company's complete technical position,
including its disclosed defects and open decisions, and is not for external circulation.

---

## DOCUMENT AUTHORITY AND PRECEDENCE

This document is **derived entirely from RFP v2.0**. Where this specification and any other document
disagree, the following order of precedence applies:

| Precedence | Document | Authoritative For |
|---|---|---|
| **1** | `02-02_Module_Catalogue_Master_Register.md` | Module identity, code, category, ownership, priority, wave |
| **2** | `05-01` … `05-06` Cross-Cutting Specifications | Requirement IDs, entities, integrations, roles, rules, NFRs |
| **3** | Module specification files (`03_Modules/**/M*.md`) — Annex 1 | Individual functional requirements and acceptance criteria |
| **4** | **RFP v2.0** | Commercial terms, procurement, evaluation, **and the reference architecture the stack must realise** |
| **5** | BRD v2.0 | Business rationale, objectives, process design, benefit case |
| **6** | URD v2.0 | User needs, personas, stories, journeys, usability |
| **7** | **This Technology Stack Specification** | **Component selection, version, licence, configuration, sizing, and the mapping from every requirement class to the technology that delivers it** |
| **8** | Detailed design and build artefacts | Implementation detail below the component level |

**What this means in practice.** This document does not create scope. It **realises** scope that the
register and the RFP have already fixed. Where this document appears to add a capability, it is
selecting the technology for a capability already required. Where it appears to remove one, that is a
defect and must be raised — see §25.

---

## DOCUMENT REVISION HISTORY

| Version | Date | Author | Description |
|---|---|---|---|
| 1.0 | 18 March 2026 | 1000FiX IT Team | Initial release — 5-layer stack, 11 modules, 6 portals, 405 requirements, 20 custom modules, 18-month plan, single-region Singapore hosting |
| **2.0** | **13 August 2026** | **Enterprise Architecture** | **Complete re-baseline against the v2.0 specification set. Restated from 11 modules / 6 portals / 405 requirements / 18 months to 67 modules in 11 categories / 12 portals / 2,930 measured requirements / 225 entities / 47 integrations / 101 NFRs / 46 roles / 9 waves over 36 months. Sixth delivery layer (L6 commercial) added. Custom-development register completed from 30-module to 67-module coverage. Single-region topology replaced by the split-residency architecture required by the Personal Data Protection Act 2026 (NFR-086). Regulatory position corrected — Digital Security Act 2018 repealed twice and replaced by the Cyber Security Ordinance 2025. Every component version re-verified against upstream release and end-of-life data on 13 August 2026. Technology cost model restated to a $690K–1,150K three-year TCO on 1,513 measured person-weeks.** |

---

## DOCUMENT APPROVALS

| Role | Name | Responsibility | Signature | Date |
|---|---|---|---|---|
| Chief Technology Officer | | Owns this document; approves every layer decision | | |
| Solution Architect | | Technical accuracy, standards conformance | | |
| Chief Financial Officer | | Approves all L6 commercial components (§9) | | |
| Operations Director | | Confirms operational fitness of the field stack | | |
| Head of Information Security | | Approves §14 security and compliance architecture | | |
| Data Protection Officer / CDO | | Approves §14.4 split-residency design | | |
| Implementation Partner — Technical Lead | | Confirms buildability and sizing | | |

---

## HOW THIS DOCUMENT DIFFERS FROM VERSION 1.0

Version 1.0 specified a technology stack for a programme that no longer exists. The programme it
described was eleven functional modules and six portals delivered in eighteen months against 405
requirements. The programme now specified is **sixty-seven modules and twelve portals delivered in
thirty-six months against 2,930 measured requirements**. Almost every quantitative statement in v1.0
is therefore wrong, and the qualitative architecture — while sound in its principles — was sized for
roughly one-fifth of the eventual system.

| Dimension | v1.0 | **v2.0** | Change |
|---|---|---|---|
| Delivery layers | 5 (L1–L5) | **6 (L1–L6)** | +1 — commercial SaaS admitted where no viable open source exists |
| Functional modules | 11 | **67** | +509% |
| Portals & applications | 6 | **12** | +100% |
| Requirements covered | 405 | **2,930 measured** *(+48 est. for two unwritten specs)* | +623% |
| Data entities | ~40 | **225** | +463% |
| External integrations | 31 | **47** | +52% |
| Non-functional requirements | 30 | **101** | +237% |
| User roles | 20 | **46** *(38 registered)* | +130% |
| Odoo CE modules deployed | 14 | **23** | +64% |
| OCA repositories | 11 | **18** | +64% |
| OCA modules | 94+ | **140+** | +49% |
| Standalone open-source systems | 10 | **24** | +140% |
| Custom development items | 20 modules | **248 CD items** *(restated — see §8.2)* | see §8.2 |
| Mobile applications | 1 (Flutter) | **4 (Flutter)** | +300% |
| Web applications | 2 (Next.js) | **6 (Next.js)** | +200% |
| Data residency model | Single region (Singapore) | **Split residency — Bangladesh-resident sensitive store + regional primary** | Architecture change |
| Data platform | PostgreSQL + Redis | **PostgreSQL 16 + TimescaleDB + ClickHouse + Redis + object storage** | +3 stores |
| Event architecture | Webhooks via n8n | **Transactional outbox → Redis Streams → Redpanda/Kafka, with a 70-event domain catalogue** | Architecture change |
| API surface | Odoo JSON-2 direct | **Kong gateway · 12 API families · OpenAPI 3.1 · BFF per portal** | Architecture change |
| Build effort | 80–115 PW | **1,513 PW measured** | +1,215% |
| 3-year TCO | $182K–342K | **$690K–1,150K** | +279% |
| Regulatory basis | ICT Act 2006, Digital Security Act 2018 | **ICT Act 2006, Cyber Security Ordinance 2025, Personal Data Protection Act 2026** | Corrected — DSA 2018 repealed twice |
| Programme duration | 18 months, 6 phases | **36 months, 9 waves** | +100% |

**Six changes are structural, not arithmetic.** They change how the system is built, not merely how
much of it there is:

1. **A sixth layer.** v1.0 asserted a zero-licence-cost stack absolutely. Four capabilities —
   carrier telephony, qualified e-signature, accredited identity verification, and enterprise patch
   orchestration — have no viable open-source equivalent. L6 is bounded, individually CFO-approved,
   and capped at **$0–36K over three years** against a $690K–1,150K programme.

2. **Split residency.** v1.0 placed everything in DigitalOcean Singapore. The Personal Data
   Protection Act 2026 restricts large-scale transfer of Sensitive Personally Identifiable Data —
   NID, passport, TIN, biometric templates, criminal-record checks. NFR-086 now requires those fields
   to sit in a **Bangladesh-resident store**, joined to the regional record by key. This is a change
   to the data model, not only to hosting, and it is the single largest architectural change in v2.0.

3. **An event platform, not webhooks.** v1.0 used n8n to fan out webhooks. At 67 modules the
   coupling that creates is unmanageable. v2.0 mandates a **transactional outbox** in the same
   database transaction as the state change, publication to Redis Streams to Wave 5 and to
   Redpanda/Kafka thereafter, and **idempotent consumers** — architecture standard AS-08.

4. **A real API gateway.** Six portals could call Odoo's JSON-2 API directly. Twelve portals with
   twelve distinct authorisation scopes, plus external partner consumption, cannot. Kong sits in
   front of everything, with a backend-for-frontend per portal.

5. **An analytical tier.** v1.0 ran BI off a PostgreSQL read replica. At 5 million service orders a
   year and 50,000 telemetry points a minute, the replica cannot serve both. v2.0 adds
   **TimescaleDB** for time series from Wave 2 and **ClickHouse** for the analytical warehouse from
   Wave 8.

6. **Custom development is enumerated, not estimated.** v1.0 listed 20 custom modules. The v2.0
   source register lists 138 CD items — but covering only 30 of the 67 modules. §8.2 completes that
   register to **248 items across all 67 modules**. This does **not** increase cost: the 1,513 PW is
   already measured from all 67 module specifications. It completes the deliverable breakdown that
   the effort figure already reflects.

---

## NOTATION AND CONVENTIONS

### Delivery layer codes

| Code | Layer | Licence position | Target share of requirements |
|---|---|---|---:|
| **L1** | Odoo 19 Community Edition, native | LGPL-3 — $0 | ~28% |
| **L2** | OCA community module | LGPL-3 / AGPL-3 — $0 | ~24% |
| **L3** | Free third-party Odoo module | Various — $0 | ~4% |
| **L4** | Standalone open-source system | Apache / MIT / BSD / AGPL — $0 | ~17% |
| **L5** | Custom development | Proprietary to 1000FiX — development cost only | ~25% |
| **L6** | Commercial SaaS or licensed component | Subscription — CFO approval required | ~2% |

The selection hierarchy is **mandatory** and is restated in §2.5. A capability is delivered at the
cheapest viable layer, and any classification at L5 or L6 where a lower layer would serve is a
defect.

### Component identifiers

| Prefix | Meaning | Example |
|---|---|---|
| `TC-nnn` | **Technology component** — a discrete, separately deployed or separately licensed piece of the stack, registered in Appendix A | TC-001 Odoo 19 CE |
| `CD-nnn` | **Custom development item** — a custom Odoo module, service, application or extension, registered in §8.2 | CD-009 `cd_dispatch` |
| `TD-nn` | **Technology decision** — a recorded, reasoned choice with the rejected alternative, registered in §24 | TD-01 Odoo 19 CE as ERP core |
| `TR-nn` | **Technology risk** — registered in §23 | TR-03 OCA v19 migration debt |
| `AS-nn` | **Architecture standard** — testable, CI-verified, contractually binding | AS-08 outbox event emission |
| `TSA-nn` | **Technology Stack audit finding** — registered in Appendix G | TSA-01 |

### Identifier spaces inherited from the specification set

| Prefix | Space | Owning register | Count |
|---|---|---|---:|
| `Mnn` | Module | `02-02` | 67 |
| `Pnn` | Portal / application | `04-00` | 12 |
| `FR-<CODE>-nnn` | Functional requirement | `05-01` + module files | 2,930 measured |
| `NFR-nnn` | Non-functional requirement | `05-06` | 101 |
| `INT-nnn` | External integration | `05-03` | 47 |
| `Rnn` | Role | `05-04` | 46 in use (38 registered) |
| `AUT-nnn` | Automation | `05-05` | 60 |
| `KPI-nnn` | Programme KPI | `06-02` | 95 |
| `Tn` | Data isolation tier | `05-04` | 6 (T0–T5) |
| `SOD-nn` | Segregation-of-duties control | `05-04` | 30 |
| `Wn` | Delivery wave | `06-01` | 9 |

### Coverage codes used in the mapping tables

| Code | Meaning |
|---|---|
| **N** | Delivered by **native** Odoo 19 CE capability (L1) with configuration only |
| **O** | Delivered by an **OCA** module (L2) |
| **T** | Delivered by a free **third-party** Odoo module (L3) |
| **S** | Delivered by a **standalone** open-source system (L4) |
| **C** | Delivered by **custom** development (L5) |
| **X** | Delivered by a commercial component (L6) |
| **∅** | **No technology assigned** — a coverage gap. Zero permitted; any occurrence is a defect |

These are the same codes respondents use in RFP Appendix A, deliberately, so that a respondent's
functional response can be diffed against this document line by line.

### Priority and wave

`P0` regulatory, safety or go-live blocking · `P1` core business capability · `P2` important,
deferrable one wave · `P3` desirable, opportunistic. Waves `W1`–`W9` span 36 months as fixed by
RFP §12.

### Figure basis marking

Under register rule **RG-06 — count, do not consult** — every figure describing what the
specification set *contains* is derived by direct enumeration at time of writing and carries the date
it was counted. Figures marked ***(est.)*** are extrapolations and, under **RG-05**, must not be used
for contractual commitment.

---

## TABLE OF CONTENTS

**PART A — FOUNDATION**

1. [Executive Summary](#1-executive-summary)
2. [Derivation, Coverage Method and Governing Rules](#2-derivation-coverage-method-and-governing-rules)
3. [System Architecture](#3-system-architecture)

**PART B — THE STACK, LAYER BY LAYER**

4. [Layer 1 — Odoo 19 Community Edition](#4-layer-1--odoo-19-community-edition)
5. [Layer 2 — The OCA Module Ecosystem](#5-layer-2--the-oca-module-ecosystem)
6. [Layer 3 — Free Third-Party Modules](#6-layer-3--free-third-party-modules)
7. [Layer 4 — Standalone Open-Source Systems](#7-layer-4--standalone-open-source-systems)
8. [Layer 5 — Custom Development](#8-layer-5--custom-development)
9. [Layer 6 — Commercial Components](#9-layer-6--commercial-components)

**PART C — COVERAGE**

10. [Module-to-Technology Coverage — All 67 Modules](#10-module-to-technology-coverage--all-67-modules)
11. [Portal & Application Technology — P01 to P12](#11-portal--application-technology--p01-to-p12)
12. [Cross-Cutting Platform Technology](#12-cross-cutting-platform-technology)
13. [Non-Functional Requirement Realisation](#13-non-functional-requirement-realisation)
14. [Security, Data Protection & Compliance Architecture](#14-security-data-protection--compliance-architecture)
15. [Localisation & Accessibility Technology](#15-localisation--accessibility-technology)
16. [Offline & Low-Connectivity Technology](#16-offline--low-connectivity-technology)
17. [Observability & Operations Technology](#17-observability--operations-technology)
18. [Environments, CI/CD & Engineering Practice](#18-environments-cicd--engineering-practice)
19. [Data Migration Technology](#19-data-migration-technology)

**PART D — DELIVERY & COMMERCIAL**

20. [Wave-by-Wave Technology Deployment](#20-wave-by-wave-technology-deployment)
21. [Infrastructure Sizing & Capacity](#21-infrastructure-sizing--capacity)
22. [Technology Cost Model](#22-technology-cost-model)
23. [Technology Risk Register](#23-technology-risk-register)
24. [Technology Decision Log](#24-technology-decision-log)

**PART E — DISCLOSURE & APPENDICES**

25. [Disclosed Open Items, Defects and Version-Currency Findings](#25-disclosed-open-items-defects-and-version-currency-findings)
26. [Appendices](#26-appendices)

---
---

# PART A — FOUNDATION

---

## 1. EXECUTIVE SUMMARY

### 1.1 Purpose

This document states, for every capability the 1000FiX ERP programme has committed to deliver,
**which specific technology delivers it, at which layer, under which licence, at which version, in
which wave, and at what cost.** It is the single technical reference that binds the business
documents to buildable components.

It serves four audiences with four different questions:

| Audience | Question this document answers |
|---|---|
| **Implementation partner** | What exactly do I deploy, configure, extend and build — and against what standards will it be accepted? |
| **Steering Committee & CFO** | What does the technology cost, what is licensed versus free, and where is the commercial exposure? |
| **Architecture Board & CTO** | Why this component and not the alternative, and what happens when the component changes underneath us? |
| **Quality assurance & audit** | Can every one of the 2,930 requirements, 101 NFRs, 47 integrations, 46 roles and 12 portals be traced to a named technology? |

The fourth question is the one this document is structured around. **§10 through §13 exist to make
the coverage claim verifiable rather than asserted**, and §26 Appendix G records the audit that
tested it.

### 1.2 The Coverage Claim

> **Every module, portal, functional requirement class, data entity, external integration,
> non-functional requirement, role, data isolation tier, segregation-of-duties control, business
> automation and user journey defined in the v2.0 specification set has an assigned technology
> realisation in this document. There are zero `∅` entries.**

This claim is bounded, and the bounds are stated rather than buried:

| Obligation set | Count | Where covered | Basis |
|---|---:|---|---|
| Functional modules | **67** | §10 | Complete — every module has a row |
| Portals & applications | **12** | §11 | Complete — every portal has a subsection |
| Functional requirements | **2,930 measured** | §10 at module level; §26 Appendix B at requirement-class level | **Module-level and class-level.** Individual requirement-by-requirement mapping is completed in Annex 1 by the implementation partner (RFP §6.1) — see the bound stated below |
| Data entities | **225** | §12.3 | Complete at entity-group level; per-entity DDL is a design artefact |
| External integrations | **47** | §12.2.4 | Complete — every INT-001…047 has a named client technology and a fallback |
| Non-functional requirements | **101** | §13 | Complete — every NFR has a realising technology and a verification method |
| User roles | **46** | §12.1.2 | Complete — including the 8 unregistered roles, disclosed |
| Data isolation tiers | **6 (T0–T5)** | §12.1.3 | Complete |
| Segregation-of-duties controls | **30** | §12.1.4 | Complete at mechanism level; 18 remain unregistered upstream — disclosed §25 |
| Business automations | **60 (AUT-001…060)** | §12.8 | Complete — every automation has an execution engine |
| Programme KPIs | **95** | §12.4.4 | Complete — instrumentation and surfacing technology assigned |
| Critical user journeys | **15** | §20.4 | Complete — each mapped to its end-to-end test harness |
| Custom development items | **248 restated** | §8.2 | Complete — extended from the 138-item, 30-module source register |

**The bound on requirement-level coverage, stated plainly.** This document maps technology to
requirements at the level of the **module and the requirement class** — for example, "all 74
FR-FSM requirements are delivered by OCA `field-service` extended by CD-009…CD-015, with routing at
L4 on VROOM/OSRM". It does **not** contain 2,930 individual rows. That mapping is produced by the
implementation partner in RFP Appendix A at individual requirement level and is a contractual
deliverable of the partner, not of this document. What this document guarantees is that **no
requirement class is left without an assigned technology**, so that the partner's requirement-level
response has a defined answer to map onto in every case. §26 Appendix B is the class-level matrix
that makes this checkable.

### 1.3 The Six-Layer Stack

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  L6  COMMERCIAL COMPONENTS                                    ~2% · $0–36K/3yr   │
│      Cloud telephony (CPaaS) · Qualified e-signature · KYC/identity verification │
│      Endpoint RMM agent (conditional, Wave 5 pilot decision)                     │
│      Every item individually CFO-approved with a written OSS alternative review  │
├──────────────────────────────────────────────────────────────────────────────────┤
│  L5  CUSTOM DEVELOPMENT — 248 CD items + 10 applications      ~25% of reqs       │
│      232 custom Odoo modules & extensions (cd_*)  ·  16 standalone services      │
│      4 Flutter applications (APP-01…04)  ·  6 Next.js applications (APP-05…10)   │
│      Bangladesh compliance · dispatch intelligence · marketplace settlement ·    │
│      offline sync · MSP platform · data-services custody · split-residency layer │
├──────────────────────────────────────────────────────────────────────────────────┤
│  L4  STANDALONE OPEN SOURCE — 24 systems                      ~17% · $0 licence  │
│      Keycloak · Kong · n8n · Novu · Redis · MinIO · PostgreSQL · PgBouncer ·     │
│      Nginx · Docker/K3s · Traccar · OSRM · VROOM · TimescaleDB · Grafana ·       │
│      OpenTelemetry/Prometheus/Loki/Tempo · Metabase · Mayan EDMS ·               │
│      MeshCentral/RustDesk · Wazuh/osquery · Redpanda/Kafka · MLflow · Ollama ·   │
│      ClickHouse                                                                  │
├──────────────────────────────────────────────────────────────────────────────────┤
│  L3  FREE THIRD-PARTY ODOO MODULES                            ~4%  · $0 licence  │
│      SSLCOMMERZ · bKash · Nagad · SMS gateway · WhatsApp connector · barcode     │
├──────────────────────────────────────────────────────────────────────────────────┤
│  L2  OCA COMMUNITY MODULES — 140+ across 18 repositories      ~24% · $0 licence  │
│      field-service (33) · helpdesk (28) · management-system (33) ·               │
│      operating-unit (15) · hr+payroll (50+) · account-financial-tools (40+) ·    │
│      stock-logistics-* (55+) · purchase-workflow (25+) · partner-contact (30+) · │
│      contract (12) · dms (5) · server-tools (30+) · web (40+) · l10n-bangladesh  │
├──────────────────────────────────────────────────────────────────────────────────┤
│  L1  ODOO 19 COMMUNITY EDITION — 23 modules deployed          ~28% · $0 licence  │
│      base · web · mail · contacts · crm · sale · sale_management · product ·     │
│      stock · purchase · account · hr · hr_attendance · hr_holidays · hr_expense ·│
│      project · calendar · fleet · website · portal · maintenance · repair ·      │
│      sale_renting                                        LGPL-3 · PostgreSQL 16  │
└──────────────────────────────────────────────────────────────────────────────────┘

Software licence cost for the ERP core: $0.  Total licence exposure: $0–36K over three years.
```

### 1.4 The Ten Decisions That Matter Most

Of the 27 recorded technology decisions in §24, ten determine whether this programme succeeds. They
are stated here because a reader who reads nothing else should read these.

| # | Decision | Why it is decisive |
|---|---|---|
| **1** | **Odoo 19 CE as the system of record** | $0 licence against $45–90K over three years for Enterprise; 52% of requirements met at L1+L2 without writing code; Bangladesh developer availability. The cost is disciplined extension practice — see decision 2 |
| **2** | **Extend, never fork** (AS-05) | 140+ OCA modules and 23 Odoo modules must survive an annual upgrade cycle across a 36-month build. A single fork of a core module converts every future upgrade into a merge exercise. This is enforced in CI, not by convention |
| **3** | **Split-residency data architecture** (NFR-086) | The Personal Data Protection Act 2026 makes single-region hosting non-compliant for NID, passport, TIN, biometric and recovered-data fields. This is a Wave 1 architecture decision with a **legal-opinion dependency (DEP-31) that is still open** |
| **4** | **Transactional outbox for every write path** (AS-08) | 67 modules cannot integrate by direct calls without becoming one indivisible system. The outbox in the same transaction is what makes events reliable rather than best-effort |
| **5** | **Flutter for all four field applications** | 24-hour offline with server-authoritative conflict resolution is the single hardest technical requirement in the programme. One codebase, one offline engine, one sync protocol across technician, rider, auditor and customer apps |
| **6** | **Next.js 15 + Payload CMS 3 portal platform is not replaceable** (CON-03) | A hard constraint, not a preference. The stack integrates with it through a versioned contract (§12.2.5); it does not absorb it. **Version currency requires attention — see §11.1 and §25** |
| **7** | **Build the marketplace and the settlement engine** | Commission and payout must post to the ledger. A SaaS marketplace cannot be the system of record for money the Company owes to 5,000 sellers |
| **8** | **Self-hosted LLM (Ollama) for conversational AI** | Customer conversation data must not leave the Company under PDPA transfer restrictions. Open-weight Bengali-capable models remove per-query cost at 250,000 customer interactions a month |
| **9** | **Bounded L6 with individual CFO approval** | Four components, $0–36K over three years, each with a written open-source alternative assessment reviewed annually. This is what prevents "zero licence cost" degrading into unbounded SaaS sprawl |
| **10** | **Odoo 19 is an LTS release with a finite life** | Odoo 19.0 released 18 September 2025; Odoo 20 is expected September–October 2026, one month after this document. A 36-month programme on an annually-versioned platform **must plan an in-flight major upgrade** — this is decision D-15, raised in §4.4 and §25 |

### 1.5 Technology Cost Summary

| Category | 3-year cost | Basis |
|---|---|---|
| **Software licensing — ERP core, L1–L5** | **$0** | LGPL-3, AGPL-3, Apache-2.0, MIT, BSD, PostgreSQL Licence |
| **Software licensing — L6 commercial** | **$0–36K** | 4 components, individually approved; RMM agent conditional on a Wave 5 pilot |
| Infrastructure / hosting (split residency) | $52K–96K | §21.3 — progresses $450–700/month (W1) to $4,000–5,800/month (W9), plus the Bangladesh-resident store |
| Third-party API consumption | $41K–95K | §22.3 — SMS, WhatsApp, maps, traffic, storage egress, identity checks |
| Implementation & custom development | **$525K–855K** | 1,513 measured person-weeks at approved unit rates |
| Training & change management | $35K–65K | 46 roles, Bengali and English |
| Support & maintenance (years 2–3) | $60K–130K | |
| *Component sum* | *$713K–1,277K* | |
| **HEADLINE 3-YEAR TCO** | **$690K–1,150K** | As fixed by RFP §16.1 |

> **The component sum and the headline do not match, and this is disclosed rather than smoothed.**
> The headline range is the Company's restated figure, derived by applying measured effort to
> approved unit rates. The component sum is wider at both ends because its lower bound assumes every
> line lands at best case simultaneously and its upper bound assumes every line lands at worst case
> simultaneously — neither is likely. This is the same reconciliation carried in RFP §16.1 and BRD
> §19.1, restated here so the technology cost model does not appear to contradict them.

**The most important cost fact in this document:** software licensing is between **0% and 3.1%** of
total cost of ownership. The programme's financial risk lives almost entirely in the **1,513
person-weeks of implementation**, not in what the software costs. Optimising the stack for further
licence savings would be optimising the wrong variable.

### 1.6 Compliance Position

Every component in this stack is selected to satisfy identified obligations from:

- **RFP v2.0** — the reference architecture (§5), 2,930 requirements (§6), 12 portals (§7),
  cross-cutting specifications (§8), 101 NFRs (§9), compliance obligations (§10), the 9-wave plan
  (§12) and the commercial envelope (§16).
- **BRD v2.0** — 18 business objectives, 11 business-rule domains, 60 automations, 95 KPIs, the
  benefit case, and the 46-role stakeholder model.
- **URD v2.0** — 255 user stories, 36 personas, 15 journeys, the offline contract (§20), the
  accessibility position (§21) and the localisation requirements (§22).

**Regulatory currency, verified 13 August 2026:**

| Statute | Status | Consequence for the stack |
|---|---|---|
| **Personal Data Protection Act 2026 (Law 63 of 2026)** | **In force**; enforcement mechanisms activate ~13 May 2027, inside Wave 4 | Split residency (§14.4), consent and transparency infrastructure (§14.3), data-subject rights tooling, breach notification to the National Data Management Authority |
| **Cyber Security Ordinance 2025** | **In force** (21 May 2025) | Replaces the Digital Security Act 2018 cited throughout v1.0 |
| Digital Security Act 2018 | **Repealed** — by the Cyber Security Act 2023, itself repealed by the 2025 Ordinance | **Every v1.0 reference to it is void** |
| ICT Act 2006 | In force | |
| VAT & Supplementary Duty Act 2012 | In force | Mushak 6.3 tax invoice, Mushak 9.1 monthly return via vat.gov.bd by the 15th (§14.6) |
| Bangladesh Labour Act 2006 (as amended) | In force | Payroll, working time, safety (§10 Category H) |

---

## 2. DERIVATION, COVERAGE METHOD AND GOVERNING RULES

### 2.1 How This Document Was Derived

This specification was produced by working forward from RFP v2.0 rather than by revising v1.0. The
method is recorded because the coverage claim in §1.2 depends on it.

| Step | Action | Output |
|---|---|---|
| 1 | Enumerate every obligation the RFP, BRD and URD place on technology | The 13-row obligation register in §1.2 |
| 2 | Enumerate the authoritative registers by direct file count (rule RG-06) | 67 modules · 12 portals · 2,930 requirements · 225 entities · 47 integrations · 101 NFRs · 46 roles · 60 automations · 95 KPIs |
| 3 | For each obligation, apply the L1→L6 selection hierarchy | A layer assignment and a named component |
| 4 | Register each named component with version, licence, wave and sizing | Appendix A — the complete component register |
| 5 | Verify every component's version, licence and support status against upstream sources | §25.2 version-currency findings |
| 6 | Test the coverage claim by re-enumeration, not by re-reading | Appendix G — audit record |

**Step 6 is the one that matters.** Under rule RG-06 a prior statement of a figure is not evidence
for that figure. Every count in this document was re-derived at time of writing, and the audit in
Appendix G re-derived them again independently. Where the two disagreed, the disagreement is
recorded as a finding, not silently reconciled.

### 2.2 What "100% Coverage" Means and Does Not Mean

The instruction governing this document is that all features, functions, modules and project
requirements be 100% covered by the technology stack. That is achievable and is achieved, but the
term needs a precise definition or it becomes unfalsifiable.

**Coverage means:** for every obligation in the register, this document names the technology that
delivers it, states the layer, and states how conformance is verified. A reader can take any module,
portal, integration, NFR, role or automation identifier and find its technology in this document.

**Coverage does not mean:**

| Not claimed | Why | Where it is actually delivered |
|---|---|---|
| That 2,930 individual requirements each have their own row here | A 2,930-row table is not a specification, it is a spreadsheet, and it would be stale within a sprint | Implementation partner's RFP Appendix A response, at requirement level, contractually |
| That every entity has its DDL | Physical schema is a design artefact produced per module | Module detailed design; §12.3 fixes the standards it must obey |
| That the technology is proven for 1000FiX's specific data | Selection is evidence-based, not yet evidence-tested at 1000FiX scale | Wave-gate performance testing at 1.5× expected peak (§18.6) |
| That no component will be replaced | A 36-month programme on an annually-versioned foundation will see component change | §24 records the decision and the rejected alternative so a future change is a re-decision, not a rediscovery |
| That M66 and M67 requirements are counted | Their specification files do not exist. 48 requirements are estimated | Disclosed §25.1; technology assigned on the registered module scope |

**One consequence worth stating.** Because two module specifications (M66 Internal IT Service
Management, M67 Project, Program & Portfolio Management) are unwritten, their technology assignment
in §10 is made against the **registered module scope** in `02-02`, not against enumerated
requirements. Those two rows are marked *(est.)* and, under rule RG-05, must not be used for
contractual commitment until the specifications exist.

### 2.3 The Selection Hierarchy — Mandatory

```
For every capability:

  1.  Can Odoo 19 CE deliver it natively, with configuration only?     → L1
  2.  Is there a production-grade OCA module, v19-migrated?            → L2
  3.  Is there a maintained free third-party Odoo module?              → L3
  4.  Is there a mature standalone open-source system?                 → L4
  5.  Must it be built?                                                → L5
  6.  Only if 1–5 all fail AND the CFO approves in writing             → L6

  At each step, "no" must be justified in writing, not assumed.
```

**Enforcement.** RFP §5.3 states that a respondent whose functional response places materially more
than 25% of requirements at L5 must justify each such classification, and that over-classification to
L5 is scored as either a capability gap or commercial inflation. This document holds itself to the
same standard: the L5 share here is **~25%**, matching the reference position, and §8 states for each
CD item why a lower layer does not serve.

**The reverse error is equally serious.** Classifying at L1 or L2 something that OCA does not
actually deliver produces a discovery in Wave 3 rather than a decision in Wave 0. §5.4 records the
v19 migration status of every OCA repository precisely because that is where this error would occur.

### 2.4 Governance Rules This Document Operates Under

Inherited from the authoritative register `02-02` §1 and binding on this document:

| Rule | Statement | How this document complies |
|---|---|---|
| **RG-01** Register-first (extended) | No identifier may be introduced in a shared space that does not exist in its owning register | New `TC-`, `CD-`, `TD-`, `TR-` identifiers are registered here, in Appendix A and §8.2, §24 and §23 respectively. This document introduces **no** new `FR-`, `NFR-`, `INT-`, `R`, `KPI-`, `AUT-` or `SOD-` identifiers |
| **RG-02** Permanent identity | Module IDs and codes are permanent; a retired code is never reused | All 67 module codes used here are taken verbatim from `02-02` §5 |
| **RG-03** Single owner | Every module has one business owner and one system owner | §10 carries the system-owner column |
| **RG-04** Boundary symmetry | If module A declares a capability out of scope and owned by B, B must claim it | Verified in the audit, Appendix G |
| **RG-05** Provisional figures | Figures marked *(est.)* must not be used for contractual commitment | Applied to M66, M67, and to the CD effort split in §8.2 |
| **RG-06** Count, do not consult | Any figure describing repository contents is derived by direct enumeration at time of writing; a prior statement is not evidence | Applied to every count in this document; the audit re-derived them independently |

### 2.5 Architecture Standards — Testable and Contractually Binding

These fifteen standards are reproduced verbatim from RFP §5.5 and `05-06` §12 because **they are the
acceptance conditions for everything this document specifies**. A component correctly selected but
integrated in violation of these standards has not been delivered.

| # | Standard | Verified by | Layer most at risk |
|---|---|---|---|
| **AS-01** | No module accesses another module's tables directly | Static analysis in CI; architecture review | L5 |
| **AS-02** | All custom models inherit `mail.thread` + `mail.activity.mixin` | Model registry check in CI | L5 |
| **AS-03** | All custom models carry `operating_unit_id` and `company_id` | Model registry check in CI | L5 |
| **AS-04** | All custom tables prefixed `fix_`; models prefixed `fix.` | Linter rule | L5 |
| **AS-05** | OCA modules extended via `_inherit`, never forked without architecture-board approval | Repository review | **L2 — the highest-risk standard in the stack** |
| **AS-06** | Every state machine is explicit, with transitions declared in one place | Code review checklist | L5 |
| **AS-07** | Every API is versioned (`/v1/`) and documented in OpenAPI 3.1 | CI validation against specification | L4, L5 |
| **AS-08** | Every write path emits a domain event via the transactional outbox | Event coverage test | L5 |
| **AS-09** | No business logic in views, controllers or portal code | Code review; portal contract test | L5 portals |
| **AS-10** | All money uses `Monetary` with explicit currency; no floats | Linter rule; financial test suite | L5 finance |
| **AS-11** | All timestamps stored UTC, presented Asia/Dhaka | Schema check | All |
| **AS-12** | All user-facing strings translatable; Bengali translation is a definition-of-done item | Translation coverage report at 100% | All |
| **AS-13** | Offline-capable apps use an append-only local journal with server-authoritative conflict resolution | Offline test suite | L5 mobile |
| **AS-14** | Personally identifiable and recovered customer data encrypted at field level | Security test suite | L5, data tier |
| **AS-15** | Every module ships with unit tests ≥ 80% and its KPI instrumentation | Definition-of-done gate | All |

**AS-05 deserves separate emphasis.** The stack depends on 140+ OCA modules across 18 repositories,
several of which are only partially migrated to v19. The temptation to fork rather than extend will
be strongest in exactly the repositories where migration is incomplete — `field-service` and
`helpdesk`. A fork taken in Wave 2 to save two weeks converts every subsequent OCA update and every
Odoo major upgrade into a manual merge for the remaining 34 months. This is registered as risk
**TR-03** and is the reason §5.5 sets an explicit fork policy with named approval.

---

## 3. SYSTEM ARCHITECTURE

### 3.1 Architectural Position

The system is a **layered, event-driven, API-first architecture** with Odoo 19 CE as the system of
record, a shared kernel of six modelled concepts, twelve experience surfaces, and a separate data and
intelligence tier.

```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│  EXPERIENCE LAYER — 12 portals and applications (P01–P12)                             │
│                                                                                       │
│   Next.js 15 (6 web apps)      Flutter (4 mobile apps)      Odoo Web OWL 2 (P03)     │
│   P01 · P04 · P07 · P08        P01-app · P02 · P09 · P11    Metabase/Grafana (P06)   │
│   P10 · P12                                                  Odoo Portal (P05)       │
└──────────────────────────────────────┬────────────────────────────────────────────────┘
                                       │ HTTPS · OAuth 2.0 / OIDC · per-portal credential
┌──────────────────────────────────────▼────────────────────────────────────────────────┐
│  EXPERIENCE API GATEWAY                                                               │
│  Kong Gateway 3.x  ·  OAuth2 introspection  ·  rate limiting  ·  versioning  ·        │
│  request tracing  ·  backend-for-frontend per portal  ·  12 API families              │
│  Keycloak 26.x — identity, SSO, MFA, step-up, per-client SAML/OIDC federation         │
└──────────────────────────────────────┬────────────────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼────────────────────────────────────────────────┐
│  SYSTEM OF RECORD — 1000FiX ERP v2.0                                                  │
│  Odoo 19 CE (23 modules) + OCA (140+ modules, 18 repos) + custom (248 CD items)       │
│  67 modules in 11 categories · 2,930 requirements · 225 entities                      │
│                                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│  │ SHARED KERNEL — party · product · location · legal entity · document · event    │  │
│  │ Modelled once. Changing a kernel concept requires architecture-board review.    │  │
│  └─────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                       │
│  DOMAIN SERVICES (L5, outside the Odoo process)                                       │
│  Dispatch scoring · Route orchestration (VROOM/OSRM) · Pricing engine ·                │
│  Settlement engine · ML inference gateway · Telemetry collector · RMM collector ·      │
│  Document generation · OCR · Notification dispatcher · Warehouse ETL · Reconciliation  │
└──────────────────────────────────────┬────────────────────────────────────────────────┘
                                       │ transactional outbox → event bus → idempotent consumers
┌──────────────────────────────────────▼────────────────────────────────────────────────┐
│  MESSAGING & AUTOMATION                                                               │
│  Redis Streams (W1–W5)  →  Redpanda / Kafka (W6+)   ·  n8n orchestration  ·           │
│  Novu notification routing  ·  70-event domain catalogue  ·  dead-letter + replay      │
└──────────────────────────────────────┬────────────────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼────────────────────────────────────────────────┐
│  DATA & INTELLIGENCE PLATFORM                                                          │
│  PostgreSQL 16 primary + 2 read replicas + PgBouncer   (OLTP, 225 entities)            │
│  ▸ Bangladesh-resident sensitive store  (NFR-086 split residency)                      │
│  TimescaleDB (GPS, telemetry, IoT)  ·  ClickHouse (analytical warehouse, W8)           │
│  Redis 7 (cache, sessions, locks)  ·  MinIO / object storage (documents, evidence)     │
│  MLflow (model registry)  ·  Ollama (LLM inference)  ·  Metabase + Grafana (BI)        │
└───────────────────────────────────────────────────────────────────────────────────────┘

OBSERVABILITY (cross-cutting):  OpenTelemetry → Prometheus + Loki + Tempo → Grafana
```

### 3.2 The Shared Kernel — Technology Realisation

Six concepts are modelled once. Every module consumes them; no module re-implements them. This is the
single most important structural decision in the data model, because it is what allows a marketplace
seller to also be a customer, and a corporate client to also be a referral partner, without duplicate
master records.

| Kernel concept | Odoo basis (L1) | OCA extension (L2) | Custom extension (L5) | Consumed by |
|---|---|---|---|---|
| **Party** — customer, employee, vendor, seller, partner, brand | `res.partner` | `OCA/partner-contact` (30+ modules) | `fix.party.role`, `fix.party.hierarchy`, `fix.identity.document` (CD-033…036) | All 67 modules |
| **Product & service catalogue** | `product.template`, `product.product` | `OCA/product-attribute` | `fix.catalogue.item`, service kits, rental SKUs, refurbishment grades (CD-048, CD-183…186) | M01, M11, M12, M13, M14, M15, M37 |
| **Location & geography** | `res.country`, `res.country.state`, `res.city` | `OCA/partner-contact` address tools | `fix.bd.address` — 8 divisions / 64 districts / upazilas / unions (CD-035); `fix.zone`, `fix.geofence` (CD-012) | M02, M03, M04, M12, M65 |
| **Legal entity & operating unit** | `res.company` | **`OCA/operating-unit` (15 modules)** | `fix.entity`, `fix.branch`, `fix.cost.center` (CD-133) | All — this is the multi-branch isolation mechanism |
| **Document & attachment** | `ir.attachment` | `OCA/dms` (5 modules) | `fix.document`, retention class, e-signature envelope (CD-107…109) | All; Mayan EDMS from W5 for volume |
| **Event** | — | — | **`fix.domain.event` — transactional outbox (CD-125)** | All — AS-08 makes this non-optional |

**A design rule that follows from this and is easy to violate.** A single party holds multiple roles
simultaneously. Respondents and implementers must not model seller, customer, vendor and partner as
separate master records joined by reference; they are one `res.partner` with multiple
`fix.party.role` records. Violating this produces exactly the duplicate-identity problem that the
programme exists to remove, and it is unrecoverable once transaction volume accrues against the
duplicates.

### 3.3 Runtime Topology — Production

```
┌── PRODUCTION — SPLIT RESIDENCY (NFR-086) ────────────────────────────────────────────┐
│                                                                                       │
│  EDGE          CDN · WAF (OWASP CRS) · DDoS mitigation · bot management               │
│                ─────────────────────────────────────────────────────────────          │
│  INGRESS       Kong Gateway 3.x + Nginx 1.27 · TLS 1.3 · OAuth2 introspection ·        │
│                per-consumer rate limits · request/response logging                    │
│                ─────────────────────────────────────────────────────────────          │
│  ┌──────────────┬──────────────────┬────────────────────┬─────────────────────────┐   │
│  │ ODOO 19 CE   │ NEXT.JS PLATFORM │ DOMAIN SERVICES    │ SUPPORTING SYSTEMS      │   │
│  │              │                  │                    │                         │   │
│  │ 4× app nodes │ P01 P04 P07 P08  │ Dispatch scoring   │ Keycloak (identity)     │   │
│  │ 12 workers ea│ P10 P12          │ Route orchestrator │ n8n (orchestration)     │   │
│  │ 2× cron nodes│ React 19         │ Pricing engine     │ Novu (notification)     │   │
│  │ 2× longpoll  │ Payload CMS 3    │ Settlement engine  │ Traccar (GPS)           │   │
│  │              │ (CON-03 — fixed) │ ML inference gw    │ VROOM + OSRM (routing)  │   │
│  │ 67 modules   │                  │ Telemetry collector│ Mayan EDMS (documents)  │   │
│  │ 248 CD items │                  │ RMM collector      │ MinIO (object storage)  │   │
│  │ 140+ OCA     │                  │ Doc generation     │ Metabase (BI)           │   │
│  │ 23 Odoo core │                  │ OCR · STT          │ Grafana (monitoring)    │   │
│  │              │                  │ Notification disp. │ MLflow · Ollama         │   │
│  │              │                  │ Warehouse ETL      │ Wazuh · MeshCentral     │   │
│  │              │                  │ Reconciliation     │                         │   │
│  └──────────────┴──────────────────┴────────────────────┴─────────────────────────┘   │
│                ─────────────────────────────────────────────────────────────          │
│  MESSAGING     Transactional outbox (in-transaction)                                  │
│                  → Redis Streams  (W1–W5, intra-system)                               │
│                  → Redpanda / Kafka  (W6+, inter-system, durable replay)              │
│                  → idempotent consumers · dead-letter queue · replay-from-timestamp    │
│                ─────────────────────────────────────────────────────────────          │
│  DATA          REGIONAL PRIMARY                    BANGLADESH-RESIDENT STORE          │
│                PostgreSQL 16 primary               PostgreSQL 16 (encrypted)          │
│                  + 2 read replicas                   NID · passport · TIN ·           │
│                  + PgBouncer (1,000 conns)           biometric templates ·            │
│                TimescaleDB (time series)             recovered customer data ·        │
│                ClickHouse (warehouse, W8)            seller KYC · criminal records    │
│                Redis 7 · MinIO object store        ── joined by resident key only ──  │
│                ─────────────────────────────────────────────────────────────          │
│  OBSERVABILITY OpenTelemetry → Prometheus + Loki + Tempo → Grafana                    │
│                Single correlation id across every hop (NFR-092)                       │
│                ─────────────────────────────────────────────────────────────          │
│  BACKUP        Hourly WAL · daily full (30 d) · weekly (1 y) · monthly (7 y)          │
│                AES-256 at rest · weekly automated restore verification (NFR-052)      │
│                ─────────────────────────────────────────────────────────────          │
│  DR            Warm standby · RPO ≤ 15 min · RTO ≤ 2 h · failover drill twice yearly  │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

**The split-residency boundary is a data-model boundary, not a network boundary.** A record about a
customer exists in the regional primary; the customer's NID number exists only in the
Bangladesh-resident store; the two are joined by a resident key. The sensitive field is **never
duplicated into the regional store, not even transiently, not even in a cache, not even in a log**.
This is enforced by field-level residency classification checked at write time (NFR-086a), not by
developer discipline. §14.4 states the mechanism.

### 3.4 Trust Zones and Network Segmentation

| Zone | Contents | Ingress | Egress | Controls |
|---|---|---|---|---|
| **Z0 Public edge** | CDN, WAF, DDoS | Internet | Z1 only | Rate limiting, bot management, geo-rules |
| **Z1 Ingress** | Kong, Nginx | Z0 | Z2, Z3 | TLS 1.3 termination, OAuth2 introspection, per-consumer quotas |
| **Z2 Application** | Odoo nodes, Next.js nodes, domain services | Z1 | Z3, Z4, Z6 | Service identity, mTLS between services, no direct internet egress except through Z6 |
| **Z3 Data — regional** | PostgreSQL, TimescaleDB, ClickHouse, Redis, MinIO | Z2 only | None | Private network only; no public endpoint; encryption at rest |
| **Z4 Data — Bangladesh resident** | Sensitive-data PostgreSQL store | Z2 via a dedicated residency service only | None | Separate key material; access logged per read; step-up authentication for human access |
| **Z5 Management** | CI/CD runners, bastion, Vault, observability | Restricted source ranges + MFA | Z2, Z3 | Privileged session recording (NFR-070); no standing access |
| **Z6 Egress** | Outbound proxy to third-party APIs | Z2 | Named allow-list only | Credential injection from Vault; every outbound call logged (IP-10) |

**Two rules that follow.** First, no application node reaches the internet except through Z6 with an
allow-listed destination — this is what makes IP-10 ("data leaving the Company is minimised and
logged") enforceable rather than aspirational. Second, Z4 is reachable only through a dedicated
residency service, so that the residency rule is implemented in exactly one place and can be audited
in exactly one place.

### 3.5 Environment Ladder

Six environments, all delivered and maintained by the implementation partner, as fixed by RFP §5.8.

| Environment | Purpose | Data | Refresh | Residency-classified data |
|---|---|---|---|---|
| `local` | Developer workstation, Docker Compose | Synthetic fixtures | On demand | **Never** — synthetic only |
| `dev` | Continuous integration target | Synthetic + anonymised sample | Every merge to `develop` | **Never** |
| `staging` | UAT, performance and security testing | Production clone, PII-masked | Weekly | **Never — masked** (NFR-071, NFR-086c) |
| `training` | Super-user and end-user training | Curated scenario data | Per training cycle | **Never** |
| `prod` | Live | Live | — | Yes, in Z4 only |
| `dr` | Warm standby | Streaming replica | Continuous | Yes, in a Bangladesh-resident standby |

**NFR-086c is absolute:** non-production environments never contain unmasked residency-classified
data in any region. Masking runs as part of the clone job, not as a subsequent step, so that an
unmasked clone cannot exist even briefly.

### 3.6 Data Flow — Four Critical Paths

The following four flows are shown because they exercise the parts of the architecture where the most
components interact, and because they are where an integration defect would be most costly.

#### 3.6.1 Service request to cash (M01 → M02 → M15 → M20 → M19)

```
Customer      P01 Portal      Kong        Odoo/M01      Outbox      Novu       P02 App
   │              │             │            │            │           │           │
   │─book────────►│             │            │            │           │           │
   │              │─POST /api/v1/service-orders (Idempotency-Key)     │           │
   │              │             │───────────►│            │           │           │
   │              │             │            │─create SO──┤           │           │
   │              │             │            │  + entitlement check (M08)         │
   │              │             │            │  + SLA assignment (M01)            │
   │              │             │            │─event: service_order.created──────►│
   │              │◄─201 + tracking token────│            │           │           │
   │◄─confirmation│             │            │            │           │─SMS──────►│ customer
   │              │             │            │            │           │           │
   │              │      Dispatch scoring service (L5) ◄──event──────┤           │
   │              │             │  candidate scoring · skill · certification ·    │
   │              │             │  van stock · zone · SLA risk · VROOM route      │
   │              │             │            │◄─assignment────────────┤           │
   │              │             │            │─event: work_order.assigned────────►│─push─►│
   │              │             │            │            │           │           │
   │              │             │            │            │      [technician works offline]
   │              │             │            │◄──sync: append-only journal, idempotent────┤
   │              │             │            │─parts consumed (M15) · time · evidence     │
   │              │             │            │─event: work_order.completed───────►│
   │              │             │            │─QC pass (M23) → invoice (M20) ≤ 5 s (NFR-040)
   │              │             │            │─event: invoice.created────────────►│─link─►│ customer
   │─pay bKash───►│─POST /api/v1/payments/confirm──────►│            │           │
   │              │             │            │─post to GL (M19) · Mushak 6.3 (M51)│
   │              │             │            │─event: invoice.paid───────────────►│─receipt►│
```

**Where this flow is fragile.** Three points: the idempotency key on order creation (a retried POST
must not create two orders); the offline sync reconciliation (a technician's queued actions must
apply exactly once); and the invoice-to-GL posting (which must be atomic with the Mushak register
write, or the VAT return will not reconcile). All three are covered by DI-04, DI-05 and AS-08.

#### 3.6.2 GPS to live customer ETA (M02 · Traccar · TimescaleDB · P01)

```
P02 App (Flutter)   Traccar 6.x     TimescaleDB     Odoo/M02      Kong      P01 Portal
      │                  │               │              │           │           │
      │─position (30 s)─►│               │              │           │           │
      │                  │─write─────────►│ hypertable, compressed  │           │
      │                  │─REST update──────────────────►│           │           │
      │                  │               │              │─ETA calc (OSRM)       │
      │                  │               │              │─event: technician.location_updated
      │                  │               │              │   (throttled)         │
      │                  │               │              │───────────►│──webhook─►│
      │                  │               │              │           │           │─map + ETA─► customer
      │                  │               │              │◄─GET /api/v1/technicians/{id}/location
      │                  │               │              │      (polling fallback if webhook fails)
```

**Sizing consequence.** 400 technicians at 30-second intervals is 800 positions per minute sustained
(NFR-056), 1.15 million per day, ~420 million per year. This is why GPS does not live in the primary
OLTP database: at that volume it would dominate the transaction log and degrade every other write.
TimescaleDB with native compression is TD-13, and it uses the same engine and the same operational
skill set as PostgreSQL, which is the reason it was chosen over InfluxDB.

#### 3.6.3 Warranty claim to reimbursement (M09 · P08 · M20 · M19)

```
P02 App        Odoo/M09           n8n           P08 Brand Portal      M20/M19
   │              │                 │                   │                 │
   │─warranty job complete + evidence pack              │                 │
   │─────────────►│                 │                   │                 │
   │              │─auto-validate warranty status (M17 device registry)   │
   │              │─auto-create claim ≤ 24 h (AUT-018)  │                 │
   │              │─assemble pack: photos, diagnostic, parts, serial,     │
   │              │  technician certification (M22), purchase proof       │
   │              │─completeness check — blocks submission if incomplete  │
   │              │─event: warranty_claim.created──────►│                 │
   │              │                 │─format per brand template (17+ brands)
   │              │                 │─submit───────────►│                 │
   │              │                 │                   │─brand decides   │
   │              │◄────────────────┤◄──status webhook──┤                 │
   │              │─update claim · on approval queue for billing──────────►│
   │              │─on remittance: match, post to ledger, flag unmatched  │
```

**Why n8n and not custom code here.** Seventeen-plus brand partners each require a different
submission format and a different portal. That is exactly the workload an orchestration tool is for:
the transformation is configuration that changes when a brand changes its template, not code that
requires a release. The claim record, the evidence pack and the reconciliation stay in Odoo, where
the ledger is.

#### 3.6.4 PDPA data-subject request (M33 · M29 · split residency)

```
Customer     P01 Portal      M33 Consent      Residency Service      Z4 Resident Store
   │             │                │                    │                     │
   │─request access / erasure────►│                    │                     │
   │             │                │─identity verification (step-up, NFR-065) │
   │             │                │─assemble regional record                 │
   │             │                │─request resident fields───►│             │
   │             │                │                    │─read, log access───►│
   │             │                │◄───────────────────┤             │
   │             │                │─assemble portable export (machine-readable)
   │             │◄───────────────┤                    │                     │
   │◄─export / confirmation       │                    │                     │
   │             │                │─on erasure: purge both stores in one saga,
   │             │                │  retain the statutory processing record (NFR-095)
   │             │                │─notify controller-side consumers within 30 days (NFR-093)
```

**The hard part is not the export, it is the erasure.** An erasure must remove the personal data from
the regional primary, the resident store, every read replica, the warehouse, the object store, the
search index and the backups-in-scope, while **preserving** the processing record that NFR-095
requires be kept for five years. This is a saga with compensating actions, not a `DELETE`. It is
CD-036 and CD-233, and it is P0 because enforcement activates ~13 May 2027, inside Wave 4.

---
---

# PART B — THE STACK, LAYER BY LAYER

---

## 4. LAYER 1 — ODOO 19 COMMUNITY EDITION

### 4.1 Platform Specification

| Attribute | Specification | Verified |
|---|---|---|
| **Product** | Odoo Community Edition | — |
| **Version** | **19.0**, released **18 September 2025** at Odoo Experience, Brussels; patched to the current 19.x | 13 Aug 2026 |
| **Release class** | **Long-Term Support (LTS)** | 13 Aug 2026 |
| **Licence** | LGPL v3 — **$0** | 13 Aug 2026 |
| **Runtime** | Python 3.12+ | |
| **Database** | PostgreSQL 16 (see §25.2 on version currency) | |
| **Frontend framework** | OWL 2 — TypeScript component framework | |
| **Primary API** | **JSON-2** — RESTful, token-authenticated, introduced in v19 | |
| **Legacy APIs** | JSON-RPC (maintained); XML-RPC (deprecated, not used) | |
| **Internationalisation** | Full i18n with `.po` translation files; Bengali (`bn_BD`) | |
| **Multi-currency** | Native; BDT primary, USD secondary | |
| **Source access** | Full — forkable, modifiable, redistributable under LGPL-3 | |
| **Ecosystem** | 15M+ downloads; active OCA ecosystem across 200+ repositories | |
| **Support horizon** | Odoo supports each major version approximately three years; **19.0 support runs to approximately September 2028** | 13 Aug 2026 |

> **Correction to v1.0.** The v1.0 specification stated Odoo 19 was "Released October 2025" and
> referred to a "Patch 19.1 (January 2026)". The release date is **18 September 2025**. This
> correction was first raised as audit finding C-04 against `02-05` and is carried here.

### 4.2 Odoo Modules Deployed — 23

| # | Module | Function | Categories served | Wave |
|---|---|---|---|:--:|
| 1 | `base` | Platform foundation, users, companies, security primitives | All | W1 |
| 2 | `web` | OWL 2 web client, the surface for P03 | K, all | W1 |
| 3 | `mail` | Chatter, activities, message threading, inbound parsing | All (AS-02) | W1 |
| 4 | `contacts` | Party master foundation | B, kernel | W1 |
| 5 | `product` | Catalogue foundation | C, E | W1 |
| 6 | `project` | Task tracking for complex and multi-visit work | A, K | W1 |
| 7 | `calendar` | Scheduling foundation | A, H | W1 |
| 8 | `repair` | Repair order foundation — **extended heavily** by M01, M31 | A | W1 |
| 9 | `crm` | Lead and opportunity management | B | W1 |
| 10 | `stock` | Multi-warehouse inventory, moves, valuation, reorder rules | E, A | W2 |
| 11 | `sale` | Quotations, sales orders | C | W3 |
| 12 | `sale_management` | Sales workflow, order lines, upsell | C | W3 |
| 13 | `purchase` | Requisitions, purchase orders, receipts, three-way match | E | W3 |
| 14 | `account` | GL, AR, AP, tax engine, banking, reconciliation | G | W3 |
| 15 | `fleet` | Vehicle master, assignment, cost tracking | F | W3 |
| 16 | `website` | Portal framework foundation | K (P05) | W3 |
| 17 | `portal` | External-user portal surface with record rules | K (P05) | W3 |
| 18 | `hr` | Employee master, org hierarchy, departments, skills | H | W5 |
| 19 | `hr_attendance` | Check-in/out, attendance records | H | W5 |
| 20 | `hr_holidays` | Leave types, requests, approvals, balances | H | W5 |
| 21 | `hr_expense` | Employee expense claim and reimbursement | G, H | W5 |
| 22 | `maintenance` | Equipment maintenance foundation | F | W5 |
| 23 | `sale_renting` | Rental foundation — **extended** by M13 | D | W6 |

**Count verified 13 August 2026 by enumeration against RFP §5.4.1 — 23 modules.**

### 4.3 What Odoo 19 CE Delivers Natively — By Category

This table answers the question "what do we get for free before writing anything", and it is the
basis of the ~28% L1 share.

| Category | Native Odoo coverage | What Odoo does **not** cover — escalates to L2/L4/L5 |
|---|---|---|
| **A** Service Delivery & Operations | `repair` order lifecycle; `project` task tracking; `calendar` scheduling; `stock` parts issue | Field service dispatch, SLA engine, offline execution, workshop bench management, custody chain, remote support, data-services custody |
| **B** Customer Engagement | `crm` pipeline; `contacts` party master; `mail` threading and inbound parsing | Party role model, loyalty engine, omnichannel contact centre, conversational AI, complaint/CAPA linkage, campaign management |
| **C** Commercial, Pricing & Revenue | `sale` quotation and order; `product` catalogue; native pricelists | Contract lifecycle, warranty claim automation, dynamic pricing, marketplace, tender management, subscription proration, settlement |
| **D** Circular & Asset-Based | `sale_renting` rental base; `stock` for refurbished goods | Condition reporting, grading, trade-in valuation, e-waste chain of custody, disposal certification |
| **E** Supply Chain & Inventory | `stock` multi-warehouse, valuation, reorder; `purchase` PO and three-way match | Van stock, consignment stock, cycle counting at branch scale, WMS bin logic, demand forecasting, landed cost with Bangladesh import duty |
| **F** Asset, Equipment & Facilities | `maintenance` foundation; `fleet` vehicle master | Customer asset registry at 5M scale, test-equipment calibration, facility management, IoT telemetry, predictive maintenance |
| **G** Finance & Treasury | `account` double-entry GL, AR, AP, tax engine, bank reconciliation, multi-currency | **Mushak 6.3 / 9.1**, Bangladesh TDS, BEFTN, revenue recognition, commission settlement, cost accounting to business line, FP&A |
| **H** People & Workforce | `hr`, `hr_attendance`, `hr_holidays`, `hr_expense` | **Bangladesh payroll in full** — tax slabs, provident fund, gratuity, Labour Act artefacts; shift rostering; competency-gated dispatch; incentive calculation; HSE |
| **I** Governance, Risk, Quality | `mail` audit thread; `ir.attachment` | ISO 9001/27001 management system, NCR/CAPA, e-signature, retention enforcement, knowledge management |
| **J** Data, Analytics & Intelligence | Native list/pivot/graph views | Warehouse, semantic layer, ML operations, self-hosted LLM, process automation orchestration |
| **K** Platform & Technology | `base` access control, record rules; JSON-2 API | Federated identity, API gateway, event platform, MDM, multi-entity localisation, feature flags, ITSM, PPM |

**The pattern is consistent and worth naming.** Odoo natively covers the *transaction* in each domain
and does not cover the *industry specialisation*, the *Bangladesh statutory obligation*, or the
*operational scale*. That is precisely the shape the layer model expects, and it is why L1 sits at
28% rather than the 40% v1.0 claimed against a much smaller requirement set.

### 4.4 Version Strategy — and the Odoo 20 Question

**This is decision D-15 and it is open.**

| Fact | Verified 13 August 2026 |
|---|---|
| Odoo 19.0 released | 18 September 2025 |
| Odoo 19.0 release class | LTS |
| Odoo support horizon per major version | ~3 years → **19.0 to approximately September 2028** |
| Odoo release cadence | Annual, at Odoo Experience |
| **Odoo 20 expected** | **September–October 2026** — Odoo Experience 2026 is 24–26 September 2026, with general availability typically 2–4 weeks after |
| Programme duration | **36 months** — Wave 1 start to Wave 9 completion |

**The arithmetic is unavoidable.** A 36-month programme beginning now on Odoo 19.0 will still be in
delivery when Odoo 21 ships and will reach steady state within roughly a year of 19.0 leaving
support. Three options exist and the Steering Committee must choose one:

| Option | Description | Consequence |
|---|---|---|
| **A — Baseline on 19.0, upgrade once mid-programme** | Build Waves 1–5 on 19.0; upgrade to 20.0 or 21.0 in a dedicated slot between Wave 5 and Wave 6 | ~8–14 PW of upgrade and regression effort, plus OCA module re-migration. Predictable, schedulable. **Recommended** |
| **B — Baseline on 19.0, upgrade after Wave 9** | Complete the whole build on 19.0, upgrade in year 4 | Programme finishes on a version within a year of end-of-support. Upgrade cost is higher because 248 CD items must be migrated at once rather than at half that count |
| **C — Track the annual release** | Upgrade each year as Odoo ships | Rejected. Three major upgrades inside a build programme, each requiring full OCA re-migration and full regression across 67 modules |

**Recommendation: Option A**, with the upgrade slot placed between Wave 5 and Wave 6 — after the
finance and people modules are stable and before the new business lines begin. The slot must be in
the baselined plan, not absorbed as contingency. **This is not currently in RFP §12's wave plan and
is raised as a change in §25.3.**

**What makes Option A affordable is AS-05.** If OCA modules are extended rather than forked and
custom modules use inheritance rather than core modification, the upgrade is a re-test exercise. If
they are not, it is a re-write. The two options differ by roughly an order of magnitude in cost, and
the decision that determines which one applies is taken in Wave 1, not at upgrade time.

### 4.5 Bangladesh Localisation — What `l10n_bd` Gives and What It Does Not

#### 4.5.1 Available at L1/L2

| Feature | Status | Requirement |
|---|---|---|
| Bangladesh chart of accounts | Available (`l10n_bd`, `OCA/l10n-bangladesh`) | M19 |
| VAT rate structure (15% standard) | Available | NFR-021, M51 |
| BDT currency (৳) with two decimals | Available | NFR — localisation |
| Bengali base translation | Partial — incomplete for v19; completion is a project task | AS-12, NFR-016 |
| Fiscal year July–June | Configurable | M19 |

#### 4.5.2 Gaps requiring L5 — the Bangladesh compliance pack

| Gap | Why Odoo cannot do it | CD item | Module | Wave |
|---|---|---|---|:--:|
| **Mushak 6.3 tax invoice** | NBR-prescribed format, BIN presentation, sequence rules, signature and 5-year preservation | CD-083 `cd_mushak` | M51 | W4 |
| **Mushak 9.1 monthly VAT return** | Return assembly and submission to vat.gov.bd by the 15th (NFR-100) | CD-084 `cd_vat_register` | M51 | W4 |
| **Input VAT credit control** | Credit claimable only against a valid compliant Mushak 6.3; the system must **block** claims without one (NFR-101) | CD-084 | M51 | W4 |
| **NBR income tax slabs** | Bangladesh-specific progressive computation with investment rebate | CD-198 `cd_tax_slab_bd` | M56 | W5 |
| **TDS / withholding** | Section-wise deduction at source with certificate generation | CD-085 `cd_tds` | M51 | W4 |
| **Provident fund & gratuity** | Labour Act-prescribed accrual and settlement | CD-199 `cd_pf_gratuity` | M56 | W5 |
| **BEFTN salary and vendor file** | Bangladesh bank transfer file format | CD-100 `cd_beftn` | M56, M50 | W5 |
| **NID validation** | 10-digit and 17-digit formats, checksum, residency classification | CD-086 `cd_nid` | M33 | W1 |
| **Bangladesh address hierarchy** | 8 divisions → 64 districts → upazilas/thanas → unions/wards → postcode | CD-035 `cd_bd_address` | M33, M65 | W1 |
| **Lakh/crore number grouping** | 12,34,567 grouping in the Bengali locale | CD-136 `cd_locale_pack` | M65 | W1 |
| **Bangladesh public holidays** | Including moon-dependent dates that shift annually | CD-136 | M65, M55 | W1 |
| **Mobile operator validation** | +880 number validation by operator prefix | CD-035 | M33 | W1 |

> **A note on e-invoicing.** The National Board of Revenue has progressively rolled out Electronic
> Fiscal Devices and Sales Data Controllers for retail and service businesses, and both physical and
> digital Mushak 6.3 copies are acceptable, with the supplier-signed original carrying the greatest
> evidentiary weight. The stack must therefore produce a **compliant, signable, preservable** Mushak
> 6.3 and support electronic submission of the 9.1 return, while not assuming a fully electronic
> invoice-clearance regime that is not yet mandatory. CD-083 is specified to accommodate a future
> clearance model without redesign — the invoice record carries the fields a clearance API would
> require, whether or not one is called. **Verified 13 August 2026; NBR requirements should be
> re-verified at Wave 4 gate under DoD-17.**

### 4.6 Extension Rules for Layer 1

| # | Rule | Rationale |
|---|---|---|
| L1-01 | Odoo core is **never modified**. Extension is by `_inherit`, `_inherits` or new model | Upgradeability; LGPL-3 obligations remain clean |
| L1-02 | Every custom model is prefixed `fix.`; every custom table `fix_` (AS-04) | Instant identification of custom surface at upgrade time |
| L1-03 | Every custom business model inherits `mail.thread` and `mail.activity.mixin` (AS-02) | Uniform audit thread and activity model across 67 modules |
| L1-04 | Every custom transactional model carries `company_id` and `operating_unit_id` (AS-03) | Multi-branch isolation is structural, not conditional |
| L1-05 | Money uses `Monetary` with explicit `currency_id`; floats are forbidden in money paths (AS-10, DI-01) | Financial correctness; VAT rounding |
| L1-06 | Odoo is pinned as a submodule at a specific commit; upgrades are deliberate | Reproducible builds |
| L1-07 | No business logic in Odoo controllers or website templates (AS-09) | Portals must be surfaces, not rule engines |

---

## 5. LAYER 2 — THE OCA MODULE ECOSYSTEM

### 5.1 Why OCA Is Load-Bearing

The Odoo Community Association maintains 200+ repositories under enterprise-grade quality controls.
For this programme OCA is not a convenience — it is **the replacement for the Odoo Enterprise modules
the Company is not buying**. `OCA/field-service` substitutes for Enterprise Field Service;
`OCA/helpdesk` for Enterprise Helpdesk; `OCA/management-system` for a quality management product that
would otherwise be a separate purchase. Together they carry **~24% of all requirements at zero
licence cost**.

| Quality control | What it means in practice |
|---|---|
| Mandatory peer review | Every module reviewed by two or more OCA maintainers before merge |
| CI on every pull request | Automated tests run against the target Odoo version |
| Coding standards | OCA guidelines, PEP 8, Odoo style, security checks enforced |
| Maturity rating | Alpha → Beta → Production/Stable, declared per module |
| Licence compliance | LGPL-3 or AGPL-3 throughout — compatible with Odoo CE |
| Documentation | README with installation, configuration and usage per module |
| Version migration | Community-driven migration to each new Odoo major version |

**Selection criterion, binding:** only modules rated **Production/Stable or Beta** with **confirmed
v19 migration**, or with **active migration commits in the last six months**, are deployed. Every
module is tested in `staging` before production. A module that fails this test is either migrated by
the implementation partner and contributed back (§5.5), or its capability is reclassified to L5 with
the effort added to the wave.

### 5.2 Repository Register — 18 Repositories, 140+ Modules

| # | Repository | Modules used | Modules served | v19 migration status | Risk | Wave |
|---|---|---:|---|---|:--:|:--:|
| 1 | **`OCA/field-service`** | **33** | M01, M02, M03, M31 | **~25 of 33 migrated** | **M** | W1–W2 |
| 2 | **`OCA/helpdesk`** | **28** | M01, M05, M27, M34 | **~20 of 28 migrated** | **M** | W1 |
| 3 | `OCA/management-system` | 33 | M23, M60 | ~28 of 33 | L | W5 |
| 4 | **`OCA/operating-unit`** | **15** | **All 67 modules** | ~12 of 15 | L | **W1** |
| 5 | `OCA/hr` + `OCA/payroll` | 50+ | M21, M22, M55, M56, M57, M58 | ~40 of 50+ | L | W5 |
| 6 | `OCA/account-financial-tools` | 40+ | M19, M49, M52 | Mostly migrated | L | W3 |
| 7 | `OCA/account-financial-reporting` | 20+ | M19, M25, M54 | Mostly migrated | L | W3 |
| 8 | `OCA/reporting-engine` + `OCA/mis-builder` | 20+ | M19, M25, M54 | Mostly migrated | L | W4 |
| 9 | `OCA/stock-logistics-workflow` | 25+ | M15, M41 | Mostly migrated | L | W2 |
| 10 | `OCA/stock-logistics-barcode` | 10 | M15, M02, M41 | Mostly migrated | L | W2 |
| 11 | `OCA/stock-logistics-warehouse` | 20+ | M15, M41 | Mostly migrated | L | W3 |
| 12 | `OCA/purchase-workflow` | 25+ | M16, M42 | Mostly migrated | L | W3 |
| 13 | `OCA/partner-contact` | 30+ | M07, M33 | Mostly migrated | L | W1 |
| 14 | `OCA/contract` | 12 | M08, M39 | Mostly migrated | L | W4 |
| 15 | `OCA/dms` | 5 | M24 | Mostly migrated | L | W3 |
| 16 | `OCA/server-tools` | 30+ | M29, M30, M64 | Mostly migrated | L | W1 |
| 17 | `OCA/web` | 40+ | UI enhancements, Keycloak auth bridge | Mostly migrated | L | W1 |
| 18 | `OCA/l10n-bangladesh` | 2 | M19, M51 | Mostly migrated | L | W3 |

**Register verified 13 August 2026 against RFP §5.4.2 — 18 repositories.**

### 5.3 The Six Repositories That Carry Material Load

#### 5.3.1 `OCA/field-service` — 33 modules · the Enterprise FSM replacement

This is the **single most load-bearing OCA dependency in the programme**. It is the foundation of
M01, M02, M03 and M31 — 202 measured requirements and roughly 138 person-weeks.

| Module | Function | Modules served |
|---|---|---|
| `fieldservice` | Core: work orders, locations, workers, scheduling | M01, M02 |
| `fieldservice_repair` | Odoo `repair` integration | M01, M31 |
| `fieldservice_equipment` | Equipment and device registry | M17 |
| `fieldservice_equipment_warranty` | Per-device warranty tracking | M09, M17 |
| `fieldservice_route` | Route planning base — extended by VROOM/OSRM at L4 | M02 |
| `fieldservice_skill` | Technician skill and certification | M02, M22 |
| `fieldservice_agreement` | Service agreements (AMC / RAMC) | M08 |
| `fieldservice_recurring` | Recurring service orders, preventive schedules | M08 |
| `fieldservice_stock` | Parts consumption against work orders | M15 |
| `fieldservice_vehicle` / `fieldservice_fleet` | Van and vehicle linkage | M46 |
| `fieldservice_substatus` | Configurable sub-statuses per workflow | M01 |
| `fieldservice_timeline` / `fieldservice_calendar` | Visual dispatch scheduling | M02, P03 |
| `fieldservice_stage_validation` | Stage-gated validation — QC checklist enforcement | M23 |
| `fieldservice_geoengine` | GIS zone mapping | M02 |
| `fieldservice_distribution` | Distribution and delivery management | M03 |
| `fieldservice_crm` / `fieldservice_sale` / `fieldservice_account` / `fieldservice_purchase` | CRM, sales, accounting and procurement integration | M07, M11, M20, M16 |
| `fieldservice_quality_control` | Quality checks on field orders | M23 |
| `fieldservice_template` | Service order templates | M01 |
| `fieldservice_change_management` | Change order tracking and approval | M01 |
| `fieldservice_partner_multi_relation` | Multi-contact corporate accounts | M07 |
| `fieldservice_activity` | Activity tracking per work order | M01 |
| `fieldservice_size` | Territory sizing | M02 |
| `fieldservice_maintenance` | Maintenance schedule management | M45 |
| `fieldservice_google_map` + marker icon picker | Map display and custom markers | M02, P03 |
| *(remaining modules deployed as required)* | | |

**Risk position.** Roughly 8 of 33 modules are not yet v19-migrated. Those 8 sit on the critical
path for Wave 2. Mitigation is in §5.4.

#### 5.3.2 `OCA/helpdesk` — 28 modules · ticketing and SLA

Serves M01 (service request intake), M05 (MSP incident management), M27 (contact centre) and M34
(complaint handling). `helpdesk_mgmt` provides ticket lifecycle; `helpdesk_mgmt_sla` provides SLA
tracking with breach alerting, which is the base for the M01 SLA engine extended by CD-005.

**Risk position.** ~20 of 28 migrated. The core (`helpdesk_mgmt`, `helpdesk_mgmt_sla`) is migrated;
the gap is in peripheral modules that can be deferred or replaced.

#### 5.3.3 `OCA/operating-unit` — 15 modules · the isolation mechanism

**This repository is used by all 67 modules and is the technical basis of branch-level data
isolation (NFR-015), the T1–T3 isolation tiers, and the multi-branch reporting model.** Every custom
model carries `operating_unit_id` under AS-03 precisely so that this repository's record rules apply
uniformly.

It is deployed in **Wave 1** and cannot be deferred: retrofitting operating-unit isolation after
transaction volume exists across 51+ branches is a data migration, not a configuration change.

#### 5.3.4 `OCA/hr` + `OCA/payroll` — 50+ modules

Provides the payroll rule engine, contract types, salary structures and payslip mechanics that
Bangladesh-specific rules (CD-198, CD-199, CD-100) are then written against. The distinction matters:
**OCA provides the payroll *engine*; the Bangladesh statutory content is L5.** Attempting to source
Bangladesh tax slabs and gratuity rules from OCA would fail — they do not exist there.

#### 5.3.5 `OCA/account-financial-*` + `mis-builder` — 80+ modules

Financial controls, asset management, financial reporting and the MIS report builder that produces
management reporting without a BI round trip. `mis-builder` is what allows a finance user to build a
management report against the ledger directly, which is why M54 FP&A does not require a separate
planning tool.

#### 5.3.6 `OCA/server-tools` — 30+ modules

Provides `auditlog` (the base for the immutable audit trail, NFR-014), technical utilities, and
base automation. Deployed W1 because the audit trail must exist before the first transaction does.

### 5.4 The v19 Migration Plan

Two repositories carry medium risk, both on the Wave 1–2 critical path. This is registered as risk
**TR-03**.

| Repository | Gap | Plan | Effort | Owner | Gate |
|---|---|---|---|---|---|
| `OCA/field-service` | ~8 of 33 modules not v19-migrated | Assess each of the 8 in Wave 0. For each: migrate and contribute upstream, or confirm the capability is not needed, or reclassify to L5 with effort added | **12–20 PW** *(est.)* | Implementation partner | **Wave 1 gate — no Wave 2 start until closed** |
| `OCA/helpdesk` | ~8 of 28 not migrated | Core is migrated. Assess the 8 peripheral modules; most are deferrable | **4–8 PW** *(est.)* | Implementation partner | Wave 1 gate |
| `OCA/operating-unit` | ~3 of 15 not migrated | Assess in Wave 0 — this repository cannot be partially deployed | **2–4 PW** *(est.)* | Implementation partner | **Wave 1 gate — blocking** |
| All others | Mostly migrated | Standard staging test before deployment | Absorbed | Implementation partner | Per wave |

**Wave 0 is where this is done, not Wave 2.** The migration assessment is a pre-build activity with a
named deliverable: a per-module status matrix for all 140+ modules, produced before Wave 1
architecture is fixed. A programme that discovers in Wave 2 that eight `field-service` modules do not
run has already lost the wave.

### 5.5 Fork Policy — AS-05 Made Operational

| Rule | Detail |
|---|---|
| **Default** | Extend via `_inherit` in a `fix_*` module. No exceptions without the process below |
| **Fork approval** | A fork requires written architecture-board approval naming the module, the reason, the maintenance owner and the exit plan |
| **Migration contribution** | Where the partner migrates an OCA module to v19, the work is **contributed back upstream**. This is a contractual condition, not a preference (RFP §5.4.2) |
| **Fork register** | Every approved fork is registered in M30 with its upstream divergence tracked and reviewed at every wave gate |
| **Exit condition** | Every fork carries a documented plan to return to upstream, reviewed annually |
| **CI enforcement** | Repository review in CI flags any modification to a file under an OCA subtree |

**Why this is stated at this length.** The fork decision does not feel consequential when it is
taken. It feels like a two-week saving in a tight wave. Its cost lands 18 months later as an upgrade
that cannot be automated, and by then the person who took the decision has usually moved on. The
register and the wave-gate review exist to make the accumulated cost visible while it is still small.

---

## 6. LAYER 3 — FREE THIRD-PARTY ODOO MODULES

L3 is the smallest layer at **~4% of requirements**, and it is deliberately kept small because it
carries the highest maintenance risk per unit of value: third-party modules have no OCA peer-review
guarantee, no CI guarantee, and no migration commitment.

### 6.1 Register

| # | Component | Purpose | Integration | Module | Wave | Maintenance risk |
|---|---|---|---|---|:--:|---|
| TC-060 | **SSLCOMMERZ** Odoo payment module | Card, net banking, aggregated wallets | INT-003 | M20 | W3 | **Medium** — validate maintainer activity before adoption |
| TC-061 | **bKash** payment connector | Mobile money collection, refund, reversal | INT-001 | M20 | W3 | **Medium** |
| TC-062 | **Nagad** payment connector | Mobile money collection, refund | INT-002 | M20 | W3 | **Medium** |
| TC-063 | Bangladesh **SMS gateway** connector | Transactional SMS, OTP | INT-010, INT-011 | M27 | W1 | Low — thin API wrapper |
| TC-064 | **WhatsApp Business** connector | Notifications, conversations, invoice sharing | INT-012 | M27 | W1 | Medium |
| TC-065 | **Barcode / QR** scanning extensions | Van stock, warehouse, custody scanning | — | M15, M02, M41 | W2 | Low — largely superseded by `OCA/stock-logistics-barcode` |

### 6.2 The L3 Adoption Rule

Because these modules carry no community quality guarantee, each is subject to a **pre-adoption
assessment** that is a wave-gate deliverable:

| # | Check | Fail action |
|---|---|---|
| L3-01 | Commits in the last 6 months, and an identifiable maintainer | Reject → build at L5 |
| L3-02 | Compatible licence (not GPL-3 in a way that conflicts with LGPL-3 distribution) | Reject |
| L3-03 | No credentials, keys or telemetry embedded in the module | Reject unconditionally |
| L3-04 | Reads no data outside its stated purpose | Reject unconditionally |
| L3-05 | Passes the same SAST and dependency scan as custom code | Remediate or reject |
| L3-06 | Payment modules only: gateway sandbox test passes for collect, refund, reversal, and duplicate-callback handling | Reject |

**A specific position on payment modules.** The payment connectors are the highest-consequence L3
components in the stack — they handle money, and a defect in duplicate-callback handling produces
double-crediting. The **fallback position is to wrap the gateway API directly at L5** rather than
accept an unmaintained third-party module. This costs roughly 3–5 PW per gateway and is the correct
trade if any of L3-01 through L3-06 fails. The decision is taken per gateway in Wave 3, and the
effort is carried as contingency, not as baseline.

---
## 7. LAYER 4 — STANDALONE OPEN-SOURCE SYSTEMS

L4 carries **~17% of requirements at zero licence cost** through 24 systems that do things Odoo
should not be asked to do: identity federation, API gateway management, GPS ingestion at 800
positions per minute, vehicle-routing optimisation, analytical query at warehouse scale, document
management at 50 TB, LLM inference, and observability.

**The selection principle for this layer.** A capability moves to L4 when it is a *solved
infrastructure problem with a mature open-source answer* and building it inside Odoo would mean
re-implementing that answer badly. Every system here has a named owner module, a named wave, and a
defined failure mode.

### 7.1 The Register — 24 Reference-Stack Systems in 28 Registered Components

| TC | System | Version | Licence | Serves | Wave | If it fails |
|---|---|---|---|---|:--:|---|
| TC-010 | **PostgreSQL** | **16** | PostgreSQL Licence | Primary datastore, all 225 entities | W1 | Total outage — HA + DR (§21.5) |
| TC-011 | **PgBouncer** | current | ISC | Connection pooling, 1,000 connections | W1 | Connection exhaustion; direct-connect fallback |
| TC-012 | **Redis** | **7.x** | BSD-3 | Cache, sessions, queues, locks, Streams event bus (W1–W5) | W1 | Session loss; degraded performance; queue drain |
| TC-013 | **Nginx** | **1.27+** | BSD-2 | Reverse proxy, TLS termination, static serving | W1 | Total ingress outage — HA pair |
| TC-014 | **Docker / K3s** | current | Apache-2.0 | Containerisation and orchestration | W1 | Deployment blocked; running workloads unaffected |
| TC-015 | **Keycloak** | **26.x** | Apache-2.0 | M29 — identity, SSO, MFA, step-up, per-client SAML/OIDC federation | W1 | **All authentication stops** — HA cluster mandatory |
| TC-016 | **Kong Gateway** | **3.x** | Apache-2.0 | M28 — API gateway, rate limiting, versioning | W1 | All portal API traffic stops — HA pair |
| TC-017 | **n8n** | **1.x** | Sustainable Use Licence | M28, M63 — workflow orchestration, brand-claim transformation | W1 | Automations queue; manual fallback per AUT catalogue |
| TC-018 | **Novu** | **2.x** | MIT | M27 — notification orchestration across 6 channels | W1 | Notifications queue; direct-send fallback for P0 messages |
| TC-019 | **MinIO** | current | AGPL-3 | Object storage — documents, evidence, exports, backups | W1 | Evidence capture blocked; local buffer on device |
| TC-020 | **Traccar** | **6.x** | Apache-2.0 | M02 — GPS ingestion and position streaming | W2 | Last-known position; manual technician status updates |
| TC-021 | **OSRM** | **5.x** | BSD-2 | M02, M03 — road distance and duration matrices | W2 | Straight-line distance fallback; degraded ETA accuracy |
| TC-022 | **VROOM** | **1.14+** | BSD-2 | M02, M03 — vehicle routing problem solving | W2 | Manual dispatch sequencing; previous day's route retained |
| TC-023 | **TimescaleDB** | **2.x** (Apache-2.0 features only) | Apache-2.0 / TSL | M02, M05, M17, M48 — time series, telemetry, GPS history | W2 | GPS history unavailable; live tracking unaffected |
| TC-024 | **Grafana** | **11.x** | AGPL-3 | M25, M28 — operational monitoring, real-time operations board | W2 | Blind operations; Prometheus retains data |
| TC-025 | **OpenTelemetry** | current | Apache-2.0 | Distributed tracing instrumentation (NFR-092) | W3 | Trace loss; logs and metrics unaffected |
| TC-026 | **Prometheus** | current | Apache-2.0 | Metrics collection and alerting | W3 | Alerting stops — **P0 for operations** |
| TC-027 | **Loki** | current | AGPL-3 | Log aggregation | W3 | Log search unavailable; local logs retained |
| TC-028 | **Tempo** | current | AGPL-3 | Trace storage and query | W3 | Trace query unavailable |
| TC-029 | **Metabase** | **0.52+** | AGPL-3 | M25 — BI, dashboards, self-service analytics, P06 | W4 | Reporting unavailable; scheduled exports retained |
| TC-030 | **Mayan EDMS** | **4.10** | Apache-2.0 | M24 — document management at volume, OCR, retention | W5 | New document indexing stops; OCA `dms` retains W1–W4 documents |
| TC-031 | **MeshCentral / RustDesk** | current | Apache-2.0 / AGPL-3 | M05 — attended and unattended remote support sessions | W5 | Remote support falls back to third-party tools with consent capture |
| TC-032 | **Wazuh** | current | GPL-2 | M05 — endpoint monitoring, security posture, SIEM | W5 | Client estate monitoring blind; alerting stops |
| TC-033 | **osquery** | current | Apache-2.0 | M05 — endpoint inventory and query | W5 | Asset discovery degraded |
| TC-034 | **Redpanda / Kafka** | current | BSL / Apache-2.0 | M28 — durable event bus with replay, from W6 | W6 | Redis Streams fallback; replay capability lost |
| TC-035 | **MLflow** | **2.x** | Apache-2.0 | M26 — model registry, experiment tracking, lineage | W6 | Model governance manual; inference unaffected |
| TC-036 | **Ollama** | **0.5+** | MIT | M26, M32 — self-hosted LLM inference, Bengali assistant | W6 | Rule-based responses; direct human routing |
| TC-037 | **ClickHouse** | **24.x** | Apache-2.0 | M25, M62 — analytical warehouse | W8 | Analytics falls back to the read replica with degraded performance |

**Register verified 13 August 2026 against RFP §5.4.3.** Two reconciliation notes, both disclosed
rather than smoothed:

**(a) 24 systems, 28 rows.** OpenTelemetry, Prometheus, Loki and Tempo are counted as one
observability entry in the RFP table and as four registered components here, because they are
separately deployed and separately versioned. This is a presentation difference, not a scope
difference.

**(b) Two components are required by NFRs but absent from the RFP's reference stack — finding
TSA-04.** Direct enumeration of Appendix A returns **30 L4 components**, not 28. The two additions
are:

| TC | Component | Required by | Why it cannot be omitted |
|---|---|---|---|
| **TC-038** | **ClamAV** | **NFR-063** — malware scanning on every file upload before storage or serving | The programme accepts uploaded files from customers, technicians, vendors, sellers and brand partners across ten portals. NFR-063 is P0 and needs a named scanner |
| **TC-039** | **Vault** *(or OpenBao)* | **NFR-062, IP-07** — secrets held in a vault, never in code, configuration or logs | Every integration credential, encryption key and service credential in the estate depends on it. It is a Wave 1 component |

Both are $0 at licence level (ClamAV GPL-2; OpenBao MPL-2.0 as the open-source option for Vault) and
neither changes the cost model. **They are raised as an addition to RFP §5.4.3 in §25.3.9** so that a
respondent pricing against the RFP's 24-system list is not surprised by two Wave 1 components.

### 7.2 The Nine Systems That Carry Material Load

#### 7.2.1 Keycloak — the identity spine (TC-015)

**Serves M29. Deployed W1. Single most availability-critical component after PostgreSQL.**

| Capability | Requirement satisfied |
|---|---|
| SSO across 12 portals, Odoo, Metabase, Grafana and the domain services | PS-01, PS-12, NFR-011 |
| OAuth 2.0 / OIDC / SAML 2.0 | API-01 through API-12, all portal auth |
| **Per-corporate-client SAML/OIDC federation** — a corporate client's staff log in with their own credentials | **INT-046**, P04 |
| MFA (TOTP, WebAuthn) mandatory for admin, finance, HR and privileged roles | NFR-012 |
| Step-up authentication for sensitive actions (T5 data, payroll, refunds) | NFR-065 |
| Session policy — 30 min idle external, 60 min internal, 12 h absolute | NFR-069 |
| 46 roles mapped to realm roles and client roles | §12.1.2 |
| Access lifecycle — provisioning on `employee.joined`, deprovisioning ≤ 1 h on `employee.left` | KPI-090 |

**Version position.** Keycloak has **no LTS release** — only the newest version receives active
development and security fixes. The current release as at 13 August 2026 is in the **26.7.x** line.
The reference stack specifies "26.x", which remains correct, but the operating consequence must be
stated: **Keycloak must be kept current continuously, not pinned for the life of a wave.** This is
registered as risk **TR-08** and an operational standard in §17.4.

**Deployment.** HA cluster from Wave 1 — not a single node. Every portal, every service and Odoo
itself depends on it; a single-node Keycloak makes authentication a single point of failure for the
entire estate.

#### 7.2.2 Kong Gateway — the API front door (TC-016)

**Serves M28. Deployed W1.**

Twelve API families (§12.2.2), per-consumer credentials, per-consumer rate limits with
`X-RateLimit-*` headers and `429 Retry-After` (API-08), OpenAPI 3.1 validation, correlation-id
injection (API-09), and a backend-for-frontend per portal so that P01's read model is not P10's.

**Why a gateway and not Nginx alone.** Nginx can rate-limit. It cannot do per-consumer OAuth token
introspection against Keycloak, per-consumer quota accounting across twelve distinct scopes, API
versioning with concurrent v1/v2 support, or developer-portal publication of OpenAPI specifications
to external partner consumers. At six portals the difference is marginal; at twelve portals plus
external partner API consumption (P12, INT-047) it is not.

**Version position.** Kong Gateway's open-source line is at 3.x, with 3.4.x designated LTS in the
enterprise line; releases through 3.14 exist as at 2026. The specification remains "3.x". Pin a
specific minor per environment and upgrade on the standard dependency cycle (§18.7).

#### 7.2.3 n8n — orchestration (TC-017)

**Serves M28 and M63. Deployed W1.**

n8n executes the cross-system choreography that does not belong inside a module: brand-specific
warranty-claim transformation for 17+ brand partners (§3.6.3), scheduled route optimisation trigger
(AUT-013), dunning sequences (AUT-023), reconciliation triggers, and the 60-automation catalogue's
orchestration layer (§12.8).

**Licence position — important.** n8n is licensed under the **Sustainable Use Licence**, a fair-code
licence, not an OSI-approved open-source licence. It restricts use to **internal business purposes**:
all use is permitted unless you are selling a product or service whose value derives entirely or
substantially from n8n functionality. **1000FiX's use is internal orchestration of its own ERP and is
squarely within the licence.** The boundary that must not be crossed: n8n workflows must not be
exposed as a saleable automation service to marketplace sellers, corporate clients or partners. This
is recorded in the licence register (Appendix D) and reviewed annually.

#### 7.2.4 Novu — notification orchestration (TC-018)

**Serves M27. Deployed W1.**

Six channels — SMS, WhatsApp, email, push (FCM/APNs), in-app inbox, and voice handoff — with template
resolution per locale, preference and quiet-hours enforcement (URD §23.5), delivery-status callbacks
feeding the audit trail, and per-channel fallback chains.

**The dependency that matters.** URD §23 and BRD §22 require notifications from Wave 1 onward, and
every module from Wave 1 needs to notify customers. The owning module M27 is scheduled for **Wave 4**.
If Novu is not deployed in Wave 1, each Wave 1–3 module builds its own send path — recreating exactly
the fragmentation the programme exists to remove. **This stack therefore deploys Novu and the
notification dispatcher service in Wave 1, ahead of M27**, and M27 in Wave 4 assumes the platform
rather than creating it. This is the technology position on open decision **Q-05** and is raised in
§25.3.

#### 7.2.5 Traccar + OSRM + VROOM — the field intelligence triad (TC-020/021/022)

**Serve M02 and M03. Deployed W2.**

| System | Role | Load |
|---|---|---|
| **Traccar** | Receives GPS from 400 technician devices and vehicle trackers; streams positions over REST and WebSocket | 800 positions/minute sustained (NFR-056), ~420M/year |
| **OSRM** | Computes road distance and duration matrices from OpenStreetMap data | Every dispatch scoring run and every ETA calculation |
| **VROOM** | Solves the vehicle routing problem with 1000FiX's constraints — skill, certification, van stock, zone, SLA, working time | Nightly full optimisation ≤ 20 minutes (NFR-044); intra-day re-optimisation on disruption |

**Why self-hosted routing rather than a commercial API (TD-05).** Commercial routing APIs cost
$200–400/month ongoing and — the decisive point — **cannot embed 1000FiX's constraints**. A route is
not valid because it is short; it is valid because the technician assigned to it holds the brand
certification the job requires (M22 FR-LMS-039), carries the part in the van (M15), is inside the
zone, and will not breach working-time rules (M55). Those constraints live in the ERP. VROOM accepts
them as inputs. A commercial API does not.

**Traffic data remains a paid API** (INT-022) because OSM does not carry real-time traffic and Dhaka
metro traffic materially changes ETA accuracy. This is a bounded third-party API cost
($150–350/month), not an L6 licence.

#### 7.2.6 TimescaleDB — time series (TC-023)

**Serves M02, M05, M17, M48. Deployed W2.**

GPS history, endpoint monitoring metrics, device telemetry and IoT sensor data. Hypertables with
native compression, continuous aggregates for dashboard queries, and retention policies aligned to
the data-retention schedule.

**Licence position — a real constraint.** TimescaleDB has an Apache-2.0 core, but a set of advanced
features sit under the source-available **Timescale License (TSL)**. **This stack uses Apache-2.0
features only.** The build must not take a dependency on a TSL-only feature, because doing so
converts a $0 component into a licensed one mid-programme. This is a CI-checkable constraint and is
registered in Appendix D.

#### 7.2.7 Metabase + Grafana — the two-headed analytics surface (TC-029, TC-024)

The split is deliberate and is often got wrong:

| | **Metabase** | **Grafana** |
|---|---|---|
| Question it answers | "What happened, and why?" | "What is happening right now?" |
| Data | PostgreSQL replica, then ClickHouse from W8 | Prometheus, Loki, Tempo, TimescaleDB |
| Users | Executives, managers, analysts (P06) | Operations, dispatch, IT (P06 real-time board, §17) |
| Latency | Seconds to minutes | Sub-second, live |
| Governance | Certified datasets, row-level security by operating unit and role | Operational dashboards, alert rules |

Both are **AGPL-3**. Both are deployed **unmodified**. Any modification to either must be published
— this is a licence obligation, not a preference, and is registered in Appendix D.

#### 7.2.8 Mayan EDMS — document management at volume (TC-030)

**Serves M24. Deployed W5.** The transition is deliberate: `OCA/dms` serves Waves 1–4, when document
volume is manageable and the requirement is attachment management. Mayan takes over from Wave 5 when
the requirements become **50 TB with sub-10-second retrieval (NFR-060)**, OCR including Bengali
(INT-044), retention-class enforcement (NFR-088, NFR-095) and records management.

**Migration is a planned Wave 5 activity**, not an assumption. Documents created in Waves 1–4 under
OCA `dms` migrate into Mayan with their metadata, retention class and audit history intact. This is
CD-236 and it must be in the Wave 5 plan.

#### 7.2.9 ClickHouse — the analytical warehouse (TC-037)

**Serves M25 and M62. Deployed W8.**

Deferred to Wave 8 deliberately. Through Wave 7 the PostgreSQL read replica serves analytical load
adequately. From Wave 8, with marketplace, e-commerce, rental, refurbishment and IoT all producing
volume, and with NFR-053 targeting 5 million service orders a year, the replica cannot serve both
transactional read offload and analytical scan. ClickHouse handles analytical volume at a fraction of
managed-warehouse cost (TD-09).

**Licence position:** Apache-2.0. Unencumbered.

### 7.3 Licence Compliance — Binding Obligations

| Licence | Components | Obligation | How it is met |
|---|---|---|---|
| **AGPL-3** | Metabase, Grafana, MinIO, RustDesk, Loki, Tempo | Source disclosure if **modified and served over a network** | **Deployed unmodified.** Any modification must be published. CI flags any change to a vendored AGPL component |
| **LGPL-3** | Odoo, most OCA modules | Modifications to the library itself must be shared | **Extensions are separate modules, never modifications to core** (AS-05, L1-01) |
| **Sustainable Use** | n8n | Free for internal business purposes only; not for resale as a competing service | Used only for internal orchestration; never exposed as a saleable service (§7.2.3) |
| **BSL** | Redpanda | Source-available; converts to Apache-2.0 four years after each code merge; production use permitted within stated limits | Reviewed at deployment; **Kafka (Apache-2.0) is the registered fallback** |
| **TSL** | TimescaleDB advanced features | Some features require a commercial licence | **Apache-2.0 features only**; CI-checked (§7.2.6) |
| **GPL-2** | Wazuh | Copyleft; distribution triggers source obligations | Deployed, not distributed |
| Apache-2.0 / MIT / BSD | The remainder | Attribution | Attribution register maintained in M30 |

**A licence register is maintained in M30, reviewed annually, and reviewed at every wave gate for
components entering that wave.** A licence change upstream is a registered risk (**TR-09**) — the
2018–2026 pattern of open-source licence changes across MongoDB, Redis, Elastic, HashiCorp and
Timescale makes this a live rather than theoretical concern, and every AGPL/BSL/TSL component in this
stack has a named fallback for that reason.

### 7.4 Systems Assessed and Not Selected

Recording the rejected option is what makes a future re-decision cheap.

| Capability | Selected | Assessed and rejected | Reason |
|---|---|---|---|
| BI | Metabase | Apache Superset | Embedding maturity and operational simplicity at this scale |
| Time series | TimescaleDB | InfluxDB | Same engine and operational skill set as PostgreSQL (TD-13) |
| Event bus | Redis Streams → Redpanda | RabbitMQ; Redis Streams alone | Durability and replay requirements grow past Redis at Wave 6 (TD-10) |
| Conversational AI | Ollama + open-weight model | Rasa 3.6; hosted LLM API | Rasa OSS in maintenance mode; hosted APIs send customer data offshore, breaching PDPA transfer restrictions (TD-06) |
| Routing | VROOM + OSRM | Google Routes; Timefold | Cannot embed 1000FiX skill/certification/van-stock constraints (TD-05) |
| Identity | Keycloak | Odoo native auth; Auth0 | Corporate-client federation (INT-046) and $0 (TD-07) |
| Warehouse | ClickHouse | PostgreSQL analytics; managed warehouse | Analytical volume from W8 exceeds economic replica capacity (TD-09) |
| Document mgmt | OCA `dms` → Mayan | Alfresco; commercial ECM | Volume, OCR and retention at $0 (TD-17) |
| Object storage | MinIO | Cloud-native object storage only | Portability across the split-residency boundary |
| Search | PostgreSQL FTS + `pg_trgm` → OpenSearch if needed | OpenSearch from day one | Deferred until measured need; see §12.9 |

---

## 8. LAYER 5 — CUSTOM DEVELOPMENT

### 8.1 Composition and the Restated Register

**This section corrects the largest structural gap in the inherited technology documentation.**

The source register `02-05` §5.2 allocates custom-development identifiers **CD-001 through CD-138**.
Direct enumeration of that allocation on 13 August 2026 shows it maps to **M01 through M30 only —
30 of the 67 modules.** The 37 modules registered as M31 through M67 have **no CD allocation at
all**. `02-05` itself flags this: *"A unified CD register covering all 67 modules is required and is
not yet written. All CD IDs in module files are marked provisional until it exists."*

**This section is that register.**

> **What this does and does not change.** It does **not** increase cost. The 1,513 person-weeks in the
> business case were measured by direct enumeration of all 67 module specification files and already
> include the work these new CD items name. Completing the register makes the deliverable breakdown
> match the effort figure that already exists. What it changes is that the RFP's "~138 CD items"
> figure is superseded by **248**, and respondents pricing against a 138-item deliverable list would
> be pricing a deliverable breakdown covering 45% of the modules. **This is raised as finding
> TSA-02 in Appendix G and as a change to RFP §5.3 in §25.3.**

#### 8.1.1 Restated composition

| Block | Range | Contents | Count |
|---|---|---|---:|
| **Block 1** | CD-001 … CD-138 | Custom Odoo modules and extensions for **M01–M30** — preserved verbatim from `02-05` §5.2; permanent under RG-02 | **138** |
| **Block 2** | CD-139 … CD-232 | Custom Odoo modules and extensions for **M31–M67** — new allocation | **94** |
| **Block 3** | CD-233 … CD-248 | Standalone domain services not attributable to a single module | **16** |
| | | **Total CD items** | **248** |
| *Separate register* | APP-01 … APP-10 | Applications — 4 Flutter, 6 Next.js. Registered separately because an application is not an Odoo module; conflating the two was a defect in the source composition table | **10** |

#### 8.1.2 Effort

| Deliverable class | Count | Effort *(est.)* | Basis |
|---|---:|---:|---|
| Custom Odoo modules and extensions (Blocks 1–2) | 232 | ~590–700 PW | Proportional allocation of measured module effort |
| Standalone services (Block 3) | 16 | ~170–200 PW | Extrapolated from the 12-service, 148 PW source figure |
| Applications (APP-01…10) | 10 | ~250–290 PW | 4 Flutter apps at ~126 PW for 4 in the source, scaled; 6 Next.js at ~148 PW |
| **L5 total** | **258** | **~1,010–1,190 PW** *(est.)* | |
| **Programme total (all layers)** | | **1,513 PW measured** | `02-02` §3, counted 13 Aug 2026 |

> **Rule RG-05 applies.** The per-class effort split above is **estimated**. Only the **1,513 PW
> programme total is measured**. The split is offered for planning and resourcing, not for
> contractual commitment, and a respondent must derive their own split from Annex 1 at requirement
> level. The split implies L5 consumes ~67–79% of total effort against ~25% of requirements — which
> is expected, because L1 and L2 requirements resolve to configuration while L5 requirements resolve
> to code, and it is the reason effort variance (+15%) tracked so much closer than requirement
> variance (+21%) in the source recount.

### 8.2 The Unified CD Register — All 67 Modules

#### Block 1 — CD-001 … CD-138 · Modules M01–M30 *(preserved from `02-05` §5.2)*

| Range | Module | Custom modules |
|---|---|---|
| CD-001…008 | **M01** SRM | `cd_service_order`, `cd_diagnostic`, `cd_estimate`, `cd_qc`, `cd_sla`, `cd_rework`, `cd_workshop`, `cd_service_ext` |
| CD-009…015 | **M02** FSM | `cd_dispatch`, `cd_technician`, `cd_route`, `cd_geofence`, `cd_van_stock`, `cd_field_session`, `cd_offline_sync` |
| CD-016…020 | **M03** LOG | `cd_consignment`, `cd_custody`, `cd_courier`, `cd_rider`, `cd_logistics_charge` |
| CD-021…023 | **M04** FRD | `cd_queue`, `cd_cash_drawer`, `cd_branch_ops` |
| CD-024…029 | **M05** RMS | `cd_msp_contract`, `cd_monitoring`, `cd_alerting`, `cd_msp_ticket`, `cd_remote_session`, `cd_patch_mgmt` |
| CD-030…032 | **M06** DTS | `cd_data_case`, `cd_media_custody`, `cd_destruction_cert` |
| CD-033…036 | **M07** CRM | `cd_customer_ext`, `cd_party_role`, `cd_bd_address`, `cd_consent` |
| CD-037…040 | **M08** CTR | `cd_contract_engine`, `cd_entitlement`, `cd_pm_schedule`, `cd_contract_profit` |
| CD-041…044 | **M09** WTY | `cd_warranty_register`, `cd_warranty_product`, `cd_claim_automation`, `cd_claim_reconcile` |
| CD-045…047 | **M10** LOY | `cd_loyalty`, `cd_voucher`, `cd_campaign` |
| CD-048…051 | **M11** PRC | `cd_price_book`, `cd_quotation`, `cd_bidding`, `cd_dynamic_pricing` |
| CD-052…058 | **M12** MKP | `cd_ecommerce`, `cd_marketplace_seller`, `cd_mp_listing`, `cd_mp_job`, `cd_review`, `cd_commission`, `cd_advertising` |
| CD-059…062 | **M13** RNT | `cd_rental_asset`, `cd_rental_agreement`, `cd_condition_report`, `cd_rental_billing` |
| CD-063…066 | **M14** TRF | `cd_tradein`, `cd_refurb`, `cd_grading`, `cd_resale` |
| CD-067…071 | **M15** INV | `cd_part_master`, `cd_stock_ext`, `cd_consignment_stock`, `cd_cycle_count`, `cd_landed_cost` |
| CD-072…074 | **M16** PRO | `cd_vendor_ext`, `cd_rfq`, `cd_import_order` |
| CD-075…079 | **M17** AST | `cd_asset_registry`, `cd_asset_estate`, `cd_maintenance_plan`, `cd_telemetry`, `cd_asset_health` |
| CD-080…082 | **M18** ESG | `cd_ewaste`, `cd_recycling`, `cd_esg_report` |
| CD-083…089 | **M19** FIN | `cd_mushak`, `cd_vat_register`, `cd_tds`, `cd_nid`, `cd_cash_position`, `cd_fixed_asset_ext`, `cd_close_checklist` |
| CD-090…095 | **M20** ARB | `cd_billing_engine`, `cd_subscription`, `cd_usage_billing`, `cd_revenue_recognition`, `cd_settlement`, `cd_dunning` |
| CD-096…101 | **M21** HCM | `cd_payroll_bd`, `cd_incentive`, `cd_shift_roster`, `cd_overtime`, `cd_beftn`, `cd_ess` |
| CD-102…104 | **M22** LMS | `cd_competency`, `cd_certification`, `cd_lms_bridge` |
| CD-105…106 | **M23** QMS | `cd_qms_ext`, `cd_audit_mobile` |
| CD-107…109 | **M24** DMS | `cd_document_ext`, `cd_esignature`, `cd_retention` |
| CD-110…112 | **M25** BID | `cd_metric_registry`, `cd_warehouse_sync`, `cd_embedded_analytics` |
| CD-113…118 | **M26** AIM | `cd_ml_gateway`, `cd_dispatch_ml`, `cd_forecast`, `cd_predictive`, `cd_pricing_ml`, `cd_llm_bridge` |
| CD-119…124 | **M27** CCE | `cd_conversation`, `cd_telephony`, `cd_agent_console`, `cd_assistant`, `cd_notification_ext`, `cd_inbox` |
| CD-125…129 | **M28** IPF | `cd_event_outbox`, `cd_api_layer`, `cd_webhook`, `cd_sync_engine`, `cd_integration_monitor` |
| CD-130…132 | **M29** SEC | `cd_rbac_ext`, `cd_audit_ext`, `cd_sod` |
| CD-133…138 | **M30** ADM | `cd_entity_config`, `cd_mdm`, `cd_feature_flag`, `cd_locale_pack`, `cd_country_pack`, `cd_platform_ops` |

> **Two corrections applied to Block 1 without changing any identifier.** (a) CD-048…051 were recorded
> against module code `SLS` in the v1.0-era register; `SLS` was superseded and M11's permanent code is
> **`PRC`** under RG-02. (b) CD-096…101 were recorded against `HRM`; M21's permanent code is **`HCM`**.
> The identifiers are unchanged and permanent; only the module code labels are corrected to match
> `02-02` §5.

#### Block 2 — CD-139 … CD-232 · Modules M31–M67 *(new allocation)*

| Range | Module | Custom modules | Wave |
|---|---|---|:--:|
| CD-139…141 | **M31** WSR Workshop & Depot Repair | `cd_bench`, `cd_wip_board`, `cd_repair_level` | W2 |
| CD-142…144 | **M32** CAI Conversational AI | `cd_intent`, `cd_conversation_flow`, `cd_ai_handoff` | W4 |
| CD-145…148 | **M33** CPM Customer & Party Master | `cd_party_master`, `cd_identity_document`, `cd_dedup_merge`, `cd_consent_registry` | W1 |
| CD-149…151 | **M34** CXM Customer Experience & Complaints | `cd_feedback`, `cd_complaint`, `cd_cx_score` | W4 |
| CD-152…154 | **M35** MKT Marketing & Campaigns | `cd_segment`, `cd_campaign_exec`, `cd_attribution` | W5 |
| CD-155…157 | **M36** QTE Quotation, Estimation & Tender | `cd_tender`, `cd_estimate_builder`, `cd_bid_response` | W3 |
| CD-158…160 | **M37** CAT Product & Service Catalogue | `cd_catalogue_item`, `cd_service_kit`, `cd_catalogue_publish` | W1 |
| CD-161…163 | **M38** ECM E-Commerce & Storefront | `cd_storefront_api`, `cd_cart_checkout`, `cd_order_fulfilment` | W7 |
| CD-164…166 | **M39** SUB Subscription & Recurring Revenue | `cd_subscription_plan`, `cd_proration`, `cd_renewal_engine` | W4 |
| CD-167…169 | **M40** PCM Partner, Channel & Franchise | `cd_partner_program`, `cd_referral`, `cd_channel_settlement` | W7 |
| CD-170…172 | **M41** WMS Warehouse Management | `cd_bin_strategy`, `cd_putaway_pick`, `cd_wave_picking` | W3 |
| CD-173…174 | **M42** SRM2 Supplier Relationship & Performance | `cd_vendor_scorecard`, `cd_vendor_compliance` | W4 |
| CD-175…177 | **M43** DPL Demand Planning & Replenishment | `cd_demand_forecast`, `cd_replenishment`, `cd_safety_stock` | W6 |
| CD-178…180 | **M44** ITC Import & Landed Cost | `cd_import_declaration`, `cd_duty_calc_bd`, `cd_landed_cost_alloc` | W6 |
| CD-181…182 | **M45** EAM Enterprise Asset & Test Equipment | `cd_test_equipment`, `cd_calibration` | W5 |
| CD-183…184 | **M46** FLT Fleet & Vehicle Management | `cd_fleet_ext`, `cd_fuel_trip` | W5 |
| CD-185…186 | **M47** FAC Facility & Workplace | `cd_facility`, `cd_workplace_service` | W7 |
| CD-187…189 | **M48** IOT IoT Telemetry & Predictive Maintenance | `cd_iot_ingest`, `cd_iot_rule`, `cd_predictive_asset` | W8 |
| CD-190…191 | **M49** FXA Fixed Assets & Capital | `cd_capex`, `cd_depreciation_bd` | W5 |
| CD-192…194 | **M50** TRE Treasury, Cash & Banking | `cd_bank_connect`, `cd_cash_forecast`, `cd_bank_recon_bd` | W3 |
| CD-195…197 | **M51** TAX Tax & Regulatory Compliance (BD) | `cd_mushak_return`, `cd_tds_certificate`, `cd_tax_filing` | W4 |
| CD-198…200 | **M52** APE Accounts Payable & Expense | `cd_ap_workflow`, `cd_expense_bd`, `cd_three_way_match_ext` | W3 |
| CD-201…203 | **M53** REV Revenue Recognition & Settlement | `cd_rev_rec`, `cd_commission_calc`, `cd_payout_run` | W4/W7 |
| CD-204…206 | **M54** FPA Cost Accounting, Budgeting & FP&A | `cd_cost_center_alloc`, `cd_budget`, `cd_business_line_pnl` | W6 |
| CD-207…209 | **M55** WFM Time, Attendance & Scheduling | `cd_roster`, `cd_attendance_bd`, `cd_working_time_rules` | W5 |
| CD-210…213 | **M56** PAY Payroll & Statutory Compliance | `cd_payroll_engine_bd`, `cd_tax_slab_bd`, `cd_pf_gratuity`, `cd_payslip_bn` | W5 |
| CD-214…215 | **M57** PIC Performance & Incentives | `cd_scorecard`, `cd_incentive_calc` | W5 |
| CD-216…217 | **M58** TAO Talent Acquisition & Onboarding | `cd_requisition`, `cd_onboarding` | W6 |
| CD-218…220 | **M59** HSE Health, Safety & Wellbeing | `cd_incident_report`, `cd_hazard`, `cd_safety_compliance` | W3/W6 |
| CD-221…222 | **M60** GRC Governance, Risk & Compliance | `cd_risk_register`, `cd_compliance_control` | W6 |
| CD-223…224 | **M61** KMS Knowledge Management | `cd_knowledge_article`, `cd_knowledge_search` | W6 |
| CD-225…227 | **M62** DAT Data Platform & Warehouse | `cd_data_contract`, `cd_lineage`, `cd_data_quality` | W4/W8 |
| CD-228…229 | **M63** BPA Process Automation & Orchestration | `cd_process_engine`, `cd_task_orchestration` | W3 |
| CD-230 | **M64** MDM Master Data Management | `cd_mdm_governance` | W2 |
| CD-231 | **M65** GLO Multi-Entity & Localisation | `cd_entity_localisation` | W9 |
| CD-232 | **M66** ITS · **M67** PPM | `cd_itsm_ppm` *(est. — specifications unwritten; see §25.1)* | W6/W7 |

> **Allocation note.** CD-232 covers M66 and M67 jointly because **neither module specification file
> exists**. Under rule RG-01 the allocation is reserved rather than detailed; it will be split when
> the specifications are written. Under RG-05 this row is *(est.)* and must not be used for
> contractual commitment. The reserved growth range for the split is **CD-249…CD-260** — that is, the
block immediately after Block 3, not inside it.

#### Block 3 — CD-233 … CD-248 · Standalone domain services

| CD | Service | Technology | Purpose | Wave |
|---|---|---|---|:--:|
| CD-233 | **Residency service** | Python / FastAPI | **The single gateway to the Bangladesh-resident store.** All reads and writes of residency-classified fields pass through it; every access logged (NFR-086, §14.4) | **W1** |
| CD-234 | Notification dispatcher | Node.js | Channel routing, template resolution, delivery tracking; fronts Novu | W1 |
| CD-235 | Dispatch scoring service | Python / FastAPI | Candidate scoring; calls ML models with rule-based fallback | W2 |
| CD-236 | Route optimisation orchestrator | Python | Wraps VROOM/OSRM; handles intra-day re-optimisation and document migration to Mayan | W2 |
| CD-237 | Telemetry collector | Go / Python | High-throughput ingestion into TimescaleDB | W2 |
| CD-238 | Document generation service | Python | High-volume PDF/A generation with **Bengali rendering** — invoices, Mushak 6.3, service reports, payslips, certificates | W3 |
| CD-239 | Pricing engine | Python | Rule evaluation, guard rails, decision logging | W3 |
| CD-240 | OCR service wrapper | Python | Bengali and English document extraction (INT-044) | W3 |
| CD-241 | Reconciliation service | Python | Nightly cross-system divergence detection (DI-07) | W3 |
| CD-242 | Settlement engine | Python | Commission calculation, payout file generation, dispute holds | W4 |
| CD-243 | Warehouse ETL | Python / dbt | Warehouse loading, transformation, data-quality gates | W4 |
| CD-244 | RMM collector | Python | Agent and SNMP data normalisation across client estates | W5 |
| CD-245 | ML inference gateway | Python / FastAPI | Single entry point to all models with per-model fallback | W6 |
| CD-246 | Speech-to-text wrapper | Python | Bengali call transcription and voice notes (INT-045) | W8 |
| CD-247 | Event replay & audit service | Python | Replay any consumer from a point in time; event-catalogue conformance checks | W6 |
| CD-248 | Data-subject request orchestrator | Python | **PDPA saga** — access, portability, rectification, erasure across both stores, warehouse, object store and search index, preserving the statutory processing record | **W4** |

#### Applications — APP-01 … APP-10

| APP | Application | Technology | Portal | Offline | Wave |
|---|---|---|---|:--:|:--:|
| APP-01 | **Technician mobile application** | Flutter | P02 | **24 h** | W2 |
| APP-02 | **Logistics & rider application** | Flutter | P09 | **24 h** | W3 |
| APP-03 | **Field auditor & quality application** | Flutter | P11 | **24 h** | W5 |
| APP-04 | **Customer mobile application** | Flutter | P01 | Cached read | W6 |
| APP-05 | Customer self-service portal (web) | Next.js 15 + Payload CMS 3 | P01 | PWA shell | W2 |
| APP-06 | Corporate B2B portal | Next.js 15 | P04 | — | W4 |
| APP-07 | Brand partner portal | Next.js 15 | P08 | — | W4 |
| APP-08 | Contact centre agent console | Next.js 15 | P10 | — | W4 |
| APP-09 | Marketplace seller portal | Next.js 15 (+ mobile — see §11.9) | P07 | — | W7 |
| APP-10 | Partner & referral portal | Next.js 15 | P12 | — | W7 |

### 8.3 Custom Development Standards

| # | Standard | Applies to |
|---|---|---|
| L5-01 | Every CD item ships with a README, an operational runbook and its OpenAPI specification — a definition-of-done item (DoD-11, DoD-06) | All |
| L5-02 | Unit test coverage ≥ 80%; **100% on financial and tax calculations** (DoD-03, NFR-090) | All |
| L5-03 | Every state-changing path emits its domain event through the outbox in the same transaction (AS-08) | All |
| L5-04 | Business rules enforced at the model layer and negative-tested through **both UI and API** (DoD-04) | Odoo modules |
| L5-05 | Access control, record rules and field permissions defined and negative-tested for every applicable role (DoD-07) | All |
| L5-06 | Bengali translation complete for every user-facing string before acceptance (DoD-08, AS-12) | All |
| L5-07 | KPI instrumentation with allocated `KPI-nnn` identifiers, visible in M25 (DoD-09, AS-15) | All |
| L5-08 | Services are stateless, horizontally scalable, and expose `/health` and `/metrics` | Block 3 services |
| L5-09 | Every service degrades to a defined fallback; no service failure blocks a P0 business path (IP-05, NFR-050) | Block 3 services |
| L5-10 | All source, configuration, migrations, tests and documentation are 1000FiX property, delivered continuously to a Company-controlled repository — **not at milestones** (RFP §5.10) | All |

### 8.4 Why Each Major Build Is a Build

The selection hierarchy requires that every L5 classification be justified. The eight largest are:

| Build | Why not L1–L4 | Effort weight |
|---|---|---|
| **Offline sync engine** (CD-015, APP-01…03) | No product delivers 24-hour offline with server-authoritative conflict resolution against a 67-module ERP, in Bengali, on a 3 GB Android device. This is the hardest single requirement in the programme | Very high |
| **Bangladesh compliance pack** (CD-083…085, 195…197, 210…213) | Mushak 6.3/9.1, NBR tax slabs, TDS, PF, gratuity and BEFTN do not exist in Odoo, OCA or any open-source component. They are statutory and they change | High |
| **Marketplace & settlement** (CD-052…058, CD-242) | Commission and payout must post to the ledger. A SaaS marketplace cannot be the system of record for money owed to 5,000 sellers (TD-11) | High |
| **Dispatch intelligence** (CD-009, CD-235, CD-114) | Scoring must combine skill, certification, van stock, zone, SLA risk and travel. No product knows 1000FiX's constraints | High |
| **MSP platform** (CD-024…029, CD-244) | Commercial PSA licensing scales badly at 400 technicians and still requires ERP integration (TD-12) | Medium-high |
| **Split-residency layer** (CD-233, CD-248) | A statutory requirement specific to Bangladesh's PDPA 2026 with no product equivalent | Medium-high |
| **Data-services custody** (CD-030…032) | Chain of custody for recovered customer data at T5 isolation with destruction certification — a regulated, evidence-bearing workflow | Medium |
| **Portal platform integration** (CD-126…128) | The contract with a portal platform that cannot be replaced (CON-03) must be built and versioned | Medium |

---

## 9. LAYER 6 — COMMERCIAL COMPONENTS

**Four components. $0–36K over three years. Each individually CFO-approved with a written
open-source alternative assessment, reviewed annually.**

L6 exists because v1.0's absolute "zero licence cost" position was not achievable for four
capabilities. Admitting a bounded, governed L6 is more honest than either forcing an unsuitable
open-source substitute or allowing unmanaged SaaS to accumulate outside the architecture.

| TC | Component | Purpose | Module | Estimated cost | Open-source alternative assessed | Wave |
|---|---|---|---|---|---|:--:|
| TC-070 | **Cloud telephony / CPaaS** | Inbound IVR, call routing and recording on hotline **16743** | M27 | $200–600/month | **Asterisk / FreePBX is technically viable** but requires carrier interconnect and in-house telecom expertise the Company does not hold. Revisit at renewal | W4 |
| TC-071 | **Qualified e-signature** | Legally binding signatures on AMC, MSP, rental and marketplace-seller agreements | M24 | $100–400/month | **OSS signing works technically but lacks accredited trust-service status**, which is what makes a signature enforceable. Operational signatures (job completion, delivery) are built at L5 and need no accreditation | W4 |
| TC-072 | **Identity verification / KYC** | Marketplace seller and high-value customer verification (INT-034, INT-035) | M12 | $0.30–0.80 per check | Requires an accredited data source. **No open-source equivalent exists** | W7 |
| TC-073 | **Endpoint RMM agent** *(conditional)* | Patch orchestration at scale across client Windows/macOS estates | M05 | $2–5 per endpoint/month | **Wazuh + osquery cover monitoring fully.** Patch orchestration at enterprise scale may require a commercial agent. **Decision deferred to a Wave 5 pilot** | W5–W6 |

### 9.1 L6 Governance

| # | Rule |
|---|---|
| L6-01 | Every L6 component requires **written CFO approval** before contract, with a documented open-source alternative assessment attached |
| L6-02 | Every L6 component is reviewed **annually** against whether an open-source alternative has matured; the review is minuted |
| L6-03 | Every L6 contract states the **exit position**: data export format, notice period, and what the Company retains at termination |
| L6-04 | Any L6 component with a **per-user, per-technician or per-transaction licence metric must be modelled at 5× current volume** before approval (mirrors RFP condition ALT-08) |
| L6-05 | **No customer personal data leaves the Company to an L6 provider** without a PDPA transfer assessment, a documented safeguard and an Authority notification record where required (NFR-086b, NFR-099) |
| L6-06 | An implementation partner proposing any **additional** L6 component must price it separately and provide a written OSS alternative assessment (RFP §5.4.4) |

**L6-05 has teeth and constrains component choice.** Telephony records customer calls; KYC processes
NID and trade-licence documents; e-signature holds signed contracts bearing personal data. All three
are transfers of personal data — and KYC touches Sensitive Personally Identifiable Data directly.
Each requires a transfer assessment before contract, and the KYC provider in particular must satisfy
NFR-099's restriction on large-scale transfer of government unique identifiers. **The preferred
resolution for KYC is a provider that performs verification against a Bangladesh-resident data
source without exporting the identifier**; where that is not available, the assessment and Authority
notification must be complete before Wave 7.

### 9.2 The RMM Decision (TC-073) — Deliberately Deferred

This is the only conditional L6 component and the only open L6 decision.

| Position | Detail |
|---|---|
| **What is certain** | Wazuh + osquery cover endpoint **monitoring**, inventory, security posture and vulnerability detection completely, at $0 |
| **What is uncertain** | Whether patch **orchestration** across heterogeneous client Windows/macOS estates at MSP scale can be delivered by open-source tooling with acceptable operational cost |
| **How it is resolved** | A **Wave 5 pilot** on a defined client subset, measuring patch success rate, remediation time and operator effort against a commercial agent trial |
| **Cost if commercial** | $2–5 per endpoint/month — **this is the one L6 line with volume-scaling exposure**, so L6-04 applies with force: model at 5× the contracted endpoint count before signing |
| **Decision owner** | CTO, with CFO approval; recorded at the Wave 5 gate |

---
---

# PART C — COVERAGE

---

## 10. MODULE-TO-TECHNOLOGY COVERAGE — ALL 67 MODULES

### 10.1 How to Read This Section

Each of the eleven categories has one table. **Every one of the 67 modules has exactly one row.** Each
row states the delivery technology at every layer that contributes to it.

| Column | Meaning |
|---|---|
| **W** | Wave, from `02-02` §4.2. `W1/W4` means delivered across two waves |
| **Reqs** | Measured requirement count from the module specification file, counted 13 Aug 2026 |
| **L1** | Odoo 19 CE modules used |
| **L2** | OCA repositories used |
| **L4** | Standalone open-source systems used |
| **L5** | CD items — the custom development that delivers what the layers above do not |
| **L6** | Commercial component, where one is required |
| **Own** | System owner from `02-02` §4.3 |

`—` means the layer contributes nothing to this module. **`∅` would mean no technology is assigned at
all; there are none, and the audit in Appendix G verified this by enumeration.**

Requirement counts are **per-module figures from the register**. Under the reconciliation carried in
RFP §6.1a and BRD §4.2, per-module figures are **measured for Categories A, B and H** and
***estimated* for C, D, E, F, G, I, J and K**, while **category totals are measured throughout**. The
category totals shown in each table heading are the measured, authoritative figures. **Do not add the
per-module column and expect it to equal the heading** — for Categories C, F, G and I it will not,
and the variance is disclosed in the source. Use the category total.

### 10.2 Category A — Service Delivery & Operations · 7 modules · **362 requirements (measured)** · 206 PW

| ID | Module · Code | W | Reqs | L1 Odoo | L2 OCA | L4 OSS | L5 CD | L6 | Own |
|---|---|:--:|---:|---|---|---|---|:--:|---|
| **M01** | Service Request & Order Management · `SRM` | W1/W2 | 88 | `repair`, `project`, `calendar`, `mail` | `field-service` (core, substatus, template, stage-validation, change-mgmt), `helpdesk` (mgmt, sla) | Novu, n8n | **CD-001…008** — order, diagnostic, estimate, QC, SLA, rework, workshop, service ext | — | Service Ops Dir |
| **M31** | Workshop & Depot Repair · `WSR` | W2 | 58 | `repair`, `stock` | `field-service_repair`, `stock-logistics-workflow` | — | **CD-139…141** — bench, WIP board, repair level | — | Service Ops Dir |
| **M02** | Field Service & Dispatch · `FSM` | W2 | 74 | `calendar`, `fleet` | `field-service` (skill, route, timeline, geoengine, vehicle, google_map) | **Traccar, OSRM, VROOM, TimescaleDB**, Redis | **CD-009…015** — dispatch, technician, route, geofence, van stock, field session, **offline sync**; CD-235, CD-236 | — | Service Ops Dir |
| **M03** | Service Logistics & Reverse Logistics · `LOG` | W3 | 42 | `stock` | `field-service_distribution`, `stock-logistics-*`, `stock-logistics-barcode` | OSRM, VROOM, Traccar | **CD-016…020** — consignment, custody, courier, rider, logistics charge | — | Logistics Mgr |
| **M04** | Branch & Front-Desk Operations · `FRD` | W1 | 31 | `base`, `mail` | `operating-unit` | — | **CD-021…023** — queue, cash drawer, branch ops | — | Branch Ops Lead |
| **M05** | Remote Support & Managed Services · `RMS` | W5 | 61 | `project` | `helpdesk` (mgmt, sla), `contract` | **MeshCentral/RustDesk, Wazuh, osquery**, TimescaleDB, Grafana | **CD-024…029** — MSP contract, monitoring, alerting, MSP ticket, remote session, patch mgmt; CD-244 | **RMM agent (conditional)** | Corp Services Head |
| **M06** | Data Services & Secure Data Handling · `DTS` | W6 | 34 | `project` | `dms` | Mayan EDMS, MinIO | **CD-030…032** — data case, media custody, destruction certificate; **CD-233 residency service** | — | Tech Services Head |

**Category A technology note.** This category is the reason `OCA/field-service` is the single most
load-bearing L2 dependency in the stack (§5.3.1) and the reason its v19 migration gap is a **Wave 1
blocking gate**. M02's offline sync (CD-015) is the hardest deliverable in the programme; it is
covered separately in §16. M06 is the only Category A module that touches the Bangladesh-resident
store, because recovered customer data is residency-classified under NFR-086.

### 10.3 Category B — Customer Engagement & Experience · 7 modules · **320 requirements (measured)** · 148 PW

| ID | Module · Code | W | Reqs | L1 Odoo | L2 OCA | L4 OSS | L5 CD | L6 | Own |
|---|---|:--:|---:|---|---|---|---|:--:|---|
| **M33** | Customer & Party Master · `CPM` | W1 | 52 | `contacts`, `base` | **`partner-contact`** (30+) | — | **CD-145…148** — party master, identity document, dedup/merge, **consent registry**; CD-033…036; **CD-233** | — | CCO |
| **M07** | CRM, Sales Pipeline & Account Mgmt · `CRM` | W1/W4 | 46 | `crm`, `contacts`, `mail` | `partner-contact`, `field-service_crm`, `field-service_partner_multi_relation` | — | CD-033…036 — customer ext, party role, BD address, consent | — | CCO |
| **M10** | Loyalty, Membership & Rewards · `LOY` | W2 | 44 | `sale` | — | Redis | **CD-045…047** — loyalty, voucher, campaign | — | Marketing Head |
| **M34** | Customer Experience, Feedback & Complaints · `CXM` | W4 | 42 | `mail` | `helpdesk_mgmt`, `management-system` | Novu | **CD-149…151** — feedback, complaint, CX score | — | Cust Svc Mgr |
| **M27** | Omnichannel Contact Centre · `CCE` | W4 *(platform W1)* | 58 | `mail` | `helpdesk_mgmt` | **Novu, n8n**, Redis | **CD-119…124** — conversation, telephony, agent console, assistant, notification ext, inbox; **CD-234** | **Cloud telephony / CPaaS** | Cust Svc Mgr |
| **M32** | Conversational AI & Virtual Assistant · `CAI` | W4 | 38 | — | — | **Ollama**, MLflow | **CD-142…144** — intent, conversation flow, AI handoff; CD-118, CD-245 | — | Cust Svc Mgr |
| **M35** | Marketing, Campaigns & Demand Generation · `MKT` | W5 | 40 | `crm`, `mail` | `partner-contact` | Novu, n8n, Metabase | **CD-152…154** — segment, campaign execution, attribution | — | Marketing Head |

**Category B technology note — two sequencing consequences.** First, **M27's notification platform
(Novu + CD-234) deploys in Wave 1**, three waves ahead of M27 itself, because every module from Wave
1 needs to notify customers and building per-module send paths would recreate the fragmentation the
programme exists to remove (open decision Q-05, §25.3). Second, **M32 depends on M61 Knowledge
Management, scheduled two waves later in W6.** An assistant without a knowledge base can answer
transactional questions from live ERP data but not "how do I" or "why is this happening". The
technology position is that CD-142's intent model must be configurable to a reduced intent scope at
W4 launch, with the knowledge-backed intents enabled when M61 lands (open decision Q-01, §25.3).

### 10.4 Category C — Commercial, Pricing & Revenue · 9 modules · **494 requirements (measured)** · 262 PW

> Per-module figures below are ***(est.)***; the measured category total is **494**, a **+39%**
> variance. Price against the category total and Annex 1, not against this column.

| ID | Module · Code | W | Reqs | L1 Odoo | L2 OCA | L4 OSS | L5 CD | L6 | Own |
|---|---|:--:|---:|---|---|---|---|:--:|---|
| **M37** | Product & Service Catalogue · `CAT` | W1 | 34 *(est.)* | **`product`**, `sale` | `product-attribute` | Redis (cache) | **CD-158…160** — catalogue item, service kit, catalogue publish | — | CCO |
| **M11** | Pricing, Rate Cards & Dynamic Pricing · `PRC` | W3/W7 | 36 *(est.)* | `product` pricelists, `sale` | — | — | **CD-048…051** — price book, quotation, bidding, dynamic pricing; **CD-239 pricing engine**; CD-117 | — | CCO |
| **M36** | Quotation, Estimation & Tender · `QTE` | W3 | 32 *(est.)* | `sale`, `sale_management` | `purchase-workflow` (tender patterns) | — | **CD-155…157** — tender, estimate builder, bid response | — | CCO |
| **M08** | Contract Lifecycle Management · `CTR` | W4 | 44 *(est.)* | `sale` | **`contract`** (12), `field-service_agreement`, `field-service_recurring` | n8n | **CD-037…040** — contract engine, entitlement, PM schedule, contract profit | **Qualified e-signature** | CCO |
| **M09** | Warranty, Protection Plans & Claims · `WTY` | W4 | 48 *(est.)* | `account` | `field-service_equipment_warranty` | **n8n** (17+ brand transformations) | **CD-041…044** — warranty register, warranty product, claim automation, claim reconcile | — | Finance Dir |
| **M39** | Subscription & Recurring Revenue · `SUB` | W4 | 30 *(est.)* | `sale`, `account` | `contract` | — | **CD-164…166** — subscription plan, proration, renewal engine; CD-091, CD-092 | — | CFO |
| **M38** | E-Commerce & Digital Storefront · `ECM` | W7 | 40 *(est.)* | `sale`, `stock`, `product` | — | Redis, MinIO | **CD-161…163** — storefront API, cart/checkout, order fulfilment; APP-05 | — | CCO |
| **M12** | Marketplace & Seller Ecosystem · `MKP` | W7 | 62 *(est.)* | `sale`, `account` | `partner-contact` | Redis, MinIO, Novu | **CD-052…058** — e-commerce, seller, listing, job, review, commission, advertising; **CD-242 settlement engine**; APP-09 | **KYC / identity verification** | CCO |
| **M40** | Partner, Channel, Alliance & Franchise · `PCM` | W7 | 30 *(est.)* | `sale`, `contacts` | `partner-contact` | — | **CD-167…169** — partner program, referral, channel settlement; APP-10 | — | CCO |

**Category C technology note.** This category carries the programme's money-movement risk. **CD-242
(settlement engine) is the highest-consequence single service in the stack**: it calculates
commission for up to 5,000 marketplace sellers, generates disbursement files, and must post to the
ledger atomically. It is subject to L5-02's 100% test-coverage requirement on financial calculation,
AS-10's decimal-money rule, and DI-02's reconcilability rule without exception.

### 10.5 Category D — Circular & Asset-Based Business · 3 modules · **109 requirements (measured)** · 60 PW

| ID | Module · Code | W | Reqs | L1 Odoo | L2 OCA | L4 OSS | L5 CD | L6 | Own |
|---|---|:--:|---:|---|---|---|---|:--:|---|
| **M13** | Rental & Equipment-as-a-Service · `RNT` | W6 | 44 *(est.)* | **`sale_renting`**, `stock`, `maintenance` | `field-service_equipment` | — | **CD-059…062** — rental asset, rental agreement, condition report, rental billing | — | Corp Svcs Head |
| **M14** | Trade-In, Refurbishment & Resale · `TRF` | W6 | 39 *(est.)* | `stock`, `repair`, `product` | `stock-logistics-workflow` | MinIO (evidence) | **CD-063…066** — trade-in, refurbishment, grading, resale | — | Retail Ops Head |
| **M18** | E-Waste, Recycling & Circular Economy · `ESG` | W8 | 26 *(est.)* | `stock` | `management-system` | Mayan EDMS | **CD-080…082** — e-waste, recycling, ESG report | — | Quality Mgr |

**Category D technology note.** All three modules depend on the **device identity and custody chain**
established by M17 and M03. A trade-in device must carry its data-wipe certificate (CD-032) before
refurbishment, and an e-waste batch must carry its disposal certificate before the ESG return —
these are evidence-bearing workflows where the document store (Mayan, MinIO) is part of the
compliance record, not an attachment.

### 10.6 Category E — Supply Chain & Inventory · 6 modules · **235 requirements (measured)** · 119 PW

> Per-module figures ***(est.)***; measured category total **235**, a **+22%** variance.

| ID | Module · Code | W | Reqs | L1 Odoo | L2 OCA | L4 OSS | L5 CD | L6 | Own |
|---|---|:--:|---:|---|---|---|---|:--:|---|
| **M15** | Spare Parts & Inventory · `INV` | W2 | 48 *(est.)* | **`stock`**, `product` | **`stock-logistics-workflow`, `-warehouse`, `-barcode`**, `field-service_stock` | Redis | **CD-067…071** — part master, stock ext, consignment stock, cycle count, landed cost | — | Warehouse Mgr |
| **M41** | Warehouse Management · `WMS` | W3 | 34 *(est.)* | `stock` | `stock-logistics-warehouse`, `-barcode` | — | **CD-170…172** — bin strategy, put-away/pick, wave picking | — | Warehouse Mgr |
| **M16** | Procurement & Strategic Sourcing · `PRO` | W3 | 32 *(est.)* | **`purchase`** | **`purchase-workflow`** (25+) | n8n | **CD-072…074** — vendor ext, RFQ, import order | — | Procurement Mgr |
| **M42** | Supplier Relationship & Performance · `SRM2` | W4 | 26 *(est.)* | `purchase` | `purchase-workflow`, `partner-contact` | Metabase | **CD-173…174** — vendor scorecard, vendor compliance | — | Procurement Mgr |
| **M43** | Demand Planning & Replenishment · `DPL` | W6 | 24 *(est.)* | `stock` reordering | `stock-logistics-warehouse` | **MLflow, ClickHouse** | **CD-175…177** — demand forecast, replenishment, safety stock; CD-115 | — | Warehouse Mgr |
| **M44** | Import, Trade Compliance & Landed Cost · `ITC` | W6 | 28 *(est.)* | `purchase`, `stock` | `account-financial-tools` (landed cost) | — | **CD-178…180** — import declaration, **Bangladesh duty calculation**, landed cost allocation | — | Procurement Mgr |

### 10.7 Category F — Asset, Equipment & Facilities · 5 modules · **232 requirements (measured)** · 114 PW

> Per-module figures ***(est.)***; measured category total **232** — a **+73% variance, the largest
> in the programme.** The per-module column here is the least reliable in this document. Price
> against Annex 1.

| ID | Module · Code | W | Reqs | L1 Odoo | L2 OCA | L4 OSS | L5 CD | L6 | Own |
|---|---|:--:|---:|---|---|---|---|:--:|---|
| **M17** | Device & Customer Asset Registry · `AST` | W2 | 34 *(est.)* | `maintenance`, `product` | **`field-service_equipment`** | TimescaleDB | **CD-075…079** — asset registry, asset estate, maintenance plan, telemetry, asset health | — | Service Ops Dir |
| **M45** | Enterprise Asset & Test Equipment · `EAM` | W5 | 26 *(est.)* | `maintenance` | `management-system` (calibration control) | — | **CD-181…182** — test equipment, calibration | — | Quality Mgr |
| **M46** | Fleet & Vehicle Management · `FLT` | W5 | 24 *(est.)* | **`fleet`** | `field-service_fleet`, `field-service_vehicle` | Traccar | **CD-183…184** — fleet ext, fuel/trip | — | Logistics Mgr |
| **M47** | Facility, Branch Infrastructure & Workplace · `FAC` | W7 | 22 *(est.)* | `maintenance` | `operating-unit` | — | **CD-185…186** — facility, workplace service | — | Branch Ops Lead |
| **M48** | IoT Telemetry & Predictive Maintenance · `IOT` | W8 | 28 *(est.)* | — | — | **TimescaleDB, MLflow, Redpanda** | **CD-187…189** — IoT ingest, IoT rule, predictive asset; **CD-237 telemetry collector**; CD-116 | — | CTO |

**Category F technology note.** M17 must scale to **5 million assets (NFR-054)** with telemetry at
**50,000 points per minute (NFR-055)**. This is the load case that justifies TimescaleDB as a
separate store from Wave 2 rather than a Wave 8 addition — the device registry begins accumulating
health telemetry as soon as managed services (M05) starts in Wave 5, and retrofitting a time-series
store under a live asset registry is materially harder than deploying it early.

### 10.8 Category G — Finance & Treasury · 8 modules · **333 requirements (measured)** · 185 PW

> Per-module figures ***(est.)***; measured category total **333**, a **+29%** variance driven by
> statutory density.

| ID | Module · Code | W | Reqs | L1 Odoo | L2 OCA | L4 OSS | L5 CD | L6 | Own |
|---|---|:--:|---:|---|---|---|---|:--:|---|
| **M19** | Financial Accounting & GL · `FIN` | W3 | 40 *(est.)* | **`account`** | **`account-financial-tools`, `account-financial-reporting`, `l10n-bangladesh`** | — | **CD-083…089** — Mushak, VAT register, TDS, NID, cash position, fixed asset ext, close checklist | — | CFO |
| **M20** | Accounts Receivable & Collections · `ARB` | W3 | 36 *(est.)* | `account` | `account-financial-tools` | n8n (dunning) | **CD-090…095** — billing engine, subscription, usage billing, revenue recognition, settlement, dunning; **CD-238 document generation** | — | CFO |
| **M52** | Accounts Payable & Employee Expense · `APE` | W3 | 28 *(est.)* | `account`, **`hr_expense`**, `purchase` | `account-financial-tools`, `purchase-workflow` | — | **CD-198…200** — AP workflow, Bangladesh expense, three-way-match ext | — | CFO |
| **M50** | Treasury, Cash & Banking · `TRE` | W3 | 30 *(est.)* | `account` | `account-financial-tools` | — | **CD-192…194** — bank connect, cash forecast, **Bangladesh bank reconciliation**; CD-100 BEFTN | — | CFO |
| **M51** | Tax & Regulatory Compliance (BD) · `TAX` | W4 | 34 *(est.)* | `account` tax engine | `l10n-bangladesh` | — | **CD-195…197** — **Mushak 9.1 return, TDS certificate, tax filing**; CD-083…085 | — | CFO |
| **M53** | Revenue Recognition, Commission & Settlement · `REV` | W4/W7 | 38 *(est.)* | `account` | `account-financial-tools` | — | **CD-201…203** — revenue recognition, commission calculation, payout run; **CD-242** | — | CFO |
| **M49** | Fixed Assets & Capital Investment · `FXA` | W5 | 22 *(est.)* | `account` | **`account-financial-tools`** (asset management) | — | **CD-190…191** — capex, Bangladesh depreciation | — | CFO |
| **M54** | Cost Accounting, Budgeting & FP&A · `FPA` | W6 | 30 *(est.)* | `account` analytic | **`mis-builder`, `reporting-engine`** | Metabase, ClickHouse | **CD-204…206** — cost-centre allocation, budget, business-line P&L | — | CFO |

**Category G technology note — the non-negotiables.** Three rules apply here without exception and
are CI-enforced: **AS-10** (money is `Monetary` with explicit currency, never float), **L5-02** (100%
unit-test coverage on financial and tax calculation), and **DI-02** (every financial posting is
reconcilable to its source transaction). Additionally, **NFR-101** requires the system to *block*
input-VAT credit claims that are not supported by a valid Mushak 6.3 — this is a hard rule at the
model layer (BR-STD-05), not a warning, and it is the clearest example in the stack of a statutory
obligation becoming a code-level constraint.

### 10.9 Category H — People & Workforce · 7 modules · **310 requirements (measured)** · 124 PW

| ID | Module · Code | W | Reqs | L1 Odoo | L2 OCA | L4 OSS | L5 CD | L6 | Own |
|---|---|:--:|---:|---|---|---|---|:--:|---|
| **M21** | Core HR & Employee Lifecycle · `HCM` | W5 | 46 | **`hr`** | **`OCA/hr`** (50+) | Keycloak (lifecycle events) | **CD-096…101** — payroll BD, incentive, shift roster, overtime, BEFTN, ESS | — | HR Director |
| **M55** | Time, Attendance & Workforce Scheduling · `WFM` | W5 | 52 | **`hr_attendance`**, `hr_holidays` | `OCA/hr` | — | **CD-207…209** — roster, **Bangladesh attendance (biometric, residency-classified)**, working-time rules | — | HR Director |
| **M56** | Payroll, Benefits & Statutory Compliance · `PAY` | **W5 · P0** | 54 | `hr` | **`OCA/payroll`** | — | **CD-210…213** — **payroll engine BD, tax slabs, PF & gratuity, Bengali payslip**; CD-100 BEFTN; CD-238 | — | HR Director |
| **M57** | Performance, Incentives & Compensation · `PIC` | W5 | 42 | `hr` | `OCA/hr` | Metabase | **CD-214…215** — scorecard, incentive calculation; CD-097 | — | HR Director |
| **M22** | Learning, Competency & Certification · `LMS` | W5 | 40 | `hr` | `OCA/hr` | — | **CD-102…104** — competency, certification, LMS bridge | — | HR Director |
| **M58** | Talent Acquisition & Onboarding · `TAO` | W6 | 34 | `hr` | `OCA/hr` (recruitment) | — | **CD-216…217** — requisition, onboarding | — | HR Director |
| **M59** | Health, Safety & Wellbeing · `HSE` | W3/W6 | 42 | `hr` | `management-system` (ISO 45001 patterns) | MinIO (evidence) | **CD-218…220** — incident report, hazard, safety compliance | — | HR Director |

**Category H technology note — two cross-wave build constraints that must be honoured in Wave 2.**

1. **M22's certification eligibility check (FR-LMS-039) is consumed by M02 at assignment. M02 goes
   live in W2; M22 in W5.** The interface must be **built into M02 in Wave 2 as a stub returning
   "eligible"**, and connected in Wave 5. Retrofitting a blocking check into a live assignment path
   three years into production is materially riskier than building the seam early. This is a
   technology instruction, not a preference.

2. **M59's mobile safety reporting should move from W6 to W3.** FR-HSE-009 (incident, near-miss and
   hazard reporting from the technician app) and FR-HSE-011 (immediate serious-incident alert) depend
   only on **P02 and M21**, not on the rest of M59. They ship with the technician app in Wave 3 at low
   incremental cost. **This stack assigns CD-218 to W3 and CD-219…220 to W6** on that basis, and the
   split is raised for wave-plan ratification in §25.3.

### 10.10 Category I — Governance, Risk, Quality & Knowledge · 4 modules · **170 requirements (measured)** · 78 PW

> Per-module figures ***(est.)***; measured category total **170**, a **+44%** variance.

| ID | Module · Code | W | Reqs | L1 Odoo | L2 OCA | L4 OSS | L5 CD | L6 | Own |
|---|---|:--:|---:|---|---|---|---|:--:|---|
| **M23** | Quality Management System · `QMS` | W5 | 32 *(est.)* | `mail`, `project` | **`management-system`** (33) | MinIO (evidence) | **CD-105…106** — QMS ext, **audit mobile** (APP-03) | — | Quality Mgr |
| **M60** | Governance, Risk & Compliance · `GRC` | W6 | 34 *(est.)* | — | `management-system` | Wazuh (control evidence) | **CD-221…222** — risk register, compliance control | — | CFO |
| **M24** | Document, Records & E-Signature · `DMS` | W3 | 28 *(est.)* | `ir.attachment` | **`OCA/dms`** (5) | **Mayan EDMS** (from W5), MinIO | **CD-107…109** — document ext, **e-signature**, retention; CD-236 migration | **Qualified e-signature** | Quality Mgr |
| **M61** | Knowledge Management & Technical Library · `KMS` | W6 | 24 *(est.)* | `mail` | — | **Ollama** (semantic search), PostgreSQL FTS | **CD-223…224** — knowledge article, knowledge search | — | Quality Mgr |

**Category I technology note — the two-tier e-signature position.** M24 delivers **two distinct
signature capabilities** and conflating them is a costly mistake. **Operational signatures** — job
completion on the technician's device, delivery acceptance by a customer, audit acknowledgement —
are built at L5 (CD-108) with capture, timestamp, GPS and evidence binding, and require no
accreditation. **Legally binding contract signatures** — AMC, MSP, rental and marketplace-seller
agreements — require **accredited trust-service status**, which open-source signing cannot supply,
and are therefore L6 (TC-071). Using the L6 service for operational signatures would multiply
envelope cost by a factor of thousands; using L5 for contracts would produce unenforceable
agreements.

### 10.11 Category J — Data, Analytics & Intelligence · 4 modules · **146 requirements (measured)** · 97 PW

| ID | Module · Code | W | Reqs | L1 Odoo | L2 OCA | L4 OSS | L5 CD | L6 | Own |
|---|---|:--:|---:|---|---|---|---|:--:|---|
| **M62** | Data Platform, Warehouse & Governance · `DAT` | W4/W8 | 34 *(est.)* | — | — | **ClickHouse, PostgreSQL replicas, Redpanda** | **CD-225…227** — data contract, lineage, data quality; **CD-243 warehouse ETL (dbt)** | — | CTO |
| **M25** | Business Intelligence & Reporting · `BID` | W4 | 30 *(est.)* | native views | **`reporting-engine`, `mis-builder`, `account-financial-reporting`** | **Metabase, Grafana, ClickHouse** | **CD-110…112** — metric registry, warehouse sync, embedded analytics | — | CTO |
| **M26** | AI/ML Services & Model Operations · `AIM` | W6–W8 | 38 *(est.)* | — | — | **MLflow, Ollama**, TimescaleDB, ClickHouse | **CD-113…118** — ML gateway, dispatch ML, forecast, predictive, pricing ML, LLM bridge; **CD-245 inference gateway** | — | CTO |
| **M63** | Process Automation & Workflow Orchestration · `BPA` | W3 | 28 *(est.)* | `base` automation | `server-tools` | **n8n**, Redis, Redpanda | **CD-228…229** — process engine, task orchestration | — | CTO |

**Category J technology note — the ML fallback rule.** Every model served through CD-245 must have a
**deterministic fallback**: dispatch scoring falls back to rule-based scoring, demand forecast falls
back to reorder points, dynamic pricing falls back to the published price book, and the LLM assistant
falls back to rule-based responses and human routing. **No business path may depend on a model being
available or correct.** Every prediction writes `model.prediction_made` to the event log with its
inputs and its model version, so that a wrong outcome is explicable and the model is improvable
(IP-05, NFR-050).

### 10.12 Category K — Platform & Technology · 7 modules · **219 requirements measured across 5 written specs** *(+48 est. for M66, M67)* · 120 PW

| ID | Module · Code | W | Reqs | L1 Odoo | L2 OCA | L4 OSS | L5 CD | L6 | Own |
|---|---|:--:|---:|---|---|---|---|:--:|---|
| **M28** | Integration, API & Event Platform · `IPF` | W1 | 44 *(est.)* | JSON-2 API | `server-tools` | **Kong, n8n, Redis Streams, Redpanda/Kafka** | **CD-125…129** — **event outbox**, API layer, webhook, sync engine, integration monitor; **CD-247** | — | CTO |
| **M29** | Identity, Access & Information Security · `SEC` | W1 | 44 *(est.)* | `base` access control, record rules | **`server-tools`** (auditlog), **`OCA/web`** (Keycloak auth), `operating-unit` | **Keycloak, Wazuh**, Vault | **CD-130…132** — RBAC ext, audit ext, **SoD engine**; **CD-233 residency service**; **CD-248 DSR orchestrator** | — | CTO |
| **M64** | Master Data Management & Configuration · `MDM` | W2 | 26 *(est.)* | `base` | `server-tools` | — | **CD-230** — MDM governance; CD-134 | — | CTO |
| **M65** | Multi-Entity, Multi-Country & Localisation · `GLO` | W9 | 30 *(est.)* | `base` multi-company | **`operating-unit`** | — | **CD-231** — entity localisation; CD-136, CD-137 | — | CTO |
| **M66** | Internal IT Service Management · `ITS` | W6 | 22 *(est.)* | `project` | **`helpdesk_mgmt`** | Wazuh, osquery | **CD-232** *(est.)* | — | CTO |
| **M30** | Platform Administration & Configuration · `ADM` | W1 | 28 *(est.)* | `base` | `server-tools` | Grafana, Prometheus | **CD-133…138** — entity config, MDM, **feature flag**, locale pack, country pack, platform ops | — | CTO |
| **M67** | Project, Program & Portfolio Management · `PPM` | W7 | 26 *(est.)* | **`project`** | — | Metabase | **CD-232** *(est.)* | — | CTO |

> **M66 and M67 have no specification file.** Their technology assignment above is made against the
> **registered module scope in `02-02`**, not against enumerated requirements. Both rows are
> ***(est.)*** and, under rule RG-05, **must not be used for contractual commitment** until the
> specifications exist. This is the only place in this document where technology is assigned without
> a requirement set behind it, and it is disclosed rather than presented as equivalent to the other
> 65 rows. See §25.1.

### 10.13 Coverage Verification — Module Level

**Counted by direct enumeration of §10.2–§10.12 on 13 August 2026:**

| Category | Modules in `02-02` | Rows in this section | Rows with `∅` |
|---|---:|---:|---:|
| A — Service Delivery & Operations | 7 | **7** | 0 |
| B — Customer Engagement & Experience | 7 | **7** | 0 |
| C — Commercial, Pricing & Revenue | 9 | **9** | 0 |
| D — Circular & Asset-Based Business | 3 | **3** | 0 |
| E — Supply Chain & Inventory | 6 | **6** | 0 |
| F — Asset, Equipment & Facilities | 5 | **5** | 0 |
| G — Finance & Treasury | 8 | **8** | 0 |
| H — People & Workforce | 7 | **7** | 0 |
| I — Governance, Risk, Quality & Knowledge | 4 | **4** | 0 |
| J — Data, Analytics & Intelligence | 4 | **4** | 0 |
| K — Platform & Technology | 7 | **7** | 0 |
| **Total** | **67** | **67** | **0** |

### 10.14 Layer Distribution Across the 67 Modules

| Layer | Modules where it contributes | Share of requirements | Comment |
|---|---:|---:|---|
| **L1** Odoo 19 CE | **62 of 67** | ~28% | Absent from **M26, M32, M48, M60, M62** — AI/ML, conversational AI, IoT, GRC and the data platform, for which Odoo has no analogue |
| **L2** OCA | **58 of 67** | ~24% | Absent from M10, M11, M26, M32, M38, M48, M61, M62, M67 |
| **L3** Third-party | **5 of 67** *(at integration level)* | ~4% | M02, M15, M20, M27, M41 — payment, messaging and barcode connectors. **L3 has no column in the §10 tables** because it contributes at the integration layer rather than the module layer; the assignment is in §6.1 and §12.2.4 |
| **L4** Standalone OSS | **42 of 67** | ~17% | Every module needing identity, gateway, notification, storage, routing, time series or analytics |
| **L5** Custom | **67 of 67** | ~25% | **Every module requires custom development.** No module in this programme is pure configuration |
| **L6** Commercial | **5 of 67** | ~2% | **M05, M08, M12, M24, M27** |

*Counted by direct enumeration of the 67 rows in §10.2–§10.12 on 13 August 2026. An earlier draft of
this table stated projected rather than counted figures; the correction is recorded as audit finding
**TSA-01** in Appendix G.*

**The most consequential line in that table is L5 at 67 of 67.** There is no module that can be
delivered by configuration alone. Any delivery plan that assumes a "configuration-only" wave, or an
implementation partner who proposes one, has misread the specification set.

---
## 11. PORTAL & APPLICATION TECHNOLOGY — P01 TO P12

### 11.1 The Portal Principle and the CON-03 Constraint

**The ERP is the system of record. Portals are surfaces onto it.** Four rules follow, and they are
technology constraints, not stylistic preferences:

| Rule | Technology consequence |
|---|---|
| No portal holds authoritative state | A portal may cache for performance, never for truth. Cache invalidation is event-driven from the ERP |
| No portal implements a business rule (PS-11, AS-09) | Client-side validation is for convenience. Every rule is re-evaluated server-side, and the portal contract test verifies this by submitting invalid payloads directly to the API |
| Every portal authenticates through M29 (PS-01) | **No portal maintains a credential store.** Keycloak is the only identity |
| Every portal calls through the M28 gateway (PS-02) | Per-portal credential, per-portal rate limit, per-portal BFF |

#### CON-03 — the portal platform cannot be replaced

The **Next.js 15 + Payload CMS 3** platform already exists and is a hard constraint on this
programme. This stack **integrates with it through a versioned contract** (§12.2.5); it does not
absorb, replace or fork it. Alternative-architecture proposals must honour CON-03 (RFP condition
ALT-04).

> **Version-currency finding — TSA-05.** The specification set fixes the platform at **Next.js 15**.
> As at 13 August 2026 the current stable line is **Next.js 16** (16.2.x), which is the designated
> LTS line, with React 19.2 and a stable React Compiler. **CON-03 constrains the *platform*, not the
> *version*.** Holding six customer-facing web applications on Next.js 15 for the 36-month programme
> duration will place them outside the actively supported line well before Wave 9. The technology
> position recommended here is: **treat the Next.js 15 → 16 upgrade as a Wave 1 platform activity**,
> before six applications are built on it, rather than as a Wave 8 migration of six applications at
> once. This is raised as a change in §25.3 and does not breach CON-03 — the platform remains Next.js
> + Payload CMS. Payload CMS 3 compatibility with Next.js 16 must be confirmed in Wave 0 as a
> blocking check.

### 11.2 Suite Technology Overview

| ID | Portal / application | Users | Volume | **Technology** | Offline | Wave | APP |
|---|---|---|---|---|:--:|:--:|---|
| **P01** | Customer Self-Service Portal & Mobile App | Individual customers | 250,000+/month | **Next.js 15→16 + Payload CMS 3** (web, PWA) · **Flutter** (native app) | PWA shell + cached read | W2 / W6 | APP-05, APP-04 |
| **P02** | Technician Mobile Application | Field & workshop technicians | 200–400 | **Flutter** (Android primary, iOS secondary) | **24 h full** | W2 | APP-01 |
| **P03** | Admin Operations Portal | Back-office & branch staff | 150–250 | **Odoo Web (OWL 2)** — 14 role-scoped workspaces | — | W1 | — |
| **P04** | Corporate B2B Portal | Corporate & government clients | 500–2,000 | **Next.js 15→16** | — | W4 | APP-06 |
| **P05** | Vendor & Supplier Portal | Vendors, couriers, sub-contractors | 200–500 | **Odoo Portal** (`website` + `portal`) + selective Next.js | — | W3 | — |
| **P06** | Analytics & Executive Dashboard | Management | 25–60 | **Metabase** (analytical) + **Grafana** (real-time), embedded | — | W4 | — |
| **P07** | Marketplace Seller Portal & App ★ | External engineers & shops | 500–2,000 | **Next.js 15→16** + mobile surface — see §11.9 | — | W7 | APP-09 |
| **P08** | Brand Partner Portal ★ | 17+ brand partners | 50–150 | **Next.js 15→16** | — | W4 | APP-07 |
| **P09** | Logistics & Rider Application ★ | Riders, coordinators, courier staff | 50–200 | **Flutter** (rider) + Odoo Web (coordinator) | **24 h full** | W3 | APP-02 |
| **P10** | Contact Centre Agent Console ★ | Agents & supervisors | 30–80 | **Next.js 15→16** + WebRTC/SIP client | — | W4 | APP-08 |
| **P11** | Field Auditor & Quality Application ★ | Quality auditors, branch managers | 20–60 | **Flutter** | **24 h full** | W5 | APP-03 |
| **P12** | Partner & Referral Portal ★ | Alliance partners, referrers, resellers | 100–500 | **Next.js 15→16** | — | W7 | APP-10 |

**Count verified 13 August 2026 — 12 portals, all with assigned technology.**

### 11.3 P01 — Customer Self-Service Portal & Mobile Application

**Wave 2 (web) / Wave 6 (native app) · Backing modules: M01, M02, M03, M06, M07, M08, M09, M10, M11,
M12, M13, M14, M18, M20, M27, M33, M34, M38**

| Layer | Technology |
|---|---|
| Web | **Next.js 15→16 + Payload CMS 3 + React 19** — CON-03 platform. Server components for catalogue and content; client components for booking, tracking and payment |
| Native app | **Flutter (APP-04)** — shared offline and sync patterns with APP-01 |
| Content | **Payload CMS 3** owns marketing content, pages, blog and SEO; the ERP owns everything transactional (§12.2.5 field ownership) |
| API | Kong → Customer API family `/api/v1/customer/*`, customer-scoped OAuth 2.0 user token |
| Real-time | Webhook push from the ERP with **polling fallback** — the tracking page must work if webhooks fail |
| Identity | Keycloak — phone/email OTP, social login, biometric login on the native app |
| Payments | SSLCOMMERZ, bKash, Nagad connectors (INT-001…003) via the L3 modules or L5 wrappers per §6.2 |
| Maps | Google Maps Platform for display (INT-019); technician position from Traccar via the ERP |
| Notification | Novu — push (FCM/APNs), SMS, WhatsApp, email, in-app inbox |
| Assistant | Ollama-backed assistant (M32) with human handoff to P10 |
| Consent | **PDPA consent management (CD-148)** — granular, per-purpose, withdrawable |

**Performance and delivery constraints that shape the build:**

| Constraint | Target | Technology response |
|---|---|---|
| First load on the booking path | **< 400 KB** (PS-07, NFR-081) | Server components, route-level code splitting, no client-side chart libraries on the booking path, WebP/AVIF images, self-hosted Bengali subset fonts |
| Works on 3G | Required | Streaming SSR, skeleton states, aggressive edge caching of catalogue and branch data |
| Booking in ≤ 3 steps | Required | Slot availability computed server-side ≤ 800 ms p95 (NFR-032) |
| PWA | Offline shell, installable | Service worker caching the shell, catalogue and the customer's open orders |
| Public tracking without login | Required | Signed, expiring tracking token — no session, no PII beyond the order's own status |
| WCAG 2.1 AA | Contracted (PS-04) | Automated axe scan in CI + manual audit per release |

### 11.4 P02 — Technician Mobile Application

**Wave 2 · Flutter · The hardest deliverable in the programme · Backing modules: M01, M02, M03, M05,
M06, M13, M14, M15, M17, M21, M22**

| Layer | Technology |
|---|---|
| Framework | **Flutter** — Android primary, iOS secondary. TD-03 |
| Local store | **Encrypted SQLite** (SQLCipher) with an **append-only action journal** (AS-13) |
| Sync | CD-015 `cd_offline_sync` + CD-128 `cd_sync_engine` — see §16 in full |
| Location | Traccar client integration; batched, battery-aware position reporting |
| Navigation | Handoff to the device's map application; route overview rendered in-app from OSRM geometry |
| Evidence | Camera with GPS and timestamp binding; local encryption; deferred upload to MinIO |
| Scanning | Barcode/QR via device camera for van stock and custody |
| Signature | On-device capture, bound to job and GPS (CD-108 operational signature — not the L6 service) |
| Payment | On-site collection via bKash/Nagad SDK handoff; receipt generation offline, reconciled on sync |
| Push | FCM (Android) / APNs (iOS) via Novu |
| Knowledge | Offline repair manuals and past repair notes, synced by device model relevance |
| Language | **Bengali-first, complete — including every error message** (AS-12) |

**The seven non-negotiables (from `04-00` P02) and how the technology meets each:**

| # | Requirement | Technology response |
|---|---|---|
| 1 | Full operation offline for **24 hours** with no data loss | Append-only journal in encrypted SQLite; every action is a discrete idempotent command with a client-generated UUID |
| 2 | Sync within **30 seconds** of reconnection with 100% integrity | Delta sync from a server-issued token; batched with per-batch checksums; failed batches retried whole, **never partially applied** |
| 3 | Complete Bengali UI | Full `.arb` localisation; translation completeness gate at 100% in CI |
| 4 | Runs on mid-range **Android 11, 3 GB RAM** | Impeller renderer; bounded working set; image downscaling on capture; no unbounded in-memory lists |
| 5 | Battery **≤ 12% per 8-hour shift** excluding navigation (NFR-082) | Adaptive location sampling, batched network, deferred non-critical uploads (FR-FSM-061, FR-FSM-062) |
| 6 | Every state-changing action queued locally and **idempotent** on the server | `Idempotency-Key` on every command (API-07); server records processed UUIDs |
| 7 | **No feature requires a connection** a technician cannot complete offline | Feature-by-feature offline audit is a release gate; any online-only feature must be justified and flagged in-app before the technician relies on it |

### 11.5 P03 — Admin Operations Portal

**Wave 1 · Odoo Web (OWL 2) · Backing modules: all 67**

Delivered as **14 role-scoped workspaces** inside the Odoo web client, each opening on the work its
role actually does — not as a generic menu tree.

| Workspace | Role | Opens on | Key technology |
|---|---|---|---|
| Service Intake | R08 Service Centre Agent | Queue, quick intake, customer search | OWL 2, keyboard-first; NFR-076 ≤ 3 min intake |
| **Dispatch Console** | R07 Dispatch Manager | Live map, unassigned queue, technician load, SLA risk | **Traccar + OSRM live map, VROOM suggestions**; NFR-033 ≤ 1 s refresh at 500 open jobs |
| Branch Console | R06 Branch Manager | Today's numbers, WIP ageing, cash, staff | `operating-unit` scoping |
| Workshop Console | R09 Workshop Supervisor | Bench board, WIP by state, parts holds | CD-140 WIP board |
| Inventory Console | R17 Inventory Manager | Network stock, alerts, transfers, counts | `stock-logistics-*` |
| Procurement Console | R19 Procurement Officer | Requisitions, POs, receipts, vendor performance | `purchase-workflow` |
| Finance Console | R26/R27 | Invoices, receipts, reconciliation, ageing, close checklist | `account`, `mis-builder` |
| HR Console | R30/R31 | Attendance exceptions, leave, payroll run, incentives | `OCA/hr`, `OCA/payroll` |
| Quality Console | R32 Quality Manager | NCRs, CAPAs, complaints, audits | `management-system` |
| Contract Console | R22 Account Manager | Contract base, renewals, entitlements, profitability | `OCA/contract` |
| Warranty Console | R28 Warranty Officer | Claim pipeline, ageing, rejections, reconciliation | CD-043, n8n |
| Marketplace Console | R24 Marketplace Ops | Seller approvals, disputes, scores, payouts | CD-053…057 |
| Managed Services Console | R13 / MSP Ops | Estate health, alerts, tickets, SLA, patch compliance | Wazuh, Grafana embed |
| System Console | R33 IT Administrator | Users, roles, configuration, jobs, integrations, health | Keycloak admin bridge, Grafana |

**Design constraints:** every workspace one click from home; any record in **≤ 4 clicks** (NFR-077);
bulk actions on every list; **keyboard-first** for intake, dispatch and finance; screen density tuned
for **1366×768** — the most common branch hardware, not a design assumption but a measured fact about
the estate.

### 11.6 P04 — Corporate B2B Portal

**Wave 4 · Next.js 15→16 · Backing modules: M05, M07, M08, M09, M11, M17, M20, M25, M27**

| Capability area | Technology |
|---|---|
| Multi-user corporate account with approval chains | Keycloak group hierarchy per corporate account + CD-034 approval-chain configuration |
| **Client SSO federation** | **Keycloak identity brokering — per-client SAML 2.0 / OIDC (INT-046)**. A corporate client's staff sign in with their employer's credentials |
| Asset estate management with bulk upload | M17 asset registry; CSV/XLSX ingest with validation and preview |
| Bulk service requests | Bulk CSV upload validated against contract coverage **before** submission — NFR: ≤ 5 min for a bulk request |
| Contract, entitlement and consumption view | `OCA/contract` + CD-038 entitlement engine |
| Managed-services estate dashboard | Grafana embed scoped by row-level security to the client's estate |
| Consolidated billing with dispute | CD-090 billing engine; invoice approval workflow |
| Scoped analytics with export | **Metabase embed with row-level security** — a client sees only their own estate, enforced server-side |
| Compliance evidence packs | Mayan EDMS retrieval of destruction and disposal certificates |

**The security-critical element is row-level security on the analytics embed.** A corporate client
must never see another client's data through a dashboard filter. This is enforced by signed embedding
parameters carrying the client scope, validated server-side — never by a client-side filter (API-10).

### 11.7 P05 — Vendor & Supplier Portal

**Wave 3 · Odoo Portal (`website` + `portal`) with selective Next.js · Backing modules: M03, M15,
M16, M18, M20**

The only portal delivered primarily on the **Odoo portal framework** rather than Next.js. The
rationale: P05's surface is close to Odoo's native record model (POs, receipts, invoices, RFQs), its
user population is 200–500 rather than hundreds of thousands, and its interactions are transactional
rather than experiential. Building it in Next.js would add an integration layer for no user benefit.

| Capability | Technology |
|---|---|
| Onboarding, documents, approval tracking | Odoo portal + `OCA/dms` |
| RFQ receipt and quotation submission | `purchase-workflow` + CD-073 |
| PO acknowledgement, ASN, delivery confirmation | `purchase` + portal record rules |
| Invoice submission and three-way match status | `account` + CD-200 |
| Vendor scorecard | CD-173, rendered from Metabase |
| Logistics partner consignment updates and POD upload | CD-018 courier module + MinIO |
| Recycling partner disposal certificates | CD-081 + Mayan EDMS |

### 11.8 P06 — Analytics & Executive Dashboard

**Wave 4 · Metabase + Grafana, embedded · Backing module: M25 (data from all 67)**

| Surface | Technology | Answers |
|---|---|---|
| Executive performance across 14 revenue streams | **Metabase** on certified datasets | "What happened and why?" |
| Branch league table across 51+ branches | Metabase, `operating-unit` dimension | "Who is performing?" |
| Functional dashboards (service, field, inventory, finance, HR, quality, warranty, contracts, marketplace, MSP) | Metabase | "How is my function doing?" |
| **Real-time operations board** — open jobs, technicians on map, SLA countdowns, queue health, system health | **Grafana** on Prometheus + TimescaleDB | "What is happening right now?" |
| Self-service analysis without SQL | Metabase question builder on certified datasets **within row-level security** | "Let me look myself" |
| Scheduled distribution and export | Metabase subscriptions → PDF/Excel/CSV | |
| Threshold and anomaly alerting | Grafana alerting + CD-110 metric registry | |
| Mobile dashboards | Metabase responsive views | |

**Data path:** PostgreSQL read replica through Wave 7 → **ClickHouse from Wave 8** via CD-243 (dbt).
Executive dashboard load target **≤ 5 s** (NFR-038); warehouse analytical query **≤ 10 s p95**
(NFR-039).

### 11.9 P07 — Marketplace Seller Portal & Application ★

**Wave 7 · Next.js 15→16 · Backing modules: M11, M12, M15, M20, M22, M23, M27**

| Capability | Technology |
|---|---|
| Registration with NID, trade licence, references, work samples | CD-053 seller module + **L6 KYC verification (TC-072)** + **residency service CD-233** — seller KYC documents are residency-classified under NFR-086 |
| OTP verification, approval tracking, digital agreement | Keycloak OTP + **L6 qualified e-signature (TC-071)** for the seller agreement |
| Listings, pricing, availability, bulk management | CD-054 listing module |
| Broadcast job matching, quotation, counter-bid | CD-055 job module + CD-050 bidding |
| Customer chat on open jobs | Novu + WebSocket chat infrastructure (INT-018) |
| Wallet, earnings, commission breakdown, payout request | **CD-057 commission + CD-242 settlement engine** |
| Performance scorecard with automatic visibility reduction | CD-056 review + CD-053 scoring |
| Boost and advertising purchase with impressions/clicks | CD-058 advertising + INT-037 |
| Disputes with evidence | CD-055 + MinIO |

> **Open item — the P07 mobile surface. TSA-06.** The source documents disagree. `04-00` §2 specifies
> "Next.js 15 + React Native"; `02-05` §5.4 lists only four Flutter applications and places P07 in
> the Next.js group; RFP §7.2 states "Next.js 15 + mobile" without naming a framework. **Three
> different positions across three documents.** The technology position recommended here is:
> **deliver P07's mobile surface as a Progressive Web App on the Next.js codebase in Wave 7**, and
> treat a native seller app as a separately approved item in Wave 8 or later, **built in Flutter if
> approved** so the estate carries one mobile framework rather than two. Introducing React Native
> alongside Flutter would mean two mobile toolchains, two offline engines, two CI pipelines and two
> skill sets for one additional application. **This is a decision required — see §25.3.**

### 11.10 P08 — Brand Partner Portal ★

**Wave 4 · Next.js 15→16 · Backing modules: M09, M15, M17, M23, M25**

| Capability | Technology |
|---|---|
| Claim receipt with full evidence packs; approve / part-approve / reject / request info | CD-043 claim automation + MinIO evidence retrieval |
| Evidence viewing — photographs, diagnostic reports, parts, technician certification, purchase proof | MinIO + CD-102 certification lookup |
| Reconciliation — submitted, approved, paid; remittance upload | CD-044 claim reconcile |
| Consignment parts visibility and replenishment | CD-069 consignment stock |
| Rate-card publication and versioning | CD-048 price book |
| Service performance on their brand — volume, TAT, first-time fix, rework, CSAT, failure patterns | **Metabase embed, row-level security scoped to the brand** |
| Quality concerns, CAPA responses, partner audits | `management-system` + CD-105 |
| Bulletins, technical notices, recall notifications | Novu + CD-224 knowledge article |

**17+ brand partners each require a different claim submission format.** The transformation layer is
**n8n**, not code (§3.6.3), so that adding or changing a brand template is configuration rather than
a release.

### 11.11 P09 — Logistics & Rider Application ★

**Wave 3 · Flutter (rider) + Odoo Web (coordinator) · Backing modules: M03, M13, M14, M15, M18**

| Capability | Technology |
|---|---|
| Daily optimised manifest | VROOM + OSRM via CD-236 |
| Collection — scan, verify against manifest, photograph items and packaging, seal number, **customer OTP + signature**, receipt | Flutter camera + barcode + CD-108 signature + CD-017 custody |
| Transit status and exceptions | Offline queue; CD-016 consignment |
| Delivery — recipient verification, handover scan, photo, OTP, signature, payment collection | Same stack as collection |
| **Unbroken custody** — every handover with GPS, timestamp and both parties' identity | **CD-017 `cd_custody`** — the custody chain is an append-only ledger, not a status field |
| Cash on delivery reconciliation per rider per shift | CD-020 logistics charge + CD-022 cash drawer |
| **Full offline operation** | Same offline engine as APP-01 (§16) |
| Coordinator dashboard (web) | Odoo Web workspace — real-time consignment board, assignment, SLA monitoring |

### 11.12 P10 — Contact Centre Agent Console ★

**Wave 4 · Next.js 15→16 + WebRTC/SIP · Backing modules: M01, M05, M07, M08, M09, M11, M20, M23, M27**

| Capability | Technology |
|---|---|
| Unified queue across voice, chat, WhatsApp, email, SMS, social | **Novu inbound routing + CD-119 conversation + CD-124 inbox** |
| Voice — answer, hold, transfer, conference, consult, recording | **L6 cloud telephony (TC-070)** with a WebRTC/SIP client in the console; CD-120 telephony bridge |
| **Screen pop of Customer 360 on caller identification** | CD-121 agent console + Customer API; NFR-031 ≤ 2 s load |
| Full cross-channel conversation history | CD-119 |
| Act without leaving the conversation — create order, reschedule, quote, take payment, renew, raise complaint | CD-121 embedding ERP actions; **< 3 screen switches per contact** |
| Remote support launch with consent capture | MeshCentral/RustDesk (INT-028) + consent record |
| **AI assist** — suggested responses, next-best-action, article recommendations, live | **Ollama** via CD-245 inference gateway; CD-122 assistant |
| Wrap-up, disposition coding, follow-up creation | CD-119 |
| Quality — recording playback, scoring forms, coaching notes | L6 telephony recording + `management-system` |
| Supervision — live queue, agent status, barge-in, whisper | L6 telephony supervisor API + Grafana |

### 11.13 P11 — Field Auditor & Quality Application ★

**Wave 5 · Flutter · Backing modules: M15, M17, M23, M24**

| Capability | Technology |
|---|---|
| Assigned audits, schedule, scope, checklist | CD-106 `cd_audit_mobile` |
| **Offline checklist completion with photo and document evidence** | Same offline engine as APP-01 (§16) |
| Findings with classification, severity, linkage, owner assignment | `management-system` NCR model |
| On-site CAPA verification | `management-system` |
| Branch checks — cash spot check, inventory spot count, equipment, safety, 5S | CD-070 cycle count + CD-022 cash drawer + CD-220 safety compliance |
| Marketplace seller audit against platform standards | CD-053 seller + `management-system` |
| **Audit report generated on device with auditee acknowledgement signature** | On-device PDF generation + CD-108 operational signature; synced to M23 |

### 11.14 P12 — Partner & Referral Portal ★

**Wave 7 · Next.js 15→16 · Backing modules: M10, M12, M14, M20**

| Capability | Technology |
|---|---|
| Onboarding, document submission, partner agreement signature | Keycloak + **L6 e-signature (TC-071)** |
| Referral link/code generation, lead submission, conversion tracking | **CD-168 `cd_referral`** — attribution is permanent (FR-CRM-048) |
| Partner benefit schedule | CD-046 voucher + CD-167 partner program |
| Commission earned, statements, payout schedule and history | **CD-169 channel settlement + CD-242 settlement engine** |
| Co-marketing materials and campaign performance | Payload CMS asset library + CD-154 attribution |
| Reseller — refurbished stock allocation, pricing, orders, fulfilment, settlement | CD-066 resale + CD-161 storefront API |
| Performance — leads, conversion, revenue attributed, ranking | Metabase embed, partner-scoped |

### 11.15 Cross-Portal Technology Standards

Every standard below is realised by a named technology and verified in CI.

| # | Standard | Technology realisation | Verified by |
|---|---|---|---|
| **PS-01** | SSO through M29; no local credential store | Keycloak OIDC; no portal has a user table | Architecture review; credential-store scan in CI |
| **PS-02** | All API traffic through the M28 gateway with per-portal credentials and rate limits | Kong consumer per portal; direct-to-Odoo network path blocked at Z2 | Network policy test |
| **PS-03** | Bengali and English throughout, **Bengali default** on customer and field surfaces | `next-intl` (web) / `.arb` (Flutter) / Odoo `.po`; ICU `bn-BD` collation | Translation completeness report at 100% |
| **PS-04** | WCAG 2.1 AA | axe-core automated scan in CI + manual audit per portal release | Accessibility gate per release |
| **PS-05** | Responsive from 320 px, no horizontal scrolling | Shared design system breakpoints | Visual regression suite |
| **PS-06** | One design system — one component library, one token set across all 12 | **Shared token package consumed by Next.js, Flutter and Odoo OWL themes** | Design-system conformance lint |
| **PS-07** | Works on 3G; critical paths **< 400 KB** first load (P01, P02, P07, P09) | Bundle budget enforced in CI; build fails on breach | Bundle-size gate |
| **PS-08** | Offline-capable with queued sync (P02, P09, P11) | Shared Flutter offline engine (§16) | Offline test suite |
| **PS-09** | Every error states what happened and what to do next, in the user's language | Standard error envelope (API-04) with localised `message`; no raw exception surfaces | Error-catalogue review |
| **PS-10** | Analytics instrumentation on every critical funnel, feeding M25 | Event instrumentation → CD-110 metric registry → Metabase | Funnel coverage check |
| **PS-11** | **No business rule client-side**; client validation is convenience only | **Portal contract test submits invalid payloads directly to the API and asserts server-side rejection** | Contract test in CI |
| **PS-12** | Session, idle timeout and MFA policy inherited from M29, never portal-specific | Keycloak session policy; no portal-local session config | Configuration audit |

**PS-11's verification method is the one that matters.** It is easy to write "no business rule
client-side" and then implement a rule in a React form because it produces better UX. The contract
test defeats this by bypassing the UI entirely: it posts an invalid payload to the API and fails the
build if the server accepts it. Without that test, PS-11 is an aspiration.

---

## 12. CROSS-CUTTING PLATFORM TECHNOLOGY

### 12.1 Identity, Access and Authorisation

#### 12.1.1 Component stack

| Concern | Technology | Layer |
|---|---|---|
| Identity provider, SSO, MFA, step-up, federation | **Keycloak 26.x** (TC-015) | L4 |
| Odoo authentication bridge | `OCA/web` Keycloak/OIDC auth modules | L2 |
| Record-level access rules | Odoo `ir.rule` + `OCA/operating-unit` | L1 + L2 |
| Field-level permissions | **CD-130 `cd_rbac_ext`** | L5 |
| Segregation of duties | **CD-132 `cd_sod`** | L5 |
| Immutable audit trail | `OCA/server-tools` `auditlog` + **CD-131 `cd_audit_ext`** | L2 + L5 |
| Secrets | **Vault** — never in code, configuration or logs (NFR-062, IP-07) | L4 |
| Privileged session recording | Bastion session recording (NFR-070) | L4 |

#### 12.1.2 The 46 roles

| Group | Roles | Count | Portals |
|---|---|---:|---|
| Executive & management | R01 CEO · R02 CTO · R03 CFO · R04 CCO · R05 Operations Director | 5 | P03, P06 |
| Service operations | R06 Branch Manager · R07 Dispatch Manager · R08 Service Centre Agent · R09 Workshop Supervisor · R10 Senior Technician · R11 Junior Technician · R12 Specialist (L3) Technician · R13 Remote Support Engineer · R14 Data Services Technician | 9 | P02, P03, P06, P10, P11 |
| Logistics & supply chain | R15 Logistics Coordinator · R16 Rider · R17 Inventory Manager · R18 Branch Store Keeper · R19 Procurement Officer · R20 Warehouse Operative | 6 | P03, P05, P06, P09 |
| Commercial | R21 Sales Manager · R22 Account Manager · R23 Marketing Manager · R24 Marketplace Operations · R25 Retail/Refurbishment Officer | 5 | P03, P04, P06, P07, P12 |
| Finance, people & governance | R26 Finance Manager · R27 Finance Officer · R28 Warranty Claims Officer · R29 Cashier · R30 HR Manager · R31 HR Officer · R32 Quality Manager | 7 | P03, P05, P06, P08, P11 |
| Technology & support | R33 IT Administrator · R34 Contact Centre Agent · R35 Contact Centre Supervisor | 3 | P03, P06, P10 |
| External | R36 Customer · R37 Corporate Portal User · R38 External Party | 3 | P01, P04, P05, P07, P08, P09, P12 |
| **Registered subtotal** | | **38** | |
| **In use but unregistered** ⚠ | R39 Data Steward · R40 Chief Data Officer · R41 Payroll Officer · R42 Training Coordinator · R43 Competency Assessor · R44 HSE Officer · R45 Recruiter · R46 Occupational Health | **8** | P03, P06, P11 |
| **Total in use** | | **46** | |

> **Disclosed defect — inherited, and it is a live permission defect.** Eight roles (R39–R46) are
> used in module specifications but are **not in the role register**. Separately, **R60 is a
> duplicate identity for R32 Quality Manager**, and R54 and R57 are referenced with no definition.
> **A duplicate role identity means an access rule written against R32 does not apply to a user
> granted R60.** The technology consequence is direct: **Keycloak realm roles and Odoo groups must
> be built on 46 roles with R60 eliminated and R54/R57 resolved, as Wave 1 scope.** Building on 38
> roles and adding eight later means retrofitting record rules and field permissions across live
> data. See §25.1 and RFP §20.2.4.

#### 12.1.3 Data isolation tiers

| Tier | Visibility | Mechanism | Examples |
|---|---|---|---|
| **T0 Global** | All authenticated internal users | No record rule | Service catalogue, parts catalogue, brand/model master, checklist templates, knowledge base, branch directory |
| **T1 Company** | Within the legal entity | `company_id` rule | Company-wide configuration, group policies |
| **T2 Operating unit** | Within the branch or business unit | **`operating_unit_id` rule via `OCA/operating-unit`** | Branch service orders, branch stock, branch cash |
| **T3 Team / zone** | Within the assigned team or geographic zone | `zone_id` / team membership rule | Dispatch zone queues, technician team scorecards |
| **T4 Owner** | The record's owner and their management line | Owner + hierarchy rule | Own jobs, own leave, own expenses, own performance |
| **T5 Restricted** | Explicit grant only, **access logged, step-up authentication** | **Named allow-list + audit + step-up (NFR-065)** | Individual payroll, NID records, bank details, data-recovery case content, call recordings, audit logs, biometric templates, seller KYC documents |

**T5 is where the split-residency boundary and the isolation model coincide.** Almost every T5 data
class is also residency-classified under NFR-086. The technology consequence: **a T5 read is a call
to the residency service (CD-233), which performs the step-up check, logs the access, and returns the
field** — it is never a direct database read. This gives one enforcement point and one audit point.

#### 12.1.4 Segregation of duties

**30 SoD controls (SOD-01…SOD-30)** enforced by **CD-132 `cd_sod`** at the permission engine
(NFR-064), evaluated at **role assignment time**, not at transaction time — so a conflicting
assignment is refused rather than a conflicting transaction being blocked after the fact.

| Control class | Examples | Enforcement |
|---|---|---|
| Financial | The user who creates a vendor cannot approve a payment to it; the user who raises a credit note cannot approve it | Hard block at role assignment; override requires named approval and is logged |
| Inventory | The user who performs a stock count cannot approve its variance adjustment | Hard block |
| HR & payroll | The user who maintains employee bank details cannot approve the payroll run | Hard block |
| Access | The user who grants a role cannot grant it to themselves | Hard block |
| Quality | The user who performs work cannot sign its own QC | Hard block |
| Marketplace | The user who approves a seller cannot approve that seller's payout | Hard block |

> **Disclosed defect — inherited.** **SOD-13 through SOD-30 are used but unregistered** in `05-04`.
> The 30 controls are named in the specification set but only 12 are formally registered. **CD-132
> must implement all 30**; completion of the register to SOD-30 is Wave 1 scope. See §25.1.

#### 12.1.5 Access lifecycle

| Event | Trigger | Technology | Target |
|---|---|---|---|
| Joiner | `employee.joined` from M21 | Keycloak provisioning via CD-130 | Access active on day one |
| Mover | Role change in M21 | Old role revoked and new granted **in one transaction** — never additive | No accumulated privilege |
| Leaver | `employee.left` from M21 | **Keycloak deprovisioning ≤ 1 hour**, device access revoked (FR-FSM-064) | **Zero orphaned accounts beyond 24 h (KPI-090)** |
| Recertification | Quarterly | CD-130 attestation workflow | Every privileged role re-attested by its owner |

### 12.2 Integration and API Platform

#### 12.2.1 Component stack

| Concern | Technology | Layer |
|---|---|---|
| API gateway | **Kong 3.x** (TC-016) | L4 |
| Event outbox | **CD-125 `cd_event_outbox`** — writes in the same DB transaction as the state change (AS-08) | L5 |
| Event bus | **Redis Streams** (W1–W5) → **Redpanda/Kafka** (W6+) | L4 |
| Orchestration | **n8n 1.x** (TC-017) | L4 |
| Webhook delivery | **CD-127 `cd_webhook`** with retry, signature and dead-letter | L5 |
| Integration monitoring | **CD-129** + Grafana + Prometheus | L5 + L4 |
| API specification | **OpenAPI 3.1**, generated from code, validated in CI (AS-07, API-03) | — |

#### 12.2.2 The twelve API families

| Family | Base path | Consumers | Auth |
|---|---|---|---|
| Customer | `/api/v1/customer/*` | P01, P04, assistant | OAuth 2.0 user token, customer-scoped |
| Technician | `/api/v1/technician/*` | P02 | OAuth 2.0 + PKCE, technician-scoped |
| Operations | `/api/v1/ops/*` | P03, P10 | OAuth 2.0 staff token, role-scoped |
| Corporate | `/api/v1/corporate/*` | P04 | OAuth 2.0, corporate-account-scoped |
| Vendor | `/api/v1/vendor/*` | P05 | OAuth 2.0, vendor-scoped |
| Seller | `/api/v1/seller/*` | P07 | OAuth 2.0, seller-scoped |
| Brand | `/api/v1/brand/*` | P08 | OAuth 2.0, brand-scoped |
| Logistics | `/api/v1/logistics/*` | P09 | OAuth 2.0, rider/coordinator-scoped |
| Analytics | `/api/v1/analytics/*` | P06, embedded dashboards | OAuth 2.0 + **row-level security context** |
| Admin | `/api/v1/admin/*` | P03 system console | OAuth 2.0 + **MFA + step-up** |
| Partner | `/api/v1/partner/*` | P12, external partners | OAuth 2.0 client credentials |
| Webhook receiver | `/hooks/v1/*` | External systems | **Signature verification** |

#### 12.2.3 API standards and their enforcement

| # | Standard | Enforced by |
|---|---|---|
| API-01 | REST over HTTPS with JSON; GraphQL only through the federation layer for composed portal reads | Architecture review |
| API-02 | Versioned in path; minimum two concurrent versions; six months' deprecation notice | Kong route configuration; deprecation register |
| API-03 | OpenAPI 3.1 generated from code, validated in CI, published to the developer portal | CI gate |
| API-04 | Standard error envelope: `code`, localised `message`, `details`, `correlation_id` | Shared error middleware |
| API-05 | Cursor-based pagination on all collections with enforced maximum page size | Shared pagination library |
| API-06 | Filtering, sorting, sparse field selection on all collections | Shared query library |
| API-07 | **`Idempotency-Key` required on all state-changing operations** | Gateway rejects state-changing requests without it |
| API-08 | Rate limits per consumer with `X-RateLimit-*` headers; 429 with `Retry-After` | Kong plugin |
| API-09 | Every response carries a `correlation_id` | Gateway injection + OpenTelemetry propagation |
| API-10 | **No endpoint returns data outside the caller's authorisation scope, ever — enforced server-side** | Contract test per family; negative tests per role (DoD-07) |
| API-11 | Bengali and English error/validation messages driven by `Accept-Language` | Shared i18n middleware |
| API-12 | Payload size limits enforced; large exports go through an async job with a download link | Gateway + export service |

**Performance targets (from `05-03` §5.3), enforced at wave gates:**

| Endpoint class | p50 | p95 | p99 |
|---|---|---|---|
| Status / lookup reads | 80 ms | 250 ms | 500 ms |
| Standard reads with joins | 150 ms | 400 ms | 800 ms |
| Writes | 200 ms | 500 ms | 1,000 ms |
| Search | 200 ms | 600 ms | 1,200 ms |
| Availability calculation | 300 ms | 800 ms | 1,500 ms |
| Analytics queries | 1 s | 5 s | 10 s |

#### 12.2.4 The 47 external integrations — technology assignment

Every integration has a named client technology, a pattern, and — for P0 — a **tested manual
fallback** (NFR-050, IP-09).

**Payments (INT-001…009)**

| ID | Integration | Client technology | Pattern | Wave | Pri | Fallback |
|---|---|---|---|:--:|:--:|---|
| INT-001 | bKash | L3 connector or L5 wrapper (§6.2) | Sync + webhook | W3 | **P0** | Alternative gateway; cash at counter; link resent |
| INT-002 | Nagad | L3 connector or L5 wrapper | Sync + webhook | W3 | **P0** | As above |
| INT-003 | SSLCOMMERZ | L3 connector or L5 wrapper | Sync + webhook | W3 | **P0** | As above |
| INT-004 | Rocket (via aggregator) | L5 wrapper | Sync | W3 | P1 | Alternative gateway |
| INT-005 | Bank BEFTN | **CD-100 `cd_beftn`** | Batch file | W5 | **P0** | Manual bank-portal submission |
| INT-006 | Bank statement import | CD-194 | Batch/API | W3 | **P0** | Manual statement upload |
| INT-007 | Seller payout rail | **CD-242 settlement engine** | Batch + API | W7 | P1 | Manual disbursement file |
| INT-008 | International gateway (Stripe/PayPal) | L5 wrapper | Sync + webhook | W9 | P3 | Deferred capability |
| INT-009 | Instalment / BNPL partner | L5 wrapper | Sync + webhook | W8 | P3 | Full-payment only |

**Communications (INT-010…018)**

| ID | Integration | Client technology | Pattern | Wave | Pri | Fallback |
|---|---|---|---|:--:|:--:|---|
| INT-010 | BD SMS gateway (primary) | L3 connector via **Novu** | Sync | **W1** | **P0** | Failover gateway; WhatsApp; push; queue |
| INT-011 | BD SMS gateway (failover) | Novu channel | Sync | W2 | P1 | Primary gateway |
| INT-012 | WhatsApp Business Cloud API | L3 connector via Novu | Sync + webhook | **W1** | **P0** | SMS; email; in-app inbox |
| INT-013 | Email (SMTP/API + IMAP) | Odoo `mail` + Novu | Sync + IMAP | **W1** | **P0** | Alternative relay |
| INT-014 | Push (FCM / APNs) | Novu + Flutter SDK | Sync | W2 | **P0** | **SMS fallback for critical messages** |
| INT-015 | Cloud telephony / IVR | **L6 CPaaS (TC-070)** + CD-120 | SIP + API + webhook | W4 | P1 | Divert hotline to mobiles with manual logging |
| INT-016 | WebRTC video | WebRTC in P10/P01 | Sync | W6 | P3 | Voice + screenshare |
| INT-017 | Social messaging (Messenger, IMO) | Novu channel | Webhook | W6 | P3 | Other channels |
| INT-018 | In-app chat infrastructure | WebSocket + Redis pub/sub | WebSocket | W4 | P1 | Async message thread |

**Location, mapping & logistics (INT-019…027)**

| ID | Integration | Client technology | Pattern | Wave | Pri | Fallback |
|---|---|---|---|:--:|:--:|---|
| INT-019 | Google Maps Platform | Maps SDK / REST | Sync | W2 | **P0** | Cached geocodes; OSRM-only routing; manual address entry |
| INT-020 | **OSRM (self-hosted)** | TC-021 | Sync | W2 | P1 | Straight-line distance |
| INT-021 | **VROOM (self-hosted)** | TC-022 | Sync | W2 | P1 | Manual sequencing |
| INT-022 | Traffic data API | L5 wrapper | Sync | W2 | P2 | Historical travel times |
| INT-023 | **Traccar GPS server** | TC-020 REST + WebSocket | Bidirectional | W2 | **P0** | Last known position; manual status updates |
| INT-024 | Courier — Pathao | CD-018 `cd_courier` | REST + webhook | W3 | P2 | Manual booking |
| INT-025 | Courier — RedX | CD-018 | REST + webhook | W3 | P2 | Manual booking |
| INT-026 | Courier — Steadfast/Sundarban | CD-018 | REST + webhook | W3 | P2 | Manual booking |
| INT-027 | International freight forwarder | CD-179 | API / file | W9 | P3 | Manual documentation |

**Remote support & monitoring (INT-028…033)**

| ID | Integration | Client technology | Pattern | Wave | Pri | Fallback |
|---|---|---|---|:--:|:--:|---|
| INT-028 | Remote desktop | **RustDesk / MeshCentral (TC-031)** | API | W5 | P1 | Third-party tool with consent capture |
| INT-029 | Monitoring agent telemetry | **Wazuh (TC-032)** + CD-244 | Agent push | W5 | P1 | Manual estate check |
| INT-030 | SNMP / ICMP collector | CD-244 | Poll | W5 | P1 | Manual device check |
| INT-031 | Patch feed / update catalogue | CD-029 | Sync | W6 | P2 | Manual patch list |
| INT-032 | Endpoint protection console | CD-244 | API | W6 | P2 | Manual status report |
| INT-033 | Cloud provider APIs (M365/Google/AWS) | CD-244 | API | W6 | P2 | Manual subscription review |

**Marketplace & trust (INT-034…037)**

| ID | Integration | Client technology | Pattern | Wave | Pri | Fallback |
|---|---|---|---|:--:|:--:|---|
| INT-034 | NID / identity verification | **L6 KYC (TC-072)** + CD-233 residency service | Sync | W7 | **P0** | **Manual document review by compliance** |
| INT-035 | Trade licence / business registry | L6 KYC or L5 wrapper | Sync | W7 | P1 | Manual verification |
| INT-036 | IMEI / stolen-device blocklist | CD-064 `cd_tradein` | Sync | W6 | P1 | Manual check; hold device |
| INT-037 | Ad delivery service | CD-058 `cd_advertising` | API | W7 | P2 | Direct placement |

**Government & compliance (INT-038…042)**

| ID | Integration | Client technology | Pattern | Wave | Pri | Fallback |
|---|---|---|---|:--:|:--:|---|
| INT-038 | **NBR e-VAT filing (vat.gov.bd)** | **CD-195 `cd_mushak_return`** | File / API | W4 | **P0** | **Manual portal filing from the generated return** |
| INT-039 | BIN / TIN validation | CD-086 `cd_nid` + residency service | Sync | W3 | P1 | Manual validation |
| INT-040 | E-waste authority reporting | CD-082 `cd_esg_report` | File | W8 | P2 | Manual return |
| INT-041 | Biometric attendance devices | **CD-208** + residency service (templates are residency-classified) | SDK / file | W5 | P1 | Manual attendance entry |
| INT-042 | RJSC / company registry | CD-034 | Sync | W9 | P3 | Manual verification |

**AI, data & enterprise (INT-043…047)**

| ID | Integration | Client technology | Pattern | Wave | Pri | Fallback |
|---|---|---|---|:--:|:--:|---|
| INT-043 | **Self-hosted LLM inference** | **Ollama (TC-036)** + CD-245 gateway | Sync | W6 | P2 | **Rule-based responses; human routing** |
| INT-044 | OCR service | **CD-240** (Tesseract/PaddleOCR with Bengali models) | Sync | W3 | P2 | Manual data entry |
| INT-045 | Speech-to-text (Bengali) | **CD-246** (Whisper-class self-hosted) | Sync/async | W8 | P3 | Manual note-taking |
| INT-046 | **Corporate client SSO (SAML/OIDC per client)** | **Keycloak identity brokering** | Federation | W6 | P2 | Local portal accounts |
| INT-047 | Client ITSM (ServiceNow / Jira) | CD-127 `cd_webhook` + CD-244 | REST + webhook | W7 | P3 | Email ticket exchange |

**Integration count verified 13 August 2026 — 47 integrations, 47 technology assignments, 0 gaps.
Priority distribution: P0 = 12 · P1 = 17 · P2 = 12 · P3 = 6.**

#### 12.2.5 The portal platform contract (CON-03)

The most important integration in the estate, with its own contract.

**Field ownership — who owns what, declared:**

| Data | Owner | Direction | Sync |
|---|---|---|---|
| Customer identity and profile | **ERP (M07/M33)** | ERP → Portal | Event-driven, near real-time |
| Customer authentication | **Keycloak (M29)** | Shared | Federated |
| Marketing content, pages, blog, SEO | **Portal (Payload CMS)** | Portal only | — |
| Service catalogue and prices | ERP (M11, M37) | ERP → Portal | Scheduled + on change |
| Branch and coverage data | ERP (M30) | ERP → Portal | On change |
| Booking availability | ERP (M02) | Portal queries ERP | **Synchronous** |
| Service orders | ERP (M01) | Portal → ERP on create; ERP → Portal on update | Sync + events |
| Order status and tracking | ERP (M01, M02) | ERP → Portal | **Events + polling fallback** |
| Invoices and payments | ERP (M19, M20) | ERP → Portal | Events |
| Contracts and entitlements | ERP (M08) | ERP → Portal | Events |
| Loyalty points and vouchers | ERP (M10) | ERP → Portal | Events |
| Reviews and ratings | ERP (M12) | Portal → ERP on submit; ERP → Portal on publish | Sync |

**Contract rules:**

| Rule | Detail |
|---|---|
| Versioning | Both sides support **at least two API versions concurrently**; six months' notice before removal |
| Idempotency | Every POST accepts `Idempotency-Key`; duplicate keys return the original result |
| Authentication | OAuth 2.0 client credentials per environment; short-lived tokens |
| Rate limits | 600 requests/minute per portal instance; burst 100/second |
| Timeouts | Portal timeout 5 s on synchronous calls; **ERP responds within 2 s at p95** |
| Failure behaviour | Portal degrades gracefully — cached catalogue, **queued booking with confirmation on recovery** |
| Reconciliation | **Nightly job compares order and customer counts; divergence alerts** |

#### 12.2.6 Domain events

**Naming:** `<aggregate>.<past-tense-verb>`. **Envelope** (every event, without exception):

```json
{
  "event_id": "uuid",
  "event_type": "service_order.completed",
  "schema_version": "1.2",
  "occurred_at": "2026-08-13T09:14:22Z",
  "company_id": 1,
  "operating_unit_id": 17,
  "actor": { "type": "user", "id": 442 },
  "correlation_id": "uuid",
  "causation_id": "uuid",
  "aggregate": { "type": "service_order", "id": 918234 },
  "payload": { }
}
```

**Consumer rules — technology-enforced:**

| Rule | Enforcement |
|---|---|
| **Idempotency** — every consumer records processed `event_id`s and ignores duplicates | Shared consumer library; event test suite |
| **Ordering** — guaranteed per aggregate id only, never globally | Partition key = aggregate id |
| **Failure** — three retries with exponential backoff, then dead-letter with alert | Consumer library + Prometheus alert |
| **Replay** — any consumer replayable from a point in time with no side effects on others | **CD-247 event replay service**; Redpanda retention |
| **Schema** — additive changes only within a `schema_version`; breaking changes need a new version and a dual-publish period | Schema registry + CI compatibility check |
| **Latency** — 95% of events consumed within **5 seconds** of publication (NFR-043) | Event platform metrics |

**Why the outbox is non-negotiable (AS-08).** Publishing an event after committing a transaction
means that a crash between the two loses the event silently. Publishing before committing means an
event can describe a state that never existed. The outbox writes the event **into the same database
transaction** as the state change, and a separate relay publishes from the outbox table. This is the
only pattern that makes "every state change produces exactly one event" true rather than usually
true, and at 67 modules the difference between usually and always is a permanent source of data
divergence.

### 12.3 Data Model and Persistence

#### 12.3.1 Store assignment — what lives where and why

| Store | Technology | Contents | Sizing driver |
|---|---|---|---|
| **Primary OLTP** | PostgreSQL 16 | 225 entities; all transactional state | 5M service orders/year (NFR-053); 5M assets (NFR-054) |
| **Read replicas ×2** | PostgreSQL 16 streaming replication | Reporting offload, BI through W7 | Analytical read isolation |
| **Bangladesh-resident store** | PostgreSQL 16, separate key material | Residency-classified fields only (§14.4) | NFR-086; regulatory, not volume |
| **Time series** | TimescaleDB 2.x | GPS history, endpoint metrics, IoT telemetry | 800 GPS/min + 50,000 telemetry points/min (NFR-055, NFR-056) |
| **Analytical warehouse** | ClickHouse 24.x (W8) | Conformed dimensions, fact tables | Analytical query ≤ 10 s p95 (NFR-039) |
| **Cache / sessions / locks / streams** | Redis 7 | Sessions, cache, job queues, distributed locks, event streams (W1–W5) | 800+ concurrent internal users (NFR-003) |
| **Object storage** | MinIO / S3-compatible | Documents, evidence photos, exports, backups | **50 TB with sub-10-second retrieval (NFR-060)** |
| **Document management** | Mayan EDMS (W5) over object storage | Retention-classed records, OCR index | NFR-060, NFR-088, NFR-095 |
| **Model registry** | MLflow | Model versions, experiments, lineage | M26 governance |

#### 12.3.2 Modelling standards — DM-01 to DM-15

| # | Standard | Enforcement |
|---|---|---|
| DM-01 | Odoo models prefixed `fix.`; tables `fix_`; snake_case columns | Linter (AS-04) |
| DM-02 | Three-tier hierarchy: Odoo native → OCA extension → custom `cd_*` module | Architecture review |
| DM-03 | Every transactional model carries `company_id`, `operating_unit_id`, and where relevant `zone_id`, `cost_center_id`, `business_line_id` | Model registry check (AS-03) |
| DM-04 | Every business model inherits `mail.thread` and `mail.activity.mixin` | Model registry check (AS-02) |
| DM-05 | Create/write user and date on all; explicit audit entries for controlled objects | `auditlog` configuration |
| DM-06 | **Soft delete only** — business records archived, never hard-deleted (DI-08) | Model base class; hard delete requires an approved logged procedure |
| DM-07 | **`Monetary` with explicit `currency_id`; never floats** | Linter + financial test suite (AS-10, DI-01) |
| DM-08 | Stored UTC; presented Asia/Dhaka; durations in minutes | Schema check (AS-11) |
| DM-09 | UTF-8 throughout; **Bengali collation `bn_BD` with ICU fallback** | Database configuration |
| DM-10 | Explicit `state` field with the transition map declared in one place | Code review (AS-06) |
| DM-11 | Sequences branch- and business-line-aware with configurable masks | Sequence configuration |
| DM-12 | **Foreign keys enforced at the database level**; `ondelete` policy declared (DI-03) | Schema check |
| DM-13 | Business-line specialisation via one-to-one extension models, **not by widening the core model** | Architecture review |
| DM-14 | Fields classified **S0–S3**; S3 encrypted at field level and access-logged | Security test suite (AS-14, NFR-061) |
| DM-15 | **Every state change writes to the outbox in the same transaction** | Event coverage test (AS-08) |

**DM-13 is the standard most often violated and hardest to reverse.** When rental, refurbishment and
marketplace each need three extra fields on the service order, the tempting move is to add nine
columns to `fix.service.order`. After nine business lines the core model is unreadable and every
query is conditional. The rule is one-to-one extension models — `fix.service.order.rental`,
`fix.service.order.marketplace` — so that the core stays the core.

#### 12.3.3 Performance design

| Technique | Applied to | Purpose |
|---|---|---|
| **Range partitioning by date** | Service orders, work orders, invoices, journal items, events, audit log | Keeps hot partitions small at 5M orders/year |
| **Hash partitioning by operating unit** | High-volume branch-scoped tables | Branch query isolation across 51+ (target 200) branches |
| Covering indexes on dispatch queries | Open orders by zone, skill, SLA deadline | NFR-033 ≤ 1 s dispatch board at 500 open jobs |
| GIN + `pg_trgm` indexes | Free-text and **Bengali** search fields | NFR-035 ≤ 600 ms search p95 including Bengali |
| Materialised views, refreshed on event | Customer 360, branch dashboard aggregates | NFR-031 ≤ 2 s Customer 360 |
| TimescaleDB hypertables + native compression | GPS, telemetry | Volume containment |
| TimescaleDB continuous aggregates | Dashboard time-series queries | Sub-second live dashboards |
| PgBouncer transaction pooling | All application connections | 1,000 connections against 800+ concurrent users |
| Redis read-through cache | Catalogue, price book, branch directory, configuration | Removes repeated hot reads from OLTP |
| Async export jobs with download links | Any export over the payload limit | API-12 |

### 12.4 Analytics, Warehouse and KPI Instrumentation

| Concern | Technology | Wave |
|---|---|---|
| Operational reporting inside the ERP | `mis-builder`, `reporting-engine`, `account-financial-reporting` | W3 |
| Analytical BI and dashboards | **Metabase** on read replica → ClickHouse | W4 → W8 |
| Real-time operational monitoring | **Grafana** on Prometheus + TimescaleDB | W2 |
| Warehouse | **ClickHouse** | W8 |
| ETL and transformation | **CD-243 (Python + dbt)** with data-quality gates (DI-06) | W4 |
| Semantic layer / certified datasets | CD-110 metric registry + Metabase models | W4 |
| Embedded analytics in portals | CD-112 with **row-level security context** | W4 |
| Data contracts, lineage, quality | CD-225…227 | W4/W8 |

#### 12.4.4 KPI instrumentation — 95 KPIs

**Every module ships its KPI instrumentation as a definition-of-done item (DoD-09, AS-15).** The
mechanism:

| Step | Technology |
|---|---|
| 1. KPI registered with a `KPI-nnn` identifier and an owning module | **CD-110 `cd_metric_registry`** |
| 2. The module emits the measurement as part of its normal transaction or event | Domain event payload or a dedicated measurement model |
| 3. Measurements land in the warehouse | CD-111 warehouse sync → CD-243 ETL |
| 4. The KPI is surfaced against its target and baseline | Metabase (analytical) / Grafana (real-time) |
| 5. Threshold and anomaly alerts route to the owning role | Grafana alerting → Novu |

**A KPI without instrumentation is not a KPI, it is an intention.** This is why DoD-09 blocks module
acceptance rather than being a reporting-workstream activity: retrofitting measurement into 67
modules after the fact costs more than building it in, and produces a baseline gap that makes benefit
realisation unprovable.

> **Disclosed defect — inherited.** The programme KPI register carries **colliding `KPI-` identifiers**
> across module specifications (audit finding H2-04). CD-110 cannot register two KPIs with the same
> identifier. **The KPI register must be de-duplicated before Wave 1 instrumentation begins.** See
> §25.1.

### 12.5 AI and Machine Learning Platform

| Concern | Technology | Module | Wave |
|---|---|---|:--:|
| Model registry, experiment tracking, lineage | **MLflow 2.x** | M26 | W6 |
| Inference gateway with per-model fallback | **CD-245** (Python/FastAPI) | M26 | W6 |
| LLM inference, self-hosted | **Ollama 0.5+** with open-weight Bengali-capable models | M26, M32 | W6 |
| Feature data | TimescaleDB + ClickHouse | M62 | W6 |
| Dispatch scoring model | CD-114 `cd_dispatch_ml` | M02, M26 | W6 |
| Demand forecasting | CD-115 `cd_forecast` | M43, M26 | W6 |
| Predictive maintenance | CD-116 `cd_predictive` | M48, M26 | W8 |
| Dynamic pricing model | CD-117 `cd_pricing_ml` | M11, M26 | W7 |
| LLM bridge for assistant and summarisation | CD-118 `cd_llm_bridge` | M32, M27 | W6 |

**Four rules govern this platform and they are absolute:**

| # | Rule | Why |
|---|---|---|
| ML-01 | **Every model has a deterministic fallback**, and no business path depends on a model being available | IP-05, NFR-050 |
| ML-02 | **Every prediction writes `model.prediction_made`** with inputs, output and model version | Explicability; model improvement; audit |
| ML-03 | **Customer data does not leave the Company for inference** | **PDPA transfer restrictions (NFR-099)** — this is why Ollama is self-hosted and hosted LLM APIs were rejected (TD-06) |
| ML-04 | Every model is registered in MLflow with its training data lineage before it serves production traffic | Governance; reproducibility |

**ML-03 is a regulatory constraint, not an architectural preference.** Sending a customer
conversation to a hosted LLM API is a cross-border transfer of personal data requiring assessment,
safeguard documentation and potentially Authority notification. Self-hosting removes the question
entirely, removes per-query cost at 250,000 customer interactions a month, and is the reason a GPU
line appears in the infrastructure sizing.

### 12.6 Document, Records and E-Signature

| Concern | Technology | Wave |
|---|---|---|
| Attachments and basic documents | Odoo `ir.attachment` + `OCA/dms` | W1 |
| Object storage | MinIO / S3-compatible | W1 |
| **Document management at volume, OCR, retention** | **Mayan EDMS 4.10** | W5 |
| Migration from OCA `dms` to Mayan | **CD-236** | W5 |
| Bengali + English OCR | **CD-240** | W3 |
| **High-volume PDF/A generation with Bengali rendering** | **CD-238** — invoices, Mushak 6.3, service reports, payslips, certificates | W3 |
| **Operational e-signature** (job completion, delivery, audit acknowledgement) | **CD-108** — capture, timestamp, GPS, evidence binding | W3 |
| **Qualified e-signature** (AMC, MSP, rental, seller agreements) | **L6 TC-071** — accredited trust service | W4 |
| Retention-class enforcement | **CD-109 `cd_retention`** | W3 |
| Malware scanning on upload | **ClamAV** before storage or serving (NFR-063) | W1 |

**Bengali PDF rendering is a real engineering problem, not a font setting.** Bengali is a complex
script with conjuncts, reordering vowel signs and ligature substitution. Naive PDF generation
produces text that is legible to a machine but wrong to a reader — which on a Mushak 6.3 tax invoice
or a payslip is a compliance failure, not a cosmetic one. CD-238 uses a rendering path with proper
OpenType shaping, and **Bengali print output is verified on every supported printer as a wave-gate
item** (`05-06` §10).

### 12.7 Notification and Communications

| Concern | Technology | Wave |
|---|---|---|
| Notification orchestration across 6 channels | **Novu 2.x** | **W1** |
| Channel routing, template resolution, delivery tracking | **CD-234 notification dispatcher** | **W1** |
| SMS (primary + failover) | L3 connectors via Novu | W1/W2 |
| WhatsApp Business Cloud API | L3 connector via Novu | W1 |
| Email (SMTP/API out, IMAP in with ticket parsing) | Odoo `mail` + Novu | W1 |
| Push (FCM / APNs) | Novu + Flutter SDK | W2 |
| In-app inbox | CD-124 `cd_inbox` | W2 |
| Voice / IVR | **L6 CPaaS (TC-070)** + CD-120 | W4 |
| Preference, quiet hours, consent enforcement | **CD-123** + CD-148 consent registry | W1 |
| Delivery-status callbacks into the audit trail | CD-234 → `auditlog` | W1 |

**Two rules with technology consequences:** (a) a **do-not-contact instruction is honoured
absolutely**, including operational messages where lawful (FR-CRM-044) — enforced at the dispatcher,
not at each caller; (b) **quiet hours** are enforced centrally with an explicit override for
safety-critical messages only, and the override is logged.

### 12.8 Workflow and Automation — the 60-Automation Catalogue

**Every one of AUT-001 … AUT-060 has an execution engine and a defined manual fallback.** Assignment
by engine:

| Engine | Automations | Why this engine |
|---|---|---|
| **Odoo model layer / automated actions** (L1 + L5) | Rules that must be atomic with the transaction — entitlement evaluation, SLA assignment, stock reservation, GL posting, rework flagging | Must not be eventually consistent |
| **Odoo scheduled actions (cron)** (L1) | Time-based within one module — reminder sequences, ageing, expiry, recurring generation | Simple, in-transaction, observable |
| **n8n** (L4) | Cross-system choreography — brand-claim transformation, courier booking, external notification fan-out, reconciliation triggers, route-optimisation trigger | Configuration rather than code; changes without release |
| **CD-228 process engine** (L5) | Multi-step, multi-role, long-running business processes with state — approval chains, onboarding, offboarding, dispute resolution | Needs durable state and role routing |
| **Event consumers** (L5) | Reactive automations triggered by domain events across modules | Idempotent, replayable |
| **CD-245 ML gateway** (L5) | Automations with a predictive component — dispatch scoring, forecast-driven replenishment, anomaly detection | Model-backed with deterministic fallback (ML-01) |

**Every automation has a fallback, and the fallback is tested.** BRD §22 and `05-05` §12 define the
manual fallback for each of the 60; NFR-050 requires that every P0 integration's fallback be
documented **and tested**. An automation whose fallback has never been executed is not a fallback, it
is a hope — so fallback execution is part of the DR drill (NFR-051).

### 12.9 Search

| Scope | Technology | Wave |
|---|---|---|
| Structured search across records | Odoo ORM search with covering indexes | W1 |
| Free-text and **Bengali** search | **PostgreSQL full-text search + `pg_trgm` + ICU `bn-BD` collation** | W1 |
| Document content search | **Mayan EDMS OCR index** | W5 |
| Knowledge semantic search | **Ollama embeddings + vector index** (CD-224) | W6 |
| Escalation path | **OpenSearch, if and only if measured latency exceeds NFR-035 (≤ 600 ms p95)** | Deferred |

**Search is deliberately not over-engineered at Wave 1.** PostgreSQL FTS with trigram indexes serves
Bengali and English search well below the 600 ms target at expected Wave 1–5 volume. Introducing a
separate search cluster adds an index-synchronisation problem, a consistency problem and an
operational surface for no measured benefit. **The escalation is planned but not pre-committed** —
the trigger is measurement against NFR-035, reviewed at each wave gate.

---
## 13. NON-FUNCTIONAL REQUIREMENT REALISATION

### 13.1 Method and Scope

**Every NFR identifier from NFR-001 to NFR-101 appears in this section with the technology that
realises it and the method by which conformance is verified.** An NFR without a named realising
technology is a defect; there are none.

> **Disclosed defect — identifier collision, inherited. TSA-03.** The source register `05-06`
> assigns **NFR-090, NFR-091 and NFR-092 to two different requirements each**: in §6.3 they are
> PDPA obligations (consent ground, consent standard, transparency notice) and in §7 they are
> maintainability requirements (test coverage, runbook, distributed tracing). `05-06` §6.4 also
> repeats NFR-088 and NFR-089 inside the residency field table. **The identifier space therefore
> holds 101 identifiers carrying 104 distinct requirements.** This document covers **all 104**, using
> the suffix `-M` for the maintainability reading (NFR-090-M, NFR-091-M, NFR-092-M) so that both are
> traceable, and it **does not create new identifiers** (rule RG-01). Resolution of the collision in
> the owning register is Wave 1 scope. See §25.1.

### 13.2 Performance — NFR-001 to NFR-005, NFR-031 to NFR-044

| ID | Requirement | Target | Realising technology | Verified by |
|---|---|---|---|---|
| NFR-001 | ERP screen load under normal load | ≤ 2 s p95 | OWL 2 with server-side pagination; Redis read-through cache; covering indexes; PgBouncer | Synthetic monitoring, per wave gate |
| NFR-002 | API response time | ≤ 400 ms p95 | Kong + Odoo tuned workers; materialised views for composed reads | Gateway metrics |
| NFR-003 | Concurrent internal users | 800+ | 4 Odoo nodes × 12 workers; PgBouncer 1,000 connections; Redis sessions | Load test at 1.5× peak |
| NFR-004 | Concurrent customer portal users | 75,000+ | Next.js edge caching + CDN; static catalogue; read replica; autoscaling portal nodes | Load test |
| NFR-005 | Standard report generation | ≤ 20 s | `mis-builder` on read replica; Metabase caching | Report timing log |
| NFR-031 | Customer 360 view load | ≤ 2 s | **Materialised view refreshed on event**; Redis cache | Instrumentation |
| NFR-032 | Booking availability calculation | ≤ 800 ms p95 | Pre-computed slot capacity in Redis; OSRM travel matrix cached | API metrics |
| NFR-033 | Dispatch board refresh at 500 open jobs | ≤ 1 s | Covering index on (zone, state, SLA deadline); WebSocket delta push, not full reload | Instrumentation |
| NFR-034 | Live map update latency from GPS emission | ≤ 5 s | Traccar WebSocket → event → portal webhook, no polling in the hot path | End-to-end trace |
| NFR-035 | Search results, any entity, including Bengali | ≤ 600 ms p95 | **PostgreSQL FTS + `pg_trgm` + ICU `bn-BD`**; OpenSearch escalation if breached (§12.9) | Instrumentation |
| NFR-036 | Technician app job list on 3G | ≤ 8 s cold, ≤ 2 s warm | Local SQLite read for warm; delta-only cold sync | Field test on a real 3G network |
| NFR-037 | **Offline sync completion after 24 h offline** | **≤ 30 s on 3G** | Batched delta sync, compressed, checksummed; deferred evidence upload (§16) | **Field test — a wave-gate blocker** |
| NFR-038 | Executive dashboard load | ≤ 5 s | Metabase on ClickHouse (W8); pre-aggregated dimensions | Instrumentation |
| NFR-039 | Warehouse analytical query | ≤ 10 s p95 | ClickHouse columnar store, partitioned and sorted by query pattern | Warehouse metrics |
| NFR-040 | **Invoice generation from job closure** | ≤ 5 s | In-transaction invoice creation; async PDF via CD-238 | Instrumentation |
| NFR-041 | Bulk operation, 1,000 records | ≤ 60 s with progress feedback | Async job queue on Redis; progress channel to the UI | Load test |
| NFR-042 | Payment confirmation round trip | ≤ 3 s p95 | Direct gateway call with a 3 s timeout and a webhook reconciliation path | Gateway metrics |
| NFR-043 | Event delivery to consumer | ≤ 5 s p95 | Redis Streams / Redpanda with consumer-lag alerting | Event platform metrics |
| NFR-044 | Nightly route optimisation, all technicians | ≤ 20 minutes | VROOM parallelised by zone; OSRM matrices pre-computed | Job monitor |

### 13.3 Availability and Continuity — NFR-006 to NFR-008, NFR-045 to NFR-052

| ID | Requirement | Target | Realising technology | Verified by |
|---|---|---|---|---|
| NFR-006 | Uptime in Bangladesh business hours (09:00–22:00 BST) | ≥ 99.9% | HA across every tier; no single-node critical component | Uptime monitoring |
| NFR-045 | Uptime 24×7 (managed services requires it) | ≥ 99.7% | As above; maintenance windows outside the band | Uptime monitoring |
| NFR-007 | Disaster recovery | **RPO ≤ 15 min, RTO ≤ 2 h** | Streaming replication to warm standby; hourly WAL archive; DR runbook | **DR drill twice yearly (NFR-051)** |
| NFR-008 | Zero-downtime deployment | Standard for all releases | Rolling deploys behind Kong; forward-only, backward-compatible migrations (OPS-07) | Deployment log |
| NFR-046 | Customer portal availability | ≥ 99.9% | CDN + multi-instance Next.js + graceful ERP-degradation mode | Uptime monitoring |
| NFR-047 | Technician app functional without connectivity | **24 hours** | Offline engine (§16) | Offline test suite |
| NFR-048 | Payment path availability | ≥ 99.95% | **Multi-gateway failover across bKash, Nagad, SSLCOMMERZ**; cash fallback | Synthetic transaction monitoring |
| NFR-049 | Planned maintenance window | Outside 08:00–23:00 BST; ≤ 4 h/month; 72 h notice | Change calendar; deployment gate | Change record |
| NFR-050 | **Graceful degradation** | Every P0 integration has a documented, **tested** manual fallback | Circuit breakers; fallback register (§12.2.4) | **Fallback executed in the DR drill** |
| NFR-051 | DR drill | Full failover twice yearly with documented results | DR runbook | Drill report |
| NFR-052 | Backup verification | **Automated restore test weekly** | Automated restore into an isolated environment with control totals | Restore-test report |

### 13.4 Scalability — NFR-009, NFR-010, NFR-053 to NFR-060

| ID | Requirement | Target | Realising technology | Verified by |
|---|---|---|---|---|
| NFR-009 | Growth headroom without re-architecture | 5× users, 10× data over 5 years | Horizontal app tier; partitioned OLTP; separate time-series and analytical stores | Capacity model reviewed monthly (OPS-08) |
| NFR-010 | Elastic capacity for demand peaks | Automatic scaling | K3s horizontal pod autoscaling on app and portal tiers | Load test at seasonal peak profile |
| NFR-053 | Service order volume | **5 million/year by year 5** | Date range partitioning; archival of closed orders (FR-SRM-087) | Volume projection test |
| NFR-054 | Device registry | **5 million assets** | Partitioned asset tables; indexed by serial/IMEI | Volume test |
| NFR-055 | Telemetry ingestion | 50,000 points/minute | **TimescaleDB hypertables + CD-237 collector** | Ingestion load test |
| NFR-056 | GPS ingestion | 400 technicians at 30 s sustained | **Traccar + TimescaleDB with compression** | Sustained load test |
| NFR-057 | Marketplace scale | 5,000 sellers, 50,000 listings | Partitioned listing tables; Redis-cached search facets | Volume test |
| NFR-058 | Branch scale | **200 branches without configuration redesign** | `OCA/operating-unit` hierarchy; configuration is data, not code | Configuration model review |
| NFR-059 | Multi-entity scale | 10 legal entities across 5 countries | Odoo multi-company + `operating-unit` + CD-231 localisation | M65 design review |
| NFR-060 | Document store | **50 TB with sub-10-second retrieval** | MinIO/object storage + **Mayan EDMS** index | Retrieval test at volume |

### 13.5 Security — NFR-011 to NFR-015, NFR-061 to NFR-072

| ID | Requirement | Realising technology | Verified by |
|---|---|---|---|
| NFR-011 | RBAC with field-level granularity | Keycloak roles + Odoo `ir.rule` + **CD-130 field permissions** | Negative test per role (DoD-07) |
| NFR-012 | MFA mandatory for admin, finance, HR and privileged roles | Keycloak MFA policy by role group | Configuration audit |
| NFR-013 | AES-256 at rest; **TLS 1.2+, TLS 1.3 preferred** in transit | Storage-level encryption; Nginx/Kong TLS 1.3 | TLS scan; encryption audit |
| NFR-014 | Complete **immutable** audit trail — who, what, when, before, after | `OCA/server-tools` `auditlog` + **CD-131**, append-only with WORM-class object storage for exports | Tamper test |
| NFR-015 | Branch-level data isolation at record level | **`OCA/operating-unit`** record rules | Negative test per branch |
| NFR-061 | **Field-level encryption for S3-classified data with separate key material** | CD-233 residency service + envelope encryption; keys in Vault, distinct from the database key | Security test suite (AS-14) |
| NFR-062 | Secrets in a vault; never in code, configuration or logs | **Vault** + secret scanning pre-commit and in CI | Secret scan gate |
| NFR-063 | Malware scanning on every upload before storage or serving | **ClamAV** in the upload path | Upload test with EICAR |
| NFR-064 | **Segregation of duties enforced by the permission engine** | **CD-132 `cd_sod`** — 30 controls at role-assignment time | SoD conflict test |
| NFR-065 | Step-up authentication for sensitive actions | Keycloak step-up (ACR/AMR) triggered by CD-130 on T5 access | Step-up test |
| NFR-066 | Automated dependency, container and infrastructure vulnerability scanning in CI **and in production** | SCA + container scanning in CI; runtime scanning via Wazuh | CI gate; production scan report |
| NFR-067 | Annual penetration test with findings tracked to closure | External engagement; findings in M60 | Test report + closure register |
| NFR-068 | Rate limiting and bot protection on all public endpoints | Kong rate limiting + CDN bot management | Configuration audit |
| NFR-069 | Session policy — 30 min idle external, 60 min internal, 12 h absolute | Keycloak session configuration (PS-12) | Configuration audit |
| NFR-070 | All privileged sessions recorded | Bastion session recording; Odoo admin action logging | Recording audit |
| NFR-071 | **Non-production environments use masked data only** | Masking in the clone job, not after it (§3.5) | Data-scan of every non-production environment |
| NFR-072 | Security incident response with defined severities and breach-notification assessment | Incident runbook in M60; **PDPA breach assessment path to the National Data Management Authority (NFR-094)** | Incident drill |

### 13.6 Usability and Accessibility — NFR-016 to NFR-020, NFR-073 to NFR-082

| ID | Requirement | Realising technology | Verified by |
|---|---|---|---|
| NFR-016 | Full Bengali and English in interfaces, notifications, reports and data entry | Odoo `.po` · `next-intl` · Flutter `.arb` · Novu locale templates · CD-238 Bengali PDF | **Translation completeness 100% (AS-12)** |
| NFR-017 | Technician app on **Android 11+, 3 GB RAM, intermittent 4G** | Flutter with Impeller; bounded memory; adaptive sync | Device matrix test on real hardware |
| NFR-018 | Offline mode with automatic sync on reconnection | Offline engine (§16) | Offline test suite |
| NFR-019 | Responsive across mobile, tablet and desktop on all portals | Shared design system breakpoints from 320 px | Visual regression |
| NFR-020 | **Low-bandwidth mode** for field and rural operation | Image downscaling, deferred uploads, text-first fallbacks (FR-FSM-061) | 3G field test |
| NFR-073 | **WCAG 2.1 AA on all web portals** | Design system components built accessible; axe-core in CI | **Automated scan + manual audit per portal release** |
| NFR-074 | Bengali input — phonetic typing and voice-to-text on mobile | Platform IME support; Bengali STT via CD-246 | Input test |
| NFR-075 | New service agent competent in ≤ 4 hours of training | P03 role-scoped workspaces; task-oriented design | Timed training measurement |
| NFR-076 | Walk-in intake in ≤ 3 minutes | Keyboard-first intake workspace; customer search by phone/serial | Timed observation |
| NFR-077 | Any record reachable in ≤ 4 clicks | Global search + workspace navigation model | Navigation audit |
| NFR-078 | Every error states what happened and what to do next, in the user's language | Standard error envelope (API-04) + error catalogue; **no raw exception surfaces to a user** | Error-catalogue review |
| NFR-079 | Destructive actions require confirmation and are reversible where possible | Soft delete (DM-06, DI-08); confirmation pattern in the design system | UX review |
| NFR-080 | **Consistent design system across all 12 portals — one component library, one token set** | **Shared token package consumed by Next.js, Flutter and Odoo OWL** | Design-system conformance lint |
| NFR-081 | Critical customer paths **under 400 KB first load** | Bundle budget enforced in CI; build fails on breach | Bundle-size gate |
| NFR-082 | Technician app battery **≤ 12% per 8-hour shift** excluding navigation | Adaptive location sampling; batched network; deferred uploads | Measured 8-hour field test |

> **Accessibility position.** The contracted standard is **WCAG 2.1 AA** (NFR-073, PS-04), and this
> stack builds to it. URD §21.4 recommends moving the target to **WCAG 2.2 AA** and identifies a
> concrete gap: **the dispatch board is specified as drag-and-drop, and drag-only interaction fails
> SC 2.5.7 Dragging Movements.** The technology response is that the P03 dispatch console **must
> provide a keyboard and single-pointer alternative to every drag interaction regardless of which
> standard is adopted** — it is required under 2.1 for accessibility persona A-06 and would be
> required explicitly under 2.2. This is built, not deferred pending the standard decision.

### 13.7 Compliance — NFR-021 to NFR-025, NFR-083 to NFR-085, NFR-087 to NFR-089, NFR-100, NFR-101

| ID | Requirement | Realising technology | Verified by |
|---|---|---|---|
| NFR-021 | **Mushak 6.3 tax invoice compliance** per the VAT & SD Act 2012 | **CD-083 `cd_mushak`** + CD-238 Bengali PDF generation | NBR format validation; wave-gate review under DoD-17 |
| NFR-022 | Bangladesh NBR income tax computation | **CD-198/CD-211 tax slabs** | 100% unit-test coverage on tax calculation (L5-02) |
| NFR-023 | **ICT Act 2006 and Cyber Security Ordinance 2025 compliance** | Security architecture §14; audit trail; incident response | Compliance review with a *verified-on* date (DoD-17) |
| NFR-024 | ISO 9001:2015 audit trail and documentation | **`OCA/management-system`** + CD-105 + Mayan EDMS retention | ISO audit readiness review |
| NFR-025 | ISO 27001 security control alignment | Keycloak, Vault, Wazuh, `auditlog`, CD-130…132 | Control mapping review |
| NFR-083 | Bangladesh Labour Act compliance in HR and payroll | **CD-207…213** — working time, PF, gratuity, employment artefacts | Legal review; 100% test coverage on statutory calculation |
| NFR-084 | Bangladesh e-waste and environmental handling rules | **CD-080…082** + INT-040 | Statutory return validation |
| NFR-085 | Consumer protection obligations on marketplace transactions | CD-053…057 — dispute process, payout holds, review integrity | Policy conformance review |
| NFR-087 | Data-subject rights supportable within legal constraints | **CD-248 DSR orchestrator** — see NFR-093 for the statutory set | DSR end-to-end test |
| NFR-088 | **Records retention per the statutory schedule, enforced by the system** | **CD-109 `cd_retention`** + Mayan EDMS retention classes | Retention-policy test; expiry simulation |
| NFR-089 | SOC 2 / ISO 27001 readiness for enterprise and multi-country expansion | Control evidence collection in M60; Wazuh; audit trail | Readiness assessment |
| NFR-100 | **Mushak 9.1 monthly VAT return filed by the 15th, submitted through vat.gov.bd** | **CD-195 `cd_mushak_return`** + INT-038 | Return generation test; submission dry run |
| NFR-101 | **Input VAT credit claimable only against a valid compliant Mushak 6.3; the system must block claims without one** | **CD-084 `cd_vat_register`** — a **hard rule at the model layer** (BR-STD-05), not a warning | Negative test through both UI and API (DoD-04) |

### 13.8 Personal Data Protection Act 2026 — NFR-090 to NFR-099

**Regulator: the National Data Management Authority. Enforcement mechanisms activate ~13 May 2027 —
inside Wave 4. Penalty exposure: up to BDT 25 lakh, and up to BDT 50 lakh for significant data
fiduciaries.**

| ID | Requirement | Realising technology | Owning module | Verified by |
|---|---|---|---|---|
| NFR-090 | Process personal data only on consent or a stated legitimate ground, **recorded per processing purpose** | **CD-148 `cd_consent_registry`** — purpose-scoped consent records with timestamp, channel and version | M33 | Consent-record audit |
| NFR-091 | Consent **clear, explicit, specific and freely given**, with a heightened *specific consent* standard for sensitive personal data | CD-148 — separate capture path and separate record type for sensitive-data consent; no bundled consent | M33 | Consent-flow review |
| NFR-092 | **Transparency notice** before or during processing — categories, purposes, risks, retention, third-party transfers, withdrawal procedure | CD-148 + Payload CMS versioned notice content, with the version bound to the consent record | M33 | Notice-version audit |
| NFR-093 | Data-subject rights — **access and portability**, **rectification with controller notification within 30 days**, **erasure**, **consent withdrawal by a simplified procedure** | **CD-248 DSR orchestrator** — a saga across the regional store, resident store, warehouse, object store and search index | M33, M29 | **DSR end-to-end test per right** |
| NFR-094 | **Notify the National Data Management Authority** of any breach likely to cause significant damage, within the prescribed timeframe | Incident runbook in M60 + CD-131 audit evidence + notification template and register | M60, M29 | Breach-notification drill |
| NFR-095 | Maintain processing records for a **minimum of five years** | CD-109 retention class `processing_record` — **retained through erasure of the underlying personal data** | M24, M29 | Retention test |
| NFR-096 | **Appoint a Chief Data Officer** if classified a *significant* data fiduciary, with role, authority and reporting line defined | Organisational; system support via **role R40 Chief Data Officer** (currently unregistered — §12.1.2) and a CDO console in P03 | M60 | Governance review |
| NFR-097 | Technical and organisational measures proportionate to risk | The whole of §14 | M29 | Security review |
| NFR-098 | Treat a processor's processing as the controller's own; flow equivalent obligations to every processor and sub-processor by contract | **Processor register in M60**; contractual flow-down; applies to every **L6** component (L6-05) | M42, M60 | Contract audit |
| NFR-099 | **Restrict large-scale transfer of Sensitive Personally Identifiable Data** — NID, passport, TIN, biometric, genetic, criminal records — notify the Authority of cross-border transfers and disclose safeguards | **Split-residency architecture (§14.4) + CD-233 residency service + NFR-086b transfer gate** | M29, M65 | **Residency enforcement test — attempt a classified write to the regional store and assert rejection** |

### 13.9 Data Residency — NFR-086, NFR-086a, NFR-086b, NFR-086c

| ID | Requirement | Realising technology | Verified by |
|---|---|---|---|
| NFR-086 | **Split-residency data architecture** — Sensitive Personally Identifiable Data in a **Bangladesh-resident** store; the remainder may be regional; **joined by a resident key, never by duplicating the sensitive field** | Separate PostgreSQL 16 instance in Bangladesh, separate key material, reachable only through **CD-233** from trust zone Z4 | Architecture review + penetration test of the boundary |
| NFR-086a | **The data model carries a residency classification on every field, and the platform enforces it at write time — not by convention** | Field-level `residency` attribute in the model registry; **the ORM layer rejects a classified write to the regional store**; CI model-registry check | **Negative test: attempt the write, assert rejection** |
| NFR-086b | Any cross-border transfer of a classified field requires an **Authority notification record and a documented safeguard before the transfer executes** | CD-233 transfer gate — the transfer is blocked until the notification record exists | Transfer-gate test |
| NFR-086c | **Non-production environments never contain unmasked classified data in any region** | Masking inside the clone job (§3.5) | Data scan of every non-production environment |

**Fields currently classified as residency-restricted:**

| Field | Entity | Owning module | Store |
|---|---|---|---|
| National ID number | `fix.identity.document` | M33 | **Z4 resident** |
| Passport number | `fix.identity.document` | M33 | **Z4 resident** |
| TIN | `fix.party`, `hr.employee` | M33, M21 | **Z4 resident** |
| Biometric attendance template | `fix.attendance.record` | M55 | **Z4 resident** |
| Recovered customer data and its index | `fix.recovered.inventory` | M06 | **Z4 resident** |
| Marketplace seller KYC documents | `fix.mp.seller.document` | M12 | **Z4 resident** |
| Criminal record checks, where collected | `fix.mp.seller.document` | M12 | **Z4 resident** |

> **Open dependency — DEP-31, and it gates Wave 1.** A **legal opinion on the split-residency design
> is required before the Wave 1 architecture is fixed**, registered as decision **D-13**. The
> technology position is designed to be robust to either outcome: if the opinion permits a narrower
> classification, fields move out of Z4 by reclassification, not by redesign; if it requires a wider
> one, additional fields move in the same way. **What cannot be retrofitted is the residency service
> and the field-level classification mechanism itself — those are built in Wave 1 regardless.**

### 13.10 Maintainability and Operability — NFR-026 to NFR-028, NFR-090-M to NFR-092-M

| ID | Requirement | Realising technology | Verified by |
|---|---|---|---|
| NFR-026 | API-first architecture with documented REST APIs for all integrations | Kong + OpenAPI 3.1 generated from code (AS-07, API-03) | CI specification validation |
| NFR-027 | **No-code configuration** for workflows, forms, thresholds and business rules | Odoo studio-equivalent configuration models; **thresholds are configuration, not code (BR-STD-03)**; n8n for orchestration; CD-135 feature flags | Configuration-change test without deployment |
| NFR-028 | Customisation without modifying core product code | AS-05, L1-01 — inheritance only | Repository review |
| **NFR-090-M** | Unit test coverage ≥ 80% on custom code; **100% on financial calculations** | Coverage gate in CI | **Build fails below threshold** |
| **NFR-091-M** | Every module ships with an operational runbook | DoD-11 gate | Wave-gate checklist |
| **NFR-092-M** | Distributed tracing across all services with a **single correlation id** | **OpenTelemetry** propagated through Kong, Odoo, services and the event bus | Trace-continuity test across a full journey |

**Operability standards OPS-01 to OPS-08:**

| # | Standard | Technology |
|---|---|---|
| OPS-01 | Every deployment automated, repeatable and reversible | CI/CD pipeline with a tested rollback path (DoD-16) |
| OPS-02 | Configuration versioned and promoted through environments, **never hand-edited in production** | Configuration-as-code; production write access removed |
| OPS-03 | Every alert has a runbook entry; **alerts without actions are removed** | Alert register reviewed at each wave gate |
| OPS-04 | Logs structured and searchable; **no personal data in logs** | Structured logging + Loki; **log scrubbing of classified fields, CI-checked** |
| OPS-05 | Every scheduled job reports success, failure and duration; **silent failure is a defect** | Job instrumentation → Prometheus → alert |
| OPS-06 | **Feature flags allow any new capability to be disabled without a deployment** | **CD-135 `cd_feature_flag`** |
| OPS-07 | Migrations forward-only, tested against a production-sized dataset, reversible by documented procedure | Migration test stage in CI against a production-sized clone |
| OPS-08 | Capacity reviewed monthly against growth; scaling decisions made ahead of need | Capacity model + Grafana capacity dashboard |

### 13.11 Data Integrity — NFR-029, NFR-030, DI-01 to DI-08

| ID | Requirement | Realising technology | Verified by |
|---|---|---|---|
| NFR-029 | All transactions ACID-compliant with full rollback | PostgreSQL transactional guarantees; no cross-store writes outside a saga | Transaction test |
| NFR-030 | Automated backups — daily/30 days, weekly/1 year, monthly/7 years | Backup schedule + AES-256 + weekly restore verification (NFR-052) | Restore test |
| DI-01 | Financial calculations use decimal arithmetic; **no floating point in money paths** | `Monetary` fields; linter rule (AS-10) | Financial test suite |
| DI-02 | Every financial posting reconcilable to its source transaction | Source-document reference mandatory on every journal entry | Reconciliation test |
| DI-03 | **Referential integrity enforced at the database level**, not only in application code | Foreign keys with declared `ondelete` (DM-12) | Schema check |
| DI-04 | **Offline sync guarantees zero data loss and zero double-application** | Append-only journal + client UUID + server-side idempotency ledger (§16) | Offline conflict test suite |
| DI-05 | Event delivery at-least-once with idempotent consumption | Outbox + consumer idempotency ledger | Event test suite |
| DI-06 | **Data quality tests run on every warehouse load; failures block dependent refreshes** | dbt tests in CD-243 | Warehouse load gate |
| DI-07 | Cross-system reconciliation nightly with divergence alerting | **CD-241 reconciliation service** | Reconciliation report |
| DI-08 | **Soft deletion only**; hard deletion requires an approved, logged procedure | DM-06; hard-delete procedure in M30 with approval and audit | Deletion audit |

### 13.12 Environmental and Device Support

| Category | Supported | Technology consequence |
|---|---|---|
| Desktop browsers | Chrome, Edge, Firefox (latest two); Safari (latest two) | Build targets set accordingly; no polyfills for older engines |
| Minimum desktop resolution | **1366×768** | P03 screen density designed for it, not for a 1440p developer monitor |
| Mobile OS — technician, rider, auditor | **Android 11+** primary; iOS 15+ secondary | Flutter minimum SDK targets |
| Mobile OS — customer | Android 9+; iOS 14+ | Flutter + PWA fallback below minimum |
| Minimum field device | **3 GB RAM, 32 GB storage, GPS, camera, 4G** | Memory ceiling enforced in the app; local store pruning |
| Network | **Functional on 3G**; optimised for 4G; full offline where specified | Bundle budgets; adaptive sync |
| Peripherals | Thermal receipt printers, label printers, barcode/QR scanners, biometric devices, signature capture, queue displays, kiosks | Driver/SDK integration per device class; **Bengali rendering verified on every supported printer** |
| Printing | A4 and thermal receipt formats | CD-238 with per-format templates |

### 13.13 Testing Technology

| Level | Coverage | Tooling | Gate |
|---|---|---|---|
| Unit | ≥ 80% custom code; **100% financial and tax** | Odoo test framework, pytest, Flutter test, Jest/Vitest | Every commit |
| Integration | All module-to-module contracts; all external integrations against sandboxes | CI integration suite | Every merge |
| Contract | Every published API validated against its OpenAPI specification | Schemathesis / Dredd-class validation | Every merge |
| Event | Every producer/consumer pair for schema compatibility and idempotency | Schema registry compatibility check + replay test | Every merge |
| End-to-end | **Every one of the 15 critical business journeys** | Playwright (web), Patrol/integration_test (Flutter) | Nightly |
| Performance | Every NFR performance target **at 1.5× expected peak** | k6 / Locust | **Before each wave gate** |
| Security | SAST, DAST, dependency and container scanning every build; penetration test annually | Semgrep-class SAST, ZAP-class DAST, SCA, Trivy-class container scan | Every build + annual |
| Accessibility | WCAG 2.1 AA automated scan **plus manual audit per portal** | axe-core + manual | Before each portal release |
| Localisation | Translation completeness, **Bengali rendering**, formatting, layout under text expansion | Translation coverage report + visual test | Before each wave gate |
| **Offline** | **24-hour offline operation with a scripted conflict scenario set** | Custom offline harness (§16.5) | **Before each mobile release** |
| Data migration | Reconciliation and control totals on every load | Migration test harness (§19) | Before every cutover |
| UAT | Every P0 and P1 requirement, by **named business super-users** | UAT environment on production-clone masked data | Before each wave gate |

---

## 14. SECURITY, DATA PROTECTION & COMPLIANCE ARCHITECTURE

### 14.1 Defence in Depth — the Layers

```
┌─ EDGE ───────────────────────────────────────────────────────────────────────┐
│  CDN · DDoS mitigation · bot management · WAF with OWASP Core Rule Set       │
├─ INGRESS ────────────────────────────────────────────────────────────────────┤
│  Kong + Nginx · TLS 1.3 · OAuth2 introspection · per-consumer rate limits     │
│  (NFR-013, NFR-068)                                                          │
├─ IDENTITY ───────────────────────────────────────────────────────────────────┤
│  Keycloak 26.x · SSO · MFA · step-up · federation · session policy           │
│  46 roles · 6 isolation tiers · 30 SoD controls (NFR-011/012/064/065/069)     │
├─ APPLICATION ────────────────────────────────────────────────────────────────┤
│  Record rules (operating-unit) · field permissions (CD-130) · SoD (CD-132)   │
│  No business logic in portals (AS-09, PS-11) · server-side scope (API-10)     │
├─ DATA ───────────────────────────────────────────────────────────────────────┤
│  AES-256 at rest · field-level encryption for S3 (NFR-061) · split residency │
│  Soft delete · referential integrity · decimal money (DI-01/03/08)            │
├─ AUDIT ──────────────────────────────────────────────────────────────────────┤
│  Immutable trail — who, what, when, before, after (NFR-014)                   │
│  Privileged session recording (NFR-070) · access logging on every T5 read     │
├─ OPERATIONS ─────────────────────────────────────────────────────────────────┤
│  Vault secrets · no standing access · masked non-production · ClamAV uploads  │
│  SAST/DAST/SCA in CI · Wazuh in production · annual penetration test          │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 14.2 Regulatory Position — Verified 13 August 2026

| Statute | Status | Technology obligation |
|---|---|---|
| **Personal Data Protection Act 2026 (Law 63 of 2026)** | **In force**, enacted April 2026; enforcement ~13 May 2027 (**inside Wave 4**) | §14.3, §14.4 — consent, transparency, DSR, breach notification, split residency |
| **Cyber Security Ordinance 2025** | **In force** (21 May 2025) | Security controls, incident reporting, lawful data handling |
| Cyber Security Act 2023 | **Repealed** by the 2025 Ordinance | — |
| Digital Security Act 2018 | **Repealed** by the 2023 Act, itself repealed | **Every v1.0 reference is void** |
| ICT Act 2006 | In force | Electronic records, evidence |
| VAT & Supplementary Duty Act 2012 | In force | Mushak 6.3, Mushak 9.1, input-credit control |
| Bangladesh Labour Act 2006 (as amended) | In force | Payroll, working time, safety records |
| Bangladesh Labour Rules 2015 | In force | HSE obligations |

**Every citation carries a *verified-on* date under rule DoD-17, and each is re-verified at the wave
gate of the module that depends on it.** A regulatory citation that was correct at specification time
and is not re-checked at build time is exactly how the Digital Security Act 2018 reference survived
into v1.0 two repeals after it ceased to exist.

### 14.3 PDPA Technology Architecture

| Obligation | Component | Where it lives |
|---|---|---|
| **Consent registry** — purpose-scoped, versioned, withdrawable | **CD-148** | M33, surfaced in P01 |
| **Transparency notice** — versioned, bound to the consent record | CD-148 + Payload CMS versioned content | M33, P01 |
| **Data-subject request orchestration** — access, portability, rectification, erasure, withdrawal | **CD-248** | M33, M29, surfaced in P01 and P03 |
| **Residency enforcement** | **CD-233** | M29 |
| **Processing record** retained 5 years | CD-109 retention class | M24 |
| **Breach notification** to the National Data Management Authority | Incident runbook + notification register | M60 |
| **Processor register** with contractual flow-down | M60 register; applies to every L6 component | M60, M42 |
| **Chief Data Officer** support | Role R40 + CDO console in P03 | M60 |

**The rectification obligation is the one most often under-built.** NFR-093 requires **notification
to the controller within 30 days** of a rectification. In a 67-module system a customer's corrected
address exists in the party master, in open service orders, in dispatch routing, in invoices already
issued, in the warehouse and in the search index. CD-248 propagates the correction through the event
bus and records the propagation — it does not simply update one row.

### 14.4 Split Residency — the Enforcement Mechanism

**One gateway, one enforcement point, one audit point.**

```
Application code
      │
      │  reads/writes a field marked residency = restricted
      ▼
┌──────────────────────────────────────────────────────────────┐
│  ORM residency guard (CD-233 client)                         │
│  ▸ Field-level `residency` attribute from the model registry │
│  ▸ A classified write routed to the regional store is        │
│    REJECTED at write time — not logged and allowed (NFR-086a)│
└───────────────────────┬──────────────────────────────────────┘
                        │ only path
                        ▼
┌──────────────────────────────────────────────────────────────┐
│  RESIDENCY SERVICE — CD-233  (trust zone boundary Z2 → Z4)   │
│  ▸ Step-up authentication check for T5 access (NFR-065)      │
│  ▸ Purpose and legal-ground check against the consent registry│
│  ▸ Access logged — who, what field, which subject, when, why │
│  ▸ Transfer gate: cross-border requires an Authority         │
│    notification record to exist BEFORE execution (NFR-086b)  │
│  ▸ Envelope encryption with key material separate from the   │
│    database key (NFR-061)                                    │
└───────────────────────┬──────────────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────────┐
│  Z4 — BANGLADESH-RESIDENT POSTGRESQL 16                      │
│  NID · passport · TIN · biometric templates · recovered      │
│  customer data · seller KYC · criminal record checks         │
│  Joined to the regional record by RESIDENT KEY only          │
│  Never duplicated to the regional store — not in a cache,    │
│  not in a log, not transiently                               │
└──────────────────────────────────────────────────────────────┘
```

**Three tests make this real rather than documented:**

| Test | Assertion |
|---|---|
| **Negative write test** | Attempting to write a classified field to the regional store is **rejected**, and the rejection is asserted in CI |
| **Log-scrubbing test** | A classified value never appears in application logs, error traces, APM payloads or exports (OPS-04) |
| **Non-production scan** | No unmasked classified value exists in `local`, `dev`, `staging`, `training` or `dr`-non-resident, in any region (NFR-086c) |

### 14.5 Data Classification

| Class | Definition | Storage | Examples |
|---|---|---|---|
| **S0 Public** | No restriction | Any | Service catalogue, branch directory, published prices |
| **S1 Internal** | Company-internal | Regional | Operational metrics, internal procedures |
| **S2 Confidential** | Restricted by role | Regional, access-controlled | Customer contact details, pricing agreements, supplier terms |
| **S3 Restricted** | **Field-level encrypted, access-logged** | **Z4 resident where residency-classified** | NID, passport, TIN, biometric, bank details, payroll, recovered customer data, KYC documents, call recordings |

**S3 and residency classification overlap but are not identical.** Every residency-classified field is
S3; not every S3 field is residency-classified (individual payroll amounts are S3 but not restricted
from regional storage; a TIN is both). The model registry carries both attributes independently, and
the enforcement paths are separate: **S3 triggers field-level encryption and access logging;
residency classification triggers Z4 routing.**

### 14.6 Bangladesh Tax Technology

| Obligation | Component | Detail |
|---|---|---|
| **Mushak 6.3 tax invoice** | CD-083 + CD-238 | NBR-prescribed format; BIN presentation; sequence rules; **Bengali rendering verified**; supplier-signable; **preserved 5 years** |
| **Mushak 9.1 monthly return** | CD-195 | Assembled from the VAT register; **filed by the 15th of the following month via vat.gov.bd** (NFR-100); manual portal filing is the tested fallback |
| **Input VAT credit control** | CD-084 | **Hard block** on a credit claim without a valid compliant Mushak 6.3 (NFR-101) |
| **VAT register** | CD-084 | Output and input VAT by period, reconcilable to the ledger (DI-02) |
| **TDS / withholding** | CD-085 + CD-196 | Section-wise deduction at source; certificate generation |
| **BIN / TIN validation** | CD-086 + CD-233 | Format and checksum validation; TIN is residency-classified |
| **Income tax and payroll statutory** | CD-198, CD-211, CD-212 | Progressive slabs, investment rebate, PF, gratuity |
| **Fiscal year July–June** | Odoo configuration | Period close, reporting calendar |

**Why the tax pack is L5 and cannot be otherwise.** Odoo's tax engine computes tax; it does not
produce a Mushak 6.3 in NBR's prescribed form, does not assemble a Mushak 9.1, does not know
Bangladesh's TDS sections, and does not block an input credit without a compliant invoice. None of
this exists in OCA or any open-source component. It is also the part of the stack **most likely to
change during the programme**, which is why it is built as a **versioned rule pack** — statutory
rates and thresholds are configuration with an effective date, not constants in code (BR-STD-03,
BR-STD-07).

---

## 15. LOCALISATION & ACCESSIBILITY TECHNOLOGY

### 15.1 Bengali Language Technology

| Aspect | Technology | Standard |
|---|---|---|
| Encoding | **UTF-8 throughout** — database, API, files, print | Absolute |
| Collation | **ICU `bn-BD`** for sorting and comparison | PostgreSQL ICU collation |
| Web i18n | `next-intl` with ICU message format | Next.js portals |
| Mobile i18n | Flutter `.arb` with ICU message format | All 4 Flutter apps |
| ERP i18n | Odoo `.po` translation files | Odoo web and reports |
| Notification i18n | Novu locale-specific templates | All 6 channels |
| **Print / PDF** | **CD-238 with OpenType shaping** — conjuncts, reordering vowel signs, ligature substitution | Invoices, Mushak 6.3, payslips, service reports, certificates |
| Fonts | Self-hosted Bengali subset (web) · bundled (mobile) · **embedded in PDF** | Renders identically across Android, iOS, Windows and print |
| Input | Phonetic and Unicode keyboard support; **voice-to-text on mobile** (CD-246) | NFR-074 |
| Search | PostgreSQL FTS with `pg_trgm` and ICU `bn-BD` | NFR-035 ≤ 600 ms p95 |
| Translation quality | **Professionally translated, reviewed by a native speaker. Machine translation is not acceptable for release** | AS-12, DoD-08 |
| Completeness | **100% of user-facing strings before any module is accepted** | CI translation-coverage report |

**Bengali is not a font problem, and treating it as one is the standard failure mode.** It is a
complex script requiring proper text shaping. A PDF generated without OpenType shaping produces
output that passes an automated test and is wrong to a reader — on a Mushak 6.3 that is a compliance
defect. **Bengali print output is verified on every supported printer as a wave-gate item**, and
layout is tested under Bengali text expansion, which commonly runs 15–30% longer than English.

### 15.2 Formats

| Aspect | Standard | Technology |
|---|---|---|
| Numbers | **Lakh/crore grouping (12,34,567)** in the Bengali locale; international grouping in English | CD-136 locale pack |
| Currency | **BDT (৳)** primary, two decimals; multi-currency supported | Odoo currency + CD-136 |
| Date | DD/MM/YYYY; **Bengali month names** in the Bengali locale | CD-136 |
| Time | 12-hour with **Bengali AM/PM equivalents**; stored UTC, displayed Asia/Dhaka | AS-11 + CD-136 |
| Calendar | Gregorian with **Bangladesh public holidays including moon-dependent dates** | CD-136 — moon-dependent dates are data with an effective date, updated annually, not computed |
| Fiscal year | July–June | Odoo configuration |
| **Address** | **Division → District → Upazila/Thana → Union/Ward → Postcode** | **CD-035 `cd_bd_address`** — 8 divisions, 64 districts |
| Phone | **+880** with Bangladesh mobile operator prefix validation | CD-035 |
| National ID | **10-digit and 17-digit** formats validated; **residency-classified** | CD-086 + CD-233 |

### 15.3 Accessibility Technology

| Requirement | Technology | Verification |
|---|---|---|
| **WCAG 2.1 AA on all web portals** (contracted) | Design system components built accessible by construction — semantic HTML, ARIA where required, focus management, colour contrast tokens | **axe-core in CI + manual audit per portal release** |
| Keyboard operability | Full keyboard navigation; visible focus; logical tab order; keyboard-first for high-volume roles | Manual audit |
| Screen reader support | Semantic markup, live regions for status changes, meaningful labels | Manual audit with NVDA/TalkBack |
| Colour and contrast | Contrast tokens meeting AA; **never colour alone to convey status** | Automated contrast check |
| Text sizing | Relative units; layout survives 200% zoom | Visual regression at 200% |
| Mobile accessibility | Touch targets ≥ 44 px; **gloved-hand operability for field use**; high-contrast outdoor mode | Field usability test |
| **Drag-and-drop alternative** | **Every drag interaction on the P03 dispatch board has a keyboard and single-pointer equivalent** | Manual audit — required under 2.1 for persona A-06 and explicitly under 2.2 SC 2.5.7 |
| Situational accessibility | Bright sunlight, gloves, noise, one-handed use, low battery, poor connectivity | Field usability test |

---

## 16. OFFLINE & LOW-CONNECTIVITY TECHNOLOGY

**This is the hardest technical requirement in the programme.** P02, P09 and P11 must operate for
**24 hours with no connectivity and no data loss**, and sync within **30 seconds** of reconnection on
a 3G connection. The consequence of getting it wrong is not a degraded feature — it is a technician
who cannot tell whether four hours of work is safe.

### 16.1 The Offline Engine

**One engine, shared across APP-01 (technician), APP-02 (rider) and APP-03 (auditor).** Building
three would produce three sets of conflict-resolution bugs.

| Aspect | Technology |
|---|---|
| Local store | **Encrypted SQLite (SQLCipher)** — key derived from device credentials, wiped on remote revocation |
| Journal | **Append-only action journal.** Every user action is a discrete, idempotent command with a **client-generated UUID** (AS-13) |
| Data scope | Only the user's assigned work plus the reference data they need; **scope re-evaluated on every sync** |
| Upload | Commands replayed **in order** on reconnection; server acknowledges each **by UUID** |
| Download | **Delta since the last successful sync token**; full refresh available on demand |
| Batching | Per-batch checksums; a failed batch is **retried whole, never partially applied** (DI-04) |
| Evidence | Photos and video captured locally, encrypted, uploaded on a deferred low-priority channel so evidence upload never delays state sync |
| Pruning | Automatic pruning of synced, closed work older than the retention window |
| Integrity | Server-side idempotency ledger of processed command UUIDs |

### 16.2 Conflict Resolution — the Rules

| Domain | Authority | Rationale |
|---|---|---|
| **Assignment** | **Server** | Dispatch may have reassigned the job |
| **Pricing** | **Server** | The price book may have changed |
| **Stock** | **Server** | Another technician may have consumed the part |
| **State** | **Server** | The order may have been cancelled or put on hold |
| **Evidence** (photos, video, voice notes) | **Client** | It was captured in the field and cannot be recreated |
| **Notes and diagnosis** | **Client** | The technician's own observation |
| **Field timestamps** | **Client** | When work actually happened |

**The rule that makes this usable rather than merely correct: any resolved conflict is shown to the
user, with what changed and why.** The system never silently picks a winner on something a technician
entered by hand.

**Worked example.** A technician completes a job offline at 11:20. Dispatch reassigned that job at
10:55. On sync, the **server's reassignment wins** — but the technician's **diagnosis, photographs
and time entries are preserved and attached to the job**, and the technician is shown: *"This job was
reassigned to another technician at 10:55 while you were offline. Your work has been saved to the
job."* Nothing is lost, and nothing is silently overwritten.

### 16.3 What the User Must Always Be Able to See

| Requirement | Technology |
|---|---|
| Whether the device is online or offline | Persistent, unambiguous status indicator |
| **Whether work is saved on the device** — distinct from **sent to the office** | Two distinct states with distinct indicators. This distinction is the single most important UX decision in the offline design |
| How many actions are queued | Queue count, always visible |
| When the last successful sync occurred | Timestamp, always visible |
| Whether a sync failed, and what to do | Explicit failure state with an action, in Bengali |

### 16.4 Degraded Connectivity — Portals

| Portal | Degraded behaviour |
|---|---|
| P01 Customer | PWA shell + cached catalogue and open orders; **booking queued with confirmation on recovery**; tracking falls back to polling |
| P03 Admin | Cached list views; write operations queue with explicit pending state |
| P04, P07, P08, P10, P12 | Cached read; writes blocked with a clear message rather than a silent failure |
| P06 Analytics | Last-loaded dashboard retained with a staleness timestamp |

### 16.5 Offline Test Harness

**Offline correctness cannot be verified by inspection.** A dedicated harness runs before every mobile
release:

| Scenario class | Examples |
|---|---|
| Duration | 24-hour offline with continuous work; 48-hour offline (beyond guarantee) with graceful behaviour |
| Conflict | Reassignment during offline; price change during offline; part consumed elsewhere; order cancelled during offline; concurrent edit by two technicians |
| Failure | Sync interrupted mid-batch; battery death mid-sync; app killed mid-write; storage full; clock skew on the device |
| Volume | 200 queued actions; 500 evidence photos pending upload |
| Network | Sync on 3G, on 2G, on an intermittent connection that drops every 10 seconds |
| Security | Device lost — remote revocation wipes the local store; local store not readable without device credentials |

**Every scenario asserts two invariants: zero data loss and zero double-application (DI-04).**

---

## 17. OBSERVABILITY & OPERATIONS TECHNOLOGY

### 17.1 The Observability Stack

```
Application code · Odoo · Next.js · Flutter · domain services
        │  OpenTelemetry SDK — traces, metrics, logs, one correlation id
        ▼
   OpenTelemetry Collector
        │
        ├──► Prometheus ──► metrics, alert rules
        ├──► Loki       ──► structured logs (personal data scrubbed)
        └──► Tempo      ──► distributed traces
                 │
                 ▼
              Grafana ──► dashboards · alerting · on-call routing via Novu
```

**One correlation id spans the whole journey** (NFR-092-M): injected by Kong, propagated through
Odoo, the domain services, the event bus and back into the portal response. A support engineer takes
a correlation id from a user's error message and sees the entire request path.

### 17.2 What Is Monitored

| Layer | Signals | Alert threshold |
|---|---|---|
| Business | Orders created, jobs completed, invoices raised, payments received, SLA breaches | Deviation from expected volume band |
| Integration | Availability, error rate, latency p95, queue depth, dead-letter count, webhook failures, credential expiry | Per `05-03` §7 — availability < 99% over 15 min; error rate > 2% over 5 min; dead letters > 0 for 1 h; **credential expiry 30 days ahead** |
| Application | Request rate, error rate, latency percentiles, worker saturation, job success | NFR targets |
| Data | Replication lag, connection pool saturation, slow queries, table and index bloat, partition health | Replication lag > 30 s |
| Infrastructure | CPU, memory, disk, network, container restarts | Standard thresholds |
| Security | Failed authentications, privilege changes, T5 access, anomalous data export | Any privilege escalation; any anomalous export |
| **Offline sync** | Sync success rate, sync duration, conflict rate, queue depth per device | **Any sync failure — target is zero** |
| Cost | Infrastructure spend against the wave budget; third-party API consumption | Monthly variance > 15% |

### 17.3 Alert Discipline

| Rule | Detail |
|---|---|
| OPS-03 | **Every alert has a runbook entry. Alerts without an action are removed** |
| Severity | Sev1 business-stopping · Sev2 degraded · Sev3 informational. Only Sev1 pages out of hours |
| Routing | Alerts route to the **owning role**, not to a shared inbox (Grafana → Novu) |
| Noise | Alert volume is reviewed at every wave gate; a persistently firing alert is a defect in the alert or the system, never background noise |
| Silent failure | **OPS-05 — every scheduled job reports success, failure and duration. A job that fails silently is a defect** |

### 17.4 Operational Standards for the Stack Itself

| Component | Standard |
|---|---|
| **Keycloak** | **No LTS line exists — must be kept current continuously**, not pinned for a wave. Monthly review; security releases applied within the standard window (TR-08) |
| Odoo | Pinned as a submodule; patch releases applied monthly; **major version per §4.4** |
| OCA subtrees | Updated on a controlled cadence; every update regression-tested in staging |
| PostgreSQL | Minor versions applied monthly; **major version currency reviewed annually (§25.2)** |
| All components | **Pinned versions; automated vulnerability alerts; monthly update cycle** (RFP §5.10) |
| Licence watch | Every AGPL/BSL/TSL/fair-code component monitored for upstream licence change; fallback named (TR-09) |

---

## 18. ENVIRONMENTS, CI/CD & ENGINEERING PRACTICE

### 18.1 Repository Structure

| Aspect | Standard |
|---|---|
| Structure | **Monorepo** — Odoo as a pinned submodule, OCA as subtrees, custom modules and services as first-class directories (TD-15) |
| Rationale | Cross-cutting changes across 248 CD items and 10 applications are routine; a polyrepo makes an atomic change across three modules a three-PR coordination problem |
| Branching | `main` (production) ← `release/*` ← `develop` ← `feature/*`, `fix/*`; `hotfix/*` from `main` |
| Commits | `<type>(<scope>): <subject>` — feat, fix, docs, style, refactor, test, chore, perf |
| Ownership | **All source, configuration, migrations, tests and documentation are 1000FiX property, delivered continuously to a Company-controlled repository — not at milestones** |

### 18.2 The CI Pipeline

| Stage | Checks | Blocks merge |
|---|---|---|
| Pre-commit | Formatting, linting, Odoo-specific checks, **secret scanning** | Local |
| Lint & type | Python, JavaScript/TypeScript, Dart; **naming conventions (AS-04)** | ✔ |
| **Model registry** | AS-02 chatter mixins · AS-03 company/operating-unit fields · **AS-14 field-level residency and S3 classification** | ✔ |
| Unit tests | ≥ 80% coverage; **100% on financial and tax paths** | ✔ |
| Integration tests | Module-to-module contracts; external integrations against sandboxes | ✔ |
| **Contract tests** | OpenAPI 3.1 validation; **PS-11 portal contract test — invalid payload posted directly to the API must be rejected** | ✔ |
| Event tests | Producer/consumer schema compatibility; **AS-08 outbox coverage**; idempotency | ✔ |
| Security | SAST, dependency scan, container scan, IaC scan | ✔ on high/critical |
| **Architecture** | **AS-01 no cross-module table access · AS-05 no OCA fork · AS-09 no logic in views/portals · AS-10 no float money** | ✔ |
| Localisation | **Translation completeness at 100%** | ✔ |
| Bundle budget | **Critical customer paths < 400 KB** | ✔ |
| Accessibility | axe-core on portal builds | ✔ on violations |
| Build verification | Container build, migration dry run against a production-sized clone | ✔ |

### 18.3 Deployment

| Environment | Trigger | Gate |
|---|---|---|
| `dev` | Automatic on merge to `develop` | CI green |
| `staging` | Manual promotion | CI green + integration suite |
| `training` | Manual, per training cycle | Curated data load |
| `prod` | **Manual gate** | Wave-gate acceptance + change approval + rollback rehearsed (DoD-16) |
| `dr` | Continuous replication | DR drill twice yearly |

**Zero-downtime deployment (NFR-008)** requires forward-only, backward-compatible migrations
(OPS-07): a release adds a column before code uses it and removes a column only after no code
references it — two releases, never one.

### 18.4 Secrets and Configuration

| Aspect | Standard |
|---|---|
| Secrets | **Vault-managed. Never in the repository, configuration files or logs** (NFR-062, IP-07). Rotation scheduled; expiry alerted 30 days ahead |
| Configuration | **Versioned and promoted through environments, never hand-edited in production** (OPS-02) |
| Feature flags | **CD-135** — any new capability disableable without a deployment (OPS-06) |
| Environment parity | Same container images across environments; only configuration differs |

### 18.5 Dependency Management

| Aspect | Standard |
|---|---|
| Pinning | **Every dependency pinned to an exact version** — Python, Node, Dart, container base images, OCA commits |
| Vulnerability alerts | Automated, with a defined response window by severity |
| Update cadence | **Monthly** review and update cycle; security patches out of cycle |
| Odoo/OCA | Odoo submodule pinned; OCA subtrees updated on a controlled cadence with staging regression |
| Licence check | Automated licence scan on every dependency addition; **AGPL, BSL, TSL and fair-code components require architecture approval** |

### 18.6 Definition of Done — Technology Items

A module is not accepted until every item is true (from `02-02` §8):

| # | Criterion | Technology gate |
|---|---|---|
| DoD-03 | Unit coverage ≥ 80%; **100% financial and tax** | CI coverage gate |
| DoD-04 | Business rules at the model layer, negative-tested **through both UI and API** | Contract test |
| DoD-05 | Domain events published through the outbox and registered in the event catalogue | Event coverage test |
| DoD-06 | APIs documented in OpenAPI 3.1 and published | CI specification gate |
| DoD-07 | Access control, record rules and field permissions defined and **negative-tested for every applicable role** | Permission test suite |
| DoD-08 | **Bengali translation complete** for all user-facing strings | Translation coverage report |
| DoD-09 | KPIs instrumented with allocated `KPI-nnn` identifiers, visible in M25 | Metric registry check |
| DoD-11 | Operational runbook written | Wave-gate checklist |
| DoD-14 | Performance tested against applicable NFRs **at 1.5× expected peak** | Performance gate |
| DoD-15 | Security review with **zero open high or critical findings** | Security gate |
| DoD-16 | **Rollback plan documented and rehearsed** | Deployment gate |
| DoD-17 | **Regulatory citations verified current, with a verified-on date** | Compliance gate |

---

## 19. DATA MIGRATION TECHNOLOGY

### 19.1 Source Landscape and Tooling

| Source | Technology to extract | Target | Wave |
|---|---|---|:--:|
| Per-branch service order spreadsheets | Structured ingest with per-file mapping and validation | M01, M04 | W2 |
| Workshop whiteboards and paper job cards | Manual capture of open WIP only; **history not migrated** | M31 | W2 |
| `station.1000fix.com` order tracking | Database extract | M01, P01 | W2 |
| Legacy tracker `123.0.26.238/orderTracking` | Database extract | M01, P01 | W2 |
| Branch inventory spreadsheets | Structured ingest with reconciliation to a physical count | M15 | W2 |
| Standalone accounting software | **Balances and open items only** — not transaction history | M19, M20, M52 | W3 |
| AMC tracking spreadsheets | Structured ingest | M08 | W4 |
| Email-based warranty claims | Open claims only | M09 | W4 |
| Manual payroll in Excel | Employee master, YTD balances, statutory balances | M56 | W5 |
| Attendance sign-in books | **Not migrated** — opening balances only | M55 | W5 |
| Customer contact data (multiple sources) | Deduplication and merge under CD-147 | M33 | W1 |

### 19.2 Migration Standards

| # | Standard |
|---|---|
| MIG-01 | Every migration is **repeatable and idempotent** — a re-run produces the same result |
| MIG-02 | **Control totals on every load** — record count, value total, checksum — reconciled before the load is accepted (DI-06) |
| MIG-03 | Every migrated record carries its **legacy reference**, permanently (FR-SRM-088 legacy order lookup) |
| MIG-04 | **Dry run against production-sized data before every cutover** (DoD-10) |
| MIG-05 | Data quality is assessed and reported **before** migration; the business decides what to cleanse, what to migrate as-is and what to leave behind |
| MIG-06 | **Personal data is migrated under the same residency and classification rules as new data** — a migrated NID goes to Z4, not to the regional store |
| MIG-07 | Rollback plan per migration, rehearsed |
| MIG-08 | Legacy systems are decommissioned only after **reconciliation sign-off**, not on go-live day |

**MIG-06 is the one most easily missed.** A migration script is written to load data quickly, and
residency enforcement is a runtime ORM check that a bulk loader can bypass. **The migration path uses
the same residency service (CD-233) as the application path** — bulk-loading classified fields
directly into the regional store would create exactly the compliance breach the architecture exists
to prevent, at scale, on day one.

---
---

# PART D — DELIVERY & COMMERCIAL

---

## 20. WAVE-BY-WAVE TECHNOLOGY DEPLOYMENT

### 20.1 Wave 0 — Pre-Build (before Wave 1 starts)

**Wave 0 is not in the RFP's wave plan and it must be.** Six activities cannot be done inside Wave 1
without putting Wave 1 at risk, and all six are technology activities.

| # | Activity | Deliverable | Blocks |
|---|---|---|---|
| **W0-01** | **OCA v19 migration assessment** — per-module status for all 140+ modules across 18 repositories | Status matrix; migrate/defer/reclassify decision per gap | **Wave 1 architecture fix** |
| **W0-02** | **Split-residency legal opinion (DEP-31 / D-13)** | Confirmed field classification list | **Wave 1 data model** |
| **W0-03** | **Register completion** — roles to R46 with R60 eliminated, SOD-13…30 registered, KPI collisions resolved, NFR-090/091/092 collision resolved | Clean identifier registers | **Wave 1 permission model and instrumentation** |
| **W0-04** | **Odoo version decision (D-15)** — baseline and upgrade slot | Baselined plan including the upgrade window | Wave 5/6 planning |
| **W0-05** | **Next.js 15 → 16 assessment** including Payload CMS 3 compatibility | Upgrade decision and plan | **Wave 2 portal build** |
| **W0-06** | Environment ladder, CI pipeline, Vault, monorepo, container registry | Working `local`, `dev`, `staging` with the full CI gate set | All build |

> **W0-01, W0-02 and W0-03 are blocking.** Beginning Wave 1 without them means building the
> permission model on 38 roles when 46 are needed, fixing the data model before knowing which fields
> are residency-classified, and discovering OCA gaps in Wave 2 when the wave is already committed.

### 20.2 Technology Deployment by Wave

| Wave | Months | Modules | **Technology entering service** |
|---|---|---|---|
| **W1** Foundation & Service Core | 1–4 | M29, M28, M30, M33, M37, M17*, M01*, M04 (8) | **PostgreSQL 16 + PgBouncer · Bangladesh-resident store (Z4) + CD-233 residency service · Keycloak (HA) · Kong · Redis · MinIO · Nginx · Docker/K3s · n8n · Novu + CD-234 · Odoo 19 CE (11 modules) · OCA operating-unit, partner-contact, server-tools, web, helpdesk, field-service core · P03 Admin Portal · outbox CD-125 · Vault · CI pipeline** |
| **W2** Field Operations & Inventory | 5–8 | M31, M02, M15, M10, M64, M01*, M17* (7) | **Traccar · OSRM · VROOM · TimescaleDB · Grafana · CD-235 dispatch scoring · CD-236 route orchestrator · CD-237 telemetry collector · APP-01 technician app (Flutter, offline engine) · APP-05 customer portal (Next.js) · Odoo `stock` · OCA stock-logistics-* · barcode** |
| **W3** Money & Movement | 9–13 | M19, M20, M52, M50, M11*, M36, M03, M16, M41, M24, M63 (11) | **OpenTelemetry + Prometheus + Loki + Tempo · CD-238 document generation (Bengali PDF) · CD-239 pricing engine · CD-240 OCR · CD-241 reconciliation · OCA `dms` · payment connectors (bKash, Nagad, SSLCOMMERZ) · Odoo `account`, `purchase`, `sale`, `fleet`, `website`, `portal` · APP-02 rider app · P05 vendor portal · CD-218 mobile safety reporting** |
| **W4** Agreements & Contact | 14–18 | M08, M09, M39, M51, M53*, M27, M32, M34, M25, M62*, M42 (11) | **Metabase · CD-242 settlement engine · CD-243 warehouse ETL (dbt) · CD-248 DSR orchestrator · L6 cloud telephony · L6 qualified e-signature · OCA `contract`, `mis-builder`, `reporting-engine` · APP-06 B2B · APP-07 brand · APP-08 contact centre · P06 analytics · NBR e-VAT (INT-038)** |
| **W5** People & Managed Services | 19–22 | M21, M55, M56, M57, M22, M23, M05, M45, M46, M49 (10) | **Mayan EDMS + CD-236 document migration · MeshCentral/RustDesk · Wazuh · osquery · CD-244 RMM collector · Odoo `hr`, `hr_attendance`, `hr_holidays`, `hr_expense`, `maintenance` · OCA hr/payroll, management-system, account-financial-tools · APP-03 auditor app · BEFTN (INT-005) · biometric devices (INT-041)** |
| **W6** New Business Lines | 23–26 | M13, M14, M06, M26*, M43, M44, M54, M58, M59, M60, M61, M66 (12) | **Redpanda/Kafka (event bus migration from Redis Streams) · MLflow · Ollama · CD-245 ML inference gateway · CD-247 event replay · Odoo `sale_renting` · APP-04 customer mobile app · corporate SSO federation (INT-046)** *— and the Odoo major-version upgrade slot if Option A is adopted (§4.4)* |
| **W7** Marketplace & Settlement | 27–30 | M38, M12, M40, M11*, M53*, M47, M67 (7) | **L6 KYC / identity verification · APP-09 seller portal · APP-10 partner portal · ad delivery (INT-037) · client ITSM (INT-047) · seller payout rail (INT-007)** |
| **W8** Intelligence & ESG | 31–34 | M62*, M26*, M48, M18 (4) | **ClickHouse · warehouse migration from the read replica · CD-246 speech-to-text · IoT ingestion at scale · e-waste authority reporting (INT-040)** |
| **W9** Expansion | 35–36 | M65 (1) | **Multi-entity, multi-country localisation · international payments (INT-008) · freight forwarder (INT-027) · company registry (INT-042)** |

*Modules marked `*` are delivered across two waves; their effort is split.*

> **Wave module counts are taken verbatim from `02-02` §4.2** (8 · 7 · 11 · 11 · 10 · 12 · 7 · 4 · 1 =
> 67). The register's wave view is known to omit M07's W1 portion and M25's W8 portion, which is an
> inherited inconsistency disclosed in BRD §23.9 finding BA-04; the counts above match the
> authoritative register rather than reconciling it independently.

### 20.3 The Wave 1 Technology Load

**Wave 1 is the heaviest technology wave in the programme and this is often underestimated.** Eight
modules is the second-smallest module count of any wave, but Wave 1 stands up **fifteen distinct
infrastructure components plus the entire engineering pipeline** — because almost everything else
depends on them.

| Category | Wave 1 components |
|---|---|
| Data | PostgreSQL 16, PgBouncer, **Bangladesh-resident store**, Redis, MinIO |
| Identity & access | **Keycloak (HA)**, Vault, 46 roles, 6 tiers, 30 SoD controls |
| Integration | **Kong**, n8n, **outbox CD-125**, Redis Streams |
| Communication | **Novu + CD-234** *(three waves ahead of its owning module M27 — §12.7)* |
| Compliance | **CD-233 residency service**, consent registry CD-148 |
| Application | Odoo 19 CE with 11 core modules, 6 OCA repositories, P03 |
| Engineering | Monorepo, 6 environments, full CI gate set, container registry, observability foundations |

**Consequence for sequencing:** a delivery plan that treats Wave 1 as "eight modules, the smallest
functional wave" will under-resource it. The register records W1 at ~180 PW against W3's ~200 PW and
W4's ~230 PW; the *infrastructure* content of W1 is the highest in the programme.

### 20.4 The Fifteen Critical Journeys — End-to-End Test Coverage

Each journey has an automated end-to-end test that runs nightly from the wave in which its last
component lands.

| # | Journey | Spans | Test from |
|---|---|---|:--:|
| 1 | Book online → dispatch → field repair → invoice → pay → close → survey | P01, M01, M02, M15, M20, M19, M34 | W3 |
| 2 | Walk-in intake → workshop repair → estimate → approval → QC → handover → pay | M04, M31, M01, M23, M20 | W3 |
| 3 | Pick & drop collection → workshop → return delivery → invoice | M03, P09, M31, M20 | W3 |
| 4 | Warranty job → claim → submission → approval → reimbursement → reconciliation | M09, P08, M20, M19 | W4 |
| 5 | AMC sale → activation → preventive schedule → visit → renewal | M08, M02, M20 | W4 |
| 6 | MSP alert → ticket → remote resolution → SLA → monthly service report | M05, P04, M25 | W5 |
| 7 | Marketplace order → seller quote → selection → job → review → commission → payout | M12, P07, M53, M20 | W7 |
| 8 | Rental reservation → delivery → return → damage assessment → billing | M13, M03, M20 | W6 |
| 9 | Trade-in → offer → intake → data wipe → refurbishment → grading → resale | M14, M06, M12 | W6 |
| 10 | E-waste collection → triage → destruction → recycling → disposal certificate | M18, M24 | W8 |
| 11 | Data recovery case → custody → recovery → handover → purge certificate | M06, M24, **Z4 resident store** | W6 |
| 12 | Purchase requisition → PO → receipt → inspection → three-way match → payment | M16, M15, M52, M19 | W3 |
| 13 | Payroll cycle → attendance lock → calculation → approval → BEFTN → payslips → posting | M55, M56, M19 | W5 |
| 14 | Complaint → non-conformance → root cause → CAPA → verification → closure | M34, M23 | W5 |
| 15 | Month-end close → reconciliation → **VAT return** → management pack | M19, M51, M25 | W4 |

---

## 21. INFRASTRUCTURE SIZING & CAPACITY

### 21.1 Steady-State Production Sizing (Wave 8)

| Component | Specification | Driver |
|---|---|---|
| Odoo application nodes | **4 × 8 vCPU / 32 GB**, 12 workers each | NFR-003 — 800+ concurrent internal users |
| Odoo cron nodes | 2 × 4 vCPU / 16 GB | Scheduled jobs isolated from user traffic |
| Odoo long-polling nodes | 2 × 2 vCPU / 8 GB | Real-time channels, dispatch board push |
| Next.js portal nodes | 3 × 4 vCPU / 8 GB (or serverless equivalent) | NFR-004 — 75,000+ concurrent portal users |
| Domain services | 4 × 4 vCPU / 16 GB | 16 services (CD-233…248) |
| **PostgreSQL primary** | **16 vCPU / 64 GB / 2 TB NVMe**, partitioned and tuned | 5M orders/year, 5M assets |
| PostgreSQL read replicas | 2 × 8 vCPU / 32 GB / 2 TB | Read and BI offload |
| **Bangladesh-resident store** | **4 × vCPU / 16 GB / 500 GB**, encrypted, HA pair | NFR-086 — regulatory, low volume |
| TimescaleDB | 8 vCPU / 32 GB / 4 TB with compression | 800 GPS/min + 50,000 telemetry/min |
| ClickHouse | 8 vCPU / 32 GB / 4 TB | NFR-039 analytical query |
| Redis | 4 vCPU / 16 GB | Sessions, cache, queues, locks |
| Event bus (Redpanda) | 3 × 4 vCPU / 16 GB | Durable events with replay |
| Supporting services | 3 × 8 vCPU / 32 GB | Keycloak, Kong, n8n, Novu, Metabase, Grafana, Traccar, VROOM/OSRM, Mayan, MinIO, Wazuh, MLflow |
| ML inference | 1 × 8 vCPU / 32 GB **+ GPU (optional)** | Ollama LLM inference; GPU only if latency requires |
| Object storage | **20 TB growing toward 50 TB** | NFR-060 |

> **Sizing note — the resident store is new.** The RFP §5.9 sizing table predates the split-residency
> decision and does not carry a line for the Bangladesh-resident store. It is added here. It is
> **small in volume and large in consequence**: a few hundred gigabytes, but it must be HA, encrypted
> with separate key material, hosted in Bangladesh, and it gates every T5 read in the system.

### 21.2 Capacity Progression by Wave

| Wave | Odoo nodes | PG primary | Additional stores | Supporting | **Monthly cost** |
|---|---|---|---|---|---|
| W1 | 2 × 4 vCPU/16 GB | 8 vCPU/32 GB/500 GB | Resident store, Redis, MinIO | Keycloak, Kong, n8n, Novu | **$450–700** |
| W2 | 2 × 8 vCPU/32 GB | 8 vCPU/32 GB/1 TB | + TimescaleDB | + Traccar, OSRM, VROOM, Grafana | **$800–1,200** |
| W3 | 3 × 8 vCPU/32 GB | 12 vCPU/48 GB/1 TB | + replica ×1 | + observability stack | **$1,200–1,800** |
| W4 | 3 × 8 vCPU/32 GB | 12 vCPU/48 GB/1.5 TB | + replica ×2 | + Metabase | **$1,600–2,400** |
| W5 | 4 × 8 vCPU/32 GB | 16 vCPU/64 GB/2 TB | | + Mayan, Wazuh, MeshCentral | **$2,000–3,000** |
| W6 | 4 × 8 vCPU/32 GB | 16 vCPU/64 GB/2 TB | + Redpanda | + MLflow, Ollama (+GPU option) | **$2,600–3,800** |
| W7 | 4 × 8 vCPU/32 GB | 16 vCPU/64 GB/2 TB | | + portal nodes ×3 | **$3,200–4,600** |
| W8 | 4 × 8 vCPU/32 GB | 16 vCPU/64 GB/2 TB | **+ ClickHouse** | | **$3,800–5,400** |
| W9 | 4 × 8 vCPU/32 GB | 16 vCPU/64 GB/2 TB | | | **$4,000–5,800** |

**Cumulative infrastructure: ~$8K (Year 1) · ~$19K (Year 2) · ~$44K (Year 3) — $52K–96K over three
years**, plus the Bangladesh-resident store from Wave 1.

### 21.3 High Availability

| Tier | HA design | Failure tolerance |
|---|---|---|
| Edge / CDN | Provider HA | Provider SLA |
| Ingress | Kong + Nginx HA pair behind a load balancer | Single-node loss |
| **Identity** | **Keycloak HA cluster from Wave 1** | Single-node loss — **non-negotiable, it is a total-outage dependency** |
| Application | ≥ 2 Odoo nodes from Wave 1; rolling deploys | Single-node loss; zero-downtime deploy |
| Portal | ≥ 2 Next.js instances | Single-node loss |
| **Data — primary** | Streaming replication to a hot standby + 2 read replicas | **Automated failover; RPO ≤ 15 min** |
| **Data — resident store** | HA pair in Bangladesh with encrypted replication | Single-node loss |
| Time series | TimescaleDB replica | Single-node loss |
| Event bus | 3-node Redpanda cluster | Single-node loss with no message loss |
| Cache | Redis with persistence + replica | Single-node loss; session continuity |
| Object storage | Erasure coding across nodes | Multi-disk loss |
| DR | **Warm standby, RPO ≤ 15 min, RTO ≤ 2 h, drilled twice yearly** | Region loss |

**No single-node critical component is acceptable in production.** The components where a single node
causes total outage are PostgreSQL primary, Keycloak, Kong and Nginx — all four are HA from Wave 1.

---

## 22. TECHNOLOGY COST MODEL

### 22.1 Software Licensing — Three-Year Cost

| Layer | Components | Licence | **3-year cost** |
|---|---|---|---|
| **L1** Odoo 19 CE | 23 modules | LGPL-3 | **$0** |
| **L2** OCA | 140+ modules, 18 repositories | LGPL-3 / AGPL-3 | **$0** |
| **L3** Third-party | 6 connectors | Various | **$0** |
| **L4** Standalone OSS | 24 systems | Apache-2.0 / MIT / BSD / AGPL-3 / PostgreSQL / ISC / GPL-2 / BSL | **$0** |
| **L5** Custom | 248 CD items + 10 applications | Proprietary to 1000FiX | **$0 licence** (development cost only) |
| **L6** Commercial | 4 components | Subscription | **$0–36,000** |
| | | **Total licence** | **$0–36,000** |

**Comparison — the counterfactual.** Odoo Enterprise licensing for the same user population over
three years is **$45,000–90,000**, and it would still not deliver field service at 1000FiX's
constraint model, Bangladesh statutory compliance, the marketplace, the MSP platform or the
split-residency architecture. The open-source position saves the licence and buys nothing that would
otherwise have been bought.

### 22.2 L6 Cost Detail

| Component | Basis | Monthly | 3-year | Trigger |
|---|---|---|---|---|
| Cloud telephony / CPaaS | Seats + minutes | $200–600 | $7,200–21,600 | W4 |
| Qualified e-signature | Per envelope | $100–400 | $4,800–14,400 | W4 |
| Identity verification / KYC | Per check | $0.30–0.80/check | Volume-dependent | W7 |
| Endpoint RMM agent | Per endpoint | $2–5/endpoint | **Conditional — Wave 5 pilot decision** | W5–W6 |
| | | | **$0–36,000 (envelope)** | |

**The RMM line is the one with volume-scaling exposure.** At $2–5 per endpoint per month, a
managed-services business that grows its contracted estate grows this cost linearly. **L6-04 requires
it to be modelled at 5× the contracted endpoint count before signing.**

### 22.3 Third-Party API Consumption

| Service | Basis | Monthly at scale |
|---|---|---|
| SMS (transactional + OTP) | Per message | $600–1,600 |
| WhatsApp Business | Per conversation | $400–1,100 |
| Google Maps Platform | Per request | $300–700 |
| Traffic data | Per request | $150–350 |
| Firebase Cloud Messaging | Free tier sufficient | $0 |
| Payment gateway fees | % of transaction value | Netted against revenue |
| Identity verification | Per check | $80–300 |
| Cloud storage egress | Per GB | $60–180 |
| Telephony (L6) | Per minute + seats | $200–600 |
| E-signature (L6) | Per envelope | $100–400 |
| **Total** | | **$1,890–5,230/month** |

**3-year third-party API total: $41,000–95,000.**

**Cost control mechanisms built into the stack:**

| Mechanism | Saving |
|---|---|
| **Self-hosted OSRM/VROOM instead of a commercial routing API** | $200–400/month avoided ongoing |
| **Self-hosted LLM (Ollama) instead of a hosted API** | Per-query cost eliminated at 250,000 interactions/month — and PDPA-compliant |
| **Self-hosted OCR and STT** | Per-page and per-minute cost eliminated |
| WhatsApp preferred over SMS where the customer has opted in | WhatsApp conversation cost < per-message SMS at volume |
| Geocode caching and address learning (FR-LOG-035) | Repeated Maps requests eliminated |
| Data-usage optimisation in the field app (FR-FSM-061) | Technician data cost and egress reduced |
| Novu channel fallback ordering | Cheapest effective channel first, escalating only on failure |

### 22.4 Three-Year Total Cost of Ownership

| Category | 3-year cost | Note |
|---|---|---|
| Software licensing — L1–L5 | **$0** | |
| Software licensing — L6 | $0–36K | 4 components, individually approved |
| Infrastructure / hosting | $52K–96K | Including the Bangladesh-resident store |
| Third-party APIs | $41K–95K | |
| **Implementation & custom development** | **$525K–855K** | **1,513 measured PW at approved unit rates** |
| Training & change management | $35K–65K | 46 roles, Bengali and English |
| Support & maintenance (Yr 2–3) | $60K–130K | |
| *Component sum* | *$713K–1,277K* | |
| **HEADLINE 3-YEAR TCO** | **$690K–1,150K** | As fixed by RFP §16.1 |

> **The component sum and the headline do not match, and the reason is stated rather than smoothed.**
> The headline is the Company's restated figure from measured effort at approved unit rates. The
> component sum is wider at both ends because it assumes every line lands at its extreme
> simultaneously. Both figures are carried in RFP §16.1 and BRD §19.1 with the same caveat; they are
> reproduced here so the technology cost model does not appear to contradict the commercial one.

**The distribution matters more than the total.** Licensing is **0%–3.1%** of TCO; implementation is
**76%–74%**. Any effort to reduce technology cost should be directed at implementation efficiency —
reuse, code generation, disciplined scope — not at further licence optimisation, where there is
almost nothing left to save.

> **Decision D-14 is open.** The Steering Committee has not decided whether to fund the restated
> figure, phase it across more waves, or cut scope. **The stack is designed so that Waves 8 and 9 —
> ClickHouse, IoT, speech-to-text, multi-country — can be removed cleanly without stranding earlier
> investment**, because analytics falls back to the read replica and the remaining capability is
> additive rather than foundational. Categories D, F, I and J are similarly removable. **What cannot
> be removed without redesign is anything in Waves 1–3**, and in particular the residency
> architecture, the identity model, the outbox and the offline engine.

---

## 23. TECHNOLOGY RISK REGISTER

| ID | Risk | Layer | P × I | Mitigation | Owner |
|---|---|---|:--:|---|---|
| **TR-01** | **Offline sync defects cause data loss or double-application in the field** | L5 | **H × H** | Append-only journal; client UUID + server idempotency ledger; per-batch checksums; **dedicated offline test harness (§16.5) as a release gate**; field pilot before general rollout | Solution Architect |
| **TR-02** | **Split-residency legal opinion (DEP-31) arrives late or changes the classification** | L5, data | **H × H** | Residency service and field-level classification built in Wave 1 **regardless of outcome**; classification is data, so a change is reclassification not redesign; W0-02 makes the opinion a pre-build deliverable | CTO / DPO |
| **TR-03** | **OCA v19 migration gap in `field-service` / `helpdesk` blocks Wave 2** | L2 | **H × H** | W0-01 assessment before Wave 1 architecture is fixed; 12–20 PW migration budget carried; **Wave 1 gate blocks Wave 2 start until closed**; contribute upstream | Implementation Partner |
| **TR-04** | **OCA modules forked rather than extended, making every future upgrade manual** | L2 | **M × H** | AS-05 CI enforcement; named architecture-board approval per fork; fork register reviewed at every wave gate with divergence tracked | Solution Architect |
| **TR-05** | **Odoo 19 leaves support before the programme reaches steady state (D-15)** | L1 | **H × M** | §4.4 Option A — schedule a major-version upgrade slot between W5 and W6, in the baselined plan, not in contingency | CTO |
| **TR-06** | **Next.js 15 falls behind the supported line across six portals (CON-03 version currency)** | L5 | **M × M** | §11.1 — treat 15→16 as a Wave 1 platform activity, before six applications are built on it; confirm Payload CMS 3 compatibility in W0-05 | CTO |
| **TR-07** | **Bengali rendering fails in PDF, print or on a peripheral** | L5 | **M × H** | OpenType shaping in CD-238; **Bengali print verified on every supported printer as a wave-gate item**; layout tested under Bengali text expansion | Solution Architect |
| **TR-08** | **Keycloak has no LTS — falling behind creates unpatched authentication** | L4 | **M × H** | Monthly currency review; security releases applied within the standard window; HA cluster allows rolling upgrade with no outage | Head of InfoSec |
| **TR-09** | **Upstream licence change on an AGPL / BSL / TSL / fair-code component** | L4 | **M × M** | Licence register in M30 reviewed annually and at wave gates; **every such component has a named fallback** (Kafka for Redpanda, Apache-only features for TimescaleDB); automated licence scan on dependency addition | Solution Architect |
| **TR-10** | **Third-party L3 payment module unmaintained or defective in duplicate-callback handling** | L3 | **M × H** | Pre-adoption assessment L3-01…L3-06; **L5 direct-gateway wrapper as the registered fallback at 3–5 PW per gateway, carried as contingency** | Solution Architect |
| **TR-11** | **Wave 1 infrastructure load underestimated because module count is low** | All | **M × H** | §20.3 — 15 infrastructure components plus the full pipeline in Wave 1; resource Wave 1 on infrastructure content, not module count | Programme Manager |
| **TR-12** | **Event outbox not applied uniformly, producing silent data divergence between modules** | L5 | **M × H** | AS-08 event-coverage test in CI blocks merge; DoD-05 blocks module acceptance | Solution Architect |
| **TR-13** | **Role register built on 38 roles, requiring retrofit to 46 with R60 eliminated** | L4, L5 | **M × H** | W0-03 register completion is blocking; **Keycloak and Odoo groups built on 46 from the start** | CTO |
| **TR-14** | **Analytical load degrades OLTP before ClickHouse arrives in Wave 8** | L4 | **M × M** | Read replicas from Wave 3; analytical queries never hit the primary; ClickHouse trigger reviewed at each gate and pullable forward | Solution Architect |
| **TR-15** | **L6 cost scales with volume beyond the $36K envelope (RMM in particular)** | L6 | **M × M** | L6-04 — model every per-unit metric at 5× before signing; Wave 5 RMM pilot before commitment; annual OSS alternative review | CFO |
| **TR-16** | **Personal data leaks into logs, traces or non-production environments** | All | **M × H** | OPS-04 log scrubbing CI-checked; NFR-086c masking inside the clone job; automated data scan of every non-production environment | Head of InfoSec |
| **TR-17** | **ML model failure blocks a business path** | L5 | **L × H** | ML-01 — every model has a deterministic fallback; no business path depends on model availability; fallbacks exercised in the DR drill | CTO |
| **TR-18** | **Talent availability for Flutter, Odoo 19 and the split-residency design in Bangladesh** | All | **M × M** | Odoo talent is available locally; Flutter and platform-engineering skills are scarcer — named team members with CVs required at bid (RFP §15.4); knowledge transfer as a definition-of-done item | Programme Manager |

---

## 24. TECHNOLOGY DECISION LOG

### 24.1 Decisions Taken

| # | Decision | Alternative rejected | Reason | Status |
|---|---|---|---|---|
| **TD-01** | **Odoo 19 CE as the ERP core** | Odoo Enterprise; ERPNext; custom build | $0 licence against $45–90K/3yr; 52% of requirements at L1+L2; local talent availability | Settled (v1.0) |
| **TD-02** | PostgreSQL 16 shared with the portal platform | Separate databases per system | One technology, one operational skill set, simpler integration | Settled (v1.0) |
| **TD-03** | **Flutter for all field applications** | React Native; native iOS/Android | One codebase across four apps; one offline engine; strong offline story | Settled (v1.0) |
| **TD-04** | Next.js for external web portals | Odoo web for everything | The portal platform exists and **cannot be replaced (CON-03)** | Constraint |
| **TD-05** | **VROOM + OSRM for routing** | Google Routes; Timefold | $0; self-hosted; **embeds skill, certification, van-stock and working-time constraints a commercial API cannot** | Settled |
| **TD-06** | **Self-hosted LLM (Ollama) for conversational AI** | Rasa 3.6; hosted LLM API | Rasa OSS in maintenance mode; **hosted APIs send customer data offshore, breaching PDPA transfer restrictions** | Settled |
| **TD-07** | Keycloak for identity | Odoo native auth; Auth0 | **Per-client corporate federation (INT-046)**; standards-based; $0 | Settled |
| **TD-08** | Kong for the API gateway | Nginx alone; a cloud gateway | 12 portals with 12 scopes plus external partner consumption | Settled |
| **TD-09** | ClickHouse for the warehouse | PostgreSQL analytics; managed warehouse | Analytical volume from W8 exceeds economic replica capacity | Settled |
| **TD-10** | Redis Streams → Redpanda for the event bus | Redis Streams alone; RabbitMQ | Redis sufficient to W5; durability and replay needs grow beyond it | Settled |
| **TD-11** | **Build the marketplace rather than buy** | Marketplace SaaS | **Commission and settlement must live in the ledger** | Settled |
| **TD-12** | Build the MSP platform on Odoo + OSS monitoring | Commercial PSA/RMM suite | Licence scaling at 400 technicians; integration burden; conditional L6 for the agent only | Settled |
| **TD-13** | TimescaleDB for time series | Plain PostgreSQL; InfluxDB | Same engine, same operational skills, proven compression | Settled |
| **TD-14** | Metabase for BI | Superset; commercial BI | Maturity, embedding, row-level security, $0 | Settled |
| **TD-15** | Monorepo | Polyrepo | Cross-cutting changes across 248 CD items and 10 applications are routine | Settled |
| **TD-16** | **Transactional outbox for every write path** | Post-commit publishing; direct calls | **The only pattern that makes "exactly one event per state change" true rather than usually true** | **New in v2.0** |
| **TD-17** | OCA `dms` → Mayan EDMS at Wave 5 | Mayan from Wave 1; commercial ECM | OCA sufficient to W4; Mayan for volume, OCR and retention from W5 | Settled |
| **TD-18** | **Split-residency data architecture** | Single-region hosting | **PDPA 2026 NFR-099 restricts transfer of Sensitive Personally Identifiable Data** | **New in v2.0 — supersedes the v1.0 single-region position** |
| **TD-19** | **Two-tier e-signature — L5 operational, L6 qualified** | L6 for everything; L5 for everything | Operational signatures need no accreditation; contracts do. Using L6 for both multiplies envelope cost; using L5 for both produces unenforceable contracts | **New in v2.0** |
| **TD-20** | **Bounded L6 with individual CFO approval** | Absolute zero-licence-cost position (v1.0) | Four capabilities have no viable OSS equivalent; a governed L6 is more honest than forcing an unsuitable substitute or allowing ungoverned SaaS | **New in v2.0** |
| **TD-21** | **PostgreSQL FTS before a search cluster** | OpenSearch from Wave 1 | Meets NFR-035 at expected volume; a search cluster adds a synchronisation and consistency problem for no measured benefit. **Escalation planned, not pre-committed** | **New in v2.0** |
| **TD-22** | **Deploy Novu and the notification dispatcher in Wave 1, ahead of M27 in Wave 4** | Build notification with M27 in W4 | Every module from W1 must notify customers; deferring the platform recreates the fragmentation the programme exists to remove | **New in v2.0 — resolves Q-05** |
| **TD-23** | **Build the M22 eligibility interface into M02 as a stub in Wave 2** | Connect in Wave 5 only | Retrofitting a blocking certification check into a live assignment path is materially riskier than building the seam early | **New in v2.0** |
| **TD-24** | **One shared offline engine across APP-01, APP-02 and APP-03** | Per-application offline implementation | Three implementations produce three sets of conflict-resolution bugs | **New in v2.0** |
| **TD-25** | **n8n for brand-claim transformation, not code** | Custom transformation per brand | 17+ brand templates change on the brand's schedule; configuration beats a release cycle | **New in v2.0** |
| **TD-26** | **Complete the CD register to 248 items across all 67 modules** | Retain the 138-item, 30-module register | The register covered 45% of modules; effort was already measured across all 67. Completing it aligns the deliverable list to the effort figure | **New in v2.0** |
| **TD-27** | **Odoo major-version upgrade slot between Wave 5 and Wave 6** | Upgrade after Wave 9; track annual releases | 36 months on an annually-versioned platform requires a planned in-flight upgrade; one scheduled slot beats three or a late scramble | **New in v2.0 — requires ratification (D-15)** |

### 24.2 Decisions Required

| ID | Decision | Owner | Needed by | Consequence of delay |
|---|---|---|---|---|
| **D-13** | **Split-residency legal opinion (DEP-31)** | CFO / Legal / DPO | **Before Wave 1 architecture is fixed** | The data model cannot be fixed; every module built before it carries reclassification risk |
| **D-14** | **Fund the restated 1,513 PW, phase it, or cut scope** | Steering Committee | Before contract award | Scope and sequencing cannot be baselined |
| **D-15** | **Odoo version baseline and upgrade slot (§4.4)** | CTO / Steering | Wave 0 | Programme reaches steady state near end-of-support with an unplanned upgrade |
| **D-16** | **Next.js 15 → 16 upgrade timing (§11.1)** | CTO | Wave 0 | Six portals built on a version leaving the supported line, then migrated together |
| **D-17** | **P07 mobile surface — PWA now, Flutter later, or React Native (§11.9)** | CTO | Wave 6 | Risk of a second mobile framework entering the estate by default |
| **D-18** | **RMM: open source or commercial agent (TC-073)** | CTO / CFO | Wave 5, after the pilot | MSP patch orchestration unresolved; L6 exposure unbounded |
| **Q-01** | **M32 conversational AI launches before its knowledge base (M61, two waves later)** | Steering | Wave 3 | Assistant launches able to answer transactional questions only |
| **Q-05** | **M27 notification platform timing** — this stack's position is Wave 1 (TD-22) | Steering | Wave 0 | Per-module send paths proliferate in Waves 1–3 |
| **Q-05b** | **M59 mobile safety reporting moved to Wave 3** — this stack's position is yes (CD-218 in W3) | Steering | Wave 2 | Field safety reporting stays on paper three waves longer than necessary |

---
---

# PART E — DISCLOSURE & APPENDICES

---

## 25. DISCLOSED OPEN ITEMS, DEFECTS AND VERSION-CURRENCY FINDINGS

This section exists because a technology specification that presents only what is settled is
misleading. Everything below is either an inherited defect in the source specification set, a
version-currency finding raised by this document, or a change this document proposes to the governing
documents. **None of it is hidden in an appendix; all of it affects build decisions.**

### 25.1 Inherited Defects That Affect the Build

These originate in the specification set, not in this document. They are reproduced here because each
one changes what must be built in Wave 1.

| # | Defect | Source | Build consequence | Resolution |
|---|---|---|---|---|
| **25.1.1** | **Two module specifications do not exist** — M66 Internal IT Service Management and M67 Project, Program & Portfolio Management. 48 requirements are estimated | `02-02` §3 (H2-02) | Technology assigned against registered scope only; **CD-232 is a joint reserved allocation**, not a specification | Write both specifications before their waves (W6, W7) |
| **25.1.2** | **Roles R39–R46 are used but unregistered; R54 and R57 are referenced with no definition; R60 is a duplicate identity for R32** | `05-04` (H2-07) | **This is a live permission defect.** An access rule written against R32 does not apply to a user granted R60. **Keycloak realms and Odoo groups must be built on 46 roles with R60 eliminated** | Complete the register to R46; eliminate R60; resolve R54/R57 — **Wave 0, blocking** |
| **25.1.3** | **SOD-13 through SOD-30 are used but unregistered** — 30 controls are named, 12 registered | `05-04` (H2-06) | **CD-132 must implement all 30.** Building 12 leaves 18 segregation-of-duties conflicts unenforced | Complete the register — Wave 0 |
| **25.1.4** | **Colliding `KPI-` identifiers across module specifications** | `06-02` (H2-04) | **CD-110 cannot register two KPIs under one identifier.** Instrumentation blocked until resolved | De-duplicate the KPI register — Wave 0, before instrumentation |
| **25.1.5** | **NFR-090, NFR-091 and NFR-092 each carry two different requirements**; NFR-088 and NFR-089 are repeated | `05-06` §6.3 vs §7, §6.4 | 101 identifiers carry 104 requirements. This document covers all 104 using the `-M` suffix (§13.1) | Resolve the collision in the owning register — Wave 0 |
| **25.1.6** | **28 requirement IDs in M01, M02 and M31 are allocated but unused** | `02-02` §3 (H2-03) | Category A per-module figures overstate by 27. Effort estimation against ID ranges rather than counts will over-size Category A | Recount per module; align the register |
| **25.1.7** | **The CD register covers 30 of 67 modules** | `02-05` §5.2 | **Addressed in this document** — §8.2 completes it to 248 items. The RFP's "~138 CD items" figure is superseded | Ratify the restated register (§25.3) |
| **25.1.8** | **Per-module requirement figures do not sum to measured category totals** in C, E, F, G, I | `02-02` §3.1, RFP §6.1a | Sizing from per-module rows under-quotes C (+39%), F (+73%), G (+29%), I (+44%) | **Size from category totals and Annex 1, never from per-module rows** |
| **25.1.9** | **Wave capacity has not been validated against the restated effort** | `02-02` §4.2 (M-09) | W3, W4 and W6 are tight against available person-weeks with almost no contingency — and §20.3 shows W1's infrastructure load is understated by module count | Capacity re-plan before the roadmap is baselined |
| **25.1.10** | **The wave view omits M07's W1 portion and M25's W8 portion** | `02-02` §4.2 (BA-04) | Wave module counts in §20.2 follow the register; the underlying inconsistency is unresolved | Reconcile the register's wave view |

### 25.2 Version-Currency Findings Raised by This Document

**Every component version in the reference stack was re-verified against upstream release and
end-of-life data on 13 August 2026.** Five findings arise. None invalidates the architecture; all
five require a decision.

| # | Component | Specified | Current position (13 Aug 2026) | Finding | Recommendation |
|---|---|---|---|---|---|
| **25.2.1** | **Odoo** | 19.0 | 19.0 released **18 September 2025**, LTS, supported to approximately **September 2028**. **Odoo 20 expected September–October 2026** (Odoo Experience, 24–26 September 2026) | A **36-month programme will reach steady state within about a year of 19.0 leaving support** | **Baseline on 19.0; schedule one major-version upgrade slot between W5 and W6** (§4.4 Option A). **D-15** |
| **25.2.2** | **Next.js** | 15 | **16.2.x is current and is the LTS line**, with React 19.2 and a stable React Compiler | **Six customer-facing applications would be built on a version leaving the supported line during the programme.** CON-03 constrains the platform, not the version | **Treat 15 → 16 as a Wave 1 platform activity, before six applications are built on it.** Confirm Payload CMS 3 compatibility in Wave 0. **D-16** |
| **25.2.3** | **PostgreSQL** | 16 | 16 is supported to **November 2029**; 17 to November 2029; **18 to November 2030** | 16 remains a **valid and safe choice** — it is supported past the programme's steady state. But the margin at steady state is roughly one year | **Retain 16 for Wave 1** (it is Odoo 19's tested pairing). **Review the move to 17 or 18 at the same gate as the Odoo upgrade slot**, so both major upgrades happen once, together |
| **25.2.4** | **Keycloak** | 26.x | **26.7.x current. Keycloak has no LTS line — only the newest version receives active development and security fixes** | Pinning Keycloak for the life of a wave leaves authentication on an unpatched release | **Operational standard, not a version change: Keycloak is kept current continuously** (§17.4, TR-08). HA cluster makes rolling upgrade non-disruptive |
| **25.2.5** | **Flutter / React Native** | Flutter for four apps; P07 mobile framework unresolved | **Flutter 3.44 current** (Dart 3.12, Impeller default on Android). React Native's legacy architecture has been **removed** as of 0.83 — the New Architecture is mandatory | The estate must not acquire a second mobile framework by default through P07 | **Confirm Flutter as the single mobile framework**; deliver P07's mobile surface as a PWA in W7 (§11.9). **D-17** |

**Two components carry licence-currency watch rather than version currency:**

| Component | Watch | Fallback |
|---|---|---|
| **TimescaleDB** | Apache-2.0 core with advanced features under the source-available **TSL** | **Apache-2.0 features only** — CI-checked. A TSL dependency would convert a $0 component into a licensed one mid-programme |
| **Redpanda** | **BSL**, converting to Apache-2.0 four years after each merge | **Kafka (Apache-2.0)** is the registered fallback |

### 25.3 Changes This Document Proposes to the Governing Documents

This specification cannot change the RFP, BRD or URD. Each item below is a change request with a named
owner.

| # | Change | Affects | Rationale | Owner |
|---|---|---|---|---|
| **25.3.1** | **Restate "~138 CD items" to 248** | RFP §5.3, §16.2 | The 138-item register covers 30 of 67 modules. **This does not increase cost** — 1,513 PW already measures all 67 — it aligns the deliverable list to the effort figure | CTO |
| **25.3.2** | **Add a Wave 0 to the delivery plan** | RFP §12, BRD §21 | Six pre-build activities (§20.1), three of them blocking, cannot be done inside Wave 1 without putting Wave 1 at risk | Programme Manager |
| **25.3.3** | **Add an Odoo major-version upgrade slot between W5 and W6** | RFP §12.2, §12.3 | A 36-month programme on an annually-versioned platform requires a planned in-flight upgrade | CTO |
| **25.3.4** | **Deploy the notification platform (Novu + CD-234) in Wave 1, ahead of M27 in Wave 4** | RFP §12.3, `06-01`, Q-05 | Every module from W1 must notify customers; deferring the platform recreates the fragmentation the programme exists to remove | Steering |
| **25.3.5** | **Move M59's mobile safety reporting (CD-218) from W6 to W3** | RFP §12.3, `06-01`, Q-05b | FR-HSE-009 and FR-HSE-011 depend only on P02 and M21; they ship with the technician app at low incremental cost, and field safety reporting otherwise stays on paper three waves longer | Steering |
| **25.3.6** | **Add the Bangladesh-resident store to the production sizing table** | RFP §5.9 | The sizing table predates the split-residency decision and carries no line for it | CTO |
| **25.3.7** | **Add the Next.js 15 → 16 upgrade as a Wave 1 platform activity** | RFP §5.4, §12.3 | §25.2.2 — six portals otherwise built on a version leaving support, then migrated together | CTO |
| **25.3.8** | **Build a keyboard and single-pointer alternative to every drag interaction on the P03 dispatch board** | RFP §9.5, URD §21.4 | Required under WCAG 2.1 AA for accessibility persona A-06 and explicitly under 2.2 SC 2.5.7. **Built regardless of which standard is adopted** | Solution Architect |
| **25.3.9** | **Add ClamAV (TC-038) and Vault/OpenBao (TC-039) to the L4 reference stack** | RFP §5.4.3 | **NFR-063 requires malware scanning on every upload and NFR-062 requires vault-managed secrets, but neither has a named component in the RFP's 24-system list.** Both are Wave 1, both are $0 (§7.1 note b) | CTO |

### 25.4 Assumptions This Document Makes

| # | Assumption | If wrong |
|---|---|---|
| A-01 | A Bangladesh-resident hosting option with adequate availability, encryption and operational maturity is procurable | Split residency requires an in-country data-centre arrangement with materially higher cost and longer lead time |
| A-02 | The split-residency legal opinion permits a resident-key join rather than requiring full record residency | If full record residency is required, the regional/resident split becomes a much larger architectural change |
| A-03 | OCA `field-service` v19 migration gaps are closable within 12–20 PW | The gap reclassifies to L5 with effort added to Wave 2 |
| A-04 | Open-weight LLMs deliver adequate Bengali quality for the assistant's intent scope | The assistant's scope narrows to templated and transactional responses; ML-01's fallback becomes the primary path |
| A-05 | Payload CMS 3 is compatible with Next.js 16 | The 15 → 16 upgrade is deferred and TR-06 materialises |
| A-06 | Bangladesh SMS, WhatsApp and payment providers maintain their current API contracts | Connector rework; the L5 wrapper fallback (§6.2) applies |
| A-07 | NBR does not mandate a full electronic invoice-clearance regime inside the programme window | CD-083 is designed to accommodate one without redesign, but integration effort would be added at the Wave 4 gate |
| A-08 | Odoo 20 and 21 do not break the OCA extension model in a way that invalidates AS-05 | The upgrade slot cost rises materially; TR-05 escalates |

### 25.5 What Would Make This Stack Fail

Stated plainly, because the failure modes are known and each has a named control.

| # | Failure mode | Control |
|---|---|---|
| 1 | **OCA modules forked instead of extended.** Every upgrade becomes a manual merge across 140+ modules for 34 months | AS-05 in CI; fork register; wave-gate review (TR-04) |
| 2 | **The offline engine loses or double-applies field data.** Technicians stop trusting the app, revert to paper, and the field data model is permanently incomplete | Append-only journal, idempotency ledger, dedicated test harness, field pilot (TR-01) |
| 3 | **Residency enforcement built as convention rather than mechanism.** A single bulk loader or a log line puts NID data in the regional store | ORM guard, single residency service, negative tests, log scrubbing, migration path through CD-233 (TR-02, TR-16) |
| 4 | **Wave 1 resourced by module count.** The 15-component infrastructure wave slips, and every subsequent wave inherits the slip | §20.3; resource Wave 1 on infrastructure content (TR-11) |
| 5 | **The permission model built on 38 roles.** Retrofitting 8 roles and eliminating R60 across live data with record rules and field permissions already in place | W0-03 blocking gate (TR-13) |
| 6 | **The event outbox applied unevenly.** Some modules emit reliably, others best-effort; data divergence accumulates silently and is discovered in reconciliation months later | AS-08 CI coverage test; DoD-05 acceptance gate (TR-12) |
| 7 | **Bengali treated as a font setting.** Invoices and payslips render wrongly to readers while passing automated tests — a compliance defect on a Mushak 6.3 | OpenType shaping in CD-238; print verification per printer at every wave gate (TR-07) |
| 8 | **Scope funded on the 138-item CD register and the per-module requirement columns.** The build is quoted at roughly half its deliverable breadth in Categories C, F, G and I | §8.2 restated register; §10 category-total rule; price against Annex 1 |

---

## 26. APPENDICES

### Appendix A — Complete Technology Component Register

Every separately deployed or separately licensed component, with its layer, licence, version, owning
module and wave.

| TC | Component | Layer | Version | Licence | Serves | Wave |
|---|---|:--:|---|---|---|:--:|
| TC-001 | **Odoo Community Edition** | L1 | 19.0 (19.x) | LGPL-3 | All 67 modules | W1 |
| TC-002 | Python runtime | L1 | 3.12+ | PSF | Odoo, domain services | W1 |
| TC-003 | OWL 2 | L1 | bundled | LGPL-3 | P03 | W1 |
| TC-004 | **Next.js** | L5 | 15 → **16** *(§25.2.2)* | MIT | P01, P04, P07, P08, P10, P12 | W2 |
| TC-005 | React | L5 | 19.2 | MIT | Next.js portals | W2 |
| TC-006 | **Payload CMS** | L5 | 3 | MIT | P01 content (CON-03) | W2 |
| TC-007 | **Flutter** | L5 | 3.44 (current stable) | BSD-3 | APP-01…04 | W2 |
| TC-008 | Dart | L5 | 3.12 | BSD-3 | Flutter apps | W2 |
| TC-009 | Node.js | L5 | active LTS | MIT | Next.js, CD-234 | W1 |
| TC-010 | **PostgreSQL** | L4 | 16 | PostgreSQL Licence | Primary datastore, resident store | W1 |
| TC-011 | PgBouncer | L4 | current | ISC | Connection pooling | W1 |
| TC-012 | **Redis** | L4 | 7.x | BSD-3 | Cache, sessions, queues, Streams | W1 |
| TC-013 | Nginx | L4 | 1.27+ | BSD-2 | Reverse proxy, TLS | W1 |
| TC-014 | Docker / K3s | L4 | current | Apache-2.0 | Containerisation, orchestration | W1 |
| TC-015 | **Keycloak** | L4 | 26.x *(kept current — §25.2.4)* | Apache-2.0 | M29, all portals | W1 |
| TC-016 | **Kong Gateway** | L4 | 3.x | Apache-2.0 | M28, all API traffic | W1 |
| TC-017 | **n8n** | L4 | 1.x | **Sustainable Use** | M28, M63 | W1 |
| TC-018 | **Novu** | L4 | 2.x | MIT | M27 | W1 |
| TC-019 | MinIO | L4 | current | **AGPL-3** | Object storage | W1 |
| TC-020 | **Traccar** | L4 | 6.x | Apache-2.0 | M02, M46 | W2 |
| TC-021 | OSRM | L4 | 5.x | BSD-2 | M02, M03 | W2 |
| TC-022 | VROOM | L4 | 1.14+ | BSD-2 | M02, M03 | W2 |
| TC-023 | **TimescaleDB** | L4 | 2.x (**Apache-2.0 features only**) | Apache-2.0 / TSL | M02, M05, M17, M48 | W2 |
| TC-024 | Grafana | L4 | 11.x | **AGPL-3** | M25, M28, P06 | W2 |
| TC-025 | OpenTelemetry | L4 | current | Apache-2.0 | Observability | W3 |
| TC-026 | Prometheus | L4 | current | Apache-2.0 | Metrics, alerting | W3 |
| TC-027 | Loki | L4 | current | **AGPL-3** | Logs | W3 |
| TC-028 | Tempo | L4 | current | **AGPL-3** | Traces | W3 |
| TC-029 | **Metabase** | L4 | 0.52+ | **AGPL-3** | M25, P06 | W4 |
| TC-030 | **Mayan EDMS** | L4 | 4.10 | Apache-2.0 | M24 | W5 |
| TC-031 | MeshCentral / RustDesk | L4 | current | Apache-2.0 / **AGPL-3** | M05 | W5 |
| TC-032 | Wazuh | L4 | current | **GPL-2** | M05, M29 | W5 |
| TC-033 | osquery | L4 | current | Apache-2.0 | M05 | W5 |
| TC-034 | **Redpanda / Kafka** | L4 | current | **BSL** / Apache-2.0 | M28 | W6 |
| TC-035 | MLflow | L4 | 2.x | Apache-2.0 | M26 | W6 |
| TC-036 | **Ollama** | L4 | 0.5+ | MIT | M26, M32 | W6 |
| TC-037 | **ClickHouse** | L4 | 24.x | Apache-2.0 | M25, M62 | W8 |
| TC-038 | ClamAV | L4 | current | GPL-2 | Upload scanning (NFR-063) | W1 |
| TC-039 | Vault | L4 | current | BUSL / MPL *(fallback: OpenBao, MPL-2.0)* | Secrets (NFR-062) | W1 |
| TC-040 | dbt | L5 | current | Apache-2.0 | CD-243 warehouse ETL | W4 |
| TC-060 | SSLCOMMERZ connector | L3 | current | Various | INT-003 | W3 |
| TC-061 | bKash connector | L3 | current | Various | INT-001 | W3 |
| TC-062 | Nagad connector | L3 | current | Various | INT-002 | W3 |
| TC-063 | BD SMS gateway connector | L3 | current | Various | INT-010, INT-011 | W1 |
| TC-064 | WhatsApp Business connector | L3 | current | Various | INT-012 | W1 |
| TC-065 | Barcode / QR extensions | L3 | current | Various | M15, M02, M41 | W2 |
| TC-070 | **Cloud telephony / CPaaS** | **L6** | vendor | Subscription | M27, INT-015 | W4 |
| TC-071 | **Qualified e-signature** | **L6** | vendor | Subscription | M24, M08, M12 | W4 |
| TC-072 | **Identity verification / KYC** | **L6** | vendor | Per check | M12, INT-034, INT-035 | W7 |
| TC-073 | **Endpoint RMM agent** *(conditional)* | **L6** | vendor | Per endpoint | M05 | W5–W6 |

**Plus 18 OCA repositories (Appendix C), 248 CD items (§8.2) and 10 applications (§8.2).**

> **Note on TC-039.** HashiCorp Vault moved to the Business Source Licence in 2023. **OpenBao**
> (MPL-2.0, Linux Foundation) is the registered open-source fallback and is the preferred option
> where it meets the operational requirement. This is a licence-watch item under TR-09.

### Appendix B — Requirement-Class-to-Layer Coverage Matrix

This is the class-level matrix referenced in §1.2. It states, for every requirement class in the
specification set, which layers deliver it — so that the implementation partner's requirement-level
response in RFP Appendix A has a defined answer to map onto in every case.

| Requirement class | Prefix | Count | L1 | L2 | L3 | L4 | L5 | L6 | Coverage |
|---|---|---:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| Service request & order | `FR-SRM` | 88 | ● | ● | | ● | ● | | ✔ |
| Workshop & depot repair | `FR-WSR` | 58 | ● | ● | | | ● | | ✔ |
| Field service & dispatch | `FR-FSM` | 74 | ● | ● | | ● | ● | | ✔ |
| Logistics | `FR-LOG` | 42 | ● | ● | ● | ● | ● | | ✔ |
| Front desk | `FR-FRD` | 31 | ● | ● | | | ● | | ✔ |
| Remote & managed services | `FR-RMS` | 61 | ● | ● | | ● | ● | ● | ✔ |
| Data services | `FR-DTS` | 34 | ● | ● | | ● | ● | | ✔ |
| Customer & party master | `FR-CPM` | 52 | ● | ● | | ● | ● | | ✔ |
| CRM | `FR-CRM` | 46 | ● | ● | | | ● | | ✔ |
| Loyalty | `FR-LOY` | 44 | ● | | | ● | ● | | ✔ |
| Customer experience | `FR-CXM` | 42 | ● | ● | | ● | ● | | ✔ |
| Contact centre | `FR-CCE` | 58 | ● | ● | ● | ● | ● | ● | ✔ |
| Conversational AI | `FR-CAI` | 38 | | | | ● | ● | | ✔ |
| Marketing | `FR-MKT` | 40 | ● | ● | | ● | ● | | ✔ |
| Catalogue | `FR-CAT` | *(est.)* | ● | ● | | ● | ● | | ✔ |
| Pricing | `FR-PRC` | *(est.)* | ● | | | | ● | | ✔ |
| Quotation & tender | `FR-QTE` | *(est.)* | ● | ● | | | ● | | ✔ |
| Contract lifecycle | `FR-CTR` | *(est.)* | ● | ● | | ● | ● | ● | ✔ |
| Warranty & claims | `FR-WTY` | *(est.)* | ● | ● | | ● | ● | | ✔ |
| Subscription | `FR-SUB` | *(est.)* | ● | ● | | | ● | | ✔ |
| E-commerce | `FR-ECM` | *(est.)* | ● | | | ● | ● | | ✔ |
| Marketplace | `FR-MKP` | *(est.)* | ● | ● | | ● | ● | ● | ✔ |
| Partner & channel | `FR-PCM` | *(est.)* | ● | ● | | | ● | | ✔ |
| Rental | `FR-RNT` | *(est.)* | ● | ● | | | ● | | ✔ |
| Trade-in & refurbishment | `FR-TRF` | *(est.)* | ● | ● | | ● | ● | | ✔ |
| E-waste & ESG | `FR-ESG` | *(est.)* | ● | ● | | ● | ● | | ✔ |
| Inventory | `FR-INV` | *(est.)* | ● | ● | ● | ● | ● | | ✔ |
| Warehouse | `FR-WMS` | *(est.)* | ● | ● | ● | | ● | | ✔ |
| Procurement | `FR-PRO` | *(est.)* | ● | ● | | ● | ● | | ✔ |
| Supplier performance | `FR-SRM2` | *(est.)* | ● | ● | | ● | ● | | ✔ |
| Demand planning | `FR-DPL` | *(est.)* | ● | ● | | ● | ● | | ✔ |
| Import & landed cost | `FR-ITC` | *(est.)* | ● | ● | | | ● | | ✔ |
| Asset registry | `FR-AST` | *(est.)* | ● | ● | | ● | ● | | ✔ |
| Enterprise asset | `FR-EAM` | *(est.)* | ● | ● | | | ● | | ✔ |
| Fleet | `FR-FLT` | *(est.)* | ● | ● | | ● | ● | | ✔ |
| Facility | `FR-FAC` | *(est.)* | ● | ● | | | ● | | ✔ |
| IoT & predictive | `FR-IOT` | *(est.)* | | | | ● | ● | | ✔ |
| Financial accounting | `FR-FIN` | *(est.)* | ● | ● | | | ● | | ✔ |
| Receivables | `FR-ARB` | *(est.)* | ● | ● | | ● | ● | | ✔ |
| Payables & expense | `FR-APE` | *(est.)* | ● | ● | | | ● | | ✔ |
| Treasury | `FR-TRE` | *(est.)* | ● | ● | | | ● | | ✔ |
| Tax (Bangladesh) | `FR-TAX` | *(est.)* | ● | ● | | | ● | | ✔ |
| Revenue & settlement | `FR-REV` | *(est.)* | ● | ● | | | ● | | ✔ |
| Fixed assets | `FR-FXA` | *(est.)* | ● | ● | | | ● | | ✔ |
| Costing & FP&A | `FR-FPA` | *(est.)* | ● | ● | | ● | ● | | ✔ |
| Core HR | `FR-HCM` | 46 | ● | ● | | ● | ● | | ✔ |
| Time & workforce | `FR-WFM` | 52 | ● | ● | | | ● | | ✔ |
| Payroll | `FR-PAY` | 54 | ● | ● | | | ● | | ✔ |
| Performance & incentives | `FR-PIC` | 42 | ● | ● | | ● | ● | | ✔ |
| Learning & certification | `FR-LMS` | 40 | ● | ● | | | ● | | ✔ |
| Talent acquisition | `FR-TAO` | 34 | ● | ● | | | ● | | ✔ |
| Health & safety | `FR-HSE` | 42 | ● | ● | | ● | ● | | ✔ |
| Quality management | `FR-QMS` | *(est.)* | ● | ● | | ● | ● | | ✔ |
| Governance & risk | `FR-GRC` | *(est.)* | | ● | | ● | ● | | ✔ |
| Document & records | `FR-DMS` | *(est.)* | ● | ● | | ● | ● | ● | ✔ |
| Knowledge management | `FR-KMS` | *(est.)* | ● | | | ● | ● | | ✔ |
| Data platform | `FR-DAT` | *(est.)* | | | | ● | ● | | ✔ |
| Business intelligence | `FR-BID` | *(est.)* | ● | ● | | ● | ● | | ✔ |
| AI/ML services | `FR-AIM` | *(est.)* | | | | ● | ● | | ✔ |
| Process automation | `FR-BPA` | *(est.)* | ● | ● | | ● | ● | | ✔ |
| Integration & API | `FR-IPF` | *(est.)* | ● | ● | | ● | ● | | ✔ |
| Identity & security | `FR-SEC` | *(est.)* | ● | ● | | ● | ● | | ✔ |
| Master data | `FR-MDM` | *(est.)* | ● | ● | | | ● | | ✔ |
| Multi-entity & localisation | `FR-GLO` | *(est.)* | ● | ● | | | ● | | ✔ |
| IT service management | `FR-ITS` | *(est.)* | ● | ● | | ● | ● | | ✔ |
| Platform administration | `FR-ADM` | *(est.)* | ● | ● | | ● | ● | | ✔ |
| Project & portfolio | `FR-PPM` | *(est.)* | ● | | | ● | ● | | ✔ |
| **Portal requirements** | `FR-POR` | 140 | ● | ● | | ● | ● | | ✔ |
| **Non-functional** | `NFR` | 101 *(104 reqs)* | ● | ● | | ● | ● | | ✔ **§13** |

**69 requirement classes. 69 with assigned technology. 0 gaps.**

### Appendix C — OCA Repository Index

| Repository | Modules | Serves | v19 status | Wave |
|---|---:|---|---|:--:|
| `OCA/field-service` | 33 | M01, M02, M03, M31 | ~25 of 33 — **medium risk** | W1–W2 |
| `OCA/helpdesk` | 28 | M01, M05, M27, M34 | ~20 of 28 — **medium risk** | W1 |
| `OCA/management-system` | 33 | M23, M45, M59, M60 | ~28 of 33 | W5 |
| `OCA/operating-unit` | 15 | **All 67** | ~12 of 15 | **W1** |
| `OCA/hr` + `OCA/payroll` | 50+ | M21, M22, M55, M56, M57, M58 | ~40 of 50+ | W5 |
| `OCA/account-financial-tools` | 40+ | M19, M49, M50, M52 | Mostly migrated | W3 |
| `OCA/account-financial-reporting` | 20+ | M19, M25, M54 | Mostly migrated | W3 |
| `OCA/reporting-engine` + `OCA/mis-builder` | 20+ | M19, M25, M54 | Mostly migrated | W4 |
| `OCA/stock-logistics-workflow` | 25+ | M15, M41 | Mostly migrated | W2 |
| `OCA/stock-logistics-barcode` | 10 | M15, M02, M41 | Mostly migrated | W2 |
| `OCA/stock-logistics-warehouse` | 20+ | M15, M41 | Mostly migrated | W3 |
| `OCA/purchase-workflow` | 25+ | M16, M42, M36 | Mostly migrated | W3 |
| `OCA/partner-contact` | 30+ | M07, M33, M35, M40 | Mostly migrated | W1 |
| `OCA/contract` | 12 | M08, M39 | Mostly migrated | W4 |
| `OCA/dms` | 5 | M24, M06 | Mostly migrated | W3 |
| `OCA/server-tools` | 30+ | M29, M30, M63, M64 | Mostly migrated | W1 |
| `OCA/web` | 40+ | UI, Keycloak auth bridge | Mostly migrated | W1 |
| `OCA/l10n-bangladesh` | 2 | M19, M51 | Mostly migrated | W3 |
| **18 repositories** | **140+** | | | |

**Standing contractual obligation:** where the implementation partner migrates an OCA module to v19,
**the work is contributed back upstream** (RFP §5.4.2).

### Appendix D — Licence Compliance Register

| Licence | Components | Obligation | Compliance mechanism | Watch |
|---|---|---|---|:--:|
| **LGPL-3** | Odoo 19 CE, most OCA modules | Modifications to the library must be shared | **Extensions are separate modules, never core modifications** (AS-05, L1-01) | |
| **AGPL-3** | Metabase, Grafana, MinIO, Loki, Tempo, RustDesk | Source disclosure if **modified and served over a network** | **Deployed unmodified**; CI flags any change to a vendored AGPL component | ● |
| **Apache-2.0** | Keycloak, Kong, Traccar, TimescaleDB (core), Mayan, MLflow, ClickHouse, osquery, MeshCentral, Prometheus, OpenTelemetry, Docker/K3s, dbt | Attribution, patent grant | Attribution register in M30 | |
| **MIT** | Novu, Ollama, Next.js, Payload CMS, React, Node.js | Attribution | Attribution register | |
| **BSD-2 / BSD-3** | Nginx, OSRM, VROOM, Redis, Flutter, Dart | Attribution | Attribution register | |
| **PostgreSQL Licence** | PostgreSQL | Attribution | Attribution register | |
| **ISC** | PgBouncer | Attribution | Attribution register | |
| **GPL-2** | Wazuh, ClamAV | Copyleft on distribution | **Deployed, not distributed** | ● |
| **Sustainable Use** (fair-code) | **n8n** | **Internal business purposes only**; not resaleable as a competing service | Internal orchestration only; **never exposed as a saleable automation service** to sellers, clients or partners | ● |
| **BSL** | **Redpanda** | Source-available; converts to Apache-2.0 four years after each merge | Reviewed at deployment; **Kafka (Apache-2.0) is the registered fallback** | ● |
| **TSL** | **TimescaleDB advanced features** | Some features require a commercial licence | **Apache-2.0 features only — CI-checked** | ● |
| **BUSL / MPL** | Vault | Source-available | **OpenBao (MPL-2.0) is the registered fallback** | ● |
| **Proprietary** | 248 CD items, 10 applications | — | **1000FiX-owned**; delivered continuously to a Company-controlled repository | |
| **Subscription** | 4 L6 components | Contractual | CFO approval; annual OSS review; exit position stated | ● |

**● = licence-watch item.** Reviewed annually and at every wave gate for components entering that
wave. Every watched component has a named fallback (TR-09).

### Appendix E — Interface and Protocol Register

| Interface | Protocol | Between | Auth | Notes |
|---|---|---|---|---|
| Portal → Gateway | HTTPS / TLS 1.3 | Portals → Kong | OAuth 2.0 (+ PKCE for mobile) | Per-portal credential and rate limit |
| Gateway → Odoo | HTTP (private) | Kong → Odoo | Service credential | mTLS within Z2 |
| Gateway → Services | HTTP (private) | Kong → domain services | Service credential | mTLS within Z2 |
| Odoo → Database | PostgreSQL wire | Odoo → PgBouncer → PostgreSQL | Certificate + password | Private network only |
| **Any → Resident store** | HTTPS | **CD-233 residency service only** | Service credential + step-up | **The only path into Z4** |
| Outbox → Event bus | Redis protocol / Kafka protocol | Relay → Redis Streams / Redpanda | Service credential | At-least-once with idempotent consumption |
| Odoo → Traccar | REST + WebSocket | Odoo ↔ Traccar | API token | Position stream |
| Odoo → VROOM/OSRM | HTTP | Route orchestrator → VROOM/OSRM | Network-restricted | Private, no auth needed inside Z2 |
| Odoo → Novu | HTTPS | Notification dispatcher → Novu | API key from Vault | |
| Odoo → n8n | Webhook + REST | Both directions | Signed webhook + API key | |
| ERP ↔ Portal platform | HTTPS REST + webhooks | Odoo ↔ Next.js/Payload | OAuth 2.0 client credentials | **CON-03 contract, §12.2.5** |
| Mobile → Gateway | HTTPS | Flutter apps → Kong | OAuth 2.0 + PKCE | Certificate pinning |
| Mobile local store | SQLCipher | On device | Device-derived key | Wiped on remote revocation |
| External inbound | HTTPS | Third parties → `/hooks/v1/*` | **Signature verification** | |
| External outbound | HTTPS | Z6 egress proxy → named allow-list | Credentials injected from Vault | **Every call logged (IP-10)** |
| Observability | OTLP | All → OTel Collector | Service credential | |
| Biometric devices | SDK / file | Devices → CD-208 → residency service | Device credential | **Templates are residency-classified** |
| Printers | Network / USB | P03, P04 counters → printers | Network-restricted | **Bengali rendering verified per printer** |

### Appendix F — Glossary

| Term | Meaning |
|---|---|
| **AGPL-3** | GNU Affero General Public Licence v3 — requires source disclosure if modified software is served over a network |
| **APP-nn** | Application identifier in this document — 4 Flutter, 6 Next.js |
| **AS-nn** | Architecture standard — testable, CI-verified, contractually binding |
| **BFF** | Backend-for-frontend — a portal-specific API composition layer |
| **BSL** | Business Source Licence — source-available, converting to an open licence after a stated period |
| **CD-nnn** | Custom development item — a custom Odoo module, extension or service |
| **CON-03** | Constraint: the Next.js + Payload CMS portal platform cannot be replaced |
| **DoD-nn** | Definition-of-done criterion; a module is not accepted until all are true |
| **Fair-code** | Source-available licensing permitting internal use but restricting resale (n8n) |
| **JSON-2** | Odoo 19's RESTful, token-authenticated API |
| **Kernel** | The six concepts modelled once and consumed by all modules — party, product, location, entity, document, event |
| **L1…L6** | Delivery layers, cheapest viable first |
| **LGPL-3** | GNU Lesser General Public Licence v3 — Odoo CE's licence; extensions may be separately licensed |
| **Mushak 6.3** | Bangladesh NBR-prescribed VAT tax invoice |
| **Mushak 9.1** | Bangladesh NBR monthly VAT return, filed by the 15th via vat.gov.bd |
| **OCA** | Odoo Community Association — nonprofit maintaining peer-reviewed Odoo modules |
| **Outbox** | Transactional outbox — writing the event into the same DB transaction as the state change |
| **OWL 2** | Odoo Web Library v2, the TypeScript component framework behind the Odoo web client |
| **PDPA 2026** | Bangladesh Personal Data Protection Act 2026 (Law 63 of 2026) |
| **PW** | Person-week |
| **RG-nn** | Register governance rule |
| **Residency-classified** | A field that must be stored in the Bangladesh-resident store under NFR-086 |
| **S0…S3** | Data sensitivity classification; S3 is field-level encrypted and access-logged |
| **SoD** | Segregation of duties |
| **Split residency** | The architecture placing sensitive personal data in Bangladesh and the remainder regionally, joined by key |
| **T0…T5** | Data isolation tiers, T5 being restricted with step-up authentication |
| **TC-nnn** | Technology component identifier, registered in Appendix A |
| **TD-nn** | Technology decision, registered in §24 |
| **TR-nn** | Technology risk, registered in §23 |
| **TSA-nn** | Technology Stack audit finding, registered in Appendix G |
| **TSL** | Timescale Licence — source-available licence covering TimescaleDB's advanced features |
| **Wave / Wn** | One of the nine delivery waves across 36 months |
| **Z0…Z6** | Network trust zones, §3.4 |

---
### Appendix G — Technology Stack v2.0 Audit Record

**Audit date:** 13 August 2026 · **Method:** direct enumeration under rule **RG-06** — *count, do not
consult*. Every figure was re-derived from the document text and from the source registers
programmatically. A figure asserted earlier in this document was **not** treated as evidence for
itself.

#### G.1 Scope of the Audit

| # | Question tested | Method |
|---|---|---|
| 1 | Does every one of the 67 modules have a technology assignment? | Enumerate module rows in §10.2–§10.12 and diff against `02-02` |
| 2 | Does every one of the 12 portals have a technology assignment? | Enumerate §11 subsections |
| 3 | Does every NFR from NFR-001 to NFR-101 appear in §13 with a realising technology? | Regex-enumerate NFR identifiers in §13 and diff against the full range |
| 4 | Does every integration from INT-001 to INT-047 have a named client technology? | Regex-enumerate in §12.2.4 and diff against `05-03` |
| 5 | Are all 46 roles present? | Regex-enumerate `R01`–`R46` |
| 6 | Is the restated CD register contiguous and gap-free from CD-001 to CD-248? | Expand every declared range and single, diff against 1–248 |
| 7 | Are the applications APP-01…APP-10 all registered? | Enumerate |
| 8 | Do the layer-distribution claims in §10.14 match the §10 tables? | Parse every module row, count non-empty layer cells |
| 9 | Are headline figures internally consistent and consistent with RFP/BRD/URD? | Cross-count occurrences of each headline figure |
| 10 | Is the document structurally complete — no missing or duplicated sections, no draft artefacts? | Enumerate headings; scan for chunk markers |

#### G.2 What the Audit Verified as Correct

| Check | Result |
|---|---|
| Modules with a technology assignment | **67 of 67** — zero `∅` |
| Portals with a technology assignment | **12 of 12** |
| NFRs realised in §13 | **101 of 101 identifiers**, covering all **104 distinct requirements** including the three collided identifiers |
| Integrations with a named client technology and, for P0, a fallback | **47 of 47** |
| Roles present | **46 of 46** (R01–R46) |
| CD register continuity CD-001…CD-248 | **Zero gaps, zero overlaps** |
| Applications registered | **10 of 10** (APP-01…APP-10) |
| Requirement classes in Appendix B with an assigned layer | **69 of 69** |
| Sections 1–26 | **All present, none duplicated** |
| Appendices | **A–G present, correctly lettered** |
| Draft artefacts | **Zero chunk markers remaining** |
| Headline figure consistency with RFP v2.0 / BRD v2.0 / URD v2.0 | **2,930 requirements · 1,513 PW · 67 modules · 11 categories · 12 portals · 225 entities · 47 integrations · 101 NFRs · 46 roles · 60 automations · 95 KPIs · 15 journeys · 9 waves / 36 months · $690K–1,150K TCO — all consistent** |

#### G.3 Findings Raised Against This Document, and Their Resolution

| ID | Severity | Finding | Resolution |
|---|:--:|---|---|
| **TSA-01** | **Medium** | **§10.14's layer-distribution figures were projected, not counted.** The draft stated L1 60/67, L2 52/67, L4 41/67 and L6 4/67. Direct enumeration of the 67 module rows returns **L1 62, L2 58, L4 42, L5 67, L6 5**. The L6 figure had omitted **M08**, which consumes the qualified e-signature component for AMC and MSP contracts | **Fixed.** All six figures recounted and replaced; the modules absent from each layer are now named explicitly; the L3 row is annotated to explain that L3 has no column in §10 because it contributes at integration level |
| **TSA-02** | **Medium** | **CD identifier-range collision introduced by this document.** §8.2 reserved **CD-233…CD-260** as the growth range for splitting M66/M67, but **CD-233…CD-248 is already Block 3 (the 16 standalone services)**. Sixteen identifiers were double-allocated | **Fixed.** The reserved growth range is now **CD-249…CD-260**, immediately after Block 3. Re-verified: CD-001…CD-248 is contiguous with zero overlaps |
| **TSA-03** | **Low** | **§1.3's layer diagram stated "~150 custom Odoo modules & extensions"** against §8.1.2's **232** module-attributed CD items, and folded the 10 applications into the CD count | **Fixed.** Corrected to 232 modules/extensions + 16 services, with the 10 applications shown separately as APP-01…APP-10 |
| **TSA-04** | **Medium** | **Two components required by NFRs are absent from the RFP's 24-system reference stack.** Appendix A registers **30 L4 components**; §7.1 registers 28. The additions are **ClamAV** (NFR-063, malware scanning on every upload) and **Vault/OpenBao** (NFR-062, IP-07, secrets management). Both are Wave 1 and both are P0-adjacent | **Disclosed and raised as a change.** §7.1 note (b) documents both with their driving NFR; **§25.3.9** raises the addition to RFP §5.4.3. Neither changes the cost model — both are $0 |
| **TSA-05** | **Medium** | **The specification set fixes Next.js at version 15; the current supported line is Next.js 16.** Six customer-facing applications would be built on a version leaving the supported line during the programme | **Raised, not unilaterally changed.** §11.1 and §25.2.2 state the finding; **D-16** and change **25.3.7** carry it. CON-03 is not breached — the platform remains Next.js + Payload CMS |
| **TSA-06** | **Medium** | **Three source documents give three different answers for P07's mobile framework** — `04-00` says React Native, `02-05` implies Next.js only, RFP §7.2 says "mobile" unqualified | **Raised for decision.** §11.9 recommends a PWA in Wave 7 with a Flutter native app if later approved, so the estate does not acquire a second mobile toolchain by default. **D-17** |
| **TSA-07** | Low | **§7.1's heading claimed 24 systems above a 28-row table** | **Fixed.** Heading now reads "24 Reference-Stack Systems in 28 Registered Components", with the reconciliation stated beneath |

#### G.4 Inherited Defects Confirmed but Not Fixed Here

These originate upstream. This document **discloses and works around** them; it does not silently
correct another document's register.

| Defect | Where disclosed |
|---|---|
| M66 and M67 specifications do not exist — 48 requirements estimated | §10.12, §25.1.1 |
| Roles R39–R46 unregistered; **R60 is a live duplicate-identity permission defect**; R54/R57 undefined | §12.1.2, §25.1.2 |
| SOD-13…SOD-30 used but unregistered | §12.1.4, §25.1.3 |
| Colliding `KPI-` identifiers | §12.4.4, §25.1.4 |
| **NFR-090/091/092 each carry two conflicting requirements**; NFR-088/089 repeated | §13.1, §25.1.5 |
| 28 allocated-but-unused requirement IDs in Category A | §25.1.6 |
| Per-module requirement figures do not sum to measured category totals in C, E, F, G, I | §10.1, §25.1.8 |
| Wave capacity unvalidated against restated effort | §25.1.9 |
| Register wave view omits M07's W1 and M25's W8 portions | §20.2, §25.1.10 |

#### G.5 Method Note — Why TSA-01 and TSA-02 Occurred

Both findings share one cause and it is worth naming, because it is the failure mode this
specification set has already suffered twice upstream.

**TSA-01** happened because the layer-distribution table was written from an impression formed while
drafting §10, rather than from §10 itself. The figures were plausible — they were within a few
modules of correct in every row — which is precisely what makes this class of error survive review.
It was caught only by parsing the 67 rows programmatically and counting the non-empty cells.

**TSA-02** happened because two identifier blocks were designed in separate passes and the reserved
growth range was written before Block 3's boundary was fixed. It was caught by expanding every
declared range and diffing against 1–248, not by reading the register.

**The generalisable point:** RG-06 exists because a figure that is nearly right reads exactly like a
figure that is right. Neither of these would have been found by careful reading. Both were found in
seconds by enumeration. Every count in this document has now been produced that way.

#### G.6 Audit Conclusion

> **This Technology Stack Specification provides complete, traceable technology coverage of the v2.0
> specification set: all 67 modules, all 12 portals, all 69 requirement classes, all 47 integrations,
> all 101 NFR identifiers covering 104 requirements, all 46 roles, all 6 isolation tiers, all 30
> segregation-of-duties controls, all 60 automations, all 95 KPIs and all 15 critical journeys have
> an assigned, named, versioned and licensed technology realisation. There are zero coverage gaps.**
>
> **It is fit** to be issued to implementation partners as the technical reference accompanying RFP
> v2.0, to be used for infrastructure planning and sizing, for build-versus-buy validation, and for
> engineering-standard enforcement.
>
> **It is not yet fit to be frozen as a build baseline**, and the reasons are specific and closable:
>
> 1. **Three blocking Wave 0 activities are incomplete** — the OCA v19 migration assessment (W0-01),
>    the split-residency legal opinion (W0-02, DEP-31/D-13), and the identifier-register completion
>    covering roles to R46 with R60 eliminated, SOD-13…30, the KPI collisions and the NFR-090/091/092
>    collision (W0-03).
> 2. **Six technology decisions are open** — D-13 residency opinion, D-14 funding the restated 1,513
>    PW, D-15 the Odoo version baseline and upgrade slot, D-16 the Next.js 15 → 16 timing, D-17 the
>    P07 mobile framework, and D-18 the RMM buy decision after the Wave 5 pilot.
> 3. **Nine change requests to the governing documents are unratified** (§25.3), of which two are
>    material: restating the CD register from 138 to 248 items, and adding a Wave 0 to the delivery
>    plan.
> 4. **Two module specifications do not exist** (M66, M67), so two of the 67 technology assignments
>    are made against registered scope rather than enumerated requirements.
>
> None of the four requires re-architecture. All four are register, decision and sequencing work that
> must complete before Wave 1 build begins.

---

*Technology Stack Specification v2.0 · 1000FIX-ERP-TECHSTACK-2026-002 · 13 August 2026*
*Derived from RFP v2.0 (1000FIX-ERP-RFP-2026-002) · Companion to BRD v2.0 and URD v2.0*
*Enterprise Architecture · 1000FiX Services Limited · CONFIDENTIAL*
