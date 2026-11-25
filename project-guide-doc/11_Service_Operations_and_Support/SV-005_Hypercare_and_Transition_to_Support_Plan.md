---
id: SV-005
title: Hypercare and Transition-to-Support Plan
category: 11 — Service Operations & Support
code: SV
project: 1000FiX ERP System v2.0
version: 1.1
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Head of IT Service Management, with the Programme Manager
approver: Programme Manager, jointly with the Chief Technology Officer and the CFO
standards_basis: >
  ISO/IEC 20000-1:2018 + Amd 1:2024 §8.5.2 service design and transition (transition of new and
  changed services into live operation), §7.1 resources, §7.6 knowledge · ITIL 4 service design
  and transition · ISO 21502:2020 §7.6 resource management and §4.5 benefits sustainment ·
  ERP hypercare practice — elevated staffing, floor-walking, measured exit criteria
traces_to: >
  PGD-000 SV-005 row (◐ OP-002) · SV-001 §8.4 (the establishment), SMF-15 (the shared pool) ·
  OP-002 §4.1–§4.12 (adopted by citation) · AUDIT-017 §4, OP-11, OP-12 ·
  06-01 wave months · 06-02 §4 gate criteria · OP-002-OI-01, OI-04 · M66 §18 Q-02
depends_on: >
  SV-001 · SV-002 · SV-003 · SV-004 (this category — the rota hypercare competes with) ·
  RL-002 (issued) · RL-003 (issued) · RL-004 (issued) · RL-005 (issued) ·
  CH-001 (issued) · CH-002 (issued) · CH-005 (issued) · GV-004 (issued) · GV-007 (issued) ·
  QA-010 (issued) · MG-006 (issued) · 06-06 Deployment and Operations Plan (DOES NOT EXIST) ·
  RF-006 Content Decision Log (DOES NOT EXIST)
verified_on: 2026-08-19
enumeration_timestamp: 2026-08-19 02:15 (+06)
rule_prefix: HCT — verified to return zero occurrences in identifier form across all 777 markdown files of the workspace before allocation, at 2026-08-19 02:15 (+06); re-verified against the 786-file baseline at 02:56 (+06). Conforms to RR-002 IDC-08
priority: P1
needed_by: W2
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# SV-005 — Hypercare and Transition-to-Support Plan

### Category 11 · Code `SV` · Rule space `HCT` · ISO/IEC 20000-1:2018 §8.5.2 · ISO 21502:2020 §7.6

---

> **`PGD-000` states the gap this document fills:** *"`OP-002` defines hypercare **plan content and
> exit criteria**. The resourcing and transfer mechanism is undefined, and hypercare recurs at
> **every one of nine waves**."*
>
> `OP-002` is a good document. It defines what hypercare is, ten entry conditions, a duration per
> wave, floor-walking ratios, a twice-daily cadence, six roles, a known-issue log, the rollback
> decision, **eighteen measured exit criteria** and an exit form. It is not missing anything a
> hypercare plan is normally asked for.
>
> **What it does not do is multiply.** Read its §4.3 duration table and add it up: **56 weeks of
> hypercare across a 156-week programme.** Apply its own §4.1 staffing rule — *"2× baseline T1, plus
> floor-walkers on site, plus the delivery team ring-fenced"* — to those 56 weeks and the answer is
> **roughly 680 person-weeks**, split across three cost pools with three different owners.
>
> **None of it is in the 1,513 PW build estimate. None of it is in the 520–775 PW content estimate.
> The largest of the three pools is invisible to both, because it is paid by branch staff.**
>
> §5 is that derivation. §7 is the transfer mechanism `PGD-000` says is undefined.

---

## 1. Purpose

This document states **what hypercare costs, who pays it, how many times, and how the platform
stops being a project and becomes a service**.

It exists because hypercare is the only activity in the programme that happens nine times and is
planned once. Every ERP programme that has slipped a wave "for stabilisation" slipped it because the
people who were supposed to build the next wave were still standing beside users in the last one —
and because nobody wrote down, in advance, that they would be.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The **recurrence** — nine hypercare periods, their calendar, and their overlap with delivery (§4) |
| 2 | The **cost derivation** — three pools, ~680 PW, with the arithmetic shown (§5) |
| 3 | The **resourcing decision** — who is ring-fenced, from where, and what it displaces (§6) |
| 4 | The **knowledge transfer mechanism** — the artefact set, its owners and its acceptance test (§7) |
| 5 | **Transition to business as usual** — what changes at exit, and how it is announced (§8) |
| 6 | **What changes wave to wave** — hypercare is not the same event nine times (§9) |
| 7 | The **collision with the on-call rota**, stated rather than discovered (§10) |
| 8 | **Hypercare fatigue** — the failure mode of the seventh one (§11) |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| **What hypercare is**: entry conditions `HE-01`…`HE-10`, durations, floor-walking ratios, cadence, roles, the known-issue log, the rollback decision, the **eighteen exit criteria `HX-01`…`HX-18`**, the exit form | [`OP-002`](../../project_content/17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md) | **Adopted whole by citation (`HCT-01`) and never restated.** `OP-002` is issued and complete at its own altitude; a second copy of eighteen exit criteria is a second copy to keep in step |
| Cutover itself — freeze, last transaction, parallel run, reconciliation | [`MG-006`](../09_Data_Migration_and_Cutover/MG-006_Cutover_Plan_and_Runbook.md), `DM-014` | Hypercare begins when cutover completes |
| The deployment sequence and go-live checklist | [`RL-002`](../12_Release_Deployment_and_Transition/RL-002_Deployment_Plan_and_Go_Live_Checklist.md) | A deployment is an event; hypercare is a posture |
| **Whether** a wave is ready to go live | [`RL-003`](../12_Release_Deployment_and_Transition/RL-003_Go_Live_Readiness_Assessment_and_Gate_Criteria.md) | Readiness decides go/no-go; this decides what happens after go |
| Which branches go live in which order | [`RL-004`](../12_Release_Deployment_and_Transition/RL-004_Rollout_and_Branch_Wave_Deployment_Plan.md) | §5.4's floor-walking volume is **driven by** `RL-004`'s tranching |
| The post-implementation review of the wave | [`RL-005`](../12_Release_Deployment_and_Transition/RL-005_Post_Implementation_Review_Standard.md) | A wave PIR reviews delivery; `SV-006` reviews incidents |
| Change impact, resistance, sponsorship, adoption measurement | [`CH-001`](../13_Training_Change_and_Adoption/CH-001_Organisational_Change_Management_Plan.md), [`CH-004`](../13_Training_Change_and_Adoption/CH-004_Adoption_Measurement_and_Reinforcement_Plan.md) | Adoption failure is **not a rollback trigger** (`OP-002` §4.7); it is a change problem |
| The champion network's charter and time release | [`CH-005`](../13_Training_Change_and_Adoption/CH-005_Super_User_and_Champion_Network_Charter.md) | **§5.4's largest cost pool depends on it** — the seam is stated in §6.4 |
| Refresher training content | `TR-024` | Hypercare feeds it; it does not own it |
| Defect severity and triage | [`QA-010`](../08_Quality_Engineering_and_Test/QA-010_Defect_Management_and_Quality_Gate_Standard.md), `TS-018` | `HX-01`…`HX-03` depend on the `S1`–`S4` scale |
| The permanent support model hypercare hands over to | `SV-001` | This document is the bridge; `SV-001` is the far bank |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Programme Manager** | §5's number, §6's ring-fencing decision, and the fact that both must be in the plan before W1 cutover |
| **CFO** | §5.6 — three cost pools, three owners, none funded |
| **Chief Technology Officer** | §6 and §10 — hypercare, the on-call rota and the next wave's build are competing for one pool of engineers |
| **Operations Director and branch managers** | §5.4 — the largest cost pool is **branch staff time**, and it is being asked for nine times |
| Head of IT Service Management | §7's transfer mechanism and §8's BAU handover |
| Change Lead | §6.4's seam with `CH-005`, and §9's per-wave differences |
| QA Lead | §7.3's defect and known-issue handover |
| Steering Committee | §5.7 and §11 — the number, and the failure mode of the seventh hypercare |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / section | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO/IEC 20000-1:2018 + Amd 1:2024** | §8.5.2 — new or changed services are **planned, with resources determined**, and transitioned into live operation against acceptance criteria | §5 determines the resources; §7 defines the transition; `OP-002` §4.8 supplies the acceptance criteria | **None in specification. Unmet in operation** — §5's resources are unfunded |
| Same | §7.1 resources; §7.6 knowledge | §6's resourcing; §7's transfer artefact set | None |
| **ISO 21502:2020** | §7.6 resource management; the practice that a project's resources are planned across its whole life, not per phase | §5's nine-wave total, rather than a per-wave figure that never gets added up | **This is the departure from current practice, not from the standard.** `OP-002` plans a hypercare; the standard requires the programme to plan all nine |
| **ITIL 4** | Service design and transition — knowledge transfer as an explicit deliverable, not a by-product | §7.2's five artefacts, each with an **acceptance test** | None |
| ERP hypercare practice | 2–8 weeks typical, extending to ~12 for complex phased rollouts; elevated staffing; measured exit | `OP-002` §4.3's durations sit inside that range; §9 states why three waves are at the top of it | None |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| **`OP-002`** | [`../../project_content/17_.../OP-002`](../../project_content/17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md) | **The whole of hypercare as a practice.** §4.1 the eight dimensions that change · §4.2 `HE-01`…`HE-10` entry · **§4.3 durations per wave and `HD-01`…`HD-04`** · §4.4 floor-walking ratios and `FW-01`…`FW-04` · §4.5 cadence and six roles · §4.6 the known-issue log · §4.7 the rollback decision and `RB-01`…`RB-04` · **§4.8 `HX-01`…`HX-18` and the waiver rule** · §4.9 the exit form · §4.10 BAU transition and `TX-01` · §4.11 what hypercare must produce for the next wave · §4.12 five open decisions |
| `06-01` Implementation Roadmap | [`../../1000fix_ERP_Module/06_.../06-01`](../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md) | The nine waves and their month ranges — the calendar §4.2 builds on |
| `06-02` §4 | Same folder | Wave gate criteria `G1-01`…`G4-09`, consumed by `HE-01` and `HX-11` |
| `OP-001` §4.7 | [`../../project_content/17_.../OP-001`](../../project_content/17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) | **The T1 baseline hypercare doubles**: 2 FTE at W1, 4 at W4, 6–8 at W8 |
| `SV-001` §8.4, `SMF-15` | This category | The single establishment table, and the rule that the rota, the T3 line and hypercare are **the same people** |
| `SV-004` §6.6, `OCP-F-02` | This category | Eleven rota positions drawn from the same pool, and the observation that two documents are asking for the same time |
| `AUDIT-017` `OP-11`, `OP-12`, §4 | [`../../project_content/_AUDIT/AUDIT-017`](../../project_content/_AUDIT/AUDIT-017_Category_17_OP_Content_Audit.md) | `06-06` does not exist; `RF-006` does not exist; the four unevidenceable assertions |
| `M66` §18 Q-02 | [`../../1000fix_ERP_Module/.../M66`](../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66_Internal_IT_Service_Management.md) | The unanswered staffing question §5 exists to make answerable |
| `PGD-000` §0.5, §2.1 | [`../PGD-000`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) | The **1,513 PW** build estimate and the **520–775 PW** content estimate — the two figures §5.7 compares against |

### 2.3 Audit findings this document closes or contributes to

| Finding | Source | How this document acts on it |
|---|---|---|
| **`OP-002-OI-01`** — delivery-team ring-fencing not accepted as a schedule cost in `06-01` | `OP-002` §4.12 | **Closed in specification.** §5.2 quantifies the ring-fence at **288 PW across nine waves**; §6.2 states what it displaces. Closes on a `GV-004` schedule change |
| **`OP-002-OI-04`** — floor-walker headcount unresourced; *"1 per 8–15 users implies 20–40 people at a full branch tranche"* | `OP-002` §4.12 | **Closed in specification.** §5.4 derives **~140 PW** of branch-staff time across the programme and identifies it as the pool nobody is counting |
| **`OP-002-OI-05`** — `HX-08` adoption may not be measurable | `OP-002` §4.12 | **Contributes.** §7.4 makes the expected-volume model a **transfer artefact with an owner**, rather than a measurement hoped for |
| **`OP-11`** — `06-06_Deployment_and_Operations_Plan.md` does not exist | `AUDIT-017` | **Contributes.** `HCT-02` records that Category 11 plus `RL-002`/`RL-003` now discharge what `06-06` would have owned, and recommends the register trace be amended rather than the document written |
| **`OP-12`** — 94 open decisions with no `RF-006` to record them in | `AUDIT-017` | **Contributes.** `SMF-24` routes this category's decisions to `GV-003`; `OP-002`'s five remain blocked |
| **`AUDIT-017` §4** — the programme cannot evidence its operational assertions | `AUDIT-017` | **Contributes.** §5.7 adds a fifth: **the programme cannot evidence that it has resourced its own stabilisation** |
| **`SMF-15`** / **`OCP-F-02`** | This category | **§10 states the three-way collision explicitly** rather than leaving each document to assume the others yielded |

### 2.4 The rule space

**`HCT`**, verified at **2026-08-19 02:15 (+06)** to return **zero occurrences in identifier form**
across all **777** markdown files. No rule in this category uses the form `SV-nn` (`SV-001` §2.4),
and every cross-document rule citation names its owning file (`SMF-26`).

---

## 3. What This Document Adds to `OP-002`

`HCT-01` forbids restating `OP-002`. The clearest way to honour that is to say precisely what is
new here and what is not.

| `OP-002` owns | `SV-005` adds |
|---|---|
| What hypercare **is** — posture, cadence, roles | **What it costs**, nine times, in three pools (§5) |
| Duration **per wave** | The **calendar**, the overlaps, and the 56-of-156-weeks fact (§4) |
| *"The delivery team is ring-fenced — a planning constraint, not a favour"* | **288 PW**, and what it displaces in `GV-004` (§5.2, §6.2) |
| Floor-walking **ratios** | **~140 PW of branch-staff time**, and the observation that it is in no estimate (§5.4) |
| *"What hypercare must produce for the next wave"* — six artefacts | **The transfer mechanism**: owner, format, acceptance test and deadline for each (§7) |
| Eighteen exit criteria | **What happens to the four unwaivable ones when the seventh hypercare is tired** (§11) |
| One hypercare | **Nine, and how they differ** (§9) |
| — | **The collision with the on-call rota and the next wave's build** (§10) |

---

## 4. The Recurrence

### 4.1 The fact `OP-002` states and does not add up

`OP-002` §4.3 gives a baseline duration per wave, derived from each wave's size and risk. Summed:

| Wave | Scope | `06-01` months | **Hypercare (`OP-002` §4.3)** |
|:--:|---|:--:|:--:|
| W1 | Core platform, Admin `P03` | 3–8 | **8 weeks** |
| W2 | Customer `P01`, Technician `P02` | 8–14 | 6 weeks |
| W3 | Logistics `P09`, Vendor `P05`, Payments | 14–18 | **8 weeks** |
| W4 | Corporate `P04`, Brand `P08`, Contact Centre `P10`, Analytics `P06` | 18–23 | 6 weeks |
| W5 | Quality `P11`, Finance depth, HR depth | 23–27 | **8 weeks** |
| W6 | Native apps, AI assistant, `M66` ITSM | 27–30 | 4 weeks |
| W7 | Marketplace `P07`, Partner `P12` | 30–33 | 6 weeks |
| W8 | Scale, optimisation | 33–36 | 4 weeks |
| W9 | Multi-entity | 33–36 | 6 weeks |
| | | | **Σ = 56 weeks** |

**A 36-month programme is ~156 weeks.**

> **`HCT-F-01`. Hypercare is an active posture for 56 of the programme's 156 weeks — 36% of the
> delivery period — and it is planned as a single event.** Two of the nine periods (W8 and W9) run
> concurrently because both waves end at month 36, giving roughly **52 weeks of hypercare calendar
> time**; the other seven are sequential and each begins inside the *build* window of the wave that
> follows it.

### 4.2 The calendar, and where each hypercare lands

Hypercare begins at cutover, which is the end of the wave's `06-01` month range.

| Hypercare for | Begins ≈ month | Ends ≈ month | Runs concurrently with |
|:--:|:--:|:--:|---|
| **W1** | 8 | 9.8 | **W2 build** (months 8–14) |
| W2 | 14 | 15.4 | **W3 build** (14–18) |
| **W3** | 18 | 19.8 | **W4 build** (18–23) |
| W4 | 23 | 24.4 | **W5 build** (23–27) |
| **W5** | 27 | 28.8 | **W6 build** (27–30) |
| W6 | 30 | 30.9 | **W7 build** (30–33) |
| W7 | 33 | 34.4 | **W8 and W9 build** (33–36) |
| W8 | 36 | 36.9 | **W9 hypercare** |
| W9 | 36 | 37.4 | **W8 hypercare, and beyond the programme's 36-month horizon** |

> **`HCT-F-02`. Every hypercare period begins inside the build window of the following wave, and the
> last two extend past the programme's stated end.** `OP-002` `HD-03` already notes that a tranched
> rollout runs the wave clock from the **last** tranche, which pushes each of these later still.
> **The 36-month plan does not contain the ninth hypercare.**

| # | Rule |
|---|---|
| **`HCT-03`** | **Every wave's plan in `GV-004` carries its hypercare as a named, resourced activity with a start date and an end condition** — not as a note in the go-live section |
| **`HCT-04`** | **A wave's build cannot be scheduled to consume the resources ring-fenced for the previous wave's hypercare.** This is a schedule constraint, and §6.2 states what it costs |
| **`HCT-05`** | **The ninth hypercare is inside the programme, or the programme ends before its last wave is stable.** `GV-004` extends to month 38 or W9 moves earlier. **Both are decisions; neither is the current plan** |

---

## 5. The Cost, Derived

### 5.1 Method and honesty

Three kinds of number, labelled as `PE-006` §3.1 and `SV-002` §5.1 label theirs:

| Label | Meaning |
|---|---|
| **Inherited** | Stated in `OP-002`, `OP-001` or `06-01` and used unchanged |
| **Derived** | Calculated here from an inherited figure, with the arithmetic shown |
| **Assumed** | A figure no upstream document states. **Every assumption is declared inline and requires ratification** |

> **Three declared weaknesses in this derivation, stated before the numbers rather than after them.**
>
> 1. **`OP-002` §4.3's durations are themselves unratified.** `OP-002`'s own Open Items record that
>    they are *"content-proposed and require Programme Manager ratification; they are not in
>    `06-01`"*. Every figure below inherits that.
> 2. **The ring-fenced engineer count is Assumed.** `OP-002` §4.1 says *"the delivery team"* without
>    a number. §5.2 assumes four at W1–W5 and three at W6–W9 and says so.
> 3. **Floor-walking volume depends on `RL-004`'s tranching**, which sequences 51+ branches. §5.4
>    derives a range rather than a point, and names the driver.
>
> **A derivation with declared weaknesses is more useful than an absent one**, which is the position
> today, and `RG-06` requires the enumeration to be shown rather than the conclusion asserted.

### 5.2 Pool 1 — Project effort (competes with the build estimate)

`OP-002` §4.1: *"Delivery team: **ring-fenced** for the hypercare period; this is a planning
constraint, not a favour."* Plus the coordination roles in §4.5 — Hypercare Manager, plus QA Lead
and Change Lead part-time.

**Assumed:** 4 ring-fenced engineers W1–W5 (the waves with money, statutory output or first-of-kind
risk), 3 at W6–W9. **Coordination: 1.5 FTE throughout** (Hypercare Manager 1.0, QA + Change 0.5).

| Wave | Ring-fenced | + coordination | FTE | × weeks | **PW** |
|:--:|:--:|:--:|:--:|:--:|--:|
| W1 | 4 | 1.5 | 5.5 | 8 | **44** |
| W2 | 4 | 1.5 | 5.5 | 6 | 33 |
| W3 | 4 | 1.5 | 5.5 | 8 | **44** |
| W4 | 4 | 1.5 | 5.5 | 6 | 33 |
| W5 | 4 | 1.5 | 5.5 | 8 | **44** |
| W6 | 3 | 1.5 | 4.5 | 4 | 18 |
| W7 | 3 | 1.5 | 4.5 | 6 | 27 |
| W8 | 3 | 1.5 | 4.5 | 4 | 18 |
| W9 | 3 | 1.5 | 4.5 | 6 | 27 |
| | | | | | **Σ 288 PW** |

**Owner: Programme / CTO. Competes directly with the 1,513 PW build estimate.**

### 5.3 Pool 2 — Support effort (competes with the establishment)

`OP-002` §4.1: T1 staffing at **2× baseline**. The baseline is `OP-001` §4.7: **2 FTE at W1, 4 at
W4, 6–8 at W8**. Interpolating linearly between the three stated points, and taking 7 for the
W8 range:

| Wave | T1 baseline *(interpolated)* | **Uplift = +baseline** | × weeks | **PW** |
|:--:|:--:|:--:|:--:|--:|
| W1 | 2.0 | +2.0 | 8 | 16.0 |
| W2 | 2.7 | +2.7 | 6 | 16.2 |
| W3 | 3.3 | +3.3 | 8 | 26.4 |
| W4 | 4.0 | +4.0 | 6 | 24.0 |
| W5 | 4.75 | +4.75 | 8 | 38.0 |
| W6 | 5.5 | +5.5 | 4 | 22.0 |
| W7 | 6.25 | +6.25 | 6 | 37.5 |
| W8 | 7.0 | +7.0 | 4 | 28.0 |
| W9 | 7.0 | +7.0 | 6 | 42.0 |
| | | | | **Σ 250 PW** |

**Owner: Head of IT Service Management / CFO. Competes with `SV-001` §8.4's establishment** — and
note that **the baseline itself is unfunded** (`OP-001-OI-03`), so this is a doubling of a number
that is currently zero.

### 5.4 Pool 3 — Business effort (in no estimate at all)

`OP-002` §4.4's ratios, applied to the estate. **`FW-02` requires floor-walkers to be drawn from the
champion network plus the project team, never solely the project team** — so most of this pool is
**branch and business staff**, not project staff.

| Activity | `OP-002` §4.4 ratio | Volume | **PW** |
|---|---|---|--:|
| Pilot branches — on-site, full hours, **10 working days**, 1 per 8–10 users | ~2 wk each | ≈ 3 pilot sites across the wave set, ~15 staff each → ~2 walkers × 2 wk | **≈ 12** |
| Subsequent branches — **5 working days**, 1 per 12–15 users | 1 wk each | **51+ branches**, ~10–15 staff each → ≈ 1 walker-week per branch | **≈ 51** |
| Central warehouse — 10 working days, 1 per shift | 2 wk × shifts | 1 site, 2–3 shifts | ≈ 6 |
| Workshops / depots — 5 working days | 1 wk each | ~8 sites | ≈ 8 |
| **Field technicians — ride-along, first 5 shifts per cohort, 1 per 6 technicians** | 1 wk per walker | **200–400 technicians** → 33–67 walkers | **≈ 33–67** |
| Contact centre — 10 working days, 1 per 10 agents | 2 wk | ~30 agents → 3 walkers | ≈ 6 |
| Head office — daily 60-min clinic per function, 10 working days | — | ~8 functions | ≈ 4 |
| | | | **Σ ≈ 120–160 PW** |

> **`HCT-F-03`. Roughly 140 person-weeks of this programme's stabilisation is paid in branch staff
> time, and it appears in no estimate the programme holds.** It is not in the 1,513 PW build figure
> (it is not build), not in the 520–775 PW content figure (it is not content), and not in any branch
> operating budget (nobody has asked). **`OP-002-OI-04` recorded the ratios as *"aspirational"*; this
> is what they weigh.**
>
> It is also the pool that gets cut first, because it is the only one whose absence is invisible on a
> project plan — and `OP-002` §4.4 opens by saying exactly that: floor-walking *"is the single
> highest-yield hypercare activity and the first one cut when resourcing is short."*

### 5.5 The total

| Pool | Effort | Owner | Competes with | Funded? |
|---|--:|---|---|:--:|
| **1 — Project** (ring-fence + coordination) | **288 PW** | Programme / CTO | The **1,513 PW** build estimate | ✗ |
| **2 — Support** (T1 uplift) | **250 PW** | Head of ITSM / CFO | `SV-001` §8.4's establishment, itself unfunded | ✗ |
| **3 — Business** (floor-walking, ride-alongs) | **≈ 140 PW** | Operations Director | **Nothing — it is in no estimate** | ✗ |
| **Total** | **≈ 678 PW** | | | **✗** |

**Sanity check.** 678 PW across 156 weeks ≈ **4.3 FTE sustained for three years** to stabilise nine
waves across 51+ branches, 500–1,000 staff, 200–400 field technicians and twelve portals. That is
not a large number for a rollout of this shape; it is a number nobody has written down.

### 5.6 What the three pools mean separately

> **`HCT-06`. The three pools are funded separately or the largest one is not funded at all.** A
> single "hypercare budget" line will be approved at the size of pool 1, because pool 1 is the only
> one whose owner attends the meeting.

| Pool | If it is not funded | Observable symptom |
|---|---|---|
| 1 — Project | Engineers are borrowed from the next wave | **Both waves slip.** `OP-002-OI-01` |
| 2 — Support | Every contact reaches T2 or T3 | The tier model collapses to direct-to-engineer support (`OP-001` §4.7) |
| 3 — Business | Floor-walking is cut | **Adoption fails silently.** Users work around the system on paper, `HX-08` is missed, and the wave exits anyway because `HX-08` is waivable |

### 5.7 Against the programme's own figures

| Figure | Value | Source |
|---|--:|---|
| Build estimate | **1,513 PW** | `PGD-000` §2.1, `AUDIT` H-02 |
| Content estimate | **520–775 PW** | `AUDIT-017` `AF-09`, `PGD-000` |
| **Hypercare, derived here** | **≈ 678 PW** | §5.5 |
| Hypercare as a share of build | **≈ 45%** | 678 ÷ 1,513 |

> **`HCT-F-04`. The programme's stabilisation effort is roughly 45% of its build effort and appears
> in neither of its two published estimates.** `AUDIT-017` §4 lists four things the programme
> asserts and cannot evidence. **This is a fifth: the programme cannot evidence that it has resourced
> its own stabilisation**, and unlike the other four, no infrastructure purchase closes it.

---

## 6. Resourcing

### 6.1 The ring-fence, specified

`OP-002` §4.1 states the principle. This states the mechanism.

| # | Rule |
|---|---|
| **`HCT-07`** | **Ring-fenced engineers are named individuals, allocated in `GV-004` by name, for dated periods.** *"The delivery team"* is not an allocation |
| **`HCT-08`** | **A ring-fenced engineer's next-wave commitments are reduced in the plan before the hypercare starts, not absorbed by overtime afterwards** |
| **`HCT-09`** | **Ring-fencing is released by the exit decision (`OP-002` §4.9), not by the calendar.** If hypercare extends, the ring-fence extends, and the next wave's plan moves — which is why `HD-04`'s 150% escalation exists |
| **`HCT-10`** | **The ring-fenced set includes at least one engineer who built the wave's highest-risk module.** Hypercare is where design assumptions meet real users, and the person who can answer *"was that intended?"* in ten seconds saves a day |

### 6.2 What the ring-fence displaces

288 PW removed from build capacity has to come from somewhere, and the three honest options are:

| Option | Consequence | Assessment |
|---|---|---|
| **Extend the schedule** | 288 PW ≈ 45 engineer-months. At a ~10-engineer build team, **≈ 4.5 months** across the programme | **The honest option.** It makes the cost visible in the plan |
| **Add capacity** | Recruit or contract for the ring-fenced role | Viable for pool 2; harder for pool 1, because §`HCT-10` requires people who built the thing |
| **Absorb it** | Engineers do both | **The current plan by default.** It is what produces the slipped wave every ERP programme reports |

> **`SV-005-D-01`. The programme schedules the ring-fence explicitly, accepting the schedule effect,
> rather than absorbing it.** The alternative is not cheaper; it is the same cost paid later, in a
> less visible currency, by people who are already tired.

### 6.3 Support uplift

| # | Rule |
|---|---|
| **`HCT-11`** | **T1 hypercare uplift is recruited or contracted ahead of the wave, and shadowed** for at least five working days before cutover. An agent hired on go-live day is a second problem |
| **`HCT-12`** | **Contact Centre agents (`P10`) may staff the uplift from W4**, subject to `OP-001-OI-05`'s unresolved question about whether they act as T1 for internal contacts. **Until that is answered, the uplift is a separate hire** |
| **`HCT-13`** | **Uplift staff are retained into the following wave where the baseline is rising anyway.** `OP-001` §4.7's baseline grows from 2 to 6–8 across the programme; treating each wave's uplift as disposable re-hires the same role nine times |

> **`HCT-13` is where the largest saving in this document sits.** Pool 2 is 250 PW of *doubling*.
> Because the baseline itself rises from 2 to 7 FTE, a substantial share of each wave's uplift is
> next wave's baseline arriving early. **Treated as a hiring ramp rather than nine surges, pool 2
> falls materially** — the exact figure depends on `GV-007`'s recruitment plan and is `HCT-Q-03`.

### 6.4 The seam with `CH-005`

Pool 3 is branch staff time, and the instrument that releases branch staff from their day jobs is
[`CH-005`](../13_Training_Change_and_Adoption/CH-005_Super_User_and_Champion_Network_Charter.md), the Super-User and Champion Network Charter — which `PGD-000` describes as *"the charter
that releases these people from their day jobs — the actual constraint"*.

| # | Rule |
|---|---|
| **`HCT-14`** | **Floor-walking time is drawn against `CH-005`'s charter allocation and is counted there, not invented per wave.** If the charter allocates a champion two days a month and hypercare needs ten in a fortnight, that is a charter problem, not a hypercare problem |
| **`HCT-15`** | **A branch whose champion has not been released does not enter the wave.** This is added to `OP-002`'s `HE-10` (branch readiness) as a precondition, not discovered on the first morning |
| **`HCT-16`** | **`FW-02` holds: floor-walkers are never drawn solely from the project team.** The champion is who remains after exit, and a wave floor-walked entirely by the project team has transferred nothing |

---

## 7. The Transfer Mechanism

**`PGD-000` names this as the gap: *"the resourcing and transfer mechanism is undefined."*** §5 is
the resourcing. This is the mechanism.

### 7.1 The principle

> **`HCT-17`. Knowledge transfer is a deliverable with an owner, a format, an acceptance test and a
> deadline — not an outcome of people working alongside each other.** Proximity produces familiarity;
> only an artefact with an acceptance test produces transfer.

`OP-002` §4.11 lists six things hypercare must produce for the next wave. It does not say who
produces them, in what form, or how anyone knows they are adequate. That is what follows.

### 7.2 The transfer artefact set

| # | Artefact | Owner | Format | **Acceptance test** | Due |
|---:|---|---|---|---|:--:|
| **1** | **Top 10 observed error patterns**, in user language | Hypercare Manager | One page per pattern: symptom, cause, resolution, prevention | **A T1 analyst who did not work the wave resolves a sample contact using only the pattern sheet** | Exit − 1 wk |
| **2** | **Runbook deltas** | Service owner (`SV-001` §5.3) | Merged into `SV-003`'s runbooks, with **§12 ledger rows** | **Every procedure executed during hypercare has a ledger row** (`RBS-11`) | **At exit**, `HX-14` |
| **3** | **Support volume actuals per population** | Hypercare Manager | Contacts per population per week, against the modelled expectation | **The next wave's `OP-001` §4.7 staffing is set from it, and the variance from the model is stated** | Exit + 1 wk |
| **4** | **Known-issue log, live** | QA Lead | The `OP-002` §4.6 log, **handed over rather than closed** (`KI-04`) | **Every entry has a workaround and a named BAU owner** (`HX-13`) | At exit |
| **5** | **The expected-volume model** for `HX-08` adoption | BI Lead | Expected transaction volume per population per week | **`HX-08` was actually measured this wave** — if it was not, the model is the first deliverable of the next | **Before entry**, not exit |
| 6 | Cutover lessons | Data Migration Lead | Into `MG-006`, `RL-002` | Next wave's cutover plan cites them | Exit + 2 wk |
| 7 | Every PIR | Review facilitator | `OP-016` register | `HX-17`: 100% complete for `Sev1`/`Sev2` | At exit |
| 8 | Adoption barriers | Change Lead | Into `CM-011`, `CH-004` | Next wave's resistance pack cites them | Exit + 2 wk |

> **Artefact 5 is out of sequence deliberately.** `OP-002-OI-05` records that `HX-08` — *"adoption of
> the wave's primary transactions ≥ 90% of expected volume"* — may not be measurable, because it
> requires a modelled expected volume per population that does not exist. **`HX-08` is the most
> important exit criterion in the set** and it is the one at risk of being unmeasurable. Producing
> the model is therefore an **entry** obligation, not an exit one.

| # | Rule |
|---|---|
| **`HCT-18`** | **`HX-08`'s expected-volume model is an entry condition, added to `OP-002`'s `HE-01`…`HE-10` set as `HE-11`.** A wave that goes live without it cannot measure the criterion that says whether people are using the system |
| **`HCT-19`** | **An artefact that fails its acceptance test does not block exit; it blocks the *release of the ring-fence*.** The distinction matters: holding a wave open punishes the business for a project failure, while holding the engineers punishes the party that owed the artefact |

### 7.3 Transfer from project to operations — the two-way test

> **`HCT-20`. Transfer is proved by the receiver, not asserted by the giver.**

| Test | Who performs it | Passes when |
|---|---|---|
| **The runbook test** | A BAU engineer who did not build the wave | They execute the wave's `P0` recovery procedure in `staging`, unaided, from the runbook alone (`SV-003` §6.3) |
| **The contact test** | A T1 analyst who did not work the wave | They resolve five sampled hypercare contacts from the macro and known-error library alone |
| **The escalation test** | The on-call primary | They page, escalate and command a `Sev2` on the new wave's services without asking a project engineer (`SV-004` §11's game day) |
| **The champion test** | A branch champion | They answer the five most common hypercare questions for their branch without calling the project team |

**All four are run in the final week of hypercare, and their results are attached to the `OP-002`
§4.9 exit form.** They do not replace `HX-01`…`HX-18`; they evidence `HX-14`, `HX-15` and `HX-18`.

### 7.4 What must not be transferred

| # | Rule |
|---|---|
| **`HCT-21`** | **An open `S1` defect is not transferred; it is fixed.** `HX-01` is unwaivable for this reason |
| **`HCT-22`** | **An undocumented workaround is not transferred; it is written down or it is withdrawn.** A workaround that lives in one person's head is a single point of failure with a friendly name (`OP-016`'s `single-person` tag) |
| **`HCT-23`** | **A relationship is not transferable.** T1 keeps the requester relationship through escalation (`OP-001` `TR-05`), and at exit the branch is told **who** they now call, by name, not which queue |

---

## 8. Transition to Business as Usual

`OP-002` §4.10 defines what changes at exit, across seven dimensions, and `TX-01` requires the exit
to be announced. Both are adopted whole (`HCT-01`). Three additions:

| # | Rule |
|---|---|
| **`HCT-24`** | **The BAU support model must be *operating*, not *specified*, before exit.** `SV-001` §4.3's four words apply: `HX-15` reads *"BAU support model staffed and briefed"*, and **staffed means people who have worked a shift**, not a published roster |
| **`HCT-25`** | **The on-call rota covers the exit week with a member who worked the hypercare.** The first out-of-hours incident after hypercare exit is the one with the least context available |
| **`HCT-26`** | **Exit is announced to every affected population in both languages, stating what changes about getting help** (`TX-01`), **and the previous route continues to work for two further weeks**, redirecting rather than failing. A route that stops working on the announced day teaches people that announcements are threats |

### 8.1 The exit decision, and who may not make it

`OP-002` §4.9's exit form carries six signatures and the Programme Manager's decision. One addition:

> **`HCT-27`. The exit decision may not be made by anyone whose next commitment depends on it.** A
> Programme Manager whose Wave 4 start date depends on Wave 3's hypercare ending is not a neutral
> assessor of whether it has. **Where that conflict exists, the CTO co-signs**, and `OP-002`'s
> waiver rule — `HX-01`, `HX-09`, `HX-12` and `HX-17` are **not waivable** — is what protects the
> other fourteen from it.

---

## 9. Nine Hypercares, Not One

`OP-002` §4.3 sets a duration per wave from size and risk. **What changes beyond duration** is not
stated anywhere, and it is what makes each one a different exercise.

| Wave | The thing that makes this hypercare different | Consequence |
|:--:|---|---|
| **W1** | **Nothing about the operating model has been proven.** The support model, the rota, the runbooks and the paging platform are all being used for the first time | **Longest at 8 weeks, and the only one where hypercare is also testing hypercare.** Its transfer artefacts set the template for the other eight |
| W2 | **200–400 field technicians in real network conditions**, which cannot be simulated | Ride-alongs dominate pool 3; `SLI-SYNC` and 24-hour offline behaviour are the exit risk |
| **W3** | **Money moves.** A full settlement and reconciliation cycle must complete inside the window | `HX-09` (reconciliation variance) becomes the binding criterion; **CFO signature is not a formality** |
| W4 | **Four external populations at once**, including contractual clients | Communication load, not technical load. `OP-004`'s corporate notification templates get their first real use |
| **W5** | **One full payroll run and one statutory filing** must complete inside it | `HD-02` binds hardest here; a missed filing is not a defect, it is a penalty |
| W6 | **`M66` go-live migrates the support model itself** — and, if `SV-001-D-04` is approved, `CD-163` landed at W1 and this is only the asset half | **The one hypercare where the support function is the thing changing.** §9.1 |
| W7 | New external populations **with money flowing outward** (seller payouts) | Payout reconciliation; a new counterparty class |
| W8 | Mostly non-functional | Shortest; the risk is that it is treated as trivial and the ring-fence is not applied |
| **W9** | **Multi-entity and cross-border introduce statutory surfaces** (`NFR-086`, `NFR-099`) | **And it falls outside the 36-month plan** (`HCT-F-02`) |

### 9.1 The W6 special case

At W6 the support platform itself changes. Under either branch of `SV-001-D-04`:

| If | W6 hypercare must additionally |
|---|---|
| `CD-163` moved to W1 (`SV-001-D-04` approved) | Migrate **asset, CMDB and SAM** into `M66`, and complete the IT asset physical audit across 51+ branches (`M66` §16.4, Q-01) |
| `M66` stayed whole at W6 | Migrate **the entire support function** — queues, SLA policies, known errors, macros and history — from the interim `helpdesk` configuration, **while running a hypercare on eight other modules** |

> **`HCT-F-05`. Under the second branch, W6's hypercare is scheduled at four weeks — the joint
> shortest — and is the only one that also migrates the support function itself.** That is the
> shortest window allocated to the most reflexive change in the programme. **It is a further argument
> for `SV-001-D-04`**, and it is recorded here because `OP-002` §4.3's duration was set from module
> count rather than from this.

---

## 10. The Collision

Three documents now ask the same engineers for the same time, and each was written assuming the
others would yield.

| Claim | Document | Ask |
|---|---|---|
| **Ring-fenced for hypercare** | `OP-002` §4.1, **this document §5.2** | **288 PW** across nine periods, each 4–8 weeks |
| **On the on-call rota** | `OP-013` §4.3, **`SV-004` §6.6** | **7 platform + 4 security** positions, one week in three, 24×7 |
| **Building the next wave** | `06-01`, `GV-004` | The whole of the **1,513 PW** estimate |

`SV-001` `SMF-15` records the first half of this — *"the rota headcounts and the T3 line are the
same people"* — and `SV-004` `OCP-F-02` records the second — *"two documents are asking eleven people
for the same time and neither is funded"*. **This is the third edge of the same triangle.**

### 10.1 The worked collision

Take a platform engineer during W1 hypercare (months 8–9.8), which overlaps W2's build:

| Simultaneously | Demand |
|---|---|
| Ring-fenced for W1 hypercare | Full-time, on-site, twice-daily triage |
| On the on-call rota | One week in three, 24×7, `Sev1` acknowledgement in 5 minutes |
| Committed to W2 build | Per `GV-004` |
| After a `Sev1` past 01:00 | **Does not start before 12:00** (`OP-013` `RT-05`, `OCP-36`) |

> **`HCT-F-06`. The same engineer is simultaneously ring-fenced, on call and committed to the next
> wave, and one of the three protections — `RT-05`'s late start — mechanically removes capacity from
> whichever of the other two is scheduled that morning.** No document is wrong. **The plan is
> over-subscribed and nobody has added it up**, which is the same defect as `HCT-F-04` at the level
> of an individual rather than the programme.

### 10.2 The resolution rules

| # | Rule |
|---|---|
| **`HCT-28`** | **A ring-fenced engineer is removed from the on-call rota for the hypercare period.** The rota's pool of seven (`SV-004` §6.3) is sized on the assumption that all seven are available; **removing one for eight weeks puts it at six and back into `RT-04` breach.** Either the pool is eight, or hypercare draws its ring-fence from outside the rota |
| **`HCT-29`** | **Where an engineer must hold both, the on-call week takes precedence over hypercare presence, and hypercare coverage is backfilled** — because the rota has a five-minute acknowledgement obligation and hypercare does not |
| **`HCT-30`** | **`GV-004` shows the same person once.** A named individual appearing in two concurrent allocations is a planning error, and it is currently invisible because the three allocations live in three documents |

> **`SV-005-D-02`. The platform rota pool is sized at **eight**, not seven, if ring-fenced engineers
> are drawn from it.** `SV-004` `SV-004-D-03` derived seven from leave alone. Hypercare removes one
> more for 4–8 weeks at a time, nine times. **This is presented as a consequence for the Steering
> Committee to price, not a unilateral change to `SV-004`'s number** — the two documents are
> consistent, and the difference is exactly the hypercare ring-fence.

---

## 11. Hypercare Fatigue

### 11.1 The failure mode of the seventh one

The first hypercare is well-attended, well-resourced and closely watched. **The seventh is not.**
By month 33 the same people have done this six times, the exit criteria are familiar, the programme
is behind, and the exit review is a meeting somebody wants to keep short.

`OP-002` §1 already anticipates the moment: *"Every wave in this programme will reach a point where
the hypercare team is tired, the next wave is late, and somebody proposes that hypercare 'wind
down'. This file exists so that proposal has to be answered with numbers."*

**`OP-002` is right, and numbers alone do not survive fatigue.** What survives is that four criteria
cannot be waived at all.

### 11.2 The four that hold

`OP-002` §4.8's waiver rule: **`HX-01` (zero open `S1` defects), `HX-09` (reconciliation variance),
`HX-12` (every business cycle completed) and `HX-17` (all PIRs complete) are not waivable.** Any
other may be waived **once**, jointly, with the reason and a compensating control recorded.

| # | Rule |
|---|---|
| **`HCT-31`** | **Waiver counts are reported cumulatively across all nine waves in the monthly service report** (`SMF-25`). One waiver is a judgement; the same criterion waived at four consecutive waves is a criterion the programme has decided not to meet, and it should say so |
| **`HCT-32`** | **A criterion waived at three or more waves is escalated to the Steering Committee for a decision to change it or fund it** — not waived a fourth time |
| **`HCT-33`** | **The exit review for W6 onward is chaired by someone who did not chair the previous one.** Rotation is the cheapest available defence against a review that has become a formality |
| **`HCT-34`** | **`HD-04` holds throughout: an extension beyond 150% of baseline goes to the Steering Committee with a root-cause statement** — *"it means something failed before go-live, not during it"* |

### 11.3 The signal to watch

> **`HCT-35`. The leading indicator of hypercare fatigue is the *waiver rate*, not the *incident
> rate*.** Incidents fall as the platform matures, which looks like success. Waivers rise as
> attention moves on, and they are the measure that tells the Steering Committee whether wave seven
> was stabilised or merely survived.

---

## 12. Governing Rules — Consolidated

| # | Rule | § |
|---|---|:--:|
| **`HCT-01`** | `OP-002` §4.1–§4.12 — entry conditions, durations, ratios, cadence, roles, rollback, **the eighteen exit criteria** and the exit form — are **adopted whole by citation and never restated** | 1.1 |
| **`HCT-02`** | Category 11 plus `RL-002`/`RL-003` discharge what `06-06` would have owned; the register trace is amended rather than the document written | 2.3 |
| **`HCT-03`** | Every wave's `GV-004` plan carries its hypercare as a **named, resourced activity** | 4.2 |
| **`HCT-04`** | A wave's build may not consume the resources ring-fenced for the previous wave's hypercare | 4.2 |
| **`HCT-05`** | **The ninth hypercare is inside the programme, or the programme ends before its last wave is stable** | 4.2 |
| **`HCT-06`** | **The three cost pools are funded separately**, or the largest is not funded at all | 5.6 |
| **`HCT-07`** | Ring-fenced engineers are **named individuals in `GV-004`**, for dated periods | 6.1 |
| **`HCT-08`** | Next-wave commitments are reduced in the plan **before** hypercare starts | 6.1 |
| **`HCT-09`** | The ring-fence is released by the **exit decision**, not the calendar | 6.1 |
| **`HCT-10`** | The ring-fence includes an engineer who **built the wave's highest-risk module** | 6.1 |
| **`HCT-11`** | T1 uplift is recruited ahead and **shadowed five days** before cutover | 6.3 |
| **`HCT-12`** | Contact Centre staffing of the uplift awaits `OP-001-OI-05` | 6.3 |
| **`HCT-13`** | **Uplift staff are retained where the baseline is rising** — a hiring ramp, not nine surges | 6.3 |
| **`HCT-14`** | Floor-walking time is drawn against **`CH-005`'s charter allocation** and counted there | 6.4 |
| **`HCT-15`** | **A branch whose champion has not been released does not enter the wave** | 6.4 |
| **`HCT-16`** | Floor-walkers are **never drawn solely from the project team** (`FW-02`) | 6.4 |
| **`HCT-17`** | **Knowledge transfer is a deliverable with an owner, a format, an acceptance test and a deadline** | 7.1 |
| **`HCT-18`** | **`HX-08`'s expected-volume model is an entry condition (`HE-11`)**, not an exit one | 7.2 |
| **`HCT-19`** | A failed transfer artefact blocks **the release of the ring-fence**, not the exit | 7.2 |
| **`HCT-20`** | **Transfer is proved by the receiver**, through four named tests | 7.3 |
| **`HCT-21`** | An open `S1` is **fixed, not transferred** | 7.4 |
| **`HCT-22`** | An undocumented workaround is written down or withdrawn | 7.4 |
| **`HCT-23`** | **A relationship is not transferable** — the branch is told who they now call, by name | 7.4 |
| **`HCT-24`** | The BAU model must be **operating, not specified**, before exit | 8 |
| **`HCT-25`** | The rota covers the exit week with **someone who worked the hypercare** | 8 |
| **`HCT-26`** | Exit is announced in both languages, and **the old route redirects for two further weeks** | 8 |
| **`HCT-27`** | **The exit decision is not made by anyone whose next commitment depends on it** | 8.1 |
| **`HCT-28`** | **A ring-fenced engineer is removed from the on-call rota** — which puts a pool of seven back into `RT-04` breach | 10.2 |
| **`HCT-29`** | Where both are held, **the on-call week takes precedence** and hypercare is backfilled | 10.2 |
| **`HCT-30`** | **`GV-004` shows the same person once** | 10.2 |
| **`HCT-31`** | **Waiver counts are reported cumulatively across all nine waves** | 11.2 |
| **`HCT-32`** | A criterion waived at three or more waves is **escalated, not waived again** | 11.2 |
| **`HCT-33`** | From W6, the exit review is **chaired by someone who did not chair the last one** | 11.2 |
| **`HCT-34`** | `HD-04`'s 150% escalation holds throughout | 11.2 |
| **`HCT-35`** | **The leading indicator of fatigue is the waiver rate, not the incident rate** | 11.3 |

**Findings raised by this document**

| # | Finding | Severity | Owner |
|---|---|:--:|---|
| **`HCT-F-01`** | **Hypercare is an active posture for 56 of 156 weeks — 36% of the delivery period — and is planned as a single event** | **HIGH** | Programme Manager |
| **`HCT-F-02`** | **Every hypercare begins inside the next wave's build window, and the last two extend past the programme's 36-month end.** The plan does not contain the ninth hypercare | **HIGH** | Programme Manager |
| **`HCT-F-03`** | **≈ 140 PW of stabilisation is paid in branch-staff time and appears in no estimate** — not build, not content, not any branch budget. It is also the pool that is cut first, and `OP-002` §4.4 says so | **HIGH** | Operations Director + CFO |
| **`HCT-F-04`** | **Total hypercare effort ≈ 678 PW, roughly 45% of the 1,513 PW build estimate, in neither published estimate.** A fifth item for `AUDIT-017` §4's unevidenceable list: **the programme cannot evidence that it has resourced its own stabilisation** | **HIGH** | CFO + Programme Manager |
| **`HCT-F-05`** | **W6 is allocated the joint-shortest hypercare (4 weeks) and is the only one that migrates the support function itself** — under the branch where `M66` stays whole. A further argument for `SV-001-D-04` | MEDIUM | CTO |
| **`HCT-F-06`** | **The same engineer is simultaneously ring-fenced, on call and committed to the next wave**, and `RT-05`'s late-start protection mechanically removes capacity from whichever is scheduled that morning. Three documents, three allocations, one person, no reconciliation | **HIGH** | Programme Manager + CTO |

---

## 13. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| **`SV-005-D-01`** | How the ring-fence is absorbed | (a) Extend the schedule; (b) add capacity; (c) **absorb it** — the current default | **(a)**, with (b) for pool 2 | (c) is not cheaper; it is the same cost paid later by tired people, and it is what produces the slipped wave every ERP programme reports. 288 PW ≈ **4.5 months** of schedule at a ~10-engineer team | `GV-004` extends; the effect is visible in the plan rather than in wave slippage |
| **`SV-005-D-02`** | Rota pool size given hypercare | (a) Seven, per `SV-004-D-03`; (b) **eight, if ring-fenced engineers come from the rota**; (c) draw the ring-fence from outside the rota | **(b) or (c) — presented for Steering decision** | `SV-004`'s seven is derived from leave alone. Hypercare removes one more for 4–8 weeks, nine times, putting the pool back into `RT-04` breach | Priced by the Steering Committee. **The two documents are consistent; the difference is exactly the ring-fence** |
| **`SV-005-D-03`** | `HX-08`'s expected-volume model | (a) Produce it at exit as `OP-002` §4.11 implies; (b) **make it an entry condition `HE-11`** | **(b)** | A model produced at exit cannot measure the criterion during the period. `OP-002-OI-05` records the risk that **the most important exit criterion is unmeasurable** | `OP-002`'s entry set gains an eleventh condition; BI Lead owns it before cutover |
| **`SV-005-D-04`** | Support uplift staffing | (a) Nine discrete surges; (b) **a hiring ramp, retaining uplift where the baseline rises** | **(b)** | `OP-001` §4.7's baseline rises 2 → 7 FTE across the programme; a share of each uplift is simply the next baseline arriving early. **Nine surges re-hire the same role nine times** | Pool 2 falls materially; the figure depends on `GV-007`'s recruitment plan (`HCT-Q-03`) |
| **`SV-005-D-05`** | Where `06-06` lands | (a) Write `06-06`; (b) **record that Category 11 with `RL-002`/`RL-003` is the operational plan of record** | **(b)** | `06-06` has been absent through three categories' authoring (`AUDIT-011`, `AUDIT-017` `OP-11`). What it would have owned is now written elsewhere and better | The register's `OP-002` trace is amended; `OP-002-OI-02` closes |

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|:--:|---|
| **`HCT-Q-01`** | **Is the ≈ 678 PW accepted, and against which budget lines?** | CFO + Programme Manager | **Before W1 cutover** | `HCT-F-04`; every pool in §5 |
| **`HCT-Q-02`** | **Is the delivery-team ring-fence accepted as a schedule cost in `GV-004`/`06-01`** (`OP-002-OI-01`, open since 2026-08-20)? | Programme Manager + CTO | **Before W1 cutover** | `SV-005-D-01`; `HCT-F-06` |
| `HCT-Q-03` | What does `GV-007`'s recruitment plan say about the T1 ramp, and how much of pool 2 does `SV-005-D-04` remove? | Head of ITSM + HR | W1 | Pool 2's true size |
| `HCT-Q-04` | **Does `CH-005` allocate enough champion time to cover ≈ 140 PW of floor-walking**, and is branch management aware? | Change Lead + Operations Director | **W1** | `HCT-F-03`; `HCT-14`, `HCT-15` |
| `HCT-Q-05` | Is the rota pool eight, or is the ring-fence drawn from outside it (`SV-005-D-02`)? | Steering Committee | W1 | `RT-04` compliance during every hypercare |
| `HCT-Q-06` | **Does `GV-004` extend to month 38 to contain W9's hypercare, or does W9 move earlier?** | Programme Manager | W7 | `HCT-F-02`, `HCT-05` |
| `HCT-Q-07` | Can `HX-08` be measured at W1 — does the BI Lead have an expected-volume model (`OP-002-OI-05`)? | BI Lead | **Before W1 cutover** | `HCT-18`; the wave's most important exit criterion |
| `HCT-Q-08` | Do Contact Centre agents act as T1 for internal contacts (`OP-001-OI-05`), and may they staff the uplift from W4? | Contact Centre Supervisor + Support Lead | W2 | `HCT-12`; pool 2's sourcing |
| `HCT-Q-09` | Is `OP-002` §4.3's duration table ratified by the Programme Manager? **Every figure in §5 inherits its unratified status** | Programme Manager | **W1** | The whole of §5 |

---

## 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Nothing from `OP-002` §4.1–§4.12 is restated | `HCT-01`; §3's table states what is added instead |
| `AC-02` | The recurrence is quantified from `OP-002`'s own durations | §4.1 — 56 weeks summed and shown |
| `AC-03` | The hypercare calendar is placed against `06-01`'s wave months, with overlaps identified | §4.2 — nine rows |
| `AC-04` | The cost is **derived with the arithmetic shown**, and every assumption is declared | §5.1's three declared weaknesses; §5.2, §5.3, §5.4 |
| `AC-05` | The cost is split by **who pays**, not only by how much | §5.5 — three pools, three owners |
| `AC-06` | The derivation is compared against the programme's published estimates | §5.7 — 678 PW against 1,513 PW and 520–775 PW |
| `AC-07` | The transfer mechanism names an owner, format, acceptance test and deadline per artefact | §7.2 — eight artefacts |
| `AC-08` | Transfer is proved by the receiver | §7.3 — four tests, attached to the `OP-002` §4.9 exit form |
| `AC-09` | The nine hypercares are differentiated by more than duration | §9 — nine rows plus the W6 special case |
| `AC-10` | The collision with the rota and the build is stated, not left to be discovered | §10; `HCT-F-06`; `SV-005-D-02` |
| `AC-11` | The failure mode of the later waves is addressed by a mechanism, not an exhortation | §11 — waiver counts, chair rotation, the waiver-rate indicator |
| `AC-12` | Every relative link resolves; no rule uses the form `SV-nn` | Verified at issue |

**Definition of done.** Complete when every criterion is met, `PGD-000` is updated with a fresh
enumeration timestamp, and the approver has signed **jointly with the CTO and the CFO**.
**`AC-04`'s figures remain `Derived` on an unratified base** (`HCT-Q-09`) and **`AC-06`'s conclusion
requires a funding decision this document cannot make** (`HCT-Q-01`).

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | [`OP-002`](../../project_content/17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md) | **The practice this document resources.** Adopted whole |
| Upstream | `SV-001` §8.4, `SMF-15` | The establishment and the shared-pool rule |
| Upstream | `SV-004` §6.3, §6.6 | The rota this hypercare competes with; `SV-005-D-02`'s consequence |
| Upstream | `06-01`, [`GV-004`](../00_Programme_Governance_and_Control/GV-004_Integrated_Programme_Plan_and_Master_Schedule.md) | The wave calendar §4.2 builds on and the plan §5 must enter |
| Upstream | [`GV-007`](../00_Programme_Governance_and_Control/GV-007_Estimation_Model_and_Resource_Plan.md), [`GV-008`](../00_Programme_Governance_and_Control/GV-008_Programme_Budget_and_Cost_Baseline.md) | Where the three pools belong |
| Upstream | [`RL-002`](../12_Release_Deployment_and_Transition/RL-002_Deployment_Plan_and_Go_Live_Checklist.md), [`RL-003`](../12_Release_Deployment_and_Transition/RL-003_Go_Live_Readiness_Assessment_and_Gate_Criteria.md), [`RL-004`](../12_Release_Deployment_and_Transition/RL-004_Rollout_and_Branch_Wave_Deployment_Plan.md) | Deployment, readiness, and the branch tranching that drives pool 3 |
| Upstream | [`CH-005`](../13_Training_Change_and_Adoption/CH-005_Super_User_and_Champion_Network_Charter.md) | **The instrument that releases pool 3's people** — §6.4 |
| Downstream | `SV-001` | Hypercare hands over to this operating model (`HX-15`, `HCT-24`) |
| Downstream | `SV-003` | Runbook deltas and ledger rows are transfer artefact 2 |
| Downstream | `SV-006` | Every `Sev1`/`Sev2` PIR is transfer artefact 7 (`HX-17`, unwaivable) |
| Downstream | [`RL-005`](../12_Release_Deployment_and_Transition/RL-005_Post_Implementation_Review_Standard.md) | The wave PIR consumes §5's actuals against estimate |
| Downstream | [`CH-004`](../13_Training_Change_and_Adoption/CH-004_Adoption_Measurement_and_Reinforcement_Plan.md) | `HX-08`'s expected-volume model and the adoption barriers |
| Lateral | [`MG-006`](../09_Data_Migration_and_Cutover/MG-006_Cutover_Plan_and_Runbook.md), `DM-014` | Cutover completes; hypercare begins |
| Lateral | [`QA-010`](../08_Quality_Engineering_and_Test/QA-010_Defect_Management_and_Quality_Gate_Standard.md), `TS-018` | `HX-01`…`HX-03`'s defect scale |

---

## 17. References

**Within this repository**
[`PGD-000`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
`SV-001`, `SV-002`, `SV-003`, `SV-004`, `SV-006` ·
[`GV-004`](../00_Programme_Governance_and_Control/GV-004_Integrated_Programme_Plan_and_Master_Schedule.md) ·
[`GV-007`](../00_Programme_Governance_and_Control/GV-007_Estimation_Model_and_Resource_Plan.md) ·
[`GV-008`](../00_Programme_Governance_and_Control/GV-008_Programme_Budget_and_Cost_Baseline.md) ·
[`RL-002`](../12_Release_Deployment_and_Transition/RL-002_Deployment_Plan_and_Go_Live_Checklist.md) ·
[`RL-003`](../12_Release_Deployment_and_Transition/RL-003_Go_Live_Readiness_Assessment_and_Gate_Criteria.md) ·
[`RL-004`](../12_Release_Deployment_and_Transition/RL-004_Rollout_and_Branch_Wave_Deployment_Plan.md) ·
[`RL-005`](../12_Release_Deployment_and_Transition/RL-005_Post_Implementation_Review_Standard.md) ·
[`CH-001`](../13_Training_Change_and_Adoption/CH-001_Organisational_Change_Management_Plan.md) ·
[`CH-004`](../13_Training_Change_and_Adoption/CH-004_Adoption_Measurement_and_Reinforcement_Plan.md) ·
[`CH-005`](../13_Training_Change_and_Adoption/CH-005_Super_User_and_Champion_Network_Charter.md) ·
[`MG-006`](../09_Data_Migration_and_Cutover/MG-006_Cutover_Plan_and_Runbook.md) ·
[`QA-010`](../08_Quality_Engineering_and_Test/QA-010_Defect_Management_and_Quality_Gate_Standard.md)

**Workspace**
[`OP-002`](../../project_content/17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md) ·
[`OP-001`](../../project_content/17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) ·
[`OP-013`](../../project_content/17_Operations_Support_and_Runbooks/OP-013_On_Call_Escalation_and_Handover_Content.md) ·
[`OP-016`](../../project_content/17_Operations_Support_and_Runbooks/OP-016_Post_Incident_Review_Template_and_Register.md) ·
[`06-01`](../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md) ·
[`06-02`](../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md) ·
[`M66`](../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66_Internal_IT_Service_Management.md) ·
[`AUDIT-017`](../../project_content/_AUDIT/AUDIT-017_Category_17_OP_Content_Audit.md)

**External standards and sources** *(each verified 2026-08-19)*

| Source | Verified |
|---|:--:|
| ISO/IEC 20000-1:2018 §8.5.2, §7.1, §7.6 | 2026-08-19 |
| ISO/IEC 20000-1:2018/Amd 1:2024 · https://www.iso.org/standard/88434.html | 2026-08-19 |
| ISO 21502:2020 — project, programme and portfolio management guidance, §7.6 resource management | 2026-08-19 |
| ERP hypercare practice — 2–8 weeks typical, extending to ~12 for complex phased rollouts; elevated staffing; measured exit criteria *(as cited by `OP-002`, sources verified there 2026-08-20)* | 2026-08-19 |

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Head of IT Service Management, with the Programme Manager | Initial issue. Rule space `HCT` allocated after verification against 777 files. **Hypercare recurrence quantified at 56 of 156 weeks; effort derived at ≈ 678 PW across three cost pools, ≈ 45% of the build estimate, in neither published estimate.** Transfer mechanism specified as eight artefacts with acceptance tests. Five decisions, six findings, nine open questions — of which two must be answered before W1 cutover | Programme Manager, **jointly with the CTO and the CFO** *(all pending)* |
| **1.1** | **2026-08-19** | Head of IT Service Management | **Conformance to `RR-002` `IDC-08`** (timestamp and denominator in `rule_prefix:`). Cross-references into `SV-006` corrected after that document's structure was fixed — the `AUDIT-017` `OP-23` defect class, caught by this category's own audit rather than by a later one. | As above |

---

*`SV-005` · Category 11 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
