---
id: FIX-ERP2-003
title: ERP Module Architecture & System Map
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL
---

# ERP Module Architecture & System Map
# 1000FiX ERP System v2.0

---

> **Revision 2.1 — audit findings C-01 and C-05.** This document was written against the
> 30-module, 5-pillar architecture. The architecture is now **67 modules in 11 categories**;
> the authoritative structure is `02-02_Module_Catalogue_Master_Register.md`. The layering,
> integration patterns, shared kernel and architecture standards below remain valid and apply
> unchanged to all 67 modules. **Two corrections apply:**
>
> 1. **Pillars A–E are superseded by categories A–K.** Where this document says "five
>    pillars", read "eleven categories". The category definitions are in `02-02` §2.
> 2. **The single-region deployment topology in §6 is superseded** by the split-residency
>    architecture in `05-06` NFR-086. Sensitive personal data — NID, passport, TIN, biometric
>    templates and recovered customer data — must be held in a **Bangladesh-resident** store.
>    A full redraw of §6 is pending the legal opinion in DEP-31.

---

## 1. Architectural Position

The ERP is the **system of record** for the 1000FiX digital estate. It owns every business
object that has a lifecycle, a financial consequence or an audit obligation.

```
                          ┌─────────────────────────────────────┐
                          │        EXPERIENCE LAYER             │
                          │  12 portals & applications (P01-P12)│
                          │  Next.js 15 · Flutter · Odoo Web     │
                          └──────────────────┬──────────────────┘
                                             │
                          ┌──────────────────▼──────────────────┐
                          │      EXPERIENCE API GATEWAY         │
                          │  Kong · OAuth2/OIDC · Rate limiting │
                          │  BFF per portal · GraphQL federation│
                          └──────────────────┬──────────────────┘
                                             │
   ┌─────────────────────────────────────────▼─────────────────────────────────────────┐
   │                        1000FiX ERP v2.0 — SYSTEM OF RECORD                        │
   │                                                                                   │
   │  ┌───────────┬───────────┬───────────┬───────────┬───────────┐                    │
   │  │ PILLAR A  │ PILLAR B  │ PILLAR C  │ PILLAR D  │ PILLAR E  │                    │
   │  │  Service  │ Commercial│  Supply   │  Finance  │Intelligence                    │
   │  │ Operations│ & Revenue │  & Assets │ People &  │ & Platform│                    │
   │  │           │           │           │Governance │           │                    │
   │  │ M01 SRM   │ M07 CRM   │ M15 INV   │ M19 FIN   │ M25 BID   │                    │
   │  │ M02 FSM   │ M08 CTR   │ M16 SCM   │ M20 BIL   │ M26 AIM   │                    │
   │  │ M03 LOG   │ M09 WTY   │ M17 AST   │ M21 HRM   │ M27 CCE   │                    │
   │  │ M04 FRD   │ M10 LOY   │ M18 ESG   │ M22 LMS   │ M28 IPF   │                    │
   │  │ M05 RMS   │ M11 SLS   │           │ M23 QMS   │ M29 SEC   │                    │
   │  │ M06 DTS   │ M12 ECM   │           │ M24 DMS   │ M30 ADM   │                    │
   │  │           │ M13 RNT   │           │           │           │                    │
   │  │           │ M14 TRF   │           │           │           │                    │
   │  └───────────┴───────────┴───────────┴───────────┴───────────┘                    │
   │                                                                                   │
   │  ┌─────────────────────────────────────────────────────────────────────────────┐  │
   │  │  SHARED KERNEL — party · product · location · entity · document · event     │  │
   │  └─────────────────────────────────────────────────────────────────────────────┘  │
   └───────────────────────────────────┬───────────────────────────────────────────────┘
                                       │
   ┌───────────────────────────────────▼───────────────────────────────────────────────┐
   │                     DATA & INTELLIGENCE PLATFORM                                  │
   │  PostgreSQL 16 (OLTP) · TimescaleDB (telemetry) · ClickHouse (OLAP)               │
   │  Redis · Object storage · MLflow · Metabase · Grafana                             │
   └───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Five Pillars

| Pillar | Name | Modules | Data Domain | Accountable Executive |
|---|---|---|---|---|
| **A** | Core Service Operations | M01–M06 | Work, devices in our custody, technician execution | Service Operations Director |
| **B** | Customer, Commercial & Revenue | M07–M14 | Parties, agreements, prices, orders, channels | Chief Commercial Officer |
| **C** | Supply Chain & Assets | M15–M18 | Materials, suppliers, assets, end-of-life | Supply Chain Director |
| **D** | Finance, People & Governance | M19–M24 | Money, workforce, competency, quality, records | CFO / HR Director / Quality Manager |
| **E** | Intelligence & Platform | M25–M30 | Insight, automation, connectivity, identity, tenancy | CTO |

### Pillar Boundary Rules

1. A module may **read** another pillar's data only through published APIs or the shared kernel.
2. Cross-pillar writes occur only via **domain events** or an explicit orchestrated command.
3. Each pillar owns its own scheduled jobs; no cross-pillar cron dependencies.
4. Financial postings originate in Pillar D. Other pillars raise *billable events*, never journal entries.
5. Identity and permission decisions are always delegated to M29; no module implements its own auth.

---

## 3. The Shared Kernel

Six concepts are used by nearly every module and are therefore modelled once, in a shared
kernel owned by the platform team. Changing a kernel concept requires architectural review.

| Kernel Concept | Odoo Basis | Extended By | Used By |
|---|---|---|---|
| **Party** (customer, employee, vendor, seller, partner, brand) | `res.partner` | `fix.party.role`, `fix.party.hierarchy` | All |
| **Product & Service Catalogue** | `product.template` / `product.product` | `fix.catalogue.item`, service kits, rental SKUs, refurb grades | M01, M11, M12, M13, M14, M15 |
| **Location & Geography** | `res.country`, `res.country.state`, `res.city` | `fix.bd.address` (8 divisions / 64 districts / upazilas), `fix.zone`, `fix.geofence` | M02, M03, M04, M12, M30 |
| **Legal Entity & Operating Unit** | `res.company`, OCA `operating.unit` | `fix.entity`, `fix.branch`, `fix.cost.center` | All |
| **Document & Attachment** | `ir.attachment`, OCA `dms` | `fix.document`, retention class, e-signature envelope | All |
| **Event** | — | `fix.domain.event` (outbox pattern) | All |

### Party Model

A single party may hold multiple roles simultaneously. This is essential: a marketplace
seller can also be a customer; a corporate client can also be a referral partner.

```
                        ┌──────────────┐
                        │  fix.party   │  (res.partner)
                        └──────┬───────┘
                               │ 1..N
                    ┌──────────▼──────────┐
                    │  fix.party.role     │
                    └──────────┬──────────┘
        ┌──────────┬───────────┼───────────┬──────────┬──────────┐
        ▼          ▼           ▼           ▼          ▼          ▼
   Customer    Employee     Vendor    MP Seller   Brand      Referral
   (indiv/     (staff/      (parts/   (engineer/  Partner    Partner
    corp/      technician)  courier)   shop)                 (alliance)
    dealer/
    govt)
```

---

## 4. Module Dependency Map

Arrows read "depends on". Only significant dependencies are shown.

```
                                   ┌──────────────────────────────┐
                                   │  M28 IPF · M29 SEC · M30 ADM │  PLATFORM FOUNDATION
                                   │  (every module depends on)   │
                                   └───────────────┬──────────────┘
                                                   │
        ┌──────────────────────────────────────────┼──────────────────────────────────┐
        │                                          │                                  │
┌───────▼────────┐                         ┌───────▼────────┐                ┌────────▼───────┐
│  M07 CRM       │◄────────────────────────│  M17 AST       │                │  M24 DMS       │
│  Customer 360  │                         │  Device/Asset  │                │  Documents     │
└───┬────────┬───┘                         └───────┬────────┘                └────────────────┘
    │        │                                     │
    │        └──────────────┐                      │
    ▼                       ▼                      ▼
┌────────────┐      ┌──────────────┐       ┌──────────────┐
│ M08 CTR    │      │ M10 LOY      │       │  M01 SRM     │◄──── M04 FRD (walk-in intake)
│ Contracts  │      │ Loyalty      │       │  Service     │◄──── M27 CCE (phone/chat intake)
└─────┬──────┘      └──────────────┘       │  Order       │◄──── M12 ECM (online intake)
      │                                    └──┬────┬───┬──┘
      │  entitlement                          │    │   │
      ▼                                       │    │   └──────────────┐
┌────────────┐                                │    │                  │
│ M05 RMS    │────► monitored assets          │    │                  ▼
│ Managed    │                                ▼    ▼          ┌──────────────┐
│ Services   │                     ┌──────────┐  ┌─────────┐  │  M06 DTS     │
└────────────┘                     │ M02 FSM  │  │ M15 INV │  │  Data        │
                                   │ Dispatch │─►│ Parts   │  │  Services    │
                                   └────┬─────┘  └────┬────┘  └──────────────┘
                                        │             │
                                        ▼             ▼
                                  ┌──────────┐  ┌──────────┐
                                  │ M03 LOG  │  │ M16 SCM  │
                                  │Logistics │  │Procure   │
                                  └────┬─────┘  └────┬─────┘
                                       │             │
        ┌──────────────────────────────┴─────────────┴────────────┐
        │                                                          │
        ▼                                                          ▼
┌────────────────┐   ┌────────────┐   ┌────────────┐      ┌────────────────┐
│ M14 TRF        │   │ M13 RNT    │   │ M18 ESG    │      │  M09 WTY       │
│ Trade-in/Refurb│──►│ Rental     │   │ E-Waste    │      │  Warranty      │
└───────┬────────┘   └─────┬──────┘   └─────┬──────┘      └───────┬────────┘
        │                  │                │                     │
        └──────────────────┴────────────────┴─────────────────────┤
                                                                  │
                    ┌─────────────────────────────────────────────▼─────────┐
                    │  M11 SLS (pricing) ──► M12 ECM (channel)              │
                    └───────────────────────┬───────────────────────────────┘
                                            │  billable events
                    ┌───────────────────────▼───────────────────────────────┐
                    │  M20 BIL  Billing · Revenue Recognition · Settlement   │
                    └───────────────────────┬───────────────────────────────┘
                                            │  postings
                    ┌───────────────────────▼───────────────────────────────┐
                    │  M19 FIN  Ledger · VAT/Mushak · TDS · Banking          │
                    └───────────────────────────────────────────────────────┘

     M21 HRM ──► M22 LMS ──► (competency gate) ──► M02 FSM dispatch eligibility
     M23 QMS ──► consumes events from M01, M02, M12, M16 (quality signals)
     M25 BID ──► consumes from all (read-only warehouse)
     M26 AIM ──► consumes from M25, writes recommendations to M02, M11, M15, M17
```

### Critical Path

The build order is constrained by these hard dependencies:

```
M29 SEC + M28 IPF + M30 ADM (foundation)
   → M07 CRM + M17 AST (masters)
      → M01 SRM + M04 FRD (intake & work)
         → M15 INV (parts consumption)
            → M02 FSM (dispatch) → M03 LOG (movement)
               → M11 SLS → M20 BIL → M19 FIN (money)
                  → M08 CTR + M09 WTY (agreements)
                     → M05 RMS / M06 DTS / M13 RNT / M14 TRF / M12 ECM (new lines)
                        → M26 AIM (intelligence over accumulated data)
```

---

## 5. Layered Delivery Model

Every capability is delivered at the cheapest viable layer. This is the v1.0 selection
hierarchy, extended with L6.

| Layer | Description | Licence | Share of v2.0 Requirements |
|---|---|---|---|
| **L1** | Odoo 19 CE native | LGPL-3, $0 | 28% |
| **L2** | OCA community modules (140+ across 18 repositories) | LGPL/AGPL-3, $0 | 24% |
| **L3** | Free third-party Odoo modules | Various, $0 | 4% |
| **L4** | Standalone open-source systems | Apache/MIT/BSD/AGPL, $0 | 17% |
| **L5** | Custom development (58 `CD-*` modules + services + apps) | Proprietary, dev cost | 25% |
| **L6** | Commercial SaaS where no viable OSS exists | Subscription | 2% |

### Selection Rule

```
For each requirement:
  1. Can Odoo 19 CE do it out of the box?            → L1
  2. Is there a production-grade OCA module?          → L2
  3. Is there a maintained free third-party module?   → L3
  4. Is there a mature standalone OSS system?         → L4
  5. Must it be built?                                → L5
  6. Only if 1–5 all fail AND CFO approves            → L6
```

### L6 Components Approved for v2.0

| Component | Purpose | Module | Why No OSS |
|---|---|---|---|
| Cloud telephony / CPaaS | Inbound IVR, call recording, agent routing on hotline 16743 | M27 | Carrier interconnect in Bangladesh requires a licensed provider |
| Qualified e-signature provider | Legally binding signatures on AMC/MSP contracts and rental agreements | M24 | Legal enforceability requires an accredited trust service |
| Endpoint RMM agent (optional) | Managed-endpoint monitoring on client Windows/macOS estates | M05 | OSS agents (osquery/Wazuh) cover monitoring; a commercial agent may be required for patch management at scale — decision deferred to Wave 5 |
| Identity verification (NID/KYC) | Marketplace seller verification | M12 | Requires accredited data source |

Everything else is L1–L5. **Software licence cost remains $0 for the ERP core.**

---

## 6. Runtime Topology

```
┌───────────────── PRODUCTION — Cloud Region: Singapore (primary) ─────────────────┐
│                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │  EDGE — Cloudflare CDN · WAF · DDoS · Bot management                        │ │
│  └────────────────────────────────┬────────────────────────────────────────────┘ │
│                                   │                                               │
│  ┌────────────────────────────────▼────────────────────────────────────────────┐ │
│  │  INGRESS — Kong API Gateway + Nginx                                         │ │
│  │  TLS 1.3 · OAuth2 introspection · rate limits · request signing             │ │
│  └────────────────────────────────┬────────────────────────────────────────────┘ │
│                                   │                                               │
│  ┌───────────────────┬────────────┴──────────┬─────────────────┬───────────────┐ │
│  │  ODOO 19 CE       │  NEXT.JS PLATFORM     │  DOMAIN         │  SUPPORTING   │ │
│  │  APPLICATION TIER │  (portals P01,P04,    │  SERVICES       │  SYSTEMS      │ │
│  │                   │   P07,P08,P12)        │                 │               │ │
│  │  4× app nodes     │  Vercel / K8s         │  · Dispatch AI  │ · Keycloak    │ │
│  │  12 workers each  │  React 19             │  · Pricing eng. │ · n8n         │ │
│  │  2× cron nodes    │  Payload CMS 3        │  · ML inference │ · Novu        │ │
│  │  2× longpoll      │                       │  · Route (VROOM │ · Traccar     │ │
│  │                   │                       │    + OSRM)      │ · Mayan EDMS  │ │
│  │  30 modules       │                       │  · Settlement   │ · Metabase    │ │
│  │  58 CD modules    │                       │  · RMM collector│ · Grafana     │ │
│  │  140+ OCA modules │                       │  · OCR/STT      │ · MinIO       │ │
│  └───────────────────┴───────────────────────┴─────────────────┴───────────────┘ │
│                                   │                                               │
│  ┌────────────────────────────────▼────────────────────────────────────────────┐ │
│  │  MESSAGING — Redis Streams (intra) · Kafka/Redpanda (inter-system, W6+)     │ │
│  │  Transactional outbox → event bus → consumers                              │ │
│  └────────────────────────────────┬────────────────────────────────────────────┘ │
│                                   │                                               │
│  ┌────────────────────────────────▼────────────────────────────────────────────┐ │
│  │  DATA TIER                                                                  │ │
│  │  PostgreSQL 16 primary (16 vCPU / 64GB) + 2 read replicas + PgBouncer       │ │
│  │  TimescaleDB — GPS tracks, IoT telemetry, RMM metrics                       │ │
│  │  ClickHouse — OLAP warehouse (Wave 8)                                       │ │
│  │  Redis 7 — cache, sessions, queues, locks                                   │ │
│  │  Object storage — attachments, photos, evidence packs, backups              │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │  OBSERVABILITY — OpenTelemetry → Prometheus + Loki + Tempo → Grafana        │ │
│  │  BACKUP — hourly WAL · daily full (30d) · weekly (1y) · monthly (7y) AES-256│ │
│  │  DR — warm standby, RPO ≤ 15 min, RTO ≤ 2 hours                             │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────────┘
```

### Environment Ladder

| Environment | Purpose | Data | Refresh |
|---|---|---|---|
| `local` | Developer workstation, Docker Compose | Synthetic fixtures | On demand |
| `dev` | Continuous integration target | Synthetic + anonymised sample | Every merge to `develop` |
| `staging` | UAT, performance, security testing | Full production clone, PII-masked | Weekly |
| `training` | Super-user and end-user training | Curated scenario data | Per training cycle |
| `prod` | Live | Live | — |
| `dr` | Warm standby | Streaming replica | Continuous |

---

## 7. Integration Architecture Patterns

Five patterns cover all 47 integrations. Every integration must declare which it uses.

| Pattern | When Used | Transport | Example |
|---|---|---|---|
| **Synchronous request/response** | Caller needs the answer now | REST / Odoo JSON-2 over HTTPS | Booking availability lookup, warranty status check |
| **Asynchronous command** | Work can be queued | Message to queue → worker | Bulk device import, batch invoice generation |
| **Domain event (publish/subscribe)** | Other modules react to a state change | Transactional outbox → event bus | `service_order.completed` → warranty claim, invoice, CSAT survey |
| **Webhook (inbound/outbound)** | Third-party notification | Signed HTTPS POST with replay protection | Payment confirmation, courier status update |
| **Batch file exchange** | Bulk, scheduled, or regulator-mandated | SFTP / signed file drop | BEFTN payroll file, NBR VAT return, brand claim batches |

### Event Catalogue Principles

- Events are **facts about the past**, named `<aggregate>.<past-tense-verb>`.
- Every event carries: `event_id`, `occurred_at`, `entity_id`, `branch_id`, `actor`, `correlation_id`, `schema_version`, payload.
- Events are published through a **transactional outbox** — never directly from business logic.
- Consumers must be **idempotent**; every consumer records processed `event_id`s.
- Schema evolution is additive only; breaking changes require a new `schema_version` and a dual-publish period.

---

## 8. Multi-Entity, Multi-Branch and Multi-Country Model

Even while operating a single Bangladesh entity, every record carries the full dimensional
context. This is what makes Wave 9 expansion a configuration exercise rather than a rebuild.

| Dimension | Field | Source | Enforced By |
|---|---|---|---|
| Legal entity | `company_id` | `res.company` | Odoo multi-company rules |
| Country / jurisdiction | `country_id` | `res.country` | M30 locale pack |
| Branch / operating unit | `operating_unit_id` | OCA `operating.unit` | Record rules (M29) |
| Zone | `zone_id` | `fix.zone` | Dispatch and territory rules |
| Cost centre | `cost_center_id` | `fix.cost.center` | Finance posting rules |
| Business line | `business_line_id` | `fix.business.line` | Reporting and revenue attribution |
| Currency | `currency_id` | `res.currency` | Finance |
| Locale | `lang` | `res.lang` | Presentation and notification templates |

### Data Isolation Tiers

| Tier | Rule | Applies To |
|---|---|---|
| **T0 — Global** | Visible to all entities | Product catalogue, brand master, parts catalogue, checklist templates |
| **T1 — Entity** | Visible within a legal entity | Chart of accounts, tax configuration, payroll structures |
| **T2 — Branch** | Visible within an operating unit | Service orders, inventory, cash, local HR |
| **T3 — Zone** | Visible within a dispatch zone | Technician schedules, van stock |
| **T4 — Own record** | Visible to owner only | Customer's own orders, technician's own jobs, seller's own listings |
| **T5 — Restricted** | Explicit grant only | Payroll detail, recovered customer data, NID records, audit logs |

---

## 9. Business-Line Architecture

Nine business lines run through shared modules. Each is configured, not coded separately.

| Business Line | Order Object | Work Object | Billing Model | Modules Engaged |
|---|---|---|---|---|
| Warranty repair | Service Order (type=warranty) | Work Order | Brand claim | M01, M02, M09, M15, M20 |
| Paid repair | Service Order (type=paid) | Work Order | Invoice on completion | M01, M02, M11, M15, M19 |
| AMC / RAMC | Contract | Scheduled Work Order | Recurring subscription | M08, M01, M02, M20 |
| Managed services | MSP Contract | MSP Ticket / Patch Job | Per-seat or per-asset recurring | M05, M08, M20, M27 |
| Data services | Data Case | Recovery / Backup Job | Fixed fee or subscription | M06, M20, M24 |
| Rental | Rental Agreement | Delivery / Collection / Service | Period + usage + damages | M13, M03, M17, M20 |
| Trade-in & resale | Trade-In Offer / Sales Order | Refurb Work Order | Purchase then margin on resale | M14, M12, M15, M20 |
| Marketplace | Marketplace Order | Seller Job | Commission + fees | M12, M11, M20, M23 |
| Recycling | Collection Event | Recycling Batch | Fee or material recovery credit | M18, M03, M20 |

**Design consequence:** the Service Order object must be *polymorphic by service line*
without becoming a god-object. This is achieved with a thin `fix.service.order` core plus
line-specific extension models linked one-to-one, each owned by its business-line module.

---

## 10. Non-Negotiable Architecture Standards

| # | Standard | Rationale |
|---|---|---|
| AS-01 | No module accesses another module's tables directly | Preserves module boundaries and refactorability |
| AS-02 | All custom models inherit `mail.thread` + `mail.activity.mixin` | Universal chatter, audit and task capability |
| AS-03 | All custom models carry `operating_unit_id` and `company_id` | Multi-branch/multi-entity from day one |
| AS-04 | All custom tables prefixed `fix_`; models prefixed `fix.` | Distinguishable from Odoo and OCA |
| AS-05 | OCA modules are extended via `_inherit`, never forked, unless architecture board approves | Upgrade path preservation |
| AS-06 | Every state machine is explicit, with allowed transitions declared in one place | Testability and audit |
| AS-07 | Every API is versioned (`/v1/`, `/v2/`) and documented in OpenAPI 3.1 | Contract stability for 12 portals |
| AS-08 | Every write path emits a domain event via the outbox | Auditability and loose coupling |
| AS-09 | No business logic in views, controllers, or portal code | Single place to change a rule |
| AS-10 | All money uses `Monetary` with explicit currency; no floats | Financial integrity |
| AS-11 | All timestamps stored UTC, presented in Asia/Dhaka | Multi-country readiness |
| AS-12 | All user-facing strings translatable; Bengali translation is a definition-of-done item | Bengali-first principle |
| AS-13 | Offline-capable apps use an append-only local journal with server-side conflict resolution | Data integrity in the field |
| AS-14 | Personally identifiable and recovered customer data is encrypted at field level | ISO 27001 / Digital Security Act |
| AS-15 | Every module ships with unit tests ≥ 80% and its KPI instrumentation | Quality and measurability |

---

## 11. Module-to-Layer Allocation Summary

| Module | L1 | L2 | L3 | L4 | L5 | L6 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| M01 SRM | ● | ●● | | | ●● | |
| M02 FSM | ● | ●● | ● | ●● | ●● | |
| M03 LOG | ● | ● | | ● | ●● | |
| M04 FRD | ● | | | | ●● | |
| M05 RMS | | ● | | ●● | ●● | ○ |
| M06 DTS | | ● | | ● | ●● | |
| M07 CRM | ●● | ● | | | ● | |
| M08 CTR | ● | ●● | | | ●● | |
| M09 WTY | | ●● | | ● | ●● | |
| M10 LOY | ● | ● | | | ●● | |
| M11 SLS | ●● | ● | | | ●● | |
| M12 ECM | ● | ● | ● | | ●●● | ○ |
| M13 RNT | ● | ● | | | ●● | |
| M14 TRF | ● | ● | | | ●● | |
| M15 INV | ●● | ●● | ● | | ● | |
| M16 SCM | ●● | ● | | | ● | |
| M17 AST | ● | ●● | | ● | ●● | |
| M18 ESG | ● | ● | | | ● | |
| M19 FIN | ●● | ●● | ● | | ●● | |
| M20 BIL | ● | ● | | | ●●● | |
| M21 HRM | ●● | ●● | | | ●● | |
| M22 LMS | ● | ● | | ● | ●● | |
| M23 QMS | | ●●● | | | ● | |
| M24 DMS | ● | ●● | | ●● | ● | ○ |
| M25 BID | | ●● | | ●●● | ● | |
| M26 AIM | | | | ●● | ●●● | |
| M27 CCE | | ● | | ●● | ●● | ○ |
| M28 IPF | ● | ● | | ●●● | ●● | |
| M29 SEC | ● | ● | | ●●● | ● | |
| M30 ADM | ●● | ● | | | ●● | |

● = some ● ●● = substantial ● ●●● = primary ● ○ = optional/conditional

---

*Next document: `04_Module_Catalog_Master_Register.md`*
