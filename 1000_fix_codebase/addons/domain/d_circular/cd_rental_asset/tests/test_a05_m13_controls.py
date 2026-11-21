# A05 workflow audit, M13 Rental (cd_rental_asset): the controls the A05 probes
# (working/A05_evidence/probes/m13/probe_m13.py) found open, each attacked as
# a NON-ADMIN user three ways where it applies - the wrong transition, a plain
# write() (what JSON-RPC does) and /p03/model/write - and the legitimate path
# proved to still work. The superuser is trusted by the field guard and would
# hide a gap, so every attack runs as a user created here. The odoo_env
# fixture rolls the transaction back.
import itertools
import types
from datetime import timedelta
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_service_order.models import fix_otp_util
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
RES = "fix.rental.reservation"
SN = "A05M13T-SN-0001"
_SEQ = itertools.count(1)


# --------------------------------------------------------------------------- fixtures
def _branch(env):
    """A booking branch that belongs to an operating unit (the GL posting's
    branch dimension must match the unit)."""
    branch = env["fix.branch"].search([("operating_unit_id", "!=", False)], limit=1)
    if branch:
        return branch
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].search([], limit=1) or env["fix.entity"].create(
        {"legal_name": "A05 M13T Entity", "code": "A5M13TE", "company_id": env.company.id}
    )
    return env["fix.branch"].create(
        {
            "name": "A05 M13T Branch",
            "code": "A5M13T-BR",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )


def _user(env, login, groups=()):
    n = next(_SEQ)
    ou = _branch(env).operating_unit_id
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "%s %d" % (login, n),
                "login": "a05m13t.%s.%d@a05.test" % (login, n),
                "group_ids": [(6, 0, ids)],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


# M13 capture pass 2 (2026-11-19): a rental needs a party with a verified M33
# identity (BRU-RNT-20) and photographed condition reports (BRU-RNT-01).
_PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="


def _kyc(env, partner):
    env["fix.identity.document"].sudo().create(
        {"partner_id": partner.id, "document_type": "nid_10", "verification_status": "verified"}
    )
    return partner


def _photo(env, condition, view="front"):
    att = (
        env["ir.attachment"]
        .sudo()
        .create({"name": "%s.png" % view, "datas": _PNG, "mimetype": "image/png"})
    )
    return env["fix.rental.condition.photo"].create(
        {"condition_id": condition.id, "attachment_id": att.id, "view_code": view}
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env, codes=[])
    x.today = fields.Date.context_today(env[RES])
    x.branch = _branch(env)
    x.ou = x.branch.operating_unit_id
    x.clerk = _user(env, "clerk")
    x.clerk2 = _user(env, "clerk2")
    x.inspector = _user(env, "inspector")
    x.t1 = _user(env, "t1", ["cd_entity_config.group_dofa_tier_1"])
    x.t1b = _user(env, "t1b", ["cd_entity_config.group_dofa_tier_1"])
    x.t2 = _user(env, "t2", ["cd_entity_config.group_dofa_tier_2"])
    # A02 pass 2 review: the data lab records the wipe, a verifier verifies it
    x.wipe_tech = _user(env, "wipetech", ["cd_data_case.group_data_recovery_operator"])
    x.wipe_verifier = _user(env, "wipeverifier", ["cd_data_case.group_wipe_verifier"])
    x.fleet = _user(env, "fleet", ["cd_rental_asset.group_rental_fleet_manager"])
    x.csh = _user(env, "csh", ["cd_rental_asset.group_rental_csh"])
    x.cfo = _user(env, "cfo", ["cd_rental_asset.group_rental_cfo"])
    x.customer = _kyc(
        env, env["res.partner"].create({"name": "A05 M13T Customer", "phone": "01700001302"})
    )
    tmpl = env["product.template"].create({"name": "A05M13T Camera rental"})
    item = env["fix.catalogue.item"].create({"product_tmpl_id": tmpl.id})
    x.sku = env["fix.rental.sku"].create(
        {"catalogue_item_id": item.id, "daily_rate": 1000, "security_deposit": 5000}
    )
    x.asset = env["fix.rental.asset"].create(
        {
            "name": "A05M13T-CAM-1",
            "rental_sku_id": x.sku.id,
            "serial_no": SN,
            "category": "camera",
            "purchase_cost": 100000,
            "acquisition_date": x.today - timedelta(days=100),
            "operating_unit_id": x.ou.id,
        }
    )
    # owner D8: the deposit is max(SKU floor, book value x tier rate); these
    # suites are about other controls, so the value rate stays under the floor
    env["ir.config_parameter"].set_param("cd_rental_asset.deposit_rate_pct.standard", "5")
    x.tech = env["hr.employee"].create({"name": "A05M13T Technician"})
    brand = env["fix.brand"].create({"name": "A05M13TBrand", "code": "A5M13T"})
    model = env["fix.device.model"].create({"name": "A05M13T model", "brand_id": brand.id})
    x.device = env["fix.device"].create({"device_model_id": model.id})

    def fake_dispatch(phone, code, ttl, language="bn"):
        x.codes.append(code)

    with mock.patch.object(fix_otp_util, "dispatch_otp", fake_dispatch):
        yield x


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()
    mw = getattr(g.P03GenericApiController.model_write, "original_endpoint", None)
    ma = getattr(g.P03GenericApiController.model_action, "original_endpoint", None)
    mw = mw or g.P03GenericApiController.model_write
    ma = ma or g.P03GenericApiController.model_action
    req = types.SimpleNamespace(env=c.env(user=c.clerk.id))
    old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)
    g.request = req
    s.request = req
    try:
        yield types.SimpleNamespace(
            write=lambda **kw: mw(ctl, **kw), action=lambda **kw: ma(ctl, **kw)
        )
    finally:
        g.request, s.request = old_g, old_s


def res(c, user=None, **kw):
    vals = {
        "customer_id": c.customer.id,
        "rental_sku_id": c.sku.id,
        "rental_asset_id": c.asset.id,
        "operating_unit_id": c.ou.id,
        "branch_id": c.branch.id,
        "date_from": c.today,
        "date_to": c.today + timedelta(days=2),
        "deposit_collected": 5000,
        "stamp_duty_cert_no": "STAMP-0001",
    }
    vals.update(kw)
    return c.env[RES].with_user(user or c.clerk).create(vals)


def sign(c, r):
    r.action_send_agreement()
    assert r.action_sign_agreement(code=c.codes[-1]) == {"verified": True}
    return r


def report(c, r, report_type, user=None):
    cond = (
        c.env["fix.rental.condition"]
        .with_user(user or c.clerk)
        .create({"reservation_id": r.id, "report_type": report_type, "grade": "a"})
    )
    _photo(cond.env, cond)
    return cond


def walk(c, r, upto):
    """The legitimate path, as the record's user, up to and including `upto`."""
    steps = [
        ("sign", lambda: sign(c, r)),
        ("action_reserve", r.action_reserve),
        ("pre", lambda: report(c, r, "pre_delivery", r.env.user)),
        ("action_deliver", r.action_deliver),
        ("action_activate", r.action_activate),
        ("action_return", r.action_return),
        ("post", lambda: report(c, r, "post_return", r.env.user)),
        ("action_assess_damage", r.action_assess_damage),
    ]
    for name, step in steps:
        step()
        if name == upto:
            break
    return r


def close(c, r, user=None):
    """XC-22: the settlement is made by someone other than the deposit taker."""
    return r.with_user(user or c.clerk2).action_close()


def damage(c, r, user=None, **kw):
    vals = {"reservation_id": r.id, "description": "Cracked lens", "cost": 3000}
    vals.update(kw)
    return c.env["fix.rental.damage"].with_user(user or c.inspector).create(vals)


def inbox_approve(record, approver):
    task = record.approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == approver
    )
    assert task, "no inbox task for %s" % approver.name
    task.with_user(approver).action_approve()


def approve_charge(c, dmg, approver=None, requester=None):
    dmg.with_user(requester or c.clerk).action_request_charge_approval()
    inbox_approve(dmg.charge_approval_id, approver or c.t1)


def _other_ou(c):
    env = c.env
    other = env["operating.unit"].search([("id", "!=", c.ou.id)], limit=1)
    return other or env["operating.unit"].create(
        {"name": "A05M13T Other OU", "code": "A5M13TOU", "partner_id": env.company.partner_id.id}
    )


def ledger(c, r):
    return c.env["fix.rental.deposit"].sudo().search([("reservation_id", "=", r.id)], order="id")


def moves(c, r, kind="collect"):
    return c.env["account.move"].sudo().search([("ref", "=", "RDEP %s — %s" % (r.name, kind))])


# --------------------------------------------------------------- E4 / M13-5 availability
def test_overlap_born_active_is_refused_for_user_and_superuser(c):
    walk(c, res(c), "action_reserve")
    with pytest.raises(REFUSED):
        res(c, user=c.clerk2, state="active")
    # the availability constraint holds even for a trusted data load
    with pytest.raises(ValidationError, match="already reserved"), c.env.cr.savepoint():
        c.env[RES].create(
            {
                "customer_id": c.customer.id,
                "rental_asset_id": c.asset.id,
                "date_from": c.today,
                "date_to": c.today + timedelta(days=1),
                "state": "active",
            }
        )


def test_device_double_booking_by_write_and_p03_is_refused(c, p03):
    walk(c, res(c, rental_asset_id=False, device_id=c.device.id), "action_reserve")
    r2 = res(c, user=c.clerk2, rental_asset_id=False, device_id=c.device.id)
    with pytest.raises(REFUSED):
        r2.write({"state": "active"})
    out = p03.write(model=RES, record_id=r2.id, values={"state": "active"})
    r2.invalidate_recordset()
    assert out.get("error") and r2.state == "draft"
    sign(c, r2.with_user(c.clerk2))
    with pytest.raises(UserError, match="already reserved"):
        r2.with_user(c.clerk2).action_reserve()


def test_sku_pool_capacity_and_turnaround_padding(c):
    first = walk(c, res(c, rental_asset_id=False), "action_reserve")
    assert first.state == "reserved"
    second = sign(c, res(c, rental_asset_id=False))
    with pytest.raises(UserError, match="pool is fully booked"):
        second.action_reserve()
    # a fleet unit is blocked for 1 turnaround day after a booking...
    first.with_user(c.clerk2).action_cancel()  # XC-22: not the deposit taker
    walk(c, res(c), "action_reserve")
    nextday = sign(
        c, res(c, date_from=c.today + timedelta(days=3), date_to=c.today + timedelta(days=4))
    )
    with pytest.raises(UserError, match="turnaround"):
        nextday.action_reserve()
    # ...and free the day after that
    later = sign(
        c, res(c, date_from=c.today + timedelta(days=4), date_to=c.today + timedelta(days=5))
    )
    later.action_reserve()
    assert later.state == "reserved"


def test_reserve_needs_a_unit_the_sku_limits_and_the_sku_deposit(c):
    with pytest.raises(UserError, match="names no fleet asset"):
        res(c, rental_asset_id=False, rental_sku_id=False).action_reserve()
    c.sku.max_rental_days = 3
    with pytest.raises(UserError, match="at most 3 rental days"):
        res(c, date_to=c.today + timedelta(days=29)).action_reserve()
    c.sku.max_rental_days = 0
    with pytest.raises(UserError, match="required deposit is 5000"):
        res(c, deposit_collected=0).action_reserve()
    # owner D8: the old switch no longer waives the deposit
    c.env["ir.config_parameter"].set_param("cd_rental_asset.enforce_sku_deposit", "0")
    with pytest.raises(UserError, match="required deposit"):
        res(c, deposit_collected=0, stamp_duty_cert_no=False).action_reserve()


# --------------------------------------------------------- E8 / M13-7 customer signature
def test_agreement_cannot_be_forged_by_write_create_or_p03(c, p03):
    r = res(c)
    with pytest.raises(REFUSED):
        r.write(
            {
                "agreement_state": "signed",
                "signature_ref": "TYPED",
                "signed_at": fields.Datetime.now(),
            }
        )
    with pytest.raises(REFUSED):
        res(c, signature_ref="TYPED-AT-CREATE")
    out = p03.write(
        model=RES, record_id=r.id, values={"agreement_state": "signed", "signature_ref": "X"}
    )
    r.invalidate_recordset()
    assert out.get("error") and r.agreement_state == "draft"


def test_agreement_is_signed_only_with_the_customers_code(c):
    r = res(c)
    with pytest.raises(UserError, match="only be signed after it was sent"):
        r.action_sign_agreement(code="123456")
    r.action_send_agreement()
    assert r.agreement_state == "sent"
    with pytest.raises(UserError, match="signed by the customer"):
        r.action_sign_agreement()
    wrong = "000000" if c.codes[-1] != "000000" else "111111"
    assert r.action_sign_agreement(code=wrong)["verified"] is False
    assert r.agreement_state == "sent" and r.agreement_otp_attempts == 1
    assert r.action_sign_agreement(code=c.codes[-1]) == {"verified": True}
    assert r.agreement_state == "signed" and r.signed_at
    assert r.signature_ref.startswith("OTP:017*****302:")


def test_terms_freeze_once_sent_and_reset_reopens_them(c, p03):
    r = res(c)
    r.action_send_agreement()
    with pytest.raises(REFUSED, match="terms of the agreement"):
        r.write({"liability_cap_amount": 1})
    out = p03.write(model=RES, record_id=r.id, values={"liability_cap_amount": 1})
    assert out.get("error")
    r.action_reset_agreement()
    r.write({"liability_cap_amount": 900})
    sign(c, r)
    with pytest.raises(REFUSED):
        r.write({"daily_rate": 1, "deposit_collected": 0, "liability_cap_amount": 0})
    with pytest.raises(UserError, match="signed agreement is final"):
        r.action_reset_agreement()


def test_no_handover_without_signature_or_pre_delivery_report(c):
    r = res(c)
    r.action_reserve()
    report(c, r, "pre_delivery")
    with pytest.raises(UserError, match="has not signed"):
        r.action_deliver()
    r2 = sign(c, res(c, rental_asset_id=False, device_id=c.device.id))
    r2.action_reserve()
    with pytest.raises(UserError, match="pre-delivery condition report"):
        r2.action_deliver()
    assert r2.state == "reserved"


# ------------------------------------------------------- E8 / M13-16 condition reports
def test_condition_reports_belong_to_their_stage(c):
    r = walk(c, res(c), "action_reserve")
    with pytest.raises(REFUSED, match="post-return condition report is written"):
        report(c, r, "post_return")
    pre = report(c, r, "pre_delivery")
    walk_on = [r.action_deliver, r.action_activate, r.action_return]
    for step in walk_on:
        step()
    with pytest.raises(REFUSED, match="is final"):
        pre.with_user(c.clerk).write({"grade": "d"})
    with pytest.raises(UserError, match="post-return condition report"):
        r.action_assess_damage()
    report(c, r, "post_return")
    r.action_assess_damage()
    assert r.state == "damage_assess"


# ------------------------------------------------------ E3 / M13-6 / M13-17 state machine
def test_state_cannot_be_written_and_transitions_are_ordered(c, p03):
    r = walk(c, res(c), "action_activate")
    with pytest.raises(REFUSED):
        r.write({"state": "closed"})
    out = p03.write(model=RES, record_id=r.id, values={"state": "closed"})
    assert out.get("error")
    r2 = walk(c, res(c, rental_asset_id=False, device_id=c.device.id), "action_reserve")
    with pytest.raises(UserError, match="Activate from delivered"):
        r2.action_activate()
    with pytest.raises(REFUSED):
        r.write({"late_fee": 1})
    with pytest.raises(REFUSED):
        damage(c, r2)  # damage on a unit never returned


def test_closed_rental_and_its_damage_are_final(c):
    r = walk(c, res(c), "action_assess_damage")
    dmg = damage(c, r)
    approve_charge(c, dmg)
    close(c, r)
    assert r.state == "closed"
    with pytest.raises(REFUSED, match="final"):
        dmg.with_user(c.inspector).write({"cost": 0})
    with pytest.raises(REFUSED):
        r.write({"special_terms": "rewritten after close"})


# ------------------------------------------------------- E6 / M13-1 / M13-2 deposit GL
def test_rental_clerk_posts_the_deposit_and_closes_without_accounting_rights(c):
    r = walk(c, res(c), "action_reserve")
    (row,) = ledger(c, r)
    assert row.gl_state == "posted" and row.journal_entry_id, row.gl_note
    walk_rest = [
        lambda: report(c, r, "pre_delivery"),
        r.action_deliver,
        r.action_activate,
        r.action_return,
        lambda: report(c, r, "post_return"),
        r.action_assess_damage,
    ]
    for step in walk_rest:
        step()
    close(c, r)
    refund = ledger(c, r).filtered(lambda d: d.kind == "refund")
    assert r.state == "closed" and refund.amount == 5000
    assert refund.gl_state == "refund_queued" and refund.payment_execution_id
    # A05 E10 / A08 hand-off: THE treasury request, pinned to this refund
    pay = refund.payment_execution_id
    assert pay.source_pinned and (pay.source_model, pay.source_id) == (refund._name, refund.id)
    assert (pay.partner_id, pay.amount) == (r.customer_id, 5000)


LIABILITY_PARAM = "cd_rental_asset.account_code.deposit_liability"


def test_refused_posting_leaves_no_move_and_repost_posts_once(c):
    params = c.env["ir.config_parameter"]
    params.set_param(LIABILITY_PARAM, "")
    r = sign(c, res(c))
    r.action_reserve()
    (row,) = ledger(c, r)
    assert row.gl_state == "failed" and LIABILITY_PARAM in row.gl_note
    assert not moves(c, r), "a refused posting left a journal entry behind"
    with pytest.raises(UserError, match="not posted to the General Ledger"):
        r.with_user(c.clerk2).action_cancel()
    params.set_param(LIABILITY_PARAM, "212000")
    row.with_user(c.clerk).action_repost_gl()
    assert row.gl_state == "posted"
    assert len(moves(c, r).filtered(lambda m: m.state == "posted")) == 1
    with pytest.raises(UserError, match="already carries"):
        row.with_user(c.clerk).action_repost_gl()


def test_repost_adopts_an_orphan_move_instead_of_posting_twice(c):
    from odoo.addons.cd_rental_asset.models.rental_gl import (
        post_rental_move,
        rental_account,
        tender_account,
    )

    env = c.env
    params = env["ir.config_parameter"]
    params.set_param(LIABILITY_PARAM, "")
    r = sign(c, res(c))
    r.action_reserve()
    (row,) = ledger(c, r)
    assert row.gl_state == "failed"
    params.set_param(LIABILITY_PARAM, "212000")
    # the legacy defect: a posted move from the refused attempt (M13-1 live orphans)
    company = r.company_id
    liability = rental_account(env, company, "deposit_liability")
    post_rental_move(
        env,
        r,
        row.date,
        "RDEP %s — collect" % r.name,
        [
            (tender_account(env, company, "cash"), "orphan", 5000.0, 0.0, r.customer_id),
            (liability, "orphan", 0.0, 5000.0, r.customer_id),
        ],
    )
    row.with_user(c.clerk).action_repost_gl()
    assert row.gl_state == "posted"
    assert len(moves(c, r).filtered(lambda m: m.state == "posted")) == 1


def test_ledger_is_immutable(c, p03):
    r = walk(c, res(c), "action_reserve")
    (row,) = ledger(c, r)
    row = row.with_user(c.clerk)
    for vals in (
        {"gl_state": "failed"},
        {"journal_entry_id": False},
        {"amount": 1},
        {"kind": "refund"},
    ):
        with pytest.raises(REFUSED):
            row.write(vals)
    with pytest.raises(REFUSED, match="cannot be typed"):
        c.env["fix.rental.deposit"].with_user(c.clerk).create(
            {"reservation_id": r.id, "kind": "refund", "amount": 50000}
        )
    out = p03.write(
        model="fix.rental.deposit",
        record_id=None,
        values={"reservation_id": r.id, "kind": "refund", "amount": 50000, "method": "bkash"},
    )
    assert out.get("error")
    out = p03.write(model="fix.rental.deposit", record_id=row.id, values={"gl_state": "failed"})
    assert out.get("error")
    with pytest.raises(REFUSED):
        row.write({"reference": "changed after posting"})


# ------------------------------------------------------- E6 / M13-3 refund from the ledger
def test_deposit_is_fixed_after_reserve_and_refund_is_the_ledger(c):
    r = walk(c, res(c), "action_reserve")
    with pytest.raises(REFUSED):
        r.write({"deposit_collected": 50000})
    walk_rest = [
        lambda: report(c, r, "pre_delivery"),
        r.action_deliver,
        r.action_activate,
        r.action_return,
        lambda: report(c, r, "post_return"),
        r.action_assess_damage,
    ]
    for step in walk_rest:
        step()
    close(c, r)
    refunds = ledger(c, r).filtered(lambda d: d.kind == "refund")
    assert sum(refunds.mapped("amount")) == 5000 == r.deposit_refunded


# ------------------------------------------------------------ E6 / M13-4 late fee once
@pytest.mark.parametrize("mode", ["invoice", "deposit"])
def test_late_fee_is_charged_once(c, mode):
    """A05 M13-03/M13-09: whatever the old settlement switch says, the late
    fee is invoiced once, as a VAT supply, and never taken from the deposit."""
    c.env["ir.config_parameter"].set_param("cd_rental_asset.late_fee_settlement", mode)
    r = res(c, date_from=c.today - timedelta(days=5), date_to=c.today - timedelta(days=3))
    walk(c, r, "action_assess_damage")
    assert r.late_fee == 3 * 1000 * 1.5
    close(c, r)
    with pytest.raises(UserError, match="already invoiced"):
        r.action_issue_rental_invoice()
    deducted = sum(ledger(c, r).filtered(lambda d: d.kind == "deduction").mapped("amount"))
    lines = r.billing_ids.mapped("invoice_id.line_ids")
    late = lines.filtered(lambda ln: "Late return fee" in (ln.description or ""))
    assert deducted == 0
    assert round(sum(late.mapped("taxable_amount")), 2) == r.late_fee
    assert late.vat_amount > 0  # M51 standard VAT on the late fee (owner D2)


def test_late_fee_grace_period(c):
    c.env["ir.config_parameter"].set_param("cd_rental_asset.late_fee_grace_days", "2")
    r = res(c, date_from=c.today - timedelta(days=5), date_to=c.today - timedelta(days=3))
    walk(c, r, "action_return")
    assert r.late_fee == 1 * 1000 * 1.5


# ---------------------------------------------- E5 / M13-8 damage charge approval (M63)
def test_damage_charge_needs_a_routed_approval_before_close(c, p03):
    r = walk(c, res(c), "action_assess_damage")
    dmg = damage(c, r, cost=4999)
    with pytest.raises(UserError, match="no granted charge approval"):
        close(c, r)
    dmg.with_user(c.clerk).action_request_charge_approval()
    approval = dmg.charge_approval_id
    with pytest.raises(UserError, match="approver's inbox"):
        approval.with_user(c.t1).action_dofa_approve()
    assert c.t1 in approval.approval_request_id.task_ids.mapped("assigned_user_id")
    inbox_approve(approval, c.t1)
    assert approval.dofa_approved and approval.approval_state == "approved"
    # raising the cost voids the approval
    dmg.with_user(c.inspector).write({"cost": 6000})
    assert not approval.dofa_approved
    with pytest.raises(UserError, match="no granted charge approval"):
        close(c, r)
    approve_charge(c, dmg)
    close(c, r)
    deduction = ledger(c, r).filtered(lambda d: d.kind == "deduction")
    assert deduction.amount == 5000 and deduction.damage_id == dmg
    assert r.excess_billed == 1000 and r.excess_invoice_id


def test_the_inspector_never_approves_their_own_charge(c):
    r = walk(c, res(c), "action_assess_damage")
    dmg = damage(c, r, user=c.t1b)  # the assessor holds tier 1
    dmg.with_user(c.clerk).action_request_charge_approval()
    assigned = dmg.charge_approval_id.approval_request_id.task_ids.mapped("assigned_user_id")
    assert c.t1b not in assigned and c.clerk not in assigned


def test_disputed_charge_holds_the_close_until_the_approver_resolves_it(c, p03):
    r = walk(c, res(c), "action_assess_damage")
    dmg = damage(c, r, disputed=True, dispute_reason="customer denies")
    with pytest.raises(REFUSED):
        dmg.with_user(c.inspector).write({"disputed": False})
    out = p03.write(model="fix.rental.damage", record_id=dmg.id, values={"disputed": False})
    assert out.get("error") and dmg.disputed
    with pytest.raises(UserError, match="disputed"):
        close(c, r)
    dmg.with_user(c.clerk).action_request_charge_approval()
    task = dmg.charge_approval_id.approval_request_id.task_ids.filtered(
        lambda t: t.assigned_user_id == c.t1
    )
    with pytest.raises(UserError, match="record the resolution"), c.env.cr.savepoint():
        task.with_user(c.t1).action_approve()
    dmg.with_user(c.inspector).write({"settlement_notes": "handover photos show no crack"})
    inbox_approve(dmg.charge_approval_id, c.t1)
    assert not dmg.disputed and dmg.dispute_resolved_by_id == c.t1
    close(c, r)
    assert r.state == "closed"
    # a dispute raised after the approval withdraws it
    r2 = walk(c, res(c, rental_asset_id=False, device_id=c.device.id), "action_assess_damage")
    d2 = damage(c, r2)
    approve_charge(c, d2)
    d2.with_user(c.clerk).action_raise_dispute(reason="second thoughts")
    assert d2.disputed and not d2.charge_approval_id.dofa_approved


# ------------------------------------------------- E5 / M13-9 waiver at the true amount
def test_waiver_fields_cannot_be_typed_and_the_waiver_is_routed(c, p03):
    r = walk(c, res(c), "action_assess_damage")
    dmg = damage(c, r, cost=20000)
    for vals in (
        {"recovered_amount": 20000},
        {"settled": True},
        {"waived": True, "waived_amount": 20000},
    ):
        with pytest.raises(REFUSED):
            dmg.with_user(c.inspector).write(vals)
    out = p03.write(model="fix.rental.damage", record_id=dmg.id, values={"recovered_amount": 20000})
    assert out.get("error") and dmg.recovered_amount == 0
    # the tier is the true amount at risk: nothing recovered, 20,000 -> tier 1
    assert dmg._dofa_current_tier() == "tier_1" and not dmg.settled
    with pytest.raises(UserError, match="approver's inbox"):
        dmg.with_user(c.t1).action_dofa_approve()
    with pytest.raises(REFUSED):
        dmg.with_user(c.clerk).action_waive()
    out = p03.action(model="fix.rental.damage", ids=[dmg.id], method="action_request_approval")
    assert out.get("success"), out
    assert c.inspector not in dmg.approval_request_id.task_ids.mapped("assigned_user_id")
    inbox_approve(dmg, c.t1)
    dmg.with_user(c.clerk).action_waive()
    assert dmg.waived and dmg.waived_amount == 20000 and dmg.settled
    # nothing left to charge: the close needs no charge approval and refunds all
    close(c, r)
    assert r.deposit_refunded == 5000 and not ledger(c, r).filtered(lambda d: d.kind == "deduction")


def test_recovery_comes_from_the_ledger_and_an_invoiced_loss_is_not_waived(c):
    r = walk(c, res(c), "action_assess_damage")
    dmg = damage(c, r, cost=20000)
    approve_charge(c, dmg)
    close(c, r)
    assert dmg.recovered_amount == 5000 and dmg.unrecovered_loss_amount == 15000
    assert dmg.invoice_id == r.excess_invoice_id and r.excess_billed == 15000
    with pytest.raises(UserError, match="credit note"):
        dmg.with_user(c.clerk).action_waive()


# --------------------------------------------- E5 / M13-10 retirement on the book value
def test_retirement_cannot_be_written_or_typed_down(c, p03):
    a = c.asset.with_user(c.clerk)
    with pytest.raises(REFUSED):
        a.write({"status": "retired"})
    out = p03.write(model="fix.rental.asset", record_id=a.id, values={"status": "retired"})
    assert out.get("error") and c.asset.status == "available"
    # XC-08: the counter neither sees nor types the cost basis
    with pytest.raises(AccessError):
        a.read(["purchase_cost"])
    with pytest.raises(REFUSED):
        a.write({"purchase_cost": 1})
    a = c.asset.with_user(c.fleet)
    for vals in (
        {"purchase_cost": 0},
        {"useful_life_days": 1},
        {"acquisition_date": c.today - timedelta(days=3000)},
    ):
        with pytest.raises(REFUSED, match="cut its book value"):
            a.write(vals)
    a.write({"purchase_cost": 120000})  # raising it is fine
    with pytest.raises(UserError, match="no approved retirement request"):
        a.action_retire()
    with pytest.raises(UserError, match="Retirement Request"):
        a.action_request_approval(justification="old style")


def test_retirement_through_the_inbox_hands_off_to_m49(c):
    env = c.env
    fa = env["fix.fixed.asset"].create(
        {
            "name": "A05M13T camera (M49)",
            "gross": 100000,
            "life_months": 36,
            "purchase_date": c.today - timedelta(days=100),
            "category": "Rental fleet",
            "company_id": env.company.id,
        }
    )
    fa.write({"state": "active"})
    c.asset.write({"fixed_asset_id": fa.id, "category": "tool"})
    a = c.asset.with_user(c.clerk)
    ret = (
        c.env["fix.rental.retirement"]
        .with_user(c.clerk)
        .create({"asset_id": a.id, "route": "resale", "reason": "end of life: sensor failure"})
    )
    ret.action_request_approval(justification="end of life: sensor failure")
    inbox_approve(ret, c.csh)
    inbox_approve(ret, c.cfo)
    a.action_retire()
    assert a.status == "retired" and a.retired_on and ret.state == "retired"
    assert a.disposal_id and a.disposal_id.asset_id == fa and a.disposal_id.state == "draft"
    with pytest.raises(REFUSED):
        a.write({"notes": "after retirement"})


# ------------------------------------------- E4 / M13-11 / M13-12 turnaround wipe gate
def _turnaround(c):
    r = walk(c, res(c), "action_return")
    t = c.env["fix.rental.turnaround"].search([("reservation_id", "=", r.id)])
    assert t and c.asset.status == "maintenance"
    return r, t.with_user(c.clerk)


def _cert(c, serial, request=None, method="nist_800_88_purge"):
    """The data lab's wipe certificate on the real role path (a lab operator
    records it, a wipe verifier verifies it). A unit leaving for its next
    renter is judged by the D16 matrix at release; Purge passes it for any
    media kind (A02 pass 2 review)."""
    log = (
        c.env["ir.attachment"]
        .with_user(c.wipe_tech)
        .create({"name": "wipe.log", "raw": b"nwipe: PASS %s" % serial.encode()})
    )
    vals = {
        "method": method,
        "sector_count": 1000,
        "wipe_log_attachment_id": log.id,
    }
    if request:
        vals["wipe_request_id"] = request.id
    else:
        vals["serial_number"] = serial
    cert = c.env["fix.data.wipe.certificate"].with_user(c.wipe_tech).create(vals)
    cert.with_user(c.wipe_verifier).action_verify()
    return cert.with_env(c.env)


def test_turnaround_release_needs_the_checklist_and_a_verified_wipe(c, p03):
    r, t = _turnaround(c)
    with pytest.raises(UserError, match="checklist is incomplete"):
        t.action_ready()
    t.write(
        {"cleaning_done": True, "inspection_done": True, "regrade": "b", "technician_id": c.tech.id}
    )
    # not opt-in: no reset box ticked, the camera is still data-bearing
    with pytest.raises(UserError, match="data-bearing"):
        t.action_ready()
    with pytest.raises(REFUSED):
        t.write({"nist_wipe_hash": "x"})
    with pytest.raises(REFUSED):
        t.write({"state": "ready"})
    out = p03.write(model="fix.rental.turnaround", record_id=t.id, values={"state": "ready"})
    t.invalidate_recordset()
    assert out.get("error") and t.state == "pending"
    t.write({"data_wipe_certificate_id": _cert(c, "OTHER-SN").id})
    with pytest.raises(UserError, match="certifies media"):
        t.action_ready()
    # A02 pass 2 review (M06-05): a certificate answering another record's
    # wipe request does not release this unit
    other = c.env["fix.data.wipe.request"].create(
        {
            "source": "customer",
            "source_ref": "SOMEONE-ELSES-ORDER",
            "serial_number": SN,
            "confidentiality_level": "high",
            "disposition": "internal_reuse",
        }
    )
    t.write({"data_wipe_certificate_id": _cert(c, SN, request=other).id})
    with pytest.raises(UserError, match="no wipe request raised for"):
        t.action_ready()
    # A02 pass 2 review N2: a certificate answering no request does not release
    # it, and a Clear of a unit of unrecorded media kind fails the D16 matrix
    clear = _cert(c, SN, method="nist_800_88")
    assert "no wipe request raised for" in clear._fix_certify_denial(SN, consumer=t.sudo())
    assert "sanitisation matrix" in clear._m06_matrix_denial()
    # the turnaround raised its own request when it opened; its certificate releases it
    own = c.env["fix.data.wipe.request"].search([("source_ref", "=", t.name)])
    assert (own.source, own.serial_number) == ("m13_rental", SN)
    cert = _cert(c, SN, request=own)
    t.write({"data_wipe_certificate_id": cert.id})
    t.action_ready()
    assert t.state == "ready" and c.asset.status == "available" and c.asset.condition_grade == "b"
    assert t.nist_wipe_hash == cert.verified_hash
    with pytest.raises(REFUSED, match="final"):
        t.write({"notes": "after release"})


def test_non_data_bearing_unit_needs_only_the_checklist(c):
    c.asset.write({"category": "tool"})
    r, t = _turnaround(c)
    t.write(
        {"cleaning_done": True, "inspection_done": True, "regrade": "a", "technician_id": c.tech.id}
    )
    t.action_ready()
    assert c.asset.status == "available"


def test_turnarounds_are_not_typed_and_an_asset_on_rent_is_not_released(c):
    with pytest.raises(REFUSED, match="not typed"):
        c.env["fix.rental.turnaround"].with_user(c.clerk).create({"rental_asset_id": c.asset.id})
    walk(c, res(c), "action_deliver")
    assert c.asset.status == "out"
    with pytest.raises(UserError, match="only a unit in maintenance"):
        c.asset.with_user(c.clerk).action_ready()
    assert c.asset.status == "out"


# ----------------------------------------------------------- P2 / M13-15 cancellation
def test_cancel_frees_the_unit_and_refunds_the_posted_deposit(c):
    r = walk(c, res(c), "action_reserve")
    assert c.asset.status == "reserved"
    with pytest.raises(UserError, match="you took the deposit"):
        r.action_cancel()
    r.with_user(c.clerk2).action_cancel()
    assert r.state == "cancelled" and c.asset.status == "available"
    refund = ledger(c, r).filtered(lambda d: d.kind == "refund")
    assert refund.amount == 5000 and refund.payment_execution_id
    r2 = walk(c, res(c), "action_deliver")
    with pytest.raises(UserError, match="only a draft or reserved"):
        r2.action_cancel()


def test_cancellation_fee_switch(c):
    """A05 FIN-18 / owner D2: the cancellation fee is a VAT supply invoiced
    through M51, not a forfeit of the deposit outside VAT."""
    c.env["ir.config_parameter"].set_param("cd_rental_asset.cancellation_fee_pct", "10")
    r = walk(c, res(c), "action_reserve")
    r.with_user(c.clerk2).action_cancel()
    rows = ledger(c, r)
    assert not rows.filtered(lambda d: d.kind == "forfeit")
    assert rows.filtered(lambda d: d.kind == "refund").amount == 5000
    fee = r.billing_ids.filtered(lambda b: b.kind == "cancellation")
    assert fee.fee_amount == 500 and fee.invoice_id.vat_amount > 0


# ----------------------------------------------------------------- E12 overdue cron
def test_overdue_cron_accrues_the_late_fee_once(c):
    r = res(c, date_from=c.today - timedelta(days=6), date_to=c.today - timedelta(days=2))
    walk(c, r, "action_activate")
    Res = c.env[RES]
    Res.cron_rental_overdue()
    r.invalidate_recordset()
    assert r.late_fee == 2 * 1000 * 1.5 and r.overdue_since == r.date_to + timedelta(days=1)
    acts = len(r.activity_ids)
    Res.cron_rental_overdue()
    r.invalidate_recordset()
    # the overdue to-do, and the 1-day escalation milestone (M13-26): once each
    assert r.late_fee == 3000 and len(r.activity_ids) == acts == 2


# ------------------------------------------------- M13-18 / M13-19 P03 wiring and KPIs
def test_surfaces_offer_the_routed_requests_and_every_button(c):
    import re
    from pathlib import Path

    from odoo.addons.cd_p03_portal.controllers.a05 import m13

    js = (Path(m13.__file__).resolve().parents[2] / "static" / "src" / "a05" / "m13.js").read_text(
        encoding="utf-8"
    )
    assert "fix.rental.agreement" not in js
    # A05 XC-26 (S1): a fleet unit's retirement is requested on its own
    # fix.rental.retirement record; the unit's surface no longer raises it
    for model in ("fix.rental.damage", "fix.rental.retirement"):
        assert {"action_request_approval", "action_recall_approval"} <= m13.SURFACES[model][
            "actions"
        ]
    for model in ("fix.rental.damage", "fix.rental.asset", "fix.rental.retirement"):
        assert "action_dofa_approve" not in m13.SURFACES[model]["actions"]
    screens = js[js.index("export const SCREENS") : js.index("export const REPORT_ROUTES")]
    for block in re.split(r"\n  '", screens):
        model = re.search(r"model: '([a-z.]+)'", block)
        if not model or "kind: 'model_list'" not in block:
            continue
        for method in re.findall(r"\bm: '(\w+)'", block):
            if method == "p03_print_document":
                continue  # a print button (XC-10): the workspace renders it itself
            assert method in m13.SURFACES[model.group(1)]["actions"], (model.group(1), method)
    assert all("writable" in conf for conf in m13.SURFACES.values())


def test_kpis_stay_inside_the_users_companies(c):
    from odoo.addons.cd_p03_portal.controllers.a05 import m13

    env = c.env
    clerk_env = env(user=c.clerk.id)
    before = m13.kpis(clerk_env)
    other = env["res.company"].create({"name": "A05M13T Other Company"})
    asset = env["fix.rental.asset"].create(
        {"name": "OTHER-CO-1", "rental_sku_id": c.sku.id, "company_id": other.id}
    )
    rec = env[RES].create(
        {"customer_id": c.customer.id, "company_id": other.id, "rental_asset_id": asset.id}
    )
    rec.write({"state": "active"})
    after = m13.kpis(clerk_env)
    assert after["fleet_size"] == before["fleet_size"]
    assert after["active_rentals"] == before["active_rentals"]
    pack = m13.availability(clerk_env)
    assert "OTHER-CO-1" not in {row["asset"] for row in pack["rows"]}
