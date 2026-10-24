---
id: SV-006
title: Problem and Major Incident Management Procedure
category: 11 — Service Operations & Support
code: SV
project: 1000FiX ERP System v2.0
version: 1.1
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Head of IT Service Management
approver: Chief Technology Officer, with the Quality Manager for §8 and the Operations Director for §9
standards_basis: >
  ISO/IEC 20000-1:2018 + Amd 1:2024 §8.6.1 incident management, §8.7.1 problem management,
  §8.7.3 service continuity management · ITIL 4 incident management and problem management
  practices, including the reactive/proactive split · ISO 22301:2019 + Amd 1:2024 §8.2 business
  impact analysis, with ISO/TS 22317:2021 as the BIA method · ISO 9001:2015 cl. 10.2 nonconformity
  and corrective action · Incident command practice — a commander who coordinates and does not
  troubleshoot
traces_to: >
  PGD-000 SV-006 row (◐ OP-013, OP-016) · AUDIT-017 OP-04 (severity had three claimed owners),
  OP-01 (no lawful DR path), OP-18 (breach clock not law yet) · SV-001 §6.4, §6.7 ·
  OP-013 §4.1, §4.5, §4.6, §4.7 · OP-016 §4.1–§4.10 · SP-031 §5.5, §8 · M66 FR-ITS-010,
  FR-ITS-013…017, BRU-ITS-03/05/21 · PE-007 §6, §7 · PE-008 §8.5 · SC-011 · 05-06 NFR-007, NFR-094
depends_on: >
  SV-001 (severity adjudication §6.7, practice map §6.2) · SV-002 (breach → problem, §9.1) ·
  SV-003 (the runbook the commander directs) · SV-004 (the page that starts it) ·
  SV-005 (hypercare PIRs, HX-17) · PE-007 (issued) · PE-008 (issued) · SC-011 (issued) ·
  QA-010 (issued) · RL-005 (issued) · M23 QMS (module, W-dependent) ·
  RF-006 Content Decision Log (DOES NOT EXIST) · LG-024 breach notification period (NOT YET LAW)
verified_on: 2026-08-19
enumeration_timestamp: 2026-08-19 02:15 (+06)
rule_prefix: MIM — verified to return zero occurrences in identifier form across all 777 markdown files of the workspace before allocation, at 2026-08-19 02:15 (+06); re-verified against the 786-file baseline at 02:56 (+06). Conforms to RR-002 IDC-08
priority: P1
needed_by: W2
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# SV-006 — Problem and Major Incident Management Procedure

### Category 11 · Code `SV` · Rule space `MIM` · ISO/IEC 20000-1:2018 §8.6.1, §8.7.1, §8.7.3 · ISO 22301:2019 + Amd 1:2024 §8.2

---

> **`PGD-000` states the gap this document fills:** *"Audit **OP-04**: severity had **three claimed
> owners** before `OP-013` §4.1 took it. `OP-016` provides a post-incident **template** with no
> procedure behind it."*
>
> Both halves are still true and the first has got worse. `AUDIT-017` `OP-04` found `SP-005` §5,
> `SP-005` §12, `SP-031` §2 and `TS-018` §2 all pointing at the wrong owner for the platform severity
> scale, and adjudicated it to `OP-013` §4.1. **Those three one-line corrections have not been made**,
> and on 2026-08-19 a **fourth claimant** appeared: `PE-008` §8.5 rules *"one severity model, defined
> here"* — a **three-level** model, where `OP-013` §4.1 has four. `SV-001` §6.7 adjudicates it for
> this category; **§4.2 below states the operational consequence and lists every correction now
> outstanding.**
>
> The second half — a template with no procedure — is what §8 and §10 supply. And a third gap
> emerges from writing them: **`NFR-007` sets one recovery objective for the whole platform, and no
> business impact analysis has ever been done to justify it.** `PE-007` §3.2 says so plainly —
> *"objectives per tier, because one number is not honest"*. §9 is that analysis, assembled from
> tolerable-outage durations already stated across the estate and never collected.

---

## 1. Purpose

This document states **what happens between the page and the lesson**: how a major incident is
declared and commanded, how it is communicated and closed, how a recurring fault becomes a problem
record and then a permanent fix, how a review produces change rather than understanding, and how
long each business process can actually be down before the damage is irreversible.

It exists because `OP-013` tells an engineer what to do in the first five minutes and `OP-016` gives
a report template for afterwards, and **nothing in the estate covers the two hours in between, or
the ninety days after.**

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | **Major incident** — what it is, and its exact relationship to `Sev1` (§4) |
| 2 | **Severity ownership**, closed: the outstanding corrections and the operational consequence (§4.2) |
| 3 | The **command procedure** — cadence, decision points, the war room, stand-down (§5) |
| 4 | **Communication during a major incident** — cadence, ownership and the one rule that prevents two truths (§6) |
| 5 | The **three escalation seams**: security (`SC-011`), disaster (`PE-007`/`OP-012`), and business (`SP-005`) (§7) |
| 6 | **Problem management** — the practice `SP-031` §5.5 covers in three steps (§8) |
| 7 | **Business impact analysis** — MTPD per process, assembled from evidence already in the estate (§9) |
| 8 | The **post-incident review procedure** behind `OP-016`'s template (§10) |
| 9 | **Measurement** — including the two numbers that show whether reviews change anything (§11) |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| **The severity scale** `Sev1`–`Sev4` | [`OP-013`](../../project_content/17_Operations_Support_and_Runbooks/OP-013_On_Call_Escalation_and_Handover_Content.md) §4.1 | Canonical. **This document is the fifth to reference it and the first not to claim it** |
| Declaration wording, incident roles, the authority table, handover | `OP-013` §4.5, §4.6, §4.8, §4.9 | **Adopted by citation** (`MIM-01`) |
| **The PIR report template, blameless principle, contributing-factor tags, action rules, the register fields** | [`OP-016`](../../project_content/17_Operations_Support_and_Runbooks/OP-016_Post_Incident_Review_Template_and_Register.md) §4.2–§4.10 | **Adopted whole.** §10 supplies the **procedure** — who facilitates, how it is scheduled, how actions are chased — which `OP-016` does not contain |
| The words issued to each audience | `OP-004`, `OP-005` | §6 owns cadence and ownership, never wording |
| Paging, rota, acknowledgement, escalation ladder | `SV-004` | This document begins when the engineer is awake |
| **Security classification, breach assessment, notification decision** | [`SC-011`](../05_Security_Privacy_and_Compliance/SC-011_Security_Incident_Response_Plan.md), `M29` | **`M66` `BRU-ITS-21` is absolute.** §7.1 states the handover point |
| Backup design, restore procedure, failover sequence, `Z4` recovery | [`PE-007`](../10_Infrastructure_DevOps_and_Environments/PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md) | §7.2 states when a major incident becomes a disaster; `PE-007` states what happens then |
| Disaster declaration authority and crisis roles | [`OP-012`](../../project_content/17_Operations_Support_and_Runbooks/OP-012_Disaster_Recovery_and_Continuity_Playbook.md) §4.2 | Adopted; §7.2's seam only |
| Defect triage, `S1`–`S4`, deferral | [`QA-010`](../08_Quality_Engineering_and_Test/QA-010_Defect_Management_and_Quality_Gate_Standard.md), `TS-018` | `SV-001` §6.4's three relationships hold |
| Change and emergency change mechanics | [`RL-001`](../12_Release_Deployment_and_Transition/RL-001_Release_Management_and_Versioning_Policy.md) §9, `SP-031` §5.4 | §5.4 states what the commander may authorise, and `RL-001`'s CAB reviews it |
| The **wave** post-implementation review | [`RL-005`](../12_Release_Deployment_and_Transition/RL-005_Post_Implementation_Review_Standard.md) | A wave PIR reviews delivery. This reviews incidents. `AUDIT-017` notes three artefacts called "PIR" — §10.1 disambiguates |
| CAPA mechanics, nonconformance records | `M23` | §8.6 routes into it |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Incident Commanders** | §5 — the cadence, the decision points, and the four things a commander does not do |
| On-call engineers | §4.1 (is this a major incident?), §7 (when does it leave my hands?) |
| **Chief Technology Officer** | §4.2's outstanding corrections; §9's BIA and what it says about `NFR-007`; §12's four decisions |
| **Operations Director and business owners** | §9 — how long each business process can actually be down, and who decided |
| Head of IT Service Management | §8's problem practice, §10's review procedure, §11's measures |
| Quality Manager | §8.6 and §10.5 — the route into `M23` that brings incidents inside the ISO 9001 scope |
| Security Lead and DPO | §7.1's handover, and the statutory clock that starts at **detection** |
| Review facilitators | §10 — how to run one, and what independence means |
| Steering Committee | §11.3's quarterly pattern report, and §8.7's organisational-cause signal |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO/IEC 20000-1:2018 + Amd 1:2024** | §8.6.1 — incidents classified, prioritised, escalated, resolved and closed against documented procedures; **major incidents have an agreed definition and are managed by a documented procedure** | §4 defines major incident; §5 is the procedure; §5.7 is closure | None |
| Same | §8.7.1 — problems identified from incident trends, **root causes investigated**, and **changes raised where a permanent fix is available** | §8's five stages, thresholds and closure test | None |
| Same | §8.7.3 — service continuity requirements **determined from a business impact analysis and risk assessment** | **§9 is the BIA the clause requires and the estate has never had** | **The clause is currently unmet.** §9 supplies the analysis; the objectives it implies still need `RQ-006` amendment |
| **ISO 22301:2019 + Amd 1:2024** | §8.2 business impact analysis; **§4.1/§4.2 climate change as a context issue** (Amd 1, published Feb 2024) | §9.1's method; §9.5's climate scenarios, as `SV-001` §4.4's determination requires | None |
| **ISO/TS 22317:2021** | BIA method — scoping, data collection, impact over time, validation | §9.1 follows the four steps; §9.6 records that validation with business owners has **not** occurred | Validation is a business activity this document cannot perform |
| **ITIL 4** | Problem management — **reactive and proactive**; an incident closes on restoration while the problem stays open until the cause is removed | §8.2's two entry paths; `MIM-15` restates `M66` `BRU-ITS-03` as the closure rule | None |
| **ISO 9001:2015** | cl. 10.2 — nonconformity, correction, root cause, corrective action, and evaluation of effectiveness | §8.6 and §10.5 route into `M23` CAPA rather than a parallel list | None |
| Incident command practice | A named commander who **coordinates and does not troubleshoot** | `OP-013` §4.6, adopted; §5.2 adds the four prohibitions | None |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| **`OP-013`** | [`../../project_content/17_.../OP-013`](../../project_content/17_Operations_Support_and_Runbooks/OP-013_On_Call_Escalation_and_Handover_Content.md) | §4.1 the four-level scale and `SV-01`…`SV-07` · §4.2 the four scales and their only three relationships · §4.5 declaration · **§4.6 the six incident roles** · §4.7 the ladder and parallel escalations · §4.8 the authority table · §4.9 incident handover |
| **`OP-016`** | [`../../project_content/17_.../OP-016`](../../project_content/17_Operations_Support_and_Runbooks/OP-016_Post_Incident_Review_Template_and_Register.md) | §4.1 eleven review triggers and `RV-01`…`RV-04` · §4.2 blameless, `BL-01`/`BL-02` · §4.3 evidence and `EV-01` · §4.4 contributing factors and `CF-01`…`CF-04` · §4.5 the meeting · **§4.6 the report template** · §4.7 `AC-01`…`AC-08` · §4.8 the register fields and `RG-01` · **§4.9 the twenty contributing-factor tags and `TG-01`** · §4.10 publication |
| `SP-031` §5.5, §8 | [`../../project_content/06_.../SP-031`](../../project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) | Problem management in **three steps** — investigate, raise a CAPA, publish known errors — and the exceptions table |
| `M66` §5.2, §5.3, §9 | [`../../1000fix_ERP_Module/.../M66`](../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66_Internal_IT_Service_Management.md) | `FR-ITS-010` major incident handling · `FR-ITS-013`…`017` problem management · `AUT-ITS-07`/`08` automatic and proactive problem raising · **`BRU-ITS-03`, `BRU-ITS-05`, `BRU-ITS-21`** |
| **`PE-007` §3.2, §6, §7** | [`../10_.../PE-007`](../10_Infrastructure_DevOps_and_Environments/PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md) | **Objectives per tier — *"because one number is not honest"*** · declaring a disaster · the failover sequence · `Z4` recovery routes and §7.5's forced, unmade decision |
| `PE-008` §8.5 | [`../10_.../PE-008`](../10_Infrastructure_DevOps_and_Environments/PE-008_Observability_and_Monitoring_Design.md) | The fourth severity claimant, adjudicated in `SV-001` §6.7 |
| `SC-011` | [`../05_.../SC-011`](../05_Security_Privacy_and_Compliance/SC-011_Security_Incident_Response_Plan.md) | The security incident response this procedure hands over to |
| **`OP-007` §7, `OP-011`, `OP-014`** | [`../../project_content/17_.../`](../../project_content/17_Operations_Support_and_Runbooks/) | **Tolerable outage durations per scenario** — the raw material §9.3 assembles into a BIA |
| `05-06` | [`../../1000fix_ERP_Module/.../05-06`](../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md) | `NFR-007` RPO 15 min / RTO 2 h · `NFR-047` 24 h offline · `NFR-094` breach notification |
| `AUDIT-017` `OP-04`, `OP-18` | [`../../project_content/_AUDIT/AUDIT-017`](../../project_content/_AUDIT/AUDIT-017_Category_17_OP_Content_Audit.md) | The three claimants; and that the PDPA 2026 notification period **is not yet law** |

### 2.3 Audit findings this document closes or contributes to

| Finding | Source | How this document acts on it |
|---|---|---|
| **`OP-04`** — platform severity had three claimed owners and no owner | `AUDIT-017`, HIGH | **Closed in specification, and re-opened by a fourth claimant.** §4.2 lists **four** outstanding corrections (three from `AUDIT-017`, one new against `PE-008` §8.5) and states the operational consequence of each remaining unmade |
| `PGD-000` `SV-006` row — *"`OP-016` provides a template with no procedure behind it"* | Register | **Closed.** §10 supplies the procedure: facilitator pool, independence test, scheduling mechanics, action chasing, register operation, quarterly pattern |
| `PGD-000` `SV-006` row — *"severity had three claimants, a governance gap `SV-006` closes"* | Register | **Closed** by §4.2, subject to four upstream one-line edits that are not this document's to make |
| **`OP-01`** — no lawful DR path for resident personal data | `AUDIT-017`, **CRITICAL** | **Contributes.** §9.4 shows the BIA consequence: **`S-12`'s MTPD is shorter than its achievable recovery time**, which is the impact statement `PE-007` §7.5's forced decision needs |
| **`OP-18`** — the PDPA 2026 notification period is not law yet | `AUDIT-017`, MEDIUM | **Contributes.** `MIM-12`: the clock starts at **detection**, the 72-hour figure is a planning assumption and never stated as fact, and §7.1 assesses within 24 hours regardless |
| **`SMF-F-06`** (`SV-001`) — `PE-008` §8.5's severity claim and three prefix collisions | This category | **§4.2** carries the correction list; `SV-001` §6.7 carries the adjudication |
| **`PSL-F-01`** (`SV-002`) — planned maintenance exceeds the 24×7 error budget | This category | **Contributes.** `MIM-08`: **a maintenance window that overruns its announced end is declared as an incident at the announced end**, not when someone notices |
| `AUDIT-017` — *"three artefacts called PIR"* | `AUDIT-017` `OP-06` context | **Closed.** §10.1 disambiguates post-**incident** review, post-**implementation** review and the wave PIR, and names the owner of each |

### 2.4 The rule space

**`MIM`**, verified at **2026-08-19 02:15 (+06)** to return **zero occurrences in identifier form**
across all **777** markdown files. No rule in this category uses the form `SV-nn` (`SV-001` §2.4),
and every cross-document rule citation names its owning file (`SMF-26`) — a rule this document
depends on more than most, because it cites `SV-01`…`SV-07` (severity, `OP-013`), `RV-01`…`RV-04`
(reviews, `OP-016`), `AC-01`…`AC-08` (actions, `OP-016`) and `AD-01`…`AD-05` (alerts, `PE-008`),
and three of those four prefixes are reused elsewhere in the estate with different meanings.

---

## 3. Where This Document Sits

| Moment | Owned by |
|---|---|
| Something breaks | The platform |
| It is detected | `PE-008` §8 |
| A human is woken | **`SV-004`** |
| The engineer opens the runbook | `SV-003` |
| **It is declared major, commanded, communicated and closed** | **§4–§7, this document** |
| The lesson is extracted | **§10, this document** (procedure) + `OP-016` (method and template) |
| **The cause is removed** | **§8, this document** |
| The change that removes it | `RL-001`, `SP-031` |
| The corrective action is tracked to closure | `M23` |

> **`MIM-01`. `OP-013` §4.1, §4.5, §4.6, §4.8 and §4.9 and `OP-016` §4.2–§4.10 are adopted whole by
> citation and never restated.** This document is the procedure that runs between and around them.

---

## 4. Major Incident

### 4.1 What makes an incident major

The estate uses two terms that are related and not identical. `OP-013` §4.1 defines `Sev1`. `M66`
`FR-ITS-010` and ITIL 4 define a **major incident** — one requiring a named incident manager, a
communication cadence and a mandatory review. Nothing states the relationship, so two people can be
in the same incident disagreeing about whether it is "major".

> **`SV-006-D-01`. A major incident is: every `Sev1`, plus any `Sev2` that spans two or more
> teams **or** exceeds 60 minutes unresolved.**

This is **derived, not chosen**. `OP-013` §4.1's own row for *Incident Commander* reads:
**`Sev1` — required; `Sev2` — required if it lasts > 60 min or spans teams.** A major incident is
exactly an incident with a commander, and `OP-013` already states when one is required.

| Trigger | Major? | Basis |
|---|:--:|---|
| Any `Sev1` | **Yes, immediately** | `OP-013` §4.1 — IC required |
| `Sev2` spanning two or more teams | **Yes** | `OP-013` §4.1 |
| `Sev2` unresolved at 60 minutes | **Yes, automatically at 60 min** | `OP-013` §4.1 |
| `Sev2` resolved in 40 minutes by one team | No | — |
| A maintenance window that overruns its announced end | **Yes, at the announced end** | `MIM-08`; `SV-002` `PSL-12` |
| `Sev3`, `Sev4` | No | — |

| # | Rule |
|---|---|
| **`MIM-02`** | **"Major incident" adds a commander, a cadence and a mandatory review. It does not add a severity.** There is no `Sev0`, and inventing one would be the fifth severity scale (`OP-013` §4.2) |
| **`MIM-03`** | **The transition from `Sev2` to major at 60 minutes is automatic and announced**, not proposed. `OP-013` `SV-04`'s asymmetry holds — upgrading is easy, downgrading needs more authority |
| **`MIM-04`** | **Anyone may declare** (`OP-013` `SV-01`, `OP-001` `TR-07`). **`OP-013` `SV-07` holds absolutely: a `Sev1` that turns out to have been over-declared is closed with a one-line note and no review of the declarer, ever** |

### 4.2 Severity ownership — closing the governance gap

`AUDIT-017` `OP-04` found four documents pointing at the platform severity scale and three pointing
at the wrong place, and adjudicated ownership to `OP-013` §4.1. **`PGD-000` assigns the closure of
that governance gap to this document.** Closing it means stating who owns it, listing every
outstanding correction, and saying what each costs while it is unmade.

**Owner: `OP-013` §4.1. Four levels: `Sev1`, `Sev2`, `Sev3`, `Sev4`.** *(`SV-001` `SMF-27`.)*

| # | Document | Currently says | Should say | Cost while unmade |
|---:|---|---|---|---|
| 1 | `SP-005` §5 and §12 | *"`OP-008` — technical severity classification"* | `OP-013` §4.1 | **An engineer following `SP-005` at 02:00 reaches a component runbook with no severity table in it** |
| 2 | `SP-031` §2 | *"Technical incident runbooks and severity classification → `OP-008`"* | `OP-013` §4.1 | The SOP that governs the service desk misroutes its own classification step |
| 3 | `TS-018` §2 | *"IT incident management and its own severity scale → `M66`, `SP-031`, `OP-002`"* | `M66` owns **ticket priority**; `OP-013` §4.1 owns **platform severity**; `OP-002` is the hypercare plan | Defect triage points at three documents, none of which owns the platform scale |
| 4 | **`PE-008` §8.5** *(new, 2026-08-19)* | *"One severity model, defined here"* — **three levels**, rule `SV-01` asserting programme scope | **Map, do not own**: `PE-008` `Sev1`→`Sev1`, `Sev2`→`Sev2`, `Sev3`→**`Sev3` *and* `Sev4`** | **A capacity threshold approached — dashboard-only under `OP-013` — becomes a ticket with a five-day restoration target.** And `PE-008`'s `SV-01`/`RT-04`/`AL-03` collide with three existing prefixes |

> **`MIM-F-01`. Three corrections have been outstanding since 2026-08-20 and a fourth arose on
> 2026-08-19.** All four are one-line edits in documents this category does not own. **Until they are
> made, the estate contains a control with four published owners**, and the failure is realised at
> exactly the moment nobody has time to check which document is right.
>
> `AUDIT-017` `R-04` is directly on point: *"a finding that does not change the next author's
> behaviour has not been actioned, only recorded."* `OP-04` was recorded, and the next author
> claimed the space again.

| # | Rule |
|---|---|
| **`MIM-05`** | **No document in Category 11 defines a severity scale.** This document, `SV-001`, `SV-002`, `SV-003`, `SV-004` and `SV-005` all cite `OP-013` §4.1 and none extends it |
| **`MIM-06`** | **Severity is set on impact, not cause** (`OP-013` `SV-02`), **is re-assessed as understanding changes** (`OP-013` `SV-03`), and **is never adjusted to avoid a review, a metric or an awkward conversation** (`OP-013` `SV-05`). *Note the hazard `SMF-26` exists for: `PE-008` §8.5 also defines an `SV-03`, and it means something else entirely* |
| **`MIM-07`** | **A severity dispute during an incident is settled by the Incident Commander in ten seconds and reviewed afterwards.** An incident is not the forum for a governance question |
| **`MIM-08`** | **A maintenance window that passes its announced end is an incident, declared at the announced end.** `SV-002` `PSL-12` excludes announced maintenance from availability **only within its stated window**; the overrun is unavailability, and treating it as "still maintenance" is how an exclusion becomes a loophole |

---

## 5. Command

### 5.1 The first ten minutes

`OP-013` §4.5 owns declaration and `OP-007` §6 owns the first-five-minutes list. This is the
commander's sequence, which runs alongside them.

| Min | Commander does | Basis |
|:--:|---|---|
| 0 | **Takes the role explicitly and says so**: *"I am Incident Commander for `INC-…`"* | `OP-013` §4.6 |
| 0–2 | **Names a Scribe and a Communications Owner** — at `Sev1` both are **separate people from the IC** | `OP-013` §4.6 |
| 2 | Confirms severity and states blast radius using `SV-003` §9.1's **depended-on-by** column | `SV-003` `RBS-25` |
| 3 | **Instructs preservation of evidence before remediation** — logs, `pg_stat_activity`, last backup timestamp, 24 h of deployment history | `OP-016` `EV-01`; `OP-007` §6 |
| 5 | Sets the **first communication deadline** and hands it to the Comms Owner | §6.1 |
| 8 | States **what is confirmed, what is assumed, what has been ruled out** | `OP-013` §4.9 |
| 10 | Sets the **next command-call time** and the first decision point | §5.3 |

### 5.2 What a commander does not do

`OP-013` §4.6 states the principle — *"the moment the IC starts debugging, nobody is commanding."*
Four prohibitions make it operable:

| # | Rule |
|---|---|
| **`MIM-09`** | **The IC does not troubleshoot.** If the IC is the only person who can fix it, they hand over command first and fix it second |
| **`MIM-10`** | **The IC does not communicate externally.** The Comms Owner does, and adds no fact the IC has not confirmed (`OP-013` §4.6) |
| **`MIM-11`** | **The IC does not take the business decision.** Fallback invocation, customer impact acceptance and SLA pauses belong to the Business Decision Owner (`OP-013` §4.6, `OP-001` §4.6) |
| **`MIM-12`** | **The IC does not make a breach determination.** Suspected personal-data involvement goes to the DPO immediately and in parallel; **the `NFR-094` assessment clock runs from detection**, and `SC-011` owns the judgement (`M66` `BRU-ITS-21`) |

### 5.3 Cadence and decision points

An incident that runs without a rhythm runs on whoever speaks loudest.

| Element | `Sev1` | `Sev2` (major) |
|---|---|---|
| Command call | **Continuous bridge**, open until stand-down | On declaration, then hourly |
| Internal update | **Every 30 minutes** | Every 2 hours |
| External update | Per `OP-004`; status page ≤ 15 min | Only if visible |
| **Decision point** | **Every 30 minutes**, on the update | Every 2 hours |
| Business escalation | Ops Director + CTO **at declaration** | CTO at 2 h |
| Crisis Management Team | **At 2 h if unresolved** (`OP-013` §4.7 L4) | — |

**The decision point is a fixed question, asked aloud, every cycle:**

> *"Given what we know now — do we continue this line, change approach, invoke the fallback, or
> escalate? And what is the time-box on the answer?"*

| # | Rule |
|---|---|
| **`MIM-13`** | **Every diagnostic line of enquiry is time-boxed at the decision point.** An untimed investigation is how a 20-minute incident becomes a four-hour one — `OP-013` §1 names exactly that as the cost of escalation ambiguity |
| **`MIM-14`** | **Restoration precedes diagnosis.** If a fallback, a restart, a rollback or a feature flag restores service, it is used, and the cause is found afterwards from preserved evidence. `M66` `BRU-ITS-03`: **an incident closes when service is restored; the problem stays open until the cause is removed** |

### 5.4 Authority during an incident

`OP-013` §4.8's authority table is adopted whole and not restated. Two procedural additions:

| # | Rule |
|---|---|
| **`MIM-16`** | **The IC exercises the on-call column of `OP-013` §4.8 without seeking permission**, and an emergency change made as IC is reviewed by `RL-001`'s CAB within **2 working days** — not approved by it beforehand |
| **`MIM-17`** | **Where the IC needs authority they do not hold, they name the holder and the deadline aloud**, and the escalation ladder (`OP-013` §4.7) is used to reach them. **Waiting silently for an absent approver is the failure `OP-013` `AU-01` exists to make visible** |

### 5.5 The war room

| Attribute | Value |
|---|---|
| Primary | The incident channel in the standard collaboration tool (`OP-013` §4.10 tier 1) |
| **If the estate is down** | **Tier 2 — SMS via the failover gateway; tier 3 — the printed telephone tree.** `OP-013` `OB-01`: *"a tree stored only in the system it exists to survive is not a tree"* |
| Who joins | Only those the IC has asked for. **`MIM-18`: an incident channel with thirty observers is a channel the responders stop using** |
| Scribe's record | Times, actions, decisions, owners — **contemporaneous**, because `OP-016` §4.3 needs it and memory does not supply it |
| Stand-down | Explicit, announced, with the next steps named (§5.7) |

### 5.6 Handover mid-incident

`OP-013` §4.9's incident-handover format is adopted whole: the outgoing IC states current severity ·
what is confirmed · what is assumed · what has been ruled out · who is doing what · when the next
communication is due · what decision is pending and who owns it — and **the incoming IC repeats it
back before the handover completes**.

> **`MIM-19`. `OP-013` `HO-01` applies to command as it does to shifts: an unacknowledged handover
> leaves an incident with no owner.** The repeat-back is the acknowledgement and it is not optional
> at 04:00 because everyone is tired — that is when it matters.

### 5.7 Closure

An incident is closed when **service is restored and verified**, not when the cause is understood.

| Step | Requirement |
|---|---|
| 1 | Restoration **verified** by the check the runbook names (`SV-003` §4.2 §3), not by absence of alerts |
| 2 | The affected population **told it is over**, by the Comms Owner, and never before `OP-005` says so (`OP-001` §4.10) |
| 3 | **Fallback stood down and reconciled** — `OP-014`'s closure record; batch entry, duplicate check, VAT sequence integrity where invoicing was affected |
| 4 | **SLA pause decision recorded** on the incident record, if one was made (`OP-001` §4.6, `SV-002` `PSL-24`) |
| 5 | **The review is already scheduled** — `OP-016` `RV-01` requires it booked at *declaration*, not at closure |
| 6 | **A problem record opened** where the cause is unknown or the fault has recurred (§8.2) |
| 7 | Ledger rows written for every procedure executed (`SV-003` `RBS-19`), within 2 working days |
| 8 | Severity timeline finalised — every re-assessment timestamped (`OP-013` `SV-03`) |

> **`MIM-20`. An incident may not be closed with an unknown cause and no problem record.** That
> combination is how the eleventh occurrence is experienced as the first — the exact condition
> `M66` §2 was written to end.

---

## 6. Communication During a Major Incident

`OP-004` owns every word and `OP-005` owns the status page. This section owns **cadence, ownership
and the rule that prevents two truths**.

### 6.1 The cadence

| Audience | First message | Then | Owner |
|---|:--:|:--:|---|
| Internal — all affected staff | **≤ 15 min** (`Sev1`) | Every 30 min | Comms Owner |
| **Status page** | **≤ 15 min** (`Sev1`) | Every 30 min | Comms Owner |
| Customers, where customer-facing | **≤ 30 min** | Every 30 min | Comms Owner |
| Corporate clients with notification rights | Per contract | Per contract | Account Manager (`OP-004` template 6) |
| Branches — **what to do meanwhile** | **In the first message, not later** | With each update | Comms Owner |
| Executive | At declaration | Every 30 min | IC |
| Regulator / Authority | **Never by this route** | — | **DPO / Legal only** (`OP-013` §4.8) |

### 6.2 The rules

| # | Rule |
|---|---|
| **`MIM-21`** | **One Communications Owner, one voice.** Nobody else sends anything — `OP-002` §4.5 and `OP-004` §3 already say so, and it is broken most often by a well-meaning manager reassuring their own team |
| **`MIM-22`** | **Every message carries the time of the next update, and that commitment is met even when there is nothing new.** *"No change, next update 14:30"* is a message; silence is interpreted as a worse outage than the one occurring |
| **`MIM-23`** | **The first message to branches contains the fallback instruction** (`OP-014`), not a promise of one. `OP-007` §6 already requires it in the first five minutes |
| **`MIM-24`** | **No message states a cause before it is confirmed.** A retracted cause costs more trust than an admitted uncertainty |
| **`MIM-25`** | **The status page is the single source of truth for external communication** (`OP-005` `IC-07`) — **and `AUDIT-017` `OP-14` records that it has no independent hosting**, so §6.3 states what happens when it is unavailable |

### 6.3 When the status page is part of the outage

`AUDIT-017` `OP-14`: `OP-005` `SP-10` requires the status page to be hosted independently of the ERP
estate; `02-05` §8 provisions no such hosting. In a `Sev1` affecting the estate, **the single source
of truth may be unavailable at exactly the moment every other channel points at it.**

> **`MIM-26`. If the status page is unavailable, the declared external channel is SMS to branch
> managers plus a banner on the public website, and the incident's first message says which channel
> is authoritative.** Two silent channels are worse than one working one, and an audience that
> cannot reach the stated source assumes the worst available explanation.

This is a documented fallback, not a solution. **The solution is independent hosting**, and it is
the same procurement as `SV-002` `PSL-Q-03`'s external synthetic monitoring and `SV-004`'s separate
paging account — **three requirements, one account, and it should be bought once** (`OCP-Q-04`).

---

## 7. The Three Seams

### 7.1 Security — handover to `SC-011`

> **`MIM-27`. The moment personal-data or security compromise is suspected, the security on-call and
> the DPO are engaged in parallel, and the classification decision leaves this procedure.**
> `M66` `BRU-ITS-21` is absolute: the service-management process **makes no security judgement**.

| Who | Owns |
|---|---|
| **This procedure** | Restoration, command, communication cadence, the incident record |
| **`SC-011` / `M29`** | Classification, containment strategy, forensic preservation, breach assessment |
| **DPO / Legal (`LG-024`)** | **The notification decision and its timing.** Nobody else, ever |

| # | Rule |
|---|---|
| **`MIM-28`** | **The `NFR-094` assessment clock runs from detection**, not from declaration or from classification. `OP-013` §4.7's parallel escalation exists for this reason |
| **`MIM-29`** | **A DPO assessment is initiated within 24 hours of suspicion, regardless of the notification period.** `AUDIT-017` `OP-18` records that the **PDPA 2026 notification period is left to regulations that are not yet published**; `OP-004` `RN-03` therefore uses **72 hours as a stated planning assumption and not a legal statement**, and this document does the same. **No document may state a notification deadline as fact until `LG-024` sets it** |
| **`MIM-30`** | **Evidence preservation for a security incident overrides speed of restoration**, and this is the one place `MIM-14` is inverted. The IC is told so explicitly at handover, because the reflex is the other way |

### 7.2 Disaster — the seam with `PE-007` and `OP-012`

A major incident becomes a **disaster** when restoration within the RTO is no longer credible by any
route available to the responders.

| Condition | Becomes | Authority |
|---|---|---|
| `Sev1` at **2 hours** with RTO at risk | Crisis Management Team engaged | `OP-013` §4.7 L4 |
| Environment, site or region **lost** | **Disaster** — `PE-007` §6.1 declaration | **CTO**, with Ops Director informed (`OP-013` §4.8) |
| Restore production from backup, **accepting data loss** | Not a disaster by itself; **a business decision** | **CTO and CFO** (`OP-013` §4.8) |
| **`Z4` / `BD-R` resident store lost** | **Disaster, and a regulatory question** | **CTO with Legal and the DPO** — §9.4 |

| # | Rule |
|---|---|
| **`MIM-31`** | **Declaring a disaster is an escalation of authority, not an admission of failure**, and the 2-hour trigger is automatic so that nobody has to propose it |
| **`MIM-32`** | **The `Z4` route is never chosen by an engineer at 02:00.** `OP-012` `RD-01` forbids the cross-border restore; `PE-007` §7.5 records the decision as *forced and unmade*. **Until it is made, `MIM-33` applies** |
| **`MIM-33`** | **On loss of the resident store, the declared response is degraded operation without residency-classified fields** (`PE-007` §7.4, `SC-007` §9.2), **and the CTO, Legal and the DPO are engaged before any restore route is selected.** This is a documented holding position, not a recovery |

### 7.3 Business — the seam with `SP-005`

`SP-005` owns operational, commercial, safety and legal escalation. Two rules keep the seam clean:

| # | Rule |
|---|---|
| **`MIM-34`** | **A service problem is not a platform incident.** A customer's repair job running late is `MD-028` and `SP-005`; the platform being unable to record it is this procedure. `OP-001` §4.6 states the only sanctioned relationship |
| **`MIM-35`** | **Safety leaves this procedure entirely and immediately**, per `SP-030` — *before any system consideration* (`OP-013` §4.7) |

---

## 8. Problem Management

**`SP-031` §5.5 covers problem management in three steps.** `M66` `FR-ITS-013`…`017` specifies the
capability and arrives at W6 (or W1 under `SV-001-D-04`). This is the practice in between, and it is
what stops the estate re-learning the same fault.

### 8.1 The distinction that makes it work

| | Incident | Problem |
|---|---|---|
| Purpose | **Restore service** | **Remove the cause** |
| Closes when | Service is restored and verified | **Recurrence is verifiably absent** over a defined period |
| Severity | `Sev1`–`Sev4` | **None** — it has an impact estimate (`OP-013` §4.2) |
| Owner | Incident Commander → service owner | **A named investigator** |
| Typical duration | Hours | Weeks |

> **`MIM-15`. An incident closes when service is restored; the problem stays open until the cause is
> removed** (`M66` `BRU-ITS-03`). **`MIM-36`: a problem closes only on verified absence of
> recurrence** (`M66` `BRU-ITS-05`) — never on the fix being deployed.

### 8.2 Entry — the two paths and their thresholds

**Reactive** — a problem is raised automatically when any of these is met:

| # | Threshold | Basis |
|---|---|---|
| **`PT-01`** | **Three occurrences of the same cause within 90 days** | `OP-016` §4.1's escalated-review trigger, adopted as the problem threshold so the two agree |
| **`PT-02`** | **Two `Sev1` incidents from the same cause within 12 months** | Derived — a second `Sev1` from one cause is not chance |
| **`PT-03`** | **Three `Sev2` or `Sev3` incidents with the same symptom and configuration item within 30 days** | `M66` `AUT-ITS-07`'s recurrence pattern, given a number |
| **`PT-04`** | **Any incident closed with an unknown cause** | `MIM-20` |
| **`PT-05`** | **Any known-issue entry open beyond 20 working days** | `OP-002` `KI-02`, adopted |
| **`PT-06`** | **The same SLO missed in two consecutive months** | `SV-002` §9.1 |
| **`PT-07`** | **Any fallback that did not work when invoked** | `OP-016`'s `fallback-failure` tag; a broken fallback is a latent `Sev1` |

**Proactive** — a problem candidate is raised from a trend before an incident occurs:

| Signal | Source |
|---|---|
| Slow-burn error-budget consumption without an incident | `PE-008` §8.2 slow tier; `SV-002` §6.4 |
| A capacity scaling trigger approached repeatedly | `PE-006` §7.2 |
| Dead-letter volume trending up while staying inside tolerance | `OP-008` |
| An alert firing frequently and being acknowledged without action | `PE-008` `AD-04` |
| A runbook procedure repeatedly executed | **`SV-003`'s §12 execution ledger** — a recovery run monthly is a defect being managed rather than fixed |

> **`MIM-37`. The execution ledger is a problem-detection instrument.** `SV-003` built it to prove
> runbooks; it also reveals which failures the organisation has quietly accepted as routine. **A
> procedure executed more than three times in a quarter raises a proactive problem candidate.**

### 8.3 Investigation

| Stage | Requirement |
|---|---|
| **Assign** | **One named investigator** — never a team (`OP-016` `AC-01`'s rule, applied to problems) |
| **Quantify** | Incident count, total downtime, contacts generated, business impact, effort consumed. **A problem with no impact estimate cannot be prioritised against another** |
| **Analyse** | `OP-016` §4.4's six layers — trigger, technical conditions, detection, response, organisational, mitigation. **`CF-01`: at least three contributing factors across at least two layers** |
| **Evidence** | Named, retained, and referenced. `SP-029`'s method where the cause is a process rather than a technical fault |
| **Time-box** | **20 working days to a stated cause or a stated inability to find one.** An investigation with no deadline is an open record, not an investigation |

| # | Rule |
|---|---|
| **`MIM-38`** | **"Human error" is never a cause** (`OP-016` `CF-02`). The cause is what made the error likely and undetected |
| **`MIM-39`** | **"Third-party failure" is never a complete cause** (`OP-016` `CF-03`). The cause is **our exposure to it** and the state of our fallback |
| **`MIM-40`** | **An investigation that cannot find a cause is closed as such, with the detection gap recorded as the finding.** Not knowing why is a monitoring problem, and it is more useful stated than left open |

### 8.4 Known error and workaround

> **`MIM-41`. A known error is published as soon as a workaround exists — not when the cause is
> understood.** `SV-001` `SMF-20` sets the second-occurrence trigger; this sets the content.

| Field | Requirement |
|---|---|
| Symptom | **In the user's words**, as they experience it (`OP-002` §4.6) |
| Affected population | Which of `OP-001` §4.1's populations, and how many |
| Workaround | **Mandatory.** An entry with no workaround is escalated, not published (`OP-002` §4.6) |
| Customer-visible? | If yes, mirrored to `OP-005` and the `HC` set (`OP-002` `KI-03`) |
| Bilingual? | **If it reaches branch staff, field technicians, sellers or customers — yes** (`CG-010` §3.3) |
| Retirement | On verified permanent fix, not on the change being deployed |

### 8.5 Permanent fix and closure

| Step | Requirement |
|---|---|
| 1 | The fix is a **change** — `RL-001`, `SP-031` §5.3. A problem is never fixed outside change control |
| 2 | **A verification period is stated before the change is made**, proportionate to the recurrence interval: at minimum **three times the observed interval**, and never less than 30 days |
| 3 | Recurrence is **monitored** across that period (`M66` `AUT-ITS-10`) |
| 4 | **Closed on verified absence** (`MIM-36`); **reopened on any recurrence**, with the verification period restarting |
| 5 | The known error is retired and the workaround withdrawn from `OP-003`, `HC` and `KB` |
| 6 | **The runbook is updated** and its ledger row refreshed (`SV-003` `RBS-20`) |

> **`MIM-42`. The verification period is set before the fix, not after.** Setting it afterwards
> means setting it to whatever has already elapsed, which verifies nothing.

### 8.6 The route into `M23`

| # | Rule |
|---|---|
| **`MIM-43`** | **Every problem raises a corrective action in `M23`**, not a private list. `M23` `BRU-QMS-02` requires root cause and CAPA before a non-conformance closes, and `SV-001` `SMF-22` brings support inside the ISO 9001 certified scope on that route |
| **`MIM-44`** | **A problem the organisation decides not to fix is closed as `accepted risk`, with a named accepter, and recorded in `M60`** (`OP-016` `AC-08`). **This is honest; a problem left open for a year is not** |

### 8.7 The organisational signal

`OP-016` `TG-01` identifies three contributing-factor tags that indicate an **organisational** rather
than technical cause: **`deferred-work`, `single-person`, `authority-gap`**.

> **`MIM-45`. If those three tags dominate a quarter, the pattern report says so plainly to the
> Steering Committee, because no engineering action will address them.** Given `AUDIT-017`'s
> enumeration — an unstaffed rota, unfunded T1, no break-glass, no access profiles, an unprovisioned
> `dr` — **the programme should expect `deferred-work` to dominate its first year, and should read
> that as confirmation rather than surprise.**

---

## 9. Business Impact Analysis

### 9.1 Why this section exists

`NFR-007` sets **RPO ≤ 15 min, RTO ≤ 2 h** for the platform — one pair of numbers for everything.
`PE-007` §3.2 responds with *"objectives per tier — because one number is not honest"*, and derives
tiered objectives from an engineering standpoint.

**Neither is a business impact analysis.** ISO/IEC 20000-1 §8.7.3 requires continuity requirements to
be **determined from a BIA**, and ISO 22301 §8.2 with ISO/TS 22317:2021 gives the method:
scope, collect, analyse impact over time, validate. **The estate has never done one**, so the
recovery objectives it commits to were chosen rather than derived.

> **`MIM-46`. A recovery objective that was not derived from an impact analysis is a preference.**
> The test is simple: **can anyone say what happens at hour three?** If not, the two-hour RTO is a
> number somebody liked.

### 9.2 Method

Following ISO/TS 22317:2021's four steps, at the altitude the evidence supports:

| Step | What was done here |
|---|---|
| **Scope** | The 21 services of `SV-001` §5.2, expressed as the business processes they carry |
| **Collect** | **The estate already states tolerable outage durations in six places** and has never collected them: `OP-007` §7, `OP-011`, `OP-014`, `OP-002` §4.7, `NFR-047`, `SP-020`. §9.3 assembles them |
| **Analyse** | Impact over time — the point at which the consequence changes character, which is the MTPD |
| **Validate** | **Not done.** §9.6 states this plainly; validation is a business-owner activity |

**MTPD** = maximum tolerable period of disruption: the point beyond which the damage becomes
irreversible or disproportionate. **RTO must be shorter than MTPD**, with margin.

### 9.3 The analysis, assembled from existing evidence

| Business process | Service | **MTPD** | Basis — **already stated in the estate** | Impact at MTPD |
|---|:--:|:--:|---|---|
| **Payment acceptance** | `S-06` | **~1 h** | `NFR-048` 99.95% ⇒ 22 min/month; `IN-007` multi-gateway failover exists for this | Revenue stops; customers leave the counter; cash handling risk rises |
| **Job creation and dispatch, branches open** | `S-01`, `S-09` | **4 h** | **`OP-007` §7: *"4 hours before customer impact becomes reputational"*** | Paper backlog exceeds same-day re-entry capacity; SLA clocks breach in bulk |
| **Customer booking** | `S-07` | **4 h** | `OP-007` §7 — hotline takes bookings on paper for up to 4 h | Bookings lost rather than deferred |
| **Sign-in / identity** | `S-03` | **~1 h** | `PE-001` §9.2 — *"a total-outage dependency"*; every process above depends on it | Everything above fails simultaneously |
| **Field technician work** | `S-08` | **24 h** | **`NFR-047`** — the app holds 24 hours offline and syncs on recovery | Beyond 24 h, queued work is at risk (`OP-011` §6 makes unsynced field work a `Sev1`) |
| **Invoicing** | `S-01`, `S-06` | **8 h** | `OP-007` §7 — manual invoice from the fallback pack, reserved manual range | VAT sequence integrity at risk; `DT-011` reconciliation load |
| **Month-end close** | `S-01`, `S-15` | **1 working day** | `OP-007` §7 and `SP-020`'s defined close-calendar slack | Close slips; statutory timetable compresses |
| **Statutory filing (Mushak, VAT)** | `S-01`, `S-12` | **Deadline minus 4 h** | `OP-013` §4.1 — a statutory output missing its deadline is `Sev1` **regardless of impact** | **Penalty. Not recoverable by working faster** |
| **Payroll run** | `S-01` | **Deadline minus 1 day** | `OP-002` §4.3 — W5 hypercare must contain one full payroll run | Statutory and employment consequence |
| **Residency-classified data availability** | **`S-12`** | **≈ 2 h** | Gates every `T5` read (`PE-006` §7.2); `PE-008` `SV-03` makes `Z4` unavailability `Sev1` | **See §9.4 — this is the row that does not work** |
| Warehouse / analytics | `S-15` | 24 h | Reporting, not transacting | Decisions delayed, not lost |
| Vendor, brand, partner portals | `S-14`, `S-17`, `S-21` | 24–48 h | Business-hours services with manual alternatives | Counterparty friction |

### 9.4 The row that does not work

> **`MIM-F-02`. `S-12`'s MTPD is approximately two hours and its achievable recovery time is
> unbounded.**

| Fact | Source |
|---|---|
| `Z4` unavailability is `Sev1` and gates every `T5` read | `PE-008` `SV-03`; `PE-006` §7.2 |
| The only lawful recovery route — resident-to-resident restore — **has no resident DR target** | `AUDIT-017` `OP-01`, **CRITICAL** |
| The regional route is **a regulatory act** under `NFR-086b`, requiring Authority notification and a documented safeguard **before** execution | `OP-012` §4.3, `RD-01` |
| `PE-007` §7.5 records the decision as **forced and unmade** | `PE-007` |
| `PE-008` `SLO-08` therefore reports `Z4` separately and **never folds it into an estate SLO** | `PE-008` `Z4-01`…`Z4-04` |

**The BIA's contribution is to state the consequence in business terms**, which is what `PE-007`
§7.5's forced decision needs and does not have: at hour three of a resident-store outage, the
platform cannot serve residency-classified fields, cannot produce the statutory outputs that depend
on them, and **has no lawful route to recovery that an engineer may take**. `MIM-33`'s degraded
operation is a holding position measured in hours, and §9.3 says the process it holds has an MTPD
measured in hours too.

### 9.5 Climate scenarios — ISO 22301 Amd 1:2024

`SV-001` §4.4 determined that climate change is a relevant issue to this SMS. ISO 22301 Amd 1:2024
requires it in the context; ISO/TS 22317 requires the BIA's assumptions to reflect it.

| Scenario | Affects | Why it is not a generic outage |
|---|---|---|
| **Flood or cyclone at `BD-R`** | `S-12` | **Residency means the exposure cannot be engineered away by moving the data.** A single Bangladeshi facility is the design, not an accident |
| **Branch closure for days** (flood, cyclone, grid) | Branch operations | **Not a system outage.** The out-of-band tree (`OP-013` §4.10) is exercised against a system failure of hours; this is a **site** unreachable for days |
| **Regional grid or connectivity failure** | Branch and field connectivity (`PE-001` §8.1) | The platform is up and unreachable — which no runbook §5 currently covers |
| **Workforce unavailability** | The rota | **A climate event that closes branches also prevents seven engineers reaching connectivity.** `SV-004` §10.2 requires a laptop and connectivity within 15 minutes |

| # | Rule |
|---|---|
| **`MIM-47`** | **`PE-007`'s drill programme includes at least one site-level climate scenario per year**, and the out-of-band communication drill (`OP-013` `OB-03`) is exercised against **a branch unreachable for days**, not a system outage of hours |
| **`MIM-48`** | **The rota's continuity assumption is stated and tested**: what happens when the on-call primary and secondary are both in a flood-affected district. **The answer today is that nothing happens, because nobody has asked** |

### 9.6 What this BIA is not

> **`MIM-F-03`. This is a desk analysis assembled from durations already stated in the estate. It has
> not been validated with business owners, and ISO/TS 22317:2021 requires validation.**

| Present | Absent |
|---|---|
| Scope, collection, impact-over-time analysis | **Validation with each process owner** |
| MTPD per process, traced to an existing statement | Financial quantification per hour of outage |
| The `S-12` contradiction, stated | The Steering decision it demands |
| Climate scenarios, per Amd 1:2024 | A full risk assessment (ISO 22301 §8.2.3) |

**It is offered as the first BIA the programme has had, not as the last one it needs.** `MIM-Q-04`
carries the validation.

---

## 10. The Post-Incident Review Procedure

**`OP-016` is a good document and it is a method and a template.** `PGD-000` records what is missing:
*"a post-incident template with no procedure behind it."* This is the procedure.

### 10.1 Three artefacts called "PIR"

`AUDIT-017` records that three distinct artefacts share the abbreviation. Disambiguated:

| Term | Reviews | Owner | Trigger |
|---|---|---|---|
| **Post-incident review (PIR)** | **An incident** | Independent facilitator; register held by the Head of ITSM | `OP-016` §4.1's eleven triggers |
| **Post-implementation review** | **A change** | `RL-001` CAB | Every emergency, failed or major change (`M66` `BRU-ITS-10`) |
| **Wave post-implementation review** | **A wave's delivery** | Programme Office, [`RL-005`](../12_Release_Deployment_and_Transition/RL-005_Post_Implementation_Review_Standard.md) | Wave exit |

> **`MIM-49`. In Category 11, "PIR" means post-incident review and nothing else**, and any citation
> of another kind names its owning document (`SMF-26`).

### 10.2 The facilitator

`OP-016` `RV-04` requires the facilitator not to be the person who ran or fixed the incident. That is
a constraint; this is the mechanism.

| Element | Specification |
|---|---|
| **Pool** | **A named pool of 4–6 trained facilitators** across Platform, Security, Support, QA and the Quality Manager |
| **Independence test** | Not the IC, not the fixer, **and not the service owner** of the affected service |
| **Training** | Two co-facilitated reviews before leading one (`SV-001` §8.5) |
| **Assignment** | By the Head of ITSM **at declaration**, not at closure |
| **`Sev1` escalation** | The Quality Manager or an external facilitator where the incident involved a **cross-team dispute**, personal data, or a repeat cause |

> **`MIM-50`. The facilitator is assigned when the incident is declared.** `OP-016` `RV-01` already
> requires the review to be *scheduled* at declaration; assigning the facilitator then is what makes
> the schedule real, and it puts someone in the incident channel whose only job is to notice what
> the review will need.

### 10.3 Scheduling, and why reviews slip

| Deadline | Mechanism |
|---|---|
| `Sev1` — **5 working days** (`OP-016` §4.1) | **Booked at declaration**, in the calendar, with attendees, before anyone knows the outcome |
| `Sev2` — **10 working days** | As above |
| Timeline circulated **beforehand** | `OP-016` §4.5 — *the meeting corrects and interprets it, it does not build it* |
| Draft report within **2 working days** of the meeting | `OP-016` §4.5 |

| # | Rule |
|---|---|
| **`MIM-51`** | **A review that is not booked at declaration will slip past the point of accurate memory.** `OP-016` §4.3 requires responder interviews within **3 working days** *"while memory is accurate"*, and a meeting arranged on day four has already lost the material |
| **`MIM-52`** | **A review may be waived only by the CTO, in writing, with the reason recorded in the register** (`OP-016` `RV-03`). **The register shows waivers, so a pattern of waivers is visible** — and `SV-005` `HCT-31` reports the count |
| **`MIM-53`** | **Near misses are reviewed** (`OP-016` `RV-02`). They are the cheapest learning available, because nobody is defensive about them |

### 10.4 Running it

`OP-016` §4.5's structure is adopted whole — 10 minutes timeline, 25 contributing factors, 10 what
went well, 25 actions and owners, 10 publication. Three procedural additions:

| # | Rule |
|---|---|
| **`MIM-54`** | **The facilitator opens with `OP-016` `BL-02`'s sentence, verbatim**, every time: *"We are here to find out what made this outcome likely, not who produced it. If the answer is that a person made a mistake, the question becomes what made that mistake easy."* Saying it every time is what makes it believed the time it matters |
| **`MIM-55`** | **`BL-01`'s test is applied before the report is issued**: if the output would change depending on who is in the room, the review is not blameless yet |
| **`MIM-56`** | **The review names what went well** (`OP-016` `CF-04`). Reviews that only find faults stop being attended honestly, and the mitigation that limited the damage is as important as the cause |

### 10.5 Actions — the part that decides whether any of this matters

`OP-016` `AC-01`…`AC-08` are adopted whole: one named owner, a realistic date, a
Prevent/Detect/Mitigate/Respond/Document classification, **at least one Detect or Prevent for any
`Sev1`**, tracked in `M23`, escalated at the due date, closed with evidence, and closed as
`accepted risk` where they will not be done.

**The procedure `OP-016` does not contain:**

| Step | Who | When |
|---|---|---|
| Actions entered in `M23` as corrective actions | Facilitator | **Within 2 working days of the meeting** |
| Overdue actions listed | Head of ITSM | **Weekly** |
| Overdue actions escalated to the CTO | Head of ITSM | At the due date (`AC-06`) |
| Action closure rate reported | Head of ITSM | **Monthly**, to the Service Management Board |
| Actions still open at 90 days | Head of ITSM | **Re-presented to the Board for a decision: fund, re-plan, or accept the risk** |

> **`MIM-57`. An action open at 90 days is re-presented for a decision, not chased a fourth time.**
> The three outcomes are fund it, re-plan it, or accept the risk with a named accepter. **Chasing is
> not a fourth option, and pretending it is produces the register of open actions that every
> organisation has and nobody reads.**

### 10.6 The register

`OP-016` §4.8's field set is adopted whole. The operation of it:

| Activity | Who | Cadence |
|---|---|:--:|
| Entry created | Facilitator | At declaration |
| Completed and published internally **without names** | Facilitator | Within 2 working days of sign-off (`OP-016` §4.10) |
| **Reviewed for recurrence** against prior tags | Head of ITSM | **Monthly**, with the Quality Manager and CTO (`OP-016` `RG-01`) |
| **Quarterly pattern report** | Head of ITSM | To the Steering Committee — **top contributing-factor tags, action closure rate, recurrence count — not a list of incidents** (`RG-01`) |

---

## 11. Measurement

### 11.1 Response

Adopted from `OP-013` §4.12 and `SV-004` §12; not restated.

### 11.2 Problem and review — the numbers that show whether anything changes

| Measure | Definition | Target | Source |
|---|---|:--:|---|
| **Repeat incidents** | Same cause within 90 days | **Declining.** Each one is a failure to act on a prior review | Incident register |
| **Problems opened per quarter** | Reactive + proactive | **Rising then falling** — a rise means detection is working | Problem register |
| **Proactive share** | Problems raised before an incident ÷ all problems | ≥ 20% by W4 | Problem register |
| **Problem age** | Median days open | < 45 days | Problem register |
| **Review completion** | Reviews held within the `OP-016` §4.1 deadline ÷ required | **100%** | PIR register |
| **Review waivers** | Waived ÷ required, cumulative across waves | **< 5%**, and the trend is the signal (`HCT-31`) | PIR register |
| **Action closure** | Actions closed with evidence by the due date ÷ due | ≥ 85% | `M23` |
| **Detect/Prevent share** | `Sev1` reviews with ≥ 1 Detect or Prevent action ÷ all `Sev1` reviews | **100%** (`OP-016` `AC-04`) | PIR register |
| **Document-only reviews** | Reviews whose actions are all *Document* ÷ all | **< 10%** — *"a review whose actions are all Document has not changed the system"* (`AC-03`) | PIR register |
| **Organisational-cause share** | Reviews tagged `deferred-work`, `single-person` or `authority-gap` ÷ all | **Reported, not targeted** (`TG-01`, `MIM-45`) | PIR register |

> **`MIM-58`. The two measures that matter most are `repeat incidents` and `Detect/Prevent share`.**
> Everything else measures whether the process ran. **Those two measure whether it worked** — the
> first because recurrence is the only proof that a cause was not removed, the second because a
> review producing only documentation has produced a feeling.

### 11.3 The quarterly pattern report

One page to the Steering Committee: top five contributing-factor tags · repeat-incident count and
trend · action closure rate and the 90-day list · problems opened, closed and their median age ·
waiver count cumulative across waves · **and, where `TG-01`'s three organisational tags dominate, a
plain statement that no engineering action will address them.**

---

## 12. Governing Rules — Consolidated

| # | Rule | § |
|---|---|:--:|
| **`MIM-01`** | `OP-013` §4.1/§4.5/§4.6/§4.8/§4.9 and `OP-016` §4.2–§4.10 are **adopted whole and never restated** | 3 |
| **`MIM-02`** | Major incident adds a commander, a cadence and a review — **not a severity** | 4.1 |
| **`MIM-03`** | `Sev2` → major at 60 minutes is **automatic and announced** | 4.1 |
| **`MIM-04`** | Anyone may declare; **an over-declared `Sev1` is never reviewed against the declarer** | 4.1 |
| **`MIM-05`** | **No Category 11 document defines a severity scale** | 4.2 |
| **`MIM-06`** | Severity on impact, re-assessed as understanding changes, **never adjusted to avoid a review or a metric** | 4.2 |
| **`MIM-07`** | A severity dispute is settled by the IC in ten seconds and reviewed afterwards | 4.2 |
| **`MIM-08`** | **A maintenance window past its announced end is an incident, declared at the announced end** | 4.2 |
| **`MIM-09`** | **The IC does not troubleshoot** | 5.2 |
| **`MIM-10`** | The IC does not communicate externally | 5.2 |
| **`MIM-11`** | The IC does not take the business decision | 5.2 |
| **`MIM-12`** | **The IC does not make a breach determination** | 5.2 |
| **`MIM-13`** | **Every line of enquiry is time-boxed at the decision point** | 5.3 |
| **`MIM-14`** | **Restoration precedes diagnosis** | 5.3 |
| **`MIM-15`** | An incident closes on restoration; **the problem stays open until the cause is removed** | 8.1 |
| **`MIM-16`** | The IC exercises `OP-013` §4.8's on-call column without permission; CAB reviews within 2 days | 5.4 |
| **`MIM-17`** | Missing authority is **named aloud with a deadline**, never waited for silently | 5.4 |
| **`MIM-18`** | An incident channel with thirty observers is one the responders stop using | 5.5 |
| **`MIM-19`** | **An unacknowledged command handover leaves an incident with no owner** | 5.6 |
| **`MIM-20`** | **No closure with an unknown cause and no problem record** | 5.7 |
| **`MIM-21`** | **One Communications Owner, one voice** | 6.2 |
| **`MIM-22`** | **Every message carries the next update time, and the commitment is met even with nothing new** | 6.2 |
| **`MIM-23`** | The first branch message **contains** the fallback instruction | 6.2 |
| **`MIM-24`** | No message states an unconfirmed cause | 6.2 |
| **`MIM-25`** | The status page is the single external source of truth — **and it has no independent hosting** | 6.2 |
| **`MIM-26`** | If the status page is down, **SMS to branch managers plus a website banner**, and the first message says which is authoritative | 6.3 |
| **`MIM-27`** | Suspected compromise engages security and the DPO **in parallel**; classification leaves this procedure | 7.1 |
| **`MIM-28`** | **The `NFR-094` clock runs from detection** | 7.1 |
| **`MIM-29`** | DPO assessment within **24 hours**; **72 hours is a planning assumption, never stated as law** | 7.1 |
| **`MIM-30`** | **For a security incident, evidence preservation overrides speed of restoration** — the one inversion of `MIM-14` | 7.1 |
| **`MIM-31`** | **Declaring a disaster is an escalation of authority, not an admission of failure** | 7.2 |
| **`MIM-32`** | **The `Z4` route is never chosen by an engineer at 02:00** | 7.2 |
| **`MIM-33`** | On resident-store loss: **degraded operation without residency-classified fields**, CTO + Legal + DPO before any restore route | 7.2 |
| **`MIM-34`** | A service problem is not a platform incident | 7.3 |
| **`MIM-35`** | **Safety leaves this procedure immediately** | 7.3 |
| **`MIM-36`** | **A problem closes only on verified absence of recurrence** | 8.1 |
| **`MIM-37`** | **The execution ledger is a problem-detection instrument** — a procedure run 3× in a quarter raises a candidate | 8.2 |
| **`MIM-38`** | **"Human error" is never a cause** | 8.3 |
| **`MIM-39`** | **"Third-party failure" is never a complete cause** | 8.3 |
| **`MIM-40`** | An investigation with no cause found is **closed as such, with the detection gap as the finding** | 8.3 |
| **`MIM-41`** | **A known error is published when a workaround exists, not when the cause is understood** | 8.4 |
| **`MIM-42`** | **The verification period is set before the fix** | 8.5 |
| **`MIM-43`** | Every problem raises an `M23` corrective action | 8.6 |
| **`MIM-44`** | A problem not being fixed is closed as **`accepted risk` with a named accepter** | 8.6 |
| **`MIM-45`** | **When the three organisational tags dominate a quarter, the report says so plainly** | 8.7 |
| **`MIM-46`** | **A recovery objective not derived from an impact analysis is a preference** | 9.1 |
| **`MIM-47`** | `PE-007`'s drills include **a site-level climate scenario yearly**; the comms drill tests a branch unreachable for **days** | 9.5 |
| **`MIM-48`** | **The rota's continuity assumption is stated and tested** | 9.5 |
| **`MIM-49`** | In Category 11, **"PIR" means post-incident review and nothing else** | 10.1 |
| **`MIM-50`** | **The facilitator is assigned at declaration** | 10.2 |
| **`MIM-51`** | A review not booked at declaration slips past accurate memory | 10.3 |
| **`MIM-52`** | Waiver only by the CTO, in writing, **visible in the register** | 10.3 |
| **`MIM-53`** | **Near misses are reviewed** | 10.3 |
| **`MIM-54`** | The facilitator opens with `BL-02`'s sentence, **verbatim, every time** | 10.4 |
| **`MIM-55`** | `BL-01`'s test is applied before the report issues | 10.4 |
| **`MIM-56`** | **The review names what went well** | 10.4 |
| **`MIM-57`** | **An action open at 90 days is re-presented for a decision — fund, re-plan or accept — never chased a fourth time** | 10.5 |
| **`MIM-58`** | **The two measures that matter are repeat incidents and Detect/Prevent share** | 11.2 |

**Findings raised by this document**

| # | Finding | Severity | Owner |
|---|---|:--:|---|
| **`MIM-F-01`** | **Severity has four published claimants.** Three corrections outstanding since 2026-08-20 (`SP-005` §5/§12, `SP-031` §2, `TS-018` §2) and a fourth arose 2026-08-19 (`PE-008` §8.5, which also reduces four levels to three). All four are one-line edits this category cannot make | **HIGH** | Business Process Lead, QA Lead, Enterprise Architecture |
| **`MIM-F-02`** | **`S-12`'s MTPD is ≈ 2 hours and its achievable recovery time is unbounded.** The BIA states in business terms the consequence `PE-007` §7.5's forced decision needs and does not have | **CRITICAL** *(inherits `AUDIT-017` `OP-01`)* | CTO + Legal + DPO |
| **`MIM-F-03`** | **This BIA is a desk analysis and has not been validated with business owners**, which ISO/TS 22317:2021 requires. It is the programme's first BIA, not its last | MEDIUM | Operations Director |
| **`MIM-F-04`** | **The estate states tolerable outage durations in at least six places and had never collected them.** They were consistent enough to assemble a BIA from — which is a credit to the content estate and an indictment of the absence of a cross-reference index (`RR-006`, unwritten) | MEDIUM | Programme Office |
| **`MIM-F-05`** | **No runbook §5 covers "the platform is up and unreachable"** — a regional connectivity or grid failure — although `PE-001` §8.1 designs branch connectivity and §9.5 identifies it as a climate scenario | MEDIUM | Service owners (`SV-003`) |
| **`MIM-F-06`** | **The rota has no stated continuity assumption.** `SV-004` §10.2 requires a laptop and connectivity within 15 minutes; nothing states what happens when primary and secondary are both in a flood-affected district | MEDIUM | Head of ITSM + CTO |

---

## 13. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| **`SV-006-D-01`** | What makes an incident "major" | (a) Every `Sev1` only; (b) a separate judgement call; (c) **every `Sev1`, plus `Sev2` spanning teams or exceeding 60 min** | **(c)** | **Derived, not chosen**: `OP-013` §4.1 already states when an Incident Commander is required, and a major incident is exactly an incident with a commander. (b) creates a fifth judgement in an estate with four severity scales | `MIM-02`, `MIM-03`; no new scale is created |
| **`SV-006-D-02`** | Problem entry thresholds | (a) Leave to judgement, as `SP-031` §5.5 does; (b) **seven stated thresholds** | **(b)** | `M66` `AUT-ITS-07` automates problem raising *"above the configured threshold"* and nothing configures it. `PT-01` is set to `OP-016` §4.1's existing 3-in-90-days so the review and problem triggers agree | Seven automatable rules; `M66`'s configuration has a source |
| **`SV-006-D-03`** | Whether to perform a BIA | (a) Defer to a future continuity workstream; (b) **assemble one from durations already stated in the estate, and declare it unvalidated** | **(b)** | ISO/IEC 20000-1 §8.7.3 requires continuity objectives to be **derived** from a BIA. The estate had the raw material in six places and had never collected it. **An unvalidated BIA that names `S-12`'s contradiction beats an absent one** | §9; `MIM-F-02`, `MIM-F-03`; validation carried as `MIM-Q-04` |
| **`SV-006-D-04`** | Where PIR actions are tracked | (a) A private incident action list; (b) **`M23` CAPA** | **(b)** | `OP-016` `AC-05` already requires it and `M23` `BRU-QMS-02` gives it teeth. `SV-001` `SMF-22` brings support inside the ISO 9001 certified scope by the same route | `MIM-43`; §10.5's weekly and monthly mechanics |
| **`SV-006-D-05`** | Status page unavailability | (a) Accept the single point of failure; (b) **declare a fallback channel and state which is authoritative** | **(b)** as a holding position | `AUDIT-017` `OP-14` is open and independent hosting is unfunded. A documented fallback is not a solution, and saying so is what keeps the procurement on the list | `MIM-26`; the procurement is the same one as `SV-002` `PSL-Q-03` and `SV-004` `OCP-Q-04` — **one account, three requirements** |

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|:--:|---|
| **`MIM-Q-01`** | **Will the four severity corrections be made** — `SP-005` §5/§12, `SP-031` §2, `TS-018` §2, `PE-008` §8.5? | Business Process Lead, QA Lead, Enterprise Architecture | **W1** | `MIM-F-01`; the estate has a control with four owners until they are |
| **`MIM-Q-02`** | Who are the 4–6 facilitators, and when are they trained? | Head of ITSM | **W1** | `OP-016` `RV-04`'s independence is unachievable with a pool of one |
| `MIM-Q-03` | Is the problem-management practice run manually from W1, or does `SV-001-D-04` bring `CD-163`'s `FR-ITS-013`…`017` forward? | CTO | W1 | §8's automation; manual is workable and slower |
| **`MIM-Q-04`** | **Will business owners validate the §9 BIA**, per ISO/TS 22317:2021, and quantify the financial impact per hour? | Operations Director + CFO | **W2** | `MIM-F-03`; and `RQ-006` cannot amend `NFR-007` without it |
| **`MIM-Q-05`** | **Is `PE-007` §7.5's `Z4` recovery decision taken** — a resident DR target, or a pre-agreed Authority position? | CTO + Legal + DPO | **W2** | `MIM-F-02`; `AUDIT-017` `OP-01`, still CRITICAL and open |
| `MIM-Q-06` | Is independent status-page hosting funded, in the same account as external synthetic monitoring and the paging platform? | CTO + CFO | W2 | `MIM-26`, `PSL-Q-03`, `OCP-Q-04` — **one procurement** |
| `MIM-Q-07` | Has `LG-024` set the PDPA 2026 notification period, or does the 72-hour planning assumption still stand? | Legal Counsel + DPO | W2 | `MIM-29`; `AUDIT-017` `OP-18` |
| `MIM-Q-08` | Does `M23` accept incident and problem corrective actions into its CAPA queue, and is support inside the ISO 9001 certified scope at the next surveillance audit? | Quality Manager | W2 | `MIM-43`; `SMF-Q-06` |
| `MIM-Q-09` | **What is the rota's continuity assumption** when primary and secondary are both unreachable? | Head of ITSM + CTO | W2 | `MIM-F-06`, `MIM-48` |

---

## 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | "Major incident" is defined and its relationship to `Sev1` is **derived from an existing statement** | §4.1; `SV-006-D-01` from `OP-013` §4.1's IC row |
| `AC-02` | Severity ownership is closed, with every outstanding correction listed and costed | §4.2 — four rows, each with its consequence |
| `AC-03` | No document in this category defines a severity scale | `MIM-05`; verified across all six `SV` documents |
| `AC-04` | The command procedure has a cadence, decision points and explicit prohibitions | §5.1, §5.2, §5.3 |
| `AC-05` | All three escalation seams are stated with an owner on each side | §7 — security, disaster, business |
| `AC-06` | Problem entry has **numeric thresholds**, not judgement | §8.2 — `PT-01`…`PT-07` plus five proactive signals |
| `AC-07` | Problem closure requires verified absence of recurrence over a period set in advance | `MIM-36`, `MIM-42` |
| `AC-08` | **A business impact analysis exists, with MTPD per process traced to an existing source** | §9.3 — twelve processes, each with its basis |
| `AC-09` | The BIA's limitations are declared | §9.6; `MIM-F-03` |
| `AC-10` | Climate scenarios are included, per ISO 22301 Amd 1:2024 | §9.5 — four scenarios |
| `AC-11` | The PIR **procedure** — facilitator, scheduling, actions, register — is specified without restating `OP-016`'s method | §10; `MIM-01` |
| `AC-12` | Measurement distinguishes *did the process run* from *did it work* | §11.2; `MIM-58` |
| `AC-13` | Every relative link resolves; no rule uses the form `SV-nn` | Verified at issue |

**Definition of done.** Complete when every criterion is met, `PGD-000` is updated with a fresh
enumeration timestamp, and the approver has signed **with the Quality Manager for §8 and the
Operations Director for §9**. **`AC-02` depends on four edits in documents this category does not
own** (`MIM-Q-01`), and **`AC-08`'s analysis is unvalidated** (`MIM-Q-04`).

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `SV-001` §6.2, §6.4, §6.7 | The practice map, the three record relationships, the severity adjudication |
| Upstream | `SV-002` §9.1 | A repeat SLO miss becomes a problem (`PT-06`) |
| Upstream | `SV-003` §9.1, §12 ledger | Blast radius at declaration; **the ledger as a problem-detection instrument** (`MIM-37`) |
| Upstream | `SV-004` | The page that starts everything here |
| Upstream | `SV-005` `HX-17`, `HCT-31` | Hypercare PIRs, unwaivable; cumulative waiver counts |
| Upstream | [`PE-007`](../10_Infrastructure_DevOps_and_Environments/PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md) §6, §7 | The disaster seam, and the forced `Z4` decision §9.4 supplies the impact statement for |
| Upstream | [`PE-008`](../10_Infrastructure_DevOps_and_Environments/PE-008_Observability_and_Monitoring_Design.md) §8 | Detection; and §4.2's fourth severity claimant |
| Upstream | [`SC-011`](../05_Security_Privacy_and_Compliance/SC-011_Security_Incident_Response_Plan.md) | The security seam (§7.1) |
| Downstream | [`RL-001`](../12_Release_Deployment_and_Transition/RL-001_Release_Management_and_Versioning_Policy.md) §9 | Emergency change during an incident, reviewed by CAB within 2 days |
| Downstream | `M23` | Every corrective action (`MIM-43`) |
| Downstream | [`RQ-006`](../01_Requirements_Engineering/RQ-006_Non_Functional_Requirements_Specification.md) | §9's BIA is the basis on which `NFR-007` should be tiered |
| Downstream | `GV-005` RAID | Nine open questions |
| Lateral | [`OP-013`](../../project_content/17_Operations_Support_and_Runbooks/OP-013_On_Call_Escalation_and_Handover_Content.md), [`OP-016`](../../project_content/17_Operations_Support_and_Runbooks/OP-016_Post_Incident_Review_Template_and_Register.md) | **Adopted whole**; this is the procedure around them |
| Lateral | [`OP-004`](../../project_content/17_Operations_Support_and_Runbooks/OP-004_Incident_Communication_Template_Set.md), [`OP-005`](../../project_content/17_Operations_Support_and_Runbooks/OP-005_Status_Page_and_Maintenance_Notice_Copy.md), [`OP-012`](../../project_content/17_Operations_Support_and_Runbooks/OP-012_Disaster_Recovery_and_Continuity_Playbook.md), [`OP-014`](../../project_content/17_Operations_Support_and_Runbooks/OP-014_Manual_Fallback_Procedure_Set.md) | Words, status page, disaster playbook, fallback |
| Lateral | [`SP-031`](../../project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md), [`SP-005`](../../project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md), [`SP-030`](../../project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md) | The three-step problem SOP §8 extends; the two ladders that are not this one |

---

## 17. References

**Within this repository**
[`PGD-000`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
`SV-001`, `SV-002`, `SV-003`, `SV-004`, `SV-005` ·
[`PE-007`](../10_Infrastructure_DevOps_and_Environments/PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md) ·
[`PE-008`](../10_Infrastructure_DevOps_and_Environments/PE-008_Observability_and_Monitoring_Design.md) ·
[`SC-011`](../05_Security_Privacy_and_Compliance/SC-011_Security_Incident_Response_Plan.md) ·
[`QA-010`](../08_Quality_Engineering_and_Test/QA-010_Defect_Management_and_Quality_Gate_Standard.md) ·
[`RL-001`](../12_Release_Deployment_and_Transition/RL-001_Release_Management_and_Versioning_Policy.md) ·
[`RL-005`](../12_Release_Deployment_and_Transition/RL-005_Post_Implementation_Review_Standard.md) ·
[`RQ-006`](../01_Requirements_Engineering/RQ-006_Non_Functional_Requirements_Specification.md) ·
[`GV-005`](../00_Programme_Governance_and_Control/GV-005_RAID_Register.md)

**Workspace**
[`OP-013`](../../project_content/17_Operations_Support_and_Runbooks/OP-013_On_Call_Escalation_and_Handover_Content.md) ·
[`OP-016`](../../project_content/17_Operations_Support_and_Runbooks/OP-016_Post_Incident_Review_Template_and_Register.md) ·
[`OP-004`](../../project_content/17_Operations_Support_and_Runbooks/OP-004_Incident_Communication_Template_Set.md) ·
[`OP-005`](../../project_content/17_Operations_Support_and_Runbooks/OP-005_Status_Page_and_Maintenance_Notice_Copy.md) ·
[`OP-007`](../../project_content/17_Operations_Support_and_Runbooks/OP-007_Runbook_Core_ERP_Platform.md) ·
[`OP-012`](../../project_content/17_Operations_Support_and_Runbooks/OP-012_Disaster_Recovery_and_Continuity_Playbook.md) ·
[`OP-014`](../../project_content/17_Operations_Support_and_Runbooks/OP-014_Manual_Fallback_Procedure_Set.md) ·
[`SP-031`](../../project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) ·
[`SP-005`](../../project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md) ·
[`M66`](../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66_Internal_IT_Service_Management.md) ·
[`05-06`](../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md) ·
[`AUDIT-017`](../../project_content/_AUDIT/AUDIT-017_Category_17_OP_Content_Audit.md)

**External standards and sources** *(each verified 2026-08-19)*

| Source | Verified |
|---|:--:|
| ISO/IEC 20000-1:2018 §8.6.1, §8.7.1, §8.7.3 | 2026-08-19 |
| ISO/IEC 20000-1:2018/Amd 1:2024 · https://www.iso.org/standard/88434.html | 2026-08-19 |
| **ISO 22301:2019 §8.2 business impact analysis; Amd 1:2024 climate action changes**, published February 2024 · https://www.iso.org/standard/88412.html | 2026-08-19 |
| **ISO/TS 22317:2021** — business impact analysis guidelines: scoping, data collection, impact over time, validation | 2026-08-19 |
| ISO 9001:2015 cl. 10.2 — nonconformity and corrective action | 2026-08-19 |
| ITIL 4 — incident and problem management practices, reactive/proactive split | 2026-08-19 |
| Incident command practice — a named commander who coordinates and does not troubleshoot *(as cited by `OP-013`, verified there 2026-08-20)* | 2026-08-19 |

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Head of IT Service Management | Initial issue. Rule space `MIM` allocated after verification against 777 files. **Severity ownership closed with four outstanding corrections listed** — three from `AUDIT-017` `OP-04` and one against `PE-008` §8.5. Major incident derived from `OP-013` §4.1's IC requirement. Problem management given **seven numeric entry thresholds** where `SP-031` §5.5 had three steps. **The programme's first business impact analysis**, assembled from tolerable-outage durations stated in six places across the estate and never collected, including the climate scenarios ISO 22301 Amd 1:2024 requires. PIR procedure supplied behind `OP-016`'s template. Five decisions, six findings, nine open questions | Chief Technology Officer, **with the Quality Manager (§8) and the Operations Director (§9)** *(all pending)* |
| **1.1** | **2026-08-19** | Head of IT Service Management | **Conformance to `RR-002` `IDC-08`** (timestamp and denominator in `rule_prefix:`). **Two violations of `SMF-26`/`IDC-07` in this document's own rules corrected** — bare `SV-07`, `SV-03` and `SV-05` citations now qualified as `OP-013`'s, with a note that `PE-008` §8.5 also defines an `SV-03` meaning something else. Found by extraction during this category's audit, in the document that depends on the rule most. | As above |

---

*`SV-006` · Category 11 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
