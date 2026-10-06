# Migration Rehearsal Record — migration-staging (PP6 E5)

Procedure and sign-off record for every REAL-data rehearsal load into the
`migration-staging` profile (03-DATA-STRATEGY §3 E5 / §5; governed by
MIG-01…MIG-08). One copy of this file per rehearsal run, filed under
`migrations/<run>/REHEARSAL.md`. A run is not "done" until every box is
ticked and the business owner has signed MG-004.

## Environment

| Item | Value |
|---|---|
| Profile | `infra/compose/docker-compose.migration-staging.yml` (profile `migration-staging`) |
| Database | `fix_migration` on the `pgdata-migration` volume (loopback 5434; NEVER the dev volume) |
| Loader | the migration pipeline ONLY — nothing else may write this database |
| Data class | REAL (production extracts) — a developer workstation never loads real data (DE-12) |

## Procedure (copy per run)

1. **Bring the profile up**
   `docker compose -f docker-compose.yml -f docker-compose.migration-staging.yml --profile migration-staging up -d`
2. **Extract with control totals (MIG-02)** — the pipeline emits
   `migrations/<run>/control-totals.json` per source (48 legacy sources
   profiled in Phase 1; the two live trackers feed M01/P01).
3. **Load via the pipeline** — the loader emits
   `migrations/<run>/loaded-counts.json`; every migrated record carries
   its permanent legacy reference (MIG-03 — FR-SRM-088 legacy lookup
   survives decommission).
4. **Reconcile (MG-004)**
   `python tooling/scripts/mig-totals.py --manifest migrations/<run>/control-totals.json --loaded migrations/<run>/loaded-counts.json`
   (or `--dsn postgresql://…fix_migration` for live counts). Fails closed
   on any variance.
5. **Mock migration at production volume (MG-005)** before every cutover.
6. **Business sign-off (MG-004)** on every variance; only then may a
   legacy source be scheduled for decommission (MIG-08).
7. **Point portals at migration-staging for UAT** (API base env only —
   the same code path as production, different database).

## Run record (fill per run)

| Field | Value |
|---|---|
| Run id | |
| Date | |
| Sources loaded | |
| mig-totals verdict | PASS / FAIL (attach output) |
| Variances + disposition | |
| Business sign-off (MG-004) | name / date |
| Decommission approved (MIG-08) | sources / date |

## Status

No rehearsal has run yet — the profile, the loader gate and this record
ship at PP6 as the enforceable procedure. The first rehearsal populates
the run record above.
