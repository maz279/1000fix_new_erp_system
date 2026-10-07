# Gateway & infra runbook (layer 4 + Docker)

## Kong (DB-less — the FILE is the config)

- Config: `infra/compose/kong/kong.yml`, mounted read-only at
  /kong/declarative into compose-kong-1. Proxy :8000, admin :8001.
- Apply changes: `docker exec compose-kong-1 kong reload` (no restart).
- Health: `docker exec compose-kong-1 kong health`; logs:
  `docker logs compose-kong-1` (+ `KONG_LOG_LEVEL=debug` env if needed).

## Route map (current truth)

- `/customer /vendor /analytics /brand /contact /partner /seller
  /corporate /web/session` → Odoo `host.docker.internal:8069`,
  **`strip_path: false`** (default TRUE silently deletes the first path
  segment — Odoo access log shows `/purchase-orders` arriving for
  `/vendor/purchase-orders`; that log line is the proof).
- `/api/odoo` → Odoo with strip (legacy path).
- CORS plugin: explicit origin list (localhost+127.0.0.1 on 3000-3007 and
  3010-3017), `credentials: true`, methods+headers for JSON-RPC.
  **No wildcard with credentials** (CORS spec). Browsers fail closed.

## CORS/preflight probe (PASS shape)

```
HTTP/1.1 200|204
Access-Control-Allow-Origin: <exact echo of Origin>
Access-Control-Allow-Credentials: true
```
If preflight passes but the POST fails: check the POST response ALSO
carries ACAO (headers are case-sensitive in probes — grep -i).

## Full-stack port census

core: pg 5433, redis 6380, ceph 9002, mailpit 8025/1025 ·
auth: keycloak 8080 (+pgbouncer) · integration: kong 8000/8001 ·
host: odoo 8069 · portals 3001/3010-17 · dev 3020/3021 · prototype 3030 ·
residency-stub 8100. Foreign neighbours on this box: crms-dev kafka/minio/
postgres on 9092/8333/9000/5432 and an unrelated app holds 0.0.0.0:3000 —
**never bind our prod to 3000-3007 on 0.0.0.0**; the pane resolves
`localhost` to that squatter.

## Docker debugging

- Liveness: `docker ps` (health column). Wedge check: `docker top <c>`
  (idle worker = blocked; ~100% CPU threads = heap spiral).
- Postgres prompt: `docker exec -it compose-postgres-1 psql -U fix -d fix_dev`.
- Compose interpolation needs `--env-file .env` from repo root; the
  migration-staging overlay additionally requires MIGRATION_DB_PASSWORD
  from the UAT host env (fails closed by design).

## Keycloak

Realm imported at first boot; portals' OIDC (corporate app) validates
issuer and uses redirect:"error"; token lands in sessionStorage
`fix_token` → Authorization Bearer via ApiClient tokenGetter. Debug at
http://127.0.0.1:8080 (admin creds from .env, env-only).
