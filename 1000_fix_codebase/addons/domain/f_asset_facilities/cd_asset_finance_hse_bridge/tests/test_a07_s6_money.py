"""A07 ERP audit (2026-11-20), stream S6: the A07 money paths reach the GL.

Live ORM, rolled back. Accounts are created per test (fix_real's chart is not
in the test template) and wired through the account-role parameters the seed
sets on fix_real/fix_dev (decisions D1-D3). Each test names the finding it
proves; decisions are taken as non-admin users holding the real role.
"""

from __future__ import annotations

import itertools
import types
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.addons.cd_fixed_asset_ext.models.fix_asset_common import month_start
from odoo.addons.cd_fixed_asset_ext.models.fix_lease import (
    lease_payment_vector,
    lease_present_value,
    lease_present_value_vector,
)
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

REFUSED = (UserError, ValidationError, AccessError)
MOD = "cd_asset_finance_hse_bridge"
P = "cd_asset_finance_hse_bridge."
ACC = "account.group_account_user"
MGR = "account.group_account_manager"
_SEQ = itertools.count(1)


def _refused(fn, *args, match=None, **kw):
    with pytest.raises(REFUSED, match=match), fn.__self__.env.cr.savepoint():
        fn(*args, **kw)


@pytest.fixture
def m(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.co = env.company
    x.co.vat = x.co.vat or "1234567890123"
    tag = next(_SEQ)
    x.tag = tag
    x.today = fields.Date.context_today(env["res.users"].with_context(tz="Asia/Dhaka"))
    Account = env["account.account"]
    icp = env["ir.config_parameter"].sudo()

    def acc(code, name, kind):
        full = "S6%02d%s" % (tag, code)
        return Account.search(
            [("code", "=", full), ("company_ids", "in", x.co.id)], limit=1
        ) or Account.create(
            {"code": full, "name": name, "account_type": kind, "company_ids": [(6, 0, x.co.ids)]}
        )

    x.a = {
        "fuel": acc("01", "Fuel Expense", "expense"),
        "auto": acc("02", "Auto Maintenance", "expense"),
        "rent": acc("03", "Office Rent", "expense"),
        "repair": acc("04", "Repair & Maintenance", "expense"),
        "fine": acc("05", "Penalty Expense", "expense"),
        "clearing": acc("06", "Rent Payable Clearing (IFRS 16)", "liability_current"),
        "liability": acc("07", "Lease Liability (IFRS 16)", "liability_non_current"),
        "interest": acc("08", "Interest on Lease Liability", "expense"),
        "rou": acc("09", "Right of use Asset", "asset_fixed"),
        "rou_acc": acc("10", "Acc. Depreciation ROU", "asset_fixed"),
        "rou_dep": acc("11", "Depreciation ROU", "expense_depreciation"),
        "gain": acc("12", "Gain on Disposal", "income_other"),
        "loss": acc("13", "Loss on Disposal", "expense"),
        "petty": acc("14", "Petty Cash Branch", "asset_cash"),
        "card": acc("15", "Fuel Card Clearing", "liability_current"),
        "emp_pay": acc("16", "Employee Payable", "liability_current"),
        "emp_rec": acc("17", "Employee Recovery Receivable", "asset_current"),
        "ins_rec": acc("18", "Insurance Claim Receivable", "asset_current"),
        "eq_loss": acc("19", "Loss on Disposal (recharge)", "expense"),
        "veh": acc("20", "Vehicle", "asset_fixed"),
        "veh_acc": acc("21", "Acc. Dep. Vehicles", "asset_fixed"),
        "veh_dep": acc("22", "Dep. Vehicles", "expense_depreciation"),
        "proceeds": acc("23", "Disposal Proceeds Clearing", "asset_current"),
        "vat_in": acc("24", "Input VAT", "asset_current"),
        "tds": acc("25", "TDS payable", "liability_current"),
        "vds": acc("26", "VDS payable", "liability_current"),
    }
    for key, account in (
        ("vehicle_fuel", "fuel"),
        ("vehicle_service", "auto"),
        ("lease_rent", "rent"),
        ("facility_work_order", "repair"),
        ("site_utility", "repair"),
        ("vehicle_fine", "fine"),
        ("vehicle_renewal", "auto"),
        ("petty_cash", "petty"),
        ("fuel_card_clearing", "card"),
        ("employee_recovery_receivable", "emp_rec"),
        ("insurance_claim_receivable", "ins_rec"),
        ("recovery.equipment_loss", "eq_loss"),
        ("recovery.insurance", "auto"),
        ("disposal_proceeds", "proceeds"),
    ):
        icp.set_param(P + "account." + key, x.a[account].code)
    for param, key in (
        ("cd_ap_ext.account_code.employee_payable", "emp_pay"),
        ("cd_tax_engine_bd.vat_input_account_code", "vat_in"),
        ("cd_tax_engine_bd.account_code.tds_payable", "tds"),
        ("cd_tax_engine_bd.account_code.vds_payable", "vds"),
    ):
        icp.set_param(param, x.a[key].code)
    x.journal = env["account.journal"].create(
        {"name": "S6 FA %s" % tag, "code": "S6F%s" % (tag % 100), "type": "general"}
    )
    x.cat_rou = env["fix.asset.category"].create(
        {
            "company_id": x.co.id,
            "code": "S6ROU%s" % tag,
            "name": "S6 Right of Use",
            "journal_id": x.journal.id,
            "asset_account_id": x.a["rou"].id,
            "accumulated_account_id": x.a["rou_acc"].id,
            "expense_account_id": x.a["rou_dep"].id,
            "gain_account_id": x.a["gain"].id,
            "loss_account_id": x.a["loss"].id,
        }
    )
    x.cat_veh = env["fix.asset.category"].create(
        {
            "company_id": x.co.id,
            "code": "S6VEH%s" % tag,
            "name": "S6 Vans",
            "useful_life_months": 60,
            "journal_id": x.journal.id,
            "asset_account_id": x.a["veh"].id,
            "accumulated_account_id": x.a["veh_acc"].id,
            "expense_account_id": x.a["veh_dep"].id,
            "gain_account_id": x.a["gain"].id,
            "loss_account_id": x.a["loss"].id,
        }
    )

    def ou(code):
        return env["operating.unit"].create(
            {
                "name": "S6 OU %s %s" % (code, tag),
                "code": "S6%s%s" % (code, tag),
                "company_id": x.co.id,
                "partner_id": x.co.partner_id.id,
            }
        )

    x.ou, x.ou2 = ou("A"), ou("B")

    def user(login, *groups):
        ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": "s6%s_%s" % (tag, login),
                    "group_ids": [(6, 0, ids)],
                    "company_ids": [(6, 0, x.co.ids)],
                    "company_id": x.co.id,
                    "assigned_operating_unit_ids": [(6, 0, (x.ou | x.ou2).ids)],
                    "default_operating_unit_id": x.ou.id,
                }
            )
        )

    x.acct = user("acct", ACC)
    x.acct2 = user("acct2", ACC)
    x.mgr = user("mgr", MGR)
    x.clerk = user("clerk")
    x.bol = user("bol", "cd_facility.group_branch_operations_lead")
    x.lm = user("lm", "cd_vehicle_ext.group_logistics_manager")
    x.cfo = user("cfo", "cd_entity_config.group_dofa_tier_4")
    x.hr = user("hr", "hr.group_hr_manager")
    x.vendor = env["res.partner"].create({"name": "S6 Garage %s" % tag})
    x.landlord = env["res.partner"].create({"name": "S6 Landlord %s" % tag})
    x.employee = env["hr.employee"].create({"name": "S6 Driver %s" % tag, "company_id": x.co.id})
    x.product = env["product.product"].create({"name": "S6 service", "type": "service"})
    brand = env["fleet.vehicle.model.brand"].create({"name": "S6 Brand %s" % tag})
    x.model = env["fleet.vehicle.model"].create({"name": "S6 Van", "brand_id": brand.id})
    return x


def _ou(m, lines):
    """The operating units of journal items (M19 dimension rows)."""
    dims = m.env["fix.journal.dimension"].sudo().search([("move_line_id", "in", lines.ids)])
    return dims.mapped("operating_unit_id")


def _as(m, user, model):
    return m.env(user=user.id, context=dict(m.env.context, allowed_company_ids=m.co.ids))[model]


def _van(m, plate, ou=None, **kw):
    vals = {
        "model_id": m.model.id,
        "license_plate": plate,
        "company_id": m.co.id,
        "operating_unit_id": (ou or m.ou).id,
    }
    vals.update(kw)
    return m.env["fleet.vehicle"].create(vals)


def _entry(m, cost_type="vehicle_service", amount=5000.0, **kw):
    """A cost the way a module stream hands it over (_m52_queue) on a source."""
    src = kw.pop("source", None) or m.env["res.partner"].create(
        {"name": "S6 source %s" % next(_SEQ)}
    )
    vals = {
        "cost_type": cost_type,
        "company_id": m.co.id,
        "operating_unit_id": m.ou.id,
        "amount": amount,
        "cost_date": m.today,
        "vendor_id": m.vendor.id,
        "invoice_ref": "GAR-77",
        "payment_method": "vendor_bill",
    }
    vals.update(kw)
    return m.env["fix.asset.cost.entry"]._m52_queue(src, vals)


def _bill(m, vendor, amounts, ou=None, ref="GAR-77"):
    return m.env["fix.vendor.invoice"].create(
        {
            "company_id": m.co.id,
            "operating_unit_id": (ou or m.ou).id,
            "vendor_id": vendor.id,
            "invoice_ref": ref,
            "bill_type": "non_po",
            "line_ids": [
                (0, 0, {"product_id": m.product.id, "description": "line %s" % i, "unit_price": a})
                for i, a in enumerate(amounts)
            ],
        }
    )


def _post_bill(bill):
    bill.sudo()._guarded().write({"approval_state": "approved"})
    bill.sudo()._post_approved_bill()
    return bill.move_id


# ============================================================ M52 money contract
def test_vendor_bill_cost_pins_payee_invoice_and_branch_and_posts_its_account(m):
    """FIN-05, M46-02, M46-04, M47-13, M47-37: the bill line posts the D3 account."""
    entry = _entry(m, amount=5000.0)
    assert entry.state == "pending" and entry.account_id == m.a["auto"]
    mine = _as(m, m.acct, "fix.asset.cost.entry").browse(entry.id)
    other = m.env["res.partner"].create({"name": "S6 other garage"})
    _refused(mine.action_match_bill, _bill(m, other, [5000.0]).id, match="vendor")
    _refused(mine.action_match_bill, _bill(m, m.vendor, [5000.0], ref="X-1").id, match="invoice")
    _refused(mine.action_match_bill, _bill(m, m.vendor, [5000.0], ou=m.ou2).id, match="branch")
    two = _bill(m, m.vendor, [5000.0, 7000.0])
    mine.action_match_bill(two.id)  # the line of the same amount is found
    assert entry.state == "matched" and entry.vendor_invoice_line_id.line_total == 5000.0
    # A06 ERP audit P09 / BRU-PRO-02: the 7,000 line carries no A07 source
    # document, and the garage is not in the M42 register, so an accounting
    # administrator records the non-PO exception (a bill backed line by line
    # by A07 cost entries needs none)
    two.with_user(m.mgr).action_approve_non_po_exception(
        reason="Second line: garage work outside the matched vehicle service"
    )
    move = _post_bill(two)
    line = move.line_ids.filtered(lambda ln: ln.account_id == m.a["auto"])
    assert line.debit == 5000.0 and _ou(m, line) == m.ou
    assert entry.state == "posted" and entry.move_id == move
    # an entry with no vendor is never matched to whatever bill has headroom
    blind = _entry(m, vendor_id=False, invoice_ref=False)
    _refused(
        _as(m, m.acct, "fix.asset.cost.entry").browse(blind.id).action_match_bill,
        _bill(m, m.vendor, [5000.0]).id,
        match="names no vendor",
    )


def test_unset_account_role_fails_closed(m):
    """D3 / brief rule 4: no account role, no posting (no guessed account)."""
    m.env["ir.config_parameter"].sudo().set_param(P + "account.vehicle_service", "")
    entry = _entry(m)
    assert not entry.account_id
    _refused(
        _as(m, m.acct, "fix.asset.cost.entry").browse(entry.id).action_match_bill,
        _bill(m, m.vendor, [5000.0]).id,
        match="account.vehicle_service",
    )


def test_petty_cash_employee_and_fuel_card_post_on_the_branch(m):
    """FIN-05 / M46-03: non-bill costs post their own entry."""
    fund = m.env["fix.imprest.fund"].sudo().search([("operating_unit_id", "=", m.ou.id)])
    assert not fund  # the role param stands in for a branch with no M50 fund
    cash = _entry(m, "vehicle_fuel", 1200.0, payment_method="cash", vendor_id=False)
    assert cash.payment_method == "petty_cash" and cash.state == "posted"
    lines = cash.move_id.line_ids
    assert lines.filtered(lambda ln: ln.account_id == m.a["fuel"]).debit == 1200.0
    assert lines.filtered(lambda ln: ln.account_id == m.a["petty"]).credit == 1200.0
    assert set(_ou(m, lines)) == {m.ou}
    paid = _entry(m, "vehicle_fine", 900.0, payment_method="employee_expense", vendor_id=False)
    assert paid.state == "pending" and "employee who paid" in paid.message_ids[0].body
    paid2 = _entry(
        m, "vehicle_fine", 900.0, payment_method="employee_expense", employee_id=m.employee.id
    )
    assert paid2.state == "posted"
    assert (
        paid2.move_id.line_ids.filtered(lambda ln: ln.account_id == m.a["emp_pay"]).credit == 900.0
    )
    # fuel card: posts only against ONE statement line of the card (card/date/amount)
    card = (
        m.env["fix.expense.card"]
        .sudo()
        .create(
            {
                "issuer": "S6 Fuel Co",
                "last_digits": "4321",
                "holder_id": m.employee.id,
                "card_type": "fuel",
            }
        )
    )
    fill = _entry(
        m, "vehicle_fuel", 3000.0, payment_method="fuel_card", card_id=card.id, vendor_id=False
    )
    assert fill.state == "pending" and "statement line" in fill.message_ids[0].body
    txn = (
        m.env["fix.expense.card.transaction"]
        .sudo()
        .create(
            {
                "card_id": card.id,
                "txn_date": m.today,
                "merchant": "Meghna",
                "amount": 3000.0,
                "statement_ref": "S6-ST-1",
            }
        )
    )
    _as(m, m.acct, "fix.asset.cost.entry").browse(fill.id).action_post_direct()
    assert fill.state == "posted" and fill.card_transaction_id == txn
    again = _entry(
        m, "vehicle_fuel", 3000.0, payment_method="fuel_card", card_id=card.id, vendor_id=False
    )
    _refused(
        _as(m, m.acct, "fix.asset.cost.entry").browse(again.id).action_post_direct,
        match="no fuel-card",
    )


def test_internal_job_is_recorded_not_sent_to_ap(m):
    """M47-19: an internal job is not a payable."""
    entry = _entry(m, "facility_work_order", 8000.0, payment_method="internal", vendor_id=False)
    assert entry.state == "internal"
    _refused(
        _as(m, m.acct, "fix.asset.cost.entry").browse(entry.id).action_match_bill,
        _bill(m, m.vendor, [8000.0]).id,
    )


def test_a_rejected_bill_reopens_its_costs_and_paid_comes_from_the_payment(m):
    """M47-06 / FIN-19: matched is not paid; a rejection reopens the entry."""
    calls = []
    src = m.env["res.partner"].create({"name": "S6 paid source"})
    type(src)._m52_mark_paid = lambda self, a, d, r: calls.append((a, d, r))
    try:
        entry = _entry(m, source=src)
        bill = _bill(m, m.vendor, [5000.0])
        _as(m, m.acct, "fix.asset.cost.entry").browse(entry.id).action_match_bill(bill.id)
        assert not calls and not entry.paid_on
        bill.sudo()._guarded().write({"approval_state": "to_approve"})
        bill.with_user(m.mgr).sudo().action_reject()
        assert entry.state == "pending" and not entry.vendor_invoice_id
        bill2 = _bill(m, m.vendor, [5000.0])
        _as(m, m.acct, "fix.asset.cost.entry").browse(entry.id).action_match_bill(bill2.id)
        _post_bill(bill2)
        assert not calls
        bill2.sudo()._guarded().write({"payment_state": "paid"})
        assert entry.paid_on == m.today and calls == [(5000.0, m.today, "GAR-77")]
    finally:
        del type(src)._m52_mark_paid


def test_budget_hold_needs_ops_and_cfo_release(m):
    """D16 / FIN-15 / M47-20: above the remaining budget the cost is held."""
    version = (
        m.env["fix.budget.version"]
        .sudo()
        .create(
            {
                "name": "S6 FY",
                "fiscal_year": str(m.today.year),
                "date_from": m.today.replace(month=1, day=1),
                "date_to": m.today.replace(month=12, day=31),
            }
        )
    )
    budget = (
        m.env["fix.budget"]
        .sudo()
        .create(
            {
                "name": "S6 fleet",
                "version_id": version.id,
                "fiscal_year": str(m.today.year),
                "date_from": version.date_from,
                "date_to": version.date_to,
            }
        )
    )
    branch = m.env["fix.branch"].sudo().search([("operating_unit_id", "=", m.ou.id)], limit=1)
    if not branch:
        entity = m.env["fix.entity"].search([("company_id", "=", m.co.id)], limit=1)
        entity = entity or m.env["fix.entity"].sudo().create(
            {"code": "S6E%s" % m.tag, "legal_name": "S6 entity", "company_id": m.co.id}
        )
        branch = (
            m.env["fix.branch"]
            .sudo()
            .create(
                {
                    "name": "S6 Branch",
                    "code": "S6BR%s" % m.tag,
                    "entity_id": entity.id,
                    "operating_unit_id": m.ou.id,
                }
            )
        )
    m.env["fix.budget.line"].sudo().create(
        {
            "budget_id": budget.id,
            "account_id": m.a["auto"].id,
            "branch_id": branch.id,
            "date_from": version.date_from,
            "date_to": version.date_to,
            "planned_amount": 10000.0,
        }
    )
    version.sudo()._guarded().write({"state": "approved"})
    budget.invalidate_recordset()
    assert budget.state == "approved"
    van = _van(m, "S6-BUD-%s" % m.tag)
    small = _entry(m, amount=4000.0, vehicle_id=van.id)
    assert small.state == "pending" and small.budget_remaining == 10000.0
    big = _entry(m, amount=120000.0, vehicle_id=van.id)
    assert big.state == "held" and big.budget_overrun == 114000.0
    mine = _as(m, m.acct, "fix.asset.cost.entry").browse(big.id)
    _refused(mine.action_match_bill, _bill(m, m.vendor, [120000.0]).id, match="held")
    _refused(_as(m, m.bol, "fix.asset.cost.entry").browse(big.id).action_release_budget, "go")
    _as(m, m.lm, "fix.asset.cost.entry").browse(big.id).action_release_budget("urgent repair")
    assert big.state == "held"  # > BDT 100,000 over: the CFO too
    _as(m, m.cfo, "fix.asset.cost.entry").browse(big.id).action_release_budget("approved")
    assert big.state == "pending"


# ============================================================ IFRS 16 (D5)
def _lease(m, **kw):
    vals = {
        "company_id": m.co.id,
        "operating_unit_id": m.ou.id,
        "name": "S6 Lease %s" % next(_SEQ),
        "partner_id": m.landlord.id,
        "category_id": m.cat_rou.id,
        "commencement_date": month_start(m.today) - timedelta(days=1),
        "term_months": 36,
        "payment_amount": 50000.0,
        "ibr_percent": 9.0,
        "liability_account_id": m.a["liability"].id,
        "interest_account_id": m.a["interest"].id,
        "payment_account_id": m.a["clearing"].id,
    }
    vals["commencement_date"] = month_start(vals["commencement_date"])
    vals.update(kw)
    return m.env["fix.lease"].create(vals)


def test_escalated_and_quarterly_rent_is_measured_on_its_schedule(m):
    """FIN-08 / M47-09 / D5(b): each payment discounted, escalation included."""
    flat = lease_payment_vector(50000.0, 36, True)
    assert lease_present_value_vector(flat, 0.0075, True) == pytest.approx(
        lease_present_value(50000.0, 36, 0.0075, True), abs=0.02
    )
    pays = lease_payment_vector(50000.0, 60, True, 1, 10.0, 12)
    assert pays[0] == 50000.0 and pays[12] == 55000.0 and pays[59] == 73205.0
    # the audit's hand figure: 5 years, 10% a year, 9% IBR -> 2,912,968.68
    assert lease_present_value_vector(pays, 0.0075, True) == pytest.approx(2912968.68, abs=1.0)
    quarterly = lease_payment_vector(50000.0, 12, True, 3)
    assert quarterly == [150000.0, 0, 0, 150000.0, 0, 0, 150000.0, 0, 0, 150000.0, 0, 0]
    lease = _lease(m, escalation_percent=10.0, term_months=60)
    assert lease.pv_preview == pytest.approx(2912968.68, abs=1.0)


def test_lease_books_on_its_branch_and_activation_needs_one(m):
    """FIN-02 / M47-02: recognition and every month on the lease's branch."""
    _refused(
        _as(m, m.acct, "fix.lease").browse(_lease(m, operating_unit_id=False).id).action_activate,
        match="branch",
    )
    lease = _lease(m, operating_unit_id=m.ou2.id, payment_frequency="3")
    _as(m, m.acct, "fix.lease").browse(lease.id).action_activate()
    lines = lease.schedule_line_ids.sorted("sequence")
    assert lines[0].payment == 150000.0 and lines[1].payment == 0.0
    assert lines[-1].closing == 0.0
    lines[0].with_user(m.acct).action_post()
    move = lines[0].move_id
    assert set(_ou(m, move.line_ids)) == {m.ou2}
    dep = lease.asset_id.depreciation_line_ids.move_id
    assert dep and set(_ou(m, dep.line_ids)) == {m.ou2}


def test_depreciation_posts_on_each_assets_own_branch(m):
    """FIN-01: one run, two branches, two dimensions; no branch is refused."""
    Asset = m.env["fix.fixed.asset"]._guarded()
    period = month_start(m.today)
    a1 = Asset.create(
        {
            "company_id": m.co.id,
            "operating_unit_id": m.ou.id,
            "name": "S6 V1",
            "category_id": m.cat_veh.id,
            "gross": 600000.0,
            "purchase_date": period - timedelta(days=40),
        }
    )
    a2 = Asset.create(
        {
            "company_id": m.co.id,
            "operating_unit_id": m.ou2.id,
            "name": "S6 V2",
            "category_id": m.cat_veh.id,
            "gross": 1200000.0,
            "purchase_date": period - timedelta(days=40),
        }
    )
    (a1 | a2)._fix_activate_from_source()
    run = m.env["fix.asset.depreciation.run"]._depreciate(a1 | a2, period)
    lines = run.move_ids.line_ids.filtered(lambda ln: ln.account_id == m.a["veh_dep"])
    by_ou = {_ou(m, ln): ln.debit for ln in lines}
    assert by_ou == {m.ou: 10000.0, m.ou2: 20000.0}
    a3 = Asset.create(
        {
            "company_id": m.co.id,
            "name": "S6 V3",
            "category_id": m.cat_veh.id,
            "gross": 60000.0,
            "purchase_date": period - timedelta(days=40),
        }
    )
    a3._fix_activate_from_source()
    _refused(m.env["fix.asset.depreciation.run"]._depreciate, a3, period, match="no branch")


def test_commenced_lease_rent_bill_clears_the_ifrs16_account(m):
    """FIN-03 / M47-01 / D5(a): no double rent once the lease is on the book."""
    site = m.env["fix.site"].create(
        {
            "name": "S6 Site %s" % m.tag,
            "company_id": m.co.id,
            "operating_unit_id": m.ou.id,
            "state": "active",
        }
    )
    site_lease = (
        m.env["fix.site.lease"]
        .sudo()
        ._guarded()
        .create(
            {
                "site_id": site.id,
                "lessor_id": m.landlord.id,
                "start_date": month_start(m.today),
                "end_date": month_start(m.today) + timedelta(days=3 * 365),
                "monthly_rent": 50000.0,
            }
        )
    )
    row = site_lease.schedule_ids.sorted("due_date")[:1]
    assert row
    lease = _lease(m, commencement_date=month_start(m.today))
    lease.sudo().write({"site_lease_id": site_lease.id})
    entry = _entry(
        m, "lease_rent", row.rent_due, source=row, vendor_id=m.landlord.id, invoice_ref=False
    )
    mine = _as(m, m.acct, "fix.asset.cost.entry").browse(entry.id)
    _refused(
        mine.action_match_bill,
        _bill(m, m.landlord, [row.rent_due], ref="R1").id,
        match="not commenced",
    )
    _as(m, m.acct, "fix.lease").browse(lease.id).action_activate()
    bill = _bill(m, m.landlord, [row.rent_due], ref="R2")
    mine.action_match_bill(bill.id)
    move = _post_bill(bill)
    assert move.line_ids.filtered(lambda ln: ln.account_id == m.a["clearing"]).debit == row.rent_due
    assert not move.line_ids.filtered(lambda ln: ln.account_id == m.a["rent"])
    # M47-05: a bill above the scheduled rent is a Finance Manager's decision
    row2 = site_lease.schedule_ids.sorted("due_date")[1]
    e2 = _entry(
        m, "lease_rent", row2.rent_due, source=row2, vendor_id=m.landlord.id, invoice_ref=False
    )
    over = _bill(m, m.landlord, [row2.rent_due + 5000.0], ref="R3")
    _refused(
        _as(m, m.acct, "fix.asset.cost.entry").browse(e2.id).action_match_bill,
        over.id,
        match="variance",
    )


def test_remeasurement_and_termination_are_accounted(m):
    """FIN-07 / M47-09 / D5(c): a revised rent remeasures; an end derecognises."""
    lease = _lease(m, commencement_date=month_start(m.today) - timedelta(days=62))
    lease = _as(m, m.acct, "fix.lease").browse(lease.id)
    lease.action_activate()
    due = lease.schedule_line_ids.filtered(lambda ln: ln.period_start < month_start(m.today))
    due.sorted("sequence").with_user(m.acct).action_post()
    carrying = lease.liability_balance
    doc = _as(m, m.acct, "fix.lease.remeasurement").create(
        {
            "lease_id": lease.id,
            "effective_date": month_start(m.today),
            "payment_amount": 60000.0,
            "term_months": 36,
            "ibr_percent": 10.0,
            "reason": "rent review",
        }
    )
    _refused(doc.action_post, match="Segregation")
    _as(m, m.acct2, "fix.lease.remeasurement").browse(doc.id).action_post()
    assert doc.state == "posted" and doc.move_id
    adj = doc.move_id.line_ids.filtered(lambda ln: ln.account_id == m.a["liability"]).credit
    assert adj > 0 and lease.payment_amount == 60000.0
    left = lease.schedule_line_ids.filtered(lambda ln: ln.state == "draft")
    assert left and left[0].payment == 60000.0
    assert round(carrying + adj, 2) == round(left.sorted("sequence")[0].opening, 2)
    move = lease.sudo()._fix_terminate(m.today, "branch closed")
    assert lease.state == "ended" and lease.asset_id.state == "disposed"
    assert move.line_ids.filtered(lambda ln: ln.account_id == m.a["liability"]).debit > 0
    assert not lease.schedule_line_ids.filtered(lambda ln: ln.state == "draft")


def test_ifrs16_cron_posts_due_months_in_order(m):
    """FIN-18 / D5(g): the month posts itself once its (Dhaka) month end passed."""
    lease = _lease(m, commencement_date=month_start(m.today) - timedelta(days=62))
    _as(m, m.acct, "fix.lease").browse(lease.id).action_activate()
    due = lease.schedule_line_ids.filtered(lambda ln: ln.period_start < month_start(m.today))
    posted = m.env["fix.lease"]._cron_post_due_months()
    done = lease.schedule_line_ids.filtered(lambda ln: ln.state == "posted")
    assert (
        done == due and len(done) >= 2 and posted.filtered(lambda ln: ln.lease_id == lease) == done
    )
    assert not m.env["fix.lease"]._cron_post_due_months().filtered(lambda ln: ln.lease_id == lease)


def test_leased_vehicle_is_drafted_on_the_ifrs16_book(m):
    """FIN-09 / M46-11 / D5(d,e): long lease drafted, short one exempt."""
    van = _van(
        m,
        "S6-LEASE-%s" % m.tag,
        fix_ownership_basis="leased",
        fix_contract_ref="LC-1",
        fix_contract_end=m.today + timedelta(days=3 * 365),
        acquisition_date=m.today,
    )
    lease = m.env["fix.lease"].search([("vehicle_id", "=", van.id)])
    exc = m.env["fix.bridge.exception"].search([("key", "=", "m49_vehicle_lease:%s" % van.id)])
    if "fix_lease_monthly_rent" in van._fields:
        van.write({"fix_lease_monthly_rent": 40000.0})
        lease = m.env["fix.lease"].search([("vehicle_id", "=", van.id)])
        assert lease.state == "draft" and lease.exemption == "none"
        assert lease.operating_unit_id == m.ou
    else:
        # the fleet register does not hold the rent yet: an exception, nothing invented
        assert not lease and exc.state == "open" and "monthly rent" in exc.message


# ============================================================ M49 requests
def _posted_line(m, account, amount, ou=None):
    other = m.a["proceeds"]
    move = m.env["account.move"].create(
        {
            "journal_id": m.journal.id,
            "line_ids": [
                (0, 0, {"account_id": account.id, "name": "cost", "debit": amount}),
                (0, 0, {"account_id": other.id, "name": "cost", "credit": amount}),
            ],
        }
    )
    move.action_post()
    return move.line_ids.filtered("debit")


def test_capitalisation_refuses_a_line_already_in_the_register_and_no_branch(m):
    """FIN-06 / FIN-16: one ledger debit, one asset; never the first OU."""
    van = _van(m, "S6-CAP-%s" % m.tag, net_car_value=900000.0)
    req = m.env["fix.asset.finance.request"].search(
        [("source_model", "=", "fleet.vehicle"), ("source_res_id", "=", van.id)]
    )
    mine = _as(m, m.acct, "fix.asset.finance.request").browse(req.id)
    lease = _lease(m, payment_amount=25000.0, term_months=36)
    _as(m, m.acct, "fix.lease").browse(lease.id).action_activate()
    rou_line = lease.move_id.line_ids.filtered(lambda ln: ln.account_id == m.a["rou"])
    m.cat_veh.asset_account_id = m.a["rou"]
    mine.write(
        {
            "category_id": m.cat_veh.id,
            "acquisition_line_id": rou_line.id,
            "amount": rou_line.balance,
        }
    )
    _refused(mine.action_accept, match="already brought")
    m.cat_veh.asset_account_id = m.a["veh"]
    good = _posted_line(m, m.a["veh"], 900000.0)
    mine.write({"acquisition_line_id": good.id, "amount": 900000.0, "operating_unit_id": False})
    _refused(mine.action_accept, match="branch")
    mine.write({"operating_unit_id": m.ou.id})
    mine.action_accept()
    assert van.fixed_asset_id.operating_unit_id == m.ou


def test_disposal_takes_the_sources_asset_and_a_vehicle_needs_the_cfo(m):
    """FIN-17, D10: the source's own asset; vehicle disposal at DOFA tier 4."""
    van = _van(m, "S6-DSP-%s" % m.tag, net_car_value=500000.0)
    cap = m.env["fix.asset.finance.request"].search(
        [("source_model", "=", "fleet.vehicle"), ("source_res_id", "=", van.id)]
    )
    mine = _as(m, m.acct, "fix.asset.finance.request")
    mine.browse(cap.id).write(
        {
            "category_id": m.cat_veh.id,
            "acquisition_line_id": _posted_line(m, m.a["veh"], 500000.0).id,
        }
    )
    mine.browse(cap.id).action_accept()
    asset = van.fixed_asset_id
    asset._guarded().write({"state": "active"})
    # archiving never raises a disposal (D10)
    van.write({"active": False})
    assert not m.env["fix.asset.finance.request"].search(
        [
            ("source_res_id", "=", van.id),
            ("source_model", "=", "fleet.vehicle"),
            ("kind", "=", "dispose"),
        ]
    )
    van.write({"active": True})
    buyer = m.env["res.partner"].create({"name": "S6 buyer"})
    req = m.env["fix.asset.finance.request"]._m49_dispose_vehicle(
        van, "sold", proceeds=350000.0, buyer_id=buyer.id, reference="VD-1"
    )
    assert req.disposal_kind == "sale" and req.sale_proceeds == 350000.0
    other = (
        m.env["fix.fixed.asset"]
        ._guarded()
        .create(
            {
                "company_id": m.co.id,
                "operating_unit_id": m.ou.id,
                "name": "S6 other",
                "category_id": m.cat_veh.id,
                "gross": 1000.0,
                "purchase_date": m.today,
            }
        )
    )
    other._fix_activate_from_source()
    mine.browse(req.id).write({"fixed_asset_id": other.id})
    _refused(mine.browse(req.id).action_accept, match="registered in M49")
    mine.browse(req.id).write({"fixed_asset_id": False})
    mine.browse(req.id).action_accept()
    disposal = req.disposal_id
    assert (disposal.kind, disposal.proceeds, disposal.partner_id) == ("sale", 350000.0, buyer)
    assert disposal.proceeds_account_id == m.a["proceeds"]
    assert disposal._dofa_current_tier() == "tier_4"


def test_transfer_moves_cost_and_depreciation_between_branches(m):
    """FIN-13: the acknowledged transfer reclassifies the GL balances."""
    asset = (
        m.env["fix.fixed.asset"]
        ._guarded()
        .create(
            {
                "company_id": m.co.id,
                "operating_unit_id": m.ou.id,
                "name": "S6 T",
                "category_id": m.cat_veh.id,
                "gross": 600000.0,
                "purchase_date": month_start(m.today) - timedelta(days=40),
            }
        )
    )
    asset._fix_activate_from_source()
    m.env["fix.asset.depreciation.run"]._depreciate(asset, month_start(m.today))
    t = _as(m, m.acct, "fix.asset.transfer").create(
        {"asset_id": asset.id, "operating_unit_id": m.ou2.id}
    )
    t.action_confirm()
    _as(m, m.acct2, "fix.asset.transfer").browse(t.id).action_acknowledge()
    lines = t.gl_move_id.line_ids
    to_cost = lines.filtered(lambda ln: ln.account_id == m.a["veh"] and ln.debit)
    assert _ou(m, to_cost) == m.ou2 and to_cost.debit == 600000.0
    from_acc = lines.filtered(lambda ln: ln.account_id == m.a["veh_acc"] and ln.debit)
    assert _ou(m, from_acc) == m.ou and from_acc.debit == 10000.0


# ============================================================ recoveries (D9)
def test_hr_approved_recharge_is_booked_at_once(m):
    """S2 hand-off / D9: M45 publishes the recharge after HR approved it: booked."""
    eq = m.env["fix.equipment"].create(
        {
            "code": "S6-EQH-%s" % m.tag,
            "name": "S6 meter H",
            "company_id": m.co.id,
            "operating_unit_id": m.ou.id,
            "acquisition_cost": 6000.0,
        }
    )
    loss = (
        m.env["fix.equipment.loss"]
        .sudo()
        .create({"equipment_id": eq.id, "kind": "lost", "circumstances": "dropped in a river"})
    )
    loss.sudo()._guarded().write({"recharge_employee_id": m.employee.id, "recharge_amount": 1500.0})
    event = {
        "event_type": "equipment.recharge_requested",
        "aggregate": "fix.equipment.loss",
        "aggregate_id": loss.id,
        "payload": {
            "equipment": eq.code,
            "employee_id": m.employee.id,
            "amount": 1500.0,
            "hr_approved_by_id": m.hr.id,
            "hr_approved_on": str(m.today),
        },
    }
    rec = m.env["fix.asset.recovery"].sudo().consume_equipment_recharge_requested(event)
    assert rec.state == "approved" and rec.decided_by_id == m.hr
    assert rec.move_id.line_ids.filtered(lambda ln: ln.account_id == m.a["emp_rec"]).debit == 1500.0
    again = m.env["fix.asset.recovery"].sudo().consume_equipment_recharge_requested(event)
    assert again == rec and len(rec.move_id) == 1


def test_recharge_and_recovered_fine_become_hr_recoveries(m):
    """FIN-10 / M45-05 / D9: HR approves; Dr 100049; payroll fail-closed."""
    eq = m.env["fix.equipment"].create(
        {
            "code": "S6-EQ-%s" % m.tag,
            "name": "S6 meter",
            "company_id": m.co.id,
            "operating_unit_id": m.ou.id,
            "acquisition_cost": 5000.0,
        }
    )
    loss = (
        m.env["fix.equipment.loss"]
        .sudo()
        .create({"equipment_id": eq.id, "kind": "lost", "circumstances": "left on a bus"})
    )
    loss.sudo()._guarded().write({"recharge_employee_id": m.employee.id, "recharge_amount": 2000.0})
    publish(
        m.env,
        "equipment.recharge_requested",
        "fix.equipment.loss",
        loss.id,
        {
            "equipment": eq.code,
            "loss": loss.name,
            "employee_id": m.employee.id,
            "employee": m.employee.name,
            "amount": 2000.0,
        },
    )
    sub = m.env.ref("%s.consumer_equipment_recharge_requested" % MOD)
    for row in m.env["fix.event.outbox"].search(
        [("event_type", "=", "equipment.recharge_requested"), ("aggregate_id", "=", loss.id)]
    ):
        assert m.env["fix.event.outbox"]._relay_deliver(sub, row) == ""
    rec = m.env["fix.asset.recovery"].search([("source_res_id", "=", loss.id)])
    assert len(rec) == 1 and rec.state == "pending" and rec.amount == 2000.0
    _refused(_as(m, m.acct, "fix.asset.recovery").browse(rec.id).action_approve)
    _as(m, m.hr, "fix.asset.recovery").browse(rec.id).action_approve()
    lines = rec.move_id.line_ids
    assert lines.filtered(lambda ln: ln.account_id == m.a["emp_rec"]).debit == 2000.0
    assert lines.filtered(lambda ln: ln.account_id == m.a["eq_loss"]).credit == 2000.0
    _refused(
        _as(m, m.hr, "fix.asset.recovery").browse(rec.id).action_send_to_payroll, match="statutory"
    )
    fine = _entry(
        m,
        "vehicle_fine",
        3000.0,
        payment_method="petty_cash",
        vendor_id=False,
        recovery_employee_id=m.employee.id,
    )
    assert fine.state == "posted"
    rec2 = m.env["fix.asset.recovery"].search([("cost_entry_id", "=", fine.id)])
    assert rec2.credit_account_id == m.a["fine"] and rec2.employee_id == m.employee


# ============================================================ events
def test_events_resolve_their_own_aggregate(m):
    """FIN-04 / M47-14: an id is read in the model the event names."""
    from odoo.addons.cd_asset_finance_hse_bridge.models.fix_bridge_exception import event_source

    eq = m.env["fix.equipment"].create(
        {
            "code": "S6-AGG-%s" % m.tag,
            "name": "S6 scope",
            "company_id": m.co.id,
            "operating_unit_id": m.ou.id,
        }
    )
    event = {"aggregate": "fix.site.lease.event", "aggregate_id": eq.id}
    assert not event_source(m.env, event, "fix.equipment")
    assert event_source(m.env, dict(event, aggregate="fix.equipment"), "fix.equipment") == eq
    loss = (
        m.env["fix.equipment.loss"]
        .sudo()
        .create({"equipment_id": eq.id, "kind": "lost", "circumstances": "gone"})
    )
    found = m.env["fix.asset.finance.request"].sudo()
    from odoo.addons.cd_asset_finance_hse_bridge.models.m49_asset_request import lost_subject

    subject = lost_subject(
        m.env,
        {
            "aggregate": "fix.equipment.loss",
            "aggregate_id": loss.id,
            "payload": {"equipment": eq.code},
        },
    )
    assert subject and subject[0] == eq
    assert not lost_subject(
        m.env,
        {
            "aggregate": "fix.equipment.loss",
            "aggregate_id": loss.id,
            "payload": {"equipment": "SOMETHING-ELSE"},
        },
    )
    assert found._name == "fix.asset.finance.request"


def test_health_check_lists_unconfigured_categories(m):
    """FIN-25: what blocks the A07 money paths is listed."""
    bare = m.env["fix.asset.category"].create(
        {"company_id": m.co.id, "code": "S6BARE%s" % m.tag, "name": "S6 Bare"}
    )
    health = m.env["fix.asset.category"]._fix_a07_health(m.co)
    codes = [code for code, _name, _missing in health["categories"]]
    assert bare.code in codes and m.cat_rou.code not in [
        c for c, _n, miss in health["categories"] if "Asset Journal" in miss
    ]
    assert not health["ok"]


def test_consumers_are_registered(m):
    for xmlid, (event_type, model, method) in {
        "consumer_equipment_recharge_requested": (
            "equipment.recharge_requested",
            "fix.asset.recovery",
            "consume_equipment_recharge_requested",
        ),
        "consumer_equipment_disposed": (
            "equipment.disposed",
            "fix.asset.finance.request",
            "consume_equipment_disposed",
        ),
        "consumer_lease_terminated": ("lease.terminated", "fix.lease", "consume_lease_terminated"),
    }.items():
        sub = m.env.ref("%s.%s" % (MOD, xmlid))
        assert (sub.event_type, sub.model, sub.method) == (event_type, model, method)
        assert callable(getattr(m.env[model], method))
    cron = m.env.ref("%s.ir_cron_ifrs16_post_due_months" % MOD)
    assert cron.active and "_cron_post_due_months" in cron.code
    assert isinstance(date.today(), date)
