"""A02 P0 controls for M04 Branch & Front-Desk (cd_front_desk).

Every GAP probe of the A02 audit (working/A02_evidence/probes/m31_m04/
probe_m31_m04.py, P04-01 .. P04-13) is turned into a control here, tested
both ways: the bypass is refused, and the legitimate path still works.

The tests act as NON-ADMIN users created in the test (cashier, branch
manager, refund approver, plain internal user), because the superuser is
trusted by the field guard and would hide a gap. ``odoo_env`` rolls back.
"""

import itertools
from contextlib import contextmanager
from datetime import timedelta
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import a02
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a02.writable import WRITABLE
from odoo.exceptions import AccessError, UserError, ValidationError

_SEQ = itertools.count(1)
GUARD = "changes only through its workflow"


@pytest.fixture
def call():
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", SimpleNamespace(env=env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


@contextmanager
def _refused(env, exc=(UserError, ValidationError), match=None):
    """Expect ``exc``; the failed operation is rolled back (flushing savepoint)."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info
    env.invalidate_all()


@pytest.fixture
def m04(odoo_env):
    env = odoo_env
    n = next(_SEQ)
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "M4P%d" % n, "legal_name": "M04 P0 Entity %d" % n, "company_id": env.company.id}
    )

    def branch(code):
        return env["fix.branch"].create(
            {
                "name": "M04 P0 %s" % code,
                "code": "%s%d" % (code, n),
                "entity_id": entity.id,
                "operating_unit_id": ou.id,
            }
        )

    Users = env["res.users"].with_context(no_reset_password=True)

    def user(login, *groups):
        vals = {
            "name": login,
            "login": "a02.m04.%s.%d@p0.test" % (login, n),
            "group_ids": [
                (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
            ],
        }
        if "assigned_operating_unit_ids" in Users._fields:
            vals["assigned_operating_unit_ids"] = [(6, 0, [ou.id])]
        if (
            "operating_unit_ids" in Users._fields
            and "assigned_operating_unit_ids" not in Users._fields
        ):
            vals["operating_unit_ids"] = [(6, 0, [ou.id])]
        if "default_operating_unit_id" in Users._fields:
            vals["default_operating_unit_id"] = ou.id
        u = Users.create(vals)
        emp = env["hr.employee"].create({"name": login + " (emp)", "user_id": u.id})
        return u, emp

    cashier, cashier_emp = user("cashier", "cd_front_desk.group_fd_cashier")
    cashier2, cashier2_emp = user("cashier2", "cd_front_desk.group_fd_cashier")
    manager, _m = user("manager", "cd_front_desk.group_fd_branch_manager")
    # a manager who also works the till: SoD still applies to her own drawer
    manager_cashier, manager_cashier_emp = user(
        "mgrcash", "cd_front_desk.group_fd_branch_manager", "cd_front_desk.group_fd_cashier"
    )
    approver, _a = user("approver", "cd_front_desk.group_fd_refund_approver")
    plain, _p = user("plain")
    product = env["product.product"].create(
        {"name": "M04 P0 screen guard", "list_price": 1000.0, "type": "consu"}
    )
    customer = env["res.partner"].create({"name": "M04 P0 customer", "phone": "+8801700000404"})
    brand = env["fix.brand"].create({"name": "M04P0Brand%d" % n, "code": "M4B%d" % n})
    dmodel = env["fix.device.model"].create({"name": "M04P0 Phone", "brand_id": brand.id})
    device = env["fix.device"].create(
        {
            "device_model_id": dmodel.id,
            "owner_id": customer.id,
            "serial_number": "SN-M04P0-%d" % n,
        }
    )
    signature = env["ir.attachment"].create({"name": "signed-receipt.png", "raw": b"signed"})
    ns = SimpleNamespace(
        env=env,
        ou=ou,
        branch=branch("MA"),
        branch2=branch("MB"),
        cashier=cashier,
        cashier_emp=cashier_emp,
        cashier2=cashier2,
        cashier2_emp=cashier2_emp,
        manager=manager,
        manager_cashier=manager_cashier,
        manager_cashier_emp=manager_cashier_emp,
        approver=approver,
        plain=plain,
        product=product,
        customer=customer,
        device=device,
        signature=signature,
    )

    def shift(as_user=None, branch=None, opening=5000.0, operator=None):
        return (
            env["fix.cash.shift"]
            .with_user(as_user or cashier)
            .create(
                {
                    "branch_id": (branch or ns.branch).id,
                    "operating_unit_id": ou.id,
                    "operator_id": (operator or cashier_emp).id,
                    "opening_float": opening,
                }
            )
        )

    def sale(shift_rec=None, qty=1, price=1000.0, method="cash", as_user=None, branch=None):
        return (
            env["fix.counter.sale"]
            .with_user(as_user or cashier)
            .create(
                {
                    "shift_id": shift_rec.id if shift_rec else False,
                    "branch_id": (branch or ns.branch).id,
                    "operating_unit_id": ou.id,
                    "product_id": product.id,
                    "quantity": qty,
                    "unit_price": price,
                    "payment_method": method,
                }
            )
        )

    def count(shift_rec, **denoms):
        shift_rec.write({"denom_%s_count" % k[1:]: v for k, v in denoms.items()})
        shift_rec.action_submit_blind_count()

    def as_(user_rec, rec):
        return rec.with_user(user_rec)

    def intake(as_user=None, **vals):
        base = {
            "branch_id": ns.branch.id,
            "operating_unit_id": ou.id,
            "customer_id": customer.id,
            "fault_description": "screen dead",
        }
        base.update(vals)
        return env["fix.walkin.intake"].with_user(as_user or cashier).create(base)

    def token(as_user=None, **vals):
        base = {"branch_id": ns.branch.id, "operating_unit_id": ou.id, "service_type": "drop_off"}
        base.update(vals)
        return env["fix.token.queue"].with_user(as_user or cashier).create(base)

    ns.shift, ns.sale, ns.count, ns.as_, ns.intake, ns.token = (
        shift,
        sale,
        count,
        as_,
        intake,
        token,
    )
    return ns


def _reconciled(m, s):
    """Count a balanced drawer and reconcile it as the manager."""
    total = int(s.sudo().expected_closing)
    m.count(s, d1000=total // 1000, d500=(total % 1000) // 500, d100=(total % 500) // 100)
    s.action_confirm_closed()
    m.as_(m.manager, s).action_reconcile()
    assert s.sudo().state == "reconciled"


# ============================================================ cash shift (A1)


def test_p04_01_cashier_cannot_forge_takings_or_count(m04):
    """P04-01: the cashier zeroed BDT 3,000 of takings and typed her count."""
    m = m04
    s = m.shift()
    m.sale(s, qty=3).action_confirm()
    assert s.cash_payments == 3000.0 and s.expected_closing == 8000.0
    for vals in (
        {"cash_payments": 0.0},
        {"cash_refunds": 999.0},
        {"cash_advances": 3000.0},
        {"field_cash_deposited": -3000.0},
        {"closing_counted": 5000.0},
        {"blind_count_submitted": True},
        {"reconciled_by": m.cashier.id},
        {"closed_at": fields.Datetime.now()},
    ):
        with _refused(m.env, UserError, GUARD):
            s.write(vals)
    s.invalidate_recordset()
    assert (s.cash_payments, s.closing_counted) == (3000.0, 0.0)


def test_p04_01_p03_write_of_drawer_totals_is_refused(m04, call):
    m = m04
    s = m.shift()
    res = call(
        m.env(user=m.cashier.id),
        "model_write",
        model="fix.cash.shift",
        record_id=s.id,
        values={"cash_payments": 0.0, "closing_counted": 5000.0},
    )
    assert "error" in res, res
    s.invalidate_recordset()
    assert s.closing_counted == 0.0
    # the legitimate form save (denominations) still works
    res = call(
        m.env(user=m.cashier.id),
        "model_write",
        model="fix.cash.shift",
        record_id=s.id,
        values={"denom_1000_count": 5},
    )
    assert res.get("id") == s.id, res


def test_p04_02_reconcile_without_a_count_is_refused(m04):
    """P04-02 / BRU-FRD-02: a BDT 5,000 drawer 'counted 0' reconciled."""
    m = m04
    s = m.shift()
    s.action_close_shift()
    with _refused(m.env, UserError, "no count"):
        m.as_(m.manager, s).action_reconcile()
    with _refused(m.env, UserError, "blind denomination count"):
        s.action_confirm_closed()
    assert s.sudo().state == "counting"
    # legitimate: count, confirm, reconcile by a manager
    _reconciled(m, s)
    assert s.sudo().reconciled_by == m.manager


def test_blind_count_does_not_reveal_the_variance(m04):
    """M04-11: the count gate told the cashier her drawer was short."""
    m = m04
    s = m.shift()
    s.action_close_shift()
    assert s.variance == 0.0  # nothing counted yet: no hint of the expected figure
    m.count(s, d1000=1)  # BDT -4,000: accepted silently
    assert s.sudo().blind_count_submitted and s.sudo().counted_by == m.cashier
    assert s.sudo().variance == -4000.0


def test_p04_03_cashier_cannot_sign_off_her_own_variance(m04, call):
    """P04-03 / -03b: the cashier signed off her own -1,000 variance."""
    m = m04
    s = m.shift()
    m.count(s, d1000=4)  # -1,000
    with _refused(m.env, UserError, GUARD):
        s.write({"supervisor_variance_approved_by": m.cashier.id})
    with _refused(m.env, UserError, "Only a Branch Manager"):
        s.action_approve_variance()
    res = call(
        m.env(user=m.cashier.id),
        "model_write",
        model="fix.cash.shift",
        record_id=s.id,
        values={"supervisor_variance_approved_by": m.cashier.id},
    )
    assert "error" in res, res
    res = call(
        m.env(user=m.cashier.id),
        "model_action",
        model="fix.cash.shift",
        ids=[s.id],
        method="action_approve_variance",
    )
    assert res["success"] is False and "Branch Manager" in res["error"], res
    s.action_confirm_closed()
    with _refused(m.env, UserError, "Only a Branch Manager"):
        s.action_reconcile()
    assert not s.sudo().supervisor_variance_approved_by
    assert s.sudo().state == "closed"


def test_p04_03_manager_cannot_approve_or_reconcile_her_own_drawer(m04):
    """BRU-FRD-11: the person who handled the cash cannot approve or reconcile it."""
    m = m04
    s = m.shift(as_user=m.manager_cashier, operator=m.manager_cashier_emp)
    mc = m.as_(m.manager_cashier, s)
    mc.write({"denom_1000_count": 3})
    mc.action_submit_blind_count()  # -2,000
    with _refused(m.env, UserError, "BRU-FRD-11"):
        mc.action_approve_variance()
    mc.action_confirm_closed()
    with _refused(m.env, UserError, "BRU-FRD-11"):
        mc.action_reconcile()
    # legitimate: an independent manager approves the exact variance, then reconciles
    other = m.as_(m.manager, s)
    other.action_approve_variance()
    assert (s.sudo().supervisor_variance_approved_by, s.sudo().variance_approved_amount) == (
        m.manager,
        -2000.0,
    )
    other.action_reconcile()
    assert (s.sudo().state, s.sudo().reconciled_by) == ("discrepancy", m.manager)


def test_p04_04_approval_is_pinned_and_a_recount_voids_it(m04):
    """P04-04: approved at -50, recounted to -5,000, reconciled."""
    m = m04
    s = m.shift()
    m.count(s, d1000=3, d500=1, d100=4)  # 3,900: -1,100
    m.as_(m.manager, s).action_approve_variance()
    assert s.sudo().variance_approved_amount == -1100.0
    s.write({"denom_1000_count": 0, "denom_500_count": 0, "denom_100_count": 0})
    s.action_submit_blind_count()  # recount: 0, -5,000
    assert not s.sudo().supervisor_variance_approved_by  # void
    s.action_confirm_closed()
    with _refused(m.env, ValidationError, "must approve this variance"):
        m.as_(m.manager, s).action_reconcile()
    # within tolerance, nothing to approve
    s2 = m.shift(branch=m.branch2)
    m.count(s2, d1000=4, d500=1, d100=4, d50=1)  # 4,950: -50
    with _refused(m.env, UserError, "within the BDT 100.00"):
        m.as_(m.manager, s2).action_approve_variance()
    m.as_(m.manager, s2).action_reconcile()
    assert s2.sudo().state == "discrepancy"


def test_variance_tolerance_is_a_config_parameter(m04):
    m = m04
    m.env["ir.config_parameter"].set_param("cd_front_desk.variance_tolerance_bdt", "10")
    s = m.shift()
    m.count(s, d1000=4, d500=1, d100=4, d50=1)  # -50 > 10
    with _refused(m.env, ValidationError, "exceeds BDT 10.00"):
        m.as_(m.manager, s).action_reconcile()


def test_p04_05_state_cannot_be_written_directly(m04, call):
    """P04-05: the cashier wrote 'reconciled' on an open shift."""
    m = m04
    s = m.shift()
    with _refused(m.env, UserError, GUARD):
        s.write({"state": "reconciled"})
    res = call(
        m.env(user=m.cashier.id),
        "model_write",
        model="fix.cash.shift",
        record_id=s.id,
        values={"state": "reconciled", "closing_counted": 5000.0},
    )
    assert "error" in res, res
    s.invalidate_recordset()
    assert s.state == "open"
    # a shift cannot be born late either
    with _refused(m.env, UserError, GUARD):
        m.env["fix.cash.shift"].with_user(m.cashier).create(
            {
                "branch_id": m.branch2.id,
                "operating_unit_id": m.ou.id,
                "operator_id": m.cashier_emp.id,
                "opening_float": 100.0,
                "state": "reconciled",
            }
        )


def test_p04_06_no_sale_posts_into_a_closed_or_reconciled_shift(m04):
    """P04-06: a sale confirmed onto a reconciled shift moved it to -970."""
    m = m04
    s = m.shift()
    _reconciled(m, s)
    late = m.sale(s, price=1000.0)
    with _refused(m.env, UserError, "only to an open shift"):
        late.action_confirm()
    assert s.sudo().variance == 0.0 and late.state == "draft"
    # frozen: the float and the count of a reconciled shift do not move
    with _refused(m.env, UserError, "can no longer be changed"):
        s.write({"opening_float": 1.0})
    with _refused(m.env, UserError, "can no longer be changed"):
        s.write({"denom_1000_count": 9})
    s.write({"bank_deposit_slip_no": "SLIP-1"})  # banking follows the close
    assert "opening_float" in s._fix_form_locked_fields()


def test_cash_sale_without_shift_goes_to_the_open_shift(m04):
    m = m04
    orphan = m.sale(None)
    with _refused(m.env, UserError, "no open cash shift"):
        orphan.action_confirm()
    s = m.shift()
    orphan.action_confirm()
    assert orphan.shift_id == s and s.cash_payments == 1000.0
    assert orphan.confirmed_by == m.cashier


def test_one_open_shift_per_branch(m04):
    """M04-10 / BRU-FRD-01."""
    m = m04
    s = m.shift()
    with _refused(m.env, ValidationError, "BRU-FRD-01"):
        m.shift(as_user=m.cashier2, operator=m.cashier2_emp)
    # another branch may open; once the first count is confirmed a new one may too
    m.shift(as_user=m.cashier2, branch=m.branch2, operator=m.cashier2_emp)
    m.count(s, d1000=5)
    s.action_confirm_closed()
    assert m.shift(as_user=m.cashier2, operator=m.cashier2_emp).state == "open"


def test_one_open_shift_per_operator_scope(m04):
    m = m04
    m.env["ir.config_parameter"].set_param("cd_front_desk.open_shift_scope", "operator")
    m.shift()
    m.shift(as_user=m.cashier2, operator=m.cashier2_emp)  # a second counter, allowed
    with _refused(m.env, ValidationError, "BRU-FRD-01"):
        m.shift()


def test_plain_user_cannot_open_or_edit_a_shift(m04):
    """M04-6: every internal user had RWC on the cash models."""
    m = m04
    with _refused(m.env, AccessError):
        m.shift(as_user=m.plain)
    s = m.shift()
    with _refused(m.env, AccessError):
        m.as_(m.plain, s).write({"denom_1000_count": 1})
    assert m.as_(m.plain, s).read(["state"])  # reading stays open


def test_field_cash_posts_through_the_shift_method(m04):
    """HS-08: the M02 settlement posts through _post_field_cash, open shift only."""
    m = m04
    s = m.shift()
    s._post_field_cash(1200.0)
    assert s.field_cash_deposited == 1200.0 and s.expected_closing == 6200.0
    with _refused(m.env, UserError, "positive"):
        s._post_field_cash(-5.0)
    s.action_close_shift()
    with _refused(m.env, UserError, "only to an open shift"):
        s._post_field_cash(10.0)


# ============================================================ counter sale


def test_p04_07_sale_state_cannot_be_forged(m04, call):
    """P04-07: /p03/model/write state=refunded; ORM state=confirmed."""
    m = m04
    s = m.shift()
    sale = m.sale(s)
    sale.action_confirm()
    res = call(
        m.env(user=m.cashier.id),
        "model_write",
        model="fix.counter.sale",
        record_id=sale.id,
        values={"state": "refunded"},
    )
    assert "error" in res, res
    sale2 = m.sale(s, qty=2)
    for vals in ({"state": "confirmed"}, {"refund_state": "refunded"}, {"total": 1.0}):
        with _refused(m.env, UserError, GUARD):
            sale2.write(vals)
    assert (sale.sudo().state, sale2.sudo().state, s.sudo().cash_payments) == (
        "confirmed",
        "draft",
        1000.0,
    )
    # what was sold is frozen once confirmed
    with _refused(m.env, UserError, "can no longer be changed"):
        sale.write({"quantity": 5})


def test_p04_08_negative_quantity_and_price_below_list(m04):
    """P04-08: qty -5 drained BDT 5,000; BDT 1 against a 1,000 list price."""
    m = m04
    s = m.shift()
    with _refused(m.env, ValidationError, "greater than zero"):
        m.sale(s, qty=-5)
    with _refused(m.env, ValidationError, "greater than zero"):
        m.sale(s, qty=0)
    cheap = m.sale(s, price=1.0)
    with _refused(m.env, UserError, "below the list price"):
        cheap.action_confirm()
    # the seller cannot approve her own price; a cashier is not a manager
    with _refused(m.env, UserError, "Only a Branch Manager"):
        cheap.action_approve_price_override()
    own = m.sale(s, price=900.0, as_user=m.manager_cashier)
    with _refused(m.env, UserError, "cannot approve its price"):
        m.as_(m.manager_cashier, own).action_approve_price_override()
    # legitimate: a manager approves BDT 900; the approval is pinned to it
    discounted = m.sale(s, price=900.0)
    m.as_(m.manager, discounted).action_approve_price_override()
    discounted.write({"unit_price": 800.0})
    with _refused(m.env, UserError, "below the list price"):
        discounted.action_confirm()
    discounted.write({"unit_price": 900.0})
    discounted.action_confirm()
    assert s.sudo().cash_payments == 900.0
    m.sale(s, price=1000.0).action_confirm()  # at list: no approval needed
    assert s.sudo().cash_payments == 1900.0


def test_p04_09_refund_needs_reason_and_an_independent_approver(m04, call):
    """P04-09: the seller refunded her own sale after reconcile, no reason."""
    m = m04
    s = m.shift()
    sale = m.sale(s)
    sale.action_confirm()
    with _refused(m.env, UserError, "reason code"):
        sale.action_request_refund()
    with _refused(m.env, UserError, "reason code"):
        sale.action_request_refund(reason="because")
    with _refused(m.env, UserError, "has no refund request"):
        m.as_(m.approver, sale).action_approve_refund()
    res = call(
        m.env(user=m.cashier.id),
        "model_action",
        model="fix.counter.sale",
        ids=[sale.id],
        method="action_request_refund",
        kwargs={"reason": "defective: glass cracked on fitting"},
    )
    assert res["success"], res
    assert (sale.refund_state, sale.refund_reason_code) == ("requested", "defective")
    # the seller (and requester) cannot approve; a cashier is not an approver
    with _refused(m.env, UserError, "Only a Refund Approver"):
        sale.action_approve_refund()
    with _refused(m.env, UserError, "Only a Refund Approver"):
        m.as_(m.cashier2, sale).action_approve_refund()
    # the drawer the sale went into is reconciled: the refund pays from the OPEN one
    _reconciled(m, s)
    with _refused(m.env, UserError, "no open cash shift"):
        m.as_(m.approver, sale).action_approve_refund()
    now_open = m.shift(as_user=m.cashier2, operator=m.cashier2_emp)
    m.as_(m.approver, sale).action_approve_refund()
    sale.invalidate_recordset()
    assert (sale.state, sale.refund_state, sale.refund_approved_by, sale.refund_shift_id) == (
        "refunded",
        "refunded",
        m.approver,
        now_open,
    )
    assert (s.sudo().cash_refunds, s.sudo().variance, s.sudo().state) == (0.0, 0.0, "reconciled")
    assert now_open.sudo().cash_refunds == 1000.0
    # only once
    with _refused(m.env, UserError, "Only confirmed sales"):
        m.as_(m.cashier2, sale).action_request_refund(reason="duplicate")


def test_seller_manager_cannot_approve_her_own_refund(m04):
    m = m04
    s = m.shift(as_user=m.manager_cashier, operator=m.manager_cashier_emp)
    sale = m.sale(s, as_user=m.manager_cashier)
    sale.action_confirm()
    m.as_(m.cashier, sale).action_request_refund(reason="wrong_item")
    with _refused(m.env, UserError, "cannot approve the"):
        sale.action_approve_refund()
    m.as_(m.manager, sale).action_approve_refund()
    assert sale.sudo().state == "refunded"


# ============================================================ intake (A6)


def test_p04_10a_intake_without_device_is_refused_in_plain_words(m04):
    """P04-10a / BRU-FRD-12: the hand-off died on a NotNullViolation."""
    m = m04
    it = m.intake(handover_method="signature", customer_signature_attachment_id=m.signature.id)
    with _refused(m.env, UserError, "BRU-FRD-12"):
        it.action_complete_handover()
    with _refused(m.env, UserError, "BRU-FRD-12"):
        it.action_submit_for_handover()
    assert it.state == "in_progress" and not it.service_order_id
    # a scanned, registered serial identifies the device
    it.write({"device_serial_input": m.device.serial_number})
    it.action_complete_handover()
    assert it.device_id == m.device and it.service_order_id.device_id == m.device


def test_p04_10b_handover_needs_the_customer_signature(m04):
    """P04-10b: handover_acknowledged was ticked True with no method or proof."""
    m = m04
    it = m.intake(device_id=m.device.id)
    with _refused(m.env, UserError, "acknowledgement"):
        it.action_complete_handover()
    it.write({"handover_method": "witness"})
    with _refused(m.env, UserError, "acknowledgement"):
        it.action_complete_handover()
    it.write({"handover_method": "signature"})
    with _refused(m.env, UserError, "signed intake receipt"):
        it.action_complete_handover()
    with _refused(m.env, UserError, GUARD):
        it.write({"handover_acknowledged": True})
    assert not it.handover_acknowledged
    it.write({"customer_signature_attachment_id": m.signature.id})
    it.action_complete_handover()
    assert (it.state, it.handover_acknowledged, it.service_order_id.state) == (
        "completed",
        True,
        "intake",
    )
    # what the customer acknowledged is frozen
    with _refused(m.env, UserError, "can no longer be changed"):
        it.write({"fault_description": "rewritten"})


def test_p04_11_state_write_cannot_complete_an_intake(m04, call):
    """P04-11: /p03/model/write state=completed closed an intake with no order."""
    m = m04
    it = m.intake(device_id=m.device.id)
    res = call(
        m.env(user=m.cashier.id),
        "model_write",
        model="fix.walkin.intake",
        record_id=it.id,
        values={"state": "completed"},
    )
    assert "error" in res, res
    for vals in ({"state": "completed"}, {"handover_complete": fields.Datetime.now()}):
        with _refused(m.env, UserError, GUARD):
            it.write(vals)
    it.invalidate_recordset()
    assert it.state == "in_progress" and not it.service_order_id


# ============================================================ token (A6)


def test_p04_12_token_state_and_stamps_cannot_be_written(m04):
    """P04-12: a waiting token was written 'completed' with no call or serve."""
    m = m04
    t = m.token()
    for vals in (
        {"state": "completed"},
        {"called_at": fields.Datetime.now()},
        {"supervisor_escalated": True},
        {"wait_sla_breached": True},
    ):
        with _refused(m.env, UserError, GUARD):
            t.write(vals)
    # the legitimate lifecycle, as the non-admin cashier
    t.action_call()
    t.action_serving()
    t.action_complete()
    assert t.state == "completed" and t.called_at and t.served_at


def test_wait_sla_cron_escalates_breaches(m04):
    """M04-9: no cron; a stored now() compute froze; 5 breached, 0 escalated."""
    m = m04
    env = m.env
    cron = env.ref("cd_front_desk.ir_cron_token_wait_sla")
    assert cron.active and "_cron_evaluate_wait_sla" in cron.code
    m.branch.manager_id = m.manager.id
    old = env["fix.token.queue"].create(  # superuser: back-dated issue time
        {
            "branch_id": m.branch.id,
            "operating_unit_id": m.ou.id,
            "issued_at": fields.Datetime.now() - timedelta(minutes=10),
        }
    )
    fresh = m.token()
    assert old.wait_seconds >= 600  # live, not frozen at the last write
    assert not old.wait_sla_breached
    env["fix.token.queue"]._cron_evaluate_wait_sla()
    old.invalidate_recordset()
    assert (old.wait_sla_breached, old.supervisor_escalated, bool(old.escalated_at)) == (
        True,
        True,
        True,
    )
    assert not fresh.sudo().wait_sla_breached
    assert old.activity_ids.filtered(lambda a: a.user_id == m.manager)
    events = env["fix.event.outbox"].search(
        [("aggregate", "=", "fix.token.queue"), ("aggregate_id", "=", old.id)]
    )
    assert "token.sla_breached" in events.mapped("event_type")
    # escalated once
    env["fix.token.queue"]._cron_evaluate_wait_sla()
    assert len(old.activity_ids) == 1


# ============================================================ P03 surface


def test_p03_surface_offers_the_new_actions_and_no_workflow_field(m04):
    shift_actions = a02.SURFACES["fix.cash.shift"]["actions"]
    sale_actions = a02.SURFACES["fix.counter.sale"]["actions"]
    assert {"action_submit_blind_count", "action_approve_variance"} <= shift_actions
    assert {"action_request_refund", "action_approve_refund", "action_approve_price_override"} <= (
        sale_actions
    )
    assert "action_refund" not in sale_actions
    env = m04.env
    for model in ("fix.cash.shift", "fix.token.queue", "fix.walkin.intake"):
        guarded = env[model].browse()._fix_guarded_fields()
        assert not guarded & set(WRITABLE[model]), model
        assert set(WRITABLE[model]) <= set(env[model]._fields), model  # no phantoms
    for name in ("payment_trx_ref", "vat_amount", "invoice_attachment_id"):
        assert name not in WRITABLE["fix.counter.sale"]
