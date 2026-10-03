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

*Loader implementation (`db/seeds/seed.py`) lands with the first kernel
modules in Phase 3 — this manifest is its binding specification.*
