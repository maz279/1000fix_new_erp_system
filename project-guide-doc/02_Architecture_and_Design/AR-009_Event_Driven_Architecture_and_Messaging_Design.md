---
id: AR-009
title: Event-Driven Architecture & Messaging Design
category: 02 — Architecture & Design
code: AR
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Architect
approver: Design Authority (constituted under GV-002)
standards_basis: >
  Transactional outbox pattern · CloudEvents 1.0 (envelope influence) · JSON Schema 2020-12 ·
  Enterprise Integration Patterns (Hohpe/Woolf) · ISO/IEC/IEEE 42010:2022 process viewpoint
traces_to: >
  PGD-000 AR-009 · AS-08 · ADR-016 · ADR-017 · audit AP-01 (critical) ·
  05-03 §4 · NFR-043 · DI-05 · risk TR-12
depends_on: AR-001 · AR-008 (aggregate names) · IN-003 (schema registry)
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 02:05 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# AR-009 — Event-Driven Architecture & Messaging Design

### Category 02 · Code `AR` · Transactional outbox · Enterprise Integration Patterns

---

> **The measurement that sizes this document.** Extraction across the `### 12.3 Domain Events
> Published` table of all 67 module specifications at **2026-08-18 02:05 (+06)** returns
> **988 distinct declared events**. `05-03` §4.2 registers **64**.
>
> Audit **`AP-01` (critical)** found 21 unregistered event names by comparing three files. That
> finding is sound; its *scale* was set by its sample. **The true gap is 953 unregistered events —
> approximately 45× larger.**

---

## 1. Purpose

`AR-001` fixes that the system is event-driven and that the outbox is mandatory. This document
**designs the mechanism**: the taxonomy, the naming convention, the envelope, delivery semantics,
ordering, idempotency, the outbox and relay, replay, poison handling, schema evolution, and the
governance that keeps a 988-event catalogue from becoming unusable.

It also does the thing `AP-01` asked for and nobody could do without the measurement: **rule on
whether `05-03` §4.2 is complete or principal, and say so.**

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | Event taxonomy — four kinds, with different rules for each |
| 2 | The naming convention ruling (ADR-017) and the migration it requires |
| 3 | The envelope, and what every field is for |
| 4 | Delivery semantics — at-least-once, ordering, idempotency |
| 5 | The transactional outbox and relay design |
| 6 | Bus topology — Redis Streams (W1–W5) → Redpanda (W6+) |
| 7 | Consumer contract — retries, dead-letter, poison handling, replay |
| 8 | Schema evolution and the compatibility rule |
| 9 | **Catalogue governance** — how 988 events are registered, generated and kept true |
| 10 | The measured reconciliation and its remediation plan |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| The event catalogue itself — per-event payload schemas | `IN-003` | This document designs the mechanism; `IN-003` is the registry |
| Aggregate names | `AR-008` | The first component of every event name |
| API contracts | `IN-002` | Synchronous surface |
| Webhook signature scheme and partner delivery | `IN-006` | External delivery; three W1 platform decisions are unmade there |
| Broker infrastructure sizing and operation | `PE-005`, `PE-008` | This document fixes the topology; `PE` runs it |
| Per-module emission code | `AR-003` DP-04, `AR-007` §7.4 | Design and standard |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **`IN-003` author** | §9's governance model determines whether the registry is hand-written (unviable at 988) or generated |
| Every module developer | §3 naming, §4 envelope, §7 consumer contract |
| Solution Architect | §10's remediation plan is Wave 1 work |
| Platform engineers | §6 topology, §5 relay, §8 evolution |
| QA lead | §7 is directly testable; the event test suite derives from it |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure and rationale |
|---|---|---|
| **Transactional outbox pattern** | §5 — event written in the same DB transaction as the state change; relay publishes | None. ADR-016 |
| **CloudEvents 1.0** | §4 envelope carries `id`, `type`, `source`, `time`, `subject`, `datacontenttype` equivalents | **Departure:** field names follow the estate's existing envelope (`event_id`, `event_type`, `occurred_at`, `aggregate`) rather than CloudEvents' names. Rationale: the envelope is already specified in `05-03` §4.1 and in the Technology Stack Specification §12.2.6; renaming it now would invalidate two published documents for no functional gain. **A CloudEvents mapping is published in `IN-003` for external consumers** |
| **JSON Schema 2020-12** | Payload schemas in `IN-003`; compatibility checked in CI | None |
| **Enterprise Integration Patterns** | Publish-subscribe, dead letter, idempotent receiver, message store, claim check | Adopted by name so the vendor market recognises them |
| ISO/IEC/IEEE 42010:2022 | Process viewpoint | Inherits `AR-001` VP-4 |

### 2.2 Source material and extraction

| Source | Contribution |
|---|---|
| All 67 specifications §12.1, §12.3 | **The measurement.** 988 published, 34 consumed-without-producer candidates |
| `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` §4 | Envelope, 64-event inventory, consumer rules |
| `../../primary-doc/…Technology_Stack_Specification.md` §12.2.6 | Consumer rules with named enforcement; CD-125, CD-247 |
| Ibid. §23 `TR-12` | *"Event outbox not applied uniformly, producing silent data divergence"* |
| `../../project_content/_AUDIT/AUDIT-016_*.md` `AP-01` | The 21-name finding and its three-class analysis |
| `../../project_content/15_Integration_and_Developer_Content/AP-003_*.md` | Domain event catalogue **descriptions** — content written against the 64-event inventory |

```bash
# Published events — first column of every module's §12.3 table
for f in $(find 03_Modules -name 'M[0-9]*.md'); do
  awk 'BEGIN{p=0} /^### 12\.3/{p=1;next} /^### 12\.4/{p=0} /^## /{p=0} p' "$f" \
    | grep -oE '^\| `[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*`' | sed 's/^| //;s/`//g'
done | sort -u | wc -l          # → 988

# Registered events — 05-03 §4.2
sed -n '/### 4.2 Event Inventory/,/### 4.3/p' 05_Cross_Cutting_Specifications/05-03_*.md \
  | grep -cE '^\| `[a-z_]+\.[a-z_]+`'                                  # → 64
```

### 2.3 Audit findings this document closes

| Finding | Disposition |
|---|---|
| **`AP-01` (critical)** — 21 events consumed and unregistered, 14 genuinely missing | **Contributes decisively.** §10 rules on the "principal vs complete" question `AP-01` posed, quantifies the true gap at 953, and schedules the remediation. **Closes fully only with `IN-003`** |
| `AP-01` sub-finding — `credit_note.issued` appears **twice** in the list of 14 "genuinely missing" events, so 14 distinct names is actually **13** | **Raised as `PGD-A3-14`.** A minor arithmetic slip, recorded rather than silently corrected, per the estate's convention |
| `TR-12` Outbox applied unevenly | §5.5 CI coverage gate `FF-04` + DoD-05 |
| `AR-001` CR-04 — correspondence between the runtime view and the event registry currently fails | §10's remediation is the closure path |

---

## 3. Event Taxonomy and Naming

### 3.1 Four kinds of event

Not everything on the bus is a domain event, and applying domain-event rules to all of it is why
event catalogues become unusable.

| # | Kind | Definition | Naming | Registered in `IN-003`? | Retention |
|---|---|---|---|:--:|---|
| **E1 — Domain event** | A fact about a business aggregate that has happened | `<aggregate>.<past-tense-verb>` | **Yes — always** | Per event class (§8.4) |
| **E2 — Integration event** | A domain event shaped for an **external** consumer, with fields removed or added at the boundary | Same name, `external` channel | Yes, with its external schema | As E1 |
| **E3 — Platform event** | An infrastructure fact — job completed, sync failed, credential expiring | `platform.<noun>_<verb>` | Yes, in the `platform` namespace | 30 days |
| **E4 — Notification trigger** | An instruction to send something to a person | **Not an event.** A command to CD-234 | No | n/a |

> **E4 is on this list because it is the most common category error.** *"Send the customer an SMS"* is
> not a fact about the past; it is an instruction. Modelling it as an event means a replay re-sends
> every SMS ever sent. **Notification is triggered by a consumer reacting to an E1 event**, never by
> publishing a "notification event".

### 3.2 The naming ruling

**Convention A is normative** (ADR-017, proposed 2026-08-18):

```
<aggregate>.<past_tense_verb>
```

where **aggregate** is the domain aggregate root from `AR-008` §4.2 — **not** the owning module's
code.

| Rule | Detail |
|---|---|
| **N-01** | The aggregate is one of the 22 roots in `AR-008` §4.2, or an interior entity of one where the fact is genuinely about the interior entity (`work_order.completed`) |
| **N-02** | The verb is **past tense**. `service_order.completed`, never `service_order.complete` or `.completing` |
| **N-03** | `snake_case` throughout. No dots inside either component |
| **N-04** | **Ambiguous nouns are qualified per `AR-008` §3.** `claim.submitted` is forbidden; `warranty_claim.submitted` is required |
| **N-05** | Platform events use the reserved `platform.` namespace (E3) |
| **N-06** | The name is **permanent**. A renamed event is a new event with a dual-publish period (§8.3) |

### 3.3 The measured convention split

The 988 declared events use **243 distinct namespaces**. They fall into two populations:

| Population | Namespaces | Events | Example | Verdict |
|---|---:|---:|---|---|
| **Aggregate-aligned** (convention A) | ~200 | ~743 | `service_order.completed`, `asset.registered`, `contract.activated`, `rental.dispatched` | ✅ Conforms |
| **Module-code-aligned** (convention B) | **~40** | **~245** | `ap.invoice_received`, `ar.credit_note_issued`, `gl.entry_posted`, `wh.pick_confirmed`, `fpa.budget_approved`, `mdm.record_merged`, `grc.control_tested` | ⚠ **Must be renamed** |

Module-code namespaces observed: `ai ap ar bi cash cod data deal dr eol esg fpa gl grc hse it job
kpi lead mdf mdm mrr msp pip po qbr rma rtv rule site sla sod task tax wh wipe zone` — 40 of the 243.

**Worked renames**, showing the pattern:

| Convention B | → Convention A | Aggregate (`AR-008`) |
|---|---|---|
| `ap.invoice_received` | `vendor_invoice.received` | new interior root under `purchase_order` context |
| `ap.payment_released` | `payment.released` | AGG-09 |
| `ar.credit_note_issued` | `credit_note.issued` | interior to AGG-08 |
| `gl.entry_posted` | `journal_entry.posted` | AGG-10 |
| `wh.pick_confirmed` | `stock_item.picked` | AGG-11 |
| `mdm.record_merged` | `party.merged` (where the record is a party) | AGG-03 |
| `tax.return_filed` | `vat_return.filed` | interior to AGG-08 context |
| `sod.violation_blocked` | `platform.sod_violation_blocked` | E3 platform event |

### 3.4 Why this cannot wait

| Timing | Cost |
|---|---|
| **Now (Wave 1, before `IN-003`)** | A text change across 67 specification files. **No code exists.** Approximately 245 renames |
| After consumers exist | `05-03` §4.3 forbids breaking changes within a `schema_version`. The rename becomes a **new event, a dual-publish period, and a coordinated migration of every consumer** — across 67 modules and 12 surfaces |

**Prerequisite:** `AR-008` §3 and §4.2 must be ratified first, because a rename requires knowing the
aggregate name. That makes `AR-008` a Wave 1 critical-path item it was not previously understood to be.

---

## 4. The Envelope

Every event, without exception:

```json
{
  "event_id":       "uuid",
  "event_type":     "service_order.completed",
  "schema_version": "1.2",
  "occurred_at":    "2026-08-18T09:14:22Z",
  "company_id":     1,
  "operating_unit_id": 17,
  "actor":          { "type": "user", "id": 442 },
  "correlation_id": "uuid",
  "causation_id":   "uuid",
  "aggregate":      { "type": "service_order", "id": 918234 },
  "payload":        { }
}
```

| Field | Purpose — stated because two of these are routinely omitted and then missed |
|---|---|
| `event_id` | **The idempotency key.** Consumers record processed ids and ignore duplicates |
| `event_type` | Routing and schema selection |
| `schema_version` | Evolution (§8). Additive changes keep the version; breaking changes require a new one |
| `occurred_at` | **When the fact happened**, not when it was published. UTC, always |
| `company_id`, `operating_unit_id` | Multi-entity/branch context. **Consumers filter on these**; without them every consumer sees every branch |
| `actor` | Who or what caused it — `user`, `system`, `integration`, `job`. Required for audit |
| `correlation_id` | **The whole-journey identifier**, injected by Kong and propagated across every hop (NFR-092-M). This is what turns a two-day diagnosis into a twenty-minute one |
| `causation_id` | **The `event_id` of the event that caused this one.** Lets a chain be reconstructed: booking → order created → dispatched → completed → invoiced |
| `aggregate` | Type and id. **The partition key** (§4.2) |
| `payload` | The facts, per the `IN-003` schema |

### 4.1 Payload rules

| # | Rule |
|---|---|
| **P-01** | Payload carries **facts, not commands**. `service_order.completed` carries what was done, never "now raise an invoice" |
| **P-02** | Payload carries **what a consumer needs to act without a call-back**. An event that forces every consumer to fetch the record has moved the coupling, not removed it |
| **P-03** | Payload **never** carries a residency-classified value (`AR-001` LB-08). It carries the resident key; the consumer reads through CD-233 |
| **P-04** | Payload carries **no personal data beyond what every consumer needs** (IP-10). Where one consumer needs more, it reads through an API |
| **P-05** | Large binaries use the **claim-check pattern** — a reference to object storage, never the bytes |
| **P-06** | Money in a payload is `{ "amount": "1234.50", "currency": "BDT" }` — **string decimal**, never a float (AS-10) |

> **P-03 is the rule most likely to be broken by accident.** A developer adding `nid_number` to a
> `party.updated` payload for a consumer's convenience puts residency-classified data on the bus, in
> the broker's log, in the dead-letter queue and in every consumer's inbox. Checked by `FF-09`.

### 4.2 Partitioning and ordering

| Property | Position |
|---|---|
| Partition key | **`aggregate.type` + `aggregate.id`** |
| Ordering guarantee | **Per aggregate instance only. Never global** |
| Consequence | Two events about the same service order arrive in order. An event about a service order and one about an invoice have **no relative order**, and a consumer that assumes one is defective |

**A consumer needing cross-aggregate order must use `causation_id`** to reconstruct the chain, or
tolerate arrival in either order. This is stated because "the invoice event arrived before the order
event" is the most common event-system bug, and it is a consumer defect, not a broker defect.

---

## 5. The Transactional Outbox

### 5.1 Why (restated once, because it is the decision most likely to be skipped)

| Approach | Failure |
|---|---|
| Publish after commit | A crash between commit and publish **loses the event silently**. Nothing alerts |
| Publish before commit | A rollback after publication means **the event describes a state that never existed** |
| **Outbox in-transaction + relay** | Exactly-once *emission*. The only pattern that makes AS-08 true rather than usually true |

### 5.2 Structure

```
BUSINESS TRANSACTION (one DB transaction)
  ├─ UPDATE fix_service_order SET state='delivered' …
  └─ INSERT INTO fix_domain_event (event_id, event_type, schema_version,
                                   occurred_at, aggregate_type, aggregate_id,
                                   company_id, operating_unit_id, actor,
                                   correlation_id, causation_id, payload,
                                   published=false, attempts=0)
COMMIT  ← both, or neither
                    │
        ┌───────────▼────────────┐
        │  OUTBOX RELAY (CD-125) │  polls (published=false) ORDER BY occurred_at
        │  batch · publish · mark│  index: (published, occurred_at)
        └───────────┬────────────┘
                    ▼
        Redis Streams (W1–W5) → Redpanda (W6+)
```

### 5.3 Relay design

| Property | Position |
|---|---|
| Trigger | Poll on a short interval, plus a `LISTEN/NOTIFY` wake so latency is not bounded by the poll interval |
| Batching | Bounded batch; **publish then mark, never mark then publish** |
| Failure | A relay crash after publish and before mark causes a **duplicate**, which is safe — consumers are idempotent. The reverse order would cause a **loss**, which is not |
| Ordering | Per aggregate, by `occurred_at` then insertion order |
| Concurrency | Multiple relay instances partition by `aggregate_id` hash. **Never two relays on one aggregate** |
| Backpressure | If the bus is unavailable, outbox rows accumulate. **State remains correct.** Alert on outbox depth and age, not only on relay errors |
| Pruning | Published rows retained 7 days for replay-from-source, then archived |
| Latency target | 95% of events consumed within **5 s** of publication (NFR-043) — measured end-to-end, not relay-only |

> **The property that makes the outbox a *resilience* mechanism and not only a correctness one:**
> a bus outage degrades event **timeliness**, never event **existence**. Compare the post-commit
> publish, where a bus outage silently loses facts.

### 5.4 Monitoring

| Signal | Threshold | Action |
|---|---|---|
| Outbox depth | > 1,000 unpublished | Alert — relay health |
| **Outbox age** — oldest unpublished row | **> 60 s** | Alert. **This is the leading indicator**; depth alone hides a stuck partition |
| Relay error rate | > 1% over 5 min | Alert |
| Publish→consume p95 | > 5 s | NFR-043 breach |
| Dead-letter count | > 0 for 1 h | Mandatory triage |

### 5.5 The uniformity gate

`TR-12`: *"Event outbox not applied uniformly, producing silent data divergence between modules."*

**Control `FF-04`:** for every model with a `state` field, CI asserts that **every declared
transition emits an event through `emit_event()`**, and that the emitted set matches the module's
SDD §9 transition table. A transition with no event, or an event with no transition, **fails the
build**. Reinforced by DoD-05 at module acceptance.

---

## 6. Bus Topology

### 6.1 Two phases (ADR-013)

| Phase | Broker | Rationale |
|---|---|---|
| **W1–W5** | **Redis Streams** | Already deployed for cache, sessions and locks. Consumer groups, at-least-once and per-stream ordering are sufficient at Wave 1–5 volume. **No new operational component in the heaviest wave** |
| **W6+** | **Redpanda** (Kafka API) | Durable retention, replay-from-timestamp, partition scaling, and inter-system integration as external consumers arrive |

| Property | Position |
|---|---|
| Migration | **Dual-write during one wave boundary**, then cut over. Consumers use a shared client library so the broker change is a configuration change (§6.2) |
| Trigger to move early | Replay or retention needs arriving before W6, or outbox depth sustained above threshold |
| Licence watch | Redpanda is **BSL**, converting to Apache-2.0 four years after each merge. **Kafka (Apache-2.0) is the registered fallback** (`TR-09`) |

### 6.2 The consumer library — the decision that makes the migration cheap

**One shared consumer library** (part of CD-125) provides: subscription, deserialisation, schema
validation, the idempotency ledger, retry with exponential backoff, dead-lettering, metrics and
tracing propagation.

| Reason | Detail |
|---|---|
| Broker independence | The W5→W6 migration is a library version bump, not 67 module changes |
| Uniform semantics | Idempotency and retry cannot be "mostly right" in some modules |
| Observability | Every consumer emits the same metrics without each author remembering to |

**No module writes bus client code directly.** This is a `FF-28` CI check.

### 6.3 Channels

| Channel | Contents | Consumers | Retention |
|---|---|---|---|
| `domain` | E1 domain events | Internal modules | 7 days (Redis) / 30 days (Redpanda) |
| `external` | E2 integration events, boundary-shaped | Webhook dispatcher, partner delivery | 30 days |
| `platform` | E3 platform events | Observability, ops | 30 days |
| `dlq.<channel>` | Poisoned messages | Triage tooling | **90 days — never auto-purged** |

---

## 7. The Consumer Contract

Every consumer, without exception.

| # | Rule | Enforcement |
|---|---|---|
| **C-01** | **Idempotent.** Record processed `event_id`s; ignore duplicates | Shared library; event test suite |
| **C-02** | **Order-tolerant across aggregates.** Assume ordering only within one aggregate instance | Design review; test with shuffled delivery |
| **C-03** | **Retry:** 3 attempts, exponential backoff, then dead-letter with alert | Shared library |
| **C-04** | **Never block the stream.** A consumer that cannot process a message dead-letters it and continues | Shared library |
| **C-05** | **Replayable** from a point in time with **no side effect on other consumers** (CD-247) | Consumer design; replay test |
| **C-06** | **No side effect outside its own boundary during replay.** A replay must not re-send SMS, re-charge a card or re-post to the ledger | §7.2 |
| **C-07** | Declares its subscriptions in `IN-003` so producers know who they will break | Registry |
| **C-08** | Emits standard metrics: lag, processed, failed, dead-lettered | Shared library |
| **C-09** | Filters on `company_id` / `operating_unit_id` where the consumer is branch-scoped | Design review |

### 7.1 Poison handling

| Stage | Behaviour |
|---|---|
| Attempt 1–3 | Exponential backoff; transient failures usually clear |
| Dead-letter | Full envelope + failure reason + stack + consumer id → `dlq.<channel>` |
| Alert | **Any dead letter older than 1 hour is a mandatory triage item.** Not a dashboard number |
| Resolution | Fix the consumer, **replay from the DLQ**. Never edit and re-inject by hand |
| **Never** | Auto-purge a DLQ. A silently discarded event is the failure mode the whole design exists to prevent |

### 7.2 Replay safety — the classification every consumer must declare

| Class | Behaviour on replay | Examples |
|---|---|---|
| **R1 Idempotent projection** | Safe. Recompute from scratch | Warehouse loads, read models, search index, KPI aggregates |
| **R2 Guarded side effect** | Safe **only** with a suppression window or an already-done check | Invoice creation (check existence first) |
| **R3 External side effect** | **Never replayed without an explicit operator decision.** Flagged in the registry | SMS/WhatsApp send, payment execution, brand claim submission, BEFTN file generation |

**Every consumer declares its class in `IN-003`.** The replay service (CD-247) **refuses to replay an
R3 consumer** without an explicit override with a named operator, which is logged. This is what stops
a routine replay from re-sending 40,000 SMS messages.

---

## 8. Schema Evolution

### 8.1 Compatibility rule

| Change | Allowed within `schema_version`? |
|---|:--:|
| Add an optional field | ✅ |
| Add a value to an open enumeration | ✅ |
| Remove a field | ❌ |
| Rename a field | ❌ |
| Change a type | ❌ |
| Make an optional field required | ❌ |
| Narrow a constraint | ❌ |

**Additive only.** Anything else requires a new `schema_version` and a **dual-publish period**.

### 8.2 CI enforcement

| Check | Blocks |
|---|:--:|
| New schema is backward-compatible with the registered one | ✔ |
| Every emitted event's payload validates against its registered schema | ✔ |
| Every consumed event has a registered producer | ✔ |
| Every declared consumer's expected schema is satisfied by the producer's | ✔ |

### 8.3 Dual publish

| Step | Action |
|---|---|
| 1 | Producer publishes **both** versions to the same channel |
| 2 | Consumers migrate, each confirming in the registry |
| 3 | When every registered consumer is on the new version, the old is deprecated |
| 4 | **Minimum six months' notice** before removal (API-02 parity) |
| 5 | Removal is recorded in `IN-003` with the date and the consumers that confirmed |

### 8.4 Retention by event class

| Class | Retention | Reason |
|---|---|---|
| Financial (`invoice.*`, `payment.*`, `journal_entry.*`) | **7 years** | Statutory |
| Personal-data events (`party.*`, consent, DSR) | **5 years minimum** | NFR-095 processing records |
| Custody and evidence (`data_case.*`, `consignment.*`, destruction) | Evidence period | Legal defensibility |
| Operational | 30 days | Replay window |
| Platform (E3) | 30 days | Diagnostics |

> **A tension that must be stated rather than discovered.** NFR-095 requires processing records for
> five years; PDPA erasure (NFR-093) requires personal data removed on request. **Event payloads
> containing personal data are subject to erasure; the processing record is not.** The resolution is
> P-03/P-04: keep personal data out of payloads, so the event stream carries the *fact* of processing
> without the *data* processed. Where a payload must carry personal data, it is subject to the CD-248
> erasure saga — which makes the event store one more place erasure must reach. Referred to `SC-003`
> and `DA-006`.

---

## 9. Catalogue Governance

### 9.1 The 64-event catalogue cannot be maintained by hand at 988

`05-03` §4.2 was authored as a cross-cutting inventory before most module specifications existed. It
was accurate for 30 modules. **At 988 events across 67 modules, a hand-maintained catalogue will
diverge from reality within one wave** — and the measurement in §10 shows it already has, by 953.

### 9.2 The generated catalogue

| Layer | Content | Source of truth |
|---|---|---|
| **Registry** (`IN-003`) | Name, aggregate, producer, schema, version, consumers, replay class, retention | **Declared in code**, at the emission point |
| **Generated catalogue** | Human-readable, published to the developer portal | Generated from the registry in CI |
| `05-03` §4.2 | **Demoted to a curated cross-cutting subset** — the ~30 events that cross three or more categories | Hand-curated, explicitly partial, labelled as such |
| `AP-003` content pack | Descriptions for the developer portal | Written against the generated catalogue, not against `05-03` |

**This is M28 `FR-IPF-032`'s living catalogue.** The measurement in §10 is the evidence that it is
mandatory rather than desirable.

### 9.3 Registration rules

| # | Rule |
|---|---|
| **G-01** | An event is registered **before** the code that emits it merges |
| **G-02** | Registration names: aggregate, producer module, schema, consumers, ordering guarantee, replay class, retention class |
| **G-03** | **An event with no declared consumer is a defect** — either a consumer is missing or the event should not exist |
| **G-04** | **An event consumed with no registered producer fails CI** |
| **G-05** | A name is permanent. A rename is a new event with a dual-publish period |
| **G-06** | The catalogue is regenerated at every wave gate and diffed. **An undeclared change is a gate failure** |

> **G-03 has teeth.** Of the 988 declared events, every one names consumers in the §12.3 table — the
> specifications are disciplined about this. What is not yet verified is whether the named consumer's
> §12.1 reciprocates, which is `IN-003`'s first reconciliation job.

---

## 10. The Measured Reconciliation and Its Remediation

### 10.1 The measurement

| Measure | Count |
|---|---:|
| Distinct events **declared published** in module §12.3 tables | **988** |
| Events **registered** in `05-03` §4.2 | **64** |
| **Declared but unregistered** | **953** |
| **Registered but published by no module §12.3** | **29** |
| Distinct events **consumed** in module §12.1 tables | 34 |
| **Consumed with no producer anywhere** | **8** |
| Distinct namespaces in use | **243** |
| Namespaces in **convention B** (module-code) | **~40**, covering ~245 events |

### 10.2 The ruling `AP-01` asked for

`AP-01` posed the question directly: *"`05-03` §4.2 is headed 'Event Inventory (Principal Events)'.
'Principal' is doing a great deal of work in that heading. If the inventory is deliberately partial,
then `FR-IPF-032`'s living catalogue will be the first document that reveals the true event count, at
which point every consumer specification written against the inventory is incomplete."*

> **Ruling. `05-03` §4.2 is PARTIAL and is hereby declared so.** It is a curated cross-cutting subset,
> not the catalogue. Its heading is corrected to *"Principal Cross-Cutting Events — a curated subset;
> the complete catalogue is generated and held in `IN-003`."*
>
> **`AP-01`'s prediction was correct**, and it is discharged 45× larger than the sample suggested.
> No consumer specification should be written against `05-03` §4.2.

### 10.3 The 29 registered-but-unpublished events

These are **not missing** — they are convention-A names whose producers now declare convention-B
names for the same facts:

`asset.status_changed` · `capa.closed` · `certification.expired` · `certification.expiring` ·
`commission.earned` · `complaint.raised` · `contract.expiring` · `customer.merged` ·
`customer.registered` · `employee.joined` · `employee.left` · `ewaste.disposed` · `invoice.created` ·
`invoice.paid` · `model.prediction_made` · `nonconformance.raised` · `part.consumed` ·
`payment.failed` · `payout.executed` · `price_book.published` · `purchase_order.issued` ·
`refund.processed` · `service_order.completed` · `stock.below_reorder` · `stock.count_variance` ·
`tradein.accepted` · `warranty_claim.created` · `warranty_claim.decided` · `warranty_claim.submitted`

**`service_order.completed` is on that list**, and it is the most-referenced event in the entire
estate — cited in `05-03` §4.2, `02-01` §7 as the worked example, `AP-003` content, and multiple
portal specifications. **No module's §12.3 declares it.** That single line is the clearest possible
illustration of what the convention split costs.

**Disposition:** all 29 are reconciled by the §3.3 rename, not by registering new events. They are
the *correct* names; the producers' declarations must move to them.

### 10.4 The 8 consumed-with-no-producer events

| Event | Consumed by | Disposition |
|---|---|---|
| `asset.status_changed` | Multiple | §10.3 — rename resolves |
| `employee.joined` | M29 | §10.3 — rename resolves. **Also `AR-006` §5.1**: M29 (W1) consuming an M21 (W5) event is the wave violation MV-01 addresses |
| `employee.left` | M29 | As above |
| `import.cleared` | M15, M41 | **Genuinely missing.** M44 must publish it |
| `landed_cost.finalised` | M15 | **Genuinely missing.** M44 must publish it |
| `loyalty.benefit_changed` | M38, M12 | **Genuinely missing.** M10 must publish it |
| `order.completed` | Several | **Ambiguous** — `service_order.completed` or `marketplace_order.completed`? `AR-008` §3 forbids the unqualified form. Must be disambiguated per consumer |
| `service_order.routed_to_workshop` | M31 | **Genuinely missing.** M01 must publish it — and it is the trigger for the entire workshop path |

### 10.5 `AP-01`'s three safety-critical events

`AP-01` identified three of its 14 as more than documentation conveniences. All three remain
unpublished by any module's §12.3:

| Event | What depends on it |
|---|---|
| **`warranty_claim.evidence_incomplete`** *(named `claim.evidence_incomplete` in `AP-01`; qualified per `AR-008` §3)* | **A control.** `P08` `T-05` uses it to **suppress claim submission** when the evidence pack is incomplete against the brand's rules. The W4 gate's 90% first-submission approval target rests on that suppression |
| **`recall.execution_updated`** | **Product safety.** `P08` `FR-POR-254` publishes recall execution status to the brand |
| **`credit_note.issued`** | **The SLA remedy.** `P04` `AC-10` requires service credits published to the client without prompting |

> **An architectural control that is documented and unpublished is not a control.** These three are
> Wave 1 registration items, ahead of the bulk remediation.

### 10.6 Remediation plan

| # | Action | Owner | Wave | Blocking |
|---|---|---|:--:|:--:|
| **RM-01** | Ratify **ADR-017** (convention A normative) | Design Authority | **W0** | ✔ everything below |
| **RM-02** | Ratify `AR-008` §3 language rulings and §4.2 aggregate names | Design Authority | **W0** | ✔ RM-03 |
| **RM-03** | Rename ~245 convention-B declarations across the affected specifications | Enterprise Architecture | **W1** | ✔ RM-05 |
| **RM-04** | Register the 3 safety-critical events (§10.5) and the 4 genuinely missing (§10.4) | Module owners | **W1** | ✔ |
| **RM-05** | Build the registry (`IN-003`) with generated catalogue; register all 988 | `IN-003` owner + M28 | **W1** | ✔ every consumer |
| **RM-06** | Correct `05-03` §4.2's heading to declare it partial; curate to the cross-cutting subset | Enterprise Architecture | W1 | |
| **RM-07** | Reconcile every §12.3 consumer against the consumer's §12.1 (G-03/G-04) | `IN-003` owner | W1 | |
| **RM-08** | Re-check `AP-003` content descriptions against the generated catalogue | Content Lead | W2 | |
| **RM-09** | Enable `FF-04` outbox coverage and `FF-28` shared-library checks | Platform | W1 | |

> **RM-05 is materially larger than `PGD-000` records.** `IN-003` is one register row carrying **988
> event registrations with schemas**. It is a Wave 1 blocker for every consumer, and its effort is in
> no plan. This extends open finding `PGD-A1-05` and is raised as **`PGD-A3-15`**.

---

## 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | **Ratify ADR-017?** Without it, RM-03 cannot start and 953 registrations would be made under a convention that then changes | Design Authority | **W0 — blocking** | The whole remediation |
| Q-02 | **Is `IN-003` (988 schemas) resourced?** (`PGD-A3-15`) | Programme Director | **W0** | Every consumer in W1 |
| Q-03 | Does the event store fall within PDPA erasure scope where payloads carry personal data (§8.4)? | DPO / `SC-003` | W2 | CD-248 saga scope |
| Q-04 | Who owns the ~245 renames — module authors or Enterprise Architecture? | Chief Architect | W1 | RM-03 scheduling |
| Q-05 | Does the W5→W6 Redis→Redpanda migration need a dual-write wave, or is a cutover acceptable? | Solution Architect | W4 | `PE-005` |
| Q-06 | Should `platform.` (E3) events be exempt from `IN-003` registration to keep the catalogue navigable? | Chief Architect | W1 | Catalogue size |

---

## 12. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-A9-01 | `05-03` §4.2 status | Complete; **partial** | **Partial, declared** | 64 of 988 is 6.5%; calling it complete would make every consumer specification wrong | Heading corrected; no consumer specification written against it |
| D-A9-02 | Catalogue maintenance | Hand-maintained; **generated from the registry** | **Generated** | 988 events cannot be hand-maintained across 67 modules and 9 waves | `IN-003` is a registry with a generator, not a document |
| D-A9-03 | Naming | Convention A; convention B; both with aliases | **A (ADR-017)** | Names must survive module reorganisation; the decomposition has changed twice, the aggregates have not | ~245 renames, in W1, while free |
| D-A9-04 | Delivery semantics | Exactly-once; **at-least-once + idempotent consumers** | **At-least-once** | Exactly-once across a broker and 67 consumers is a promise that cannot be kept; idempotency can be verified | C-01 mandatory; shared library |
| D-A9-05 | Consumer implementation | Per-module; **shared library** | **Shared library** | Idempotency and retry cannot be "mostly right"; and it makes the W6 broker change a version bump | `FF-28` forbids direct client use |
| D-A9-06 | Replay safety | Trust the operator; **declared replay class with R3 refusal** | **Declared class** | A routine replay must not re-send 40,000 SMS | Every consumer declares R1/R2/R3 in `IN-003` |
| D-A9-07 | Notification | Model as an event; **treat as a command (E4)** | **Command** | A replay would re-send every notification ever sent | Notification is a consumer reaction, never a published event |

---

## 13. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The event surface is **measured**, with a reproducible method | §2.2, §10.1 — 988 counted |
| AC-02 | The naming convention is ruled, with the migration cost and timing stated | §3.2, §3.3, §3.4 |
| AC-03 | The envelope is specified with every field's purpose | §4 |
| AC-04 | Delivery semantics, ordering and idempotency are unambiguous | §4.2, §7 |
| AC-05 | The outbox is designed, including relay failure ordering and monitoring | §5 |
| AC-06 | Poison handling and replay safety are specified, with R3 protection | §7.1, §7.2 |
| AC-07 | Schema evolution has a compatibility rule and CI enforcement | §8 |
| AC-08 | `AP-01`'s "principal vs complete" question is **ruled** | §10.2 |
| AC-09 | Every safety-critical event from `AP-01` is dispositioned | §10.5 |
| AC-10 | A remediation plan exists with owners, waves and blocking flags | §10.6 |

**Definition of done.** Complete when every criterion is met, ADR-017 is ratified (Q-01), RM-01…RM-05
are executed, and `PGD-000`'s `AR-009` row is updated with a fresh enumeration timestamp. **`AR-009`
does not close `AP-01` alone — `IN-003` must publish the 988 registrations.**

---

## 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `AR-001` §7.3, §7.4 | Messaging architecture and the ASR-11 ruling |
| Upstream | **`AR-008`** §3, §4.2 | **Aggregate names are the first component of every event name.** Blocking prerequisite for RM-03 |
| Upstream | `AR-004` ADR-016, ADR-017 | Outbox and naming decisions |
| Downstream | **`IN-003`** | The registry — 988 registrations |
| Downstream | `IN-001`, `IN-006` | Integration architecture; webhook signature scheme (three unmade W1 decisions) |
| Downstream | `AR-003` DP-04, `AR-007` §7.4 | Emission design and standard |
| Downstream | `AR-012` `FF-04`, `FF-09`, `FF-28` | Coverage, residency and library checks |
| Downstream | `QA-005` | Event test suite: idempotency, ordering, schema compatibility |
| Downstream | `PE-005`, `PE-008` | Broker deployment and monitoring |
| Downstream | `SC-003`, `DA-006` | Event-store erasure scope (Q-03) |
| Lateral | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03` §4 | Envelope source; §4.2 demoted to a curated subset by D-A9-01 |
| Lateral | `../../project_content/15_Integration_and_Developer_Content/AP-003` | Content descriptions to be re-checked (RM-08) |

---

## 15. References

**Within this repository**
`../PGD-000_*.md` · `./_CATEGORY_OVERVIEW.md` · `./AR-001` · `./AR-004` · `./AR-006` · `./AR-007` ·
`./AR-008` · `./AR-012` · `../_AUDIT/PGD-AUDIT-003_*.md`

**Workspace**
`../../1000fix_ERP_Module/03_Modules/**/M*.md` §12.1, §12.3 (all 67) ·
`.../05_Cross_Cutting_Specifications/05-03` §4 · `.../02_Architecture/02-01` §7 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §12.2.6, §23 `TR-12` ·
`../../project_content/_AUDIT/AUDIT-016_Category_15_AP_Content_Audit.md` `AP-01`

**External sources**

| Source | Verified |
|---|---|
| Transactional outbox pattern (Chris Richardson, microservices.io) | 2026-08-18 |
| Hohpe & Woolf, *Enterprise Integration Patterns* — publish-subscribe, dead letter, idempotent receiver, claim check | 2026-08-18 |
| CloudEvents Specification 1.0 | 2026-08-18 |
| JSON Schema 2020-12 | 2026-08-18 |
| Redpanda BSL licence — converts to Apache-2.0 four years after each merge | 2026-08-18 |

---

## 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Measures the true event surface at **988 declared vs 64 registered**. Rules `05-03` §4.2 partial, discharging `AP-01`'s central question 45× larger than its sample. Rules convention A normative. Raises `PGD-A3-14` (`AP-01` arithmetic) and `PGD-A3-15` (`IN-003` scope unfunded) | *Pending — Design Authority not constituted* |

---

*`AR-009` · Category 02 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
