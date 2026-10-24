---
id: IN-006
title: Webhook, Callback & Partner Push Specification
category: 04 — Integration & API Engineering
code: IN
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Integration Architect
approver: CTO with Security Lead
standards_basis: >
  Standard Webhooks specification · HMAC-SHA256 (FIPS 198-1) · RFC 6234 (SHA-2) ·
  RFC 9110 HTTP Semantics · RFC 3339 · OpenAPI 3.1 `webhooks` object ·
  OWASP SSRF prevention guidance
traces_to: >
  PGD-000 IN-006 · 05-03 §3.3, §5.1 · M28 FR-IPF-034, -035, -036, -037 · CD-127 cd_webhook ·
  audit AP-04 (high) · AP-004 §4.4 · IN-001 §5.4 PT-05 · IN-003 §5 external channel ·
  NFR-062, NFR-068
depends_on: IN-001 · IN-003 · IN-005 (consumer register) · IN-002 (payload schemas)
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 17:25 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# IN-006 — Webhook, Callback & Partner Push Specification

### Category 04 · Code `IN` · Standard Webhooks · HMAC-SHA256

---

> **This document closes the second of the three unmade Wave 1 platform decisions.**
>
> `AUDIT-016` `AP-04` (high, open): *"`FR-IPF-035` requires every outbound webhook to be signed.
> `FR-IPF-037` requires inbound signature verification. `05-03` §5.1 registers the receiver family
> with 'signature verification'.*
>
> ***No document in the module repository states an algorithm, a header set, a signed-content
> construction, a replay window, a rotation-overlap behaviour, or a comparison requirement.***"
>
> And its compounding finding: *"extraction found **no webhook management endpoint registered
> anywhere**"* — `M28` §12.5 lists eighteen platform endpoints and **none** for registration, testing
> or secret rotation, despite `FR-IPF-034` requiring a registry and `fix_webhook_endpoint` existing
> as an entity.
>
> **Why it cannot wait for W4.** The CON-03 portal platform consumes **eleven webhooks from W1**
> (`05-03` §3.3). Until the scheme is decided, either the portal accepts unverified POSTs, or each
> side implements a different scheme and the integration fails at the first delivery. **A forged
> `payment.received` to an unverified endpoint is a financial-fraud vector, and the endpoint URL is
> discoverable by anyone who has seen one delivery.**

---

## 1. Purpose

A webhook is the estate's only mechanism for telling an external system something happened without
being asked. It is also the only inbound HTTP surface that does not authenticate with a bearer token.
Both properties make it the sharpest edge in the integration surface.

This document specifies both directions: **outbound** — the signature scheme, delivery guarantees,
retry ladder, auto-disable, subscription management and the endpoints `AP-04` found missing — and
**inbound** — the receiver contract, per-provider verification, and the read-back rule that makes a
notification a hint rather than an authority.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **The outbound signature scheme** — the `AP-04` ratification candidate, in full |
| 2 | The delivery payload envelope and its relationship to the `external` channel |
| 3 | Subscription and endpoint registration, testing, and secret rotation |
| 4 | **The three management endpoints `AP-04` found missing** |
| 5 | Delivery guarantees, ordering, retry ladder, dead-lettering |
| 6 | Auto-disable and re-enablement |
| 7 | **The twelve consumer obligations** |
| 8 | The **inbound** receiver contract, and per-provider verification |
| 9 | **`PT-05` read-back** — why an inbound webhook is never authoritative |
| 10 | SSRF and endpoint-registration abuse prevention |
| 11 | Which events are webhook-eligible, and which never are |
| 12 | CI and runtime gates `FF-77`…`FF-84` |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| The event catalogue and payload schemas | `IN-003` | A webhook **delivers** an event; it does not define one |
| Per-external-system contracts | `IN-004` | An ICD names which provider sends what; this specifies how it is verified |
| Payment-specific flows | `IN-007` | The rails' read-back is applied there per rail |
| Consumer registration, scopes, deprecation | `IN-005` | A webhook consumer is a consumer |
| Bus mechanism and outbox | `AR-009` | The `external` channel is fed from it |
| Notification to **people** | M27, `NT-*` | **A notification is a command, not an event** (`AR-009` E4). A webhook is machine-to-machine |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **CTO and Security Lead** | §4 is the scheme awaiting their ratification |
| Partner developers | §4, §5, §8 — everything needed to consume a 1000FiX webhook correctly |
| Integration engineers | §9, §10 — the inbound receiver |
| Platform engineers | §6, §7 — dispatcher, retry, auto-disable |
| `IN-004` ICD authors | §9.3's per-provider table is each ICD's verification clause |
| QA lead | §11's negative cases are a test charter |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure |
|---|---|---|
| **Standard Webhooks specification** | §4 adopts it: `webhook-id`, `webhook-timestamp`, `webhook-signature`; HMAC-SHA256 over `id.timestamp.body`; `v1,` prefix; base64 signature; **300-second tolerance** | **None.** Adopted *because* it is what a partner's existing library already implements — the interoperability argument, not a technical preference |
| **HMAC-SHA256** (FIPS 198-1, RFC 6234) | §4.2 | None |
| **RFC 9110** | Status semantics for consumer responses (§5.5) | None |
| **OpenAPI 3.1 `webhooks` object** | §3.3 — the delivery contract is published as OpenAPI `webhooks`, **not** AsyncAPI | A delivery genuinely is an HTTP request; AsyncAPI describes the *channel*, OpenAPI the *call* |
| **OWASP SSRF prevention** | §7.2 — URL validation at registration | None |

### 2.2 Source material

| Source | Contribution |
|---|---|
| `05-03` §3.3 | **The eleven CON-03 webhooks, live from W1** — of which `IN-001` §9.2 measured **8 published by no module** |
| `05-03` §5.1 | The `/hooks/v1/*` receiver family with "signature verification" and nothing more |
| `M28` `FR-IPF-034`…`037`, §12.5 | Registry required, signing required, verification required — **and no endpoint to manage any of it** |
| **`AP-004` §4.4** | The proposed scheme, `SIG-01`…`SIG-09`, marked a proposal throughout per `CG-012` |
| `AP-004` §4.5–§4.12 | Delivery, auto-disable, twelve consumer obligations, per-provider verification, negative cases |
| `AUDIT-016` `AP-04` | The finding, and the missing-endpoint compounding finding |
| `IN-001` §5.4 | `PT-05` — an inbound webhook is a hint, never authority |
| `IN-003` §5 | The `external` channel and the CloudEvents mapping |

### 2.3 Audit findings this document closes

| Finding | Disposition |
|---|---|
| **`AP-04` (high)** — no signature scheme anywhere | **Closed on ratification.** §4 states algorithm, headers, signed content, tolerance, rotation and comparison |
| **`AP-04` compounding** — no webhook management endpoint registered | **Closed.** §7 specifies three; they are **issued as executable OpenAPI** in `IN-002_artefacts/platform/openapi.yaml` |
| `AP-004` `O-01` | The scheme, ratified here |
| `AP-004` `O-03` | The three endpoints, registered here |
| `IN-001` §9.2 — 8 of 11 CON-03 webhooks have no producer | **Not this document's to close** — `IN-003` `RE-02`. §12 records which of the eleven are deliverable today |

---

## 3. Two Directions, Two Contracts

`AP-004` §4.1 makes the point and it is worth keeping: **outbound and inbound are not symmetric.**

| | **Outbound** (1000FiX → consumer) | **Inbound** (provider → 1000FiX) |
|---|---|---|
| We control | The scheme, the retry ladder, the payload | **Nothing.** We accept what the provider sends |
| Signature | **Ours** — §4 | **Theirs** — §9.3, one per provider |
| Authority of the content | It **is** the fact — we produced it | **A hint only.** `PT-05` requires read-back |
| Failure of delivery | Our retry ladder, our dead-letter | Their retry ladder; we must be **idempotent and fast** |
| Registration | The consumer registers with us (§7) | We register a URL with them, out of band |

### 3.1 The single most consequential asymmetry

> **Outbound, a signature is sufficient. Inbound, it never is.**
>
> Outbound we are the source of truth, so a correctly signed delivery *is* the fact. Inbound, the
> counterparty is the source of truth and the webhook is their **claim** about it. `IN-001-D-06`
> requires read-back, and §9.2 gives the specific reason per rail.

### 3.2 What is never a webhook

| Not a webhook | Why | What it is instead |
|---|---|---|
| A notification to a person | `AR-009` E4 — a notification is a **command**, and a replay would re-send every SMS ever sent | An M27 command, triggered by a consumer reacting to an event |
| A high-frequency telemetry stream | A delivery ladder per GPS ping | WebSocket (`IN-001` §9.3) |
| A bulk export | Payload ceilings; retries multiply the volume | `202` + `job_url` (`API-12`) |
| An internal module-to-module message | Webhooks are for crossing the boundary | The `domain` channel (`AR-009`) |

### 3.3 Where the outbound contract is published

As **OpenAPI 3.1 `webhooks`**, alongside the eleven context contracts — because a delivery is an HTTP
POST the consumer must implement, and OpenAPI is what generates the handler stub. `IN-003`'s AsyncAPI
describes the `external` **channel**; this describes the **call**.

---

## 4. The Outbound Signature Scheme

> **Status: ratification candidate.** `AP-004` §4.4 proposed it and marked it a proposal throughout,
> correctly (`CG-012`, `CM-R8`). This document carries it forward **unchanged in substance**, adds
> the four rules a partner-facing scheme needs and `AP-004` did not state, and puts it to the CTO and
> Security Lead. **Until ratified, `AP-04` remains open and no partner webhook may go live.**

### 4.1 Why this scheme and not a bespoke one

| Option | Assessment |
|---|---|
| **Standard Webhooks** | ✅ **Chosen.** A partner's existing library — JavaScript, Python, Java, Kotlin, Go, Ruby, PHP, C#, Rust, Elixir — already implements it. **Zero integration cost on their side is worth more than any marginal design preference on ours** |
| Bespoke HMAC | Every partner writes and gets wrong the same code; §5.3's raw-body trap is hit repeatedly |
| Mutual TLS | Strong, but a client-certificate lifecycle across 500–2,000 marketplace sellers is not operable |
| JWS / detached JWS | Sound, but heavier tooling and no ecosystem advantage here |
| **Nothing** | The current position. `AP-04` |

### 4.2 The construction

```
signed_payload = webhook-id + "." + webhook-timestamp + "." + raw_request_body
signature      = base64( HMAC-SHA256( signing_secret, signed_payload ) )
webhook-signature = "v1," + signature
```

**Three headers travel together:**

| Header | Content |
|---|---|
| `webhook-id` | Unique delivery identifier, UUID. **The consumer's deduplication key** |
| `webhook-timestamp` | Unix seconds at signing |
| `webhook-signature` | `v1,<base64>` — space-separated list during rotation |

### 4.3 The nine rules

Carried from `AP-004` §4.4:

| # | Rule | Reason |
|---|---|---|
| **SIG-01** | **HMAC-SHA256.** Not SHA-1, not MD5 | The interoperable default; every partner library supports it |
| **SIG-02** | The signature covers **`webhook-id`, `webhook-timestamp` and the raw body**, joined by `.` | Signing the body alone permits replay; the timestamp is what makes a replay window enforceable |
| **SIG-03** | The consumer verifies against the **raw body bytes**, before any JSON parsing or re-serialisation | **The single most common consumer implementation error.** Re-serialising changes whitespace and key order and breaks the signature |
| **SIG-04** | Comparison is **constant-time** | A byte-by-byte comparison leaks the signature through timing |
| **SIG-05** | Reject if `webhook-timestamp` is more than **5 minutes** from the consumer's clock, **in either direction** | Replay prevention. 300 s is the specification's recommendation and tolerates ordinary skew |
| **SIG-06** | The consumer **also** records `webhook-id` and rejects a repeat within at least the replay window — **ideally permanently** | Timestamp tolerance alone permits replay inside the window. **Both controls are required; neither is sufficient** |
| **SIG-07** | `webhook-signature` may carry **more than one signature**, space-separated, during rotation. The consumer accepts if **any** verifies | Zero-downtime rotation. Without it, **every rotation is an outage on the consumer's side** |
| **SIG-08** | The signing secret is issued **once**, vault-stored, consumer-rotatable, and **never logged** | A secret in a delivery log is a secret in a log-aggregation system |
| **SIG-09** | An unsigned or wrongly-signed delivery is **rejected with `401` and not processed** | And is a **security event on the 1000FiX side** if 1000FiX did not send it |

### 4.4 Four rules this document adds

`AP-004` wrote a developer *guide*; a partner-facing *standard* needs four more:

| # | Rule | Why |
|---|---|---|
| **SIG-10** | **The secret is per endpoint, not per consumer.** A consumer with three endpoints holds three secrets | Compromise of one endpoint's secret does not compromise the others, and a single endpoint can be rotated without disturbing the rest |
| **SIG-11** | Secret length is **at least 24 bytes of CSPRNG output**, base64-encoded, and it is **never derived** from a consumer identifier | A derivable secret is not a secret |
| **SIG-12** | **A secret is rotated at least every 12 months**, and immediately on a suspected compromise. `platform.credential_expiring` fires at 30 and 7 days | An unrotated secret has an unbounded exposure window; `IN-005` §6 already forbids perpetual credentials |
| **SIG-13** | The scheme version prefix `v1,` is **part of the contract**. A future `v2` is a **breaking change** under `IN-005` §8.3 and carries the six-month notice | Otherwise a scheme upgrade breaks every consumer silently |

### 4.5 What the scheme does not do

Stated so it is not assumed:

| Not provided | Provided by |
|---|---|
| **Confidentiality** | TLS |
| **Authentication of the consumer to 1000FiX** | Nothing — the consumer is identified by which endpoint we called |
| Protection against a consumer's own compromised secret | Rotation (SIG-12) |
| **Ordering** | Nothing. §5.4 |
| **Exactly-once delivery** | Nothing. §5.2 — at-least-once, and the consumer deduplicates |

---

## 5. Outbound Delivery

### 5.1 The payload

```json
{
  "webhook_id": "018f2c...",
  "event_type": "service_order.status_changed",
  "schema_version": "1.0",
  "occurred_at": "2026-08-18T09:14:22Z",
  "delivered_at": "2026-08-18T09:14:23Z",
  "attempt": 1,
  "data": { }
}
```

| Field | Note |
|---|---|
| `webhook_id` | Matches the `webhook-id` header. **The deduplication key** |
| `event_type` | From the `IN-003` registry |
| `occurred_at` vs `delivered_at` | **When the fact happened** vs when we attempted delivery. A retried delivery has a later `delivered_at` and the **same** `occurred_at` |
| `attempt` | Lets a consumer log retry pressure without inferring it |
| `data` | **The `external` (E2) shape** — boundary-shaped, `actor` removed (`IN-003` §5.4). **Not** the internal payload |

> **`data` is the `external` channel's shape, and that is a deliberate constraint.** A webhook may
> never carry a field the E2 registration does not declare, which is what makes `IP-10` minimisation
> checkable at the boundary rather than trusted at the dispatcher.

### 5.2 Guarantees

| Property | Value |
|---|---|
| Delivery | **At-least-once.** A consumer will receive duplicates and must deduplicate (SIG-06) |
| Ordering | **None guaranteed** (`IN-001` §5.2). A consumer that assumes order is defective |
| Latency target | 95% delivered within **5 s** of publication, consistent with `NFR-043` |
| Timeout | **10 s** for the consumer to acknowledge |
| Payload ceiling | 256 KB. Larger uses the **claim check** — a reference, never bytes |

### 5.3 The retry ladder

| Attempt | Delay after the previous |
|---|---|
| 1 | immediate |
| 2 | 5 s |
| 3 | 30 s |
| 4 | 5 min |
| 5 | 30 min |
| 6 | 2 h |
| 7 | 6 h |
| 8 | 12 h |

**Exponential with jitter**, then **dead-letter with alert**. Total window ≈ 21 hours, which covers a
consumer's overnight outage without indefinite retention.

| Rule | Detail |
|---|---|
| **Retry on** | Timeout, connection failure, `5xx`, `429` (honouring `Retry-After`) |
| **Never retry on** | `2xx` (success), `410 Gone` (**disable immediately**), `400`/`422` (**a consumer bug — retrying will not fix it**) |
| **On `401`/`403`** | Retry twice, then treat as a configuration failure and alert both sides — usually a secret mismatch after rotation |
| Dead-letter | Full envelope, headers, all attempts and responses → `dlq.external`, retained **90 days, never auto-purged** |

### 5.4 Ordering — and the one thing a consumer must do

Deliveries are independent HTTP requests, so `service_order.status_changed` for the same order may
arrive out of order after a retry.

> **The consumer's obligation:** compare `occurred_at` against the last processed value for that
> aggregate and **discard the older**. This is a two-line control that eliminates the single most
> common webhook data-corruption bug, and it is why `occurred_at` is in the payload rather than left
> to the consumer to infer from `data`.

### 5.5 The consumer response contract

| Status | Meaning to the dispatcher |
|---|---|
| `200`, `202`, `204` | **Accepted.** Stop |
| `410` | **Endpoint gone.** Disable immediately; notify the owner |
| `400`, `422` | Consumer rejected the payload. **Do not retry**; record and alert both sides |
| `401`, `403` | Retry twice, then alert — usually a rotation mismatch |
| `429` | Retry honouring `Retry-After` |
| `5xx`, timeout | Retry per the ladder |

> **Acknowledge fast, work later.** A consumer that does its processing before responding will time
> out under load and receive the whole ladder. The correct pattern is: verify, deduplicate, persist,
> **respond `202`**, then process.

### 5.6 Auto-disable and re-enablement

| Rule | Detail |
|---|---|
| **Disable after five consecutive failures** | `05-03` §7's threshold |
| On disable | Publish `platform.webhook_endpoint_disabled`; notify the endpoint owner **through the `IN-005` §7 register contact** |
| Undelivered events | Held in `dlq.external` for **90 days**, replayable on re-enablement |
| **Re-enablement is deliberate** | The owner calls `testWebhookEndpoint`, it must succeed, then re-enables. **Never automatic** — an automatically re-enabled endpoint flaps |
| Backfill on re-enablement | Optional and **explicit**, subject to the replay-class rule (`IN-003` §8.3): an `R3` consumer is not backfilled without a named operator decision |

---

## 6. The Twelve Consumer Obligations

Published to partners verbatim (`AP-004` §4.7 basis). **A consumer that does all twelve cannot be
broken by anything in §5.**

| # | Obligation |
|---|---|
| **CO-01** | **Verify the signature on every delivery**, against the raw body bytes, in constant time |
| **CO-02** | **Reject deliveries outside the 5-minute timestamp window** |
| **CO-03** | **Deduplicate on `webhook-id`** — permanently if you can |
| **CO-04** | **Respond within 10 seconds.** Acknowledge first, process after |
| **CO-05** | **Be idempotent.** You will receive duplicates |
| **CO-06** | **Tolerate out-of-order delivery.** Compare `occurred_at`; discard the older |
| **CO-07** | **Tolerate new fields.** Additive change is not breaking; do not validate strictly on responses |
| **CO-08** | **Return the right status.** `2xx` stops retries; `400` stops them permanently |
| **CO-09** | **Serve HTTPS with a valid certificate.** Plain HTTP is refused at registration |
| **CO-10** | **Keep the secret out of logs**, source control and error reports |
| **CO-11** | **Support multi-signature during rotation** — accept the delivery if any signature verifies |
| **CO-12** | **Monitor your own endpoint.** Five consecutive failures disable it, and you will be notified but not rescued |

---

## 7. Registration and Management

### 7.1 The three endpoints `AP-04` found missing

`M28` §12.5 lists eighteen platform endpoints and none for webhooks. **Registered here, and issued as
executable OpenAPI** in
[`IN-002_artefacts/platform/openapi.yaml`](./IN-002_artefacts/platform/openapi.yaml):

| Operation | Path | Purpose |
|---|---|---|
| `registerWebhookEndpoint` | `POST /api/v1/platform/webhook-endpoints` | Register a URL and event set; **returns the signing secret once** |
| `listWebhookEndpoints` | `GET /api/v1/platform/webhook-endpoints` | The consumer's own endpoints and their state |
| **`testWebhookEndpoint`** | `POST /api/v1/platform/webhook-endpoints/{id}/test` | Send a **fully signed** test delivery and report what the consumer returned |
| **`rotateWebhookSecret`** | `POST /api/v1/platform/webhook-endpoints/{id}/rotate-secret` | Rotate **with an overlap window** |

> **`testWebhookEndpoint` is not a convenience.** It is how `SIG-03` — verify against raw bytes — is
> diagnosed before a real event depends on it. The response reports the consumer's status, latency
> and body excerpt, which is the difference between "it works" and a partner discovering at
> go-live that their framework re-serialised the body.

### 7.2 URL validation — SSRF prevention

**A registration endpoint that accepts an arbitrary URL is a server-side request forgery primitive.**
Validation at registration, and again before each delivery:

| # | Check |
|---|---|
| **UV-01** | **HTTPS only.** Plain HTTP refused |
| **UV-02** | The host must resolve to a **public** address. Loopback, link-local, RFC 1918 and cloud metadata addresses are refused |
| **UV-03** | **Re-resolve before delivery** and re-check — DNS can be rebound after registration |
| **UV-04** | No redirects followed. A `3xx` is a delivery failure, not a hop |
| **UV-05** | Certificate validation is **mandatory and non-overridable** |
| **UV-06** | A **challenge** must be answered at registration, proving control of the endpoint |
| **UV-07** | Delivery originates from the **Z6 egress proxy** to an allow-listed destination, like every other outbound call (`AR-001` §8.1) |
| **UV-08** | A per-consumer cap on registered endpoints |

### 7.3 Subscription

| Rule | Detail |
|---|---|
| Events are chosen **by name** from the `IN-003` registry | An unregistered name is refused — a subscription to an event nobody publishes is silently dead (`IN-003` `G-04`) |
| A subscription requires the **corresponding read scope** (`IN-005` §5.5) | A consumer cannot receive by webhook what it could not read by API |
| Subscriptions appear in the **consumer register** (`IN-005` §7) | So producers know who they will break |
| Only **E2 `external`-channel** events are subscribable | An internal `domain` event has no external shape and must not be exposed |

### 7.4 Which events are webhook-eligible

| Eligible | Not eligible |
|---|---|
| E2 integration events with a declared external shape | E1 domain events with no E2 shape |
| Events whose consumer holds the matching read scope | `platform.*` E3 events — internal diagnostics |
| Coarse projections designed for external surfaces (`IN-003` §7.3.3) | High-frequency telemetry — WebSocket instead |
| | Anything whose payload carries a `residency_restricted` field — **which is none, by `IN-003` `SC-07`** |

---

## 8. The Inbound Receiver

### 8.1 The family

`/hooks/v1/{integration}` — **the only API family that does not authenticate with a bearer token**
(`IN-001` `AA-08`). Six receiver paths are declared across the module specifications:

`/hooks/v1/{integration}` · `/hooks/v1/agent/checkin` · `/hooks/v1/agent/telemetry` ·
`/hooks/v1/biometric/{device}` · `/hooks/v1/channel/{provider}` · `/hooks/v1/courier/{partner}`

### 8.2 The eight-step contract

Every inbound webhook, without exception:

| # | Step | Note |
|---|---|---|
| 1 | Receive | |
| 2 | **Verify the provider's signature** per §9.3 | `401` if absent or wrong, and a **security event** |
| 3 | **Deduplicate** on the provider's delivery id | |
| 4 | **Persist the raw envelope verbatim** | Audit; `AP-012` §4.8 ingress logging |
| 5 | **Acknowledge fast** — `2xx` within the provider's tolerance, before any work | |
| 6 | Raise an internal **P2 command** | |
| 7 | **Read the authoritative state back from the provider's own query API** | **`PT-05`** |
| 8 | Apply the state change **from that read** | Never from the webhook body |

### 8.3 Why step 7 is not optional

| Rail | The specific reason | Verified |
|---|---|---|
| **SSLCOMMERZ** | Its published integration requirement is that an IPN — carrying an **MD5** `verify_sign` — is re-validated through the **Transaction Validation API** returning `VALID`/`FAILED`/`CANCELLED` before the merchant treats a payment as complete. **MD5 is not collision-resistant**, so the validation call is the actual control (`IN-004` `IN-A-15`) | 2026-08-18 |
| **bKash** | The documented flow is `create → execute → **query**`. The query is the authoritative read | 2026-08-18 |
| **Nagad** | Response signatures are verified against Nagad's RSA public key; the read-back is where that verification actually protects state | 2026-08-18 |
| **Couriers** | Verification support is **inconsistent across the three**. Where none exists, read-back plus IP allow-listing is the only control | 2026-08-18 |

> **A forged `payment.received` against an unverified endpoint is a financial-fraud vector, and the
> endpoint URL is discoverable by anyone who has seen one delivery** (`AP-04`). Step 7 is what makes
> forgery worthless: a forged notification triggers a read-back that disagrees, and the read wins.

### 8.4 Per-provider verification

**Every provider is different, and the differences are load-bearing.** This table is each ICD's
verification clause (`IN-004` §2.4 section 5).

| Provider | Mechanism | Consequence for our implementation |
|---|---|---|
| **SSLCOMMERZ** | **MD5** `verify_sign` over the documented value set, using the store password | Verify, **then** call Transaction Validation. Never treat the signature as sufficient |
| **bKash** | Callback returns to our URL; authority is the `payment/status` query | Treat the callback as a **trigger only** |
| **Nagad** | **RSA signature verification** against Nagad's public key | Distinguish a **signature failure** (integrity event) from a **payment failure** (`dependency.*`) — they must not share an error code |
| **WhatsApp Business Cloud** | Provider-specific signature header over the raw body | Same raw-body trap as `SIG-03` |
| **Couriers** (Pathao, RedX, Steadfast) | **Inconsistent; some offer none** | Where absent: **IP allow-list + mandatory read-back**, recorded in the ICD as a stated weakness, not an assumed strength |
| **Biometric devices** | SDK / file, on the internal network | Not internet-facing; network isolation is the control |
| **Monitoring agents** | Agent credential | Rate-limited per device; a compromised agent must not be able to flood |

> **`IN-A-22` (medium).** Three of the seven provider rows are **"inconsistent" or "none"**. An
> inbound surface with no signature is authenticated only by URL obscurity and network position.
> Where a provider offers a signature and we have not enabled it, that is a defect; **where they
> offer none, it must be recorded in the ICD as an accepted weakness with a compensating control**,
> not silently tolerated. `IN-004` §17 does this for the couriers.

---

## 9. Negative Cases

The test charter (`IN-008`), and the list `AP-004` §4.12 asked `TS-017` for:

| # | Case | Expected |
|---|---|---|
| N-01 | Outbound: consumer returns `500` five times | Ladder runs, endpoint auto-disabled, owner notified, events in `dlq.external` |
| N-02 | Outbound: consumer returns `410` | **Immediate disable**, no retries |
| N-03 | Outbound: consumer times out at 11 s | Treated as a failure; retried |
| N-04 | Outbound: duplicate delivery of the same `webhook-id` | Consumer deduplicates; no double effect |
| N-05 | Outbound: two deliveries for one aggregate arrive out of order | Consumer discards the older by `occurred_at` |
| N-06 | Outbound: rotation in progress, consumer holds the old secret | **Multi-signature — delivery still verifies** |
| N-07 | Outbound: registration of an RFC 1918 URL | **Refused** (`UV-02`) |
| N-08 | Outbound: registered host later resolves to a private address | **Refused at delivery** (`UV-03`) |
| N-09 | Outbound: registration of an unregistered event name | Refused (`IN-003` `G-04`) |
| N-10 | Inbound: unsigned POST | `401`, not processed, **security event** |
| N-11 | Inbound: valid signature, timestamp 10 minutes old | Rejected (`SIG-05`) |
| N-12 | Inbound: replay of a previously seen `webhook-id` inside the window | Rejected (`SIG-06`) |
| N-13 | Inbound: signature valid, **read-back disagrees** | **The read-back wins**; divergence alert |
| N-14 | Inbound: body re-serialised by a proxy | Signature fails — the `SIG-03` case, and the reason `testWebhookEndpoint` exists |
| N-15 | Inbound: 1,000 deliveries in one second | Rate-limited per consumer; acknowledged, queued, not dropped |
| N-16 | Secret appears in a delivery log | **Fails `FF-82`** |

---

## 10. Gates

| # | Check | Timing | Enforcement |
|---|---|---|---|
| **FF-77** | Every outbound delivery carries all three headers and a `v1,` signature | Runtime sample + CI | Fail |
| **FF-78** | No `/hooks/v1/*` handler processes a request before signature verification | CI static analysis | Fail |
| **FF-79** | Every `/hooks/v1/*` handler performs a **read-back** before applying a state change (`PT-05`) | CI static analysis | Fail |
| **FF-80** | Every registered endpoint URL passes `UV-01`…`UV-05` at registration **and** before delivery | Runtime | Block |
| **FF-81** | Every webhook subscription names an event in the `IN-003` registry with an **E2 external shape** | CI | Fail |
| **FF-82** | **No signing secret appears in any log, trace, DLQ entry or error body** | Log scanning | Alert + fail |
| **FF-83** | Every endpoint's secret is younger than 12 months (`SIG-12`) | Daily | Alert |
| **FF-84** | No webhook payload carries a field outside its E2 registration | Runtime sample | Fail |

---

## 11. What Can Actually Be Delivered Today

**An honest statement of readiness, because the eleven CON-03 webhooks are a W1 commitment.**

| `05-03` §3.3 webhook | Published by a module? | Deliverable at W1? |
|---|:--:|---|
| `service_order.created` | ✅ | **Yes** |
| `technician.dispatched` | ✅ | **Yes** |
| `technician.location_updated` | ✅ | Yes — but see below |
| `service_order.status_changed` | ✘ | **No — a projection with no projector** (`IN-003` §7.3.3) |
| `estimate.issued` | ✘ | **No — a rename** (`IN-003` §7.3.2) |
| `invoice.created` | ✘ | **No — a rename** |
| `contract.expiring` | ✘ | **No** |
| `consignment.status_changed` | ✘ | **No — a projection with no projector** |
| `loyalty.points_changed` | ✘ | **No — genuinely absent** |
| **`payment.received`** | ✘ | **No — genuinely absent, and it is the money path** |
| `catalogue.updated` | ✘ | **No — genuinely absent** |

> **Three of eleven are deliverable.** The remaining eight are `IN-003` `RE-02` and `RE-05`, Wave 1.
> **This document can specify how a webhook is signed and delivered; it cannot invent the events.**
>
> **`technician.location_updated` carries a caveat**: as a per-ping webhook it is a delivery ladder
> per GPS update. `IN-001` §9.3 rules it **throttled and delivered over the existing WebSocket**, not
> as a webhook. `05-03` §3.3 lists it as a webhook, and that listing is superseded.

---

## 12. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `IN-006-D-01` | Outbound signature scheme | Bespoke HMAC · mTLS · JWS · **Standard Webhooks** · none | **Standard Webhooks** | A partner's existing library already implements it. **Zero integration cost on their side beats any marginal design preference on ours** | Closes `AP-04` on ratification |
| `IN-006-D-02` | Replay protection | Timestamp only · id only · **both** | **Both** | Timestamp tolerance alone permits replay inside the window; an id ledger alone permits an indefinitely delayed delivery | `SIG-05` + `SIG-06` |
| `IN-006-D-03` | Secret granularity | Per consumer · **per endpoint** | **Per endpoint** | One compromised endpoint must not compromise the others, and one endpoint must be rotatable alone | `SIG-10` |
| `IN-006-D-04` | Rotation | Hard cutover · **overlap with multi-signature** | **Overlap** | Without it every rotation is a consumer-side outage — a rotation endpoint without it would close `AP-04` in name only | `SIG-07`; `rotateWebhookSecret` |
| `IN-006-D-05` | Inbound trust | Signature sufficient · **signature + read-back** | **Read-back** | SSLCOMMERZ's own requirement, bKash's `create→execute→query`, and MD5's collision weakness | `PT-05`; `FF-79` |
| `IN-006-D-06` | Delivery contract language | AsyncAPI · **OpenAPI 3.1 `webhooks`** | **OpenAPI** | A delivery genuinely is an HTTP POST the consumer implements; OpenAPI generates the handler stub | `IN-003` describes the channel, this the call |
| `IN-006-D-07` | Re-enablement after auto-disable | Automatic on next success · **deliberate, after a passing test** | **Deliberate** | An automatically re-enabled endpoint flaps, and each flap costs a retry ladder | §5.6 |
| `IN-006-D-08` | `technician.location_updated` | Webhook per `05-03` §3.3 · **throttled WebSocket** | **WebSocket** | A delivery ladder per GPS ping | Supersedes `05-03` §3.3 for that row |

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | **Is the §4 scheme ratified?** Until it is, either the CON-03 portal accepts unverified POSTs from W1, or the two sides implement different schemes and the first delivery fails | **CTO + Security Lead** | **W0 — blocking** | Every partner push; `AP-04` |
| Q-02 | Do the three couriers offer **any** signature mechanism? Two ICDs currently assume none (`IN-A-22`) | Integration Architect | **W3 − 2 months** | `IN-004` §17 |
| Q-03 | Does the CON-03 portal platform implement Standard Webhooks, or does it need a shim? | Portal platform owner | **W1** | The eleven W1 webhooks |
| Q-04 | Who **operates** the dead-letter triage for `dlq.external` — platform or the integration owner? | Programme Director | W1 | §5.3, `SV-*` |
| Q-05 | Is a **backfill on re-enablement** offered to partners as a product feature, or only on request? | Integration Architect | W3 | §5.6 |

---

## 14. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **An algorithm, header set, signed-content construction, replay window, rotation behaviour and comparison requirement all exist** — the six things `AP-04` found absent | §4.2, §4.3 |
| AC-02 | The scheme is chosen for **interoperability**, with the alternatives assessed | §4.1, `IN-006-D-01` |
| AC-03 | Rotation does not break consumers | `SIG-07`, `IN-006-D-04` |
| AC-04 | **The three missing management endpoints are registered**, and issued as executable contracts | §7.1; `IN-002_artefacts/platform/openapi.yaml` |
| AC-05 | Registration cannot be used as an SSRF primitive | §7.2 `UV-01`…`UV-08` |
| AC-06 | The inbound contract requires **read-back**, with a per-rail reason | §8.2, §8.3 |
| AC-07 | Per-provider verification is tabulated, including where **none exists** | §8.4, `IN-A-22` |
| AC-08 | Consumer obligations are stated as a publishable list | §6 — twelve |
| AC-09 | Negative cases are enumerated for `IN-008` | §9 — sixteen |
| AC-10 | **What is deliverable today is stated honestly** | §11 — **three of eleven** |

**Definition of done.** Complete when every criterion is met, **Q-01 is ratified**, `FF-77`…`FF-84`
are enabled, the three management endpoints are built, and `PGD-000`'s `IN-006` row carries a fresh
enumeration timestamp. **`AP-04` closes on ratification of §4 plus delivery of §7.1 — not on issue
of this document.**

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | **`IN-001`** §5.4 | `PT-05` read-back; `AA-08` |
| Upstream | **`IN-003`** §5 | The `external` E2 channel and shapes this delivers |
| Upstream | `IN-005` §7 | The consumer register; notice contacts |
| Upstream | `AR-001` §8.1 | Z6 egress for outbound delivery |
| Downstream | **`IN-004`** | §8.4 is each ICD's verification clause |
| Downstream | **`IN-007`** | Per-rail read-back applied to the money path |
| Downstream | **`IN-008`** | §9's sixteen negative cases |
| Downstream | `AP-004` | The developer guide; **its `O-01` and `O-03` close here** |
| Downstream | `SC-002` | `/hooks/v1/*` is a distinct attack surface |
| Lateral | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` §3.3, §5.1 | The eleven W1 webhooks; **§3.3's `technician.location_updated` row superseded** |
| Lateral | `../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M28_*.md` §12.5 | **The eighteen endpoints, now nineteen through twenty-two** |

---

## 16. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`./IN-001_Integration_Architecture_Specification.md`](./IN-001_Integration_Architecture_Specification.md) ·
[`./IN-003_Domain_Event_Catalogue_and_Schema_Registry.md`](./IN-003_Domain_Event_Catalogue_and_Schema_Registry.md) ·
[`./IN-004_Interface_Control_Documents.md`](./IN-004_Interface_Control_Documents.md) ·
[`./IN-005_API_Governance_Versioning_and_Deprecation_Standard.md`](./IN-005_API_Governance_Versioning_and_Deprecation_Standard.md) ·
[`./IN-002_artefacts/platform/openapi.yaml`](./IN-002_artefacts/platform/openapi.yaml)

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` §3.3, §5.1, §7 ·
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M28_*.md` §5.4, §12.5 ·
`../../project_content/_AUDIT/AUDIT-016_*.md` `AP-04` ·
`../../project_content/15_Integration_and_Developer_Content/AP-004_*.md` §4.4–§4.12

**External sources**

| Source | What it establishes | Verified |
|---|---|---|
| Standard Webhooks specification | `webhook-id` / `webhook-timestamp` / `webhook-signature`; HMAC-SHA256 over `id.timestamp.body`; `v1,` prefix; base64; **300 s tolerance**; SDKs in ten languages | 2026-08-18 |
| FIPS 198-1 / RFC 6234 | HMAC and SHA-2 | 2026-08-18 |
| RFC 9110 | Status-code semantics | 2026-08-18 |
| SSLCOMMERZ developer documentation (v4) | IPN with **MD5** `verify_sign` **plus a mandatory Transaction Validation API call** | 2026-08-18 |
| bKash Tokenized Checkout API Integration Guide | `create → execute → **query**` | 2026-08-18 |
| Nagad merchant API integration guidance | RSA response-signature verification against Nagad's public key | 2026-08-18 |
| OWASP SSRF prevention guidance | `UV-01`…`UV-05` | 2026-08-18 |

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Integration Architecture | Initial issue. Puts a **complete outbound signature scheme** to ratification — algorithm, headers, signed content, 300 s replay window, multi-signature rotation and constant-time comparison — closing the six gaps `AP-04` enumerated. **Registers the three webhook-management endpoints `AP-04` found missing** and issues them as executable OpenAPI. Adds `SIG-10`…`SIG-13` for per-endpoint secrets, entropy, rotation cadence and scheme versioning. Specifies the inbound eight-step contract with **mandatory read-back**, tabulates per-provider verification including three providers where it is inconsistent or absent (`IN-A-22`), and states honestly that **three of the eleven W1 CON-03 webhooks are deliverable today** | *Pending — CTO and Security Lead ratification (`AP-04` Q-01)* |

---

*`IN-006` · Category 04 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
