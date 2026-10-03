---
id: BM-003
title: Business Case and ROI Model
category: 15 — Benefits, Measurement & Assurance
code: BM
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Financial Officer
approver: Board of Directors, on the recommendation of the ERP Steering Committee
standards_basis: >
  HM Treasury Green Book 2022 (appraisal and evaluation; the Five Case Model, optimism bias,
  discounting) · ISO 21502:2020 §7.9 (cost management) and §7.13 (benefits management) ·
  ISO 21503:2022 (programme management — the business case as a programme control) ·
  MSP 5th edition (business case theme) · PMBOK 7 (Delivery and Measurement performance
  domains) · ISO 15686-5:2017 life-cycle costing, consumed via CO-005 ·
  AACE International Recommended Practice 17R-97 (estimate classification)
traces_to: >
  PGD-000 BM-003 · PGD-A2-10 (CRITICAL — 06-02 §3.2 and §3.4 disagree on three-year benefit by
  2.2×–3.3×) · CO-005 §10.2 ("BM-003 must not simply adopt these figures") ·
  CO-005 §10.1, §7.1, §7.2, §7.3 · CVA-04 (FX assumption unverified) · 00-06 H-02 ·
  BM-002 §3.7 (improvement exposure BDT 542 lac) · BM-002 §3.8 · BRD §19 · 06-02 §3 ·
  GV-008 §7.2, §9 · GV-007 §7.3 · D-014 · RL-005 PIR-25
depends_on: CO-005 (cost basis, consumed unchanged) · BM-002 (claimable benefit) · GV-008 (budget) · GV-007 (effort) · 06-02 §3.1 (benefit lines)
verified_on: 2026-08-19
enumeration_timestamp: 2026-08-19 00:48 (+06)
priority: P0
needed_by: Now
rule_space: BSC
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# BM-003 — Business Case and ROI Model

### Category 15 · Code `BM` · Rule space `BSC` · HM Treasury Green Book 2022 Five Case Model · ISO 21502:2020 §7.9

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `BM-003` exists in `PGD-000` Category 15, status ◐ BRD §19,
>    `P0`, `needed_by: Now`.
> 2. **`PG-03` Count, do not consult.** Every figure below is either **counted**, **carried from a
>    named source unchanged**, or **derived here with its arithmetic shown**. Which of the three
>    applies is stated for every number.
> 3. **`PG-06` Cite standards.** §2.1.
> 4. **`PG-M4` Verify citations.** `verified_on: 2026-08-19`. The FX rate is verified in §4.
>
> **`CO-005` §10.2 gave this document two instructions and they are the reason it exists:**
>
> > *"`BM-003` must not simply adopt these figures. Two problems remain unresolved and both are
> > `BM-003`'s: the annual-versus-cumulative label defect (`PGD-A2-10`), which is worth 2.2×–3.3×
> > on the three-year benefit and is larger than everything in this document; and whether the FX
> > rate should be a spot rate, a forward curve, or a hedged rate."*
>
> §3 resolves the first. §4 resolves the second. §5 adds the third thing no document in this estate
> has ever done: **discount the cash flows.**

---

## 1. Purpose

The Board holds a business case. It is in BRD §19, it is restated in `06-02` §3, and the two
disagree with each other and with their own supporting tables.

**The cost side has already been repaired.** `CO-005` re-derived it to a five-year, two-tier,
life-cycle basis and closed `H-02`. **The benefit side has not been touched since it was written**,
and `PGD-A2-10` records the consequence as **Critical**: the published three-year benefit cannot be
reproduced from the curve that is supposed to generate it, under either reading of that curve.

This document does four things:

| # | Job | Where |
|---|---|---|
| 1 | **Resolve `PGD-A2-10`** — decide, on evidence, whether `06-02` §3.2's column is annual or cumulative, and restate the three-year benefit accordingly | §3 |
| 2 | **Settle the FX basis** for a case whose benefits are earned in BDT and whose costs are largely incurred in USD | §4 |
| 3 | **Produce the discounted case** — NPV, IRR, payback and discounted payback across the scenario corners, which the estate has never had | §5, §6 |
| 4 | **State what is claimable**, not merely what is claimed, using `BM-002`'s corrected baseline position | §7 |

**What this document changes and what it does not.** It changes no benefit line, no target, no cost
line and no effort figure. Every input is carried from `06-02` §3.1, `CO-005` §7 or `BM-002`
unchanged. **What changes is the arithmetic performed on them, and the arithmetic was wrong.**

> **The honest summary, stated at the top because a business case that buries it is not a business
> case.** On the expected cost and the base benefit, this programme has a **negative NPV at every
> discount rate tested** and pays back in **Year 8**, not Year 2. In the low-cost / optimistic
> corner it returns an **IRR of about 48%** and pays back in **Year 4**. In the high-cost /
> conservative corner **its steady-state annual run cost exceeds its steady-state annual benefit**,
> so it never pays back on any horizon. The spread between those corners is the decision, and §8
> is about narrowing it.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **Resolution of `PGD-A2-10`** with the evidence and the restated three-year benefit (§3) |
| 2 | **FX policy** — planning rate, sensitivity band, and the asymmetry between BDT benefit and USD cost (§4) |
| 3 | **The discount rate** — derivation, recommendation and the Board decision (§5) |
| 4 | **The restated case** — annual cash flows, NPV, IRR, payback, discounted payback, three corners (§6) |
| 5 | **Claimed versus claimable** benefit, on `BM-002`'s corrected population (§7) |
| 6 | **Sensitivity**, including the structural finding about steady-state run cost (§8) |
| 7 | **Reconciliation** of every return figure in the estate (§9) |
| 8 | **Five Case Model** mapping, so the case is assessable against a recognised framework (§10) |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| **Every cost line and its derivation** | `CO-005` §5–§7 | **Consumed unchanged** (`BSC-02`). A disagreement is raised to `CO-005`, never resolved here. This mirrors `CO-005`'s own `TCO-02`/`TCO-03` discipline toward `GV-007`/`GV-008` |
| **Effort** | `GV-007` §7.1 | Consumed via `CO-005` |
| **The budget and its contingency** | `GV-008` | A budget is authority to spend; a business case is justification. §10 states the seam, in the Financial Case row |
| **Benefit line values** | `06-02` §3.1 | Carried unchanged. This document restates *when* they arrive and *what they are worth discounted*, never *how large* they are |
| **Baseline measurement** | `BM-002` | Consumed. §7 uses its corrected population |
| **Benefit ownership, tracking, the miss rule** | `BM-004` | This document forecasts; `BM-004` tracks. `RL-005` `PIR-25` keeps them separate |
| **Option pricing A–E** | `CO-005` §11 | Referenced in §8.5, not re-priced |
| **Procurement strategy** | `CO-002`, `CO-003` | |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Board of Directors** | §1's summary, §6.5's three corners, §8.5's decision. This is the document `D-014` is decided against |
| **CFO** | The whole model; §5's discount-rate decision is the CFO's recommendation to the Board |
| **ERP Steering Committee** | §7 — why funding `BM-002` changes the case by more than any other single act |
| **Enterprise Architecture** | §3 — the label defect and the six documents that must be corrected |
| **Internal audit / `GV-010`** | §9's reconciliation, and §11's rules, which are what an assurance review tests against |
| **Prospective vendors** | Not an audience. §1.1 boundaries and `CO-002` govern what is disclosed |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this document conforms | Departure and rationale |
|---|---|---|---|
| **HM Treasury Green Book 2022** *(current edition, published 31 March 2022; verified 2026-08-19)* | Five Case Model; discounting; optimism bias | §10 maps the case to the five cases. §5 discounts. §8.4 applies an explicit optimism-bias adjustment rather than leaving it implicit | **Departure:** the Green Book's 3.5% Social Time Preference Rate is a *public-sector* rate for social value. This is a private commercial investment in Bangladesh, so §5 derives a commercial hurdle rate instead and says so. **Using 3.5% here would flatter the case by a wide margin** |
| **ISO 21502:2020** | §7.9 cost management; §7.13 benefits management | The business case as a live control re-tested at each gate (`BSC-13`) | None |
| **ISO 21503:2022** | Programme business case | Benefit-to-cost traceability at programme level | None |
| **MSP 5th edition** *(PeopleCert; current)* | Business case theme | The case is maintained, not written once; reviewed at every gate | **Departure:** MSP expects the business case to precede the blueprint. Here it follows 133 specification documents; §3 is the price of that inversion |
| **PMBOK 7** | Delivery, Measurement performance domains | Value delivery measured, not assumed | None |
| **ISO 15686-5:2017**, **AACE 17R-97** | Life-cycle costing; estimate classes | **Consumed via `CO-005`**, not re-applied | `BSC-02` |

### 2.2 Source material relied on, and how each is used

> **`BSC-01`. Every figure in this document is labelled `[carried]`, `[counted]` or `[derived]`.**
> A business case in which the reader cannot tell which numbers were computed here is a business
> case that cannot be audited.

| Source | What is taken | Label |
|---|---|:--:|
| `06-02` §3.1 | The 14 benefit lines: 521 / 876 / 1,273 BDT lac | `[carried]` |
| `06-02` §3.2 | The realisation curve: 45 / 310 / 645 / 876 / 920 | `[carried]`, **re-labelled** in §3 |
| `06-02` §3.4, BRD §19.4 | The two published Return tables | `[carried]` for reconciliation only; **superseded** by §6 |
| `CO-005` §7.1 | Tier 1 three-year cost: 1,488 / 2,558 / 4,330 (`$K`) | `[carried]` |
| `CO-005` §7.2 | Years 4–5: 207/337/506 and 217/354/531 | `[carried]` |
| `CO-005` §7.3 | Five-year Tier 1: 1,912 / 3,249 / 5,367; Tier 2: 2,311 / 3,977 / 6,568 | `[carried]` |
| `CO-005` §10.1, §10.2 | FX 122.70; the benefit conversion; payback at that rate | `[carried]` |
| `BM-002` §3.7 | Improvement exposure **BDT 542 lac**, absolutes **334 lac** | `[carried]` |
| `BM-002` §3.8 | Benefit claimable today: **BDT 0** | `[carried]` |
| `GV-004` §5.2 | The wave-to-month map and the build-effort profile | `[carried]`, used to derive the annual cost profile in §6.1 |
| BRD §19.5 | The cost of not proceeding: BDT 2.55–4.0 crore/yr | `[carried]`, and challenged in §8.6 |
| Bangladesh Bank / market USD-BDT | The rate verification in §4.1 | `[counted]` |

### 2.3 Findings this document closes, raises or advances

| Finding | Source | Disposition |
|---|---|---|
| `PGD-A2-10` **CRITICAL** — §3.2 and §3.4 disagree by 2.2×–3.3× | Estate audit | **CLOSED IN SPECIFICATION.** §3 resolves the reading on evidence, fixes the discrepancy at **2.2×**, restates the three-year benefit, and lists the six documents to correct. Closes on those corrections, not on this issue |
| `CVA-04` — the FX assumption is unverified | `CO-005` | **CLOSED.** §4 verifies the rate, adopts a **planning rate** rather than a spot rate, and states the sensitivity `CO-005` asked for |
| `H-02` — effort and TCO materially wrong | `00-06` | **Confirmed closed by `CO-005` §9.2.** This document does not reopen the cost side |
| `RP-02` / `BM-002` `BMR-F-01` | `AUDIT-015`, `BM-002` | Consumed: §7 recomputes claimable benefit on the corrected population of 71, superseding `CO-005` §10.1's split |
| **`BSC-F-01`** *(new, HIGH)* | This document | **`CO-005` publishes no annual cost profile**, so no discounted measure can be computed from the estate as published. §6.1 derives one and states the method |
| **`BSC-F-02`** *(new, CRITICAL)* | This document | **In the high-cost / conservative corner, steady-state annual run cost exceeds steady-state annual benefit**, so the programme never pays back on any horizon. No document in the estate states this. §8.3 |
| **`BSC-F-03`** *(new, HIGH)* | This document | The published Return tables' benefit column is **not derivable from §3.1 or §3.2 under either reading**, and the three scenarios are not a consistent transformation of one another. §3.4 |
| **`BSC-F-04`** *(new, MEDIUM)* | This document | BRD §19.5's *"BDT 2.55–4.0 crore per year"* of current-state waste **overlaps the §19.2 benefit lines by an unstated amount**, so it may not be added to the case. §8.6 |
| **`BSC-F-05`** *(new, MEDIUM)* | This document | **Two live Return tables** — `06-02` §3.4 and BRD §19.4 — carry the same wrong benefit column against different cost bases and produce ROI figures differing by 108 points on the base case. §9.1 |

---

## 3. Resolving `PGD-A2-10`

### 3.1 The defect

`06-02` §3.2 and BRD §19.3 carry an identical table whose column is headed **"Cumulative benefit
(base, BDT lac)"**:

| Period | Value | Note as published |
|---|---:|---|
| Year 1 (M1–M12) | 45 | Pilot productivity and early automation only |
| Year 2 (M13–M24) | 310 | v1.0 scope fully live |
| Year 3 (M25–M36) | 645 | New business lines ramping |
| Year 4 | **876** | **"Full run rate"** |
| Year 5 | 920 | Compounding on customer base growth |

`06-02` §3.4 and BRD §19.4 then state a three-year base-case benefit of **$1.96M**. `PGD-A2-10`
records that the two cannot both be right and sizes the gap at **2.2×–3.3×**.

### 3.2 The reading is decidable, and it is *annual*

Three tests, all of which point the same way.

| # | Test | Result |
|---|---|---|
| 1 | **Year 4 equals §3.1's steady-state total exactly.** §3.1 gives the base-case annual benefit at steady state as **876**. Year 4 in this table is **876**, annotated *"full run rate"* | A cumulative series reaching 876 at Year 4 would mean Year 4's *annual* benefit was 876 − 645 = **231**, which contradicts *"full run rate"* on its face |
| 2 | **The Year 4 → Year 5 step is +44.** A cumulative series at full run rate must rise by at least the run rate — **≥ 876** — in every subsequent year | +44 is 5% of 876. Under the cumulative reading, Year 5's annual benefit would be **44 lac**, i.e. the programme would collapse by 81% in its best year. Refuted |
| 3 | **The Year 5 note says *"compounding on customer base growth"*** | 920 ÷ 876 = **1.050** — a 5% growth on an annual run rate. Under the cumulative reading it is a 5% growth on a *cumulative total*, which is not a meaningful quantity |

**Verification**: 876 − 645 = **231** ✓ · 920 − 876 = **44** ✓ · 44 ÷ 876 = 0.050 → **5.0%** ✓ ·
920 ÷ 876 = **1.050** ✓.

> **`BM-003-D-01`. The column contains annual values. The header is wrong in both `06-02` §3.2 and
> BRD §19.3, and is corrected to "Annual benefit (base, BDT lac)".** The values are not changed.

### 3.3 The restated three-year benefit

| | Annual (BDT lac) | Cumulative (BDT lac) |
|---|---:|---:|
| Year 1 | 45 | 45 |
| Year 2 | 310 | 355 |
| Year 3 | 645 | **1,000** |
| Year 4 | 876 | 1,876 |
| Year 5 | 920 | **2,796** |

**Verification** `[derived]`: 45 + 310 = **355** ✓ · 355 + 645 = **1,000** ✓ ·
1,000 + 876 = **1,876** ✓ · 1,876 + 920 = **2,796** ✓.

> **The three-year base-case benefit is BDT 1,000 lac.** At `CO-005`'s verified rate of 122.70 that
> is **$815.0K** — the same figure `CO-005` §10.2 reaches, which is the cross-check that this
> resolution is consistent with the only other document to have attempted it.
>
> **Verification**: 1,000 × 100,000 ÷ 122.70 = **$814,996** → $815.0K ✓.

### 3.4 `BSC-F-03` — the published figure is derivable from neither reading

**Severity: HIGH · Status: OPEN · Owner: CFO**

The published three-year base benefit is **$1.96M**. Converting at the rate those tables use (110):

| Basis | Three-year benefit, BDT lac | Ratio to the published 2,156 |
|---|---:|---:|
| **Annual reading** (this document) | 1,000 | **2.16×** |
| **Cumulative reading** | 645 | **3.34×** |
| **Published in `06-02` §3.4 / BRD §19.4** | **2,156** | 1.00× |

**Verification**: $1.96M × 110 = 215,600,000 BDT = **2,156 lac** ✓ · 2,156 ÷ 1,000 = **2.156** ✓ ·
2,156 ÷ 645 = **3.343** ✓.

**This confirms and decodes `PGD-A2-10`'s range.** Its "2.2×–3.3×" is the *same* base-case
discrepancy measured under the two readings — 2.2× annual, 3.3× cumulative. **Resolving the reading
collapses the range to a single number: 2.2×.**

**The three scenarios are not consistent transformations of one another either.** If the Return
table were generated from one curve scaled by the §3.1 scenario totals, the ratios would match:

| Scenario | Published, BDT lac | Annual-reading 3-yr, BDT lac | Overstatement |
|---|---:|---:|---:|
| Conservative | 1,364 | 595 | **2.29×** |
| Base | 2,156 | 1,000 | **2.16×** |
| Optimistic | 2,871 | 1,453 | **1.98×** |

**Verification** `[derived]`: $1.24M × 110 = **1,364 lac** ✓ · $2.61M × 110 = **2,871 lac** ✓ ·
conservative scale 521 ÷ 876 = 0.59475 → 1,000 × 0.59475 = **595 lac** ✓ ·
optimistic scale 1,273 ÷ 876 = 1.45320 → 1,000 × 1.45320 = **1,453 lac** ✓ ·
1,364 ÷ 595 = **2.29** ✓ · 2,871 ÷ 1,453 = **1.98** ✓.

> **The overstatement factor is not constant across scenarios, so the Return table was not
> generated from the curve by any single rule.** Its benefit column has no reproducible derivation
> from any published table. It is therefore **superseded**, not adjusted: §6 computes the return
> from the curve directly.

### 3.5 The six documents that carry the defect

| Document | Where | Correction |
|---|---|---|
| `06-02` §3.2 | Column header | *"Cumulative"* → **"Annual"** |
| `06-02` §3.4 | Return table | **Superseded by `BM-003` §6.** Row retained with a pointer |
| BRD §19.3 | Column header | *"Cumulative"* → **"Annual"** |
| BRD §19.4 | Return table | **Superseded by `BM-003` §6** |
| `CO-005` §10.2 | Already reads the curve as annual, citing `PGD-A2-10` | **No correction needed** — `CO-005` reached the right reading and correctly declined to close the finding |
| `RL-005` `PIR-23` | Cites *"Year 1 cumulative benefit at 45 BDT lac"* | *"cumulative"* → **"annual"**. The rule's substance — that a large Year-1 benefit is a measurement error — is unaffected and correct |

> **`BSC-03`. `PGD-A2-10` closes when these corrections are made, not at this issue.** A finding
> closed by the document that diagnosed it, before the corrections land, is the pattern `BM-005`
> exists to break.

---

## 4. The Foreign Exchange Basis

### 4.1 The rate, verified

`CO-005` `CVA-04` recorded the estate's 110 BDT/USD as an unverified assumption and replaced it with
**122.70**, verified 2026-08-19.

| Observation | Value | Source and date | Label |
|---|---:|---|:--:|
| Market USD/BDT | **122.00** | Market quote, **18 August 2026** | `[counted]` |
| Market USD/BDT | 122.70 | Market quote, 17 August 2026 — the rate `CO-005` adopted | `[carried]` |
| Bangladesh Bank crawling-peg mid-rate | 117.00 | Bangladesh Bank crawling-peg regime | `[counted]` |
| 12-month high | 123.87 | Market series | `[counted]` |
| Estate assumption, unverified | 110.00 | `06-02` §3.1, BRD §19.2, `GV-008` §7.2 | `[carried]` |

**The rate moved 0.6% between `CO-005`'s verification and this one, one day apart.** That is the
argument against a spot rate, not an argument about which spot rate to use.

### 4.2 `BM-003-D-02` — a planning rate, not a spot rate

`CO-005` §10.2 asked whether the rate should be *"a spot rate, a forward curve, or a hedged rate
under `CO-003` `SOW-44`."* The answer follows from what the rate is used for.

| Option | Assessment |
|---|---|
| **Spot** | Rejected. A five-year case re-quoted on every day's close produces a different NPV every day and no comparability between issues. It also invites the appearance of selecting a favourable date |
| **Forward curve** | Rejected as the primary basis. A five-year BDT forward curve is thin and its quotes would themselves need verification at each issue, replacing one unverified assumption with five |
| **Hedged rate** | Rejected as the primary basis, retained as a **decision**. Hedging is available only for contracted USD outflows under `CO-003` `SOW-44`; it cannot hedge BDT benefits. §4.4 |
| **Planning rate with a sensitivity band** | **Adopted.** One rate, fixed at issue, restated only at a wave gate, with the case's sensitivity to it published every time |

> **`BSC-04`. The planning rate is 122.70 BDT/USD, fixed at this issue, restated only at a wave
> gate (`BSC-13`), and every published figure states it.** 122.70 is adopted rather than the
> 122.00 observed a day later **for one reason: `CO-005` §10 is already computed at 122.70, and a
> 0.6% refinement that forces the estate's two financial documents out of agreement costs more in
> reconciliation than it gains in accuracy.** The difference is disclosed here rather than absorbed.

### 4.3 The asymmetry nobody has stated

> **`BSC-05`. Benefits are earned in BDT; costs are incurred substantially in USD. Depreciation of
> the taka therefore damages the case on both sides simultaneously.**

| | Currency | Effect of taka depreciation |
|---|---|---|
| Benefit — all 14 lines are BDT operating improvements | **BDT** | USD value **falls** |
| Cost — vendor rates, infrastructure, third-party APIs, L6 subscriptions | **largely USD** | BDT cost **rises** |
| Cost — internal resource (`CO-005` Tier 2), local training delivery | BDT | Neutral |

**This is not a presentational point.** At 110 the base-case steady-state benefit is $797K; at
122.70 it is **$714K**; at 135 it is **$649K** — a **19% reduction** from the estate's published
assumption, against a cost base that does not fall with it.

**Verification** `[derived]`: 876 × 100,000 ÷ 110 = **$796,364** ✓ · ÷ 122.70 = **$713,936** ✓ ·
÷ 135 = **$648,889** ✓ · (796,364 − 648,889) ÷ 796,364 = 0.185 → **18.5%** ✓.

### 4.4 Sensitivity band

| Rate | Basis | Base-case steady-state benefit | Δ vs planning rate |
|---:|---|---:|---:|
| 110.00 | The estate's superseded assumption | $796.4K | +11.5% |
| 117.00 | Bangladesh Bank crawling-peg mid-rate | $748.7K | +4.9% |
| **122.70** | **Planning rate** (`BSC-04`) | **$713.9K** | — |
| 135.00 | ~10% depreciation over the analysis period | $648.9K | **−9.1%** |

**Verification** `[derived]`: 876 × 100,000 ÷ 117 = **$748,718** ✓ ·
748,718 ÷ 713,936 = 1.049 → **+4.9%** ✓ · 648,889 ÷ 713,936 = 0.909 → **−9.1%** ✓ ·
796,364 ÷ 713,936 = 1.115 → **+11.5%** ✓.

> **`BSC-06`. Where `CO-003` `SOW-44` permits hedging contracted USD outflows, the hedged
> proportion is disclosed in this model and the unhedged residue is what the sensitivity band
> applies to.** Hedging the cost side while the benefit side floats reduces the exposure; it does
> not remove it, and a case that presents a hedge as removing FX risk is misleading.

---

## 5. The Discount Rate

### 5.1 Why this section exists

**No document in the 784-file estate discounts a cash flow.** `06-02` §3.4, BRD §19.4, `GV-008` §7.2
and `CO-005` §10.2 all compare undiscounted sums. For a programme whose benefits arrive in Years 3–5
and whose costs are incurred in Years 1–2, that systematically flatters the case, because it values
a dollar in Year 5 identically to a dollar in Year 1.

> **`BSC-07`. Every return measure in this document is published in both undiscounted and
> discounted form.** The undiscounted form is what the estate has been using and is retained for
> comparability; the discounted form is the one that should drive the decision.

### 5.2 The Green Book rate does not transfer

The Green Book prescribes a **3.5% Social Time Preference Rate**. It is the correct rate for
appraising *public* investment in social value. **This is a private commercial investment by a
Bangladeshi company**, and applying 3.5% here would produce an NPV that is not comparable to any
alternative use of the Company's capital.

> **Recorded because the temptation is real: at 3.5% the base case's NPV is far less negative than
> at a commercial rate, and a reader could reach for the Green Book to obtain it.** §2.1 records
> this as a deliberate departure.

### 5.3 The derivation

A nominal **USD** rate is required, because §6 discounts USD cash flows.

| Component | Rate | Basis |
|---|---:|---|
| US 10-year risk-free | 4.0% | Long-horizon nominal USD base |
| Bangladesh sovereign risk premium | 5.0% | Country risk applicable to a Bangladesh-resident obligor |
| Project-specific risk premium | 5.0% | `CO-005` `TCO-06` records the estimate class as **5** (order-of-magnitude); `GV-004` `GV-004-A1` records the delivery factor as an unmeasured assumption; `GV-007` §7.3 records the TCO as bounded below, not bounded |
| **Recommended nominal USD hurdle rate** | **14.0%** | |

**Verification**: 4.0 + 5.0 + 5.0 = **14.0%** ✓.

> **`BSC-08`. The 14% is a recommendation, not a fact, and the Board sets the rate.** Its components
> are stated so the Board can change any one of them and see the effect. **The CFO's actual
> weighted average cost of capital supersedes this derivation the moment it is supplied** — raised
> as `Q-01`.

### 5.4 The rate matters far less than the estate would expect

| Discount rate | Base-case 5-year NPV *(Tier 1 expected cost)* |
|---:|---:|
| 10% | **−$999.6K** |
| **14%** | **−$994.2K** |
| 18% | **−$983.0K** |

*(Derivation in §6.3.)*

> **When a project does not pay back inside the horizon, the discount rate is nearly irrelevant.**
> Discounting shrinks the negative early flows and the positive late flows together, and here they
> roughly offset. **The sensitivity that matters is the horizon and the cost band, not the rate** —
> which is why §8, not §5, is where the decision is made. This is the opposite of what a reader
> expects, and it is why the rate should not become the argument.

---

## 6. The Restated Case

> **Cost basis consumed at a stated timestamp.** Every cost figure in this section is `CO-005` as at
> its **2026-08-19 10:05 (+06)** enumeration — Tier 1 three-year **$1,488K / $2,558K / $4,330K**,
> five-year **$1,912K / $3,249K / $5,367K**. `CO-005` restated its hypercare and escalation lines
> (`C` and `D`) after this category's first draft, and this section was recomputed against the
> restated figures. **This is `RG-08` operating as intended**: the basis is named with its
> timestamp, so a later reader can tell what was consumed.

### 6.1 `BSC-F-01` — the cost model has no annual profile, and discounting needs one

**Severity: HIGH · Status: OPEN · Owner: CFO with Enterprise Architecture**

`CO-005` §7.1 publishes a **three-year total** of $2,558K expected, and §7.2 publishes Years 4 and 5
individually. **It publishes no split of the three-year total across Years 1, 2 and 3.** Without
that split no NPV, IRR or discounted payback can be computed from the estate as published — which
is a sufficient explanation for why none ever has been.

This document derives the profile. **The derivation is stated in full so that `CO-005` can adopt,
amend or reject it**, per `BSC-02`, which forbids this document from changing a cost line.

**The people profile follows `GV-004` §5.2's build demand** `[derived]`:

| Year | Waves contributing | PW | Share |
|:--:|---|---:|---:|
| 1 | W1 (217) + W2 (167) + 4/5 of W3 (122.4) | **506.4** | **46.9%** |
| 2 | 1/5 of W3 (30.6) + W4 (224) + W5 (108) + 2/4 of W6 (49.5) | **412.1** | **38.2%** |
| 3 | 2/4 of W6 (49.5) + W7 (98) + W8 (13) + W9 (0) | **160.5** | **14.9%** |
| | | **1,079** | **100%** |

**Verification**: 217 + 167 + 122.4 = **506.4** ✓ · 30.6 + 224 + 108 + 49.5 = **412.1** ✓ ·
49.5 + 98 + 13 + 0 = **160.5** ✓ · 506.4 + 412.1 + 160.5 = **1,079** ✓, which equals `GV-004`
§5.2's demand total ✓ · 506.4 ÷ 1,079 = **46.93%** ✓.

**The full profile**, expected case, `$K` `[derived]`:

| Line | 3-yr | **Y1** | **Y2** | **Y3** | Allocation driver |
|:--:|---:|---:|---:|---:|---|
| **A** People — delivery | 1,358 | 637 | 519 | 202 | Build-effort profile above |
| **B** PMO, assurance | 136 | 45 | 45 | 46 | Even — the PMO runs throughout |
| **C** Hypercare — pools 1 + 2, 538 PW | 177 | 39 | 59 | 79 | Waves completing per year: **2 / 3 / 4** of 9 |
| **D** Rate escalation | 117 | 0 | 77 | 40 | Year 1 is the base year; balance apportioned over A+B+C |
| **E** Infrastructure, 12 environments | 195 | 55 | 70 | 70 | Ramp then steady |
| **F** `BD-R` Bangladesh-resident store | 114 | 30 | 42 | 42 | Required from first go-live |
| **G** Third-party APIs | 85 | 15 | 30 | 40 | Transaction-volume driven, rising |
| **H** L6 commercial components | 45 | 12 | 16 | 17 | Subscriptions from early waves |
| **I** Support and maintenance | 120 | 0 | 55 | 65 | **`CO-005` §7.1 states Years 2–3** |
| **J** Change and training delivery | 52 | 12 | 17 | 23 | Follows go-lives, 2 / 3 / 4 of 9 |
| **K** VAT non-recoverable residue | 20 | 9 | 7 | 4 | Proportional to taxable spend |
| **L** Withholding-tax gross-up | 83 | 39 | 32 | 12 | Proportional to vendor payments (line A) |
| **M** Vendor and contract administration | 56 | 19 | 19 | 18 | Even |
| **Total** | **2,558** | **912** | **988** | **658** | |

**Verification** *(rows)*: 637+519+202 = **1,358** ✓ · 45+45+46 = **136** ✓ · 39+59+79 = **177** ✓ ·
0+77+40 = **117** ✓ · 55+70+70 = **195** ✓ · 30+42+42 = **114** ✓ · 15+30+40 = **85** ✓ ·
12+16+17 = **45** ✓ · 0+55+65 = **120** ✓ · 12+17+23 = **52** ✓ · 9+7+4 = **20** ✓ ·
39+32+12 = **83** ✓ · 19+19+18 = **56** ✓.
**Verification** *(columns)*: Y1 = **912** · Y2 = **988** · Y3 = **658** ·
912 + 988 + 658 = **2,558** ✓, reconciling exactly to `CO-005` §7.1.

Years 4 and 5 are `CO-005` §7.2 unchanged: **337** and **354** `[carried]`.
Five-year total 912 + 988 + 658 + 337 + 354 = **3,249** ✓, reconciling to `CO-005` §7.3.

> **`BSC-09`. This profile is a derivation of `CO-005`'s total, not a new estimate.** It changes no
> line and no total. If `CO-005` publishes its own annual profile, this section is replaced by it.

### 6.2 The benefit profile

`06-02` §3.2 as re-labelled by §3.2, converted at the planning rate `[carried from CO-005 §10.2]`:

| Year | BDT lac | **USD $K @ 122.70** | Cumulative $K |
|:--:|---:|---:|---:|
| 1 | 45 | **36.7** | 36.7 |
| 2 | 310 | **252.6** | 289.3 |
| 3 | 645 | **525.7** | **815.0** |
| 4 | 876 | **714.0** | 1,529.0 |
| 5 | 920 | **749.8** | **2,278.8** |

**Verification**: 45 × 100,000 ÷ 122.70 = **$36,675** ✓ · 310 → **$252,649** ✓ ·
645 → **$525,672** ✓ · 876 → **$713,936** ✓ · 920 → **$749,796** ✓.
These reproduce `CO-005` §10.2 exactly.

### 6.3 The base case — expected cost, base benefit

| Year | Benefit $K | Cost $K | **Net $K** | Cumulative net $K | DF @14% | **PV $K** |
|:--:|---:|---:|---:|---:|---:|---:|
| 1 | 36.7 | 912 | **−875.3** | −875.3 | 0.877193 | −767.8 |
| 2 | 252.6 | 988 | **−735.4** | −1,610.7 | 0.769468 | −565.9 |
| 3 | 525.7 | 658 | **−132.3** | −1,743.0 | 0.674972 | −89.3 |
| 4 | 714.0 | 337 | **+377.0** | −1,366.0 | 0.592080 | +223.2 |
| 5 | 749.8 | 354 | **+395.8** | **−970.2** | 0.519369 | +205.6 |
| | **2,278.8** | **3,249** | **−970.2** | | | **−994.2** |

**Verification**: 2,278.8 − 3,249 = **−970.2** ✓, reconciling to `CO-005` §7.3's five-year Tier 1
expected cost and §10.2's cumulative benefit · PV column −767.8 − 565.9 − 89.3 + 223.2 + 205.6 =
**−994.2** ✓.

| Measure | Base case |
|---|---:|
| **5-year NPV @ 14%** | **−$994.2K** |
| 5-year NPV @ 10% | −$999.6K |
| 5-year NPV @ 18% | −$983.0K |
| **IRR, 5-year horizon** | **Undefined — cumulative net is negative in every year** |
| 3-year ROI, undiscounted | **−68%** |
| 5-year ROI, undiscounted | **−30%** |
| **Simple payback** | **≈ month 92 (Year 8)** |
| **Discounted payback @14%** | **Year 13** if benefit grows with cost escalation; **never** if benefit is flat (§8.7) |

**Verification**: (815.0 − 2,558) ÷ 2,558 = −0.681 → **−68%** ✓ ·
(2,278.8 − 3,249) ÷ 3,249 = −0.299 → **−30%** ✓.

**Payback derivation** `[derived]`: beyond Year 5, benefit is held at the Year-5 level of $749.8K
and cost escalates at `CO-005` §7.2's 5% — Y6 $372K, Y7 $390K, Y8 $410K. Net: Y6 +377.8 → cumulative
−592.4; Y7 +359.8 → −232.6; Y8 +339.8 → **+107.2**, crossing during Year 8.
232.6 ÷ 339.8 = 0.685 of a year → month 84 + 8.2 = **month 92** ✓.

### 6.4 The two corners

**Low cost / optimistic benefit** — `CO-005` Tier 1 low (5-yr $1,912K); `06-02` optimistic
(1,273 lac steady state, scale 1.45320):

| Year | Benefit $K | Cost $K | Net $K | Cumulative $K | PV @14% |
|:--:|---:|---:|---:|---:|---:|
| 1 | 53.3 | 530 | −476.7 | −476.7 | −418.2 |
| 2 | 367.2 | 575 | −207.8 | −684.5 | −159.9 |
| 3 | 763.9 | 383 | +380.9 | −303.6 | +257.1 |
| 4 | 1,037.5 | 207 | +830.5 | **+526.9** | +491.7 |
| 5 | 1,089.6 | 217 | +872.6 | **+1,399.5** | +453.2 |
| | **3,311.5** | **1,912** | **+1,399.5** | | **+624.0** |

**Verification**: optimistic scale 1,273 ÷ 876 = **1.45320** ✓ · Y1 45 × 1.45320 = 65.4 lac →
$53,301 ✓ · Y3 645 × 1.45320 = 937.3 lac → $763,896 ✓ · Y5 920 × 1.45320 = 1,336.9 lac →
$1,089,568 ✓ · cost split at the expected case's 35.65 / 38.62 / 25.72% of $1,488K =
530 / 575 / 383, summing to **1,488** ✓ · 1,488 + 207 + 217 = **1,912** ✓ ·
3,311.5 − 1,912 = **+1,399.5** ✓.

| Measure | Low cost / optimistic |
|---|---:|
| **5-year NPV @ 14%** | **+$624.0K** |
| **IRR** | **≈ 48%** |
| 5-year ROI, undiscounted | **+73%** |
| **Simple payback** | **≈ month 40 (Year 4)** |

**Verification**: (3,311.5 − 1,912) ÷ 1,912 = 0.732 → **+73%** ✓ · payback 303.6 ÷ 830.5 = 0.366
of Year 4 → month 36 + 4.4 = **month 40** ✓ · IRR bracketed: NPV at 45% = **+$21.3K**, at 48% =
**−$3.5K**, interpolating to **≈ 48%** ✓.

**High cost / conservative benefit** — `CO-005` Tier 1 high (5-yr $5,367K); `06-02` conservative
(521 lac steady state, scale 0.59475):

| Year | Benefit $K | Cost $K | Net $K | Cumulative $K |
|:--:|---:|---:|---:|---:|
| 1 | 21.8 | 1,544 | −1,522.2 | −1,522.2 |
| 2 | 150.3 | 1,672 | −1,521.7 | −3,043.9 |
| 3 | 312.6 | 1,114 | −801.4 | −3,845.3 |
| 4 | 424.6 | 506 | **−81.4** | −3,926.7 |
| 5 | 446.0 | 531 | **−85.0** | **−4,011.7** |
| | **1,355.3** | **5,367** | **−4,011.7** | |

**Verification**: conservative scale 521 ÷ 876 = **0.59475** ✓ · Y5 920 × 0.59475 = 547.2 lac →
$445,966 ✓ · cost split of $4,330K at 35.65 / 38.62 / 25.72% = 1,544 / 1,672 / 1,114, summing to
**4,330** ✓ · 4,330 + 506 + 531 = **5,367** ✓ · 1,355.3 − 5,367 = **−4,011.7** ✓.

| Measure | High cost / conservative |
|---|---:|
| **5-year NPV @ 14%** | **−$3,139.4K** |
| **IRR** | **Undefined — no positive net in any year** |
| 5-year ROI, undiscounted | **−75%** |
| **Simple payback** | **Never, on any horizon** (§8.3) |

**Verification**: (1,355.3 − 5,367) ÷ 5,367 = −0.748 → **−75%** ✓.

### 6.5 The three corners in one table

| | Low cost / optimistic | **Expected / base** | High cost / conservative |
|---|---:|---:|---:|
| 5-yr benefit | $3,311.5K | **$2,278.8K** | $1,355.3K |
| 5-yr cost (Tier 1) | $1,912K | **$3,249K** | $5,367K |
| 5-yr net | **+$1,399.5K** | **−$970.2K** | **−$4,011.7K** |
| **5-yr NPV @14%** | **+$624.0K** | **−$994.2K** | **−$3,139.4K** |
| **IRR** | **≈48%** | undefined | undefined |
| **Simple payback** | **month 40** | **month 92** | **never** |
| 5-yr ROI | +73% | −30% | −75% |

**Verification**: band = 624.0 − (−3,139.4) = **$3,763.4K** ✓.

> **The spread is $3.76M of NPV across the band, and the band is `CO-005`'s own — its estimate
> class is 5, order-of-magnitude.** No decision should rest on the point estimate. **The decision
> that should be taken is the one that narrows the band**, which is why `CO-005` §11 option B —
> fund to the Wave 4 gate and re-decide — is the recommendation this document endorses in §8.5.

> **Tier 2.** On `CO-005`'s full economic basis (Tier 1 + internal resource), the five-year cost is
> $2,311K / $3,977K / $6,568K. The expected additional draw is **$681K in Years 1–3** (`CO-005`
> §6.6) and **$47K in Years 4–5**. Discounted at the §6.1 profile weights, that is
> **−$559.5K of NPV**, giving a **Tier 2 expected NPV of ≈ −$1,553.7K**.
>
> **Verification**: 3,239 − 2,558 = **$681K** ✓ · 3,977 − 3,249 − 681 = **$47K** ✓ ·
> weighted three-year discount factor = 0.877193×0.3565 + 0.769468×0.3862 + 0.674972×0.2572 =
> **0.78358** ✓ · 681 × 0.78358 = **533.6** · 47 apportioned 21/26 across Years 4–5 →
> 21 × 0.592080 + 26 × 0.519369 = **25.9** · 533.6 + 25.9 = **559.5** ✓ ·
> −994.2 − 559.5 = **−1,553.7** ✓.
>
> Tier 2 is the correct basis for asking *"is this the best use of the Company's capacity"*; Tier 1
> is the correct basis for *"can the Company fund this"*. `BSC-10` requires both to be quoted with
> their tier named, mirroring `CO-005` `TCO-10`.

## 7. Claimed versus Claimable

### 7.1 The rule that makes this section necessary

`06-02` §6: *"A KPI without a baseline cannot claim a benefit."* `RL-005` `PIR-27` makes it a
precondition. `BM-002` §3.8 states the current position: **benefit claimable today is BDT 0** —
not reduced, not provisional, zero, because no baseline in the register has been signed.

**A business case may be built on claimed benefit. A benefit *report* may only use claimable
benefit.** `BSC-11` keeps them separate.

### 7.2 The three states

| State | Steady-state benefit, BDT lac | At 122.70 | Condition |
|---|---:|---:|---|
| **Claimed** — `06-02` §3.1 base case | **876** | **$713.9K/yr** | The case as published |
| **Claimable today** | **0** | **$0** | No signed baseline exists (`BM-002` §3.8) |
| **Claimable if `BM-002`'s measurement programme is *not* funded** | **334** | **$272.2K/yr** | Only the class-`C`/`D` new-business absolutes, which need no baseline |
| **Claimable if it *is* funded** | **876** | **$713.9K/yr** | Improvement lines recover their comparators |

**Verification**: 334 × 100,000 ÷ 122.70 = **$272,208** ✓ · 876 − 334 = **542**, `BM-002` §3.7's
improvement exposure ✓.

> **Note the reconciliation to BRD §19.2.** BRD splits the case as *existing revenue streams* 502
> and *new revenue streams* 374. `BM-002`'s split is *improvement* 542 and *absolutes* 334. The
> difference is **dynamic pricing margin uplift, BDT 40 lac**, which BRD counts as a new revenue
> stream but which `RP-015` §4.8 classifies as an improvement benefit *"indexed to itself"*.
> **Verification**: 374 − 40 = **334** ✓ · 502 + 40 = **542** ✓. Both splits are correct for their
> own purpose; they are not interchangeable, and `BSC-12` requires the purpose to be stated.

### 7.3 The finding that should decide the `BM-002` funding question

Set the **unfunded-measurement** claimable benefit against `CO-005` §7.2's steady-state run cost:

| | Steady state, per year |
|---|---:|
| Claimable benefit if measurement is not funded | **$272.2K** |
| `CO-005` §7.2 Year-5 run cost, expected | **$354K** |
| **Net** | **−$81.8K per year, in perpetuity** |

**Verification**: 272.2 − 354 = **−81.8** ✓.

> **If the baselines are never measured, the benefit the Company is permitted to claim at full run
> rate is less than the cost of running the platform.** That is not a marginal case; it is a
> perpetual loss recorded as a success, because the improvement benefits will be *delivered* and
> simply not *claimable*.
>
> **`BM-002` §5.4 prices the fix at 31.6 person-weeks of business time.** Against $441.7K a year of
> otherwise unclaimable benefit, that is the highest-return decision available to this programme,
> and it is available for a limited window. This document endorses `BM-002` §6.6 decision 1 without
> qualification.

---

## 8. Sensitivity

### 8.1 One-at-a-time sensitivity, base case, 5-year NPV @14%

Each row changes **one** variable from the §6.3 base case and recomputes the full five-year model.

| Variable | Change | New NPV | NPV effect |
|---|---|---:|---:|
| **Cost** | to `CO-005` low (5-yr $1,912K) | **−$7.6K** | **+$986.6K** |
| **Cost** | to `CO-005` high (5-yr $5,367K) | −$2,574.7K | **−$1,580.5K** |
| **Benefit** | to optimistic (1,273 lac) | −$362.8K | +$631.4K |
| **Benefit** | to conservative (521 lac) | −$1,558.9K | −$564.7K |
| **Benefit slips one year** | curve shifts right by 12 months | −$1,506.9K | **−$512.7K** |
| **FX** | 110 (the superseded assumption) | −$833.3K | +$160.9K |
| **FX** | 135 | −$1,121.0K | −$126.8K |
| **Discount rate** | 10% | −$999.6K | −$5.4K |
| **Discount rate** | 18% | −$983.0K | +$11.2K |

**Verification of the band widths** `[derived]`: cost 986.6 + 1,580.5 = **$2,567.1K** ·
benefit 631.4 + 564.7 = **$1,196.1K** · slippage **$512.7K** · FX 160.9 + 126.8 = **$287.7K** ·
discount rate 5.4 + 11.2 = **$16.6K**.

**Ranked by band width**: cost **$2,567K** ≫ benefit **$1,196K** > slippage **$513K** >
FX **$288K** ≫ discount rate **$17K**.

> **The cost band dominates everything, and the discount rate is noise.** This is the single most
> useful output of the sensitivity analysis, and it points the decision at `CO-005`'s estimate
> class — which is 5 — rather than at any financial assumption. **Narrowing the estimate class is
> worth more than any other action available**, and `CO-005` `TCO-11` already provides the
> mechanism: re-baseline at every wave gate.
>
> **Note the first row.** At `CO-005`'s **low** cost the base-case NPV is **−$7.6K** — within
> rounding of break-even. **The difference between a programme that destroys $994K of value and one
> that breaks even is entirely inside the cost estimate's own uncertainty band**, which is the
> clearest possible statement of why the estimate class, not the benefit case, is the thing to
> work on.

### 8.2 Slippage is the second lever, and it is asymmetric

A twelve-month slip in the benefit curve costs **$513K of NPV** without changing a single benefit
or cost figure, because it moves every positive flow one year further from the present and extends
the negative ones.

> **`BSC-14`. Schedule slippage is reported in this model in NPV, not only in months.** `GV-004`
> §5.2 rates W1 **infeasible at 5.33×** capacity, W2 at 1.76× and W4 at 1.32×. **A schedule the
> programme's own plan rates infeasible is a financial exposure of roughly $513K per year of slip**,
> and it is currently reported only as a capacity problem.

### 8.3 `BSC-F-02` — in the high-cost corner the platform costs more to run than it earns

**Severity: CRITICAL · Status: OPEN · Owner: CFO with the Board**

| Corner | Year-5 benefit | Year-5 cost | Steady-state net |
|---|---:|---:|---:|
| Low cost / optimistic | $1,089.6K | $217K | **+$872.6K** |
| Expected / base | $749.8K | $354K | **+$395.8K** |
| Expected cost / conservative benefit | $446.0K | $354K | +$92.0K |
| **High cost / conservative benefit** | **$446.0K** | **$531K** | **−$85.0K** |

**Verification**: 446.0 − 531 = **−85.0** ✓ · 446.0 − 354 = **+92.0** ✓.

**In the high-cost / conservative corner, the annual net is negative at full run rate.** A programme
whose steady state is negative does not have a long payback — **it has no payback at any horizon**,
because every additional year makes the position worse rather than better.

**Why no document contains this.** Every published return figure in the estate is a three-year
cumulative comparison. **A three-year cumulative view cannot detect a negative steady state**,
because the large negative early years dominate and the run-rate relationship is never isolated.
`CO-005` §7.2 computed the run cost for the first time; this document is the first to set a benefit
run rate beside it.

**Remediation.** This corner is not a forecast; it is a corner. But it is a **stop condition**, and
it must be one:

> **`BSC-15`. The steady-state run-rate test is computed and published at every wave gate.** If
> projected steady-state annual benefit falls below projected steady-state annual run cost, the
> programme is escalated to the Board as a **stop-or-restructure decision**, regardless of how much
> has been spent. Sunk cost is not a reason to continue into a negative steady state.

### 8.4 Optimism bias, per the Green Book

The Green Book requires an explicit optimism-bias adjustment rather than an implicit one. This
model carries it on **both** sides, and it is named here so it is not applied twice:

| Side | Mechanism | Implied adjustment |
|---|---|---:|
| **Cost** | `CO-005`'s high case, $4,330K against $2,558K expected (3-year) | **+69%** |
| **Benefit** | `06-02`'s conservative case, 521 lac against 876 | **−41%** |

**Verification**: 4,330 ÷ 2,558 = 1.693 → **+69%** ✓ · 521 ÷ 876 = 0.595 → **−41%** ✓.

> **`BSC-16`. No further optimism-bias uplift is applied on top of the scenario structure.** The
> +74% cost uplift is consistent with Green Book guidance for software and IT projects at an
> early estimate maturity, which is what AACE class 5 means. **Applying a further uplift to an
> already-conservative corner would produce a case nobody believes and therefore nobody uses.**

### 8.5 The decision

| # | Question | This document's position |
|---|---|---|
| 1 | **Is the programme worth doing?** | **On the expected case as it stands, no — NPV is −$994K.** But the expected case rests on an order-of-magnitude cost estimate, and the low corner returns ≈48% IRR. **The correct answer is not yes or no; it is that the question cannot be answered at estimate class 5** |
| 2 | **What should the Board authorise?** | **`CO-005` §11 option B — fund Tranche 0 and Tranche 1, re-decide at the Wave 4 gate.** Endorsed. §6.5 strengthens `CO-005`'s own reasoning: the wider the band, the more a real option to stop is worth, and this document measures the band at **$3.76M of NPV** |
| 3 | **What single act most improves the case?** | **Fund `BM-002`'s 31.6 PW of measurement** (§7.3). It is the only action that moves claimable benefit from $272.2K/yr to $713.9K/yr, and its window closes at W1 go-live |
| 4 | **What single act most reduces risk?** | **Narrow the estimate class.** §8.1 — the cost band is $2,567K of NPV, more than twice the benefit band. `CO-005` `TCO-11`'s gate re-baseline is the instrument |
| 5 | **Is `D-014` decidable now?** | **No, and it should not be forced.** `D-014` asks whether to fund the restated position. §8.1 says the information needed to decide it arrives at the Wave 4 gate, not before |

### 8.6 `BSC-F-04` — the cost of not proceeding may not simply be added

**Severity: MEDIUM · Status: OPEN · Owner: CFO**

BRD §19.5 states that deferral continues *"current-state waste … **BDT 2.55–4.0 crore per year**"*
— that is **255–400 BDT lac a year**, comparable to half the entire benefit case.

**It cannot be added to the case, because it substantially *is* the case.** The `06-02` §3.1 lines
that are waste reduction:

| Line | BDT lac |
|---|---:|
| Warranty revenue recovery | 100 |
| Technician productivity | 130 |
| Inventory cost reduction | 34 |
| Administrative labour savings | 62 |
| Financial close & cash flow | 26 |
| **Total waste-reduction benefit already in the case** | **352** |

**Verification**: 100 + 130 + 34 + 62 + 26 = **352** ✓, which sits squarely inside §19.5's
255–400 lac range.

> **`BSC-17`. The cost of not proceeding is presented as a *counterfactual narrative*, never as an
> addition to quantified benefit**, unless and until the overlap is quantified and the
> non-overlapping residue identified. A case that adds both would double-count roughly BDT 352 lac
> a year — **40% of the entire benefit claim.** Raised as `Q-04`.

### 8.7 `BSC-F-06` — the post-Year-5 benefit assumption is unstated and worth "Year 13" versus "never"

**Severity: MEDIUM · Status: OPEN · Owner: CFO**

`06-02` §3.2 stops at Year 5. `CO-005` §7.2 escalates cost at 5% a year indefinitely. **Nothing
states whether benefit grows, holds or decays after Year 5**, and the two plausible assumptions
give opposite answers:

| Assumption | Annual net, Year 6+ | **Discounted payback @14%** |
|---|---|---|
| Benefit **grows at 5%**, matching cost escalation | roughly constant at +$378K | **Year 13** |
| Benefit **flat** at the Year-5 level, cost escalating at 5% | declines by ~$18K each year; turns **negative around Year 20** | **Never** |

**Verification** `[derived]`, growth case: cumulative NPV **−994.2** at Y5; Y6 +377.8 × 0.455587 =
+172.1 → −822.1; Y7 +396.7 × 0.399637 = +158.5 → −663.6; Y8 +416.5 × 0.350559 = +146.0 → −517.6;
Y9 +437.3 × 0.307508 = +134.5 → −383.1; Y10 +459.2 × 0.269744 = +123.9 → −259.2;
Y11 +482.2 × 0.236617 = +114.1 → −145.1; Y12 +506.3 × 0.207559 = +105.1 → −40.0;
Y13 +531.6 × 0.182069 = +96.8 → **+56.8** ✓.

> **`BSC-18`. The model states its post-horizon assumption explicitly and the Board approves it.**
> This document adopts the **growth case** as its base — Year 5's own note, *"compounding on
> customer base growth"*, supports it — and publishes the flat case beside it. An unstated
> post-horizon assumption is how a five-year model becomes a perpetuity nobody agreed to.

---

## 9. Reconciliation

### 9.1 `BSC-F-05` — every return figure in the estate, in one table

**Severity: MEDIUM · Status: OPEN · Owner: CFO**

| Source | Basis | 3-yr benefit | 3-yr cost | ROI | Payback | Status |
|---|---|---:|---:|---:|---|---|
| `06-02` §3.4 conservative | 110 FX; superseded costs | $1.24M | $780K | 59% | 24 mo | **Superseded** |
| `06-02` §3.4 **base** | 110 FX; superseded costs | **$1.96M** | **$610K** | **221%** | **17 mo** | **Superseded** |
| `06-02` §3.4 optimistic | 110 FX; superseded costs | $2.61M | $455K | 475% | 12 mo | **Superseded** |
| BRD §19.4 conservative | 110 FX; restated costs | $1.24M | $1.15M | 8% | 32 mo | **Superseded** |
| BRD §19.4 **base** | 110 FX; restated costs | **$1.96M** | **$0.92M** | **113%** | **22 mo** | **Superseded** |
| BRD §19.4 optimistic | 110 FX; restated costs | $2.61M | $0.69M | 278% | 15 mo | **Superseded** |
| `GV-008` §7.2 | 110 FX; budget basis | — | $1,630K | — | ~month 47 | Superseded by `CO-005` §10.2 |
| `CO-005` §10.2 | **122.70**; Tier 1 | $815.0K | $2,558K | — | Year 6 | **Current for cost; partial for return** |
| **`BM-003` §6.3 base** | **122.70; `CO-005` Tier 1; annual reading** | **$815.0K** | **$2,558K** | **−68%** | **month 92** | **CURRENT** |

**Two live Return tables carry the same wrong benefit column against different cost bases**, and
produce base-case ROI figures of **221%** and **113%** — a **108-point** difference on the same
programme. **Verification**: 221 − 113 = **108** ✓.

> **`BSC-19`. One return position is current at any time, and it is this document's.** Superseded
> tables are marked superseded **in place**, with a pointer, and never deleted — deletion destroys
> the audit trail that shows how the figure moved. This is `CO-005` `TCO-10` applied to return
> rather than cost.

### 9.2 What moved, and why

| Step | Base-case effect | Attributable to |
|---|---:|---|
| Published position, `06-02` §3.4 | **221% ROI, 17-month payback** | — |
| Restate cost to `CO-005` Tier 1 3-year ($2,558K) | → 221% becomes ~−23% at the published benefit | `H-02`, `CO-005` §7.1 — **arithmetic, not deterioration** |
| Correct FX 110 → 122.70 | −10.4% on all BDT benefit | `CVA-04`, §4 |
| **Resolve `PGD-A2-10`: 3-yr benefit $1.96M → $815.0K** | **−23% becomes −68%** | **§3 — the largest single correction** |
| Discount at 14% | 5-year NPV **−$994.2K** | §5, §6.3 — never previously computed |

> **The programme did not get worse. The arithmetic got right.** `CO-005` §10.3 makes this point
> about cost and it holds equally here: nothing changed between the BRD's issue and this document
> except that figures which were always wrong were computed correctly.

---

## 10. The Five Case Model

Mapped so the case is assessable against a recognised framework rather than only against itself.

| Case | Question | Where it is answered | Assessment |
|---|---|---|---|
| **Strategic** | Is there a compelling case for change? | BRD §1–§6; `GV-001`; `06-02` §1's 18 objectives | **Strong and unchallenged.** `CO-005` §10.3: *"the benefit case is not disputed by any audit"* |
| **Economic** | Does it optimise value for money? | **§6, §8 — this document** | **Weak at the expected point estimate, undecidable at estimate class 5.** The band is $3.76M of NPV |
| **Commercial** | Is it attractive to the market and procurable? | `CO-001` RFP; `CO-002`; `CO-003`; `CO-005` §9.4 | **Qualified.** `CVA-02` — the live RFP carries a superseded envelope |
| **Financial** | Is it affordable? | `GV-008`; `CO-005` §7; §6.1's profile | **Qualified.** Peak funding need is **Year 2 at $988K** on the expected profile — the number the Financial Case actually turns on, and §6.1 is the first place it appears |
| **Management** | Is it deliverable? | `GV-004`; `GV-009`; `GV-007` | **Weak.** `GV-004` §5.2 rates W1 **infeasible at 5.33×** capacity |

> **Two of the five cases are weak and one of those is the Economic Case this document owns.** The
> Green Book's discipline is that a business case is not approvable on the Strategic Case alone,
> however compelling. **The route to approval is not a better argument; it is a narrower cost band
> and a measured baseline**, which is precisely what §8.5's options 3 and 4 buy.

---

## 11. Governing Rules — Consolidated

| # | Rule |
|---|---|
| **`BSC-01`** | Every figure is labelled **`[carried]`**, **`[counted]`** or **`[derived]`** |
| **`BSC-02`** | **Cost lines are consumed from `CO-005` unchanged.** A disagreement is raised to `CO-005`, never resolved here |
| **`BSC-03`** | A finding is **closed by the correction landing**, not by the document that diagnosed it |
| **`BSC-04`** | The **planning rate is 122.70 BDT/USD**, fixed at issue, restated only at a wave gate, and stated beside every figure |
| **`BSC-05`** | The **BDT-benefit / USD-cost asymmetry** is disclosed wherever the case is presented |
| **`BSC-06`** | Where USD outflows are hedged, the **hedged proportion is disclosed** and sensitivity applies to the residue |
| **`BSC-07`** | Every return measure is published in **both undiscounted and discounted form** |
| **`BSC-08`** | The discount rate is a **Board decision**; 14% is a recommendation with its components shown |
| **`BSC-09`** | §6.1's annual cost profile is a **derivation of `CO-005`'s total**, replaced the moment `CO-005` publishes its own |
| **`BSC-10`** | Every quoted figure states its **tier and its horizon** (`CO-005` `TCO-10` applied to return) |
| **`BSC-11`** | **Claimed and claimable benefit are never presented as one number.** A benefit report uses claimable only |
| **`BSC-12`** | Where a benefit split is used, its **purpose is stated** — improvement/absolute and existing/new are not interchangeable |
| **`BSC-13`** | The case is **re-computed at every wave gate** (`GV-009`), stating which estimate classes migrated and how the band narrowed |
| **`BSC-14`** | **Schedule slippage is reported in NPV**, not only in months — roughly **$513K per year of slip** |
| **`BSC-15`** | The **steady-state run-rate test** is computed at every gate. A negative steady state is escalated as a stop-or-restructure decision regardless of sunk cost |
| **`BSC-16`** | **No optimism-bias uplift is applied on top of the scenario structure**, which already carries +74% on cost and −41% on benefit |
| **`BSC-17`** | The **cost of not proceeding is a counterfactual narrative, never an addition** to quantified benefit, until the overlap is quantified |
| **`BSC-18`** | The **post-horizon benefit assumption is stated explicitly** and approved by the Board |
| **`BSC-19`** | **One return position is current at any time.** Superseded tables are marked in place with a pointer, never deleted |
| **`BSC-20`** | **This document forecasts; `BM-004` tracks.** A wave review does not re-forecast (`RL-005` `PIR-25`), and this model is not adjusted to match an actual |

---

## 12. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `BM-003-D-01` | The `06-02` §3.2 column reading | Cumulative · annual | **Annual** | Three independent tests, §3.2. Year 4 = 876 = §3.1's run rate; +44 step; "compounding" note | `PGD-A2-10` fixed at 2.2×; six documents corrected (§3.5) |
| `BM-003-D-02` | FX basis | Spot · forward curve · hedged · planning rate | **Planning rate 122.70** | A five-year case re-quoted daily has no comparability. §4.2 | `CO-005` §10 and this document agree; the 0.6% difference to 18 Aug spot is disclosed, not absorbed |
| `BM-003-D-03` | Discount rate | Green Book 3.5% · commercial WACC · 14% build-up | **14%, recommended to the Board** | 3.5% is a public-sector social rate and would flatter the case materially (§5.2) | §5.4 shows the rate is nearly immaterial here; the Board still owns it |
| `BM-003-D-04` | The published Return tables | Adjust · supersede | **Supersede** | Their benefit column is not derivable from any published table under any reading (§3.4) | §9.1 marks both in place with a pointer |
| `BM-003-D-05` | Annual cost profile | Wait for `CO-005` · derive here | **Derive, with the method stated** | Without it no discounted measure exists at all; §6.1 reconciles exactly to `CO-005`'s totals | `BSC-09` — replaced when `CO-005` publishes its own |
| `BM-003-D-06` | Post-Year-5 benefit | Flat · grows with cost | **Grows at 5%**, flat published beside it | Year 5's own note, *"compounding on customer base growth"* | Discounted payback Year 13 rather than never (§8.7) |
| `BM-003-D-07` | Whether to publish the negative base-case NPV | Present the low corner · present all three | **All three, negative first** | `06-02` §6: *"missed benefits are reported as missed"*. A case presented only at its favourable corner is not a case | §8.5's decision becomes a real option rather than an approval |

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **What is the Company's actual weighted average cost of capital?** §5.3's 14% is a build-up, not a measurement | CFO | W1 | §6's NPV; supersedes `BSC-08` |
| `Q-02` | **Will the Steering Committee fund `BM-002`'s 31.6 PW before W1 go-live?** | Programme Director | **Month 1** | §7.3 — the difference between $272.2K/yr and $713.9K/yr of claimable benefit |
| `Q-03` | **Does `CO-005` adopt §6.1's annual profile, or publish its own?** | CFO with Enterprise Architecture | W1 | `BSC-09`; every discounted figure |
| `Q-04` | **What part of BRD §19.5's BDT 255–400 lac of current-state waste is *not* already inside the §3.1 benefit lines?** | CFO | W2 | `BSC-17`; whether the Strategic Case carries an unquantified addition |
| `Q-05` | **Is the FX exposure hedged under `CO-003` `SOW-44`, and for what proportion?** | CFO with Commercial | Before contract signature | `BSC-06`; §4.4's band |
| `Q-06` | **Which corner does the Board underwrite for the purposes of `D-014`?** | Board | Wave 4 gate | §8.5 |
| `Q-07` | **Does `GV-004` §5.2's infeasible W1 mean the benefit curve should already be shifted right?** If so, §8.2's −$513K is not a sensitivity but a correction | Programme Director | W1 | §6.2's curve |

> `Q-02` and `Q-07` are escalated to `GV-005` at issue. `Q-07` is the more uncomfortable: **this
> document has costed slippage that `GV-004` has already, in effect, declared.**

---

## 14. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | `PGD-A2-10` is resolved on stated evidence, not asserted | §3.2's three tests, with verification |
| `AC-02` | Every figure is labelled `[carried]`, `[counted]` or `[derived]` | `BSC-01`; §2.2 |
| `AC-03` | No cost line is changed from `CO-005` | §6.1 reconciles to 2,558 / 3,249 exactly |
| `AC-04` | No benefit line is changed from `06-02` §3.1 | §6.2 carries 45/310/645/876/920 |
| `AC-05` | NPV, IRR, payback and discounted payback are stated for all three corners | §6.3, §6.4, §6.5 |
| `AC-06` | Every arithmetic total is verified from its own inputs (`PG-M10`) | **Twenty-nine** `**Verification**` statements |
| `AC-07` | The FX basis is decided, verified and its sensitivity published | §4 |
| `AC-08` | The discount rate is derived, recommended and its immateriality shown | §5.3, §5.4 |
| `AC-09` | Claimed and claimable are separated, with the funding consequence quantified | §7 |
| `AC-10` | Every superseded return figure in the estate is listed with its status | §9.1 |
| `AC-11` | The case is mapped to a recognised framework with an honest assessment per case | §10 |
| `AC-12` | The unfavourable result is stated first and not buried | §1's summary; `BM-003-D-07` |

**Definition of done.** Complete when every criterion is met, the six corrections in §3.5 have
landed, the Board has set the discount rate under `Q-01`, and `PGD-000`'s status is updated with a
fresh enumeration timestamp.

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `CO-005` §7.1, §7.2, §7.3, §10 | **The cost basis, consumed unchanged** (`BSC-02`) |
| Upstream | `06-02` §3.1, §3.2 | Benefit lines and curve, carried; §3.2's header corrected |
| Upstream | `BM-002` §3.7, §3.8 | Claimable population and the improvement exposure |
| Upstream | `GV-004` §5.2 | The build-effort profile behind §6.1, and the slippage exposure in §8.2 |
| Upstream | `GV-007`, `GV-008` | Effort and budget, via `CO-005` |
| Downstream | **`BM-004`** | Consumes §6.2's curve as the forecast it tracks against (`BSC-20`) |
| Downstream | `GV-001`, `GV-008` | Charter justification and the budget's benefit side |
| Downstream | `GV-003` `D-014` | The decision this document informs but does not take (§8.5) |
| Downstream | `RL-005` `PIR-23`, `PIR-25` | Corrected wording; the forecast/track separation |
| Downstream | `CO-002`, `CO-003` | Affordability envelope for evaluation and the SOW |
| Lateral | `BRD` §19 | Superseded in place (§9.1) |
| Lateral | `GV-009` | Gate re-computation (`BSC-13`, `BSC-15`) |
| Lateral | `GV-010` | The independent review that tests §11's rules |
| Lateral | **`BM-005`** | `BSC-F-01`…`BSC-F-06` are seeded as lessons with landing sites |

---

## 16. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./BM-002_KPI_Baseline_Measurement_Report.md` · `./BM-004_Benefits_Realisation_Plan.md` ·
`./BM-005_Lessons_Learned_and_Continuous_Improvement_Register.md` ·
`../00_Programme_Governance_and_Control/GV-004_Integrated_Programme_Plan_and_Master_Schedule.md` ·
`../00_Programme_Governance_and_Control/GV-008_Programme_Budget_and_Cost_Baseline.md` ·
`../12_Release_Deployment_and_Transition/RL-005_Post_Implementation_Review_Standard.md` ·
`../14_Commercial_Vendor_and_Contract/CO-005_Total_Cost_of_Ownership_Model.md`

**Workspace**
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-06_Documentation_Audit_Report.md` ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md` §19 ·
`../../project_content/14_Reporting_Analytics_and_KPI/RP-015_Benefits_Realisation_and_KPI_Baseline_Register.md`

**External standards and sources**

| Source | Edition relied on | Verified |
|---|---|---|
| HM Treasury, *The Green Book: appraisal and evaluation in central government* | **2022**, published 31 March 2022; current | 2026-08-19 |
| Five Case Model / Better Business Cases | Green Book supporting guidance | 2026-08-19 |
| ISO 21502 — Guidance on project management | **2020** | 2026-08-19 |
| ISO 21503 — Guidance on programme management | **2022** | 2026-08-19 |
| MSP — Managing Successful Programmes | **5th edition**, PeopleCert | 2026-08-19 |
| PMBOK Guide | **7th edition, 2021** | 2026-08-19 |
| ISO 15686-5 — Life-cycle costing | **2017** *(consumed via `CO-005`)* | 2026-08-19 |
| AACE International RP 17R-97 — Cost estimate classification | *(consumed via `CO-005`)* | 2026-08-19 |
| USD/BDT market rate **122.00** (18 Aug 2026); **122.70** (17 Aug 2026); 12-month high 123.87 | Market series | **2026-08-19** |
| Bangladesh Bank crawling-peg mid-rate **117.00** | Bangladesh Bank regime | 2026-08-19 |

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Enterprise Architecture for the CFO | Initial issue. **Resolves `PGD-A2-10`** — the `06-02` §3.2 / BRD §19.3 column is annual, not cumulative; three-year base benefit restated from $1.96M to **$815.0K**. **Settles the FX basis** as a planning rate of 122.70 with a published band, closing `CVA-04`. **Introduces discounting** for the first time in the estate: base-case five-year NPV **−$994.2K** at 14%, payback month 92; low corner **+$624.0K** and **≈48% IRR**; high corner **−$3,139.4K** and no payback. Establishes that the **claimable** benefit without `BM-002` funding is **less than the steady-state run cost**. Recomputed at audit against `CO-005`'s restated hypercare and escalation lines (Tier 1 three-year $2,501K → $2,558K). Six new findings `BSC-F-01`…`BSC-F-06`, one CRITICAL | Board of Directors |

---

*`BM-003` · Category 15 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
