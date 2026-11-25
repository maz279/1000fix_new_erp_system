# Migration Rehearsal Record — migration-staging (PP6 E5)

Procedure and sign-off record for every REAL-data rehearsal load into the
`migration-staging` profile (03-DATA-STRATEGY §3 E5 / §5; governed by
MIG-01…MIG-08). One copy of this file per rehearsal run, filed under
`migrations/<run>/REHEARSAL.md`. A run is not "done" until every box is
ticked and the business owner has signed MG-004.

## Environment

The rehearsal always loads its **own clean database, `fix_migration`** — never
the shared dev database `fix_dev` (DE-12). Every entry point (`pipeline.py`,
`rollback.py`, `load_inventory.py`, `tooling/scripts/load-master-data.py`, the
`migrations/tests` suite) defaults to it through `migrations/target_db.py`;
`--dsn` / `DATABASE_URL` / `PGHOST PGPORT PGUSER PGPASSWORD PGDATABASE` override,
and a target named `fix_dev` or `postgres` is refused. `mig-totals.py --dsn`
refuses any loopback database other than `fix_migration`.

| Item | Synthetic Wave-1 rehearsal (workstation / CI) | REAL-data rehearsal (UAT host) |
|---|---|---|
| Server | dev Postgres 17 (`compose-postgres-1`, loopback 5433) | `infra/compose/docker-compose.migration-staging.yml` (profile `migration-staging`, loopback 5434, `pgdata-migration` volume — NEVER the dev volume) |
| Database | `fix_migration`, rebuilt clean: all 71 first-party addons, no demo | `fix_migration` |
| Inputs | `migrations/extracts/*` (synthetic) + `migrations/fixtures/wave1_reference_data.json` | production extracts with their own manifest |
| Loader | the migration pipeline ONLY — nothing else may write this database | same |
| Data class | SYNTHETIC only | REAL — a developer workstation never loads real data (DE-12) |

## Procedure — synthetic Wave-1 rehearsal on a clean target

Run from the codebase root. The run is reproducible: it never depends on
whatever happens to be in a developer database.

0. **Prerequisites** — dev Postgres up, and the local residency stub (Z4,
   MIG-06; the pipeline fails fast without it):
   `docker compose -f infra/compose/docker-compose.yml --profile core up -d residency-stub`
1. **Build the clean target** (drops and recreates it; ~5-10 min):
   `python tooling/scripts/build-test-db.py --db fix_migration`
   (equivalently `FIX_TEST_DB=fix_migration`; the script only accepts
   `fix_test*` and `fix_migration`).
2. **Extracts + control totals (MIG-02)** — `python migrations/extracts_generator.py`
   (only when the extracts change). It writes the Wave-1 extracts and their
   manifest `migrations/extracts/control-totals.json` (record count +
   LF-normalised sha256 per extract) at EXTRACT time. Scope: Dhaka HQ + 5 pilot centres
   (6 branches), 50 customers (1 exact duplicate phone), 50 devices (device 50
   repeats device 1's serial — exercises the ETL-2 MDM quarantine), 20 employees,
   20 attendance opening balances. The 53-centre register (`tooling/scripts/seed-51-branches.py`,
   R08-M05) is the MG-005 production-volume scope, not this extract.
3. **Load via the pipeline** — `python migrations/pipeline.py`. It re-verifies
   every extract checksum against the manifest (fails closed on drift), then
   loads in topological order:
   - ETL-0 reference data a clean install lacks — legal entity (fixture, on the
     target's single company), operating units named in the branch extract
     (resolved; created only when the fixture names them), brands (with the
     fixture's code — never an invented one) + device models named in the device
     extract — and the 48 MD-* master-data register sets (MD-048 tiers);
   - ETL-3 branches → ETL-1 customers (M64 dedup, Z4) → ETL-2 devices →
     ETL-4 employees (JML outbox, Z4) → attendance opening balances (TSS 19.1).
     Company / operating unit of every record are its branch's; a record whose
     branch, role, owner or model is missing on the target — or whose serial /
     phone a different target record already holds — is quarantined with its
     reason, never loaded with a fallback id and never overwriting the holder;
   - emits `migrations/extracts/loaded-counts.json` (accepted + quarantined per
     entity; quarantines carry their reason), runs mig-totals and the MIG-06
     check (the extracts' NID/TIN values are searched for in every text column of
     the tables the loaders write). Every migrated record carries its permanent
     legacy reference (MIG-03). Re-running is idempotent. The closing line states
     the accepted and quarantined counts.
4. **Reconcile (MG-004)**
   `python tooling/scripts/mig-totals.py --manifest migrations/extracts/control-totals.json --loaded migrations/extracts/loaded-counts.json`
   Fails closed on any variance. Add `--dsn postgresql://fix@127.0.0.1:5433/fix_migration`
   (password via `PGPASSWORD`) to count the migrated rows live by legacy reference
   and prove the load report against the database (`[DRIFT]` fails); `--dsn` alone
   reports every quarantined record as a variance.
5. **Inventory baseline (ETL-5, Wave-2)** — `python migrations/load_inventory.py`
   (after step 3: the count sheet's locations need the branches, and its vans the
   custodian employees). It regenerates the deterministic synthetic SRC-37/SRC-38
   extracts (`--no-generate` loads the ones in `--extracts-dir` instead), loads
   parts, locations (with `LEG:SRC38:<location>` legacy references, the branch's
   company / operating unit, the plate and custodian the count sheet carries) and
   one suspense row per count line, then READS THE DATABASE BACK and writes the
   G2-04 record `docs/traceability/inventory-reconciliation-signoff.md`. Every
   number and the status in it are measured (loaded quantity vs physical count);
   rejected rows are counted and listed; sign-offs are written as `PENDING` — the
   loader never records one. Exit 0 PASS / 1 FAIL / 2 INCOMPLETE. Re-running is
   idempotent (keyed on legacy reference).
6. **Tests** — `python -m pytest migrations/tests -p no:cacheprovider -W ignore -q`.
   DB-backed tests target `fix_migration` and are SKIPPED (with the build
   command) when it does not exist. The suite re-runs the pipeline once and the
   inventory load, writing their outputs to pytest tmp dirs — it never rewrites
   the committed `migrations/extracts` or `docs/traceability` artefacts. Variant
   extracts (unknown branch / part / custodian, control-total mismatch, low
   accuracy) must come out rejected and non-PASS; their `TST-` rows are removed.
   Warranty state is derived from the warranty end date at load time
   (end 2026-06-15 ⇒ `out_of_warranty`).
7. **Rollback rehearsal (MG-007)** — `python migrations/rollback.py` deletes every
   migrated record by legacy reference (inventory baseline included) and erases its
   Z4 keys (reference data and the MD-* register stay), then reads the database
   back: it reports the baseline restored only when no migrated row is left and
   every Z4 key was erased (else INCOMPLETE, exit 1). Re-run steps 3 and 5 to prove
   a clean reload.

## Procedure — REAL-data rehearsal (migration-staging, copy per run)

1. **Bring the profile up**
   `docker compose -f docker-compose.yml -f docker-compose.migration-staging.yml --profile migration-staging up -d`
2. **Extract with control totals (MIG-02)** — one
   `migrations/<run>/control-totals.json` per run (48 legacy sources
   profiled in Phase 1; the two live trackers feed M01/P01).
3. **Load via the pipeline** pointed at the profile's database
   (`--dsn postgresql://fix@127.0.0.1:5434/fix_migration`); it emits the
   run's `loaded-counts.json`.
4. **Reconcile (MG-004)** — `mig-totals.py --manifest … --loaded …` as above.
   Fails closed on any variance.
5. **Mock migration at production volume (MG-005)** before every cutover.
6. **Business sign-off (MG-004)** on every variance; only then may a
   legacy source be scheduled for decommission (MIG-08).
7. **Point portals at migration-staging for UAT** (API base env only —
   the same code path as production, different database).

## Clean-target reproduction — 2026-10-22 (synthetic, `fix_migration`)

Fresh `build-test-db.py --db fix_migration` (71/71 addons) → `pipeline.py` →
`mig-totals.py` (file and live `--dsn` modes) → `load_inventory.py` twice →
`rollback.py` → `pipeline.py` + `load_inventory.py` reload → `pytest migrations/tests`
(52 passed, 0 skipped). Every figure below is what those runs printed / read back.

- **ETL-0**: created the legal entity `1000FIX` and 5 device models (2 brands);
  MD-* register 48 sets / 162 rows; no operating unit or brand needed inventing.
- **MIG-02**: 5/5 control totals dispositioned — branches 6, customers 50,
  devices 50, employees 20, attendance_opening 20 (file and live `--dsn` modes OK).
  Accepted 6 / 49 / 49 / 20 / **0** (124); quarantined **22**: customers 1 (M64
  duplicate phone `CUST:WP_STORE:1050`), devices 1 (MDM duplicate serial
  `SN-OPP-2026001`, source `DEV-AST-2050`), attendance opening **20** — the
  sign-in-book extract references employees `EMP-2024-001…020` (branches TEJGAON,
  BANANI, …) that are not in the Wave-1 employee extract (`E-0001…E-0020`).
  All 22 are **pending data-steward disposition (MG-004)**.
- All 49 devices load `out_of_warranty` (warranty ended 2026-06-15); company and
  operating unit of every device, warranty and employee are its branch's.
- **MIG-06**: 70 classified extract values absent from 115 text columns of the 9
  tables the loaders write.
- **ETL-5 inventory**: 150 SKUs, 10 locations, 950 count lines loaded, 0 rejected;
  physical 4,115 units vs 4,095 loaded (20 units: five lines per branch hub where the
  legacy book is one unit short) — measured accuracy **99.51%**, measured G2-04
  status PASS; valuation BDT 12,605,500.00 in suspense 110999 / STUB-M15-M19-001.
  Second run: 950 suspense rows / 950 legacy references, 10 locations, 150 parts —
  unchanged. G2-04 sign-offs (Stock Controller, Lead Inventory Auditor, System
  Architect): **PENDING**.
- **MG-007**: rollback deleted 950 suspense rows, 10 locations, 150 parts, 49
  devices, 20 employees, 69 partners and 6 branches, erased 69 Z4 keys (0 failed);
  read-back found no migrated row; the reload reproduced the figures above.

## Run record (fill per run)

| Field | Value |
|---|---|
| Run id | `WAVE1_REHEARSAL_20261016` (synthetic extracts; clean-target reproduction 2026-10-22) |
| Date | 2026-10-22 |
| Sources loaded | Branches (ETL-3), Customers (ETL-1), Devices (ETL-2), Employees (ETL-4), Attendance opening (TSS 19.1); Inventory baseline (ETL-5) |
| mig-totals verdict | PASS (measured: 5/5 control totals dispositioned; 124 accepted, 22 quarantined) |
| Variances + disposition | customers 1, devices 1, attendance_opening 20 quarantined (reasons in `migrations/extracts/loaded-counts.json`) — disposition **PENDING** |
| Rollback rehearsal (MG-007) | PASS (measured: read-back after rollback found no migrated row; 69 Z4 keys erased, 0 failed; clean reload reconciled) |
| Residency routing (MIG-06) | PASS (measured: 70 classified values absent from 115 text columns) |
| Inventory G2-04 (ETL-5) | measured PASS — accuracy 99.51% (`docs/traceability/inventory-reconciliation-signoff.md`); sign-offs **PENDING** |
| Business sign-off (MG-004) | **PENDING** — business owner / lead data steward; no signature has been recorded |
| Decommission (MIG-08) | **NOT AUTHORISED** — requires the MG-004 sign-off and the disposition of every quarantined record |

## Status

The synthetic rehearsal **WAVE1_REHEARSAL_20261016** reproduces on a clean target
with the measured results above. Gate criterion **G1-03 remains open**: the MG-004
business sign-off and the steward disposition of the 22 quarantined records are
pending, and no legacy source is authorised for decommission.

> Correction (R01 re-audit, GV-009): an earlier version of this record named a
> business signatory, stated the MG-004 sign-off as recorded, the decommission as
> authorised and G1-03 as closed. No such signature exists
> (`docs/traceability/evidence/r10-m05-mg004-business-signoff.json`: verdict
> UNMEASURED, signatory null); those statements were withdrawn.

---

## Production Volume Rehearsal Record — MG-005 (R10-M05-T02)

| Field | Value |
|---|---|
| Run id | none — no production-volume rehearsal has been executed |
| Sizing profile | MG-005 production volume on `migration-staging` (not available on a workstation, DE-12) |
| mig-totals verdict | NOT RUN |
| Rollback rehearsal (MG-007) | NOT RUN at volume |
| Residency routing (MIG-06) | NOT RUN at volume |
| Business sign-off (MG-004) | **PENDING** — no signature recorded |
| Decommission (MIG-08) | **NOT AUTHORISED** |
| Gate GP-11 | **OPEN** — measured state: `docs/traceability/evidence/r10-m05-migration-rehearsal-evidence.json` (status INCOMPLETE: MG005_PRODUCTION_VOLUME, MG007_ROLLBACK and MG004_BUSINESS_SIGNOFF UNMEASURED) |

> Correction (R01 re-audit, GV-009): an earlier version of this section reported a
> production-volume run `PROD_REHEARSAL_MG005_20261021` (53 branches, 1,250
> customers, 2,840 devices, 380 employees, 4,600 stock lots, 520 tickets) as loaded,
> reconciled, rolled back, signed off and authorised for cutover, and GP-11 as
> closed. No such run took place: `migrations/extracts/PROD_REHEARSAL_MG005_20261021-*.json`
> were written by a superseded generator that produced "production-volume" manifests
> and reconciled them against themselves (see the docstring of
> `tooling/scripts/run_production_migration_rehearsal.py`). Those two files are
> not evidence and should be deleted.
