"""A08 M51 controls (findings M51-1 ... M51-13): every gap probe of
working/A08_evidence/probes/m51/probe_m51.py run again as the attack it was,
now refused, plus the proper path that the legitimate maker and checker CAN
complete. Live ORM, rolled back.

Every attack runs as a NON-ADMIN user created in the transaction with the
real finance role (account.group_account_user = Accountant,
account.group_account_manager = Accounting Administrator, the shipped-empty
Tax Return Filing Approver). The records live in a company of their own, so
nothing in the shared test database changes the figures.
"""

from __future__ import annotations

import base64
import hashlib
import itertools
import types
from datetime import timedelta
from decimal import Decimal

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

pytestmark = [pytest.mark.tax, pytest.mark.financial]

REFUSED = (UserError, ValidationError, AccessError)
BIN = "1234567890123"
SUPPLIER_BIN = "0011223344556"
ACC = "account.group_account_user"
MGR = "account.group_account_manager"
FILER = "cd_tax_engine_bd.group_tax_filing_approver"
WL, CERT, CREDIT, REG, RET = (
    "fix.withholding.line",
    "fix.withholding.certificate",
    "fix.input.vat.credit",
    "fix.mushak.register",
    "fix.vat.return",
)
_SEQ = itertools.count(1)
_CR = []


def _refused(fn, *args, match=None, **kw):
    """The call is refused; its side effects are rolled back to a savepoint."""
    with pytest.raises(REFUSED, match=match), _CR[-1].savepoint():
        fn(*args, **kw)


class Ctx(types.SimpleNamespace):
    def as_(self, user):
        """An environment of `user` in the test company."""
        return self.env(
            user=user.id, context=dict(self.env.context, allowed_company_ids=self.co.ids)
        )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    _CR.append(env.cr)
    n = next(_SEQ)
    x = Ctx(env=env)
    x.co = env["res.company"].create({"name": "A08 M51 Controls Co %s" % n, "vat": BIN})
    x.ou = env["operating.unit"].create(
        {
            "name": "A08 M51 OU %s" % n,
            "code": "A8M51%s" % n,
            "company_id": x.co.id,
            "partner_id": x.co.partner_id.id,
        }
    )
    x.cenv = env(context=dict(env.context, allowed_company_ids=x.co.ids))
    x.today = fields.Date.context_today(env.user)
    x.period = x.today.strftime("%Y-%m")
    Account = x.cenv["account.account"]  # code is company-dependent: create in the company

    def acc(code, name, kind):
        return Account.create(
            {
                "code": "A8M51%s%s" % (n, code),
                "name": name,
                "account_type": kind,
                "company_ids": [(6, 0, x.co.ids)],
            }
        )

    x.vat_out = acc("1", "VAT output payable", "liability_current")
    x.vat_in = acc("2", "VAT input credit", "asset_current")
    x.tds_payable = acc("3", "TDS payable", "liability_current")
    x.vds_payable = acc("4", "VDS payable", "liability_current")
    x.expense = acc("5", "Repair expense", "expense")
    x.ap = acc("6", "Trade payables", "liability_payable")
    x.revenue = acc("7", "Service revenue", "income")
    x.ar = acc("8", "Receivables", "asset_receivable")
    x.ar.reconcile = True
    x.ap.reconcile = True
    icp = env["ir.config_parameter"].sudo()
    icp.set_param("cd_tax_engine_bd.vat_output_account_code", x.vat_out.code)
    icp.set_param("cd_tax_engine_bd.vat_input_account_code", x.vat_in.code)
    icp.set_param("cd_tax_engine_bd.account_code.tds_payable", x.tds_payable.code)
    icp.set_param("cd_tax_engine_bd.account_code.vds_payable", x.vds_payable.code)
    x.journal = x.cenv["account.journal"].create(
        {
            "name": "A08 M51 misc %s" % n,
            "code": "M5G%s" % n,
            "type": "general",
            "company_id": x.co.id,
        }
    )
    x.cash = acc("9", "Bank", "asset_cash")
    x.bank = x.cenv["account.journal"].create(
        {
            "name": "A08 M51 bank %s" % n,
            "code": "M5B%s" % n,
            "type": "bank",
            "company_id": x.co.id,
            "default_account_id": x.cash.id,
        }
    )
    icp.set_param("cd_tax_engine_bd.challan_journal_code", x.bank.code)

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
                    "assigned_operating_unit_ids": [(6, 0, x.ou.ids)],
                    "default_operating_unit_id": x.ou.id,
                }
            )
        )

    x.plain = user("a08m51c_plain")
    x.acct = user("a08m51c_acct", ACC)
    x.acct2 = user("a08m51c_acct2", ACC)
    x.mgr = user("a08m51c_mgr", MGR)
    x.mgr2 = user("a08m51c_mgr2", MGR)
    x.filer = user("a08m51c_filer", ACC, FILER)
    x.vendor = env["res.partner"].create({"name": "A08 M51 Vendor %s" % n})
    x.customer = env["res.partner"].create({"name": "A08 M51 Customer %s" % n})
    x.rate = env["fix.tax.rate"].find_rate("tds", "service_general", x.today, x.co)
    x.vbill = None
    if "fix.vendor.invoice" in env:
        x.vbill = (
            x.cenv["fix.vendor.invoice"]
            .sudo()
            .create(
                {
                    "vendor_id": x.vendor.id,
                    "operating_unit_id": x.ou.id,
                    "invoice_ref": "A08-M51-VB-%s" % n,
                    "bill_type": "non_po",
                }
            )
        )
    return x


# ------------------------------------------------------------------ helpers
def _entry(c, lines, when=None):
    """A posted GL entry (the arrangement of what AP / AR posted)."""
    move = c.cenv["account.move"].create(
        {
            "journal_id": c.journal.id,
            "date": when or c.today,
            "line_ids": [
                (0, 0, {"account_id": a.id, "name": "a08", "debit": dr, "credit": cr})
                for a, dr, cr in lines
            ],
        }
    )
    move.action_post()
    return move


def _bill_posting(c, base=100000.0, tds=None):
    """The approved vendor bill's posting: Dr expense / Cr TDS payable / Cr AP."""
    tds = round(base * c.rate.rate / 100.0, 2) if tds is None else tds
    return _entry(c, [(c.expense, base, 0.0), (c.tds_payable, 0.0, tds), (c.ap, 0.0, base - tds)])


def _deduction_vals(c, **kw):
    vals = {
        "company_id": c.co.id,
        "operating_unit_id": c.ou.id,
        "tax_kind": "tds",
        "partner_id": c.vendor.id,
        "partner_tin": "123456789012",
        "psr_received": True,
        "paid_by_bank": True,
        "rate_id": c.rate.id,
        "document_date": c.today,
        "base_amount": 100000.0,
        "amount": round(100000.0 * c.rate.rate / 100.0, 2),
        "source_ref": "BILL-%s" % next(_SEQ),
    }
    if c.vbill:
        vals["vendor_invoice_id"] = c.vbill.id
    vals.update(kw)
    return vals


def _deduction(c, user=None, move=None, **kw):
    """A deduction recorded the proper way: with its posted liability entry."""
    vals = _deduction_vals(c, **kw)
    move = move or _bill_posting(c, vals["base_amount"], vals["amount"])
    return c.as_(user or c.acct)[WL]._fix_record_deductions([vals], move)


def _challan(c, lines, user=None, verify_by=None, **kw):
    vals = {
        "challan_no": "CH-A08M51-%s" % next(_SEQ),
        "challan_date": c.today,
        "tax_kind": "tds",
        "period": c.period,
        "amount": sum(lines.mapped("amount")),
        "operating_unit_id": c.ou.id,
    }
    vals.update(kw)
    ch = c.as_(user or c.acct)["fix.tax.challan"].create(vals)
    lines.with_user(user or c.acct).write({"challan_id": ch.id})
    if verify_by:
        ch.with_user(verify_by).action_record_verification("IBAS-%s" % ch.challan_no)
    return ch


def _deposited(c):
    line = _deduction(c)
    ch = _challan(c, line, verify_by=c.acct2)
    ch.with_user(c.acct).action_confirm_deposit()
    return line, ch


def _credit(c, user=None, **kw):
    vals = {
        "partner_id": c.vendor.id,
        "supplier_bin": SUPPLIER_BIN,
        "supplier_mushak_no": "M63-%s" % next(_SEQ),
        "invoice_date": c.today,
        "taxable_amount": 6000.0,
        "vat_amount": 900.0,
        "operating_unit_id": c.ou.id,
    }
    vals.update(kw)
    return c.as_(user or c.acct)[CREDIT].create(vals)


def _reg(c, taxable, vat, **kw):
    """A register row as the billing engine writes it (its issuing service)."""
    vals = {
        "company_id": c.co.id,
        "operating_unit_id": c.ou.id,
        "mushak_no": "A08M51-%s" % next(_SEQ),
        "invoice_ref": "AR/%s" % next(_SEQ),
        "invoice_date": c.today,
        "supplier_name": c.co.name,
        "supplier_bin": BIN,
        "customer_name": "A08 customer",
        "taxable_amount": taxable,
        "vat_amount": vat,
        "total_payable": taxable + vat,
        "treatment_summary": "SVC: standard_15 @ 15%",
    }
    vals.update(kw)
    return c.cenv[REG]._fix_issue_register_row(vals)


def _vat_return(c, user=None):
    return c.as_(user or c.acct)[RET].create({"period": c.period})


class StubEvat:
    """Stands in for the INT-038 NBR adapter: accepts whatever it is sent."""

    def build_payload(self, **kw):
        return kw

    def submit_return(self, payload):
        return types.SimpleNamespace(
            status="ACCEPTED", ack_token="ACK-STUB-1", filed_at="", validation_messages=[]
        )


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


# ======================================================= rate tables & parameters
def test_m51_t01_accountant_cannot_change_tax_rate(c):
    vat = c.env["fix.tax.rate"].find_rate("vat", "standard", c.today, c.co)
    _refused(vat.with_user(c.acct).write, {"rate": 5.0})


def test_m51_t02_accountant_cannot_change_tax_rate_via_p03(c, p03):
    vat = c.env["fix.tax.rate"].find_rate("vat", "standard", c.today, c.co)
    res = p03.write(c.acct, model="fix.tax.rate", record_id=vat.id, values={"rate": 5.0})
    vat.invalidate_recordset()
    assert vat.rate == 15.0 and "error" in res, res


def test_m51_t03_vat_rate_master_is_what_invoices_use(c):
    """M51-5: the master moves to 10% (proposal by one manager, adviser
    confirmation, activation by another) and the sales determination charges
    10% from that day; before it, 15%."""
    from odoo.addons.cd_tax_engine_bd.models import tax_logic

    Treatment = c.cenv["fix.vat.treatment"]
    line = [tax_logic.TaxLine("SVC", Decimal("1"), Decimal("1000"))]
    assert Treatment._fix_determine_tax(line, c.today, c.co).total_vat == Decimal("150.00")
    start = c.today + timedelta(days=1)
    new = c.as_(c.mgr)["fix.tax.rate"].create(
        {
            "tax_kind": "vat",
            "code": "standard",
            "name": "VAT standard (cut)",
            "rate": 10.0,
            "date_from": start,
            "company_id": c.co.id,
        }
    )
    assert new.state == "proposed"
    # a proposal is not what is charged
    assert Treatment._fix_determine_tax(line, start, c.co).total_vat == Decimal("150.00")
    new.with_user(c.mgr).action_record_adviser_verification("ADV-2026-11")
    new.with_user(c.mgr2).action_activate()
    det = Treatment._fix_determine_tax(line, start, c.co)
    assert (det.total_vat, det.rates_source) == (Decimal("100.00"), "master")
    assert Treatment._fix_determine_tax(line, c.today, c.co).total_vat == Decimal("150.00")
    # the tariff treatment is read too: an active exempt tariff row
    c.cenv["fix.vat.treatment"].create(
        {"code": "EDU-SVC", "name": "Training", "treatment_type": "exempt", "rate": 0.0}
    )
    edu = [tax_logic.TaxLine("EDU-SVC", Decimal("1"), Decimal("1000"))]
    assert Treatment._fix_determine_tax(edu, c.today, c.co).total_vat == Decimal("0.00")


def test_m51_t04_manager_cannot_zero_tds_rate_alone(c):
    """M51-6: an active row is never edited in place; one manager's 0%
    proposal is not used, cannot be activated by its proposer, and needs the
    adviser's confirmation."""
    old = c.rate
    _refused(old.with_user(c.mgr).write, {"date_to": c.today - timedelta(days=1)})
    new = c.as_(c.mgr)["fix.tax.rate"].create(
        {
            "tax_kind": "tds",
            "code": "service_general",
            "name": "zero",
            "section": "ITA 2023 s.90",
            "rate": 0.0,
            "date_from": c.today,
            "company_id": c.co.id,
            "verify_with_adviser": False,
        }
    )
    assert (new.state, new.verify_with_adviser) == ("proposed", True)
    assert c.env["fix.tax.rate"].find_rate("tds", "service_general", c.today, c.co) == old
    _refused(new.with_user(c.mgr2).action_activate, match="verify-with-adviser")
    new.with_user(c.mgr).action_record_adviser_verification("ADV-1")
    _refused(new.with_user(c.mgr).action_activate, match="Segregation")
    _refused(new.with_user(c.acct).action_activate, match="Accounting Administrator")
    _refused(new.with_user(c.mgr).write, {"state": "active"})


def test_m51_t04_proper_path_second_manager_activates(c):
    new = c.as_(c.mgr)["fix.tax.rate"].create(
        {
            "tax_kind": "tds",
            "code": "service_general",
            "name": "revised",
            "section": "ITA 2023 s.90",
            "rate": 12.0,
            "date_from": c.today + timedelta(days=10),
            "company_id": c.co.id,
        }
    )
    new.with_user(c.mgr).action_record_adviser_verification("ADV-2")
    new.with_user(c.mgr2).action_activate()
    assert (new.state, new.activated_by_id) == ("active", c.mgr2)
    later = c.env["fix.tax.rate"].find_rate(
        "tds", "service_general", c.today + timedelta(days=10), c.co
    )
    assert later == new
    # an edited proposal loses its adviser confirmation
    other = c.as_(c.mgr)["fix.tax.rate"].create(
        {"tax_kind": "tds", "code": "a08_x", "name": "x", "rate": 3.0, "company_id": c.co.id}
    )
    other.with_user(c.mgr2).action_record_adviser_verification("ADV-3")
    other.with_user(c.mgr).write({"rate": 4.0})
    assert other.verify_with_adviser is True and not other.adviser_reference


def test_m51_t05_accountant_cannot_rewrite_vat_treatment(c):
    row = c.cenv["fix.vat.treatment"].create(
        {
            "code": "A08-HS-%s" % next(_SEQ),
            "name": "Repair",
            "treatment_type": "standard_15",
            "rate": 15.0,
        }
    )
    _refused(row.with_user(c.acct).write, {"treatment_type": "exempt", "rate": 0.0})
    # a manager cannot either: an active tariff row changes by proposal
    _refused(row.with_user(c.mgr).write, {"treatment_type": "exempt", "rate": 0.0})


def test_m51_t06_one_tds_schedule(c):
    from odoo.addons.cd_tax_engine_bd.models import tax_logic

    assert not hasattr(tax_logic, "TDS_DEFAULT_RATES")
    assert not hasattr(tax_logic, "determine_tds")


def test_m51_t07_non_filer_multiplier_floor(c):
    p = c.env["fix.tax.parameter"].search(
        [("key", "=", "non_filer_multiplier"), ("state", "=", "active")], limit=1
    )
    _refused(p.with_user(c.mgr).write, {"value": 0.0})
    _refused(
        c.as_(c.mgr)["fix.tax.parameter"].create,
        {"key": "non_filer_multiplier", "value": 1.0, "date_from": c.today, "company_id": c.co.id},
        match="below the statutory",
    )
    assert c.env["fix.tax.parameter"].get_value("non_filer_multiplier", c.today, c.co) >= 1.5


# ======================================================= input VAT credit (s.46)
def test_m51_v01_missing_bin_is_ineligible(c):
    cr_ = _credit(c, supplier_bin=False)
    cr_.with_user(c.acct).action_check_eligibility()
    assert cr_.state == "ineligible"


def test_m51_v02_forged_eligible_is_refused_and_prepare_rechecks(c):
    cr_ = _credit(
        c, supplier_bin=False, supplier_mushak_no=False, vat_amount=24000.0, taxable_amount=160000.0
    )
    cr_.with_user(c.acct).action_check_eligibility()
    _refused(cr_.with_user(c.acct).write, {"state": "eligible"}, match="cannot be set directly")
    # even a row that reached "eligible" is re-checked before the 9.1 claims it
    cr_.sudo().write({"state": "eligible"})  # arrangement: a legacy forged row
    ret = _vat_return(c)
    ret.with_user(c.acct).action_prepare()
    assert cr_.state == "ineligible" and ret.input_vat == 0.0


def test_m51_v03_same_supplier_mushak_claimed_once(c):
    a = _credit(c, supplier_mushak_no="DUP-63-001")
    b = _credit(c, supplier_mushak_no="DUP-63-001")
    (a | b).with_user(c.acct).action_check_eligibility()
    assert (a.state, b.state) == ("eligible", "ineligible")
    assert "already recorded" in b.ineligible_reason
    ret = _vat_return(c)
    ret.with_user(c.acct).action_prepare()
    assert (a.state, b.state, ret.input_vat) == ("claimed", "ineligible", 900.0)


def test_m51_v04_vat_out_of_proportion_is_ineligible(c):
    cr_ = _credit(c, taxable_amount=1000.0, vat_amount=15000.0)
    cr_.with_user(c.acct).action_check_eligibility()
    assert cr_.state == "ineligible" and "matches no VAT rate" in cr_.ineligible_reason
    reduced = _credit(c, taxable_amount=1000.0, vat_amount=75.0)  # 7.5%: a master rate
    reduced.with_user(c.acct).action_check_eligibility()
    assert reduced.state == "eligible"


def test_m51_v05_debit_note_follows_its_invoice(c):
    base = _credit(c, supplier_mushak_no=False, vat_amount=4050.0, taxable_amount=27000.0)
    base.with_user(c.acct).action_check_eligibility()
    assert base.state == "ineligible"
    loose = _credit(
        c,
        adjustment_type="increase",
        supplier_mushak_no="MN-6.8",
        vat_amount=450.0,
        taxable_amount=3000.0,
    )
    loose.with_user(c.acct).action_check_eligibility()
    assert loose.state == "ineligible" and "not linked" in loose.ineligible_reason
    linked = _credit(
        c,
        adjustment_type="increase",
        supplier_mushak_no="MN-6.8b",
        vat_amount=450.0,
        taxable_amount=3000.0,
        original_credit_id=base.id,
    )
    linked.with_user(c.acct).action_check_eligibility()
    assert linked.state == "ineligible" and "original invoice credit" in linked.ineligible_reason
    good = _credit(c)
    good.with_user(c.acct).action_check_eligibility()
    dn = _credit(
        c,
        adjustment_type="increase",
        supplier_mushak_no="MN-6.8c",
        vat_amount=150.0,
        taxable_amount=1000.0,
        original_credit_id=good.id,
    )
    dn.with_user(c.acct).action_check_eligibility()
    assert dn.state == "eligible"


def test_m51_v06_claim_window_enforced(c):
    _refused(_credit, c, claim_period="%04d-%02d" % (c.today.year + 2, 1))


def test_m51_v07_claimed_credit_is_frozen(c):
    cr_ = _credit(c, vat_amount=900.0)
    cr_.with_user(c.acct).action_check_eligibility()
    ret = _vat_return(c)
    ret.with_user(c.acct).action_prepare()
    assert cr_.state == "claimed"
    _refused(
        cr_.with_user(c.acct).write,
        {"vat_amount": 9000.0, "taxable_amount": 60000.0},
        match="frozen",
    )
    # an edited unclaimed verdict goes stale
    other = _credit(c)
    other.with_user(c.acct).action_check_eligibility()
    other.with_user(c.acct).write({"vat_amount": 901.0})
    assert other.state == "pending"


def test_m51_v08_input_credit_state_via_p03(c, p03):
    cr_ = _credit(c, supplier_bin=False)
    cr_.with_user(c.acct).action_check_eligibility()
    res = p03.write(c.acct, model=CREDIT, record_id=cr_.id, values={"state": "eligible"})
    cr_.invalidate_recordset()
    assert cr_.state == "ineligible", res


# ======================================================= Mushak register and the 9.1
def test_ref_m51_m01_vat_return_computation(c):
    _reg(c, 10000.0, 1500.0)
    _reg(c, 20000.0, 3000.0)
    cr_ = _credit(c, vat_amount=900.0)
    cr_.with_user(c.acct).action_check_eligibility()
    ret = _vat_return(c)
    ret.with_user(c.acct).action_prepare()
    assert (ret.state, ret.prepared_by_id) == ("prepared", c.acct)
    assert (ret.output_vat, ret.input_vat, ret.net_payable) == (4500.0, 900.0, 3600.0)


def test_m51_m02_issued_mushak_is_immutable_corrected_by_note(c):
    r = _reg(c, 20000.0, 3000.0)
    _refused(r.with_user(c.acct).write, {"vat_amount": 0.0, "total_payable": 20000.0})
    _refused(r.with_user(c.mgr).write, {"vat_amount": 0.0})
    note = c.cenv[REG]._fix_issue_note(r, "credit_note", 2000.0, 300.0, "Price reduction")
    assert (note.row_type, note.vat_amount, note.original_id) == ("credit_note", -300.0, r)
    ret = _vat_return(c)
    ret.with_user(c.acct).action_prepare()
    assert ret.output_vat == 2700.0


def test_m51_m03_typed_register_row_refused(c):
    vals = {
        "operating_unit_id": c.ou.id,
        "mushak_no": "TYPED-1",
        "invoice_ref": "NONE",
        "invoice_date": c.today,
        "supplier_name": c.co.name,
        "supplier_bin": BIN,
        "customer_name": "x",
        "taxable_amount": 1000.0,
        "vat_amount": 150.0,
        "total_payable": 1150.0,
    }
    _refused(c.as_(c.acct)[REG].create, vals)
    _refused(c.as_(c.mgr)[REG].create, vals)
    # the issuing service refuses a placeholder BIN too
    _refused(
        c.cenv[REG]._fix_issue_register_row,
        dict(vals, supplier_bin="0000000000000"),
        match="real 13-digit",
    )


def test_m51_m04_mark_posted_needs_the_gl(c):
    r = _reg(c, 1000.0, 150.0)
    _refused(r.with_user(c.acct).action_mark_posted, match="no posted GL entry")
    assert not r.posted
    _refused(r.sudo().write, {"posted": True}, match="no posted GL entry")
    move = _entry(c, [(c.ar, 1150.0, 0.0), (c.revenue, 0.0, 1000.0), (c.vat_out, 0.0, 150.0)])
    r._fix_mark_posted(move)
    assert (r.posted, r.move_id) == (True, move)


def test_m51_m05_file_from_draft_refused(c):
    ret = _vat_return(c)
    _refused(ret.with_user(c.acct).action_file, "TYPED-12345")
    _refused(ret.with_user(c.filer).action_file_online, client=StubEvat())
    assert ret.state == "draft"


def test_m51_m06_vat_return_state_forged(c, p03):
    ret = _vat_return(c)
    res = p03.write(
        c.acct,
        model=RET,
        record_id=ret.id,
        values={"state": "filed", "nbr_confirmation": "P03-FAKE"},
    )
    ret.invalidate_recordset()
    assert ret.state == "draft", res
    _refused(ret.with_user(c.acct).write, {"state": "filed"}, match="cannot be set directly")
    _refused(ret.with_user(c.mgr).write, {"nbr_confirmation": "X"}, match="cannot be set directly")
    _refused(c.as_(c.acct)[RET].create, {"period": "2020-01", "state": "filed"})


def test_m51_m07_subledger_status_recomputed_at_filing(c):
    _reg(c, 10000.0, 1500.0)
    ret = _vat_return(c)
    ret.with_user(c.acct).action_prepare()
    _refused(
        ret.with_user(c.acct).write,
        {"subledger_status": "reconciled"},
        match="cannot be set directly",
    )
    ret.sudo().write({"subledger_status": "reconciled"})  # arrangement: a stale status
    _refused(ret.with_user(c.filer).action_file_online, client=StubEvat(), match="IRB-09")
    assert ret.state == "prepared"


def test_m51_m08_reconciliation_fails_closed_without_accounts(c):
    _reg(c, 10000.0, 1500.0)
    ret = _vat_return(c)
    ret.with_user(c.acct).action_prepare()
    c.env["ir.config_parameter"].sudo().set_param("cd_tax_engine_bd.vat_input_account_code", "")
    _refused(ret.with_user(c.acct).action_subledger_reconciliation, match="vat_input")


def test_m51_m09_filed_return_not_reprepared(c):
    ret = _filed_return(c)
    _refused(ret.with_user(c.acct).action_prepare, match="filed")


def test_m51_m10_preparer_cannot_file(c):
    _reg(c, 10000.0, 1500.0)
    _entry(c, [(c.ar, 11500.0, 0.0), (c.revenue, 0.0, 10000.0), (c.vat_out, 0.0, 1500.0)])
    ret = _vat_return(c, user=c.filer)
    ret.with_user(c.filer).action_prepare()
    _refused(
        ret.with_user(c.filer).action_file_online, client=StubEvat(), match="prepared this return"
    )
    _refused(ret.with_user(c.acct).action_file_online, client=StubEvat(), match="Filing Approver")


def _filed_return(c):
    """Proper path: accountant prepares, the system reconciles to the posted
    GL, the filing approver (not the preparer) files online."""
    _reg(c, 10000.0, 1500.0)
    _entry(c, [(c.ar, 11500.0, 0.0), (c.revenue, 0.0, 10000.0), (c.vat_out, 0.0, 1500.0)])
    cr_ = _credit(c, vat_amount=900.0)
    cr_.with_user(c.acct).action_check_eligibility()
    _entry(c, [(c.vat_in, 900.0, 0.0), (c.expense, 6000.0, 0.0), (c.ap, 0.0, 6900.0)])
    ret = _vat_return(c)
    ret.with_user(c.acct).action_prepare()
    ret.with_user(c.acct).action_subledger_reconciliation()
    assert ret.subledger_status == "reconciled", ret.subledger_notes
    for key in ("declarant_name", "declarant_designation", "declarant_nid"):
        c.env["ir.config_parameter"].sudo().set_param("cd_tax_engine_bd.%s" % key, "A08 %s" % key)
    result = ret.with_user(c.filer).action_file_online(client=StubEvat())
    assert result["token"] == "ACK-STUB-1"
    assert (ret.state, ret.nbr_confirmation, ret.filed_by_id) == ("filed", "ACK-STUB-1", c.filer)
    return ret


def test_ref_m51_proper_path_prepare_reconcile_file(c):
    ret = _filed_return(c)
    assert (ret.output_vat, ret.input_vat, ret.net_payable) == (1500.0, 900.0, 600.0)


# ======================================================= withholding, challans, certificates
def test_m51_w01_certificate_needs_deposit(c):
    ln = _deduction(c)
    _refused(ln.with_user(c.acct).action_issue_certificate, match="after the challan deposit")


def test_m51_w02_forged_deposited_refused(c):
    ln = _deduction(c)
    _refused(ln.with_user(c.acct).write, {"state": "deposited"}, match="cannot be set directly")
    ln.sudo().write({"state": "deposited"})  # arrangement: a legacy row with no challan
    _refused(ln.with_user(c.acct).action_issue_certificate, match="verified challan")


def test_m51_w03_free_standing_certificate_refused(c):
    vals = {
        "certificate_type": "mushak_6_6",
        "supplier_name": "Any supplier",
        "supplier_bin": "0000000000000",
        "withheld_amount": 7750.0,
    }
    if c.vbill:
        vals["vendor_invoice_id"] = c.vbill.id
    _refused(c.as_(c.acct)[CERT].create, vals, match="never created by hand")


def test_m51_w04_challan_must_equal_linked_liabilities(c):
    ln = _deduction(c)
    ch = _challan(c, ln, amount=ln.amount - 1000.0, verify_by=c.acct2)
    _refused(ch.with_user(c.acct).action_confirm_deposit, match="does not equal")


def test_ref_m51_w05_deposit_posts_and_certificate_states_the_challan(c):
    ln = _deduction(c)
    ch = _challan(c, ln)
    _refused(ch.with_user(c.acct).action_confirm_deposit, match="not verified")
    _refused(ch.with_user(c.acct).action_record_verification, "IBAS-1", match="Segregation")
    ch.with_user(c.acct2).action_record_verification("IBAS-1")
    ch.with_user(c.acct).action_confirm_deposit()
    assert ch.state == "deposited" and ch.move_id.state == "posted" and ln.state == "deposited"
    ln.with_user(c.acct).action_issue_certificate()
    cert = ln.certificate_id
    assert (cert.state, cert.challan_no, ln.state) == ("issued", ch.challan_no, "certified")


def test_m51_w06_low_multiplier_refused_for_every_row(c):
    _refused(_deduction, c, partner_tin=False, multiplier=1.0, match="below the statutory")
    ok = _deduction(c, partner_tin=False, amount=round(100000.0 * c.rate.rate * 1.5 / 100.0, 2))
    assert ok.multiplier == 1.5


def test_m51_w07_psr_and_bank_default_unfavourable(c):
    vals = _deduction_vals(c)
    vals.pop("psr_received")
    vals.pop("paid_by_bank")
    vals["amount"] = round(100000.0 * c.rate.rate * 2.25 / 100.0, 2)
    move = _bill_posting(c, 100000.0, vals["amount"])
    ln = c.as_(c.acct)[WL]._fix_record_deductions([vals], move)
    assert (ln.psr_received, ln.paid_by_bank, ln.multiplier) == (False, False, 2.25)


def test_m51_w08_issued_certificate_frozen(c):
    ln, _ch = _deposited(c)
    ln.with_user(c.acct).action_issue_certificate()
    cert = ln.certificate_id
    _refused(
        cert.with_user(c.acct).write,
        {"withheld_amount": 1.0, "challan_no": "OTHER"},
        match="never edited",
    )
    _refused(ln.with_user(c.acct).write, {"amount": 1.0}, match="never edited")


def test_m51_w09_rate_comes_from_rate_row(c):
    _refused(_deduction, c, rate=3.0, amount=3000.0, match="rate comes from the Tax Rate Master")


def test_m51_w10_certified_state_written_directly(c):
    ln = _deduction(c)
    _refused(ln.with_user(c.acct).write, {"state": "certified"}, match="cannot be set directly")


def test_m51_w11_tds_return_from_draft_refused(c):
    ret = c.as_(c.acct)["fix.tds.return"].create({"quarter": _quarter(c)})
    _refused(ret.with_user(c.filer).action_file, "TYPED-ACK", match="prepare it")
    _refused(ret.with_user(c.acct).write, {"state": "prepared"}, match="cannot be set directly")


def _quarter(c):
    t = c.today
    return "%04d-Q%d" % (t.year if t.month >= 7 else t.year - 1, ((t.month - 7) % 12) // 3 + 1)


def test_m51_w12_tds_return_with_undeposited_deductions_refused(c):
    _deduction(c)
    ret = c.as_(c.acct)["fix.tds.return"].create({"quarter": _quarter(c)})
    ret.with_user(c.acct).action_prepare()
    _refused(ret.with_user(c.filer).action_file, "ACK-Q", match="not yet deposited")
    _refused(
        c.as_(c.acct)["fix.tds.return.line"].create,
        {
            "tds_return_id": ret.id,
            "vendor_name": "x",
            "base_amount": 1.0,
            "rate_percent": 1.0,
            "tds_amount": 1.0,
        },
    )


def test_ref_m51_tds_return_proper_path(c):
    _deposited(c)
    ret = c.as_(c.acct)["fix.tds.return"].create({"quarter": _quarter(c)})
    ret.with_user(c.acct).action_prepare()
    _refused(ret.with_user(c.acct).action_file, "ACK-1", match="Filing Approver")
    ret.with_user(c.filer).action_file("NBR-TDS-ACK-1")
    assert (ret.state, ret.filed_by_id) == ("filed", c.filer)


def test_m51_w13_tds_return_quarter_format(c):
    _refused(c.as_(c.acct)["fix.tds.return"].create, {"quarter": "Q2-2026"})


def test_m51_w14_challan_number_unique(c):
    c.as_(c.acct)["fix.tax.challan"].create(
        {"challan_no": "CH-UNIQ-1", "challan_date": c.today, "tax_kind": "tds", "amount": 10.0}
    )
    with pytest.raises(Exception), c.env.cr.savepoint():  # noqa: B017
        c.as_(c.acct)["fix.tax.challan"].create(
            {"challan_no": "CH-UNIQ-1", "challan_date": c.today, "tax_kind": "tds", "amount": 10.0}
        )


def test_m51_w15_deduction_without_gl_liability_refused(c):
    """M51-8: a deduction exists only with its posted liability."""
    _refused(c.as_(c.acct)[WL].create, _deduction_vals(c), match="_fix_record_deductions")
    short = _bill_posting(c, 100000.0, tds=100.0)
    _refused(c.as_(c.acct)[WL]._fix_record_deductions, [_deduction_vals(c)], short, match="exceed")


def test_m51_w16_vat_challan_settles_after_vds(c):
    """M51-11: a VAT challan settles net_payable_after_vds."""
    ret = c.cenv[RET].create(
        {
            "period": c.period,
            "state": "prepared",
            "net_payable": 1000.0,
            "net_payable_after_vds": 700.0,
        }
    )
    ch = c.as_(c.acct)["fix.tax.challan"].create(
        {
            "challan_no": "CH-VAT-1",
            "challan_date": c.today,
            "tax_kind": "vat",
            "amount": 700.0,
            "vat_return_id": ret.id,
        }
    )
    assert ch.liability_total == 700.0


# ======================================================= calendar / evidence
def test_m51_s01_evidence_never_marks_vat_return_done(c):
    rule = c.env.ref("cd_tax_engine_bd.due_rule_vat_91")
    key = (c.today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    _refused(
        c.as_(c.acct)["fix.statutory.filing"].create,
        {"rule_id": rule.id, "period_key": key, "reference": "anything"},
        match="typed filing evidence",
    )
    status, _detail = rule._status(key, c.co)
    assert status != "done"


def test_m51_s02_accountant_cannot_change_due_rules(c):
    rule = c.env["fix.statutory.due.rule"].sudo().search([("state", "=", "active")], limit=1)
    _refused(rule.with_user(c.acct).write, {"due_day": 28})


# ======================================================= audit pack
def test_m51_a01_audit_pack_detects_tampered_bundle(c):
    pack = c.as_(c.acct)["fix.tax.audit.pack"].create({"date_from": c.today, "date_to": c.today})
    pack.with_user(c.acct).action_generate()
    pack.attachment_id.sudo().write({"datas": base64.b64encode(b"tampered")})
    pack.with_user(c.acct).action_verify()
    assert pack.integrity_status == "tampered"


def test_m51_a02_audit_pack_rehash_refused_and_detected(c):
    pack = c.as_(c.acct)["fix.tax.audit.pack"].create({"date_from": c.today, "date_to": c.today})
    pack.with_user(c.acct).action_generate()
    pack.with_user(c.acct).action_verify()
    assert pack.integrity_status == "intact"
    fake = b"PK\x05\x06" + b"\x00" * 18
    _refused(
        pack.with_user(c.acct).write,
        {"pack_sha256": hashlib.sha256(fake).hexdigest(), "manifest": '{"files": []}'},
        match="cannot be set directly",
    )
    pack.attachment_id.sudo().write({"datas": base64.b64encode(fake)})
    pack.with_user(c.acct).action_verify()
    assert pack.integrity_status == "tampered"
    seal = pack.sudo().seal_id
    _refused(seal.with_user(c.mgr).write, {"pack_sha256": "x"})
    _refused(seal.sudo().unlink)


# ======================================================= contracts, GL mapping, wiring
def test_m51_c01_native_invoices_reach_the_register(c):
    """M51-9: _fix_register_from_invoice(move), swept by the 9.1 preparation.
    Runs in the main company (it has a chart for native invoicing)."""
    env = c.env
    company = env.company
    company.vat = BIN
    tax = env["account.tax"].search(
        [
            ("company_id", "=", company.id),
            ("type_tax_use", "=", "sale"),
            ("amount_type", "=", "percent"),
            ("amount", "=", 15.0),
        ],
        limit=1,
    )
    if not tax:
        group = env["account.tax.group"].search([("company_id", "=", company.id)], limit=1)
        tax = env["account.tax"].create(
            {
                "name": "A08 VAT 15",
                "amount": 15.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "company_id": company.id,
                **({"tax_group_id": group.id} if group else {}),
            }
        )
    product = env["product.product"].create({"name": "A08 repair", "default_code": "A08RPR"})
    move = env["account.move"].create(
        {
            "move_type": "out_invoice",
            "partner_id": c.customer.id,
            "invoice_date": c.today,
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "quantity": 1,
                        "price_unit": 2000.0,
                        "tax_ids": [(6, 0, tax.ids)],
                    },
                )
            ],
        }
    )
    move.action_post()
    # the billing engine registers it on posting (B4's hook); the 9.1 sweep
    # registers any posted invoice the hook did not reach
    acct = c.acct.sudo()
    acct.write({"company_ids": [(4, company.id)]})
    ret = env(user=c.acct.id, context=dict(env.context, allowed_company_ids=company.ids))[
        RET
    ].search([("period", "=", c.period), ("company_id", "=", company.id)]) or env(
        user=c.acct.id, context=dict(env.context, allowed_company_ids=company.ids)
    )[RET].create({"period": c.period})
    if ret.state == "filed":
        pytest.skip("the main company's 9.1 for this period is already filed")
    ret.with_user(c.acct).action_prepare()
    row = env[REG].search([("source_move_id", "=", move.id)])
    assert (row.row_type, row.vat_amount, row.posted) == ("invoice", move.amount_tax_signed, True)
    assert "standard_15" in row.treatment_summary
    start = c.today.replace(day=1)
    period_rows = (
        env[REG]
        .search(
            [
                ("company_id", "=", company.id),
                ("invoice_date", ">=", start),
                ("invoice_date", "<=", c.today.replace(day=28) + timedelta(days=4)),
            ]
        )
        .filtered(lambda r: r.invoice_date.strftime("%Y-%m") == c.period)
    )
    assert abs(ret.output_vat - sum(period_rows.mapped("vat_amount"))) < 0.01
    assert env[REG]._fix_register_from_invoice(move) == row  # idempotent


def test_m51_c02_input_vat_account_is_configuration(c):
    from odoo.addons.cd_tax_engine_bd.models.fix_tax_master import TAX_ACCOUNT_ROLES, tax_account

    assert TAX_ACCOUNT_ROLES["vat_input"][1] is None  # never the 110500 WIP collision
    c.env["ir.config_parameter"].sudo().set_param("cd_tax_engine_bd.vat_input_account_code", "")
    _refused(tax_account, c.env, c.co, "vat_input", match="vat_input")


def test_m51_c03_reclass_proposal_for_input_vat_posted_to_wip(c):
    """M51-8: the method the lead runs on fix_dev proposes (never posts) the
    re-class of AP input VAT that landed in 110500 Work in Progress."""
    wip = c.cenv["account.account"].create(
        {
            "code": "A8WIP%s" % next(_SEQ),
            "name": "Work in Progress",
            "account_type": "asset_current",
            "company_ids": [(6, 0, c.co.ids)],
        }
    )
    move = c.cenv["account.move"].create(
        {
            "journal_id": c.journal.id,
            "date": c.today,
            "line_ids": [
                (0, 0, {"account_id": c.expense.id, "name": "Bill X", "debit": 1000.0}),
                (0, 0, {"account_id": wip.id, "name": "Input VAT Bill X", "debit": 150.0}),
                (0, 0, {"account_id": c.ap.id, "name": "Bill X", "credit": 1150.0}),
            ],
        }
    )
    move.action_post()
    proposal = c.cenv[CREDIT]._fix_propose_vat_input_reclass(c.co, wip.code)
    assert proposal["total"] == 150.0 and len(proposal["source_lines"]) == 1
    assert proposal["entry"][0] == {
        "account": c.vat_in.code,
        "label": "Re-class AP input VAT from %s" % wip.code,
        "debit": 150.0,
        "credit": 0.0,
    }
    draft = c.cenv[CREDIT]._fix_propose_vat_input_reclass(c.co, wip.code, create_draft=True)
    reclass = c.env["account.move"].browse(draft["move_id"])
    assert reclass.state == "draft" and reclass.amount_total == 150.0


def test_m51_c04_invoice_created_consumer_registered(c):
    sub = c.env.ref("cd_tax_engine_bd.consumer_invoice_created_mushak_register")
    assert (sub.event_type, sub.model, sub.method) == (
        "invoice.created",
        "fix.mushak.register",
        "consume_invoice_created",
    )


def test_m51_x01_p03_surfaces_whitelisted_and_engine_methods_removed(c):
    from odoo.addons.cd_p03_portal.controllers.a08 import m51

    missing = [m for m, conf in m51.SURFACES.items() if "writable" not in conf]
    assert not missing, missing
    assert not {"action_mark_posted", "action_rebuild_from_events"} & m51.SURFACES[REG]["actions"]
    assert "action_issue" not in m51.SURFACES[CERT]["actions"]


def test_m51_x02_plain_user_cannot_read_register(c):
    _reg(c, 1000.0, 150.0)
    _refused(c.as_(c.plain)[REG].search_count, [])
    _refused(c.as_(c.plain)["fix.tax.rate"].search_count, [])


def test_m51_w17_certificate_for_a_non_ap_source(c):
    """A05 trade-in payouts withhold TDS outside AP: the deduction names its
    source model, and its certificate is issued under the same F5 rules
    (deposited by a verified challan, from the deduction, frozen once issued)."""
    field = c.env[CERT]._fields.get("vendor_invoice_id")
    if field is not None and field.required:
        pytest.skip("cd_ap_ext still makes vendor_invoice_id required (B2 change pending)")
    vals = _deduction_vals(c, source_model="fix.tradein", source_ref="TRADEIN-A08-1")
    vals.pop("vendor_invoice_id", None)
    line = c.as_(c.acct)[WL]._fix_record_deductions(
        [vals], _bill_posting(c, vals["base_amount"], vals["amount"])
    )
    ch = _challan(c, line, verify_by=c.acct2)
    ch.with_user(c.acct).action_confirm_deposit()
    line.with_user(c.acct).action_issue_certificate()
    cert = line.certificate_id
    assert (cert.state, cert.source_model, cert.source_ref, cert.challan_no) == (
        "issued",
        "fix.tradein",
        "TRADEIN-A08-1",
        ch.challan_no,
    )
    _refused(cert.with_user(c.acct).write, {"withheld_amount": 1.0}, match="never edited")


def test_m51_w18_vds_and_non_filer_exempt_rates_carry_no_ita_uplift(c):
    """The ITA 2023 default multiplier is an income-tax rule: a VDS line, or a
    rate row with non_filer_applies=False, for a payee with no TIN / PSR is
    withheld at the plain rate (B2: a VDS deduction for a no-TIN vendor was
    refused). A TDS line under a non-filer rate still carries the floor."""
    vds = c.env.ref("cd_tax_engine_bd.tax_rate_vds_rent")
    base = 100000.0
    vals = _deduction_vals(
        c,
        tax_kind="vds",
        rate_id=vds.id,
        partner_tin=False,
        psr_received=False,
        paid_by_bank=False,
        amount=round(base * vds.rate / 100.0, 2),
    )
    move = _entry(
        c,
        [
            (c.expense, base, 0.0),
            (c.vds_payable, 0.0, vals["amount"]),
            (c.ap, 0.0, base - vals["amount"]),
        ],
    )
    line = c.as_(c.acct)[WL]._fix_record_deductions([vals], move)
    assert (line.multiplier, line.defaults_count, line.statutory_shortfall) == (1.0, 0, 0.0)
    plain = c.cenv["fix.tax.rate"].create(
        {
            "tax_kind": "tds",
            "code": "a08_plain",
            "name": "flat",
            "rate": 2.0,
            "non_filer_applies": False,
            "company_id": c.co.id,
        }
    )
    flat = _deduction(c, rate_id=plain.id, partner_tin=False, psr_received=False, amount=2000.0)
    assert (flat.multiplier, flat.defaults_count) == (1.0, 0)
    # the TDS floor still holds where the master applies it
    _refused(_deduction, c, partner_tin=False, multiplier=1.0, match="below the statutory")
