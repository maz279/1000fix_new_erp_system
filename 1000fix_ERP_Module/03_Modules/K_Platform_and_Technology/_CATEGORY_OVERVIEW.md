---
id: FIX-ERP2-CAT-K
category: K
category_name: Platform & Technology
module_count: 7
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT
---

# Category K — Platform & Technology

**7 modules · Category owner: Chief Technology Officer**

---

## 1. What Belongs in This Category

The technical substrate every other module depends on, plus the disciplines that keep the
estate coherent as it grows to 67 modules, 12 portals and eventually more than one country.

If a capability answers *"how does anything connect, who is allowed to do what, where does
configuration live, and how does this run in production"*, it belongs here.

**These modules have no business process of their own.** Their success is measured by the
absence of problems in everything else.

---

## 2. Modules

| ID | Module | Status | Priority | Wave | One-Line Definition |
|---|---|---|:--:|:--:|---|
| **M28** | Integration, API & Event Platform | Re-scoped | P0 | W1 | Gateway, API management, event bus, connectors, webhooks, sync protocol and integration observability |
| **M29** | Identity, Access & Information Security | Retained | P0 | W1 | Who is who, what they may do, and the audit trail and data protection that proves it |
| **M64** | Master Data Management & Configuration ★ | New | P1 | W2 | Master data ownership, stewardship workflows, data quality rules, reference data distribution, business-rule parameters |
| **M65** | Multi-Entity, Multi-Country & Localisation ★ | New | P2 | W9 | Legal entities, country packs, locale packs, currency, translation, jurisdiction isolation, expansion readiness |
| **M66** | Internal IT Service Management ★ | New | P2 | W6 | The Company's own IT: employee helpdesk, internal asset and licence management, change and incident management |
| **M30** | Platform Administration & Configuration | Re-scoped | P0 | W1 | Organisation structure, users, environments, feature flags, jobs, health console, archival, announcements |
| **M67** | Project, Program & Portfolio Management ★ | New | P2 | W7 | Delivery of projects: corporate rollouts, IT infrastructure engagements, branch openings, internal initiatives |

★ = new in v2.1 after enterprise benchmarking.

### 2.1 The Twelve Portal Specifications Are Filed Here — But Are Not Category K Modules

`FOLDER_STRUCTURE.md` §188–201 places `P01`–`P12` in **`04_Portals_and_Applications/`**. All
twelve specification files are physically in **this folder**, so this directory holds **19 spec
files, not 7**: seven Category K modules plus twelve portals.

| | Files | Requirements | Effort |
|---|---:|---:|---:|
| Category K modules (M28, M29, M30, M64, M65, M66, M67) | 7 | **281** | 151 PW |
| Portal suite (P01–P12) — *belongs in `04_`* | 12 | **358** | 298 PW |
| **In this directory** | **19** | **639** | **449 PW** |

Portals are **consumers** of modules, not modules. They carry `FR-POR-###` identifiers, a
`Portal Identity` section rather than `Module Identity`, and their own audit report
(`_PORTAL_SUITE_AUDIT_REPORT.md`). Counting them as Category K inflates the category by 12
specifications and 358 requirements.

**Open — relocation decision required.** Either move `P01`–`P12` and
`_PORTAL_SUITE_AUDIT_REPORT.md` to `04_Portals_and_Applications/`, or amend `FOLDER_STRUCTURE.md`
to record this folder as their permanent home. Until then any count of "Category K" or of
`03_Modules` is ambiguous. *(Audit finding A3-02.)*

---

## 3. Why Internal ITSM Is Not the Same as Managed Services

This is the boundary most likely to be confused, and it matters commercially.

| | M05 Remote Support & Managed Services (Category A) | M66 Internal IT Service Management |
|---|---|---|
| **Serves** | Paying corporate clients | 1000FiX's own 500+ employees |
| **Revenue** | Billable — a revenue stream | Cost centre |
| **SLA** | Contractual, with service credits | Internal target |
| **Assets** | Client estates | Company laptops, phones, branch IT, licences |
| **Failure cost** | Contract penalty, client loss | Internal productivity |
| **Analogue** | PSA / RMM for an MSP | ServiceNow ITSM for internal IT |

They share a ticket shape and nothing else. Merging them would mean internal helpdesk noise
sitting in a system audited by paying clients.

---

## 4. Why Project Management Belongs Here

1000FiX runs real projects that are not service orders:

| Project Type | Example |
|---|---|
| Corporate rollout | Registering and commissioning 400 devices for a new AMC client across 12 sites |
| IT infrastructure engagement | Designing and installing a client's server and network refresh under an MSP contract |
| Branch opening | Standing up a new 1000FiX Station: premises, fit-out, stock, staffing, systems, licences |
| Bulk decommission | A corporate client retiring 300 assets with data destruction and buy-back |
| Internal initiative | The ERP programme itself, and each of its nine waves |

A service order cannot model a six-month engagement with phases, a budget, a resource plan
and milestone billing. That is professional services automation, and it is a recognised ERP
module in every benchmark system.

| Analogue | Module |
|---|---|
| Oracle | Project Portfolio Management — Project Management, Costing, Billing |
| SAP | Project System (PS) / Commercial Project Management |
| Dynamics 365 | Project Operations |
| Odoo | Project + Timesheets |

---

## 5. Why Master Data Management Is Separate from Platform Admin

| | M30 Platform Administration | M64 Master Data Management |
|---|---|---|
| **Owns** | Technical configuration: users, environments, jobs, feature flags, health, archival | Business master data governance: who may change a part number, a brand, a price book, a branch code — and through what approval |
| **Audience** | IT administrators | Data stewards in each business function |
| **Failure mode** | System does not run | System runs perfectly on wrong data |
| **Analogue** | System administration | SAP *MDG* · Oracle *Product/Customer Hub* · Informatica MDM |

**Rule:** M30 keeps the platform running. M64 keeps the data trustworthy. A branch code
created without approval is an M64 failure, not an M30 one.

---

## 6. Category Boundary Map

| Capability | Owned By | Not Owned By |
|---|---|---|
| API gateway, versioning, rate limits, developer portal | **M28** | Every module publishes through it |
| Event bus, outbox, schema registry, dead letters | **M28** | M63 (consumes events to run workflow) |
| Workflow, approvals, business-rule execution | **M63** (Category J) | M28 |
| External connectors and credentials | **M28** | — |
| Identity, authentication, MFA, SSO, federation | **M29** | Every module and portal delegates |
| Roles, permissions, record rules, field permissions | **M29** | M64 (does not define access) |
| Segregation-of-duties enforcement | **M29** | M60 (defines and tests the rules) |
| Encryption, key management, data classification, audit trail | **M29** | — |
| Master data ownership, stewardship, quality rules | **M64** | M37 (owns catalogue content), M33 (owns party content) |
| Business-rule parameters and thresholds | **M64** stores; **M63** executes | — |
| Organisation structure: entity, branch, zone, cost centre | **M30** | M65 (adds the country dimension) |
| Legal entity, country pack, locale, currency, translation | **M65** | M30 |
| Users, environments, jobs, feature flags, health, archival | **M30** | M66 |
| Internal employee IT support and company IT assets | **M66** | M05, M45 |
| Client-facing managed services | **M05** (Category A) | M66 |
| Project structure, budget, resource plan, milestone billing | **M67** | M01 (service orders), M20 (invoicing) |
| Observability, tracing, alerting on platform health | **M30** with **M28** integration health | M25 |

---

## 7. The Platform Contract

Seven promises this category makes to the other sixty modules. If any is broken, the
architecture degrades.

| # | Promise | Owning Module |
|---|---|---|
| 1 | Every module can publish and consume events reliably, exactly once, in order per aggregate | M28 |
| 2 | Every module can expose a versioned, documented, rate-limited API without building plumbing | M28 |
| 3 | No module implements its own authentication, session handling or permission engine | M29 |
| 4 | Every data change is audited without the module writing audit code | M29 |
| 5 | Every module inherits multi-branch, multi-entity and multi-currency context from the platform | M30, M65 |
| 6 | Business thresholds, approval chains and rule parameters change without a code release | M64, M63 |
| 7 | Every module gets consistent Bengali and English localisation infrastructure | M65 |

---

## 8. Multi-Country Expansion (M65)

The portal roadmap identifies the intended expansion markets through their localised payment
gateways: **India (Razorpay), Myanmar (KBZPay), Nepal (eSewa)**.

A country pack is an installable unit containing everything that varies by jurisdiction:

| Component | Example — Bangladesh Reference Pack |
|---|---|
| Tax rules and rates | VAT 15%, Mushak formats, TDS/VDS categories |
| Statutory reports | Mushak 9.1, TDS challans, income-tax schedules |
| Payroll rules | Tax slabs, provident fund, gratuity, festival bonus |
| Address structure | Division → District → Upazila → Union/Ward |
| Public holidays | Including moon-dependent dates |
| Payment methods | bKash, Nagad, SSLCOMMERZ, BEFTN |
| Language and locale | Bengali primary, lakh/crore number grouping |
| Regulatory obligations | ICT Act, Digital Security Act, Labour Act, e-waste rules |
| Fiscal calendar | July–June |

**Target:** a new country pack authored and live in **≤ 12 weeks**, with zero changes to core
module code. This is the Wave 9 gate criterion.

---

## 9. Category KPIs

| KPI | Baseline | Target | Owning Module |
|---|---|---|---|
| API availability | n/a | > 99.95% | M28 |
| API p95 latency | n/a | < 400 ms | M28 |
| Event delivery success | n/a | > 99.9% | M28 |
| Events unresolved in dead letter > 1 hour | n/a | **Zero** | M28 |
| APIs with a current OpenAPI specification | n/a | 100% | M28 |
| Data divergence incidents (ERP vs portal) | n/a | **Zero** | M28 |
| MFA coverage on privileged accounts | 0% | **100%** | M29 |
| Orphaned accounts after a leaver | unknown | **Zero beyond 24 h** | M29 |
| Access certification completion | n/a | 100% per cycle | M29 |
| Critical vulnerabilities open > 7 days | unknown | **Zero** | M29 |
| Audit coverage of financial transactions | partial | **100%** | M29 |
| Master data changes made through the approved workflow | 0% | 100% | M64 |
| Master data quality score | unmeasured | > 97% | M64 |
| Bengali translation completeness | partial | **100%** | M65 |
| Time to stand up a new branch | weeks | < 1 day | M30 |
| Time to stand up a new legal entity | not possible | < 10 days | M65 |
| Time to stand up a new country pack | not possible | **≤ 12 weeks** | M65 |
| Configuration changes made without a code release | unmeasured | > 95% | M30 / M64 |
| Internal IT tickets resolved within SLA | unmeasured | > 92% | M66 |
| Company IT assets tracked | manual | 100% | M66 |
| Projects delivered on time and on budget | unmeasured | > 80% | M67 |

---

## 10. Category Delivery Sequence

```
W1   M29 Identity & Security ──┐
     M28 Integration Platform ─┤  nothing else can start
     M30 Platform Admin ───────┘
W2   M64 Master Data Management ──► data governance before volume arrives
W6   M66 Internal ITSM ───────────► own IT under control
W7   M67 Project Management ──────► corporate rollouts and branch openings
W9   M65 Multi-Country ───────────► expansion readiness
```

M28, M29 and M30 are the first three modules built. Every subsequent module depends on all
three.

---

## 11. Category Risks

| Risk | Impact | Mitigation | Owning Module |
|---|---|---|---|
| Modules bypass the platform and integrate point-to-point | **Critical** — the architecture becomes a mesh within two years | Architecture standard AS-01 enforced in CI; static analysis blocks direct cross-module table access | M28 |
| Identity or permission defect exposes data across branches or customers | **Critical** — legal and contractual | Negative testing is mandatory for every role; access certification quarterly | M29 |
| Master data governance treated as bureaucracy and bypassed | High — the system runs perfectly on wrong data | Stewardship workflow is the only path to change; direct edits blocked | M64 |
| Multi-country deferred, then retrofitted into a live single-entity system | High — typically 3–5× the cost of designing for it | Entity, country, currency and locale dimensions carried on every record from Wave 1 | M65 |
| Platform team becomes a bottleneck for all 60 other modules | High — delivery stalls | Self-service capability: modules publish APIs and events through a framework, not a ticket | M28 |
| Internal IT support runs on WhatsApp while clients get a portal | Medium — credibility and productivity | M66 delivered in Wave 6; the Company uses its own product | M66 |
| Corporate rollouts run on spreadsheets alongside the ERP | Medium — the exact fragmentation the programme exists to remove | M67 delivered before the marketplace and expansion waves | M67 |

---

*Category K · 1000FiX ERP System v2.0*
