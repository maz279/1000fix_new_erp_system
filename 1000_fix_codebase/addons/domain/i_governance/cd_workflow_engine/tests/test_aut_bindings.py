"""A11 fix B1 — the automation register's bindings are real, verified at
runtime, and enforced.

Every test runs inside the `odoo_env` transaction and is rolled back. The
catalogue is reloaded where a test needs the full 60 rows; sabotage is
written through the catalogue path (`_catalogue_write`) because the public
write guard would (rightly) refuse it — the negative path is tested too.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from odoo.exceptions import UserError

MODULE = Path(__file__).resolve().parents[1]
MIGRATION = MODULE / "migrations" / "19.0.1.2.0" / "post-migrate.py"

ENGINES = {"odoo_cron", "odoo_method", "event_consumer", "manual"}
IMPLEMENTATIONS = {"full", "partial", "none"}


def load_catalogue(env):
    automations = env["fix.automation"].with_context(active_test=False)
    automations.search([]).unlink()
    assert automations.action_load_register() == 60
    return automations.search([])


def by_code(env, code):
    return (
        env["fix.automation"].with_context(active_test=False).search([("code", "=", code)], limit=1)
    )


# ---------------------------------------------------------------- catalogue
def test_catalogue_is_the_honest_taxonomy(odoo_env):
    """The three retired values are gone; every row names a real mechanism and
    a verdict, and implementation 'none' is always the manual engine."""
    rows = load_catalogue(odoo_env)
    assert len(rows) == 60
    assert {r.engine for r in rows} <= ENGINES
    assert {r.implementation for r in rows} <= IMPLEMENTATIONS
    published = {r.engine for r in rows}
    assert published == ENGINES
    for row in rows:
        assert row.executor_note, "%s has no executor note" % row.code
        if row.implementation == "none":
            assert row.engine == "manual" and not row.engine_ref, row.code
            assert not row.active, "%s is unimplemented yet active" % row.code
        else:
            assert row.engine != "manual", row.code
            assert row.engine_ref, row.code
            assert row.active, row.code


def test_every_claimed_binding_resolves_on_this_database(odoo_env):
    """The P0 acceptance: 0 of 60 resolved before; every row that claims an
    implementation must resolve here, and the gap report must be empty."""
    rows = load_catalogue(odoo_env)
    claimed = rows.filtered(lambda r: r.implementation != "none")
    unresolved = [(r.code, r.engine_ref) for r in claimed if r.binding_state != "verified"]
    assert unresolved == []
    # ... and the manual rows are manual, not silently "verified"
    manual = rows.filtered(lambda r: r.implementation == "none")
    assert {r.binding_state for r in manual} == {"manual"}
    assert odoo_env["fix.automation"].action_report_engine_gap() == []
    broken = rows.filtered(lambda r: r.coverage_state == "broken")
    assert not broken
    assert {r.coverage_state for r in rows} == {"implemented", "partial", "planned"}


def test_binding_state_flags_an_inactive_executor(odoo_env):
    """Binding verified is not the same as executor running: a switched-off
    cron is still a verified reference, and executor_active says so."""
    rows = load_catalogue(odoo_env)
    row = rows.filtered(lambda r: r.engine == "odoo_cron")[0]
    cron = odoo_env.ref(row.engine_ref[len("cron:") :])
    cron.active = False
    assert row.binding_state == "verified"
    assert row.executor_active is False


# ------------------------------------------------------------- gap report
def test_gap_report_finds_a_sabotaged_reference(odoo_env):
    """The reporter RESOLVES the reference; it does not string-match. A wrong
    xmlid on an active row is reported as broken."""
    load_catalogue(odoo_env)
    row = by_code(odoo_env, "AUT-001")
    assert row.engine == "odoo_method"
    row._catalogue_write({"engine_ref": "method:fix.service.order.no_such_method"})
    assert row.binding_state == "unresolved"
    assert row.coverage_state == "broken"
    report = odoo_env["fix.automation"].action_report_engine_gap()
    assert [r["code"] for r in report] == ["AUT-001"]
    assert report[0]["coverage_state"] == "broken"


def test_gap_report_finds_a_reactivated_planned_row(odoo_env):
    load_catalogue(odoo_env)
    row = by_code(odoo_env, "AUT-003")
    assert row.implementation == "none" and not row.active
    row._catalogue_write({"active": True})
    report = odoo_env["fix.automation"].action_report_engine_gap()
    assert [r["code"] for r in report] == ["AUT-003"]
    assert report[0]["coverage_state"] == "planned"


def test_gap_report_finds_a_cron_that_left_the_registry(odoo_env):
    load_catalogue(odoo_env)
    row = by_code(odoo_env, "AUT-006")  # a model method
    assert row.binding_state == "verified"
    row._catalogue_write({"engine": "odoo_cron", "engine_ref": "cron:base.no_such_cron"})
    assert row.binding_state == "unresolved"
    assert [r["code"] for r in odoo_env["fix.automation"].action_report_engine_gap()] == ["AUT-006"]


# -------------------------------------------------------------- write guard
def test_write_guard_refuses_an_unresolvable_reference(odoo_env):
    Automations = odoo_env["fix.automation"].with_context(active_test=False)
    Automations.search([]).unlink()
    with pytest.raises(UserError, match=r"AUT-910 .*does not resolve"), odoo_env.cr.savepoint():
        Automations.create(
            {
                "code": "AUT-910",
                "trigger": "Something happens",
                "action": "Something runs",
                "engine": "odoo_method",
                "engine_ref": "method:no.such.model.run",
                "implementation": "full",
            }
        )
    # an inactive row may still be prepared before its executor exists
    draft = Automations.create(
        {
            "code": "AUT-910",
            "trigger": "Something happens",
            "action": "Something runs",
            "engine": "odoo_method",
            "engine_ref": "method:no.such.model.run",
            "implementation": "full",
            "active": False,
        }
    )
    with pytest.raises(UserError, match="does not resolve"), odoo_env.cr.savepoint():
        draft.write({"active": True})


def test_write_guard_refuses_manual_with_an_implementation(odoo_env):
    Automations = odoo_env["fix.automation"].with_context(active_test=False)
    Automations.search([]).unlink()
    with pytest.raises(UserError, match="engine 'manual' cannot carry"), odoo_env.cr.savepoint():
        Automations.create(
            {
                "code": "AUT-911",
                "trigger": "Something happens",
                "action": "Someone does it",
                "engine": "manual",
                "implementation": "partial",
            }
        )
    row = Automations.create(
        {
            "code": "AUT-911",
            "trigger": "Something happens",
            "action": "Someone does it",
            "engine": "manual",
            "implementation": "none",
        }
    )
    with (
        pytest.raises(UserError, match="cannot carry implementation 'full'"),
        odoo_env.cr.savepoint(),
    ):
        row.write({"implementation": "full"})


def test_write_guard_accepts_a_verified_reference(odoo_env):
    Automations = odoo_env["fix.automation"].with_context(active_test=False)
    Automations.search([]).unlink()
    row = Automations.create(
        {
            "code": "AUT-912",
            "trigger": "Same device within 30 days",
            "action": "Flag rework",
            "engine": "odoo_method",
            "engine_ref": "method:fix.service.order._flag_rework",
            "implementation": "full",
        }
    )
    assert row.binding_state == "verified" and row.coverage_state == "implemented"
    row.write({"active": False})
    assert row.binding_state == "verified"


# ------------------------------------------------------------------ loader
def test_loader_is_idempotent_and_refreshes_stale_bindings(odoo_env):
    rows = load_catalogue(odoo_env)
    snapshot = {
        r.code: (
            r.engine,
            r.engine_ref,
            r.implementation,
            r.executor_note,
            r.active,
            r.failure_policy,
        )
        for r in rows
    }
    assert odoo_env["fix.automation"].action_load_register() == 0
    after = {
        r.code: (
            r.engine,
            r.engine_ref,
            r.implementation,
            r.executor_note,
            r.active,
            r.failure_policy,
        )
        for r in odoo_env["fix.automation"].with_context(active_test=False).search([])
    }
    assert after == snapshot, "a second load changed the register"

    stale = by_code(odoo_env, "AUT-002")
    stale._catalogue_write({"engine": "manual", "engine_ref": False, "implementation": "none"})
    odoo_env["fix.automation"].action_load_register()
    fresh = by_code(odoo_env, "AUT-002")
    assert fresh.engine == "odoo_method"
    assert fresh.engine_ref == "method:fix.field.order.action_suggest_technicians"
    assert fresh.implementation == "partial"


def test_loader_never_overwrites_the_business_words(odoo_env):
    load_catalogue(odoo_env)
    row = by_code(odoo_env, "AUT-010")
    row._catalogue_write({"trigger": "Our own trigger wording", "action": "Our own action wording"})
    odoo_env["fix.automation"].action_load_register()
    assert row.trigger == "Our own trigger wording"
    assert row.action == "Our own action wording"


def test_loader_publishes_honest_counts(odoo_env):
    import json

    load_catalogue(odoo_env)
    events = odoo_env["fix.event.outbox"].search(
        [("event_type", "=", "automation.register.loaded")], order="id desc", limit=1
    )
    payload = json.loads(events.payload)
    assert payload == {
        "loaded": 60,
        "refreshed": 0,
        # the 52 rows that claim an implementation resolve; the 8 manual rows
        # are honestly 'manual', neither verified nor unresolved
        "verified": 52,
        "unresolved": 0,
        "total": 60,
    }


# --------------------------------------------------------------- consumer
def test_register_loaded_consumer_raises_one_todo_per_broken_row(odoo_env):
    load_catalogue(odoo_env)
    broken = by_code(odoo_env, "AUT-001")
    broken._catalogue_write({"engine_ref": "method:fix.service.order.no_such_method"})
    result = odoo_env["fix.automation"].consume_register_loaded(
        {"event_id": "evt-b1-consumer-1", "payload": {"unresolved": 1}}
    )
    assert result["created"] == 1
    activities = odoo_env["mail.activity"].search(
        [("res_model", "=", "fix.automation"), ("res_id", "=", broken.id)]
    )
    assert len(activities) == 1
    assert "AUT-001" in activities.summary
    assert "does not resolve" in activities.summary
    assert "evt-b1-consumer-1" in (activities.note or "")
    # redelivery of the same event creates nothing
    again = odoo_env["fix.automation"].consume_register_loaded(
        {"event_id": "evt-b1-consumer-1", "payload": {"unresolved": 1}}
    )
    assert again["created"] == 0
    assert (
        odoo_env["mail.activity"].search_count(
            [("res_model", "=", "fix.automation"), ("res_id", "=", broken.id)]
        )
        == 1
    )


def test_register_loaded_consumer_is_silent_when_everything_resolves(odoo_env):
    load_catalogue(odoo_env)
    before = odoo_env["mail.activity"].search_count([("res_model", "=", "fix.automation")])
    result = odoo_env["fix.automation"].consume_register_loaded(
        {"event_id": "evt-b1-consumer-2", "payload": {"unresolved": 0}}
    )
    assert result["created"] == 0
    assert odoo_env["mail.activity"].search_count([("res_model", "=", "fix.automation")]) == before


# --------------------------------------------------------------- migration
def _migration():
    spec = importlib.util.spec_from_file_location("b1_post_migrate_19120", MIGRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_migration_converts_a_non_catalogue_retired_row(odoo_env):
    """A row no longer in the catalogue, still carrying a retired engine
    value, is deactivated with the migration's note — and the catalogue is
    refreshed by the same script."""
    load_catalogue(odoo_env)
    cr = odoo_env.cr
    cr.execute(
        """
        INSERT INTO fix_automation
            (company_id, code, "trigger", action, engine, engine_ref,
             failure_policy, active, implementation)
        VALUES (%s, 'AUT-998', 'Legacy nightly', 'Run a DAG', 'airflow',
                'dag: fix_aut998', 'manual_fallback', TRUE, 'full')
        RETURNING id
        """,
        [odoo_env.company.id],
    )
    legacy_id = cr.fetchone()[0]
    _migration().migrate(cr, "19.0.1.1.0")
    legacy = odoo_env["fix.automation"].with_context(active_test=False).browse(legacy_id)
    assert legacy.engine == "manual"
    assert legacy.implementation == "none"
    assert legacy.active is False
    assert "19.0.1.2.0" in (legacy.executor_note or "")
    # the catalogue came through the same run, resolved
    assert by_code(odoo_env, "AUT-001").engine == "odoo_method"
    assert odoo_env["fix.automation"].action_report_engine_gap() == []
    # idempotent: a second run changes nothing
    snapshot = {
        r.code: (r.engine, r.implementation, r.active)
        for r in odoo_env["fix.automation"].with_context(active_test=False).search([])
    }
    _migration().migrate(cr, "19.0.1.2.0")
    after = {
        r.code: (r.engine, r.implementation, r.active)
        for r in odoo_env["fix.automation"].with_context(active_test=False).search([])
    }
    assert after == snapshot
