#!/usr/bin/env bash
# =============================================================================
# ci-stack-up.sh - bring up the LIVE stack the nightly stages test against, on
# a clean GitHub-hosted runner (ci.yml stages 5 integration + 13b journeys).
#
# R01 re-audit 2026-10-22: both nightly jobs ran `docker compose --profile
# full up` with no .env (every service's ${..:?} interpolation fails) and with
# a profile no service declared (nothing would start), and no step started
# Odoo or a portal - the journeys targeted ports nothing served. This script
# is the one place that builds the stack, so the two jobs cannot drift.
#
#   bash tooling/e2e/ci-stack-up.sh [--portals]
#     always : .env from .env.example (dev placeholders only), generated
#              odoo conf, compose core (+ kong when --portals), clean fix_test
#              build of every cd_* addon, Odoo on :8069 with FIX_ENV=local
#     --portals: Kong gateway :8000 + the 8 Next.js portals on the journey
#              port map (tooling/e2e/journeys/helpers.ts PORTALS)
#
# Exit non-zero on the first thing that does not come up healthy - a stage
# never runs against half a stack. Runs from the codebase root.
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")/../.."

PORTALS=0
[ "${1:-}" = "--portals" ] && PORTALS=1
LOGS=tooling/e2e/results/stack
mkdir -p "$LOGS"

# Wait until URL answers 2xx/3xx, or fail with the tail of LOG.
wait_http() { # url label log [tries]
  local url=$1 label=$2 log=$3 tries=${4:-60}
  for _ in $(seq 1 "$tries"); do
    if curl -s -o /dev/null -w '%{http_code}' "$url" | grep -qE '^[23]'; then
      echo "ci-stack-up: $label up ($url)"
      return 0
    fi
    sleep 5
  done
  echo "ci-stack-up: FAIL - $label not reachable at $url"
  [ -f "$log" ] && tail -n 60 "$log"
  return 1
}

# 1. Environment: the runner has no .env (git-ignored, DE-10). The example
#    holds development-only placeholders - never a real credential.
[ -f .env ] || cp .env.example .env
uv run python tooling/scripts/generate-odoo-conf.py

# 2. Backing services. Kong (integration profile) is started by name so the
#    rest of that profile (Airflow, Novu) stays down on a 7 GB runner.
COMPOSE=(docker compose -f infra/compose/docker-compose.yml --env-file .env --profile core)
if [ "$PORTALS" = 1 ]; then
  "${COMPOSE[@]}" --profile integration up -d --wait postgres redis object-store mailpit residency-stub kong
else
  "${COMPOSE[@]}" up -d --wait
fi

# 3. Clean build of every first-party addon (also the clean-install proof).
#    Connection comes from the generated local.resolved.conf (127.0.0.1:5433).
uv run python tooling/scripts/build-test-db.py --db fix_test

# 4. Odoo. Kong reaches it as host.docker.internal (host-gateway = the docker
#    bridge address), so on the runner it listens on all interfaces; the
#    runner is ephemeral and has no inbound route. FIX_ENV=local is what the
#    DE-11 guard and the OTP dev channel (e2e) require.
FIX_ENV=local PYTHONPATH="$PWD" nohup uv run python vendor/odoo/odoo-bin \
  -c infra/odoo-conf/local.resolved.conf -d fix_test --db-filter='^fix_test$' \
  --http-interface=0.0.0.0 --http-port=8069 --workers=0 \
  >"$LOGS/odoo.log" 2>&1 &
echo $! >"$LOGS/odoo.pid"
wait_http http://127.0.0.1:8069/web/health "Odoo" "$LOGS/odoo.log"

[ "$PORTALS" = 1 ] || exit 0

# 5. Kong must route to that Odoo before any portal depends on it
#    (kong.yml route odoo-api: /api/odoo/* -> Odoo, prefix stripped).
wait_http http://127.0.0.1:8000/api/odoo/web/health "Kong -> Odoo" "$LOGS/odoo.log" 24

# 6. Portals: production build (`next build --webpack` - the build law) with
#    the gateway base baked in at BUILD time, then `next start` on the port
#    the journeys use (helpers.ts PORTALS; package.json ports are dev ones).
declare -A PORT=(
  [customer]=3010 [corporate]=3001 [analytics]=3012 [seller]=3013
  [brand]=3014 [agent-console]=3015 [partner]=3016 [vendor]=3017
)
for app in "${!PORT[@]}"; do
  echo "::group::portal $app -> :${PORT[$app]}"
  (
    cd "apps/web/$app"
    npm ci --no-audit --no-fund
    NEXT_PUBLIC_FIX_API_BASE=http://127.0.0.1:8000 npm run build
  ) >"$LOGS/build-$app.log" 2>&1 || { tail -n 80 "$LOGS/build-$app.log"; exit 1; }
  (
    cd "apps/web/$app"
    nohup npx next start --port "${PORT[$app]}" --hostname 127.0.0.1 \
      >"../../../$LOGS/portal-$app.log" 2>&1 &
  )
  echo "::endgroup::"
done
for app in "${!PORT[@]}"; do
  wait_http "http://127.0.0.1:${PORT[$app]}/" "portal $app" "$LOGS/portal-$app.log" 24
done
echo "ci-stack-up: OK - Odoo, Kong and ${#PORT[@]} portals up"
