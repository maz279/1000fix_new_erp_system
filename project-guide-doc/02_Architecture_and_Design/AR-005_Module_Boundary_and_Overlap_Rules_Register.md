---
id: AR-005
title: Module Boundary & Overlap Rules Register
category: 02 — Architecture & Design
code: AR
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Architect
approver: Design Authority (constituted under GV-002)
standards_basis: Domain-Driven Design (bounded context, shared kernel, anticorruption layer) · ISO/IEC/IEEE 42010:2022
traces_to: >
  PGD-000 AR-005 · 02-03 (planned, never written) · FOLDER_STRUCTURE.md §7 (overlap controls) ·
  RG-04 boundary symmetry · _MODULE_TEMPLATE §3
depends_on: AR-001 · AR-008 (aggregate boundaries)
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 02:05 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# AR-005 — Module Boundary & Overlap Rules Register

### Category 02 · Code `AR` · Domain-Driven Design · Bounded contexts and shared kernel

---

## 1. Purpose

With 67 modules, the probability that two of them claim the same capability approaches certainty.
`_MODULE_TEMPLATE` §3 already contains the anti-overlap control — *"Both sides of every boundary must
agree. If §3.2 says a capability belongs to another module, that module's §3.1 must claim it"* — and
`FOLDER_STRUCTURE.md` §7 names three overlap controls of which this register is one.

**The register (`02-03`) was never written.** Without it, `_MODULE_TEMPLATE` §3's rule is enforced
only by each author checking their own file, which cannot detect the case the rule exists for: two
modules both claiming, or — more dangerous — **both disclaiming**.

This document is that register. It also states the **adjudication procedure**, because a boundary
dispute between two module owners with no arbiter resolves either by seniority or by whoever writes
their specification last.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The boundary taxonomy — five kinds of boundary, each with a different rule |
| 2 | Measured boundary declarations across all 67 specifications — 1,371 in-scope claims, 909 out-of-scope declarations, 760 shared-concept declarations |
| 3 | The symmetry check method, and what it can and cannot verify mechanically |
| 4 | **The adjudicated register** — 21 contested or high-traffic boundaries, each ruled with a reason and a test |
| 5 | The adjudication procedure for boundaries not yet contested |
| 6 | Anticorruption-layer rules where a boundary crosses into an external system |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Which module is built first | `AR-006` | Sequence presumes a settled boundary |
| Aggregate roots and invariants | `AR-008` | A boundary between modules is coarser than an aggregate boundary |
| The ERP-vs-portal boundary | `AR-002` §4.2 | Inter-system, not inter-module |
| Entity ownership at field level | `DA-002` | This register rules on **capability**; the data dictionary rules on **field** |
| Requirement allocation | `05-01`, `RQ-005` | A requirement follows its capability's owner |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| Module authors | Before writing §3, check whether the boundary is already ruled here |
| Solution Architect | §5 is the answer to "who builds this" |
| Implementation vendor | Prevents the same capability being priced and built twice |
| QA lead | A ruled boundary is a testable statement about where a rule is enforced |

---

## 2. Basis and Method

### 2.1 Standards conformance

| Concept | Source | Application |
|---|---|---|
| **Bounded context** | Eric Evans, *Domain-Driven Design* | A module is a bounded context. Its boundary is where the ubiquitous language changes meaning |
| **Shared kernel** | Ibid. | Six kernel concepts (`AR-001` §6.3) are deliberately shared, under change control. Everything else is owned by exactly one module |
| **Anticorruption layer** | Ibid. | §7 — where a boundary crosses to an external system, translation is explicit and one-directional |
| **Customer/supplier** | Ibid. | §5's rulings state which side is upstream, because that determines who accommodates whom |

### 2.2 Measured boundary declarations

Counted across all 67 specification files at **2026-08-18 02:05 (+06)**:

| Declaration | Count | Source |
|---|---:|---|
| §3.1 **In scope** — capability claims | **1,371** | Numbered rows |
| §3.2 **Explicitly out of scope** — declarations naming an owning module | **909** | Rows naming `**M<nn>**` |
| §3.3 **Shared concepts** — read-live / write-via-API / consume-event declarations | **760** | Rows |
| **Total boundary assertions** | **3,040** | |

**The estate's boundary discipline is genuinely strong, and that should be said before the findings.**
Three thousand explicit boundary assertions across 67 files, written to a template that requires the
reason as well as the ruling, is better than most enterprise programmes achieve. The declarations are
also *good*: `M15`'s *"M15 is the ledger; M41 is the floor. A branch with one stockroom needs no M41"*
is a boundary rule that a developer can apply without asking anyone.

**What is missing is not quality but verification.** No mechanism has ever checked that the 909
out-of-scope declarations are reciprocated by the 1,371 in-scope claims.

### 2.3 Boundary traffic — where contests concentrate

Modules most frequently named as the owner in another module's §3.2:

| Module | Times named as owner | Reading |
|---|---:|---|
| **M15** INV | **38** | The stock ledger. Everything that touches a part disclaims to it |
| **M20** ARB | **35** | Receivable and invoicing — the money funnel |
| **M21** HCM | **31** | Employee master |
| **M33** CPM | **29** | Party kernel |
| **M11** PRC | **26** | Pricing |
| **M60** GRC · **M29** SEC · **M19** FIN | **25** each | Compliance, security, ledger |
| **M53** REV · **M12** MKP · **M08** CTR · **M02** FSM | **24** each | |
| M01, M51, M16 | 21–23 each | |

> **A module named 25+ times as an owner is carrying a great deal of other people's expectations.**
> M15, M20, M21, M33 and M19 are the five where a boundary misunderstanding is most expensive, and
> they are the five the register in §5 covers most closely.

### 2.4 Audit findings this document addresses

| Finding | How |
|---|---|
| `PGD-000` `AR-005` — *"`FOLDER_STRUCTURE.md` §7 names this as one of three overlap controls; the file does not exist"* | This is the file |
| `RG-04` boundary symmetry, unverified | §4 states the check and its limits; `AR-012` `FF-15` makes it mechanical |
| `EO-02` `05-05` carries no business rule for M40 or M42 | §5.9 and §5.14 rule the boundaries; a ruled boundary makes the missing rules discoverable |
| `AR-006` `PGD-A3-11` — 55 module-level reciprocity failures | Related but distinct: that is *dependency* symmetry; this is *capability* symmetry |

---

## 3. Boundary Taxonomy

Not all boundaries are the same kind, and applying one rule to all of them is why boundary disputes
recur. Five kinds:

| # | Kind | Rule | Example |
|---|---|---|---|
| **B1 — Exclusive ownership** | Exactly one module owns the capability, its data and its rules. Others read through a published interface | Ledger posting → **M19** only |
| **B2 — Lifecycle split** | Two modules own different **phases** of one object's life. The handover point is named and is a state transition | Trade-in device: **M14** owns acquisition→grading; **M12** owns resale listing. Handover = `refurb.graded` |
| **B3 — Decision/execution split** | One module **decides**, another **executes**. The decider owns the parameters; the executor owns the transaction | **M43** sets reorder points; **M15** executes and alerts |
| **B4 — Kernel share** | A shared-kernel concept (`AR-001` §6.3). All read; one owns the model; change requires Design Authority | `res.partner` — owned by **M33**, read by all 67 |
| **B5 — Advisory overlay** | One module produces an advisory output over another's data. The overlay **never mutates** the underlying state | **M26** scores dispatch candidates; **M02** assigns (`AR-001` LB-06) |

**The taxonomy is the tool.** Most boundary disputes are actually disagreements about *which kind of
boundary this is* — one party arguing B1 (exclusive) while the other assumes B3 (decision/execution).
**An adjudication that does not name the kind has not adjudicated.**

---

## 4. The Symmetry Check

### 4.1 What is checked

| # | Check | Mechanism | Status |
|---|---|---|---|
| **SC-01** | Every §3.2 out-of-scope row names a **module that exists** | Regex against the 67-module register | ✅ Automatable |
| **SC-02** | The named owner's §3.1 **claims** the capability | **Semantic** — capability text is prose, not an identifier | ⚠ Not automatable; see §4.2 |
| **SC-03** | No capability is claimed in §3.1 by **two** modules | Semantic | ⚠ Not automatable |
| **SC-04** | No capability is disclaimed by both parties | Semantic | ⚠ Not automatable |
| **SC-05** | Every §3.3 shared concept names an owning module that defines it in §10.1 | **Entity name is an identifier** | ✅ Automatable — `AR-012` `FF-15` |
| **SC-06** | Every §3.2 named owner is also in §1 `Depends on` or `Depended on by` | Identifier-level | ✅ Automatable |

### 4.2 The honest limitation

**SC-02, SC-03 and SC-04 cannot be checked mechanically, because a capability is a sentence and not
an identifier.** *"Bin-level location, put-away strategy, pick path"* in M15's §3.2 and *"Directed
put-away and picking"* in M41's §3.1 are the same capability under two descriptions. No regex closes
that gap.

Three options were considered:

| Option | Assessment |
|---|---|
| Allocate a `CAP-nnn` identifier to every capability and require both sides to cite it | **Rejected for now.** 1,371 capability rows would need identifiers; it introduces an eighth programme-wide identifier space into an estate where seven already collide (`RR-002`'s problem). The cure is worse than the disease at this stage |
| Leave it to per-file review | **Rejected.** That is the current state, and it produced 3,040 unverified assertions |
| **Adjudicate the high-traffic boundaries explicitly (§5) and review the remainder at design gate** | **Chosen.** Twenty-one rulings cover the boundaries where the modules named 20+ times meet. The long tail is reviewed at `AR-003`'s design gate, when both modules' designs exist and the overlap becomes concrete |

> **Recommendation to `RR-002`.** If a capability identifier space is ever created, it should be
> created *there*, in the identifier convention standard, not here — so it arrives with an allocating
> authority rather than as an eighth uncontrolled space.

---

## 5. The Adjudicated Register

Twenty-one rulings. Each states the **kind** (§3), the **ruling**, the **reason**, and the **test** —
a question whose answer distinguishes the two sides in a real case.

---

### 5.1 M15 INV ↔ M41 WMS — stock ledger vs warehouse floor

**Kind** B1 exclusive, with a capability threshold · **Ruling** M15 owns quantity, valuation,
reservation and the stock ledger. **M41 owns physical location below the stockroom level** — bin,
put-away strategy, pick path, wave and cluster picking, dock and staging.
**Reason** M15 is the ledger; M41 is the floor. A branch with one stockroom needs no M41 at all,
which is the test of whether a capability is M41's.
**Test** *"Would a single-stockroom branch need this?"* Yes → M15. No → M41.
**Upstream** M15. M41 accommodates M15's model, not the reverse.

### 5.2 M15 INV ↔ M43 DPL ↔ M26 AIM — execution, planning, algorithm

**Kind** B3 decision/execution, twice · **Ruling** M15 executes replenishment and raises alerts.
**M43 owns the parameters** — reorder point, safety stock, network rebalancing proposal.
**M26 owns the forecasting model itself.**
**Reason** Three distinct accountabilities: the transaction, the policy, and the algorithm.
**Test** *"If the number is wrong, who is accountable?"* Stock didn't move → M15. Parameter wrong →
M43. Prediction wrong → M26.
**Note** M26's output is **B5 advisory** — it never writes a reorder point directly (`AR-001` LB-06).

### 5.3 M15 INV ↔ M44 ITC — landed cost

**Kind** B3 · **Ruling** **M44 computes** landed cost and its allocation; **M15 receives the final
unit cost** and values stock at it.
**Reason** Cross-border supply is a discipline (customs, duty, LC, clearing), not a stock attribute.
**Test** *"Does answering this need a customs document?"* Yes → M44.
**Wave consequence** M41 (W3) declares a dependency on M44 (W6) — dispositioned **NOT-A-PREREQ** in
`AR-006` §5.2: W3 receipts value at standard cost.

### 5.4 M16 PRO ↔ M52 APE — three-way match

**Kind** B2 lifecycle split · **Ruling** **M16 owns the match** (PO ↔ GRN ↔ invoice); **M52 owns the
payment**, the AP ledger and the vendor invoice posting.
**Reason** Matching is a procurement control; paying is a treasury act. Putting both in one module
creates a segregation-of-duties problem in code (`SOD` financial class).
**Test** *"Does this decide whether we owe, or when we pay?"* Owe → M16. Pay → M52.
**Cycle note** This ruling resolves cycle #11 in `AR-006` §4.1: `cd_three_way_match_ext` sits in M52
and consumes M16 and M15 events, so the synchronous back-call disappears.

### 5.5 M16 PRO ↔ M42 SRM2 — buying vs supplier relationship

**Kind** B1 · **Ruling** M16 owns requisition, RFQ, PO and receipt. **M42 owns supplier
qualification, contract, scorecard and compliance.**
**Reason** *"M15 never talks to a supplier"* is M15's stated rule; the same logic separates the
transaction from the relationship.
**Test** *"Does this survive between purchase orders?"* Yes → M42.
**Cycle note** Resolves cycle #10: M42 is a read-and-score consumer of M16 events; M16 reads
scorecards through a published API. Asymmetric, not mutual.

### 5.6 M11 PRC ↔ M36 QTE — price vs quotation

**Kind** B3 · **Ruling** **M11 owns the price** — price books, rate cards, rules, guard rails,
dynamic pricing. **M36 owns the quotation document** — versioning, validity, tender response,
approval and the customer decision.
**Reason** A price is a fact about the catalogue; a quotation is a commercial offer with a lifecycle.
**Test** *"Would this change if we never quoted anyone?"* Yes → M11.
**Interaction with M01** M01 holds the estimate for a service order but does **not** author or price
it: `fix.estimate` lives in M01's `cd_estimate` and is populated by M36 through a published API.
That is a **B2 lifecycle split with the handover at `service_order.estimated`**, and it is the most
commonly misunderstood boundary in Category A.

### 5.7 M01 SRM ↔ M31 WSR — field vs workshop

**Kind** B2 lifecycle split · **Ruling** **M01 owns the service order** — the customer promise, its
SLA and its lifecycle. **M31 owns the workshop execution** — bench assignment, WIP board, repair-level
(L1/L2/L3) routing.
**Reason** One customer promise may be fulfilled at a bench, in the field, or both. The promise does
not belong to the place it is fulfilled.
**Test** *"Is this visible to the customer as a commitment?"* Yes → M01.
**Handover** `service_order.approved` → M31 creates a workshop work order; `work_order.completed` →
M01 progresses to QC.

### 5.8 M01 SRM ↔ M02 FSM — order vs assignment

**Kind** B1 · **Ruling** **M01 never assigns.** M02 owns dispatch, scoring, routing, geofence,
technician availability and van stock.
**Reason** Assignment is an optimisation over the whole open queue, not a property of one order.
**Test** *"Does answering this require knowing about other orders?"* Yes → M02.

### 5.9 M09 WTY ↔ M20 ARB ↔ M53 REV — claim, receivable, settlement

**Kind** B2, twice · **Ruling** **M09 owns the claim** — entitlement, assessment, evidence pack,
brand submission and decision. **M20 owns the receivable** created when a claim is approved.
**M53 owns reconciliation of the remittance** to the claim set.
**Reason** A claim is an assertion; a receivable is money owed; a remittance is money arriving. Three
objects, three lifecycles.
**Test** *"Has the brand agreed to pay?"* No → M09. Yes → M20. Has it arrived? → M53.
**Open gap** `EO-02` records that `05-05` carries **no business rule for M40 or M42**. The M09/M20
boundary is well-ruled; the M40 partner-commission equivalent is not, because M40 has no rules at
all. Referred to `RQ-009`.

### 5.10 M12 MKP ↔ M53 REV — commission

**Kind** B3 · **Ruling** **M12 owns the commission *scheme* and emits `commission.earned`.**
**M53 owns the calculation, the payout run and the ledger posting.**
**Reason** `AR-001` LB-04 — only Category G posts to the ledger. Marketplace commission is money.
**Test** *"Does this produce a number that must reconcile to the ledger?"* Yes → M53.
**Cycle note** Resolves cycle #12: M12 must not call M53.

### 5.11 M33 CPM ↔ M07 CRM — party master vs relationship

**Kind** B4 kernel share · **Ruling** **M33 owns the party**: identity, roles, hierarchy, addresses,
consent, identity documents, deduplication and merge. **M07 owns the commercial relationship**: lead,
opportunity, account plan, activity, health.
**Reason** A party exists whether or not anyone is selling to it. The kernel concept must not be
owned by a functional module.
**Test** *"Would this record exist for a customer nobody is selling to?"* Yes → M33.
**Kernel consequence** M33's model is **change-controlled** — a change requires Design Authority
approval, not a module release.

### 5.12 M37 CAT ↔ M15 INV — catalogue vs stock

**Kind** B4 kernel share · **Ruling** **M37 owns the definition** — part specification, compatibility
matrix, supersession chain, service kit definition. **M15 owns the quantity** at a location.
**Reason** *"A part is a catalogue concept before it is a stock concept; the same definition serves
pricing, e-commerce and procurement"* — M15's own §3.2, and it is right.
**Test** *"Is this true when we hold zero of them?"* Yes → M37.

### 5.13 M21 HCM ↔ M55 WFM ↔ M56 PAY ↔ M57 PIC — the People split

**Kind** B1 with a shared kernel · **Ruling** **M21 owns the employee master and the employment
lifecycle.** M55 owns time, attendance, roster and working-time rules. M56 owns payroll calculation
and statutory compliance. M57 owns performance, scorecards and incentive calculation.
**Reason** Four distinct statutory and operational regimes over one master record.
**Test** *"Which of these would a company with no payroll still need?"* → M21 and M55.
**Wave consequence** `AR-006` §5.1 moves M21's employee master and joiner/mover/leaver events to
**Wave 1** because M29 (in-degree 53) depends on them. The rest of M21 stays W5.

### 5.14 M23 QMS ↔ M60 GRC — quality vs governance

**Kind** B1, and the least clear boundary in the estate · **Ruling** **M23 owns the quality
management system** — ISO 9001 process register, NCR, CAPA, internal audit, management review.
**M60 owns enterprise risk and regulatory compliance** — risk register, control library, compliance
obligations, policy attestation.
**Reason** A non-conformance is a quality event; a regulatory obligation is a compliance object.
**Test** *"Would a regulator or a certification body ask for this?"* Certification body → M23.
Regulator → M60.
**Acknowledged softness** Both own a "risk register" concept (`fix.risk.register` appears in M23's
entity list). **`AR-008` must rule which is the aggregate root** and make the other a projection.
Raised as `PGD-A3-12`.

### 5.15 M24 DMS ↔ M60 GRC — document vs policy

**Kind** B4 kernel share · **Ruling** **M24 owns `fix.document`** — the kernel concept, versions,
retention class, signature envelope, legal hold, disposal record. **M60 owns policy content and
attestation.**
**Reason** A policy is a document; not every document is a policy.
**Test** *"Does someone have to acknowledge having read it?"* Yes → M60 wraps M24's document.
**Wave consequence** `AR-006` §5.3 moves M24's `fix.document` kernel to **Wave 1**. Cycle #15 is
resolved by the same move: M24-core no longer depends on M60.

### 5.16 M25 BID ↔ M62 DAT — reporting vs data platform

**Kind** B2 · **Ruling** **M62 owns the platform** — warehouse, pipelines, data contracts, lineage,
data quality. **M25 owns the semantic layer and the reports** — metric definitions, datasets,
dashboards, subscriptions.
**Reason** One is plumbing, one is meaning.
**Test** *"Would this exist if there were only one report?"* Yes → M62.
**Advisory rule** Both are **B5 relative to every transactional module** — read-only downstream
(`AR-001` LB-06).

### 5.17 M28 IPF ↔ M63 BPA — integration vs process orchestration

**Kind** B1 · **Ruling** **M28 owns the transport** — gateway, outbox, event bus, webhook delivery,
API management. **M63 owns the business process** — multi-step, multi-module orchestration with human
tasks and escalation.
**Reason** A retry ladder is a transport concern; an approval chain crossing four modules is a
process concern.
**Test** *"Would a business analyst change this, or a platform engineer?"* Analyst → M63.
**n8n note** n8n is used by both — by M28 for brand-claim transformation (ADR-025) and by M63 for
process orchestration. **The tool is shared; the ownership is not.** Each owns its own workflows and
its own credentials.

### 5.18 M29 SEC ↔ M60 GRC — security vs compliance

**Kind** B3 · **Ruling** **M29 owns the control implementation** — identity, RBAC, record rules,
field permissions, SoD enforcement, audit trail, security events. **M60 owns the obligation and its
evidence** — which control satisfies which regulatory requirement, and the attestation.
**Reason** M29 makes it true; M60 proves it to someone.
**Test** *"Does this stop something happening, or record that it did not?"* Stop → M29.

### 5.19 M30 ADM ↔ M64 MDM ↔ M65 GLO — configuration, master data, localisation

**Kind** B1 three ways · **Ruling** **M30 owns platform configuration** — entity, branch, zone, cost
centre, business line, calendar, feature flags, scheduled jobs. **M64 owns master-data governance** —
golden-record rules, survivorship, match/merge, change requests, stewardship. **M65 owns country and
locale packs** — jurisdiction-specific configuration sets.
**Reason** Configuration is a value; governance is a process; localisation is a bundle of both,
scoped to a jurisdiction.
**Test** *"Does changing this need an approval workflow?"* Yes → M64. *"Is it different in another
country?"* Yes → M65.
**Wave consequence** `AR-006` §5.2 redeclares M51's dependency on M65 (W9) as a dependency on M30's
country-pack **interface** (W1), removing a +5-wave violation and cycle #18.

### 5.20 M66 ITS ↔ M30 ADM — internal ITSM vs platform administration

**Kind** B1 · **Ruling** **M30 owns the ERP platform's own configuration and operations.** **M66 owns
the Company's internal IT service management** — the service desk for 1000FiX staff, asset management
for corporate IT, internal change management.
**Reason** M30 administers *this system*; M66 services *this company's IT*, of which this system is
one item.
**Test** *"Is the subject the ERP itself, or a laptop in the finance department?"*
**Note** Both module specifications now exist on disk (86 KB and 82 KB, written 2026-08-13) despite
`02-02` §3 and the Technology Stack Specification §25.1.1 recording them as unwritten — see
`AR-001` §2.4 finding `PGD-A3-01`.

### 5.21 M05 RMS ↔ M66 ITS — customer estates vs our own

**Kind** B1 · **Ruling** **M05 owns managed services delivered to customers.** **M66 owns internal
IT.** They share no data and no lifecycle.
**Reason** One is a revenue stream; one is an overhead.
**Test** *"Does someone pay us for this?"* Yes → M05.
**Why it needs stating** They use overlapping technology (monitoring agents, remote support, patch
orchestration). Shared tooling with unshared ownership is exactly the situation in which a boundary
erodes silently.

---

## 6. Adjudication Procedure

For boundaries not ruled above.

| Step | Action | Owner |
|:--:|---|---|
| 1 | **Check this register first.** 21 rulings plus the taxonomy resolve most cases | Module author |
| 2 | Apply the taxonomy (§3) — **name the kind before arguing the ruling** | Module author |
| 3 | Apply the four ordering tests in §6.1 | Module author |
| 4 | If unresolved, raise a **Boundary Adjudication Request** stating both claims, the kind, and the consequence of each ruling | Either module owner |
| 5 | Design Authority rules within **one sprint**. The ruling is added to §5 and to `AR-004` as an ADR if it changes a structural position | Design Authority |
| 6 | **Both** specifications are updated in the same change — §3.1 of the winner, §3.2 of the loser | Chief Architect |

### 6.1 The four ordering tests

Applied in order; the first that discriminates decides.

| # | Test | Rationale |
|---|---|---|
| **T1 — Statutory** | If one side carries a statutory obligation for the capability, it owns it | A regulator asks one owner, not two |
| **T2 — Ledger** | If the capability produces a number that must reconcile to the ledger, Category G owns the posting (`AR-001` LB-04) | Financial truth is single-sourced |
| **T3 — Lifecycle** | The module that owns the object's **state machine** owns the capability | State and the rules that change it cannot be separated |
| **T4 — Blast radius** | Otherwise, the module whose failure would affect **fewer** other modules owns it | Concentrating capability in a high-in-degree module concentrates risk |

### 6.2 Tie-break

If all four tests are silent, **the module earlier in the wave plan owns it**, because the later
module can consume a published interface but the earlier one cannot consume an interface that does
not yet exist. This is a scheduling tie-break, not an architectural one, and it is recorded as such.

---

## 7. Anticorruption Layers

Where a module boundary crosses to an external system, the internal model must not be shaped by the
external one.

| Boundary | External model | ACL rule | Owner |
|---|---|---|---|
| M09 ↔ 17+ brand partners | 17 different claim formats | **n8n transformation (ADR-025).** The internal claim model is 1000FiX's; each brand's format is a translation at the edge | M09 / M28 |
| M19/M20 ↔ payment rails | Three rails, three transaction models | Gateway wrapper normalises to `fix.gateway.settlement`. **No rail-specific field reaches the ledger** | M20 |
| M51 ↔ NBR VAT Online | Mushak forms and portal schema | The internal VAT register is the source; the return is **generated** from it. **The form does not shape the register** | M51 |
| M03 ↔ courier partners | Four courier APIs | `fix.consignment.leg` is the internal model; each courier is a connector | M03 |
| M29 ↔ corporate client IdPs | Per-client SAML/OIDC claims | **Keycloak identity brokering** maps client claims to internal roles. No client's role vocabulary enters the ERP | M29 |
| M05 ↔ customer IT estates | Customer's own asset and ticket models | `fix.monitored.asset` is ours; client ITSM exchange (INT-047) is a translation | M05 |

> **The rule stated once:** an external contract change must be absorbable at the connector. If it
> reaches the domain model, the anticorruption layer has failed. This is a `AR-003` design gate item
> for every module with an external boundary.

---

## 8. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | **M23 ↔ M60 risk register** — which owns the aggregate root? (`PGD-A3-12`) | Chief Architect / `AR-008` | W1 | M23 and M60 design; duplicate entity risk |
| Q-02 | Should a `CAP-nnn` capability identifier space be created in `RR-002` to make SC-02/03/04 mechanical? | Enterprise Architecture | W2 | Full boundary symmetry verification |
| Q-03 | Who arbitrates until the Design Authority is constituted (`PGD-A1-09`)? | CTO | **Now** | Every step-5 adjudication |
| Q-04 | Does `05-01` need reissue so requirement allocation follows these 21 rulings? | Enterprise Architecture | W1 | Requirement-to-module traceability |

---

## 9. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-A5-01 | Boundary verification | Full capability identifiers; per-file review; **adjudicate hotspots + design-gate the tail** | **Hotspots + design gate** | 1,371 capability identifiers would create an eighth colliding identifier space | 21 rulings now; the tail resolves as designs are written |
| D-A5-02 | Taxonomy | One rule for all boundaries; **five kinds** | **Five kinds (§3)** | Most disputes are disagreements about the *kind*, not the ruling | Every adjudication must name the kind |
| D-A5-03 | Tie-break | Seniority; **earlier wave**; coin toss | **Earlier wave (§6.2)** | The later module can consume an interface; the earlier cannot consume one that does not exist | Recorded as a scheduling tie-break, not an architectural principle |
| D-A5-04 | Shared tooling | Shared ownership; **shared tool, separate ownership** | **Separate ownership** | n8n is used by M28 and M63; Wazuh by M05 and M66. Shared tooling with unshared ownership must be explicit or the boundary erodes | Each owns its own workflows and credentials |

---

## 10. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A boundary taxonomy exists and every ruling names its kind | §3; §5 — 21 rulings |
| AC-02 | Boundary declarations across all 67 specifications are counted | §2.2 — 3,040 assertions |
| AC-03 | The symmetry check states what it can and cannot verify mechanically | §4.1, §4.2 — stated rather than overclaimed |
| AC-04 | Every boundary involving a module named 20+ times as owner is ruled | §2.3 lists 14 such modules; §5 covers all 14 |
| AC-05 | Every ruling carries a **test** a developer can apply unaided | §5 — every ruling |
| AC-06 | An adjudication procedure with a named arbiter and a time limit exists | §6 — one sprint |
| AC-07 | External boundaries carry an anticorruption rule | §7 — 6 boundaries |

**Definition of done.** Complete when every criterion is met, Q-01 (M23 ↔ M60) is ruled, and
`PGD-000`'s `AR-005` row is updated with a fresh enumeration timestamp.

---

## 11. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `AR-001` §6.5 | Boundary rules LB-01…LB-09 that these rulings apply |
| Upstream | `AR-008` | Aggregate boundaries — finer than module boundaries; Q-01 depends on it |
| Downstream | `AR-003` | Design gate entry condition E-03 requires boundaries adjudicated |
| Downstream | `AR-006` | §5.4, §5.10, §5.15, §5.19 rulings resolve four of the eleven cycles |
| Downstream | `AR-012` `FF-15` | Mechanises SC-05 and SC-06 |
| Downstream | `BE-005` | CD allocation follows capability ownership |
| Downstream | `05-01`, `RQ-005` | Requirement allocation follows these rulings (Q-04) |
| Lateral | `../../1000fix_ERP_Module/03_Modules/**/M*.md` §3 | 3,040 declarations this register verifies |

---

## 12. References

**Within this repository**
`../PGD-000_*.md` · `./_CATEGORY_OVERVIEW.md` · `./AR-001` · `./AR-003` · `./AR-004` · `./AR-006` ·
`./AR-008` · `./AR-012` · `../_AUDIT/PGD-AUDIT-003_*.md`

**Workspace**
`../../1000fix_ERP_Module/03_Modules/**/M*.md` §3.1, §3.2, §3.3 (all 67) ·
`../../1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md` §3 · `../../1000fix_ERP_Module/FOLDER_STRUCTURE.md` §7 ·
`.../05_Cross_Cutting_Specifications/05-01`, `05-05`

**External sources**

| Source | Verified |
|---|---|
| Eric Evans, *Domain-Driven Design* — bounded context, shared kernel, anticorruption layer, customer/supplier | 2026-08-18 |
| ISO/IEC/IEEE 42010:2022 | 2026-08-18 |

---

## 13. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Replaces the never-written `02-03`. 21 boundaries adjudicated; five-kind taxonomy; adjudication procedure with a one-sprint limit. Raises `PGD-A3-12` (M23/M60 risk register) | *Pending — Design Authority not constituted* |

---

*`AR-005` · Category 02 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
