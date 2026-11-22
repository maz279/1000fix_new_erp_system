# cd_payroll_bd live-ORM tests — P08-M03 (CD-M56-01), DoD-03 statutory payroll.
#
# Every money figure below is hand-computed from the FY 2026-27 rules the
# engine documents (375k general threshold, 10/15/20% slabs, s.78 rebate,
# s.173 minimum tax, 2x overtime on basic/30/8, 10% + 10% PF) and from the
# Labour (Amendment) Act 2026 separation bands; the working is in comments.
import json
from datetime import date, datetime, timedelta
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
    # basic 30,000; OT 2h: hourly 30,000/208 = 144.2307... -> 2 x hourly x 2h = 576.92
    # gross 30,576.92; PF 10% of basic = 3,000 each wing
    # annual taxable (30,576.92 - 3,000) x 12 = 330,923.04 < 375,000 -> no tax
    period = _period(odoo_env)
    slip = _slip(odoo_env, period, _employee(odoo_env, "Karim"), 30000.0, ot_hours=2.0)
    assert slip.overtime == 576.92
    assert slip.gross == 30576.92
    assert (slip.pf_employee, slip.pf_employer) == (3000.00, 3000.00)
    assert slip.tax_withheld == 0.00
    assert slip.net == 27576.92


def test_payslip_contract_allowances_and_ita2023_exemption(odoo_env):
    """RAP-M56-01 & RAP-M56-03: contract with basic 40,000 + HR 12,000 + med 4,000 + conv 2,500
    -> gross 58,500; ITA 2023 Para 27 exemption min(employment_income/3, 450,000)."""
    env = odoo_env
    emp = _employee(env, "Tariq Allowance")
    _contract(env, emp, 40000.0).write(
        {
            "house_rent": 12000.0,
            "medical_allowance": 4000.0,
            "conveyance_allowance": 2500.0,
        }
    )
    _locked_attendance(env)
    period = _period(env, name="2026-01-ALLOW")
    period.action_verify_attendance_locked()
    period.action_calculate()
    slip = period.payslip_ids.filtered(lambda s: s.employee_id == emp)
    assert len(slip) == 1
    assert slip.basic == 40000.0
    assert slip.house_rent == 12000.0
    assert slip.medical_allowance == 4000.0
    assert slip.conveyance_allowance == 2500.0
    assert slip.allowances_total == 18500.0
    assert slip.gross == 58500.0
    assert slip.annual_exemption == 218000.0
    assert slip.tax_withheld == 508.33
    assert slip.net == 53991.67


def test_payslip_general_slab_tax(odoo_env):
    # basic 60,000: employment income (60,000 - 6,000) x 12 = 648,000;
    # ITA 2023 Para 27 exemption min(216,000, 450,000) = 216,000 (due on a
    # basic-only salary too); taxable 432,000; (432,000 - 375,000) = 57,000
    # in the 10% band = 5,700 (> 5,000 minimum) -> 475.00 / month
    slip = _slip(odoo_env, _period(odoo_env), _employee(odoo_env, "Nasrin"), 60000.0)
    assert slip.annual_exemption == 216000.0
    assert slip.tax_withheld == 475.00
    assert slip.net == 53525.00  # 60,000 - 6,000 - 475


def test_payslip_category_and_investment_rebate(odoo_env):
    # employment income 648,000; Para 27 exemption 216,000 -> taxable 432,000
    # female/senior threshold 400,000: 432,000 - 400,000 = 32,000 @10% = 3,200
    # s.78 rebate = min(3% x 432,000 = 12,960; 15% x 100,000 = 15,000; 1M) = 12,960
    # 3,200 - 12,960 -> 0, but s.163 keeps the Dhaka minimum as a FLOOR on a
    # taxpayer inside the charge -> 5,000 / 12 = 416.67
    slip = _slip(
        odoo_env,
        _period(odoo_env),
        _employee(odoo_env, "Shirin"),
        60000.0,
        taxpayer_category="female_senior",
        investment_allowance=100000.0,
    )
    assert slip.tax_withheld == 416.67
    assert slip.net == 53583.33  # 60,000 - 6,000 - 416.67


def test_payslip_disabled_child_raises_threshold(odoo_env):
    # taxable 432,000 after the Para 27 exemption; threshold 375,000 + 50,000
    # = 425,000; (432,000 - 425,000) = 7,000 @10% = 700 -> lifted to the Dhaka
    # minimum 5,000 -> 416.67 / month
    slip = _slip(
        odoo_env,
        _period(odoo_env),
        _employee(odoo_env, "Babul"),
        60000.0,
        has_disabled_child=True,
    )
    assert slip.tax_withheld == 416.67
    assert slip.net == 53583.33


@pytest.mark.parametrize(
    ("location", "monthly_tax", "net"),
    [
        # employment income (30,000 - 3,000) x 12 = 324,000, less the Para 27
        # exemption min(108,000, 450,000) -> 216,000, plus 176,000 of
        # non-employment YTD income = 392,000 taxable; 17,000 over the
        # threshold @10% = 1,700 -> raised to the s.163 minimum for the area.
        # (The YTD figure is 176,000 rather than 76,000 so the payee is still
        # inside the charge once Para 27 is applied; below the threshold no
        # minimum tax is due at all and the floor would never be exercised.)
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
        annual_taxable_other=176000.0,
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
    assert slip.tax_withheld == 475.00


# ---------------------------------------------------------------------------
# Journey 13 — lock -> calculate -> approve -> pay (BEFTN) -> post
# ---------------------------------------------------------------------------


def _locked_attendance(env):
    lock = env["fix.attendance.lock"].create(
        {"name": "Jan 2026", "period_start": PERIOD_START, "period_end": PERIOD_END}
    )
    lock.action_lock()
    return lock


def _second_payroll_manager(env, company=None):
    """The checker: a Payroll Manager who did not calculate the run."""
    company = company or env.company
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Payroll Checker",
                "login": "payroll.checker.%s@example.test" % company.id,
                "company_id": company.id,
                "company_ids": [(6, 0, [company.id])],
                "group_ids": [(6, 0, [env.ref("cd_payroll_bd.group_payroll_manager").id])],
            }
        )
    )


def _releaser(env, company=None):
    """SOD-29: the Finance releaser, who neither calculated nor approved the run."""
    company = company or env.company
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Payroll Releaser",
                "login": "payroll.releaser.%s@example.test" % company.id,
                "company_id": company.id,
                "company_ids": [(6, 0, [company.id])],
                "group_ids": [(6, 0, [env.ref("cd_payroll_bd.group_payroll_release").id])],
            }
        )
    )


def _decide(env, record, approver):
    """`approver` approves `record` from the inbox task the engine routed to them."""
    task = env["fix.workflow.task"].search(
        [
            ("request_id", "=", record.approval_request_id.id),
            ("assigned_user_id", "=", approver.id),
            ("state", "=", "pending"),
        ]
    )
    assert task, "no inbox task for %s" % approver.name
    task.with_user(approver).action_approve()
    record.invalidate_recordset()


def _register_salary_account(env, emp, acc_number, routing):
    """HR registers the employee's salary account (a res.partner.bank record)
    and BEFTN routing code on the employee master - what calculate reads."""
    account = env["res.partner.bank"].create(
        {"acc_number": acc_number, "partner_id": emp.work_contact_id.id}
    )
    emp.write({"bank_account_ids": [(6, 0, [account.id])], "routing_number": routing})
    return account


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
    # M56-F12: PF is deducted only from members of the APPROVED register now
    # (an empty register pays no PF at all). The two are members at 10/10 -
    # the ruled case this test's figures were always computed under.
    for emp in (karim, nasrin):
        member = env["fix.pf.member"].create(
            {
                "employee_id": emp.id,
                "joined_fund_on": date(2020, 1, 1),
                "employee_rate": 10.0,
                "employer_rate": 10.0,
            }
        )
        member.action_approve()
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
    # M55 (D4): the 2h are payable only against an approved overtime request
    # (superuser fixture; M55 proves the routed approval itself)
    req = env["fix.overtime.request"].create(
        {
            "employee_id": karim.id,
            "company_id": karim.company_id.id,
            "date": date(2026, 1, 31),
            "hours": 2.0,
            "reason": "Month-end backlog approved before the work",
        }
    )
    req.write({"state": "submitted"})
    req.action_approve()
    _locked_attendance(env)
    checker = _second_payroll_manager(env, payroll_co.company)
    releaser = _releaser(env, payroll_co.company)

    # A run calculated BEFORE the employees' salary accounts are registered
    # carries no bank details: pre-validation refuses to route it for
    # approval, naming both (it used to be approved and fail only at the bank
    # file). The details are never typed onto the slips.
    unbanked = _period(env, name="2026-01-UNBANKED")
    unbanked.write({"company_account_no": COMPANY_ACCOUNT, "company_routing_no": COMPANY_ROUTING})
    unbanked.action_verify_attendance_locked()
    unbanked.action_calculate()
    with pytest.raises(UserError, match="fails pre-validation") as err, env.cr.savepoint():
        unbanked.action_request_approval()
    assert "Karim Uddin has no registered salary account" in str(err.value)
    assert "Nasrin Sultana has no registered salary account" in str(err.value)
    assert unbanked.state == "calculated" and unbanked.approval_state == "none"
    # the employee master feeds the next run: a registered bank account record
    # and the BEFTN routing number of each employee
    _register_salary_account(env, karim, "1501203345001", "060274689")
    _register_salary_account(env, nasrin, "2702150098761", "090261725")

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
    assert (slips[karim].ot_hours, slips[karim].overtime, slips[karim].net) == (
        2.0,
        576.92,
        27576.92,
    )
    assert slips[nasrin].net == 53525.00
    # totals: gross 30,576.92 + 60,000; tax 0 + 475; PF (3,000 + 6,000) x 2
    assert period.slip_count == 2
    assert period.gross_total == 90576.92
    assert period.tax_total == 475.00
    assert period.pf_total == 18000.00
    assert period.net_total == 81101.92

    # the slips carry the employee master's salary account and routing
    assert (slips[karim].bank_account_no, slips[karim].routing_no) == (
        "1501203345001",
        "060274689",
    )
    assert (slips[nasrin].bank_account_no, slips[nasrin].routing_no) == (
        "2702150098761",
        "090261725",
    )

    # No company originating account -> the run is not even routed for
    # approval (no assumed account).
    with pytest.raises(UserError, match="company originating account"), env.cr.savepoint():
        period.action_request_approval()
    period.write({"company_account_no": COMPANY_ACCOUNT, "company_routing_no": COMPANY_ROUTING})

    # Maker-checker: the run is routed to a Payroll Manager who did not
    # calculate it, and decided from that manager's inbox (the calculator is
    # never rewritten to get there)
    period.action_request_approval()
    assert period.approval_state == "pending"
    _decide(env, period, checker)
    assert period.state == "approved" and period.approval_state == "approved"
    assert (period.calculator_id, period.approved_by_id) == (env.user, checker)
    assert period.approved_net_total == 81101.92
    assert _events(env, "payroll.approved", period.id) == [{"period": "2026-01", "net": 81101.92}]

    # SOD-29: the approver does not release the file; the releaser does
    with pytest.raises(AccessError, match="Disbursement Releaser"), env.cr.savepoint():
        period.with_user(checker).action_pay()
    submitted = datetime(2026, 10, 1, 17, 0)  # Thursday after the 16:00 cut-off
    with (
        mock.patch.object(fix_payroll, "datetime", _fixed_now(submitted)),
        mock.patch(
            "libs.py.payroll_engine.beftn.datetime", _fixed_now(datetime(2026, 10, 1, 17, 5))
        ),
    ):
        period.with_user(releaser).action_pay()
    period.invalidate_recordset()
    assert period.released_by_id == releaser
    batch = period.beftn_batch_id
    assert period.state == "paid"
    # Fri 2 + Sat 3 are the weekend -> settles Sunday 4 October
    assert batch.settlement_date == date(2026, 10, 4)
    assert (batch.employee_count, batch.total_amount) == (2, 81101.92)
    assert (batch.company_account_no, batch.company_routing_no) == (
        COMPANY_ACCOUNT,
        COMPANY_ROUTING,
    )
    lines = batch.file_content.split("\r\n")
    assert [line[:1] for line in lines] == ["1", "5", "6", "6", "8", "9", ""]
    assert all(len(line) == 128 for line in lines[:-1])
    # 27,576.92 + 51,725.00 = 7,930,192 paisa in the batch and file controls
    assert lines[4][32:44] == "000008110192"
    assert lines[5][43:55] == "000008110192"
    # A09 round 2: the payload names the company and the amounts for M50
    assert _events(env, "payroll.beftn_submitted", period.id) == [
        {
            "period": "2026-01",
            "company_id": payroll_co.company.id,
            "batch_id": batch.id,
            "amount": 81101.92,
            "mfs_amount": 0.0,
            "settlement": "2026-10-04",
        }
    ]

    period.action_post()
    assert period.state == "posted"
    move = period.gl_move_id
    assert move.state == "posted"
    assert move.company_id == payroll_co.company
    assert move.journal_id == payroll_co.company.payroll_journal_id
    assert (move.ref, move.date) == ("Payroll GL Posting - 2026-01", PERIOD_END)
    # Dr basic 30,000 + 60,000; overtime 576.92; employer PF 3,000 + 6,000
    # Cr net 27,576.92 + 53,525; TDS 0 + 475; PF (3,000 + 6,000) x 2
    assert _move_lines(move) == [
        ("210100", "Net salary payable - 2026-01", 0.0, 81101.92),
        ("210200", "Income tax withheld (TDS) - 2026-01", 0.0, 475.0),
        ("210300", "Provident fund payable - 2026-01", 0.0, 18000.0),
        ("610100", "Basic salary - 2026-01", 90000.0, 0.0),
        ("610100", "Overtime - 2026-01", 576.92, 0.0),
        ("610200", "Employer PF contribution - 2026-01", 9000.0, 0.0),
    ]
    assert sum(move.line_ids.mapped("debit")) == sum(move.line_ids.mapped("credit")) == 99576.92
    # every line carries the company operating unit (AS-03 dimension)
    dimensions = env["fix.journal.dimension"].search([("move_line_id", "in", move.line_ids.ids)])
    assert len(dimensions) == 6
    assert dimensions.operating_unit_id.company_id == payroll_co.company
    # A09 round 2: plus the company, the entry and the per-unit split (M56-5)
    assert _events(env, "payroll.posted", period.id) == [
        {
            "period": "2026-01",
            "company_id": payroll_co.company.id,
            "move_id": move.id,
            "period_end": "2026-01-31",
            "gross": 90576.92,
            "net": 81101.92,
            "tax": 475.0,
            "pf": 18000.0,
            "total_debit": 99576.92,
            "total_credit": 99576.92,
            "by_operating_unit": [
                {
                    "operating_unit_id": False,
                    "branch_id": False,
                    "cost_centre": False,
                    "gross": 90576.92,
                    "tax": 475.0,
                    "net": 81101.92,
                }
            ],
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
    # a plain employee holds no payroll ACL at all (their own published slip
    # is served by fix.payslip.fix_my_payslips, never by an ACL)
    for model in ("fix.payroll.period", "fix.payslip", "fix.beftn.batch"):
        assert not env[model].with_user(clerk).has_access("read"), model
    # an officer prepares but cannot approve (nor create BEFTN batches)
    assert env["fix.payslip"].with_user(officer).has_access("write")
    assert not env["fix.beftn.batch"].with_user(officer).has_access("create")
    with pytest.raises(UserError, match="approver's inbox"), env.cr.savepoint():
        period.with_user(officer).action_approve()
    assert period.state == "calculated"
    assert env.ref("base.user_admin").has_group("cd_payroll_bd.group_payroll_manager")


def test_an_empty_run_is_never_approved(odoo_env):
    """It used to approve: a calculated period with no payslip and no
    calculator went to 'approved' (pre-validation, M56-14)."""
    period = _period(odoo_env, state="calculated")
    with pytest.raises(UserError, match="the run has no payslip"), odoo_env.cr.savepoint():
        period.action_approve()
    assert period.state == "calculated"


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
    # never assumed: the routing code comes from the employee master, and this
    # employee has none registered
    assert real.routing_no is False
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
    """A BEFTN batch over `period` as action_pay builds it: the period is
    approved first (a file is built only for an approved run whose slips
    still match the approval) and the batch carries the approved total."""
    if period and period.state != "approved":
        # fixture: the superuser plays an approved run (pinned digest and
        # total). The real approval refuses these slips at pre-validation;
        # the BEFTN checks below are the second line of defence and are
        # tested on their own.
        digest, total = period._payroll_snapshot()
        period.write({"state": "approved", "approved_digest": digest, "approved_net_total": total})
    base = {
        "period_id": period.id if period else False,
        "total_amount": period.approved_net_total if period else 0.0,
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


def test_settlement_waits_for_the_date_and_the_bank_confirmation(odoo_env):
    period = _period(odoo_env)
    future = _batch(odoo_env, period, settlement_date=date(2099, 1, 4))
    with pytest.raises(UserError, match="BEFTN settles 2099-01-04"), odoo_env.cr.savepoint():
        future.action_settle()
    assert future.state == "submitted"
    due = _batch(odoo_env, period, settlement_date=date(2026, 1, 4))
    # the date alone no longer settles a batch (A09 probe A10)
    with pytest.raises(UserError, match="bank's confirmation"), odoo_env.cr.savepoint():
        due.action_settle()
    due.write({"bank_confirmation_ref": "BB-RET-20260104-77"})
    with pytest.raises(UserError, match="bank's confirmation"), odoo_env.cr.savepoint():
        due.action_settle()
    due.write(
        {"bank_confirmation_file": "UkVUVVJOIEZJTEU=", "bank_confirmation_filename": "ret.txt"}
    )
    due.action_settle()
    assert due.state == "settled" and due.settled_by_id == odoo_env.user
    assert _events(odoo_env, "payroll.beftn_settled", due.id) == [{"settlement": "2026-01-04"}]
    # the confirmation is evidence once settled
    with pytest.raises(UserError, match="can no longer be changed"), odoo_env.cr.savepoint():
        due.with_user(_releaser(odoo_env)).write({"bank_confirmation_ref": "FORGED"})


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
        # BLA s.20(1)(a): ONE month's notice or wages in lieu (it paid the s.26
        # 120 days); s.20(2)(c): 30 days per completed year or gratuity if higher
        (0, 210000.0),  # 6 x 30 x 1,000 = 180,000 (= gratuity) + 30 days in lieu
        (10, 200000.0),  # 20 days in lieu
        (30, 180000.0),  # the full month served
        (120, 180000.0),  # more than a month served: nothing in lieu
    ],
)
def test_retrenchment_compensation_follows_s20(odoo_env, notice_days, expected):
    slip = _slip_with_contract(odoo_env, date(2019, 3, 15))
    assert slip.action_compute_retrenchment(date(2026, 3, 14), notice_days) == expected
    assert slip.notice_pay_amount == 1000.0 * max(30 - notice_days, 0)


def test_retrenchment_probe_m9_three_years(odoo_env):
    # A09 probe M9: 3 years at 30,000 paid 210,000 (120 days' notice);
    # s.20 gives 3 x 30 x 1,000 = 90,000 + one month 30,000 = 120,000
    slip = _slip_with_contract(odoo_env, date(2023, 3, 1))
    assert slip.action_compute_retrenchment(date(2026, 3, 1), 0) == 120000.0


def test_separation_and_retrenchment_need_a_contract(odoo_env):
    slip = _slip(odoo_env, _period(odoo_env), _employee(odoo_env, "No Contract"), 30000.0)
    with (
        pytest.raises(UserError, match="No active or terminated contract"),
        odoo_env.cr.savepoint(),
    ):
        slip.action_compute_separation(date(2026, 3, 14))
    with (
        pytest.raises(UserError, match="No active or terminated contract"),
        odoo_env.cr.savepoint(),
    ):
        slip.action_compute_retrenchment(date(2026, 3, 14))
    # the workspace button sends no date: without an exit or a left date
    # there is nothing to compute from, and it says so (probe M10 crashed)
    with pytest.raises(UserError, match="no separation date"), odoo_env.cr.savepoint():
        slip.action_compute_separation()


# --- WPPF (BLA 2006 Ch. XV) — A09 zero-trust re-audit 2026-10-30 ------------
# The S1 statutory allocation had no behavioural test: its only coverage was
# inspect.getsource(FixWppfAllocation._compute_wppf_split) + a substring check.


def test_wppf_year_end_run_splits_80_10_10_and_gates_on_the_challan(odoo_env):
    company = _bdt_company(odoo_env, name="WPPF Test Ltd", code="WPPT")
    env = _company_env(odoo_env, company)
    # A09 round 2 (M56-13): the beneficiaries are the company's employees
    # under an active contract, one line each; a typed head count is not used
    for n in range(4):
        _contract(env, _employee(env, "WPPF Worker %d" % n, company), 20000.0)
    alloc = env["fix.wppf.allocation"].create(
        {
            "company_id": company.id,
            "name": "WPPF 2025-2026",
            "fiscal_year": "2025-2026",
            "net_profit": 10_000_000.0,
            "eligible_workers_count": 100,
            "fiscal_year_end_date": date(2026, 6, 30),
            # the audited figure, with its evidence (no M19 audited record exists)
            "audited_statement_file": "JVBERi0xLjQK",
            "audit_report_ref": "AUDIT/FY26/01",
        }
    )
    alloc.action_calculate()
    assert alloc.state == "calculated"
    assert alloc.eligible_workers_count == 4 and len(alloc.beneficiary_ids) == 4
    # 5% of 10,000,000 = 500,000 pool
    assert alloc.total_wppf_pool == 500000.00
    # 80 : 10 : 10, the foundation taking the residual so the split is exact
    assert alloc.participatory_fund_amount == 400000.00
    assert alloc.welfare_fund_amount == 50000.00
    assert alloc.welfare_foundation_amount == 50000.00
    assert (
        alloc.participatory_fund_amount
        + alloc.welfare_fund_amount
        + alloc.welfare_foundation_amount
    ) == alloc.total_wppf_pool
    # s.242: two thirds distributed in cash, one third invested
    assert alloc.equal_distribution_pool == 266666.67
    assert alloc.investment_pool_share == 133333.33
    assert (
        alloc.equal_distribution_pool + alloc.investment_pool_share
    ) == alloc.participatory_fund_amount
    # equal per-worker share of the cash pool, over the 4 eligible workers
    assert alloc.per_worker_equal_share == 66666.67
    assert set(alloc.beneficiary_ids.mapped("share_amount")) == {66666.67}
    # s.234: transferred within nine months of the year end
    assert alloc.distribution_due_date == date(2026, 6, 30) + timedelta(days=270)

    # The signed trustee resolution (reference AND file) gates the request;
    # a Payroll Manager who did not prepare or calculate it decides it
    checker = _second_payroll_manager(env, company)
    with pytest.raises(UserError, match="Board of Trustees resolution"), env.cr.savepoint():
        alloc.action_request_approval()
    alloc.trustee_board_resolution_ref = "BOT/2026/11"
    with pytest.raises(UserError, match="Board of Trustees resolution"), env.cr.savepoint():
        alloc.action_request_approval()
    alloc.write({"trustee_resolution_file": "JVBERi0xLjQK", "trustee_resolution_filename": "r.pdf"})
    alloc.action_request_approval()
    _decide(env, alloc, checker)
    assert alloc.state == "approved"
    assert alloc.approved_by_id == checker

    # the BWWF 10% deposit challan gates posting, and posting makes an entry
    with pytest.raises(UserError, match="challan"), env.cr.savepoint():
        alloc.action_post()
    alloc.bwwf_challan_ref = "BWWF/CH/2026/0007"
    with pytest.raises(UserError, match="Configure the payroll accounting"), env.cr.savepoint():
        alloc.action_post()
    _configure_payroll_gl(env, company)
    company.write(
        {
            "payroll_wppf_expense_account_id": _account(
                env, company, "620900", "WPPF Expense", "expense"
            ).id,
            "payroll_wppf_payable_account_id": _account(
                env, company, "219900", "WPPF Payable", "liability_current"
            ).id,
        }
    )
    alloc.action_post()
    assert alloc.state == "posted"
    assert alloc.gl_move_id.state == "posted"
    assert _move_lines(alloc.gl_move_id) == [
        ("219900", "WPPF 5% pool 2025-2026", 0.0, 500000.0),
        ("620900", "WPPF 5% pool 2025-2026", 500000.0, 0.0),
    ]


def test_wppf_refuses_a_non_positive_net_profit(odoo_env):
    alloc = odoo_env["fix.wppf.allocation"].create(
        {"name": "WPPF loss year", "fiscal_year": "2025-2026", "net_profit": 0.0}
    )
    with pytest.raises(UserError, match="Net profit must be positive"):
        alloc.action_calculate()
