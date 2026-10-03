---
id: CH-001
title: Organisational Change Management Plan
category: 13 — Training, Change & Adoption
code: CH
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Change Lead
approver: Chief Executive Officer with the ERP Steering Committee
standards_basis: >
  ACMP Standard for Change Management Version 2 (Association of Change Management Professionals,
  released 26 August 2025) — five process groups · Prosci ADKAR (Awareness, Desire, Knowledge,
  Ability, Reinforcement) as the individual-outcome model · Kotter's 8 Accelerators and the dual
  operating system (Accelerate, 2014; CHANGE, 2021) — NOT the 1995 linear 8-step ·
  ISO 21502:2020 §7 (integrated project management practices) · ISO 10018:2020 (people engagement) ·
  ISO 9001:2015 clause 6.3 (planning of changes)
traces_to: >
  PGD-000 CH-001 · 06-05_Change_Management_and_Training_Plan.md (planned, never written —
  superseded by this document) · AUDIT-019 CM-01, CM-06 · AUDIT-009 R-07 · 00-04 RSK-001,
  RSK-003, RSK-008, RSK-009, RSK-010, RSK-012 · GV-005 §4.2 · 06-01 §7 · URD §24 · RFP §13
depends_on: GV-001 · GV-002 · GV-003 · GV-004 · GV-005 · GV-007 · RQ-007 · CH-003 (lateral)
verified_on: 2026-08-19
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-19 01:20 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# CH-001 — Organisational Change Management Plan

### Category 13 · Code `CH` · ACMP Standard for Change Management v2 (2025) · Prosci ADKAR · Kotter 8 Accelerators · ISO 21502:2020 §7 · ISO 10018:2020

---

> **Local rule prefix: `OCM-nn`.** Verified to return **zero** occurrences workspace-wide before
> allocation, at 2026-08-19 01:20 (+06), by
> `grep -rho "OCM-[0-9]\{1,3\}" --include=*.md .` across all five repositories.
>
> **⚠ The category code `CH` is already a rule prefix elsewhere in the estate.** `CH-01`…`CH-06`
> are channel rules in `project_content/04_Notification_and_Messaging/NT-001` §4, `CH-01`…`CH-05`
> are chart rules in `RP-007`, and `CH-01` is a support-channel rule in `OP-001`. `CH-001`…`CH-005`
> — this category's document identifiers — collide **by digit count** with all three, exactly as
> `MG-nn`/`MG-nnn` did in Category 09 (`MGA-04`) and `MIG-nn`/`MIG-nnn` before it. **No document in
> this category uses `CH-nn` as a local rule prefix**, and every prefix allocated here was verified
> to return zero workspace-wide occurrences first. Recorded as finding `CHA-02`.

---

## 1. Purpose

**`06-05_Change_Management_and_Training_Plan.md` was planned and never written.** In its place the
programme holds eighteen `CM` content files — narrative, calendars, kits, transition packs and
adoption copy — and twenty-four `TR` framework and pack files. That is a great deal of *what will
be said*. It is not a plan.

A plan answers four questions that no file in the estate currently answers:

| # | Question | Where it is answered today |
|:--:|---|---|
| 1 | **Whose work changes, how much, and at which site?** | Nowhere. `CM-018` supplies a *template* for a per-role statement and states that 38 must be produced; none exists, and no statement is per-site |
| 2 | **Who sponsors the change, visibly, and what are they required to do?** | `06-01` §7 says *"visible executive sponsorship"* in three words |
| 3 | **How is resistance detected, classified and answered — and what happens when the honest answer is "you are worse off"?** | `CM-002` §4.7 defines the classification. Nothing defines the response |
| 4 | **How do we know a site, a role or a wave is *ready* — and who may stop a go-live because it is not?** | [`RL-003`](../12_Release_Deployment_and_Transition/RL-003_Go_Live_Readiness_Assessment_and_Gate_Criteria.md) was written on 2026-08-19, concurrently with this document, and holds the **gate**. It cannot hold the **people-readiness criteria**, which is what §7 supplies to it |

**This document is what `06-05` would have been**, restricted to the change half; the training half
is [`CH-002`](CH-002_Training_Plan_and_Delivery_Schedule.md), and `06-05` is **superseded, not
awaited**.

> **The single most important sentence in this plan.** The programme's own risk register rates
> technician rejection of the mobile application (`RSK-008`) **High likelihood / Critical
> consequence**, and `GV-005` §4.2 records its treatment status as *"Design mitigations specified;
> **no pilot scheduled**"*. Five of the six named mitigations for the programme's most dangerous
> adoption risk are change activities. **Not one of them has an owner with time, a date, or a
> budget line.** That is the gap this document exists to close.

### 1.1 Scope

**In scope:**

| # | Covered |
|:--:|---|
| 1 | The change impact assessment method, and its application at **role × site** grain |
| 2 | The sponsorship roadmap: who sponsors, what they must be seen to do, and the cadence |
| 3 | Resistance management — detection, classification, response and escalation |
| 4 | **Change readiness measurement** and the readiness bar a site must clear before cutover |
| 5 | **Change saturation** across nine waves and thirty-six months, and the load limits |
| 6 | The treatment plans for the five adoption risks `00-04` §1.2 registers and `GV-005` carries untreated |
| 7 | The change organisation: roles, RACI, and the appointments the programme has not made |
| 8 | The interface to `GV-003` change control — an approved scope change is a change-impact event |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Training curriculum, delivery, trainers, certification | [`CH-002`](CH-002_Training_Plan_and_Delivery_Schedule.md) | Training is a change lever, not the change plan. Conflating them is how `06-05` came to be one unwritten document instead of two written ones |
| Stakeholder register, message matrix, channel plan, calendar | [`CH-003`](CH-003_Stakeholder_Engagement_and_Communication_Plan.md) | Communication executes the engagement strategy this plan sets |
| Adoption metrics, intervention triggers, sustainment | [`CH-004`](CH-004_Adoption_Measurement_and_Reinforcement_Plan.md) | Measurement of the outcome, not management of the transition |
| Champion and super-user selection, release and charter | [`CH-005`](CH-005_Super_User_and_Champion_Network_Charter.md) | The network is the delivery mechanism; its constitution needs its own instrument |
| The words used — narrative, objection answers, kits, copy | `project_content` `CM-001`…`CM-018` | Content is authored there and governed by `CG-*`. This plan consumes it and never restates it (`CP-01`) |
| Technical change control of releases | [`RL-001`](../12_Release_Deployment_and_Transition/RL-001_Release_Management_and_Versioning_Policy.md) *(issued 2026-08-19)* | Organisational change ≠ release change. Both are called "change management" and they are different disciplines |
| Configuration and document change control | `GV-011`, `GV-003` | A `CR-nnn` is a governance instrument |
| Go-live readiness *assessment* and gate authority | [`RL-003`](../12_Release_Deployment_and_Transition/RL-003_Go_Live_Readiness_Assessment_and_Gate_Criteria.md) *(issued 2026-08-19)* | This plan supplies the **people** readiness criteria that `RL-003` consumes; it does not grant itself gate authority |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Chief Executive Officer** | The sponsorship commitment being asked of them, in hours and in named acts (§5) |
| ERP Steering Committee | The readiness bar, the escalation route for `Interest` objections, and the saturation limits that constrain wave sequencing |
| **Change Lead** *(a post nobody holds — `OCM-Q-01`)* | The operating instrument of the role |
| Operations Director | Site-level readiness, branch manager obligations, and the two adoption risks they own |
| HR Director | The appraisal, backfill and recognition decisions that make the network real |
| Branch managers (51+) | What is asked of them per site, and when |
| PMO | The change items in `GV-004`'s schedule and `GV-005`'s RAID |
| Implementation vendor | The client-side obligations that condition the delivery plan |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / element | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ACMP Standard for Change Management, Version 2** (released **26 August 2025**; CCMP examination transitions to it 1 April 2026) | Process group 1 — *Evaluate change impact and organisational readiness* | §4 impact assessment; §7 readiness measurement | None |
| " | Process group 2 — *Formulate change management strategy* | §3 and §5 | None |
| " | Process group 3 — *Develop the change management plan* (v2 adds 5.2.1 *Develop the resource strategy* and 5.3.1.5 *Develop the readiness plan*) | §7, §10, and `CH-002` §7 for the resource strategy | **Declared departure:** the resource strategy is split across this document and `CH-002` because the training resource is an order of magnitude larger than the change resource and needs its own arithmetic |
| " | Process group 4 — *Execute the change management plan* | §6, §8, §9 | None |
| " | Process group 5 — *Complete the change management effort* | §9.5 sustainment handover; `CH-004` §8 owns the measurement half | None |
| " | v2's emphasis on the **"iterative and non-sequential nature"** of change management | §8's saturation model treats nine waves as nine overlapping change efforts, not one sequence | None |
| **Prosci ADKAR** | Awareness · Desire · Knowledge · Ability · Reinforcement | §4.4 maps every impacted population to the ADKAR element that is actually missing; §6.3 routes each classification of resistance to the element that answers it | **Declared departure:** ADKAR is used as a *diagnostic*, never as a delivery sequence. A 2025 peer-reviewed case study of a German public-media organisation found ADKAR's linear structure did not capture institutional and normative resistance; this plan handles that case in §6.4 through `Interest` escalation rather than by more Desire activity |
| **Kotter — 8 Accelerators, dual operating system** (*Accelerate*, HBR 2012 / book 2014; *CHANGE*, 2021) | Volunteer network operating in parallel with the hierarchy | §9 constitutes the champion network as the "network" half and `CH-005` charters it | **The 1995 linear 8-step model is deliberately not used.** The category overview's undated *"Kotter 8-step"* citation is corrected here — recorded as `CHA-05` |
| **ISO 21502:2020** | §7.2 planning · §7.5 stakeholder engagement · §7.10 change control · §7.13 benefits | §4, §5, §8, and the `GV-003` interface in §10.4 | None |
| **ISO 10018:2020** *(current; ISO 10018:2012 withdrawn)* | Guidance for people engagement; competence section aligned to ISO 9001:2015 | §5 sponsorship, §6 engagement, §9 network | None |
| **ISO 9001:2015** | Clause 6.3 — *planning of changes*: purpose and consequences, integrity of the QMS, availability of resources, allocation of responsibilities | §4.6 records every wave as a clause 6.3 planned change, which the ISO surveillance audit behind `KPI-067` will test | None |
| **ISO 30401:2018 + Amd 1:2022 + Amd 2:2024** | Knowledge management system | Cited only where knowledge transfer is claimed (§9.5). **`ISO/DIS 30401` is in the enquiry phase and will replace the 2018 edition** — flagged to `RR-005` | The category overview cited *"ISO 30401"* with no edition and no amendments; corrected here (`CHA-05`) |

> **`OCM-01` — every standard cited in this category carries an edition and a verification date.**
> Three of the estate's critical findings (`C-04` DSA 2018 repealed twice, `H-01` NIST SP 800-88 r1
> withdrawn, `M-01` Odoo release date) were stale citations, and this category inherited four
> undated citations from its own overview. Verified **2026-08-19**.

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `06-01` §7 | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` | Nine change activities in a nine-row table, and the adoption-risk-by-group table this plan treats |
| `06-01` §4 | " | **The business-side commitment table** — 4 h/week per branch champion W1–W5, 30% super-user during UAT, 20% data owner. `06-01` calls it *"the binding constraint on the programme"* |
| `06-01` §6 | " | The per-location rollout pattern, T−4 weeks to T+4 weeks |
| `06-01` §9 | " | Contingency, including *"adoption failure at a location — pause rollout, diagnose, remediate, re-pilot"* |
| `06-02` §4 | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` | Gate criteria `G1-01`…`G9-nn`, including `G1-03` (3-minute intake), `G1-11` (UAT signed off by named super-users) and `G2-01` (100% of Dhaka technicians in daily use) |
| `00-04` §1.2 | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-04_Risks_Assumptions_Dependencies_and_Governance.md` | `RSK-008`…`RSK-012` — the five adoption and change risks |
| `05-04` §5 | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` | The 38 registered roles `R01`–`R38` with headcount |
| `CM-001`…`CM-018` | `../../project_content/16_Change_Management_and_Comms/` | 18 files, 6,980 lines, **313 governing rules across 18 prefixes** (counted by `AUDIT-019` §2.2) |
| `TR-001`…`TR-024` | `../../project_content/08_Training_and_Enablement/` | Training strategy, curriculum map, 15 role packs, instruments, job aids |
| `AUDIT-019` | `../../project_content/_AUDIT/AUDIT-019_Category_16_CM_Content_Audit.md` | 14 findings, 1 critical; 10 open |
| `AUDIT-009` | `../../project_content/_AUDIT/AUDIT-009_Category_08_TR_Content_Audit.md` | 11 findings, 1 critical; 9 open |
| `GV-005` §4.2 | `../00_Programme_Governance_and_Control/GV-005_RAID_Register.md` | The twelve Critical risks and their **treatment status** — the field `00-04` does not carry |
| `GV-007` §8 | `../00_Programme_Governance_and_Control/GV-007_Estimation_Model_and_Resource_Plan.md` | The resource plan, in which **no trainer, no change practitioner and no champion backfill appears** |
| URD §24 · RFP §13 | `../../primary-doc/` | Transition requirements, user adoption, and the contractual change-management obligation |

> **`OCM-02` — this plan enumerated every category it cites, at the moment of writing, and records
> the timestamp.** `AUDIT-019` `CM-01` is the CRITICAL finding that eighteen `CM` files were
> authored against a stale status table and asserted **24 times in 13 files** that four written
> categories were empty, when **58 files** were on disk. Its proposed rule is adopted here verbatim:
> *the register's status table is not a source for what exists*. Enumeration at
> **2026-08-19 01:20 (+06)**: `project_content` **488** files, `1000fix_ERP_Module` **123**,
> `primary-doc` **4**, `old-primary-doc` **6**, `project-guide-doc` **131** `.md` (142 files of all
> types). **Total 752 `.md` files.** Reproduction:
> `find <repo> -name '*.md' -type f | wc -l`.

### 2.3 Audit findings this document closes, and how

| Finding | Source | Severity | How this document treats it |
|---|---|:--:|---|
| **`CM-01`** | `AUDIT-019` | **CRITICAL** | Closed **as a control**, not as a correction. §4.7 makes a change-impact assessment invalid unless its enumeration timestamp is inside it, and `OCM-02` makes the register non-authoritative for existence. The 24 assertions were corrected in the files; the control that prevents recurrence is here |
| **`CM-06`** | `AUDIT-019` | High | **Treated, not closed.** §9.2.4 sets out the W1–W5 substitute for the `RSK-008` incentive-visibility mitigation that `M57` cannot deliver before W5, and names the decision that must be taken. The decision belongs to the HR Director and CFO; a plan cannot take it |
| **`CM-03`** | `AUDIT-019` | High | **Referred to [`CH-003`](CH-003_Stakeholder_Engagement_and_Communication_Plan.md) §3**, which retires one of the two current wave calendars. This plan uses `06-01` §3 / `06-02` §4 exclusively and says so |
| **`CM-08`** | `AUDIT-019` | Medium | Referred to `CH-003` §4, which adopts `OP-001` §4.1 as the single external enumeration |
| **`CM-09`** | `AUDIT-019` | Medium | Referred to `CH-003` §4.4 — the `CM`/`EO` transition-versus-onboarding boundary |
| **`CM-12`** | `AUDIT-019` | Medium | §6.5 records the four company positions that block `G2` factual review of `CM-011` and `CM-015`, and gives each an owner and a needed-by date. **Two of them are this plan's own open questions** |
| **`AUDIT-009` `R-07`** | `AUDIT-009` | — | §10.3 and `CH-002` §7. *"The delivery model currently rests on people who have not been asked"* — quoted because no paraphrase improves it |
| **`RSK-008` untreated** | `GV-005` §4.2 | **Critical** | §9.2 — a dated field-pilot plan with entry and exit criteria |
| **`RSK-001` untreated** | `GV-005` §4.2 | **Critical** | Referred to [`CH-005`](CH-005_Super_User_and_Champion_Network_Charter.md), which is the instrument that releases the time |

---

## 3. What This Change Actually Is

**`OCM-03`: the size of the change is stated, counted, before the plan for it.** A change plan
written without a stated magnitude produces activity proportional to the change team's capacity
rather than to the change.

### 3.1 The magnitude, counted

| Dimension | Figure | Source, counted 2026-08-19 01:20 (+06) |
|---|---:|---|
| Registered roles whose work changes | **35 of 38** | `05-04` §5; `R36`–`R38` are external (`CU-04`) |
| Internal population, sum of role bounds | **732 – 1,368** | Summed from `05-04` headcounts — §4.2 below |
| Sites | **51+** | `06-01` §6 |
| Waves | **9** | `06-01` §2 |
| Programme duration | **36 months**, benefits review at 42 | `06-01` §8 |
| Modules replacing existing practice | **67** | `1000fix_ERP_Module/03_Modules` |
| Portals introduced | **12** | `04_Portals_and_Applications` |
| Legacy systems switched off | **48** | `DM-002` |
| Customers whose experience changes | **250,000+/month** | BRD |
| **Adoption risks rated High or Critical** | **5 of 5** in `00-04` §1.2 | `00-04` §1.2 — no adoption risk is rated Medium or below |

### 3.2 The five ways this programme fails on the people side

`00-04` §8 names five programme failure modes. Three are change failures, and `GV-005` §4.2 records
that **the two Critical ones are untreated**:

| # | Failure mode | Registered as | Rating | Treatment status (`GV-005` §4.2) | Owned here by |
|:--:|---|---|:--:|---|---|
| 1 | **Super-users are not released and UAT stalls** | `RSK-001` | **Critical** | ⬜ **Untreated.** `D-002` open since 2026-08-12 | [`CH-005`](CH-005_Super_User_and_Champion_Network_Charter.md) |
| 2 | **Technicians reject the mobile app** | `RSK-008` | **Critical** | ⬜ Design mitigations specified; **no pilot scheduled** | §9.2 |
| 3 | Branch staff resist at the counter | `RSK-009` | High | Carried | §9.3 |
| 4 | Marketplace sellers fail to adopt | `RSK-010` | High | Carried | `CH-004` §6 |
| 5 | Management reverts to spreadsheets | `RSK-012` | High | Carried | §9.4 |
| — | *(compounding)* Programme fatigue over 36 months | `RSK-003` | High | Carried | §8 saturation |

> **`OCM-04` — an adoption risk with a specified mitigation and no scheduled activity is
> untreated.** `GV-005` introduced the treatment-status column precisely so that *"mitigation
> specified"* could stop being read as *"mitigation in place"*. This plan inherits that distinction
> and applies it to every activity it commissions: **each carries an owner, a date and a funding
> position, or it is recorded as unfunded in §10.3.**

### 3.3 What is *not* changing, and why saying so matters

`CM-001` §4.3 owns this content and it is not restated here (`CP-01`). The planning consequence is:

**`OCM-05`: every change impact statement declares what is unaffected, and the declaration is
verified before issue.** `CM-018`'s nine-section structure requires it. Unverified reassurance is
worse than no reassurance: it is discovered at go-live, and it is discovered by the person who was
reassured.

---

## 4. Change Impact Assessment

**`OCM-06`: change impact is assessed at *role × site*, not per programme and not per role alone.**

The programme's existing instruments assess at two grains and neither is sufficient:

| Instrument | Grain | What it misses |
|---|---|---|
| `CM-018` change impact statement | **Per role**, 38 of them | That the same role at a Dhaka pilot centre and at a district branch faces different connectivity, different volumes, different staffing depth and a different wave |
| `CM-012` branch readiness checklist | **Per site**, 51+ of them | That a site with three roles ready and two not is not ready, because the checklist does not decompose by role |

### 4.1 The assessment method

Five dimensions, scored `0`–`3` per role per site. **`OCM-07`: the score is evidence-based and its
evidence is named in the cell.**

| # | Dimension | `0` | `1` | `2` | `3` |
|:--:|---|---|---|---|---|
| **D1** | **Process** — how much of the daily task sequence changes | No change | New screen, same sequence | New sequence, same outcome | **New sequence and new outcome** (e.g. paper job card → `P02`) |
| **D2** | **System** — how much of the day is spent in a new tool | < 10% | 10–30% | 30–70% | **> 70%** |
| **D3** | **Authority** — what the person may now decide, or may no longer decide | Unchanged | Minor | Approval limit or route changes | **A discretion is removed or a control is introduced** |
| **D4** | **Measurement** — whether the person's work becomes visible in a way it was not | Unchanged | Aggregate only | Named, periodic | **Named, continuous, comparable** |
| **D5** | **Environment** — device, connectivity, language of work, physical setting | Unchanged | Minor | New device or connectivity dependency | **New device, new language of record, or offline dependency** |

**Impact class** = sum of D1–D5:

| Sum | Class | Consequence for the plan |
|:--:|---|---|
| 0–3 | **Light** | Communication only. `CM-018` statement optional |
| 4–7 | **Moderate** | Statement required; role pack; standard support |
| 8–11 | **Heavy** | Statement required per site; champion presence at go-live; pre-wave engagement session |
| **12–15** | **Severe** | All of the above **plus** a named executive sponsor act (§5), a pilot before rollout, and a **role-specific readiness criterion carried into `RL-003`** |

### 4.2 The population being assessed

Summed from `05-04` §5 headcounts at 2026-08-19 01:20 (+06). **This is a count, not a quotation.**

| Grouping | Roles | Population (low – high) |
|---|---|---:|
| Executive and management | `R01`–`R07` | 59 – 74 |
| Service delivery | `R08`–`R14` | 405 – 772 |
| Logistics, inventory, procurement | `R15`–`R20` | 135 – 283 |
| Commercial | `R21`–`R25` | 22 – 55 |
| Finance | `R26`–`R29` | 67 – 94 |
| People, quality, technology | `R30`–`R33` | 10 – 20 |
| Contact centre | `R34`–`R35` | 34 – 70 |
| **Registered internal total** | **35 roles** | **732 – 1,368** |
| Unregistered but operating — field auditors (`AUDIT-009` `TR-07`) | — | 20 – 60 |
| Unregistered — Sustainability (`SP-026`), Rental Operations (`SP-027`) (`AUDIT-009` `TR-02`) | — | **not enumerable** |
| **Total assessed population** | | **752 – 1,428+** |

> **⚠ `CHA-01` — the role register's upper bounds sum to 1,368 against a workforce the estate
> describes as "500+, growing to 800+".** `CM-002` `S17` describes the wider workforce as *"the
> remainder of 500–900"*. **The upper bounds cannot all be true simultaneously**, and every
> downstream figure — cohort count, trainer days, translation volume, licence cost, learner-time
> cost — is driven by them. This is not a rounding matter: the high case is **87% larger** than the
> low case. Recorded as open question `OCM-Q-02`, owned by HR with MDM, and as an audit finding.

### 4.3 The severe- and heavy-impact populations — assessed

Assessed against §4.1. **`OCM-08`: a Severe classification obliges the plan; it does not merely
describe the role.**

| Role | Pop. | D1 | D2 | D3 | D4 | D5 | Σ | Class | The specific thing that changes |
|---|---:|:-:|:-:|:-:|:-:|:-:|:-:|---|---|
| **`R10`–`R12` Technicians** | 215 – 430 | 3 | 3 | 2 | **3** | **3** | **14** | **Severe** | Paper job card → `P02` on a Company device, offline-first, in Bengali, with earnings and timing visible. `RSK-008` |
| **`R29` Cashier / Counter Finance** | 51 – 60 | 3 | 3 | **3** | 2 | 1 | **12** | **Severe** | Cash handling moves inside a controlled ledger with `SP-019` banking discipline. A discretion is removed |
| **`R16` Rider / Delivery Agent** | 50 – 150 | 2 | 3 | 1 | **3** | **3** | **12** | **Severe** | POD capture on device, custody chain, cash reconciliation, continuous visibility of movement |
| **`R13` Remote Support Engineer** | 15 – 40 | 3 | 3 | 2 | 2 | 2 | **12** | **Severe** | A new business line (`M05` MSP) with privileged access to customers' infrastructure — **and no course pack** (`AUDIT-009` `TR-02`) |
| `R08` Service Centre Agent | 150 – 250 | 3 | 3 | 2 | 2 | 1 | **11** | Heavy | Intake in under 3 minutes (`G1-03`) while learning the system, at the counter, with a queue. `RSK-009` |
| `R18` Branch Store Keeper | 51 – 60 | 3 | 3 | 2 | 2 | 1 | **11** | Heavy | Count accountability becomes continuous; van stock reconciles |
| `R27` Finance Officer | 10 – 20 | 3 | 3 | **3** | 2 | 0 | **11** | Heavy | Control tightening, parallel close, statutory filing inside the system |
| `R34` Contact Centre Agent | 30 – 60 | 3 | 3 | 1 | **3** | 1 | **11** | Heavy | Six channels; disposition coding at 100% completeness (`G4-06`) |
| `R33` IT / System Administrator | 4 – 8 | 3 | 3 | **3** | 1 | 1 | **11** | Heavy | Becomes the operator of `M29` identity for 752–1,428 people |
| `R06` Branch Manager | 51 – 60 | 2 | 2 | 2 | **3** | 1 | **10** | Heavy | Measured on a branch dashboard they did not design — `00-04` §1.2's own words |

**Four roles classify Severe, covering 331 – 680 people — 44% – 48% of the assessed population.**

> **`OCM-09` — `R13` is Severe and has no training pack.** `AUDIT-009` `TR-02` routes 15–40 remote
> support engineers to `TR-021` plus a 6-hour MSP delta. `KB-007` §5.1 establishes that a wrong
> action on a degraded array destroys data no subsequent skill recovers. **A Severe-class change,
> for a population holding privileged access to customers' infrastructure, delivered on an interim
> route.** This plan does not accept it: §9.6 requires a decision before the first MSP contract
> goes live, and `CH-002` §5.4 costs the dedicated pack.

### 4.4 ADKAR diagnosis per severe and heavy population

**`OCM-10`: the ADKAR element that is missing is diagnosed before an intervention is chosen.**
Applying more Awareness to a Desire problem is the most common and most expensive change error.

| Population | Missing element | Evidence for the diagnosis | Intervention that follows | Wrong intervention |
|---|---|---|---|---|
| **Technicians `R10`–`R12`** | **Desire** | `00-04` `RSK-008` names monitoring, earnings and device cost as the concerns; `CM-002` `S07` records *"being timed"*. These are not information deficits | **Field pilot with respected senior technicians** (§9.2); earnings visibility; device provision; Bengali-first | A briefing. A poster. A town hall |
| **Cashiers `R29`** | **Ability** | A control is introduced and a discretion removed; the task itself is new | Practice on a sandbox with realistic data; a counter-cash-specific route (`CH-002` `TPD-Q-03`) | Communication about why controls matter |
| **Riders `R16`** | **Ability**, then **Reinforcement** | Device operation and POD discipline are learnable; sustaining them across 50–150 people at 51+ sites is not automatic | Mobile microlearning; supervisor sign-off; `CH-004` reinforcement | A one-off training day |
| **Branch managers `R06`** | **Desire** | *"Visibility cuts both ways"* (`00-04` §1.2). The objection is to being measured, not to the tool | **Involve in KPI design** — `00-04`'s own mitigation; position the dashboard as their instrument | More dashboard training |
| **Service centre agents `R08`** | **Ability** | The `G1-03` bar is 3-minute intake *while learning* | Speed as the product's design goal; floor-walking; job aids at the counter | Exhortation to be faster |
| **Finance `R26`–`R28`** | **Knowledge** | The process is genuinely more complex; the parallel close is real work | Early design involvement (already `00-04`'s mitigation); parallel run; classroom | Reassurance |
| **Management `R01`–`R05`** | **Reinforcement** | `RSK-012` — reversion to spreadsheets happens *after* capability exists | **Withdraw the source data** (`UP-08`, `RSK-012` mitigation); require decisions to cite the dashboard | Dashboard training |
| **Remote support `R13`** | **Knowledge** | A genuinely new domain with a severe failure mode | A dedicated pack (§9.6) | An interim delta on a system-administrator course |

### 4.5 The site dimension

**`OCM-11`: a role's impact class is modified by site, and the modifier is recorded.**

| Site attribute | Modifier | Rationale |
|---|:--:|---|
| Connectivity below the `05-06` threshold for the role's portal | **+1 D5** | Offline dependence becomes real rather than theoretical |
| Site staffing at or below two people in the affected role | **+1 D2** | No colleague to ask; no cover for a training absence |
| Site is Bengali-only in working language | **+1 D5** where the material is English-first | `SK-08`, `LS-07` |
| Site goes live in **W1 or W2** | **+1 D1** | Least mature product, least mature support, most defects |
| Site has an unresolved legacy data-quality finding (`MG-002`) | **+1 D1** | The first week is spent on data, not on the task |
| Site has **no confirmed champion and deputy** | **+1 to every dimension** | `CNC-14`: the site is not ready for cutover at all |

### 4.6 ISO 9001 clause 6.3 — each wave is a planned change

**`OCM-12`: every wave is registered as a clause 6.3 planned change and the four clause elements
are answered before the wave gate.** `KPI-067` targets **zero ISO major non-conformances**, and
`M23` holds the QMS. A 36-month replacement of the operating system of a certified organisation,
executed without clause 6.3 records, is a finding waiting for a surveillance visit.

| Clause 6.3 element | Where it is answered, per wave |
|---|---|
| (a) The purpose of the change and its potential consequences | `CM-005` wave launch kit + this plan's §4 assessment for the roles in scope |
| (b) The integrity of the quality management system | `M23` process-map update; `SP-*` SOP revisions; `RQ-007` To-Be process baseline |
| (c) The availability of resources | §10.3 — **and this is the element the programme currently fails** |
| (d) The allocation or reallocation of responsibilities and authorities | `05-04` access-matrix delta; `CM-018` §6 authority and access section |

### 4.7 Producing the assessments

| Element | Value |
|---|---|
| Instrument | `CM-018` nine-section template, **extended by the §4.5 site modifier** |
| Volume | **38 role statements** (`CM-018` §4.5) × site-modifier annexes for the **four Severe roles across 51+ sites** |
| Effort | `CM-018` §4.7 derives **95–140 person-days** for the 38 statements alone, against a Master Index allocation of **90–140 person-days for all eighteen `CM` files** (`AUDIT-019` `CM-07`). This plan adds the site annexes: **+15–25 person-days** |
| Timing | For the roles in scope of a wave: issued at **Kickoff + 4 weeks** for W1 (`CA-16`) and **wave start + 2 weeks** thereafter (`CA-04` `M2`) |
| **Validity** | **`OCM-13`: an assessment carries the enumeration timestamp of the sources it was derived from, and is invalid twelve weeks after it** |
| Approval | The role's business owner + the Change Lead. **Severe class additionally requires the executive sponsor named in §5.2** |

> **`OCM-13` is `CM-01`'s control.** The `CM` set was authored against a register that was correct
> when written and wrong when read. Timestamping the assessment does not stop the estate moving; it
> makes the staleness visible at the moment someone relies on it, which is the only property a
> control of this kind can have.

---

## 5. Sponsorship

**`OCM-14`: sponsorship is a set of named, dated, observable acts by named people — never a
statement that sponsorship is visible.** `06-01` §7's entire treatment is the phrase *"visible
executive sponsorship"*.

### 5.1 What sponsorship has to survive

| Test | The failure it prevents |
|---|---|
| The sponsor is asked to do something that costs them | Sponsorship that costs nothing is read, correctly, as endorsement rather than commitment |
| The sponsor appears **at the site**, not only at the town hall | 51+ branches; the ones never visited conclude they do not matter |
| The sponsor answers the hard question in public | `CM-011` objections `OB-01` (job security) and `OB-05` (opening variances) cannot be answered by the Change Lead |
| The sponsor **stops something** to make room | §8's saturation limits are unenforceable without an executive who will cancel a competing initiative |

### 5.2 The sponsorship roadmap

| Sponsor | Role in the coalition | Committed acts | Cadence | Sourced from |
|---|---|---|---|---|
| **CEO** | **Primary sponsor.** Owner of `RSK-001` and `RSK-012` | Opens the W0 town hall; chairs the quarterly all-staff; personally escalates any super-user below 25% availability; **signs the champion release letters** (`CH-005` §5) | 4 h/month steering + 1 town hall/quarter + 1 gate appearance/wave | `06-01` §4; `00-04` §1.1 owner column |
| **Operations Director** | Sponsor for `R06`–`R20` — the largest impacted population. Owner of `RSK-008` and `RSK-009` | Attends the **field pilot** in person (§9.2); visits every pilot site in W1; owns the branch-readiness escalation at 48 hours | Monthly branch-manager briefing; per-site in their wave | `CM-002` §4.8 |
| **CFO** | Sponsor for `R26`–`R29`. Owner of the incentive-scheme approval (`BRU-PIC-01`) | Confirms the **opening-variance amnesty position** (`CM-011` `O-01`) before W1 communications; approves the recognition budget | Fortnightly finance forum in W3 | `AUDIT-019` `CM-12` |
| **HR Director** | Sponsor for the workforce contract of the change | **Decides the appraisal-recognition question** (`CNC-11`); approves backfill; owns the statutory induction obligation | Monthly | `CM-008` §4.10 |
| **CTO** | Sponsor for `R33`, `R13` and the platform | Owns the `M29` ↔ `M22` competence-gate confirmation (`AUDIT-009` `R-02`) | Per wave | `AUDIT-009` |
| **CCO** | Sponsor for `R21`–`R25` and the external counterparties | Owns `RSK-010` seller adoption | Monthly | `00-04` |
| **Branch manager × 51+** | **The sponsor the workforce actually sees** | Nominates and releases the champion in writing; confirms site readiness; runs the huddle | Weekly in their wave | `CM-012`, `CM-008` §4.3 |

> **`OCM-15` — the branch manager is a sponsor, not a recipient.** Fifty-one-plus people carry the
> credibility of this programme in the only place the workforce experiences it. `CM-002` records
> their stated concern as *"being measured on a dashboard they did not design"* — which means the
> programme is asking its most numerous sponsor group to advocate for the instrument of their own
> measurement. §4.4 routes that to Desire, and `00-04`'s own mitigation — **involve them in KPI
> design** — is the treatment. It has no owner and no date. `OCM-Q-04`.

### 5.3 Sponsor readiness

**`OCM-16`: a sponsor who cannot answer the three questions their population will actually ask is
not ready to sponsor, and is briefed before they appear.**

| Population | The question that will be asked | Who must be able to answer it |
|---|---|---|
| Technicians | *"Is this being used to time me and cut my pay?"* | Operations Director — **not** the Change Lead, and **not** in English |
| Counter staff | *"Am I going to be slower in front of a queue?"* | Branch manager, with the measured intake time |
| Finance | *"Who carries the opening variance?"* | **CFO.** `CM-011` `OB-05` is blocked on this, and it blocks `G2` factual review |
| Everyone | *"Will there be redundancies?"* | **CEO.** `CM-011` `OB-01` is blocked on `CON-10`'s standing |
| Branch managers | *"Will I be judged on a number I did not agree?"* | Operations Director |

> **Two of these five have no answer today**, and both are recorded in `AUDIT-019` `CM-12` as
> blocking the factual-review gate on `CM-011`. They are carried here as `OCM-Q-05` and `OCM-Q-06`
> with owners and dates, because a communication plan cannot resolve a company position.

---

## 6. Resistance Management

`06-01` §7 requires resistance to be *"actively tracked"*. `CM-002` §4.7 defines the tracking
instrument. **Neither defines the response**, and the response is where change plans fail.

### 6.1 The classification, inherited

`CM-002` `SK-15` classifies every objection instance as `Capability`, `Clarity`, `Belief` or
`Interest`. **`OCM-17`: this plan does not re-define the classification; it defines what happens
after it.**

### 6.2 Detection

| Source | Owner | Cadence | Feeds |
|---|---|---|---|
| Champion forum item 3 — *questions from the floor* | Change Lead | Monthly | `CM-002` §4.7 log |
| Branch huddle escalations | Branch manager | Weekly in wave | " |
| UAT session observations | PMO | Per session | " |
| Support ticket themes (`OP-003`) | Support Lead | Weekly | " |
| **Adoption telemetry** | `CH-004` | Weekly in rollout | " |
| **Silence** | Change Lead | Per wave | `SK-16` — two waves of silence from a `Support` group is a coverage failure, not consent |

### 6.3 Response, by classification

| Class | Meaning | Response | **Who owns it** | Never |
|---|---|---|---|---|
| **`Capability`** | *Cannot* | Training, job aid, refresher, device, connectivity — a `CH-002` referral with a date | L&D | Answered with a message |
| **`Clarity`** | *Does not understand* | `CM-011` objection-index entry; re-brief through the champion, not by re-broadcast | Change Lead | Answered by repeating the original message |
| **`Belief`** | *Does not accept the reason* | **Sponsor act** (§5.2) — a person with authority answers in person, at the site, in the working language | The population's sponsor | Delegated to the Change Lead |
| **`Interest`** | *Understands, and is worse off* | **Escalated to the Steering Committee within one meeting cycle**, with the quantified detriment | Change Lead → `S02` | **Answered with better messaging.** `SK-15` |

> **`OCM-18` — an `Interest` objection is a business decision, not a communication task.** The
> programme has at least three known `Interest` positions: technicians whose earnings become
> visible and comparable, counter staff whose intake time becomes measured, and managers whose
> manual reporting discretion is withdrawn — `RSK-012`'s own mitigation is *"retire the source
> data"*, which is a deliberate detriment, correctly identified. Each is legitimate. Each needs a
> Steering decision recorded in `GV-003`, not a persuasion campaign.

### 6.4 The case ADKAR does not cover

Where an objection is `Interest` **and** the detriment is real **and** the Steering Committee
confirms the change anyway, ADKAR offers Desire-building activity, and it will not work.

**`OCM-19`: in that case the plan states the position honestly, records it, and manages the
consequence instead of the sentiment.**

| Element | Requirement |
|---|---|
| The position is **stated**, in both languages, by the sponsor | Not softened, not deferred to a later message |
| The compensating action is stated, or its absence is | `CM-017` §4.5's permitted recognition patterns are the only lever available before W5 (§9.2.4) |
| The affected population's **attrition and error rates are monitored** for two waves | `CH-004` §5 |
| The decision is recorded in `GV-003` as a `D-nnn` with the detriment named | `GV-003` |

### 6.5 Company positions that block change communication today

Extracted from `AUDIT-019` `CM-12`, with an owner and a date attached here because the audit could
not assign them:

| # | Position | Blocks | Owner | Needed by |
|:--:|---|---|---|---|
| 1 | **Job security** — the standing of `CON-10` | `CM-011` `OB-01`; every town hall | **CEO** | **W0 — before the first communication** |
| 2 | **Opening-variance amnesty** at inventory and cash cutover | `CM-011` `OB-05`; `G2` factual review | **CFO with Operations Director** | **W1 − 6 weeks** |
| 3 | **Monitoring disclosure** — `LG-020` `AU2` | `CM-011` `OB-02`; **`P02` go-live disclosure** | Legal Counsel with the DP Forum | **W2 − 8 weeks** |
| 4 | Seller commercial terms — `D-03`, `D-09`, `D-10` | `CM-015` | CCO | W7 − 12 weeks |

> **Position 3 is the one to watch.** A monitoring disclosure that is not settled blocks the go-live
> of the application carrying the programme's Critical adoption risk, for a population whose stated
> objection is *being monitored*. `RSK-032` rates PDPA non-compliance Critical with enforcement
> around **13 May 2027 — inside Wave 4**.

---

## 7. Change Readiness

**`OCM-20`: readiness is measured, per site and per role, against a published bar, by someone with
the authority to say "not ready".**

**⚠ Corrected at issue.** This section was drafted while `RL-003` was ⛔; [`RL-003`](../12_Release_Deployment_and_Transition/RL-003_Go_Live_Readiness_Assessment_and_Gate_Criteria.md) was
written on **2026-08-19, concurrently with this document**, and holds the gate. **This section
supplies the people-readiness half that `RL-003` consumes, and claims no gate authority of its
own** (`CH-001-D-04`). The seven criteria in §7.2 are offered to `RL-003` for adoption; where they
and `RL-003` differ, **`RL-003` governs the gate and this document governs the people evidence**.
Reconciliation is `OCM-Q-09`.

### 7.1 The readiness instrument

| Element | Value |
|---|---|
| Unit of assessment | **One site, decomposed by role** |
| Frequency | At **T−4 weeks** (`06-01` §6 site readiness assessment), re-tested at **T−1 week** |
| Assessor | Branch manager proposes; **Change Lead confirms**; Operations Director arbitrates |
| Instrument | `CM-012` branch readiness checklist, extended by §7.2 |
| Output | `Ready` · `Ready with named exceptions` · **`Not ready`** |
| **Escalation** | A site not confirmed within 48 hours of the deadline escalates to the Operations Director (`CM-002` §4.8) |

### 7.2 The people-readiness criteria

**All seven must be met.** `OCM-21`: a criterion may be waived only by the Operations Director,
only in writing, and only with the compensating control named.

| # | Criterion | Evidence | Source |
|:--:|---|---|---|
| **PR-1** | **Champion and deputy confirmed, trained and published at the site** | Site notice; `TR-023` completion recorded in `M22` | `CNC-14` |
| **PR-2** | **Layer 1 universal core complete for every person at the site** | `M22` completion record | `CU-03` |
| **PR-3** | **Role pack complete and assessed for every person in a role going live** | `M22` assessment record | `CU-05`, `LS-14` |
| **PR-4** | Change impact statement issued in Bengali for every affected role at the site | Issue log; `CM-018` | `OCM-05`, `OCM-33` |
| **PR-5** | The site has confirmed **who answers a question on day one**, in the working language | `CM-012`; the champion, the deputy and the escalation route | `NW-10` |
| **PR-6** | **Data owner has signed the site's legacy data preparation** | `MG-004` reconciliation record | `06-01` §6, T−3 weeks |
| **PR-7** | The site has **no open Severe-class impact with no mitigation** | §4.3 assessment plus the §4.5 modifier | `OCM-08` |

> **`OCM-22` — PR-2 and PR-3 are access preconditions, not readiness preferences.** `CU-03` and
> `CU-05` are Class `H` hard rules and `BRU-LMS-01` restricts affected work types when mandatory
> training is overdue. **`AUDIT-009` `TR-03` records that whether `M29` can enforce this from an
> `M22` competence signal is unconfirmed.** If it cannot, PR-2 and PR-3 are manual controls across
> 752–1,428 people and nine waves, and §10.5 says what that means.

### 7.3 Readiness reporting

| Report | Audience | Cadence | Content |
|---|---|---|---|
| Site readiness board | Operations Director, Change Lead | Weekly from T−6 weeks | 51+ sites × 7 criteria, **worst first** (`EP-06`) |
| Wave people-readiness summary | Steering Committee | At the gate | Aggregate, plus every `Not ready` and every waiver with its compensating control |
| Role readiness | Business owner | Weekly in wave | `M22` completion and assessment by role |

---

## 8. Change Saturation

**`OCM-23`: the programme measures how much change each population is absorbing at once, and stops
adding when the limit is reached.** `RSK-003` — programme fatigue over 36 months — is rated High
and its mitigation is *"visible wave-by-wave value delivery; celebrate gates; rotate team
assignments"*. That treats the delivery team. **It does not treat the 752–1,428 people receiving
nine waves of change.**

### 8.1 The saturation model

| Load type | Unit | Limit per population per quarter | Source |
|---|---|---:|---|
| **Formal learning** | Learner-hours per person | **8 h**, beyond which absorption falls and absence rises | `CH-002` §4; declared planning assumption, not a measured figure |
| **Go-live events** | Cutovers affecting the same person | **1** | `06-01` §6 — a site cannot parallel-run two processes |
| **New systems of record** | Distinct portals the person must adopt | **2** | `04-00` |
| **Communications** | Programme messages per audience per week | **2** | `CA-10` |
| **Process re-issues** | `SP-*` SOPs changing for the same role | **3** | `SP` register |

### 8.2 Where the model bites

Derived from the wave assignments in `TR-002` §5 and `06-01` §3, counted 2026-08-19:

| Population | Waves in which they take change | Peak quarter | Saturation position |
|---|---|---|---|
| **Branch counter staff (`R08`, `R18`, `R29`)** | W1 (system), W2 (customer portal + van-stock recall), W3 (finance controls), W5 (all-centre) | **W2** | **Over.** Three of the five load types breach simultaneously |
| **Technicians (`R10`–`R12`)** | W2 (`P02`), W3 (parts and movement), W5 (competence and MSP), W6 (new lines) | **W2** | **Over.** A Severe-class change plus a new device plus a new language of record |
| **Finance (`R26`–`R29`)** | W1 (core), W3 (money and documents — the heaviest), W4 (billing), W5 (payroll) | **W3** | **At the limit**, and W3 contains a month-end close |
| Branch managers (`R06`) | W1–W5 continuously | W1–W2 | **Over** — they are simultaneously learners, sponsors and champion-releasers |
| Contact centre (`R34`, `R35`) | W4 | W4 | Within |
| HR (`R30`, `R31`) | W5 | W5 | Within — but **payroll has zero tolerance**; `06-01` §6 requires two parallel pay cycles |

> **`OCM-24` — three populations are over-saturated at W2 and this plan does not have the authority
> to fix it.** The remedies are all outside change management: re-sequence a wave, extend a
> parallel-run period, or reduce the number of portals a population must adopt at once. **The
> saturation position is therefore reported to the Steering Committee at each gate as an input to
> the Go/No-Go**, and `RSK-037` (wave capacity infeasibility, `GV-005` §4.2, **Critical**) is the
> risk it feeds. This plan's obligation is to make the load visible before the gate, not to absorb
> it silently afterwards.

### 8.3 The quiet periods that are not negotiable

Inherited from `CA-12`, `CA-13` and `CA-14`, and applied here to **change activity**, not only to
communication:

| Window | Prohibition | Basis |
|---|---|---|
| Ramadan; Eid-ul-Fitr and Eid-ul-Adha peak | **No go-live, no wave launch, no training cohort** | `ASM-16`, `CA-12` |
| Month-end: last 3 and first 5 working days | No change activity for finance populations | `CA-13` |
| Payroll week | No activity touching pay, incentives or recognition, for any population | `CA-14` |
| A site's own hypercare period | No campaign, no new training, no second cutover | `UP-15` |

---

## 9. Risk Treatment — The Five Adoption Risks

**`OCM-25`: every adoption risk in `00-04` §1.2 has a treatment in this plan with an owner, a
date, an entry condition and an exit condition — or it is declared untreated and escalated.**

### 9.1 Treatment summary

| Risk | Rating | Treatment here | Owner | Funded? |
|---|:--:|---|---|:--:|
| `RSK-001` Super-user availability | **Critical** | [`CH-005`](CH-005_Super_User_and_Champion_Network_Charter.md) — the release instrument | CEO | ⬜ **No** |
| `RSK-008` Technician rejection | **Critical** | §9.2 field pilot + §9.2.4 the W1–W5 recognition substitute | Ops Director | ⬜ **No** |
| `RSK-009` Counter-staff resistance | High | §9.3 | Ops Director | ⬜ No |
| `RSK-010` Seller adoption | High | `CH-004` §6 | CCO | ⬜ No |
| `RSK-012` Management reversion | High | §9.4 | CEO | ➖ n/a — the treatment is a withdrawal, not a spend |

> **Five treatments, zero funded lines.** `GV-007` §8.1 lists ten squads; none is change or
> training. §10.3 states the consequence.

### 9.2 `RSK-008` — the field pilot

`GV-005` §4.2: *"Design mitigations specified; **no pilot scheduled**."* This is the schedule.

**9.2.1 Purpose.** Not to test the software — `QA-002` does that. To answer one question:
**does a respected senior technician, on a real job, in Bengali, complete the task faster on `P02`
than on paper?** `GV-005` names the trigger to watch as *"field-pilot task completion slower than
paper"*, which presupposes a pilot that measures it.

**9.2.2 Design.**

| Element | Specification |
|---|---|
| Participants | **8–12 `R10` Senior Technicians**, selected for standing among peers, not for enthusiasm (`CNC-05`) |
| Sites | 3 Dhaka centres + **1 district centre with sub-threshold connectivity** |
| Duration | **4 weeks**, spanning at least one full week of offline operation |
| Timing | **W2 minus 8 weeks** — the pilot must complete before the wave that carries the risk |
| Measured | Task completion time against the paper baseline; offline sync failures; battery life over a shift; error rate; **and each technician's own stated position at week 1 and week 4** |
| Baseline | **Captured before the pilot** on the paper process. `UP-02`: no baseline, no claim |
| Exit — pass | Median completion time **≤ paper**; zero data-loss events over a 24-hour offline period (`G2-02`); **≥ 75% of participants state they would use it** |
| **Exit — fail** | **The wave does not proceed to full rollout.** `06-01` §9 already provides *"pause rollout, diagnose, remediate, re-pilot"* |
| Reporting | To the Steering Committee, with the participants' own words unedited |

**9.2.3 Why the participants must be senior.** `00-04`'s mitigation says *"respected senior
technicians"* and it is precise. A junior technician's endorsement carries no weight with the
population; a senior technician's rejection is fatal, and it is better discovered in a pilot of ten
than in a rollout of four hundred.

**9.2.4 The W1–W5 recognition gap — `AUDIT-019` `CM-06`.**

`RSK-008`'s named mitigation includes *"earnings and incentive visibility as an immediate personal
benefit."* `M57` (incentive engine and scorecard) and `M21` (HR / salary of record) both arrive at
**W5**. `P02` and the risk arrive at **W2**. `BRU-PIC-01` blocks any calculation until a scheme
version is approved by the HR Director and CFO.

**The mitigation is unavailable for three waves after the risk arrives.** `AUDIT-019` records this
as the twenty-first instance of the wave-sequencing defect, and the first in which the late
artefact is a Critical-risk mitigation.

| Option | What it delivers | What it requires |
|:--:|---|---|
| **A** | A **minimum scorecard-visibility capability at W2** — jobs completed, first-time-fix, and the technician's own trend, with **no earnings figure and no peer comparison** | An `M57` slice at W2 and a `GV-003` `D-nnn`. Scheme approval under `BRU-PIC-01` is **not** required, because no incentive is calculated |
| **B** | Accept the gap and **name the substitute**: `CM-017` §4.6 named recognition and §4.5 team comparison, which are the only surfaces available — and **have no budget** | A recorded Steering decision naming what replaces the mitigation for three waves |
| C | Do nothing | The Critical risk runs untreated for three waves. **Not offered as an option** |

> **`OCM-26` — option A or option B is a decision, and a decision is not a default.** This plan
> recommends **A**, on the ground that the risk is Critical and the mitigation was named by the
> risk register itself. The decision belongs to the HR Director with the CFO and the PMO —
> `OCM-Q-03`.

### 9.3 `RSK-009` — counter staff

| Element | Treatment |
|---|---|
| Diagnosis (§4.4) | **Ability**, not Belief. The `G1-03` bar is 3-minute intake while learning, in front of a queue |
| Treatment | Measured intake time published **as the product's commitment, not the agent's target** (`LS-06` — the four-hour and three-minute targets are joint L&D/product commitments); floor-walking through hypercare; job aids at the counter |
| `00-04`'s own mitigation | *"Involve resistors in design and UAT"* — operationalised in `CH-005` §4.3's selection rule: **a sceptic who engages is preferred to an enthusiast who does not listen** |
| Trigger to watch | Intake time at a site not falling below the paper baseline **by the end of hypercare** |
| Escalation | A product finding to the portal squad (`UP-03` question 3), **not** a further training cycle |

### 9.4 `RSK-012` — management reversion

| Element | Treatment |
|---|---|
| Diagnosis | **Reinforcement.** Capability exists; the old artefact is more comfortable |
| Treatment | **Withdraw the source data for manual packs** — `00-04`'s own mitigation, and the strongest internal adoption lever available (`UP-08`) |
| **Precondition** | `UP-08`: the alternative is withdrawn **only after the replacement is proven**. Withdrawal before capability is coercion and produces shadow spreadsheets |
| Sequence | W4 `G4-09` dashboard criterion met → 4 weeks parallel → source data withdrawn → decisions required to cite the dashboard |
| Owner | CEO (`00-04` names them), executed by the Operations Director |

### 9.5 Sustainment and the handover out of the programme

ACMP process group 5 — *complete the change management effort*. **`OCM-27`: the change effort ends
at a named handover, not by the programme finishing.**

| Element | Requirement |
|---|---|
| Trigger | Wave gate passed **and** hypercare exited **and** `CH-004`'s adoption measure held for four weeks |
| Receiving function | Line management, with L&D for refresh and `SV-005` for support — **`SV-005` is ⛔ unwritten**, `OCM-Q-07` |
| Transferred | The champion network (to Operations), adoption reporting (to the PMO's standing pack), refresher scheduling (to L&D), the objection log (to `OP-003` support themes) |
| Knowledge | ISO 30401:2018 + Amd 1:2022 + Amd 2:2024 §4.4 — what the network learned is captured in `KB-*`, not in the change team's heads |
| Not transferred | Anything with an open `Interest` objection. **It goes back to the Steering Committee** |

### 9.6 The `R13` decision

**`OCM-28`: a Severe-class population may not go live on an interim training route without a
knowing exception with an end date.** `R13` Remote Support Engineer — 15–40 people, privileged
access to customers' infrastructure, no course pack, routed to `TR-021` plus a 6-hour MSP delta.

| Element | Requirement |
|---|---|
| Decision | A dedicated pack, or the interim route accepted as a **knowing exception with an end date** |
| Decision owner | CTO with the Training Lead |
| **Needed by** | **Before the first MSP contract goes live** — which `KB-007` `O-01` warns may be earlier than W4 |
| If interim | The exception is recorded in `GV-003`; the delta is extended to cover `KB-007` §5.1's destructive-action cases; and a named senior engineer supervises every first engagement |

---

## 10. The Change Organisation

### 10.1 Roles

| Role | Accountable for | Held by |
|---|---|---|
| **Change Lead** | This plan, `CH-003`, `CH-004`, `CH-005`, the objection log, the champion forum | **Nobody.** `AUDIT-019` `R-11`: twelve of eighteen `CM` files name a role nobody holds as their owner |
| Training Lead | `CH-002`, curriculum, delivery, certification | Nobody — `TR-001` `O-04` records that **no trainer establishment exists** |
| Change & Training Lead (programme line) | The 0.5–1.0 FTE line in `06-01` §4 — **one post for two functions** | Unfilled |
| Communications owner | `CM-*` production and translation scheduling | Content Design (content only) |
| Executive sponsors | §5.2 | Appointed by post, not by name |
| Branch managers | Site sponsorship, champion release, readiness | 51+, in post |
| Champions and super-users | `CH-005` | **Not selected** |

### 10.2 RACI for the change deliverables

| Deliverable | R | A | C | I |
|---|---|---|---|---|
| Change impact assessments (38 + site annexes) | Change Lead | Operations Director | Business owners, branch managers | Steering |
| Sponsorship roadmap execution | Sponsors | **CEO** | Change Lead | All staff |
| Objection log and classification | Change Lead | Change Lead | Champions, Support Lead | Steering monthly |
| **`Interest` escalations** | Change Lead | **Steering Committee** | CFO, HR Director | Affected population |
| Site people-readiness | Branch manager | **Operations Director** | Change Lead, L&D | Steering at gate |
| Saturation reporting | Change Lead | PMO | Business owners | Steering at gate |
| Field pilot (`RSK-008`) | Ops Director | **CEO** | CTO, L&D, technicians | Steering |
| Champion release letters | Branch managers | **CEO** | HR Director | Champions |

### 10.3 The resource position, stated plainly

**`OCM-29`: an activity with no funded owner is recorded as unfunded, in the plan, at the point it
is commissioned.**

| Activity | Effort | In `GV-007`? | Funded? |
|---|---|:--:|:--:|
| 38 change impact statements + site annexes | **110–165 person-days** (`CM-018` §4.7 + §4.7 above) | ✘ | ✘ |
| Change Lead | 1.0 FTE × 36 months | ✘ — `06-01` §4 has 0.5–1.0 FTE for a **combined** "Change & Training Lead" | ✘ |
| Training delivery | **380–525 trainer-days** (`CH-002` §6.3) | ✘ | ✘ |
| Champion released time | **51+ × 4 h/week across W1–W5** — `CH-005` §5 | ✘ | ✘ |
| Champion backfill | Undetermined — the decision does not exist | ✘ | ✘ |
| Super-user released time | **40–60 people × 30% during UAT** | ✘ | ✘ |
| **Learner time** | **12,306–21,759 learner-hours = 308–544 person-weeks** (`CH-002` §4.4) | ✘ | ✘ |
| Field pilot | 4 weeks × 8–12 technicians, plus measurement | ✘ | ✘ |
| Bengali translation of change material | `AUDIT-019` `CM-11`: **zero of twelve** bilingual `CM` files has a counterpart on disk | ✘ | ✘ |

> **This table is the plan's most important output.** `AUDIT-009` `R-07` states it exactly:
> *"the delivery model currently rests on people who have not been asked."* `GV-007` §8.1 allocates
> **352 PW to an "Engineering Definition" squad the programme does not have**, and correctly calls
> that out as a trade-off requiring a decision. The change and training establishment is the same
> class of omission and is called out nowhere. Escalated as `OCM-Q-01` and `OCM-Q-08`, and to
> `GV-005` as a new risk at issue.

### 10.4 Interface with `GV-003` change control

**`OCM-30`: an approved scope change is a change-impact event and re-opens the assessments it
touches.**

| `GV-003` event | Consequence here |
|---|---|
| `CR-nnn` approved altering a role's function | The role's `CM-018` statement is re-issued; impact re-scored (§4.1) |
| Descope decision | `CM-005` `M1` re-issued; statements re-issued for affected roles (`CA-18`) |
| Wave re-sequenced | **Saturation model re-run** (§8.2); readiness dates re-anchored to the gate (`CA-02`) |
| A `D-nnn` closing an `Interest` objection | Recorded in the objection log with the detriment and the compensating action |

> `GV-003` §7.2 records that **the change log is empty while scope has tripled twice**, and
> `RSK-040` records that the programme has taken **no recorded decision in five months** — 23 open,
> 1 escalated, 0 decided. **Eight of this plan's dependencies are open decisions.** A change plan
> whose escalation route has never produced a decision is a plan with an untested control, and that
> is stated here rather than assumed away.

### 10.5 If the competence gate cannot be automated

`AUDIT-009` `TR-03`: whether `M29` can gate production access on an `M22` competence signal is
unconfirmed, and four files in two categories state the rule as though it can.

| If | Then |
|---|---|
| The integration exists | `PR-2`/`PR-3` are automated preconditions; no manual control is needed |
| **The integration does not exist** | `CU-03`, `CU-05`, `LS-14`, `QB-27` and `PK-11` must be **restated as manual controls** with a named operator per site, a sampling regime and an audit trail — across **752–1,428 users and nine waves** |

> **`OCM-31` — a manual access control at that scale is not operated; it is documented and then
> bypassed under delivery pressure.** If the answer is "no integration", this plan requires the five
> rules to be re-expressed honestly and the residual risk recorded in `GV-005`, rather than left as
> automated-sounding rules nobody enforces. Confirmation is `AUDIT-009` `R-02`, owned by the CTO
> with the Security Lead, needed by W1.

---

## 11. Governing Rules

| # | Rule | Class |
|---|---|:--:|
| `OCM-01` | Every standard cited in this category carries an edition and a verification date | **H** |
| `OCM-02` | A change document enumerates every category it cites at the moment of authoring and records the timestamp; the register's status table is not a source for what exists | **H** |
| `OCM-03` | The magnitude of the change is stated, counted, before the plan for it | **H** |
| `OCM-04` | An adoption risk with a specified mitigation and no scheduled activity is **untreated** | **H** |
| `OCM-05` | Every change impact statement declares what is unaffected, and the declaration is verified before issue | **H** |
| `OCM-06` | Change impact is assessed at role × site, never per programme and never per role alone | **H** |
| `OCM-07` | Every impact score names its evidence in the cell | **H** |
| `OCM-08` | A Severe classification obliges the plan: a sponsor act, a pilot, and a role-specific `RL-003` criterion | **H** |
| `OCM-09` | A Severe-class population is not rolled out on an interim training route | **H** |
| `OCM-10` | The missing ADKAR element is diagnosed before an intervention is chosen | **H** |
| `OCM-11` | A role's impact class is modified by site, and the modifier is recorded | **H** |
| `OCM-12` | Every wave is registered as an ISO 9001 clause 6.3 planned change, with all four elements answered before the gate | **H** |
| `OCM-13` | An impact assessment carries its sources' enumeration timestamp and expires twelve weeks after it | **H** |
| `OCM-14` | Sponsorship is a set of named, dated, observable acts by named people | **H** |
| `OCM-15` | The branch manager is a sponsor, not a recipient | **H** |
| `OCM-16` | A sponsor is briefed on the questions their population will ask, before they appear | **H** |
| `OCM-17` | This plan defines the response to resistance; `CM-002` `SK-15` defines the classification and is not restated | **H** |
| `OCM-18` | An `Interest` objection escalates to the Steering Committee with the quantified detriment; it is never answered with better messaging | **H** |
| `OCM-19` | Where a confirmed detriment stands, the position is stated honestly and the consequence is monitored for two waves | **H** |
| `OCM-20` | Readiness is measured per site and per role against a published bar, by someone with authority to say "not ready" | **H** |
| `OCM-21` | A people-readiness criterion is waived only by the Operations Director, in writing, with the compensating control named | **A** |
| `OCM-22` | `PR-2` and `PR-3` are access preconditions under `CU-03`/`CU-05`, not readiness preferences | **H** |
| `OCM-23` | Change saturation is measured per population per quarter and reported at every gate | **H** |
| `OCM-24` | An over-saturated population is reported to the Steering Committee before the gate, not absorbed after it | **H** |
| `OCM-25` | Every adoption risk has a treatment with an owner, a date, an entry and an exit condition — or is declared untreated and escalated | **H** |
| `OCM-26` | The W1–W5 recognition substitute is a recorded decision, never a default | **H** |
| `OCM-27` | The change effort ends at a named handover with a receiving function, not when the programme finishes | **H** |
| `OCM-28` | An interim training route for a Severe population requires a knowing exception with an end date | **A** |
| `OCM-29` | An activity with no funded owner is recorded as unfunded, in the plan, when it is commissioned | **H** |
| `OCM-30` | An approved scope change re-opens the impact assessments it touches and re-runs the saturation model | **H** |
| `OCM-31` | If the competence gate cannot be automated, the five dependent rules are restated as manual controls with a named operator and a sampling regime | **H** |
| `OCM-32` | No change activity is scheduled into a quiet period listed in §8.3 | **H** |
| `OCM-33` | Change material reaching field, branch, workshop, store or rider audiences is Bengali-first; English-only does not count as having communicated (`SK-08`) | **H** |

> Class: **H** hard block · **A** approved override · **S** soft warning · **C** computed — the
> same scale as `05-05` §1 and `TR-001` §4.11.

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `OCM-Q-01` | **Who is the Change Lead, and who is the Training Lead?** Twelve `CM` files and this plan name a post nobody holds | **CEO with HR Director** | **W0** | Everything in this category. `AUDIT-019` `R-11` |
| `OCM-Q-02` | The role register's upper bounds sum to **1,368** against a workforce described as 500–900. Which is the planning population? | HR Director with MDM | **W1 − 8 weeks** | Cohort count, trainer days, translation volume, `CH-002` §4 |
| `OCM-Q-03` | Option A or option B for the W1–W5 `RSK-008` recognition gap (§9.2.4)? | HR Director with CFO and PMO | **W2 − 12 weeks** | The Critical risk's own mitigation |
| `OCM-Q-04` | Who owns *"involve branch managers in KPI design"* — `00-04`'s own `RSK-009`/`RSK-012` mitigation — and by when? | Operations Director | W1 − 6 weeks | The Desire of 51+ sponsors |
| `OCM-Q-05` | What is the company's job-security position (`CON-10`)? | **CEO** | **W0 — before the first communication** | `CM-011` `OB-01`; every town hall; `G2` factual review |
| `OCM-Q-06` | What is the opening-variance amnesty position at cutover? | CFO with Operations Director | W1 − 6 weeks | `CM-011` `OB-05`; counter and store readiness |
| `OCM-Q-07` | `SV-005` Hypercare & Transition-to-Support Plan is ⛔ unwritten. Which function receives the change effort at §9.5? | Support Lead with CTO | W1 | ACMP process group 5 |
| `OCM-Q-08` | Is there a funded change and training establishment at all, or is §10.3 the answer? | **CFO with the Steering Committee** | **W0** | Every activity this plan commissions |
| `OCM-Q-09` | **Reconcile §7.2's seven people-readiness criteria with the gate criteria in `RL-003`**, issued 2026-08-19 concurrently with this document. Where they differ, `RL-003` governs the gate and this document governs the people evidence — but the difference must be found, not assumed absent | Change Lead with the PMO | **W1 − 4 weeks** | The site readiness board; `PR-1`…`PR-7`; audit finding `CHA-12` |

> An open question with no owner and no needed-by date is not an open question — it is an
> unrecorded risk. All eight are escalated to `GV-005` RAID at issue.

---

## 13. Decisions Recorded

Local decisions of this document. Identifiers take the form `CH-001-D-nn` — **never the bare
`D-nn`**, which is the programme decision space allocated only by `GV-003` (rule `DL-06`).

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `CH-001-D-01` | Which change-management standard governs | ACMP Standard v1 · **ACMP Standard v2** · Prosci methodology alone · no standard | **ACMP Standard v2 (26 Aug 2025)**, with ADKAR as the individual-outcome model | v2 is current from 26 August 2025 and adds the resource strategy (5.2.1) and readiness plan (5.3.1.5) this programme most lacks. Prosci is a methodology, not a standard, and is used for what it is good at | §2.1 conformance is testable; the CCMP examination transition on 1 April 2026 does not affect conformance |
| `CH-001-D-02` | Kotter 1995 8-step, or the 8 Accelerators | 8-step (1995) · **8 Accelerators / dual operating system (2014, 2021)** | **Accelerators** | Nine overlapping waves over 36 months are not a single linear change. The champion network *is* the volunteer network of the dual operating system | The category overview's undated *"Kotter 8-step"* citation is corrected; `CHA-05` |
| `CH-001-D-03` | Impact assessment grain | Per programme · per role (`CM-018`) · **per role × site** | **Role × site**, with the §4.5 modifier | A role at a Dhaka pilot centre and at a sub-threshold-connectivity district branch face different changes. `CM-012` assesses sites without decomposing by role; `CM-018` assesses roles without varying by site | +15–25 person-days on top of `CM-018` §4.7's 95–140 |
| `CH-001-D-04` | Whether this plan claims go-live gate authority | Yes · **No** | **No** — it supplies people-readiness criteria to `RL-003` | Taken while `RL-003` was ⛔. A plan that grants itself gate authority in the absence of the document that should hold it creates a second authority to reconcile later. **`RL-003` was then issued 2026-08-19 during this document's authoring window, which vindicates the decision**: had §7 claimed the gate, there would now be two | §7 is an input, not a gate. Reconciliation with the issued `RL-003` is `OCM-Q-09` |
| `CH-001-D-05` | How to treat the `RSK-008` recognition gap | Recommend A · recommend B · present both neutrally | **Recommend A; decide at Steering** | The risk is Critical and the mitigation was named by the risk register itself. A plan that presents a Critical risk's treatment as a neutral menu has deferred rather than planned | `OCM-Q-03` carries a recommendation, and the decision remains the HR Director's and the CFO's |
| `CH-001-D-06` | Local rule prefix | `CH-nn` · **`OCM-nn`** | **`OCM-nn`**, verified zero workspace-wide | `CH-nn` is already a rule prefix in `NT-001`, `RP-007` and `OP-001`; using it would repeat `MGA-04` exactly | `CHA-02`; no `CH` document uses `CH-nn` |
| `CH-001-D-07` | Whether to restate `CM-002`'s resistance classification | Restate · **cite and extend** | **Cite and extend** (`OCM-17`) | `CP-01` prohibits authoring content in two places; `AUDIT-009` `TR-08` and `AUDIT-019` `CM-09` are both duplication findings | This plan owns the *response*; `CM-002` owns the *classification*. The boundary is stated in a table, not in prose |

---

## 14. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every activity commissioned names an owner, a date and a funding position | §9.1, §10.3 |
| `AC-02` | Every adoption risk in `00-04` §1.2 has a treatment or a declared non-treatment | §9.1 — five of five |
| `AC-03` | The impact method is applied, not merely described | §4.3 — ten populations scored, four Severe |
| `AC-04` | Every standard cited carries an edition and a verification date | §2.1 and §16 — seven standards, all dated; `verified_on: 2026-08-19` |
| `AC-05` | No figure is quoted from a register without being counted | §3.1, §4.2, §10.3 — all counted at 2026-08-19 01:20 (+06), with the reproduction command in §2.2 |
| `AC-06` | The rule prefix returned zero workspace-wide occurrences before allocation | Header note; `CHA-02` |
| `AC-07` | Every open question has an owner and a needed-by date | §12 — eight of eight |
| `AC-08` | Findings from `AUDIT-009` and `AUDIT-019` are treated, referred or declared out of scope | §2.3 |
| `AC-09` | The document declares what it does **not** own | §1.1 out-of-scope table — eight boundaries |
| `AC-10` | Approval record | ⬜ **Cannot be met.** No constituted body can approve anything until `GV-001` `CC-01` completes — `PGD-A2-25`. Recorded, not worked around |

**Definition of done.** Complete when `AC-01`–`AC-09` are met, its `PGD-000` row is updated with a
fresh enumeration timestamp, and its approver has signed. `AC-10` is blocked outside this document.

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `GV-001` Programme Charter | Sponsorship authority; `CC-01` blocks approval |
| Upstream | `GV-002` Governance, RACI & ToR | The bodies that receive escalations |
| Upstream | `GV-003` Decision Log & Change Control | Where `Interest` decisions and `CR-nnn` land |
| Upstream | `GV-004` Integrated Programme Plan | Where change activities must appear as schedule lines |
| Upstream | `GV-005` RAID Register | Risk ratings and treatment status; eight new open questions escalate here |
| Upstream | `GV-007` Estimation Model & Resource Plan | The plan that does not contain this plan's people |
| Upstream | `RQ-007` Business Process Model Repository | To-Be processes from which the D1 process impact derives |
| **Lateral** | [`CH-002`](CH-002_Training_Plan_and_Delivery_Schedule.md) | Capability treatment for every `Capability` classification |
| **Lateral** | [`CH-003`](CH-003_Stakeholder_Engagement_and_Communication_Plan.md) | Executes the engagement strategy; retires the second wave calendar |
| **Lateral** | [`CH-004`](CH-004_Adoption_Measurement_and_Reinforcement_Plan.md) | Measures whether the change landed |
| **Lateral** | [`CH-005`](CH-005_Super_User_and_Champion_Network_Charter.md) | Constitutes the delivery network |
| Downstream | [`RL-003`](../12_Release_Deployment_and_Transition/RL-003_Go_Live_Readiness_Assessment_and_Gate_Criteria.md) *(issued 2026-08-19)* | Consumes §7's people-readiness criteria; reconciliation is `OCM-Q-09` |
| Downstream | [`RL-004`](../12_Release_Deployment_and_Transition/RL-004_Rollout_and_Branch_Wave_Deployment_Plan.md) *(issued 2026-08-19)* | Per-site readiness bar includes §7.2 |
| Downstream | `SV-005` Hypercare & Transition-to-Support Plan ⛔ | Receives the §9.5 handover |
| Downstream | `BM-004` Benefits Realisation Plan ◐ | Benefit delivery depends on adoption |
| Lateral | `../../project_content/16_Change_Management_and_Comms/` | 18 `CM` files; content this plan consumes and never restates |
| Lateral | `../../project_content/08_Training_and_Enablement/` | 24 `TR` files |
| Lateral | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` §7 | The nine-row change table this plan replaces |

---

## 16. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
[`CH-002`](CH-002_Training_Plan_and_Delivery_Schedule.md) ·
[`CH-003`](CH-003_Stakeholder_Engagement_and_Communication_Plan.md) ·
[`CH-004`](CH-004_Adoption_Measurement_and_Reinforcement_Plan.md) ·
[`CH-005`](CH-005_Super_User_and_Champion_Network_Charter.md) ·
[`../00_Programme_Governance_and_Control/GV-005_RAID_Register.md`](../00_Programme_Governance_and_Control/GV-005_RAID_Register.md) ·
[`../00_Programme_Governance_and_Control/GV-007_Estimation_Model_and_Resource_Plan.md`](../00_Programme_Governance_and_Control/GV-007_Estimation_Model_and_Resource_Plan.md)

**Workspace**
[`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md`](../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md) ·
[`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md`](../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md) ·
[`../../1000fix_ERP_Module/00_Governance_and_Charter/00-04_Risks_Assumptions_Dependencies_and_Governance.md`](../../1000fix_ERP_Module/00_Governance_and_Charter/00-04_Risks_Assumptions_Dependencies_and_Governance.md) ·
[`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md`](../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md) ·
[`../../project_content/_AUDIT/AUDIT-019_Category_16_CM_Content_Audit.md`](../../project_content/_AUDIT/AUDIT-019_Category_16_CM_Content_Audit.md) ·
[`../../project_content/_AUDIT/AUDIT-009_Category_08_TR_Content_Audit.md`](../../project_content/_AUDIT/AUDIT-009_Category_08_TR_Content_Audit.md)

**External standards and sources** *(all verified 2026-08-19)*

| Source | Edition / date | Verified |
|---|---|---|
| ACMP *Standard for Change Management* | **Version 2**, released 26 August 2025; CCMP examination transitions 1 April 2026 | 2026-08-19 |
| Prosci ADKAR Model | Current published model; the 2025 peer-reviewed critique of linear application is noted in §2.1 | 2026-08-19 |
| Kotter — *Accelerate* (HBR 2012; book 2014) and *CHANGE* (2021) | 8 Accelerators; dual operating system | 2026-08-19 |
| ISO 21502:2020 | Project, programme and portfolio management — guidance on project management | 2026-08-19 |
| ISO 10018:2020 | Quality management — Guidance for people engagement. **ISO 10018:2012 is withdrawn** | 2026-08-19 |
| ISO 9001:2015 | Clause 6.3 planning of changes; clause 7.2 competence | 2026-08-19 |
| ISO 30401:2018 + **Amd 1:2022** + **Amd 2:2024** | Knowledge management systems. **ISO/DIS 30401 is in enquiry and will replace the 2018 edition** — flagged to `RR-005` | 2026-08-19 |

> Every relative path above was resolved before issue.

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Enterprise Architecture with Change Management | Initial issue. Supersedes `06-05_Change_Management_and_Training_Plan.md` (planned, never written) for the change half | ⬜ Blocked — `GV-001` `CC-01` |

---

*`CH-001` · Category 13 · 1000FiX ERP System v2.0 · CONFIDENTIAL — Internal Use Only*
