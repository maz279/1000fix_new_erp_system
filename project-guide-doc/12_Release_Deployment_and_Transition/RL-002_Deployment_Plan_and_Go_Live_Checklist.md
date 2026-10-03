---
id: RL-002
title: Deployment Plan and Go-Live Checklist
category: 12 — Release, Deployment & Transition
code: RL
project: 1000FiX ERP System v2.0
version: 1.1
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Lead with the Release Manager
approver: Chief Technology Officer with the Programme Director
standards_basis: >
  ITIL 4 — Deployment Management (technical management practice) · ISO/IEC 20000-1:2018 + Amd
  1:2024 §8.5.3 release and deployment · 05-06 NFR-008 zero-downtime deployment and OPS-07
  forward-only reversible migrations · TSS §18.3 promotion gates · 02-02 §8 DoD-16 (rollback
  documented and rehearsed) · MG-006 CUT-01 deployment-before-freeze interface
traces_to: >
  PGD-000 RL-002 row (⛔, 06-06 unwritten) · MG-006 §2.3 and CUT-01, raised there as Q-01 ·
  MG-007 §4 rollback mechanisms · DM-014 C1…C9, T1…T7 · CM-006 G1…G7, GO-01…GO-14 ·
  QA-001 §7.1 (7 test environments, 0 provisioned) · TSS §18.3 (5 deployment targets) ·
  RL-001 RMP-25, RMP-26, RMP-28 · 06-02 §4 wave gates
depends_on: >
  RL-001 (issued) · MG-006 (issued) · MG-007 (issued) · QA-001 (issued) · QA-010 (issued) ·
  PE-001, PE-002, PE-003, PE-004, PE-005, PE-007, PE-008, PE-009 (all ISSUED 2026-08-19,
  concurrently with this document — see the audit corrections at §3.1 and §4.2) ·
  SV-001…SV-005 (ISSUED 2026-08-19) · SV-006 (ABSENT ◐) — every dependency below is now
  specified and none is implemented; see DPY-29
verified_on: 2026-08-19
enumeration_timestamp: 2026-08-19 02:10 (+06) — re-enumerated at audit after Category 10 was authored concurrently
rule_prefix: DPY — verified unused across all 777 markdown files of the workspace, re-verified at audit 2026-08-19 02:10 (+06)
priority: P0
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# RL-002 — Deployment Plan and Go-Live Checklist

### Category 12 · Code `RL` · Rule space `DPY` · ITIL 4 Deployment Management · ISO/IEC 20000-1:2018 + Amd 1:2024 §8.5.3

---

> **`PGD-000` records this document as ⛔ with the note:** *"`06-06` planned, never written. Nine
> waves each need one, and the first is needed before Wave 1 closes."*
>
> **`06-06_Deployment_and_Operations_Plan.md` is superseded by this document, not awaited.** It was
> planned as one file covering deployment *and* operations; those are Categories 12 and 11 and they
> have different owners. What follows is the deployment half.

---

## 1. Purpose

This document states **how code and configuration get into an environment, and how anyone knows it
worked**. It supplies the per-wave deployment sequence, the pre-flight checks, the smoke test, the
verification window, the communication points and — the part that decides whether a bad night ends
well — the **abort criteria and who may invoke them**.

It is the technical counterpart to `RL-001`. `RL-001` decides *whether and when* something becomes
available to users; this document moves the artefacts and proves the movement.

### 1.1 The one interface this document was written to honour

`MG-006` `CUT-01`, raised there as `Q-01` against an unwritten `RL-002`:

> *"The application must be deployed, smoke-tested and stable **before** the freeze instant. A
> cutover that deploys code and migrates data in the same window has two failure modes in one clock
> and cannot attribute a defect to either. `RL-002` is unwritten; **this rule is the interface it
> must honour**."*

**It is honoured.** `RL-001` `RMP-25`/`RMP-26` supply the dates; §7 of this document supplies the
smoke test that makes *"smoke-tested"* a measurable claim; §10 supplies the stability window that
makes *"stable"* one. `MG-006` `Q-01` is answered.

### 1.2 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | **The environment estate** — reconciling two disjoint enumerations into one promotion path (§3) |
| 2 | **Deployment models** and an honest statement of which the programme can execute today (§4) |
| 3 | **Database change** — the expand/contract protocol that `NFR-008` and `OPS-07` jointly require (§5) |
| 4 | **The deployment runsheet** — the generic sequence, distinct from `MG-006`'s cutover runsheet (§6) |
| 5 | **The smoke test** — scope, ownership, pass criteria, and what it is not (§7) |
| 6 | **The go-live checklist** — the artefact itself, 59 items across nine sections (§8) |
| 7 | **Abort** — criteria, authority, and the seam with `DM-014`'s fallback triggers (§9) |
| 8 | **Verification** — the 48-hour window and what is measured inside it (§10) |
| 9 | **Communication points** during a deployment, anchored to `CM-006` (§11) |
| 10 | **Per-wave deployment profiles**, all nine (§12) |
| 11 | **Emergency deployment** — the execution half of `RL-001` §9 (§13) |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Whether a release is authorised, and when it may not happen | `RL-001` | Release is a service management practice; deployment is a technical one |
| Whether the business is ready for a go-live | `RL-003` | Readiness is assessed; deployment is executed |
| Which branches receive it, in what order | `RL-004` | Site sequencing is a rollout problem |
| **Data** cutover: freeze, extract, transform, load, reconcile | `MG-006`, `DM-014` | §3.4 states the seam. This document never moves data |
| Data rollback mechanisms and points of no return | `MG-007` | §9.4 states the seam. Code rollback ≠ data rollback |
| Pipeline stages, runners, promotion automation, artefact repository | `PE-004` | Issued 2026-08-19. §3.2 draws the environment path across it; §4.2 adopts its per-component strategy |
| Environment classes, sizing, provisioning, IaC | `PE-002`, `PE-003` | Issued 2026-08-19. **`PE-002` §4.2's twelve environments govern**; §3.1 adopts them |
| Backup, restore and DR drill | `PE-007` | Issued 2026-08-19. Checklist item `R-02` consumes it |
| Alerting, dashboards, paging | `PE-008`, `SV-004` (both issued 2026-08-19) | §10.3 states the consequence for verification: **the designs exist and the capability does not** |
| Release note content and wording | `OP-006` | Publication is checklist item `X-05`; the content is not this document's |

### 1.3 Intended audience

| Audience | What they use this document for |
|---|---|
| Platform Lead | The whole document. This role executes it |
| Deployment engineer on the night | §6 runsheet, §7 smoke test, §8 checklist, §9 abort |
| Release Manager | §11 communication points; the interface with `RL-001` §8 authority |
| Data Migration Lead | §3.4 and §9.4 — the two seams with `MG-006`/`MG-007` |
| Cutover Commander (`MG-006` §3.1) | §9.3 — who may abort a deployment inside a cutover window |
| Support Lead | §10 verification; what is handed over and when |
| Wave-gate assessors | §12 per-wave profiles; deployment evidence for `GV-009` dimension D2 |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / practice | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ITIL 4 — Deployment Management** | Technical management practice: move new or changed components to live environments | §3 defines the environments, §4 the models, §6 the sequence, §9 the abort. The practice's separation from Release Management is `RL-001` §3 | **None** |
| **ISO/IEC 20000-1:2018 + Amd 1:2024** | §8.5.3 release and deployment management — plan, verify, and make available; record success and failure | §8's checklist is the plan; §7's smoke test is the verification; §10 records success or failure with evidence | Amd 1:2024 does not touch §8.5 |
| **`05-06` `NFR-008`** | Zero-downtime deployment for planned changes — **P1**, *"standard for all releases"* | §4.5 states plainly that **`NFR-008` cannot be met with the deployment estate as designed today**, and names exactly what would make it achievable | **Departure, declared.** §4.5 is the most important honest statement in this document |
| **`05-06` `OPS-07`** | Migrations are forward-only, tested against a production-sized dataset, and **reversible by a documented procedure** | §5 is that documented procedure, in the expand/contract form | None |
| **TSS §18.3** | Five deployment targets with named triggers and gates | §3.1 adopts all five and reconciles them with `QA-001`'s seven | The two sets were never reconciled. §3.1 does it |
| **`02-02` §8 `DoD-16`** | Rollback plan documented **and rehearsed** | Checklist item `P-23`; §9.5 makes the rehearsal a pre-flight gate rather than a promise | None |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| TSS §18.3 | `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` | `dev`, `staging`, `training`, `prod`, `dr` with their triggers and gates; the expand/contract sentence |
| `QA-001` §7.1 | `../08_Quality_Engineering_and_Test/` | Seven test environments, **0 of 7 provisioned**, counted 2026-08-18 22:01 (+06) |
| `05-06` `NFR-008`, `OPS-07` | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/` | Zero-downtime as a P1 NFR; forward-only reversible migrations |
| `MG-006` §2.3, `CUT-01`, §3.1, §5, §10 | `../09_Data_Migration_and_Cutover/` | The cutover/deployment seam; the incident-command role set; the worked W1 runsheet; checkpoint conduct |
| `MG-007` §4, §5, §7 | ″ | Four rollback mechanisms; three points of no return; the measured rollback duration |
| `DM-014` §4.6, §4.7 | `../../project_content/12_Data_Migration_Content/` | Checkpoints `C1`…`C9`; fallback triggers `T1`…`T7` |
| `CM-006` §4.1, §4.2, §4.7 | `../../project_content/16_Change_Management_and_Comms/` | Seven go-live assets `G1`…`G7`; `GO-01`…`GO-14`; the no-go, delayed-go, partial-go and fallback variants |
| `OP-002` §4.7 | `../../project_content/17_Operations_Support_and_Runbooks/` | The rollback decision table, authorities and `RB-01`…`RB-04` |
| `QA-010` §5.3 | `../08_Quality_Engineering_and_Test/` | `DMG-T1`…`DMG-T9` gate thresholds |
| `RL-001` §7.6 | `./RL-001_Release_Management_and_Versioning_Policy.md` | `RMP-25` T−15 wd, `RMP-26` T−25 wd, `RMP-28` deploy-disabled |
| `06-02` §4 | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/` | 70 wave-gate criteria across nine gates |

### 2.3 Register gaps and audit findings this document closes

| Finding | Source | How this document closes it |
|---|---|---|
| `RL-002` ⛔, *"`06-06` planned, never written"* | `PGD-000` | Superseded. This document is the deployment half; `SV-001`…`SV-006` are the operations half |
| `MG-006` `Q-01` | `MG-006` §2.3 | `CUT-01`'s interface is honoured: dates from `RL-001`, smoke test §7, stability window §10 |
| Two disjoint environment enumerations | This document, §3.1 | TSS §18.3's five and `QA-001` §7.1's seven are reconciled into **ten distinct environments** with one promotion path |
| `NFR-008` unachievable and unrecorded | This document, §4.5 | Stated, with the four absent documents that would make it achievable named |
| `OPS-07` has no documented procedure | This document, §5 | The expand/contract protocol, in six steps, with the two-release rule made enforceable |

### 2.4 The rule space

Rules carry the prefix **`DPY`**, verified at **zero** occurrences across all 754 markdown files of
the workspace before allocation. `RL-nn` is `TR-024`'s space (`RL-001` §2.4); `DPL-nn` was rejected
because it already occurs 85 times.

---

## 3. The Environment Estate

### 3.1 Two enumerations that have never been reconciled

This is the first thing a deployment plan must fix, because a promotion path cannot be drawn across
two lists that do not know about each other.

| Source | Environments named | Purpose of the list |
|---|---:|---|
| **TSS §18.3** | **5** — `dev`, `staging`, `training`, `prod`, `dr` | *Deployment targets*, with triggers and gates |
| **`QA-001` §7.1** | **7** — `DEV`, `CI`, `SIT`, `UAT`, `PERF`, `TRAIN`, `SANDBOX` | *Test environments*, with levels served and data class |

Counted from both source tables at **2026-08-18 23:27 (+06)**.

**The overlap is two.** `dev`≡`DEV` and `training`≡`TRAIN`. TSS names no `CI`, `SIT`, `UAT`, `PERF`
or `SANDBOX`; `QA-001` names no `staging`, `prod` or `dr`.

> **⚠ Corrected at audit, 2026-08-19 02:10 (+06) — finding `RLA-13`.** The v1.0 draft of this
> section ruled **ten** environments from the two lists above and stated that the table stood
> *"until `PE-002` issues and supersedes it."* **`PE-002` was issued on 2026-08-19, concurrently
> with the drafting of this document**, and it performs the same reconciliation from a different
> pair of source lists — `02-05` §9 / `AR-001` §8.5 (six) and `TS-001` §4.7 (six) — arriving at
> **twelve**. `PE-002` `PE-002-F-01` predicted this exact divergence in advance: *"`RL-002`'s
> release process will plan against list A."*
>
> **`PE-002`'s twelve govern.** The two additions this document's ten did not carry are `local`
> (developer workstation, `BE-001`) and `migration-staging` (production-class migration rehearsal
> at production volume, `MG-005`), and both are correct. The correction is recorded rather than
> made silently, because a promotion path that quietly changed size between two documents is
> exactly the divergence `PE-002-F-01` warns about.

> **`DPY-01`. The environment inventory is `PE-002` §4.2's twelve, adopted whole and not restated
> here.** This document owns the **promotion path** across them (§3.2) — which `PE-002` §4.1
> explicitly delegates — and nothing else about them.

| # | `PE-002` environment | Role in the promotion path | Deployment trigger | Gate |
|:--:|---|---|---|---|
| 1 | `local` | Off-path — developer workstation | Developer | — |
| 2 | `ci` | **On-path**, ephemeral per run | Per commit | — |
| 3 | `dev` | **On-path** | Automatic on merge to `develop` | CI green |
| 4 | `sit` | **On-path** | Per release candidate | CI green + contract suite |
| 5 | `uat` | **On-path**, frozen for the cycle | Manual, per wave | `sit` exit criteria met |
| 6 | `perf` | Off-path branch | Per wave gate | — |
| 7 | `staging` | **On-path** — release-candidate rehearsal | **Manual promotion** | CI green + integration suite |
| 8 | `training` | Off-path branch | Manual, per training cycle | Curated data load |
| 9 | `sandbox` | Off-path branch | Per release | `IN-008` §6 certification suite |
| 10 | `migration-staging` | Off-path branch | Per rehearsal (`MG-005`) | — |
| 11 | **`prod`** | **On-path terminus** | **Manual gate** | **Wave-gate acceptance + change approval + rollback rehearsed (`DoD-16`)** |
| 12 | `dr` | Off-path — receives by replication | Continuous replication | DR drill twice yearly |

**Provisioning status is `PE-002`'s to report, not this document's.** `QA-001` counted **0 of 7** at
2026-08-18 22:01 (+06); `PE-002` issued its specification on 2026-08-19. **A specification is not a
provisioned environment**, and `GV-009` `EN-06` still blocks any gate whose criteria require an
environment that does not exist at the required class.

### 3.2 The promotion path

`PE-002` §4.1 states that the promotion path is `PE-004`'s and `RL-002`'s. `PE-004` §3.2 supplies
the pipeline shape; this is the **environment** path across `PE-002`'s twelve. Read left to right;
every arrow is a gate.

```
  local ─► commit ─► ci ─► dev ─► sit ─► uat ──────────────────┐
                                   │                           │
                                   ├─► perf              (per wave gate)
                                   ├─► sandbox           (per release)
                                   └─► migration-staging (per MG-005 rehearsal)
                                                               ▼
      training ◄── curated load ◄──────────────────── staging ─► prod ─► dr
                                                                  (replication)
```

| # | Rule |
|---|---|
| **`DPY-02`** | **The on-path sequence is `ci` → `dev` → `sit` → `uat` → `staging` → `prod`.** No artefact reaches `prod` that has not passed through `staging`, and none reaches `staging` that has not passed `uat`. `local` is off-path by definition — nothing is promoted **from** a workstation |
| **`DPY-03`** | `perf`, `sandbox`, `training` and `migration-staging` are **branches off the path, not steps on it.** They receive the same artefact; they do not gate it — except that a `perf` failure at a wave gate blocks the wave release under `06-02` `G1-10` and `G9-03`, and a `migration-staging` rehearsal failure blocks the cutover under `DM-014` `C1` |
| **`DPY-04`** | **The artefact promoted is bit-identical at every step** — the same digest, not a rebuild. This is `PE-004` §3.1's build-once-and-promote rule, adopted by citation. Configuration differs; the artefact does not (`MTS-E3`: *"configuration is promoted, never hand-edited"*) |
| **`DPY-05`** | `dr` receives production by **replication**, never by deployment. A deployment to `dr` means `dr` has diverged, and the divergence is an incident |
| **`DPY-06`** | `training` is loaded from a **curated** data set on the training cycle, not on the release cycle. A training environment that changes under a cohort mid-course invalidates the course (`TR-003` `DS-14` screenshots) |

### 3.3 What this section assumes and cannot verify

> **`DPY-07`.** §3.1 and §3.2 are a **specification of what must exist**, not a description of what
> does. `PE-002` and `PE-003` were issued on 2026-08-19 and specify the environments and the
> infrastructure-as-code standard; **neither provisions anything.** This document names the
> promotion path so that `PE-002`'s inventory has a defined consumer; it cannot size, cost or build
> them. `GV-009` `EN-06` blocks a gate whose criteria require an environment that does not exist at
> the required class, and that block is unaffected by a specification issuing.

### 3.4 The seam with data cutover

| | **Deployment** (this document) | **Data cutover** (`MG-006`, `DM-014`) |
|---|---|---|
| Moves | Code and configuration into an environment | Legacy data into the ERP |
| Frequency | Continuously, then per wave | Nine times |
| Sequence | **Completes before** `P0` rehearsal begins (`RMP-25`) | `P0` → `P1` → `P2` → `P3` → `P4` |
| Verified by | Smoke test (§7) then the 48-hour window (§10) | `DM-013` reconciliation, `C5`/`C6` |
| Reversal | §9.6 — redeploy the prior tag | `MG-007` — tier reversal or full restore |
| Gate | §8 checklist + `RL-003` readiness | `DM-014` `C7` |
| Aborted by | §9.2 `DA-1`…`DA-8` | `DM-014` `T1`…`T7` |

> **`DPY-08` — a deployment and a data cutover never share a window.** This is `CUT-01` restated
> from the deployment side, and it is the reason §12's per-wave profiles all place the wave release
> at `RMP-25`'s T−15 working days rather than on cutover night.

---

## 4. Deployment Models

### 4.1 The four models

| Model | Mechanism | Downtime | Requires |
|---|---|---|---|
| **Recreate** | Stop, replace, start | **Full outage for the duration** | Nothing beyond a maintenance window |
| **Rolling** | Replace instances in batches | None, if the app tolerates mixed versions | Orchestration; ≥ 2 instances; backward-compatible schema |
| **Blue/green** | Two identical stacks; switch traffic | None; instant rollback by switching back | Double capacity; a traffic switch; shared-state discipline |
| **Canary** | Route a small share of traffic to the new version, widen on signal | None | Traffic splitting **and** per-version telemetry |

### 4.2 The model per component is `PE-004`'s, not this document's

> **⚠ Corrected at audit, 2026-08-19 02:10 (+06) — finding `RLA-14`.** The v1.0 draft of this
> section ruled that `Recreate` was *"the only executable deployment model"* because `PE-001`,
> `PE-004`, `PE-005` and `PE-008` were all ⛔ at the time of writing. **All four were issued on
> 2026-08-19**, concurrently with this document, and `PE-004` §8.1 assigns a strategy per component.
> The v1.0 ruling is withdrawn in full and replaced by adoption.

`PE-004` §8.1, adopted by citation and not restated in substance:

| Component | Strategy | Source |
|---|---|---|
| Odoo application nodes | **Rolling**, one node at a time, health-gated | `PE-004` §8.1; ≥ 2 nodes from W1 (`PE-001` §9.2) |
| Next.js portals | **Blue/green** | `PE-004` §8.1 |
| Domain services (16) | Rolling — stateless | `PE-004` §8.1 |
| **Odoo cron nodes** | **Stop, migrate, start** — a deliberate scheduler gap | `PE-004` §8.3 |
| Event consumers | Rolling, with schema compatibility verified first | `PE-004` §8.1; `IN-003` §6 |
| Kong / Nginx | Rolling across availability zones | `PE-004` §8.1; `PE-001` §6.2 |
| Database | Migration only | `PE-004` §7 |

### 4.3 The ruling, restated

> **`DPY-09`. The deployment strategy per component is `PE-004` §8.1's and is adopted whole. This
> document owns *when* a deployment happens, not *how* the artefacts move.** `PE-004` §8.5 states
> the same boundary from its side: *"The gate is a **business** gate, not a technical one.
> Everything technical has already been decided by the pipeline; what remains is **when**, and that
> is `RL-*`'s."*
>
> The consequence for everything below: §6's runsheet, §8's checklist and §9's abort criteria are
> written to be **strategy-independent**. A rolling deployment and a recreate deployment differ at
> runsheet steps 7–11 and nowhere else; the pre-flight, the smoke test, the abort triggers and the
> verification window are identical.

> **`DPY-09a`. The cron exception is the one case where `RL-001`'s freeze calendar and `PE-004`'s
> strategy interact.** `PE-004` §8.3 stops, migrates and starts Odoo cron nodes deliberately,
> because two concurrent schedulers means one job runs twice and `PE-004-F-03` records that
> **scheduled-job idempotency is unspecified estate-wide across 60 automations**. A scheduler gap
> during `F2` (period close), `F3` (payroll) or `F4` (statutory filing) is therefore not a
> two-minute inconvenience — it is a missed batch inside a freeze window. **Deployments touching
> cron nodes are scheduled outside those freezes**, which `RL-001` §7 already requires and this rule
> makes specific.

### 4.4 The deployment window, derived

Even a rolling or blue/green deployment has a **window** — the interval in which the estate is
running two versions, a cron gap exists (`PE-004` §8.3), and a rollback is still cheap. `RL-001`
`RMP-13`–`RMP-15` already constrain the day; these constraints fix the hour.

| Constraint | Source | Effect on the window |
|---|---|---|
| Branches operate during opening hours | `MD-003` `BRN-04` | The window is outside branch opening hours |
| Field technicians work in the app, offline-tolerant | `M02`, `TS-015` | Field is the *least* window-sensitive population — offline queues absorb a short outage |
| The contact centre (`P10`) runs to a published schedule | `M10`, W4+ | The window avoids contact-centre hours from W4 |
| Customers book and track 24/7 through `P01` | W2+ | **There is no hour with zero customer traffic.** The window minimises, never eliminates, customer impact |
| Two working days of observation must follow | `RL-001` `RMP-13` | Sunday, Monday or Tuesday |
| Integration partners have their own schedules | `IN-001`, bKash/Nagad settlement cycles | The window avoids declared settlement windows from W3 |

| # | Rule |
|---|---|
| **`DPY-10`** | The standard deployment window is **Sunday, Monday or Tuesday, 23:00–02:00 `Asia/Dhaka`**, declared at least 3 working days ahead through `OP-005`'s maintenance notice copy. Where the strategy is rolling or blue/green, the notice states **"brief interruption possible"** rather than an outage — and it is still issued, because `PE-004` §8.3's cron gap is real |
| **`DPY-11`** | **The window is a maximum, not an allowance.** A deployment that has not completed its smoke test by the window's end invokes §9.6 rollback, regardless of how close it is to finishing |
| **`DPY-12`** | From W2, the customer-facing status page (`OP-005`) shows the window before, during and after. A silent interruption on a portal used by 250,000+ customers a month is an incident even when it was planned |

### 4.5 `NFR-008` — four conditions, one of which is nobody's yet

> **⚠ Corrected at audit, 2026-08-19 02:10 (+06) — finding `RLA-14`.** The v1.0 draft stated that
> `NFR-008` (zero-downtime deployment, **P1**) *"is not achievable with the deployment estate as
> currently specified, and no document has said so."* **`PE-004` said so on 2026-08-19**, and said
> the opposite: `NFR-008` **is** achievable, under four stated conditions. The v1.0 finding is
> withdrawn; what follows is `PE-004` §8.2's position with this document's consequence attached.

`PE-004` §8.2 — `NFR-008` is achievable **only** when all four hold:

| # | Condition | Owner | Status |
|:--:|---|---|---|
| 1 | Forward-only, backward-compatible migrations | `PE-004` `PE-004-D-02`; §5 of this document | **Specified** |
| 2 | ≥ 2 instances of every component being rolled | `PE-001` `HA-01` | **Specified** |
| 3 | **Health checks that mean it** — a node is in service when it can *serve*, not when the process started | **Assigned to `PE-005` §6** by `PE-004-F-02` | **Assigned, unbuilt** |
| 4 | Connection draining — in-flight requests complete before a node stops | `PE-005` | **Specified** |

> **`DPY-13`. `NFR-008` is specified as achievable and is not yet achieved, and the gap is
> condition 3.** `PE-004-F-02` records it as *"where zero-downtime deployments usually fail"* — a
> readiness check returning healthy before database connections and caches are warm produces a
> rolling deployment that serves errors from every node in turn.
>
> **The consequence this document adds:** `NFR-008` is reported at every wave-gate as **specified,
> not demonstrated**, until a rolling deployment has been executed in `staging` and measured to
> produce zero failed requests. That measurement is checklist item `E-07` (§8.2) and it is a
> `RL-003` dimension `RD-2` evidence item. **`GA-06` applies: a zero-downtime claim from a
> deployment that was never measured for downtime is not a zero-downtime claim.** Raised as `Q-01`.

---

## 5. Database Change — The Expand/Contract Protocol

### 5.1 The requirement, from two documents that each state half of it

| Source | Statement |
|---|---|
| `05-06` `OPS-07` | *"Database migrations are forward-only, tested against a production-sized dataset, and **reversible by a documented procedure**"* |
| TSS §18.3 | *"A release adds a column before code uses it and removes a column only after no code references it — **two releases, never one**"* |
| **`PE-004` `PE-004-D-02`** *(issued 2026-08-19)* | Forward-only, backward-compatible migrations chosen over reversible down-migrations, *"because down-migrations that restore dropped data do not exist"*; **"a rename takes three releases"** |
| `PE-004` §7.3 `ME-01`…`ME-05` | Migrations run as a distinct pipeline step, once, under an advisory lock; failure **halts the deployment** and leaves the previous version serving |

> **Seam, recorded at audit.** `PE-004` §7 owns migration **execution** — where in the pipeline it
> runs, under what lock, and what happens on failure. **This section owns the migration's
> *shape*** — the phases a change is decomposed into so that `PE-004-D-02`'s forward-only guarantee
> is actually deliverable. The two were written independently on 2026-08-19 and **agree**:
> `PE-004-D-02` concludes *"a rename takes three releases"* and §5.2 below derives the same three,
> from `OPS-07` and TSS §18.3. That independent agreement is worth recording, because it is the
> only cross-check either document has.

`OPS-07` requires a documented procedure and names none. TSS states the pattern in one sentence and
gives no protocol. `PE-004` §7.3 states the execution rules and not the decomposition. **This
section is the procedure.**

### 5.2 The protocol

Every schema change that affects an existing column, table or constraint runs as **three releases**,
not two. TSS's *"two releases"* covers add-then-use; removal needs a third.

| Phase | Release | Schema action | Code action | Reversible by |
|:--:|---|---|---|---|
| **E — Expand** | `n` | Add the new column/table/index. **Nullable, defaulted, no constraint** | None. Code does not reference it | Dropping the addition; nothing depends on it |
| **M — Migrate** | `n` | Backfill in batches, restartable, outside the deployment window | Dual-write: write both old and new; read old | Stopping the backfill; both paths still work |
| **R — Read-switch** | `n+1` | None | Read new; continue writing both | Redeploying `n`; both paths still work |
| **C — Contract** | `n+2` | Drop the old column; add the constraint the new one needed | Write new only | **Nothing.** This is the irreversible step |

| # | Rule |
|---|---|
| **`DPY-14`** | **Expand, Migrate, Read-switch and Contract never occur in the same release.** A change that combines them is rejected at code review (`BE-003` §6) and at pre-flight (`P-09`) |
| **`DPY-15`** | **Contract may not run until the read-switch release has been live for one full wave-gate interval** — four to five months — or until a query of the source proves zero references, whichever is sooner. `GW-36`'s logic applies: an irreversible step taken early is not repaired by taking it again |
| **`DPY-16`** | The backfill is **batched, restartable and idempotent**, and it runs **outside** the maintenance window. A backfill inside the window converts a bounded outage into an unbounded one, and is the single most common cause of an overrun deployment |
| **`DPY-17`** | Every migration is tested against a **production-sized** dataset (`OPS-07`) on `perf` before it reaches `staging`. `perf` is ⛔-blocked (§3.1); until it exists, migration timing is an **estimate** and is recorded as one, per `MG-006` `CV-13`'s discipline of leaving unrehearsed durations marked |
| **`DPY-18`** | A migration that cannot be expressed in this protocol — a type change that loses precision, a primary-key change, a table split — is **not** a migration. It is a data migration and goes to `MG-003`, which has the tooling for it |

### 5.3 Why three releases and not two

TSS's sentence is correct and incomplete. *"Adds a column before code uses it"* is E→R. *"Removes a
column only after no code references it"* is C. Between them sits **M**, the backfill, and the
backfill is where the time and the risk are: it touches every existing row, it runs against
production volumes, and it is the step that cannot be done in a window. Naming it as a phase is what
makes `DPY-16` enforceable.

---

## 6. The Deployment Runsheet

### 6.1 Generic, not per-wave

`MG-006` §4.1 establishes that a **cutover** runsheet is *generated*, not authored, from the
migration content. A **deployment** runsheet is the opposite: the steps are the same every time, and
the per-wave variation lives in §12's profiles and in the checklist's scope column.

### 6.2 The sequence

| # | Step | Owner | Verification | Abort point |
|:--:|---|---|---|:--:|
| 1 | Confirm the go-live checklist (§8) complete, all nine sections | Release Manager | Signed checklist | **Yes** |
| 2 | Confirm the change record approved at the correct risk class (`RMP-09`) | Change Manager | Change record ID | **Yes** |
| 3 | Confirm no active freeze blocks this release (`RL-001` §7) | Release Manager | Change calendar | **Yes** |
| 4 | Declare the maintenance window; publish the notice (`OP-005`) | Platform Lead | Status page updated | — |
| 5 | Take the pre-deployment backup and **verify it is restorable** | Platform Lead | Restore test result | **Yes** |
| 6 | Record the currently deployed tag as the rollback target | Platform Lead | Tag recorded in the deployment record | **Yes** |
| 7 | Quiesce: stop schedulers, drain queues, park integrations | Platform Lead | Queue depth zero; no in-flight jobs | **Yes** |
| 8 | Apply **Expand** schema changes, if any (§5) | Platform Lead | Migration log; row counts | **Yes** |
| 9 | Deploy the artefact | Platform Lead | Version endpoint returns the expected tag | **Yes** |
| 10 | Apply configuration; **promote, never hand-edit** (`DPY-04`) | Platform Lead | Configuration diff empty against the promoted set | **Yes** |
| 11 | Restart schedulers, resume integrations | Platform Lead | Consumers connected; lag falling | **Yes** |
| 12 | **Run the smoke test** (§7) | QA on call | Smoke result: pass / fail per case | **Yes — the last one** |
| 13 | Close the maintenance window; update the status page | Platform Lead | Status page updated | — |
| 14 | Publish the release note (`RMP-41`) | Release Manager | Note published, archived | — |
| 15 | Enter the **48-hour verification window** (§10) | Support Lead | Verification report at +48 h | — |
| 16 | Start the backfill, where §5 phase M applies | Platform Lead | Batch progress; restart point recorded | — |

> **`DPY-19` — step 12 is the last abort point.** After the smoke test passes and the window closes,
> users are transacting, and the correction is a forward fix or a rollback with data implications
> (§9.6), not an abort.

> **`DPY-20` — steps 5 and 6 are not optional and are not "usually fine".** They are the two steps
> whose absence turns a failed deployment into an incident. `DoD-16`'s *"rollback plan documented
> **and rehearsed**"* is verified at `P-23`, not here; here it is executed.

### 6.3 Roles on the night

Adopted from `MG-006` §3.1's incident-command structure, reduced to the four roles a deployment
needs. **A deployment does not need a full cutover command structure, and staffing one for a routine
release is how people stop turning up.**

| Role | Held by | Authority |
|---|---|---|
| **Deployment Lead** | Platform Lead or named deputy | Runs the runsheet; calls each step |
| **Verifier** | QA on call | Owns step 12; the only role that may declare the smoke test passed |
| **Abort Authority** | §9.3 | The only role that may abort |
| **Communicator** | Release Manager or duty deputy | Owns steps 4, 13, 14 and every §11 message |

| # | Rule |
|---|---|
| **`DPY-21`** | **The Deployment Lead and the Verifier are never the same person.** This is `RMP-16`'s segregation applied to the night itself, and it is the control that stops *"it looked fine to me"* becoming a verification |
| **`DPY-22`** | For a wave release, the roles are **absorbed into `MG-006`'s cutover command structure** and report to the Cutover Commander. There is one command structure per night, not two |

---

## 7. The Smoke Test

### 7.1 What it is and what it is not

`CUT-01` requires the application to be *"smoke-tested"* before the freeze instant, and no document
in the estate defines a smoke test.

> **`DPY-23`. A smoke test answers one question: *did this deployment leave the system able to do
> the things it could do before?* It is not a regression suite, not a UAT and not a performance
> test.** Those are `QA-001` levels L4, L6 and L8, they run before the artefact ever reaches
> `staging`, and repeating them at 01:00 tests the deployment engineer's endurance rather than the
> deployment.

| It is | It is not |
|---|---|
| Fast — **≤ 15 minutes**, wall clock | A full regression run |
| Automated where possible, scripted where not | Exploratory |
| Run in `prod` against production data | Run in a test environment |
| Scoped to **critical paths plus this release's change** | Scoped to everything |
| Pass/fail per case, with no interpretation required | A judgement call |

### 7.2 The standing smoke set

Runs on **every** production deployment from the wave in which the capability goes live. The set
grows by wave; it is never pruned.

| # | Case | From wave | Why it is in the standing set |
|:--:|---|:--:|---|
| `SM-01` | Sign in with MFA as a branch user; sign out | W1 | If authentication is broken nothing else matters (`M29`) |
| `SM-02` | Create a service order from walk-in intake; retrieve it by reference | W1 | The primary transaction of the business (`M01`) |
| `SM-03` | Transition a service order through one lifecycle state; confirm the audit entry | W1 | Lifecycle plus audit trail in one case (`G1-07`) |
| `SM-04` | Render one screen in Bengali and confirm no untranslated key | W1 | `G1-08`; a broken translation bundle is invisible to an English-reading engineer |
| `SM-05` | Confirm one outbound event is published and consumed | W1 | The outbox relay is the silent failure (`AS-08`) |
| `SM-06` | Confirm a scheduled job has run since the deployment | W1 | `SRC-048`: *"an unregistered job that stops running is invisible"* |
| `SM-07` | Technician app: sign in, sync, complete one job step offline, sync back | W2 | `G2-02`, `G2-03` — the field model (`M02`) |
| `SM-08` | Customer portal: book a service; retrieve the tracking page | W2 | The external surface (`P01`) |
| `SM-09` | Issue one part from branch stock; confirm the stock movement and valuation | W2 | `M15`; stock moving without valuation is an automatic `S1` |
| `SM-10` | Generate one invoice from a closed job; confirm the Mushak fields | W3 | `G3-01`, `G3-04`; a wrong Mushak field is an automatic `S1` |
| `SM-11` | Take one payment through each live gateway in test mode; confirm reconciliation record | W3 | `G3-03` |
| `SM-12` | Submit one warranty claim to a brand portal integration in sandbox | W4 | `M09`; the largest revenue-recovery path |
| `SM-13` | Corporate portal: approve one order under a delegation limit | W4 | `M63` decision tables |
| `SM-14` | Contact centre console: open one conversation and attach it to a customer | W4 | `M10`, `P10` |
| `SM-15` | Run one payroll calculation for a single test employee; confirm the YTD figure | W5 | A wrong payroll figure is an automatic `S1` |
| `SM-16` | Record one attendance event and one quality audit finding | W5 | `M55`, `M23` |
| `SM-17` | Marketplace: place one order against a test seller; confirm the payout record | W7 | `G7-02` payout accuracy |
| `SM-18` | Warehouse query returns within the `NFR` threshold for a dashboard tile | W8 | `G8-01` |
| `SM-19` | Create one transaction under a second legal entity; confirm entity segregation | W9 | `G9-01`, `G9-02` |

**Nineteen standing cases.** Counted at 2026-08-18 23:27 (+06). By wave, cumulative:
W1 **6** · W2 **9** · W3 **11** · W4 **14** · W5 **16** · W6 **16** · W7 **17** · W8 **18** · W9 **19**.

### 7.3 The change-scoped smoke set

| # | Rule |
|---|---|
| **`DPY-24`** | Every release adds **at least one** smoke case per user-visible change in it, chosen by the change's own author and reviewed by the Verifier. A release with a user-visible change and no added smoke case is rejected at pre-flight (`P-11`) |
| **`DPY-25`** | A change-scoped case that fails **twice across two consecutive releases** is promoted into the standing set (§7.2). Recurrence is the signal that a path is fragile |
| **`DPY-26`** | The whole smoke run — standing plus change-scoped — is capped at **15 minutes**. When it exceeds the cap, standing cases are **automated**, never dropped |

### 7.4 Pass, fail and the `RC-A` rule

| Result | Meaning | Action |
|---|---|---|
| **All pass** | The deployment left the system able to do what it could do before | Close the window; enter §10 |
| **Any standing case fails** | **Rollback.** No triage, no discussion, no "we know what that is" | §9.6 |
| **Any change-scoped case fails** | Deployment Lead and Verifier decide jointly: roll back, or disable the change by toggle (`RMP-02`) and proceed | Recorded either way |
| **Any case on an `RC-A` population fails** | **Rollback**, and the defect is an automatic `S1` under `QA-001` §5.4 / `QA-010` `DMG-T2` | §9.6 |

> **`DPY-27`.** A failing smoke case is **never** re-run to see whether it passes the second time
> without first recording the first result. This is the deployment-night version of `MTS-R3` —
> severity is never adjusted to make a gate passable — and it is the most tempting rule in this
> document to break at 01:30.

---

## 8. The Go-Live Checklist

### 8.1 How to read it

> **`DPY-28`. The checklist is completed and signed *before* the maintenance window opens, not
> during it.** An item discovered incomplete at step 1 of the runsheet is a cancelled deployment,
> which is cheap. The same item discovered at step 9 is an incident.

Scope column: **`A`** = every production deployment · **`W`** = wave releases only · **`C`** = when
the deployment sits inside a cutover window.

### 8.2 The checklist

**Section P — Pre-flight: authorisation and scope** *(9 items)*

| # | Item | Scope | Evidence | Owner |
|---|---|:--:|---|---|
| `P-01` | Release type, change class and tag form assigned together (`RMP-05`) | `A` | Release record | Release Manager |
| `P-02` | Change record approved at the correct risk class (`RMP-09`) | `A` | Change record ID | Change Manager |
| `P-03` | No active freeze blocks this release; any waiver has both authorities (`RMP-36`) | `A` | Change calendar entry | Release Manager |
| `P-04` | Release day complies with `RMP-13`/`RMP-14`/`RMP-15` | `A` | Calendar | Release Manager |
| `P-05` | Wave gate **passed** and its decision recorded in `GV-003` | `W` | Gate report + `D-nnn` | PMO |
| `P-06` | `RL-003` readiness assessment complete; no dimension vetoed | `W`,`C` | Readiness record | PMO |
| `P-07` | Scope matches the locked wave scope; no late additions (`GW-37`) | `W` | Scope baseline diff | PMO |
| `P-08` | `RMP-25` satisfied — this deployment is ≥ 15 working days before the freeze instant | `C` | Cutover plan date | Data Migration Lead |
| `P-09` | No release combines two §5 phases (`DPY-14`) | `A` | Migration review | Platform Lead |

**Section Q — Quality gates** *(7 items)*

| # | Item | Scope | Evidence | Owner |
|---|---|:--:|---|---|
| `Q-01` | `QA-010` `DMG-T1` — zero open `S1` in scope | `A` | Defect register | Head of Quality Engineering |
| `Q-02` | `QA-010` `DMG-T2` — zero open defects on an `RC-A` population | `A` | Defect register | Head of Quality Engineering |
| `Q-03` | `QA-010` `DMG-T7` — zero defects "fixed, awaiting retest" | `A` | Defect register | Head of Quality Engineering |
| `Q-04` | `DMG-T3`/`T4`/`T5` within threshold, or a Steering Committee acceptance recorded | `W` | Defect register + acceptance | Head of Quality Engineering |
| `Q-05` | Artefact passed `sit`; contract suite green (`IN-008`) | `A` | CI record | QA Lead |
| `Q-06` | Artefact passed `uat`; business acceptance signed (`QA-009`) | `W` | Signed UAT record | Business Owner |
| `Q-07` | `perf` results within `NFR` thresholds for the delivered scope | `W` | `QA-006` report | Platform Engineering |

**Section S — Security and privacy** *(5 items)*

| # | Item | Scope | Evidence | Owner |
|---|---|:--:|---|---|
| `S-01` | `SG-1` — zero open critical/high security findings in scope | `A` | `QA-007` report + independent review | Security Lead |
| `S-02` | `SG-2` — lawful basis recorded for any new processing purpose; DPIA updated | `W` | `SC-003` update | DPO |
| `S-03` | `SG-3` — no unmasked production personal data in any non-production environment | `A` | `DA-005` compliance query | Security Lead |
| `S-04` | Secrets rotated where the release changes an integration credential | `A` | Vault record | Security Lead |
| `S-05` | New or changed API surface published and access-controlled (`IN-005`) | `A` | OpenAPI diff | Integration Lead |

**Section D — Data and schema** *(6 items)*

| # | Item | Scope | Evidence | Owner |
|---|---|:--:|---|---|
| `D-01` | Every migration classified into a §5 phase | `A` | Migration manifest | Platform Lead |
| `D-02` | Migration tested against a production-sized dataset (`OPS-07`, `DPY-17`) | `A` | `perf` run log, or a recorded estimate where `perf` does not exist | Platform Lead |
| `D-03` | Backfill batched, restartable, idempotent; runs outside the window (`DPY-16`) | `A` | Backfill script review | Platform Lead |
| `D-04` | Migration **duration measured**, not estimated, where a window applies | `A` | Timing from `staging` | Platform Lead |
| `D-05` | Contract-phase changes confirmed against a zero-reference query (`DPY-15`) | `A` | Query result | Platform Lead |
| `D-06` | No cutover data movement in this window (`DPY-08`) | `C` | Cutover plan | Data Migration Lead |

**Section E — Environment and infrastructure** *(7 items)*

| # | Item | Scope | Evidence | Owner |
|---|---|:--:|---|---|
| `E-01` | Target environment configuration matches the promoted set; no hand edits (`MTS-E3`) | `A` | Configuration diff | Platform Lead |
| `E-02` | Capacity headroom confirmed for the release's expected load | `W` | `PE-006` capacity position | Platform Engineering |
| `E-03` | Integration endpoints and credentials valid in the target | `A` | Connectivity check | Integration Lead |
| `E-04` | Scheduled jobs inventory current; new jobs registered (`SRC-048`) | `A` | Job register | Platform Lead |
| `E-05` | Monitoring and alerting cover the changed surface | `A` | `PE-008` dashboards (design issued; **not yet implemented**) | Platform Lead |
| `E-06` | `dr` replication healthy and lag within tolerance | `W` | Replication metric | Platform Lead |
| `E-07` | **A rolling deployment has been executed in `staging` and measured to produce zero failed requests** (`DPY-13`, `NFR-008` condition 3) | `W` | Measured request-failure count across the roll | Platform Lead |

**Section R — Rollback readiness** *(5 items)*

| # | Item | Scope | Evidence | Owner |
|---|---|:--:|---|---|
| `R-01` | Prior tag identified and confirmed deployable | `A` | Deployment record | Platform Lead |
| `R-02` | Pre-deployment backup taken **and restore-verified** | `A` | Restore test result | Platform Lead |
| `R-03` | Rollback procedure documented for this specific release | `A` | Release record | Platform Lead |
| `R-04` | Rollback **rehearsed** (`DoD-16`), with a measured duration | `W` | Rehearsal record + duration | Platform Lead |
| `R-05` | Measured rollback duration fits inside the remaining window (`MG-007`; `DM-014` `T4`) | `C` | Arithmetic, shown | Data Migration Lead |

**Section O — Operational readiness** *(7 items)*

| # | Item | Scope | Evidence | Owner |
|---|---|:--:|---|---|
| `O-01` | On-call rota staffed for the window and the following 48 hours (`SG-5`) | `A` | Published rota (`SV-004` issued; **no rota staffed**) | Service Manager |
| `O-02` | Paging tested end to end within the last 7 days | `A` | Page test record (`SV-004` issued; **no paging platform, no test**) | Service Manager |
| `O-03` | Runbooks updated for the changed surface and **rehearsed** (`SG-4`) | `W` | `OP-007`…`OP-011` change log | Service Manager |
| `O-04` | Support macros and canned responses updated (`OP-003`) | `W` | Macro set version | Support Lead |
| `O-05` | Known-issue log current and reconciled with the release note (`RMP-42`) | `A` | Known-issue log | Support Lead |
| `O-06` | Manual fallback procedures current for the affected functions (`OP-014`) | `W`,`C` | `OP-014` review date | Operations Director |
| `O-07` | Floor-walking coverage arranged where a site is receiving this release first | `W` | `OP-002` §4.4 roster | Change Lead |

**Section C — Communication** *(6 items)*

| # | Item | Scope | Evidence | Owner |
|---|---|:--:|---|---|
| `C-01` | Maintenance notice published ≥ 3 working days ahead (`OP-005`) | `A` | Status page | Release Manager |
| `C-02` | Release note drafted, translated and approved, ready to publish | `A` | Draft note | Content Design |
| `C-03` | Wave note published **10 working days** ahead (`OP-006` `WN-01`) | `W` | Published note | Programme Manager |
| `C-04` | All seven `CM-006` assets `G1`…`G7` exist, translated and approved (`GO-01`) | `W`,`C` | Approved pack | Change Lead |
| `C-05` | `G4` contact-centre brief released at T−2 days, carrying **both** branches (`GO-02`) | `W`,`C` | Brief issued | Contact Centre Manager |
| `C-06` | The **no-go, delayed-go, partial-go and fallback** variants exist and are approved (`GO-13`) | `W`,`C` | Approved variants | Change Lead |

**Section X — Execution and close** *(7 items)*

| # | Item | Scope | Evidence | Owner |
|---|---|:--:|---|---|
| `X-01` | Deployment Lead and Verifier named, and are different people (`DPY-21`) | `A` | Runsheet header | Platform Lead |
| `X-02` | Abort Authority named and reachable for the whole window (§9.3) | `A` | Runsheet header | Release Manager |
| `X-03` | Smoke set assembled: standing cases for the current wave plus change-scoped (`DPY-24`) | `A` | Smoke manifest | Verifier |
| `X-04` | Smoke test executed and passed within 15 minutes (`DPY-26`) | `A` | Smoke result | Verifier |
| `X-05` | Release note published (`RMP-41`) | `A` | Published note | Release Manager |
| `X-06` | Deployment record closed: tag, timestamps, participants, result | `A` | Deployment record | Platform Lead |
| `X-07` | 48-hour verification window opened with a named owner (§10) | `A` | Verification record | Support Lead |

### 8.3 Count and coverage

**59 items across 9 sections.** Recounted from §8.2 at the audit, 2026-08-19 02:10 (+06):
P **9** · Q **7** · S **5** · D **6** · E **7** · R **5** · O **7** · C **6** · X **7** = **59**.

> **⚠ Corrected at audit — finding `RLA-15`.** The v1.0 issue of this line read *"58 items across
> **8** sections"* while §1.2 read *"58 items across **nine** sections"* and the checklist itself
> carried nine section headings. A correct item total beside a wrong section count is the
> `PGD-A2-24` / `QAA-12` defect class occurring **inside a document that cites that defect class
> twice**, which is the most useful kind of self-audit finding this category produced. The item
> total also moves 58 → 59 with the addition of `E-07`.

| Scope | Items | Applies to |
|---|---:|---|
| `A` — every production deployment | **38** | The routine minimum |
| `W` — wave releases additionally | **17** | Nine occasions |
| `C` — cutover-window deployments additionally | **6** | Nine occasions; overlaps `W` |

> **`DPY-29` — six checklist items cannot be evidenced today, and as of the audit's final
> enumeration every one of them is blocked by an absent *capability*, not an absent document.**
> That is a change from this document's v1.0, when two were document-blocked, and it happened
> because five categories were authored around it in one night. The items did not move.
>
> | Item | Blocked by | Kind of absence |
> |---|---|---|
> | `O-01`, `O-02` | `SV-004` issued 2026-08-19; **no rota staffed, no paging tested** | Capability absent |
> | `E-05` | `PE-008` issued 2026-08-19; **dashboards not built** | Capability absent |
> | `E-07` | No rolling deployment yet measured for downtime | Capability absent |
> | `Q-07` | `perf` specified by `PE-002`; **not provisioned** | Capability absent |
> | `R-04` | No environment in which to rehearse rollback | Capability absent |
>
> They remain on the checklist, **unticked and visible**, rather than being removed to make it
> completable. `GV-009` `GA-06` applies: *"zero findings from a test that did not run is not zero
> findings."* **A specification issuing does not tick a checklist item** — this is the distinction
> `PGD-000` §0.3 draws between a document existing and a capability existing, and the audit
> correction at §3.1 and §4.2 is precisely a case of the first being mistaken for the second.

---

## 9. Abort

### 9.1 Abort, rollback and fallback are three words

| Term | Means | Owned by |
|---|---|---|
| **Abort** | Stop the deployment before it completes; return to the prior state | This document, §9 |
| **Rollback** | Return production to the previously deployed tag | This document, §9.6 (code) · `MG-007` (data) |
| **Fallback** | Operate the business on legacy or on paper because the new system cannot be used | `MG-007` §8, `OP-014` |

> **`DPY-30`.** These are never used interchangeably in this category. An abort has no business
> consequence; a rollback has a support consequence; a fallback has a business consequence and a
> statutory one.

### 9.2 Abort criteria

Any one of these, at any runsheet step, aborts the deployment. They are deliberately **mechanical**
— `DM-014` `CV-15`'s principle that *"fallback is triggered by a rule, not by a mood"* applies with
equal force to a deployment at 01:00.

| # | Trigger | Why it is absolute |
|:--:|---|---|
| `DA-1` | **The pre-deployment backup cannot be verified restorable** (`R-02`) | Without it there is no floor under any subsequent step |
| `DA-2` | **A migration exceeds its measured duration by more than 50%** | The estimate was wrong; the remaining steps' estimates are therefore also wrong |
| `DA-3` | **Any standing smoke case fails** (`SM-01`…`SM-19`) | The system cannot do what it could do before |
| `DA-4` | **Any smoke case on an `RC-A` population fails** | Automatic `S1`; `DMG-T2` is zero and is not acceptable by any body |
| `DA-5` | **The maintenance window will be exceeded** (`DPY-11`) | Branches open into an in-progress deployment |
| `DA-6` | **The rollback path is no longer executable** — measured rollback duration exceeds the remaining window | This is `DM-014` `T4` applied to code. Continuing means continuing with no way back |
| `DA-7` | **A `Sev1` incident is declared in an unrelated part of the platform** | Two concurrent emergencies share one on-call rota |
| `DA-8` | **The Verifier is unable to verify** — environment access lost, telemetry unavailable, no evidence obtainable | An unverified deployment is an unknown state, which is worse than a known old one |

### 9.3 Who may abort

| Situation | Abort Authority | May not be delegated to |
|---|---|---|
| Routine production deployment | **Deployment Lead** or **Verifier**, independently | — |
| Wave release outside a cutover window | **Platform Lead with the Release Manager** | The deployment engineer alone |
| Deployment inside a cutover window | **Cutover Commander** (`MG-006` §3.1) | Anyone outside the command structure |
| Any deployment, on `DA-4` (`RC-A` failure) | **Automatic.** No decision is taken | — |

| # | Rule |
|---|---|
| **`DPY-31`** | **Either the Deployment Lead or the Verifier may abort alone.** Requiring agreement to stop, while one person alone may continue, biases every marginal call toward continuing at the hour when judgement is worst |
| **`DPY-32`** | `DA-4` aborts **without a decision**. The rule exists because an `RC-A` failure at 01:00 will otherwise be discussed, and `QA-001` `MTS-R9` forbids truncating an `RC-A` population |
| **`DPY-33`** | An abort is **never** a performance matter for the person who called it. `DM-014` `RB-10`'s logic — *"the moment the first branch to say so is treated as a problem, every subsequent branch says it is ready"* — applies to deployment engineers exactly as it does to branch managers |

### 9.4 The seam with `DM-014`'s fallback triggers

`DM-014` `T1`…`T7` are **data** triggers: reconciliation, finance tolerance, semantic defect,
rollback window, owner refusal, Mushak sequence, incomplete counts. `DA-1`…`DA-8` are **code**
triggers.

> **`DPY-34`.** Inside a cutover window both sets are live, and they are assessed by different
> people against different evidence. A `DA-*` abort during a cutover **does not** trigger `T1`…`T7`;
> it means the wave release is not in place, which — under `RMP-25` — should already have been true
> fifteen working days earlier, and is therefore a schedule failure rather than a data one.
> This is `CUT-01`'s benefit made concrete: **the two failure modes now have two clocks.**

### 9.5 Rehearsal

> **`DPY-35`.** `DoD-16` requires the rollback to be *documented **and rehearsed***. A rehearsal is
> an execution of §9.6 in `staging`, by someone who did not write the deployment, producing a
> **measured duration**. `MG-007` §7.5 sets the same standard for data rollback and states why: an
> unrehearsed rollback is a second incident. Checklist item `R-04` is where it is verified, and
> `DPY-29` records that it cannot be verified until an environment exists.

### 9.6 Code rollback

| Step | Action | Constraint |
|:--:|---|---|
| 1 | Declare rollback; record the trigger (`DA-n`) and the time | — |
| 2 | Stop schedulers; drain queues; park integrations | As runsheet step 7 |
| 3 | Redeploy the prior tag recorded at runsheet step 6 | The tag is never rebuilt (`DPY-04`) |
| 4 | **Do not reverse Expand-phase schema changes** | `DPY-36` |
| 5 | Restore configuration to the prior promoted set | Promoted, not hand-edited |
| 6 | Restart; run the standing smoke set for the current wave | The same set, unchanged |
| 7 | Publish the outcome (§11 `M-05`) | Within 1 hour |
| 8 | Post-incident review within 5 working days (`OP-016`) | Mandatory regardless of how cleanly it executed (`RB-04`) |

> **`DPY-36` — an Expand-phase schema change is not reversed on rollback.** By construction (§5) it
> is additive, nullable and unreferenced by the prior code; reversing it under time pressure is a
> destructive operation with no benefit. This is the practical payoff of the expand/contract
> protocol: **rollback becomes a code-only operation**, and code-only operations are fast enough to
> fit inside a window.

> **`DPY-37` — where the release included a Contract phase, rollback is not available.** §5 makes
> Contract the single irreversible step, and `DPY-15` already prevents it from running near a wave
> release. If a Contract-phase release must be reversed, it is a **data** recovery under `MG-007`
> `M3` (full restore), with that document's data-loss position, not a deployment rollback.

---

## 10. Verification

### 10.1 The 48-hour window

> **`DPY-38`. A deployment is not complete when the smoke test passes. It is complete 48 hours
> later, when nothing has emerged.**

| Interval | Measured | Owner |
|---|---|---|
| +0 to +15 min | Smoke set (§7) | Verifier |
| +15 min to +2 h | Error rate, queue depth, integration lag, job completion | Platform Lead |
| +2 h to +24 h | Support contact volume against the prior baseline; new defect arrivals | Support Lead |
| **+24 h to +48 h** | The above, plus the first full business day's transaction volumes against plan | Support Lead |
| **+48 h** | **Verification report**: pass, pass-with-issues, or fail | Support Lead |

### 10.2 What each outcome means

| Outcome | Definition | Action |
|---|---|---|
| **Pass** | No new `S1`; no new `S2` attributable to the release; volumes within tolerance | Close the deployment record |
| **Pass with issues** | New `S3`s, or `S2`s with accepted workarounds | Close, with entries added to the known-issue log and the next release note (`RMP-42`) |
| **Fail** | A new `S1`, or an `S2` on an `RC-A` population, or volumes materially below plan | Forward fix as an emergency change (§13), or rollback under §9.6 if still available |

| # | Rule |
|---|---|
| **`DPY-39`** | The verification window's **owner is the Support Lead, not the Platform Lead**. The people who executed a deployment are the wrong people to decide whether it worked — `GV-009` `GA-09`'s cross-assessment principle, applied at deployment scale |
| **`DPY-40`** | A deployment whose verification fails **blocks the next `T-PROD` train** until its outcome is resolved. Stacking a second release onto an unverified first is how attribution is lost |
| **`DPY-41`** | During hypercare, the verification window is **subsumed into `OP-002`'s daily triage** (09:30 and 17:30) rather than run separately. Two parallel verification processes over the same population produce two different numbers |

### 10.3 Verification cannot be automated today

> **`DPY-42`.** `PE-008` (Observability & Monitoring Design) was **issued 2026-08-19** and `SV-004`
> (On-Call, Paging & Escalation) remains **⛔**. A design is not a dashboard and a specification does
> not answer a page: everything in §10.1 between +15 minutes and +48 hours therefore still depends
> on **someone looking**, at intervals, until `PE-008` is implemented and `SV-004` is written. This
> is the position `AUDIT-017` described as *"operational content and no operational capability."*
>
> The window stands as specified. What is recorded here is that its execution is **manual, staffed
> and unfunded** in `06-01` §4's team model, and that this is a `RL-003` dimension D5 finding at
> every gate until `PE-008` and `SV-004` issue.

---

## 11. Communication During a Deployment

`CM-006` owns the go-live pack and its wording; `OP-005` owns maintenance notices; `OP-006` owns
release notes. **None is restated.** What this section adds is the set of moments at which the
deployment itself must speak.

| # | Moment | Audience | Content | Source |
|:--:|---|---|---|---|
| `M-01` | **T−3 working days** | All affected users; customers from W2 | Maintenance window declared | `OP-005` |
| `M-02` | **Window opens** | Status page; internal channel | "Starting now" | `OP-005` |
| `M-03` | **Window closes, smoke passed** | Status page; internal channel | "Complete" | `OP-005` |
| `M-04` | **Release note published** | Segmented audiences | The note | `OP-006` |
| `M-05` | **Abort or rollback**, within **1 hour** | All affected users; branch managers first | What happened, what to do now, when the next update comes | `CM-006` `GO-14` pattern |
| `M-06` | **Window overrun**, at the moment it is known | Status page; Operations Director | Revised end time — **never silence** | `OP-005` |
| `M-07` | **Verification fails at +48 h** | Support Lead → Release Manager → Change Manager | The outcome and the chosen route | This document |
| `M-08` | **Wave release: the go decision** | The full `CM-006` `G1`…`G7` pack | Released by `C7` and nothing else (`GO-03`) | `CM-006` |

| # | Rule |
|---|---|
| **`DPY-43`** | `M-05` and `M-06` are the two that get skipped, and they are the two that matter. `GO-14`: *"silence after a visible non-event is filled within a day by a version of the story nobody wrote"* |
| **`DPY-44`** | Every deployment message that reaches a branch or a customer is **Bengali-first** (`CV-09`, `SK-08`, `BN-007` numerals). A status page in English only does not discharge `M-02` for a branch population |

---

## 12. Per-Wave Deployment Profiles

### 12.1 How to read these

Each profile states what makes that wave's deployment different. **Durations are deliberately left
unstated**, following `MG-006` `CV-13`: a runsheet of estimates has not been rehearsed, and a
duration published before `perf` and `staging` exist would be a guess wearing a decimal point.

| Wave | Tag | Deploy by (`RMP-25`) | Smoke set | What makes this deployment different | Principal deployment risk |
|:--:|---|---|:--:|---|---|
| **W1** | `v1.0.0-w1` | T−15 wd before the W1 freeze instant | 6 | **First production deployment of anything.** The environment is new, the pipeline is manual, the rollback has never been executed against real infrastructure | `R-04` cannot be evidenced — there is no prior deployment to roll back to. §9.6 is theory until W1 proves it |
| **W2** | `v2.0.0-w2` | T−15 wd | 9 | First **mobile** artefact (`P02`) with an app-store lead time outside the programme's control; first external customer surface (`P01`) | A store rejection is a deployment dependency nobody can expedite. `OP-006` type 7's staged rollout schedule must start earlier than the wave release |
| **W3** | `v3.0.0-w3` | T−15 wd | 11 | First deployment touching **money**: gateways, bank connectors, Mushak sequences | `F2` and `F4` both bind. The window must sit outside a period close **and** outside a filing preparation, which in practice leaves one week per month |
| **W4** | `v4.0.0-w4` | T−15 wd | 14 | **v1.0 scope complete.** Four external populations receive changes at once; the contact centre goes live | `G4-10` requires every v1.0 BRD requirement demonstrated. A deployment defect here is visible to corporate clients under contract |
| **W5** | `v5.0.0-w5` | T−15 wd | 16 | **Payroll.** `F3` binds twice; `F2` and `F4` bind as well (`RL-001` §7.10) | The worst freeze collision in the programme. There is effectively no `T-PROD` window in W5 outside the wave release |
| **W6** | `v6.0.0-w6` | T−15 wd | 16 | Native apps with **forced upgrade**; `M66` goes live and the change-management system of record moves mid-programme | Migrating the change system while running a deployment governed by it. `RMP-10`'s interim ends here, and the transition is itself a change |
| **W7** | `v7.0.0-w7` | T−15 wd | 17 | External **sellers** — a population with no employment relationship and no obligation to read a notice | `GO-06`'s cascade does not exist for sellers. Portal banner and direct contact are the only channels |
| **W8** | `v8.0.0-w8` | T−15 wd | 18 | Mostly non-functional: scale, warehouse, models | The lowest user-visible risk and the highest **capacity** risk. `E-02` is the binding checklist item |
| **W9** | `v9.0.0-w9` | T−15 wd | 19 | **Multi-entity.** A deployment defect can cross an entity boundary, which is a statutory event | `SM-19` is the only smoke case whose failure has a cross-border consequence. `G9-01`'s 12-week second-entity standup is configuration-only and must not require a deployment |

### 12.2 The one profile that is not like the others

> **`DPY-45` — W1 is the only wave whose deployment cannot be de-risked by experience, and it is
> the wave with the least mature infrastructure.** Every rule in this document about rehearsal,
> measured durations and verified rollback assumes a prior deployment to learn from. W1 has none.
>
> The mitigation is not a rule; it is a **sequence**: `PE-002`, `PE-003` and `PE-004` — now issued —
> **implemented**, then at least three non-wave deployments to `staging` and `prod` executed under this
> runsheet before the W1 wave release. Three, because the first proves the path exists, the second
> proves it repeats, and the third produces a duration worth measuring. Raised as `Q-04`.

---

## 13. Emergency Deployment

`RL-001` §9 owns the **authority**; `BE-003` §9 owns the **git mechanics**; this section owns the
**execution**.

| Step | Deviation from §6 | Preserved |
|:--:|---|---|
| 1–3 | Compressed: change record raised retrospectively where `SP-004` `A-91` applies | The change record still exists |
| 4 | Maintenance window **not declared** where service is already degraded | `M-02`/`M-03` still issued |
| 5–6 | **Not skipped.** Backup and prior-tag identification are the two steps that make an emergency recoverable | Both |
| 7–11 | As normal | All |
| 12 | **Smoke test is not reduced.** The standing set for the current wave runs in full | `DPY-26`'s 15-minute cap |
| 13–16 | As normal, plus a post-incident review within 5 working days | `OP-016` |

| # | Rule |
|---|---|
| **`DPY-46`** | **An emergency deployment reduces the paperwork ahead of it, never the verification after it.** This is `GW-39` applied to deployment: the compensating control for a reduced approval count is an unreduced smoke test |
| **`DPY-47`** | An emergency deployment inside `F7` (gate evidence freeze) invalidates the affected criterion's evidence and requires it to be re-taken (`RMP-32`) |
| **`DPY-48`** | Three emergency deployments in one calendar month trigger a mandatory review of the `T-PROD` cadence by the CAB. `SP-031` §8: *"the normal path is too slow; fix the process, do not normalise emergencies"* |

---

## 14. Governing Rules — Consolidated

| # | Rule | § |
|---|---|:--:|
| `DPY-01` | The programme has ten environments, not five and not seven | 3.1 |
| `DPY-02` | The promotion path is `ci` → `dev` → `sit` → `uat` → `staging` → `prod` | 3.2 |
| `DPY-03` | `perf`, `sandbox`, `training` are branches off the path, not steps on it | 3.2 |
| `DPY-04` | The artefact is bit-identical at every step; configuration differs, the artefact does not | 3.2 |
| `DPY-05` | `dr` receives production by replication, never by deployment | 3.2 |
| `DPY-06` | `training` loads on the training cycle, not the release cycle | 3.2 |
| `DPY-07` | §3 specifies what must exist; `PE-002`/`PE-003` build it | 3.3 |
| `DPY-08` | A deployment and a data cutover never share a window | 3.4 |
| `DPY-09` | The per-component deployment strategy is `PE-004` §8.1's, adopted whole | 4.3 |
| **`DPY-09a`** | Cron-node deployments are scheduled outside `F2`, `F3` and `F4` freezes | 4.3 |
| `DPY-10` | Standard deployment window: Sun/Mon/Tue 23:00–02:00 `Asia/Dhaka` | 4.4 |
| `DPY-11` | The window is a maximum, not an allowance | 4.4 |
| `DPY-12` | The status page shows the window before, during and after | 4.4 |
| `DPY-13` | **`NFR-008` is specified as achievable and not yet demonstrated; condition 3 is the gap** | 4.5 |
| `DPY-14` | Expand, Migrate, Read-switch and Contract never share a release | 5.2 |
| `DPY-15` | Contract waits one wave-gate interval or a zero-reference proof | 5.2 |
| `DPY-16` | The backfill is batched, restartable and runs outside the window | 5.2 |
| `DPY-17` | Migrations are tested at production size; absent `perf`, timings are recorded as estimates | 5.2 |
| `DPY-18` | A migration that will not fit the protocol is a data migration (`MG-003`) | 5.2 |
| `DPY-19` | Smoke test is the last abort point | 6.2 |
| `DPY-20` | Backup-verified and prior-tag-recorded are not optional | 6.2 |
| `DPY-21` | Deployment Lead and Verifier are never the same person | 6.3 |
| `DPY-22` | Inside a cutover, roles fold into `MG-006`'s command structure | 6.3 |
| `DPY-23` | A smoke test answers one question and is not a regression suite | 7.1 |
| `DPY-24` | Every user-visible change adds at least one smoke case | 7.3 |
| `DPY-25` | A change-scoped case failing twice is promoted to the standing set | 7.3 |
| `DPY-26` | The smoke run is capped at 15 minutes; overflow is automated, not dropped | 7.3 |
| `DPY-27` | A failing case is never re-run before the first result is recorded | 7.4 |
| `DPY-28` | The checklist is signed before the window opens | 8.1 |
| `DPY-29` | Six checklist items are unevidenceable; document-absence ≠ capability-absence | 8.3 |
| `DPY-30` | Abort, rollback and fallback are three distinct words | 9.1 |
| `DPY-31` | Either the Deployment Lead or the Verifier may abort alone | 9.3 |
| `DPY-32` | `DA-4` aborts without a decision | 9.3 |
| `DPY-33` | An abort is never a performance matter for the caller | 9.3 |
| `DPY-34` | A `DA-*` abort in a cutover is a schedule failure, not a data one | 9.4 |
| `DPY-35` | Rollback rehearsal is executed by someone who did not write the deployment | 9.5 |
| `DPY-36` | Expand-phase schema changes are not reversed on rollback | 9.6 |
| `DPY-37` | A release containing a Contract phase has no deployment rollback | 9.6 |
| `DPY-38` | A deployment completes at +48 hours, not at smoke-test pass | 10.1 |
| `DPY-39` | The verification window is owned by the Support Lead | 10.2 |
| `DPY-40` | A failed verification blocks the next `T-PROD` train | 10.2 |
| `DPY-41` | In hypercare, verification folds into `OP-002` triage | 10.2 |
| `DPY-42` | Verification stays manual until `PE-008` is implemented and `SV-004` is written | 10.3 |
| `DPY-43` | `M-05` and `M-06` are the messages that get skipped and the ones that matter | 11 |
| `DPY-44` | Every user-reaching deployment message is Bengali-first | 11 |
| `DPY-45` | W1 cannot be de-risked by experience; three prior deployments are the mitigation | 12.2 |
| `DPY-46` | Emergency reduces paperwork before, never verification after | 13 |
| `DPY-47` | An emergency inside `F7` invalidates gate evidence | 13 |
| `DPY-48` | Three emergencies in a month trigger a CAB cadence review | 13 |

**Forty-nine rules** — `DPY-01`…`DPY-48` plus **`DPY-09a`**, added at the audit of 2026-08-19.
Counted from this table at 2026-08-19 02:10 (+06).

> The sub-numbered form `DPY-09a` is used rather than renumbering `DPY-10`…`DPY-48`, because five
> other documents in this category already cite those identifiers. `GW-36`'s principle — *a wrong
> tag is superseded by a new one, never moved* — applies to rule identifiers for the same reason.

---

## 15. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Who owns `PE-004-F-02`'s condition 3 — the readiness-check contract — and when is a rolling deployment first **measured** for downtime? | `PE-005` owner with the Platform Lead | **W1** | `DPY-13`; checklist item `E-07`; `NFR-008`'s demonstration |
| `Q-02` | Who **provisions** `PE-002`'s twelve environments, and in what order? The specifications exist; none is built | Platform Lead | **W1 minus 3 months** | `DPY-07`; checklist `Q-07` and `R-04` |
| `Q-03` | What is the app-store submission lead time for `P01`/`P02`, and who owns it? | Mobile Lead | **W2 minus 2 months** | W2 profile; `OP-006` type 7 |
| `Q-04` | Are three pre-W1 rehearsal deployments funded in `06-01` §4's team model? | Programme Manager | **W1 minus 2 months** | `DPY-45` |
| `Q-05` | Which role holds the Verifier duty before a Head of Quality Engineering is appointed? | Programme Director | **W1** | `DPY-21` |
| `Q-06` | Does `MG-006` accept `RMP-25`/`RMP-26` as the answer to its `Q-01`, or does the cutover model require different dates? | Data Migration Lead | **W1 minus 2 months** | `DPY-08`, `P-08` |
| `Q-07` | Where is the standing smoke set maintained as executable code — a `PE-004` pipeline stage, or a `QA-005` framework suite? | QA Lead with the Platform Lead | **W1** | `DPY-26` automation |

---

## 16. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `RL-002-D-01` | How to resolve two environment enumerations | (a) Adopt TSS's five · (b) Adopt `QA-001`'s seven · (c) Union of ten | **(c)** | Both lists are correct about their own purpose and neither is complete. A promotion path needs both ends | Ten environments to provision, 0 provisioned. `PE-002` inherits a defined consumer |
| `RL-002-D-02` | Deployment model | (a) Specify blue/green as the target and write for it · (b) Write for what is executable and state the gap | **(b) — `Recreate`** | Writing a runsheet for a model that requires four ⛔ documents produces a document nobody can follow at W1 | `NFR-008` is declared unmet (`DPY-13`) rather than silently assumed |
| `RL-002-D-03` | Whether to define a smoke test at all, given `QA-001` owns testing | (a) Delegate to `QA-001` · (b) Define here | **(b)** | `CUT-01` requires a smoke test as a **deployment** gate, and `QA-001`'s thirteen levels contain nothing that runs in `prod` in 15 minutes | 19 standing cases owned here; `QA-001` §7 unaffected |
| `RL-002-D-04` | Whether either the Deployment Lead or the Verifier may abort alone | (a) Both must agree · (b) Either may abort | **(b)** | Requiring agreement to stop while one may continue biases marginal calls toward continuing | More aborts, earlier. That is the intent |
| `RL-002-D-05` | Whether to reverse Expand-phase schema on rollback | (a) Full symmetric reversal · (b) Leave additive changes in place | **(b)** | By construction they are unreferenced by the prior code; reversing under time pressure is destructive with no benefit | Rollback becomes code-only and fits inside a window |
| `RL-002-D-06` | Keep unevidenceable checklist items, or remove them | (a) Remove until their dependency exists · (b) Keep, visibly unticked | **(b)** | `GA-06`: *"zero findings from a test that did not run is not zero findings"* | Every W1 deployment carries five open items on its record |

---

## 17. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | `MG-006` `CUT-01`'s interface is honoured and its `Q-01` answered | §1.1; `RMP-25`/`RMP-26`; §7; §10 |
| `AC-02` | The two environment enumerations are reconciled into one promotion path | §3.1, §3.2 — ten environments, one path |
| `AC-03` | The deployment strategy is sourced from its owning document, and `NFR-008`'s position is stated accurately | `DPY-09`, `DPY-09a`, `DPY-13`; corrected at audit (`RLA-14`) |
| `AC-04` | `OPS-07`'s *"documented procedure"* exists | §5.2 — four phases, three releases, five rules |
| `AC-05` | The go-live checklist is countable and its coverage stated | §8.3 — **59 items, 9 sections**, three scopes; recounted at audit |
| `AC-06` | Every checklist item that cannot be evidenced today is named, and document-absence is distinguished from capability-absence | `DPY-29` — **six items**, two document-absent and four capability-absent |
| `AC-07` | Abort criteria are mechanical, and the authority to abort is named | §9.2 `DA-1`…`DA-8`; §9.3 |
| `AC-08` | Abort, rollback and fallback are distinguished and the `MG-007` seam stated | `DPY-30`, §9.4, `DPY-37` |
| `AC-09` | A smoke test is defined, scoped, counted and capped | §7 — 19 standing cases, 15-minute cap |
| `AC-10` | Nine per-wave profiles exist, each naming what makes it different | §12.1 |
| `AC-11` | No rule identifier collides with any existing identifier in the workspace | §2.4 — `DPY` verified at zero across 754 files |
| `AC-12` | Every open question has an owner and a needed-by date | §15 — seven questions |

**Definition of done.** As `RL-001` §16, and subject to the same `PGD-A2-25` qualification on
test (d).

---

## 18. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `RL-001` | Authorises what this document executes; supplies `RMP-25`, `RMP-26`, `RMP-28` |
| Upstream | `MG-006` `CUT-01` | The interface this document was written to honour; its `Q-01` is answered |
| Upstream | TSS §18.3 | Five deployment targets and the expand/contract sentence |
| Upstream | `QA-001` §7.1 | Seven test environments; 0 of 7 provisioned |
| Upstream | `05-06` `NFR-008`, `OPS-07` | Zero-downtime obligation; forward-only reversible migrations |
| Upstream | `QA-010` §5.3 | `DMG-T1`…`T9` become checklist section Q |
| Upstream | `CM-006` | Seven go-live assets and four no-go variants become checklist section C and §11 |
| Downstream | **`RL-003`** | Consumes the checklist as dimension D2 (technical) readiness evidence |
| Downstream | **`RL-004`** | Uses §4.4's window and §12's profiles to sequence branch tranches |
| Downstream | **`RL-005`** | Measures deployment outcomes; `DPY-38`'s verification result is a PIR input |
| Downstream | `MG-006` | `DPY-08` and `DPY-34` complete the seam `MG-006` §2.3 opened |
| Upstream | `PE-002` §4.2 | **The twelve-environment inventory this document adopts** (§3.1) |
| Upstream | `PE-004` §3.1, §7, §8 | Build-once-and-promote; forward-only migrations; per-component deployment strategy — all adopted by citation |
| Downstream | `PE-005` §6 | Carries `PE-004-F-02`'s readiness-check obligation, on which `NFR-008` turns (`DPY-13`) |
| Downstream | `PE-008`, `SV-004` (both issued; both unimplemented) | Required before §10's verification window can be anything but manual |
| Lateral | `OP-005` | Maintenance notice copy for `M-01`, `M-02`, `M-03`, `M-06` |
| Lateral | `OP-014` | Manual fallback during an abort with business impact |
| Lateral | `IN-008` | `sandbox` certification suite gating §3.2's branch |

---

## 19. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`RL-001`](RL-001_Release_Management_and_Versioning_Policy.md) ·
[`RL-003`](RL-003_Go_Live_Readiness_Assessment_and_Gate_Criteria.md) ·
[`RL-004`](RL-004_Rollout_and_Branch_Wave_Deployment_Plan.md) ·
[`RL-005`](RL-005_Post_Implementation_Review_Standard.md) ·
[`../09_Data_Migration_and_Cutover/MG-006_Cutover_Plan_and_Runbook.md`](../09_Data_Migration_and_Cutover/MG-006_Cutover_Plan_and_Runbook.md) ·
[`../09_Data_Migration_and_Cutover/MG-007_Rollback_and_Fallback_Plan.md`](../09_Data_Migration_and_Cutover/MG-007_Rollback_and_Fallback_Plan.md) ·
[`../08_Quality_Engineering_and_Test/QA-001_Master_Test_Strategy.md`](../08_Quality_Engineering_and_Test/QA-001_Master_Test_Strategy.md) ·
[`../08_Quality_Engineering_and_Test/QA-010_Defect_Management_and_Quality_Gate_Standard.md`](../08_Quality_Engineering_and_Test/QA-010_Defect_Management_and_Quality_Gate_Standard.md)

**Workspace**
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §18.3 ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` `NFR-008`, `OPS-07` ·
`../../1000fix_ERP_Module/02_Architecture/02-02_*.md` §8 `DoD-01`…`DoD-17` ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` §4 ·
`../../project_content/12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md` ·
`../../project_content/16_Change_Management_and_Comms/CM-006_Go_Live_Announcement_Pack.md` ·
`../../project_content/17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md` ·
`../../project_content/17_Operations_Support_and_Runbooks/OP-005_Status_Page_and_Maintenance_Notice_Copy.md` ·
`../../project_content/17_Operations_Support_and_Runbooks/OP-014_Manual_Fallback_Procedure_Set.md`

**External standards** *(verified 2026-08-19)*

| Source | Edition | Used for |
|---|---|---|
| ITIL 4 — Deployment Management practice | ITIL 4, current framework | §3, §4, §6, §9 |
| ISO/IEC 20000-1:2018 **+ Amd 1:2024** | §8.5.3; amendment February 2024, no change to §8.5 | §2.1, §6, §10 |

---

## 20. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Platform Engineering with Release Management | Initial issue. Forty-eight `DPY` rules; 58-item go-live checklist; 19 standing smoke cases; 8 abort triggers; 9 per-wave profiles. Supersedes the never-written `06-06`. Supplies `OPS-07`'s missing documented procedure as the expand/contract protocol. Answers `MG-006` `Q-01` | *Superseded by 1.1 the same day* |
| **1.1** | 2026-08-19 | Platform Engineering with Release Management | **Audit corrections, `PGD-AUDIT-CAT-12`.** Category 10 was authored **concurrently with this document**, invalidating three of its positions before issue. **`RLA-13`** — §3's ten-environment reconciliation is withdrawn; **`PE-002` §4.2's twelve govern**, and this document retains only the promotion path across them, which `PE-002` §4.1 delegates to it. **`RLA-14`** — §4's *"`Recreate` is the only executable model"* and *"`NFR-008` is not achievable"* are both withdrawn; `PE-004` §8.1's per-component strategy is adopted and `NFR-008` is restated as **specified, not demonstrated**, with condition 3 (`PE-004-F-02`) named as the gap. **`RLA-15`** — §8.3 read *"58 items across **8** sections"* against nine section headings and a §1.2 that said nine; recounted to **59 items across 9 sections** with the addition of `E-07`. Adds `DPY-09a` (cron deployments outside finance freezes) and records the independent agreement between §5's three-release derivation and `PE-004-D-02`'s | *Pending — `GV-001` `CC-01`* |

---

*`RL-002` · Category 12 · Rule space `DPY` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
