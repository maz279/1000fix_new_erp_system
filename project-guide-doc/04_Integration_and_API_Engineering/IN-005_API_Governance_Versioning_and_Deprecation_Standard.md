---
id: IN-005
title: API Governance, Versioning & Deprecation Standard
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
  Semantic Versioning 2.0.0 · RFC 8594 (Sunset header) · RFC 9745 (Deprecation header) ·
  draft-ietf-oauth-v2-1-15 (scope semantics) · draft-ietf-httpapi-ratelimit-headers ·
  ISO/IEC 25010 (compatibility characteristic)
traces_to: >
  PGD-000 IN-005 · 05-03 §5.2 API-02, API-08, API-10 · M28 §5.2, §8.2, FR-IPF-013, -014, -023 ·
  BRU-IPF-05 · EA-11, EA-12 · audit AP-05 (high), AP-14 (medium), AP-11 · AP-005 §4.3, §4.7 ·
  IN-001 §4, §10 · IN-002 §7, §8
depends_on: IN-001 · IN-002 · 05-04 (role register) · GV-002 (Design Authority)
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 17:25 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# IN-005 — API Governance, Versioning & Deprecation Standard

### Category 04 · Code `IN` · SemVer 2.0.0 · RFC 8594 · RFC 9745

---

> **This document exists to close one of the three unmade Wave 1 platform decisions.**
>
> `AUDIT-016` `AP-05` (high, open): *"`FR-IPF-003` enforces the caller's authorisation scope at the
> gateway. `EA-11` binds external API access to the credential's scope and forbids widening by
> parameter. `API-10` forbids any endpoint returning data outside the caller's scope. `AP-002`
> `AR-04` requires every published operation to declare the scope it needs, by name.*
>
> ***Not one scope name appears anywhere in the repository.***"
>
> `IN-002` `FF-54` **blocks publication of every API contract and the issue of every credential**
> until that vocabulary exists. **§5 is it.** `AP-005` §4.3 proposed the form and marked it a
> proposal throughout; this document ratifies the form, enumerates the vocabulary, and states what
> happens to a scope once it is issued.

---

## 1. Purpose

An API contract says what an operation *does*. Governance says **who may call it, under what name,
for how long, and what happens when it changes.** Without it, a credential is scoped by an engineer's
judgement at a keyboard, a version is retired when someone forgets it is in use, and a partner
discovers a breaking change in production.

This document establishes the lifecycle that surrounds `IN-002`'s 1,187 operations and `IN-003`'s
988 events: the **scope vocabulary**, the versioning scheme, the breaking-change policy, the
deprecation and sunset procedure, consumer registration, rate-limit classes, and the enforcement that
makes each of them mechanical rather than aspirational.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **The scope vocabulary** — form, derivation, the enumerated set, and the grant rules |
| 2 | Credential lifecycle: issue, scope, rotate, suspend, revoke |
| 3 | The **consumer register** — who is integrated, against what, at what version |
| 4 | Versioning: path version vs contract version, and what forces each |
| 5 | The **breaking-change policy** — a closed list, with the reasoning |
| 6 | Deprecation and sunset: notice periods, headers, and what happens if a consumer will not move |
| 7 | Rate-limit classes and their assignment |
| 8 | API design review and the exemption procedure |
| 9 | The **contractual gap** `AP-14` found, and what must go into partner agreements |
| 10 | CI and runtime gates `FF-69`…`FF-76` |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Contract **form** — schemas, paths, errors | `IN-002` | Form is not lifecycle |
| Event schema compatibility and dual-publish | `IN-003` §6 | Same principles, different surface, stated where the surface lives |
| Base-path scoping | `IN-001` §4 | Ruled there |
| Webhook signature and delivery | `IN-006` | The second of the three unmade W1 decisions |
| **Human roles and permissions** | `05-04`, `SC-004` | **A scope is not a role** — §5.6 |
| Authentication mechanism | `M29`, `SC-004` | This document governs what a token *carries*, not how it is issued |
| Commercial terms and pricing of API access | `CO-*` | §11 states what the contract must say; Legal writes it |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **`IN-002` author and every module developer** | §5's vocabulary is what `x-scope` must draw from |
| Security Lead | §5.7's grant rules and §6's credential lifecycle |
| Partner-facing engineers | §7's consumer register is the record of who is integrated |
| Commercial and Legal | §11 — the clause that does not exist in any agreement today |
| Platform Engineering | §9's rate-limit classes and §12's gates |
| Support | §6.5 — what a consumer may self-serve, and what requires an approval |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Concept | Conformance | Departure |
|---|---|---|---|
| **Semantic Versioning 2.0.0** | `MAJOR.MINOR.PATCH` | §8.2 — the **contract** version | None |
| **RFC 9745** | `Deprecation` HTTP header | §10.3 emits it on every deprecated operation | None |
| **RFC 8594** | `Sunset` HTTP header and `rel="sunset"` link | §10.3 | None |
| **draft-ietf-oauth-v2-1-15** | Scope as a capability grant | §5 | **Cited as a draft, not an RFC** (`IN-001` VC-02) |
| **draft-ietf-httpapi-ratelimit-headers** | `RateLimit`, `RateLimit-Policy` | §9.3 emits **both** these and the `X-` forms | Additive, per `AP-005` §4.7 |
| **ISO/IEC 25010** | Compatibility — co-existence and interoperability | §8, §10 are its realisation | None |

### 2.2 Source material relied on

| Source | Contribution |
|---|---|
| `05-03` §5.2 `API-02`, `API-08`, `API-10` | Two concurrent versions, six months' notice; per-consumer limits; server-side scope |
| `05-03` §3.4 | **600 req/min per portal instance, burst 100/s** — the only rate-limit figure in the estate with a source |
| `M28` §5.2, §8.2, §12.5 | API lifecycle, version states, the consumer and credential endpoints |
| `M28` `Q-08` | *"What is the escalation path when a consumer refuses to migrate and blocks a sunset?"* — **unanswered** |
| `BRU-IPF-05` | The two-version rule as a hard internal rule |
| `EA-11`, `EA-12` | External access bound to credential scope; export controlled |
| `05-04` | **38 human roles** with CRUDA per module and an isolation tier; `R38 External Party` |
| **`AP-005` §4.3, §4.4, §4.7** | The proposed scope form, credential lifecycle and six rate-limit classes — **all marked proposals** |
| `AP-011` | Deprecation and change-notice **content**, written against a policy that did not exist |
| `AUDIT-016` `AP-05`, `AP-14` | The two findings this document closes |

### 2.3 Audit findings this document closes

| Finding | Source | Disposition |
|---|---|---|
| **`AP-05` (high)** — no scope naming convention; every credential scoped by judgement | `AUDIT-016` | **Closed.** §5 ratifies the vocabulary; §5.5 enumerates it; `FF-69` enforces it. Unblocks `IN-002` `FF-54`, `AP-002` `AR-04`, `AP-007` §4.5 and `AP-008` §4.5 |
| **`AP-14` (medium)** — the six-month API notice promise appears in **no partner agreement** | `AUDIT-016` | **Contributes decisively.** §11 states the reciprocal clause; Legal must insert it. **Cannot be closed by an engineering document alone** |
| `M28` `Q-08` — no escalation when a consumer refuses to migrate | `M28` §18 | **Answered** — §10.6, and it depends on §11's clause existing |
| `AP-005` `O-01` — the scope proposal needs ratification | `AP-005` | Ratified here, with three amendments (§5.4) |
| `AP-005` `O-03` — no limit published for any non-portal consumer | `AP-005` | §9.2 publishes six classes; five remain **proposals with no external source**, and §9.2 says so |
| `AP-002` `AR-04` — every operation declares its scope by name | `AP-002` | Enforceable from now (`FF-69`) |

---

## 3. What Governance Applies To

| Surface | Governed by this document | Not governed here |
|---|---|---|
| The **1,187 synchronous operations** (`IN-002`) | Version, scope, deprecation, rate limit, consumer registration | Their schemas |
| The **988 events** (`IN-003`) | Consumer registration, deprecation notice period | Schema compatibility — `IN-003` §6 |
| **Outbound webhooks** (`IN-006`) | Subscription registration, deprecation | Signature scheme |
| The **47 external integrations** (`IN-004`) | Our obligations to them; **their obligations to us are the ICD's §15** | The wire contract |

---

## 4. The Governance Bodies

`GV-002` constitutes nine bodies. Three matter here, and the allocation is stated so a decision has a
home rather than an owner-by-default.

| Decision | Body | Cadence |
|---|---|---|
| Ratify a **new scope name** | **Design Authority** | Per sprint |
| Approve a **breaking change** (new path version) | **Design Authority** | Per sprint |
| Approve a **sunset** of a version in use by a registered external consumer | **Change Advisory Board** | Per change |
| Approve a **scope widening** on a live external credential | **Security Lead + Commercial Director**, recorded | Per request |
| Approve a **rate-limit class change** for a named consumer | Integration Architect, recorded | Per request |
| Grant an **exemption** from this standard | Design Authority, **with an expiry date** | Per request |

> **`PGD-A1-09` applies here as everywhere: none of these bodies is constituted, and no approval
> record can exist until `GV-001` `CC-01` completes.** Until then, the decisions above are recorded
> and executed by their named roles, and the absence of a ratification is a stated condition, not a
> silent one.

---

## 5. The Scope Vocabulary

### 5.1 The form

`AP-005` §4.3 proposed it. **Ratified:**

```
<resource>:<action>[:<qualifier>]
```

| Element | Rule |
|---|---|
| `resource` | The **`AR-008` aggregate** the operation's path root maps to — singular, `snake_case`. **Not** the module code and **not** the API family. A family is a routing and policy concept; a scope is a permission concept |
| `action` | Exactly four: **`read` · `write` · `approve` · `export`** |
| `qualifier` | Optional narrowing — `own_brand`, `own_org`, `own_seller`. Used **only** where the same resource is exposed to more than one external audience |

### 5.2 Why `delete` is absent

`DI-08` permits **soft deletion only**; a hard deletion is an approved, logged procedure and never an
API operation. A `DELETE` operation therefore requires `write` (`IN-002` §4.4).

> **Stated explicitly because the omission looks like an oversight and is not.** A `delete` scope
> would imply a hard-delete capability exists to be granted, and the first partner to ask for it
> would be asking for something the data model does not offer.

### 5.3 Why the resource is the aggregate, not the endpoint

| Granularity | Scope count for 1,187 operations |
|---|---:|
| Per operation | **1,187** |
| Per path | 978 |
| **Per aggregate × action** | **~88** |

**A permission model with 1,187 members cannot be administered**, and `AP-005` `SC-04` requires the
narrowest scope **that satisfies the contract** — not the narrowest conceivable. A partner agreement
covers *"warranty claims for our own brand"*, not *"`POST /api/v1/warranty/claims/{id}/decision`"*.
The scope should be expressible in the same words as the contract that grants it.

### 5.4 Three amendments to `AP-005`'s proposal

`AP-005` marked its scope model a proposal throughout, correctly. Ratifying it produces three
changes:

| # | Amendment | Reason |
|---|---|---|
| **AM-01** | `resource` is **the `AR-008` aggregate name**, not "the `CG-004` controlled term for the business object" | `CG-004` is a **content** vocabulary and `AR-008` is the **domain** vocabulary. They mostly agree, and where they do not, a permission must follow the domain model — the same reasoning that made the *event* namespace the aggregate rather than the module code (ADR-017) |
| **AM-02** | The qualifier set is **closed**: `own_brand`, `own_org`, `own_seller`. A new qualifier requires Design Authority ratification | An open qualifier set becomes a second, undocumented data-scope model competing with record rules |
| **AM-03** | A scope name, once issued to an external consumer, is **permanent** — retiring one follows §10's deprecation procedure | Re-scoping a live partner credential is a **breaking change**, which `AP-05` identified and `AP-011` must give notice of |

### 5.5 The enumerated vocabulary

Derived per §5.1 from the `AR-008` §4.2 aggregate roots. **This is the closed set at issue; additions
require Design Authority ratification and appear in the consumer-facing changelog.**

#### Service delivery

| Scope | Grants |
|---|---|
| `service_order:read` · `:write` | Read / create and update service orders within the credential's data scope |
| `work_order:read` · `:write` | Field work orders, evidence, transitions |
| `consignment:read` · `:write` | Pick-and-drop consignments, custody events |
| `customer_asset:read` · `:write` | Registered customer devices |

#### Customer engagement

| Scope | Grants |
|---|---|
| `party:read` · `:write` | Customer and organisation master records |
| `loyalty_account:read` | Tier, points, vouchers |
| `interaction:read` · `:write` | Contact-centre interactions |
| `complaint:read` · `:write` | Complaints and their resolution |

#### Commercial

| Scope | Grants |
|---|---|
| `contract:read` · `:write` | Service contracts and entitlements |
| `warranty_claim:read` · `:write` · **`:approve`** | Claims; `approve` is the decision authority |
| `warranty_claim:read:own_brand` · `:approve:own_brand` | **The brand-partner grant** |
| `quotation:read` · `:write` · **`:approve`** | Estimates and the customer's decision |
| `catalogue:read` | Services, products, price books |
| `price_book:read` · `:write` | Pricing — `write` is internal only |

#### Marketplace

| Scope | Grants |
|---|---|
| `listing:read` · `:write` · `:write:own_seller` | Marketplace listings |
| `marketplace_job:read` · `:write:own_seller` | Job broadcast, bid, award |
| `dispute:read` · `:write` | Marketplace disputes |
| `payout:read:own_seller` | A seller's own payouts and statements |

#### Supply chain and asset

| Scope | Grants |
|---|---|
| `stock_item:read` · `:write` | Parts and stock |
| `purchase_order:read` · `:write` · **`:approve`** | Procurement |
| `supplier:read` · `:write:own_org` | **The vendor-portal grant** |
| `enterprise_asset:read` · `:write` | Internal assets, fleet, equipment |

#### Finance

| Scope | Grants |
|---|---|
| `invoice:read` · `:read:own_org` · **`:export:own_org`** | **The corporate-client grant** |
| `payment:read` · `:write` | Payment initiation and confirmation |
| `credit_note:read` · **`:approve`** | SLA remedies and adjustments |
| `journal_entry:read` | Ledger — read only, ever, over an API |

#### Platform

| Scope | Grants |
|---|---|
| `platform_event:read` · `:write` | Event catalogue, schemas, subscriptions |
| `webhook_endpoint:read` · `:write` | Endpoint registration, test, secret rotation |
| `integration:read` | The 47-integration register with health |
| `api_consumer:read` · `:write` | The consumer register (§7) |

**Counted at issue: 27 resources · 4 actions · 3 qualifiers — 58 named scopes**, against 1,187
operations. The ratio is the whole argument for §5.3.

### 5.6 A scope is not a role

`05-04` registers **38 human roles** with CRUDA per module and an isolation tier. A scope governs a
**credential**, usually machine-held, and is coarser.

| Property | Role (`05-04`) | Scope (this document) |
|---|---|---|
| Held by | A person | A credential |
| Granularity | CRUDA per module, 67 modules | Aggregate × action |
| Source | Employment and organisational position | **The contract** |
| Data scope | Isolation tier `T0`–`T5` | Record rules, **plus** an optional qualifier |
| Changed by | HR and line management | A commercial and security decision, recorded |

**The relationship:** a credential issued to an external party is granted scopes that are a **subset**
of what role `R38 External Party` may do in that portal, **never a superset**.

> **`IN-A-21` (medium).** Where a machine credential appears to need more than `R38` holds, **that is
> a role gap to raise against `05-04`, not a scope to invent** (`AP-005` §4.3). `M28` §13 already
> records that `05-04` has **no "platform engineer" and no "module developer" role**, and `AR-006`
> records that **R39–R46 are unregistered, R60 duplicates R32, and R54/R57 are undefined**. The
> subset rule in §5.6 is therefore **currently unverifiable for at least eight roles**, and
> `AR-007` `FF-26` is already recorded as unsatisfiable for the same reason. Referred to `SC-004`.

### 5.7 The eight grant rules

`AP-005` §4.3 proposed eight. **Ratified unchanged**, because each is already anchored in an existing
control:

| # | Rule | Basis |
|---|---|---|
| **SC-01** | A scope grants **capability**, never **visibility**. Data scope is enforced separately by record rules and cannot be widened by holding a scope | `API-10`, `EA-11` |
| **SC-02** | **A request parameter can never widen scope.** A credential scoped to one brand asking for another brand's claims receives an empty result or `403` — never another brand's data, and **never a different error revealing the record exists** | `EA-11`, `AP-002` `ED-06`, `IN-002-D-05` |
| **SC-03** | Scopes are granted at credential issue, **from the contract**. Widening is a commercial and security decision with a recorded approval, not a support action | `EA-01` |
| **SC-04** | The **narrowest scope that satisfies the contract** is granted. `IP-10` minimisation applies to capability as well as to data | `IP-10` |
| **SC-05** | **`approve` is never granted with `write` by default.** Approving is a distinct authority and several `05-04` §6 segregation rules depend on the separation | `SOD-01`…`SOD-12` |
| **SC-06** | `export` is separate from `read`, and is **rate-controlled and logged** | `EA-12`, `FR-SEC-041` |
| **SC-07** | A scope is **never** granted to an external consumer for a resource with no external audience — `payroll`, `employee`, `recovered_data`, `internal_note`, `model_features` | `05-04` §5, `EA-02` |
| **SC-08** | **Every published operation declares the scope it requires**, in its contract | `AP-002` `AR-04`, `IN-002` `SD-01`, `FF-50` |

---

## 6. Credential Lifecycle

| Stage | Rule |
|---|---|
| **Request** | Names the consumer, the contract clause justifying each scope, the environment and an owner **role** |
| **Issue** | Scopes from §5.5 only (`FF-69`). Secret returned **once**, vault-stored, never retrievable |
| **Environment binding** | A credential is valid in **one** environment. A production credential used against sandbox returns `401 auth.environment_mismatch` |
| **Expiry** | Every credential has an `expires_at`. **No perpetual credentials** |
| **Expiry alerting** | `platform.credential_expiring` at **30 and 7 days** |
| **Rotation** | **Consumer self-service**, with an overlap window (`IN-006` §7) |
| **Widening** | §4's recorded approval. **Never a support action** |
| **Suspension** | Immediate on a security event; the consumer is notified |
| **Revocation** | On contract termination. **Revocation is not deletion** — the register row is retained (`GV-011` `CM-22`) |

### 6.1 What a credential may never do

Carried from `AP-005` §4.11 because it is the shortest useful summary of §5.7:

| # | Never |
|---|---|
| 1 | Hold a scope for a resource with no external audience |
| 2 | Widen its own data scope by parameter |
| 3 | Perform a step-up-requiring action without a human (`403 auth.step_up_required`) |
| 4 | Be shared between two consumers, or between two environments |
| 5 | Appear in a log, a trace, a DLQ entry, an error body or a URL |
| 6 | Outlive the contract that justified it |

---

## 7. The Consumer Register

**`M28` §12.5 declares `/api/v1/platform/consumers`. This is what a row must carry.**

| Field | Why |
|---|---|
| Consumer id, legal entity, **owner role** | Identity and who to notify |
| Class — `portal` · `partner` · `internal` · `sandbox` | Drives the rate-limit class and the notice period |
| **Contracts consumed** — which of the eleven `IN-002` documents, at which **path version** | **The set §10.4 queries to answer "who is still on v1?"** |
| **Scopes granted**, and the contract clause justifying each | `SC-03`; makes an audit of over-scoping a query |
| **Event subscriptions** (`IN-003` `C-07`) | So producers know who they will break |
| **Webhook endpoints** (`IN-006`) | Delivery state, failure count |
| Rate-limit class | §9 |
| Credential references and expiry | §6 |
| **Environment** | `SC` binding |
| Certification status and date (`IN-008`) | Whether they have passed sandbox certification |
| **Notice contact** — a role and an address, never a person | §10.3 |

> **The register is what makes deprecation possible.** Without it, "every consumer has migrated" is
> unanswerable and a version is retired on optimism — which is exactly the failure `IN-003` §6.3
> step 2 guards against on the event side.

---

## 8. Versioning

### 8.1 Two versions, and they are not the same thing

| Version | Where | Changes on | Governed by |
|---|---|---|---|
| **Path version** `/api/v1/` | Every URL | **Only a breaking change** | §8.3 |
| **Contract version** `info.version` | The OpenAPI document | **Every** change | SemVer 2.0.0 |

`FF-49` enforces the implication: a `MAJOR` contract bump without a new path version fails CI.

### 8.2 SemVer applied

| Component | Increments on |
|---|---|
| `MAJOR` | A breaking change (§8.3) — **and it requires a new path version** |
| `MINOR` | An additive, non-breaking change: a new operation, a new optional field, a new enum value in an open enumeration |
| `PATCH` | Documentation, examples, descriptions — **nothing a client can observe** |

### 8.3 The breaking-change list — closed

**A change is breaking if and only if it appears here.** A closed list is what makes "is this
breaking?" answerable at review rather than in production.

| # | Change | Breaking |
|---|---|:--:|
| 1 | Remove an operation, or change its path or method | ✔ |
| 2 | **Rename an `operationId`** | ✔ — it breaks every generated client, contract test and portal deep link (`IN-002` `OP-04`) |
| 3 | Add a **required** request field, or make an optional one required | ✔ |
| 4 | Remove a response field, or change its type | ✔ |
| 5 | Narrow a constraint — shorten `maxLength`, reduce a numeric range, remove an enum value | ✔ |
| 6 | Add a value to a **closed** enumeration | ✔ |
| 7 | Change the **HTTP status** an existing condition returns | ✔ |
| 8 | Change an **error `code`**, or the **meaning** of an existing one | ✔ — `AP-006` `CG-04` |
| 9 | Change an error's **retry classification** | ✔ — `AP-006` `CG-06`; a partner's handler is built on it |
| 10 | Add or widen a **required scope** on an existing operation | ✔ — existing credentials stop working |
| 11 | Change pagination semantics, or invalidate outstanding cursors | ✔ |
| 12 | Change authentication scheme or token format | ✔ |
| 13 | Reduce a rate limit for an existing consumer class | ✔ — §9.4 |
| 14 | Add a new **optional** request field | ✘ |
| 15 | Add a response field | ✘ — which is why `IN-002` `BD-03` forbids `additionalProperties: false` on responses |
| 16 | Add a value to an **open** enumeration | ✘ — consumers must carry a default branch |
| 17 | Add a new operation | ✘ |
| 18 | Change an error **`message`** | ✘ — `AP-006` `CG-05`; that is what `EP-01` buys |
| 19 | Relax a constraint, or widen a range | ✘ |
| 20 | Improve latency, or change an internal implementation | ✘ |

> **Rows 8, 9 and 18 together are the point of `AP-006` `EP-01`** — *"the `code` is the contract; the
> `message` is the courtesy."* It is what lets the estate reword and retranslate 90 error messages
> freely while their codes stay frozen.

### 8.4 Concurrency

| Rule | Value |
|---|---|
| Concurrent path versions supported | **At least two** (`API-02`, `BRU-IPF-05`) |
| Maximum concurrently supported | **Two.** A third is an exemption with an expiry (§12.2) |
| A version's minimum life | **Twelve months** from general availability |

---

## 9. Rate Limits

### 9.1 Where the limit lives

Per `IN-001-D-01`, the **API family is the policy unit**, realised as a Kong consumer group. A limit
is assigned to a **consumer**, not to an endpoint (`API-08`).

### 9.2 The six classes

`AP-005` §4.7 proposed them, so that a limit is a **class assignment at registration** rather than a
number invented per partner. **Ratified with the source position stated per class:**

| Class | Sustained | Burst | Typical consumer | Source |
|---|---:|---:|---|---|
| `portal` | 600/min | 100/s | The CON-03 portal platform, per instance | **`05-03` §3.4 — the only figure in the estate with a source** |
| `partner-high` | 300/min | 50/s | Payment gateways, couriers — latency-critical, callback-driven | **Proposal** |
| `partner-standard` | 120/min | 20/s | Brand partners, corporate clients | **Proposal** |
| `partner-light` | 60/min | 10/s | Marketplace sellers, referral partners — individually small, collectively up to 2,000 | **Proposal** |
| `bulk` | 20/min | 5/s | Estate loads, bulk submission, exports | **Proposal** |
| `sandbox` | 60/min | 10/s | Every sandbox credential | **Proposal** |

> **Five of the six figures have no source in the repository** (`AP-005` `O-03`). They are internally
> consistent and defensible; they are **not measured**. `CG-012` and `CM-R8` require the distinction
> to be visible, so it is. **They are calibrated against real traffic at the W2 gate**, and until
> then a limit breach is investigated before it is enforced.

### 9.3 Headers

Emit **both** forms — the `X-` forms because `API-08` specifies them and partner libraries expect
them, and the IETF standard forms because that is where the industry is going. Additive, one extra
header.

| Header | Note |
|---|---|
| `X-RateLimit-Limit`, `-Remaining`, `-Reset` | `-Reset` is an **absolute Unix time** |
| `RateLimit`, `RateLimit-Policy` | `reset` here is **seconds remaining** — the two forms differ, and a client that confuses them will back off for decades or not at all |
| `Retry-After` | **On `429` and `503` only** |

### 9.4 Changing a consumer's class

| Direction | Treatment |
|---|---|
| **Increase** | Recorded, effective immediately |
| **Decrease** | **A breaking change** (§8.3 row 13) — §10's notice period applies |
| Temporary increase | Time-boxed, with an expiry, recorded |

### 9.5 The six consumer rules

Carried from `AP-005` §4.7 into the standard, because a rate limit only works if both sides
cooperate:

| # | Rule |
|---|---|
| **RL-01** | Read `X-RateLimit-Remaining` and slow down **before** exhaustion. The headers exist so `429` is avoidable |
| **RL-02** | On `429`, honour `Retry-After`. **Do not retry immediately and do not retry faster** |
| **RL-03** | Back off exponentially **with jitter**. Synchronised retries from many consumers are a self-inflicted denial of service |
| **RL-04** | Use `bulk`-class endpoints for bulk work rather than looping an interactive one |
| **RL-05** | **A `429` is not a failure of the request.** Retried with the same `Idempotency-Key`, it succeeds and nothing is duplicated |
| **RL-06** | Sustained breaches are recorded, alerted, and feed `M29` anomaly detection. **Persistent breach is a commercial conversation, not a technical one** |

> **Bot protection is not rate limiting.** `NFR-068` requires bot detection on all public endpoints
> (`FR-IPF-005`). A tripped request receives **`403 auth.bot_blocked`, not `429`**, and the remedy is
> registration rather than backoff.

---

## 10. Deprecation and Sunset

### 10.1 The lifecycle

| State | Meaning | Consumer-visible |
|---|---|---|
| **Planned** | Announced, not yet built | Changelog |
| **Available** | The current version | — |
| **Deprecated** | Still served; a successor exists; a sunset date is set | `Deprecation` + `Sunset` headers, changelog, direct notice |
| **Sunset** | No longer served | `400 request.version_unsupported` |
| **Retired** | Removed from the contract; the register row retained | — |

### 10.2 Notice periods

| Consumer class | Minimum notice | Basis |
|---|---:|---|
| **External partner** | **6 months** | `API-02`, `BRU-IPF-05`, `05-03` §3.4 |
| Corporate client / brand partner | 6 months | As above |
| Internal portal | 3 months | Same release train |
| Sandbox-only consumer | 1 month | No production dependency |
| **Emergency security sunset** | **As short as necessary**, with a written justification and CAB approval | §10.5 |

### 10.3 What a deprecation must emit

| Channel | Requirement |
|---|---|
| **Contract** | `deprecated: true`, `x-sunset: <RFC 3339>`, `x-replaced-by: <operationId>` (`IN-002` `DP-01`) |
| **Runtime headers** | `Deprecation` (RFC 9745) and `Sunset` (RFC 8594) on every response from the deprecated operation |
| **Link header** | `rel="deprecation"` pointing to the changelog entry |
| **Changelog** | `AP-011`'s content, published to the developer portal |
| **Direct notice** | To every **registered consumer** of that version, at the register's notice contact |
| **Dashboard** | Remaining call volume per consumer, so migration progress is measured, not assumed |

`FF-72` fails a build where `x-sunset` is less than the class notice period after the deprecation
date.

### 10.4 The migration query

Because §7's register exists, **"who is still on v1?"** is a query, not a survey:

```
consumers WHERE contract = 'service-delivery' AND path_version = 'v1'
          AND calls_last_30d > 0
```

A version is sunset when that result is empty, **or** when the notice period has elapsed and §10.6
has been applied.

### 10.5 Emergency security sunset

A vulnerability may require a shorter notice than §10.2. Then, in order:

| # | Step |
|---|---|
| 1 | Security Lead states the vulnerability and the shortest defensible notice |
| 2 | **CAB approves**, recorded |
| 3 | Every registered consumer is notified directly, with the mitigation |
| 4 | A compensating control is offered where possible — an IP-restricted extension, a proxy shim |
| 5 | The decision and its cost are recorded in `GV-003` |

> **§11's contract clause must carry an emergency exception, or step 2 has no contractual footing.**

### 10.6 When a consumer will not migrate — answering `M28` `Q-08`

`M28` `Q-08` asks: *"What is the escalation path when a consumer refuses to migrate and blocks a
sunset?"* It has had no answer. **Here is one**, and it is honest about where it depends on Legal:

| Stage | Action | Owner |
|---|---|---|
| 1 | Automated notice at **6, 3, 1 month** and **2 weeks**, with call volume | Platform |
| 2 | Direct contact with the register's notice contact | Integration Architect |
| 3 | **Escalation to the account owner.** Migration becomes a commercial conversation | Commercial Director |
| 4 | **Rate-limit reduction on the deprecated version** — degrade, do not sever | Integration Architect + CAB |
| 5 | **Sunset proceeds** on the stated date | CAB |

> **Stage 5 requires §11's clause.** `AP-14` found that the six-month promise appears in **no partner
> agreement** — and the asymmetry runs **both ways**: 1000FiX cannot contractually require a partner
> to migrate, and a partner cannot hold 1000FiX to the six months. **`BRU-IPF-05` gives the platform
> no unilateral remedy**, which is exactly why `Q-08` had no answer.
>
> **Stage 4 is the mechanism that works without a contract.** Degrading a deprecated version's rate
> limit converts an indefinite standoff into a deteriorating experience the consumer must respond to,
> without severing a live integration. It is deliberately the *last* step before sunset, and it is a
> breaking change under §8.3 row 13 — so it is announced, not sprung.

---

## 11. The Contractual Gap — `AP-14`

### 11.1 What is missing

`05-03` §3.4 and `API-02` promise **two concurrent versions and six months' notice**. `BRU-IPF-05`
makes it a hard internal rule and `FR-IPF-014` enforces the clock.

> **The promise is made in an architecture document.** `LG-003` corporate terms, `LG-005` brand
> terms, `LG-006` vendor terms and `LG-007` partner terms are the instruments that would bind it,
> **and none is cited anywhere as containing an API notice clause.**

### 11.2 What the clause must contain

| # | Element | Why |
|---|---|---|
| 1 | **1000FiX's notice obligation** — minimum six months before removing a supported version | Makes the published promise binding |
| 2 | **The partner's obligation to maintain a supported version** | Without it, §10.6 stage 5 has no footing |
| 3 | **The emergency security exception**, with its own shorter notice | §10.5 step 2 |
| 4 | **The consumer register as the notice mechanism** — notice to the registered contact is deemed given | Prevents "we never received it" |
| 5 | **Rate-limit degradation on a deprecated version** as a stated remedy | Makes §10.6 stage 4 contractual rather than unilateral |
| 6 | **Scope changes are contract changes** (`SC-03`, `AM-03`) | Re-scoping a live credential is breaking |
| 7 | Sandbox availability and certification obligations | `IN-008` |

### 11.3 What this document cannot do

**`AP-14` cannot be closed by an engineering document.** Legal Counsel must insert the clause into
`LG-003`, `LG-005`, `LG-006` and `LG-007` **before the first external contract is signed**. Recorded
as **`IN-A-13`**, owner Legal Counsel with Commercial Director, needed **W3**, and it is the missing
piece of `AP-011` §4.7 stage 3.

---

## 12. Enforcement

### 12.1 Gates

Continuing `AR-012` v1.1 `FF-01`…`FF-37`, `IN-001` `FF-38`…`FF-45`, `IN-002` `FF-46`…`FF-58`,
`IN-003` `FF-59`…`FF-68`.

| # | Check | Scope | Timing | Enforcement |
|---|---|---|---|---|
| **FF-69** | Every `x-scope` value is in §5.5's ratified vocabulary | 1,187 operations | CI | Fail |
| **FF-70** | No credential holds a scope for a resource with no external audience (`SC-07`) | All credentials | CI + issue-time | Block |
| **FF-71** | No operation declares `approve` **and** `write` unless it genuinely does both (`SC-05`, `SD-04`) | 1,187 | CI | **Report**, reviewed |
| **FF-72** | `x-sunset` ≥ deprecation date + the consumer class's notice period | Deprecated ops | CI | Fail |
| **FF-73** | Every consumer of a version being sunset is **registered and notified**, evidenced | Per sunset | Release gate | Block |
| **FF-74** | No breaking change (§8.3 rows 1–13) ships without a new **path version** | Per release | CI diff against the published contract | Fail |
| **FF-75** | Every issued credential has an `expires_at`, and none exceeds its contract's end date | All | Issue-time + daily | Block / alert |
| **FF-76** | Every external consumer in the register has a **certification record** (`IN-008`) before production credentials are issued | All partners | Issue-time | Block |

### 12.2 Exemptions

| Rule | Detail |
|---|---|
| Who grants | **Design Authority** |
| What is recorded | The rule, the reason, the compensating control, the **expiry date** |
| Maximum duration | **One wave** |
| **On expiry** | The exemption **lapses**; the gate applies. There is no automatic renewal |
| Where recorded | `GV-003` decision log, and the consumer register row where consumer-specific |

> **An exemption without an expiry is a silent standard change.** `AR-012`'s exemption procedure
> established the pattern; this one follows it deliberately rather than inventing a second.

---

## 13. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `IN-005-D-01` | Scope form | Per operation · per path · **per aggregate × action, with an optional qualifier** | **Aggregate × action** | 1,187 scopes cannot be administered; a scope must be expressible in the same words as the contract that grants it | **58 named scopes**; unblocks `IN-002` `FF-54` and closes `AP-05` |
| `IN-005-D-02` | `resource` vocabulary | `CG-004` content terms · **`AR-008` aggregate names** | **`AR-008`** | A permission must follow the domain model, not the content vocabulary — the same reasoning that made the event namespace the aggregate (ADR-017) | `AM-01`; scope and event namespaces agree by construction |
| `IN-005-D-03` | Qualifier set | Open · **closed at three, extendable by ratification** | **Closed** | An open qualifier set becomes a second, undocumented data-scope model competing with record rules | `AM-02` |
| `IN-005-D-04` | Scope permanence | Rename freely · **permanent once issued externally** | **Permanent** | Re-scoping a live partner credential is a breaking change | `AM-03`; §10 applies |
| `IN-005-D-05` | Breaking-change definition | Case by case · **a closed list of thirteen** | **Closed list** | "Is this breaking?" must be answerable at review, not discovered in production | §8.3; `FF-74` |
| `IN-005-D-06` | Concurrent versions | Two minimum, unlimited · **two minimum, two maximum** | **Exactly two** | A third doubles the test matrix and triples the support surface for a benefit nobody has articulated | A third is an exemption with an expiry |
| `IN-005-D-07` | Consumer who will not migrate | Sever · sustain indefinitely · **escalate, then degrade the rate limit, then sunset** | **Degrade, then sunset** | Answers `M28` `Q-08`. Degradation works **without** a contract clause, which is the position the estate is actually in | §10.6; depends on `IN-A-13` for stage 5 |
| `IN-005-D-08` | Rate-limit figures | Present as decided · **publish with the five unsourced marked as proposals** | **Mark them** | Only the `portal` figure has a source. `CG-012` requires the distinction visible | §9.2; calibrated at the W2 gate |

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | **Is the §5.5 vocabulary ratified?** Until it is, `FF-54` blocks every contract publication and every credential | Design Authority + Security Lead | **W0 — blocking** | `IN-002`, every partner integration |
| Q-02 | **Does Legal insert the API lifecycle clause into `LG-003`/`005`/`006`/`007`?** (`IN-A-13`, `AP-14`) | Legal Counsel + Commercial Director | **W3 — before the first external contract** | §10.6 stage 5, `AP-011` §4.7 |
| Q-03 | The subset rule (§5.6) is **unverifiable for at least eight roles** — R39–R46 unregistered, R60 duplicates R32, R54/R57 undefined (`IN-A-21`) | CTO / `SC-004` owner | **W1** | Credential issue, `FF-26`, `FF-70` |
| Q-04 | Are the five unsourced rate-limit figures calibrated against real traffic at the W2 gate? | Integration Architect | W2 | §9.2 |
| Q-05 | Does a **corporate client federating its own SSO** (`INT-046`) receive scopes, or does its own IdP assert them? The two models are not compatible | Security Lead | W5 | `INT-046`, `IN-004` §20 |
| Q-06 | Who owns the **consumer register** operationally — Integration Architect, or a partner-management function that does not yet exist? | Programme Director | W2 | §7, §10.4 |

---

## 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **A scope vocabulary exists and is enumerated**, closing `AP-05` | §5.5 — 58 named scopes |
| AC-02 | The vocabulary's derivation is stated, so a new operation's scope is derived rather than invented | §5.1, §5.3 |
| AC-03 | The relationship between a scope and an `05-04` role is stated, including where it is currently **unverifiable** | §5.6, `IN-A-21` |
| AC-04 | Breaking change is a **closed list** | §8.3 — twenty rows, thirteen breaking |
| AC-05 | Deprecation emits contract, header, changelog and **direct notice** | §10.3 |
| AC-06 | **`M28` `Q-08` is answered**, and the answer's dependency on a contract clause is stated | §10.6, `IN-005-D-07` |
| AC-07 | The contractual gap `AP-14` found is specified as a clause Legal can insert | §11.2 |
| AC-08 | Rate-limit figures distinguish sourced from proposed | §9.2 |
| AC-09 | Every rule that can be checked mechanically has a gate | §12.1 — `FF-69`…`FF-76` |
| AC-10 | Exemptions carry an expiry and lapse | §12.2 |

**Definition of done.** Complete when every criterion is met, **Q-01 is ratified** (which unblocks
`IN-002`), Q-02's clause is inserted, `FF-69`…`FF-76` are enabled, the consumer register is
populated, and `PGD-000`'s `IN-005` row carries a fresh enumeration timestamp. **`AP-14` closes only
when Legal inserts the clause — this document cannot close it.**

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | **`IN-001`** §4 | Family-as-policy; the consumer group is the rate-limit unit |
| Upstream | `05-04` | The 38 roles a credential's scopes must be a subset of |
| Upstream | `AR-008` §4.2 | The aggregate names the vocabulary is built from |
| Downstream | **`IN-002`** | **`FF-54` unblocks the moment §5.5 is ratified** |
| Downstream | `IN-003` §6.3 | Same notice period applied to event schema retirement |
| Downstream | `IN-006` | Webhook subscription registration and endpoint deprecation |
| Downstream | `IN-008` | `FF-76` — certification before production credentials |
| Downstream | `SC-004` | The role gaps §5.6 depends on |
| Downstream | `AP-002` `AR-04`, `AP-005`, `AP-007` §4.5, `AP-008` §4.5, `AP-011` | All four were blocked on the vocabulary |
| Downstream | `CO-*`, `LG-003`/`005`/`006`/`007` | §11's clause |
| Lateral | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` §5.2 | `API-02`, `API-08`, `API-10` realised |
| Lateral | `../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M28_*.md` §5.2, §8.2, §18 | API lifecycle; **`Q-08` answered** |

---

## 17. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`./IN-001_Integration_Architecture_Specification.md`](./IN-001_Integration_Architecture_Specification.md) ·
[`./IN-002_API_Specification_OpenAPI_Contracts.md`](./IN-002_API_Specification_OpenAPI_Contracts.md) ·
[`./IN-003_Domain_Event_Catalogue_and_Schema_Registry.md`](./IN-003_Domain_Event_Catalogue_and_Schema_Registry.md) ·
[`./IN-006_Webhook_Callback_and_Partner_Push_Specification.md`](./IN-006_Webhook_Callback_and_Partner_Push_Specification.md) ·
[`./IN-008_Integration_Test_Sandbox_and_Certification_Specification.md`](./IN-008_Integration_Test_Sandbox_and_Certification_Specification.md)

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` §3.4, §5.2 ·
`.../05-04_Role_Permission_and_Access_Matrix.md` §5, §6 ·
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M28_*.md` §5.2, §8.2, §12.5, §18 ·
`../../project_content/_AUDIT/AUDIT-016_*.md` `AP-05`, `AP-14` ·
`../../project_content/15_Integration_and_Developer_Content/AP-005_*.md` §4.3, §4.4, §4.7, §4.11 ·
`.../AP-011_Integration_Change_Deprecation_and_Notice_Content.md`

**External sources**

| Source | Verified |
|---|---|
| Semantic Versioning 2.0.0 | 2026-08-18 |
| RFC 9745 — *The Deprecation HTTP Response Header Field* | 2026-08-18 |
| RFC 8594 — *The Sunset HTTP Header Field* | 2026-08-18 |
| `draft-ietf-oauth-v2-1-15` — Internet-Draft, 2 March 2026 | 2026-08-18 |
| `draft-ietf-httpapi-ratelimit-headers` — `RateLimit`, `RateLimit-Policy` | 2026-08-18 |

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Integration Architecture | Initial issue. **Closes `AP-05`** by ratifying the scope form and enumerating **58 named scopes** against 1,187 operations, unblocking `IN-002` `FF-54`. Amends `AP-005`'s proposal in three respects (`AM-01`…`AM-03`). Establishes a **closed twenty-row breaking-change list**. **Answers `M28` `Q-08`** with a five-stage escalation whose stage 4 works without a contract clause. Specifies the clause `AP-14` found missing from all four partner agreements (`IN-A-13`), and records that the scope-subset rule is **currently unverifiable for at least eight roles** (`IN-A-21`) | *Pending — Design Authority not constituted (`PGD-A1-09`)* |

---

*`IN-005` · Category 04 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
