---
id: AP-003
title: Domain Event Catalogue Descriptions
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering Lead
author: Platform Engineering with Enterprise Architecture
reviewers: [CTO, Solution Architect, Enterprise Architecture, Security Lead, Data Platform Lead, QA Lead, Content Design Lead]
approver: Content Design Lead with CTO
content_class: D
purpose: >
  The authored business meaning of every domain event the estate publishes — what each event means,
  the exact condition that emits it, what a consumer may and may not infer from it, and where each
  one carries personal data. `05-03` §4.2 gives 64 event names, their producer and their consumer
  list; a name and a producer are not a contract. Without this file every one of the 67 modules and
  12 portals infers event semantics from the name, and the first time two teams infer differently
  the divergence surfaces as wrong data in a customer's hands rather than as a build failure.
traces_to: [M28, M28 FR-IPF-023, M28 FR-IPF-024, M28 FR-IPF-025, M28 FR-IPF-032, M28 FR-IPF-033, M28 §12.3, 05-02 DM-15, 05-02 §10, 05-03, 05-03 §3.3, 05-03 §4.1, 05-03 §4.2, 05-03 §4.3, 05-06 AS-08, 05-06 DI-05, 05-06 NFR-043, 05-06 NFR-086a, P04, P08, AP-001, AP-002, AP-004, AP-011, AP-012, MD-027, RP-001, RF-001]
priority: P1
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md §4.1 naming and envelope, §4.2 the 64-event principal inventory with producer and consumers, §4.3 the six consumer rules, §3.3 the eleven portal webhooks
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M28_Integration_API_and_Event_Platform.md §5.3 FR-IPF-021…FR-IPF-033, §6 T-01…T-03, §8.1 event lifecycle, §12.3 the fifteen platform events
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md DM-15 (every state change writes to the outbox in the same transaction), DM-14 and §10 sensitivity classes S0–S3
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P04_Corporate_B2B_Portal.md §12.3 and P08_Brand_Partner_Portal.md §12.3 — the consumed-event lists that diverge from the §4.2 inventory (§4.9 of this file)
    verified: 2026-08-18
    class: P1
  - source: AsyncAPI 3.0 (November 2023) and event-catalogue practice 2026 — a generated discovery layer answering "who produces this event and who consumes it", as the governance control for event-driven estates. https://www.asyncapi.com/blog/doc-event-driven-api · https://www.eventcatalog.dev/specifications/asyncapi
    verified: 2026-08-18
    class: P3
supersedes: none
review_due: 2027-02-18
---

# Domain Event Catalogue Descriptions

| Item | Value |
|---|---|
| Business events described | **64** — the `05-03` §4.2 principal inventory, in full |
| Platform events described | **15** — `M28` §12.3, in full |
| Events named elsewhere but **not in the inventory** | **26** — §4.9, the naming-divergence register |
| Producing modules | 24 of 67 |
| Envelope fields explained | 11 (§4.2) |
| Description standard | 9 required elements per entry (§4.3) |
| Publication | `AP-001` section 4, page type PT-07, generated from `fix_event_schema` with these descriptions injected |
| Wave | W3 registered · **first consumed W1** — open item `O-01` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order; §4 subdivided by volume — 79 catalogue entries do not fit one
> undifferentiated section. The **event reference table** required by `CG-009` §3 for this
> category is §4.5 and §4.6. There is no error catalogue table in this file: events do not carry
> error codes, and `AP-006` owns errors (`CP-01`).

---

## 1. Purpose

`AS-08` makes the outbox mandatory: every write path emits its domain event. `DM-15` puts the
outbox write inside the business transaction. `FR-IPF-032` publishes a living catalogue generated
from the registry. `05-03` §4.2 lists 64 events with a producer and a consumer list.

**None of that says what an event means.**

Take `service_order.completed`. `05-03` §4.2 gives producer `M01` and six consumers — `M09`,
`M15`, `M20`, `M23`, `M25`, `M27`. Six teams now have to decide independently: does *completed*
mean the technician finished the work, or that the customer accepted it, or that QC passed? Is
the invoice raised on this event or on `service_order.closed`? If the job is reopened, is there a
compensating event or does `completed` fire twice? Each answer is defensible; three of them are
wrong; and the wrong ones produce an invoice raised before the customer accepted the repair.

That is what this file prevents, and it is why the register places it at `P1`. A schema tells a
consumer the *shape* of a payload. `FR-IPF-025`'s registry enforces compatibility of that shape.
Neither tells a consumer what the event *asserts about the world* — and every integration defect
that survives contract testing lives in that gap.

**What stops working without this file.**

| Absent | Consequence |
|---|---|
| Business meaning per event | Consumers infer from the name. `05-03` §4.3 guarantees ordering per aggregate and at-least-once delivery; it guarantees nothing about interpretation, and interpretation is where the money is |
| Emission conditions | A consumer cannot tell whether an absent event means "did not happen" or "happened and was not published". The second is a defect and the first is normal, and they are indistinguishable without a stated condition |
| Consumer guidance | `05-03` §4.3 states ordering is per aggregate and never global. Consumers still write cross-aggregate assumptions, because nothing tells them which specific pairs of events are *not* ordered relative to each other |
| Personal-data annotation | Event payloads flow to the warehouse (`M62`), to dead-letter triage screens and to external webhook endpoints. `NFR-086a` requires residency classification enforced at write time; an unannotated catalogue makes egress review manual |
| Naming reconciliation | Twenty-six events are named in portal specifications and the webhook contract that do not exist in the inventory (§4.9). Each is either a missing registration or a wrong name, and today nobody knows which |

---

## 2. Scope

**In scope.** The envelope explained field by field; the description standard; authored business
meaning, emission condition and consumer guidance for all 64 business events and all 15 platform
events; ordering, idempotency and replay guidance; personal-data and residency annotation; naming
and versioning rules; the divergence register between the inventory and the specifications that
consume it; and what is deliberately not an event.

**Out of scope.**

| Out of scope | Owned by | Note |
|---|---|---|
| Event payload schemas (fields and types) | The **producing module**, registered in `fix_event_schema` | `M28` §3.2: M28 validates the envelope and the schema, never the business meaning. This file describes meaning; the module owns the fields |
| The transport, outbox, registry, subscriptions, dead letters, replay mechanics | `M28` `FR-IPF-021`…`FR-IPF-031` | Engineering capability, not content |
| Webhook delivery of events to external consumers | `AP-004` | An event and its webhook delivery are different contracts with different guarantees |
| API endpoint documentation | `AP-002` | Parallel conventions, deliberately not merged |
| State names and customer-facing state labels | `MD-027`, `VB-008` | An event is a transition; `MD-027` owns the states it moves between. This file names states; it does not define or label them |
| Which consumer reacts how | The **consuming module** | Naming a consumer is not specifying its reaction |
| Metric definitions derived from events | `RP-001` | `commission.earned` is an event; "commission earned this month" is a KPI with a formula, a grain and an owner |
| Lawful basis for events leaving the company | `AP-012` | §4.8 annotates sensitivity; `AP-012` decides disclosure |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Module developers (all 67)** | Deciding what to emit, and what they may infer from what they consume. Primary audience |
| **Portal platform team (CON-03)** | The eleven `05-03` §3.3 webhooks and their divergence from the inventory (§4.9) |
| **Data Platform (`M62`)** | Event streams are a warehouse source; grain and meaning determine the fact table |
| **Enterprise Architecture** | The registry of what the estate asserts about itself |
| **Security and DPO function** | §4.8 — which events carry personal data, and which carry residency-classified fields |
| **QA** | `TS-001` level 4 (Event) is CI-owned; the *business* assertions here are what SIT scenarios verify (`TS-003`–`TS-005`) |
| **External partners with event subscriptions** | Through `AP-001` section 4 at tier T-Auth, filtered to the events their scope permits |

---

## 4. Content

### 4.1 What a domain event is on this programme

| # | Statement | Consequence |
|---|---|---|
| **EV-01** | An event is a **statement that something has already happened**, in the past tense, about one aggregate | `FR-IPF-024` rejects imperative and present-tense names at registration. `stock.reorder` would be a command; `stock.below_reorder` is a fact |
| **EV-02** | An event is **immutable and is never deleted** before its retention expires. A correction is a **compensating event**, never an edit | `BRU-IPF-22` |
| **EV-03** | An event is emitted **only from the outbox, inside the business transaction** | `AS-08`, `DM-15`, `T-01`. If the transaction rolls back, the event never existed |
| **EV-04** | An event carries **what happened**, not **what should happen next** | `M28` §3.2 — M63 decides what happens because of an event. An event payload containing an instruction is a defect |
| **EV-05** | Delivery is **at-least-once**; exactly-once *effect* is the consumer's, achieved by recording `event_id` | `DI-05`, `T-02`, `BRU-IPF-07` |
| **EV-06** | Ordering holds **per `aggregate.id` only, never globally** | `T-03`, `BRU-IPF-08`. §4.7 lists the specific cross-aggregate pairs where this bites |
| **EV-07** | An event's **absence is not information**. A consumer must never infer a negative from an event not arriving | Delivery is at-least-once, not at-most-once, and latency is p95 ≤ 5 s (`NFR-043`) — not a bound |

### 4.2 The envelope, field by field

`05-03` §4.1 gives the envelope. This is what each field means to a consumer, which is what
`FR-IPF-023` enforces the presence of but does not explain.

| Field | Type | What it means to a consumer | Consumer obligation |
|---|---|---|---|
| `event_id` | UUID | The unique identity of **this publication**. Two deliveries of the same event share it | **Record it and ignore duplicates.** This is the entire idempotency mechanism (`BRU-IPF-07`) |
| `event_type` | `<aggregate>.<past-tense-verb>` | The catalogue key. Resolves to exactly one entry in §4.5 or §4.6 | Route on this, never on payload shape |
| `schema_version` | e.g. `1.2` | The payload contract version. Changes within a version are **additive only** | Tolerate unknown fields; never fail on an added one (`BRU-IPF-06`) |
| `occurred_at` | RFC 3339 UTC | When the **business fact** occurred — not when it was published and not when it was delivered | Use for business time. Use delivery time for nothing except diagnostics |
| `company_id` | int | The legal entity (`M65`, `AS-03`) | Multi-entity consumers must scope on it. Single-entity consumers must still not assume `1` |
| `operating_unit_id` | int | The branch or operating unit | `T2` isolation tier (`05-04` §4). A consumer widening beyond it is a scope defect |
| `actor` | `{type, id}` | Who or what caused it — `user`, `system`, `integration`, `job` | Never assume `user`. A large share of events are system-actored, and audit trails that assume a human are wrong at scale |
| `correlation_id` | UUID | The single identifier tying this event to the originating request across every hop (`NFR-092`, `T-05`) | **Propagate it into everything you emit as a result.** A consumer that drops it breaks the trace for everyone downstream |
| `causation_id` | UUID | The `event_id` of the event that directly caused this one | Use to build causal chains. Distinct from `correlation_id`: correlation is the whole journey, causation is the previous step |
| `aggregate` | `{type, id}` | The thing the event is about; the **partition key** | Ordering is guaranteed within one `aggregate.id` and nowhere else |
| `payload` | object | The module-owned business content | Read only the fields you need. Depending on a field you do not need makes an additive change feel breaking |

> **`correlation_id` and `causation_id` are the two fields most often dropped by consumers and
> are the two that make a 67-module estate debuggable.** `M28` `AC-19` requires end-to-end
> traceability by a single correlation id and `KPI` targets 100% of requests traceable. A
> consumer that emits without propagating is why that figure will not reach 100%.

### 4.3 The description standard — nine required elements

Every catalogue entry carries these nine. Entries in §4.5 present the first six in table form and
carry the remaining three in the group notes, because presenting nine columns produces a table
nobody reads.

| # | Element | Why it is required |
|---:|---|---|
| 1 | **Event type** | The registry key |
| 2 | **Producer** | The single owning module (`05-03` §4.2) |
| 3 | **Business meaning** — one sentence, stating what is now true | The gap this file exists to fill |
| 4 | **Emitted when** — the exact condition, in terms of a state transition or a business act | Distinguishes "did not happen" from "not published" |
| 5 | **Consumer guidance / caution** — what may *not* be inferred, and the specific trap | The defect-prevention element |
| 6 | **Personal data** — S-class of the most sensitive field, and residency flag | `05-02` §10, `NFR-086a`, and the input to `AP-012` |
| 7 | **Ordering partner** — the events it must not be assumed ordered against | `EV-06` made concrete |
| 8 | **Compensating event** — what reverses it, or "none — irreversible" | `EV-02` made actionable |
| 9 | **Principal consumers** | `05-03` §4.2, carried for traceability, not restated per row |

### 4.4 How to read §4.5

Six columns. Producer and principal consumers come from `05-03` §4.2 and are not re-derived here.
**PD** is the personal-data column: `—` none, `S1`…`S3` per `05-02` §10, and `R` appended where
the payload can carry a residency-classified field (`NFR-086`).

Where a row's **caution** is bold, that caution has a named failure mode that has been argued for
in this programme's own documents, and the bolding is deliberate.

### 4.5 Business event catalogue — 64 events

#### 4.5.1 Service order — `M01`, 8 events

| Event | Business meaning | Emitted when | Consumer guidance / caution | PD |
|---|---|---|---|:--:|
| `service_order.created` | A service order now exists and is the system of record for this piece of work | An order is persisted in `draft` from any channel — portal, branch, contact centre, corporate bulk, marketplace | **Nothing is priced, covered or scheduled yet.** Warranty, contract and price are unresolved until `classified`. A consumer that reads a price here reads a default | S2 |
| `service_order.classified` | Coverage and commercial treatment are now decided: warranty, contract, chargeable, or a combination | Classification completes against `M08` entitlement, `M09` warranty and `M11` pricing | This is the first event on which a financial decision is safe. It may arrive seconds or minutes after `created`; it is **not** ordered against `work_order.*` on a different aggregate | S1 |
| `service_order.estimated` | An estimate has been produced and is awaiting a decision | An estimate is issued to the customer for approval | An estimate is not revenue and not a commitment. It may be superseded by a later `estimated` on the same order — the last one governs | S1 |
| `service_order.approved` | The customer has authorised the work at the stated value | The customer accepts, part-accepts or the approval threshold in `05-04` §7 is satisfied | **Part-approval is an approval.** A consumer treating this as "full estimate accepted" over-commits parts and labour. The payload states what was approved | S1 |
| `service_order.on_hold` | Work has stopped for a stated reason and the SLA clock may be paused | The order enters a hold state — awaiting parts, awaiting customer, awaiting approval, awaiting third party | Hold does not always pause SLA; the pause rule is `MD-028`'s, per hold reason. **Do not infer a clock pause from this event alone** | — |
| `service_order.completed` | The work is finished and has passed internal quality control | The order reaches `completed` after QC, **before** customer acceptance and handover | **This is not customer acceptance and not the invoicing trigger on its own.** Six modules consume it; the distinction between this and `closed` is the most consequential in the catalogue and is stated at §4.7 | S1 |
| `service_order.closed` | The order is finished, handed over and financially settled or committed | The order reaches `closed` after handover and settlement or credit terms | Terminal for operational purposes. Reopening produces a **new** order linked to this one, never a re-`created` on the same aggregate | S1 |
| `service_order.cancelled` | The order will not be delivered | Cancellation is accepted at any pre-`completed` state | Compensating for `created`, `approved` and any reservation made against them. Consumers holding reservations **must** release on this event | — |

**Ordering partners for this group.** `service_order.*` is partitioned on the order id; `work_order.*`
is partitioned on the work order id. **They are different aggregates and are not ordered relative to
each other.** A consumer may legitimately receive `work_order.completed` before
`service_order.completed`, and must not treat the reverse as an invariant.

**Compensating events.** `cancelled` compensates `created` and `approved`. Nothing compensates
`completed` or `closed`; a reversal is a new order plus a credit note (`credit_note.issued` —
see §4.9, unregistered).

#### 4.5.2 Work order and technician — `M02`, 5 events

| Event | Business meaning | Emitted when | Consumer guidance / caution | PD |
|---|---|---|---|:--:|
| `work_order.assigned` | A named technician is now responsible for this work | Dispatch assigns, reassigns or auto-assigns | Reassignment emits again. **The latest event governs**; a consumer keeping the first assignment shows the customer the wrong technician | S1 |
| `work_order.started` | Work has physically begun | The technician starts work on site or at the bench | Started ≠ arrived. In on-site modes `technician.arrived` precedes it, sometimes by an hour | — |
| `work_order.completed` | The technician's task is finished | The technician marks the work order complete, with evidence captured | Does **not** imply `service_order.completed`; an order may hold several work orders. Also does not imply QC passed | S1 |
| `technician.dispatched` | A technician is on the way, with an ETA | Dispatch confirms travel has begun | Customer-visible. Feeds `05-03` §3.3's portal webhook of the same name. ETA is a projection and is revised by `technician.location_updated` (§4.9, unregistered) | S1 |
| `technician.arrived` | The technician is at the customer location | Arrival is confirmed, by geofence or by the technician | Arrival stops the travel clock and starts the on-site clock. In offline conditions this can arrive **late and out of order relative to wall time** — `occurred_at` is authoritative, not delivery time | S1 R |

> **Offline caution for this whole group.** `P02` guarantees 24 hours of offline operation
> (`NFR-047`). Every `M02` event can therefore be published **hours after it occurred**, in a
> burst, on reconnection. `occurred_at` is the business time; a consumer computing a duration from
> delivery time will report field durations that are wrong by the length of the outage.

#### 4.5.3 SLA and rework — `M01`, 3 events

| Event | Business meaning | Emitted when | Consumer guidance / caution | PD |
|---|---|---|---|:--:|
| `sla.warning` | An SLA target is approaching and is at risk | The warning threshold in `MD-028` is crossed | A warning is not a breach. Consumers escalating on this must not also escalate on `breached` for the same order, or every at-risk job escalates twice | — |
| `sla.breached` | An SLA target has been missed | The target time passes with the target unmet | **Carries contractual and financial consequence** — service credits under `LG-015`. Consumed by `M08`, `M23`, `M20`. A duplicate delivery must not produce a duplicate credit; idempotency on `event_id` is not optional here | — |
| `rework.detected` | Work previously reported complete has had to be redone | A return visit or reopened order is classified as rework by `M23`'s rule set | Rework attribution is a quality and incentive input (`M21`, `M26`). **It is not a defect claim against a named technician until `M23` completes its process** — consumers must not surface it as one | S1 |

#### 4.5.4 Logistics and custody — `M03`, 3 events

| Event | Business meaning | Emitted when | Consumer guidance / caution | PD |
|---|---|---|---|:--:|
| `consignment.created` | A physical movement of a customer's device or of parts has been booked | A consignment is raised for pick-up, delivery or inter-branch transfer | Booking is not collection. The courier may reject or fail to collect | S2 R |
| `consignment.custody_transferred` | Legal and physical custody of the item has moved between named parties | A custody handover is recorded with evidence | **The chain-of-custody event.** `G3-07` requires unbroken custody with zero exceptions; a gap in this sequence is an audit finding, not a data gap. Consumers must treat an out-of-sequence transfer as an exception, not reorder it | S2 |
| `consignment.delivered` | The item has reached its destination and been accepted | Delivery is confirmed with proof | Terminal for the consignment aggregate. Feeds rental return, invoice and customer notification | S2 R |

#### 4.5.5 Inventory and procurement — `M15`, `M16`, 5 events

| Event | Business meaning | Emitted when | Consumer guidance / caution | PD |
|---|---|---|---|:--:|
| `part.consumed` | A specific part, by serial where serialised, has been used on a job | A part is issued and consumed against a work order | The financial and warranty-claim trigger for parts. **Consumption is not reversible by a second event of this type** — a return is a separate movement | — |
| `stock.below_reorder` | A stock item at a location has fallen below its reorder point | The balance crosses the point downward | Fires **once per crossing**, not per transaction below the point. A consumer raising a requisition per event is correct; one raising per stock movement is not | — |
| `stock.count_variance` | A physical count disagrees with the system balance | A count is posted with a difference | Consumed by `M19` and `M23`. Variance is a fact; whether it is a loss is a later determination | — |
| `goods.received` | Goods have physically arrived and been accepted into a location | Receipt is posted against a purchase order | Part of the three-way match (`G3-06`). Receipt is not inspection; a receipt may later be rejected | — |
| `purchase_order.issued` | A purchase order has been sent to a supplier and is binding | The PO is approved and issued | Visible to the supplier in `P05`. **Amendments emit a new event; the payload carries the revision** — a consumer keying only on PO number will overwrite | — |

#### 4.5.6 Asset — `M17`, 3 events

| Event | Business meaning | Emitted when | Consumer guidance / caution | PD |
|---|---|---|---|:--:|
| `asset.registered` | A device now exists in the registry with an owner and an identity | A device is registered at intake, purchase, estate load or trade-in | The same physical device may be registered more than once over its life under different owners; identity is by serial, ownership is a relationship | S2 R |
| `asset.status_changed` | The asset's lifecycle state has moved | Any registry state transition — in service, in repair, retired, disposed, rented, refurbished | **The most broadly consumed event in the catalogue after `service_order.*`.** Consumers must read the target state from the payload, never infer it from the fact of a change | S1 |
| `asset.health_degraded` | Telemetry or diagnostics indicate the asset's condition has worsened materially | A health index crosses a threshold, or a predictive model raises confidence above the configured level | A prediction, not a fault. Consumed by `M05`, `M08`, `M26`. **Surfacing it to a customer as a fault is a trust failure**; `P04` presents it as an indication | S1 |

#### 4.5.7 Contract and entitlement — `M08`, 4 events

| Event | Business meaning | Emitted when | Consumer guidance / caution | PD |
|---|---|---|---|:--:|
| `contract.activated` | A contract is live and its entitlements are consumable from the stated date | Activation completes, on or after the effective date | Activation may be back-dated; use `payload.effective_from`, not `occurred_at`, for coverage decisions | S1 |
| `contract.entitlement_consumed` | A unit of entitlement — a visit, an incident, a covered repair — has been used | Consumption is posted against the contract | The balance is on the aggregate; **this event carries the delta, not the balance.** A consumer summing deltas after a replay will double-count unless it is idempotent on `event_id` | — |
| `contract.expiring` | A contract will expire within the notice horizon | The horizon is crossed | Fires once per horizon per contract. Feeds renewal in `M10`, `M27` and the portal webhook of the same name | S1 |
| `contract.terminated` | The contract is no longer in force | Termination is recorded, for any reason including expiry without renewal | Consumers holding entitlement caches **must** invalidate. Termination does not retroactively invalidate work already covered | S1 |

#### 4.5.8 Warranty — `M09`, 3 events

| Event | Business meaning | Emitted when | Consumer guidance / caution | PD |
|---|---|---|---|:--:|
| `warranty_claim.created` | A claim has been raised internally against a brand | The claim is created, automatically or manually, from a warranty-classified job | Internal only. **`P08` must not show it**; the brand sees a claim on submission, not on creation. `G4-01` times creation within 24 h | S1 |
| `warranty_claim.submitted` | The claim has been sent to the brand and their clock has started | Submission completes with a complete evidence pack | The externally visible event. `G4-01` times submission within 72 h. Resubmission after an information request emits again | S1 |
| `warranty_claim.decided` | The brand has approved, part-approved or rejected the claim | A decision is recorded, by API or by portal entry | **Part-approval is a decision.** Consumers treating this as binary mis-post the receivable. Feeds `M19`, `M20`, `M23` | S1 |

#### 4.5.9 Billing and payment — `M20`, 4 events

| Event | Business meaning | Emitted when | Consumer guidance / caution | PD |
|---|---|---|---|:--:|
| `invoice.created` | A legally issued invoice exists with a statutory document number | The invoice is posted and its Mushak-compliant number is allocated (`MD-040`) | **The document number is allocated here and is gap-free and immutable.** A consumer must never regenerate or reformat it. Feeds the portal webhook of the same name | S2 |
| `invoice.paid` | An invoice is fully settled | Payment application brings the balance to zero | Partial payments do **not** emit this. There is **no registered partial-payment event** — see §4.9 `O-03` | S2 |
| `payment.failed` | An attempted payment did not succeed | A gateway or bank returns a definitive failure | Not the same as pending or unknown. **A timeout is not a failure**; `AP-009` §4.6 covers indeterminate outcomes, which are the dangerous case | S2 |
| `refund.processed` | Money has been returned to a payer | A refund is executed and confirmed by the rail | Compensating for `invoice.paid` in accounting terms, but **not** its reversal — the invoice remains issued. Reversal of an invoice is a credit note | S2 R |

#### 4.5.10 Marketplace and settlement — `M12`, `M20`, 6 events

| Event | Business meaning | Emitted when | Consumer guidance / caution | PD |
|---|---|---|---|:--:|
| `commission.earned` | 1000FiX has earned commission on a marketplace transaction | The transaction reaches the state at which commission is recognised | Recognition timing is `M53`'s rule, not the event's. Consumers must not re-derive it | — |
| `payout.executed` | Money has left 1000FiX to a seller | A payout is executed on the payout rail | **Financially irreversible in practice.** `G7-02` requires 100% payout accuracy with zero unexplained variance. Idempotency here is a money control, not a hygiene rule | S2 R |
| `seller.approved` | A seller may transact on the marketplace | Approval completes after verification (`INT-034`, `INT-035`) | Approval is scoped by category (`MD-018`); a seller approved in one category is not approved in all | S2 R |
| `seller.suspended` | A seller may no longer transact | Suspension is applied, for quality, dispute or compliance reasons | Consumers must stop routing work **immediately**. Suspension does not cancel work already awarded | S1 |
| `review.published` | A customer review is now publicly visible | Moderation passes and the review is published | Published, not submitted. A submitted review that fails moderation emits nothing — `EV-07` applies | S1 |
| `dispute.raised` | A party has formally disputed a transaction | A dispute is opened by customer or seller | **Holds payouts** (`P07`). A consumer releasing a payout after this event is the specific failure `EO-013` and `G7-04` exist to prevent | S1 |

#### 4.5.11 Circular and asset-based business — `M13`, `M14`, `M06`, `M18`, 6 events

| Event | Business meaning | Emitted when | Consumer guidance / caution | PD |
|---|---|---|---|:--:|
| `rental.dispatched` | A rental unit has left for the customer | Dispatch of the rental asset is confirmed | Starts the billing clock per the rental plan. Not the same as delivery | S2 R |
| `rental.returned` | The rental unit is back in 1000FiX custody | Return is received and recorded | Stops the billing clock. **Damage assessment is a separate later determination**; consumers must not bill damage from this event | S2 |
| `tradein.accepted` | A customer's device has been accepted in trade and title has passed | The trade-in is accepted and the customer compensated or credited | Triggers the wipe obligation. **A traded-in device must not be resold before `wipe.certified`** | S2 R |
| `refurb.graded` | A refurbished unit has a final condition grade and is saleable at that grade | Grading completes | The grade governs price and warranty. Re-grading emits again; the latest governs | — |
| `wipe.certified` | Customer data on a device has been destroyed to the certified standard and evidence exists | A certified wipe completes and its certificate is issued | **A hard gate.** `G6-02` requires zero units released without a destruction certificate. Consumers releasing stock must key on this event, not on `tradein.accepted` | S3 R |
| `ewaste.disposed` | An item has been disposed of through a certified route and a disposal certificate exists | Disposal is confirmed by the recycling partner | Statutory record (`LG-018`). `G8-04` requires zero uncertified disposals | S1 |

#### 4.5.12 Managed services — `M05`, 2 events

| Event | Business meaning | Emitted when | Consumer guidance / caution | PD |
|---|---|---|---|:--:|
| `alert.raised` | A monitored client asset or service has raised a condition requiring attention | Monitoring detects a condition above the alerting threshold | High volume. **Consumers must expect duplicates and storms**; suppression is `M05`'s, not the consumer's | S1 |
| `msp_ticket.resolved` | A managed-services ticket has been resolved | Resolution is recorded and accepted | Feeds SLA measurement and the monthly service report. Resolved ≠ closed; reopening emits nothing on this type | S1 |

#### 4.5.13 People — `M21`, `M22`, 5 events

| Event | Business meaning | Emitted when | Consumer guidance / caution | PD |
|---|---|---|---|:--:|
| `employee.joined` | A person is now an employee with an effective start date | The employee record reaches active on the start date | **Triggers identity creation and access provisioning** in `M29` (`05-04` §9). Back-dated joins are possible; use the effective date | S3 R |
| `employee.left` | A person is no longer an employee | The leaver process records the last working day | **`05-04` §9 requires all access revoked within one hour** and zero orphaned accounts beyond 24 hours. This event is the control's trigger and its latency is a security metric | S3 R |
| `certification.expiring` | A technician certification will lapse within the notice horizon | The horizon is crossed | Feeds dispatch planning, `P08` and `M27` | S1 |
| `certification.expired` | A certification has lapsed | The expiry date passes | **A hard dispatch block** (`05-03` §4.2 names `M02` as the sole consumer, "hard dispatch block"; `BRU-SRM-09`). A consumer treating this as advisory allows an uncertified technician onto brand warranty work | S1 |
| `payroll.approved` | A payroll run is authorised for disbursement | HR Manager and CFO both approve (`05-04` §7, `SOD-03`) | Feeds `M19` posting and `M24` records. **Never emitted before both approvals** — a single-approval emission is a segregation-of-duties breach | S3 R |

#### 4.5.14 Quality and customer — `M23`, `M07`, 5 events

| Event | Business meaning | Emitted when | Consumer guidance / caution | PD |
|---|---|---|---|:--:|
| `nonconformance.raised` | A process or output has departed from a specified requirement | An NC is raised under `M23`'s rules | **A non-conformance is not a defect and not an incident.** `TS-001` §4.10 holds the three-way boundary; consumers must not merge the records | S1 |
| `capa.closed` | A corrective or preventive action has been completed and verified | CAPA closure is verified | Closure requires verification, not just action. Visible to brands in `P08` | — |
| `complaint.raised` | A customer has formally complained | A complaint is registered through any channel | Producer is recorded in `05-03` §4.2 as `M07/M23` — **the only dual-producer row in the inventory**, and `FR-IPF-024` registration assumes one producing module. Open item `O-04` | S2 |
| `customer.registered` | A customer party now exists as a golden record | Registration completes with matching and deduplication applied (`M33`) | Registration is not the first order; a walk-in customer may be registered at intake | S2 R |
| `customer.merged` | Two customer records have been resolved into one; one identifier is now retired | A merge is executed after survivorship rules run | **The highest-blast-radius event in the catalogue.** `05-03` §4.2 lists its consumers as "all consumers holding customer ids". Every consumer holding a customer identifier **must** remap. A consumer that ignores it holds a dangling reference forever | S2 R |

#### 4.5.15 Pricing and intelligence — `M11`, `M26`, 2 events

| Event | Business meaning | Emitted when | Consumer guidance / caution | PD |
|---|---|---|---|:--:|
| `price_book.published` | A price book version is effective from a stated date | A price book is published with an effective date | **Publication is not immediate effect.** Use `payload.effective_from`. Caches keyed on publication time price the wrong work | — |
| `model.prediction_made` | An ML model produced a prediction that influenced or may influence a decision | A model in `M26` returns a prediction that is recorded | Consumed by the consuming module **and the audit trail**. A prediction is an input to a decision, never the decision (`05-04` §5 restricts `model_confidence` and `model_features` to `R02`, `R33` and model owners) | S1 |

### 4.6 Platform event catalogue — 15 events

`M28` §12.3: *"M28 publishes only platform events. It transports every business event but authors
none."* These are operational, tier `T-Int` in `AP-001` §4.5, and are **never** delivered to an
external subscriber.

| Event | Business meaning | Emitted when | Consumer guidance / caution |
|---|---|---|---|
| `platform.event_dead_lettered` | An event could not be delivered to a consumer after three retries | Retries are exhausted (`AUT-IPF-03`) | **A dead letter unresolved beyond one hour is an incident** (`BRU-IPF-14`), not a backlog item. The payload is masked for S3 and residency-classified fields (`M28` §13) |
| `platform.event_replayed` | A dead-lettered event has been re-delivered | An administrator authorises replay | Recorded with who and why. Replay targets **one consumer only**; other consumers are unaffected |
| `platform.integration_degraded` | An integration has breached a monitoring threshold but is still serving | Error rate > 2% over 5 min, or availability < 99% over 15 min (`05-03` §7) | Degraded is not failed. Alerting on both as if identical produces alert fatigue and is why `OPS-03` exists |
| `platform.integration_failed` | An integration is not serving and its fallback is engaged | The circuit opens or an outage is confirmed | Carries the fallback engaged. Feeds `M27` user messaging |
| `platform.integration_recovered` | An integration is serving again and queued work has been replayed | Probes succeed and the error rate normalises | Recovery includes replay of queued work; consumers should expect a **burst** after this event |
| `platform.fallback_engaged` | A registered fallback is now handling traffic for a failed integration | Automatic fallback engages (`FR-IPF-043`) | Distinct from `integration_failed`: an integration can fail with **no** fallback available, and that is the worse case |
| `platform.api_deprecated` | An API version is deprecated and its sunset clock has started | Deprecation is marked (`AUT-IPF-08`) | Six-month clock (`API-02`). Feeds `AP-011` notice content and the `AP-001` §7 register |
| `platform.api_version_retired` | An API version no longer exists | Retirement completes after sunset with no live traffic | Cannot fire while a registered consumer is still calling (`BRU-IPF-05`, `AUT-IPF-09`) |
| `platform.schema_registered` | An event schema version is registered and in force | Registration passes compatibility checks | Notifies producing and consuming teams. A rejected registration emits nothing — the build fails instead |
| `platform.rate_limit_breached` | A consumer has exceeded its rate limit | The limit is exceeded (`AUT-IPF-10`) | Sustained breach is a capacity or abuse signal, not a single-request event. Feeds `M29` anomaly detection |
| `platform.credential_expiring` | An integration credential expires within 30 days | The 30-day horizon is crossed (`AUT-IPF-15`) | Escalates at 7 days. An expired credential on a `P0` integration is a business outage |
| `platform.webhook_endpoint_disabled` | An outbound webhook endpoint has been disabled after five consecutive failures | Fifth consecutive delivery failure (`AUT-IPF-14`, `BRU-IPF-18`) | The consumer's own owner is notified. **Re-enabling is manual by design** — see `AP-004` §4.6 |
| `platform.reconciliation_divergence` | A nightly reconciliation found a difference between systems | Divergence is detected (`AUT-IPF-17`, `DI-07`) | **Divergence is investigated, never absorbed** (`BRU-IPF-19`). Target is zero |
| `platform.sync_conflict_resolved` | An offline sync conflict was detected and resolved by policy | Conflict resolution completes (`FR-IPF-049`) | Also surfaced to the user in the app (`UI-009`). Consumed by the originating module and `M23` as a quality signal |
| `platform.direct_access_violation` | A build attempted direct cross-module table access | Static analysis detects it (`AUT-IPF-19`, `AS-01`) | **Fails the build.** The event is the record, not the control |

### 4.7 The `completed` versus `closed` distinction, and other ordering traps

Six specific traps. Each is a place where a reasonable inference is wrong.

| # | Trap | The wrong inference | The rule |
|---|---|---|---|
| **T-01** | `service_order.completed` vs `closed` | "Completed means we can invoice" | `completed` is work finished and QC passed. `closed` is handed over and settled. **`M20` raises the invoice on the trigger `M20` declares, not on whichever of these arrives first.** Six modules consume `completed`; only some may act financially |
| **T-02** | `work_order.completed` before `service_order.completed` | "The order is finished" | Different aggregates, no ordering guarantee, and an order may hold several work orders |
| **T-03** | `service_order.approved` | "The whole estimate was accepted" | Part-approval is an approval. Read the payload |
| **T-04** | `invoice.paid` absent | "Not paid" | `EV-07`. Also: partial payment emits nothing at all today (`O-03`) |
| **T-05** | `certification.expired` | "Advisory; the dispatcher will notice" | Hard block. `05-03` §4.2 gives it a single consumer with a parenthetical instruction — the only such row in the inventory |
| **T-06** | `customer.merged` | "Our copy is fine; we'll pick it up on the next read" | Every consumer holding a customer identifier must remap. There is no next read for a retired identifier |

**Why `completed` and `closed` deserve their own trap entry.** They are the only pair in the
inventory where two events on the **same aggregate** are both plausibly the financial trigger,
both have six-plus consumers, and the wrong choice produces an invoice for work the customer has
not accepted. The rule above does not *decide* the trigger — that is `M20`'s — it removes the
assumption that the catalogue has decided it. Recorded as `O-02`.

### 4.8 Personal data in event payloads

`05-02` §10 classifies fields S0–S3. `NFR-086` restricts residency-classified fields. Event
payloads reach three places that are easy to forget: the **warehouse** (`M62`), **dead-letter and
trace views** (`M28` §13), and **external webhook endpoints** (`AP-004`).

| # | Rule |
|---|---|
| **PD-01** | Every catalogue entry carries an S-class and a residency flag (§4.5 **PD** column). An entry without one cannot be registered |
| **PD-02** | An event payload carries **identifiers, not personal data**, wherever a consumer can resolve the identifier through an authorised API. This is `IP-10` minimisation applied to the bus |
| **PD-03** | **No event payload contains a residency-classified field value** — NID, passport, TIN, biometric template, recovered-data index, seller KYC document. It carries a reference. Fifteen entries in §4.5 are flagged `R` because they concern an aggregate that *has* such a field, not because the payload carries one |
| **PD-04** | Dead-letter and trace views **mask** S3 and residency-classified fields (`M28` §13, `NFR-086`, `NFR-061`). An administrator triaging a failure sees the envelope and the failure, not the customer's identity |
| **PD-05** | An event delivered to an **external** subscriber is subject to `AP-012`. There is no event whose internal payload may be forwarded unfiltered to an external endpoint |
| **PD-06** | Event **retention** is unresolved. `M28` Q-05 asks what the retention period is and whether it differs for events carrying personal data under PDPA 2026 minimisation. `BRU-IPF-22` forbids deletion before retention expires — **a retention period that does not exist cannot expire**, so today no event can lawfully be deleted and none can be lawfully retained on a stated basis. Open item `O-05` |

**The counted position.** Of the 64 business events: **17 carry no personal data**, 24 are `S1`,
**19 are `S2`**, 4 are `S3`, and **15 concern an aggregate holding a residency-classified field**.
Counted from §4.5, 2026-08-18, per `CP-11`.

### 4.9 The naming-divergence register — 26 events named elsewhere and not registered

**This is the most operationally significant finding in this file.** Extraction of every event
name used in `05-03` §3.3, `P04` §12.3 and `P08` §12.3 against the `05-03` §4.2 inventory,
2026-08-18:

| # | Named in | Event name used | In §4.2? | Nearest inventory event | Assessment |
|---:|---|---|:--:|---|---|
| 1 | `05-03` §3.3 webhook | `service_order.status_changed` | ✗ | the eight specific `service_order.*` | Either a coarse portal-facing projection of the eight, or a missing registration |
| 2 | `05-03` §3.3, `P04` | `technician.location_updated` | ✗ | — | Explicitly throttled in §3.3. **High volume; if it is a domain event it changes the throughput envelope** (`T-07`, 5,000/min at W8) |
| 3 | `05-03` §3.3 | `estimate.issued` | ✗ | `service_order.estimated` | Same fact, two names |
| 4 | `05-03` §3.3, `P08` | `payment.received` | ✗ | `invoice.paid` | Different facts — a payment can be received without settling an invoice |
| 5 | `05-03` §3.3 | `loyalty.points_changed` | ✗ | — | `M10` produces no event in the inventory at all |
| 6 | `05-03` §3.3 | `consignment.status_changed` | ✗ | the three `consignment.*` | As row 1 |
| 7 | `05-03` §3.3 | `catalogue.updated` | ✗ | `price_book.published` | Catalogue and price book are different aggregates (`M37` vs `M11`) |
| 8 | `P04` §12.3 | `sla.at_risk` | ✗ | `sla.warning` | Same fact, two names |
| 9 | `P04` §12.3 | `invoice.issued` | ✗ | `invoice.created` | Same fact, two names |
| 10 | `P04` §12.3 | `credit_note.issued` | ✗ | — | **No credit-note event exists**, yet credit notes have an approval matrix (`05-04` §7) and a dispute flow (`P04`) |
| 11 | `P04` §12.3 | `contract.renewal_due` | ✗ | `contract.expiring` | Same fact, two names |
| 12 | `P04` §12.3 | `entitlement.threshold_crossed` | ✗ | `contract.entitlement_consumed` | Different facts — consumption is a delta, threshold is a condition |
| 13 | `P04` §12.3 | `asset.estate_reconciled` | ✗ | — | `M17` estate reconciliation produces no registered event |
| 14 | `P04` §12.3 | `asset.alert_raised` | ✗ | `alert.raised` | Aggregate prefix differs; `05-03` §4.2 puts the producer at `M05`, `P04` at `M48` |
| 15 | `P04` §12.3 | `project.milestone_reached` | ✗ | — | `M67` produces no event in the inventory |
| 16 | `P08` §12.3 | `claim.submitted` | ✗ | `warranty_claim.submitted` | Aggregate prefix differs |
| 17 | `P08` §12.3 | `claim.evidence_incomplete` | ✗ | — | **Suppresses submission in `P08`** — a control with no registered event |
| 18 | `P08` §12.3 | `stock.consignment_consumed` | ✗ | `part.consumed` | Consignment stock is a distinct custody model |
| 19 | `P08` §12.3 | `stock.consignment_reconciled` | ✗ | — | Monthly brand reconciliation pack, `P08` `FR-POR-242` |
| 20 | `P08` §12.3 | `stock.rtv_raised` | ✗ | — | Defective consignment returns |
| 21 | `P08` §12.3 | `recall.execution_updated` | ✗ | — | **Recall execution status** — a safety-relevant flow with no registered event |
| 22–26 | `P04`, `P08` §12.2 | Five write-back "commands" | n/a | — | Commands, not events; listed for completeness so a future reader does not add them to the inventory |

**Twenty-one distinct event names are consumed by specifications and do not exist in the
inventory.** They fall into three classes and the classes need different remedies:

| Class | Count | Examples | Remedy |
|---|---:|---|---|
| **Same fact, two names** | 5 | `estimate.issued`, `sla.at_risk`, `invoice.issued`, `contract.renewal_due`, `claim.submitted` | Correct the specification to the inventory name. Free |
| **Coarse projection of finer events** | 2 | `service_order.status_changed`, `consignment.status_changed` | Decide whether the portal contract receives a projection or the fine-grained set. **A projection is a legitimate design; an undocumented one is not** |
| **Genuinely missing registration** | 14 | `credit_note.issued`, `loyalty.points_changed`, `claim.evidence_incomplete`, `recall.execution_updated`, `asset.estate_reconciled`, `project.milestone_reached`, `stock.consignment_*`, `stock.rtv_raised`, `entitlement.threshold_crossed`, `technician.location_updated`, `catalogue.updated`, `asset.alert_raised` | Register, or the consuming specification is describing behaviour the platform will not provide |

> **`05-03` §4.2 is headed "Event Inventory (Principal Events)".** "Principal" is doing a great
> deal of work in that heading. If the inventory is deliberately partial, the catalogue is not a
> catalogue and `FR-IPF-032`'s living catalogue will be the first document that reveals the true
> count. If it is meant to be complete, fourteen registrations are missing. **This file cannot
> decide which**, and records it as `O-06` — the first finding of the Category 15 audit.

### 4.10 Naming and versioning

| # | Rule |
|---|---|
| **NM-01** | `<aggregate>.<past-tense-verb>`, lower snake case (`05-03` §4.1). Enforced at registration (`FR-IPF-024`) |
| **NM-02** | The aggregate prefix is the **controlled term** for the business object (`CG-004`), not the module code and not the table name. `warranty_claim`, not `claim` and not `wty` |
| **NM-03** | One fact, one event type. Two names for one fact is the defect §4.9 counts five times |
| **NM-04** | An event name is **permanent**. Renaming is a breaking change requiring a new `schema_version` and a dual-publish period (`BRU-IPF-06`) |
| **NM-05** | Additive changes within a `schema_version` only. A removed or retyped field requires a new version (`FR-IPF-025`) |
| **NM-06** | A new version requires a **dual-publish period** with both live, and the period is stated in `fix_event_schema.dual_publish_until` |
| **NM-07** | Description changes are **not** schema changes. Correcting the business meaning of an event does not version it — but it does require a `RF-006` entry, because consumers may have built on the prior reading |
| **NM-08** | `AP-011` owns the notice content for any change under `NM-04`, `NM-05` or `NM-06` |

### 4.11 What is deliberately not an event

Recorded so the boundary is not re-litigated per module.

| Not an event | Why | Where it lives |
|---|---|---|
| A user viewing a record | Not a state change | Access log (`M29`) |
| A validation failure on input | Nothing happened | API error (`AP-006`) |
| A workflow step firing | Workflow is `M63`'s; the event is what caused it | `M63` |
| A scheduled job running | Operational telemetry | `M30`, `OPS-05` |
| A report being generated | Not a business fact | `M25` |
| A field edit with no state transition | `DM-15` binds the outbox to state change | Chatter / audit trail (`AS-02`) |
| An external system's internal state | We do not observe it | The integration's own contract |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `05-03` §4.1, §4.2, §4.3 | The envelope, the 64-event inventory and the consumer rules this file describes |
| `M28` `FR-IPF-023`…`FR-IPF-025`, `FR-IPF-032` | Envelope enforcement, naming enforcement, the registry and the generator that publishes these descriptions |
| `M28` `FR-IPF-033` | Contract testing per producer/consumer pair — the mechanism that would catch a meaning divergence, if meaning were testable |
| `05-02` DM-15, DM-14, §10 | The outbox binding and the sensitivity classes §4.8 annotates against |
| `MD-027` | State names. Every "emitted when" that names a state resolves there |
| `AP-002` | Parallel conventions for REST; `AR-03` requires endpoints to name the events they emit, resolving here |
| `AP-004` | Webhook delivery of a subset of these events to external consumers |
| `AP-011` | Notice content for `NM-04`…`NM-06` changes |
| `AP-012` | Disclosure decisions for any event leaving the company |
| `RF-001` | The controlled-term register `NM-02` resolves against — **unwritten** |
| `RP-001` | KPI definitions built on these events; the grain of a fact table is decided by the event's meaning |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per wave, as each wave's modules register their events |
| Trigger for out-of-cycle review | Any new event registration · any `schema_version` increment · resolution of `O-06` · a consumer reporting a meaning divergence · a change to `05-03` §4.2 |
| Owner | Platform Engineering Lead, with Enterprise Architecture accountable for meaning where two modules disagree |
| Change control | A change to a **business meaning** or an **emission condition** requires the producing module's owner and Enterprise Architecture, and a `RF-006` entry (`NM-07`). Adding a catalogue entry requires the producing module's owner only |
| Version pinning | Pinned to `schema_version` per event, not to a document version (`CG-006` §5) |
| Generation | Descriptions are **injected into the generated catalogue** (`AP-001` PT-07). This file is the source; the portal page is the output. Editing the portal page is prohibited |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **Registered W3; first consumed W1.** `AS-08` and `DM-15` apply from the first write path in W1. Every module built in W1 and W2 registers events without an agreed meaning, and `FR-IPF-033` contract testing verifies schema compatibility, not semantics — so the divergence will not be caught in CI. Sixth consecutive category with this defect | Programme Content Lead with Platform Engineering Lead | **W1 — before the first event is registered** |
| **O-02** | **The financial trigger between `service_order.completed` and `closed` is undecided.** `05-03` §4.2 lists `M20` as a consumer of both. `G3-01` requires 100% of invoices generated automatically from **closed** jobs, which suggests `closed` — but `M20`'s own specification is the authority and this file has not been reconciled against it | `M20` owner with Enterprise Architecture | **W3 — before the billing engine is built** |
| **O-03** | **No partial-payment event exists.** `invoice.paid` fires on full settlement only. Instalment (`INT-009`), corporate part-payment and multi-method settlement all produce a state no event describes | `M20` owner | W3 |
| **O-04** | **`complaint.raised` has two producers** — `05-03` §4.2 records `M07/M23`. `FR-IPF-024` registration assumes one producing module, and `05-02` requires one owning system per fact (`IP-01`) | Enterprise Architecture | W4 |
| **O-05** | **Event retention is undefined** (`M28` Q-05). `BRU-IPF-22` forbids deletion before retention expires; with no period defined, no event can lawfully be deleted **and** no retention basis can be stated to the National Data Management Authority under PDPA 2026 processing-record obligations (`NFR-095`) | CTO with Legal Counsel | **W1 build** |
| **O-06** | **Twenty-one event names are consumed by specifications and are not in the inventory** (§4.9); fourteen appear to be genuinely missing registrations, including `credit_note.issued`, `recall.execution_updated` and `claim.evidence_incomplete` — the last two carrying safety and control consequence. Whether `05-03` §4.2 is complete or "principal" is itself undecided | Enterprise Architecture with CTO | **W1 — this determines whether the catalogue is a catalogue** |
| **O-07** | **`technician.location_updated` is not sized.** `T-07` sets the throughput envelope at 5,000 events/minute sustained at W8. `NFR-056` requires GPS ingestion for 400 technicians at 30-second intervals — **800 position updates per minute from GPS alone**. If position updates traverse the event bus rather than a separate telemetry path, the envelope is wrong by a large factor | CTO with Platform Engineering Lead | **W2 — before `INT-023` Traccar lands** |
| **O-08** | **No AsyncAPI decision.** `IP-08` specifies JSON Schema for events. The industry contract format for event-driven APIs is AsyncAPI 3.0, and the generated catalogue (`FR-IPF-032`) is the natural place to emit it. Without a decision, external subscribers receive a bespoke format while receiving OpenAPI 3.1 for REST | Solution Architect | W4 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the §4 subdivision is the only addition and is justified
- [x] **All 64 `05-03` §4.2 business events described — none omitted, none invented**
- [x] All 15 `M28` §12.3 platform events described
- [x] Envelope explained field by field with the consumer obligation for each
- [x] Nine-element description standard stated before the catalogue that applies it
- [x] Six ordering and inference traps stated with the wrong inference named
- [x] Personal-data class and residency flag on every entry, with the totals counted (`CP-11`)
- [x] **Twenty-six externally-named events extracted and classified into three remedy classes**
- [x] Eight naming and versioning rules including the description-change rule
- [x] The not-an-event boundary recorded so it is not re-litigated per module
- [x] Every open question referred to a named owner rather than resolved by assertion
- [x] All internal links resolve
- [x] Eight open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` registered after first consumption — outstanding**
- [ ] **`O-02` the invoicing trigger is undecided — outstanding; blocks the billing engine**
- [ ] **`O-05` event retention undefined — outstanding; a PDPA processing-record obligation**
- [ ] **`O-06` twenty-one unregistered event names — outstanding; the largest single finding in this category**
- [ ] Named approvers recorded — **pending Content Design Lead and CTO**
- [ ] Bengali counterpart — n/a; developer audience, English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
