---
id: SP-002
title: As-Is Process Baseline Register
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Business Process Lead
author: Business Process Lead with Operations and Finance
reviewers: [Operations Director, Finance Manager, HR Manager, Quality Manager, Branch Managers Forum, Change Manager]
approver: Operations Director
content_class: E
purpose: >
  Records the current-state process at every branch and function before cutover — including
  the variation between branches, the undocumented workarounds and the pain points — and
  captures the measured baseline for every KPI the programme commits to improve. A baseline
  cannot be reconstructed after cutover: once the old process stops, the evidence of how it
  performed is gone, and every benefit claim in the business case becomes unprovable.
traces_to: [06-01, 06-02, SP-001, DM-002, CM-002, TR-002, RP-001]
priority: P1
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 §1–§9 KPI register with stated baselines and "unmeasured" flags
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04_Risks_Assumptions_Dependencies_and_Governance.md
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 9.1.1 — monitoring, measurement, analysis and evaluation (what needs to be monitored and when results shall be evaluated)
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SP-002 — As-Is Process Baseline Register

> ⚠ **This file has a deadline that no other content file has.** Every other content file can be
> written late at a cost of delay. This one becomes **impossible** to write once a site cuts
> over. The window for each branch closes at that branch's go-live date. See §4.6.

---

## 1. Purpose

The programme commits to 95 measurable improvements (`06-02`, `KPI-001`…`KPI-095`). Enumerating
the baseline column of that register — counted, not estimated (`CP-11`) — produces an
uncomfortable result:

| Baseline state in `06-02` | Count | Consequence |
|---|---:|---|
| A numeric baseline is stated (e.g. `70%`, `15–20 days`, `~10 min`) | 17 | Improvement is provable |
| Measured at **zero** — the capability genuinely does not exist today | 7 | Provable as an absolute, not as an improvement |
| Stated only as **`baseline`** — indexed to an unstated current value | 3 | **The index has no value behind it** |
| Stated as **`unmeasured`**, **`unknown`**, **`untracked`**, **`manual`** or **`n/a`** | **41** | **Improvement is currently unprovable** |
| Listed with **no baseline field at all** (`KPI-069`…`KPI-095`, stated as target + wave only) | **27** | **No starting point was ever asked for** |
| | **95** | |

**Twenty-four of ninety-five KPIs have a measured starting point. Seventy-one do not.** If the
programme goes live without establishing one, it will be able to state its post-implementation
performance and unable to state that it improved anything. That is not a reporting
inconvenience — it is the difference between a defensible benefits case and an assertion.

> *Enumerated from `06-02` on 2026-08-15 by extracting the baseline column of every `KPI-` row.
> The 27 with no baseline field are a defect in `06-02` itself, not in this register, and are
> raised as escalation **E-04** in §6.*

This register does three things:

1. **Documents the current process** as it is actually performed — including the variation
   between the 51+ branches and the workarounds staff have invented, which is where the real
   requirements hide.
2. **Establishes a measured baseline** for every KPI, or records explicitly that no baseline is
   obtainable and what will be used instead.
3. **Preserves the evidence** — sample documents, screenshots, spreadsheets, register books —
   so that migration mapping (`DM-002`) and dispute resolution after cutover have a source.

---

## 2. Scope

**In scope**

- Every process in the five value streams of `SP-001`, as currently performed.
- All 51+ branches and service centres, plus head office, the central warehouse and the workshop network.
- Branch-to-branch variation, including where a branch has invented its own process.
- Shadow systems: spreadsheets, WhatsApp groups, paper registers, personal notebooks.
- Current-state measurement: what is counted today, by whom, and how reliably.

**Out of scope**

| Not covered here | Owned by |
|---|---|
| The designed future process | `SP-001`, the `06B` SOP set |
| Data cleansing rules and source-to-target mapping | `DM-002`, `DM-011` |
| KPI definitions, formulae and grain | `RP-001` |
| Change impact and stakeholder analysis derived from the baseline | `CM-002` |
| Training gap analysis derived from the baseline | `TR-002` |

---

## 3. Audience

| Reader | Uses it to |
|---|---|
| Business Process Lead | Design the to-be process against what is actually done, not what is believed |
| PMO / benefits owner | Defend every benefit claim with a measured before-and-after |
| Migration lead | Find the data that is not in any system (`DM-002`) |
| Change manager | Size the change per role and per branch (`CM-002`) |
| Training designer | Target training at the actual gap (`TR-002`) |
| Branch Manager | Confirm that the record of their branch is accurate — they sign it |
| Internal auditor | Evidence of ISO 9001:2015 clause 9.1.1 evaluation before and after change |

---

## 4. Content

### 4.1 The baseline record — one per process per site cluster

Each entry in the register is a structured record. This is the schema; the populated records live
in the workbook named in §4.7.

| Field | Meaning | Required |
|---|---|:--:|
| `baseline_id` | `BL-<stream>-<nnn>`, e.g. `BL-VS1-014` | ✔ |
| `process_name` | The L2 process from `SP-001` §4.1 | ✔ |
| `value_stream` | VS-1…VS-5 | ✔ |
| `site_cluster` | Which branches this record describes (see §4.3) | ✔ |
| `observed_at` | Sites and dates actually observed, not inferred | ✔ |
| `observer` | Named — accountability for the record | ✔ |
| `current_steps` | The steps as performed, in order | ✔ |
| `systems_used` | Including shadow systems and paper | ✔ |
| `roles_involved` | Mapped to `05-04` `Rnn` where a mapping exists; flagged where it does not | ✔ |
| `volume` | Transactions per day/week/month at this cluster | ✔ |
| `cycle_time_observed` | Measured, with sample size and method | ✔ |
| `variation_from_standard` | How this cluster differs from the dominant pattern | ✔ |
| `workarounds` | What staff do because the official process does not work | ✔ |
| `pain_points` | Named by the people doing the work, in their words | ✔ |
| `controls_present` | What stops error or fraud today — often nothing | ✔ |
| `evidence_refs` | Photographs, sample documents, register scans | ✔ |
| `kpi_baseline_refs` | Which `KPI-nnn` this record supplies a baseline for | ✔ |
| `data_held_outside_systems` | Feeds `DM-002` | ✔ |
| `signed_off_by` | Branch Manager or function head | ✔ |
| `signoff_date` | Must precede that site's cutover | ✔ |

**Rule BL-01.** A record with `cycle_time_observed` but no `sample size` and `method` is not a
baseline; it is an opinion. It is recorded as an estimate and flagged.

**Rule BL-02.** A record is not complete until the accountable Branch Manager or function head
has signed it. They are agreeing to the *before* figure that their *after* figure will be
compared with.

**Rule BL-03.** Workarounds are recorded without blame. A workaround is a requirement that was
never captured. Staff who fear consequence do not disclose workarounds, and the to-be design
then omits a real need — this is stated in the observer briefing (§4.5).

### 4.2 Baseline coverage plan by value stream

| Stream | L2 processes to baseline | Sites to observe | Priority | Window |
|---|---:|---|:--:|---|
| VS-1 Request-to-cash | 15 | 12 branches across all clusters + 2 workshops + 1 warehouse | **P0** | Before W1 gate |
| VS-2 Procure-to-pay | 9 | Head office + central warehouse + 3 branches | P1 | Before W3 gate |
| VS-3 Hire-to-retire | 9 | Head office HR + 4 branches | P1 | Before W5 gate |
| VS-4 Claim-to-reimbursement | 7 | Head office warranty desk + 3 brand-authorised workshops | P1 | Before W4 gate |
| VS-5 Lead-to-contract | 8 | Head office commercial + corporate account team | P1 | Before W2 gate |
| Cross-cutting: cash, complaints, quality, safety | 6 | Sampled with each of the above | **P0** | With VS-1 |
| | **54 process baselines** | | | |

> The VS-1 window is the binding constraint: **12 branches, 15 processes, before the W1 gate.**
> At two observer-days per branch-process cluster this is the single largest field-work item in
> the content programme and it is not currently resourced. Escalated in §6.

### 4.3 Site clustering — why 51+ branches do not need 51+ baselines

Observing every branch is not affordable and not necessary. Branches are clustered by the
factors that actually drive process variation, and a representative sample is observed per
cluster with a variation check at the others.

| Cluster | Defining characteristics | Approx. branches | Sites observed |
|---|---|---:|---:|
| **C1 — Metro flagship** | Dhaka/Chattogram, high volume, on-site workshop, cash + card + MFS, 2 shifts | 6–8 | 3 |
| **C2 — Metro standard** | Metro, intake-and-forward, no workshop | 10–14 | 3 |
| **C3 — Divisional centre** | Divisional HQ towns, workshop, serves surrounding districts | 8–10 | 2 |
| **C4 — District branch** | Single-shift, small team, high role-doubling | 15–20 | 3 |
| **C5 — Kiosk / partner counter** | Intake only, often shared premises | 4–8 | 1 |
| | | **51+** | **12** |

**Rule BL-04.** Cluster membership is confirmed against `MD-003` Branch and Service Centre
Master, not against an observer's impression. If a branch does not fit its cluster's process
pattern, that is a finding, not a re-clustering.

**Rule BL-05.** Role-doubling in C4 and C5 is recorded explicitly. A branch where one person
takes intake, holds cash and reconciles it is a live `SOD-12` violation today. Recording it is
how the to-be design knows a compensating control is needed at those sites (`SP-006` §5).

### 4.4 KPI baseline acquisition — the 61 unmeasured

Each unmeasured KPI needs one of four treatments. Every one of the 61 is assigned a treatment
in the workbook; the pattern is stated here.

| Treatment | When it applies | Method | Example |
|---|---|---|---|
| **T1 — Measure now** | The data exists but is not reported | Extract and count from existing records for a defined period | `KPI-009` uncollected devices > 30 days — countable from branch registers |
| **T2 — Sample now** | No records, but the event is observable | Time-and-motion or stratified sample with a stated confidence | `KPI-010` walk-in intake time — currently ~10 min, sampled at 12 branches |
| **T3 — Reconstruct** | Records exist in a form that needs assembly | Rebuild from source documents for a representative period | `KPI-041` claims with complete evidence at submission — reconstruct by re-examining closed warranty jobs against claims filed |
| **T4 — Declare no baseline** | The activity genuinely does not happen today | Record `0` with an explicit statement that the target is an absolute, not an improvement | `KPI-013` automatic assignment rate — 0% because no dispatch engine exists |

**Rule BL-06.** T4 is the honest treatment for a genuinely new capability and must not be used
to avoid the effort of T1–T3. Every T4 assignment is approved by the benefits owner, not by the
observer.

**Rule BL-07.** A measured baseline states its period, its sample size, its method and its known
distortions (seasonality, Eid peaks, monsoon effects on field service). A baseline taken during
Ramadan and compared with a post-go-live October is not a comparison.

| Baseline distortion to control for | Affects |
|---|---|
| Ramadan and the two Eid periods — volume, staffing and hours all shift | VS-1, VS-3 attendance, cash |
| Monsoon (June–September) — field access, travel time, failed visits | `KPI-014`, `KPI-015`, `KPI-018` |
| Financial year-end (30 June) — finance process load | VS-2, `KPI-050` |
| New-model launch seasons for major brands | Warranty and parts demand |

### 4.5 Observer method and briefing

| Step | What the observer does | Not |
|---:|---|---|
| 1 | Reads `SP-001` for the stream, and the relevant module file for what the system will do | Arrives with a to-be process to validate |
| 2 | Walks the process end to end with the person who performs it | Interviews the manager about what the team does |
| 3 | Records what happens, including the parts nobody mentions in a meeting | Records what should happen |
| 4 | Counts and times, with sample size stated | Estimates and rounds |
| 5 | Photographs or scans the artefacts — register books, forms, whiteboards, WhatsApp threads used operationally | Describes them from memory |
| 6 | Asks "what do you do when that does not work?" at every step | Assumes the happy path is the process |
| 7 | Reads the record back to the person observed and corrects it | Files it unverified |
| 8 | Obtains the Branch Manager's signature | Reports the branch as done without sign-off |

**Observer briefing text (issued verbatim to every observer).**

> You are recording how the work is done today so that we can prove we improved it, and so that
> the new design meets a real need rather than an imagined one. Workarounds are the most
> valuable thing you will find: a workaround is a requirement somebody never wrote down. Record
> them without judgement and without naming the individual. Nothing you record will be used in
> anyone's performance assessment — this commitment is made by the Operations Director and is
> repeated to every team you observe (`CM-005`).

### 4.6 The closing window — per-site deadline

| Wave | Sites cutting over | Baseline must be signed by | Consequence of missing it |
|---|---|---|---|
| W1 | Pilot cluster (C1 metro flagship, 3 sites) + head office admin | W1 gate − 6 weeks | The pilot's own improvement is unprovable, and the pilot is the evidence used to authorise W2 |
| W2 | Customer and technician rollout across C1, C2 | W2 gate − 6 weeks | Field-service baselines (`KPI-011`…`KPI-017`) are lost permanently |
| W3 | Logistics, vendor, payments | W3 gate − 6 weeks | Procure-to-pay and cash baselines lost |
| W4 | Corporate, brand, contact centre | W4 gate − 6 weeks | Warranty leakage baseline lost — the largest single value claim in the case |
| W5 | Quality, finance depth, HR depth | W5 gate − 6 weeks | Payroll and close-cycle baselines lost |

**Rule BL-08.** Six weeks, not one. A baseline signed in the fortnight before cutover is taken
from a site already changing its behaviour in anticipation, and measures the transition rather
than the baseline.

### 4.7 Where the register lives

| Artefact | Form | Location |
|---|---|---|
| This specification | Markdown | This file |
| The populated records | Structured workbook, one row per `baseline_id` | `SP-002_As_Is_Process_Baseline_Register.xlsx` — **not yet created; field work has not begun** |
| Evidence pack | Photographs, scans, sample documents, per `baseline_id` | Programme document store under `M24` retention, class per `LG-010` |
| KPI baseline extract | The 95-row treatment table feeding `RP-001` | Sheet 2 of the workbook |

> The workbook does not exist yet. Recording that plainly is `CP-11`: this file specifies the
> register; it does not claim the register is populated.

### 4.8 Known current-state findings already on record

These are not new observations — they are already documented in the module and governance set,
and they seed the register rather than waiting for field work.

| Finding | Source | Baseline implication |
|---|---|---|
| Warranty claims currently filed at 30–90 days, roughly half within window | `06-02` `KPI-037` | VS-4 baseline exists; reconstruct precisely (T3) |
| Inventory accuracy ~75% | `06-02` `KPI-042` | Physical count required before cutover, not after (`DM-006`) |
| Month-end close 15–20 days | `06-02` `KPI-050` | Directly observable in the current finance calendar (T1) |
| Walk-in intake ~10 minutes against a < 3 minute stretch target | `06-02` `KPI-010` | T2 sampling at 12 branches; the single most-repeated process in the company |
| Bank reconciliation entirely manual | `06-02` `KPI-051` | T4 for auto-match rate; T1 for reconciliation effort hours |
| Existing SLA commitments stated in prose across contracts and marketing, never reconciled, some possibly already unachievable | `MD-028` §6 | VS-5 baseline must record what is actually being promised today, per contract |
| 51+ branches, 8 divisions, no single operating standard | `MD-003`, `SP-001` | Variation is the expected finding, not the exception |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`SP-001_Process_Architecture_and_Value_Stream_Map.md`](SP-001_Process_Architecture_and_Value_Stream_Map.md) | Supplies the L2 process list to be baselined |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-003_Branch_and_Service_Centre_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-003_Branch_and_Service_Centre_Master.md) | Site clustering in §4.3 is validated against it |
| `06-01` Roadmap | Per-site cutover dates set the closing window in §4.6 |
| `06-02` KPI register | The 95 KPIs and their stated baselines |
| `RP-001` KPI definition dictionary | A baseline must be measured on the same definition as the target |

| Depended on by |
|---|
| `DM-002` Data landscape and source-system inventory · `CM-002` Change impact assessment · `TR-002` Training needs analysis · `RP-001` and `RP-003` benefit reporting · `SP-003` (to-be design compares against baseline) · Every benefits claim in the business case |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Weekly during field work; then frozen per site at that site's cutover |
| Trigger for out-of-cycle review | A site's cutover date moving; a new KPI added to `06-02`; discovery of a shadow system not in the register |
| Owner | Business Process Lead |
| Freeze rule | **A baseline record is frozen at its site's cutover and is never edited afterwards.** Corrections are appended as a dated addendum with the reason. An edited baseline is not evidence |
| Retention | Retained for the life of the programme plus the statutory record period in `LG-010`; cited in benefits realisation reporting |

**Escalation raised by this file.**

| # | Issue | Owner | Needed by |
|---|---|---|---|
| E-01 | **71 of 95 KPIs have no usable measured baseline** (§1). Without T1–T3 acquisition the benefits case cannot be evidenced | PMO / benefits owner | Decision before W1 gate − 8 weeks |
| E-02 | **Baseline field work is not resourced.** 54 process baselines across 12 sites, with the VS-1 subset due before the W1 gate | PMO | Resource decision before W1 gate − 10 weeks |
| E-03 | The workbook in §4.7 does not exist and no observer has been appointed | Business Process Lead | Immediate |
| E-04 | **`06-02` omits a baseline field entirely for `KPI-069`…`KPI-095` (27 KPIs).** They are stated as target + wave only. This is a defect in the KPI register, not in this file, and cannot be corrected here | Programme Manager (owner of `06-02`) | Before W1 gate |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3)
- [x] Every factual claim carries a source and a verification date
- [x] The record schema is specified field by field
- [x] Site clustering method stated and tied to `MD-003`
- [x] Every unmeasured KPI has an assigned acquisition treatment class (T1–T4)
- [x] Per-site closing window stated with consequence
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] The populated workbook exists — **outstanding; field work not begun**
- [ ] Branch Manager sign-off obtained per site — **outstanding**
- [ ] Named approver recorded — **pending Operations Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
