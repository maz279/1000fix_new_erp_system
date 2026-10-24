# Deployment Guide — 1000 FiX ERP v2.0

**Status:** honest local-harness deployment path (R01 re-audit, 2026-10-22).
**What is proven:** every command below has been executed on this workstation
against the live stack. **What is NOT proven:** a cloud/production host — k3s/
Terraform are absent and recorded OPEN (see the R02-R11 correction report).

---

## 1. Prerequisites

| Requirement | Verified value |
|---|---|
| Docker Engine + compose v2 | Docker Desktop, 16 CPU / 31 GiB |
| Node.js | 22.x (portals), npm per-portal lockfiles |
| Python | 3.12 (`py -3.12`) for tooling, Odoo and services |
| Postgres (compose) | 17.4 image, ICU/UTF-8 initdb |
| Ports free | 5433, 6380, 8000/8001 (Kong), 8069 (Odoo), 8080 (Keycloak), 8081 (Airflow), 8084 (telemetry), 8100 (residency stub), 8110 (dispatcher), 8120 (identity), 3001 + 3010-3017 (portals) |

Local secrets live in `.env` (git-ignored; see `.env.example` for the full
list including the three Novu secrets generated per environment).

## 2. Infrastructure stack

```bash
cd 1000_fix_codebase
docker compose -f infra/compose/docker-compose.yml --env-file .env \
  --profile core --profile auth --profile integration up -d
```

Brings up (verified healthy 2026-10-22): postgres, redis, object-store
(CEPH), mailpit, residency-stub, keycloak, pgbouncer, kong, identity-
lifecycle, novu-mongo, novu, notification-dispatcher, airflow.

Profiles `field`, `observability`, `intelligence`, `asset-ml` extend the
stack (Traccar/OSRM/VROOM, Prometheus/Grafana/Loki/Tempo, ClickHouse+dbt,
Kafka×3/MLflow/Ollama) — start them when those subsystems are exercised.

## 3. Odoo backend

```bash
python tooling/scripts/generate-odoo-conf.py        # local.conf + local.resolved.conf
PYTHONPATH="$(pwd)" python vendor/odoo/odoo-bin \
  -c infra/odoo-conf/local.resolved.conf -d fix_dev  # http://127.0.0.1:8069
```

All 71 first-party modules install cleanly (`-i <list>` from
`tooling/scripts/...` or module names from `addons/*/__manifest__.py`).
The 338 generated AS-03 isolation rules ship inside each module
(`security/fix_isolation_rules.xml`, regenerate with
`python tooling/generators/generate-isolation-rules.py`).

**Production posture:** `python tooling/scripts/generate-odoo-conf.py
--profile prod` emits `infra/odoo-conf/prod.conf` — `list_db=False`,
`workers=4`, `proxy_mode=True`, `dbfilter`, no demo data, secrets as
`${VAR}` placeholders the deployment injects. Never run prod against the
development `.env`.

## 4. Web portals (8)

```bash
cd apps/web/<portal> && npm run build      # output: "standalone" (all 8 verified)
npx next start --port 3010                 # customer; 3001 corporate; 3012-3017 rest
```

Container image (context = repo root):

```bash
docker build -f apps/web/Dockerfile.portal --build-arg PORTAL=customer \
  -t 1000fix/portal-customer:local .
```

Multi-stage, non-root (UID 10001), healthchecked, ships only
`.next/standalone`.

## 5. Gateway

Kong (DB-less) config `infra/compose/kong/kong.yml` routes the portal API
surface to Odoo (`/customer /vendor /analytics /brand /contact /partner
/seller /corporate /technician /storefront /p03 /web/session`, plus
`/api/odoo/*` stripped), CORS-with-credentials for the portal origins,
rate limiting 300/min, and HSTS/nosniff/DENY response headers. Reload after
edits: `docker exec compose-kong-1 kong reload`.

## 6. Verification battery (run before any release)

```bash
python tooling/fitness/run.py                     # 28+ checks, 0 failures expected
python -m pytest addons services libs             # estate suite
python tooling/scripts/measure-coverage.py        # coverage gates
python tooling/scripts/doctor.py --json docs/traceability/evidence/doctor.json
powershell -File tooling/gate/verify-gate-g0a.ps1 -Json tooling/gate/evidence/gate-g0a-latest.json
# ... G0b, G1a, G1, G2..G9, GP likewise
python tooling/ci/run-pipeline.py --profile pre-merge
python tooling/ci/run-pipeline.py --profile nightly
node tooling/e2e/visual-drive.mjs                 # 36/36 expected with all portals up
node tooling/e2e/headers-sweep.mjs                # 24/24 expected
python tooling/e2e/api-sweep.py                   # 67/67 routes probed
pre-commit run -a                                 # full hook suite
```

## 7. Known OPEN items (do not paper over)

- Real GitHub Actions execution (gh unauthenticated locally) — pipeline
  evidence is labelled `runner: local-harness`.
- External credentials: bKash/Nagad/SSLCOMMERZ, NBR IVAS, bank feeds,
  CPaaS/telephony, SMS gateways — all integrations fail CLOSED without them.
- Odoo image build + registry push (digests PENDING-FIRST-BUILD until then).
- k8s/Terraform manifests (`infra/k3s`, `infra/terraform` are empty).
- Env-ladder compose port collisions (see correction report) — the twelve
  environments cannot run concurrently on one host yet.
- Independent penetration test, production cutover, and all human sign-offs.
