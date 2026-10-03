# CR-P01M03-01 — Module register correction: M66/M67 are written (T10)

| | |
|---|---|
| **CR ID** | `CR-P01M03-01` |
| **Date** | 2026-10-01 |
| **Raised against** | `1000fix_ERP_Module/02_Architecture/02-02_Module_Catalogue_Master_Register.md` §3 |
| **Closes** | `B-13` (M66/M67 baselining); executes roadmap `P01-M03-T10` |
| **Allocating authority** (`DL-08`) | Module register rows are `BE-005` §6's to re-issue; evidence by direct count (`CR-01` pattern) |

## The incorrect claim (verbatim, measured 2026-08-13)

> "Only M66 and M67 remain unwritten."
> `| M66 Internal IT Service Management | | ⬜ not written | 22 (est.) | 11 PW (est.) |`
> `| M67 Project, Program & Portfolio Mgmt | | ⬜ not written | 26 (est.) | 14 PW (est.) |`
> "**Projected total (67 modules)** … ~2,978 … ~1,538 PW"

## The measured reality (this run, 2026-10-01)

| Module | On disk | Requirement rows (§5, `CR-01` pattern) | Effort estimate (spec §header) |
|---|---|---:|---|
| **M66** Internal IT Service Management | ✅ `K_Platform_and_Technology/M66_…md`, dated 2026-08-13 | **30** (was est. 22) | **14 PW** — spec states *"measured — supersedes the 11 PW estimate"* |
| **M67** Project, Program & Portfolio Management | ✅ `K_Platform_and_Technology/M67_…md`, dated 2026-08-13 | **32** (was est. 26) | **17 PW** — spec states *"measured — supersedes the 14 PW estimate"* |

The register's §3 "unwritten" claim and its Category K table (5/7, 219 reqs,
120 PW) predate the two files by the same day — the register's own measurement
stamp (2026-08-13) is the timestamp of the count, not of the files it counted.

## Required register changes

1. §3: "Only M66 and M67 remain unwritten" → **"All 67 module specifications
   are written"**; retire the correction-factor paragraph's residual ("only
   M66 and M67 remain estimated") with it.
2. Category K row: 5/7 → **7/7**; add M66 (30 reqs, 14 PW) and M67
   (32 reqs, 17 PW) as counted rows.
3. Totals: written 65/67 → **67/67**; the "projected total ~2,978 / ~1,538 PW"
   row retires in favour of counted totals. Note: the module-§5 row basis
   (3,347 with portals) and the register's 2,930 module-only figure reconcile
   via RQ-001 §3.10.5's denominator table — the register should quote the
   `CR-01` basis or none (`CR-02`).

## Baseline action (done here, per T10)

Both specifications are **baselined**: existence verified, rows counted
(30/32), measured effort recorded (14/17 PW), CD items noted (`CD-163` M66;
`CD-165/166` M67). `B-13` closes when this CR is applied to the register.
