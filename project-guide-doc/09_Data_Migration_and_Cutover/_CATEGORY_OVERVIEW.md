---
id: PGD-CAT-09
category: 09 — Data Migration & Cutover
code: MG
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
owner: Migration Lead
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
audit: ../_AUDIT/PGD-AUDIT-CAT-09_Category_09_Data_Migration_and_Cutover_Audit.md
enumeration_timestamp: 2026-08-19 09:30 (+06)
---

# Category 09 — Data Migration & Cutover (`MG`)

> **v2.0 — the category is authored.** All seven `MG` documents were written on 2026-08-18 and
> audited in [`PGD-AUDIT-CAT-09`](../_AUDIT/PGD-AUDIT-CAT-09_Category_09_Data_Migration_and_Cutover_Audit.md).
> The category moves from **0 ✅ / 3 ◐ / 1 ⬜ / 3 ⛔** to **7 ✅**, qualified per `PGD-A2-25` —
> tests (a), (b) and (c) of `PGD-000` §0.3 are met; test (d)'s **approval record** cannot exist
> until `GV-001` `CC-01` constitutes a body that can create one.
>
> The audit identifier is **category-keyed** (`PGD-AUDIT-CAT-09`), following the precedent set by
> `PGD-AUDIT-CAT-07`, because sequential allocation under concurrent authoring is the mechanism
> behind five identifier collisions in this repository (`PGD-A7-01`). `PGD-AUDIT-008` was taken by
> Category 05 while this category was being written.

## Purpose

`project_content/12_Data_Migration_Content/` holds **14 migration content files** — seven
field-mapping workbooks, data quality rules, load templates, reconciliation report specifications
and a cutover data checklist.

`AUDIT-011` raised the gap beneath them as **CRITICAL**:

> **`06-03_Data_Migration_Strategy.md` does not exist**, so migration has no technical
> specification. **Two migration domains have no workbook**; **all 48 legacy sources are
> unprofiled**.

**That gap is now closed at the specification layer.** `AUDIT-011` `DM-01` enumerated seven
unspecified items; every one is now owned by an issued document. What remains open is **execution**,
and §"What is still open" below states it plainly.

## Documents

| ID | Document | Size | Rules | Status | Pri | Needed by |
|---|---|---:|---|:--:|:--:|:--:|
| `MG-001` | [**Data Migration Strategy**](MG-001_Data_Migration_Strategy.md) | 65 KB | `MST-01`…`MST-31` | ✅ † | **P0** | **Now** |
| `MG-002` | [**Legacy System Profiling & Extract Specification**](MG-002_Legacy_System_Profiling_and_Extract_Specification.md) | 60 KB | `LPX-01`…`LPX-43` | ✅ † | **P0** | **Now** |
| `MG-003` | [ETL Design & Transformation Rules Specification](MG-003_ETL_Design_and_Transformation_Rules_Specification.md) | 58 KB | `ETR-01`…`ETR-50` | ✅ † | **P0** | W1 |
| `MG-004` | [Reconciliation & Validation Plan](MG-004_Reconciliation_and_Validation_Plan.md) | 44 KB | `RVP-01`…`RVP-33` | ✅ † | P0 | W1 |
| `MG-005` | [Mock Migration & Dress Rehearsal Plan](MG-005_Mock_Migration_and_Dress_Rehearsal_Plan.md) | 38 KB | `DRH-01`…`DRH-31` | ✅ † | P0 | W2 |
| `MG-006` | [Cutover Plan & Runbook](MG-006_Cutover_Plan_and_Runbook.md) | 47 KB | `CUT-01`…`CUT-36` | ✅ † | P0 | W2 |
| `MG-007` | [Rollback & Fallback Plan](MG-007_Rollback_and_Fallback_Plan.md) | 43 KB | `RBK-01`…`RBK-33` | ✅ † | P0 | W2 |
| | **Total** | **357 KB** ¹ | **257 rules** | | | |

¹ **Measured, not summed.** 357,707 bytes at 2026-08-19 09:50 (+06); truncated per the house convention (`BE-005` 110,392 bytes is recorded as 110 KB). The rounded per-file figures
above add to 355; the total is the measurement, not their sum. `PG-M10` — regenerate, do not
accumulate.

† Qualified ✅ — see the note above and `PGD-A2-25`.

## What each document added that Category 12 could not

`MST-01` governs the seam: **a rule stated in Category 12 is adopted by citation and never
restated.** These documents therefore add mechanism, never content.

| Document | The question Category 12 leaves open | What was added |
|---|---|---|
| `MG-001` | *How does data get from the legacy estate into the ERP?* | The approach **derived** (phased, per wave, bounded parallel run); the five-stream operating model; the nine-stage lifecycle; the tolerance hierarchy; the environment position; **the lawful-basis block** |
| `MG-002` | *What does "profiled" mean, and how do you profile paper?* | A six-condition definition with owner acceptance; a method for **all eight source classes**, including the 36 of 48 no tool can read; Bengali encoding verification; the extract manifest; **the one irreversible deadline** |
| `MG-003` | *What actually executes?* | Seven pipeline zones; the ORM `load()` mechanism with deterministic external identifiers; the residency second pass; the transformation-rule catalogue; lineage; merge reversibility; delta capture; **event suppression** |
| `MG-004` | *Who signs, on what evidence?* | Segregation of duties; control-total derivation and freezing; **a stated `R5` sampling basis**; the evidence pack; external-verification scheduling; exception drain rates |
| `MG-005` | *How long does any of this take?* | Four rehearsal types; per-wave counts; the measurement protocol **including the human steps**; the window arithmetic; the branch count rehearsal; **the rollback rehearsal that supplies trigger `T4`'s number** |
| `MG-006` | *Who does what, at what hour?* | The incident-command role structure; the runsheet with a worked W1 instance; the 51-site zone model; live evidence capture; checkpoint conduct; the post-cutover review |
| `MG-007` | *How is any of it undone?* | Four rollback mechanisms; **three points of no return**; the data-loss position at every stage; the fallback operating model distinct from `OP-014`; the re-attempt gate |

## The seven `AUDIT-011` `DM-01` items, discharged

| # | Unspecified item | Now specified in |
|:--:|---|---|
| 1 | ETL / orchestration platform, retry, checkpointing, idempotency | `MG-003` §3, §5, §12 |
| 2 | Staging-layer architecture | `MG-003` §4; environment position `MG-001` §7 |
| 3 | Environment topology and masking mechanism | `MG-001` §7 → **`PE-002`, still absent** |
| 4 | **Rollback mechanics and their measured duration** | `MG-007` §4, §7 + `MG-005` §8 |
| 5 | Merge reversibility for the burn-down period | `MG-003` §9.4 |
| 6 | Delta capture during the parallel run | `MG-003` §10 |
| 7 | **The migration tooling itself** (BRD `MIG-008`) | `MG-003` §3 — **and it has no build component**, `MGA-01` |

## Why unprofiled sources still invalidate the mapping workbooks

`DM-004` through `DM-010` are seven field-mapping workbooks covering party, device, service
history, inventory, finance, HR and contracts. They map **from** 48 legacy sources that
**nobody has looked inside**. `profiling_status` was `not_started` on all 48 at enumeration.

A mapping written against *assumed* source structure is a hypothesis, not a specification.
**`MG-001` `MST-13` now makes the re-verification mandatory** — and its effort is still in no
estimate (`MG-001` `Q-03`).

| Migration domain | Workbook | Source profiled? |
|---|---|:--:|
| Party & customer | `DM-004` | ✗ |
| Device & asset | `DM-005` | ✗ |
| Service history & jobs | `DM-006` | ✗ |
| Inventory & parts | `DM-007` | ✗ |
| Finance & open items | `DM-008` | ✗ |
| HR & payroll | `DM-009` | ✗ |
| Contracts, warranty & claims | `DM-010` | ✗ |
| **Catalogue & pricing — a W1 load** | **none** | ✗ |
| **Documents & paper archive — 500,000+ records** | **none** | ✗ |

`MG-001` `MST-27`: a disposition `M` dataset with no mapping workbook is **blocked at lifecycle
stage 3**. The catalogue domain blocks part of W1 today.

## Cutover is an operational document, not a data document

`DM-014` provides the cutover **data checklist and freeze communication**. `MG-006` supplies the
operational runbook: **who does what, in what order, at what hour, with what abort criteria** —
plus the command structure, the zone model for 51+ sites, and the evidence captured live.

For a business running 51+ branches serving 250,000+ customers a month, cutover windows are
measured in hours, and the timing must be **measured in rehearsal** (`MG-005`), not estimated.
**The runsheet in `MG-006` §5 ships with `[R3]` placeholders where every duration goes** — because
`CV-13`, `ETR-49` and `DRH-13` all forbid publishing a duration nobody has measured.

## What "done" looks like for this category

| # | Criterion | State |
|:--:|---|---|
| 1 | `MG-001` states the approach per wave and what is **not** migrated | ✅ §4, §10 |
| 2 | All 48 legacy sources profiled: schema, volume, quality, extract, freeze, owner | ⬜ **Specified (`MG-002`), unperformed** |
| 3 | `MG-003` transformation logic executable, restartable, producing lineage | ✅ Specified; **no build component** (`MGA-01`) |
| 4 | `MG-004` reconciles rows, values and financial control totals to a stated tolerance, signed | ✅ Specified; **external verifiers unengaged** |
| 5 | At least two full dress rehearsals with measured timings before the first production cutover | ✅ Specified (`MG-005` §4); **none performed** |
| 6 | `MG-007` states the point of no return and the data-loss position at each stage | ✅ §5, §6 |

**Three of six are specification-complete and execution-blocked.** That is the honest position of
this category at issue.

## What is still open

The category's own open questions total **40 across seven documents**. Six matter above the rest:

| # | Open item | Owner | Needed by |
|:--:|---|---|:--:|
| 1 | **The lawful basis for the migration processing is not recorded anywhere.** `MST-21` blocks every personal-data load; 100,000+ data subjects at W1 | Legal Counsel with the DPO | **W1** |
| 2 | **The migration tooling has no build component** — no `CD` identifier, no wave, no effort, against P0 contractual `MIG-008` | Chief Architect with `GV-007` | **W0** |
| 3 | **Profiling is funded by nobody**, and it unblocks the estimate, the thresholds, the workbooks and the window | Programme Director with `GV-007` | **W0** |
| 4 | **`SRC-001`/`SRC-002` expire at W2** and their data is then unrecoverable — the only irreversible deadline in the programme | CTO | **Immediately** |
| 5 | **The physical-verification programme is in no plan** — 13 business commitments against Data Owners at 20% | Programme Director | **W0** |
| 6 | **`migration-staging`, the rehearsal environment, and snapshot/restore have no owning design** (`PE-002`, `PE-007` absent) | CTO | **W1 − 3 months** |

## Dependencies

| Direction | Category | Relationship | State |
|---|---|---|---|
| Upstream | `03_Data` | Every mapping targets the `DA-001` schema and `DA-002` dictionary | ✅ Issued |
| Upstream | `05_Security` | NID/TIN/biometric migration engages `SC-007` residency and the `CD-233` path | ✅ Issued |
| Upstream | `02_Architecture` | `AR-009`'s outbox is why migration needs event suppression (`MGA-04`) | ✅ Issued |
| Upstream | `00_Governance` | `GV-009` gates consume the evidence packs; `GV-003` must record the lawful basis | ✅ Issued |
| **Upstream** | **`10_Infrastructure`** | **`PE-002` must specify `migration-staging` and the rehearsal environment; `PE-007` the snapshot/restore** | **⛔ Absent** |
| Lateral | `08_Quality` | `QA-004` test-data masking and `QA-002` UAT overlap `MG-001` §7 and `MG-005` `R2` — **seam unreconciled** | ✅ Issued during this session (`MGA-07`) |
| Downstream | `12_Release` | `RL-002` must honour `CUT-01`; `RL-003` consumes the evidence packs; `RL-006` must not retire legacy while fallback depends on it | ⛔ Absent |
| Downstream | `11_Operations` | `MG-006` `CUT-35` hands over to `SV-005`; `MG-007` §10 escalates to `SV-006` | ⛔ Absent |
| Downstream | `13_Training` | Branch counting training and the Bengali instruction set (`DRH-24`, `CUT-23`) | ⛔ Absent |

## Audience and change frequency

| Attribute | Value |
|---|---|
| Primary audience | Migration team, DBAs, finance controllers, branch managers, business owners |
| Change frequency | **High during W1–W3, then per-wave cutover** |
| Standards basis | DAMA-DMBOK 2.0 · PDMv2 (BCS 2012) · ISO 8000-61:2016 · ISO/IEC 25012 · ISO/IEC/IEEE 29119-3:2021 · ISA 500/530 · ITIL 4 · ISO/IEC 20000-1:2018 · ISO 22301:2019 · Odoo 19.0 ORM |
| Local rule prefixes | `MST` · `LPX` · `ETR` · `RVP` · `DRH` · `CUT` · `RBK` — each verified unused workspace-wide before allocation (`MGA-02`) |

## Existing material built from

`project_content/12_Data_Migration_Content/DM-001…014` — all 14 files ·
`project_content/_AUDIT/AUDIT-011_Category_12_DM_Content_Audit.md` — 12 findings, 10 open ·
`project_content/17_Operations_Support_and_Runbooks/OP-014_Manual_Fallback_Procedure_Set.md` ·
`1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02` §12 (11 source domains, `MIG-01`…`MIG-07`) ·
all 67 module files §16.4 (per-module migration tables) ·
`primary-doc` BRD §6.1, §6.5, §11.6 (`MIG-001`…`MIG-015`) and TSS §8.2, §14

---

*Category 09 · `MG` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
