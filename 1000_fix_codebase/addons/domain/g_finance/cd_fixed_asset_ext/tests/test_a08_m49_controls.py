"""A08 M49 controls (findings M49-1 ... M49-13): every gap probe of
working/A08_evidence/probes/m49/probe_m49.py run again as the attack it was,
now refused, plus the proper paths — budget -> capex (routed by amount
through the M63 inbox) -> CWIP from posted cost -> capitalisation ->
depreciation -> revaluation / disposal / transfer / lease — that the
legitimate maker and checker CAN complete. Live ORM, rolled back.

Attacks run as NON-ADMIN users created in the transaction with the real
finance role (Accountant, Accounting Administrator, Billing) and, for the
approvers, a DOFA tier group. The records live in a company of their own, so
the approval engine routes only to the users made here.
"""

from __future__ import annotations

import base64
import itertools
import types
from datetime import date

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, assigned
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
ACC = "account.group_account_user"
MGR = "account.group_account_manager"
BILL = "account.group_account_invoice"
TIER = "cd_entity_config.group_dofa_tier_%d"
BIN = "1234567890123"
_SEQ = itertools.count(1)
_CR = []


def _refused(fn, *args, match=None, **kw):
    with pytest.raises(REFUSED, match=match), _CR[-1].savepoint():
        fn(*args, **kw)


class Ctx(types.SimpleNamespace):
    def as_(self, user):
        return self.env(
            user=user.id, context=dict(self.env.context, allowed_company_ids=self.co.ids)
        )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    _CR.append(env.cr)
    n = next(_SEQ)
    x = Ctx(env=env)
    x.today = fields.Date.context_today(env.user)
    x.co = env["res.company"].create({"name": "A08 M49 Controls Co %s" % n, "vat": BIN})
    x.ou = env["operating.unit"].create(
        {
            "name": "A08 M49 OU %s" % n,
            "code": "A8M49%s" % n,
            "company_id": x.co.id,
            "partner_id": x.co.partner_id.id,
        }
    )
    x.ou2 = env["operating.unit"].create(
        {
            "name": "A08 M49 OU2 %s" % n,
            "code": "A8M49B%s" % n,
            "company_id": x.co.id,
            "partner_id": x.co.partner_id.id,
        }
    )
    x.cenv = env(context=dict(env.context, allowed_company_ids=x.co.ids))

    def acc(code, name, kind):  # code is company-dependent: create in the company
        return x.cenv["account.account"].create(
            {
                "code": "A849%s%s" % (n, code),
                "name": "A08M49 %s" % name,
                "account_type": kind,
                "company_ids": [(6, 0, x.co.ids)],
            }
        )

    x.a = {
        "asset": acc("01", "Asset", "asset_fixed"),
        "accum": acc("02", "Accumulated depreciation", "asset_fixed"),
        "expense": acc("03", "Depreciation expense", "expense_depreciation"),
        "cwip": acc("04", "CWIP", "asset_non_current"),
        "surplus": acc("05", "Revaluation surplus", "equity"),
        "impair": acc("06", "Impairment loss", "expense"),
        "gain": acc("07", "Gain on disposal", "income_other"),
        "loss": acc("08", "Loss on disposal", "expense"),
        "proceeds": acc("09", "Disposal clearing", "asset_current"),
        "liability": acc("10", "Lease liability", "liability_non_current"),
        "interest": acc("11", "Interest expense", "expense"),
        "rent": acc("12", "Rent payable", "liability_current"),
        "payable": acc("13", "Trade payables", "liability_current"),
        "other": acc("14", "Other asset", "asset_current"),
    }
    x.journal = x.cenv["account.journal"].create(
        {
            "name": "A08M49 Assets %s" % n,
            "code": "A9%s" % n,
            "type": "general",
            "company_id": x.co.id,
        }
    )
    cat_vals = {
        "company_id": x.co.id,
        "journal_id": x.journal.id,
        "asset_account_id": x.a["asset"].id,
        "accumulated_account_id": x.a["accum"].id,
        "expense_account_id": x.a["expense"].id,
        "cwip_account_id": x.a["cwip"].id,
        "revaluation_surplus_account_id": x.a["surplus"].id,
        "impairment_account_id": x.a["impair"].id,
        "gain_account_id": x.a["gain"].id,
        "loss_account_id": x.a["loss"].id,
    }
    Cat = x.cenv["fix.asset.category"]
    x.cat = Cat.create(
        dict(
            cat_vals,
            code="T%s" % n,
            name="Tools %s" % n,
            useful_life_months=12,
            tax_rate_code="ITA3-PLANT",
        )
    )
    x.cat_it = Cat.create(
        dict(
            cat_vals,
            code="IT%s" % n,
            name="IT %s" % n,
            useful_life_months=36,
            tax_rate_code="ITA3-COMPUTER",
        )
    )
    x.cat_rou = Cat.create(
        dict(cat_vals, code="ROU%s" % n, name="ROU %s" % n, useful_life_months=12)
    )

    def user(login, *groups):
        gids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": "%s-%s" % (login, n),
                    "group_ids": [(6, 0, gids)],
                    "company_id": x.co.id,
                    "company_ids": [(6, 0, x.co.ids)],
                    "assigned_operating_unit_ids": [(6, 0, (x.ou | x.ou2).ids)],
                    "default_operating_unit_id": x.ou.id,
                }
            )
        )

    x.acc1 = user("a08m49c_acc1", ACC)
    x.acc2 = user("a08m49c_acc2", ACC)
    x.mgr = user("a08m49c_mgr", MGR)
    x.mgr2 = user("a08m49c_mgr2", MGR)
    x.bill = user("a08m49c_bill", BILL)
    x.plain = user("a08m49c_plain")
    x.t2 = user("a08m49c_t2", MGR, TIER % 2)
    x.t3 = user("a08m49c_t3", MGR, TIER % 3)
    x.t4 = user("a08m49c_t4", MGR, TIER % 4)
    x.t5 = user("a08m49c_t5", MGR, TIER % 5)
    x.e1 = env["hr.employee"].create({"name": "A08M49 custodian 1", "company_id": x.co.id})
    x.e2 = env["hr.employee"].create({"name": "A08M49 custodian 2", "company_id": x.co.id})
    x.buyer = env["res.partner"].create({"name": "A08M49 buyer %s" % n})
    return x


# ------------------------------------------------------------------ helpers
def _post(c, lines, when=None):
    """A posted journal entry: the arrangement of what AP / M19 posted."""
    move = c.cenv["account.move"].create(
        {
            "journal_id": c.journal.id,
            "date": when or c.today,
            "line_ids": [
                (0, 0, {"account_id": a.id, "name": lbl, "debit": dr, "credit": cr})
                for a, dr, cr, lbl in lines
            ],
        }
    )
    move.action_post()
    return move


def _approve(record, approver):
    task = approve_via_inbox(record, approver)
    record.invalidate_recordset()
    return task


def budget(c, amount=1000000.0, by=None, approve_by=None):
    b = c.as_(by or c.mgr)["fix.capex.budget"].create(
        {
            "name": "A08M49 FY26-27",
            "date_from": date(2026, 7, 1),
            "date_to": date(2027, 6, 30),
            "amount": amount,
        }
    )
    if approve_by:
        b.with_user(approve_by).action_approve()
    return b


def request(c, b, amount=100000.0, by=None, **kw):
    vals = {
        "title": "A08M49 diagnostic bench",
        "request_date": date(2026, 10, 1),
        "category_id": c.cat.id,
        "budget_id": b.id if b else False,
        "amount": amount,
        "justification": "Bench for the Dhaka hub",
        # FIN-01/02: an M49 entry posts on its own branch, never the first OU
        "operating_unit_id": c.ou.id,
    }
    vals.update(kw)
    return c.as_(by or c.acc1)["fix.capex.request"].create(vals)


def approved_capex(c, amount=100000.0, approver=None):
    b = budget(c, amount=max(amount * 2, 1000000.0), by=c.mgr, approve_by=c.mgr2)
    r = request(c, b, amount=amount)
    r.with_user(c.acc1).action_submit()
    by_tier = {"tier_2": c.t2, "tier_3": c.t3, "tier_4": c.t4, "tier_5": c.t5}
    _approve(r, approver or by_tier[r.dofa_tier_required])
    assert r.state == "approved" and r.dofa_approved
    return b, r


def cwip_with_cost(c, r, cost):
    cw = c.env["fix.cwip.entry"].browse(r.with_user(c.acc1).action_create_cwip()["cwip_ids"])
    bill = _post(c, [(c.a["cwip"], cost, 0.0, "capital bill"), (c.a["payable"], 0.0, cost, "AP")])
    cw.with_user(c.acc1).action_book_posted_cost([bill.id])
    return cw


def proper_asset(c, gross=120000.0):
    _b, r = approved_capex(c, gross)
    cw = cwip_with_cost(c, r, gross)
    return cw.with_user(c.acc1).action_capitalise()


def seam_asset(c, gross=120000.0, purchase=date(2026, 1, 15), cat=None, life=12, **kw):
    """An asset in service from the M19 capitalisation seam (a posted
    acquisition on the asset account), activated by an accountant."""
    cat = cat or c.cat
    move = _post(
        c,
        [(cat.asset_account_id, gross, 0.0, "acquisition"), (c.a["payable"], 0.0, gross, "AP")],
        when=purchase,
    )
    line = move.line_ids.filtered(lambda ln: ln.account_id == cat.asset_account_id)
    seam = c.cenv["fix.fixed.asset.seam"].create(
        {
            "operating_unit_id": c.ou.id,
            "name": "SEAM-%s" % next(_SEQ),
            "move_line_id": line.id,
            "amount": gross,
        }
    )
    vals = {
        "name": "A08M49 bench",
        "category_id": cat.id,
        "gross": gross,
        "salvage": 0.0,
        "life_months": life,
        "purchase_date": purchase,
        "seam_id": seam.id,
        "operating_unit_id": c.ou.id,
    }
    vals.update(kw)
    a = c.as_(c.acc1)["fix.fixed.asset"].create(vals)
    a.with_user(c.acc1).action_activate()
    return a


def dep_run(c, a, month, year=2026, book="book", by=None, post=True):
    run = c.as_(by or c.acc1)["fix.asset.depreciation.run"].create(
        {"period_start": date(year, month, 1), "asset_ids": [(6, 0, a.ids)], "book": book}
    )
    run.action_compute()
    if post:
        run.action_post()
    return run


def balance(c, account):
    c.env.flush_all()
    lines = c.env["account.move.line"].search(
        [("account_id", "=", account.id), ("parent_state", "=", "posted")]
    )
    return round(sum(lines.mapped("debit")) - sum(lines.mapped("credit")), 2)


def _disposal(c, a, by=None, **kw):
    vals = {
        "asset_id": a.id,
        "kind": "sale",
        "date": c.today,
        "proceeds": 100000.0,
        "partner_id": c.buyer.id,
        "proceeds_account_id": c.a["proceeds"].id,
        "reason": "Obsolete",
    }
    vals.update(kw)
    return c.as_(by or c.acc1)["fix.asset.disposal"].create(vals)


def _reval(c, a, by=None, value=150000.0, report=True, **kw):
    vals = {
        "asset_id": a.id,
        "kind": "revaluation",
        "date": c.today,
        "new_value": value,
        "basis": "Independent valuer, market approach",
    }
    if report:
        att = c.as_(by or c.acc1)["ir.attachment"].create(
            {"name": "valuer.pdf", "datas": base64.b64encode(b"%PDF-1.4 valuer report")}
        )
        vals["valuer_report_ids"] = [(6, 0, att.ids)]
    vals.update(kw)
    return c.as_(by or c.acc1)["fix.asset.revaluation"].create(vals)


def _lease(c, by=None, **kw):
    vals = {
        "name": "A08M49 lease",
        "category_id": c.cat_rou.id,
        "commencement_date": date(2026, 1, 1),
        "term_months": 12,
        "payment_amount": 10000.0,
        "payment_timing": "arrears",
        "ibr_percent": 12.0,
        "liability_account_id": c.a["liability"].id,
        "interest_account_id": c.a["interest"].id,
        "payment_account_id": c.a["rent"].id,
        "operating_unit_id": c.ou.id,
    }
    vals.update(kw)
    return c.as_(by or c.acc1)["fix.lease"].create(vals)


def _confirm_tax_rate(c, code):
    """The adviser's confirmation of a seeded Third Schedule rate (M51)."""
    rate = c.env["fix.tax.rate"].find_rate("depreciation", code, date(2026, 6, 1), c.co)
    if rate.verify_with_adviser:
        rate.with_user(c.mgr).action_record_adviser_verification("ADV-THIRD-SCHEDULE")
    return rate


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    ctl = g.P03GenericApiController()
    cls = g.P03GenericApiController
    mw = getattr(cls.model_write, "original_endpoint", cls.model_write)
    ma = getattr(cls.model_action, "original_endpoint", cls.model_action)
    old = getattr(g, "request", None)

    def call(fn, user, **kw):
        g.request = types.SimpleNamespace(env=c.as_(user))
        return fn(ctl, **kw)

    try:
        yield types.SimpleNamespace(
            write=lambda user, **kw: call(mw, user, **kw),
            action=lambda user, **kw: call(ma, user, **kw),
        )
    finally:
        g.request = old


# ============================================================ reference runs
def test_ref_01_capex_to_cwip_to_asset_proper_path(c):
    b, r = approved_capex(c, 100000.0, approver=c.t3)
    assert (r.approved_by_id, r.dofa_approved_tier) == (c.t3, "tier_3")
    cw = cwip_with_cost(c, r, 90000.0)
    assert cw.amount == 90000.0
    asset = cw.with_user(c.acc1).action_capitalise()
    assert asset.state == "active" and asset.gross == 90000.0 and asset.cwip_id == cw
    assert balance(c, c.a["asset"]) == 90000.0 and balance(c, c.a["cwip"]) == 0.0
    assert r.state == "capitalised" and b.committed_amount == 100000.0
    log = c.env["fix.journal.posting.log"].search([("move_id", "=", cw.move_id.id)])
    assert log.source == "fixed_asset"  # M49-10: posted through M19's API


def test_ref_02_straight_line_book_depreciation_maths(c):
    a = seam_asset(c)
    dep_run(c, a, 1)
    dep_run(c, a, 2)
    assert a.accumulated_depreciation == 20000.0 and a.book_nbv == 100000.0
    assert balance(c, c.a["expense"]) == 20000.0 and balance(c, c.a["accum"]) == -20000.0


def test_disposal_dated_before_posted_depreciation_is_refused(c):
    """E2E3 flow 7: a disposal dated 11 Nov reversed the November charge
    posted on 30 Nov, so between the two dates the GL showed a debit balance on
    accumulated depreciation for an asset that was gone, and the asset was
    charged depreciation after it left the books. The derecognition entry may
    only reverse depreciation posted on or before the disposal date."""
    a = seam_asset(c)
    dep_run(c, a, 1)  # January 2026, posted on 2026-01-31
    d = _disposal(c, a, proceeds=30000.0, date=date(2026, 1, 20))
    d.with_user(c.acc1).action_submit()
    _approve(d, c.t4)
    with pytest.raises(UserError, match="after the disposal date"):
        d.with_user(c.acc2).action_post()
    assert a.state == "active" and d.state == "approved"
    assert not c.env["fix.ar.invoice"].search(
        [("source_model", "=", d._name), ("source_id", "=", d.id)]
    ), "no sale invoice is raised for a refused disposal"


def test_ref_03_disposal_sale_invoiced_with_loss(c):
    a = seam_asset(c)
    dep_run(c, a, 1)
    d = _disposal(c, a, proceeds=30000.0)
    d.with_user(c.acc1).action_submit()
    assert d.dofa_tier_required == "tier_4"  # NBV 110,000 > 25,000
    _approve(d, c.t4)
    d.with_user(c.acc2).action_post()
    assert (d.nbv, d.gain_loss, a.state) == (110000.0, -80000.0, "disposed")
    assert balance(c, c.a["loss"]) == 80000.0 and balance(c, c.a["asset"]) == 0.0
    assert balance(c, c.a["accum"]) == 0.0
    inv = c.env["fix.ar.invoice"].browse(d.sale_invoice_res_id)
    assert inv.exists() and inv.customer_id == c.buyer and inv.taxable_amount == 30000.0


def test_ref_04_revaluation_surplus_maths(c):
    a = seam_asset(c)
    dep_run(c, a, 1)
    rv = _reval(c, a)
    rv.with_user(c.acc1).action_submit()
    _approve(rv, c.t4)
    assert rv.state == "approved" and rv.approved_by_id == c.t4
    rv.with_user(c.acc2).action_post()
    assert (rv.cost_delta, rv.surplus_amount, rv.pl_amount) == (40000.0, 40000.0, 0.0)
    assert a.book_nbv == 150000.0 and balance(c, c.a["surplus"]) == -40000.0


def test_ref_05_lease_ifrs16_maths(c):
    lease = _lease(c)
    lease.with_user(c.acc1).action_activate()
    lines = lease.schedule_line_ids.sorted("sequence")
    assert lease.initial_liability == 112550.77
    assert lines[-1].closing == 0.0
    assert round(sum(lines.mapped("interest")), 2) == round(120000.0 - 112550.77, 2)
    assert balance(c, c.a["liability"]) == -112550.77
    assert lease.asset_id.state == "active" and lease.asset_id.acquisition_move_id == lease.move_id


# ============================================================ capex controls
def test_m49_01_capex_requester_cannot_approve(c):
    b = budget(c, by=c.mgr, approve_by=c.mgr2)
    r = request(c, b, by=c.t3)
    r.with_user(c.t3).action_submit()
    assert c.t3 not in assigned(r)
    _refused(r.with_user(c.t3).action_approve, match="inbox")


def test_m49_02_capex_over_budget_refused(c):
    b = budget(c, amount=50000.0, by=c.mgr, approve_by=c.mgr2)
    r = request(c, b, amount=60000.0)
    _refused(r.with_user(c.acc1).action_submit, match="available amount")


def test_m49_03_accountant_cannot_write_capex_approved(c, p03):
    r = request(c, None, amount=5000000.0)
    _refused(r.with_user(c.acc1).write, {"state": "approved"}, match="cannot be set directly")
    _refused(r.with_user(c.acc1).action_create_cwip, match="approved")


def test_m49_04_accountant_cannot_forge_budget_approval(c):
    b = c.as_(c.acc1)["fix.capex.budget"].create(
        {
            "name": "forged",
            "date_from": date(2026, 7, 1),
            "date_to": date(2027, 6, 30),
            "amount": 1.0,
        }
    )
    _refused(b.with_user(c.acc1).write, {"state": "approved", "amount": 10000000.0})
    _refused(b.with_user(c.acc1).action_approve, match="accounting manager")
    _refused(b.with_user(c.acc1).write, {"prepared_by_id": c.mgr.id})
    b2 = budget(c, by=c.mgr)
    _refused(b2.with_user(c.mgr).action_approve, match="segregation")
    b2.with_user(c.mgr2).action_approve()
    _refused(b2.with_user(c.mgr2).write, {"amount": 99999999.0}, match="frozen")


def test_m49_05_requester_field_cannot_be_rewritten(c):
    b = budget(c, by=c.mgr2, approve_by=c.mgr)
    r = request(c, b, by=c.t3)
    _refused(
        r.with_user(c.t3).write, {"requested_by_id": c.acc2.id}, match="cannot be set directly"
    )
    _refused(
        c.as_(c.acc1)["fix.capex.request"].create,
        {"title": "x", "amount": 1.0, "requested_by_id": c.acc2.id},
        match="cannot be set directly",
    )


def test_m49_06_capex_amount_frozen_after_approval(c):
    _b, r = approved_capex(c, 100000.0)
    _refused(r.with_user(c.acc1).write, {"amount": 900000.0}, match="frozen")
    _refused(r.with_user(c.mgr).write, {"budget_id": False}, match="frozen")
    # capitalisation never exceeds the approved capex
    cw = cwip_with_cost(c, r, 150000.0)
    _refused(cw.with_user(c.acc1).action_capitalise, match="exceeds the approved capex")


def test_m49_07_capitalise_cwip_without_capex_refused(c):
    cw = c.as_(c.acc1)["fix.cwip.entry"].create({"name": "no-capex", "category_id": c.cat.id})
    bill = _post(c, [(c.a["cwip"], 2500000.0, 0.0, "bill"), (c.a["payable"], 0.0, 2500000.0, "AP")])
    cw.with_user(c.acc1).action_book_posted_cost([bill.id])
    _refused(cw.with_user(c.acc1).action_capitalise, match="no capex request")


def test_m49_08_asset_born_active_refused(c):
    vals = {
        "name": "ghost",
        "category_id": c.cat.id,
        "gross": 3000000.0,
        "life_months": 36,
        "purchase_date": date(2026, 1, 15),
    }
    _refused(c.as_(c.acc1)["fix.fixed.asset"].create, dict(vals, state="active"))
    draft = c.as_(c.acc1)["fix.fixed.asset"].create(vals)
    _refused(draft.with_user(c.acc1).action_activate, match="no source")
    # no capitalisation event for a draft asset (M49-11)
    events = c.env["fix.event.outbox"].search(
        [("event_type", "=", "asset.capitalized"), ("aggregate_id", "=", draft.id)]
    )
    assert not events


def test_m49_09_cwip_cost_is_booked_not_typed(c):
    _b, r = approved_capex(c, 800000.0, approver=c.t4)
    cw = c.env["fix.cwip.entry"].browse(r.with_user(c.acc1).action_create_cwip()["cwip_ids"])
    _refused(cw.with_user(c.acc1).write, {"amount": 750000.0}, match="cannot be set directly")
    _refused(cw.with_user(c.acc1).action_capitalise, match="Nothing accumulated")
    wrong = _post(c, [(c.a["other"], 1000.0, 0.0, "x"), (c.a["payable"], 0.0, 1000.0, "AP")])
    _refused(cw.with_user(c.acc1).action_book_posted_cost, [wrong.id], match="No posted CWIP cost")
    bill = _post(c, [(c.a["cwip"], 700000.0, 0.0, "bill"), (c.a["payable"], 0.0, 700000.0, "AP")])
    cw.with_user(c.acc1).action_book_posted_cost([bill.id])
    other = c.as_(c.acc1)["fix.cwip.entry"].create({"name": "steal", "category_id": c.cat.id})
    _refused(
        other.with_user(c.acc1)._fix_book_cost,
        bill.line_ids,
        match="already booked|not on the CWIP",
    )
    # the CWIP GL balance is the ceiling: someone credited CWIP elsewhere
    _post(c, [(c.a["payable"], 650000.0, 0.0, "x"), (c.a["cwip"], 0.0, 650000.0, "reclass")])
    _refused(cw.with_user(c.acc1).action_capitalise, match="below zero")


def test_m49_10_cwip_on_unapproved_request_refused(c):
    b = budget(c, by=c.mgr, approve_by=c.mgr2)
    r = request(c, b, amount=100000.0)
    cw = c.as_(c.acc1)["fix.cwip.entry"].create(
        {"name": "draft-capex", "category_id": c.cat.id, "capex_request_id": r.id}
    )
    bill = _post(c, [(c.a["cwip"], 99000.0, 0.0, "bill"), (c.a["payable"], 0.0, 99000.0, "AP")])
    cw.with_user(c.acc1).action_book_posted_cost([bill.id])
    _refused(cw.with_user(c.acc1).action_capitalise, match="approved capex")


def test_m49_11_dofa_tier_by_amount(c):
    b = budget(c, amount=60000000.0, by=c.mgr2, approve_by=c.mgr)
    r = request(c, b, amount=50000000.0)
    r.with_user(c.acc1).action_submit()
    assert r.dofa_tier_required == "tier_5"
    assert c.t4 not in assigned(r) and c.mgr not in assigned(r)
    _refused(r.with_user(c.mgr2).action_approve, match="inbox")
    _approve(r, c.t5)
    assert (r.state, r.dofa_approved_tier) == ("approved", "tier_5")


def test_m49_12_billing_and_plain_users_cannot_touch_capex(c):
    for u in (c.bill, c.plain):
        _refused(c.as_(u)["fix.capex.request"].create, {"title": "x", "amount": 1.0})
        _refused(
            c.as_(u)["fix.fixed.asset"].create,
            {"name": "x", "gross": 1.0, "life_months": 1, "purchase_date": c.today},
        )


# ============================================================ depreciation
def test_m49_20_double_run_same_month_skipped(c):
    a = seam_asset(c)
    dep_run(c, a, 1)
    run2 = dep_run(c, a, 1, post=False)
    assert not run2.line_ids and a.accumulated_depreciation == 10000.0
    _refused(run2.with_user(c.acc1).action_post, match="nothing to post")


def test_m49_21_run_state_forged_refused(c):
    a = seam_asset(c)
    run = dep_run(c, a, 1, post=False)
    _refused(run.with_user(c.acc1).write, {"state": "posted"}, match="cannot be set directly")
    assert a.accumulated_depreciation == 0.0


def test_m49_22_future_month_refused(c):
    a = seam_asset(c, gross=360000.0, life=36)
    _refused(dep_run, c, a, 10, year=2027, match="not yet reached")


def test_m49_23_posted_line_immutable(c):
    a = seam_asset(c)
    dep_run(c, a, 1)
    dep_run(c, a, 2)
    lines = a.depreciation_line_ids.sorted("period_start")
    _refused(lines[0].with_user(c.acc1).write, {"amount": 1.0})
    _refused(lines[1].with_user(c.acc1).unlink)
    _refused(lines[1].sudo().unlink, match="never deleted")
    _refused(lines[0].sudo().write, {"amount": 1.0}, match="never edited")
    assert a.accumulated_depreciation == -balance(c, c.a["accum"]) == 20000.0


def test_m49_24_abandoned_run_does_not_block_the_month(c):
    a = seam_asset(c)
    abandoned = dep_run(c, a, 1, post=False)
    run_b = dep_run(c, a, 1, by=c.acc2, post=False)
    assert run_b.line_ids and not abandoned.line_ids
    run_b.with_user(c.acc2).action_post()
    feb = dep_run(c, a, 2, by=c.acc2)
    assert feb.total_amount == 10000.0 and -balance(c, c.a["accum"]) == 20000.0


def test_m49_25_tax_book_annual_wdv(c):
    _confirm_tax_rate(c, "ITA3-COMPUTER")
    a = seam_asset(c, gross=100000.0, cat=c.cat_it, life=36, purchase=date(2026, 1, 10))
    for m in range(1, 11):
        dep_run(c, a, m, book="tax")
    # 10 of the year's 12 months, at 30% of the opening WDV: 2,500 each
    assert a.tax_accumulated == 25000.0


def test_m49_25b_tax_year_lands_on_the_annual_allowance():
    from odoo.addons.cd_fixed_asset_ext.models.fix_fixed_asset import annual_wdv_month

    charged = 0.0
    for m in range(12):
        charged += annual_wdv_month(100000.0, 30.0, m, charged)
    assert round(charged, 2) == 30000.0
    # the second year runs on the written-down value
    assert annual_wdv_month(70000.0, 30.0, 0, 0.0) == 1750.0


def test_m49_26_unverified_tax_rate_refused(c):
    a = seam_asset(c, gross=100000.0, cat=c.cat_it, life=36)
    rate = c.env["fix.tax.rate"].find_rate("depreciation", "ITA3-COMPUTER", date(2026, 1, 1), c.co)
    assert rate.verify_with_adviser
    _refused(dep_run, c, a, 1, book="tax", match="not yet confirmed")


def test_m49_27_billing_user_cannot_post_depreciation(c):
    a = seam_asset(c)
    _refused(dep_run, c, a, 1, by=c.bill)


def test_m49_28_cost_frozen_in_service(c):
    a = seam_asset(c)
    dep_run(c, a, 1)
    _refused(a.with_user(c.acc1).write, {"gross": 1200000.0}, match="frozen")


def test_m49_29_locked_period_refused(c):
    a = seam_asset(c)
    c.co.sudo().write({"fiscalyear_lock_date": date(2026, 6, 30)})
    _refused(dep_run, c, a, 3, match="closed period")
    assert not a.depreciation_line_ids


def test_m49_29b_m19_closed_period_refused(c):
    if "fix.period.close" not in c.env:
        pytest.skip("cd_gl_ext period close not installed")
    a = seam_asset(c)
    c.cenv["fix.period.close"].create(
        {"company_id": c.co.id, "period_end": date(2026, 2, 28), "state": "closed"}
    )
    _refused(dep_run, c, a, 2, match="closed period")


# ============================================================ disposal
def test_m49_30_disposal_requester_cannot_approve(c):
    a = seam_asset(c)
    d = _disposal(c, a, by=c.t4)
    d.with_user(c.t4).action_submit()
    assert c.t4 not in assigned(d)
    _refused(d.with_user(c.t4).action_approve, match="inbox")


def test_m49_31_disposal_state_forged_refused(c):
    a = seam_asset(c)
    d = _disposal(c, a, kind="write_off", proceeds=0.0, incident_ref="GD-1")
    _refused(d.with_user(c.acc1).write, {"state": "approved"}, match="cannot be set directly")
    _refused(d.with_user(c.acc1).action_post, match="Approve")


def test_m49_32_disposal_requester_rewrite_refused(c):
    a = seam_asset(c)
    d = _disposal(c, a, by=c.mgr)
    _refused(
        d.with_user(c.mgr).write, {"requested_by_id": c.acc2.id}, match="cannot be set directly"
    )


def test_m49_33_disposal_terms_pinned(c):
    a = seam_asset(c)
    d = _disposal(c, a)
    d.with_user(c.acc1).action_submit()
    _approve(d, c.t4)
    assert d.state == "approved" and d.dofa_approved
    d.with_user(c.acc1).write({"proceeds": 1.0})
    assert (d.state, d.dofa_approved) == ("draft", False)
    _refused(d.with_user(c.acc1).action_post, match="Approve")


def test_m49_34_asset_state_disposed_refused(c):
    a = seam_asset(c)
    _refused(a.with_user(c.acc1).write, {"state": "disposed"}, match="cannot be set directly")


def test_m49_35_large_write_off_needs_the_cfo_tier(c):
    a = seam_asset(c, gross=40000000.0)
    d = _disposal(c, a, kind="write_off", proceeds=0.0, incident_ref="GD-2026-77")
    d.with_user(c.acc1).action_submit()
    assert d.dofa_tier_required == "tier_4"
    assert c.t2 not in assigned(d) and c.mgr not in assigned(d)
    _approve(d, c.t4)
    d.with_user(c.acc2).action_post()
    assert d.state == "posted" and a.state == "disposed" and d.gain_loss == -40000000.0


def test_m49_36_disposal_posted_by_write_refused(c):
    a = seam_asset(c)
    d = _disposal(c, a)
    _refused(d.with_user(c.acc1).write, {"state": "posted"}, match="cannot be set directly")


def test_m49_37_write_off_needs_incident(c):
    a = seam_asset(c)
    d = _disposal(c, a, kind="write_off", proceeds=0.0, reason=False)
    _refused(d.with_user(c.acc1).action_submit, match="incident reference")


def test_m49_38_useful_life_frozen(c):
    a = seam_asset(c)
    dep_run(c, a, 1)
    _refused(a.with_user(c.acc1).write, {"life_months": 2}, match="frozen")


# ============================================================ revaluation
def test_m49_40_revaluation_requester_cannot_approve(c):
    a = seam_asset(c)
    rv = _reval(c, a, by=c.t4)
    rv.with_user(c.t4).action_submit()
    assert c.t4 not in assigned(rv)
    _refused(rv.with_user(c.t4).action_approve, match="inbox")


def test_m49_41_forged_posted_revaluation_refused(c):
    a = seam_asset(c)
    rv = _reval(c, a)
    _refused(
        rv.with_user(c.acc1).write,
        {"state": "posted", "cost_delta": 1000000.0, "surplus_amount": 1000000.0},
        match="cannot be set directly",
    )
    _refused(rv.with_user(c.acc1).action_post, match="once approved")


def test_m49_42_revaluation_requester_rewrite_refused(c):
    a = seam_asset(c)
    rv = _reval(c, a, by=c.mgr, value=500000.0)
    _refused(
        rv.with_user(c.mgr).write, {"requested_by_id": c.acc2.id}, match="cannot be set directly"
    )


def test_m49_43_revaluation_needs_valuer_report_and_approval(c):
    a = seam_asset(c)
    rv = _reval(c, a, value=900000.0, report=False)
    _refused(rv.with_user(c.acc1).action_submit, match="valuer")
    ok = _reval(c, a, value=900000.0)
    ok.with_user(c.acc1).action_submit()
    assert ok.dofa_tier_required == "tier_4"
    _refused(ok.with_user(c.mgr).action_post, match="once approved")


# ============================================================ transfer / verification
def test_m49_50_branch_moves_only_by_acknowledged_transfer(c):
    a = seam_asset(c, custodian_id=c.e1.id)
    _refused(a.with_user(c.acc1).write, {"operating_unit_id": c.ou2.id}, match="transfer")
    t = c.as_(c.acc1)["fix.asset.transfer"].create(
        {"asset_id": a.id, "operating_unit_id": c.ou2.id}
    )
    t.with_user(c.acc1).action_confirm()
    assert a.operating_unit_id == c.ou  # not moved until acknowledged
    _refused(t.with_user(c.acc1).action_acknowledge, match="Segregation")
    t.with_user(c.acc2).action_acknowledge()
    assert (a.operating_unit_id, t.state, t.acknowledged_by_id) == (c.ou2, "done", c.acc2)


def test_m49_51_verification_result_typed_refused(c):
    a = seam_asset(c)
    camp = c.as_(c.acc1)["fix.asset.verification.campaign"].create(
        {"name": "count", "operating_unit_id": c.ou.id}
    )
    camp.with_user(c.acc1).action_start()
    line = camp.line_ids.filtered(lambda ln: ln.asset_id == a)
    _refused(line.with_user(c.acc1).write, {"result": "found"}, match="cannot be set directly")
    _refused(line.with_user(c.acc1).action_mark_found, match="counter")
    line.with_user(c.acc2).action_mark_found()
    assert (line.result, line.corrected_by_id) == ("found", c.acc2)
    camp.with_user(c.acc1).action_record_scan(a.code)
    assert line.result == "found"


def test_m49_52_custodian_moves_only_by_transfer(c):
    a = seam_asset(c, custodian_id=c.e1.id)
    _refused(a.with_user(c.acc1).write, {"custodian_id": c.e2.id}, match="transfer")
    assert a.custodian_id == c.e1 and not a.transfer_ids


# ============================================================ lease
def test_m49_60_lease_state_forged_refused(c):
    lease = _lease(c)
    _refused(lease.with_user(c.acc1).write, {"state": "active"}, match="cannot be set directly")


def test_m49_61_future_lease_months_refused(c):
    lease = _lease(c, commencement_date=date(2026, 11, 1))
    lease.with_user(c.acc1).action_activate()
    _refused(lease.schedule_line_ids.with_user(c.acc1).action_post, match="not yet reached")
    lease.with_user(c.acc1).action_post_due()  # the due month (2026-11) only
    posted = lease.schedule_line_ids.filtered(lambda ln: ln.state == "posted")
    assert posted.mapped("period_start") == [date(2026, 11, 1)]


def test_m49_62_lease_terms_frozen_after_recognition(c):
    lease = _lease(c)
    lease.with_user(c.acc1).action_activate()
    _refused(
        lease.with_user(c.acc1).write,
        {"payment_amount": 50000.0, "ibr_percent": 1.0},
        match="frozen",
    )
    _refused(lease.schedule_line_ids[:1].with_user(c.acc1).write, {"payment": 1.0})


# ============================================================ P03 surface / wiring
def test_m49_70_surfaces_declare_writable(c):
    from odoo.addons.cd_p03_portal.controllers.a08 import m49 as surf

    missing = [m for m, conf in surf.SURFACES.items() if "writable" not in conf]
    assert not missing, missing
    for model in ("fix.capex.request", "fix.asset.disposal", "fix.asset.revaluation"):
        assert "action_approve" not in surf.SURFACES[model]["actions"], model


def test_m49_71_p03_write_capex_state_refused(c, p03):
    r = request(c, None)
    out = p03.write(c.acc1, model="fix.capex.request", record_id=r.id, values={"state": "approved"})
    r.invalidate_recordset()
    assert r.state == "draft", out


def test_m49_72_p03_write_disposal_and_reval_state_refused(c, p03):
    a = seam_asset(c)
    d = _disposal(c, a)
    rv = _reval(c, a)
    o1 = p03.write(c.acc1, model="fix.asset.disposal", record_id=d.id, values={"state": "approved"})
    o2 = p03.write(
        c.acc1, model="fix.asset.revaluation", record_id=rv.id, values={"state": "posted"}
    )
    d.invalidate_recordset()
    rv.invalidate_recordset()
    assert d.state == "draft" and rv.state == "draft", (o1, o2)


def test_m49_73_p03_action_approve_refused(c, p03):
    b = budget(c, by=c.mgr, approve_by=c.mgr2)
    r = request(c, b, by=c.acc2)
    r.with_user(c.acc2).action_submit()
    out = p03.action(c.t3, model="fix.capex.request", ids=[r.id], method="action_approve")
    r.invalidate_recordset()
    assert not out.get("success") and r.state == "submitted", out


def test_m49_74_p03_requester_rewrite_refused(c, p03):
    a = seam_asset(c)
    d = _disposal(c, a, by=c.mgr)
    p03.write(
        c.mgr, model="fix.asset.disposal", record_id=d.id, values={"requested_by_id": c.acc2.id}
    )
    d.invalidate_recordset()
    assert d.requested_by_id == c.mgr


def test_m49_80_events_have_registered_consumers(c):
    for xmlid, event in (
        ("consumer_asset_capitalized_gl_tieout", "asset.capitalized"),
        ("consumer_depreciation_accrued_gl_tieout", "depreciation.accrued"),
        ("consumer_asset_disposed_gl_tieout", "asset.disposed"),
    ):
        sub = c.env.ref("cd_fixed_asset_ext.%s" % xmlid)
        assert (sub.event_type, sub.model, sub.method) == (
            event,
            "fix.fixed.asset",
            "consume_asset_event",
        )
    a = proper_asset(c, 40000.0)
    ev = c.env["fix.event.outbox"].search(
        [("event_type", "=", "asset.capitalized"), ("aggregate_id", "=", a.id)]
    )
    assert len(ev) == 1
    event = {
        "event_type": "asset.capitalized",
        "aggregate_id": a.id,
        "payload": {"move_id": a.acquisition_move_id.id},
    }
    assert c.env["fix.fixed.asset"].consume_asset_event(event) is True
    assert c.env["fix.fixed.asset"].consume_asset_event(dict(event, payload={})) is False


def test_m49_81_capex_reject_and_resubmit(c):
    b = budget(c, by=c.mgr, approve_by=c.mgr2)
    r = request(c, b, amount=40000.0)
    r.with_user(c.acc1).action_submit()
    assert r.dofa_tier_required == "tier_2" and c.t2 in assigned(r)
    _refused(r.with_user(c.acc1).action_reject, match="accounting manager")
    r.with_user(c.mgr).action_reject()
    assert r.state == "rejected"
    r.with_user(c.acc1).write({"amount": 30000.0})
    r.with_user(c.acc1).action_submit()
    _approve(r, c.t2)
    assert r.state == "approved"


def test_m49_82_register_reconciles_to_the_gl(c):
    """BRU-FXA-03 (M49-10): the register against its control accounts."""
    a = seam_asset(c)
    dep_run(c, a, 1)
    rows = c.env["fix.fixed.asset"]._fix_register_gl_reconciliation(c.co)
    by_line = {(r["account"], r["line"]): r for r in rows}
    cost = by_line[(c.a["asset"].display_name, "cost")]
    accum = by_line[(c.a["accum"].display_name, "accumulated")]
    assert (cost["register"], cost["gl"], cost["variance"]) == (120000.0, 120000.0, 0.0)
    assert (accum["register"], accum["gl"], accum["variance"]) == (-10000.0, -10000.0, 0.0)
