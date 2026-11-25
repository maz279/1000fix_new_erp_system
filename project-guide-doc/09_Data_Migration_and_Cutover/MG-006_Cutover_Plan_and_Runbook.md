---
id: MG-006
title: Cutover Plan and Runbook
category: 09 — Data Migration & Cutover
code: MG
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Data Migration Lead with the Change Lead
approver: Chief Technology Officer with the Programme Director
standards_basis: >
  ITIL 4 — Release Management and Deployment Management practices · ISO/IEC 20000-1:2018 §8.5.1
  (change control) and §8.5.3 (release and deployment) · Incident Command System role model,
  applied to a planned operation · DM-014 phase and checkpoint model (adopted unchanged)
traces_to: >
  PGD-000 MG-006 · DM-014 CV-01…CV-22, C1…C9, T1…T7 · DM-003 §4.4 (SQ-18 runsheet generation) ·
  BRD §6.5 legacy withdrawal · 06-02 wave gates · GV-009 · AUDIT-011 DM-05, DM-08
depends_on: MG-001 · MG-002 · MG-003 · MG-004 · MG-005 · MG-007 · DM-014 · SV-004 (absent) · RL-002 (absent)
verified_on: 2026-08-18
priority: P0
needed_by: W2
enumeration_timestamp: 2026-08-18 23:05 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# MG-006 — Cutover Plan and Runbook

### Category 09 · Code `MG` · ITIL 4 Release & Deployment · ISO/IEC 20000-1:2018 §8.5 · ICS role model

---

> **Local rule prefix: `CUT-nn`.** Verified unused workspace-wide at 2026-08-18 23:05 (+06).

---

## 1. Purpose

`DM-014` is a strong 32 KB cutover **data** document: five phases `P0`–`P4`, an exact freeze instant,
last-transaction rules for eleven functions, nine checkpoints `C1`–`C9`, seven fallback triggers
`T1`–`T7`, a twelve-message communication schedule and rules `CV-01`…`CV-22`. Its register status is
◐ for the right reason:

> *"`DM-014` provides the cutover data checklist and freeze communication. The operational runbook —
> who does what, in what order, at what hour, with what abort points — does not exist."*

`DM-014` `CV-12` states where the runsheet comes from — generated from `DM-003` §4.4, never authored
independently — and then, correctly, stops. **A content file cannot staff a control room.**

This document is the operational half: **the command structure, the runsheet format and its worked
instance, the branch coordination model for 51+ sites, the evidence captured as the night proceeds,
and what happens when something goes wrong at 03:00.**

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The cutover command structure and its roles (§3) |
| 2 | The runsheet: format, generation, and a worked W1 instance (§4, §5) |
| 3 | Per-wave cutover profiles — how the four migration classes differ operationally (§6) |
| 4 | **The 51-branch coordination model** (§7) |
| 5 | The communication bridge and status cadence during the window (§8) |
| 6 | Evidence captured live, and how it reaches the pack (§9) |
| 7 | Checkpoint conduct — how a `C1`–`C9` decision is actually taken (§10) |
| 8 | The `P2` paper contingency as an operational responsibility (§11) |
| 9 | Post-cutover: catch-up, parallel run, hypercare handover, and the review (§12) |
| 10 | Rules `CUT-01`…`CUT-36` (§13) |

**Explicitly out of scope**

| Topic | Owned by |
|---|---|
| Phases, freeze instants, last-transaction rules, checkpoint **definitions**, trigger **definitions**, the communication **schedule** | **`DM-014`** — adopted whole under `MST-01` |
| The **wording** of branch and customer communications | `CM-012`, `CM-013` — **written 2026-08-20**, `Draft`, `P1`; their **Bengali counterparts do not exist** (§7.3) |
| Tier order and load dependencies | `DM-003` |
| Rollback **mechanics** and the fallback procedure | **`MG-007`** |
| Rehearsal and the durations this runsheet carries | **`MG-005`** |
| Reconciliation and sign-off | **`MG-004`** |
| Application deployment (code release) as distinct from data cutover | `RL-002` ⛔ — §2.3 states the seam |
| On-call rota and paging | `SV-004` ⛔ |
| Hypercare | `SV-005` ⛔ |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Cutover Manager** | The whole document; §4 is the instrument they run |
| **CTO / Programme Director** | §10 — the `C7` decision they jointly hold and cannot delegate |
| Domain owners | §10 `C6`; §9 what they must produce |
| **Branch managers (51+)** | §7 — what their site does, and when |
| Migration engineers | §4, §5 |
| Contact centre | §11.3 — the `P2` script problem |
| Support / hypercare | §12.3 |

---

## 2. Basis

### 2.1 Standards conformance

| Standard | Clause | Conformance | Departure |
|---|---|---|---|
| **ITIL 4** | Release Management; Deployment Management | §4 runsheet; §10 checkpoints; §12 post-deployment | ITIL treats deployment as repeatable and frequent. A wave cutover happens **once**, so §5's emphasis is on rehearsal-derived durations rather than on a mature pipeline's history |
| **ISO/IEC 20000-1:2018** | §8.5.1 change control; §8.5.3 release and deployment | Cutover is a change with a plan, a back-out and a post-implementation review | The back-out is `MG-007`; the review is §12.4 |
| **Incident Command System** role model | Single incident commander; defined command roles; span of control | §3 — one Cutover Manager, named deputies, explicit spans | ICS governs unplanned incidents. **A cutover is a planned operation with an incident-shaped failure mode**, which is why the role model transfers and the activation model does not |
| `DM-014` | `CV-01`…`CV-22`, `C1`…`C9`, `T1`…`T7` | Adopted unchanged | — |

### 2.2 Why an incident-command role model

A migration cutover has the two properties that make ICS the right shape: **many people, few of whom
report to each other normally**, and **a failure mode requiring an immediate, unambiguous decision**.

`DM-014` `CV-14` already gets the critical part right — *"a go decision taken by whoever is present
at 04:00 is how a known-bad load reaches production"*. §3 generalises it: **every role is named
before the freeze, every role has a deputy, and nobody holds two roles that check each other.**

### 2.3 The seam with `RL-002` deployment

| | Data cutover (**this document**) | Application deployment (`RL-002` ⛔) |
|---|---|---|
| Moves | Legacy data into the ERP | Code and configuration into an environment |
| Frequency | Nine times | Continuously, then per wave |
| Reversal | `MG-007` — tier reversal or restore | Pipeline rollback (`PE-004` ⛔) |
| Gate | `DM-014` `C7` | `RL-003` ⛔ readiness |

> **`CUT-01` — the application must be deployed, smoke-tested and stable *before* the freeze
> instant.** A cutover that deploys code and migrates data in the same window has two failure modes
> in one clock and cannot attribute a defect to either. `RL-002` is unwritten; **this rule is the
> interface it must honour**, and it is raised as `Q-01`.

---

## 3. The Cutover Command Structure

### 3.1 Roles

**`CUT-02`: every role is named, in writing, at `C2` (T−3 days), with a named deputy.** A role with
no name at `C2` is an unfilled role, and the cutover does not proceed to freeze.

| Role | Holder | Accountable for | May not also be |
|---|---|---|---|
| **Cutover Manager** | Data Migration Lead | The runsheet; the clock; declaring checkpoints; **declaring fallback when a trigger fires** | Load Operator; Reconciliation Reviewer |
| **Deputy Cutover Manager** | Migration Engineering Lead | Assuming command; **enforced handover at the §3.3 interval** | — |
| **Load Operator(s)** | Migration engineers | Executing runsheet steps | Reconciliation Reviewer or Approver (`RVP-02`) |
| **Reconciliation Reviewer** | QA Lead | Checking each `DM-013` report before it reaches the approver | Load Operator |
| **Domain Approvers** | CCO · CFO · Service Ops Director · Warehouse Manager · HR Director · Finance Director | Signing `RV-11` for their domain | — |
| **Business Readiness Lead** | Change Lead | Freeze confirmations from all eleven functions; branch readiness | — |
| **Branch Coordination Lead** | Branch Operations Lead | The 51+ sites; counting; van recalls | — |
| **Communications Officer** | Change / Comms | The §8 schedule; the bridge log | Cutover Manager |
| **Technical Standby** | Platform / DBA | Environment, database, restore capability | Load Operator |
| **Security Standby** | Security Lead | `CD-233` availability; residency pass 2; access anomalies | — |
| **Go/No-Go Authority** | **CTO with the Programme Director, jointly** | `C7` only. **Not delegable** (`CV-14`) | Any operational role |
| **Observer / Scribe** | PMO | The event log (§9.2); timing every step | Any operational role |

> **`CUT-03` — the Cutover Manager declares fallback; they do not decide it.** `MG-001` `MST-09`:
> the triggers are absolute and the go/no-go authority may not override them. The Cutover Manager's
> role at a trigger is to **recognise and declare**, immediately, and then execute `MG-007`.

### 3.2 Span of control

**`CUT-04`: no role directs more than seven others.** At W2 and W3, 51+ sites cannot report to one
person; §7.2 defines the zone layer that keeps the span within bounds.

### 3.3 Fatigue and handover

**A W1 cutover window plus rollback contingency exceeds a single shift, and every wave except the
D-class ones will run overnight.**

| # | Rule |
|---|---|
| `CUT-05` | Every role has a **named deputy briefed to the same standard**, not a name on a list |
| `CUT-06` | **A mandatory command handover occurs at a declared interval** — measured from the `MG-005` `R3` duration, and never longer than 8 hours on shift. The handover is a runsheet step with its own checklist, not a conversation |
| `CUT-07` | **The Go/No-Go Authority is not on shift**; they are called for `C7`. Two named people who have been awake for eighteen hours are not an independent authority |
| `CUT-08` | Domain approvers are **scheduled to a time window** derived from the `R3` measurement, not "on call all night". `MG-004` §11.2's 03:00 problem is solved by scheduling, not by stamina |

---

## 4. The Runsheet

### 4.1 Generation, not authoring

**`CUT-09`: the runsheet is generated from `DM-003` §4.4 and `MG-005`'s measurements.** `DM-014`
`CV-12` and `DM-003` `SQ-18` both require it: a runsheet step with no tier in the sequencing plan is
a breach of the plan, not an addition to it.

```
   DM-003 §4.4  ──►  MG-003 run plan  ──►  runsheet skeleton (steps, tiers, predecessors)
                                                    │
   MG-005 R3 measurements  ─────────────────────────┤  durations, per step
                                                    │
   MG-007 procedures  ──────────────────────────────┤  rollback_step, rollback duration
                                                    │
   MG-004 schedule  ────────────────────────────────┤  reconciliation and sign-off steps
                                                    │
   DM-014 §4.4, §4.10  ────────────────────────────►│  freeze confirmations, comms points
                                                    ▼
                                            THE CUTOVER RUNSHEET
```

### 4.2 Columns

Adopted from `DM-014` §4.5 with five operational columns added. The `DM-014` set is unchanged.

| Column | Source | Added here? |
|---|---|:--:|
| `step_no`, `phase`, `tier`, `activity`, `owner_role` | `DM-014` §4.5 | — |
| `planned_start`, `planned_duration` | `DM-014`; **from `MG-005` measurement** | — |
| `predecessor`, `checkpoint`, `rollback_step`, `evidence` | `DM-014` §4.5 | — |
| `actual_start`, `actual_end`, `status` | `DM-014` §4.5 | — |
| **`deputy_role`** | Who executes if the owner is unavailable | ✔ |
| **`verification`** | How the step is *proven* done, not just marked done | ✔ |
| **`comms_trigger`** | The §8 message this step releases, if any | ✔ |
| **`ponr`** | Whether this step crosses the point of no return (`MG-007` §5) | ✔ |
| **`abort_action`** | What happens if this step fails: retry · skip · **fallback** | ✔ |

> **`CUT-10` — every step has a `verification`, and "the operator said it finished" is not one.**
> A load step is verified by its row count and `ctl_run` outcome; a freeze step by the named
> function's confirmation; a count step by a signed count sheet. A step without a verification is
> a step that can be reported complete when it is not.

> **`CUT-11` — every step has an `abort_action` decided in advance.** At 03:00 the question *"do we
> retry or fall back?"* must already be answered on the sheet. `DM-014`'s triggers `T1`–`T7` are
> automatic; `abort_action` covers everything below trigger level.

### 4.3 Conduct

| # | Rule |
|---|---|
| `CUT-12` | The runsheet is the **single source of truth for the night**. A step not on it is not performed; if it must be, it is added, numbered and logged before execution |
| `CUT-13` | `actual_start` and `actual_end` are recorded **as they happen**, by the Scribe, not reconstructed afterwards |
| `CUT-14` | The Cutover Manager announces each step start and end on the bridge (§8.2) |
| `CUT-15` | **A step that overruns its planned duration by more than a declared threshold is escalated immediately**, not at the next checkpoint. The window is cumulative and the overrun is only recoverable early |
| `CUT-16` | Parallel steps share an explicit predecessor and obey `SQ-07`; **parallelism not proven at `R3` is not attempted in production** |

---

## 5. A Worked Runsheet — Wave 1

### 5.1 Read this before reading the table

**Every duration below is `[R3]` — to be filled from the `MG-005` timed dress rehearsal.**

This is not an omission. `DM-014` `CV-13` states it exactly: *"a runsheet whose durations are
estimates has not been rehearsed."* `MG-003` `ETR-49` and `MG-005` `DRH-13` both forbid publishing an
unmeasured duration. **A runsheet issued with plausible invented numbers is the specific artefact
that causes a cutover to discover at 04:00 that its window closed at 02:00.**

The structure, sequence, owners, verifications, evidence, PONR position and abort actions **are**
specified, and they are the parts that cannot be measured.

### 5.2 W1 — Foundation and service core

Derived from `DM-003` §4.4 W1, `DM-014` §4.2 W1 (*Dhaka HQ + 5 pilot centres, one weekend*), and
`MG-004` §5.1.

| # | Phase | Tier | Activity | Owner | Dur | Pred | Verification | Chk | PONR | Abort |
|--:|:--:|:--:|---|---|:--:|:--:|---|:--:|:--:|---|
| 1 | P1 | — | Application deployed, smoke-tested, stable (`CUT-01`) | Technical Standby | `[R3]` | — | Smoke suite green | — | — | Halt |
| 2 | P1 | — | Confirm rehearsal exit criteria met; publish rollback duration | Cutover Mgr | `[R3]` | 1 | `MG-005` report filed | **C1** | — | Halt |
| 3 | P1 | — | Branch/site readiness confirmations from all 6 W1 sites | Business Readiness | `[R3]` | — | Written confirmation per site | **C2** | — | Halt |
| 4 | P1 | — | Confirm `CD-233` live and resident store verified | Security Standby | `[R3]` | 1 | Verification record | — | — | **Defer S3 pass 2** |
| 5 | P1 | — | Confirm control totals registered and frozen | Recon Reviewer | `[R3]` | — | `MG-004` control register | — | — | Halt |
| 6 | **P2** | — | **FREEZE INSTANT** — publish, Bengali + English | Comms Officer | 0 | 3 | Message sent, receipt logged | — | — | — |
| 7 | P2 | — | Function stop confirmations — 11 functions × 6 sites | Business Readiness | `[R3]` | 6 | Each function's named confirmation + last number | **C3** | — | Halt |
| 8 | P2 | — | Record last legacy job numbers, invoice numbers per sequence | Business Readiness | `[R3]` | 7 | Recorded numbers | — | — | Halt |
| 9 | P2 | — | Final delta extract: `SRC-001`, `SRC-002`, `SRC-003` | Load Operator | `[R3]` | 7 | Manifest + hash verified | — | — | Retry ×2 → fallback |
| 10 | P2 | — | Final collection: `SRC-005`, `SRC-008`, `SRC-009`, `SRC-011`, `SRC-012` | Load Operator | `[R3]` | 7 | Manifest per file; origin recorded | — | — | Retry → fallback |
| 11 | P2 | — | Z1→Z2 parse; encoding normalise; manifest reconcile | Load Operator | `[R3]` | 9,10 | Z2 counts = manifest counts | **C4** | — | Retry → fallback |
| 12 | P2 | — | Z2→Z3 cleanse, match, survive | Load Operator | `[R3]` | 11 | `E7`/`E8` counts within declared band | — | — | Retry → fallback |
| 13 | P2 | — | Z3→Z4 conform; Z4→Z5 payload build with external IDs | Load Operator | `[R3]` | 12 | Payload count reconciles | — | — | Retry → fallback |
| 14 | P2 | `X0` | Load batch register, source register, legacy-ID xref | Load Operator | `[R3]` | 13 | `ctl_batch` open; `ctl_xref` populated | — | — | Retry |
| 15 | P2 | `X1` | **Load parties** — customers, corporate, employees-as-parties, brand partners | Load Operator | `[R3]` | 14 | Row count + `ctl_run` success | — | **▲ PONR** | **Fallback** |
| 16 | P2 | `X1` | Load addresses — **`zone_code` computed, not supplied** (`SQ-04`) | Load Operator | `[R3]` | 15 | Zone computed on 100% | — | ▲ | Fallback |
| 17 | P2 | `X2` | Load customer profiles, segments, corporate hierarchy | Load Operator | `[R3]` | 15 | Row count | — | ▲ | Fallback |
| 18 | P2 | `X2` | Load identity records — **`S3` fields deferred** (`SQ-10`) | Load Operator | `[R3]` | 17 | `resident_key` null on 100% | — | ▲ | Fallback |
| 19 | P2 | `X3` | Load devices and asset identifiers | Load Operator | `[R3]` | 16 | Row count; confidence split reported | — | ▲ | Fallback |
| 20 | P2 | `X3` | Load asset ownership and corporate estates | Load Operator | `[R3]` | 19 | Row count | — | ▲ | Fallback |
| 21 | P2 | `X5` | Load open and recent service orders | Load Operator | `[R3]` | 15,19 | Row count; archive flagged separately | — | ▲ | Fallback |
| 22 | P2 | `X0` | Load portal identities — **forced re-auth, no password carried** | Load Operator | `[R3]` | 15 | Zero password values present | — | ▲ | Fallback |
| 23 | P2 | — | **Residency pass 2** through `CD-233` (`ETR-19`) | Security Standby | `[R3]` | 18, 4 | `resident_key` set; access log written | — | ▲ | **Hold, not fallback** |
| 24 | P2 | — | Reconcile `R1`–`R4`, per tier | Recon Reviewer | `[R3]` | 21,23 | `DM-013` report §2–5 per tier | **C5** | ▲ | See `T1`, `T2` |
| 25 | P2 | — | **`R5` sample draw (149 party, 149 asset) + owner inspection** | CCO, Svc Ops Dir | `[R3]` | 24 | Inspection record; Bengali render check | — | ▲ | **`T3` on any defect** |
| 26 | P2 | — | Domain sign-offs — `RV-11` forms | Domain Approvers | `[R3]` | 25 | Signed forms | **C6** | ▲ | **`T5` on refusal** |
| 27 | P2 | — | Assemble and hash the evidence pack | Recon Reviewer | `[R3]` | 26 | Pack manifest hash | — | ▲ | — |
| 28 | P2 | — | Smoke test: create an order, look up a migrated customer, verify a legacy reference resolves | Business Readiness | `[R3]` | 26 | Scripted result set | — | ▲ | Fallback |
| 29 | **P2** | — | **GO / NO-GO** | **CTO + Programme Director** | `[R3]` | 27,28 | Decision recorded with instant and evidence | **C7** | ▲ | Fallback |
| 30 | P3 | — | Release to users; publish start message, Bengali + English | Comms Officer | `[R3]` | 29 | Message sent | — | — | — |
| 31 | P3 | — | **`P2` paper catch-up batch keyed** (`CV-11`) | Business Readiness | `[R3]` | 30 | Every paper form accounted for | — | — | — |
| 32 | P3 | `X9` | Archive load — service history, legacy tracker extracts | Load Operator | `[R3]` | 29 | Retrievability sample passes | — | — | Retry (off critical path) |
| 33 | P3 | — | Parallel run begins; daily comparison starts | Cutover Mgr | — | 30 | Day-1 comparison produced | — | — | — |
| 34 | P4 | — | Parallel-run exit; legacy withdrawal confirmed for W1 sites | Programme Director | — | 33 | Every W1 legacy practice confirmed stopped | **C8/C9** | — | — |

> **Step 15 is the point of no return for W1.** Everything before it is reversible by dropping
> staging tables (`ETR-10`); from step 15 the target holds migrated records. `MG-007` §5 analyses
> what "reversible" means after it, and why the answer changes again at step 23.

> **Step 23 is a hold, not a fallback.** If `CD-233` is unavailable, `SQ-10` and `ETR-21` hold the
> `S3` fields on the residency queue. **The cutover proceeds without them.** This is deliberate: the
> alternative — falling back an entire wave because a residency service is down — is worse than
> operating without NID data for a period.

---

## 6. Per-Wave Cutover Profiles

Each migration class (`MG-001` §4.3) changes the runbook's shape, not just its content.

| | **W1 (A — volume)** | **W2 (B — physical)** | **W3 (C — statutory)** | **W5 (B+C)** |
|---|---|---|---|---|
| Sites in scope | 6 | **All Dhaka centres** | **All Dhaka + Chittagong** | **All 51+** |
| Freeze driver | Load + reconcile duration | **Counting capacity** | **Period end** | Payroll period; assessment year (`Q-01`, `MG-001`) |
| Dominant risk | The window arithmetic is unrun | A branch does not count, or counts wrongly | A T-EXACT control does not tie | **YTD exactness; `never_reload`** |
| Command emphasis | Load operations | **Branch coordination (§7)** | Finance approvals and external verification | HR + finance jointly; 100% verification |
| Longest human step | `R5` inspection ×2 domains | **51+ count completions** | Auditor-agreed TB confirmation | **500+ employee YTD verification** |
| Extra roles | — | Zone Coordinators (§7.2) | Financial Controller on shift; auditor reachable | HR Manager on shift |
| Distinctive abort | — | `T7` — counts incomplete at more than the declared number of sites | `T2`, `T6` — control does not tie; Mushak sequence unassertable | `T2` on YTD |
| Post-go critical | Archive load | Van stock daily reconciliation (`G2-07`) | **One full parallel month-end close** | First payroll run (`G5-01`) |

> **`CUT-17`.** The profile is declared and its extra roles filled **before `C2`**. A W2 cutover run
> with a W1 command structure has no zone layer and violates `CUT-04` on the night.

---

## 7. The 51-Branch Coordination Model

### 7.1 The problem, stated as `DM-014` states it

> *"The largest cutovers in this programme — W2 stock and W3 cash — require simultaneous physical
> work at more sites than the programme has migration staff."*

`DM-014` §4.9 lists six constraints and their consequences. **What it does not provide is the
command structure that makes 51 sites reportable to one runsheet.**

### 7.2 The zone layer

**`CUT-18`: sites are grouped into zones; each zone has a named Zone Coordinator; the Branch
Coordination Lead directs zones, never sites.** This keeps every span within `CUT-04`.

| Layer | Count | Reports to | Accountable for |
|---|---:|---|---|
| Branch Coordination Lead | 1 | Cutover Manager | All zones |
| **Zone Coordinator** | **6–8** | Branch Coordination Lead | 6–9 sites each |
| Branch Manager | 51+ | Zone Coordinator | Their site's count, confirmations and sign-offs |
| Counters | 2+ per site | Branch Manager | The count itself; two counters plus the manager sign (`CV-10`) |

### 7.3 Sequencing 51 sites

| # | Rule |
|---|---|
| `CUT-19` | Counting is **sequenced by zone**, not attempted simultaneously everywhere, and the sequence is derived from the `MG-005` §7.3 **count-throughput figure per site size band** |
| `CUT-20` | **Van recall is sequenced by zone** so that field service degrades in one zone at a time, never nationally (`DM-007` `O-06`) |
| `CUT-21` | A zone's count window is closed by the Zone Coordinator confirming **every site** in the zone, not by the clock reaching a time |
| `CUT-22` | **A site that has not confirmed is a hole in the opening position** and is escalated at once — `DM-014` §4.9. `T7` fires when incomplete sites exceed the declared number |
| `CUT-23` | Every instruction reaching branch staff is **Bengali-first** (`CV-09`), and the Zone Coordinator confirms comprehension, not receipt |

> **`CUT-23` has no owning content today.** `DM-014` `O-04` and `AUDIT-011` `DM-08` both record it:
> **`CM-012` and `CM-013` now exist** — written **2026-08-20**, after the 2026-08-18 enumeration on
> which `DM-014` `O-04` and `AUDIT-011` `DM-08` both rest. Those two findings' absence claims have
> decayed and are superseded by this paragraph. Re-enumerated for this issue: Category 16 holds
> **18 `CM` files** and Category 17 holds **16 `OP` files**.
>
> **The dependency is not discharged, and the reason has moved.** `CM-012` declares
> `bilingual: yes` and names `CM-012_Branch_Readiness_Communication_Checklist_BN.md` as its
> counterpart. **That file does not exist**, and neither do **15 other declared `BN` counterparts
> across `CM` and `OP`** — including `OP-014`'s, which is the fallback procedure set 51 branches
> would work from during a rollback (`MG-007` §8). Counted 2026-08-19 09:10 (+06).
>
> `CM-012` is also registered **`P1`**, against a **`P0`** cutover that cannot proceed without it.
> **`CV-09` and `CUT-23` therefore remain unenforceable** — not for want of a file, but for want of
> its translation and its priority. Raised as `Q-03` and as audit finding `MGA-06`.

### 7.4 What a branch is actually asked to do

Stated plainly, because the request is larger than "confirm you have stopped".

| Wave | The branch's tasks |
|:--:|---|
| W1 | Stop at the instant; confirm last job number; move to the paper intake pad |
| **W2** | **Close for the count; count all stock with two counters; recall and count vans; confirm consignment; photograph and preserve the workshop whiteboard; sign the count sheets** |
| **W3** | **Witnessed cash count; seal the drawer; count cheque stock; record the last invoice number per sequence** |
| **W5** | **Physical asset and test-equipment verification; agree leave balances with every employee** |

---

## 8. Communications During the Window

### 8.1 The schedule is `DM-014`'s

`DM-014` §4.10 owns the twelve-message schedule and `CV-21` owns which four require confirmation.
Adopted unchanged.

### 8.2 The bridge

**`CUT-24`: a single communication bridge runs from freeze to go, with a logged join list.**

| # | Rule |
|---|---|
| `CUT-25` | The Cutover Manager announces every step start and end on the bridge (`CUT-14`) |
| `CUT-26` | **A status update goes out on a fixed cadence** — derived from `R3`, typically hourly — **including when nothing has changed.** Silence on a cutover bridge is read as failure, and people start making their own decisions |
| `CUT-27` | The Scribe logs every bridge decision with its instant, its decider and its basis (`CV-22`) |
| `CUT-28` | **Fallback declaration is announced on the bridge in plain words**, in one sentence, and repeated. It is not implied by a technical discussion |

### 8.3 Who must be reachable and who must be present

| Role | Present on the bridge | Reachable within |
|---|:--:|---|
| Cutover Manager, Load Operators, Recon Reviewer, Scribe | ✔ Throughout | — |
| Branch Coordination Lead, Zone Coordinators | ✔ During physical phases | — |
| Domain Approvers | Scheduled window (`CUT-08`) | 30 minutes |
| **Go/No-Go Authority** | **Called for `C7`** (`CUT-07`) | **1 hour, guaranteed** |
| Technical Standby, Security Standby | ✔ Throughout | — |
| External auditor (W3), tax consultant (W3/W4) | ✘ | **Agreed in advance** (`RVP-27`) |
| Contact centre supervisor | ✔ During `P2` | — |

---

## 9. Evidence Captured Live

### 9.1 Why live

`MG-004` §6 defines the evidence pack. **Much of it can only be captured while the cutover is
happening**, and reconstruction afterwards produces an account, not evidence.

| Evidence | Captured at | By |
|---|---|---|
| Last legacy numbers per function and sequence | Step 8 | Business Readiness |
| Function stop confirmations | Step 7 | Business Readiness |
| Count sheets, signed and witnessed | During the count | Branch Manager + 2 counters |
| Whiteboard/WIP photographs | At freeze | Workshop supervisor |
| Extract manifests and hashes | Steps 9–10 | Load Operator |
| `ctl_run` records with actual timings | Every load step | The harness |
| `R5` sample list, inspector, findings | Step 25 | Reconciliation Reviewer |
| Signed `RV-11` forms | Step 26 | Domain Approvers |
| **Checkpoint decisions with instant, decider and basis** | `C1`–`C9` | Scribe (`CV-22`) |
| Bridge log | Throughout | Scribe |
| Smoke test results | Step 28 | Business Readiness |

### 9.2 The event log

**`CUT-29`: the Scribe keeps a single chronological event log for the whole window**, and it is an
evidence-pack item. It records step transitions, decisions, deviations, escalations and anything
that surprised anyone.

> The event log is what makes the `MG-005`/§12.4 improvement loop work. **W1 has six sites and W5
> has 51+**; `DM-014` §6 states the requirement plainly — *"the plan must get better, not just
> repeat"* — and it cannot get better from a memory of the night.

---

## 10. Checkpoint Conduct

### 10.1 How a checkpoint is actually taken

`DM-014` §4.6 defines the nine checkpoints and their criteria. **`CUT-30` defines the conduct**, so
that a checkpoint is an event rather than a moment someone decides has passed.

| # | Step |
|:--:|---|
| 1 | The Cutover Manager **calls the checkpoint on the bridge**, by name |
| 2 | The named decider(s) state each criterion and whether it is **met, not met, or met with a stated exception** |
| 3 | Evidence for each criterion is **named**, not summarised |
| 4 | The decision is stated in one sentence: **proceed · proceed with reduced scope · hold · fall back** |
| 5 | The Scribe records decision, decider, instant and basis (`CV-22`) |
| 6 | The decision is announced to the bridge |

### 10.2 `C7` specifically

| # | Rule |
|---|---|
| `CUT-31` | `C7` is taken by the **CTO and the Programme Director jointly and is not delegable** (`CV-14`). If either is unavailable, `C7` **does not happen** and the cutover holds |
| `CUT-32` | `C7`'s criteria include **"fallback still executable inside the remaining window"** (`DM-014` `C7`), computed live against the published rollback duration (`MG-005` `DRH-25`). If it is not, **`T4` has already fired** |
| `CUT-33` | A `C7` decision is recorded with the **evidence pack manifest hash** it was taken against |

> **`CUT-32` is the operational form of the `T4` trigger that `AUDIT-011` says cannot be
> evaluated.** With `MG-005` supplying a measured rollback duration and the Scribe supplying an
> actual clock, it becomes a subtraction. Without `MG-005`, `C7` is taken on an unevaluable
> criterion — which is the current position.

---

## 11. The `P2` Paper Contingency

### 11.1 Emergency work does not stop

`DM-014` `CV-11`: a device that must be repaired during `P2` is repaired; what changes is that it is
recorded on a numbered paper form and keyed as a catch-up batch immediately after go.

**`CUT-34`: the paper contingency is a staffed operational responsibility with named owners per
function, per site**, not an instruction in a document.

| Function | Contingency artefact | Owner |
|---|---|---|
| Front desk / intake | Pre-numbered paper intake pad, from the reserved sequence block (`SH-10`) | Branch Manager |
| Workshop | Paper job card; whiteboard preserved | Supervisor |
| Field / dispatch | Paper visit forms | Dispatcher |
| Store | **Numbered manual issue voucher** | Storekeeper |
| Cash | Manual receipt; sealed drawer | Cashier |
| Invoicing | **Emergency invoice pad only**; last number recorded | Financial Controller |
| Procurement | Paper GRN pad | Procurement Manager |

### 11.2 The forms do not exist

`DM-014` `O-06` records it: *"the paper contingency has no forms. `DT` templates exist for live
documents, not for `P2` contingency."*

**Verified rather than repeated, 2026-08-19 09:15 (+06).** Category 05 `DT` holds the live-document
templates the freeze replaces — `DT-002` service intake receipt, `DT-024` goods receipt note,
`DT-029` physical count and stock adjustment sheet. A search across all `DT` files for *paper
intake*, *manual voucher*, *emergency pad* and *contingency pad* returns **zero matches**.
**`DM-014` `O-06` stands, and it is the one open item in this category whose absence is felt at
every one of the nine cutovers.** It is a W1-minus-1-month deliverable with no owner, raised as
`Q-04`.

### 11.3 The contact centre cannot look anything up

`DM-014` `O-07`: for the duration of `P2` the hotline cannot look up a job status, and 250,000+
monthly customers are unaware there is a window.

| # | Requirement |
|:--:|---|
| 1 | A **holding-response script**, Bengali and English, agreed before `C2` |
| 2 | A **call-back list** maintained through `P2` and worked immediately after go |
| 3 | The contact-centre supervisor **on the bridge** through `P2` (§8.3) |
| 4 | A **`P2` duration commitment** the contact centre can state to a caller |

> Requirement 4 is the one that turns `CV-02` — *"every hour of `P2` is an hour of paper"* — into a
> customer-facing commitment, and it is the reason `P2` minimisation is an operational objective
> rather than an engineering preference.

---

## 12. After the Window

### 12.1 Catch-up

**The `P2` paper batch is keyed before normal operation resumes** (`CV-11`, runsheet step 31), as a
runsheet step with its own verification: every numbered form accounted for, none skipped.

### 12.2 The parallel run

| Element | Owner |
|---|---|
| Declared primacy — **the new system is the system of record from the go decision** | Cutover Manager announces at step 30 |
| Daily comparison on the declared measures | `MG-004` §5.3 |
| Divergence reporting to the Change Lead | Business Readiness Lead |
| Finance: **one full parallel month-end close**, reconciled line by line and signed | CFO |
| Exit at `C8` — **a parallel run allowed to lapse has not been exited** (`CV-19`) | CFO for finance; CTO otherwise |

### 12.3 Handover to support

**`CUT-35`: the cutover formally ends with a handover to support**, not with the go decision.

| Handed over | To |
|---|---|
| Open exceptions `E3`, `E4`, `E6`, `E7`, `E8` with owners and dates | Domain owners; stewardship queues |
| The residency hold queue | Security Lead with the domain owner |
| Known defects and workarounds | Hypercare (`SV-005` ⛔) |
| The legacy-reference lookup path for customer enquiries | Contact centre |
| The parallel-run comparison duty | Business Readiness Lead |

> `SV-005` (hypercare) and `SV-004` (on-call and paging) are both ⛔ in `PGD-000` and Category 11
> holds **no documents on disk** — re-enumerated 2026-08-19 09:10 (+06). `AUDIT-017`'s conclusion —
> *"the programme has operational content and no operational capability"* — lands here precisely:
> the **content** now exists (Category 17 holds **16 `OP` files**, written 2026-08-20, including
> `OP-002` Hypercare Plan and Exit Criteria), and the **capability** does not. `OP-002` tells the
> handover what good looks like; it does not staff it. **There is currently nobody defined to hand
> over to.** Raised as `Q-05`.

### 12.4 The post-cutover review

**`CUT-36`: a post-cutover review is held within five working days of every cutover**, whether it
succeeded or not.

| Input | Output |
|---|---|
| The event log (§9.2) | What actually happened |
| Planned versus actual durations, per step | **The next wave's runsheet baseline** |
| `D1`–`D5` defects encountered | Fixes and re-rehearsal needs |
| Branch and function feedback | Instruction and training changes |
| Exception profile versus the rehearsal forecast | Queue sizing for the next wave |

> `DM-014` §6 requires the improvement loop; `CV-17` requires a written post-mortem within five
> working days **of a fallback**. `CUT-36` extends it to every cutover, because W1 has six sites and
> W5 has fifty-one, and the only way the plan improves is if the successful nights are examined too.

---

## 13. Governing Rules

> Class: **H** hard block · **A** approved override · **S** soft warning · **C** computed.

| # | Rule | Class |
|---|---|:--:|
| `CUT-01` | The application is deployed, smoke-tested and stable before the freeze instant | **H** |
| `CUT-02` | Every role is named in writing at `C2`, with a deputy | **H** |
| `CUT-03` | The Cutover Manager declares fallback on a trigger; they do not decide it | **H** |
| `CUT-04` | No role directs more than seven others | **H** |
| `CUT-05` | Every deputy is briefed to the same standard as the principal | **H** |
| `CUT-06` | A mandatory command handover occurs at a declared interval, as a runsheet step | **H** |
| `CUT-07` | The Go/No-Go Authority is not on shift; they are called for `C7` | **H** |
| `CUT-08` | Domain approvers are scheduled to a measured time window | **H** |
| `CUT-09` | The runsheet is generated from `DM-003` §4.4 and `MG-005` measurements | **H** |
| `CUT-10` | Every step has a verification; an operator's word is not one | **H** |
| `CUT-11` | Every step has an abort action decided in advance | **H** |
| `CUT-12` | The runsheet is the single source of truth; additions are numbered and logged first | **H** |
| `CUT-13` | Actual times are recorded as they happen, by the Scribe | **H** |
| `CUT-14` | Every step start and end is announced on the bridge | **H** |
| `CUT-15` | An overrun beyond the declared threshold escalates immediately | **H** |
| `CUT-16` | Parallelism not proven at `R3` is not attempted in production | **H** |
| `CUT-17` | The wave's cutover profile and its extra roles are declared before `C2` | **H** |
| `CUT-18` | Sites are grouped into zones; the Coordination Lead directs zones, not sites | **H** |
| `CUT-19` | Counting is sequenced by zone using the measured count-throughput figure | **H** |
| `CUT-20` | Van recall is sequenced by zone; field service degrades one zone at a time | **H** |
| `CUT-21` | A zone's window closes on every site confirming, not on the clock | **H** |
| `CUT-22` | An unconfirmed site is escalated at once; `T7` governs the threshold | **H** |
| `CUT-23` | Branch instructions are Bengali-first; the Zone Coordinator confirms comprehension | **H** |
| `CUT-24` | One communication bridge runs from freeze to go, with a logged join list | **H** |
| `CUT-25` | The Cutover Manager announces every step on the bridge | **H** |
| `CUT-26` | Status goes out on a fixed cadence, including when nothing has changed | **H** |
| `CUT-27` | Every bridge decision is logged with instant, decider and basis | **H** |
| `CUT-28` | Fallback is announced in plain words, in one sentence, and repeated | **H** |
| `CUT-29` | The Scribe keeps one chronological event log for the window | **H** |
| `CUT-30` | A checkpoint follows the six-step conduct, with evidence named | **H** |
| `CUT-31` | `C7` requires both named authorities; otherwise the cutover holds | **H** |
| `CUT-32` | `C7` computes fallback executability live against the published rollback duration | **H** |
| `CUT-33` | A `C7` decision records the evidence pack manifest hash | **H** |
| `CUT-34` | The paper contingency is staffed with named owners per function per site | **H** |
| `CUT-35` | The cutover ends with a handover to support, not with the go decision | **H** |
| `CUT-36` | A post-cutover review is held within five working days of every cutover | **H** |

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **`RL-002` is unwritten.** `CUT-01` requires deployment to complete before the freeze; the deployment plan that must honour it does not exist | CTO with the `RL-002` author | **W1 minus 2 months** | The W1 cutover shape |
| `Q-02` | **Who are the Zone Coordinators, and do 6–8 people with that authority exist?** `CUT-18` requires a layer the organisation does not currently have | Branch Operations Lead | **W2 minus 3 months** | W2, W3 and W5 cutovers |
| `Q-03` | **`CM-012` and `CM-013` exist but their declared Bengali counterparts do not**, and both are `P1` against a `P0` cutover. `CV-09`/`CUT-23` remain unenforceable. 16 declared `BN` counterparts are missing across `CM` and `OP` | Change Lead with Localisation Lead | **W1 — T−21** | Every branch communication; `MGA-06` |
| `Q-04` | **The `P2` paper contingency forms do not exist** (`DM-014` `O-06`) — numbered intake pads, issue vouchers, GRNs, visit forms, drawn from the reserved sequence block | Data Migration Lead with Content Design | **W1 minus 1 month** | `CUT-34`; `P2` at every wave |
| `Q-05` | **There is nobody to hand over to.** `SV-004` (on-call/paging) and `SV-005` (hypercare) are ⛔; `AUDIT-017` records no operational capability | Support Lead with CTO | **W1** | `CUT-35`; every go-live |
| `Q-06` | **What is the declared `P2` duration commitment the contact centre may state to customers?** §11.3 requirement 4 | Customer Service Manager with the Cutover Manager | **W1 minus 1 month** | The `P2` script; customer messaging |

---

## 15. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `MG-006-D-01` | Command model | Ad hoc · a RACI table · **an incident-command role model** | **ICS role model** | Many people who do not normally report to each other, plus a failure mode needing an immediate unambiguous decision | Named roles and deputies for every cutover, ×9 |
| `MG-006-D-02` | Runsheet durations at issue | Publish planned estimates · **publish `[R3]` placeholders** | **Placeholders** | `CV-13`, `ETR-49`, `DRH-13`. An invented duration is worse than a visible gap | The runsheet is unusable until `MG-005` runs — which is the true position |
| `MG-006-D-03` | Branch coordination | Direct to 51 sites · **a zone layer** | **Zone layer** | `CUT-04` span of control; the alternative is one person taking 51 phone calls | Requires 6–8 Zone Coordinators who do not currently exist (`Q-02`) |
| `MG-006-D-04` | `CD-233` unavailability at cutover | Fall back the wave · **hold the `S3` fields and proceed** | **Hold and proceed** | Falling back an entire wave for a deferred field set is disproportionate; `SQ-10` already sequences the hold | A residency backlog with an owner and a burn-down |
| `MG-006-D-05` | Post-cutover review scope | After a fallback only (`CV-17`) · **after every cutover** | **Every cutover** | W1 has 6 sites and W5 has 51+; only examining failures loses most of the learning | Nine reviews, each feeding the next runsheet |

---

## 16. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | A command structure exists with named roles, deputies and span limits | §3 |
| `AC-02` | The runsheet is generated, not authored, and its lineage is shown | §4.1 |
| `AC-03` | A complete worked W1 runsheet exists with owners, verifications, PONR and abort actions | §5.2 |
| `AC-04` | No unmeasured duration is published | §5.1; `MG-006-D-02` |
| `AC-05` | Per-wave profiles show how the four migration classes differ operationally | §6 |
| `AC-06` | A 51-site coordination model exists that respects span of control | §7 |
| `AC-07` | Evidence captured live is enumerated and mapped to the `MG-004` pack | §9 |
| `AC-08` | Checkpoint conduct is specified, including `C7`'s non-delegability and `T4` computation | §10 |
| `AC-09` | The `P2` contingency is a staffed responsibility, and its missing artefacts are named | §11; `Q-04` |
| `AC-10` | The cutover has a defined end, a handover and a review | §12 |
| `AC-11` | No `DM-014` rule is restated | Verified at issue (`MST-01`) |

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `DM-014` | Phases, instants, checkpoints, triggers, communication schedule — adopted whole |
| Upstream | `DM-003` §4.4 | The tier sequence the runsheet is generated from |
| Upstream | **`MG-005`** | **Every duration in the runsheet** |
| Upstream | `MG-003` | The run plan and the harness the steps execute |
| Upstream | `MG-004` | Reconciliation and sign-off steps; the evidence pack |
| Upstream | `MG-007` | `rollback_step` per runsheet row; the PONR analysis |
| Downstream | `GV-009` | Checkpoint and gate evidence |
| Downstream | `RL-002` ⛔, `RL-003` ⛔ | Deployment plan and readiness assessment must honour `CUT-01` |
| Downstream | `SV-004` ⛔, `SV-005` ⛔ | The handover target that does not yet exist |
| Downstream | `CM-012`, `CM-013` | Branch and customer communication content — written, `Draft`, **untranslated** (§7.3) |

---

## 18. References

**Within this repository**
[`MG-001`](MG-001_Data_Migration_Strategy.md) · [`MG-002`](MG-002_Legacy_System_Profiling_and_Extract_Specification.md) ·
[`MG-003`](MG-003_ETL_Design_and_Transformation_Rules_Specification.md) · [`MG-004`](MG-004_Reconciliation_and_Validation_Plan.md) ·
[`MG-005`](MG-005_Mock_Migration_and_Dress_Rehearsal_Plan.md) · [`MG-007`](MG-007_Rollback_and_Fallback_Plan.md)

**Workspace**
`../../project_content/12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md` ·
`../../project_content/12_Data_Migration_Content/DM-003_Entity_Migration_Priority_and_Sequencing_Plan.md` ·
`../../project_content/_AUDIT/AUDIT-011_Category_12_DM_Content_Audit.md` ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md` §6.5

**External standards**

| Source | Used for | Verified |
|---|---|---|
| ITIL 4 — Release Management, Deployment Management | §4, §10, §12 | 2026-08-18 |
| ISO/IEC 20000-1:2018 §8.5.1, §8.5.3 | Change control; release and deployment; back-out and PIR | 2026-08-18 |
| Incident Command System role model | §3 command structure | 2026-08-18 |

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Data Migration Lead with the Change Lead | Initial issue. Supplies the operational runbook `DM-014` explicitly does not carry: command structure, runsheet format and a worked W1 instance, per-wave profiles, the 51-site zone model, live evidence capture, checkpoint conduct and the post-cutover review | CTO with the Programme Director *(pending — `GV-001` `CC-01`)* |

---

*`MG-006` · Category 09 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
