---
id: PGD-AUDIT-CAT-09
title: Category 09 Data Migration & Cutover — Authoring Integrity Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: FINDINGS ISSUED — 17 findings · 5 closed · 12 open
classification: CONFIDENTIAL — Internal Use Only
auditor: Enterprise Architecture
scope: >
  All 7 documents authored into project-guide-doc/09_Data_Migration_and_Cutover/ on 2026-08-18
  (MG-001 … MG-007, 357 KB, 257 governing rules), the updated _CATEGORY_OVERVIEW, and every
  factual claim they make about the workspace estate.
enumeration_start: 2026-08-18 21:55 (+06)
enumeration_close: 2026-08-19 09:40 (+06)
identifier_note: >
  Category-keyed, following PGD-AUDIT-CAT-07. Sequential allocation was not used because
  PGD-AUDIT-007 (Category 04) and PGD-AUDIT-008 (Category 05) were both claimed while this
  category was being authored. See PGD-A7-01 and finding MGA-05.
---

# Category 09 Authoring Integrity Audit
# `09_Data_Migration_and_Cutover/` — `MG-001` … `MG-007`

---

## 1. Purpose and Method

This audit is **mandatory under the commissioning instruction** and was performed on the seven
Category 09 documents immediately after authoring, before any consumer relied on them.

It applies the six methods established by `PGD-AUDIT-003` and extended by `PGD-AUDIT-005`, plus one
added because this category specifies **an operation performed against a live production system**
rather than only a design:

| # | Method | What was checked |
|---|---|---|
| 1 | **Structural consistency** | Front-matter completeness, house-section conformance, identifier uniqueness, link integrity |
| 2 | **Arithmetic consistency** | Every roll-up figure regenerated from its source rows immediately before issue (`PG-M10`) |
| 3 | **External verification** | Every extraction re-executed against the filesystem; commands recorded in §7.3 |
| 4 | **Temporal verification** | Whether the estate changed during authoring |
| 5 | **Cross-document consistency** | Whether a rule stated in one document is used consistently in the others, and against Categories 00–08 and 12 |
| 6 | **Regulatory verification** | Statutory claims checked, with evidentiary standing recorded |
| 7 | **Operational executability** *(added)* | For every rule that must be executed during a cutover: can the named actor perform it, with the named artefact, in the named window? |

**Result: 17 findings — 2 critical, 5 high, 9 medium, 1 low. Five are closed; twelve remain open.**

> Counts regenerated from the §2 rows immediately before issue, per `PG-M10`. **The first draft of
> this line said "2 critical, 6 high, 8 medium — six closed", carried from the finding list as it
> stood mid-drafting.** It was wrong by one in three columns. Recorded in `MGA-16` §"A second
> instance", because an audit that reports a regeneration failure and then commits one has not
> understood its own finding.

### 1.1 Method 7 and why this category needed it

Categories 00–08 specify **designs**. A design can be complete and correct while the thing it
describes does not yet exist; that is normal and is what ⛔ means everywhere else in this register.

Category 09 specifies **an operation**: a named person performing a named act, at a named hour, on a
named artefact, with a clock running and a business waiting. **A rule that cannot be executed is not
a partially-complete design — it is a rule that will be broken on the night**, and the breaking will
be improvised.

Method 7 therefore asks three questions of every operational rule:

| # | Question | Example of a failure it caught |
|---|---|---|
| 7a | **Does the actor exist?** | `CUT-18` requires 6–8 Zone Coordinators; the organisation has no such role (`MGA-13`) |
| 7b | **Does the artefact exist?** | `CUT-34` requires numbered paper contingency pads; a search of all `DT` templates returns zero (`MGA-12`) |
| 7c | **Is it executable in the window?** | `CV-09` requires Bengali branch instructions; `CM-012`'s declared Bengali counterpart does not exist (`MGA-06`) |

**Nine of the seventeen findings below were caught by method 7 and by no other method.** They would
all have passed a structural, arithmetic and cross-reference audit unchanged.

### 1.2 What this audit does not claim

| # | Limit |
|---|---|
| L-01 | It does not verify that the seven documents are *sufficient* to execute a migration. Sufficiency is proved by `MG-005` `R3`, and no rehearsal has been performed |
| L-02 | It does not test the claims of `DM-001`…`DM-014`. Those were audited by `AUDIT-011`; this audit tests **whether Category 09 uses them correctly** |
| L-03 | It does not re-open `AUDIT-011`'s ten open findings. It records which are now specified and which remain both unspecified and unperformed (§4) |
| L-04 | Regulatory findings rest on the same secondary-source position `PGD-A5-03` established and carry the same *"requires legal confirmation"* label |

---

## 2. Findings Summary

| # | Finding | Sev | Status | Owner |
|---|---|:--:|:--:|---|
| `MGA-01` | **The migration tooling has no build component anywhere in the estate** | **CRITICAL** | OPEN | Chief Architect with `GV-007` |
| `MGA-02` | **The lawful basis for migration processing is recorded nowhere, and the first load is W1** | **CRITICAL** | OPEN | Legal Counsel with the DPO |
| `MGA-03` | A migration load emits ~0.5–0.9 M events into a live bus with a live notification consumer | **HIGH** | OPEN | Solution Architect |
| `MGA-04` | Sixth identifier collision: `MG-0n` schema rules against `MG-00n` documents | **HIGH** | **CLOSED** by design | Enterprise Architecture |
| `MGA-05` | The register cited two audits that did not exist when this category was written | **MEDIUM** | **CLOSED** | Programme Content Lead |
| `MGA-06` | **16 declared Bengali counterparts do not exist**, including the two the cutover depends on | **HIGH** | OPEN | Localisation Lead |
| `MGA-07` | Category 08 was authored concurrently; three seams with Category 09 are unreconciled | **MEDIUM** | OPEN | QA Lead with the Data Migration Lead |
| `MGA-08` | **Nine external verifications, none engaged, one with a three-month lead time** | **HIGH** | OPEN | CFO |
| `MGA-09` | `DM-002` `SI-01` and `MG-002` `LPX-06` now disagree on the extract gate | **MEDIUM** | OPEN | Programme Content Lead |
| `MGA-10` | Two named control registers do not exist, and a third is newly required | **MEDIUM** | OPEN | Data Migration Lead |
| `MGA-11` | `IV-14` voids a count outside its window; `RBK-27` preserves it across a fallback | **MEDIUM** | OPEN | Warehouse Manager |
| `MGA-12` | **The `P2` paper contingency has no forms** — verified, not repeated | **HIGH** | OPEN | Content Design |
| `MGA-13` | Three operational roles this category requires do not exist in the organisation | **MEDIUM** | OPEN | Programme Director |
| `MGA-14` | Absence claims in `AUDIT-011` and `DM-014` have decayed; `CM` and `OP` now exist | **MEDIUM** | **CLOSED** | This audit |
| `MGA-15` | The estate moved during authoring for at least the sixth recorded time | **MEDIUM** | OPEN | PMO |
| `MGA-16` | This session quoted four stale rule ranges in its own scope statements | **LOW** | **CLOSED** | This session |
| `MGA-17` | This session mis-cited two section numbers in its own traceability table | **MEDIUM** | **CLOSED** | This session |

**Two findings are against this authoring session's own work** (`MGA-16`, `MGA-17`), and both are of
the class this category exists to prevent: a citation that does not resolve. Both were caught by
methods 1 and 5 and are closed.

---

## `MGA-01` — The migration tooling has no build component anywhere in the estate

**Severity: CRITICAL · Status: OPEN · Owner: Chief Architect with `GV-007`**

### What was found

BRD `MIG-008` is a **P0 contractual requirement**: *"Migration tooling delivered to the Company,
repeatable and re-runnable."* It is the requirement that distinguishes a migration the Company owns
from one a consultant performed and left.

Four tests were run against the build estate at **2026-08-18 22:10 (+06)** and repeated at
**2026-08-19 09:40 (+06)** with the same result:

| # | Test | Result |
|:--:|---|---|
| 1 | `BE-005` items (331 across 79 units) whose description mentions *migration*, *ETL* or *cutover* | **0 of 331** |
| 2 | TSS §8.2 Block 3 services (`CD-233`…`CD-248`) scoped to legacy-to-ERP migration | **0 of 16** |
| 3 | Any `CD` unit owning the tooling `MIG-008` requires | **None** |
| 4 | `CD-SVC-nn`, the space `BE-005` §5.1 reserves for cross-cutting services | **Deliberately empty at that issue** |

The only transformation tooling declared anywhere in the estate is **`CD-243`, warehouse ETL, dbt,
Wave 4** — which loads a ClickHouse analytical warehouse, not the operational model, and arrives
**three waves after the first migration load.**

### Why it is Critical

`AUDIT_Checklist_Recurring.md` defines Critical as *"a required artefact assumed present when
absent."* Every one of the fourteen `DM` content files, and every one of the seven `MG` documents,
assumes a tool exists to execute what they specify. **It has no identifier, no wave, no effort
figure, no owner and no line in any plan**, while being a P0 contractual deliverable with a W1
consumption date.

This is `AUDIT-011` `DM-01` item 7 seen from the build side, and it is worse than `DM-01` recorded:
`DM-01` found the tooling *unspecified*. `MG-003` §3 now specifies it. **What this audit finds is
that nobody is going to build it**, because no register says anyone should.

### Consequence if unaddressed

| # | Consequence |
|:--:|---|
| 1 | The W1 load has no executable pipeline, and W1 migration is a gate criterion (`G1-05`) |
| 2 | `GV-007`'s build baseline (1,842 PW against 1,088 PW capacity, `BEA-06`) omits it entirely — the real overrun is worse than measured |
| 3 | `MIG-008` is contractual; a vendor may reasonably read its absence from the CD register as its absence from scope |
| 4 | The alternative is improvisation, and an improvised loader is the one thing `ETR-12`, `SQ-04` and `LB-08` jointly forbid |

### Remediation instruction

1. **Allocate `CD-SVC-nn`** for the migration tooling under `BE-005` `CDR-01` — the Chief Architect's
   act, and `MG-003` `Q-01`/`Q-02` request it rather than performing it.
2. **Size it and add it to the build baseline** as part of the fifth work stream `BE-005` `BEA-05`
   already refers to `GV-007`.
3. **Set its wave to W0**, not W1: `MG-005` requires a rehearsal at T−45 days against a working
   pipeline, so the tool precedes the wave that uses it.
4. Record it in `GV-005` as an issue, not a risk — the consumption date is fixed.

---

## `MGA-02` — The lawful basis for migration processing is recorded nowhere, and the first load is W1

**Severity: CRITICAL · Status: OPEN · Owner: Legal Counsel with the Chief Data Officer**

### What was found

At W1 the migration processes **100,000+ customer records, 100,000+ addresses and an estimated
300,000–600,000 device records** into a new controller environment.

Two obligations attach, and both are recorded in the estate:

| Obligation | Source |
|---|---|
| Personal data migrated **only with a lawful basis recorded**, and transparency notice obligations addressed | BRD `MIG-015` |
| A transparency notice **before or during processing** | `05-06` §PDPA `NFR-092` |

`M33` §16.4 rule 2, adopted as `DM-001` `MS-20`, correctly prohibits *inferring* consent from prior
dealings. **The consequence nobody has followed through is arithmetical: if consent is not the
basis, some other basis applies, and no document in the estate names one.**

Re-verified at this audit:

| Artefact | State on disk |
|---|---|
| `LG-008` Privacy Notice and Consent Copy | Written 2026-08-17, `Draft`, registered **W2** |
| `LG-012` Cross-Border Transfer and Residency Statement | Written 2026-08-17, `Draft`, registered **W2** |
| `SC-003` DPIA (PDPA 2026) | **Issued.** Assesses the processing; a DPIA assesses, a controller decides |
| Any document naming the lawful basis for the migration itself | **None found** |

### Why this is reported again rather than deferred to `AUDIT-011` `DM-10`

`AUDIT-011` `DM-10` raised the **notice timing**. This finding raises the **basis itself**, which is
the prior question, and it now has a hard consequence in a controlled document: **`MG-001` `MST-21`
blocks every production load of personal data until the basis is recorded in `GV-003`.**

That rule was written deliberately and its discomfort is the point. It converts a standing legal
ambiguity into a **P0 blocker against a W1 gate criterion**, which is where it belongs and where it
will now be seen.

> This is the **third** finding in the programme about the *lawfulness* of a planned activity rather
> than its correctness — after `AUDIT-010` `HC-01` (transcript mining, W2) and `AUDIT-011` `DM-10`
> (notice timing, W1). It lands at the largest population and the earliest wave of the three.

### Remediation instruction

1. **Determine and record the lawful basis** for a bulk controller-side migration of the existing
   customer, device and employee base, in `GV-003`, with a named legal owner.
2. Move the transparency-notice obligation to **W1**, or record in writing why W2 is compliant.
3. Raise in `GV-005` as an **issue**, not a risk: the processing date is fixed and the basis is
   absent.
4. `CG-013` legal escalation applies. **This cannot be closed by the engineering or content
   functions**, and no `MG` document claims to close it.

---

## `MGA-03` — A migration load emits ~0.5–0.9 M events into a live bus with a live notification consumer

**Severity: HIGH · Status: OPEN · Owner: Solution Architect with the `AR-009` author**

### What was found

Three facts, each established independently and each correct on its own:

| # | Fact | Source |
|:--:|---|---|
| 1 | **An outbox row is written in the same database transaction as every state change.** The outbox is mandatory and uniform application is a stated risk (`TR-12`) | `05-02` `DM-15`; `AR-009` §5 |
| 2 | The migration load path is the **Odoo ORM**, because every alternative bypasses constraints, computed fields, `_inherit` behaviour and the outbox itself | `MG-003` `ETR-12`, `MG-003-D-01` |
| 3 | **`CD-234`, the notification dispatcher fronting Novu, is a Wave 1 component** — TSS: *"Novu + CD-234 deploys in Wave 1, three waves ahead of M27 itself"* | TSS §8.2, §14 |

**Together they mean that a W1 party and device load publishes on the order of 0.5–0.9 million
domain events into a live bus whose consumers include a live notification dispatcher.**

Order of magnitude, from `DM-001` §4.2 and `M17` §16.4: 100,000+ parties, 100,000+ addresses,
300,000–600,000 devices, ~50,000 service orders, plus dependants.

### Why no existing document catches it

Because it is invisible from either side alone. `AR-009` designs an event architecture for a running
system and never contemplates a bulk load. `DM-003` sequences a bulk load and never contemplates the
outbox except as a **contention** risk — `SQ-07` warns that outbox contention *"is invisible until
volume"*, which is the same table seen as a performance problem rather than a publication one.

**No document in the estate owns both, which is precisely the class of defect a guiding-document
category is supposed to surface.**

### Consequence if unaddressed

| # | Consequence | Reversible? |
|:--:|---|:--:|
| 1 | **A welcome or status message to every customer 1000FiX has ever had** | **No** |
| 2 | Webhook and partner push to 17+ brand partners (`IN-006`) | No |
| 3 | Consumer backlogs measured in hours at a moment when the cutover window is the constraint | Yes, expensively |
| 4 | A search-index or read-model rebuild triggered as a side effect rather than as a step | Yes |

### What `MG-003` does about it, and what it cannot do

`MG-003` §13 specifies a **migration execution context**: outbox rows are written with
`origin = migration` and a batch id, **retained** for lineage, and **not published** by the relay
unless a named event type is explicitly enabled for that batch (`ETR-44`…`ETR-47`). `ETR-48`
requires the rehearsal to prove that zero outbound messages were emitted, and `MG-005` `DRH-19`
adds a second, independent control: the rehearsal environment has no outbound path at all.

**`MG-003` cannot bind `AR-009`.** The `origin = migration` concept belongs in the event
architecture, not in a migration document that references it.

### Remediation instruction

1. **`AR-009` adopts the `origin = migration` outbox attribute and the relay's default-suppress
   behaviour** in its §5, as a design element of the event architecture.
2. Record the decision as an ADR in `AR-004`.
3. Add a fitness function (`AR-012`) asserting that no relay publishes a migration-origin row
   without an explicit per-batch enablement.
4. `MG-003` `Q-03` carries the dependency; it is on the W1 critical path.

---

## `MGA-04` — Sixth identifier collision: `MG-0n` schema rules against `MG-00n` documents

**Severity: HIGH · Status: CLOSED by design · Owner: Enterprise Architecture**

### What was found

The category code `MG` was already in use as a **local rule prefix** before Category 09 was written:

| Space | Meaning | Where | Count |
|---|---|---|---:|
| **`MG-001`…`MG-007`** | **The seven guiding documents of Category 09** | `PGD-000` | 7 |
| `MG-01`…`MG-08` | **Schema-change rules** — forward-only, two-release column removal, `CONCURRENTLY` index creation | `DA-001` §12 | 8 |
| `MG-07` | *A different* schema-change rule — residency migrations through `CD-233` | `AR-007` §MG | 1 |

`DA-001` §13 already cites *"`MG-003` ETL design"* as a document **in the same file** that defines
`MG-01`…`MG-08` as rules. The two spaces are distinguishable only by digit count, which is exactly
the failure `CG-005` §3.3 registered for `DM`, `AUDIT-011` `O-07` registered for `MIG`, and
`AUDIT-011` `DM-11` registered for `TPL-DM`.

A second, independent collision was also found:

| Space | Meaning | Where |
|---|---|---|
| `MS-00`…`MS-12` | **Programme milestones** | `GV-004` §6.1 |
| `MS-01`…`MS-26` | **Migration standards** | `DM-001` §4.9 |

**Both are live, both are cited across documents, and `DM-001` `MS-23` and `GV-004` `MS-11` are
routinely cited in the same context — migration and schedule.**

### How it was closed

**By yielding, and by verifying before allocating.** Category 04 set the precedent when it yielded
`FF-36`/`FF-37` and `PGD-AUDIT-006`.

1. **No `MG` document uses `MG-nn` as a local rule prefix.** `MG-001`'s identifier notice states all
   four colliding spaces on its first page.
2. **`MS-nn` is not used in this category**, explicitly, and the reason is stated.
3. Seven distinct prefixes were allocated — `MST`, `LPX`, `ETR`, `RVP`, `DRH`, `CUT`, `RBK` — and
   **each was verified to return zero occurrences workspace-wide before use**. Command in §7.3.
4. `MST-03` makes it a hard rule: no `MG` document allocates into `MS-`, `SI-`, `SQ-`, `DQ-`, `LT-`,
   `RV-` or `CV-`.

### The residual, which is not closed

**This is the sixth identifier collision in this repository, and the fix has now been recommended
six times and executed zero times:** write `RR-002` (Identifier Convention Standard) and ratify
`RG-08` (timestamped enumeration).

> Verifying a prefix before allocating it is a **workaround that depends on every future author
> remembering to do it**. `RR-002` is the control. Its absence is `PGD-A7-01`, and this audit adds
> the sixth data point rather than a seventh recommendation.

### The finding generalises — four more categories will hit it

Rather than record this as one category's misfortune, the test was run across **every unauthored
category code**, counting existing uses of `<CODE>-nn` as a **local rule prefix** anywhere in the
workspace. Measured 2026-08-19 09:45 (+06):

| Category | Code | `CODE-nn` already in use as a rule prefix | Collides on authoring? |
|:--:|:--:|---:|:--:|
| 08 Quality Engineering & Test | `QA` | 0 | No |
| **09 Data Migration & Cutover** | **`MG`** | **70** | **Yes — this finding** |
| 10 Infrastructure, DevOps & Environments | `PE` | 0 | No |
| **11 Service Operations & Support** | **`SV`** | **2** | **Yes** |
| **12 Release, Deployment & Transition** | **`RL`** | **58** | **Yes** |
| **13 Training, Change & Adoption** | **`CH`** | **39** | **Yes** |
| **14 Commercial, Vendor & Contract** | **`CO`** | **50** | **Yes** |
| 15 Benefits, Measurement & Assurance | `BM` | 0 | No |
| 99 Reference, Registers & Glossary | `RR` | 0 | No |

**Four of the six remaining unauthored categories will hit the same collision**, and `RL` and `CO`
will hit it harder than `MG` did — 58 and 50 existing uses against `MG`'s 70, in spaces that are
cited across the delivery and commercial documents rather than confined to two architecture files.

> **This is what makes `RR-002` worth writing rather than working around.** The workaround — *verify
> the prefix before allocating it* — worked here because this session happened to check. **It is
> now known in advance that it will be needed four more times**, which converts a recurring accident
> into a scheduled one. The command is in §7.3 and takes two seconds; the standard that would make
> running it unnecessary has been recommended six times.

**Instruction to the authors of Categories 11, 12, 13 and 14:** run the §7.3 prefix-freedom command
before allocating any local rule identifier, state the collision in your document's first page as
`MG-001` does, and **do not use your category code as a rule prefix**.

---

## `MGA-05` — The register cited two audits that did not exist when this category was written

**Severity: MEDIUM · Status: CLOSED · Owner: Programme Content Lead**

### What was found

Enumerating `_AUDIT/` at **2026-08-18 21:55 (+06)**, immediately before authoring, returned **six
files**: `PGD-AUDIT-001` … `PGD-AUDIT-006`.

`PGD-000` v1.2 cites two audits that were not among them:

| Cited in the register | Present at 21:55? | Present at 09:40 on 2026-08-19? |
|---|:--:|:--:|
| `PGD-AUDIT-007` (Category 04 Integration & API) | **✘** | **✔** |
| `PGD-AUDIT-CAT-07` (Category 07 Build Engineering) | **✘** | **✔** |

Both now exist. A third, `PGD-AUDIT-008` (Category 05), also appeared during the same window and is
cited nowhere in the register.

### Why it is worth recording

**This is the inverse of the defect the register has recorded five times.** `PGD-A1-03`,
`AUDIT-016` `AP-17`, `PGD-AUDIT-002` §8, `PGD-A3-18` and `PGD-000` §0.5 all record the register
**lagging** the filesystem. Here the register **led** it: for some interval, a reader following two
citations in the master register would have found nothing at the path.

The effect is the same — a citation that does not resolve — and the cause is the same: **no
mechanism makes a register assertion and a filesystem state agree at a stated instant.**

### How it was closed

Both files now exist and both citations resolve, verified 2026-08-19 09:40 (+06). **Closed by the
passage of events rather than by any control**, which is itself the point: `RG-08` remains
unratified after six recommendations.

---

## `MGA-06` — 16 declared Bengali counterparts do not exist, including the two the cutover depends on

**Severity: HIGH · Status: OPEN · Owner: Localisation Lead with the Change Lead**

### What was found

`DM-014` `CV-09` is a hard rule: *"every freeze instant and instruction reaching branch staff is
stated in Bengali and English."* `MG-006` `CUT-23` extends it — the Zone Coordinator confirms
**comprehension**, not receipt.

`AUDIT-011` `DM-08` recorded the dependency as blocked because Category 16 held **zero files**.
**That is no longer true** (see `MGA-14`). `CM-012` and `CM-013` were written **2026-08-20**.

**The dependency is still blocked, and the reason has moved.** Every file in Categories 16 and 17
declaring `bilingual: yes` was checked against the filesystem for its named counterpart:

| Test | Result |
|---|---|
| `CM` and `OP` files declaring a `bn_counterpart` | Checked all |
| **Declared counterparts that do not exist on disk** | **16** |
| Among them | **`CM-012_Branch_Readiness_Communication_Checklist_BN.md`** — the file `CV-09` depends on |
| Among them | **`OP-014_Manual_Fallback_Procedure_Set_BN.md`** — the procedure set 51 branches work from during a rollback (`MG-007` §8) |

Counted 2026-08-19 09:10 (+06). Command in §7.3.

A second defect compounds it:

| File | Declared priority | Consumer's priority |
|---|:--:|:--:|
| `CM-012` Branch Readiness Communication Checklist | **`P1`** | **`P0`** — no cutover proceeds without branch readiness (`C2`) |
| `CM-013` Customer Migration and Transition Pack | **`P1`** | **`P0`** |

### Why it is High

A count sheet filled in wrongly at 51 sites produces an opening inventory position that is wrong at
51 sites, and `AUDIT-011` `DM-05` already establishes that the counters have **never done a formal
count**. `DM-014` §4.9 states it directly: branch staff *"are not uniformly English-comfortable"* and
*"every instruction must be Bengali-first"*.

**The rollback case is worse than the cutover case.** `OP-014` is the procedure set staff would work
from during a fallback — under time pressure, at night, at 51 sites — and it exists only in English.

### Remediation instruction

1. **Translate `CM-012`, `CM-013` and `OP-014` first**, ahead of the other thirteen; they are the
   three on a cutover critical path.
2. **Re-register `CM-012` and `CM-013` as `P0`**, matching their consumer.
3. Add a check to the content-governance gate: **a file declaring `bilingual: yes` whose named
   counterpart is absent fails the gate.** Sixteen instances passed undetected.
4. `MG-006` `Q-03` and `MG-005` `Q-04` carry the dependency.

---

## `MGA-07` — Category 08 was authored concurrently; three seams with Category 09 are unreconciled

**Severity: MEDIUM · Status: OPEN · Owner: QA Lead with the Data Migration Lead**

### What was found

Enumerating `project-guide-doc/` at **2026-08-18 21:55** returned **119 files** and Category 08 held
only its `_CATEGORY_OVERVIEW`. Re-enumerating at **2026-08-19 09:30** returns **136 files**, and
Category 08 holds **7 of its 11 `QA` documents** — `QA-001` … `QA-007`, all created during the
window in which Category 09 was being written.

Three seams are now live and none is reconciled:

| # | Seam | Category 09 position | Category 08 position | Risk |
|:--:|---|---|---|---|
| 1 | **Business UAT before cutover** | `MG-005` `R2` — trial migration with business UAT, BRD `MIG-005` | `QA-002` defines a UAT test level | Two documents scheduling the same business people for overlapping activity |
| 2 | **Test-data masking and provisioning** | `MG-001` §7 — `migration-staging` is **production-class, unmasked**; `staging` is masked | `QA-004` Test Data Management and Anonymisation Plan | If `QA-004` claims all non-production data is masked, it contradicts `MG-001-D-02` |
| 3 | **Migration defect classes** | `MG-005` §9.3 `D1`–`D5`; `DM-013` `E1`–`E9` | `QA-010` defect taxonomy *(not yet written)* | A third defect space, unreconciled with two existing ones |

Category 09 corrected three stale ⛔ claims about `QA-001`, `QA-002` and `QA-004` during this audit
(§6, remediation 4). **It did not reconcile the seams**, because doing so unilaterally would assert
a position in a category this session did not author and has not assessed — the same reasoning
`BEA-21` applied to Categories 04–06.

### Why it is Medium and not Low

Seam 2 is a **contradiction, not an overlap**. `NFR-086c` forbids unmasked residency-classified data
in non-production environments; `MG-001-D-02` resolves it by classifying `migration-staging` as
production-class and excluding classified values entirely. **If `QA-004` resolves the same tension
by asserting blanket masking, one of the two documents is wrong and a cleansing pipeline is
operating on masked values** — which cannot work, because the cleansing is of the real values.

### Remediation instruction

1. **Read `QA-004` against `MG-001` §7.2 and record which position governs**, as a `GV-003` decision.
2. Reconcile `MG-005` `R2` with `QA-002`'s UAT level: one activity, one owner, one schedule entry.
3. When `QA-010` is written, adopt `DM-013` `E1`–`E9` by citation rather than defining a third space.

> **This is the seventh occurrence of two categories being authored in parallel by independent
> sessions** — after 00/01/02, 03, 04, 05, 06 and 07. `RG-08` remains unratified.

---

## `MGA-08` — Nine external verifications, none engaged, one with a three-month lead time

**Severity: HIGH · Status: OPEN · Owner: Chief Financial Officer**

### What was found

`MG-004` §8.1 enumerates every reconciliation control that must be verified by a party outside the
programme. **None of the nine is engaged or scheduled.**

| # | Verification | Verifier | State | Wave |
|:--:|---|---|---|:--:|
| 1 | Opening trial balance | **External auditor** | Not engaged | W3 |
| 2 | Bank balances and reconciling items | The bank's own statement | Not scheduled | W3 |
| 3 | Mushak 6.3 sequence and opening input VAT | **Tax consultant** | **Not engaged** | W3/W4 |
| 4 | Payroll tax slabs (`MD-043`), VAT rates (`MD-037`) | **Tax adviser**, `G6` gate evidence | **Not engaged** | W3/W5 |
| 5 | Consignment balances | 17+ brand partners, in writing | Not scheduled | W2 |
| 6 | Top-50 AR customer balances | The customers, in writing | Not scheduled | W3 |
| 7 | Leave balances | Each employee, agreed | Not scheduled | W5 |
| 8 | Fixed-asset tax-book WDV | Tax consultant | Not engaged | W5 |
| 9 | Physical counts | Witnessed and signed | Count programme unresourced | W2/W3/W5 |

Items 3, 4 and 8 depend on a tax adviser that `AUDIT-011` `DM-09` recorded as unengaged, with a
**three-month lead time**, against a **W3** load and a **W5** payroll.

### The one that will be discovered late

**Item 1 is not a standard audit engagement.** An external auditor asked at the wave gate to
countersign an ERP opening balance, with no prior engagement covering it, will decline — correctly.
`G3-08` is a **CFO signature countersigned by the auditor** and is **non-delegable**.

`MG-004` `RVP-27` addresses it by requiring the auditor's scope to be agreed **in writing, in
advance**, and `MG-004` §8.2 states what the auditor is and is not being asked. **That rule now
exists; the engagement does not.**

### Consequence

`G3-08` fails on a procedural point after all the technical work is complete, at a wave `GV-004`
§5.2 already measures at **1.00× capacity — zero float**.

### Remediation instruction

1. **Engage the tax adviser now**, not at W3. `AUDIT-011` `DM-09` recorded the same instruction on
   2026-08-18; this is its second issue.
2. **Extend the external auditor's engagement letter** to cover agreement of the migration opening
   trial balance, with the `MG-004` §8.2 scope attached.
3. Schedule items 5, 6 and 7 as business activities in `GV-004` with owners — they are the same
   class as the `AUDIT-011` `DM-05` physical-verification commitments and belong in the same plan.

---

## `MGA-09` — `DM-002` `SI-01` and `MG-002` `LPX-06` now disagree on the extract gate

**Severity: MEDIUM · Status: OPEN · Owner: Programme Content Lead with the Data Migration Lead**

### What was found

| Rule | Gate |
|---|---|
| `DM-002` `SI-01` | *"No extract may run against a source whose `profiling_status` is `not_started`"* |
| **`MG-002` `LPX-06`** | *"Extract requires `accepted`, not `reported`"* |

`DM-002`'s enum has five values: `not_started` / `in_progress` / `reported` / `accepted`. `SI-01`
blocks only the first. `LPX-06` blocks the first three.

**This is a deliberate tightening**, recorded as `MG-002-D-01` and taken under `MST-02` (this
category wins on technical mechanism). The reasoning is that BRD `MIG-002` requires profiling
*"reported to the data owner"*, and **a report nobody read is not a control** — the acceptance is
the point of the requirement.

### Why it is still a finding

**Two controlled documents state different gates for the same act.** Under `MST-02` the tightening
is legitimate; under `PG-M2` and `CM-R1` the *other* document must be updated to match, and it has
not been. A migration analyst reading `DM-002` will believe an extract may run at `reported`.

### Remediation instruction

Amend `DM-002` `SI-01` to read `accepted`, cite `MG-002` `LPX-06`, and record the change in `RF-006`.
`MG-002` `Q-05` carries it. **This audit does not make the change** — `DM-002` is a content file and
its amendment is the Programme Content Lead's act under `CM-R1`, not an auditor's.

---

## `MGA-10` — Two named control registers do not exist, and a third is newly required

**Severity: MEDIUM · Status: OPEN · Owner: Data Migration Lead**

### What was found

Three machine-readable registers are named by controlled documents as the place a control lives.
Searched across the whole workspace at 2026-08-19 09:40 (+06):

| Register | Named by | On disk |
|---|---|:--:|
| `DM-013_Reconciliation_Control_Register.csv` | `DM-013` `RV-05` — *"declared before its first load, and not changed after"* | **✘** |
| `DM-012_Load_Template_Register.csv` | `DM-012` §2.1 | **✘** |
| `MG-004_Reconciliation_Control_Register.csv` | **`MG-004` `RVP-07`** *(new at this issue)* | **✘** |

`project_content/12_Data_Migration_Content/` contains **zero `.csv` files**.

### Why it matters

`RV-05` and `RVP-04` both turn on the control total being **declared before the load and frozen**.
A control that lives in a register that does not exist is a control that will be reconstructed from
the result — which is the precise failure `RVP-04` and `DQ-05` exist to prevent, and it is
undetectable afterwards because the reconstructed total always reconciles.

### An honest note about this category's own contribution

**`MG-004` `RVP-07` names a third register that also does not exist.** That is a forward
requirement, not a false claim — `MG-004` states it as something that must be created, and §4.3
specifies its columns. It is recorded here so that Category 09 is not credited with closing a gap it
has restated in a new place.

### Remediation instruction

1. Create the two `DM` registers, or amend `DM-012`/`DM-013` to name the artefact that actually
   carries the control.
2. Create `MG-004_Reconciliation_Control_Register.csv` before the first W1 load, per `RVP-07`.
3. Consider consolidating: `DM-013`'s and `MG-004`'s registers describe the same controls at
   different altitudes and may be one file.

---

## `MGA-11` — `IV-14` voids a count outside its window; `RBK-27` preserves it across a fallback

**Severity: MEDIUM · Status: OPEN · Owner: Warehouse Manager with the Programme Content Lead**

### What was found

| Rule | Position |
|---|---|
| `DM-007` `IV-14` / `DM-014` `CV-08` | *"A count outside the window is void"* — count sheets carry the freeze instant printed |
| **`MG-007` `RBK-27`** | *"A completed physical count survives a fallback and is re-used at the re-attempt"* |

Both are defensible and they conflict at exactly one moment: **a W2 cutover that loads successfully,
reconciles, and then falls back on an unrelated trigger.**

### Why `RBK-27` was written

A count is **evidence of a physical position at an instant**. A data rollback does not move stock.
Re-counting 10,000 SKUs across 51 branches, recalling 200–400 vans a second time, and closing 51
sites again — because a load failed — is a cost the business would pay twice for no informational
gain. `AUDIT-011` `DM-05` already establishes the count as *"the single largest operational
commitment M15 asks of the business"*.

### Why `IV-14` is also right

A count's value decays with every movement after it. Preserving it without adjustment would carry a
stale opening position into the re-attempt, which is the contamination `M15` §16.4 refuses in the
first place.

### The reconciliation this audit proposes but does not impose

**A completed count is preserved, and adjusted forward by the movements recorded since it was
taken** — which, during a freeze and a fallback, are exactly the numbered paper records `CV-11`
requires. This makes `RBK-27` conditional on `MGA-12` being closed: **without the paper forms, there
is no movement record, and the count cannot be adjusted — so it must be redone.**

### Remediation instruction

Ruled by the Warehouse Manager with the Programme Content Lead, recorded in `GV-003`, and reflected
in whichever of `DM-007` `IV-14` or `MG-007` `RBK-27` yields. `MG-007` `Q-03` carries it.

---

## `MGA-12` — The `P2` paper contingency has no forms

**Severity: HIGH · Status: OPEN · Owner: Content Design with the Data Migration Lead**

### What was found

`DM-014` `O-06` records it. **This audit verified it rather than repeating it**, at 2026-08-19 09:15
(+06):

| Test | Result |
|---|---|
| `DT` templates for the **live** documents the freeze replaces | Present — `DT-002` service intake receipt, `DT-024` goods receipt note, `DT-029` physical count and stock adjustment sheet, and 26 others |
| A search across all `DT` files for *paper intake*, *manual voucher*, *emergency pad*, *contingency pad* | **Zero matches** |

`DM-014` `CV-11` requires, per function per site: a pre-numbered paper intake pad drawn from the
reserved sequence block (`SH-10`), paper job cards, paper visit forms, numbered manual issue
vouchers, paper GRN pads, manual receipts and an emergency invoice pad.

### Why this audit raises the severity above `DM-014`'s

`DM-014` lists it as one open item among eight. **`MG-007` §6 makes it recovery-critical.**

Between `P-BUS` (the first user transaction on the new system) and a signed reconciliation, the
paper record is the **only** means of reconstructing what the business did. `RBK-17` states it;
`RBK-25` requires the paper batch to be keyed into legacy **even when rolling back**, because *"the
company must still know what happened during the window"*.

And per `MGA-11`, the forms are also what makes a preserved physical count adjustable.

**A missing form is therefore three failures, not one:** an unrecordable freeze, an unreconstructable
fallback, and a voided count.

### Consequence

Every one of nine cutovers, at up to 51 sites, with no artefact for staff to write on. The
improvisation that follows produces records `DM-014` `CV-11` describes as *"keyed as a P2 catch-up
batch"* — from sources that were never designed to be keyed.

### Remediation instruction

1. Register the `P2` contingency form set as `DT` artefacts with an owner and a W1-minus-1-month
   date, drawn from the `SH-10` reserved sequence block.
2. Produce them **bilingually** — they are branch-facing, and `MGA-06` applies.
3. Include them in the `MG-005` `R3` rehearsal: a form nobody has filled in is a form that will be
   filled in wrongly.

---

## `MGA-13` — Three operational roles this category requires do not exist in the organisation

**Severity: MEDIUM · Status: OPEN · Owner: Programme Director**

### What was found

Method 7a applied to `MG-006` §3 and `MG-005` §5.2 identifies three roles that every cutover
depends on and that no organisational document defines:

| Role | Required by | Why it cannot be absorbed |
|---|---|---|
| **Zone Coordinator** (6–8 of them) | `CUT-18` | 51+ sites cannot report to one Branch Coordination Lead without breaching `CUT-04`'s span of control. This is a layer, not a task |
| **Migration Engineering Lead** | `MG-001` §5.1 stream `S2`; `MG-006` Deputy Cutover Manager | Named as *unappointed* in `MG-001` at issue. It is also the `MG-003` owner |
| **Observer / Scribe** | `DRH-07`, `CUT-13`, `CUT-29` | Must be **separate from the performer** for the whole window, at every rehearsal and every cutover. A Load Operator timing their own steps measures nothing |

`06-01` §Resourcing allocates **Data Owners at 20% through W1–W5** and names no cutover-specific
roles at all.

### Why it is Medium

None of the three is a specialist hire; all three are assignments. **The finding is that they are
assignments nobody has made**, and `CUT-02` blocks the freeze on every role being named in writing
at `C2` — so the first cutover will discover them three days before it runs.

### Remediation instruction

Name all three, with deputies, in `GV-004` resourcing, before the first `R1` rehearsal at T−45 days.
`MG-006` `Q-02` and `MG-005` `Q-02` carry them.

---

## `MGA-14` — Absence claims in `AUDIT-011` and `DM-014` have decayed; `CM` and `OP` now exist

**Severity: MEDIUM · Status: CLOSED · Owner: This audit**

### What was found

Four controlled documents assert that Categories 16 and 17 are empty:

| Assertion | Where |
|---|---|
| *"`CM-012` and `CM-013`… Category 16 `CM` held zero files at enumeration 2026-08-18"* | `DM-014` `O-04` |
| *"`OP-002` is unwritten (enumerated 2026-08-18; Category 17 held zero files)"* | `DM-014` `O-05` |
| *"Category 16 `CM` held zero files at enumeration 2026-08-18"* | `AUDIT-011` `DM-08` |
| *"`CM-012` Branch Readiness… **Unwritten**"*, *"`OP-002`… **Unwritten**"* | `DM-014` §5 dependencies |

Re-enumerated 2026-08-19 09:10 (+06):

| Category | Files on disk | Written |
|---|---:|---|
| 16 `CM` Change Management & Comms | **18** | 2026-08-20 |
| 17 `OP` Operations Support & Runbooks | **16** | 2026-08-20 |

**All four absence claims are false as of this audit.**

### Why it is closed rather than open

**Because Category 09 corrected itself.** Three passages in `MG-005` and `MG-006` had inherited the
decayed claims and asserted that `CM-012`/`CM-013` were unwritten. All were corrected during this
audit (§6, remediation 3), and the substantive finding was **re-derived from the current filesystem**
— producing `MGA-06`, which is a stronger and more actionable finding than the one it replaced.

`AUDIT-011` `DM-12` named this class itself: *"nine absence claims decayed within hours."* This is
its second recorded occurrence in the same category's lineage.

### Residual, referred onward

`DM-014` `O-04` and `O-05` and `AUDIT-011` `DM-08` **remain uncorrected in their own files.** Their
amendment is the Programme Content Lead's act under `CM-R1`. Referred, not performed.

---

## `MGA-15` — The estate moved during authoring, for at least the sixth recorded time

**Severity: MEDIUM · Status: OPEN · Owner: PMO**

### What was found

| Enumeration | `project_content` | `project-guide-doc` | Workspace total |
|---|---:|---:|---:|
| 2026-08-18 02:06 (per `PGD-000` §0.1) | 477 | — | 610 |
| 2026-08-18 19:48 (per `PGD-000` front matter) | — | 115 | 736 |
| 2026-08-18 21:55 (this session's start) | — | **119** | — |
| **2026-08-19 09:40 (this audit's close)** | **488** | **136** | **757** |

**`project_content` gained 11 files and `project-guide-doc` gained 17** — seven of which are this
category's, meaning **ten were written by other sessions** while this one ran: `QA-001`…`QA-007`,
`PGD-AUDIT-007`, `PGD-AUDIT-008`, `PGD-AUDIT-CAT-07`.

### Why it is reported again

`PGD-A1-03`, `AUDIT-016` `AP-17`, `PGD-AUDIT-002` §8, `PGD-A3-18`, `PGD-A5-18` and `PGD-000` §0.5
all record the same phenomenon. **Proposed rule `RG-08` (timestamped enumeration) has been pending
ratification throughout**, and `RR-002` (Identifier Convention Standard) has been recommended six
times (`MGA-04`).

Every figure in Category 09 carries a timestamp for this reason, and §7.3 records the commands so
any figure can be re-derived rather than trusted.

### Remediation instruction

**Ratify `RG-08` and write `RR-002`.** This is the sixth recommendation and it is deliberately
identical to the previous five; varying the wording would suggest the previous ones were the
problem.

---

## `MGA-16` — This session quoted four stale rule ranges in its own scope statements

**Severity: LOW · Status: CLOSED · Owner: This session**

### What was found

Each document's §1.2 scope table names its rule range. Four were written before the rule sets were
finished and were not regenerated:

| Document | Stated | Actual | Corrected to |
|---|---|---|---|
| `MG-002` | `LPX-01`…`LPX-30` | 43 rules | `LPX-01`…`LPX-43` |
| `MG-003` | `ETR-01`…`ETR-42` | 50 rules | `ETR-01`…`ETR-50` |
| `MG-005` | `DRH-01`…`DRH-30` | 31 rules | `DRH-01`…`DRH-31` |
| `MG-006` | `CUT-01`…`CUT-34` | 36 rules | `CUT-01`…`CUT-36` |

`MG-001`, `MG-004` and `MG-007` were correct.

### Why a Low finding is recorded rather than silently fixed

**Because it is a `PG-M10` breach in miniature** — a figure carried forward rather than regenerated
from its rows. The category contains 257 rules across seven documents; four scope statements were
wrong by 4 to 8 rules each. Nobody would have been misled, and the discipline is the point.

### How it was closed

All four corrected. Verified by regenerating the count from the rules tables:
**31 + 43 + 50 + 33 + 31 + 36 + 33 = 257.** Every rule referenced anywhere in a document was also
confirmed present in that document's rules table — **zero orphans across all seven.** Command in
§7.3.

### A second instance — in this audit's own findings ledger

**The same defect recurred one level up, in §9.3 of this document.** The severity ledger was written
while the finding list was still being drafted and was not regenerated before issue:

| Figure | Draft | Actual | Wrong by |
|---|---:|---:|---:|
| High | 6 | **5** | 1 |
| Medium | 8 | **9** | 1 |
| Closed | 6 | **5** | 1 |
| Open | 11 | **12** | 1 |

Critical (2), Low (1) and the total (17) were correct, which is what made it survive a read-through:
**the total reconciled, so the components were not checked.** `PGD-A2-24` states exactly this — *"a
correct total conceals wrong components"* — and it is why `PG-M10` requires regeneration rather than
verification.

Corrected by extracting severity and status from columns 3 and 4 of the §2 rows by script (§7.3),
and the front matter, §1 and §9.3 were all reissued from that extraction. **This finding's severity
is left at Low**, because no reader was misled about any individual finding; the escalation is that
it happened **in the audit that reports it**, which is recorded rather than smoothed over.

---

## `MGA-17` — This session mis-cited two section numbers in its own traceability table

**Severity: MEDIUM · Status: CLOSED · Owner: This session**

### What was found

`MG-001` §13 traces all fifteen BRD `MIG-nnn` requirements to a discharging document and section.
Two pointed at the wrong section:

| Requirement | Cited | Actually at | Corrected |
|---|---|---|---|
| `MIG-011` Bengali conversion and UTF-8 normalisation | `MG-003` §7.4 | §7.4 is *the date-ambiguity rule*; normalisation is `S-02`/`S-03` in **§7.3** | ✔ |
| `MIG-013` Financial history reconciled to the trial balance | `MG-004` §5.3 | §5.3 is *the parallel-run comparison*; the trial balance is **§4.2** and **§10.1** | ✔ |

### Why it is Medium and not Low

**This is the `F3` defect class** — a citation that resolves to a document but not to the content it
claims. `PGD-A5-17` recorded the same class against Category 03, and `DA-002` was written partly to
close it. A reader following `MIG-013` to `MG-004` §5.3 would have found a section about daily
comparison and concluded the trial-balance reconciliation was unspecified.

It is more serious here than a broken link, because **a broken link fails visibly and a mis-aimed
one does not.**

### How it was closed

Both corrected. A full sweep was then run over **every** inter-document section reference in the
category — 33 distinct `MG-00n §x.y` citations — confirming each resolves to an existing heading.
**Zero further mismatches.** Command in §7.3.

---

## 4. `AUDIT-011`'s Open Findings — Position After This Category

`AUDIT-011` issued 12 findings, 10 open. Category 09 was written against them. This is where they
now stand.

| Finding | Sev | Position after Category 09 |
|---|:--:|---|
| **`DM-01`** Migration has no technical specification | CRITICAL | **Closed at the specification layer.** All seven unspecified items are owned by an issued document (`_CATEGORY_OVERVIEW` §"The seven items"). **Item 7's tooling has no builder** — `MGA-01` |
| `DM-02` Two migration domains have no workbook | CRITICAL | **Open, unchanged.** `DM-015`/`DM-016` remain unregistered, verified 09:40. `MST-27` now **blocks** the affected datasets at lifecycle stage 3 rather than leaving them silent — the catalogue domain blocks part of W1 |
| `DM-03` All 48 sources unprofiled | HIGH | **Specified, unperformed.** `MG-002` supplies the method, the sequence and the acceptance; profiling remains an execution act with no funding (`MG-002` `Q-02`) |
| `DM-04` Match thresholds unset, queue unsized | HIGH | **Specified, unperformed.** `LPX-07` makes the candidate **count** a mandatory profiling output; `RVP-29` forbids setting a threshold before its queue is priced |
| `DM-05` The physical-count programme is in no plan | HIGH | **Open.** `MST-11` and `MST-26` require every `C` dataset in `GV-004` with a duration and a resource; `MG-006` §7 sequences it. **Resourcing remains `GV-007`'s act** |
| `DM-06` The wave column has two definitions | MEDIUM | Untouched — a content-register matter |
| `DM-07` The `M64` quality gate arrives a wave late | MEDIUM | **Open.** `MG-003` §9 executes `DQ-26`'s interim gate; it still has no build owner |
| `DM-08` English-only category, Bengali-first audience | MEDIUM | **Superseded by `MGA-06`.** Its premise (Category 16 empty) has decayed; the defect has moved to 16 missing translations |
| `DM-09` Two statutory verification gates unperformed | MEDIUM | **Open and restated as `MGA-08`**, now with the auditor engagement added |
| `DM-10` Transparency notice one wave late | MEDIUM | **Open and escalated as `MGA-02`** — the notice timing is a symptom; the missing basis is the finding |
| `DM-11` Third `DM` identifier space | LOW | Fixed by `AUDIT-011` |
| `DM-12` A summary figure written ahead of its derivation; nine absence claims decayed | MEDIUM | **Recurred — `MGA-14`, `MGA-16`.** Both caught and closed within this category |

---

## 5. Checks That Passed

Recorded because a finding list without them misrepresents the state of the work.

### 5.1 Structural

| # | Check | Result |
|:--:|---|---|
| 1 | Seven documents exist at the paths `PGD-000` names | ✔ |
| 2 | Front matter complete against `TPL_Guiding_Document.md` — `id`, `title`, `category`, `code`, `owner`, `approver`, `standards_basis`, `traces_to`, `depends_on`, `verified_on`, `priority`, `needed_by`, `register` | ✔ 7 of 7 |
| 3 | `enumeration_timestamp` present on all seven — not required by the template, added under `RG-08`'s proposed rule | ✔ |
| 4 | Every relative link resolves | ✔ **19 distinct targets, 0 broken** |
| 5 | Every inter-document section reference resolves to an existing heading | ✔ **33 references, 0 broken** *(after `MGA-17`)* |
| 6 | Every rule referenced in prose appears in its document's rules table | ✔ **257 rules, 0 orphans** |
| 7 | Rule identifiers contiguous from `01`, no gaps, no duplicates | ✔ 7 of 7 |
| 8 | No document allocates into a foreign rule space | ✔ |

### 5.2 Arithmetic

| # | Check | Result |
|:--:|---|---|
| 1 | Rule count regenerated from the tables: 31+43+50+33+31+36+33 | **257** ✔ |
| 2 | Category size regenerated from the filesystem | **357 KB** ✔ |
| 3 | Source-class distribution restated from `DM-002` §2.1: 4+14+5+2+12+3+4+4 | **48** ✔ |
| 4 | "36 of 48 not machine-profilable" — 14 `SS` counted as partly profilable, so 48 − 4 `DB` − 4 `PUB` − 4 `CFG` = **36** ✔ |
| 5 | `MG-004` §7.2 sample sizes recomputed as `−ln(1−c)/r` | ✔ 30/59/149/299 at 95% |
| 6 | BRD requirement trace: 15 requirements = 11 discharged + 2 partial + 1 build-blocked + 1 legally blocked | **15** ✔ |

### 5.3 Cross-document

| # | Check | Result |
|:--:|---|---|
| 1 | No Category 12 rule restated in a Category 09 document (`MST-01`) | ✔ Adopted by citation throughout |
| 2 | `DM-014` `T1`–`T7`, `C1`–`C9`, `P0`–`P4` used with `DM-014`'s meanings | ✔ |
| 3 | `DM-003` `X0`–`X9` tiers used with `DM-003`'s meanings | ✔ |
| 4 | `DM-013` `R1`–`R5`, `E1`–`E9` used with `DM-013`'s meanings | ✔ |
| 5 | `MG-001`'s tolerance hierarchy consistent with `DM-013` `RV-08` | ✔ |
| 6 | Residency position consistent with `AR-001` `LB-08`, `DA-001` `RS-03`, `SC-007` §7 | ✔ — no `MG` document proposes a path around `CD-233` |
| 7 | No unmeasured duration or throughput figure published anywhere | ✔ — `ETR-49`, `DRH-13`, `MG-006` §5.1 |
| 8 | No migration-execution effort figure published | ✔ — `MST-28`, `LPX-34`, `MG-001-D-05` |

> **Check 7 deserves comment.** `MG-006` §5.2 ships a 34-step worked W1 runsheet in which **every
> duration is `[R3]`**. A reviewer may read that as incomplete. It is the opposite: `CV-13` states
> that *"a runsheet whose durations are estimates has not been rehearsed"*, and a runsheet with
> plausible invented numbers is the artefact that causes a cutover to discover at 04:00 that its
> window closed at 02:00. **The structure is specified; the numbers are `MG-005`'s to supply.**

### 5.4 Operational executability (method 7)

| # | Rule class | Executable today? |
|:--:|---|---|
| 1 | Rules requiring an **artefact** — count sheets, extract manifests, evidence packs | Mostly ✔; **`P2` contingency forms ✘** (`MGA-12`) |
| 2 | Rules requiring a **role** — Cutover Manager, Reviewer, Approver, Scribe, Zone Coordinator | ✔ except three (`MGA-13`) |
| 3 | Rules requiring an **environment** — `migration-staging`, rehearsal, snapshot | **✘ — `PE-002` and `PE-007` absent** |
| 4 | Rules requiring a **language** — Bengali branch instruction | **✘** (`MGA-06`) |
| 5 | Rules requiring an **external party** — auditor, tax consultant, brands, customers | **✘** (`MGA-08`) |
| 6 | Rules requiring a **build component** — the pipeline, `CD-233` | **✘** (`MGA-01`) |
| 7 | Rules requiring a **decision** — lawful basis, W3 invoicing hold, W5 tax-year alignment | **✘** (`MGA-02`; `MG-007` `Q-02`; `MG-001` `Q-01`) |

**Four of seven classes are not executable today.** The specification is complete; the operation is
not, and §8 states the shortest path.

---

## 6. Remediation Applied During This Audit

| # | Correction | Documents | Finding |
|:--:|---|---|:--:|
| 1 | Four stale rule ranges corrected in scope statements | `MG-002`, `MG-003`, `MG-005`, `MG-006` | `MGA-16` |
| 2 | Two mis-cited section numbers corrected in the BRD trace | `MG-001` §13 | `MGA-17` |
| 3 | Decayed absence claims about `CM-012`/`CM-013` replaced with the current, stronger finding | `MG-005` `Q-04`; `MG-006` §1.2, §7.3, `Q-03`, §17 | `MGA-14` → `MGA-06` |
| 4 | Stale ⛔ claims about `QA-001`, `QA-002`, `QA-004` corrected; `MG-005` `depends_on` updated | `MG-001` §17; `MG-005` front matter, §1.2 | `MGA-07` |
| 5 | `OP-014`'s characterisation replaced with a counted one (0 occurrences of *migration*/*cutover*); its path corrected to the full filename | `MG-007` §8.1, §16 | `MGA-14` |
| 6 | `DM-014` `O-06` verified rather than repeated, with the `DT` search recorded | `MG-006` §11.2 | `MGA-12` |
| 7 | `SV-005`/`AUDIT-017` note made precise — content exists, capability does not | `MG-006` §12.3 | — |
| 8 | `_CATEGORY_OVERVIEW` reissued at v2.0 with the audited position | `_CATEGORY_OVERVIEW` | — |
| 9 | **`PGD-000` §3 Register Control corrected** — it read *"Version **1.2**"* and *"Documents authored **54**"* while the front matter read `1.3` and §0.5 read **81**. The register's own control block disagreed with the register by **27 documents and two versions**; the audit list was four entries short and the enumeration timestamp two moves stale | `PGD-000` §3 | — |
| 10 | `PGD-000` §2.1 row 18 and §2.2 tranche T7 updated; a note added recording that **T7's weeks 16–26 schedules migration after `SRC-001`/`SRC-002` expire at W2** | `PGD-000` §2.1, §2.2 | `R-01` |

> **No content file was amended.** `DM-002` `SI-01` (`MGA-09`), `DM-007` `IV-14` (`MGA-11`),
> `DM-014` `O-04`/`O-05` and `AUDIT-011` `DM-08` (`MGA-14`) all need changes that are the Programme
> Content Lead's act under `CM-R1`, not an auditor's. Each is referred with its instruction.

---

## 7. Verification Record

### 7.1 Filesystem and extraction claims

| Claim | Method | Result | Instant (+06) |
|---|---|---|---|
| 7 `MG` documents, 357 KB | `wc -c` | ✔ | 2026-08-19 09:40 |
| 257 rules across 7 prefixes | Table extraction + count | ✔ | 09:40 |
| 19 relative link targets, 0 broken | Path existence test | ✔ | 09:40 |
| 33 inter-document section references, 0 broken | Heading existence test | ✔ | 09:40 |
| 0 rule orphans (referenced but not tabled) | Set difference | ✔ | 09:40 |
| 7 rule prefixes each unused before allocation | Workspace-wide grep | ✔ | 2026-08-18 22:10 |
| `BE-005`: 0 of 331 items mention migration/ETL/cutover | Case-insensitive grep | ✔ | 09:40 |
| TSS Block 3: 0 of 16 are migration tooling | Line-by-line read of `CD-233`…`CD-248` | ✔ | 2026-08-18 22:10 |
| 48 sources, `profiling_status = not_started` on all | `DM-002` §2.2 read | ✔ | 2026-08-18 22:20 |
| 16 declared `BN` counterparts absent | Front-matter extraction + path test | ✔ | 09:10 |
| Category 16 = 18 files; Category 17 = 16 files | Directory listing | ✔ | 09:10 |
| Category 08 = 7 `QA` documents | Directory listing | ✔ | 09:30 |
| `06-03_Data_Migration_Strategy.md` absent | Workspace-wide `find` | ✔ absent | 09:40 |
| `DM-015`/`DM-016` unregistered | Directory listing | ✔ absent | 09:40 |
| 0 `.csv` files in `12_Data_Migration_Content` | Directory listing | ✔ | 09:40 |
| 0 `DT` matches for contingency-pad terms | Recursive grep | ✔ | 09:15 |
| `OP-014`: 0 occurrences of *migration* or *cutover* | Case-insensitive grep | ✔ | 09:20 |
| Workspace 757 files; `project_content` 488; PGD 136 | `find -type f` | ✔ | 09:40 |

### 7.2 Internal consistency

| Claim | Method | Result |
|---|---|---|
| No Category 12 rule restated | Prefix scan for `MS-`, `SI-`, `SQ-`, `DQ-`, `LT-`, `RV-`, `CV-` used as *definitions* | ✔ all citations, no definitions |
| Rule identifiers contiguous, no duplicates | `unique count == max` per prefix | ✔ 7 of 7 |
| No unmeasured duration published | Manual read of `MG-005` §5, `MG-006` §5, `MG-007` §7.5 | ✔ all `[R3]` or "measured at" |
| Sample sizes reproducible | Recomputed `−ln(1−c)/r` | ✔ |

### 7.3 Verification commands

Recorded so any figure above can be re-derived rather than trusted (`PG-03`, `RG-08` proposed).

```bash
# Rule counts, contiguity and orphans, per document
for p in MST:MG-001 LPX:MG-002 ETR:MG-003 RVP:MG-004 DRH:MG-005 CUT:MG-006 RBK:MG-007; do
  pre=${p%%:*}; doc=${p##*:}; f=$(ls ${doc}_*.md)
  grep -o "^| \`$pre-[0-9][0-9]\`" "$f" | grep -o "$pre-[0-9][0-9]" | sort -u > tbl
  grep -o "$pre-[0-9][0-9]" "$f" | sort -u > all
  echo "$pre tabled=$(wc -l < tbl) referenced=$(wc -l < all) orphans=$(comm -13 tbl all | wc -l)"
done

# Prefix freedom, before allocation
for p in MST LPX ETR RVP DRH CUT RBK; do
  echo "$p: $(grep -ro "$p-[0-9][0-9]" --include='*.md' . | wc -l)"; done

# Relative link resolution
grep -oh "](\.\./[^)]*\|](MG-[^)]*" MG-00*.md | sed 's/^](//' | sort -u |
  while read -r p; do [ -e "$p" ] || echo "BROKEN $p"; done

# Inter-document section references
grep -oh "MG-00[1-7]\`\**  *§[0-9][0-9.]*" MG-00*.md | ...   # full form in the audit working set

# BE-005 migration components
grep -o -i "migrat[a-z]*\|\betl\b\|cutover" ../07_*/BE-005_*.md | wc -l    # -> 1 (a warehouse ETL mention)

# Declared Bengali counterparts against the filesystem
for d in 16_Change_Management_and_Comms 17_Operations_Support_and_Runbooks; do
  for f in $d/*.md; do
    bn=$(awk '/^---$/{n++;next} n==1' "$f" | grep "^bn_counterpart:" | sed 's/bn_counterpart: *//')
    [ -n "$bn" ] && [ "$bn" != "n/a" ] && [ ! -e "$d/$bn" ] && [ ! -e "11_Localisation_Bengali/$bn" ] && echo "$bn"
  done; done | wc -l                                                        # -> 16

# Estate enumeration
find . -type f | wc -l ; find project_content -type f | wc -l ; find project-guide-doc -type f | wc -l

# Findings ledger — regenerated from the §2 rows, never carried (PG-M10, MGA-16)
grep '^| .MGA-' PGD-AUDIT-CAT-09_*.md |
  awk -F'|' '{gsub(/[ *`]/,"",$4); gsub(/[ *`]/,"",$5); print $4" "$5}' | sort | uniq -c
#   2 CRITICAL OPEN | 1 HIGH CLOSEDbydesign | 4 HIGH OPEN
#   3 MEDIUM CLOSED | 6 MEDIUM OPEN        | 1 LOW CLOSED      -> 17 total, 5 closed, 12 open
```

---

## 8. Recommendations

Ordered by the date at which not doing them starts destroying work.

| # | Recommendation | Owner | By |
|:--:|---|---|:--:|
| **R-01** | **Obtain hosting-vendor access and extract `SRC-001` and `SRC-002`.** Both are withdrawn at W2 and their data is then permanently unrecoverable. **The only irreversible deadline in the migration programme** | CTO | **Immediately** |
| **R-02** | **Determine and record the lawful basis for migration processing** in `GV-003`. `MST-21` blocks every personal-data load until it exists | Legal Counsel with the DPO | **W0** |
| **R-03** | **Allocate and size `CD-SVC-nn` for the migration tooling**, wave W0. `MIG-008` is P0 and contractual | Chief Architect with `GV-007` | **W0** |
| **R-04** | **Fund the profiling programme.** It unblocks the estimate, the thresholds, the seven workbooks and the window arithmetic. `GV-007` excludes migration execution *because* profiling has not run | Programme Director | **W0** |
| **R-05** | **Engage the tax adviser and extend the auditor's engagement.** Three-month lead time against a W3 load; second issue of this instruction | CFO | **W0** |
| **R-06** | **Commission `PE-002` and `PE-007`.** `migration-staging`, the rehearsal environment and snapshot/restore have no owning design, and four rule classes depend on them | CTO | **W1 − 3 months** |
| **R-07** | **Build the physical-verification programme** spanning W1–W8, resourced separately from the migration team, with training and a rehearsal count. `AUDIT-011` `DM-05`, second issue | Programme Director | **W0** |
| **R-08** | **Translate `CM-012`, `CM-013` and `OP-014`**, re-register the first two as `P0`, and add a bilingual-counterpart existence check to the content gate | Localisation Lead | **W1 − 2 months** |
| **R-09** | **Register `DM-015` (catalogue and pricing) and `DM-016` (documents).** Catalogue is a **W1** load with no mapping specification, blocked by `MST-27` | Programme Content Lead | **W1 − 3 months** |
| **R-10** | **Adopt `origin = migration` into `AR-009` §5** with an ADR and a fitness function | Solution Architect | **W1 − 2 months** |
| **R-11** | **Produce the `P2` contingency form set**, bilingually, from the `SH-10` reserved block, and rehearse it | Content Design | **W1 − 1 month** |
| **R-12** | **Name the Zone Coordinators, the Migration Engineering Lead and the Scribe**, with deputies | Programme Director | **W1 − 2 months** |
| **R-13** | **Ratify `RG-08` and write `RR-002`.** Sixth issue, deliberately unchanged | Programme Content Lead | **W0** |
| **R-14** | **Reconcile the three Category 08 seams** — UAT, test-data masking, defect taxonomy — as `GV-003` decisions | QA Lead with the Data Migration Lead | **W1** |

> **R-01 through R-05 are all `W0` or immediate, and four of the five are decisions or engagements
> rather than work.** The migration programme's critical path currently runs through things nobody
> has to build.

---

## 9. Closure

### 9.1 Status assigned

Category 09 moves from **0 ✅ / 3 ◐ / 1 ⬜ / 3 ⛔** to **7 ✅**, against `PGD-000` §0.3's four tests:

| Test | Met? | Evidence |
|---|:--:|---|
| (a) A named file exists at a stated path | ✔ | §7.1; seven files |
| (b) Complete front matter per `RR-003` | ✔ | §5.1 check 2 |
| (c) ≥ 90% of the section set its governing standard requires | ✔ | §2.1 of each document maps clause to section; departures stated |
| (d) A named owner **and an approval record** | **Owner ✔ · approval record ✘** | `PGD-A1-09` — no constituted body can approve anything until `GV-001` `CC-01` |

**The ✅ is therefore qualified**, exactly as Categories 00–07 are, and for the same reason
(`PGD-A2-25`). It is not qualified for any reason specific to this category.

### 9.2 What a reader should not conclude

> **A complete specification is not a performed migration.** Every one of the seven documents is
> issued; **not one source has been profiled, not one pipeline exists, not one rehearsal has run, and
> not one rollback has been timed.** Method 7 found four of seven rule classes inexecutable today.
>
> The honest summary is the one in `_CATEGORY_OVERVIEW` §"What done looks like": **three of six
> completion criteria are specification-complete and execution-blocked.** Reading ✅ as progress
> toward a migration would repeat, at category scale, the misreading `PGD-000` §0.3 warns about for ◐.

### 9.3 Findings ledger

| Severity | Total | Closed | Open |
|---|---:|---:|---:|
| Critical | 2 | 0 | **2** |
| High | 5 | 1 | **4** |
| Medium | 9 | 3 | **6** |
| Low | 1 | 1 | 0 |
| **Total** | **17** | **5** | **12** |

**Check:** 2 + 5 + 9 + 1 = 17 ✔ · 5 closed + 12 open = 17 ✔

**Method:** extracted from columns 3 and 4 of the seventeen §2 rows by script, not counted by eye
and not carried from the drafting notes. The command is in §7.3. **The previous draft of this table
read 2 / 6 / 8 / 1 with six closed** — wrong in three of five figures, and wrong in the direction
that flattered the result. See `MGA-16`.

---

## 10. Audit Control

| Item | Value |
|---|---|
| Audit id | `PGD-AUDIT-CAT-09` — **category-keyed**, per `PGD-AUDIT-CAT-07`'s precedent |
| Why not sequential | `PGD-AUDIT-007` and `PGD-AUDIT-008` were both claimed during this session (`MGA-05`, `MGA-15`). Sequential allocation under concurrent authoring is the mechanism behind six collisions (`PGD-A7-01`) |
| Scope | 7 documents, 357 KB, 257 rules, plus `_CATEGORY_OVERVIEW` v2.0 |
| Methods | 7 — the six of `PGD-AUDIT-005` plus operational executability |
| Findings against this session's own work | **2** — `MGA-16`, `MGA-17`; both closed |
| Enumeration window | 2026-08-18 21:55 → 2026-08-19 09:40 (+06) |
| Estate at close | **757** files workspace-wide · 621 source estate · **136** this repository |
| Next review | On completion of the first `MG-005` `R1` rehearsal, or on any of `R-01`…`R-05` closing |
| Referred onward | `DM-002` `SI-01` · `DM-007` `IV-14` · `DM-014` `O-04`/`O-05`/`O-06` · `AUDIT-011` `DM-08` · `AR-009` §5 · `BE-005` §5.1 · `GV-003` · `GV-005` · `GV-007` |

---

*`PGD-AUDIT-CAT-09` · Category 09 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
