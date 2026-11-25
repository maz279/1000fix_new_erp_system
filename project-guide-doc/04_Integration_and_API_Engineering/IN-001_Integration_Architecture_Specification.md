---
id: IN-001
title: Integration Architecture Specification
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
  ISO/IEC/IEEE 42010:2022 (interface and process viewpoints, inherited from AR-001) ·
  Enterprise Integration Patterns (Hohpe & Woolf) · Richardson Maturity Model ·
  OpenAPI 3.1 (contract form, IN-002) · AsyncAPI 3.0 (channel form, IN-003) ·
  Release It! stability patterns (circuit breaker, bulkhead, timeout)
traces_to: >
  PGD-000 IN-001 · 05-03 §1 IP-01…IP-10 · 05-03 §5 · AR-001 §7.1, §7.2, §8.1 ·
  M28 FR-IPF-001…057 · CON-03 · audit AP-01, AP-04, AP-05, AP-06 · NFR-042, NFR-043,
  NFR-048, NFR-050, NFR-068
depends_on: AR-001 · AR-002 · AR-009 · AR-005 · GV-002
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 14:40 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# IN-001 — Integration Architecture Specification

### Category 04 · Code `IN` · Enterprise Integration Patterns · ISO/IEC/IEEE 42010:2022

---

> **The measurement that sizes this category.** Extraction across the API-surface table of all
> **67 module specifications** and all **12 portal specifications** at **2026-08-18 14:40 (+06)**
> returns:
>
> | Measure | Count |
> |---|---:|
> | Distinct API paths declared by modules | **978** |
> | Distinct `(method, path)` operations declared by modules | **1,187** |
> | Distinct API paths **consumed by portals** | **140** |
> | Of those, declared by **no** module (after parameter normalisation) | **100 — 71.4%** |
> | Distinct events consumed by portals | **102** |
> | Of those, published by **no** module | **69 — 67.6%** |
> | Module paths sitting under one of the **twelve declared API families** | **38 — 3.9%** |
>
> Audit `AP-01` found **21** unregistered event names by comparing three files. The consumer-side
> gap measured across all twelve portals is **69**, and it contains **all three** of `AP-01`'s
> safety-critical events. `AR-009` measured the producer side at **988 declared vs 64 registered**.
> **Both halves of the contract are broken, in opposite directions, and neither side knows.**

---

## 1. Purpose

`AR-001` §7.1 and §7.2 fix *that* the system integrates through twelve API families and five
patterns. `05-03` states ten integration principles and catalogues 47 external systems. Neither
designs the mechanism. This document **designs it**: the gateway topology, the canonical model, the
pattern-selection rule, idempotency, the retry and circuit-breaker ladder, the anticorruption
boundary, the integration lifecycle, and the governance that keeps 1,187 operations and 47 external
contracts coherent across nine waves.

It also does the thing no document in the estate has done: **reconcile the producing side against
the consuming side**, and rule on the contradiction between consumer-scoped API families and
resource-scoped module paths — a contradiction that decides the base path of every operation
`IN-002` will write.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The integration reference architecture — layers, components and where each concern is enforced |
| 2 | The **five patterns**, and the rule that selects one |
| 3 | **The API family ruling** — consumer-scoped vs resource-scoped, and the migration it implies |
| 4 | Gateway topology, policy placement, and what may never be enforced at the edge |
| 5 | The canonical model, and the deliberate decision not to build one |
| 6 | Idempotency — key form, scope, retention, and the operations it is mandatory on |
| 7 | Resilience — timeout, retry, backoff, circuit breaker, bulkhead, fallback |
| 8 | The **anticorruption layer** rule for external systems |
| 9 | The CON-03 portal platform architecture — the estate's most important integration |
| 10 | Integration lifecycle: registration, connector shape, promotion, retirement |
| 11 | Observability and the integration health model |
| 12 | The measured producer/consumer reconciliation and its remediation plan |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Machine-readable API contracts | `IN-002` | This document rules the shape; `IN-002` writes the contracts |
| Event catalogue, schemas and registry | `IN-003` | `AR-009` designs the bus; `IN-003` is the registry |
| Per-external-system contracts | `IN-004` | One ICD per counterparty; this document gives them their common frame |
| Versioning, deprecation, consumer registration | `IN-005` | Governance is a separate lifecycle concern |
| Webhook signature and delivery | `IN-006` | External delivery has its own threat surface |
| Payment-specific design | `IN-007` | Money movement carries obligations no generic pattern covers |
| Contract testing and sandbox | `IN-008` | Verification, not design |
| Bus mechanism, outbox, replay | `AR-009` | Ruled there; consumed here |
| Network design, broker sizing | `PE-001`, `PE-005` | This document fixes topology; `PE` runs it |
| Threat model of the API surface | `SC-002` | Trust zones are `AR-001` §8.1; the threat model is `SC-002` |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **`IN-002` author** | §4's family ruling sets the base path of every operation |
| **`IN-004` author** | §8's anticorruption rule and §7's resilience ladder are the ICD's common clauses |
| Integration engineers | §5 pattern selection, §6 idempotency, §7 resilience — the day-to-day rules |
| Portal and app developers | §9's CON-03 architecture and §11's reconciliation are what they are building against |
| Platform engineers | §3 topology and §10 lifecycle |
| Partner developers | §8's boundary contract, indirectly through `AP-007`/`AP-008` |
| QA lead | §5, §6 and §7 are directly testable; `IN-008` derives from them |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / concept | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO/IEC/IEEE 42010:2022** | Interface and process viewpoints | Inherits `AR-001` VP-3 and VP-4; this document is the *detailed design* those views delegate | None |
| **Enterprise Integration Patterns** (Hohpe & Woolf) | Messaging gateway, message router, content enricher, dead letter channel, idempotent receiver, claim check, anticorruption layer | Adopted **by name** in §5 and §8, so a vendor's engineers recognise them without translation | None |
| **Richardson Maturity Model** | Level 2 (resources + verbs + status codes) | The estate targets **Level 2**, explicitly, and does **not** adopt Level 3 hypermedia | **Deliberate departure.** HATEOAS costs client complexity for a closed, versioned, generated contract set. Recorded as `IN-001-D-04` |
| **Release It!** stability patterns | Timeout, circuit breaker, bulkhead, fail fast, steady state | §7's ladder is a direct implementation | None |
| **OpenAPI 3.1** | Contract form | Named in `05-03` API-03 and Technology Stack §12.2.1; `IN-002` writes them | **Version currency finding — see §2.4** |
| **AsyncAPI 3.0** | Channel and message form | Named as the category standards basis; `IN-003` writes them | None |
| **OAuth 2.1** | Grant restrictions | §3.4 adopts the mandated practices | **OAuth 2.1 is an Internet-Draft, not an RFC — see §2.4** |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| Integration & API Catalogue | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` | IP-01…IP-10, the 47 integrations, the CON-03 contract, API-01…API-12, performance targets |
| All 67 module specifications | `../../1000fix_ERP_Module/03_Modules/**/M*.md` §12 | **The measurement.** 978 paths, 1,187 operations, 988 events |
| All 12 portal specifications | `../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P*.md` §12 | **The consumer side.** 140 paths and 102 events consumed |
| M28 Integration, API & Event Platform | `.../K_Platform_and_Technology/M28_*.md` | `FR-IPF-001`…`057`, 18 platform endpoints, the connector framework, `BRU-IPF-*` |
| Technology Stack Specification | `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §12.2 | Kong 3.x, CD-125 outbox, CD-127 webhook, n8n, the 47 technology assignments |
| `AR-001` | `../02_Architecture_and_Design/AR-001_*.md` §7.1, §7.2, §8.1 | Twelve families, five patterns, six trust zones, LB-01…LB-09 |
| `AR-009` | `../02_Architecture_and_Design/AR-009_*.md` | Outbox, envelope, delivery semantics, the 988 measurement |
| `AUDIT-016` | `../../project_content/_AUDIT/AUDIT-016_*.md` | `AP-01`, `AP-04`, `AP-05`, `AP-06` — the three unmade W1 decisions |
| `AP-001`…`AP-012` | `../../project_content/15_Integration_and_Developer_Content/` | Developer-facing content written **against** these contracts |

**Reproducible extraction.** Every count in this document was produced by the following, run at
**2026-08-18 14:40 (+06)** against `1000fix_ERP_Module/03_Modules`:

```bash
# API operations. NOTE: §12 is not uniform — 46 modules put API Surface at 12.5
# (12.4 being External Integrations); 21 put it at 12.4. See finding IN-A-03.
for f in $(find 03_Modules -name 'M[0-9]*.md'); do
  if grep -q '^### 12\.5 API Surface' "$f"; then S='12\.5'; else S='12\.4'; fi
  awk -v S="$S" 'BEGIN{p=0} $0 ~ "^### "S {p=1;next} /^### 1[0-9]\./{p=0} /^## /{p=0} p' "$f" \
    | grep -E '^\| *`' | awk -F'|' '{gsub(/^ +| +$/,"",$2);gsub(/^ +| +$/,"",$3);
        gsub(/`/,"",$2); if($2 ~ /^\//) print $3"\t"$2}'
done | sort -u                     # → 987 rows · 978 distinct paths · 1,187 (method,path)

# Portal-consumed paths (P01…P12 §12.5) and events (§12.3), normalised on {param}
```

### 2.3 Audit findings this document closes or contributes to

| Finding | Source | Disposition |
|---|---|---|
| **`AP-01` (critical)** — 21 events consumed and unregistered | `AUDIT-016` | **Extended, not merely confirmed.** §11.2 measures the consumer-side gap at **69** across all twelve portals. Closes with `IN-003` |
| **`AP-04` (high)** — no webhook signature scheme | `AUDIT-016` | §5.4 fixes the pattern; **`IN-006` ratifies the scheme** |
| **`AP-05` (high)** — no scope vocabulary | `AUDIT-016` | §3.4 fixes where scope is enforced; **`IN-005` §5 ratifies the vocabulary** |
| **`AP-06` (high)** — three payment availability commitments do not reconcile | `AUDIT-016` | §7.6 rules the general case (circuit-breaker state drives failover, not the monitoring window); **`IN-007` §9 reconciles the three** |
| `AR-001` `CR-03` — interface view correspondence to the module surface untested | `PGD-AUDIT-003` | §4.3 runs the test. **It fails at 3.9%** |
| `TR-12` — outbox applied unevenly | Tech Stack §23 | Inherited from `AR-009` §5.5; reinforced by `FF-38` (§10.5) |
| `M28` `Q-08` — no escalation when a consumer refuses to migrate | `M28` §18 | Referred to `IN-005` §7.4 with a contractual remedy |

### 2.4 Version-currency findings raised by this document

**`PG-M4` requires every standard and vendor version claim to carry a verification date.** Three
claims inherited from the estate do not survive verification at **2026-08-18**:

| # | Claim in the estate | Verified position | Disposition |
|---|---|---|---|
| **VC-01** | *"OpenAPI 3.1"* — `05-03` API-03, Tech Stack §12.2.1, `PGD-000` `IN-002` row title | **OpenAPI 3.2.0 was released in September 2025** and is the current stable specification. 3.2 is a **non-breaking** superset of 3.1 | **`IN-002` is authored to 3.1.0 and validates as 3.1.0**, because the register row, three published documents and `AS-07` name 3.1, and `PG-01` is register-first. §2.4a records the upgrade path. Raised as `IN-A-06` |
| **VC-02** | *"OAuth 2.1"* — this category's `_CATEGORY_OVERVIEW.md` standards basis | **OAuth 2.1 is an IETF Internet-Draft** (`draft-ietf-oauth-v2-1`, revision 15, 2 March 2026), **not a published RFC** | Conform to its **mandated practices** (§3.4), and cite it as a draft. A document that cites a draft as a standard is the `C-04`/`H-01`/`M-01` defect class. Raised as `IN-A-07` |
| **VC-03** | *"PDPA 2026"* — cited throughout the estate, with a penalty ceiling of **BDT 25–50 lakh** | The instrument is the **Personal Data Protection Ordinance 2025** (gazetted 6 November 2025) as amended by the **Personal Data Protection (Amendment) Ordinance, 2026 — Ordinance No. 23 of 2026**, promulgated 5 February 2026. Enforcement mechanisms — Chief Data Officer appointment, complaint, investigation and penalty procedures — are **deferred by 18 months to on or about 13 May 2027**. Published analyses describe a **turnover-proportional** penalty regime (1–2% of annual turnover generally; 2–5% for a significant data fiduciary), **not** a fixed BDT ceiling | **Referred, not corrected here.** The instrument's short name and penalty basis are cited in `05-06` §6.3, `LG-*`, `AP-012`, `GV-005` and four audits. Correcting it is a repository-wide change and belongs to `SC-005`/`DA-005` with Legal Counsel. **Raised as `IN-A-08`, severity High** — a turnover-based penalty on a company with 250,000+ customers per month is not the same exposure as BDT 50 lakh, and `GV-008`'s risk budget is sized against the smaller figure |

> **Why VC-03 is raised in an integration document.** `IN-004`'s ICD for `INT-034` (NID
> verification) and `IN-002`'s `data.residency_restricted` error both rest on the statute's
> cross-border and localisation rules, and the Amendment Ordinance **narrowed** localisation to
> restricted data and Critical Information Infrastructure. An integration designed against the
> unamended text is designed against a rule that has changed. Verification date **2026-08-18**.

#### 2.4a The OpenAPI version upgrade path

| Question | Position |
|---|---|
| Does 3.2 break 3.1? | **No.** 3.2.0 is additive — hierarchical tags, first-class streaming (SSE, JSON Lines, multipart), `additionalOperations` for custom methods |
| Does anything in `IN-002` need 3.2? | **One thing.** The technician and rider position streams (§9.3) are a streaming surface that 3.1 can only describe as a normal response |
| When does the estate move? | **At the `W2` wave gate**, once tooling for 3.2 is proven in CI. `AR-013` carries it as a radar item |
| What must not happen | Authoring some contracts to 3.1 and some to 3.2. **One version across the contract set**, changed once, deliberately (`IN-005` `GV-API-09`) |

---

## 3. The Integration Reference Architecture

### 3.1 The layered view

Every integration in the estate passes through the same five bands. **Naming them is what makes
"where is this enforced?" answerable without reading code.**

```
                              EXTERNAL WORLD
   47 external systems · 17+ brand partners · 500–2,000 sellers · 12 portals · 4 apps
        │                                                              │
        │ inbound                                              outbound│
┌───────▼──────────────────────────────────────────────────────────────▼───────┐
│ B1  EDGE  (Z0/Z1)   CDN · WAF · bot management · Kong 3.x                    │
│     TLS 1.3 · OAuth introspection · quota · correlation-id injection ·       │
│     Idempotency-Key presence · payload ceiling · request/response logging    │
├──────────────────────────────────────────────────────────────────────────────┤
│ B2  CONTRACT        OpenAPI 3.1 (IN-002) · AsyncAPI 3.0 (IN-003) ·           │
│     JSON Schema 2020-12 · error envelope · pagination · versioning           │
├──────────────────────────────────────────────────────────────────────────────┤
│ B3  MEDIATION       Anticorruption layers (§8) · connector framework ·        │
│     n8n long-tail orchestration · content enrichment · claim check ·          │
│     residency service CD-233 · outbound proxy (Z6 allow-list)                │
├──────────────────────────────────────────────────────────────────────────────┤
│ B4  TRANSPORT       Sync REST/HTTPS │ Outbox → Redis Streams (W1–W5) →       │
│     Redpanda (W6+) │ Signed webhook POST │ SFTP batch │ WebSocket            │
├──────────────────────────────────────────────────────────────────────────────┤
│ B5  DOMAIN          The 67 modules. Business meaning lives ONLY here          │
└──────────────────────────────────────────────────────────────────────────────┘
```

| Band | Owns | May **never** own |
|---|---|---|
| **B1 Edge** | Authentication *verification*, quota, correlation id, transport security, coarse routing | **Any authorisation decision that depends on a record.** Scope-vs-record is B5's job (`API-10`, `LB-05`) |
| **B2 Contract** | Shape, validation, versioning, error form | Business rules. A schema says a field is a date; `RQ-009` says whether it may be in the past |
| **B3 Mediation** | Translation between the estate's model and a counterparty's | Persistence of business state. A mediator is stateless except for idempotency and dedup ledgers |
| **B4 Transport** | Delivery, ordering, durability, retry | Interpretation of the payload |
| **B5 Domain** | **All business meaning, all authorisation on records, all state** | Direct bus-client code (`FF-28`), direct external HTTP calls (must pass B3/Z6) |

> **Rule `IA-01` — the band a concern belongs to is the band that can enforce it in exactly one
> place.** The estate's most expensive integration defects are concerns enforced in the wrong band:
> authorisation at the edge (unenforceable against records), business rules in a connector
> (invisible to the module that owns them), retry logic per module (never uniformly correct).

### 3.2 Component allocation

| Concern | Component | Layer | Source |
|---|---|---|---|
| API gateway | **Kong 3.x** (TC-016) | L4 | Tech Stack §12.2.1 |
| Event outbox | **CD-125 `cd_event_outbox`** | L5 | AS-08, `AR-009` §5 |
| Event bus | **Redis Streams** → **Redpanda** (W6+) | L4 | ADR-013 |
| Webhook delivery | **CD-127 `cd_webhook`** | L5 | `IN-006` |
| Connector framework | **CD-126** (M28 §5.5) | L5 | `FR-IPF-026`…`031` |
| Long-tail orchestration | **n8n 1.x** (TC-017) | L4 | Tech Stack §12.2.1 |
| Residency mediation | **CD-233** | L5 | NFR-086, `AR-001` LB-08 |
| Outbound proxy | **Z6 egress** with named allow-list | Infra | `AR-001` §8.1 |
| Integration monitoring | **CD-129** + Prometheus + Grafana | L5 + L4 | `05-03` §7 |
| Credential store | **Vault** (or equivalent) | Infra | IP-07, NFR-062 |
| Schema registry | **`IN-003`** registry + CI compatibility gate | L5 | `AR-009` §9 |

### 3.3 Where a policy may be enforced — the placement table

Enforcement placement is the decision most often made by accident. It is made here.

| Policy | Edge (B1) | Contract (B2) | Domain (B5) | Rule |
|---|:--:|:--:|:--:|---|
| TLS termination, HSTS | ✔ | | | Edge only |
| Token signature and expiry | ✔ | | | Edge introspects; `M29` is authoritative |
| **Scope held by the credential** | ✔ | | | Coarse capability check at the edge is a **fail-fast optimisation** |
| **Record within the caller's data scope** | | | ✔ | **`API-10`, `LB-05`. Never at the edge.** The edge cannot know who owns row 918234 |
| Rate limit / quota | ✔ | | | Kong plugin, per consumer (`IN-005` §6) |
| Bot / abuse detection | ✔ | | | NFR-068 |
| `Idempotency-Key` **present** | ✔ | | | Gateway rejects a state-changing request without one (API-07) |
| `Idempotency-Key` **honoured** | | | ✔ | Only the domain knows what "the same request" produced |
| Payload size ceiling | ✔ | ✔ | | Edge for the hard ceiling; contract for the per-endpoint limit (API-12) |
| Schema validation | | ✔ | | Generated from the contract; run in the service, not the gateway |
| Field-level disclosure (`AP-012`) | | | ✔ | Depends on the counterparty **and** the record |
| Residency (`NFR-086`, LB-08) | | | ✔ | Through CD-233 only |
| Business rules (`RQ-009`) | | | ✔ | Always |
| `correlation_id` injection | ✔ | | | One origin, propagated everywhere (`NFR-092` §7 sense) |

> **`IA-02` — a policy enforced in two bands is a policy with two behaviours.** Where a check
> appears twice in the table above, the second occurrence is explicitly labelled an optimisation
> and is **never** the authority.

### 3.4 Authentication and authorisation position

| # | Position | Basis |
|---|---|---|
| **AA-01** | **Every** API call carries an OAuth bearer token issued by `M29`. There is no unauthenticated API surface except the tokenised public tracking view (`/api/v1/tracking/{token}`), which is a capability URL, not an API | PS-01, `LB-05` |
| **AA-02** | Authorisation-code grant **with PKCE** for every interactive client — including confidential ones. The **implicit grant and resource-owner password grant are forbidden** | OAuth 2.1 draft-15 mandated practices; `AP-005` §4.2 |
| **AA-03** | Client-credentials grant for machine-to-machine only, never for a flow with an end user behind it | OAuth 2.1; `SC-03` of `AP-005` |
| **AA-04** | Redirect URIs are matched **exactly** — no wildcard, no prefix match | OAuth 2.1 |
| **AA-05** | Refresh tokens are **sender-constrained or single-use with rotation** | OAuth 2.1 |
| **AA-06** | Scope grants **capability**; record visibility is a data-scope property enforced in B5 and cannot be widened by a request parameter | `API-10`, `EA-11`, `AP-005` `SC-01`/`SC-02` |
| **AA-07** | The **scope vocabulary is `IN-005` §5's**. `AP-005` §4.3 proposed it; `IN-005` ratifies it. **No credential is issued before ratification** | `AP-05` (audit) |
| **AA-08** | The webhook receiver family `/hooks/v1/*` authenticates by **signature**, not by bearer token, and is the only family that does | `IN-006` §6 |

---

## 4. The API Family Ruling

### 4.1 The contradiction

Three published documents declare the same twelve **consumer-scoped** API families:

| Source | Statement |
|---|---|
| `05-03` §5.1 | Twelve families: `/api/v1/customer/*`, `/api/v1/technician/*`, `/api/v1/ops/*`, `/api/v1/corporate/*`, `/api/v1/vendor/*`, `/api/v1/seller/*`, `/api/v1/brand/*`, `/api/v1/logistics/*`, `/api/v1/analytics/*`, `/api/v1/admin/*`, `/api/v1/partner/*`, `/hooks/v1/*` |
| Technology Stack §12.2.2 | The same twelve, with the same auth model |
| `AR-001` §7.1 | The same twelve, and: *"**the family is the unit of contract, versioning and rate limiting** — not the endpoint, and not the module"* |

The 67 module specifications declare **resource-scoped** paths: `/api/v1/service-orders`,
`/api/v1/warranty/claims`, `/api/v1/assets/{id}`, `/api/v1/payouts`.

### 4.2 The measurement

| Measure | Count | Share |
|---|---:|---:|
| Distinct module-declared paths | **978** | 100% |
| Sitting under one of the eleven `/api/v1/<family>/` prefixes | **38** | **3.9%** |
| `/hooks/v1/*` receiver paths | **6** | 0.6% |
| Sitting under **neither** | **934** | **95.5%** |
| Distinct **second path segments** in use (de facto resource families) | **219** | — |

The eleven `/api/v1/<family>/` prefixes that do carry traffic are almost entirely `analytics`
(P06) and `admin` (M30/M28 console). Every business resource — service orders, claims, invoices,
consignments, payouts — is resource-scoped.

### 4.3 The ruling

> **Ruling `IN-001-D-01`. The path is resource-scoped. The family is a *policy* label, not a path
> prefix.**
>
> - **Base path:** `/api/v1/<resource-collection>` — kebab-case plural, as the 978 already are.
> - **The twelve families remain**, and remain "the unit of contract, versioning and rate limiting"
>   exactly as `AR-001` §7.1 says — but they are realised as **Kong consumer groups and
>   OpenAPI tag groups**, not as URL segments.
> - **`/hooks/v1/*` is unchanged**, because it genuinely is a different surface with a different
>   authentication model (AA-08).
> - `/api/v1/analytics/*`, `/api/v1/admin/*` and `/api/v1/platform/*` are **retained as real
>   prefixes**, because those three are not business resources — they are surfaces.

**Why this way round, stated because the opposite is the intuitive choice:**

| Consideration | Consumer-scoped paths | Resource-scoped paths |
|---|---|---|
| Same resource, two audiences | `/api/v1/customer/service-orders` **and** `/api/v1/ops/service-orders` — **two paths, two contracts, two sets of tests for one resource** | One path, one contract; the credential's scope decides what comes back |
| Cost of the decision today | Rewrite **934 of 978** declared paths across 67 specifications | Rewrite **38**, and only their prefix |
| Consistency with `API-10` | Encourages the belief that the *path* enforces scope — which is exactly the shortcut `API-10` forbids | Scope is visibly a credential property, never a URL property |
| A new audience (a 13th portal) | A whole new path tree, and every operation duplicated into it | A new consumer group and a scope grant. **Zero new paths** |
| Machine-readable contract | Twelve OpenAPI documents that repeat the same schemas | One document set per bounded context, tagged by family |

> **The decisive argument is `API-10`.** *"No endpoint returns data outside the caller's
> authorisation scope, ever — enforced server-side."* A consumer-scoped path makes the scope look
> like it lives in the URL. It does not, it cannot, and a design that suggests it does will produce
> exactly the defect `API-10` exists to prevent — the day someone adds `/api/v1/ops/service-orders`
> as "the same thing without the customer filter."

### 4.4 What changes, and what it costs

| # | Change | Volume | When | Cost |
|---|---|---:|:--:|---|
| **FR-01** | Correct `05-03` §5.1's family table to state that a family is a policy grouping, not a path prefix | 1 table | **W0** | One edit |
| **FR-02** | Correct `AR-001` §7.1 and Tech Stack §12.2.2 to the same | 2 tables | **W0** | Two edits |
| **FR-03** | Re-prefix the **38** module paths currently under a consumer-scoped family to their resource form, **except** `analytics`, `admin` and `platform` | ≤ 38 paths | **W1** | Text edit; no code exists |
| **FR-04** | Register the twelve families as Kong **consumer groups** with their auth model and rate-limit class | 12 | **W1** | `IN-005` §6 |
| **FR-05** | Declare the family as an OpenAPI **tag group** on every operation (`IN-002` §5.3) | 1,187 operations | W1–W9 | Part of authoring |

**None of this is possible after consumers exist.** `05-03` §3.4 and `API-02` require two
concurrent versions and six months' notice; a base-path change after the first partner integrates
is a v2 of the entire surface. Like `AR-009`'s 245 event renames, the window is **now**.

### 4.5 The consequential naming standard

| # | Rule | Measured position |
|---|---|---|
| **PN-01** | Collections are **plural, kebab-case nouns**: `/service-orders`, `/warranty-claims` | **136 of 756** distinct path segments already use kebab-case; **0** use snake_case; **0** use camelCase. The estate is already consistent |
| **PN-02** | A resource identifier segment is `{id}` unless the resource genuinely has two identifier kinds | `{id}` occurs **350** times; **20** other parameter names occur, several of them nouns (`{employee}`, `{party}`, `{brand}`) rather than identifiers |
| **PN-03** | Sub-resources nest **at most two levels**: `/service-orders/{id}/evidence`. Three levels means a missing resource |
| **PN-04** | An action that is not CRUD is a **sub-resource POST**, not a verb in the collection path: `/service-orders/{id}/cancel`, never `/cancel-service-order` | The estate already does this consistently |
| **PN-05** | **Abbreviated namespaces are expanded.** `/api/v1/mp/*` → `/api/v1/marketplace/*`; `/api/v1/ap/*`, `/api/v1/ar/*`, `/api/v1/gl/*`, `/api/v1/wh/*`, `/api/v1/fpa/*` are module codes, not resources — the same defect `AR-009` §3.3 found in event names | **~40 of the 219** second segments are module codes. Renamed in the same W1 pass as the event renames |
| **PN-06** | Version is **in the path** (`/v1/`), never in a header or a query parameter | `API-02`; **971 of 978** paths already comply; the 6 `/hooks/v1/*` are the intended exception |
| **PN-07** | `{param}` names are `snake_case` and name the **thing identified**, not its type: `{employee_id}`, not `{employee}` | Corrects the 20-name spread under PN-02 |

> **`PN-05` and `AR-009` `D-A9-03` are the same decision applied to two surfaces.** Event names use
> module-code namespaces in ~245 cases; API paths use them in ~40. Both were authored by module
> teams naming things after themselves. Both are free to fix in W1 and expensive afterwards. They
> should be executed as **one remediation**, not two.

---

## 5. The Five Integration Patterns

`AR-001` §7.2 fixes five patterns. This section makes them **selectable** — the failure mode
otherwise is that every integration becomes synchronous REST because that is what is easiest.

### 5.1 The selection rule

Apply in order. **The first rule that matches decides**, and the decision is recorded in the
integration's row in the register (§10.2).

| # | Question | If yes → | Why |
|---|---|---|---|
| 1 | Does a **human is waiting** for the answer to proceed? | **P1 Synchronous** | Anything else means a screen that says "we'll tell you later" |
| 2 | Is the counterparty a **regulator or bank** that mandates a file? | **P5 Batch file** | The form is not ours to choose (`INT-005`, `INT-038`, `INT-040`) |
| 3 | Does the counterparty **notify us** of state we did not ask for? | **P4 Webhook (inbound)** | Polling for it is a defect with a cost (`INT-001`…`003`, `INT-024`…`026`) |
| 4 | Do **two or more** modules need to react to the same fact? | **P3 Domain event** | A command to each is coupling that grows quadratically |
| 5 | Must the work happen, but **not now**? | **P2 Asynchronous command** | Queued, idempotent, retried, with a visible completion |
| 6 | Otherwise | **P3 Domain event** | Default to the loosest coupling that works |

### 5.2 The five patterns in full

| # | Pattern | Transport | Delivery | Ordering | Failure semantics | Idempotency mechanism |
|---|---|---|---|---|---|---|
| **P1** | Synchronous request/response | REST/JSON over HTTPS via Kong | Exactly once *attempted* | n/a | Timeout → circuit breaker → declared fallback; **the caller degrades visibly** | `Idempotency-Key` on state-changing verbs (§6) |
| **P2** | Asynchronous command | Command queue → worker | **At-least-once** | Per command stream | Retry ladder → DLQ → alert | Client-generated command **UUID** |
| **P3** | Domain event (pub/sub) | Transactional outbox → bus | **At-least-once** | **Per aggregate instance only** | 3 retries → DLQ after backoff → mandatory triage | Consumer-side `event_id` ledger (`AR-009` C-01) |
| **P4** | Webhook (in/outbound) | Signed HTTPS POST | At-least-once | **None guaranteed** | Retry ladder; endpoint disabled after 5 consecutive failures | `webhook-id` dedup ledger (`IN-006` §5) |
| **P5** | Batch file exchange | SFTP / signed drop | Exactly once per **file** | Per file, by sequence number | Control totals; freeze point; **manual fallback mandatory** | File sequence number + content hash |

### 5.3 Pattern rules that are not optional

| # | Rule | Consequence if broken |
|---|---|---|
| **PT-01** | **Every integration declares exactly one primary pattern** in the register (IP-03) | An integration with no declared pattern has no declared failure semantics |
| **PT-02** | A **synchronous call may never be made inside a database transaction.** Ever | The transaction holds locks for the counterparty's latency budget. This is how a 30-second bKash timeout becomes a table-wide lock |
| **PT-03** | A synchronous call to an **external** system may never be made on the **critical path of a state transition**. The transition commits; the call is a P2 command or a P3 consumer | Otherwise the counterparty's availability becomes ours |
| **PT-04** | A **domain event may never carry a command** (`AR-009` P-01), and a **notification is never an event** (`AR-009` E4) | Replay re-sends every SMS ever sent |
| **PT-05** | A **webhook is never trusted on its own content.** An inbound webhook is a *hint*; the authoritative state is read back from the counterparty | See §5.4 — this is a money-loss control |
| **PT-06** | A **batch file is never partially applied.** Control totals reconcile or the whole file is rejected | Half a payroll run is worse than none |
| **PT-07** | **Polling is a fallback, never a design.** Where a counterparty offers a webhook, polling exists only as the degraded mode, with a declared interval and a stated cost | `05-03` §3.1 already assumes "events + polling fallback" for the portal |

### 5.4 `PT-05` in full — why an inbound webhook is only a hint

The single most consequential rule in this document, and the one an implementation is most likely
to shortcut.

| Step | Behaviour |
|---|---|
| 1 | Receive the POST at `/hooks/v1/{integration}` |
| 2 | **Verify the signature** per the provider's scheme (`IN-006` §6). Reject `401` if absent or wrong |
| 3 | **Deduplicate** on the provider's delivery id |
| 4 | Persist the raw envelope, verbatim, for audit (`AP-012` §4.8 egress/ingress logging) |
| 5 | **Acknowledge fast** — 2xx within the provider's tolerance, before doing any work |
| 6 | Raise an internal P2 command |
| 7 | **Read the authoritative state back from the counterparty's own query API** |
| 8 | Apply the state change from *that* read, not from the webhook body |

> **The reason is specific and it is financial.** SSLCOMMERZ's own integration guidance requires an
> IPN to be re-validated through its Transaction Validation API before the merchant treats a
> payment as complete; its IPN carries an MD5 `verify_sign`, and a signature check alone is not the
> published sufficient condition. bKash's flow is `create → execute → **query**`. **A forged or
> replayed `payment.received` against an endpoint whose URL is discoverable from one prior delivery
> is a direct financial-fraud vector** — `AP-04` says so, and it is unmitigated today. Verified
> 2026-08-18. `IN-007` §6 makes this a per-rail obligation.

---

## 6. Idempotency

`API-07` requires `Idempotency-Key` on all state-changing operations, enforced at the gateway.
That is a presence check. This section specifies the **semantics**, which nothing in the estate
does.

### 6.1 The contract

| # | Rule |
|---|---|
| **ID-01** | `Idempotency-Key` is **required** on `POST`, `PUT`, `PATCH` and `DELETE`. The gateway rejects `400 request.header_missing` if absent |
| **ID-02** | The key is a **client-generated UUIDv4**. The server never generates one |
| **ID-03** | The key's scope is **`(consumer_id, method, path_template, key)`**. Two different consumers may use the same key value without collision, and a key is not portable across endpoints |
| **ID-04** | On first receipt: process, then **store `(key, request_body_hash, response_status, response_body, created_at)`** |
| **ID-05** | On repeat with the **same body hash**: return the **stored response**, byte-identical, with `Idempotency-Replayed: true`. Do not re-execute |
| **ID-06** | On repeat with a **different body hash**: `409 idempotency.key_reused_different_body`. **Never process it** |
| **ID-07** | On repeat **while the first is still executing**: `409 idempotency.in_flight`, `Retry-After: 2` |
| **ID-08** | Retention is **24 hours** for ordinary operations and **7 days** for money-moving operations (`IN-007` §5.3). After expiry: `422 idempotency.key_expired` |
| **ID-09** | The idempotency record is written in the **same transaction** as the effect. A record without an effect, or an effect without a record, is the defect this exists to prevent |
| **ID-10** | An operation that is **naturally idempotent** (`PUT` of a full representation, a state transition to a terminal state) still honours the key — `state.already_in_target` is a success, not an error (`AP-006` §4.5) |

### 6.2 Why 7 days for money

`idempotency.key_expired` says, verbatim, *"Treat the outcome as unknown and reconcile before
resubmitting. **Never blind-resubmit a payment or a payout.**"* A 24-hour window means a partner
whose integration was down over a weekend cannot safely retry, and the only remaining option is a
human reconciliation against the gateway. Seven days covers the realistic outage-and-recovery
envelope. Storage cost is trivial; a double payout is not.

### 6.3 The three idempotency mechanisms are different, and must not be confused

| Surface | Key | Held by | Lifetime |
|---|---|---|---|
| Synchronous API (P1) | `Idempotency-Key` header, client UUID | Server-side ledger | 24 h / 7 d |
| Domain event (P3) | `event_id` in the envelope | **Each consumer's own** ledger | Consumer's replay window |
| Inbound webhook (P4) | Provider's delivery id (`webhook-id` or equivalent) | Receiver's dedup ledger | ≥ the replay window, ideally permanent |

> A single "idempotency table" serving all three is a design smell: the three have different keys,
> different owners and different lifetimes, and merging them makes the retention rule
> unsatisfiable.

---

## 7. Resilience

### 7.1 The ladder

Every outbound call, without exception, sits inside all five rungs.

| Rung | Setting | Default | Notes |
|---|---|---|---|
| **1 Timeout** | Connect / read | **2 s / 5 s** internal; **per-counterparty** external | An unbounded call is an outage waiting for traffic |
| **2 Retry** | Attempts | **3** total, on **idempotent operations only** | A non-idempotent operation without an idempotency key is **never** retried |
| **3 Backoff** | Exponential with **full jitter** | base 200 ms, cap 8 s | Synchronised retries are a self-inflicted denial of service (`AP-005` `RL-03`) |
| **4 Circuit breaker** | Open / half-open / closed | open at **≥50% failures over 20 calls**; half-open probe after **30 s** | **The breaker's state, not the monitoring window, drives failover** — see §7.6 |
| **5 Bulkhead** | Connection pool + concurrency cap per counterparty | pool 20, concurrency 10 | One slow counterparty must not exhaust the shared pool |
| **+ Fallback** | Declared per integration | Mandatory for all **13** P0 | NFR-050, IP-09 |

### 7.2 External timeouts are per-counterparty, not global

The 5 s internal default is wrong for several counterparties, and using it would produce spurious
failures. Verified against published guidance **2026-08-18**:

| Counterparty | Published expectation | Timeout to set | Consequence |
|---|---|---|---|
| **bKash** (`INT-001`) | Its own integration guide instructs merchants to set an **API timeout of 30 s** on all calls | **30 s**, on a bulkhead of its own | **`NFR-042`'s 3 s p95 payment confirmation cannot be met end-to-end.** §7.6 |
| **SSLCOMMERZ** (`INT-003`) | IPN + **mandatory** Transaction Validation API call | 15 s | The validation call is on the critical path of "paid" |
| **Nagad** (`INT-002`) | RSA sign/verify on every request and response | 20 s | Crypto work at both ends |
| **Google Maps** (`INT-019`) | Interactive | 3 s | Fallback: cached geocodes, OSRM |
| **Traccar** (`INT-023`) | Self-hosted, LAN-adjacent | 2 s | Fallback: last known position |
| **NBR e-VAT** (`INT-038`) | Portal-mediated; no published machine API | n/a — **P5 batch** | §7.5 |
| **BEFTN** (`INT-005`) | T+1 batch through the sponsoring bank | n/a — **P5 batch** | §7.5 |

> **`IN-A-04` (high).** `05-03` §2 assigns `INT-038` the pattern *"File / API"* and `INT-005`
> *"Batch file"*. Verification at 2026-08-18 finds **no publicly documented machine API** for
> Mushak-9.1 submission through IVAS at `vat.gov.bd`; the return is filed through the portal,
> monthly, by the 15th. Likewise, **1000FiX is not a BEFTN participant** — Bangladesh Bank's
> operating rules make the *originating bank* the participant, and the file 1000FiX produces is its
> **bank's** implementation of the BEFTN fixed-width record format (file header, batch header,
> entry detail, control records, three-digit Standard Entry Class codes), not Bangladesh Bank's.
> **Both ICDs are with a different counterparty than the register names.** `IN-004` §7 and §8.

### 7.3 Retry safety by verb — the table an engineer actually needs

| Verb | Retry without a key | Retry with `Idempotency-Key` | Notes |
|---|:--:|:--:|---|
| `GET`, `HEAD` | ✔ | n/a | Naturally safe |
| `PUT` (full replace) | ✔ | ✔ | Naturally idempotent |
| `DELETE` | ✔ | ✔ | Second delete is `state.already_in_target` |
| `PATCH` | ✘ | ✔ | A partial update is not idempotent in general |
| `POST` | **✘ — never** | ✔ | This row is the reason `API-07` exists |

**On a timeout the outcome is unknown, not failed.** A caller that treats a timeout as a failure
and resubmits without a key has created a duplicate. `AP-006`'s retry column is normative and
`IN-002` §7 carries it into every operation.

### 7.4 Fallback register — the P0 obligation

`NFR-050` requires every P0 integration to have a **documented, tested** manual fallback. `05-03` §7
lists twelve. **A P0 integration whose fallback has not been exercised is a wave-gate failure, not
a risk** (`AR-001` §7.2).

| # | Rule |
|---|---|
| **FB-01** | Every P0 integration has a named fallback, a named owner, and a written procedure in `SV-*`/`OP-014` |
| **FB-02** | The fallback is **exercised at least once per wave gate**, on a scheduled drill, through `/api/v1/platform/integrations/{id}/test-fallback` |
| **FB-03** | Engaging a fallback publishes `platform.fallback_engaged` and is **visible to affected users** in their own language (IP-05, PS-09) |
| **FB-04** | A fallback that requires more than **15 minutes of manual work per transaction** is not a fallback; it is an outage with paperwork. Recorded and escalated |
| **FB-05** | **`INT-003` has no failover.** It is the only card acquirer in the catalogue. §7.6 |

### 7.5 Batch integrations get their own rules

`P5` is the pattern most likely to be designed as though it were `P1` with a delay.

| # | Rule |
|---|---|
| **BF-01** | Every file carries a **header record, a control record and a monotonic sequence number**. A gap in the sequence is an incident |
| **BF-02** | **Control totals** (record count and value sum) are computed on generation and re-verified on the counterparty's acknowledgement. Mismatch = whole file rejected (`PT-06`) |
| **BF-03** | Every file has a **freeze point** — a stated instant after which no further transaction enters that file — and the freeze point is a business decision, not a job schedule |
| **BF-04** | The generated file is **retained immutably** for the statutory period alongside its acknowledgement |
| **BF-05** | **A regulator-mandated file has no fallback other than manual submission**, and that path is exercised before the first live filing, not after |
| **BF-06** | A batch counterparty that returns results asynchronously (BEFTN returns, bank statement imports) has a **declared reconciliation window** and an alert when it lapses |

### 7.6 The `AP-06` reconciliation — the general ruling

`AP-06` found three payment commitments that cannot all hold. The payment-specific resolution is
`IN-007` §9. The **architectural** half is ruled here because it applies to all 47 integrations:

> **Ruling `IN-001-D-02`. Failover is driven by circuit-breaker state, never by the monitoring
> window.**
>
> `05-03` §7 detects unavailability at *"< 99% over 15 minutes"* and error rate at *"> 2% over 5
> minutes"*. `M28` `AC-13` requires automatic fallback **within 2 minutes**. A 5-minute detection
> window cannot produce a 2-minute failover, and no amount of tuning makes it. The two are
> different instruments:
>
> | Instrument | Purpose | Timescale |
> |---|---|---|
> | **Circuit breaker** (per-counterparty, in-process) | **Engages the fallback** | Seconds — 20 calls, ~50% failure |
> | **Monitoring window** (`05-03` §7) | **Alerts a human and opens an incident** | Minutes |
>
> `M28` `AC-13`'s 2 minutes is satisfied by the breaker. `05-03` §7's windows are correct **as
> alerting thresholds** and are wrong if read as failover triggers. `05-03` §7's heading is
> corrected to *"Integration Monitoring and Alerting"*.

> **Ruling `IN-001-D-03`. A latency budget that includes a third party is stated as two numbers.**
> `NFR-042`'s *"payment confirmation round trip ≤ 3 s p95"* is unachievable against a rail whose
> own guidance sets a 30 s client timeout. It is restated as **internal processing ≤ 3 s p95,
> excluding third-party call time**, plus a **separate, published end-to-end expectation per rail**.
> This is a correction to `05-06`, raised as `IN-A-05` and owned with `RQ-006`.

---

## 8. The Anticorruption Layer

### 8.1 The rule

> **`AC-01`. No external system's model enters the domain.** Every one of the 47 external
> integrations is mediated by an anticorruption layer in band B3 that translates the counterparty's
> vocabulary, identifiers, enumerations, date formats, currency representation and error taxonomy
> into the estate's own.

`AR-005` §6 registers six anticorruption layers between internal contexts. This section extends the
same discipline outward, where the need is far stronger: an internal context we can change, a
payment gateway we cannot.

### 8.2 What an ACL must do

| # | Obligation | Example |
|---|---|---|
| **AC-02** | **Identifier translation both ways**, with the mapping persisted | bKash `paymentID` ↔ `fix_payment_transaction.id`. Never store one and derive the other |
| **AC-03** | **Enumeration translation**, with an explicit `unknown` branch that alerts rather than defaults | A courier status the mapping has never seen must not silently become `in_transit` |
| **AC-04** | **Money is `{amount: "1234.50", currency: "BDT"}`** — string decimal, never float (AS-10) — regardless of what the counterparty sends | SSLCOMMERZ returns amounts as strings; some rails return numbers |
| **AC-05** | **Time is RFC 3339 UTC** at the boundary. Bangladesh Standard Time is UTC+06 and is a *presentation* concern | A gateway that reports local time without an offset is the classic six-hour reconciliation bug |
| **AC-06** | **Error translation** into the `AP-006` code set. A counterparty's error string never reaches a user or a caller | `dependency.*` codes exist for exactly this |
| **AC-07** | **Personal-data minimisation at the boundary** (IP-10) — only the fields the counterparty's purpose requires, per `AP-012`'s field-level register | A courier receives name, phone and address; never NID |
| **AC-08** | **Residency-classified values never cross the boundary except through CD-233**, which is also the only place the transfer is logged | `AR-001` LB-08, `NFR-099` |
| **AC-09** | **The ACL is the only place the counterparty's SDK or protocol appears.** No module imports a gateway SDK | Makes replacing a counterparty a bounded change |
| **AC-10** | **The ACL is independently testable** with a recorded fixture set, without the counterparty | `IN-008` §5 |

### 8.3 Where the ACL lives

| Counterparty class | Implementation | Basis |
|---|---|---|
| P0 payments, government, bank | **Custom L5 connector** (`CD-100`, `CD-194`, `CD-195`, `CD-242`) | Consequence too high for low-code |
| Communications, mapping, courier | **L3 connector or L5 wrapper** through CD-126 | Tech Stack §12.2.4 |
| Long tail (P2/P3, low volume) | **n8n workflow** under M28 governance | `INT-IPF-05` |
| Portal platform (CON-03) | **Neither.** It is a first-class internal contract, not an external one | §9 |

> **`AC-11` — an n8n workflow is a connector with a lower bar, not a lower standard.** It carries
> the same obligations `AC-02`…`AC-10`. What it does not carry is a release cycle. A P0 integration
> may **never** be an n8n workflow.

---

## 9. The CON-03 Portal Platform Architecture

### 9.1 Why this is the estate's most important integration

`CON-03` states the Next.js 15 + Payload CMS 3 platform cannot be replaced. It is live from **W1**,
it carries the customer-facing brand, and it is the only integration where **both sides are ours
and neither side owns the whole**. `05-03` §3 gives it a field-ownership table, 22 endpoints, 11
webhooks and seven contract rules — the most detailed integration contract in the estate.

### 9.2 The measured state of that contract

| Half of the contract | Declared in `05-03` §3 | Reconciled against the module surface | Gap |
|---|---:|---:|---:|
| **Synchronous** — §3.2 core API surface | 22 endpoints | **10 declared by a module** | **12 — 54.5%** |
| **Asynchronous** — §3.3 webhooks | 11 events | **3 published by a module** | **8 — 72.7%** |

**The 12 endpoints no module declares:**

`/api/v1/booking/availability` · `/api/v1/catalogue/products` · `/api/v1/catalogue/services` ·
`/api/v1/customers/{id}` · `/api/v1/customers/{id}/assets` · `/api/v1/customers/{id}/contracts` ·
`/api/v1/customers/{id}/invoices` · `/api/v1/customers/{id}/loyalty` ·
`/api/v1/marketplace/offers` · `/api/v1/payments/confirm` · `/api/v1/rentals/availability` ·
`/api/v1/tradein/quote`

**The 8 webhooks no module publishes:**

`catalogue.updated` · `consignment.status_changed` · `contract.expiring` · `estimate.issued` ·
`invoice.created` · `loyalty.points_changed` · `payment.received` · `service_order.status_changed`

> **`/api/v1/payments/confirm` is the payment gateway confirmation endpoint and `payment.received`
> is the event that tells the portal money arrived. Neither exists on the producing side.** The W1
> portal contract contains a money path with no owner.

Three of the eight are the **coarse-projection** class `AP-01` identified — `service_order.status_changed`
and `consignment.status_changed` are projections of finer module events, and `estimate.issued`,
`invoice.created` and `contract.expiring` are the same-fact-two-names class. **Three are genuinely
missing**: `catalogue.updated`, `loyalty.points_changed`, `payment.received`.

### 9.3 The architecture the contract needs

| Concern | Design | Why not the obvious alternative |
|---|---|---|
| **Projection events** | The portal subscribes to a **published projection channel** carrying `service_order.status_changed` and `consignment.status_changed`, produced by a **named projector** in M01 and M03 from the fine-grained set | An undocumented projection is what `AP-01` found. A *documented* projection is a legitimate and better design than forcing a web front end to understand 16 order events |
| **Customer-composed reads** | `/api/v1/customers/{id}/…` are **composition endpoints** owned by **M33 (Party Master)**, which fans out to M08, M20, M10 and M17 behind one contract | Making the portal issue four calls moves the composition to the client, where it cannot be cached, scoped or rate-limited coherently |
| **Catalogue** | `/api/v1/catalogue/*` owned by **M37**, with `catalogue.updated` published on publish of a price book or a service definition | `05-03` §3.1 already says "scheduled + on change"; the event is what makes "on change" real |
| **Availability** | `/api/v1/booking/availability` owned by **M02**, **synchronous**, and the only synchronous cross-boundary read the portal makes on the critical path | `05-03` §3.1 declares it synchronous. It is; and it therefore carries the 2 s p95 obligation alone |
| **Payment confirmation** | `/api/v1/payments/confirm` owned by **M20**, and it is a **hint endpoint under `PT-05`** — it never marks an invoice paid on its own | See §5.4 |
| **Position streaming** | `technician.location_updated` is throttled and delivered over the existing WebSocket, **not** as a webhook per update | A webhook per GPS ping is a delivery ladder per ping |
| **Reconciliation** | Nightly count reconciliation on orders and customers, publishing `platform.reconciliation_divergence` | `05-03` §3.4 requires it; §11.4 makes it a gate |
| **Degradation** | Portal serves cached catalogue and **queues bookings**, confirming on recovery | `05-03` §3.4. The queue is the portal's, and it is the one place a surface is permitted to hold state — because it holds an *intent*, not a *fact* (`LB-07` is not breached) |

### 9.4 The `LB-07` clarification this forces

`AR-001` `LB-07` says a portal holds no authoritative state. `05-03` §3.4 requires the portal to
queue a booking during an ERP outage. **These are compatible and the reconciliation is worth
stating**: the queued booking is an *unaccepted intent*, not a service order. It has no order
number, appears in no report, and is either accepted by the ERP on recovery — becoming a real
order — or expires and is shown to the customer as failed. **The rule is that the portal may hold
an intent it has not yet been able to submit; it may never hold a fact.**

---

## 10. Integration Lifecycle and Governance

### 10.1 The stages

| Stage | Gate to leave it | Evidence |
|---|---|---|
| **S1 Proposed** | Registered with an `INT-nnn`, an owning module, a pattern and a priority | Row in the register (§10.2) |
| **S2 Designed** | **ICD issued** (`IN-004`), ACL specified, fallback named, `AP-012` disclosure row **Determined** | ICD + `AP-012` row |
| **S3 Built** | Connector merged; contract tests green; fixtures recorded | `IN-008` §5 |
| **S4 Certified** | Sandbox certification passed with the counterparty | `IN-008` §7 |
| **S5 Live** | Monitoring, alerting and fallback drill all in place | `05-03` §7 dashboard + one drill |
| **S6 Deprecated** | Replacement live; consumers migrated; notice served | `IN-005` §7 |
| **S7 Retired** | Credentials revoked; egress allow-list entry removed; data retention decided | `IN-005` §7.5 |

> **`LC-01` — the S2→S3 gate is where `AP-08` bites.** `AP-012` `DS-01`'s default is refusal: an
> integration may not carry personal data while its disclosure register rows are `Undetermined`.
> **Nine of 53 counterparties are `Determined`.** The three W3 couriers — Pathao, RedX,
> Steadfast/Sundarban — carry customer name, phone and address and are `Undetermined`, which
> **blocks W3 pick-and-drop**. This document does not soften that gate; it makes it a stage.

### 10.2 The integration register

`M28` owns *"the register and the connector shape for all 47"*. This document specifies what a row
must carry. **It is a register, not a table in a document** — the `AR-009` §9.1 lesson applied to
integrations.

| Field | Why |
|---|---|
| `INT-nnn`, name, counterparty legal entity | Identity |
| **Pattern** (P1…P5) | IP-03; determines failure semantics |
| Direction, owning module, consuming modules | Ownership and blast radius |
| Priority, wave | Sequencing |
| **ICD reference** (`IN-004` section) | S2 gate |
| **ACL implementation** and its repository location | AC-09 |
| **Timeout, retry, breaker and bulkhead settings** | §7.1 — per counterparty, not global |
| **Fallback** + last drill date | NFR-050, FB-02 |
| **Credential reference** (vault path) + expiry | IP-07; `platform.credential_expiring` |
| **`AP-012` disclosure status** (`Determined` / `Undetermined`) | LC-01 |
| **Residency position** — does any field cross a border | NFR-086, NFR-099 |
| **Processor contract** reference | NFR-098 |
| Sandbox availability and credential set | `IN-008` §6 |
| Health, error rate, latency (live) | `05-03` §7 |

### 10.3 The measured state of the register today

| Measure | Count |
|---|---:|
| `INT-nnn` identifiers declared in `05-03` §2 | **47** |
| Contiguous `INT-001`…`INT-047`, no gaps, no duplicates | ✅ |
| Technology assignments in Tech Stack §12.2.4 | **47** — complete |
| `P0` integrations | **13** — counted from `05-03` §2's rows, **not** from its summary, which states 12 (`PE-A-01`) |
| Integrations cited in **only two files** in the whole estate (`05-03` and Tech Stack) | **8** — `INT-016`, `INT-018`, `INT-022`, `INT-029`, `INT-030`, `INT-031`, `INT-032`, `INT-042` |
| Integrations with an ICD | **0** before this category; **`IN-004` issues 14** |
| Integrations with a `Determined` disclosure register | **9 of 53 counterparties** (`AP-012`) |
| Integrations with a **tested** fallback | **0** |

> **The eight thinly-cited integrations are not a defect; they are a signal.** An integration named
> in the catalogue and the technology map, and nowhere else, has no module specification asserting
> what it is *for*. Six of the eight are `INT-029`…`INT-032` — the managed-services monitoring
> stack. `IN-004` §11 records them as **ICD-deferred with a stated review wave**, rather than
> writing an ICD against a purpose no specification states.

### 10.4 Registration rules

| # | Rule |
|---|---|
| **IR-01** | A connector may not merge before its `INT-nnn` row exists (register-first, `PG-01` parity) |
| **IR-02** | An `INT-nnn` is **permanent**. A replaced counterparty gets a new number; the old row is retired, never reused |
| **IR-03** | An integration with **no declared fallback and priority P0** fails CI (`FF-40`) |
| **IR-04** | An outbound destination not on the **Z6 allow-list** cannot be reached, and adding one is a recorded change (`AR-001` §8.1) |
| **IR-05** | Every credential is vault-referenced with an expiry; **no credential in code or configuration** (IP-07, NFR-062) |
| **IR-06** | The register is regenerated and diffed at every wave gate. An undeclared change is a **gate failure** (`AR-009` G-06 parity) |

### 10.5 Fitness functions this document adds

`AR-012` v1.1 registers `FF-01`…`FF-37` (`FF-36`/`FF-37` added for Category 03). These continue the sequence and are contributed back to it.

| # | Check | Scope | Timing | Enforcement |
|---|---|---|---|---|
| **FF-38** | Every module path in a `§12` API table resolves to an operation in an `IN-002` contract, and vice versa | 1,187 operations | CI | Fail |
| **FF-39** | Every path consumed by a portal `§12.5` table is declared by exactly one module | 140 paths | CI | Fail |
| **FF-40** | Every `P0` integration row has a fallback and a drill date within the current wave | **13** | Wave gate | Fail |
| **FF-41** | No source file outside a registered ACL imports a counterparty SDK or issues a direct external HTTP call | All | CI static analysis | Fail |
| **FF-42** | No synchronous external call occurs inside a database transaction (`PT-02`) | All | CI static analysis | Fail |
| **FF-43** | Every state-changing operation in a contract declares `Idempotency-Key` as required | 1,187 | CI, from the contract | Fail |
| **FF-44** | Every outbound destination is on the Z6 allow-list | All | Runtime + CI config check | Alert + fail |
| **FF-45** | No API path segment is a module code (`PN-05`) | 978 | CI | Fail after W1 |

---

## 11. The Reconciliation, and the Remediation It Requires

### 11.1 What was measured

| # | Measure | Count |
|---|---|---:|
| M-01 | Distinct API paths declared by the 67 modules | **978** |
| M-02 | Distinct `(method, path)` operations | **1,187** |
| M-03 | Rows in module API tables | 987 |
| M-04 | Distinct second path segments (de facto resource families) | **219** |
| M-05 | Paths under one of the twelve declared families | **38 (3.9%)** |
| M-06 | Paths declared by **more than one** module | **6** |
| M-07 | Distinct paths consumed by the 12 portals | **140** |
| M-08 | Of M-07, declared by no module (normalised on `{param}`) | **100 (71.4%)** |
| M-09 | Of M-08, in a resource family that exists in **no** module | **55**, across **26 resource families** |
| M-10 | Distinct events consumed by the 12 portals | **102** |
| M-11 | Of M-10, published by no module | **69 (67.6%)** |
| M-12 | Distinct method-cell strings in module API tables | **20**, using **3 different separators** plus one `Various` |
| M-13 | Modules whose API surface is at `§12.5` / at `§12.4` | **46 / 21** |
| M-14 | Non-markdown artefacts in the entire four-repository estate | **0** |

### 11.2 The six contested endpoints (M-06)

Two modules each declare these, with no adjudication in `AR-005`:

| Path | Claimants | Likely resolution |
|---|---|---|
| `/api/v1/assets`, `/api/v1/assets/{id}` | **M17** (Device & Customer Asset Registry) · **M49** (Fixed Assets & Capital Investment) | **Different resources with the same name.** A customer's device and a capitalised fixed asset are not one thing. `/api/v1/customer-assets` and `/api/v1/fixed-assets` |
| `/api/v1/requisitions`, `/api/v1/requisitions/{id}/approve` | **M16** (Procurement) · **M58** (Talent Acquisition) | Same. A purchase requisition and a hiring requisition. `/api/v1/purchase-requisitions` and `/api/v1/hiring-requisitions` |
| `/api/v1/campaigns` | **M09** (Warranty — recall campaigns) · **M35** (Marketing campaigns) | Same. `/api/v1/recall-campaigns` and `/api/v1/marketing-campaigns` |
| `/api/v1/catalogue/search` | **M37** (Catalogue) · **M62** (Data Platform) | **Genuinely contested.** M37 owns the catalogue; M62 owns search infrastructure. **M37 owns the endpoint; M62 provides the index.** Referred to `AR-005` |

> This is `AR-008` §3's ambiguous-noun ruling reaching the API surface. Three of the four are the
> same defect class as `claim.submitted` vs `warranty_claim.submitted`.

### 11.3 The three classes of consumer-side gap (M-08, M-11)

Following `AP-01`'s taxonomy, because it is the right one:

| Class | Paths | Events | Remedy |
|---|---:|---:|---|
| **Same thing, two names** | ~45 (a module declares the resource family, the portal names a variant) | ~14 (`estimate.issued`/`service_order.estimated`, `invoice.issued`/`invoice.created`, `sla.at_risk`/`sla.warning`, `payment.received`/`payment.executed`) | **Correct the consumer to the producer's name.** Free today |
| **Coarse projection** | 0 | ~4 (`service_order.status_changed`, `consignment.status_changed`, `claim.status_changed`, `lead.status_changed`) | **Decide, then document, the projection.** §9.3 |
| **Genuinely absent** | **55**, across 26 resource families | **~51** | **Register, or delete the consuming specification's claim.** Not free at any point |

**The 26 resource families with no module endpoint at all:** `analytics` `asn` `assist` `audits`
`availability` `brands` `capa` `cash` `certificates` `contact` `customer-360` `deal-registrations`
`dispatch` `feedback` `findings` `mp` `notifications` `payments` `qc` `receipts` `rfqs` `riders`
`safety` `sla` `sync` `track`

Three of these are not absent but **renamed**: `sync` (M28 declares `/api/v1/platform/sync`),
`analytics` (M25/M62 declare `/api/v1/bi/*`), `track` (M01 declares `/api/v1/tracking/{token}`).
**Twenty-three are real.** `/api/v1/mp/*` alone is the entire marketplace seller surface for P07 —
fifteen paths, none declared by M12.

### 11.4 Remediation plan

| # | Action | Owner | Wave | Blocks |
|---|---|---|:--:|:--:|
| **RI-01** | **Ratify `IN-001-D-01`** (resource-scoped paths; families as policy) | Design Authority | **W0** | ✔ everything below and all of `IN-002` |
| **RI-02** | Correct the family tables in `05-03` §5.1, `AR-001` §7.1, Tech Stack §12.2.2 | Enterprise Architecture | **W0** | RI-03 |
| **RI-03** | Re-prefix the 38 consumer-scoped paths; expand the ~40 module-code namespaces (`PN-05`) — **executed jointly with `AR-009` RM-03** | Enterprise Architecture | **W1** | `IN-002` |
| **RI-04** | Adjudicate the 6 contested paths in `AR-005` | Design Authority | **W1** | `IN-002` |
| **RI-05** | Reconcile the 100 portal-consumed paths: rename, project, or register — **one disposition per path, recorded** | Integration Architect + module owners | **W1** | P01–P12 build |
| **RI-06** | Reconcile the 69 portal-consumed events — handed to `IN-003` §8 with `AR-009` RM-04 | `IN-003` owner | **W1** | Every portal |
| **RI-07** | **Close the CON-03 gap first** — 12 endpoints and 8 webhooks, before any other portal | M01, M03, M20, M33, M37, M10 | **W1** | CON-03 is live at W1 |
| **RI-08** | Normalise the method column to one separator across 67 specifications (M-12) | Enterprise Architecture | W1 | Contract generation |
| **RI-09** | Normalise `§12` sub-section numbering to one layout (M-13) | Enterprise Architecture | W1 | Extraction reliability |
| **RI-10** | Publish the integration register per §10.2 and populate all 47 rows | M28 owner | **W1** | S2 gate for every integration |
| **RI-11** | Enable `FF-38`…`FF-45` | Platform Engineering | W1–W2 | Prevents recurrence |

> **RI-05 and RI-06 are larger than `PGD-000` records.** One hundred paths and sixty-nine events,
> each needing an owner, a disposition and — where genuinely absent — a design. This is the same
> class of understatement `AR-009` raised as `PGD-A3-15` for `IN-003`. Raised here as **`IN-A-01`**
> and referred to `GV-007`.

---

## 12. Observability

| # | Requirement | Basis |
|---|---|---|
| **OB-01** | `correlation_id` is injected at Kong on every inbound request and propagated across every hop, including into event `correlation_id` and outbound calls | `API-09`, `NFR-092` (§7 sense — **the tracing one**, per `AP-02`) |
| **OB-02** | Every outbound external call is logged with counterparty, endpoint, latency, outcome and **the field set sent** (IP-10, `AP-012` §4.8) | Egress audit |
| **OB-03** | Every integration reports availability, throughput, latency p50/p95/p99, error rate, queue depth, DLQ count and breaker state | `05-03` §7, IP-06 |
| **OB-04** | **Outbox depth *and age*** are both alerted. Age is the leading indicator | `AR-009` §5.4 |
| **OB-05** | A trace is retrievable end to end by correlation id through `/api/v1/platform/trace/{correlation_id}` | `M28` §12.5 |
| **OB-06** | Credential expiry alerts at **30 and 7 days** | `05-03` §7, `AP-005` `AUT-IPF-15` |
| **OB-07** | **A secret never appears in a log, a trace, a DLQ entry or an error body** | IP-07, NFR-062, `AP-004` `SIG-08` |

> **`OB-02` is where minimisation becomes auditable.** `IP-10` says data leaving the company is
> minimised and logged. Logging *that* a call was made is not logging *what left*. `AP-012`'s
> field-level registers are the specification of what may leave; `OB-02` is the record of what did.

---

## 13. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `IN-001-D-01` | API path scoping | Consumer-scoped families as path prefixes · **Resource-scoped paths, families as policy** · Both with gateway rewriting | **Resource-scoped** | 95.5% of the declared surface is already resource-scoped; consumer-scoped paths encourage the exact shortcut `API-10` forbids; a 13th audience would otherwise duplicate every operation | 38 paths re-prefixed; three published family tables corrected; families become Kong consumer groups and OpenAPI tag groups |
| `IN-001-D-02` | What triggers failover | Monitoring window · **Circuit-breaker state** · Manual | **Breaker state** | A 5-minute detection window cannot produce a 2-minute failover; the two instruments have different jobs | `M28` `AC-13` satisfied; `05-03` §7 reclassified as alerting; closes the architectural half of `AP-06` |
| `IN-001-D-03` | Latency budgets spanning a third party | One end-to-end number · **Internal budget + per-rail expectation** | **Two numbers** | `NFR-042`'s 3 s cannot hold against a rail whose own guidance sets a 30 s timeout | `05-06` correction raised as `IN-A-05`; per-rail figures published in `IN-004` |
| `IN-001-D-04` | REST maturity | Level 2 · Level 3 (HATEOAS) | **Level 2** | Hypermedia costs client complexity for a closed, generated, versioned contract set with no discovery problem | Stated as a deliberate departure so it is not later read as an omission |
| `IN-001-D-05` | Canonical data model | Build a canonical model · **Per-integration ACL** · Neither | **Per-integration ACL** | A canonical model across 47 counterparties becomes the union of everyone's requirements and is owned by nobody. The estate's canonical model is `AR-008`'s **domain** model; the ACL maps to it | `AC-01`…`AC-11`; no canonical-model project |
| `IN-001-D-06` | Inbound webhook trust | Trust the signed body · **Signature + read-back** | **Read-back** | Both SSLCOMMERZ's published integration requirement and bKash's `create→execute→query` flow assume it; a forged `payment.received` is a direct fraud vector | `PT-05`; `IN-007` §6 makes it per-rail |
| `IN-001-D-07` | Where a fallback is decided | Per module · **Per integration, in the register, with a drill** | **Per integration** | `NFR-050` is per integration; a fallback nobody has exercised is not a fallback | `FB-01`…`FB-05`; `FF-40` |
| `IN-001-D-08` | OpenAPI version | **3.1.0 now** · 3.2.0 now · mixed | **3.1.0 now, 3.2.0 reviewed at the W2 gate** | The register row, `AS-07` and three published documents name 3.1; `PG-01` is register-first. 3.2 is additive, so the move is cheap and deliberate later | §2.4a; `AR-013` radar item |

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | **Ratify `IN-001-D-01`?** Without it `IN-002` cannot fix a base path, and 1,187 operations would be written against a convention that then changes | Design Authority | **W0 — blocking** | All of `IN-002` |
| Q-02 | Who owns the **55 genuinely-absent portal endpoints**? Several — the whole `/api/v1/mp/*` surface — imply module scope nobody has costed | Solution Architect + module owners | **W1** | P07, P12, P10 |
| Q-03 | Is the **projection channel** (§9.3) a new platform capability or a per-module projector? | Chief Architect | **W1** | CON-03, P01 |
| Q-04 | Are the **three W3 courier disclosure rows** determined in time, or does W3 pick-and-drop move? (`AP-08`) | Legal Counsel | **W3 − 3 months** | `INT-024`…`026`, `G3-07` |
| Q-05 | Does `INT-003` get a **second card acquirer**, or does `NFR-048` restate to the aggregate payment path? (`AP-06`) | CTO + CFO | **W3** | `IN-007`, `FB-05` |
| Q-06 | Is there **any machine API** for NBR IVAS Mushak-9.1 submission, or is `INT-038` permanently a manual portal filing from a generated return? | Head of Tax + CTO | **W4 − 3 months** | `IN-004` §7, `INT-038` |
| Q-07 | Which **bank** is the BEFTN sponsor, and what is *its* file specification? The counterparty is the bank, not Bangladesh Bank | CFO + Treasury | **W5 − 4 months** | `IN-004` §8, `CD-100` |
| Q-08 | Does the **PDPA penalty basis** change `GV-008`'s risk budget? (`IN-A-08`) | Legal Counsel + CFO | **W2** | `GV-008`, `SC-005` |
| Q-09 | Is `IN-002`'s 1,187-operation authoring effort funded? It is in no plan (`IN-A-01`) | Programme Director | **W0** | Every portal and partner |

---

## 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The API surface is **measured**, by a reproducible method | §2.2 script; §11.1 — 978 / 1,187 counted |
| AC-02 | The producer/consumer contradiction is measured on **both** halves | §11.1 M-08 (100 paths), M-11 (69 events) |
| AC-03 | The family-vs-resource contradiction is **ruled**, with its cost and timing | §4.3, §4.4 |
| AC-04 | Five patterns have a **selection rule**, not merely a description | §5.1 |
| AC-05 | Idempotency has semantics, not only a required header | §6 |
| AC-06 | The resilience ladder is specified with **per-counterparty** values | §7.1, §7.2 |
| AC-07 | `AP-06`'s architectural half is ruled | §7.6, `IN-001-D-02`, `IN-001-D-03` |
| AC-08 | The anticorruption obligation is explicit and testable | §8.2 |
| AC-09 | The CON-03 contract's gap is measured and given an architecture | §9.2, §9.3 |
| AC-10 | An integration lifecycle with gates and a register exists | §10 |
| AC-11 | Every claim about a statute, standard or vendor version carries a verification date | §2.4 — three version-currency findings raised |
| AC-12 | A remediation plan with owners, waves and blocking flags exists | §11.4 |

**Definition of done.** Complete when every criterion is met, `IN-001-D-01` is ratified (Q-01),
`RI-01`…`RI-04` are executed, and `PGD-000`'s `IN-001` row carries a fresh enumeration timestamp.
**`IN-001` does not close `AP-01`, `AP-04`, `AP-05` or `AP-06` alone** — `IN-003`, `IN-006`,
`IN-005` and `IN-007` respectively must issue.

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `AR-001` §7.1, §7.2, §8.1 | Twelve families, five patterns, six trust zones — **§4.3 corrects §7.1's realisation** |
| Upstream | `AR-009` | Outbox, envelope, delivery semantics; the 988 producer-side measurement |
| Upstream | `AR-002` | System-of-record boundary; controller/processor position per data class |
| Upstream | `AR-005` | Where the 6 contested endpoints are adjudicated |
| Upstream | `GV-002` | The Design Authority that must ratify `IN-001-D-01` |
| Downstream | **`IN-002`** | Base path, error envelope, idempotency, scope declaration — all fixed here |
| Downstream | **`IN-003`** | The 69 unpublished portal-consumed events |
| Downstream | **`IN-004`** | §7.2 timeouts, §8 ACL obligations and §10.2 register fields are every ICD's common clauses |
| Downstream | **`IN-005`** | Family-as-consumer-group, versioning, the scope vocabulary |
| Downstream | **`IN-006`** | `PT-05` read-back, `/hooks/v1/*` authentication |
| Downstream | **`IN-007`** | §7.6's rulings applied to the payment rails |
| Downstream | **`IN-008`** | §5, §6, §7 are the contract-test surface |
| Downstream | `SC-002` | The API surface this threat model covers |
| Downstream | `PE-001`, `PE-005` | Z6 egress, gateway and broker deployment |
| Downstream | `QA-005` | Contract-test layer |
| Lateral | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` | §5.1 family table corrected by `IN-001-D-01`; §7 reclassified by `IN-001-D-02` |
| Lateral | `../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M28_*.md` | The platform that implements this architecture |
| Lateral | `../../project_content/15_Integration_and_Developer_Content/AP-001…012` | Developer content written against these contracts |

---

## 17. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`./IN-002_API_Specification_OpenAPI_Contracts.md`](./IN-002_API_Specification_OpenAPI_Contracts.md) ·
[`./IN-003_Domain_Event_Catalogue_and_Schema_Registry.md`](./IN-003_Domain_Event_Catalogue_and_Schema_Registry.md) ·
[`./IN-004_Interface_Control_Documents.md`](./IN-004_Interface_Control_Documents.md) ·
[`./IN-005_API_Governance_Versioning_and_Deprecation_Standard.md`](./IN-005_API_Governance_Versioning_and_Deprecation_Standard.md) ·
[`./IN-006_Webhook_Callback_and_Partner_Push_Specification.md`](./IN-006_Webhook_Callback_and_Partner_Push_Specification.md) ·
[`./IN-007_Payment_and_Financial_Gateway_Integration_Design.md`](./IN-007_Payment_and_Financial_Gateway_Integration_Design.md) ·
[`./IN-008_Integration_Test_Sandbox_and_Certification_Specification.md`](./IN-008_Integration_Test_Sandbox_and_Certification_Specification.md) ·
[`../02_Architecture_and_Design/AR-001_Software_Architecture_Document.md`](../02_Architecture_and_Design/AR-001_Software_Architecture_Document.md) ·
[`../02_Architecture_and_Design/AR-009_Event_Driven_Architecture_and_Messaging_Design.md`](../02_Architecture_and_Design/AR-009_Event_Driven_Architecture_and_Messaging_Design.md)

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md` ·
`../../1000fix_ERP_Module/03_Modules/**/M*.md` §12 (all 67) ·
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P*.md` §12 (all 12) ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §12.2 ·
`../../project_content/_AUDIT/AUDIT-016_Category_15_AP_Content_Audit.md` ·
`../../project_content/15_Integration_and_Developer_Content/AP-001…AP-012`

**External sources**

| Source | What it establishes | Verified |
|---|---|---|
| OpenAPI Specification v3.2.0 (OpenAPI Initiative, released September 2025) | Current stable OAS; additive over 3.1 | 2026-08-18 |
| AsyncAPI Specification 3.0 / 3.1 | Channel and message description for event APIs | 2026-08-18 |
| RFC 9457 *Problem Details for HTTP APIs* (July 2023; obsoletes RFC 7807) | The industry error form; `AP-006` `O-02` mapping | 2026-08-18 |
| `draft-ietf-oauth-v2-1-15` *The OAuth 2.1 Authorization Framework* (2 March 2026) | **Internet-Draft, not an RFC.** PKCE for all clients; no implicit; no ROPC; exact redirect matching | 2026-08-18 |
| Standard Webhooks specification | `webhook-id` / `webhook-timestamp` / `webhook-signature`; HMAC-SHA256 over `id.timestamp.body`; 300 s tolerance | 2026-08-18 |
| Hohpe & Woolf, *Enterprise Integration Patterns* | Messaging gateway, dead letter channel, idempotent receiver, claim check, anticorruption layer | 2026-08-18 |
| Nygard, *Release It!* | Timeout, circuit breaker, bulkhead, fail fast | 2026-08-18 |
| bKash Tokenized Checkout API Integration Guide | `token/grant` → `create` → `execute` → `payment/status` → `refund`; **30 s client timeout**; sandbox `sandbox.bka.sh`, production `pay.bka.sh` | 2026-08-18 |
| SSLCOMMERZ developer documentation (v4) | IPN with MD5 `verify_sign` **plus mandatory Transaction Validation API** call before treating a payment as complete | 2026-08-18 |
| Nagad Merchant API Integration Guide | Merchant RSA key pair; merchant signs with its private key, encrypts with Nagad's public key, verifies responses with Nagad's public key | 2026-08-18 |
| Bangladesh Bank, *BEFTN Operating Rules* | Fixed-width file: file header, batch header, entry detail, control records; three-digit Standard Entry Class codes; participants are banks; T+1 clearing | 2026-08-18 |
| NBR VAT Online / IVAS (`vat.gov.bd`), Mushak-9.1 | Monthly return, filed by the 15th, through the portal; no publicly documented machine API | 2026-08-18 |
| Personal Data Protection Ordinance 2025, as amended by Ordinance No. 23 of 2026 (5 February 2026) | Enforcement deferred ~18 months to on or about 13 May 2027; turnover-proportional penalties; localisation narrowed to restricted data and CII | 2026-08-18 |

> Every relative link above was resolved against the filesystem before issue (`PG-M9`). Links to
> `IN-002`…`IN-008` resolve because those documents are issued in the same change.

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Integration Architecture | Initial issue. Measures the API surface at **978 paths / 1,187 operations**, and the consumer-side gap at **100 of 140 portal paths (71.4%)** and **69 of 102 portal events (67.6%)** — extending `AP-01` from a 21-name sample. Rules the family/resource contradiction (`IN-001-D-01`), the failover trigger (`IN-001-D-02`) and third-party latency budgets (`IN-001-D-03`). Raises three version-currency findings including the PDPA instrument and penalty basis (`IN-A-08`) | *Pending — Design Authority not constituted (`PGD-A1-09`)* |

---

*`IN-001` · Category 04 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
