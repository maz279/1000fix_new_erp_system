---
id: PGD-CAT-15
category: 15 — Benefits, Measurement & Assurance
code: BM
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
owner: Programme Director / CFO
enumeration_timestamp: 2026-08-19 18:09 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# Category 15 — Benefits, Measurement & Assurance (`BM`)

## Purpose

The programme claims a **BDT 876 lac** annual benefit case. This category makes it defensible before
it is presented, and measurable after it is delivered.

> **⚠ v2.0 restates this overview's own figures.** v1.0 said *"44 of 95 KPI baselines are absent,
> which places roughly BDT 396 lac — about 45% — outside what may be claimed."* **Both figures were
> carried from `AUDIT-015` `RP-02` without being counted.** `BM-002` §3.4 counted them:
>
> | Claim in v1.0 | Counted position |
> |---|---|
> | 44 of 95 baselines absent | **71 of 95 — 75%.** 27 of the 95 rows have **no baseline column at all**, and `RP-02`'s complement silently counted them as baselined |
> | ~BDT 396 lac exposed — 45% | **BDT 542 lac — 62%.** Three improvement lines with the weakest baselines of all were omitted from the 396 |
> | *"19+ open findings"* | **219 open findings**, of 326 recorded across 38 audit documents |
>
> This is `PG-03` — *count, do not consult* — applied to this overview. All four documents are
> issued; all four are counted.

## Documents

| ID | Document | Status | Pri | Needed by |
|---|---|:--:|:--:|:--:|
| `BM-001` | KPI, Benefits & Acceptance Criteria | ✅ ⚠ `06-02` | P0 | Issued |
| `BM-002` | [**KPI Baseline Measurement Report**](BM-002_KPI_Baseline_Measurement_Report.md) | ✅ | **P0** | **Now** |
| `BM-003` | [**Business Case & ROI Model**](BM-003_Business_Case_and_ROI_Model.md) | ✅ | **P0** | **Now** |
| `BM-004` | [**Benefits Realisation Plan**](BM-004_Benefits_Realisation_Plan.md) | ✅ | P1 | W2 |
| `BM-005` | [**Lessons Learned & Continuous Improvement Register**](BM-005_Lessons_Learned_and_Continuous_Improvement_Register.md) | ✅ | P2 | W1 |

> **`BM-001` has no file in this folder, by design.** Its ✅ points at
> `1000fix_ERP_Module/06_Delivery_and_Implementation/06-02`, an existing document outside this
> repository — the same treatment `CO-001` receives for the RFP. Re-authoring it here would create a
> second KPI register, which is the defect `RP-01` records. The ⚠ stands: its cost line is
> superseded by `CO-005` and `BM-003` §9.1, and its KPI register is contradicted by `RP-01`.

## What each document establishes

| Document | The finding it turns on |
|---|---|
| **`BM-002`** | **Only 15 of 95 KPIs have both a usable baseline and a module that produces the metric; only 8 have a *precise* value and a producing module.** Benefit claimable today under `06-02` §6 is **BDT 0** |
| **`BM-003`** | **`PGD-A2-10` resolved.** `06-02` §3.2's column is **annual**, not cumulative, so the three-year base benefit is **$815.0K**, not the published $1.96M. Discounted for the first time in the estate: base-case five-year **NPV −$994.2K**, payback **month 92** |
| **`BM-004`** | **No disbenefit is recorded anywhere in the 796-file workspace**, and **no decision rule exists for a benefit that misses** — the gap `PGD-000` names as this document's reason for existing |
| **`BM-005`** | **219 open findings of 326**, a **33% closure rate across 38 audits**, and **not one finding anywhere carries an age** |

## The two numbers the Steering Committee is asked to act on

| | Figure |
|---|---|
| **Cost of measuring the missing baselines** | **31.6 person-weeks of business time** (`BM-002` §5.4) |
| **Benefit that becomes unclaimable without it** | **BDT 542 lac/yr = $441.7K/yr** at the verified rate |

> **`BM-003` §7.3 states the consequence in one line: if the baselines are never measured, the
> claimable benefit at full run rate — $272.2K a year — is *less than the cost of running the
> platform*, $354K a year.** The programme would deliver the improvements and be unable to claim
> them.

## The measurement window

`BM-002` `BMR-08` corrects an assumption the estate has been operating on:

| Measurement kind | What forecloses it | When |
|---|---|---|
| **Observational** — timed counts, effort logs, stock counts, surveys | **Go-live** | End of the wave that changes the process |
| **Record-based** — legacy extracts, job-record and claim-file samples | **Legacy decommissioning (`RL-006`)** — *not* go-live | Later, and protectable |
| **Attestation** — class `C` and `D` | Nothing | Never |

> **Roughly half the measurement programme is not foreclosed by Wave 1 go-live**, and the belief
> that it was has been suppressing the case for running it. **What forecloses it instead is
> `RL-006`, which mentions *baseline*, *KPI* and `BM-002` zero times** — `BM-002` `BMR-F-06`, fixed
> by new rule `BMR-09`.

## Rule spaces allocated

| Document | Rule space | Rules |
|---|---|---|
| `BM-002` | **`BMR`** | `BMR-01`…`BMR-18` |
| `BM-003` | **`BSC`** | `BSC-01`…`BSC-20` |
| `BM-004` | **`BRP`** | `BRP-01`…`BRP-20` |
| `BM-005` | **`LLR`** | `LLR-01`…`LLR-18` |

> Verified free across the whole workspace before allocation. **`BM-nn` is *not* used as a rule
> prefix** — it is the category's document space, and `BL-` was already taken by `RP-015`'s baseline
> rules. This is finding `AF-11` / `H-03`'s defect class, avoided rather than repeated.

## Findings raised by this category

**24 findings: 1 CRITICAL, 11 HIGH, 12 MEDIUM.** All seeded into `BM-005` §7.4 at issue, per
`LLR-11`, rather than waiting for an audit.

| The CRITICAL one | |
|---|---|
| **`BSC-F-02`** | In the high-cost / conservative corner, **steady-state annual run cost ($531K) exceeds steady-state annual benefit ($446K)**. A programme with a negative steady state has no payback at any horizon. No document in the estate states this. New rule `BSC-15` makes it a gate test |

## What "done" looks like for this category

1. All 95 registered KPIs have a **measured, signed** baseline, or a recorded class `C`/`D`, before
   the wave that changes what they measure.
2. The 250-vs-95 identifier discrepancy is reconciled to one register (`RP-001` `O-01`).
3. `BM-003`'s six corrections (§3.5) land in `06-02`, the BRD and `RL-005`.
4. Every benefit has a named owner **who has signed** (`BRP-09`), and a miss rule that has been used.
5. The 219-finding backlog is converted into lessons with landing sites, and `LM-2` — the closure
   rate — is published monthly.

## Dependencies

| Direction | Category | Relationship |
|---|---|---|
| Upstream | `03_Data` | `BM-002` measurement needs `DA-007` metric definitions to be unambiguous |
| Upstream | `14_Commercial` | `BM-003` consumes `CO-005` §7 unchanged — **at a stated timestamp**, because `CO-005` restated its hypercare and escalation lines during this category's authoring |
| Upstream | `12_Release` | `BM-004` tracking consumes `RL-005` post-implementation reviews; `BM-005` holds `PIR-33`'s output |
| **Lateral** | **`09_Migration`, `12_Release`** | **`BMR-09` binds `RL-006` and `MG-002`** — a legacy source carrying an unsigned baseline may not be decommissioned |
| Downstream | `00_Governance` | `BM-002` and `BM-003` feed `GV-001` charter and `GV-008` budget; `BM-005` feeds `GV-003` and `GV-005` |
| Downstream | `13_Change` | `BM-004` `BRP-05` — benefit delivery depends on `CH-004` adoption thresholds |

## Audience and change frequency

| Attribute | Value |
|---|---|
| Primary audience | Board, CEO, CFO, Steering Committee, benefit owners, internal audit |
| Change frequency | **Low for the model, continuous for measurement** |
| Standards basis | ISO/IEC/IEEE 15939:2017 · HM Treasury Green Book 2022 · MSP 5th edition · ISO 21502:2020 · ISO 21503:2022 · ISO 9001:2015 §10.2 · IIA Global Internal Audit Standards 2024 · PRINCE2 7 |

## Audit

[`PGD-AUDIT-CAT-15`](../_AUDIT/PGD-AUDIT-CAT-15_Category_15_Benefits_Measurement_and_Assurance_Audit.md)
— run after issue; **7 defects found and corrected in place**, including two roll-up errors in
`BM-005`'s own severity table and a whole-model recomputation of `BM-003` against a `CO-005`
revision that landed mid-authoring.

---

*Category 15 · `BM` · 1000FiX ERP System v2.0 · CONFIDENTIAL · counted 2026-08-19 18:09 (+06)*
