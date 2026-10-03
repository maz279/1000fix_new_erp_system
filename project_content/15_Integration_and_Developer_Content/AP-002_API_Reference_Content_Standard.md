---
id: AP-002
title: API Reference Content Standard
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering Lead
author: Platform Engineering with Content Design
reviewers: [CTO, Solution Architect, Content Design Lead, Security Lead, Localisation Lead, QA Lead]
approver: Programme Content Lead with CTO
content_class: E
purpose: >
  The authoring standard for every description, summary, example and error entry that appears in a
  1000FiX OpenAPI 3.1 specification — what each field must say, what it must never say, and how
  conformance is enforced in CI rather than by review. Without it `AS-07` and `M28` `AC-08` are satisfied
  by specifications that are structurally complete and unreadable: 100% OpenAPI coverage with
  descriptions generated from method names, which is the exact outcome `M28` §4 names as
  "technically complete and practically unusable" and which no partner integration team can work
  from.
traces_to: [M28, M28 FR-IPF-012, M28 FR-IPF-015, M28 FR-IPF-018, M28 AC-08, M28 BRU-IPF-04, 05-03, 05-03 IP-08, 05-03 §5.2, 05-06 AS-07, 05-06 NFR-078, CG-003, CG-004, CG-011, CG-012, UI-004, AP-001, AP-003, AP-004, AP-005, AP-006, AP-011, RF-001, TS-001]
priority: P1
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md §5.2 API-01…API-12 and §5.3 performance targets; §1 IP-08 "every external contract is versioned and documented — OpenAPI 3.1 for REST, JSON Schema for events"
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M28_Integration_API_and_Event_Platform.md §4 design position (governance enforced in CI, not by review), §5.2 FR-IPF-012 and FR-IPF-018, §17 AC-08
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md AS-07; NFR-078 "every error message states what happened and what to do next, in the user's language"
    verified: 2026-08-18
    class: P1
  - source: RFC 9457 Problem Details for HTTP APIs (July 2023), successor to RFC 7807 — type, title, status, detail, instance plus extension members and a shared registry of problem types. https://datatracker.ietf.org/doc/html/rfc9457
    verified: 2026-08-18
    class: P2
  - source: IETF HTTPAPI working group — draft-ietf-httpapi-idempotency-key-header-07 (Idempotency-Key request header for non-idempotent methods) and draft-ietf-httpapi-ratelimit-headers-11 (RateLimit and RateLimit-Policy fields). https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-07 · https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-ratelimit-headers
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# API Reference Content Standard

| Item | Value |
|---|---|
| Governs | Every authored string inside every 1000FiX OpenAPI 3.1 document |
| Applies to | All 12 API families (`05-03` §5.1) and every endpoint in every one of the 67 modules |
| Enforcement | CI lint (`FR-IPF-018`), build-failing — not review |
| Rules | 28 authoring rules `AR-01`…`AR-28` (§4.3) |
| Required fields per operation | 11 (§4.4) |
| Standards mapped to lint rules | `API-01`…`API-12` (§4.9) |
| Language | English only for the specification; `Accept-Language` behaviour documented per `AR-24` |
| Wave | W3 registered · **first consumed W1** — open item `O-01` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order; §4 subdivided by volume. The **endpoint reference table**
> required by `CG-009` §3 for this category appears at §4.5 as a fully worked reference entry —
> the standard is demonstrated on one real endpoint rather than described in the abstract, because
> a content standard that carries no specimen is re-interpreted by every author. The **error
> catalogue table** required by `CG-009` §3 appears at §4.7 as the *documentation* contract for
> errors; the catalogue of codes itself is `AP-006` (`CP-01`).

---

## 1. Purpose

`IP-08` requires every external contract to be versioned and documented, in OpenAPI 3.1 for REST.
`AS-07` makes it testable. `FR-IPF-012` generates the specification from code and fails the build
on divergence. `M28` `AC-08` requires 100% of published endpoints to carry a current, CI-validated
specification.

**All four of those can be satisfied by a document nobody can integrate against.** Generation
guarantees that the specification matches the code. It guarantees nothing about whether a human
can read it. A generated `POST /api/v1/service-orders` with `summary: "Create service order"`, no
`description`, no example, no error list and parameters documented as `customer_id (integer)`
passes every one of the four checks above and answers none of a partner developer's questions:
what does this actually create, what happens next, what does the customer see, what do I do when
it returns 409, and is it safe to retry.

`M28` §4 states the position: *"OpenAPI generated from code with no authored descriptions is
technically complete and practically unusable."* This file is the standard that closes the gap,
and it takes `M28`'s own enforcement position — **governance enforced in CI, not by review** —
because a standard enforced by review is a standard that lapses under schedule pressure at
exactly the wave when the most endpoints ship.

**What stops working without this file.**

| Absent | Consequence |
|---|---|
| Description conventions | 67 module teams author 67 description styles. A developer integrating across three families reads three voices and cannot tell whether a difference in wording signals a difference in behaviour |
| Required-field list | Optional fields are omitted. `description` and `example` are always the first two omitted, because they are the two the compiler does not need |
| Error documentation contract | Every partner escalates every non-2xx to 1000FiX, which is precisely the support load `AP-006`'s register justification names |
| Idempotency and pagination note conventions | `API-05` and `API-07` are implemented and undocumented. A partner writes a retry loop that double-books, or a page loop that misses records — both silent, both attributed to 1000FiX |
| Lint rules | The standard is aspirational. `M28` §4 already rejected "a central API review board as a gate; it recreates the bottleneck" — leaving CI as the only enforcement point that scales to 67 modules |

---

## 2. Scope

**In scope.** Authoring conventions for `info`, `tags`, operation `summary` and `description`,
parameter and property descriptions, request and response examples, error response documentation,
pagination notes, idempotency notes, rate-limit notes, scope and authorisation notes, deprecation
annotations, code samples, naming, terminology binding, and the CI lint rule set that enforces
all of it. Also: the boundary between what is authored in the specification and what is authored
in a guide.

**Out of scope.**

| Out of scope | Owned by | Note |
|---|---|---|
| API design itself — paths, verbs, status codes, resource modelling | `05-03` §5.2 `API-01`…`API-12` | This file documents a design; it does not set one. Where a design decision is undocumented, that is an `05-03` gap, recorded not resolved |
| The error code catalogue (codes, causes, remedies) | `AP-006` | §4.7 is the *documentation contract*; `AP-006` is the *register* |
| Event descriptions | `AP-003` | Events are JSON Schema, not OpenAPI. The conventions are deliberately parallel and are cross-referenced, not merged |
| Scope names and rate-limit values | `AP-005` | Documented here as a *required note*; the values are `AP-005`'s |
| Where the reference is published, and to whom | `AP-001` §4.2, §4.5 | This file governs content; `AP-001` governs surface |
| Deprecation notice **content** | `AP-011` | `AR-26` requires the annotation; `AP-011` writes the notice |
| UI-facing error copy | `UI-004` | An API error code and a UI error string are different artefacts with different audiences. §4.7 states the binding and refuses the merge |
| OpenAPI tooling, generator, linter selection | `M28` engineering / `06-04` (does not exist) | `O-02` |
| GraphQL federation schema documentation | `M28` `FR-IPF-010` | Out of scope by omission in the register; recorded as `O-06` |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Module developers across all 67 modules** | The instruction set they follow when annotating an endpoint. Primary audience by volume |
| **Platform Engineering** | The lint rule specification (§4.9) |
| **Content Design** | Review of the specimen (§4.5) and of `tags` and `info` prose |
| **Partner integration teams** | Indirect — they never read this file, they read its output. Every rule here is written against what they need |
| **QA** | `TS-001` level 3 (Contract) is CI-owned; description conformance is a *content* gate and needs a `TS` hook — `O-05` |
| **Technical writers or vendors** engaged later | The only document that lets a non-author bring an existing specification up to standard |

---

## 4. Content

### 4.1 The two-layer model

Every fact about an API lives in exactly one of two layers. Deciding this once removes the most
common argument in API documentation — whether something belongs in the reference or the guide.

| Layer | Contains | Authored in | Read when |
|---|---|---|---|
| **Reference** | What this endpoint is, what each field means, what each response means, what is required to call it | The OpenAPI document, as `description` / `example` / `summary` | The developer is writing the call |
| **Guide** | Why you would call it, in what order, with what else, and what the business outcome is | `AP-004`, `AP-007`…`AP-010`, and the Concepts pages of `AP-001` §4.2 | The developer is deciding what to build |

**The test:** if the sentence contains the word *then*, it is a guide sentence. Reference prose
describes one call in isolation; sequence belongs to a guide. This is `CP-01` applied inside a
single deliverable.

### 4.2 Voice

`CG-003` governs. Four points restated because they are the four most often broken in generated
API documentation.

| # | Rule | Wrong | Right |
|---|---|---|---|
| V-01 | **Present tense, active, third person.** The API is the subject | "This will create a service order" | "Creates a service order" |
| V-02 | **Sentence case throughout**, including `summary` and `tags` | "Create Service Order" | "Create a service order" |
| V-03 | **No first person and no marketing register.** No "simply", "just", "easy", "powerful" | "Simply pass the customer ID" | "Requires `customer_id`" |
| V-04 | **The controlled term, every time** (`CG-004`) | "job", "ticket", "case", "request" used interchangeably for `fix.service.order` | "service order" throughout; the term is bound in `RF-001` |

### 4.3 The twenty-eight authoring rules

Each rule states what it requires and what breaks without it. Rules marked **CI** are enforced by
lint and fail the build (`FR-IPF-018`); rules marked **REV** are review-enforced because they
cannot be mechanised, and are sampled per §4.10.

| # | Rule | Enforcement |
|---|---|:--:|
| **AR-01** | Every operation has a `summary` of **3–8 words**, verb-first, sentence case, describing the business action — not the HTTP method | **CI** |
| **AR-02** | Every operation has a `description` of **at least two sentences**: what it does in business terms, and one fact the caller cannot infer from the path — a precondition, a side effect, or a constraint | **CI** (length) + **REV** (substance) |
| **AR-03** | The `description` names the **side effects outside this resource**. If the call emits a domain event, the event type is named and linked to the `AP-003` catalogue entry | **CI** (link presence where the module registers an outbox write) |
| **AR-04** | Every operation declares its **required scope** by name (`AP-005`), in a dedicated `x-scopes` annotation rendered into the description | **CI** |
| **AR-05** | Every operation declares whether it is **safe to retry**, and if it accepts `Idempotency-Key`, says so explicitly with the duplicate-key behaviour | **CI** on state-changing operations (`API-07`) |
| **AR-06** | Every **path and query parameter** carries a `description`, a `schema`, and an `example` that is a realistic 1000FiX value — never `string`, `0`, `abc` or `foo` | **CI** |
| **AR-07** | Every **enumerated value** is listed with its meaning. An enum with no per-value meaning is an undocumented state machine | **CI** (presence) |
| **AR-08** | A parameter whose values come from a master-data register **names the register** — for example "`branch_code`: branch code from `MD-003`" | **REV** |
| **AR-09** | Every **request body property** carries `description`, `example`, and `required` status. Nested objects are documented to leaf level | **CI** |
| **AR-10** | Monetary fields state the **currency field they pair with** and that the value is decimal, never float (`DI-01`, `AS-10`) | **CI** on any property matching the money naming convention |
| **AR-11** | Timestamp fields state **UTC, RFC 3339** (`AS-11`), and whether the caller may supply one | **CI** |
| **AR-12** | Bengali-capable text fields state the field is **UTF-8 and may contain Bengali**, and give the length limit in **characters, not bytes** | **REV** |
| **AR-13** | Every operation carries **at least one complete request example and one complete response example**, using `TS-002` persona data — never production-shaped real data (`TX-05`, `NFR-071`) | **CI** |
| **AR-14** | Examples are **valid against their own schema**. A schema-invalid example fails the build | **CI** |
| **AR-15** | Every operation documents **every error status it can return**, with the `AP-006` code, not just the HTTP status | **CI** |
| **AR-16** | The error list includes **`401`, `403`, `429` and `5xx`** on every authenticated operation. These are omitted more often than any others and are the four a partner most needs | **CI** |
| **AR-17** | A `403` description distinguishes **"your credential lacks the scope"** from **"the record is outside your data scope"**. They are different failures with different remedies (`API-10`, `EA-11`) | **REV** |
| **AR-18** | Every **collection** operation documents cursor pagination: the cursor parameter, the page-size parameter, the maximum page size, and how the caller knows there are no more pages (`API-05`) | **CI** |
| **AR-19** | Every collection operation documents the **filter, sort and sparse-fieldset** parameters it supports, or states that it supports none (`API-06`) | **CI** |
| **AR-20** | Every operation documents its **rate-limit policy class** and points to `AP-005`, and states that `RateLimit` headers are returned (`API-08`) | **CI** |
| **AR-21** | Every operation states that responses carry a **`correlation_id`**, and that quoting it is the first step of any support request (`API-09`, `NFR-092`) | **CI** at the specification level, once per document |
| **AR-22** | Any operation with a **performance class** in `05-03` §5.3 states its class and its p95 target | **REV** |
| **AR-23** | Any operation subject to a **payload or export limit** states the limit and names the asynchronous job route (`API-12`) | **CI** where a limit is configured |
| **AR-24** | The specification states, once, that **error and validation messages are localised by `Accept-Language`** and that `code` and `details` are **never** localised (`API-11`) | **CI** at document level |
| **AR-25** | Any field carrying **personal data** is annotated with its `05-02` §10 sensitivity class, and any **residency-classified** field is annotated as such (`NFR-086a`) | **CI** against the classification register |
| **AR-26** | A **deprecated** operation carries the OpenAPI `deprecated: true` flag, the sunset date, and a link to the `AP-011` migration guide. Deprecation is never communicated by description text alone | **CI** |
| **AR-27** | No `description` contains an **internal identifier a caller cannot act on** — no Odoo model names, no table names, no `CD-nnn`, no internal ticket references | **CI** (pattern) |
| **AR-28** | No `description`, `example` or `summary` contains a **credential, token, key, real customer identifier or real phone number** — including in examples (`IP-07`, `NFR-062`) | **CI** (secret scanning over the specification, not only over code) |

> **`AR-28` is the rule most likely to be treated as unnecessary and is the one with the worst
> failure mode.** Secret scanning is normally run over source. An OpenAPI document is generated
> *from* source and published *to* a public surface (`AP-001` T-Pub), so a secret in an annotation
> reaches the outside world by a path that source-only scanning does not cover.

### 4.4 Required fields per operation

The eleven fields below are mandatory on every published operation. The lint rule set is the list
below plus §4.3; nothing else fails a build.

| # | Field | Source | Rule |
|---:|---|---|---|
| 1 | `summary` | Authored | `AR-01` |
| 2 | `description` | Authored | `AR-02`, `AR-03` |
| 3 | `operationId` | Generated | Stable across versions; changing it is a breaking documentation change (`AP-011`) |
| 4 | `tags` | Authored — one API family (`05-03` §5.1) | Exactly one; multi-tagged operations break the `AP-001` PT-04 generator |
| 5 | `x-scopes` | Authored | `AR-04` |
| 6 | `x-idempotent` | Authored | `AR-05` |
| 7 | Parameters with `description` + `example` | Authored | `AR-06`…`AR-08` |
| 8 | Request body schema with leaf-level descriptions | Authored | `AR-09`…`AR-12` |
| 9 | At least one request and one response example | Authored | `AR-13`, `AR-14` |
| 10 | Complete error response list with `AP-006` codes | Authored | `AR-15`…`AR-17` |
| 11 | `x-performance-class` where `05-03` §5.3 assigns one | Authored | `AR-22` |

**`x-scopes`, `x-idempotent` and `x-performance-class` are OpenAPI extension fields and are
proposals of this file.** `05-03` defines none of them. They are recorded as `O-03` because a
lint rule cannot enforce a field that no standard defines.

### 4.5 Worked reference entry — the specimen

One endpoint, documented to this standard. `POST /api/v1/service-orders` is chosen because it is
the first endpoint in `05-03` §3.2, it is the portal contract's most important write, and it
exercises every rule that is easy to skip.

| Element | Content |
|---|---|
| **Path** | `POST /api/v1/service-orders` |
| **Tag** | Customer API |
| **`summary`** | Create a service order |
| **`description`** | Creates a service order from a customer booking and returns the order with its tracking token. The order is created in `draft` and is classified asynchronously — warranty, contract and pricing outcomes are **not** present in this response and arrive by the `service_order.classified` event. A successful call emits `service_order.created`. Booking a slot does **not** reserve technician capacity; capacity is confirmed at dispatch. |
| **`x-scopes`** | `service_order:write` *(name provisional — `AP-005` `O-01`)* |
| **`x-idempotent`** | `true` — requires `Idempotency-Key`. A repeated key within the retention window returns the **original** order with `201`, not a duplicate and not a `409`. |
| **`x-performance-class`** | Writes — p50 200 ms · p95 500 ms · p99 1,000 ms (`05-03` §5.3) |
| **Request — required** | `customer_id` · `service_type_code` · `delivery_mode` · `asset` (one of `asset_id` or an inline device) · `contact` |
| **Request — key field notes** | `service_type_code`: service type from `MD-020`; determines price, promise and routing. `delivery_mode`: one of `walk_in`, `on_site`, `pick_drop`, `remote`, `workshop`, `kiosk` — each with different eligibility and charging (`MD-020`). `preferred_slot`: RFC 3339 UTC; must be a slot returned by `GET /api/v1/booking/availability` within the last 15 minutes. `description_bn`: UTF-8, may contain Bengali, 500 **characters**. |
| **Responses** | `201` order created · `400` `validation.failed` · `401` `auth.token_invalid` · `403` `auth.scope_insufficient` **or** `auth.out_of_scope` · `409` `order.duplicate_idempotency_key_in_flight` · `422` `order.service_type_not_available_at_location` · `429` `ratelimit.exceeded` · `503` `dependency.unavailable` |
| **Error notes** | `403 auth.scope_insufficient` — the credential does not hold `service_order:write`; remedy is a scope change, not a retry. `403 auth.out_of_scope` — the credential holds the scope but `customer_id` is not within its data scope; remedy is to correct the request, and **the response body never confirms whether the customer exists** (`EA-01`, `API-10`). |
| **Retry guidance** | `429` and `503` are retryable with the same `Idempotency-Key`, honouring `Retry-After`. `400`, `403` and `422` are not retryable without changing the request. `409` means an identical key is still in flight — retry the same key after 2 s. |
| **Pagination** | n/a — single-resource write |
| **Emits** | `service_order.created` → see `AP-003` |
| **Sensitivity** | `contact.phone` S2 · inline device `serial` S1 · no residency-classified field in this payload (`AR-25`) |

> **Read the `description` again.** Three of its four sentences state something the path cannot
> tell you, and all three are the sentences a partner would otherwise discover in production:
> classification is asynchronous, the response is incomplete by design, and a booking is not a
> reservation. That is what `AR-02` is asking for.

### 4.6 Schema and property conventions

| # | Convention |
|---|---|
| SC-01 | One schema per business object, named by its `CG-004` controlled term in `PascalCase` — `ServiceOrder`, not `SrmOrderV1` |
| SC-02 | Request and response schemas are **separate** where they differ. A single shared schema with half its fields marked read-only is the most common cause of a partner sending a field that is silently ignored |
| SC-03 | Field names are `snake_case`, matching the payload; the description never repeats the name back ("`customer_id`: the customer id" is a lint failure under `AR-09`) |
| SC-04 | Nullable is explicit. A field that can be null says **when** it is null |
| SC-05 | A field that is present but empty and a field that is absent mean the same thing, or the difference is documented |
| SC-06 | Identifiers state their **stability**: permanent, or replaceable on merge. `customer_id` is subject to `customer.merged` and this must be said in the schema, not only in `AP-003` |
| SC-07 | Every collection response uses the **same envelope shape** across all 12 families: `data`, `page`, `correlation_id` |
| SC-08 | Enumerations are **closed by default**. Where a new value may be added within a version, the schema says so and tells the consumer to tolerate unknown values — this is `05-03` §4.3's additive-compatibility rule applied to REST |
| SC-09 | No schema exposes a field the caller's tier may not see. Field-level restriction (`05-04` §5) is enforced server-side **and** the specification for an external family omits the field entirely — a documented field a partner can never receive is a support ticket |

**SC-09 has a structural consequence.** Because `05-04` §5 restricts fields by *role* and a
partner credential maps to one audience class, the twelve families in `05-03` §5.1 need **twelve
schema sets, not one shared set with conditional visibility.** Generation from a single internal
model will produce the wrong specification for external families unless the generator is
family-aware. Recorded as `O-04`.

### 4.7 Error documentation contract

The error catalogue table required by `CG-009` §3. This is the **documentation** contract; the
codes, causes and remedies are `AP-006`'s register, loaded into the reference as data (`AP-001`
PT-08).

**Envelope.** `API-04` specifies `code`, localised `message`, `details`, `correlation_id`. This
file documents that envelope and records the standards question rather than silently deviating:

| Position | Detail |
|---|---|
| **The programme standard is `API-04`** | Four fields, as specified. Every specification documents this shape |
| **RFC 9457 Problem Details is the wider industry default** | `type`, `title`, `status`, `detail`, `instance`, plus extension members and a registry of problem types; it supersedes RFC 7807 and is backward compatible |
| **They are not equivalent** | `API-04` has no `type` URI, no `status` in the body and no multi-problem representation. A partner whose stack has an RFC 9457 client gets no benefit from it |
| **This file does not change the standard** | Changing `API-04` is an `05-03` decision, not a content decision. It is recorded as `O-07` with the recommendation that `API-04` fields be emitted **as RFC 9457 extension members** so both readings hold — a change that is additive and costs one mapping |

**Per-error documentation requirements.**

| # | Requirement | Rule |
|---|---|:--:|
| ED-01 | Every documented error names its `AP-006` code, not only the HTTP status | `AR-15` |
| ED-02 | Every documented error states the **cause in the caller's terms** — what the caller did or what was true | `AR-15` |
| ED-03 | Every documented error states **the remedy**, and the remedy is an action the caller can take | `NFR-078` applied to APIs |
| ED-04 | Every documented error states **retry-safe: yes / no / yes-with-backoff** | `AR-05` |
| ED-05 | Errors caused by 1000FiX (`5xx`, `dependency.*`) say so plainly and name the status page (`AP-001` §8) | Trust; also reduces `PM-04` tickets |
| ED-06 | An error that reveals the existence of a record outside the caller's scope is a **defect**, not a documentation issue | `API-10`, `EA-01` |
| ED-07 | Business-rule violations reference the rule class from `05-05` — a hard (`H`) rule tells the caller no override exists; an approved-override (`A`) rule tells them who can authorise | Prevents partners retrying a permanently impossible request |
| ED-08 | `message` is localised (`API-11`); `code` and `details` are stable, machine-readable and **never** translated | `AR-24` |

**The `UI-004` binding, and why it is a binding and not a merge.** `UI-004` is the validation and
error message library for human interfaces, keyed `common.error.<domain>.*`. `AP-006` is the API
error catalogue. The same underlying condition appears in both — a service order rejected because
the device is out of warranty is one business fact with two audiences. The rule:

> **One condition, one `AP-006` code, one `UI-004` key, and a declared mapping between them.
> Neither file restates the other's text.** The mapping lives in `AP-006` §4 and is checked by
> audit check `F4`, which today only tests `MD` → `UI-004`. Extending `F4` to `AP-006` → `UI-004`
> is recommendation `R-04` of the Category 15 audit.

### 4.8 Code samples

| # | Rule |
|---|---|
| CS-01 | Samples are **generated from the specification**, not hand-written, in cURL, Python, PHP and Node.js. Hand-written samples drift and are the second-worst staleness source after hand-written reference pages |
| CS-02 | Four languages, chosen for the audience: **cURL** (universal, and the only one usable in a support conversation), **PHP** (Bangladesh integrator prevalence), **Python**, **Node.js** (the portal platform's own runtime) |
| CS-03 | No sample contains a real credential, real token, real customer identifier or real phone number (`AR-28`) |
| CS-04 | Every sample for a state-changing operation **includes the `Idempotency-Key` header**. A sample that omits it teaches every reader to omit it |
| CS-05 | Every sample handles the non-2xx path. A sample that only prints the happy path is where partner retry storms come from |
| CS-06 | Samples are not translated (`CG-010` §3.2) and contain no Bengali literals except where demonstrating a Bengali text field, in which case a real Bengali string is used, not a transliteration |

### 4.9 Standards-to-lint mapping

`M28` §4: *"`05-03` §5.2 API-01…API-12 become linter rules and contract tests. A specification that
is not enforced is documentation, not governance."* This is that mapping, and it is the reason
this file is `P1` rather than `P2`.

| Standard | What it requires | Documentation rule | Lint check |
|---|---|:--:|---|
| **API-01** | REST/JSON; GraphQL only via federation | — | Non-REST path outside the federation prefix fails |
| **API-02** | Path versioning; ≥ 2 concurrent versions; 6 months' notice | `AR-26` | Missing `deprecated`/sunset annotation on a superseded version fails |
| **API-03** | OpenAPI 3.1, CI-validated, published | All | Specification absent, invalid, or divergent from implementation fails (`FR-IPF-012`) |
| **API-04** | Standard error envelope | §4.7 ED-01…ED-08 | Error response not conforming to the envelope schema fails |
| **API-05** | Cursor pagination, max page size enforced | `AR-18` | Collection operation without cursor parameters documented fails |
| **API-06** | Filter, sort, sparse fieldsets on collections | `AR-19` | Collection operation with neither the parameters nor the explicit "none supported" statement fails |
| **API-07** | `Idempotency-Key` on all state-changing operations | `AR-05` | State-changing operation without `x-idempotent` fails |
| **API-08** | Rate limits with headers; 429 + `Retry-After` | `AR-20`, `AR-16` | Operation not documenting `429` fails |
| **API-09** | `correlation_id` on every response | `AR-21` | Document-level check |
| **API-10** | No data outside the caller's scope | `AR-17`, SC-09, ED-06 | Schema exposing a field restricted for the family fails |
| **API-11** | Bengali/English messages via `Accept-Language` | `AR-24`, ED-08 | Document-level check |
| **API-12** | Payload limits; large exports async | `AR-23` | Operation with a configured limit and no documented limit fails |

**Two standards have no mechanical check and are therefore review-sampled:** `API-01`'s GraphQL
boundary and `API-06`'s "supports none" declaration where a collection genuinely supports none.

### 4.10 Conformance measurement

`M28` `AC-08` counts specifications. This counts **descriptions**, and it is the gap `AP-001` `O-04`
records from the surface side.

| # | Measure | Definition | Target |
|---|---|---|---|
| **DC-01** | Rule conformance | Operations passing all **CI** rules ÷ published operations | **100%** — build-enforced, so any other figure means the gate is bypassed |
| **DC-02** | Review-rule sample defect rate | `REV` rule failures ÷ rules × operations sampled | ≤ 5%, sampled at **10% of operations per wave gate**, matching audit check `E3`'s sampling standard |
| **DC-03** | Example realism | Sampled examples using `TS-002` persona data ÷ sampled examples | **100%** |
| **DC-04** | Error completeness | Documented error codes ÷ error codes the endpoint can actually emit, measured against production error logs by code | ≥ 95% by W5 |
| **DC-05** | Partner-reported documentation defects | Tickets classed "documentation wrong or missing" per 100 registered consumers | Downward trend; no absolute target set until a baseline exists |

**DC-04 is the only measure here that cannot be gamed**, because its denominator comes from
production traffic rather than from the specification. An endpoint emitting a code it does not
document is found by comparing the gateway error log to the specification — a query, not a
review.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `05-03` §5.2 `API-01`…`API-12` | The standards this file turns into documentation rules. If a standard changes, §4.9 changes |
| `05-03` §5.3 | The performance classes `AR-22` requires |
| `M28` `FR-IPF-012`, `FR-IPF-018` | Generation and lint. Without `FR-IPF-018` every **CI** rule in §4.3 becomes **REV** and the standard does not scale |
| `AP-005` | Scope names for `AR-04`; rate-limit classes for `AR-20` |
| **`AP-006`** | Error codes for `AR-15`. `AR-15` cannot pass CI before `AP-006`'s codes exist — both are W3, so the sequencing holds only if they are authored together |
| `AP-003` | Event names for `AR-03` |
| `AP-011` | Migration-guide links for `AR-26` |
| `CG-003`, `CG-004`, `RF-001` | Voice and terminology; `RF-001` is the term register `AR`/`V-04` resolve against — **and it is unwritten** |
| `05-02` §10 | The S0–S3 classification `AR-25` annotates against |
| `05-04` §5 | Field-level restrictions SC-09 enforces |
| `TS-002` | The persona data `AR-13` requires in examples |
| `UI-004` | The binding target of §4.7 |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per wave gate |
| Trigger for out-of-cycle review | A change to `API-01`…`API-12` · adoption of RFC 9457 (`O-07`) · a new API family · a lint rule found to produce false failures · the first partner documentation retrospective |
| Owner | Platform Engineering Lead |
| Change control | Adding or removing a **CI** rule requires CTO approval and a `RF-006` entry, because it changes what fails a build across 67 module teams. Wording changes to a **REV** rule need the owner only |
| Version pinning | Pinned to **API version** (`CG-006` §5) |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **Registered W3; first consumed W1.** `M28` ships its framework in W1 with the API registry, OpenAPI generation and lint (`FR-IPF-012`, `FR-IPF-018` — both `P0`, both W1), and `AS-07` applies from the first published endpoint. Every endpoint written in W1 and W2 without this standard must be retrofitted. **This is the fifth category in which the register places a file after the wave that consumes it** (`AUDIT-008`, `-009`, `-010`, `-014`) | Programme Content Lead with Platform Engineering Lead | **W1 — before the first endpoint is published** |
| **O-02** | **No linter is selected and no CI owner is named.** §4.9 specifies twelve mappings and §4.3 twenty-one **CI** rules. `06-04_Testing_and_Quality_Strategy.md` — which would own CI tooling — **does not exist** (`TS-001` `O-01`). Without a linter this file is a style guide, and `M28` §4 explicitly rejected the review-board alternative | CTO | **W1 build** |
| **O-03** | **`x-scopes`, `x-idempotent` and `x-performance-class` are proposals of this file.** No extension-field convention exists in `05-03`. Three mandatory fields (§4.4) and four lint rules depend on them | Solution Architect with CTO | **W1 design** |
| **O-04** | **Twelve API families need family-aware specification generation.** SC-09 plus `05-04` §5 means one internal model cannot generate twelve correct external specifications. If the generator is model-driven rather than family-driven, external specifications will document fields partners can never receive — or worse, fields they must not know exist | Platform Engineering Lead | **W3 — before the first external family publishes** |
| **O-05** | **Description conformance has no test level.** `TS-001` §4.1 places Contract testing at level 3, engineering-owned, with **no Category 13 file** — and its coverage standard is "validated against its OpenAPI specification", which is structural. DC-02 and DC-03 are content measures with no owning pack | QA Lead with Platform Engineering Lead | W3 |
| **O-06** | **GraphQL federation documentation is unowned.** `API-01` and `FR-IPF-010` provide a federation layer for composed portal reads. This standard covers OpenAPI only; a federated schema has its own documentation conventions and no file in the register covers them | Platform Engineering Lead | W4 |
| **O-07** | **`API-04` versus RFC 9457.** The programme's four-field envelope predates and diverges from the current IETF standard. Recommendation: emit `API-04` fields as RFC 9457 extension members so both readings hold. This is an `05-03` change, not a content change, and cannot be made here | Solution Architect with CTO | **W1 — the envelope is implemented in W1 and is expensive to change afterwards** |
| **O-08** | **`RF-001` glossary is unwritten.** `V-04` and `AR-08` resolve terms against it. Until it exists, "the controlled term" is `CG-004` plus judgement, and 67 module teams will exercise judgement differently | Enterprise Architecture with Programme Content Lead | W1 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the §4 subdivision is the only addition and is justified
- [x] **Reference-versus-guide boundary settled with a stated test (`CP-01`)**
- [x] Twenty-eight authoring rules, each marked CI-enforced or review-enforced
- [x] Eleven mandatory fields per operation listed
- [x] A complete worked reference entry authored to the standard, not described in the abstract
- [x] Nine schema conventions including the field-restriction consequence
- [x] Error documentation contract with eight requirements
- [x] **The `API-04` versus RFC 9457 divergence stated and referred upward rather than silently deviated from**
- [x] **The `AP-006` ↔ `UI-004` binding stated as a mapping, with the merge explicitly refused**
- [x] All twelve `API-*` standards mapped to a documentation rule and a lint check
- [x] Five conformance measures with denominators (`CP-11`)
- [x] Extension-field proposals marked as proposals (`CG-012`, `CM-R8`)
- [x] All internal links resolve
- [x] Eight open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` registered after first consumption — outstanding; W1 endpoints will need retrofit**
- [ ] **`O-02` no linter selected, no CI owner — outstanding; without it every CI rule degrades to review**
- [ ] **`O-03` extension-field convention undefined — outstanding; blocks four lint rules**
- [ ] **`O-07` `API-04` envelope decision — outstanding; cheapest to settle before W1 build**
- [ ] Named approvers recorded — **pending Programme Content Lead and CTO**
- [ ] Bengali counterpart — n/a; developer audience, English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
