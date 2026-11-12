# Shared Postgres crashing under test load (13 Nov 2026)

## What happens
`compose-postgres-1` (host port 5433) runs with Docker's default **64 MB `/dev/shm`**. Postgres
takes dynamic shared memory for parallel queries and parallel index builds from `/dev/shm`
(`dynamic_shared_memory_type = posix`). Idle use is already ~32 MB (8 live segments, 13 Nov 02:32).
When several sessions run suites, clones and module upgrades at once, it overflows:

- 12 Nov 16:16 UTC onwards: `could not resize shared memory segment "/PostgreSQL.…" to 1048576 bytes: No space left on device`, then a backend crash and crash recovery. The recovery fsynced the whole data directory (172 databases, 53 GB) for **over 30 minutes**, and every database, live `fix_real` included, refused connections.
- 5 Nov 02:58 UTC: the same error asking for 33554432 bytes during a module install (`CREATE INDEX`), then `server process … was terminated by signal 11: Segmentation fault`.

A test that runs during recovery is **skipped** (`odoo_env: test database … unavailable`), not failed. A run reading "3 passed, 16 skipped" is not green.

Settings today: `shared_buffers` 128 MB, `work_mem` 4 MB, `max_parallel_workers_per_gather` 2, `max_parallel_workers` 8, `max_connections` 100 (21 in use). Docker VM: 16 CPUs, 32 GB.

## Fix (in `infra/compose/docker-compose.yml`, not yet applied)
`shm_size: "1gb"` on the `postgres` service. Docker applies it only when the container is
**recreated**. The data volume `pgdata` is kept; the dry run below changes only `compose-postgres-1`.

```bash
cd "1000fix_new_erp_system/1000_fix_codebase/infra/compose"
docker compose -p compose --env-file ../../.env -f docker-compose.yml --profile core up --dry-run --no-deps -d postgres
docker compose -p compose --env-file ../../.env -f docker-compose.yml --profile core up --no-deps -d postgres
docker inspect compose-postgres-1 --format '{{.HostConfig.ShmSize}}'   # expect 1073741824
```

Impact: about 10-30 s with no database. A clean shutdown is a checkpoint, not a crash, so there is no
long recovery. The Odoo servers on 8069/8089/8090 reconnect by themselves; open requests fail once.
Do NOT add `--remove-orphans`: the kafka, clickhouse and replica containers are listed as orphans
of this file and are still in use.

## Shortening recovery: stale databases (list only, nothing dropped)
95 `fix_*` databases (18.8 GB) have had no write since before 10 Nov and no connection now. Dropping
them would cut a crash recovery by roughly a third. Never dropped without an explicit OK. Kept regardless: `fix_real`,
`fix_dev`, `fix_test`, `fix_seedchk_tpl`, `fix_real_docchk`, `airflow`, `snapshot_verify`.

Separately, 8 `fix_real_*` rehearsal copies hold **real customer data**
(`fix_real_cfd`, `_deployreh`, `_e2e`, `_e2e3`, `_invreh`, `_invreh2`, `_purgereh`, `_m14r`). They were
written after 10 Nov, so some may still be in use by a session. Ask their owners before dropping.

| Database | MB | Last write |
|---|---:|---|
| fix_audit | 209 | 2026-10-31 07:46 |
| fix_cert_indep | 216 | 2026-11-01 18:51 |
| fix_test_a02 | 189 | 2026-11-04 09:01 |
| fix_test_a02v | 181 | 2026-11-05 19:56 |
| fix_test_a02w | 201 | 2026-11-06 10:07 |
| fix_test_a03w | 202 | 2026-11-06 10:42 |
| fix_test_a10a | 183 | 2026-11-04 01:19 |
| fix_test_a10b | 183 | 2026-11-04 01:17 |
| fix_test_a10c | 184 | 2026-11-04 01:22 |
| fix_test_a10e | 196 | 2026-11-05 22:21 |
| fix_test_a10x | 195 | 2026-11-05 22:34 |
| fix_test_a11a | 183 | 2026-11-04 00:57 |
| fix_test_a11b | 183 | 2026-11-04 00:48 |
| fix_test_a11c | 183 | 2026-11-04 00:54 |
| fix_test_a11x | 183 | 2026-11-04 10:18 |
| fix_test_a12b | 184 | 2026-11-04 04:22 |
| fix_test_a12b2 | 156 | 2026-11-05 06:34 |
| fix_test_a12b3 | 152 | 2026-11-05 06:22 |
| fix_test_a12b5 | 153 | 2026-11-05 09:28 |
| fix_test_a12base | 149 | 2026-11-05 09:13 |
| fix_test_a12c | 183 | 2026-11-04 04:23 |
| fix_test_a12d | 183 | 2026-11-04 04:39 |
| fix_test_a12f | 196 | 2026-11-07 18:29 |
| fix_test_a12f1 | 199 | 2026-11-08 11:06 |
| fix_test_a12f2 | 200 | 2026-11-08 01:06 |
| fix_test_a12f3 | 200 | 2026-11-07 22:46 |
| fix_test_a12f4 | 201 | 2026-11-07 22:45 |
| fix_test_a12f5 | 198 | 2026-11-07 23:52 |
| fix_test_a12f6 | 199 | 2026-11-08 02:02 |
| fix_test_a12int | 178 | 2026-11-05 14:02 |
| fix_test_a12x | 183 | 2026-11-04 03:57 |
| fix_test_a4b | 198 | 2026-11-04 20:05 |
| fix_test_a4b4 | 155 | 2026-11-05 12:36 |
| fix_test_a4b5 | 153 | 2026-11-05 12:36 |
| fix_test_a4b6 | 156 | 2026-11-05 12:58 |
| fix_test_a4c | 197 | 2026-11-04 20:09 |
| fix_test_a4d | 197 | 2026-11-04 20:38 |
| fix_test_a4merge | 185 | 2026-11-05 21:38 |
| fix_test_a4p | 202 | 2026-11-05 11:14 |
| fix_test_a4s | 173 | 2026-11-05 14:53 |
| fix_test_a4t | 194 | 2026-11-04 18:50 |
| fix_test_a4u | 202 | 2026-11-05 20:01 |
| fix_test_a5w | 199 | 2026-11-06 09:32 |
| fix_test_a7a | 187 | 2026-11-04 06:41 |
| fix_test_a7b | 189 | 2026-11-04 06:41 |
| fix_test_a7c | 188 | 2026-11-04 06:31 |
| fix_test_a7e | 190 | 2026-11-04 08:51 |
| fix_test_a7f2 | 210 | 2026-11-04 18:07 |
| fix_test_a7g | 190 | 2026-11-04 07:38 |
| fix_test_a7h | 186 | 2026-11-04 08:38 |
| fix_test_a7p | 192 | 2026-11-04 09:09 |
| fix_test_a7q | 191 | 2026-11-04 09:12 |
| fix_test_a7r | 195 | 2026-11-04 12:10 |
| fix_test_a7s | 194 | 2026-11-04 18:48 |
| fix_test_a7u | 211 | 2026-11-04 16:31 |
| fix_test_a7v | 222 | 2026-11-04 17:01 |
| fix_test_a7w | 210 | 2026-11-04 17:14 |
| fix_test_a7y | 210 | 2026-11-04 17:26 |
| fix_test_a7z | 200 | 2026-11-05 10:54 |
| fix_test_a8a | 183 | 2026-11-04 04:41 |
| fix_test_a8b | 184 | 2026-11-04 04:48 |
| fix_test_a8b1 | 198 | 2026-11-04 20:43 |
| fix_test_a8b2 | 198 | 2026-11-04 22:18 |
| fix_test_a8b5 | 200 | 2026-11-04 22:18 |
| fix_test_a8b6 | 198 | 2026-11-04 20:16 |
| fix_test_a8build | 194 | 2026-11-04 18:42 |
| fix_test_a8c | 183 | 2026-11-04 04:47 |
| fix_test_a8d | 183 | 2026-11-04 04:43 |
| fix_test_a8f | 217 | 2026-11-08 14:55 |
| fix_test_a8x | 183 | 2026-11-04 03:57 |
| fix_test_a9_r2b | 190 | 2026-11-04 16:08 |
| fix_test_a9_r2c | 192 | 2026-11-04 18:32 |
| fix_test_a9_r2d | 189 | 2026-11-04 12:07 |
| fix_test_a9_r2f | 192 | 2026-11-04 16:55 |
| fix_test_a9a | 183 | 2026-11-03 22:45 |
| fix_test_a9b | 183 | 2026-11-03 22:51 |
| fix_test_a9b_m21 | 185 | 2026-11-04 08:06 |
| fix_test_a9b_m55 | 185 | 2026-11-04 07:16 |
| fix_test_a9b_m56 | 186 | 2026-11-04 07:43 |
| fix_test_a9b_m57 | 185 | 2026-11-04 08:04 |
| fix_test_a9b_m58 | 185 | 2026-11-04 07:13 |
| fix_test_a9d | 183 | 2026-11-03 22:39 |
| fix_test_a9e | 183 | 2026-11-03 22:39 |
| fix_test_a9f | 198 | 2026-11-06 01:54 |
| fix_test_a9final | 193 | 2026-11-04 20:34 |
| fix_test_a9i | 184 | 2026-11-05 06:23 |
| fix_test_a9int | 188 | 2026-11-04 08:47 |
| fix_test_a9int3 | 188 | 2026-11-04 10:25 |
| fix_test_a9int5 | 196 | 2026-11-04 17:26 |
| fix_test_a9int6 | 196 | 2026-11-04 19:55 |
| fix_test_a9merge | 211 | 2026-11-05 09:16 |
| fix_test_a9p0 | 184 | 2026-11-04 08:50 |
| fix_test_a9x | 185 | 2026-11-03 23:51 |
| fix_test_all | 185 | 2026-11-04 08:38 |
| fix_test_rules | 92 | 2026-10-23 17:44 |