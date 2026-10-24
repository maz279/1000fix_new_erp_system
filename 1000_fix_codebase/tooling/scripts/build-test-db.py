#!/usr/bin/env python3
"""build-test-db - (re)create the ORM test database used by the `odoo_env` fixture.

Drops and recreates FIX_TEST_DB (default `fix_test`), then installs EVERY
first-party addon (addons/**/cd_*) on it with no demo data via odoo-bin.
This is also the clean-install proof: if any addon is missing a declared
dependency, the install fails here (FF-46 catches the static half).

Connection settings come from infra/odoo-conf/local.resolved.conf - the
GENERATED, .env-resolved conf (`python tooling/scripts/generate-odoo-conf.py`,
REPO-15); PGHOST / PGPORT / PGUSER / PGPASSWORD override (CI). Never targets
fix_dev.

The same clean install also builds the dedicated Wave-1 migration rehearsal
target `fix_migration` (migrations/REHEARSAL.md): `--db fix_migration` or
FIX_TEST_DB=fix_migration. Only `fix_test*` and `fix_migration` are accepted.

After the install, the Bengali back-office language (bn_BD, created by
cd_multi_entity) is loaded for EVERY installed module with
`odoo-bin i18n loadlang -l bn_BD`. The build fails if a module whose
i18n/bn_BD.po translates field labels ends up with none loaded (TR-07/DoD-08).

Usage: python tooling/scripts/build-test-db.py [--db NAME] [--keep]
  (--db: target database, overrides FIX_TEST_DB; --keep: skip if it already exists)
Exit 0 built - 1 install failed - 2 refused/unreachable.
"""

from __future__ import annotations

import configparser
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CONF = ROOT / "infra" / "odoo-conf" / "local.resolved.conf"
TEST_DB = os.environ.get("FIX_TEST_DB", "fix_test")
if "--db" in sys.argv[1:-1]:
    TEST_DB = sys.argv[sys.argv.index("--db") + 1]
# Exact names accepted besides fix_test*: the Wave-1 migration rehearsal target.
EXTRA_DBS = {"fix_migration"}


def settings() -> dict[str, str]:
    conf = configparser.ConfigParser(interpolation=None)
    conf.read(CONF, encoding="utf-8")
    opts = conf["options"] if conf.has_section("options") else {}
    return {
        "host": os.environ.get("PGHOST", opts.get("db_host", "127.0.0.1")),
        "port": os.environ.get("PGPORT", opts.get("db_port", "5432")),
        "user": os.environ.get("PGUSER", opts.get("db_user", "fix")),
        "password": os.environ.get("PGPASSWORD", opts.get("db_password", "")),
    }


def main() -> int:
    if TEST_DB in {"fix_dev", "postgres"} or not (
        TEST_DB.startswith("fix_test") or TEST_DB in EXTRA_DBS
    ):
        print(f"build-test-db: REFUSED - {TEST_DB!r} is not a fix_test* or fix_migration database")
        return 2
    import psycopg2

    s = settings()
    try:
        conn = psycopg2.connect(dbname="postgres", **s)
    except psycopg2.OperationalError as exc:
        print(f"build-test-db: database server unreachable - {exc}")
        return 2
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (TEST_DB,))
        exists = cur.fetchone() is not None
        if exists and "--keep" in sys.argv:
            print(f"build-test-db: {TEST_DB} exists - kept")
            return 0
        if exists:
            cur.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s",
                (TEST_DB,),
            )
            cur.execute(f'DROP DATABASE "{TEST_DB}"')
        cur.execute(f'CREATE DATABASE "{TEST_DB}"')
    conn.close()

    modules = sorted({p.parent.name for p in ROOT.glob("addons/**/__manifest__.py")})
    # TZ=UTC: Odoo's server clock contract (Windows has no time.tzset).
    env = dict(os.environ, PYTHONPATH=str(ROOT), TZ="UTC")
    cmd = [
        sys.executable,
        str(ROOT / "vendor" / "odoo" / "odoo-bin"),
        "-c",
        str(CONF),
        "-d",
        TEST_DB,
        "-i",
        ",".join(modules),
        "--without-demo=True",
        "--stop-after-init",
        "--http-port=8099",
        "--log-level=warn",
        f"--db_host={s['host']}",
        f"--db_port={s['port']}",
        f"--db_user={s['user']}",
    ]
    if s["password"]:
        cmd.append(f"--db_password={s['password']}")
    print(f"build-test-db: installing {len(modules)} first-party addons on {TEST_DB} ...")
    proc = subprocess.run(cmd, cwd=ROOT, env=env, check=False)
    if proc.returncode != 0:
        print(f"build-test-db: FAIL - odoo-bin exit {proc.returncode}")
        return 1
    conn = psycopg2.connect(dbname=TEST_DB, **s)
    with conn.cursor() as cur:
        cur.execute(
            "SELECT name FROM ir_module_module WHERE name = ANY(%s) AND state <> 'installed'",
            (modules,),
        )
        missing = [r[0] for r in cur.fetchall()]
    conn.close()
    if missing:
        print(f"build-test-db: FAIL - not installed: {', '.join(missing)}")
        return 1
    print(f"build-test-db: OK - {len(modules)}/{len(modules)} first-party addons installed")
    return load_bengali(s, env)


# Bengali back office (TR-07 / DoD-08). cd_multi_entity's data creates the
# bn_BD res.lang (Odoo 19 ships only bn_IN). Odoo loads a language's PO files
# for a module when THAT module installs, so the modules installed before
# cd_multi_entity get no bn_BD terms. `odoo-bin i18n loadlang` (the Odoo 19
# CLI; the old --i18n-* server flags are gone) loads bn_BD for every installed
# module. Use the same command on any existing database after
# `-u cd_multi_entity` (docs/guides/bn-terminology-glossary.md section 7).
BN_LANG = "bn_BD"


def load_bengali(s: dict[str, str], env: dict[str, str]) -> int:
    import psycopg2

    env = dict(env, PGHOST=s["host"], PGPORT=str(s["port"]), PGUSER=s["user"])
    if s["password"]:
        env["PGPASSWORD"] = s["password"]
    cmd = [
        sys.executable,
        str(ROOT / "vendor" / "odoo" / "odoo-bin"),
        "i18n",
        "loadlang",
        "-c",
        str(CONF),
        "-d",
        TEST_DB,
        "-l",
        BN_LANG,
    ]
    print(f"build-test-db: loading {BN_LANG} translations for every installed module ...")
    proc = subprocess.run(cmd, cwd=ROOT, env=env, check=False)
    if proc.returncode != 0:
        print(f"build-test-db: FAIL - i18n loadlang {BN_LANG} exit {proc.returncode}")
        return 1
    # every module whose bn_BD.po translates a field label must now render it
    expected = sorted(
        po.parent.parent.name
        for po in ROOT.glob(f"addons/**/i18n/{BN_LANG}.po")
        if "field_description:" in po.read_text(encoding="utf-8")
    )
    conn = psycopg2.connect(dbname=TEST_DB, **s)
    with conn.cursor() as cur:
        cur.execute("SELECT active FROM res_lang WHERE code = %s", (BN_LANG,))
        lang = cur.fetchone()
        cur.execute(
            """
            SELECT DISTINCT d.module
              FROM ir_model_data d JOIN ir_model_fields f ON f.id = d.res_id
             WHERE d.model = 'ir.model.fields' AND d.module = ANY(%s)
               AND f.field_description ? %s
            """,
            (expected, BN_LANG),
        )
        loaded = {r[0] for r in cur.fetchall()}
    conn.close()
    if not (lang and lang[0]):
        print(f"build-test-db: FAIL - language {BN_LANG} missing or inactive")
        return 1
    if unloaded := [m for m in expected if m not in loaded]:
        print(f"build-test-db: FAIL - no {BN_LANG} field labels loaded for: {', '.join(unloaded)}")
        return 1
    print(
        f"build-test-db: OK - {BN_LANG} active; field labels loaded for {len(loaded)}/{len(expected)} modules"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
