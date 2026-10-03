# Notification dispatcher — P04-M05 (M27 / CD-M27-nn).
# Stdlib-only service: no pip dependencies, nothing to pin beyond the base.
# DE-06: digest placeholder resolved at first pull by tooling/scripts/resolve-digests.ps1.
FROM python:3.12.10-slim@sha256:fd95fa221297a88e1cf49c55ec1828edd7c5a428187e67b5d1805692d11588db
# DE-11: refuse to start outside local/dev environments (same guard as the
# residency stub). Credentials enter only via environment variables at
# runtime (FIX_SMS_GATEWAY_TOKEN etc.) — never baked into the image.
ENV FIX_ENV=local PYTHONUNBUFFERED=1
WORKDIR /srv/dispatcher
COPY src/ ./src/
COPY templates/ ./templates/
RUN printf '#!/bin/sh\n[ "$FIX_ENV" = "local" ] || [ "$FIX_ENV" = "staging" ] || { echo "refusing to start: FIX_ENV=$FIX_ENV (DE-11)"; exit 42; }\nexec python -m src.main\n' > /entrypoint.sh && chmod +x /entrypoint.sh
# No ports EXPOSEd on the send path: events arrive via fix_events.consume.
# 8110 serves operations endpoints (health/kpis/dlq/fallbacks).
EXPOSE 8110
ENTRYPOINT ["/entrypoint.sh"]
