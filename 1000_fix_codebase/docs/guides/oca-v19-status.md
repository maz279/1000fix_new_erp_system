# OCA v19 migration status — the in-repo matrix (P02-M04-T09)

**Source:** the `W0-01` assessment matrix (P01-M04-T07,
`docs/p01-m04/oca-v19-migration-matrix.md`), loaded in-repo so developers see,
per module, whether v19 support is **real or assumed**. Status values:
**M** migrated · **P** in progress · **N** not started · **A** abandoned ·
**R** reclassify (gap → own-maintenance).

Verification basis: each repository's `19.0` branch state at vendoring time
(`tooling/scripts/import-vendor.sh` records the pinned commit in
`tooling/versions.lock` [vendor]; per-module verification is the W0-01
execution step and updates this file under change control).

| # | OCA repository | Load (TSS §5.3) | Status @ vendoring | Gap decision |
|---|---|---|:--:|---|
| 1 | `server-tools` | **Heavy** — M29/M30/M64 | ☐ | migrate-or-reclassify per module |
| 2 | `web` | **Heavy** — portal UX surface | ☐ | |
| 3 | `field-service` | **Heavy** — M01/M02 service core, substatus, SLA | ☐ | |
| 4 | `helpdesk` | **Heavy** — M01 helpdesk mgmt/SLA | ☐ | |
| 5 | `hr` | Medium — M21/M55/M56 (priority raised by `MV-01`) | ☐ | |
| 6 | `payroll` | Medium — M56 | ☐ | BD statutory rates extend at L5 (M56 CR) |
| 7 | `dms` | Medium — M24 | ☐ | |
| 8 | `management-system` | Medium | ☐ | |
| 9 | `operating-unit` | Medium — `AS-03` OU fields | ☐ | |
| 10 | `account-financial-tools` | Medium — M19 (consumed from Phase 6) | ☐ | |
| 11 | `account-financial-reporting` | Medium — M19 | ☐ | |
| 12 | `reporting-engine` | Light — BI substrate | ☐ | |
| 13 | `mis-builder` | Light — M19 MIS | ☐ | |
| 14 | `stock-logistics-workflow` | Medium — M15/M41 | ☐ | |
| 15 | `stock-logistics-barcode` | Medium | ☐ | |
| 16 | `stock-logistics-warehouse` | Medium | ☐ | |
| 17 | `purchase-workflow` | Medium — M16 | ☐ | |
| 18 | `partner-contact` | Medium — M33 | ☐ | |
| 19 | `contract` | Medium — M08 | ☐ | |
| 20 | `l10n-bangladesh` | **Localisation base for `M51`/`M65`** | ☐ | BD-specific: migrate or extend at L5 |

**Count note (finding `CR-P02M04-01`):** the roadmap's heading says "18
subtrees" while its own enumeration (T03: 9 + T04: 4 + T05: 7) lists **20**
repositories. This matrix and `versions.lock` [vendor] carry all **20 named**
repositories — the enumeration is treated as authoritative until `BE-004` §5
rules on the count.

**Per-gap decision rule (migrate–defer–reclassify):** a module not migrated
to v19 by its consuming wave is **reclassified to an L5 maintenance fork** —
registered in `FORKS.yaml` with a Design-Authority-approved exit plan — never
a silent fork (`AS-05`/`FF-03`).
