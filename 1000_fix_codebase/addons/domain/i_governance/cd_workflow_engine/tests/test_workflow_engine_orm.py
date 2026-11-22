"""cd_workflow_engine — live-ORM behaviour of the M63 automation register.

19.0.1.2.0 (A11 fix B1): the register's bindings are verified at runtime; the
loader refreshes every catalogue fact; the gap report resolves references.
The deeper binding/guard/consumer/migration tests live in test_aut_bindings.py.
"""

from __future__ import annotations

import json

import pytest
from odoo.exceptions import ValidationError


def test_code_must_be_an_aut_code(odoo_env):
    with pytest.raises(ValidationError, match="AUT codes are AUT-nnn"), odoo_env.cr.savepoint():
        odoo_env["fix.automation"].create(
            {
                "code": "JOB-1",
                "trigger": "t",
                "action": "a",
                "engine": "odoo_method",
                "engine_ref": "method:fix.service.order._flag_rework",
                "implementation": "full",
            }
        )


def test_register_load_is_idempotent(odoo_env):
    automations = odoo_env["fix.automation"].with_context(active_test=False)
    automations.search([]).unlink()
    model = odoo_env["fix.automation"]

    assert model.action_load_register() == 60
    first = model.search([("code", "=", "AUT-001")])
    assert (first.engine, first.engine_ref) == (
        "odoo_method",
        "method:fix.walkin.intake.action_complete_handover",
    )
    assert first.binding_state == "verified"
    # the LAST event of this load: the outbox also holds events from earlier
    # module migrations, and their counts were taken with a partial registry
    events = odoo_env["fix.event.outbox"].search(
        [("event_type", "=", "automation.register.loaded")], order="id desc", limit=1
    )
    payload = json.loads(events.payload)
    assert payload == {
        "loaded": 60,
        "refreshed": 0,
        "verified": 52,
        "unresolved": 0,
        "total": 60,
    }

    # a stale binding is REFRESHED to the catalogue's (the register states what
    # really executes a row, so a hand-typed reference cannot survive a reload)
    second = model.search([("code", "=", "AUT-002")])
    second._catalogue_write({"engine": "manual", "engine_ref": False, "implementation": "none"})
    assert model.action_load_register() == 0
    second.invalidate_recordset()
    assert second.engine == "odoo_method"
    assert second.engine_ref == "method:fix.field.order.action_suggest_technicians"
    assert second.implementation == "partial" and second.active


def test_reload_with_a_deactivated_automation(odoo_env):
    """Regression: the existence check skipped archived rows, so a reload
    re-created a deactivated AUT code and hit the UNIQUE(code) key. And a
    deliberate switch-off by an operator survives a reload (only the
    implemented-by-nobody rows are forced inactive)."""
    model = odoo_env["fix.automation"]
    model.with_context(active_test=False).search([]).unlink()
    model.action_load_register()
    model.search([("code", "=", "AUT-010")]).active = False
    assert model.action_load_register() == 0
    rows = model.with_context(active_test=False).search([("code", "=", "AUT-010")])
    assert len(rows) == 1
    assert not rows.active, "a reload must not revive an automation an operator switched off"


def test_engine_gap_report_uses_the_binding_resolver(odoo_env):
    model = odoo_env["fix.automation"]
    model.with_context(active_test=False).search([]).unlink()
    broken = model.create(
        {
            "code": "AUT-901",
            "trigger": "Stock below minimum",
            "action": "Raise requisition",
            "engine": "odoo_cron",
            "engine_ref": "cron:cd_inventory.no_such_cron",
            "implementation": "full",
            "active": False,
        }
    )
    planned = model.create(
        {
            "code": "AUT-902",
            "trigger": "Nightly",
            "action": "Sync",
            "engine": "manual",
            "implementation": "none",
        }
    )
    verified = model.create(
        {
            "code": "AUT-903",
            "trigger": "Order closed",
            "action": "Flag rework",
            "engine": "odoo_method",
            "engine_ref": "method:fix.service.order._flag_rework",
            "implementation": "partial",
        }
    )
    report = {row["code"]: row for row in model.action_report_engine_gap()}
    assert broken.code in report and report[broken.code]["coverage_state"] == "broken"
    # a manual row is born inactive: nothing implements it, so it claims nothing
    assert planned.active is False
    assert planned.code not in report
    assert verified.code not in report
    planned.active = True
    report = {row["code"]: row for row in model.action_report_engine_gap()}
    assert planned.code in report and report[planned.code]["coverage_state"] == "planned"


def test_approval_matrix_row(odoo_env):
    row = odoo_env["fix.approval.matrix"].create(
        {"decision_domain": "credit_note", "threshold": 25000.0, "approver_role": "R-07"}
    )
    assert row.currency_id == odoo_env.ref("base.BDT")
