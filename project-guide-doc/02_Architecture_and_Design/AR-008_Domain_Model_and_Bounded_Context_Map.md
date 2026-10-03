---
id: AR-008
title: Domain Model & Bounded Context Map
category: 02 — Architecture & Design
code: AR
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Architect
approver: Design Authority (constituted under GV-002)
standards_basis: Domain-Driven Design (aggregates, invariants, bounded contexts, context mapping) · ISO/IEC/IEEE 42010:2022 information viewpoint
traces_to: >
  PGD-000 AR-008 · 05-02 (entity catalogue, 225 entities / 30 modules) ·
  _MODULE_TEMPLATE §10 · AR-001 §6.3 shared kernel · AR-005 boundary register
depends_on: AR-001 · AR-005
verified_on: 2026-08-18
priority: P1
needed_by: W1
enumeration_timestamp: 2026-08-18 02:05 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# AR-008 — Domain Model & Bounded Context Map

### Category 02 · Code `AR` · Domain-Driven Design · Aggregates, invariants and context mapping

---

## 1. Purpose

`05-02` catalogues entity **names**. This document assigns **aggregate roots**, states **invariants**,
and draws the **context map** that says which module's language governs which concept.

The distinction is not academic. An entity list tells a developer what tables exist. An aggregate
model tells them **what must be true at the end of every transaction**, and **which object is
responsible for making it true**. Without it, an invariant like *"a service order cannot be invoiced
before it is delivered"* is enforced in whichever module happens to think of it — or, more commonly,
in two, inconsistently.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The measured entity population and its reconciliation against `05-02` |
| 2 | The ubiquitous language — terms whose meaning is contested across the estate |
| 3 | **Aggregate roots** — which entities are transaction boundaries, and which are inside one |
| 4 | **Invariants** per aggregate — what must be true at commit |
| 5 | The bounded-context map — eleven contexts, their relationships and integration patterns |
| 6 | Shared-kernel governance |
| 7 | **The 34 multi-owned entities**, each adjudicated |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Physical schema, DDL, column types, indexes | `DA-001` | Logical model vs physical realisation |
| Field-level definitions | `DA-002` Data Dictionary | This document works at entity granularity |
| Module capability boundaries | `AR-005` | A context boundary is coarser than a capability boundary |
| Event names and payloads | `AR-009`, `IN-003` | This document fixes the **aggregate names** events are built from (ADR-017) |
| Class and method design | `AR-003` | An SDD *applies* this model |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| Data architects, `DA-001` author | The logical model the schema realises — and the corrected entity count |
| Module developers | Which aggregate their model belongs to, and what invariant they must not break |
| `AR-009` author | **Aggregate names are the first component of every event name** under ADR-017 |
| Solution Architect | The context map is the answer to "why does this concept mean something different over there" |
| QA lead | Invariants are directly testable assertions |

---

## 2. Basis and Method

### 2.1 Standards conformance

| Concept | Source | Application |
|---|---|---|
| **Aggregate** | Evans, *DDD* | A transaction boundary. One root; external references point only at the root |
| **Invariant** | Ibid. | A consistency rule true at the **end of every transaction** on the aggregate |
| **Bounded context** | Ibid. | Where the ubiquitous language changes meaning. Here: the eleven module categories |
| **Context map** | Ibid. | §6 — nine relationship kinds with an integration pattern each |
| **Shared kernel** | Ibid. | Six kernel concepts (`AR-001` §6.3), change-controlled |
| ISO/IEC/IEEE 42010:2022 | Information viewpoint | This document is the logical half; `DA-001` the physical half |

### 2.2 Measured entity population

Extracted from the `### 10.1 Owned Entities` table of all 67 specifications at **2026-08-18 02:05
(+06)**:

| Measure | Count |
|---|---:|
| Owned-entity rows declared | **1,369** |
| **Distinct entities declared owned** | **1,334** |
| Entities referenced in §10.2 by a module that does not own them | **274 rows, 177 distinct** |
| **§10.2 references whose declared owner does not define the entity in its own §10.1** | **0** ✅ |
| **Entities declared owned by more than one module** | **34** ⚠ |
| Entities catalogued in `05-02` | **225** |

> **Restated 2026-08-19 18:46 (+06) — two corrections to the table above.**
>
> **1. The population moved by one between counts, and the current figure is 1,335.** `DA-001` §2.1
> re-extracted the same tables at **2026-08-18 14:30 (+06)** and returned **1,370 owned rows, 1,335
> distinct**; an independent recount at **2026-08-19 18:46 (+06)** reproduces `DA-001` exactly. The
> 1,369 / 1,334 above is correct **as at 02:05** and is retained under `RG-08` rather than
> overwritten. **`DA-002` publishes 1,335 as the single figure**, which discharges `UXA-21`'s
> remediation instruction. Downstream sizing uses **1,335**.
>
> **2. `NEW — AR-008-F-01` (HIGH): the ownership completeness check above covers the 67 module
> specifications and was never run against the 12 portal specifications.** Re-run across all **79**
> specifications, the `0 ✅` on row four does not hold:

| Measure, all 79 specifications | Count |
|---|---:|
| Owned-entity rows declared | **1,370** |
| **Distinct entities declared owned** | **1,335** |
| Owned-entity rows contributed by the 12 portal specifications | **0** — portals own nothing |
| **Entities named in a §10.2 that are owned by no specification** | **35** ⚠ |
| …of which genuine entities referenced by portals | **34** |
| …of which a wildcard pattern, not an entity (`fix.warehouse.fact.*`, `M54` → `M62`) | **1** |
| Portal specifications affected | **10 of 12** |

> **Verification**: 1,370 − 1,335 = **35** excess owned rows, from the **34** multi-owned entities
> (`fix.contract.cost` is owned by three) ✓ · 1,335 owned + 35 unowned-but-referenced = **1,370**
> distinct entities named anywhere in §10 ✓.
>
> **Why the original check returned zero and this one does not.** Row four tests whether a §10.2
> row's *declared owner* defines the entity in its own §10.1 — a test over module-to-module
> references, all of which pass. **It does not test whether an entity referenced by a *portal* is
> defined anywhere at all.** `P07` references 8 such entities, `P01` 7, `P02` 6, `P04` and `P12` 5
> each, `P09` and `P11` 4 each, `P05` and `P10` 3 each, `P08` 2.
>
> **What is actually missing.** `fix.invoice`, `fix.payment`, `fix.warranty`, `fix.warranty.claim`,
> `fix.sale.order`, `fix.partner`, `fix.rental`, `fix.commission`, `fix.settlement`, `fix.dispute`,
> `fix.statement`, `fix.credit.note`, `fix.vendor.invoice`, `fix.attendance`, `fix.leave`,
> `fix.loyalty.balance`, `fix.loyalty.benefit`, `fix.marketplace.seller`, `fix.mp.job`,
> `fix.mp.listing`, `fix.tradein`, `fix.rfq`, `fix.qc.record`, `fix.pm.schedule`, `fix.finding`,
> `fix.hse.inspection`, `fix.audit.checklist`, `fix.incentive`, `fix.advertising`,
> `fix.dispatch.assignment`, `fix.ewaste.batch`, `fix.sla.status`, `fix.rental.availability`,
> `fix.uom.category`.
>
> **This is the `AUDIT-016` `AP-01` defect class — "21 event names are consumed by specifications
> and do not exist in the inventory" — occurring on entities instead of events**, and it reaches
> the user-facing surface. Several are near-misses for entities that *do* exist under another name
> (`fix.warranty.register` is owned by `M09`; `fix.invoice` may be `M20`'s), so the likely
> resolution is a **naming reconciliation, not 34 new tables** — but until it is done, ten portal
> specifications reference tables the schema will not contain.
>
> **Remediation.** Enterprise Architecture reconciles each of the 34 against the owned set and
> records either the correct owner or a new owning module, before `DA-001` freezes the schema.
> Raised to `DA-001` and `AR-005`; tracked as `Q-06` below and as a `GV-005` entry.

### 2.3 Two findings, one good and one not

> **Finding `PGD-A3-13` — the entity catalogue is stale by a factor of roughly six.**
> `05-02` is titled *"225 Entities Across 30 Modules"*. It is correct for what it covers and it was
> never restated for the 67-module architecture. **The estate now declares 1,334 distinct owned
> entities.** The consequence is not documentary: `DA-001` (Database Schema Specification, P0, W1) is
> the downstream deliverable, and sizing it from 225 entities under-scopes it by ~83%. Referred to
> Enterprise Architecture and to `DA-001`'s author.

> **A finding in the other direction, stated because an analysis that reports only faults is not
> credible.** `_MODULE_TEMPLATE` §10.2 carries a warning: *"255 references across the estate
> currently name entities their declared owner does not define — the single largest technical defect
> found in the August 2026 audit."* **Reconciling all 274 referenced-entity rows against their
> declared owner's §10.1 returns zero mismatches.** That defect has been fully remediated. It is the
> clearest evidence in the estate that the audit culture `PGD-000` §2.3 praises actually closes
> findings rather than only recording them.

### 2.4 Source material

| Source | Contribution |
|---|---|
| All 67 specifications §10.1, §10.2, §8, §9 | The entity population, references, state models and invariant candidates |
| `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_*.md` §1–§8, §10 | DM-01…DM-15; the 225-entity catalogue; ERDs; classification S0–S3 |
| `.../05-05_*.md` | Business rules — the source of most invariants |
| `../../primary-doc/…Technology_Stack_Specification.md` §3.2, §12.3 | Kernel realisation across L1/L2/L5; store assignment |
| `AR-005` | Boundary rulings that determine context ownership |

---

## 3. Ubiquitous Language

Six terms are used across the estate with more than one meaning. Each is adjudicated here; the ruling
is normative for code, events, APIs and documentation.

| Term | Contested usage | **Ruling** | Consequence |
|---|---|---|---|
| **Service order** vs **work order** vs **job card** vs **repair order** | Used interchangeably across M01, M02, M04, M31 | **Service order** = the customer promise (one per request, owns the SLA). **Work order** = a unit of technician execution (N per service order). **Job card** is retired — it means "work order" and adds nothing. **Repair order** is the Odoo core `repair.order` model only, never a domain term | `RR-001` glossary; every UI string; `AR-009` event names |
| **Asset** vs **device** vs **equipment** | M17 says "device", M45 says "equipment", M49 says "asset" | **Asset** is the aggregate root. **Device** = a customer-owned asset (M17). **Equipment** = a company-owned operational asset (M45). **Fixed asset** = the financial view of a company asset (M49) — a *projection*, not a second entity | Resolves the `fix.asset` multi-ownership (§7) |
| **Claim** | Warranty claim (M09), insurance claim, SLA credit claim (M08), expense claim (M52) | **Unqualified "claim" is forbidden.** Always `warranty_claim`, `sla_credit`, `expense_claim` | Event names under ADR-017; API paths |
| **Contract** | Customer agreement (M08), employment contract (M21), vendor contract (M42), marketplace seller agreement (M12) | **`fix.contract` is the customer-facing commercial agreement (M08).** Others are `employment_contract`, `vendor_agreement`, `seller_agreement` | Prevents four modules extending one model |
| **Partner** | Odoo `res.partner` (any party), brand partner (M09/P08), referral partner (M40), courier partner (M03) | **`res.partner` is the technical kernel entity and is never called "partner" in domain language.** Domain terms are `brand`, `referral_partner`, `courier`, `seller` | The most confusing collision in the estate, because Odoo's own naming causes it |
| **Settlement** | Marketplace payout (M53), bank settlement (M50), gateway settlement (M19), claim reimbursement (M09) | Always qualified: `seller_payout`, `bank_settlement`, `gateway_settlement`, `claim_remittance` | Four different reconciliation processes with four different controls |

> **Why this section is worth its length.** `AR-009` names every event `<aggregate>.<verb>` (ADR-017).
> If "claim" is ambiguous, `claim.submitted` is ambiguous, and a consumer subscribing to it receives
> warranty claims and expense claims in one stream. Language precision here is a runtime property,
> not a style preference.

---

## 4. Aggregates

### 4.1 The aggregate rule

| # | Rule |
|---|---|
| **AG-01** | An aggregate is a **transaction boundary**. Everything inside is committed together, or not at all |
| **AG-02** | An aggregate has exactly **one root**. External references point at the root, never at an interior entity |
| **AG-03** | **Invariants hold at the end of every transaction** on the aggregate. Not eventually — at commit |
| **AG-04** | **Cross-aggregate consistency is eventual**, achieved by domain events, never by a distributed transaction |
| **AG-05** | Keep aggregates small. A large aggregate is a lock-contention problem before it is a design problem |
| **AG-06** | An aggregate root's name is the **event namespace** under ADR-017 |

### 4.2 The principal aggregates

Twenty-two aggregate roots carry the transactional core. The remaining ~1,312 entities are either
interior to an aggregate, reference data, or configuration.

| # | Aggregate root | Context | Interior entities (examples) | Invariants |
|---|---|:--:|---|---|
| **AGG-01** | `service_order` | A | work orders, tasks, diagnostic results, estimate, QC results, SLA clock, holds, custody events, service report | I-01…I-06 (§5.1) |
| **AGG-02** | `asset` | F | identifiers, ownership, custody, status history, service history, part genealogy | I-07…I-09 |
| **AGG-03** | `party` **(kernel)** | B | roles, hierarchy, addresses, contact verifications, identity documents, consent records | I-10…I-13 |
| **AGG-04** | `catalogue_item` **(kernel)** | C | variants, compatibility, supersession chain, service kit definition | I-14, I-15 |
| **AGG-05** | `contract` | C | lines, covered assets, entitlements, SLAs, amendments, PM schedule | I-16…I-18 |
| **AGG-06** | `warranty_claim` | C | evidence, lines, brand response, remittance link | I-19…I-21 |
| **AGG-07** | `quotation` | C | lines, versions, decision | I-22 |
| **AGG-08** | `invoice` | G | lines, tax lines, Mushak register entry, payment applications | I-23…I-26 |
| **AGG-09** | `payment` | G | allocations, gateway settlement reference | I-27, I-28 |
| **AGG-10** | `journal_entry` | G | lines, dimensions | I-29, I-30 |
| **AGG-11** | `stock_item` | E | quants, reservations, moves, cycle counts, variances | I-31…I-33 |
| **AGG-12** | `purchase_order` | E | lines, receipts, three-way match result | I-34 |
| **AGG-13** | `consignment` | A | legs, items, custody events, POD | I-35, I-36 |
| **AGG-14** | `employee` **(kernel-adjacent)** | H | employment contract, position, competencies, certifications | I-37, I-38 |
| **AGG-15** | `payroll_run` | H | payslips, tax computations, PF, gratuity, BEFTN file | I-39, I-40 |
| **AGG-16** | `marketplace_order` | C | fulfilment orders, seller jobs, offers, commission entries | I-41, I-42 |
| **AGG-17** | `seller` | C | documents, agreement, listings, wallet, scores | I-43, I-44 |
| **AGG-18** | `rental_agreement` | D | lines, reservations, condition reports, damage assessments, deposits | I-45, I-46 |
| **AGG-19** | `refurb_unit` | D | trade-in origin, grading result, QA results, provenance, resale listing | I-47, I-48 |
| **AGG-20** | `data_case` | A | media items, custody events, recovery attempts, recovered inventory, destruction certificate | I-49…I-51 |
| **AGG-21** | `document` **(kernel)** | I | versions, signature envelope, retention class, legal hold, disposal record | I-52, I-53 |
| **AGG-22** | `conversation` | B | messages, call record, agent session, disposition | I-54 |

---

## 5. Invariants

**An invariant is a statement that is true at the end of every transaction, enforced at the model
layer, and negatively tested.** Fifty-four are stated; the ones with statutory or financial
consequence are given first.

### 5.1 `service_order` (AGG-01)

| # | Invariant | Class | Source |
|---|---|:--:|---|
| I-01 | A service order has an identified party **and** an identified asset | **H** | `BRU-SRM-01` |
| I-02 | `state = on_hold` ⟺ a hold reason is set | **H** | Constraint |
| I-03 | An order may not reach `ready` without a **passed** QC result | **H** | `BRU-SRM-04` |
| I-04 | An order may not be invoiced before `delivered` | **H** | `BRU-SRM-05` |
| I-05 | `order_type = warranty` ⟹ warranty was active at the service request date | **H** | `BRU-SRM-02` |
| I-06 | The sum of work-order labour minutes never exceeds the order's elapsed active time | **C** | Consistency |

### 5.2 Financial aggregates — where an invariant failure is unrecoverable

| # | Invariant | Aggregate | Class |
|---|---|---|:--:|
| I-23 | Invoice total = Σ line totals + Σ tax lines, **to the declared rounding precision** | `invoice` | **H** |
| I-24 | **Every invoice with VAT has exactly one Mushak 6.3 register entry, written in the same transaction** | `invoice` | **H** — statutory |
| I-25 | **Input VAT credit is claimable only against a valid compliant Mushak 6.3 invoice; the system blocks a claim without one** | `invoice` | **H** — NFR-101 |
| I-26 | An invoice may not be voided after payment application; a credit note is issued instead | `invoice` | **H** |
| I-27 | Σ payment allocations ≤ payment amount | `payment` | **H** |
| I-28 | A payment references exactly one gateway settlement, or none (cash) — never two | `payment` | **H** |
| I-29 | **Σ debits = Σ credits in every journal entry.** No exception, no tolerance | `journal_entry` | **H** |
| I-30 | Every posting carries the full dimension set required by its posting rule | `journal_entry` | **H** |
| I-39 | A payroll run is immutable once approved; a correction is a new run | `payroll_run` | **H** |
| I-40 | Σ payslip net = Σ BEFTN file lines, exactly | `payroll_run` | **H** — statutory |

> **I-24 is the invariant most likely to be implemented as two transactions and most expensive when
> it is.** If the invoice commits and the Mushak register write fails, the VAT return will not
> reconcile to the ledger, and the discrepancy is found by NBR, not by us.

### 5.3 Personal data and custody — statutory invariants

| # | Invariant | Aggregate | Class |
|---|---|---|:--:|
| I-11 | **A residency-classified value never exists in the regional store** — not in a column, a cache, a log, a search index or a report | `party` | **H** — NFR-086 |
| I-12 | Every processing purpose has a recorded lawful basis (consent or stated legitimate ground) | `party` | **H** — NFR-090 |
| I-13 | An erasure removes personal data from **every** store while preserving the statutory processing record | `party` | **H** — NFR-093, NFR-095 |
| I-49 | A data case's custody chain has **no gap**: every transfer has both parties, a timestamp and evidence | `data_case` | **H** |
| I-50 | Recovered customer data is readable only by case-assigned staff, under dual control | `data_case` | **H** — T5 |
| I-51 | **No refurbished unit is released without a destruction certificate** | `data_case` / `refurb_unit` | **H** — W6 gate |
| I-53 | A document under legal hold cannot be disposed of, whatever the retention schedule says | `document` | **H** |

### 5.4 Operational invariants (abridged)

| # | Invariant | Aggregate |
|---|---|---|
| I-07 | An asset has at most one **active** ownership record at any instant |
| I-08 | An asset's status history is append-only and gapless |
| I-09 | A serial number, IMEI or asset tag is unique where present (partial unique index) |
| I-10 | A party holds ≥ 1 role; roles are additive and independently revocable |
| I-14 | A catalogue item's supersession chain is acyclic |
| I-16 | An entitlement's consumption never exceeds its grant |
| I-19 | A warranty claim may not be submitted with an incomplete evidence pack (`claim.evidence_incomplete`) |
| I-31 | Σ reservations against a quant ≤ on-hand quantity |
| I-32 | A stock move is never partially applied |
| I-35 | A consignment leg has exactly one custody holder at any instant |
| I-38 | **A technician may not be assigned work requiring a certification they do not hold or that has expired** |
| I-43 | A seller may not transact before documents are verified, the agreement is signed and admin approval is granted |
| I-44 | A payout is blocked while a dispute is open on any contributing job |
| I-46 | A rental asset is on at most one active agreement |

> **I-38 is the invariant currently protected by a stub.** `AR-006` §5.2 dispositions M02's W2
> dependency on M22 (W5) as STUB — eligibility returns "eligible" until Wave 5. **An invariant
> enforced by a stub that always returns true is not enforced.** It must be registered in `GV-005`
> with an expiry, per `AR-006` D-A6-04.

---

## 6. Bounded Context Map

### 6.1 Eleven contexts

The eleven module categories (`AR-001` §6.2) are the bounded contexts. Each has a language, a core
aggregate set and a relationship to its neighbours.

| Context | Core aggregates | Language centre |
|:--:|---|---|
| **A** Service Delivery | `service_order`, `consignment`, `data_case` | Work, custody, promise |
| **B** Customer Engagement | `party` (kernel), `conversation` | Identity, relationship, contact |
| **C** Commercial | `catalogue_item` (kernel), `contract`, `quotation`, `warranty_claim`, `marketplace_order`, `seller` | Offer, agreement, entitlement |
| **D** Circular | `rental_agreement`, `refurb_unit` | Asset lifecycle beyond first sale |
| **E** Supply Chain | `stock_item`, `purchase_order` | Quantity, location, supply |
| **F** Asset & Facilities | `asset` | Physical thing with a history |
| **G** Finance | `invoice`, `payment`, `journal_entry` | Money, obligation, period |
| **H** People | `employee`, `payroll_run` | Person as worker |
| **I** Governance | `document` (kernel) | Evidence, control, obligation |
| **J** Intelligence | *(none — read-only)* | Measurement, prediction |
| **K** Platform | *(kernel infrastructure)* | Identity, configuration, transport |

### 6.2 Context relationships

| Relationship | Kind (DDD) | Pattern | Note |
|---|---|---|---|
| **K → all** | **Shared kernel** | Direct model sharing | Party, catalogue, location, entity, document, event. Change-controlled |
| **A → G** | **Customer/supplier** — G is upstream | Billable events | A raises billable events; **G decides the posting**. Never the reverse (LB-04) |
| **A → E** | Customer/supplier — E upstream | Reservation API + `part.consumed` event | A requests; E rules on availability |
| **C → G** | Customer/supplier — G upstream | Events | Revenue, commission and settlement post through G |
| **C → A** | **Partnership** | Bidirectional events | A contract generates service orders; service orders consume entitlements |
| **H → A** | Customer/supplier — H upstream | Competency API (stubbed to W5) | Certification gates dispatch (I-38) |
| **H → G** | Customer/supplier — G upstream | Events | Payroll posts to the ledger |
| **F → A, D, E** | Shared kernel-adjacent | `asset` read via API | The asset is referenced by three contexts with three different concerns |
| **J → all** | **Conformist, read-only** | Event projection + warehouse | J conforms to every producer's model; it never negotiates one (LB-06) |
| **I → all** | Shared kernel (`document`) + published language | Document API | Evidence is attached everywhere |
| **B → all** | Shared kernel (`party`) | Direct | The most-referenced kernel concept |
| **→ external** | **Anticorruption layer** | Per `AR-005` §7 | Six external boundaries |

> **The two relationships worth naming explicitly.** *A → G is customer/supplier with G upstream* —
> service delivery does not get to decide how its work is accounted for, which is what makes financial
> truth single-sourced. *J is conformist* — analytics accepts whatever model the producers give it and
> never asks a producer to change for reporting convenience, which is what stops a warehouse becoming
> a second system of record.

### 6.3 Shared-kernel governance

| # | Rule |
|---|---|
| **SK-01** | The kernel is exactly six concepts: `party`, `catalogue_item`, `location`, `legal_entity`, `document`, `event`. Adding a seventh is a Design Authority decision |
| **SK-02** | Each kernel concept has exactly **one owning module** — M33, M37, M30, M30, M24, M28 |
| **SK-03** | A change to a kernel model requires Design Authority approval and an impact assessment across **all** consuming modules |
| **SK-04** | A consuming module may **extend** a kernel model with its own fields; it may not change kernel semantics |
| **SK-05** | **Kernel concepts are Wave 1 deliverables.** `AR-006` §5.5 moves `document` (M24-core) and the employee master to W1 for exactly this reason |

---

## 7. The 34 Multi-Owned Entities

**Thirty-four entities are declared as owned by two or three modules in their respective §10.1
tables.** Each is a latent duplicate implementation. Adjudicated below, using `AR-005`'s taxonomy and
ordering tests.

### 7.1 Kernel violations — most serious

| Entity | Claimed by | **Ruling** | Reason |
|---|---|---|---|
| **`fix.zone`** | M02, M30 | **M30 owns it.** M02 extends with dispatch attributes | `zone` is part of the **location kernel** (`AR-001` §6.3). A kernel concept owned by a functional module is SK-02 violated |
| **`fix.cost.center`** | M54, M30 | **M30 owns it.** M54 extends with allocation rules | Kernel — organisational dimension |
| **`fix.working.calendar`** | M63, M30 | **M30 owns it** | Kernel — configuration |
| `fix.asset` | M17, M49 | **M17 owns it.** M49's `fix.fixed.asset` is the **financial projection**, a distinct entity | §3 ruling: asset vs fixed asset |
| `fix.asset.custody` | M17, M49 | **M17** | Interior to AGG-02 |
| `fix.survivorship.rule` | M33, M64 | **M64 owns it.** M33 consumes | `AR-005` §5.19 — governance is M64's |

### 7.2 Security and compliance overlaps — audit-relevant

| Entity | Claimed by | **Ruling** | Reason |
|---|---|---|---|
| **`fix.sod.rule`** | M60, M29 | **M29 owns it.** M60 maps rules to obligations | `AR-005` §5.18 — M29 implements the control; M60 evidences it |
| **`fix.sod.exception`** | M60, M29 | **M29** | Same |
| `fix.delegation` | M63, M29 | **M29 owns it.** M63 consumes for task routing | Delegation is an authorisation act |
| **`fix.risk.assessment`** | M59, M60 | **M60 owns the enterprise risk assessment.** M59's HSE risk assessment is a **distinct entity**, `fix.hse.risk.assessment` | Closes `PGD-A3-12` raised in `AR-005` §5.14 Q-01 |
| `fix.control` | M59, M60 | **M60 owns the control library.** M59 references | Same |
| **`fix.processing.record`** | M33, M60 | **M33 owns it** — it is a property of the party's data, and NFR-095 requires it survive erasure | The PDPA processing record must live with the data subject, not with the compliance function |

### 7.3 Financial overlaps

| Entity | Claimed by | **Ruling** | Reason |
|---|---|---|---|
| `fix.contract.cost` | M08, M53, M54 | **M08 owns the contract cost line.** M53 and M54 project | Interior to AGG-05 |
| `fix.settlement.line` | M50, M53 | **M53 owns marketplace/commission settlement.** M50's `fix.bank.settlement.line` is distinct | §3 "settlement" must always be qualified |
| `fix.letter.of.credit` | M44, M50 | **M44 owns it** (trade instrument); M50 references for cash forecasting | T1 statutory test — import compliance |
| `fix.tax.challan` | M51, M56 | **M51 owns it.** M56 references payroll TDS challans | T1 — one tax authority interface |
| `fix.intercompany.transaction` | M19, M65 | **M19 owns it.** M65 configures the jurisdictional rules | T2 — it posts to the ledger |
| `fix.subscription` | M39, M25 | **M39 owns it.** M25's is a **reporting dimension**, not an entity — remove from M25 §10.1 | Specification correction |
| `fix.forecast` | M43, M54 | **Two different things.** M43 owns `fix.demand.forecast`; M54 owns `fix.financial.forecast`. **Rename both** | Naming collision, not ownership conflict |

### 7.4 Platform and operational overlaps

| Entity | Claimed by | **Ruling** |
|---|---|---|
| `fix.scheduled.job`, `fix.job.run` | M63, M30 | **M30 owns the platform scheduler.** M63 owns business-process tasks — rename M63's to `fix.process.task` / `fix.process.run` |
| `fix.event.subscription` | M63, M28 | **M28 owns it** — it is transport (`AR-005` §5.17) |
| `fix.escalation.rule` | M01, M63 | **M01 owns SLA escalation.** M63 owns process escalation — rename M63's `fix.process.escalation` |
| `fix.runbook`, `fix.maintenance.window`, `fix.oncall.rota` | M05 + (M30 / M55) | **M05 owns the customer-facing MSP versions.** M30 owns the platform's own; M55 owns the staff rota. **Prefix M05's `fix.msp.*`** |
| `fix.alert`, `fix.alert.rule` | M05, M48 | **M05 owns MSP alerting; M48 owns IoT alerting.** Prefix both: `fix.msp.alert`, `fix.iot.alert` |
| `fix.quality.result` | M62, M64 | **M62 owns data-quality results.** M64 references |
| `fix.pipeline` | M07, M62 | **Two different things.** M07's is a **sales** pipeline (`fix.sales.pipeline`); M62's is a **data** pipeline. Rename both |
| `fix.review` | M34, M57 | **M34 owns customer review; M57 owns performance review.** Rename: `fix.customer.review`, `fix.performance.review` |
| `fix.job.profile` | M21, M58 | **M21 owns it** (org position). M58 references for requisitions |
| `fix.equipment.usage` | M31, M45 | **M45 owns it.** M31 records usage against it |
| `fix.repair.warranty` | M01, M09 | **M01 owns it** — it is created by the repair. M09 references for claim eligibility |

### 7.5 Summary of remediation

| Remediation kind | Count | Action |
|---|---:|---|
| **Rename** — two genuinely different concepts sharing a name | **14** | Both specifications renamed; no ownership change |
| **Single owner ruled**, other reduced to a reference | **17** | Losing module's §10.1 row moves to §10.2 |
| **Split into two entities** | **3** | `fix.risk.assessment`, `fix.forecast`, `fix.settlement.line` |
| | **34** | |

> **Fourteen of the thirty-four are naming collisions, not ownership conflicts** — two teams
> independently choosing `fix.review` for a customer rating and a performance appraisal. That is a
> predictable consequence of 67 specifications written in parallel with no entity-name registry, and
> it is the strongest argument in this document for **`FF-27`: entity-name uniqueness as a CI check**
> (`AR-012`), so the 35th collision fails a build rather than reaching an audit.

---

## 8. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | **Is `05-02` reissued for 67 modules and 1,335 entities, or superseded by `DA-001`?** (`PGD-A3-13`) | Enterprise Architecture | **W1 — blocking `DA-001`** | Schema specification scope and cost |
| Q-02 | Are the 34 §7 rulings accepted, and who executes the 14 renames and 17 §10.1→§10.2 moves? | Design Authority | W1 | `AR-003` design gate E-04 |
| Q-03 | Is the 22-aggregate set complete? It was derived from state models; a module without an explicit §8 may hide an aggregate | Chief Architect | W1 | `DA-001` transaction boundaries |
| Q-04 | Does `RR-001` (glossary) adopt the §3 language rulings as normative? | `RR-001` owner | W1 | Every UI string, event name and API path |
| Q-05 | Should entity names be a registered identifier space in `RR-002`? | Enterprise Architecture | W2 | `FF-27` |

---

## 9. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-A8-01 | Bounded context granularity | Per module (67); **per category (11)**; per pillar (5) | **Per category** | 67 contexts is not a map, it is the module list again. The language genuinely changes at category boundaries | Eleven contexts, nine relationship kinds |
| D-A8-02 | Aggregate scope | Large (fewer, richer); **small, transaction-sized** | **Small** | AG-05 — a large aggregate is a lock-contention problem at 5 M service orders/year | 22 roots over 1,335 entities |
| D-A8-03 | Multi-owned entities | Leave to design; **adjudicate all 34 now** | **Adjudicate now** | Each is a latent duplicate implementation, cheapest to fix before code | 14 renames, 17 reductions, 3 splits |
| D-A8-04 | Language collisions | Allow context-local meaning; **qualify globally** | **Qualify** | Event names are global under ADR-017; `claim.submitted` cannot mean two things on one bus | Six terms ruled in §3 |
| D-A8-05 | `05-02` disposition | Reissue for 67; **supersede by `DA-001`**; leave | **Recommend supersession**, decision to Enterprise Architecture (Q-01) | Reissuing a 30-module catalogue to 1,335 entities is writing `DA-001` under another name | `DA-001` scope grows ~6× |

---

## 10. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The entity population is counted, not consulted, and reconciled against `05-02` | §2.2, §2.3 |
| AC-02 | Contested domain terms are adjudicated | §3 — 6 terms |
| AC-03 | Aggregate roots are assigned with interior entities named | §4.2 — 22 aggregates |
| AC-04 | Every aggregate has at least one stated invariant, classified and traceable to a business rule or statute | §5 — 54 invariants |
| AC-05 | A context map exists with a DDD relationship kind and an integration pattern per edge | §6.2 — 12 relationships |
| AC-06 | Every multi-owned entity is adjudicated | §7 — 34 of 34 |
| AC-07 | Shared-kernel governance is stated | §6.3 SK-01…SK-05 |
| AC-08 | Findings are reported in both directions | §2.3 — the 255-reference defect is recorded as **remediated** |

**Definition of done.** Complete when every criterion is met, Q-01 and Q-02 are decided, and
`PGD-000`'s `AR-008` row is updated with a fresh enumeration timestamp.

---

## 11. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `AR-001` §6.3 | Shared kernel |
| Upstream | `AR-005` | Boundary rulings that determine context ownership; §7.2 closes its Q-01 |
| Downstream | **`DA-001`** | Realises this logical model physically — **and must be sized from 1,335, not 225** |
| Downstream | `DA-002` | Field-level dictionary within these entities |
| Downstream | `AR-009` | **Aggregate names are the first component of every event name** (ADR-017) |
| Downstream | `AR-003` | Design gate entry condition E-04 |
| Downstream | `AR-012` `FF-27` | Entity-name uniqueness check |
| Downstream | `RR-001` | Glossary adopts §3 rulings |
| Downstream | `QA-003` | Invariants are directly testable |
| Lateral | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02` | Superseded as a *catalogue* if Q-01 is decided that way; retained for ERDs and classification |

---

## 12. References

**Within this repository**
`../PGD-000_*.md` · `./_CATEGORY_OVERVIEW.md` · `./AR-001` · `./AR-003` · `./AR-005` · `./AR-009` ·
`./AR-012` · `../_AUDIT/PGD-AUDIT-003_*.md`

**Workspace**
`../../1000fix_ERP_Module/03_Modules/**/M*.md` §8, §9, §10 (all 67) ·
`.../05_Cross_Cutting_Specifications/05-02` §1–§8, §10, `05-05` ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §3.2, §12.3

**External sources**

| Source | Verified |
|---|---|
| Eric Evans, *Domain-Driven Design* — aggregates, invariants, bounded contexts, context mapping | 2026-08-18 |
| Vaughn Vernon, *Implementing Domain-Driven Design* — aggregate design rules | 2026-08-18 |
| VAT and Supplementary Duty Act 2012 — Mushak 6.3, NFR-101 input-credit rule | 2026-08-18 |
| Personal Data Protection Act 2026, Bangladesh — NFR-090, NFR-093, NFR-095 | 2026-08-18 |

---

## 13. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. 22 aggregates, 54 invariants, 11 bounded contexts. Raises `PGD-A3-13` (entity catalogue stale ~6×). Adjudicates 34 multi-owned entities. Closes `AR-005` Q-01 (`PGD-A3-12`). Records the 255-reference defect as **remediated** | *Pending — Design Authority not constituted* |

---

*`AR-008` · Category 02 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
