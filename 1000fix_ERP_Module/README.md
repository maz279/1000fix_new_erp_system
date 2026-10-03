---
id: FIX-ERP2-README
title: 1000FiX ERP System v2.0 — Module Documentation Repository
version: 2.2
date: 2026-08-15
status: ACTIVE
last_enumerated: 2026-08-15
revision_note: "v2.2 applies audit AUDIT-001 findings AF-01, AF-02, AF-03, AF-05, AF-06, AF-08"
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Technology Officer, 1000FiX Services Limited
---

# 1000FiX ERP System v2.0
# Module Documentation Repository

**67 modules · 11 categories · 12 portals · 36-month programme**

---

## What This Repository Is

This is the complete, authoritative definition of every module, feature and function of the
1000FiX Enterprise Resource Planning system.

It exists because 1000FiX Services Limited — Bangladesh's largest and only ISO 9001:2015
certified after-sales service provider — has committed, across its business plan, its
Service App scope of work and its portal roadmap, to operating **fourteen distinct revenue
streams**. The originally approved ERP covered eleven modules and could run five of them.

This repository defines the system that can run all fourteen, benchmarked against SAP
S/4HANA Service, Oracle Fusion Cloud, Microsoft Dynamics 365, IFS Cloud, Odoo 19 and the
specialist after-sales service platforms used in comparable markets.

---

## Start Here

> **Read the audit report first.** An August 2026 audit of this repository found 5 critical,
> 6 high, 9 medium and 4 low findings, including two factual errors with legal consequence.
> Remediation is in progress. **Do not build from this set without reading
> [00-06 Documentation Audit Report](00_Governance_and_Charter/00-06_Documentation_Audit_Report.md).**

| I want to… | Go to | Status |
|---|---|---|
| **See what is known to be wrong** | [00-06 Documentation Audit Report](00_Governance_and_Charter/00-06_Documentation_Audit_Report.md) | ✅ |
| Understand the folder layout | [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md) | ✅ |
| Understand why the scope expanded | [00-02 Executive Summary](00_Governance_and_Charter/00-02_Executive_Summary_and_Scope_Charter.md) | ✅ |
| See what changed from the v1.0 plan | [00-03 Scope Expansion Delta](00_Governance_and_Charter/00-03_Scope_Expansion_Delta_v1_to_v2.md) | ✅ |
| **See the complete module list — authoritative** | [02-02 Module Catalogue Master Register](02_Architecture/02-02_Module_Catalogue_Master_Register.md) | ✅ |
| Understand how modules fit together | [02-01 Architecture & System Map](02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md) | ✅ *(with correction notice)* |
| Read one module in full | [03_Modules/](03_Modules/) — pick a category folder | ✅ **67 of 67 written** |
| Read one portal specification in full | `03_Modules/K_Platform_and_Technology/` — see ⚠ below | ✅ **12 of 12 written**, currently **misfiled** |
| See the delivery plan | [06-01 Implementation Roadmap](06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md) | ✅ |
| See the business case and targets | [06-02 KPI, Benefits & Acceptance](06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md) | ✅ *(cost line provisional)* |
| See the risks | [00-04 Risks & Governance](00_Governance_and_Charter/00-04_Risks_Assumptions_Dependencies_and_Governance.md) | ✅ |
| **See what the audits found** | [00-06 Audit 1](00_Governance_and_Charter/00-06_Documentation_Audit_Report.md) · [00-07 Audit 2 — Category H & repository integrity](00_Governance_and_Charter/00-07_Category_H_Audit_and_Repository_Integrity_Report.md) · [AUDIT-001 Audit 3 — content & repository integrity](../project_content/_AUDIT/AUDIT-001_Content_and_Repository_Integrity_Audit.md) | ✅ **19 findings open across three audits** |
| **See what content the programme owes** | [ERP Content Master Index](../project_content/1000FiX_ERP_Content_Master_Index.md) — 452 files, 21 categories | ✅ **Issued 2026-08-15** |
| See regulatory obligations | [05-06 NFR & Standards](05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md) §6 | ✅ |
| See how we benchmarked against world-class ERP | `01_Research_and_Benchmarking/01-01_ERP_Market_Benchmark_Study.md` | ⬜ **Planned** |
| See which modules were missing and why | `01_Research_and_Benchmarking/01-03_Module_Gap_Analysis.md` | ⬜ **Planned** |
| Understand where module boundaries sit | `02_Architecture/02-03_Module_Boundary_and_Overlap_Rules.md` | ⬜ **Planned** — boundaries are currently declared in each `_CATEGORY_OVERVIEW.md` and each module file §3 |
| Look up an identifier convention | `99_Reference/99-02_Identifier_Conventions.md` | ⬜ **Planned** — conventions are in `02-02` §1 and §5 meanwhile |

**Legend:** ✅ written · ⬜ planned, not yet written. Links to planned files are shown as plain
text, not hyperlinks, so nothing in this README leads to a missing page.

---

## Documentation Completeness

> **Enumerated from the filesystem on 2026-08-15.** These are counted figures. Any completeness
> statement in this repository without an enumeration date beside it is not authoritative — see
> proposed rule **RG-07** in
> [project_content/_AUDIT/AUDIT-001](../project_content/_AUDIT/AUDIT-001_Content_and_Repository_Integrity_Audit.md).

| Layer | Written | Planned | Total |
|---|---:|---:|---:|
| Governance & charter | 6 | 1 | 7 |
| Research & benchmarking | 0 | 5 | 5 |
| Architecture | 3 | 2 | 5 |
| Module specifications | **67** | **0** | 67 |
| Category overviews | 11 | 0 | 11 |
| Portals & applications | **13** | **0** | 13 |
| Cross-cutting specifications | 6 | 0 | 6 |
| Delivery & implementation | 2 | 4 | 6 |
| Reference | 0 | 4 | 4 |
| Repository files (README, folder map, module template) | 3 | 0 | 3 |
| Category & suite audit reports | 7 | 0 | 7 |
| Superseded pillar drafts (archive) | 5 | 0 | 5 |
| **Total** | **123 on disk** | **16 planned** | **139** |

**The specification layer is complete: 67 of 67 modules and 12 of 12 portals are written.**
What remains unwritten is the research layer (5 files), the reference layer (4), four delivery
documents, the `00-05` decision log and two architecture documents — 16 in total.

> ⚠ **Structural defect — the twelve portal specifications are in the wrong folder.**
> `P01`–`P12` are saved in `03_Modules/K_Platform_and_Technology/` rather than
> `04_Portals_and_Applications/` as [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md) §2 requires. They
> are complete (771 KB, 10,020 lines) and authoritative; only their location is wrong.
> Correcting it needs CTO approval under FOLDER_STRUCTURE.md §8. Tracked as audit finding
> **AF-01**.

| Category | Specs | Requirements | Effort |
|---|:--:|---:|---:|
| A — Service Delivery & Operations | 7 / 7 | 362 | 206 PW |
| B — Customer Engagement & Experience | 7 / 7 | 320 | 148 PW |
| C — Commercial, Pricing & Revenue | 9 / 9 | 494 | 262 PW |
| D — Circular & Asset-Based Business | 3 / 3 | 109 | 60 PW |
| E — Supply Chain & Inventory | 6 / 6 | 235 | 119 PW |
| F — Asset, Equipment & Facilities | 5 / 5 | 232 | 114 PW |
| G — Finance & Treasury | 8 / 8 | 333 | 185 PW |
| H — People & Workforce | 7 / 7 | 310 | 124 PW |
| I — Governance, Risk, Quality & Knowledge | 4 / 4 | 170 | 78 PW |
| J — Data, Analytics & Intelligence | 4 / 4 | 146 | 97 PW |
| **K — Platform & Technology** | **7 / 7** | 219 ⚠ | 120 PW ⚠ |
| **Total** | **67 / 67** | **2,930 ⚠** | **1,513 PW ⚠** |

⚠ **The requirement and effort columns predate `M66` and `M67` and must be recounted.** The
Category K figures of 219 requirements and 120 PW were measured across five module files;
Category K now has seven. The totals are therefore **understated by two modules' worth** and
must not be used for contractual commitment (rule **RG-05**). Tracked as audit findings
**AF-06** and **AF-08**; recount instruction at recommendation R-04.

**Specification counts are enumerated; requirement and effort figures are counted but stale.**
See [02-02 §3](02_Architecture/02-02_Module_Catalogue_Master_Register.md) for the
estimate-versus-actual analysis,
[00-06 Documentation Audit Report](00_Governance_and_Charter/00-06_Documentation_Audit_Report.md)
and [00-07 Category H Audit](00_Governance_and_Charter/00-07_Category_H_Audit_and_Repository_Integrity_Report.md)
for identifier-integrity findings, and
[AUDIT-001 Content & Repository Integrity Audit](../project_content/_AUDIT/AUDIT-001_Content_and_Repository_Integrity_Audit.md)
for the 18 findings raised on 2026-08-15, of which 9 remain open.

---

## The Company

| | |
|---|---|
| **Legal name** | 1000FiX Services Limited |
| **Founded** | 29 August 2017 |
| **Position** | Bangladesh's largest after-sales service provider; the country's only ISO 9001:2015 certified IT service provider |
| **Network** | 51+ service centres across all 8 administrative divisions |
| **People** | 500+ employees, including 200–400 field technicians |
| **Customers** | 250,000+ per month |
| **Brand partnerships** | 17+ authorised warranty service agreements |
| **Hotline** | 16743 |
| **Head office** | 586/1 (4th Floor), Begum Rokeya Sarani, Shewrapara, Mirpur, Dhaka-1216 |

---

## The Fourteen Revenue Streams

| # | Revenue Stream | Owning Module |
|---|---|---|
| 1 | Authorised brand warranty service | M09 |
| 2 | Out-of-warranty paid repair | M01 / M31 |
| 3 | AMC / RAMC maintenance contracts | M08 |
| 4 | Warranty extension & protection products | M09 |
| 5 | Spare parts & accessories | M15 / M38 |
| 6 | Corporate managed IT services (MSP) | M05 |
| 7 | Equipment rental / Equipment-as-a-Service | M13 |
| 8 | Data recovery | M06 |
| 9 | Data backup & archival subscriptions | M06 / M39 |
| 10 | Refurbished device resale | M14 |
| 11 | Trade-in / exchange margin | M14 |
| 12 | E-waste recycling & material recovery | M18 |
| 13 | Marketplace commission & settlement | M12 |
| 14 | Advertising, boost & lead placement | M12 / M35 |

---

## The 67 Modules

### A — Service Delivery & Operations (7)
`M01` Service Request & Order Management · `M02` Field Service & Dispatch ·
`M03` Service Logistics & Reverse Logistics · `M04` Branch & Front-Desk Operations ·
`M05` Remote Support & Managed Services · `M06` Data Services ·
`M31` Workshop & Depot Repair Management ★

### B — Customer Engagement & Experience (7)
`M07` CRM, Sales Pipeline & Account Management · `M10` Loyalty, Membership & Rewards ·
`M27` Omnichannel Contact Centre · `M32` Conversational AI & Virtual Assistant ★ ·
`M33` Customer & Party Master Management ★ · `M34` Customer Experience & Complaints ★ ·
`M35` Marketing, Campaigns & Demand Generation ★

### C — Commercial, Pricing & Revenue (9)
`M08` Contract Lifecycle Management · `M09` Warranty, Protection Plans & Claims ·
`M11` Pricing, Rate Cards & Dynamic Pricing · `M12` Marketplace & Seller Ecosystem ·
`M36` Quotation, Estimation & Tender Management ★ ·
`M37` Product & Service Catalogue Management ★ · `M38` E-Commerce & Digital Storefront ★ ·
`M39` Subscription & Recurring Revenue ★ · `M40` Partner, Channel & Franchise ★

### D — Circular & Asset-Based Business (3)
`M13` Rental & Equipment-as-a-Service · `M14` Trade-In, Refurbishment & Resale ·
`M18` E-Waste, Recycling & Circular Economy

### E — Supply Chain & Inventory (6)
`M15` Spare Parts & Inventory Management · `M16` Procurement & Strategic Sourcing ·
`M41` Warehouse Management ★ · `M42` Supplier Relationship & Performance ★ ·
`M43` Demand Planning & Replenishment ★ · `M44` Import, Trade Compliance & Landed Cost ★

### F — Asset, Equipment & Facilities (5)
`M17` Device & Customer Asset Registry · `M45` Enterprise Asset & Test Equipment ★ ·
`M46` Fleet & Vehicle Management ★ · `M47` Facility & Branch Infrastructure ★ ·
`M48` IoT Telemetry & Predictive Maintenance ★

### G — Finance & Treasury (8)
`M19` Financial Accounting & General Ledger · `M20` Accounts Receivable & Collections ·
`M49` Fixed Assets & Capital Investment ★ · `M50` Treasury, Cash & Banking ★ ·
`M51` Tax & Regulatory Compliance (Bangladesh) ★ ·
`M52` Accounts Payable & Employee Expense ★ ·
`M53` Revenue Recognition, Commission & Settlement ★ ·
`M54` Cost Accounting, Budgeting & FP&A ★

### H — People & Workforce (7)
`M21` Core HR & Employee Lifecycle · `M22` Learning, Competency & Certification ·
`M55` Time, Attendance & Workforce Scheduling ★ ·
`M56` Payroll, Benefits & Statutory Compliance ★ ·
`M57` Performance, Incentives & Compensation ★ · `M58` Talent Acquisition & Onboarding ★ ·
`M59` Health, Safety & Wellbeing ★

### I — Governance, Risk, Quality & Knowledge (4)
`M23` Quality Management System · `M24` Document, Records & E-Signature ·
`M60` Governance, Risk & Compliance ★ · `M61` Knowledge Management & Technical Library ★

### J — Data, Analytics & Intelligence (4)
`M25` Business Intelligence & Reporting · `M26` AI/ML Services & Model Operations ·
`M62` Data Platform, Warehouse & Governance ★ ·
`M63` Process Automation & Workflow Orchestration ★

### K — Platform & Technology (7)
`M28` Integration, API & Event Platform · `M29` Identity, Access & Information Security ·
`M30` Platform Administration & Configuration · `M64` Master Data Management ★ ·
`M65` Multi-Entity, Multi-Country & Localisation ★ · `M66` Internal IT Service Management ★ ·
`M67` Project, Program & Portfolio Management ★

★ = added in this revision after benchmarking against enterprise ERP standards.

---

## The Twelve Portals

`P01` Customer Self-Service · `P02` Technician Mobile · `P03` Admin Operations ·
`P04` Corporate B2B · `P05` Vendor & Supplier · `P06` Analytics & Executive ·
`P07` Marketplace Seller · `P08` Brand Partner · `P09` Logistics & Rider ·
`P10` Contact Centre Console · `P11` Field Auditor · `P12` Partner & Referral

---

## Technology Foundation

| Layer | Content | Licence Cost |
|---|---|---|
| L1 | Odoo 19 Community Edition | $0 |
| L2 | 140+ OCA modules across 18 repositories | $0 |
| L3 | Free third-party Odoo modules | $0 |
| L4 | 24 standalone open-source systems | $0 |
| L5 | Custom development — Odoo modules, services, applications | Development cost |
| L6 | Four commercial components where no viable open source exists | $0–36K / 3 years |

**Software licence cost for the ERP core: $0.**

---

## Document Conventions

| Convention | Rule |
|---|---|
| Module IDs `M01`–`M67` | Permanent. Never reused, never renumbered. |
| Portal IDs `P01`–`P12` | Permanent. |
| Requirement IDs `FR-<CODE>-nnn` | Permanent. A withdrawn requirement's ID is retired, not reused. |
| Priority | `P0` blocking · `P1` must-have · `P2` important · `P3` desirable |
| Delivery layer | `L1`–`L6` as above |
| Wave | `W1`–`W9` across 36 months |
| Status | Proposed · Approved · In Build · Verified · Deferred · Superseded |

Full conventions: `02_Architecture/02-02_Module_Catalogue_Master_Register.md` §1 (register
rules), §5 (complete 67-module code register) and §6 (requirement identifier allocation).
A consolidated `99_Reference/99-02_Identifier_Conventions.md` is planned.

---

## Status

| Item | State |
|---|---|
| Module architecture | Defined — 67 modules, 11 categories |
| Module specifications | **Complete — 67 of 67** (enumerated 2026-08-15) |
| Portal specifications | **Complete — 12 of 12**, misfiled (finding AF-01) |
| Benchmark study | **Recorded per-module** in §4 of every specification. The consolidated study `01-01` is **not written**; `01_Research_and_Benchmarking/` is empty |
| Gap analysis | **Not written** — `01-03` planned. The scope delta is documented in `00-03` |
| Decision log | **Not written** — `00-05` is absent while audits cite decision D-14 (finding AF-04) |
| Content register | **Issued** — [`project_content/1000FiX_ERP_Content_Master_Index.md`](../project_content/1000FiX_ERP_Content_Master_Index.md), 452 files, draft for approval |
| Programme charter | Draft, awaiting approval |
| Implementation roadmap | Draft |
| Effort variance | **Open** — build 1,513 PW vs 834 PW approved, plus 520–775 PW content not in the business case (findings AF-08, AF-09) |

**This documentation set is DRAFT FOR APPROVAL.** Nothing here is authorised for build until
the ERP Steering Committee approves the charter in `00_Governance_and_Charter/00-02`.

---

*1000FiX Services Limited · Hotline 16743 · info@1000fix.com · ISO 9001:2015 Certified*
