# rmm-collector (CD-M05-04 companion) — the deployment runbook
# for the L5 telemetry service. It runs WHERE its agents are, not
# necessarily in compose; this Dockerfile is the container path.
#
# Target: the Odoo origin it pushes to is FIX_RMM_ODOO_URL (validated:
# origin only, no credentials, https unless loopback / an internal service
# name such as http://odoo:8069); unset = the local Odoo (127.0.0.1:8069).
# NOTE: `python -m rmm_collector` is the evaluation library + push client
# entry point - it prints its usage and exits; it is not a long-running
# daemon, so it is not part of the always-on production stack.
FROM python:3.12-slim@sha256:cb33f7f771ecec2ef1225cf39b159591a040391bd73e4c01f00fdfc4c47611d2
WORKDIR /app
COPY src/ /app/
# stdlib only — no pip installs (the L5 discipline)
# DE-11: refuse to start unless FIX_ENV is local, staging or prod/production.
RUN printf '#!/bin/sh\ncase "$FIX_ENV" in local|staging|prod|production) ;; *) echo "refusing to start: FIX_ENV=$FIX_ENV (DE-11)"; exit 42;; esac\nexec "$@"\n' > /entrypoint.sh \
    && chmod +x /entrypoint.sh \
    && useradd --system --uid 10001 --no-create-home rmm
ENV PYTHONUNBUFFERED=1
USER 10001
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-u", "-m", "rmm_collector"]
