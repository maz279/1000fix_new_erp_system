# cd_payroll_bd live-ORM tests — P08-M03 (CD-M56-01), DoD-03 statutory payroll.
#
# Every money figure below is hand-computed from the FY 2026-27 rules the
# engine documents (375k general threshold, 10/15/20% slabs, s.78 rebate,
# s.173 minimum tax, 2x overtime on basic/30/8, 10% + 10% PF) and from the
# Labour (Amendment) Act 2026 separation bands; the working is in comments.
import json
from datetime import date, datetime
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo import Command
from odoo.addons.cd_payroll_bd.models import fix_payroll
from odoo.exceptions import AccessError, UserError

pytestmark = [pytest.mark.financial, pytest.mark.tax]

PERIOD_START = date(2026, 1, 1)
PERIOD_END = date(2026, 1, 31)
COMPANY_ACCOUNT = "2051234567"
COMPANY_ROUTING = "175261726"


def _events(env, event_type, aggregate_id):
    rows = env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)]
    )
    return [json.loads(r.payload) for r in rows]


def _employee(env, name, company=None):
    vals = {"name": name}
    if company:
        vals["company_id"] = company.id
    return env["hr.employee"].create(vals)


def _contract(env, emp, basic, state="active", joining=date(2020, 1, 1)):
    return env["fix.employment.contract"].create(
        {
            "employee_id": emp.id,
            "company_id": emp.company_id.id,
            "contract_type": "permanent",
            "joining_date": joining,
            "basic_monthly": basic,
            "state": state,
        }
    )


def _period(env, name="2026-01", **vals):
    return env["fix.payroll.period"].create(
        {"name": name, "period_start": PERIOD_START, "period_end": PERIOD_END, **vals}
    )


def _slip(env, period, emp, basic, **vals):
    return env["fix.payslip"].create(
        {"period_id": period.id, "employee_id": emp.id, "basic": basic, **vals}
    )


def _fixed_now(value):
    class _Fixed(datetime):
        @classmethod
        def now(cls, tz=None):
            return value

    return _Fixed


def _bdt_company(env, name="1000FiX Payroll Test Ltd", code="PAYT"):
    """A BDT-ledger company with its operating unit (synthetic test data)."""
    bdt = env.ref("base.BDT")
    bdt.active = True
    company = env["res.company"].create({"name": name, "currency_id": bdt.id})
    env["operating.unit"].create(
        {
            "name": f"{name} OU",
            "code": code,
            "partner_id": company.partner_id.id,
            "company_id": company.id,
        }
    )
    return company


def _account(env, company, code, name, account_type):
    return (
        env["account.account"]
        .with_company(company)
        .create(
            {
                "code": code,
                "name": name,
                "account_type": account_type,
                "company_ids": [Command.set([company.id])],
            }
        )
    )


def _configure_payroll_gl(env, company, skip=()):
    """Finance's payroll GL set-up for the company (a test chart of accounts)."""
    journal = env["account.journal"].create(
        {"name": "Payroll", "code": "PAYR", "type": "general", "company_id": company.id}
    )
    vals = {
        "payroll_journal_id": journal.id,
        "payroll_salary_expense_account_id": _account(
            env, company, "610100", "Salaries & Wages", "expense"
        ).id,
        "payroll_pf_expense_account_id": _account(
            env, company, "610200", "Employer PF Contribution", "expense"
        ).id,
        "payroll_net_payable_account_id": _account(
            env, company, "210100", "Salaries Payable", "liability_current"
        ).id,
        "payroll_tax_payable_account_id": _account(
            env, company, "210200", "TDS Payable - Salaries", "liability_current"
        ).id,
        "payroll_pf_payable_account_id": _account(
            env, company, "210300", "Provident Fund Payable", "liability_current"
        ).id,
    }
    company.write({key: value for key, value in vals.items() if key not in skip})


def _company_env(env, company):
    return env(context=dict(env.context, allowed_company_ids=[company.id]))


@pytest.fixture
def payroll_co(odoo_env):
    """A BDT company whose payroll GL is configured; `env` acts in it."""
    company = _bdt_company(odoo_env)
    _configure_payroll_gl(odoo_env, company)
    return SimpleNamespace(env=_company_env(odoo_env, company), company=company)


def _move_lines(move):
    return sorted(
        (line.account_id.code, line.name, line.debit, line.credit) for line in move.line_ids
    )


# ---------------------------------------------------------------------------
# Payslip arithmetic — the mapping onto the engine (fix.payslip._compute_slip)
# ---------------------------------------------------------------------------


def test_payslip_untaxed_with_overtime(odoo_env):
    # basic 30,000; OT 2h: hourly 30,000/30/8 = 125 -> 2 x 125 x 2h = 500
    # gross 30,500; PF 10% of basic = 3,000 each wing
    # annual taxable (30,500 - 3,000) x 12 = 330,000 < 375,000 -> no tax
    period = _period(odoo_env)
    slip = _slip(odoo_env, period, _employee(odoo_env, "Karim"), 30000.0, ot_hours=2.0)
    assert slip.overtime == 500.00
    assert slip.gross == 30500.00
    assert (slip.pf_employee, slip.pf_employer) == (3000.00, 3000.00)
    assert slip.tax_withheld == 0.00
    assert slip.net == 27500.00


def test_payslip_general_slab_tax(odoo_env):
    # basic 60,000: annual (60,000 - 6,000) x 12 = 648,000; 648,000 - 375,000
    # = 273,000 in the 10% band = 27,300 (> 5,000 minimum) -> 2,275.00 / month
    slip = _slip(odoo_env, _period(odoo_env), _employee(odoo_env, "Nasrin"), 60000.0)
    assert slip.tax_withheld == 2275.00
    assert slip.net == 51725.00  # 60,000 - 6,000 - 2,275


def test_payslip_category_and_investment_rebate(odoo_env):
    # female/senior threshold 400,000: 648,000 - 400,000 = 248,000 @10% = 24,800
    # s.78 rebate = min(3% x 648,000 = 19,440; 15% x 100,000 = 15,000; 1M) = 15,000
    # 24,800 - 15,000 = 9,800 (> 5,000 minimum) -> 9,800 / 12 = 816.67
    slip = _slip(
        odoo_env,
        _period(odoo_env),
        _employee(odoo_env, "Shirin"),
        60000.0,
        taxpayer_category="female_senior",
        investment_allowance=100000.0,
    )
    assert slip.tax_withheld == 816.67
    assert slip.net == 53183.33  # 60,000 - 6,000 - 816.67


def test_payslip_disabled_child_raises_threshold(odoo_env):
    # 375,000 + 50,000 = 425,000; 648,000 - 425,000 = 223,000 @10% = 22,300
    # -> 1,858.33 / month
    slip = _slip(
        odoo_env,
        _period(odoo_env),
        _employee(odoo_env, "Babul"),
        60000.0,
        has_disabled_child=True,
    )
    assert slip.tax_withheld == 1858.33
    assert slip.net == 52141.67


@pytest.mark.parametrize(
    ("location", "monthly_tax", "net"),
    [
        # annual (30,000 - 3,000) x 12 + 76,000 YTD = 400,000; 25,000 over the
        # threshold @10% = 2,500 -> raised to the s.173 minimum for the area
        ("non_city_corporation", 250.00, 26750.00),  # 3,000 / 12
        ("other_city_corporation", 333.33, 26666.67),  # 4,000 / 12
        ("dhaka_chattogram", 416.67, 26583.33),  # 5,000 / 12
    ],
)
def test_payslip_minimum_tax_by_location(odoo_env, location, monthly_tax, net):
    slip = _slip(
        odoo_env,
        _period(odoo_env),
        _employee(odoo_env, "Rupa"),
        30000.0,
        annual_taxable_other=76000.0,
        minimum_tax_location=location,
    )
    assert slip.tax_withheld == monthly_tax
    assert slip.net == net


def test_payslip_empty_category_and_location_fall_back(odoo_env):
    # Cleared selections fall back to general / Dhaka: same as the slab case.
    slip = _slip(
        odoo_env,
        _period(odoo_env),
        _employee(odoo_env, "Jamal"),
        60000.0,
        taxpayer_category=False,
        minimum_tax_location=False,
    )
    assert slip.tax_withheld == 2275.00


# ---------------------------------------------------------------------------
# Journey 13 — lock -> calculate -> approve -> pay (BEFTN) -> post
# ---------------------------------------------------------------------------


def _locked_attendance(env):
    lock = env["fix.attendance.lock"].create(
        {"name": "Jan 2026", "period_start": PERIOD_START, "period_end": PERIOD_END}
    )
    lock.action_lock()
    return lock


def test_calculation_is_refused_on_open_attendance(odoo_env):
    period = _period(odoo_env)
    with (
        pytest.raises(UserError, match="Lock attendance before calculating"),
        odoo_env.cr.savepoint(),
    ):
        period.action_calculate()
    with (
        pytest.raises(UserError, match="may not calculate on open attendance"),
        odoo_env.cr.savepoint(),
    ):
        period.action_verify_attendance_locked()
    assert period.state == "draft"


def test_state_guards_refuse_out_of_order_steps(odoo_env):
    period = _period(odoo_env)
    with pytest.raises(UserError, match="Calculate before approving"), odoo_env.cr.savepoint():
        period.action_approve()
    with pytest.raises(UserError, match="Approve before paying"), odoo_env.cr.savepoint():
        period.action_pay()
    with pytest.raises(UserError, match="Pay before posting"), odoo_env.cr.savepoint():
        period.action_post()


def test_full_cycle_lock_calculate_approve_pay_post(payroll_co):
    env = payroll_co.env
    karim = _employee(env, "Karim Uddin")
    nasrin = _employee(env, "Nasrin Sultana")
    draft_only = _employee(env, "Draft Contract")
    _contract(env, karim, 30000.0)
    _contract(env, nasrin, 60000.0)
    _contract(env, draft_only, 90000.0, state="draft")
    other_company = env["res.company"].create({"name": "Sister Concern Ltd"})
    outsider = _employee(env, "Other Company Staff", company=other_company)
    _contract(env, outsider, 45000.0)
    # 10h on the LAST day of the period: 2h overtime that must reach the slip
    env["fix.attendance.record"].create(
        {
            "employee_id": karim.id,
            "check_in": datetime(2026, 1, 31, 8, 0),
            "check_out": datetime(2026, 1, 31, 18, 0),
        }
    )
    # outside the period: never counted
    env["fix.attendance.record"].create(
        {
            "employee_id": karim.id,
            "check_in": datetime(2026, 2, 1, 8, 0),
            "check_out": datetime(2026, 2, 1, 20, 0),
        }
    )
    _locked_attendance(env)

    period = _period(env)
    manual = _slip(env, period, karim, 1.0)
    period.action_verify_attendance_locked()
    assert period.state == "attendance_locked"
    assert _events(env, "payroll.attendance_locked", period.id) == [{"period": "2026-01"}]

    period.action_calculate()
    assert period.state == "calculated"
    assert period.calculator_id == env.user
    assert not manual.exists()  # a recalculation replaces earlier slips
    slips = {s.employee_id: s for s in period.payslip_ids}
    assert set(slips) == {karim, nasrin}  # no draft contract, no other company
    assert (slips[karim].ot_hours, slips[karim].overtime, slips[karim].net) == (2.0, 500.0, 27500.0)
    assert slips[nasrin].net == 51725.00
    # totals: gross 30,500 + 60,000; tax 0 + 2,275; PF (3,000 + 6,000) x 2
    assert period.slip_count == 2
    assert period.gross_total == 90500.00
    assert period.tax_total == 2275.00
    assert period.pf_total == 18000.00
    assert period.net_total == 79225.00

    # Maker-checker: the calculator may not approve their own run
    with pytest.raises(UserError, match="Maker-Checker SoD violation"), env.cr.savepoint():
        period.action_approve()
    checker = env["res.users"].create({"name": "Payroll Checker", "login": "payroll.checker.t"})
    period.calculator_id = checker
    period.action_approve()
    assert period.state == "approved"
    assert _events(env, "payroll.approved", period.id) == [{"period": "2026-01", "net": 79225.0}]

    # Pay: no company originating account -> refused (no assumed account).
    # The savepoint plays the request transaction a UserError rolls back.
    with pytest.raises(UserError, match="company originating account"), env.cr.savepoint():
        period.action_pay()
    assert period.state == "approved"
    assert not env["fix.beftn.batch"].search([("period_id", "=", period.id)])
    period.write({"company_account_no": COMPANY_ACCOUNT, "company_routing_no": COMPANY_ROUTING})
    # ...and no employee bank details -> refused, naming both employees
    with pytest.raises(UserError, match="Karim Uddin, Nasrin Sultana"), env.cr.savepoint():
        period.action_pay()
    assert period.state == "approved"
    slips[karim].write({"routing_no": "060274689", "bank_account_no": "1501203345001"})
    slips[nasrin].write({"routing_no": "090261725", "bank_account_no": "2702150098761"})
    submitted = datetime(2026, 10, 1, 17, 0)  # Thursday after the 16:00 cut-off
    with (
        mock.patch.object(fix_payroll, "datetime", _fixed_now(submitted)),
        mock.patch(
            "libs.py.payroll_engine.beftn.datetime", _fixed_now(datetime(2026, 10, 1, 17, 5))
        ),
    ):
        period.action_pay()
    batch = period.beftn_batch_id
    assert period.state == "paid"
    # Fri 2 + Sat 3 are the weekend -> settles Sunday 4 October
    assert batch.settlement_date == date(2026, 10, 4)
    assert (batch.employee_count, batch.total_amount) == (2, 79225.00)
    assert (batch.company_account_no, batch.company_routing_no) == (
        COMPANY_ACCOUNT,
        COMPANY_ROUTING,
    )
    lines = batch.file_content.split("\r\n")
    assert [line[:1] for line in lines] == ["1", "5", "6", "6", "8", "9", ""]
    assert all(len(line) == 128 for line in lines[:-1])
    # 27,500.00 + 51,725.00 = 7,922,500 paisa in the batch and file controls
    assert lines[4][32:44] == "000007922500"
    assert lines[5][43:55] == "000007922500"
    assert _events(env, "payroll.beftn_submitted", period.id) == [
        {"period": "2026-01", "batch_id": batch.id, "settlement": "2026-10-04"}
    ]

    period.action_post()
    assert period.state == "posted"
    move = period.gl_move_id
    assert move.state == "posted"
    assert move.company_id == payroll_co.company
    assert move.journal_id == payroll_co.company.payroll_journal_id
    assert (move.ref, move.date) == ("Payroll GL Posting - 2026-01", PERIOD_END)
    # Dr basic 30,000 + 60,000; overtime 500; employer PF 3,000 + 6,000
    # Cr net 27,500 + 51,725; TDS 0 + 2,275; PF (3,000 + 6,000) x 2
    # (no incentive this month: no incentive line)
    assert _move_lines(move) == [
        ("210100", "Net salary payable - 2026-01", 0.0, 79225.0),
        ("210200", "Income tax withheld (TDS) - 2026-01", 0.0, 2275.0),
        ("210300", "Provident fund payable - 2026-01", 0.0, 18000.0),
        ("610100", "Basic salary - 2026-01", 90000.0, 0.0),
        ("610100", "Overtime - 2026-01", 500.0, 0.0),
        ("610200", "Employer PF contribution - 2026-01", 9000.0, 0.0),
    ]
    assert sum(move.line_ids.mapped("debit")) == sum(move.line_ids.mapped("credit")) == 99500.0
    # every line carries the company operating unit (AS-03 dimension)
    dimensions = env["fix.journal.dimension"].search([("move_line_id", "in", move.line_ids.ids)])
    assert len(dimensions) == 6
    assert dimensions.operating_unit_id.company_id == payroll_co.company
    assert _events(env, "payroll.posted", period.id) == [
        {
            "period": "2026-01",
            "gross": 90500.0,
            "net": 79225.0,
            "tax": 2275.0,
            "pf": 18000.0,
            "total_debit": 99500.0,
            "total_credit": 99500.0,
        }
    ]
    # idempotent: a posted period is never posted twice
    with pytest.raises(UserError, match="already posted to the GL"), env.cr.savepoint():
        period.action_post()
    assert env["account.move"].search_count([("ref", "=", "Payroll GL Posting - 2026-01")]) == 1


def test_the_former_bypass_context_no_longer_allows_self_approval(odoo_env):
    """Regression: with_context(bypass_payroll_sod=True) let the calculator
    approve its own payroll (reachable over RPC) - the context is ignored."""
    period = _period(odoo_env)
    period.write({"state": "calculated", "calculator_id": odoo_env.user.id})
    with pytest.raises(UserError, match="Maker-Checker SoD"), odoo_env.cr.savepoint():
        period.with_context(bypass_payroll_sod=True).action_approve()
    assert period.state == "calculated"


def test_approval_requires_the_payroll_manager_role(odoo_env):
    env = odoo_env
    users = env["res.users"].with_context(no_reset_password=True)
    clerk = users.create(
        {
            "name": "Payroll Probe Employee",
            "login": "payroll.probe.employee@example.test",
            "group_ids": [(6, 0, [env.ref("base.group_user").id])],
        }
    )
    officer = users.create(
        {
            "name": "Payroll Probe Officer",
            "login": "payroll.probe.officer@example.test",
            "group_ids": [(6, 0, [env.ref("cd_payroll_bd.group_payroll_officer").id])],
        }
    )
    period = _period(env, state="calculated")
    # a plain employee holds no payroll ACL at all
    for model in ("fix.payroll.period", "fix.payslip", "fix.beftn.batch"):
        assert not env[model].with_user(clerk).has_access("read"), model
    # an officer prepares but cannot approve (nor create BEFTN batches)
    assert env["fix.payslip"].with_user(officer).has_access("write")
    assert not env["fix.beftn.batch"].with_user(officer).has_access("create")
    with pytest.raises(AccessError, match="Payroll Manager"), env.cr.savepoint():
        period.with_user(officer).action_approve()
    assert period.state == "calculated"
    assert env.ref("base.user_admin").has_group("cd_payroll_bd.group_payroll_manager")


def test_approval_without_recorded_calculator(odoo_env):
    period = _period(odoo_env, state="calculated")
    period.action_approve()
    assert period.state == "approved"


def test_calculation_carries_only_real_bank_details(odoo_env):
    """R01 regression: no fabricated "1234567890123" / "020260123" /
    "BRAC Bank PLC" — a missing account stays empty and blocks BEFTN."""
    env = odoo_env
    unbanked = _employee(env, "No Bank Yet")
    banked = _employee(env, "Has Salary Account")
    _contract(env, unbanked, 30000.0)
    _contract(env, banked, 30000.0)
    bank = env["res.bank"].create({"name": "Sonali Bank PLC"})
    account = env["res.partner.bank"].create(
        {
            "acc_number": "0112233445566",
            "partner_id": banked.work_contact_id.id,
            "bank_id": bank.id,
        }
    )
    banked.bank_account_ids = [(6, 0, [account.id])]
    _locked_attendance(env)
    period = _period(env)
    period.action_verify_attendance_locked()
    period.action_calculate()
    slips = {s.employee_id: s for s in period.payslip_ids}

    empty = slips[unbanked]
    assert (empty.bank_account_no, empty.routing_no, empty.bank_name) == (False, False, False)
    # the employee's registered salary account (Odoo 19 primary_bank_account_id)
    real = slips[banked]
    assert (real.bank_account_no, real.bank_name) == ("0112233445566", "Sonali Bank PLC")
    assert real.routing_no is False  # never assumed: the officer enters it
    for slip in period.payslip_ids:
        assert "1234567890123" not in (slip.bank_account_no or "")
        assert slip.routing_no != "020260123"
        assert slip.bank_name != "BRAC Bank PLC"


def _paid_period(ctx, basic=30000.0):
    """A paid 2026-01 period in ctx's company with one payslip of `basic`
    (30,000: gross 30,000; PF 3,000 + 3,000; tax 0; net 27,000)."""
    period = _period(ctx.env, state="paid")
    _slip(ctx.env, period, _employee(ctx.env, "Rana Hamid"), basic)
    return period


def test_post_refused_until_payroll_accounting_is_configured(odoo_env):
    company = _bdt_company(odoo_env, name="Unconfigured Ltd", code="UNCF")
    ctx = SimpleNamespace(env=_company_env(odoo_env, company), company=company)
    period = _paid_period(ctx)
    with pytest.raises(UserError) as err, ctx.env.cr.savepoint():
        period.action_post()
    assert str(err.value) == (
        "Configure the payroll accounting of Unconfigured Ltd before posting 2026-01: "
        "Payroll Journal, Salary & Wage Expense, Employer PF Contribution Expense, "
        "Net Salary Payable, Income Tax (TDS) Payable, Provident Fund Payable."
    )
    assert period.state == "paid"
    assert not period.gl_move_id
    # one account still missing: still refused, naming only that account
    _configure_payroll_gl(odoo_env, company, skip=("payroll_tax_payable_account_id",))
    with (
        pytest.raises(UserError, match=r"posting 2026-01: Income Tax \(TDS\) Payable\.$"),
        ctx.env.cr.savepoint(),
    ):
        period.action_post()
    assert period.state == "paid"
    assert not odoo_env["account.move"].search([("company_id", "=", company.id)])


def test_post_refuses_another_companys_accounts(payroll_co, odoo_env):
    other = _bdt_company(odoo_env, name="Borrowed Books Ltd", code="BRWD")
    _configure_payroll_gl(odoo_env, other)
    payroll_co.company.write(
        {
            "payroll_journal_id": other.payroll_journal_id.id,
            "payroll_pf_payable_account_id": other.payroll_pf_payable_account_id.id,
        }
    )
    period = _paid_period(payroll_co)
    with (
        pytest.raises(
            UserError,
            match="do not belong to the company: Payroll Journal, Provident Fund Payable",
        ),
        payroll_co.env.cr.savepoint(),
    ):
        period.action_post()
    assert period.state == "paid"


def test_post_refuses_a_period_in_another_currency(odoo_env):
    # the default company keeps a USD ledger; payroll periods are in BDT
    assert odoo_env.company.currency_id.name == "USD"
    period = _period(odoo_env, state="paid")
    with (
        pytest.raises(UserError, match=r"is in BDT but .* keeps its ledger in USD"),
        odoo_env.cr.savepoint(),
    ):
        period.action_post()
    assert period.state == "paid"


def test_post_refuses_a_period_with_nothing_to_post(payroll_co):
    period = _paid_period(payroll_co, basic=0.0)
    with (
        pytest.raises(UserError, match="Payroll period 2026-01 has nothing to post"),
        payroll_co.env.cr.savepoint(),
    ):
        period.action_post()
    assert period.state == "paid"


def test_post_lines_only_for_components_carried(payroll_co):
    period = _paid_period(payroll_co)
    period.action_post()
    # no overtime, incentive or tax this month
    assert _move_lines(period.gl_move_id) == [
        ("210100", "Net salary payable - 2026-01", 0.0, 27000.0),
        ("210300", "Provident fund payable - 2026-01", 0.0, 6000.0),
        ("610100", "Basic salary - 2026-01", 30000.0, 0.0),
        ("610200", "Employer PF contribution - 2026-01", 3000.0, 0.0),
    ]
    assert period.gl_move_id.state == "posted"


def test_post_with_incentive_line(payroll_co):
    period = _paid_period(payroll_co)
    period.payslip_ids.incentive = 2400.0  # M57 incentive applied before approval
    # gross 32,400; PF 3,000 + 3,000; annual (32,400 - 3,000) x 12 = 352,800
    # < 375,000 -> no tax; net 29,400
    period.action_post()
    assert ("610100", "Incentive - 2026-01", 2400.0, 0.0) in _move_lines(period.gl_move_id)
    assert ("210100", "Net salary payable - 2026-01", 0.0, 29400.0) in _move_lines(
        period.gl_move_id
    )


def test_post_refuses_unbalanced_ledger(payroll_co):
    env = payroll_co.env
    period = _paid_period(payroll_co)
    # corrupt the stored net (bypassing the engine) by 100.00
    env.flush_all()
    env.cr.execute(
        "UPDATE fix_payslip SET net = net - 100 WHERE id IN %s", [tuple(period.payslip_ids.ids)]
    )
    env.invalidate_all()
    # Dr 30,000 + 3,000 = 33,000; Cr 26,900 + 6,000 + 0 = 32,900
    with (
        pytest.raises(UserError, match=r"Debits \(33000.00\) != Credits \(32900.00\)"),
        env.cr.savepoint(),
    ):
        period.action_post()
    assert period.state == "paid"
    assert not period.gl_move_id


# ---------------------------------------------------------------------------
# BEFTN batch file (INT-005) — refusals and the exact fixed-width content
# ---------------------------------------------------------------------------


def _batch(env, period, **vals):
    base = {
        "period_id": period.id if period else False,
        "submitted_at": datetime(2026, 10, 5, 10, 30),
        "settlement_date": date(2026, 10, 5),
        "company_account_no": COMPANY_ACCOUNT,
        "company_routing_no": COMPANY_ROUTING,
    }
    base.update(vals)
    return env["fix.beftn.batch"].create(base)


def test_beftn_refuses_without_period(odoo_env):
    with pytest.raises(UserError, match="No payroll period linked"), odoo_env.cr.savepoint():
        _batch(odoo_env, None).action_generate_beftn_file()


@pytest.mark.parametrize(
    ("account", "routing"),
    [(False, COMPANY_ROUTING), (COMPANY_ACCOUNT, False), ("   ", COMPANY_ROUTING)],
)
def test_beftn_refuses_without_company_originating_details(odoo_env, account, routing):
    period = _period(odoo_env)
    _slip(odoo_env, period, _employee(odoo_env, "Payee"), 30000.0)
    batch = _batch(odoo_env, period, company_account_no=account, company_routing_no=routing)
    with (
        pytest.raises(UserError, match="Enter the company originating account and routing"),
        odoo_env.cr.savepoint(),
    ):
        batch.action_generate_beftn_file()
    assert not batch.file_content


def test_beftn_refuses_malformed_company_routing(odoo_env):
    period = _period(odoo_env)
    batch = _batch(odoo_env, period, company_routing_no="17526172")  # 8 digits
    with (
        pytest.raises(UserError, match="Invalid company routing number '17526172'"),
        odoo_env.cr.savepoint(),
    ):
        batch.action_generate_beftn_file()


def test_beftn_refuses_when_nothing_is_payable(odoo_env):
    period = _period(odoo_env)
    _slip(odoo_env, period, _employee(odoo_env, "Unpaid Leave"), 0.0)  # net 0
    with pytest.raises(UserError, match="no payable payslip"), odoo_env.cr.savepoint():
        _batch(odoo_env, period).action_generate_beftn_file()


def test_beftn_refuses_missing_employee_bank_details_naming_them(odoo_env):
    period = _period(odoo_env)
    _slip(odoo_env, period, _employee(odoo_env, "Ayesha"), 30000.0, bank_account_no="11223344")
    _slip(odoo_env, period, _employee(odoo_env, "Mitu"), 30000.0, routing_no="060274689")
    _slip(
        odoo_env,
        period,
        _employee(odoo_env, "Blank Routing"),
        30000.0,
        routing_no="   ",
        bank_account_no="11223344",
    )
    _slip(
        odoo_env,
        period,
        _employee(odoo_env, "Complete"),
        30000.0,
        routing_no="060274689",
        bank_account_no="11223344",
    )
    batch = _batch(odoo_env, period)
    with pytest.raises(UserError) as err, odoo_env.cr.savepoint():
        batch.action_generate_beftn_file()
    message = str(err.value)
    assert "Bank details are missing for: Ayesha, Mitu, Blank Routing." in message
    assert "Complete" not in message
    assert not batch.file_content


def test_beftn_refuses_malformed_employee_routing(odoo_env):
    period = _period(odoo_env)
    _slip(
        odoo_env,
        period,
        _employee(odoo_env, "Sumon"),
        30000.0,
        routing_no="06027468X",
        bank_account_no="1501203345001",
    )
    with (
        pytest.raises(UserError, match="Invalid bank routing number for employee Sumon"),
        odoo_env.cr.savepoint(),
    ):
        _batch(odoo_env, period).action_generate_beftn_file()


def test_beftn_refuses_account_longer_than_the_field(odoo_env):
    period = _period(odoo_env)
    _slip(
        odoo_env,
        period,
        _employee(odoo_env, "Long Account"),
        30000.0,
        routing_no="060274689",
        bank_account_no="123456789012345678",  # 18 > 17 characters
    )
    with (
        pytest.raises(UserError, match="Long Account is longer than the 17-character"),
        odoo_env.cr.savepoint(),
    ):
        _batch(odoo_env, period).action_generate_beftn_file()


def test_beftn_happy_path_fixed_width_file(odoo_env):
    period = _period(odoo_env, name="2026-09")
    rahima = _employee(odoo_env, "Rahima Akter")
    # basic 30,000 - PF 3,000 - tax 0 -> net 27,000.00 = 2,700,000 paisa
    _slip(
        odoo_env,
        period,
        rahima,
        30000.0,
        routing_no=" 060274689 ",
        bank_account_no=" 1501203345001 ",
    )
    _slip(odoo_env, period, _employee(odoo_env, "Zero Net"), 0.0)  # not payable, not in file
    batch = _batch(odoo_env, period)
    with mock.patch(
        "libs.py.payroll_engine.beftn.datetime", _fixed_now(datetime(2026, 10, 5, 10, 30))
    ):
        content = batch.action_generate_beftn_file()

    batch_no = str(batch.id).rjust(7, "0")
    emp_ref = f"EMP{rahima.id:05d}".ljust(15)
    expected = [
        # 1 file header: priority 01, dest BBANK, origin routing, 261005 1030, A 128 10 1
        "101BBANK     175261726 2610051030A128101"
        "BANGLADESH BANK        1000FIX SERVICES LTD   SALARY  " + " " * 34,
        # 5 batch header: 220 credits, company, account, PPD, "SALARY 202"(10),
        # created 261005, effective 261005, originator DFI 17526172, batch no
        "52201000FIX SERVICES" + " " * 20 + "2051234567PPDSALARY 202261005261005   1"
        "17526172" + batch_no + " " * 34,
        # 6 entry: 22 demand credit, DFI 06027468 check 9, account(17), paisa(10),
        # id(15), name(22), 2 blanks, addenda 0, trace = DFI + 0000001
        "62206027468"
        + "9"
        + "1501203345001    "
        + "0002700000"
        + emp_ref
        + "Rahima Akter          "
        + "  "
        + "0"
        + "175261720000001"
        + " " * 34,
        # 8 batch control: 1 entry, hash 06027468, debit 0, credit 2,700,000
        "8220000001"
        + "0006027468"
        + "0" * 12
        + "000002700000"
        + "2051234567"
        + " " * 25
        + "17526172"
        + batch_no
        + " " * 34,
        # 9 file control: 1 batch, 1 block, 1 entry, hash, debit 0, credit
        "9000001000001000000010006027468" + "0" * 12 + "000002700000" + " " * 73,
    ]
    assert all(len(line) == 128 for line in expected)
    assert content == "\r\n".join(expected) + "\r\n"
    assert batch.file_content == content
    assert batch.file_name == f"BEFTN_2026-09_{batch.id}.txt"


def test_settlement_waits_for_the_settlement_date(odoo_env):
    period = _period(odoo_env)
    future = _batch(odoo_env, period, settlement_date=date(2099, 1, 4))
    with pytest.raises(UserError, match="BEFTN settles 2099-01-04"), odoo_env.cr.savepoint():
        future.action_settle()
    assert future.state == "submitted"
    due = _batch(odoo_env, period, settlement_date=date(2026, 1, 4))
    due.action_settle()
    assert due.state == "settled"
    assert _events(odoo_env, "payroll.beftn_settled", due.id) == [{"settlement": "2026-01-04"}]


# ---------------------------------------------------------------------------
# Separation pay — Labour (Amendment) Act 2026 / BLA 2006 s.20 & s.26
# ---------------------------------------------------------------------------


def _slip_with_contract(env, joining, state="active", basic=30000.0):
    emp = _employee(env, "Leaver %s" % joining.isoformat())
    _contract(env, emp, basic, state=state, joining=joining)
    return _slip(env, _period(env), emp, basic)


def test_separation_six_years(odoo_env):
    # 2019-03-15 -> 2026-03-14 = 6 completed years; daily 30,000/30 = 1,000
    # gratuity 6 x 30 days = 180,000; resignation 6 x 15 days (5-<10y) = 90,000
    slip = _slip_with_contract(odoo_env, date(2019, 3, 15), state="terminated")
    result = slip.action_compute_separation(date(2026, 3, 14))
    assert result == {"gratuity": 180000.0, "resignation": 90000.0}
    assert _events(odoo_env, "payroll.separation_computed", slip.id) == [
        {
            "employee": "Leaver 2019-03-15",
            "gratuity": 180000.0,
            "resignation_compensation": 90000.0,
        }
    ]


def test_separation_below_gratuity_vesting(odoo_env):
    # 3 completed years: no gratuity (5-year vesting); 3 x 7 days x 1,000 = 21,000
    slip = _slip_with_contract(odoo_env, date(2023, 1, 1))
    assert slip.action_compute_separation(date(2026, 1, 1)) == {
        "gratuity": 0.0,
        "resignation": 21000.0,
    }


@pytest.mark.parametrize(
    ("notice_days", "expected"),
    [
        (0, 300000.0),  # 6 x 30 x 1,000 = 180,000 + 120 days in lieu = 120,000
        (30, 270000.0),  # 90 days in lieu
        (120, 180000.0),  # full notice served
    ],
)
def test_retrenchment_compensation(odoo_env, notice_days, expected):
    slip = _slip_with_contract(odoo_env, date(2019, 3, 15))
    assert slip.action_compute_retrenchment(date(2026, 3, 14), notice_days) == expected


def test_separation_and_retrenchment_need_a_contract(odoo_env):
    slip = _slip(odoo_env, _period(odoo_env), _employee(odoo_env, "No Contract"), 30000.0)
    with (
        pytest.raises(UserError, match="No contract found for separation pay"),
        odoo_env.cr.savepoint(),
    ):
        slip.action_compute_separation(date(2026, 3, 14))
    with (
        pytest.raises(UserError, match="No contract found for retrenchment pay"),
        odoo_env.cr.savepoint(),
    ):
        slip.action_compute_retrenchment(date(2026, 3, 14))
