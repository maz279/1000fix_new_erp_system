"""Behavioural tests for the M04 front desk on the live ORM
(``odoo_env``: fix_test, rolled back after every test)."""

import json
from contextlib import contextmanager
from datetime import datetime
from types import SimpleNamespace

import pytest
from odoo.exceptions import ValidationError


@contextmanager
def _refused(env, exc, match=None):
    """Expect ``exc``; the failed operation is rolled back (flushing savepoint)."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info
    env.invalidate_all()


@pytest.fixture
def desk(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "FDKENT", "legal_name": "Front Desk Entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {"name": "Gulshan Desk", "code": "gul1", "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    other = env["fix.branch"].create(
        {"name": "Mirpur Desk", "code": "MIR1", "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    brand = env["fix.brand"].create({"name": "DeskBrand", "code": "DSKBR"})
    model = env["fix.device.model"].create({"name": "DeskPad", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "Desk Customer", "phone": "01611000000"})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-FDK-1"}
    )
    cashier = env["hr.employee"].create({"name": "Desk Cashier"})
    return SimpleNamespace(
        env=env,
        ou=ou,
        branch=branch,
        other=other,
        customer=customer,
        device=device,
        cashier=cashier,
    )


def _events(env, aggregate, rec_id):
    return env["fix.event.outbox"].search(
        [("aggregate", "=", aggregate), ("aggregate_id", "=", rec_id)], order="id asc"
    )


# --- fix.token.queue -------------------------------------------------------------------


def _token(desk, **vals):
    return desk.env["fix.token.queue"].create(
        {"branch_id": desk.branch.id, "operating_unit_id": desk.ou.id, **vals}
    )


def test_tokens_number_per_branch_and_display_the_branch_prefix(desk):
    first, second = _token(desk), _token(desk, service_type="payment")
    elsewhere = desk.env["fix.token.queue"].create(
        {"branch_id": desk.other.id, "operating_unit_id": desk.ou.id}
    )
    assert (first.token_number, second.token_number, elsewhere.token_number) == (1, 2, 1)
    assert (first.token_display, second.token_display, elsewhere.token_display) == (
        "GUL-001",
        "GUL-002",
        "MIR-001",
    )
    explicit = _token(desk, token_number=40)
    assert (explicit.token_number, _token(desk).token_number) == (40, 41)
    payload = json.loads(_events(desk.env, "fix.token.queue", second.id).payload)
    assert payload == {"token": "GUL-002", "branch": "Gulshan Desk", "service_type": "payment"}


def test_tokens_created_in_one_batch_get_distinct_numbers(desk):
    """Regression: every vals of a batch searched the table, so a batch of two
    tokens for one branch got the SAME number."""
    common = {"branch_id": desk.branch.id, "operating_unit_id": desk.ou.id}
    batch = desk.env["fix.token.queue"].create(
        [dict(common), dict(common), dict(common, branch_id=desk.other.id)]
    )
    assert batch.mapped("token_number") == [1, 2, 1]
    assert batch.mapped("token_display") == ["GUL-001", "GUL-002", "MIR-001"]


def test_token_flow_is_audit_tracked(desk):
    """A09-01: the queue carries the chatter/activity mixins of its siblings and
    every state change leaves a tracking message."""
    cr = desk.env.cr
    token = _token(desk)
    assert "activity_ids" in token._fields and "message_ids" in token._fields
    cr.flush()  # tracking is finalised per flush (mail precommit hook)
    token.action_call()
    assert (token.state, bool(token.called_at)) == ("called", True)
    cr.flush()
    token.action_serving()
    assert (token.state, bool(token.served_at)) == ("serving", True)
    cr.flush()
    token.action_complete()
    cr.flush()
    tracked = token.message_ids.tracking_value_ids.filtered(
        lambda t: t.field_id.name == "state"
    ).sorted("id")
    assert [(t.old_value_char, t.new_value_char) for t in tracked] == [
        ("Waiting", "Called"),
        ("Called", "Serving"),
        ("Serving", "Completed"),
    ]
    activity = token.activity_schedule("mail.mail_activity_data_todo", summary="Call back")
    assert token.activity_ids == activity


# --- fix.cash.shift -------------------------------------------------------------------------


def _shift(desk, **vals):
    return desk.env["fix.cash.shift"].create(
        {
            "branch_id": desk.branch.id,
            "operating_unit_id": desk.ou.id,
            "operator_id": desk.cashier.id,
            "opening_float": 2000.0,
            "cash_payments": 7500.0,
            "cash_refunds": 500.0,
            "cash_advances": 1000.0,
            **vals,
        }
    )


def test_expected_closing_and_variance(desk):
    shift = _shift(desk)
    # 2000 + 7500 - 500 - 1000 = 8000; no variance while the drawer is open
    assert (shift.expected_closing, shift.variance) == (8000.0, 0.0)
    shift.action_close_shift()
    shift.closing_counted = 7950.0
    assert shift.variance == -50.0
    shift.action_reconcile()
    assert (shift.state, shift.reconciled_by, bool(shift.closed_at)) == (
        "discrepancy",
        desk.env.user,
        True,
    )
    payload = json.loads(_events(desk.env, "fix.cash.shift", shift.id).payload)
    assert payload == {
        "shift_id": shift.id,
        "branch": "Gulshan Desk",
        "variance": -50.0,
        "currency": "BDT",
    }


def test_balanced_drawer_reconciles(desk):
    shift = _shift(desk)
    shift.action_close_shift()
    shift.closing_counted = 8000.0
    shift.action_reconcile()
    assert (shift.state, shift.variance) == ("reconciled", 0.0)


def test_an_empty_drawer_is_a_discrepancy_not_a_reconciled_shift(desk):
    """Regression: a count of 0.00 read as "not counted": variance 0, reconciled."""
    shift = _shift(desk)
    shift.action_close_shift()
    shift.closing_counted = 0.0
    assert shift.variance == -8000.0
    shift.action_reconcile()
    assert shift.state == "discrepancy"


def test_only_a_counted_shift_reconciles_and_only_an_open_one_closes(desk):
    """Regression: an OPEN drawer could be reconciled (nothing compared)."""
    env = desk.env
    shift = _shift(desk)
    with _refused(env, ValidationError, "being counted can be reconciled"):
        shift.action_reconcile()
    assert shift.state == "open"
    shift.action_close_shift()
    with _refused(env, ValidationError, "Only open shifts can be closed"):
        shift.action_close_shift()


# --- fix.walkin.intake ------------------------------------------------------------------------


def _intake(desk, **vals):
    return desk.env["fix.walkin.intake"].create(
        {
            "branch_id": desk.branch.id,
            "operating_unit_id": desk.ou.id,
            "customer_id": desk.customer.id,
            "device_id": desk.device.id,
            "fault_description": "Cracked screen",
            "intake_start": datetime(2026, 10, 22, 10, 0, 0),
            **vals,
        }
    )


def test_handover_opens_the_service_order_and_times_the_intake(desk):
    intake = _intake(desk)
    assert intake.intake_duration_seconds == 0  # not handed over yet
    intake.action_complete_handover()
    order = intake.service_order_id
    assert (intake.state, intake.handover_acknowledged) == ("completed", True)
    assert (order.state, order.service_type, order.device_id, order.customer_id) == (
        "intake",
        "walk_in",
        desk.device,
        desk.customer,
    )
    assert (order.branch_id, order.fault_description, order.operating_unit_id) == (
        desk.branch,
        "Cracked screen",
        desk.ou,
    )
    intake.handover_complete = datetime(2026, 10, 22, 10, 2, 45)
    assert intake.intake_duration_seconds == 165  # 2 min 45 s: inside the 3-minute gate
    payload = json.loads(_events(desk.env, "fix.walkin.intake", intake.id).payload)
    assert (payload["intake_id"], payload["branch"]) == (intake.id, "Gulshan Desk")


def test_handover_keeps_an_existing_service_order(desk):
    existing = desk.env["fix.service.order"].create(
        {
            "device_id": desk.device.id,
            "customer_id": desk.customer.id,
            "branch_id": desk.branch.id,
            "fault_description": "Booked online",
        }
    )
    intake = _intake(desk, service_order_id=existing.id)
    intake.action_complete_handover()
    assert intake.service_order_id == existing
    assert desk.env["fix.service.order"].search_count([("device_id", "=", desk.device.id)]) == 1
