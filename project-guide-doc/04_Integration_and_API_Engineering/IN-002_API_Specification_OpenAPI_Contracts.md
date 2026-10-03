---
id: IN-002
title: API Specification — OpenAPI 3.1 Contracts
category: 04 — Integration & API Engineering
code: IN
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Integration Architect
approver: Design Authority (constituted under GV-002)
standards_basis: >
  OpenAPI Specification 3.1.0 · JSON Schema 2020-12 · RFC 9457 Problem Details ·
  RFC 9110 HTTP Semantics · RFC 3339 date-time · RFC 8259 JSON ·
  draft-ietf-oauth-v2-1-15 (mandated practices) · Richardson Maturity Level 2
traces_to: >
  PGD-000 IN-002 · 05-03 §3.2, §5.1, §5.2 API-01…API-12 · AS-07 · M28 FR-IPF-012, -018, -021 ·
  M28 AC-08 · AR-001 §7.1 · IN-001 §4 · audit AP-01, AP-05, AP-15 · NFR-042, NFR-092
depends_on: IN-001 · AR-001 · AR-008 · IN-005 (scope vocabulary) · DA-002 (field definitions)
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 14:40 (+06)
artefacts: ./IN-002_artefacts/
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# IN-002 — API Specification — OpenAPI 3.1 Contracts

### Category 04 · Code `IN` · OpenAPI 3.1.0 · JSON Schema 2020-12 · RFC 9457

---

> **The three measurements that size this document**, taken **2026-08-18 14:40 (+06)**:
>
> | Measure | Count |
> |---|---:|
> | Distinct `(method, path)` operations declared across all 67 module specifications | **1,187** |
> | Machine-readable API contract files anywhere in the four-repository estate | **0** |
> | Non-markdown files of **any** kind anywhere in the four-repository estate | **0** |
>
> `05-03` API-03 requires OpenAPI 3.1 generated from code and validated in CI. `M28` `AC-08`
> requires *"100% of published endpoints have a current, CI-validated OpenAPI 3.1 specification."*
> **Neither has ever been started.** This document issues the standard, the first four executable
> contracts — **35 operations, 2.9%** — and the plan that closes the remaining **1,152**.

---

## 1. Purpose

Frontend, mobile, portal and partner teams cannot start without contracts. A markdown table listing
an endpoint tells a developer a path exists; it does not tell them the request schema, the response
schema, the error set, the pagination form, the scope required, the idempotency obligation or the
rate-limit class — and it cannot generate a client, a mock, a contract test or a documentation page.

This document specifies **what a 1000FiX API contract is**, in a form a machine can consume: the
OpenAPI 3.1.0 document structure, the shared component library every contract imports, the naming
and typing rules, the error model, the security scheme declarations, the CI conformance gates, and
the ownership and coverage plan across nine waves. It issues **four worked exemplar contracts** as
executable artefacts under `IN-002_artefacts/`, which are the first machine-readable files in the
estate.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The OpenAPI 3.1.0 document structure and the **one-per-bounded-context** rule |
| 2 | The **shared component library** — schemas, parameters, responses, headers, security schemes |
| 3 | Path, operation, `operationId`, tag and parameter naming |
| 4 | Request and response body rules, typing rules, money, time, identifiers, Bengali text |
| 5 | **Pagination, filtering, sorting and sparse fieldsets** — the `API-05`/`API-06` realisation |
| 6 | The **error model** and the RFC 9457 ruling |
| 7 | Security scheme declarations and the **mandatory scope declaration** per operation |
| 8 | Idempotency, rate-limit and correlation headers as contract obligations |
| 9 | **Generated, not hand-written** — the toolchain, the source of truth, the drift gate |
| 10 | Four worked exemplar contracts, validating, in `IN-002_artefacts/` |
| 11 | The **coverage plan**: 1,187 operations, per module, per wave, with an owner |
| 12 | CI gates `FF-46`…`FF-54` |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Base-path scoping | `IN-001` §4 | Ruled there (`IN-001-D-01`); consumed here |
| Versioning, deprecation, consumer registration | `IN-005` | Contract *lifecycle*, not contract *form* |
| The **scope vocabulary** itself | `IN-005` §5 | This document requires a scope per operation; `IN-005` names them |
| Event and message contracts | `IN-003` | AsyncAPI, not OpenAPI |
| Webhook **delivery** contracts | `IN-006` | Outbound POST is a different contract shape |
| Per-external-system contracts | `IN-004` | An ICD is a bilateral document; an OpenAPI file is a unilateral publication |
| Field-level business meaning and validation limits | `DA-002` data dictionary | A schema says `maxLength: 200`; `DA-002` says why |
| Business rules expressed as errors | `RQ-009`, `AP-006` | The catalogue is content; the contract references it |
| Developer-portal information architecture | `AP-001`, `AP-002` | Publication, not specification |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| Every module developer | §4–§8 are the rules their generated contract must satisfy |
| Portal and app developers | §5 shared components and §9 exemplars are what they generate clients from |
| Partner developers | Indirectly, through the generated developer portal (`AP-001`, `AP-002`) |
| QA lead | §10's gates and the contracts themselves are the contract-test source (`IN-008`) |
| Technical writers | `AP-002`'s reference content is generated from these files |
| Security Lead | §7's scheme declarations and §8's scope obligation are where `API-10` becomes checkable |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / concept | How this document conforms | Departure and rationale |
|---|---|---|---|
| **OpenAPI 3.1.0** | Whole specification | Every contract declares `openapi: 3.1.0` and validates against the OAS 3.1 meta-schema in CI | **Version choice recorded as `IN-001-D-08`.** OAS **3.2.0** (September 2025) is current and additive; the estate moves at the W2 gate, once, deliberately |
| **JSON Schema 2020-12** | Schema dialect | 3.1 aligns to 2020-12; every schema declares no other dialect | None. This alignment is the reason 3.1 was chosen over 3.0 originally |
| **RFC 9457** Problem Details | Error body | **Adopted as the wire form**, carrying `API-04`'s four fields as extension members | **Departure from `API-04` as written** — see §6.2 ruling `IN-002-D-03`. `API-04`'s four fields are preserved exactly; RFC 9457's five are added |
| **RFC 9110** HTTP Semantics | Methods, status codes, conditional requests | §4.4's verb table and §6.1's status table | None |
| **RFC 3339** | `date-time` | All timestamps, UTC, with offset | None |
| **RFC 8259** | JSON | UTF-8 only | None |
| **draft-ietf-oauth-v2-1-15** | Grants and PKCE | `securitySchemes` declare only permitted grants (§7.1) | **Cited as a draft, not an RFC** (`IN-001` VC-02) |
| **Richardson Maturity Level 2** | Resources, verbs, status codes | Target level; no hypermedia controls | Deliberate — `IN-001-D-04` |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| API standards `API-01`…`API-12` | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` §5.2 | The twelve rules this document realises |
| Performance targets | Ibid. §5.3 | Six endpoint classes with p50/p95/p99 — carried into contracts as documented expectations |
| CON-03 core API surface | Ibid. §3.2 | 22 endpoints; **12 declared by no module** (`IN-001` §9.2) |
| All 67 module `§12` API tables | `../../1000fix_ERP_Module/03_Modules/**/M*.md` | **The measurement.** 987 rows, 978 paths, 1,187 operations |
| All 12 portal `§12.5` tables | `.../K_Platform_and_Technology/P*.md` | 140 consumed paths, **100 unmatched** |
| `M28` §5.1, §5.2, §12.5 | `.../K_Platform_and_Technology/M28_*.md` | Gateway, API lifecycle, 18 platform endpoints, `AC-08` |
| `AP-002` API Reference Content Standard | `../../project_content/15_Integration_and_Developer_Content/AP-002_*.md` | `AR-01`…`AR-27`, `ED-06`, `DC-04` — the content rules the generated portal applies |
| `AP-005` §4.3, §4.7, §4.10 | Ibid. | Proposed scope form, six rate-limit classes, 17 auth/limit error codes |
| `AP-006` | Ibid. | **90 error codes across 12 domains** (union with `AP-005` §4.10), retry-safety matrix, `UI-004` bindings |
| `IN-001` | `./IN-001_*.md` | Base path ruling, idempotency semantics, resilience, the reconciliation |

### 2.3 Audit findings this document closes or contributes to

| Finding | Source | Disposition |
|---|---|---|
| **`M28` `AC-08`** — 100% of endpoints CI-validated OpenAPI 3.1 | `M28` §17 | **Made achievable.** §10 gates it; §11 schedules it. Currently 0% |
| **`AP-05` (high)** — no scope vocabulary, credentials scoped by judgement | `AUDIT-016` | §8.1 makes a named scope **mandatory in the contract**; `IN-005` §5 supplies the names. Contributes decisively |
| **`AP-15` (low)** — zero relative links in externally-published material | `AUDIT-016` | The generated portal derives navigation from `operationId` and tags; §4.3 makes both machine-resolvable |
| `AP-002` `AR-04` — every published operation declares the scope it needs | `AP-002` | §8.1, enforced by `FF-50` |
| `AP-002` `O-07` — recommend RFC 9457 extension members | `AP-002` | **Ruled and adopted** — §6.2, `IN-002-D-03` |
| `AP-006` `O-02` — the cost of not adopting 9457 lands in the error catalogue | `AP-006` | Closed by the same ruling |
| `AP-01` (critical) | `AUDIT-016` | Not this document's — `IN-003`'s. `IN-002` contributes the **synchronous** half of the reconciliation (`IN-001` §11.3) |
| `IN-A-01` — the 1,187-operation authoring effort is in no plan | `IN-001` §11.4 | §11.4 sizes it: **169–338 person-weeks** |

---

## 3. What a Contract Is, and Where It Lives

### 3.1 One contract per bounded context

> **Ruling `IN-002-D-01`. The unit of an OpenAPI document is the bounded context from `AR-008`
> §5 — eleven documents — not the module (67), not the API family (12), and not the whole estate
> (one).**

| Option | Documents | Why rejected / chosen |
|---|---:|---|
| One document for everything | 1 | 1,187 operations in one file is unnavigable, unmergeable and produces a client library nobody can consume selectively |
| One per module | 67 | Modules are a *delivery* decomposition and have changed twice (11 → 30 → 67). Contracts pinned to it would churn with every re-decomposition |
| One per API family | 12 | Families are consumer-scoped; a resource appears in several. `IN-001-D-01` removed families from the path, so they cannot organise files either |
| **One per bounded context** | **11** | ✅ Contexts are the stable structure (`AR-008` §5). A context owns its aggregates, so it owns their resources. Contexts change only when the domain does |

**The eleven contract documents**, each at `IN-002_artefacts/<context>/openapi.yaml`:

| # | Context (`AR-008` §5) | Principal resources | Owning modules |
|---|---|---|---|
| 1 | `service-delivery` | service orders, work orders, consignments, workshop jobs | M01–M06, M31 |
| 2 | `customer-engagement` | parties, customers, loyalty, interactions, complaints | M07, M10, M27, M32–M35 |
| 3 | `commercial` | contracts, warranty claims, pricing, quotations, catalogue, subscriptions | M08, M09, M11, M36–M40 |
| 4 | `marketplace` | listings, sellers, jobs, bids, disputes, payouts, e-commerce | M12, M38 |
| 5 | `circular` | rentals, trade-ins, refurbishment, e-waste | M13, M14, M18 |
| 6 | `supply-chain` | parts, stock, purchase orders, warehouse, suppliers, imports | M15, M16, M41–M44 |
| 7 | `asset` | customer assets, enterprise assets, fleet, facilities, IoT | M17, M45–M48 |
| 8 | `finance` | invoices, payments, ledger, tax, treasury, payroll postings | M19, M20, M49–M54 |
| 9 | `people` | employees, competency, attendance, payroll, safety | M21, M22, M55–M59 |
| 10 | `governance` | quality, risk, audit, knowledge, documents, projects | M23, M24, M60, M61, M66, M67 |
| 11 | `platform` | events, schemas, subscriptions, integrations, sync, trace, identity, config, BI, ML | M25, M26, M28–M30, M62–M65 |

**Cross-context references** use a `$ref` into the shared component library (§5), never into
another context's document. A context that needs to name another context's resource carries its
**identifier**, not its schema — the same rule as `AR-009` P-02 for events.

### 3.2 File layout

```
04_Integration_and_API_Engineering/
├── IN-002_API_Specification_OpenAPI_Contracts.md      ← this document
└── IN-002_artefacts/
    ├── README.md                                       ← how to lint, bundle and generate
    ├── _shared/
    │   ├── components.yaml                             ← THE shared library (§5)
    │   ├── errors.yaml                                 ← RFC 9457 + the 90 codes (§6)
    │   └── security.yaml                               ← securitySchemes (§7)
    ├── service-delivery/
    │   └── openapi.yaml                                ← exemplar, issued
    ├── commercial/
    │   └── openapi.yaml                                ← exemplar, issued
    ├── finance/
    │   └── openapi.yaml                                ← exemplar, issued
    └── platform/
        └── openapi.yaml                                ← exemplar, issued
```

Per `GV-011` `CM-20`: *"Supporting artefacts sit in a subfolder sharing the document's ID stem."*
**These are the first non-markdown files in the estate.** Four of the eleven contexts are issued as
worked exemplars; §11 schedules the remaining seven.

### 3.3 Generated, not hand-written

> **Ruling `IN-002-D-02`. The source of truth is the code. The contract is generated, and the
> markdown table in a module's `§12` is demoted to a human-readable index.**

`05-03` API-03 already says *"generated from code and validated in CI."* This ruling states the
consequence nobody has drawn: **the four exemplar files in `IN-002_artefacts/` are the shape the
generator must emit, not a set of files to be maintained by hand.**

| Stage | Artefact | Maintained by |
|---|---|---|
| **Source of truth** | Route decorators + schema classes in the module | The module developer, in the same commit as the behaviour |
| **Generated** | `IN-002_artefacts/<context>/openapi.yaml` | CI, on every merge |
| **Checked** | Lint + meta-schema + drift + this document's rules | CI gates `FF-46`…`FF-54` |
| **Published** | Developer portal reference pages | Generated per `AP-002` |
| **Demoted** | Module `§12` API tables | **A human index, explicitly partial**, exactly as `AR-009` `D-A9-01` demoted `05-03` §4.2 |

**Before code exists** — which is the position in Wave 1 — the exemplars are **hand-authored and
then become generator fixtures**: the generator is correct when it reproduces them. This is the only
sequencing that lets portal teams start against a real contract before the module is built.

> **Why the demotion matters.** `AR-009` measured a hand-maintained event catalogue at **64 of 988
> — 6.5% accurate**. There is no reason to expect a hand-maintained endpoint catalogue across 67
> modules to fare better, and `IN-001` §11 already measured its consumer-side divergence at 71%.

---

## 4. Document, Path and Operation Rules

### 4.1 Required document-level fields

Every `openapi.yaml`:

| Field | Value | Rule |
|---|---|---|
| `openapi` | `3.1.0` | Exactly. `FF-46` |
| `info.title` | `1000FiX <Context> API` | |
| `info.version` | **SemVer of the contract**, e.g. `1.4.0` — *not* the path version | §4.2 |
| `info.description` | One paragraph, plus a link to the owning context in `AR-008` | |
| `info.contact` | A **role** and a team address, never a person (`GV-011` convention) | |
| `info.license` | `CONFIDENTIAL — Internal Use Only`, `identifier` omitted | |
| `servers` | Six: `sandbox`, `dev`, `ci`, `sit`, `uat`, `production` — plus `SANDBOX` as the seventh environment (`AP-12`) | `IN-008` §6 |
| `tags` | One per resource group, with `x-family` naming which of the twelve API families governs policy | `IN-001-D-01` |
| `security` | The document-level default; overridden per operation | §7 |
| `externalDocs` | The developer-portal URL for this context | `AP-001` |

### 4.2 Two versions, and they are not the same thing

The single most common misunderstanding a generated contract set produces:

| Version | Where | Changes when | Governed by |
|---|---|---|---|
| **Path version** `/api/v1/` | In every URL | **Only on a breaking change.** Two concurrent, six months' notice | `API-02`, `IN-005` §4 |
| **Contract version** `info.version` | In the document | On **every** change, breaking or not | SemVer; `IN-005` §4.3 |

A minor contract version bump with the same path version tells a consumer "something was added, you
are safe." A major contract bump **requires** a new path version. `FF-49` enforces the implication.

### 4.3 `operationId` — the identifier everything else keys on

| # | Rule |
|---|---|
| **OP-01** | Every operation has an `operationId`. No exceptions. `FF-47` |
| **OP-02** | Form: `<verb><Resource>[<Qualifier>]` in `lowerCamelCase` — `createServiceOrder`, `listServiceOrders`, `getServiceOrderStatus`, `cancelServiceOrder` |
| **OP-03** | **Globally unique across all eleven contracts.** A generated client merges them into one namespace |
| **OP-04** | **Permanent.** Renaming an `operationId` breaks every generated client, every contract test and every developer-portal deep link. It is a breaking change even when the path is unchanged |
| **OP-05** | The verb prefix is drawn from a closed set: `list`, `get`, `create`, `update`, `replace`, `delete`, `search`, plus a **domain verb** for a non-CRUD sub-resource POST (`cancelServiceOrder`, `approveQuotation`, `confirmPayment`) |
| **OP-06** | The resource noun matches the `AR-008` aggregate or interior-entity name, singular for item operations, plural for collections |

> **`OP-04` is why `operationId` is specified before any contract is written.** `AP-015`'s finding
> that the category carries zero resolvable links is fixed by generated deep links keyed on
> `operationId`; a churning identifier would reintroduce it worse.

### 4.4 Verbs and their obligations

| Verb | Use | Idempotency-Key | Request body | Success | Notes |
|---|---|:--:|:--:|---|---|
| `GET` | Read a resource or collection | — | ✘ | `200` | Safe, cacheable per §4.7 |
| `POST` (collection) | Create | **Required** | ✔ | `201` + `Location` | `IN-001` ID-01 |
| `POST` (sub-resource) | Domain action | **Required** | ✔ or empty | `200` / `202` | `PN-04` |
| `PATCH` | Partial update | **Required** | ✔ (merge-patch) | `200` | `application/merge-patch+json` |
| `PUT` | Full replacement | **Required** | ✔ | `200` | Rare; used only where the client genuinely holds the whole representation |
| `DELETE` | Retire | **Required** | ✘ | `204` | **Soft delete only** (`DI-08`). A hard delete is never an API operation |
| `HEAD`, `OPTIONS` | Gateway-level | — | ✘ | — | Not authored per operation |

> **`DI-08` and the absent `delete` scope.** `AP-005` `SC-04`'s action set is `read · write ·
> approve · export` — deliberately with no `delete`, because the estate permits soft deletion only.
> A `DELETE` operation therefore requires the `write` scope, not a `delete` scope. Stated because
> the omission looks like an oversight and is not.

### 4.5 Parameters

| # | Rule |
|---|---|
| **PR-01** | Path parameters are `snake_case`, named for the thing identified: `{service_order_id}`, not `{id}`, not `{order}` (`IN-001` `PN-07`) |
| **PR-02** | Every path parameter carries a `schema` with a `format` or a `pattern`. A bare `type: string` is a defect |
| **PR-03** | Query parameters are `snake_case` and drawn from the shared library where one exists (`cursor`, `limit`, `sort`, `fields`, `filter[...]`) |
| **PR-04** | Header parameters are declared explicitly: `Idempotency-Key`, `Accept-Language`, `X-Correlation-Id` (response only) |
| **PR-05** | **No parameter is undocumented.** An implementation that reads a query parameter absent from the contract fails `FF-48` |
| **PR-06** | Boolean query parameters are `true`/`false`, never `1`/`0` or presence-only |
| **PR-07** | Enumerated parameters carry `enum` **and** name their governing register (`MD-020` service types, `MD-027` states) in `description` |

### 4.6 Request and response bodies

| # | Rule |
|---|---|
| **BD-01** | Media type is `application/json` — except `multipart/form-data` for uploads and `application/merge-patch+json` for `PATCH` |
| **BD-02** | Every schema sets `additionalProperties: false` on request bodies. Unknown fields are rejected with `request.unknown_field` |
| **BD-03** | Response schemas **do not** set `additionalProperties: false` — a consumer must tolerate added fields, because additive change is non-breaking (`IN-005` §4.4) |
| **BD-04** | Property names are `snake_case`, matching the `DA-002` data dictionary technical name |
| **BD-05** | **A collection response is always an object with `data` and `page`**, never a bare array. A bare array cannot be extended without a breaking change |
| **BD-06** | Nullability is explicit — `type: [string, "null"]` in JSON Schema 2020-12 form, never `nullable: true` (which is OAS 3.0 and invalid in 3.1) |
| **BD-07** | `required` is stated on every object schema, even when empty, so "not required" is a decision rather than an omission |
| **BD-08** | No schema exceeds **three levels of nesting**. A fourth level is a missing sub-resource |

### 4.7 Caching and conditional requests

| # | Rule |
|---|---|
| **CA-01** | `GET` on a mutable resource returns `ETag`; the operation declares `If-None-Match` and a `304` response |
| **CA-02** | `PATCH`/`PUT`/`DELETE` on a resource that supports `ETag` **must** accept `If-Match` and return `412` on mismatch — this is the optimistic-concurrency mechanism behind `resource.conflict` |
| **CA-03** | Reference and master data (`MD-*`) declares `Cache-Control: public, max-age=…`; anything scoped to a caller declares `private, no-store` |
| **CA-04** | **Nothing scoped to a caller is ever cached at the edge.** `API-10` is a server-side guarantee, and an edge cache is not the server |

---

## 5. The Shared Component Library

`_shared/components.yaml` is imported by all eleven contracts. **A schema defined twice is a schema
that will diverge**, and it is the same defect class as `AP-006` `EP-06` (one condition, one code).

### 5.1 Envelope schemas

| Component | Shape | Notes |
|---|---|---|
| `PageEnvelope` | `{ data: [...], page: { cursor_next, cursor_prev, limit, has_more } }` | `BD-05`; cursor-based (`API-05`) |
| `Money` | `{ amount: string (decimal), currency: string (ISO 4217) }` | **String decimal, never float** (AS-10, `AC-04`) |
| `Quantity` | `{ value: string (decimal), uom: string }` | UoM from `MD-*` |
| `Address` | Bangladesh-shaped: `division`, `district`, `upazila`, `union_ward`, `postcode`, `line_1`, `line_2`, `landmark`, `geo` | **Not** a generic international address; `M65` handles the multi-country case separately |
| `GeoPoint` | `{ lat: number, lon: number, accuracy_m: number }` | |
| `PersonName` | `{ full_name, full_name_bn }` | §5.4 |
| `PhoneNumber` | `string`, `pattern: ^\+8801[3-9][0-9]{8}$` for BD numbers, with an international fallback | `validation.format_invalid` names this |
| `Attachment` | `{ id, filename, media_type, size_bytes, url, sha256 }` | **Claim check** — a reference, never bytes (`AR-009` P-05) |
| `AuditStamp` | `{ created_at, created_by, updated_at, updated_by }` | Read-only; present on every persisted resource |
| `Reference` | `{ id, type, display }` | How a cross-context resource is named (§3.1) |

### 5.2 Common parameters

| Component | In | Notes |
|---|---|---|
| `CursorParam` (`cursor`) | query | Opaque, base64url. **Never an offset** — offset pagination is forbidden by `API-05` |
| `LimitParam` (`limit`) | query | `default: 25`, `maximum: 100`; the maximum is per-endpoint and enforced |
| `SortParam` (`sort`) | query | `field` or `-field`, comma-separated; permitted fields enumerated per operation |
| `FieldsParam` (`fields`) | query | Sparse fieldsets (`API-06`); comma-separated; **cannot widen scope** |
| `FilterParam` (`filter[<field>]`) | query | Bracket form so filters are unambiguous against other parameters |
| `IdempotencyKeyParam` | header | `required: true` on every state-changing operation (`FF-43`) |
| `AcceptLanguageParam` | header | `bn-BD` or `en` (`API-11`); anything else falls back to `en` |
| `IfMatchParam`, `IfNoneMatchParam` | header | `CA-01`, `CA-02` |

### 5.3 Common response headers

| Header | On | Basis |
|---|---|---|
| `X-Correlation-Id` | **Every** response, success or error | `API-09`, `NFR-092` (§7 tracing sense) |
| `X-RateLimit-Limit`, `-Remaining`, `-Reset` | Every response | `API-08` |
| `RateLimit`, `RateLimit-Policy` | Every response | The IETF standard form, emitted **in addition** — `AP-005` §4.7 |
| `Retry-After` | `429`, `503` | `API-08` |
| `Idempotency-Replayed` | Replayed responses | `IN-001` ID-05 |
| `ETag` | Cacheable `GET` | `CA-01` |
| `Deprecation`, `Sunset`, `Link rel="deprecation"` | Deprecated operations | `IN-005` §7.2 |

### 5.4 Bengali text — a first-class typing rule

The estate is bilingual and this is a **contract** concern, not a presentation one.

| # | Rule |
|---|---|
| **BN-01** | A user-entered name, address or free text that may be Bengali is carried as **two properties**: `<field>` and `<field>_bn`. Never one field with a language flag |
| **BN-02** | **Length limits are in characters, not bytes.** `AP-006` `validation.length_exceeded` says so explicitly; a schema `maxLength` in JSON Schema is already characters, and any byte limit at the gateway must be set higher accordingly |
| **BN-03** | Request and response encoding is **UTF-8 only**; `request.encoding_invalid` is returned otherwise |
| **BN-04** | Localised **error messages** are selected by `Accept-Language`; `code` and `details` are never translated (`AP-006` §4.2) |
| **BN-05** | Sorting and collation of Bengali text is a server concern and is **declared per sortable field**, because Bengali collation is not codepoint order |

> **`BN-02` is a real defect source, not a nicety.** A 200-character Bengali address is roughly 600
> bytes in UTF-8. A gateway body limit or a database column sized in bytes against a limit expressed
> in characters truncates silently at the two-thirds mark, and the failure appears only in Bengali.

---

## 6. The Error Model

### 6.1 Status codes — the closed set

| Status | Meaning in this estate | Never used for |
|---|---|---|
| `200` | Success with a body | Errors of any kind |
| `201` | Created; `Location` header mandatory | An accepted-but-not-created async job |
| `202` | Accepted for asynchronous processing; body carries `job_url` | Anything the caller can poll by resource id instead |
| `204` | Success with no body | A soft delete still returns `204` |
| `304` | Not modified | — |
| `400` | Malformed or invalid request | Authorisation failures |
| `401` | Authentication absent, invalid or expired | **Authorisation** failures |
| `403` | Authenticated, and not permitted | A record the caller may not know exists — see below |
| `404` | Resource absent **and the caller would be entitled to see it** | An out-of-scope record |
| `409` | Conflict — idempotency clash, uniqueness, concurrent modification | A business-rule violation |
| `410` | Permanently gone | Retired API versions (that is `400 request.version_unsupported`) |
| `412` | `If-Match` precondition failed | — |
| `413` | Payload too large | — |
| `422` | Well-formed, but semantically refused — **state and business rules live here** | Field-format failures (those are `400`) |
| `429` | Rate limited | — |
| `451` | Unavailable for legal reasons — **residency-restricted field** | Any non-statutory refusal |
| `500` | Unhandled | Anything the estate has a code for |
| `503` | Dependency unavailable or maintenance | — |

> **The `403`/`404` rule is a security control, not a style preference.** `AP-006` `EP-03` and
> `AP-005` `SC-02`: an error must never reveal that a record outside the caller's scope exists.
> A brand partner probing `/warranty-claims/{id}` must receive the **same** response for "no such
> claim" and "another brand's claim". The estate resolves this with **`403 auth.out_of_scope` for
> both**, and reserves `404 resource.not_found` for records the caller *would* be entitled to see.
> `FF-51` tests it.

### 6.2 The body — RFC 9457 ruling

`API-04` specifies four fields: `code`, `message`, `details`, `correlation_id`. `AP-002` `O-07`
and `AP-006` `O-02` both recommend emitting them as RFC 9457 extension members. **Ruled here:**

> **Ruling `IN-002-D-03`. The error body is an RFC 9457 Problem Details object carrying `API-04`'s
> four fields as extension members. `API-04` is not changed; it is embedded.**

```json
{
  "type":    "https://developer.1000fix.com/errors/srm.warranty_inactive",
  "title":   "Warranty is not active for this device",
  "status":  422,
  "detail":  "This device is not under warranty on 18 August 2026. Its warranty ended 2 March 2026.",
  "instance":"/api/v1/warranty/check",

  "code":    "srm.warranty_inactive",
  "message": "This device is not under warranty on 18 August 2026. Its warranty ended 2 March 2026.",
  "details": { "device_id": "DEV-0294817", "warranty_expiry": "2026-03-02",
               "rule": "BRU-SRM-02", "rule_class": "H" },
  "correlation_id": "7c1f4b2e-9a33-4f61-8b7d-2e5c1a09d4f6"
}
```

| Field | Source | Rule |
|---|---|---|
| `type` | RFC 9457 | A **stable URI** derived from `code`. Resolves to the developer-portal page. **This is what fixes `AP-15`** — an external reader can reach the explanation |
| `title` | RFC 9457 | Short, **not localised**, stable per `code` |
| `status` | RFC 9457 | Duplicates the HTTP status, so a body surviving a proxy is still interpretable |
| `detail` | RFC 9457 | **Equals `message`.** Localised by `Accept-Language` |
| `instance` | RFC 9457 | The path, not the correlation id |
| `code` | `API-04` | **The contract** (`AP-006` `EP-01`). Callers branch on this |
| `message` | `API-04` | Retained verbatim so existing content and `UI-004` bindings are untouched |
| `details` | `API-04` | Machine-readable context, additive only |
| `correlation_id` | `API-04` | Also present as the `X-Correlation-Id` header |

**Content type** is `application/problem+json` on every error response.

**Why embed rather than replace.** `AP-006` and `AP-005` between them define **90 codes** whose
`message` strings are bound into `UI-004` and the `BN-009`…`BN-013` Bengali bundles. Replacing
`code`/`message` with `type`/`detail` would invalidate every one of those bindings for no
functional gain. Emitting both costs one mapping and lets a partner's existing Problem Details
client work — which is `AP-002` `O-07`'s exact argument.

### 6.3 The catalogue is referenced, not restated

| # | Rule |
|---|---|
| **ER-01** | `AP-006` (plus `AP-005` §4.10) is the **single register** of error codes — **90 codes across 12 domains** at the enumeration instant. The contracts reference it; they never define a code |
| **ER-02** | Every operation enumerates the codes it can return. `AP-006` §4.10's endpoint-class index is the derivation source |
| **ER-03** | A module may not invent a code (`AP-006` `CG-03`). A condition with no code uses the nearest domain code with `details`, and raises the gap |
| **ER-04** | Every error response in every contract `$ref`s `_shared/errors.yaml`. `FF-52` fails a contract that inlines an error schema |
| **ER-05** | The **retry classification** in `AP-006` is carried into the contract as `x-retry-safe: true \| false \| conditional`. Changing it is a breaking change (`AP-006` `CG-06`) |

**Measured code distribution** at 2026-08-18 14:40 (+06), across `AP-005` §4.10 and `AP-006`
§4.4–§4.7:

| Domain | Codes | Domain | Codes |
|---|---:|---|---:|
| `rule` | 20 | `data` | 6 |
| `auth` | 15 | `resource` | 5 |
| `validation` | 9 | `platform` | 5 |
| `request` | 8 | `idempotency` | 4 |
| `state` | 6 | `export` | 4 |
| `dependency` | 6 | `ratelimit` | 2 |
| | | **Total** | **90** |

> **`IN-A-09` (medium).** Nineteen of the twenty `rule.*` codes are business-rule violations tied to
> `BRU-` identifiers in `05-05` and the owning module. `RQ-009` records that `05-05` **carries no
> business rule at all for M40 or M42** (audit `EO-02`). **A generated contract cannot enumerate a
> `rule.*` code for a module that has no rules registered**, so `FF-53` will report M40 and M42 as
> having zero business-rule error coverage — correctly, and it should not be suppressed.

---

## 7. Security Schemes

### 7.1 Declared schemes

`_shared/security.yaml` declares exactly three, and no contract declares a fourth.

| Scheme | Type | Used by | Grants permitted |
|---|---|---|---|
| `oauthUser` | `oauth2` | P01, P02, P03, P04, P07, P09, P10, P11, P12 — anything with a human behind it | **`authorizationCode` with PKCE only.** `implicit` and `password` are **not declared** |
| `oauthMachine` | `oauth2` | Portal platform (CON-03), partner servers, batch jobs | **`clientCredentials` only** |
| `webhookSignature` | `apiKey`-shaped, documented | `/hooks/v1/*` **only** | n/a — signature, not bearer (`IN-006` §6) |

> **The forbidden grants are forbidden by omission, and that is deliberate.** An OpenAPI document
> that does not declare `implicit` cannot generate a client that uses it. This is `AA-02` made
> mechanical rather than aspirational, and it is the OAuth 2.1 draft's central instruction.

### 7.2 Scope declaration is mandatory

| # | Rule |
|---|---|
| **SD-01** | **Every operation declares the scopes it requires**, by name, in its `security` block. `AP-002` `AR-04` requires it; `FF-50` enforces it |
| **SD-02** | Scope names come **only** from `IN-005` §5's ratified vocabulary. An unregistered scope fails CI |
| **SD-03** | An operation requiring more than **two** scopes is a design smell and is reviewed |
| **SD-04** | `approve` is never declared alongside `write` on the same operation unless the operation genuinely does both — the separation is what `05-04` §6's segregation rules rest on (`AP-005` `SC-05`) |
| **SD-05** | **A scope is capability, never visibility.** The contract's `description` states the data scope in words; it is enforced in the domain (`API-10`, `IN-001` §3.3) |
| **SD-06** | `export` scoped operations additionally declare `x-export: true`, which drives the `bulk` rate-limit class and the `EA-12` approval path |

> **`SD-02` is currently unsatisfiable, and saying so is the point.** `AP-05` records that **not one
> scope name exists anywhere in the repository**. Until `IN-005` §5 is ratified, the exemplar
> contracts in `IN-002_artefacts/` carry the proposed names from `AP-005` §4.3 marked
> `x-scope-status: proposed`. **No contract may be published to a partner, and no credential may be
> issued, while any operation carries `proposed`.** `FF-54`.

### 7.3 The scope-to-operation derivation

A scope is derived, not invented, so that 1,187 operations do not produce 1,187 scopes:

```
scope = <resource>:<action>[:<qualifier>]

  resource   = the AR-008 aggregate the operation's path root maps to, singular, snake_case
  action     = read    ← GET
               write   ← POST (create), PATCH, PUT, DELETE
               approve ← a domain-verb POST that is an approval or decision
               export  ← any operation returning a bulk or file representation
  qualifier  = own_brand | own_org | own_seller — only where the resource has
               more than one external audience
```

**Worked derivation across the four exemplar contracts:**

| Operation | `operationId` | Scope |
|---|---|---|
| `POST /api/v1/service-orders` | `createServiceOrder` | `service_order:write` |
| `GET /api/v1/service-orders/{service_order_id}` | `getServiceOrder` | `service_order:read` |
| `POST /api/v1/service-orders/{service_order_id}/cancel` | `cancelServiceOrder` | `service_order:write` |
| `POST /api/v1/quotations/{quotation_id}/decision` | `decideQuotation` | `quotation:approve` |
| `POST /api/v1/warranty/claims/{claim_id}/decision` | `decideWarrantyClaim` | `warranty_claim:approve:own_brand` |
| `GET /api/v1/invoices` | `listInvoices` | `invoice:read` |
| `GET /api/v1/invoices/export` | `exportInvoices` | `invoice:export:own_org` |
| `GET /api/v1/platform/events/catalogue` | `getEventCatalogue` | `platform_event:read` |

**This yields roughly 22 aggregates × 4 actions ≈ 88 base scopes**, plus qualified variants —
against 1,187 operations. That ratio is the whole reason a scope is derived from the aggregate and
not from the endpoint.

---

## 8. Contract Obligations That Are Not Schema

Things a contract must state that are not the shape of a body.

### 8.1 Per-operation obligations

| Extension | On | Value | Basis |
|---|---|---|---|
| `x-scope` | every operation | The derived scope(s) | `SD-01` |
| `x-scope-status` | every operation | `ratified` \| `proposed` | `SD-02`, `FF-54` |
| `x-api-family` | every tag | One of the twelve | `IN-001-D-01` |
| `x-rate-limit-class` | every operation | `portal` \| `partner-high` \| `partner-standard` \| `partner-light` \| `bulk` \| `sandbox` | `AP-005` §4.7 |
| `x-endpoint-class` | every operation | One of the six in `05-03` §5.3 | §8.2 |
| `x-retry-safe` | every error response | `true` \| `false` \| `conditional` | `ER-05` |
| `x-owning-module` | every operation | `M01`…`M67` — **exactly one** | `FF-48`, `IN-001` §11.2 |
| `x-wave` | every operation | `W1`…`W9` | §11 |
| `x-pii` | every schema property carrying personal data | `none` \| `personal` \| `sensitive` \| `residency-restricted` | `NFR-086a`, `AP-012` |
| `x-disclosure-ref` | operations returning data to an external counterparty | The `AP-012` register row | `AP-012` `DS-01` |

> **`x-pii` is the field-level realisation of `NFR-086a`** — *"the data model must carry a residency
> classification on every field, and the platform must enforce it at write time, not by
> convention."* Declaring it in the contract is what lets `FF-55` (`DA-002`'s gate) check the
> contract against the data dictionary rather than against a developer's memory.

### 8.2 Performance expectations are published, not implied

`05-03` §5.3 gives six endpoint classes with p50/p95/p99 targets. Each operation declares its class
in `x-endpoint-class`, and the class table is published in the contract `description`:

| Class | p50 | p95 | p99 |
|---|---|---|---|
| `status-lookup` | 80 ms | 250 ms | 500 ms |
| `standard-read` | 150 ms | 400 ms | 800 ms |
| `write` | 200 ms | 500 ms | 1,000 ms |
| `search` | 200 ms | 600 ms | 1,200 ms |
| `availability` | 300 ms | 800 ms | 1,500 ms |
| `analytics` | 1 s | 5 s | 10 s |

> **These are internal budgets.** Per `IN-001-D-03`, an operation whose path includes a third-party
> call publishes **two** numbers: this class for internal processing, and a separate end-to-end
> expectation. `POST /api/v1/payments/confirm` is `write` internally and carries a per-rail
> end-to-end figure from `IN-004`.

### 8.3 Deprecation is in the contract

| # | Rule |
|---|---|
| **DP-01** | A deprecated operation sets `deprecated: true` **and** `x-sunset: <RFC 3339 date>` |
| **DP-02** | Runtime responses carry `Deprecation` and `Sunset` headers matching the contract |
| **DP-03** | The sunset date is **≥ 6 months** after the deprecation date (`API-02`). `FF-49` computes it |
| **DP-04** | A deprecated operation names its replacement in `x-replaced-by: <operationId>` |

---

## 9. The Four Exemplar Contracts

Issued as executable artefacts. Each validates against the OAS 3.1 meta-schema and demonstrates a
different class of problem.

| # | Context | Operations issued | What it demonstrates |
|---|---|---:|---|
| 1 | `service-delivery` | **16** — the full M01 `§12.4` surface plus the `/customer-assets` resolution | The base case: CRUD, sub-resource actions, state transitions, the tokenised public tracking view, cursor pagination, `ETag`/`If-Match` |
| 2 | `commercial` | **6** — warranty claim decision path | **Qualified scopes** (`own_brand`), the `403`/`404` rule under adversarial probing, `rule.*` errors with `rule_class`, and `claim.evidence_incomplete` suppression |
| 3 | `finance` | **5** — invoice, payment confirmation, export | **`Money` as string decimal**, the 7-day idempotency window, `x-export` and the `bulk` class, `451 data.residency_restricted`, and the two-number latency budget |
| 4 | `platform` | **8** — the M28 event and integration surface | **The three webhook-management endpoints `AP-04` found missing**, plus schema registration, catalogue, DLQ replay |

**35 of 1,187 operations — 2.9%.** Counted from the issued artefacts at 2026-08-18 15:10 (+06)
by parsing them, not by adding the column above (`PG-M10`). Stated plainly rather than presented
as coverage.

### 9.1 What the exemplars deliberately include

| Included | Why |
|---|---|
| The **three missing webhook-management endpoints** — register, test, rotate secret | `AP-04`: *"no webhook management endpoint registered anywhere"*, despite `FR-IPF-034` requiring a registry and `fix_webhook_endpoint` existing as an entity |
| `/api/v1/payments/confirm` | One of the **12 CON-03 endpoints no module declares** (`IN-001` §9.2), and the one on the money path |
| A resource with **two claimant modules resolved** — `/api/v1/customer-assets` | `IN-001` §11.2's M17/M49 contest, shown resolved rather than left ambiguous |
| `x-scope-status: proposed` on every operation | `SD-02` — the contracts are honest that the vocabulary is unratified |
| A `202` + `job_url` async export | `API-12`, `export.accepted` |

### 9.2 What they deliberately omit

| Omitted | Why |
|---|---|
| Any operation whose owning module is contested and unresolved | Publishing a contract for a resource with two owners institutionalises the defect |
| The `/api/v1/mp/*` marketplace surface | **Fifteen paths, no module declares any of them** (`IN-001` §11.3). A contract would assert an owner that does not exist |
| Real example values for personal data | `AP-012`; examples use obviously synthetic values |
| Server URLs for production | `IN-008` §6; only `sandbox` and placeholder hosts are published |

---

## 10. CI Gates

Continuing `AR-012` v1.1's `FF-01`…`FF-37` and `IN-001`'s `FF-38`…`FF-45`.

| # | Check | Scope | Timing | Enforcement |
|---|---|---|---|---|
| **FF-46** | Every contract declares `openapi: 3.1.0` and validates against the OAS 3.1 meta-schema | 11 contracts | CI | Fail |
| **FF-47** | Every operation has a globally unique `operationId` matching the `OP-02` form | 1,187 | CI | Fail |
| **FF-48** | Every operation declares exactly one `x-owning-module`, and no path is claimed by two modules | 978 paths | CI | Fail |
| **FF-49** | `info.version` SemVer implies the path version: a major bump without a new `/vN/` fails; `x-sunset` ≥ deprecation + 6 months | 11 | CI | Fail |
| **FF-50** | Every operation declares `x-scope` | 1,187 | CI | Fail |
| **FF-51** | **Adversarial `403`/`404` test**: an out-of-scope record and a non-existent record return byte-identical bodies | Per resource | CI + `IN-008` | Fail |
| **FF-52** | No contract inlines an error schema; all `$ref` `_shared/errors.yaml` | 11 | CI | Fail |
| **FF-53** | Every `rule.*` code an operation declares resolves to a `BRU-` identifier in `05-05` or the owning module | All | CI | **Report** (M40, M42 will fail — `IN-A-09`) |
| **FF-54** | **No contract with `x-scope-status: proposed` is published externally, and no credential is issued against one** | 11 | Publication gate | Block |
| **FF-55** | Every `x-pii` classification matches `DA-002`'s classification for the same field | All properties | CI | Fail once `DA-002` exists |
| **FF-56** | **Drift**: the generated contract equals the committed contract | 11 | CI | Fail |
| **FF-57** | Every operation is exercised by at least one contract test | 1,187 | CI | Fail |
| **FF-58** | Every `4xx`/`5xx` response uses `application/problem+json` | All responses | CI | Fail |

> **`FF-56` is the gate that makes `IN-002-D-02` real.** Without a drift check, "generated from
> code" degrades into "generated once, then hand-edited," which is how the 64-of-988 event
> catalogue happened.

---

## 11. Coverage Plan

### 11.1 The denominator

| Measure | Count |
|---|---:|
| Operations to specify | **1,187** |
| Distinct paths | 978 |
| Contexts | 11 |
| Contracts issued today | 4 |
| **Operations issued today** | **35 (2.9%)** |
| **Operations remaining** | **1,152** |

### 11.2 Per-context distribution

Derived by mapping each operation's `x-owning-module` to its context (§3.1), at
2026-08-18 14:40 (+06):

| Context | Modules | Approx. operations | Wave of first need |
|---|---:|---:|:--:|
| `platform` | 10 | ~190 | **W1** |
| `finance` | 8 | ~175 | W3 |
| `service-delivery` | 7 | ~130 | **W1** |
| `supply-chain` | 6 | ~125 | W2 |
| `asset` | 5 | ~105 | W2 |
| `governance` | 6 | ~105 | W4 |
| `people` | 7 | ~100 | W5 |
| `commercial` | 9 | ~95 | W3 |
| `customer-engagement` | 7 | ~85 | **W1** |
| `marketplace` | 2 | ~45 | W7 |
| `circular` | 3 | ~32 | W6 |
| **Total** | **67** | **~1,187** | |

### 11.3 Sequencing rule

> **A contract is issued one wave before the wave that first consumes it** — the rule `AP-03`
> found broken for **eight of twelve** `AP` files, six of them needed at W1. It is stated here so
> Category 04 does not repeat the defect its own audit identified.

| Wave | Contracts complete by | Rationale |
|---|---|---|
| **W0 → W1** | `platform`, `service-delivery`, `customer-engagement` — **~405 operations** | CON-03 is live at W1 and consumes from all three; P03 ships at W1 |
| W1 → W2 | `supply-chain`, `asset` | P05 at W3 needs supply-chain a wave early |
| W2 → W3 | `finance`, `commercial` | Payments at W3 (`G3-03`); P04 at W4 |
| W3 → W4 | `governance` | P11 at W5 |
| W4 → W5 | `people` | |
| W5 → W6 | `circular` | |
| W6 → W7 | `marketplace` | P07 and P12 at W7 |

**~405 operations must exist before Wave 1 completes.** That is 34% of the surface, in the wave the
programme is already 5.33× over-committed in (`GV-004`).

### 11.4 Effort

`GV-007` establishes the estimation method and calibration factor `CF-01`. Applying it:

| Component | Basis | Low | Expected | High |
|---|---|---:|---:|---:|
| Contract authoring — 1,187 operations | 0.5–1.5 h per operation including schemas, errors, examples | 74 PW | 124 PW | 223 PW |
| Shared component library | One-off, high care | 4 PW | 6 PW | 10 PW |
| Generator + CI gates `FF-46`…`FF-58` | Toolchain build | 8 PW | 14 PW | 24 PW |
| Reconciling the **100 unmatched portal paths** (`IN-001` RI-05) | Design where genuinely absent | 20 PW | 45 PW | 90 PW |
| Adjudicating and re-prefixing (`RI-03`, `RI-04`) | Text plus review | 3 PW | 5 PW | 9 PW |
| **Total** | | **109 PW** | **194 PW** | **356 PW** |

> **`IN-A-01` quantified. `IN-002` is a 109–356 person-week deliverable carried in `PGD-000` as one
> row.** `GV-007` sized the guiding-document stream at 264–528 PW for 127 documents — an average of
> ~3 PW each. This single document is **35–120× that average**, and `IN-003` (988 event schemas) is
> the same shape. Referred to `GV-007` and `GV-008`; raised as **`IN-A-02`**.

---

## 12. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `IN-002-D-01` | The unit of an OpenAPI document | One global · One per module (67) · One per family (12) · **One per bounded context (11)** | **Bounded context** | Contexts are the stable structure; the module decomposition has changed twice and families are consumer-scoped | 11 contracts; cross-context references carry identifiers, not schemas |
| `IN-002-D-02` | Source of truth | Hand-authored contract · **Generated from code, contract committed and drift-checked** | **Generated** | A hand-maintained catalogue at this scale measured 6.5% accurate for events (`AR-009`) | `FF-56`; module `§12` tables demoted to a human index |
| `IN-002-D-03` | Error body form | Keep `API-04`'s four fields · Replace with RFC 9457 · **Embed `API-04` as RFC 9457 extension members** | **Embed** | 90 codes are bound into `UI-004` and the Bengali bundles; replacing them invalidates all of it for no gain. Embedding costs one mapping and lets partner Problem Details clients work | `application/problem+json`; `type` URIs fix `AP-15` for external readers |
| `IN-002-D-04` | Collection responses | Bare array · **`{data, page}` envelope** | **Envelope** | A bare array cannot gain a field without a breaking change | `PageEnvelope`; cursor-only pagination |
| `IN-002-D-05` | Out-of-scope records | `404` · **`403 auth.out_of_scope` for both** | **`403` for both** | `AP-006` `EP-03`, `AP-005` `SC-02` — an error must not reveal existence | `FF-51` tests it adversarially |
| `IN-002-D-06` | Bengali text | One field with a language tag · **Paired `<field>` / `<field>_bn`** | **Paired** | A record commonly holds both; a language tag forces a choice the data does not make | `BN-01`; length limits in characters (`BN-02`) |
| `IN-002-D-07` | Scope granularity | Per operation (1,187) · **Per aggregate × action (~88)** | **Per aggregate × action** | 1,187 scopes is a permission model nobody can administer; `AP-005` `SC-04` requires the narrowest scope *that satisfies the contract*, not the narrowest conceivable | §7.3 derivation; `IN-005` §5 ratifies the names |
| `IN-002-D-08` | Publishing before the vocabulary is ratified | Publish with placeholders · **Block publication** | **Block** | A partner integrating against a scope name that then changes is a breaking change on day one | `FF-54`; exemplars carry `x-scope-status: proposed` |

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | **Is the scope vocabulary ratified?** Until it is, no contract may be published and no credential issued (`SD-02`, `FF-54`) | Solution Architect + Security Lead | **W0 — blocking** | Every partner integration |
| Q-02 | Is `IN-002`'s **109–356 PW** funded? (`IN-A-02`) | Programme Director | **W0** | The whole surface |
| Q-03 | Who owns the **~190 `platform` operations**? M28 declares 18; the rest are spread across M29, M30, M62–M65 | Chief Architect | **W1** | W1 contract set |
| Q-04 | Which generator? The estate has **no code and no toolchain**; the choice constrains the route-decorator form in every module | Platform Engineering | **W1** | `FF-56`, `AR-007` §5 |
| Q-05 | Do partners receive **bundled** single-file contracts or `$ref`-resolved multi-file? Some partner tooling cannot follow external `$ref` | Integration Architect | W3 | `AP-001` publication |
| Q-06 | Does the estate adopt **OAS 3.2.0** at the W2 gate, and does the technician position stream need it? (`IN-001` §2.4a) | Design Authority | W2 | Streaming surfaces |
| Q-07 | `FF-53` will report **M40 and M42 as having zero business-rule coverage** because `05-05` registers no rules for them (`EO-02`). Is that accepted as a true finding or suppressed? | Chief Architect + `RQ-009` owner | W2 | Contract completeness reporting |

---

## 14. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The API surface is **measured** and the denominator stated | §11.1 — 1,187 operations |
| AC-02 | The unit of a contract document is ruled, with rejected alternatives | §3.1, `IN-002-D-01` |
| AC-03 | Generation, not hand-maintenance, is ruled and gated | §3.3, `FF-56` |
| AC-04 | A shared component library exists and duplication is forbidden | §5 |
| AC-05 | The error model is ruled against a current standard, without invalidating 90 existing codes | §6.2, `IN-002-D-03` |
| AC-06 | Every operation must declare a **named scope**, and publication is blocked until the vocabulary exists | §7.2, `FF-54` |
| AC-07 | Bengali text is a typing rule, not a presentation note | §5.4 |
| AC-08 | **Executable artefacts exist** — the first non-markdown files in the estate | `IN-002_artefacts/`, 7 files, 35 operations, all parsing |
| AC-09 | Machine-checkable gates cover every rule that can be checked | §10, `FF-46`…`FF-58` |
| AC-10 | A coverage plan exists with contexts, waves, owners and **effort** | §11 |
| AC-11 | The sequencing rule explicitly avoids the `AP-03` defect | §11.3 |
| AC-12 | Every standard version claim carries a verification date | §2.1, `IN-001` §2.4 |

**Definition of done.** Complete when every criterion is met, `IN-001-D-01` and the `IN-005` §5
scope vocabulary are ratified, `FF-46`…`FF-58` are enabled, the W1 contract set (~405 operations)
is issued, and `PGD-000`'s `IN-002` row carries a fresh enumeration timestamp. **`M28` `AC-08` —
100% CI-validated coverage — is a Wave 9 criterion, not a Wave 1 one, and no document should imply
otherwise.**

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | **`IN-001`** §4, §6, §7 | Base path, idempotency semantics, resilience — fixed there, consumed here |
| Upstream | `AR-008` §5 | The eleven bounded contexts that organise the contracts |
| Upstream | `AR-001` §7.1 | The twelve families, now realised as tag groups and consumer groups |
| Upstream | **`IN-005`** §5 | **The scope vocabulary. `IN-002` is blocked on it** |
| Upstream | `DA-002` | Field names, types, limits and PII classification (`FF-55`) |
| Downstream | `IN-006` | Webhook **payload** schemas reuse `_shared/components.yaml` |
| Downstream | `IN-007` | Payment operations are `finance` context operations |
| Downstream | **`IN-008`** | Contract tests are generated from these files (`FF-57`) |
| Downstream | `UX-*` | Portal and app teams generate clients from these contracts |
| Downstream | `AP-002` | The developer-portal reference is generated from these contracts |
| Downstream | `SC-002` | The attack surface is exactly this contract set |
| Downstream | `QA-005` | Contract-test layer |
| Lateral | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` §5.2 | `API-01`…`API-12` realised; `API-04` embedded by `IN-002-D-03` |
| Lateral | `../../1000fix_ERP_Module/03_Modules/**/M*.md` §12 | Demoted to a human index by `IN-002-D-02` |
| Lateral | `../../project_content/15_Integration_and_Developer_Content/AP-002_*.md`, `AP-005`, `AP-006` | Content standard, scope proposal, error catalogue |

---

## 16. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`./IN-001_Integration_Architecture_Specification.md`](./IN-001_Integration_Architecture_Specification.md) ·
[`./IN-003_Domain_Event_Catalogue_and_Schema_Registry.md`](./IN-003_Domain_Event_Catalogue_and_Schema_Registry.md) ·
[`./IN-004_Interface_Control_Documents.md`](./IN-004_Interface_Control_Documents.md) ·
[`./IN-005_API_Governance_Versioning_and_Deprecation_Standard.md`](./IN-005_API_Governance_Versioning_and_Deprecation_Standard.md) ·
[`./IN-006_Webhook_Callback_and_Partner_Push_Specification.md`](./IN-006_Webhook_Callback_and_Partner_Push_Specification.md) ·
[`./IN-008_Integration_Test_Sandbox_and_Certification_Specification.md`](./IN-008_Integration_Test_Sandbox_and_Certification_Specification.md) ·
[`./IN-002_artefacts/README.md`](./IN-002_artefacts/README.md)

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md` §3.2, §5 ·
`../../1000fix_ERP_Module/03_Modules/**/M*.md` §12 (all 67) ·
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M28_*.md` §5, §12.5, §17 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §12.2.3 ·
`../../project_content/15_Integration_and_Developer_Content/AP-002_*.md`, `AP-005_*.md`, `AP-006_*.md`

**External sources**

| Source | Verified |
|---|---|
| OpenAPI Specification 3.1.0 (OpenAPI Initiative) | 2026-08-18 |
| OpenAPI Specification 3.2.0 — current stable, released September 2025, additive over 3.1 | 2026-08-18 |
| JSON Schema 2020-12 | 2026-08-18 |
| RFC 9457 *Problem Details for HTTP APIs* (July 2023; obsoletes RFC 7807) | 2026-08-18 |
| RFC 9110 *HTTP Semantics* | 2026-08-18 |
| RFC 3339 *Date and Time on the Internet* | 2026-08-18 |
| `draft-ietf-oauth-v2-1-15` — Internet-Draft, 2 March 2026 | 2026-08-18 |
| IETF `draft-ietf-httpapi-ratelimit-headers` — `RateLimit`, `RateLimit-Policy` | 2026-08-18 |

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Integration Architecture | Initial issue. Measures the surface at **1,187 operations against 0 machine-readable contracts**. Rules the contract unit (bounded context, `IN-002-D-01`), generation (`IN-002-D-02`) and the RFC 9457 embedding (`IN-002-D-03`). Issues the estate's **first non-markdown artefacts** — seven YAML files, four contracts, 35 operations. Sizes the deliverable at **109–356 PW** (`IN-A-02`) and blocks publication pending the scope vocabulary (`FF-54`) | *Pending — Design Authority not constituted (`PGD-A1-09`)* |

---

*`IN-002` · Category 04 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
