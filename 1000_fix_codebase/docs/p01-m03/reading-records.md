# Reading records and the question list (T01/T02)

**Tasks `P01-M03-T01` + `P01-M03-T02`** · Recorded 2026-10-01.

## T01 — Primary documents (programmatic reading basis)

| Document | Lines | Read/verified basis |
|---|---:|---|
| RFP | 3,942 | Structure, §17 evaluation basis, §5.4/§7.2 technology positions cross-read during P01-M02/M03 work |
| BRD | 4,525 | §21 governance chain cross-read (`P01-M01-T01` basis) |
| URD | 4,815 | User-requirement sections cross-read against module §5 tables |
| TSS | 4,398 | §1.3 six-layer stack, §4 Odoo, §7 L4 register, §11 portals, §12 CD mapping, §14.4 split residency, §18.5 licence rule, §25 currency — read in full during P01-M02 (decisions) and this milestone |
| **Total** | **17,680** | ✅ measured = the roadmap's basis exactly (scan check T01) |

The deep-read record for each `SA`/`BA`/`EL` is a team action at programme
start (a week of work per the roadmap); this codebase records the **verified
reading basis** (files, line counts, the sections load-bearing for Phase 1
decisions) and the question list below — the defects a full read must answer.

## T02 — Delivery-unit specifications

**79/79 verified on disk** (67 M + 12 P; scan check T02), each carrying
`wave:` frontmatter and §5 requirement tables with Layer columns
(3,347 rows, 0 duplicate ids). Per-unit reading assignment is a squad action;
the scan's per-module row/wave/layer counts are the reading record's
quantitative skeleton (`registers/wave-allocation.csv`).

## The question list (from this baseline — questions a full read must close)

| # | Question | Raised by |
|---|---|---|
| Q-1 | **Why do the §5 Layer columns contradict 02-05 §1 (and module §16.1) on such a scale — 92% L5 measured vs 25% claimed?** Which figure does the effort model believe? | F-P01M03-1 (fit-gap finding) |
| Q-2 | Which 40 requirement rows carry no Layer value, and who assigns them? | Scan T04c |
| Q-3 | Does RQ-009's "M40: 41 rules / M42: 27" count a form other than §9 `BRU-` rows (20/20 measured), or is the figure stale? | F-P01M03-2 |
| Q-4 | Where do the SWR-001…042 requirements wave-allocate (none carry a module)? | T08 residual |
| Q-5 | Why does the module register's 2,930 coexist with the CR-01 3,347+42 basis — which does the contract quote? | SRS baseline reconciliation |
| Q-6 | The `BRU-ECM` ten-identifier collision (RQ-009) — resolved by `RR-002` when? | Rules baseline flag |
