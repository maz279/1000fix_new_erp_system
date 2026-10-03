---
id: PGD-CAT-04
category: 04 — Integration & API Engineering
code: IN
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
owner: Integration Architect
enumeration_timestamp: 2026-08-18 21:55 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
audit: ../_AUDIT/PGD-AUDIT-007_Category_04_Integration_and_API_Engineering_Audit.md
---

# Category 04 — Integration & API Engineering (`IN`)

## Purpose

The ERP is the system of record for **12 portals, 4 mobile applications, 17+ brand partners,
500–2,000 marketplace sellers, three payment rails, the NBR VAT Online portal, BEFTN, courier
networks and a pre-existing portal platform that constraint `CON-03` says cannot be replaced**.

Every one of those is an integration contract. An undocumented contract is a production incident
with a delay fuse.

---

## ✅ Authored — 8 of 8 issued 2026-08-18

| ID | Document | Status | Pri | Needed by |
|---|---|:--:|:--:|:--:|
| [`IN-001`](IN-001_Integration_Architecture_Specification.md) | Integration Architecture Specification | ✅ | **P0** | **W1** |
| [`IN-002`](IN-002_API_Specification_OpenAPI_Contracts.md) | **API Specification — OpenAPI 3.1 Contracts** | ✅ ◐* | **P0** | **W1** |
| [`IN-003`](IN-003_Domain_Event_Catalogue_and_Schema_Registry.md) | **Domain Event Catalogue & Schema Registry** | ✅ ◐* | **P0** | **W1** |
| [`IN-004`](IN-004_Interface_Control_Documents.md) | Interface Control Documents (ICD) — per external system | ✅ ◐* | P0 | W2 |
| [`IN-005`](IN-005_API_Governance_Versioning_and_Deprecation_Standard.md) | API Governance, Versioning & Deprecation Standard | ✅ | **P0** | **W1** |
| [`IN-006`](IN-006_Webhook_Callback_and_Partner_Push_Specification.md) | Webhook, Callback & Partner Push Specification | ✅ | P0 | W1 |
| [`IN-007`](IN-007_Payment_and_Financial_Gateway_Integration_Design.md) | Payment & Financial Gateway Integration Design | ✅ | P0 | W3 |
| [`IN-008`](IN-008_Integration_Test_Sandbox_and_Certification_Specification.md) | Integration Test, Sandbox & Certification Specification | ✅ | P1 | W2 |

\* **`IN-002`, `IN-003` and `IN-004` are inherently incremental** — ✅ as standards, ◐ as sets.
`IN-002` issues the standard and 35 of 1,187 operations; `IN-003` the registration standard and two
of 988 schemas; `IN-004` 14 of 47 ICDs, all at `Draft`. The remainders are scheduled and **unfunded**.

### Executable artefacts — the estate's first non-markdown files

```
IN-002_artefacts/                        IN-003_artefacts/
  README.md                                README.md
  _shared/components.yaml                  reconciliation/portal-consumed-unpublished.csv
  _shared/errors.yaml                      schemas/service_order.delivered.v1.json
  _shared/security.yaml                    schemas/warranty_claim.evidence_incomplete.v1.json
  service-delivery/openapi.yaml            service-delivery/asyncapi.yaml
  commercial/openapi.yaml
  finance/openapi.yaml
  platform/openapi.yaml
```

**Enumeration at 2026-08-18 14:40 (+06) returned 0 files of any non-`.md` type across
`1000fix_ERP_Module`, `project_content`, `primary-doc` and `old-primary-doc`.** Every OpenAPI file,
JSON Schema, AsyncAPI document and DDL script in the programme is written from nothing.

All seven YAML files parse; both JSON Schemas parse; the CSV has 69 rows. Verified 2026-08-18.

---

## What the category measured

Extraction across all **67 module `§12` tables** and all **12 portal specifications**,
**2026-08-18 14:40–17:25 (+06)**:

| # | Measure | Count |
|---|---|---:|
| M-01 | Distinct API paths declared by modules | **978** |
| M-02 | Distinct `(method, path)` operations | **1,187** |
| M-03 | Distinct paths **consumed by portals** | 140 |
| M-04 | **Of M-03, declared by no module** | **100 — 71.4%** |
| M-05 | Distinct events consumed by portals | 102 |
| M-06 | **Of M-05, published by no module** | **69 — 67.6%** |
| M-07 | Module paths under one of the twelve declared API families | **38 — 3.9%** |
| M-08 | Distinct second path segments (de facto resource families) | 219 |
| M-09 | Paths declared by **more than one** module | 6 |
| M-10 | Events declared published by modules | 988 |
| M-11 | Of those, using a **module-code namespace** (convention B) | **242 across 37 namespaces** |
| M-12 | CON-03 §3.2 endpoints declared by no module | **12 of 22** |
| M-13 | CON-03 §3.3 webhooks published by no module | **8 of 11** |
| M-14 | External integrations · of which P0 | **47 · 12** |
| M-15 | Integrations with an ICD before this category | **0** |
| M-16 | P0 integrations with a **tested** fallback | **0 of 12** |
| M-17 | Error codes across `AP-005` §4.10 + `AP-006` | **90 in 12 domains** |
| M-18 | Machine-readable contract files before this category | **0** |

> **The finding that reframed the category.** Audit `AP-01` (critical) found **21** event names
> consumed and unregistered, by comparing three files. Measured across all twelve portals, the
> consumer-side gap is **69** — and it contains all three of `AP-01`'s safety-critical events.
> `AR-009` measured the producer side at 988 declared against 64 registered.
>
> **Both halves of the contract were broken, in opposite directions, and neither side knew.** Each
> side was authored correctly and independently; nobody ran the join. That is why `IN-002` and
> `IN-003` are **generated registries with CI reconciliation**, not documents, and why `IN-008`'s
> `CT-07` fails a consumer's build when no provider satisfies its pact.

---

## The three unmade Wave 1 decisions

`AUDIT-016` recorded three open platform decisions, each blocking work.

| Decision | Before | After |
|---|---|---|
| **Webhook signature scheme** | Nothing anywhere in 621 files | **`IN-006` §4** — algorithm, three headers, signed-content construction, 300 s replay window, multi-signature rotation, constant-time comparison. **Awaiting CTO + Security Lead** |
| **Scope vocabulary** | *"Not one scope name appears anywhere in the repository"* | **`IN-005` §5** — 58 named scopes, ratified form, eight grant rules. **Awaiting Design Authority** |
| **Error envelope** | `API-04` vs RFC 9457 unresolved | **Ruled.** `IN-002-D-03` embeds `API-04`'s four fields as RFC 9457 extension members, preserving all 90 codes and their `UI-004` and Bengali bindings |

**Every integration built before the first two are settled is rework**, and `FF-54` enforces it:
no contract may be published and no credential issued while any operation carries
`x-scope-status: proposed`.

---

## The event problem — closed jointly, not alone

`AP-01`'s three safety-critical events, after three independent measurements:

| Event | Disposition |
|---|---|
| **`warranty_claim.evidence_incomplete`** | **Still published by no module.** The suppression control `P08` `T-05` and gate `G4-02` depend on. Schema issued in `IN-003_artefacts/`; the emitter is `RE-02`, W1 |
| **`recall.execution_updated`** | **Still published by no module.** Product safety, `P08` `FR-POR-254`. `RE-02`, W1 |
| **`credit_note.issued`** | **Not missing — renamed.** `ar.credit_note_issued` is declared and published by M53. `AP-01` listed it as "genuinely missing" and listed it twice. **Corrected as `IN-A-10`** |

`AP-01` closes when `IN-003` `RE-02`, `RE-03` and `RE-04` complete — **`AR-009` and `IN-003`
together, neither alone.**

---

## What "done" looks like for this category

| # | Criterion | Position at issue |
|---|---|---|
| 1 | Machine-readable OpenAPI files exist per API and generate clients, mocks and contract tests | **35 of 1,187 operations (2.9%)** — the standard, the toolchain requirement and four contracts |
| 2 | Every event has a versioned schema, a named producer, ≥1 declared consumer, and stated ordering and delivery guarantees | The nineteen-field registration standard and 2 of 988 schemas |
| 3 | Every external system has a signed ICD, not a table row | **14 of 47 issued, all at `Draft`** — none `Agreed` with a counterparty |
| 4 | Contract tests run in CI between all 67 modules and all 12 portals | **~800 pairs specified; 0 running** |

**None of the four is complete, and none was ever going to be completed by a document.** What the
category delivers is the standard, the measurement, the rulings, the first artefacts and a costed,
sequenced plan — plus the honest statement of how far that is from done.

---

## Blocking dependencies this category surfaced and cannot resolve

| # | Blocker | Owner | Consequence |
|---|---|---|---|
| 1 | **Scope vocabulary unratified** | Design Authority + Security Lead | `FF-54` blocks every contract publication and every credential |
| 2 | **Signature scheme unratified** | **CTO + Security Lead** | The CON-03 portal accepts unverified POSTs from W1, or the first delivery fails |
| 3 | **A second card acquirer, or `NFR-048` restated** | **CTO + CFO** | `INT-003` is the only card acquirer. `G3-03` requires cards live at W3. **A procurement decision** |
| 4 | **Which bank sponsors BEFTN** | CFO + Treasury | **`CD-100` cannot be specified.** The counterparty is the bank, not Bangladesh Bank |
| 5 | **Three courier `AP-012` rows + processor contracts** | Legal Counsel | **Blocks W3 pick-and-drop**, in the wave `G3-07` requires unbroken custody |
| 6 | **`SANDBOX` provisioned** | Platform Engineering | None of `TS-001` §4.7's six environments exists either |
| 7 | **`IN-002` + `IN-003` resourced at 193–675 PW** | Programme Director | Against `GV-007`'s 264–528 PW for **all 127 remaining documents** |
| 8 | **`DA-001` ledger schema** | `DA-001` owner | `IN-007` §10's posting rules depend on it |
| 9 | **Role register gaps** — R39–R46 unregistered, R60 duplicates R32, R54/R57 undefined | CTO / `SC-004` | The scope-subset rule (`IN-005` §5.6) is **unverifiable for at least eight roles** |

---

## Dependencies

| Direction | Category | Relationship |
|---|---|---|
| Upstream | `02_Architecture` | `AR-001` §7.1 interface view (**corrected by `IN-001-D-01`**), `AR-008` contexts and aggregates, `AR-009` messaging design |
| Upstream | `03_Data` | `DA-002` field definitions and PII classification; `DA-001` ledger schema |
| Upstream | `00_Governance` | `GV-002` — the Design Authority that must ratify two blocking decisions |
| Downstream | `06_Experience` | Portal and app teams cannot start without `IN-002`; `UX-006` offline UX consumes `AR-010` and `IN-002` |
| Downstream | `05_Security` | `SC-002`'s attack surface **is** this contract set; `SC-004` owns the role gaps `IN-005` §5.6 depends on |
| Downstream | `08_Quality` | `QA-005` contract-test layer; `IN-008` is its integration slice |
| Downstream | `10_Infrastructure` | `PE-001` Z6 egress, `PE-005` broker and `SANDBOX` provisioning |
| Downstream | `11_Service_Operations` | Every ICD §11 fallback is a runbook input; `OP-014` |

---

## Audience and change frequency

| Attribute | Value |
|---|---|
| Primary audience | Integration engineers, portal/app developers, partner developers |
| Change frequency | **High** — versioned and deprecation-controlled under `IN-005` |
| Standards basis | OpenAPI 3.1 · AsyncAPI 3.0 · JSON Schema 2020-12 · RFC 9457 · `draft-ietf-oauth-v2-1-15` · CloudEvents 1.0 · Standard Webhooks · PCI DSS v4.0 · ISO/IEC/IEEE 29119 |

> **Two version-currency positions are recorded rather than assumed.** OpenAPI **3.2.0** is the
> current stable release; the estate authors to **3.1.0** because the register row, `AS-07` and three
> published documents name 3.1, and moves at the W2 gate (`IN-001-D-08`). **OAuth 2.1 is an IETF
> Internet-Draft, not an RFC** — its mandated practices are conformed to, and it is cited as a draft.

---

## Existing material this category built from

`1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03` (all 8 sections) ·
all 67 module files §12 · all 12 portal files §12 ·
`project_content/15_Integration_and_Developer_Content/AP-001…012` ·
`primary-doc/…Technology_Stack_Specification.md` §12.2 ·
`project_content/_AUDIT/AUDIT-016`

---

*Category 04 · `IN` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
