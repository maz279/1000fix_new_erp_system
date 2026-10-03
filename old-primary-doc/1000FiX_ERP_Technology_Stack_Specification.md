# Technology Stack Specification Document

# Comprehensive ERP System & Smart Portal Suite

# For 1000FiX Services Limited

---

| **Document Information** | |
|---|---|
| **Document Title** | Technology Stack Specification — Comprehensive ERP System & Smart Portal Suite |
| **Organization** | 1000FiX Services Limited |
| **Document Version** | 1.0 |
| **Date** | March 18, 2026 |
| **Reference Number** | 1000FIX-ERP-TECHSTACK-2026-001 |
| **Related Documents** | 1000FIX-ERP-RFP-2026-001, 1000FIX-ERP-BRD-2026-001, 1000FIX-ERP-URD-2026-001, 1000FIX-ERP-STRATEGY-2026-001 |
| **Classification** | CONFIDENTIAL — Technical Specification Document |

---

**CONFIDENTIALITY NOTICE**

This Technology Stack Specification document and all accompanying materials are the confidential property of 1000FiX Services Limited. The information contained herein is intended solely for the use of authorized implementation teams, technology vendors, and internal stakeholders involved in the ERP implementation project. Recipients must not disclose, reproduce, or distribute any part of this document without the prior written consent of 1000FiX Services Limited.

---

## REVISION HISTORY

| Version | Date | Author | Description |
|---|---|---|---|
| 1.0 | March 18, 2026 | 1000FiX IT Team | Initial release — comprehensive technology stack specification |

---

## DOCUMENT APPROVALS

| Role | Name | Signature | Date |
|---|---|---|---|
| Chief Technology Officer | | | |
| Operations Director | | | |
| Finance Director | | | |
| IT Administrator | | | |
| Implementation Vendor PM | | | |

---

## NOTATION AND CONVENTIONS

### Requirement ID Prefixes

| Prefix | Source | Category |
|---|---|---|
| SRM-nnn | RFP §5.1 | Service & Repair Management |
| FSM-nnn | RFP §5.2 | Field Service Management |
| INV-nnn | RFP §5.3 | Inventory & Spare Parts Management |
| CRM-nnn | RFP §5.4 | Customer Relationship Management |
| FIN-nnn | RFP §5.5 | Financial Management & Accounting |
| HRM-nnn | RFP §5.6 | Human Resource Management & Payroll |
| CWM-nnn | RFP §5.7 | Contract & Warranty Management |
| SCM-nnn | RFP §5.8 | Procurement & Supply Chain Management |
| BI-nnn | RFP §5.9 | Reporting & Business Intelligence |
| DMS-nnn | RFP §5.10 | Document Management System |
| QMS-nnn | RFP §5.11 | Quality Management System |
| CSP-nnn | RFP §6.1 | Customer Self-Service Portal |
| TMP-nnn | RFP §6.2 | Technician Mobile Portal |
| AOP-nnn | RFP §6.3 | Admin Operations Portal |
| B2B-nnn | RFP §6.4 | Corporate B2B Portal |
| VPP-nnn | RFP §6.5 | Vendor & Partner Portal |
| ABD-nnn | RFP §6.6 | Analytics & BI Dashboard |
| TECH-nnn | RFP §7 | Technical Requirements |
| INT-nnn | RFP §8 | Integration Requirements |
| MIG-nnn | RFP §9 | Data Migration Requirements |
| SEC-nnn | RFP §10 | Security & Compliance Requirements |
| TRN-nnn | RFP §12 | Training & Change Management |

### Layer Codes

| Code | Description |
|---|---|
| L1 | Odoo 19 CE native module (zero license cost) |
| L2 | OCA community module (zero license cost, peer-reviewed) |
| L3 | Free third-party marketplace module |
| L4 | Complementary open-source tool (zero license cost) |
| L5 | Custom development (development cost only) |

### Priority Levels

| Code | Meaning |
|---|---|
| P1 | Must-Have — Required for go-live |
| P2 | Important — Required within 6 months of go-live |
| P3 | Nice-to-Have — Future enhancement |

### Vendor Response Codes

| Code | Meaning |
|---|---|
| S | Supported out of the box (standard feature) |
| C | Supported with configuration (no custom code) |
| D | Requires custom development |
| T | Supported via third-party integration |
| N | Not supported |

---

## TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Layer 1 — Odoo 19 CE Foundation](#3-layer-1--odoo-19-ce-foundation)
4. [Layer 2 — OCA Module Ecosystem](#4-layer-2--oca-module-ecosystem)
5. [Layer 3 — Free Third-Party Modules](#5-layer-3--free-third-party-modules)
6. [Layer 4 — Complementary Open-Source Tools](#6-layer-4--complementary-open-source-tools)
7. [Layer 5 — Custom Development](#7-layer-5--custom-development)
8. [Requirement-to-Technology Traceability Matrix](#8-requirement-to-technology-traceability-matrix)
9. [Integration Architecture](#9-integration-architecture)
10. [Security Architecture](#10-security-architecture)
11. [Infrastructure & Performance](#11-infrastructure--performance)
12. [Localization & Accessibility](#12-localization--accessibility)
13. [Smart Portal Suite Technology](#13-smart-portal-suite-technology)
14. [Phased Technology Deployment](#14-phased-technology-deployment)
15. [Compliance Traceability Matrix](#15-compliance-traceability-matrix)
16. [Cost Breakdown](#16-cost-breakdown)
17. [Risk Register](#17-risk-register)
18. [Appendices](#18-appendices)

---

## 1. EXECUTIVE SUMMARY

### 1.1 Purpose and Scope

This Technology Stack Specification document defines every technology component, its version, license, role, configuration, and traceability to specific requirements for the 1000FiX ERP System and Smart Portal Suite implementation. It serves as the definitive technical reference for:

- **Implementation teams** — to understand exactly what to deploy, configure, and develop
- **Management** — to understand how technology investments map to business outcomes
- **Quality assurance** — to verify that every RFP, BRD, and URD requirement has a technology solution
- **Operations** — to plan infrastructure, security, and ongoing maintenance

The technology stack follows a **zero-license-cost** open-source strategy using Odoo 19 Community Edition as the ERP backbone, augmented by 94+ OCA community modules, free third-party integrations, 10+ complementary open-source tools, and 20 custom-developed modules. This approach delivers 100% coverage of all 405 requirements defined across the RFP (1000FIX-ERP-RFP-2026-001), BRD (1000FIX-ERP-BRD-2026-001), and URD (1000FIX-ERP-URD-2026-001) documents.

### 1.2 Architecture Overview — The 5-Layer Stack

```
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 5: CUSTOM DEVELOPMENT (20 Modules)                          │
│  Bangladesh-specific: Mushak VAT, BEFTN payroll, brand warranty    │
│  Custom Flutter mobile app, AI dispatch, Bengali NLP chatbot       │
│  Coverage: ~15% of requirements │ Cost: Dev only │ 80-115 PW       │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 4: COMPLEMENTARY OPEN SOURCE TOOLS (Zero License)          │
│  Metabase (BI) · Grafana (Monitoring) · Traccar (GPS)             │
│  n8n (Automation) · VROOM/OSRM (Routing) · Keycloak (SSO)        │
│  Mayan EDMS (Documents) · Novu (Notifications) · Flutter (Mobile) │
│  Coverage: ~10% of requirements │ License: $0                      │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 3: FREE THIRD-PARTY MODULES                                │
│  SSLCOMMERZ · bKash · Nagad · SMS Gateways · WhatsApp Connector   │
│  Coverage: ~5% of requirements │ License: $0                       │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 2: OCA FREE MODULES (94+ modules across 11 repositories)   │
│  Field Service (33) · Helpdesk (28) · Quality/ISO (33)            │
│  Payroll · Multi-Branch · DMS · BI Reporting · HR · Barcode       │
│  Coverage: ~30% of requirements │ License: $0                      │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 1: ODOO 19 CE (Zero License — LGPL v3)                    │
│  CRM · Sales · Inventory · Accounting · HR · Purchase             │
│  Website/Portal · Project · Attendance · Leave · Fleet · Calendar │
│  Coverage: ~40% of requirements │ License: $0                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.3 Key Technology Decisions Summary

| Decision | Technology Selected | License | Replaces | Key Requirements |
|---|---|---|---|---|
| ERP Backbone | Odoo 19 CE (v19.0/19.1) | LGPL v3 ($0) | Manual processes, spreadsheets | All functional modules |
| Database | PostgreSQL 16 | PostgreSQL License ($0) | Fragmented data stores | TECH-001, shared with Next.js platform |
| Web Platform Integration | Next.js 15 + Payload CMS 3 | MIT ($0) | WordPress website | CON-03 (cannot be replaced), INT-001 |
| Technician Mobile App | Custom Flutter App | BSD-3 ($0) | Phone-based manual dispatch | TMP-001 to TMP-017, FSM-013 to FSM-026 |
| Field Service Management | OCA/field-service (33 modules) | LGPL/AGPL ($0) | Enterprise FSM module | SRM, FSM, CWM requirements |
| Helpdesk & Tickets | OCA/helpdesk (28 modules) | LGPL/AGPL ($0) | Enterprise Helpdesk | SRM-001 to SRM-020 |
| Quality Management | OCA/management-system (33 modules) | LGPL/AGPL ($0) | No existing system | QMS-001 to QMS-008 |
| Multi-Branch Management | OCA/operating-unit (15+ modules) | LGPL ($0) | Fragmented operations | All branch-level requirements |
| Business Intelligence | Metabase (v0.52+) | AGPL-3 ($0) | No analytics capability | BI-001 to BI-014, ABD-001 to ABD-010 |
| Real-Time Monitoring | Grafana (v11.x) | AGPL-3 ($0) | No monitoring | ABD-002, ABD-010 |
| GPS Tracking | Traccar (v6.x) | Apache-2.0 ($0) | No tracking system | FSM-003, FSM-027, INT-018 |
| Route Optimization | VROOM + OSRM | BSD-2 ($0) | No route optimization | FSM-004, INT-019 |
| Workflow Automation | n8n (v1.x) | Fair-code ($0 self-hosted) | Manual processes | All notification/automation workflows |
| SSO / Identity | Keycloak (v26.x) | Apache-2.0 ($0) | No SSO | SEC-001 to SEC-007, INT-006 |
| Document Management | Mayan EDMS (v4.10) + OCA/dms | Apache-2.0 ($0) | Paper/email-based | DMS-001 to DMS-008 |
| Notifications | Novu (v2.x) | MIT ($0) | No unified notifications | INT-013 to INT-016, CSP-014, TMP-016 |
| Payment Gateways | SSLCOMMERZ + bKash + Nagad modules | Various ($0) | Manual payment collection | INT-007 to INT-012 |
| Bengali Chatbot (Phase 6) | Ollama + Qwen3-8B + LangChain | MIT/Apache ($0) | No chatbot | INT-022, CSP-013 |
| Bangladesh VAT | Custom Mushak 6.3 Module | Proprietary (dev cost) | Manual VAT | FIN-024 to FIN-027 |
| Bangladesh Payroll | Custom Payroll Module | Proprietary (dev cost) | Manual spreadsheet payroll | HRM-017 to HRM-023 |

### 1.4 Compliance Statement

Every technology component specified in this document has been selected to satisfy one or more requirements from:

- **RFP** (1000FIX-ERP-RFP-2026-001) — 405 requirements across 22 categories
- **BRD** (1000FIX-ERP-BRD-2026-001) — Detailed business rules, NFRs, constraints, and dependencies
- **URD** (1000FIX-ERP-URD-2026-001) — 20 user roles, UI/UX specifications, and acceptance criteria

The technology selection follows the evaluation hierarchy defined in the Implementation Strategy (1000FIX-ERP-STRATEGY-2026-001):

1. Does Odoo 19 CE handle it natively? → Use L1
2. Does OCA have a quality module? → Use L2
3. Is there a free third-party module? → Use L3
4. Is there a standalone open-source tool? → Use L4
5. Custom development required → Use L5

### 1.5 Budget Summary

| Category | 3-Year Cost | Notes |
|---|---|---|
| **Software Licensing** | **$0** | All open-source / free licenses |
| Implementation & Custom Development | $111,000 – $200,000 | 20 custom modules + configuration |
| Infrastructure / Hosting | $16,740 – $29,520 | DigitalOcean Singapore |
| Third-Party APIs | $16,200 – $37,800 | Google Maps, WhatsApp, SMS, Firebase, Cloudinary |
| Training | $8,000 – $15,000 | Bengali + English materials |
| Support & Maintenance | $30,000 – $60,000 | Years 2-3 |
| **3-Year Total Cost of Ownership** | **$181,940 – $342,320** | Within RFP budget of $150,000 – $350,000 |

---

## 2. SYSTEM ARCHITECTURE

### 2.1 High-Level System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           USER ACCESS LAYER                                      │
│                                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Customer │ │Technician│ │  Admin   │ │Corporate │ │ Vendor/  │ │Analytics │ │
│  │  Portal  │ │Mobile App│ │Operations│ │B2B Portal│ │ Partner  │ │Dashboard │ │
│  │(Next.js) │ │(Flutter) │ │(Odoo CE) │ │(Next.js) │ │(Odoo CE) │ │(Metabase)│ │
│  │CSP-001–  │ │TMP-001– │ │AOP-001– │ │B2B-001– │ │VPP-001– │ │ABD-001– │ │
│  │CSP-017   │ │TMP-017   │ │AOP-012   │ │B2B-010   │ │VPP-008   │ │ABD-010   │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │
└───────┼────────────┼────────────┼────────────┼────────────┼────────────┼────────┘
        │            │            │            │            │            │
┌───────┼────────────┼────────────┼────────────┼────────────┼────────────┼────────┐
│       ▼            ▼            ▼            ▼            ▼            ▼        │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    KEYCLOAK SSO (SEC-001 to SEC-007)                    │    │
│  │          SAML 2.0 / OAuth 2.0 / OpenID Connect / MFA                   │    │
│  └─────────────────────────────┬───────────────────────────────────────────┘    │
│                                │                                                │
│  ┌─────────────────────────────▼───────────────────────────────────────────┐    │
│  │                    NGINX REVERSE PROXY + WAF                            │    │
│  │         TLS 1.2+ Termination · Rate Limiting · Load Balancing           │    │
│  │                    (SEC-009, TECH-009)                                   │    │
│  └──────────┬──────────────────┬──────────────────────┬────────────────────┘    │
│             │                  │                      │                          │
│  ┌──────────▼──────────┐ ┌────▼────────────────┐ ┌───▼─────────────────┐       │
│  │   ODOO 19 CE        │ │ NEXT.JS 15 PLATFORM │ │ OPEN SOURCE TOOLS   │       │
│  │   ERP BACKBONE      │ │ (CON-03 Mandate)    │ │                     │       │
│  │                     │ │                     │ │ Metabase (BI)       │       │
│  │ • CRM, Sales, INV  │ │ • Payload CMS 3     │ │ Grafana (Monitor)   │       │
│  │ • Accounting, HR   │ │ • React 19          │ │ Traccar (GPS)       │       │
│  │ • Purchase, Fleet  │ │ • Tailwind CSS      │ │ n8n (Automation)    │       │
│  │ • OCA field-service │ │ • Socket.io         │ │ VROOM/OSRM (Route) │       │
│  │ • OCA helpdesk     │ │ • BullMQ            │ │ Mayan EDMS (Docs)   │       │
│  │ • OCA mgmt-system  │ │ • Drizzle ORM       │ │ Novu (Notify)       │       │
│  │ • OCA operating-   │ │                     │ │ Ollama (AI/LLM)     │       │
│  │   unit (branches)  │ │                     │ │                     │       │
│  │ • Custom modules   │ │                     │ │                     │       │
│  │   (L5: CD-01–20)   │ │                     │ │                     │       │
│  │                     │ │                     │ │                     │       │
│  │ JSON-2 API ◄──────►│ │ REST API ◄─────────►│ │ REST/WS APIs        │       │
│  │ (TECH-036)         │ │ (INT-001 to INT-006)│ │                     │       │
│  └──────────┬──────────┘ └──────────┬──────────┘ └──────────┬──────────┘       │
│             │                       │                       │                   │
│  ┌──────────▼───────────────────────▼───────────────────────▼──────────┐        │
│  │                    DATA & STORAGE LAYER                             │        │
│  │                                                                     │        │
│  │  ┌──────────────────┐  ┌─────────────┐  ┌────────────────────┐     │        │
│  │  │ PostgreSQL 16    │  │ Redis 7     │  │ File Storage       │     │        │
│  │  │ Primary + Read   │  │ Session     │  │ Mayan EDMS + Odoo  │     │        │
│  │  │ Replica          │  │ Cache +     │  │ Cloudinary (media) │     │        │
│  │  │ (PgBouncer pool) │  │ Job Queue   │  │ (INT-030)          │     │        │
│  │  └──────────────────┘  └─────────────┘  └────────────────────┘     │        │
│  └─────────────────────────────────────────────────────────────────────┘        │
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────┐       │
│  │                    EXTERNAL INTEGRATIONS                             │       │
│  │                                                                      │       │
│  │  bKash · Nagad · SSLCOMMERZ │ SMS Gateway · WhatsApp · Firebase     │       │
│  │  (INT-007 to INT-012)       │ (INT-013 to INT-016)                  │       │
│  │                              │                                       │       │
│  │  Google Maps · OSRM         │ Biometric Devices · BEFTN Bank Files  │       │
│  │  (INT-018 to INT-021)       │ (INT-028, HRM-021)                    │       │
│  └──────────────────────────────────────────────────────────────────────┘       │
│                                                                                 │
│                    INFRASTRUCTURE: DigitalOcean Singapore (TECH-008)             │
│                    Docker / K3s Containers (TECH-010)                            │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Deployment Architecture

```
┌────────────────── DigitalOcean Singapore Region (TECH-008) ──────────────────┐
│                                                                               │
│  ┌─────────────── Docker Compose / K3s Cluster (TECH-010) ───────────────┐   │
│  │                                                                        │   │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │   │
│  │  │  NGINX Reverse Proxy + Load Balancer (TECH-009)                 │  │   │
│  │  │  • TLS 1.2+ termination (SEC-009)                               │  │   │
│  │  │  • ModSecurity WAF rules                                        │  │   │
│  │  │  • Rate limiting for API endpoints                              │  │   │
│  │  │  • Static asset caching                                         │  │   │
│  │  └──────────────────────────────────────────────────────────────────┘  │   │
│  │                                                                        │   │
│  │  ┌───────────────────┐  ┌───────────────────┐                         │   │
│  │  │ Odoo App Server 1 │  │ Odoo App Server 2 │  (TECH-004, TECH-014)  │   │
│  │  │ 8 vCPU / 16GB RAM │  │ 8 vCPU / 16GB RAM │                        │   │
│  │  │ 10-12 workers each│  │ 10-12 workers each│                        │   │
│  │  │ Odoo 19 CE + OCA  │  │ Odoo 19 CE + OCA  │                        │   │
│  │  │ + Custom modules  │  │ + Custom modules   │                        │   │
│  │  └─────────┬─────────┘  └─────────┬─────────┘                        │   │
│  │            │                       │                                   │   │
│  │  ┌─────────▼───────────────────────▼─────────┐                        │   │
│  │  │        PgBouncer Connection Pooler         │                        │   │
│  │  │        Max 1,000 connections               │                        │   │
│  │  └─────────┬───────────────────────┬─────────┘                        │   │
│  │            │                       │                                   │   │
│  │  ┌─────────▼─────────┐  ┌─────────▼─────────┐                        │   │
│  │  │ PostgreSQL 16     │  │ PostgreSQL 16      │                        │   │
│  │  │ PRIMARY           │  │ READ REPLICA       │                        │   │
│  │  │ 8 vCPU / 32GB RAM│  │ 8 vCPU / 32GB RAM │  (for Metabase/BI)    │   │
│  │  │ 500GB SSD         │  │ 500GB SSD          │                        │   │
│  │  │ WAL Streaming ───►│  │ ◄── Replication    │                        │   │
│  │  └───────────────────┘  └────────────────────┘                        │   │
│  │                                                                        │   │
│  │  ┌───────────────────┐  ┌───────────────────┐                         │   │
│  │  │ Redis 7           │  │ Supporting Services│                         │   │
│  │  │ Session store     │  │ Server             │                         │   │
│  │  │ Background queue  │  │ 8 vCPU / 16GB RAM │                         │   │
│  │  │ Pub/sub messaging │  │                    │                         │   │
│  │  └───────────────────┘  │ • Metabase (BI)   │                         │   │
│  │                          │ • Grafana (Monitor)│                         │   │
│  │                          │ • Traccar (GPS)    │                         │   │
│  │                          │ • n8n (Automation) │                         │   │
│  │                          │ • Keycloak (SSO)   │                         │   │
│  │                          │ • VROOM/OSRM       │                         │   │
│  │                          │ • Mayan EDMS       │                         │   │
│  │                          │ • Novu (Notify)    │                         │   │
│  │                          └───────────────────┘                         │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │  Backup Storage (SEC-012)                                              │   │
│  │  • Daily automated backups — 30 day retention                          │   │
│  │  • Weekly backups — 1 year retention                                   │   │
│  │  • Encrypted backup storage (AES-256)                                  │   │
│  │  • Point-in-time recovery via WAL archiving                            │   │
│  │  RPO < 1 hour │ RTO < 4 hours (TECH-007)                              │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  Cloudflare CDN — DDoS protection, static asset caching for portals          │
└───────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Security Architecture

```
┌─────────────────────── SECURITY ARCHITECTURE ──────────────────────────┐
│                                                                         │
│  AUTHENTICATION LAYER                                                   │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  KEYCLOAK v26.x (SEC-001, SEC-002, SEC-003)                      │  │
│  │  • SAML 2.0 / OAuth 2.0 / OpenID Connect (SSO for all systems)  │  │
│  │  • RBAC: 20 roles with field-level granularity (SEC-001)         │  │
│  │  • MFA: TOTP mandatory for admin/finance users (SEC-002)         │  │
│  │  • Password policies: length, complexity, expiry, history (SEC-004)│  │
│  │  • Session mgmt: timeout, concurrent limits, forced logout (SEC-005)│ │
│  │  • IP-based restrictions for admin portals (SEC-006)             │  │
│  │  • Branch-level data isolation via operating-unit (SEC-007)      │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  NETWORK SECURITY LAYER                                                 │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  NGINX + Cloudflare                                               │  │
│  │  • TLS 1.2+ for all data in transit (SEC-009)                    │  │
│  │  • ModSecurity WAF with OWASP Core Rule Set                      │  │
│  │  • Rate limiting: API 100 req/min, portal 500 req/min            │  │
│  │  • DDoS protection via Cloudflare                                │  │
│  │  • VPC private networking between all services                   │  │
│  │  • Firewall: only ports 80, 443 exposed externally               │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  DATA SECURITY LAYER                                                    │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  • AES-256 encryption at rest — PostgreSQL + backup (SEC-008)    │  │
│  │  • Database encryption with managed key rotation (SEC-010)       │  │
│  │  • PII masking for non-production environments (SEC-011)         │  │
│  │  • Encrypted backup storage (SEC-012)                            │  │
│  │  • ClamAV malware scanning on file uploads (SEC-013)             │  │
│  │  • Data retention policies configurable per type (SEC-022)       │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  AUDIT & COMPLIANCE LAYER                                               │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  • Immutable audit trail: who, what, when, before/after (SEC-014)│  │
│  │  • Tamper-protected audit logs — append-only (SEC-015)           │  │
│  │  • ISO 27001 aligned security controls (SEC-016)                 │  │
│  │  • Bangladesh ICT Act 2006 compliance (SEC-018)                  │  │
│  │  • Bangladesh Digital Security Act 2018 compliance               │  │
│  │  • Annual penetration testing (SEC-020)                          │  │
│  │  • Vulnerability management and patching (SEC-021)               │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.4 Data Flow Architecture — Critical Workflows

#### 2.4.1 Service Order Lifecycle (SRM-001 → SRM-003 → FIN-010)

```
Customer                Next.js Portal         Odoo 19 CE            n8n/Novu           Technician
   │                         │                      │                    │                  │
   │──Book service──────────►│                      │                    │                  │
   │                         │──POST /json/2/       │                    │                  │
   │                         │  service.order ──────►│                    │                  │
   │                         │                      │──Create SO─────────│                  │
   │                         │                      │──Webhook: ─────────►│                  │
   │                         │                      │  order.created     │──SMS+WhatsApp───►│ Customer
   │                         │                      │                    │──Push notify────►│ Technician
   │                         │                      │──AI Dispatch ──────│                  │
   │                         │                      │  (VROOM/OSRM)     │                  │
   │                         │                      │──Assign tech───────│                  │
   │                         │                      │──Webhook: ─────────►│                  │
   │                         │                      │  tech.dispatched   │──SMS w/ETA──────►│ Customer
   │                         │                      │                    │                  │
   │                         │                      │◄──Job complete─────│                  │◄──Complete
   │                         │                      │──Auto-invoice──────│                  │
   │                         │                      │──Webhook: ─────────►│                  │
   │                         │                      │  invoice.created   │──Payment link───►│ Customer
   │──Pay via bKash──────────►│                      │                    │                  │
   │                         │──POST /json/2/       │                    │                  │
   │                         │  payment.confirm ────►│                    │                  │
   │                         │                      │──Close SO──────────│                  │
   │                         │                      │──Webhook: ─────────►│──Receipt SMS────►│ Customer
   │                         │                      │  order.closed      │                  │
```

#### 2.4.2 Real-Time GPS Tracking (FSM-003, FSM-027)

```
Technician Phone        Traccar Server         Odoo 19 CE           Next.js Portal        Customer
   │                         │                      │                    │                  │
   │──GPS coords (30s)──────►│                      │                    │                  │
   │  (Traccar Client app)  │──Store position───────│                    │                  │
   │                         │──REST API update─────►│                    │                  │
   │                         │                      │──Update tech loc───│                  │
   │                         │                      │                    │                  │
   │                         │                      │◄──GET /json/2/─────│◄──View tracking──│
   │                         │                      │  technician/{id}/  │   page           │
   │                         │                      │  location ─────────►│──Render map─────►│
   │                         │                      │                    │  with ETA         │
   │                         │──WebSocket stream────►│  (real-time)       │                  │
```

#### 2.4.3 Warranty Claim Automation (CWM-009 → CWM-014)

```
Technician              Odoo 19 CE             n8n Workflow          Brand Partner
   │                         │                      │                    │
   │──Complete warranty──────►│                      │                    │
   │  repair + photos        │──Auto-validate────────│                    │
   │                         │  warranty status      │                    │
   │                         │──Auto-create claim────│                    │
   │                         │  (within 24 hours)    │                    │
   │                         │──Attach docs: ────────│                    │
   │                         │  photos, diag report  │                    │
   │                         │  parts list, serial#  │                    │
   │                         │──Webhook: claim ──────►│                    │
   │                         │  .created             │──Format claim per──│
   │                         │                      │  brand template    │
   │                         │                      │──Submit to brand───►│
   │                         │                      │  partner portal    │
   │                         │                      │                    │──Approve/Reject
   │                         │◄─────────────────────│◄──Status webhook───│
   │                         │──Update claim status──│                    │
   │                         │──Reconcile payment────│                    │
   │                         │  (FIN-034)            │                    │
```

#### 2.4.4 Daily Route Optimization (FSM-004, INT-019)

```
n8n Scheduler           Odoo 19 CE             VROOM/OSRM            Technician App
(5:00 AM daily)              │                      │                    │
   │                         │                      │                    │
   │──Trigger route ─────────►│                      │                    │
   │  optimization           │──Fetch tomorrow's────│                    │
   │                         │  unassigned jobs      │                    │
   │                         │──Fetch technician─────│                    │
   │                         │  skills, zones, van   │                    │
   │                         │  stock, availability  │                    │
   │                         │──Send to ─────────────►│                    │
   │                         │  VROOM API            │──Solve VRP────────│
   │                         │                      │  (milliseconds)   │
   │                         │◄──Optimized routes────│                    │
   │                         │  + assignments        │                    │
   │                         │──Update dispatch──────│                    │
   │                         │  board                │                    │
   │                         │──Push routes via──────│───────────────────►│
   │                         │  Firebase             │                    │──Display job
   │                         │                      │                    │  queue + nav
```

#### 2.4.5 Multi-Channel Notification Delivery (INT-013 to INT-016)

```
Odoo 19 CE              n8n Workflow            Novu                  Channels
   │                         │                      │                    │
   │──Webhook event──────────►│                      │                    │
   │  (e.g., status_changed) │──Determine template───│                    │
   │                         │  + channels + locale  │                    │
   │                         │──Trigger Novu─────────►│                    │
   │                         │                      │──SMS (MuthoSMS)───►│ Customer phone
   │                         │                      │──WhatsApp──────────►│ Customer WhatsApp
   │                         │                      │──Email (SMTP)──────►│ Customer email
   │                         │                      │──Push (Firebase)───►│ Technician app
   │                         │                      │──In-app notify─────►│ Odoo CE backend
   │                         │                      │                    │
   │                         │                      │──Delivery status───►│ n8n → Odoo
   │                         │                      │  (callback)         │ (audit trail)
```

### 2.5 Technology Selection Principles

The following principles govern all technology decisions in this stack, in order of priority:

| # | Principle | Rationale | Key Requirements |
|---|---|---|---|
| 1 | **Zero License Cost** | Maximize budget for implementation quality; $0 software licensing | RFP Budget §15 ($150K-$350K TCO) |
| 2 | **API-First Architecture** | All systems must communicate via documented APIs | TECH-036, INT-001 to INT-006 |
| 3 | **Offline-First Mobile** | Technician app must operate without internet for 24+ hours | TECH-020, FSM-014, URD §13.6 |
| 4 | **PostgreSQL as Shared Backbone** | Single database technology across ERP and web platform | CON-03 (Next.js uses PostgreSQL 16) |
| 5 | **Bengali-First Localization** | All field-facing interfaces must be Bengali-primary | TECH-025, URD §13.1 |
| 6 | **Container-Based Deployment** | Reproducible, scalable infrastructure | TECH-010, TECH-004 |
| 7 | **Event-Driven Integration** | Webhooks + n8n for real-time cross-system communication | TECH-017, INT-005 |
| 8 | **Security by Default** | Encryption, MFA, RBAC, audit trails enabled from day one | SEC-001 to SEC-022 |

---

## 3. LAYER 1 — ODOO 19 CE FOUNDATION

### 3.1 Platform Specifications

| Attribute | Specification | Requirement Mapping |
|---|---|---|
| **Product** | Odoo Community Edition | — |
| **Version** | 19.0 (Released October 2025), Patch 19.1 (January 2026) | — |
| **License** | LGPL v3 (GNU Lesser General Public License) | $0 license cost |
| **Runtime** | Python 3.12+ | — |
| **Database** | PostgreSQL 16 (shared technology with Next.js platform) | CON-03, TECH-001 |
| **Frontend Framework** | OWL (Odoo Web Library) — TypeScript-based, component-driven | TECH-018 |
| **Primary API** | JSON-2 API (new in v19 — RESTful, token-authenticated) | TECH-036, INT-001 |
| **Legacy APIs** | JSON-RPC (maintained), XML-RPC (deprecated in v22+) | — |
| **PWA Support** | Yes (v19 improvements — responsive mobile web) | TECH-019 (secondary to Flutter app) |
| **Multi-Language** | Full i18n framework with .po translation files | TECH-025, TECH-026 |
| **Multi-Currency** | Native support (BDT primary, USD secondary) | TECH-030, FIN-006 |
| **Source Code** | Full access — forkable, modifiable, redistributable | TECH-037 |
| **Community** | 15M+ downloads, 2,000+ community contributors | — |

### 3.2 Odoo 19 CE Modules Deployed

| # | Module (Technical Name) | Function | BRD Modules Served | Key Requirements | Phase |
|---|---|---|---|---|---|
| 1 | `crm` | Lead & pipeline management, customer 360 | CRM | CRM-001, CRM-003, CRM-014 to CRM-018 | 1 |
| 2 | `sale` | Quotations, sales orders, pricing, discounts | CRM, SRM | SRM-031 to SRM-037, CRM-017 | 1 |
| 3 | `stock` | Multi-warehouse inventory, stock moves, reorder rules, valuation | INV | INV-001 to INV-024 (partial) | 1 |
| 4 | `account` | Chart of accounts, GL, journal entries, invoicing, bank recon, tax | FIN | FIN-001 to FIN-035 (partial) | 3 |
| 5 | `hr` | Employee master records, org hierarchy, departments, skills | HRM | HRM-001 to HRM-005 | 5 |
| 6 | `hr_attendance` | Check-in/out tracking, attendance records | HRM | HRM-012 | 5 |
| 7 | `hr_holidays` | Leave types, requests, approvals, balance tracking | HRM | HRM-014, HRM-015 | 5 |
| 8 | `purchase` | RFQs, purchase orders, supplier management, 3-way matching | SCM | SCM-001 to SCM-012 (partial) | 3 |
| 9 | `project` | Task management, Kanban boards, basic tracking | SRM, FSM | SRM-003 (workflow tracking) | 1 |
| 10 | `website` | Portal framework, customer self-service base | VPP | VPP-001 to VPP-008 (base portal) | 4 |
| 11 | `discuss` | Internal messaging, channels, mail integration | SRM, FSM | SRM-012, FSM-023 (internal comms) | 1 |
| 12 | `contacts` | Contact management, companies, addresses | CRM | CRM-001, CRM-015 | 1 |
| 13 | `calendar` | Event management, scheduling | FSM, HRM | FSM-002, HRM-011 | 1 |
| 14 | `fleet` | Vehicle management for technician vans | FSM | FSM-008 (van/mobile stock vehicles) | 2 |

### 3.3 Bangladesh Localization (l10n_bd)

#### 3.3.1 Available in l10n_bd Module (L1/L2)

| Feature | Status | Requirement |
|---|---|---|
| Bangladesh Chart of Accounts | Available | FIN-001 |
| VAT Rate (15% standard) | Available | FIN-024 |
| BDT Currency (৳) with lakh format | Available | TECH-030 |
| Bengali language base translations | Available (partial) | TECH-025 |
| Bangladesh fiscal year (July–June) | Configurable | FIN-009 |

#### 3.3.2 Gaps Requiring Custom Development (L5)

| Feature | Gap | Custom Module | Requirement |
|---|---|---|---|
| Mushak 6.3 Invoice Format | Not available — requires NBR-specific template | CD-02 | FIN-026, FIN-027 |
| e-VAT Filing | Not available — Bangladesh NBR electronic submission | CD-02 (extension) | FIN-026 |
| Income Tax Slabs | Not available — Bangladesh-specific tax computation | CD-03 | HRM-020 |
| BEFTN File Generation | Not available — Bangladesh bank salary transfer format | CD-03 (extension) | HRM-021 |
| NID Validation | Not available — 10/17-digit Bangladesh National ID format | CD-19 | BRD BRU-FIN-02 |
| Bangladesh Address Format | Partial — needs 8 divisions, 64 districts, upazilas | CD-12 | TECH-031 |

### 3.4 Scalability Configuration

To meet TECH-014 (500+ concurrent internal users) and TECH-015 (50,000+ concurrent portal users):

| Component | Configuration | Requirement Mapping |
|---|---|---|
| **Odoo Workers** | 20-24 workers across 2 app servers (10-12 per server) | TECH-014 |
| **Cron Workers** | 2 dedicated cron workers per server | TECH-016 (batch processing) |
| **PgBouncer** | Connection pooling — max 1,000 PostgreSQL connections | TECH-014, TECH-015 |
| **Read Replica** | PostgreSQL streaming replication for BI/reporting queries | TECH-013, BI-001 to BI-014 |
| **Redis** | Session store + background job queue + pub/sub messaging | TECH-017 (real-time sync < 5s) |
| **Nginx Caching** | Static assets cached at proxy; API response caching for portal | TECH-011 (page load < 3s) |
| **CDN** | Cloudflare for portal static assets and DDoS protection | TECH-015 (50K+ portal users) |
| **Long-Polling** | Dedicated Nginx upstream for Odoo Discuss/real-time channels | TECH-017 |
| **Database Partitioning** | Partition large tables (service orders, invoices) by date range | TECH-004 (5x growth) |

### 3.5 Odoo JSON-2 API Specification

The JSON-2 API (new in Odoo v19) provides the primary integration interface between Odoo CE and the Next.js platform (INT-001 to INT-006).

| Endpoint | Method | Purpose | Direction | Requirement |
|---|---|---|---|---|
| `/json/2/service.order` | POST | Create service order from web booking | Next.js → Odoo | INT-003, SRM-001 |
| `/json/2/service.order/{id}` | GET | Query service order status | Next.js → Odoo | INT-002 |
| `/json/2/service.order/{id}/status` | PATCH | Update service order status | Odoo → Next.js (webhook) | INT-005 |
| `/json/2/technician/{id}/location` | GET | Get technician GPS position | Next.js → Odoo | FSM-003, FSM-027 |
| `/json/2/booking/availability` | GET | Query available time slots | Next.js → Odoo | INT-004, CSP-007 |
| `/json/2/customer/sync` | POST | Bidirectional customer data sync | Bidirectional | INT-002, CRM-001 |
| `/json/2/payment/confirm` | POST | Confirm payment received | Next.js → Odoo | INT-011, FIN-014 |
| `/json/2/invoice/{id}` | GET | Retrieve invoice details | Next.js → Odoo | FIN-010, CSP-005 |
| `/json/2/contract/{customer_id}` | GET | Get active contracts for customer | Next.js → Odoo | CWM-001, CSP-011 |
| `/json/2/device/{serial}` | GET | Device lookup by serial number | Next.js → Odoo | SRM-005, CRM-002 |
| `/json/2/privilege/member/{id}` | GET | Privilege program membership status | Next.js → Odoo | CRM-009, CSP-009 |

**Authentication**: All API calls authenticated via OAuth 2.0 bearer tokens (issued by Keycloak).
**Rate Limiting**: 100 requests/minute per API key (configurable via Nginx).
**Response Format**: JSON with standard error codes and pagination.

---

## 4. LAYER 2 — OCA MODULE ECOSYSTEM

### 4.1 OCA Quality Framework

The Odoo Community Association (OCA) is a nonprofit organization that maintains 200+ repositories of Odoo modules with enterprise-grade quality controls:

| Quality Measure | Description |
|---|---|
| **Mandatory Peer Review** | Every module undergoes code review by 2+ OCA maintainers before merge |
| **CI/CD Testing** | Automated tests run on every pull request (Travis CI / GitHub Actions) |
| **Coding Standards** | OCA coding guidelines enforced (PEP 8, Odoo coding style, security checks) |
| **Version Migration** | Active migration to latest Odoo version (v19 migration underway for core modules) |
| **License Compliance** | All modules licensed under LGPL-3 or AGPL-3 (compatible with Odoo CE) |
| **Maturity Rating** | Modules classified by maturity: Alpha → Beta → Production/Stable |
| **Documentation** | README with installation, configuration, usage instructions per module |

**Risk Mitigation**: Only modules with "Production/Stable" or "Beta" maturity rating and v19 migration confirmed (or in-progress with active commits in last 6 months) will be deployed. All modules will be tested in staging before production deployment.

### 4.2 OCA/field-service — Field Service Management (33 Modules)

This repository is the **cornerstone** replacement for the Odoo Enterprise Field Service module, which is not available in CE. It addresses the majority of SRM, FSM, and CWM requirements.

| # | Module (Technical Name) | Function | Requirements Covered | Phase |
|---|---|---|---|---|
| 1 | `fieldservice` | Core FSM: work orders, locations, workers, scheduling | SRM-001 to SRM-003, FSM-001, FSM-002, FSM-009 | 1 |
| 2 | `fieldservice_repair` | Integration with Odoo Repair module | SRM-021 to SRM-030 | 1 |
| 3 | `fieldservice_equipment` | Equipment/device tracking and registry | SRM-005, SRM-006, CRM-002 | 1 |
| 4 | `fieldservice_equipment_warranty` | Warranty tracking per device | CWM-009, CWM-010 | 1 |
| 5 | `fieldservice_route` | Route planning and optimization | FSM-004, FSM-010 (base) | 2 |
| 6 | `fieldservice_skill` | Technician skill and certification management | FSM-005, HRM-006, HRM-007 | 1 |
| 7 | `fieldservice_agreement` | Service agreements (AMC/RAMC contracts) | CWM-001 to CWM-008 | 4 |
| 8 | `fieldservice_portal` | Customer portal for field service | CSP-003, CSP-004 | 1 |
| 9 | `fieldservice_stock` | Inventory integration for parts consumption | SRM-024, INV-003, INV-011, FSM-021 | 1 |
| 10 | `fieldservice_vehicle` | Vehicle/van management | INV-003 (van stock) | 2 |
| 11 | `fieldservice_recurring` | Recurring service orders (AMC visits) | CWM-005, FSM-012 | 4 |
| 12 | `fieldservice_substatus` | Custom sub-statuses per workflow | SRM-011 | 1 |
| 13 | `fieldservice_partner_multi_relation` | Multi-contact management | CRM-015 (corporate multi-contact) | 4 |
| 14 | `fieldservice_timeline` | Visual timeline for scheduling | FSM-002 (drag-and-drop dispatch) | 1 |
| 15 | `fieldservice_calendar` | Calendar integration for scheduling | FSM-002, AOP-003 | 1 |
| 16 | `fieldservice_activity` | Activity tracking per work order | SRM-012 (internal notes/comms) | 1 |
| 17 | `fieldservice_stage_validation` | Stage-based validation rules | SRM-026 (QC checklist enforcement) | 1 |
| 18 | `fieldservice_geoengine` | GIS/geographic integration for zone mapping | FSM-008, INT-021 | 2 |
| 19 | `fieldservice_distribution` | Distribution/delivery management | FSM-029 (Pick & Drop tracking) | 2 |
| 20 | `fieldservice_crm` | CRM integration for field service | CRM-001, CRM-004 | 1 |
| 21 | `fieldservice_sale` | Sales order integration | SRM-031 to SRM-035 (pricing/estimation) | 1 |
| 22 | `fieldservice_purchase` | Purchase integration for parts procurement | SRM-024, SCM-006 | 3 |
| 23 | `fieldservice_account` | Accounting integration for invoicing | FIN-010, FIN-011 | 3 |
| 24 | `fieldservice_project` | Project management integration | SRM-003 (lifecycle tracking) | 1 |
| 25 | `fieldservice_fleet` | Fleet management integration | FSM-008 (van tracking) | 2 |
| 26 | `fieldservice_google_map` | Google Maps integration for location display | INT-018, FSM-016 | 2 |
| 27 | `fieldservice_google_marker_icon_picker` | Custom map marker icons | AOP-004 (live map indicators) | 2 |
| 28 | `fieldservice_change_management` | Change order tracking | SRM-020 (approval workflows) | 1 |
| 29 | `fieldservice_quality_control` | Quality checks on field orders | SRM-026, QMS-006 | 1 |
| 30 | `fieldservice_template` | Service order templates | SRM-016 (common repair templates) | 1 |
| 31 | `fieldservice_maintenance` | Maintenance schedule management | CWM-005 (scheduled maintenance) | 4 |
| 32 | `fieldservice_size` | Service territory sizing | FSM-008 (zone management) | 2 |
| 33 | `fieldservice_isp` | Field service for ISP operations (adaptable) | — (reference architecture) | — |

### 4.3 OCA/helpdesk — Service Desk Management (28 Modules)

Replaces the Enterprise Helpdesk module. Handles ticket creation, SLA tracking, and customer interaction.

| # | Module (Technical Name) | Function | Requirements Covered | Phase |
|---|---|---|---|---|
| 1 | `helpdesk_mgmt` | Core helpdesk: tickets, categories, stages, assignment | SRM-001, SRM-003, SRM-004, SRM-012 | 1 |
| 2 | `helpdesk_mgmt_sla` | SLA tracking and enforcement with breach alerts | SRM-009, SRM-010, CWM-018 to CWM-022 | 1 |
| 3 | `helpdesk_mgmt_fieldservice` | Integration with OCA field-service module | SRM-001 (multi-channel order creation) | 1 |
| 4 | `helpdesk_mgmt_rating` | Customer satisfaction ratings post-service | CRM-006, CSP-008 | 1 |
| 5 | `helpdesk_mgmt_timesheet` | Time tracking on tickets/service orders | SRM-025, FSM-022 | 1 |
| 6 | `helpdesk_mgmt_project` | Project integration for complex repairs | SRM-003 (lifecycle tracking) | 1 |
| 7 | `helpdesk_mgmt_priority` | Priority management and escalation | SRM-015, CWM-021 | 1 |
| 8-28 | Additional helpdesk modules | Partner, team, type, template, and reporting modules | Various SRM, CRM, AOP requirements | 1-4 |

### 4.4 OCA/management-system — Quality & ISO 9001:2015 (33 Modules)

Provides comprehensive quality management aligned with ISO 9001:2015 certification requirements.

| # | Module (Technical Name) | Function | Requirements Covered | Phase |
|---|---|---|---|---|
| 1 | `mgmtsystem` | Core management system framework | QMS-001 (ISO compliance tracking) | 5 |
| 2 | `mgmtsystem_quality` | Quality management with KPIs | QMS-006, QMS-008 | 5 |
| 3 | `mgmtsystem_audit` | Internal audit management | QMS-002 (audit plans, findings) | 5 |
| 4 | `mgmtsystem_nonconformity` | Non-conformance tracking (NCR) | QMS-003 | 5 |
| 5 | `mgmtsystem_action` | Corrective/Preventive Actions (CAPA) | QMS-004 | 5 |
| 6 | `mgmtsystem_review` | Management reviews and documentation | QMS-001, QMS-007 | 5 |
| 7 | `mgmtsystem_hazard` | Hazard identification and risk assessment | QMS-001 (risk-based approach) | 5 |
| 8 | `mgmtsystem_nonconformity_repair` | NCR integration with repair module | QMS-005 (complaint + root cause) | 5 |
| 9-33 | Additional management-system modules | Survey, claim, environment, health/safety | Various QMS, compliance requirements | 5-6 |

### 4.5 OCA/hr and OCA/payroll — Employee & Payroll Management

| # | Module (Technical Name) | Function | Requirements Covered | Phase |
|---|---|---|---|---|
| 1 | `hr_employee_skill` | Employee skill and certification management | HRM-006 (technician skill matrix) | 1 |
| 2 | `hr_attendance_geolocation` | GPS-based attendance capture | HRM-013 (GPS field attendance) | 5 |
| 3 | `hr_contract_type` | Contract type management (permanent, contractual) | HRM-001, HRM-002 | 5 |
| 4 | `hr_holidays_public` | Public holiday management | HRM-015 (Bangladesh holiday calendar) | 5 |
| 5 | `hr_payroll_community` | Basic payroll processing framework | HRM-017 (base — extended by CD-03) | 5 |
| 6 | `hr_expense` | Expense management and reimbursement | FSM-025 (technician expenses) | 5 |
| 7-40+ | Additional HR/payroll modules | Skill, recruitment, evaluation, department, timesheet | Various HRM requirements | 5 |

### 4.6 OCA/operating-unit — Multi-Branch Management (15+ Modules)

Critical for managing 51+ service center locations with branch-level data isolation (SEC-007).

| # | Module (Technical Name) | Function | Requirements Covered | Phase |
|---|---|---|---|---|
| 1 | `operating_unit` | Core operating unit (branch) definition and hierarchy | SEC-007, all multi-branch requirements | 1 |
| 2 | `account_operating_unit` | Branch-wise accounting and P&L | FIN-001, FIN-002, FIN-030 | 3 |
| 3 | `stock_operating_unit` | Branch-wise inventory management | INV-001, INV-004, INV-010 | 1 |
| 4 | `sale_operating_unit` | Branch-wise sales and quotations | SRM-004 (branch-specific numbering) | 1 |
| 5 | `purchase_operating_unit` | Branch-wise procurement | SCM-006 (branch-level purchase reqs) | 3 |
| 6 | `hr_operating_unit` | Branch-wise HR management | HRM-003, HRM-011 | 5 |
| 7 | `crm_operating_unit` | Branch-wise CRM pipeline | CRM-003, CRM-015 | 1 |
| 8-15+ | Additional operating-unit modules | Analytic, project, fleet, helpdesk per branch | Various branch-level requirements | 1-5 |

### 4.7 OCA/reporting-engine and OCA/mis-builder — BI & Reporting

| # | Module (Technical Name) | Function | Requirements Covered | Phase |
|---|---|---|---|---|
| 1 | `mis_builder` | KPI/MIS report builder with formula engine | BI-009, FIN-029, FIN-030, FIN-033 | 3 |
| 2 | `mis_builder_budget` | Budget management with variance analysis | FIN-033 (budget vs actual) | 3 |
| 3 | `bi_view_editor` | BI view creation from Odoo data models | BI-009, BI-012 | 5 |
| 4 | `bi_sql_editor` | SQL-based custom reports for power users | BI-012 (ad-hoc query capability) | 5 |
| 5 | `report_xlsx` | Excel report generation and export | BI-011 (export to Excel) | 1 |
| 6 | `report_qweb_pdf` | PDF report generation | BI-011 (export to PDF) | 1 |

### 4.8 OCA/dms — Document Management System

| # | Module (Technical Name) | Function | Requirements Covered | Phase |
|---|---|---|---|---|
| 1 | `dms` | Core DMS: categories, tags, version control, access control | DMS-001, DMS-002, DMS-005 | 1 |
| 2 | `dms_field` | Document fields attached to any Odoo record | DMS-006 (templates on records) | 1 |
| 3 | `dms_auto_classification` | Auto-categorization of uploaded documents | DMS-002 (auto-categorize) | 5 |

### 4.9 Additional OCA Modules

| Repository | Key Modules | Function | Requirements Covered | Phase |
|---|---|---|---|---|
| `OCA/account-financial-tools` | `account_asset_management` + 39 modules | Fixed asset depreciation, financial tools | FIN-007, FIN-008 | 3 |
| `OCA/stock-logistics-barcode` | `stock_barcodes` + 9 modules | Barcode scanning for inventory operations | INV-005, FSM-021 | 1 |
| `OCA/l10n-bangladesh` | `l10n_bd` | Bangladesh chart of accounts, VAT, currency | FIN-001, FIN-024, TECH-030 | 1 |
| `OCA/web` | `auth_keycloak` | Keycloak SSO integration for Odoo | SEC-003, INT-006 | 1 |
| `OCA/server-tools` | `audit_log`, `base_technical_features` | Audit trail, technical configuration | SEC-014, TECH-032 | 1 |

### 4.10 OCA Module v19 Compatibility Matrix

| Repository | Total Modules | v19 Migrated | v19 In-Progress | Risk Level | Mitigation |
|---|---|---|---|---|---|
| OCA/field-service | 33 | ~25 | ~8 | Medium | Fork and migrate remaining; test in staging |
| OCA/helpdesk | 28 | ~20 | ~8 | Medium | Core modules migrated; test remaining |
| OCA/management-system | 33 | ~28 | ~5 | Low | Mature repository with active maintenance |
| OCA/hr + payroll | 50+ | ~40 | ~10 | Low | Wide community adoption |
| OCA/operating-unit | 15+ | ~12 | ~3 | Low | Actively maintained, enterprise-critical |
| OCA/reporting-engine | 20+ | ~18 | ~2 | Low | Stable, widely deployed |
| OCA/dms | 5+ | ~4 | ~1 | Low | Mature module |
| OCA/account-financial-tools | 40+ | ~35 | ~5 | Low | Well-maintained |
| OCA/stock-logistics-barcode | 10+ | ~8 | ~2 | Low | Stable |

**Overall OCA Risk**: Medium-Low. All critical-path modules (field-service core, helpdesk core, operating-unit, accounting) have v19 migration confirmed. Non-critical modules can be deferred to later phases if migration is delayed.

---

## 5. LAYER 3 — FREE THIRD-PARTY MODULES

### 5.1 Payment Gateway Modules

| Module | Provider | Integration Protocol | Requirements Covered | Phase | Risk |
|---|---|---|---|---|---|
| **SSLCOMMERZ for Odoo** | Metamorphosis (Official GitHub) | REST API — card payments, net banking | INT-009 (card payments), FIN-014 | 3 | Low — Official module |
| **bKash Payment Module** | Metamorphosis / Custom | REST API — OTP-based mobile money | INT-007, FIN-014 | 3 | Medium — May need CD-08 |
| **Nagad via SSLCOMMERZ** | SSLCOMMERZ aggregation | REST API via SSLCOMMERZ | INT-008, FIN-014 | 3 | Low — Via aggregator |
| **Rocket via SSLCOMMERZ** | SSLCOMMERZ aggregation | REST API via SSLCOMMERZ | INT-010, FIN-014 | 3 | Low — Via aggregator |

**Payment Reconciliation**: All payment modules integrate with Odoo `account` module for automated reconciliation (INT-011). Refund processing handled via Odoo credit note workflow (INT-012, FIN-016).

### 5.2 Communication Modules

| Module | Provider | Integration Protocol | Requirements Covered | Phase | Risk |
|---|---|---|---|---|---|
| **Bangladesh SMS Gateway** | MuthoSMS / GreenWeb | REST API — outbound transactional SMS | INT-013 | 1 | Low — Multiple providers |
| **WhatsApp Connector** | Community (chatwithio/odoo-whatsapp-api) | WhatsApp Cloud API — bidirectional | INT-015 | 1 | Medium — Requires Meta approval |
| **Email Integration** | Odoo CE built-in `mail` module | SMTP / IMAP — transactional email | INT-014 | 1 | Very Low — Native module |

**Note**: All communication modules are orchestrated through n8n (L4) and delivered via Novu (L4) for unified template management, delivery tracking, and channel preference handling. Direct module integrations serve as fallback paths.

### 5.3 GPS and Location Modules

| Module | Provider | Integration Protocol | Requirements Covered | Phase | Risk |
|---|---|---|---|---|---|
| **Traccar GPS Integration** | Community connector | REST API — Traccar ↔ Odoo | FSM-003, INT-018 | 2 | Medium — Custom connector |
| **fieldservice_google_map** | OCA/field-service repository | Google Maps JavaScript API | INT-018, FSM-016, AOP-004 | 2 | Low — OCA maintained |

### 5.4 Barcode and Scanning

| Module | Provider | Integration Protocol | Requirements Covered | Phase | Risk |
|---|---|---|---|---|---|
| **stock_barcodes** | OCA/stock-logistics-barcode | Native Odoo integration | INV-005, FSM-021 | 1 | Low — OCA maintained |
| **Mobile Camera Barcode** | Custom web component | HTML5 Camera API + ZXing library | FSM-021 (mobile barcode scan) | 2 | Low — Standard web API |

### 5.5 Reliability Risk Assessment

| Risk Level | Modules | Mitigation Strategy |
|---|---|---|
| **Low** | SSLCOMMERZ, OCA modules, Email, stock_barcodes | Official/OCA maintained; active communities; update regularly |
| **Medium** | bKash module, WhatsApp Connector, Traccar connector | Code review before adoption; fork and maintain if abandoned; custom development (CD-08) as backup for bKash |
| **Higher** | Community-contributed modules without active maintenance | Full code audit; maintain internal fork; allocate development time for patches |

---

## 6. LAYER 4 — COMPLEMENTARY OPEN-SOURCE TOOLS

### 6.1 Metabase — Business Intelligence & Analytics

| Attribute | Specification |
|---|---|
| **Version** | v0.52+ |
| **License** | AGPL-3 (free, self-hosted) |
| **Maturity** | 10+ years, 40,000+ GitHub stars, enterprise-deployed globally |
| **Integration** | Direct PostgreSQL connection to Odoo read replica |
| **Embedding** | iframe/JWT embedding in Odoo backend and Next.js portals |
| **Phase** | Phase 2 (initial dashboards), Phase 5 (full suite) |

**Requirements Covered**: BI-001 to BI-014, ABD-001 to ABD-010, FIN-029 to FIN-035

**Dashboard Specifications for 1000FiX**:

| Dashboard | Key Metrics | Users | Refresh Rate | Requirement |
|---|---|---|---|---|
| Executive Dashboard | MTD revenue, jobs completed, CSAT, utilization %, revenue trends | CEO, Directors | 15 min | BI-001, ABD-001 |
| Branch Performance | Jobs, revenue, cost, profitability, technician utilization per location (51+ centers) | Operations Manager, Branch Managers | 15 min | BI-002, ABD-005 |
| Technician Scorecard | Jobs/day, first-time fix rate, CSAT, earnings, rework rate | Operations, HR | 15 min | BI-003, ABD-002 |
| Financial Dashboard | Revenue by service/brand/branch, P&L actual vs budget, cash flow, AR aging | Finance Manager | 15 min | BI-006, ABD-003, FIN-030, FIN-033 |
| Inventory Dashboard | Stock levels across 51+ locations, turnover, dead stock, stockout frequency | Inventory Manager | 15 min | BI-005, INV-004 |
| Customer Analytics | Acquisition, retention, LTV, satisfaction trends, churn rate | Management | Daily | BI-007, ABD-004 |
| SLA Compliance | Breach rates by branch/technician, escalation trends, resolution times | Operations | 5 min | CWM-020, CWM-022, ABD-002 |
| Warranty Claims | Claims by brand, approval rates, revenue realization, aging pipeline | Finance, Operations | 15 min | BI-008, FIN-034 |

**Additional Capabilities**:
- Custom report builder with drag-and-drop (BI-009)
- Scheduled report generation and email distribution (BI-010)
- Data export: PDF, Excel, CSV (BI-011)
- Ad-hoc SQL query capability for power users (BI-012)
- Drill-down from summary to transaction level (ABD-007)

### 6.2 Grafana — Operational Real-Time Monitoring

| Attribute | Specification |
|---|---|
| **Version** | v11.x |
| **License** | AGPL-3 (free, self-hosted) |
| **Maturity** | Very high, enterprise-ready, CNCF ecosystem |
| **Integration** | PostgreSQL + Prometheus for system metrics |
| **Phase** | Phase 2 |

**Requirements Covered**: ABD-002 (real-time operational metrics), ABD-010 (automated threshold alerts)

**Dashboards**:
- **Live Operations**: Active technicians on map, open jobs by status, real-time SLA countdown (30-second refresh)
- **Infrastructure Health**: Server CPU/memory/disk, PostgreSQL query performance, API response times, Odoo worker status
- **Business Alerts**: SLA breach alerts → escalation via n8n; stock below reorder → procurement alert; performance degradation → ops team notification

### 6.3 Custom Flutter Mobile App — Technician Portal

| Attribute | Specification |
|---|---|
| **Technology** | Flutter (Dart) — compiles to native Android + iOS |
| **License** | BSD-3 (Flutter SDK) |
| **Target Platform** | Android 11+ (primary), iOS (secondary) |
| **Offline Architecture** | SQLite/Hive local database, 24-hour offline capability |
| **Sync Protocol** | Background service, auto-sync within 30 seconds on reconnect |
| **Language** | Bengali (primary) + English (secondary), full UI translation |
| **Development Effort** | 16-20 person-weeks, 2 Flutter developers |
| **Phase** | Phase 2 |

**Requirements Covered**: TMP-001 to TMP-017, FSM-013 to FSM-026

| Feature | Priority | Requirement | Offline? |
|---|---|---|---|
| Daily job queue with priority sorting | P1 | TMP-002, FSM-015 | Yes |
| GPS navigation to customer (Google Maps) | P1 | TMP-004, FSM-016 | Cached maps |
| Digital service forms with pre-populated data | P1 | TMP-005, FSM-017 | Yes |
| Before/after photo capture with GPS/timestamp | P1 | TMP-006, FSM-018 | Yes (sync later) |
| Barcode/QR scanning (camera API) | P1 | TMP-007, FSM-021 | Yes |
| Customer e-signature capture | P1 | TMP-009, FSM-019 | Yes |
| Parts consumption recording | P1 | TMP-007, FSM-021, INV-011 | Yes |
| Time tracking (auto-capture departed/arrived/completed) | P1 | TMP-008, FSM-022 | Yes |
| Push notifications (Firebase) | P1 | TMP-016, FSM-026, INT-016 | Online only |
| Real-time status updates to dispatch | P1 | FSM-020 | Queue offline |
| Offline mode with automatic sync on reconnect | P1 | TMP-010, TECH-020 | Yes |
| Bengali language UI (100% translation) | P1 | TMP-017, TECH-025 | Yes |
| Guided diagnostic checklists | P1 | SRM-022, FSM-017 | Yes |
| Parts request for items not in van stock | P1 | TMP-015 | Queue offline |
| Job acceptance/rejection with reason | P1 | TMP-003 | Yes |
| In-app messaging with dispatch/customer | P2 | TMP-013, FSM-023 | Queue offline |
| Earnings dashboard (daily/weekly/monthly) | P2 | TMP-011, HRM-009 | Cached data |
| Knowledge base access (repair manuals) | P2 | TMP-012, FSM-024 | Cached PDFs |
| Leave request submission | P2 | TMP-014, HRM-014 | Queue offline |
| Bengali voice-to-text for notes | P2 | URD §13.2 | Device-dependent |

**Integration Pattern**: Flutter App ↔ Odoo JSON-2 API (authenticated via Keycloak OAuth 2.0 token) ↔ PostgreSQL. Offline data stored in SQLite/Hive; synced via background Dart isolate when connectivity restored. 100% data integrity on reconnect (TECH-020).

### 6.4 Traccar — GPS Tracking Server

| Attribute | Specification |
|---|---|
| **Version** | v6.x |
| **License** | Apache-2.0 (free) |
| **Maturity** | 12+ years, 5,000+ GitHub stars, enterprise-deployed globally |
| **Protocols** | 200+ GPS device protocols supported |
| **Integration** | REST API to Odoo, WebSocket for real-time map, Traccar Client app on technician phones |
| **Phase** | Phase 2 |

**Requirements Covered**: FSM-003 (real-time GPS tracking), FSM-027 (customer-facing tracking page), FSM-008 (geo-fencing), INT-018 (Google Maps integration), INT-021 (geo-fencing)

**Data Flow**: Technician phone (Traccar Client app, 30-second GPS interval) → Traccar Server → REST API → Odoo (technician location update) → Next.js portal (customer tracking page via FSM-027). WebSocket stream for real-time map display in Admin Operations Portal (AOP-004).

### 6.5 Mayan EDMS — Document Management System

| Attribute | Specification |
|---|---|
| **Version** | v4.10 |
| **License** | Apache-2.0 (free) |
| **Stack** | Python/Django — aligns with Odoo's Python ecosystem |
| **Database** | PostgreSQL native (shared technology) |
| **OCR** | Tesseract integration — supports Bengali script (DMS-007) |
| **Integration** | REST API to/from Odoo; document links stored in Odoo records |
| **Phase** | Phase 5 (OCA/dms sufficient for Phases 1-4) |

**Requirements Covered**: DMS-001 (centralized storage with version control), DMS-002 (categorization), DMS-003 (digital form builder — partial), DMS-004 (e-signature verification), DMS-005 (approval workflows), DMS-006 (templates), DMS-007 (OCR/scanning), DMS-008 (retention policies)

### 6.6 n8n — Workflow Automation & Notification Orchestration

| Attribute | Specification |
|---|---|
| **Version** | v1.x |
| **License** | Sustainable Use License (free for self-hosted) |
| **Maturity** | High, enterprise-ready, 1,000+ integration connectors |
| **Integration** | Native Odoo node, HTTP Request node, webhooks |
| **Phase** | Phase 1 (basic notifications), expanded each phase |

**Requirements Covered**: All notification requirements (URD §14), TECH-035 (workflow automation engine), INT-005 (webhook-driven integration), plus notification delivery for SRM-014, FSM-026, FSM-028, CWM-007, CRM-005

**Key Workflow Specifications**:

| # | Workflow | Trigger | Actions | Requirements |
|---|---|---|---|---|
| 1 | Service Order Status Change | Odoo webhook: `service_order.status_changed` | Determine template → Novu: SMS + WhatsApp + Push to customer | SRM-014, CSP-003 |
| 2 | Technician Dispatched | Odoo webhook: `technician.dispatched` | Novu: SMS with ETA to customer + Push to technician | FSM-028, TMP-016 |
| 3 | SLA Breach Approaching | Odoo webhook: `sla.warning` (50%, 75%, 90%) | Novu: Push to dispatch manager + Email escalation | SRM-010, CWM-021 |
| 4 | Invoice Generated | Odoo webhook: `invoice.created` | Novu: Email invoice + WhatsApp with bKash payment link | FIN-010, CSP-005 |
| 5 | Warranty Claim Ready | Odoo webhook: `warranty_claim.created` | Format per brand template → Submit to brand partner portal | CWM-011, CWM-012 |
| 6 | Stock Below Reorder | Odoo webhook: `stock.reorder_alert` | Novu: Email to inventory manager + Auto-create purchase req | INV-012, INV-018 |
| 7 | AMC Renewal Reminder | Scheduled: 60/30/15 days before expiry | Novu: SMS + WhatsApp + Email renewal sequence to customer | CWM-007, CRM-005 |
| 8 | Payroll Approved | Odoo webhook: `payroll.approved` | Generate BEFTN file → Store in Mayan EDMS | HRM-021, DMS-001 |
| 9 | CSAT Survey Post-Service | Scheduled: 2 hours after service completion | Novu: SMS + WhatsApp survey link to customer | CRM-006, CSP-008 |
| 10 | Daily Route Optimization | Cron: 5:00 AM daily | Fetch jobs → VROOM API → Push optimized routes to Odoo dispatch | FSM-004, INT-019 |

### 6.7 VROOM + OSRM — Route Optimization

| Attribute | VROOM | OSRM |
|---|---|---|
| **Function** | Vehicle Routing Problem (VRP) solver | Road distance/time calculation engine |
| **Version** | v1.14+ | v5.x |
| **License** | BSD-2-Clause | BSD-2-Clause |
| **Maturity** | High — 1,000+ GitHub stars | Very high — 6,000+ GitHub stars |
| **Integration** | HTTP API, Python wrapper (pyvroom) | HTTP API, Bangladesh road data via OpenStreetMap |
| **Phase** | Phase 2 | Phase 2 |

**Requirements Covered**: FSM-004 (route optimization minimizing travel time), FSM-006 (emergency re-optimization), FSM-010 (travel time estimation), INT-019 (route optimization engine)

**Strategy Divergence from RFP**: The RFP (INT-019) specified "Google Routes API or Timefold" for route optimization. This specification uses VROOM + OSRM instead.

**Justification**:
- VROOM/OSRM: $0 license cost, self-hosted, Bangladesh OpenStreetMap data available, solves VRP in milliseconds
- Timefold: Open-source but complex Java stack, higher infrastructure requirements
- Google Routes API: $200-400/month ongoing cost

**Supplementary**: Google Routes API used selectively for Dhaka metro area traffic data ($200-400/month) to augment OSRM's static road network. This provides the real-time traffic data capability requested in INT-020.

### 6.8 Keycloak — Identity & SSO Management

| Attribute | Specification |
|---|---|
| **Version** | v26.x |
| **License** | Apache-2.0 (CNCF project) |
| **Maturity** | 10+ years, 25,000+ GitHub stars, CNCF ecosystem |
| **Protocols** | SAML 2.0, OAuth 2.0, OpenID Connect |
| **Phase** | Phase 1 |

**Requirements Covered**: SEC-001 (RBAC), SEC-002 (MFA), SEC-003 (SSO), SEC-004 (password policies), SEC-005 (session management), SEC-006 (IP restrictions), SEC-007 (branch-level isolation), INT-006 (shared SSO)

**Integration Points**:

| System | Protocol | Module/Library |
|---|---|---|
| Odoo 19 CE | SAML 2.0 | OCA `auth_keycloak` module |
| Next.js 15 Portal | OpenID Connect | NextAuth.js OIDC provider |
| Metabase | SAML 2.0 | Native Keycloak support |
| Grafana | OAuth 2.0 | Native Keycloak support |
| Mayan EDMS | OpenID Connect | Django OIDC library |
| n8n | OAuth 2.0 | Built-in OAuth support |
| Flutter Mobile App | OAuth 2.0 + PKCE | `flutter_appauth` package |

**20 User Roles Configured in Keycloak** (from URD §4):

| # | Role | Portal Access | MFA Required | Branch Isolation |
|---|---|---|---|---|
| 1 | CEO / Business Owner | Analytics + Admin | Yes | All branches |
| 2 | Operations Manager | Admin Operations | Yes | All branches |
| 3 | Branch Manager | Admin + Branch Dashboard | Yes | Own branch only |
| 4 | Dispatch Manager | Admin Operations (dispatch) | Yes | Assigned zones |
| 5 | Service Center Agent | Admin Operations (service orders) | No | Own branch |
| 6 | Senior Technician | Technician Mobile App | No | Assigned zone |
| 7 | Junior Technician | Technician Mobile App | No | Assigned zone |
| 8 | Finance Manager | Admin + Finance modules | Yes | All branches |
| 9 | Finance Officer | Finance modules | Yes | Assigned scope |
| 10 | HR Manager | Admin + HR modules | Yes | All branches |
| 11 | HR Officer | HR modules | No | Assigned scope |
| 12 | Inventory Manager | Admin + Inventory modules | No | All locations |
| 13 | Procurement Officer | Purchase modules | No | Central |
| 14 | IT Administrator | System configuration | Yes | All systems |
| 15 | Quality Manager | QMS modules | No | All branches |
| 16 | Customer (Individual) | Customer Self-Service Portal | No | Own data only |
| 17 | Customer (Corporate Facility Manager) | B2B Corporate Portal | No | Own company |
| 18 | Vendor / Supplier | Vendor & Partner Portal | No | Own data only |
| 19 | Brand Partner Representative | Vendor Portal (warranty claims) | No | Own claims only |
| 20 | External Auditor (read-only) | Reports + Audit Logs | Yes | Read-only |

### 6.9 Novu — Multi-Channel Notification Infrastructure

| Attribute | Specification |
|---|---|
| **Version** | v2.x |
| **License** | MIT (free) |
| **Maturity** | High — 35,000+ GitHub stars, active development |
| **Channels** | Email, SMS, Push, WhatsApp, In-App |
| **Integration** | REST API; n8n triggers Novu for delivery |
| **Phase** | Phase 1 |

**Requirements Covered**: INT-013 (SMS), INT-014 (email), INT-015 (WhatsApp), INT-016 (push notifications), CSP-014 (push preferences), TMP-016 (technician push), AOP-008 (notification center)

**Capabilities**:
- Unified template management (Bengali + English templates per channel)
- Subscriber preference center (notification opt-in/opt-out per channel per event type)
- Delivery tracking and retry logic
- Digest mode (bundle non-urgent notifications)
- Quiet hours configuration (10 PM – 7 AM, emergency overrides)
- Integration with Bangladesh SMS providers (MuthoSMS, GreenWeb)
- WhatsApp Business API integration (Meta-approved)
- Firebase Cloud Messaging for push notifications

### 6.10 Ollama + LLM — Bengali NLP Chatbot (Phase 6)

| Attribute | Specification |
|---|---|
| **Technology** | Ollama (local LLM server) + Qwen3-8B or TigerLLM (Bengali-capable) + LangChain (orchestration) |
| **License** | MIT (Ollama), Apache-2.0 (LangChain), Model-specific |
| **Integration** | WhatsApp Cloud API → LangChain → Odoo JSON-2 API |
| **Phase** | Phase 6 (highest complexity, lowest priority) |

**Requirements Covered**: INT-022 (AI chatbot with Bengali NLP), CSP-013 (live chat with AI + human escalation)

**Strategy Divergence from RFP**: The RFP (INT-022) specified "Rasa 3.6 with Bengali NLP." This specification uses an LLM-based approach instead.

**Justification**:
- Rasa OSS has entered maintenance mode (limited future development — increased long-term risk)
- LLM approach provides superior Bengali language understanding (Qwen3-8B trained on Bengali corpus)
- Tool-use capability allows LLM to directly interact with Odoo API (create bookings, check status)
- Self-hosted via Ollama — no per-query API costs, data remains on-premises
- Human agent escalation via handoff to WhatsApp live agent queue

### 6.11 Tool Version and License Summary

| Tool | Version | License | GitHub Stars | Self-Hosted | Monthly Cost | Phase |
|---|---|---|---|---|---|---|
| Odoo 19 CE | 19.0/19.1 | LGPL-3 | 38,000+ | Yes | $0 | 1 |
| OCA Modules (94+) | v19 | LGPL-3 / AGPL-3 | Varies | Yes | $0 | 1-5 |
| Metabase | 0.52+ | AGPL-3 | 40,000+ | Yes | $0 | 2 |
| Grafana | 11.x | AGPL-3 | 65,000+ | Yes | $0 | 2 |
| Traccar | 6.x | Apache-2.0 | 5,000+ | Yes | $0 | 2 |
| n8n | 1.x | Sustainable Use | 50,000+ | Yes | $0 | 1 |
| VROOM | 1.14+ | BSD-2 | 1,200+ | Yes | $0 | 2 |
| OSRM | 5.x | BSD-2 | 6,500+ | Yes | $0 | 2 |
| Keycloak | 26.x | Apache-2.0 | 25,000+ | Yes | $0 | 1 |
| Mayan EDMS | 4.10 | Apache-2.0 | 500+ | Yes | $0 | 5 |
| Novu | 2.x | MIT | 35,000+ | Yes | $0 | 1 |
| Flutter SDK | 3.x | BSD-3 | 167,000+ | N/A | $0 | 2 |
| Ollama | 0.5+ | MIT | 100,000+ | Yes | $0 | 6 |
| LangChain | 0.3+ | Apache-2.0 | 95,000+ | Yes | $0 | 6 |
| PostgreSQL | 16 | PostgreSQL | N/A | Managed | Included | 1 |
| Redis | 7 | BSD-3 | 67,000+ | Managed | Included | 1 |
| Nginx | 1.27+ | BSD-2 | N/A | Yes | $0 | 1 |
| Docker | 27+ | Apache-2.0 | N/A | Yes | $0 | 1 |

---

## 7. LAYER 5 — CUSTOM DEVELOPMENT

### 7.1 Custom Development Overview

20 custom modules totaling 80-115 person-weeks of development effort. These modules address Bangladesh-specific requirements, mobile field operations, and integration gaps that cannot be filled by existing open-source solutions.

**Development Team Composition**:

| Role | Count | Duration | Monthly Rate (Bangladesh) | Total Cost |
|---|---|---|---|---|
| Senior Odoo Developer (Python) | 2 | 12 months | $2,500 – $4,000 | $60,000 – $96,000 |
| Flutter Developer | 2 | 4 months | $2,000 – $3,500 | $16,000 – $28,000 |
| DevOps / Infrastructure Engineer | 1 | 6 months | $2,000 – $3,000 | $12,000 – $18,000 |
| Business Analyst / QA | 1 | 12 months | $1,500 – $2,500 | $18,000 – $30,000 |
| **Total** | **6** | — | — | **$106,000 – $172,000** |

### 7.2 Custom Module Specifications

#### CD-01: Technician Mobile App (Flutter)

| Attribute | Detail |
|---|---|
| **Priority** | P1 |
| **Effort** | 16-20 person-weeks |
| **Phase** | Phase 2 |
| **Requirements** | TMP-001 to TMP-017, FSM-013 to FSM-026 |
| **Technology** | Flutter (Dart), SQLite/Hive (offline), Firebase (push), Google Maps SDK |
| **Dependencies** | Odoo JSON-2 API (L1), Traccar (L4), Keycloak OAuth (L4) |
| **Acceptance** | 24hr offline operation, <30s sync on reconnect, 100% data integrity, Bengali UI |

#### CD-02: Bangladesh Mushak 6.3 Invoice

| Attribute | Detail |
|---|---|
| **Priority** | P1 |
| **Effort** | 4-6 person-weeks |
| **Phase** | Phase 3 |
| **Requirements** | FIN-024 to FIN-027 |
| **Technology** | Odoo Python module extending `account` module |
| **Dependencies** | Odoo `account` (L1), l10n_bd (L2) |
| **Acceptance** | NBR-compliant Mushak 6.3 format, auto-VAT calculation (15%), BIN/TIN fields, VAT return preparation |

#### CD-03: Bangladesh Payroll Module

| Attribute | Detail |
|---|---|
| **Priority** | P1 |
| **Effort** | 8-12 person-weeks |
| **Phase** | Phase 5 |
| **Requirements** | HRM-017 to HRM-023 |
| **Technology** | Odoo Python module extending `hr_payroll_community` (L2) |
| **Dependencies** | OCA `hr_payroll_community` (L2), `hr_attendance` (L1), `hr_holidays` (L1) |
| **Acceptance** | Bangladesh tax slab computation, provident fund, gratuity, BEFTN file generation, digital payslips |

#### CD-04: Warranty Claim Automation

| Attribute | Detail |
|---|---|
| **Priority** | P1 |
| **Effort** | 6-8 person-weeks |
| **Phase** | Phase 4 |
| **Requirements** | CWM-009 to CWM-017, FIN-011, FIN-034 |
| **Technology** | Odoo Python module + n8n workflows for brand-specific submission |
| **Dependencies** | OCA `fieldservice_equipment_warranty` (L2), n8n (L4) |
| **Acceptance** | Auto-claim within 24hrs of work order closure, brand-specific formats (17+ partners), revenue reconciliation |

#### CD-05: Privilege Program (Loyalty)

| Attribute | Detail |
|---|---|
| **Priority** | P1 |
| **Effort** | 4-6 person-weeks |
| **Phase** | Phase 1 |
| **Requirements** | CRM-009 to CRM-013 |
| **Technology** | Odoo Python module extending `crm` and `sale` |
| **Dependencies** | Odoo `crm` (L1), `sale` (L1) |
| **Acceptance** | Silver/Gold/Diamond tiers, auto-discount on labor (not parts), enrollment/renewal/upgrade workflows |

#### CD-06: AI Dispatch Engine

| Attribute | Detail |
|---|---|
| **Priority** | P1 |
| **Effort** | 6-8 person-weeks |
| **Phase** | Phase 2 |
| **Requirements** | FSM-001, FSM-004 to FSM-006, FSM-009, INT-019, INT-023 |
| **Technology** | Python service integrating VROOM/OSRM with Odoo scheduling logic |
| **Dependencies** | VROOM/OSRM (L4), OCA `fieldservice_skill` (L2), `fieldservice_route` (L2) |
| **Acceptance** | Skill matching, zone awareness, van stock consideration, emergency re-optimization, 7-8 jobs/tech/day target |

#### CD-07: Customer Tracking Page

| Attribute | Detail |
|---|---|
| **Priority** | P1 |
| **Effort** | 3-4 person-weeks |
| **Phase** | Phase 2 |
| **Requirements** | FSM-027, CSP-003 |
| **Technology** | Next.js page component + Traccar WebSocket + Google Maps embed |
| **Dependencies** | Traccar (L4), Next.js platform (CON-03), Odoo JSON-2 API (L1) |
| **Acceptance** | Real-time technician location on map with ETA, SMS link to customer, mobile-responsive |

#### CD-08: bKash/Nagad Direct Integration

| Attribute | Detail |
|---|---|
| **Priority** | P1 |
| **Effort** | 3-4 person-weeks |
| **Phase** | Phase 3 |
| **Requirements** | INT-007, INT-008, FIN-014, INT-011 |
| **Technology** | Odoo Python module + bKash/Nagad REST APIs |
| **Dependencies** | Odoo `account` (L1), bKash API sandbox/production access |
| **Acceptance** | OTP-based payment flow, auto-reconciliation with accounting, refund processing |

#### CD-09: Bangladesh TDS Module

| Attribute | Detail |
|---|---|
| **Priority** | P1 |
| **Effort** | 2-3 person-weeks |
| **Phase** | Phase 3 |
| **Requirements** | FIN-025 |
| **Technology** | Odoo Python module extending `account` |
| **Dependencies** | Odoo `account` (L1), CD-02 (Mushak module) |
| **Acceptance** | Tax withholding at source per Bangladesh tax laws, auto-deduction on vendor payments |

#### CD-10: Rework Detection

| Attribute | Detail |
|---|---|
| **Priority** | P1 |
| **Effort** | 2-3 person-weeks |
| **Phase** | Phase 1 |
| **Requirements** | SRM-017, SRM-029 |
| **Technology** | Odoo Python module extending `fieldservice` |
| **Dependencies** | OCA `fieldservice` (L2), `fieldservice_equipment` (L2) |
| **Acceptance** | Auto-flag same device + same fault category returning within 30 days; rework rate tracking in BI |

#### CD-11: Diagnostic Checklist Builder

| Attribute | Detail |
|---|---|
| **Priority** | P1 |
| **Effort** | 3-4 person-weeks |
| **Phase** | Phase 1 |
| **Requirements** | SRM-022, SRM-026, FSM-017, QMS-005 |
| **Technology** | Odoo Python module with configurable form builder |
| **Dependencies** | OCA `fieldservice_quality_control` (L2) |
| **Acceptance** | Templates per device type + issue category, mandatory completion before job close, syncs to mobile app |

#### CD-12: Bangladesh Address Fields

| Attribute | Detail |
|---|---|
| **Priority** | P1 |
| **Effort** | 1-2 person-weeks |
| **Phase** | Phase 1 |
| **Requirements** | TECH-031, CSP-017 |
| **Technology** | Odoo Python module extending `contacts` |
| **Dependencies** | Odoo `contacts` (L1) |
| **Acceptance** | 8 divisions, 64 districts, upazilas, postal codes; cascading dropdown selection; map-based address picker |

#### CD-13: Consolidated B2B Invoicing

| Attribute | Detail |
|---|---|
| **Priority** | P1 |
| **Effort** | 3-4 person-weeks |
| **Phase** | Phase 4 |
| **Requirements** | FIN-012, B2B-005 |
| **Technology** | Odoo Python module extending `account` |
| **Dependencies** | Odoo `account` (L1), OCA `account_operating_unit` (L2) |
| **Acceptance** | Monthly consolidated invoice per corporate client, configurable billing cycles (weekly/bi-weekly/monthly) |

#### CD-14: Performance Incentive Calculator

| Attribute | Detail |
|---|---|
| **Priority** | P1 |
| **Effort** | 3-4 person-weeks |
| **Phase** | Phase 5 |
| **Requirements** | HRM-009, HRM-019 |
| **Technology** | Odoo Python module integrated with payroll |
| **Dependencies** | CD-03 (Bangladesh Payroll), OCA `fieldservice` (L2) |
| **Acceptance** | KPI-based incentive (jobs completed, CSAT, first-time fix rate) → auto-feed to payroll computation |

#### CD-15: Shift & Roster Management

| Attribute | Detail |
|---|---|
| **Priority** | P1 |
| **Effort** | 3-4 person-weeks |
| **Phase** | Phase 5 |
| **Requirements** | HRM-011 |
| **Technology** | Odoo Python module extending `hr_attendance` |
| **Dependencies** | Odoo `hr_attendance` (L1), `calendar` (L1) |
| **Acceptance** | Branch-wise shift planning, roster generation, auto-assignment consideration for dispatch |

#### CD-16: Bengali NLP Chatbot

| Attribute | Detail |
|---|---|
| **Priority** | P2 |
| **Effort** | 8-12 person-weeks |
| **Phase** | Phase 6 |
| **Requirements** | INT-022, CSP-013 |
| **Technology** | Ollama + Qwen3-8B/TigerLLM + LangChain + WhatsApp Cloud API |
| **Dependencies** | Ollama (L4), Odoo JSON-2 API (L1), WhatsApp Business API |
| **Acceptance** | Bengali intent classification, service order creation via chat, status queries, human agent escalation |

#### CD-17: Walk-in Queue Management

| Attribute | Detail |
|---|---|
| **Priority** | P2 |
| **Effort** | 2-3 person-weeks |
| **Phase** | Phase 1 |
| **Requirements** | FSM-030 |
| **Technology** | Odoo Python module + simple queue display view |
| **Dependencies** | OCA `fieldservice` (L2) |
| **Acceptance** | Token system, estimated wait time display, queue display monitor at service center reception |

#### CD-18: Warranty Revenue Tracker

| Attribute | Detail |
|---|---|
| **Priority** | P1 |
| **Effort** | 2-3 person-weeks |
| **Phase** | Phase 4 |
| **Requirements** | FIN-034, CWM-014, BI-008 |
| **Technology** | Odoo Python module extending `account` + warranty claim model |
| **Dependencies** | CD-04 (Warranty Claim Automation), Odoo `account` (L1) |
| **Acceptance** | Claim aging dashboard, submitted vs paid reconciliation, brand-wise revenue tracking |

#### CD-19: NID Validation

| Attribute | Detail |
|---|---|
| **Priority** | P1 |
| **Effort** | 1 person-week |
| **Phase** | Phase 3 |
| **Requirements** | BRD BRU-FIN-02 (cash > BDT 50,000 requires NID) |
| **Technology** | Odoo Python module — field validation |
| **Dependencies** | Odoo `contacts` (L1) |
| **Acceptance** | 10-digit and 17-digit Bangladesh NID format validation, mandatory capture for high-value cash payments |

#### CD-20: Overtime Approval Module

| Attribute | Detail |
|---|---|
| **Priority** | P1 |
| **Effort** | 2-3 person-weeks |
| **Phase** | Phase 5 |
| **Requirements** | HRM-016 |
| **Technology** | Odoo Python module extending `hr_attendance` |
| **Dependencies** | Odoo `hr_attendance` (L1), CD-03 (Bangladesh Payroll) |
| **Acceptance** | Pre-approval workflow by line manager, auto-integration with payroll computation |

### 7.3 Custom Module Summary by Phase

| Phase | Modules | Total Effort (Person-Weeks) |
|---|---|---|
| Phase 1 (Months 1-4) | CD-05, CD-10, CD-11, CD-12, CD-17 | 12-18 PW |
| Phase 2 (Months 4-7) | CD-01, CD-06, CD-07 | 25-32 PW |
| Phase 3 (Months 7-10) | CD-02, CD-08, CD-09, CD-19 | 10-14 PW |
| Phase 4 (Months 10-13) | CD-04, CD-13, CD-18 | 11-15 PW |
| Phase 5 (Months 13-16) | CD-03, CD-14, CD-15, CD-20 | 16-23 PW |
| Phase 6 (Months 16-18) | CD-16 | 8-12 PW |
| **TOTAL** | **20 modules** | **80-115 PW** |

---

## 8. REQUIREMENT-TO-TECHNOLOGY TRACEABILITY MATRIX

### 8.1 Service & Repair Management (SRM) — 37 Requirements

| Req # | Requirement | Priority | Layer | Technology Solution | Response |
|---|---|---|---|---|---|
| SRM-001 | Multi-channel service order creation | P1 | L2 | OCA `helpdesk_mgmt` + `fieldservice` + Next.js API | C |
| SRM-002 | Service order type classification | P1 | L2 | OCA `fieldservice` (configurable work order types) | C |
| SRM-003 | Full service order lifecycle | P1 | L2 | OCA `helpdesk_mgmt` stages + `fieldservice` workflow | C |
| SRM-004 | Auto-assign unique service order number per branch | P1 | L2 | OCA `fieldservice` + `operating_unit` (branch prefix) | C |
| SRM-005 | Link to customer devices with serial number | P1 | L2 | OCA `fieldservice_equipment` | S |
| SRM-006 | Device information capture | P1 | L2 | OCA `fieldservice_equipment` | S |
| SRM-007 | Complete service history per device | P1 | L2 | OCA `fieldservice_equipment` (history view) | S |
| SRM-008 | Multiple service items per order | P1 | L2 | OCA `fieldservice` (multiple tasks per order) | C |
| SRM-009 | SLA tracking per service type/brand/tier | P1 | L2 | OCA `helpdesk_mgmt_sla` | C |
| SRM-010 | SLA breach alerts with escalation | P1 | L2+L4 | OCA `helpdesk_mgmt_sla` + n8n escalation workflows | C |
| SRM-011 | Configurable statuses and sub-statuses | P2 | L2 | OCA `fieldservice_substatus` | S |
| SRM-012 | Internal notes and communication thread | P1 | L1+L2 | Odoo `discuss` + OCA `fieldservice_activity` | S |
| SRM-013 | Photo/video attachment capability | P1 | L1+L4 | Odoo attachment framework + Flutter app (CD-01) | S |
| SRM-014 | Auto customer notifications at status change | P1 | L4 | n8n + Novu (SMS + WhatsApp + push) | T |
| SRM-015 | Prioritization rules (VIP, emergency, SLA) | P2 | L2 | OCA `helpdesk_mgmt_priority` | C |
| SRM-016 | Service order templates | P2 | L2 | OCA `fieldservice_template` | S |
| SRM-017 | Duplicate/rework detection | P2 | L5 | CD-10 (Rework Detection module) | D |
| SRM-018 | Service order splitting | P3 | L2 | OCA `fieldservice` (sub-tasks) | C |
| SRM-019 | Service order merging | P3 | L5 | Minor custom development | D |
| SRM-020 | Approval workflows for high-value repairs | P1 | L2 | OCA `fieldservice_change_management` | C |
| SRM-021 | Multi-level repair classification | P1 | L2 | OCA `fieldservice_repair` (configurable levels) | C |
| SRM-022 | Diagnostic checklist templates | P1 | L5 | CD-11 (Diagnostic Checklist Builder) | D |
| SRM-023 | Repair cost estimation with customer approval | P1 | L1+L2 | Odoo `sale` quotation + fieldservice integration | C |
| SRM-024 | Parts requisition linked to inventory | P1 | L2 | OCA `fieldservice_stock` | S |
| SRM-025 | Labor time tracking per order/technician | P1 | L2 | OCA `helpdesk_mgmt_timesheet` | S |
| SRM-026 | Quality inspection checklist on completion | P1 | L2+L5 | OCA `fieldservice_quality_control` + CD-11 | C |
| SRM-027 | Post-repair testing/certification | P2 | L2 | OCA `fieldservice_stage_validation` | C |
| SRM-028 | Warranty claim generation from warranty repair | P1 | L5 | CD-04 (Warranty Claim Automation) | D |
| SRM-029 | Rework tracking (same issue within 30 days) | P1 | L5 | CD-10 (Rework Detection) | D |
| SRM-030 | Root cause analysis categorization | P2 | L2 | OCA `mgmtsystem_nonconformity` | C |
| SRM-031 | Configurable service price list | P1 | L1 | Odoo `sale` pricelists | S |
| SRM-032 | Separate warranty vs out-of-warranty pricing | P1 | L1 | Odoo `sale` pricelists (per category) | C |
| SRM-033 | Dynamic cost estimation (labor+parts+transport+tax) | P1 | L1+L2 | Odoo `sale` + `fieldservice_sale` | C |
| SRM-034 | Customer-facing quotation with approval | P1 | L1 | Odoo `sale` quotation + portal signature | S |
| SRM-035 | Discount management (privilege, promo, bulk) | P1 | L1+L5 | Odoo `sale` discounts + CD-05 (Privilege Program) | C |
| SRM-036 | NTE limits for B2B accounts | P2 | L5 | Custom business rule in CD-13 | D |
| SRM-037 | Price revision history | P2 | L1 | Odoo `sale` pricelist versioning | S |

**Coverage**: L1=30% | L2=43% | L4=5% | L5=22%

### 8.2 Field Service Management (FSM) — 31 Requirements

| Req # | Requirement | Priority | Layer | Technology Solution | Response |
|---|---|---|---|---|---|
| FSM-001 | AI-powered smart scheduling engine | P1 | L5 | CD-06 (AI Dispatch Engine) + VROOM/OSRM | D |
| FSM-002 | Drag-and-drop dispatch board | P1 | L2 | OCA `fieldservice_timeline` + `fieldservice_calendar` | C |
| FSM-003 | Real-time GPS tracking | P1 | L4 | Traccar (GPS server) + Flutter app (Traccar Client) | T |
| FSM-004 | Route optimization for multiple jobs/day | P1 | L4+L5 | VROOM + OSRM + CD-06 | D |
| FSM-005 | Skill-based assignment matching | P1 | L2 | OCA `fieldservice_skill` | S |
| FSM-006 | Emergency job insertion + re-optimization | P1 | L5 | CD-06 (re-optimization via VROOM API) | D |
| FSM-007 | Auto rescheduling suggestions | P2 | L5 | CD-06 (extension) | D |
| FSM-008 | Service territory/zone management + geo-fencing | P2 | L2+L4 | OCA `fieldservice_geoengine` + Traccar geo-fencing | C |
| FSM-009 | Capacity planning (max jobs/tech/day) | P1 | L2 | OCA `fieldservice` (configurable limits) | C |
| FSM-010 | Travel time estimation with traffic data | P2 | L4 | OSRM + Google Routes API (Dhaka metro supplement) | T |
| FSM-011 | Preferred technician for repeat customers | P3 | L5 | Minor custom field on customer record | D |
| FSM-012 | Batch scheduling for AMC recurring visits | P2 | L2 | OCA `fieldservice_recurring` | S |
| FSM-013 | Mobile app (PWA/native) for field technicians | P1 | L5 | CD-01 (Flutter App) | D |
| FSM-014 | Offline mode with auto-sync | P1 | L5 | CD-01 (SQLite/Hive + background sync) | D |
| FSM-015 | Mobile job queue | P1 | L5 | CD-01 (Flutter job queue screen) | D |
| FSM-016 | GPS navigation to job site (Google Maps) | P1 | L5 | CD-01 (Google Maps SDK integration) | D |
| FSM-017 | Digital service forms/checklists on mobile | P1 | L5 | CD-01 + CD-11 (diagnostic checklists synced to app) | D |
| FSM-018 | Before/after photo with timestamp/GPS | P1 | L5 | CD-01 (camera + EXIF data) | D |
| FSM-019 | Customer e-signature capture | P1 | L5 | CD-01 (signature pad widget) | D |
| FSM-020 | Real-time status updates from field | P1 | L5 | CD-01 (auto-status: en route/arrived/working/done) | D |
| FSM-021 | Parts consumption via barcode/QR scan | P1 | L5 | CD-01 (ZXing barcode + OCA stock_barcodes API) | D |
| FSM-022 | Time tracking (travel/on-site/repair) auto-capture | P1 | L5 | CD-01 (timestamp capture per status transition) | D |
| FSM-023 | In-app messaging (tech ↔ dispatch/customer) | P2 | L5 | CD-01 (Odoo Discuss integration) | D |
| FSM-024 | Knowledge base from mobile | P2 | L5 | CD-01 (cached PDF/HTML repair guides) | D |
| FSM-025 | Expense reporting from mobile | P3 | L2+L5 | OCA `hr_expense` + CD-01 mobile form | D |
| FSM-026 | Push notifications for assignments/changes | P1 | L4+L5 | Firebase via Novu + CD-01 (FCM integration) | T |
| FSM-027 | Customer-facing tracking page with ETA | P1 | L5 | CD-07 (Next.js + Traccar WebSocket + Google Maps) | D |
| FSM-028 | Auto SMS when dispatched/en route/arriving | P1 | L4 | n8n + Novu (triggered by FSM-020 status updates) | T |
| FSM-029 | Pick & Drop service lifecycle tracking | P1 | L2 | OCA `fieldservice_distribution` | C |
| FSM-030 | Walk-in queue management | P2 | L5 | CD-17 (Walk-in Queue Management) | D |
| FSM-031 | Remote support session tracking | P3 | L2 | OCA `helpdesk_mgmt` (remote session ticket type) | C |

**Coverage**: L1=0% | L2=23% | L4=10% | L5=67%

### 8.3 Inventory & Spare Parts Management (INV) — 24 Requirements

| Req # | Requirement | Priority | Layer | Technology Solution | Response |
|---|---|---|---|---|---|
| INV-001 | Multi-warehouse across 51+ locations | P1 | L1+L2 | Odoo `stock` + OCA `stock_operating_unit` | S |
| INV-002 | Central warehouse + regional hubs | P1 | L1 | Odoo `stock` (warehouse hierarchy) | S |
| INV-003 | Technician van/mobile stock | P1 | L2 | OCA `fieldservice_vehicle` + `fieldservice_stock` | C |
| INV-004 | Real-time stock visibility dashboard | P1 | L1+L4 | Odoo `stock` + Metabase (BI-005) | S |
| INV-005 | Barcode and QR code support | P1 | L2 | OCA `stock_barcodes` | S |
| INV-006 | Serial number tracking (high-value parts) | P1 | L1 | Odoo `stock` (lot/serial tracking) | S |
| INV-007 | Batch/lot tracking for consumables | P2 | L1 | Odoo `stock` (lot tracking) | S |
| INV-008 | Multi-unit of measure | P2 | L1 | Odoo `stock` (UoM categories) | S |
| INV-009 | Goods receipt with quality inspection | P1 | L1 | Odoo `stock` (receipt + quality check) | S |
| INV-010 | Inter-branch transfer with approval | P1 | L1+L2 | Odoo `stock` inter-warehouse + OCA operating-unit approval | C |
| INV-011 | Stock requisition from service orders | P1 | L2 | OCA `fieldservice_stock` (auto-reservation) | S |
| INV-012 | Auto replenishment (reorder points) | P1 | L1 | Odoo `stock` (reorder rules) | S |
| INV-013 | Cycle counting and reconciliation | P1 | L1 | Odoo `stock` (inventory adjustments) | S |
| INV-014 | Dead stock identification | P2 | L1+L4 | Odoo `stock` aging + Metabase report (BI-005) | C |
| INV-015 | Warranty returns to brand/supplier (RTV) | P1 | L1+L5 | Odoo `stock` returns + CD-04 warranty integration | C |
| INV-016 | Consignment inventory | P2 | L1 | Odoo `stock` (owner field on quants) | C |
| INV-017 | Stock valuation: FIFO, weighted average | P1 | L1 | Odoo `stock` (FIFO/average costing) | S |
| INV-018 | Min/max stock level alerts per item/location | P1 | L1+L4 | Odoo `stock` reorder rules + n8n alert workflow | S |
| INV-019 | Master parts catalog with device compatibility | P1 | L1+L5 | Odoo `product` + custom compatibility fields | C |
| INV-020 | Genuine vs compatible classification | P1 | L1 | Odoo `product` categories | C |
| INV-021 | Parts pricing tiers (warranty/paid/internal) | P1 | L1 | Odoo `sale` pricelists (multiple) | C |
| INV-022 | Parts substitution mapping | P2 | L1 | Odoo `product` alternative products | C |
| INV-023 | Parts image library | P3 | L1 | Odoo `product` image attachments | S |
| INV-024 | Supplier lead time tracking | P2 | L1 | Odoo `purchase` (vendor lead time) | S |

**Coverage**: L1=71% | L2=17% | L4=4% | L5=8%

### 8.4 Customer Relationship Management (CRM) — 18 Requirements

| Req # | Requirement | Priority | Layer | Technology Solution | Response |
|---|---|---|---|---|---|
| CRM-001 | 360-degree customer profile | P1 | L1+L2 | Odoo `crm` + `contacts` + OCA `fieldservice_crm` | S |
| CRM-002 | Device registry per customer | P1 | L2 | OCA `fieldservice_equipment` | S |
| CRM-003 | Customer segmentation | P1 | L1 | Odoo `crm` + `contacts` tags/categories | C |
| CRM-004 | Communication history (all channels) | P1 | L1+L4 | Odoo `discuss` mail thread + Novu delivery logs | C |
| CRM-005 | Auto lifecycle communications | P2 | L4 | n8n scheduled workflows + Novu templates | T |
| CRM-006 | CSAT and NPS surveys (auto post-service) | P1 | L2+L4 | OCA `helpdesk_mgmt_rating` + n8n/Novu survey trigger | C |
| CRM-007 | Complaint management with escalation | P1 | L2 | OCA `helpdesk_mgmt` + `mgmtsystem_nonconformity` | C |
| CRM-008 | Duplicate customer detection and merge | P2 | L1 | Odoo `contacts` duplicate detection | S |
| CRM-009 | Privilege Program (Silver/Gold/Diamond) | P1 | L5 | CD-05 (Privilege Program module) | D |
| CRM-010 | Membership enrollment/renewal/upgrade | P1 | L5 | CD-05 | D |
| CRM-011 | Points/rewards system | P2 | L5 | CD-05 (extension) | D |
| CRM-012 | Promotional campaign with coupons | P2 | L1 | Odoo `sale` coupon/promo programs | S |
| CRM-013 | Referral program tracking | P3 | L5 | Minor custom development | D |
| CRM-014 | Lead capture (web, phone, walk-in, corporate) | P2 | L1 | Odoo `crm` leads/opportunities | S |
| CRM-015 | Corporate account management (multi-contact, multi-location) | P1 | L1+L2 | Odoo `contacts` + OCA `fieldservice_partner_multi_relation` | C |
| CRM-016 | Sales pipeline for B2B deals | P2 | L1 | Odoo `crm` pipeline | S |
| CRM-017 | Quotation for corporate with approval | P1 | L1 | Odoo `sale` quotation + approval workflow | S |
| CRM-018 | Sales forecast and revenue projection | P3 | L4 | Metabase trend analysis (BI-013) | T |

**Coverage**: L1=44% | L2=17% | L4=11% | L5=28%

### 8.5 Financial Management (FIN) — 35 Requirements

| Req # | Requirement | Priority | Layer | Technology Solution | Response |
|---|---|---|---|---|---|
| FIN-001 | Multi-branch chart of accounts | P1 | L1+L2 | Odoo `account` + OCA `account_operating_unit` | C |
| FIN-002 | Multi-cost center/profit center | P1 | L2 | OCA `account_operating_unit` (analytic accounts) | C |
| FIN-003 | General ledger with drill-down | P1 | L1 | Odoo `account` GL report | S |
| FIN-004 | Journal entries (manual + auto) | P1 | L1 | Odoo `account` journal entries | S |
| FIN-005 | Bank reconciliation | P1 | L1 | Odoo `account` bank reconciliation | S |
| FIN-006 | Multi-currency (BDT + USD) | P2 | L1 | Odoo `account` multi-currency | S |
| FIN-007 | Fixed asset management + depreciation | P2 | L2 | OCA `account_asset_management` | S |
| FIN-008 | Period-end closing with auto checks | P1 | L1 | Odoo `account` period lock | S |
| FIN-009 | Bangladesh fiscal year (July-June) | P1 | L1 | Odoo `account` configurable fiscal year | C |
| FIN-010 | Auto-invoice from completed service orders | P1 | L2 | OCA `fieldservice_account` | S |
| FIN-011 | Warranty claim invoicing to brand partners | P1 | L5 | CD-04 (Warranty Claim Automation) | D |
| FIN-012 | Corporate invoicing (configurable cycles) | P1 | L5 | CD-13 (Consolidated B2B Invoicing) | D |
| FIN-013 | AMC/RAMC subscription billing | P1 | L2 | OCA `fieldservice_agreement` + Odoo subscription | C |
| FIN-014 | Multiple payment methods recording | P1 | L1+L3 | Odoo `account` + SSLCOMMERZ/bKash/Nagad modules | S |
| FIN-015 | Advance payment/deposit management | P2 | L1 | Odoo `account` advance payments | S |
| FIN-016 | Credit note and refund management | P1 | L1 | Odoo `account` credit notes | S |
| FIN-017 | AR aging + auto payment reminders | P1 | L1+L4 | Odoo `account` aging + n8n reminder workflow | C |
| FIN-018 | Collection management with follow-up | P2 | L1 | Odoo `account` follow-up actions | S |
| FIN-019 | Vendor invoice with 3-way matching | P1 | L1 | Odoo `purchase` + `account` 3-way match | S |
| FIN-020 | Payment scheduling and batch processing | P1 | L1 | Odoo `account` scheduled payments | C |
| FIN-021 | Technician expense reimbursement | P2 | L2 | OCA `hr_expense` | S |
| FIN-022 | Vendor aging analysis | P1 | L1 | Odoo `account` AP aging report | S |
| FIN-023 | Auto payment approval workflows | P1 | L1 | Odoo `account` approval rules | C |
| FIN-024 | Bangladesh VAT calculation | P1 | L5 | CD-02 (Mushak 6.3 module) | D |
| FIN-025 | TDS per Bangladesh tax laws | P1 | L5 | CD-09 (Bangladesh TDS module) | D |
| FIN-026 | Auto VAT return preparation (Mushak) | P1 | L5 | CD-02 (extension) | D |
| FIN-027 | Tax invoice per NBR requirements | P1 | L5 | CD-02 (Mushak 6.3 invoice template) | D |
| FIN-028 | Audit trail for all financial transactions | P1 | L1+L2 | Odoo `account` audit trail + OCA `audit_log` | S |
| FIN-029 | Financial statements (Bangladesh GAAP/IFRS) | P1 | L1+L2 | Odoo `account` reports + OCA `mis_builder` | C |
| FIN-030 | Branch-wise + consolidated P&L | P1 | L2 | OCA `mis_builder` + `account_operating_unit` | C |
| FIN-031 | Revenue analysis by service/brand/branch/segment | P1 | L4 | Metabase dashboards (BI-006) | T |
| FIN-032 | Cost analysis per service order | P1 | L4 | Metabase dashboards | T |
| FIN-033 | Budget vs actual with variance | P2 | L2 | OCA `mis_builder_budget` | S |
| FIN-034 | Warranty revenue tracking/reconciliation | P1 | L5 | CD-18 (Warranty Revenue Tracker) | D |
| FIN-035 | Configurable dashboards + custom report builder | P1 | L4 | Metabase (BI-009) | T |

**Coverage**: L1=49% | L2=17% | L3=3% | L4=11% | L5=20%

### 8.6 Human Resource Management & Payroll (HRM) — 23 Requirements

| Req # | Requirement | Priority | Layer | Technology Solution | Response |
|---|---|---|---|---|---|
| HRM-001 | Employee master data | P1 | L1 | Odoo `hr` | S |
| HRM-002 | Employee lifecycle management | P1 | L1 | Odoo `hr` | S |
| HRM-003 | Org hierarchy and reporting structure | P1 | L1 | Odoo `hr` (department hierarchy) | S |
| HRM-004 | Employee document management | P2 | L1+L2 | Odoo `hr` + OCA `dms_field` | C |
| HRM-005 | Employee self-service portal | P2 | L1 | Odoo `website` + `hr` portal views | C |
| HRM-006 | Technician skill matrix | P1 | L2 | OCA `hr_employee_skill` + `fieldservice_skill` | S |
| HRM-007 | Certification tracking with expiry alerts | P1 | L2+L4 | OCA `fieldservice_skill` + n8n alert (60/30/15 days) | C |
| HRM-008 | Training management | P1 | L2 | OCA `hr_course` (training catalog) | C |
| HRM-009 | Technician performance metrics | P1 | L4+L5 | Metabase (BI-003) + CD-14 (Incentive Calculator) | T |
| HRM-010 | Technician ranking/leaderboard | P2 | L4 | Metabase dashboard | T |
| HRM-011 | Shift management and roster planning | P1 | L5 | CD-15 (Shift & Roster Management) | D |
| HRM-012 | Attendance with biometric/mobile clock-in | P1 | L1+L3 | Odoo `hr_attendance` + biometric integration (INT-028) | C |
| HRM-013 | GPS-based attendance for field technicians | P2 | L2 | OCA `hr_attendance_geolocation` | S |
| HRM-014 | Leave management (all types + accruals) | P1 | L1 | Odoo `hr_holidays` | S |
| HRM-015 | Bangladesh public holiday calendar | P1 | L2 | OCA `hr_holidays_public` | S |
| HRM-016 | Overtime tracking and approval | P1 | L5 | CD-20 (Overtime Approval Module) | D |
| HRM-017 | Payroll processing | P1 | L2+L5 | OCA `hr_payroll_community` + CD-03 (BD Payroll) | D |
| HRM-018 | Salary structure (basic + allowances) | P1 | L5 | CD-03 | D |
| HRM-019 | Incentive/commission from performance | P1 | L5 | CD-14 (Performance Incentive Calculator) | D |
| HRM-020 | Statutory deductions (tax + PF) | P1 | L5 | CD-03 (Bangladesh tax slabs, provident fund) | D |
| HRM-021 | Bank salary transfer file (BEFTN) | P1 | L5 | CD-03 (BEFTN file generation) | D |
| HRM-022 | Payslip generation and distribution | P1 | L5 | CD-03 (digital payslips via email/portal) | D |
| HRM-023 | Annual tax certificate (NBR) | P2 | L5 | CD-03 (extension) | D |

**Coverage**: L1=22% | L2=26% | L4=9% | L5=43%

### 8.7 Contract & Warranty Management (CWM) — 22 Requirements

| Req # | Requirement | Priority | Layer | Technology Solution | Response |
|---|---|---|---|---|---|
| CWM-001 | AMC creation with configurable terms | P1 | L2 | OCA `fieldservice_agreement` | C |
| CWM-002 | RAMC management (6 packages) | P1 | L2+L5 | OCA `fieldservice_agreement` + custom config | C |
| CWM-003 | Corporate AMC (multi-location, multi-device) | P1 | L2 | OCA `fieldservice_agreement` + `partner_multi_relation` | C |
| CWM-004 | Contract lifecycle (draft → active → expired) | P1 | L2 | OCA `fieldservice_agreement` | S |
| CWM-005 | Auto scheduled maintenance from AMC | P1 | L2 | OCA `fieldservice_recurring` + `fieldservice_maintenance` | S |
| CWM-006 | Contract utilization tracking | P1 | L2 | OCA `fieldservice_agreement` (visits tracking) | C |
| CWM-007 | Renewal alerts (60/30/15 days) | P1 | L4 | n8n scheduled workflow + Novu notification | T |
| CWM-008 | Contract profitability analysis | P2 | L4 | Metabase (BI dashboard) | T |
| CWM-009 | Device warranty registration/tracking | P1 | L2 | OCA `fieldservice_equipment_warranty` | S |
| CWM-010 | Auto warranty status verification | P1 | L2+L5 | OCA `fieldservice_equipment_warranty` + CD-04 | C |
| CWM-011 | Warranty claim creation/submission | P1 | L5 | CD-04 (Warranty Claim Automation) | D |
| CWM-012 | Warranty claim lifecycle tracking | P1 | L5 | CD-04 (pipeline: submitted → approved → paid) | D |
| CWM-013 | Warranty claim documentation | P1 | L5 | CD-04 (auto-attach photos, diag report, parts list) | D |
| CWM-014 | Warranty revenue reconciliation | P1 | L5 | CD-18 (Warranty Revenue Tracker) | D |
| CWM-015 | Extended warranty enrollment | P1 | L2+L5 | OCA `fieldservice_equipment_warranty` + custom product | C |
| CWM-016 | Warranty extension pricing/billing | P1 | L1 | Odoo `sale` + product pricing | C |
| CWM-017 | Brand-specific warranty terms config | P2 | L5 | CD-04 (configurable per-brand templates for 17+ partners) | D |
| CWM-018 | SLA definition per type/tier/contract/brand | P1 | L2 | OCA `helpdesk_mgmt_sla` | C |
| CWM-019 | SLA metrics (response, resolution, FTFR) | P1 | L2 | OCA `helpdesk_mgmt_sla` | C |
| CWM-020 | Real-time SLA monitoring dashboard | P1 | L4 | Metabase (SLA Compliance Dashboard) | T |
| CWM-021 | SLA escalation matrix (50/75/90/100%) | P1 | L2+L4 | OCA `helpdesk_mgmt_sla` + n8n escalation | C |
| CWM-022 | SLA compliance reporting | P1 | L4 | Metabase (per branch/tech/brand/contract) | T |

**Coverage**: L1=5% | L2=40% | L4=18% | L5=37%

### 8.8 Procurement & Supply Chain (SCM) — 12 Requirements

| Req # | Requirement | Priority | Layer | Technology Solution | Response |
|---|---|---|---|---|---|
| SCM-001 | Vendor master with classification | P1 | L1 | Odoo `purchase` (vendor categorization) | S |
| SCM-002 | Vendor qualification/onboarding | P2 | L1 | Odoo `purchase` approval workflow | C |
| SCM-003 | Vendor performance scorecard | P1 | L1+L4 | Odoo `purchase` metrics + Metabase dashboard | C |
| SCM-004 | Vendor contract management | P1 | L1 | Odoo `purchase` (blanket orders, pricing agreements) | S |
| SCM-005 | Vendor document management | P2 | L2 | OCA `dms_field` on vendor records | C |
| SCM-006 | Purchase requisition with approval | P1 | L1+L2 | Odoo `purchase` + OCA `purchase_operating_unit` | C |
| SCM-007 | Purchase order creation/management | P1 | L1 | Odoo `purchase` | S |
| SCM-008 | Auto PO from reorder alerts | P2 | L1 | Odoo `stock` reorder rules → auto-create draft PO | S |
| SCM-009 | Purchase price comparison | P2 | L1 | Odoo `purchase` (RFQ comparison) | S |
| SCM-010 | Goods receipt + quality inspection | P1 | L1 | Odoo `stock` (receipt + quality check) | S |
| SCM-011 | 3-way matching (PO → GRN → Invoice) | P1 | L1 | Odoo `purchase` + `account` 3-way match | S |
| SCM-012 | Return to vendor (RTV) | P1 | L1 | Odoo `stock` (vendor return shipments) | S |

**Coverage**: L1=75% | L2=17% | L4=8%

### 8.9 Reporting & Business Intelligence (BI) — 14 Requirements

| Req # | Requirement | Priority | Layer | Technology Solution | Response |
|---|---|---|---|---|---|
| BI-001 | Executive dashboard with real-time KPIs | P1 | L4 | Metabase (Executive Dashboard) | T |
| BI-002 | Branch performance dashboard (51+ locations) | P1 | L4 | Metabase (Branch Performance Dashboard) | T |
| BI-003 | Technician performance analytics | P1 | L4 | Metabase (Technician Scorecard) | T |
| BI-004 | Service analytics (TAT, common issues, rework) | P1 | L4 | Metabase (Service Analytics) | T |
| BI-005 | Inventory analytics | P1 | L4 | Metabase (Inventory Dashboard) | T |
| BI-006 | Financial analytics | P1 | L4 | Metabase (Financial Dashboard) | T |
| BI-007 | Customer analytics (acquisition, retention, LTV) | P2 | L4 | Metabase (Customer Analytics) | T |
| BI-008 | Warranty analytics | P1 | L4 | Metabase (Warranty Claims Dashboard) | T |
| BI-009 | Custom report builder (drag-and-drop) | P1 | L4 | Metabase native question builder | T |
| BI-010 | Scheduled reports + email distribution | P1 | L4 | Metabase scheduled alerts + email | T |
| BI-011 | Export: PDF, Excel, CSV | P1 | L2+L4 | OCA `report_xlsx`/`report_qweb_pdf` + Metabase export | S |
| BI-012 | Ad-hoc query for power users | P2 | L2+L4 | OCA `bi_sql_editor` + Metabase SQL mode | T |
| BI-013 | Predictive analytics (demand forecasting) | P3 | L4 | Metabase trend analysis + custom SQL | T |
| BI-014 | Metabase/equivalent BI tool integration | P2 | L4 | Metabase (direct PostgreSQL connection to read replica) | T |

**Coverage**: L2=7% | L4=93%

### 8.10 Document Management (DMS) — 8 Requirements

| Req # | Requirement | Priority | Layer | Technology Solution | Response |
|---|---|---|---|---|---|
| DMS-001 | Centralized storage with version control | P1 | L2+L4 | OCA `dms` (Phase 1-4) + Mayan EDMS (Phase 5+) | S |
| DMS-002 | Document categorization | P1 | L2 | OCA `dms` (categories, tags) | S |
| DMS-003 | Digital form builder | P2 | L5 | CD-11 (Diagnostic Checklist Builder — adaptable) | D |
| DMS-004 | E-signature capture and verification | P1 | L4+L5 | Mayan EDMS + CD-01 (Flutter e-signature) | T |
| DMS-005 | Document approval workflows | P1 | L2+L4 | OCA `dms` + Mayan EDMS workflow engine | C |
| DMS-006 | Document templates | P1 | L2 | OCA `dms_field` (templates per record type) | S |
| DMS-007 | Bulk scanning and OCR | P3 | L4 | Mayan EDMS (Tesseract OCR — Bengali supported) | T |
| DMS-008 | Retention policies and auto-archiving | P2 | L4 | Mayan EDMS (retention policy engine) | T |

**Coverage**: L2=50% | L4=25% | L5=25%

### 8.11 Quality Management (QMS) — 8 Requirements

| Req # | Requirement | Priority | Layer | Technology Solution | Response |
|---|---|---|---|---|---|
| QMS-001 | ISO 9001:2015 compliance tracking | P1 | L2 | OCA `mgmtsystem_quality` + `mgmtsystem_review` | S |
| QMS-002 | Internal audit management | P2 | L2 | OCA `mgmtsystem_audit` | S |
| QMS-003 | Non-conformance report (NCR) | P2 | L2 | OCA `mgmtsystem_nonconformity` | S |
| QMS-004 | CAPA tracking | P2 | L2 | OCA `mgmtsystem_action` | S |
| QMS-005 | Customer complaint with root cause analysis | P1 | L2 | OCA `helpdesk_mgmt` + `mgmtsystem_nonconformity_repair` | C |
| QMS-006 | Service quality scoring per tech/branch | P1 | L2+L4 | OCA `fieldservice_quality_control` + Metabase | C |
| QMS-007 | SOP management with version control | P2 | L2+L4 | OCA `mgmtsystem_review` + Mayan EDMS | C |
| QMS-008 | Quality KPI dashboards | P1 | L4 | Metabase (rework rate, complaints, SLA, CSAT) | T |

**Coverage**: L2=75% | L4=25%

### 8.12 Smart Portal Suite — 74 Requirements

| Portal | Req Range | Technology | Layer | Phase |
|---|---|---|---|---|
| Customer Self-Service (CSP-001 to CSP-017) | 17 reqs | Next.js 15 + Payload CMS 3 + Odoo JSON-2 API | CON-03 + L1 API | 1-3 |
| Technician Mobile (TMP-001 to TMP-017) | 17 reqs | Custom Flutter App (CD-01) | L5 | 2 |
| Admin Operations (AOP-001 to AOP-012) | 12 reqs | Odoo CE backend (OWL) + custom views | L1+L2 | 1-2 |
| Corporate B2B (B2B-001 to B2B-010) | 10 reqs | Next.js 15 + Odoo JSON-2 API | CON-03 + L1 API | 4 |
| Vendor & Partner (VPP-001 to VPP-008) | 8 reqs | Odoo CE portal module + custom views | L1 | 4 |
| Analytics Dashboard (ABD-001 to ABD-010) | 10 reqs | Metabase embedded dashboards (iframe/JWT): ABD-001 exec KPIs, ABD-002 real-time ops, ABD-003 financial, ABD-004 customer, ABD-005 branch comparison, ABD-006 trend analysis, ABD-007 drill-down, ABD-008 custom builder, ABD-009 mobile-responsive, ABD-010 threshold alerts | L4 | 2-5 |

### 8.13 Overall Coverage Summary

| Module | Total Reqs | L1 (Odoo CE) | L2 (OCA) | L3 (Third-Party) | L4 (Open Source) | L5 (Custom) |
|---|---|---|---|---|---|---|
| SRM | 37 | 30% | 43% | — | 5% | 22% |
| FSM | 31 | — | 23% | — | 10% | 67% |
| INV | 24 | 71% | 17% | — | 4% | 8% |
| CRM | 18 | 44% | 17% | — | 11% | 28% |
| FIN | 35 | 49% | 17% | 3% | 11% | 20% |
| HRM | 23 | 22% | 26% | — | 9% | 43% |
| CWM | 22 | 5% | 40% | — | 18% | 37% |
| SCM | 12 | 75% | 17% | — | 8% | — |
| BI | 14 | — | 7% | — | 93% | — |
| DMS | 8 | — | 50% | — | 25% | 25% |
| QMS | 8 | — | 75% | — | 25% | — |
| Portals | 74 | 20% | 10% | — | 15% | 55% |
| **TOTAL** | **306 functional** | **~30%** | **~27%** | **~1%** | **~15%** | **~27%** |

**Non-functional requirements** (TECH: 38, INT: 31, SEC: 22, MIG: 9, TRN: 9 = 109 additional) are addressed across all layers as documented in Sections 9-15.

**Grand Total**: 405 requirements — 100% coverage across the 5-layer stack.

---

## 9. INTEGRATION ARCHITECTURE

### 9.1 Integration Principles

| # | Principle | Implementation |
|---|---|---|
| 1 | **API-First** | All integrations via documented REST/JSON-2 APIs (TECH-036) |
| 2 | **Event-Driven** | Webhooks from Odoo trigger n8n workflows (INT-005) |
| 3 | **n8n as Orchestration Hub** | All cross-system workflows routed through n8n |
| 4 | **OAuth 2.0 Authentication** | All API calls authenticated via Keycloak-issued tokens |
| 5 | **JSON Format** | Standard JSON request/response bodies |
| 6 | **Versioned Endpoints** | `/json/2/` prefix for Odoo API versioning |
| 7 | **Idempotent Operations** | All write operations support idempotency keys |
| 8 | **Rate Limiting** | Nginx enforces per-client rate limits |

### 9.2 Integration Catalog

| # | Integration | Systems | Direction | Protocol | Data Exchanged | Auth | Frequency | Phase | Requirement |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ERP ↔ Web Platform | Odoo ↔ Next.js 15 | Bidirectional | REST JSON-2 + Webhooks | Service orders, customers, devices, invoices, payments, booking slots | OAuth 2.0 | Real-time | 1 | INT-001 to INT-006 |
| 2 | ERP ↔ bKash | Odoo ↔ bKash API | Bidirectional | REST | Payment requests, OTP verification, confirmations, reconciliation | API Key + OAuth | Real-time | 3 | INT-007 |
| 3 | ERP ↔ Nagad | Odoo ↔ Nagad (via SSLCOMMERZ) | Bidirectional | REST | Payment requests, confirmations | API Key | Real-time | 3 | INT-008 |
| 4 | ERP ↔ SSLCOMMERZ | Odoo ↔ SSLCOMMERZ API | Bidirectional | REST | Card/net-banking payments, refunds | API Key | Real-time | 3 | INT-009 |
| 5 | ERP ↔ Rocket | Odoo ↔ SSLCOMMERZ (aggregated) | Bidirectional | REST | Mobile banking payments | API Key | Real-time | 3 | INT-010 |
| 6 | ERP → SMS Gateway | Odoo → n8n → Novu → MuthoSMS/GreenWeb | Outbound | REST | Transactional SMS (Bengali templates) | API Key | Event-driven | 1 | INT-013 |
| 7 | ERP → Email | Odoo → n8n → Novu → SMTP | Outbound | SMTP/REST | Invoices, reminders, reports | SMTP credentials | Event-driven | 1 | INT-014 |
| 8 | ERP ↔ WhatsApp | Odoo → n8n → Novu → WhatsApp Cloud API | Bidirectional | REST | Notifications, booking confirmations, chatbot | Meta API Token | Event-driven | 1 | INT-015 |
| 9 | ERP → Push | Odoo → n8n → Novu → Firebase | Outbound | REST | Push notifications to mobile app | Firebase API Key | Event-driven | 2 | INT-016 |
| 10 | ERP ↔ Google Maps | Odoo ↔ Google Maps Platform | Bidirectional | REST | Geocoding, directions, distance matrix, map embed | API Key | On-demand | 2 | INT-018 |
| 11 | ERP ↔ Route Optimizer | Odoo ↔ VROOM/OSRM | Bidirectional | HTTP API | Job locations, technician positions → optimized routes | Internal | Scheduled (5 AM) + on-demand | 2 | INT-019 |
| 12 | ERP ↔ Traffic Data | Odoo ↔ Google Routes API | Inbound | REST | Real-time traffic for Dhaka metro ETA | API Key | On-demand | 2 | INT-020 |
| 13 | ERP ↔ Geo-fencing | Odoo ↔ Traccar | Bidirectional | REST | Zone boundaries, enter/exit events | Internal | Real-time | 2 | INT-021 |
| 14 | ERP ↔ AI Chatbot | Odoo ↔ Ollama/LangChain | Bidirectional | REST | Customer intents, booking creation, status queries | Internal | Real-time | 6 | INT-022 |
| 15 | ERP ↔ AI Dispatch | Odoo ↔ VROOM + CD-06 | Bidirectional | HTTP API | Technician assignments, optimization scores | Internal | Scheduled + event | 2 | INT-023 |
| 16 | Biometric → ERP | Biometric devices → Odoo | Inbound | File/SDK | Clock-in/out timestamps | Device auth | Scheduled (hourly) | 5 | INT-028 |
| 17 | ERP ↔ Barcode Printers | Odoo → Printers | Outbound | ZPL/ESC-POS | Inventory labels, service order labels | Local network | On-demand | 1 | INT-029 |
| 18 | ERP ↔ Cloud Storage | Odoo ↔ Cloudinary | Bidirectional | REST | Photo upload/thumbnail generation | API Key | On-demand | 1 | INT-030 |
| 19 | ERP ↔ Metabase | Odoo DB → Metabase | Inbound (read) | PostgreSQL | Direct database read (read replica) | DB credentials | Continuous (15 min refresh) | 2 | INT-031 |
| 20 | ERP ↔ Traccar | Odoo ↔ Traccar Server | Bidirectional | REST + WebSocket | Technician GPS positions, events | Internal | Real-time (30s) | 2 | FSM-003 |
| 21 | ERP ↔ Keycloak | Odoo ↔ Keycloak | Bidirectional | SAML 2.0 / OIDC | Authentication tokens, user roles, sessions | SAML/OIDC | Per-login | 1 | SEC-003 |
| 22 | ERP ↔ Mayan EDMS | Odoo ↔ Mayan EDMS | Bidirectional | REST | Document metadata, file links, approval status | OAuth 2.0 | Event-driven | 5 | DMS-001 |
| 23 | Mobile App ↔ ERP | Flutter ↔ Odoo JSON-2 API | Bidirectional | REST JSON-2 | Jobs, forms, photos, signatures, parts, time entries | OAuth 2.0 + PKCE | Real-time + sync | 2 | TMP-001 to TMP-017 |
| 24 | Mobile App ↔ Traccar | Flutter → Traccar Client | Outbound | GPS protocol | GPS coordinates every 30 seconds | Device auth | Continuous | 2 | FSM-003 |

### 9.3 Webhook Event Specification

| Event | Trigger | Payload | Consumers | Requirement |
|---|---|---|---|---|
| `service_order.created` | New service order in Odoo | Order ID, customer, device, type, priority | n8n → Novu (customer SMS) + Next.js (portal update) | SRM-001, SRM-014 |
| `service_order.status_changed` | Status transition | Order ID, old status, new status, timestamp | n8n → Novu (customer notification) | SRM-014, CSP-003 |
| `technician.dispatched` | Technician assigned to job | Order ID, tech ID, ETA | n8n → Novu (customer SMS + tech push) | FSM-028 |
| `technician.status_changed` | Tech status: en route/arrived/working/done | Tech ID, status, timestamp, GPS | n8n → Novu (customer SMS) + Next.js (tracking) | FSM-020, FSM-028 |
| `invoice.created` | Auto-invoice generated | Invoice ID, amount, payment methods | n8n → Novu (email invoice + bKash link) | FIN-010 |
| `payment.received` | Payment confirmed | Payment ID, method, amount, invoice ID | Odoo accounting reconciliation | INT-011 |
| `warranty_claim.created` | Auto-claim generated | Claim ID, brand, serial, docs | n8n → brand partner submission | CWM-011 |
| `warranty_claim.status_changed` | Brand response received | Claim ID, status, amount | Odoo reconciliation + Metabase | CWM-012 |
| `sla.warning` | SLA at 50/75/90% threshold | Order ID, SLA %, remaining time | n8n → Novu (manager alert) | SRM-010, CWM-021 |
| `sla.breached` | SLA 100% exceeded | Order ID, SLA type, breach duration | n8n → Novu (escalation chain) | SRM-010, CWM-021 |
| `stock.reorder_alert` | Stock below reorder point | Product ID, location, current qty, reorder qty | n8n → Novu (inventory alert) + auto-PR | INV-012, INV-018 |
| `contract.expiring` | AMC/RAMC 60/30/15 days to expiry | Contract ID, customer, expiry date | n8n → Novu (renewal reminder) | CWM-007 |
| `payroll.approved` | Monthly payroll finalized | Payroll batch ID, employee count | n8n → BEFTN file generation | HRM-021 |

### 9.4 Next.js 15 + Payload CMS 3 Integration Detail (CON-03)

The existing 1000FiX web platform (CON-03 — cannot be replaced) uses the following stack:

| Component | Technology | Notes |
|---|---|---|
| Frontend | Next.js 15 + React 19 + Tailwind CSS + shadcn/ui | Server-side rendering, responsive |
| CMS | Payload CMS 3.x | Content management, admin UI |
| Database | PostgreSQL 16 + TimescaleDB | Shared DB technology (separate instance from Odoo) |
| Cache | Redis 7 | Shared technology with Odoo stack |
| ORM | Drizzle ORM | TypeScript-first ORM |
| Real-time | Socket.io | Live tracking, notifications |
| Queue | BullMQ | Background job processing |
| Hosting | Vercel (frontend) + DigitalOcean (backend) + Cloudflare (CDN) | — |

**Integration Points**:
- **Shared SSO**: Keycloak provides OIDC tokens for both Odoo and Next.js (INT-006)
- **API Communication**: Next.js calls Odoo JSON-2 API for all ERP data (INT-001)
- **Webhooks**: Odoo pushes events to Next.js endpoint for real-time updates (INT-005)
- **Shared PostgreSQL Technology**: Both use PostgreSQL 16, but maintain separate database instances
- **Shared Redis**: Redis 7 used by both platforms for caching and queues

---

## 10. SECURITY ARCHITECTURE

### 10.1 Security Requirements Traceability

| Req # | Requirement | Priority | Technology Component | Implementation |
|---|---|---|---|---|
| SEC-001 | RBAC with field-level granularity | P1 | Keycloak + Odoo CE groups/rules | 20 roles configured; Odoo ir.rule for record-level; field-level via custom access |
| SEC-002 | MFA for all users | P1 | Keycloak TOTP | Mandatory for admin/finance (roles 1-4, 8-10, 14, 20); optional for others |
| SEC-003 | SSO (SAML 2.0, OAuth 2.0, OIDC) | P2 | Keycloak | SSO across Odoo, Next.js, Metabase, Grafana, Mayan EDMS, n8n |
| SEC-004 | Password policies | P1 | Keycloak | Min 12 chars, complexity, 90-day expiry, 5-password history |
| SEC-005 | Session management | P1 | Keycloak + Odoo | 30-min idle timeout, max 3 concurrent sessions, forced logout |
| SEC-006 | IP-based restrictions for admin | P2 | Nginx + Keycloak | Whitelist IPs for admin portal access via Nginx rules |
| SEC-007 | Branch-level data isolation | P1 | OCA `operating_unit` | Users see only own branch data; cross-branch requires explicit grant |
| SEC-008 | AES-256 encryption at rest | P1 | PostgreSQL (managed) | DigitalOcean managed DB with encryption at rest enabled |
| SEC-009 | TLS 1.2+ in transit | P1 | Nginx | TLS 1.2+ termination; HSTS headers; A+ SSL Labs rating target |
| SEC-010 | Database encryption with key mgmt | P1 | PostgreSQL (managed) | Managed key rotation by cloud provider |
| SEC-011 | PII masking for non-production | P1 | Custom script | Anonymization script run on staging/dev DB copies |
| SEC-012 | Backup encryption | P1 | DigitalOcean + custom | Encrypted backup storage; GPG encryption for off-site copies |
| SEC-013 | Secure file upload + malware scan | P2 | Nginx + ClamAV | ClamAV daemon scanning uploads before storage |
| SEC-014 | Complete audit trail (who/what/when/before-after) | P1 | OCA `audit_log` + Odoo `mail.tracking` | All CRUD operations logged with field-level change tracking |
| SEC-015 | Tamper-protected immutable logs | P1 | Append-only PostgreSQL table + log forwarding | Audit logs in append-only table; forwarded to separate log store |
| SEC-016 | ISO 27001 alignment | P1 | OCA `mgmtsystem` + operational controls | Security controls documented per ISO 27001 Annex A |
| SEC-017 | SOC 2 Type II | P2 | Operational controls | Cloud provider SOC 2; organizational controls documented |
| SEC-018 | Bangladesh ICT Act compliance | P1 | Organizational + technical | Data handling per ICT Act 2006 provisions |
| SEC-019 | GDPR-compatible privacy controls | P3 | Odoo CE + Keycloak | Data subject access/deletion rights; consent management |
| SEC-020 | Annual penetration testing | P1 | External vendor | Annual pentest scheduled; Phase 6 includes initial pentest |
| SEC-021 | Vulnerability management + patching | P1 | Operational | Monthly OS/dependency updates; CVE monitoring; 48hr critical patch SLA |
| SEC-022 | Configurable data retention/deletion | P1 | Odoo + Mayan EDMS | Per-type retention policies (see §10.3 below) |

### 10.2 Data Retention Policies (SEC-022)

| Data Type | Retention Period | Legal Basis | Technology |
|---|---|---|---|
| Customer records | 7 years after last transaction | Bangladesh business law | Odoo `contacts` + archival policy |
| Financial transactions | 7 years | Bangladesh Companies Act / NBR | Odoo `account` + PostgreSQL partitioning |
| Service records | 5 years | Operational + warranty | Odoo + Mayan EDMS archival |
| Warranty claims | 7 years | Brand partner audit requirements | Odoo + Mayan EDMS |
| Employee records | 10 years after termination | Bangladesh Labour Act | Odoo `hr` + Mayan EDMS |
| Audit logs | 5 years | ICT Act / ISO 27001 | Append-only PostgreSQL table |

### 10.3 Compliance Matrix

| Standard/Regulation | Requirement Source | Technology Components | Status |
|---|---|---|---|
| **ISO 9001:2015** | QMS-001 to QMS-008 | OCA `mgmtsystem_quality`, `mgmtsystem_audit`, `mgmtsystem_action` | Supported |
| **ISO 27001** | SEC-016 | Keycloak, encryption, audit trails, access controls | Aligned |
| **Bangladesh ICT Act 2006** | SEC-018 | Data handling, storage, access controls | Compliant |
| **Bangladesh Digital Security Act 2018** | BRD §16 | Data privacy, security controls | Compliant |
| **NBR VAT (Mushak)** | FIN-024 to FIN-027 | CD-02 (Mushak 6.3 module) | Custom Dev |
| **NBR Income Tax** | HRM-020 | CD-03 (Bangladesh Payroll) | Custom Dev |
| **Bangladesh Labour Act** | HRM data retention | Odoo `hr` + 10-year retention policy | Configured |
| **Bangladesh Companies Act** | Financial retention | Odoo `account` + 7-year retention | Configured |

---

## 11. INFRASTRUCTURE & PERFORMANCE

### 11.1 Server Sizing Specification

| Component | vCPU | RAM | Storage | Monthly Cost | Requirements Served |
|---|---|---|---|---|---|
| **Odoo App Server 1** | 8 | 16-32 GB | 100 GB SSD | $100-160 | TECH-004, TECH-014, TECH-011 |
| **Odoo App Server 2** | 8 | 16-32 GB | 100 GB SSD | $100-160 | TECH-004, TECH-009 (load balancing) |
| **PostgreSQL Primary** | 8 | 32 GB | 500 GB SSD | $150-250 | All data storage requirements |
| **PostgreSQL Read Replica** | 8 | 32 GB | 500 GB SSD | Included | BI-001 to BI-014, TECH-013 |
| **PgBouncer** | Shared | Shared | — | — | TECH-014 (connection pooling) |
| **Redis 7** | 2 | 4 GB | — | Shared | TECH-017 (session cache, queue) |
| **Supporting Services Server** | 8 | 16 GB | 200 GB SSD | $80-160 | Metabase, Traccar, n8n, Keycloak, VROOM/OSRM, Novu, Mayan EDMS |
| **Backup Storage** | — | — | 500 GB | $25-50 | TECH-007 (DR), SEC-012 |
| **CDN (Cloudflare)** | — | — | — | $0-20 | TECH-015 (50K+ portal users) |
| **TOTAL** | **34+** | **132+ GB** | **1.4+ TB** | **$465-820/mo** | — |

### 11.2 Performance Justification

| Requirement | Target | Architecture Solution | How It Meets Target |
|---|---|---|---|
| TECH-011 | Page load < 3 seconds | Nginx caching + CDN + PgBouncer + Redis session | Static assets cached at edge; dynamic pages rendered in <1.5s; DB queries via connection pool |
| TECH-012 | API response < 500ms (p95) | Odoo JSON-2 API + PgBouncer + Redis | JSON-2 API optimized in v19; connection pooling eliminates DB wait; read replica for heavy queries |
| TECH-013 | Report generation < 30 seconds | Metabase on read replica + materialized views | Reports query read replica; materialized views pre-computed every 15 minutes for complex aggregations |
| TECH-014 | 500+ concurrent internal users | 2x app servers × 10-12 workers = 20-24 workers + PgBouncer | Each worker handles 1 request; 24 workers serve 24 concurrent requests with <2s avg response; queue handles bursts |
| TECH-015 | 50,000+ concurrent portal users | Cloudflare CDN + Nginx caching + dedicated portal workers | Static content served from CDN; dynamic API calls load-balanced; portal pages are 90% cacheable |
| TECH-016 | Batch processing 10,000+ records | Dedicated cron workers + PostgreSQL COPY | 2 cron workers per server; bulk operations use PostgreSQL COPY for 10x throughput |
| TECH-017 | Real-time sync < 5 seconds | Webhooks + n8n + Redis pub/sub | Odoo fires webhook → n8n processes in <500ms → target system updated; Redis pub/sub for inter-service events |

### 11.3 Scalability Plan (5-Year Growth)

| Metric | Year 1 | Year 3 | Year 5 | Scaling Method |
|---|---|---|---|---|
| Internal users | 500-900 | 1,200 | 2,500 | Add app server nodes behind Nginx |
| Portal users/month | 250,000 | 500,000 | 1,250,000 | CDN + cache layer scaling |
| Service orders/day | 500-1,000 | 2,000 | 5,000 | PostgreSQL partitioning by date |
| Service order records (total) | 500,000 | 1,500,000 | 3,000,000 | Archival strategy (data > 2yr → archive partition) |
| Service centers | 51 | 80 | 150 | Operating unit configuration (no code change) |
| Technicians | 200-400 | 600 | 1,000 | Flutter app scales linearly; Traccar supports 10,000+ |
| PostgreSQL DB size | 50 GB | 200 GB | 500 GB | Vertical scale to 16vCPU/64GB; add read replicas |
| Odoo Workers | 20-24 | 36-48 | 60-80 | Add app server nodes (horizontal) |

### 11.4 High Availability & Disaster Recovery

| Metric | Target | Implementation | Requirement |
|---|---|---|---|
| **Uptime SLA** | 99.9% during business hours (9 AM – 10 PM BST) | 2 app servers with Nginx health checks; auto-restart on failure | TECH-006 |
| **RPO** | < 1 hour | WAL-based streaming replication to read replica; 15-minute backup snapshots | TECH-007 |
| **RTO** | < 4 hours | Documented recovery procedures; automated failover scripts; quarterly DR drills | TECH-007 |
| **Data Center** | Singapore (DigitalOcean) | < 50ms network latency to Dhaka | TECH-008 |
| **Backup Schedule** | Daily (30-day retention) + Weekly (1-year retention) | Automated via DigitalOcean managed backups + custom scripts | SEC-012 |
| **Backup Testing** | Quarterly restore test | Full DB restore to staging; data validation against production | TECH-007 |

### 11.5 Monitoring & Alerting

| Tool | Function | Alert Conditions |
|---|---|---|
| **Grafana** | Server metrics, PostgreSQL performance, API latency, Odoo worker health | CPU > 80%, Memory > 85%, Disk > 90%, API p95 > 500ms, DB connections > 80% pool |
| **Prometheus** | Metrics collection from all Docker containers | Container restart, health check failure |
| **Sentry** | Application error tracking, bug reporting | Exception rate > threshold, new error types |
| **n8n Alerting** | Business metric alerts | SLA breach count > 0, jobs backlog > threshold |
| **Uptime Robot / Similar** | External uptime monitoring | Any portal/API endpoint down > 30 seconds |

---

## 12. LOCALIZATION & ACCESSIBILITY

### 12.1 Bengali Language Technology

| Requirement | Implementation | Technology |
|---|---|---|
| TECH-025: Full Bengali UI | 100% UI string translation — no English fallback for Bengali-mode users | Odoo .po translation files + Flutter arb files |
| TECH-026: English as secondary | Full English UI available as secondary language | Odoo native + Next.js i18n |
| TECH-027: User-level language switching | Per-user language preference stored in Keycloak profile | Keycloak user attributes → Odoo/Next.js/Flutter |
| TECH-028: Bengali Unicode | Full Unicode support for all text fields, reports, and data entry | PostgreSQL UTF-8 encoding, Odoo Unicode fields |
| URD §13.2: Bengali keyboard | Avro and Bijoy keyboard layout support | OS-level input methods (no app-level action needed) |
| URD §13.2: Bengali voice-to-text | Voice input for technician notes | Android native Speech-to-Text API (Bengali) |
| URD §13.2: Bengali font | Kalpurush or SolaimanLipi at minimum 16px | CSS @font-face in Odoo OWL + Flutter custom fonts |
| URD §14.4: Bengali SMS templates | All transactional SMS in Bengali | Novu template management with Bengali locale |

### 12.2 Date, Time, Currency & Number Formatting

| Requirement | Format | Technology |
|---|---|---|
| TECH-029: Bangladesh date format | DD/MM/YYYY throughout all modules | Odoo `res.lang` locale configuration |
| URD §13.3: Time format | 12-hour AM/PM | Odoo locale + Flutter DateFormat |
| TECH-030: BDT currency | ৳ symbol, lakh format (৳1,23,456) | Odoo `res.currency` + custom number format |
| TECH-031: Phone validation | +880 and 01X prefix formats | CD-12 (Bangladesh Address Fields) + regex validation |

### 12.3 Accessibility (WCAG 2.1 AA)

| Requirement | Standard | Implementation |
|---|---|---|
| TECH-024 | WCAG 2.1 AA compliance | Applied to all portal interfaces |
| URD §12.5 | 4.5:1 color contrast ratio | Tailwind CSS custom theme (Next.js), OWL theme customization (Odoo) |
| URD §12.5 | Screen reader support | ARIA labels on all interactive elements |
| URD §12.5 | Keyboard navigation | Tab order, focus indicators on all inputs and buttons |
| URD §12.3 | 44×44px touch targets | Mobile-first CSS with minimum tap target sizing |
| URD §12.3 | 16px mobile body text | CSS `font-size: 16px` on mobile breakpoints |
| URD §12.3 | Bottom navigation (mobile) | Flutter app: bottom nav bar for thumb accessibility |
| URD §12.3 | Single-direction scrolling | No horizontal scroll on any portal page |

### 12.4 Device & Browser Support Matrix

| Device | OS | Browsers | Users | Priority |
|---|---|---|---|---|
| Windows Desktop | Windows 10+ | Chrome, Firefox, Edge | Service Center Agents, Finance, HR | P1 |
| Android Smartphone | Android 11+ | Chrome (portal), Flutter app (technician) | Field Technicians, Branch Managers | P1 |
| Android Tablet | Android 11+ | Chrome | Warehouse staff (barcode scanning) | P1 |
| iPhone / iPad | iOS 15+ | Safari, Chrome | CEO, tech-savvy customers, Corporate clients | P2 |
| Feature Phone | Any | SMS-only interaction | Elderly/low-tech customers | P1 (SMS) |

### 12.5 Low-Bandwidth Optimization

| Technique | Implementation | Requirement |
|---|---|---|
| Image compression | All uploaded images ≤ 200KB via Cloudinary transformation | TECH-023, URD §13.6 |
| Lazy loading | Images and non-critical resources load on scroll | TECH-023 |
| Pagination | All list views paginated (20 items default) | TECH-023 |
| Data compression | gzip/brotli compression on all Nginx responses | TECH-023 |
| Offline-first mobile | SQLite/Hive local DB with background sync | TECH-020, TECH-023 |
| 3G compatibility | Flutter app functional on 3G (no WiFi dependency) | URD §13.6 |

---

## 13. SMART PORTAL SUITE TECHNOLOGY

### 13.1 Customer Self-Service Portal (CSP-001 to CSP-017)

| Attribute | Specification |
|---|---|
| **Technology** | Next.js 15 + Payload CMS 3 + PostgreSQL 16 (existing platform — CON-03) |
| **Integration** | Odoo JSON-2 API + webhooks |
| **Authentication** | Keycloak OIDC via NextAuth.js |
| **Languages** | Bengali (primary) + English |
| **Responsiveness** | Desktop, tablet, mobile (PWA capable) |
| **Phase** | Phase 1 (basic booking), Phase 2 (tracking), Phase 3 (payments) |

| Req # | Feature | Implementation |
|---|---|---|
| CSP-001 | Registration/login (email, phone, social) | Keycloak registration flow with social identity providers |
| CSP-002 | Service request wizard | Next.js multi-step form → Odoo JSON-2 API (POST /service.order) |
| CSP-003 | Real-time tracking with technician location/ETA | CD-07 (Next.js + Traccar WebSocket + Google Maps) |
| CSP-004 | Service history and device registry | Odoo JSON-2 API (GET /device, GET /service.order history) |
| CSP-005 | Invoice and payment history | Odoo JSON-2 API (GET /invoice) |
| CSP-006 | Online payment (bKash, Nagad, SSLCOMMERZ) | Next.js payment page → Payment gateway APIs → Odoo reconciliation |
| CSP-007 | Appointment scheduling/rescheduling | Odoo JSON-2 API (GET /booking/availability, POST /service.order) |
| CSP-008 | Feedback and rating submission | Odoo JSON-2 API → OCA helpdesk_mgmt_rating |
| CSP-009 | Privilege program management | Odoo JSON-2 API (GET /privilege/member) → CD-05 |
| CSP-010 | Warranty extension purchase | Odoo JSON-2 API → product/sale workflow |
| CSP-011 | AMC/RAMC subscription management | Odoo JSON-2 API (GET /contract) |
| CSP-012 | Knowledge base and FAQ | Payload CMS content + Next.js pages |
| CSP-013 | Live chat (AI + human escalation) | CD-16 (Ollama/LangChain chatbot) — Phase 6 |
| CSP-014 | Push notifications + preferences | Novu subscriber preferences + Firebase push |
| CSP-015 | Bengali and English UI | Next.js i18n with per-user locale |
| CSP-016 | Responsive PWA | Next.js PWA plugin + manifest.json |
| CSP-017 | Multi-address with map selection | CD-12 (Bangladesh addresses) + Google Maps Places API |

### 13.2 Technician Mobile Portal (TMP-001 to TMP-017)

See Section 6.3 (Custom Flutter Mobile App) for full specification.

**Technology**: Custom Flutter App (CD-01) | **Phase**: 2

### 13.3 Admin Operations Portal (AOP-001 to AOP-012)

| Attribute | Specification |
|---|---|
| **Technology** | Odoo CE backend (OWL frontend) + custom views + Metabase embeds |
| **Authentication** | Keycloak SAML via OCA `auth_keycloak` |
| **Users** | 100-150 back-office users |
| **Phase** | Phase 1-2 |

| Req # | Feature | Implementation |
|---|---|---|
| AOP-001 | Real-time operational dashboard | Custom Odoo dashboard + Grafana embed (live SLA, GPS map) |
| AOP-002 | Service order CRUD + assign/escalate | OCA `helpdesk_mgmt` + `fieldservice` |
| AOP-003 | Dispatch control center (drag-and-drop) | OCA `fieldservice_timeline` + `fieldservice_calendar` |
| AOP-004 | Live technician tracking map | Traccar WebSocket + OCA `fieldservice_google_map` |
| AOP-005 | Customer management (search, profiles) | Odoo `contacts` + `crm` |
| AOP-006 | Inventory management | Odoo `stock` + OCA `stock_operating_unit` |
| AOP-007 | Financial overview | Odoo `account` dashboard + Metabase embed |
| AOP-008 | Notification center | Odoo `discuss` notifications + n8n alerts |
| AOP-009 | System configuration (catalog, pricing, SLAs) | Odoo settings + OCA module configurations |
| AOP-010 | User/role management | Odoo `res.users` + Keycloak admin console |
| AOP-011 | Bulk operations | Odoo list view actions (mass update) |
| AOP-012 | Audit log viewer | OCA `audit_log` viewer |

### 13.4 Corporate B2B Portal (B2B-001 to B2B-010)

| Attribute | Specification |
|---|---|
| **Technology** | Next.js 15 + Odoo JSON-2 API |
| **Authentication** | Keycloak OIDC |
| **Users** | 500-2,000 corporate account users |
| **Phase** | Phase 4 |

| Req # | Feature | Implementation |
|---|---|---|
| B2B-001 | Corporate dashboard | Next.js dashboard → Odoo API (contracts, services, invoices) |
| B2B-002 | Multi-location management | Odoo `contacts` (multi-address per company) |
| B2B-003 | Bulk service request (CSV/Excel upload) | Next.js upload → parse → Odoo batch API |
| B2B-004 | AMC/contract management | Odoo JSON-2 API → OCA `fieldservice_agreement` |
| B2B-005 | Consolidated invoicing | CD-13 (Consolidated B2B Invoicing) |
| B2B-006 | Service analytics per location | Metabase embedded dashboard (filtered by company) |
| B2B-007 | Authorized requester management | Odoo `contacts` + company-level access rules |
| B2B-008 | NTE limit management | CD-13 extension (approval workflow for exceeding NTE) |
| B2B-009 | SLA compliance dashboard | Metabase embedded (CWM-020) |
| B2B-010 | Dedicated account manager | Odoo `crm` (salesperson assignment) |

### 13.5 Vendor & Partner Portal (VPP-001 to VPP-008)

| Attribute | Specification |
|---|---|
| **Technology** | Odoo CE portal module + custom views |
| **Authentication** | Keycloak OIDC |
| **Users** | 100-500 vendors and brand partners |
| **Phase** | Phase 4 |

| Req # | Feature | Implementation |
|---|---|---|
| VPP-001 | Vendor self-registration/onboarding | Odoo `website` portal registration + approval workflow |
| VPP-002 | PO acknowledgment/delivery tracking | Odoo `purchase` portal views |
| VPP-003 | Invoice submission/payment tracking | Odoo `account` portal views |
| VPP-004 | Warranty claim status/doc exchange | CD-04 portal views (warranty claim pipeline) |
| VPP-005 | Parts catalog/pricing management | Odoo `product` portal views |
| VPP-006 | Performance scorecard visibility | Metabase embedded dashboard (vendor metrics) |
| VPP-007 | Compliance document upload | OCA `dms_field` on vendor records |
| VPP-008 | Communication tools | Odoo `discuss` portal messaging |

### 13.6 Analytics Dashboard (ABD-001 to ABD-010)

See Section 6.1 (Metabase) for full specification.

**Technology**: Metabase embedded dashboards (iframe/JWT) | **Phase**: 2-5

### 13.7 Portal Technology Matrix

| Portal | Technology | Backend API | Auth | Users | Language | Offline | Phase |
|---|---|---|---|---|---|---|---|
| Customer | Next.js 15 + Payload CMS 3 | Odoo JSON-2 | Keycloak OIDC | 50K-250K/mo | BN + EN | No (PWA cache) | 1-3 |
| Technician | Flutter (Android/iOS) | Odoo JSON-2 | Keycloak OAuth+PKCE | 200-400 | BN + EN | Yes (24hr) | 2 |
| Admin Ops | Odoo CE (OWL) | Native | Keycloak SAML | 100-150 | EN (primary) | No | 1-2 |
| B2B Corporate | Next.js 15 | Odoo JSON-2 | Keycloak OIDC | 500-2,000 | EN + BN | No | 4 |
| Vendor/Partner | Odoo CE Portal | Native | Keycloak OIDC | 100-500 | EN | No | 4 |
| Analytics | Metabase (embedded) | PostgreSQL (direct) | Keycloak SAML | 15-25 | EN | No | 2-5 |

---

## 14. PHASED TECHNOLOGY DEPLOYMENT

### 14.1 Phase 1: Foundation (Months 1-4)

**Geography**: Dhaka HQ + 5 pilot service centers
**Go-Live**: Month 4

| Category | Technologies Deployed |
|---|---|
| **Infrastructure** | Docker/K3s cluster, PostgreSQL 16 (primary + replica), Nginx, Redis, PgBouncer |
| **ERP Core** | Odoo 19 CE: `crm`, `sale`, `stock`, `contacts`, `discuss`, `calendar`, `project`, `website` |
| **OCA Modules** | `fieldservice` (core + repair + equipment + stock + skill + portal + timeline + calendar + activity + stage_validation + quality_control + template + change_management + crm + sale + project), `helpdesk_mgmt` (core + sla + fieldservice + rating + timesheet + priority), `operating_unit` (core + stock + sale + crm), `dms` (core + field), `report_xlsx`, `report_qweb_pdf`, `stock_barcodes`, `audit_log`, `auth_keycloak`, `l10n_bd` |
| **Open Source Tools** | Keycloak (SSO), n8n (basic notification workflows), Novu (SMS + email delivery) |
| **Custom Modules** | CD-05 (Privilege Program), CD-10 (Rework Detection), CD-11 (Diagnostic Checklist Builder), CD-12 (Bangladesh Address Fields), CD-17 (Walk-in Queue Management) |
| **Integrations** | Next.js 15 ↔ Odoo JSON-2 API, SMS Gateway, Email (SMTP), Cloudinary, Barcode scanning |

### 14.2 Phase 2: Field Operations (Months 4-7)

**Geography**: All Dhaka service centers
**Go-Live**: Month 7

| Category | Technologies Deployed |
|---|---|
| **OCA Modules** | `fieldservice_route`, `fieldservice_geoengine`, `fieldservice_distribution`, `fieldservice_vehicle`, `fieldservice_fleet`, `fieldservice_google_map`, `fieldservice_google_marker_icon_picker`, `fieldservice_size` |
| **Open Source Tools** | Traccar (GPS server), VROOM + OSRM (route optimization), Metabase (initial dashboards), Grafana (operations monitoring) |
| **Custom Modules** | CD-01 (Flutter Mobile App), CD-06 (AI Dispatch Engine), CD-07 (Customer Tracking Page) |
| **Integrations** | Flutter App ↔ Odoo JSON-2 API, Traccar Client → Server → Odoo, VROOM/OSRM ↔ Odoo, Google Maps API, Firebase push |

### 14.3 Phase 3: Financial Control (Months 7-10)

**Geography**: All Dhaka + Chittagong
**Go-Live**: Month 10

| Category | Technologies Deployed |
|---|---|
| **ERP Core** | Odoo `account`, `purchase` (full activation) |
| **OCA Modules** | `account_operating_unit`, `purchase_operating_unit`, `fieldservice_account`, `fieldservice_purchase`, `account_asset_management`, `mis_builder`, `mis_builder_budget` |
| **Third-Party Modules** | SSLCOMMERZ payment module, bKash module, Nagad (via SSLCOMMERZ) |
| **Custom Modules** | CD-02 (Mushak 6.3 Invoice), CD-08 (bKash/Nagad Direct Integration), CD-09 (Bangladesh TDS Module), CD-19 (NID Validation) |
| **Integrations** | bKash API, Nagad API, SSLCOMMERZ API, Bank reconciliation |

### 14.4 Phase 4: Contracts & Partners (Months 10-13)

**Geography**: All active service centers
**Go-Live**: Month 13

| Category | Technologies Deployed |
|---|---|
| **OCA Modules** | `fieldservice_agreement`, `fieldservice_recurring`, `fieldservice_maintenance`, `fieldservice_partner_multi_relation` |
| **Custom Modules** | CD-04 (Warranty Claim Automation), CD-13 (Consolidated B2B Invoicing), CD-18 (Warranty Revenue Tracker) |
| **Portals** | B2B Corporate Portal (Next.js), Vendor & Partner Portal (Odoo CE portal) |
| **Integrations** | Brand partner warranty submission (n8n workflows for 17+ partners) |

### 14.5 Phase 5: Workforce & Intelligence (Months 13-16)

**Geography**: All 51+ service centers
**Go-Live**: Month 16

| Category | Technologies Deployed |
|---|---|
| **ERP Core** | Odoo `hr`, `hr_attendance`, `hr_holidays` (full activation) |
| **OCA Modules** | `hr_employee_skill`, `hr_attendance_geolocation`, `hr_contract_type`, `hr_holidays_public`, `hr_payroll_community`, `hr_expense`, `hr_operating_unit`, `mgmtsystem` (full suite: quality + audit + nonconformity + action + review), `bi_view_editor`, `bi_sql_editor`, `dms_auto_classification` |
| **Open Source Tools** | Mayan EDMS (full document management) |
| **Custom Modules** | CD-03 (Bangladesh Payroll), CD-14 (Performance Incentive Calculator), CD-15 (Shift & Roster Management), CD-20 (Overtime Approval Module) |
| **Integrations** | Biometric device integration (INT-028), BEFTN file generation |

### 14.6 Phase 6: Optimization (Months 16-18)

**Geography**: Complete system
**Go-Live**: Month 18 (Full system)

| Category | Technologies Deployed |
|---|---|
| **Open Source Tools** | Ollama (local LLM server) |
| **Custom Modules** | CD-16 (Bengali NLP Chatbot) |
| **Activities** | AI dispatch optimization refinement, advanced Metabase analytics, load testing (150% peak), security audit, penetration testing, documentation completion, full system acceptance testing, knowledge transfer, post-go-live stabilization |

### 14.7 Technology Deployment Timeline

```
Month:  1    2    3    4    5    6    7    8    9   10   11   12   13   14   15   16   17   18
        ├────┼────┼────┤────┼────┼────┤────┼────┼────┤────┼────┼────┤────┼────┼────┤────┼────┤
PHASE:  │◄── Phase 1 ──►│◄── Phase 2 ──►│◄── Phase 3 ──►│◄── Phase 4 ──►│◄── Phase 5 ──►│◄─P6─►│

INFRA:  [Docker/K3s/PG/Redis/Nginx──────────────────────────────────────────────────────────────►]
ODOO:   [Core CE Modules────────────────][Account/Purchase─────────────────][HR/Attendance────────►]
OCA-FS: [field-service core──────────────][route/geo/distribution──────────][agreement/recurring──►]
OCA-HD: [helpdesk core──────────────────────────────────────────────────────────────────────────►]
OCA-OU: [operating-unit (all)───────────────────────────────────────────────────────────────────►]
OCA-QMS:[                                                                  [mgmtsystem (full)───►]
OCA-BI: [report_xlsx/pdf────────────────────────────][mis_builder──────────][bi_view/sql_editor──►]
OCA-DMS:[dms (basic)────────────────────────────────────────────────────────][dms_auto_classify──►]

KEYCL:  [Keycloak SSO──────────────────────────────────────────────────────────────────────────►]
N8N:    [n8n (basic)─────────────][n8n (expanded)──────────────────────────────────────────────►]
NOVU:   [Novu (SMS+email)───────][Novu (+ push + WhatsApp)─────────────────────────────────────►]
TRACCAR:[                        [Traccar GPS──────────────────────────────────────────────────►]
VROOM:  [                        [VROOM+OSRM───────────────────────────────────────────────────►]
METAB:  [                        [Metabase (init dashboards)───────][Metabase (full suite)─────►]
GRAFANA:[                        [Grafana────────────────────────────────────────────────────────►]
MAYAN:  [                                                                  [Mayan EDMS──────────►]
OLLAMA: [                                                                                  [LLM─►]

FLUTTER:[                        [Flutter App Dev──────][App Live──────────────────────────────►]
PAY-GW: [                                       [SSLCOMMERZ/bKash/Nagad──────────────────────────►]

CD-05:  [Privilege──►]
CD-10:  [Rework──►]
CD-11:  [Checklist──►]
CD-12:  [BD Address►]
CD-17:  [Queue Mgmt►]
CD-01:  [                        [Flutter App────────►]
CD-06:  [                        [AI Dispatch────────►]
CD-07:  [                        [Customer Track─►]
CD-02:  [                                       [Mushak 6.3──────►]
CD-08:  [                                       [bKash/Nagad──────►]
CD-09:  [                                       [TDS──────►]
CD-19:  [                                       [NID──►]
CD-04:  [                                                    [Warranty Claim──────►]
CD-13:  [                                                    [B2B Invoice──────►]
CD-18:  [                                                    [Warranty Rev──────►]
CD-03:  [                                                                  [BD Payroll────────►]
CD-14:  [                                                                  [Incentive Calc────►]
CD-15:  [                                                                  [Shift/Roster──────►]
CD-20:  [                                                                  [Overtime──────►]
CD-16:  [                                                                                  [Chat►]

GO-LIVE:            ★ Ph1                ★ Ph2                ★ Ph3                ★ Ph4    ★ Ph5  ★ Full
```

---

## 15. COMPLIANCE TRACEABILITY MATRIX

### 15.1 RFP Technical Requirements (TECH-001 to TECH-038)

| Req # | Requirement | Priority | Technology | Status |
|---|---|---|---|---|
| TECH-001 | Cloud-native SaaS architecture | P1 | DigitalOcean Singapore, Docker/K3s | Compliant |
| TECH-002 | Multi-tenant with data isolation | P1 | Odoo single-tenant per org + OCA operating-unit | Compliant |
| TECH-003 | Modular architecture | P2 | Odoo module system + Docker containers | Compliant |
| TECH-004 | Horizontal scalability (500 → 5,000+ users) | P1 | 2+ app servers, K3s, PgBouncer, read replica | Compliant |
| TECH-005 | Auto-scaling for peak demand | P2 | K3s HPA + Nginx load balancing | Compliant |
| TECH-006 | 99.9% uptime SLA | P1 | Multi-server, health checks, auto-restart | Compliant |
| TECH-007 | DR: RPO < 1hr, RTO < 4hr | P1 | WAL streaming replication, automated backups, DR drills | Compliant |
| TECH-008 | South/Southeast Asia data center | P1 | DigitalOcean Singapore | Compliant |
| TECH-009 | Load balancing | P2 | Nginx upstream load balancing | Compliant |
| TECH-010 | Container-based deployment | P3 | Docker Compose / K3s | Compliant |
| TECH-011 | Page load < 3 seconds | P1 | Nginx cache, CDN, PgBouncer, Redis | Compliant |
| TECH-012 | API response < 500ms (p95) | P1 | Odoo JSON-2 optimized, PgBouncer, read replica | Compliant |
| TECH-013 | Report generation < 30 seconds | P1 | Metabase on read replica with materialized views | Compliant |
| TECH-014 | 500+ concurrent internal users | P1 | 20-24 Odoo workers, PgBouncer | Compliant |
| TECH-015 | 50,000+ concurrent portal users | P1 | CDN, Nginx caching, dedicated portal workers | Compliant |
| TECH-016 | Batch processing 10,000+ records | P2 | Dedicated cron workers, PostgreSQL COPY | Compliant |
| TECH-017 | Real-time sync < 5 seconds | P1 | Webhooks + n8n + Redis pub/sub | Compliant |
| TECH-018 | Responsive web design | P1 | Odoo OWL responsive + Next.js responsive | Compliant |
| TECH-019 | Native/PWA mobile for technician | P1 | Custom Flutter App (CD-01) — native Android/iOS | Compliant |
| TECH-020 | Offline mode with auto-sync | P1 | Flutter SQLite/Hive + background sync | Compliant |
| TECH-021 | Camera, GPS, barcode on mobile | P1 | Flutter native device APIs | Compliant |
| TECH-022 | Push notification support | P1 | Firebase via Novu | Compliant |
| TECH-023 | Low bandwidth optimization | P1 | Image compression, lazy loading, pagination, gzip | Compliant |
| TECH-024 | WCAG 2.1 AA accessibility | P2 | ARIA labels, contrast ratios, keyboard nav, touch targets | Compliant |
| TECH-025 | Full Bengali language support | P1 | Odoo .po + Flutter arb + Next.js i18n | Compliant |
| TECH-026 | English secondary language | P1 | All platforms support EN locale | Compliant |
| TECH-027 | User-level language switching | P1 | Keycloak user profile → per-app locale | Compliant |
| TECH-028 | Bengali Unicode support | P1 | PostgreSQL UTF-8, all text fields Unicode | Compliant |
| TECH-029 | DD/MM/YYYY date format | P1 | Odoo res.lang, Flutter/Next.js locale config | Compliant |
| TECH-030 | BDT primary currency | P1 | Odoo res.currency (BDT ৳, lakh format) | Compliant |
| TECH-031 | Bangladesh phone validation (+880) | P1 | CD-12 (Bangladesh Address Fields) | Compliant |
| TECH-032 | No-code/low-code config | P1 | Odoo Studio-like config + OCA modules | Compliant |
| TECH-033 | Customizable dashboards | P1 | Metabase drag-and-drop + Odoo dashboard | Compliant |
| TECH-034 | Custom fields without coding | P1 | Odoo custom field creation via UI | Compliant |
| TECH-035 | Workflow automation engine | P1 | n8n visual workflow builder | Compliant |
| TECH-036 | API-first architecture | P1 | Odoo JSON-2 API (new in v19) | Compliant |
| TECH-037 | Plugin/extension framework | P2 | Odoo module system (Python + OWL) | Compliant |
| TECH-038 | White-labeling capability | P2 | Odoo branding module + CSS theming | Compliant |

### 15.2 RFP Integration Requirements (INT-001 to INT-031)

| Req # | Requirement | Priority | Technology | Status |
|---|---|---|---|---|
| INT-001 | REST API with Next.js 15 | P1 | Odoo JSON-2 API | Compliant |
| INT-002 | Shared customer/device data sync | P1 | Bidirectional API + webhooks | Compliant |
| INT-003 | Service order from web → ERP | P1 | POST /json/2/service.order | Compliant |
| INT-004 | Real-time booking availability | P1 | GET /json/2/booking/availability | Compliant |
| INT-005 | Webhook support | P1 | Odoo webhook events → n8n | Compliant |
| INT-006 | Shared SSO | P2 | Keycloak (OIDC for Next.js, SAML for Odoo) | Compliant |
| INT-007 | bKash integration | P1 | CD-08 + bKash module | Compliant |
| INT-008 | Nagad integration | P1 | SSLCOMMERZ aggregation | Compliant |
| INT-009 | SSLCOMMERZ integration | P1 | SSLCOMMERZ Odoo module | Compliant |
| INT-010 | Rocket integration | P2 | SSLCOMMERZ aggregation | Compliant |
| INT-011 | Payment reconciliation | P1 | Odoo `account` auto-reconciliation | Compliant |
| INT-012 | Refund via payment gateways | P1 | Odoo credit note + gateway refund API | Compliant |
| INT-013 | SMS gateway (Bangladesh) | P1 | Novu → MuthoSMS/GreenWeb | Compliant |
| INT-014 | Email integration | P1 | Novu → SMTP (Odoo built-in mail) | Compliant |
| INT-015 | WhatsApp Business API | P1 | Novu → WhatsApp Cloud API | Compliant |
| INT-016 | Push notification (Firebase) | P1 | Novu → Firebase Cloud Messaging | Compliant |
| INT-017 | VoIP/telephony | P3 | Deferred — Phase 6+ enhancement | Planned |
| INT-018 | Google Maps (geocoding, tracking) | P1 | Google Maps API + Traccar + OCA fieldservice_google_map | Compliant |
| INT-019 | Route optimization | P1 | VROOM + OSRM (replaces Timefold — see §15.5) | Compliant |
| INT-020 | Real-time traffic data | P2 | Google Routes API (Dhaka metro supplement) | Compliant |
| INT-021 | Geo-fencing | P2 | Traccar geo-fencing + OCA fieldservice_geoengine | Compliant |
| INT-022 | AI chatbot (Bengali NLP) | P2 | Ollama + LLM (replaces Rasa — see §15.5) | Compliant |
| INT-023 | AI dispatch optimization | P2 | CD-06 (VROOM + skill matching) | Compliant |
| INT-024 | ML demand forecasting | P3 | Metabase trend analysis + custom SQL | Planned |
| INT-025 | Predictive maintenance | P3 | Deferred — Phase 6+ enhancement | Planned |
| INT-026 | Accounting software integration | P2 | N/A — Odoo `account` replaces standalone | Superseded |
| INT-027 | HR/Payroll integration | P2 | N/A — Odoo `hr` + CD-03 replaces standalone | Superseded |
| INT-028 | Biometric device integration | P2 | File/SDK import to Odoo `hr_attendance` | Compliant |
| INT-029 | Barcode/QR printer integration | P2 | ZPL/ESC-POS printing from Odoo | Compliant |
| INT-030 | Cloud storage (Cloudinary) | P1 | Cloudinary REST API for image storage | Compliant |
| INT-031 | Metabase BI integration | P2 | Metabase direct PostgreSQL read replica | Compliant |

### 15.3 Data Migration Requirements (MIG-001 to MIG-009)

| Req # | Requirement | Priority | Technology / Approach | Status |
|---|---|---|---|---|
| MIG-001 | Detailed migration plan with mapping | P1 | Source → Odoo data model mapping document | Planned |
| MIG-002 | Data cleansing and deduplication | P1 | Python ETL scripts + Odoo duplicate detection | Planned |
| MIG-003 | Validation rules and reconciliation reports | P1 | Custom validation scripts + Metabase reconciliation dashboards | Planned |
| MIG-004 | Trial migration with UAT | P1 | Staging environment trial load → UAT sign-off | Planned |
| MIG-005 | Rollback plan | P1 | Pre-migration snapshot + documented rollback procedures | Planned |
| MIG-006 | Migration tools provided | P1 | Python/Odoo XML-RPC bulk import + CSV import | Planned |
| MIG-007 | Incremental/delta migration | P2 | Change data capture during parallel run period | Planned |
| MIG-008 | Historical data with audit trail | P1 | Full import with created_date/modified_date preservation | Planned |
| MIG-009 | Bangla text format conversion | P2 | Python Unicode normalization scripts | Planned |

### 15.4 Training Requirements (TRN-001 to TRN-009)

| Req # | Requirement | Priority | Approach | Status |
|---|---|---|---|---|
| TRN-001 | Role-based training programs | P1 | 6 training tracks (agent, tech, manager, finance, HR, corporate) | Planned |
| TRN-002 | Train-the-Trainer program | P1 | 51 super-users (1 per branch), 8hr advanced training | Planned |
| TRN-003 | Bengali language training | P1 | All field staff training in Bengali | Planned |
| TRN-004 | Hands-on sandbox training | P1 | Dedicated training environment (copy of production) | Planned |
| TRN-005 | Video-based training library | P1 | 10-15 min Bengali-narrated videos per module | Planned |
| TRN-006 | User manuals + quick reference guides | P1 | Bengali + English PDF + laminated quick reference cards | Planned |
| TRN-007 | In-app guided tours | P2 | Odoo OWL tour framework + Flutter onboarding wizard | Planned |
| TRN-008 | Training effectiveness assessment | P2 | Pre/post-training evaluation forms | Planned |
| TRN-009 | Quarterly refresher training (Year 1) | P2 | Scheduled quarterly sessions post-go-live | Planned |

### 15.5 Strategy Divergences from RFP

| RFP Specification | Strategy Choice | Justification |
|---|---|---|
| **Timefold** (INT-019) for route optimization | **VROOM + OSRM** | Zero license cost; VROOM solves VRP in milliseconds; OSRM uses Bangladesh OpenStreetMap data; simpler deployment than Java-based Timefold. Google Routes API supplements for Dhaka metro traffic data. |
| **Rasa 3.6** (INT-022) for Bengali NLP chatbot | **Ollama + Qwen3-8B/TigerLLM + LangChain** | Rasa OSS entered maintenance mode (long-term risk); LLM approach provides superior Bengali understanding; tool-use capability for Odoo API interaction; self-hosted via Ollama ($0 API cost). |
| **Implied proprietary ERP** (RFP §15 budget range) | **Odoo 19 CE** ($0 license) | Zero license cost frees budget for implementation quality; LGPL v3 ensures full source access; 94+ OCA modules cover Enterprise-only gaps; saves $124K-$209K vs Odoo Enterprise over 3 years. |
| **SendGrid/AWS SES** (BRD §14.2) for email | **Novu** (unified notification) + SMTP | Novu provides unified multi-channel management (SMS + email + WhatsApp + push) with template management, preference center, and delivery tracking. SMTP used as transport. |
| **Cloudinary only** (INT-030) for documents | **Cloudinary** (media) + **Mayan EDMS** (documents) | Cloudinary handles image thumbnails and media optimization; Mayan EDMS adds enterprise document management with OCR (Bengali Tesseract), workflow, version control, and retention policies. |

---

## 16. COST BREAKDOWN

### 16.1 Software Licensing — 3-Year Cost: $0

| Component | License | 3-Year Cost |
|---|---|---|
| Odoo 19 CE | LGPL-3 | $0 |
| OCA Modules (94+) | LGPL-3 / AGPL-3 | $0 |
| Metabase | AGPL-3 | $0 |
| Grafana | AGPL-3 | $0 |
| Traccar | Apache-2.0 | $0 |
| n8n | Sustainable Use | $0 (self-hosted) |
| VROOM + OSRM | BSD-2 | $0 |
| Keycloak | Apache-2.0 | $0 |
| Mayan EDMS | Apache-2.0 | $0 |
| Novu | MIT | $0 |
| Flutter SDK | BSD-3 | $0 |
| Ollama + LangChain | MIT / Apache-2.0 | $0 |
| PostgreSQL + Redis + Nginx + Docker | Various open-source | $0 |
| **TOTAL SOFTWARE LICENSE** | | **$0** |

### 16.2 Third-Party API Costs (Ongoing)

| API Service | Monthly Cost | Annual Cost | 3-Year Cost |
|---|---|---|---|
| Google Maps Platform (geocoding, routes, embed) | $200 – $400 | $2,400 – $4,800 | $7,200 – $14,400 |
| WhatsApp Business API (message fees) | $100 – $300 | $1,200 – $3,600 | $3,600 – $10,800 |
| Bangladesh SMS Gateway (MuthoSMS/GreenWeb) | $100 – $200 | $1,200 – $2,400 | $3,600 – $7,200 |
| Firebase Cloud Messaging | $0 – $50 | $0 – $600 | $0 – $1,800 |
| Cloudinary (image storage/transformation) | $50 – $100 | $600 – $1,200 | $1,800 – $3,600 |
| **TOTAL API COSTS** | **$450 – $1,050** | **$5,400 – $12,600** | **$16,200 – $37,800** |

### 16.3 Infrastructure / Hosting (Ongoing)

| Component | Monthly Cost | Annual Cost | 3-Year Cost |
|---|---|---|---|
| Odoo App Servers (2× 8vCPU/16-32GB) | $200 – $320 | $2,400 – $3,840 | $7,200 – $11,520 |
| PostgreSQL Managed DB (primary + replica) | $150 – $250 | $1,800 – $3,000 | $5,400 – $9,000 |
| Supporting Services Server (8vCPU/16GB) | $80 – $160 | $960 – $1,920 | $2,880 – $5,760 |
| Backup Storage (500GB) | $25 – $50 | $300 – $600 | $900 – $1,800 |
| CDN (Cloudflare) | $0 – $20 | $0 – $240 | $0 – $720 |
| Domain + SSL | $10 – $20 | $120 – $240 | $360 – $720 |
| **TOTAL INFRASTRUCTURE** | **$465 – $820** | **$5,580 – $9,840** | **$16,740 – $29,520** |

### 16.4 Implementation & Custom Development (Year 1)

| Category | Cost |
|---|---|
| Project Management (12 months) | $12,000 – $24,000 |
| Business Analysis & Design (3 months) | $6,000 – $12,000 |
| Odoo Configuration & Setup | $8,000 – $15,000 |
| Custom Module Development (20 modules — CD-01 to CD-20) | $40,000 – $65,000 |
| Flutter Mobile App Development (CD-01) | $16,000 – $28,000 |
| Integration Development (22+ integrations) | $10,000 – $18,000 |
| Data Migration (9 data sources) | $5,000 – $10,000 |
| Testing (SIT + UAT, 6 phases) | $4,000 – $8,000 |
| DevOps & Infrastructure Setup | $5,000 – $10,000 |
| Go-Live Support (6 phases) | $5,000 – $10,000 |
| **TOTAL IMPLEMENTATION** | **$111,000 – $200,000** |

### 16.5 Training (Year 1)

| Category | Cost |
|---|---|
| Train-the-Trainer program (51 super-users) | $3,000 – $5,000 |
| End-user training materials (Bengali + English) | $2,000 – $4,000 |
| On-site training sessions (51+ branches) | $3,000 – $6,000 |
| **TOTAL TRAINING** | **$8,000 – $15,000** |

### 16.6 Support & Maintenance (Years 2-3)

| Category | Annual Cost | 2-Year Total |
|---|---|---|
| Odoo version updates + OCA module patches | $5,000 – $10,000 | $10,000 – $20,000 |
| Custom module maintenance | $5,000 – $10,000 | $10,000 – $20,000 |
| Infrastructure management | $3,000 – $5,000 | $6,000 – $10,000 |
| Help desk / user support | $2,000 – $5,000 | $4,000 – $10,000 |
| **TOTAL SUPPORT (2-YEAR)** | **$15,000 – $30,000/yr** | **$30,000 – $60,000** |

### 16.7 3-Year TCO Summary

| Category | Year 1 | Year 2 | Year 3 | 3-Year Total |
|---|---|---|---|---|
| Software Licensing | $0 | $0 | $0 | **$0** |
| Implementation & Dev | $111,000 – $200,000 | — | — | $111,000 – $200,000 |
| Training | $8,000 – $15,000 | — | — | $8,000 – $15,000 |
| Infrastructure/Hosting | $5,580 – $9,840 | $5,580 – $9,840 | $5,580 – $9,840 | $16,740 – $29,520 |
| Third-Party APIs | $5,400 – $12,600 | $5,400 – $12,600 | $5,400 – $12,600 | $16,200 – $37,800 |
| Support & Maintenance | — (warranty) | $15,000 – $30,000 | $15,000 – $30,000 | $30,000 – $60,000 |
| **ANNUAL TOTAL** | **$129,980 – $237,440** | **$25,980 – $52,440** | **$25,980 – $52,440** | |
| **3-YEAR TCO** | | | | **$181,940 – $342,320** |

### 16.8 Comparison: Odoo CE + Open Source vs Odoo Enterprise

| Category | CE + Open Source (This Spec) | Odoo Enterprise (700 users) | Savings |
|---|---|---|---|
| Software License (3yr) | $0 | $260,820 | **$260,820** |
| Implementation | $111,000 – $200,000 | $60,000 – $120,000 | ($51,000 – $80,000) more |
| Infrastructure | $16,740 – $29,520 | $20,000 – $50,000 | Similar |
| Training | $8,000 – $15,000 | $10,000 – $20,000 | Similar |
| Support | $30,000 – $60,000 | $15,000 – $40,000 | ($15,000 – $20,000) more |
| **3-Year TCO** | **$182K – $342K** | **$366K – $491K** | **$124K – $209K savings** |

---

## 17. RISK REGISTER

### 17.1 Technical Risks

| # | Risk | Impact | Probability | Mitigation |
|---|---|---|---|---|
| TR-01 | OCA module incompatibility with Odoo v19 | High | Medium | Test all modules in staging pre-deployment; use only v19-migrated modules; fork and maintain critical modules if migration delayed |
| TR-02 | Flutter mobile app development delay | High | Medium | Hire experienced Flutter team early; use 2-week Agile sprints; interim Odoo PWA as fallback for Phase 2 |
| TR-03 | Performance issues at 500+ concurrent users | High | Low | Load test at 150% expected peak before each phase go-live; horizontal scaling ready; PgBouncer + Redis pre-configured |
| TR-04 | Offline sync data conflicts | Medium | Medium | Conflict resolution strategy: last-write-wins with full audit trail; server-side merge logic for critical fields |
| TR-05 | Integration complexity (22+ systems) | High | Medium | Standardize all integrations through n8n; maintain API contract documentation; automated integration tests |
| TR-06 | PostgreSQL performance degradation | Medium | Low | Table partitioning for large tables; read replicas; materialized views; PgBouncer connection pooling; regular VACUUM/ANALYZE |
| TR-07 | Odoo v19 → v20 migration effort | Medium | Certain | Budget annual version migration effort; maintain OCA module compatibility matrix; test migration on staging 3 months before upgrade |

### 17.2 Operational Risks

| # | Risk | Impact | Probability | Mitigation |
|---|---|---|---|---|
| OR-01 | Low technician mobile app adoption | High | Medium | Bengali-only UI; gamification (leaderboard); peer champions; pilot with 20 technicians before full rollout; incentive tracking visible in app |
| OR-02 | Bangladesh internet instability | Medium | High | Offline-first architecture; 24hr offline capability; auto-sync; data compression; 3G-compatible design |
| OR-03 | Staff resistance to change | High | Medium | Executive sponsorship; involve resistors in UAT; celebrate early wins; super-user program (51 champions) |
| OR-04 | Data migration quality issues | High | Medium | Data profiling during Phase 1; trial migration; 2-week parallel run with daily reconciliation; 80% quality threshold (ASM-03) |
| OR-05 | Key team member departure | Medium | Low | Knowledge documentation; cross-train 2 people per critical role; code documentation; implementation partner backup |

### 17.3 Strategic Risks

| # | Risk | Impact | Probability | Mitigation |
|---|---|---|---|---|
| SR-01 | Budget overrun (custom scope creep) | High | Medium | Fixed-scope contracts; formal change control process; defer P3 features; weekly budget tracking |
| SR-02 | OCA repository loses community support | Medium | Low | Choose only actively maintained modules (commits in last 6 months); maintain internal forks; contribute back to OCA |
| SR-03 | Odoo SA changes CE licensing | Low | Very Low | LGPL v3 is irrevocable by design; worst case: fork current v19 codebase and maintain independently |
| SR-04 | Competitor launches superior platform | Medium | Low | Focus on execution speed; Phase 1 live in 4 months; early value delivery; modular architecture allows future platform changes |

---

## 18. APPENDICES

### Appendix A: Open-Source Tool Reference Table

| Tool | Website | GitHub Repository | License | Version |
|---|---|---|---|---|
| Odoo CE | odoo.com | github.com/odoo/odoo | LGPL-3 | 19.0 |
| Metabase | metabase.com | github.com/metabase/metabase | AGPL-3 | 0.52+ |
| Grafana | grafana.com | github.com/grafana/grafana | AGPL-3 | 11.x |
| Traccar | traccar.org | github.com/traccar/traccar | Apache-2.0 | 6.x |
| n8n | n8n.io | github.com/n8n-io/n8n | Sustainable Use | 1.x |
| VROOM | vroom-project.org | github.com/VROOM-Project/vroom | BSD-2 | 1.14+ |
| OSRM | project-osrm.org | github.com/Project-OSRM/osrm-backend | BSD-2 | 5.x |
| Keycloak | keycloak.org | github.com/keycloak/keycloak | Apache-2.0 | 26.x |
| Mayan EDMS | mayan-edms.com | github.com/mayan-edms/Mayan-EDMS | Apache-2.0 | 4.10 |
| Novu | novu.co | github.com/novuhq/novu | MIT | 2.x |
| Flutter | flutter.dev | github.com/flutter/flutter | BSD-3 | 3.x |
| Ollama | ollama.com | github.com/ollama/ollama | MIT | 0.5+ |
| LangChain | langchain.com | github.com/langchain-ai/langchain | Apache-2.0 | 0.3+ |
| PostgreSQL | postgresql.org | github.com/postgres/postgres | PostgreSQL | 16 |
| Redis | redis.io | github.com/redis/redis | BSD-3 | 7 |
| Nginx | nginx.org | github.com/nginx/nginx | BSD-2 | 1.27+ |
| Docker | docker.com | github.com/moby/moby | Apache-2.0 | 27+ |

### Appendix B: OCA Repository Links

| Repository | URL | Module Count | Primary Function |
|---|---|---|---|
| OCA/field-service | github.com/OCA/field-service | 33 | Field service management |
| OCA/helpdesk | github.com/OCA/helpdesk | 28 | Service desk and ticket management |
| OCA/management-system | github.com/OCA/management-system | 33 | ISO 9001 quality management |
| OCA/hr | github.com/OCA/hr | 50+ | Human resource management |
| OCA/payroll | github.com/OCA/payroll | 15+ | Payroll processing |
| OCA/operating-unit | github.com/OCA/operating-unit | 15+ | Multi-branch management |
| OCA/reporting-engine | github.com/OCA/reporting-engine | 20+ | Report generation (XLSX, PDF) |
| OCA/mis-builder | github.com/OCA/mis-builder | 5+ | KPI and financial reporting |
| OCA/dms | github.com/OCA/dms | 5+ | Document management |
| OCA/account-financial-tools | github.com/OCA/account-financial-tools | 40+ | Financial tools and asset management |
| OCA/stock-logistics-barcode | github.com/OCA/stock-logistics-barcode | 10+ | Barcode support for inventory |

### Appendix C: Bangladesh Implementation Partners

| Partner | Odoo Tier | Location | Key Strengths |
|---|---|---|---|
| **Metamorphosis Ltd.** | Silver Partner | Dhaka, Bangladesh | Local presence; BD-specific modules (bKash, SSLCOMMERZ); VAT/payroll experience |
| **Xsellence Bangladesh** | — | Dhaka, Bangladesh | ERP implementation; local HR/payroll expertise |
| **Ergo Ventures** | — | Dhaka, Bangladesh | Odoo implementation; manufacturing and services |
| **VS ONE IT Services** | — | Dhaka, Bangladesh | Odoo consulting; custom development |
| **Open Source Integrators** | Gold Partner | International (with BD projects) | OCA contributors; field-service expertise |

### Appendix D: Glossary of Acronyms

| Acronym | Full Form |
|---|---|
| AMC | Annual Maintenance Contract |
| API | Application Programming Interface |
| AR | Accounts Receivable |
| AP | Accounts Payable |
| BEFTN | Bangladesh Electronic Fund Transfer Network |
| BDT | Bangladeshi Taka |
| BIN | Business Identification Number |
| BRD | Business Requirements Document |
| BST | Bangladesh Standard Time (UTC+6) |
| BTRC | Bangladesh Telecommunication Regulatory Commission |
| CAPA | Corrective and Preventive Action |
| CE | Community Edition |
| CMS | Content Management System |
| CNCF | Cloud Native Computing Foundation |
| CSAT | Customer Satisfaction Score |
| CSV | Comma-Separated Values |
| DR | Disaster Recovery |
| DDoS | Distributed Denial of Service |
| EDMS | Electronic Document Management System |
| ERP | Enterprise Resource Planning |
| ETA | Estimated Time of Arrival |
| FIFO | First In, First Out |
| FTFR | First-Time Fix Rate |
| GL | General Ledger |
| GPS | Global Positioning System |
| GRN | Goods Receipt Note |
| HSTS | HTTP Strict Transport Security |
| IAM | Identity and Access Management |
| ISO | International Organization for Standardization |
| JWT | JSON Web Token |
| KPI | Key Performance Indicator |
| LGPL | GNU Lesser General Public License |
| LLM | Large Language Model |
| MFA | Multi-Factor Authentication |
| MIS | Management Information System |
| NBR | National Board of Revenue (Bangladesh) |
| NCR | Non-Conformance Report |
| NID | National Identity Document (Bangladesh) |
| NLP | Natural Language Processing |
| NTE | Not-to-Exceed |
| OCA | Odoo Community Association |
| OIDC | OpenID Connect |
| ORM | Object-Relational Mapping |
| OSRM | Open Source Routing Machine |
| OWL | Odoo Web Library |
| P&L | Profit and Loss |
| PF | Provident Fund |
| PgBouncer | PostgreSQL Connection Pooler |
| PII | Personally Identifiable Information |
| PO | Purchase Order |
| PWA | Progressive Web Application |
| RAMC | Residential Annual Maintenance Contract |
| RBAC | Role-Based Access Control |
| REST | Representational State Transfer |
| RFP | Request for Proposal |
| RFQ | Request for Quotation |
| RPO | Recovery Point Objective |
| RTO | Recovery Time Objective |
| RTV | Return to Vendor |
| SAML | Security Assertion Markup Language |
| SLA | Service Level Agreement |
| SOC | System and Organization Controls |
| SOP | Standard Operating Procedure |
| SRM | Service and Repair Management |
| SSO | Single Sign-On |
| TCO | Total Cost of Ownership |
| TDS | Tax Deducted at Source |
| TIN | Tax Identification Number |
| TLS | Transport Layer Security |
| TOTP | Time-based One-Time Password |
| UAT | User Acceptance Testing |
| UoM | Unit of Measure |
| URD | User Requirements Document |
| VPC | Virtual Private Cloud |
| VPN | Virtual Private Network |
| VRP | Vehicle Routing Problem |
| WAF | Web Application Firewall |
| WAL | Write-Ahead Logging |
| WCAG | Web Content Accessibility Guidelines |

### Appendix E: Requirement ID Cross-Reference Index

This index maps the first and last requirement ID of each category to the primary section(s) of this document where they are addressed.

| Requirement Range | Count | Primary Section(s) |
|---|---|---|
| SRM-001 to SRM-037 | 37 | §8.1, §3.2, §4.2, §7.2 |
| FSM-001 to FSM-031 | 31 | §8.2, §4.2, §6.3, §6.4, §6.7, §7.2 |
| INV-001 to INV-024 | 24 | §8.3, §3.2, §4.9 |
| CRM-001 to CRM-018 | 18 | §8.4, §3.2, §7.2 |
| FIN-001 to FIN-035 | 35 | §8.5, §3.2, §3.3, §4.6, §4.7, §7.2 |
| HRM-001 to HRM-023 | 23 | §8.6, §3.2, §4.5, §7.2 |
| CWM-001 to CWM-022 | 22 | §8.7, §4.2, §7.2 |
| SCM-001 to SCM-012 | 12 | §8.8, §3.2 |
| BI-001 to BI-014 | 14 | §8.9, §6.1 |
| DMS-001 to DMS-008 | 8 | §8.10, §4.8, §6.5 |
| QMS-001 to QMS-008 | 8 | §8.11, §4.4 |
| CSP-001 to CSP-017 | 17 | §8.12, §13.1 |
| TMP-001 to TMP-017 | 17 | §8.12, §6.3, §13.2 |
| AOP-001 to AOP-012 | 12 | §8.12, §13.3 |
| B2B-001 to B2B-010 | 10 | §8.12, §13.4 |
| VPP-001 to VPP-008 | 8 | §8.12, §13.5 |
| ABD-001 to ABD-010 | 10 | §8.12, §6.1, §13.6 |
| TECH-001 to TECH-038 | 38 | §15.1, §2, §3.4, §11, §12 |
| INT-001 to INT-031 | 31 | §15.2, §9.2, §3.5 |
| MIG-001 to MIG-009 | 9 | §15.3 |
| SEC-001 to SEC-022 | 22 | §10.1, §2.3, §6.8 |
| TRN-001 to TRN-009 | 9 | §15.4 |
| **TOTAL** | **405** | |

### Appendix F: License Compliance Summary

| License | Tools Using It | Commercial Use | Modification | Distribution | Source Disclosure | Copyleft |
|---|---|---|---|---|---|---|
| **LGPL-3** | Odoo CE, most OCA modules | Yes | Yes | Yes | Modified files only | Weak |
| **AGPL-3** | Some OCA modules, Metabase, Grafana | Yes | Yes | Yes | Network use = distribution (full source) | Strong |
| **Apache-2.0** | Keycloak, Traccar, Mayan EDMS, LangChain, Docker | Yes | Yes | Yes | NOTICE file only | No |
| **BSD-2-Clause** | VROOM, OSRM, Nginx | Yes | Yes | Yes | Copyright notice only | No |
| **BSD-3-Clause** | Flutter, Redis | Yes | Yes | Yes | Copyright notice + no endorsement | No |
| **MIT** | Novu, Ollama, Next.js | Yes | Yes | Yes | Copyright notice only | No |
| **Sustainable Use** | n8n | Yes (self-hosted) | Yes | Restricted | Per license terms | Partial |
| **PostgreSQL** | PostgreSQL | Yes | Yes | Yes | Copyright notice only | No |

**Key Compliance Notes**:
1. **AGPL-3 (Metabase, Grafana)**: Network use counts as distribution. If these tools are exposed to external users (e.g., embedded dashboards), source code must be available. Mitigation: Use iframe embedding (separate application boundary); maintain source code access link.
2. **LGPL-3 (Odoo CE)**: Custom modules written for Odoo are NOT required to be open-sourced, provided they link dynamically (standard Odoo module loading). This allows proprietary custom modules (CD-01 to CD-20).
3. **Sustainable Use License (n8n)**: Free for self-hosted use. Cannot be offered as a hosted/SaaS service to third parties. Internal use by 1000FiX is fully compliant.
4. All licenses permit commercial use for 1000FiX's internal operations. No license fees are due for any component in this stack.

---

**END OF DOCUMENT**

---

| **Document Reference** | 1000FIX-ERP-TECHSTACK-2026-001 |
|---|---|
| **Version** | 1.0 |
| **Total Requirements Covered** | 405 (100% of RFP + BRD + URD) |
| **Total Technology Components** | 30+ open-source tools and frameworks |
| **Total Software License Cost** | $0 |
| **3-Year TCO** | $181,940 – $342,320 |
| **Implementation Timeline** | 18 months (6 phases) |
