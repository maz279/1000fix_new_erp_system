# addons/conftest.py - P07 verification harness.
#
# The module test suites import real model classes
# (from odoo.addons.cd_x.models... import FixX). Importing an Odoo addon
# requires Odoo's module machinery to have initialised its addons path;
# plain pytest cannot do that by itself, so this conftest bootstraps it at
# collection time: configure addons_path, initialise sys.path, then load
# every first-party module IN DEPENDENCY ORDER (cross-addon imports such as
# cd_ap_ext -> cd_tax_engine_bd.models require the dependency to be loaded
# first). No database is needed - model classes are built at import.
from __future__ import annotations

import os
import sys
from pathlib import Path

# Odoo's server clock is UTC by contract: odoo/__init__.py sets TZ=UTC and
# calls time.tzset(). Windows has no time.tzset, and the C runtime has already
# cached the local zone by the time pytest imports odoo - so on the Windows
# workstation (D-WS-001) fields.Datetime.now() returned LOCAL time labelled as
# UTC and date-window tests flipped to "tomorrow" in the evening (R01 re-audit
# 2026-10-22). Re-read TZ in the UCRT, exactly what tzset does on Linux.
os.environ["TZ"] = "UTC"
if sys.platform == "win32":
    import ctypes

    ctypes.CDLL("ucrtbase")._tzset()

CODE_ROOT = Path(__file__).resolve().parents[1]
for p in (str(CODE_ROOT), str(CODE_ROOT / "vendor" / "odoo")):
    if p not in sys.path:
        sys.path.insert(0, p)

# Reuse the canonical addons_path builder (REPO-15: single source). The
# generator file has a hyphenated name, so it is loaded by path.
import importlib.util  # noqa: E402

import odoo  # noqa: E402
from odoo.modules.module import initialize_sys_path, load_openerp_module  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "generate_odoo_conf", CODE_ROOT / "tooling" / "scripts" / "generate-odoo-conf.py"
)
_gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_gen)
build_addons_path = _gen.build_addons_path

odoo.tools.config["addons_path"] = [
    str((CODE_ROOT / part).resolve()) for part in build_addons_path().split(",")
]
initialize_sys_path()


def _load_order():
    """First-party module names in manifest-dependency order."""
    import re

    deps: dict[str, set[str]] = {}
    for mf in CODE_ROOT.glob("addons/**/__manifest__.py"):
        text = mf.read_text(encoding="utf-8", errors="replace")
        found = re.search(r"[\"']depends[\"']\s*:\s*\[(.*?)\]", text, re.S)
        deps[mf.parent.name] = (
            set(re.findall(r"[\"']([A-Za-z0-9_.]+)[\"']", found.group(1))) if found else set()
        )
    order: list[str] = []
    seen: set[str] = set()

    def visit(name: str) -> None:
        if name in seen:
            return
        seen.add(name)
        for dep in sorted(deps.get(name, ())):
            if dep in deps:
                visit(dep)
        order.append(name)

    for name in sorted(deps):
        visit(name)
    return order


_loaded = 0
for _mod in _load_order():
    load_openerp_module(_mod)
    _loaded += 1

# Some collectors/tools address the addons by their bare module name
# (import_module('cd_catalogue')) or under importlib relative path
# ('addons.platform.cd_event_outbox'); without an alias that re-EXECUTES the
# package under a non-odoo.addons name and Odoo's metaclass rejects the
# model classes. Aliasing makes every such import a sys.modules cache hit.
_mod_prefixes: dict[str, str] = {}
for _mf in CODE_ROOT.glob("addons/**/__manifest__.py"):
    _mod_prefixes[_mf.parent.name] = _mf.parent.relative_to(CODE_ROOT).as_posix().replace("/", ".")

for _name in list(sys.modules):
    if _name.startswith("odoo.addons.cd_"):
        _mod_part = _name[len("odoo.addons.") :].split(".", 1)[0]
        _sub = _name[len(f"odoo.addons.{_mod_part}") :]
        _alias = _name[len("odoo.addons.") :]
        sys.modules.setdefault(_alias, sys.modules[_name])
        if _mod_part in _mod_prefixes:
            _rel_alias = f"{_mod_prefixes[_mod_part]}{_sub}"
            sys.modules.setdefault(_rel_alias, sys.modules[_name])
print(f"conftest: {_loaded} first-party odoo modules loaded for test collection")


# ---------------------------------------------------------------------------
# Live ORM fixture (R01 re-audit 2026-10-22, DoD-03 coverage)
#
# The suites above import model classes but never execute ORM methods, so
# model bodies were uncoverable. `odoo_env` gives a test a real
# odoo.api.Environment on a dedicated, cleanly-installed test database
# (default `fix_test`; build it with tooling/scripts/build-test-db.py) inside
# a transaction that is ROLLED BACK after the test - tests never persist data
# and never touch fix_dev.
#
# Connection: infra/odoo-conf/local.resolved.conf (generated, REPO-15) supplies
# db_host/db_port/db_user/db_password; FIX_TEST_DB / PGHOST / PGPORT / PGUSER /
# PGPASSWORD override (CI). An unreachable database SKIPS with the reason - the
# coverage gate then fails loudly, so a skip can never pass the 100% gate.
# ---------------------------------------------------------------------------
import configparser  # noqa: E402
import os  # noqa: E402

import pytest  # noqa: E402

TEST_DB = os.environ.get("FIX_TEST_DB", "fix_test")


def _db_settings() -> dict[str, str]:
    conf = configparser.ConfigParser(interpolation=None)
    conf.read(CODE_ROOT / "infra" / "odoo-conf" / "local.resolved.conf", encoding="utf-8")
    opts = conf["options"] if conf.has_section("options") else {}
    return {
        "db_host": os.environ.get("PGHOST", opts.get("db_host", "127.0.0.1")),
        "db_port": os.environ.get("PGPORT", opts.get("db_port", "5432")),
        "db_user": os.environ.get("PGUSER", opts.get("db_user", "fix")),
        "db_password": os.environ.get("PGPASSWORD", opts.get("db_password", "")),
    }


@pytest.fixture(scope="session")
def odoo_registry():
    """The Odoo registry of the test database, loaded once per session."""
    from odoo.modules.registry import Registry

    for key, value in _db_settings().items():
        odoo.tools.config[key] = int(value) if key == "db_port" else value
    try:
        registry = Registry(TEST_DB)
    except Exception as exc:  # unreachable / uninitialised database
        pytest.skip(f"odoo_env: test database {TEST_DB!r} unavailable ({exc})")
    return registry


@pytest.fixture
def odoo_env(odoo_registry):
    """A superuser Environment whose transaction is rolled back afterwards.

    `cr.commit()` is neutralised for the duration (a test must never persist
    data); code under test that commits keeps working inside the rollback.
    """
    from odoo import SUPERUSER_ID, api

    cr = odoo_registry.cursor()
    cr.commit = lambda: None  # type: ignore[method-assign]
    env = api.Environment(cr, SUPERUSER_ID, {"lang": "en_US", "tz": "Asia/Dhaka"})
    try:
        yield env
    finally:
        _discard_env(env)


# ---------------------------------------------------------------------------
# The statutory chart, as on the live database (A08, 7 Nov 2026).
#
# Live links MD-035 to the Odoo chart, and that switches on its posting rules:
# a line on the bank account needs a branch, VAT a branch and cost centre, TDS a
# cost centre. The test database has no statutory chart, so no ledger test ever
# met those rules: payments were refused on the first real run, and no bill could
# be marked paid, while every test passed. So the suites that post to the ledger
# run on the linked chart, loaded the way production loads it, in the test's own
# rolled-back transaction. A test ABOUT the chart itself opts out with
# @pytest.mark.unlinked_chart.
# ---------------------------------------------------------------------------
LINKED_CHART_SUITES = (
    "/g_finance/",
    "/cd_multi_entity/",
    "/cd_payroll_bd/",
    "/cd_import_order/",
    "/cd_rental_asset/",
)


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "unlinked_chart: this test is about the statutory chart, so it starts without it"
    )


def link_statutory_chart(env):
    """Load and link MD-035 for the company, with the sub-ledger default dimensions."""
    company = env.company
    loader = env["fix.chart.loader"].sudo().create({"company_id": company.id})
    loader.action_load_from_csv()
    loader.action_link_odoo_accounts()
    params = env["ir.config_parameter"].sudo()
    params.set_param("cd_gl_ext.default_branch_code", "HO")
    params.set_param("cd_gl_ext.default_cost_centre", "CORP")
    params.set_param("cd_gl_ext.default_business_line", "SERVICE")


def _head_office_branch(env, company):
    """The default branch, made on first need: a test that sets up its own entity
    for the company must not meet one this harness already created."""
    Branch = env["fix.branch"].sudo()
    branch = Branch.search([("code", "=", "HO"), ("company_id", "=", company.id)], limit=1)
    if branch:
        return branch
    unit = env["operating.unit"].sudo().search([("company_id", "=", company.id)], limit=1)
    if not unit:
        return Branch
    entity = env["fix.entity"].sudo().search([("company_id", "=", company.id)], limit=1)
    if not entity:
        entity = (
            env["fix.entity"]
            .sudo()
            .create(
                {"code": "E%s" % company.id, "legal_name": company.name, "company_id": company.id}
            )
        )
    return Branch.create(
        {
            "code": "HO",
            "name": "Test Head Office",
            "entity_id": entity.id,
            "operating_unit_id": unit.id,
        }
    )


@pytest.fixture(autouse=True)
def _statutory_chart_as_on_live(request):
    path = Path(str(request.node.path)).as_posix()
    if (
        not any(suite in path for suite in LINKED_CHART_SUITES)
        or "odoo_env" not in request.fixturenames
        or request.node.get_closest_marker("unlinked_chart")
    ):
        return
    env = request.getfixturevalue("odoo_env")
    link_statutory_chart(env)

    # Many finance tests build a private company. Its accounts carry the real chart
    # codes, so they get the rules those codes carry on live: otherwise those tests
    # would pass without ever meeting MD-035, which is the gap this closes.
    from odoo.addons.cd_gl_ext.models import fix_chart_loader, fix_gl_ext

    home = env.company.id
    chart_map = fix_gl_ext._chart_map_for_company
    default_dimension = fix_gl_ext._default_dimension

    def linked_chart_map(env_, company_id):
        found = chart_map(env_, company_id)
        if found or company_id == home:
            return found
        rows = {
            row.account_code: row
            for row in env_["fix.chart.account"]
            .sudo()
            .with_context(active_test=False)
            .search([("company_id", "=", home)])
        }
        accounts = (
            env_["account.account"]
            .sudo()
            .with_company(company_id)
            .search(
                [
                    ("company_ids", "in", company_id),
                    ("code", "in", list(fix_chart_loader.ODOO_CHART_MAPPING)),
                ]
            )
        )
        for account in accounts:
            row = rows.get(fix_chart_loader.ODOO_CHART_MAPPING[account.code])
            if row:
                found[account.id] = row
        return found

    def linked_default_dimension(env_, company, dimension):
        value = default_dimension(env_, company, dimension)
        # the test company has no head office yet, but only if one is configured at all:
        # with no default the COA-03 refusal must stand, and a test says so
        code = env_["ir.config_parameter"].sudo().get_param("cd_gl_ext.default_branch_code")
        if dimension == "branch" and not value and code:
            return _head_office_branch(env_, company).id or False
        return value

    monkeypatch = request.getfixturevalue("monkeypatch")
    monkeypatch.setattr(fix_gl_ext, "_chart_map_for_company", linked_chart_map)
    monkeypatch.setattr(fix_gl_ext, "_default_dimension", linked_default_dimension)


def _discard_env(env) -> None:
    """Roll back and close a test transaction, whatever the test left pending.

    Pending writes are discarded, never flushed: a test that left an invalid
    pending write made the flushing invalidate_all() raise and skip the
    rollback, leaking an open transaction whose row locks stalled every other
    live-ORM run on fix_test (R01 re-audit 2026-10-22). The rollback and the
    close happen whatever fails, and the registry caches are cleared last so
    no `ormcache` entry survives the transaction that filled it.
    """
    cr = env.cr
    registry = env.registry
    try:
        env.invalidate_all(flush=False)
    finally:
        try:
            cr.rollback()
        finally:
            try:
                cr.close()
            finally:
                # Registry `ormcache` entries outlive the cursor, so a rolled-back
                # test could still poison every later test in the process. The
                # harness neutralises `cr.commit`, which is also what normally
                # signals cache invalidation, so nothing cleared them: a fixture
                # that linked its private company to the superuser left that
                # company's id in `res.users._get_company_ids` (ormcached on
                # `self.id`), and the next suite resolved `env.companies` to a
                # company the rollback had already removed — MissingError on
                # res.company in an unrelated module, only when the suites ran
                # together. Odoo's own TransactionCase clears the caches on every
                # test cleanup (odoo/tests/common.py); this does the same.
                registry.clear_all_caches()
