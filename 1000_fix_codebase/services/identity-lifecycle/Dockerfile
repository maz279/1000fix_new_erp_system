# build-context: repo-root
# identity-lifecycle — M29 leaver deprovisioning (employee.left -> Keycloak, KPI-090).
# Built from the REPOSITORY ROOT (it needs libs/py/fix_events + fix_env_guard - FF-28,
# DE-11); Dockerfile.dockerignore next to this file limits the context to exactly those.
# One pip dependency: kafka-python-ng (libs/py/fix_events real transport), pinned = uv.lock.
# DE-06: base pinned by digest (same base as the other L5 services).
FROM python:3.12.10-slim@sha256:fd95fa221297a88e1cf49c55ec1828edd7c5a428187e67b5d1805692d11588db
# DE-11: the image entrypoint refuses to start unless FIX_ENV is local, staging or
# prod/production (`prod` is the infra/environments.yaml name, `production` an alias).
# The service itself ALSO checks FIX_ENV (identity_lifecycle_service.check_environment:
# local, staging, prod, production); outside local its ops endpoints need
# IDENTITY_LIFECYCLE_TOKEN.
# A local process still asserts it never reaches a non-local Keycloak.
# Credentials only via env at runtime.
# IDENTITY_LIFECYCLE_HOST=0.0.0.0 is the in-container bind; the port is reachable only
# through the compose network / cluster Service, never published to the edge.
ENV FIX_ENV=local PYTHONUNBUFFERED=1 FIX_REPO_ROOT=/srv/app IDENTITY_LIFECYCLE_HOST=0.0.0.0
WORKDIR /srv/app
RUN pip install --no-cache-dir kafka-python-ng==2.2.3
COPY libs/__init__.py libs/__init__.py
COPY libs/py/__init__.py libs/py/__init__.py
COPY libs/py/fix_events/ libs/py/fix_events/
COPY libs/py/fix_env_guard/ libs/py/fix_env_guard/
COPY libs/py/fix_telemetry/ libs/py/fix_telemetry/
COPY services/identity-lifecycle/src/ services/identity-lifecycle/src/
RUN printf '#!/bin/sh\ncase "$FIX_ENV" in local|staging|prod|production) ;; *) echo "refusing to start: FIX_ENV=$FIX_ENV (DE-11)"; exit 42;; esac\nexec python /srv/app/services/identity-lifecycle/src/identity_lifecycle_service.py "$@"\n' > /entrypoint.sh \
    && chmod +x /entrypoint.sh \
    && useradd --system --uid 10001 --home-dir /var/lib/identity-lifecycle identity \
    && mkdir -p /var/lib/identity-lifecycle \
    && chown identity /var/lib/identity-lifecycle
USER 10001
# 8120 serves operations endpoints only (health/outcomes/drain); events arrive via fix_events.
EXPOSE 8120
ENTRYPOINT ["/entrypoint.sh"]
