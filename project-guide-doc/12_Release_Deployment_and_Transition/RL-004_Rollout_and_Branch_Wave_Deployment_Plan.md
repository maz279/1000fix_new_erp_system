---
id: RL-004
title: Rollout and Branch Wave Deployment Plan
category: 12 — Release, Deployment & Transition
code: RL
project: 1000FiX ERP System v2.0
version: 1.1
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Branch Operations Lead with the Change Lead
approver: Operations Director with the Programme Director
standards_basis: >
  ITIL 4 Deployment Management — phased deployment and pilot patterns · ISO 21502:2020 §7.7
  (managing delivery across dispersed locations) · PRINCE2 7th Edition (2023) stage and tranche
  planning · Theory of constraints applied to a capacity-bounded rollout — the binding resource is
  named and the plan is sized to it
traces_to: >
  PGD-000 RL-004 row (◐ 06-01 §6) · 06-01 §6 geographic sequence and rollout pattern · RFP §12.6 ·
  CM-012 RB-01…RB-12 (eight readiness domains) · MG-006 CUT-18…CUT-23 (zone layer) ·
  OP-002 §4.4 floor-walking ratios, HD-03 · DM-014 §4.9 (51-branch coordination) ·
  05-04 §5 role headcounts · MD-003 (branch master, class P3) · MD-006 (eight divisions) ·
  CH-002 §4 learner-hour model · RL-003 GLR-11
depends_on: >
  RL-001, RL-002, RL-003 (issued) · MG-006 (issued) · CH-002 (issued) · PE-002, PE-004 (issued) ·
  MD-003 Branch and Service Centre Master (content, NOT POPULATED — class P3) ·
  SV-005 Hypercare & Transition-to-Support (ISSUED 2026-08-19) · CH-005 Super-User Charter (ISSUED 2026-08-19;
  its backfill decision CNC-08 remains open) ·
  16 declared Bengali counterpart files (NOT ON DISK — verified 2026-08-19)
verified_on: 2026-08-19
enumeration_timestamp: 2026-08-19 01:40 (+06)
rule_prefix: RLO — verified unused across all 777 markdown files of the workspace, re-verified at audit 2026-08-19 02:10 (+06)
priority: P0
needed_by: W2
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# RL-004 — Rollout and Branch Wave Deployment Plan

### Category 12 · Code `RL` · Rule space `RLO` · ITIL 4 phased deployment · ISO 21502:2020 §7.7

---

> **`PGD-000` records this document as ◐ against `06-01` §6, with the note:** *"`06-01` §6 describes
> a rollout approach at programme level. `CM-012` provides a branch readiness **communication
> checklist**. The site-by-site plan does not exist."*
>
> `_CATEGORY_OVERVIEW` states the four questions it must answer, and they are the right four:
> which branch is the pilot and on what criteria; what the per-site readiness bar is; who is on site
> and for how long; and what the sequence and pause rule are across eight divisions.
>
> **This document answers all four, and finds that the fourth is not a scheduling question.** The
> rollout rate is bounded by a resource nobody has counted, and §7 counts it.

---

## 1. Purpose

`06-01` §6 says the rollout goes *pilot → Dhaka → major cities → national*. That is a direction, not
a plan. A plan states **how many sites go live in a week, why that number and not a larger one, what
happens to the ones that are not ready, and what the whole sequence costs in elapsed time**.

This document states those things, and the central finding is arithmetic: **the rollout is bounded
by floor-walkers, not by technology, training or migration capacity** — and at the ratios `OP-002`
already declares, the binding rate is **two to three sites per week**, which makes the national
rollout a 15-to-30-week operation rather than an event.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | **The site population** — why "51+" is not a number, and how to plan without one (§3) |
| 2 | **The zone layer and division sequence** — adopting `MG-006` `CUT-18` and extending it to rollout (§4) |
| 3 | **Pilot selection** — eight criteria, derived (§5) |
| 4 | **The per-site readiness bar** — `CM-012`'s eight domains, and what rollout adds (§6) |
| 5 | **Tranche sizing** — the constraint arithmetic, and the rate it produces (§7) |
| 6 | **Go-live-critical roles** — the population that escalates `RL-003` `RD-6` to a programme veto (§8) |
| 7 | **The on-site support model** — who is present, for how long, drawn from where (§9) |
| 8 | **The pause rule** — what stops a rollout, who calls it, and how it restarts (§10) |
| 9 | **The per-wave rollout profile**, all nine, reconciled against `06-01` §6 (§11) |
| 10 | **The Bengali blocker** — why `CUT-23` and `CV-09` are unenforceable today (§12) |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Whether the release is authorised, and the freeze calendar | `RL-001` | Rollout schedules sites, not releases |
| How code reaches an environment; the go-live checklist | `RL-002` | One deployment serves many sites |
| Whether readiness is sufficient to go | `RL-003` | This document supplies the *sites*; `RL-003` assesses them |
| The **wording** of every branch communication | `CM-012`, `CM-005`, `CM-006` | Adopted by citation; §6.2 states the relationship |
| The cutover **command structure** and count sequencing | `MG-006` §7 | **Adopted whole.** §4.1 states why rollout does not build a second one |
| Training content, curricula, learner-hours | `CH-002` | Consumed as a constraint input in §7.4 |
| Hypercare content and exit criteria | `OP-002`, `SV-005` (issued 2026-08-19) | `OP-002` §4.4's ratios are the binding input to §7; neither plan is restated |
| Adoption measurement | `CH-004` | `RL-005` consumes it; this document does not |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| Branch Operations Lead | The whole document. This role runs the rollout |
| Zone Coordinators | §4, §6, §10 — their sites, their bar, their escalation |
| Change Lead | §7 and §9 — the floor-walker demand this plan creates and cannot fund |
| Operations Director | §10 — the pause rule and the authority to invoke it |
| Programme Manager and PMO | §7.6 — the elapsed-time consequence, which changes the wave schedule |
| Support Lead | §9 — who is on site, and when the champions take over |
| Steering Committee | §7.7 — the single decision this document cannot take |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ITIL 4 — Deployment Management** | Phased deployment; pilot deployment | §5's pilot and §11's phased sequence | None |
| **ISO 21502:2020** | §7.7 managing delivery, and §7.3 planning against constrained resource | §7's constraint model is a §7.3 resource plan expressed as a rate | None |
| **PRINCE2 7 (2023)** | Stage and tranche planning; management by exception | §7's tranche, §10's pause rule as an exception with a named tolerance | None |
| **Theory of constraints** | Identify the binding constraint; subordinate the plan to it | §7.5 names the constraint (floor-walkers) and §7.6 sizes the whole rollout to it | Not a formal standard; used as an analytic frame and labelled as one |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `06-01` §6 | Geographic sequence; the T−4 → T+4 rollout pattern per location; parallel-running periods |
| RFP §12.6 | The same sequence and pattern, contractually |
| `06-01` §4 | Team model per wave in FTE; business-side commitment, including **branch champions at 4 hours/week during rollout, W1–W5** |
| `06-01` §9 | *"Adoption failure at a location — pause rollout, diagnose, remediate, re-pilot before continuing"* |
| **`OP-002` §4.4** | **Floor-walking ratios**: pilot branch 1 per 8–10 users for 10 working days; subsequent branch 1 per 12–15 users for 5 working days; `FW-01`…`FW-04` |
| **`OP-002` `HD-03`** | *"Where a wave rolls out to branches in tranches, each tranche gets its own floor-walking period; the wave-level hypercare clock runs from the **last** tranche"* |
| `CM-012` §4.1–§4.8 | Eight readiness domains, confirmers, the not-ready route, `RB-11` re-confirmation, three post-cutover confirmations |
| `MG-006` §7.2, §7.3 | The zone layer `CUT-18`; `CUT-19`…`CUT-23` |
| `DM-014` §4.9 | 51+ sites, one migration team; counting done by branch staff; 200–400 van recall by zone |
| **`05-04` §5** | **Registered roles `R01`–`R38` with headcount** — the population input to §7.2 |
| `MD-003` | The branch master. *"The figure '51+ service centres' is class **P3** until this dataset is populated and confirmed"* |
| `MD-006` §2.1 | The **eight** administrative divisions, loaded as fact |
| `CH-002` §4 | The learner-hour model computed from `05-04` headcounts and `TR-*` durations |
| `PE-004` §8.1 | Rolling and blue/green deployment per component — one deployment serves all sites |

### 2.3 Register gaps and audit findings this document closes or raises

| Finding | Source | Position |
|---|---|---|
| `RL-004` ◐ — *"the site-by-site plan does not exist"* | `PGD-000` | **Closed in specification.** §4, §5, §7 and §11 are the plan. It cannot be closed in execution until `MD-003` is populated (§3) |
| `MGA-06` — 16 declared Bengali counterparts absent | `MG-006` §7.3 | **Independently re-verified 2026-08-19**: 16 files declare `bilingual: yes` and name a `_BN.md` counterpart; **0 `_BN.md` files exist anywhere in `project_content`**. §12 |
| The rollout rate has never been computed | This document, §7 | **New finding `RLA-06`.** The binding constraint is floor-walkers and the rate is 2–3 sites per week |
| `OP-002`'s hypercare durations assume a single go-live per wave | This document, §7.6 | **New finding `RLA-07`.** With `HD-03`'s clock running from the last tranche, W2's hypercare ends beyond W2's own window |
| Two workforce headcounts coexist estate-wide | This document, §3.3 | **New finding `RLA-08`.** *"500+ employees"* occurs 90 times, *"800+ employees/staff"* 30 times, and no document reconciles them |
| `MD-003` is class `P3` and blocks its own consumers | `MD-003` §preamble | Recorded; §3.2 states what a plan can and cannot do without it |

### 2.4 The rule space

Rules carry the prefix **`RLO`**, verified at **zero** occurrences across all markdown files of the
workspace before allocation, re-verified at 2026-08-19 01:40 (+06) after Category 10 and four
Category 13 documents were written concurrently with this one.

---

## 3. The Site Population

### 3.1 "51+" is not a number

Every rollout figure in the estate rests on *"51+ service centres"*. `MD-003` — the branch master
itself — states the position plainly:

> *"⚠ The figure '51+ service centres' is class **P3** (company profile) until this dataset is
> populated and confirmed. `CG-012` §7 requires it to be converted to P1 here."*

> **`RLO-01`. A rollout plan cannot sequence a population whose size is unknown, and this one does
> not pretend to.** The plan below is expressed as a **rate and a rule**, not as a list of dates
> against named sites. When `MD-003` is populated, the rate produces the dates; until then the dates
> would be fiction with a decimal point.

### 3.2 What a plan can do without the list

| Can be determined now | Requires `MD-003` populated |
|---|---|
| The **rate** at which sites can go live (§7) | Which site goes live in which week |
| The **sequence rule** — division, then zone, then site (§4) | The named pilot sites (§5 gives the criteria, not the names) |
| The **readiness bar** per site (§6) | The count of sites failing each domain |
| The **support model** and its cost per site (§9) | The total floor-walker budget |
| The **pause rule** (§10) | — |
| The **elapsed-time consequence** as a range (§7.6) | The elapsed time as a date |

> **`RLO-02`. Populating `MD-003` is a Wave 1 prerequisite of this plan, not a Wave 1 deliverable of
> it.** `MD-003`'s own collection method — *"structured confirmation form per branch, including a
> GPS reading taken on site"* — is itself a 51-site field exercise, and it must complete before the
> first tranche is scheduled. Raised as `Q-01`.

### 3.3 The workforce figure is also unreconciled

Counted across the workspace at 2026-08-19 01:40 (+06):

| Figure | Occurrences | Where |
|---|---:|---|
| *"500+ employees"* / *"500+ staff"* | **90** | `PGD-000`, `06-01`, RFP, BRD and throughout |
| *"800+ employees"* / *"800+ staff"* / *"800+ people"* | **35** | `M29`, `GV-007`, `GV-008`, `SC-001`, `SC-003`, `SC-004`, `SC-011`, `CH-002`, `CM-012` |

> **`RLO-03`. Two workforce denominators coexist and no document reconciles them.** This is the
> `GA-04` defect class — *a percentage carries its denominator* — applied to a headcount, and it is
> the same class as `AUDIT-014` `TS-01`'s five coverage denominators. It matters here because
> **floor-walker demand is computed from headcount**, and a 60% difference in the denominator is a
> 60% difference in the rollout's elapsed time.
>
> §7.2 does not use either figure. It computes the branch-resident population from `05-04` §5's
> per-role headcounts directly, which is the only source that can be counted rather than quoted.
> Recorded as `RLA-08` and routed to `RR-005` and `GV-005`.

---

## 4. Zones and the Division Sequence

### 4.1 One zone layer, not two

`MG-006` `CUT-18` already establishes a zone layer for cutover: 6–8 Zone Coordinators, 6–9 sites
each, reporting to a Branch Coordination Lead.

> **`RLO-04`. Rollout uses `MG-006`'s zone layer unchanged and does not create a second one.** The
> same sites, the same coordinators, the same span-of-control constraint. A branch manager who
> reports to one coordinator for the count and a different one for the rollout has two managers on
> the most stressful week of their year.

| Layer | Count | Rollout accountability |
|---|---:|---|
| Branch Operations Lead | 1 | The rollout rate; the pause decision recommendation |
| **Zone Coordinator** | **6–8** | Their zone's tranche schedule, readiness confirmations and on-site support |
| Branch Manager | 51+ | Their site's `C2` submission and three post-cutover confirmations |

### 4.2 Zones are drawn from divisions, not from convenience

`MD-006` §2.1 loads the **eight** administrative divisions as fact: `DHA` Dhaka · `CTG` Chattogram ·
`RAJ` Rajshahi · `KHU` Khulna · `BAR` Barishal · `SYL` Sylhet · `RAN` Rangpur · `MYM` Mymensingh.

| # | Rule |
|---|---|
| **`RLO-05`** | **A zone never crosses a division boundary.** Divisions are the unit in which travel time, public holidays, local administration and — critically — the branch manager's existing reporting line already work |
| **`RLO-06`** | Where a division holds more than nine sites it is split into multiple zones; where it holds fewer than four it may be combined **only** with an adjacent division, and the combination is recorded | 
| **`RLO-07`** | `MD-003` `BRN-03` already requires `upazila → district → division` integrity. **Zone assignment is derived from `MD-003`, never maintained separately.** A second list of which site is in which zone is a second list that will diverge |

### 4.3 The division sequence

`06-01` §6 gives a four-stage geographic sequence. Expressed as divisions:

| Stage | `06-01` §6 | Divisions | Wave |
|---|---|---|:--:|
| **Pilot** | Dhaka HQ + 5 selected centres | `DHA` only | W1 |
| **Dhaka** | All Dhaka centres (~20) | `DHA` | W2 |
| **Major cities** | + Chittagong, Sylhet, Khulna, Rajshahi | `CTG`, `SYL`, `KHU`, `RAJ` | W3 |
| **National** | All 51+ centres | **+ `BAR`, `RAN`, `MYM`** | W4–W5 |
| New capability | Each new business line to all centres as it goes live | All eight | W6–W8 |

> **`RLO-08`. Three of the eight divisions — Barishal, Rangpur and Mymensingh — are never named in
> `06-01` §6 or RFP §12.6.** They appear only inside *"all 51+ centres"* at W4–W5. They are the
> furthest from Dhaka, the thinnest on connectivity, and they are scheduled last with the least
> planning attention. **This plan names them**, because a site that is only ever referred to as part
> of a remainder is a site nobody has thought about.

| # | Rule |
|---|---|
| **`RLO-09`** | Each division's **first** site is treated as a pilot for that division under §5's criteria and receives pilot-level floor-walking (`OP-002` §4.4, 10 working days), not subsequent-site level. Divisions differ in connectivity, staffing and local practice, and the first site is where that is discovered |
| **`RLO-10`** | Van recall is sequenced **by zone** so field service degrades in one zone at a time (`MG-006` `CUT-20`, `DM-007` `O-06`). Rollout tranches and van-recall zones are the same zones |

---

## 5. Pilot Selection

### 5.1 Why criteria and not names

`06-01` §6 says *"Dhaka HQ + 5 selected centres"* and does not say selected how. A pilot chosen for
convenience — the nearest, the friendliest manager, the one with the newest hardware — proves that
the system works at the easiest site in the network, which is the one piece of information the
programme does not need.

### 5.2 The eight criteria

> **`RLO-11`. The pilot cohort is selected against all eight criteria, scored and recorded. A site
> that scores well on seven and fails one is not a pilot; it is a site that will teach one lesson
> late.**

| # | Criterion | Why | Target for the cohort |
|:--:|---|---|---|
| `PS-1` | **Transaction volume spans the range** | A system that works at 20 jobs a day may not work at 120 | At least one site in the **top quartile** and one in the **bottom quartile** by volume |
| `PS-2` | **Capability mix is representative** | `MD-003` records capabilities per site; a pilot of walk-in-only sites tests one third of the estate | The cohort collectively holds every capability flag in `MD-003` |
| `PS-3` | **Connectivity spans the range** | `ASM-01` assumes ≥ 3G in operating hours; `CM-012` `RB-02` tests at the busiest hour | At least one site at the **weakest measured** connectivity in `DHA` |
| `PS-4` | **Data quality spans the range** | `SRC-005` records per-branch formats and inconsistent order numbering | At least one site with **known-poor** legacy data |
| `PS-5` | **Staffing is normal, not exceptional** | A site staffed above establishment for the pilot proves nothing about the other fifty | No site receives additional permanent headcount for the pilot |
| `PS-6` | **The branch manager is credible with peers, not merely compliant** | The pilot's real output is testimony. `CM-011` handles objections; a respected manager prevents them | At least three of six chosen for standing in the network |
| `PS-7` | **The site can be reached within the working day** | Floor-walkers at 10 working days must physically be there | All pilot sites within same-day travel of Dhaka |
| `PS-8` | **The site is not simultaneously carrying another change** | A branch relocating, re-staffing or under audit is a confounded experiment | Confirmed by the Operations Director |

### 5.3 The technician pilot is separate and is not optional

`06-01` §7 records the adoption risk for field technicians as **Critical** — *"app rejection
collapses the field model"* — and names the mitigation: *"field pilot with respected senior
technicians."*

| # | Rule |
|---|---|
| **`RLO-12`** | The **technician app pilot is a distinct cohort** from the branch pilot, selected under `PS-5`, `PS-6` and `PS-8` from `R10` Senior Technicians, and it runs **before** W2's first branch tranche, not alongside it |
| **`RLO-13`** | Ride-alongs are on real jobs in real network conditions (`OP-002` `FW-03`: *"a ride-along in the branch car park does not count"*), and the cohort is **not** drawn only from Dhaka, because Dhaka's connectivity is the estate's best |

### 5.4 What the pilot must produce before the next tranche

> **`RLO-14`.** The pilot is not complete when it goes live. It is complete when it has produced
> **five things**, and the second tranche does not start until they exist:

| # | Output | Consumed by |
|:--:|---|---|
| 1 | A **measured** count of floor-walker hours actually used per site | §7's rate, replacing the estimate |
| 2 | A **measured** site cutover duration and count duration | `MG-005`, `MG-006` `CV-13` |
| 3 | The eight-domain readiness bar validated — which domains actually failed | §6 |
| 4 | The top five observed error patterns, issued as `TR-024` refresher content | `OP-002` `FW-04` |
| 5 | A revised per-site support estimate signed by the Change Lead | §9 |

---

## 6. The Per-Site Readiness Bar

### 6.1 `CM-012`'s eight domains are the bar

`CM-012` §4.1 defines eight domains `D1`…`D8`, each with a named confirmer, an evidence requirement
and a deadline, and `RB-08` defines the four states — Ready, Conditional, Not ready, Withdrawn.
`RB-09` makes `D1` connectivity, `D3` access, `D6` data and `D8` cash **non-negotiable**.

> **`RLO-15`. `CM-012`'s eight domains are adopted whole as the per-site readiness bar and are not
> restated, extended or reordered here.** `RL-003` §4.7 already maps them into the seven readiness
> dimensions. What this document adds is what happens to the **rollout** when a site fails.

### 6.2 What rollout adds to `CM-012`

| # | Addition | Rule |
|:--:|---|---|
| 1 | **A failed site does not stop its tranche** | **`RLO-16`** — the site is removed from the tranche and joins the next window (`RB-08`). The tranche proceeds at reduced size. `CM-006` `GO-13`'s **partial go** is the communication route |
| 2 | **A failed *domain* across a tranche does stop it** | **`RLO-17`** — where the **same** domain fails at **more than one third** of a tranche's sites, the tranche is paused. `CM-012` §4.6 states the diagnostic: *"eleven sites failing `D2` is a procurement problem, not eleven branch problems"* |
| 3 | **Re-confirmation on slip is `CM-012` `RB-11`'s** | **`RLO-18`** — adopted unchanged; `RL-003` §9 applies the same tiers at assessment level |
| 4 | **The three post-cutover confirmations gate the *next* tranche** | **`RLO-19`** — `CM-012` §4.8's start acknowledgement, parallel-run exit and legacy withdrawal. A tranche whose sites have not confirmed legacy withdrawal (`C9`) does not release capacity for the next one, because its floor-walkers are still deployed |

### 6.3 The readiness bar and the rollout rate are the same constraint seen twice

> **`RLO-20`.** A site is ready when eight domains are confirmed, and six of the eight are confirmed
> by people who are also the rollout's scarce resource — the IT Administrator (`D1`, `D2`, `D3`),
> L&D (`D4`), Data Migration (`D6`) and the Warehouse Manager (`D7`). **`05-04` §5 records
> `R33` IT / System Administrator at 4–8 people for the whole company.** Four to eight people
> confirming three domains at every one of 51+ sites, at T−4, T−3 and T−1 weeks, is a second
> constraint on the same rate §7 computes, and it binds in the same direction.

---

## 7. Tranche Sizing — The Arithmetic

### 7.1 Why this section is the centre of the document

Every other question in a rollout plan has an answer somewhere in the estate. This one has never
been asked: **how many branches can go live in a week?**

`06-01` §6 implies the whole national network is live by W4–W5. `OP-002` §4.4 specifies
floor-walking ratios. `06-01` §4 specifies the team. Nobody has multiplied them together.

### 7.2 Step 1 — the branch-resident population, counted

From `05-04` §5, taking every registered role whose access scope is a **branch, workshop, branch
stock or counter**. Counted from the source table at 2026-08-19 01:40 (+06).

| Role | Description | Low | High |
|---|---|---:|---:|
| `R06` | Branch Manager | 51 | 51+ |
| `R08` | Service Centre Agent | 150 | 250 |
| `R09` | Workshop Supervisor | 20 | 40 |
| `R10` | Senior Technician | 80 | 150 |
| `R11` | Junior Technician | 120 | 250 |
| `R12` | Specialist Technician (L3) | 15 | 30 |
| `R18` | Branch Store Keeper | 51 | 51+ |
| `R29` | Cashier / Counter Finance | 51 | 51+ |
| | **Branch-resident total** | **538** | **≥ 873** |

> **`RLO-21`.** `R06`, `R18` and `R29` are recorded in `05-04` §5 as **"51+"**, which is a floor and
> not a range. The high column therefore reads **≥ 873**, not 873. `CH-002` §4.2 converts the same
> three to *"51–60"*; that is a reasonable working assumption and it is **an interpolation, not a
> source figure**. This document uses the floor, so that the derived rate is optimistic in the
> direction that will be discovered rather than pessimistic in the direction that will be argued.

**Per site**, at 51 sites: **538 ÷ 51 = 10.5 users** (low) · **873 ÷ 51 = 17.1 users** (high).

### 7.3 Step 2 — floor-walker demand per site

From `OP-002` §4.4, unchanged:

| Site type | Ratio | Duration | Demand at 10.5 users | Demand at 17.1 users |
|---|---|---|---|---|
| **Pilot** (first of a wave, and first of a division under `RLO-09`) | 1 per **8–10** users | **10 working days** | 2 walkers × 10 d = **20 walker-days** | 3 × 10 = **30 walker-days** |
| **Subsequent** | 1 per **12–15** users | **5 working days** | 1 × 5 = **5 walker-days** | 2 × 5 = **10 walker-days** |

Central warehouse, workshops, contact centre and head office carry their own separate demand under
`OP-002` §4.4 and are excluded here; they are not part of the branch tranche rate.

### 7.4 Step 3 — floor-walker supply

`OP-002` `FW-02` is explicit: floor-walkers come from **the champion network plus the project team,
never solely from the project team**.

| Source | Available | Constraint |
|---|---:|---|
| **Branch champions** (`06-01` §4) | 1 per branch | **4 hours per week**, W1–W5. A champion is committed at their **own** site, and 4 h/week is 10% of a floor-walking week |
| **Project team**, W2 (`06-01` §4) | 11.5 FTE total | Of these, only the **Change & Training Lead (1.0)**, **Business Analyst (1.0)** and **QA Engineer (1.0)** are plausibly deployable to a branch floor. The remaining 8.5 are developers, architects and platform engineers building W3 |
| Contracted floor-walkers | **0** | Not a line in `06-01` §4 or `GV-007` |

> **`RLO-22`. The realistic sustained supply is three floor-walkers.** The champion contributes
> ~4 hours at their own site, which covers roughly **10%** of one site's subsequent-site demand and
> **does not** transfer to another site. The project team contributes three people, and every day
> they spend on a branch floor is a day not spent on the next wave.

### 7.5 Step 4 — the rate

Demand per tranche of **T** subsequent sites, going live in the same week:

| Case | Walker-days demanded | Supply available (3 walkers × 5 days) | **Maximum T** |
|---|---|---|:--:|
| Low population (10.5 users/site) | 5 T | 15 walker-days | **T = 3** |
| High population (17.1 users/site) | 10 T | 15 walker-days | **T = 1.5** |
| With champions contributing 10% | 4.5 T – 9 T | 15 walker-days | **T = 1.7 – 3.3** |

> **`RLO-23`. The rollout rate is two to three sites per week, and it is bounded by floor-walkers.**
> Not by deployment — `PE-004` §8.1 deploys once, rolling, and serves every site. Not by training
> capacity — `CH-002` §4's learner-hour model schedules ahead of the site. Not by migration
> tooling — `MG-003`'s pipeline is volume-bounded, not site-bounded. **By the number of people who
> can stand next to a user doing the work for the first time.**

| # | Rule |
|---|---|
| **`RLO-24`** | **The default tranche is 3 sites.** It reduces to 2 where the tranche's measured per-site population exceeds 14 users, and to 1 for any division's first site (`RLO-09`, pilot-level floor-walking) |
| **`RLO-25`** | The tranche size is **recomputed after the pilot** from `RLO-14`'s measured walker-hours, replacing §7.3's ratio-derived estimate. `OP-002` `FW-01` — every floor-walker intervention becomes a ticket — is what makes that measurement possible |
| **`RLO-26`** | **Floor-walking is never the variable that absorbs a schedule squeeze.** `OP-002` §4.4 records it as *"the single highest-yield hypercare activity and the first one cut when resourcing is short."* Where the schedule and the rate conflict, the schedule moves or the resource is funded — the ratio does not |

### 7.6 Step 5 — the elapsed-time consequence

At 51 sites, with the pilot cohort of 6 and 8 division-first sites already counted at pilot rate:

| Population case | Subsequent sites | Rate | **Elapsed weeks** |
|---|---:|:--:|:--:|
| Low (10.5 users/site) | 45 | 3 / week | **15 weeks** |
| High (17.1 users/site) | 45 | 1.5 / week | **30 weeks** |

Plus the pilot cohort at 10 working days each, and eight division-first sites at pilot rate.

> **`RLO-27`. `OP-002`'s hypercare durations were set per wave and assume one go-live per wave.
> `HD-03` runs the wave hypercare clock from the **last** tranche. A 15-to-30-week tranche schedule
> therefore ends a wave's hypercare 15 to 30 weeks after its first site went live** — and W2's
> hypercare baseline is **6 weeks**, inside a wave whose whole duration (`06-01` §3, Months 5–8) is
> approximately 17 weeks.
>
> **At the high-population rate, W2's rollout alone outlasts W2.** It collides with W3, whose own
> cutover carries the witnessed cash count at every site.
>
> This is recorded as `RLA-07`. It is not resolved here, because the three routes out of it are all
> decisions above this document's authority (§7.7).

### 7.7 The decision this document cannot take

> **`RLO-28`.** Three routes close `RLA-07`, and choosing between them is a Steering Committee
> decision because each spends a different currency:

| Route | What it costs | Who decides |
|---|---|---|
| **Fund contracted floor-walkers** | Money. Roughly 45–90 floor-walker-weeks across the national rollout, plus travel to eight divisions | Steering Committee, via `GV-008` |
| **Extend the wave schedule** | Time. W2 and W4–W5 lengthen; the 36-month programme moves | Steering Committee, via `GV-004` |
| **Reduce the floor-walking ratio** | Adoption. `06-01` §7 rates field-technician adoption risk **Critical** and branch counter staff **High** | **Not available.** `RLO-26` forbids it, and `OP-002` §4.4 names it as the first thing cut and the highest-yield thing kept |

Raised as `Q-02`, routed to `GV-005` as a **Critical** risk and to `GV-008` as an unfunded cost.

---

## 8. Go-Live-Critical Roles

`RL-003` `GLR-11` escalates a `RD-6` People veto from site-scoped to programme-wide **when the
untrained population includes a role whose absence makes the system unoperable anywhere**, and
delegates the identification of those roles to this section.

> **`RLO-29`. A role is go-live-critical for a wave when the wave's primary transaction cannot be
> completed by any route without it, including the manual fallback in `OP-014`.**

| Wave | Go-live-critical roles | Why | Minimum coverage |
|:--:|---|---|---|
| **W1** | `R06` Branch Manager · `R08` Service Centre Agent · `R33` IT Administrator | Intake and the service-order lifecycle are the wave; `R33` holds `D1`, `D2`, `D3` at every site | 2 trained per site for `R06`/`R08`; **2 per zone** for `R33` |
| **W2** | + `R10`/`R11` Technicians · `R18` Store Keeper | Field model and stock. `06-01` §7: technician app rejection *"collapses the field model"* | 2 per site; technicians ≥ 80% of the site's establishment |
| **W3** | + `R29` Cashier · `R27` Finance Officer | Money movement; the Mushak sequence is asserted per counter | **2 per counter** — a single trained cashier is a single point of statutory failure |
| **W4** | + `R28` Warranty Claims Officer · `R34` Contact Centre Agent · `R22` Account Manager | Contractual external populations | Central roles; 2 minimum per function |
| **W5** | + `R30`/`R31` HR · `R32` Quality Manager | Payroll and ISO audit are zero-tolerance and single-threaded | **`R30` HR Manager is 1–2 people company-wide.** See `RLO-30` |
| **W6–W9** | Per the wave's new business line | Additive capability | 2 per function |

| # | Rule |
|---|---|
| **`RLO-30`** | **Three go-live-critical roles have a company-wide establishment of two or fewer**: `R30` HR Manager (1–2), `R26` Finance Manager (2–4), `R32` Quality Manager (2–4). For these, `RD-6` `P-4`'s *"at least two trained people"* is **not a redundancy target, it is the entire establishment**, and a single absence at W5 is a programme-wide `RD-6` veto under `GLR-11`. Raised as `Q-03` |
| **`RLO-31`** | Go-live-critical coverage is confirmed **per site** at `CM-012` `D4`, and **per wave** at `RL-003` `RD-6` `P-4`. The two confirmations are different: a site can be covered while the wave is not |

---

## 9. The On-Site Support Model

### 9.1 Who is present, and for how long

Adopted from `OP-002` §4.4 and `06-01` §6's T−4 → T+4 pattern, expressed as a site's timeline.

| Offset | Who is on site | Purpose | Source |
|---|---|---|---|
| **`S−4 wk`** | IT Administrator | Connectivity test at the **busiest hour** | `CM-012` `D1`, `RB-02` |
| `S−3 wk` | Data Migration, remotely with the branch | Site data review | `CM-012` `D6` |
| `S−2 wk` | Warehouse Manager or delegate | Count rehearsal (`DM-014` `CV-20`) | `CM-012` `D7` |
| `S−2 wk` | Change Lead | Champion training (`TR-023`, 16 h over four days) | `CM-012` `D5` |
| `S−1 wk` | L&D | All-staff training in Bengali; access provisioned after training | `TR-002`, `CM-012` `D3`, `D4` |
| **`S−0`** | **Floor-walkers** — 1–2 subsequent, 2–3 pilot | Standing beside the user doing the work | `OP-002` §4.4 |
| `S+5 d` | Floor-walkers withdraw (subsequent sites) | Champion takes over | `OP-002` §4.4 |
| `S+10 d` | Floor-walkers withdraw (pilot and division-first sites) | Champion takes over | `RLO-09` |
| `S+2 wk` | — | Parallel-run exit confirmation | `CM-012` §4.8 #2, `DM-014` `C8` |
| **`S+4 wk`** | — | **Legacy withdrawal confirmation** | `CM-012` §4.8 #3, `DM-014` `C9`, BRD §6.5 |

### 9.2 The champion is who remains

`OP-002` `FW-02`: *"the champion is who remains after exit."*

| # | Rule |
|---|---|
| **`RLO-32`** | A site does not enter a tranche without a **confirmed, trained champion and deputy** (`CM-012` `D5`, `NW-16`). The deputy is not optional: a single champion who is ill, on leave or resigns in the fortnight after go-live leaves the site with no local capability |
| **`RLO-33`** | **The champion's 4 hours per week is a floor-walking contribution at their own site, not a substitute for a floor-walker.** §7.4 counts it at ~10% of a subsequent site's demand and no more |
| **`RLO-34`** | **Corrected at audit.** `CH-005` was **issued 2026-08-19**, concurrently with this document, and supplies the release instrument `PGD-000` said did not exist. **The constraint has moved, not closed**: `CH-005` §5.3 `CNC-08` records that released time must be *"backfilled, absorbed, or the release is not real"*, and that **the backfill decision has not been taken** — three options, costed at **1,190–1,622 PW of cover** for option A. Until it is taken, a champion whose branch manager has not been given cover is still a name on a list, and `RLO-32` is still unsatisfied |

### 9.3 The manual fallback must be physically present

| # | Rule |
|---|---|
| **`RLO-35`** | `OP-014`'s manual fallback procedures are **physically on site, in Bengali, before `S−0`** — not available on an intranet the site may not be able to reach. `DM-014` `CV-02` establishes that `P2` has **no system of record** and paper is the only path; a fallback procedure that requires the system to read it is not a fallback |
| **`RLO-36`** | `RL-003` `RD-5` `O-4` verifies `RLO-35` per site. §12 records that **`OP-014`'s Bengali counterpart does not exist**, which makes `RLO-35` currently unsatisfiable |

---

## 10. The Pause Rule

### 10.1 The inherited rule

`06-01` §9: *"Adoption failure at a location — pause rollout, diagnose, remediate, re-pilot before
continuing."* That is the right instinct and it is not operable: it does not say what counts as
adoption failure, who declares it, what is paused, or what re-pilot means.

### 10.2 What triggers a pause

> **`RLO-37`. A pause stops the *next* tranche. It never reverses a site that is already live** —
> that is a rollback decision under `OP-002` §4.7 and is a different question with different
> authority.

| # | Trigger | Measured as | Threshold |
|:--:|---|---|---|
| `PA-1` | **Same readiness domain failing across a tranche** | `CM-012` §4.6 dashboard, per domain | **> ⅓ of the tranche's sites** (`RLO-17`) |
| `PA-2` | **Adoption below plan at live sites** | `OP-002` `HX-08` — transactions in the system vs expected volume | **< 90%** at 10 working days post-go-live, at **> ⅓** of live sites |
| `PA-3` | **Support volume not falling** | `OP-002` `HX-06` | Rising week on week across two consecutive weeks at live sites |
| `PA-4` | **Floor-walker supply below the tranche's demand** | §7's arithmetic, per tranche | Supply < demand for the **next** tranche |
| `PA-5` | **A go-live-critical role uncovered** | §8, `RD-6` `P-4` | Any wave-level uncovered role (`GLR-11`) |
| `PA-6` | **An open `S1`, or any open defect on an `RC-A` population** | `QA-010` `DMG-T1`, `DMG-T2` | **Any** — and this pauses immediately, not at the next tranche boundary |
| `PA-7` | **A statutory exposure at a live site** | Mushak sequence, payroll, filing | **Any** |

### 10.3 Who declares it

| Trigger | Recommends | Decides |
|---|---|---|
| `PA-1`, `PA-4` | Branch Operations Lead | **Branch Operations Lead** — a tranche-level operational call |
| `PA-2`, `PA-3` | Change Lead | **Change Lead with the Operations Director** |
| `PA-5` | Change Lead | **Operations Director** |
| `PA-6` | Head of Quality Engineering | **Automatic.** No decision is taken (`QA-010` §5.5: no body may accept `DMG-T1`/`T2`) |
| `PA-7` | Financial Controller | **CFO** |

| # | Rule |
|---|---|
| **`RLO-38`** | **A pause is a normal outcome and is not escalated as a failure.** `CM-012` `RB-10` and `RL-003` `GLR-09` state the same rule for branch managers and assessors; it applies with the same force to a Zone Coordinator recommending a pause |
| **`RLO-39`** | A pause is **declared to every site in the rollout**, live and pending, within **one working day**, with the reason and the date of the next update. `CM-006` `GO-14`'s logic applies: silence after a visible non-event is filled by a version nobody wrote |

### 10.4 Diagnose, remediate, re-pilot

`06-01` §9's three verbs, made operable.

| Stage | What it means | Exit |
|---|---|---|
| **Diagnose** | Identify whether the cause is **site-specific, domain-specific or systemic** — `CM-012` §4.6's granularity rule: *"eleven sites failing `D2` is a procurement problem, not eleven branch problems"* | A written cause statement naming the class |
| **Remediate** | Fix the class, not the instances. A procurement problem is fixed by procurement; a training problem by `TR-024` refresher content; a defect by `RL-001` §9 | Evidence that the cause is closed |
| **Re-pilot** | **One tranche of one site**, at pilot-level floor-walking, before the rate resumes | The site meets its readiness bar **and** its 10-working-day adoption measure |

| # | Rule |
|---|---|
| **`RLO-40`** | **Re-pilot is a single site, not a reduced tranche.** The purpose is to prove the remediation, and a three-site tranche confounds the proof with the variability between three sites |
| **`RLO-41`** | The rollout resumes at the **previous rate**, not at a recovery rate. `RLO-26` applies: catching up is not a reason to reduce floor-walking |

---

## 11. Per-Wave Rollout Profiles

| Wave | Sites entering | Divisions | Tranches (at 3/wk) | What is distinctive | Binding constraint |
|:--:|---|---|:--:|---|---|
| **W1** | **Dhaka HQ + 5 pilot centres** | `DHA` | 6 sites at pilot rate | The estate's first production go-live; every measurement in §7 is an estimate until this wave produces one | `RLO-14`'s five outputs; nothing proceeds without them |
| **W2** | All Dhaka (~20, i.e. ~14 new) | `DHA` | ~5–9 weeks | **Stock count at every site**, 200–400 van recall, technician app to the field. `DM-014` `CV-04`: the count cannot be compressed by adding people | Counters and van recall, sequenced by zone (`CUT-19`, `CUT-20`) — and floor-walkers |
| **W3** | + Chattogram, Sylhet, Khulna, Rajshahi | `CTG`, `SYL`, `KHU`, `RAJ` | 4 division-first sites at pilot rate, then ~3/wk | **Witnessed cash count at every site**; four new divisions, each with a division-first site (`RLO-09`); travel enters the plan | Travel time and `R33` IT Administrator availability across four divisions |
| **W4** | + remaining sites in live divisions | `DHA`,`CTG`,`SYL`,`KHU`,`RAJ` | ~3/wk | Corporate, brand, contact centre — **external contractual populations**. A site defect is visible to a client under contract | `RD-7` commercial readiness; contact centre is central, not per-site |
| **W5** | **+ Barishal, Rangpur, Mymensingh** — the three divisions `06-01` never names | **All eight** | 3 division-first at pilot rate, then ~3/wk | **National completion.** `06-02` `G5-06`: *"all 51+ service centres operating on the platform."* Payroll and HR go live concurrently | `RLO-30`'s three roles with an establishment of ≤ 2; the furthest sites with the thinnest connectivity |
| **W6** | No new sites | All eight | — | **Capability, not geography.** Native apps with forced upgrade; `M66` ITSM | Not a rollout wave. Floor-walking demand is a fraction of a site wave |
| **W7** | No new sites; **new external population** | All eight | — | Marketplace sellers — outside the employment relationship, with no branch manager to cascade through | `CM-006` `GO-06`'s cascade does not exist for sellers |
| **W8** | No new sites | All eight | — | Scale and optimisation; mostly non-functional | — |
| **W9** | Second-entity test site | Per `G9-01` | 1 | A **second country** entity stood up in ≤ 12 weeks using configuration only | Configuration-only is the criterion; a deployment would fail `G9-01` |

> **`RLO-42`. Only W1–W5 are rollout waves.** W6–W9 deliver capability to sites already live, and
> their floor-walking demand is a fraction of a site wave's. **This is the reason the programme's
> rollout risk is concentrated in the first 22 months**, and it is why `RLA-07`'s elapsed-time
> problem cannot be absorbed by the later waves.

---

## 12. The Bengali Blocker

### 12.1 The requirement

| Source | Requirement |
|---|---|
| `DM-014` `CV-09` | Every freeze instant is stated in **both** Bengali and English in branch communications |
| `MG-006` `CUT-23` | Every instruction reaching branch staff is **Bengali-first**, and comprehension is confirmed, not receipt |
| `CM-012` §4.9 | Branch manager communications are **written, EN + BN** |
| `06-01` §9 | *"Bengali localisation — field adoption fails without it"* — listed under **what cannot be descoped** |
| `RLO-35` | `OP-014` fallback procedures physically on site, **in Bengali** |

### 12.2 The position, independently verified

Counted at 2026-08-19 01:40 (+06) across `project_content/16_Change_Management_and_Comms/` and
`project_content/17_Operations_Support_and_Runbooks/`:

| Measure | Count |
|---|---:|
| Files declaring `bilingual: yes` and naming a `_BN.md` counterpart | **16** |
| `_BN.md` files present anywhere in `project_content` | **0** |

The 16 named counterparts include **`CM-012_Branch_Readiness_Communication_Checklist_BN.md`** — the
readiness checklist every branch manager works from — and **`OP-014_Manual_Fallback_Procedure_Set_BN.md`**
— the fallback 51 branches would work from during a rollback.

> **`RLO-43`. The rollout cannot begin.** Not for want of a plan, a system or a schedule, but because
> the instructions that reach 51+ sites, in the language most of their staff work in, do not exist.
> `MG-006` raised this as `MGA-06`; this document **independently re-verifies it** and records that
> it blocks `RLO-15` (the readiness bar), `RLO-35` (fallback on site) and `RLO-39` (the pause
> declaration) as well as the cutover rules `MG-006` raised it against.
>
> `CM-012` is additionally registered **`P1`** against a **`P0`** rollout that cannot proceed without
> it. Raised as `Q-04`, and as the highest-priority item this document produces.

---

## 13. Governing Rules — Consolidated

| # | Rule | § |
|---|---|:--:|
| `RLO-01` | A rollout plan cannot sequence a population of unknown size; this one gives a rate and a rule | 3.1 |
| `RLO-02` | Populating `MD-003` is a W1 prerequisite of this plan, not a deliverable of it | 3.2 |
| `RLO-03` | Two workforce denominators coexist; §7 uses `05-04` §5 directly instead | 3.3 |
| `RLO-04` | Rollout uses `MG-006`'s zone layer unchanged; there is no second one | 4.1 |
| `RLO-05` | A zone never crosses a division boundary | 4.2 |
| `RLO-06` | Divisions over nine sites split; under four may combine with an adjacent one, recorded | 4.2 |
| `RLO-07` | Zone assignment is derived from `MD-003`, never maintained separately | 4.2 |
| `RLO-08` | Barishal, Rangpur and Mymensingh are named; they appear nowhere in `06-01` §6 | 4.3 |
| `RLO-09` | Each division's first site is a pilot for that division | 4.3 |
| `RLO-10` | Van recall and rollout tranches use the same zones | 4.3 |
| `RLO-11` | The pilot cohort is selected against all eight criteria, scored and recorded | 5.2 |
| `RLO-12` | The technician pilot is a distinct cohort, run before W2's first branch tranche | 5.3 |
| `RLO-13` | Ride-alongs are on real jobs, in real conditions, not only in Dhaka | 5.3 |
| `RLO-14` | The pilot produces five outputs; the second tranche waits for them | 5.4 |
| `RLO-15` | `CM-012`'s eight domains are the readiness bar, adopted whole | 6.1 |
| `RLO-16` | A failed site leaves its tranche; the tranche proceeds at reduced size | 6.2 |
| `RLO-17` | The same domain failing at > ⅓ of a tranche's sites pauses the tranche | 6.2 |
| `RLO-18` | Re-confirmation on slip is `CM-012` `RB-11`'s tiers | 6.2 |
| `RLO-19` | Legacy-withdrawal confirmation gates the next tranche's capacity | 6.2 |
| `RLO-20` | Six of eight readiness domains are confirmed by the rollout's own scarce resource | 6.3 |
| `RLO-21` | `R06`, `R18`, `R29` are "51+", a floor; the high column reads ≥ 873 | 7.2 |
| `RLO-22` | Realistic sustained floor-walker supply is three | 7.4 |
| `RLO-23` | **The rollout rate is 2–3 sites per week, bounded by floor-walkers** | 7.5 |
| `RLO-24` | Default tranche 3; 2 above 14 users/site; 1 for a division's first site | 7.5 |
| `RLO-25` | Tranche size is recomputed after the pilot from measured walker-hours | 7.5 |
| `RLO-26` | Floor-walking never absorbs a schedule squeeze | 7.5 |
| `RLO-27` | **`HD-03`'s clock plus a 15–30 week schedule ends W2's hypercare beyond W2** | 7.6 |
| `RLO-28` | Three routes close `RLA-07`; one is not available and two are Steering decisions | 7.7 |
| `RLO-29` | A role is go-live-critical when the wave's primary transaction fails without it, including fallback | 8 |
| `RLO-30` | Three go-live-critical roles have an establishment of ≤ 2 company-wide | 8 |
| `RLO-31` | Coverage is confirmed per site **and** per wave; they are different confirmations | 8 |
| `RLO-32` | No site enters a tranche without a confirmed champion **and deputy** | 9.2 |
| `RLO-33` | The champion's 4 h/week is ~10% of a site's demand and does not transfer | 9.2 |
| `RLO-34` | `CH-005`'s absence is the binding constraint on `RLO-32` | 9.2 |
| `RLO-35` | `OP-014` fallback is physically on site, in Bengali, before `S−0` | 9.3 |
| `RLO-36` | `RLO-35` is currently unsatisfiable — `OP-014`'s Bengali counterpart does not exist | 9.3 |
| `RLO-37` | A pause stops the next tranche; it never reverses a live site | 10.2 |
| `RLO-38` | A pause is a normal outcome, never escalated as a failure | 10.3 |
| `RLO-39` | A pause is declared to every site within one working day, with the next update date | 10.3 |
| `RLO-40` | Re-pilot is a single site, not a reduced tranche | 10.4 |
| `RLO-41` | Rollout resumes at the previous rate, not a recovery rate | 10.4 |
| `RLO-42` | Only W1–W5 are rollout waves; the risk is concentrated in 22 months | 11 |
| `RLO-43` | **The rollout cannot begin: 16 declared Bengali counterparts, 0 on disk** | 12.2 |

**Forty-three rules.** Counted from this table at 2026-08-19 01:40 (+06).

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **When is `MD-003` populated and converted from class `P3` to `P1`?** Its own collection method is a 51-site field exercise | Operations MDM analyst with the Operations Director | **W1 minus 3 months** | `RLO-01`, `RLO-02`, `RLO-07`; every date in this plan |
| `Q-02` | **Which of §7.7's two available routes closes `RLA-07`** — funded floor-walkers, or an extended wave schedule? | **ERP Steering Committee** | **W1** | `RLO-23`, `RLO-27`; the W2 and W4–W5 schedules |
| `Q-03` | How are `R30`, `R26` and `R32` covered at W5, given an establishment of ≤ 2 company-wide? | HR Director with the Programme Director | **W5 minus 6 months** | `RLO-30`; `GLR-11` escalation |
| `Q-04` | **Who translates the 16 declared Bengali counterparts, and by when?** `CM-012_BN` and `OP-014_BN` are the two that block first | Content Design with the Change Lead | **W1 minus 2 months** | `RLO-43`; `CUT-23`; `CV-09`; the entire rollout |
| `Q-05` | Is `CM-012` re-prioritised from `P1` to `P0` to match the cutover it gates? | PMO | **W1** | `RLO-43` |
| `Q-06` | **Which of `CH-005` `CNC-08`'s three backfill options is chosen, and who funds it?** The charter issued 2026-08-19; the decision inside it has not been taken | **ERP Steering Committee**, on the Change Lead's recommendation | **W1** | `RLO-32`, `RLO-34`; and it compounds `Q-02`, since both spend the same currency |
| `Q-07` | Which figure is the workforce denominator — 500+ or 800+? | Programme Director with HR Director | W1 | `RLO-03`; every headcount-derived estimate in the estate |
| `Q-08` | Does `SV-005`'s hypercare resourcing account for `RLO-27` — a wave clock running from the last of 15–30 weeks of tranches? It was issued hours after this document and does not cite it | Support Lead with the Branch Operations Lead | **W1** | `RLO-27`, `RLO-31` |

---

## 15. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `RL-004-D-01` | How to plan without a site list | (a) Wait for `MD-003` · (b) Assume 51 and name sites · (c) Express the plan as a rate and a rule | **(c)** | (a) blocks the plan on a dataset nobody has scheduled; (b) produces dates that are fiction | The plan has no site-level dates until `Q-01` closes |
| `RL-004-D-02` | Which headcount to compute floor-walker demand from | (a) *"500+ employees"* · (b) *"800+ employees"* · (c) `05-04` §5 per-role, counted | **(c)** | Both estate-wide figures are quoted, neither is counted, and they disagree by 60% | §7.2's 538 – ≥873 branch-resident range, derived and reproducible |
| `RL-004-D-03` | Whether to reduce the floor-walking ratio to hit the schedule | (a) Reduce to 1 per 20–25 · (b) Hold `OP-002`'s ratio and report the consequence | **(b)** | `OP-002` §4.4 names floor-walking as the highest-yield activity and the first one cut; `06-01` §7 rates field adoption risk **Critical** | `RLA-07`: the rollout outlasts its wave, and the decision escalates (`Q-02`) |
| `RL-004-D-04` | Whether to build a rollout zone layer | (a) A rollout-specific zone structure · (b) Adopt `MG-006` `CUT-18` unchanged | **(b)** | A branch manager with two coordinators in their worst week has none | Zone Coordinators carry both cutover and rollout accountability |
| `RL-004-D-05` | Pilot selection: names or criteria | (a) Name six sites now · (b) Eight criteria, names when `MD-003` is populated | **(b)** | Naming sites without volume, capability and connectivity data is selecting for convenience — the failure mode §5.1 describes | `PS-1`…`PS-8` are scored when the data exists |
| `RL-004-D-06` | Whether to name the three unnamed divisions | (a) Follow `06-01` §6's *"all 51+"* · (b) Name Barishal, Rangpur, Mymensingh explicitly | **(b)** | A site referred to only as part of a remainder is a site nobody has planned for | Three additional division-first pilots at W5 (`RLO-09`) |

---

## 16. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | All four `_CATEGORY_OVERVIEW` questions are answered | §5 pilot · §6 bar · §9 on-site model · §4 + §10 sequence and pause |
| `AC-02` | The rollout rate is **derived**, from counted inputs, not asserted | §7.2–§7.5; `05-04` §5 counted, `OP-002` §4.4 ratios, `06-01` §4 team |
| `AC-03` | The binding constraint is named | `RLO-23` — floor-walkers |
| `AC-04` | The elapsed-time consequence is stated even though it is unwelcome | `RLO-27`, `RLA-07` |
| `AC-05` | The decision this document cannot take is escalated with its options costed | `RLO-28`, `Q-02` |
| `AC-06` | Nothing `CM-012` or `MG-006` owns is restated | `RLO-15`, `RLO-04` |
| `AC-07` | Pilot selection is criteria-based and the criteria span ranges, not averages | §5.2 — eight criteria |
| `AC-08` | The pause rule is operable: triggers, thresholds, authority, restart | §10.2, §10.3, §10.4 |
| `AC-09` | Every wave has a profile and a named binding constraint | §11 — nine rows |
| `AC-10` | The Bengali position is **independently re-verified**, not quoted | §12.2 — 16 declared, 0 on disk, counted here |
| `AC-11` | No rule identifier collides with any existing identifier | §2.4 — `RLO` verified at zero, re-verified after concurrent writes |
| `AC-12` | Every open question has an owner and a needed-by date | §14 — seven questions |

**Definition of done.** As `RL-001` §16, subject to the same `PGD-A2-25` qualification.

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `06-01` §4, §6, §9 | Team model, geographic sequence, rollout pattern, contingency |
| Upstream | `OP-002` §4.4, `HD-03` | Floor-walking ratios — the input that produces §7's rate |
| Upstream | `05-04` §5 | Role headcounts — the population input, counted not quoted |
| Upstream | `CM-012` | The eight readiness domains, adopted whole |
| Upstream | `MG-006` §7 | The zone layer, adopted unchanged |
| Upstream | `MD-003`, `MD-006` | The site master (class `P3`) and the eight divisions |
| Upstream | `CH-002` §4 | Learner-hour model; the training constraint that is **not** binding |
| Downstream | **`RL-003`** | Supplies the sites in scope, and `GLR-11`'s go-live-critical roles (§8) |
| Downstream | **`RL-005`** | Rollout rate actual-versus-planned is a PIR estimate-accuracy input |
| Downstream | **`RL-006`** | Legacy withdrawal per site (`C9`) is the decommissioning trigger per source |
| Downstream | `SV-005` (issued 2026-08-19) | Hypercare per tranche; **`RLO-27` is a direct input to its resourcing and `SV-005` was written without it** — raised as `Q-08` |
| Upstream | `CH-005` (issued 2026-08-19) | Supplies the release instrument; its open `CNC-08` backfill decision is `RLO-34`'s residual constraint |
| Downstream | `GV-004` | The wave schedule changes if `Q-02` chooses the time route |
| Downstream | `GV-008` | The floor-walker cost if `Q-02` chooses the money route |
| Lateral | `CM-005`, `CM-006`, `CM-012` | Own the wording of every message this plan schedules |

---

## 18. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`RL-001`](RL-001_Release_Management_and_Versioning_Policy.md) ·
[`RL-002`](RL-002_Deployment_Plan_and_Go_Live_Checklist.md) ·
[`RL-003`](RL-003_Go_Live_Readiness_Assessment_and_Gate_Criteria.md) ·
[`RL-005`](RL-005_Post_Implementation_Review_Standard.md) ·
[`RL-006`](RL-006_Legacy_Decommissioning_Plan.md) ·
[`../09_Data_Migration_and_Cutover/MG-006_Cutover_Plan_and_Runbook.md`](../09_Data_Migration_and_Cutover/MG-006_Cutover_Plan_and_Runbook.md) ·
[`../13_Training_Change_and_Adoption/CH-002_Training_Plan_and_Delivery_Schedule.md`](../13_Training_Change_and_Adoption/CH-002_Training_Plan_and_Delivery_Schedule.md) ·
[`../10_Infrastructure_DevOps_and_Environments/PE-004_CI_CD_Pipeline_Design_Specification.md`](../10_Infrastructure_DevOps_and_Environments/PE-004_CI_CD_Pipeline_Design_Specification.md)

**Workspace**
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` §4, §6, §7, §9 ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §5 ·
`../../project_content/16_Change_Management_and_Comms/CM-012_Branch_Readiness_Communication_Checklist.md` ·
`../../project_content/17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md` §4.4 ·
`../../project_content/17_Operations_Support_and_Runbooks/OP-014_Manual_Fallback_Procedure_Set.md` ·
`../../project_content/12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md` §4.9 ·
`../../project_content/02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-003_Branch_and_Service_Centre_Master.md` ·
`../../project_content/02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-006_Bangladesh_Geographic_Hierarchy.md` §2.1 ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` §12.6

**External standards** *(verified 2026-08-19)*

| Source | Edition | Used for |
|---|---|---|
| ITIL 4 — Deployment Management practice | ITIL 4, current framework | §5, §11 phased and pilot deployment |
| ISO 21502:2020 | Current | §7.3 resource planning, §7.7 delivery |
| PRINCE2 | **7th Edition (2023)** | §10 management by exception |

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| **1.1** | 2026-08-19 | Branch Operations with Change Management | **Audit correction, `PGD-AUDIT-CAT-12`.** `CH-005` was issued 2026-08-19, concurrently with this document, supplying the champion release instrument `RLO-34` recorded as absent. **The constraint moved rather than closing**: `CH-005` §5.3 `CNC-08` records that the **backfill decision has not been taken**, with option A costed at **1,190–1,622 PW of cover**. `RLO-34` and `Q-06` rewritten to the residual constraint, which now shares a currency with `Q-02` | *Pending — `GV-001` `CC-01`* |
| 1.0 | 2026-08-19 | Branch Operations with Change Management | Initial issue. Forty-three `RLO` rules; eight pilot-selection criteria; seven pause triggers; nine wave profiles. **Computes the rollout rate for the first time** — 2–3 sites per week, bounded by floor-walkers, from `05-04` §5 headcounts and `OP-002` §4.4 ratios — and states the consequence (`RLA-07`): with `HD-03`'s clock, W2's hypercare ends beyond W2's own window. Names the three divisions `06-01` §6 never names. **Independently re-verifies that 16 declared Bengali counterpart files do not exist**, and records that the rollout cannot begin without them | *Pending — `GV-001` `CC-01`* |

---

*`RL-004` · Category 12 · Rule space `RLO` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
