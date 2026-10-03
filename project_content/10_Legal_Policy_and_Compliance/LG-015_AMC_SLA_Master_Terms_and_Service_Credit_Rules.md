---
id: LG-015
title: AMC / SLA Master Terms and Service Credit Rules
project: 1000FiX ERP System v2.0
content_type: Legal / policy
template: TPL_Legal_Document.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance with Service Operations
author: Legal & Compliance with Service Operations, Finance, Account Management and Enterprise Architecture
reviewers: [Legal Counsel, COO, CFO, Service Operations, Account Management, Platform Engineering, Localisation Lead, Accessibility reviewer]
approver: Legal Counsel with COO
content_class: B
purpose: >
  The master service terms for AMC, RAMC and managed-service contracts, the definitions of the
  service levels the company commits to, how attainment is measured, what pauses and excludes the
  clock, and the exact calculation of a service credit. Service credits are a quantified financial
  liability, and MD-028 validation rule SLA-03 hard-blocks activation of any SLA band whose credit
  calculation does not match this file's wording — so this file must publish that wording, not
  describe it.
traces_to: [M08, M05, M01, M02, M19, M20, M53, P04, P11, LG-001, LG-002, LG-003, LG-013, LG-014, LG-016, DT-030, DT-031, DT-020, DT-015, MD-028, MD-026, MD-041, MD-014, MD-020, SP-015, NT-020, RP-004, UI-014, BRU-CTR-01, BRU-CTR-02, BRU-CTR-03, BRU-CTR-04, BRU-CTR-05, BRU-CTR-06, BRU-CTR-07, BRU-CTR-08, BRU-SRM-10, BRU-SRM-15, BRU-RMS-05, BRU-RMS-06, BRU-RMS-07, BRU-QMS-04, SLA-01, SLA-02, SLA-03, SLA-04, SLA-06]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: LG-015_AMC_SLA_Master_Terms_and_Service_Credit_Rules_BN.md
sources:
  - source: project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md §2 record structure — sla_band_code, band_name_en, band_name_bn, priority_level, severity_scale, response_target_min, resolution_target_min, business_calendar_code, clock_runs, pause_conditions, service_credit_applies, credit_calculation, credit_cap_pct, escalation_at_pct, effective_from, active; §4 SLA-02 and SLA-03; §9 sample rows SLA-P0, SLA-P2, SLA-P3
    verified: 2026-08-18
    class: P1
  - source: project_content/05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-031_SLA_Schedule_and_Service_Credit_Annex.md — the four ambiguities an annex must remove, L-31-a to L-31-e layout rules, FM-31-a to FM-31-f field rules, MI-01 to MI-07 measurement integrity, §6 variants, §9 MD-028 version pinning at signature, and G6 questions SL1 to SL5
    verified: 2026-08-18
    class: P1
  - source: project_content/_AUDIT/AUDIT_Checklist_Recurring.md check F3 — SLA definitions identical across MD-028, DT-031 and LG-015, zero divergence required because these carry financial liability
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-CTR-01 to BRU-CTR-08 contract activation, out-of-scope billing, expiry cancellation, entitlement over-consumption, suspension notice, RAMC appliance-derived pricing, calibration for healthcare, automatic credit calculation with CFO approval for manual credits; BRU-SRM-10 privilege auto-upgrade; BRU-SRM-15 clock suspension only on an approved hold reason
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M05 §9 BRU-RMS-05 SLA clocks honour the contracted coverage window not office hours; BRU-RMS-06 credits calculated automatically from measured breach; BRU-RMS-07 entitlement over-consumption billed or escalated, never absorbed
    verified: 2026-08-18
    class: P1
  - source: Consumer Rights Protection Act 2009 and the Contract Act 1872 — the enforceability of a liquidated-damages or penalty mechanism and the limits on excluding a consumer's core remedies. **Instrument-level citations from secondary sources; clause-level content unverified, pending G5**
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# LG-015 — AMC / SLA Master Terms and Service Credit Rules

| Item | Value |
|---|---|
| Document class | **Terms** — master terms adopted by reference into an executed contract |
| Counterparty | A contract customer — corporate, government, healthcare, or a residential RAMC holder |
| Governing law | **Bangladesh** |
| Effective date | On publication of version 1.0 — *pending approval* |
| Acceptance capture method | **`AC-2` executed contract** (`DT-030`) with the SLA annex as Schedule C (`DT-031`). **The `MD-028` version in force at signature is pinned to the contract** (`DT-031` §9) |
| Version accepted by users | Recorded in `LG-001`, **with the pinned `MD-028` version alongside it** |
| External counsel review | **Required** — the credit mechanism, the cap and the sole-remedy statement. **These are `DT-031`'s `SL1`–`SL5`, unanswered** |
| Bengali version | **Required.** RAMC holders are consumers, and `DT-031` requires **parallel bilingual columns for the credit calculation** |

> ⚠ **Class B, `P0`. This file is one of three that audit check F3 tests against each other, and F3
> exists because of exactly this triangle.**
>
> `MD-028` §2 says `credit_calculation` **"must match `LG-015` verbatim"**. `MD-028` `SLA-03` makes a
> divergence a **hard block on activation**. `DT-031` opens with the same warning and says
> *"identical — not broadly aligned"*.
>
> **So this file must publish the calculation as an exact string, not describe it.** §4.6 does.
>
> **It also has to publish the band definitions the other two copy.** §4.3 does — reproduced from
> `MD-028`'s actual record structure and sample rows, **not from `DT-031`'s field mapping, which
> names nine `MD-028` fields that do not exist** (`O-02`).
>
> **Conformance note.** All ten template sections retained in order. The band definitions are §4.3,
> the clock rules §4.4, the exclusions §4.5 and the credit calculation §4.6, within §4 Terms. Gate
> questions and open items are §1.2 and §1.3 (`CP-09`).

---

## 1. Approval Record

| Role | Name | Date | Evidence |
|---|---|---|---|
| Drafted by | Legal & Compliance with Service Operations | 2026-08-18 | Draft issue v1.0 |
| G1 Editorial — Content Design | *pending* | | |
| G2 Factual — COO with Service Operations | *pending* | | |
| **G3 Technical — Platform Engineering: every committed target is measurable as specified** | *pending* | | **Required. `CG-007` §2.1 makes G3 mandatory where a Class B file is system-pinned** |
| G4 Linguistic — independent reviewer, in context (`BN-018`) | *pending* | | |
| **G5 Legal — Legal Counsel** | *pending* | | **Required** |
| Approved by — Legal Counsel with COO | *pending* | | |

### 1.2 Questions for Legal Counsel (G5)

**These are `DT-031` §2.1 `SL1`–`SL5` verbatim, because the same five questions govern all three
files and must be answered once.**

| # | Question | `DT-031` ref |
|---|---|---|
| **SL1** | **Is the service-credit mechanism enforceable as drafted, or should it be framed as liquidated damages?** A credit that reads as a penalty may be unenforceable | `SL1` |
| **SL2** | **Is a cap on aggregate credits enforceable, and at what level?** `MD-028` samples 10% for `SLA-P0` and 5% for `SLA-P2` | `SL2` |
| **SL3** | **Can credits be the sole remedy for a service-level failure, and is that enforceable for consumers?** | `SL3` |
| **SL4** | **What exclusions are permissible**, particularly force majeure and third-party dependency? | `SL4` |
| **SL5** | **Are the RAMC service levels compatible with consumer protection obligations?** Consumer contracts cannot exclude core obligations | `SL5` |
| **SL6** | *(added here)* Where a tender prescribes service levels that **override** ours, does adopting them by reference import the tender's remedy regime too? | `DT-031` §6 flags the override |
| **SL7** | *(added here)* Is a **claim requirement** — the customer must claim a credit within a window — enforceable, given `FM-31-d` says requiring a claim the customer cannot know to make is not defensible? | `FM-31-d` |

### 1.3 Open items

| # | Open item | Blocking? | Owner |
|---|---|:--:|---|
| **O-01** | **`SL1`–`SL7` unanswered.** §4.6 and §5 are provisional under `CG-012` `PR-01`, and `PR-03` prohibits relying on a provisional term for a contractual commitment | **Yes — blocks `Approved` on all three F3 files** | Legal Counsel |
| **O-02** | **F3 divergence found. `DT-031` §4.1 and §4.2 map nine fields to `MD-028` that `MD-028` §2 does not contain**: `priority_code`, `priority_name_en`/`_bn`, `definition`, `response_target`, `resolution_target`, `coverage_window`, `measurement_basis`, `clock_start_event`, `clock_stop_event`. `MD-028` has `sla_band_code`, `band_name_en`/`_bn`, `response_target_min`, `resolution_target_min`, `business_calendar_code`, `clock_runs` and `pause_conditions`, **and has no `definition`, no `measurement_basis` and no clock-event fields at all**. **This is a live F3 failure between two written files** | **Yes — F3 is blocking, and `DT-031`'s own DoD leaves the F3 run outstanding** | Enterprise Architecture with Legal |
| **O-03** | **`MD-028` has no field for clock start and stop events, and `DT-031` §1.1 makes them one of the four ambiguities an annex must remove.** §4.4 defines them in this file and **requires two new `MD-028` columns** | **Yes — a master-data change** | Master Data Owner |
| **O-04** | **`MD-028` has no `definition` field**, yet `DT-031` prints a per-band definition and `DT-031` `L-31-b` requires values **copied, not paraphrased**. §4.3 supplies the definitions and **requires a new `MD-028` column** | **Yes** | Master Data Owner |
| **O-05** | **`MD-028` says 10–20 bands in production and samples three** (`SLA-P0`, `SLA-P2`, `SLA-P3`). **`SLA-P1` and `SLA-P4` are referenced by the `priority_level` enum and are not defined.** §4.3 defines five and marks which are sampled and which are proposed | **Yes** | Service Operations |
| **O-06** | **`MD-028` §6 records that existing SLA commitments are stated in prose across contracts and marketing content, have not been reconciled, and "some may already be unachievable."** **This file cannot ratify a target the business cannot meet** | **Yes — G3 must test each target before G5** | COO with Platform Engineering |
| **O-07** | **No target attainment percentage is registered.** `DT-031` §4.1 maps `contract.sla_attainment_pct` to the contract, not to `MD-028`, so **each contract could carry a different attainment threshold against the same band** | Yes — blocks §4.6 | Service Operations with Legal |
| **O-08** | **The RAMC variant has no credit mechanism** (`DT-031` §6) but is a **consumer** contract, so `SL5` and `LG-013`/`LG-014` consumer rights apply instead. §4.9 states that; it needs `SL5` | **Yes** | Legal Counsel |
| **O-09** | **`MD-028` `SLA-06` requires Legal and CCO approval to change a target on a band referenced by an active contract**, while `DT-031` §9 pins the version at signature. **Both are needed and they answer different questions** — §4.10 reconciles them | No — reconciled here | — |

---

## 2. Scope and Parties

| Party | Identity |
|---|---|
| **The Company** | 1000FiX Services Limited |
| **The Customer** | The party to an executed AMC, RAMC, managed-service or framework contract |

**Precedence:**

| Rank | Instrument | Governs |
|---|---|---|
| **1** | The **executed contract** (`DT-030`) and its schedules | Scope, price, term, and any commercial term it states expressly |
| **2** | The **SLA annex** as Schedule C (`DT-031`) | The bands, targets and credit terms **as they applied at signature**, with the `MD-028` version pinned |
| **3** | **These master terms** | Definitions, measurement, clock, exclusions, the credit calculation, and anything 1 and 2 are silent on |
| **4** | `LG-008` / `LG-009` / `LG-012` | Personal data — **prevail** |

| # | Clause |
|---|---|
| **2.1** | These terms are adopted by reference in the contract. **A contract that does not adopt them does not get them** |
| **2.2** | Where the contract states a band or target expressly, **rank 1 governs and `MD-028` must contain a matching band** (`FM-31-a`: a contract cannot promise a target the register does not contain) |
| **2.3** | **A tender-prescribed service level overrides ours where the tender mandates it**, and Legal confirms each (`DT-031` §6) — subject to `SL6` |
| **2.4** | A consumer RAMC holder also has the rights in `LG-013` and `LG-014`, **which these terms do not reduce** (§4.9) |

---

## 3. Definitions

> **`SD-01`: every definition here is the definition. `MD-028`, `DT-031` and `RP-004` use these
> words with these meanings and no others.** This is the F3 vocabulary.

| Term | Definition |
|---|---|
| **SLA band** | A named, coded set of commitments — `sla_band_code`, format `SLA-Pn`, permanent and never reused (`MD-028` §3) |
| **Priority** | Business urgency — `priority_level`, one of `P0`…`P4` |
| **Severity** | Impact, **distinct from priority** — `severity_scale`, one of critical, high, medium, low |
| **Response** | **The first meaningful response**, recorded as a system event (`MI-01`). Not an internal acknowledgement, not an automated receipt |
| **Resolution** | The service restored or the work completed, as the band defines |
| **Response target** | `response_target_min`, in **minutes** |
| **Resolution target** | `resolution_target_min`, in **minutes** |
| **Clock** | The elapsed measurement against a target, running on the band's `clock_runs` basis and `business_calendar_code` |
| **Coverage window** | `clock_runs` — `24x7`, `business_hours` or `extended_hours` — read against the `MD-041` calendar |
| **Hold** | A suspension of the clock on an **approved** reason. **A hold reason not in the `MD-026` approved set does not stop the clock** (`BRU-SRM-15`, `FM-31-b`) |
| **Exclusion** | A circumstance entirely outside the SLA (§4.5), distinct from a hold |
| **Breach** | A target missed after holds and exclusions are applied |
| **Attainment** | Breaches against total in-scope events over the measurement period |
| **Service credit** | The contractual remedy for a breach, calculated by §4.6 |
| **Aggregate cap** | `credit_cap_pct` — the ceiling on credits in one measurement period as a percentage of that period's charge |
| **Out-of-scope work** | Work outside the contract, **billed separately and outside the SLA** (`BRU-CTR-02`) |
| **Governing text** | The **English** version (`LG-001` `LR-03`); the credit calculation is presented in **parallel bilingual columns** (`DT-031` §3) |

---

## 4. Terms

### 4.1 The contract

| # | Clause |
|---|---|
| **4.1.1** | **A contract cannot be activated without at least one covered asset or seat, defined entitlements, a billing frequency and approval** (`BRU-CTR-01`) |
| **4.1.2** | **Work outside scope is billed separately and never silently absorbed** (`BRU-CTR-02`), and **is outside the SLA as well as outside the price** |
| **4.1.3** | **Entitlement over-consumption is blocked or flagged for billing per the contract's configuration; it is never invisible** (`BRU-CTR-04`, `BRU-RMS-07`) |
| **4.1.4** | **Over-consumption does not suspend the SLA unless the annex says so** (`BRU-CTR-04` as applied in `DT-031` §5) |
| **4.1.5** | **RAMC package price is derived from the number and type of registered appliances, never a flat fee** (`BRU-CTR-06`) |
| **4.1.6** | **A healthcare equipment contract requires calibration scheduling as a mandatory element** (`BRU-CTR-07`) |
| **4.1.7** | **On expiry, future scheduled work orders are cancelled and the Customer is notified** (`BRU-CTR-03`) |
| **4.1.8** | **Suspension for non-payment follows the defined notice sequence and cannot be applied without it** (`BRU-CTR-05`) |

### 4.2 Entitlements

Entitlements are visible to the Customer at all times in `P04`, consumed as work is delivered, and
reported against the contract. Unused entitlement does not carry forward unless the contract says
so. **A request for an asset not covered is refused with the reason shown, not silently** (`LG-003`
§4.4.2).

### 4.3 The SLA bands — **the F3 table**

> **`SD-02`: this is the authoritative band definition. `MD-028` carries these values as data;
> `DT-031` prints them; neither may vary them** (`L-31-b`: copied, not paraphrased).
>
> **Three bands are reproduced from `MD-028` §9 sample rows. Two are proposed because the
> `priority_level` enum admits them and `MD-028` states 10–20 production bands** (`O-05`).
> **The `Definition` column has no `MD-028` field to live in — `O-04`.**

| `sla_band_code` | `band_name_en` | `band_name_bn` | `priority_level` | `severity_scale` | `response_target_min` | `resolution_target_min` | `business_calendar_code` | `clock_runs` | `pause_conditions` | `service_credit_applies` | `credit_cap_pct` | `escalation_at_pct` | Definition — **`O-04`** | Status |
|---|---|---|:--:|---|---:|---:|---|---|---|:--:|---:|---:|---|---|
| `SLA-P0` | Critical Enterprise | ক্রিটিক্যাল এন্টারপ্রাইজ | `P0` | critical | **30** | **240** | `CAL-24X7` | `24x7` | `awaiting_customer`; `awaiting_part` | **TRUE** | **10.00** | 75 | Complete loss of a business-critical function with no workaround, on a covered asset | **From `MD-028` §9** |
| `SLA-P1` | Critical Standard | ক্রিটিক্যাল স্ট্যান্ডার্ড | `P1` | high | *proposed* | *proposed* | *proposed* | *proposed* | *proposed* | *proposed* | *proposed* | *proposed* | Major degradation with a partial workaround | **Proposed — `O-05`** |
| `SLA-P2` | Standard Corporate | স্ট্যান্ডার্ড কর্পোরেট | `P2` | medium | **240** | **2880** | `CAL-BUS` | `business_hours` | `awaiting_customer`; `awaiting_part`; `awaiting_brand` | **TRUE** | **5.00** | 75 | A covered asset is faulty; the Customer's operations continue | **From `MD-028` §9** |
| `SLA-P3` | Standard Consumer | স্ট্যান্ডার্ড কনজিউমার | `P3` | medium | **480** | **4320** | `CAL-BUS` | `business_hours` | `awaiting_customer`; `awaiting_part` | **FALSE** | — | 80 | A covered residential appliance is faulty | **From `MD-028` §9** |
| `SLA-P4` | Deferred | ডেফার্ড | `P4` | low | *proposed* | *proposed* | *proposed* | *proposed* | *proposed* | *proposed* | — | *proposed* | A request the Customer has agreed may be scheduled | **Proposed — `O-05`** |

| # | Rule |
|---|---|
| **SD-03** | **`resolution_target_min` must exceed `response_target_min`** (`MD-028` `SLA-01`, hard block) |
| **SD-04** | **`service_credit_applies` TRUE requires a credit calculation and a cap** (`MD-028` `SLA-02`, hard block) |
| **SD-05** | **`band_name_bn` is mandatory** (`MD-028` `SLA-05`), because the band name is shown to the Customer in `P01` and `P04` |
| **SD-06** | **`SLA-P3` Standard Consumer carries no service credit.** A consumer's remedy is `LG-013` and `LG-014`, not a credit — §4.9, `SL5` |
| **SD-07** | **A privilege Gold or Diamond customer receives priority-1 SLA regardless of service type** (`BRU-SRM-10`), and the annex says so (`FM-31-e`). **`SLA-P1` is therefore not optional — `O-05` blocks a live commitment** |
| **SD-08** | **Targets are in minutes.** A contract expressing a target in hours or days is converted once, at signature, and the minute value is what is measured |
| **SD-09** | **A target the platform cannot measure as specified is not committed.** G3 tests each one before G5 (`O-06`) |

### 4.4 The clock — start, stop, hold

> **`DT-031` §1.1 names four ambiguities every SLA dispute is about: what is measured, when the clock
> starts and stops, what pauses it, and what is excluded. §4.3, §4.4 and §4.5 answer all four.**
>
> **`MD-028` has no field for clock start and stop events — `O-03`.**

| # | Clause |
|---|---|
| **4.4.1** | **The response clock starts when the request is recorded in the Company's system**, whether raised by the Customer in `P04`, by hotline, by monitoring alert, or by scheduled work becoming due |
| **4.4.2** | **The response clock stops on the first meaningful response, recorded as a system event** (`MI-01`). *"Responded" means a recorded event, not a belief that someone called* |
| **4.4.3** | **The resolution clock starts with the response clock** and stops when the work is recorded complete and the Customer-facing state changes to resolved |
| **4.4.4** | The clock runs on the band's `clock_runs` basis against the `MD-041` calendar. **A managed-service clock honours the contracted coverage window, not office hours** (`BRU-RMS-05`) |
| **4.4.5** | **The clock suspends only on an approved hold reason from `MD-026`, and resumes automatically when the hold is released** (`BRU-SRM-15`). Approved reasons per band are `pause_conditions` in §4.3 |
| **4.4.6** | **A hold requires a coded reason and is visible to the Customer in `P04`. A hidden hold is an unmeasurable SLA** (`MI-02`) |
| **4.4.7** | **A paused clock without a recorded trigger resumes** (`MD-028` `SLA-04`). The default is that the clock runs |
| **4.4.8** | **Hold duration is reported alongside attainment. A 100% attainment achieved through extensive holds is a reporting artefact, not performance** (`MI-03`) |
| **4.4.9** | Where the contract caps hold duration, the cap applies and the clock resumes at it |
| **4.4.10** | **Breaches are notified as they occur** (`NT-020`, `MI-05`), **not discovered at period end** |
| **4.4.11** | **The Customer sees the same measurement the Company does, in `P04`** (`MI-06`). Two versions of the truth is how SLA relationships fail |
| **4.4.12** | **Where a measurement is disputed, the underlying event log is producible** (`MI-07`) |
| **4.4.13** | Escalation fires at `escalation_at_pct` of the target (`NT-020`) — **75% on `SLA-P0` and `SLA-P2`, 80% on `SLA-P3`** |

### 4.5 Exclusions

> **`DT-031` `L-31-d`: exclusions are a numbered list, not prose, because each is separately
> arguable and must be separately identifiable.** Every item is provisional pending `SL4`.

| # | Exclusion |
|---|---|
| **SX-01** | Work outside the contract's scope (`BRU-CTR-02`) |
| **SX-02** | A request for an asset not covered by the contract |
| **SX-03** | A fault caused by the Customer, its staff, or a party the Customer engaged |
| **SX-04** | A fault caused by an environment outside the asset's stated operating conditions — power, temperature, humidity, contamination |
| **SX-05** | The Customer's failure to provide access, at an agreed time, to the site or the asset |
| **SX-06** | The Customer's failure to provide information or an approval the work needs |
| **SX-07** | A third-party dependency outside the Company's control, **where notified to the Customer when it arises** — subject to `SL4` |
| **SX-08** | Parts unavailable from the manufacturer or from any qualified source, **where evidenced and notified** |
| **SX-09** | A Customer-requested deferral, and any period covered by an agreed maintenance window |
| **SX-10** | Force majeure — subject to `SL4` |
| **SX-11** | A period during which the contract is suspended for non-payment under the §4.1.8 notice sequence |
| **SX-12** | Work on an asset the Customer has modified without the Company's agreement |
| **SX-13** | A request raised outside the coverage window, for the period until the window opens |

| # | Rule |
|---|---|
| **SX-R1** | **An exclusion is applied only where it is evidenced and recorded**, on the same standard `BRU-WTY-17` sets for a warranty void |
| **SX-R2** | **An exclusion is not a hold and a hold is not an exclusion.** A hold pauses; an exclusion removes the event from measurement. **Confusing the two is the most common way attainment is overstated** |
| **SX-R3** | **`SX-07` and `SX-10` are the two the Customer will contest**, and both require notification at the time — not an explanation at period end |
| **SX-R4** | Excluded events are reported with a count and reason, so the Customer can see what was excluded and why |

### 4.6 The service credit calculation — **the canonical text**

> **`CL-01`. `MD-028` §2 says `credit_calculation` "must match `LG-015` verbatim". `SLA-03` makes a
> divergence a hard block on activation. This is that text.**
>
> **`DT-031` `L-31-c` requires a worked example on the annex itself**, because *"a formula without an
> example is a formula two parties will compute differently"*. §4.7 supplies it.
>
> **Provisional pending `SL1`, `SL2`, `SL3` and `O-07`.**

**Canonical text — to be copied into `MD-028.credit_calculation` exactly as written:**

> **Service credit = the Period Charge × the Credit Rate for the attainment band achieved, capped at
> the Aggregate Cap for the band. The Period Charge is the charge for the measurement period in
> which the breach occurred, excluding out-of-scope work, parts billed separately, and taxes.
> Attainment is calculated as in-scope events resolved within target divided by total in-scope
> events for the period, after approved holds are deducted and excluded events are removed.
> Credits are calculated automatically from measured breach; a manual credit requires CFO approval.
> Credits for a period are applied as a credit note or an offset against the next invoice, never as a
> cash payment, and never exceed the Aggregate Cap for that period.**

**Bengali parallel text** — required by `DT-031` §3, **to be authored and linguistically signed off
in context under `BN-018`; not drafted here** (`CM-R6`).

| Element | Value | Source |
|---|---|---|
| **Period Charge** | The measurement period's charge, excluding out-of-scope work, separately billed parts, and taxes | This file |
| **Credit Rate** | Per attainment band, in the contract | `contract.credit_rate` (`DT-031` §4.2) |
| **Credit Basis** | Per breach, **or** per period attainment — one, stated in the contract | `contract.credit_basis` |
| **Aggregate Cap** | **`credit_cap_pct` — 10.00% for `SLA-P0`, 5.00% for `SLA-P2`** | `MD-028` §9 |
| **Attainment threshold** | **Not registered — `O-07`** | `contract.sla_attainment_pct` |
| **Application** | Credit note (`DT-015`) or offset on the next invoice (`DT-020`) | `DT-031` §4.2 |

| # | Rule |
|---|---|
| **CR-01** | **Credits are calculated automatically from measured breach. A manual credit requires CFO approval and appears on the invoice with the approver named** (`BRU-CTR-08`, `BRU-RMS-06`, `FM-31-c`) |
| **CR-02** | **A credit is never paid in cash.** It is a credit note or an invoice offset |
| **CR-03** | **The cap is per measurement period**, not per contract year, unless the contract says otherwise |
| **CR-04** | **Holds are deducted before attainment is computed**, and hold duration is reported beside it (`MI-03`) |
| **CR-05** | **Excluded events are removed from both numerator and denominator**, and are reported (`SX-R4`) |
| **CR-06** | **Where a claim is required within a window, the window is stated and the Customer is notified of breaches as they occur** (`NT-020`). **Requiring a claim the Customer cannot know to make is not a defensible position** (`FM-31-d`) — subject to `SL7` |
| **CR-07** | **Whether credits are the sole remedy is `SL3` and is not asserted here.** Until answered, the annex states that credits are *a* remedy |
| **CR-08** | **A credit is not a refund and is not compensation.** `LG-014` governs refunds and compensation; **a credit does not extinguish a `LG-014` entitlement and a `LG-014` payment does not extinguish a credit** |
| **CR-09** | **The `MD-028` version pinned at signature governs the calculation for that contract.** A later register change does not alter a signed commitment (`DT-031` §9) |
| **CR-10** | Measurement evidence supporting attainment is retained for the claim window plus the dispute period (`DT-031` §9; `LG-009` `RC-08`, `DC-10`) |

### 4.7 Worked example — required on every annex

**Assumptions:** band `SLA-P2` Standard Corporate · monthly measurement period · Period Charge
BDT 200,000 · Credit Basis *per period attainment* · Credit Rate 2% per full percentage point below
the attainment threshold · **Aggregate Cap 5.00%** (`MD-028` §9).

| Step | Calculation | Result |
|---|---|---|
| 1 | In-scope events in the period | 40 |
| 2 | Less excluded events (`SX-05` access refused ×2, `SX-08` parts unavailable ×1, evidenced) | 37 in scope |
| 3 | Events resolved within target, after approved holds deducted | 33 |
| 4 | Attainment = 33 ÷ 37 | **89.2%** |
| 5 | Attainment threshold (contract) — **`O-07`; 95% used for illustration** | 95.0% |
| 6 | Full percentage points below threshold | 5 |
| 7 | Credit = 5 × 2% × BDT 200,000 | **BDT 20,000** |
| 8 | Aggregate Cap = 5.00% × BDT 200,000 | **BDT 10,000** |
| 9 | **Credit payable — capped** | **BDT 10,000** |
| 10 | Applied as | Credit note (`DT-015`) or offset on the next `DT-020` |
| 11 | Reported alongside | Total hold duration, and the 3 excluded events with reasons |

> **The example is deliberately one that hits the cap.** A worked example that never reaches the cap
> leaves the most contentious step untested, and step 8 is the step a customer disputes.

### 4.8 Variants

Reproduced from `DT-031` §6, which is the authority for the annex's variants.

| Variant | Use | Difference |
|---|---|---|
| **Standard corporate** | AMC and MSP | Full annex with credits |
| **RAMC consumer** | Residential | Simplified targets, plainer language, **no credit mechanism unless offered; consumer protections retained** — §4.9, `SL5` |
| **Healthcare / critical** | Hospitals, diagnostics | Tighter targets, escalation contacts, **calibration-linked commitments** (`BRU-CTR-07`) |
| **Enterprise multi-service** | Framework | One annex per service schedule; targets differ by service |
| **Government / tender** | Public procurement | **Prescribed levels override ours; Legal confirms each** (`SL6`) |
| **Pilot / trial** | Evaluation | Targets measured, **explicitly no credit liability** |
| **Marketplace-delivered** | Seller-fulfilled | **Same customer-facing commitment**; the seller's obligation is in `LG-004`, not here (`BRU-ECM-03`) |

### 4.9 The consumer position

| # | Clause |
|---|---|
| **4.9.1** | **`SLA-P3` Standard Consumer carries no service credit** (`MD-028` §9, `service_credit_applies` FALSE) |
| **4.9.2** | A consumer's remedy for a service failure is **`LG-013`** (repair, replacement, re-performance) and **`LG-014`** (refund, cancellation, compensation). **These master terms do not reduce either** |
| **4.9.3** | **A consumer contract cannot exclude a core obligation**, and §4.5 is read subject to that — `SL5` |
| **4.9.4** | Where a RAMC contract is offered with a credit mechanism, §4.6 applies and **the consumer's statutory rights remain in addition** |
| **4.9.5** | **The consumer's right to complain to the Directorate of National Consumer Rights Protection is preserved and unconditional** |

### 4.10 Change to a band, and version pinning — **reconciling `O-09`**

> **Two controls exist and they answer different questions. Both are needed.**

| Control | Question it answers | Effect |
|---|---|---|
| **`MD-028` `SLA-06`** | *May this band change at all?* | **Changing a target on a band referenced by an active contract requires Legal and CCO approval** |
| **`DT-031` §9 pinning** | *Which version applies to a contract already signed?* | **The `MD-028` version in force at signature is pinned. A later change does not alter a signed commitment** |

| # | Rule |
|---|---|
| **4.10.1** | **A band is effective-dated. A job is judged by the band version in force at its creation** (`MD-028` §8) |
| **4.10.2** | **The system measures each contract against its pinned version, not against today's register** (`DT-031` §9) |
| **4.10.3** | The pinned `MD-028` version **prints in the annex footer** (`L-31-a`), because the first question in a dispute is which definitions applied |
| **4.10.4** | A band is archived, never deleted (`MD-028` §8, `05-02` DM-06) |
| **4.10.5** | **A change to §4.6's canonical text requires the `MD-028` `credit_calculation` field to be updated in the same release.** Until it is, `SLA-03` blocks activation — **which is the control working** |

---

## 5. Liability, Exclusions and Limits

> Provisional pending `SL1`, `SL2`, `SL3`.

| # | Clause |
|---|---|
| **5.1** | The Company is liable for loss caused by its failure to exercise reasonable skill and care in delivering the contracted service |
| **5.2** | **Service credits are the contractual remedy for a service-level failure to the extent §4.6 provides. Whether they are the sole remedy is `SL3` and is not asserted** (`CR-07`) |
| **5.3** | **Aggregate credits in a measurement period never exceed the Aggregate Cap** — `credit_cap_pct` (§4.6), provisional pending `SL2` |
| **5.4** | The Company is not liable for a failure arising from an exclusion in §4.5, where evidenced (`SX-R1`) |
| **5.5** | Neither party is liable for indirect or consequential loss, **except where the executed contract provides otherwise** — rank 1 governs |
| **5.6** | **Nothing limits liability that cannot lawfully be limited**, including for death or personal injury caused by negligence, for fraud, for a statutory data-protection liability, or for a non-excludable consumer right (§4.9) |
| **5.7** | **A credit is not a cap on the Company's obligation to fix the problem.** `BRU-QMS-04`: a complaint linked to a breach is closed with the Customer, not internally |

---

## 6. Data Protection

> Must reconcile with `LG-008`, `LG-009`, `LG-012`. Check **F6**.

| # | Clause |
|---|---|
| **6.1** | Contract, entitlement, SLA measurement and credit records are processed for `LG-008` `P-08` on contract performance |
| **6.2** | Contract and SLA records are retained per `LG-009` `RC-08` and `DC-10` — **contract term plus the limitation period**, with the pinned `MD-028` version preserved |
| **6.3** | **Measurement event logs supporting attainment are retained for the claim window plus the dispute period** (`CR-10`), because `MI-07` requires them to be producible |
| **6.4** | Corporate portal users' personal data is `LG-003` §6; a Customer administrator can see requests their colleagues raised (`LG-008` `P-08` risk statement) |
| **6.5** | Where managed-service access is involved, `LG-016` governs consent, session recording and data handling |
| **6.6** | **Session recordings under a managed-service contract are retained per the contract and the retention schedule, and access is logged** (`BRU-RMS-12`, `LG-009`) |

---

## 7. Termination and Consequences

| Event | Consequence |
|---|---|
| **Contract expires** | **Future scheduled work orders are cancelled and the Customer is notified** (`BRU-CTR-03`). Credits for the final period are calculated and applied |
| **Non-payment** | Suspension only after the defined notice sequence (`BRU-CTR-05`). **A suspension period is excluded from measurement** (`SX-11`) |
| **Termination by either party** | Work in progress is completed or handed over; **entitlement already consumed is not refunded**; credits accrued are applied |
| **Managed-service offboarding** | **Not complete until every agent is removed and every access revoked, evidenced** (`BRU-RMS-11`) |
| **Band withdrawn from `MD-028`** | **Signed contracts keep their pinned version** (§4.10.2). The band is archived, not deleted |
| **These master terms superseded** | Contracts adopting version 1.0 keep version 1.0. Prior versions retained permanently (`LG-009` `DC-23`) |

---

## 8. Dispute Resolution

| Step | Route |
|---|---|
| **1 — Measurement dispute** | The account manager, with the **event log produced** (`MI-07`). **The log governs; recollection does not** |
| **2 — Credit calculation dispute** | Service Operations with Finance, against the pinned `MD-028` version and the §4.7 worked example |
| **3 — Commercial escalation** | Corporate Services Head, then the COO |
| **4 — Consumer route** | For a RAMC holder: `SP-028` complaint, then the DNCRP (§4.9.5) |
| **5 — Arbitration** | Per the executed contract; where silent, arbitration in Dhaka under the Arbitration Act 2001 |
| **6 — Courts** | The courts of Dhaka, Bangladesh |

---

## 9. Change Control

| Version | Date | Change | Notice given to users | Re-acceptance required |
|---|---|---|---|:--:|
| 1.0 | 2026-08-18 | Initial issue — draft. Canonical credit-calculation text established for `MD-028` `SLA-03`; F3 divergence with `DT-031` recorded at `O-02` | n/a | n/a |

| # | Rule |
|---|---|
| **9.1** | A change to a definition, a target, an exclusion, the calculation or the cap is **MAJOR** |
| **9.2** | **A MAJOR change does not affect a signed contract**, which keeps its pinned `MD-028` version (§4.10.2) |
| **9.3** | **A change to §4.3 or §4.6 re-opens F3 and must be pushed to `MD-028` and `DT-031` in the same release** (§4.10.5) |
| **9.4** | A change requires **Legal and CCO approval** where any active contract references the affected band (`MD-028` `SLA-06`) |
| **9.5** | **`SL1`–`SL3` answers are MAJOR by definition** and change all three F3 files together |
| **9.6** | G3 is re-run on any target change, because a target the platform cannot measure is not committable (`SD-09`) |

---

## 10. Cross-References

| Document | Relationship | Must not contradict |
|---|---|---|
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md) | **F3 file 1 — carries §4.6 verbatim; `SLA-03` hard-blocks divergence** | **Every value in §4.3 and the §4.6 text** |
| [`../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-031_SLA_Schedule_and_Service_Credit_Annex.md`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-031_SLA_Schedule_and_Service_Credit_Annex.md) | **F3 file 2 — prints §4.3, §4.4, §4.5, §4.6 and §4.7** | **`O-02`: nine field names in its §4.1/§4.2 do not exist in `MD-028`** |
| [`../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-030_Contract_and_AMC_Agreement_Template_Set.md`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-030_Contract_and_AMC_Agreement_Template_Set.md) | Rank 1; this annex is its Schedule C | Commercial terms |
| [`LG-014_Refund_Cancellation_and_Compensation_Policy.md`](LG-014_Refund_Cancellation_and_Compensation_Policy.md) | **`CR-08` — a credit is not a refund** | `EN-18` contract cancellation |
| [`LG-013_Service_Terms_Warranty_Terms_and_Exclusions.md`](LG-013_Service_Terms_Warranty_Terms_and_Exclusions.md) | §4.9.2 consumer remedy | A credit is not a warranty remedy |
| [`LG-003_Portal_Terms_of_Use_Corporate.md`](LG-003_Portal_Terms_of_Use_Corporate.md) | Rank 2 in its §2; §4.6 defers here | Service levels and credits |
| [`LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md`](LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md) | §6.5, §6.6 | Consent, recording, retention |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md) | **Approved hold reasons (§4.4.5)** | The approved set |
| [`../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md) | Business-hour clocks (§4.4.4) | The calendar |
| [`../04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-020_Escalation_and_SLA_Breach_Notification_Library.md`](../04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-020_Escalation_and_SLA_Breach_Notification_Library.md) | §4.4.10, §4.4.13, `CR-06` | Breach and escalation notification |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-015_SOP_Contract_and_AMC_Lifecycle.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-015_SOP_Contract_and_AMC_Lifecycle.md) | Operates the mechanism | Hold handling, credit application |
| `RP-004` operational dashboards · `UI-014` `P04` copy | `MI-03` hold-adjusted attainment; `MI-06` customer-visible measurement | **One measurement, shown identically to both parties** |
| `HC-006` Help Set `P04` · `TR-018` account manager course | Explain these terms | No help may state a target `MD-028` does not contain |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Legal_Document.md` — ten sections in order; additions declared
- [x] **The canonical service-credit calculation published as exact text for `MD-028.credit_calculation`** (`CL-01`, `SLA-03`)
- [x] **The F3 band table reproduced from `MD-028`'s actual record structure and sample rows**, with proposed bands marked as proposals
- [x] **All four `DT-031` §1.1 ambiguities answered** — what is measured (§4.3), when the clock starts and stops (§4.4), what pauses it (§4.4.5), what is excluded (§4.5)
- [x] Thirteen numbered exclusions, with hold and exclusion explicitly distinguished (`SX-R2`)
- [x] **Worked example that reaches the cap**, so the contentious step is demonstrated (§4.7)
- [x] `MD-028` `SLA-06` and `DT-031` §9 pinning reconciled as two different controls (§4.10, `O-09`)
- [x] Consumer position stated: **no credit on `SLA-P3`, and `LG-013`/`LG-014` rights unreduced** (§4.9)
- [x] All internal links resolve
- [ ] **Check F3 run against `MD-028` and `DT-031` — zero divergence.** **FAILS TODAY: `O-02` records nine non-existent field names in `DT-031`.** Blocks `Approved` on all three files
- [ ] **`SL1`–`SL7` answered at G5** — outstanding
- [ ] **G3: Platform confirmation that every committed target is measurable as specified** — outstanding, `O-06`
- [ ] **`MD-028` extended with `definition`, `clock_start_event` and `clock_stop_event` columns** — outstanding, `O-03`, `O-04`
- [ ] **`SLA-P1` and `SLA-P4` defined; `SLA-P1` is required by `BRU-SRM-10`** — outstanding, `O-05`
- [ ] **Attainment threshold registered** — outstanding, `O-07`
- [ ] **Bengali parallel credit-calculation text authored and signed off in context** — outstanding, and `DT-031` §3 requires parallel columns
- [ ] Named approver recorded — pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
