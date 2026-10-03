---
id: AP-006
title: Error Code Catalogue and Remediation Copy
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
reviewers: [CTO, Solution Architect, Content Design Lead, Security Lead, Localisation Lead, Support Lead, QA Lead]
approver: Content Design Lead with CTO
content_class: D
purpose: >
  Every error a 1000FiX API returns, with its machine-readable code, the cause in the caller's
  terms, the remedy the caller can act on, and whether retrying is safe — plus the binding between
  each code and its `UI-004` human-facing counterpart so that one business condition is never
  described two different ways to two audiences. Without it every non-2xx becomes a support ticket:
  integration partners escalate errors they could resolve themselves, `NFR-078`'s "state what
  happened and what to do next" is satisfied only inside the user interface, and the same blocked
  action is explained one way on a screen and not at all through the API.
traces_to: [M28, M28 FR-IPF-006, M28 FR-IPF-009, M28 FR-IPF-043, 05-03, 05-03 §5.2, 05-03 API-04, 05-03 API-08, 05-03 API-11, 05-05, 05-06 NFR-078, 05-06 NFR-086, 05-06 NFR-090, 05-06 NFR-091, PS-09, UI-004, UI-005, UI-009, CG-003, CG-011, AP-001, AP-002, AP-004, AP-005, AP-009, AP-012, OP-001, OP-003, TS-017, RF-001]
priority: P1
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md §5.2 API-04 standard error envelope (`code`, localised `message`, `details`, `correlation_id`), API-08 rate-limit response, API-10 scope, API-11 Accept-Language
    verified: 2026-08-18
    class: P1
  - source: project_content/03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-004_Validation_and_Error_Message_Library.md §3.1 three-part structure, §3.2–§3.5 the `common.error.*` key families, §5.1 rules E-01…E-09, §5.2 system errors
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md NFR-078 every error states what happened and what to do next in the user's language; §12 AS-01…AS-15
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md — the `BRU-` rule register and the H / A / S / C classification that determines whether an error is overridable
    verified: 2026-08-18
    class: P1
  - source: RFC 9457 Problem Details for HTTP APIs — type, title, status, detail, instance plus extension members; successor to RFC 7807 and backward compatible. https://datatracker.ietf.org/doc/html/rfc9457
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# Error Code Catalogue and Remediation Copy

| Item | Value |
|---|---|
| Error domains | 12 (§4.3) |
| Codes catalogued in this file | **74** |
| Codes authored in `AP-005` §4.10 and referenced, not restated | **17** (`auth.*`, `ratelimit.*`) |
| **Total catalogue** | **91** |
| Codes bound to a `UI-004` key | 24 (§4.9) |
| Codes bound to an `05-05` `BRU-` rule | 20 (§4.7) |
| Retryable codes | 11 (§4.8) |
| Envelope | `API-04` four-field, with the RFC 9457 position recorded (§4.2) |
| Wave | W3 registered · **first consumed W1** — open item `O-01` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order; §4 subdivided by volume. The **error catalogue table** required
> by `CG-009` §3 is §4.4–§4.7, and is the reason this file exists. The **endpoint reference
> table** required by `CG-009` §3 is §4.10 — the errors are indexed by the endpoint class that
> emits them, because a developer arrives at this file holding an endpoint and a status code.

---

## 1. Purpose

The register justification is exact: *"Integration partners escalate to the company for errors
they could resolve themselves if the catalogue existed."*

`API-04` gives the envelope — `code`, localised `message`, `details`, `correlation_id`. It does
not give a single code. `NFR-078` requires every error to state what happened and what to do next,
in the user's language; `PS-09` repeats it for portals. Both are satisfied inside the interface by
`UI-004`, which is a well-built library of 24 messages with a three-part structure and an
enforcement rule (`CG-008` `B-10`) that a message missing the remedy cannot be approved.

**None of that reaches an API caller.** A partner's server receives `{"code": "...", "message":
"..."}` and has no register telling it which codes exist, which are permanent, which are worth
retrying, and which mean *your credential is wrong* rather than *your data is wrong*. The
observable consequences are three, and all three are expensive:

1. **Escalation.** Every unexpected code becomes a ticket, because the alternative is guessing.
2. **Retry storms.** A partner that cannot tell a permanent failure from a transient one retries
   both. `BRU-SRM-02` — device not under warranty — is permanent, and retried in a loop it
   consumes the partner's rate limit and ours.
3. **Divergent explanations.** The same blocked action is explained one way on a branch agent's
   screen and a different way, or not at all, to the brand partner's system attempting it through
   the API. `05-05` `BR-STD-01` already establishes that a rule bypassed by an API call is not a
   rule; the same logic applies to its explanation.

**What stops working without this file.**

| Absent | Consequence |
|---|---|
| A code register | `AP-002` `AR-15` requires every operation to document every error it can return, by code. There is nothing to document against, so the rule cannot pass CI |
| Retry-safety classification | Partners retry permanent failures and give up on transient ones. Both are wrong and only one is visible to us |
| Remedy copy | Support answers the same question repeatedly, in whatever words the agent chooses that day (`OP-003` macro library has no API error content) |
| `UI-004` binding | One condition acquires two independent descriptions. When one changes, the other does not |
| Rule-class exposure | A caller cannot tell a hard block (`H`) from an overridable one (`A`). The first should never be retried; the second needs a human with authority |
| Scope-error distinction | "You lack the scope" and "the record is not yours" are conflated into one `403`, and neither partner nor support can tell which |

---

## 2. Scope

**In scope.** The error envelope and its RFC 9457 position; the code taxonomy; the HTTP status
mapping policy; the full catalogue across twelve domains with cause, remedy and retry safety; the
business-rule error family and its `05-05` binding; the retry-safety matrix; the `UI-004` binding
register; localisation behaviour; the endpoint-class index; and the governance for adding a code.

**Out of scope.**

| Out of scope | Owned by | Note |
|---|---|---|
| Authentication, scope and throttling codes | **`AP-005` §4.10** | Seventeen codes authored there and **referenced here, not restated** (`CP-01`). §4.4 carries the index row only |
| Human-facing error strings | `UI-004`, `UI-005`, `UI-009` | §4.9 is the **binding**, not a copy. Neither file restates the other's text |
| Business rules themselves | `05-05` and the owning module | This file names the rule and its class; it does not define or change it |
| Webhook consumer response codes | `AP-004` §4.10 | The reciprocal contract — codes a consumer returns to us |
| Payment gateway error codes | `AP-009` §4.7 | A gateway's own codes are the gateway's; §4.6 covers only how they surface through our API |
| Error envelope documentation conventions | `AP-002` §4.7 | How to document an error; this file is what to document |
| Support routing and escalation | `OP-001` | The remedy column tells the caller what to do; it does not route a ticket |
| Bengali translation of `message` | `BN-009`…`BN-013` string bundles | `API-11` localises `message`; the translations live with the string bundles, not here |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Integration partners** | The single most-read reference page after authentication in every comparable estate. Read at 02:00 with a failing integration |
| **Internal module teams** | Choosing the right code rather than inventing one (§4.11) |
| **Portal platform team** | Mapping API errors into portal user experience without inventing new text |
| **Support (`OP-001` tiers 1–2)** | The remedy column is written to be quoted directly; `OP-003` macros should cite it rather than paraphrase |
| **Content Design** | Custodian of the remedy copy's voice and of the `UI-004` binding |
| **QA** | Negative-case expected results. A negative test asserts a **code**, not a status |
| **Localisation** | Which strings are translated (`message`) and which are never (`code`, `details`) |

---

## 4. Content

### 4.1 Six principles

| # | Principle | Consequence |
|---|---|---|
| **EP-01** | **The `code` is the contract; the `message` is the courtesy.** Callers branch on `code`, never on `message` or on HTTP status alone | A message may be reworded or retranslated at any time without notice; a code may not (§4.11) |
| **EP-02** | **Every error states a remedy the caller can act on.** An error whose remedy is "contact support" is a defect in this catalogue unless support genuinely is the only route | `NFR-078` extended from screens to APIs |
| **EP-03** | **An error never reveals the existence of a record outside the caller's scope** | `API-10`, `EA-01`, `AP-002` ED-06. This is why §4.4 has two distinct `403` codes and no `404` for out-of-scope records |
| **EP-04** | **An error never exposes internal detail** — no table names, no model names, no stack traces, no SQL, no internal identifiers | `UI-004` `E-02` applied to APIs; `AP-002` `AR-27` |
| **EP-05** | **Retry safety is declared, not inferred** | Every entry carries it. A caller that has to guess will guess wrong in the expensive direction |
| **EP-06** | **One condition, one code, one `UI-004` key** | `CP-01`. Two codes for one condition is the same defect as two names for one event (`AP-003` §4.9) |

### 4.2 The envelope

`API-04` specifies four fields. This file documents them and records the standards position
rather than deviating from it.

```json
{
  "code": "srm.warranty_inactive",
  "message": "This device is not under warranty on 18 August 2026. Its warranty ended 2 March 2026.",
  "details": {
    "device_id": "DEV-0294817",
    "warranty_expiry": "2026-03-02",
    "rule": "BRU-SRM-02",
    "rule_class": "H"
  },
  "correlation_id": "7c1f4b2e-9a33-4f61-8b7d-2e5c1a09d4f6"
}
```

| Field | Localised | Stable | Notes |
|---|:--:|:--:|---|
| `code` | **Never** | **Yes** — permanent once published | Lower snake case, `<domain>.<condition>` |
| `message` | **Yes** — `Accept-Language`, `bn-BD` or `en` (`API-11`) | No | Human-readable. **Never parsed** |
| `details` | **Never** | Additive only | Machine-readable context. Field names are stable; new fields may be added within a version |
| `correlation_id` | — | — | Present on **every** response, error or not (`API-09`, `NFR-092`) |

**Two `details` conventions this file introduces**, because they are what make a business-rule
error actionable rather than merely descriptive:

| Key | Present when | Purpose |
|---|---|---|
| `rule` | The error is a business-rule violation | The `05-05` `BRU-` identifier. **Machine-readable only** — `UI-004` `E-06` forbids showing it in user-facing text, and `details` is not user-facing |
| `rule_class` | Same | `H` hard · `A` approved override · `S` soft warning · `C` computed. **This is what tells a caller whether a human with authority can unblock it** |

> **The RFC 9457 position.** The industry default for HTTP API errors is RFC 9457 Problem Details
> — `type`, `title`, `status`, `detail`, `instance`, extension members, and a shared registry of
> problem types. `API-04` predates it and has no `type` URI, no in-body status and no multi-problem
> form. **This file does not change the standard**; `AP-002` `O-07` carries the recommendation that
> `API-04`'s four fields be emitted **as RFC 9457 extension members**, which is additive, costs one
> mapping, and lets a partner's existing Problem Details client work. Recorded here as `O-02`
> because this is the file where the cost of not doing it lands.

### 4.3 Taxonomy

```
<domain>.<condition>
```

Twelve domains. The domain tells the caller **who must act** before they read the condition, which
is the fastest possible triage.

| Domain | Meaning | Who must act | Count |
|---|---|---|---:|
| `auth` | Identity, credential, scope, step-up | The caller, or their account manager | 14 → **`AP-005` §4.10** |
| `ratelimit` | Throttling and quota | The caller, by pacing | 2 → **`AP-005` §4.10** |
| `request` | The request is malformed or unsupported | The caller, by fixing the request | 8 |
| `validation` | A field value is unacceptable | The caller, by fixing the value | 9 |
| `idempotency` | `Idempotency-Key` handling | The caller, by retry discipline | 4 |
| `resource` | The addressed thing does not exist, is gone, or conflicts | The caller, by correcting the reference | 5 |
| `state` | The object is in a state that forbids this action | The caller, by sequencing correctly | 6 |
| `rule` | A business rule blocks it | **Depends on `rule_class`** — the caller, or a human with authority | 20 |
| `data` | Consent, residency or disclosure forbids it | Legal / DPO — **not** resolvable by the caller | 6 |
| `export` | Bulk and asynchronous job handling | The caller, by using the async route | 5 |
| `dependency` | A downstream system 1000FiX depends on is failing | **1000FiX** | 6 |
| `platform` | 1000FiX internal failure | **1000FiX** | 5 |

**HTTP status mapping policy.** Status classes are coarse and a caller must not branch on them
alone (`EP-01`), but the mapping must still be consistent:

| Status | Used for | Never used for |
|:--:|---|---|
| `400` | Malformed request, unparseable body, unsupported media type | A valid request that fails a business rule |
| `401` | Authentication — no identity established | Authorisation |
| `403` | Authorisation, scope, step-up, disclosure refusal | "Not found" concealment — see `404` |
| `404` | The resource genuinely does not exist **and the caller would be entitled to see it if it did** | Concealing an out-of-scope record — that is `403 auth.out_of_scope` (`EP-03`) |
| `409` | Idempotency conflict, concurrent modification | A business-rule block |
| `410` | A resource that existed and is permanently gone | Soft-deleted records, which remain `404` or visible per `DI-08` |
| `413` | Payload too large | Result set too large — that is `422 export.result_too_large` |
| `422` | Semantically valid but unprocessable — **business rules and state errors live here** | Field-format failures, which are `400`/`validation.*` |
| `429` | Rate limit and quota | Any other kind of "too much" |
| `451` | Disclosure or residency refusal with a legal basis | Anything without one |
| `500` | Unexpected internal failure | A known dependency failure — that is `503` |
| `503` | A named dependency is unavailable; fallback engaged or unavailable | Rate limiting |

> **`404` versus `403 auth.out_of_scope` is the most consequential row in that table.** Returning
> `404` for a record that exists but belongs to another party leaks nothing; returning `404` for
> some and `403` for others leaks everything, because the difference is an oracle. The policy is:
> **out-of-scope always returns `403 auth.out_of_scope`, uniformly, whether or not the record
> exists.** `TS-017` verifies it.

### 4.4 Catalogue — request, validation, idempotency, resource

| HTTP | Code | Cause | Remedy | Retry |
|:--:|---|---|---|:--:|
| `400` | `request.malformed` | The body could not be parsed as JSON | Check the body is valid JSON and `Content-Type` is `application/json` | No |
| `400` | `request.unsupported_media_type` | `Content-Type` is not accepted by this endpoint | Send `application/json`, or `multipart/form-data` for uploads | No |
| `400` | `request.missing_body` | A body is required and none was sent | Send the documented request body | No |
| `400` | `request.unknown_field` | A field in the body is not part of the schema **and the endpoint rejects unknown fields** | Remove the field. Check the API version — the field may belong to a later one | No |
| `400` | `request.encoding_invalid` | The body is not valid UTF-8 | Send UTF-8. Bengali content requires it and no other encoding is accepted | No |
| `400` | `request.header_missing` | A required header is absent — commonly `Idempotency-Key` | Add the header named in `details.header` | No |
| `400` | `request.version_unsupported` | The path version does not exist or has been retired | Use a supported version; see the changelog (`AP-011`) | No |
| `413` | `request.payload_too_large` | The body exceeds the endpoint's limit | Reduce the payload, or use the bulk endpoint (`API-12`) | No |
| `400` | `validation.failed` | One or more fields failed validation. `details.errors[]` lists each with its field path and reason | Fix the fields listed and resubmit | No |
| `400` | `validation.required_missing` | A required field is absent | Supply it | No |
| `400` | `validation.format_invalid` | A value does not match its required format | Correct the format. Common: `+880` phone format, RFC 3339 UTC timestamps, 10- or 17-digit NID | No |
| `400` | `validation.enum_invalid` | A value is not in the permitted set | Use a value from the enumeration in the endpoint reference | No |
| `400` | `validation.length_exceeded` | A text value exceeds its limit | Shorten it. **Limits are in characters, not bytes** — Bengali text is multi-byte | No |
| `400` | `validation.reference_invalid` | A referenced identifier does not resolve to a valid master-data record | Check the identifier against the register named in `details.register` — for example `MD-020` service types | No |
| `400` | `validation.currency_missing` | A monetary value was sent without its currency | Send both. Money is always decimal with an explicit currency (`DI-01`, `AS-10`) | No |
| `400` | `validation.date_range_invalid` | A date range is reversed, or outside the permitted window | Correct the range | No |
| `400` | `validation.language_unsupported` | `Accept-Language` requested a language other than `bn-BD` or `en` | Use `bn-BD` or `en`; anything else falls back to `en` and this code is returned only where the endpoint requires an explicit choice | No |
| `409` | `idempotency.key_reused_different_body` | The same `Idempotency-Key` was sent with a **different** request body | Use a new key for a new request. Reusing a key with different content is always a caller bug | No |
| `409` | `idempotency.in_flight` | An identical key is currently being processed | Wait 2 seconds and retry **the same key** | **Yes** |
| `400` | `idempotency.key_invalid` | The key is absent, empty, or longer than the permitted length on a state-changing operation | Send a unique key — a UUID is the expected form (`API-07`) | No |
| `422` | `idempotency.key_expired` | The key is outside the retention window, so the original result can no longer be returned | Treat the outcome as unknown and reconcile before resubmitting. **Never blind-resubmit a payment or a payout** | No |
| `404` | `resource.not_found` | The resource does not exist and the caller would be entitled to see it if it did | Check the identifier | No |
| `410` | `resource.gone` | The resource existed and is permanently removed | Stop referencing it. If it was a customer identifier, check for `customer.merged` (`AP-003`) | No |
| `409` | `resource.conflict` | The resource was modified by another actor since the caller read it | Re-read and re-apply. `details.modified_at` gives the time | **Yes**, after re-read |
| `409` | `resource.already_exists` | A uniqueness constraint would be breached | Use the existing resource, or change the unique value | No |
| `422` | `resource.identifier_superseded` | The identifier was replaced by a merge | Use `details.replacement_id` and **update your own records** | **Yes**, with the replacement |

### 4.5 Catalogue — state, data, export

| HTTP | Code | Cause | Remedy | Retry |
|:--:|---|---|---|:--:|
| `422` | `state.transition_invalid` | The object cannot move from its current state to the requested one | `details.current_state` and `details.allowed_transitions` give the valid moves. States are `MD-027`'s | No |
| `422` | `state.already_in_target` | The object is already in the requested state | Treat as success. This usually means an earlier call succeeded and the response was lost | No |
| `422` | `state.terminal` | The object is in a terminal state and cannot be changed | A reversal is a new object, not an edit (`AP-003` `EV-02`) | No |
| `422` | `state.locked` | The object is locked by a process — a period close, a payroll run, a cutover freeze | Wait for the process, or ask the owning function. `details.lock_reason` names it | **Yes**, later |
| `422` | `state.dependency_incomplete` | A prerequisite object is not in the required state | `details.blocking` names it. Common: an order cannot complete while a work order is open | No |
| `422` | `state.period_closed` | The accounting period is closed | Post to the current period, or ask Finance to reopen. Binds to `common.error.fin.period_closed` | No |
| `403` | `data.consent_absent` | Processing for this purpose requires a consent that has not been given or has been withdrawn | Obtain consent through the customer's own channel. **The caller cannot resolve this and must not retry** (`NFR-090`, `NFR-091`) | No |
| `451` | `data.residency_restricted` | The requested field is residency-classified and cannot be returned to this caller or region | Not resolvable by the caller. `NFR-086`, `NFR-099` | No |
| `403` | `data.disclosure_not_permitted` | The field is not in this counterparty's permitted disclosure set | `AP-012` governs. Widening is a legal and commercial decision | No |
| `403` | `data.minimisation_refused` | The request asked for more fields than the counterparty's purpose requires | Request only the fields you need (`IP-10`) | No |
| `422` | `data.subject_request_pending` | The record is subject to an in-flight data-subject request | Wait for resolution. `NFR-093`, `LG-010` | **Yes**, later |
| `422` | `data.retention_expired` | The record has passed its retention period and has been purged | Not recoverable. `NFR-088`, `LG-009` | No |
| `422` | `export.result_too_large` | The result set exceeds the synchronous limit | Use the asynchronous export route in `details.async_endpoint` (`API-12`) | No |
| `202` | *(not an error)* `export.accepted` | An asynchronous export was accepted | Poll `details.job_url`. Documented here because callers treat `202` as an anomaly | — |
| `403` | `export.approval_required` | Bulk personal-data export requires approval and step-up | A human requests approval; this cannot be automated (`EA-12`, `FR-SEC-041`) | No |
| `429` | `export.rate_limited` | Export-specific rate control | Space exports. Export limits are separate from the interactive limit (`AP-005` §4.7 `bulk` class) | **Yes** |
| `422` | `export.job_failed` | An accepted asynchronous export failed | `details.reason`. Resubmit if the reason is transient | Conditional |

### 4.6 Catalogue — dependency and platform

These are the codes where **1000FiX** must act. `EP-02` still applies: the remedy tells the caller
what to do while we act.

| HTTP | Code | Cause | Remedy | Retry |
|:--:|---|---|---|:--:|
| `503` | `dependency.unavailable` | A downstream system is not responding. `details.integration` names it — for example `INT-001` | Retry with backoff. Check the status page (`AP-001` §8) | **Yes** |
| `503` | `dependency.fallback_engaged` | The primary integration failed and a registered fallback is handling the request. The response may be **degraded but valid** | Proceed. `details.fallback` states what is degraded — cached geocodes, alternate gateway, last-known position (`FR-IPF-043`) | No — it succeeded |
| `503` | `dependency.no_fallback` | The integration failed and **no fallback is available** | Retry later; the manual fallback in `OP-014` applies operationally. `IP-09` requires a fallback for every `P0` integration, so this code on a `P0` integration is itself an incident | **Yes**, later |
| `504` | `dependency.timeout` | A downstream system did not respond in time | **The outcome is unknown, not failed.** For anything financial, reconcile before resubmitting (`AP-009` §4.6) | Conditional |
| `502` | `dependency.invalid_response` | A downstream system returned something we could not interpret | Not resolvable by the caller. Raise with the correlation id | **Yes** |
| `503` | `dependency.circuit_open` | The circuit breaker is open for this integration and requests are failing fast (`IP-05`) | Honour `Retry-After`. Failing fast is deliberate, not a bug | **Yes** |
| `500` | `platform.unexpected` | An unhandled internal failure. **Nothing was changed** | Quote the `correlation_id` to support. Hotline 16743 | **Yes**, once |
| `500` | `platform.outbox_failed` | The business change and its event could not be committed together, so **neither was applied** (`T-01`) | Retry with the same `Idempotency-Key`. Atomicity means there is no partial state to clean up | **Yes** |
| `503` | `platform.maintenance` | Planned maintenance within an announced window | `Retry-After`. Windows are announced 72 hours ahead (`NFR-049`, `OP-005`) | **Yes** |
| `503` | `platform.capacity` | The platform is shedding load to protect the estate | Back off with jitter. Distinct from `429`: this is our capacity, not your quota | **Yes** |
| `500` | `platform.configuration_missing` | Required configuration or master data is absent — a tax class, a sequence, a zone | Not resolvable by the caller. `details.missing` names it; the owning function must supply it | No |

### 4.7 Catalogue — business rules

**Twenty codes bound to `05-05` rules.** This family is the reason `details.rule` and
`details.rule_class` exist: a caller must be able to tell a permanent block from one a human can
authorise.

| `rule_class` | Meaning | What the caller should do |
|:--:|---|---|
| **H** Hard block | No override exists | **Do not retry.** Change the request or abandon the action |
| **A** Approved override | A named role can authorise an exception with a recorded reason | Route to a human with that authority. `details.authorising_role` names it |
| **S** Soft warning | Proceeds with a warning | Not an error; returned as a `warnings[]` array on a `2xx`, never as a failure |
| **C** Computed | The system applied a rule automatically | Not an error; surfaced as `details.applied[]` on a `2xx` |

> **Only `H` and `A` rules produce errors.** `S` and `C` rules produce successful responses that
> carry information, and a caller treating a `C` outcome as a failure — for example a loyalty tier
> auto-upgrading a priority — will report a defect that is correct behaviour. This is stated
> because `UI-004` §3.2 lists `BRU-SRM-10` (`C`) alongside hard blocks in the same table.

| HTTP | Code | `BRU-` | Class | Cause | Remedy |
|:--:|---|---|:--:|---|---|
| `422` | `rule.device_required` | `BRU-SRM-01` | H | A service order was submitted without an identified device | Identify or register the device first |
| `422` | `rule.warranty_inactive` | `BRU-SRM-02` | H | The device is not under warranty on the service date | Create a paid repair instead. `details.warranty_expiry` |
| `422` | `rule.not_on_contract` | `BRU-SRM-03` | H | The device is not on the named contract's covered-asset list | Add it to the contract, or create a paid repair |
| `422` | `rule.qc_not_passed` | `BRU-SRM-04` | H | Completion attempted with the quality checklist not passed | Complete the checklist first |
| `422` | `rule.invoice_before_complete` | `BRU-SRM-05` | H | An invoice was requested for an order that is not completed | Complete the order first |
| `422` | `rule.estimate_approval_required` | `BRU-SRM-07` / `-08` | H | Work above a threshold requires customer, and above BDT 25,000 branch-manager, approval | Obtain approval. `details.threshold`, `details.authorising_role` |
| `422` | `rule.technician_not_certified` | `BRU-SRM-09` | H | The assigned technician is not certified for this brand's warranty work | Assign a certified technician. `details.expiry` |
| `422` | `rule.parts_unapproved` | `BRU-SRM-11` | H | Parts issue attempted against an unapproved paid repair | Approve the estimate first |
| `422` | `rule.over_approval_limit` | `05-04` §7 | A | The action exceeds the caller's delegated limit | Route to `details.authorising_role` |
| `422` | `rule.self_approval` | `05-04` §6 | H | The actor cannot approve their own object | A different actor must approve |
| `422` | `rule.sod_conflict` | `SOD-01`…`SOD-12` | H | The action would breach segregation of duties | A different actor must perform it. `details.sod_rule` |
| `422` | `rule.override_reason_required` | `BR-STD-06` | H | An override was attempted with no recorded reason | Supply a reason; it is recorded against the transaction |
| `422` | `rule.stock_unavailable` | `M15` | H | The part is not in stock at the location | `details.alternative_locations`. Request a transfer or order it |
| `422` | `rule.part_incompatible` | `M15` | H | The part does not fit the model | `details.compatible_parts` |
| `422` | `rule.stock_would_go_negative` | `M15` | H | Issuing would take the location below zero | Count the location, or record a receipt first |
| `422` | `rule.hazard_acknowledgement_required` | `M15` | H | A hazard-class part requires an acknowledgement | Confirm the handling instructions have been read |
| `422` | `rule.tax_class_missing` | `M51` | H | The item has no tax class, so a compliant Mushak invoice cannot be issued | Finance must set the tax class |
| `422` | `rule.buyer_bin_required` | `M51` | H | A VAT invoice to a business requires the buyer's BIN | Add the BIN, or issue to an individual |
| `422` | `rule.tax_code_unverified` | `M51` | H | The tax code is not verified for the fiscal year | Not resolvable by the caller; Finance is completing verification |
| `422` | `rule.dimension_required` | `05-02` DM-03 | H | A posting account requires an analytic dimension | Supply the dimension named in `details.dimension` |

### 4.8 Retry-safety matrix

The single most useful table in this file for a partner writing an error handler.

| Retry safety | Codes | Correct handling |
|---|---|---|
| **Never retry** | All `validation.*`, all `request.*`, `auth.*` except `token_expired`, all `rule.*` with class `H`, `data.consent_absent`, `data.residency_restricted`, `data.disclosure_not_permitted`, `resource.not_found`, `resource.already_exists`, `state.*` except `locked` | Fix the request or escalate to a human. Retrying is guaranteed to fail and consumes quota |
| **Retry once, after a corrective action** | `auth.token_expired` (fetch a new token), `resource.conflict` (re-read), `resource.identifier_superseded` (use the replacement) | One corrective step, one retry. Not a loop |
| **Retry with backoff** | `ratelimit.exceeded`, `dependency.unavailable`, `dependency.circuit_open`, `platform.unexpected`, `platform.capacity`, `platform.maintenance`, `platform.outbox_failed`, `idempotency.in_flight`, `export.rate_limited` | Exponential backoff **with jitter**, honouring `Retry-After` where present, with the **same `Idempotency-Key`** |
| **Retry later, not immediately** | `state.locked`, `data.subject_request_pending`, `dependency.no_fallback` | The blocking condition is time-bound; minutes to hours, not seconds |
| **Outcome unknown — reconcile, do not blind-retry** | `dependency.timeout`, `idempotency.key_expired` | **The dangerous class.** For payments, payouts and custody, query the authoritative record first. `AP-009` §4.6 |

> **The last row is where money is lost.** A `504` on a payment call does not mean the payment
> failed; it means we do not know. A partner that retries it as if it failed can take payment
> twice; one that treats it as failed can lose a payment silently. Both are recorded as real
> failure modes in payment integration practice, and both are prevented by the same rule: query
> before resubmitting.

### 4.9 The `UI-004` binding register

**One business condition, one `AP-006` code, one `UI-004` key.** Neither file restates the other's
text; this register is the join, and it is what makes audit check `F4` extensible to APIs.

| `AP-006` code | `UI-004` key | `BRU-` | Same condition? |
|---|---|---|:--:|
| `rule.device_required` | `common.error.srm.device_required` | `BRU-SRM-01` | ● |
| `rule.warranty_inactive` | `common.error.srm.warranty_inactive` | `BRU-SRM-02` | ● |
| `rule.not_on_contract` | `common.error.srm.not_on_contract` | `BRU-SRM-03` | ● |
| `rule.qc_not_passed` | `common.error.srm.qc_not_passed` | `BRU-SRM-04` | ● |
| `rule.invoice_before_complete` | `common.error.srm.invoice_before_complete` | `BRU-SRM-05` | ● |
| `rule.estimate_approval_required` | `common.error.srm.estimate_approval_5k` · `…_25k` | `BRU-SRM-07`, `-08` | ● — **two UI keys, one API code**; the threshold is in `details` |
| `rule.technician_not_certified` | `common.error.srm.tech_not_certified` | `BRU-SRM-09` | ● |
| `rule.parts_unapproved` | `common.error.srm.parts_unapproved` | `BRU-SRM-11` | ● |
| `rule.over_approval_limit` | `common.error.approval.over_limit` | — | ● |
| `rule.self_approval` | `common.error.approval.self` | — | ● |
| `rule.override_reason_required` | `common.error.approval.reason_required` | `BR-STD-06` | ● |
| *(no API code — `2xx` with `warnings[]`)* | `common.error.approval.override_available` | — | Class `A` advisory; not an API error |
| `rule.stock_unavailable` | `common.error.stock.unavailable` | — | ● |
| `rule.part_incompatible` | `common.error.stock.incompatible` | — | ● |
| `rule.stock_would_go_negative` | `common.error.stock.negative` | — | ● |
| `rule.hazard_acknowledgement_required` | `common.error.stock.hazard_ack` | — | ● |
| `state.period_closed` | `common.error.fin.period_closed` | — | ● |
| `rule.tax_class_missing` | `common.error.fin.no_tax_class` | — | ● |
| `rule.buyer_bin_required` | `common.error.fin.bin_required` | — | ● |
| `rule.tax_code_unverified` | `common.error.fin.tax_unverified` | — | ● |
| `rule.dimension_required` | `common.error.fin.dimension_required` | — | ● |
| `dependency.unavailable` · `dependency.no_fallback` | `common.error.system.unavailable` | — | ● |
| `dependency.timeout` | `common.error.system.timeout` | — | ⚠ **Not the same.** `UI-004` says "Nothing was saved"; the API cannot assert that — see the note below |
| `resource.conflict` | `common.error.system.conflict` | — | ● |
| `platform.unexpected` | `common.error.system.unexpected` | — | ● |

**Three findings fall out of building this register, and all three are material.**

1. **`common.error.system.timeout` asserts something the API cannot.** `UI-004` §5.2 reads *"This
   took longer than expected and was stopped. Nothing was saved. Try again."* On a synchronous UI
   action against a single transaction that is true. On an API call to an endpoint that may have
   committed before the gateway timed out, **it is not**, and it is the exact assertion that
   causes double submission. The API code `dependency.timeout` therefore says the opposite: *the
   outcome is unknown*. `UI-004` should carry a second key for the API-mediated case. Recorded as
   `O-04`.

2. **`BRU-SRM-06` and `BRU-SRM-10` have `UI-004` keys and no API code, correctly** — both are
   class `C`, computed, and produce successful responses. Their presence in a table headed
   "Validation and error messages" is a `UI-004` presentation issue, not an error.

3. **Eleven `UI-004` keys map to `05-05` rules; nine map to no rule identifier at all** — the
   approval, stock and finance families. `05-05` is the register those should resolve against.
   Whether the rules exist there under other identifiers, or in the owning module as `M15` and
   `M51` families, is unresolved and mirrors the module-scoped rule-family pattern `AUDIT-010` and
   `AUDIT-014` already recorded. Recorded as `O-05`.

### 4.10 Endpoint-class index

The endpoint reference table required by `CG-009` §3, inverted for the way this file is actually
used: a developer arrives holding an endpoint and a status.

| Endpoint class | Always possible | Commonly seen | Never |
|---|---|---|---|
| **Any authenticated endpoint** | `auth.*` (5), `ratelimit.exceeded`, `platform.unexpected`, `platform.maintenance` | — | — |
| **Reads — single resource** | + `resource.not_found`, `auth.out_of_scope` | `data.disclosure_not_permitted` | `idempotency.*`, `validation.*` |
| **Reads — collections** | + `validation.format_invalid` on filters | `export.result_too_large` | `state.*` |
| **Writes — create** | + `validation.*`, `idempotency.*`, `rule.*`, `resource.already_exists` | `dependency.*` | `resource.gone` |
| **Writes — update / transition** | + `state.*`, `resource.conflict`, `rule.*` | `state.locked` | `resource.already_exists` |
| **Approval / decision endpoints** | + `rule.over_approval_limit`, `rule.self_approval`, `rule.sod_conflict`, `auth.step_up_required` | `auth.mfa_required` | — |
| **Payment and payout endpoints** | + `dependency.timeout`, `dependency.fallback_engaged`, `idempotency.key_expired` | `dependency.no_fallback` | — |
| **Export and bulk endpoints** | + `export.*`, `auth.export_not_permitted` | `data.minimisation_refused` | — |
| **Endpoints returning personal data** | + `data.consent_absent`, `data.residency_restricted`, `data.subject_request_pending` | `data.retention_expired` | — |

### 4.11 Governance — adding, changing and retiring a code

| # | Rule |
|---|---|
| **CG-01** | A code is **permanent once published**. Retiring one requires the `AP-011` deprecation process, because callers branch on it (`EP-01`) |
| **CG-02** | A new code requires: a domain from §4.3, a unique condition not already covered (`EP-06`), a cause, a remedy, a retry classification, and a `UI-004` binding **or** a recorded statement that the condition has no user-facing counterpart |
| **CG-03** | A module may **not** invent a code outside this catalogue. A condition with no code uses the nearest domain code with `details`, and the gap is raised here |
| **CG-04** | Changing a code's **meaning** is a breaking change even if the string is unchanged. Add a new code instead |
| **CG-05** | Changing a code's **message** is not a breaking change and needs no notice — that is what `EP-01` buys |
| **CG-06** | Changing a code's **retry classification** is a breaking change. A partner's error handler is built on it |
| **CG-07** | The catalogue is held as a **data file** and generated into the developer portal (`AP-001` PT-08). This markdown is the source; the portal page is the output |
| **CG-08** | Every code in this catalogue must be **emittable**. A code nobody emits is removed at the next review; measured by `AP-002` DC-04 against production error logs |

**Localisation.** `message` is localised by `Accept-Language` into `bn-BD` or `en` (`API-11`,
`AR-24`). `code` and `details` are never translated. The Bengali strings live in the `BN-009`…`BN-013`
bundles with every other user-facing string, **not in this file** — because an API `message` shown
to a branch agent through a portal is the same string that agent sees elsewhere, and duplicating
it here would create the two-descriptions defect `EP-06` forbids.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `05-03` `API-04` | The envelope this catalogue populates |
| `05-05` | The `BRU-` rules and their `H`/`A`/`S`/`C` class — §4.7 is meaningless without it |
| **`UI-004`** | The binding target of §4.9. The two files must be changed together |
| `AP-002` `AR-15`, `AR-16` | Requires every operation to document every error by code — this is the register it documents against |
| `AP-005` §4.10 | The 17 `auth.*` and `ratelimit.*` codes, authored there |
| `AP-004` §4.10 | The reciprocal contract for webhook consumers |
| `AP-009` §4.6 | Payment-specific handling of the unknown-outcome class |
| `AP-012` | The disclosure decisions the `data.*` domain enforces |
| `MD-027` | State names referenced by `state.transition_invalid` `details` |
| `OP-003` | Support macro library — should cite these remedies rather than paraphrase them |
| `TS-017` | Negative cases assert codes, not statuses; §4.3's `404`/`403` policy is a named test |
| `RF-001` | Term register — **unwritten** |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per wave, as each wave's modules add conditions |
| Trigger for out-of-cycle review | A new `05-05` hard rule · a `UI-004` change · adoption of RFC 9457 (`O-02`) · a `DC-04` measurement showing undocumented codes in production · a support trend showing a remedy that does not work |
| Owner | Platform Engineering Lead, with Content Design Lead accountable for the remedy copy's voice and the `UI-004` binding |
| Change control | Adding a code needs the owning module and Platform Engineering. **Changing a retry classification or retiring a code needs CTO approval, a `RF-006` entry and notice under `AP-011`** (`CG-06`, `CG-01`) |
| Version pinning | Pinned to **API version** (`CG-006` §5) |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **Registered W3; first consumed W1.** `FR-IPF-006` enforces the standard error envelope from W1 and `AP-002` `AR-15` cannot pass CI without this register. Every W1 and W2 endpoint will emit codes invented at the keyboard, and `CG-01` then makes each of them permanent. Ninth consecutive category with this defect | Programme Content Lead with Platform Engineering Lead | **W1 — before the first endpoint returns an error** |
| **O-02** | **`API-04` versus RFC 9457** (also `AP-002` `O-07`). The four-field envelope has no `type` URI and no multi-problem form, so a partner with a Problem Details client gets no benefit. The recommendation is additive — emit `API-04` fields as RFC 9457 extension members. **This is the file where the cost of not doing it lands**, because 91 codes are cheaper to publish once with a `type` URI than to retrofit | Solution Architect with CTO | **W1 — the envelope is built in W1** |
| **O-03** | **Twenty business-rule codes cover four `05-05` families.** `05-05` holds far more rules than the ones with a `UI-004` key, and `AP-002` `AR-15` requires every emittable error to be documented. **The full rule-to-code mapping cannot be completed until each module's rules are built**, so this catalogue grows every wave and `CG-08` must be run every wave or it silently drifts | Platform Engineering Lead with each module owner | **Per wave, from W1** |
| **O-04** | **`common.error.system.timeout` asserts "Nothing was saved", which an API cannot assert.** On an API-mediated timeout the outcome is unknown, and asserting otherwise is the direct cause of double submission on payment paths. `UI-004` needs a second key for the API-mediated case, and this is a change to a Category 03 file | Content Design Lead with Platform Engineering Lead | **W3 — before payment integrations land** |
| **O-05** | **Nine `UI-004` keys resolve to no rule identifier.** The approval, stock and finance families carry no `BRU-` reference in `UI-004` and this file could not supply one. Either the rules exist in `05-05` under identifiers `UI-004` does not cite, or they are module-scoped families like `BRU-QMS-*` — the pattern `AUDIT-014` §2 recorded as "the variant that will catch the next author out" | Enterprise Architecture with Content Design Lead | W3 |
| **O-06** | **No `warnings[]` convention exists** for class `S` and `C` rule outcomes. §4.7 states they are returned on `2xx` rather than as errors, and `05-03` §5.2 defines no such field. Without it, a computed outcome — a loyalty tier upgrading a priority, a rework link being created — is invisible to an API caller | Solution Architect | W3 |
| **O-07** | **The catalogue has no data file yet.** `CG-07` requires it to be held as data and generated into the portal (`AP-001` PT-08). Until the format and location are decided, the markdown is the only artefact and drift between it and the implementation is unmeasurable | Platform Engineering Lead | W3 |
| **O-08** | **Audit check `F4` covers `MD` → `UI-004` only.** With this binding register in place, `F4` should equally verify `AP-006` → `UI-004`. That is a change to `AUDIT_Checklist_Recurring.md` and is recommendation `R-04` of the Category 15 audit | Programme Content Lead | W3 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the §4 subdivision is the only addition and is justified
- [x] Six principles stated before the catalogue that applies them
- [x] Envelope documented with the localisation and stability property of every field
- [x] **`details.rule` and `details.rule_class` conventions introduced, so a caller can tell a hard block from an overridable one**
- [x] Twelve domains with the who-must-act triage
- [x] HTTP status mapping policy including the `404` versus `403` concealment rule
- [x] **74 codes catalogued here; 17 referenced to `AP-005` and deliberately not restated (`CP-01`)**
- [x] Every entry carries cause, remedy and retry safety
- [x] Retry-safety matrix with the unknown-outcome class called out as the one where money is lost
- [x] **`UI-004` binding register built, with the three findings it surfaced recorded rather than smoothed over**
- [x] Endpoint-class index for the way the file is actually used
- [x] Eight governance rules including code permanence and the emittability sweep
- [x] Localisation position stated, with duplication of Bengali strings explicitly refused
- [x] All internal links resolve
- [x] Eight open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` registered after first consumption — outstanding; codes invented in W1 become permanent under `CG-01`**
- [ ] **`O-02` RFC 9457 decision — outstanding; cheapest before 91 codes are published**
- [ ] **`O-04` `UI-004` timeout copy asserts what an API cannot — outstanding; a double-submission cause**
- [ ] **`O-07` no catalogue data file — outstanding; drift is unmeasurable until there is one**
- [ ] Named approvers recorded — **pending Content Design Lead and CTO**
- [ ] Bengali counterpart — n/a; developer audience, English-only per `CG-010` §3.2. **The `message` strings this catalogue emits are localised through `BN-009`…`BN-013`, not here**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
