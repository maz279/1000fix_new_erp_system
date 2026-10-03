"""DE-11 environment guard - P02-M06-T06.

Every service asserts FIX_ENV=local at startup and REFUSES to start if a
non-local endpoint is configured alongside it. "A local process must not be
able to reach a production database because someone pasted a connection
string."

Usage (first import in any service entrypoint):

    from fix_env_guard import assert_local
    assert_local()          # raises SystemExit(42) on violation

Rules enforced:
  1. FIX_ENV must exist and be exactly "local".
  2. Known endpoint variables (DB/S3/SMTP/residency/Keycloak) must point at
     loopback or the compose service names - never at a routable host.
"""
from __future__ import annotations

import os
import sys

ALLOWED_HOSTS = {
    "127.0.0.1", "localhost", "::1",
    # compose service names (resolvable only inside the local compose network)
    "postgres", "redis", "object-store", "mailpit", "keycloak",
    "pgbouncer", "kong", "airflow", "novu", "residency-stub",
}

ENDPOINT_VARS = {
    "PGHOST": None, "DB_HOST": None, "S3_ENDPOINT": ("http", "https"),
    "SMTP_HOST": None, "RESIDENCY_BASE": ("http", "https"),
    "KEYCLOAK_URL": ("http", "https"), "OTEL_EXPORTER_OTLP_ENDPOINT": ("http", "https"),
}


def _host_of(value: str) -> str:
    v = value.strip()
    for scheme in ("http://", "https://"):
        if v.startswith(scheme):
            v = v[len(scheme):]
    # strip credentials, port, path
    if "@" in v:
        v = v.split("@", 1)[1]
    return v.split("/", 1)[0].split(":", 1)[0].lower()


def assert_local() -> None:
    env = os.environ.get("FIX_ENV", "")
    if env != "local":
        print(f"DE-11: refusing to start: FIX_ENV={env!r} (must be 'local')", file=sys.stderr)
        sys.exit(42)
    for var, schemes in ENDPOINT_VARS.items():
        value = os.environ.get(var)
        if not value:
            continue
        host = _host_of(value)
        if host and host not in ALLOWED_HOSTS:
            print(
                f"DE-11: refusing to start: {var} points at {host!r} - a local process "
                f"must not reach a non-local endpoint. Fix the .env and restart.",
                file=sys.stderr,
            )
            sys.exit(42)


if __name__ == "__main__":
    assert_local()
    print("fix_env_guard: FIX_ENV=local, all endpoints loopback - OK")
