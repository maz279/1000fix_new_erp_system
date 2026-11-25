# ml-gateway (CD-M26-01) — the ML inference gateway.
# Stdlib-only HTTP server (same pattern as services/notification-dispatcher).
# Every response is labelled model_backend=heuristic-v1: no trained model is
# deployed, and the registry carries no invented metrics or lineage ids.
# Build context: services/ml-gateway (libs/py/fix_telemetry is NOT in this
# image, so request spans fall back to no-ops - the server handles ImportError).
FROM python:3.12-slim@sha256:cb33f7f771ecec2ef1225cf39b159591a040391bd73e4c01f00fdfc4c47611d2
WORKDIR /app
COPY src/ /app/
# stdlib only — no pip installs (the L5 discipline)
# DE-11: refuse to start unless FIX_ENV is local, staging or prod/production
# (`prod` = infra/environments.yaml name, `production` an alias), then run the
# real server. ML_GATEWAY_HOST defaults to 0.0.0.0 inside the container.
RUN printf '#!/bin/sh\ncase "$FIX_ENV" in local|staging|prod|production) ;; *) echo "refusing to start: FIX_ENV=$FIX_ENV (DE-11)"; exit 42;; esac\nexec python -u main.py\n' > /entrypoint.sh \
    && chmod +x /entrypoint.sh \
    && useradd --system --uid 10001 --no-create-home mlgateway
ENV PYTHONUNBUFFERED=1
USER 10001
EXPOSE 8090
ENTRYPOINT ["/entrypoint.sh"]
