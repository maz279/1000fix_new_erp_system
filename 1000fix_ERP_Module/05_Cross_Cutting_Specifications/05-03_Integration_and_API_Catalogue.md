---
id: FIX-ERP2-013
title: Integration & API Catalog
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL
---

# Integration & API Catalog
# 47 External Integrations · Internal API Surface · Domain Event Catalogue

---

## 1. Integration Principles

| # | Principle | Consequence |
|---|---|---|
| IP-01 | The ERP is the system of record; integrations synchronise, they do not duplicate authority | Every field has one owning system, declared |
| IP-02 | All traffic passes through the API gateway | One place for auth, rate limits, versioning, observability |
| IP-03 | Every integration declares its pattern | Sync request/response · async command · domain event · webhook · batch file |
| IP-04 | Every integration is idempotent | Retries and replays never double-apply |
| IP-05 | Every integration fails safely | Circuit breakers, timeouts, graceful degradation with user-visible messaging |
| IP-06 | Every integration is observable | Health, throughput, latency and error rate on a dashboard; alerting on failure |
| IP-07 | No credentials in code or configuration files | Vault-stored, rotated, access-audited |
| IP-08 | Every external contract is versioned and documented | OpenAPI 3.1 for REST; JSON Schema for events |
| IP-09 | Third-party outages must not stop the business | Defined manual fallback for every P0 integration |
| IP-10 | Data leaving the Company is minimised and logged | Only the fields the counterparty needs |

---

## 2. External Integration Catalogue

### 2.1 Payments (9)

| ID | Integration | Direction | Pattern | Purpose | Module | Wave | Pri |
|---|---|---|---|---|---|:--:|:--:|
| INT-001 | bKash | Bidirectional | Sync + webhook | Mobile money collection, refund, reversal | M19, M20 | W3 | P0 |
| INT-002 | Nagad | Bidirectional | Sync + webhook | Mobile money collection, refund | M19, M20 | W3 | P0 |
| INT-003 | SSLCOMMERZ | Bidirectional | Sync + webhook | Card, net banking, aggregated wallets | M19, M20 | W3 | P0 |
| INT-004 | Rocket (via aggregator) | Bidirectional | Sync | Mobile money collection | M19, M20 | W3 | P1 |
| INT-005 | Bank BEFTN | Outbound | Batch file | Payroll and vendor disbursement | M19, M21 | W5 | P0 |
| INT-006 | Bank statement import | Inbound | Batch file / API | Automated reconciliation | M19 | W3 | P0 |
| INT-007 | Seller payout rail | Outbound | Batch + API | Marketplace seller payouts | M20 | W7 | P1 |
| INT-008 | International gateway (Stripe/PayPal) | Bidirectional | Sync + webhook | Cross-border customer payments | M20 | W9 | P3 |
| INT-009 | Instalment / BNPL partner | Bidirectional | Sync + webhook | Consumer instalment on high-value repairs and refurbished sales | M20 | W8 | P3 |

### 2.2 Communications (9)

| ID | Integration | Direction | Pattern | Purpose | Module | Wave | Pri |
|---|---|---|---|---|---|:--:|:--:|
| INT-010 | Bangladesh SMS gateway (primary) | Outbound | Sync | Transactional SMS, OTP | M27 | W1 | P0 |
| INT-011 | Bangladesh SMS gateway (failover) | Outbound | Sync | Redundancy for P0 messaging | M27 | W2 | P1 |
| INT-012 | WhatsApp Business Cloud API | Bidirectional | Sync + webhook | Notifications, conversations, invoice sharing | M27 | W1 | P0 |
| INT-013 | Email (SMTP/API) | Bidirectional | Sync + IMAP | Transactional and marketing email; inbound parsing to tickets | M27 | W1 | P0 |
| INT-014 | Push notifications (FCM/APNs) | Outbound | Sync | Mobile push to customer, technician, rider and seller apps | M27 | W2 | P0 |
| INT-015 | Cloud telephony / IVR | Bidirectional | SIP + API + webhook | Hotline 16743, call routing, recording | M27 | W4 | P1 |
| INT-016 | WebRTC video | Bidirectional | Sync | Video support sessions | M27 | W6 | P3 |
| INT-017 | Social messaging (Messenger, IMO) | Bidirectional | Webhook | Additional customer conversation channels | M27 | W6 | P3 |
| INT-018 | In-app chat infrastructure | Bidirectional | WebSocket | Real-time chat across portals | M27 | W4 | P1 |

### 2.3 Location, Mapping & Logistics (9)

| ID | Integration | Direction | Pattern | Purpose | Module | Wave | Pri |
|---|---|---|---|---|---|:--:|:--:|
| INT-019 | Google Maps Platform | Outbound | Sync | Geocoding, map display, navigation handoff | M02, M03, M07 | W2 | P0 |
| INT-020 | OSRM (self-hosted) | Outbound | Sync | Road distance and duration matrices | M02, M03 | W2 | P1 |
| INT-021 | VROOM (self-hosted) | Outbound | Sync | Vehicle routing problem solving | M02, M03 | W2 | P1 |
| INT-022 | Traffic data API | Outbound | Sync | Real-time traffic for Dhaka metro | M02 | W2 | P2 |
| INT-023 | Traccar GPS server | Bidirectional | REST + WebSocket | Technician and vehicle position streaming | M02 | W2 | P0 |
| INT-024 | Courier partner — Pathao | Bidirectional | REST + webhook | Consignment booking and tracking | M03 | W3 | P2 |
| INT-025 | Courier partner — RedX | Bidirectional | REST + webhook | Consignment booking and tracking | M03 | W3 | P2 |
| INT-026 | Courier partner — Steadfast/Sundarban | Bidirectional | REST + webhook | Nationwide coverage | M03 | W3 | P2 |
| INT-027 | International freight forwarder | Bidirectional | API / file | Cross-border shipments and customs documents | M03, M16 | W9 | P3 |

### 2.4 Remote Support & Monitoring (6)

| ID | Integration | Direction | Pattern | Purpose | Module | Wave | Pri |
|---|---|---|---|---|---|:--:|:--:|
| INT-028 | Remote desktop (RustDesk / MeshCentral) | Bidirectional | API | Attended and unattended remote sessions | M05 | W5 | P1 |
| INT-029 | Monitoring agent telemetry | Inbound | Agent push | Endpoint and server metrics | M05, M17 | W5 | P1 |
| INT-030 | SNMP / ICMP collector | Inbound | Poll | Agentless network device monitoring | M05 | W5 | P1 |
| INT-031 | Patch feed / update catalogue | Inbound | Sync | Available patch inventory | M05 | W6 | P2 |
| INT-032 | Endpoint protection console | Inbound | API | Antivirus/EDR status across client estates | M05 | W6 | P2 |
| INT-033 | Cloud provider APIs (M365 / Google / AWS) | Inbound | API | Client cloud subscription, licence and health data | M05 | W6 | P2 |

### 2.5 Marketplace & Trust (4)

| ID | Integration | Direction | Pattern | Purpose | Module | Wave | Pri |
|---|---|---|---|---|---|:--:|:--:|
| INT-034 | NID / identity verification | Outbound | Sync | Verify seller and high-value customer identity | M12, M07 | W7 | P0 |
| INT-035 | Trade licence / business registry check | Outbound | Sync | Verify seller business registration | M12 | W7 | P1 |
| INT-036 | IMEI / stolen-device blocklist | Outbound | Sync | Screen trade-in devices | M14 | W6 | P1 |
| INT-037 | Ad delivery service | Bidirectional | API | Serve and measure marketplace advertising | M12 | W7 | P2 |

### 2.6 Government & Compliance (5)

| ID | Integration | Direction | Pattern | Purpose | Module | Wave | Pri |
|---|---|---|---|---|---|:--:|:--:|
| INT-038 | NBR e-VAT filing | Outbound | File / API | VAT return submission | M19 | W4 | P0 |
| INT-039 | BIN / TIN validation | Outbound | Sync | Validate customer and vendor tax identity | M19 | W3 | P1 |
| INT-040 | e-waste authority reporting | Outbound | File | Statutory e-waste returns | M18 | W8 | P2 |
| INT-041 | Biometric attendance devices | Inbound | SDK / file | Staff attendance capture | M21 | W5 | P1 |
| INT-042 | RJSC / company registry | Outbound | Sync | Corporate customer verification | M07 | W9 | P3 |

### 2.7 AI, Data & Enterprise (5)

| ID | Integration | Direction | Pattern | Purpose | Module | Wave | Pri |
|---|---|---|---|---|---|:--:|:--:|
| INT-043 | Self-hosted LLM inference | Outbound | Sync | Bengali assistant, summarisation, drafting | M26, M27 | W6 | P2 |
| INT-044 | OCR service | Outbound | Sync | Document extraction including Bengali | M24, M16 | W3 | P2 |
| INT-045 | Speech-to-text (Bengali) | Outbound | Sync/async | Call transcription, voice notes | M26, M27 | W8 | P3 |
| INT-046 | Corporate client SSO (SAML/OIDC per client) | Bidirectional | Federation | Corporate portal access using client credentials | M29 | W6 | P2 |
| INT-047 | Client ITSM (ServiceNow / Jira) | Bidirectional | REST + webhook | Ticket exchange with enterprise MSP clients | M05 | W7 | P3 |

### Integration Priority Summary

| Priority | Count | Notes |
|---|---:|---|
| P0 | 12 | Business stops without them; manual fallback documented for each |
| P1 | 17 | Significant degradation; workaround available |
| P2 | 12 | Reduced capability; deferrable |
| P3 | 6 | Enhancement; opportunistic |

---

## 3. Portal Platform Integration (CON-03)

The Next.js 15 + Payload CMS 3 platform cannot be replaced. This is the most important
integration in the estate and has its own contract.

### 3.1 Field Ownership

| Data | Owned By | Direction | Sync |
|---|---|---|---|
| Customer identity and profile | ERP (M07) | ERP → Portal | Event-driven, near real-time |
| Customer authentication | Identity provider (M29) | Shared | Federated |
| Marketing content, pages, blog, SEO | Portal (Payload CMS) | Portal only | — |
| Service catalogue and prices | ERP (M11, M15) | ERP → Portal | Scheduled + on change |
| Branch and coverage data | ERP (M30) | ERP → Portal | On change |
| Booking availability | ERP (M02) | Portal queries ERP | Synchronous |
| Service orders | ERP (M01) | Portal → ERP on create; ERP → Portal on update | Sync + events |
| Order status and tracking | ERP (M01, M02) | ERP → Portal | Events + polling fallback |
| Invoices and payments | ERP (M19, M20) | ERP → Portal | Events |
| Contracts and entitlements | ERP (M08) | ERP → Portal | Events |
| Loyalty points and vouchers | ERP (M10) | ERP → Portal | Events |
| Reviews and ratings | ERP (M12) | Portal → ERP on submit; ERP → Portal on publish | Sync |

### 3.2 Core API Surface (ERP ← Portal)

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v1/service-orders` | POST | Create a service order from a web or app booking |
| `/api/v1/service-orders/{id}` | GET | Retrieve full order detail (scoped to the requesting customer) |
| `/api/v1/service-orders/{id}/status` | GET | Lightweight status for the tracking page |
| `/api/v1/service-orders/{id}/reschedule` | POST | Reschedule within policy |
| `/api/v1/service-orders/{id}/cancel` | POST | Cancel within policy |
| `/api/v1/booking/availability` | GET | Available slots by service, location and date |
| `/api/v1/quotations/{id}/decision` | POST | Accept, part-accept or reject an estimate |
| `/api/v1/technicians/{id}/location` | GET | Live technician position and ETA for an active job |
| `/api/v1/customers/{id}` | GET/PATCH | Customer profile read and update |
| `/api/v1/customers/{id}/assets` | GET/POST | Registered devices |
| `/api/v1/customers/{id}/contracts` | GET | Active contracts and entitlements |
| `/api/v1/customers/{id}/invoices` | GET | Invoices and payment status |
| `/api/v1/customers/{id}/loyalty` | GET | Tier, points, vouchers |
| `/api/v1/catalogue/services` | GET | Service catalogue with prices |
| `/api/v1/catalogue/products` | GET | Parts, accessories, refurbished stock |
| `/api/v1/warranty/check` | POST | Warranty status by serial |
| `/api/v1/payments/confirm` | POST | Payment gateway confirmation |
| `/api/v1/consignments/{id}` | GET | Pick & drop tracking |
| `/api/v1/rentals/availability` | GET | Rental availability |
| `/api/v1/tradein/quote` | POST | Trade-in indicative valuation |
| `/api/v1/marketplace/offers` | GET/POST | Marketplace offers and selection |
| `/api/v1/branches` | GET | Branch directory with capabilities |

### 3.3 Webhooks (ERP → Portal)

| Event | Payload Summary |
|---|---|
| `service_order.created` | Order id, customer, asset, type, promised date, tracking token |
| `service_order.status_changed` | Order id, from state, to state, timestamp, customer-safe message |
| `technician.dispatched` | Order id, technician name/photo, ETA, tracking token |
| `technician.location_updated` | Order id, coordinates, ETA (throttled) |
| `estimate.issued` | Order id, estimate id, total, expiry, approval link |
| `invoice.created` | Invoice id, order id, amount, due date, payment link |
| `payment.received` | Invoice id, amount, method, receipt link |
| `contract.expiring` | Contract id, expiry date, renewal link |
| `loyalty.points_changed` | Customer id, delta, new balance, reason |
| `consignment.status_changed` | Consignment id, status, ETA |
| `catalogue.updated` | Changed catalogue item ids |

### 3.4 Contract Rules

| Rule | Detail |
|---|---|
| Versioning | Both sides support at least two API versions concurrently; six months' notice before removing a version |
| Idempotency | Every POST accepts an `Idempotency-Key`; duplicate keys return the original result |
| Authentication | OAuth 2.0 client credentials issued per environment; tokens short-lived |
| Rate limits | 600 requests/minute per portal instance; burst 100/second |
| Timeouts | Portal timeout 5 s on synchronous calls; ERP responds within 2 s at p95 |
| Failure behaviour | Portal degrades gracefully — cached catalogue, queued booking with confirmation on recovery |
| Reconciliation | Nightly reconciliation job compares order and customer counts; divergence alerts |

---

## 4. Domain Event Catalogue

### 4.1 Event Naming and Envelope

```
<aggregate>.<past-tense-verb>
```

Every event carries a standard envelope:

```json
{
  "event_id": "uuid",
  "event_type": "service_order.completed",
  "schema_version": "1.2",
  "occurred_at": "2026-08-12T09:14:22Z",
  "company_id": 1,
  "operating_unit_id": 17,
  "actor": { "type": "user", "id": 442 },
  "correlation_id": "uuid",
  "causation_id": "uuid",
  "aggregate": { "type": "service_order", "id": 918234 },
  "payload": { }
}
```

### 4.2 Event Inventory (Principal Events)

| Event | Producer | Principal Consumers |
|---|---|---|
| `service_order.created` | M01 | M02, M07, M20, M23, M25, M27 |
| `service_order.classified` | M01 | M08, M09, M11 |
| `service_order.estimated` | M01 | M11, M20, M27 |
| `service_order.approved` | M01 | M15, M02, M20 |
| `service_order.on_hold` | M01 | M02, M27, M23 |
| `service_order.completed` | M01 | M09, M15, M20, M23, M25, M27 |
| `service_order.closed` | M01 | M07, M20, M25 |
| `service_order.cancelled` | M01 | M02, M15, M20 |
| `work_order.assigned` | M02 | M01, M21, M27 |
| `work_order.started` | M02 | M01, M25 |
| `work_order.completed` | M02 | M01, M15, M21, M23 |
| `technician.dispatched` | M02 | M27, portal |
| `technician.arrived` | M02 | M01, M27 |
| `sla.warning` | M01 | M02, M27, M23 |
| `sla.breached` | M01 | M08, M23, M20 |
| `rework.detected` | M01 | M21, M23, M26 |
| `consignment.created` | M03 | M01, M27 |
| `consignment.custody_transferred` | M03 | M01, M17, M24 |
| `consignment.delivered` | M03 | M01, M13, M20, M27 |
| `part.consumed` | M15 | M01, M09, M19, M26 |
| `stock.below_reorder` | M15 | M16, M27 |
| `stock.count_variance` | M15 | M19, M23 |
| `goods.received` | M16 | M15, M19 |
| `purchase_order.issued` | M16 | M15, portal P05 |
| `asset.registered` | M17 | M07, M08, M09 |
| `asset.status_changed` | M17 | M13, M14, M18 |
| `asset.health_degraded` | M17 | M05, M08, M26 |
| `contract.activated` | M08 | M01, M05, M17, M20 |
| `contract.entitlement_consumed` | M08 | M20, M25 |
| `contract.expiring` | M08 | M10, M27, portal |
| `contract.terminated` | M08 | M01, M05, M20 |
| `warranty_claim.created` | M09 | M20, M25, portal P08 |
| `warranty_claim.submitted` | M09 | M20, M25 |
| `warranty_claim.decided` | M09 | M19, M20, M23 |
| `invoice.created` | M20 | M19, M27, portal |
| `invoice.paid` | M20 | M01, M19, M07, M27 |
| `payment.failed` | M20 | M27 |
| `refund.processed` | M20 | M19, M07, M27 |
| `commission.earned` | M12 | M20 |
| `payout.executed` | M20 | M12, M19, portal P07 |
| `seller.approved` | M12 | M02, M22, M20 |
| `seller.suspended` | M12 | M02, M20 |
| `review.published` | M12 | M07, M23, M25 |
| `dispute.raised` | M12 | M20, M23 |
| `rental.dispatched` | M13 | M03, M17, M20 |
| `rental.returned` | M13 | M17, M20, M15 |
| `tradein.accepted` | M14 | M17, M20, M15 |
| `refurb.graded` | M14 | M12, M15, M20 |
| `wipe.certified` | M06 | M14, M18, M24 |
| `ewaste.disposed` | M18 | M17, M24, M25 |
| `alert.raised` | M05 | M01, M27, M25 |
| `msp_ticket.resolved` | M05 | M08, M20, M25 |
| `employee.joined` | M21 | M29, M22, M30 |
| `employee.left` | M21 | M29, M02, M15 |
| `certification.expiring` | M22 | M02, M21, M27 |
| `certification.expired` | M22 | M02 (hard dispatch block) |
| `payroll.approved` | M21 | M19, M24 |
| `nonconformance.raised` | M23 | M01, M16, M12, M21 |
| `capa.closed` | M23 | M25 |
| `complaint.raised` | M07/M23 | M27, M25, management |
| `customer.registered` | M07 | M10, M27, M25 |
| `customer.merged` | M07 | all consumers holding customer ids |
| `price_book.published` | M11 | M12, portal, M20 |
| `model.prediction_made` | M26 | consuming module + audit |

### 4.3 Consumer Rules

| Rule | Detail |
|---|---|
| Idempotency | Every consumer records processed `event_id`s and ignores duplicates |
| Ordering | Ordering guaranteed per aggregate id only, never globally |
| Failure | Three retries with exponential backoff, then dead-letter with alert |
| Replay | Any consumer can be replayed from a point in time without side effects on other consumers |
| Schema | Additive changes only within a `schema_version`; breaking changes require a new version and a dual-publish period |
| Latency target | 95% of events consumed within 5 seconds of publication |

---

## 5. Internal API Surface

### 5.1 API Families

| Family | Base Path | Consumers | Auth |
|---|---|---|---|
| Customer API | `/api/v1/customer/*` | P01, P04, chatbot | OAuth 2.0 user token, customer-scoped |
| Technician API | `/api/v1/technician/*` | P02 | OAuth 2.0 + PKCE, technician-scoped |
| Operations API | `/api/v1/ops/*` | P03, P10 | OAuth 2.0 staff token, role-scoped |
| Corporate API | `/api/v1/corporate/*` | P04 | OAuth 2.0, corporate-account-scoped |
| Vendor API | `/api/v1/vendor/*` | P05 | OAuth 2.0, vendor-scoped |
| Seller API | `/api/v1/seller/*` | P07 | OAuth 2.0, seller-scoped |
| Brand API | `/api/v1/brand/*` | P08 | OAuth 2.0, brand-scoped |
| Logistics API | `/api/v1/logistics/*` | P09 | OAuth 2.0, rider/coordinator-scoped |
| Analytics API | `/api/v1/analytics/*` | P06, embedded dashboards | OAuth 2.0 + row-level security context |
| Admin API | `/api/v1/admin/*` | P03 system console | OAuth 2.0 + MFA + step-up |
| Partner API | `/api/v1/partner/*` | P12, external partners | OAuth 2.0 client credentials |
| Webhook receiver | `/hooks/v1/*` | External systems | Signature verification |

### 5.2 API Standards

| # | Standard |
|---|---|
| API-01 | REST over HTTPS with JSON; GraphQL only through the federation layer for composed portal reads |
| API-02 | Versioned in the path (`/v1/`); minimum two concurrent versions; six months' deprecation notice |
| API-03 | OpenAPI 3.1 specification generated from code and validated in CI; published to the developer portal |
| API-04 | Standard error envelope: `code`, `message` (localised), `details`, `correlation_id` |
| API-05 | Cursor-based pagination on all collections; maximum page size enforced |
| API-06 | Filtering, sorting and sparse field selection on all collection endpoints |
| API-07 | `Idempotency-Key` supported and required on all state-changing operations |
| API-08 | Rate limits per consumer with `X-RateLimit-*` headers and 429 with `Retry-After` |
| API-09 | Every response carries a `correlation_id` for tracing |
| API-10 | No endpoint returns data outside the caller's authorisation scope, ever — enforced server-side |
| API-11 | Bengali and English error and validation messages driven by `Accept-Language` |
| API-12 | Payload size limits enforced; large exports go through an async job with a download link |

### 5.3 Performance Targets

| Endpoint Class | p50 | p95 | p99 |
|---|---|---|---|
| Status / lookup reads | 80 ms | 250 ms | 500 ms |
| Standard reads with joins | 150 ms | 400 ms | 800 ms |
| Writes (create/update) | 200 ms | 500 ms | 1,000 ms |
| Search | 200 ms | 600 ms | 1,200 ms |
| Availability calculation | 300 ms | 800 ms | 1,500 ms |
| Analytics queries | 1 s | 5 s | 10 s |

---

## 6. Offline Synchronisation Protocol

Used by P02 (technician), P09 (rider) and P11 (auditor).

| Aspect | Design |
|---|---|
| Local store | Encrypted local database with an append-only action journal |
| Data scope | Only the user's assigned work, plus reference data they need; scope re-evaluated on each sync |
| Action model | Every user action is a discrete, idempotent command with a client-generated UUID |
| Upload | Commands replayed in order on reconnection; server acknowledges each by UUID |
| Download | Delta since last successful sync token; full refresh available on demand |
| Conflict policy | Server is authoritative for assignment, pricing, stock and state; client wins for evidence, notes and timestamps captured in the field |
| Conflict visibility | Any resolved conflict is shown to the user with what changed and why |
| Duration guarantee | 24 hours of offline operation with no data loss |
| Sync target | Complete within 30 seconds of connectivity restoration on a 3G connection |
| Integrity | Checksums on every batch; failed batches retried, never partially applied |
| Storage limits | Automatic pruning of synced, closed work older than the retention window |

---

## 7. Integration Monitoring

| Metric | Threshold | Action |
|---|---|---|
| Integration availability | < 99% over 15 minutes | Alert integration owner |
| Error rate | > 2% over 5 minutes | Alert; open incident if sustained |
| Latency p95 | > 2× baseline over 10 minutes | Alert |
| Queue depth | > 1,000 pending | Alert; investigate consumer health |
| Dead-letter count | > 0 for more than 1 hour | Alert; mandatory triage |
| Webhook delivery failure | > 5 consecutive to one endpoint | Disable endpoint; notify owner |
| Credential expiry | 30 days before | Alert; schedule rotation |
| Third-party outage detected | Any | Switch to fallback; notify affected users |

### Fallback Register for P0 Integrations

| Integration | Fallback |
|---|---|
| bKash / Nagad / SSLCOMMERZ | Alternative gateway; cash at counter; payment link resent when restored |
| SMS gateway | Failover gateway; WhatsApp; push; queued for retry |
| WhatsApp | SMS; email; in-app inbox |
| Google Maps | Cached geocodes; OSRM-only routing; manual address entry |
| Traccar | Last known position; manual status updates by technician |
| Bank statement import | Manual statement upload |
| BEFTN | Manual bank file submission via bank portal |
| NBR e-VAT | Manual portal filing from generated return |
| Identity verification | Manual document review by compliance |
| Push notifications | SMS fallback for critical messages |
| LLM inference | Rule-based responses; direct human routing |
| Telephony | Divert hotline to mobile numbers with manual logging |

---

## 8. Integration Delivery Sequence

| Wave | Integrations Delivered |
|---|---|
| W1 | INT-010, INT-012, INT-013 (SMS, WhatsApp, email) |
| W2 | INT-011, INT-014, INT-019, INT-020, INT-021, INT-022, INT-023 (redundant SMS, push, mapping, routing, GPS) |
| W3 | INT-001…004, INT-006, INT-024…026, INT-039, INT-044 (payments, bank, couriers, tax validation, OCR) |
| W4 | INT-015, INT-018, INT-038 (telephony, chat, e-VAT) |
| W5 | INT-005, INT-028…030, INT-041 (BEFTN, remote support, monitoring, biometric) |
| W6 | INT-016, INT-017, INT-031…033, INT-036, INT-043, INT-046 (video, social, patch/EDR/cloud, IMEI check, LLM, corporate SSO) |
| W7 | INT-007, INT-034, INT-035, INT-037, INT-047 (payouts, KYC, ads, client ITSM) |
| W8 | INT-009, INT-040, INT-045 (instalments, e-waste reporting, speech-to-text) |
| W9 | INT-008, INT-027, INT-042 (international payments and freight, company registry) |

---

*Next document: `14_Role_Permission_and_Access_Matrix.md`*
