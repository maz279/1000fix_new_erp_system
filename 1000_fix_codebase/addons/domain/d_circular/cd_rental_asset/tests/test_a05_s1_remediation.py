# A05 ERP remediation, stream S1 (M13 Rental), 2026-11-20. Each test drives
# the ORM as a non-admin user (rolled back) and is built so only the new rule
# refuses what it attacks; the mutation run re-introduces each defect.
import json
from datetime import timedelta
from unittest import mock

import pytest
from odoo.addons.cd_rental_asset.models import fix_rental_money, rental_policy
from odoo.addons.cd_rental_asset.tests import test_a05_m13_controls as ctl
from odoo.addons.cd_rental_asset.tests.test_a05_m13_controls import (
    REFUSED,
    RES,
    SN,
    _cert,
    _user,
    close,
    damage,
    inbox_approve,
    ledger,
    res,
    sign,
    walk,
)
from odoo.exceptions import AccessError, UserError

# the controls suite's fixtures, shared
c = ctl.c
p03 = ctl.p03

pytestmark = [pytest.mark.financial]


def events(c, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id:
        domain.append(("aggregate_id", "=", aggregate_id))
    return c.env["fix.event.outbox"].sudo().search(domain)


def payload(event):
    return json.loads(event.payload)


def _sku(c, **rates):
    tmpl = c.env["product.template"].create({"name": "A05S1 SKU %s" % sorted(rates.items())})
    item = c.env["fix.catalogue.item"].create({"product_tmpl_id": tmpl.id})
    return c.env["fix.rental.sku"].create(dict({"catalogue_item_id": item.id}, **rates))


def _finance(c, login="fin"):
    return _user(c.env, login, ["cd_rental_asset.group_rental_finance"])


def _acc_manager(c, login="accman"):
    return _user(c.env, login, ["account.group_account_manager"])


# ============================================================ tariff (M13-01/11)
@pytest.mark.parametrize(
    "days,rates,charge",
    [
        (6, (1000, 5000, 20000), 5000),  # a week beats 6 days
        (13, (1000, 5000, 20000), 10000),  # two weeks beat 1 week + 6 days
        (29, (1000, 5000, 20000), 20000),  # a month beats 4 weeks + 1 day
        (5, (0, 5000, 0), 5000),  # weekly-only: the odd days cost a whole week
        (5, (0, 0, 20000), 20000),  # monthly-only
        (35, (1500, 9000, 30000), 37500),
    ],
)
def test_cheapest_ladder(odoo_env, days, rates, charge):
    cost, breakdown = odoo_env[RES]._cheapest_ladder(days, *rates)
    assert cost == charge, breakdown


def test_no_rate_prices_nothing(odoo_env):
    assert odoo_env[RES]._cheapest_ladder(5, 0, 0, 0)[0] is None


def test_tariff_is_the_skus_and_cannot_be_typed(c, p03):
    with pytest.raises(REFUSED):
        res(c, daily_rate=1)
    r = res(c, daily_rate=1000)  # the SKU's own rate posted back is not a typed tariff
    assert (r.daily_rate, r.weekly_rate, r.monthly_rate) == (1000, 0, 0)
    with pytest.raises(REFUSED):
        r.write({"daily_rate": 1})
    out = p03.write(model=RES, record_id=r.id, values={"daily_rate": 1})
    assert out.get("error") and r.daily_rate == 1000
    sku2 = _sku(c, daily_rate=700, weekly_rate=4000)
    r.write({"rental_sku_id": sku2.id, "rental_asset_id": False})
    assert (r.daily_rate, r.weekly_rate) == (700, 4000)  # re-snapshot while draft
    assert r.tariff_breakdown and r.rental_charge == 3 * 700


def test_unpriceable_tariff_is_refused_at_reserve(c):
    sku = _sku(c, security_deposit=0)
    r = res(c, rental_sku_id=sku.id, rental_asset_id=False, device_id=c.device.id)
    assert r.tariff_breakdown.startswith("UNPRICED")
    sign(c, r)
    with pytest.raises(REFUSED, match="cannot price"):
        r.action_reserve()


# =================================================== cumulative billing (FIN-07)
def test_close_is_refused_while_charges_are_not_invoiced(c):
    r = walk(c, res(c), "action_assess_damage")
    row = r.billing_ids.filtered(lambda b: b.key == "return")
    assert row and r._unbilled()[0] == r._unbilled()[1]  # the return billed it
    row.invoice_id.sudo().action_cancel("finance dropped the draft")
    assert r._unbilled() == (r.rental_charge, 0)
    with pytest.raises(REFUSED, match="not invoiced"):
        close(c, r)
    r.action_issue_rental_invoice()
    close(c, r)
    assert r.state == "closed"


def test_extension_is_billed_as_its_own_supplementary_invoice(c):
    r = walk(c, res(c), "action_activate")
    r.action_issue_rental_invoice()
    first = r.billing_ids
    assert len(first) == 1 and first.taxable_amount == 3000
    ext = (
        c.env["fix.rental.extension"]
        .with_user(c.clerk)
        .create(
            {"reservation_id": r.id, "new_date_to": r.date_to + timedelta(days=4), "reason": "more"}
        )
    )
    ext.with_user(c.clerk2).action_apply()
    row = r.billing_ids.filtered(lambda b: b.key == "ext-%d" % ext.id)
    assert row.rental_amount == 4000 and row.extension_id == ext
    assert row.service_date_from == ext.old_date_to + timedelta(days=1)
    assert row.service_date_to == ext.new_date_to
    assert row.invoice_id and row.invoice_id != first.invoice_id
    assert r._unbilled() == (7000, 7000)


def test_retroactive_extension_keeps_the_accrued_late_fee(c):
    r = res(c, date_from=c.today - timedelta(days=6), date_to=c.today - timedelta(days=3))
    walk(c, r, "action_activate")
    c.env[RES].cron_rental_overdue()
    r.invalidate_recordset()
    accrued = r.late_fee
    assert accrued == 3 * 1000 * 1.5
    ext = (
        c.env["fix.rental.extension"]
        .with_user(c.clerk)
        .create(
            {
                "reservation_id": r.id,
                "new_date_to": c.today + timedelta(days=2),
                "reason": "late ask",
            }
        )
    )
    ext.with_user(c.clerk2).action_apply()
    assert r.late_fee == accrued and r.late_fee_retained == accrued
    r.action_return()
    assert r.late_fee == accrued  # still charged at the (now on-time) return


def test_late_return_is_billed_as_a_supplementary_invoice(c):
    r = res(c, date_from=c.today - timedelta(days=5), date_to=c.today - timedelta(days=3))
    walk(c, r, "action_activate")
    r.action_issue_rental_invoice()
    r.action_return()
    row = r.billing_ids.filtered(lambda b: b.key == "return")
    assert row.late_fee_amount == 4500 and row.rental_amount == 0
    assert len(r.billing_ids.mapped("invoice_id")) == 2


# ================================================ early return / min hire (M13-18)
def test_early_return_is_charged_for_the_days_used_and_rebilled(c):
    r = res(c, date_from=c.today - timedelta(days=1), date_to=c.today + timedelta(days=8))
    walk(c, r, "action_activate")
    r.action_issue_rental_invoice()
    first = r.billing_ids.invoice_id
    assert first.state == "draft" and r.rental_charge == 10000
    r.action_return()
    assert r.billable_days == 2 and r.rental_charge == 2000
    assert first.state == "cancelled"
    assert r._unbilled() == (2000, 2000)


def test_minimum_hire_floors_an_early_return(c):
    c.sku.write({"min_hire_days": 5})
    r = res(c, date_from=c.today - timedelta(days=1), date_to=c.today + timedelta(days=8))
    assert r.min_hire_days == 5
    walk(c, r, "action_return")
    assert r.billable_days == 5 and r.rental_charge == 5000


# =========================================== cancel credits the invoice (FIN-08)
def test_cancel_cancels_the_rental_invoice(c):
    r = walk(c, res(c), "action_reserve")
    r.action_issue_rental_invoice()
    inv = r.mushak_6_3_id
    assert inv.state == "draft"
    r.with_user(c.clerk2).action_cancel()
    assert inv.state == "cancelled" and r._unbilled() == (0, 0)


# ================================================ accounts (FIN-01/FIN-17, D1)
def test_rental_lines_credit_rental_income_and_damage_recovery(c):
    r = walk(c, res(c), "action_assess_damage")
    rental_inv = r.billing_ids.filtered(lambda b: b.kind == "rental").invoice_id
    assert rental_inv.revenue_account_id.code == "400000"
    assert rental_inv.vat_amount > 0
    dmg = damage(c, r, cost=8000)
    dmg.with_user(c.clerk).action_request_charge_approval()
    inbox_approve(dmg.charge_approval_id, c.t1)
    close(c, r)
    excess = r.excess_invoice_id
    assert excess.revenue_account_id.code == "450000"
    assert excess.vat_amount == 0 and excess.taxable_amount == 3000
    assert dmg.invoice_id == excess


@pytest.mark.parametrize("role", ["deposit_liability", "recovery_income", "rental_income"])
def test_rental_accounts_fail_closed(c, role):
    from odoo.addons.cd_rental_asset.models.rental_gl import rental_account

    params = c.env["ir.config_parameter"]
    params.set_param("cd_rental_asset.account_code.%s" % role, "")
    with pytest.raises(UserError, match="cd_rental_asset.account_code.%s" % role):
        rental_account(c.env, c.env.company, role)
    params.set_param("cd_rental_asset.account_code.%s" % role, "A05S1-NO-SUCH")
    with pytest.raises(UserError, match="does not exist"):
        rental_account(c.env, c.env.company, role)


def test_damage_compensation_needs_an_out_of_vat_treatment(c):
    c.env["ir.config_parameter"].set_param("cd_rental_asset.vat_treatment_code.damage", "")
    r = walk(c, res(c), "action_assess_damage")
    dmg = damage(c, r, cost=8000)
    dmg.with_user(c.clerk).action_request_charge_approval()
    inbox_approve(dmg.charge_approval_id, c.t1)
    with pytest.raises(UserError, match="vat_treatment_code.damage"):
        close(c, r)


# ======================================================== deposit (D8, M13-19)
def test_deposit_is_the_value_times_the_risk_tier(c):
    params = c.env["ir.config_parameter"]
    params.set_param("cd_rental_asset.deposit_rate_pct.standard", "20")
    params.set_param("cd_rental_asset.deposit_rate_pct.high", "35")
    r = res(c, deposit_collected=5000)
    book = c.asset._book_value()
    assert r.deposit_required == round(book * 0.20, 2) > 5000
    c.env["fix.rental.exposure"].create(
        {"partner_id": c.customer.id, "risk_tier": "high", "exposure_limit": 10**9, "basis": "x"}
    )
    r.invalidate_recordset()
    assert r.deposit_required == round(book * 0.35, 2)
    sign(c, r)
    with pytest.raises(REFUSED, match="required deposit"):
        r.action_reserve()


def test_a_lower_deposit_needs_a_finance_managers_routed_approval(c):
    c.env["ir.config_parameter"].set_param("cd_rental_asset.deposit_rate_pct.standard", "20")
    fm, fm2 = _acc_manager(c, "fm"), _acc_manager(c, "fm2")
    r = res(c, deposit_collected=6000)
    red = (
        c.env["fix.rental.deposit.reduction"]
        .with_user(c.clerk)
        .create(
            {"reservation_id": r.id, "reduced_amount": 6000, "reason": "long-standing customer"}
        )
    )
    with pytest.raises(UserError, match="approver's inbox"):
        red.with_user(fm)._reduction_approve()
    sign(c, r)
    with pytest.raises(REFUSED, match="required deposit"), c.env.cr.savepoint():
        r.action_reserve()  # asked for, not yet approved
    red.with_user(c.clerk).action_request_approval(justification="long-standing customer")
    assigned = red.approval_request_id.task_ids.mapped("assigned_user_id")
    approver = (fm | fm2) & assigned
    assert c.clerk not in assigned and approver
    inbox_approve(red, approver[:1])
    assert red.approval_state == "approved"
    r.action_reserve()
    assert r.state == "reserved"


# ======================================================= OU from branch (FIN-09)
def test_ou_comes_from_the_branch_and_is_frozen(c):
    other = c.env["operating.unit"].search([("id", "!=", c.ou.id)], limit=1) or c.env[
        "operating.unit"
    ].create({"name": "A05S1 OU", "code": "A5S1OU", "partner_id": c.env.company.partner_id.id})
    with pytest.raises(REFUSED, match="carries that unit"):
        res(c, operating_unit_id=other.id)
    r = res(c, operating_unit_id=False)
    assert r.operating_unit_id == c.branch.operating_unit_id
    walk(c, r, "action_reserve")
    with pytest.raises(REFUSED, match="fixed once the booking"):
        r.write({"branch_id": False})
    r.with_user(c.clerk2).action_cancel()
    refund = ledger(c, r).filtered(lambda d: d.kind == "refund")
    assert refund.payment_execution_id.operating_unit_id == c.branch.operating_unit_id


def test_a_booking_without_a_branch_is_not_confirmed(c):
    r = sign(c, res(c, branch_id=False, operating_unit_id=False))
    with pytest.raises(REFUSED, match="no booking branch"):
        r.action_reserve()


# ============================================ exposure (XC-01/XC-02, M13-12)
def test_exposure_limits_are_finance_only_and_masked(c):
    Exp = c.env["fix.rental.exposure"]
    with pytest.raises(AccessError):
        Exp.with_user(c.clerk).create(
            {"partner_id": c.customer.id, "exposure_limit": 999999999, "basis": "self"}
        )
    fin = _finance(c)
    exp = Exp.with_user(fin).create(
        {"partner_id": c.customer.id, "exposure_limit": 1000, "basis": "credit file"}
    )
    with pytest.raises(AccessError):
        exp.with_user(c.clerk).read(["exposure_limit"])
    with pytest.raises(AccessError):
        exp.with_user(c.clerk).write({"exposure_limit": 10**9})
    assert exp.with_user(c.clerk).read(["partner_id"])


def test_an_exposure_override_is_a_routed_tiered_approval(c):
    _finance(c)
    c.env["fix.rental.exposure"].create(
        {"partner_id": c.customer.id, "exposure_limit": 1000, "basis": "credit file"}
    )
    r = res(c)
    ov = (
        c.env["fix.rental.exposure.override"]
        .with_user(c.clerk)
        .create({"reservation_id": r.id, "justification": "event week"})
    )
    with pytest.raises(UserError, match="M63 inbox"):
        ov.with_user(c.clerk2).action_approve()
    tier = ov._dofa_current_tier()
    assert tier in ("tier_1", "tier_2")
    ov.with_user(c.clerk).action_request_approval(justification="event week")
    approver = c.t2 if tier == "tier_2" else c.t1
    assert c.clerk not in ov.approval_request_id.task_ids.mapped("assigned_user_id")
    inbox_approve(ov, approver)
    assert ov.state == "approved" and ov.decided_by == approver
    sign(c, r)
    r.action_reserve()


# ========================================== loss write-off (XC-04, M13-13)
def _loss(c, valuation=None):
    r = walk(c, res(c), "action_activate")
    vals = {
        "reservation_id": r.id,
        "kind": "loss",
        "circumstances": "left in a taxi",
        "claim_decision": "no_claim",
        "no_claim_reason": "below the excess",
    }
    if valuation is not None:
        vals["valuation"] = valuation
    return r, c.env["fix.rental.loss"].with_user(c.clerk).create(vals)


def test_loss_write_off_is_routed_on_the_loss_and_pinned(c):
    r, loss = _loss(c)
    assert loss.valuation == c.asset._book_value()
    with pytest.raises(UserError, match="not granted"):
        loss.with_user(c.clerk2).action_write_off()
    loss.with_user(c.clerk).action_request_writeoff(justification="lost")
    tier = loss._dofa_current_tier()
    assert tier == "tier_2"
    inbox_approve(loss, c.t2)
    assert loss.approval_state == "approved"
    loss.with_user(c.clerk).write({"valuation": 1})  # re-pointed after approval
    assert loss.approval_state == "none" and not loss.dofa_approved
    with pytest.raises(UserError, match="justify"):
        loss.with_user(c.clerk).action_request_writeoff()
    loss.with_user(c.clerk).action_request_writeoff(justification="customer insolvent")
    inbox_approve(loss, c.t2)  # the approval covers the book value written off
    loss.with_user(c.clerk2).action_write_off()
    assert loss.state == "written_off" and r.state == "lost"


# ================================ retirement (M13-14/16, XC-03, I1, M13-28)
def _retirement(c, asset=None, **kw):
    vals = {"asset_id": (asset or c.asset).id, "route": "recycle", "reason": "end of life"}
    vals.update(kw)
    return c.env["fix.rental.retirement"].with_user(c.clerk).create(vals)


def test_retirement_needs_the_wipe_gate_and_a_destination(c):
    ret = _retirement(c, weight_kg=1.2)
    with pytest.raises(UserError, match="data-bearing"):
        ret.action_request_approval(justification="eol")
    ret.write({"data_wipe_certificate_id": _cert(c, "OTHER-SN").id})
    with pytest.raises(UserError, match="data-bearing"):
        ret.action_request_approval(justification="eol")
    no_weight = _retirement(c, data_wipe_certificate_id=_cert(c, SN).id)
    with pytest.raises(UserError, match="weight"):
        no_weight.action_request_approval(justification="eol")


def test_a_zero_value_unit_is_still_jointly_approved(c):
    c.asset.write({"category": "tool", "purchase_cost": 0})
    ret = _retirement(c, route="resale")
    assert ret._approval_needed()
    with pytest.raises(UserError, match="no approved retirement"):
        c.asset.with_user(c.clerk).action_retire()
    ret.action_request_approval(justification="eol")
    assert ret.approval_request_id.approval_policy == "all"
    inbox_approve(ret, c.csh)
    assert ret.state == "requested"  # one signature is not the joint approval
    with pytest.raises(UserError, match="not approved"):
        ret.action_retire()
    inbox_approve(ret, c.cfo)
    assert ret.state == "approved"


def test_one_person_holding_both_roles_cannot_retire_alone(c):
    c.asset.write({"category": "tool"})
    both = _user(
        c.env, "both", ["cd_rental_asset.group_rental_csh", "cd_rental_asset.group_rental_cfo"]
    )
    c.csh.write({"group_ids": [(3, c.env.ref("cd_rental_asset.group_rental_csh").id)]})
    c.cfo.write({"group_ids": [(3, c.env.ref("cd_rental_asset.group_rental_cfo").id)]})
    ret = _retirement(c, route="resale")
    ret.action_request_approval(justification="eol")
    task = ret.approval_request_id.task_ids.filtered(lambda t: t.assigned_user_id == both)
    with pytest.raises(UserError, match="two different"):
        task.with_user(both).action_approve()


def test_executed_retirement_publishes_the_route_and_feeds_m49_m18(c):
    env = c.env
    fa = env["fix.fixed.asset"].create(
        {
            "name": "A05S1 camera (M49)",
            "gross": 100000,
            "life_months": 36,
            "purchase_date": c.today - timedelta(days=100),
            "category": "Rental fleet",
            "company_id": env.company.id,
        }
    )
    fa.write({"state": "active"})
    c.asset.write({"fixed_asset_id": fa.id, "branch_id": c.branch.id})
    ret = _retirement(c, weight_kg=1.5, material="other", data_wipe_certificate_id=_cert(c, SN).id)
    ret.action_request_approval(justification="eol")
    inbox_approve(ret, c.csh)
    inbox_approve(ret, c.cfo)
    ret.action_retire()
    assert c.asset.status == "retired" and ret.state == "retired"
    # S6 wiring: S4's M49 API opens a RECYCLE disposal started by the unit;
    # M18 receives it from rental.asset_retired (S3), so the M49 posting must
    # not open a second collection (no ewaste_route)
    disposal = ret.disposal_id.sudo()
    assert disposal.kind == "recycle" and not disposal.ewaste_route
    assert (disposal.source_model, disposal.source_res_id) == ("fix.rental.asset", c.asset.id)
    assert disposal.ewaste_weight_kg == 1.5
    (event,) = events(c, "rental.asset_retired", c.asset.id)
    data = payload(event)
    assert data["route"] == "recycle" and data["serial"] == SN and data["weight_kg"] == 1.5
    assert data["branch_id"] == c.branch.id and data["operating_unit_id"] == c.ou.id
    assert data["book_value"] == round(fa.book_nbv, 2)
    assert set(data) == {
        "asset_id",
        "device_id",
        "serial",
        "route",
        "weight_kg",
        "material",
        "company_id",
        "operating_unit_id",
        "branch_id",
        "book_value",
    }


def test_matrix_domains_are_the_ones_models_route_on(c):
    selection = dict(c.env["fix.approval.matrix"]._fields["decision_domain"].selection)
    assert "rental_damage_waiver" not in selection and "rental_asset_writeoff" not in selection
    for model in (
        "fix.rental.damage",
        "fix.rental.charge.approval",
        "fix.rental.retirement",
        "fix.rental.loss",
        "fix.rental.exposure.override",
        "fix.rental.deposit.reduction",
    ):
        assert type(c.env[model])._approval_domain in selection, model


# ======================================== availability (M13-20)
def test_hold_expiry_releases_an_unhanded_booking(c):
    r = walk(c, res(c), "action_reserve")
    assert r.hold_expires_at
    r.sudo()._guarded().write({"hold_expires_at": r.hold_expires_at - timedelta(days=10)})
    c.env[RES].cron_rental_hold_expiry()
    assert r.state == "cancelled" and c.asset.status == "available"
    assert ledger(c, r).filtered(lambda d: d.kind == "refund").amount == 5000


def test_a_unit_below_the_category_minimum_grade_is_not_allocated(c):
    c.asset.sudo()._guarded().write({"condition_grade": "d"})
    r = sign(c, res(c))
    with pytest.raises(REFUSED, match="BRU-RNT-14"):
        r.action_reserve()
    c.env["ir.config_parameter"].set_param("cd_rental_asset.min_dispatch_grade.camera", "d")
    r.action_reserve()


def test_availability_takes_a_row_lock_on_the_sku_pool(c):
    """M13-20: deciding availability writes (and so row-locks) the SKU pool
    row, which nothing else in the reservation touches: a concurrent
    confirmation of the same pool waits on it and, under REPEATABLE READ,
    is retried against the committed booking. The row's new tuple version
    (ctid) is the proof that the lock-taking UPDATE ran. (A second
    connection cannot see this rolled-back test's SKU row at all.)"""
    cr = c.env.cr
    c.env.flush_all()
    cr.execute("SELECT ctid::text FROM fix_rental_sku WHERE id = %s", (c.sku.id,))
    before = cr.fetchone()[0]
    walk(c, res(c), "action_reserve")
    c.env.flush_all()
    cr.execute("SELECT ctid::text FROM fix_rental_sku WHERE id = %s", (c.sku.id,))
    assert cr.fetchone()[0] != before


# ====================================== overdue escalation, return due (M13-26, I5)
def test_overdue_milestones_publish_rental_overdue_once_each(c):
    r = res(c, date_from=c.today - timedelta(days=6), date_to=c.today - timedelta(days=4))
    walk(c, r, "action_activate")
    Res = c.env[RES]
    Res.cron_rental_overdue()
    Res.cron_rental_overdue()
    (event,) = events(c, "rental.overdue", r.id)
    assert payload(event) == {
        "reservation_id": r.id,
        "partner_id": c.customer.id,
        "days_overdue": 4,
    }
    later = c.today + timedelta(days=3)
    with mock.patch.object(rental_policy, "dhaka_today", lambda env: later):
        Res.cron_rental_overdue()
    assert len(events(c, "rental.overdue", r.id)) == 2


def test_return_due_notice_goes_once_the_day_before(c):
    r = res(c, date_from=c.today - timedelta(days=2), date_to=c.today + timedelta(days=1))
    walk(c, r, "action_activate")
    Res = c.env[RES]
    Res.cron_rental_return_due()
    Res.cron_rental_return_due()
    (event,) = events(c, "rental.return_due", r.id)
    assert payload(event) == {
        "reservation_id": r.id,
        "partner_id": c.customer.id,
        "due_at": str(r.date_to),
    }


# ============================================ M53 lease flag (BRU-RNT-18, M13-29)
def test_a_twelve_month_rental_waits_for_its_m53_assessment(c, p03):
    c.sku.write({"monthly_rate": 20000})
    r = res(c, date_to=c.today + timedelta(days=400))
    assert r.lease_assessment_required
    with pytest.raises(REFUSED):
        r.write({"ifrs16_classification": "finance"})
    walk(c, r, "action_deliver")
    with pytest.raises(REFUSED, match="BRU-RNT-18"):
        r.action_activate()
    with pytest.raises(UserError, match="Finance"):
        r.action_record_lease_assessment(reference="M53/1", classification="operating")
    r.with_user(_finance(c)).action_record_lease_assessment(reference="M53/1")
    r.action_activate()
    assert r.state == "active" and r.m53_assessment_ref == "M53/1"


# ===================================== book value on read (FIN-15, M13-15)
def test_book_value_is_computed_on_read_or_read_from_m49(c):
    asset = c.asset.sudo()
    today_value = asset.net_book_value
    later = c.today + timedelta(days=200)
    with mock.patch.object(rental_policy, "dhaka_today", lambda env: later):
        asset.invalidate_recordset(["net_book_value"])
        assert asset.net_book_value < today_value
    fa = c.env["fix.fixed.asset"].create(
        {
            "name": "A05S1 M49",
            "gross": 50000,
            "life_months": 36,
            "purchase_date": c.today,
            "category": "Rental fleet",
            "company_id": c.env.company.id,
        }
    )
    fa.write({"state": "active"})
    asset.write({"fixed_asset_id": fa.id})
    assert asset._book_value() == round(fa.book_nbv, 2)


# ===================================== fleet record set by process (M13-25, XC-08)
def test_grade_and_unit_change_only_through_their_process(c, p03):
    a = c.asset.with_user(c.fleet)
    with pytest.raises(REFUSED, match="M13-25"):
        a.write({"condition_grade": "b"})
    out = p03.write(model="fix.rental.asset", record_id=a.id, values={"condition_grade": "b"})
    assert out.get("error") and c.asset.condition_grade == "a"
    with pytest.raises(AccessError):
        c.asset.with_user(c.clerk).read(["net_book_value"])


# ===================================== waiver plans (XC-07)
def test_waiver_plans_are_finance_products(c):
    Plan = c.env["fix.rental.waiver.plan"]
    vals = {"name": "A05S1 waiver", "fee_pct": 50, "excess_amount": 0, "legal_review_ref": "L/1"}
    with pytest.raises(AccessError):
        Plan.with_user(c.clerk).create(vals)
    plan = Plan.with_user(_finance(c, "fin1")).create(vals)
    with pytest.raises(AccessError, match="XC-07"):
        plan.with_user(c.clerk2).action_publish()
    plan.with_user(_finance(c, "fin2")).action_publish()
    assert plan.state == "published"


# ===================================== deposit release SoD (XC-22)
def test_the_deposit_taker_does_not_settle_the_rental(c):
    r = walk(c, res(c), "action_assess_damage")
    with pytest.raises(UserError, match="you took the deposit"):
        r.action_close()
    close(c, r)
    refund = ledger(c, r).filtered(lambda d: d.kind == "refund")
    assert refund.payment_execution_id.source_approved_by_id == c.clerk2


def test_vat_code_helper_refuses_a_vatable_damage_treatment(c):
    Treatment = c.env["fix.vat.treatment"].sudo()
    row = Treatment.create({"code": "A05S1-STD", "name": "std", "treatment_type": "standard_15"})
    if row.state != "active":
        row._guarded().write({"state": "active"})
    c.env["ir.config_parameter"].set_param("cd_rental_asset.vat_treatment_code.damage", "A05S1-STD")
    with pytest.raises(UserError, match="outside VAT"):
        fix_rental_money._vat_code(c.env, c.env.company, "damage")


def test_damage_is_not_invoiced_on_an_unsigned_treatment(c):
    """Owner decision D12: the exempt compensation treatment is a proposal until
    the tax adviser and the CFO sign it; until then no damage is invoiced."""
    Treatment = c.env["fix.vat.treatment"].sudo()
    row = Treatment.create(
        {"code": "A05S1-UNSIGNED", "name": "comp", "treatment_type": "exempt", "rate": 0.0}
    )
    if row.state != "active":
        row._guarded().write({"state": "active"})
    assert row.signoff_state != "signed"
    c.env["ir.config_parameter"].set_param(
        "cd_rental_asset.vat_treatment_code.damage", "A05S1-UNSIGNED"
    )
    with pytest.raises(UserError, match="awaiting sign-off"):
        fix_rental_money._vat_code(c.env, c.env.company, "damage")
    # signed by the adviser and the CFO: the same row is invoiceable
    row._guarded().write({"verify_with_adviser": False})
    assert row.signoff_state == "signed"
    assert fix_rental_money._vat_code(c.env, c.env.company, "damage") == "A05S1-UNSIGNED"


def test_an_undated_damage_is_dated_the_dhaka_day_and_reported_in_the_period(c):
    """A05 e2e walk defect 3: a damage recorded without an incident date fell
    out of every period report. It is the Dhaka business day it is recorded,
    so the M13 Damage & Recovery pack counts it in the current period."""
    from odoo import fields
    from odoo.addons.cd_p03_portal.controllers.a05 import m13

    clerk_env = c.env(user=c.clerk.id)
    before = m13.damage_recovery(clerk_env)["totals"]
    r = walk(c, res(c), "action_assess_damage")
    dmg = damage(c, r)
    assert dmg.incident_date == rental_policy.dhaka_today(c.env)
    after = m13.damage_recovery(clerk_env)["totals"]
    assert after["incidents"] == (before.get("incidents") or 0) + 1
    assert after["assessed"] == (before.get("assessed") or 0.0) + 3000
    # 20:00 UTC is already the next day in Dhaka (UTC+6): never the UTC date
    utc_evening = fields.Datetime.now().replace(hour=20, minute=0, second=0, microsecond=0)
    with mock.patch.object(fields.Datetime, "now", return_value=utc_evening):
        late = damage(c, r, description="Scratched body")
    assert late.incident_date == utc_evening.date() + timedelta(days=1)


def test_billing_rows_cannot_be_typed(c):
    r = walk(c, res(c), "action_assess_damage")
    with pytest.raises(REFUSED):
        c.env["fix.rental.billing"].with_user(c.clerk).create(
            {"reservation_id": r.id, "kind": "credit", "key": "x", "name": "x"}
        )
    row = r.billing_ids[:1].with_user(c.clerk)
    with pytest.raises(REFUSED):
        row.write({"taxable_amount": 1})
