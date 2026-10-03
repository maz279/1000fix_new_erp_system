---
id: FIX-ERP2-M28
module_id: M28
module_code: IPF
module_name: Integration, API & Event Platform
category: K — Platform & Technology
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Technology Officer
system_owner: Platform Squad
priority: P0
wave: W1
---

# M28 — Integration, API & Event Platform
### Category K · Code `IPF` · Existing (re-scoped in v2.1)

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M28 |
| **Module code** | `IPF` |
| **Category** | K — Platform & Technology |
| **Status** | Existing (re-scoped in v2.1 — workflow and approval execution moved to M63) |
| **Priority** | **P0** — one of the three modules built first |
| **Delivery wave** | W1 (Months 1–4), extended through every subsequent wave as integrations land |
| **Business owner** | Chief Technology Officer |
| **System owner** | Platform Squad |
| **Delivery layers** | L4 Kong · Redis Streams · Redpanda · OpenTelemetry · L5 custom outbox, schema registry, connector framework and sync engine |
| **Custom modules** | `cd_event_outbox`, `cd_api_layer`, `cd_webhook`, `cd_sync_engine`, `cd_integration_monitor` |
| **Requirement range** | FR-IPF-001 … FR-IPF-057 |
| **Requirement count** | **57** *(measured — within the 001–058 range allocated in `05-01` §1.3)* |
| **Effort estimate** | **30 person-weeks** *(measured — supersedes the 26 PW estimate in `02-02`)* |
| **Depends on** | M29 Identity (token introspection) · M30 Platform Admin (entity and environment context) |
| **Depended on by** | **All 66 other modules and all 12 portals** |

---

## 2. Purpose

M28 is **the connective tissue of the estate**. It is the reason a service order raised in
M01 causes a warranty claim in M09, an invoice in M20 and an SMS from M27 without any of those
four modules knowing the others exist.

It owns three things the other sixty modules must never build for themselves: **the way a
module exposes an API**, **the way a module publishes and consumes an event**, and **the way
the Company talks to the 47 systems outside its own walls**.

The category overview states the promise plainly: *every module can publish and consume events
reliably, exactly once, in order per aggregate*, and *every module can expose a versioned,
documented, rate-limited API without building plumbing*. If M28 does not deliver that as a
framework, sixty teams will each solve it badly, and within two years the architecture is a
point-to-point mesh that nobody can change.

### Why It Exists

**Because 67 modules and 12 portals cannot integrate pairwise.** Sixty-seven modules connected
directly is a theoretical 2,211 relationships. Through a platform it is 67 producers and a
catalogue of events.

**Because the portal platform cannot be replaced.** Constraint CON-03 fixes the Next.js 15 +
Payload CMS 3 estate in place. The ERP and the portal must therefore agree on field ownership,
API contracts and reconciliation — the most important single integration in the estate, and it
is M28's contract to hold.

**Because integrations fail, and the business must not.** Twelve of the 47 external
integrations are P0: payments, SMS, WhatsApp, maps, GPS. Every one of them will be down at some
point. IP-09 requires a documented, tested manual fallback for each.

**Because the platform team must not become the bottleneck.** Category risk: *"Platform team
becomes a bottleneck for all 60 other modules."* The mitigation is that M28 ships
**self-service capability** — a module publishes an API and an event through a framework, not
through a ticket to the platform team.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| `_CATEGORY_OVERVIEW.md` §7 promises 1, 2 | Reliable exactly-once eventing per aggregate; versioned documented rate-limited APIs without per-module plumbing |
| `_CATEGORY_OVERVIEW.md` §6 | M28 owns gateway, event bus, outbox, schema registry, dead letters, connectors and credentials; **M63 owns workflow and business-rule execution** |
| `_CATEGORY_OVERVIEW.md` §9 | API availability > 99.95%, p95 < 400 ms, event delivery > 99.9%, zero dead letters beyond 1 hour, 100% OpenAPI coverage, zero data divergence |
| `_CATEGORY_OVERVIEW.md` §11 | Risk: modules bypassing the platform to integrate point-to-point — "the architecture becomes a mesh within two years" |
| `05-03` §1 IP-01 … IP-10 | The ten integration principles this module enforces |
| `05-03` §2 | The full catalogue of **47 external integrations**, INT-001 … INT-047, with pattern, wave and priority |
| `05-03` §3 | The portal platform contract (CON-03): field ownership, API surface, webhooks, versioning, reconciliation |
| `05-03` §4 | Event naming, the standard envelope, the principal event inventory and the consumer rules |
| `05-03` §5 | Twelve API families, API-01 … API-12 standards, and per-class performance targets |
| `05-03` §6 | The offline synchronisation protocol for P02, P09 and P11 |
| `05-03` §7 | Integration monitoring thresholds and the P0 fallback register |
| `05-06` NFR-002, NFR-043, NFR-092 | API p95 ≤ 400 ms; event delivery ≤ 5 s p95; distributed tracing with a single correlation id |
| `05-06` AS-01, AS-07, AS-08 | No direct cross-module table access; every API versioned and documented; every write path emits through the outbox |
| `05-06` DI-05 | Event delivery at-least-once with idempotent consumption |
| `02-01` §7 | The five integration patterns every integration must declare |

---

## 3. Scope Boundary

> **The rule:** M28 owns **the pipe, not the payload, and not the decision**. It moves messages
> reliably, authenticates the caller and observes the traffic. It never interprets business
> content and never decides what should happen next.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | API gateway: routing, TLS termination, request/response transformation, header handling |
| 2 | Token validation and introspection against M29; scope enforcement at the edge |
| 3 | Rate limiting, quotas, burst control and bot protection per consumer |
| 4 | API versioning, concurrent version support, deprecation and sunset lifecycle |
| 5 | OpenAPI 3.1 specification generation, validation in CI, and publication |
| 6 | Developer portal: API catalogue, interactive documentation, credential self-service, usage dashboards |
| 7 | API consumer registry, credential issue, rotation and revocation |
| 8 | Standard error envelope, pagination, filtering, sparse fieldsets and idempotency-key handling |
| 9 | GraphQL federation layer for composed portal reads |
| 10 | **Transactional outbox** — the single mechanism by which every module publishes an event |
| 11 | Event bus operation: topics, partitioning by aggregate, retention, replay |
| 12 | **Event schema registry** with compatibility enforcement and versioned envelopes |
| 13 | Subscription management: which consumer receives which event, with filters |
| 14 | Delivery guarantees: at-least-once, ordered per aggregate, with consumer idempotency support |
| 15 | Retry with exponential backoff, **dead-letter queues**, triage tooling and replay |
| 16 | Event catalogue and producer/consumer contract testing |
| 17 | Outbound webhooks: endpoint registry, signing, delivery, retry, auto-disable |
| 18 | Inbound webhooks: signature verification, replay protection, idempotent ingestion |
| 19 | **External connector framework** — a common shape for all 47 integrations |
| 20 | Integration credential management through the vault, with rotation and expiry alerting |
| 21 | Circuit breakers, timeouts, bulkheads and graceful degradation |
| 22 | **Fallback orchestration**: detecting a third-party outage and switching to the registered fallback |
| 23 | Batch and file exchange: SFTP, signed file drop, scheduled import and export |
| 24 | **Offline synchronisation protocol** — the shared engine behind P02, P09 and P11 |
| 25 | Conflict detection and server-authoritative resolution for offline sync |
| 26 | **The portal platform contract (CON-03)**: field ownership, sync direction, nightly reconciliation |
| 27 | Cross-system reconciliation and divergence alerting |
| 28 | Integration observability: health, throughput, latency, error rate, queue depth, per-integration dashboards |
| 29 | Distributed tracing with a single correlation id across every hop |
| 30 | Sandbox environments and partner onboarding for external API consumers |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Workflow, approval chains, business-rule execution** | **M63** Process Automation (Category J) | This is the sharpest boundary in Category K. M28 delivers the message; M63 decides what happens because of it. Merging them produces an ESB with business logic inside — the architecture the programme exists to avoid |
| Business-rule parameters and thresholds | **M64** MDM (stores) / **M63** (executes) | M28 carries neither |
| Authentication, identity, session, MFA, permissions | **M29** | M28 *validates* a token at the edge; it never issues one, and it never decides what a role may do |
| Encryption key material and data classification | **M29** | M28 enforces TLS; field-level key management is a security concern |
| Organisation structure, environments, feature flags, scheduled-job registry | **M30** | M28 consumes entity and environment context |
| Country pack, locale, translation infrastructure | **M65** | — |
| The content of any event payload | The **producing module** | M28 validates the envelope and the schema; it never validates business meaning |
| The business meaning of an external integration | The **owning module** (M19 payments, M27 messaging, M02 GPS, …) | M28 owns the connector shape; the module owns what the data means |
| Analytical data movement, ETL, warehouse loading | **M62** Data Platform | Event streams feed the warehouse; the pipeline is M62's |
| Dashboards and business reporting | **M25** BI | M28 exposes platform telemetry, not business insight |
| Internal IT incident and change management | **M66** ITSM | An integration outage raises an alert; M66 runs the incident process |
| ML model serving | **M26** AI/ML | The ML gateway is M26's; M28 routes to it |
| Document storage and retention | **M24** | — |
| Portal user experience and content | Portal platform (CON-03) | M28 owns the contract, not the front end |

### 3.3 Shared Concepts

| Concept | M28's Role | Owning Module |
|---|---|---|
| Domain event | **Owns** the envelope, transport, schema and delivery; the producer owns the payload | M28 / producer |
| API | **Owns** the gateway, standards, versioning and documentation; the module owns the endpoint's behaviour | M28 / module |
| Token and scope | Validates and enforces at the edge | M29 |
| Correlation id | **Owns** — generated at the edge, propagated through every hop | M28 |
| Integration credential | **Owns** the lifecycle; the vault holds the secret | M28 / M30 |
| Offline sync | **Owns** the protocol and engine; the app owns its own data scope | M28 / M02, M03, M23 |
| Portal contract | **Owns** | M28 |
| Outage and fallback | Detects and switches; the owning module defines the manual fallback | M28 / module |
| Platform health telemetry | **Owns** integration health; M30 owns the platform health console | M28 / M30 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Transactional outbox pattern (microservices.io, AWS Prescriptive Guidance)** | Write the event to an outbox table inside the same transaction that changes the business object; a separate process publishes it | **The single most important pattern in M28, and it is mandatory estate-wide (AS-08).** A business write and its event are one logical change; if one succeeds and the other fails, downstream systems observe incomplete state. No module may publish directly from business logic | The polling-publisher-versus-log-tailing debate is settled pragmatically: polling publisher on PostgreSQL to Wave 5, with change-data-capture available if throughput demands it |
| **Confluent Schema Registry practice** | A registry enforcing consistent event structure, with compatibility modes preventing breaking changes | **Schema registry with additive-only compatibility inside a `schema_version`**, and a mandatory dual-publish period for breaking changes (`05-03` §4.3). This is what stops one team's refactor breaking six consumers | The full Avro toolchain; we use JSON Schema, which is legible to the whole team and adequate at our volumes |
| **Dead-letter queue practice** | Unprocessable messages captured for inspection behind every consumer, monitored | **A monitored DLQ behind every consumer**, with the category KPI set at **zero events unresolved beyond one hour**. A DLQ nobody watches is a silent data-loss channel | — |
| **Kong / Azure API Management / Apache APISIX** | Gateway policy enforcement: auth, rate limiting, caching, transformation; developer portal with interactive documentation generated from OpenAPI; consumer self-service credentials | Gateway-enforced policy so that auth, limits and observability exist in **one place rather than 67**; the **developer portal** as the self-service surface that keeps the platform team off the critical path | Commercial API management licensing; Kong's open tier is sufficient at our consumer count |
| **API governance practice (2025–26)** | A published rule set for design, auth, versioning, limits and deprecation; automated linting and contract validation in CI; discovery and tracking | **Governance enforced in CI, not by review.** `05-03` §5.2 API-01…API-12 become linter rules and contract tests. A specification that is not enforced is documentation, not governance | A central API review board as a gate; it recreates the bottleneck |
| **IETF HTTP deprecation and sunset headers** | Machine-readable deprecation signalling to consumers | `Deprecation` and `Sunset` headers on every superseded version, alongside the six-month notice in `05-03` §3.4 | — |
| **Circuit breaker / bulkhead (resilience patterns)** | Prevent a failing dependency cascading; isolate failure domains | Circuit breakers and timeouts on every outbound connector, with the **fallback register** from `05-03` §7 wired as automatic behaviour rather than a runbook instruction | — |
| **Enterprise integration patterns (pub-sub, content-based routing, aggregator)** | The classical message-oriented vocabulary | Publish-subscribe and content-based routing (subscription filters) | The ESB heritage — orchestration and transformation logic living in the integration layer. That is M63's job, and keeping it out of M28 is deliberate |
| **OpenTelemetry (CNCF baseline)** | Vendor-neutral traces, metrics and logs with context propagation | **A single correlation id from portal click to database write to event consumption** (NFR-092). Without it, debugging a 67-module estate is guesswork | Vendor-specific agents; the collector is neutral by design |

**Design position.** Four deliberate differences.

First, **the outbox is not optional and not per-module**. Most ERP programmes let modules
choose how to notify each other, and end up with a mixture of direct calls, triggers and
scheduled comparisons. In 1000FiX the outbox is a framework primitive: a module raises an
event by calling one function, and AS-08 is verified by an event-coverage test in CI. The cost
is a small tax on every write path; the return is that the estate remains changeable.

Second, **M28 carries no business logic whatsoever, and workflow lives in M63**. This is
enforced structurally — M28's code has no dependency on any business module. The
temptation to "just add a small rule in the integration layer" is how integration platforms
become unmaintainable, and the boundary is drawn where it is precisely because that temptation
is strongest at Wave 1 when M63 does not yet exist.

Third, **self-service is a delivery requirement, not a nice-to-have**. The category risk
register names the platform team becoming a bottleneck as a High risk. M28 is therefore judged
on whether a module team can publish an event, expose an API and register a consumer **without
opening a ticket**. Framework, generator, linter and developer portal exist for that reason.

Fourth, **fallback is automatic, not documented**. `05-03` §7 lists a manual fallback for each
P0 integration. A fallback that requires a human to notice the outage first is a fallback that
activates twenty minutes late. M28 detects the outage, switches to the registered alternative,
and tells the affected users — with the manual path as the last resort rather than the first.

---

## 5. Functional Areas & Features

### 5.1 API Gateway & Traffic Management

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-IPF-001 | API gateway | Route all internal and external API traffic through a single gateway, terminating TLS 1.3 and applying policy centrally (IP-02) | **P0** | L4 |
| FR-IPF-002 | Token validation | Validate and introspect OAuth 2.0 / OIDC tokens against M29 at the edge, rejecting unauthenticated and out-of-scope requests before they reach a module | **P0** | L4/L5 |
| FR-IPF-003 | Scope enforcement | Enforce the caller's authorisation scope at the gateway so that no endpoint can return data outside it, regardless of request parameters (API-10, EA-11) | **P0** | L5 |
| FR-IPF-004 | Rate limiting and quotas | Apply per-consumer rate limits and quotas with `X-RateLimit-*` headers and `429` plus `Retry-After` (API-08); default 600 req/min per portal instance, burst 100/s | **P0** | L4 |
| FR-IPF-005 | Bot protection | Apply bot detection and abuse protection on all public endpoints (NFR-068) | **P0** | L4 |
| FR-IPF-006 | Standard request handling | Enforce the standard error envelope (`code`, localised `message`, `details`, `correlation_id`), cursor pagination, filtering, sorting and sparse fieldsets (API-04…API-06) | **P0** | L5 |
| FR-IPF-007 | Idempotency | Accept and honour `Idempotency-Key` on every state-changing operation, returning the original result on a duplicate key (API-07, IP-04) | **P0** | L5 |
| FR-IPF-008 | Payload and export limits | Enforce payload size limits and route large exports to an asynchronous job with a download link (API-12) | P1 | L5 |
| FR-IPF-009 | Language negotiation | Return Bengali or English error and validation messages driven by `Accept-Language` (API-11) | **P0** | L5 |
| FR-IPF-010 | GraphQL federation | Provide a federation layer for composed portal reads without exposing it as a general-purpose write surface (API-01) | P1 | L4/L5 |

### 5.2 API Lifecycle & Governance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-IPF-011 | API registry | Maintain a registry of every published API with its owning module, family, version, status and consumers | **P0** | L5 |
| FR-IPF-012 | OpenAPI generation and validation | Generate an OpenAPI 3.1 specification from code for every endpoint and validate the implementation against it in CI, failing the build on divergence (AS-07, API-03) | **P0** | L5 |
| FR-IPF-013 | Versioning | Support at least two concurrent versions per API, versioned in the path, with traffic visible per version (API-02) | **P0** | L4 |
| FR-IPF-014 | Deprecation and sunset | Mark a version deprecated with machine-readable `Deprecation` and `Sunset` headers, notify registered consumers, enforce the six-month notice, and block removal while a consumer is still calling it | **P0** | L5 |
| FR-IPF-015 | Developer portal | Publish the API catalogue with interactive documentation, code samples, changelog and a sandbox, in one self-service surface | P1 | L5 |
| FR-IPF-016 | Consumer registry and credentials | Register API consumers, issue scoped credentials per environment, and support self-service rotation and revocation (IP-07) | **P0** | L5 |
| FR-IPF-017 | Usage analytics | Report per-consumer, per-endpoint, per-version usage, latency and error rate, and surface it to the consumer and the owning module | P1 | L5 |
| FR-IPF-018 | API linting | Enforce the API-01…API-12 standards automatically in CI, so that a non-conforming API cannot be released | **P0** | L5 |
| FR-IPF-019 | Sandbox environment | Provide a sandbox with representative masked data for external consumers and partner onboarding | P2 | L5 |
| FR-IPF-020 | Partner onboarding | Onboard an external API consumer with scoped credentials, documentation access, rate limits and an agreed support contract | P2 | L5 |

### 5.3 Domain Event Platform

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-IPF-021 | **Transactional outbox** | Provide the single framework primitive by which any module publishes a domain event, writing the event to the outbox inside the business transaction (AS-08) | **P0** | L5 |
| FR-IPF-022 | Outbox drain and publication | Drain the outbox to the event bus reliably, at-least-once, preserving order per aggregate id, with progress and lag observable | **P0** | L5 |
| FR-IPF-023 | Standard envelope | Enforce the standard envelope on every event — `event_id`, `event_type`, `schema_version`, `occurred_at`, `company_id`, `operating_unit_id`, `actor`, `correlation_id`, `causation_id`, `aggregate`, `payload` (`05-03` §4.1) | **P0** | L5 |
| FR-IPF-024 | Event naming | Enforce the `<aggregate>.<past-tense-verb>` convention at registration; reject imperative or present-tense names | **P0** | L5 |
| FR-IPF-025 | **Schema registry** | Register a JSON Schema per event type and version, enforce additive-only compatibility within a `schema_version`, and require a new version plus a dual-publish period for a breaking change | **P0** | L5 |
| FR-IPF-026 | Subscription management | Register which consumer receives which event type, with optional content filters, and make every subscription discoverable | **P0** | L5 |
| FR-IPF-027 | Delivery and ordering | Deliver at-least-once with ordering guaranteed per aggregate id and never globally, within a 5-second p95 target (NFR-043, DI-05) | **P0** | L4/L5 |
| FR-IPF-028 | Consumer idempotency support | Provide the framework by which a consumer records processed `event_id`s and ignores duplicates, so idempotency is inherited rather than re-implemented | **P0** | L5 |
| FR-IPF-029 | Retry and dead-lettering | Retry three times with exponential backoff, then dead-letter with an alert; hold the full envelope, the failure reason and the attempt history | **P0** | L5 |
| FR-IPF-030 | Dead-letter triage and replay | Present dead letters with their cause, allow correction and replay individually or in bulk, and record who replayed what | **P0** | L5 |
| FR-IPF-031 | Consumer replay | Replay any consumer from a point in time without side effects on other consumers | P1 | L5 |
| FR-IPF-032 | Event catalogue | Publish the living catalogue of every event type, its schema, its producer and its consumers, generated from the registry rather than maintained by hand | **P0** | L5 |
| FR-IPF-033 | Contract testing | Test every producer/consumer pair in CI for schema compatibility and consumer idempotency (`05-06` §11) | **P0** | L5 |

### 5.4 Webhooks

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-IPF-034 | Outbound webhook registry | Register outbound endpoints per consumer and event type, with a secret, retry policy and owner | **P0** | L5 |
| FR-IPF-035 | Outbound delivery and signing | Sign every outbound webhook, deliver over HTTPS, retry on failure, and record every attempt and response | **P0** | L5 |
| FR-IPF-036 | Endpoint auto-disable | Disable an endpoint after five consecutive delivery failures and notify its owner (`05-03` §7) | **P0** | L5 |
| FR-IPF-037 | Inbound webhook receiver | Receive third-party webhooks at `/hooks/v1/*` with signature verification, replay protection and idempotent ingestion (IP-04) | **P0** | L5 |
| FR-IPF-038 | Inbound routing | Route a verified inbound webhook to the owning module as a command or an event, without interpreting its business content | **P0** | L5 |

### 5.5 External Connectors, Credentials & Resilience

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-IPF-039 | Connector framework | Provide one connector shape — configuration, credentials, retry, timeout, circuit breaker, observability, fallback — used by all 47 integrations in `05-03` §2 | **P0** | L5 |
| FR-IPF-040 | Pattern declaration | Require every integration to declare its pattern: synchronous request/response, asynchronous command, domain event, webhook, or batch file (IP-03) | **P0** | L5 |
| FR-IPF-041 | Credential management | Hold every external credential in the vault, never in code, configuration or logs; support rotation and alert 30 days before expiry (IP-07, NFR-062) | **P0** | L4/L5 |
| FR-IPF-042 | Circuit breakers and timeouts | Apply a circuit breaker, timeout and bulkhead to every outbound connector, failing fast rather than exhausting resources (IP-05) | **P0** | L5 |
| FR-IPF-043 | **Automatic fallback** | Detect a third-party outage and switch to the registered fallback from `05-03` §7 — alternative payment gateway, failover SMS, cached geocodes, last-known GPS — and notify affected users with a clear message | **P0** | L5 |
| FR-IPF-044 | Data minimisation | Send only the fields the counterparty requires, and log what left the Company (IP-10) | **P0** | L5 |
| FR-IPF-045 | Batch and file exchange | Support scheduled and event-driven SFTP and signed file drop for BEFTN payroll, NBR returns, brand claim batches and statement import | **P0** | L5 |

### 5.6 Offline Synchronisation

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-IPF-046 | Sync protocol engine | Provide the shared offline synchronisation engine used by P02 technician, P09 rider and P11 auditor applications (`05-03` §6) | **P0** | L5 |
| FR-IPF-047 | Command journal | Model every offline user action as a discrete idempotent command with a client-generated UUID, replayed in order on reconnection and acknowledged individually (AS-13) | **P0** | L5 |
| FR-IPF-048 | Delta download and scoping | Download a delta since the last sync token, scoped to the user's assigned work plus the reference data they need, with scope re-evaluated each sync | **P0** | L5 |
| FR-IPF-049 | Conflict resolution | Apply the server-authoritative policy — server wins on assignment, pricing, stock and state; client wins on field-captured evidence, notes and timestamps — and surface every resolved conflict to the user with what changed and why | **P0** | L5 |
| FR-IPF-050 | Sync integrity and guarantees | Guarantee 24 hours of offline operation with zero data loss and zero double-application, checksummed per batch, with failed batches retried and never partially applied (DI-04, NFR-047) | **P0** | L5 |

### 5.7 Portal Contract, Reconciliation & Observability

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-IPF-051 | **Portal platform contract** | Implement and enforce the CON-03 contract in `05-03` §3: declared field ownership per data domain, sync direction, idempotency, dual-version support and graceful portal degradation | **P0** | L5 |
| FR-IPF-052 | **Cross-system reconciliation** | Reconcile record counts and key balances between the ERP and the portal nightly, and between the ERP and every stateful external system, alerting on divergence (DI-07) | **P0** | L5 |
| FR-IPF-053 | Integration health monitoring | Monitor availability, throughput, latency, error rate, queue depth and dead-letter count per integration against the `05-03` §7 thresholds, with alerting and a per-integration dashboard (IP-06) | **P0** | L5 |
| FR-IPF-054 | Distributed tracing | Propagate a single correlation id across every hop — portal, gateway, module, event, consumer, external call — and make an end-to-end trace retrievable by that id (NFR-092) | **P0** | L4 |
| FR-IPF-055 | Integration registry | Hold the authoritative register of all 47 integrations with owner, pattern, priority, wave, credentials reference, fallback and current health | **P0** | L5 |
| FR-IPF-056 | Direct-access prevention | Detect and block direct cross-module table access in CI through static analysis, enforcing AS-01 | **P0** | L5 |
| FR-IPF-057 | Platform self-service | Provide generators, templates and linting so a module team can publish an API and an event, and register a consumer, without platform-team involvement | **P0** | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Outbox atomicity** | The outbox write and the business write share one database transaction. A rollback discards both. There is no code path that publishes without an outbox row |
| T-02 | **Exactly-once effect from at-least-once delivery** | The bus guarantees at-least-once; consumers achieve exactly-once *effect* through framework-provided idempotency keyed on `event_id`. The distinction is stated explicitly because promising exactly-once delivery is not achievable and claiming it causes design errors downstream |
| T-03 | **Ordering scope** | Partitioning is by `aggregate.id`, so ordering holds per aggregate and never globally (`05-03` §4.3). Consumers must not assume cross-aggregate order |
| T-04 | **Schema compatibility gate** | Registration of an incompatible schema fails in CI. Breaking changes require a new `schema_version` and a dual-publish period with both versions live |
| T-05 | **Correlation propagation** | The gateway generates a `correlation_id` if absent; every module, event and outbound call propagates it. A request with no correlation id in its trace is a defect |
| T-06 | **Gateway latency budget** | Gateway overhead ≤ 25 ms at p95, inside the NFR-002 API budget of 400 ms p95 end to end |
| T-07 | **Event throughput envelope** | Designed for 5,000 events/minute sustained at Wave 8, with 10× burst headroom; Redis Streams to Wave 5, Redpanda from Wave 6 (TD-10) |
| T-08 | **Outbox lag alerting** | Outbox drain lag is a first-class metric; sustained lag above 30 seconds alerts, because a silent outbox is indistinguishable from a working one from the module's side |
| T-09 | **Poison-message isolation** | A message that fails deterministically is dead-lettered rather than retried indefinitely; one bad message never blocks a partition |
| T-10 | **Credential isolation** | Credentials are resolved at call time from the vault, never cached to disk, never logged, and scoped per environment (OPS-04) |
| T-11 | **Sync journal integrity** | The offline journal is append-only with per-batch checksums; a partially applied batch is impossible by construction |
| T-12 | **Multi-tenant context propagation** | `company_id` and `operating_unit_id` travel in the envelope and in the request context, so no consumer has to re-derive them (AS-03) |
| T-13 | **Zero-downtime deployment** | Gateway and consumer deployments are rolling; in-flight requests drain and unacknowledged events redeliver (NFR-008) |
| T-14 | **Observability cardinality control** | Metrics are dimensioned by integration, endpoint, version and status — not by customer or order id — to keep the telemetry cost trajectory defensible |
| T-15 | **No business dependency** | M28's code imports no business module. Verified by dependency analysis in CI. This is what keeps the boundary in §3.2 real |
| T-16 | **Availability** | Gateway and bus availability ≥ 99.95%, exceeding the NFR-006 system target because everything else depends on them |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M28 |
|---|---|---|
| **Customer** | Books on the website and the branch has no record until someone re-keys it | One booking, visible everywhere, tracked end to end |
| **Service centre agent** | Re-keys data between the portal, the spreadsheet and the system | Enters once; every downstream module reacts automatically |
| **Technician** | Loses work when the network drops in a stairwell | 24 hours offline with guaranteed sync and visible conflict resolution |
| **Finance** | Reconciles the portal against the ERP by eye, monthly | Nightly automated reconciliation with divergence alerts |
| **IT administrator** | Discovers a payment gateway is down when customers complain | Detected in minutes, fallback switched automatically, users told |
| **Module developer** | Would build their own API auth, retry, logging and event plumbing | Publishes an API and an event through a framework, in hours |
| **Integration partner** | Emails for documentation and credentials | Self-serves both from the developer portal |
| **CTO** | Cannot see how the estate actually connects | A live registry of 47 integrations, every API and every event, with health |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **The programme becomes possible at all** | 67 modules and 12 portals cannot integrate pairwise. Without a platform the architecture collapses into a mesh within two years — the explicit category risk | This is the enabling benefit. Every one of the **BDT 876 lac** annual benefits in the Executive Summary depends on modules being able to talk to each other |
| **Elimination of double entry** | One booking flows to order, dispatch, parts, invoice and notification without re-keying | A material share of the **BDT 62 lac/year** administrative labour saving attributed to cross-module automation |
| **Zero data divergence** | Nightly reconciliation between ERP and portal, and against every stateful external system | Category KPI: **zero divergence incidents**. Divergence is what destroys trust in a system and sends people back to spreadsheets |
| **Business continuity through outages** | Automatic fallback across 12 P0 integrations rather than a documented manual procedure | Payment path availability ≥ 99.95% (NFR-048) despite individual gateways failing |
| **Development velocity** | Self-service API and event publication; no platform ticket on the critical path | Removes the High-rated bottleneck risk; compounding effect across 60 downstream module builds |
| **Change safety** | Schema registry plus contract testing means a producer change cannot silently break six consumers | Avoids the class of production incident that is hardest to diagnose and most expensive to fix |
| **Field productivity** | Offline sync guarantees 24 hours of work with no loss across 200–400 technicians and 50–200 riders | Protects the **BDT 130 lac/year** technician productivity benefit in areas with poor connectivity |
| **Diagnostic cost** | One correlation id from portal click to event consumption | Turns multi-hour cross-team incident investigations into a single trace lookup |
| **Partner and expansion readiness** | Documented, versioned, sandboxed APIs | A precondition for the marketplace (W7), corporate client ITSM integration and multi-country expansion |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Architectural integrity over a decade** | AS-01 enforced in CI is the difference between a system that can be changed in year five and one that must be replaced |
| **Auditability** | Every event carries actor, timestamp, entity and correlation. ISO 9001 and ISO 27001 both ask how a change propagated; the answer is a query |
| **Vendor independence** | Connectors are a framework, not bespoke code. Replacing a payment gateway or a courier is a configuration and a connector, not a project |
| **Security posture** | One place where authentication, rate limiting, bot protection and data minimisation are enforced — rather than 67 places where they might be |
| **Knowledge retention** | The event catalogue and API registry are generated from the running system, so the documentation cannot drift from reality |
| **Regulatory readiness** | IP-10 data minimisation and egress logging directly support the PDPA 2026 cross-border and disclosure obligations |
| **Multi-country readiness** | Entity and operating-unit context in every envelope means a second country needs no change to the transport layer (BO-18) |

---

## 8. Lifecycle & State Models

### 8.1 Domain Event Lifecycle

```
   Module business transaction
            │
            │  ── same DB transaction (T-01) ──
            ▼
     ┌─────────────┐
     │  PENDING    │  row in fix_domain_event (the outbox)
     └──────┬──────┘
            │ drain process picks up, envelope validated against the schema registry
            │  ✖ schema invalid ──► REJECTED (producer alerted; never silently dropped)
     ┌──────▼──────┐
     │  PUBLISHED  │  on the bus, partitioned by aggregate.id
     └──────┬──────┘
            │ fan-out to every registered subscription
     ┌──────▼───────────┐
     │  DELIVERING      │  per consumer
     └──┬────────────┬──┘
        │            │ consumer error
        │       ┌────▼──────┐
        │       │ RETRYING  │  3 attempts, exponential backoff
        │       └────┬──────┘
        │            │ retries exhausted
        │       ┌────▼──────────┐
        │       │ DEAD LETTERED │ ◄── alert; **KPI: zero unresolved > 1 h**
        │       └────┬──────────┘
        │            │ cause corrected
        │       ┌────▼──────┐
        │       │ REPLAYED  │  who replayed, when, why — recorded
        │       └────┬──────┘
        │◄───────────┘
   ┌────▼──────┐
   │ CONSUMED  │  consumer records event_id; duplicates ignored (T-02)
   └───────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Pending | Business transaction commits with its outbox row | Producing module |
| Pending | Published | Envelope complete; schema registered and compatible | Drain process |
| Pending | Rejected | Schema invalid or unregistered event type | Drain process |
| Published | Delivering | One or more active subscriptions match | Bus |
| Delivering | Consumed | Consumer acknowledges; `event_id` recorded | Consumer |
| Delivering | Retrying | Consumer error or timeout | Bus |
| Retrying | Dead lettered | Three attempts exhausted | Bus |
| Dead lettered | Replayed | Cause corrected; replay authorised and recorded | IT Administrator / CTO |
| Any | (never) Deleted | Events are not deleted before their retention expires | — |

### 8.2 API Version Lifecycle

```
   DESIGNED ──► OpenAPI spec registered, linted (FR-IPF-018)
       │
       ▼
   PUBLISHED ──► live, documented in the developer portal, consumers registered
       │
       │ successor version released
       ▼
   DEPRECATED ──► Deprecation + Sunset headers returned;
       │          registered consumers notified;
       │          six-month clock starts (API-02)
       │
       ├──► consumers still calling at sunset ──► REMOVAL BLOCKED
       │                                          (escalate to consumer owner)
       ▼
    SUNSET ──► no traffic for the notice period; removal authorised
       │
       ▼
    RETIRED ──► routes removed; specification archived
```

### 8.3 Integration Health & Fallback

```
   HEALTHY ──► availability, latency, error rate within `05-03` §7 thresholds
      │
      │ error rate > 2% over 5 min, or availability < 99% over 15 min
      ▼
   DEGRADED ──► alert integration owner; circuit breaker half-open
      │
      │ circuit opens, or outage confirmed
      ▼
   FAILED ──► **automatic fallback engaged** (FR-IPF-043)
      │        affected users notified with a clear message
      │
      │ probe succeeds, error rate normalises
      ▼
   RECOVERING ──► traffic ramped back; queued work replayed
      │
      ▼
   HEALTHY
```

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-IPF-01 | **No module reads or writes another module's tables directly** (AS-01); static analysis blocks it in CI | **H** | CTO |
| BRU-IPF-02 | **Every write path emits its domain event through the transactional outbox** (AS-08); direct publication from business logic is prohibited | **H** | CTO |
| BRU-IPF-03 | All API traffic passes through the gateway; no module exposes a port directly (IP-02) | **H** | CTO |
| BRU-IPF-04 | Every API is versioned and has a current, CI-validated OpenAPI 3.1 specification (AS-07) | **H** | CTO |
| BRU-IPF-05 | An API version cannot be removed while a registered consumer is still calling it, or before its six-month notice expires | **H** | CTO |
| BRU-IPF-06 | An event schema change within a `schema_version` must be additive; a breaking change requires a new version and a dual-publish period | **H** | CTO |
| BRU-IPF-07 | Every consumer is idempotent and records processed `event_id`s | **H** | CTO |
| BRU-IPF-08 | Ordering is guaranteed per aggregate id only; no consumer may assume global ordering | **H** | CTO |
| BRU-IPF-09 | Every state-changing API operation accepts and honours an `Idempotency-Key` (API-07) | **H** | CTO |
| BRU-IPF-10 | No endpoint returns data outside the caller's authorisation scope, and scope cannot be widened by request parameters (API-10, EA-11) | **H** | CTO |
| BRU-IPF-11 | No credential appears in code, configuration files or logs; all are vault-held and rotated (IP-07, NFR-062) | **H** | CTO |
| BRU-IPF-12 | Every P0 integration has a registered, tested fallback; an integration without one cannot be promoted to production (IP-09, NFR-050) | **H** | CTO |
| BRU-IPF-13 | Every integration declares its pattern at registration (IP-03) | **H** | CTO |
| BRU-IPF-14 | A dead letter unresolved for more than one hour is an incident, not a backlog item | **H** | CTO |
| BRU-IPF-15 | Only the fields the counterparty requires leave the Company, and every egress is logged (IP-10) | **H** | CTO |
| BRU-IPF-16 | Offline sync never loses data and never double-applies a command (DI-04) | **H** | CTO |
| BRU-IPF-17 | The server is authoritative for assignment, pricing, stock and state; the client is authoritative for field-captured evidence, notes and timestamps | **C** | CTO |
| BRU-IPF-18 | A webhook endpoint failing five consecutive deliveries is disabled and its owner notified | **C** | CTO |
| BRU-IPF-19 | Nightly reconciliation runs against the portal and every stateful external system; divergence raises an alert and is investigated, never absorbed | **H** | CTO |
| BRU-IPF-20 | M28 contains no business logic and imports no business module; verified by dependency analysis in CI | **H** | CTO |
| BRU-IPF-21 | Non-production environments never hold live external credentials (NFR-071) | **H** | CTO |
| BRU-IPF-22 | An event is never deleted before its retention period expires; correction is a compensating event | **H** | CTO |

---

## 10. Data Entities

### 10.1 Owned Entities

Aligned to the 15 entities allocated to M28 in `05-02` §M28, extended where this specification
adds capability.

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.domain.event` | `fix_domain_event` | **The transactional outbox** (shared kernel) | event_id, event_type, schema_version, occurred_at, company_id, operating_unit_id, actor_json, correlation_id, causation_id, aggregate_type, aggregate_id, payload_json, published, published_at, attempts |
| `fix.event.schema` | `fix_event_schema` | The schema registry | event_type, schema_version, json_schema, compatibility_mode, producer_module, status, registered_by, effective_from, dual_publish_until |
| `fix.event.subscription` | `fix_event_subscription` | Who receives what | event_type, schema_version, consumer_module, consumer_endpoint, filter_expression, active, created_by |
| `fix.event.delivery` | `fix_event_delivery` | Per-consumer delivery record | event_id, subscription_id, attempt, state, delivered_at, latency_ms, error_code, error_detail |
| `fix.dead.letter` | `fix_dead_letter` | Undeliverable events | event_id, subscription_id, envelope_json, failure_reason, attempts, first_failed_at, triaged_by, replayed_at, replayed_by, resolution |
| `fix.api.consumer` | `fix_api_consumer` | Registered API consumer | name, type (portal/module/partner/external), owner_party_id, environment, scopes, rate_limit, quota, status |
| `fix.api.credential` | `fix_api_credential` | Issued credentials | consumer_id, client_id, secret_vault_ref, environment, issued_at, rotates_at, expires_at, revoked_at, revoked_reason |
| `fix.api.registry` | `fix_api_registry` | Every published API | path, method, family, owning_module, version, status (published/deprecated/sunset/retired), openapi_ref, deprecated_at, sunset_at, consumer_count |
| `fix.api.usage.log` | `fix_api_usage_log` | Traffic record | consumer_id, api_id, version, timestamp, status_code, latency_ms, bytes, correlation_id, rate_limited |
| `fix.webhook.endpoint` | `fix_webhook_endpoint` | Outbound webhook target | consumer_id, url, event_types, secret_vault_ref, retry_policy, consecutive_failures, active, disabled_at, owner_user_id |
| `fix.webhook.delivery` | `fix_webhook_delivery` | Outbound attempt | endpoint_id, event_id, attempt, request_hash, response_code, response_time_ms, delivered_at, error |
| `fix.integration.config` | `fix_integration_config` | The register of all 47 integrations | int_id (INT-nnn), name, direction, pattern, owning_module, priority, wave, endpoint_config, timeout_ms, retry_policy, circuit_breaker_config, fallback_id, health_state |
| `fix.integration.credential` | `fix_integration_credential` | External system credentials | integration_id, environment, vault_ref, credential_type, rotates_at, expires_at, last_rotated_by |
| `fix.integration.fallback` | `fix_integration_fallback` | The registered fallback per integration | integration_id, fallback_type (alternate/cached/queued/manual), fallback_target, user_message_key, last_tested_at, last_engaged_at, engagement_count |
| `fix.integration.health` | `fix_integration_health` | Live health per integration | integration_id, window_start, availability_pct, error_rate_pct, p95_latency_ms, queue_depth, dead_letter_count, state, alerted_at |
| `fix.sync.state` | `fix_sync_state` | Offline sync position per device | user_id, device_id, app (P02/P09/P11), last_sync_token, last_sync_at, scope_hash, pending_commands, journal_bytes |
| `fix.sync.command` | `fix_sync_command` | The offline command journal | client_uuid, user_id, device_id, command_type, payload_json, captured_at, received_at, applied_at, state, batch_checksum |
| `fix.sync.conflict` | `fix_sync_conflict` | Detected and resolved conflicts | command_id, entity_type, entity_id, field, client_value, server_value, resolution (server/client), rule_applied, surfaced_to_user_at |
| `fix.batch.job.run` | `fix_batch_job_run` | File exchange execution | integration_id, direction, file_ref, record_count, started_at, completed_at, state, control_total, error_detail |
| `fix.reconciliation.run` | `fix_reconciliation_run` | Cross-system reconciliation | scope (portal/external/internal), target_system, run_at, records_compared, divergences_found, divergence_detail_ref, alerted, resolved_at |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.identity`, token introspection endpoint | M29 | Synchronous call at the edge |
| `fix.role`, `fix.permission.set` (scope resolution) | M29 | Read |
| `fix.entity`, `fix.branch`, `fix.feature.flag` | M30 | Read for context and rollout control |
| `fix.config.parameter` | M30 | Read |
| `fix.country.pack`, `fix.locale.pack` | M65 | Read for locale-aware error messages |
| Every module's published API and event definitions | Each module | Registered by the module; M28 holds the registry |
| `fix.scheduled.job` | M30 / M63 | Read; M28 runs the batch-exchange jobs registered there |
| Vault secret references | M30 platform infrastructure | Resolve at call time |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-IPF-01 | Business transaction commits with an outbox row | Drain, validate the envelope against the schema registry, publish to the bus partitioned by aggregate id | Retain as pending; alert on drain lag > 30 s |
| AUT-IPF-02 | Event published | Fan out to every matching active subscription | Retry per consumer independently |
| AUT-IPF-03 | Consumer delivery fails | Retry three times with exponential backoff | Dead-letter with alert after the third failure |
| AUT-IPF-04 | Event dead-lettered | Alert the consumer's owning team with the envelope and failure reason; open the triage item | Escalate to CTO if unresolved at one hour |
| AUT-IPF-05 | Dead letter replayed | Re-deliver to the failing consumer only, record who replayed and why | Return to dead letter with the new failure |
| AUT-IPF-06 | Schema registration attempted | Validate compatibility against the current version; accept additive changes, reject breaking ones | **Hard block in CI** with the incompatibility explained |
| AUT-IPF-07 | API deployed | Generate and publish the OpenAPI specification, validate the implementation against it, update the developer portal | Fail the build |
| AUT-IPF-08 | API version deprecated | Emit `Deprecation` and `Sunset` headers, notify every registered consumer, start the six-month clock | Alert only |
| AUT-IPF-09 | Sunset date reached with live traffic | Block removal, notify the consumer owner and the API owner, escalate | Version remains live |
| AUT-IPF-10 | Rate limit exceeded | Return `429` with `Retry-After`; record against the consumer; alert on sustained breach | — |
| AUT-IPF-11 | Integration error rate > 2% over 5 minutes | Alert the integration owner; open the circuit if the threshold is sustained | Escalate |
| AUT-IPF-12 | Circuit opens or outage confirmed | **Engage the registered fallback**; notify affected users with the localised message; queue recoverable work | Escalate to CTO; surface the manual fallback instruction |
| AUT-IPF-13 | Third-party recovers | Half-open the circuit, ramp traffic, replay queued work, notify that normal service has resumed | Remain on fallback; alert |
| AUT-IPF-14 | Webhook delivery fails five consecutive times | Disable the endpoint and notify its owner | — |
| AUT-IPF-15 | Credential within 30 days of expiry | Alert the integration owner and schedule rotation | Escalate at 7 days |
| AUT-IPF-16 | Device reconnects after offline work | Replay the command journal in order, acknowledge each by UUID, resolve conflicts by policy, surface them to the user | Retain the journal; retry; never partially apply a batch |
| AUT-IPF-17 | Nightly | Reconcile ERP against the portal and every stateful external system; alert on divergence | Alert; retry the run |
| AUT-IPF-18 | Queue depth > 1,000 pending | Alert; investigate consumer health; scale consumers where automatic scaling applies | Escalate |
| AUT-IPF-19 | Pull request opened | Run static analysis for direct cross-module table access, API linting, contract tests and event-coverage tests | **Fail the build** |
| AUT-IPF-20 | Batch file exchange scheduled | Execute, verify control totals, record the run, notify the owning module | Retry per policy; alert the owning module on failure |

---

## 12. Interfaces

### 12.1 Upstream — M28 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M29 Identity** | Token introspection, scope resolution, consumer identity | REST (synchronous, at the edge) |
| **M30 Platform Admin** | Entity, branch and environment context; feature flags; scheduled-job registry; vault references | REST |
| **Every module (all 66)** | Outbox rows, API registrations, event schema registrations, subscription registrations | Framework primitives |
| M65 Localisation | Locale packs for localised error and user messages | REST |
| M63 Process Automation | Subscription registrations for workflow triggers | Framework |
| External systems (47) | Webhook callbacks, batch files, API responses | Per `05-03` §2 |

### 12.2 Downstream — M28 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **Every module (all 66)** | Event publication and consumption; API exposure; connector framework; correlation context | Framework + bus |
| **All 12 portals** | The gateway, the API families and the contract in `05-03` §5.1 | REST / GraphQL |
| **P02, P09, P11** | The offline synchronisation engine | REST + journal |
| **Portal platform (CON-03)** | The contract: APIs, webhooks, field ownership, reconciliation | REST + webhooks |
| M63 Process Automation | Event stream that triggers workflows | Events |
| M62 Data Platform | Event stream as a warehouse source | Events |
| M30 Platform Admin | Integration health feeding the platform health console | Events + REST |
| M66 ITSM | Integration incidents raised as internal IT incidents | Events |
| M29 Identity | API access logs and anomalous-access signals | Events |
| M25 BI | Platform and integration telemetry | Warehouse extract |
| External partners | Documented, sandboxed, versioned APIs | Developer portal + REST |

### 12.3 Domain Events Published

M28 publishes only **platform** events. It transports every business event but authors none.

| Event | Payload Summary | Consumers |
|---|---|---|
| `platform.event_dead_lettered` | event id, type, consumer, failure reason, attempts | M66, M30, owning team |
| `platform.event_replayed` | event id, consumer, replayed by, reason | M29 (audit), M66 |
| `platform.integration_degraded` | integration, metric breached, threshold, current value | M30, M66, owning module |
| `platform.integration_failed` | integration, cause, fallback engaged | M30, M66, M27 (user messaging) |
| `platform.integration_recovered` | integration, downtime, queued work replayed | M30, M66 |
| `platform.fallback_engaged` | integration, fallback type, affected user scope | M27, M30 |
| `platform.api_deprecated` | api, version, sunset date, affected consumers | consumer owners, M66 |
| `platform.api_version_retired` | api, version, retired at | M30 |
| `platform.schema_registered` | event type, version, producer, compatibility | producing and consuming teams |
| `platform.rate_limit_breached` | consumer, api, window, count | M29, M30 |
| `platform.credential_expiring` | integration, environment, days remaining | M30, M66 |
| `platform.webhook_endpoint_disabled` | endpoint, consumer, consecutive failures | consumer owner, M66 |
| `platform.reconciliation_divergence` | scope, target system, divergence count, detail ref | M30, M66, owning module |
| `platform.sync_conflict_resolved` | user, device, entity, field, resolution | originating module, M23 |
| `platform.direct_access_violation` | module, target table, build reference | M30, CTO |

### 12.4 External Integrations

M28 does not own the business meaning of any external integration, but it owns the **register
and the connector shape for all 47** catalogued in `05-03` §2. The infrastructure integrations
below are M28's own.

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-IPF-01 | **Kong Gateway** | Internal | API gateway, policy enforcement, rate limiting, routing |
| INT-IPF-02 | **Redis Streams** (to W5) / **Redpanda** (W6+) | Internal | Event bus transport (TD-10) |
| INT-IPF-03 | **HashiCorp Vault** (or equivalent) | Internal | Credential storage, rotation and access audit |
| INT-IPF-04 | **OpenTelemetry Collector → Prometheus / Loki / Tempo → Grafana** | Internal | Traces, metrics, logs, platform dashboards |
| INT-IPF-05 | **n8n** | Internal | Low-code connector authoring for long-tail integrations, under M28 governance |
| INT-IPF-06 | SFTP endpoints (banks, NBR, brand partners) | Bidirectional | Batch file exchange for BEFTN, VAT returns and claim batches |
| INT-IPF-07 | **Portal platform (Next.js 15 + Payload CMS 3)** | Bidirectional | The CON-03 contract — the single most important integration in the estate |
| INT-001 … INT-047 | All catalogued external systems | Various | Transported and governed by M28; business meaning owned by the module named in `05-03` §2 |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/*` | Various | The gateway front door for all 12 API families (`05-03` §5.1) | All portals and partners |
| `/hooks/v1/{integration}` | POST | Verified inbound webhook receiver | External systems |
| `/api/v1/platform/events/schemas` | GET/POST | Register or browse an event schema | Module teams, CI |
| `/api/v1/platform/events/catalogue` | GET | The living event catalogue with producers and consumers | Module teams, developer portal |
| `/api/v1/platform/events/subscriptions` | GET/POST/DELETE | Manage subscriptions | Module teams |
| `/api/v1/platform/events/dead-letters` | GET | Triage queue with cause and envelope | IT Administrator, module teams |
| `/api/v1/platform/events/dead-letters/{id}/replay` | POST | Replay a dead letter (recorded) | IT Administrator |
| `/api/v1/platform/events/replay` | POST | Replay a consumer from a point in time | IT Administrator |
| `/api/v1/platform/apis` | GET | The API registry with versions, status and consumers | Developer portal |
| `/api/v1/platform/consumers` | GET/POST | Register a consumer and issue scoped credentials | Developer portal, IT Administrator |
| `/api/v1/platform/consumers/{id}/credentials/rotate` | POST | Self-service credential rotation | Consumer owner |
| `/api/v1/platform/integrations` | GET | The 47-integration register with health and fallback state | P03, P06 |
| `/api/v1/platform/integrations/{id}/health` | GET | Live health for one integration | P03, M30 |
| `/api/v1/platform/integrations/{id}/test-fallback` | POST | Exercise a registered fallback (non-production and scheduled drills) | IT Administrator |
| `/api/v1/platform/sync` | POST | Offline command journal replay | P02, P09, P11 |
| `/api/v1/platform/sync/delta` | GET | Delta download since a sync token | P02, P09, P11 |
| `/api/v1/platform/reconciliation` | GET | Reconciliation runs and divergences | P03, Finance |
| `/api/v1/platform/trace/{correlation_id}` | GET | End-to-end trace for one correlation id | IT Administrator, module teams |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R02 Chief Technology Officer | C R U D A | All; sole approver of architecture-standard exceptions |
| R33 IT / System Administrator | C R U D A | All operational functions: dead-letter triage, replay, credential rotation, fallback drills |
| R01 Chief Executive Officer · R03 Chief Financial Officer · R05 Operations Director | R | Integration health summary and platform availability only |
| R26 Finance Manager | R | Payment and bank integration health; reconciliation divergences |
| R32 Quality Manager / ISO Coordinator | R | Sync conflicts and reconciliation divergences as quality signals |
| Module development teams *(not an `05-04` business role)* | C R U | **Own module's** APIs, schemas and subscriptions — self-service |
| R38 External Party (partner API consumer) | R U | Own consumer registration, own credentials, own usage — developer portal only |

**Elevated operations.** Event replay, dead-letter resolution, credential rotation and fallback
engagement are privileged actions requiring step-up authentication (NFR-065) and are recorded
as security events in M29 (NFR-070).

**Field-level restrictions.** Event payloads may contain personal data. Dead-letter and trace
views **mask residency-classified and S3-classified fields** (NFR-086, NFR-061); an
administrator triaging a delivery failure sees the envelope and the failure, not the customer's
NID. Unmasked payload inspection requires named CTO approval and is itself audited.

**Segregation of duties.**
- The engineer who registers a schema cannot approve its breaking-change dual-publish exception.
- Credential rotation and credential approval for external financial integrations are separate actors.
- No role may disable a reconciliation job; suppression requires CTO approval and is time-boxed.

> **Note.** `05-04` §1 contains no "platform engineer" or "module developer" role. Category K
> makes extensive use of self-service by development teams, and this gap is raised as an audit
> action against `05-04`.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Integration health board** | IT Administrator, CTO | Real time | All 47 integrations: availability, latency, error rate, queue depth, circuit state, fallback engagement |
| **Event platform board** | IT Administrator, CTO | Real time | Outbox lag, publication rate, delivery latency, dead-letter count and age, consumer lag by subscription |
| API traffic and performance | CTO, module owners | Daily | Requests by consumer, endpoint and version; p50/p95/p99 against `05-03` §5.3; error rate; rate-limit breaches |
| **Dead-letter register** | IT Administrator, module teams | Real time | Every dead letter with cause, age and owner — **KPI: zero beyond one hour** |
| API version adoption | CTO, module owners | Monthly | Traffic by version; deprecated versions still in use; consumers blocking a sunset |
| OpenAPI coverage | CTO | Weekly | Share of endpoints with a current, validated specification — target 100% |
| **Reconciliation divergence** | CTO, Finance Manager, module owners | Daily | Divergences between ERP and portal and every stateful external system — **target zero** |
| Offline sync health | CTO, Operations Director | Daily | Devices syncing, journal depth, conflicts by type and resolution, failed batches |
| Fallback engagement log | CTO, Operations Director | Monthly | Which fallbacks engaged, for how long, user impact, and drill results |
| Credential and certificate expiry | IT Administrator | Weekly | Credentials expiring within 30 days; rotation status |
| Architecture-standard compliance | CTO, Architect | Per build + monthly | AS-01 violations blocked, AS-07 and AS-08 coverage, contract-test results |
| Platform self-service usage | CTO | Quarterly | APIs and events published by module teams without platform-team involvement — the bottleneck-risk measure |
| Egress and data-minimisation log | CTO, Quality Manager | Monthly | What data left the Company, to whom, under which integration (IP-10, PDPA) |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| — | **API availability** | n/a | 99.9% | **> 99.95%** |
| — | **API p95 latency** | n/a | < 500 ms | **< 400 ms** (NFR-002) |
| — | **Event delivery success** | n/a | 99.5% | **> 99.9%** |
| — | **Events unresolved in dead letter > 1 hour** | n/a | **Zero** | **Zero** |
| — | **APIs with a current OpenAPI specification** | n/a | 100% | **100%** |
| — | **Data divergence incidents (ERP vs portal)** | n/a | **Zero** | **Zero** |
| — | Event delivery latency p95 | n/a | < 8 s | **< 5 s** (NFR-043) |
| — | Outbox drain lag p95 | n/a | < 10 s | **< 3 s** |
| — | Direct cross-module table access violations reaching production | unknown | **Zero** | **Zero** |
| — | P0 integrations with a tested automatic fallback | 0% | **100%** | **100%** |
| — | Mean time to detect a third-party outage | hours | < 5 min | **< 2 min** |
| — | Offline sync data loss incidents | unknown | **Zero** | **Zero** |
| — | Offline sync completion after 24 h offline (3G) | n/a | ≤ 45 s | **≤ 30 s** (NFR-037) |
| — | APIs and events published without platform-team involvement | 0% | 70% | **95%** |
| — | Requests traceable end to end by correlation id | 0% | 98% | **100%** |
| — | Breaking schema changes reaching production | unknown | **Zero** | **Zero** |

> **Register note.** `_CATEGORY_OVERVIEW.md` §9 names six of these as the category KPIs owned by
> M28. **None has a canonical `KPI-0nn` identifier** — `06-02` §2.6 ends at KPI-049 and has no
> platform section. Allocation for all sixteen metrics is an audit action.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `base` transaction and ORM hooks underpinning the outbox write | 6% |
| L2 | OCA `server-tools` (technical utilities, audit hooks), OCA `web` (Keycloak auth integration) | 6% |
| L4 | **Kong Gateway**, **Redis Streams**, **Redpanda**, **OpenTelemetry + Prometheus + Loki + Tempo + Grafana**, **n8n**, Vault | 34% |
| L5 | `cd_event_outbox`, `cd_api_layer`, `cd_webhook`, `cd_sync_engine`, `cd_integration_monitor` | 54% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-125 | `cd_event_outbox` — outbox primitive, drain, envelope, schema registry, subscriptions, delivery, dead letters, replay, catalogue, contract testing | Odoo module + service | 9 PW |
| CD-126 | `cd_api_layer` — API registry, OpenAPI generation and validation, versioning and deprecation, standard envelope and pagination, idempotency, consumer and credential management, developer portal | Odoo module + service + frontend | 8 PW |
| CD-127 | `cd_webhook` — outbound registry, signing, delivery and retry, auto-disable; inbound verification, replay protection and idempotent routing | Odoo module | 3 PW |
| CD-128 | `cd_sync_engine` — offline command journal, delta scoping, conflict detection and server-authoritative resolution, batch integrity | Odoo module + service | 6 PW |
| CD-129 | `cd_integration_monitor` — integration register, connector framework, credential lifecycle, circuit breakers, **automatic fallback orchestration**, health monitoring, reconciliation, tracing integration | Odoo module + service | 4 PW |

> All five CD IDs retain their `02-05` §5.2 allocation. **All CD IDs remain provisional**
> pending the unified CD register required by audit finding M-01 in `02-05`.
>
> **Category K CD block (for cross-module coherence).** CD-125…129 M28 · CD-130…132 + CD-157…158
> M29 · CD-133, CD-135, CD-138 + CD-159 M30 · CD-134 + CD-160…161 M64 · CD-136…137 + CD-162 M65 ·
> CD-163…164 M66 · CD-165…167 M67. Category E holds CD-139…156.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M29 Identity** | Token introspection at the edge. M28 and M29 are built together in W1 and bootstrap each other: M29 needs the gateway to expose its endpoints; M28 needs M29 to validate tokens. The dependency is resolved by building the gateway's pass-through mode first and enabling introspection once M29's token endpoint is live |
| **M30 Platform Admin** | Entity, branch and environment context; the vault; the scheduled-job registry. Also W1 |
| Infrastructure: Kong, Redis, Vault, OpenTelemetry stack | Must be provisioned before any module can be built |
| **M63 Process Automation (W3)** | M28 must ship *without* workflow. Until M63 lands, event consumers implement their own reactions in-module. **No workflow logic may be added to M28 as an interim measure** — this is the boundary most at risk during W1–W2 |
| M65 Localisation (W9) | Localised error messages; until W9, Bengali and English strings are held in M30 configuration |
| M62 Data Platform (W4) | Event stream to the warehouse; M28 is unaffected if it lands later |

> **M28 is never "done".** It ships its framework in W1 and then absorbs integrations wave by
> wave, following the `05-03` §8 delivery sequence: 3 in W1, 7 in W2, 10 in W3, 3 in W4, 5 in
> W5, 8 in W6, 5 in W7, 3 in W8, 3 in W9. **The 30 PW estimate covers the platform framework
> and the W1–W2 integrations only**; each subsequent integration is costed with its owning
> module. This is a material scoping clarification and is raised as an audit finding.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Existing portal ↔ legacy system integrations | Few, undocumented | `fix.integration.config` | W1, surveyed and authored |
| Existing API consumers (order tracking, customer portal) | 2–4 | `fix.api.consumer` | W1 |
| Event catalogue | — | `fix.event.schema` | W1 onward, **authored per module as each is built** |
| Integration credentials | Currently in configuration files | Vault + `fix.integration.credential` | W1, rotated on migration |

> **Position.** M28 has almost nothing to migrate and almost everything to author. The
> significant task is the **credential sweep**: every existing credential in a configuration
> file or a developer's notes is moved to the vault and **rotated on migration**, on the
> assumption that anything previously held in plain text is compromised.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | No module in production reads or writes another module's tables; CI blocks the attempt | Static analysis over the full codebase plus a build-failure demonstration |
| AC-02 | Every write path that changes state emits its event through the outbox | Event-coverage test across all modules at each wave gate |
| AC-03 | A rollback of a business transaction discards its outbox row; no orphan events exist | Induced-failure test |
| AC-04 | Events are delivered at-least-once and ordered per aggregate id, and consumers achieve exactly-once effect | Ordering and duplicate-injection test at production volume |
| AC-05 | Event delivery success exceeds 99.9% with p95 latency under 5 seconds | Four weeks of production measurement |
| AC-06 | No dead letter remains unresolved beyond one hour | Twelve weeks of measurement |
| AC-07 | A breaking schema change is blocked in CI with the incompatibility explained | Negative test |
| AC-08 | 100% of published endpoints have a current, CI-validated OpenAPI 3.1 specification | Coverage report at each wave gate |
| AC-09 | An API version cannot be removed while a registered consumer is calling it or before its notice expires | Negative test |
| AC-10 | API availability exceeds 99.95% and p95 latency is under 400 ms | Four weeks of production measurement |
| AC-11 | No endpoint returns data outside the caller's scope, including via crafted parameters | Penetration test against API-10 and EA-11 |
| AC-12 | Every state-changing operation honours `Idempotency-Key`; a duplicate returns the original result | Contract test across all state-changing endpoints |
| AC-13 | Each of the 12 P0 integrations engages its fallback automatically within 2 minutes of an induced outage, and users receive a clear localised message | Scheduled fallback drill for all 12 |
| AC-14 | No credential appears in code, configuration or logs; all resolve from the vault | Secret scanning plus log inspection |
| AC-15 | Nightly reconciliation detects an injected divergence between ERP and portal and alerts | Scripted divergence injection |
| AC-16 | Zero production divergence incidents between ERP and portal | Twelve weeks of reconciliation records |
| AC-17 | A device offline for 24 hours synchronises within 30 seconds on 3G with no data loss and no double application | Field test with 20 devices across P02, P09 and P11 |
| AC-18 | Every resolved sync conflict is surfaced to the user with what changed and why | Scripted conflict scenario set |
| AC-19 | Any request is traceable end to end by a single correlation id, across portal, gateway, module, event and external call | Trace retrieval test |
| AC-20 | A module team publishes a new API and a new event without platform-team involvement | Timed exercise with two module teams |
| AC-21 | Dead-letter and trace views mask residency-classified and S3-classified fields | Negative test against NFR-086 and NFR-061 |
| AC-22 | M28 imports no business module | Dependency analysis |
| AC-23 | CTO signs off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 23 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **How is the M28/M29 W1 bootstrap sequenced in practice** — gateway pass-through first, or a temporary static credential? Both are live on day one and each needs the other. | CTO | W1 minus 1 month |
| Q-02 | Redis Streams to Wave 5 then Redpanda (TD-10) implies a migration of live subscriptions. When does it happen, and is dual-running required? | CTO | W4 |
| Q-03 | Is the vault self-hosted HashiCorp Vault or a managed alternative, and who holds the unseal keys under the split-residency architecture (NFR-086)? | CTO / CFO | W1 build |
| Q-04 | **Does the portal platform team accept the CON-03 contract as specified in `05-03` §3**, including dual-version support and nightly reconciliation? This is the single largest integration risk in the programme. | CTO / portal owner | W1 minus 2 months |
| Q-05 | What is the event retention period, and does it differ for events carrying personal data under PDPA 2026 minimisation? | CTO / Legal | W1 build |
| Q-06 | Who owns a dead letter when the producing and consuming modules disagree on the cause? A named default owner is required or triage stalls. | CTO | W1 build |
| Q-07 | Is a developer portal for **internal** module teams justified in W1, or does internal self-service run on generated documentation until the marketplace wave needs an external portal? | CTO | W1 design |
| Q-08 | What is the escalation path when a consumer refuses to migrate off a deprecated API version and blocks a sunset? | CTO | W3 |
| Q-09 | Does n8n's Sustainable Use licence permit its use for integrations that serve marketplace sellers and brand partners, or only for internal orchestration? | CTO / Legal | W6 (before M12) |
| Q-10 | **How are per-wave integration builds costed and staffed**, given that the 30 PW estimate covers only the framework and W1–W2 integrations? | CTO / Programme Manager | W2 |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §6 (boundary map), §7 (the platform contract, promises 1 and 2),
§9 (category KPIs), §11 (mesh and bottleneck risks) ·
`M29_Identity_Access_and_Information_Security.md` (token introspection, audit, step-up) ·
`M30_Platform_Administration_and_Configuration.md` (entity context, feature flags, health console) ·
`M63` Process Automation & Workflow Orchestration *(Category J — the workflow boundary)* ·
`05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md` §1 (IP-01…IP-10),
§2 (INT-001…047), §3 (CON-03 portal contract), §4 (event envelope, catalogue, consumer rules),
§5 (API families, API-01…API-12, performance targets), §6 (offline sync protocol),
§7 (monitoring thresholds, fallback register), §8 (integration delivery sequence) ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md`
NFR-002, NFR-008, NFR-037, NFR-043, NFR-047, NFR-050, NFR-061, NFR-062, NFR-065, NFR-068,
NFR-071, NFR-086, NFR-092; AS-01, AS-03, AS-07, AS-08, AS-13; DI-04, DI-05, DI-07; OPS-01…OPS-08 ·
`05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` §M28 (15 entities), DM-15 ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §7 (integration patterns), §10 (AS-01…AS-15) ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §4 (L4 systems), §5.2 (CD-125…129), TD-08, TD-10 ·
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md`

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` (integration requirements) ·
CON-03 portal platform constraint

**External benchmark**
[Transactional outbox pattern — microservices.io](https://microservices.io/patterns/data/transactional-outbox.html) ·
[Transactional outbox — AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) ·
[Transactional outbox trade-offs](https://www.softwarecraftsperson.com/posts/2025-10-08-transactional-outbox-pattern/) ·
[Event-driven architecture reference — outbox, idempotent consumers, monitored DLQ](https://www.digitalapplied.com/blog/event-driven-architecture-message-queues-2026-engineering-reference) ·
[Enterprise integration patterns for streaming architectures](https://tacnode.io/post/enterprise-integration-patterns) ·
[API management best practices — developer portal, versioning, rate limiting](https://api7.ai/blog/api-management-guide-best-practices) ·
[API governance policies and standards](https://api7.ai/learning-center/api-101/api-governance-policies-standards-guide) ·
[API governance across the full lifecycle](https://www.celigo.com/blog/api-governance-best-practices-for-the-full-api-lifecycle/) ·
[OpenAPI deprecation and sunset support](https://github.com/OAI/OpenAPI-Specification/discussions/5193) ·
[Building a cost-effective observability platform with OpenTelemetry — CNCF](https://www.cncf.io/blog/2025/12/16/how-to-build-a-cost-effective-observability-platform-with-opentelemetry/) ·
Confluent Schema Registry — compatibility modes · Kong Gateway, Keycloak, OpenTelemetry documentation

---

*Module M28 · Category K · 1000FiX ERP System v2.0 · CONFIDENTIAL*
