---
id: AP-001
title: Developer Portal Information Architecture
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
reviewers: [CTO, Solution Architect, Content Design Lead, Security Lead, Commercial Director, Account Management Lead, Marketplace Operations]
approver: Programme Content Lead with CTO
content_class: E
purpose: >
  The structure of the external and internal developer surface — what sections exist, what lives in
  each, which pages are generated and which are authored, who may see what, and the golden path that
  takes a partner developer from first arrival to first successful API call. Without it the eleven
  other Category 15 files have no place to be published, `FR-IPF-015` is built as a documentation
  dump rather than a surface, and every brand partner, corporate client and courier integrates by
  emailing the platform team — which is the integration support load `05-03` exists to prevent and
  which the company has not staffed.
traces_to: [M28, M28 FR-IPF-015, M28 FR-IPF-017, M28 FR-IPF-019, M28 FR-IPF-020, M28 FR-IPF-032, M28 Q-07, 05-03, 05-03 §5.1, 05-03 §5.2, PS-02, CG-003, CG-004, CG-009, CG-010, CG-011, AP-002, AP-003, AP-004, AP-005, AP-006, AP-007, AP-008, AP-009, AP-010, AP-011, AP-012, EO-003, EO-007, HC-001, RF-003]
priority: P2
wave: W4
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M28_Integration_API_and_Event_Platform.md §3.1 items 6 and 30, §5.2 FR-IPF-015…FR-IPF-020, §12.5 platform endpoints, §18 Q-07 — the developer portal as the self-service surface that keeps the platform team off the critical path
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md §5.1 twelve API families and their auth models; §5.2 API-01…API-12; §3 the CON-03 portal contract
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-009_Content_Template_Register.md §3 — Category 15 uses template 1 with an endpoint/event reference table and an error catalogue table
    verified: 2026-08-18
    class: P1
  - source: Developer-portal information-architecture practice 2026 — a linear getting-started path to first successful call, one catalogue across every gateway, role-based visibility, docs generated from OpenAPI, built-in sandbox, audit logs from day one. https://buildwithfern.com/post/information-architecture-best-practices-documentation and https://www.mintlify.com/library/api-developer-portals-for-enterprise
    verified: 2026-08-18
    class: P3
supersedes: none
review_due: 2027-02-18
---

# Developer Portal Information Architecture

| Item | Value |
|---|---|
| Surface governed | The 1000FiX developer portal — external partner-facing and internal module-team-facing |
| Owning capability | `M28` `FR-IPF-015` developer portal · `FR-IPF-017` usage analytics · `FR-IPF-019` sandbox · `FR-IPF-020` partner onboarding |
| Audiences served | 7 (§3) |
| Top-level sections | 9 (§4.2) |
| Page types | 14 (§4.3) |
| Access tiers | 4 (§4.5) |
| Generated vs authored | 6 page types generated, 8 authored (§4.7) |
| Language | English only — `CG-010` §3.2 |
| Wave | W4 registered · **first consumed W3** — open item `O-02` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order. §4 carries the substance and is subdivided; the subdivision is
> the only addition and is justified by volume. The endpoint reference table required by `CG-009`
> §3 for this category appears at §4.8 and is deliberately a **surface map, not an endpoint
> catalogue** — the endpoint catalogue is `AP-002`'s and the event catalogue is `AP-003`'s
> (`CP-01`).

---

## 1. Purpose

`05-03` catalogues 47 external integrations and 12 API families. `M28` §3.1 item 6 makes the
developer portal M28's own deliverable and §4 states the reason plainly: the platform team
becoming a bottleneck for all 60 other modules is a **High** category risk, and the mitigation is
self-service. `M28` §7.1 sets the test — *"integration partner: emails for documentation and
credentials → self-serves both from the developer portal."*

**Nothing in the repository says what that surface contains.** `FR-IPF-015` says "API catalogue
with interactive documentation, code samples, changelog and a sandbox, in one self-service
surface" — five nouns, no structure. Five nouns will be built five different ways by whoever
picks the ticket up, and the eleven other files in this category will have no agreed place to
land.

**What stops working without this file.**

| Absent | Consequence |
|---|---|
| Section structure | `AP-002`…`AP-012` are eleven documents with no publication target. They exist as repository markdown and never reach the audience they were written for |
| Access tier model | Either everything is public — including the `AP-012` disclosure register and per-partner rate limits, which are commercially and legally sensitive — or everything is gated, and a prospective brand partner cannot evaluate whether integration is feasible before signing |
| Golden path definition | A partner's first experience is a 22-endpoint reference table (`05-03` §3.2). Time-to-first-call is measured in days, integration projects stall, and the support load lands on a platform team of unstated size |
| Generated-versus-authored boundary | Hand-maintained endpoint pages drift from the OpenAPI specification within one release. `AS-07` requires CI validation of the *specification*; nothing requires the *portal* to be regenerated from it |

**The single sentence this file exists to settle:** a developer arriving at the portal for the
first time, with a signed agreement and no prior contact with 1000FiX, reaches a successful
authenticated call against the sandbox **without speaking to anyone**.

---

## 2. Scope

**In scope.** The information architecture of the developer portal: audience segmentation, the
section tree, the page-type inventory with owner and update trigger, access tiers and what each
tier may see, navigation and naming rules, the golden path, the generated-versus-authored
boundary, version and changelog placement, search behaviour, the surface map of `AP-002`…`AP-012`
onto pages, and the measurement set.

**Out of scope.**

| Out of scope | Owned by | Note |
|---|---|---|
| The endpoint descriptions themselves | `AP-002` | This file says a reference section exists and how it is generated; `AP-002` says what a good description contains |
| Event descriptions and the event catalogue | `AP-003` | Published *into* the Events section defined here |
| Error code catalogue content | `AP-006` | Published into the Reference section |
| Credential issue, scopes, limits | `AP-005` | Published into Authentication |
| Sandbox mechanics and test credentials | `AP-010` | Published into Sandbox |
| Deprecation notices and migration guides | `AP-011` | Published into Changelog |
| Visual design, component library, tokens | `VB-006`, `MM-010` | This file specifies structure, not appearance |
| Portal platform build, hosting, CDN | `M28` `FR-IPF-015` engineering | A content architecture cannot procure a platform — `O-01` |
| Public marketing pages about API capability | Corporate website content set | Master Index §11 — the two sets are deliberately separate and must not be merged |
| Help content for **portal end users** (not developers) | `HC-001` and the `HC-003`…`HC-014` help sets | A brand partner's warranty administrator reads `HC-010`; their developer reads this surface. Different people, different surfaces |
| Commercial terms of API access | `LG-003`, `LG-005`, `LG-006`, `LG-007` | Linked from Legal (§4.2), never restated |

---

## 3. Audience

Seven audiences, and the IA has to serve all seven from one surface without any of them seeing
another's material.

| # | Audience | Population | Arrives from | Needs first |
|---|---|---:|---|---|
| A1 | **Internal module teams** | 67 module builds over 36 months | Internal onboarding | How to publish an API and an event through the framework without a platform ticket (`FR-IPF-057`) |
| A2 | **Portal platform team** (Next.js 15 + Payload CMS 3, CON-03) | 1 team, continuous | `05-03` §3 contract | Field ownership, the 22 core endpoints, the 11 webhooks, reconciliation expectations |
| A3 | **Brand partner integration teams** | 17+ brands (figure unverified — `MD-017`, `00-07` H2-12) | `EO-003` onboarding pack | Whether their existing warranty system can exchange claims, and what it costs them |
| A4 | **Corporate client IT / ITSM teams** | 500–2,000 corporate users across an unknown number of client organisations (`P04` Q-01) | `EO-007` welcome kit, account manager | Estate load format, coverage validation, ticket exchange |
| A5 | **Payment, courier and logistics vendors** | 9 payment + 4 courier/freight integrations | Commercial contract | Callback contract, reconciliation keys, sandbox |
| A6 | **Marketplace sellers with their own systems** | 500–2,000 sellers, small share with systems | `EO-001` onboarding kit | Order and payout endpoints only |
| A7 | **Referral and alliance partners** | `P12` population | `EO-009` kit | Referral link and attribution mechanics |

> **A1 and A2 are the majority of traffic for the first three years.** A3–A7 arrive from W4
> onward. The IA must not be optimised for external partners at the cost of the internal
> audience that uses it every working day — this is the substance of `M28` Q-07 and is handled
> at §4.9 rather than avoided.

---

## 4. Content

### 4.1 The three organising decisions

Everything below follows from three decisions. They are stated first so that a future change to
the tree can be tested against the reason the tree is shaped this way.

| # | Decision | Rejected alternative | Why |
|---|---|---|---|
| **IA-D1** | **One portal, four access tiers** — internal and external audiences share one surface, with visibility controlled per page | Two portals, internal and external | Two portals means two changelogs, two reference sets and guaranteed divergence. `M28` §3.1 item 6 names one developer portal. Divergence between an internal and an external description of the same endpoint is the exact failure `AS-07` exists to stop |
| **IA-D2** | **Generated is the default; authored is the exception** — every page that *can* be derived from the OpenAPI specification, the schema registry or the integration register **is** | Authored reference pages reviewed per release | `FR-IPF-032` already requires the event catalogue to be generated "rather than maintained by hand". Extending that rule to the whole reference surface is what makes 100% OpenAPI coverage (`M28` `AC-08`) mean something a developer can read |
| **IA-D3** | **The golden path is a section, not a page** — "Start here" is a numbered five-step sequence with its own navigation, separate from Guides | A single long "Getting started" page | A first-time integrator and a returning one have different needs. Mixing them produces a page too long for the first and too shallow for the second. Time-to-first-call is the portal's primary measure (§4.10) and it is a property of a *sequence* |

### 4.2 Section tree

Nine top-level sections. The order is the order of a developer's need, not alphabetical and not
organisational.

```
1000FiX Developer Portal
│
├── 1  Start here                       ← the golden path (§4.4). Tier: Public
│     ├── What 1000FiX APIs do
│     ├── Step 1 — Register and get credentials
│     ├── Step 2 — Get a token
│     ├── Step 3 — Make your first call (sandbox)
│     ├── Step 4 — Receive your first webhook
│     └── Step 5 — Go to production
│
├── 2  Guides                           ← task-shaped, authored. Tier: mixed
│     ├── Concepts (envelope, correlation id, idempotency, scopes, pagination)
│     ├── Integration patterns (the five patterns of IP-03)
│     ├── Partner guides ─ Brands  ────────────► AP-007   Tier: Partner-scoped
│     ├── Partner guides ─ Corporate ─────────► AP-008   Tier: Partner-scoped
│     ├── Payments ────────────────────────────► AP-009   Tier: Partner-scoped
│     ├── Webhooks and callbacks ─────────────► AP-004   Tier: Authenticated
│     └── Offline sync (P02/P09/P11 apps) ────► 05-03 §6  Tier: Internal
│
├── 3  API reference                    ← generated from OpenAPI 3.1. Tier: mixed
│     └── one node per API family (05-03 §5.1) ─ 12 families
│           Customer · Technician · Operations · Corporate · Vendor · Seller ·
│           Brand · Logistics · Analytics · Admin · Partner · Webhook receiver
│
├── 4  Events                           ← generated from the schema registry
│     ├── Envelope and consumer rules ──────► AP-003 §4.2
│     ├── Event catalogue (by aggregate) ──► AP-003 §4.5   Tier: mixed
│     └── Platform events ─────────────────► AP-003 §4.6   Tier: Internal
│
├── 5  Authentication                   ← AP-005. Tier: Public (model) / Authenticated (limits)
│     ├── Grant types by audience
│     ├── Scopes
│     ├── Credential lifecycle and rotation
│     └── Rate limits and throttling
│
├── 6  Sandbox                          ← AP-010. Tier: Authenticated
│     ├── What is simulated and what is not
│     ├── Test credentials and test data
│     ├── Forcing an error
│     └── Promotion to production checklist
│
├── 7  Changelog and deprecations       ← AP-011. Tier: Public
│     ├── Release notes by API version
│     ├── Deprecation register (live)
│     └── Migration guides
│
├── 8  Status and support               ← OP-005 status content, OP-001 routing
│     ├── Integration status board
│     ├── Known issues
│     └── How to raise an integration issue
│
└── 9  Legal and data                   ← Tier: mixed
      ├── API terms of use ───────────► LG-003 / LG-005 / LG-006 / LG-007 (linked, never restated)
      ├── What data you receive ──────► AP-012 (counterparty-scoped extract only)
      └── Acceptable use and rate abuse
```

**Why nine and not more.** Every additional top-level section costs every developer a decision
on every visit. Sections 8 and 9 are the two most often argued for merging into a footer; both
are kept because an integration partner in an incident needs section 8 in under five seconds,
and because `AP-012` needs a canonical, linkable home that is not buried under Guides.

**Why "Start here" is section 1 and not a banner.** A banner is dismissed. A numbered section is
a place a developer can be *sent back to* by support — "you are at step 3" is a usable sentence
in a support conversation and a dismissed banner is not.

### 4.3 Page-type inventory

Fourteen page types. Each has one owner, one update trigger and one source of truth. A page type
not on this list is not created without a `RF-006` decision.

| # | Page type | Section | Generated / authored | Source of truth | Owner | Update trigger |
|---:|---|:--:|:--:|---|---|---|
| PT-01 | Golden-path step | 1 | Authored | This file §4.4 | Content Design | Change to auth or onboarding flow |
| PT-02 | Concept page | 2 | Authored | `05-03` §4.1, §4.3, §5.2 | Platform Engineering | Change to a standard `API-01`…`API-12` |
| PT-03 | Task guide | 2 | Authored | `AP-004`, `AP-007`…`AP-010` | Named `AP` file owner | Change to the owning `AP` file |
| PT-04 | API family landing | 3 | **Generated** | `fix_api_registry` | — (automatic) | Any endpoint registered, deprecated or retired |
| PT-05 | Endpoint reference | 3 | **Generated** | OpenAPI 3.1 spec, validated in CI (`AS-07`) | Owning module team | Every deployment |
| PT-06 | Schema / model page | 3 | **Generated** | OpenAPI components | Owning module team | Every deployment |
| PT-07 | Event catalogue entry | 4 | **Generated** | `fix_event_schema` + `AP-003` description fields | Producing module | Schema registration |
| PT-08 | Error code entry | 3 | **Generated** | `AP-006` catalogue, loaded as data | Platform Engineering | New code added |
| PT-09 | Auth / scope page | 5 | Authored | `AP-005` | Platform + Security | Scope model change |
| PT-10 | Rate-limit table | 5 | **Generated** | `fix_api_consumer` policy config | Platform Engineering | Limit change |
| PT-11 | Sandbox page | 6 | Authored | `AP-010` | Platform Engineering | Sandbox capability change |
| PT-12 | Changelog entry | 7 | Authored | `AP-011` templates | Owning module team | Every release affecting a public contract |
| PT-13 | Deprecation register row | 7 | **Generated** | `fix_api_registry` status + `deprecated_at` / `sunset_at` | — (automatic) | Deprecation marked |
| PT-14 | Status / incident notice | 8 | Authored from template | `OP-004`, `OP-005` | Support Lead | Incident or planned maintenance |

**Six generated, eight authored.** The generated six are precisely the six that go stale fastest
and that a human cannot keep correct across 67 modules and nine waves. This is `IA-D2` made
operational.

### 4.4 The golden path

Five steps. The target is stated as a number because a target that is not a number is an
aspiration.

| Step | Page | Developer does | Ends when | Target elapsed |
|---:|---|---|---|---:|
| 1 | Register and get credentials | Registers a consumer, receives sandbox `client_id` and secret (`FR-IPF-016`) | Credentials in hand | ≤ 5 min |
| 2 | Get a token | Exchanges credentials for an access token at `/api/v1/auth/token` | `200` with a token | ≤ 3 min |
| 3 | First call | Calls one read endpoint scoped to their audience against sandbox | `200` with a body | ≤ 5 min |
| 4 | First webhook | Registers an endpoint, triggers a simulated event, verifies the signature | Signature verified locally | ≤ 15 min |
| 5 | Go to production | Works the `AP-010` promotion checklist | Production credentials issued | Days — human-gated |

**Steps 1–4 target ≤ 30 minutes unassisted.** Step 5 is deliberately not self-service: production
credentials for a counterparty that receives customer personal data require the `AP-012`
disclosure row and the `AP-010` promotion gate to be satisfied, and `IP-07` puts credential issue
under the vault and an accountable owner.

**The step-3 endpoint is chosen per audience, not globally.** The first call must return
something the developer recognises as *their* data, because a `200` with an empty array teaches
nothing:

| Audience | First-call endpoint | Why this one |
|---|---|---|
| A2 Portal platform | `GET /api/v1/branches` | Public reference data, non-empty in sandbox, no scope complexity |
| A3 Brand | `GET /api/v1/warranty/claims?status=submitted` | The brand's own queue — proves scoping works on the first call |
| A4 Corporate | `GET /api/v1/contracts` | Proves organisation scoping |
| A5 Payments | `POST /api/v1/payments/confirm` against a seeded pending payment | The only meaningful first action for a gateway |
| A5 Courier | `GET /api/v1/consignments/{id}` | A consignment assigned to them (`EA-07`) |
| A6 Seller | `GET /api/v1/marketplace/offers` | Own offers only |
| A7 Referral partner | `GET /api/v1/partner/referrals` | Own referrals only |

> **`GET /api/v1/partner/referrals` is not in `05-03`.** `05-03` §5.1 registers the Partner API
> family at `/api/v1/partner/*` but §3.2 lists no partner endpoints. The path above is this
> file's **proposal** and is recorded as open item `O-05` rather than presented as fact, per
> `CG-012` and `CM-R8`.

### 4.5 Access tiers

Four tiers. A page carries exactly one.

| Tier | Who sees it | Applied to | Enforcement |
|---|---|---|---|
| **T-Pub** Public | Anyone, unauthenticated | Start here, concepts, auth model, changelog, deprecation register, status | None — but see the disclosure rule below |
| **T-Auth** Authenticated | Any registered consumer in any environment | Sandbox, webhook guide, error catalogue, schema pages | Portal login bound to `fix_api_consumer` |
| **T-Part** Partner-scoped | Consumers of one audience class only | `AP-007` brand guide, `AP-008` corporate guide, `AP-009` payment runbook content, per-consumer rate limits, the `AP-012` extract | Consumer `type` on `fix_api_consumer`; enforced server-side, never by hiding a link |
| **T-Int** Internal | 1000FiX staff and contracted engineers | Offline sync protocol, platform events, admin API family, dead-letter and replay pages | Staff identity via `M29`; not reachable by an external credential under any path |

**The disclosure rule for T-Pub.** A page is public only if every fact on it would be acceptable
in a competitor's hands. That excludes: per-consumer rate limits, the integration register
(`fix_integration_config`), which brands have API integrations, payment gateway account
identifiers, and the full `AP-012` register. It includes the auth *model*, the error *catalogue*
and the deprecation *register*, because a partner evaluating integration feasibility before
contract needs all three, and none of them discloses anything commercial.

**Tiering is authorisation, not navigation.** `API-10` and `EA-11` apply to the portal as much as
to the API: a hidden link is not access control. Every T-Part and T-Int page is server-side
authorised, and the `TS-017` security pack carries a negative case per tier — recorded at §4.10.

### 4.6 Navigation and naming rules

| # | Rule | Reason |
|---|---|---|
| **NAV-01** | Maximum depth is **three levels** below a top-level section | `NFR-077` sets four clicks to any record; the portal holds itself to the same standard |
| **NAV-02** | Section and page names are **noun phrases in sentence case**, matching `CG-003` | The portal is written by engineers; without the rule it acquires "Getting Started With Webhooks (v2)" |
| **NAV-03** | Every business object is named by its `CG-004` controlled term, never by its table name or its Odoo model name | A partner reading `fix.service.order` learns nothing. `CG-004` binds "service order" to the entity; the portal uses the term |
| **NAV-04** | An API family node is named by its **audience**, not its path — "Brand API", not `/api/v1/brand/*` | The path is on the page; the audience is what a developer navigates by |
| **NAV-05** | No page exists in two places in the tree. Cross-links, never duplicates | `CP-01` |
| **NAV-06** | The version selector is **global and persistent**, not per page | A developer working a migration reads eight pages at one version; per-page selectors lose the context on every click |
| **NAV-07** | Deprecated content is **never removed from navigation before sunset**; it is marked, not hidden | `FR-IPF-014` blocks removal while a consumer still calls it. Hiding the documentation while the endpoint lives strands that consumer |
| **NAV-08** | Search returns generated and authored pages in one result set, filtered by the reader's tier | Two search boxes is the most common developer-portal defect and the cheapest to avoid |
| **NAV-09** | Every page carries its **last-verified date** and, where generated, its **source and generation timestamp** | `CM-R8` and `CG-012` applied to a surface where staleness is invisible |
| **NAV-10** | Every reference page links to the guide that uses it, and every guide links to the reference it calls | The single highest-value navigation link in a developer portal, and the one most often absent |

### 4.7 Generated versus authored — the contract

The generated six (PT-04, PT-05, PT-06, PT-07, PT-08, PT-10, PT-13 — seven page *instances* across
six types) are produced by the pipeline below. Authored pages never describe an endpoint, a field
or an event; they describe a **task**.

```
  Module code ──► OpenAPI 3.1 generated (FR-IPF-012) ──► CI validation vs implementation
                                                              │ ✖ divergence → build fails (AS-07)
                                                              ▼
                                            fix_api_registry ──► PT-04, PT-05, PT-06, PT-13
                                                              │
  Schema registration (FR-IPF-025) ──► fix_event_schema ───────► PT-07  (+ AP-003 descriptions)
                                                              │
  AP-006 catalogue (data file) ───────────────────────────────► PT-08
                                                              │
  fix_api_consumer policy ────────────────────────────────────► PT-10
                                                              ▼
                                                    Portal build ──► published
```

**The description problem, stated here and solved in `AP-002`.** Generation produces structure,
not meaning. `M28` §4 records the position: *"OpenAPI generated from code with no authored
descriptions is technically complete and practically unusable."* The pipeline above therefore
carries authored description text **inside** the specification — as `summary`, `description` and
`example` on every operation, parameter and schema — and `AP-002` is the standard those fields
are written to. **Coverage of the specification is measured by CI; coverage of the descriptions
is measured by nobody**, which is open item `O-04`.

### 4.8 Surface map — where each Category 15 file is published

The endpoint/event reference table required by `CG-009` §3 for this category. It maps content to
surface; it does not restate the endpoints, which belong to `AP-002` and the generated reference.

| File | Publishes to | Section | Page type | Tier | Generated? |
|---|---|:--:|:--:|:--:|:--:|
| `AP-001` *(this file)* | The IA itself — not published as a page | — | — | — | — |
| `AP-002` API reference content standard | Governs PT-05 / PT-06 content; not itself published externally | 3 | PT-05 | T-Int | Governs the generator |
| `AP-003` Domain event catalogue descriptions | Events | 4 | PT-07 | T-Auth / T-Int | Yes — descriptions injected |
| `AP-004` Webhook and callback guide | Guides → Webhooks and callbacks | 2 | PT-03 | T-Auth | No |
| `AP-005` Authentication, scopes, rate limits | Authentication | 5 | PT-09, PT-10 | T-Pub / T-Part | Limits table generated |
| `AP-006` Error code catalogue | API reference → Errors | 3 | PT-08 | T-Auth | Yes — from the catalogue data file |
| `AP-007` Brand integration guide | Guides → Partner guides → Brands | 2 | PT-03 | T-Part | No |
| `AP-008` Corporate integration guide | Guides → Partner guides → Corporate | 2 | PT-03 | T-Part | No |
| `AP-009` Payment gateway runbook content | Guides → Payments **(external-safe extract only)** | 2 | PT-03 | T-Part | No |
| `AP-010` Sandbox onboarding | Sandbox | 6 | PT-11 | T-Auth | No |
| `AP-011` Change, deprecation and notice | Changelog and deprecations | 7 | PT-12, PT-13 | T-Pub | Register generated |
| `AP-012` Data sharing and disclosure register | Legal and data → What data you receive | 9 | PT-03 | T-Part | **Extract only** |

> **Two files are published in part, not in whole, and the distinction is load-bearing.**
> `AP-009` is an operational runbook containing failure modes, manual fallbacks and internal
> escalation; only the gateway-facing contract is external. `AP-012` is the complete
> counterparty-by-field register across all 47 integrations; a counterparty sees **their own rows
> only**, which is `EA-01` and `EA-02` applied to documentation. Both extracts are generated from
> the source file, never re-authored, or they diverge — `CP-01`.

### 4.9 The internal-portal question — `M28` Q-07, answered

`M28` Q-07 asks whether a developer portal for **internal** module teams is justified in W1, or
whether internal self-service runs on generated documentation until the marketplace wave needs an
external portal. It is open and addressed to the CTO at "W1 design". This file cannot close it,
but it can remove the false choice inside it.

| Option | What it means | Assessment |
|---|---|---|
| **(a)** Full portal at W1 | Sections 1–9, all tiers, all audiences | Rejected as posed. Sections 6, 7 and 9 have no external audience until W3–W4 and would be built empty |
| **(b)** No portal until W4; internal teams use generated docs | Generated OpenAPI and event catalogue served from CI, no surface | Rejected. Section 4 (Events) and the `FR-IPF-057` self-service story are exactly what internal teams need from W1, and building the surface twice costs more than building it once |
| **(c) Recommended — one surface, phased by section** | Sections 3, 4 and 2-Concepts at **W1**, tier T-Int only. Sections 1, 5, 6, 7 at **W3** with the first external audience. Sections 8, 9 and the partner guides at **W4** | The tree above is the W4 end state; the W1 state is a subtree of it. No section is built twice, and no external section is built before it has a reader |

**Why (c) is a content position and not an engineering one.** `M28`'s W1 deliverable is the
framework; `05-03` §8 lands the first external-partner integrations at **W3** (couriers INT-024…026)
and **W4** (brand and corporate portals). A portal built for external partners at W1 has no
external partners; a portal deferred to W4 leaves the internal audience — the one that mitigates
the bottleneck risk — with nothing for three waves. Recorded as `O-03`.

### 4.10 Measurement

`FR-IPF-017` provides per-consumer usage analytics. Six portal measures, each with a stated
denominator per `CP-11`.

| # | Measure | Definition | Target | Reported |
|---|---|---|---|---|
| **PM-01** | **Time to first successful call** | Median elapsed from consumer registration to first `2xx` on any sandbox endpoint | ≤ 30 min for steps 1–4 | Per consumer cohort, monthly |
| PM-02 | Golden-path completion | Consumers reaching step 4 ÷ consumers registered | ≥ 80% | Monthly |
| PM-03 | Self-service rate | Consumers reaching production without a support ticket ÷ consumers onboarded | ≥ 70% by W7 | Per wave |
| PM-04 | Documentation-caused tickets | Integration tickets whose resolution was "answered by an existing page" ÷ integration tickets | ≤ 15% | Monthly, from `M66` |
| PM-05 | Generated-page staleness | Generated pages whose source timestamp is older than the current release ÷ generated pages | **Zero** | Per deployment |
| PM-06 | Tier-leak negative tests passing | `TS-017` cases proving a T-Part consumer cannot reach another partner's page ÷ cases | **100%** | Per wave |

**PM-01 is the portal's primary measure** and the only one this file would defend if the others
were cut. `M28`'s self-service KPI ("APIs and events published without platform-team involvement
— 95% by W8") measures the internal half; PM-01 measures the external half.

**PM-06 requires `TS-017` to carry portal cases.** `TS-017` as registered covers access-control
matrix verification, data-scope isolation, consent, residency and audit-log completeness — the
*application*. The developer portal is a second surface with the same scoping obligation and is
not in that scope today. Recorded as `O-06`.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `M28` `FR-IPF-015` | The portal is M28's build. This file specifies its content structure; it does not deliver it |
| `M28` `FR-IPF-016`, `FR-IPF-019` | Steps 1 and 3 of the golden path are consumer self-registration and sandbox. Without both, the golden path stops at step 2 |
| `M28` `FR-IPF-012`, `FR-IPF-032` | The generated six exist only if OpenAPI generation and the event catalogue generator exist |
| `M29` `/api/v1/auth/token` | Golden-path step 2 |
| **`AP-002`…`AP-012`** | The eleven files this surface publishes. A section with no content is worse than an absent section |
| `CG-003`, `CG-004` | `NAV-02` and `NAV-03` are direct applications |
| `CG-009` §3 | Template allocation and the required additional tables |
| `CG-010` §3.2 | English-only; there is no Bengali developer surface and none is planned |
| `CG-011` | The portal is a web surface and `PS-04` WCAG 2.1 AA applies to it — see `O-07` |
| `OP-004`, `OP-005` | Section 8 content is owned by Operations, published here |
| `LG-003`, `LG-005`, `LG-006`, `LG-007` | Section 9 links; terms are never restated here (`CP-01`) |
| `EO-001`, `EO-003`, `EO-005`, `EO-007`, `EO-009` | The onboarding kits that route each external audience here. A kit with no landing link and a portal with no inbound route both fail |
| `HC-001` | The help-centre IA. Two information architectures for two audiences must not use contradictory section names for the same thing |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per wave gate, and on the addition of any new external audience |
| Trigger for out-of-cycle review | A new API family in `05-03` §5.1 · a new top-level section proposed · resolution of `M28` Q-07 · a change to `FR-IPF-015` scope · the first external partner onboarding retrospective |
| Owner | Platform Engineering Lead (`CG-002` §6 names it accountable for Category 15) |
| Change control | Section-tree changes (§4.2) and tier changes (§4.5) require CTO and Content Design Lead approval and a `RF-006` entry. Page-type additions require a `RF-006` entry only |
| Version pinning | Pinned to **API version**, per `CG-006` §5 for `AP` content — not to a wave |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **No developer-portal platform is selected, budgeted or provisioned.** `M28` §16.2 folds the portal into `CD-126` (`cd_api_layer`, 8 PW) alongside the API registry, OpenAPI generation, versioning, envelope, idempotency and credential management. **A nine-section surface with four access tiers and a generated pipeline is not a share of 8 PW.** This is a scope and estimate exposure, not a content gap | CTO with Programme Manager | **W1 design — before `CD-126` is sized** |
| **O-02** | **Registered W4; first consumed W3.** `05-03` §8 lands INT-024…026 (Pathao, RedX, Steadfast/Sundarban) in **W3**, each bidirectional REST + webhook with an external development team. `AP-004` and `AP-005` are also registered W3. A W4 surface cannot publish W3 content. This is the same defect `AUDIT-010` §7 and `AUDIT-014` TS-02 recorded across four prior categories — **the register is sequenced by when a file's subject matures, not by when its consumer needs it** | Programme Content Lead with Platform Engineering Lead | **W3 minus 2 months — register correction** |
| **O-03** | **`M28` Q-07 is unresolved.** §4.9 proposes option (c) — one surface, phased by section, T-Int at W1. It is a recommendation, not a decision, and `CD-126` cannot be sized without it | CTO | **W1 design** |
| **O-04** | **Description coverage is unmeasured.** `M28` `AC-08` measures *specifications*, not *descriptions*. An endpoint with `summary: "Post service order"` passes `AS-07`, passes CI and fails every reader. `AP-002` sets the standard; nothing counts conformance to it | Platform Engineering Lead | **W3 — with the first external consumer** |
| **O-05** | **The Partner API family has no registered endpoints.** `05-03` §5.1 registers `/api/v1/partner/*` for `P12` and external partners; §3.2's 22-endpoint core surface contains none. `GET /api/v1/partner/referrals` at §4.4 is this file's proposal, unregistered | Platform Engineering with `M40` owner | W7 — before `P12` |
| **O-06** | **`TS-017` does not cover the developer portal.** PM-06 requires negative cases proving a T-Part consumer cannot reach another partner's pages. The portal is a second scoped surface and is outside the registered `TS-017` scope | QA Lead with Security Lead | W4 |
| **O-07** | **Accessibility obligation undeclared.** `PS-04` and `NFR-073` make WCAG 2.1 AA contractual for "all web portals". Whether the developer portal is a *portal* in that sense has never been decided. `CG-011` applies to user-facing content and this surface is user-facing to seven audiences | Content Design Lead with CTO | W3 |
| **O-08** | **No owner is named for section 8 or the changelog cadence.** `OP-004` and `OP-005` own incident and status *templates*; nobody owns publishing them to a developer audience, and `AP-011` owns notice *content*, not the release cadence | Support Lead with Platform Engineering Lead | W4 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the §4 subdivision is the only addition and is justified
- [x] Seven audiences identified with population, arrival route and first need
- [x] Nine-section tree specified, with the reason for the count and for two contested sections
- [x] Fourteen page types with owner, source of truth and update trigger
- [x] Generated-versus-authored boundary specified as a pipeline, not a preference
- [x] Golden path defined with a numeric target and a per-audience first-call endpoint
- [x] Four access tiers with the T-Pub disclosure rule stated
- [x] **Tiering declared as server-side authorisation, not navigation (`API-10`, `EA-11`)**
- [x] All eleven other Category 15 files mapped to a section, page type and tier
- [x] **The two files published as extracts rather than in whole are identified and the reason stated**
- [x] `M28` Q-07 addressed with a recommended option and its rationale, not avoided
- [x] Six measures with denominators (`CP-11`)
- [x] Unregistered endpoint proposal marked as a proposal (`CG-012`, `CM-R8`)
- [x] All internal links resolve
- [x] Eight open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` no portal platform selected or budgeted — outstanding; blocks `CD-126` sizing**
- [ ] **`O-02` registered a wave after first consumption — outstanding; register correction required**
- [ ] **`O-03` `M28` Q-07 unresolved — outstanding**
- [ ] Named approvers recorded — **pending Programme Content Lead and CTO**
- [ ] Bengali counterpart — n/a; developer audience, English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
