# Single-host synthetic UAT runbook

`infra/compose/docker-compose.uat.full.yml` (project `fix-uat`) is the
business-acceptance surface for the rebuilt 8-portal estate on ONE host:
compose, not k8s. It runs alongside the developer stack without collisions.

**Environment contract — disclose at sign-off.** The stack runs
`FIX_ENV=local` (`infra/environments.yaml`: generated-synthetic-only). That is
deliberate: the customer phone-OTP dev echo (DE-11) and the dispatcher dry-run
exist only under the local contract, so testers sign in without an SMS
gateway, and Mailpit is the only mail sink (DE-07). The formal `uat`
environment — full TS-002 frozen dataset, real delivery channels, residency
service, TLS, registry digest pins — is an operator step beyond this host
(`infra/README-production.md`). Nothing here is production-shaped data.

## Ports (all 127.0.0.1 — host-only)

| Surface | Port | Surface | Port |
|---|---|---|---|
| Odoo back office | 8073 | PostgreSQL | 5437 |
| customer portal | 3400 | Redis | 6383 |
| corporate portal | 3401 | Mailpit UI | 8026 |
| analytics portal | 3402 | Mailpit SMTP | 1026 |
| seller portal | 3403 | dispatcher | 8111 |
| brand portal | 3404 | | |
| agent console | 3405 | | |
| partner portal | 3406 | | |
| vendor portal | 3407 | | |

A LAN or reverse-proxy exposure is an operator decision with TLS — not this
file. The portals use the same-origin `/api/odoo` bridge (no Kong); the
upstream is the server-configured `ODOO_INTERNAL_URL`, host-allowlisted.

## 1. Secrets

```bash
cp infra/uat/uat.env.example infra/uat/.env.uat   # git-ignored (.env.*)
python -c "import secrets; print(secrets.token_urlsafe(24))"   # per value
```

Fill `UAT_DB_PASSWORD` and `UAT_ADMIN_PASSWORD` with fresh random values.
Compose refuses to load while either is unset (`${VAR:?}`). Never commit the
filled file; never reuse production or developer credentials.

## 2. Build and start

```bash
docker compose -p fix-uat -f infra/compose/docker-compose.uat.full.yml \
  --env-file infra/uat/.env.uat up -d --build
```

First boot creates `fix_uat` EMPTY (the server runs, `/web/health` returns 500
until the registry has models) - the init step below installs `base` and every
first-party addon, after which the health check passes and the portals start.
The Odoo image build is
digest-pinned at every `FROM`; after the first build, pin the produced image
digests per `docs/guides/digest-pinning-policy.md` before any registry push.

## 3. Initialise the database (once)

Install every first-party addon through the same entrypoint (the clean-install
proof, exactly as `tooling/scripts/build-test-db.py` does for `fix_test`):

```bash
MODS=$(docker compose -p fix-uat exec -T odoo python -c \
  "import pathlib; print(','.join(sorted({p.parent.name for p in pathlib.Path('addons').rglob('__manifest__.py')})))")
docker compose -p fix-uat exec -T odoo fix-odoo-entrypoint \
  -d fix_uat -i "$MODS" --stop-after-init --http-port=8099
# i18n is a NESTED subcommand: the entrypoint inserts -c right after `i18n`,
# which argparse rejects - call odoo-bin directly with the config after the
# nested verb (verified 2026-11-24). On Git Bash prefix MSYS_NO_PATHCONV=1 so
# the /opt/... paths are not rewritten.
docker compose -p fix-uat exec -T odoo \
  /opt/venv/bin/python /opt/1000fix/vendor/odoo/odoo-bin \
  i18n loadlang -c /etc/odoo/odoo.conf -d fix_uat -l bn_BD
docker compose -p fix-uat restart odoo
```

Then seed the demo accounts and records the portals render (idempotent;
passwords come from the env file, never from the script):

```bash
set -a; . infra/uat/.env.uat; set +a
docker compose -p fix-uat exec -T \
  -e DEMO_UAT_PW -e DEMO_PARTNER_PW -e DEMO_VENDOR_PW \
  odoo fix-odoo-entrypoint shell -d fix_uat --shell-interface=plain \
  < tooling/scripts/seed-uat-demo.py
```

## 4. Verify

- `http://127.0.0.1:8073/web/health` → Odoo healthy; sign in at `/web/login`.
- Every portal `http://127.0.0.1:340x/` serves its landing; `/login` signs in;
  a protected path redirects to `/login?next=…` (the J16 smoke contract,
  `tooling/e2e/journeys/j16-portal-surfaces.spec.ts`, against these ports).
- Customer OTP: request a code for a seeded demo phone — the local contract
  echoes `dev_code`; verify signs into that phone's own portal session.
- Mailpit `http://127.0.0.1:8026` captures every outbound mail (DOFA digests,
  notifications). No real mail leaves the host.

## 5. Backup / restore (verify before sign-off)

```bash
docker compose -p fix-uat exec -T postgres \
  pg_dump -U fix -Fc fix_uat > uat-$(date +%Y%m%d).dump
# restore into a fresh database:
docker compose -p fix-uat exec -T postgres \
  pg_restore -U fix -d fix_uat --clean --if-exists < uat-YYYYMMDD.dump
```

A backup is only evidence once a restore has been read back (row counts on
the core tables) — do that before stakeholder sign-off.

## 6. Teardown

```bash
docker compose -p fix-uat -f infra/compose/docker-compose.uat.full.yml down      # keep data
docker compose -p fix-uat -f infra/compose/docker-compose.uat.full.yml down -v   # destroy data
```
