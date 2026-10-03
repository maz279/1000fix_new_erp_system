---
id: AP-004
title: Webhook and Callback Integration Guide
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering Lead
author: Platform Engineering
reviewers: [CTO, Solution Architect, Security Lead, Content Design Lead, QA Lead, Finance Systems Lead]
approver: Content Design Lead with CTO
content_class: D
purpose: >
  The two-way webhook contract — how an external consumer subscribes to 1000FiX events, verifies
  that a delivery is genuine, survives duplicates and retries, and knows when its endpoint has been
  disabled; and how 1000FiX verifies, de-duplicates and routes the callbacks it receives from
  payment gateways, couriers and messaging platforms. `IP-04` requires every integration to be
  idempotent, which is an obligation on **both** ends. Without this file the consumer end is
  undocumented, and the predictable results are double-applied payments, replayed deliveries
  accepted as new, and silently disabled endpoints whose owners discover the outage days later.
traces_to: [M28, M28 FR-IPF-034, M28 FR-IPF-035, M28 FR-IPF-036, M28 FR-IPF-037, M28 FR-IPF-038, M28 AUT-IPF-14, M28 BRU-IPF-18, 05-03, 05-03 IP-04, 05-03 IP-05, 05-03 §3.3, 05-03 §5.1, 05-03 §7, 05-06 DI-05, 05-06 NFR-062, 05-06 NFR-063, AP-001, AP-002, AP-003, AP-005, AP-006, AP-009, AP-010, AP-011, AP-012, OP-008, TS-017]
priority: P2
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M28_Integration_API_and_Event_Platform.md §5.4 FR-IPF-034…FR-IPF-038, §11 AUT-IPF-14, §9 BRU-IPF-18, §10.1 fix_webhook_endpoint and fix_webhook_delivery entities
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md §1 IP-04 idempotency and IP-05 safe failure; §3.3 the eleven portal webhooks; §5.1 the `/hooks/v1/*` receiver family; §7 "webhook delivery failure > 5 consecutive to one endpoint — disable endpoint; notify owner"
    verified: 2026-08-18
    class: P1
  - source: Standard Webhooks specification — HMAC-SHA256 signing, `webhook-id` / `webhook-timestamp` / `webhook-signature` headers, timestamp tolerance for replay prevention, key-versioned signatures. https://github.com/standard-webhooks/standard-webhooks/blob/main/spec/standard-webhooks.md
    verified: 2026-08-18
    class: P2
  - source: Webhook replay-prevention practice — timestamp tolerance of no greater than five minutes, nonce or event-id cache within the replay window, and constant-time signature comparison. https://webhooks.fyi/security/replay-prevention · https://docs.stripe.com/webhooks
    verified: 2026-08-18
    class: P3
  - source: SSLCOMMERZ IPN listener contract — POST to a merchant-configured listener, MD5 `verify_sign` hash match, then mandatory server-side validation through the Transaction Validation API before the transaction is treated as successful. https://developer.sslcommerz.com/doc/v4/
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# Webhook and Callback Integration Guide

| Item | Value |
|---|---|
| Directions covered | 2 — outbound (1000FiX → consumer) and inbound (third party → 1000FiX) |
| Outbound events available | The `05-03` §3.3 portal set (11) plus subscription-scoped business events (`AP-003`) |
| Inbound receivers | `/hooks/v1/{integration}` — 14 integrations with a webhook pattern in `05-03` §2 |
| Signature scheme | **Proposed** — HMAC-SHA256, three headers, 5-minute tolerance (§4.4). **Not specified anywhere in the repository** — open item `O-01` |
| Retry schedule | 3 attempts, exponential backoff, then dead-letter (`AUT-IPF-03`) |
| Auto-disable | 5 consecutive failures (`BRU-IPF-18`, `05-03` §7) |
| Consumer obligations | 12 (§4.7) |
| Wave | W3 registered · **first consumed W1** — open item `O-02` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order; §4 subdivided by volume. The **endpoint reference table**
> required by `CG-009` §3 is §4.9 (inbound receivers) together with §4.2's subscription
> management endpoints. The **error catalogue table** required by `CG-009` §3 is §4.10 — the
> response codes a consumer returns to 1000FiX and what each one causes, which is the error
> surface unique to webhooks and is not in `AP-006`.

---

## 1. Purpose

A webhook is the only integration pattern on this programme where **the counterparty operates
half of the mechanism**. An API call fails on our side or theirs and the caller sees it. A webhook
that is mis-verified, double-processed or silently disabled fails on the *receiving* side, where
1000FiX has no visibility and the consumer has no alert.

`IP-04` states the requirement — *"every integration is idempotent; retries and replays never
double-apply"* — and `M28` §4 states the consequence for content: *"consumers must be told how to
hold up their end."* `FR-IPF-034`…`FR-IPF-038` build the mechanism. **Nothing in the repository
tells a consumer how to use it.**

**What stops working without this file.**

| Absent | Consequence |
|---|---|
| Signature scheme documentation | Consumers accept unverified POSTs. A forged `payment.received` to a partner's endpoint is a financial fraud vector, and the endpoint URL is discoverable by anyone who has seen one delivery |
| Replay-window rule | A captured delivery is replayable indefinitely. Timestamp tolerance is the control, and a control nobody documents is a control nobody implements |
| Idempotency guidance | At-least-once delivery (`DI-05`) plus a non-idempotent consumer equals double-applied business effects. This is not a rare edge case — retries are normal operation |
| Ordering statement | Consumers assume delivery order matches business order. It does not, and the failure is silent: a status regresses on a customer's screen |
| Auto-disable documentation | `BRU-IPF-18` disables an endpoint after five consecutive failures. A consumer who does not know this exists experiences it as "1000FiX stopped sending events" and raises it as an outage days later |
| Inbound verification per provider | Each of bKash, Nagad, SSLCOMMERZ, Pathao, RedX, WhatsApp and the rest verifies differently. Undocumented, each is implemented by whoever builds that connector, and one of them will be implemented without verification |

---

## 2. Scope

**In scope.** Outbound webhook subscription and endpoint registration; the signature and replay
scheme; delivery guarantees, retry and ordering; consumer-side idempotency; auto-disable and
re-enablement; the twelve consumer obligations; inbound receiver contract and per-provider
verification; the consumer response-code contract; failure modes; and sandbox simulation.

**Out of scope.**

| Out of scope | Owned by | Note |
|---|---|---|
| What each event means | `AP-003` | A webhook is a **delivery mechanism**; the payload's meaning is the event's |
| Credential and secret issue | `AP-005` | The signing secret is a credential and follows the credential lifecycle |
| Error codes returned by 1000FiX APIs | `AP-006` | §4.10 is the reciprocal — codes the **consumer** returns |
| Payment-specific callback semantics and reconciliation | `AP-009` | §4.9 gives the verification contract per gateway; `AP-009` gives what the callback *means* for money |
| Sandbox environment and test credentials | `AP-010` | §4.11 states what can be simulated; `AP-010` provides the access |
| Deprecating or changing a webhook payload | `AP-011` | A webhook payload is a public contract |
| Which fields a counterparty may receive | `AP-012` | Disclosure decision, not a delivery decision |
| Internal event bus mechanics, dead letters, replay tooling | `M28` `FR-IPF-021`…`FR-IPF-031`, `OP-008` | A webhook consumer never sees the bus |
| Operating the receiver in production — backlog, dead-letter triage | `OP-008` runbook | This file is for consumers; `OP-008` is for operators |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Portal platform team (CON-03)** | The eleven `05-03` §3.3 webhooks — the largest single consumer, from W1 |
| **Brand partner integration teams** | Claim decision and consignment callbacks (`AP-007`) |
| **Corporate client IT teams** | SLA, invoice and estate callbacks (`AP-008`) |
| **Payment gateway integration engineers (internal)** | §4.9 inbound verification per gateway |
| **Courier integration engineers (internal)** | Pathao, RedX, Steadfast/Sundarban tracking callbacks |
| **Marketplace sellers with systems** | Order-awarded and payout callbacks |
| **Security** | §4.4 and §4.9 — the two places webhook security is either present or absent |
| **QA** | `TS-017` security cases; §4.12 lists the negative cases this contract requires |

---

## 4. Content

### 4.1 Two directions, two different contracts

They are routinely conflated and they have almost nothing in common.

| | **Outbound** — 1000FiX → consumer | **Inbound** — third party → 1000FiX |
|---|---|---|
| Who initiates | 1000FiX, on an event | The third party, on their event |
| Who owns the endpoint | The consumer | 1000FiX — `/hooks/v1/{integration}` |
| Who defines the signature scheme | **1000FiX** (§4.4) | **The third party** — one scheme per provider (§4.9) |
| Guarantee | At-least-once, ordering **not** guaranteed | Whatever the provider gives, which is usually less than they claim |
| Failure handling | Retry 3×, then dead-letter and count toward auto-disable | Verify, acknowledge fast, process asynchronously |
| Primary risk | Consumer double-applies, or endpoint silently disabled | Forged or replayed callback accepted as genuine |
| Governing requirement | `FR-IPF-034`…`FR-IPF-036` | `FR-IPF-037`, `FR-IPF-038` |

**The single most important asymmetry:** on the outbound path 1000FiX controls the security
scheme and the consumer must implement it correctly. On the inbound path **the provider controls
the scheme and 1000FiX must implement each one correctly** — fourteen times, differently. §4.9
exists because that is fourteen chances to get it wrong once.

### 4.2 Outbound — subscription and endpoint registration

| Step | What the consumer does | Endpoint | Notes |
|---:|---|---|---|
| 1 | Register a consumer and obtain credentials | `POST /api/v1/platform/consumers` | `AP-005`; prerequisite for everything below |
| 2 | Register an endpoint URL per environment | `POST /api/v1/platform/webhooks/endpoints` *(path proposed — `O-03`)* | HTTPS only. One endpoint may receive many event types |
| 3 | Select event types | Same call, `event_types[]` | Scope-filtered: a consumer may only subscribe to events their credential's scope permits (`EA-11`) |
| 4 | Receive the signing secret **once** | Response body | Stored in the vault on the 1000FiX side (`fix_webhook_endpoint.secret_vault_ref`, `IP-07`). **It is not retrievable again** — rotation issues a new one |
| 5 | Verify with a test delivery | `POST /api/v1/platform/webhooks/endpoints/{id}/test` *(proposed — `O-03`)* | Sends a signed `platform.test` delivery. Not a real event; carries no business data |
| 6 | Go live | — | The endpoint becomes active on first successful test delivery |

**Endpoint registration fields**, from `fix_webhook_endpoint` (`M28` §10.1):

| Field | Consumer sets | Notes |
|---|:--:|---|
| `url` | ● | HTTPS, publicly resolvable, no basic-auth credentials in the URL |
| `event_types` | ● | Subject to scope filtering |
| `secret_vault_ref` | — | 1000FiX side; the consumer receives the secret value once |
| `retry_policy` | — | Fixed by 1000FiX (§4.5); not consumer-configurable |
| `consecutive_failures` | — | Read-only counter driving auto-disable |
| `active` | read | Set false by auto-disable |
| `owner_user_id` | ● | **The human notified on auto-disable.** A registration with no reachable owner is the failure mode in §4.6 |

> **`owner_user_id` is the field most likely to be filled with a shared mailbox and is the one
> that matters most.** `AUT-IPF-14` notifies this owner when the endpoint is disabled. A shared
> mailbox nobody reads converts a five-failure auto-disable into a multi-day silent outage.

### 4.3 Delivery payload shape

Every outbound delivery carries the standard event envelope (`05-03` §4.1, `AP-003` §4.2)
unchanged, plus transport headers. **The envelope is not re-shaped for webhook delivery** —
a consumer reading the catalogue reads the same structure it receives.

| Header | Value | Purpose |
|---|---|---|
| `webhook-id` | The `event_id` | Idempotency key for the consumer. **Same value across all retries of the same event** |
| `webhook-timestamp` | Unix seconds at signing | Replay window (§4.4) |
| `webhook-signature` | `v1,<base64 HMAC-SHA256>` — space-separated list when more than one key is valid | Authenticity |
| `content-type` | `application/json; charset=utf-8` | Bengali content is UTF-8 |
| `x-correlation-id` | The envelope `correlation_id` | Support and tracing (`NFR-092`) |
| `user-agent` | `1000FiX-Webhooks/1.0` | Identification in the consumer's logs |

**`webhook-id` is the `event_id`, not a delivery id.** This is deliberate and is the whole
idempotency story: three retries of one event carry one `webhook-id`, so a consumer recording it
de-duplicates retries for free. A per-delivery identifier would defeat the mechanism, and is the
most common way this is implemented wrongly.

### 4.4 Signature and replay — the proposed scheme

> **This scheme is a proposal.** `FR-IPF-035` requires every outbound webhook to be signed;
> **no repository document specifies how.** `05-03` §5.1 says only "signature verification" for
> the inbound family. What follows is the recommendation, aligned to the Standard Webhooks
> specification because that is what a partner's existing library will already implement — and it
> is recorded as `O-01`, not presented as decided.

**Signed content.**

```
signed_payload = webhook-id + "." + webhook-timestamp + "." + raw_request_body
signature       = base64( HMAC-SHA256( signing_secret, signed_payload ) )
header          = "v1," + signature
```

| # | Rule | Reason |
|---|---|---|
| **SIG-01** | **HMAC-SHA256.** Not SHA-1, not MD5 | The interoperable default. Every partner library supports it |
| **SIG-02** | The signature covers **`webhook-id`, `webhook-timestamp` and the raw body**, joined by `.` | Signing the body alone permits replay; including the timestamp is what makes the replay window enforceable |
| **SIG-03** | The consumer verifies against the **raw body bytes**, before any JSON parsing or re-serialisation | Re-serialising changes whitespace and key order and breaks the signature. The single most common consumer implementation error |
| **SIG-04** | Comparison is **constant-time** | A byte-by-byte comparison leaks the signature through timing |
| **SIG-05** | **Reject if `webhook-timestamp` is more than 5 minutes from the consumer's clock**, in either direction | Replay prevention. Five minutes is the interoperable convention and tolerates ordinary clock skew |
| **SIG-06** | The consumer **also** records `webhook-id` and rejects a repeat within at least the replay window — ideally permanently | Timestamp tolerance alone permits replay inside the window. Both controls are required; neither is sufficient |
| **SIG-07** | `webhook-signature` may carry **more than one signature**, space-separated, during a secret rotation. The consumer accepts the delivery if **any** verifies | Zero-downtime rotation. Without it, every rotation is an outage on the consumer's side |
| **SIG-08** | The signing secret is issued once, stored in the vault (`IP-07`, `NFR-062`), rotatable by the consumer, and **never** logged | A secret in a delivery log is a secret in a log-aggregation system |
| **SIG-09** | An unsigned or wrongly-signed delivery is **rejected by the consumer with `401`** and not processed | And is a security event on the 1000FiX side if 1000FiX did not send it |

**What the scheme does not do, stated so it is not assumed.** It does not provide confidentiality
— TLS does that. It does not authenticate the *consumer* to 1000FiX. It does not prevent a
consumer's own compromised secret being used against them; that is what rotation is for.

### 4.5 Delivery guarantees, retry and ordering

| Property | Guarantee | Consumer consequence |
|---|---|---|
| **Delivery** | At-least-once (`DI-05`) | Duplicates are normal. `SIG-06` is mandatory, not advisory |
| **Ordering** | **None.** Webhook delivery carries **no** ordering guarantee, not even per aggregate | The bus guarantees per-aggregate order (`T-03`); HTTP delivery, retry and consumer latency destroy it. **Consumers must order on `occurred_at`, and must tolerate an older state arriving after a newer one** |
| **Latency** | No committed target for webhook delivery. `NFR-043` sets event delivery to a **consumer** at p95 ≤ 5 s; that is the bus, not the far end of an internet round trip | Do not build a timing dependency |
| **Retry** | 3 attempts with exponential backoff, then dead-letter (`AUT-IPF-03`) | After the third failure the event will **not** be delivered again without manual replay |
| **Backoff** | Attempt 1 immediate · attempt 2 at ~30 s · attempt 3 at ~5 min *(schedule proposed — `O-04`)* | Total window ≈ 5 minutes. A consumer down for an hour loses every event in that hour to the dead-letter queue |
| **Timeout** | 10 seconds per delivery attempt *(proposed — `O-04`)* | A consumer that processes synchronously and takes 11 seconds fails every delivery |
| **Success** | Any `2xx` | Anything else counts as a failure |

> **The ordering statement is the one consumers most often disbelieve.** It is worth being blunt:
> if a service order moves `created → classified → approved` within two seconds, a consumer can
> receive `approved` before `classified`, because `classified` was retried once. **A consumer that
> writes "if new_state == X then …" without checking `occurred_at` will regress a customer's
> visible status.** `05-03` §3.3's `service_order.status_changed` webhook makes this concrete for
> the portal.

### 4.6 Auto-disable and re-enablement

`BRU-IPF-18` and `05-03` §7: five consecutive delivery failures disable the endpoint and notify
its owner.

```
  ACTIVE ──► delivery fails ──► consecutive_failures += 1
     ▲                              │
     │  any success resets to 0     │  reaches 5
     │                              ▼
     └──── manual re-enable ◄── DISABLED ──► AUT-IPF-14 notifies owner_user_id
                (§4.6 checklist)              platform.webhook_endpoint_disabled emitted
```

| # | Rule |
|---|---|
| **AD-01** | The counter is **consecutive**, not cumulative. One success resets it |
| **AD-02** | Disablement is **per endpoint**, not per consumer. A consumer with three endpoints loses one |
| **AD-03** | Events occurring while disabled are **not queued for that endpoint**. They are dead-lettered. **This is the fact consumers most need to know and the one they discover last** |
| **AD-04** | Re-enablement is **manual and deliberate** — there is no automatic retry-until-healthy, because an endpoint that failed five times in a row is usually broken rather than busy |
| **AD-05** | Re-enablement does **not** replay missed events automatically. Replay is a separate, recorded, authorised action (`FR-IPF-030`, `M28` §13 step-up) |
| **AD-06** | The consumer's `owner_user_id` is notified by `M27`. **If that address is unmonitored, `AD-03` becomes a silent multi-day data gap** |

**Re-enablement checklist for a consumer.**

1. Fix the cause — expired TLS certificate, changed URL, deployment window, signature failure.
2. Confirm with a test delivery (§4.2 step 5).
3. Request re-enablement through the developer portal or the integration owner.
4. **Ask explicitly whether missed events should be replayed**, and state the window. Replay is
   authorised and recorded on the 1000FiX side; it is not automatic and it is not free.
5. Reconcile. For financial or custody events, a replay is not sufficient assurance on its own —
   run the reconciliation the integration provides (`AP-009` for payments, `AP-007` §consignment
   for brands).

### 4.7 The twelve consumer obligations

`IP-04` puts idempotency on both ends. This is the consumer's end, stated as a checklist because
that is how it will be used.

| # | Obligation | Consequence of not doing it |
|---:|---|---|
| **CO-01** | Verify the signature on **every** delivery, against the raw body, in constant time | Accepts forged deliveries |
| **CO-02** | Reject deliveries outside the 5-minute timestamp window | Accepts replayed deliveries |
| **CO-03** | Record `webhook-id` and ignore repeats | Double-applies business effects on every retry |
| **CO-04** | Return `2xx` **within 10 seconds**, before doing the work | Every delivery times out and the endpoint auto-disables in five events |
| **CO-05** | Acknowledge first, process asynchronously from your own queue | Couples your processing latency to our retry policy |
| **CO-06** | Order on `occurred_at`, never on arrival | Status regression visible to end users |
| **CO-07** | Tolerate **unknown fields** in the payload | An additive change within a `schema_version` — which is permitted at any time (`BRU-IPF-06`) — breaks you |
| **CO-08** | Treat the payload as **notification, not truth for anything financial**. Fetch the authoritative record by API where money or custody is involved | A forged or stale payload becomes a financial posting |
| **CO-09** | Monitor your own endpoint's success rate and alert on it | You learn about failures from `AD-06`, if anyone reads that mailbox |
| **CO-10** | Keep `owner_user_id` pointing at a monitored, human-reachable address | `AD-03` becomes a silent gap |
| **CO-11** | Support signature rotation — accept multiple signatures during the overlap (`SIG-07`) | Every rotation is an outage |
| **CO-12** | Never log the raw body of a delivery containing personal data, and never log the signing secret | `OPS-04`; and under PDPA 2026 an unnecessary copy of personal data is processing |

**CO-08 is the obligation that prevents the worst outcome.** A webhook says *something happened*.
For anything with financial or custody consequence — `invoice.paid`, `payout.executed`,
`consignment.custody_transferred`, `wipe.certified` — the consumer fetches the record through the
API before acting. This is also what makes a forged delivery harmless: it triggers a lookup that
returns the truth.

### 4.8 Which events are available as webhooks

Not every event is deliverable to every consumer. Three filters apply, in order.

| # | Filter | Effect |
|---:|---|---|
| 1 | **Platform events are never external** | The 15 `platform.*` events (`AP-003` §4.6) are `T-Int` and are not subscribable by any external consumer |
| 2 | **Scope** | A consumer receives only events their credential's scope permits (`EA-11`, `API-10`). A brand consumer subscribing to `service_order.created` receives nothing — not an error, and this must be documented or it reads as a bug |
| 3 | **Disclosure** | Even in scope, a payload is filtered to the fields `AP-012` permits that counterparty. **The webhook payload for an external consumer is not the internal payload** |

| Consumer class | Typical subscribable set | Authority |
|---|---|---|
| Portal platform (CON-03) | The eleven `05-03` §3.3 webhooks | `05-03` §3.3 |
| Brand partner | `warranty_claim.*` (own brand), consignment events, `capa.closed`, `certification.expiring` | `P08` §12.3, `EA-05` |
| Corporate client | `service_order.*`, `sla.*`, `invoice.*` (own organisation) | `P04` §12.3, `EA-03` |
| Payment gateway | **None** — gateways receive no 1000FiX webhooks; the direction is inbound only | `05-03` §2.1 |
| Courier partner | `consignment.*` for own consignments | `EA-07` |
| Marketplace seller | Own offers, own awards, own payouts | `EA-04` |

> **Filter 2's silent-empty behaviour needs explicit documentation.** A consumer who subscribes
> out of scope should receive an error at subscription time, not silence at delivery time. Whether
> `FR-IPF-026` validates the subscription against the credential's scope is not stated in `M28`.
> Recorded as `O-05`.

### 4.9 Inbound — the receiver contract and per-provider verification

`FR-IPF-037` receives third-party webhooks at `/hooks/v1/*` with signature verification, replay
protection and idempotent ingestion. `FR-IPF-038` routes a verified webhook to the owning module
**without interpreting its business content**.

**The receiver contract, identical for every provider:**

| # | Step | Rule |
|---:|---|---|
| RX-01 | Terminate TLS, accept `POST /hooks/v1/{integration}` | One path per integration; never a shared path with a body-discriminated router |
| RX-02 | **Verify** using that provider's scheme (table below) | Verification failure returns the provider's expected rejection code and raises a security event |
| RX-03 | **Replay-check** on the provider's own idempotency identifier | Where the provider supplies none, the receiver derives one — and that derivation is per-provider and is the weakest link |
| RX-04 | **Persist raw**, then acknowledge | The raw body is evidence. Acknowledging after persistence, before processing, is the only shape that survives a processing outage |
| RX-05 | **Route** to the owning module as a command or event | M28 does not interpret (`M28` §3.2) |
| RX-06 | **Independently confirm** anything financial by calling the provider's own query API | The provider's callback is a notification. `AP-009` makes this mandatory for payments |

**Per-provider verification — the fourteen inbound integrations.**

| INT | Provider | Verification mechanism | Replay identifier | Independent confirmation | Wave |
|---|---|---|---|---|:--:|
| INT-001 | **bKash** | Provider-issued credentials; callback validated by calling **Query/Search Transaction** with the payment id | `paymentID` / `trxID` | **Mandatory** — Execute/Query before treating as paid | W3 |
| INT-002 | **Nagad** | Signature/encryption using the merchant key pair issued at onboarding | Order id + payment reference | **Mandatory** — verify by payment status call | W3 |
| INT-003 | **SSLCOMMERZ** | `verify_sign` hash match on the IPN body, **then** the Order/Transaction Validation API | `tran_id` + `val_id` | **Mandatory** — the provider's own documentation requires validation before treating a transaction as successful | W3 |
| INT-004 | Rocket (via aggregator) | Aggregator's scheme — **aggregator not named in `05-03`** | Unknown | Assume mandatory | W3 |
| INT-008 | International gateway (Stripe/PayPal) | Provider HMAC signature header with timestamp tolerance | Provider event id | Mandatory | W9 |
| INT-009 | Instalment / BNPL partner | Partner-defined; unknown | Unknown | Mandatory | W8 |
| INT-012 | **WhatsApp Business Cloud** | Payload signature header verified against the app secret | Message id | Not applicable (no money) | W1 |
| INT-013 | Email (inbound parsing) | **No signature.** Sender verification only — SPF/DKIM/DMARC | Message-Id | Not applicable | W1 |
| INT-015 | Cloud telephony / IVR | Provider-defined | Call id | Not applicable | W4 |
| INT-017 | Social messaging (Messenger, IMO) | Platform signature header | Message id | Not applicable | W6 |
| INT-023 | Traccar GPS | REST + WebSocket over authenticated session | Position id + device time | Not applicable | W2 |
| INT-024 | **Pathao** | Partner scheme — not documented in `05-03` | Consignment id | Confirm status by API | W3 |
| INT-025 | **RedX** | Partner scheme — not documented in `05-03` | Consignment id | Confirm status by API | W3 |
| INT-026 | Steadfast / Sundarban | Partner scheme — not documented in `05-03` | Consignment id | Confirm status by API | W3 |
| INT-047 | Client ITSM (ServiceNow / Jira) | Per-client; typically HMAC or mutual TLS | Client ticket id + update sequence | Not applicable | W7 |

> **Five of the fifteen rows say "unknown" or "not documented".** That is not a defect in this
> file; it is the current state of the repository, and it is stated rather than filled with a
> plausible guess (`CG-012`, `CM-R8`). Four of the five — INT-004, INT-024, INT-025, INT-026 —
> land in **W3**, and the courier three carry customer addresses. Recorded as `O-06`.

**Two rows deserve separate attention.**

`INT-013` inbound email parsing has **no cryptographic verification available at all**. Email is
trivially spoofable and it creates tickets. The controls are SPF/DKIM/DMARC evaluation, allow-list
of sender domains where the flow permits, and **never** letting an inbound email alone cause a
financial or custody state change. Malware scanning on every attachment is required before storage
or serving (`NFR-063`).

`INT-023` Traccar is a **stream**, not a webhook, and is included because it arrives on the same
inbound path in `05-03` §2.3's "REST + WebSocket". Its volume — 400 technicians at 30-second
intervals (`NFR-056`) — is the throughput concern recorded in `AP-003` `O-07`.

### 4.10 The consumer response-code contract

The error catalogue table required by `CG-009` §3. These are the codes a **consumer** returns to
1000FiX, and what each causes on our side. Consumers get this wrong more often than they get the
signature wrong, because nothing tells them it matters.

| Consumer returns | 1000FiX treats it as | Counts toward auto-disable | Retried | Consumer should use it when |
|---|---|:--:|:--:|---|
| `200` / `201` / `202` / `204` | Success | No — resets counter | No | Delivery accepted and durably recorded |
| `400` Bad Request | **Failure** | Yes | Yes | Never, deliberately. A `400` means the consumer thinks our payload is malformed — investigate rather than return it |
| `401` Unauthorized | **Failure** | Yes | Yes | Signature verification failed (`SIG-09`). Also the correct response to a forged delivery |
| `403` Forbidden | **Failure** | Yes | Yes | The consumer no longer accepts this event type. **Unsubscribe instead** — `403` burns the auto-disable counter |
| `404` Not Found | **Failure** | Yes | Yes | The endpoint URL has moved. Update the registration; do not leave a `404` in place |
| `409` Conflict | **Success** *(recommended)* | No | No | Duplicate `webhook-id` already processed. **Returning `2xx` for a duplicate is preferred** and `409` is documented only because consumers reach for it |
| `410` Gone | **Failure** | Yes | Yes | The endpoint is permanently retired. Unsubscribe and deregister |
| `422` Unprocessable | **Failure** | Yes | Yes | The consumer cannot process this payload. Almost always a `CO-07` violation |
| `429` Too Many Requests | **Failure** | Yes | Yes, honouring `Retry-After` | The consumer is overloaded. Valid, but `CO-05` avoids it |
| `5xx` | **Failure** | Yes | Yes | Consumer-side error. Expected occasionally; five consecutive disables the endpoint |
| Timeout (> 10 s) | **Failure** | Yes | Yes | Never deliberately — `CO-04` |
| Connection refused / TLS failure | **Failure** | Yes | Yes | Certificate expiry is the most common real-world cause of auto-disable |

> **`409` deserves the note it has.** A consumer that de-duplicates correctly (`CO-03`) and then
> returns `409` is being *more* correct than the mechanism expects and is punished for it: the
> delivery counts as a failure and burns the auto-disable counter. **Return `2xx` for a
> duplicate.** The duplicate was our retry, not the consumer's mistake.

### 4.11 Testing

| Capability | Available in sandbox | Notes |
|---|:--:|---|
| Signed test delivery | ● | §4.2 step 5; `platform.test`, no business data |
| Trigger a real event type on demand | ● | `AP-010` §simulated events |
| Force a signature mismatch | ● | Proves the consumer rejects — the negative case most often untested |
| Force a stale timestamp | ● | Proves `CO-02` |
| Force a duplicate delivery | ● | Proves `CO-03` |
| Force out-of-order delivery | ● | Proves `CO-06` |
| Force five consecutive failures to observe auto-disable | ● | The only way a consumer learns what `AD-03` feels like before it happens in production |
| Rotate the signing secret with overlap | ● | Proves `CO-11` |
| Inbound provider callbacks | **Provider sandboxes only** | SSLCOMMERZ and bKash provide sandboxes; four providers' sandbox availability is unknown — `AP-010` `O-04` |

### 4.12 Negative cases this contract requires of `TS-017`

`TS-017` covers access control, data scope, consent, residency and audit-log completeness. Webhook
security is a distinct surface and needs its own cases. Listed here so the requirement is owned:

| # | Case | Proves |
|---|---|---|
| WH-N1 | A delivery with a valid body and an invalid signature is rejected | `SIG-01`…`SIG-04` |
| WH-N2 | A captured valid delivery replayed after 6 minutes is rejected | `SIG-05` |
| WH-N3 | A captured valid delivery replayed within the window is de-duplicated | `SIG-06` |
| WH-N4 | An outbound payload to an external consumer contains no field outside `AP-012` for that counterparty | `AP-012`, `EA-02` |
| WH-N5 | A consumer subscribing to an out-of-scope event type is refused **at subscription** | `EA-11`, `O-05` |
| WH-N6 | Five consecutive failures disable the endpoint and notify the owner within the stated time | `BRU-IPF-18`, `AUT-IPF-14` |
| WH-N7 | An inbound callback with an invalid provider signature is rejected and raises a security event | `FR-IPF-037` |
| WH-N8 | An inbound payment callback alone does not settle an invoice without independent confirmation | `RX-06`, `AP-009` |
| WH-N9 | No webhook delivery log or dead-letter view exposes an unmasked S3 or residency-classified field | `M28` §13, `NFR-061`, `NFR-086` |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `M28` `FR-IPF-034`…`FR-IPF-038` | The mechanism. This file documents it; it does not build it |
| `M28` `FR-IPF-026` | Subscription management, including the scope validation `O-05` questions |
| `AP-003` | The payload envelope and the meaning of every deliverable event |
| `AP-005` | Consumer registration and credential lifecycle — prerequisite to §4.2 step 1; the signing secret follows the same lifecycle |
| `AP-006` | Errors 1000FiX returns; §4.10 is the reciprocal contract |
| `AP-009` | Payment callback semantics; §4.9 gives verification, `AP-009` gives meaning |
| `AP-010` | The sandbox that makes §4.11 possible |
| `AP-012` | Payload filtering per counterparty — filter 3 in §4.8 |
| `OP-008` | Operating the receiver: backlog, dead letters, replay. The operator's half of this contract |
| `TS-017` | The nine negative cases in §4.12 have no owning pack today |
| `05-03` §3.3 | The eleven portal webhooks — the first and largest consumer |
| `NT-021` | Alerting content for `platform.webhook_endpoint_disabled` |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per wave, as each wave's inbound integrations land |
| Trigger for out-of-cycle review | Resolution of `O-01` (signature scheme) · a new inbound provider · a provider changing its verification scheme · a change to the retry policy or auto-disable threshold · the first consumer-reported double-application incident |
| Owner | Platform Engineering Lead |
| Change control | Changes to §4.4 (signature), §4.5 (retry, ordering) or §4.6 (auto-disable) are **breaking changes to a public contract** and require CTO approval, a `RF-006` entry and notice under `AP-011` |
| Version pinning | Pinned to **API version** (`CG-006` §5). The webhook contract versions with the API, not independently |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **No webhook signature scheme is specified anywhere in the repository.** `FR-IPF-035` requires signing; `05-03` §5.1 says "signature verification"; neither states an algorithm, a header set, a signed-content construction or a replay window. §4.4 is a proposal aligned to Standard Webhooks. **Until it is decided, no consumer can implement verification and every delivery is effectively unauthenticated** | CTO with Security Lead | **W1 — the portal contract (CON-03) consumes webhooks from W1** |
| **O-02** | **Registered W3; first consumed W1.** `05-03` §3.3 gives the portal platform eleven webhooks, and the portal is live from W1. `AP-005`, also W3, is a prerequisite. Seventh consecutive category with this defect | Programme Content Lead with Platform Engineering Lead | **W1** |
| **O-03** | **Webhook management endpoints are unregistered.** `M28` §12.5 lists platform endpoints for schemas, subscriptions, dead letters, consumers, integrations, sync, reconciliation and trace — **and none for webhook endpoint registration, testing or rotation**, despite `FR-IPF-034` requiring a registry. The three paths at §4.2 are proposals | Platform Engineering Lead | **W1 design** |
| **O-04** | **The retry schedule and delivery timeout are unstated.** `AUT-IPF-03` gives "three retries with exponential backoff"; the intervals and the per-attempt timeout are not specified. §4.5's figures are proposals. A consumer cannot size its acknowledge-fast path without the timeout | Platform Engineering Lead | **W1 design** |
| **O-05** | **Subscription-time scope validation is unspecified.** `FR-IPF-026` registers subscriptions with optional content filters; nothing says an out-of-scope subscription is refused. If it is accepted and silently delivers nothing, every partner will raise it as a defect | Platform Engineering Lead with Security Lead | W3 |
| **O-06** | **Five of fifteen inbound providers have no documented verification scheme** — INT-004 (aggregator unnamed), INT-024 Pathao, INT-025 RedX, INT-026 Steadfast/Sundarban, INT-009 BNPL. **Four land in W3 and the courier three carry customer names, phone numbers and addresses.** A courier callback accepted without verification is a route to injected consignment status | Platform Engineering Lead with the owning module (`M03`, `M20`) | **W3 minus 2 months** |
| **O-07** | **Inbound email (`INT-013`) has no cryptographic verification and creates tickets.** SPF/DKIM/DMARC plus sender allow-listing is the whole control set, and `INT-013` is W1. The rule that an inbound email alone never causes a financial or custody state change needs to be a stated business rule, not a paragraph in a guide | Security Lead with `M27` owner | **W1** |
| **O-08** | **No consumer-facing status or delivery-history surface exists.** `fix_webhook_delivery` records every attempt and response (`M28` §10.1) but no endpoint in `M28` §12.5 exposes it to the consumer. `CO-09` asks consumers to monitor their own endpoint with no data from our side to reconcile against | Platform Engineering Lead | W4 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the §4 subdivision is the only addition and is justified
- [x] **Outbound and inbound treated as two different contracts, with the control asymmetry stated**
- [x] Signature scheme specified in full — construction, headers, nine rules — and **marked as a proposal because none exists**
- [x] Replay prevented by two independent controls, with the reason neither alone suffices
- [x] Delivery guarantees stated including the **absence** of ordering, with the concrete failure named
- [x] Auto-disable lifecycle drawn, with the not-queued-while-disabled fact made prominent
- [x] Twelve consumer obligations stated as a checklist with the consequence of each
- [x] Three subscription filters stated, including payload filtering per `AP-012`
- [x] All fifteen inbound integrations tabled with verification, replay identifier and confirmation requirement
- [x] **Undocumented provider schemes recorded as unknown rather than guessed (`CG-012`, `CM-R8`)**
- [x] Consumer response-code contract tabled, including the `409` trap
- [x] Nine negative test cases specified for `TS-017`
- [x] All internal links resolve
- [x] Eight open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` no signature scheme exists — outstanding; blocks every consumer implementation**
- [ ] **`O-02` registered after first consumption — outstanding**
- [ ] **`O-03` webhook management endpoints unregistered — outstanding**
- [ ] **`O-06` five inbound providers unverified, four at W3 — outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and CTO**
- [ ] Bengali counterpart — n/a; developer audience, English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
