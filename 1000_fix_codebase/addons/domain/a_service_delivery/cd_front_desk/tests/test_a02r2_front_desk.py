# ruff: noqa: F811  (the M04 fixtures are imported and used as parameters)
"""A02 pass 2: M04 front-desk controls (cd_front_desk).

- M04-03: the opening float is the last close's cash less what was banked; a
  different float needs a Branch Manager who does not run the drawer, before
  the drawer takes any cash or closes.
- M04-04: shift.closed is published when the count is confirmed.
- M04-05: a service order's device is on one storage location at the branch:
  taken from its intake at the hand-off, required at Ready once the branch has
  shelves, freed at delivery / cancellation; one device per location.
- M04-06: the counter rating is the customer's own (a one-time page), never
  typed by staff.
- D20: a technician's field-cash shortage leaves the drawer for payroll.

Non-admin users (cashier, branch manager, Service Order Cashier).
"""

from __future__ import annotations

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

from .test_a02_p0_m04 import _refused, m04  # noqa: F401
from .test_a02_p1p2_cd_front_desk import _outbox
from .test_m04_build2 import _ready_order, screens, ui  # noqa: F401

REFUSED = (UserError, ValidationError, AccessError)


def _close_counted(m, s, **denoms):
    m.count(s, **denoms)
    s.action_confirm_closed()
    s.invalidate_recordset()
    return s


# ------------------------------------------------------------------ M04-03
def test_the_float_is_proposed_from_the_last_close(m04):
    m = m04
    s1 = m.shift()
    _close_counted(m, s1, d1000=5)  # counted 5,000, balanced
    # left empty, the next drawer opens with what the last close left
    s2 = (
        m.env["fix.cash.shift"]
        .with_user(m.cashier)
        .create({"branch_id": m.branch.id, "operator_id": m.cashier_emp.id})
    )
    assert (s2.opening_float, s2.proposed_float, s2.float_basis_shift_id) == (5000.0, 5000.0, s1)
    assert s2.float_variance == 0.0 and not s2._fd_float_unapproved()
    # the proposal cannot be typed
    with _refused(m.env, UserError):
        s2.write({"proposed_float": 9000.0})


def test_a_different_float_needs_an_independent_manager_first(m04):
    m = m04
    s1 = m.shift()
    _close_counted(m, s1, d1000=5)
    s2 = m.shift(opening=4800.0)  # 200 short of what the last close left
    assert s2.float_variance == -200.0 and s2._fd_float_unapproved()
    # the drawer takes no cash and cannot close until it is accepted
    sale = m.sale(s2)
    with _refused(m.env, UserError, "opening float"):
        sale.action_confirm()
    with _refused(m.env, UserError, "opening float"):
        s2.action_close_shift()
    # not the cashier, not a manager who runs the drawer
    with _refused(m.env, REFUSED):
        s2.with_user(m.cashier).action_approve_opening_float()
    s2.with_user(m.manager).action_approve_opening_float()
    s2.invalidate_recordset()
    assert s2.float_approved_by_id == m.manager and not s2._fd_float_unapproved()
    sale.action_confirm()
    assert s2.sudo().cash_payments == 1000.0


def test_a_first_shift_has_no_proposal(m04):
    s = m04.shift(branch=m04.branch2, opening=3000.0)
    assert not s.float_basis_shift_id and s.float_variance == 0.0
    assert not s._fd_float_unapproved()


# ------------------------------------------------------------------ M04-04
def test_shift_closed_is_published_when_the_count_is_confirmed(m04):
    m = m04
    s = m.shift()
    m.count(s, d1000=5)
    assert not _outbox(m.env, "shift.closed", "fix.cash.shift", s.id)
    s.action_confirm_closed()
    assert len(_outbox(m.env, "shift.closed", "fix.cash.shift", s.id)) == 1
    m.as_(m.manager, s).action_reconcile()
    assert len(_outbox(m.env, "shift.closed", "fix.cash.shift", s.id)) == 1


# ------------------------------------------------------------------ M04-05
def _location(m, code, branch=None):
    return (
        m.env["fix.storage.location"]
        .with_user(m.manager)
        .create({"branch_id": (branch or m.branch).id, "code": code})
    )


def test_a_ready_device_is_on_one_shelf(m04):
    m = m04
    loc = _location(m, "R2-A1")
    order = _ready_order(m)
    order.write({"storage_location_id": loc.id})
    loc.invalidate_recordset()
    assert loc.occupied and loc.occupied_by_order_id == order
    # BRU-FRD-06: one device per location
    other = m.env["fix.service.order"].create(
        {
            "device_id": m.env["fix.device"]
            .create({"device_model_id": m.device.device_model_id.id})
            .id,
            "customer_id": m.customer.id,
            "branch_id": m.branch.id,
            "fault_description": "second device",
            "service_type": "walk_in",
        }
    )
    with _refused(m.env, ValidationError, "holds one device"):
        other.write({"storage_location_id": loc.id})
    # another branch's shelf is refused
    far = _location(m, "R2-B1", branch=m.branch2)
    with _refused(m.env, ValidationError, "not at the order's branch"):
        other.write({"storage_location_id": far.id})
    # freed at delivery
    m.env.cr.execute("UPDATE fix_service_order SET state = 'delivered' WHERE id = %s", [order.id])
    m.env.invalidate_all()
    loc.invalidate_recordset()
    other.write({"storage_location_id": loc.id})
    assert loc.occupied_by_order_id == other


def test_ready_needs_a_shelf_once_the_branch_has_shelves(m04):
    m = m04
    order = m.env["fix.service.order"].create(
        {
            "device_id": m.device.id,
            "customer_id": m.customer.id,
            "branch_id": m.branch.id,
            "fault_description": "needs a shelf",
            "service_type": "walk_in",
        }
    )
    _location(m, "R2-C1")
    with pytest.raises(UserError, match="storage location"):
        order.action_ready()


def test_the_intakes_shelf_passes_to_its_order(m04):
    m = m04
    loc = _location(m, "R2-D1")
    it = m.intake(
        device_id=m.device.id,
        handover_method="signature",
        customer_signature_attachment_id=m.signature.id,
        storage_location_id=loc.id,
    )
    it.action_complete_handover()
    order = it.service_order_id
    assert order.storage_location_id == loc
    loc.invalidate_recordset()
    assert loc.occupied_by_order_id == order and not loc.occupied_by_id


# ------------------------------------------------------------------ M04-06
def test_the_customer_rates_on_their_own_page_staff_cannot_type_it(m04, ui, screens):
    m = m04
    order = _ready_order(m)
    # staff cannot type or change a rating
    res = ui.write(
        m.cashier, model="fix.service.order", record_id=order.id, values={"counter_rating": "5"}
    )
    assert "error" in res
    with _refused(m.env, REFUSED):
        order.with_user(m.cashier).write({"counter_rating": "5"})
    res = ui.action(
        m.cashier, model="fix.service.order", ids=[order.id], method="action_request_counter_rating"
    )
    assert res["success"], res
    url = res["result"]["rating_url"]
    token = url.rsplit("/", 1)[-1]
    assert order.sudo().counter_rating_token == token
    Order = m.env["fix.service.order"]
    with pytest.raises(UserError):
        Order._fd_take_customer_rating(token, "9")
    Order._fd_take_customer_rating(token, "4", "Quick, polite")
    order.invalidate_recordset()
    assert (order.counter_rating, order.counter_feedback) == ("4", "Quick, polite")
    assert order.counter_rated_by_id == m.cashier and order.counter_rated_at
    # the link was single use
    with pytest.raises(UserError, match="no longer open"):
        Order._fd_take_customer_rating(token, "1")
    assert not Order._fd_order_for_rating(token)


def test_an_expired_rating_link_is_closed(m04):
    m = m04
    order = _ready_order(m)
    order.with_user(m.cashier).action_request_counter_rating()
    token = order.sudo().counter_rating_token
    m.env.flush_all()
    m.env.cr.execute(
        "UPDATE fix_service_order SET counter_rating_requested_at = %s WHERE id = %s",
        [fields.Datetime.subtract(fields.Datetime.now(), days=2), order.id],
    )
    m.env.invalidate_all()
    with pytest.raises(UserError, match="no longer open"):
        m.env["fix.service.order"]._fd_take_customer_rating(token, "5")
