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
  2. Known endpoint variables (DB/S3/SMTP/Redis/residency/Keycloak/OTLP) must
     point at loopback or the compose service names - never at a routable host.
  3. URL-valued variables must use one of their declared schemes and name a
     host; host-valued variables must be a bare host (or a local socket path),
     never a URL - a pasted "postgres://prod-db..." must not slip through.
"""

from __future__ import annotations

import os
import sys
from urllib.parse import urlsplit

ALLOWED_HOSTS = {
    "127.0.0.1",
    "localhost",
    "::1",
    # compose service names (resolvable only inside the local compose network)
    "postgres",
    "redis",
    "object-store",
    "mailpit",
    "keycloak",
    "pgbouncer",
    "kong",
    "airflow",
    "novu",
    "residency-stub",
}

#: variable -> allowed URL schemes, or None for a variable that holds a bare host.
ENDPOINT_VARS: dict[str, tuple[str, ...] | None] = {
    "PGHOST": None,
    "DB_HOST": None,
    "DATABASE_URL": ("postgres", "postgresql"),
    "S3_ENDPOINT": ("http", "https"),
    "SMTP_HOST": None,
    "REDIS_URL": ("redis", "rediss"),
    "RESIDENCY_BASE": ("http", "https"),
    "KEYCLOAK_URL": ("http", "https"),
    "OTEL_EXPORTER_OTLP_ENDPOINT": ("http", "https"),
}


def _host_of(value: str) -> str:
    """Host part of a bare ``[user@]host[:port][/path]`` value (IPv6 literal aware)."""
    v = value.strip()
    if "@" in v:
        v = v.rsplit("@", 1)[1]
    v = v.split("/", 1)[0]
    if v.startswith("["):  # [::1]:5432
        return v[1:].split("]", 1)[0].lower()
    if v.count(":") > 1:  # bare IPv6 literal, e.g. ::1
        return v.lower()
    return v.split(":", 1)[0].lower()


def endpoint_violation(var: str, value: str, schemes: tuple[str, ...] | None) -> str | None:
    """Why ``var=value`` would let a local process reach a non-local endpoint, else None."""
    v = value.strip()
    if schemes is None:
        if "://" in v:
            return f"{var} must be a bare host, not a URL ({v.split('://', 1)[0]}://...)"
        if v.startswith("/"):  # libpq/SMTP unix-socket directory: local by construction
            return None
        host = _host_of(v)
    else:
        try:
            parts = urlsplit(v)
        except ValueError as exc:  # e.g. an unterminated "[::1" IPv6 literal
            return f"{var} is not a valid URL: {exc}"
        if parts.scheme not in schemes:  # urlsplit lower-cases the scheme
            return (
                f"{var} must be a {'/'.join(schemes)} URL "
                f"(got scheme {parts.scheme or '<none>'!r})"
            )
        host = parts.hostname or ""  # credentials/port/path stripped, lower-cased
    if not host:
        return f"{var} names no host"
    if host not in ALLOWED_HOSTS:
        return f"{var} points at {host!r} - a local process must not reach a non-local endpoint"
    return None


def assert_local() -> None:
    env = os.environ.get("FIX_ENV", "")
    if env != "local":
        print(f"DE-11: refusing to start: FIX_ENV={env!r} (must be 'local')", file=sys.stderr)
        sys.exit(42)
    for var, schemes in ENDPOINT_VARS.items():
        value = os.environ.get(var)
        if not value or not value.strip():
            continue
        reason = endpoint_violation(var, value, schemes)
        if reason:
            print(
                f"DE-11: refusing to start: {reason}. Fix the .env and restart.",
                file=sys.stderr,
            )
            sys.exit(42)


if __name__ == "__main__":
    assert_local()
    print("fix_env_guard: FIX_ENV=local, all endpoints loopback - OK")
