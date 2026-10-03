---
id: MG-007
title: Rollback and Fallback Plan
category: 09 — Data Migration & Cutover
code: MG
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Data Migration Lead with the CTO
approver: Chief Technology Officer with the Chief Financial Officer
standards_basis: >
  BRD MIG-007 (documented, rehearsed rollback plan for every cutover) · 05-06 OPS-07 (reversible by
  a documented procedure) · ISO/IEC 20000-1:2018 §8.5.1 (change control — documented back-out) ·
  ISO 22301:2019 §8.4 (business continuity procedures) applied to the fallback period ·
  DM-003 SQ-08 (exact reverse tier order) · DM-014 T1…T7, CV-15…CV-18
traces_to: >
  PGD-000 MG-007 · AUDIT-011 DM-01 (rollback mechanics unspecified; T4 unevaluable) ·
  DM-001 MS-06, MS-23 · DM-003 §4.6, SQ-08 · DM-014 §4.7, CV-16, CV-17, CV-18 ·
  OP-014 (manual fallback procedures) · M51 §16.4 · M56 §16.4
depends_on: MG-001 · MG-003 · MG-004 · MG-005 · MG-006 · PE-007 (absent) · SV-006 (absent)
verified_on: 2026-08-18
priority: P0
needed_by: W2
enumeration_timestamp: 2026-08-18 23:20 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# MG-007 — Rollback and Fallback Plan

### Category 09 · Code `MG` · BRD `MIG-007` · `05-06` `OPS-07` · ISO/IEC 20000-1:2018 §8.5.1 · ISO 22301:2019 §8.4

---

> **Local rule prefix: `RBK-nn`.** Verified unused workspace-wide at 2026-08-18 23:20 (+06).

---

## 1. Purpose

**Five documents require a rollback. None of them says how to perform one.**

| Source | Requirement |
|---|---|
| BRD `MIG-007` | A documented, **rehearsed** rollback plan for every cutover |
| `05-06` `OPS-07` | Migrations *"reversible by a documented procedure"* |
| `05-02` `MIG-03` | *"Every load is reversible"* |
| `DM-003` `SQ-08` | Rollback in **exact reverse tier order**, with a rehearsed and published duration |
| `DM-014` `T4` | Fallback fires when the remaining window is shorter than **the measured rollback duration** |

`AUDIT-011` `DM-01` names the gap as the sharpest instance of the missing strategy: *"a rule that
cannot be evaluated, because nothing specifies how a rollback is performed, and no rollback has been
rehearsed."*

`DM-001` `MS-23` states the standard this document must meet: ***"reversible" means a rehearsed
procedure with a measured duration, not the existence of a backup.***

### 1.1 The register's other point

`PGD-000` marks `MG-007` ◐ against `OP-014`, and states why that is not enough:

> *"`OP-014` provides manual fallback procedures for operations. **A migration rollback is a
> different artefact** and does not exist."*

Correct, and the distinction runs deeper than the register has room for. `OP-014` answers *"the
system is down, how do we keep trading?"* — a continuity question. **This document answers two
questions `OP-014` does not ask:** how do we undo a migration that has already written to
production, and what does the business do for the days afterwards while the legacy estate is
running again and the new system is not.

### 1.2 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The four terms that are routinely conflated, defined and separated (§3) |
| 2 | **Four rollback mechanisms** and which applies to which tier (§4) |
| 3 | **The point of no return — technical, business and statutory** (§5) |
| 4 | **The data-loss position at every stage** (§6) |
| 5 | The rollback procedure itself, step by step (§7) |
| 6 | **The fallback operating model** — what the business does while rolled back (§8) |
| 7 | Re-attempt policy and the root-cause gate (§9) |
| 8 | The interface to major-incident management (§10) |
| 9 | Rules `RBK-01`…`RBK-33` (§11) |

**Explicitly out of scope**

| Topic | Owned by |
|---|---|
| Fallback **triggers** `T1`–`T7` and rules `CV-15`–`CV-18` | **`DM-014`** — adopted whole |
| **Measuring** the rollback duration | **`MG-005`** §8 |
| The runsheet's `rollback_step` column and cutover command | **`MG-006`** |
| Operational manual procedures for an unplanned outage | `OP-014` — §8.1 states the seam |
| Backup, restore and DR infrastructure design | `PE-007` ⛔ |
| Major-incident command for unplanned events | `SV-006` ⛔ |
| Application (code) rollback | `PE-004` ⛔, `RL-002` ⛔ |
| Legacy decommissioning | `RL-006` ⛔ — a rollback assumes legacy is still there; §8.2 |

---

## 2. Basis

### 2.1 Standards conformance

| Standard | Clause | Conformance | Departure |
|---|---|---|---|
| **ISO/IEC 20000-1:2018** | §8.5.1 — change control requires a documented back-out | §7 is the back-out procedure; §9 the re-attempt control | ISO 20000 assumes a change small enough to reverse. §5 records where that assumption fails |
| **ISO 22301:2019** | §8.4 — business continuity procedures | §8 is the fallback operating model for the days after a rollback | 22301 addresses disruption. **A rollback is a *planned* reversion**, so §8 is a continuity procedure with a known start time and a shorter warning than any incident |
| **BRD `MIG-007`** | Documented, rehearsed rollback plan | This document + `MG-005` §8 | — |
| `05-06` `OPS-07` | Reversible by a documented procedure | §4, §7 | — |
| `DM-003` `SQ-08` | Exact reverse tier order, rehearsed, published duration | §7.2, §4.2 | — |
| `DM-014` `T1`–`T7`, `CV-15`–`CV-18` | Trigger set; paper catch-up; post-mortem; re-attempt gate | Adopted unchanged (`MST-01`) | — |

### 2.2 The design problem, stated honestly

**A migration cannot always be undone, and a plan that pretends otherwise is more dangerous than one
that admits it.**

Three facts make full reversal impossible after a certain point:

| # | Fact | Consequence |
|:--:|---|---|
| 1 | **Users transact on the new system from the go decision** (`CV-19` primacy) | Deleting migrated records deletes the parents of records real people created |
| 2 | **Statutory sequences advance** — a Mushak 6.3 number issued cannot be unissued (`M51`: *"cannot be corrected afterwards"*) | Reversal does not restore the statutory position |
| 3 | **Money moves** — a payroll paid cannot be unpaid (`M56`, `G5-01`) | Reversal is an accounting event, not a data operation |

> **`RBK-01` — this document therefore specifies *four* mechanisms, not one, and states plainly
> where reversal stops being available.** §5's point-of-no-return analysis is the most important
> section here, and it is the one the estate has never had.

---

## 3. Four Terms, Separated

`DM-014` uses "rollback" and "fallback" and means different things by them. `OP-014` uses "fallback"
for a third thing. **`RBK-02`: these four terms are used as defined below, everywhere in this
category.**

| Term | Definition | Duration | Owner |
|---|---|---|---|
| **Rollback** | **Undoing the data change.** Returning the target to its pre-load state, or as close as the mechanism permits | Minutes to hours — **measured** (`MG-005` §8) | Data Migration Lead |
| **Fallback** | **What the business does afterwards.** Operating on the legacy estate (or on paper) while the new system is not in use | Hours to weeks | Business Readiness Lead |
| **Recovery** | Restoring service after an **unplanned** failure — a database corruption, a hardware loss | Per `PE-007` RPO/RTO | Technical Standby / `SV-006` |
| **Re-attempt** | Running the cutover again, after the root cause is closed (`CV-18`) | A new cutover | Cutover Manager |

> **`RBK-03` — a plan with a rollback and no fallback leaves 51 branches with a clean database and
> no instructions.** This is the most common shape of an incomplete rollback plan, and it is why §8
> exists at the same weight as §7.

---

## 4. The Four Rollback Mechanisms

### 4.1 The mechanisms

| # | Mechanism | What it does | Available | Cost | Data loss |
|:--:|---|---|---|---|---|
| **`M1`** | **Staging discard** | Drop the staging schema. The target was never written | **Before the first target write** (`MG-006` W1 step 15) | Minutes | **None** |
| **`M2`** | **Tier reversal** | Delete migrated records **by `migration_batch_id`**, in exact reverse tier order (`SQ-08`) | After target writes, **before business transactions reference them** | Measured per tier | None, if complete |
| **`M3`** | **Full restore** | Restore the target database from the **pre-load snapshot** | While the snapshot remains valid — i.e. before any post-snapshot business transaction must be kept | Measured; the longest | **Everything after the snapshot** |
| **`M4`** | **Compensating correction** | No reversal. Correct forward: reverse journals, corrective entries, data remediation, an amended filing | **After the PONR**, when `M1`–`M3` are unavailable | Days to weeks | None — but the error is now part of the record |

### 4.2 Why `M2` needs the lineage columns

**`RBK-04`: `M2` is possible only because every migrated record carries `migration_batch_id`**
(`MS-18`, `MG-003` `ETR-30`). Without it, "delete what the migration created" is not a computable
set, and `M3` becomes the only mechanism — which converts every rollback into a full restore and
every restore into the loss of every transaction since the snapshot.

| # | Rule |
|---|---|
| `RBK-05` | `M2` deletes in **exact reverse tier order**: `X9`→`X8`→`X7`→`X6`→`X5`→`X4`→`X3`→`X2`→`X1`→`X0` (`SQ-08`) |
| `RBK-06` | `M2` deletes **only** records whose `migration_batch_id` matches the batch being reversed. A record created by a user is never in scope, and if one references a record being deleted, **`M2` has failed and `M3` is required** (§5.2) |
| `RBK-07` | `M2` **also removes the `__migration__` external identifiers** it created (`ETR-13`), or a re-run will update ghosts instead of creating records |
| `RBK-08` | `M2` reverses the **residency second pass first** — `CD-233` entries are deleted through `CD-233`, never by touching the resident store (`LB-08`). This is the only rollback step that leaves the deletion of a value to another component |
| `RBK-09` | `M2` completeness is **verified, not assumed**: after reversal, a count by `migration_batch_id` returns zero, and `ctl_xref` records the reversal per record |

### 4.3 Which mechanism per tier

| Tier | Primary | Fallback mechanism | Note |
|:--:|:--:|:--:|---|
| `X0` control | `M2` | `M3` | Control tables; trivially reversible |
| `X1` party | `M2` | `M3` | **Every later tier references it** — reversing `X1` alone is never valid |
| `X2` party dependants | `M2` | `M3` | Includes the `CD-233` pass (`RBK-08`) |
| `X3` asset | `M2` | `M3` | |
| `X4` commercial | `M2` | `M3` | Entitlement grants are movements; reversal must reverse the movement, not the balance |
| `X5` service | `M2` | `M3` | **Highest risk of user reference** — open orders are worked on immediately |
| `X6` inventory | `M2` | `M3` | Counted positions; a stock movement after load makes `M2` unsafe |
| **`X7` finance** | **`M3` or `M4`** | — | **`M2` is not used for finance.** Deleting posted GL entries is not an accounting operation; see §4.4 |
| **`X8` people** | **`M3` or `M4`** | — | YTD balances are `never_reload` (`SQ-06`); a partial reversal is worse than none |
| `X9` archive | `M2` | — | **Off the critical path** (`SQ-03`); its failure never triggers fallback |

### 4.4 Why finance and payroll are different

**`RBK-10`: posted financial entries are never deleted. They are reversed by a compensating entry
(`M4`) or the whole database is restored (`M3`).**

| Reason | Detail |
|---|---|
| Audit trail | An accounting system that permits deletion of posted entries fails every audit expectation and `SC-010`'s forensic-readiness requirements |
| Statutory sequences | Document sequences (invoice, Mushak) advance and must not gap or reset (`FO-12`, `M51`) |
| The trial balance | `G3-08` reconciles to an **auditor-agreed** opening TB; a deleted-and-reloaded TB is a different TB with the same figures and no provenance |
| Payroll | A paid payroll is money that left a bank account. `M56` and `G5-01` make this exact per employee |

> **The practical consequence:** the finance and payroll waves (W3, W4, W5) rely on `M3` full restore
> **within a tight window**, and on `M4` after it. §5.4 is therefore the statutory point-of-no-return
> analysis, and it is the shortest window in the programme.

---

## 5. The Point of No Return

### 5.1 There are three, not one

**The single most common error in cutover planning is treating the first target write as the point
of no return.** It is not. There are three PONRs, they arrive at different times, they have
different owners, and each closes a different mechanism.

| PONR | Reached when | Closes | Owner |
|:--:|---|---|---|
| **`P-TECH`** | The first record is written to the target | `M1` (staging discard) | Cutover Manager |
| **`P-BUS`** | **The first business transaction is created on the new system** by a real user | `M2` and, shortly after, `M3` | Business Readiness Lead |
| **`P-STAT`** | **A statutory artefact is issued** — a Mushak 6.3 number, a filed return, a paid payroll | `M2`, `M3` and any clean reversal. **Only `M4` remains** | CFO |

### 5.2 `P-BUS` — the one that actually binds

`DM-014` `CV-19` declares primacy: **the new system is the system of record from the go decision.**
Users transact on it immediately. From the first user-created record:

| Effect | Consequence |
|---|---|
| A user-created service order references a migrated party and a migrated device | `M2` on `X1`/`X3` would orphan or delete the parent of real work — **`RBK-06` makes this an `M2` failure, not a warning** |
| `M3` full restore would delete the user's work | The restore point predates it |
| **Therefore, after `P-BUS`, a rollback destroys real business activity** | The decision is no longer technical |

> **`RBK-11` — after `P-BUS`, a rollback decision requires the Go/No-Go Authority *and* the affected
> domain owner**, because it is a decision to discard work people have done. `MG-006` `CUT-31`'s
> `C7` authority is not sufficient on its own after this point.

> **`RBK-12` — the interval between `P-TECH` and `P-BUS` is the real rollback window, and it is
> under the programme's control.** Holding the release to users until reconciliation is signed
> (`MG-006` step 30 after step 29) is what keeps `M2` available through the whole load. **Releasing
> users early to "get a head start" closes the rollback window and is prohibited.**

### 5.3 `P-STAT` — per wave

| Wave | The statutory artefact | When it is issued | What is closed |
|:--:|---|---|---|
| W1 | — | — | No statutory PONR |
| W2 | — | — | — |
| **W3** | **The first Mushak 6.3 invoice issued on the new sequence** | Immediately after go, on the first sale | **The sequence has advanced. `M51`: *"the first thing an NBR audit looks for, and it cannot be corrected afterwards."*** Only `M4` remains |
| **W4** | The Mushak 6.3 **sequence assertion** and the input-VAT opening position agreed to the last filed 9.1 | At load (`DM-003` W4 step 9) | The asserted position is the basis for the next filing |
| **W5** | **The first payroll run, paid** (`G5-01`) | The first payroll date after go | Money has left the account. Only `M4` |
| W6–W8 | Per module; generally none | — | — |

> **`RBK-13`.** For W3, W4 and W5 the runsheet identifies `P-STAT` as an explicit step, and the
> Cutover Manager announces it on the bridge. Everyone on the bridge must know the moment the
> mechanisms available to them change.

### 5.4 The W3 statutory window is the tightest in the programme

| Moment | Elapsed after go | Available mechanisms |
|---|---|---|
| Go decision | 0 | `M3` (restore), `M4` |
| First user transaction | Minutes | `M4`, and `M3` only at the cost of that transaction |
| **First Mushak 6.3 issued** | **Possibly within the first hour of trading** | **`M4` only** |

> **`RBK-14` — for W3, an option exists and must be a recorded decision: hold invoicing.** Releasing
> the new system to users **without** enabling Mushak-bearing invoicing for a declared period keeps
> `P-STAT` open while `P-BUS` closes. It costs the business the ability to invoice for that period.
> **The decision belongs to the CFO, before the cutover, not to whoever is on the bridge**, and it is
> recorded as `MG-007-D-03` with the period left for the CFO to set (`Q-02`).

---

## 6. The Data-Loss Position at Each Stage

**`RBK-15`: at every stage of a cutover, the data-loss position is stated in advance, in the
runsheet, so that a rollback decision is taken with the loss already known.**

| Stage | Rollback mechanism | **What is lost** | Recoverable from |
|---|:--:|---|---|
| Pre-freeze | none needed | Nothing | — |
| Freeze declared, no extract | `M1` | Nothing. Legacy resumes | The freeze is lifted; `P2` paper is keyed to legacy (`CV-16`) |
| Extract taken, staging populated | `M1` | Nothing | Extracts are retained; staging is rebuildable |
| **First target write (`P-TECH`)** | `M2` | Nothing, if `M2` completes | Staging + extracts |
| All tiers loaded, not reconciled | `M2` | Nothing | *ibid.* |
| Reconciled, signed, **not released** | `M2` | Nothing | *ibid.* — **this is the last clean point** |
| **Released to users (`P-BUS`)** | `M2` fails; `M3` | **Every user transaction since the restore point** | **Only from the `P2`/post-go paper record, if one was kept** |
| **Statutory artefact issued (`P-STAT`)** | `M4` only | Nothing is *lost*; the error becomes **part of the permanent record** and is corrected forward | Corrective entries; an amended filing where permitted |
| Parallel run under way | `M4` | As above, plus divergence between two systems that must be reconciled manually | The daily comparison record (`MG-004` §5.3) |
| **Legacy withdrawn (`P4`)** | **None** | **There is nothing to fall back to** | — |

> **`RBK-16` — the last row is the one to plan around.** Once a wave's legacy processes are
> withdrawn (`CV-03`, BRD §6.5), fallback has no destination. **`RL-006` legacy decommissioning must
> not retire a source until the parallel run has exited and a declared stabilisation period has
> passed.** `RL-006` is ⛔; this rule is the interface it must honour, raised as `Q-04`.

> **`RBK-17` — during `P2` and the parallel run, the paper record is the only recovery path for
> user transactions.** `CV-11`'s numbered paper forms are not an inconvenience; between `P-BUS` and
> a successful reconciliation they are **the sole means of reconstructing what happened**. This
> raises the priority of `DM-014` `O-06` — the forms that do not exist — from administrative to
> recovery-critical.

---

## 7. The Rollback Procedure

### 7.1 Declaration

| # | Step |
|:--:|---|
| 1 | A trigger `T1`–`T7` fires, **or** a step's `abort_action` is `fallback` (`MG-006` `CUT-11`) |
| 2 | **The Cutover Manager declares fallback on the bridge, in plain words, and repeats it** (`CUT-28`). They declare; they do not decide (`CUT-03`, `MST-09`) |
| 3 | After `P-BUS`, the affected domain owner is joined to the decision (`RBK-11`) |
| 4 | The Scribe records the trigger, the instant and the declarer |
| 5 | The mechanism is selected from §4.3 by the tier reached and the PONR position |
| 6 | The Communications Officer releases the fallback message set (§8.4) |

### 7.2 Execution — `M2` tier reversal

| # | Step | Verification |
|:--:|---|---|
| 1 | **Stop all loading.** Confirm no step is mid-batch | `ctl_run` shows no running step |
| 2 | **Block user access** to the target if it was released | Access confirmed blocked |
| 3 | Reverse the **residency pass 2** through `CD-233` (`RBK-08`) | `resident_key` count for the batch is zero; deletions logged |
| 4 | Reverse tiers in exact reverse order (`RBK-05`), one tier at a time | Per tier: count by `migration_batch_id` returns zero |
| 5 | Remove `__migration__` external identifiers (`RBK-07`) | `ir.model.data` count for the batch is zero |
| 6 | **Verify no user-created record was deleted and none is orphaned** (`RBK-06`) | Referential check; if it fails, **escalate to `M3`** |
| 7 | Verify the target matches its pre-load state | Row counts per affected model against the pre-load baseline |
| 8 | Record the reversal in `ctl_xref` and close the batch as `reversed` | Batch state |
| 9 | Confirm rollback complete on the bridge, with the elapsed time | Scribe log |

### 7.3 Execution — `M3` full restore

| # | Step | Verification |
|:--:|---|---|
| 1 | Stop all loading; block all access | Confirmed |
| 2 | **Confirm the restore point and state the loss explicitly on the bridge** — everything after it | The Go/No-Go Authority acknowledges the loss |
| 3 | Restore the target database from the pre-load snapshot | Restore completes; integrity check passes |
| 4 | **Reconcile the restored state to the pre-load baseline** | Row counts per model |
| 5 | Reverse any `CD-233` writes made after the snapshot (they are **not** in the target database) | `RBK-18` |
| 6 | Restart application services; smoke test | Smoke suite green |
| 7 | Confirm complete on the bridge, with elapsed time | Scribe log |

> **`RBK-18` — the resident store is not restored by restoring the target database.** `CD-233`'s
> store is separate, with separate key material (`DA-001` §10.1). An `M3` restore leaves orphaned
> `resident_key` entries unless they are explicitly removed through `CD-233`. **This is the single
> most likely thing to be forgotten in an `M3` rollback**, and it leaves classified values in the
> resident store keyed to records that no longer exist.

### 7.4 The pre-load snapshot

| # | Rule |
|---|---|
| `RBK-19` | A **pre-load snapshot is taken as a runsheet step** immediately before the first target write, and its completion is **verified before loading starts** |
| `RBK-20` | The snapshot's **restore time is measured at `MG-005` `R3`**, at production data volume, and is part of the published rollback duration (`DRH-25`) |
| `RBK-21` | The snapshot is retained until the parallel run exits, then destroyed with a record |
| `RBK-22` | **A snapshot that has not been restored from in a rehearsal is not a snapshot; it is a file.** `MS-23` applies |

### 7.5 The published rollback duration

**`RBK-23`: each wave publishes, before its freeze, a single rollback duration** — the worst measured
case across the mechanisms available at the worst point (`DRH-25`) — and `MG-006` `CUT-32` computes
`T4` against it live.

| Component | Source |
|---|---|
| Declaration and mobilisation | `MG-005` §8.2 item 5 |
| Mechanism execution (`M2` or `M3`) | `MG-005` §8.2 items 1–3 |
| Verification | `MG-005` §8.2 item 4 |
| Legacy resumption and paper catch-up | `MG-005` §8.2 item 6; §8.3 below |

---

## 8. The Fallback Operating Model

### 8.1 The seam with `OP-014`

| | `OP-014` | **`MG-007` §8** |
|---|---|---|
| Triggered by | An **unplanned** outage | A **declared** cutover fallback |
| Warning | None | The freeze was already in force |
| Destination | Manual procedures while the ERP is unavailable | **The legacy estate**, which is still running |
| Duration | Until service is restored | Until the wave is re-attempted — **days to weeks** |
| Data reconstruction | Key manual records into the ERP when it returns | **Key the `P2` paper batch into the *legacy* system** (`CV-16`) |

> **`RBK-24`.** `OP-014`'s procedures are **reused where they apply** — the paper forms, the manual
> workarounds, the escalation contacts. What `OP-014` cannot supply is the direction: **on a
> migration fallback the destination is legacy, not paper indefinitely**, and the legacy system must
> be un-frozen.
>
> **Measured, not asserted.** `OP-014_Manual_Fallback_Procedure_Set.md` was written **2026-08-20**
> (after the enumeration `PGD-000` and `AUDIT-011` rest on) and stands at `Draft`, `P0`, wave `W1`.
> Searching it for *migration* and *cutover* returns **zero occurrences**, counted 2026-08-19 09:20
> (+06). Its §4.3 total-unavailability procedures and §4.6 catch-up and reconciliation are directly
> reusable; its trigger model, its destination and its duration are not. **The register's ◐ was
> correct, and it is correct for a sharper reason than "different artefact": `OP-014` never
> contemplates a planned reversion.**
>
> `OP-014` also declares `bilingual: yes` and names `OP-014_Manual_Fallback_Procedure_Set_BN.md`.
> **That file does not exist** — one of 16 declared `BN` counterparts missing across `CM` and `OP`
> (`MG-006` §7.3). A fallback executed at 51 branches by Bengali-first staff, from an English-only
> procedure set, is the same defect `CV-09` names. Audit finding `MGA-06`.

### 8.2 Un-freezing legacy

**This is the step most likely to be missed, because it is the opposite of everything the team spent
the night doing.**

| # | Step | Owner |
|:--:|---|---|
| 1 | Confirm the legacy estate is **still available** — not decommissioned, credentials valid, hosting live | Technical Standby |
| 2 | **Lift the freeze**, function by function, with the same eleven-function granularity `CV-10` used to impose it | Business Readiness Lead |
| 3 | **Key the `P2` paper catch-up batch into legacy** (`CV-16`) — the company must still know what happened during the window | Branch Managers |
| 4 | Re-issue the last-number positions so legacy sequences resume without a gap | Financial Controller |
| 5 | Confirm every site has resumed, by zone (`CUT-21`) | Zone Coordinators |
| 6 | Communicate resumption to staff and to customers with open jobs | Communications Officer |

> **`RBK-25` — `CV-16` is a recovery requirement, not an administrative one.** The paper batch keyed
> into legacy is the **only record** of what the business did during the freeze. If it is discarded
> because "we're rolling back anyway", the company has a gap in its trading record.

> **`RBK-26` — legacy availability is verified at `C2`, not assumed at the moment of fallback.**
> `SRC-001` and `SRC-002` are withdrawn at W2 (BRD §6.5); after that, a W2-or-later fallback has
> fewer legacy destinations than a W1 one. **`RL-006` decommissioning and fallback availability are
> the same question asked from two directions** (`RBK-16`, `Q-04`).

### 8.3 What the business does during the fallback period

| Function | During fallback |
|---|---|
| Front desk / intake | Legacy spreadsheets and paper resume |
| Workshop | Whiteboard and paper job cards resume; the preserved WIP photograph is the reconciliation point |
| Field / dispatch | Legacy dispatch resumes; paper visit forms keyed to legacy |
| Store / inventory | **If a physical count was completed, its result is preserved** — see `RBK-27` |
| Cash | Counted positions preserved; legacy cash records resume |
| Invoicing | Legacy sequence resumes from the recorded last number |
| Contact centre | Legacy lookup restored; the `P2` call-back list is worked |
| Customers | Told the transition is rescheduled — **not that something failed** (§8.4) |

> **`RBK-27` — a completed physical count survives a fallback.** The count is evidence of a physical
> position at an instant; it is not invalidated by a data rollback. It is **preserved, signed and
> re-used at the re-attempt**, adjusted for movements since. Re-counting 51 branches because a load
> failed is a cost the business should not pay twice, and `IV-14`'s count-window rule must be read
> with this in mind. Raised to `DM-007`/`DM-012` as a clarification, `Q-03`.

### 8.4 Communication on fallback

`DM-014` §4.10 owns the schedule for a successful cutover. **A fallback needs its own message set,
and `DM-014` does not have one.**

| Audience | Message | Timing | Confirmation? |
|---|---|---|:--:|
| Bridge | Fallback declared, in plain words (`CUT-28`) | Immediate | — |
| All staff in scope | **Return to the old system now.** Per-function resumption instruction, Bengali and English | Within the declared notification time | **Yes** |
| Branch managers | Resumption confirmation request, by zone | Immediate | **Yes** |
| Customers with open jobs | The transition is rescheduled; service continues normally | Within 24 h | No |
| Steering / Board | Trigger, position, next steps | Same day | — |
| Contact centre | Revised script; the `P2` call-back list is now live | Immediate | Yes |

> **`RBK-28` — the customer-facing message says the transition is rescheduled, and says nothing
> about a failure.** This is not spin: from the customer's position, nothing has failed — their
> service continues on the system it was always on. **A fallback executed correctly is the plan
> working**, and describing it as a failure teaches the organisation to avoid declaring one.

---

## 9. Re-attempt

### 9.1 The gate

`DM-014` `CV-18`: *"a wave may be re-attempted only after the trigger's root cause is closed — never
on the assumption that the next attempt will go better."* Adopted unchanged.

**`RBK-29`: the re-attempt gate has five conditions, all of which must hold.**

| # | Condition | Evidence |
|:--:|---|---|
| 1 | The **root cause is identified and closed** | The `CV-17` post-mortem, within five working days |
| 2 | The **fix has a test**, and the test is in the pipeline suite | `ETR-26` |
| 3 | The affected tier has been **re-rehearsed**, with new measurements | `MG-005` `R1` minimum; `R3` if the window changed |
| 4 | The **window arithmetic still closes**, recomputed | `DRH-13`, `DRH-16` |
| 5 | Extracts and counts are **still valid**, or scheduled to be retaken | §9.2 |

### 9.2 What has to be redone

| Artefact | Still valid? |
|---|---|
| Profiles (`MG-002`) | Yes, unless a supersession trigger fired (`LPX-31`) |
| Extracts | **Only if the freeze held.** If legacy resumed trading (§8.2), a **new extract is required** |
| **Physical counts** | **Yes, preserved** (`RBK-27`), adjusted for movements since |
| Control totals | Re-derived if the cut-off instant changes; **finance totals almost always change** because a period has moved |
| `R5` inspections | Redone — they were of a dataset that no longer exists |
| Sign-offs | **Redone.** A signature is against a specific reconciliation |
| Branch readiness confirmations | Redone |
| The rehearsal | Per condition 3 |

> **`RBK-30` — a re-attempt is a new cutover, not a resumption.** It gets a new batch id, a new
> cut-off instant, a new runsheet and new sign-offs. Treating it as "finishing what we started" is
> how a stale extract reaches production.

### 9.3 The wave-slip consequence

**`RBK-31`: a fallback is reported to the Steering Committee with its schedule consequence**, not
only its technical cause. `GV-004` §5.2 records that W3 has **zero float** at 1.00× capacity and
`GV-004` §4.3 records that the programme's +3-month tolerance is **already consumed before Month 0**.
A wave slip is therefore a programme-level event, and `GV-005` RAID carries it.

---

## 10. Interface to Major Incident Management

**A rollback is a planned procedure. What follows a *failed* rollback is an incident.**

| Situation | Handled as | Owner |
|---|---|---|
| A trigger fires; rollback executes as planned | **A cutover event**, this document | Cutover Manager |
| `M2` fails because user records reference migrated ones (`RBK-06`) | Escalate to `M3` — still this document | Cutover Manager |
| **`M3` fails** — the snapshot will not restore, or the restore is corrupt | **A major incident** | `SV-006` ⛔ → CTO |
| Data loss beyond the declared position (§6) | **A major incident**, and potentially a **personal-data incident** (`SC-011`) | CTO with the DPO |
| Legacy unavailable when fallback is declared | **A major incident** | CTO |

> **`RBK-32`.** `SV-006` (problem and major-incident management) is ⛔ and `SV-004` (on-call and
> paging) is ⛔. `AUDIT-017`: *"the programme has operational content and no operational
> capability."* **Two of the five rows above escalate to a procedure that does not exist**, and the
> escalation path for a cutover-night major incident is currently the CTO's mobile number. Raised as
> `Q-05`.

> **`RBK-33`.** A rollback that loses personal data beyond the declared position is assessed against
> `SC-011` (security incident response) and the PDPA 2026 notification obligations **within the
> statutory window**, not after the wave is re-attempted.

---

## 11. Governing Rules

> Class: **H** hard block · **A** approved override · **S** soft warning · **C** computed.

| # | Rule | Class |
|---|---|:--:|
| `RBK-01` | Four mechanisms, not one; the plan states where reversal stops being available | **H** |
| `RBK-02` | Rollback, fallback, recovery and re-attempt are used as defined in §3 | **C** |
| `RBK-03` | A rollback plan without a fallback operating model is incomplete | **H** |
| `RBK-04` | `M2` depends on `migration_batch_id` on every migrated record | **H** |
| `RBK-05` | `M2` deletes in exact reverse tier order | **H** |
| `RBK-06` | `M2` never deletes a user-created record; a reference from one makes `M2` a failure, not a warning | **H** |
| `RBK-07` | `M2` removes the `__migration__` external identifiers it created | **H** |
| `RBK-08` | Residency entries are removed **through `CD-233`**, first, never by touching the resident store | **H** |
| `RBK-09` | `M2` completeness is verified by count and recorded per record | **H** |
| `RBK-10` | Posted financial entries are never deleted; `M3` or `M4` only | **H** |
| `RBK-11` | After `P-BUS`, a rollback decision requires the Go/No-Go Authority **and** the affected domain owner | **H** |
| `RBK-12` | Users are released only after reconciliation is signed. Early release closes the rollback window and is prohibited | **H** |
| `RBK-13` | For W3, W4 and W5 the runsheet marks `P-STAT` explicitly and it is announced on the bridge | **H** |
| `RBK-14` | Whether to hold Mushak-bearing invoicing after W3 go-live is a CFO decision taken before the cutover | **A** |
| `RBK-15` | The data-loss position is stated in the runsheet at every stage, in advance | **H** |
| `RBK-16` | Legacy is not retired until the parallel run has exited and a stabilisation period has passed | **H** |
| `RBK-17` | Between `P-BUS` and a signed reconciliation, the paper record is the sole recovery path | **H** |
| `RBK-18` | An `M3` restore does not restore the resident store; `CD-233` entries are removed explicitly | **H** |
| `RBK-19` | A pre-load snapshot is a verified runsheet step before the first target write | **H** |
| `RBK-20` | Restore time is measured at `R3` at production volume | **H** |
| `RBK-21` | The snapshot is retained until parallel-run exit, then destroyed with a record | **H** |
| `RBK-22` | An unrestored snapshot is a file, not a snapshot | **H** |
| `RBK-23` | Each wave publishes one worst-case rollback duration before its freeze | **H** |
| `RBK-24` | `OP-014` procedures are reused; the destination on a migration fallback is legacy | **C** |
| `RBK-25` | The `P2` paper batch is keyed into legacy even when rolling back | **H** |
| `RBK-26` | Legacy availability is verified at `C2`, not assumed at fallback | **H** |
| `RBK-27` | A completed physical count survives a fallback and is re-used at the re-attempt | **H** |
| `RBK-28` | The customer message says rescheduled, not failed | **C** |
| `RBK-29` | The re-attempt gate has five conditions, all of which must hold | **H** |
| `RBK-30` | A re-attempt is a new cutover with a new batch id, cut-off, runsheet and sign-offs | **H** |
| `RBK-31` | A fallback is reported with its schedule consequence to Steering and `GV-005` | **H** |
| `RBK-32` | A failed `M3`, or legacy unavailability, is a major incident | **H** |
| `RBK-33` | Data loss beyond the declared position is assessed under `SC-011` and PDPA notification | **H** |

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **`PE-007` is unwritten.** Snapshot and restore capability, its performance at production volume, and where snapshots live are infrastructure design decisions with no owning document | CTO with the `PE-007` author | **W1 minus 3 months** | `M3`; `RBK-19`…`RBK-22`; the published rollback duration |
| `Q-02` | **Does W3 hold Mushak-bearing invoicing after go-live, and for how long?** It is the only lever that keeps `P-STAT` open, and it costs invoicing capability | **CFO** | **W3 minus 2 months** | `RBK-14`; the W3 rollback position |
| `Q-03` | **Does a completed physical count survive a fallback?** `RBK-27` says yes; `IV-14` voids a count outside its window. The two must be reconciled | Warehouse Manager with the Programme Content Lead | **W2 minus 2 months** | Whether a W2 fallback costs 51 recounts |
| `Q-04` | **`RL-006` is unwritten.** `RBK-16` requires legacy retention through stabilisation; nothing currently prevents a source being retired while fallback still depends on it | Programme Director with the `RL-006` author | **W2** | Fallback availability from W2 onward |
| `Q-05` | **`SV-004` and `SV-006` are ⛔.** Two escalation paths in §10 lead to procedures that do not exist | Support Lead with CTO | **W1** | `RBK-32`; cutover-night incident handling |
| `Q-06` | **Who exercises the `M3` restore, and how often?** `RBK-22` requires a restore to have been performed; `MG-005` rehearses it per wave, but the capability decays between waves | Technical Standby with `PE-007` | **W1** | `M3` confidence |

---

## 13. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `MG-007-D-01` | Rollback approach | One mechanism · **four mechanisms selected by tier and PONR** | **Four** | Finance and payroll cannot be reversed by deletion; a single mechanism would be wrong for three of ten tiers | More to rehearse; a clearer decision at the moment it matters |
| `MG-007-D-02` | User release timing | Release at go for a head start · **release only after reconciliation is signed** | **After sign-off** | The `P-TECH`→`P-BUS` interval **is** the rollback window (`RBK-12`) | Users wait; the wave stays reversible |
| `MG-007-D-03` | W3 Mushak invoicing hold | No hold · **a CFO-declared hold period** | **CFO-declared hold**, period to be set | The only lever that keeps `P-STAT` open past go | Invoicing is unavailable for the declared period (`Q-02`) |
| `MG-007-D-04` | Finance tier reversal | `M2` deletion · **`M3`/`M4` only** | **`M3`/`M4`** | Deleting posted entries breaks the audit trail and the statutory sequences | The finance rollback window is bounded by snapshot validity, and is the shortest in the programme |
| `MG-007-D-05` | Physical counts after a fallback | Recount · **preserve and re-use** | **Preserve and re-use** | A count is evidence of a physical position, not of a data load | Requires an `IV-14` clarification (`Q-03`) |

---

## 14. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Rollback mechanics are specified — the `AUDIT-011` `DM-01` item 4 gap | §4, §7 |
| `AC-02` | The point of no return is analysed as three distinct points with owners | §5 |
| `AC-03` | The data-loss position is stated for every stage | §6 |
| `AC-04` | A fallback operating model exists, distinct from `OP-014` | §8 |
| `AC-05` | `T4`'s number has a defined source and a worst-case rule | §7.5; `MG-005` §8 |
| `AC-06` | Finance and payroll reversal is treated as accounting, not deletion | §4.4; `RBK-10` |
| `AC-07` | The residency store's separate reversal is specified for both `M2` and `M3` | `RBK-08`, `RBK-18` |
| `AC-08` | The re-attempt gate is defined with five conditions and a redo list | §9 |
| `AC-09` | Escalation to major incident is defined, including where the target does not exist | §10; `Q-05` |
| `AC-10` | No `DM-014` trigger or rule is restated | Verified at issue (`MST-01`) |

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `DM-014` | Triggers `T1`–`T7`; `CV-15`–`CV-18` — adopted whole |
| Upstream | `DM-003` §4.6, `SQ-08` | Reverse tier order; reload policy |
| Upstream | `MG-003` | `migration_batch_id`, external identifiers and `ctl_xref` make `M2` possible |
| Upstream | **`MG-005`** | **Measures every duration this plan publishes** |
| Upstream | `MG-006` | The runsheet's `rollback_step`, `ponr` and `abort_action` columns |
| Upstream | `OP-014` | Manual procedures reused during fallback |
| Downstream | `GV-005` | A fallback is a RAID event with a schedule consequence |
| Downstream | `PE-007` ⛔ | Snapshot/restore capability |
| Downstream | `SV-006` ⛔, `SV-004` ⛔ | Major-incident escalation |
| Downstream | `RL-006` ⛔ | Must not retire legacy while fallback depends on it |
| Downstream | `SC-011` | Data loss beyond the declared position |

---

## 16. References

**Within this repository**
[`MG-001`](MG-001_Data_Migration_Strategy.md) · [`MG-003`](MG-003_ETL_Design_and_Transformation_Rules_Specification.md) ·
[`MG-004`](MG-004_Reconciliation_and_Validation_Plan.md) · [`MG-005`](MG-005_Mock_Migration_and_Dress_Rehearsal_Plan.md) ·
[`MG-006`](MG-006_Cutover_Plan_and_Runbook.md) ·
[`../05_Security_Privacy_and_Compliance/SC-011_Security_Incident_Response_Plan.md`](../05_Security_Privacy_and_Compliance/SC-011_Security_Incident_Response_Plan.md)

**Workspace**
`../../project_content/12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md` ·
`../../project_content/17_Operations_Support_and_Runbooks/OP-014_Manual_Fallback_Procedure_Set.md` ·
`../../project_content/_AUDIT/AUDIT-011_Category_12_DM_Content_Audit.md` ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md` §6.5, §11.6 `MIG-007`

**External standards**

| Source | Used for | Verified |
|---|---|---|
| ISO/IEC 20000-1:2018 §8.5.1 | Documented back-out as a change-control requirement | 2026-08-18 |
| ISO 22301:2019 §8.4 | Business continuity procedures, applied to §8 | 2026-08-18 |

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Data Migration Lead with the CTO | Initial issue. Specifies four rollback mechanisms, the three points of no return, the data-loss position at every stage, the fallback operating model distinct from `OP-014`, and the re-attempt gate. Supplies the mechanics `AUDIT-011` `DM-01` found unspecified | CTO with CFO *(pending — `GV-001` `CC-01`)* |

---

*`MG-007` · Category 09 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
