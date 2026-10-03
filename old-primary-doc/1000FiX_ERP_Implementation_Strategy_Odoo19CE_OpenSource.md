# ERP Implementation Strategy & Technology Blueprint

# Odoo 19 Community Edition + Open Source Stack

# For 1000FiX Services Limited

---

| **Document Information** | |
|---|---|
| **Document Title** | ERP Implementation Strategy — Odoo 19 CE + Open Source Technology Stack |
| **Organization** | 1000FiX Services Limited |
| **Document Version** | 1.0 |
| **Date** | March 18, 2026 |
| **Reference Number** | 1000FIX-ERP-STRATEGY-2026-001 |
| **Related Documents** | 1000FIX-ERP-RFP-2026-001, 1000FIX-ERP-BRD-2026-001, 1000FIX-ERP-URD-2026-001 |
| **Classification** | CONFIDENTIAL — Strategic Planning Document |

---

## TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Strategic Approach](#2-strategic-approach)
3. [Odoo 19 CE Foundation Analysis](#3-odoo-19-ce-foundation-analysis)
4. [OCA (Odoo Community Association) Module Layer](#4-oca-odoo-community-association-module-layer)
5. [Free Third-Party Modules](#5-free-third-party-modules)
6. [Complementary Open Source Tools](#6-complementary-open-source-tools)
7. [Requirement-to-Solution Mapping](#7-requirement-to-solution-mapping)
8. [Gap Analysis & Custom Development Scope](#8-gap-analysis--custom-development-scope)
9. [System Architecture Design](#9-system-architecture-design)
10. [Cost Analysis & Budget Projection](#10-cost-analysis--budget-projection)
11. [Implementation Roadmap](#11-implementation-roadmap)
12. [Risk Assessment & Mitigation](#12-risk-assessment--mitigation)
13. [Expert Recommendation & Final Verdict](#13-expert-recommendation--final-verdict)
14. [Appendices](#14-appendices)

---

## 1. EXECUTIVE SUMMARY

### 1.1 Purpose

This document presents a comprehensive technology strategy for implementing 1000FiX's ERP system and Smart Portal Suite using **Odoo 19 Community Edition (CE)** as the zero-license-cost backbone, augmented by OCA (Odoo Community Association) free modules, free third-party marketplace modules, qualified open source tools, and targeted custom development.

The strategy addresses all 190+ functional requirements defined across the RFP (1000FIX-ERP-RFP-2026-001), BRD (1000FIX-ERP-BRD-2026-001), and URD (1000FIX-ERP-URD-2026-001) documents.

### 1.2 Strategic Approach — The 5-Layer Stack

The implementation follows a layered approach, prioritizing solutions with zero licensing cost, maximum reliability, and strong community support:

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 5: CUSTOM DEVELOPMENT                                    │
│  Bangladesh-specific: Mushak VAT, BEFTN payroll, brand warranty │
│  Custom Flutter mobile app, AI dispatch, Bengali NLP chatbot    │
│  Coverage: ~15% of requirements                                 │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 4: OTHER OPEN SOURCE TOOLS (Zero License)               │
│  Metabase (BI) · Traccar (GPS) · n8n (Automation)              │
│  VROOM/OSRM (Route Optimization) · Keycloak (SSO)              │
│  Mayan EDMS (Documents) · Novu (Notifications)                  │
│  Coverage: ~10% of requirements                                 │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 3: FREE THIRD-PARTY MODULES                             │
│  SSLCOMMERZ · bKash · SMS Gateways · WhatsApp Connectors       │
│  Coverage: ~5% of requirements                                  │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2: OCA FREE MODULES (94+ modules)                       │
│  Field Service (33) · Helpdesk (28) · Quality/ISO (33)         │
│  Payroll · Multi-Branch · DMS · BI Reporting                   │
│  Coverage: ~30% of requirements                                 │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 1: ODOO 19 CE (Zero License — LGPL v3)                 │
│  CRM · Sales · Inventory · Accounting · HR · Purchase          │
│  Website/Portal · Project · Manufacturing                       │
│  Coverage: ~40% of requirements                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Coverage Summary

| Solution Layer | Requirements Covered | License Cost | Reliability |
|---|---|---|---|
| Odoo 19 CE (Native) | ~40% | $0 | Very High (Odoo SA maintained) |
| OCA Modules | ~30% | $0 | High (peer-reviewed, CI/CD tested) |
| Free Third-Party Modules | ~5% | $0 | Medium-High (varies by module) |
| Other Open Source Tools | ~10% | $0 | High (established projects) |
| Custom Development | ~15% | Dev cost only | Depends on implementation |
| **TOTAL** | **~100%** | **$0 license** | |

### 1.4 Budget Projection vs RFP Budget

| Category | Odoo CE + Open Source | RFP Budget Range |
|---|---|---|
| Software Licensing | **$0** | $45,000 – $90,000 |
| Implementation & Custom Development | $80,000 – $160,000 | $60,000 – $150,000 |
| Infrastructure / Hosting (3-year) | $15,000 – $36,000 | $20,000 – $50,000 |
| Training | $8,000 – $15,000 | $10,000 – $20,000 |
| Support & Maintenance (3-year) | $20,000 – $45,000 | $15,000 – $40,000 |
| **3-Year TCO** | **$123,000 – $256,000** | **$150,000 – $350,000** |

**Verdict: Within budget.** The zero-license approach saves $45,000–$90,000 which can be redirected to custom development and local support.

### 1.5 Key Findings

1. **Odoo 19 CE is viable as the backbone** — It provides CRM, Sales, Inventory, Accounting, HR (basic), Purchase, and Website/Portal natively
2. **Enterprise-only gaps are bridgeable** — The 10 critical Enterprise-only modules (Field Service, Helpdesk, Planning, Quality, Payroll, Documents, Mobile, Barcode, Studio, BI) all have OCA or open-source alternatives
3. **Bangladesh localization needs custom work** — Mushak 6.3 VAT invoicing, BEFTN payroll, and Bangladesh Labour Act compliance require dedicated development
4. **Mobile app requires custom build** — No adequate open-source technician mobile app exists with offline-first capability; a custom Flutter app is recommended
5. **Local expertise is available** — Metamorphosis Ltd. (Odoo Silver Partner, Bangladesh) and Xsellence Bangladesh Ltd. (Odoo Gold Partner) can provide local implementation support

---

## 2. STRATEGIC APPROACH

### 2.1 Why Odoo 19 CE as the Foundation

| Decision Factor | Assessment | Score |
|---|---|---|
| **License Cost** | LGPL v3, completely free, no per-user fees | 10/10 |
| **Functional Breadth** | 30+ modules in CE covering core ERP functions | 8/10 |
| **Technical Architecture** | PostgreSQL 16, Python 3.12, modern OWL frontend, JSON-2 API | 9/10 |
| **Customizability** | Python/XML/OWL, modular architecture, full source access | 10/10 |
| **Community Size** | Largest open-source ERP community globally (10M+ users) | 9/10 |
| **Ecosystem** | 40,000+ apps on marketplace, 250+ OCA repositories | 9/10 |
| **Integration Capability** | REST API, JSON-RPC, webhooks, PostgreSQL shared access | 8/10 |
| **Scalability** | Proven at 5,000+ internal users with proper architecture | 7/10 |
| **Bangladesh Presence** | 2 official partners (Metamorphosis, Xsellence), l10n_bd module | 7/10 |
| **Long-term Viability** | Odoo SA valued at $3.7B+, annual releases since 2005 | 10/10 |

### 2.2 The Selection Hierarchy

For every requirement in the RFP/BRD/URD, the following evaluation hierarchy is applied:

```
1. Does Odoo 19 CE handle this natively?
   → YES: Use standard Odoo CE module (Layer 1)
   → NO: Continue to step 2

2. Does an OCA module exist for this?
   → YES: Evaluate quality (stars, recent commits, CI status)
     → Quality OK: Use OCA module (Layer 2)
     → Quality insufficient: Continue to step 3
   → NO: Continue to step 3

3. Is there a free third-party module on apps.odoo.com or GitHub?
   → YES: Evaluate reliability (downloads, reviews, maintainer)
     → Reliable: Use third-party module (Layer 3)
     → Risky: Continue to step 4
   → NO: Continue to step 4

4. Is there a standalone open-source tool that integrates with Odoo?
   → YES: Evaluate integration feasibility and tool maturity
     → Feasible: Deploy and integrate (Layer 4)
     → Not feasible: Continue to step 5
   → NO: Continue to step 5

5. Custom development required (Layer 5)
   → Estimate scope, cost, and timeline
   → Prioritize P1 requirements first
```

### 2.3 Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|---|---|---|---|
| **Odoo Enterprise** | Complete solution, official support, native mobile | $31.10/user/month = $186,600–$335,880/yr for 500-900 users; exceeds entire budget | Rejected (cost) |
| **ERPNext (Frappe)** | Free, Python/JS, good for services | Smaller ecosystem, fewer modules, limited FSM | Viable alternative, but Odoo ecosystem is richer |
| **Dolibarr** | Lightweight, PHP, free | Too simple for 51+ branches, limited FSM | Rejected (scale) |
| **iDempiere** | Enterprise-grade, Java, free | Complex, small community, no FSM focus | Rejected (complexity) |
| **Custom from scratch** | Perfect fit | Cost $500K+, 3+ years, high risk | Rejected (cost/time) |
| **Hybrid: Odoo CE + ERPNext** | Best of both | Integration complexity, two learning curves | Not recommended |

**Verdict: Odoo 19 CE is the optimal foundation** given the combination of zero licensing, broad functionality, massive ecosystem, Bangladesh local partners, and PostgreSQL compatibility with the existing Next.js platform stack.

---

## 3. ODOO 19 CE FOUNDATION ANALYSIS

### 3.1 Release Status

| Attribute | Detail |
|---|---|
| **Version** | Odoo 19.0 (released October 2025), patch 19.1 (January 2026) |
| **License** | LGPL v3 (fully open source) |
| **Source Code** | github.com/odoo/odoo (branch 19.0) |
| **Database** | PostgreSQL 15+ (recommended: PostgreSQL 16) |
| **Server** | Python 3.11+ (recommended: 3.12) |
| **Frontend** | OWL (Odoo Web Library) — TypeScript-based, component-driven |
| **API** | JSON-2 API (new in v19), XML-RPC, JSON-RPC (deprecated, removal planned v22) |
| **PWA Support** | Yes (v19 improvements: pull-to-refresh, compact status bars, bottom sheet menus) |

### 3.2 Modules Available in CE (Free)

| Module | CE Capabilities for 1000FiX | Limitations vs Enterprise |
|---|---|---|
| **CRM** | Full pipeline, leads, activities, customer 360 view, communication tracking | No AI lead scoring, no predictive analytics |
| **Sales** | Quotations, sales orders, invoicing, price lists, discounts | No subscriptions, no Amazon connector |
| **Inventory** | Multi-warehouse, stock moves, internal transfers, reorder rules, stock valuation (FIFO/weighted avg) | No barcode app, no warehouse routing, no batch picking, no carrier integrations |
| **Accounting** | Chart of accounts, journal entries, invoicing, tax management, bank reconciliation (manual), financial reports (P&L, Balance Sheet) | No OCR vendor bills, no live bank sync, no automated reconciliation, no deferred revenue, no consolidation |
| **HR (Employees)** | Employee records, org hierarchy, departments, skills | No recruitment, no appraisal, no advanced attendance |
| **Attendance** | Basic check-in/out tracking | No advanced rules, no kiosk mode |
| **Leave Management** | Leave types, requests, approvals, balance tracking | Basic functionality, sufficient for needs |
| **Purchase** | RFQs, purchase orders, supplier management, 3-way matching | No advanced procurement dashboard |
| **Project** | Tasks, Kanban boards, basic tracking | No Gantt charts, no advanced planning |
| **Website** | Website builder, portal, eCommerce | No advanced SEO, no A/B testing |
| **Discuss** | Internal messaging, channels, mail integration | Sufficient for internal comms |
| **Contacts** | Contact management, companies, addresses | Full functionality |
| **Calendar** | Event management, scheduling | Basic scheduling |
| **Fleet** | Vehicle management | Basic fleet tracking |

### 3.3 Modules Enterprise-Only (NOT in CE)

These represent the critical gaps that must be filled by OCA modules, open-source tools, or custom development:

| Enterprise Module | Relevance to 1000FiX | Gap Severity | Proposed Alternative |
|---|---|---|---|
| **Field Service** | Core business — technician dispatch, GPS, mobile app | **CRITICAL** | OCA/field-service (33 modules) + Custom Flutter app |
| **Helpdesk** | SLA tracking, ticket management, escalation | **CRITICAL** | OCA/helpdesk (28 modules) |
| **Planning** | Technician scheduling, shift management | **HIGH** | OCA/field-service scheduling + VROOM/OSRM |
| **Quality Management** | ISO 9001:2015, QC checklists, CAPA | **HIGH** | OCA/management-system (33 modules) |
| **Payroll** | Salary processing, deductions, bank files | **HIGH** | OCA/payroll + Custom BD payroll module |
| **Documents** | Centralized DMS, workflows | **MEDIUM** | OCA/dms + Mayan EDMS |
| **Native Mobile Apps** | iOS/Android for technicians | **HIGH** | Custom Flutter app (offline-first) |
| **Barcode** | Inventory scanning, mobile barcode | **MEDIUM** | OCA stock_barcodes + mobile camera API |
| **Studio** | Low-code customization | **LOW** | Direct Python/XML customization |
| **Spreadsheet/BI** | Advanced analytics, dashboards | **HIGH** | Metabase + Grafana |
| **Sign** | Electronic signatures | **MEDIUM** | OCA/web module + custom e-signature |
| **Marketing Automation** | Campaign automation | **LOW** | n8n workflows |
| **VoIP** | Telephony integration | **LOW** | Future phase |

### 3.4 Bangladesh Localization (l10n_bd)

| Feature | Status | Notes |
|---|---|---|
| Chart of Accounts | Available | Pre-configured Bangladesh chart of accounts |
| VAT (15%) | Available | Standard 15% VAT rate configured |
| Currency (BDT ৳) | Available | Bangladeshi Taka as primary currency |
| Bengali Language | Available | Community-maintained translations |
| Mushak 6.3 Invoice | **NOT available** | Requires custom development |
| e-VAT Filing | **NOT available** | Requires custom development |
| Income Tax Slabs | **NOT available** | Requires custom payroll development |
| BEFTN File Generation | **NOT available** | Requires custom development |
| NID Validation | **NOT available** | Requires custom development |
| Bangladesh Address Format | **Partial** | Divisions/districts need custom fields |

### 3.5 Scalability Assessment

| Scenario | Feasibility | Requirements |
|---|---|---|
| **500+ concurrent internal users** | Achievable | 20-25 Odoo workers, load balancer, dedicated PostgreSQL with read replicas |
| **250,000+ monthly portal users** | Achievable with architecture | Dedicated portal server instances, PgBouncer connection pooling, Varnish/Nginx caching, CDN |
| **51+ service center branches** | Achievable | Multi-company or operating unit configuration, branch-level access control |
| **500,000+ service order records** | Achievable | PostgreSQL partitioning, archival strategy, separate reporting database |
| **Real-time dashboards** | Achievable | Metabase/Grafana reading from PostgreSQL, materialized views |

**Recommended Infrastructure for Target Scale:**

```
┌─ Load Balancer (Nginx) ─────────────────────────────────┐
│                                                           │
├─ Odoo App Server 1 (8 vCPU, 16GB RAM) ─ 8 workers      │
├─ Odoo App Server 2 (8 vCPU, 16GB RAM) ─ 8 workers      │
├─ Odoo Portal Server (4 vCPU, 8GB RAM) ─ dedicated       │
│                                                           │
├─ PostgreSQL Primary (8 vCPU, 32GB RAM, SSD)             │
├─ PostgreSQL Read Replica (for reporting/BI)              │
├─ PgBouncer (connection pooling)                          │
│                                                           │
├─ Redis (session cache, queue)                            │
├─ Metabase (BI, connected to read replica)                │
├─ Traccar (GPS server)                                    │
├─ n8n (workflow automation)                               │
├─ Keycloak (SSO)                                          │
├─ Mayan EDMS (document management)                        │
└─ VROOM/OSRM (route optimization)                        │
```

---

## 4. OCA (ODOO COMMUNITY ASSOCIATION) MODULE LAYER

### 4.1 About OCA

The **Odoo Community Association (OCA)** is a non-profit organization established in 2013, maintaining 1,000+ free open-source modules across 250+ GitHub repositories. OCA modules undergo:

- Mandatory peer code review before merge
- Automated CI/CD testing on every pull request
- Strict coding guidelines adherence
- Regular version migration (each Odoo major release)
- Active community maintenance (contributors in 50+ countries)

Odoo SA itself endorsed OCA's security and reliability at Odoo Experience 2025.

**Reliability Rating: HIGH** — OCA modules are production-grade and widely deployed globally.

### 4.2 Critical OCA Repositories for 1000FiX

#### 4.2.1 OCA/field-service — 33 Modules

**Repository:** github.com/OCA/field-service
**Status:** Actively maintained, v19 branch available
**Relevance:** CRITICAL — This is the cornerstone replacing the Enterprise Field Service module

| Module | Function | 1000FiX Requirement Coverage |
|---|---|---|
| `fieldservice` | Core FSM: work orders, locations, workers, scheduling | FSM-001 to FSM-012 (dispatch, scheduling) |
| `fieldservice_repair` | Integration with Odoo Repair module | SRM-021 to SRM-030 (repair workflows) |
| `fieldservice_equipment` | Equipment/device tracking | CRM-002 (device registry) |
| `fieldservice_equipment_warranty` | Warranty tracking on equipment | CWM-009 to CWM-017 (warranty management) |
| `fieldservice_route` | Route planning and optimization | FSM-004 (route optimization base) |
| `fieldservice_skill` | Technician skill/certification management | FSM-005, HRM-006 (skill-based assignment) |
| `fieldservice_agreement` | Service agreements (AMC/RAMC) | CWM-001 to CWM-008 (contract management) |
| `fieldservice_portal` | Customer portal for field service | CSP-001 to CSP-017 (customer self-service) |
| `fieldservice_stock` | Inventory integration for parts | INV-011, FSM-021 (parts consumption) |
| `fieldservice_vehicle` | Vehicle/van management | INV-003 (van stock management) |
| `fieldservice_recurring` | Recurring service orders (AMC visits) | CWM-005 (scheduled maintenance) |
| `fieldservice_substatus` | Custom sub-statuses for workflow | SRM-011 (configurable statuses) |
| `fieldservice_partner_multi_relation` | Multi-contact management | CRM-015 (corporate multi-contact) |
| `fieldservice_timeline` | Visual timeline for scheduling | FSM-002 (dispatch board) |
| `fieldservice_calendar` | Calendar integration | FSM-002 (calendar view) |
| `fieldservice_activity` | Activity tracking on FSM orders | SRM-012 (internal notes) |
| `fieldservice_stage_validation` | Stage-based validation rules | SRM-020 (approval workflows) |
| `fieldservice_isp` | ISP/telecom field service | Not directly needed |
| `fieldservice_geoengine` | GIS/geographic integration | FSM-008 (geo-fencing) |
| `fieldservice_size` | Size-based planning | Not directly needed |
| `fieldservice_distribution` | Distribution/delivery management | FSM-029 (pick & drop service) |
| `fieldservice_crm` | CRM integration for FSM leads | CRM-014 (lead capture) |
| `fieldservice_sale` | Sales order integration | CRM-017 (quotation generation) |
| `fieldservice_purchase` | Purchase integration for parts | SCM-006 to SCM-012 (purchase management) |
| `fieldservice_account` | Accounting integration | FIN-010, FIN-011 (invoicing) |
| `fieldservice_project` | Project management integration | General project tracking |
| `fieldservice_fleet` | Fleet management integration | Vehicle tracking |
| `fieldservice_google_map` | Google Maps integration | FSM-016 (GPS navigation) |
| `fieldservice_google_marker_icon_picker` | Map markers customization | Visual dispatch enhancement |
| `fieldservice_change_management` | Change order tracking | SRM-018, SRM-019 (order splitting/merging) |
| `fieldservice_quality_control` | Quality checks on field orders | QMS-006 (service quality scoring) |
| `fieldservice_template` | Service order templates | SRM-016 (service order templates) |
| `fieldservice_maintenance` | Maintenance schedule management | CWM-005 (preventive maintenance) |

#### 4.2.2 OCA/helpdesk — 28 Modules

**Repository:** github.com/OCA/helpdesk
**Status:** Actively maintained
**Relevance:** HIGH — Replaces Enterprise Helpdesk module

| Key Module | Function | Requirement Coverage |
|---|---|---|
| `helpdesk_mgmt` | Core helpdesk: tickets, categories, stages | SRM-001 to SRM-020 (service order management) |
| `helpdesk_mgmt_sla` | SLA tracking and enforcement | CWM-018 to CWM-022 (SLA management) |
| `helpdesk_mgmt_fieldservice` | Integration with OCA field service | FSM integration |
| `helpdesk_mgmt_rating` | Customer satisfaction ratings | CRM-006 (CSAT surveys) |
| `helpdesk_mgmt_timesheet` | Time tracking on tickets | SRM-025 (labor time tracking) |
| `helpdesk_mgmt_project` | Project integration | Project tracking |
| `helpdesk_mgmt_priority` | Priority management | SRM-015 (prioritization rules) |

#### 4.2.3 OCA/management-system — 33 Modules

**Repository:** github.com/OCA/management-system
**Status:** Actively maintained
**Relevance:** HIGH — Covers Quality Management and ISO 9001:2015 compliance

| Key Module | Function | Requirement Coverage |
|---|---|---|
| `mgmtsystem` | Core management system | QMS-001 (ISO compliance framework) |
| `mgmtsystem_quality` | Quality management | QMS-001 to QMS-008 |
| `mgmtsystem_audit` | Internal audit management | QMS-002 (audit management) |
| `mgmtsystem_nonconformity` | Non-conformance tracking (NCR) | QMS-003 (NCR management) |
| `mgmtsystem_action` | Corrective/preventive actions (CAPA) | QMS-004 (CAPA tracking) |
| `mgmtsystem_review` | Management reviews | ISO review process |
| `mgmtsystem_hazard` | Hazard identification | Safety compliance |
| `mgmtsystem_nonconformity_repair` | NCR integration with repair | Repair quality tracking |

#### 4.2.4 OCA/hr & OCA/payroll — Employee & Payroll Management

**Repository:** github.com/OCA/hr, github.com/OCA/payroll
**Relevance:** HIGH

| Key Module | Function | Requirement Coverage |
|---|---|---|
| `hr_employee_skill` | Employee skill management | HRM-006 (technician skill matrix) |
| `hr_attendance_geolocation` | GPS-based attendance | HRM-013 (GPS clock-in) |
| `hr_contract_type` | Contract type management | HRM-002 (employee lifecycle) |
| `hr_holidays_public` | Public holiday management | HRM-015 (Bangladesh holidays) |
| `hr_payroll_community` | Basic payroll processing | HRM-017 to HRM-023 (base payroll) |
| `hr_expense` | Expense management | FSM-025 (expense reporting) |

**Note:** Bangladesh-specific payroll rules (tax slabs, BEFTN, provident fund) require custom development on top of OCA payroll.

#### 4.2.5 OCA/operating-unit — Multi-Branch Management

**Repository:** github.com/OCA/operating-unit
**Relevance:** HIGH

| Key Module | Function | Requirement Coverage |
|---|---|---|
| `operating_unit` | Core operating unit (branch) management | Multi-branch support for 51+ centers |
| `account_operating_unit` | Branch-wise accounting | FIN-001, FIN-002 (multi-branch accounting) |
| `stock_operating_unit` | Branch-wise inventory | INV-001 (multi-warehouse management) |
| `sale_operating_unit` | Branch-wise sales | Branch revenue tracking |
| `purchase_operating_unit` | Branch-wise procurement | Branch-level purchasing |
| `hr_operating_unit` | Branch-wise HR | Branch employee management |

#### 4.2.6 OCA/reporting-engine & OCA/mis-builder — BI & Reporting

| Key Module | Function | Requirement Coverage |
|---|---|---|
| `mis_builder` | KPI/MIS report builder | BI-001 to BI-014 (base reporting) |
| `mis_builder_budget` | Budget management | FIN-033 (budget vs actual) |
| `bi_view_editor` | BI view creation | BI-009 (custom report builder) |
| `bi_sql_editor` | SQL-based custom reports | BI-012 (ad-hoc queries) |
| `report_xlsx` | Excel report generation | BI-011 (Excel export) |
| `report_qweb_pdf` | PDF report generation | BI-011 (PDF export) |

#### 4.2.7 OCA/dms — Document Management System

| Key Module | Function | Requirement Coverage |
|---|---|---|
| `dms` | Core DMS with categories, tags, versions | DMS-001, DMS-002 |
| `dms_field` | Document fields on records | DMS-006 (document templates) |
| `dms_auto_classification` | Auto-categorization | DMS-002 (categorization) |

### 4.3 OCA Module Quality Assessment

| Criterion | Assessment |
|---|---|
| **Code Review** | All modules undergo mandatory peer review |
| **CI/CD Testing** | Automated tests on every PR (GitHub Actions) |
| **Version Compatibility** | Migrated to v19 within 3-6 months of release |
| **Documentation** | README in each module; varies in depth |
| **Community Support** | GitHub issues, Odoo forums, OCA mailing lists |
| **Production Usage** | Widely deployed by Odoo integrators globally |
| **Risk** | Lower risk than individual third-party modules; higher than Odoo SA modules |

---

## 5. FREE THIRD-PARTY MODULES

### 5.1 Payment Gateway Integration

| Module | Source | License | Status | Requirement |
|---|---|---|---|---|
| **SSLCOMMERZ for Odoo** | github.com/sslcommerz/SSLCommerz-Odoo | Open Source | Official SSLCOMMERZ module | INT-009 (SSLCOMMERZ integration) |
| **bKash Payment Module** | apps.odoo.com (Metamorphosis) | Free/Community | Maintained by BD partner | INT-007 (bKash integration) |
| **Nagad** | Via SSLCOMMERZ aggregation | — | Nagad accessible through SSLCOMMERZ | INT-008 (Nagad integration) |
| **Rocket (DBBL)** | Via SSLCOMMERZ aggregation | — | Available through SSLCOMMERZ | INT-010 (Rocket integration) |

### 5.2 Communication Integration

| Module | Source | License | Status | Requirement |
|---|---|---|---|---|
| **Bangladesh SMS Gateway** | Metamorphosis (MuthoSMS, GreenWeb) | Free/Community | BD-specific SMS providers | INT-013 (SMS gateway) |
| **WhatsApp Connector** | github.com/chatwithio/odoo-whatsapp-api | Open Source | Community-maintained | INT-015 (WhatsApp integration) |
| **Email Integration** | Odoo CE built-in mail module | Built-in | Fully functional | INT-014 (email integration) |

### 5.3 GPS & Location

| Module | Source | License | Status | Requirement |
|---|---|---|---|---|
| **Traccar GPS Integration** | Community connectors | Open Source | Traccar server + Odoo bridge | FSM-003 (GPS tracking) |
| **fieldservice_google_map (OCA)** | OCA/field-service | AGPL-3 | Actively maintained | INT-018 (Google Maps integration) |

### 5.4 Barcode & Scanning

| Module | Source | License | Status | Requirement |
|---|---|---|---|---|
| **stock_barcodes (OCA)** | OCA/stock-logistics-barcode | AGPL-3 | Active | INV-005 (barcode support) |
| **Mobile camera barcode** | Custom web component | Custom | HTML5 camera API | FSM-021 (mobile barcode) |

### 5.5 Reliability Assessment

| Risk Level | Modules | Mitigation |
|---|---|---|
| **Low Risk** | SSLCOMMERZ (official), OCA modules | Well-maintained, large user base |
| **Medium Risk** | bKash module, WhatsApp connector | Test thoroughly; maintain fork if needed |
| **Higher Risk** | Individual GitHub modules | Code review before adoption; maintain internal fork |

---

## 6. COMPLEMENTARY OPEN SOURCE TOOLS

### 6.1 Metabase — Business Intelligence & Analytics

| Attribute | Detail |
|---|---|
| **What** | Open source BI and analytics platform |
| **License** | AGPL v3 (free, self-hosted) |
| **Why for 1000FiX** | Connects directly to Odoo's PostgreSQL; drag-and-drop dashboards; embeddable in Odoo/Next.js; non-technical users can build reports |
| **Key Features** | Interactive dashboards, drill-down, scheduled reports, email distribution, custom SQL queries, dashboard embedding (iframe/JWT) |
| **Requirements Covered** | BI-001 to BI-014, ABD-001 to ABD-010 |
| **Integration** | Direct PostgreSQL connection to Odoo database (read replica recommended) |
| **Maturity** | 10+ years, 40K+ GitHub stars, enterprise-ready |

**Metabase Dashboards for 1000FiX:**
- Executive Dashboard (CEO): Revenue, jobs, CSAT, technician utilization
- Branch Performance Dashboard: Comparison across 51+ centers
- Technician Scorecard: Jobs/day, FTFR, ratings, earnings
- Financial Dashboard: Revenue, P&L, warranty claims, cash flow
- Inventory Dashboard: Stock levels, turnover, stockouts
- Customer Analytics: Acquisition, retention, lifetime value
- SLA Compliance Dashboard: Breach rates, escalation trends

### 6.2 Grafana — Operational Real-Time Monitoring

| Attribute | Detail |
|---|---|
| **What** | Real-time monitoring and alerting platform |
| **License** | AGPL v3 (free, self-hosted) |
| **Why** | Real-time operational dashboards with auto-refresh (every 30 seconds); alerting for SLA breaches; infrastructure monitoring |
| **Requirements Covered** | ABD-002 (real-time metrics), ABD-010 (threshold alerts) |
| **Integration** | PostgreSQL data source + Prometheus for system metrics |

### 6.3 Custom Flutter Mobile App — Technician Portal

| Attribute | Detail |
|---|---|
| **What** | Custom-built cross-platform mobile app for field technicians |
| **Technology** | Flutter (Dart) — compiles to native iOS and Android |
| **Why Custom** | No adequate open-source technician mobile app exists with offline-first capability, Bengali language, and Odoo integration |

**Key Features to Build:**
| Feature | Priority | Effort |
|---|---|---|
| Daily job queue with priority sorting | P1 | Medium |
| GPS navigation (Google Maps integration) | P1 | Medium |
| Offline-first architecture (SQLite/Hive local DB) | P1 | High |
| Auto-sync on reconnect | P1 | High |
| Digital service forms with pre-populated data | P1 | Medium |
| Before/after photo capture with GPS/timestamp | P1 | Medium |
| Barcode/QR scanning (camera API) | P1 | Low |
| Customer e-signature capture | P1 | Medium |
| Parts consumption recording | P1 | Medium |
| Time tracking (auto-capture) | P1 | Low |
| Push notifications (Firebase) | P1 | Low |
| Bengali language support | P1 | Medium |
| Guided diagnostic checklists | P1 | Medium |
| In-app messaging (dispatch/customer) | P2 | Medium |
| Earnings dashboard | P2 | Low |
| Knowledge base access | P2 | Medium |
| Leave request submission | P2 | Low |
| Voice-to-text (Bengali) | P2 | High |

**Estimated Development Effort:** 3-4 months with 2 Flutter developers

**Integration Pattern:**
```
Flutter App ←→ Odoo JSON-2 API ←→ Odoo 19 CE Backend
     ↕                                    ↕
SQLite/Hive (offline)              PostgreSQL
     ↕
Background Sync Service
```

### 6.4 Traccar — GPS Tracking Server

| Attribute | Detail |
|---|---|
| **What** | Open source GPS tracking platform |
| **License** | Apache 2.0 (free) |
| **Why** | Supports 200+ GPS protocols; web-based tracking interface; real-time fleet monitoring; geofencing; event alerts |
| **Requirements Covered** | FSM-003 (GPS tracking), FSM-008 (geo-fencing), FSM-027 (customer tracking), INT-018 (mapping) |
| **Integration** | REST API to Odoo; GPS data from technician phones via Traccar Client app; real-time WebSocket for live map |
| **Maturity** | 12+ years, 5K+ GitHub stars, enterprise-deployed globally |

### 6.5 Mayan EDMS — Document Management System

| Attribute | Detail |
|---|---|
| **What** | Enterprise document management system |
| **License** | Apache 2.0 (free) |
| **Why** | Python/Django stack (aligns with Odoo); PostgreSQL native; REST API; built-in OCR (Tesseract, supports Bengali); workflow engine; version control |
| **Requirements Covered** | DMS-001 to DMS-008 |
| **Integration** | REST API to/from Odoo; shared PostgreSQL possible; document links in Odoo records |
| **Maturity** | v4.10 (October 2025), actively maintained |

**Note:** OCA/dms covers basic document management within Odoo. Mayan EDMS is recommended as a complement for advanced features (OCR, complex workflows, large document archives). For Phase 1, OCA/dms may be sufficient.

### 6.6 n8n — Workflow Automation & Notification Orchestration

| Attribute | Detail |
|---|---|
| **What** | Open source workflow automation platform (alternative to Zapier) |
| **License** | Sustainable Use License (free for self-hosted) |
| **Why** | Native Odoo integration node; 1000+ connectors; visual workflow builder; handles all notification routing (SMS, WhatsApp, email, push) |
| **Requirements Covered** | All notification requirements (14.1-14.4 from URD), INT-013 to INT-016 (communication integrations) |
| **Key Workflows** |
| | Service order status change → SMS + WhatsApp + Push notification |
| | SLA breach approaching → Alert dispatch manager + escalation |
| | Invoice generated → Send via email + WhatsApp with payment link |
| | Warranty claim ready → Submit to brand partner portal |
| | Stock below reorder → Alert inventory manager + auto-create PR |
| | AMC expiring → Customer renewal reminder sequence |
| | Payroll approved → Generate BEFTN file |

### 6.7 VROOM + OSRM — Route Optimization

| Attribute | Detail |
|---|---|
| **VROOM** | Vehicle Routing Open-source Optimization Machine |
| **OSRM** | Open Source Routing Machine (road distance calculations) |
| **License** | BSD-2-Clause (VROOM), BSD-2-Clause (OSRM) |
| **Why** | VROOM solves VRP (Vehicle Routing Problems) in milliseconds; OSRM provides Bangladesh road network routing using OpenStreetMap data |
| **Requirements Covered** | FSM-004 (route optimization), FSM-010 (travel time estimation), INT-019 (route optimization engine) |
| **Integration** | HTTP API; Python wrapper (pyvroom); scheduled optimization runs from Odoo via n8n |
| **Alternative** | Google Routes API (paid, but more accurate traffic data for Dhaka) |

**Recommendation:** Use VROOM/OSRM as primary (zero cost); supplement with Google Routes API for Dhaka metro area where traffic data is critical. Budget $200-400/month for Google Routes API usage.

### 6.8 Keycloak — Identity & SSO Management

| Attribute | Detail |
|---|---|
| **What** | Enterprise identity and access management |
| **License** | Apache 2.0 (CNCF project) |
| **Why** | Centralizes authentication across Odoo, Next.js portal, Metabase, Grafana, Mayan EDMS, n8n; SAML 2.0, OAuth 2.0, OpenID Connect |
| **Requirements Covered** | SEC-001 to SEC-007 (authentication, RBAC, MFA, SSO), INT-006 (shared SSO) |
| **Integration** | OCA `auth_keycloak` module for Odoo; NextAuth.js OIDC provider for Next.js; native support in Metabase, Grafana |
| **Maturity** | 10+ years, CNCF project, 25K+ GitHub stars |

### 6.9 Novu — Multi-Channel Notification Infrastructure

| Attribute | Detail |
|---|---|
| **What** | Open source notification infrastructure |
| **License** | MIT (free) |
| **Why** | Unified API for email, SMS, push, WhatsApp; template management; preference center; delivery tracking |
| **Requirements Covered** | All notification requirements from URD Section 14 |
| **Integration** | REST API; n8n triggers Novu for actual delivery |
| **Alternative** | ntfy (simpler, HTTP-based push only) for lighter deployment |

### 6.10 Bengali NLP Chatbot — LLM-Based Approach

| Attribute | Detail |
|---|---|
| **What** | AI-powered customer support chatbot with Bengali language capability |
| **Technology** | Ollama (local LLM server) + Qwen3-8B or TigerLLM (Bengali-capable) + LangChain (orchestration) |
| **Why** | Rasa OSS has entered maintenance mode (risky long-term); LLM-based approach is more capable, handles Bengali natively, and provides tool-use for Odoo API interaction |
| **Requirements Covered** | INT-022 (AI chatbot with Bengali NLP), CSP-013 (live chat) |
| **Integration** | WhatsApp Cloud API → LangChain → Odoo JSON-2 API (for booking, status queries) |
| **Risk** | Higher complexity; recommend as Phase 6 deployment |

### 6.11 Complete Open Source Tool Stack Summary

| Tool | Purpose | License | Maturity | Integration Effort |
|---|---|---|---|---|
| Metabase | BI/Analytics | AGPL-3 | Very High | Low (PostgreSQL direct) |
| Grafana | Real-time monitoring | AGPL-3 | Very High | Low (PostgreSQL + Prometheus) |
| Flutter App | Technician mobile | Custom | N/A (custom build) | High (3-4 months) |
| Traccar | GPS tracking | Apache-2.0 | Very High | Medium (REST API) |
| Mayan EDMS | Document management | Apache-2.0 | High | Medium (REST API) |
| n8n | Workflow automation | Fair-code | Very High | Medium (native Odoo node) |
| VROOM + OSRM | Route optimization | BSD-2 | High | Medium (HTTP API) |
| Keycloak | SSO/Identity | Apache-2.0 | Very High | Medium (OCA auth module) |
| Novu | Notifications | MIT | High | Medium (REST API) |
| Ollama + LLM | Bengali chatbot | MIT | Medium | High (custom integration) |

---

## 7. REQUIREMENT-TO-SOLUTION MAPPING

### 7.1 Mapping Legend

| Code | Meaning |
|---|---|
| **L1** | Odoo 19 CE native (Layer 1) |
| **L2** | OCA module (Layer 2) |
| **L3** | Free third-party module (Layer 3) |
| **L4** | Other open source tool (Layer 4) |
| **L5** | Custom development (Layer 5) |
| **C** | Configuration only (no code) |
| **D** | Development required |

### 7.2 Service & Repair Management (SRM) — 37 Requirements

| Req # | Requirement | Priority | Solution | Layer | Notes |
|---|---|---|---|---|---|
| SRM-001 | Multi-channel service order creation | P1 | OCA helpdesk_mgmt + L5 WhatsApp/chatbot integration | L2+L5 | WhatsApp/chatbot intake needs custom work |
| SRM-002 | Service order classification (Warranty, OOW, AMC, Emergency, PM) | P1 | OCA helpdesk categories + fieldservice | L2 | Configuration |
| SRM-003 | Full service order lifecycle | P1 | OCA helpdesk_mgmt + fieldservice stages | L2 | Configure stages to match workflow |
| SRM-004 | Auto-assign unique service order number (branch-configurable) | P1 | Odoo CE sequence module + L5 branch prefix | L1+L5 | Minor customization for branch prefix |
| SRM-005 | Link service orders to customer devices (serial tracking) | P1 | Odoo CE product + OCA fieldservice_equipment | L1+L2 | Serial number tracking native in Odoo |
| SRM-006 | Capture device info (brand, model, serial, warranty) | P1 | OCA fieldservice_equipment | L2 | Configuration |
| SRM-007 | Complete service history per device | P1 | OCA fieldservice_equipment + helpdesk | L2 | Linked via serial number |
| SRM-008 | Multiple service items per order | P1 | Odoo CE + OCA helpdesk | L1+L2 | Multi-line support |
| SRM-009 | SLA timelines per service type, brand, customer tier | P1 | OCA helpdesk_mgmt_sla | L2 | SLA configuration |
| SRM-010 | SLA breach alerts with escalation | P1 | OCA helpdesk_mgmt_sla + n8n | L2+L4 | n8n handles multi-channel alerts |
| SRM-011 | Configurable statuses and sub-statuses | P2 | OCA fieldservice_substatus | L2 | Configuration |
| SRM-012 | Internal notes and communication thread | P1 | Odoo CE mail/chatter | L1 | Built-in on all records |
| SRM-013 | Photo/video attachment capability | P1 | Odoo CE attachments + Flutter app | L1+L5 | Mobile photo capture in custom app |
| SRM-014 | Automatic customer notifications at status change | P1 | n8n + Novu | L4 | Webhook from Odoo triggers n8n workflow |
| SRM-015 | Service order prioritization rules | P2 | OCA helpdesk_mgmt_priority | L2 | Configuration |
| SRM-016 | Service order templates | P2 | OCA fieldservice_template | L2 | Template configuration |
| SRM-017 | Duplicate service order detection | P2 | L5 custom module | L5 | Custom logic for duplicate detection |
| SRM-018 | Service order splitting | P3 | OCA fieldservice_change_management | L2 | Available in OCA |
| SRM-019 | Service order merging | P3 | L5 custom module | L5 | Custom development |
| SRM-020 | Configurable approval workflows | P1 | OCA fieldservice_stage_validation | L2 | Stage-based validation |
| SRM-021 | Multi-level repair classification (L1/L2/L3) | P1 | OCA fieldservice + custom tags | L2+L5 | Custom repair level field |
| SRM-022 | Diagnostic checklist templates | P1 | L5 custom checklist module | L5 | Custom development |
| SRM-023 | Repair cost estimation with approval | P1 | OCA fieldservice + Odoo CE quotations | L1+L2 | Sales quotation integration |
| SRM-024 | Parts requisition linked to inventory | P1 | OCA fieldservice_stock | L2 | Direct inventory link |
| SRM-025 | Labor time tracking | P1 | OCA helpdesk_mgmt_timesheet | L2 | Timesheet integration |
| SRM-026 | Quality inspection checklist | P1 | OCA mgmtsystem_quality + fieldservice_quality_control | L2 | Quality checks |
| SRM-027 | Post-repair testing workflow | P2 | OCA fieldservice_stage_validation | L2 | Stage-based |
| SRM-028 | Warranty claim generation | P1 | L5 custom warranty claim module | L5 | Brand-specific claim formats |
| SRM-029 | Rework tracking | P1 | L5 custom rework detection | L5 | Custom logic |
| SRM-030 | Root cause analysis categorization | P2 | OCA mgmtsystem_nonconformity | L2 | NCR categorization |
| SRM-031 | Configurable service price list | P1 | Odoo CE pricelists | L1 | Native pricelist feature |
| SRM-032 | Warranty vs OOW pricing | P1 | Odoo CE pricelists | L1 | Multiple pricelists |
| SRM-033 | Dynamic cost estimation | P1 | Odoo CE + OCA fieldservice | L1+L2 | Labor + parts + transport |
| SRM-034 | Customer quotation with approval | P1 | Odoo CE sales quotation | L1 | Native quotation workflow |
| SRM-035 | Discount management | P1 | Odoo CE pricelists + discounts | L1 | Native discount features |
| SRM-036 | NTE limits for B2B accounts | P2 | L5 custom approval rules | L5 | Custom development |
| SRM-037 | Price revision history | P2 | Odoo CE pricelist versioning | L1 | Configuration |

**SRM Coverage: L1=30%, L2=43%, L4=5%, L5=22%**

### 7.3 Field Service Management (FSM) — 31 Requirements

| Req # | Requirement | Priority | Solution | Layer |
|---|---|---|---|---|
| FSM-001 | AI-powered smart scheduling | P1 | VROOM/OSRM + L5 dispatch logic | L4+L5 |
| FSM-002 | Drag-and-drop dispatch board | P1 | OCA fieldservice_timeline + L5 enhancements | L2+L5 |
| FSM-003 | Real-time GPS tracking | P1 | Traccar server + Flutter app | L4+L5 |
| FSM-004 | Route optimization | P1 | VROOM + OSRM | L4 |
| FSM-005 | Skill-based assignment | P1 | OCA fieldservice_skill | L2 |
| FSM-006 | Emergency job insertion with re-optimization | P1 | VROOM + L5 logic | L4+L5 |
| FSM-007 | Auto rescheduling suggestions | P2 | L5 custom logic | L5 |
| FSM-008 | Service territory/geo-fencing | P2 | Traccar geo-fencing + OCA fieldservice_geoengine | L2+L4 |
| FSM-009 | Capacity planning | P1 | OCA fieldservice + L5 rules | L2+L5 |
| FSM-010 | Travel time estimation (real-time traffic) | P2 | OSRM + Google Routes API (Dhaka) | L4+L3 |
| FSM-011 | Preferred technician for repeat customers | P3 | L5 custom field + logic | L5 |
| FSM-012 | Batch scheduling for AMC visits | P2 | OCA fieldservice_recurring | L2 |
| FSM-013 | Mobile app (PWA or native) | P1 | Custom Flutter app | L5 |
| FSM-014 | Offline mode with auto-sync | P1 | Custom Flutter app (SQLite/Hive) | L5 |
| FSM-015 | Mobile job queue | P1 | Custom Flutter app | L5 |
| FSM-016 | GPS navigation (Google Maps) | P1 | Flutter Google Maps plugin | L5 |
| FSM-017 | Digital service forms on mobile | P1 | Custom Flutter app | L5 |
| FSM-018 | Before/after photo capture with GPS/timestamp | P1 | Custom Flutter app | L5 |
| FSM-019 | Customer e-signature capture | P1 | Custom Flutter app | L5 |
| FSM-020 | Real-time status updates from field | P1 | Custom Flutter app → Odoo API | L5 |
| FSM-021 | Parts consumption with barcode scanning | P1 | Custom Flutter app + camera API | L5 |
| FSM-022 | Time tracking with auto-capture | P1 | Custom Flutter app | L5 |
| FSM-023 | In-app messaging | P2 | Custom Flutter app + Odoo Discuss | L5 |
| FSM-024 | Knowledge base access | P2 | Custom Flutter app + Odoo knowledge/wiki | L5 |
| FSM-025 | Expense reporting from mobile | P3 | Custom Flutter app + OCA hr_expense | L2+L5 |
| FSM-026 | Push notifications | P1 | Firebase + Novu | L4 |
| FSM-027 | Customer-facing tracking page | P1 | Next.js portal + Traccar API | L4+L5 |
| FSM-028 | Auto SMS/notification on dispatch/arrival | P1 | n8n + Novu | L4 |
| FSM-029 | Pick & Drop service tracking | P1 | OCA fieldservice_distribution | L2 |
| FSM-030 | Walk-in queue management | P2 | L5 custom queue module | L5 |
| FSM-031 | Remote support session | P3 | Future phase | — |

**FSM Coverage: L2=16%, L4=23%, L5=61%** (mobile app is the largest custom development effort)

### 7.4 Inventory & Spare Parts (INV) — 24 Requirements

| Req # | Requirement | Priority | Solution | Layer |
|---|---|---|---|---|
| INV-001 | Multi-warehouse (51+ locations) | P1 | Odoo CE inventory + OCA operating_unit | L1+L2 |
| INV-002 | Central warehouse + regional hubs | P1 | Odoo CE warehouse hierarchy | L1 |
| INV-003 | Van/mobile stock per technician | P1 | OCA fieldservice_vehicle + fieldservice_stock | L2 |
| INV-004 | Real-time stock visibility dashboard | P1 | Odoo CE + Metabase dashboard | L1+L4 |
| INV-005 | Barcode and QR code support | P1 | OCA stock_barcodes | L2 |
| INV-006 | Serial number tracking | P1 | Odoo CE serial tracking | L1 |
| INV-007 | Batch/lot tracking | P2 | Odoo CE lot tracking | L1 |
| INV-008 | Multi-UoM support | P2 | Odoo CE UoM | L1 |
| INV-009 | Goods receipt with quality inspection | P1 | Odoo CE receipt + OCA mgmtsystem_quality | L1+L2 |
| INV-010 | Inter-branch transfer with approval | P1 | Odoo CE internal transfers + L5 approval | L1+L5 |
| INV-011 | Stock requisition from service orders | P1 | OCA fieldservice_stock | L2 |
| INV-012 | Automatic replenishment (reorder rules) | P1 | Odoo CE reorder rules | L1 |
| INV-013 | Cycle counting and reconciliation | P1 | Odoo CE inventory adjustment | L1 |
| INV-014 | Dead stock identification | P2 | Metabase report + L5 alert | L4+L5 |
| INV-015 | Warranty returns management | P1 | L5 custom module | L5 |
| INV-016 | Consignment inventory | P2 | L5 custom module | L5 |
| INV-017 | Stock valuation (FIFO, weighted avg) | P1 | Odoo CE stock valuation | L1 |
| INV-018 | Min/max stock level alerts | P1 | Odoo CE reorder rules + n8n alerts | L1+L4 |
| INV-019 | Master parts catalog with compatibility | P1 | Odoo CE products + L5 compatibility matrix | L1+L5 |
| INV-020 | Genuine vs compatible classification | P1 | Odoo CE product categories | L1 |
| INV-021 | Parts pricing tiers | P1 | Odoo CE pricelists | L1 |
| INV-022 | Parts substitution mapping | P2 | Odoo CE alternative products | L1 |
| INV-023 | Parts image library | P3 | Odoo CE product images | L1 |
| INV-024 | Supplier lead time tracking | P2 | Odoo CE vendor delays | L1 |

**INV Coverage: L1=63%, L2=17%, L4=8%, L5=12%**

### 7.5 CRM — 18 Requirements

| Req # | Requirement | Priority | Solution | Layer |
|---|---|---|---|---|
| CRM-001 | 360-degree customer profile | P1 | Odoo CE contacts + L5 custom views | L1+L5 |
| CRM-002 | Device registry per customer | P1 | OCA fieldservice_equipment | L2 |
| CRM-003 | Customer segmentation | P1 | Odoo CE contact tags + categories | L1 |
| CRM-004 | Communication history (all channels) | P1 | Odoo CE chatter + L5 WhatsApp log | L1+L5 |
| CRM-005 | Automated lifecycle communications | P2 | n8n workflows | L4 |
| CRM-006 | Customer satisfaction surveys (CSAT/NPS) | P1 | OCA helpdesk_mgmt_rating + L5 NPS | L2+L5 |
| CRM-007 | Complaint management with escalation | P1 | OCA helpdesk_mgmt | L2 |
| CRM-008 | Duplicate detection and merge | P2 | Odoo CE contact merge | L1 |
| CRM-009 | Privilege Program (Silver/Gold/Diamond) | P1 | L5 custom loyalty module | L5 |
| CRM-010 | Membership enrollment/renewal | P1 | L5 custom loyalty module | L5 |
| CRM-011 | Points/rewards system | P2 | L5 custom loyalty module | L5 |
| CRM-012 | Promotional campaign management | P2 | Odoo CE mass mailing + n8n | L1+L4 |
| CRM-013 | Referral program | P3 | L5 custom module | L5 |
| CRM-014 | Lead capture (multi-channel) | P2 | Odoo CE CRM leads | L1 |
| CRM-015 | Corporate account management | P1 | Odoo CE contacts + OCA multi-relation | L1+L2 |
| CRM-016 | Sales pipeline for B2B | P2 | Odoo CE CRM pipeline | L1 |
| CRM-017 | Quotation generation with approval | P1 | Odoo CE sales quotation | L1 |
| CRM-018 | Sales forecast | P3 | Metabase reports | L4 |

**CRM Coverage: L1=44%, L2=17%, L4=11%, L5=28%**

### 7.6 Financial Management (FIN) — 35 Requirements

| Req # | Requirement | Priority | Solution | Layer |
|---|---|---|---|---|
| FIN-001 | Multi-branch chart of accounts | P1 | Odoo CE accounting + OCA operating_unit | L1+L2 |
| FIN-002 | Multi-cost center accounting | P1 | Odoo CE analytic accounts | L1 |
| FIN-003 | GL with drill-down | P1 | Odoo CE general ledger | L1 |
| FIN-004 | Journal entries (manual + auto) | P1 | Odoo CE journal entries | L1 |
| FIN-005 | Bank reconciliation | P1 | Odoo CE bank reconciliation (manual) | L1 |
| FIN-006 | Multi-currency (BDT + USD) | P2 | Odoo CE multi-currency | L1 |
| FIN-007 | Fixed asset management | P2 | OCA account_asset_management | L2 |
| FIN-008 | Period-end closing | P1 | Odoo CE fiscal period lock | L1 |
| FIN-009 | Bangladesh fiscal year (July-June) | P1 | Odoo CE fiscal year config | L1 |
| FIN-010 | Invoice from service orders (auto) | P1 | OCA fieldservice_account | L2 |
| FIN-011 | Warranty claim invoicing | P1 | L5 custom warranty billing | L5 |
| FIN-012 | Corporate billing cycles | P1 | L5 custom consolidated invoicing | L5 |
| FIN-013 | AMC subscription invoicing | P1 | OCA fieldservice_agreement + Odoo invoicing | L1+L2 |
| FIN-014 | Multiple payment methods | P1 | Odoo CE + SSLCOMMERZ + bKash modules | L1+L3 |
| FIN-015 | Advance payment/deposit | P2 | Odoo CE advance payments | L1 |
| FIN-016 | Credit note and refund | P1 | Odoo CE credit notes | L1 |
| FIN-017 | Customer aging analysis | P1 | Odoo CE aged receivable report | L1 |
| FIN-018 | Collection management | P2 | n8n automated follow-up workflows | L4 |
| FIN-019 | 3-way matching (PO/receipt/invoice) | P1 | Odoo CE purchase + inventory | L1 |
| FIN-020 | Payment scheduling and batch | P1 | Odoo CE batch payments | L1 |
| FIN-021 | Technician expense reimbursement | P2 | OCA hr_expense | L2 |
| FIN-022 | Vendor aging analysis | P1 | Odoo CE aged payable report | L1 |
| FIN-023 | Automated payment approvals | P1 | L5 custom approval workflow | L5 |
| FIN-024 | Bangladesh VAT calculation | P1 | Odoo CE l10n_bd (15% VAT) | L1 |
| FIN-025 | Tax withholding (TDS) | P1 | L5 custom TDS module | L5 |
| FIN-026 | Mushak VAT return preparation | P1 | L5 custom Mushak module | L5 |
| FIN-027 | NBR-compliant tax invoice (Mushak 6.3) | P1 | L5 custom Mushak invoice template | L5 |
| FIN-028 | Audit trail for all transactions | P1 | Odoo CE audit log | L1 |
| FIN-029 | Financial statements (BD GAAP/IFRS) | P1 | Odoo CE + OCA mis_builder | L1+L2 |
| FIN-030 | Branch-wise P&L + consolidated | P1 | OCA operating_unit + mis_builder | L2 |
| FIN-031 | Revenue analysis (multi-dimensional) | P1 | Metabase dashboards | L4 |
| FIN-032 | Cost analysis per service order | P1 | Metabase reports | L4 |
| FIN-033 | Budget vs actual reporting | P2 | OCA mis_builder_budget | L2 |
| FIN-034 | Warranty revenue tracking | P1 | L5 custom warranty revenue module | L5 |
| FIN-035 | Configurable financial dashboards | P1 | Metabase + Grafana | L4 |

**FIN Coverage: L1=49%, L2=17%, L3=3%, L4=11%, L5=20%**

### 7.7 HR & Payroll (HRM) — 23 Requirements

| Req # | Requirement | Priority | Solution | Layer |
|---|---|---|---|---|
| HRM-001 | Employee master data | P1 | Odoo CE HR employees | L1 |
| HRM-002 | Employee lifecycle management | P1 | Odoo CE HR + OCA hr_contract_type | L1+L2 |
| HRM-003 | Organization hierarchy | P1 | Odoo CE HR departments | L1 |
| HRM-004 | Employee document management | P2 | OCA dms + Odoo attachments | L2 |
| HRM-005 | Employee self-service portal | P2 | Odoo CE portal + L5 ESS enhancements | L1+L5 |
| HRM-006 | Technician skill matrix | P1 | OCA hr_employee_skill + fieldservice_skill | L2 |
| HRM-007 | Certification tracking with expiry alerts | P1 | OCA hr_employee_skill + n8n alerts | L2+L4 |
| HRM-008 | Training management | P1 | L5 custom training module | L5 |
| HRM-009 | Technician performance metrics | P1 | Metabase dashboards from Odoo data | L4 |
| HRM-010 | Technician ranking/leaderboard | P2 | Metabase dashboard | L4 |
| HRM-011 | Shift management and roster | P1 | L5 custom shift module | L5 |
| HRM-012 | Attendance (biometric integration) | P1 | Odoo CE attendance + L5 biometric bridge | L1+L5 |
| HRM-013 | GPS-based attendance for field staff | P2 | OCA hr_attendance_geolocation | L2 |
| HRM-014 | Leave management | P1 | Odoo CE time off | L1 |
| HRM-015 | Bangladesh public holiday calendar | P1 | OCA hr_holidays_public | L2 |
| HRM-016 | Overtime tracking and approval | P1 | L5 custom overtime module | L5 |
| HRM-017 | Payroll processing | P1 | OCA hr_payroll_community + L5 BD rules | L2+L5 |
| HRM-018 | Bangladesh salary structure | P1 | L5 custom payroll (BD Labour Act) | L5 |
| HRM-019 | Performance-based incentive calculation | P1 | L5 custom incentive module | L5 |
| HRM-020 | Bangladesh tax deductions | P1 | L5 custom tax slab module | L5 |
| HRM-021 | BEFTN bank salary file | P1 | L5 custom BEFTN generator | L5 |
| HRM-022 | Payslip generation | P1 | OCA hr_payroll_community | L2 |
| HRM-023 | Annual tax certificate | P2 | L5 custom NBR certificate | L5 |

**HRM Coverage: L1=22%, L2=26%, L4=13%, L5=39%** (Bangladesh payroll requires significant custom work)

### 7.8 Contract & Warranty Management (CWM) — 22 Requirements

**Coverage: L1=5%, L2=45%, L4=5%, L5=45%** (Warranty claim processing is heavily custom)

### 7.9 Procurement & Supply Chain (SCM) — 12 Requirements

**Coverage: L1=67%, L2=25%, L5=8%** (Well covered by Odoo CE Purchase + OCA)

### 7.10 Reporting & BI (BI) — 14 Requirements

**Coverage: L1=14%, L2=22%, L4=64%** (Metabase + Grafana cover most BI needs)

### 7.11 Document Management (DMS) — 8 Requirements

**Coverage: L1=12%, L2=50%, L4=25%, L5=13%**

### 7.12 Quality Management (QMS) — 8 Requirements

**Coverage: L2=75%, L4=12%, L5=13%** (OCA management-system covers most QMS needs)

### 7.13 Smart Portal Suite — 60+ Requirements

| Portal | Solution | Coverage |
|---|---|---|
| Customer Self-Service | 1000FiX Next.js 15 platform + Odoo API integration | Next.js handles UI; Odoo provides data via JSON-2 API |
| Technician Mobile | Custom Flutter app | Full custom development |
| Admin Operations | Odoo CE backend + custom dashboards | Odoo backend with custom views |
| Corporate B2B | Next.js portal + Odoo API | Next.js handles UI; Odoo provides data |
| Vendor & Partner | Odoo CE portal module + custom views | L1+L5 |
| Analytics Dashboard | Metabase embedded dashboards | L4 |

**Note:** The 1000FiX Next.js 15 + Payload CMS 3 platform is a separate project (out of ERP scope) but the ERP must provide APIs for integration. Odoo's JSON-2 API and webhook support enable this.

### 7.14 Overall Coverage Summary

| Module | Total Reqs | L1 (Odoo CE) | L2 (OCA) | L3 (Third-party) | L4 (Open Source) | L5 (Custom) |
|---|---|---|---|---|---|---|
| Service & Repair (SRM) | 37 | 30% | 43% | 0% | 5% | 22% |
| Field Service (FSM) | 31 | 0% | 16% | 0% | 23% | 61% |
| Inventory (INV) | 24 | 63% | 17% | 0% | 8% | 12% |
| CRM | 18 | 44% | 17% | 0% | 11% | 28% |
| Finance (FIN) | 35 | 49% | 17% | 3% | 11% | 20% |
| HR & Payroll (HRM) | 23 | 22% | 26% | 0% | 13% | 39% |
| Contract/Warranty (CWM) | 22 | 5% | 45% | 0% | 5% | 45% |
| Procurement (SCM) | 12 | 67% | 25% | 0% | 0% | 8% |
| BI & Reporting | 14 | 14% | 22% | 0% | 64% | 0% |
| Document Mgmt (DMS) | 8 | 12% | 50% | 0% | 25% | 13% |
| Quality (QMS) | 8 | 0% | 75% | 0% | 12% | 13% |
| Smart Portals | 60+ | 15% | 10% | 5% | 20% | 50% |
| **WEIGHTED TOTAL** | **290+** | **~30%** | **~25%** | **~2%** | **~15%** | **~28%** |

**P1 (Must-Have) Requirements Coverage:**
- **72%** covered by zero-license solutions (L1+L2+L3+L4)
- **28%** requires custom development (L5)

---

## 8. GAP ANALYSIS & CUSTOM DEVELOPMENT SCOPE

### 8.1 Custom Development Items (Layer 5)

| # | Custom Module | Priority | Effort (Person-Weeks) | Phase | Description |
|---|---|---|---|---|---|
| **CD-01** | **Technician Mobile App (Flutter)** | P1 | 16-20 | Phase 2 | Full mobile app with offline-first, GPS, e-signature, barcode, Bengali UI |
| **CD-02** | **Bangladesh Mushak 6.3 Invoice** | P1 | 4-6 | Phase 3 | NBR-compliant VAT invoice format, BIN/TIN fields, Mushak report |
| **CD-03** | **Bangladesh Payroll Module** | P1 | 8-12 | Phase 5 | Tax slabs, provident fund, gratuity, BEFTN file generation |
| **CD-04** | **Warranty Claim Automation** | P1 | 6-8 | Phase 4 | Brand-specific claim formats (Dell, HP, Samsung, etc.), auto-submission |
| **CD-05** | **Privilege Program (Loyalty)** | P1 | 4-6 | Phase 1 | Silver/Gold/Diamond tiers, auto-discount on labor, enrollment/renewal |
| **CD-06** | **AI Dispatch Engine** | P1 | 6-8 | Phase 2 | Integration with VROOM/OSRM, skill matching, AI assignment scoring |
| **CD-07** | **Customer Tracking Page** | P1 | 3-4 | Phase 2 | Real-time GPS tracking page with ETA (Next.js + Traccar) |
| **CD-08** | **bKash/Nagad Direct Integration** | P1 | 3-4 | Phase 3 | OTP-based payment flow, auto-reconciliation |
| **CD-09** | **Bangladesh TDS Module** | P1 | 2-3 | Phase 3 | Tax withholding at source per BD tax laws |
| **CD-10** | **Rework Detection** | P1 | 2-3 | Phase 1 | Auto-flag same device + same fault within 30 days |
| **CD-11** | **Diagnostic Checklist Builder** | P1 | 3-4 | Phase 1 | Configurable checklists per device type and issue |
| **CD-12** | **Bangladesh Address Fields** | P1 | 1-2 | Phase 1 | 8 divisions, 64 districts, upazilas, postal codes |
| **CD-13** | **Consolidated B2B Invoicing** | P1 | 3-4 | Phase 4 | Monthly consolidated invoice for corporate clients |
| **CD-14** | **Performance Incentive Calculator** | P1 | 3-4 | Phase 5 | KPI-based incentive (jobs, CSAT, FTFR) → payroll |
| **CD-15** | **Shift & Roster Management** | P1 | 3-4 | Phase 5 | Branch-wise shift planning, roster generation |
| **CD-16** | **Bengali NLP Chatbot** | P2 | 8-12 | Phase 6 | LLM-based chatbot (Ollama + multilingual model) |
| **CD-17** | **Walk-in Queue Management** | P2 | 2-3 | Phase 1 | Token system, estimated wait time display |
| **CD-18** | **Warranty Revenue Tracker** | P1 | 2-3 | Phase 4 | Claim aging, reconciliation, brand payment matching |
| **CD-19** | **NID Validation** | P1 | 1 | Phase 3 | 10/17-digit Bangladesh NID format validation |
| **CD-20** | **Overtime Approval Module** | P1 | 2-3 | Phase 5 | Pre-approval workflow, auto-payroll integration |

**Total Custom Development Effort: 80-115 person-weeks (~20-29 person-months)**

With a team of 4 developers: **5-7 months of development** spread across the 18-month implementation.

### 8.2 Custom Development Cost Estimate

| Resource | Rate (USD/month) | Duration | Cost |
|---|---|---|---|
| 2 Senior Odoo Developers (Python) | $2,500-$4,000/person | 12 months | $60,000-$96,000 |
| 2 Flutter Developers | $2,000-$3,500/person | 4 months | $16,000-$28,000 |
| 1 DevOps/Infrastructure | $2,000-$3,000 | 6 months | $12,000-$18,000 |
| 1 BA/QA | $1,500-$2,500 | 12 months | $18,000-$30,000 |
| **Total Custom Development** | | | **$106,000-$172,000** |

**Note:** Rates are based on Bangladesh market rates (local developers). Using an Odoo implementation partner like Metamorphosis Ltd. or Xsellence would add project management overhead but reduce risk.

---

## 9. SYSTEM ARCHITECTURE DESIGN

### 9.1 High-Level System Architecture

```
╔══════════════════════════════════════════════════════════════════════╗
║                    1000FiX DIGITAL ECOSYSTEM                        ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ┌──────────────────────────┐     ┌──────────────────────────────┐  ║
║  │   ODOO 19 CE             │     │  NEXT.JS 15 WEB PLATFORM     │  ║
║  │   (ERP BACKBONE)         │◄───►│  (Payload CMS 3)             │  ║
║  │                          │ API │                              │  ║
║  │  ▪ CRM & Contacts       │     │  ▪ Customer Portal           │  ║
║  │  ▪ OCA Field Service     │     │  ▪ Corporate B2B Portal      │  ║
║  │  ▪ OCA Helpdesk + SLA   │     │  ▪ Public Website            │  ║
║  │  ▪ Inventory & Stock    │     │  ▪ AI Chatbot Interface      │  ║
║  │  ▪ Accounting (l10n_bd) │     │  ▪ Customer Tracking Page    │  ║
║  │  ▪ OCA Payroll          │     │                              │  ║
║  │  ▪ Purchase & SCM       │     └──────────────────────────────┘  ║
║  │  ▪ OCA Quality/ISO      │                                      ║
║  │  ▪ OCA Operating Unit   │     ┌──────────────────────────────┐  ║
║  │  ▪ OCA DMS              │     │  FLUTTER MOBILE APP           │  ║
║  │  ▪ BD Custom Modules    │◄───►│  (Technician Portal)         │  ║
║  │                          │ API │                              │  ║
║  └────────┬─────────────────┘     │  ▪ Job Queue & Navigation   │  ║
║           │                       │  ▪ Offline-First (SQLite)    │  ║
║           │ PostgreSQL 16         │  ▪ GPS Check-in/Tracking     │  ║
║           │                       │  ▪ Photo/Barcode/E-Sign      │  ║
║  ┌────────▼─────────────────┐     │  ▪ Bengali Language          │  ║
║  │   POSTGRESQL 16          │     └──────────────────────────────┘  ║
║  │   (Shared Database)      │                                      ║
║  │   ▪ Primary Server       │     ┌──────────────────────────────┐  ║
║  │   ▪ Read Replica (BI)    │     │  OPEN SOURCE SERVICES        │  ║
║  │   ▪ PgBouncer (pooling)  │     │                              │  ║
║  └──────────────────────────┘     │  ▪ Metabase (BI Dashboards)  │  ║
║                                    │  ▪ Grafana (Real-time Ops)   │  ║
║  ┌──────────────────────────┐     │  ▪ Traccar (GPS Server)      │  ║
║  │   INTEGRATION LAYER      │     │  ▪ n8n (Workflow Automation) │  ║
║  │                          │     │  ▪ Keycloak (SSO/Auth)       │  ║
║  │  ▪ Odoo JSON-2 API      │     │  ▪ VROOM/OSRM (Routing)     │  ║
║  │  ▪ Webhooks             │     │  ▪ Mayan EDMS (Documents)    │  ║
║  │  ▪ n8n Orchestration    │     │  ▪ Novu (Notifications)      │  ║
║  └──────────────────────────┘     │  ▪ Ollama (AI/Chatbot)       │  ║
║                                    └──────────────────────────────┘  ║
║  ┌──────────────────────────────────────────────────────────────┐   ║
║  │   EXTERNAL INTEGRATIONS                                       │   ║
║  │                                                               │   ║
║  │  bKash · Nagad · SSLCOMMERZ · Google Maps · Firebase          │   ║
║  │  WhatsApp Business API · Bangladesh SMS Gateway               │   ║
║  │  Biometric Devices · Brand Partner Portals                    │   ║
║  └──────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════╝
```

### 9.2 Integration Architecture (Odoo ↔ Next.js Platform)

```
    NEXT.JS 15 PLATFORM                    ODOO 19 CE
    ┌─────────────────┐                   ┌─────────────────┐
    │ Customer Portal │                   │ Service Orders   │
    │ B2B Portal      │─── JSON-2 API ──►│ CRM / Contacts  │
    │ Public Website  │◄── Webhooks ─────│ Inventory       │
    │ Tracking Page   │                   │ Invoicing       │
    └────────┬────────┘                   └────────┬────────┘
             │                                      │
    ┌────────▼────────┐                   ┌────────▼────────┐
    │ Payload CMS 3   │                   │ PostgreSQL 16   │
    │ PostgreSQL 16   │                   │ (Odoo Database) │
    │ (CMS Database)  │                   │                 │
    └─────────────────┘                   └─────────────────┘

    API ENDPOINTS (Odoo → Next.js):
    ────────────────────────────────
    POST /json/2/service.order          → Create service order
    GET  /json/2/service.order/{id}     → Get order status
    GET  /json/2/technician/{id}/location → GPS position
    GET  /json/2/booking/availability   → Available time slots
    POST /json/2/customer/sync          → Sync customer data
    POST /json/2/payment/confirm        → Payment confirmation
    GET  /json/2/invoice/{id}           → Invoice details
    GET  /json/2/contract/{customer_id} → Active contracts

    WEBHOOKS (Odoo → Next.js):
    ────────────────────────────
    service_order.status_changed        → Trigger notifications
    technician.dispatched               → Enable live tracking
    invoice.created                     → Send payment link
    warranty.claim_created              → Notify brand partner
```

### 9.3 Deployment Architecture

```
    ┌─── CLOUD INFRASTRUCTURE (DigitalOcean Singapore) ──────────────┐
    │                                                                  │
    │  ┌─── Docker Compose / K3s Cluster ──────────────────────────┐ │
    │  │                                                            │ │
    │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │ │
    │  │  │ Nginx    │  │ Odoo 19  │  │ Odoo 19  │               │ │
    │  │  │ (Reverse │──│ Worker 1 │  │ Worker 2 │               │ │
    │  │  │  Proxy + │  │ (8 wkrs) │  │ (8 wkrs) │               │ │
    │  │  │  LB)     │  └─────┬────┘  └─────┬────┘               │ │
    │  │  └──────────┘        │              │                     │ │
    │  │                 ┌────▼──────────────▼────┐               │ │
    │  │                 │  PostgreSQL 16          │               │ │
    │  │                 │  Primary (32GB RAM)     │               │ │
    │  │                 │  + Read Replica          │               │ │
    │  │                 │  + PgBouncer             │               │ │
    │  │                 └────────────────────────┘               │ │
    │  │                                                            │ │
    │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │ │
    │  │  │ Metabase │  │ Grafana  │  │ Traccar  │               │ │
    │  │  └──────────┘  └──────────┘  └──────────┘               │ │
    │  │                                                            │ │
    │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │ │
    │  │  │ n8n      │  │ Keycloak │  │ Novu     │               │ │
    │  │  └──────────┘  └──────────┘  └──────────┘               │ │
    │  │                                                            │ │
    │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │ │
    │  │  │ VROOM    │  │ OSRM     │  │ Mayan    │               │ │
    │  │  │          │  │ (BD Map) │  │ EDMS     │               │ │
    │  │  └──────────┘  └──────────┘  └──────────┘               │ │
    │  │                                                            │ │
    │  │  ┌──────────┐  ┌──────────┐                              │ │
    │  │  │ Redis    │  │ Ollama   │  (Phase 6)                   │ │
    │  │  │ (Cache)  │  │ (AI/LLM) │                              │ │
    │  │  └──────────┘  └──────────┘                              │ │
    │  │                                                            │ │
    │  └────────────────────────────────────────────────────────────┘ │
    │                                                                  │
    │  Estimated Monthly Cost: $300-$600/month                        │
    │  (2x Droplets: 8vCPU/32GB each + Managed PostgreSQL)           │
    │                                                                  │
    └──────────────────────────────────────────────────────────────────┘
```

---

## 10. COST ANALYSIS & BUDGET PROJECTION

### 10.1 Software Licensing Cost

| Component | License | Annual Cost | 3-Year Cost |
|---|---|---|---|
| Odoo 19 CE | LGPL v3 | $0 | $0 |
| All OCA Modules (94+) | AGPL-3 / LGPL-3 | $0 | $0 |
| Metabase | AGPL-3 | $0 | $0 |
| Grafana | AGPL-3 | $0 | $0 |
| Traccar | Apache-2.0 | $0 | $0 |
| Mayan EDMS | Apache-2.0 | $0 | $0 |
| n8n | Fair-code (self-hosted free) | $0 | $0 |
| Keycloak | Apache-2.0 | $0 | $0 |
| VROOM + OSRM | BSD-2 | $0 | $0 |
| Novu | MIT | $0 | $0 |
| Flutter SDK | BSD-3 | $0 | $0 |
| **TOTAL SOFTWARE LICENSE** | | **$0** | **$0** |

### 10.2 Third-Party API Costs (Not Avoidable)

| Service | Estimated Monthly Cost | Annual Cost | Notes |
|---|---|---|---|
| Google Maps Platform (Geocoding + Routes) | $200-$400 | $2,400-$4,800 | $200 free credit/month from Google |
| WhatsApp Business API | $100-$300 | $1,200-$3,600 | Per-conversation pricing |
| Bangladesh SMS Gateway | $100-$200 | $1,200-$2,400 | ~BDT 0.25-0.50/SMS |
| Firebase (Push Notifications) | $0-$50 | $0-$600 | Free tier sufficient initially |
| Cloudinary (Image Storage) | $50-$100 | $600-$1,200 | Photo storage for service orders |
| **TOTAL API COSTS** | **$450-$1,050/month** | **$5,400-$12,600/year** |

### 10.3 Infrastructure / Hosting (3-Year)

| Resource | Monthly Cost | Annual Cost | 3-Year Cost |
|---|---|---|---|
| Odoo App Servers (2x 8vCPU/32GB) | $200-$320 | $2,400-$3,840 | $7,200-$11,520 |
| PostgreSQL Managed DB (8vCPU/32GB) | $150-$250 | $1,800-$3,000 | $5,400-$9,000 |
| Supporting Services Server (8vCPU/16GB) | $80-$160 | $960-$1,920 | $2,880-$5,760 |
| Backup Storage (500GB) | $25-$50 | $300-$600 | $900-$1,800 |
| CDN (Cloudflare) | $0-$20 | $0-$240 | $0-$720 |
| Domain + SSL | $10-$20 | $120-$240 | $360-$720 |
| **TOTAL INFRASTRUCTURE** | **$465-$820/month** | **$5,580-$9,840/year** | **$16,740-$29,520** |

### 10.4 Implementation & Development Costs

| Category | Estimated Cost | Notes |
|---|---|---|
| Project Management (12 months) | $12,000-$24,000 | PM from implementation partner |
| Business Analysis & Design (3 months) | $6,000-$12,000 | BA from implementation partner |
| Odoo Configuration & Setup | $8,000-$15,000 | Module installation, configuration, workflows |
| Custom Module Development (20 modules) | $40,000-$65,000 | 2 senior Odoo developers, 12 months |
| Flutter Mobile App Development | $16,000-$28,000 | 2 Flutter developers, 4 months |
| Integration Development | $10,000-$18,000 | Odoo ↔ Next.js, payment gateways, SMS, GPS |
| Data Migration | $5,000-$10,000 | Data profiling, cleansing, migration scripts |
| Testing (SIT + UAT) | $4,000-$8,000 | Included in dev team scope |
| DevOps & Infrastructure Setup | $5,000-$10,000 | Docker/K3s, monitoring, backups, CI/CD |
| Go-Live Support (6 phases) | $5,000-$10,000 | On-site support per phase |
| **TOTAL IMPLEMENTATION** | **$111,000-$200,000** |

### 10.5 Training Costs

| Training | Cost | Notes |
|---|---|---|
| Train-the-Trainer Program (10 super-users) | $3,000-$5,000 | 5-day intensive program |
| End-User Training Materials (Bengali) | $2,000-$4,000 | Video tutorials, QRCs, manuals |
| On-Site Training Sessions (51 branches) | $3,000-$6,000 | Regional batch training |
| **TOTAL TRAINING** | **$8,000-$15,000** |

### 10.6 Support & Maintenance (Annual, Years 2-3)

| Category | Annual Cost | 2-Year Cost (Y2+Y3) |
|---|---|---|
| Odoo Technical Support (local partner) | $6,000-$12,000 | $12,000-$24,000 |
| Bug Fixes & Enhancements | $4,000-$8,000 | $8,000-$16,000 |
| Version Upgrades (Odoo 19 → 20) | $3,000-$6,000 | $3,000-$6,000 |
| Infrastructure Management | $2,000-$4,000 | $4,000-$8,000 |
| **TOTAL SUPPORT** | **$15,000-$30,000/year** | **$27,000-$54,000** |

### 10.7 Total Cost of Ownership (3-Year)

| Category | Year 1 | Year 2 | Year 3 | 3-Year Total |
|---|---|---|---|---|
| Software Licensing | $0 | $0 | $0 | **$0** |
| Implementation & Development | $111,000-$200,000 | $0 | $0 | $111,000-$200,000 |
| Training | $8,000-$15,000 | $0 | $0 | $8,000-$15,000 |
| Infrastructure / Hosting | $5,580-$9,840 | $5,580-$9,840 | $5,580-$9,840 | $16,740-$29,520 |
| Third-Party APIs | $5,400-$12,600 | $5,400-$12,600 | $5,400-$12,600 | $16,200-$37,800 |
| Support & Maintenance | $0 (warranty) | $15,000-$30,000 | $15,000-$30,000 | $30,000-$60,000 |
| **ANNUAL TOTAL** | **$129,980-$237,440** | **$25,980-$52,440** | **$25,980-$52,440** | |
| **3-YEAR TCO** | | | | **$181,940-$342,320** |

### 10.8 Comparison: Odoo CE + Open Source vs Odoo Enterprise

| Category | Odoo CE + Open Source | Odoo Enterprise | Savings |
|---|---|---|---|
| Software License (3yr, 700 users) | $0 | $260,820 ($31.10/user/mo) | **$260,820** |
| Implementation | $111,000-$200,000 | $60,000-$120,000 | ($51,000-$80,000) more |
| Infrastructure | $16,740-$29,520 | $20,000-$50,000 | Similar |
| Training | $8,000-$15,000 | $10,000-$20,000 | Similar |
| Support | $30,000-$60,000 | $15,000-$40,000 | ($15,000-$20,000) more |
| **3-Year TCO** | **$182K-$342K** | **$366K-$491K** | **$124K-$209K savings** |

**Verdict:** The CE + Open Source approach saves $124K-$209K over 3 years compared to Odoo Enterprise, with the savings coming entirely from eliminated licensing fees. The trade-off is higher implementation cost and greater technical complexity in managing multiple open-source tools.

---

## 11. IMPLEMENTATION ROADMAP

### 11.1 Phased Rollout (18 Months)

```
MONTH:  1    2    3    4    5    6    7    8    9   10   11   12   13   14   15   16   17   18
        ├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤
PHASE 1 ████████████████
        Foundation        GO-LIVE ▲
                          (Month 4)

PHASE 2              ████████████████
                     Field Operations  GO-LIVE ▲
                                       (Month 7)

PHASE 3                           ████████████████
                                  Financial Control   GO-LIVE ▲
                                                      (Month 10)

PHASE 4                                        ████████████████
                                               Contracts/Partners   GO-LIVE ▲
                                                                    (Month 13)

PHASE 5                                                      ████████████████
                                                             HR/BI/Quality    GO-LIVE ▲
                                                                              (Month 16)

PHASE 6                                                                   ████████████
                                                                          Optimization
                                                                                  FULL GO-LIVE ▲
                                                                                  (Month 18)
```

### 11.2 Phase Details

#### Phase 1: Foundation (Months 1-4) — GO-LIVE Month 4

**Scope:** Service & Repair Management, CRM, Basic Inventory
**Geography:** Dhaka HQ + 5 pilot service centers

| Deliverable | Technology | Week |
|---|---|---|
| Infrastructure setup (Docker, PostgreSQL, Nginx) | DevOps | W1-2 |
| Odoo 19 CE installation and base configuration | Odoo CE | W2-3 |
| OCA field-service + helpdesk installation | OCA | W3-4 |
| OCA operating-unit (multi-branch) setup | OCA | W3-4 |
| Bangladesh localization (l10n_bd + custom address fields) | L1+L5 | W4-5 |
| Keycloak SSO setup | Keycloak | W4-5 |
| CRM configuration (contacts, devices, segmentation) | L1+L2 | W5-7 |
| Service order workflows (stages, SLAs, escalation) | L2+L5 | W6-8 |
| Privilege Program module development | L5 | W7-10 |
| Diagnostic checklist module development | L5 | W8-10 |
| Rework detection module | L5 | W9-11 |
| Basic inventory setup (HQ + 5 pilots) | L1 | W10-12 |
| n8n notification workflows (SMS, email) | L4 | W11-13 |
| Data migration (customers, devices, service history) | Migration | W12-14 |
| User training (agents, dispatchers) | Training | W14-15 |
| UAT and go-live | | W15-16 |

#### Phase 2: Field Operations (Months 4-7) — GO-LIVE Month 7

**Scope:** Field Service, Technician Mobile App, Route Optimization
**Geography:** All Dhaka service centers

| Deliverable | Technology | Week |
|---|---|---|
| Flutter mobile app development (Sprint 1: Core UI, job queue) | Flutter | W1-4 |
| Traccar GPS server deployment | Traccar | W2-3 |
| Flutter app Sprint 2: GPS navigation, check-in, photos | Flutter | W4-7 |
| Flutter app Sprint 3: Offline mode, barcode, e-signature | Flutter | W7-10 |
| VROOM/OSRM deployment + AI dispatch engine | L4+L5 | W4-8 |
| Customer tracking page (Next.js integration) | L5 | W6-8 |
| OCA fieldservice_route + Google Maps integration | L2 | W5-7 |
| Metabase deployment + initial dashboards | Metabase | W8-10 |
| Grafana real-time operations dashboard | Grafana | W9-10 |
| Field technician training (batch 1: 50 technicians) | Training | W10-11 |
| Pilot with 20 technicians | Testing | W11-12 |
| Full Dhaka rollout | | W12-13 |

#### Phase 3: Financial Control (Months 7-10) — GO-LIVE Month 10

**Scope:** Finance & Accounting, Invoicing, Payment Integration
**Geography:** All Dhaka + Chittagong

| Deliverable | Technology | Week |
|---|---|---|
| Bangladesh Mushak 6.3 invoice module development | L5 | W1-5 |
| Bangladesh TDS module | L5 | W3-5 |
| SSLCOMMERZ payment integration | L3 | W2-4 |
| bKash direct integration | L5 | W4-7 |
| Odoo accounting configuration (chart of accounts, fiscal year) | L1 | W1-3 |
| Auto-invoice from service orders | L2 | W3-5 |
| Bank reconciliation setup | L1 | W5-7 |
| OCA mis_builder financial reports (branch P&L) | L2 | W6-8 |
| n8n payment reminder workflows | L4 | W7-8 |
| NID validation module | L5 | W8-9 |
| Finance team training | Training | W9-10 |
| Chittagong rollout | | W10-12 |

#### Phase 4: Contracts & Partners (Months 10-13) — GO-LIVE Month 13

**Scope:** Contract/Warranty Management, Vendor Portal, B2B Portal
**Geography:** All active service centers

| Deliverable | Technology | Week |
|---|---|---|
| AMC/RAMC contract management (OCA fieldservice_agreement) | L2 | W1-4 |
| Warranty claim automation module (brand-specific formats) | L5 | W2-7 |
| Warranty revenue tracker | L5 | W5-7 |
| Consolidated B2B invoicing module | L5 | W4-7 |
| Vendor portal configuration (Odoo CE portal) | L1 | W5-7 |
| Brand partner integration (claim submission workflows) | L5+L4 | W6-9 |
| Next.js B2B portal API integration | Integration | W7-9 |
| n8n renewal reminder workflows | L4 | W8-9 |
| Partner/vendor training | Training | W9-10 |
| National rollout to all active centers | | W10-12 |

#### Phase 5: Workforce & Intelligence (Months 13-16) — GO-LIVE Month 16

**Scope:** HR & Payroll, Full BI, Quality Management
**Geography:** All 51+ service centers

| Deliverable | Technology | Week |
|---|---|---|
| Bangladesh payroll module (tax slabs, PF, BEFTN) | L5 | W1-8 |
| Performance incentive calculator | L5 | W4-7 |
| Shift & roster management | L5 | W5-8 |
| Overtime approval module | L5 | W6-8 |
| OCA management-system (ISO 9001:2015 compliance) | L2 | W3-6 |
| Biometric attendance integration | L5 | W7-9 |
| Full Metabase dashboard suite (all KPIs from RFP Appendix D) | L4 | W6-10 |
| Mayan EDMS deployment | L4 | W8-10 |
| HR team training | Training | W10-11 |
| All 51+ centers live | | W11-12 |

#### Phase 6: Optimization (Months 16-18) — FULL GO-LIVE Month 18

**Scope:** AI Dispatch Optimization, Advanced Analytics, Bengali Chatbot, Process Optimization
**Geography:** Complete system

| Deliverable | Technology | Week |
|---|---|---|
| AI dispatch optimization refinement | L5 | W1-4 |
| Bengali NLP chatbot (Ollama + LLM) | L5 | W1-8 |
| Advanced Metabase analytics (predictive, forecasting) | L4 | W2-5 |
| Performance optimization and load testing | DevOps | W4-6 |
| Security audit and penetration testing | Security | W5-7 |
| Documentation completion | Docs | W6-8 |
| Full system acceptance testing | UAT | W7-8 |
| Knowledge transfer to internal team | Training | W8-10 |
| Post-go-live stabilization | Support | W8-12 |

### 11.3 Key Milestones

| Milestone | Target Date | Success Criteria |
|---|---|---|
| Project Kickoff | September 1, 2026 | Infrastructure ready, team onboarded |
| Phase 1 Go-Live | January 1, 2027 | Service orders from all channels at 6 pilot centers |
| Phase 2 Go-Live | April 1, 2027 | Mobile app deployed to 50+ technicians in Dhaka |
| Phase 3 Go-Live | July 1, 2027 | Mushak invoices, bKash payments, bank reconciliation |
| Phase 4 Go-Live | October 1, 2027 | AMC management, warranty claims automated |
| Phase 5 Go-Live | January 1, 2028 | Payroll processed, all 51+ centers live |
| Full System Go-Live | March 1, 2028 | All modules, all centers, AI dispatch, chatbot |
| Project Closure | May 31, 2028 | 30-day stability, knowledge transfer complete |

---

## 12. RISK ASSESSMENT & MITIGATION

### 12.1 Technical Risks

| # | Risk | Probability | Impact | Score | Mitigation | Contingency |
|---|---|---|---|---|---|---|
| TR-01 | OCA module incompatibility with Odoo 19 | Medium | High | High | Test all OCA modules in staging before deployment; use only v19-migrated modules | Fork and patch incompatible modules; engage OCA maintainers |
| TR-02 | Custom Flutter app development delays | Medium | Critical | Critical | Hire experienced Flutter team early; Agile sprints with 2-week demos | Phase 2 go-live delayed; use Odoo web PWA as interim (limited) |
| TR-03 | Performance issues at 500+ concurrent users | Low | Very High | High | Load test at 150% expected capacity before each go-live; horizontal scaling ready | Scale infrastructure; optimize PostgreSQL queries; implement caching |
| TR-04 | Offline sync data conflicts in mobile app | Medium | High | High | Conflict resolution strategy in design; last-write-wins with audit trail | Manual conflict resolution queue for dispatchers |
| TR-05 | Integration complexity (10+ systems) | High | High | High | Standardize on n8n for orchestration; API contract documentation; integration tests | Simplify by reducing tools; fallback to manual processes |
| TR-06 | PostgreSQL performance with large datasets | Low | High | Medium | Database partitioning, read replicas, materialized views, PgBouncer | Upgrade to larger DB instance; archive historical data |
| TR-07 | Odoo 19 → 20 migration disrupts OCA modules | Low | Medium | Medium | Budget for annual version migration; maintain module compatibility matrix | Delay upgrade; stay on v19 LTS if available |

### 12.2 Operational Risks

| # | Risk | Probability | Impact | Score | Mitigation | Contingency |
|---|---|---|---|---|---|---|
| OR-01 | Low technician mobile app adoption | High | Critical | Critical | Bengali-only UI; gamification; peer champions; field pilot with 20 users first; incentive tracking visible in app | Extended hands-on training; paper fallback for 60 days |
| OR-02 | Bangladesh internet instability in field | High | Medium | High | Offline-first architecture; 24-hour offline; auto-sync; data compression | Extended offline cache; SMS-based fallback for status updates |
| OR-03 | Staff resistance to change | Medium | High | High | Executive sponsorship; involve resistors in UAT; celebrate early wins; Bengali training materials | Additional change management workshops; slower rollout |
| OR-04 | Data migration quality issues | Medium | High | High | Data profiling early; trial migration; 2-week parallel run; reconciliation reports | Manual validation for top 1,000 customers and active contracts |
| OR-05 | Key team member departure | Medium | High | High | Knowledge documentation; cross-train 2 people per role; code documentation | Engage implementation partner as backup |

### 12.3 Strategic Risks

| # | Risk | Probability | Impact | Score | Mitigation | Contingency |
|---|---|---|---|---|---|---|
| SR-01 | Budget overrun due to custom development scope | Medium | High | High | Fixed-scope contracts for custom modules; change control for additions; defer P3 features | Reduce custom development scope; use simpler solutions |
| SR-02 | OCA project loses community support | Low | High | Medium | Choose only actively maintained modules (commits in last 6 months); maintain internal forks | Fork and maintain internally; engage Odoo partners |
| SR-03 | Odoo SA changes CE licensing terms | Very Low | Very High | Medium | LGPL v3 is irrevocable for published code; worst case: fork current version | Fork at current version; community will maintain (precedent exists) |
| SR-04 | Competitor launches superior digital platform | Low | Medium | Low | Focus on execution speed; Phase 1 live in 4 months provides early competitive advantage | Accelerate high-impact features |

---

## 13. EXPERT RECOMMENDATION & FINAL VERDICT

### 13.1 Recommended Approach

**Primary Recommendation: Odoo 19 CE + OCA + Open Source Stack (as documented in this strategy)**

This approach is recommended based on:

1. **Zero license cost** — Saves $260K+ over 3 years compared to Odoo Enterprise
2. **Budget compliance** — 3-year TCO of $182K-$342K fits within the $150K-$350K RFP range
3. **Functional coverage** — 72% of P1 requirements covered by existing free solutions; 28% via targeted custom development
4. **Local expertise available** — Metamorphosis Ltd. and Xsellence Bangladesh provide local Odoo support
5. **Technology alignment** — PostgreSQL 16 shared with existing Next.js platform; API-first architecture enables bidirectional integration
6. **Scalability proven** — Odoo CE has been deployed at 5,000+ user scale; architecture plan addresses 250K+ portal users
7. **Community strength** — OCA provides 1,000+ production-grade modules; Metabase, Traccar, n8n are established tools with large communities
8. **Risk manageable** — All risks identified have viable mitigation strategies; phased rollout limits blast radius

### 13.2 Critical Success Factors

1. **Hire or engage an experienced Odoo implementation partner** — Metamorphosis Ltd. (Bangladesh) is recommended given their local presence, Odoo Silver Partner status, and existing Bangladesh-specific modules (bKash, SSLCOMMERZ, SMS)
2. **Build the Flutter mobile app with a dedicated team** — This is the largest custom development effort and the most impactful for field operations
3. **Invest in Bangladesh-specific custom modules early** — Mushak 6.3, payroll, and bKash integration are non-negotiable; start development in Phase 1 even if deployment is later
4. **Run a focused pilot** — Phase 1 with 5 service centers before scaling; Phase 2 with 20 technicians before full rollout
5. **Appoint a dedicated ERP Project Manager internally** — Not outsourced; this person owns adoption and cross-department coordination

### 13.3 Alternative Approaches (Not Recommended, But Viable)

#### Option B: Odoo Enterprise Edition

| Aspect | Assessment |
|---|---|
| **When to consider** | If budget increases to $500K+ (3-year TCO); if internal development capacity is limited |
| **Advantages** | All modules included; official mobile app; Odoo.sh hosting; official support |
| **Disadvantages** | $31.10/user/month = $260K+/year for 700 users; vendor lock-in; still needs Bangladesh customization |
| **Verdict** | Exceeds budget; but provides lowest implementation risk |

#### Option C: ERPNext (Frappe Framework)

| Aspect | Assessment |
|---|---|
| **When to consider** | If Odoo CE proves too complex; if the team prefers JavaScript/Python (Frappe) |
| **Advantages** | Free, open source; simpler architecture; good for services businesses |
| **Disadvantages** | Smaller ecosystem; fewer modules; limited field service capabilities; smaller community |
| **Verdict** | Viable but riskier; Odoo's ecosystem advantage is significant |

#### Option D: Hybrid Odoo CE + Enterprise (Selected Modules)

| Aspect | Assessment |
|---|---|
| **When to consider** | If specific Enterprise modules (e.g., Field Service, Helpdesk) are critical and OCA alternatives prove insufficient |
| **Disadvantages** | Odoo does not sell individual Enterprise modules; it's all-or-nothing per user |
| **Verdict** | Not possible under current Odoo licensing model |

### 13.4 Final Decision Matrix

| Criterion (Weight) | Odoo CE + Open Source | Odoo Enterprise | ERPNext |
|---|---|---|---|
| License Cost (20%) | 10/10 | 2/10 | 10/10 |
| Functional Coverage (25%) | 7/10 | 9/10 | 5/10 |
| Bangladesh Localization (15%) | 5/10 | 6/10 | 4/10 |
| Implementation Risk (15%) | 6/10 | 8/10 | 5/10 |
| Scalability (10%) | 7/10 | 8/10 | 6/10 |
| Community/Ecosystem (10%) | 8/10 | 9/10 | 6/10 |
| Long-term Independence (5%) | 10/10 | 5/10 | 9/10 |
| **WEIGHTED SCORE** | **7.3/10** | **6.8/10** | **5.8/10** |

**Winner: Odoo 19 CE + Open Source Stack**

The zero-license approach achieves the best balance of cost, functionality, and long-term independence for 1000FiX's specific needs and budget constraints.

### 13.5 Next Steps

1. **Select implementation partner** — Engage Metamorphosis Ltd. or Xsellence Bangladesh for initial assessment
2. **Set up development environment** — Install Odoo 19 CE + OCA modules in staging
3. **Validate OCA modules** — Test field-service, helpdesk, management-system on v19
4. **Begin Flutter app design** — UX wireframes, offline architecture design
5. **Finalize Bangladesh custom modules scope** — Mushak 6.3 format specification, BEFTN file format, tax slab rules
6. **Prepare data migration assessment** — Profile existing spreadsheet/paper data quality
7. **Draft detailed project plan** — Convert this strategy into week-by-week project plan with resource allocation

---

## 14. APPENDICES

### Appendix A: Open Source Tool Reference

| Tool | Website | GitHub | License | Version |
|---|---|---|---|---|
| Odoo 19 CE | odoo.com | github.com/odoo/odoo | LGPL-3 | 19.0 |
| OCA Modules | odoo-community.org | github.com/OCA | AGPL-3/LGPL-3 | 19.0 |
| Metabase | metabase.com | github.com/metabase/metabase | AGPL-3 | 0.52+ |
| Grafana | grafana.com | github.com/grafana/grafana | AGPL-3 | 11.x |
| Traccar | traccar.org | github.com/traccar/traccar | Apache-2.0 | 6.x |
| Mayan EDMS | mayan-edms.com | github.com/mayan-edms/Mayan-EDMS | Apache-2.0 | 4.10 |
| n8n | n8n.io | github.com/n8n-io/n8n | Fair-code | 1.x |
| Keycloak | keycloak.org | github.com/keycloak/keycloak | Apache-2.0 | 26.x |
| VROOM | vroom-project.org | github.com/VROOM-Project/vroom | BSD-2 | 1.x |
| OSRM | project-osrm.org | github.com/Project-OSRM/osrm-backend | BSD-2 | 5.x |
| Novu | novu.co | github.com/novuhq/novu | MIT | 2.x |
| Flutter | flutter.dev | github.com/flutter/flutter | BSD-3 | 3.x |
| Ollama | ollama.com | github.com/ollama/ollama | MIT | 0.5+ |

### Appendix B: Bangladesh Implementation Partners

| Partner | Type | Location | Specialization |
|---|---|---|---|
| **Metamorphosis Ltd.** | Odoo Silver Partner | Dhaka, Bangladesh | First BD Odoo partner (2017); bKash, SSLCOMMERZ, SMS modules |
| **Xsellence Bangladesh Ltd.** | Odoo Gold Partner | Dhaka, Bangladesh | Only Gold Partner in BD; enterprise implementations |
| **Ergo Ventures** | Odoo Partner | Dhaka, Bangladesh | SME implementations |
| **VS ONE Bangladesh** | Odoo Partner | Dhaka, Bangladesh | Additional BD partner |
| **Open Source Integrators** | OCA Contributor (USA) | Remote | Founded OCA/field-service project; 2x Partner of Year |

### Appendix C: Key OCA Repository Links

| Repository | GitHub URL | Module Count |
|---|---|---|
| OCA/field-service | github.com/OCA/field-service | 33 |
| OCA/helpdesk | github.com/OCA/helpdesk | 28 |
| OCA/management-system | github.com/OCA/management-system | 33 |
| OCA/hr | github.com/OCA/hr | 50+ |
| OCA/payroll | github.com/OCA/payroll | 15+ |
| OCA/operating-unit | github.com/OCA/operating-unit | 15+ |
| OCA/reporting-engine | github.com/OCA/reporting-engine | 20+ |
| OCA/mis-builder | github.com/OCA/mis-builder | 5+ |
| OCA/dms | github.com/OCA/dms | 5+ |
| OCA/account-financial-tools | github.com/OCA/account-financial-tools | 40+ |
| OCA/stock-logistics-barcode | github.com/OCA/stock-logistics-barcode | 10+ |

### Appendix D: Glossary

| Term | Definition |
|---|---|
| **Odoo CE** | Odoo Community Edition — free, open-source ERP under LGPL v3 |
| **OCA** | Odoo Community Association — non-profit maintaining 1,000+ free Odoo modules |
| **OWL** | Odoo Web Library — TypeScript-based frontend framework |
| **JSON-2 API** | Odoo 19's new standard API replacing XML-RPC |
| **LGPL v3** | GNU Lesser General Public License — allows commercial use without disclosing proprietary code |
| **AGPL-3** | GNU Affero General Public License — requires source disclosure for network services |
| **l10n_bd** | Odoo localization module for Bangladesh |
| **PgBouncer** | PostgreSQL connection pooler for high-concurrency deployments |
| **VROOM** | Vehicle Routing Open-source Optimization Machine |
| **OSRM** | Open Source Routing Machine — road network routing engine |
| **Mushak 6.3** | Bangladesh NBR-mandated VAT invoice format |
| **BEFTN** | Bangladesh Electronic Funds Transfer Network — salary payment system |
| **Traccar** | Open-source GPS tracking platform |
| **n8n** | Open-source workflow automation platform |
| **Keycloak** | Open-source identity and access management (SSO) |
| **Novu** | Open-source notification infrastructure |
| **Flutter** | Google's cross-platform mobile app development framework |
| **Ollama** | Local LLM server for running AI models on-premises |

---

**DOCUMENT END**

---

*1000FiX Services Limited — ERP Implementation Strategy*
*Version 1.0 | March 18, 2026 | CONFIDENTIAL*
*Reference: 1000FIX-ERP-STRATEGY-2026-001*

*586/1 (4th Floor), Begum Rokeya Sarani, Shewrapara, Mirpur, Dhaka-1216, Bangladesh*
*Hotline: 16743 | Phone: 09644-300600 | Email: info@1000fix.com*
*ISO 9001:2015 Certified — Bangladesh's Largest After-Sales Service Provider*
