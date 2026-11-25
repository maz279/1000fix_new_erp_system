"""DE-11 environment guard - behavioural suite (P02-M06-T06).

R01-AUDIT regression: the allowed URL schemes in ENDPOINT_VARS were declared
but never enforced, and the host was found by naive string splitting. A pasted
``DB_HOST=postgres://prod-db...`` (host parsed as the compose name "postgres"),
a scheme-relative ``//prod`` (empty host) or ``http://prod#@localhost`` (host
taken after the "@") all passed. These tests pin the enforced behaviour.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from libs.py.fix_env_guard import (
    ALLOWED_HOSTS,
    ENDPOINT_VARS,
    _host_of,
    assert_local,
    endpoint_violation,
)

URL_VARS = sorted(v for v, s in ENDPOINT_VARS.items() if s)
HOST_VARS = sorted(v for v, s in ENDPOINT_VARS.items() if s is None)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    monkeypatch.delenv("FIX_ENV", raising=False)
    for var in ENDPOINT_VARS:
        monkeypatch.delenv(var, raising=False)
    return monkeypatch


def _refused(capsys) -> str:
    with pytest.raises(SystemExit) as exc:
        assert_local()
    assert exc.value.code == 42
    err = capsys.readouterr().err
    assert err.startswith("DE-11: refusing to start:")
    return err


# --------------------------------------------------------------------------- FIX_ENV


@pytest.mark.parametrize("env", [None, "", "staging", "production", "Local", " local"])
def test_non_local_fix_env_refuses_to_start(clean_env, capsys, env):
    if env is not None:
        clean_env.setenv("FIX_ENV", env)
    err = _refused(capsys)
    assert f"FIX_ENV={env or ''!r} (must be 'local')" in err


def test_local_with_no_endpoints_configured_starts(clean_env, capsys):
    clean_env.setenv("FIX_ENV", "local")
    assert assert_local() is None
    assert capsys.readouterr().err == ""


def test_shipped_env_example_passes_the_guard(clean_env, capsys):
    """The onboarding .env.example must itself satisfy DE-11."""
    example = ROOT / ".env.example"
    seen = []
    for line in example.read_text(encoding="utf-8").splitlines():
        key, sep, value = line.partition("=")
        if sep and key.strip() in ENDPOINT_VARS:
            clean_env.setenv(key.strip(), value.strip())
            seen.append(key.strip())
    clean_env.setenv("FIX_ENV", "local")
    assert {"PGHOST", "S3_ENDPOINT", "REDIS_URL", "KEYCLOAK_URL"} <= set(seen)
    assert_local()
    assert capsys.readouterr().err == ""


# --------------------------------------------------------------------------- allowed values


@pytest.mark.parametrize(
    ("var", "value"),
    [
        ("PGHOST", "127.0.0.1"),
        ("PGHOST", "postgres"),
        ("PGHOST", "LOCALHOST"),
        ("PGHOST", "::1"),
        ("DB_HOST", "[::1]:5433"),
        ("DB_HOST", "pgbouncer:6432"),
        ("DB_HOST", "fix@localhost"),
        ("DB_HOST", "localhost/fix_dev"),
        ("PGHOST", "/var/run/postgresql"),  # unix-socket directory
        ("SMTP_HOST", "mailpit"),
        ("S3_ENDPOINT", "http://object-store:9000"),
        ("S3_ENDPOINT", "  http://127.0.0.1:9002  "),
        ("REDIS_URL", "redis://localhost:6380/0"),
        ("REDIS_URL", "rediss://:pw@redis:6379"),
        ("DATABASE_URL", "postgresql://fix:pw@localhost:5433/fix_dev"),
        ("DATABASE_URL", "postgres://pgbouncer/fix"),
        ("RESIDENCY_BASE", "http://residency-stub:8100/v1"),
        ("KEYCLOAK_URL", "HTTPS://KEYCLOAK:8443/realms/1000fix-dev"),
        ("OTEL_EXPORTER_OTLP_ENDPOINT", "http://[::1]:4318"),
    ],
)
def test_local_endpoints_are_accepted(clean_env, capsys, var, value):
    assert endpoint_violation(var, value, ENDPOINT_VARS[var]) is None
    clean_env.setenv("FIX_ENV", "local")
    clean_env.setenv(var, value)
    assert_local()
    assert capsys.readouterr().err == ""


def test_whitespace_only_value_is_treated_as_unset(clean_env, capsys):
    clean_env.setenv("FIX_ENV", "local")
    clean_env.setenv("KEYCLOAK_URL", "   ")
    assert_local()
    assert capsys.readouterr().err == ""


# --------------------------------------------------------------------------- refusals


@pytest.mark.parametrize(
    ("var", "value", "reason"),
    [
        # routable hosts
        ("PGHOST", "db.prod.1000fix.com", "points at 'db.prod.1000fix.com'"),
        ("SMTP_HOST", "smtp.sendgrid.net:587", "points at 'smtp.sendgrid.net'"),
        ("PGHOST", "localhost,db.prod.1000fix.com", "points at"),  # libpq multi-host
        ("S3_ENDPOINT", "https://s3.ap-southeast-1.amazonaws.com", "points at"),
        ("REDIS_URL", "redis://cache.prod.1000fix.com:6379/0", "points at"),
        ("DATABASE_URL", "postgresql://fix:pw@db.prod.1000fix.com/fix", "points at"),
        # scheme enforcement (the R01-AUDIT defect)
        ("S3_ENDPOINT", "redis://s3.amazonaws.com", "must be a http/https URL"),
        ("S3_ENDPOINT", "ftp://127.0.0.1", "got scheme 'ftp'"),
        ("REDIS_URL", "http://localhost:6379", "must be a redis/rediss URL"),
        ("DATABASE_URL", "mysql://localhost/fix", "must be a postgres/postgresql URL"),
        ("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4318", "must be a http/https URL"),
        ("KEYCLOAK_URL", "//auth.1000fix.com/realms", "got scheme '<none>'"),
        ("DB_HOST", "postgres://prod-db.example.com:5432/fix", "must be a bare host, not a URL"),
        ("PGHOST", "redis://localhost", "must be a bare host"),
        # host must exist / be parsed correctly
        ("RESIDENCY_BASE", "http://", "names no host"),
        ("PGHOST", ":5432", "names no host"),
        ("KEYCLOAK_URL", "http://auth.prod.example#@localhost", "points at 'auth.prod.example'"),
        ("S3_ENDPOINT", "http://prod.example.com/?next=@localhost", "points at 'prod.example.com'"),
        ("S3_ENDPOINT", "http://localhost@evil.example.com", "points at 'evil.example.com'"),
        ("KEYCLOAK_URL", "http://[::1", "is not a valid URL"),
    ],
)
def test_non_local_or_malformed_endpoints_are_refused(clean_env, capsys, var, value, reason):
    assert reason in endpoint_violation(var, value, ENDPOINT_VARS[var])
    clean_env.setenv("FIX_ENV", "local")
    clean_env.setenv(var, value)
    err = _refused(capsys)
    assert var in err
    assert reason in err
    assert err.rstrip().endswith("Fix the .env and restart.")


def test_first_violation_stops_startup_even_when_others_are_fine(clean_env, capsys):
    clean_env.setenv("FIX_ENV", "local")
    clean_env.setenv("PGHOST", "127.0.0.1")
    clean_env.setenv("S3_ENDPOINT", "https://bucket.prod.example")
    clean_env.setenv("KEYCLOAK_URL", "http://keycloak:8080")
    err = _refused(capsys)
    assert "S3_ENDPOINT" in err and "PGHOST" not in err


def test_fix_env_is_checked_before_any_endpoint(clean_env, capsys):
    clean_env.setenv("FIX_ENV", "staging")
    clean_env.setenv("PGHOST", "db.prod.example")
    err = _refused(capsys)
    assert "FIX_ENV='staging'" in err and "PGHOST" not in err


# --------------------------------------------------------------------------- declarations


def test_every_url_variable_declares_schemes_and_host_variables_none():
    assert set(URL_VARS) == {
        "DATABASE_URL",
        "S3_ENDPOINT",
        "REDIS_URL",
        "RESIDENCY_BASE",
        "KEYCLOAK_URL",
        "OTEL_EXPORTER_OTLP_ENDPOINT",
    }
    assert set(HOST_VARS) == {"PGHOST", "DB_HOST", "SMTP_HOST"}
    for var in URL_VARS:
        assert all(s == s.lower() and "://" not in s for s in ENDPOINT_VARS[var])


def test_allowed_hosts_are_loopback_or_compose_names_only():
    assert {"127.0.0.1", "localhost", "::1"} <= ALLOWED_HOSTS
    assert all("." not in h or h == "127.0.0.1" for h in ALLOWED_HOSTS)


@pytest.mark.parametrize(
    ("value", "host"),
    [
        ("LocalHost", "localhost"),
        ("u:p@redis:6379", "redis"),
        ("[::1]:5432", "::1"),
        ("::1", "::1"),
        ("postgres/db", "postgres"),
        ("  mailpit  ", "mailpit"),
    ],
)
def test_host_of_bare_values(value, host):
    assert _host_of(value) == host
