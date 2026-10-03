# OCA v19 migration assessment matrix (T07)

**Task `P01-M04-T07`** (`W0-01`) · Issued 2026-10-01 from the TSS §5.2
repository register (18 repositories, 140+ modules). **Blocking Wave 1
architecture**: discovering OCA gaps in Wave 2 means the wave is already
committed.

Status legend: **M** migrated · **P** in progress · **N** not started ·
**A** abandoned · **R** reclassify (gap → own-maintenance). Verification is
per-repository against the OCA branch state at Wave-0 — this matrix is the
instrument; the per-repo check is the W0-01 execution step.

| # | OCA repository | Carries (TSS §5.3) | Load | Status @ W0 | Gap decision rule |
|---|---|---|---|---|---|
| 1 | `server-tools` | M29/M30/M64 — server utilities | **Heavy** | ☐ | migrate-or-reclassify per module |
| 2 | `server-backend` (as registered) | performance, session, queue infra | Heavy | ☐ | |
| 3 | `web` | portal UX surface (P01/P04/P07…) | **Heavy** | ☐ | |
| 4 | `account-financial-tools` | M19 — financial reporting | **Heavy** | ☐ | |
| 5 | `l10n-bangladesh`-adjacent fiscal repos (as registered) | Mushak/VAT instruments | **Heavy** | ☐ | BD-specific: migrate or extend at L5 |
| 6 | `field-service`-related (as registered) | M01/M02 — service core, substatus, SLA | **Heavy** | ☐ | |
| 7 | `crm` | M09 pipeline | Medium | ☐ | |
| 8 | `sale-workflow` | M08 order flow | Medium | ☐ | |
| 9 | `purchase-workflow` | M16 procurement | Medium | ☐ | |
| 10 | `stock-logistics-warehouse` | M15/M41 inventory | Medium | ☐ | |
| 11 | `hr` | M21/M55/M56 HR core | Medium | ☐ | MV-01 raises its priority |
| 12 | `hr-timesheet` | M55 attendance | Medium | ☐ | |
| 13 | `project` | M67 PM | Light | ☐ | |
| 14 | `knowledge` | M61 | Light | ☐ | |
| 15 | `reporting-engine` | BI substrate | Light | ☐ | |
| 16 | `queue` | M28 jobs | Light | ☐ | |
| 17 | `rest-logistic`/API surface (as registered) | M28 API | Light | ☐ | |
| 18 | `webhook` | M28 events | Light | ☐ | |

*(Repository names follow the TSS §5.2 register's exact titles at execution
time; the six heavy-load repositories carry the material risk per TSS §5.3.)*

**Per-gap decision rule (migrate–defer–reclassify):** a module not migrated to
v19 by its consuming wave → **reclassify to L5 maintenance fork** (registered in
`FORKS.yaml` with an exit plan) — never a silent fork (`AS-05`/`FF-03`).
Pin verification: every subtree's pinned commit lands in `versions.lock`
(P02-M04-T06).
