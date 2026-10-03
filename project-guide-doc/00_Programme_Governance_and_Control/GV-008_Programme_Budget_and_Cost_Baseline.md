---
id: GV-008
title: Programme Budget & Cost Baseline
category: 00 — Programme Governance & Control
code: GV
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL — BOARD DECISION REQUIRED
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Financial Officer
approver: Board of Directors
standards_basis: ISO 21502:2020 §7.7 cost · PMBOK Guide 7th Edition (Measurement performance domain) · PRINCE2 7th Edition (2023) budget and tolerance · AACE International RP 17R-97 estimate classification · Earned value practice
traces_to: PGD-000 GV-008 · audit findings H-02 (cost understated 70–80%), AF-08, AF-09, PGD-A1-05 · decisions D-014, D-016, D-021
depends_on: GV-001, GV-003, GV-004, GV-006, GV-007
verified_on: 2026-08-18
enumerated_on: 2026-08-18 02:06 (+06)
priority: P0
needed_by: Now
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# GV-008 — Programme Budget & Cost Baseline
# 1000FiX ERP System & Portal Suite v2.0

### Category 00 · Code `GV` · ISO 21502:2020 · AACE 17R-97 · PRINCE2 7

---

> **Audit `H-02` states that the implementation cost line the Board is holding is understated by
> 70–80%, and describes itself as *"the finding with the largest financial consequence in the
> audit."* This document restates the cost position on counted effort.**
>
> The restated three-year total is **$1.02M – $2.61M, expected $1.63M**, against the **$455K –
> $780K** the Board is holding. The programme remains value-positive. **Payback moves from
> 17 months to Year 4–6.** Both statements are in this document, and the Board needs both.

---

## 1. Purpose

This document converts the effort position in `GV-007` into money, establishes the cost breakdown
structure, sets the drawdown schedule against the wave gates, and defines how cost is controlled
and variance reported.

It is the instrument by which the Board takes decision `D-014` — escalated on 2026-08-13 and, until
`GV-003` was issued, unrecorded.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The cost breakdown structure and the rate basis |
| 2 | **The restated cost position**, by work stream, with class and band |
| 3 | Reconciliation against the approved baseline and every intermediate figure |
| 4 | Contingency and management reserve |
| 5 | The drawdown schedule, gated to `GV-009` |
| 6 | **The restated return position** — payback, and the benefit that cannot be claimed |
| 7 | Cost control, variance measurement and earned value |
| 8 | Currency, inflation and rate risk |
| 9 | The three options the Board holds, priced |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The effort figures themselves | `GV-007` | Effort and rate are separate variables. Baselining them together hides which one moved |
| Total cost of ownership over 5 years, including run | `CO-005` | TCO extends beyond the programme's cost baseline |
| The business case, NPV and IRR | `BM-003` | A budget states cost; a business case states whether it is worth it |
| Benefit measurement and realisation | `BM-002`, `BM-004` | §7 states the benefit position it depends on; it does not own it |
| Vendor rates and contract commercials | `CO-002`, `CO-003` | The rate basis here is the Company's planning rate, not a negotiated price |
| Procurement of infrastructure and L6 components | `CO-006` | |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Board** | The paper for `D-014`. The restated number, the method, and the three priced options |
| **CFO** | The cost baseline, the drawdown schedule and the variance control |
| **CEO / Steering Committee** | The funding release gates and the tolerance they operate within |
| **Programme Director** | The budget they manage to |
| **Audit Committee** | Whether the restatement is defensible |
| **Implementation vendor** | The Company's planning rate basis — **not a price** |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Concept | How this document conforms | Departure |
|---|---|---|---|
| **ISO 21502:2020** §7.7 | Cost: budgeting, control, forecasting | §3 CBS, §5 drawdown, §8 control | None |
| **AACE RP 17R-97** | Estimate classification by definition maturity | Every cost line carries the class inherited from its effort input (`GV-007` §3.2) | Bands are re-derived for software, per `GV-007` |
| **PMBOK Guide 7th Edition** | *Measurement* performance domain; cost baseline vs management reserve | §6 separates contingency (in baseline) from management reserve (outside it) | None |
| **PRINCE2 7th Edition (2023)** | Budget, change budget, risk budget, tolerance | §6.3 establishes a risk budget — which `GV-005` `Q-02` records as absent | None |
| **Earned value practice** | PV / EV / AC; CPI; SPI | §8.2 defines the measures. **They cannot be computed until a baseline exists**, which is what this document creates | Simplified: EV at wave-gate granularity, not activity granularity |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| Estimation Model & Resource Plan | [`GV-007`](GV-007_Estimation_Model_and_Resource_Plan.md) §7.1 | **The effort position: 2,537 – 3,931 PW, expected 3,022 PW** |
| KPI, Benefits & Acceptance §3.3 | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02` | The approved cost model, year by year, line by line |
| Executive Summary §6 | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-02` | The v1.0 → v2.0 investment comparison; the provisional restatement |
| Technology Stack §8 | `../../1000fix_ERP_Module/02_Architecture/02-05` | Infrastructure sizing, cost progression by wave, third-party API costs |
| Documentation Audit `H-02` | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-06` | *"Understated by roughly 70–80%… the 3-year TCO of $455K–$780K is materially wrong"* |
| Category H Audit H2-08 | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-07` | At 1,513 PW the same unit rates give ~$525K–$855K |
| Content Audit `AF-09` | `../../project_content/_AUDIT/AUDIT-001` | 520–775 PW of content in no budget |
| Category 14 RP Audit | `../../project_content/_AUDIT/AUDIT-015` | `RP-02` — 44 of 95 KPI baselines absent |

### 2.3 Audit findings this document closes

| Finding | Source | Severity | How this document closes it |
|---|---|:--:|---|
| **`H-02`** | `00-06` | **High — the largest financial consequence in the audit** | §4 restates the cost on counted effort. The understatement is confirmed and is **larger than 70–80%** once all four work streams are included |
| `AF-08` | `AUDIT-001` | High | §4.4 reconciles every figure the estate has carried into one baseline |
| `AF-09` | `AUDIT-001` | High, escalated | §4.2 line 2 — content is in the budget for the first time |
| `PGD-A1-05` | `PGD-AUDIT-001` | High, OPEN | §4.2 lines 3 and 4 — both streams priced. **Closed jointly with `GV-007`** |
| `D-014` | `GV-003` | Escalated | §9 puts three priced options to the Board |
| `RSK-036` | `00-04` | Critical | The restated baseline is the treatment |
| **New — `PGD-A2-09`** | this document | — | `06-02` §3.3 states a three-year total of **$455K–$850K** in its own table while the headline in `00-02` §6.1 is **$455K–$780K**. Two upper bounds for the same baseline, in two active documents |

---

## 3. Cost Breakdown Structure and Rate Basis

### 3.1 Cost breakdown structure

```
FIX-ERP2 PROGRAMME COST
│
├── 1  PEOPLE  ─────────────────────────────────────────── ~83% of total
│   ├── 1.1  Build — 67 modules, 12 portals
│   ├── 1.2  Content — 477 files
│   ├── 1.3  Engineering definition — 127 guiding documents
│   ├── 1.4  Experience design — ~660–1,500 screens
│   └── 1.5  Programme management, assurance, PMO
│
├── 2  TECHNOLOGY  ─────────────────────────────────────── ~2%
│   ├── 2.1  Software licensing — L6 commercial components only
│   └── 2.2  Tooling
│
├── 3  INFRASTRUCTURE  ─────────────────────────────────── ~4%
│   ├── 3.1  Compute, storage, network
│   └── 3.2  Non-production environments — local, dev, staging, training, DR
│
├── 4  THIRD-PARTY SERVICES  ──────────────────────────── ~4%
│   ├── 4.1  SMS, WhatsApp, mapping, traffic
│   ├── 4.2  Identity verification, e-signature, telephony
│   └── 4.3  Payment gateway fees  (netted against revenue)
│
├── 5  CHANGE & TRAINING DELIVERY  ────────────────────── ~2%
│
├── 6  SUPPORT & MAINTENANCE  (Years 2–3)  ────────────── ~4%
│
└── 7  CONTINGENCY & RESERVE  ─────────────────────────── separate; §6
```

### 3.2 Rate basis

| Rate class | Roles | $/PW | Derivation |
|---|---|---|---|
| **Build** | Odoo, Flutter, Next.js, DevOps, data engineers, QA | **$350 – $565** | **Derived from the approved case itself**: $290K–$470K ÷ 834 PW = $348–$564/PW. Using the Company's own implied rate keeps the restatement about *effort*, not about *rates* |
| **Engineering definition** | Solution architects, data architects, security leads, senior technical authors | **$500 – $800** | Senior-architect premium over the build blend |
| **Content** | Content designers, translators, master-data authors, L&D | **$220 – $400** | Below the build blend; translation and content authoring are lower-cost roles in the Dhaka market |
| **Experience design** | UX designers, interaction designers | **$350 – $600** | Comparable to the build blend |

> **Rule `CB-01` — the rate basis is the approved case's own implied rate.** Every dollar of increase
> in this document comes from **effort**, not from a re-rating. That is deliberate: an increase
> driven by both would be unarbitrable, and the Board would not be able to tell which lever moved.

> **Assumption `GV-008-A1` — FX.** `06-02` converts BDT to USD at **110**. That rate is carried
> forward here for comparability and is **not verified**. Every benefit figure in this document is
> denominated in BDT and every cost figure in USD, so an FX move of ±10% changes the ROI by ±10%
> without changing either underlying figure. `BM-003` must verify the rate and state the sensitivity.

---

## 4. The Restated Cost Position

### 4.1 Method

| Step | Method |
|---|---|
| 1 | Take the effort position from `GV-007` §7.1 — expected value and band, per work stream |
| 2 | Apply the rate class from §3.2: low band × low rate, high band × high rate, expected × mid-rate |
| 3 | Add non-people costs from `06-02` §3.3 and `02-05` §8, unchanged where the driver has not moved |
| 4 | State contingency **separately** — §6 |
| 5 | Carry the estimate class through from the effort input (`EM-05`, `EM-06`) |

### 4.2 People cost by work stream

| # | Work stream | Effort (PW) | Rate class | **Low** | **Expected** | **High** | Class |
|---|---|---|---|---:|---:|---:|:--:|
| 1.1 | Build — 67 modules, 12 portals | 1,658 / 1,842 / 2,303 | Build | **$580K** | **$842K** | **$1,301K** | 2 |
| 1.2 | Content — 477 files | 520 / 648 / 775 | Content | **$114K** | **$201K** | **$310K** | 3 |
| 1.3 | Engineering definition — 127 documents | 264 / 352 / 528 | Definition | **$132K** | **$229K** | **$422K** | 3 |
| 1.4 | Experience design — ~660–1,500 screens | 95 / 180 / 325 | Design | **$33K** | **$86K** | **$195K** | **5** |
| | **People subtotal** | **2,537 / 3,022 / 3,931** | | **$859K** | **$1,358K** | **$2,228K** | **mixed** |

**Verification** *(regenerated from the rows per `PG-M10`)*:
low 580 + 114 + 132 + 33 = **859** ✓ · expected 842 + 201 + 229 + 86 = **1,358** ✓ ·
high 1,301 + 310 + 422 + 195 = **2,228** ✓.

> **Line 1.5 — programme management, assurance and PMO — is not costed.** It has never been sized
> by anyone and `GV-007` §7.3 lists it among seven excluded streams. On a 36-month programme this
> is conventionally 8–12% of delivery cost, which would add roughly **$110K–$270K**. It is **not**
> added to the tables below, because adding an unsized figure would breach `EM-06`. It is stated
> so that the total is read as **bounded below**.

### 4.3 Non-people cost

Carried from `06-02` §3.3 and `02-05` §8. Drivers have not been re-derived, and that is a
limitation, not an endorsement.

| # | Line | 3-year, low | 3-year, high | Basis and caveat |
|---|---|---:|---:|---|
| 2 | Software licensing (L6 only) | $0 | $36K | Telephony, RMM agent, e-signature. Zero by default under `00-02` principle 2 |
| 3 | Infrastructure / hosting | $52K | $96K | `02-05` §8.2 gives ~$71K cumulative over 3 years, consistent. **Caveat: sized for the `SB-2` scope and for a single region. `CON-13` split residency adds a Bangladesh-resident store that is not in this figure** |
| 4 | Third-party APIs | $41K | $95K | `02-05` §8.3: $1,890–$5,230/month at scale |
| 5 | Change & training delivery | $22K | $43K | **Caveat: sized for `SB-2`. 800+ employees across 51+ branches, nine waves** |
| 6 | Support & maintenance, Years 2–3 | $50K | $110K | **Caveat: sized against a 30-module system** |
| | **Non-people subtotal** | **$165K** | **$380K** | |

> **All four caveats point the same way.** Every non-people line was sized against `SB-2` — 30
> modules, single region, 18-month v1.0 horizon. None has been re-derived for 67 modules, split
> residency, 12 portals and 36 months. **The non-people subtotal is understated by an unknown
> amount**, and `PE-006` (capacity plan) and `CO-005` (TCO) must re-derive it.

### 4.4 The restated baseline

| | **Low** | **Expected** | **High** |
|---|---:|---:|---:|
| People (§4.2) | $859K | $1,358K | $2,228K |
| Non-people (§4.3) | $165K | $272K | $380K |
| **3-year cost baseline** | **$1,024K** | **$1,630K** | **$2,608K** |
| Contingency (§6.1, 16% weighted on people) | $137K | $217K | $356K |
| **3-year cost baseline + contingency** | **$1,161K** | **$1,847K** | **$2,964K** |

**Verification**: 859 + 165 = 1,024 ✓ · 1,358 + 272 = 1,630 ✓ · 2,228 + 380 = 2,608 ✓.

### 4.5 Reconciliation — every figure the estate carries

| Figure | Source | Basis | vs restated expected |
|---|---|---|---:|
| $182K – $342K | `SB-1`, March 2026 | 11 modules | — |
| **$455K – $780K** | `SB-2`, `00-02` §6.1 — **the figure the Board holds** | 834 PW, 30 modules | **2.6× the midpoint** |
| $455K – **$850K** | `06-02` §3.3 table | Same baseline, **different upper bound** | **`PGD-A2-09`** |
| $620K – $1,050K | `00-02` §2 provisional | ~1,302 PW | 2.0× the midpoint |
| ~$690K – $1,150K | `00-07` H2-08 | 1,513 PW, module build only | 1.8× the midpoint |
| **$1,024K – $2,608K, expected $1,630K** | **This document** | **3,022 PW, four work streams, counted** | **Current** |

> **`PGD-A2-09`.** `00-02` §6.1 and `06-02` §3.3 state **two different upper bounds** — $780K and
> $850K — for the same cost baseline, in two active documents, both dated 2026-08-12.
> `06-02` §3.3 carries a footnote explaining that the headline uses *"the mid-point of the
> optimistic maintenance assumption"* while its own table reflects *"the worst case on every line
> simultaneously."* That is a reasonable explanation and it is **not a reason for two numbers to
> circulate.** A baseline has one upper bound.

### 4.6 Is `H-02` confirmed?

`H-02` predicted the implementation line was understated by 70–80%.

| Test | Approved | Restated | Understatement |
|---|---:|---:|---:|
| Implementation & custom development line only, vs restated **build** | $290K – $470K | $580K – $1,301K | **2.0× – 2.8×** |
| Full 3-year TCO, vs restated total | $455K – $780K | $1,024K – $2,608K | **2.2× – 3.3×** |

> **`H-02` is confirmed and was conservative.** It measured the module-build understatement. Once
> portal build (`D-016`), content (`AF-09`), engineering definition and screen design (`PGD-A1-05`)
> are included, the full understatement is **2.2×–3.3×**, not 70–80%. The difference is not that
> `H-02` was wrong; it is that `H-02` measured one work stream and there are four.

---

## 5. Drawdown Schedule

### 5.1 Tranche structure

Per `GV-001` §7.3, the Board authorises in tranches, not in one release.

| Tranche | Covers | Released on | Amount (expected) |
|---|---|---|---:|
| **T0 — Authority & Truth** | `GV-002`, `GV-003`, `GV-007`, `GV-008`, `RR-002`, `RR-005`, `RQ-001`, `RQ-003`, `RQ-004`, `BE-005`, `BM-002`, `SC-003`, `DEP-31` legal opinion | **Charter approval** | **$130K** — 10% of the mid-point of the last approved envelope ($618K), per `GV-001` §7.3 |
| **T1 — Waves 1–4** | The v1.0 committed scope | Tranche 0 exit + `GV-008` baselined | **$980K** |
| **T2 — Waves 5–9** | New business lines | **The Wave 4 gate** (`MS-06`) — re-authorised, not authorised now (`D-017`) | **$520K** |
| | | **Total (expected)** | **$1,630K** |

**Verification**: 130 + 980 + 520 = **1,630** ✓.

### 5.2 Drawdown by wave

Derived from `GV-004` §5.2 demand and the §3.2 rate basis. Expected case.

| Period | Wave | Months | Demand (PW) | People cost | Non-people | **Total** | Cumulative |
|---|:--:|:--:|---:|---:|---:|---:|---:|
| Pre-kickoff | T0 | −3 to 0 | ~200 | $120K | $10K | **$130K** | $130K |
| Year 1 | W1–W2 | 1–8 | 384 | $186K | $32K | **$218K** | $348K |
| Year 1–2 | W3–W4 | 9–18 | 377 | $183K | $50K | **$233K** | $581K |
| Year 2 | W5–W6 | 19–26 | 207 | $101K | $62K | **$163K** | $744K |
| Year 3 | W7–W8 | 27–34 | 111 | $54K | $74K | **$128K** | $872K |
| Year 3 | W9 | 35–36 | 0 | $0 | $22K | **$22K** | $894K |
| **Parallel — all periods** | Content, definition, design | 0–36 | 1,180 | $516K | — | **$516K** | **$1,410K** |
| Support & maintenance | Yr 2–3 | 13–36 | — | — | $80K | **$80K** | **$1,490K** |
| Line 1.5 PMO/assurance *(unsized)* | | | — | *not included* | — | — | — |
| Rounding and unallocated | | | | | | **$140K** | **$1,630K** |

> **The drawdown profile is the finding, not the total.** Build demand peaks in Waves 1–4 (761 of
> 1,079 scheduled PW) while `GV-004` §5.2 shows Waves 1, 2 and 4 to be over capacity. **The money
> is needed earlier than the plan spends it, and the capacity to spend it does not exist.** That is
> the same finding as `GV-004` §5.3, expressed in cash.

### 5.3 Funding release gates

| Gate | Releases | Condition |
|---|---|---|
| Charter approval | T0 | `D-001` |
| T0 exit | T1 | `GV-007`, `GV-008` issued; `RQ-001` baselined; `RR-002` and `BE-005` issued; `D-013` taken |
| Each wave gate `G1`–`G3` | Next wave's allocation | `GV-009` gate pass |
| **Wave 4 gate `G4`** | **T2** | `D-017`. **v1.0 scope complete, evidenced.** The programme may legitimately stop here |
| Gates `G5`–`G9` | Next wave's allocation | `GV-009` gate pass |

---

## 6. Contingency and Reserve

### 6.1 Contingency — inside the baseline

Derived in `GV-007` §8.2, applied here:

| Component | Effort share | Contingency | $ (expected) |
|---|---:|---:|---:|
| Build, Waves 1–4 | ~40% | 10% | $34K |
| Build, Waves 5–8 | ~20% | 20% | $34K |
| Content | 21% | 15% | $30K |
| Engineering definition | 12% | 20% | $46K |
| Screen design | 6% | 35% | $30K |
| Non-people | — | 15% | $41K |
| **Total contingency** | | **~16% weighted** | **$217K** |

Contingency is **inside** the cost baseline, drawn by change request under `CC-08`, and reported
quarterly to the Board.

### 6.2 Management reserve — outside the baseline

| Provision | Value |
|---|---|
| Management reserve | **5% of the baseline — $82K expected** |
| Held by | Board |
| Drawn for | Realised risk that was in `GV-005` but outside the plan's assumptions |
| Rule `CB-02` | Management reserve is **not** a contingency top-up. Drawing it re-baselines the budget and is a Board decision |

### 6.3 Risk budget

`GV-005` `Q-02` records that no risk budget exists. PRINCE2 7 requires one, distinct from
contingency: contingency funds *variance in known work*; a risk budget funds *treatment of
identified risks*.

| Provision | Value |
|---|---|
| Risk budget | **$60K**, for treatment of the 12 Critical risks |
| Named calls on it | `DEP-31` legal opinion · `DEP-29` marketplace tax/legal opinion · `MG-002` legacy profiling · `RSK-008` technician field pilot · independent assurance under `GV-010` |
| Held by | Steering Committee |
| Rule `CB-03` | A Critical risk with no funded treatment is escalated to the Board monthly until it has one |

> **This closes `GV-005` `Q-02`.** It also explains why `GV-005` §8.2 records *"Critical risks with
> a treatment in progress: 0 of 12"* — there was no money to start one with.

---

## 7. The Return Position

### 7.1 Benefit, as claimed and as claimable

| Basis | BDT lac / yr | USD @110 |
|---|---:|---:|
| Claimed annual benefit at steady state, base case (`06-02` §3.1) | **876** | ~$797K |
| Benefit whose KPI has **no measured baseline** (`RP-02`: 44 of 95) | **~396** | ~$360K |
| **Benefit currently claimable** under `06-02` §6 (*"a KPI without a baseline cannot claim a benefit"*) | **~480** | **~$436K** |

### 7.2 Restated payback

Against the `06-02` §3.2 curve read as **annual** benefit (Yr 1: 45 lac · Yr 2: 310 · Yr 3: 645 ·
Yr 4: 876 · Yr 5: 920), base case, at BDT/USD 110.

| Year | Annual (lac) | Annual (USD) | Cumulative (USD) |
|:--:|---:|---:|---:|
| 1 | 45 | $41K | $41K |
| 2 | 310 | $282K | $323K |
| 3 | 645 | $586K | **$909K** |
| 4 | 876 | $796K | **$1,705K** |
| 5 | 920 | $836K | **$2,542K** |

| Cost scenario | Payback point |
|---|---|
| **Low, $1,024K** | **Year 4**, ~month 39 |
| **Expected, $1,630K** | **Year 4**, ~month 48 |
| **High, $2,608K** | **Year 6** |
| Expected cost, **claimable benefit only** (~55%) | **Year 6** |

Against the approved case's claim:

| | Approved (`06-02` §3.4) | **Restated** |
|---|---|---|
| 3-year cost | $455K – $780K | **$1,024K – $2,608K** |
| 3-year benefit, base | $1.96M | **$909K** *(from `06-02`'s own §3.2 curve)* |
| ROI, base | **221%** | **−44%** at 3 years; positive from Year 4 |
| Payback, base | **17 months** | **Year 4 – Year 6** |

> **Two things are wrong with the approved return figures, and only one of them is cost.**
>
> `06-02` §3.2 is headed *"Cumulative Benefit (Base, BDT lac)"* and lists 45 · 310 · 645 · 876 ·
> 920 for Years 1–5. **The header and the values contradict each other.** If the values were
> cumulative, Year 4 could not be 876 while the annual run rate in §3.1 is also 876, and Year 5
> could not rise by only 44. The row notes settle it — *"Year 4 (steady state) 876 — full run
> rate"* — so the values are **annual**, mislabelled as cumulative.
>
> Under **either** reading, `06-02` §3.4's base-case three-year benefit of **$1.96M** is
> unsupported by §3.2 in the same document:
>
> | Reading of §3.2 | 3-year benefit | vs §3.4's $1.96M |
> |---|---:|---:|
> | Values are **annual** (what the notes say) — 45 + 310 + 645 = 1,000 lac | **~$909K** | **2.2× overstated** |
> | Values are **cumulative** (what the header says) — 645 lac at Year 3 | **~$586K** | **3.3× overstated** |
>
> Recorded as **`PGD-A2-10`**. Its consequence is larger than the cost restatement, because it is
> independent of it: **even at the approved $610K cost, base-case payback on §3.2's own annual
> curve is roughly 27 months, not the 17 months §3.4 claims.** `BM-003` must resolve the label and
> restate §3.4.

### 7.3 The programme is still worth doing

Stated because a restatement that reports only the downside is as misleading as the figure it
replaces.

| Point | Evidence |
|---|---|
| **Value is positive over the benefit horizon.** Five-year cumulative benefit, base case: 2,796 BDT lac ≈ **$2.54M** against an expected cost of $1.63M | `06-02` §3.2 |
| **The benefit case is not disputed by any audit.** Three audits qualified the cost side; none qualified the benefit side. `00-06` §7: *"benefit figures reconcile between `00-02`, `06-02` and the module files — the issue is the cost side"* | `00-06` §7 |
| **The programme can legitimately stop at the Wave 4 gate** with the whole v1.0 commitment delivered, having spent T0 + T1 ≈ $1.11M | `GV-001` §7.3; `06-01` §1 |
| **~BDT 396 lac of benefit is recoverable, not lost** — by measuring baselines before the process changes | `BM-002`; `GV-001` `CC-09` |
| **`RQ-003` fit-gap could reduce build cost materially** — nobody has determined what Odoo 19 CE / OCA already delivers | `GV-007` §9.2 trigger 2 |

---

## 8. Cost Control

### 8.1 Rules

| Rule | Provision |
|---|---|
| `CB-04` | The cost baseline is changed only by an approved change request (`GV-003` §6) |
| `CB-05` | **Effort and rate are baselined separately.** A variance report states which moved |
| `CB-06` | Every figure carries its estimate class (`EM-06`). A bare number is not a budget line |
| `CB-07` | Cost variance is reported monthly to the Steering Committee and quarterly to the Board |
| `CB-08` | Contingency consumed without a change request is an unrecognised overrun and is reported as such |
| `CB-09` | **Commitment, not just spend, is tracked.** A signed contract is committed money whether invoiced or not |

### 8.2 Earned value

| Measure | Definition | Granularity |
|---|---|---|
| **PV** planned value | Budgeted cost of work scheduled | Per wave |
| **EV** earned value | Budgeted cost of work **accepted at a gate** | Per wave gate |
| **AC** actual cost | Spend + commitment | Monthly |
| **CPI** = EV / AC | Cost performance index | Per wave |
| **SPI** = EV / PV | Schedule performance index | Per wave |
| **EAC** = BAC / CPI | Estimate at completion | Re-forecast at every gate |

> **Rule `CB-10` — value is earned at the gate, not at the demo.** Work demonstrated but not
> accepted under `GV-009` earns nothing. This prevents the failure `06-01` §9 warns about:
> *"development does not run ahead into unaccepted work."*

### 8.3 Variance reporting

| Report | To | Frequency | Content |
|---|---|---|---|
| Spend and commitment | Steering Committee | Monthly | Actual vs planned; contingency drawn; forecast |
| Earned value | Steering Committee | Per wave gate | CPI, SPI, EAC |
| Tranche position | Board | Quarterly | Drawdown vs authorisation; tolerance position |
| Re-forecast | Board | Per wave gate | EAC against the baseline; re-baseline recommendation if outside tolerance |
| **Estimate class migration** | Steering Committee | Per wave gate | Which lines moved from class 5 → 3 → 2, and how the band narrowed |

### 8.4 Tolerance

| Level | Tolerance | Breach action |
|---|---|---|
| Wave | +15% | Steering Committee decision |
| Tranche | +10% | Board notification |
| Programme | **+10%** (`GV-001` §8.1) | **Board decision; re-baseline or descope** |

---

## 9. The Options Before the Board

`D-014` requires a choice. All four are priced on the expected case.

| # | Option | 3-year cost | Delivers | Consequence |
|---|---|---:|---|---|
| **A** | **Fund the restated position** | **$1,630K** *(+$217K contingency, +$82K reserve = $1,929K authorised)* | All 67 modules, 12 portals, full content estate, full engineering definition | Payback Year 4. Requires +15.8 FTE (`GV-007` §7.4) and the `GV-004` §7.2 re-shaping |
| **B** | **Fund Tranche 0 + Tranche 1 only; re-decide at the Wave 4 gate** | **$1,110K** now | The complete v1.0 committed scope by Month 18, plus the engineering definition needed to build it safely | **Recommended.** It is the smallest sum that produces a working system and a real decision point. `GV-001` §7.3 and `D-017` already propose it |
| **C** | **Descope Categories D, F, I or J** | **$1,630K − ~$180K = ~$1,450K** | 47–63 modules | `RSK-036` names these four. Removes 60 + 114 + 78 + 97 = **349 PW**. **`CC-05`: each removal must state the benefit forgone** — Category D alone carries BDT 125 lac of rental and refurbishment margin |
| **D** | **Defer Waves 8 and 9** | **$1,630K − ~$150K = ~$1,480K** | 36 months → ~30 months of delivery | `CON-01` and `06-01` §9 name these as the first deferral candidates. Forgoes BDT 52 lac (e-waste + dynamic pricing) and the second-country readiness (`BO-18`) |

> **Recommendation: Option B.** Not because it is cheapest — C and D are cheaper — but because it
> is the only option that does not require the Board to decide the fate of Waves 5–9 **on an
> estimate that includes a class 5 component and seven unsized work streams.** At the Wave 4 gate
> the programme will have a measured delivery factor, a completed fit-gap, a profiled legacy estate
> and eighteen months of actual cost performance. Every one of those makes the Waves 5–9 decision
> better. `GV-001-D-02` and `D-017` propose the same structure.

---

## 10. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `GV-008-D-01` | What rate basis to use | Market rates · Vendor rates · The approved case's own implied rate | **The approved case's implied rate** | Keeps the restatement about effort. A change in both effort and rate is unarbitrable | Every dollar of increase is attributable to counted effort |
| `GV-008-D-02` | Whether to include the unsized PMO/assurance line | Estimate it · Exclude and declare | **Exclude and declare** | `EM-06`: a figure without a class is not a budget line | The total is bounded below by ~$110K–$270K, and says so |
| `GV-008-D-03` | Whether to re-derive the non-people lines | Re-derive · Carry with caveats | **Carry with caveats** | Re-deriving infrastructure requires `PE-001`–`PE-006`, none of which exists. Inventing a figure would be worse | Four caveats, all pointing upward; `CO-005` must re-derive |
| `GV-008-D-04` | Whether to report the `06-02` §3.4 vs §3.2 benefit contradiction | Out of scope · Report it | **Report it** | It changes payback by 10 months **at the approved cost**, independently of this restatement | `PGD-A2-10`; `BM-003` must resolve it |
| `GV-008-D-05` | Whether to make a recommendation | Present options neutrally · Recommend | **Recommend Option B, with reasons** | `GV-004` deliberately made no recommendation because the choice was a planner's to present and a committee's to make. A budget is different: the CFO owns a recommendation | Option B; the Board may take any of the four |
| `GV-008-D-06` | Whether to create a risk budget | Fold into contingency · Separate | **Separate, $60K** | Contingency funds variance in known work; risk treatment is different work. `GV-005` §8.2: 0 of 12 Critical risks have a treatment in progress | Closes `GV-005` `Q-02` |

---

## 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | What is the current BDT/USD rate, and what sensitivity does the case carry? `06-02` uses 110 and it is unverified | CFO | Week 2 | Every ratio in §7; `GV-008-A1` |
| `Q-02` | Does the implementation vendor's rate card match $348–$564/PW? If not, the restatement understates again | CFO | Before `CO-003` | §3.2; the whole baseline |
| `Q-03` | What does a Bangladesh-resident data store cost? `CON-13` requires one and §4.3 line 3 excludes it | CTO + CFO | Before `D-013` | Infrastructure line; `SC-007` |
| `Q-04` | Is the Month 42 benefits audit funded? `06-02` §6 requires it and no line exists | CFO | Week 12 | `BM-004`; `GV-010` |
| `Q-05` | Which of the 44 unbaselined KPIs can still be baselined before their process changes? Each week reduces the answer | CFO + benefit owners | **Week 4** | ~BDT 396 lac of the case |
| `Q-06` | Is programme management (line 1.5) inside the vendor's price or the Company's cost? | CFO | Before `CO-003` | §4.2 note |

---

## 12. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every cost line traces to an effort line in `GV-007` with the same class | §4.2 |
| `AC-02` | The rate basis is derived and stated, not assumed | §3.2; `CB-01` |
| `AC-03` | Every roll-up is regenerated from its rows | §4.2, §4.4, §5.1 verification notes |
| `AC-04` | Every figure the estate carries is reconciled to the new baseline | §4.5 — six figures |
| `AC-05` | `H-02` is tested against the restatement and the result is stated | §4.6 — confirmed, and conservative |
| `AC-06` | Contingency, management reserve and risk budget are distinguished | §6.1–§6.3 |
| `AC-07` | Costs excluded from the baseline are stated | §4.2 note; §4.3 caveats |
| `AC-08` | The return position is restated, including what is not claimable | §7.1, §7.2 |
| `AC-09` | The Board is given priced options and a reasoned recommendation | §9 |
| `AC-10` | The document states the case for continuing, not only the case for concern | §7.3 |

**Definition of done.** Complete when every criterion is met, the Board has taken `D-014` by
selecting an option from §9, `CO-005` has absorbed both new work streams, `PGD-A2-09` and
`PGD-A2-10` are corrected at source, and `PGD-000` records `GV-008` as ✅ with a fresh enumeration
timestamp.

---

## 13. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | [`GV-001`](GV-001_Programme_Charter_and_Mandate.md) §7 | The envelope this document baselines; condition `CC-04` |
| Upstream | [`GV-007`](GV-007_Estimation_Model_and_Resource_Plan.md) §7.1 | The effort position converted here |
| Upstream | [`GV-004`](GV-004_Integrated_Programme_Plan_and_Master_Schedule.md) §5 | The demand profile behind §5.2 |
| Downstream | `CO-005` | TCO — must absorb both new streams (`R-04`) |
| Downstream | `BM-003` | Business case; must resolve `PGD-A2-10` and verify FX |
| Downstream | `CO-003` | Statement of Work priced against this baseline |
| Downstream | [`GV-009`](GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md) | Gates release the §5.3 funding |
| Downstream | [`GV-005`](GV-005_RAID_Register.md) | §6.3 risk budget closes `Q-02`; funds the 12 Critical treatments |
| Lateral | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02` §3 | The approved cost and benefit model, restated here |
| Lateral | `../../1000fix_ERP_Module/02_Architecture/02-05` §8 | Infrastructure and third-party cost drivers |

---

## 14. References

**Within this repository**
[`PGD-000`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`PGD-AUDIT-002`](../_AUDIT/PGD-AUDIT-002_Category_00_Governance_Audit.md) ·
[`GV-007`](GV-007_Estimation_Model_and_Resource_Plan.md) · [`GV-001`](GV-001_Programme_Charter_and_Mandate.md)

**Workspace**
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-02` §6, `00-06` `H-02`, `00-07` H2-08 ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02` §3 ·
`../../1000fix_ERP_Module/02_Architecture/02-05` §8 ·
`../../project_content/_AUDIT/AUDIT-001` `AF-09`, `AUDIT-015` `RP-02`

**External standards** *(all verified 2026-08-18)*

| Source | Used for |
|---|---|
| ISO 21502:2020 §7.7 cost | §3, §5, §8 |
| AACE International RP 17R-97 — estimate classification | §4.1 class carry-through |
| PMBOK Guide 7th Edition — cost baseline vs management reserve; *Measurement* domain | §6, §8.2 |
| PRINCE2 7th Edition (2023) — budget, change budget, risk budget, tolerance | §6.3, §8.4 |
| Earned value practice — PV / EV / AC / CPI / SPI / EAC | §8.2 |

---

## 15. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Chief Financial Officer | Initial issue. **Confirms and extends `H-02`**: the restated 3-year position is **$1,024K–$2,608K, expected $1,630K** against $455K–$780K held — **2.2×–3.3×**. Prices all four work streams including the two `PGD-A1-05` streams. Establishes contingency, management reserve and a risk budget (closing `GV-005` `Q-02`). Restates payback at Year 4–6. Raises `PGD-A2-09` (two upper bounds for one baseline) and `PGD-A2-10` (`06-02` §3.2 and §3.4 disagree on benefit by 2.2×). Recommends Option B | *pending Board* |

---

*`GV-008` · Category 00 · 1000FiX ERP System v2.0 · CONFIDENTIAL — Internal Use Only*
*1000FiX Services Limited · Hotline 16743 · info@1000fix.com · ISO 9001:2015 Certified*
