# Portal Conventions — the shared contract every R2/R4 client follows (PP1-M03-T02)

This document is the `contracts/portal/` companion to the OpenAPI specs: the
cross-cutting conventions every portal and mobile app MUST honour, so that
`libs/ts/api-client` (and its Dart counterpart in PP4) stays the single HTTP
surface.

## Transport & addressing

- All traffic goes through the **Kong gateway** (P-11) — never directly to
  Odoo or the database. Local: `http://127.0.0.1:8000` (compose `integration`
  profile); production: the environment's `FIX_API_BASE`.
- HTTPS only outside loopback. No hard-coded hosts in app code — the base URL
  comes from `FIX_API_BASE` (env) via the api-client default.

## Identity

- **OIDC via Keycloak** (`1000fix-dev` realm locally, DE-09 synthetic users).
  Portals hold no credentials: the host app injects a bearer-token getter into
  the api-client; PP3 wires the code flow. Tokens never appear in code, logs
  or fixtures (standing constraint).
- Every request carries `Authorization: Bearer <token>` when a session exists
  (the api-client does this — apps never set headers by hand).

## Locale & tenancy headers

- `Accept-Language: en | bn` — the api-client sets it; server responses
  return localised strings where the schema declares them (e.g. P01 tracking
  events carry `label_en` + `label_bn`).
- Corporate tenancy is derived from the token (Keycloak claims) — portals do
  not send tenant headers by hand.

## Errors — the single envelope

```json
{ "error": { "code": "http_422 | domain code", "message": "…" } }
```

`libs/ts/api-client` raises `ApiError(status, code, message)` — UIs render
from the registry (`common.error.*` keys), never hand-write message text.
**422 responses are server-side validation** (AS-09): the portal displays
them; it never re-implements the rule (e.g. consent-without-proof).

## Money & data rules (03-DATA-STRATEGY)

- Monetary values cross the wire as **backend-computed strings**
  (BN-007-formatted) — the client renders, never calculates.
- Pagination is capped server-side (`limit ≤ 100` in every list operation).

## Versioning

- Specs in `contracts/openapi/` are the source; breaking changes bump the
  spec `info.version` major and the api-client regeneration in the same
  commit (FF-40 validates every spec; PS-11 suites pin behaviour).
