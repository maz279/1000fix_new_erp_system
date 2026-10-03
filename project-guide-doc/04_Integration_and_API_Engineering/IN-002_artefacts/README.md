# `IN-002_artefacts/` — Executable API Contracts

**Governed by** [`../IN-002_API_Specification_OpenAPI_Contracts.md`](../IN-002_API_Specification_OpenAPI_Contracts.md)
· **Issued** 2026-08-18 · **CONFIDENTIAL — Internal Use Only**

---

## What this folder is

The machine-readable half of `IN-002`. Per `GV-011` `CM-20`, supporting artefacts sit in a subfolder
sharing the document's ID stem.

> **These are the first non-markdown files in the four-repository estate.** Enumeration at
> **2026-08-18 14:40 (+06)** returned **0** files of any non-`.md` type across
> `1000fix_ERP_Module`, `project_content`, `primary-doc` and `old-primary-doc`. Every API contract,
> DDL script, Terraform module and schema in the programme is written from nothing.

## Contents

```
_shared/
  components.yaml   Shared schemas, parameters, headers        (IN-002 §5)
  errors.yaml       RFC 9457 Problem Details + the 90 codes    (IN-002 §6)
  security.yaml     The three securitySchemes                  (IN-002 §7)

service-delivery/openapi.yaml   16 operations — M01, M17       (IN-002 §9)
commercial/openapi.yaml          6 operations — M09, M36
finance/openapi.yaml             5 operations — M20
platform/openapi.yaml            8 operations — M28
```

**35 of 1,187 operations — 2.9%.** Four of eleven bounded contexts. Counted by parsing the
files at 2026-08-18 15:10 (+06), not by summing the list above (`PG-M10`). The remaining seven contexts
are scheduled in `IN-002` §11.3.

## Status of these files

| Property | Position |
|---|---|
| **Hand-authored** | Yes — deliberately. No code exists. Per `IN-002-D-02` these become **generator fixtures**: the generator is correct when it reproduces them |
| **Scopes** | Every operation carries `x-scope-status: proposed`. **Publication is blocked (`FF-54`) until `IN-005` §5 ratifies the vocabulary** |
| **Base path** | Resource-scoped per `IN-001-D-01`. **Blocked on ratification of that ruling (`IN-001` Q-01)** |
| **Servers** | `sandbox` and placeholder hosts only. No production URL is published here |
| **Examples** | Synthetic. No real personal data, per `AP-012` |

## How to validate

```bash
# Meta-schema validation — FF-46
npx @redocly/cli lint service-delivery/openapi.yaml
npx @redocly/cli lint commercial/openapi.yaml
npx @redocly/cli lint finance/openapi.yaml
npx @redocly/cli lint platform/openapi.yaml

# Bundle for partners whose tooling cannot follow external $ref  (IN-002 Q-05)
npx @redocly/cli bundle service-delivery/openapi.yaml -o dist/service-delivery.bundled.yaml

# operationId uniqueness across all contracts — FF-47
grep -rh 'operationId:' */openapi.yaml | sort | uniq -d      # must be empty
```

> The toolchain above is illustrative. **`IN-002` Q-04 records that no generator has been chosen**,
> and the choice constrains the route-decorator form in every module (`AR-007` §5).

## Rules these files demonstrate

| Rule | Where to see it |
|---|---|
| `IN-002-D-03` RFC 9457 embedding | `_shared/errors.yaml` — `Problem` schema |
| `IN-002-D-04` `{data, page}` envelope | `_shared/components.yaml` — `PageEnvelope` |
| `IN-002-D-05` `403` for out-of-scope **and** unknown | `commercial/openapi.yaml` — `getWarrantyClaim` |
| `IN-002-D-06` paired Bengali fields | `_shared/components.yaml` — `PersonName`, `Address` |
| `IN-002-D-07` scope derived from aggregate × action | every `x-scope` |
| `IN-001` `ID-08` 7-day money idempotency | `finance/openapi.yaml` — `confirmPayment` |
| `AP-04`'s three missing endpoints | `platform/openapi.yaml` — `registerWebhookEndpoint`, `testWebhookEndpoint`, `rotateWebhookSecret` |
| `IN-001` §9.2's unowned CON-03 endpoint | `finance/openapi.yaml` — `confirmPayment` |
| `IN-001` §11.2's M17/M49 contest, resolved | `service-delivery/openapi.yaml` — `/customer-assets` |

---

*`IN-002_artefacts` · Category 04 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
