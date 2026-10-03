---
id: KB-014
title: Repair Time Standards and Labour Norms
project: 1000FiX ERP System v2.0
content_type: Knowledge article
template: TPL_Knowledge_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-16
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Operations with Finance
author: Operations with Cost Accounting and Technical Services
reviewers: [Technical Director, Finance Manager, HR Manager, Quality Manager, BI Lead, Knowledge Manager, Localisation Lead]
approver: Operations Director with Finance Manager
content_class: C
purpose: >
  The standard time for every repair action, the basis on which each was established, and the rules
  that govern how those times may be used. Capacity planning, technician incentive schemes, job
  costing and quoted turnaround all read from these norms; a norm set without a stated basis and
  without rules on its use becomes a target that distorts the behaviour it was created to measure.
traces_to: [MD-025, MD-010, MD-021, M54, M57, M55, M31, M02, M36, M61, P02, P03, P06, KB-001, KB-002, KB-004, KB-005, KB-006, KB-007, KB-012, SP-010, SP-013, RP-001]
priority: P2
wave: W5
bilingual: yes
bn_counterpart: KB-014_Repair_Time_Standards_and_Labour_Norms_BN.md
sources:
  - source: project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md — standard_minutes is a mandatory column on every resolution code and is explicitly identified as the labour norm feeding KB-014 and costing; RES-06 warns for norm review when actual time exceeds standard by more than 100%
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M54_Cost_Accounting_Budgeting_and_FPA.md — job costing and profitability by revenue stream
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M57_Performance_Incentives_and_Compensation.md — technician incentive schemes; 05-05 BRU-HRM-03 performance incentive is calculated only after the minimum monthly job threshold is met
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §5.4 FR-KMS-025 — capture prompted on repairs materially exceeding standard time; §12.1 M61 consumes duration versus standard from M01
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-004 first-time fix 70%→88%; KPI-010 walk-in intake time ~10 min → under 3 min
    verified: 2026-08-16
    class: P1
supersedes: none
review_due: 2027-02-16
---

# KB-014 — Repair Time Standards and Labour Norms

| Item | Value |
|---|---|
| Article type | **Reference** |
| Device family | All — norms are scoped by `MD-025` resolution code, which is itself family-scoped |
| Brand / model scope | Model-generation scoped where the difference is material |
| Skill level required | L1 to read a norm · Operations and Cost Accounting to set one · Operations Director with Finance Manager to approve a change |
| Offline pack member | **Yes, read-only** — a technician needs to know the expectation; see `RT-12` on how it is presented |
| Review due | 2027-02-16 |

> **Template conformance.** Reference-type article; all `TPL_Knowledge_Article.md` sections
> retained in order and answered at norm-set level. Sections 11–13 are justified additions,
> consistent with [`KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md`](KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md) §11.

---

## 1. Purpose and Scope

**`MD-025` already carries `standard_minutes` as a mandatory column on every resolution code.**
That is the number. This file is everything the number needs in order to be trustworthy: where it
came from, what it includes and excludes, who may change it, and — most importantly — **what it may
and may not be used for.**

### 1.1 The four consumers, and why they conflict

| Consumer | Uses the norm to… | Pressure it applies to the norm |
|---|---|---|
| **Capacity planning** (`M55`, `M02`) | Forecast how many technician-hours a demand profile needs | Wants norms to reflect **reality**, including the slow days |
| **Job costing** (`M54`) | Attribute labour cost to a job and measure margin by revenue stream | Wants norms to reflect **standard efficient performance** |
| **Quoting and turnaround** (`M36`, `SP-013`) | Promise the customer a date | Wants norms with enough **contingency** to be met |
| **Technician incentives** (`M57`) | Reward productivity | Applies the strongest pressure of all — **to make the norm loose** |

**These four pull in different directions, and a single number cannot satisfy all four honestly.**
That is the central design problem this file exists to solve, and §6.2 resolves it by separating
the norm from the derived figures each consumer actually uses.

**Consequence of absence (`CP-03`).** Without a stated basis and stated usage rules, the norm
becomes whatever the loudest consumer needed it to be. Incentive pressure loosens it; the loosened
norm then understates capacity, overstates job cost, and lengthens every quoted turnaround. Nobody
decides this — it happens quietly over about two review cycles.

**In scope:** the norm definition and what it includes; the basis classes and their evidence
requirements; the derived figures for each consumer; the rules governing use, especially in
incentives; the setting, review and change process; the model-generation and skill-level
adjustments; and the relationship to the `M61` capture prompt.

**Out of scope:**

| Subject | Owned by |
|---|---|
| The resolution codes themselves and the `standard_minutes` field | [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md) — **`RT-01` prohibits setting a norm anywhere but there** |
| Labour **rates**, pricing and charge-out | `MD-029` Price List and Rate Card Seed |
| Incentive scheme design, thresholds and payment | `M57` · `MD-043` · `BRU-HRM-03` |
| Rostering, shifts and attendance | `M55` · `MD-042` · `SP-022` |
| Cost accounting method and overhead absorption | `M54` |
| SLA response and resolution targets — **a different concept from a labour norm** | `MD-028` · `LG-015` |
| KPI definitions | `RP-001` |

> **The distinction most often confused.** A **labour norm** is how long the work takes. An **SLA
> target** is what the customer was promised. A 40-minute repair can sit inside a 48-hour SLA. They
> are set by different people for different reasons and `RT-13` prohibits deriving one from the
> other.

---

## 2. Safety

> ⚠ **WARNING — a time standard applied as a deadline is a safety hazard.** Technicians working
> against a clock skip isolation, skip the proving step, skip the ESD check, skip the pre-use
> instrument check, and re-charge a battery they should have isolated (hazard). Injury, device
> damage and latent failures (consequence). **`RT-09` prohibits presenting a norm to a technician
> as a countdown, and `RT-10` excludes safety steps from any pressure to compress** (avoidance).

> **NOTICE — norms and quality are linked.** `KPI-004` first-time fix rises to 88% only if
> diagnosis is done properly. A norm regime that rewards speed without measuring rework will raise
> throughput and lower first-time fix simultaneously, and the second effect is larger and slower to
> appear. §8 pairs every time measure with a quality measure for this reason.

---

## 3. Symptoms — *the signals that the norm set is failing*

| Signal | What it indicates |
|---|---|
| `RES-06` warnings firing frequently on one code | The norm is wrong for that code — actual exceeding standard by more than 100% (`MD-025`) |
| Actual times clustering **just under** the norm | **Reporting to the norm rather than to reality.** The most serious signal in this table |
| Rework rising while throughput rises | Speed being bought with quality |
| A norm unchanged since it was first set | Nobody owns it; the review process is not running |
| Wide spread between technicians on the same code | Either a competence gap (`M22`) or a norm covering work that is not one thing |
| Quoted turnaround consistently missed on one repair class | Contingency in the derived quoting figure is wrong (§6.2) |
| Capacity plans consistently short | Norms exclude real work — travel, waiting, parts, customer interaction |
| Technicians declining certain job types | The norm makes them unattractive under the incentive scheme |
| A norm set by a single observation | Basis class is `estimate` and was never upgraded (§6.3) |

**`RT-02`: clustering just under the norm is investigated as a data-integrity matter, not
celebrated as performance.** A distribution that hugs the target from below is the classic
signature of a measure being reported rather than observed.

---

## 4. Likely Causes

| # | Cause | Frequency | Confirming test |
|---:|---|---|---|
| 1 | Norm set by estimate and never validated against actuals | **Highest initially** | Basis class distribution (§6.3) |
| 2 | Norm covers a resolution code that spans genuinely different work | High | Bimodal actual-time distribution |
| 3 | Model-generation differences not reflected | High | Actuals segmented by model |
| 4 | Skill level not reflected — L1 and L3 timed identically | High | Actuals segmented by `repair_level` |
| 5 | Non-productive time included or excluded inconsistently | **High and corrosive** | §6.1 boundary test |
| 6 | Incentive pressure applied to a norm used for costing | Medium | Norm-change history vs incentive scheme changes |
| 7 | Seasonal conditions not reflected — heat, monsoon access, peak load | Medium | Actuals by month |
| 8 | Field versus bench not distinguished | Medium | Actuals by service mode (`MD-020`) |

---

## 5. Diagnostic Procedure — *how a norm is established*

| Step | Who | Action | Gate |
|---:|---|---|---|
| 1 | Operations analyst | Confirm the resolution code describes **one** kind of work; if bimodal, split the code first in `MD-025` | `RT-03` |
| 2 | Operations analyst | Define the boundary — what the norm includes and excludes (§6.1) | Boundary stated |
| 3 | Operations analyst | Gather actuals: at minimum **20 completed jobs across ≥ 3 technicians and ≥ 2 branches** | `RT-04` |
| 4 | Operations analyst | Exclude outliers with a **stated reason**, not by rule of thumb; retain the excluded set | `RT-05` |
| 5 | Operations analyst | Compute the norm as the **median of competent performance**, not the mean and not the best | `RT-06` |
| 6 | R12 / R09 | Technical review: is the time achievable **safely and to the QC standard**? | `RT-10` |
| 7 | Cost Accounting | Confirm the derived costing figure (§6.2) | — |
| 8 | Operations Director + Finance Manager | Approve | `RT-08` |
| 9 | MDM | **Set `standard_minutes` in `MD-025`** — the only place a norm is stored | `RT-01` |
| 10 | System | Publish with basis class and evidence count visible | `RT-07` |

**`RT-06` — why the median of competent performance.** The mean is dragged by the pathological job
that took four hours because a part was missing. The best time is achievable by one person on a
good day and is a target disguised as a standard. The median of competent performers is the only
figure that is simultaneously achievable, honest, and stable enough to plan with.

---

## 6. Repair Procedure — *the norm framework*

### 6.1 What a norm includes

**`RT-11`: the boundary is stated on every norm, and it is the same boundary for every norm.**

| Included in the norm | Excluded from the norm |
|---|---|
| Preparing the bench or the work area | **Travel to and from site** — planned separately (`M02`) |
| **Safety checks, isolation and proving** (`RT-10`) | Waiting for a customer to be available |
| Diagnosis for the coded fault | Waiting for parts (`SP-016` hold time) |
| The repair itself | Customer-decision time on an estimate (`SP-013`) |
| Verification and QC to the article's criterion | Queue and WIP time (`SP-010`) |
| Recording the outcome, codes and evidence | Break, meal and rest time |
| Reassembly and cosmetic completion | Rework of a previous job — **separately coded and separately measured** |
| Handover preparation | Training, meetings, administration |
| **Knowledge capture where it is a completion condition** (`RT-14`) | Non-productive time of any kind |

> **`RT-14` is deliberate and contested.** `M61` `BRU-KMS-10` can make knowledge capture a
> completion condition on complex repairs, and `FR-KMS-024` targets capture in under three minutes.
> If that three minutes sits outside the norm, capture becomes unpaid time that competes with the
> technician's incentive, and it will not happen. **Including it is the difference between a
> capture policy and a capture practice.**

### 6.2 One norm, four derived figures

**`RT-07`: the norm is a single stored value. Each consumer uses a derived figure, computed by a
declared rule, and no consumer edits the norm to suit itself.**

| Consumer | Derived figure | Rule | Owner of the rule |
|---|---|---|---|
| **Job costing** (`M54`) | The norm, unmodified | Standard efficient performance is exactly what costing needs | Finance Manager |
| **Capacity planning** (`M55`, `M02`) | Norm ÷ a declared utilisation factor | Accounts for the non-productive time excluded in §6.1 | Operations Director |
| **Quoting and turnaround** (`M36`, `SP-013`) | Norm + a declared contingency by repair class, then converted to a **calendar** promise using queue and parts lead time | A labour minute is not a calendar minute | Operations Director with Commercial |
| **Incentives** (`M57`) | **A banded expectation, never the raw norm** — see §6.4 | Removes the incentive to shave minutes | HR Director with Operations Director |

**`RT-08`: a change to the norm requires Operations Director and Finance Manager approval
together.** Either alone has an interest; together they do not share the same one.

### 6.3 Basis classes

As with `KB-008` §6.3 and `KB-011` §6.2, **confidence is stated, not implied.**

| Basis | Evidence | Displayed as | May feed incentives |
|---|---|---|:--:|
| `measured` | ≥ 20 jobs, ≥ 3 technicians, ≥ 2 branches, outliers excluded with reasons | Authoritative | ✔ |
| `derived` | Computed from a `measured` norm on a closely related code, with the relationship stated | Reliable | ✔ |
| `manufacturer` | The manufacturer's published standard repair time, cited to a `LIB-` entry | Reliable — **but validate against actuals; published times often assume a fully-equipped OEM workshop** | ✔ |
| `estimate` | Technical judgement, no actuals yet | **"Provisional — not yet validated"** | ✖ (`RT-15`) |

**`RT-15`: an `estimate`-basis norm may be used for costing and planning but never for incentive
calculation.** Paying or penalising a person against an unvalidated number is indefensible, and it
is the fastest way to lose the workforce's trust in the whole norm regime.

### 6.4 Incentive use — the rules that protect the norm

`M57` operates technician incentive schemes and `BRU-HRM-03` gates them on a minimum monthly job
threshold. The norm feeds them, and that is where the distortion risk lives.

| # | Rule | Class |
|---|---|:--:|
| **RT-16** | Incentives use a **banded** expectation — "within band", "above band" — never a minute-by-minute comparison | **H** |
| **RT-17** | **Every time-based incentive measure is paired with a quality measure** — first-time fix, rework rate, QC pass rate, customer outcome. A time measure alone is never paid | **H** |
| **RT-18** | Rework attributable to a known issue (`KB-011` `KW-17`), a faulty instrument (`KB-012` §9), an ESD-control failure (`KB-013` §13) or a parts defect (`KB-009`) is **excluded** from the technician's measure | **H** |
| **RT-19** | Complex, novel and L3 work is not penalised for exceeding the norm; `M61` `FR-KMS-025` **prompts knowledge capture** on exactly those jobs, and a scheme that penalises them suppresses the capture | **H** |
| **RT-20** | Safety steps are never a source of time saving (`RT-10`); a job completed under norm with a skipped safety step is a **failed** job | **H** |
| **RT-21** | Norm changes take effect at a period boundary, never mid-period, and are communicated before they apply | **C** |
| **RT-22** | A norm may not be tightened on the evidence of the fastest performers alone (`RT-06`) | **H** |

> **`RT-19` deserves emphasis because it connects two files that would otherwise never meet.**
> `M61`'s entire capture strategy rests on prompting technicians at the moment they finish
> something hard and slow. If the incentive scheme penalises the slow job, the technician's
> rational response is to avoid hard work and decline the capture prompt — and the company loses
> exactly the expertise `M61` was created to preserve.

### 6.5 Adjustments

| Adjustment | When applied | Set by |
|---|---|---|
| **Model generation** | Where disassembly, adhesive, fastener count or access differs materially | Operations analyst with R12 |
| **Skill level** | An L1-competent task performed by an L1; L3 work timed against L3 norms | Operations analyst |
| **Service mode** (`MD-020`) | Field, bench, workshop and remote differ genuinely for the same repair | Operations analyst |
| **First-of-model** | The first repairs on a newly serviced model legitimately take longer | Automatic; excluded from norm evidence |
| **Seasonal** | Where heat, access or peak load materially changes achievable time | Operations Director, declared and time-boxed |
| **Site** | Where a branch's equipment or layout materially differs — **and this is a facilities finding, not a permanent norm** | Operations Director; must be reviewed |

**`RT-23`: every adjustment is declared, time-boxed where temporary, and visible.** An undeclared
site adjustment is how one branch quietly acquires a different standard from the other fifty.

### 6.6 Review

| Trigger | Action |
|---|---|
| Scheduled | **Annual** for `measured` norms; **6-monthly** for `estimate` and `derived` |
| `RES-06` warnings above threshold on a code | Out-of-cycle review of that norm |
| Distribution clustering just under the norm (`RT-02`) | Data-integrity investigation **before** any norm change |
| A new model generation enters service | Adjustment review |
| A procedure changes in `KB-004`…`KB-007` | The norm follows the procedure — **`RT-24`** |
| A tool or method changes (`KB-012`) | Review |
| A brand bulletin changes a procedure (`KB-010`) | Review at the bulletin's severity |
| Incentive scheme change | **Review the norms before the scheme changes, not after** |

---

## 7. Parts

Parts affect norms in two ways, and confusing them corrupts both measures:

| Effect | Handling |
|---|---|
| **Part availability** | Waiting for a part is **excluded** from the norm (§6.1). It belongs to `SP-016` and `M43`, and it is where turnaround is actually lost |
| **Part type** | A `compatible` or `refurbished` part may take longer to fit or require additional calibration (`KB-009` §6.2). Where the difference is material, it is a declared adjustment, not silent variance |
| Serialised parts | Serial capture is included in the norm (§6.1 recording) |
| Consumables | Included |

---

## 8. Verification and QC

**`RT-17` in measurement form: every time measure below is paired with a quality measure.**

| Measure | Paired quality measure | Frequency | Target |
|---|---|---|---|
| Actual vs norm by resolution code | Rework rate on that code | Monthly | Actual converging on norm **without rework rising** |
| Actual vs norm by technician | First-time fix by technician (`KPI-004`) | Monthly | Both improving |
| Actual vs norm by branch | QC pass rate at the `SP-010` gate | Monthly | Both improving |
| **Distribution shape per code** | — | Monthly | **No clustering just under the norm (`RT-02`)** |
| `RES-06` warning rate | — | Monthly | Falling as norms are validated |
| Basis-class distribution | — | Quarterly | `estimate` share **falling**; `measured` share rising |
| Norms unchanged for over 24 months | — | Quarterly | Zero |
| Capture-prompt acceptance on over-norm jobs | — | Monthly | **Rising — the `RT-19` test** |
| Quoted turnaround met | Customer complaint rate on turnaround | Monthly | Rising |
| Capacity plan accuracy | Overtime and unfilled demand | Monthly | Converging |
| Norm changes with dual approval recorded | — | Per change | 100% (`RT-08`) |
| Adjustments declared and in date | — | Quarterly | 100% (`RT-23`) |

---

## 9. Resolution Coding

The norm **lives on** the resolution code. The relationship is one-to-one and is owned by `MD-025`:

| Element | Owner | Note |
|---|---|---|
| `resolution_code` | `MD-025` | The unit a norm attaches to |
| `standard_minutes` | `MD-025` | **The stored norm.** `RT-01`: set nowhere else |
| `repair_level` | `MD-025` | Skill-level adjustment input (§6.5) |
| `RES-06` | `MD-025` | Soft warning at actual > 200% of standard — the review trigger |
| Basis class, evidence count, adjustments | **This file's register** (§11) | The metadata `MD-025` does not carry |

**`RT-03`: where actual times for one code are genuinely bimodal, the code is split in `MD-025`
before the norm is set.** A norm averaging two different jobs is wrong for both.

---

## 10. Escalation

| Escalate when | To | With what evidence |
|---|---|---|
| Actual times cluster just under a norm (`RT-02`) | **BI Lead + Operations Director** — data-integrity investigation | Distribution |
| A technician reports a norm as unachievable safely | **Operations Director + HSE Lead**; `RT-10`/`RT-20` apply | The steps that cannot be compressed |
| Rework rises as throughput rises | Quality Manager + Operations Director | Paired measures |
| A norm change is proposed by one function alone | Refuse; `RT-08` requires both approvals | The proposal |
| An `estimate`-basis norm is found feeding incentives | **HR Director + Operations Director — suspend that element** (`RT-15`) | Scheme configuration |
| Capture-prompt acceptance falls on over-norm jobs | Quality Manager + Operations Director; the scheme is suppressing capture (`RT-19`) | Acceptance trend |
| A branch is persistently outside norm across many codes | Operations Director — **investigate equipment, layout and competence before the people** | Segmented actuals |
| A norm has not been reviewed in 24 months | Operations analyst; out-of-cycle review | Review dates |
| Quoted turnaround is systematically missed | Operations Director with Commercial; the contingency rule is wrong (§6.2) | Turnaround performance |
| Norms are being used to set SLA targets | **Refuse — `RT-13`.** Escalate to Operations Director | The proposal |

---

## 11. Norm Register Structure *(addition — justified: `MD-025` stores the number; the metadata that makes it trustworthy needs a defined home and this file owns it)*

| Column | Type | Req | Notes |
|---|---|:--:|---|
| `norm_code` | `RTN-nnnnn` | ✔ | Permanent |
| `resolution_code` | fk → `MD-025` | ✔ | **One norm per resolution code** |
| `standard_minutes_ref` | — | ✔ | Read from `MD-025`; **not duplicated here** (`RT-01`, `CP-01`) |
| `basis` | enum | ✔ | §6.3 |
| `evidence_job_count`, `evidence_technician_count`, `evidence_branch_count` | int | ✔ | `RT-04` thresholds |
| `evidence_period_from` / `_to` | date | ✔ | |
| `outliers_excluded`, `exclusion_reason` | int / text | ✔ | `RT-05` — reasons stated, set retained |
| `boundary_note` | text | ✔ | §6.1 confirmation |
| `adjustments` | structured | | §6.5, each with expiry where temporary |
| `costing_figure`, `capacity_factor`, `quoting_contingency`, `incentive_band` | | ✔ | §6.2 derived figures and their rules |
| `technical_reviewer`, `approved_by_ops`, `approved_by_finance` | fk | ✔ | `RT-08` |
| `last_reviewed`, `next_review_due` | date | ✔ | §6.6 |
| `res06_warning_rate` | computed | | Review trigger |
| `distribution_shape_flag` | computed | | `RT-02` |
| `status` | enum | ✔ | active / provisional / under_review / superseded |

---

## 12. Coverage and Rollout *(addition — justified: consistent with every other `KB` register; the norm set has to be built, and how it is built determines whether it is trusted)*

| Phase | Content | Basis | When |
|---|---|---|---|
| **1 — Seed** | Every `MD-025` code carries an `estimate` norm so that costing and planning can function | `estimate` | **W1, with `MD-025`** |
| 2 — Validate high-volume | The top 50 codes by volume moved to `measured` | `measured` | W2–W3, once actuals exist |
| 3 — Validate the rest | Remaining codes moved to `measured` or `derived` | `measured` / `derived` | W4–W5 |
| 4 — Incentive-ready | **Only `measured` and `derived` codes feed incentives** (`RT-15`) | — | **W5, aligned to `M57`** |
| 5 — Steady state | Annual review; out-of-cycle on triggers | — | W6+ |

| Measure | Target |
|---|---|
| `MD-025` codes with a norm | 100% from W1 — an `estimate` is better than a blank |
| Codes at `measured` basis | Rising; **≥ 80% of volume before incentives go live** |
| Codes feeding incentives that are `estimate`-basis | **Zero** (`RT-15`) |
| Codes unreviewed beyond 24 months | Zero |

> **The rollout order is the point.** Seeding every code with an honest `estimate` on day one lets
> costing and capacity planning work immediately, while `RT-15` keeps those provisional numbers out
> of anybody's pay. Attempting the reverse — waiting for measured norms before doing anything —
> leaves `M54` unable to cost a job through the whole of W1 to W4.

---

## 13. Related Documents *(addition — justified: category convention)*

| Document | Relationship |
|---|---|
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md) | **Stores `standard_minutes` and names `KB-014` as its consumer**; `RES-06` is the review trigger |
| [`../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-010_Competency_and_Skill_Taxonomy.md`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-010_Competency_and_Skill_Taxonomy.md) | Skill-level adjustment |
| [`KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md`](KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md) · [`KB-005_Troubleshooting_Guide_Set_Home_Appliance.md`](KB-005_Troubleshooting_Guide_Set_Home_Appliance.md) · [`KB-006_Troubleshooting_Guide_Set_Mobile_and_Tablet.md`](KB-006_Troubleshooting_Guide_Set_Mobile_and_Tablet.md) · [`KB-007_Troubleshooting_Guide_Set_Server_Network_and_CCTV.md`](KB-007_Troubleshooting_Guide_Set_Server_Network_and_CCTV.md) | The procedures being timed; `RT-24` — the norm follows the procedure |
| [`KB-009_Parts_Compatibility_and_Substitution_Notes.md`](KB-009_Parts_Compatibility_and_Substitution_Notes.md) | Part-type effects on time |
| [`KB-011_Known_Issue_and_Workaround_Register.md`](KB-011_Known_Issue_and_Workaround_Register.md) | `KW-17` rework attribution feeding `RT-18` |
| [`KB-012_Tool_Jig_and_Test_Equipment_Operating_Guides.md`](KB-012_Tool_Jig_and_Test_Equipment_Operating_Guides.md) | Instrument-caused rework excluded under `RT-18` |
| [`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md) | Safety steps that may never be compressed (`RT-10`, `RT-20`) |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-010_SOP_Workshop_and_Depot_Repair.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-010_SOP_Workshop_and_Depot_Repair.md) | WIP and queue time — excluded from the norm |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-013_SOP_Estimate_Approval_and_Rework_Control.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-013_SOP_Estimate_Approval_and_Rework_Control.md) | Estimate construction and rework classification |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md) | Parts wait — excluded |
| `M54` Cost Accounting · `M57` Performance Incentives · `M55` Workforce Scheduling · `M36` Quotation and Estimation | The four consumers in §1.1 |
| `RP-001` KPI Dictionary | Where the paired measures in §8 are defined |
| `MD-028` Priority, Severity and SLA Definition Register | **A different concept — `RT-13`** |

---

## Sources and Currency

| Source | Verified | Next review |
|---|---|---|
| `MD-025` — `standard_minutes` mandatory on every resolution code, identified as the labour norm feeding `KB-014` and costing; `RES-06` soft warning where actual exceeds standard by more than 100% | 2026-08-16 | 2027-02-16 |
| `M54` Cost Accounting, Budgeting and FP&A — job costing and profitability by revenue stream | 2026-08-16 | 2027-02-16 |
| `M57` Performance, Incentives and Compensation; `05-05` §2 `BRU-HRM-03` — incentive calculated only after the minimum monthly job threshold is met | 2026-08-16 | 2027-02-16 |
| `M61` §5.4 FR-KMS-025 — capture prompted on repairs materially exceeding standard time; §12.1 duration-versus-standard consumed from `M01` | 2026-08-16 | 2027-02-16 |
| `06-02` `KPI-004`, `KPI-010` | 2026-08-16 | 2027-02-16 |

> **No specific time value appears in this file.** Every norm is a factual claim about how long work
> takes and requires the evidence in §6.3. Publishing an illustrative figure here would be quoted
> as a standard within a week — the same reason `KB-008` §11 shows mapping *form* rather than
> mapping *values*.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The `W5` register placement conflicts with the §12 rollout.** Phase 1 seeding must happen at **W1** with `MD-025`, or `M54` cannot cost a job and `M36` cannot quote one for four waves. The file is scheduled two waves after the need it serves. Raised as audit finding **KB-07** | Programme Content Lead with Operations Director and Finance Manager | **W1 for phase 1** |
| **O-02** | **Whether `M01`/`M31` capture productive time against the §6.1 boundary is unconfirmed.** If the recorded duration includes queue, parts wait or travel, every norm derived from it is wrong and no amount of governance fixes it | CTO with BI Lead and Operations Director | **Before W2 build — the whole file depends on it** |
| **O-03** | The utilisation factor, quoting contingency and incentive bands (§6.2) are not set. The framework is defined; the numbers are a joint Operations, Finance and HR decision | Operations Director with Finance Manager and HR Director | W4, before `M57` goes live |
| **O-04** | `RT-14` includes knowledge-capture time in the norm. **This is a live decision, not a settled one** — `M61` Q-05 asks which repair classes carry capture as a completion condition and whether it risks slowing job closure | Operations Director with Quality Manager | **W5, before incentives go live** |
| **O-05** | `RT-18` requires rework to be attributable to a cause — known issue, instrument, ESD, parts. That attribution depends on `KB-011` `O-03` and on `RP-001` defining rework categories. **Unattributed rework will default to the technician** | BI Lead with Quality Manager | W4 |
| **O-06** | The incentive scheme design in `M57` was not available for review during authoring. §6.4 states the rules a scheme must satisfy; **whether the designed scheme satisfies them is unverified** | HR Director with Operations Director | **Before `M57` configuration is frozen** |
| **O-07** | Bengali presentation of norms to technicians (`RT-09`, `RT-12`) — how an expectation is shown without becoming a countdown — is a content-design question that has not been answered | Content Design with Operations and Localisation | W5 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Knowledge_Article.md`; additions §11–§13 justified
- [x] The four conflicting consumers named, and the conflict resolved by deriving figures rather than editing the norm (`RT-07`)
- [x] `MD-025` confirmed as the single store of `standard_minutes`; no duplication (`RT-01`, `CP-01`)
- [x] Norm boundary stated once and applied to every norm (`RT-11`)
- [x] Median of competent performance chosen over mean or best, with the reasoning stated (`RT-06`)
- [x] Basis classes defined with evidence thresholds and displayed to the reader (`RT-04`, `RT-07`)
- [x] `estimate`-basis norms barred from incentive use (`RT-15`)
- [x] Incentive rules protect safety steps, complex work and knowledge capture (`RT-19`, `RT-20`)
- [x] Rework attribution excludes causes outside the technician's control (`RT-18`)
- [x] Clustering-under-the-norm named as a data-integrity signal rather than a performance result (`RT-02`)
- [x] Labour norm and SLA target explicitly separated (`RT-13`)
- [x] Every time measure paired with a quality measure (`RT-17`, §8)
- [x] Rollout ordered so costing works from W1 without provisional numbers reaching anyone's pay
- [x] All internal links resolve
- [x] `BRU-HRM-03` cited to `05-05`; `BRU-KMS-10` and `FR-KMS-*` cited to `M61`
- [x] No illustrative time value asserted
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` W5 placement versus W1 seeding need — outstanding**
- [ ] **`O-02` productive-time capture boundary confirmed — outstanding; blocking**
- [ ] **`O-06` `M57` scheme verified against §6.4 — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Operations Director and Finance Manager**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
