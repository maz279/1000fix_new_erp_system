---
id: FIX-ERP2-M43
module_id: M43
module_code: DPL
module_name: Demand Planning & Replenishment
category: E — Supply Chain & Inventory
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Warehouse Manager
system_owner: Supply Chain Squad
priority: P2
wave: W6
---

# M43 — Demand Planning & Replenishment
### Category E · Code `DPL` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M43 |
| **Module code** | `DPL` |
| **Category** | E — Supply Chain & Inventory |
| **Status** | ★ **New** — split out of M15 after enterprise benchmarking |
| **Priority** | **P2** |
| **Delivery wave** | **W6** (Months 23–26) — deliberately late; see §2 |
| **Business owner** | Warehouse Manager |
| **System owner** | Supply Chain Squad |
| **Delivery layers** | L1 Odoo reordering-rule substrate · L2 OCA `stock-logistics-warehouse` planning helpers · L4 statistical libraries · L5 custom planning engine, policy engine and network balancer |
| **Custom modules** | `cd_demand_plan`, `cd_replenishment_policy`, `cd_network_balance` |
| **Requirement range** | FR-DPL-001 … FR-DPL-032 |
| **Requirement count** | **32** *(measured — supersedes the 24 estimate in `02-02`)* |
| **Effort estimate** | **17 person-weeks** *(measured — supersedes the 14 PW estimate)* |
| **Depends on** | **M15 Inventory (24 months of clean history)** · M26 AI/ML Services · M62 Data Platform · M37 Catalogue · M42 Supplier Relationship · M16 Procurement · M41 Warehouse · M44 Import |
| **Depended on by** | M15, M16, M41, M44, M02, M54, M25 |

---

## 2. Purpose

M43 answers the one question the rest of Category E deliberately refuses to answer:
**how much should we hold, where, and when should we order more?**

M15 knows what exists. M41 knows where it sits. M16 knows how to buy it. None of them decides
the *quantity*. Today that decision is made by a store keeper's instinct — order when the shelf
looks empty, order what fitted last time — and it produces the twin failures of every unplanned
service parts business: **stockouts on the parts that stop jobs, and dead stock on the parts
that felt safe to buy.**

M43 replaces instinct with a policy: for each part at each location, a segment, a forecast, a
service-level target, a safety stock, a reorder point and a reorder quantity — all derived from
evidence, reviewed on a cycle, and measured against outcomes.

### Why It Is Deliberately Late

M43 is scheduled for **Wave 6, two waves after every other Category E module**, and this is a
design decision rather than a resourcing one.

> Demand forecasting requires clean consumption history. That history only exists after M15 has
> been live through W2–W5. Deploying forecasting before there is history produces bad forecasts,
> and **bad forecasts destroy trust in planning permanently** — a planner who is burned once by
> a system-recommended order reverts to instinct and never returns.

The category overview records this as a risk with the mitigation "M43 deferred to W6
deliberately". This specification treats the 24-month history requirement as a hard entry
condition, not an aspiration (BRU-DPL-01).

### Why It Exists

Three quantified arguments.

**Stockouts stop jobs.** Part availability at first request is targeted at 93% (KPI-043) and
stockout-caused job delays below 3% (KPI-044). M15 makes the stockouts visible; only M43 can
reduce them, because the cause is a stocking decision made weeks earlier.

**Dead stock is capital set on fire.** The target is under 5% of inventory value (KPI-046).
Dead stock is not a disposal problem — it is a purchasing decision made without a forecast.

**Service parts demand is intermittent, and ordinary forecasting fails on it.** Most of 10,000
SKUs move a handful of times a year at unpredictable intervals. Moving averages and exponential
smoothing are demonstrably inappropriate for this pattern; they systematically over-forecast
after a demand event and under-forecast during a gap. This is a well-studied problem with
well-established methods, and applying the wrong one is worse than not forecasting at all.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD BR-INV-006 | "Automatically generate replenishment alerts when stock falls below configured minimum levels" — M43 sets the levels, M15 raises the alerts |
| ERP BRD BR-INV-002 | "Track van/mobile stock per technician" — van par levels are a planning parameter |
| ERP BRD BR-INV-015 | "Identify and report dead stock (no movement in configurable period)" — M15 detects it, M43 prevents it |
| ERP BRD BR-SCM-003 | "Auto-generate purchase orders from approved replenishment alerts" — the planned-order hand-off to M16 |
| `_CATEGORY_OVERVIEW.md` §6 | "Reorder point, safety stock, forecast → M43; M15 executes the alert" and "Forecast model itself → M26; M43 owns the planning process" |
| `_CATEGORY_OVERVIEW.md` §7 | Forecast accuracy target: **MAPE < 22% for A-class parts** |
| `_CATEGORY_OVERVIEW.md` §8, §9 | "M43 is deliberately late: demand forecasting requires two years of clean consumption history" |
| `06-02` KPI-043 / KPI-044 / KPI-045 / KPI-046 | Availability 93%, stockout delays < 3%, turns 6+, dead stock < 5% — all outcomes M43 is the primary lever on |
| Exec Summary §6.2 | Inventory cost reduction **BDT 34 lac/year**, attributed explicitly to "**M15 + M26 demand forecasting**" |
| `02-01` §4 | "M26 AIM → consumes from M25, writes recommendations to M02, M11, **M15**, M17" — the forecasting model's delivery path |

---

## 3. Scope Boundary

> **The rule:** M43 owns *the planning process and the parameters it produces*. It does not own
> the mathematics (M26), the stock (M15), or the purchase (M16). It is the discipline that
> connects them.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Consumption history assembly, cleansing and outlier treatment across all locations |
| 2 | Demand history quality assessment and readiness gating |
| 3 | Part segmentation: ABC by value, XYZ by variability, criticality, intermittency and lifecycle stage |
| 4 | Demand-stream separation: routine repair, warranty campaign, contract-driven, project and rental demand |
| 5 | Forecast generation orchestration — method selection, invocation of M26 models, and fallback |
| 6 | Forecast review, manual adjustment with recorded rationale, and consensus sign-off |
| 7 | Forecast accuracy measurement, bias detection and method re-selection |
| 8 | Service-level target setting per segment and criticality |
| 9 | **Safety stock calculation** by segment, service level, demand variability and lead-time variability |
| 10 | **Reorder point, minimum, maximum, reorder quantity and economic order quantity** per part per location |
| 11 | Lead-time modelling from actual supplier and import performance, including variability |
| 12 | Replenishment policy assignment: reorder point, min-max, periodic review, or manual |
| 13 | Planned-order generation and release to M16, with consolidation across locations |
| 14 | **Network (multi-echelon) planning**: central-versus-branch stocking decisions and forward-stocking-location policy |
| 15 | **Network rebalancing proposals**: surplus at one location covering shortage at another |
| 16 | **Van stock par-level calculation** and periodic re-optimisation per technician and zone |
| 17 | New part introduction: initial stocking recommendation without history, by analogy and installed base |
| 18 | Supersession and end-of-life planning: run-down, last-time-buy and transition |
| 19 | Excess, obsolescence and dead-stock prevention: early-warning and disposition proposals |
| 20 | Seasonality, campaign and installed-base-driven demand adjustment |
| 21 | Plan simulation and what-if: service level versus inventory investment trade-off |
| 22 | Planning exception management and the planner's daily worklist |
| 23 | Inventory investment planning and turns targeting by category and location |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **The forecasting model itself** — algorithm, training, versioning, serving, drift monitoring | **M26** AI/ML Services & Model Operations | M43 owns the planning *process*; M26 owns the mathematics and its lifecycle. Stated explicitly in `_CATEGORY_OVERVIEW.md` §6 |
| Stock balances, reservations, movements, valuation | **M15** | M43 reads positions; it never moves or values stock |
| The replenishment **alert** itself | **M15** | M43 sets the reorder point; M15 detects the breach and raises the alert |
| Requisition, approval, RFQ, purchase order | **M16** | M43 proposes a planned order; M16 turns it into a commitment |
| Supplier qualification, agreements, scorecards | **M42** | M43 consumes lead-time and reliability facts; it does not manage the supplier |
| Physical put-away, picking, warehouse capacity execution | **M41** | M43 informs slotting through velocity; M41 executes |
| Import lead time, shipping and customs execution | **M44** | M43 models the lead time; M44 delivers against it |
| Data warehouse, pipelines, feature store, data quality platform | **M62** Data Platform | M43 is a consumer of governed data, not a data platform |
| Dashboards and self-service reporting infrastructure | **M25** BI | M43 owns planning reports; M25 owns the reporting platform |
| Budget, cost-centre planning and financial forecasting | **M54** FP&A | M43 produces the inventory investment plan as an input to M54 |
| Technician van consumption capture | **M02** Field Service | M43 sets the par level; M02 consumes against it; M15 reconciles it |
| Sales and revenue forecasting | **M07** / **M11** / **M54** | Parts demand is derived from service volume, not from a sales plan |
| Service demand and capacity forecasting | **M02** (with M26) | Different object, different horizon; M43 consumes the output as a driver |

### 3.3 Shared Concepts

| Concept | M43's Role | Owning Module |
|---|---|---|
| Consumption history | Assembles, cleanses and segments; M15 authors the source records | M15 / M43 |
| Forecast | Owns the process, the review and the accuracy measurement; M26 owns the model | M43 / M26 |
| Replenishment parameter (ROP, safety stock, min/max, EOQ) | **Owns** | M43 |
| Replenishment alert | Sets the trigger; M15 raises it | M43 / M15 |
| Planned order | **Owns** until release; M16 owns it thereafter | M43 / M16 |
| Van par level | **Owns** the calculation; M15 owns the enforcement and reconciliation | M43 / M15 |
| Lead time | Owns the *model* including variability; M42 owns the *quoted* lead time; M16 and M44 supply actuals | M43 / M42 |
| Network stocking policy | **Owns** | M43 |
| Dead stock | Owns prevention and disposition proposal; M15 owns detection and provisioning | M43 / M15 |
| Supersession | Owns the run-down and transition plan; M37 owns the supersession chain | M43 / M37 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA extended Service Parts Planning (eSPP)** | Forecasting, inventory planning, distribution requirements planning across a predefined distribution hierarchy, service-level-driven targeting, deployment and procurement of service parts at high SKU volume | **The multi-echelon principle**: a service parts network is planned as a network, with central and forward stocking decided together, not as independent locations each running its own reorder point. **DRP orchestration** — forecast plus current inventory plus transport schedules producing a restocking plan for every location — is the model for our network planning run | The full eSPP stack, deployment engine and its configuration weight. At 10,000 SKUs, roughly 60 stocking locations and one country, eSPP would be an implementation project larger than the rest of Category E combined |
| **PTC Servigistics** | Purpose-built for sparse and erratic service parts demand; demand-stream separation (routine maintenance vs recall vs campaign analysed separately); low-volume sporadic forecasting methods | **Demand-stream separation is adopted directly.** A warranty campaign, a corporate contract roll-out and routine walk-in repair are different demand processes; forecasting their sum guarantees a poor forecast of each. Also adopted: criticality-driven service-level differentiation rather than a single target | The proprietary optimisation engine and its licence model |
| **Syncron / Lokad (spare parts optimisation)** | Probabilistic demand modelling, service-level versus inventory trade-off curves, economic stocking decisions | **The trade-off curve as the planner's primary decision aid**: "this service level costs this much inventory" is a more useful artefact than a single recommended number. Also adopted: probabilistic rather than point thinking for A-class critical parts | Full probabilistic optimisation across the whole catalogue; applied to A and critical parts only |
| **Croston's method and its variants (SBA, TSB)** | Separate forecasts of inter-demand interval and demand size when demand occurs; the standard approach to intermittent demand | **Croston-family methods as the default for intermittent parts.** The literature is unambiguous that single exponential smoothing is inappropriate for intermittent demand, and the majority of a 10,000-SKU service parts catalogue is intermittent. Bootstrapping is adopted for lead-time demand distribution on critical parts | Naive application of Croston to all parts. Fast-moving consumables are better served by conventional smoothing; method selection is per segment |
| **Oracle Fusion Cloud — min-max and replenishment planning** | Min-max planning by subinventory, replenishment count, planning at organisation and subinventory level | Min-max as the appropriate policy for branch and van locations, where simplicity and predictability matter more than optimality | Oracle's planning-hierarchy configuration depth |
| **ABC/XYZ nine-box practice** | Classification by value (ABC) crossed with demand variability (XYZ), yielding nine strategies | **The nine-box is the segmentation spine of M43.** AX gets tight control and high service; CZ gets a low-effort policy or no stock at all. It also drives cycle-count frequency in M15 and slotting in M41 — one segmentation, three consumers | — |
| **Odoo 19 CE reordering rules + OCA** | Min/max reordering rules, orderpoint, procurement groups | The execution substrate for parameter enforcement, driven by M43's computed values rather than by manually maintained rules | Odoo reordering rules as the *planning* mechanism — they are storage for a decision, not a way to make one |

**Design position.** Five deliberate differences.

First, **method selection is per segment, and the default for a service parts catalogue is
intermittent-demand methods**. Most ERP planning modules assume smoothly moving inventory and
offer intermittent handling as an option. We invert the default: a part is treated as
intermittent unless its movement pattern says otherwise. Getting this backwards is the single
most common cause of failed spare-parts planning implementations.

Second, **the planner is in the loop, permanently**. M43 produces recommendations, exposes the
reasoning, and requires review before parameters change for A and critical parts. Fully
automated parameter setting is achievable and is deliberately not the target for Wave 6. Trust
must be earned before it is spent, and the first year of forecasts will contain the artefacts
of a business that has only just started measuring itself.

Third, **M43 owns the process, M26 owns the model — and the boundary is enforced by an
interface, not by convention**. M43 calls the ML gateway with a demand series and a segment,
and receives a forecast with a confidence interval and a method identifier. If M26 is
unavailable or a model has drifted, M43 falls back to a documented statistical method and marks
the forecast as degraded. Planning never stops because a model is down.

Fourth, **the van fleet is planned, not stocked by habit**. 200–400 vans each holding a
technician's guess is the largest uncontrolled inventory in the business. Par levels computed
from zone-level and skill-level consumption, refreshed quarterly, convert that from a liability
into a designed forward-stocking network.

Fifth, **the 24-month history requirement is a hard gate**. M43 will not generate a forecast for
a part-location combination whose history fails the readiness test. It will say so, and fall
back to an analogy-based or manual parameter with an explicit provisional flag. A planner who
can see which recommendations are trustworthy will use the system; one who cannot will abandon
it.

---

## 5. Functional Areas & Features

### 5.1 Demand History, Quality & Segmentation

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DPL-001 | Consumption history assembly | Assemble consumption history per part per location from M15 movements, at daily grain, retaining the causing job type, business line and demand source | **P0** | L5 |
| FR-DPL-002 | **Demand-stream separation** | Separate demand into streams — routine repair, warranty campaign, contract and AMC scheduled work, project roll-out, rental fleet, refurbishment — and forecast each independently before aggregating | **P0** | L5 |
| FR-DPL-003 | Outlier detection and treatment | Detect and treat outliers — a single 200-unit project order inside a 2-unit-per-month history — with the planner able to include, exclude or reclassify, and every decision recorded | **P0** | L5 |
| FR-DPL-004 | Censored demand correction | Correct for demand that did not occur because stock was unavailable, using M15 stockout and unmet-demand events, so that history reflects true demand rather than constrained supply | P1 | L5 |
| FR-DPL-005 | **History readiness gate** | Assess history sufficiency per part-location — length, density, completeness, migration contamination — and refuse to publish a statistical forecast where the test fails, falling back with an explicit provisional flag | **P0** | L5 |
| FR-DPL-006 | **ABC/XYZ segmentation** | Classify every part by annual consumption value (ABC) and demand variability (XYZ) into the nine-box, at both network and location level, and publish it for use by M15 counting and M41 slotting | **P0** | L5 |
| FR-DPL-007 | Criticality classification | Classify parts by consequence of unavailability — job-stopping, deferrable, cosmetic — using M01 and M31 job data, and use it to differentiate service-level targets | **P0** | L5 |
| FR-DPL-008 | Intermittency classification | Classify demand pattern as smooth, erratic, intermittent or lumpy from inter-demand interval and coefficient of variation, and use it to select the forecasting method | **P0** | L5 |
| FR-DPL-009 | Lifecycle stage | Classify parts as new, growth, mature, declining or end-of-life from installed-base and consumption trend, and adjust policy accordingly | P1 | L5 |

### 5.2 Forecasting & Forecast Management

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DPL-010 | Forecast orchestration | Generate forecasts on a defined cycle by selecting the method appropriate to the segment and invoking the model through M26's ML gateway, with the horizon set to cover lead time plus review period | **P0** | L5 |
| FR-DPL-011 | Method selection | Select the forecasting method per part by intermittency class — Croston-family for intermittent and lumpy, exponential smoothing family for smooth and erratic, bootstrapping for lead-time demand distribution on critical parts — and record the method used on every forecast | **P0** | L5 |
| FR-DPL-012 | Degraded-mode fallback | Fall back to a documented statistical method, computed locally, when M26 is unavailable or a model has drifted, and mark the forecast as degraded | **P0** | L5 |
| FR-DPL-013 | Driver-based adjustment | Adjust forecasts for known drivers: installed base from M17, contract and AMC schedules from M08, warranty campaigns from M09, seasonality, and branch openings | P1 | L5 |
| FR-DPL-014 | Forecast review and override | Present the forecast with its history, method, confidence interval and drivers, and allow a planner override with a mandatory rationale, retaining both the statistical and the final number | **P0** | L5 |
| FR-DPL-015 | Consensus sign-off | Run a periodic planning cycle in which procurement, operations and finance review and sign off the plan for A-class and critical parts | P2 | L5 |
| FR-DPL-016 | **Forecast accuracy and bias** | Measure forecast accuracy at every horizon using MAPE for regular demand and appropriate intermittent-demand measures for sparse series, detect systematic bias, and report accuracy by segment, method and planner | **P0** | L5 |
| FR-DPL-017 | Method re-selection | Re-evaluate method selection where accuracy degrades persistently, and propose a change to the planner and to M26 | P1 | L5 |

### 5.3 Inventory Policy & Parameters

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DPL-018 | Service-level targets | Set target service levels by segment, criticality and location type — for example 98% for A-class job-stopping parts at central, 85% for C-class deferrable at branch | **P0** | L5 |
| FR-DPL-019 | **Lead-time modelling** | Model lead time per part per supplier from actual M16 receipt performance and M44 import cycle times, capturing both mean and variability, and distinguishing domestic from imported supply | **P0** | L5 |
| FR-DPL-020 | **Safety stock calculation** | Calculate safety stock from demand variability, lead-time variability and the target service level, using the method appropriate to the demand pattern, and never from a flat multiplier | **P0** | L5 |
| FR-DPL-021 | **Reorder parameters** | Calculate reorder point, minimum, maximum, reorder quantity and economic order quantity per part per location, respecting supplier minimum order quantity, pack size, shelf life and budget constraints | **P0** | L5 |
| FR-DPL-022 | Policy assignment | Assign a replenishment policy per part-location — continuous reorder point, periodic review, min-max, or no-stock/order-on-demand — appropriate to segment and location type | **P0** | L5 |
| FR-DPL-023 | Parameter governance | Require planner review before parameters change for A-class and critical parts; permit automatic application for B and C classes within configured guard rails; publish approved parameters to M15 | **P0** | L5 |
| FR-DPL-024 | **Trade-off simulation** | Simulate the effect of a service-level target on inventory investment and stockout risk, and present the trade-off curve per category and location | P1 | L5 |

### 5.4 Replenishment, Network & Van Planning

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DPL-025 | Planned-order generation | Generate planned orders from projected position, forecast, open supply and parameters, and release them to M16 as draft requisitions (BR-SCM-003) | **P0** | L5 |
| FR-DPL-026 | Order consolidation | Consolidate planned orders across locations and time buckets to reach economic quantities, supplier minimums and container or shipment economics for imports | P1 | L5 |
| FR-DPL-027 | **Network stocking policy** | Decide which parts are stocked centrally only, which are forward-stocked at branches, and which are held on vans, using criticality, value, demand density and transfer lead time | **P0** | L5 |
| FR-DPL-028 | **Network rebalancing** | Identify surplus at one location covering shortage or projected shortage at another, and propose transfers to M15 ranked by benefit against transfer cost | P1 | L5 |
| FR-DPL-029 | **Van par-level optimisation** | Compute minimum and maximum par levels per part per van from zone-level consumption, technician skill profile, job mix and first-time-fix impact, and refresh them on a defined cycle | **P0** | L5 |
| FR-DPL-030 | New part introduction | Recommend an initial stocking position for a part with no history, by analogy to a similar part, installed base from M17, and brand or model launch data | P1 | L5 |
| FR-DPL-031 | Supersession and end-of-life | Plan the run-down of a superseded part and the introduction of its successor, and calculate a last-time-buy quantity where a part is going out of supply | P1 | L5 |
| FR-DPL-032 | Exception worklist and excess prevention | Present the planner a prioritised daily worklist — projected stockouts, excess build-up, parameter breaches, forecast failures, expiring last-time-buy windows — with the value at stake on each, and propose disposition for emerging excess before it becomes dead stock | **P0** | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **History integrity and provenance** | Every demand data point traces to its M15 movement. Adjustments — outlier treatment, censored-demand correction, reclassification — are stored as an overlay, never as an edit to the source series |
| T-02 | **Readiness gate as a hard precondition** | The readiness test evaluates series length, demand density, completeness and migration contamination. A part-location failing the test cannot have a statistical forecast published (BRU-DPL-01) |
| T-03 | **Model boundary via the ML gateway** | M43 calls M26's ML inference gateway with a demand series, a segment and a horizon, and receives a point forecast, a distribution or interval, and a method and model-version identifier. M43 contains no model training code |
| T-04 | **Deterministic fallback** | The degraded-mode statistical fallback is implemented within M43, is deterministic, and is unit-tested against known series. Planning continues when M26 does not |
| T-05 | **Parameter versioning** | Every published parameter set is versioned with its inputs, method, forecast reference, approver and effective date. The parameter in force on any past date is recoverable |
| T-06 | **Explainability** | Every recommendation exposes its drivers: forecast, demand variability, lead time and its variability, service target, constraints applied. A planner who cannot see why will not trust it |
| T-07 | **Planning run scale and duration** | A full network planning run over 10,000 parts × ~60 stocking locations plus 400 vans completes within a 4-hour overnight window; an incremental run for a single category completes in ≤ 10 minutes |
| T-08 | **Idempotent runs** | A planning run is idempotent; re-running with the same inputs produces the same parameters and does not duplicate planned orders |
| T-09 | **Simulation isolation** | What-if simulation executes against a snapshot and can never write parameters or planned orders |
| T-10 | **Event emission via outbox** | Parameter publication, planned-order release, rebalancing proposals and exception alerts emit through the transactional outbox (AS-08) |
| T-11 | **Warehouse-based computation** | Statistical computation runs against the M62 analytical store (ClickHouse), not against the OLTP database, so planning load never affects branch operations |
| T-12 | **Multi-entity and location scoping** | Parameters are scoped to (part, location, company); a second country plans independently on the same engine (AS-03, BO-18) |
| T-13 | **Guard rails on automatic application** | Automatic parameter application for B and C classes is bounded: no change greater than a configured percentage, no change increasing inventory value beyond a threshold, without planner review |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M43 |
|---|---|---|
| **Branch store keeper** | Orders when the shelf looks low; over-orders what recently ran out | Min and max are set for them; replenishment is triggered, not remembered |
| **Inventory manager** | Cannot answer "how much should we hold" for any part | Holds a policy per segment, a defensible parameter per part, and a measurable trade-off between service and capital |
| **Procurement officer** | Receives urgent requests with no forward view | Receives consolidated planned orders with lead-time-aware timing; emergency buying falls |
| **Technician** | Carries what accumulated in the van | Carries a par set designed from the jobs actually done in their zone |
| **Dispatcher** | Discovers parts constraints at assignment | Fewer constraints to discover, because the right parts are forward-stocked |
| **Warehouse manager** | Slotting and counting driven by intuition | Consumes one segmentation for counting frequency, slotting and stocking policy |
| **CFO** | Inventory value is what it is | Inventory investment becomes a planned number with a stated service-level consequence |
| **Operations director** | Stockouts are a recurring complaint without a lever | A measurable availability target with an owner and a mechanism |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Inventory cost reduction** | Right quantity in the right place: safety stock sized to actual variability instead of habit; central pooling for slow movers; dead stock prevented at the point of ordering | **BDT 34 lac per year** — the Executive Summary attributes this benefit explicitly to "M15 + M26 demand forecasting", and M43 is the planning process that turns the forecast into a stocking decision |
| **Part availability at first request** | Service-level targets differentiated by criticality; forward stocking of job-stopping parts | **KPI-043 → 93%.** M15 measures it; only M43 can move it |
| **Stockout-caused job delays** | Reorder points computed from lead-time and demand variability rather than from a flat minimum | **KPI-044 → < 3%** |
| **Inventory turns** | Excess prevented, slow movers centralised, order quantities economic rather than convenient | **KPI-045 → 6+ per year** |
| **Dead stock** | Early-warning on emerging excess; last-time-buy sized to run-down demand; no-stock policy for CZ parts | **KPI-046 → < 5% of value** |
| **Emergency purchase reduction** | Planned replenishment removes the cause of most emergency buying | Supports M16's **< 8% of spend** target; emergency buying carries a 15–30% price premium |
| **Van stock efficiency** | Par levels designed from zone consumption rather than accumulated by habit | Reduces the value tied up across 200–400 vans while improving first-time fix (KPI-004) |
| **Import order economics** | Consolidation to container and shipment economics, with import lead time modelled explicitly | Reduces per-unit freight and duty-handling cost on the imported base (with M44) |
| **Working capital** | Inventory investment planned and targeted rather than accumulated | A one-time cash release plus an ongoing reduction in growth of stock relative to revenue |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Decisions become defensible** | "We hold 12 because the service target is 95%, demand variability is X and lead time is 42 days ± 9" is a different conversation from "we always hold a dozen" |
| **Institutional memory** | Stocking knowledge stops living in individuals |
| **The first real use of the data asset** | M43 is where four years of disciplined transaction capture begins to pay back analytically. It is also the proving ground for M26 in a domain with clear, measurable outcomes |
| **Scalability of the branch network** | 1000FiX Station expansion adds locations. Without planning, each new branch is stocked by guesswork and repeats every mistake |
| **Supplier negotiation** | A forward plan shared with a supplier buys better prices and better lead times than a sequence of urgent orders |
| **Preparation for a second country** | A planning engine scoped by entity and location makes a new country a data problem, not a method problem (BO-18) |
| **Discipline of measurement** | Forecast accuracy is measured and published. Few disciplines in the business will be held to that standard, and it raises the standard elsewhere |

---

## 8. Lifecycle & State Models

### 8.1 The Planning Cycle

```
   ┌──────────────────────────────────────────────────────────────┐
   │                    MONTHLY PLANNING CYCLE                    │
   └──────────────────────────────────────────────────────────────┘

   1. HISTORY REFRESH          M15 movements → M62 warehouse
          │                    outlier treatment · censored-demand correction
          ▼
   2. READINESS GATE           per part-location: length · density ·
          │                    completeness · migration contamination
          │                    ── fails ──► PROVISIONAL / analogy / manual
          ▼
   3. SEGMENTATION             ABC × XYZ · criticality · intermittency ·
          │                    lifecycle → published to M15 and M41
          ▼
   4. FORECAST GENERATION      method by segment → M26 ML gateway
          │                    ── M26 unavailable ──► DEGRADED (local fallback)
          ▼
   5. FORECAST REVIEW          planner override with rationale;
          │                    consensus sign-off for A and critical
          ▼
   6. PARAMETER CALCULATION    service target · lead time + variability ·
          │                    safety stock · ROP · min/max · EOQ
          ▼
   7. PARAMETER GOVERNANCE     A + critical → planner approval
          │                    B + C        → auto within guard rails
          ▼
   8. PUBLICATION              parameters → M15 (executes alerts)
          │                    van par levels → M15
          ▼
   9. PLANNED ORDERS           projected position vs parameters
          │                    consolidation → M16 draft requisitions
          ▼
  10. REBALANCING              surplus/shortage matching → M15 transfers
          │
          ▼
  11. MEASUREMENT              forecast accuracy · bias · service level
          │                    achieved · turns · excess
          └──────────────────► feeds the next cycle and M26 retraining
```

### 8.2 Planned Order Lifecycle

```
        ┌──────────────┐
        │  PROJECTED   │  the run identifies a future shortfall
        └──────┬───────┘
               │ within the planning horizon
        ┌──────▼───────┐
        │   PLANNED    │  quantity, source and date computed
        └──────┬───────┘
               │ consolidation across locations and buckets
        ┌──────▼───────┐
        │ CONSOLIDATED │
        └──────┬───────┘
               │ planner review (mandatory for A and critical)
        ┌──────▼───────┐         ┌──────────────┐
        │   APPROVED   │────────►│  CANCELLED   │ (demand changed,
        └──────┬───────┘         └──────────────┘  alternate found)
               │ released
        ┌──────▼───────┐
        │  RELEASED    │ ──► M16 draft requisition
        │  TO M16      │
        └──────┬───────┘
               │ M16 approves and orders
        ┌──────▼───────┐
        │  CONVERTED   │  PO reference retained; supply now firm
        └──────┬───────┘
               │ received into stock (M15/M41)
        ┌──────▼───────┐
        │   CLOSED     │  actual lead time recorded → lead-time model
        └──────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| Projected | Planned | Shortfall falls within the planning horizon and the policy permits ordering | System |
| Planned | Consolidated | Consolidation rules improve economics without breaching the required-by date | System |
| Consolidated | Approved | Planner review for A and critical; auto-approval for B and C within guard rails | Planner / system |
| Approved | Released to M16 | Supplier is active in M42 for the category; budget check passes | System |
| Released | Converted | M16 creates and approves the requisition and issues the purchase order | M16 |
| Converted | Closed | Goods received; **actual lead time written back to the lead-time model** | M15 / M41 |
| Any | Cancelled | Demand disappeared, alternate source found, or the planner rejects with a reason | Planner |

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-DPL-01 | **A statistical forecast is not published for a part-location whose history fails the readiness test.** The parameter falls back to analogy or manual and is flagged provisional | **H** | Warehouse Manager |
| BRU-DPL-02 | M43 does not train, host or version forecasting models; all model execution occurs through M26's ML gateway | **H** | CTO |
| BRU-DPL-03 | When M26 is unavailable or a model has drifted, M43 falls back to a deterministic local method and marks the forecast degraded; planning never halts | **H** | CTO |
| BRU-DPL-04 | The forecasting method is selected by intermittency class; single exponential smoothing is not applied to intermittent or lumpy demand | **H** | Warehouse Manager |
| BRU-DPL-05 | Demand streams are forecast separately and aggregated; a campaign or project spike is never mixed into routine demand history | **H** | Warehouse Manager |
| BRU-DPL-06 | A planner override of a forecast requires a recorded rationale; both the statistical and the final value are retained | **H** | Warehouse Manager |
| BRU-DPL-07 | Safety stock is calculated from demand and lead-time variability against a service target; flat multipliers and "weeks of cover" rules are not permitted | **H** | Warehouse Manager |
| BRU-DPL-08 | Parameter changes for A-class and critical parts require planner approval; B and C classes apply automatically only within configured guard rails | **H** | Warehouse Manager |
| BRU-DPL-09 | Lead time is derived from actual receipt performance, not from the supplier's quoted figure; the quoted figure is retained for comparison | **C** | Warehouse Manager |
| BRU-DPL-10 | Reorder quantities respect supplier minimum order quantity, pack size and shelf life; a computed quantity that breaches a constraint is adjusted and the adjustment recorded | **C** | Warehouse Manager |
| BRU-DPL-11 | A planned order is not released to M16 for a supplier that is not active in M42 for the category | **H** | Procurement Manager |
| BRU-DPL-12 | Van par levels are computed by M43 and enforced by M15; a branch may not set a van par level locally without approval | **A** | Inventory Manager |
| BRU-DPL-13 | A rebalancing proposal is generated only where the benefit exceeds the transfer cost | **C** | Inventory Manager |
| BRU-DPL-14 | A last-time-buy quantity requires Inventory Manager approval, and above a value threshold CFO approval, because it creates unavoidable future dead stock | **H** | CFO |
| BRU-DPL-15 | Simulation cannot write parameters or planned orders under any circumstance | **H** | CTO |
| BRU-DPL-16 | Forecast accuracy is measured and published per segment, method and planner, and is not suppressible | **H** | Warehouse Manager |
| BRU-DPL-17 | A part classified CZ — low value, highly erratic — defaults to a no-stock, order-on-demand policy unless it is also job-stopping critical | **C** | Inventory Manager |
| BRU-DPL-18 | Parameters are versioned; the parameter in force on any past date must be recoverable for variance investigation | **H** | CTO |
| BRU-DPL-19 | Consumption occurring while a part was out of stock is corrected for before forecasting, so that history reflects demand rather than availability | **C** | Warehouse Manager |
| BRU-DPL-20 | The inventory investment implied by a published parameter set is reported to Finance before the parameter set takes effect where it changes total investment beyond a threshold | **H** | CFO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.demand.series` | `fix_demand_series` | Cleansed consumption history | part_id, location_id, demand_stream, period, quantity, raw_quantity, adjustments_json, censored_flag, source_move_refs |
| `fix.demand.adjustment` | `fix_demand_adjustment` | Overlay on history | series_ref, period, type (outlier/censored/reclassified), original_value, adjusted_value, reason, actor_id, applied_at |
| `fix.demand.readiness` | `fix_demand_readiness` | The history gate result | part_id, location_id, series_length_months, demand_density, completeness, migration_contaminated, verdict, assessed_at |
| `fix.part.segment` | `fix_part_segment` | The nine-box and beyond | part_id, location_id, scope, abc_class, xyz_class, criticality, intermittency_class, lifecycle_stage, consumption_value_12m, cv, adi, computed_at |
| `fix.forecast` | `fix_forecast` | A published forecast | part_id, location_id, demand_stream, horizon_period, statistical_value, final_value, lower_bound, upper_bound, method, model_version, degraded, provisional, generated_at, run_id |
| `fix.forecast.override` | `fix_forecast_override` | Planner intervention | forecast_id, original_value, override_value, rationale, driver_ref, planner_id, applied_at |
| `fix.forecast.accuracy` | `fix_forecast_accuracy` | Measurement | part_id, location_id, period, horizon, forecast_value, actual_value, error, abs_pct_error, bias, method, segment, measured_at |
| `fix.demand.driver` | `fix_demand_driver` | Known influences | type (installed_base/contract/campaign/seasonality/branch_opening), source_module, source_id, part_scope, location_scope, period_range, expected_impact |
| `fix.lead.time.model` | `fix_lead_time_model` | Lead time and its variability | part_id, supplier_id, source (domestic/import), sample_count, mean_days, std_dev_days, p95_days, quoted_days, last_updated |
| `fix.service.level.target` | `fix_service_level_target` | Policy targets | segment_key (abc/xyz/criticality/location_type), target_fill_rate, target_cycle_service, set_by, effective_from |
| `fix.replenishment.parameter` | `fix_replenishment_parameter` | **The output M15 executes against** | part_id, location_id, version, policy_type, safety_stock, reorder_point, min_qty, max_qty, reorder_qty, eoq, review_period_days, constraints_applied_json, forecast_id, provisional, approved_by, effective_from, effective_to |
| `fix.planning.run` | `fix_planning_run` | One execution of the cycle | run_id, type (full/incremental/simulation), scope, started_at, completed_at, parts_processed, forecasts_generated, degraded_count, parameters_changed, planned_orders_created, state |
| `fix.planned.order` | `fix_planned_order` | Proposed supply | part_id, location_id, quantity, required_by, suggested_supplier_id, source (purchase/transfer/import), consolidated_into_id, state, approved_by, requisition_id, po_id, actual_lead_time_days |
| `fix.network.policy` | `fix_network_policy` | Where a part is held | part_id, central_stock, branch_stock_locations, van_stock, no_stock_locations, rationale, computed_at, approved_by |
| `fix.rebalance.proposal` | `fix_rebalance_proposal` | Surplus-to-shortage matching | part_id, from_location_id, to_location_id, quantity, benefit_value, transfer_cost, net_benefit, state, transfer_id |
| `fix.van.par.recommendation` | `fix_van_par_recommendation` | Computed van par levels | van_location_id, technician_id, zone_id, part_id, min_qty, max_qty, basis_json, computed_at, approved_by, applied_to_m15_at |
| `fix.npi.recommendation` | `fix_npi_recommendation` | New part introduction | part_id, analogy_part_id, installed_base_ref, recommended_initial_qty, locations, confidence, rationale, approved_by |
| `fix.eol.plan` | `fix_eol_plan` | Run-down and last-time-buy | part_id, successor_part_id, run_down_start, projected_remaining_demand, last_time_buy_qty, last_time_buy_value, approved_by, state |
| `fix.planning.exception` | `fix_planning_exception` | The planner worklist | type (projected_stockout/excess/parameter_breach/forecast_failure/ltb_window/readiness_fail), part_id, location_id, value_at_stake, priority, detected_at, assigned_to, resolved_at, resolution |
| `fix.planning.simulation` | `fix_planning_simulation` | What-if analysis | name, scope, base_snapshot_ref, changed_assumptions, resulting_investment, resulting_service_level, resulting_stockout_risk, run_by, run_at |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.stock.move`, `fix.stock.quant`, `fix.stock.classification`, stockout events | M15 | Read (via M62 warehouse for history; REST for current position) |
| `fix.catalogue.item`, supersession chain, pack size, shelf life | M37 | Read |
| `fix.supplier.profile`, activation status, quoted lead times, MOQ, capacity | M42 | Read |
| `fix.purchase.order`, `fix.goods.receipt`, actual receipt dates | M16 | Read for lead-time actuals |
| `fix.import.consignment`, clearance cycle times | M44 | Read for import lead-time actuals |
| ML gateway forecast endpoint, model registry | M26 | REST |
| Analytical warehouse (demand history, features) | M62 | Read |
| `fix.asset` installed base by model and brand | M17 / M49 | Read as a demand driver |
| `fix.contract`, AMC and PM schedules | M08 | Read as a demand driver |
| Warranty campaigns and recalls | M09 | Read as a demand driver |
| `fix.wh.slotting`, throughput and capacity | M41 | Read; publish velocity |
| `fix.technician.profile`, zone and skill profile | M02 | Read for van par computation |
| `fix.budget`, inventory investment envelope | M54 | Read |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-DPL-01 | Nightly | Refresh demand history from M15 into M62; apply outlier and censored-demand overlays | Retain the previous series; flag staleness on the planner worklist |
| AUT-DPL-02 | Monthly, or on demand | Re-evaluate the readiness gate per part-location and update verdicts | Retain previous verdicts |
| AUT-DPL-03 | Monthly | Recompute ABC/XYZ, criticality, intermittency and lifecycle segmentation; publish to M15 (counting) and M41 (slotting) | Retain previous segmentation and alert |
| AUT-DPL-04 | Monthly planning cycle | Select methods by segment, invoke M26, generate forecasts with intervals, record method and model version | **Fall back to the local deterministic method and mark degraded** |
| AUT-DPL-05 | Forecast generated | Apply driver adjustments from M17 installed base, M08 schedules and M09 campaigns | Publish unadjusted with a note |
| AUT-DPL-06 | Forecast published | Recompute lead-time models from M16 and M44 actuals, then compute safety stock and reorder parameters | Retain previous parameters and raise an exception |
| AUT-DPL-07 | Parameters computed | Auto-apply B and C classes within guard rails; queue A-class and critical for planner approval | Queue everything for approval |
| AUT-DPL-08 | Parameters approved | Publish to M15 as the authoritative replenishment parameters; version and date-stamp | Retry; M15 continues on the previous version |
| AUT-DPL-09 | Parameter set changes total inventory investment beyond the threshold | Notify Finance before the effective date | Hold publication and escalate |
| AUT-DPL-10 | Planning run completes | Generate planned orders from projected position, consolidate, and release approved orders to M16 as draft requisitions | Present for manual release |
| AUT-DPL-11 | Weekly | Compute network rebalancing proposals ranked by net benefit and offer them to M15 as transfer suggestions | Report only |
| AUT-DPL-12 | Quarterly, or on zone or roster change | Recompute van par levels and publish approved values to M15 | Retain existing par levels |
| AUT-DPL-13 | New part added in M37 with an installed base | Produce an initial stocking recommendation by analogy and queue it for planner approval | Report as an unplanned part |
| AUT-DPL-14 | M37 records a supersession or a supplier declares end of life | Open a run-down plan, compute projected remaining demand and a last-time-buy quantity, and route for approval | Alert the planner |
| AUT-DPL-15 | Daily | Build the planner exception worklist — projected stockouts, emerging excess, parameter breaches, forecast failures, closing last-time-buy windows — ranked by value at stake | Report only |
| AUT-DPL-16 | Period close | Measure forecast accuracy and bias by segment, method and planner; publish; feed M26 for retraining evaluation | Retry |
| AUT-DPL-17 | Accuracy degrades persistently for a segment | Propose a method change to the planner and notify M26 model owners | Report only |
| AUT-DPL-18 | Emerging excess detected before it becomes dead stock | Propose disposition — stop reordering, rebalance, return to vendor, use in refurbishment — with the value at stake | Report only |

---

## 12. Interfaces

### 12.1 Upstream — M43 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M15 Inventory** | Consumption movements, current positions, stockout and unmet-demand events, in-transit supply | Warehouse extract (M62) + REST |
| **M26 AI/ML Services** | Forecast generation through the ML inference gateway; model versions and drift signals | REST |
| **M62 Data Platform** | The analytical store on which all statistical computation runs | Direct query |
| M37 Catalogue | Part attributes, pack size, shelf life, supersession chain, criticality hints | REST |
| M42 Supplier Relationship | Supplier activation status, quoted lead times, MOQ, capacity constraints, reliability | REST |
| M16 Procurement | Actual receipt dates and quantities for lead-time modelling; open supply | Events + warehouse extract |
| M44 Import | Import cycle times and clearance variability | Events |
| M41 Warehouse | Throughput and capacity constraints; consumes velocity in return | Warehouse extract |
| M17 Asset Registry | Installed base by brand and model — the primary long-run demand driver | REST |
| M08 Contracts | AMC and preventive-maintenance schedules as forward demand | REST |
| M09 Warranty | Campaigns and recalls as demand events | Events |
| M02 Field Service / M21 | Technician zone, skill profile and roster for van par computation | REST |
| M54 FP&A | Inventory investment envelope | REST |

### 12.2 Downstream — M43 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M15 Inventory** | **Replenishment parameters** (ROP, safety stock, min/max, EOQ), van par levels, segmentation, rebalancing proposals | REST + events |
| **M16 Procurement** | Planned orders released as draft requisitions, with recommended supplier, quantity and timing | Commands |
| M41 Warehouse | Velocity bands and stocking policy informing slotting | Events |
| M44 Import | Consolidated import demand and required-by dates for shipment planning | REST |
| M26 AI/ML | Accuracy and bias feedback for model evaluation and retraining | Warehouse extract |
| M54 FP&A | Inventory investment plan and its service-level consequence | REST |
| M42 Supplier Relationship | Forward demand visibility for supplier planning and negotiation | REST |
| M25 BI / M62 | Forecast, parameter, accuracy and service-level facts | Warehouse extract |
| P03 / P06 | Planner workbench and planning dashboards | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `planning.run_completed` | run, scope, counts, degraded count, duration | M15, M16, M25 |
| `segmentation.published` | parts, ABC, XYZ, criticality, intermittency | **M15**, **M41**, M16 |
| `forecast.published` | part, location, horizon, value, interval, method, degraded, provisional | M26, M25 |
| `forecast.degraded` | scope, reason, fallback method used | M26, M25, CTO alerting |
| `parameters.published` | part, location, version, ROP, safety stock, min/max, EOQ, effective from | **M15** |
| `parameters.investment_impact` | scope, prior investment, new investment, delta, service-level effect | M54, M19 |
| `van_par.published` | van, technician, parts, min/max, effective from | **M15**, M02 |
| `planned_order.released` | part, location, quantity, required by, suggested supplier | **M16** |
| `rebalance.proposed` | part, from, to, quantity, net benefit | **M15**, M03 |
| `network_policy.changed` | part, central, branch, van, no-stock locations, rationale | M15, M41 |
| `eol.last_time_buy_required` | part, quantity, value, window closing | M16, M15, CFO |
| `planning.exception_raised` | type, part, location, value at stake, priority | M15, M16, planner |
| `forecast.accuracy_published` | period, segment, method, MAPE, bias | M26, M25 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-DPL-01 | Statistical libraries (`statsmodels`, `scikit-learn`, Croston implementations) | Internal | The deterministic fallback and diagnostic computation inside M43 |
| INT-DPL-02 | Brand partner forward-demand or campaign notices | Inbound | Advance warning of campaigns and model launches; file or email, normalised into demand drivers |
| INT-DPL-03 | Supplier forward-demand sharing (P05) | Outbound | Sharing the forward plan with strategic suppliers to secure lead time and price |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/planning/parameters` | GET | Current replenishment parameters for a part-location | **M15**, P03 |
| `/api/v1/planning/parameters/{id}/approve` | POST | Approve a proposed parameter change | P03 |
| `/api/v1/planning/forecast` | GET | Forecast with interval, method and drivers | P03, P06 |
| `/api/v1/planning/forecast/{id}/override` | POST | Override with rationale | P03 |
| `/api/v1/planning/segments` | GET | ABC/XYZ, criticality, intermittency | **M15**, **M41**, P03 |
| `/api/v1/planning/planned-orders` | GET | Planned orders awaiting review or release | P03, M16 |
| `/api/v1/planning/planned-orders/{id}/release` | POST | Release to M16 | P03 |
| `/api/v1/planning/rebalance` | GET | Rebalancing proposals ranked by net benefit | P03, M15 |
| `/api/v1/planning/van-par/{van}` | GET | Recommended par levels for a van | **M15**, P03 |
| `/api/v1/planning/exceptions` | GET | The planner worklist ranked by value at stake | P03 |
| `/api/v1/planning/simulate` | POST | Run a what-if against a snapshot (never writes) | P03 |
| `/api/v1/planning/accuracy` | GET | Forecast accuracy and bias by segment and method | P03, P06, M26 |
| `/api/v1/planning/runs/{id}` | GET | Planning run status and diagnostics | P03 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R17 Inventory Manager | C R U D A | All parts and locations; approves parameters and last-time-buys within authority |
| R19 Procurement Officer | R | Planned orders, forecasts, lead-time models |
| R18 Branch Store Keeper | R | Own branch parameters and planned orders — visibility only |
| R06 Branch Manager | R | Own branch stocking policy and exceptions |
| R20 Warehouse Operative | – | No access |
| R26 Finance Manager | R A | Inventory investment plan; approves investment-impacting parameter sets |
| R03 Chief Financial Officer | R A | All; approves last-time-buys above threshold and investment envelope changes |
| R05 Operations Director | R | Service-level targets and achievement |
| R02 Chief Technology Officer | R | Model boundary, degraded-mode incidents, planning-run health |
| R33 IT / System Administrator | R U | Run scheduling and configuration; no parameter approval |
| R07 Dispatch Manager | R | Van par levels for own zones |

**Demand Planner role.** M43 introduces a planning function not present in the `05-04` role
register. It is exercised as an **elevated grant on R17 Inventory Manager** covering forecast
override, parameter approval for A-class and critical parts, network policy and simulation.
**Whether Demand Planner becomes a distinct role (R39) is an open question (Q-06) and an audit
action against `05-04`.**

**Field-level restrictions.** Inventory investment values and unit costs follow the `05-04` §5
restriction on `unit_cost` and `total_cost`: visible to R01–R05, R06, R17, R19, R26 and R27.
Branch users see quantities and parameters, not the capital they represent.

**Segregation of duties.**
- A planner may not both override a forecast and approve the parameter derived from it for A-class and critical parts above a value threshold.
- Last-time-buy approval requires Inventory Manager and, above threshold, CFO — the person proposing it cannot be the sole approver.
- Simulation carries no write authority for any user (BRU-DPL-15).

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Planner workbench** | Inventory Manager / Demand Planner | Daily | Exception worklist ranked by value at stake: projected stockouts, emerging excess, parameter breaches, forecast failures, closing last-time-buy windows |
| **Forecast accuracy and bias** | Inventory Manager, CTO, M26 owners | Monthly | MAPE for regular demand and intermittent-appropriate measures for sparse series, by segment, method, horizon and planner; bias direction; **A-class MAPE against the < 22% target** |
| Service level achieved vs target | Operations Director, Inventory Manager | Monthly | Fill rate and availability by segment, criticality and location, against target |
| **Inventory investment plan** | CFO, Finance Manager, Inventory Manager | Monthly | Current and planned inventory value by category and location, with the service-level consequence of each level |
| Service-level / investment trade-off | CFO, Inventory Manager | Quarterly | The trade-off curve per category: what each increment of service costs |
| ABC/XYZ nine-box | Inventory Manager, Warehouse Manager, Procurement | Quarterly | Distribution of parts and value across the nine boxes, with policy per box |
| Segmentation movement | Inventory Manager | Quarterly | Parts changing class, and the parameter consequences |
| Lead-time performance and variability | Procurement Manager, Inventory Manager | Monthly | Actual versus quoted lead time, mean and variability, by supplier and by domestic/import |
| **Excess and obsolescence early warning** | Inventory Manager, Procurement, CFO | Monthly | Parts trending to excess before they become dead stock, with value and proposed disposition |
| Dead stock prevented | Inventory Manager, CFO | Quarterly | Value of proposed disposition acted on, and dead stock avoided |
| Planned order pipeline | Procurement Manager, Inventory Manager | Weekly | Planned, consolidated, approved, released and converted; conversion rate and lead-time compliance |
| Network stocking policy | Inventory Manager, Operations Director | Quarterly | Central versus branch versus van policy by category; forward-stocking coverage |
| Rebalancing effectiveness | Inventory Manager, Logistics Manager | Monthly | Proposals made, accepted, executed, and net benefit realised |
| **Van stock optimisation** | Dispatch Manager, Inventory Manager | Quarterly | Par level changes, van inventory value, first-time-fix correlation |
| Planning run health | CTO, IT Administrator | Daily | Run duration, coverage, degraded-forecast count, readiness-gate failures |
| Readiness coverage | Inventory Manager, CTO | Monthly | Share of part-locations with sufficient history; the trajectory toward full statistical coverage |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W7 Target | W8+ Target |
|---|---|---|---|---|
| — | **Forecast accuracy — MAPE, A-class parts** | n/a | < 28% | **< 22%** |
| — | Forecast bias (systematic over/under) | n/a | ± 8% | **± 4%** |
| **KPI-043** | Part availability at first request *(M15 measures; M43 is the primary lever)* | unmeasured | 90% | **93%** |
| **KPI-044** | Stockout-caused job delays *(M15 measures; M43 is the primary lever)* | unmeasured | < 5% | **< 3%** |
| **KPI-045** | Inventory turns per year *(M15 measures; M43 is the primary lever)* | unmeasured | 5.0 | **6+** |
| **KPI-046** | Dead stock as % of value *(M15 measures; M43 prevents)* | unmeasured | < 7% | **< 5%** |
| — | Part-locations with a statistically derived parameter | 0% | 65% | **85%** |
| — | Parameters accepted without planner override | n/a | 70% | **85%** |
| — | Planned orders converted to purchase orders without amendment | n/a | 75% | **88%** |
| — | Emergency purchases attributable to a planning miss | unknown | < 8% | **< 4%** |
| — | Rebalancing proposals executed | n/a | 50% | **70%** |
| — | Van par-level compliance (van stock within min/max) | untracked | 85% | **95%** |
| — | Degraded-mode forecasts as % of forecasts published | n/a | < 10% | **< 2%** |
| — | Excess value flagged before becoming dead stock | 0% | 70% | **90%** |
| — | Planning cycle completed on schedule | n/a | 95% | **100%** |

> **Register note.** `_CATEGORY_OVERVIEW.md` §7 names **forecast accuracy (MAPE, A-class parts)
> < 22%** as the category KPI owned by M43; it has no canonical `KPI-0nn` identifier in `06-02`
> §2.6. KPI-043 through KPI-046 are registered to **M15**, which measures them; **M43 is the
> primary lever on all four** and shares accountability. Both facts should be recorded in
> `06-02` — an audit action, along with allocation of identifiers for the eleven unregistered
> metrics above.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo 19 reordering-rule and orderpoint substrate — the storage and execution surface for published parameters | 8% |
| L2 | OCA `stock-logistics-warehouse` planning helpers | 6% |
| L4 | Python statistical stack (`statsmodels`, `scikit-learn`, Croston-family implementations) for the deterministic fallback and diagnostics; ClickHouse (M62) for computation at scale | 16% |
| L5 | `cd_demand_plan`, `cd_replenishment_policy`, `cd_network_balance` | 70% |

> **Model execution is not counted here.** Forecast models are built, versioned and served by
> **M26** (`cd_forecast`, CD-115) and are not part of M43's layer allocation or effort estimate.
> This is the boundary made concrete.

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-152** | `cd_demand_plan` — history assembly, adjustment overlays, readiness gate, demand-stream separation, segmentation, forecast orchestration and review, accuracy measurement, planner workbench | Odoo module + service | 7 PW |
| **CD-153** | `cd_replenishment_policy` — service-level targets, lead-time modelling, safety-stock and reorder-parameter calculation, policy assignment, parameter governance and versioning, planned-order generation, simulation | Odoo module + service | 6 PW |
| **CD-154** | `cd_network_balance` — network stocking policy, multi-echelon logic, rebalancing proposals, van par optimisation, new part introduction, end-of-life and last-time-buy planning | Odoo module + service | 4 PW |

> **Dependency on M26.** `cd_forecast` (CD-115, M26) must deliver the intermittent-demand model
> family — Croston and its variants, plus bootstrapping for lead-time demand distribution —
> before M43's W6 go-live. This is a cross-category dependency and is recorded as Q-03.
> CD-152…154 are claimed from the extension block for modules M31–M67 and are **provisional**
> pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M15 Inventory, live since W2** | **The hard entry condition.** M43 requires clean consumption history, and the readiness gate (BRU-DPL-01) enforces it per part-location. This is why M43 is in W6 |
| **M26 AI/ML Services (W6)** | Forecast model execution. M43 and M26 land in the same wave and must be sequenced within it: M26's forecasting models first |
| **M62 Data Platform (W4/W8)** | The analytical store on which planning computes. The W4 slice must include the demand warehouse |
| M16 Procurement (W3) | Actual receipt dates for lead-time modelling; the recipient of planned orders |
| M42 Supplier Relationship (W4) | Supplier activation gate on planned-order release; quoted lead times and MOQ |
| M44 Import (W6) | Import lead-time actuals and consolidated shipment planning |
| M37 Catalogue (W1) | Pack size, shelf life, supersession chain |
| M17 Asset Registry (W2) | Installed base as the long-run demand driver |
| M41 Warehouse (W3) | Velocity exchange for slotting |

> **History-window arithmetic.** W2 begins at month 5 and W6 at month 23 — approximately
> **18 months** of M15 history at M43 go-live, against the 24-month ideal. The readiness gate
> handles this honestly: fast-moving A and B parts will pass at 18 months, while slow-moving C
> and intermittent parts will not and will run on provisional or analogy-based parameters until
> they do. **M43 should be planned to reach full statistical coverage during W7, not at W6
> go-live.** The KPI table above reflects that trajectory.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| M15 consumption history | ~18–24 months × 10,000 parts × ~60 locations | `fix.demand.series` | W6, computed not migrated |
| Legacy consumption records (pre-ERP) | Fragmentary, spreadsheet-based | — | **Not migrated** — see the position below |
| Existing manual min/max values | Where any exist | `fix.replenishment.parameter` (as provisional) | W6, as a starting point only |
| Van stock habitual holdings | 200–400 vans | Input to `fix.van.par.recommendation` | W6, as a comparison baseline |

> **Position on pre-ERP history — non-negotiable.** Pre-ERP consumption records are not
> migrated into the demand series. They were produced by a 75%-accurate inventory process and
> would contaminate the very history the readiness gate exists to protect. They may be retained
> in M62 as a separate, clearly labelled reference set for human comparison; they are never an
> input to a forecast. This mirrors M15's refusal to load the branch spreadsheets as opening
> balances, and for the same reason.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A statistical forecast cannot be published for a part-location failing the readiness gate; the parameter falls back and is flagged provisional | Negative test plus a full-population assertion |
| AC-02 | M43 contains no model training code; all forecast generation occurs through M26's ML gateway | Code review and dependency audit |
| AC-03 | With M26 unavailable, a full planning run completes using the local deterministic fallback and marks every forecast degraded | Induced-outage test on a full run |
| AC-04 | Intermittent and lumpy parts are forecast with Croston-family methods; single exponential smoothing is never applied to them | Method-assignment audit across the full catalogue |
| AC-05 | Demand streams are forecast separately; a project spike injected into one stream does not distort routine-demand forecasts | Scripted scenario with a synthetic campaign |
| AC-06 | Safety stock is computed from demand and lead-time variability against a service target, and a flat-multiplier configuration is not possible | Code review plus negative configuration test |
| AC-07 | Lead time derives from actual M16 and M44 receipt performance, not from the supplier's quoted figure | Data-lineage test |
| AC-08 | Parameter changes for A-class and critical parts cannot take effect without planner approval | Negative test |
| AC-09 | B and C class auto-application is bounded by guard rails; a change beyond a guard rail routes to review | Scripted scenario |
| AC-10 | Published parameters reach M15 and change its replenishment alert behaviour within one cycle | Integration test |
| AC-11 | The parameter in force on any past date is recoverable | Historical query test |
| AC-12 | A planned order cannot be released to M16 for a supplier not active in M42 for the category | Negative test |
| AC-13 | Simulation cannot write a parameter, a planned order or a par level under any circumstance or any role | Negative test across all roles |
| AC-14 | A full network planning run over 10,000 parts × ~60 locations plus 400 vans completes within a 4-hour window | Performance test at production volume |
| AC-15 | A planning run is idempotent; re-running produces identical parameters and no duplicate planned orders | Repeat-run test |
| AC-16 | Every recommendation exposes its drivers — forecast, variability, lead time, service target, constraints | UI and API review |
| AC-17 | Forecast accuracy is measured, published per segment and method, and cannot be suppressed by any role | Negative test plus three months of published measurement |
| AC-18 | A-class MAPE reaches below 22% by Wave 8 | Six months of measurement |
| AC-19 | Van par levels computed by M43 are enforced by M15, and a local override requires approval | Integration and negative test |
| AC-20 | A last-time-buy above threshold cannot be executed without CFO approval | Negative test |
| AC-21 | Pre-ERP consumption records are absent from the demand series used for forecasting | Data-lineage audit |
| AC-22 | Inventory Manager and CFO sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 22 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Is 18 months of history at W6 accepted**, with full statistical coverage reached during W7 — or is M43 deferred to W7 to reach the 24-month ideal? | Warehouse Manager / CTO | W6 minus 6 months |
| Q-02 | What are the service-level targets per segment and criticality? This is a capital-allocation decision, not a technical one. | CFO / Operations Director | W6 build |
| Q-03 | **Will M26's `cd_forecast` (CD-115) deliver the Croston-family and bootstrapping methods** M43 requires, and is that scoped and scheduled within W6? | CTO | W6 minus 6 months |
| Q-04 | What criteria define a job-stopping critical part, and who maintains that designation? M42's alternate-source obligation depends on the same list. | Operations Director / Inventory Manager | W6 build |
| Q-05 | What is the inventory investment envelope, and does M43 plan within it as a constraint or report against it as a consequence? | CFO | W6 build |
| Q-06 | **Is Demand Planner a distinct role (R39) or an elevated grant on R17?** `05-04` has no planning role, and the answer affects the segregation-of-duties model. | HR Director / Warehouse Manager | W6 design |
| Q-07 | What is the guard-rail policy for automatic parameter application on B and C classes — maximum percentage change, maximum value impact? | Inventory Manager / CFO | W6 build |
| Q-08 | Do brand partners provide forward demand signals (campaigns, model launches, known failure modes)? These would be the single highest-value external driver. | CCO / Warehouse Manager | W6 design |
| Q-09 | Is forward demand shared with strategic suppliers through P05, and what commercial protection is required before doing so? | Procurement Manager / Legal | W7 |
| Q-10 | How is rental-fleet and refurbishment parts demand forecast — as a separate stream within M43, or planned within M13 and M14? | Corporate Services Head / Retail Operations Head | W6 design |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §6 (M43 owns the planning process, M26 owns the model), §7 (MAPE < 22%),
§8 (why M43 is late), §9 (the forecasting-before-history risk) ·
`M15_Spare_Parts_and_Inventory_Management.md` §5.7, §12 (parameter consumption and alerting) ·
`M16_Procurement_and_Strategic_Sourcing.md` §5.1 (planned orders into requisitions) ·
`M42_Supplier_Relationship_and_Performance.md` (lead time, reliability, activation gate) ·
`M41_Warehouse_Management.md` §5.1 (segmentation into slotting) ·
`M44_Import_Trade_Compliance_and_Landed_Cost.md` (import lead time and shipment consolidation) ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §4 (M26 writes recommendations to M15) ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 Category E ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §3.3, §5 ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` §2.6 (KPI-043…046)

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-INV-002, BR-INV-006,
BR-INV-015, BR-SCM-003 · Executive Summary §6.2 (BDT 34 lac, "M15 + M26 demand forecasting")

**External benchmark**
[SAP S/4HANA extended Service Parts Planning](https://sapinsider.org/blogs/sap-s4hana-supply-chain-for-extended-service-parts-planning/) —
distribution requirements planning across a distribution hierarchy, service-level-driven
targeting · [SAP Service Parts Management](https://sapinsider.org/topic/sap-supply-chain-management/sap-spm/) ·
[PTC Servigistics — demand streams and low-volume sporadic forecasting](https://www.lokad.com/spare-parts-optimization-software/) ·
[Croston's method for intermittent demand — review](https://www.researchgate.net/publication/254044245_A_Review_of_Croston's_method_for_intermittent_demand_forecasting) —
single exponential smoothing is inappropriate for intermittent demand ·
[Hybrid Croston forecasting with safety-stock optimisation for intermittent spare parts](https://www.ijert.org/a-hybrid-inventory-planning-framework-using-croston-forecasting-and-safety-stock-optimization-for-intermittent-automotive-spare-parts-demand-ijertv15is070024) ·
[Bootstrapping for intermittent service-parts demand](https://smartcorp.com/wp-content/uploads/2015/07/IJF_Bootstrap_paper_Smart_Software.pdf) ·
[Forecasting for inventory management of service parts](https://link.springer.com/chapter/10.1007/978-1-84800-011-7_20) ·
[ABC/XYZ classification — the nine-box and its policies](https://www.scmdojo.com/blog/abc-xyz-analysis-complete-guide) ·
Oracle Fusion Cloud — min-max planning by subinventory · Odoo 19 CE reordering rules as the
parameter execution substrate

---

*Module M43 · Category E · 1000FiX ERP System v2.0 · CONFIDENTIAL*
