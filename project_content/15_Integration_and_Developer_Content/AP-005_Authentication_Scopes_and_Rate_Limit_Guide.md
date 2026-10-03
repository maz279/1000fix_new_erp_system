---
id: AP-005
title: Authentication, Scopes and Rate Limit Guide
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering Lead
author: Platform Engineering with Information Security
reviewers: [CTO, Solution Architect, Security Lead, Content Design Lead, QA Lead, Account Management Lead, Commercial Director]
approver: Content Design Lead with CTO
content_class: D
purpose: >
  How a consumer obtains, uses, rotates and loses the right to call a 1000FiX API — the grant type
  for each audience, the scope model and what a scope may never do, credential lifecycle across
  environments, token and session behaviour, step-up for financial actions, and the rate-limit
  policy with its headers and remediation. `PS-02` routes every portal's traffic through the M28
  gateway with per-portal credentials and limits. Undocumented limits are discovered under load, at
  the worst moment, by the partner least able to diagnose them — and an undocumented scope model is
  how a credential ends up broader than the contract that issued it.
traces_to: [M28, M28 FR-IPF-002, M28 FR-IPF-003, M28 FR-IPF-004, M28 FR-IPF-016, M28 FR-IPF-041, M29, M29 FR-SEC-004, M29 FR-SEC-007, M29 FR-SEC-012, M29 FR-SEC-018, M29 §12.5, 05-03, 05-03 IP-02, 05-03 IP-07, 05-03 §3.4, 05-03 §5.1, 05-03 §5.2, 05-04 §8, 05-06 NFR-062, 05-06 NFR-065, 05-06 NFR-068, 05-06 NFR-069, 05-06 NFR-071, PS-01, PS-02, AP-001, AP-002, AP-004, AP-006, AP-010, AP-012, OP-009, OP-015, TS-017]
priority: P1
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md §5.1 twelve API families with their auth model; §5.2 API-08 rate limits with X-RateLimit-* headers and 429 plus Retry-After; §3.4 contract rules — OAuth 2.0 client credentials per environment, short-lived tokens, 600 req/min per portal instance with burst 100/s
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M29_Identity_Access_and_Information_Security.md §5 FR-SEC-004 MFA, FR-SEC-007 token services, FR-SEC-012 service accounts, FR-SEC-018 external party rules EA-01…EA-12; §6 T-09 introspection availability and T-10 sixty-second revocation propagation; §12.5 the five auth endpoints
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md §8 EA-01…EA-12 external party access rules, in particular EA-09 MFA for financial actions, EA-11 scope bound to credential, EA-12 bulk export limited and logged
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md NFR-062 vault-held secrets, NFR-065 step-up authentication, NFR-068 rate limiting and bot protection on public endpoints, NFR-069 session policy, NFR-071 masked data in non-production
    verified: 2026-08-18
    class: P1
  - source: IETF HTTPAPI draft-ietf-httpapi-ratelimit-headers-11 — RateLimit and RateLimit-Policy header fields for advertising quota policies and current service limits so clients can avoid being throttled. https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-ratelimit-headers
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# Authentication, Scopes and Rate Limit Guide

| Item | Value |
|---|---|
| API families covered | 12 (`05-03` §5.1) |
| Grant types | 4 (§4.2) |
| Scope naming convention | **Proposed** — none exists in the repository (§4.3, open item `O-01`) |
| Environments | 3 named (§4.4) — sandbox, staging, production |
| Rate-limit policy classes | 6 (§4.7) |
| Documented limit today | **One** — 600 req/min, burst 100/s, per portal instance (`05-03` §3.4). Nothing for partners (`O-03`) |
| Auth endpoints | 5 (`M29` §12.5) + 3 consumer-management (`M28` §12.5) |
| Wave | W3 registered · **first consumed W1** — open item `O-02` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order; §4 subdivided by volume. The **endpoint reference table**
> required by `CG-009` §3 is §4.9. The **error catalogue table** required by `CG-009` §3 is
> §4.10 — the authentication, scope and throttling errors, each with its remedy. Those entries
> are the authoritative source for their rows in `AP-006`'s consolidated catalogue; they are
> presented here because a developer debugging a `401` reads this file, not the catalogue
> (`CP-01`: authored once, referenced from `AP-006`).

---

## 1. Purpose

`IP-02` puts all traffic through the gateway. `PS-01` gives every portal single sign-on through
`M29` with no portal maintaining its own credential store. `PS-02` gives every portal per-portal
credentials and rate limits. `FR-IPF-002` validates tokens at the edge; `FR-IPF-003` enforces
scope there; `FR-IPF-004` applies limits there; `FR-IPF-016` issues and rotates credentials.

**Between them these specify a complete access-control architecture and name not one scope.**

The consequence is concrete. A brand partner signs an agreement covering warranty claims for their
own brand. An engineer issues them a credential. Which scope? There is no list. The engineer
grants what the partner asked for, which is a judgement made at a keyboard on a Tuesday, and
`EA-11` — *"external API access is scoped by credential; scope cannot be widened by request
parameters"* — is satisfied by a credential that was too wide when it was issued.

That is the failure this file prevents, together with the second one: **limits nobody published.**
`05-03` §3.4 gives 600 requests per minute per portal instance. That figure exists for the portal
platform. Nine payment gateways, four couriers, seventeen brands, an unknown number of corporate
clients and up to 2,000 sellers have no published limit at all — so the first any of them learns
about throttling is a `429` in production during their busiest hour.

**What stops working without this file.**

| Absent | Consequence |
|---|---|
| Scope model | Credentials are issued by judgement. Over-broad credentials are invisible until a breach or an audit, and `EA-11` is satisfied on paper while failing in fact |
| Grant-type-per-audience map | Every integrator asks the same question and gets a different answer; some implement client credentials for a user-present flow, which is a credential-sharing pattern |
| Credential lifecycle | Secrets live in configuration files, are never rotated, and `IP-07` and `NFR-062` are aspirations. `M28` §16.4 already records a **credential sweep** on the assumption that anything previously in plain text is compromised |
| Rate-limit publication | Partners size their integrations wrong. `NFR-068` requires limits on all public endpoints; a limit that is enforced and unpublished is a trap, not a control |
| Remediation copy | A `429` with no documented remedy produces a support ticket per occurrence, plus a retry storm from the partner's own error handler |
| Step-up documentation | `EA-09` requires MFA for external financial actions. An integration built without knowing this fails at the last step of the flow it was built for |

---

## 2. Scope

**In scope.** The identity/enforcement split; grant types per audience; the scope model, naming
convention and grant rules; credential lifecycle across three environments including rotation and
revocation; token and session properties; step-up and MFA for external financial actions; the
rate-limit policy classes, headers, `429` behaviour and remediation; the auth endpoint reference;
and the authentication, scope and throttling error catalogue.

**Out of scope.**

| Out of scope | Owned by | Note |
|---|---|---|
| Identity, MFA enrolment, session policy for **human users** in portals | `M29`, `UI-005` | This file covers **API access**. A customer signing into `P01` is `M29`'s and `UI-005`'s |
| Role and permission definitions | `05-04` | A scope is not a role. §4.3 states the relationship and refuses the merge |
| Record-level data scope enforcement | `M29` record rules | Scope says *which endpoints*; record rules say *which rows*. Both apply and neither substitutes |
| Identity provider operations, break-glass, MFA reset | `OP-009` runbook | Operator content |
| Joiner–mover–leaver access for employees | `OP-015` | Internal access lifecycle |
| Corporate client SSO federation (`INT-046`) design | `M29`, `AP-008` §federation | Named here; the client-facing guidance is `AP-008`'s |
| Sandbox credentials specifically | `AP-010` | §4.4 gives the lifecycle; `AP-010` gives the sandbox specifics |
| The webhook signing secret | `AP-004` §4.4 | A different credential type with a different purpose |
| Error envelope shape and the full catalogue | `AP-002` §4.7, `AP-006` | §4.10 authors the auth subset only |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Every external integrator** | The first document they read after `AP-001` step 1. Highest-traffic page on the developer portal in every comparable estate |
| **Portal platform team** | Per-portal credentials and the 600/min limit they operate under |
| **Internal module teams** | Declaring the scope their endpoint requires (`AP-002` `AR-04`) |
| **Security** | The scope grant rules and the credential lifecycle |
| **Account managers and commercial** | What a partner's credential permits, and the fact that widening it is a commercial and security decision, not a support request |
| **Support (`OP-001` tier 1)** | §4.10 — the remediation column is written to be quotable directly to a partner |
| **QA** | `TS-017` derives its scope negative cases from §4.3 and §4.11 |

---

## 4. Content

### 4.1 Who does what — the split that confuses everyone

| Concern | Owner | Where it happens |
|---|---|---|
| Issuing a token | **`M29`** | `/api/v1/auth/token` |
| Validating a token | **`M29`** issues the decision; **`M28`** calls it | `/api/v1/auth/introspect`, called on **every** gateway request |
| Deciding what a scope permits | **`M29`** | Scope resolution during introspection |
| Enforcing the scope at the edge | **`M28`** | `FR-IPF-003`, before the request reaches a module |
| Enforcing which **rows** the caller sees | **`M29`** record rules, **inside** the module | `05-04` §4 isolation tiers |
| Registering an API consumer | **`M28`** | `FR-IPF-016`, `fix_api_consumer` |
| Holding the secret | **Vault**, referenced by `M28` | `fix_api_credential.secret_vault_ref` |
| Rate limiting | **`M28`** | `FR-IPF-004`, at the gateway |

**The one-sentence version for a developer:** *`M29` decides who you are and what you may ask for;
`M28` stops you at the door if you ask for something else; and even inside, record rules decide
which rows you see.* Three layers, and **a scope grant does not bypass the third** — this is
`API-10` and it is the answer to the most common partner question, *"I have the scope, why is the
list empty?"*

> **Introspection is the estate's single busiest dependency.** `M29` `T-09` requires ≥ 99.99%
> availability and ≤ 20 ms p95 on the introspection endpoint, with cached introspection at short
> TTL and immediate revocation propagation. A developer does not need to know this — but an
> integration architect sizing a retry policy does, because introspection failure presents as
> `503`, not `401`.

### 4.2 Grant types by audience

| # | Audience | Grant | Credential | Why this one |
|---:|---|---|---|---|
| **GT-1** | **Server-to-server partners** — brands, corporate clients, payment gateways, couriers, sellers with systems, the portal platform | **OAuth 2.0 client credentials** | `client_id` + secret, per environment | No user is present. `05-03` §3.4 names it for the portal contract; the same shape serves every machine consumer |
| **GT-2** | **Native and mobile apps** — `P02` technician, `P09` rider, `P11` auditor | **Authorization code + PKCE** | Public client, no secret | `05-03` §5.1 names PKCE for the Technician API. A secret shipped in an APK is not a secret |
| **GT-3** | **Browser portals with a signed-in human** — `P01`, `P03`…`P08`, `P10`, `P12` | **Authorization code + PKCE**, session-backed | — | `PS-01` single sign-on. The portal never holds a credential store |
| **GT-4** | **Corporate clients requiring federation** | **SAML 2.0 or OIDC federation** into `M29` (`INT-046`, `INT-P04-04`) | Client's own IdP | The client's users authenticate against their own directory. **Which protocol is undecided** — `P04` Q-05 |

**Never permitted, and stated because each has been proposed somewhere in similar estates:**

| Not permitted | Why |
|---|---|
| Resource owner password credentials grant | The consumer would hold end-user passwords. Incompatible with `PS-01` and with MFA |
| Implicit grant | Deprecated in OAuth 2.1; tokens in the URL fragment end up in logs and referrers |
| Long-lived static API keys as the primary credential | No rotation story, no revocation propagation, no scope evolution. `05-03` §3.4 specifies short-lived tokens |
| One credential shared across environments | `NFR-071`, `BRU-IPF-21` — non-production never holds live credentials |
| One credential shared across partners | Destroys attribution, revocation and rate limiting simultaneously |

### 4.3 The scope model

> **The naming convention below is a proposal.** `05-03` §5.1 names twelve API families and their
> auth model; **no scope name appears anywhere in the repository.** `AP-002` `AR-04` requires every
> operation to declare its scope by name, and cannot be enforced until this is decided. Recorded
> as `O-01`.

**Proposed form:**

```
<resource>:<action>[:<qualifier>]
```

| Element | Values | Notes |
|---|---|---|
| `resource` | The `CG-004` controlled term for the business object, singular, snake case — `service_order`, `warranty_claim`, `consignment`, `invoice`, `estate`, `payout` | **Not** the module code and **not** the API family. A family is a routing concept; a scope is a permission concept |
| `action` | `read` · `write` · `approve` · `export` | Four, deliberately. `delete` is absent because `DI-08` permits soft deletion only and hard deletion is an approved, logged procedure, never an API scope |
| `qualifier` | Optional narrowing — `own_brand`, `own_org`, `own_seller` | Used only where the same resource is exposed to more than one external audience |

| Example | Grants |
|---|---|
| `service_order:read` | Read service orders **within the credential's data scope** |
| `service_order:write` | Create and update service orders within scope |
| `warranty_claim:approve:own_brand` | Decide claims for the credential's own brand only |
| `invoice:export:own_org` | Export invoices for the credential's own organisation, subject to `EA-12` |
| `estate:write:own_org` | Bulk-load and amend the client's own estate |

**Eight grant rules.**

| # | Rule | Basis |
|---|---|---|
| **SC-01** | A scope grants **capability**, never **visibility**. Data scope is enforced separately by record rules and cannot be widened by holding a scope | `API-10`, `EA-11` |
| **SC-02** | A request parameter can never widen scope. A credential scoped to one brand asking for another brand's claims receives an empty result or `403` — **never another brand's data, and never a different error revealing that the record exists** | `EA-11`, `AP-002` ED-06 |
| **SC-03** | Scopes are granted at credential issue, from the **contract**. Widening is a commercial and security decision with a recorded approval, not a support action | `EA-01`, `CO-06` of `CG-002` |
| **SC-04** | The **narrowest scope that satisfies the contract** is granted. `IP-10` minimisation applies to capability as well as to data |
| **SC-05** | `approve` is never granted with `write` by default. Approving is a distinct authority and several `05-04` §6 segregation rules depend on the separation | `SOD-01`…`SOD-12` |
| **SC-06** | `export` is separate from `read` and is **rate-controlled and logged** | `EA-12`, `FR-SEC-041` |
| **SC-07** | A scope is **never** granted to an external consumer for a resource with no external audience — `payroll`, `employee`, `recovered_data`, `internal_note`, `model_features` | `05-04` §5, `EA-02` |
| **SC-08** | Every published operation **declares** the scope it requires, in its specification | `AP-002` `AR-04` |

**A scope is not a role.** `05-04` registers 38 roles for humans, with CRUDA per module and an
isolation tier. A scope governs a **credential**, usually machine-held, and is coarser. The
relationship: a credential issued to a partner is granted scopes that are a **subset** of what
role `R38 External Party` may do in that portal, never a superset. Where a machine credential
appears to need more than `R38` holds, that is a role gap to raise against `05-04`, not a scope
to invent — and `M28` §13 already records that `05-04` has no "platform engineer" or "module
developer" role.

### 4.4 Credential lifecycle

**Three environments.** `M28` `fix_api_credential` carries `environment`; the values are not
enumerated anywhere. Proposed:

| Environment | Purpose | Data | Credential |
|---|---|---|---|
| `sandbox` | Partner development and `AP-010` onboarding | Masked/synthetic only (`NFR-071`, `NFR-086c`) | Self-service issue |
| `staging` | Pre-production validation against a release candidate | Masked | Issued on request |
| `production` | Live | Live | **Issued only through the `AP-010` promotion gate** |

| Stage | What happens | Control |
|---|---|---|
| **Register** | Consumer registered in `fix_api_consumer` with name, type, owning party, scopes, rate-limit policy and an accountable **human** owner | `FR-IPF-016`; `FR-SEC-012` requires every non-human identity to have an accountable human owner |
| **Issue** | `client_id` returned; secret shown **once** and stored in the vault | `IP-07`, `NFR-062`. The secret is never retrievable and never logged |
| **Use** | Exchange for a short-lived access token at every session | §4.5 |
| **Rotate** | Consumer self-serves a new secret; **both valid during an overlap window** | `FR-IPF-016`; `/api/v1/platform/consumers/{id}/credentials/rotate` |
| **Expire** | `expires_at` on the credential; alert at 30 days, escalate at 7 (`AUT-IPF-15`) | `platform.credential_expiring` |
| **Revoke** | Immediate, with a recorded reason | Propagates estate-wide **within 60 seconds** (`M29` `T-10`, `BRU-SEC-25`) — not at next token expiry |
| **Deprovision** | On agreement or registration expiry, external access is automatically disabled | `05-04` §9 external expiry |

**Rotation, stated plainly because it is the stage partners skip.**

| # | Rule |
|---|---|
| **CR-01** | Rotation is **self-service** and does not require a support ticket |
| **CR-02** | The old and new secrets are **both valid during the overlap window**, so rotation is never an outage |
| **CR-03** | The overlap window length is **unstated in the repository** — `O-05` |
| **CR-04** | Rotation is required at least as often as `rotates_at`, and immediately on any suspicion of exposure |
| **CR-05** | A secret found in a repository, a log, a configuration file or a support ticket is **treated as compromised and rotated**, not assessed |
| **CR-06** | The webhook signing secret rotates on the same principle with the same overlap (`AP-004` `SIG-07`) — but it is a **different secret** and rotating one does not rotate the other |

### 4.5 Tokens and sessions

| Property | Value | Source |
|---|---|---|
| Token type | OAuth 2.0 / OIDC bearer | `FR-SEC-007` |
| Lifetime | **Short-lived** — figure not stated in the repository | `05-03` §3.4 says "short-lived"; `O-05` |
| Refresh | Supported (`FR-SEC-007` issues, introspects, refreshes and revokes) | `M29` |
| Revocation propagation | **≤ 60 seconds estate-wide** | `M29` `T-10`, `BRU-SEC-25` |
| Introspection | On every gateway request, cached at short TTL | `FR-IPF-002`, `M29` `T-09` |
| Session idle timeout (**human**, external) | 30 minutes | `NFR-069`, `EA-08` |
| Session idle timeout (**human**, internal) | 60 minutes | `NFR-069` |
| Absolute session maximum (**human**) | 12 hours | `NFR-069` |
| Machine-to-machine sessions | **Not addressed by `NFR-069`** — a client-credentials consumer has no session and no idle concept | `O-06` |

**Six token rules for consumers.**

| # | Rule |
|---|---|
| **TK-01** | Cache the token until shortly before expiry. **Do not fetch a token per request** — that multiplies load on the estate's busiest dependency |
| **TK-02** | Handle `401` by fetching a **new** token once, then retrying once. Not in a loop |
| **TK-03** | A revoked token produces `401` within 60 seconds of revocation, mid-flight. Design for it |
| **TK-04** | Never store a token in a URL, a query string, a log or a browser's local storage |
| **TK-05** | A token is scoped to **one environment**. A sandbox token against production returns `401`, never a partial success |
| **TK-06** | Send the token as `Authorization: Bearer <token>`. No other placement is accepted |

### 4.6 Step-up, MFA and financial actions

`EA-09`: MFA is mandatory for any external action with financial consequence. `NFR-065`: step-up
authentication for sensitive actions. `BRU-SEC-02` names payouts, payroll finalisation, data-case
access and bulk export.

| Action | Portal | Step-up required | Basis |
|---|---|:--:|---|
| Warranty claim approval above the value threshold | `P08` | ● | `P08` `T-09`, `05-04` §1 |
| Bulk claim decision | `P08` | ● | `P08` `T-09` |
| Remittance advice upload | `P08` | ● | `P08` `T-09` |
| Rate card publication | `P08` | ● | `P08` `T-09` |
| Consignment reconciliation acknowledgement | `P08` | ● | `P08` §13 |
| Invoice approval | `P04` | ● | `P04` `AC-07` |
| Invoice dispute | `P04` | ● | `P04` `AC-07` |
| Delegation change | `P04` | ● | `P04` `AC-07` |
| Payment initiation | `P04` | ● | `EA-09` |
| Bulk personal-data export | Any | ● | `FR-SEC-041`, `EA-12`, `AUT-SEC-18` |
| Payout release | `P07` | ● | `BRU-SEC-02` |

**The consequence for machine-to-machine integrations, which is the thing that breaks builds.**

> **A step-up challenge requires a human.** A pure server-to-server integration (GT-1) **cannot
> complete any action in the table above.** A brand partner's system can *submit* a claim decision
> for review; a human in `P08` must complete the step-up. An integration designed on the
> assumption that everything in `P08` is available by API will fail at exactly the actions that
> matter commercially.

This is stated here rather than in `AP-007` and `AP-008` because it is a property of the auth
model, not of either partner guide — and because both guides reference it (`CP-01`). **How a
step-up is signalled to a machine caller is unspecified**; the natural shape is a `403` with a
distinguishing code and a `challenge` reference. Recorded as `O-07`.

### 4.7 Rate limits

**What exists today: one number.** `05-03` §3.4 gives 600 requests/minute per portal instance,
burst 100/second, for the portal platform contract. `API-08` requires per-consumer limits with
`X-RateLimit-*` headers and `429` plus `Retry-After`. `FR-IPF-004` implements it. **No limit is
published for any non-portal consumer**, which is `O-03`.

**Proposed policy classes.** Six classes, so that a limit is a *class assignment* at consumer
registration rather than a number invented per partner.

| Class | Sustained | Burst | Typical consumer | Rationale |
|---|---:|---:|---|---|
| `portal` | 600/min | 100/s | The CON-03 portal platform, per instance | `05-03` §3.4 — the only figure with a source |
| `partner-high` | 300/min | 50/s | Payment gateways, couriers — latency-critical, callback-driven | Money and custody paths must not queue behind bulk work |
| `partner-standard` | 120/min | 20/s | Brand partners, corporate clients | Interactive plus modest batch |
| `partner-light` | 60/min | 10/s | Marketplace sellers, referral partners | Individually small, collectively up to 2,000 consumers |
| `bulk` | 20/min | 5/s | Estate loads, bulk request submission, exports | Separate class so a bulk job cannot exhaust an interactive quota |
| `sandbox` | 60/min | 10/s | Every sandbox credential | Low enough to be free to operate; high enough for the `AP-001` golden path |

> **Every figure except `portal` is a proposal.** They are internally consistent and defensible;
> none has a source in the repository. `CG-012` and `CM-R8` require the distinction to be visible,
> so it is.

**Headers.** `API-08` specifies `X-RateLimit-*`. The current IETF work (`draft-ietf-httpapi-ratelimit-headers`)
standardises `RateLimit` and `RateLimit-Policy`. The recommendation is to emit **both** — the
`X-` forms because `API-08` specifies them and partner libraries expect them, and the standard
forms because they are where the industry is going. Additive, and it costs one header:

| Header | Example | Meaning |
|---|---|---|
| `X-RateLimit-Limit` | `120` | Requests permitted in the current window |
| `X-RateLimit-Remaining` | `37` | Requests left in the current window |
| `X-RateLimit-Reset` | `1755500400` | Unix time at which the window resets |
| `RateLimit` | `limit=120, remaining=37, reset=42` | Standard form; `reset` is **seconds remaining**, not an absolute time |
| `RateLimit-Policy` | `120;w=60` | The policy: 120 requests per 60-second window |
| `Retry-After` | `42` | **On `429` only.** Seconds to wait |

**Six consumer rules for limits.**

| # | Rule |
|---|---|
| **RL-01** | Read `X-RateLimit-Remaining` and slow down **before** exhaustion. The headers exist so that `429` is avoidable |
| **RL-02** | On `429`, honour `Retry-After`. **Do not retry immediately and do not retry faster** |
| **RL-03** | Back off exponentially with jitter. Synchronised retries from many consumers are a self-inflicted denial of service |
| **RL-04** | Use the `bulk` class endpoints for bulk work rather than looping an interactive endpoint |
| **RL-05** | A `429` is **not** a failure of the request. Retried correctly with the same `Idempotency-Key`, it succeeds and nothing is duplicated (`API-07`) |
| **RL-06** | Sustained limit breaches are recorded against the consumer, alerted (`AUT-IPF-10`) and feed `M29` anomaly detection. Persistent breach is a commercial conversation, not a technical one |

**Bot protection.** `NFR-068` requires bot detection and abuse protection on all public endpoints
and `FR-IPF-005` implements it at the edge. A legitimate integration is unlikely to trip it; one
that does receives a `403`, not a `429`, and the remedy is registration rather than backoff
(§4.10).

### 4.8 Remediation copy

Written to be quoted directly to a partner by tier-1 support (`OP-001`), which is why it is
sentence-level rather than a rule.

| Situation | What to tell the developer |
|---|---|
| Repeated `401` immediately after issue | "Check you are calling the token endpoint for the same environment as your credential. A sandbox credential returns `401` against production, and the reverse. There is no partial success across environments." |
| `401` mid-session | "Your token expired or was revoked. Fetch a new token once and retry once. If it recurs immediately, your credential has been revoked — contact your integration owner rather than retrying." |
| `403 auth.scope_insufficient` | "Your credential does not hold the scope this endpoint requires. The scope is named in the endpoint's reference page. Widening a scope is a contract change, so raise it with your account manager, not with support." |
| `403 auth.out_of_scope` | "Your credential holds the scope, but the record you asked for is outside your data scope. Check the identifier belongs to your organisation. We will not confirm whether the record exists." |
| `403` bot protection | "Your traffic was classified as automated abuse. Register your consumer and authenticate; unregistered automated traffic on public endpoints is blocked by policy." |
| `429` occasionally | "You are at your limit. Read `X-RateLimit-Remaining` and pace your calls. Honour `Retry-After` on the `429`; do not retry immediately." |
| `429` constantly | "Your integration is sized above its rate-limit class. Move bulk work to the bulk endpoints, or ask your account manager to review the class — a limit change is a commercial decision." |
| Step-up blocking a machine flow | "This action requires a human step-up authentication and cannot be completed by a server-to-server credential. Your system can prepare the action; a user in the portal completes it." |
| Secret lost | "Rotate. We cannot retrieve a secret — it is stored in a vault and was shown once. Rotation is self-service and the old secret stays valid during the overlap window." |
| Secret exposed | "Rotate immediately and tell us. We treat an exposed secret as compromised, not as a risk to assess." |

### 4.9 Endpoint reference

The endpoint reference table required by `CG-009` §3.

| Endpoint | Method | Purpose | Owner | Auth to call it |
|---|---|---|---|---|
| `/api/v1/auth/token` | POST | Issue an access token | `M29` | Client credentials, or authorization code |
| `/api/v1/auth/introspect` | POST | Validate a token and resolve scope | `M29` | **Gateway only** — never called by a consumer |
| `/api/v1/auth/revoke` | POST | Revoke a token or session | `M29` | The token's own credential, or `P03` |
| `/api/v1/auth/step-up` | POST | Step-up challenge for a sensitive action | `M29` | An authenticated human session |
| `/api/v1/auth/mfa/enrol` | POST | Enrol or reset MFA | `M29` | An authenticated human session |
| `/api/v1/platform/consumers` | GET/POST | Register a consumer; list own registrations | `M28` | Portal login; scoped to own consumers |
| `/api/v1/platform/consumers/{id}/credentials/rotate` | POST | Self-service secret rotation | `M28` | The consumer's own owner |
| `/api/v1/platform/apis` | GET | The API registry with versions, status and consumers | `M28` | Portal login |

**`/api/v1/auth/introspect` is listed so that no consumer calls it.** It is `M28`'s edge
dependency at ≥ 99.99% availability; consumer traffic against it would be both useless and
harmful.

### 4.10 Error catalogue — authentication, scope and throttling

The error catalogue table required by `CG-009` §3, for this file's subset. Codes are proposals
pending `AP-006`'s consolidated register, and the two files are authored together so the sets
match.

| HTTP | Code | Cause | Remedy | Retry safe |
|:--:|---|---|---|:--:|
| `400` | `auth.grant_type_unsupported` | Requested a grant type not permitted for this consumer class | Use the grant in §4.2 for your audience | No |
| `401` | `auth.token_missing` | No `Authorization: Bearer` header | Send the token in the header (`TK-06`) | No |
| `401` | `auth.token_invalid` | Malformed, unparseable or wrong-issuer token | Fetch a new token | Once |
| `401` | `auth.token_expired` | Token past its lifetime | Fetch a new token and retry once (`TK-02`) | Once |
| `401` | `auth.token_revoked` | Token or credential revoked | **Do not retry.** Contact your integration owner | No |
| `401` | `auth.environment_mismatch` | Credential issued for a different environment | Use the credential for the environment you are calling (`TK-05`) | No |
| `401` | `auth.credential_expired` | The credential passed `expires_at` | Rotate; you were alerted at 30 and 7 days (`AUT-IPF-15`) | No |
| `403` | `auth.scope_insufficient` | The credential does not hold the required scope | Scope widening is a contract change (`SC-03`) | No |
| `403` | `auth.out_of_scope` | Scope held; the record is outside the credential's data scope | Correct the identifier. **The response never confirms the record exists** (`SC-02`) | No |
| `403` | `auth.step_up_required` | The action requires step-up and the caller is a machine | A human completes it in the portal (§4.6, `O-07`) | No |
| `403` | `auth.mfa_required` | External financial action without MFA | Complete MFA (`EA-09`) | No |
| `403` | `auth.sod_conflict` | The action would breach segregation of duties | A different actor must perform it (`05-04` §6) | No |
| `403` | `auth.bot_blocked` | Traffic classified as automated abuse (`NFR-068`) | Register and authenticate | No |
| `403` | `auth.export_not_permitted` | `export` scope absent, or the export exceeds the permitted volume | `EA-12`; bulk export requires approval and step-up | No |
| `429` | `ratelimit.exceeded` | Sustained or burst limit exceeded | Honour `Retry-After`; back off with jitter (`RL-02`, `RL-03`) | **Yes**, with the same `Idempotency-Key` |
| `429` | `ratelimit.quota_exhausted` | A longer-window quota is exhausted | Wait for the window; or review the class commercially | Yes, after the window |
| `503` | `auth.introspection_unavailable` | The identity service is not answering | Retry with backoff; check the status page | Yes |

### 4.11 What a credential may never do

Stated as absolutes so that `TS-017` can derive negative cases mechanically.

| # | Never | Basis |
|---|---|---|
| **NV-01** | See a record where the credential's party is not a named party | `EA-01` |
| **NV-02** | See cost, margin, internal notes, vendor price or another party's data | `EA-02`, `05-04` §5 |
| **NV-03** | Widen its own scope through any request parameter, header, filter or path | `EA-11`, `API-10` |
| **NV-04** | Complete a financial action without MFA | `EA-09` |
| **NV-05** | Perform an unlimited, unlogged bulk export | `EA-12`, `FR-SEC-041` |
| **NV-06** | Hold live production access from a non-production environment | `NFR-071`, `BRU-IPF-21` |
| **NV-07** | Act as a human — impersonation is not a supported pattern in any portal | `P04` §13, `P08` §13 |
| **NV-08** | Reach a `T-Int` surface, API family or documentation page | `AP-001` §4.5 |
| **NV-09** | Receive an unmasked residency-classified field | `NFR-086`, `AP-012` |
| **NV-10** | Survive its owning agreement. External access is disabled automatically at agreement expiry | `05-04` §9 |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `M29` `FR-SEC-007`, `FR-SEC-012`, `FR-SEC-018` | Token services, service accounts, external party rules |
| `M29` `T-09`, `T-10` | Introspection availability and 60-second revocation — both are consumer-visible behaviours |
| `M28` `FR-IPF-002`…`FR-IPF-004`, `FR-IPF-016`, `FR-IPF-041` | Edge enforcement, consumer registry, vault-held credentials |
| `05-04` §8 `EA-01`…`EA-12` | The external access rules §4.3 and §4.11 restate as scope rules |
| `05-04` §5, §6 | Field-level restrictions and segregation of duties, both enforced through auth outcomes |
| `05-03` §3.4 | The only sourced rate limit in existence |
| `AP-002` `AR-04` | Requires every operation to declare its scope — blocked on `O-01` |
| `AP-006` | The consolidated error catalogue §4.10 feeds |
| `AP-010` | Sandbox credentials and the production promotion gate |
| `AP-012` | Disclosure per counterparty, which scope must not exceed |
| `OP-009` | Identity operations, break-glass, MFA reset |
| `TS-017` | Derives scope and access negative cases from §4.3 and §4.11 |
| `UI-005` | Human-facing session and permission messages; §4.10 is the machine-facing counterpart and the two must not contradict |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per wave gate, and whenever a new external audience is onboarded |
| Trigger for out-of-cycle review | Resolution of `O-01` (scope names) · a rate-limit class change · a new grant type · a change to `NFR-069` · resolution of `P04` Q-05 (federation protocol) · any credential-exposure incident |
| Owner | Platform Engineering Lead, with Security Lead accountable for §4.3, §4.6 and §4.11 |
| Change control | Adding a scope, changing a rate-limit class, or changing a step-up requirement requires CTO **and** Security Lead approval and a `RF-006` entry. Rate-limit **reductions** additionally require notice under `AP-011` — a tightened limit is a breaking change to a live integration |
| Version pinning | Pinned to **API version** (`CG-006` §5) |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **No scope naming convention exists.** `FR-IPF-003` enforces scope at the edge, `EA-11` binds external access to it, and `AP-002` `AR-04` requires every operation to declare it — against a set of names nobody has defined. §4.3 is a proposal. **Until it is decided, every credential is scoped by the judgement of whoever issues it** | Solution Architect with Security Lead | **W1 — before the first credential is issued** |
| **O-02** | **Registered W3; first consumed W1.** `M28` and `M29` are both W1 `P0` and the gateway validates tokens from the first request. `AP-002` (W3) depends on this file's scope names, and `AP-004` (W3) depends on its credential lifecycle. Eighth consecutive category with this defect | Programme Content Lead with Platform Engineering Lead | **W1** |
| **O-03** | **No rate limit is published for any non-portal consumer.** One figure exists — 600/min per portal instance — for one consumer. Nine payment gateways, four couriers, 17+ brands, an unknown number of corporate clients and up to 2,000 sellers have none. §4.7's six classes are proposals | Platform Engineering Lead with Commercial | **W3 — before the first non-portal partner integrates** |
| **O-04** | **`X-RateLimit-*` versus the IETF `RateLimit` fields.** `API-08` specifies the `X-` forms; the standard forms are where partner tooling is heading. Recommendation is to emit both. This is an `05-03` change | Solution Architect | W3 |
| **O-05** | **Three lifetime figures are unstated:** token lifetime ("short-lived", `05-03` §3.4), credential rotation overlap window (`CR-03`), and refresh-token lifetime. A partner cannot implement caching or rotation without the first two | Platform Engineering Lead with Security Lead | **W1 build** |
| **O-06** | **`NFR-069` does not address machine-to-machine sessions.** It sets idle timeouts of 30/60 minutes and an absolute 12-hour maximum — all human-session concepts. A client-credentials consumer has no session, and applying a 12-hour absolute to a machine token is either a needless constraint or an unstated one | Security Lead | W3 |
| **O-07** | **Step-up is unspecified for machine callers.** §4.6 establishes that a server-to-server credential cannot complete eleven named actions. **How that is signalled** — a distinguishing code, a challenge reference, a callback — is undefined, so every partner integration will discover it as an unexplained `403` | Solution Architect with Security Lead | **W4 — `P04` and `P08` both go live in W4** |
| **O-08** | **Corporate federation protocol undecided** (`P04` Q-05, `INT-046` at W6). `GT-4` cannot be documented for a client until SAML 2.0 or OIDC is chosen, and the choice affects `AP-008`'s onboarding sequence | CTO with Account Managers | W4 build |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the §4 subdivision is the only addition and is justified
- [x] The `M29` / `M28` / record-rule split stated in one sentence a developer can act on
- [x] Four grant types mapped to audiences, with five prohibited patterns and the reason for each
- [x] **Scope model proposed with eight grant rules, and marked as a proposal because none exists**
- [x] The scope-is-not-a-role distinction stated, with the escalation route when a credential appears to need more
- [x] Credential lifecycle across three environments with six rotation rules
- [x] Six token rules written as consumer instructions
- [x] **Step-up's consequence for machine-to-machine integrations stated plainly — eleven actions no server credential can complete**
- [x] Six rate-limit classes proposed, with the one sourced figure distinguished from the five proposals
- [x] Both `X-RateLimit-*` and standard `RateLimit` headers specified, with the divergence referred upward
- [x] Remediation copy written to be quoted directly by tier-1 support
- [x] Seventeen authentication, scope and throttling errors with cause, remedy and retry safety
- [x] Ten absolute prohibitions stated so `TS-017` can derive negative cases mechanically
- [x] All internal links resolve
- [x] Eight open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` no scope names exist — outstanding; blocks `AP-002` `AR-04` and every credential issue**
- [ ] **`O-03` no partner rate limits published — outstanding**
- [ ] **`O-05` token and rotation lifetimes unstated — outstanding**
- [ ] **`O-07` machine step-up unsignalled — outstanding; surfaces as an unexplained `403` at W4**
- [ ] Named approvers recorded — **pending Content Design Lead and CTO**
- [ ] Bengali counterpart — n/a; developer audience, English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
