"""cd_workflow_engine — live-ORM behaviour of the M63 automation register."""

from __future__ import annotations

import json

import pytest
from odoo.exceptions import ValidationError


def test_code_must_be_an_aut_code(odoo_env):
    with pytest.raises(ValidationError, match="AUT codes are AUT-nnn"), odoo_env.cr.savepoint():
        odoo_env["fix.automation"].create(
            {"code": "JOB-1", "trigger": "t", "action": "a", "engine": "airflow"}
        )


def test_register_load_is_idempotent(odoo_env):
    automations = odoo_env["fix.automation"].with_context(active_test=False)
    automations.search([]).unlink()
    model = odoo_env["fix.automation"]

    assert model.action_load_register() == 60
    first = model.search([("code", "=", "AUT-001")])
    assert (first.engine, first.engine_ref) == (
        "domain_service",
        "service: cd_field_service.order_intake",
    )
    events = odoo_env["fix.event.outbox"].search(
        [("event_type", "=", "automation.register.loaded")]
    )
    assert [json.loads(e.payload) for e in events] == [{"loaded": 60, "total": 60}]

    # placeholders are refreshed from the catalogue; concrete refs are kept
    placeholder = model._default_engine_ref("airflow")
    first.engine_ref = placeholder
    second = model.search([("code", "=", "AUT-002")])
    second.engine_ref = "dag: fix_aut_002_custom"
    assert model.action_load_register() == 0
    assert first.engine_ref == "service: cd_field_service.order_intake"
    assert second.engine_ref == "dag: fix_aut_002_custom"


def test_reload_with_a_deactivated_automation(odoo_env):
    """Regression: the existence check skipped archived rows, so a reload
    re-created a deactivated AUT code and hit the UNIQUE(code) key."""
    model = odoo_env["fix.automation"]
    model.with_context(active_test=False).search([]).unlink()
    model.action_load_register()
    model.search([("code", "=", "AUT-010")]).active = False
    assert model.action_load_register() == 0
    assert model.with_context(active_test=False).search_count([("code", "=", "AUT-010")]) == 1


def test_engine_gap_report(odoo_env):
    model = odoo_env["fix.automation"]
    model.with_context(active_test=False).search([]).unlink()
    assert model._default_engine_ref("odoo_automated_action") == (
        "ir.actions.server (created at activation)"
    )
    gap = model.create(
        {
            "code": "AUT-901",
            "trigger": "Stock below minimum",
            "action": "Raise requisition",
            "engine": "odoo_automated_action",
            "engine_ref": model._default_engine_ref("odoo_automated_action"),
        }
    )
    empty = model.create(
        {"code": "AUT-902", "trigger": "Nightly", "action": "Sync", "engine": "airflow"}
    )
    done = model.create(
        {
            "code": "AUT-903",
            "trigger": "Order closed",
            "action": "Invoice",
            "engine": "domain_service",
            "engine_ref": "route: services/billing",
        }
    )
    report = model.action_report_engine_gap()
    assert {row["code"] for row in report} == {gap.code, empty.code}
    assert done.code not in {row["code"] for row in report}


def test_approval_matrix_row(odoo_env):
    row = odoo_env["fix.approval.matrix"].create(
        {"decision_domain": "credit_note", "threshold": 25000.0, "approver_role": "R-07"}
    )
    assert row.currency_id == odoo_env.ref("base.BDT")
