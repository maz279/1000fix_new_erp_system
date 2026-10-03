---
id: AP-010
title: Sandbox Onboarding and Test Credential Guide
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering Lead
author: Platform Engineering with QA
reviewers: [CTO, Solution Architect, Security Lead, QA Lead, Data Migration Lead, Legal Counsel, Content Design Lead, Account Management Lead]
approver: Content Design Lead with CTO
content_class: D
purpose: >
  How an external integrator gets a working sandbox — access, credentials, what data exists, what
  is simulated, what is deliberately not, how to force an error or an event, and the checklist that
  must pass before a production credential is issued. Partners testing against production is how
  production incidents originate; a partner with no sandbox will test against production, because
  the alternative is not testing. Without this file the sandbox is either absent, unusable, or —
  worst — populated with real customer data, which under the Personal Data Protection Act 2026 is
  processing without a basis and a breach exposure of up to BDT 25 lakh.
traces_to: [M28, M28 FR-IPF-019, M28 FR-IPF-020, M28 FR-IPF-016, M28 BRU-IPF-21, 05-06 NFR-071, 05-06 NFR-086c, 05-06 NFR-090, 05-06 NFR-091, 05-03 §2.1, TS-001, TS-001 §4.7, TS-002, AP-001, AP-002, AP-004, AP-005, AP-006, AP-007, AP-008, AP-009, AP-011, AP-012, EO-001, EO-003, EO-005, EO-007, LG-020, DM-011]
priority: P2
wave: W4
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M28_Integration_API_and_Event_Platform.md §5.2 FR-IPF-019 "sandbox with representative masked data for external consumers and partner onboarding" (P2) and FR-IPF-020 partner onboarding (P2); §9 BRU-IPF-21 non-production environments never hold live external credentials
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md NFR-071 non-production environments use masked data only; NFR-086c no unmasked residency-classified data in any region in non-production; §6.3 NFR-090 and NFR-091 consent and lawful ground for processing
    verified: 2026-08-18
    class: P1
  - source: project_content/13_Test_and_Acceptance_Content/TS-001_Test_Strategy_and_Content_Traceability_Standard.md §4.7 — six environments specified (DEV, CI, SIT, UAT, PERF, TRAIN); none is a partner-facing sandbox. Open item O-03 records that none is provisioned
    verified: 2026-08-18
    class: P1
  - source: SSLCOMMERZ sandbox — separate host, separate credentials, transactions counted as test with no accounting effect. https://developer.sslcommerz.com/docs.html
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# Sandbox Onboarding and Test Credential Guide

| Item | Value |
|---|---|
| Environment | `SANDBOX` — **a seventh environment; `TS-001` §4.7 specifies six and none of them is this one** (§4.2) |
| Audience | Every external integrator across seven audience classes (`AP-001` §3) |
| Capabilities simulated | 11 (§4.5) |
| Capabilities deliberately not simulated | 7 (§4.7) |
| Forced-error triggers | 12 (§4.6) |
| Promotion checklist items | 16 (§4.9) |
| Data source | `TS-002` persona set — **the only permitted source** (`TX-05`) |
| Wave | W4 registered · **first consumed W3** — open item `O-02` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order; §4 subdivided by volume. The **endpoint reference table**
> required by `CG-009` §3 is §4.10. The **error catalogue table** required by `CG-009` §3 is
> §4.11 — the sandbox-specific conditions, referencing `AP-006` codes (`CP-01`).

---

## 1. Purpose

The register justification is one sentence and it is the whole case: *"Partners testing against
production is how production incidents originate."*

The corollary is the part that gets missed. **A partner with no usable sandbox does not stop
testing; they test against production**, because their alternative is shipping untested code into
a live integration. Every `AP-007` brand, `AP-008` corporate client and `AP-009` payment rail
needs somewhere to make mistakes.

`FR-IPF-019` provides *"a sandbox with representative masked data for external consumers and
partner onboarding"* at priority **P2**. `FR-IPF-020` provides partner onboarding at **P2**.
Both are the lowest-priority items in `M28`'s §5.2 lifecycle block, and both are prerequisites for
the `W3` courier integrations and the `W4` brand and corporate portals. That mismatch is `O-01`.

**What stops working without this file.**

| Absent | Consequence |
|---|---|
| A sandbox at all | Partners integrate against production. `AP-001`'s golden path stops at step 2, and the 30-minute time-to-first-call target is unachievable |
| A data policy | The fastest way to populate a sandbox is a copy of production. That breaches `NFR-071` and `NFR-086c`, and under PDPA 2026 a non-production copy of personal data is **processing** — with a stated exposure of up to BDT 25 lakh |
| A simulation inventory | Partners assume everything works and build against behaviours that never fire in sandbox. The first real event is in production |
| Forced-error triggers | Nobody tests the error path. `AP-004` `CO-01`, `CO-02` and `CO-03` — signature, replay and duplicate handling — are exactly the obligations that are never exercised unless they can be forced |
| A promotion checklist | Production credentials are issued when someone asks. `AP-012` disclosure rows and `AP-005` scope decisions are then made after the fact |
| A stated limitation set | Partners raise sandbox behaviour as defects. Support absorbs it |

---

## 2. Scope

**In scope.** What the sandbox is and is not; its relationship to the six `TS-001` environments;
access and credential issue; the data policy and its legal basis; the simulation inventory; forced
errors and events; third-party sandbox availability; deliberate limitations; the promotion
checklist; endpoint reference; sandbox-specific errors; and reset, retention and housekeeping.

**Out of scope.**

| Out of scope | Owned by | Note |
|---|---|---|
| Internal test environments — `DEV`, `CI`, `SIT`, `UAT`, `PERF`, `TRAIN` | `TS-001` §4.7, `06-04` (does not exist) | §4.2 states the relationship and refuses to absorb them |
| The test data set itself | **`TS-002`** | `TX-05` makes it the only permitted source. This file states how a partner reaches it, not what is in it |
| Data masking rules and technique | `DM-011`, `M29` | `NFR-071` requires masked data; the method is not content |
| Environment provisioning, topology, refresh mechanics | `06-04` (does not exist) with `M30` | `TS-001` `O-03` already records that none of the six is provisioned |
| Credential lifecycle in general | `AP-005` §4.4 | §4.3 covers only what is sandbox-specific |
| Third-party sandbox terms and merchant onboarding | Treasury, Commercial | §4.8 records availability, not procurement |
| The partner's own test strategy | The partner | We provide a sandbox, not a test plan |
| Acceptable use of the sandbox by 1000FiX staff | `LG-020` | Internal policy |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Every external integrator** | Golden-path steps 1, 3, 4 and 5 (`AP-001` §4.4) |
| **Brand partners** | `AP-007` onboarding steps 4–6 |
| **Corporate clients** | `AP-008` onboarding steps 4–6, especially the estate-load rehearsal with a deliberate reject |
| **Payment connector engineers (internal)** | §4.8 — five of nine rails have unknown sandbox availability |
| **1000FiX Platform Engineering** | Operating the sandbox and running the promotion gate |
| **Security and Legal** | §4.4 — the data policy is a compliance position before it is a technical one |
| **QA** | The boundary between this and the six `TS-001` environments |

---

## 4. Content

### 4.1 What the sandbox is, and is not

| The sandbox **is** | The sandbox **is not** |
|---|---|
| A running copy of the API surface with masked, synthetic data | A performance environment. Do not load-test it (`TS-001` §4.7 `PERF`) |
| Where a partner proves their integration works | Where 1000FiX proves the system works — that is `SIT` and `UAT` |
| Populated from `TS-002` personas | Populated from production, under any circumstance (§4.4) |
| Reset on a stated cadence (§4.12) | A durable store. Nothing a partner leaves there is guaranteed to survive a reset |
| Rate-limited at the `sandbox` class (`AP-005` §4.7) | Unlimited because "it's only test" |
| Able to force errors and emit events on demand (§4.6) | Connected to real payment rails, real SMS, or real customers (§4.7) |
| A prerequisite for production credentials (§4.9) | A substitute for the production promotion review |

### 4.2 The seventh environment

**This matters and it is easy to miss.** `TS-001` §4.7 specifies six environments — `DEV`, `CI`,
`SIT`, `UAT`, `PERF`, `TRAIN` — with their purposes, data states and refresh cadences, and records
at `O-03` that **none of the six is specified or provisioned**. Reading that list against this
file's requirement produces the finding:

| Environment | Purpose | Could it serve as the partner sandbox? |
|---|---|---|
| `DEV` | Engineering | No — unstable by design; external access to it is an unacceptable surface |
| `CI` | Unit, integration, contract, event | No — ephemeral, fixture-driven, per commit |
| `SIT` | `TS-003`–`TS-005` | No — data moves constantly; a partner cannot build against a moving target |
| `UAT` | `TS-006`–`TS-012`, `TS-016` | **No — and emphatically.** `TS-001` §4.7: UAT data is *frozen during a UAT cycle*, and `TX-08` is voided if it changes. A partner exercising flows in UAT changes the data business users are signing against |
| `PERF` | `TS-014` | No — production-shaped volumes, and load-testing conflicts |
| `TRAIN` | `TR` practical exercises | No — reset per cohort, and trainees destroy data by design |
| **`SANDBOX`** | **Partner integration** | **This is a seventh environment and it must be provisioned as one** |

**Its data-state requirements are unlike any of the six.** It must be **stable enough to build
against** (unlike SIT), **resettable per partner** (unlike UAT), **externally reachable** (unlike
all six), **externally credentialled** (unlike all six), and it must hold **no real personal data
whatsoever** — a stricter bar than `NFR-071`'s masking, because the population with access is
outside the company entirely.

Recorded as `O-03`, and it is a correction required against `TS-001` §4.7 rather than a note in
this file alone.

### 4.3 Access and credentials

| Step | What happens | Self-service | Reference |
|---:|---|:--:|---|
| 1 | Partner registers a consumer, selecting the sandbox environment | ● | `AP-005` §4.4, `FR-IPF-016` |
| 2 | `client_id` issued and secret shown **once** | ● | Vault-held (`IP-07`) |
| 3 | Scopes granted **from the audience class**, not from a contract | ● | See the rule below |
| 4 | Rate-limit class set to `sandbox` — 60/min, burst 10/s *(proposed, `AP-005` `O-03`)* | ● | |
| 5 | Test personas assigned from `TS-002` | ● | §4.4 |
| 6 | Webhook endpoint registered and verified with a signed test delivery | ● | `AP-004` §4.2 |
| 7 | Partner works the `AP-001` golden path | ● | Target ≤ 30 min |

**Five sandbox credential rules.**

| # | Rule | Basis |
|---|---|---|
| **SB-1** | **A sandbox credential never works against production, and a production credential never works against sandbox.** The failure is `401 auth.environment_mismatch`, never a partial success | `AP-005` `TK-05` |
| **SB-2** | **Non-production never holds live external credentials** | `BRU-IPF-21`, `NFR-071` |
| **SB-3** | Sandbox scopes are granted from the **audience class default**, deliberately wider than a signed contract would give, so a partner can explore before contracting. **They are re-derived from the contract at promotion** (§4.9) | `SC-03` applies to production; sandbox is an evaluation surface |
| **SB-4** | Sandbox credentials **expire** — 90 days, renewable self-service *(proposed, `O-06`)*. An abandoned integration should not leave a live credential |
| **SB-5** | Sandbox credentials are issued **before** a contract is signed, on registration alone. Requiring a contract to evaluate the API defeats `FR-IPF-020` | `AP-007` step 4, `AP-008` step 4 |

### 4.4 The data policy

**The single rule:**

> **No production data reaches the sandbox. Ever. In any form, masked or otherwise.**

| # | Rule | Basis |
|---|---|---|
| **SD-1** | Sandbox data is **`TS-002` persona data**, generated for the purpose | `TX-05` — *"No script uses production data"* |
| **SD-2** | `NFR-071` requires masked data in non-production. **This file is stricter: not masked production data, but synthetic data**, because the population with access is external | `NFR-071` is a floor, not a ceiling |
| **SD-3** | **No residency-classified field carries a realistic value** — no real-format NID, passport, TIN or biometric template | `NFR-086c` |
| **SD-4** | Under **PDPA 2026**, a non-production copy of personal data is **processing** and requires a lawful ground and a retention basis (`NFR-090`, `NFR-091`, `NFR-095`). Synthetic data is not personal data and avoids the question entirely | This is why `SD-2` is stricter than `NFR-071` |
| **SD-5** | Personas are **recognisably fictional** — names, numbers and addresses that a human would not mistake for real. A masked record that looks real gets treated as real |
| **SD-6** | Phone numbers use a **non-routable test range** and email uses a sink domain. A sandbox that can send a real SMS to a real number will |
| **SD-7** | Data a partner creates in sandbox is **theirs and is not shared** with another partner. Sandbox tenancy follows the same isolation as production (`EA-01`, `AC-01`) |
| **SD-8** | **`TS-002` does not exist yet.** It is registered `P0`/W1 and unwritten. Until it does, the sandbox has no permitted data source — `O-04` |

### 4.5 What is simulated

| # | Capability | Behaviour in sandbox | Notes |
|---:|---|---|---|
| S-01 | **Authentication and tokens** | Full — real token issue, expiry, revocation, scope enforcement | The one thing that must behave exactly as production |
| S-02 | **Read endpoints** | Full, against persona data | Non-empty results per audience (`AP-001` §4.4) |
| S-03 | **Write endpoints** | Full — objects are created and progress through real state machines | State transitions are real; only the data is synthetic |
| S-04 | **Idempotency** | Full — same key returns the original result | `AP-004`/`AP-002` behaviour must be provable here |
| S-05 | **Rate limiting** | Full at the `sandbox` class, with real headers | Deliberately low, so a partner meets `429` in sandbox rather than in production |
| S-06 | **Webhooks** | Full — real signing, real retries, real auto-disable | Including the failure paths at §4.6 |
| S-07 | **Domain events** | Emitted on demand and on real state changes | §4.6 |
| S-08 | **Error responses** | Full `AP-006` catalogue, forcible on demand | §4.6 |
| S-09 | **Estate bulk load** | Full, including set-commit and line-by-line rejects | `AP-008` `ES-1`, `ES-2` — the rehearsal `CP` step 5 requires |
| S-10 | **Coverage validation** | Full across all three outcomes | `AP-008` §4.4, `P04` `AC-04` |
| S-11 | **Claim decision flow** | Full, including part-approval and request-for-information states | `AP-007` `CL-3`, `CL-4` |

### 4.6 Forcing errors and events

The capability that makes a sandbox worth having. Without it a partner tests only the happy path,
which is the path that does not need testing.

**Mechanism (proposed — `O-05`):** a `X-Sandbox-Behaviour` request header, honoured **only** in
sandbox and rejected outright in production.

| # | Trigger | Produces | Proves |
|---:|---|---|---|
| T-01 | `X-Sandbox-Behaviour: error=<code>` | Any `AP-006` code on demand | The partner's error handler |
| T-02 | `X-Sandbox-Behaviour: latency=5000` | A 5-second response | Timeout handling |
| T-03 | `X-Sandbox-Behaviour: timeout` | No response, connection held to timeout | **The indeterminate path** (`AP-009` `ID-3`) |
| T-04 | `X-Sandbox-Behaviour: ratelimit` | Immediate `429` with `Retry-After` | `RL-02`, backoff discipline |
| T-05 | `POST /sandbox/events/{event_type}` | Emits that event to the partner's endpoint | Event handling |
| T-06 | `POST /sandbox/webhooks/replay` | Re-delivers a prior delivery verbatim | **`AP-004` `CO-03`** duplicate handling |
| T-07 | `POST /sandbox/webhooks/bad-signature` | A delivery with a deliberately invalid signature | **`AP-004` `CO-01`** — the negative case never otherwise tested |
| T-08 | `POST /sandbox/webhooks/stale-timestamp` | A delivery timestamped outside the tolerance | **`AP-004` `CO-02`** replay-window rejection |
| T-09 | `POST /sandbox/webhooks/out-of-order` | Two deliveries with reversed `occurred_at` | **`AP-004` `CO-06`** ordering discipline |
| T-10 | `POST /sandbox/webhooks/fail-endpoint` | Five consecutive forced failures | **Auto-disable observed** before it happens in production (`AP-004` `AD-03`) |
| T-11 | `POST /sandbox/credentials/rotate?overlap=true` | Rotation with both secrets valid | `AP-004` `CO-11`, `AP-005` `CR-02` |
| T-12 | `POST /sandbox/integrations/{id}/fail` | A downstream integration marked failed; fallback engaged | `dependency.fallback_engaged` handling (`AP-009` §4.8) |

> **T-07, T-08 and T-10 are the three that matter most and the three a partner will not think to
> ask for.** They should be **required** at promotion, not offered — which is why they appear in
> §4.9 as checklist items rather than as capabilities.

### 4.7 Deliberate limitations

Stated so partners do not raise them as defects.

| # | Not available in sandbox | Why | What to do instead |
|---:|---|---|---|
| L-01 | **Real money movement** | Payment rails are in their own sandboxes (§4.8) | Use the rail's sandbox; our sandbox simulates the confirmation |
| L-02 | **Real SMS, WhatsApp, email or push** | `SD-6`; and sending to a real number from a test environment is a live incident | Messages are recorded and readable, not delivered |
| L-03 | **Production-representative performance** | Not a performance environment | `NFR` targets are proven in `PERF` (`TS-014`), not here |
| L-04 | **Production-scale data volumes** | Persona-scale only | Volume behaviour is proven internally |
| L-05 | **Step-up authentication with real MFA devices** | Requires a real enrolled human | A stubbed step-up returns success; **the production path is rehearsed as a checklist item, not simulated** (`AP-007` `BP-4`, `AP-008` `CP-4`) |
| L-06 | **Federated sign-on against the client's real IdP** | The client's directory is not ours to test against | Federation is proven at promotion, per client (`AP-008` `CP-9`) |
| L-07 | **Guaranteed persistence across a reset** | §4.12 | Re-seed after a reset; do not build a test suite that assumes durable state |

### 4.8 Third-party sandbox availability

A partner integration is only as testable as its weakest dependency. Counted from `05-03` §2 and
this file's own research, 2026-08-18:

| Integration | Third-party sandbox | Status |
|---|---|---|
| **INT-003 SSLCOMMERZ** | Separate sandbox host and credentials; test transactions have no accounting effect | **Confirmed available** |
| **INT-001 bKash** | Provider sandbox with the tokenised-checkout API surface | **Available**, issued at merchant onboarding |
| **INT-002 Nagad** | Merchant sandbox with the key pair issued at onboarding | **Available**, issued at onboarding |
| INT-004 Rocket (aggregator) | — | **Unknown — aggregator unnamed** (`AP-009` `O-02`) |
| INT-005 BEFTN | Bank test facility | **Unknown** (`AP-009` `O-05`) |
| INT-006 Bank statement import | Bank test file | **Unknown** |
| INT-007 Seller payout rail | — | **Unknown — rail unnamed** |
| INT-008 / INT-009 | — | **Unknown — providers unnamed** |
| INT-024/025/026 Couriers | Partner sandboxes | **Unknown; all three land in W3** |
| INT-012 WhatsApp Business Cloud | Test numbers available in the platform | Available |
| INT-047 Client ITSM | Client's own non-production instance | Per client |

> **Nine of the integrations a partner may need to exercise have unknown sandbox availability, and
> four of those land in W3.** An integration whose third party has no sandbox can only be proven in
> production, which is exactly the outcome this file exists to prevent. Recorded as `O-07`.

### 4.9 Promotion to production

**The gate.** A production credential is not a support request; it is the outcome of this
checklist. Sixteen items: eleven universal, plus the audience-specific items in `AP-007` §4.11
(`BP-1`…`BP-7`) and `AP-008` §4.11 (`CP-1`…`CP-9`).

| # | Item | Evidence | Owner |
|---:|---|---|---|
| **P-01** | Contract or agreement signed, including the applicable portal terms | Signed agreement | Commercial + Legal |
| **P-02** | **`AP-012` disclosure rows exist for this counterparty**, with a lawful basis per field | `AP-012` register entry | Legal + Security |
| **P-03** | **Production scopes derived from the contract**, not carried over from sandbox (`SB-3`) | Scope grant record | Security Lead |
| **P-04** | Rate-limit class assigned and **communicated to the partner** | `fix_api_consumer` record | Platform |
| **P-05** | Golden path completed in sandbox | Portal telemetry (`AP-001` PM-02) | Platform |
| **P-06** | **Webhook signature verification demonstrated, including a forced failure (`T-07`)** | Sandbox log | Platform |
| **P-07** | **Replay rejection demonstrated (`T-08`)** | Sandbox log | Platform |
| **P-08** | **Duplicate handling demonstrated (`T-06`)** | Sandbox log | Platform |
| **P-09** | Rate-limit backoff demonstrated (`T-04`) — no immediate retry, `Retry-After` honoured | Sandbox log | Platform |
| **P-10** | **Auto-disable observed (`T-10`)**, and the partner's `owner_user_id` confirmed as a monitored human address | Sandbox log + confirmation | Platform |
| **P-11** | Error handling demonstrated across at least: `401`, `403`, `422`, `429`, `503` | Sandbox log | Platform |
| **P-12** | Idempotency demonstrated — the same key returns the original result | Sandbox log | Platform |
| **P-13** | Escalation contacts exchanged **both ways**, named humans | Onboarding record | Account Management |
| **P-14** | Reconciliation responsibility agreed where money or custody is involved | Onboarding record | Finance |
| **P-15** | Audience-specific items complete (`AP-007` `BP-1`…`BP-7` **or** `AP-008` `CP-1`…`CP-9`) | Per that guide | Per that guide |
| **P-16** | Production credentials issued, with a **first-cycle parallel check** agreed | Credential record | Platform + owning function |

> **P-06 through P-10 are the five that make this a gate rather than a formality.** Each is a
> security or reliability obligation the partner carries (`AP-004` §4.7), each is invisible until
> it fails in production, and each is trivially demonstrable in sandbox. A partner who cannot
> demonstrate them has not implemented them.

### 4.10 Endpoint reference

The endpoint reference table required by `CG-009` §3. **Every path below is a proposal** — no
sandbox endpoint appears in `M28` §12.5 (`O-05`).

| Endpoint | Method | Purpose | Available in |
|---|:--:|---|:--:|
| `/api/v1/platform/consumers` | POST | Register a consumer, selecting `sandbox` | Both |
| `/api/v1/platform/consumers/{id}/credentials/rotate` | POST | Rotate a secret | Both |
| `/api/v1/auth/token` | POST | Issue a sandbox token | Both — **environment-scoped** (`SB-1`) |
| `/sandbox/personas` | GET | List assigned `TS-002` personas and their identifiers | Sandbox only |
| `/sandbox/reset` | POST | Reset the caller's own sandbox tenancy | Sandbox only |
| `/sandbox/events/{event_type}` | POST | Emit a named event to the caller's endpoint | Sandbox only |
| `/sandbox/webhooks/replay` | POST | Re-deliver a prior delivery | Sandbox only |
| `/sandbox/webhooks/bad-signature` | POST | Deliver with an invalid signature | Sandbox only |
| `/sandbox/webhooks/stale-timestamp` | POST | Deliver outside the replay window | Sandbox only |
| `/sandbox/webhooks/out-of-order` | POST | Deliver two events with reversed `occurred_at` | Sandbox only |
| `/sandbox/webhooks/fail-endpoint` | POST | Force five consecutive failures | Sandbox only |
| `/sandbox/integrations/{id}/fail` | POST | Mark a downstream integration failed | Sandbox only |
| `X-Sandbox-Behaviour` *(header)* | — | Force an error, latency or timeout on any endpoint | Sandbox only — **rejected in production** |

**`/sandbox/*` returns `404` in production, not `403`.** A `403` confirms the route exists; a
`404` does not. This is the same reasoning as `AP-006` §4.3's out-of-scope policy applied to a
route rather than a record.

### 4.11 Sandbox-specific errors

Codes are `AP-006`'s (`CP-01`).

| Situation | Code | Remedy |
|---|---|---|
| Sandbox credential used against production, or the reverse | `401 auth.environment_mismatch` | Use the credential for the environment you are calling (`SB-1`) |
| `X-Sandbox-Behaviour` sent to production | `400 request.unknown_field` — **and the request is rejected, not ignored** | Remove the header. Ignoring it silently would let a partner ship it |
| `/sandbox/*` called in production | `404 resource.not_found` | The route does not exist in production |
| Sandbox credential expired at 90 days | `401 auth.credential_expired` | Renew self-service (`SB-4`) |
| Persona not assigned to this consumer | `403 auth.out_of_scope` | Sandbox tenancy is isolated (`SD-7`) |
| Sandbox rate limit exceeded | `429 ratelimit.exceeded` | Deliberately low. Pace the calls — this is the rehearsal (`S-05`) |
| Data referenced after a reset | `404 resource.not_found` | Re-seed. Do not assume durable state (`L-07`) |
| Requesting a capability at §4.7 | `501` *(not in the `AP-006` catalogue)* — **gap, `O-08`** | Use the alternative in §4.7 |

### 4.12 Reset, retention and housekeeping

| # | Rule |
|---|---|
| **RS-1** | Each partner's sandbox tenancy is **isolated**; a reset affects only that partner (`SD-7`) |
| **RS-2** | A partner may reset **on demand** through `/sandbox/reset` |
| **RS-3** | A scheduled platform-wide refresh runs **monthly**, restoring base persona data. Partner-created objects are removed *(cadence proposed — `O-06`)* |
| **RS-4** | Notice of a platform-wide refresh is given **7 days ahead** through the changelog (`AP-011`) |
| **RS-5** | Sandbox data has **no retention obligation** because it contains no personal data (`SD-4`). This is a direct benefit of the synthetic-data policy |
| **RS-6** | Sandbox usage is monitored. Sustained production-scale traffic against sandbox is a misconfiguration and is raised with the partner |
| **RS-7** | An abandoned sandbox — no traffic for 90 days — has its credentials expired (`SB-4`) and its tenancy archived |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `M28` `FR-IPF-019`, `FR-IPF-020` | The sandbox and partner onboarding capability. Both `P2` |
| `M28` `FR-IPF-016` | Consumer registration and credential issue |
| **`TS-002`** | The only permitted data source (`SD-1`). **Unwritten** — `O-04` |
| `TS-001` §4.7 | The six-environment specification this file adds a seventh to |
| `AP-001` §4.4 | The golden path this sandbox exists to make completable |
| `AP-004` | The webhook obligations §4.6 and §4.9 exercise |
| `AP-005` | Credential lifecycle, environments, scopes, rate-limit classes |
| `AP-006` | The codes §4.11 references |
| `AP-007`, `AP-008` | Audience-specific promotion items (`P-15`) |
| `AP-009` | Payment rail sandboxes (§4.8) |
| `AP-011` | Notice of a platform-wide refresh (`RS-4`) |
| `AP-012` | `P-02` — disclosure rows are a promotion prerequisite |
| `DM-011` | Data-quality and masking standards |
| `EO-001`, `EO-003`, `EO-005`, `EO-007` | The onboarding kits that route partners here |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per wave, and after each partner onboarding |
| Trigger for out-of-cycle review | A new forced-error trigger · a change to the reset cadence · `TS-002` publication · resolution of `O-03` (environment provisioning) · a partner reaching production without completing the gate |
| Owner | Platform Engineering Lead, with QA Lead accountable for the `TS-002` boundary and Security Lead for §4.4 |
| Change control | Changes to §4.4 (data policy) require **Security Lead and Legal Counsel** approval. Changes to §4.9 (promotion gate) require CTO. Both need a `RF-006` entry |
| Version pinning | Pinned to **API version** (`CG-006` §5) |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The sandbox is `P2` and is a prerequisite for `P1` work.** `FR-IPF-019` and `FR-IPF-020` are the two lowest-priority items in `M28` §5.2, and `AP-001`'s golden path, `AP-007` step 4, `AP-008` step 4 and every W3 courier integration depend on them. **A prerequisite cannot be lower priority than the thing it enables** | CTO | **W3 minus 3 months** |
| **O-02** | **Registered W4; first consumed W3.** `05-03` §8 lands INT-024…026 in W3 with three external courier development teams, and `AP-004`, `AP-005` and `AP-009` are all W3. Tenth consecutive category with this defect | Programme Content Lead with Platform Engineering Lead | **W3** |
| **O-03** | **`SANDBOX` is a seventh environment and `TS-001` §4.7 specifies six.** None of the six can serve — UAT emphatically cannot, because a partner exercising flows there changes the data business users are signing against (`TX-08`). This requires a correction to `TS-001` §4.7 and an addition to the environment inventory that `TS-001` `O-03` already records as unprovisioned | CTO with QA Lead and `M30` owner | **W3 — blocking partner onboarding** |
| **O-04** | **`TS-002` does not exist.** It is the only permitted data source (`TX-05`, `SD-1`), it is registered `P0`/W1, and it is unwritten. **Until it exists the sandbox has no lawful data source**, and the tempting alternative — a masked production copy — is what `SD-2` and `SD-4` exist to forbid | QA Lead | **W1 — it is already a `P0` W1 obligation** |
| **O-05** | **No sandbox endpoint or mechanism is registered.** `M28` §12.5 lists eighteen platform endpoints and none is a sandbox control. Every path in §4.10 and the `X-Sandbox-Behaviour` header are proposals of this file | Platform Engineering Lead | **W3 design** |
| **O-06** | **Three cadences are proposals**: 90-day credential expiry (`SB-4`), monthly platform refresh (`RS-3`), 90-day abandonment (`RS-7`). None has a source | Platform Engineering Lead | W3 |
| **O-07** | **Nine third-party integrations have unknown sandbox availability**, four of them at W3 (`AP-009` `O-05`, §4.8). An integration whose third party has no sandbox can only be proven in production | Treasury and Platform Engineering Lead with the owning modules | **W3 minus 2 months** |
| **O-08** | **`AP-006` has no code for "capability not available in this environment".** §4.11 needs one; `501` is used in the table with no catalogue entry behind it, which breaches `AP-006` `CG-03` | Platform Engineering Lead | W3 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the §4 subdivision is the only addition and is justified
- [x] The is/is-not table stated before anything else
- [x] **The seventh-environment finding derived by testing each of `TS-001` §4.7's six against the requirement, not asserted**
- [x] Five sandbox credential rules including the pre-contract issue rule
- [x] **Data policy stated as stricter than `NFR-071`, with the PDPA reasoning that makes synthetic preferable to masked**
- [x] Eleven simulated capabilities and seven deliberate limitations, so limitations are not raised as defects
- [x] Twelve forced-error triggers, with the three that a partner will not ask for identified
- [x] Third-party sandbox availability counted, with unknowns recorded as unknown (`CG-012`, `CM-R8`)
- [x] **Sixteen-item promotion gate, with the five items that make it a gate rather than a formality identified**
- [x] Endpoint reference with every path marked as a proposal
- [x] Sandbox-specific errors referencing `AP-006`, with the one missing code recorded as a gap
- [x] Reset and retention rules, including the retention benefit the synthetic-data policy buys
- [x] All internal links resolve
- [x] Eight open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` a `P2` prerequisite for `P1` work — outstanding**
- [ ] **`O-03` `SANDBOX` is unrecognised as an environment — outstanding; requires a `TS-001` §4.7 correction**
- [ ] **`O-04` `TS-002` unwritten — outstanding; the sandbox has no lawful data source without it**
- [ ] **`O-07` nine third-party sandboxes unknown, four at W3 — outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and CTO**
- [ ] Bengali counterpart — n/a; developer audience, English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
