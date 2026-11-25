"""M04 extension tests: queue state guards, the reachable handover_pending
and closed states, the token↔order link, and the counter-sale model.

``odoo_env`` (addons/conftest.py): fix_test, rolled back after every test.
"""

import pytest
from odoo import fields
from odoo.exceptions import UserError


@pytest.fixture
def fd(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].search([("company_id", "=", env.company.id)], limit=1) or env[
        "fix.entity"
    ].create({"code": "FDEXT", "legal_name": "FD Ext Entity", "company_id": env.company.id})
    branch = env["fix.branch"].create(
        {
            "name": "FD Ext Branch",
            "code": "FDE1",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    customer = env["res.partner"].create({"name": "FD Customer", "phone": "01711000404"})
    operator = env["hr.employee"].create({"name": "FD Operator"})
    brand = env["fix.brand"].create({"name": "FdExtBrand", "code": "FDE"})
    device_model = env["fix.device.model"].create({"name": "FdExt Phone", "brand_id": brand.id})
    device = env["fix.device"].create(
        {"device_model_id": device_model.id, "owner_id": customer.id, "serial_number": "SN-FDE-1"}
    )

    def token(**vals):
        base = {"branch_id": branch.id, "operating_unit_id": ou.id, "customer_id": customer.id}
        base.update(vals)
        return env["fix.token.queue"].create(base)

    # A02 audit M04-8: the handover needs the customer's signed receipt
    signature = env["ir.attachment"].create({"name": "signed-receipt.png", "raw": b"signed"})

    def intake(**vals):
        base = {
            "branch_id": branch.id,
            "operating_unit_id": ou.id,
            "customer_id": customer.id,
            "device_id": device.id,
            "fault_description": "Charging port loose",
            "handover_method": "signature",
            "customer_signature_attachment_id": signature.id,
        }
        base.update(vals)
        return env["fix.walkin.intake"].create(base)

    def shift(**vals):
        base = {
            "branch_id": branch.id,
            "operating_unit_id": ou.id,
            "operator_id": operator.id,
            "shift_date": fields.Date.today(),
            "opening_float": 2000.0,
        }
        base.update(vals)
        return env["fix.cash.shift"].create(base)

    from types import SimpleNamespace

    return SimpleNamespace(
        env=env,
        branch=branch,
        customer=customer,
        operator=operator,
        token=token,
        intake=intake,
        shift=shift,
    )


# --- token queue guards + lifecycle ------------------------------------------


def test_token_full_guarded_lifecycle(fd):
    t = fd.token()
    assert t.token_display  # per-branch display number
    t.action_call()
    assert t.state == "called" and t.called_at
    t.action_serving()
    assert t.state == "serving" and t.served_at
    t.action_complete()
    assert t.state == "completed"


def test_token_call_refuses_completed(fd):
    t = fd.token()
    t.action_call()
    t.action_serving()
    t.action_complete()
    with pytest.raises(UserError, match="cannot be called"):
        t.action_call()


def test_token_no_show_and_recall(fd):
    t = fd.token()
    t.action_call()
    t.action_no_show()
    assert t.state == "no_show"
    t.action_call()  # recall path
    assert t.state == "called"


def test_token_cancel_refuses_completed(fd):
    t = fd.token()
    t.action_call()
    t.action_serving()
    t.action_complete()
    with pytest.raises(UserError, match="cannot be cancelled"):
        t.action_cancel()


# --- intake: handover_pending reachable + token link --------------------------


def test_intake_handover_pending_then_complete_writes_token_link(fd):
    tk = fd.token()
    wi = fd.intake(token_id=tk.id)
    wi.action_submit_for_handover()
    assert wi.state == "handover_pending"
    wi.action_complete_handover()
    assert wi.state == "completed"
    assert wi.service_order_id  # order created
    assert tk.service_order_id == wi.service_order_id  # the dead link — now written


def test_intake_submit_refuses_completed(fd):
    wi = fd.intake()
    wi.action_complete_handover()
    with pytest.raises(UserError, match="cannot complete handover"):
        wi.action_complete_handover()


# --- cash shift: closed state reachable ----------------------------------------


def test_shift_close_then_reconcile(fd):
    s = fd.shift()
    s.action_close_shift()
    assert s.state == "counting"
    s.denom_1000_count = 2  # A02 audit M04-7: the count is the blind denomination count
    s.action_submit_blind_count()
    s.action_confirm_closed()
    assert s.state == "closed" and s.closed_at
    s.action_reconcile()
    assert s.state == "reconciled"  # counted == expected (no activity)
    assert abs(s.variance) < 0.01


def test_shift_close_from_wrong_state_refused(fd):
    s = fd.shift()
    with pytest.raises(UserError, match="Only shifts in counting"):
        s.action_confirm_closed()


# --- counter sales ---------------------------------------------------------------


def test_counter_sale_confirm_feeds_cash_shift(fd):
    s = fd.shift()
    product = fd.env["product.product"].search([("list_price", ">", 0)], limit=1)
    if not product:
        product = fd.env["product.product"].create(
            {"name": "FD Tempered Glass", "list_price": 350.0, "type": "consu"}
        )
    sale = fd.env["fix.counter.sale"].create(
        {
            "shift_id": s.id,
            "branch_id": fd.branch.id,
            "product_id": product.id,
            "quantity": 2,
            "unit_price": 350.0,
            "operating_unit_id": s.operating_unit_id.id,
        }
    )
    assert sale.total == 700.0
    sale.action_confirm()
    assert sale.state == "confirmed"
    assert s.cash_payments == 700.0  # drawer expected takings include the sale


def test_counter_sale_refund_reverses_drawer(fd):
    s = fd.shift()
    product = fd.env["product.product"].search([("list_price", ">", 0)], limit=1)
    if not product:
        product = fd.env["product.product"].create(
            {"name": "FD Cable", "list_price": 200.0, "type": "consu"}
        )
    sale = fd.env["fix.counter.sale"].create(
        {
            "shift_id": s.id,
            "branch_id": fd.branch.id,
            "product_id": product.id,
            "quantity": 1,
            "unit_price": 200.0,
            "operating_unit_id": s.operating_unit_id.id,
        }
    )
    sale.action_confirm()
    # A02 audit M04-5: a refund is requested with a reason, then approved
    sale.action_request_refund(reason="defective: cable does not charge")
    sale.action_approve_refund()
    assert sale.state == "refunded"
    assert s.cash_refunds == 200.0
    with pytest.raises(UserError, match="Only confirmed sales"):
        sale.action_request_refund(reason="duplicate")
