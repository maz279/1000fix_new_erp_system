---
id: CH-004
title: Adoption Measurement and Reinforcement Plan
category: 13 — Training, Change & Adoption
code: CH
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Change Lead with the PMO
approver: Chief Executive Officer with the ERP Steering Committee
standards_basis: >
  New World Kirkpatrick Levels 3 and 4 with Required Drivers · ACMP Standard for Change Management
  Version 2 (26 August 2025), process groups 4 and 5 — execute and complete the change management
  effort · ISO 21502:2020 §7.13 (benefits management) · ISO 21503:2022 (programme management —
  benefits) · ISO 9001:2015 clause 9.1 (monitoring, measurement, analysis and evaluation) ·
  Bangladesh Personal Data Protection Act 2026 (PDPA) — lawful basis and purpose limitation for
  workforce monitoring
traces_to: >
  PGD-000 CH-004 · AUDIT-019 CM-05 (the register commissions a prohibited leaderboard), CM-06,
  CM-01 · AUDIT-015 RP-01, RP-02 · M57 BRU-PIC-14, BRU-PIC-16 · CM-016 UP-01…UP-17 ·
  CM-017 RN-08, RN-14 · 00-04 §5.5, RSK-008, RSK-010, RSK-012 · 04-00 portal adoption targets ·
  06-02 §4 gate criteria, §6 benefit tracking discipline
depends_on: CH-001 · CH-002 · CH-003 · BM-002 (absent) · BM-004 · RP-015
verified_on: 2026-08-19
priority: P1
needed_by: W2
enumeration_timestamp: 2026-08-19 01:20 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# CH-004 — Adoption Measurement and Reinforcement Plan

### Category 13 · Code `CH` · Kirkpatrick Levels 3–4 · ACMP v2 process groups 4–5 · ISO 21502:2020 §7.13 · ISO 21503:2022 · ISO 9001:2015 §9.1

---

> **Local rule prefix: `ADP-nn`.** Verified to return **zero** occurrences workspace-wide before
> allocation, at 2026-08-19 01:20 (+06).

---

## 1. Purpose

`00-04` §5.5 requires *"weekly usage reporting by role and branch; intervention where adoption
lags."* `06-01` §7 repeats it. `CM-016` supplies the campaign content and an eighteen-row adoption
target register. **What none of them supplies is the measurement instrument, the baseline, or the
authority to intervene.**

This plan supplies those three things, and it opens with the two facts that constrain everything
in it:

> **Fact 1 — most of the targets cannot currently be assessed.** `CM-016` `UP-02` records that
> **ten of eighteen** adoption target rows have **no baseline value in the specification**.
> `AUDIT-015` `RP-02`, rated **CRITICAL**, records the wider position: **44 of 95 registered KPIs
> have no usable baseline.** `06-02` §6 states the programme's own rule — *"a KPI without a baseline
> cannot claim a benefit"* — which places roughly **BDT 396 lac of an BDT 876 lac benefit case
> outside what can be claimed**. `BM-002`, the KPI Baseline Measurement Report, is **⛔ and
> unwritten**.
>
> **Fact 2 — the register commissions an adoption mechanism the system prohibits.** The Master
> Index row for `CM-017` reads *"copy for adoption recognition, **leaderboards**, milestones and
> incentive announcements."* `M57` §9 `BRU-PIC-16` is a **Class `H` hard block** owned by the Chief
> Data Officer: *"Peer comparison is anonymised; no employee sees another employee's individual
> score."* **`M57` provides no waiver route.** `AUDIT-019` `CM-05` is open, and the register row is
> uncorrected.

### 1.1 Scope

**In scope:**

| # | Covered |
|:--:|---|
| 1 | The adoption measurement model: unit, grain, cadence, denominator, and the definition of "active" |
| 2 | The **baseline capture protocol** — what must be measured before each wave, by whom |
| 3 | Adoption metrics **per role and per branch** for internal populations, and per segment for external |
| 4 | The **intervention ladder** and the authority attached to each step |
| 5 | **Reinforcement** — the Kirkpatrick Required Drivers, made into a schedule with owners |
| 6 | The **permitted recognition patterns** and the prohibition that bounds them |
| 7 | The workforce-monitoring boundary: lawful basis, purpose limitation and disclosure |
| 8 | Sustainment, stop conditions, and the handover to `BM-004` benefits realisation |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| Campaign copy, audience messages, opt-out wording | `CM-016`, `CM-017` | Content, governed by `CG-*` (`CP-01`) |
| The KPI register itself and its baselines | `BM-001` (`06-02`), `BM-002` ⛔ | This plan consumes baselines; `BM-002` produces them |
| Benefit ownership, realisation curve, NPV | `BM-003`, `BM-004` | Adoption is a leading indicator of benefit, not the benefit |
| Change impact, sponsorship, resistance response | [`CH-001`](CH-001_Organisational_Change_Management_Plan.md) | |
| Training delivery and Kirkpatrick Levels 1–2 | [`CH-002`](CH-002_Training_Plan_and_Delivery_Schedule.md) §8.5 | Levels 3 and 4 are here; 1 and 2 are there |
| Stakeholder register, calendar, channel rules | [`CH-003`](CH-003_Stakeholder_Engagement_and_Communication_Plan.md) | |
| Product instrumentation design | `AR-001`, portal specifications | This plan states what must be measurable; it does not design the telemetry |
| Incentive scheme design and approval | `M57`, HR Director with CFO (`BRU-PIC-01`) | Recognition ≠ incentive |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **ERP Steering Committee** | The intervention ladder's step 6 — the authority to pause a rollout — and the monthly worst-performer report |
| Change Lead, PMO | The operating instrument |
| **Chief Data Officer** | The `BRU-PIC-16` boundary and the register row that breaches it |
| HR Director | Recognition patterns, the monitoring boundary, and the W1–W5 gap |
| Portal squads | Which adoption failures are product findings and arrive as such |
| Business owners | The Level 4 measure their module's training targets |
| Branch managers | Their site's adoption position and what triggers a conversation |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this document conforms | Departure |
|---|---|---|---|
| **New World Kirkpatrick** | **Level 3 Behaviour** — sustained by Required Drivers, not by hope; **Level 4 Results** — defined first, worked backwards | §5 measurement model; §7 Required Drivers with named owners and a schedule | **Declared, inherited from `TR-001` `LS-16`:** no causal attribution is claimed at Level 4. A campaign claims a change **only against a pre-campaign trend, never against zero** (`UP-03`) |
| **ACMP Standard for Change Management v2** (26 Aug 2025) | Process group 4 — execute; process group 5 — **complete the change management effort**, including sustainability | §6 intervention; §8 sustainment and handover | None |
| **ISO 21502:2020** | §7.13 benefits management — identify, define, plan, monitor, sustain | §5 monitoring; §8.4 handover to `BM-004` | None |
| **ISO 21503:2022** | Programme management — benefits realisation across component projects | §8.4 — nine waves each producing a partial benefit | None |
| **ISO 9001:2015** | Clause 9.1 — monitoring, measurement, analysis and evaluation: *what*, *by which methods*, *when*, *when the results shall be analysed* | §5.1's four-column measurement definition answers all four | None |
| **Bangladesh PDPA 2026** | Lawful basis; purpose limitation; transparency | §9 monitoring boundary | `RSK-032` rates non-compliance **Critical**, with enforcement around **13 May 2027 — inside Wave 4** |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `CM-016` §4.1–4.10 | `../../project_content/16_Change_Management_and_Comms/CM-016_Adoption_Campaign_Content.md` | The eighteen-row adoption target register; the six diagnostic questions; the intervention ladder; consent rules; stop conditions; `UP-01`…`UP-17` |
| `CM-017` §4.2–4.9 | `.../CM-017_Recognition_Incentive_and_Gamification_Copy.md` | The four recognition surfaces; **the four permitted comparison patterns**; the monitoring boundary; `RN-08`, `RN-14` |
| `04-00` | `../../1000fix_ERP_Module/04_Portals_and_Applications/` | Per-portal adoption targets and design KPIs |
| `06-02` §2, §4, §6 | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` | The 95-KPI register; gate criteria; **benefit tracking discipline, including the baseline rule** |
| `00-04` §5.5, §1.2 | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-04_Risks_Assumptions_Dependencies_and_Governance.md` | *"Weekly usage reporting by role and branch; intervention where adoption lags"*; the five adoption risks |
| `06-01` §9 | `.../06-01_Implementation_Roadmap_and_Phasing.md` | The contingency that step 6 of the ladder invokes |
| `M57` §9 | `../../1000fix_ERP_Module/03_Modules/` | `BRU-PIC-14` (performance ratings are sensitivity class `S2`); **`BRU-PIC-16` Class `H` peer-comparison block** |
| `RP-015` | `../../project_content/14_Reporting_Analytics_and_KPI/` | Baseline register — **44 of 95 KPIs with no usable baseline** |
| `AUDIT-015`, `AUDIT-019` | `../../project_content/_AUDIT/` | `RP-01`, `RP-02` (both CRITICAL); `CM-05`, `CM-06`, `CM-01` |

**Enumeration** at **2026-08-19 01:20 (+06)**, per `OCM-02`.

### 2.3 Audit findings this document treats

| Finding | Source | Severity | Treatment |
|---|---|:--:|---|
| **`CM-05`** — the register commissions a leaderboard `BRU-PIC-16` prohibits | `AUDIT-019` | High | §7.3 states the prohibition and the four permitted substitutes as **governing rules of this plan**, and §7.4 assigns the register correction. **Closure requires the register row to change**, which is `AUDIT-019` `R-04` |
| **`RP-02`** — 44 of 95 KPI baselines absent | `AUDIT-015` | **CRITICAL** | §4 makes baseline capture a **gate precondition**, not a reporting preference, and names what must be captured before W1 |
| **`RP-01`** — 250 KPI identifiers in use against 95 registered | `AUDIT-015` | **CRITICAL** | `ADP-03`: this plan cites only registered `06-02` KPI identifiers and invents none. Reconciliation is `BM-001`/`RR-002`'s |
| `CM-06` — the `RSK-008` mitigation arrives three waves after the risk | `AUDIT-019` | High | §7.5 — the W1–W5 recognition surfaces that exist, and what they cost |
| `CM-01` — the category was authored against a stale register | `AUDIT-019` | **CRITICAL** | `ADP-02` and the enumeration note above |
| `UP-02` — ten of eighteen targets have no baseline | `CM-016` `O-01` | — | §4.2 |

---

## 3. What Adoption Is, and What It Is Not

**`ADP-01`: adoption is the *use of the system in the way the process requires*, measured on the
product's own instrumentation. It is not logins, not training completion, and not satisfaction.**

| Not adoption | Why it is measured anyway | Where it belongs |
|---|---|---|
| Logins | Access provisioning worked | `M29` operational reporting |
| Training completion | A precondition, and a `CU-03`/`CU-05` access gate | `CH-002` §8; Kirkpatrick Level 2 |
| Satisfaction | Diagnostic, never an outcome (`LS-02`) | Kirkpatrick Level 1 |
| Messages sent | Not a measure at all (`SEP-20`) | — |
| **Transactions completed in the system, by the role the process assigns, within the process's own tolerance** | **This is adoption** | This plan |

### 3.1 The distinction that governs the whole plan

> **`ADP-02` — a missed adoption target is diagnosed before a campaign is commissioned, and only
> one of the six diagnostic outcomes is answered by a campaign.**

`CM-016` §4.2's six questions are adopted unchanged and are the entry point to every intervention:

| # | Question | If yes | Owner |
|:--:|---|---|---|
| 1 | **Can they reach it?** Access, device, connectivity, literacy | Fix access. **Not a campaign** | IT / Operations |
| 2 | **Do they know it exists?** | **Campaign** — the awareness case | Marketing |
| 3 | **Can they complete it?** Funnel completion by step | **Product finding** → portal squad. Not a campaign | Portal squad |
| 4 | **Is it faster than what they do now?** | **Process or design finding.** Campaigning against a slower alternative fails | Business Process |
| 5 | **Are they worse off if they use it?** | **`Interest` objection** → escalate ([`CH-001`](CH-001_Organisational_Change_Management_Plan.md) `OCM-18`) | Change Lead → Steering |
| 6 | **Is someone telling them not to?** | Management or intermediary issue | Operations / Commercial |

> **`UP-04`, restated because it is the most-ignored rule in adoption practice:** only question 2 is
> answered by a campaign. `P01`'s primary design KPI is booking-funnel conversion above **72%**; if
> conversion is below that, more traffic increases abandonment and nothing else.

---

## 4. Baselines — The Precondition

ISO 21502:2020 §7.13 and `06-02` §6: *"Every KPI's baseline is measured and signed off **before**
the relevant wave begins. A KPI without a baseline cannot claim a benefit."*

### 4.1 The position today

| Fact | Figure | Source |
|---|---:|---|
| Registered KPIs in `06-02` | **95** | `06-02` §2 |
| **KPIs with no usable baseline** | **44** | `RP-015`; `AUDIT-015` `RP-02`, **CRITICAL** |
| KPI identifiers actually in use across the estate | **250** | `AUDIT-015` `RP-01`, **CRITICAL** |
| Adoption target rows in `CM-016` §4.1 | 18 |
| **Adoption rows with no baseline value** | **10** | `CM-016` `UP-02` |
| `BM-002` KPI Baseline Measurement Report | **⛔ unwritten** | `PGD-000` Category 15 |
| Benefit case placed outside what can be claimed | **~BDT 396 lac of BDT 876 lac** | `AUDIT-015`; `PGD-000` Category 15 |

### 4.2 The ten adoption targets with no baseline

Taken from `CM-016` §4.1. **`ADP-04`: a target with no captured baseline is not campaigned against
and is not reported as met or missed** (`UP-02`).

| Portal / audience | Target | Baseline | Gate criterion |
|---|---|---|:--:|
| `P01` Customer — self-service status checks | > 80% of enquiries | **~0, unmeasured** | — |
| `P01` Customer — portal MAU | > 120,000 | **absent** | — |
| `P02` Technician — daily active use | **> 95% of active technicians** | **0** | **`G2-01`** |
| `P04` Corporate — contracted clients active | > 85% | **0** | **`G4-05`** |
| `P04` Corporate — requests via portal | > 70% | **0** | — |
| `P05` Vendor — POs acknowledged | **> 90%** | **0** | — |
| `P06` Analytics — weekly manager usage | > 90% | **0** | `G4-09` |
| `P07` Seller — onboarding completion | > 60% of started registrations | **absent** | **`G7-01`** |
| `P09` Rider — POD capture completeness | 100% | **absent** | — |
| `P12` Partner — portal adoption | > 75% of approved partners | **absent** | — |

> **Four of the ten carry a gate criterion.** A Go/No-Go decision that turns on a percentage with
> no measured starting point is a decision taken on an unverifiable number. `G2-01` — *100% of
> Dhaka technicians in daily use* — is an **absolute** criterion and therefore assessable without a
> baseline; `G4-05`, `G4-09` and `G7-01` are not.

### 4.3 The baseline capture protocol

**`ADP-05`: a baseline is captured before the wave, on a stated method, on a stated date, by a
named person, and is not re-derived afterwards.**

| Element | Requirement |
|---|---|
| **When** | **Wave start minus 8 weeks**, before any communication that could change behaviour |
| **What** | The same measure, on the same denominator, that the target will be assessed on |
| Method | Stated per measure: system extract, manual count, timed observation, or sample survey — with the sample size |
| **Denominator** | **Stated with every figure, always** (`UP-05`, `NL-07`, `EP-05`) |
| Owner | The KPI's benefit owner (`06-02` §3.5); the Change Lead where none is named |
| Signature | Benefit owner + PMO, recorded in `BM-002` when it exists, and in a controlled register under `GV-011` until then |
| **Where no baseline is possible** | The measure is declared **relative** — improvement against a first-30-days trend — and the absolute target is **not** claimed. Recorded as a decision, not as an omission |

### 4.4 The W1 baseline set — what must be measured now

These are the measures whose baselines expire the moment W1 communication starts:

| # | Measure | Method | Owner | By |
|:--:|---|---|---|---|
| 1 | **Walk-in intake time**, paper process, 20 timed samples per pilot site | Timed observation | Operations Director | **W1 − 8 weeks** |
| 2 | **Technician task completion time on paper**, per job type | Timed observation, ≥ 30 jobs | Operations Director | **W2 − 12 weeks** — this is `CH-001` §9.2's pilot baseline |
| 3 | Online booking share | System/manual count | Marketing | W1 − 8 weeks |
| 4 | Service-order cycle time, current | Legacy extract | Business Process | W1 − 8 weeks |
| 5 | Support contact volume and top-ten topics, current | Manual log | Support Lead | W1 − 8 weeks |
| 6 | Manual report production hours, per manager per month | Self-report survey | PMO | W1 − 8 weeks — the `RSK-012` baseline |

> **`ADP-06` — measure 2 is the one that cannot be recovered.** Once technicians hold `P02`, the
> paper baseline is gone, and `GV-005`'s stated trigger for the programme's Critical adoption risk
> — *"field-pilot task completion slower than paper"* — becomes unevaluable. It is the adoption
> equivalent of `MG-002` `LPX-32`: **a measurement window that closes and does not reopen.**

---

## 5. The Measurement Model

### 5.1 Definition — ISO 9001 clause 9.1

Every measure in this plan is defined on four columns, because clause 9.1 asks four questions.

| Column | Clause 9.1 question |
|---|---|
| **Measure and denominator** | What needs to be monitored and measured |
| **Method** | By which methods |
| **Cadence** | When the monitoring shall be performed |
| **Analysis point** | When the results shall be analysed and evaluated |

### 5.2 Grain and cadence

`00-04` §5.5 requires *"by role and branch"*. **`ADP-07`: internal adoption is reported by role and
by branch; external adoption by segment and cohort. A programme-level percentage is not a
management instrument** — it hides the site that has not started.

| Population | Grain | Cadence | Analysis point |
|---|---|---|---|
| Internal | **Role × branch** | **Weekly during rollout**, monthly thereafter | Monthly `CM-004` §5, **worst performer first** (`EP-06`) |
| External | Segment × cohort | Weekly in the wave, monthly thereafter | Monthly |
| Gate criteria | Per criterion | At the gate | Steering Go/No-Go |
| Level 3 behaviour | Per role, sample | Per pack schedule | Per wave |

### 5.3 "Active" is defined once

> **`ADP-08` — the definition of "active" is written once per portal, published, and changed only
> by a recorded decision** (`UP-05`). *The single easiest way to meet an adoption target is to
> redefine active.*

| Portal | Proposed definition of active | Denominator |
|---|---|---|
| `P01` Customer | A booking, a status check or a document download in the period | Registered customers with a service event in the period |
| **`P02` Technician** | **At least one job accepted, updated and closed on device** on a working day | Technicians rostered on that day (**not** all technicians) |
| `P03` Admin | A transaction, not a login, in the period | Rostered staff in the role |
| `P04` Corporate | A request raised or an SLA view, per user | Users provisioned under an active contract |
| `P05` Vendor | A PO acknowledged, an invoice submitted or an RFQ answered | Vendors with an open PO in the period |
| `P06` Analytics | A dashboard opened **and** used in a decision meeting | Managers with a branch or function |
| `P07` Seller | A job accepted in the period | Approved sellers |
| `P09` Rider | POD captured on device for every assigned delivery | Riders rostered |
| `P11` Auditor | An audit completed on device | Scheduled audits |

> **`ADP-09` — the denominator is rostered population, not headcount.** A technician on leave who
> did not use `P02` is not a non-adopter. Measuring against headcount understates adoption, invites
> pressure to redefine the numerator, and is the most common way an adoption report loses
> credibility with operations.

### 5.4 Attribution

**`ADP-10`: a campaign or intervention claims a change only against a pre-intervention trend,
never against zero, and never claims causation the data does not support** (`UP-03`, `LS-16`).

---

## 6. Intervention

`00-04` §5.5 requires *"intervention where adoption lags"*. `CM-016` §4.7's ladder is adopted, and
**this plan attaches the authority to each step**, which the content file could not.

| Step | Trigger | Action | Owner | **Authority required** |
|:--:|---|---|---|---|
| 1 | A role or site below target for **2 weeks** | **Diagnose** per §3.1's six questions | Change Lead | None — this is routine |
| 2 | Awareness gap confirmed (question 2) | Targeted campaign to that audience only | Marketing | Campaign budget |
| 3 | Capability gap confirmed (question 1) | Refresher training; job aid (`TR-024`, `TR-022`) | L&D | Trainer time — **which does not exist** (`CH-002` §7) |
| 4 | Funnel or product gap confirmed (question 3) | **Product finding to the squad**, naming the step and the drop rate | Portal squad | Sprint capacity |
| 5 | Local management gap confirmed (question 6) | Branch manager conversation | Operations Director | Line authority |
| 6 | **Below target at the gate** | **`06-01` §9 contingency — pause rollout, diagnose, remediate, re-pilot** | **Steering Committee** | **Go/No-Go authority** |

> **`ADP-11` — step 6 is a real option, and it is stated so that steps 1 to 5 are taken
> seriously.** `06-01` §9 already provides it. A programme that never uses it has decided adoption
> is negotiable, and every step below it becomes advisory.

### 6.1 The external risks

| Risk | Rating | Intervention position |
|---|:--:|---|
| **`RSK-010` Marketplace sellers fail to adopt** | High | The stated mitigations — simple onboarding, fast transparent payouts, clear scoring, a seller advisory group — are **product and commercial levers, not campaign levers** (`UP-07`). The seller advisory group has no owner and no date: `ADP-Q-04` |
| `RSK-008` Technician rejection | **Critical** | `CH-001` §9.2; §7.5 below for the W1–W5 surface gap |
| `RSK-012` Management reversion | High | §7.6 — withdrawal of the alternative, after the replacement is proven |

### 6.2 Stop conditions

`CM-016` §4.8's `UP-17` is adopted: a campaign stops when its target is met, when its diagnosis is
disproved, or when it is doing harm.

| Stop condition | Signal |
|---|---|
| Target met and held for **four weeks** | The measure |
| **Diagnosis disproved** | Awareness rises, adoption does not — the problem was question 3, 4 or 5 |
| Opt-out rate rising | Over-contact |
| Complaint volume rising | Reaching people who should have been suppressed |
| **Hypercare open at the target sites** | `UP-15` — no campaign runs during hypercare |
| Consent basis in question | **Immediate stop pending Legal** |

---

## 7. Reinforcement

Kirkpatrick's Required Drivers are the part of the model organisations skip, and `TR-001` §4.3
names four with owners. **This plan turns them into a schedule.**

### 7.1 The four drivers, scheduled

| Driver | Mechanism | Owner | Cadence | Owning artefact |
|---|---|---|---|---|
| **Reinforce** | Job aids at the point of work; in-app guidance; the technician card set | L&D with Content Design | Available from T−1 week; refreshed per release | `TR-022`, `KB-016` |
| **Encourage** | Champions and super-users on the floor | L&D with Change | **The two weeks after each wave go-live**, then monthly forum for the programme's duration | [`CH-005`](CH-005_Super_User_and_Champion_Network_Charter.md), `CM-008` |
| **Monitor** | On-the-job observation against the pack's behaviour criteria; system signals — override rates, error rates, help-desk topics | Line managers with L&D | Per pack schedule; system signals weekly | `TR-004`; `M22` FR-LMS-035 |
| **Reward** | Certification recognised in `MD-011`; competence gating access and assignment; **recognition within §7.3's permitted patterns** | HR with Quality | Monthly | `TR-004`, `M57`, `CM-017` |

> **`ADP-12` — a course or a wave with no named Required Driver for each of the four is not
> complete** (`LS-04`). Level 3 behaviour is not sustained by the training event; it is sustained by
> these four, and they are the first things dropped when the programme is busy.

### 7.2 Sustainment after hypercare

| Element | Requirement |
|---|---|
| Trigger to begin | Hypercare exited |
| Duration | **Until the adoption measure has held for four weeks** *and* the wave gate has passed |
| Withdrawal of floor support | Tapered, not stopped: full presence week 1–2, on-call weeks 3–4, champion-only thereafter |
| Refresher trigger | Adoption falling below target for two consecutive weeks after sustainment begins → ladder step 3 |
| **Handover** | §8.4 |

### 7.3 Recognition — the boundary

> **`ADP-13` — no surface, in any language, at any time, displays one employee's individual score
> to another employee.** `M57` §9 `BRU-PIC-16` is a **Class `H` hard block** owned by the Chief
> Data Officer, and **`M57` provides no waiver route**. `BRU-PIC-14` additionally classifies
> performance ratings as sensitivity class `S2`.

**The four permitted comparison patterns**, taken from `CM-017` §4.5 and adopted here as governing
rules of this plan:

| # | Permitted pattern | Why it is permitted |
|:--:|---|---|
| 1 | **Own trend** — this week against your own last four weeks | No other person's data is shown |
| 2 | **Own position against an anonymised distribution** — "you are in the top quartile" | The distribution is anonymised; `BRU-PIC-16`'s condition is met |
| 3 | **Own position against target** | No comparison to a person at all |
| 4 | **Team or site comparison** | The unit is a team, not a person. **`P06`'s branch league already does this by design** |

| # | Prohibited | Rule |
|:--:|---|---|
| 1 | A named individual leaderboard, on any surface, in any language | `BRU-PIC-16`, `RN-08` |
| 2 | Ranking champions against each other | `NW-11`, `CNC-11` |
| 3 | A "bottom performers" list of any kind | `BRU-PIC-16` |
| 4 | Individual adoption percentages visible to peers | `BRU-PIC-16` |

> **`ADP-14` — team recognition is the designed substitute, not a consolation** (`RN-14`). It is
> also better change practice: at 51+ sites the unit that actually adopts or fails to adopt is the
> site, not the individual.

### 7.4 The register row that must change

**`AUDIT-019` `CM-05` is open and the register row is uncorrected.**

| Element | Position |
|---|---|
| The row | Master Index, `CM-017`: *"copy for adoption recognition, **leaderboards**, milestones and incentive announcements"* |
| The prohibition | `M57` §9 `BRU-PIC-16`, Class `H`, no waiver route |
| What `CM-017` did | `RN-08` prohibits individual leaderboards on any surface in any language, and §4.5 supplies the four substitutes |
| **What remains open** | **The register still commissions the prohibited artefact.** `AUDIT-019` `R-04`: correct the row to remove *"leaderboards"* or qualify it as team-level. Owner: Programme Content Lead with the CDO, by W2 |

> **`ADP-15` — a register row that commissions a prohibited artefact will be honoured by someone
> eventually.** The content file's refusal protects this wave; the register row is what the next
> author reads. Carried as `ADP-Q-01`.

### 7.5 The W1–W5 recognition gap

`AUDIT-019` `CM-06`, and [`CH-001`](CH-001_Organisational_Change_Management_Plan.md) §9.2.4. From
the measurement side:

| Artefact | Wave | Consequence |
|---|:--:|---|
| `P02` technician app; `RSK-008` materialises | **W2** | The risk arrives |
| `CM-017` recognition and incentive copy | **W2** | The copy exists |
| **`M57` incentive engine and scorecard** | **W5** | **The surface does not** |
| `M21` HR / salary of record | **W5** | " |

**Between W2 and W5 the only available reinforcement surfaces are:**

| Surface | Available? | Cost |
|---|:--:|---|
| `CM-017` §4.6 named public recognition | ✔ | **No budget** (`CM-017` `O-06`) |
| `CM-017` §4.5 pattern 4 — team or site comparison | ✔ | Requires `P06` branch data at W2; `P06` is W4 |
| Pattern 1 — own trend | **✘ before `M57`** | Requires the scorecard `CH-001` §9.2.4 option A would build |
| Certification recognition in `M22` | ✔ | Available from W1 |
| Champion recognition at the forum | ✔ | `CH-005` §8 |

> **`ADP-16` — the measurement consequence of the gap is that `RSK-008`'s named mitigation cannot
> be *measured* between W2 and W5, not merely that it cannot be delivered.** If option A is taken,
> the minimum scorecard is also the instrument that measures whether visibility affects adoption.
> If option B is taken, the programme must accept that it will not know.

### 7.6 `RSK-012` — withdrawal as reinforcement

**`ADP-17`: the alternative is withdrawn only after the replacement is proven** (`UP-08`).
Withdrawal before capability is coercion and produces shadow spreadsheets rather than adoption.

| Step | Condition | Owner |
|:--:|---|---|
| 1 | `G4-09` dashboard gate criterion met and evidenced | PMO |
| 2 | Four weeks of parallel running, dashboards and manual packs both available | Business owners |
| 3 | `P06` weekly manager usage above 90% for four consecutive weeks | Change Lead |
| 4 | **Source data for manual packs withdrawn** | CEO, executed by Operations Director |
| 5 | Decisions required to cite the dashboard | Steering |

`G2-09` — withdrawal of paper service forms in Dhaka — is the same pattern as a **gate criterion**,
and is the precedent.

---

## 8. Sustainment, Stop and Handover

### 8.1 What "adopted" means

**`ADP-18`: a wave's adoption is complete when its measure has met target for four consecutive
weeks, at role and branch grain, with the worst-performing site above the floor.** A programme
average above target with one site at zero is not adoption; it is arithmetic.

| Element | Requirement |
|---|---|
| Target | Per `CM-016` §4.1 / `04-00`, quoted never invented (`UP-01`) |
| Duration held | **4 consecutive weeks** |
| Grain | Role × branch |
| **Floor** | **No site below 70% of target** — declared planning threshold, reviewable |
| Evidence | Product instrumentation (`PS-10`), not a survey (`UP-03`) |

### 8.2 Stop conditions for measurement itself

**`ADP-19`: measurement stops when the behaviour is business-as-usual, and the measure moves to
standing operational reporting — it is not measured by the programme for ever.** Otherwise the
adoption report becomes a permanent programme artefact nobody reads.

### 8.3 Reporting

| Report | Audience | Cadence | Content |
|---|---|---|---|
| Adoption dashboard | Change Lead, PMO | Weekly in rollout | Role × branch, worst first |
| **`CM-004` §5 Steering section** | Steering Committee | **Monthly** | **Worst-performing audience, with the §3.1 diagnosis and the requested intervention** |
| Gate adoption position | Steering | At the gate | Every gate criterion with a measured value and its denominator |
| Branch manager view | Branch managers | Weekly in wave | Their own site, and the anonymised distribution (`ADP-13` pattern 2) |
| Benefits input | `BM-004` | Quarterly | §8.4 |

### 8.4 Handover to benefits realisation

ACMP process group 5; ISO 21503:2022.

| Element | Requirement |
|---|---|
| Trigger | §8.1 satisfied for the wave |
| Receiving artefact | **`BM-004` Benefits Realisation Plan** (◐), which names benefit owners and the decision rule when a benefit misses |
| Transferred | The measure, its definition, its denominator, its baseline, its current value and its owner |
| **Constraint** | **`06-02` §6: a KPI without a baseline cannot claim a benefit.** Forty-four of ninety-five currently cannot. `BM-002` ⛔ is the blocker |
| Not transferred | Any measure whose definition of "active" changed during the wave without a recorded decision (`ADP-08`) |

---

## 9. The Monitoring Boundary

Adoption measurement of a workforce is workforce monitoring, and it is the subject of the
programme's most sensitive open objection.

> **`ADP-20` — no adoption measure is collected without a recorded lawful basis, a stated purpose,
> and a disclosure the affected population has actually received.**

| Element | Requirement | Status |
|---|---|---|
| Lawful basis | Recorded per processing purpose under the PDPA 2026 | ⬜ `RSK-032` **Critical**; enforcement ~**13 May 2027, inside W4** |
| Purpose limitation | Adoption data is used for adoption intervention, **not** for individual performance management, unless a separate basis and disclosure exist | `BRU-PIC-14` class `S2` |
| **Disclosure** | `LG-020` §4.6 — **the disclosure exists**; `LG-020` `AU2` is the open question, and it **blocks `P02` go-live disclosure** | ⛔ `CH-001` §6.5 position 3 |
| Transparency to the individual | A technician can see what is measured about them, in Bengali | `CM-017` §4.7 |
| DPIA | [`SC-003`](../05_Security_Privacy_and_Compliance/SC-003_Data_Protection_Impact_Assessment_PDPA_2026.md) | ✅ **Issued.** Corrected at issue — this row read *"⛔ unwritten"* in draft. `ADP-Q-08`: confirm that `SC-003` covers **workforce adoption telemetry** as a processing purpose, and not only customer data |
| Retention | Per `GV-011` and the data-retention schedule | |

> **`ADP-21` — an adoption measure whose disclosure is unresolved is not collected, even if the
> instrumentation exists.** The population whose adoption the programme most needs is the
> population whose stated objection is *being monitored* (`CM-002` `S07`). Collecting the data
> before the disclosure is settled converts a Critical adoption risk into a Critical compliance
> risk, and does not improve adoption.

---

## 10. Governing Rules

| # | Rule | Class |
|---|---|:--:|
| `ADP-01` | Adoption is use of the system as the process requires, on the product's own instrumentation — not logins, training completion or satisfaction | **H** |
| `ADP-02` | A missed target is diagnosed through the six questions before a campaign is commissioned; only the awareness case is answered by a campaign | **H** |
| `ADP-03` | Only KPI identifiers registered in `06-02` are cited; none is invented | **H** |
| `ADP-04` | A target with no captured baseline is not campaigned against and is not reported as met or missed | **H** |
| `ADP-05` | A baseline is captured before the wave, on a stated method and date, by a named person, and is not re-derived afterwards | **H** |
| `ADP-06` | Measures whose baseline window closes at go-live are captured first, and their expiry is stated | **H** |
| `ADP-07` | Internal adoption is reported by role and branch; a programme-level percentage is not a management instrument | **H** |
| `ADP-08` | "Active" is defined once per portal, published, and changed only by a recorded decision | **H** |
| `ADP-09` | The denominator is the rostered population, not headcount, and is stated with every figure | **H** |
| `ADP-10` | A change is claimed only against a pre-intervention trend, never against zero, and no causation is claimed that the data does not support | **H** |
| `ADP-11` | Step 6 of the ladder — pause, diagnose, remediate, re-pilot — is a real option, exercised by the Steering Committee | **H** |
| `ADP-12` | A wave with no named Required Driver for reinforce, encourage, monitor and reward is not complete | **H** |
| `ADP-13` | **No surface displays one employee's individual score to another employee** (`BRU-PIC-16`, Class `H`, no waiver route) | **H** |
| `ADP-14` | Team recognition is the designed substitute, not a consolation | **H** |
| `ADP-15` | A register row commissioning a prohibited artefact is corrected, not merely refused in the content file | **H** |
| `ADP-16` | Where a mitigation's surface does not exist, the plan records that the mitigation cannot be measured, not only that it cannot be delivered | **H** |
| `ADP-17` | The alternative is withdrawn only after the replacement is proven | **H** |
| `ADP-18` | A wave is adopted when its measure holds for four consecutive weeks at role × branch grain with no site below the floor | **H** |
| `ADP-19` | Measurement stops at business-as-usual and moves to standing operational reporting | **S** |
| `ADP-20` | No adoption measure is collected without a recorded lawful basis, a stated purpose and a received disclosure | **H** |
| `ADP-21` | An adoption measure whose disclosure is unresolved is not collected, even where the instrumentation exists | **H** |
| `ADP-22` | No campaign runs during hypercare at the affected sites (`UP-15`) | **H** |
| `ADP-23` | Every external campaign message requires a lawful basis and a consent state checked **at send** (`UP-09`, `UP-10`) | **H** |
| `ADP-24` | Opt-out is immediate and cross-channel, and carried in both languages (`UP-11`, `UP-12`) | **H** |

---

## 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `ADP-Q-01` | **Correct the `CM-017` register row** to remove *"leaderboards"* or qualify it as team-level | **Programme Content Lead with the CDO** | **W2** | `AUDIT-019` `CM-05`/`R-04`; the next author to read the row |
| `ADP-Q-02` | **Who captures the six W1 baselines in §4.4, and is it funded?** Two of the six expire permanently at go-live | **PMO with the Operations Director** | **W1 − 8 weeks; measure 2 by W2 − 12 weeks** | `G2-01`, `G4-05`, `G4-09`, `G7-01`; `RSK-008`'s own trigger |
| `ADP-Q-03` | `BM-002` KPI Baseline Measurement Report is ⛔ unwritten and **44 of 95 baselines are absent**. When is it authored? | CFO with the PMO | **Now** — `PGD-000` Category 15 marks it `P0`/Now | Every benefit claim; `06-02` §6 |
| `ADP-Q-04` | `RSK-010`'s **seller advisory group** has no owner and no date | CCO with Marketplace Ops | W7 − 16 weeks | A High risk with an unscheduled mitigation |
| `ADP-Q-05` | Is the campaign budget funded, and does it include the `CM-017` §4.6 named-recognition surface that currently has none? | HR Director with CFO | W2 | Ladder steps 2 and 3; §7.5 |
| `ADP-Q-06` | **`LG-020` `AU2`** — the monitoring disclosure question that blocks `P02` go-live | Legal Counsel with the DP Forum | **W2 − 8 weeks** | `ADP-21`; every technician adoption measure |
| `ADP-Q-07` | Is the site floor of **70% of target** (§8.1) the right threshold, and who owns it? | Operations Director with Steering | W1 | The definition of an adopted wave |
| `ADP-Q-08` | **Does `SC-003`'s DPIA cover workforce adoption telemetry** as a processing purpose? `SC-003` was issued before this document and was recorded as absent in draft — corrected at issue, but not yet read against §9 | DP Officer with the Change Lead | **W2 − 8 weeks** | `ADP-20`, `ADP-21`; audit finding `CHA-12` |

---

## 12. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `CH-004-D-01` | Whether to define adoption measures here or defer to `BM-002` | Defer · **define the measurement model here, consume baselines from `BM-002`** | **Define here** | `BM-002` is ⛔ and marked *Now*; deferring would leave W1 with no measurement model at all. The two documents have different jobs: `BM-002` measures the starting point, this plan measures the movement | §5 exists; §4.3's protocol is written so `BM-002` can adopt it |
| `CH-004-D-02` | Denominator for "active" | Headcount · **rostered population** | **Rostered population** | Measuring against headcount counts people on leave as non-adopters, understates adoption, and creates pressure to redefine the numerator instead | `ADP-09`; every figure states its denominator |
| `CH-004-D-03` | How to handle the leaderboard prohibition | Restate `RN-08` · **adopt the four permitted patterns as governing rules and assign the register correction** | **Adopt and assign** | `CM-017` already refused correctly. What is unclosed is the **register row**, which is what the next author reads. A guiding document is the right place to assign that correction | `ADP-13`, `ADP-15`, `ADP-Q-01` |
| `CH-004-D-04` | Whether to claim causation at Level 4 | Claim · **claim correlation with a stated method** | **Correlation with a stated method** | `LS-16` and `M61` `T-12` both require it, and the Kirkpatrick model's most-criticised claim is exactly this one | `ADP-10`; adoption is reported as a leading indicator, not as a benefit |
| `CH-004-D-05` | Site floor for a wave to count as adopted | No floor · **70% of target at every site** · 100% | **70% floor**, declared and reviewable | A programme average conceals a site that never started, which is precisely the `06-01` §9 *"adoption failure at a location"* case | `ADP-18`; `ADP-Q-07` invites the threshold to be set properly |
| `CH-004-D-06` | Whether to collect technician adoption data before the disclosure is settled | Collect and disclose later · **do not collect** | **Do not collect** (`ADP-21`) | `RSK-032` rates PDPA non-compliance Critical with enforcement inside W4, and the population's stated objection is monitoring. Collecting first converts an adoption risk into a compliance risk and improves neither | `ADP-Q-06` becomes a blocking dependency for `P02` measurement |

---

## 13. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every adoption target cited is quoted from `04-00` or `06-02`, never invented | §4.2; `ADP-03` |
| `AC-02` | The baseline position is stated as a counted fact, not a caveat | §4.1 — 44 of 95; 10 of 18; four with gate criteria |
| `AC-03` | Baselines that expire at go-live are identified and dated | §4.4 measures 1, 2, 6; `ADP-06` |
| `AC-04` | Every measure defines its denominator | §5.3; `ADP-09` |
| `AC-05` | The intervention ladder attaches an authority to every step | §6 — six steps |
| `AC-06` | The prohibition and its permitted substitutes are stated as rules | §7.3; `ADP-13`, `ADP-14` |
| `AC-07` | The register correction is assigned to a named owner with a date | §7.4; `ADP-Q-01` |
| `AC-08` | The monitoring boundary is stated before any measurement is commissioned | §9 |
| `AC-09` | Every open question has an owner and a needed-by date | §11 — seven of seven |
| `AC-10` | Approval record | ⬜ **Cannot be met** — `PGD-A2-25` |

---

## 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | [`CH-001`](CH-001_Organisational_Change_Management_Plan.md) | The impact classes and risk treatments this plan measures |
| Upstream | [`CH-002`](CH-002_Training_Plan_and_Delivery_Schedule.md) | Kirkpatrick Levels 1–2; ladder step 3's refresher capacity |
| Upstream | [`CH-003`](CH-003_Stakeholder_Engagement_and_Communication_Plan.md) | Campaign channels, consent, the campaign/transition distinction |
| Upstream | `BM-001` (`06-02`) | The 95-KPI register and the gate criteria |
| Upstream | **`BM-002`** ⛔ | The baselines this plan consumes and cannot produce |
| Lateral | [`CH-005`](CH-005_Super_User_and_Champion_Network_Charter.md) | The *Encourage* driver; network health measures |
| Downstream | **`BM-004`** ◐ | Receives the §8.4 handover |
| Downstream | [`RL-003`](../12_Release_Deployment_and_Transition/RL-003_Go_Live_Readiness_Assessment_and_Gate_Criteria.md) *(issued 2026-08-19)* · `RL-005` ⛔ | Gate adoption position; post-implementation review |
| Downstream | `SV-005` ⛔ | Hypercare exit and the sustainment taper |
| Lateral | `../../project_content/16_Change_Management_and_Comms/CM-016...`, `CM-017...` | The campaign and recognition content this plan governs |
| Lateral | `../../1000fix_ERP_Module/03_Modules/` `M57` §9 | `BRU-PIC-14`, `BRU-PIC-16` |

---

## 15. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
[`CH-001`](CH-001_Organisational_Change_Management_Plan.md) ·
[`CH-002`](CH-002_Training_Plan_and_Delivery_Schedule.md) ·
[`CH-003`](CH-003_Stakeholder_Engagement_and_Communication_Plan.md) ·
[`CH-005`](CH-005_Super_User_and_Champion_Network_Charter.md)

**Workspace**
[`../../project_content/16_Change_Management_and_Comms/CM-016_Adoption_Campaign_Content.md`](../../project_content/16_Change_Management_and_Comms/CM-016_Adoption_Campaign_Content.md) ·
[`../../project_content/16_Change_Management_and_Comms/CM-017_Recognition_Incentive_and_Gamification_Copy.md`](../../project_content/16_Change_Management_and_Comms/CM-017_Recognition_Incentive_and_Gamification_Copy.md) ·
[`../../project_content/_AUDIT/AUDIT-019_Category_16_CM_Content_Audit.md`](../../project_content/_AUDIT/AUDIT-019_Category_16_CM_Content_Audit.md) ·
[`../../project_content/_AUDIT/AUDIT-015_Category_14_RP_Content_Audit.md`](../../project_content/_AUDIT/AUDIT-015_Category_14_RP_Content_Audit.md) ·
[`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md`](../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md) ·
[`../../1000fix_ERP_Module/00_Governance_and_Charter/00-04_Risks_Assumptions_Dependencies_and_Governance.md`](../../1000fix_ERP_Module/00_Governance_and_Charter/00-04_Risks_Assumptions_Dependencies_and_Governance.md)

**External standards** *(all verified 2026-08-19)*

| Source | Edition | Verified |
|---|---|---|
| New World Kirkpatrick Model | Four levels; Required Drivers; results-first design | 2026-08-19 |
| ACMP *Standard for Change Management* | **Version 2**, 26 August 2025 — process groups 4 and 5 | 2026-08-19 |
| ISO 21502:2020 | §7.13 benefits management | 2026-08-19 |
| ISO 21503:2022 | Programme management | 2026-08-19 |
| ISO 9001:2015 | Clause 9.1 monitoring, measurement, analysis and evaluation | 2026-08-19 |
| Bangladesh Personal Data Protection Act 2026 | Lawful basis; purpose limitation. Enforcement ~13 May 2027 per `RSK-032` | 2026-08-19 |

---

## 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Enterprise Architecture with Change Management | Initial issue. First measurement model and baseline protocol for adoption in the estate; adopts the `BRU-PIC-16` boundary as governing rules and assigns the register correction | ⬜ Blocked — `GV-001` `CC-01` |

---

*`CH-004` · Category 13 · 1000FiX ERP System v2.0 · CONFIDENTIAL — Internal Use Only*
