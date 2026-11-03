"""M01 extension tests: the fault-code taxonomy master, the repair-service
warranty and the config-param estimate approval thresholds.

``odoo_env`` (addons/conftest.py): superuser environment on fix_test, rolled
back after every test. Expected values are computed by hand in the comments.
"""

from contextlib import contextmanager
from datetime import timedelta
from types import SimpleNamespace

import pytest
from odoo import Command
from odoo.exceptions import UserError


@pytest.fixture
def base(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "M01EXT", "legal_name": "M01 Ext Entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "M01 Ext Branch",
            "code": "M01EB",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    brand = env["fix.brand"].create({"name": "M01ExtBrand", "code": "M01XB"})
    device_model = env["fix.device.model"].create({"name": "M01 Ext Phone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "M01 Ext Customer", "phone": "01711000601"})
    device = env["fix.device"].create(
        {"device_model_id": device_model.id, "owner_id": customer.id, "serial_number": "SN-M01X-1"}
    )
    return SimpleNamespace(env=env, branch=branch, device=device, customer=customer)


@contextmanager
def _refused(env, exc, match=None):
    """Expect ``exc``; the offending operation is rolled back (flushing
    savepoint) so nothing invalid survives for teardown."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info
    env.invalidate_all()


def _order(base, **vals):
    return base.env["fix.service.order"].create(
        {
            "device_id": base.device.id,
            "customer_id": base.customer.id,
            "branch_id": base.branch.id,
            "fault_description": "No display",
            **vals,
        }
    )


def _walk_to_delivered(order):
    """Step the AS-06 machine to delivered the way the actions do (QC gate
    satisfied with a passed checklist)."""
    order.state = "intake"
    order.action_start_diagnostic()
    order.state = "estimate_pending"
    order.action_send_estimate()
    order.state = "awaiting_approval"
    order.action_approve()
    order.action_start_repair()
    order.action_submit_qc()
    order.env["fix.qc.checklist"].create(
        {"order_id": order.id, "state": "passed", "item_ids": [Command.create({"name": "Boot"})]}
    )
    order.action_ready()
    order.action_deliver()
    return order


# --- fix.fault.code: the taxonomy master ------------------------------------------


def test_fault_code_master_creates_and_orders_by_category(base):
    env = base.env
    # codes outside the seeded taxonomy (the module data loads 26 real codes)
    first = env["fix.fault.code"].create(
        {"code": "XTST-9", "name": "Late code", "category": "software"}
    )
    env["fix.fault.code"].create({"code": "XTST-1", "name": "Early code", "category": "power"})
    # _order = category, code: power sorts before software regardless of ids
    ordered = env["fix.fault.code"].search([("code", "like", "XTST%")], order="category, code")
    assert [c.code for c in ordered] == ["XTST-1", "XTST-9"]
    assert first.default_severity == "functional"


def test_fault_code_must_be_unique(base):
    env = base.env
    env["fix.fault.code"].create({"code": "XTST-DUP", "name": "Original", "category": "power"})
    with _refused(env, Exception, match="(?i)unique|duplicate"):
        env["fix.fault.code"].create(
            {"code": "XTST-DUP", "name": "Collision", "category": "software"}
        )
        env.cr.flush()  # surface the SQL constraint inside the savepoint


# --- repair-service warranty -------------------------------------------------------


def test_repair_warranty_issues_once_with_history_and_event(base):
    env = base.env
    order = _walk_to_delivered(_order(base))
    order.action_issue_repair_warranty()

    assert order.service_warranty_until  # issued
    expected_until = (order.sla_resolution_at.date()) + timedelta(days=30)
    assert order.service_warranty_until == expected_until  # default 30 days
    assert order.service_warranty_issued_by == env.user

    # evidenced on the permanent device history
    warranty_entries = env["fix.device.history"].search(
        [("service_order_id", "=", order.id), ("event_type", "=", "warranty")]
    )
    assert len(warranty_entries) == 1

    # and broadcast (outbox) for downstream consumers
    events = env["fix.event.outbox"].search(
        [
            ("aggregate", "=", "fix.service.order"),
            ("aggregate_id", "=", order.id),
            ("event_type", "=", "service_order.warranty_issued"),
        ]
    )
    assert len(events) == 1

    # one issuance per order — the second attempt is refused
    with _refused(env, UserError, match="already issued"):
        order.action_issue_repair_warranty()


def test_repair_warranty_refused_before_delivery(base):
    env = base.env
    order = _order(base)  # draft
    with _refused(env, UserError, match="after delivery"):
        order.action_issue_repair_warranty()
    order.state = "intake"
    with _refused(env, UserError, match="after delivery"):
        order.action_issue_repair_warranty()


def test_repair_warranty_honours_configured_days(base):
    order = _walk_to_delivered(_order(base, service_warranty_days=90))
    order.action_issue_repair_warranty()
    expected_until = (order.sla_resolution_at.date()) + timedelta(days=90)
    assert order.service_warranty_until == expected_until


# --- estimate approval thresholds (config-param overridable) -----------------------


def _estimate(base, order, lines):
    return base.env["fix.estimate"].create(
        {
            "order_id": order.id,
            "line_ids": [
                Command.create(
                    {
                        "line_type": kind,
                        "description": f"{kind} line",
                        "quantity": qty,
                        "unit_price": price,
                    }
                )
                for kind, qty, price in lines
            ],
        }
    )


def test_threshold_defaults_match_bru_srm_07_08(base):
    env = base.env
    # no params set: the declared defaults 5,000 / 25,000 BDT
    assert env["fix.estimate"]._threshold_customer() == 5000.0
    assert env["fix.estimate"]._threshold_dual() == 25000.0


def test_threshold_config_param_tightens_customer_gate(base):
    env = base.env
    env["ir.config_parameter"].sudo().set_param(
        "cd_service_order.estimate_threshold_customer", "100"
    )
    try:
        assert env["fix.estimate"]._threshold_customer() == 100.0
        order = _order(base)
        # one part line at BDT 150: above the overridden threshold, below default
        est = _estimate(base, order, [("part", 1, 150.0)])
        est.action_send()  # A02 M01-4: only a sent estimate is approved
        assert est.grand_total > 100.0
        with _refused(env, UserError, match="BRU-SRM-07"):
            est.action_approve()
        # with documented customer approval the same estimate approves
        est.customer_approval_ref = "SMS-OTP-9911"
        est.action_approve()
        assert est.state == "approved"
    finally:
        # The fixture rolls the param ROW back, but Odoo 19 caches config
        # parameters in the registry's 'stable' cache (ormcache on get_param,
        # cleared by set_param — not by rollback). Without this the override
        # leaks into every later test in the process.
        env.registry.clear_cache("stable")


def test_default_threshold_still_blocks_without_config_param(base):
    """No param set: BDT 6,000 without customer approval is refused (the
    pre-existing BRU-SRM-07 behaviour, now through the helper)."""
    env = base.env
    order = _order(base)
    est = _estimate(base, order, [("part", 1, 6000.0)])
    est.action_send()  # A02 M01-4: only a sent estimate is approved
    with _refused(env, UserError, match="BRU-SRM-07"):
        est.action_approve()
