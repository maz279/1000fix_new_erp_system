"""A02 ERP review (20 Nov 2026), M02 field cash acceptance.

The cashier role (r29) holds only the front-desk and service-order cashier
groups: no field-order ACL. Accepting field cash read the field order as the
cashier, which raised AccessError in a real request (the earlier tests passed
only because the record sat in the transaction cache, where Odoo skips the
ACL). And the "cashier of the order's branch" was never checked.

``odoo_env`` rolls back after every test.
"""

# ruff: noqa: F811  (fixtures are imported and used as parameters)

from odoo.addons.cd_field_service.tests.test_a02_erp_m02 import (  # noqa: F401 (fixture)
    CASHIER_GROUPS,
    _completed_cash,
    _open_shift,
    _user,
    refused,
    w,
)


def test_a_plain_cashier_accepts_field_cash_from_a_cold_cache(w):
    so = w.so()
    rec = _completed_cash(w, so)
    shift = _open_shift(w)
    rec.with_user(w.ua).action_handover_field_cash()
    cashier = _user(w, "erp_rev_cashier", *CASHIER_GROUPS)
    assert not cashier.has_group("cd_field_service.group_fix_field_service_user")
    w.env.invalidate_all()  # a fresh request: nothing of the field order is cached
    rec.with_user(cashier).action_accept_field_cash()
    w.env.invalidate_all()
    assert rec.onsite_payment_state == "settled" and rec.cash_accepted_by_id == cashier
    assert shift.field_cash_deposited == 3000.0
    assert so.settlement_verified and so.settlement_verified_by == cashier


def test_a_cashier_of_another_branch_cannot_accept_the_field_cash(w):
    so = w.so()
    rec = _completed_cash(w, so)
    _open_shift(w)
    rec.with_user(w.ua).action_handover_field_cash()
    far = w.env["operating.unit"].create(
        {
            "name": "Far OU review",
            "code": "FARRV",
            "company_id": w.co.id,
            "partner_id": w.co.partner_id.id,
        }
    )
    outsider = _user(w, "erp_rev_far_cashier", *CASHIER_GROUPS)
    vals = {"default_operating_unit_id": far.id}
    if "assigned_operating_unit_ids" in outsider._fields:
        vals["assigned_operating_unit_ids"] = [(6, 0, [far.id])]
    outsider.write(vals)
    w.env.invalidate_all()
    err = refused(w.env, lambda: rec.with_user(outsider).action_accept_field_cash())
    assert err and "not one of your operating units" in err, err
    w.env.invalidate_all()
    assert rec.onsite_payment_state == "pending_acceptance" and not so.settlement_verified


def test_starting_travel_publishes_the_en_route_event_for_the_customer(w):
    so = w.so()
    rec = w.fo("dispatched", w.ea, order_id=so.id)
    rec.with_user(w.ua).action_accept()
    rec.with_user(w.ua).action_start_travel()
    event = w.env["fix.event.outbox"].search(
        [("event_type", "=", "field.order.en_route"), ("aggregate_id", "=", rec.id)]
    )
    assert len(event) == 1
    payload = event._relay_event_dict()["payload"]
    assert payload["service_order_id"] == so.id and payload["technician_name"]
