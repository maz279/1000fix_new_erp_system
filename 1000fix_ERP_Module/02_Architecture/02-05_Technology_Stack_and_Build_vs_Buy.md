---
id: FIX-ERP2-019
title: Technology Stack & Build-vs-Buy Decisions
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL
---

# Technology Stack & Build-vs-Buy Decisions

---

> **Revision 2.1 — audit findings C-01, C-05, H-02, H-03, M-01.** Five corrections apply to
> this document:
>
> 1. **Module count.** Written for 30 modules; the architecture is now **67** (`02-02`).
> 2. **Effort.** The 834 person-week figure covers 30 modules only. The restated estimate is
>    **~1,302 PW**, of which 206 PW is measured (Category A) and the remainder estimated.
> 3. **Odoo release date.** This document states "Released October 2025". Odoo 19.0 was
>    released **18 September 2025** at Odoo Experience in Brussels.
> 4. **Data residency.** The single-region Singapore topology is superseded by the
>    **split-residency** architecture in `05-06` NFR-086, driven by the Bangladesh Personal
>    Data Protection Act 2026. Sensitive personal data must be Bangladesh-resident.
> 5. **CD register.** Two conflicting custom-development registers exist — the CD-001…020
>    allocation below, and the CD IDs used in the Category A module files. A **unified CD
>    register covering all 67 modules is required** and is not yet written. All CD IDs in
>    module files are marked *provisional* until it exists.
>
> The layer model (L1–L6), the selection hierarchy, the licence analysis and the build-versus-buy
> decisions below remain valid and unchanged.

---

## 1. Stack Summary

The v1.0 five-layer stack is retained and extended with a sixth layer for the small set of
components where no viable open-source option exists.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ L6  COMMERCIAL SaaS (4 components)                          ~2% of reqs │
│     Telephony · Qualified e-signature · KYC · RMM agent (conditional)   │
├─────────────────────────────────────────────────────────────────────────┤
│ L5  CUSTOM DEVELOPMENT (138 CD items)                        ~25%       │
│     58 Odoo modules · 12 services · 6 applications · 62 extensions      │
├─────────────────────────────────────────────────────────────────────────┤
│ L4  STANDALONE OPEN SOURCE (18 systems)                      ~17%       │
│     Keycloak · Kong · n8n · Novu · Metabase · Grafana · ClickHouse      │
│     Traccar · VROOM/OSRM · Mayan EDMS · MLflow · Ollama · Redpanda …    │
├─────────────────────────────────────────────────────────────────────────┤
│ L3  FREE THIRD-PARTY ODOO MODULES                            ~4%        │
│     SSLCOMMERZ · bKash · SMS gateway · WhatsApp connector …             │
├─────────────────────────────────────────────────────────────────────────┤
│ L2  OCA COMMUNITY MODULES (140+ across 18 repositories)      ~24%       │
│     field-service · helpdesk · management-system · operating-unit …     │
├─────────────────────────────────────────────────────────────────────────┤
│ L1  ODOO 19 COMMUNITY EDITION                                ~28%       │
│     CRM · Sales · Inventory · Accounting · HR · Purchase · Project …    │
└─────────────────────────────────────────────────────────────────────────┘
```

**Software licence cost for the ERP core: $0.** L6 components carry subscription cost,
capped and approved individually.

---

## 2. Layer 1 — Odoo 19 Community Edition

| Attribute | Specification |
|---|---|
| Version | 19.0, patched to the current 19.x |
| Licence | LGPL v3 — $0 |
| Runtime | Python 3.12+ |
| Database | PostgreSQL 16 |
| Frontend | OWL 2 (TypeScript component framework) |
| Primary API | JSON-2 (RESTful, token-authenticated) |
| Source | Full access — forkable, modifiable |

### Modules Deployed

| Odoo Module | Serves | Wave |
|---|---|---|
| `base`, `web`, `mail`, `contacts` | Platform foundation, party master, chatter | W1 |
| `crm` | Lead and opportunity management | W1 |
| `sale`, `sale_management` | Quotations, orders, pricing | W3 |
| `product` | Catalogue foundation | W1 |
| `stock` | Multi-warehouse inventory, moves, valuation | W2 |
| `purchase` | Requisitions, POs, receipts | W3 |
| `account` | GL, AR, AP, tax, banking | W3 |
| `hr`, `hr_attendance`, `hr_holidays`, `hr_expense` | Employee, attendance, leave, expense | W5 |
| `project` | Task tracking for complex work | W1 |
| `calendar` | Scheduling foundation | W1 |
| `fleet` | Vehicle management | W3 |
| `website`, `portal` | Portal framework for vendor and partner surfaces | W3 |
| `maintenance` | Equipment maintenance foundation | W5 |
| `repair` | Repair order foundation (extended heavily) | W1 |
| `sale_renting` | Rental foundation (extended for M13) | W6 |
| `documents`-equivalent via OCA `dms` | Document foundation | W3 |

### Why Odoo 19 CE Remains the Right Foundation

| Factor | Assessment |
|---|---|
| Licence cost | $0 versus $45–90K over three years for Enterprise |
| Functional coverage | Covers 28% of requirements natively; OCA covers a further 24% |
| Extensibility | Inheritance model allows extension without forking core |
| Bangladesh localisation | Chart of accounts, VAT rate and currency available; the gaps are known and costed |
| Talent availability | Odoo developers available in Bangladesh at sustainable rates |
| Community | 15M+ downloads; active OCA ecosystem |
| Risk | Version upgrade cadence requires disciplined extension practice — addressed by architecture standards AS-05 |

---

## 3. Layer 2 — OCA Modules

140+ modules across 18 repositories. Only modules rated Production/Stable or Beta with
confirmed v19 migration (or active migration commits in the last six months) are deployed.

| Repository | Modules Used | Serves |
|---|---:|---|
| `OCA/field-service` | 33 | M01, M02 — the core FSM replacement for Enterprise |
| `OCA/helpdesk` | 28 | M01, M05, M27 — ticketing and SLA |
| `OCA/management-system` | 33 | M23 — ISO 9001 and 27001 |
| `OCA/operating-unit` | 15 | All — multi-branch isolation |
| `OCA/hr` + `OCA/payroll` | 50+ | M21, M22 |
| `OCA/account-financial-tools` | 40+ | M19 — assets, financial controls |
| `OCA/account-financial-reporting` | 20+ | M19, M25 |
| `OCA/reporting-engine` + `OCA/mis-builder` | 20+ | M19, M25 |
| `OCA/stock-logistics-workflow` | 25+ | M15 |
| `OCA/stock-logistics-barcode` | 10 | M15, M02 |
| `OCA/stock-logistics-warehouse` | 20+ | M15 |
| `OCA/purchase-workflow` | 25+ | M16 |
| `OCA/partner-contact` | 30+ | M07 |
| `OCA/contract` | 12 | M08 |
| `OCA/dms` | 5 | M24 |
| `OCA/server-tools` | 30+ | M29 — audit, technical utilities |
| `OCA/web` | 40+ | UI enhancements, Keycloak auth |
| `OCA/l10n-bangladesh` | 2 | M19 |

### v19 Migration Risk

| Repository | v19 Status | Risk | Mitigation |
|---|---|---|---|
| field-service | ~25 of 33 migrated | Medium | Fork and migrate the remaining 8; contribute back |
| helpdesk | ~20 of 28 migrated | Medium | Core migrated; migrate remainder as needed |
| management-system | ~28 of 33 | Low | Mature and actively maintained |
| operating-unit | ~12 of 15 | Low | Enterprise-critical, actively maintained |
| hr/payroll | ~40 of 50+ | Low | Wide adoption |
| Others | Mostly migrated | Low | Standard testing in staging |

**Standing commitment:** where 1000FiX migrates an OCA module to v19, the work is
contributed back upstream. This reduces long-term maintenance burden and is a condition of
the licence spirit.

---

## 4. Layer 4 — Standalone Open Source

| System | Version | Licence | Serves | Wave |
|---|---|---|---|:--:|
| **Keycloak** | 26.x | Apache-2.0 | M29 — identity, SSO, MFA, federation | W1 |
| **Kong Gateway** | 3.x | Apache-2.0 | M28 — API gateway | W1 |
| **n8n** | 1.x | Sustainable Use (self-hosted free) | M28 — workflow automation | W1 |
| **Novu** | 2.x | MIT | M27 — notification orchestration | W1 |
| **Redis** | 7.x | BSD-3 | Cache, sessions, queues, locks | W1 |
| **Redpanda / Kafka** | latest | BSL / Apache-2.0 | M28 — event bus at scale | W6 |
| **Traccar** | 6.x | Apache-2.0 | M02 — GPS tracking | W2 |
| **OSRM** | 5.x | BSD-2 | M02, M03 — road routing | W2 |
| **VROOM** | 1.14+ | BSD-2 | M02, M03 — vehicle routing optimisation | W2 |
| **Metabase** | 0.52+ | AGPL-3 | M25 — BI and dashboards | W4 |
| **Grafana** | 11.x | AGPL-3 | M25, M28 — operational monitoring | W2 |
| **TimescaleDB** | 2.x | Apache-2.0 / TSL | M02, M05, M17 — time series | W2 |
| **ClickHouse** | 24.x | Apache-2.0 | M25 — analytical warehouse | W8 |
| **Mayan EDMS** | 4.10 | Apache-2.0 | M24 — document management at scale | W5 |
| **MLflow** | 2.x | Apache-2.0 | M26 — model registry and tracking | W6 |
| **Ollama** | 0.5+ | MIT | M26, M27 — self-hosted LLM inference | W6 |
| **MeshCentral / RustDesk** | latest | Apache-2.0 / AGPL-3 | M05 — remote support sessions | W5 |
| **Wazuh / osquery** | latest | GPL-2 / Apache-2.0 | M05 — endpoint monitoring | W5 |
| **OpenTelemetry + Prometheus + Loki + Tempo** | latest | Apache-2.0 | Observability | W3 |
| **MinIO** | latest | AGPL-3 | Object storage | W1 |
| **Nginx** | 1.27+ | BSD-2 | Reverse proxy | W1 |
| **Docker / K3s** | current | Apache-2.0 | Containerisation and orchestration | W1 |
| **PostgreSQL** | 16 | PostgreSQL Licence | Primary datastore | W1 |
| **PgBouncer** | latest | ISC | Connection pooling | W1 |

### Licence Compliance Notes

| Licence | Obligation | How It Is Met |
|---|---|---|
| AGPL-3 (Metabase, Grafana, MinIO, RustDesk) | Source disclosure if modified and served over a network | Deployed unmodified; any modification would be published |
| LGPL-3 (Odoo, most OCA) | Modifications to the library itself must be shared | Extensions are separate modules, not modifications to core |
| Sustainable Use (n8n) | Free for internal business purposes; not for resale as a competing service | Used only for internal orchestration |
| BSL (Redpanda) | Converts to Apache-2.0 after four years; production use permitted within limits | Reviewed at deployment; Kafka is the fallback |
| TSL (TimescaleDB advanced features) | Some features require a commercial licence | Only Apache-2.0 features used |

A licence register is maintained in M30 and reviewed annually.

---

## 5. Layer 5 — Custom Development

### 5.1 Composition

| Type | Count | Effort (PW) |
|---|---:|---:|
| Odoo custom modules (`cd_*`) | 58 | 412 |
| Standalone services (Python/Node) | 12 | 148 |
| Mobile applications (Flutter) | 4 | 126 |
| Web applications (Next.js portals) | 6 | 148 |
| **Total** | **80 deliverables** | **834 PW** |

### 5.2 Custom Odoo Modules

| ID Range | Module Group | Serves |
|---|---|---|
| CD-001…008 | `cd_service_order`, `cd_diagnostic`, `cd_estimate`, `cd_qc`, `cd_sla`, `cd_rework`, `cd_workshop`, `cd_service_ext` | M01 |
| CD-009…015 | `cd_dispatch`, `cd_technician`, `cd_route`, `cd_geofence`, `cd_van_stock`, `cd_field_session`, `cd_offline_sync` | M02 |
| CD-016…020 | `cd_consignment`, `cd_custody`, `cd_courier`, `cd_rider`, `cd_logistics_charge` | M03 |
| CD-021…023 | `cd_queue`, `cd_cash_drawer`, `cd_branch_ops` | M04 |
| CD-024…029 | `cd_msp_contract`, `cd_monitoring`, `cd_alerting`, `cd_msp_ticket`, `cd_remote_session`, `cd_patch_mgmt` | M05 |
| CD-030…032 | `cd_data_case`, `cd_media_custody`, `cd_destruction_cert` | M06 |
| CD-033…036 | `cd_customer_ext`, `cd_party_role`, `cd_bd_address`, `cd_consent` | M07 |
| CD-037…040 | `cd_contract_engine`, `cd_entitlement`, `cd_pm_schedule`, `cd_contract_profit` | M08 |
| CD-041…044 | `cd_warranty_register`, `cd_warranty_product`, `cd_claim_automation`, `cd_claim_reconcile` | M09 |
| CD-045…047 | `cd_loyalty`, `cd_voucher`, `cd_campaign` | M10 |
| CD-048…051 | `cd_price_book`, `cd_quotation`, `cd_bidding`, `cd_dynamic_pricing` | M11 |
| CD-052…058 | `cd_ecommerce`, `cd_marketplace_seller`, `cd_mp_listing`, `cd_mp_job`, `cd_review`, `cd_commission`, `cd_advertising` | M12 |
| CD-059…062 | `cd_rental_asset`, `cd_rental_agreement`, `cd_condition_report`, `cd_rental_billing` | M13 |
| CD-063…066 | `cd_tradein`, `cd_refurb`, `cd_grading`, `cd_resale` | M14 |
| CD-067…071 | `cd_part_master`, `cd_stock_ext`, `cd_consignment_stock`, `cd_cycle_count`, `cd_landed_cost` | M15 |
| CD-072…074 | `cd_vendor_ext`, `cd_rfq`, `cd_import_order` | M16 |
| CD-075…079 | `cd_asset_registry`, `cd_asset_estate`, `cd_maintenance_plan`, `cd_telemetry`, `cd_asset_health` | M17 |
| CD-080…082 | `cd_ewaste`, `cd_recycling`, `cd_esg_report` | M18 |
| CD-083…089 | `cd_mushak`, `cd_vat_register`, `cd_tds`, `cd_nid`, `cd_cash_position`, `cd_fixed_asset_ext`, `cd_close_checklist` | M19 |
| CD-090…095 | `cd_billing_engine`, `cd_subscription`, `cd_usage_billing`, `cd_revenue_recognition`, `cd_settlement`, `cd_dunning` | M20 |
| CD-096…101 | `cd_payroll_bd`, `cd_incentive`, `cd_shift_roster`, `cd_overtime`, `cd_beftn`, `cd_ess` | M21 |
| CD-102…104 | `cd_competency`, `cd_certification`, `cd_lms_bridge` | M22 |
| CD-105…106 | `cd_qms_ext`, `cd_audit_mobile` | M23 |
| CD-107…109 | `cd_document_ext`, `cd_esignature`, `cd_retention` | M24 |
| CD-110…112 | `cd_metric_registry`, `cd_warehouse_sync`, `cd_embedded_analytics` | M25 |
| CD-113…118 | `cd_ml_gateway`, `cd_dispatch_ml`, `cd_forecast`, `cd_predictive`, `cd_pricing_ml`, `cd_llm_bridge` | M26 |
| CD-119…124 | `cd_conversation`, `cd_telephony`, `cd_agent_console`, `cd_assistant`, `cd_notification_ext`, `cd_inbox` | M27 |
| CD-125…129 | `cd_event_outbox`, `cd_api_layer`, `cd_webhook`, `cd_sync_engine`, `cd_integration_monitor` | M28 |
| CD-130…132 | `cd_rbac_ext`, `cd_audit_ext`, `cd_sod` | M29 |
| CD-133…138 | `cd_entity_config`, `cd_mdm`, `cd_feature_flag`, `cd_locale_pack`, `cd_country_pack`, `cd_platform_ops` | M30 |

### 5.3 Standalone Services

| Service | Technology | Purpose |
|---|---|---|
| Dispatch scoring service | Python / FastAPI | Candidate scoring, calls ML models |
| Route optimisation orchestrator | Python | Wraps VROOM/OSRM, handles re-optimisation |
| Pricing engine | Python | Rule evaluation, guard rails, decision logging |
| Settlement engine | Python | Commission calculation, payout file generation |
| ML inference gateway | Python / FastAPI | Single entry point to all models with fallback |
| Telemetry collector | Go / Python | High-throughput ingestion into TimescaleDB |
| RMM collector | Python | Agent and SNMP data normalisation |
| Document generation service | Python | High-volume PDF/A generation with Bengali rendering |
| OCR service wrapper | Python | Bengali and English document extraction |
| Notification dispatcher | Node.js | Channel routing, template resolution, delivery tracking |
| Warehouse ETL | Python / dbt | Warehouse loading and transformation |
| Reconciliation service | Python | Cross-system divergence detection |

### 5.4 Applications

| Application | Technology | Portal |
|---|---|---|
| Technician mobile app | Flutter | P02 |
| Rider/logistics app | Flutter | P09 |
| Field auditor app | Flutter | P11 |
| Customer mobile app | Flutter (shared codebase with P02 patterns) | P01 |
| Customer portal · B2B portal · Seller portal · Brand portal · Contact centre console · Partner portal | Next.js 15 + React 19 | P01, P04, P07, P08, P10, P12 |

---

## 6. Layer 6 — Commercial Components

Each requires CFO approval and an annual review of whether an open-source alternative has
matured.

| Component | Purpose | Module | Estimated Cost | Open-Source Alternative Assessed |
|---|---|---|---|---|
| Cloud telephony / CPaaS | Inbound IVR, call routing, recording on hotline 16743 | M27 | $200–600/month | Asterisk/FreePBX viable but requires carrier interconnect and in-house telecom expertise; revisit at renewal |
| Qualified e-signature | Legally binding signatures on AMC, MSP, rental and seller agreements | M24 | $100–400/month | OSS signing works technically but lacks accredited trust-service status for enforceability |
| Identity verification / KYC | Marketplace seller and high-value customer verification | M12 | $0.30–0.80 per check | Requires accredited data source; no OSS equivalent |
| Endpoint RMM agent (conditional) | Patch management at scale on client Windows/macOS estates | M05 | $2–5 per endpoint/month | Wazuh + osquery cover monitoring; patch orchestration at scale may require commercial. **Decision deferred to Wave 5 after a pilot.** |

**Total L6 exposure: $0–36K over three years**, against $455K–780K total programme cost.

---

## 7. Build-vs-Buy Decisions

| # | Capability | Decision | Rationale |
|---|---|---|---|
| 1 | ERP core | **Build on Odoo CE** | $0 licence; full extensibility; local talent; already the approved v1.0 decision |
| 2 | Field service management | **OCA + custom** | OCA field-service covers the majority; Enterprise FSM would cost $45–90K/3yr for less flexibility |
| 3 | Technician mobile app | **Build (Flutter)** | Offline-first for 24 hours, Bengali-first, deep ERP integration — no commercial product meets all three |
| 4 | Dispatch optimisation | **Build on VROOM/OSRM** | Commercial routing APIs cost $200–400/month ongoing and cannot embed 1000FiX skill/certification/van-stock constraints |
| 5 | Marketplace platform | **Build** | Commission and settlement must live in the ledger; SaaS marketplaces cannot be the system of record |
| 6 | Managed services PSA | **Build on Odoo + OSS monitoring** | Commercial PSA licensing scales badly at 400 technicians and still needs ERP integration |
| 7 | RMM agent | **Conditional buy (L6)** | OSS covers monitoring; patch orchestration at enterprise scale may justify a commercial agent — piloted in Wave 5 |
| 8 | Contact centre platform | **Build console, buy telephony** | The agent experience must be inside the ERP; the carrier interconnect must be licensed |
| 9 | Business intelligence | **Metabase (OSS)** | Mature, free, self-hosted, embeds cleanly; commercial BI adds cost without proportionate value at this scale |
| 10 | Data warehouse | **ClickHouse (OSS)** | Handles the analytical volume at a fraction of managed-warehouse cost |
| 11 | Identity provider | **Keycloak (OSS)** | Mature, standards-compliant, supports federation with corporate clients |
| 12 | API gateway | **Kong (OSS)** | Proven at scale, free tier sufficient |
| 13 | Document management | **OCA dms → Mayan EDMS** | OCA sufficient through Wave 4; Mayan for volume, OCR and retention from Wave 5 |
| 14 | E-signature | **Buy (L6) for binding contracts; build for operational signatures** | Operational signatures (job completion, delivery) need no accreditation; contracts do |
| 15 | Conversational AI | **Build on self-hosted LLM** | Customer data must not leave the Company; Bengali capability available in open-weight models; no per-query cost |
| 16 | ML platform | **Build on MLflow (OSS)** | Managed ML platforms add cost and data-egress concerns |
| 17 | Payment processing | **Integrate, never build** | Regulated; use bKash, Nagad, SSLCOMMERZ |
| 18 | Accounting engine | **Odoo `account` + custom Bangladesh compliance** | Core double-entry is solved; Bangladesh compliance is not |
| 19 | Payroll engine | **OCA base + custom Bangladesh rules** | Tax slabs, PF, gratuity and BEFTN are Bangladesh-specific |
| 20 | E-commerce storefront | **Build in Next.js** | Must share identity, catalogue, stock and settlement with the ERP |

---

## 8. Infrastructure

### 8.1 Production Sizing (Steady State, Wave 8)

| Component | Specification | Notes |
|---|---|---|
| Odoo application nodes | 4 × 8 vCPU / 32 GB | 12 workers each |
| Odoo cron nodes | 2 × 4 vCPU / 16 GB | Scheduled jobs isolated from user traffic |
| Next.js portal nodes | 3 × 4 vCPU / 8 GB | Or serverless equivalent |
| Domain services | 4 × 4 vCPU / 16 GB | Dispatch, pricing, ML gateway, settlement |
| PostgreSQL primary | 16 vCPU / 64 GB / 2 TB NVMe | Partitioned, tuned |
| PostgreSQL replicas | 2 × 8 vCPU / 32 GB / 2 TB | Read and BI offload |
| TimescaleDB | 8 vCPU / 32 GB / 4 TB | GPS and telemetry with compression |
| ClickHouse | 8 vCPU / 32 GB / 4 TB | Analytical warehouse |
| Redis | 4 vCPU / 16 GB | Cache, queues, sessions |
| Event bus | 3 × 4 vCPU / 16 GB | Redpanda cluster |
| Supporting services | 3 × 8 vCPU / 32 GB | Keycloak, Kong, n8n, Novu, Metabase, Grafana, Traccar, VROOM/OSRM, Mayan, MinIO |
| ML inference | 1 × 8 vCPU / 32 GB + GPU (optional) | LLM inference; GPU only if latency requires |
| Object storage | 20 TB growing | Documents, evidence, backups |

### 8.2 Cost Progression

| Wave | Monthly Infrastructure | Cumulative Annual |
|---|---:|---:|
| W1 | $450–700 | — |
| W2 | $800–1,200 | ~$8K (Yr 1) |
| W3 | $1,200–1,800 | |
| W4 | $1,600–2,400 | ~$19K (Yr 2) |
| W5 | $2,000–3,000 | |
| W6 | $2,600–3,800 | |
| W7 | $3,200–4,600 | ~$44K (Yr 3) |
| W8 | $3,800–5,400 | |
| W9 | $4,000–5,800 | |

### 8.3 Third-Party API Costs

| Service | Basis | Monthly at Scale |
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

---

## 9. Development Environment & Practice

Inherits the conventions already established in the repository (`AGENTS.md`) and the v1.0
implementation documents.

| Aspect | Standard |
|---|---|
| Repository | Monorepo with Odoo as a pinned submodule, OCA as subtrees, custom modules and services as first-class directories |
| Branching | `main` (production) ← `release/*` ← `develop` ← `feature/*` and `fix/*`; `hotfix/*` from `main` |
| Commit convention | `<type>(<scope>): <subject>` — feat, fix, docs, style, refactor, test, chore, perf |
| Code review | Every change reviewed by a second developer; architecture changes reviewed by the architect |
| Pre-commit | Formatting, linting, Odoo-specific checks, secret scanning |
| CI | Lint, type check, unit tests, integration tests, OpenAPI validation, security scan, build verification on every pull request |
| CD | Automatic to dev on merge to `develop`; manual gate to staging and production |
| Testing | See Doc 16 §11 |
| Documentation | Every module ships with a README, a runbook and its OpenAPI specification; documentation is a definition-of-done item |
| Environments | local · dev · staging · training · prod · dr |
| Secrets | Vault-managed; never in the repository; rotation scheduled |
| Dependency management | Pinned versions; automated vulnerability alerts; monthly update cycle |

---

## 10. Technology Decision Log

| # | Decision | Alternative Rejected | Reason |
|---|---|---|---|
| TD-01 | Odoo 19 CE as ERP core | Odoo Enterprise; ERPNext; custom build | Licence cost; OCA coverage; local talent (carried forward from v1.0) |
| TD-02 | PostgreSQL 16 shared with the portal platform | Separate databases | One technology, one operational skill set, simpler integration |
| TD-03 | Flutter for all field applications | React Native; native | Single codebase for four apps; strong offline story; the v1.0 decision |
| TD-04 | Next.js 15 for external web portals | Odoo web for everything | The portal platform already exists and cannot be replaced (CON-03) |
| TD-05 | VROOM + OSRM for routing | Google Routes; Timefold | $0 licence; self-hosted; embeds custom constraints (v1.0 divergence, formalised) |
| TD-06 | Self-hosted LLM for conversational AI | Rasa 3.6; hosted LLM API | Rasa in maintenance mode; hosted APIs send customer data offshore (v1.0 divergence, formalised) |
| TD-07 | Keycloak for identity | Odoo-native auth; Auth0 | Federation with corporate clients; $0; standards-based |
| TD-08 | Kong for API gateway | Nginx alone; cloud gateway | Portal count and external consumers justify a real gateway |
| TD-09 | ClickHouse for the warehouse | PostgreSQL analytics; managed warehouse | Analytical volume from Wave 8 exceeds what a replica can serve economically |
| TD-10 | Redpanda for the event bus at scale | Redis Streams alone | Redis sufficient to Wave 5; durability and replay needs grow beyond it |
| TD-11 | Build the marketplace rather than buy | Marketplace SaaS | Settlement must be in the ledger |
| TD-12 | Build the MSP platform on Odoo + OSS monitoring | Commercial PSA/RMM suite | Licence scaling; integration burden; conditional L6 for the agent only |
| TD-13 | TimescaleDB for time series | Plain PostgreSQL; InfluxDB | Same database engine, same operational skills, proven compression |
| TD-14 | Metabase for BI | Superset; commercial BI | Maturity, embedding, and the v1.0 decision |
| TD-15 | Monorepo | Polyrepo | Cross-cutting changes across 80 deliverables are common |

---

*Next document: `20_Risks_Assumptions_Dependencies_and_Governance.md`*
