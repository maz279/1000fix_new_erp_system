---
id: MG-005
title: Mock Migration and Dress Rehearsal Plan
category: 09 — Data Migration & Cutover
code: MG
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Data Migration Lead
approver: Chief Technology Officer with the Programme Director
standards_basis: >
  BRD MIG-005 (trial migration with business UAT before every cutover) · BRD MIG-007 (documented,
  rehearsed rollback plan) · 05-06 OPS-07 (tested against a production-sized dataset) ·
  ISO/IEC/IEEE 29119-3:2021 — test plan and test completion report structure ·
  PDMv2 (BCS 2012) — dress rehearsal and migration design testing
traces_to: >
  PGD-000 MG-005 · AUDIT-011 DM-01 (the T4 trigger that cannot be evaluated) · DM-014 P0, CV-13,
  CV-20, C1, trigger T4 · DM-003 SQ-08, SQ-11 · DM-013 RV-10 · GV-009 wave gates
depends_on: MG-001 · MG-002 · MG-003 · MG-004 · MG-007 · QA-001 · QA-002 · PE-002 (absent)
verified_on: 2026-08-18
priority: P0
needed_by: W2
enumeration_timestamp: 2026-08-18 22:55 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# MG-005 — Mock Migration and Dress Rehearsal Plan

### Category 09 · Code `MG` · BRD `MIG-005`/`MIG-007` · `05-06` `OPS-07` · ISO/IEC/IEEE 29119-3:2021 · PDMv2

---

> **Local rule prefix: `DRH-nn`.** Verified unused workspace-wide at 2026-08-18 22:55 (+06).

---

## 1. Purpose

**Every duration in the migration plan is an estimate, and one of the fallback triggers compares a
real clock against one of them.**

`DM-014` trigger `T4` fires fallback when *"the remaining window is shorter than the measured
rollback duration"*. `AUDIT-011` `DM-01` singles it out as the sharpest instance of the missing
strategy: **a rule that cannot be evaluated, because nothing specifies how a rollback is performed
and no rollback has ever been rehearsed.**

Four documents require rehearsal independently — BRD `MIG-005`, BRD `MIG-007`, `05-06` `OPS-07`,
`DM-003` `SQ-11` — and `DM-014` `CV-13` states the principle exactly: *"a runsheet whose durations
are estimates has not been rehearsed."*

**Nothing says how many rehearsals, of what scope, measuring what, exiting on which criteria.** This
document does.

### 1.1 What a rehearsal is for

Not, primarily, to find software defects. Those are found by `MG-003`'s test suite and by `QA-001`'s
test levels. A rehearsal exists to produce **four numbers and one decision**:

| # | Output | Consumed by |
|:--:|---|---|
| 1 | **The measured duration of every runsheet step** | `MG-006` runsheet; the window arithmetic |
| 2 | **The measured duration of a rollback, per tier** | `MG-007`; **trigger `T4`** |
| 3 | **The point of no return**, located in real time | `MG-007` §5 |
| 4 | **The defect and exception profile** the production load will produce | `MG-004` queue sizing; hypercare planning |
| 5 | The **`C1` recommendation** — that this cutover may proceed | `DM-014` checkpoint `C1` |

> **`DRH-01`.** A rehearsal that produces a green tick and no numbers has not been performed. Its
> deliverable is a **measurement report** (§9), not a pass/fail.

### 1.2 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The rehearsal ladder — four rehearsal types and what each proves (§3) |
| 2 | How many rehearsals each wave gets, derived from its migration class (§4) |
| 3 | **The measurement protocol** — what is timed, how, and the human steps everyone forgets (§5) |
| 4 | The rehearsal environment and its data (§6) |
| 5 | The **branch rehearsal count** for physical waves (§7) |
| 6 | **Rollback rehearsal** — where `T4`'s number comes from (§8) |
| 7 | The measurement report and defect capture (§9) |
| 8 | Entry and exit criteria; the `C1` recommendation (§10) |
| 9 | Rules `DRH-01`…`DRH-31` (§11) |

**Explicitly out of scope**

| Topic | Owned by |
|---|---|
| Pipeline design and its unit tests | **`MG-003`** |
| Reconciliation method and sampling | **`MG-004`** |
| Rollback **mechanics** | **`MG-007`** — this document rehearses and times them |
| The production runsheet | **`MG-006`** — generated from these measurements |
| Freeze windows and branch communication content | `DM-014` |
| System, integration and UAT testing generally | `QA-001`, `QA-002` — **both issued during this session**, re-enumerated 2026-08-19 09:30 (+06). The `R2` business-UAT rehearsal (§3) and `QA-002`'s UAT level describe overlapping activity and the seam is **not yet reconciled**; audit finding `MGA-07` |
| Environment provisioning and sizing | `PE-002` ⛔ |

---

## 2. Basis

### 2.1 The four independent requirements

| Source | Requirement | Where discharged |
|---|---|---|
| **BRD `MIG-005`** | Trial migration into `staging` with **business UAT** before every cutover | §3 `R2`; §10 exit criteria include business acceptance |
| **BRD `MIG-007`** | Documented, **rehearsed** rollback plan for every cutover | §8 |
| **`05-06` `OPS-07`** | Forward-only, **tested against a production-sized dataset**, reversible by a documented procedure | §6.2 |
| **`DM-003` `SQ-11`** | A dry run against production-sized data precedes every production load | §3, §4 |
| **`DM-014` `CV-13`, `CV-20`** | Durations measured in `P0`, not estimated; a **rehearsal count** at representative branches before W2 | §5, §7 |
| **`DM-013` `RV-10`** | A dry run produces an **identical report** to a production run | §9.2 |

### 2.2 Standards conformance

| Standard | Clause | Conformance | Departure |
|---|---|---|---|
| **ISO/IEC/IEEE 29119-3:2021** | Test plan (§5.2) and test completion report (§5.4) structures | §3–§4 are the plan; §9 is the completion report | A rehearsal is not a test level: **its primary output is measurement, not defect discovery**. §1.1 states the departure explicitly |
| **PDMv2** (BCS 2012) | Migration design testing; the dress rehearsal as the final proof | §3's ladder is PDMv2's progression from unit proving to full dress rehearsal | PDMv2 assumes one cutover; §4 scales it to nine of four different shapes |
| `GV-009` | Gate evidence classes | §10's exit criteria produce `E7` evidence usable at the gate | — |

---

## 3. The Rehearsal Ladder

**Four types.** Each proves something the previous one could not, and each costs more.

| Type | Name | Scope | Data | Environment | Proves |
|:--:|---|---|---|---|---|
| **`R0`** | **Pipeline proving** | One tier at a time | Synthetic or a small real subset | `dev` / `migration-staging` | The pipeline runs, transforms correctly, and rejects what it should |
| **`R1`** | **Mock migration** | **All tiers of the wave, in sequence** | Real extracts, **full volume** | `migration-staging` → a rehearsal target | The sequence works end to end; reconciliation balances; **first real durations** |
| **`R2`** | **Trial migration with business UAT** | All tiers, plus **business validation of the result** | Real, full volume | `staging` (masked per `NFR-086c`) | **BRD `MIG-005`.** The business can operate on the migrated data |
| **`R3`** | **Timed dress rehearsal** | The **entire cutover runsheet**, including freeze, human steps, checkpoints, sign-offs **and a rollback** | Real, full volume, production-sized | Rehearsal environment | The window arithmetic; **`T4`'s number**; the point of no return |

> **`DRH-02` — `R3` is not `R1` with a stopwatch.** `R1` measures the machine. `R3` measures the
> **operation**: people arriving, checkpoints being called, a domain owner reading a 149-record
> sample, a signature being obtained at 04:00, a decision being taken. §5.3 is the reason this
> distinction is load-bearing.

> **`DRH-03` — `R2` and `R3` may not be combined.** `R2` is masked and business-facing; `R3` is
> production-sized and clock-facing. Running them together produces a rehearsal that is neither
> valid UAT nor a valid timing, and it is the obvious economy that will be proposed.

---

## 4. How Many Rehearsals, Per Wave

### 4.1 Derived from the migration class

`MG-001` §4.3 classes each wave A (volume), B (physical), C (statutory) or D (bounded). The rehearsal
count follows from the class, so it is a derivation and not a negotiation.

| Wave | Class | `R0` | `R1` | `R2` | `R3` | Branch count rehearsal (§7) | Rationale |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|
| **W1** | **A — volume** | Per tier | **2** | **1** | **1** | — | First cutover of the programme; the window is arithmetic nobody has run; 300,000–600,000 devices |
| **W2** | **B — physical** | Per tier | 1 | 1 | **1** | **✔ mandatory** (`CV-20`) | Counting capacity, not compute; 200–400 van recalls |
| **W3** | **C — statutory** | Per tier | **2** | 1 | **1** | **✔ cash count** | T-EXACT finance; auditor agreement; period-end bound |
| **W4** | **C — statutory** | Per tier | 1 | 1 | **1** | — | **Mushak 6.3 sequence assertion is uncorrectable afterwards** |
| **W5** | **B — physical** | Per tier | **2** | 1 | **1** | **✔ asset verification** | **YTD payroll: `M56`'s "most dangerous migration"**; 100% verification |
| **W6–W8** | **D — bounded** | Per tier | 1 | 1 | — | — | Smaller populations; no statutory exposure |

> **`DRH-04`.** **Every wave gets at least one `R3` except D-class waves**, and `W1`, `W3` and `W5`
> get two `R1`s because each carries a first-of-its-kind risk: the first cutover ever, the first
> T-EXACT reconciliation, and the first per-employee YTD verification.

> **`DRH-05` — a D-class wave without an `R3` still rehearses its rollback** (§8). Skipping the
> timed dress rehearsal does not skip `T4`.

### 4.2 Timing relative to cutover

`DM-014` places `P0` rehearsal from **T−21 to T−7 days**. This document sequences within it.

| Rehearsal | Timing | Why |
|---|---|---|
| `R0` | Continuous through build | It is a development activity |
| `R1` #1 | **T−45 days** | Early enough that a discovered defect can be fixed and re-rehearsed |
| `R1` #2 *(where applicable)* | T−28 days | Confirms the fixes |
| `R2` | **T−21 days** | Business availability; `DM-014` `P0` opens |
| **`R3`** | **T−14 days** | Late enough to be representative; early enough that a failure does not force a wave slip |
| Branch count rehearsal | **T−21 days**, per zone | Storekeepers need to have counted before the night that matters |

> **`DRH-06` — `R3` at T−7 is too late and is not permitted.** If `R3` fails at T−7 there is no time
> to remediate and re-rehearse, so the only available decisions are *go anyway* or *slip the wave* —
> which is precisely the position a rehearsal exists to avoid.

---

## 5. The Measurement Protocol

### 5.1 What is timed

**`DRH-07`: every runsheet step is timed independently, with start and end instants recorded to the
minute, by an observer who is not performing the step.**

| Phase | Steps timed |
|---|---|
| **Pre-freeze** | Final delta extract per source; extract transfer; manifest verification |
| **Freeze** | Function-by-function stop confirmation (§5.3); last-number recording |
| **Extract** | Per source: extraction, transfer, hash verification, Z1→Z2 parse |
| **Transform** | Per domain: Z2→Z3 cleanse, Z3→Z4 conform, Z4→Z5 payload build |
| **Load** | **Per tier and per model**: rows loaded, elapsed, rows/second |
| **Residency pass 2** | Separately — it is a different mechanism at a different rate (§6.4) |
| **Reconcile** | Per tier: `R1`–`R4` computation |
| **Inspect** | **`R5` sample preparation, and the owner's actual inspection time** (§5.3) |
| **Sign** | Time from report ready to signature obtained |
| **Checkpoint** | Time from criteria met to decision recorded |
| **Rollback** | §8 — per tier, in reverse order |
| **Smoke test** | Post-load verification before release |

### 5.2 How it is recorded

| # | Rule |
|---|---|
| `DRH-08` | Machine steps are timed by the harness and written to `ctl_run` (`MG-003` §8.2). Human steps are timed by a **named observer** with a clock |
| `DRH-09` | Every measurement records **wall-clock elapsed**, not CPU time. A step that waited three hours for a person took three hours |
| `DRH-10` | Measurements are recorded **as observed**, including the ones that embarrass the plan. A rehearsal that reports the times the team wishes it had achieved is worse than no rehearsal |
| `DRH-11` | Each step's measurement carries the **volume it processed**, so that a production volume different from the rehearsal's can be scaled — and the scaling assumption is stated |

### 5.3 The human steps, which are the ones that run late

**This is the section that justifies `R3` existing separately from `R1`.**

| Step | Why it is slow | Typical underestimate |
|---|---|---|
| **Function-by-function freeze confirmation** | `DM-014` `CV-10` requires **eleven functions** to each confirm they have stopped, and at W2/W3/W5 that is across **51+ sites** | Planned as "the freeze instant"; actually a reply-collection exercise across dozens of people |
| **`R5` sample inspection** | `MG-004` §7.3 requires **149 records for party and asset, 299 for finance**, inspected **end to end** by the domain owner | Planned as minutes; it is hours, and the reader is tired |
| **Payroll YTD verification** | **100% of 500+ employees** (`MG-004` `MG-004-D-02`) | Cannot be compressed; it must be scheduled as its own activity |
| **Obtaining a signature** | The approver must be awake, present, and willing (`RVP-03`) | Assumed instantaneous |
| **Checkpoint decisions** | `C7` requires **two named people jointly** and is not delegable (`CV-14`) | Assumed instantaneous |
| **Physical count reporting** | 51 branches reporting a completed count up a chain | Assumed parallel; it is bounded by the slowest branch |
| **Brand and customer confirmations** | 17+ brands; top-50 customers, in writing | External parties do not operate on a cutover clock |

> **`DRH-12` — the `R3` rehearsal includes the human steps with the actual people.** A rehearsal in
> which the migration team signs on the CCO's behalf has measured nothing about the step that will
> take longest. If the CCO cannot attend the rehearsal, that is itself the finding, and it is better
> discovered at T−14 than at `C6`.

### 5.4 The window arithmetic

**`DRH-13`: the cutover window is computed, published and challenged before every cutover**, from
measured components, not asserted.

```
  WINDOW  =  freeze_confirmation
           + extract  (Σ per source, incl. the slowest — usually a rate-limited PORTAL)
           + transform
           + load     (Σ per tier, respecting SQ-07 parallelism limits)
           + residency_pass_2
           + reconcile
           + inspect  (human — §5.3)
           + sign     (human)
           + checkpoints (human)
           + smoke_test
           + CONTINGENCY

  and the constraint that makes T4 evaluable:

  WINDOW + rollback_duration(worst tier)  ≤  available_window
```

| # | Rule |
|---|---|
| `DRH-14` | **Contingency is a declared percentage of the measured total, set before the rehearsal, not the gap between the measured total and the desired total** |
| `DRH-15` | The window is computed with the **residency pass 2 included**, even though it is rehearsed only against synthetic keys (`MG-001` `Q-04`). Its duration is estimated from the synthetic run and **flagged as the least reliable number in the arithmetic** |
| `DRH-16` | If `WINDOW + rollback ≥ available_window`, the cutover **does not proceed** at that scope. The remedies are: reduce scope (move a tier to `X9`/post-go), extend the window, or improve a measured step — never adjust the contingency downward |

---

## 6. The Rehearsal Environment and Its Data

### 6.1 The environment

**`05-06` `OPS-07` requires testing against a **production-sized** dataset. `MG-001` §7 records that
the environment does not exist and `PE-002` has not been written.**

| Requirement | Detail | Status |
|---|---|:--:|
| Production-sized storage and compute | Sized from `DA-001` §7 volumetrics plus migration staging | ⛔ `PE-002` |
| Production-equivalent configuration | Same Odoo version, same modules, same indexes, same PostgreSQL settings | ⛔ `PE-002` |
| Isolated from production | No shared database, no shared bus, **no shared notification provider** | ⛔ |
| **No outbound integrations** | §6.3 | ⛔ |
| Refreshable to a known baseline | A rehearsal must be repeatable from a clean state | ⛔ |
| Production-class access control | It holds real data (`MG-001` `MST-16`) | ⛔ |

> **`DRH-17`.** **A rehearsal on an undersized environment measures the undersized environment.**
> A load that takes 40 minutes on half the production I/O does not take 40 minutes in production,
> and the direction of the error is not predictable. `PE-002` must state the rehearsal environment's
> equivalence to production, or every measurement in §5 carries an unquantified correction factor.
> Raised as `Q-01`.

### 6.2 The data

`MG-001` §7.3 states the position and its residual risk. Restated here operationally:

| Data class | In the rehearsal | Control |
|---|---|---|
| Non-classified real data | **Yes, full volume** | Production-class controls (`MST-16`) |
| Residency-classified values (`S3`) | **No** | `MST-17`; pass 2 rehearsed against **synthetic keys** |
| Synthetic data | Only for pass-2 mechanism testing and `R0` | — |

> **`DRH-18`.** The rehearsal dataset is **destroyed on rehearsal completion**, with a recorded
> destruction, unless the next rehearsal is within a declared window. A rehearsal environment
> holding a copy of the customer base indefinitely is the quiet failure `SC-007` §7's quiet-copy
> prohibitions exist to prevent.

### 6.3 Integrations must be disconnected, and this must be tested

**`DRH-19`: the rehearsal environment has no outbound path to any real external system** — no
payment gateway, no SMS or email provider, no brand portal, no NBR endpoint, no bank.

| Risk | Consequence if not controlled |
|---|---|
| Notification provider connected | **A rehearsal emails or SMSes 100,000+ real customers** |
| Payment gateway connected | Settlement calls against real accounts |
| Brand portal connected | Claim submissions to 17+ real partners |
| Webhooks enabled | Partner push to real endpoints (`IN-006`) |

> **`DRH-20` — the `R3` rehearsal explicitly asserts, as a recorded test result, that zero outbound
> messages were emitted.** This is the same assertion `MG-003` `ETR-48` requires of event
> suppression, verified here in the environment where the whole load runs. Two independent
> mechanisms — suppression (`ETR-44`) and disconnection (`DRH-19`) — because the consequence is
> irreversible and public.

### 6.4 Pass-2 rehearsal, and what it does not prove

| Rehearsed | Not rehearsed |
|---|---|
| The `CD-233` call sequence and its throughput on synthetic values | Real-value validation failures |
| Idempotency of pass 2 (`ETR-22`) | The real reject profile |
| The hold-queue behaviour on failure (`ETR-21`) | How many real NIDs are malformed |
| Logging and step-up behaviour (`RS-05`) | — |

> **`DRH-21`.** The pass-2 measurement is reported with an **explicit confidence caveat** in §9's
> report. It is the one number in the window arithmetic derived from synthetic data, and it must not
> be presented alongside the measured numbers without that distinction.

---

## 7. The Branch Rehearsal Count

`DM-014` `CV-20` makes this mandatory before W2: *"the first time a storekeeper reads a count sheet
must not be the night the opening balance is established."* Nothing schedules it.

### 7.1 Scope

| Wave | What is rehearsed | Sites | Owner |
|:--:|---|---|---|
| **W2** | Stock count, van count, consignment confirmation | **A representative sample** — see §7.2 | Warehouse Manager with Branch Operations Lead |
| **W3** | Witnessed cash count; cheque stock count | Representative sample | Financial Controller |
| **W5** | Fixed-asset and test-equipment physical verification | Representative sample | CFO with Quality Manager |

### 7.2 What "representative" means

**`DRH-22`: the sample covers the extremes, not the average.**

| Dimension | Include |
|---|---|
| Size | The largest branch and one of the smallest |
| Geography | At least one outside Dhaka |
| Staffing | One branch with an experienced storekeeper and one with a recently-appointed one |
| Stock complexity | The central warehouse and a branch with van stock |
| Language | At least one branch where staff are **not** English-comfortable (`CV-09`, `DM-008` finding) |

> **A count rehearsal at five well-run Dhaka branches proves that well-run Dhaka branches can
> count.** The opening position depends on the weakest site, and `DM-014` §4.9 states it directly:
> *"a single missed branch is a hole in the opening position."*

### 7.3 What is measured

| Measure | Why |
|---|---|
| **Elapsed time to count one location**, by size band | The W2 window is bounded by this, not by compute (`CV-04`) |
| **Error rate on the count sheet** — miscounts, wrong bins, missed lines | Sizes the recount need |
| **Instruction comprehension**, in Bengali | `CV-09`; `DM-008` records the category is English-only while its audience is not |
| **Van recall and count time**, per van | 200–400 vans; field service degrades during recall |
| **Variance against the spreadsheet** | The `IV-03` baseline measurement, obtained early |
| Whether the branch could stay closed for the duration | The real operational constraint |

> **`DRH-23`.** The branch rehearsal produces a **count-throughput figure per site size band**,
> which is the input `MG-006` needs to schedule 51 sites by zone. Without it the W2 window is a
> guess about human beings.

> **`DRH-24` — the branch rehearsal is also the training.** `DM-014` §4.9 records that counting is
> done by branch staff who have never done a formal count, and that *"training and a rehearsal count
> are prerequisites, not niceties"*. The rehearsal discharges both, and `CH-*` (Category 13) must
> carry the training material — **which does not exist**, raised as `Q-04`.

---

## 8. Rollback Rehearsal

### 8.1 Why this section exists

**`T4` cannot be evaluated today.** `DM-014` trigger `T4` compares the remaining window against *"the
measured rollback duration"*, `DM-003` `SQ-08` requires rollback *"with a rehearsed and published
duration"*, and `DM-001` `MS-23` states that *"reversible means a rehearsed procedure with a measured
duration, not the existence of a backup"*.

**No rollback has been rehearsed. There is no number.**

### 8.2 What is rehearsed

`MG-007` specifies the mechanics; this document times them.

| # | Rehearsed | Measured |
|:--:|---|---|
| 1 | **Tier reversal in exact reverse order** (`SQ-08`): `X9`→`X8`→…→`X0` | Elapsed per tier |
| 2 | **Full-restore rollback** from the pre-load snapshot | Elapsed end to end, including restart and verification |
| 3 | **Partial rollback** — one failed tier with prior tiers retained | Elapsed; and whether it leaves a consistent state |
| 4 | **Verification after rollback** — that the target is genuinely back to its pre-load state | Elapsed; and the evidence produced |
| 5 | **The decision path** — trigger fires, fallback declared, roles notified | Elapsed from finding to declaration |
| 6 | **The `CV-16` paper catch-up** — keying the P2 batch back into the legacy system | Sampled, per transaction type |

### 8.3 The rule that makes the number honest

**`DRH-25`: the published rollback duration is the *worst* measured tier reversal plus verification,
not the average and not the best run.** `T4` is a safety comparison; using an optimistic number
converts it into a trap.

**`DRH-26`: the rollback is rehearsed by someone who did not build the pipeline**, from the written
`MG-007` procedure, with no verbal assistance. A procedure that only its author can execute is not a
procedure, and at 03:00 its author may be the person who has been awake longest.

**`DRH-27`: if the measured rollback duration does not fit the available window, the cutover scope is
reduced until it does.** This is `DRH-16` restated from the rollback side, and it is the single most
likely finding of the first `R3`.

### 8.4 Rollback rehearsal is required even where `R3` is not

`DRH-05`. D-class waves skip the timed dress rehearsal; they do not skip this. Every wave publishes
a measured rollback duration before its freeze.

---

## 9. The Measurement Report

### 9.1 Structure

**`DRH-28`: every rehearsal produces the same report**, and it is an evidence-pack item (`MG-004`
§6.2 item 8).

| § | Section | Contents |
|:--:|---|---|
| 1 | Header | Wave, rehearsal type, environment, dataset, instants, observer, participants |
| 2 | Scope | Tiers rehearsed; what was excluded and why |
| 3 | **Measurements** | Every §5.1 step: volume, start, end, elapsed, rate — machine and human separately |
| 4 | **Window arithmetic** | §5.4, computed, with contingency stated and the pass-2 caveat (`DRH-21`) |
| 5 | **Rollback** | §8: per-tier and full-restore durations; the **published figure** (`DRH-25`) |
| 6 | **Point of no return** | Where in the runsheet it fell, in elapsed time |
| 7 | **Reconciliation** | The full `DM-013` report, identical in format to production (`RV-10`) |
| 8 | **Exceptions** | `E1`–`E9` profile — the production forecast |
| 9 | **Defects** | §9.3 |
| 10 | **Environment fidelity** | Deviations from production, and their effect on the numbers (`DRH-17`) |
| 11 | **Outbound assertion** | Zero external messages emitted (`DRH-20`) |
| 12 | **Recommendation** | §10.3 |

### 9.2 The reconciliation must be identical

`DM-013` `RV-10`: *"a dry run produces an identical report to a production run, so that the two are
comparable and the production result is not the first time anyone has seen the format."* **`DRH-29`:
the rehearsal reconciliation uses `MG-004` unchanged, including the `R5` sample sizes and the actual
domain-owner inspection.** A rehearsal that skips the sample inspection has skipped the longest human
step and the one most likely to surface `E9`.

### 9.3 Defect capture

| Class | Definition | Handling |
|:--:|---|---|
| **`D1` Blocking** | The rehearsal could not complete, or a T-EXACT reconciliation failed | **Fix and re-rehearse.** Cutover does not proceed |
| **`D2` Semantic** | An `E9`-class defect — data loaded meaning something different | Fix the rule **and its test** (`ETR-26`); re-rehearse the affected tier |
| **`D3` Timing** | A step exceeded its planned duration such that the window no longer closes | `DRH-16` — reduce scope, extend window, or improve the step |
| **`D4` Operational** | A human step failed — an owner unavailable, an instruction misread, a confirmation not obtained | **Fix the operation**, not the software. Often the most valuable finding |
| **`D5` Environmental** | A rehearsal-environment artefact, not a real defect | Recorded, with its effect on the measurements |

> **`DRH-30` — `D4` defects are reported to the same standard as `D1`.** The instinct is to treat "a
> person was not available" as a rehearsal artefact rather than a finding. `DM-014` `CV-14` makes
> the `C7` decision non-delegable and held by two named people; if those two could not be assembled
> for a rehearsal at T−14, the probability they assemble at 04:00 on cutover night is the actual
> risk, and it belongs in the report.

---

## 10. Entry, Exit and the `C1` Recommendation

### 10.1 Entry criteria — a rehearsal may not start without these

| # | Criterion | Source |
|:--:|---|---|
| 1 | All sources for the wave are **profiled and accepted** | `MG-002` `LPX-06` |
| 2 | All mapping workbooks for the wave are **re-verified post-profiling** | `MG-001` `MST-13` |
| 3 | The pipeline passes its own test suite; every rule has a test | `MG-003` `ETR-26` |
| 4 | The run plan is generated from `DM-003` §4.4 | `ETR-11` |
| 5 | Control totals are **registered and frozen** | `MG-004` `RVP-07` |
| 6 | `MG-007` rollback procedures are **written** | `MG-007` |
| 7 | The rehearsal environment is available at declared fidelity | `PE-002` ⛔ |
| 8 | Outbound integrations are disconnected and the disconnection verified | `DRH-19` |
| 9 | Domain owners and their deputies are **booked** for `R3` | `MG-004` `Q-04` |

### 10.2 Exit criteria

| # | Criterion |
|:--:|---|
| 1 | Every planned tier completed, or its non-completion explained |
| 2 | **Full `R1`–`R5` reconciliation performed, in the production format, with real owner inspection** |
| 3 | Zero `D1`; zero unresolved `D2` |
| 4 | **A published rollback duration**, measured, worst-case (`DRH-25`) |
| 5 | **The window arithmetic closes**, including rollback (`DRH-16`) |
| 6 | The point of no return is located |
| 7 | Zero outbound messages asserted (`DRH-20`) |
| 8 | For `R2`: **business acceptance** of the migrated data (BRD `MIG-005`) |
| 9 | The measurement report is issued and filed in the evidence pack |

### 10.3 The `C1` recommendation

`DM-014` checkpoint `C1` — *rehearsal complete* — is decided by the Data Migration Lead recommending.
**`DRH-31`: the recommendation is one of three, and "proceed with reservations" is not among them.**

| Recommendation | Meaning |
|---|---|
| **Proceed** | Exit criteria met; the window closes with contingency; rollback is measured and fits |
| **Proceed with reduced scope** | Named tiers deferred to post-go or to a later wave, with the reduced window recomputed |
| **Do not proceed** | An exit criterion is unmet. The cutover is re-planned and re-rehearsed |

---

## 11. Governing Rules

> Class: **H** hard block · **A** approved override · **S** soft warning · **C** computed.

| # | Rule | Class |
|---|---|:--:|
| `DRH-01` | A rehearsal's deliverable is a measurement report, not a pass/fail | **H** |
| `DRH-02` | `R3` measures the operation, not only the machine | **H** |
| `DRH-03` | `R2` and `R3` may not be combined | **H** |
| `DRH-04` | Every wave except D-class gets at least one `R3`; W1, W3, W5 get two `R1`s | **H** |
| `DRH-05` | A wave without an `R3` still rehearses and publishes a rollback duration | **H** |
| `DRH-06` | `R3` runs at T−14, never at T−7 | **H** |
| `DRH-07` | Every runsheet step is timed by an observer who is not performing it | **H** |
| `DRH-08` | Machine steps timed by the harness; human steps by a named observer | **H** |
| `DRH-09` | Wall-clock elapsed, never CPU time | **H** |
| `DRH-10` | Measurements are recorded as observed, including the unflattering ones | **H** |
| `DRH-11` | Every measurement carries its processed volume and any scaling assumption | **H** |
| `DRH-12` | `R3` includes the human steps with the actual accountable people | **H** |
| `DRH-13` | The window is computed and published from measured components | **H** |
| `DRH-14` | Contingency is declared in advance as a percentage, never derived as a residual | **H** |
| `DRH-15` | Pass-2 duration is included and flagged as synthetic-derived | **H** |
| `DRH-16` | If window + rollback ≥ available window, scope is reduced. Contingency is never reduced | **H** |
| `DRH-17` | An undersized rehearsal environment invalidates the measurements unless its fidelity is stated | **H** |
| `DRH-18` | Rehearsal data is destroyed on completion, with a record | **H** |
| `DRH-19` | The rehearsal environment has no outbound path to any real external system | **H** |
| `DRH-20` | `R3` asserts zero outbound messages as a recorded test result | **H** |
| `DRH-21` | The pass-2 measurement carries an explicit confidence caveat | **H** |
| `DRH-22` | The branch rehearsal sample covers extremes, not averages | **H** |
| `DRH-23` | The branch rehearsal produces a count-throughput figure per site size band | **H** |
| `DRH-24` | The branch rehearsal is also the training event; its material must exist | **H** |
| `DRH-25` | The published rollback duration is the worst measured case | **H** |
| `DRH-26` | Rollback is rehearsed by someone who did not build the pipeline, from the written procedure | **H** |
| `DRH-27` | If rollback does not fit the window, scope is reduced until it does | **H** |
| `DRH-28` | Every rehearsal produces the same report, filed in the evidence pack | **H** |
| `DRH-29` | The rehearsal reconciliation is `MG-004` unchanged, including real owner inspection | **H** |
| `DRH-30` | `D4` operational defects are reported to the same standard as `D1` | **H** |
| `DRH-31` | The `C1` recommendation is one of three; "proceed with reservations" is not one | **H** |

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Does a production-sized rehearsal environment exist, funded and specified?** `PE-002` is unwritten; `OPS-07` requires production-sized testing | CTO with the `PE-002` author | **W1 minus 3 months** | Every `R1`, `R2`, `R3`; `DRH-17` |
| `Q-02` | **Who observes and times the human steps?** `DRH-07` requires an observer separate from the performer, across a multi-hour rehearsal | Data Migration Lead with PMO | W1 minus 2 months | `R3` validity |
| `Q-03` | **Are the domain owners and their deputies available for a full `R3`?** If not, `DRH-12` is unmet and the longest steps go unmeasured | Programme Director | **W1 minus 2 months** | `R3`; `DRH-30` |
| `Q-04` | **Who produces the branch counting training and instructions, in Bengali?** `DRH-24`; `CV-09`. `CM-012` now exists (written 2026-08-20) but its declared **Bengali counterpart does not**, and it is `P1` against a `P0` count | Change Lead with Localisation Lead | **W2 minus 3 months** | The W2 branch rehearsal and the W2 count |
| `Q-05` | **Is `R3` funded as an operational event?** It occupies domain owners, branch staff and the migration team for a full cutover duration, ×9 waves | Programme Director with `GV-007` | **W0** | Every `R3` |

---

## 13. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `MG-005-D-01` | Rehearsal ladder | One rehearsal per wave · **four types, count derived from migration class** | **Four types** | `R1` and `R3` prove different things; combining them measures neither | More rehearsals, and a real operational cost (`Q-05`) |
| `MG-005-D-02` | `R3` timing | T−7 (inside `DM-014` `P0`) · **T−14** | **T−14** | A failure at T−7 leaves only "go anyway" or "slip" | `P0` effectively starts earlier than `DM-014` states; referred to `DM-014` |
| `MG-005-D-03` | Published rollback duration | Average · best · **worst measured** | **Worst measured** | `T4` is a safety comparison; optimism converts it into a trap | Windows are tighter, and honestly so |
| `MG-005-D-04` | Human steps in `R3` | Simulated by the migration team · **performed by the actual accountable people** | **Actual people** | The longest steps are human; simulating them measures nothing | Requires owner availability (`Q-03`) — and their unavailability is itself a finding |
| `MG-005-D-05` | Outbound integration control | Suppression alone (`ETR-44`) · **suppression *and* environment disconnection** | **Both** | The consequence — messaging 100,000+ real customers — is irreversible and public | Two mechanisms to maintain and verify |

---

## 14. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | A rehearsal count is derived per wave from a stated basis | §4.1 |
| `AC-02` | The measurement protocol covers human steps explicitly | §5.1, §5.3 |
| `AC-03` | The window arithmetic is stated as a formula including rollback | §5.4 |
| `AC-04` | `T4`'s missing number has a defined source and a worst-case rule | §8, `DRH-25` |
| `AC-05` | The branch rehearsal is scheduled, scoped and measured | §7 |
| `AC-06` | The rehearsal environment's requirements and its absence are both stated | §6.1, `Q-01` |
| `AC-07` | Outbound-message risk is controlled by two independent mechanisms and tested | §6.3, `DRH-20` |
| `AC-08` | The rehearsal reconciliation is identical to production's | §9.2, `RV-10` |
| `AC-09` | Exit criteria and the `C1` recommendation set are defined and closed | §10 |
| `AC-10` | No unmeasured duration is published anywhere in this document | Verified at issue |

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `MG-001` | Migration class drives rehearsal count; environment position |
| Upstream | `MG-002` | Profiling acceptance is an entry criterion |
| Upstream | `MG-003` | The pipeline rehearsed; `ETR-48` verified here |
| Upstream | `MG-004` | The reconciliation performed unchanged; sample sizes drive the human timing |
| Upstream | `MG-007` | The rollback procedures rehearsed and timed |
| Upstream | `DM-014` | `P0`, `CV-13`, `CV-20`, checkpoint `C1`, trigger `T4` |
| Downstream | **`MG-006`** | **Every runsheet duration comes from here** |
| Downstream | `GV-009` | Rehearsal reports are gate evidence |
| Downstream | `PE-002` ⛔ | Must specify the rehearsal environment |
| Downstream | `CH-*` ⛔ | Branch counting training material |

---

## 16. References

**Within this repository**
[`MG-001`](MG-001_Data_Migration_Strategy.md) · [`MG-002`](MG-002_Legacy_System_Profiling_and_Extract_Specification.md) ·
[`MG-003`](MG-003_ETL_Design_and_Transformation_Rules_Specification.md) · [`MG-004`](MG-004_Reconciliation_and_Validation_Plan.md) ·
[`MG-006`](MG-006_Cutover_Plan_and_Runbook.md) · [`MG-007`](MG-007_Rollback_and_Fallback_Plan.md)

**Workspace**
`../../project_content/12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md` ·
`../../project_content/12_Data_Migration_Content/DM-013_Reconciliation_and_Validation_Report_Specification.md` ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md` §11.6 `MIG-005`, `MIG-007`

**External standards**

| Source | Used for | Verified |
|---|---|---|
| ISO/IEC/IEEE 29119-3:2021 | Plan and completion-report structures | 2026-08-18 |
| Johny Morris, *Practical Data Migration* (PDMv2), BCS 2012 | The rehearsal ladder | 2026-08-18 |

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Data Migration Lead | Initial issue. Defines four rehearsal types, per-wave counts, the measurement protocol including human steps, the window arithmetic, the branch count rehearsal and the rollback rehearsal that supplies trigger `T4`'s number | CTO with the Programme Director *(pending — `GV-001` `CC-01`)* |

---

*`MG-005` · Category 09 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
