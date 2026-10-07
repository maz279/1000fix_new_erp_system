# Data layer runbook (PostgreSQL + Odoo data discipline)

## Connection

`docker exec -it compose-postgres-1 psql -U fix -d fix_dev`
(host port 5433; user fix; password from .env only).

## Slow-screen autopsy (in order)

```sql
-- 1. what is actually slow (needs pg_stat_statements)
SELECT calls, round(mean_exec_time::numeric,1) AS ms,
       round(total_exec_time::numeric,0) AS total_ms, left(query,90)
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;

-- 2. plan truth for the winner (from Odoo's debug_sql log or app)
EXPLAIN (ANALYZE, BUFFERS) <that query>;

-- 3. who is blocking whom right now
SELECT pid, state, wait_event_type, wait_event, left(query,80)
FROM pg_stat_activity WHERE wait_event_type IS NOT NULL OR state <> 'idle';
```

Odoo-side: restart with `--log-level=debug_sql`, fire the slow screen,
count queries for ONE request. >50 queries = read_group/N+1 smell; look
for `search` inside loops in controllers/models.

## Locks & deadlocks

- `log_lock_waits = on` (or `deadlock_timeout` tuning) to log victims.
- `pg_locks JOIN pg_stat_activity` for the blocker's pid/query.
- Odoo cursor-level: a long transaction holds row locks — check for a
  stuck `--dev=pudb` breakpoint or an open shell session.

## Data-class discipline while debugging (03-DATA-STRATEGY)

- Dev DB holds ONLY synthetic seed + `PP5-LIVEFIRE-*` tagged probe rows.
  Before blaming "wrong data", check which population a row belongs to
  (`SEED-` prefixes vs livefire tag vs your own create).
- `db/seeds/seed.py` REFUSES a second run (exit 2) by design; reseed is
  `-Target reset` (drops volume). Never mix real data into dev (DE-12).
- Deleting probe rows: children before parents, or archive (`active=False`).
- Migration-staging (real data) lives in a SEPARATE profile/volume — never
  point dev debugging at fix_migration.

## Money & precision

- All monetary math backend-side in Odoo (Decimal, currency fields).
  Client displays BN-007 strings only. If a total looks wrong: reproduce
  via the model's compute in Odoo shell, never in a calculator.
- Decimal/Float boundary: tax engine returns Decimal — coerce once
  (`float(sum(...))`) when storing into float/Monetary computes (scar #8).

## Useful one-offs

```sql
-- row counts of the core tables (sanity vs seed manifest)
SELECT relname, n_live_tup FROM pg_stat_user_tables
WHERE relname LIKE 'fix_%' ORDER BY n_live_tup DESC LIMIT 15;

-- find the table behind a model (snake_case of the _name)
SELECT table_name FROM information_schema.tables
WHERE table_name = 'fix_service_order';
```
