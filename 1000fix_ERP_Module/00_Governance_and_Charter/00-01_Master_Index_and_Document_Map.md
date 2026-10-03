---
id: FIX-ERP2-000
title: Master Index & Document Map
project: 1000FiX Enterprise Platform — ERP System v2.0 (Expanded Scope)
version: 2.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Technology Officer, 1000FiX Services Limited
---

# 1000FiX ERP System v2.0 — Expanded Scope
# Master Index & Document Map

---

> **Revision 2.1 — audit findings C-01, H-02, H-04.** This index was written for a
> 30-module, 5-pillar architecture and a superseded document numbering scheme. The current
> structure is **67 modules in 11 categories**, and the folder layout is defined in
> `FOLDER_STRUCTURE.md` at the repository root.
>
> **Use these instead of the tables below:**
>
> | For | Read |
> |---|---|
> | Navigation and folder layout | `FOLDER_STRUCTURE.md` |
> | The authoritative module list, codes and totals | `02_Architecture/02-02_Module_Catalogue_Master_Register.md` |
> | Known defects in this document set | `00_Governance_and_Charter/00-06_Documentation_Audit_Report.md` |
> | Requirement identifier allocation | `05_Cross_Cutting_Specifications/05-01` §1.3a |
>
> The **conventions, identifier schemes and source-evidence register** below remain valid.
> The **module short-code table in §3 is incomplete** — it lists 30 codes; the full 67-code
> register is in `02-02` §5.

---

## 1. What This Document Set Is

This folder contains the **complete planned module, feature and function definition** for the
**significantly expanded scope** of the 1000FiX Enterprise Resource Planning (ERP) System.

It supersedes — but does **not** discard — the v1.0 ERP plan held in
`ERP system for 1000 fix/` (BRD `1000FIX-ERP-BRD-2026-001`, RFP `1000FIX-ERP-RFP-2026-001`,
URD `1000FIX-ERP-URD-2026-001`, Technology Stack Specification, and the Odoo 19 CE
Implementation Strategy). Everything in v1.0 is carried forward as the **baseline**; this set
adds the newly approved expansion.

| | v1.0 Baseline | v2.0 Expanded |
|---|---|---|
| ERP core modules | 11 | **30** |
| Portals / applications | 6 | **12** |
| Custom Odoo modules (CD) | 20 | **58** |
| Catalogued functional requirements | ~405 | **1,180+** |
| Business lines covered | 5 revenue streams | **14 revenue streams** |
| Planning horizon | 18 months / 6 phases | **36 months / 9 waves** |
| Geographic model | Bangladesh, single legal entity | **Multi-entity, multi-country ready** |

---

## 2. Document Map

Read in the order below. Documents 01–04 are the *decision layer*; 05–11 are the
*specification layer*; 12–20 are the *engineering and governance layer*.

### Decision Layer

| # | Document | Purpose | Primary Audience |
|---|---|---|---|
| 00 | `00_MASTER_INDEX_and_Document_Map.md` | This file — navigation, conventions, ID schemes | All |
| 01 | `01_Executive_Summary_and_Expanded_Scope_Charter.md` | Why the scope expanded, what the business gets, investment envelope | Board, CEO, CFO |
| 02 | `02_Scope_Expansion_Delta_v1_to_v2.md` | Line-by-line delta from the v1.0 plan, with evidence trail | CTO, PMO, Vendor |
| 03 | `03_ERP_Module_Architecture_and_System_Map.md` | Pillars, layering, module dependency graph, deployment topology | Architects |
| 04 | `04_Module_Catalog_Master_Register.md` | The authoritative register of all 30 modules | PMO, Vendor, QA |

### Specification Layer — Modules, Features & Functions

| # | Document | Modules Covered |
|---|---|---|
| 05 | `05_Pillar_A_Core_Service_Operations_Modules.md` | **M01–M06** — SRM, FSM, Logistics, Front Desk, Remote/Managed Services, Data Services |
| 06 | `06_Pillar_B_Customer_Commercial_Revenue_Modules.md` | **M07–M14** — CRM, Contracts, Warranty, Loyalty, Sales & Pricing, E-Commerce & Marketplace, Rental, Trade-In & Refurbishment |
| 07 | `07_Pillar_C_Supply_Chain_and_Asset_Modules.md` | **M15–M18** — Inventory, Procurement, Asset & IoT Registry, E-Waste & Sustainability |
| 08 | `08_Pillar_D_Finance_People_Governance_Modules.md` | **M19–M24** — Finance & BD Compliance, Billing & Settlement, HR & Payroll, Learning & Certification, QMS, DMS |
| 09 | `09_Pillar_E_Intelligence_and_Platform_Modules.md` | **M25–M30** — BI & Data Platform, AI/ML Services, Conversational AI & Contact Centre, Integration Platform, Identity & Security, Platform Administration |
| 10 | `10_Portal_and_Application_Suite_Specification.md` | The 12 portals and applications that surface the ERP |
| 11 | `11_Feature_and_Function_Register.md` | The consolidated numbered register of every feature and function |

### Engineering & Governance Layer

| # | Document | Purpose |
|---|---|---|
| 12 | `12_Data_Model_and_Entity_Catalog.md` | Entities, key attributes, relationships, ERDs per pillar |
| 13 | `13_Integration_and_API_Catalog.md` | Internal APIs, external integrations, event catalogue, webhooks |
| 14 | `14_Role_Permission_and_Access_Matrix.md` | 38 roles, portal access, CRUD matrix, data-isolation rules |
| 15 | `15_Business_Rules_and_Automation_Catalog.md` | Enforced business rules and the automation/workflow inventory |
| 16 | `16_NonFunctional_Requirements_and_Architecture_Standards.md` | Performance, availability, security, localisation, accessibility |
| 17 | `17_Implementation_Roadmap_and_Phasing.md` | 9 delivery waves over 36 months, module sequencing, team model |
| 18 | `18_KPI_Benefits_and_Acceptance_Criteria.md` | Target KPIs, benefit model, phase gates, UAT acceptance |
| 19 | `19_Technology_Stack_and_Build_vs_Buy_Decisions.md` | Layer-by-layer stack, licences, build-vs-buy rationale |
| 20 | `20_Risks_Assumptions_Dependencies_and_Governance.md` | Risk register, RAID log, governance operating model |

---

## 3. Identifier Conventions

All identifiers used across this document set are stable and must be quoted in
requirements traceability, test cases, sprint tickets and vendor deliverables.

| Prefix | Meaning | Example | Defined In |
|---|---|---|---|
| `M01`–`M30` | ERP module | `M05` = Remote Support & Managed Services | Doc 04 |
| `P01`–`P12` | Portal / application | `P07` = Marketplace Seller Portal | Doc 10 |
| `FR-<MOD>-nnn` | Functional requirement | `FR-SRM-014` | Doc 11 |
| `FN-<MOD>-nnn` | Function (system behaviour within a feature) | `FN-RNT-007` | Doc 11 |
| `E-<MOD>-nn` | Data entity | `E-CTR-03` | Doc 12 |
| `INT-nnn` | Integration | `INT-042` | Doc 13 |
| `EVT-<domain>.<verb>` | Domain event | `EVT-service_order.completed` | Doc 13 |
| `R01`–`R38` | User role | `R14` = Logistics Coordinator | Doc 14 |
| `BRU-<MOD>-nn` | Business rule | `BRU-FIN-07` | Doc 15 |
| `AUT-nnn` | Automation / workflow | `AUT-031` | Doc 15 |
| `NFR-nnn` | Non-functional requirement | `NFR-018` | Doc 16 |
| `W1`–`W9` | Delivery wave | `W4` | Doc 17 |
| `KPI-nnn` | Key performance indicator | `KPI-022` | Doc 18 |
| `CD-nnn` | Custom Odoo module | `CD-034` | Doc 19 |
| `RSK-nnn` | Risk | `RSK-021` | Doc 20 |

### Module Short Codes

| Code | Module | Code | Module |
|---|---|---|---|
| `SRM` | Service & Repair Management | `INV` | Inventory & Spare Parts |
| `FSM` | Field Service & Dispatch | `SCM` | Procurement & Vendor |
| `LOG` | Logistics & Reverse Logistics | `AST` | Asset, Device & IoT Registry |
| `FRD` | Front Desk & Queue | `ESG` | E-Waste & Sustainability |
| `RMS` | Remote Support & Managed Services | `FIN` | Finance & BD Compliance |
| `DTS` | Data Services | `BIL` | Billing, Revenue & Settlement |
| `CRM` | Customer Relationship Management | `HRM` | HR, Payroll & Workforce |
| `CTR` | Contract Lifecycle Management | `LMS` | Learning & Certification |
| `WTY` | Warranty & Claims | `QMS` | Quality & Compliance |
| `LOY` | Loyalty, Referral & Campaigns | `DMS` | Document & Records |
| `SLS` | Sales, Quotation & Pricing | `BID` | BI & Data Platform |
| `ECM` | E-Commerce & Marketplace | `AIM` | AI/ML Services |
| `RNT` | Rental & Asset-as-a-Service | `CCE` | Conversational AI & Contact Centre |
| `TRF` | Trade-In, Refurbishment & Resale | `IPF` | Integration Platform |
| | | `SEC` | Identity, Security & Audit |
| | | `ADM` | Platform Administration |

### Priority Scale

| Priority | Meaning | Treatment |
|---|---|---|
| **P0** | Regulatory, safety or go-live blocking | Cannot be descoped |
| **P1** | Must-have — core business capability | Descope only with CEO approval |
| **P2** | Important — significant value, deferrable one wave | PMO change control |
| **P3** | Desirable — enhances experience or efficiency | Backlog, opportunistic |

### Delivery Layer Codes

Carried forward from the v1.0 Technology Stack Specification and extended:

| Layer | Meaning |
|---|---|
| **L1** | Odoo 19 CE native capability |
| **L2** | OCA (Odoo Community Association) module |
| **L3** | Free / community third-party Odoo module |
| **L4** | Complementary standalone open-source system |
| **L5** | Custom development (Odoo `CD-*` module, service, or app) |
| **L6** | *New in v2.0* — External SaaS or commercial component where open source is not viable |

---

## 4. Source Evidence Used to Build This Set

Every expansion in v2.0 traces to material already inside this workspace. The table
below is the audit trail; Doc 02 maps each new module to its source line by line.

| Source Document | Location | What It Contributed |
|---|---|---|
| ERP Comprehensive BRD v1.0 | `ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` | 11 baseline modules, 10 business objectives, 190+ requirements, business rules, ROI model |
| ERP Comprehensive URD v1.0 | `ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_URD.md` | 20 personas, role & access matrix, 12 user journeys, adoption plan |
| ERP Comprehensive RFP v1.0 | `ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_RFP.md` | 405 requirement register, evaluation criteria, vendor obligations |
| ERP Technology Stack Specification | `ERP system for 1000 fix/1000FiX_ERP_Technology_Stack_Specification.md` | 5-layer stack, 94+ OCA modules, 20 CD modules, deployment & security architecture |
| ERP Implementation Strategy (Odoo 19 CE) | `ERP system for 1000 fix/1000FiX_ERP_Implementation_Strategy_Odoo19CE_OpenSource.md` | Selection hierarchy, gap analysis, TCO comparison |
| ERP Implementation Docs 01–19 | `ERP system for 1000 fix/project_implementation_doc/` | Module architecture patterns, DB schema, sprint model, API spec, DevOps, QA, offline sync, AI dispatch |
| ERP Roadmap Phases 01–15 | `ERP system for 1000 fix/project_Roadmap_Implementation/` | Milestone decomposition format, phase gates |
| **Business Plan** | `1000fix_business/Business planning for 1000 fix.docx` | **Rental, data recovery, data backup, refurbishment & resale, e-waste recycling, 24/7 technical support, managed services, healthcare/IT-infrastructure/specialty AMC** |
| **Service App SOW** | `1000fix_business/SOW for 1000FiX Service App Development.docx` | **Marketplace aggregator model, external engineer/shop onboarding, bidding & quotation competition, commissions, paid boost & in-app ads, credit points, referral, multi-tier corporate approval, remote-desktop support, logistics interface** |
| Integrated Portal BRD / URD / SRS | `Intergrated_web_portal/project_requirement_document/` | 8-portal platform definition, portal requirement IDs |
| Portal Implementation Guides IMPL-01…64 | `Intergrated_web_portal/Technical_documentation_roadmap/` | **Predictive maintenance, demand forecasting, dynamic pricing, partner commission engine, third-party technician marketplace, ClickHouse warehouse, Kong API gateway, CQRS/event sourcing, multi-country framework, SOC 2 / ISO 27001, GDPR** |
| Digital Transformation Strategy | `The solution/1000FIX_Digital_Transformation_Strategy_AI_Portal_Systems_Report*.md` | Portal ecosystem vision, AI agent architecture, ROI targets |
| Development Approach Analysis | `The solution/1000FIX_Development_Approach_Analysis_Report.md` | Build-vs-buy precedent, option scoring method |
| Smart Portal Marketing Suite | `Marketing_1/`, `Marketing_2/` | Product positioning, competitive differentiation, use-case library |
| Company Profile | `1000FiX_Services_Company_Profile.md` | Service catalogue, brand partners, value-added programmes |
| Corporate Website Programme | `1000_fix_corporate_website/` | Content taxonomy, service/city/brand page structure feeding catalogue master data |
| Repository Conventions | `AGENTS.md` | Naming, git, coding and testing standards to be inherited |

---

## 5. How the ERP Relates to the Other 1000FiX Programmes

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     1000FiX DIGITAL ESTATE (v2.0)                        │
│                                                                          │
│   ┌────────────────────────┐        ┌──────────────────────────────┐    │
│   │  CORPORATE WEBSITE     │        │  INTEGRATED SMART PORTAL     │    │
│   │  (Next.js + Payload)   │◄──────►│  PLATFORM (8→12 portals)     │    │
│   │  Marketing · SEO ·     │        │  Customer · Technician ·     │    │
│   │  Content · Lead capture│        │  Admin · B2B · Vendor ·      │    │
│   └───────────┬────────────┘        │  Analytics · Marketplace ·   │    │
│               │                     │  Partner · Rental · Recycle  │    │
│               │                     └──────────────┬───────────────┘    │
│               │                                    │                    │
│               │        REST / JSON-2 / GraphQL / Webhooks / Events      │
│               └──────────────────┬─────────────────┘                    │
│                                  ▼                                      │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │              1000FiX ERP v2.0 — SYSTEM OF RECORD                 │  │
│   │  30 modules · 5 pillars · Odoo 19 CE + OCA + OSS + Custom        │  │
│   │  THIS DOCUMENT SET DEFINES THIS LAYER                            │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                  │                                      │
│   ┌──────────────────────────────▼───────────────────────────────────┐  │
│   │  DATA & INTELLIGENCE PLATFORM                                    │  │
│   │  PostgreSQL 16 · TimescaleDB · ClickHouse · Metabase · MLflow    │  │
│   └──────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

**Boundary rule:** the ERP owns *state and truth*; the portals own *experience and reach*.
Any business object that has a lifecycle, a financial consequence, or an audit obligation
is mastered in the ERP. Portals never hold authoritative copies.

---

## 6. Document Status & Change Control

| Version | Date | Author | Change |
|---|---|---|---|
| 2.0-draft | 2026-08-12 | Enterprise Architecture | Initial issue of the expanded-scope module, feature and function definition |

**Change control:** After approval, any change to a module boundary, a P0/P1 requirement,
or a delivery wave requires a Change Request approved by the ERP Steering Committee
(see Doc 20 §5). Additions of P2/P3 requirements inside an existing module may be
approved by the PMO.

**Open decisions requiring sign-off before Wave 1 build starts** — see Doc 20 §6:

1. Marketplace commercial model (commission %, settlement terms, seller liability).
2. Whether Rental and Refurbished Resale operate inside the ERP legal entity or a subsidiary.
3. Multi-country target markets and sequence (affects M30 design in Wave 6).
4. Contact-centre telephony vendor (affects M27 in Wave 4).
5. Data-residency posture for customer data recovered under M06 Data Services.

---

*1000FiX Services Limited — ERP System v2.0 Expanded Scope*
*586/1 (4th Floor), Begum Rokeya Sarani, Shewrapara, Mirpur, Dhaka-1216, Bangladesh*
*Hotline 16743 · info@1000fix.com · ISO 9001:2015 Certified*
