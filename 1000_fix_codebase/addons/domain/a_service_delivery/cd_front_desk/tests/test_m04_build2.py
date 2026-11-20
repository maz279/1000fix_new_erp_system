"""M04 build (13 Nov 2026): the five spec capabilities that had no record.

After every M04 sub-module page got its capture button, the audit listed
what the specification gives M04 and the estate still could not record:

- counters and their capabilities, and the rules that place a token in a
  priority lane (FR-FRD-004/-007/-027, BRU-FRD-07);
- a storage-location master, one device per location (FR-FRD-011, T-09,
  BRU-FRD-06), instead of a free-text bin;
- a ledger of every drawer movement, with approved cash-outs (FR-FRD-015,
  T-06, BRU-FRD-09/-11);
- an identity check of a third-party collector at release (BRU-FRD-05);
- branch announcements (FR-FRD-031).

Each is exercised here through the workspace endpoints the forms use, as
non-admin users. ``odoo_env``: fix_test, rolled back after every test.
"""

from __future__ import annotations

import types

import odoo.addons.cd_p03_portal.controllers.p03_generic_api as api
import pytest
from odoo.exceptions import UserError, ValidationError

from . import test_a02_p0_m04 as p0
from .test_m04_submodule_capture import _form_values, _screens

m04 = p0.m04


@pytest.fixture(scope="module")
def screens():
    return _screens()


@pytest.fixture
def ui(m04, monkeypatch):
    cls = api.P03GenericApiController
    ctl = cls()

    def call(name, user, **kw):
        monkeypatch.setattr(
            api, "request", types.SimpleNamespace(env=m04.env(user=user.id, su=False))
        )
        fn = getattr(cls, name)
        return getattr(fn, "original_endpoint", fn)(ctl, **kw)

    return types.SimpleNamespace(
        records=lambda user, **kw: call("model_records", user, **kw),
        write=lambda user, **kw: call("model_write", user, **kw),
        action=lambda user, **kw: call("model_action", user, **kw),
    )


# ------------------------------------------------- 1. counters & priority rules


def test_a_manager_sets_up_counters_and_a_cashier_cannot(m04, ui, screens):
    cfg = screens["M04-form-counter"]
    vals = _form_values(
        cfg, {"branch_id": m04.branch.id, "number": 1, "label": "Intake", "can_pay": False}
    )
    res = ui.write(m04.manager, model="fix.queue.counter", values=vals)
    assert "error" not in res, res
    counter = m04.env["fix.queue.counter"].browse(res["id"])
    assert counter.operating_unit_id == m04.branch.operating_unit_id
    assert "error" in ui.write(m04.manager, model="fix.queue.counter", values=vals)  # number taken
    assert "error" in ui.write(m04.cashier, model="fix.queue.counter", values=dict(vals, number=2))


def test_a_token_goes_only_to_a_counter_that_serves_it(m04, ui, screens):
    Counter = m04.env["fix.queue.counter"]
    intake_desk = Counter.create({"branch_id": m04.branch.id, "number": 3, "can_pay": False})
    other_branch = Counter.create({"branch_id": m04.branch2.id, "number": 3})
    cfg = screens["M04-form-token"]
    ok = ui.write(
        m04.cashier,
        model="fix.token.queue",
        values=_form_values(
            cfg,
            {"branch_id": m04.branch.id, "service_type": "drop_off", "counter_id": intake_desk.id},
        ),
    )
    assert "error" not in ok, ok
    token = m04.env["fix.token.queue"].browse(ok["id"])
    assert token.counter_number == 3
    for counter, service in ((intake_desk, "payment"), (other_branch, "drop_off")):
        res = ui.write(
            m04.cashier,
            model="fix.token.queue",
            values={"branch_id": m04.branch.id, "service_type": service, "counter_id": counter.id},
        )
        assert "error" in res, (counter.name, service)


def test_a_priority_rule_places_the_token_automatically(m04, ui, screens):
    tag = m04.env["res.partner.category"].create({"name": "M04 Senior Citizen"})
    senior = m04.env["res.partner"].create({"name": "M04 senior", "category_id": [(6, 0, tag.ids)]})
    company = m04.env["res.partner"].create({"name": "M04 Corp Ltd", "is_company": True})
    rules = screens["M04-form-priority-rule"]
    for vals in (
        {
            "name": "Seniors first",
            "partner_category_id": tag.id,
            "priority_level": "senior_citizen",
            "sequence": 1,
        },
        {
            "name": "Corporate SLA",
            "corporate_only": True,
            "priority_level": "vip_corporate",
            "sequence": 2,
        },
    ):
        res = ui.write(
            m04.manager, model="fix.queue.priority.rule", values=_form_values(rules, vals)
        )
        assert "error" not in res, res
    # a rule with no condition would put everyone first: refused
    assert "error" in ui.write(
        m04.manager,
        model="fix.queue.priority.rule",
        values={"name": "everyone", "priority_level": "vip_corporate"},
    )
    assert "error" in ui.write(
        m04.cashier,
        model="fix.queue.priority.rule",
        values={"name": "x", "corporate_only": True, "priority_level": "vip_corporate"},
    )

    def issue(partner, lane=None):
        vals = {"branch_id": m04.branch.id, "service_type": "drop_off", "customer_id": partner.id}
        if lane:
            vals["priority_level"] = lane
        res = ui.write(m04.cashier, model="fix.token.queue", values=vals)
        assert "error" not in res, res
        return m04.env["fix.token.queue"].browse(res["id"])

    t = issue(senior)
    assert t.priority_level == "senior_citizen" and t.priority_rule_id.name == "Seniors first"
    t = issue(company)
    assert t.priority_level == "vip_corporate"
    t = issue(m04.customer)
    assert t.priority_level == "normal" and not t.priority_rule_id
    # a rule raises a lane, never lowers the agent's choice
    t = issue(senior, lane="vip_corporate")
    assert t.priority_level == "vip_corporate" and not t.priority_rule_id
    # the stamp is the rule's, not typed
    res = ui.write(
        m04.cashier, model="fix.token.queue", record_id=t.id, values={"priority_rule_id": 1}
    )
    t.invalidate_recordset()
    assert not t.priority_rule_id or "error" in res


# ------------------------------------------------- 2. storage locations


def test_a_location_holds_one_device_and_frees_at_handover(m04, ui, screens):
    form = screens["M04-form-location"]
    res = ui.write(
        m04.manager,
        model="fix.storage.location",
        values=_form_values(form, {"branch_id": m04.branch.id, "code": "A-01-1", "shelf": "A"}),
    )
    assert "error" not in res, res
    loc = m04.env["fix.storage.location"].browse(res["id"])
    assert "error" in ui.write(
        m04.manager,
        model="fix.storage.location",
        values={"branch_id": m04.branch.id, "code": "a-01-1"},
    )

    assign = screens["M04-form-storage-assign"]
    first = m04.intake(device_id=m04.device.id)
    res = ui.write(
        m04.cashier,
        model="fix.walkin.intake",
        record_id=first.id,
        values=_form_values(assign, {"storage_location_id": loc.id}),
    )
    assert "error" not in res, res
    first.invalidate_recordset()
    loc.invalidate_recordset()
    assert first.storage_bin_code == "A-01-1" and loc.occupied and loc.occupied_by_id == first

    # BRU-FRD-06: a second device cannot go into the occupied location
    second = m04.intake(device_serial_input="SN-OTHER-1")
    res = ui.write(
        m04.cashier,
        model="fix.walkin.intake",
        record_id=second.id,
        values={"storage_location_id": loc.id},
    )
    assert "error" in res and "one" in res["error"]
    # T-09: the same device cannot be stored at a second location too
    loc2 = m04.env["fix.storage.location"].create({"branch_id": m04.branch.id, "code": "A-01-2"})
    third = m04.intake(device_id=m04.device.id)
    res = ui.write(
        m04.cashier,
        model="fix.walkin.intake",
        record_id=third.id,
        values={"storage_location_id": loc2.id},
    )
    assert "error" in res
    # a location of another branch is refused
    far = m04.env["fix.storage.location"].create({"branch_id": m04.branch2.id, "code": "Z-1"})
    res = ui.write(
        m04.cashier,
        model="fix.walkin.intake",
        record_id=second.id,
        values={"storage_location_id": far.id},
    )
    assert "error" in res

    # the device leaves custody at the hand-off: the location is free again
    first.write(
        {"handover_method": "signature", "customer_signature_attachment_id": m04.signature.id}
    )
    first.with_user(m04.cashier).action_submit_for_handover()
    first.with_user(m04.cashier).action_complete_handover()
    loc.invalidate_recordset()
    assert not loc.occupied
    res = ui.write(
        m04.cashier,
        model="fix.walkin.intake",
        record_id=second.id,
        values={"storage_location_id": loc.id},
    )
    assert "error" not in res, res


# ------------------------------------------------- 3. drawer movement ledger


def test_every_drawer_posting_is_a_ledger_row(m04):
    shift = m04.shift()
    sale = m04.sale(shift_rec=shift, price=1000.0)
    sale.write({"tendered_amount": 1000.0})
    sale.with_user(m04.cashier).action_confirm()
    rows = m04.env["fix.cash.movement"].search([("shift_id", "=", shift.id)])
    assert len(rows) == 1
    assert (rows.movement_type, rows.direction, rows.amount, rows.state) == (
        "receipt",
        "in",
        sale.total,
        "posted",
    )
    assert sale.name in rows.reference
    # T-06: a posted movement is neither changed nor deleted
    with pytest.raises(UserError):
        rows.with_user(m04.cashier).write({"amount": 1.0})
    with pytest.raises(UserError):
        rows.with_user(m04.cashier).unlink()


def test_a_cash_out_lowers_the_expected_cash(m04, ui, screens):
    shift = m04.shift(opening=5000.0)
    form = screens["M04-form-movement"]
    res = ui.write(
        m04.cashier,
        model="fix.cash.movement",
        values=_form_values(
            form,
            {
                "shift_id": shift.id,
                "movement_type": "petty_expense",
                "amount": 200.0,
                "reason": "Tea and water",
            },
        ),
    )
    assert "error" not in res, res
    mv = m04.env["fix.cash.movement"].browse(res["id"])
    assert mv.state == "draft" and mv.recorded_by_id == m04.cashier
    res = ui.action(m04.cashier, model="fix.cash.movement", ids=[mv.id], method="action_post")
    assert res["success"], res
    shift.invalidate_recordset()
    assert shift.cash_advances == 200.0 and shift.expected_closing == 4800.0
    mv.invalidate_recordset()
    assert mv.state == "posted"
    # receipts and refunds are never typed
    res = ui.write(
        m04.cashier,
        model="fix.cash.movement",
        values={"shift_id": shift.id, "movement_type": "receipt", "amount": 50.0, "reason": "x"},
    )
    assert "error" in res
    # a cash-out without a reason is refused
    res = ui.write(
        m04.cashier,
        model="fix.cash.movement",
        values={"shift_id": shift.id, "movement_type": "safe_drop", "amount": 50.0},
    )
    assert "error" in res


def test_a_large_petty_expense_and_an_advance_need_an_independent_manager(m04, ui):
    shift = m04.shift(as_user=m04.manager_cashier, operator=m04.manager_cashier_emp)
    Movement = m04.env["fix.cash.movement"]
    big = Movement.with_user(m04.manager_cashier).create(
        {
            "shift_id": shift.id,
            "movement_type": "petty_expense",
            "amount": 900.0,
            "reason": "Plumber",
        }
    )
    adv = Movement.with_user(m04.manager_cashier).create(
        {
            "shift_id": shift.id,
            "movement_type": "staff_advance",
            "amount": 100.0,
            "reason": "Rider fuel",
            # A02 pass 2 (D2): an advance is booked to the staff member who took it
            "employee_id": m04.cashier2_emp.id,
        }
    )
    for mv in (big, adv):
        res = ui.action(
            m04.manager_cashier, model="fix.cash.movement", ids=[mv.id], method="action_post"
        )
        assert not res["success"] and "approval" in res["error"]
        # BRU-FRD-11: the manager who recorded it cannot approve it
        res = ui.action(
            m04.manager_cashier, model="fix.cash.movement", ids=[mv.id], method="action_approve"
        )
        assert not res["success"]
        res = ui.action(
            m04.cashier, model="fix.cash.movement", ids=[mv.id], method="action_approve"
        )
        assert not res["success"]
        res = ui.action(
            m04.manager, model="fix.cash.movement", ids=[mv.id], method="action_approve"
        )
        assert res["success"], res
        res = ui.action(
            m04.manager_cashier, model="fix.cash.movement", ids=[mv.id], method="action_post"
        )
        assert res["success"], res
    shift.invalidate_recordset()
    assert shift.cash_advances == 1000.0
    assert set((big | adv).mapped("approved_by_id")) == {m04.manager}


def test_a_cash_out_cannot_post_to_a_counted_drawer(m04):
    shift = m04.shift()
    mv = (
        m04.env["fix.cash.movement"]
        .with_user(m04.cashier)
        .create(
            {"shift_id": shift.id, "movement_type": "safe_drop", "amount": 1000.0, "reason": "Safe"}
        )
    )
    shift.with_user(m04.cashier).action_close_shift()
    with pytest.raises(UserError, match="open shift"):
        mv.with_user(m04.cashier).action_post()


# ------------------------------------------------- 4. collector identity


def _ready_order(m04):
    order = m04.env["fix.service.order"].create(
        {
            "device_id": m04.device.id,
            "customer_id": m04.customer.id,
            "branch_id": m04.branch.id,
            "fault_description": "M04 release",
            "service_type": "walk_in",
        }
    )
    # the workflow to Ready (intake, diagnosis, repair, QC) is M01's and tested
    # there; this test needs only an order that IS ready
    m04.env.cr.execute("UPDATE fix_service_order SET state = 'ready' WHERE id = %s", [order.id])
    order.invalidate_recordset()
    return order


def test_a_third_party_collector_is_identified_before_release(m04, ui, screens):
    order = _ready_order(m04)
    form = screens["M04-form-release"]
    listed = ui.records(
        m04.cashier, model="fix.service.order", cols=["name"], domain=form["pickRecord"]["domain"]
    )
    assert order.id in {r["id"] for r in listed["rows"]}

    # the customer in person: their OTP is the check, no ID step
    res = ui.action(
        m04.cashier, model="fix.service.order", ids=[order.id], method="action_verify_collector_id"
    )
    assert not res["success"] and "OTP" in res["error"]

    res = ui.write(
        m04.cashier,
        model="fix.service.order",
        record_id=order.id,
        values=_form_values(
            form, {"recipient_name": "Rahim Uddin", "collector_is_customer": False}
        ),
    )
    assert "error" not in res, res
    # the evidence gate refuses a third party with no ID check
    order.invalidate_recordset()
    order.sudo().write(
        {"delivery_otp_verified": True, "service_report_attachment_id": m04.signature.id}
    )
    with pytest.raises(UserError, match="BRU-FRD-05"):
        order.with_user(m04.cashier)._check_delivery_evidence()

    res = ui.action(
        m04.cashier, model="fix.service.order", ids=[order.id], method="action_verify_collector_id"
    )
    assert not res["success"] and "relation" in res["error"]
    res = ui.write(
        m04.cashier,
        model="fix.service.order",
        record_id=order.id,
        values=_form_values(
            form,
            {
                "collector_relation": "Brother",
                "collector_id_type": "nid",
                "collector_id_last4": "4821",
                "collector_authority_attachment_id": m04.signature.id,
            },
        ),
    )
    assert "error" not in res, res
    res = ui.action(
        m04.cashier, model="fix.service.order", ids=[order.id], method="action_verify_collector_id"
    )
    assert res["success"], res
    order.invalidate_recordset()
    assert order.collector_id_verified_by == m04.cashier
    order.with_user(m04.cashier)._check_delivery_evidence()  # passes now

    # a different collector voids the check
    ui.write(
        m04.cashier,
        model="fix.service.order",
        record_id=order.id,
        values={"recipient_name": "Someone Else"},
    )
    order.invalidate_recordset()
    assert not order.collector_id_verified_by
    # the stamp is never typed
    ui.write(
        m04.cashier,
        model="fix.service.order",
        record_id=order.id,
        values={"collector_id_verified_by": m04.cashier.id},
    )
    order.invalidate_recordset()
    assert not order.collector_id_verified_by


def test_only_the_last_four_id_digits_are_kept(m04):
    field = m04.env["fix.service.order"]._fields["collector_id_last4"]
    assert field.size == 4


# ------------------------------------------------- 5. announcements


def test_an_announcement_is_published_read_and_frozen(m04, ui, screens):
    form = screens["M04-form-announcement"]
    vals = _form_values(
        form,
        {
            "name": "Eid hours",
            "kind": "notice",
            "body": "Branches close at 15:00 on the day before Eid.",
            "branch_ids": [m04.branch.id],
            "valid_from": "2026-11-01",
        },
    )
    assert "error" in ui.write(m04.cashier, model="fix.branch.announcement", values=vals)
    res = ui.write(m04.manager, model="fix.branch.announcement", values=vals)
    assert "error" not in res, res
    ann = m04.env["fix.branch.announcement"].browse(res["id"])
    for user, ok in ((m04.cashier, False), (m04.manager, True)):
        res = ui.action(
            user, model="fix.branch.announcement", ids=[ann.id], method="action_publish"
        )
        assert res["success"] is ok, res
    ann.invalidate_recordset()
    assert ann.state == "published" and ann.published_by_id == m04.manager and ann.is_current
    assert ann in m04.env["fix.branch.announcement"].search([("is_current", "=", True)])

    for _ in range(2):
        res = ui.action(
            m04.cashier, model="fix.branch.announcement", ids=[ann.id], method="action_acknowledge"
        )
        assert res["success"], res
    ann.invalidate_recordset()
    assert ann.ack_count == 1 and ann.ack_user_ids == m04.cashier

    res = ui.write(
        m04.manager, model="fix.branch.announcement", record_id=ann.id, values={"body": "changed"}
    )
    assert "error" in res
    res = ui.action(
        m04.manager, model="fix.branch.announcement", ids=[ann.id], method="action_withdraw"
    )
    assert res["success"], res
    with pytest.raises(UserError):
        ann.with_user(m04.cashier).action_acknowledge()


def test_an_announcement_cannot_end_before_it_starts(m04):
    with pytest.raises(ValidationError):
        m04.env["fix.branch.announcement"].create(
            {"name": "x", "body": "x", "valid_from": "2026-11-10", "valid_until": "2026-11-01"}
        )
