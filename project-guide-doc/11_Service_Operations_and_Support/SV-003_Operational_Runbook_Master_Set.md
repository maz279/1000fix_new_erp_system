---
id: SV-003
title: Operational Runbook Master Set
category: 11 — Service Operations & Support
code: SV
project: 1000FiX ERP System v2.0
version: 1.2
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Head of IT Service Management
approver: Chief Technology Officer
standards_basis: >
  ISO/IEC 20000-1:2018 + Amd 1:2024 §8.5.2 service design and transition, §8.6.1 incident
  management, §8.7.3 service continuity · 05-06 §7 NFR-091 (per-module operational runbook) and
  OPS-01…OPS-08 operability standards · Google SRE practice — runbooks, game days and the rule
  that an untested procedure is a hypothesis · TPL_Runbook.md (project_content), eleven sections,
  extended to twelve here with a stated reason
traces_to: >
  PGD-000 SV-003 row (◐ OP-007…011) · SV-001 §5.2 (21 services), §6.5 (NFR-091 ruled), §6.6
  (G3-on-build), §9.2 (the dependency register) · AUDIT-017 OP-07, OP-08, OP-16, OP-23, OP-25 ·
  05-06 §7 NFR-091, NFR-092, OPS-01…08 · 02-05 §9 per-module definition of done ·
  OP-007…OP-012, OP-014 · PE-001, PE-002, PE-005, PE-006
depends_on: >
  SV-001 (this category) · SV-002 (this category) · SV-004 (this category) · SV-006 (this category) ·
  PE-001…PE-009 (ALL NINE ISSUED — re-enumerated 2026-08-19 02:15 (+06); PE-007, PE-008 and PE-009
  were issued by a concurrent session during this document's authoring window and this front matter
  is corrected accordingly — see §0)
verified_on: 2026-08-19
enumeration_timestamp: 2026-08-19 02:15 (+06) — supersedes the 01:53 enumeration used at first draft
rule_prefix: RBS — verified to return zero occurrences in identifier form across all 763 markdown files of the workspace before allocation, at 2026-08-19 02:15 (+06); re-verified against the 786-file baseline at 02:56 (+06); the candidate RBK was rejected because MG-007 owns it with 101 occurrences. Conforms to RR-002 IDC-08
priority: P1
needed_by: W2
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# SV-003 — Operational Runbook Master Set

### Category 11 · Code `SV` · Rule space `RBS` · ISO/IEC 20000-1:2018 §8.5.2, §8.6.1 · `NFR-091` · `OPS-01`…`OPS-08`

---

> **`PGD-000` states the gap this document fills:** *"`OP-007…011` provide five runbooks written as
> **content**. They reference procedures against infrastructure (`PE-001…009`) that is not yet
> designed."*
>
> Half of that is now false, which is the good news: `PE-001`…`PE-006` were issued on 2026-08-19 and
> the infrastructure the runbooks describe now exists as a design. The other half has got worse under
> examination. Mapping the five runbooks against `SV-001` §5.2's twenty-one services shows that
> **two `P0` services have no runbook at all** — the payment path and the Bangladesh-resident data
> service — and that one of them carries the platform's tightest availability objective and the
> other carries its only criminal-liability exposure.
>
> And `NFR-091` still says *"every module ships with an operational runbook"*, `P0`, against a
> register containing **zero** module runbooks. `SV-001` §6.5 ruled that `NFR-091` means what it
> says. **§5 is where that ruling is costed**, and the cost is between **17 and 26 person-weeks** —
> or between **77 and 115**, if it is done the obvious way instead of the mechanised one.

---

## 0. Baseline Movement During Authoring — Read This First

> **⚠ `PE-007`, `PE-008` and `PE-009` were issued while this document was being written**, and all
> three are prerequisites of runbook sections this document declared unsatisfiable. Re-enumerated
> **2026-08-19 02:15 (+06)**; the 01:53 claims are corrected below rather than left standing.

| Claim as drafted at 01:53 | State at 02:15 | Effect on this document |
|---|---|---|
| `PE-007` — **absent ⛔**; *"every §8 is blocked"* | **Issued.** 3-2-1-1-0 backup realisation, continuous WAL archiving, the immutable copy `BKP-3`, restore verification, failover sequence, `Z4` recovery routes, and **a drill programme** (`PE-007` §10) | §8.2's exercise schedule is no longer this document's proposal — **it aligns to `PE-007` §10**. §11 corrected |
| `PE-008` — **absent ⛔**; *"every §3 dashboard reference is unusable"* | **Issued.** Signals, correlation, eight SLOs, burn-rate alerting, **alert discipline `AD-01`…`AD-05`**, dashboards `DB-01`…`DB-03` | **`RBS-06` survives and matters more, not less** — see below. §4.3, §11 corrected |
| `PE-009` — **absent ⛔**; *"every §9 reads `BLOCKED`"* | **Issued.** `PE-009` §8 designs break-glass: trigger, issue, **announce-at-issue**, rotation, `BG-01`…`BG-06`, `BF-01` | **§6.5's worked example is corrected** — the status moves from `BLOCKED (no design)` to `BLOCKED (designed, unprovisioned)`, which is a different and better kind of blocked |
| *(not drafted)* | `PE-008` §8.5 asserts a **three-level** severity model | `RBS-10` is unchanged and now points at `SV-001` §6.7's adjudication |

> **`RBS-06` is strengthened, not weakened, by `PE-008` existing.** The rule requires every health
> check to give a command that works without the dashboard. It was written because no dashboard
> existed; it survives because `PE-008` `DB-03` puts the on-call dashboard on **one screen** and the
> observability stack is itself a service that can fail. **A health check that only works when
> monitoring works cannot diagnose monitoring.**

---

## 1. Purpose

This document is the **standard that governs every runbook in the programme, and the register of
which runbooks must exist**. It does not contain procedures. It states what a runbook is, which
ones the estate requires, who owns each, how one is proved true, how it stays true, and what
happens to it when it is wrong.

It exists because a runbook is the only document in the estate that is read under time pressure by
someone who is tired, and the failure modes of such a document are specific and predictable: it
describes a system that has changed; it assumes access the reader does not have; it is stored in
the system it exists to recover; or it has never been executed and is therefore a plan wearing a
runbook's clothes.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The **runbook standard** — twelve sections, and what each must contain (§4) |
| 2 | The **master set** — service-to-runbook coverage across all 21 services, and the gaps (§5.1–§5.3) |
| 3 | The **`NFR-091` obligation** — 67 module runbooks, sized, mechanised and sequenced (§5.4–§5.6) |
| 4 | **`G3`-on-build** — the execution ledger that lets a runbook be approved procedure by procedure (§6) |
| 5 | **Currency** — the four events that change a runbook and the deadline for each (§7) |
| 6 | **Proving** — drills, game days, restore tests, and what counts as an execution (§8) |
| 7 | The **21-row service-dependency register** `SV-001` §9.2 places here (§9) |
| 8 | **Storage and access** — the offline problem, and the printed set (§10) |
| 9 | What a runbook may **not** contain (§4.4) |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The **content** of the five existing component runbooks | [`OP-007`](../../project_content/17_Operations_Support_and_Runbooks/OP-007_Runbook_Core_ERP_Platform.md)…[`OP-011`](../../project_content/17_Operations_Support_and_Runbooks/OP-011_Runbook_Portal_and_Mobile_App_Operations.md) | They are issued, good, and governed by this standard. **`RBS-01` forbids restating a single procedure** |
| The disaster recovery playbook | [`OP-012`](../../project_content/17_Operations_Support_and_Runbooks/OP-012_Disaster_Recovery_and_Continuity_Playbook.md), and `PE-007` **(absent)** | A DR playbook is a runbook of a different kind — it invokes rather than restores. §5.2 places it in the set and stops |
| Manual business fallback at the counter | [`OP-014`](../../project_content/17_Operations_Support_and_Runbooks/OP-014_Manual_Fallback_Procedure_Set.md) | §7 of every runbook **points at** `OP-014`; it never contains a fallback |
| Severity, declaration, paging, command | `OP-013` §4.1, `SV-004`, `SV-006` | §6 of every runbook cites them |
| Backup schedules, retention, DR topology, restore realisation | `PE-007` **(absent)** | §8 of every runbook states the procedure; `PE-007` states the design it rests on |
| Alert rules, dashboards, SLIs, log retention | `PE-008` **(absent)** | §3 of every runbook cites a dashboard; `PE-008` builds it |
| Vault paths, secret rotation, break-glass credential mechanics | `PE-009` **(absent)** | §9 of every runbook describes the *procedure*; `PE-009` provides the *path* |
| The build-time definition of done for a module | `02-05` §9, [`BE-006`](../07_Build_Engineering_and_Development_Standards/BE-006_Component_Build_Specification_Standard.md) | §5.6 states the seam: a module runbook is a **release** obligation, enforced by the pipeline |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| On-call engineers | Nothing, at 02:00. **They read a runbook, not this.** This is what makes the runbook they read trustworthy |
| Service owners (`SV-001` §5.3) | The obligation they hold: their runbook's accuracy is theirs |
| Platform, Security, Integration, Data and Mobile Engineering | The standard their runbooks must meet, and the four gaps in §5.3 |
| Module development teams | §5.4–§5.6 — the appendix each of 67 modules owes, and why it is 1,000 words rather than 4,400 |
| Content Design | The relationship between this standard and the sixteen `OP-*` files it governs |
| Programme Office | The 17–26 PW in §5.5, which is not in any estimate today |
| Internal Audit | §6's execution ledger — the evidence that a documented control has ever been executed |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / section | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO/IEC 20000-1:2018 + Amd 1:2024** | §8.5.2 service design and transition — services designed with the information needed to operate them | §5's master set makes operability a design output rather than a post-go-live discovery | None |
| Same | §8.6.1 incident management — documented procedures for recording, classifying, resolving | §4.2 §6 of every runbook binds to `OP-013` §4.1 and `SV-006` | None |
| Same | §8.7.3 service continuity — plans, tested at planned intervals | §8's drill schedule; **`NFR-051` requires twice-yearly failover and none is scheduled** (§11) | Conformance blocked upstream, stated |
| **`05-06` §7 `NFR-091`** | *"Every module ships with an operational runbook"* — `P0` | **Adopted literally** per `SV-001` `SV-001-D-03`. §5.4 sizes it; §5.6 sequences it | **No departure.** The alternative reading — that component runbooks discharge it — was considered and rejected in `SV-001` §6.5 |
| **`05-06` §7 `OPS-01`…`OPS-08`** | Deployments reversible · configuration versioned · **every alert has a runbook entry** · structured logs, no personal data · every job reports its outcome · feature flags · forward-only migrations · monthly capacity review | §4.2 maps each of the eight to the runbook section that evidences it (§4.3) | None |
| **Google SRE practice** | A runbook is proved by execution; game days; toil reduction | §6's execution ledger and §8's drill schedule | **Departure: no error-budget-driven toil freeze.** `SV-001-D-05` |
| **`TPL_Runbook.md`** | Eleven sections (project_content template) | **Extended to twelve.** §4.1 states which section is added and why | **Declared departure** — a twelfth section, *Verification and Execution Ledger*, is required by `SV-001` `SMF-19`. The existing eleven are unchanged and unreordered so the six issued runbooks remain conformant |

> **`RBS-02`. The eleven sections of `TPL_Runbook` are not renumbered.** `AUDIT-017` `OP-23` records
> seven files whose cross-references drifted because a section structure moved during authoring.
> The twelfth section is **appended**, never inserted.

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `OP-007`…`OP-011` | [`../../project_content/17_.../`](../../project_content/17_Operations_Support_and_Runbooks/) | **Five component runbooks, ~132 KB**, conformant to all eleven `TPL_Runbook` sections (`AUDIT-017` `E7` ✅). The reference implementations of this standard |
| `OP-012` | Same | The DR playbook — a different artefact class, placed in the set at §5.2 |
| `OP-007` §3, §5, §8 | Same | The pattern this standard generalises: 14 health checks, 14 failure modes, a 9-step restore, and a *"Last tested"* column reading **Not yet** in every row |
| `SV-001` §5.2, §6.5, §6.6, §9.2 | This category | The 21 services; the `NFR-091` ruling; `G3`-on-build; the dependency register placed here |
| `SV-002` §5.3 | This category | The RTO each runbook's §8 must achieve, per service |
| `PE-001` §9.2, §10, §11 | [`../10_.../PE-001`](../10_Infrastructure_DevOps_and_Environments/PE-001_Infrastructure_and_Network_Architecture_Design.md) | HA by tier; environment placement; **`HB-02` immutable infrastructure — *"a host that has been logged into for a change is rebuilt"*** |
| `PE-002` §5 | [`../10_.../PE-002`](../10_Infrastructure_DevOps_and_Environments/PE-002_Environment_Strategy_and_Specification.md) | **Twelve environments.** A runbook that does not say which environment it applies to applies to all of them |
| `PE-005` §5.1, §5.4, §5.5, §6.1, §10 | [`../10_.../PE-005`](../10_Infrastructure_DevOps_and_Environments/PE-005_Containerisation_and_Orchestration_Design.md) | The component inventory; two clusters; **stateful stores outside the cluster — two operational models**; node pools; the readiness contract |
| `PE-006` §7 | [`../10_.../PE-006`](../10_Infrastructure_DevOps_and_Environments/PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md) | Scaling triggers — the thresholds §3 of a runbook checks against |
| `AUDIT-017` `OP-07`, `OP-16` | [`../../project_content/_AUDIT/AUDIT-017`](../../project_content/_AUDIT/AUDIT-017_Category_17_OP_Content_Audit.md) | The 67-runbook obligation with zero delivered; the `G3` blockage; the six *"Last tested: Not yet"* files |
| `02-05` §9 | `1000fix_ERP_Module` | *"Every module ships with a README, a runbook and its OpenAPI specification"* — the second, independent statement of `NFR-091` |

### 2.3 Audit findings this document closes or contributes to

| Finding | Source | How this document acts on it |
|---|---|---|
| **`OP-07`** — 67 module runbooks required, zero registered, two readings unchosen | `AUDIT-017`, HIGH | **Closed in specification.** `SV-001` chose the reading; §5.4 sizes it at 17–26 PW, §5.5 shows the alternative costs 77–115 PW, §5.6 sequences it wave by wave and puts enforcement in the pipeline |
| **`OP-16`** — `G3` unachievable; six runbooks will be `Draft` at go-live | `AUDIT-017`, MEDIUM | **Closed.** §6's execution ledger implements `AUDIT-017` `R-06` mechanically: per-procedure execution dates, per-procedure approval, and an *unverified* marker the reader sees |
| **`OP-08`** — break-glass documented, does not exist | `AUDIT-017`, HIGH | **Contributes.** §4.2's §9 requirement plus `RBS-16` make a §9 that cites a non-existent vault path a **defect in the runbook**, not a note. §11 carries it as the blocking dependency it is |
| **`OP-23`** — section references drifted across seven files | `AUDIT-017`, LOW (fixed) | **Prevented.** `RBS-02`: sections are appended, never inserted or renumbered |
| **`OP-25`** — owner strings differ lexically from the register | `AUDIT-017`, LOW | **Contributes.** `RBS-08` requires the owner field to name the **service** (`S-nn`) and the individual, not a prose role string, which removes the comparison problem entirely |
| **`PSL-F-04`** (`SV-002`) — no observability at W1 | This category | **Contributes.** §4.2's §3 requirement is written so a health check degrades to a command an engineer can run by hand when the dashboard does not exist |
| New — **`RBS-F-01`** | This document | **Two `P0` services have no runbook**: `S-06` payment path and `S-12` resident data service (§5.3) |

### 2.4 The rule space

This document allocates **`RBS`**. Verified at **2026-08-19 01:53 (+06)**: zero occurrences in
identifier form across **763** markdown files.

> **The first candidate was rejected.** `RBK` — the obvious abbreviation for *runbook* — returns
> **101 occurrences**: it is [`MG-007`](../09_Data_Migration_and_Cutover/MG-007_Rollback_and_Fallback_Plan.md)'s rollback rule prefix. Had it been allocated here without
> checking, the estate would have gained its ninth identifier collision, in the document whose whole
> subject is procedures being correct.

---

## 3. What a Runbook Is

### 3.1 The definition

> **`RBS-03`. A runbook is the set of procedures a competent engineer who has never seen this system
> before can execute, at 02:00, without asking anyone.**

Each clause of that sentence is load-bearing:

| Clause | What it excludes |
|---|---|
| *"procedures"* | Architecture prose. A runbook that opens with three pages of design is a design document with a §5 |
| *"a competent engineer"* | It assumes engineering skill. It does not assume this system |
| *"who has never seen this system"* | Tribal knowledge. Every implicit step is a step the author knows and the reader does not |
| *"at 02:00"* | Anything requiring judgement the reader cannot make while tired. Decisions are **pre-made** and stated as authority (`OP-013` §4.8) |
| *"without asking anyone"* | Any step reading *"contact the vendor"* with no contact, ref or SLA attached |

### 3.2 The four failure modes it is written against

| Failure mode | Countered by |
|---|---|
| **It describes a system that has changed** | §7 currency rules — change-driven, incident-driven, drill-driven, review-driven updates with deadlines |
| **It assumes access the reader does not have** | §4.2's §9, and `OP-013` `RT-07` — *"an on-call engineer without production authority is a pager with no hands"* |
| **It is stored in the system it recovers** | §10's storage rule and the printed set |
| **It has never been executed** | §6's execution ledger, and `RBS-11` |

### 3.3 The distinction from four neighbours

| Artefact | Answers | Not this because |
|---|---|---|
| **Runbook** | *"It is broken. What do I do?"* | — |
| SOP (`SP-*`) | *"How is this business process performed?"* | Business audience, business hours, approval flows |
| Knowledge article (`KB`) | *"How does this work?"* | Explanatory; no execution obligation |
| Manual fallback (`OP-014`) | *"The system is down. How does the branch keep trading?"* | Executed by a cashier, in Bengali, on paper |
| Playbook (`OP-012`) | *"Is this a disaster, and do we invoke?"* | A decision procedure with a declaration authority, not a restoration procedure |

---

## 4. The Runbook Standard

### 4.1 Twelve sections

`TPL_Runbook.md` defines eleven and all six existing runbooks conform to all eleven
(`AUDIT-017` `E7` ✅). This standard **appends a twelfth** and changes nothing else.

| § | Section | Purpose | Mandatory |
|:--:|---|---|:--:|
| 1 | What this system does | Blast radius in one paragraph: what stops, for whom | ✔ |
| 2 | Architecture summary | Components, dependencies, and **the one fact that governs recovery** | ✔ |
| 3 | Health checks | Command or dashboard, and *"healthy looks like"* | ✔ |
| 4 | Routine operations | Steps, risk, approval class | ✔ |
| 5 | Common failure modes | Symptom → likely cause → diagnosis → fix → **escalate if** | ✔ |
| 6 | Incident response | Per severity: response time, first actions, who to notify, comms template | ✔ |
| 7 | Manual fallback | **Pointer to `OP-014`**, plus tolerable duration and reconciliation on recovery | ✔ |
| 8 | Backup and recovery | RPO, RTO, procedure, **last tested** | ✔ |
| 9 | Break-glass access | Who authorises, procedure, audit record | ✔ |
| 10 | Change and rollback | Change type, approval, rollback procedure, verification | ✔ |
| 11 | Post-incident | The standing review questions this runbook must answer | ✔ |
| **12** | **Verification and execution ledger** | **Per procedure: first executed, last executed, by whom, environment, outcome** | ✔ **New** |

> **Why the twelfth exists.** `AUDIT-017` `OP-16` found six runbooks whose §8 *"Last tested"* column
> reads **Not yet** in every row, and correctly identified that they cannot reach `Approved` because
> `G3` requires a system that will not exist until W8. `SV-001` `SMF-19` ruled that `G3` is granted
> **per procedure**. §12 is the ledger that makes per-procedure approval computable rather than a
> matter of opinion.

### 4.2 What each section must contain

| § | Requirement | Rule |
|:--:|---|---|
| 1 | Names the **service identifier(s)** from `SV-001` §5.2 that this runbook covers, and what stops for whom | `RBS-04` |
| 2 | States dependencies **in both directions** and names *"the one architectural fact that governs every recovery procedure"* — `OP-007` §2's pattern | `RBS-05` |
| 3 | Every check gives **both** a dashboard reference **and** a command that works without the dashboard | **`RBS-06`** |
| 4 | Every operation carries a risk rating and its `SP-031` change class (standard / normal / emergency) | `RBS-07` |
| 5 | Every failure mode carries an explicit **"escalate if"** with a threshold, never *"if it seems serious"* | `RBS-09` |
| 6 | Cites `OP-013` §4.1 for severity. **Does not define severity.** Names the `OP-004` template numbers | `RBS-10` |
| 7 | Points at the `OP-014` `FB-nn` procedure, states the tolerable duration, states reconciliation on recovery | — |
| 8 | RPO, RTO **matching the `SV-002` §5.3 objective for the service**, the procedure, and the last-tested date from §12 | `RBS-12` |
| 9 | Names the authoriser, the two-person rule, the audit record. **If the vault path does not exist, that is stated in the section, not omitted** | **`RBS-16`** |
| 10 | States the rollback decision **before** deployment (`OP-007` `CR-01`'s pattern) and the feature-flag alternative | — |
| 11 | The standing review questions, answered after every incident touching this service | — |
| 12 | One row per procedure in §4, §8 and §9: id, first executed, last executed, by whom, environment, outcome, **status** | `RBS-13` |

> **`RBS-06` is the rule most often broken and most expensive when it is.** A health check expressed
> only as *"Grafana → ERP Core → Worker utilisation"* is unusable in the incident where observability
> is what failed — and `PE-008` does not exist, so at W1 **every** dashboard reference is unusable.
> `OP-007` §3 already does this correctly: it gives `SELECT now()-pg_last_xact_replay_timestamp();`
> next to the dashboard. That is the pattern.

### 4.3 `OPS-01`…`OPS-08` — where each is evidenced

`05-06` §7's eight operability standards are not a separate checklist. Each is evidenced by a
runbook section, and a runbook that omits the section omits the evidence.

| Standard | Evidenced in |
|---|---|
| `OPS-01` deployments automated, repeatable, **reversible** | §10 rollback procedure |
| `OPS-02` configuration versioned, promoted, never hand-edited in production | §4 routine operations; `PE-003` |
| **`OPS-03` every alert has a runbook entry; alerts without actions are removed** | §5 failure modes ↔ `NT-021` alert set; **`RBS-14`** |
| `OPS-04` structured logs, consistent levels, **no personal data** | §3 health checks; §5 diagnosis steps |
| `OPS-05` every scheduled job reports success, failure and duration; **silent failure is a defect** | §3 scheduled-action checks; §5 |
| `OPS-06` feature flags allow any new capability to be disabled without a deployment | §10 `CR-02` pattern |
| `OPS-07` migrations forward-only, tested at production scale, **reversible by a documented procedure** | §10, and the documented procedure lives in §4 |
| `OPS-08` capacity reviewed monthly against growth | §3 thresholds ↔ `PE-006` §7 scaling triggers |

> **`RBS-14`. An alert with no runbook entry is a defect in the alert, and an alert entry with no
> alert is a defect in the runbook.** The correspondence is checked in both directions, quarterly,
> by the service owner. `OP-013` §4.4 step 7 states the first half; this states the second, which is
> the half that produces runbooks describing failure modes that can no longer be detected.

### 4.4 What a runbook may not contain

| Prohibited | Why | Rule |
|---|---|---|
| A severity definition | `OP-013` §4.1 owns it; `AUDIT-017` `OP-04` is what happens otherwise | `RBS-10` |
| A copy of a fallback procedure | `OP-014` owns it, in Bengali, printed | — |
| A credential, token, connection string or key | `NFR-062`. Runbooks are widely readable **and printed** (§10) | **`RBS-15`** |
| Personal data, including in an example | `NFR-090` §6.3 purpose limitation; `OPS-04` | `RBS-15` |
| A step whose authority is unstated | The reader either has the authority or must know who does (`OP-013` §4.8) | `RBS-09` |
| *"Contact the vendor"* with no name, reference or contract SLA | `RBS-03`'s *"without asking anyone"* | — |
| A dashboard-only health check | `RBS-06` | `RBS-06` |
| An untested procedure presented as tested | §6; this is the whole point of §12 | `RBS-11` |

---

## 5. The Master Set

### 5.1 Method

Every service in `SV-001` §5.2 must be covered by exactly one **primary** runbook, and may be
referenced by others. Coverage was determined by reading §1 and §2 of each of the six issued
`OP-*` runbooks and mapping the components they name against the service definitions.

### 5.2 Coverage — component runbooks

| Runbook | Primary for | Also covers | State |
|---|---|---|:--:|
| [`OP-007`](../../project_content/17_Operations_Support_and_Runbooks/OP-007_Runbook_Core_ERP_Platform.md) Core ERP Platform | **`S-01`**, **`S-02`**, **`S-05`**, `S-09` | Nginx, PgBouncer, Redis, K3s, filestore/database point-in-time consistency | ✅ Issued · Draft |
| [`OP-008`](../../project_content/17_Operations_Support_and_Runbooks/OP-008_Runbook_Integration_and_Event_Platform.md) Integration and Event Platform | **`S-10`**, `S-11`, `S-18` | Dead letters, replay, schema change, circuit breakers | ✅ Issued · Draft |
| [`OP-009`](../../project_content/17_Operations_Support_and_Runbooks/OP-009_Runbook_Identity_and_Access.md) Identity and Access | **`S-03`** | Keycloak, break-glass, the login-screen notice | ✅ Issued · Draft |
| [`OP-010`](../../project_content/17_Operations_Support_and_Runbooks/OP-010_Runbook_Data_Platform_and_Warehouse.md) Data Platform and Warehouse | **`S-15`** | ClickHouse, TimescaleDB, pipeline false-green | ✅ Issued · Draft |
| [`OP-011`](../../project_content/17_Operations_Support_and_Runbooks/OP-011_Runbook_Portal_and_Mobile_App_Operations.md) Portal and Mobile Operations | **`S-07`**, **`S-08`**, `S-13`, `S-14`, `S-16`, `S-17`, `S-20`, `S-21` | Sync conflict, rollout halt (`BG-20`), offline behaviour | ✅ Issued · Draft |
| [`OP-012`](../../project_content/17_Operations_Support_and_Runbooks/OP-012_Disaster_Recovery_and_Continuity_Playbook.md) DR and Continuity Playbook | *(cross-cutting)* | Declaration, crisis roles, site loss, the residency constraint | ✅ Issued · Draft |

### 5.3 The gaps — four services, two of them `P0`

| Service | Criticality | SLO (`SV-002` §5.3) | Covered by | Gap |
|---|:--:|:--:|---|---|
| **`S-06` Payment path** | **P0** | **99.95% platform-side** — the tightest objective in the estate | `OP-008` covers integrations *generally*; `OP-007` §7 mentions invoicing fallback | **⛔ No runbook.** No procedure for gateway failover, for a stuck settlement, for a double-charge, for reconciling a partial capture, or for the `INT-003` single-acquirer outage `IN-007` §9.3 identifies |
| **`S-12` Resident data service (`BD-R`)** | **P0** | 99.9%, **zero cross-border transfers** | `OP-012` §4.3 states the recovery *constraint*; `PE-001` §3.3 designs the site | **⛔ No runbook.** A separately-credentialled cluster in a different jurisdiction (`PE-005` `CL-04`, `CL-05`) with **no start/stop, health-check, failover or restore procedure** — and `AUDIT-017` `OP-01` (CRITICAL) says the lawful recovery route does not exist |
| **`S-04` Gateway and ingress** | P0 | 99.95% | `OP-007` §2 lists Nginx; `OP-008` covers API failures | ◐ **Partial.** Kong itself — routes, plugins, rate limits, certificate rotation at the edge, `PE-001` §6.2's two-AZ ingress — has no owning section |
| **`S-19` Contact centre (W4)** | P1 | 99.9% | — | ⬜ **None.** Telephony `INT-015`, agent desktop, call recording. Needed by W4 |

> **`RBS-F-01`. Two `P0` services have no runbook: the payment path and the resident data service.**
> They are not obscure. `S-06` carries the platform's tightest availability objective and every taka
> the business collects; `S-12` carries the only obligation in the estate whose breach is a
> **regulatory act** (`NFR-086b`). Both were missed because the five existing runbooks were scoped by
> **infrastructure component** — core, integration, identity, data, portals — and neither payments
> nor residency is a component. **They are services that cut across components**, which is exactly the
> class of thing a component-shaped inventory does not see.
>
> This is the strongest available argument for `SV-001` `SMF-05` — that the **service** list, not the
> component list, is the index for everything downstream.

**Four runbooks are therefore commissioned:**

| New runbook | Covers | Priority | Needed by | Owner |
|---|---|:--:|:--:|---|
| **`RB-PAY`** Payment and Settlement Path | `S-06` | **P0** | **W1** | Integration Engineering |
| **`RB-RES`** Resident Data Service and `BD-R` | `S-12` | **P0** | **W1** | Security Engineering |
| **`RB-GW`** Gateway, Ingress and Edge | `S-04` | **P0** | **W1** | Platform Engineering |
| **`RB-CC`** Contact Centre Platform | `S-19` | P1 | W4 | Contact Centre + Integration |

> **`RBS-17`. The four new runbooks are authored to this standard in `project_content` Category 17,
> as `OP-017`…`OP-020`, not in this repository.** A runbook is content; this document is the
> standard that governs it. Splitting the runbook set across two repositories to satisfy an
> authorship convention would be the `AF-11` defect class. Registered as a Content Master Index
> change request, `RBS-Q-01`.

### 5.4 `NFR-091` — the sixty-seven module runbooks

`SV-001` `SV-001-D-03` ruled that `NFR-091` means what it says. This is what that costs.

**Derivation — the observed rate.** From `AUDIT-017` §7 and `PGD-000` §0.5, both enumerated:

| Quantity | Value | Source |
|---|---:|---|
| Category 17 files | 16 | `AUDIT-017` `A1` |
| Category 17 words | **70,706** | `AUDIT-017` §7 |
| **Mean words per content file** | **4,419** | 70,706 ÷ 16 |
| Content estate effort estimate | **520–775 PW** | `AUDIT-017` `AF-09`, `PGD-000` §2.1 |
| Registered content files | 452 | `AUDIT-017` `A2` |
| **Mean PW per content file** | **1.15 – 1.71 PW** | 520 ÷ 452 and 775 ÷ 452 |

**Two mechanisms, two costs:**

| Mechanism | Words each | PW each | **× 67 modules** |
|---|---:|---:|---:|
| **(a) Standalone module runbook** — a full twelve-section document per module | ~4,400 | 1.15 – 1.71 | **77 – 115 PW** |
| **(b) Templated appendix** — a short section appended to the component runbook that already covers the module's substrate | ~1,000 | 0.26 – 0.39 | **17 – 26 PW** |

> **`SV-003-D-01`. Mechanism (b) is adopted.** A module runbook is a **templated appendix** to the
> component runbook covering its substrate, not a standalone document.

**Why (b) is not a shortcut.** Of the twelve sections, **eight are properties of the substrate, not
of the module**: architecture, health checks, break-glass, backup and recovery, change and
rollback, post-incident, manual fallback routing, and incident response. A per-module copy of those
eight would be 67 copies of the same text, diverging from the day it is written — and a runbook that
disagrees with another runbook about how to restore the same database is worse than one runbook.

**What a module appendix actually contains — the four module-specific things:**

| # | Content | Why it cannot be inherited |
|---:|---|---|
| 1 | **What stops in the business** when this module fails, and which of `SV-001` §5.2's services it degrades | Blast radius is a module property |
| 2 | **The module's own failure modes** — its scheduled jobs, its queues, its integrations, its known stuck states | `M23`'s CAPA queue and `M31`'s dispatch board fail differently |
| 3 | **Its data-integrity checks** — the query that proves this module's records are consistent after an incident | `DI-02` reconcilability is per-module |
| 4 | **Its statutory or financial obligations** and their deadlines — what must still be produced today if the module is down | The reason a Mushak module and a marketplace module are not interchangeable |

Everything else is one line: *"Substrate: `OP-007`. All procedures in §2, §3, §8, §9, §10 of that
runbook apply unchanged."*

### 5.5 The saving, stated

| | Standalone | Appendix | Difference |
|---|---:|---:|---:|
| Effort | 77 – 115 PW | **17 – 26 PW** | **60 – 89 PW saved** |
| Documents to keep current | 67 + 10 | **10, plus 67 short appendices** | — |
| Places the restore procedure is written | **68** | **1** | The one that matters |

> **`RBS-F-02`. Neither figure is in any estimate the programme holds.** `NFR-091` is a `P0`
> requirement stated twice (`05-06` §7, `02-05` §9), and **17–26 PW of obligation sits outside both
> the 1,513 PW build estimate and the 520–775 PW content estimate.** `AUDIT-017` `OP-07` called it
> *"an unregistered content obligation"*; this is what it weighs.

### 5.6 Sequencing and enforcement

> **`RBS-18`. A module's runbook appendix is a release obligation, not a documentation task.** It is
> produced in the wave the module is delivered, and the `PE-004` pipeline **blocks the release of a
> module whose appendix is absent**, in the same gate that already checks the README and the OpenAPI
> specification (`02-05` §9).

| Wave | Modules delivered | Appendices owed | Cumulative |
|:--:|:--:|:--:|:--:|
| W1 | Core platform, `M29`, `M30`, `M28`, `M01`, `M05`, `M64` and the W1 set | Per `AR-006` build sequence | — |
| W2–W5 | Progressive | One per module, in-wave | — |
| W6 | `M66`, `M06`, native apps | One per module | — |
| W7–W9 | Marketplace, partner, multi-entity | One per module | **67** |

**Enforcement is mechanical, not editorial.** A gate that depends on someone noticing is a gate that
fails in the wave everyone is busy, which is every wave.

---

## 6. `G3`-on-Build — The Execution Ledger

### 6.1 The problem, restated

`AUDIT-017` `OP-16`: all sixteen `OP` files are `Draft`; thirteen are Class C and three Class D, and
both classes make **`G3` Technical mandatory** — *"does it match what the system actually does, at
the pinned release?"* (`CG-007` §2.1). **The system is delivered from W1 to W8.** Every command,
threshold, dashboard name and procedure in the six runbooks is unverifiable at authoring time, and
each file says so in its header rather than implying a verification it has not had — which is
correct, and leaves six runbooks at `Draft` on the night they are first needed.

### 6.2 The mechanism

> **`RBS-11`. A procedure is `Verified` when it has been executed against a real environment and its
> outcome recorded. A runbook is `Approved` when every `P0` procedure it contains is `Verified`.
> Until then it is `Draft`, and every unverified procedure displays as **UNVERIFIED** to the reader.**

**Section 12 — the ledger format:**

```
12. VERIFICATION AND EXECUTION LEDGER                    Runbook: ______  Service(s): S-__

  Proc  Procedure                        First exec   Last exec   By    Env        Outcome   Status
  ----  -------------------------------  -----------  ----------  ----  ---------  --------  ----------
  4.1   Rolling restart of app nodes      2026-11-04   2027-02-12  role  staging→prod  pass    VERIFIED
  8.1   PostgreSQL point-in-time restore  2026-11-18   2027-01-20  role  dr           pass    VERIFIED
  8.3   Filestore restore to DB timestamp  —            —          —     —            —       UNVERIFIED
  9.1   Break-glass — vault path          —            —          —     —            —       BLOCKED ⛔

  Status:  VERIFIED · UNVERIFIED (never executed) · STALE (>N months, §6.4) · BLOCKED (cannot be
           executed because a prerequisite does not exist — the prerequisite is named)
  Gate G3 granted for this runbook when every P0 procedure reads VERIFIED.   Granted: ______
```

### 6.3 What counts as an execution

| Counts | Does not count |
|---|---|
| Executed in **`prod`** during real operations or a planned exercise | Read through in a meeting |
| Executed in **`staging`** or **`dr`**, which `PE-002` holds at production parity | Executed in `dev`, `sit` or `local` |
| Executed during a **drill or game day** (§8) | Executed by its own author on the day they wrote it, alone |
| Executed during a **real incident**, recorded afterwards from the `OP-016` timeline | Assumed to have worked because the service recovered |

> **`RBS-19`. A procedure executed during a real incident is recorded in the ledger from the
> incident timeline, not from memory.** `OP-016` §4.3 already requires the Scribe's timeline; §10 of
> its report template already requires runbook changes within 2 working days. This adds the ledger
> row to the same two-day deadline.

### 6.4 Staleness

| Procedure class | Re-execution interval | If exceeded |
|---|:--:|---|
| **Restore from backup** (§8) | **Weekly, automated** (`NFR-052`) | `Sev2` in its own right — `OP-007` §8 already states this |
| **DR failover** (`OP-012`) | **Twice yearly** (`NFR-051`) | `SV-006` §9; and the RAG status for DR readiness is **red** until the first one runs |
| Break-glass (§9) | **Quarterly** (`OP-009` `BG-10`) | Security escalation |
| Manual fallback (`OP-014`) | **Per wave**, at each branch tranche | `IP-09`/`NFR-050` compliance is documentary only until then |
| Routine operations (§4) | 6 months | Marked **STALE**; re-executed at the next opportunity |
| Failure-mode procedures (§5) | 12 months, or on any architecture change | Marked **STALE** |

### 6.5 `BLOCKED` — the status that matters most

> **`RBS-16`. A procedure whose prerequisite does not exist is marked `BLOCKED` and names the
> prerequisite. It is never marked `UNVERIFIED`, and it is never omitted.**

`OP-009` §9 and `OP-007` §9 describe a break-glass capability with five components — a vault
break-glass path, a sealed offline credential envelope in the head-office safe, two named
signatories, quarterly testing and immediate rotation after use. **`AUDIT-017` `OP-08`: none of it
exists.** Under this standard those procedures read:

`9.1 Break-glass — vault path ......... BLOCKED ⛔ (PE-009 §8 designed; vault path not provisioned)`

> **Corrected at v1.1 (§0).** The first draft of this line read *"`PE-009` absent"*. `PE-009` was
> issued during authoring and its §8 designs the procedure in full, including `BF-01` — *"break-glass
> must not depend on the system being available"* — which is the rule that makes it usable in the
> identity outage it exists for. **The status is still `BLOCKED`, and the parenthesis is the whole
> point of `RBS-16`**: a blocked row names what is missing, and what is missing changed from *a
> design* to *a purchase order and an afternoon in the head-office safe*.

**The difference between `UNVERIFIED` and `BLOCKED` is the difference between "we have not got to it"
and "it cannot be done".** The first is a schedule item. The second is `AUDIT-017` `R-07` — *the
cheapest high-severity remediation available* — and it belongs in the monthly service report under
`SMF-25`, not in a runbook nobody counts.

---

## 7. Currency

### 7.1 The four events that change a runbook

| Event | Deadline | Owner | Rule |
|---|:--:|---|---|
| **An incident found the runbook wrong or incomplete** | **2 working days** | Incident Commander → service owner | `OP-016` §4.6 item 10 already requires it; `RBS-20` binds the ledger row to the same deadline |
| **A change altered the system the runbook describes** | **Before the change closes** | Change owner | **`RBS-21`** — the change is not complete while its runbook is wrong |
| **A drill or game day found a gap** | 5 working days | Exercise lead | §8.4 |
| **A scheduled review** | Per §6.4's staleness intervals | Service owner | — |

> **`RBS-21` is the one that keeps runbooks true.** `SP-031` §5.3 step 21 already requires the
> configuration record to be updated as part of the change; this extends that step to the runbook.
> **A change record cannot be closed while a procedure it invalidated still reads `VERIFIED`** — the
> ledger row moves to `STALE` automatically and the change owner clears it.

### 7.2 The rule about the author

> **`RBS-22`. The engineer who executed a procedure and found it wrong corrects it, then and there,
> and does not raise a ticket for someone else to correct it.** A correction routed through a
> backlog is a correction that arrives after the next incident. The service owner reviews the
> correction; they do not gate it.

### 7.3 Version and provenance

| Requirement | Detail |
|---|---|
| Every runbook carries the **release it was last verified against** | `RL-001` §6 version form |
| Every procedure change is a **content change** under `CG-006`, and appears in the runbook's change log | — |
| **The printed set (§10) carries its print date and the ledger status at that date** | A printed runbook is a snapshot and must announce itself as one |

---

## 8. Proving — Drills, Game Days and Tests

### 8.1 Why this section is not optional

`OP-012` `HC-01` requires the DR readiness RAG status to be reported monthly to the Steering
Committee, and `AUDIT-017` `OP-02` records that the honest status is **red**: no `dr` environment,
no separate-failure-domain WAL archiving, no out-of-account immutable backup, **and no exercise
scheduled anywhere in `06-01`**.

> **`RBS-23`. An untested recovery procedure is a hypothesis about a system nobody has observed
> under the conditions the procedure exists for.** `OP-007` §8 already states the corollary — *"a
> backup that has not been restored is not a backup"* — and this generalises it to every §8 and §9
> procedure in the set.

### 8.2 The exercise schedule

| Exercise | Frequency | Scope | Environment | Mandated by |
|---|:--:|---|:--:|---|
| **Automated restore test** | **Weekly** | Row counts, control-table checksum, an attachment fetch, a document render | Isolated | **`NFR-052`** |
| **Full DR failover** | **Twice yearly, documented** | Site loss; `RGN-P` → `RGN-S`; `BD-R` standby | `dr` | **`NFR-051`** |
| **Manual fallback drill** | **Per wave, per branch tranche** | `OP-014` at the counter, in Bengali, on paper | Branch | `NFR-050`, `IP-09` |
| **Out-of-band communication drill** | Quarterly | `OP-013` §4.10 tiers 2 and 3; **target ≥ 90% of branches acknowledging within 30 minutes** | Real | `OP-013` `OB-03` |
| **Break-glass test** | Quarterly | Vault path, sealed envelope, two signatories, rotation after | `staging` then `prod` | `OP-009` `BG-10` |
| **Paging test page** | **Weekly** | A scheduled test page that must be acknowledged | Real | `OP-013` §4.4 step 8; `SV-004` |
| **Game day** | **Quarterly** | One unannounced-to-the-responder failure injected in `staging`, worked end to end | `staging` | §8.3 |

### 8.3 Game days — what one is here

| Attribute | Value |
|---|---|
| Duration | Half a day |
| Environment | **`staging`**, which `PE-002` holds at production parity and `PE-005` §5.4 gives an HA control plane *"because it rehearses production"* |
| Scenario | One failure from a runbook's §5, chosen by the exercise lead, **not disclosed to the responder** |
| Responder | The on-call primary who would actually be paged |
| Observers | Service owner, a scribe, the Head of ITSM |
| Success | **Not "did they fix it".** Whether the runbook got them there, and where it did not |
| Output | Ledger rows, runbook corrections within 5 working days, and one `OP-016`-format finding set |

> **`RBS-24`. The measure of a game day is the number of runbook corrections it produces.** A game
> day producing zero corrections either tested something already proven or was not hard enough, and
> either way the exercise lead says which.

### 8.4 What a drill produces

| Output | Goes to |
|---|---|
| Ledger rows (§6) | The runbook's §12 |
| Runbook corrections | The runbook, within 5 working days (§7.1) |
| A finding where the gap was organisational, not technical | `OP-016` contributing-factor tags — `access-gap`, `authority-gap`, `runbook-gap`, `single-person` |
| A `BLOCKED` row where a prerequisite is absent | The monthly service report, `SMF-25` |
| Evidence for `NFR-051`/`NFR-052`/`NFR-050` | Gate evidence (`GV-009`), and `RL-003` go-live readiness |

---

## 9. The Service Dependency Register

`SV-001` §9.2 rules that a two-level, 21-row service-dependency register is maintained from W1, by
hand, updated inside the change record, and **is not called a CMDB**. It lives here because the
people who maintain runbooks are the people who know the dependencies.

### 9.1 The register

Depth is **two levels**, following `M66` `T-06`. *Depends on* means "if that is down, this is
degraded or down".

| Service | Depends on (level 1) | Depended on by | Env | Crit | Runbook |
|---|---|---|:--:|:--:|---|
| `S-01` ERP core | `S-02`, `S-03`, `S-04`, `S-05` | `S-07`…`S-21`, all internal | prod | P0 | `OP-007` |
| `S-02` System of record | *(storage, `BD-R` link for `S-12` writes)* | `S-01`, `S-15`, `S-06`, all | prod | P0 | `OP-007` |
| `S-03` Identity | `S-02` | **Every service** | prod | P0 | `OP-009` |
| `S-04` Gateway/ingress | *(DNS, TLS, `Z0` edge)* | `S-06`, `S-07`, `S-08`, `S-10`, `S-13`…`S-21` | prod | P0 | **⛔ `RB-GW`** |
| `S-05` Filestore | *(object storage)* | `S-01`, `S-07`, `S-08`, `S-15` | prod | P0 | `OP-007` |
| `S-06` Payment path | `S-01`, `S-04`, `S-10`, **`INT-003` acquirer**, MFS | `S-07`, `S-13`, `S-16`, finance | prod | P0 | **⛔ `RB-PAY`** |
| `S-07` Customer portal | `S-01`, `S-03`, `S-04`, `S-06` | Consumers | prod | P0 | `OP-011` |
| `S-08` Technician mobile | `S-01`, `S-03`, `S-04`, `S-05` | Field operations | prod | P0 | `OP-011` |
| `S-09` Admin portal | `S-01`, `S-03`, `S-04` | All staff | prod | P0 | `OP-007` |
| `S-10` Integration/events | `S-01`, `S-04`, event bus | `S-06`, `S-11`, `S-15`, `S-18` | prod | P0 | `OP-008` |
| `S-11` Notifications | `S-10`, SMS/email/WhatsApp providers | Every population | prod | P1 | `OP-008` |
| `S-12` Resident data | `S-02`, **`BD-R` cluster and facility** | `S-01`, compliance | prod/`BD-R` | P0 | **⛔ `RB-RES`** |
| `S-13` Corporate portal | `S-01`, `S-03`, `S-04` | Corporate clients | prod | P1 | `OP-011` |
| `S-14` Vendor portal | `S-01`, `S-03`, `S-04` | Vendors | prod | P2 | `OP-011` |
| `S-15` Analytics/BI | `S-02`, `S-05`, `S-10` | Management, finance | prod | P1 | `OP-010` |
| `S-16` Marketplace (W7) | `S-01`, `S-03`, `S-04`, `S-06` | Sellers | prod | P1 | `OP-011` |
| `S-17` Brand portal | `S-01`, `S-03`, `S-04` | Brand partners | prod | P2 | `OP-011` |
| `S-18` Logistics | `S-01`, `S-04`, `S-10`, couriers | Warehouse, couriers | prod | P1 | `OP-008` |
| `S-19` Contact centre (W4) | `S-01`, `S-03`, `S-04`, `INT-015` | Agents, consumers | prod | P1 | **⬜ `RB-CC`** |
| `S-20` Quality (W5) | `S-01`, `S-03`, `S-04` | Quality function | prod | P2 | `OP-011` |
| `S-21` Partner (W7) | `S-01`, `S-03`, `S-04` | Partners | prod | P2 | `OP-011` |

### 9.2 What the register is for, in one sentence each

| Question asked during | Answered by |
|---|---|
| An incident — *"what else is affected?"* | The **depended-on-by** column, which is why it is a column and not an inference |
| A change — *"what am I risking?"* | The **depends-on** column, checked at `SP-031` §5.3 step 14 |
| A `Sev1` — *"who else do I page?"* | Owner + the depended-on-by set (`SV-004` §6) |
| A DR decision — *"what is the recovery order?"* | Topological order of the depends-on graph: `S-02` → `S-03` → `S-04` → `S-01` → the rest |

> **`RBS-25`. Three rows carry `⛔` in the runbook column, and one carries `⬜`.** The register is
> useful the moment it exists precisely because it makes that visible in a way five well-written
> component runbooks did not.

### 9.3 Maintenance

| Rule | Detail |
|---|---|
| `RBS-26` | Updated **inside the change record** (`SP-031` §5.3 step 21), never as a separate task |
| `RBS-27` | A row untouched for **two quarters** is marked **unverified**, following `M66` `BRU-ITS-18` |
| `RBS-28` | **Depth stays at two.** A third level is not added; `M66` `T-06`'s reason applies with more force to a hand-maintained table |
| — | Superseded at W6 by `M66` `FR-ITS-029`; these 21 rows seed its service mapping |

---

## 10. Storage, Access and the Offline Problem

### 10.1 The failure this section exists for

> **`RBS-29`. A runbook stored only in the system it exists to recover is not a runbook.**

The same reasoning as `OP-013` `OB-01` — *"a tree stored only in the system it exists to survive is
not a tree"* — and it applies to more of the estate than people expect: the wiki, the ticket system,
the knowledge base and the status page are all candidates for being unavailable in the incident
where the runbook is needed.

### 10.2 The three copies

| Copy | Where | Contains | Refreshed |
|---|---|---|:--:|
| **Primary** | The documentation repository, version-controlled (`GV-011`) | Everything, current | Continuous |
| **Offline** | A generated PDF/HTML bundle on the **on-call laptop and phone**, and in object storage in a **second provider account** | All runbooks, the dependency register, the escalation ladder, the authority table | **Weekly, automated** |
| **Printed** | Head office **and every branch**, in the on-call pack | `OP-013` §4.1 severity, §4.8 authority, §4.9 handover, §4.10 out-of-band tree, `OP-014` fallback (**Bengali**), and the `P0` first-five-minutes pages | **Per wave, and on any change to those pages** |

> **`RBS-30`. The printed set is the minimum needed to start**, not the whole runbook set. A printed
> 500 KB estate is a filing cabinet nobody opens; five pages in an on-call pack are read.

### 10.3 Access

| Rule | Detail |
|---|---|
| `RBS-31` | Runbooks are readable by **everyone in engineering and support**, not restricted to the owning team. Restriction produces a second, private copy |
| `RBS-32` | **They contain no secrets** (`RBS-15`), which is what makes `RBS-31` safe |
| `RBS-33` | Every runbook is reachable **from the alert that fires** (`OPS-03`, `OP-013` §4.4 step 7). A link in a wiki index is not reachable at 02:00 |

---

## 11. Dependencies That Block This Document

| Dependency | State | What is blocked |
|---|:--:|---|
| **`PE-009` Configuration and Secrets Standard** | ✅ **Issued** *(corrected §0)* | §9 of every runbook now has a **designed** procedure to describe. The five physical components — vault path, sealed envelope, safe, signatories, test schedule — remain unprovisioned, so §9 reads `BLOCKED (designed, unprovisioned)` |
| **`PE-007` Backup, DR and Continuity Design** | ✅ **Issued** *(corrected §0)* | §8 of every runbook now has a design behind it, and `PE-007` §10 carries the drill programme §8.2 aligns to. **`NFR-052`'s weekly restore test and `NFR-051`'s failover still have no environment** |
| **`PE-008` Observability and Monitoring Design** | ✅ **Issued** *(corrected §0)* | Every §3 dashboard reference now names something designed. **`RBS-06` still binds** — a health check must work when observability does not |
| **A built environment** | Not before W1 | Every ledger row starts `UNVERIFIED`; §6 is the mechanism for clearing them progressively. **This is now the principal blocker of this document** |
| A `dr` environment | **Designed by `PE-007`; not sized, not costed, not provisioned** | The DR failover exercise; `S-12`'s recovery path. **`AUDIT-017` `OP-01` moves from *no design* to *no decision* — `PE-007` §7.5 records it as forced and unmade** |
| The 38 access profiles | Do not exist | `OP-013` `RT-07` — an on-call engineer may lack the authority to execute a procedure marked as theirs |
| Bengali counterparts for `OP-014` | Do not exist | The printed branch set (§10.2) cannot be produced in the language its readers use |

---

## 12. Governing Rules — Consolidated

| # | Rule | § |
|---|---|:--:|
| **`RBS-01`** | This standard restates **no procedure** from `OP-007`…`OP-012` | 1.1 |
| **`RBS-02`** | `TPL_Runbook`'s eleven sections are never renumbered; the twelfth is **appended** | 2.1 |
| **`RBS-03`** | A runbook is what a competent engineer who has never seen the system can execute at 02:00 without asking anyone | 3.1 |
| **`RBS-04`** | §1 names the `SV-001` §5.2 **service identifiers** the runbook covers | 4.2 |
| **`RBS-05`** | §2 states dependencies in **both directions** and names the one fact that governs recovery | 4.2 |
| **`RBS-06`** | **Every health check gives a dashboard reference *and* a command that works without it** | 4.2 |
| **`RBS-07`** | Every routine operation carries a risk rating and its `SP-031` change class | 4.2 |
| **`RBS-08`** | The owner field names the **service identifier and an individual**, never a prose role string | 2.3 |
| **`RBS-09`** | Every failure mode carries an explicit *"escalate if"* with a threshold | 4.2 |
| **`RBS-10`** | A runbook **cites** severity (`OP-013` §4.1); it never defines it | 4.2, 4.4 |
| **`RBS-11`** | A procedure is `Verified` only when executed against a real environment with its outcome recorded | 6.2 |
| **`RBS-12`** | §8's RTO **matches the `SV-002` §5.3 objective** for the service | 4.2 |
| **`RBS-13`** | §12 carries one ledger row per procedure in §4, §8 and §9 | 4.2 |
| **`RBS-14`** | **Alert ↔ runbook correspondence is checked in both directions**, quarterly | 4.3 |
| **`RBS-15`** | **No credential, key, connection string or personal data** in any runbook | 4.4 |
| **`RBS-16`** | A procedure whose prerequisite does not exist is **`BLOCKED`**, naming the prerequisite — never omitted | 6.5 |
| **`RBS-17`** | The four new runbooks are authored as content (`OP-017`…`OP-020`), governed by this standard | 5.3 |
| **`RBS-18`** | A module runbook appendix is a **release obligation**; the pipeline blocks a release without it | 5.6 |
| **`RBS-19`** | Executions during a real incident are recorded from the timeline, not from memory | 6.3 |
| **`RBS-20`** | An incident that found a runbook wrong corrects it within **2 working days** | 7.1 |
| **`RBS-21`** | **A change record cannot close while a procedure it invalidated still reads `VERIFIED`** | 7.1 |
| **`RBS-22`** | The engineer who found it wrong corrects it then and there; the owner reviews, does not gate | 7.2 |
| **`RBS-23`** | An untested recovery procedure is a hypothesis | 8.1 |
| **`RBS-24`** | A game day is measured by the **corrections it produces** | 8.3 |
| **`RBS-25`** | The dependency register's value is that it makes missing runbooks visible | 9.2 |
| **`RBS-26`** | The register is updated **inside the change record**, never separately | 9.3 |
| **`RBS-27`** | A register row untouched for two quarters is marked **unverified** | 9.3 |
| **`RBS-28`** | Register depth stays at **two levels** | 9.3 |
| **`RBS-29`** | **A runbook stored only in the system it recovers is not a runbook** | 10.1 |
| **`RBS-30`** | The printed set is the minimum needed to start, not the whole estate | 10.2 |
| **`RBS-31`** | Runbooks are readable across engineering and support, not restricted to the owning team | 10.3 |
| **`RBS-32`** | Which is safe because `RBS-15` holds | 10.3 |
| **`RBS-33`** | Every runbook is reachable **from the alert that fires** | 10.3 |

**Findings raised by this document**

| # | Finding | Severity | Owner |
|---|---|:--:|---|
| **`RBS-F-01`** | **Two `P0` services have no runbook — `S-06` payment path and `S-12` resident data service** — plus a partial gap on `S-04` and none for `S-19`. The five existing runbooks are scoped by infrastructure component, and neither payments nor residency is a component | **HIGH** | CTO |
| **`RBS-F-02`** | **17–26 PW of `NFR-091` obligation sits in no estimate** — outside both the 1,513 PW build and the 520–775 PW content figures. The unmechanised alternative is 77–115 PW | **HIGH** | Programme Office + CTO |
| **`RBS-F-03`** *(revised)* | Every §9 break-glass procedure is `BLOCKED`. **`PE-009` §8 now designs it**; none of the five physical components exists. The remediation is a vault path, an envelope, a safe, two names and a quarterly diary entry | HIGH | Security Lead |
| **`RBS-F-04`** *(revised)* | **`PE-007` §10 now specifies the drill programme**, and `NFR-051`'s twice-yearly failover is still scheduled nowhere in `06-01` against an environment that does not exist. Six runbooks carry *"Last tested: Not yet"* in every backup row | HIGH | CTO |
| **`RBS-F-05`** | The printed branch set cannot be produced in Bengali, because the four `_BN.md` counterparts do not exist and `OP-014` is `P0` | MEDIUM | Localisation Lead |

---

## 13. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| **`SV-003-D-01`** | Mechanism for the 67 module runbooks | (a) Standalone twelve-section runbook per module; (b) **templated appendix to the substrate runbook** | **(b)** | Eight of twelve sections are properties of the substrate, not the module; 67 copies would diverge from the day they were written. **60–89 PW saved and one place the restore procedure is written** | 17–26 PW enters the estimate; appendix template becomes part of `BE-006`'s per-module definition of done |
| **`SV-003-D-02`** | Template conformance | (a) Rewrite `TPL_Runbook` to twelve sections; (b) **append §12 and leave eleven unchanged** | **(b)** | `AUDIT-017` `OP-23` records seven files whose cross-references drifted when a section structure moved. The six issued runbooks stay conformant | A template change request against `project_content/_templates/TPL_Runbook.md`, additive only |
| **`SV-003-D-03`** | Where the four missing runbooks are authored | (a) In this repository as `SV-00n`; (b) **in `project_content` as `OP-017`…`OP-020`** | **(b)** | A runbook is content and belongs with the other sixteen. Splitting the set across repositories to satisfy an authorship convention is the `AF-11` defect class | A Content Master Index change request (`RBS-Q-01`); this document remains the governing standard |
| **`SV-003-D-04`** | Enforcement of the module-appendix obligation | (a) Editorial review; (b) **pipeline gate alongside README and OpenAPI** | **(b)** | `02-05` §9 already gates the other two. A gate depending on someone noticing fails in the wave everyone is busy | `PE-004` pipeline change; a release without an appendix does not ship |
| **`SV-003-D-05`** | Approval granularity | (a) Per file; (b) **per procedure, via the §12 ledger** | **(b)** | `AUDIT-017` `R-06`'s recommendation, and the only way six runbooks are not still `Draft` at go-live | `RBS-11`; `CG-007` `G3` needs an amendment to recognise per-procedure grant |

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|:--:|---|
| `RBS-Q-01` | Will the Content Master Index accept `OP-017`…`OP-020` (the four missing runbooks) as new registered content files? | Programme Content Lead | **W1** | `RBS-F-01`; two `P0` services stay unrunbooked |
| `RBS-Q-02` | Is the 17–26 PW for module appendices added to the estimate, and to which line — build or content? | Programme Office + CFO | **W1** | `NFR-091` remains a `P0` requirement nobody has resourced |
| `RBS-Q-03` | Does `CG-007` accept per-procedure `G3` grant (`SV-003-D-05`)? | Programme Content Lead | W1 | Six runbooks remain `Draft` at go-live |
| `RBS-Q-04` | **When is the first `NFR-051` DR exercise scheduled**, and against which environment? | CTO | **W2** | `RBS-F-04`; `OP-012` `HC-01`'s monthly red status |
| `RBS-Q-05` | Who owns `RB-RES` — Security Engineering or Platform Engineering — given `BD-R` is separately credentialled (`PE-005` `CL-04`)? | CTO | W1 | The `S-12` runbook has no author |
| `RBS-Q-06` | Is the weekly offline bundle (§10.2) held in a **second provider account**, and is that account funded? | CTO | W1 | `RBS-29`; the same gap as the out-of-account immutable backup (`AUDIT-017` `OP-02`) |
| `RBS-Q-07` | Are quarterly game days accepted as a standing commitment on the on-call pool, given `SMF-15`? | CTO | W2 | §8.3; and the pool is already contested by hypercare |

---

## 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every one of `SV-001` §5.2's 21 services maps to a primary runbook or is recorded as a gap | §5.2, §5.3 — 17 covered, 3 ⛔, 1 ⬜ |
| `AC-02` | The runbook standard states what each of twelve sections must contain | §4.2 |
| `AC-03` | `OPS-01`…`OPS-08` each map to the section that evidences them | §4.3 — 8 rows |
| `AC-04` | The `NFR-091` obligation is **sized from enumerated figures**, not asserted | §5.4 — derivation shown from 70,706 words / 16 files and 520–775 PW / 452 files |
| `AC-05` | A mechanism exists by which a runbook can be approved before the whole platform is built | §6; `RBS-11`; `SV-003-D-05` |
| `AC-06` | `BLOCKED` is distinguishable from `UNVERIFIED` in the ledger | §6.5 |
| `AC-07` | Every currency event has a deadline and an owner | §7.1 — 4 rows |
| `AC-08` | The exercise schedule covers every `NFR` that mandates one | §8.2 — `NFR-050`, `NFR-051`, `NFR-052`, `OB-03`, `BG-10` |
| `AC-09` | The 21-row dependency register exists with two-level depth | §9.1 |
| `AC-10` | The storage rule prevents a runbook being unavailable in the incident it addresses | §10.2 — three copies |
| `AC-11` | No procedure from an issued runbook is restated | `RBS-01`; verified at issue |
| `AC-12` | Every relative link resolves | Verified at issue |

**Definition of done.** Complete when every criterion is met, `PGD-000` is updated with a fresh
enumeration timestamp, and the approver has signed. **`AC-01` cannot be fully met by this
document** — it identifies the four gaps; closing them is four authoring tasks in `project_content`,
gated on `RBS-Q-01`.

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `SV-001` §5.2, §6.5, §6.6, §9.2 | The service index, the `NFR-091` ruling, `G3`-on-build, and the register placed here |
| Upstream | `SV-002` §5.3 | The RTO each §8 must achieve |
| Upstream | [`PE-001`](../10_Infrastructure_DevOps_and_Environments/PE-001_Infrastructure_and_Network_Architecture_Design.md), [`PE-002`](../10_Infrastructure_DevOps_and_Environments/PE-002_Environment_Strategy_and_Specification.md), [`PE-005`](../10_Infrastructure_DevOps_and_Environments/PE-005_Containerisation_and_Orchestration_Design.md), [`PE-006`](../10_Infrastructure_DevOps_and_Environments/PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md) | The estate every procedure operates on |
| Upstream ✅ | [`PE-007`](../10_Infrastructure_DevOps_and_Environments/PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md), [`PE-008`](../10_Infrastructure_DevOps_and_Environments/PE-008_Observability_and_Monitoring_Design.md), [`PE-009`](../10_Infrastructure_DevOps_and_Environments/PE-009_Configuration_and_Secrets_Management_Standard.md) | **Issued during authoring (§0).** §8, §3 and §9 of every runbook depend on one of them and all three now have designs. `PE-007` §10 owns the drill programme §8.2 aligns to |
| Downstream | `OP-007`…`OP-012` | Governed by this standard; §12 added to each |
| Downstream | **`OP-017`…`OP-020`** *(commissioned)* | The four missing runbooks |
| Downstream | 67 module appendices | `SV-003-D-01`, enforced by `PE-004` |
| Downstream | `SV-004` §6 | Paging targets read the dependency register |
| Downstream | `SV-006` §4, §9 | The runbook is what the Incident Commander directs execution of |
| Downstream | [`RL-003`](../12_Release_Deployment_and_Transition/RL-003_Go_Live_Readiness_Assessment_and_Gate_Criteria.md) **(issued)** | Runbook ledger status is go-live readiness evidence. *(Corrected at v1.1 — this row read "absent" and linked to a directory; `RL-003` was issued during authoring, §0.)* |
| Lateral | [`BE-006`](../07_Build_Engineering_and_Development_Standards/BE-006_Component_Build_Specification_Standard.md), [`PE-004`](../10_Infrastructure_DevOps_and_Environments/PE-004_CI_CD_Pipeline_Design_Specification.md) | Where the module-appendix gate is implemented |
| Lateral | `project_content/_templates/TPL_Runbook.md` | Additive change request, `SV-003-D-02` |

---

## 17. References

**Within this repository**
[`PGD-000`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
`SV-001`, `SV-002`, `SV-004`, `SV-005`, `SV-006` ·
[`PE-001`](../10_Infrastructure_DevOps_and_Environments/PE-001_Infrastructure_and_Network_Architecture_Design.md) ·
[`PE-002`](../10_Infrastructure_DevOps_and_Environments/PE-002_Environment_Strategy_and_Specification.md) ·
[`PE-003`](../10_Infrastructure_DevOps_and_Environments/PE-003_Infrastructure_as_Code_Standard.md) ·
[`PE-004`](../10_Infrastructure_DevOps_and_Environments/PE-004_CI_CD_Pipeline_Design_Specification.md) ·
[`PE-005`](../10_Infrastructure_DevOps_and_Environments/PE-005_Containerisation_and_Orchestration_Design.md) ·
[`PE-006`](../10_Infrastructure_DevOps_and_Environments/PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md) ·
[`BE-006`](../07_Build_Engineering_and_Development_Standards/BE-006_Component_Build_Specification_Standard.md) ·
[`MG-007`](../09_Data_Migration_and_Cutover/MG-007_Rollback_and_Fallback_Plan.md) *(rule-space collision check)*

**Workspace**
[`OP-007`](../../project_content/17_Operations_Support_and_Runbooks/OP-007_Runbook_Core_ERP_Platform.md) ·
[`OP-008`](../../project_content/17_Operations_Support_and_Runbooks/OP-008_Runbook_Integration_and_Event_Platform.md) ·
[`OP-009`](../../project_content/17_Operations_Support_and_Runbooks/OP-009_Runbook_Identity_and_Access.md) ·
[`OP-010`](../../project_content/17_Operations_Support_and_Runbooks/OP-010_Runbook_Data_Platform_and_Warehouse.md) ·
[`OP-011`](../../project_content/17_Operations_Support_and_Runbooks/OP-011_Runbook_Portal_and_Mobile_App_Operations.md) ·
[`OP-012`](../../project_content/17_Operations_Support_and_Runbooks/OP-012_Disaster_Recovery_and_Continuity_Playbook.md) ·
[`OP-013`](../../project_content/17_Operations_Support_and_Runbooks/OP-013_On_Call_Escalation_and_Handover_Content.md) ·
[`OP-014`](../../project_content/17_Operations_Support_and_Runbooks/OP-014_Manual_Fallback_Procedure_Set.md) ·
[`OP-016`](../../project_content/17_Operations_Support_and_Runbooks/OP-016_Post_Incident_Review_Template_and_Register.md) ·
[`SP-031`](../../project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) ·
[`05-06`](../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md) ·
[`AUDIT-017`](../../project_content/_AUDIT/AUDIT-017_Category_17_OP_Content_Audit.md) ·
`project_content/_templates/TPL_Runbook.md`

**External standards and sources** *(each verified 2026-08-19)*

| Source | Verified |
|---|:--:|
| ISO/IEC 20000-1:2018 §8.5.2, §8.6.1, §8.7.3 | 2026-08-19 |
| ISO/IEC 20000-1:2018/Amd 1:2024 · https://www.iso.org/standard/88434.html | 2026-08-19 |
| Google SRE Workbook — runbooks, game days, and the practice that a procedure is proved by execution · https://sre.google/workbook/ | 2026-08-19 |

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Head of IT Service Management | Initial issue. Rule space `RBS` allocated after `RBK` was found to belong to `MG-007` with 101 occurrences. Twelve-section standard, four runbooks commissioned, `NFR-091` sized at 17–26 PW against a 77–115 PW alternative, execution ledger specified, 21-row dependency register established. Five decisions, five findings | Chief Technology Officer *(pending)* |
| **1.1** | **2026-08-19** | Head of IT Service Management | **Baseline correction, re-enumerated 02:15 (+06).** `PE-007`, `PE-008` and `PE-009` were issued during authoring; §0 added and §11's dependency table corrected — all three move from ⛔ to issued, and **the principal blocker becomes a built environment rather than a missing design**. §6.5's break-glass example and findings `RBS-F-03`, `RBS-F-04` revised: `BLOCKED (no design)` → `BLOCKED (designed, unprovisioned)`. **`RBS-06` retained and its rationale strengthened.** `RBS-F-01` (two `P0` services with no runbook) and `RBS-F-02` (17–26 PW unestimated) are **unaffected** — no `PE` document supplies either | As above |
| **1.2** | **2026-08-19** | Head of IT Service Management | **Conformance to `RR-002` `IDC-08`**; `RR-002` §5.9 cites this document's `RBS`/`RBK` allocation as the model protocol. **Sizing arithmetic corrected**: 0.26 PW × 67 = 17.4, so the appendix mechanism is **17–26 PW** (was 18–26) and the saving **60–89 PW** (was 59–89). **A stale absence claim found by this category's own audit**: the `RL-003` traceability row read *"absent"* and linked to a directory; `RL-003` is issued. | As above |

---

*`SV-003` · Category 11 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
