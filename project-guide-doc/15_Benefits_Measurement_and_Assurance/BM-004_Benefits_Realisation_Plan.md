---
id: BM-004
title: Benefits Realisation Plan
category: 15 — Benefits, Measurement & Assurance
code: BM
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Director with the Chief Financial Officer
approver: ERP Steering Committee
standards_basis: >
  MSP 5th edition (benefits management theme — benefit profiles, benefits map, disbenefits,
  benefit owner accountability) · ISO 21503:2022 (programme management — benefits realisation) ·
  ISO 21502:2020 §7.13 · PMBOK 7 (Measurement performance domain) ·
  ISO 9001:2015 §9.1, §9.3 (monitoring and management review) ·
  ISO/IEC/IEEE 15939:2017 (measurement process, consumed via BM-002)
traces_to: >
  PGD-000 BM-004 · 06-02 §3.1, §3.5, §6 · RP-015 §4.8 · CH-004 §8.4 (handover to benefits
  realisation) · RL-005 PIR-22…PIR-27, PIR-25 (a review does not re-forecast) ·
  GV-006 CC-05 (each descope states the benefit forgone) · CO-003 SOW-54 ·
  BM-002 §3.7, §3.8 · BM-003 §6.2, §7 · GV-009 wave gates · GV-010 independent review
depends_on: BM-002 (signed baselines) · BM-003 (the forecast) · 06-02 §3.1 (benefit lines) · CH-004 (adoption) · RL-005 (wave reviews)
verified_on: 2026-08-19
enumeration_timestamp: 2026-08-19 00:48 (+06)
priority: P1
needed_by: W2
rule_space: BRP
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# BM-004 — Benefits Realisation Plan

### Category 15 · Code `BM` · Rule space `BRP` · MSP 5th edition · ISO 21503:2022 · ISO 21502:2020 §7.13

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `BM-004` exists in `PGD-000` Category 15, status ◐ `06-02` §6 /
>    `RP-015`, `P1`, `needed_by: W2`.
> 2. **`PG-03` Count, do not consult.** The ownership analysis in §5.2 and the disbenefit finding in
>    §6.1 are counted from the filesystem at **2026-08-19 00:48 (+06)**, with commands shown.
> 3. **`PG-06` Cite standards.** §2.1.
> 4. **`PG-M4` Verify citations.** `verified_on: 2026-08-19`.
>
> **`PGD-000` states this document's reason for existing in one line:** *"`06-02` §6 states
> benefit-tracking discipline; `RP-015` registers baselines as content. **Neither names a benefit
> owner accountable for delivery**."* That is not quite right, and the correction matters. `06-02`
> §3.5 **does** name an owner per benefit line. **What no document names is what happens when a
> named owner misses.** §9 is that rule, and it is the reason this document exists.

---

## 1. Purpose

The programme has a benefit case (`06-02` §3.1), a corrected forecast (`BM-003` §6), a baseline
programme (`BM-002`) and a review mechanism (`RL-005`). **What it does not have is the thing that
connects them to a person and a consequence.**

`06-02` §6 says *"missed benefits are reported as missed, with the reason."* That is a **reporting**
rule. It says what appears in the pack. It does not say who decides, what they decide between, or
what happens to the benefit, the forecast or the scope when the answer is bad. **A benefit that can
be missed with no defined consequence is a forecast, not a commitment.**

This document does five things:

| # | Job | Where |
|---|---|---|
| 1 | **Turn 14 benefit lines into 14 benefit profiles** — each with a measure, a baseline reference, a curve, a dependency set and an owner | §4 |
| 2 | **Close the ownership gap** between the objectives and the benefits, which are owned by different people | §5 |
| 3 | **Create the disbenefits register** — a concept absent from all 784 files in this workspace | §6 |
| 4 | **Define attribution**, so a benefit claim can survive being challenged | §8 |
| 5 | **Define the decision rule when a benefit misses** — the gap the register names | §9 |

**What this document does not do.** It does not forecast. `BM-003` owns the forecast and `RL-005`
`PIR-25` prohibits a review from adjusting it to match an actual. **This plan tracks the variance;
it never removes it.**

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The **benefit profile schema** and all 14 profiles (§3, §4) |
| 2 | **Ownership** — accountable owner, contributing owners, and the objective-to-benefit gap (§5) |
| 3 | The **disbenefits register**, its schema and its seeded entries (§6) |
| 4 | **Measurement cadence and the tracking instrument** (§7) |
| 5 | **Attribution** — the counterfactual, and what may not be claimed (§8) |
| 6 | **The miss rule** — thresholds, decision options, escalation and the scope seam (§9) |
| 7 | **Seams** with `BM-002`, `BM-003`, `CH-004`, `RL-005`, `GV-006`, `GV-009`, `GV-010` (§10) |
| 8 | Governing rules `BRP-01`…`BRP-20` (§11) |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| **The forecast** — NPV, IRR, payback, the curve | `BM-003` | `RL-005` `PIR-25`, `BSC-20`. This plan tracks against it |
| **Benefit line values** | `06-02` §3.1 | Carried unchanged |
| **Baseline measurement** | `BM-002` | Consumed. This plan cannot start a line whose baseline is unsigned (`BRP-04`) |
| **Adoption measurement** | `CH-004` | Consumed at `CH-004` §8.4's handover. Adoption is a **dependency** of benefit, not a benefit |
| **Wave review conduct** | `RL-005` | This plan supplies `A3`'s content; `RL-005` runs the review |
| **Scope change procedure** | `GV-006` | `CC-05` requires a benefit statement; §9.6 supplies what it must contain |
| **Independent assurance** | `GV-010` | Reviews this plan; is not part of it |
| **Metric definitions** | `RP-001`, `DA-007` | |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **The 9 named benefit owners** | §4's profile for their line, and §9 — what happens if they miss |
| **Steering Committee** | §9.4's decision options; §5.3's ownership gap; §6's disbenefits |
| **CFO** | §7's tracking instrument and §8's attribution, which is what a benefit claim is defended with |
| **Programme Director** | §9's escalation path and §10's seams |
| **`RL-005` reviewers** | §7.3 — what `A3` reports at a wave review, in each of its five states |
| **`GV-010` independent review** | §8 and §11 — attribution and the rules an assurance review tests |
| **Board** | §6 and §9.4 only. The Board sees disbenefits and miss decisions, not monthly tracking |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this document conforms | Departure and rationale |
|---|---|---|---|
| **MSP 5th edition** *(PeopleCert; current, verified 2026-08-19)* | Benefits management theme | §4's benefit profile is MSP's profile: description, owner, measure, baseline, target, dependencies, realisation timing, and **disbenefits**. §6 creates the disbenefits register MSP requires | **Departure:** MSP builds a **benefits map** from the blueprint before delivery. Here 133 specifications already exist, so §4.2 constructs the map **backwards** from the delivered scope. Recorded because a backward-constructed map cannot prove completeness — only that every *claimed* benefit has a path |
| **ISO 21503:2022** | Programme benefits realisation | Benefit-to-outcome-to-output traceability; benefit owner accountability | None |
| **ISO 21502:2020** | §7.13 | Benefits management as a continuing practice, not a phase | None |
| **PMBOK 7** | Measurement performance domain | Leading and lagging indicators; the risk of measuring what is easy | Applied in §7.2 |
| **ISO 9001:2015** | §9.1, §9.3 | Monitoring, and management review as the decision forum | §9.4's decision forum is the Steering Committee, mapped to §9.3's management review |
| **ISO/IEC/IEEE 15939:2017** | Measurement process | **Consumed via `BM-002`**; this document does not re-specify measurement | `BRP-02` |

### 2.2 Source material relied on

| Source | What is taken |
|---|---|
| `06-02` §3.1 | The 14 benefit lines and their conservative/base/optimistic values |
| `06-02` §3.5 | The 14 named benefit owners and the wave each is measured from |
| `06-02` §1 | The 18 business objectives and **their** owners — the other half of §5.2's comparison |
| `06-02` §6 | Benefit tracking discipline: baseline capture, monthly reporting, quarterly review, attribution, PIR, honest reporting |
| `RP-015` §4.8 | The per-benefit-line baseline position, and the class `A`–`D` assessment |
| `BM-002` §3.7, §3.8 | Improvement exposure **BDT 542 lac**; claimable today **BDT 0** |
| `BM-003` §6.2, §7 | The corrected annual curve, and the claimed/claimable split |
| `CH-004` §8.1, §8.4 | The definition of "adopted", and the handover contract into this document |
| `RL-005` §7, §9 | `PIR-22`…`PIR-27`; the lesson lifecycle that a missed benefit feeds |
| `GV-006` `CC-05`, `CO-003` `SOW-54` | Each descope must state the benefit forgone |
| `GV-009` | The wave gates at which this plan is tested |

### 2.3 Findings this document raises

| Finding | Severity | Summary |
|---|:--:|---|
| **`BRP-F-01`** | **HIGH** | **No disbenefit is recorded anywhere in the estate** — the word appears in 0 of 784 files. MSP and ISO 21503 both require disbenefits to be identified, quantified and owned. §6.1 |
| **`BRP-F-02`** | **HIGH** | **Objective ownership and benefit ownership are different sets.** The Technical Services Head owns **BDT 30 lac** of benefit but no objective; the CEO, CTO and Customer Service Manager own objectives but no benefit. §5.2 |
| **`BRP-F-03`** | **HIGH** | **There is no decision rule when a benefit misses.** `06-02` §6 supplies a reporting rule and stops. §9 |
| **`BRP-F-04`** | **MEDIUM** | **No benefit line records a dependency on adoption**, although `CH-004` exists and adoption is the mechanism by which the largest line — technician productivity, BDT 130 lac — is delivered. §4.3 |
| **`BRP-F-05`** | **MEDIUM** | **Attribution has a rule and no method.** `06-02` §6 excludes *"general market growth"* without saying how it is identified or subtracted. §8 |
| **`BRP-F-06`** | **MEDIUM** | **Four benefit lines are measured from a wave later than the wave that delivers their capability**, so the first measurement window opens after the behaviour has already changed. §4.4 |

---

## 3. What a Benefits Realisation Plan Is

### 3.1 The four things a benefit needs

A benefit case lists amounts. A realisation plan makes each amount *deliverable*, which needs four
things the estate holds in four different documents and nowhere joins:

| # | Element | Where it lives today |
|---|---|---|
| 1 | **A measured starting point** | `BM-002` — **none signed** |
| 2 | **A forecast of when it arrives** | `BM-003` §6.2 |
| 3 | **A person accountable for delivering it** | `06-02` §3.5 — named, but with no consequence attached |
| 4 | **A rule for what happens when it does not arrive** | **Nowhere** — `BRP-F-03` |

> **`BRP-01`. A benefit with fewer than all four is tracked as *at risk* until it has all four**,
> and the missing element is named in the tracking record. On issue, **all 14 lines are at risk**,
> because element 1 is universally absent.

### 3.2 The chain this plan enforces

```
  output          →  outcome            →  benefit             →  objective
  (what is built)    (what changes)        (what it is worth)     (why we did it)
  ─────────────      ─────────────         ─────────────          ─────────────
  M02 technician     technicians work      BDT 130 lac/yr         BO-02 maximise
  mobile app         from the app,         productivity           field technician
  (RQ-001, AR-*)     jobs/day rises        (06-02 §3.1 line 2)    productivity
                     ▲                     ▲
                     │                     │
              CH-004 adoption        BM-002 baseline
              (the dependency        (the comparator
               nobody linked)         that does not exist)
```

> **`BRP-02`. Every profile states its output, its outcome and its objective, not only its
> amount.** A benefit whose outcome is unstated cannot be attributed (§8), because there is no
> mechanism to point at.

### 3.3 `BRP-F-01` context — what "backwards" costs

MSP builds the benefits map from the blueprint, so every benefit traces to a designed capability and
the map is complete by construction. **This programme has 133 specifications and no map**, so §4
constructs one from the claimed benefits backwards.

| Property | Forward-constructed map | **This map (backward)** |
|---|---|---|
| Every benefit traces to an output | Yes | **Yes** — §4 establishes it |
| Every output traces to a benefit | Yes | **Unknown.** 67 modules and 12 portals are not tested against the 14 lines |
| Completeness of the benefit set | Provable | **Not provable** |
| Disbenefits identified during design | Yes | **No** — §6 seeds them retrospectively |

> **Stated so it is not over-claimed.** This plan can show that every BDT 876 lac of claimed benefit
> has a delivery path. **It cannot show that the programme's 67 modules produce no benefit that was
> never claimed, and no disbenefit that was never noticed.** `Q-05` puts the forward pass to the
> Steering Committee as a W3 activity.

---

## 4. The Benefit Profiles

### 4.1 The profile schema

| # | Field | Content |
|---:|---|---|
| 1 | `benefit_id` | `BEN-nn`, allocated in this document only (`BRP-03`) |
| 2 | `name` | From `06-02` §3.1, unchanged |
| 3 | `value` | Conservative / base / optimistic, BDT lac per year, from `06-02` §3.1 unchanged |
| 4 | `type` | **Improvement** (needs a baseline) · **Absolute** (new capability, needs none) — from `BM-002` §3.7 |
| 5 | `accountable_owner` | One named role. From `06-02` §3.5 |
| 6 | `contributing_owners` | Roles whose delivery the benefit depends on, who are not accountable for it |
| 7 | `outputs` | The modules and portals that must be delivered |
| 8 | `outcome` | The behavioural or operational change, in one sentence |
| 9 | `objective` | The `06-02` §1 `BO-nn` it serves |
| 10 | `principal_kpis` | From `RP-015` §4.8 |
| 11 | `baseline_status` | From `BM-002` — signed / unsigned / class `C` / class `D` |
| 12 | `measured_from` | The wave, from `06-02` §3.5 |
| 13 | `capability_delivered` | The wave that delivers the output — **not always the same** (§4.4) |
| 14 | `adoption_dependency` | The `CH-004` measure the benefit requires (§4.3) |
| 15 | `disbenefits` | `DIS-nn` references (§6) |
| 16 | `attribution_method` | From §8.2 |
| 17 | `miss_threshold` | From §9.2 |

### 4.2 The fourteen profiles

Values in BDT lac per year at steady state. `[carried]` from `06-02` §3.1 and §3.5 without change.

| ID | Benefit | Base | Type | Accountable owner | Outputs | Measured from | Capability delivered |
|:--:|---|---:|:--:|---|---|:--:|:--:|
| `BEN-01` | Warranty revenue recovery | **100** | Improvement | Finance Director | `M09` | W4 | **W4** |
| `BEN-02` | Technician productivity | **130** | Improvement | Ops Director | `M02`, `M26` | **W2** | **W2** |
| `BEN-03` | Inventory cost reduction | **34** | Improvement | Inventory Manager | `M15`, `M26` | W3 | **W2** |
| `BEN-04` | Administrative labour savings | **62** | Improvement | Ops Director | All | W3 | **W1** |
| `BEN-05` | Customer retention | **78** | Improvement | CCO | `M07`, `M10`, `M27` | W4 | **W4** |
| `BEN-06` | AMC/RAMC renewal uplift | **72** | Improvement | CCO | `M08` | W5 | **W4** |
| `BEN-07` | Financial close & cash flow | **26** | Improvement | CFO | `M19`, `M20` | W3 | **W3** |
| `BEN-08` | Managed services (MSP) | **95** | Absolute | Corporate Services Head | `M05` | W6 | W6 |
| `BEN-09` | Rental gross margin | **48** | Absolute | Corporate Services Head | `M13` | W7 | W7 |
| `BEN-10` | Refurbishment & resale margin | **65** | Absolute | Retail Operations Head | `M14` | W7 | W7 |
| `BEN-11` | Marketplace commission | **84** | Absolute | CCO | `M12` | W8 | W8 |
| `BEN-12` | Data services | **30** | Absolute | **Technical Services Head** | `M06` | W7 | W7 |
| `BEN-13` | E-waste material recovery | **12** | Absolute | Quality Manager | `M18` | W9 | W8 |
| `BEN-14` | Dynamic pricing margin uplift | **40** | Improvement | CCO | `M11`, `M26` | W8 | W8 |
| | **Total** | **876** | | **9 distinct owners** | | | |

**Verification** `[counted]`: 100+130+34+62+78+72+26 = **502** improvement-and-existing ·
95+48+65+84+30+12+40 = **374** new · 502 + 374 = **876** ✓, reconciling to `06-02` §3.1 and BRD
§19.2's subtotals · improvement lines by `BM-002` §3.7's classification = 100+130+34+62+78+72+26+40
= **542**; absolutes = **334** ✓.

### 4.3 `BRP-F-04` — the adoption dependency nobody recorded

**Severity: MEDIUM · Status: OPEN · Owner: Programme Director**

`CH-004` measures adoption. `06-02` §3.1 claims benefit. **Neither document references the other's
mechanism**, yet for seven of the fourteen lines the benefit arrives only if people change what
they do.

| ID | Benefit | Base | Adoption dependency — the `CH-004` measure the benefit needs |
|:--:|---|---:|---|
| `BEN-02` | Technician productivity | **130** | **Technician app daily active usage** (`KPI-016`, target 95%). At 50% adoption this line delivers roughly half |
| `BEN-04` | Administrative labour savings | 62 | Branch staff using the system rather than parallel spreadsheets; `KPI-094` manual reports → zero |
| `BEN-05` | Customer retention | 78 | Customer self-service adoption (`KPI-025`, `KPI-022`) |
| `BEN-03` | Inventory cost reduction | 34 | Van-stock discipline and scan compliance |
| `BEN-07` | Financial close & cash flow | 26 | Finance team operating the new close, not the old one |
| `BEN-01` | Warranty revenue recovery | 100 | Technicians capturing claim evidence at the job (`KPI-041`) |
| `BEN-06` | AMC/RAMC renewal uplift | 72 | Commercial team working the renewal queue |
| | **Adoption-dependent total** | **502** | **57% of the benefit case** |

**Verification**: 130+62+78+34+26+100+72 = **502** ✓ · 502 ÷ 876 = 0.573 → **57%** ✓.

> **`BRP-05`. A benefit with an adoption dependency does not enter its realisation curve until its
> `CH-004` measure reaches the threshold in that profile.** Reporting a benefit as realisable while
> its adoption measure sits below threshold is the commonest way a benefit case is claimed and not
> delivered — and `CH-004` §8.4 already hands over the measure, its definition and its owner, so
> the data exists.

**Note the interaction with `BM-002`.** `BEN-02`'s adoption measure `KPI-016` has a baseline of 0%
(class `D`, genuine zero) and **is** used by a module specification — it is one of `BM-002` §3.5's
eight precise-and-produced KPIs. **The largest benefit line in the programme has a usable adoption
comparator.** That is the exception, not the rule, and it should be exploited: `BEN-02` can be
tracked properly from W2 while most lines cannot.

### 4.4 `BRP-F-06` — four lines are measured after their capability lands

**Severity: MEDIUM · Status: OPEN · Owner: CFO**

Comparing fields 12 and 13 of §4.2:

| ID | Benefit | Capability delivered | Measured from | Gap |
|:--:|---|:--:|:--:|:--:|
| `BEN-03` | Inventory cost reduction | **W2** | W3 | **1 wave** |
| `BEN-04` | Administrative labour savings | **W1** | W3 | **2 waves** |
| `BEN-06` | AMC/RAMC renewal uplift | **W4** | W5 | **1 wave** |
| `BEN-13` | E-waste material recovery | **W8** | W9 | **1 wave** |

**Why this matters, and it is not pedantry.** `06-02` §6 and `BM-002` `BL-05` require the baseline
to be captured **before the consuming wave**. If the capability lands at W1 and the benefit is
"measured from" W3, a reader will naturally schedule the baseline before W3 — **by which time the
W1 capability has already changed the thing being baselined.**

`BEN-04` is the worst case: **BDT 62 lac, capability at W1, measured from W3.** Its principal KPIs
are `KPI-001` and `KPI-094`, and `BM-002` exercise `B3` — the effort census — must run **before
Month 4**, two full waves before the line is "measured from".

> **`BRP-06`. The baseline deadline is set by `capability_delivered`, never by `measured_from`.**
> Field 13 governs the `BM-002` schedule; field 12 governs only when the *claim* may first be made.
> The two are recorded separately in every profile so they cannot be conflated again.

---

## 5. Ownership

### 5.1 One accountable owner, many contributors

MSP and `BRU-DAT-09` agree: one accountable owner per benefit, with contributors recorded as
contributors. `06-02` §3.5 supplies the accountable owner for all 14 lines. **This document adds
the contributor set, because a benefit owner who cannot deliver alone and does not know who else
must act is accountable for something outside their control.**

| ID | Accountable | Contributing owners |
|:--:|---|---|
| `BEN-01` | Finance Director | Ops Director *(evidence capture at the job)*; Quality Manager *(certification, `KPI-063`)* |
| `BEN-02` | Ops Director | CTO *(app delivery)*; HR Director *(technician release for training)* |
| `BEN-03` | Inventory Manager | Ops Director *(van-stock discipline)* |
| `BEN-04` | Ops Director | CFO *(close effort)*; CTO *(reporting automation, `KPI-094`)* |
| `BEN-05` | CCO | **Customer Service Manager** *(`BO-05`, `BO-16`)*; CTO *(`M27` delivery)* |
| `BEN-06` | CCO | Finance Director *(contract margin, `KPI-031`)* |
| `BEN-07` | CFO | Ops Director *(job closure timeliness)* |
| `BEN-08` | Corporate Services Head | CTO *(monitoring platform)* |
| `BEN-09` | Corporate Services Head | Inventory Manager *(asset control)* |
| `BEN-10` | Retail Operations Head | Quality Manager *(grading consistency)*; Technical Services Head *(data destruction)* |
| `BEN-11` | CCO | Finance Director *(seller payout accuracy)*; Quality Manager *(marketplace job quality)* |
| `BEN-12` | Technical Services Head | Quality Manager *(chain of custody)* |
| `BEN-13` | Quality Manager | Retail Operations Head *(disposal volume)* |
| `BEN-14` | CCO | Finance Director *(margin measurement)* |

> **`BRP-07`. A contributing owner is named in the profile and consulted before a miss decision
> (§9.4), and is never the person who reports the variance.** Accountability that can be shared is
> accountability that can be deferred.

### 5.2 `BRP-F-02` — objective ownership and benefit ownership are different sets

**Severity: HIGH · Status: OPEN · Owner: Programme Director with the CEO**

```bash
# §1 objective owners (column 7) vs §3.5 benefit owners (column 2)
sed -n '21,41p' 06-02.md | grep -E '^\| (\*\*)?BO' | awk -F'|' '{print $8}' | sort -u
sed -n '255,270p' 06-02.md | grep '^| ' | awk -F'|' '{print $3}' | sort -u
```

| Set | Count | Members |
|---|---:|---|
| Objective owners, `06-02` §1 | **12** | CCO · CEO · CFO · CFO/HR Director · CTO · Corporate Services Head · Customer Service Manager · Finance Director · Inventory Manager · Ops Director · Quality Manager · Retail Operations Head |
| Benefit owners, `06-02` §3.5 | **9** | CCO · CFO · Corporate Services Head · Finance Director · Inventory Manager · Ops Director · Quality Manager · Retail Operations Head · **Technical Services Head** |
| **Benefit owner, not an objective owner** | **1** | **Technical Services Head** |
| **Objective owner, not a benefit owner** | **4** | **CEO** · **CTO** · **Customer Service Manager** · **CFO/HR Director** *(joint role)* |

**What each divergence means:**

| Role | Position | Consequence |
|---|---|---|
| **Technical Services Head** | Accountable for **`BEN-12` data services, BDT 30 lac**, but owns none of the 18 business objectives | Accountable for a financial outcome with no strategic mandate behind it. If `BO-nn` priorities compete, this benefit has no objective to appeal to |
| **CEO** | Owns `BO-07` (real-time visibility) and `BO-09` (**+87% revenue growth**) — the programme's two largest strategic claims — and no benefit line | **The growth objective has no BDT figure and no owner of a BDT figure.** It is either outside the 876 or double-counted inside it, and nothing states which |
| **CTO** | Owns `BO-17` (decisions on live data) and `BO-18` (second-country readiness), no benefit line | `BO-18` is a real option with genuine value that the benefit case does not price at all |
| **Customer Service Manager** | Owns `BO-05` (CSAT, TAT) and `BO-16` (conversations captured), no benefit line — while **`BEN-05` customer retention, BDT 78 lac**, is the CCO's | **The person accountable for the outcome is not accountable for the benefit it produces.** §5.1 records them as a contributing owner; that is a mitigation, not a fix |

> **`BRP-08`. Every benefit names its objective and every objective names its benefit, or records
> that it has none and why.** §4.2 field 9 supplies the first direction. The second is `Q-01`, and
> it is the CEO's, because two of the four gaps are the CEO's own objectives.

### 5.3 The accountability contract

> **`BRP-09`. A benefit owner's accountability is recorded, accepted in writing, and reflected in
> that role's objectives for the period.** An owner named in a document they have not signed is a
> name, not an owner — which is the condition `06-02` §3.5 has been in since issue.

| Element | Requirement |
|---|---|
| Acceptance | The named owner signs the profile at W2 for improvement lines, at the delivering wave for absolutes |
| Authority | The owner may call on contributing owners and escalate to the Steering Committee (§9.5) |
| Reporting | Monthly variance commentary (`06-02` §6), in the owner's own words, not the PMO's |
| **Limit** | An owner is **not** accountable for a benefit whose baseline is unsigned (`BRP-04`) or whose adoption dependency is below threshold (`BRP-05`). Those are programme failures, and §9.4 routes them to the programme, not to the owner |

> **The last row is what makes the rest of this section fair.** Holding an owner to a benefit whose
> comparator was never measured produces defensive reporting, not delivery. **The programme owns
> the baseline; the owner owns the movement.**

---

## 6. Disbenefits

### 6.1 `BRP-F-01` — the estate contains no disbenefit

**Severity: HIGH · Status: OPEN · Owner: Programme Director**

```bash
grep -rli "disbenefit" .    # across the whole workspace
```

**Result: 0 files, of 784.**

MSP 5th edition's benefits management theme requires that a programme identify **disbenefits** —
outcomes perceived as negative by one or more stakeholders, which are a real consequence of the
change and are deducted from the benefit case. ISO 21503:2022 carries the same requirement.

**A benefit case containing only benefits is not a conservative case; it is an incomplete one.**
The conservative *scenario* in `06-02` §3.1 reduces the size of the good outcomes. It does not
introduce a single bad one.

> **`BRP-10`. Every profile records its disbenefits, or records that it has none and who confirmed
> that.** A blank disbenefit field is not evidence of absence.

### 6.2 The disbenefit schema

| # | Field | Content |
|---:|---|---|
| 1 | `disbenefit_id` | `DIS-nn` |
| 2 | `description` | The negative outcome, and **for whom** it is negative |
| 3 | `arises_from` | The `BEN-nn` or the delivery activity that causes it |
| 4 | `value` | BDT lac per year, or `NOT QUANTIFIED` with the owner and date to quantify it |
| 5 | `owner` | The role accountable for managing it — **not necessarily the benefit owner** |
| 6 | `treatment` | Avoid · reduce · transfer · accept |
| 7 | `deducted` | Whether it is netted against the benefit case, or managed outside it |
| 8 | `raid_ref` | The `GV-005` risk it corresponds to, where one exists |

### 6.3 Seeded register

Eight disbenefits, identified from material already in the estate. **This is a first issue and is
not asserted to be complete** — §6.4 is how it becomes so.

| ID | Disbenefit | Arises from | Value, BDT lac/yr | Owner | Treatment |
|:--:|---|---|---|---|---|
| **`DIS-01`** | **Organisation-wide productivity draw during delivery.** `CO-005` §7.3 computes a **5–7% draw** concentrated in UAT and training windows, worth **$681K over three years** on the Tier 2 basis | Delivery activity, all waves | **$681K over 3 yrs** ≈ **279 lac/yr equivalent** — *`CO-005` computed it and never labelled it a disbenefit* | HR Director | **Reduce** — `CO-005` `TCO-08`'s backfill decision |
| **`DIS-02`** | **Workforce monitoring perceived as surveillance.** `CH-004` §9 records this as *"the programme's most sensitive open objection"*; `RSK-012` rates withdrawal as reinforcement | `BEN-02` technician productivity | `NOT QUANTIFIED` — HR Director, **W2** | HR Director | **Reduce** — `ADP-20`, `ADP-21`, transparency in Bengali |
| **`DIS-03`** | **Administrative roles displaced.** `BEN-04`'s BDT 62 lac is achieved by removing administrative effort. **Nothing in the estate states whether that effort is redeployed or removed** | `BEN-04` administrative labour savings | `NOT QUANTIFIED` — HR Director, **W1** | HR Director | **Decide** — this is a Board question, not a programme one |
| **`DIS-04`** | **Marketplace cannibalises owned technician work.** `BO-12` targets **25% of job volume** to external sellers. `BEN-02`'s productivity benefit is measured per owned technician | `BEN-11` vs `BEN-02` | `NOT QUANTIFIED` — CCO with Ops Director, **W6** | CCO | **Reduce** — model the volume split before W8 |
| **`DIS-05`** | **Dynamic pricing damages customer perception.** `BEN-14` raises margin by varying price; `BEN-05` depends on CSAT and churn | `BEN-14` vs `BEN-05` | `NOT QUANTIFIED` — CCO, **W7** | CCO | **Reduce** — `G7-06`'s guard rails and decision audit |
| **`DIS-06`** | **Legacy decommissioning destroys baseline evidence**, converting recoverable class-`A` baselines into permanently unmeasurable ones | `RL-006`, against `BM-002` | Up to **542 lac** of *claimability* — not of benefit | Programme Director | **Avoid** — `BM-002` `BMR-09` |
| **`DIS-07`** | **PDPA exposure from adoption telemetry.** Enforcement lands ~13 May 2027, **inside W4** | `CH-004` measurement | `NOT QUANTIFIED` — CDO with Legal, **W3** | Chief Data Officer | **Avoid** — `SC-003`, `LG-020` `AU2` |
| **`DIS-08`** | **Concentration risk.** Fourteen revenue streams move onto one platform; an outage that was previously partial becomes total | Programme design | `NOT QUANTIFIED` — CTO, **W4** | CTO | **Reduce** — `PE-007` DR, `SV-002` SLA |

> **`DIS-01` is the one to read.** `CO-005` §7.3 already computed a **5–7% organisation-wide
> productivity draw** worth **$681K**, and treated it as a *cost*. **On the MSP definition it is
> also a disbenefit** — an outcome that is negative for the operating business, distinct from cash
> spent. It is recorded here so that the benefit case and the cost model do not each assume the
> other is carrying it.

> **`BRP-11`. A disbenefit is not deducted twice.** Where a disbenefit is already inside `CO-005`'s
> cost model (`DIS-01`) or inside `BM-002`'s claimability position (`DIS-06`), field 7 records it as
> **managed outside the benefit case**, and it is not netted from the 876 as well.

### 6.4 Completing the register

> **`BRP-12`. Every `NOT QUANTIFIED` entry carries an owner and a date, and is quantified or
> formally accepted by that date.** Six of the eight are `NOT QUANTIFIED` at this issue; the latest
> date is W7. An entry still unquantified at its date is escalated to the Steering Committee under
> §9.5, exactly as a missed benefit is.

**The forward pass.** §3.3 records that this benefits map is constructed backwards and therefore
cannot prove completeness. The forward pass — testing all 67 modules and 12 portals for benefits and
disbenefits nobody claimed — is `Q-05`, a W3 activity for Enterprise Architecture with the benefit
owners.

---

## 7. Measurement and Cadence

### 7.1 The cadence

Carried from `06-02` §6, with the owner and the artefact made explicit.

| Frequency | Forum | Artefact | Owner | Content |
|---|---|---|---|---|
| **Monthly** | PMO | Benefit tracking pack | PMO | Actual vs `BM-003` §6.2 curve per line; variance; **owner's own commentary** (`BRP-09`); unsigned-baseline count (`BM-002` `BMR-13`) |
| **Quarterly** | Steering Committee | Benefit realisation review | Programme Director | Variance by line; miss decisions (§9.4); disbenefit register movement; adoption thresholds |
| **Per wave** | `RL-005` wave review | `A3` Benefits section | PMO | The five `A3` states (§7.3) |
| **Per gate** | `GV-009` wave gate | Gate benefit position | Programme Director | Whether any line has crossed a §9.2 threshold; `BSC-15`'s steady-state run-rate test |
| **Annual** | Board | Benefit case restatement | CFO | `BM-003` recomputed (`BSC-13`); write-downs (§9.7) |
| **Month 42** | Independent | **Full benefits audit** | `GV-010` / internal audit | `06-02` §6's post-implementation review, against §7.4's register and `BM-002` §8.5's evidence |

> **`BRP-13`. The monthly commentary is written by the benefit owner, not by the PMO.** A PMO that
> writes the owner's variance explanation has quietly assumed the accountability, and the owner will
> not contest a narrative they did not write.

### 7.2 Leading and lagging indicators

PMBOK 7's Measurement domain warns against measuring what is easy. Benefit measures are **lagging**
by construction — they report a financial outcome months after the behaviour that produced it.

| ID | Lagging measure — the benefit | Leading measures — visible months earlier |
|:--:|---|---|
| `BEN-02` | Productivity value, BDT | `KPI-016` app daily active usage · `KPI-013` automatic assignment rate · `KPI-012` utilisation |
| `BEN-01` | Warranty revenue recovered | `KPI-041` claims with complete evidence at submission · `KPI-037` submitted within 72 h |
| `BEN-05` | Retention value | `KPI-025` deflection · `KPI-020` CSAT · `KPI-023` churn |
| `BEN-07` | Cash-flow value | `KPI-050` close cycle · `KPI-051` auto-match rate |
| `BEN-06` | Renewal uplift value | `KPI-028` renewal rate · `KPI-030` contract SLA attainment |
| `BEN-04` | Labour saving value | `KPI-094` manual reports remaining · `KPI-001` automation rate |

> **`BRP-14`. Every profile publishes at least one leading measure, and the miss rule (§9.2) fires
> on the leading measure, not only the lagging one.** A miss detected on the lagging measure is
> detected a wave too late to act on.

### 7.3 The five `A3` states

`BM-002` §8.4 defines when `PIR-27` releases per KPI. This is the benefit-level equivalent that
`RL-005`'s `A3` section reports:

| State | Condition | `A3` reports |
|---|---|---|
| **Not claimable — no baseline** | No signed baseline for the principal KPIs (`BM-002`) | *"Not claimable — no baseline."* `PIR-27` unchanged. **All 14 lines at this issue** |
| **Not claimable — low confidence** | Baseline signed at confidence `Low` (`BM-002` §7.4) | *"Not claimable — baseline confidence Low"*, with the upgrade date |
| **Not yet realisable** | Capability not delivered, or adoption below threshold (`BRP-05`) | *"Not yet realisable"*, with the dependency named. **Not a miss** (§9.3) |
| **Realisable — tracking** | All four elements of §3.1 present; within the §9.2 green band | Actual, forecast, variance, owner's commentary |
| **Realisable — missed** | Outside the §9.2 band | Variance, cause, and the §9.4 decision taken |

### 7.4 The tracking instrument

A controlled register under `GV-011`, one row per `BEN-nn` per period, holding: period · forecast
(from `BM-003` §6.2) · actual · variance · leading-measure values · adoption measure · state (§7.3)
· owner's commentary · decision reference where §9.4 has fired.

> **`BRP-15`. The forecast column is written once, from `BM-003`, and is never overwritten.**
> `RL-005` `PIR-25` and `BSC-20`: a review that adjusts the forecast to match the actual has removed
> the variance it exists to expose. A re-forecast is a **new row with a decision reference**, never
> an edit.

### 7.5 What is published, and to whom

| Audience | Receives | Does not receive |
|---|---|---|
| Benefit owner | Their line in full | Other owners' commentary before the quarterly review |
| Steering Committee | All 14 lines, disbenefits, miss decisions | Individual-level adoption data (`ADP-20` purpose limitation) |
| Board | Quarterly summary; all write-downs; all Red states | Monthly detail |
| `GV-010` | Everything, unfiltered | — |
| Vendor | Only measures named in `CO-003` as acceptance criteria | The benefit case |

---

## 8. Attribution

### 8.1 `BRP-F-05` — the rule exists and the method does not

**Severity: MEDIUM · Status: OPEN · Owner: CFO**

`06-02` §6 states: *"Benefits are attributed to the ERP **only where a causal mechanism is
documented**; general market growth is excluded."*

**That is the right rule and there is no method behind it.** Nothing in the estate says how general
market growth is identified, how it is subtracted, or what evidence a "documented causal mechanism"
consists of. A benefit claim of BDT 130 lac defended at the Month 42 audit with *"the mechanism is
documented"* will not survive contact with an auditor.

### 8.2 Four attribution methods

> **`BRP-16`. Every profile names its attribution method from this list, and a benefit claimed
> without one is reported as *unattributed*, not as realised.**

| Method | How it works | Strength | Applies to |
|:--:|---|:--:|---|
| **`AT-1` Direct system measurement** | Before/after on the same metric, same `RP-001` definition, same population. The baseline is the before | **Strongest** | `BEN-02`, `BEN-03`, `BEN-07` — operational metrics the system computes directly |
| **`AT-2` Staggered-rollout comparison** | `RL-004` rolls out branch by branch. At any moment some branches are live and some are not. **Not-yet-live branches are a control group**, and market conditions apply equally to both | **Strong — and free** | `BEN-01`, `BEN-04`, `BEN-05`, `BEN-06` — anything measurable per branch |
| **`AT-3` Documented causal mechanism with sensitivity** | The mechanism is written down, the counterfactual stated, and the claim published as a range with the sensitivity to the key assumption | Moderate | `BEN-14`, and any line where `AT-1`/`AT-2` are unavailable |
| **`AT-4` Not attributable** | Recorded as delivered but not attributed | — | Where the alternative is a claim that cannot be defended |

### 8.3 `AT-2` is available, valuable and time-limited

> **This is the most valuable unclaimed asset in the measurement design.** The programme is rolling
> out across **51+ service centres** in waves. That produces, at no cost, the closest thing to a
> controlled experiment a business change ever gets: **live branches and not-yet-live branches
> operating in the same market, the same season and the same economy in the same month.**

| Property | Consequence |
|---|---|
| Market growth, seasonality and price change affect both groups equally | **`06-02` §6's exclusion becomes measurable rather than asserted** — the difference between the groups is what the ERP did |
| No additional data collection is required | The measure is already being computed per branch for the live group |
| **The design expires** | Once every branch is live there is no control group. `RL-004`'s rollout completes at **W5** (`G5-06`, all 51+ centres) |

> **`BRP-17`. Where a benefit is measurable per branch, `AT-2` is the default attribution method and
> the branch-level series is retained from the first go-live.** The comparison cannot be
> reconstructed later: it requires the not-yet-live branches' data to have been captured **while
> they were still not live**. This is `BM-002` `BMR-08`'s foreclosure logic applied to attribution
> rather than to baselines, and it has the same deadline shape.

### 8.4 The counterfactual

| Element | Requirement |
|---|---|
| Statement | Every profile states what would have happened without the programme, in one sentence |
| Basis | The as-is trend from `SP-002` and the pre-programme series from `BM-002`, where they exist |
| Exclusions | Market growth, seasonality, price change, acquisitions, one-off events — identified by `AT-2` where available, argued explicitly where not |
| Publication | The counterfactual is published **beside** the claim, never held separately |

### 8.5 What may not be claimed

| # | Not claimable |
|---|---|
| 1 | Benefit from a KPI with no signed baseline (`06-02` §6; `PIR-27`) |
| 2 | Benefit whose adoption dependency is below threshold (`BRP-05`) |
| 3 | Benefit attributed by assertion — no method from §8.2 named |
| 4 | Benefit double-counted across two lines. **`BEN-11` and `BEN-02` are the live risk** (`DIS-04`) |
| 5 | **Cost avoidance already inside `CO-005`'s cost model** — `BSC-17`'s double-count prohibition |
| 6 | Benefit realised in a branch that is not yet live |

---

## 9. The Miss Rule

### 9.1 `BRP-F-03` — the gap this section fills

**Severity: HIGH · Status: OPEN · Owner: Steering Committee**

`06-02` §6's final row reads: *"Missed benefits are reported as missed, with the reason. A benefit
case that is never revisited is not a business case."*

**That sentence is admirable and it is a reporting rule.** It names no threshold, no decision, no
decider, no timescale and no consequence. `RL-005` `PIR-24` restates it verbatim and adds nothing,
correctly — a review standard should not invent a benefits decision rule. **`PGD-000` names this
gap as `BM-004`'s reason for existing.** This section is the rule.

### 9.2 Thresholds

Variance is measured against the `BM-003` §6.2 curve for the period, per line.

| Band | Condition | Action |
|:--:|---|---|
| 🟢 **Green** | Actual ≥ 90% of forecast, **and** every leading measure within its own band | Track. Owner's commentary in the monthly pack |
| 🟡 **Amber** | Actual 75–90% of forecast, **or** any leading measure below its band for one period | **Owner produces a recovery action** within 20 working days: action, owner, date, expected recovery |
| 🔴 **Red** | Actual < 75% of forecast, **or** Amber in two consecutive periods, **or** a leading measure below band for two consecutive periods | **§9.4 decision** at the next Steering Committee, and the Board is informed |

> **`BRP-18`. Two consecutive Ambers is a Red, and this is the rule that does the work.** A benefit
> that is 85% of forecast every month for a year is not on plan; it is missing by 15% and being
> reported as nearly fine. The estate's own `PIR-38` condition 4 uses the identical principle for
> lessons: *"a lesson raised twice is no longer a lesson about the wave."*

### 9.3 What is not a miss

> **`BRP-19`. A benefit cannot miss until it can be claimed.** Routing a programme failure to a
> benefit owner produces defensive reporting and no correction.

| Situation | Classification | Routed to |
|---|---|---|
| Baseline unsigned | **Not a miss.** State *"not claimable — no baseline"* | **Programme** — `BM-002` `Q-01`, Steering funding decision |
| Adoption below threshold | **Not a miss.** State *"not yet realisable"* | **`CH-004`** — adoption intervention, `ADP` reinforcement |
| Capability not delivered | **Not a miss.** State *"not yet realisable"* | **`GV-004`** schedule; `BM-003` §8.2 prices the slip at ~$513K/yr |
| Baseline signed, capability live, adoption at threshold, benefit below forecast | **A miss.** §9.2 bands apply | **The benefit owner** |

### 9.4 The decision, when a benefit misses

At Red, the Steering Committee takes **one** of five decisions. It may not take none.

| # | Decision | When it is right | What must accompany it |
|:--:|---|---|---|
| **`M1` Intervene** | The mechanism is intact and something specific is blocking it | Action, named owner, date, expected recovery, and the period by which recovery is verified. **Default choice** |
| **`M2` Re-phase** | The benefit will arrive, later | The revised timing, and **`BM-003` recomputes the case** (`BSC-13`). A re-phasing that does not move the NPV has not been computed |
| **`M3` Write down** | The benefit will not arrive at the forecast size | §9.7. The new value, the reason, **`BM-003` recomputes**, and the Board is informed at the next meeting |
| **`M4` Re-attribute** | The benefit is arriving elsewhere — commonly the `BEN-11`/`BEN-02` interaction (`DIS-04`) | Evidence under §8.2, and **both** lines adjusted in the same change |
| **`M5` Escalate as a stop condition** | The line is material and its loss changes the programme case | `BM-003` §8.5, and `BSC-15`'s steady-state test. Goes to the Board, not the Steering Committee |

> **`BRP-20`. "Accept and continue" is not a decision.** A Red with no decision recorded is
> escalated automatically to the Board at the next meeting. This is the mechanism that makes the
> difference between this document and `06-02` §6, which allows a benefit to be reported as missed
> indefinitely with no consequence.

### 9.5 Escalation and timing

| Trigger | To | Within |
|---|---|---|
| Amber | Benefit owner | Recovery action in 20 working days |
| Red | Steering Committee | Decision at the next scheduled meeting, maximum 30 days |
| Red with no decision | **Board** | Automatically, at the next Board meeting (`BRP-20`) |
| `M3` write-down of any size | Board | Informed at the next meeting; `BM-003` recomputed |
| `M5`, or cumulative write-downs > **BDT 100 lac** | **Board, as a stop-or-restructure decision** | Immediately |
| Disbenefit unquantified past its §6.4 date | Steering Committee | Next meeting |

**Verification of the BDT 100 lac trigger** `[derived]`: 100 lac is **11.4%** of the 876 lac case and
**18.5%** of the 542 lac improvement exposure — the point at which the `BM-003` §6.5 corners
materially reorder. 100 ÷ 876 = **11.4%** ✓ · 100 ÷ 542 = **18.5%** ✓.

### 9.6 The scope seam — what `CC-05` requires

`GV-006` `CC-05` and `CO-003` `SOW-54` both require that a scope change state the benefit added or
forgone, and that `BM-004` be updated in the same change. **This is what that statement must
contain:**

| # | Element |
|---|---|
| 1 | The `BEN-nn` lines affected, and the BDT change to each |
| 2 | The **accountable owner's written agreement** — a benefit may not be removed from an owner's accountability without their knowledge (`BRP-07`) |
| 3 | Any `DIS-nn` created or removed |
| 4 | The **`BM-003` recomputation** — NPV, payback and the steady-state run-rate test |
| 5 | Whether the removal changes any line's attribution method — descoping a module can destroy an `AT-1` measurement path |

> **`CO-005` §11 option C already demonstrates the need**: descoping Categories D, F, I or J removes
> 349 PW **and BDT 125 lac of rental and refurbishment margin** — `BEN-09` and `BEN-10` in full.
> A descope decision taken on cost alone is, in `SOW-54`'s words, *"half a decision."*

### 9.7 Write-down

| Rule | Requirement |
|---|---|
| A write-down is recorded in **this plan and in `BM-003`** in the same change | Never in one alone |
| The original value is **retained**, with the reason and the date | Mirrors `BM-002` `BL-07`'s restatement discipline |
| The Month 42 audit reads **original and current** | A case silently revised to match the outturn is not auditable |
| A written-down benefit **may be written back up** only on evidence, with the same approvals | Symmetry, so write-down is not a one-way ratchet that discourages honesty |

> **The purpose of §9.7 is to make honest reporting survivable.** An owner who believes a write-down
> is a permanent mark against them will defend an unachievable forecast for a year. `06-02` §6 asked
> for honest reporting; this is the mechanism that makes it rational.

---

## 10. Seams

| With | Contract | Direction |
|---|---|---|
| **`BM-002`** | Supplies signed baselines. **No line leaves "not claimable" until its principal KPIs are signed** (`BRP-04`, `PIR-27`) | In |
| **`BM-003`** | Supplies the forecast curve (§6.2) and the claimed/claimable split. **Recomputes on every `M2`, `M3`, `M4` and every `CC-05` change** | Both |
| **`CH-004`** | `CH-004` §8.4 hands over the measure, definition, denominator, baseline, value and owner at §8.1's threshold. **This plan supplies the threshold each benefit needs** (`BRP-05`) | Both |
| **`RL-005`** | Supplies `A3` content in the five states (§7.3); receives missed-benefit lessons under `PIR-33`. **Does not re-forecast** (`PIR-25`) | Both |
| **`GV-006` / `CO-003`** | `CC-05` / `SOW-54` benefit statement content (§9.6) | In |
| **`GV-009`** | Gate benefit position; `BSC-15`'s steady-state run-rate test | Out |
| **`GV-010`** | Independent review of attribution (§8) and of the miss decisions (§9.4) — the check on the incentive to report favourably | Out |
| **`GV-005`** | `DIS-nn` entries corresponding to `RSK-nnn`; `Q-01`…`Q-06` escalated | Both |
| **`BM-005`** | Every `M1`–`M5` decision and every missed benefit produces a lesson with a landing site | Out |
| **`GV-011`** | Register custody, versioning and retention of §7.4 | In |

---

## 11. Governing Rules — Consolidated

| # | Rule |
|---|---|
| **`BRP-01`** | A benefit needs a **baseline, a forecast, an accountable owner and a miss rule**. With fewer than four it is tracked as **at risk**, and the missing element is named |
| **`BRP-02`** | Every profile states its **output, outcome and objective**, not only its amount |
| **`BRP-03`** | `BEN-nn` and `DIS-nn` are allocated **in this document only** |
| **`BRP-04`** | **No line leaves "not claimable" until its principal KPIs have signed baselines** (`06-02` §6, `PIR-27`) |
| **`BRP-05`** | A benefit with an **adoption dependency does not enter its realisation curve** until its `CH-004` measure reaches the profile threshold |
| **`BRP-06`** | The **baseline deadline is set by `capability_delivered`, never by `measured_from`** |
| **`BRP-07`** | **Contributing owners are named**, consulted before a miss decision, and never report the variance |
| **`BRP-08`** | Every benefit names its objective; every objective names its benefit **or records that it has none and why** |
| **`BRP-09`** | Accountability is **accepted in writing** and reflected in the role's objectives. An owner is **not** accountable for an unsigned baseline or a sub-threshold adoption measure |
| **`BRP-10`** | Every profile records its **disbenefits**, or records that it has none and who confirmed that |
| **`BRP-11`** | **A disbenefit is not deducted twice** — field 7 records whether it is netted here or managed in `CO-005`/`BM-002` |
| **`BRP-12`** | Every `NOT QUANTIFIED` disbenefit carries an **owner and a date**, and escalates if it passes the date |
| **`BRP-13`** | The **monthly commentary is written by the benefit owner**, not by the PMO |
| **`BRP-14`** | Every profile publishes a **leading measure**, and the miss rule fires on it |
| **`BRP-15`** | The **forecast column is written once and never overwritten**. A re-forecast is a new row with a decision reference |
| **`BRP-16`** | Every profile names an **attribution method** from `AT-1`…`AT-4`. A claim without one is reported as *unattributed* |
| **`BRP-17`** | Where measurable per branch, **`AT-2` staggered-rollout comparison is the default**, and the branch series is retained from the first go-live. **The design expires at W5** |
| **`BRP-18`** | **Two consecutive Ambers is a Red** |
| **`BRP-19`** | **A benefit cannot miss until it can be claimed.** Programme failures route to the programme |
| **`BRP-20`** | **"Accept and continue" is not a decision.** A Red with no recorded decision escalates automatically to the Board |

---

## 12. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `BM-004-D-01` | Whether to create a disbenefits register | Rely on `GV-005` risks · create one | **Create** (§6) | MSP and ISO 21503 require it; a risk is a possible future event, a disbenefit is an intended consequence that is negative for someone | 8 seeded entries, 6 requiring quantification by W7 |
| `BM-004-D-02` | Where accountability sits when a baseline is unsigned | Benefit owner · programme | **Programme** (`BRP-09`, `BRP-19`) | Holding an owner to an unmeasured comparator produces defensive reporting, not delivery | §9.3 routes three situations away from owners |
| `BM-004-D-03` | Default attribution method | Direct measurement only · staggered-rollout comparison where available | **`AT-2` where measurable per branch** (`BRP-17`) | The wave rollout supplies a control group at no cost, and it makes `06-02` §6's market-growth exclusion measurable rather than asserted | Branch-level series must be retained from first go-live; expires W5 |
| `BM-004-D-04` | The Red threshold | Single band · two-band with a consecutive rule | **Three bands, two consecutive Ambers is a Red** (`BRP-18`) | A benefit at 85% every month is missing by 15% and reported as nearly fine | §9.2 |
| `BM-004-D-05` | Whether "accept and continue" is permitted | Permit · prohibit | **Prohibit** (`BRP-20`) | It is what `06-02` §6 implicitly permits, and it is the reason `PGD-000` records this document's gap | A Red with no decision escalates to the Board automatically |
| `BM-004-D-06` | Write-down reversibility | One-way · reversible on evidence | **Reversible** (§9.7) | An irreversible write-down makes honest early reporting irrational | Symmetric approvals |
| `BM-004-D-07` | Whether to net `DIS-01` from the benefit case | Net it · manage outside | **Manage outside** (`BRP-11`) | `CO-005` §6.6 already carries the $681K as Tier 2 cost; netting it here double-counts | Field 7 records the treatment for every entry |

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Which benefit line carries `BO-09`'s +87% revenue growth**, and is it inside the 876 lac or additional? Two of the four ownership gaps are the CEO's own objectives | **CEO** | W2 | `BRP-08`; whether the benefit case is complete |
| `Q-02` | **Will the 9 named benefit owners sign their profiles?** (`BRP-09`) | Programme Director | W2 | Every accountability in §5 |
| `Q-03` | **Is `BEN-04`'s BDT 62 lac a redeployment or a headcount reduction?** (`DIS-03`) | HR Director with the Board | **W1** | The disbenefit's size, and the change narrative in `CH-001` |
| `Q-04` | **What is the `BEN-11` / `BEN-02` volume interaction?** Marketplace at 25% of jobs against a per-technician productivity benefit (`DIS-04`) | CCO with Ops Director | W6 | `AT-4` double-count prohibition; potentially both lines |
| `Q-05` | **When is the forward pass run** — testing all 79 specifications for unclaimed benefits and unnoticed disbenefits? (§3.3, §6.4) | Enterprise Architecture | W3 | Whether this map is complete |
| `Q-06` | **Is the branch-level series being retained from first go-live?** If not, `AT-2` is lost and cannot be recovered (`BRP-17`) | BI Lead | **Before W1 go-live** | Attribution for four benefit lines worth **BDT 312 lac** |

**Verification of `Q-06`'s exposure**: `BEN-01` 100 + `BEN-04` 62 + `BEN-05` 78 + `BEN-06` 72 =
**312 lac** ✓.

> `Q-03` and `Q-06` are escalated to `GV-005` at issue. `Q-06` has the shortest fuse in this
> document: it costs nothing to satisfy and cannot be recovered once missed.

---

## 14. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | All 14 benefit lines have a profile with all 17 fields | §4.1, §4.2, §4.3, §5.1 |
| `AC-02` | Profile values reconcile exactly to `06-02` §3.1 | §4.2's verification: 502 + 374 = 876 |
| `AC-03` | A disbenefits register exists with a schema and seeded entries | §6.2, §6.3 |
| `AC-04` | Every disbenefit is quantified or carries an owner and a date | §6.3, `BRP-12` |
| `AC-05` | A miss rule exists with thresholds, decision options, deciders and timescales | §9.2, §9.4, §9.5 |
| `AC-06` | The rule distinguishes a benefit miss from a programme failure | §9.3, `BRP-19` |
| `AC-07` | Every profile has a named attribution method | §8.2, `BRP-16` |
| `AC-08` | The ownership gap is counted, not asserted | §5.2, with commands |
| `AC-09` | The forecast/track separation is explicit and enforced | `BRP-15`, `BSC-20`, `PIR-25` |
| `AC-10` | Every seam names a contract and a direction | §10 |
| `AC-11` | Arithmetic totals verified from their own inputs (`PG-M10`) | **Four** `**Verification**` statements |
| `AC-12` | The document states what it cannot prove | §3.3 — the backward-constructed map |

**Definition of done.** Complete when every criterion is met, the 9 owners have signed under
`BRP-09`, `Q-01` and `Q-03` are answered, and `PGD-000`'s status is updated with a fresh enumeration
timestamp. **The plan becomes operative when the first baseline is signed** — until then all 14
lines sit in `A3` state 1.

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `06-02` §1, §3.1, §3.5, §6 | Objectives, benefit lines, owners and tracking discipline |
| Upstream | `BM-002` | Signed baselines; the claimability gate |
| Upstream | `BM-003` §6.2, §7 | The forecast this plan tracks against |
| Upstream | `RP-015` §4.8 | Per-line baseline position |
| Upstream | `CH-004` §8.1, §8.4 | Adoption thresholds and the handover |
| Downstream | `RL-005` §7 | `A3` content in five states |
| Downstream | `GV-009` | Gate benefit position; steady-state run-rate test |
| Downstream | `BM-005` | Missed benefits and miss decisions become lessons with landing sites |
| Downstream | `GV-005` | `DIS-nn` ↔ `RSK-nnn`; escalated questions |
| Lateral | `GV-006` `CC-05`, `CO-003` `SOW-54` | §9.6's benefit-statement content |
| Lateral | `GV-010` | Independent review of attribution and miss decisions |
| Lateral | `CO-005` §6.6, §7.3, §11 | `DIS-01`; option C's forgone benefit |
| Lateral | `RL-004` | The wave rollout that supplies `AT-2`'s control group |
| Lateral | `GV-011` | Register custody |

---

## 16. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./BM-002_KPI_Baseline_Measurement_Report.md` · `./BM-003_Business_Case_and_ROI_Model.md` ·
`./BM-005_Lessons_Learned_and_Continuous_Improvement_Register.md` ·
`../00_Programme_Governance_and_Control/GV-005_RAID_Register.md` ·
`../00_Programme_Governance_and_Control/GV-006_Scope_Management_and_Baseline_Control_Procedure.md` ·
`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md` ·
`../00_Programme_Governance_and_Control/GV-010_Programme_Assurance_and_Independent_Review_Plan.md` ·
`../12_Release_Deployment_and_Transition/RL-004_Rollout_and_Branch_Wave_Deployment_Plan.md` ·
`../12_Release_Deployment_and_Transition/RL-005_Post_Implementation_Review_Standard.md` ·
`../13_Training_Change_and_Adoption/CH-004_Adoption_Measurement_and_Reinforcement_Plan.md` ·
`../14_Commercial_Vendor_and_Contract/CO-003_Statement_of_Work_and_Deliverable_Acceptance_Schedule.md` ·
`../14_Commercial_Vendor_and_Contract/CO-005_Total_Cost_of_Ownership_Model.md`

**Workspace**
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` ·
`../../project_content/14_Reporting_Analytics_and_KPI/RP-015_Benefits_Realisation_and_KPI_Baseline_Register.md` ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md` §19

**External standards and sources**

| Source | Edition relied on | Verified |
|---|---|---|
| MSP — Managing Successful Programmes, benefits management theme | **5th edition**, PeopleCert | 2026-08-19 |
| ISO 21503 — Guidance on programme management | **2022** | 2026-08-19 |
| ISO 21502 — Guidance on project management | **2020** | 2026-08-19 |
| PMBOK Guide | **7th edition, 2021** | 2026-08-19 |
| ISO 9001 — Quality management systems, §9.1 and §9.3 | **2015** | 2026-08-19 |
| ISO/IEC/IEEE 15939 — Measurement process *(via `BM-002`)* | **2017** | 2026-08-19 |

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Enterprise Architecture for the Programme Director | Initial issue. Converts 14 benefit lines into 14 profiles with outputs, outcomes, objectives, adoption dependencies and attribution methods. **Creates the disbenefits register** — a concept absent from all 784 files (`BRP-F-01`) — with 8 seeded entries. **Establishes the miss rule** the register names as this document's reason for existing: three bands, five decisions, and the prohibition on "accept and continue" (`BRP-20`). Counts the **objective-versus-benefit ownership gap** (`BRP-F-02`). Identifies **`AT-2` staggered-rollout attribution** as a free control group that expires at W5. Recomputed at audit: `DIS-01` restated to `CO-005`'s revised Tier 2 internal-resource figure ($660K → $681K). Six new findings `BRP-F-01`…`BRP-F-06` | ERP Steering Committee |

---

*`BM-004` · Category 15 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
