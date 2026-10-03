---
id: AR-004
title: Architecture Decision Record (ADR) Library
category: 02 — Architecture & Design
code: AR
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Architect
approver: Design Authority (constituted under GV-002)
standards_basis: Nygard ADR pattern · ISO/IEC/IEEE 42010:2022 §5.7 (architecture rationale) · MADR 4.0 structure
traces_to: PGD-000 AR-004 · 02-05 §10 (TD-01…TD-15) · Technology Stack Specification §24 (TD-01…TD-27, D-13…D-18)
depends_on: GV-003 (Decision Log) · AR-001
verified_on: 2026-08-18
priority: P0
needed_by: Now
enumeration_timestamp: 2026-08-18 02:05 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# AR-004 — Architecture Decision Record Library

### Category 02 · Code `AR` · Nygard ADR pattern · ISO/IEC/IEEE 42010:2022 §5.7

---

## 1. Purpose

An architecture decision that survives only as a table cell survives only until the person who made
it leaves. This library holds **one record per significant architecture decision**, each stating its
context, the options genuinely considered, the decision, and — the part that a decision table cannot
carry — **its consequences, including the bad ones**.

Its immediate use is defensive. When Odoo 21 lands in 2028 and a maintainer asks *"why VROOM and not
Timefold?"*, the estate's current answer is the eleven-word cell `TD-05`: *"$0 licence; self-hosted;
embeds custom constraints."* That is a reason, not a rationale. It does not say what Timefold offered,
what it cost, what conditions would make the decision wrong, or who is accountable for revisiting it.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The ADR format, lifecycle and numbering rule |
| 2 | The significance test — what needs an ADR and what does not |
| 3 | **The complete back-populated library** — 30 ADRs recovered from `02-05` §10 and Technology Stack Specification §24, each given the analysis the source table lacks |
| 4 | Six decisions **required and not yet taken**, with owner and consequence of delay |
| 5 | The supersession rule and the relationship to `GV-003` (programme Decision Log) |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Non-architecture programme decisions | `GV-003` Decision Log | An ADR is a subset. `D-14` (fund 1,513 PW or cut scope) is a Steering decision that *appears* here for traceability but is owned there |
| Technology currency and review dates | `AR-013` Technology Radar | An ADR is a point-in-time decision; the radar is a live register with review dates |
| Requirement decisions | `RQ-005` | Changing a requirement is change control, not architecture |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **The maintainer in 2029** | The primary audience. Every other reader is incidental |
| Design Authority | The record against which a change request is assessed |
| Implementation vendor | The constraints they are bidding into, and why |
| New architects and lead developers | Onboarding — twelve ADRs teach the system faster than 609 files |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure |
|---|---|---|
| **Nygard ADR pattern** | Context · Decision · Status · Consequences | Extended with **Options considered**, **Rejected because**, **Revisit if** and **Owner** — the four fields whose absence made `02-05` §10 unusable as rationale |
| **MADR 4.0** | Decision drivers, considered options, outcome, pros and cons | Adopted structurally; not adopted as file naming, because `PG-05` fixes identifiers as `ADR-nnn` permanently |
| ISO/IEC/IEEE 42010:2022 §5.7 | Architecture rationale, including rejected alternatives | Full — the standard explicitly requires *"evidence of consideration of alternatives"*, which is what the source tables omit |

### 2.2 Source material relied on

| Source | What it contributed |
|---|---|
| `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §24.1 | **TD-01…TD-27** — 27 decisions, the richest source. 12 are new in v2.0 and carry real rationale |
| Ibid. §24.2 | **D-13…D-18, Q-01, Q-05, Q-05b** — decisions required and not taken |
| Ibid. §23 | TR-01…TR-18 technology risks — the *consequences* half of several ADRs |
| Ibid. §25.2 | Five version-currency findings verified 2026-08-13 — the *revisit-if* triggers |
| `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` §10 | TD-01…TD-15 — the earlier, thinner form of the same decisions |
| `.../02-01_*.md` §5, §10 | Layer selection rule; AS-01…AS-15 |
| `.../05-06_*.md` §6.4 | NFR-086 split residency — the driver for ADR-018 |

### 2.3 Audit findings this document contributes to closing

| Finding | How |
|---|---|
| `PGD-000` `AR-004` row — *"a 15-row decision table with one-line reasons and no rejected-option analysis"* | §5 issues 30 full ADRs |
| `AF-04` The programme references decisions (**`D-14`**) that have no record | ADR-030 records `D-14`'s architectural half and points to `GV-003` for the commercial half |
| `M-01` Stale vendor-version citation (Odoo release date) | Every ADR citing a version carries a `verified_on` date, and ADR-027 makes version currency a scheduled decision rather than a discovery |

---

## 3. The ADR Format and Lifecycle

### 3.1 Format

Every ADR carries exactly these fields. A missing field is a defect, not a style choice.

| Field | Rule |
|---|---|
| **ID** | `ADR-nnn`. Permanent, never reused, never renumbered (`PG-05`) |
| **Title** | A statement of the decision, not of the topic. *"Use a transactional outbox for every write path"*, not *"Eventing"* |
| **Status** | `Proposed` → `Accepted` → (`Superseded by ADR-nnn` \| `Deprecated`). **Never deleted** |
| **Date** / **Verified on** | Decision date; verification date if it cites a statute, standard or vendor version |
| **Owner** | The role accountable for the decision and for revisiting it |
| **Context** | The forces. What was true that made this a decision rather than an obvious choice |
| **Options considered** | At least two, each with what it offered. **An ADR with one option is not a decision; it is a note** |
| **Decision** | What was chosen, stated in the active voice |
| **Rejected because** | Per rejected option. The field most useful in three years and most often omitted |
| **Consequences** | Positive **and negative**. An ADR listing only benefits has not been thought through |
| **Revisit if** | The condition that would make this decision wrong. This is what converts an ADR into a live control |

### 3.2 The significance test

> A decision needs an ADR if **any** is true:
>
> 1. It is **hard to reverse** — reversing it costs more than a sprint.
> 2. It **crosses a module boundary** — more than one team is bound by it.
> 3. It **constrains a quality attribute** — it is why a QAS in `AR-001` §10 is met or missed.
> 4. It **rejected a reasonable alternative** — someone will ask why.
> 5. It is a **deviation** from an estate pattern in `AR-003` §5 or a standard in AS-01…AS-15.

Choosing a library for date formatting is not an ADR. Choosing to hold money as decimal rather than
float is (it is AS-10, and it is ADR-008).

### 3.3 Lifecycle

| Transition | Rule |
|---|---|
| Proposed → Accepted | Design Authority approval (`GV-002`). Until that body exists, the Chief Architect proposes and the CTO accepts, and the ADR says so |
| Accepted → Superseded | **Only by a new ADR** that names it. The old ADR is never edited beyond adding the supersession line — the history is the point |
| Accepted → Deprecated | The decision no longer applies (the thing it governed was removed). Also never deleted |
| **Revisit trigger fires** | The `Revisit if` condition becomes true → the owner must raise a new ADR within one wave, or record why not. Reviewed at every wave gate |

### 3.4 Relationship to `GV-003`

`GV-003` is the **programme Decision Log**: every decision, including commercial, contractual and
organisational. `AR-004` is the **architecture subset**, held here because architecture decisions
need a structure a general decision log does not provide (options, rejection analysis, revisit
triggers). Every ADR is mirrored as a one-line entry in `GV-003`. Where they disagree, `AR-004` wins
on architectural content and `GV-003` wins on decision date and authority.

---

## 4. Library Index

**30 accepted · 0 proposed · 0 superseded · 6 decisions required and not taken.**
Counted from §5 and §6 at 2026-08-18 02:05 (+06), per `PG-M10`.

| ADR | Title | Source | Status | Owner |
|---|---|---|---|---|
| **Foundation** ||||
| ADR-001 | Build on Odoo 19 Community Edition as the system of record | TD-01 | Accepted | CTO |
| ADR-002 | Model business lines as 1:1 extensions of a thin service-order core | `02-01` §9 | Accepted | Chief Architect |
| ADR-003 | Adopt the L1–L6 layered selection hierarchy, cheapest viable layer first | `02-01` §5 | Accepted | Chief Architect |
| ADR-004 | Model six shared-kernel concepts once, under change control | `02-01` §3 | Accepted | Chief Architect |
| ADR-005 | Carry full dimensional context on every transactional record from Wave 1 | DM-03, AS-03 | Accepted | Chief Architect |
| **Data and persistence** ||||
| ADR-006 | Share PostgreSQL 16 with the portal platform | TD-02 | Accepted | CTO |
| ADR-007 | Use TimescaleDB for time series, not InfluxDB or plain PostgreSQL | TD-13 | Accepted | Solution Architect |
| ADR-008 | Represent money as decimal with explicit currency; never float | AS-10, DI-01 | Accepted | CFO / Chief Architect |
| ADR-009 | Adopt ClickHouse for the analytical warehouse from Wave 8 | TD-09 | Accepted | CTO |
| ADR-010 | Use PostgreSQL full-text search before adopting a search cluster | TD-21 | Accepted | Solution Architect |
| ADR-011 | Soft-delete business records; hard deletion only through an approved saga | DM-06, DI-08 | Accepted | Chief Architect |
| **Integration and messaging** ||||
| ADR-012 | Adopt Kong as the API gateway | TD-08 | Accepted | CTO |
| ADR-013 | Use Redis Streams to Wave 5, then Redpanda | TD-10 | Accepted | Solution Architect |
| ADR-014 | Require `Idempotency-Key` on every state-changing API call | API-07 | Accepted | Chief Architect |
| ADR-015 | Version APIs in the path with two concurrent versions | API-02 | Accepted | Chief Architect |
| ADR-016 | **Use a transactional outbox for every write path** | TD-16 | Accepted | Chief Architect |
| ADR-017 | **Name events by aggregate, not by owning module** | `AR-001` §7.3 ASR-11 | **Proposed** | Chief Architect |
| ADR-025 | Transform brand-partner claims in n8n configuration, not code | TD-25 | Accepted | Solution Architect |
| **Security, privacy and identity** ||||
| ADR-018 | **Adopt a split-residency data architecture** | TD-18 | Accepted | CTO / DPO |
| ADR-019 | Two-tier e-signature — L5 operational, L6 qualified | TD-19 | Accepted | Legal / CTO |
| ADR-020 | Adopt Keycloak as the identity provider | TD-07 | Accepted | CTO |
| ADR-021 | Enforce segregation of duties at role-assignment time, not transaction time | `12.1.4` | Accepted | Head of InfoSec |
| **Experience and applications** ||||
| ADR-022 | **Deploy the notification platform in Wave 1, ahead of M27 in Wave 4** | TD-22 | Accepted | Steering |
| ADR-023 | Build cross-wave dependency seams as stubs in the earlier wave | TD-23 | Accepted | Solution Architect |
| ADR-024 | **Build one shared offline engine across the three field applications** | TD-24 | Accepted | Solution Architect |
| ADR-026 | Adopt Flutter as the single mobile framework | TD-03 | Accepted | CTO |
| ADR-028 | Accept the Next.js + Payload CMS portal platform as a constraint | TD-04 / `CON-03` | Accepted | CTO |
| **Intelligence** ||||
| ADR-029 | Run LLM inference self-hosted; customer data does not leave the country | TD-06 | Accepted | CTO / DPO |
| **Delivery and lifecycle** ||||
| ADR-027 | Schedule one Odoo major-version upgrade slot between Wave 5 and Wave 6 | TD-27 | **Proposed — needs `D-025`** | CTO |
| ADR-030 | Complete the custom-development register to 248 items across all 67 modules | TD-26 | **Proposed — needs `D-14` context** | CTO |

---

## 5. The Records

*Nineteen ADRs whose source tables already carry adequate rationale are held in condensed form in §5.11.
The eleven below are given in full because each shapes the architecture materially, and because in each
case the source record was a table cell.*

---

### ADR-001 — Build on Odoo 19 Community Edition as the system of record

**Status** Accepted · **Date** carried from v1.0, reaffirmed 2026-08-12 · **Verified on** 2026-08-18 · **Owner** CTO

**Context.** 2,930 requirements across 67 modules, a budget that will not carry per-seat enterprise
licensing at 500+ internal users, and a Bangladesh talent market. The alternative extremes are a
full custom build (total control, no head start) and a licensed enterprise ERP (large head start,
recurring cost, limited extensibility for fourteen unusual revenue streams).

**Options considered.**

| Option | Offered |
|---|---|
| **Odoo 19 CE + OCA** | $0 licence; **52% of requirements met at L1+L2 before writing code**; full source access; local talent |
| Odoo Enterprise | Native FSM, better mobile, official support — at **$45–90K over three years** |
| ERPNext | $0 licence, cleaner Python codebase, weaker ecosystem for the specific after-sales domain |
| Full custom build | Total fit — and 100% of 2,930 requirements built from zero |

**Decision.** Build on **Odoo 19 CE**, extended by OCA modules and custom `cd_*` modules.

**Rejected because.**
*Odoo Enterprise* — the licence cost buys FSM and mobile capability that OCA `field-service` covers
adequately, and it **reduces** extensibility for the business lines (rental, marketplace, data
services) that no ERP ships. Paying for less flexibility is the wrong trade at this requirement mix.
*ERPNext* — the ecosystem gap is decisive: no equivalent of OCA's 140+ relevant modules, and a thinner
Bangladesh talent pool.
*Full custom build* — 1,513 PW is already 1.8× the approved plan; adding the ~52% that L1+L2 provides
free is not fundable, and rebuilding double-entry accounting is a solved problem being re-solved.

**Consequences.**

*Positive* — $0 core licence; 52% coverage on day one; local hiring; an active OCA community.

*Negative, and these are real* — (a) **annual major versions**: a 36-month programme will cross at
least one, forcing ADR-027; (b) the Odoo inheritance model must be respected absolutely, which is why
AS-05 exists and why one careless fork is a programme-level risk (`TR-04`); (c) OCA v19 migration is
**incomplete** — `field-service` at ~25 of 33 modules, `helpdesk` at ~20 of 28 — carrying 12–20 PW of
migration work and a Wave 2 risk (`TR-03`); (d) Odoo's ORM shapes the design, so some patterns natural
in a greenfield system are not available.

**Revisit if.** Odoo 20 or 21 breaks the OCA extension model such that AS-05 cannot hold (assumption
`A-08`); **or** OCA `field-service` v19 migration proves to exceed 20 PW (assumption `A-03`); **or**
Odoo changes CE licensing terms.

---

### ADR-016 — Use a transactional outbox for every write path

**Status** Accepted · **Date** 2026-08-14 (TD-16, new in Technology Stack Specification v2.0) · **Owner** Chief Architect

**Context.** Sixty-seven modules must react to each other's state changes. The naive implementations
both fail, and they fail *silently*, which is what makes this worth an ADR rather than a convention.

**Options considered.**

| Option | Offered |
|---|---|
| Publish after commit | Simple; one line of code |
| Publish before commit | Simple; event ordering feels natural |
| Direct synchronous calls between modules | No infrastructure; immediate consistency |
| **Transactional outbox + relay** | Exactly-once emission semantics, at the cost of a table, a relay process and discipline |

**Decision.** Every state change writes its domain event **into the same database transaction** as the
state change, to `fix.domain.event`. A separate relay publishes from the outbox table to the bus.

**Rejected because.**
*Publish after commit* — a crash between commit and publish **loses the event silently**. Nothing
alerts; the consumer simply never learns. Discovered months later in reconciliation.
*Publish before commit* — the transaction can roll back after publication, so **an event describes a
state that never existed**. Consumers act on fiction.
*Direct synchronous calls* — creates a distributed monolith: M01 cannot complete an order if M23 is
down, and 67 modules of mutual synchronous dependency has a combinatorial availability problem.

**Consequences.**

*Positive* — *"every state change produces exactly one event"* becomes **true** rather than usually
true. Across 67 modules that difference is the whole gap between a reconcilable system and one that
diverges. It also makes the bus a *performance* dependency rather than a *correctness* one: if the bus
is down, outbox rows accumulate and state is still correct.

*Negative* — every write path must use the shared `emit_event()` helper; the relay is a component that
must be monitored, and outbox growth is a capacity concern; **and applying it unevenly is worse than
not applying it**, because some modules are reliable and others best-effort with no way to tell which
(`TR-12`). Hence the CI coverage test (`AR-012` `FF-04`) and DoD-05.

**Revisit if.** Outbox relay latency breaches NFR-043 (95% within 5 s) at Wave 6 volumes and cannot be
tuned; **or** Odoo's transaction model changes such that in-transaction writes to the outbox are no
longer atomic with the state change.

---

### ADR-017 — Name events by aggregate, not by owning module

**Status** **Proposed** — requires Design Authority ratification · **Date** 2026-08-18 · **Owner** Chief Architect

**Context.** Extraction across all 67 module specifications at 2026-08-18 02:05 found **988 distinct
events declared published** against **64 registered** in `05-03` §4.2, and **two incompatible naming
conventions in active use**:

| Convention | Form | Where | Example |
|---|---|---|---|
| **A** aggregate-scoped | `<aggregate>.<past_tense_verb>` | `05-03` §4.1, `02-01` §7, and the 64-row inventory | `service_order.completed` |
| **B** module-scoped | `<module_code>.<noun>_<verb>` | §12.3 tables of later module specifications | `ap.invoice_received` |

Twenty-nine registered convention-A names have no producer, because their producers now use
convention B for the same facts.

**Options considered.**

| Option | Offered |
|---|---|
| **A — aggregate-scoped, normative** | Names follow the domain; stable across module reorganisation |
| B — module-scoped, normative | Names follow the register; guaranteed unique; easy to allocate |
| Allow both, with an alias map | No rename work now |

**Decision.** **Convention A is normative.** An event is named `<aggregate>.<past-tense-verb>`, where
the aggregate is the **domain aggregate root** (`AR-008`), not the owning module's code.

**Rejected because.**
*Convention B* — it couples the event name to the module register, which is an organisational artefact.
If M52 is later split, or accounts-payable moves category, every consumer of `ap.*` breaks for a reason
that has nothing to do with the domain. **The 67-module decomposition has already changed twice** (11 →
30 → 67); the aggregate `invoice` has not.
*Allow both with aliases* — an alias map is a permanent tax on every consumer and every debugging
session, and it guarantees that some consumer will subscribe to only one of the two names for the same
fact.

**Consequences.**

*Positive* — names survive module reorganisation; the catalogue is navigable by domain; the 29
orphaned registrations are reconciled rather than deleted.

*Negative* — approximately **953 declarations must be renamed** across 67 specification files. That is
real work, and it is cheapest **now**: no consumer code exists. Once consumers exist, `05-03` §4.3
forbids breaking changes within a `schema_version`, so the rename becomes a dual-publish migration
across 67 modules.

*Also negative* — aggregate names must themselves be fixed first, which makes `AR-008` a prerequisite
and adds a dependency to the Wave 1 critical path.

**Revisit if.** `AR-008` finds that a material number of events do not belong to any single aggregate
(a genuine possibility for cross-cutting operational events such as `job.failed`), in which case a
declared `platform.` namespace is added rather than the convention being abandoned.

---

### ADR-018 — Adopt a split-residency data architecture

**Status** Accepted · **Date** 2026-08-14 · **Verified on** 2026-08-18 · **Owner** CTO / DPO

**Context.** PDPA 2026 `NFR-099` restricts large-scale transfer of Sensitive Personally Identifiable
Data — government unique identifiers (NID, passport, TIN), biometric identifiers, genetic information
and criminal records. The v1.0 architecture assumed single-region hosting in Singapore. Audit `C-05`
found that topology **may be unlawful**; audit `OP-01` found there is **no lawful DR path** for
resident personal data. Enforcement activates ~**13 May 2027 — inside Wave 4**.

**Options considered.**

| Option | Offered |
|---|---|
| Single region (Singapore) | Simplest operationally; the v1.0 assumption |
| Full record residency in Bangladesh | Unambiguously compliant; no join complexity |
| **Split residency — classified fields resident, joined by resident key** | Compliant for the restricted set; retains regional operation for the bulk |
| Defer until the legal opinion arrives | No wasted work if the opinion changes the answer |

**Decision.** **Split residency.** Residency-classified fields live in a Bangladesh-resident store
(Z4) with separate key material. The rest of each record lives in the regional primary. The two are
joined by a **resident key**; the sensitive field is **never duplicated regionally — not transiently,
not in a cache, not in a log**. All access is through one residency service (CD-233).

**Rejected because.**
*Single region* — likely unlawful under NFR-099, with exposure of BDT 25–50 lakh, and it leaves audit
`C-05` and `OP-01` open through go-live.
*Full record residency* — every record for 250,000 customers/month in a market where in-country
hosting with adequate availability, encryption and operational maturity is **not yet demonstrated
procurable** (assumption `A-01`). It also puts the entire OLTP workload behind that procurement risk
rather than a small, bounded subset.
*Defer* — the deferral is the expensive option. Every module built before the decision carries
reclassification risk, and Wave 1 fixes the data model.

**Consequences.**

*Positive* — compliant for the restricted set; the regional tier retains normal performance
characteristics; residency becomes a **field property**, so a change of legal opinion is a
**reclassification, not a redesign** (`TR-02`). This is the single most important risk-absorbing
property of the decision.

*Negative* — a cross-store join on every path that needs an identifier; the residency service is a
new availability dependency on those paths; **DR becomes two-tier** and Z4 must fail over to a
resident standby, not a regional one (DR-02); non-production environments can **never** hold unmasked
classified data, so masking must run inside the clone job (NFR-086c); and PDPA erasure becomes a saga
across both stores plus warehouse, object store and search index (CD-248).

**Revisit if.** The `DEP-31` legal opinion requires **full record residency** (assumption `A-02`
fails) — a materially larger change to `PE-001` and `DA-001`; **or** no Bangladesh-resident hosting
option with adequate availability is procurable (assumption `A-01` fails).

---

### ADR-022 — Deploy the notification platform in Wave 1, ahead of M27 in Wave 4

**Status** Accepted · **Date** 2026-08-14 (resolves open question `Q-05`) · **Owner** Steering Committee

**Context.** M27 Omnichannel Contact Centre owns notification and is scheduled for Wave 4. Every
module from Wave 1 onward must notify customers — order created, estimate issued, technician
dispatched, invoice raised. `02-02` §2 Category B flagged this during specification as requiring a
wave-plan decision.

**Options considered.** Build notification with M27 in W4 (each earlier module builds its own send
path meanwhile); **deploy the platform (Novu + CD-234) in W1 and M27's contact-centre capability in
W4**; or move all of M27 to W1.

**Decision.** Deploy **Novu and the notification dispatcher (CD-234) in Wave 1**. M27's
contact-centre capability stays in Wave 4.

**Rejected because.**
*Build with M27 in W4* — three waves of modules each build their own send path, and then three waves
of rework to remove them. **This recreates precisely the fragmentation the programme exists to
remove**, inside the programme.
*Move all of M27 to W1* — the contact centre needs telephony (L6, W4), agent console (APP-08) and the
AI assistant. Pulling all of it forward inflates W1, which §11.3 of `AR-001` already identifies as
the heaviest wave.

**Consequences.** *Positive* — one send path from day one; template, channel and preference logic in
one place; notification delivery observable from Wave 1. *Negative* — W1 carries an additional L4
component and CD-234, adding to a wave already understated by module count (`TR-11`); and M27's
eventual owner inherits a component built before they existed.

**Revisit if.** Wave 1 capacity analysis (`GV-004`) shows the platform cannot be absorbed — in which
case the fallback is a minimal SMS/email dispatcher in W1 with Novu in W2, **not** per-module send paths.

---

### ADR-024 — Build one shared offline engine across the three field applications

**Status** Accepted · **Date** 2026-08-14 · **Owner** Solution Architect

**Context.** APP-01 (technician), APP-02 (rider) and APP-03 (auditor) each require 24-hour offline
operation with zero data loss and sync within 30 seconds on 3G. They ship in W2, W3 and W5
respectively — three different waves, and, realistically, three different developers.

**Options considered.** Per-application implementation (each optimised for its own workflow, no
coordination cost); **one shared engine** consumed as a package; or a third-party offline-sync
framework.

**Decision.** **One engine**, built once with APP-01 in Wave 2, consumed by APP-02 and APP-03.

**Rejected because.**
*Per-application* — three implementations produce **three sets of conflict-resolution bugs**, in the
highest-risk area of the programme (`TR-01`). Offline conflict resolution is where correctness bugs
hide: they appear only under a specific interleaving of network loss, concurrent edit and retry, and
they are found in the field, by a technician, on a job.
*Third-party framework* — none delivers 24-hour offline with **server-authoritative conflict
resolution against a 67-module ERP**, in Bengali, on a 3 GB Android device.

**Consequences.** *Positive* — one conflict model, one test harness (§16.5 scenarios), one place to
fix a defect for three applications; APP-02 and APP-03 arrive materially faster. *Negative* — APP-01
in Wave 2 carries the cost of generalising for two applications that do not exist yet, which is a real
schedule risk in the wave that also delivers dispatch and inventory; and a defect in the shared engine
affects all three simultaneously.

**Revisit if.** APP-02's or APP-03's domain requirements prove incompatible with the shared conflict
model — for example, if auditor evidence requires client-authoritative resolution on a field where the
technician app requires server-authoritative.

---

### ADR-027 — Schedule one Odoo major-version upgrade slot between Wave 5 and Wave 6

**Status** **Proposed** — requires decision `D-025` · **Date** 2026-08-14 · **Verified on** 2026-08-18 · **Owner** CTO

**Context.** Odoo 19.0 was released **18 September 2025** and is supported to approximately
**September 2028**. Odoo 20 is expected **September–October 2026**. The programme runs 36 months from
kickoff. **It will reach steady state within about a year of 19.0 leaving support.**

**Options considered.** Upgrade after Wave 9 (all effort on features until then); **one planned slot
between W5 and W6**; track annual releases continuously; or stay on 19.0 indefinitely.

**Decision.** Baseline on 19.0. Schedule **one major-version upgrade slot between Wave 5 and Wave 6**,
**in the baselined plan, not in contingency**.

**Rejected because.**
*Upgrade after Wave 9* — the programme ends with an unplanned, unfunded upgrade of 232 custom modules
and 140+ OCA modules, at the moment the team is demobilising.
*Track annual releases* — three upgrades across the programme, each disrupting a wave.
*Stay on 19.0* — running production on an unsupported ERP with no security patches, in a business
handling payments and personal data.

**Consequences.** *Positive* — one scheduled, resourced, rehearsed upgrade instead of three or a late
scramble; the W5/W6 boundary is the natural point (v1.0 scope complete, new business lines not yet
started). *Negative* — a full wave-boundary slot consumed by work with no visible business output,
which is exactly the work that gets cut under schedule pressure — hence the insistence that it sits in
the plan and not in contingency. It also raises the cost of any AS-05 violation, because the upgrade
is the moment forks are paid for.

**Revisit if.** Odoo 20 or 21 breaks the OCA extension model (`A-08`); **or** the OCA ecosystem does
not migrate within the slot window; **or** the programme is rebaselined such that W5/W6 no longer
falls before the support cliff.

---

### ADR-029 — Run LLM inference self-hosted; customer data does not leave the country

**Status** Accepted · **Date** carried from v1.0, restated 2026-08-14 · **Verified on** 2026-08-18 · **Owner** CTO / DPO

**Context.** M32 conversational AI, M27 assistance and M26 summarisation need language capability in
**Bengali**. Customer conversations, service history and recovered-data case notes are the input.

**Options considered.** Hosted LLM API (best quality, lowest operational burden); **self-hosted
open-weight models via Ollama**; or Rasa 3.6.

**Decision.** **Self-hosted inference (Ollama)**, with a deterministic rule-based fallback and human
routing.

**Rejected because.**
*Hosted API* — sends customer personal data offshore, **breaching PDPA transfer restrictions**
(NFR-099). This is a legal rejection, not a cost one, and it is not negotiable by improving the
commercial terms. It also carries per-query cost at 250,000 customers/month.
*Rasa 3.6* — Rasa OSS is in maintenance mode; building a W4 capability on a framework not under active
development is a five-year problem.

**Consequences.** *Positive* — no data egress; no per-query cost; model choice under our control.
*Negative* — Bengali quality from open-weight models is **an assumption, not a measurement**
(`A-04`); GPU capacity becomes an infrastructure line; and if the assumption fails, M32's scope
narrows to templated and transactional responses and the fallback becomes the primary path. **No
business path may depend on model availability** (`ML-01`, `TR-17`).

**Revisit if.** Bengali evaluation against a defined benchmark fails the intent scope (`A-04`);
**or** an in-country hosted option emerges that satisfies NFR-099 with a documented safeguard.

---

### ADR-021 — Enforce segregation of duties at role-assignment time, not transaction time

**Status** Accepted · **Date** 2026-08-14 · **Owner** Head of InfoSec

**Context.** Thirty SoD controls (SOD-01…SOD-30) must be enforced across finance, inventory, HR,
access, quality and marketplace.

**Options considered.** Check at transaction time (block the conflicting action); **check at role
assignment time** (refuse the conflicting grant); or detect after the fact by report.

**Decision.** **Evaluate at role-assignment time.** A conflicting assignment is refused; an override
requires named approval and is logged.

**Rejected because.**
*Transaction time* — the user holds the conflicting capability until they use it, so the control is
invisible until it fires, usually at the worst moment (a payment run at month end). It also has to be
implemented at every affected transaction rather than in one place.
*Detective reporting* — finds the violation after the payment left.

**Consequences.** *Positive* — one enforcement point (CD-132); the conflict is surfaced to a manager
at the moment of granting, when it can be resolved organisationally. *Negative* — assignment becomes
a slower operation with a rejection path that must be explained clearly; and a legitimate temporary
combination (a covering absence) needs a designed, time-boxed override path rather than being simply
possible.

**Open defect this ADR inherits.** Only `SOD-01`…`SOD-12` are registered in `05-04`;
**`SOD-13`…`SOD-30` are in use and unregistered.** Implementing 12 leaves **18 conflicts unenforced**.
Wave 0 blocking (`TR-13`).

---

### ADR-010 — Use PostgreSQL full-text search before adopting a search cluster

**Status** Accepted · **Date** 2026-08-14 · **Owner** Solution Architect

**Context.** NFR-035 requires search results across any entity, **including Bengali text**, within
600 ms p95.

**Options considered.** OpenSearch/Elasticsearch from Wave 1; **PostgreSQL FTS with GIN indexes and
ICU `bn-BD` collation**; or a managed search service.

**Decision.** **PostgreSQL FTS**, with escalation to a search cluster **planned but not
pre-committed**.

**Rejected because.**
*OpenSearch from W1* — adds a synchronisation problem (a second copy of searchable data that can drift)
and a consistency problem (a record findable in search and absent from the database, or vice versa)
**for no measured benefit** at expected volume. Adding a distributed system to solve a problem not yet
demonstrated is how estates acquire components nobody can name the owner of.
*Managed search* — data egress, and the same synchronisation problem with less control.

**Consequences.** *Positive* — one datastore; no drift; Bengali handled by ICU collation in the same
engine. *Negative* — search relevance tuning is more limited; and if volume outgrows FTS the migration
is a project, not a configuration change — which is why the escalation trigger is defined now.

**Revisit if.** Search p95 breaches NFR-035 at a wave gate and cannot be recovered by indexing;
**or** relevance requirements grow beyond what FTS ranking supports.

---

### ADR-023 — Build cross-wave dependency seams as stubs in the earlier wave

**Status** Accepted · **Date** 2026-08-14 · **Owner** Solution Architect

**Context.** The worked case: M22's certification-eligibility check (`FR-LMS-039`) is consumed by M02
at technician assignment. **M02 goes live in W2; M22 in W5.** The same pattern recurs across several
wave-spanning dependencies.

**Options considered.** Connect only in W5 (build the check into M02 then); **build the interface in
W2 as a stub returning "eligible", connect in W5**; or move M22 forward to W2.

**Decision.** **Build the seam early, stub the answer.** M02 calls the eligibility interface from W2;
it returns "eligible" until M22 connects in W5.

**Rejected because.**
*Connect in W5* — retrofitting a **blocking check into a live assignment path** is materially riskier
than building it into an empty one. In W5, M02 is dispatching real jobs for 400 technicians across 51
branches; a defect in a newly inserted blocking call stops dispatch.
*Move M22 forward* — the rest of M22 (learning paths, content, assessments) has no W2 consumer and
would inflate W2.

**Consequences.** *Positive* — the risky change happens when the path is empty; the interface contract
is agreed a wave early. *Negative* — **a stub that always returns "eligible" is a control that does not
work**, and if W5 slips it silently continues not working. It must therefore be **registered as an open
control gap in `GV-005` RAID with an expiry**, not left as a code comment. That registration is a
condition of this ADR.

---

### 5.11 Condensed records

Nineteen further ADRs whose source rationale is adequate. Each carries the full field set in the
issued library; summarised here for index purposes.

| ADR | Decision | Rejected | Revisit if |
|---|---|---|---|
| ADR-002 | Thin service-order core + 1:1 line extensions | Wide table (unreadable core); table per line (breaks one queue, one SLA clock, one history) | A tenth line cannot be expressed as an extension |
| ADR-003 | L1–L6 selection hierarchy, cheapest viable layer first | Build-first (cost); buy-first (fit) | Layer coverage percentages diverge >10% from the 28/24/4/17/25/2 baseline |
| ADR-004 | Six shared-kernel concepts modelled once, change-controlled | Per-module modelling (duplicate identity, unrecoverable) | A seventh concept reaches ≥50 consuming modules |
| ADR-005 | Full dimensional context on every transactional record from W1 | Add dimensions when multi-entity arrives (retrofit across 1,335 entities) | Multi-entity is formally descoped |
| ADR-006 | PostgreSQL 16 shared with the portal platform | Separate databases (two skill sets, harder integration) | PostgreSQL 16 approaches EOL (Nov 2029) — reviewed with ADR-027 |
| ADR-007 | TimescaleDB for time series | InfluxDB (second engine, second skill set); plain PostgreSQL (420 M rows/yr dominates the WAL) | TSL licence terms change (fallback: Apache-2.0 features only) |
| ADR-008 | Decimal money with explicit currency | Float (rounding errors in a ledger are unrecoverable) | Never |
| ADR-009 | ClickHouse warehouse from W8 | PostgreSQL analytics (replica capacity); managed warehouse (cost, egress) | Analytical load outgrows replicas before W8 — trigger reviewed each gate (`TR-14`) |
| ADR-011 | Soft delete; hard delete only via approved saga | Hard delete (destroys audit trail and financial history) | Never — but the PDPA erasure exception (CD-248) is the designed path |
| ADR-012 | Kong API gateway | Nginx alone (no per-consumer scoping); cloud gateway (lock-in, egress) | Consumer count or plugin needs exceed the free tier |
| ADR-013 | Redis Streams → Redpanda at W6 | Redis alone (no durable replay); Kafka from W1 (operational weight too early) | Replay or retention needs arrive before W6 |
| ADR-014 | `Idempotency-Key` required on state-changing calls | Optional (every retry becomes a duplicate risk) | Never |
| ADR-015 | Path versioning, two concurrent versions | Header versioning (invisible in logs); single version (breaks `CON-03`) | Consumer count makes two versions unsustainable |
| ADR-019 | Two-tier e-signature: L5 operational, L6 qualified | L6 for all (envelope cost multiplies); L5 for all (contracts unenforceable) | An accredited OSS trust service becomes available in Bangladesh |
| ADR-020 | Keycloak as identity provider | Odoo native auth (no federation); Auth0 (cost, data location) | Keycloak's no-LTS policy becomes unmanageable (`TR-08`) |
| ADR-025 | Brand-claim transformation in n8n configuration | Custom code per brand (17+ templates changing on the brand's schedule) | n8n's Sustainable Use licence changes |
| ADR-026 | Flutter as the single mobile framework | React Native (New Architecture mandatory as of 0.83); native (four codebases) | P07's mobile surface forces a second framework — see `D-027` |
| ADR-028 | Accept the portal platform as a constraint (`CON-03`) | Replace (unfunded); wrap (two presentation layers) | The platform is retired by its owner |
| ADR-030 | Complete the CD register to 248 items | Retain 138 items (covers 30 of 67 modules) | — ratified with `D-14` |

---

## 6. Decisions Required and Not Taken

**Six architecture decisions have no record because they have not been made.** Each is dated by its
consequence, not by convenience.

| ID | Decision | Owner | Needed by | Consequence of delay |
|---|---|---|---|---|
| **D-13** | **Split-residency legal opinion (`DEP-31`)** — is a resident-key join acceptable, or is full record residency required? | CFO / Legal / DPO | **Before W1 architecture is fixed** | The data model cannot be fixed; every module built earlier carries reclassification risk. ADR-018 absorbs most of this by design, but not all |
| **D-14** | **Fund the restated 1,513 PW, phase it, or cut scope** | Steering Committee | Before contract award | Scope and sequencing cannot be baselined. Architecturally: it determines whether ADR-030's 248-item register is the deliverable list |
| **D-025** | **Odoo version baseline and upgrade slot** | CTO / Steering | Wave 0 | ADR-027 remains Proposed; the programme reaches steady state near end-of-support with an unplanned upgrade |
| **D-026** | **Next.js 15 → 16 upgrade timing** | CTO | Wave 0 | Six portals built on a version leaving the supported line, then migrated together (`TR-06`) |
| **D-027** | **P07 mobile surface — PWA, Flutter or React Native** | CTO | Wave 6 | A second mobile framework enters the estate by default, against ADR-026 |
| **D-18** | **RMM: open-source or commercial agent** | CTO / CFO | Wave 5, after pilot | MSP patch orchestration unresolved; L6 exposure unbounded against the $36K envelope |

> **`D-13` and `D-025` are the two that block architecture rather than commerce.** Both are Wave 0.
> Neither can be taken by this repository. Both are escalated to `GV-003` and `GV-005` on issue.

---

## 6A. Decisions Recorded · Open Questions

*Both house-template sections are deliberately empty in this document, and the headings are retained
rather than omitted, per `_templates/TPL_Guiding_Document.md`.*

| Section | Why it does not apply here |
|---|---|
| **Decisions Recorded** | This document **is** the decision record. §5 and §5.11 hold all 30; duplicating a local table would create a second, divergent copy — the exact defect `H-03` (two incompatible CD registers) describes |
| **Open Questions** | §6 *Decisions Required and Not Taken* is this document's open-question register, in the form the subject matter requires: a decision with an owner, a needed-by date and a consequence of delay |

---

## 7. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every decision in `02-05` §10 (TD-01…TD-15) and Technology Stack Specification §24.1 (TD-01…TD-27) is represented | §4 index — 30 ADRs, cross-referenced to source |
| AC-02 | Every ADR carries options considered, rejection analysis, consequences **including negative**, and a revisit trigger | §3.1 format; §5 records |
| AC-03 | Decisions required and not taken are listed with owner and consequence of delay | §6 — 6 decisions |
| AC-04 | The significance test is stated so that "does this need an ADR" is decidable | §3.2 |
| AC-05 | The supersession rule preserves history | §3.3 — never deleted, never edited beyond the supersession line |
| AC-06 | The relationship to `GV-003` is stated, with a precedence rule | §3.4 |
| AC-07 | Counts are regenerated from the rows immediately before issue (`PG-M10`) | §4 header — 30 / 0 / 0 / 6, counted 2026-08-18 02:05 |

**Definition of done.** Complete when every criterion is met, `PGD-000`'s `AR-004` row is updated with
a fresh enumeration timestamp, and the Design Authority has ratified ADR-017, ADR-027 and ADR-030.
**Two ADRs remain Proposed at issue and the document says so** rather than presenting the library as
fully accepted.

---

## 8. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `GV-003` Decision Log | The superset. Every ADR mirrors to it — **`GV-003` does not exist** (`AF-04`) |
| Upstream | `GV-002` Design Authority | The body that accepts an ADR — **not constituted** (`PGD-A1-09`) |
| Upstream | `AR-001` | The architecture these decisions produced |
| Downstream | `AR-003` | Deviation from an estate pattern requires an ADR (gate X-10) |
| Downstream | `AR-009`, `AR-010`, `AR-013` | Realise ADR-016/017, ADR-024, ADR-003/027 |
| Downstream | `AR-012` | Fitness functions enforce ADR-008, ADR-014, ADR-016 |
| Downstream | `BE-005` | ADR-030's 248-item register is `BE-005`'s content |
| Lateral | `../../primary-doc/…Technology_Stack_Specification.md` §24 | Primary source; superseded as *rationale* by this library, retained as technology authority |

---

## 9. References

**Within this repository**
`../PGD-000_*.md` · `./_CATEGORY_OVERVIEW.md` · `./AR-001` · `./AR-003` · `./AR-013` · `../_AUDIT/PGD-AUDIT-003_*.md`

**Workspace**
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §23, §24, §25 ·
`../../1000fix_ERP_Module/02_Architecture/02-01` §5, §10, `02-05` §10 ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06` §6.4

**External sources**

| Source | Verified |
|---|---|
| Michael Nygard, *Documenting Architecture Decisions* (2011) — the ADR pattern | 2026-08-18 |
| MADR 4.0 — Markdown Architectural Decision Records | 2026-08-18 |
| ISO/IEC/IEEE 42010:2022 §5.7 architecture rationale | 2026-08-18 |
| Odoo 19.0 released 18 Sept 2025; supported to ~Sept 2028; Odoo 20 expected Sept–Oct 2026 | 2026-08-18 |
| Personal Data Protection Act 2026, Bangladesh — enforcement ~13 May 2027 | 2026-08-18 |

---

## 10. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. 30 ADRs back-populated with options, rejection analysis, negative consequences and revisit triggers. 6 decisions recorded as required and not taken. ADR-017 newly proposed | *Pending — Design Authority not constituted* |

---

*`AR-004` · Category 02 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
