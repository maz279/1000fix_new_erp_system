# Seed manifest — deterministic synthetic data (P02-M06-T08/T09/T10)

`make seed` / `tasks.ps1 -Target seed` loads **synthetic data only** (DE-12:
a developer workstation never holds production data, masked or otherwise) from
a **fixed random seed** (`1000fix`), **Bengali-first** (DE-17: an interface
that has only ever been seen with English data hides its layout defects until
UAT), and **state-complete** (DE-16: a state that seed data cannot reach is a
state nobody tests).

## Volumes (BE-001 §6.5)

| Entity | Volume | Notes |
|---|---:|---|
| Branches | 5 | Dhaka, Chattogram, Sylhet, Khulna, Rajshahi — names in Bengali and English |
| Users | ~25 | Across the role register (roles mirror the synthetic Keycloak realm, DE-09) |
| Customers | 200 | Bengali-first names/addresses; NID values are synthetically CHECKSUM-VALID fakes, never real |
| Devices | 500 | Across brands and warranty states |
| Service orders | 300 | **Across every state of the state machine** (DE-16) — including on-hold, rework, QC-reject, closed-lost |
| Products | 400 | Bilingual names, priced in BDT |
| SLAs | 60 | Multi-clock variants incl. paused and breached |

## Rules baked into `db/seeds/seed.py`

1. **Fixed seed**: `random.seed("1000fix")` — identical data on every load;
   order-dependent test failures are impossible to blame on the seed.
2. **Bengali-first**: primary name/address fields are Bengali; English is the
   secondary. Where the UI shows one, the seed shows the Bengali one first.
3. **State-complete**: the loader enumerates state-machine states from the
   model's selection fields, not a hardcoded happy path list.
4. **Residency-safe**: no seed value matches the residency-classified pattern
   set (doctor check 12). NID-shaped values use the reserved synthetic range.
5. **No outbound anything**: the seeder runs against `127.0.0.1` endpoints
   only; `fix_env_guard.assert_local()` is its first import (DE-11).
6. **Idempotent append**: every block searches before it creates
   (`--force` appends without duplicating; verified by double-run with
   exact row counts).
7. **Statutory-valid**: seeded rows satisfy the business constraints
   (VAT treatment rates, 13-digit BINs, masked-vs-non-masked SMS routes
   per BD-02, consent proof-on-grant, BRTA vehicle fitness/insurance,
   bilingual template names per AS-12).

## Coverage (P02-P11 audit, 2026-10)

Every transactional anchor and config master carries seed rows. The only
empty `fix_*` tables, by design, are:

| Class | Tables | Why empty |
|---|---|---|
| Detail lines of seeded parents | `*_line`, `*_item`, `*_part`, `*_turn`, `*_response`, `*_evidence`, `custody_scan`, `diagnostic_node`, `revenue_schedule`, `incentive_line`, `period_close_line` | Created by their parent flows (an estimate's lines arrive with the estimate), never standalone |
| M2M junctions | all `*_rel` tables | Populated through parent record writes |
| Pipeline-managed reference data | `fix.country.pack(.line)`, `fix.bd.address`, `fix.feature.flag`, `fix.retention.class` | AF-09/MD-005: loaded by the master-data pipeline; ACLs deny user creates |
| Flow outputs with read-only ACLs | `fix.beftn.batch` | Created by the payroll approval flow, never by hand |

Fixed taxonomy ships as **noupdate module data**, not seed rows:
isolation tiers T0-T5 (`cd_rbac_ext/data/fix_isolation_tiers.xml`) and
refurbishment grades A-E (`cd_catalogue/data/fix_refurb_grades.xml`).

*Loader implementation (`db/seeds/seed.py`) lands with the first kernel
modules in Phase 3 — this manifest is its binding specification.*
