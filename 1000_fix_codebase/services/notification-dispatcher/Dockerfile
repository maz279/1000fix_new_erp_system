# Notification dispatcher — P04-M05 (M27 / CD-M27-nn).
# Stdlib-only service: no pip dependencies, nothing to pin beyond the base.
# Build context: REPOSITORY ROOT (needs libs/py/fix_telemetry for the NFR-092
# request spans; compose sets the context).
# DE-06: digest placeholder resolved at first pull by tooling/scripts/resolve-digests.ps1.
FROM python:3.12.10-slim@sha256:fd95fa221297a88e1cf49c55ec1828edd7c5a428187e67b5d1805692d11588db
# DE-11: refuse to start unless FIX_ENV is local, staging or prod/production.
# `prod` (the infra/environments.yaml name) is normalised to `production`
# because src/channels.py switches to its production rules (https-only
# gateways + SSRF guard) ONLY on the literal FIX_ENV=production; any other
# value jails every gateway to the local allowlist (fail closed).
# Credentials enter only via environment variables at runtime
# (FIX_SMS_GATEWAY_TOKEN etc.) — never baked into the image.
# FIX_NOTIFICATION_DISPATCHER_HOST=0.0.0.0 is the in-container bind (src/main.py
# defaults to loopback when unset); the port is reachable only through the
# compose network / cluster Service.
ENV FIX_ENV=local PYTHONUNBUFFERED=1 FIX_NOTIFICATION_DISPATCHER_HOST=0.0.0.0
WORKDIR /srv/dispatcher
COPY libs/__init__.py libs/__init__.py
COPY libs/py/__init__.py libs/py/__init__.py
COPY libs/py/fix_telemetry/ libs/py/fix_telemetry/
COPY services/notification-dispatcher/src/ ./src/
COPY services/notification-dispatcher/templates/ ./templates/
RUN printf '#!/bin/sh\ncase "$FIX_ENV" in local|staging|production) ;; prod) export FIX_ENV=production;; *) echo "refusing to start: FIX_ENV=$FIX_ENV (DE-11)"; exit 42;; esac\nexec python -m src.main\n' > /entrypoint.sh \
    && chmod +x /entrypoint.sh \
    && useradd --system --uid 10001 --no-create-home dispatcher
USER 10001
# No ports EXPOSEd on the send path: events arrive via fix_events.consume.
# 8110 serves operations endpoints (health/kpis/dlq/fallbacks).
EXPOSE 8110
ENTRYPOINT ["/entrypoint.sh"]
