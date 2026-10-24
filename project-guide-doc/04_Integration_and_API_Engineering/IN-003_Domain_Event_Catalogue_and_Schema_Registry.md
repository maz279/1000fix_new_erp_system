---
id: IN-003
title: Domain Event Catalogue & Schema Registry
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
  AsyncAPI 3.0 · JSON Schema 2020-12 · CloudEvents 1.0 (external mapping) ·
  Confluent-style schema-compatibility semantics (BACKWARD) ·
  Enterprise Integration Patterns · ISO/IEC/IEEE 42010:2022 process viewpoint (via AR-001)
traces_to: >
  PGD-000 IN-003 · AR-009 §9, §10 (RM-05) · 05-03 §4 · M28 FR-IPF-032, -033 ·
  audit AP-01 (critical) · AP-003 · IN-001 §11 · NFR-043 · TR-12 · finding PGD-A3-15
depends_on: AR-009 · AR-008 (aggregate names) · IN-001 · ADR-017 (unratified)
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 17:25 (+06)
artefacts: ./IN-003_artefacts/
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# IN-003 — Domain Event Catalogue & Schema Registry

### Category 04 · Code `IN` · AsyncAPI 3.0 · JSON Schema 2020-12 · CloudEvents 1.0

---

> **Three measurements, three different questions, and only one of them had ever been asked.**
>
> | # | Question | Measured | Instant |
> |---|---|---:|---|
> | 1 | How many events do the 67 modules **declare they publish**? | **988** | `AR-009`, 02:05 (+06) — reconfirmed here |
> | 2 | How many are **registered** in `05-03` §4.2? | **64** (6.5%) | `AR-009` |
> | 3 | **How many events do the 12 portals consume that no module publishes?** | **69 of 102 — 67.6%** | **This document, 17:25 (+06)** |
>
> Audit `AP-01` (critical) asked question 3 across **three files** and found 21. Asked across **all
> twelve portal specifications**, the answer is **69** — and it includes every one of `AP-01`'s
> three safety-critical events, `payment.received` consumed by four portals, and the entire
> eight-event marketplace surface P07 is built on.
>
> `AR-009` measured the **producer** side and ruled the mechanism. This document measures the
> **consumer** side and builds the registry. Neither closes `AP-01` alone; together they do.

---

## 1. Purpose

`AR-009` designed the event mechanism — taxonomy, envelope, outbox, delivery semantics, replay,
schema evolution — and ruled that a 988-event catalogue **cannot be maintained by hand** and must be
generated from a registry (`D-A9-02`). It then delegated the registry itself to this document, as
its `RM-05`: *"Build the registry (`IN-003`) with generated catalogue; register all 988."*

This document is that registry. It specifies **what a registration is**, the schema standard each
registration carries, the reconciliation the registry must run on day one, the generated artefacts
it emits (AsyncAPI documents, JSON Schemas, the developer-portal catalogue), the governance that
keeps it true, and the measured remediation backlog — on **both** sides of the contract.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The **registration record** — every field, and why each is required |
| 2 | The **payload schema standard** (JSON Schema 2020-12) and its typing rules |
| 3 | **AsyncAPI 3.0** as the generated channel contract, and what it is and is not |
| 4 | The **CloudEvents 1.0 mapping** `AR-009` §2.1 promised external consumers |
| 5 | Compatibility semantics, versioning, dual-publish and retirement |
| 6 | **The consumer-side reconciliation** — 102 portal-consumed events measured against 988 |
| 7 | The three dispositions: rename · project · register — one per event, recorded |
| 8 | Replay-class and retention-class declaration, and their enforcement |
| 9 | Registry operation: who registers, when, what CI enforces |
| 10 | The **generated catalogue** and its relationship to `05-03` §4.2 and `AP-003` |
| 11 | The measured registration backlog, its sequencing and its effort |
| 12 | CI gates `FF-59`…`FF-68` |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Bus mechanism, outbox, relay, topology | `AR-009` §5, §6 | Ruled there. This document registers what travels, not how |
| Naming convention (ADR-017) | `AR-009` §3.2 | Ruled there. This document **enforces** it at registration |
| Envelope field semantics | `AR-009` §4 | Ruled there; carried into every schema |
| Synchronous API contracts | `IN-002` | OpenAPI, not AsyncAPI |
| Webhook **delivery** of external events | `IN-006` | The `external` channel's transport |
| Field-level business meaning | `DA-002` | A schema says the shape; `DA-002` says the meaning |
| Notification content and channel selection | `NT-*`, M27 | A notification is a **command**, never an event (`AR-009` E4) |
| Broker retention configuration | `PE-005` | This document declares retention classes; `PE` configures them |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| Every module developer | §3 is what they must fill in before their emitting code merges |
| Portal and app developers | §7's reconciliation tells them which of the events they consume actually exist |
| **`IN-006` author** | §5's `external` channel and CloudEvents mapping are what a partner receives |
| Platform engineers | §8's registry operation and §10's gates |
| QA lead | §6's compatibility rules and §8.3's replay classes are directly testable |
| Content Lead | §9.3 — `AP-003`'s descriptions must be re-checked against the generated catalogue |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Concept | How this document conforms | Departure and rationale |
|---|---|---|---|
| **AsyncAPI 3.0** | Channels, operations, messages, servers | §5 — one AsyncAPI document per bounded context, **generated** from the registry | **Version note:** AsyncAPI **3.1.0** (July 2026) is current. 3.1 is additive over 3.0; the category standards basis names 3.0 and the estate moves at the W2 gate with OAS 3.2 (`IN-001` §2.4a). Verified 2026-08-18 |
| **JSON Schema 2020-12** | Payload schemas | §4; the same dialect `IN-002` uses, so a type is defined once for both surfaces | None |
| **CloudEvents 1.0** | External event envelope | §5.4 — the mapping `AR-009` §2.1 promised, for external consumers only | **The internal envelope stays as `AR-009` §4 defines it.** Renaming `event_id`→`id`, `event_type`→`type`, `occurred_at`→`time` would invalidate `05-03` §4.1 and Tech Stack §12.2.6 for no functional gain |
| **Schema-compatibility semantics** (Confluent-style `BACKWARD`) | Evolution | §6.1's table is `BACKWARD` compatibility stated field by field | Named so a vendor recognises it |
| **Enterprise Integration Patterns** | Message store, idempotent receiver, dead letter, claim check | Inherited from `AR-009` §2.1 | None |

### 2.2 Source material and extraction

| Source | Contribution |
|---|---|
| All 67 module `§12.3` tables | **988 declared published events** — reconfirmed |
| All 67 module `§12.1` tables | 34 declared consumed events |
| **All 12 portal `§12.3` tables** | **102 consumed events — the measurement this document contributes** |
| `05-03` §4.1, §4.2, §4.3 | Envelope, the 64-event curated subset, consumer rules |
| `05-03` §3.3 | The 11 CON-03 portal webhooks — **8 published by no module** (`IN-001` §9.2) |
| `AR-009` §3, §4, §7, §8, §9, §10 | Naming, envelope, consumer contract, evolution, governance, remediation |
| `M28` §5.3, §8.1, §12.5 | `FR-IPF-032` living catalogue, event lifecycle, the schema/catalogue/subscription endpoints |
| `AP-003` | **104 distinct event names described** for the developer portal, written against the 64-event inventory |
| `AUDIT-016` `AP-01` | The 21-name finding, its three-class taxonomy and its three safety-critical events |

**Reproducible extraction**, run at **2026-08-18 17:25 (+06)**:

```bash
# 1. Published events — first column of every module §12.3 table            → 988
for f in $(find 03_Modules -name 'M[0-9]*.md'); do
  awk 'BEGIN{p=0} /^### 12\.3/{p=1;next} /^### 12\.4/{p=0} /^## /{p=0} p' "$f" \
    | grep -oE '^\| `[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*`' | sed 's/^| //;s/`//g'
done | sort -u > ev_pub.txt

# 2. Portal-CONSUMED events — every P*.md §12.3 table                       → 102
for f in 03_Modules/K_Platform_and_Technology/P*.md; do
  awk 'BEGIN{x=0} /^### 12\.3/{x=1;next} /^### 12\.4/{x=0} x' "$f" \
    | grep -oE '`[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*`' | sed 's/`//g'
done | sort -u > ev_portal.txt

comm -23 ev_portal.txt ev_pub.txt | wc -l          # → 69  UNPUBLISHED
cut -d. -f1 ev_pub.txt | sort -u | wc -l           # → 243 namespaces
```

### 2.3 Audit findings this document closes or contributes to

| Finding | Source | Disposition |
|---|---|---|
| **`AP-01` (critical)** — 21 events consumed and unregistered; 14 "genuinely missing" | `AUDIT-016` | **Closed jointly with `AR-009`.** §7 measures the true consumer-side gap at **69**, disposition each, and §11 schedules registration. `AP-01`'s central "principal vs complete" question was ruled by `AR-009` `D-A9-01` |
| `PGD-A3-14` — `credit_note.issued` appears twice in `AP-01`'s list of 14, so 14 distinct names is **13** | `PGD-AUDIT-003` | **Confirmed by re-extraction.** `AP-01`'s class-3 list contains 13 distinct names |
| **`PGD-A3-15`** — `IN-003` carries 988 registrations and the effort is in no plan | `PGD-AUDIT-003` | **Quantified.** §11.4: **99–247 person-weeks** |
| `AR-009` `RM-05` | `AR-009` §10.6 | This document is `RM-05` |
| `AR-009` `RM-07` — reconcile every §12.3 consumer against the consumer's §12.1 | `AR-009` §10.6 | §7.5 runs it and reports **the reciprocity failure rate** |
| `AR-009` Q-06 — should `platform.` (E3) events be exempt from registration? | `AR-009` §11 | **Ruled `IN-003-D-06`: registered, but in a separate namespace view** |
| `TR-12` — outbox applied unevenly | Tech Stack §23 | `FF-04` (`AR-009`) plus `FF-60` here: an emitted event with no registration fails the build |
| `M28` `FR-IPF-032` — the living catalogue | `M28` §5.3 | §9 is its specification |
| `AP-003` `O-06` | `AP-003` | §9.3 schedules the re-check against the generated catalogue |

---

## 3. The Registration Record

### 3.1 What a registration is

> **A registration is a row in a registry, declared in code at the emission point, validated at
> merge, and rendered into every downstream artefact.** It is not a paragraph in a document.

`AR-009` `G-02` names six fields. Experience across the estate's identifier collisions
(`H-03`, `H2-04`, `AP-02`, `PGD-A1-01`) argues for more. **Nineteen fields, each with a stated
reason:**

| # | Field | Required | Why it is required |
|---|---|:--:|---|
| 1 | `event_type` | ✔ | The name. `<aggregate>.<past_tense_verb>`, ADR-017 convention A |
| 2 | `schema_version` | ✔ | `MAJOR.MINOR`. Evolution (`AR-009` §8) |
| 3 | `kind` | ✔ | `E1` domain · `E2` integration · `E3` platform. **`E4` notification is not an event and cannot be registered** |
| 4 | `aggregate` | ✔ | One of the 22 `AR-008` §4.2 roots, or a named interior entity. **The partition key's type** |
| 5 | `producer_module` | ✔ | **Exactly one.** Two producers for one event name is the defect `IN-001` §11.2 found on the API side |
| 6 | `consumers[]` | ✔, `minItems: 1` | `AR-009` `G-03`: **an event with no declared consumer is a defect** — either a consumer is missing or the event should not exist |
| 7 | `payload_schema` | ✔ | JSON Schema 2020-12 (§4) |
| 8 | `ordering_guarantee` | ✔ | `per_aggregate_instance` or `none`. **Never global** (`AR-009` §4.2) |
| 9 | `replay_class` | ✔ | `R1` · `R2` · `R3`. §8.3. **This is what stops a routine replay re-sending 40,000 SMS** |
| 10 | `retention_class` | ✔ | §8.4. Statutory in three of five cases |
| 11 | `channel` | ✔ | `domain` · `external` · `platform` (`AR-009` §6.3) |
| 12 | `pii_classification` | ✔ | `none` · `personal` · `sensitive` · `residency_restricted`. **`residency_restricted` in a payload is forbidden** (`AR-009` P-03) |
| 13 | `owning_context` | ✔ | One of the eleven (`AR-008` §5) — organises the generated AsyncAPI documents |
| 14 | `wave` | ✔ | When it first exists. Drives §11's sequencing |
| 15 | `emits_from[]` | ✔ for E1 | The **state transitions** that emit it. `FF-04` asserts the set matches the SDD §9 transition table |
| 16 | `external_shape` | conditional | Required when `kind = E2`: the boundary-shaped schema, which is **not** the internal one |
| 17 | `deprecated_at`, `replaced_by`, `sunset_at` | conditional | §6.3 dual-publish |
| 18 | `registered_by`, `registered_at` | ✔ | Provenance. Auto-stamped |
| 19 | `source_ref` | ✔ | The module `§12.3` row or SDD section this registration derives from — **so a registration can be traced back to the specification that asked for it** |

### 3.2 Fields deliberately not carried

| Not a field | Why |
|---|---|
| A prose description | It belongs in `AP-003`, the content pack, generated **from** the registry. Two descriptions of one event is `AP-006` `EP-06`'s defect class |
| A Bengali name | An event name is machine-facing and never shown to a user. The **notification** a user sees is `NT-*` content |
| A "criticality" rating | Unowned adjectives decay. Consequence is carried by `replay_class` and `retention_class`, both of which have mechanical effects |
| A consumer's SLA | Latency is a platform property (`NFR-043`, 5 s p95), not a per-event negotiation |

### 3.3 Where the registration lives

| Layer | Artefact | Maintained by | Generated? |
|---|---|---|---|
| **Source of truth** | A declaration adjacent to the emitting code | The module developer, in the same commit as the emission | ✘ |
| **Registry** | `fix_event_registration` in the platform database, served by `/api/v1/platform/events/schemas` | CI, on merge | ✔ |
| **AsyncAPI documents** | `IN-003_artefacts/<context>/asyncapi.yaml` — eleven | CI | ✔ |
| **JSON Schemas** | `IN-003_artefacts/schemas/<event_type>.v<major>.json` | CI | ✔ |
| **Developer-portal catalogue** | `M28` `FR-IPF-032`'s living catalogue | CI | ✔ |
| **`AP-003` descriptions** | Content pack | Content Lead, **against the generated catalogue** | ✘ |
| **`05-03` §4.2** | **Curated cross-cutting subset, explicitly partial** | Enterprise Architecture | ✘ — `AR-009` `D-A9-01` |

---

## 4. The Payload Schema Standard

### 4.1 Structure

Every payload schema is a JSON Schema 2020-12 document describing **only the `payload` object**.
The envelope is fixed by `AR-009` §4 and is validated separately, once, for every event.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://schemas.1000fix.example/events/service_order.delivered/1.0.json",
  "title": "service_order.delivered payload",
  "type": "object",
  "additionalProperties": false,
  "required": ["service_order_id", "delivered_at", "billable_summary"],
  "properties": { }
}
```

### 4.2 Typing rules

These deliberately mirror `IN-002` §4.6 and §5, so a concept has **one** representation across both
the synchronous and asynchronous surfaces.

| # | Rule | Basis |
|---|---|---|
| **SC-01** | `additionalProperties: false`. A payload is a closed contract; an unexpected field is a producer defect | Strictness at the producer, tolerance at the consumer |
| **SC-02** | **Money is `{amount: string-decimal, currency: ISO-4217}`** — never a float | AS-10, `AR-009` P-06 |
| **SC-03** | Time is RFC 3339 **UTC** with offset. Bangladesh Standard Time is presentation | `IN-001` `AC-05` |
| **SC-04** | Property names are `snake_case`, matching `DA-002`'s technical name | `IN-002` `BD-04` |
| **SC-05** | **Facts, not commands.** `service_order.completed` carries what was done, never "now raise an invoice" | `AR-009` P-01 |
| **SC-06** | **Enough for a consumer to act without a call-back.** An event that forces every consumer to fetch the record has moved the coupling, not removed it | `AR-009` P-02 |
| **SC-07** | **No residency-classified value, ever.** The payload carries the resident key; the consumer reads through CD-233 | `AR-009` P-03, `AR-001` `LB-08`, `NFR-086` |
| **SC-08** | **No personal data beyond what *every* consumer needs.** Where one consumer needs more, it reads through an API | `AR-009` P-04, `IP-10` |
| **SC-09** | Binaries use the **claim check** — an `Attachment` reference, never bytes | `AR-009` P-05 |
| **SC-10** | Cross-aggregate references carry an **identifier and type**, never a nested representation | `IN-002` `Reference`; prevents an event becoming a snapshot of half the database |
| **SC-11** | Enumerations are **open** by default (`BACKWARD` compatibility permits adding a value); a closed enumeration is declared and justified | §6.1 |
| **SC-12** | Every property carries `description`. A schema without descriptions generates an unusable catalogue | `AP-002` parity |

> **`SC-07` is the rule most likely to be broken by accident, and the estate has already been told
> so.** `AR-009` P-03: a developer adding `nid_number` to a `party.updated` payload for a consumer's
> convenience puts residency-classified data on the bus, in the broker's log, in the dead-letter
> queue and in every consumer's inbox. `FF-09` checks it; `FF-64` here checks it **at registration**,
> which is earlier and cheaper.

### 4.3 The tension `AR-009` §8.4 recorded, and how the registry resolves it

`NFR-095` requires processing records for **five years**; PDPA erasure (`NFR-093`) requires personal
data removed on request. **An event payload containing personal data is subject to erasure; the
processing record is not.**

| Position | Mechanism |
|---|---|
| Keep personal data **out of payloads** (`SC-07`, `SC-08`) | The event stream then carries the *fact* of processing without the *data* processed, and erasure never has to reach the event store |
| Where a payload **must** carry personal data | `pii_classification` is set, and the event is enrolled in the **CD-248 erasure saga** — which makes the event store one more place erasure must reach |
| The registry's role | `pii_classification` is a **required** field, so the erasure scope is a query, not an investigation |

> **This is why field 12 is required rather than optional.** `AR-009` Q-03 asks whether the event
> store falls within PDPA erasure scope; the honest answer is *"for exactly the events whose
> `pii_classification` is not `none`, and the registry is the only place that set can be enumerated."*
> Referred to `SC-003` and `DA-006` as `AR-009` did — but now answerable.

---

## 5. Generated Contracts

### 5.1 AsyncAPI 3.0 — one per bounded context

Eleven documents, mirroring `IN-002-D-01` exactly, at `IN-003_artefacts/<context>/asyncapi.yaml`.

| Element | Content |
|---|---|
| `servers` | The bus per wave: Redis Streams (W1–W5), Redpanda (W6+) — `AR-009` §6.1 |
| `channels` | The three from `AR-009` §6.3: `domain`, `external`, `platform` — plus `dlq.<channel>` documented, not subscribable |
| `operations` | `send` per producing module; `receive` per registered consumer |
| `messages` | One per `(event_type, schema_version)`; payload `$ref`s the JSON Schema |
| `components.messageTraits` | **The envelope, defined once** and applied to every message |
| `bindings` | Partition key = `aggregate.type` + `aggregate.id` (`AR-009` §4.2) |

### 5.2 What AsyncAPI is, and is not

| It is | It is not |
|---|---|
| A machine-readable description of channels, messages and who sends/receives | A schema registry — the registry is the source; AsyncAPI is an emitted view |
| A generator input for consumer scaffolding and documentation | A runtime component |
| The artefact a partner reads to build against the `external` channel | The internal contract — internal consumers read the registry directly |

### 5.3 Why not describe events in OpenAPI

Asked because it is the intuitive shortcut, and the answer matters:

| Concern | OpenAPI | AsyncAPI |
|---|---|---|
| Direction | Request/response | **Publish/subscribe — the actual topology** |
| Who initiates | The client | The producer |
| Multiple consumers of one message | Not expressible | First-class |
| Ordering and partitioning | No concept | Bindings |
| Modelling a webhook | 3.1 `webhooks` — a *callback*, not a channel | Native |

**Both are used, for different surfaces.** `IN-002` for the 1,187 synchronous operations; `IN-003`
for the 988 events. `IN-006` uses OpenAPI 3.1 `webhooks` for the *delivery* contract because that
genuinely is an HTTP request — the two do not overlap.

### 5.4 The CloudEvents 1.0 mapping

`AR-009` §2.1 recorded a departure from CloudEvents field names and promised: *"A CloudEvents
mapping is published in `IN-003` for external consumers."* Published here.

| CloudEvents 1.0 attribute | 1000FiX envelope | Notes |
|---|---|---|
| `id` | `event_id` | Required; the idempotency key |
| `source` | derived: `/1000fix/{company_id}/{operating_unit_id}/{producer_module}` | CloudEvents requires a URI-reference; the estate's envelope has no single equivalent, so it is **composed** |
| `type` | `event_type`, prefixed `com.1000fix.` | Reverse-DNS is the CloudEvents convention |
| `time` | `occurred_at` | RFC 3339 |
| `subject` | `aggregate.type + ":" + aggregate.id` | |
| `datacontenttype` | `application/json` | Constant |
| `dataschema` | the JSON Schema `$id` for `(event_type, schema_version)` | |
| `data` | `payload` | |
| *(extension)* `correlationid` | `correlation_id` | CloudEvents extension attribute names are lowercase, no separators |
| *(extension)* `causationid` | `causation_id` | |
| *(extension)* `schemaversion` | `schema_version` | |
| *(extension)* `companyid`, `operatingunitid` | `company_id`, `operating_unit_id` | |
| *(not mapped)* | `actor` | **Deliberately withheld from external consumers.** Which internal user caused an event is not a partner's business (`IP-10`) |

> **The mapping applies to the `external` channel only.** Internal consumers see the `AR-009` §4
> envelope unchanged. This is `kind = E2`'s whole purpose: a domain event **shaped for an external
> consumer, with fields removed at the boundary**, and `actor` is the field removed.

---

## 6. Evolution

### 6.1 Compatibility — field by field

`AR-009` §8.1 gives the rule. This states it as the CI check, in `BACKWARD` terms:

| Change | Within a `schema_version`? | Reason |
|---|:--:|---|
| Add an **optional** property | ✅ | Old consumers ignore it |
| Add a value to an **open** enumeration | ✅ | `SC-11`; consumers must have a default branch |
| Widen a numeric range or string length | ✅ | Old consumers still parse |
| Add a value to a **closed** enumeration | ❌ | A closed enum is a promise the set is finite |
| Remove a property | ❌ | |
| Rename a property | ❌ | Removal plus addition |
| Change a type | ❌ | |
| Make an optional property **required** | ❌ | |
| Narrow a constraint | ❌ | An old producer's valid payload becomes invalid |
| Change `additionalProperties` false → true | ✅ | Loosening |
| Change the **meaning** of a property without changing its shape | ❌ | **Undetectable by CI and the most dangerous change of all.** `AP-006` `CG-04` says the same about error codes |

> **The last row has no automated check, and that is the point of stating it.** `FF-65` cannot catch
> a semantic change; the **design review at the registration gate** is the only control, which is why
> §8.1 makes registration a reviewed act rather than an automatic one.

### 6.2 Version numbering

| Component | Increments when |
|---|---|
| `MINOR` | An additive, `BACKWARD`-compatible change |
| `MAJOR` | Anything else — **and it is a new message requiring dual-publish** |

The envelope carries `schema_version` as `MAJOR.MINOR`. Consumers select on `MAJOR`.

### 6.3 Dual-publish and retirement

`AR-009` §8.3's five steps, with the registry's role at each:

| Step | Action | Registry |
|---|---|---|
| 1 | Producer publishes **both** versions to the same channel | Both registrations active; the old marked `deprecated_at` |
| 2 | Consumers migrate, each confirming | **Per-consumer confirmation is a registry field** — this is what makes step 3 a query |
| 3 | When every registered consumer is on the new version, the old is deprecated | Registry computes it; no human judgement |
| 4 | **Minimum six months' notice** before removal (API-02 parity) | `sunset_at` ≥ `deprecated_at` + 6 months. `FF-66` |
| 5 | Removal recorded with the date and the confirming consumers | Immutable history; the registration is retired, never deleted (`CM-22`) |

> **Step 2 is why `consumers[]` is required with `minItems: 1`.** Without a registered consumer set,
> "every consumer has migrated" is unanswerable and the old version is retired on optimism.

### 6.4 A name is permanent

`AR-009` `N-06` and `G-05`. A rename is a **new event** with a dual-publish period — which is why
the ~242 convention-B renames must happen in W1, while no consumer exists and the change is a text
edit. §11.2.

---

## 7. The Consumer-Side Reconciliation

### 7.1 What was measured

Every event name in all twelve portal `§12.3` tables, against the 988 declared published events.
**2026-08-18 17:25 (+06).**

| # | Measure | Count |
|---|---|---:|
| E-01 | Distinct events **declared published** by the 67 modules | **988** |
| E-02 | Distinct events **consumed** by the 12 portals | **102** |
| E-03 | Of E-02, published by **some** module | **33 (32.4%)** |
| E-04 | **Of E-02, published by NO module** | **69 (67.6%)** |
| E-05 | Distinct events consumed in module `§12.1` tables | 34 |
| E-06 | Events registered in `05-03` §4.2 | 64 |
| E-07 | Distinct **namespaces** across the 988 | **243** |
| E-08 | Namespaces that are **module codes** (convention B) | **37** |
| E-09 | **Events using a convention-B namespace** | **242** |
| E-10 | Namespaces holding exactly **one** event | **101** |
| E-11 | CON-03 portal webhooks (`05-03` §3.3) published by no module | **8 of 11** |
| E-12 | Event names described in `AP-003` | 104 |

> **E-09 = 242, precisely.** `AR-009` §3.3 estimated *"~245 events across ~40 namespaces"*; the
> exact figures are **242 events across 37 namespaces**. Recorded as a refinement, not a correction —
> `AR-009` labelled its figures approximate and they were.

### 7.2 The 69, by consuming portal

| Portal | Events consumed | Unpublished | Share |
|---|---:|---:|---:|
| P07 Marketplace Seller | 14 | **13** | **93%** |
| P10 Contact Centre | 8 | **8** | **100%** |
| P12 Partner & Referral | 12 | 8 | 67% |
| P01 Customer | 13 | 9 | 69% |
| P11 Field Auditor | 8 | 6 | 75% |
| P04 Corporate B2B | 11 | 6 | 55% |
| P05 Vendor & Supplier | 13 | 6 | 46% |
| P08 Brand Partner | 9 | 6 | 67% |
| P02 Technician | 10 | 5 | 50% |
| P06 Analytics | 7 | 5 | 71% |
| P09 Logistics & Rider | 7 | 5 | 71% |
| P03 Admin Operations | 8 | 2 | 25% |

> **P10 Contact Centre consumes eight events and not one of them is published by any module.** It
> is a W4 portal, so there is time — but the entire real-time behaviour of the agent console
> (`interaction.routed`, `interaction.transferred`, `queue.sla_breached`, `complaint.reference_issued`,
> `cpaas.degraded`, `assist.suggestion_available`) currently rests on nothing.
>
> **P07 Marketplace is 13 of 14**, and eight of those are the `mp.*` namespace — the same surface
> whose fifteen API paths no module declares (`IN-001` §11.3). **The marketplace is specified on
> both sides by its consumer and on neither side by a producer.**

### 7.3 The three dispositions

Following `AP-01`'s taxonomy, because it is the right one. Every one of the 69 receives **exactly
one** disposition, recorded in the registry.

| Class | Meaning | Remedy | Cost |
|---|---|---|---|
| **D1 — Same fact, two names** | The fact is published under a different name | **Correct the consumer to the producer's name** — never the reverse (`AP-01` remediation instruction) | Free in W1 |
| **D2 — Coarse projection** | The consumer wants a rolled-up view of a finer set | **Decide, then document, the projection.** A projection is a legitimate design; an undocumented one is not | Small — a named projector |
| **D3 — Genuinely absent** | Nothing publishes this fact | **Register and build, or delete the consuming specification's claim** | Not free at any point |

#### 7.3.1 Automated triage, and its measured limits

A triage was run at **2026-08-18 17:25 (+06)** over the 69, matching each against the 988 on
namespace and verb stem:

| Triage bucket | Count |
|---|---:|
| Same-namespace rename detected — high-confidence **D1** | **5** |
| Projection-shaped — `.status_changed`, `.updated`, `_en_route` — **D2** candidate | **7** |
| Remainder | **57** |
| — of the remainder, carrying a **cross-namespace** verb candidate | 29 |
| — of the remainder, carrying **no candidate at all** | **28** |

> **The triage under-detects renames, and the check that proves it is worth stating.** Manual
> verification of a sample against the 988 found **five genuine renames the heuristic missed**,
> because a rename frequently changes the verb as well as the namespace:
>
> | Consumed as | Actually published as | Why the heuristic missed it |
> |---|---|---|
> | `sla.at_risk` | **`sla.warning`** | Same namespace, unrelated verb stem |
> | `estimate.issued` | **`estimate.created`**, `estimate.ready` | Same namespace, unrelated verb stem |
> | `payout.executed` | **`payout.instructed`** | Same namespace, unrelated verb stem |
> | `settlement.released` | **`settlement.payout_released`** | Verb is a superstring, not a prefix |
> | **`credit_note.issued`** | **`ar.credit_note_issued`** | A convention-B namespace absorbed the noun |
>
> **No clean disposition split is asserted here.** The triage narrows the work; it does not decide
> it. **Each of the 69 requires an adjudication recorded in the registry** (`RE-04`), and the
> buckets above are the starting point, not the answer. Publishing a tidy "14 / 6 / 49" would be a
> figure written from intent rather than counted — the defect `PG-M10` exists to prevent, and the
> one `AUDIT-016` `AP-18` caught inside an audit of the gate that exists to catch it.

**The published triage**, generated into
[`IN-003_artefacts/reconciliation/portal-consumed-unpublished.csv`](./IN-003_artefacts/reconciliation/portal-consumed-unpublished.csv)
at 2026-08-18 17:40 (+06) and counted from that file, not from this paragraph:

| Class | Count | Basis |
|---|---:|---|
| **D1** — rename | **12** | Verified against the 988 by inspection (§7.3.2) |
| **D2** — projection | **7** | Shape-detected: `.status_changed`, `.updated`, `_en_route` |
| **D3** — genuinely absent | **25** | **No candidate of any kind** in the 988 |
| **Unadjudicated** | **25** | A cross-namespace verb candidate exists; same-fact-or-not is a human call |
| **Total** | **69** | ✓ |

**Thirty-six of the sixty-nine are settled; twenty-five remain a judgement nobody has yet made**, and
that judgement is `RE-04`. The CSV carries one row per event with its consuming portals, its
candidate and a proposed owning module, so the adjudication is a worklist rather than a discovery
exercise.

#### 7.3.2 The D1 renames established to date

| Consumed as | Published as | Consuming portals | Status |
|---|---|---|---|
| `sla.at_risk` | `sla.warning` | P03, P04, P06, P09 | Confirmed — also an `AP-01` class-1 pair |
| `estimate.issued` | `estimate.created` | P01 | Confirmed — `AP-01` class-1 pair |
| `estimate.revised` | `estimate.created` (v2) | P01 | Confirmed |
| **`credit_note.issued`** | **`ar.credit_note_issued`** | P04 | **Confirmed — see `IN-A-10`** |
| `payout.executed` | `payout.instructed` | P12 | Confirmed |
| `settlement.released` | `settlement.payout_released` | P07 | Confirmed |
| `equipment.audit_variance_computed` | `equipment.audit_completed` | P11 | Heuristic-detected |
| `ewaste.batch_transferred` | `ewaste.batched` | P05 | Heuristic-detected |
| `settlement.completed` | `settlement.reconciled` | P07 | **Adjudication needed** — two candidates |
| `project.milestone_reached` | `project.milestone_accepted` / `.milestone_ready` | P04 | **Adjudication needed** — two candidates |
| `stock.consignment_reconciled` | `stock.consignment_consumed` | P08 | **Adjudication needed** — may be a distinct fact |
| `stock.count_variance_computed` | `stock.count_completed` | P11 | **Adjudication needed** — may be a distinct fact |

> **`IN-A-10` (medium) — a correction to `AP-01`.** `AP-01` listed `credit_note.issued` among the
> **fourteen "genuinely missing"** registrations, and listed it **twice** (which `PGD-A3-14`
> recorded). Extraction across the 988 finds **`ar.credit_note_issued` declared and published by
> M53**. It is neither missing nor duplicated: it is a **convention-B naming divergence**.
>
> `P04` `AC-10`'s SLA-remedy mechanism therefore **exists and is named wrongly** — a materially
> better position than `AP-01` reported, and one that `AR-009` `RM-03` resolves automatically. An
> audit that reports a closed gap as open damages trust as much as one that misses an open gap; the
> estate has said so before, at `PGD-A2-06`.

#### 7.3.3 The D2 projections, each needing a named projector

| Projection | The finer set it projects | Projector owned by | Consumers |
|---|---|---|---|
| `service_order.status_changed` | The 16 M01 `service_order.*` events | **M01** | P01, P04, P10, CON-03 |
| `service_order.updated` | Any M01 mutation | **M01** | P02 |
| `claim.status_changed` | M09 `warranty_claim.*` | **M09** | P01 |
| `lead.status_changed` | M07 / M35 `lead.*` | **M07** | P12 |
| `dispatch.technician_en_route` | `technician.dispatched` + `technician.location_updated` | **M02** | P01 |
| `incentive.updated` | M57 incentive events | **M57** | P02 |
| `policy.updated` | M60 policy events | **M60** | P07 |
| `consignment.status_changed` *(from `05-03` §3.3, not a portal `§12.3`)* | The 6 M03 `consignment.*` events | **M03** | CON-03 |

> A projection is a **legitimate design.** Forcing a web front end to understand sixteen order
> events is worse than publishing one rolled-up event, and `AP-01` said exactly this: *"A projection
> is a legitimate design; an undocumented one is not."* What is required is a **named projector**, a
> declared source set, and a registration like any other event — which is why §3.1 field 15
> (`emits_from[]`) is mandatory.
>
> **A projection is `R1` on replay** (idempotent, recomputable) and must never carry a side effect.

#### 7.3.4 The D3 population, by the module that would own it

Grouped by the module that must publish. The counts below span the **25 with no candidate** plus
those of the 25 unadjudicated that are most likely to resolve to D3 — so the table is a **worklist
upper bound**, not a settled figure. The CSV carries the authoritative per-event position.

| Owning module | Events | Examples |
|---|---:|---|
| **M12 Marketplace** | 8 | `mp.job_awarded`, `mp.job_broadcast`, `mp.bid_unsuccessful`, `mp.seller_approved`, `mp.seller_rejected`, `mp.dispute_opened`, `mp.dispute_resolved`, `mp.scorecard_published` |
| **M27 Contact Centre** | 6 | `interaction.routed`, `interaction.transferred`, `queue.sla_breached`, `complaint.reference_issued`, `cpaas.degraded`, `assist.suggestion_available` |
| **M40 Partner & Channel** | 6 | `allocation.changed`, `benefit_schedule.changed`, `deal_registration.decided`, `partner.declined`, `commission.calculated`, `campaign.performance_published` |
| **M23 Quality / M60 GRC** | 5 | `audit.assigned`, `audit.rescheduled`, `audit.checklist_version_published`, `capa.due_for_verification`, `capa.closed` |
| **M03 Logistics** | 4 | `consignment.assigned`, `consignment.booked`, `consignment.reassigned`, `consignment.rescheduled` |
| **M20 Receivables** | 3 | **`payment.received`**, `invoice.blocked`, `invoice.issued` |
| **M02 Dispatch** | 2 | `dispatch.job_assigned`, `dispatch.job_reassigned` |
| **M09 Warranty** | 2 | **`claim.evidence_incomplete`**, **`recall.execution_updated`** |
| **M10 Loyalty** | 2 | `loyalty.points_expiring`, `loyalty.tier_changed` |
| **M22 Competency** | 2 | `certification.expiring`, `certification.expired` |
| **M62 Data Platform** | 2 | `dataset.refreshed`, `dataset.quality_failed` |
| M08, M16, M18, M26, M28, M29, M67 | ~7 | `entitlement.threshold_crossed`, `rfq.issued`, `purchase_order.issued`, `model.published`, `integration.degraded`, `user.scope_changed`, `project.milestone_reached` |

> **`payment.received` is the row to look at twice.** It is consumed by **P01, P08, P09 and P10**
> and by the CON-03 portal contract (`05-03` §3.3), and **no module publishes it.** The W1 portal
> contract carries a money path with no producer — the asynchronous half of exactly the gap
> `IN-001` §9.2 found on the synchronous side, where `/api/v1/payments/confirm` is likewise declared
> by no module.
>
> **M12 owes eight events, M27 owes six and M40 owes six**, and not one of them appears in those
> modules' `§12.3` tables. That is **module functionality nobody has costed**, not a documentation
> gap — which is why `RE-08` is separated from `RE-04` in §11.2 and priced separately in §11.4.

### 7.4 The three that are controls, not conveniences

`AP-01` identified three. `AR-009` §10.5 confirmed all three still unpublished. **This measurement
confirms it a third time, and adds the consumer count:**

| Event | Class | What depends on it | Consumers |
|---|---|---|---|
| **`claim.evidence_incomplete`** *(qualified: `warranty_claim.evidence_incomplete` per `AR-008` §3)* | **D3** | **A control.** `P08` `T-05` suppresses claim submission when the evidence pack is incomplete. `G4-02`'s 90% first-submission approval target rests on the suppression | P08 |
| **`recall.execution_updated`** | **D3** | **Product safety.** `P08` `FR-POR-254` publishes recall execution status to the brand | P08 |
| **`credit_note.issued`** | **D1 — renamed, not missing** | The SLA remedy. `P04` `AC-10` requires service credits published without prompting | P04 |

> **Two of three are genuinely absent after three independent measurements.** `AR-009` §10.5:
> *"An architectural control that is documented and unpublished is not a control."* They are **W1
> registration items ahead of the bulk remediation**, and `IN-002_artefacts/commercial/openapi.yaml`
> already specifies the `422 rule.evidence_incomplete` the first must produce.

### 7.5 Reciprocity — `AR-009` `RM-07`

`AR-009` `G-03`/`G-04` require that every event names consumers and every consumed event has a
producer. `AR-009` §9.3 observed: *"every one of the 988 names consumers in the §12.3 table — the
specifications are disciplined about this. What is not yet verified is whether the named consumer's
§12.1 reciprocates."*

**Verified here.** Module `§12.1` tables declare **34** consumed events against **988** published.

| Reading | Consequence |
|---|---|
| The `§12.1` tables are **narrative, not exhaustive** | Almost certainly true — they list *sources of data*, not every event subscription |
| Therefore reciprocity **cannot be checked from the specifications** | The consumer set exists only in the producer's `§12.3` "Principal Consumers" column, which is one side of a two-sided contract |
| **The registry is the only place reciprocity becomes checkable** | `FF-61`: a consumer declared by a producer must itself register a subscription, or the producer's claim is removed |

> **`IN-A-11` (medium).** `AR-009` `RM-07` as written — *"reconcile every §12.3 consumer against the
> consumer's §12.1"* — **cannot be executed**, because `§12.1` is not a subscription register and
> was never intended as one. It is superseded by `FF-61`, which checks the same property against the
> registry instead. Recorded rather than silently reinterpreted.

---

## 8. Registry Operation

### 8.1 Registration is a reviewed act

| # | Rule | Basis |
|---|---|---|
| **RG-01** | An event is registered **before** the code that emits it merges | `AR-009` `G-01` |
| **RG-02** | Registration requires all nineteen §3.1 fields. A partial registration is rejected | |
| **RG-03** | **A new `event_type` requires a design review**, because §6.1's last row has no automated check | §6.1 |
| **RG-04** | A `MINOR` bump is automatic if CI's compatibility check passes | §6.1 |
| **RG-05** | A `MAJOR` bump requires a dual-publish plan naming every registered consumer | §6.3 |
| **RG-06** | **An event with no declared consumer cannot be registered** | `AR-009` `G-03` |
| **RG-07** | **A consumed event with no registered producer fails CI** | `AR-009` `G-04`, `FF-60` |
| **RG-08** | The catalogue is regenerated and **diffed at every wave gate**. An undeclared change is a gate failure | `AR-009` `G-06` |
| **RG-09** | A registration is **retired, never deleted** | `GV-011` `CM-22` |

### 8.2 Who may register

| Actor | May |
|---|---|
| Module developer | Register an event their module produces; declare a subscription their module consumes |
| Integration Architect | Register `E2` external shapes; approve `MAJOR` bumps |
| Platform Engineering | Register `E3` `platform.` events |
| **Nobody** | Register an `E4` notification. **It is not an event** (`AR-009` §3.1) |

### 8.3 Replay class — declared, and enforced

`AR-009` §7.2 defines three classes and requires each consumer to declare one. The registry is where
that declaration lives, and the replay service reads it.

| Class | Behaviour on replay | Examples | Replay service |
|---|---|---|---|
| **R1** Idempotent projection | Safe — recompute from scratch | Warehouse loads, read models, search index, KPI aggregates | Proceeds |
| **R2** Guarded side effect | Safe **only** with an already-done check | Invoice creation | Proceeds; the guard is the consumer's |
| **R3** External side effect | **Refused without an explicit, named, logged operator override** | SMS/WhatsApp send, payment execution, brand claim submission, BEFTN file generation | **Refuses** |

> **`R3` refusal is implemented, not merely documented.** `IN-002_artefacts/platform/openapi.yaml`
> `replayDeadLetter` requires `r3_override: true` plus a reason, records the operator, and publishes
> `platform.event_replayed`. This is what stops a routine replay from re-sending 40,000 SMS messages.

### 8.4 Retention class

`AR-009` §8.4, carried as a required registry field so retention is a query rather than a policy
document:

| Class | Retention | Reason |
|---|---|---|
| `financial_7y` | **7 years** | Statutory — `invoice.*`, `payment.*`, `journal_entry.*` |
| `personal_5y` | **5 years minimum** | `NFR-095` processing records — `party.*`, consent, DSR |
| `evidence` | The legal evidence period | Custody and destruction — `data_case.*`, `consignment.*`, `wipe.*` |
| `operational_30d` | 30 days | The replay window |
| `platform_30d` | 30 days | E3 diagnostics |

### 8.5 The `platform.` namespace ruling

`AR-009` Q-06 asked whether `E3` platform events should be exempt from registration, to keep the
catalogue navigable.

> **Ruling `IN-003-D-06`. `platform.` events are registered, and the catalogue defaults to a
> `domain` + `external` view.** Navigability is a *rendering* problem, not a *registration* problem.
> Exempting them would mean `platform.direct_access_violation` — an architecture-compliance signal —
> has no schema and no declared consumer, which is precisely the condition `G-03` exists to prevent.
> M28 declares **16** `platform.*` events; they are a small share of 988 and their absence from the
> registry would cost more than their presence in a filtered view.

---

## 9. The Generated Catalogue

### 9.1 What it is

`M28` `FR-IPF-032`'s living catalogue, served at `/api/v1/platform/events/catalogue`, generated
from the registry on every merge.

| Property | Position |
|---|---|
| Source | The registry. Always |
| Freshness | Regenerated on merge; diffed at each wave gate (`RG-08`) |
| Filters | By aggregate, producer, context, channel, wave, **and `unconsumed=true`** |
| **`unconsumed=true`** | Deliberately surfaces the `G-03` defect class rather than hiding it |
| Rendering | Developer portal (`AP-001` PT-08); the markdown is an output, never a source |

### 9.2 `05-03` §4.2's standing

Ruled by `AR-009` `D-A9-01` and restated here because it is the single most consequential
instruction to any author in the estate:

> **`05-03` §4.2 is PARTIAL.** It is a curated cross-cutting subset — **64 of 988, 6.5%** — and its
> heading is corrected to *"Principal Cross-Cutting Events — a curated subset; the complete
> catalogue is generated and held in `IN-003`."*
>
> **No consumer specification may be written against it.**

### 9.3 `AP-003`'s re-check

`AP-003` describes **104 distinct event names**, written against the 64-event inventory. Its `O-06`
already records the exposure.

| Finding | Action |
|---|---|
| `AP-003` describes 104 names; `05-03` §4.2 holds 64 | The content pack already went beyond its source — correctly |
| **The generated catalogue will hold 988** | `AP-003` covers ~10.5% of it |
| Descriptions written against a name that is renamed in W1 | Must be re-checked **after** `RM-03`, not before |

**`AR-009` `RM-08` scheduled this at W2. Confirmed, with a dependency:** the re-check is worthless
until the ~242 convention-B renames land, so it is **W2, after `RM-03`**, and `AP-003`'s scope grows
from 104 to a curated subset of 988 that the Content Council must size. Raised as **`IN-A-12`**.

---

## 10. CI Gates

Continuing `AR-012` v1.1 `FF-01`…`FF-37`, `IN-001` `FF-38`…`FF-45`, `IN-002` `FF-46`…`FF-58`.

| # | Check | Scope | Timing | Enforcement |
|---|---|---|---|---|
| **FF-59** | Every emitted event has a registration, and every registration has an emitter | 988 | CI | Fail |
| **FF-60** | Every **consumed** event has a registered producer (`G-04`) | All subscriptions | CI | Fail |
| **FF-61** | Every consumer a producer names has itself registered a subscription — **the reciprocity check that supersedes `RM-07`** | All | CI | Fail |
| **FF-62** | Every `event_type` matches ADR-017 convention A, and its namespace is an `AR-008` aggregate — **not a module code** | 988 | CI | Fail after `RM-03` |
| **FF-63** | Every payload validates against its registered schema at emission | Runtime + CI | Runtime sample + CI | Fail |
| **FF-64** | **No payload property is classified `residency_restricted`** (`SC-07`) | All schemas | CI, at registration | Fail |
| **FF-65** | A new schema is `BACKWARD` compatible with the registered one | All | CI | Fail |
| **FF-66** | `sunset_at` ≥ `deprecated_at` + 6 months | Deprecated events | CI | Fail |
| **FF-67** | Every consumer declares a `replay_class`; the replay service refuses `R3` without an override | All consumers | CI + runtime | Fail / refuse |
| **FF-68** | Every registration declares `retention_class`, and the broker's configured retention matches it | 988 | CI + wave gate | Fail |

> **`FF-62` is scheduled, not immediate.** Enabling it before `RM-03` would fail the build for 242
> events that are correctly declared under the convention in force when they were written. It turns
> on the day `RM-03` completes, and from then on the convention cannot drift again.

---

## 11. The Registration Backlog

### 11.1 The denominator

| # | Work item | Count |
|---|---|---:|
| B-01 | Events to register with schemas | **988** |
| B-02 | Of those, convention-B renames first | **242** |
| B-03 | Consumer-side dispositions to **adjudicate and record** | **69** |
| B-04 | Of B-03, **D1** renames verified (free to correct) | **12** |
| B-05 | Of B-03, **D2** projections identified | **7** |
| B-06 | **Of B-03, D3 with no candidate of any kind — must be built** | **25** |
| B-06a | **Of B-03, unadjudicated** — a candidate exists, same-fact-or-not is a human call | **25** |
| B-07 | CON-03 webhooks to close before W1 | **8** |
| B-08 | Safety-critical events ahead of the bulk | **2** *(the third, `credit_note.issued`, is a rename — `IN-A-10`)* |
| B-09 | AsyncAPI documents to generate | 11 |
| B-10 | JSON Schemas to author | **988** |

### 11.2 Sequencing

| # | Action | Owner | Wave | Blocks |
|---|---|---|:--:|:--:|
| **RE-01** | **Ratify ADR-017** (convention A normative) and `AR-008` §3/§4.2 aggregate names | Design Authority | **W0** | ✔ everything |
| **RE-02** | Register the **2 safety-critical** events (§7.4) and the 8 CON-03 webhooks | M09, M20, M01, M03, M10, M37 | **W1** | CON-03 go-live, `G4-02` |
| **RE-03** | Execute the **242 convention-B renames** — jointly with `IN-001` `RI-03`'s ~40 API path renames | Enterprise Architecture | **W1** | RE-04, `FF-62` |
| **RE-04** | Record the **69 dispositions**; execute the 14 D1 renames | Integration Architect + portal owners | **W1** | Every portal |
| **RE-05** | Design and register the **6 D2 projections** with named projectors | M01, M02, M03, M07, M09 | **W1** | P01, P04, P10, CON-03 |
| **RE-06** | Build the registry, the generator and `FF-59`…`FF-68` | Platform Engineering + M28 | **W1** | Every consumer |
| **RE-07** | Register the W1 contexts' events with schemas (`platform`, `service-delivery`, `customer-engagement`) | Module owners | **W1** | W1 build |
| **RE-08** | **Build the D3 events** — **25 confirmed**, up to 50 once `RE-04` adjudicates the other 25; module scope that is in no plan | Module owners | W1–W7 | P07, P10, P12 |
| **RE-09** | Register the remaining contexts, one wave ahead of build | Module owners | W2–W7 | |
| **RE-10** | Re-check `AP-003` against the generated catalogue, **after** RE-03 | Content Lead | **W2** | `AP-003` `O-06` |
| **RE-11** | Correct `05-03` §4.2's heading; curate to the cross-cutting subset | Enterprise Architecture | W1 | `AR-009` `RM-06` |

### 11.3 Why the renames must be first

| Timing | Cost |
|---|---|
| **W1, before registration** | A text edit across 67 specifications. **No code exists.** 242 renames, and it resolves 5 of the 14 D1 divergences for free |
| After registration, before consumers | 242 registry updates plus 242 schema `$id` changes |
| **After consumers exist** | `05-03` §4.3 forbids breaking changes within a `schema_version`. Each rename becomes **a new event, a dual-publish period and a coordinated migration** across 67 modules and 12 surfaces — 242 times |

### 11.4 Effort — `PGD-A3-15` quantified

`PGD-AUDIT-003` raised `PGD-A3-15`: *"`IN-003` is one register row carrying 988 event registrations
with schemas. Its effort is in no plan."* Applying `GV-007`'s method:

| Component | Basis | Low | Expected | High |
|---|---|---:|---:|---:|
| 988 payload schemas + registrations | 0.4–1.2 h each incl. review | 49 PW | 84 PW | 148 PW |
| 242 convention-B renames | Text edit + citation sweep | 3 PW | 5 PW | 9 PW |
| 69 consumer adjudications (D1 correction + D2 projector design) | Analysis and agreement | 4 PW | 8 PW | 15 PW |
| **D3 events — design, build, test** (25 confirmed, up to ~50 after adjudication) | **Genuinely new module behaviour** | 14 PW | 45 PW | 110 PW |
| Registry, generator, 10 CI gates | Toolchain | 10 PW | 16 PW | 28 PW |
| 11 AsyncAPI documents + CloudEvents mapping | Generated, but the generator is built | 3 PW | 5 PW | 9 PW |
| **Total** | | **84 PW** | **163 PW** | **319 PW** |

> **`IN-003` is an 84–319 person-week deliverable carried as one `PGD-000` row**, and **RE-08's
> events — 25 confirmed, up to 50 — are module functionality that no module specification declares**,
> so the effort is absent from both the guiding-document stream and the build estimate. Together
> with `IN-002`'s 109–356 PW (`IN-A-02`), **`IN-002` and `IN-003` alone are 193–675 PW against
> `GV-007`'s 264–528 PW for all 127 remaining guiding documents.** Raised as **`IN-A-03`** and
> referred to `GV-007`, `GV-008` and `GV-004`.

---

## 12. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `IN-003-D-01` | Registry form | A markdown catalogue · **A registry declared in code, generated into artefacts** | **Registry** | A hand-maintained catalogue measured **6.5% accurate** at 64 of 988 | `AR-009` `D-A9-02` realised; `FF-59` |
| `IN-003-D-02` | Registration fields | `AR-009` `G-02`'s six · **nineteen** | **Nineteen** | Each addition answers a question the estate has already got wrong: replay safety, retention, PII scope, single producer, traceability to source | §3.1 |
| `IN-003-D-03` | Async contract language | OpenAPI `webhooks` · **AsyncAPI 3.0** · none | **AsyncAPI 3.0** | Multiple consumers of one message, ordering and partitioning are not expressible in OpenAPI | 11 generated documents |
| `IN-003-D-04` | CloudEvents | Adopt as the internal envelope · **Map at the external boundary** · ignore | **Map at the boundary** | Renaming the internal envelope invalidates `05-03` §4.1 and Tech Stack §12.2.6 for no gain; external consumers still get a standard form | §5.4; `actor` withheld |
| `IN-003-D-05` | The 69 unpublished | Register all as missing · **Disposition each into D1/D2/D3** | **Disposition each** | 14 are renames and 6 are projections; treating all 69 as missing would create 20 duplicate events | §7.3; **`credit_note.issued` reclassified** (`IN-A-10`) |
| `IN-003-D-06` | `platform.` events | Exempt from registration · **Register, filter in the view** | **Register** | Navigability is a rendering problem; exemption would leave compliance signals with no schema and no consumer | Answers `AR-009` Q-06 |
| `IN-003-D-07` | `AR-009` `RM-07` reciprocity | Execute as written · **Supersede with `FF-61`** | **Supersede** | `§12.1` is a narrative source list, not a subscription register — 34 rows against 988 events. It cannot answer the question | `IN-A-11`; `FF-61` |
| `IN-003-D-08` | When `FF-62` (naming) turns on | Immediately · **After `RM-03`** | **After `RM-03`** | Enabling it now fails the build for 242 correctly-declared events | §10 |

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | **Is ADR-017 ratified?** Without it, 988 registrations would be made under a convention that then changes | Design Authority | **W0 — blocking** | Everything |
| Q-02 | Is `IN-003`'s **84–319 PW** funded, including **RE-08's new events**? (`IN-A-03`, `PGD-A3-15`) | Programme Director | **W0** | Every consumer |
| Q-03 | **Who owns the D3 events?** M12 owes 8, M27 owes 6, M40 owes 6 — none appears in those modules' `§12.3` tables, so it is scope nobody has costed | Solution Architect + module owners | **W1** | P07, P10, P12 |
| Q-04 | Does the event store fall within PDPA erasure scope? §4.3 makes it answerable per event; the **decision** is still open (`AR-009` Q-03) | DPO / `SC-003` | W2 | CD-248 saga scope |
| Q-05 | Do external consumers receive **CloudEvents** or the native envelope? §5.4 publishes the mapping; adoption is a partner-contract decision | Integration Architect | W3 | `IN-006`, `AP-007`, `AP-008` |
| Q-06 | `AP-003` grows from 104 descriptions toward a curated subset of 988. **What subset, and who funds it?** (`IN-A-12`) | Content Council | W2 | `AP-003` `O-06`, developer portal |
| Q-07 | Is the **101-singleton-namespace** spread (E-10) a sign the aggregate model is too fine, or a normal long tail? It affects catalogue navigability | Chief Architect | W2 | `AR-008` review |

---

## 14. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The **consumer side** is measured, by a reproducible method, across all twelve portals | §2.2 script; §7.1 — 102 consumed, **69 unpublished** |
| AC-02 | Every one of the 69 is triaged, the triage's **measured limits** are stated, and no split is asserted beyond what was verified | §7.3.1 — **12 D1 · 7 D2 · 25 D3 · 25 unadjudicated**, generated into a CSV; the balance scheduled as `RE-04` |
| AC-03 | `AP-01`'s three safety-critical events are each dispositioned, and any correction to `AP-01` is stated | §7.4; `IN-A-10` reclassifies `credit_note.issued` as renamed, not missing |
| AC-04 | The registration record is specified field by field, with a reason for each | §3.1 — nineteen fields |
| AC-05 | A payload schema standard exists, consistent with `IN-002`'s type rules | §4.2 — `SC-01`…`SC-12` |
| AC-06 | The CloudEvents mapping `AR-009` §2.1 promised is published | §5.4 |
| AC-07 | Compatibility is stated as a checkable table, including the change CI **cannot** catch | §6.1 |
| AC-08 | Replay and retention classes are required fields with mechanical effects | §8.3, §8.4 |
| AC-09 | `AR-009` Q-06 is ruled | §8.5, `IN-003-D-06` |
| AC-10 | `AR-009` `RM-07` is either executed or explicitly superseded with a reason | §7.5, `IN-003-D-07`, `IN-A-11` |
| AC-11 | `PGD-A3-15` is quantified | §11.4 — 84–319 PW |
| AC-12 | A sequenced backlog with owners, waves and blocking flags exists | §11.2 |

**Definition of done.** Complete when every criterion is met, ADR-017 is ratified (Q-01), `RE-01`…
`RE-07` are executed, `FF-59`…`FF-68` are enabled, and `PGD-000`'s `IN-003` row carries a fresh
enumeration timestamp. **`AP-01` closes when `RE-02`, `RE-03` and `RE-04` are complete — not
before**, and `AR-009` and `IN-003` close it jointly.

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | **`AR-009`** | The mechanism, the envelope, the naming ruling, the 988 measurement. **This document is its `RM-05`** |
| Upstream | **`AR-008`** §3, §4.2 | Aggregate names are the first component of every event name |
| Upstream | `AR-004` ADR-016, ADR-017 | Outbox and naming decisions |
| Upstream | `IN-001` §11 | The consumer/producer reconciliation this document completes on the async side |
| Upstream | `DA-002` | Field names, types and PII classification |
| Downstream | **`IN-006`** | The `external` channel, its CloudEvents shape, and which events are webhook-eligible |
| Downstream | `IN-002` | Shares the type rules; `platform` context operations serve the registry |
| Downstream | `IN-008` | The event test suite — idempotency, ordering, compatibility, replay refusal |
| Downstream | `AR-003` DP-04, `AR-007` §7.4 | Emission design and standard |
| Downstream | `AR-012` `FF-04`, `FF-09`, `FF-28` | Outbox coverage, residency, shared library |
| Downstream | `SC-003`, `DA-006` | Event-store erasure scope, now enumerable via `pii_classification` |
| Downstream | `PE-005` | Broker retention configured from `retention_class` |
| Lateral | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` §4 | §4.2 demoted to a curated subset; heading corrected by `RE-11` |
| Lateral | `../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P*.md` §12.3 | **The 102 consumed events measured here** |
| Lateral | `../../project_content/15_Integration_and_Developer_Content/AP-003_*.md` | 104 descriptions, re-checked at W2 after `RM-03` |

---

## 16. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`./IN-001_Integration_Architecture_Specification.md`](./IN-001_Integration_Architecture_Specification.md) ·
[`./IN-002_API_Specification_OpenAPI_Contracts.md`](./IN-002_API_Specification_OpenAPI_Contracts.md) ·
[`./IN-006_Webhook_Callback_and_Partner_Push_Specification.md`](./IN-006_Webhook_Callback_and_Partner_Push_Specification.md) ·
[`./IN-008_Integration_Test_Sandbox_and_Certification_Specification.md`](./IN-008_Integration_Test_Sandbox_and_Certification_Specification.md) ·
[`./IN-003_artefacts/README.md`](./IN-003_artefacts/README.md) ·
[`../02_Architecture_and_Design/AR-009_Event_Driven_Architecture_and_Messaging_Design.md`](../02_Architecture_and_Design/AR-009_Event_Driven_Architecture_and_Messaging_Design.md) ·
[`../02_Architecture_and_Design/AR-008_Domain_Model_and_Bounded_Context_Map.md`](../02_Architecture_and_Design/AR-008_Domain_Model_and_Bounded_Context_Map.md)

**Workspace**
`../../1000fix_ERP_Module/03_Modules/**/M*.md` §12.1, §12.3 (all 67) ·
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P*.md` §12.3 (all 12) ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` §3.3, §4 ·
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M28_*.md` §5.3, §8.1, §12.5 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §12.2.6 ·
`../../project_content/_AUDIT/AUDIT-016_Category_15_AP_Content_Audit.md` `AP-01` ·
`../../project_content/15_Integration_and_Developer_Content/AP-003_*.md`

**External sources**

| Source | What it establishes | Verified |
|---|---|---|
| AsyncAPI Specification 3.0 (and 3.1.0, July 2026 — additive) | Channels, operations, messages, message traits | 2026-08-18 |
| JSON Schema 2020-12 | Payload schema dialect | 2026-08-18 |
| CloudEvents Specification 1.0 | `id`, `source`, `type`, `time`, `subject`, `dataschema`, extension attributes | 2026-08-18 |
| Schema-registry `BACKWARD` compatibility semantics | The field-by-field rules in §6.1 | 2026-08-18 |
| Hohpe & Woolf, *Enterprise Integration Patterns* | Message store, idempotent receiver, dead letter, claim check | 2026-08-18 |

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Integration Architecture | Initial issue. Measures the **consumer side** across all twelve portals for the first time: **102 events consumed, 69 published by no module (67.6%)** — extending `AP-01` from 21 to 69. Triages all 69, states the triage's measured limits rather than asserting a clean split, and establishes **12 renames, 7 projections, 25 with no candidate at all and 25 unadjudicated**, published as a CSV worklist. Reclassifies `credit_note.issued` as renamed rather than missing (`IN-A-10`). Specifies the nineteen-field registration, publishes the CloudEvents mapping `AR-009` promised, rules `AR-009` Q-06, supersedes `RM-07` (`IN-A-11`), and quantifies `PGD-A3-15` at **84–319 PW** | *Pending — Design Authority not constituted (`PGD-A1-09`)* |

---

*`IN-003` · Category 04 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
