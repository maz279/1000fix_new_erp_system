# A09 M56 build (P0-b, P1, P2) - every control proved as the person it stops.
#
# The A09 workflow audit (2026-11-03) left these M56 gaps after P0-a:
#   C1   payroll, off-cycle, bonus and WPPF approval by whoever pressed the
#        button; the approver also released the bank file (SOD-29);
#   C2   tax category, tax location and disabled child read from contract
#        fields that do not exist; overtime paid to the ineligible; an
#        arbitrary one of two active contracts paid; the attendance gate not
#        re-checked at calculation;
#   M56-14 no pre-validation (negative net, BDT 1 basic, missing bank, ghost);
#   M56-4  a batch "settled" on the date alone;
#   M56-9  a festival bonus that computed nothing, three a year, 3x gross;
#   M56-10 certificates over every slip ever, returns filed with a typed 1 BDT;
#   M56-12 a separation that never reached a payment; retrenchment at s.26's
#          120 days instead of s.20's one month;
#   I1-I5  the hand-offs (exit settlement, leave balance, leaver, incentive,
#          injury compensation);
#   M56-8  an employee could not read their own payslip, and there was none.
#
# Every attack runs as a freshly created NON-admin user; the superuser only
# builds the fixture and, where labelled, plays a tampered database row.
# Live ORM, rolled back (`odoo_env`).
import itertools
from datetime import date, datetime
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo import Command
from odoo.addons.cd_p03_portal.controllers import a09 as a09ctl
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_payroll_bd.models.fix_payroll_statutory import (
    fiscal_year_bounds,
    separation_figures,
)
from odoo.exceptions import AccessError, UserError, ValidationError

pytestmark = [pytest.mark.financial]

PS, PE = date(2026, 1, 1), date(2026, 1, 31)
CO_ACC, CO_ROUTING = "2051234567", "175261726"
KARIM_ACC, KARIM_ROUTING = "1501203345001", "060274689"
NASRIN_ACC, NASRIN_ROUTING = "2702150098761", "090261725"
FILE = "JVBERi0xLjQKJcOkw7zDtsOfCg=="  # a stand-in scanned document (PDF header)
_SEQ = itertools.count(1)


class FakeRequest:
    def __init__(self, env):
        self.env = env


def p03(env, route, **kw):
    """Call a real /p03/model/* controller method as `env`'s user."""
    with mock.patch.object(api, "request", FakeRequest(env)):
        return getattr(api.P03GenericApiController(), route)(**kw)


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


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    bdt = env.ref("base.BDT")
    bdt.active = True
    n = next(_SEQ)
    co = env["res.company"].create({"name": "A09 M56 Build Co %d" % n, "currency_id": bdt.id})
    ou = env["operating.unit"].create(
        {
            "name": "M56 OU %d" % n,
            "code": "M56B%d" % n,
            "partner_id": co.partner_id.id,
            "company_id": co.id,
        }
    )
    journal = env["account.journal"].create(
        {"name": "Payroll", "code": "PR%d" % n, "type": "general", "company_id": co.id}
    )
    co.write(
        {
            "payroll_journal_id": journal.id,
            "payroll_salary_expense_account_id": _account(
                env, co, "6101", "Salaries", "expense"
            ).id,
            "payroll_pf_expense_account_id": _account(env, co, "6102", "Employer PF", "expense").id,
            "payroll_net_payable_account_id": _account(
                env, co, "2101", "Salaries Payable", "liability_current"
            ).id,
            "payroll_tax_payable_account_id": _account(
                env, co, "2102", "TDS Payable", "liability_current"
            ).id,
            "payroll_pf_payable_account_id": _account(
                env, co, "2103", "PF Payable", "liability_current"
            ).id,
            "payroll_beftn_account_no": CO_ACC,
            "payroll_beftn_routing_no": CO_ROUTING,
        }
    )
    cenv = env(context=dict(env.context, allowed_company_ids=[co.id]))

    def user(login, *groups):
        ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
        u = (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": "%s%d@a09m56.test" % (login, n),
                    "company_id": co.id,
                    "company_ids": [Command.set([co.id])],
                    "group_ids": [Command.set(ids)],
                }
            )
        )
        if "assigned_operating_unit_ids" in u._fields:
            u.assigned_operating_unit_ids = [Command.set([ou.id])]
        if "default_operating_unit_id" in u._fields:
            u.default_operating_unit_id = ou.id
        return u

    s = SimpleNamespace(env=cenv, co=co, ou=ou)
    s.plain = user("m56plain")
    s.officer = user("m56officer", "cd_payroll_bd.group_payroll_officer")
    s.manager = user(
        "m56manager", "cd_payroll_bd.group_payroll_manager", "account.group_account_manager"
    )
    s.manager2 = user(
        "m56manager2", "cd_payroll_bd.group_payroll_manager", "account.group_account_manager"
    )
    s.releaser = user(
        "m56releaser", "cd_payroll_bd.group_payroll_release", "account.group_account_manager"
    )

    def emp(name, basic, acc=None, routing=None, joining=date(2020, 1, 1), **master):
        """HR's fixture: the employee, an active contract and the salary
        account record and BEFTN routing on the master."""
        e = cenv["hr.employee"].create({"name": name, "company_id": co.id, **master})
        cenv["fix.employment.contract"].create(
            {
                "employee_id": e.id,
                "company_id": co.id,
                "contract_type": "permanent",
                "joining_date": joining,
                "basic_monthly": basic,
                "state": "active",
            }
        )
        if acc:
            bank = cenv["res.partner.bank"].create(
                {"acc_number": acc, "partner_id": e.work_contact_id.id}
            )
            e.write({"bank_account_ids": [Command.set([bank.id])], "routing_number": routing})
        return e

    s.emp = emp
    s.karim = emp("M56 Karim", 30000.0, KARIM_ACC, KARIM_ROUTING)
    s.nasrin = emp("M56 Nasrin", 60000.0, NASRIN_ACC, NASRIN_ROUTING)
    s.lock = cenv["fix.attendance.lock"].create(
        {"name": "Jan 2026", "period_start": PS, "period_end": PE}
    )
    s.lock.action_lock()
    s.as_ = lambda u: cenv(user=u.id)
    return s


def new_period(w, name="2026-01"):
    p = w.as_(w.officer)["fix.payroll.period"].create(
        {"name": name, "period_start": PS, "period_end": PE}
    )
    p.write({"company_account_no": CO_ACC, "company_routing_no": CO_ROUTING})
    return p


def calculated(w, name="2026-01"):
    p = new_period(w, name)
    p.action_verify_attendance_locked()
    p.action_calculate()
    return p


def routed_to(w, rec):
    return (
        w.env["fix.workflow.task"]
        .sudo()
        .search([("request_id", "=", rec.approval_request_id.id), ("state", "=", "pending")])
        .mapped("assigned_user_id")
    )


def task_of(w, rec, approver):
    task = (
        w.env["fix.workflow.task"]
        .sudo()
        .search(
            [
                ("request_id", "=", rec.approval_request_id.id),
                ("assigned_user_id", "=", approver.id),
                ("state", "=", "pending"),
            ]
        )
    )
    assert task, "no inbox task for %s" % approver.name
    return w.as_(approver)["fix.workflow.task"].browse(task.id)


def decide(w, rec, approver):
    task_of(w, rec, approver).action_approve()
    rec.invalidate_recordset()


def approved(w, name="2026-01"):
    p = calculated(w, name)
    p.action_request_approval()
    decide(w, p, w.manager)
    return p


def paid(w, name="2026-01"):
    p = approved(w, name)
    w.as_(w.releaser)["fix.payroll.period"].browse(p.id).action_pay()
    p.invalidate_recordset()
    return p


def slip_of(period, employee):
    return period.payslip_ids.filtered(lambda s: s.employee_id == employee)


# ================================================================ C1 routed approval


def test_period_approval_is_routed_and_never_direct(w):
    p = calculated(w)
    # direct approval refused for everyone, ORM and workspace alike
    for u in (w.officer, w.manager):
        with pytest.raises(UserError, match="approver's inbox"), w.env.cr.savepoint():
            w.as_(u)["fix.payroll.period"].browse(p.id).action_approve()
    res = p03(
        w.as_(w.manager),
        "model_action",
        model="fix.payroll.period",
        ids=[p.id],
        method="action_approve",
    )
    assert not res["success"] and "not available" in res["error"], res
    # the officer requests through the workspace; the request reaches the
    # Payroll Managers only, never the calculator
    res = p03(
        w.as_(w.officer),
        "model_action",
        model="fix.payroll.period",
        ids=[p.id],
        method="action_request_approval",
    )
    p.invalidate_recordset()
    assert res["success"] and p.approval_state == "pending", res
    assert routed_to(w, p) == w.manager | w.manager2
    # an officer cannot decide a manager's task
    task = task_of(w, p, w.manager)
    with pytest.raises(UserError, match="Only the assignee"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.workflow.task"].browse(task.id).action_approve()
    # while pending, the run is not re-opened or recalculated
    with pytest.raises(UserError, match="awaiting approval"), w.env.cr.savepoint():
        p.action_verify_attendance_locked()
    decide(w, p, w.manager2)
    assert (p.state, p.approval_state, p.approved_by_id) == ("approved", "approved", w.manager2)


def test_a_manager_who_calculated_is_never_routed_his_own_run(w):
    p = w.as_(w.manager)["fix.payroll.period"].create(
        {
            "name": "M",
            "period_start": PS,
            "period_end": PE,
            "company_account_no": CO_ACC,
            "company_routing_no": CO_ROUTING,
        }
    )
    p.action_verify_attendance_locked()
    p.action_calculate()
    p.action_request_approval()
    assert routed_to(w, p) == w.manager2
    # the only other manager away: nobody may approve -> refused, never skipped
    q = w.as_(w.manager2)["fix.payroll.period"].create(
        {
            "name": "Q",
            "period_start": PS,
            "period_end": PE,
            "company_account_no": CO_ACC,
            "company_routing_no": CO_ROUTING,
        }
    )
    q.action_verify_attendance_locked()
    q.action_calculate()
    w.manager.sudo().active = False
    with pytest.raises(UserError, match="No one can approve"), w.env.cr.savepoint():
        q.action_request_approval()


def test_rejection_returns_the_run_for_recalculation(w):
    p = calculated(w)
    p.action_request_approval()
    task = task_of(w, p, w.manager)
    with pytest.raises(UserError, match="State why"), w.env.cr.savepoint():
        task.action_reject()
    task.action_reject("OT for M56 Karim looks wrong")
    p.invalidate_recordset()
    assert (p.state, p.approval_state) == ("attendance_locked", "rejected")
    p.action_calculate()
    p.action_request_approval()
    assert p.approval_state == "pending"


# ================================================================ pre-validation (M56-14)


def test_prevalidation_blocks_missing_bank_zero_basic_and_the_minimum_wage(w):
    w.emp("M56 Unbanked", 25000.0)
    zero = w.emp("M56 Zero Basic", 1.0, "111222333444", "060274689")
    # M21 now refuses a contract with no basic; a legacy row from before that
    # constraint is played by SQL, and pre-validation is the second safeguard
    w.env.cr.execute(
        "UPDATE fix_employment_contract SET basic_monthly = 0 WHERE employee_id = %s", (zero.id,)
    )
    w.env.invalidate_all()
    p = calculated(w)
    with pytest.raises(UserError, match="fails pre-validation") as err, w.env.cr.savepoint():
        p.action_request_approval()
    msg = str(err.value)
    assert "M56 Unbanked has no registered salary account" in msg
    assert "M56 Zero Basic has a zero basic" in msg
    with pytest.raises(UserError, match="fails pre-validation"), w.env.cr.savepoint():
        p.action_prevalidate()
    # the minimum-wage floor is a company decision; once ruled it bites
    w.co.sudo().payroll_minimum_basic_monthly = 40000.0
    with pytest.raises(UserError) as err, w.env.cr.savepoint():
        p.action_request_approval()
    assert "M56 Karim's monthly basic 30000.00 is below the minimum 40000.00" in str(err.value)
    assert p.approval_state == "none"


def test_prevalidation_blocks_a_negative_net_and_a_ghost_slip(w):
    p = calculated(w)
    ghost = w.env["hr.employee"].create({"name": "M56 Ghost", "company_id": w.co.id})
    # tampered rows: the superuser plays the database writes the guards stop
    w.env["fix.payslip"].sudo().create(
        {
            "period_id": p.id,
            "employee_id": ghost.id,
            "company_id": w.co.id,
            "basic": 50000.0,
            "bank_account_no": "999",
            "routing_no": "060274689",
        }
    )
    slip_of(p, w.karim).sudo().write({"pf_employee_pct": 1000.0})
    with pytest.raises(UserError) as err, w.env.cr.savepoint():
        p.action_request_approval()
    msg = str(err.value)
    assert "M56 Ghost's payslip has no active or terminated contract" in msg
    assert "M56 Karim has a negative net pay" in msg


def test_a_clean_run_passes_prevalidation(w):
    p = calculated(w)
    assert p.action_prevalidate() == {"issues": []}


# ================================================================ C2 inputs, I3, gate


def test_tax_profile_comes_from_the_employee_master(w):
    fem = w.emp(
        "M56 Rural Female",
        60000.0,
        "3030303030",
        "060274689",
        taxpayer_category="female_senior",
        minimum_tax_location="non_city_corporation",
        has_disabled_child=True,
    )
    p = calculated(w)
    slip, gen = slip_of(p, fem), slip_of(p, w.nasrin)
    assert (slip.taxpayer_category, slip.minimum_tax_location, slip.has_disabled_child) == (
        "female_senior",
        "non_city_corporation",
        True,
    )
    # same pay as Nasrin (general / Dhaka); a higher threshold, less tax
    assert gen.taxpayer_category == "general" and slip.tax_withheld < gen.tax_withheld
    assert "tax=engine_fy2026_27" in slip.statutory_basis
    assert "separation=engine_2026_amendment" in slip.statutory_basis


def test_bank_details_come_from_the_master_and_a_conflict_pays_nobody(w):
    # the master's own account field is read when there is no account record
    plain_field = w.emp("M56 Field Account", 25000.0)
    plain_field.sudo().write({"bank_account_number": "8080808080", "routing_number": "060274689"})
    # two different registered accounts: no account is taken, the run says so
    w.karim.sudo().bank_account_number = "9191919191"
    p = calculated(w)
    assert (slip_of(p, plain_field).bank_account_no, slip_of(p, plain_field).routing_no) == (
        "8080808080",
        "060274689",
    )
    assert not slip_of(p, w.karim).bank_account_no
    assert "M56 Karim has two different registered accounts" in p.calculation_note
    with (
        pytest.raises(UserError, match="M56 Karim has no registered salary account"),
        w.env.cr.savepoint(),
    ):
        p.action_request_approval()


def test_completed_on_call_allowance_is_paid_and_listed(w):
    if "fix.hr.oncall" not in w.env:
        pytest.skip("cd_attendance on-call is not installed")
    OnCall = w.env["fix.hr.oncall"].sudo()
    done = OnCall.create(
        {
            "employee_id": w.karim.id,
            "company_id": w.co.id,
            "date_from": datetime(2026, 1, 9, 18, 0),
            "date_to": datetime(2026, 1, 10, 8, 0),
            "allowance": 1500.0,
        }
    )
    done.action_start()
    done.action_complete()
    if "approved_allowance" in OnCall._fields:
        # I9 (M55 round 2): payroll pays the APPROVED allowance; M55's approval
        # of the full 1,500 is played as a database write here
        w.env.cr.execute(
            "UPDATE fix_hr_oncall SET approved_allowance = 1500 WHERE id = %s", (done.id,)
        )
        w.env.invalidate_all()
    OnCall.create(  # planned, never worked: not paid
        {
            "employee_id": w.karim.id,
            "company_id": w.co.id,
            "date_from": datetime(2026, 1, 16, 18, 0),
            "date_to": datetime(2026, 1, 17, 8, 0),
            "allowance": 9999.0,
        }
    )
    p = calculated(w)
    slip = slip_of(p, w.karim)
    assert (slip.oncall_allowance, slip.other_allowance) == (1500.0, 1500.0)
    assert "M56 Karim on-call allowance 1500.00 (%s)" % done.name in p.calculation_note


def test_overtime_only_for_an_eligible_employee(w):
    # the January lock is re-taken around these rows (fixture)
    w.lock.sudo().write({"state": "draft"})
    for e in (w.karim, w.nasrin):
        w.env["fix.attendance.record"].sudo().create(
            {
                "employee_id": e.id,
                "company_id": w.co.id,
                "check_in": datetime(2026, 1, 12, 8, 0),
                "check_out": datetime(2026, 1, 12, 18, 0),
            }
        )
        # M55 (D4): payable overtime needs an approved request
        req = (
            w.env["fix.overtime.request"]
            .sudo()
            .create(
                {
                    "employee_id": e.id,
                    "company_id": w.co.id,
                    "date": date(2026, 1, 12),
                    "hours": 2.0,
                    "reason": "Approved before the work (fixture)",
                }
            )
        )
        req.write({"state": "submitted"})
        req.action_approve()
    # Karim's eligibility is withdrawn after his overtime was approved: payroll
    # itself still pays no overtime to an ineligible employee
    w.karim.sudo().overtime_eligible = False
    w.lock.sudo().action_lock()
    p = calculated(w)
    assert slip_of(p, w.karim).ot_hours == 0.0
    assert slip_of(p, w.nasrin).ot_hours == 2.0


def test_two_active_contracts_refuse_the_calculation(w):
    Contract = w.env["fix.employment.contract"].sudo()
    vals = {
        "employee_id": w.karim.id,
        "company_id": w.co.id,
        "contract_type": "permanent",
        "joining_date": date(2024, 1, 1),
        "basic_monthly": 90000.0,
    }
    # M21 refuses a second active contract outright
    with (
        pytest.raises(ValidationError, match="already has an active contract"),
        w.env.cr.savepoint(),
    ):
        Contract.create({**vals, "state": "active"})
    # a legacy pair from before that constraint is played by SQL: payroll's
    # own refusal is the second safeguard (A09 probe M4)
    second = Contract.create(vals)
    w.env.cr.execute(
        "UPDATE fix_employment_contract SET state = 'active' WHERE id = %s", (second.id,)
    )
    w.env.invalidate_all()
    p = new_period(w)
    p.action_verify_attendance_locked()
    with (
        pytest.raises(UserError, match="M56 Karim each hold more than one active"),
        w.env.cr.savepoint(),
    ):
        p.action_calculate()
    assert p.state == "attendance_locked" and not p.payslip_ids


def test_attendance_reopened_after_verification_stops_the_calculation(w):
    p = new_period(w)
    p.action_verify_attendance_locked()
    # A09 probe A8c. M55 now refuses to re-open a lock payroll has verified;
    # a lock re-opened anyway (an old row, a database write) is played by SQL:
    # payroll's own re-check at calculation is the second safeguard.
    w.env.cr.execute(
        "UPDATE fix_attendance_lock SET state = 'unlocked' WHERE id = %s", (w.lock.id,)
    )
    w.lock.invalidate_recordset()
    with pytest.raises(UserError, match="not LOCKED"), w.env.cr.savepoint():
        p.action_calculate()
    assert not p.payslip_ids


def test_another_companys_lock_does_not_open_the_gate(w):
    w.lock.sudo().action_unlock(reason="Late punches to correct before payroll")
    other = w.env["res.company"].create({"name": "M56 Other Lock Co"})
    lock = (
        w.env["fix.attendance.lock"]
        .sudo()
        .create({"name": "Other Jan", "period_start": PS, "period_end": PE, "company_id": other.id})
    )
    lock.action_lock()
    p = new_period(w)
    with pytest.raises(UserError, match="not LOCKED"), w.env.cr.savepoint():
        p.action_verify_attendance_locked()


def test_leavers_are_prorated_or_skipped_and_the_run_says_so(w):
    mid = w.emp("M56 Leaves 15 Jan", 31000.0, "4040404040", "060274689")
    mid.sudo().left_date = date(2026, 1, 15)
    gone = w.emp("M56 Left In December", 50000.0, "5050505050", "060274689")
    gone.sudo().left_date = date(2025, 12, 20)
    ended = w.emp("M56 Terminated", 45000.0, "6060606060", "060274689")
    ended_contract = (
        w.env["fix.employment.contract"].sudo().search([("employee_id", "=", ended.id)])
    )
    ended_contract.state = "terminated"
    p = calculated(w)
    slip = slip_of(p, mid)
    # 15 of 31 days: basic 31,000 x 15/31 = 15,000; the hourly rate is kept
    assert (slip.paid_days, slip.period_days, slip.basic) == (15, 31, 15000.0)
    assert not slip_of(p, gone) and not slip_of(p, ended)
    note = p.calculation_note
    assert "M56 Leaves 15 Jan paid 15 of 31 days" in note
    assert "Skipped M56 Left In December: left on 2025-12-20" in note
    assert "Skipped M56 Terminated: no active contract" in note


def test_the_ot_divisor_is_pinned_on_the_slip(w):
    p = approved(w)
    slip = slip_of(p, w.karim)
    net = slip.net
    w.co.sudo().ot_divisor_hours = 104.0  # an administrator's later change (probe M8)
    slip.sudo()._compute_slip()
    assert slip.net == net and slip.ot_divisor_hours == 208.0


# ================================================================ I4 incentive pickup


@pytest.fixture
def incentive(w):
    """M57's January incentive run, computed but not yet approved, with a
    line for Karim and one for Nasrin (one run per period and company, M57).

    The run's routed approval is M57's and is tested there; here it is played
    by SQL so the test isolates payroll's pickup (interface I4)."""
    env = w.env
    if "fix.incentive.line" not in env:
        pytest.skip("cd_performance is not installed")
    run = (
        env["fix.incentive.run"]
        .sudo()
        .create({"company_id": w.co.id, "period": "2026-01", "band_base": 10000.0})
    )

    def line(amount, employee):
        sc = (
            env["fix.performance.scorecard"]
            .sudo()
            .create({"company_id": w.co.id, "employee_id": employee.id, "period": "2026-01"})
        )
        return (
            env["fix.incentive.line"]
            .sudo()
            .create(
                {
                    "company_id": w.co.id,
                    "run_id": run.id,
                    "scorecard_id": sc.id,
                    "employee_id": employee.id,
                    "amount": amount,
                }
            )
        )

    def set_state(state):
        env.cr.execute("UPDATE fix_incentive_run SET state = %s WHERE id = %s", (state, run.id))
        run.invalidate_recordset()

    karim, nasrin = line(1600.0, w.karim), line(250000.0, w.nasrin)
    set_state("computed")
    return SimpleNamespace(run=run, karim=karim, nasrin=nasrin, set_state=set_state)


def test_only_approved_incentive_lines_reach_the_payslip_once(w, incentive):
    # a computed, unapproved run pays nothing
    p = calculated(w)
    assert slip_of(p, w.karim).incentive == 0.0 and slip_of(p, w.nasrin).incentive == 0.0
    assert not incentive.karim.payslip_ref_id
    # once approved, recalculating the run picks its lines up
    incentive.set_state("approved")
    p.action_request_approval()
    task_of(w, p, w.manager).action_reject("recalculate")
    p.action_calculate()
    karim = slip_of(p, w.karim)
    assert karim.incentive == 1600.0 and slip_of(p, w.nasrin).incentive == 250000.0
    incentive.karim.invalidate_recordset()
    assert incentive.karim.payslip_ref_id == karim.id
    # a second run of the same month does not pay it again
    other = calculated(w, "2026-01-B")
    assert slip_of(other, w.karim).incentive == 0.0
    # recalculating its own run picks it up again onto the new slip (M57's
    # real hook accepts re-attaching a line whose old slip was deleted)
    p.action_request_approval()
    task_of(w, p, w.manager).action_reject("recalculate")
    p.action_calculate()
    incentive.karim.invalidate_recordset()
    assert slip_of(p, w.karim).incentive == 1600.0
    assert incentive.karim.payslip_ref_id == slip_of(p, w.karim).id


# ================================================================ release SoD and settlement (M56-4)


def test_the_approver_and_the_officer_cannot_release_the_bank_file(w):
    p = approved(w)
    for u in (w.officer, w.manager, w.manager2):
        with pytest.raises(AccessError, match="Disbursement Releaser"), w.env.cr.savepoint():
            w.as_(u)["fix.payroll.period"].browse(p.id).action_pay()
    # even holding the release role, the approver may not release
    w.manager.sudo().group_ids = [Command.link(w.env.ref("cd_payroll_bd.group_payroll_release").id)]
    with pytest.raises(UserError, match="Release SoD violation"), w.env.cr.savepoint():
        w.as_(w.manager)["fix.payroll.period"].browse(p.id).action_pay()
    w.as_(w.releaser)["fix.payroll.period"].browse(p.id).action_pay()
    p.invalidate_recordset()
    assert p.state == "paid" and p.released_by_id == w.releaser
    assert p.beftn_batch_id.released_by_id == w.releaser and p.beftn_batch_id.file_digest
    # the release stamp is not typed
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        p.write({"released_by_id": w.officer.id})


def test_a_batch_settles_only_on_the_banks_confirmation(w):
    p = paid(w)
    batch = w.as_(w.releaser)["fix.beftn.batch"].browse(p.beftn_batch_id.id)
    batch.sudo()._guarded().write({"settlement_date": date(2026, 1, 4)})  # fixture: a due batch
    with pytest.raises(AccessError, match="Disbursement Releaser"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.beftn.batch"].browse(batch.id).action_settle()
    with pytest.raises(UserError, match="bank's confirmation"), w.env.cr.savepoint():
        batch.action_settle()
    batch.write({"bank_confirmation_ref": "BB-CONF-1", "bank_confirmation_file": FILE})
    batch.action_settle()
    assert batch.state == "settled" and batch.settled_by_id == w.releaser
    with pytest.raises(UserError, match="can no longer be changed"), w.env.cr.savepoint():
        batch.write({"bank_confirmation_ref": "FORGED"})


# ================================================================ payslip publication (M56-8)


def test_an_employee_reads_only_their_own_published_payslip(w):
    w.karim.sudo().user_id = w.plain.id
    p = paid(w)
    mine, colleague = slip_of(p, w.karim), slip_of(p, w.nasrin)
    me = w.as_(w.plain)
    # a plain employee holds no payslip ACL: no ORM or workspace list at all
    w.env.invalidate_all()
    with pytest.raises(AccessError), w.env.cr.savepoint():
        me["fix.payslip"].search([])
    res = p03(me, "model_records", model="fix.payslip", cols=["employee_id", "net"])
    assert "error" in res and not res.get("rows"), res
    # self-service shows nothing before publication
    assert me["fix.payslip"].fix_my_payslips() == []
    with pytest.raises(AccessError), w.env.cr.savepoint():
        me["fix.payroll.period"].browse(p.id).action_publish_payslips()
    w.as_(w.officer)["fix.payroll.period"].browse(p.id).action_publish_payslips()
    mine.invalidate_recordset()
    assert mine.published and mine.published_digest == mine._content_digest()
    rows = me["fix.payslip"].fix_my_payslips()
    assert [r["id"] for r in rows] == [mine.id] and rows[0]["net"] == mine.net
    # the same through the workspace's self-service report
    res = p03(me, "model_report", module="M56", report="my_payslips")
    assert [r["id"] for r in res["rows"]] == [mine.id], res
    # the Bengali payslip prints for the employee's own slip, never another's
    html = me["fix.payslip"].fix_my_payslip_html(mine.id)
    assert "বেতন বিবরণী" in html and "M56 Karim" in html and KARIM_ACC in html
    with pytest.raises(AccessError, match="only your own"), w.env.cr.savepoint():
        me["fix.payslip"].fix_my_payslip_html(colleague.id)
    # payroll still reads every slip; publication stamps are not typed
    # (a paid run's slip takes no write at all)
    assert w.as_(w.releaser)["fix.payslip"].search([("period_id", "=", p.id)]) == p.payslip_ids
    with pytest.raises(UserError, match="frozen"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.payslip"].browse(colleague.id).write({"published": True})


def test_a_payslip_acl_holder_outside_payroll_reads_only_their_own(w):
    """The global rule backs the self-service window: should any role ever
    be given a payslip read ACL, it still reads only its own published slip."""
    reader = w.env["res.groups"].create(
        {
            "name": "M56 test payslip reader",
            "implied_ids": [Command.link(w.env.ref("base.group_user").id)],
        }
    )
    w.env["ir.model.access"].create(
        {
            "name": "m56 test reader",
            "model_id": w.env.ref("cd_payroll_bd.model_fix_payslip").id,
            "group_id": reader.id,
            "perm_read": True,
        }
    )
    w.plain.sudo().group_ids = [Command.link(reader.id)]
    w.karim.sudo().user_id = w.plain.id
    p = paid(w)
    w.as_(w.officer)["fix.payroll.period"].browse(p.id).action_publish_payslips()
    w.env.invalidate_all()
    assert w.as_(w.plain)["fix.payslip"].search([]) == w.as_(w.plain)["fix.payslip"].browse(
        slip_of(p, w.karim).id
    )


def test_payslips_are_published_only_after_payment(w):
    p = approved(w)
    with pytest.raises(UserError, match="published once the run is paid"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.payroll.period"].browse(p.id).action_publish_payslips()


# ================================================================ off-cycle (M56-7, I5)


def test_offcycle_routed_pinned_released_and_posted(w):
    oc = w.as_(w.officer)["fix.payroll.offcycle"].create(
        {"employee_id": w.karim.id, "payment_type": "arrear", "amount": 12000.0}
    )
    oc.action_request_approval()
    assert (oc.bank_account_no, oc.routing_no) == (KARIM_ACC, KARIM_ROUTING)
    assert routed_to(w, oc) == w.manager | w.manager2
    decide(w, oc, w.manager)
    assert oc.state == "approved" and oc.approved_digest
    with pytest.raises(AccessError, match="Disbursement Releaser"), w.env.cr.savepoint():
        w.as_(w.manager)["fix.payroll.offcycle"].browse(oc.id).action_pay()
    rel = w.as_(w.releaser)["fix.payroll.offcycle"].browse(oc.id)
    rel.action_pay()
    batch = rel.beftn_batch_id
    assert rel.state == "paid" and batch.total_amount == 12000.0
    assert KARIM_ACC in batch.file_content and "0001200000" in batch.file_content
    rel.action_post()
    lines = sorted((ln.account_id.code, ln.debit, ln.credit) for ln in rel.gl_move_id.line_ids)
    assert rel.state == "posted" and lines == [("2101", 0.0, 12000.0), ("6101", 12000.0, 0.0)]


def test_offcycle_payee_bank_change_after_request_voids_nothing_silently(w):
    oc = w.as_(w.officer)["fix.payroll.offcycle"].create(
        {"employee_id": w.karim.id, "payment_type": "adjustment", "amount": 5000.0}
    )
    oc.action_request_approval()
    # HR changes the payee's routing while the request is pending
    w.karim.sudo().routing_number = "090261725"
    with pytest.raises(UserError, match="bank details changed"), w.env.cr.savepoint():
        decide(w, oc, w.manager)
    assert oc.state == "draft"


def test_offcycle_for_an_approvers_own_salary_never_reaches_him(w):
    w.karim.sudo().user_id = w.manager2.id
    oc = w.as_(w.officer)["fix.payroll.offcycle"].create(
        {"employee_id": w.karim.id, "payment_type": "advance", "amount": 900_000.0}
    )
    oc.action_request_approval()
    assert routed_to(w, oc) == w.manager


def test_offcycle_without_a_registered_account_is_not_requested(w):
    e = w.emp("M56 No Bank", 20000.0)
    oc = w.as_(w.officer)["fix.payroll.offcycle"].create(
        {"employee_id": e.id, "payment_type": "arrear", "amount": 100.0}
    )
    with pytest.raises(UserError, match="never sent to an assumed account"), w.env.cr.savepoint():
        oc.action_request_approval()
    with pytest.raises(ValidationError), w.env.cr.savepoint():
        oc.write({"amount": -5.0})


def test_injury_compensation_arrives_as_a_draft_offcycle_once(w):
    Offcycle = w.env["fix.payroll.offcycle"]
    event = {
        "event_id": "evt-m59-comp-%d" % w.karim.id,
        "event_type": "hse.compensation.awarded",
        "payload": {
            "employee_id": w.karim.id,
            "amount": 250000.0,
            "incident_id": 4242,
            "reason": "BLA s.151 permanent partial disablement",
        },
    }
    oc = Offcycle.sudo().consume_compensation_awarded(event)
    again = Offcycle.sudo().consume_compensation_awarded(event)
    assert again == oc and oc.state == "draft" and oc.payment_type == "compensation"
    assert (oc.amount, oc.hse_incident_ref, oc.company_id) == (250000.0, 4242, w.co)
    # the officer cannot retype the awarded amount or payee
    mine = w.as_(w.officer)["fix.payroll.offcycle"].browse(oc.id)
    with pytest.raises(UserError, match="can no longer be changed"), w.env.cr.savepoint():
        mine.write({"amount": 1.0})
    with pytest.raises(UserError, match="can no longer be changed"), w.env.cr.savepoint():
        mine.write({"employee_id": w.nasrin.id})
    # and it goes through the routed approval like any other payment
    mine.action_request_approval()
    assert mine.approval_state == "pending"
    with pytest.raises(UserError, match="no positive amount"), w.env.cr.savepoint():
        Offcycle.sudo().consume_compensation_awarded(
            {"event_id": "evt-zero", "payload": {"employee_id": w.karim.id, "amount": 0}}
        )


def test_the_relay_delivers_hse_compensation_awarded(w):
    from libs.py.fix_events import publish

    publish(
        w.env,
        "hse.compensation.awarded",
        "fix.hse.incident",
        777,
        {"employee_id": w.nasrin.id, "amount": 1234.0, "incident_id": 777, "reason": "test"},
    )
    w.env["fix.event.outbox"].sudo().cron_relay()
    oc = w.env["fix.payroll.offcycle"].sudo().search([("hse_incident_ref", "=", 777)])
    assert len(oc) == 1 and oc.amount == 1234.0 and oc.employee_id == w.nasrin


def test_a_recognition_prize_arrives_as_a_draft_offcycle_once(w):
    """M57 publishes recognition.awarded once a prize is approved; the prize
    is salary income, so payroll pays (and withholds) it as a routed off-cycle
    payment whose amount and payee are the award's."""
    Offcycle = w.env["fix.payroll.offcycle"]
    event = {
        "event_id": "evt-m57-prize-%d" % w.karim.id,
        "event_type": "recognition.awarded",
        "payload": {
            "employee_id": w.karim.id,
            "amount": 5000.0,
            "recognition_id": 9191,
            "reason": "Technician of the quarter",
        },
    }
    oc = Offcycle.sudo().consume_recognition_awarded(event)
    again = Offcycle.sudo().consume_recognition_awarded(dict(event, event_id="evt-redelivered"))
    assert again == oc and oc.state == "draft" and oc.payment_type == "recognition"
    assert (oc.amount, oc.recognition_ref, oc.company_id) == (5000.0, 9191, w.co)
    mine = w.as_(w.officer)["fix.payroll.offcycle"].browse(oc.id)
    with pytest.raises(UserError, match="can no longer be changed"), w.env.cr.savepoint():
        mine.write({"amount": 50000.0})
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        mine.write({"recognition_ref": 1})
    mine.action_request_approval()
    assert mine.approval_state == "pending"
    # an award without a prize pays nothing
    assert not Offcycle.sudo().consume_recognition_awarded(
        {"event_id": "evt-no-prize", "payload": {"employee_id": w.karim.id, "amount": 0}}
    )


def test_the_relay_delivers_recognition_awarded(w):
    from libs.py.fix_events import publish

    publish(
        w.env,
        "recognition.awarded",
        "fix.performance.recognition",
        888,
        {"employee_id": w.nasrin.id, "amount": 777.0, "recognition_id": 888, "reason": "test"},
    )
    w.env["fix.event.outbox"].sudo().cron_relay()
    oc = w.env["fix.payroll.offcycle"].sudo().search([("recognition_ref", "=", 888)])
    assert len(oc) == 1 and oc.amount == 777.0 and oc.employee_id == w.nasrin


# ================================================================ festival bonus (M56-9)


def test_bonus_is_computed_capped_at_basic_and_needs_a_year_of_service(w):
    newbie = w.emp("M56 New Joiner", 20000.0, "7070707070", "060274689", joining=date(2025, 9, 1))
    run = w.as_(w.officer)["fix.payroll.bonus.run"].create(
        {
            "festival": "eid_ul_fitr",
            "basis": "gross",
            "multiplier": 3.0,
            "bonus_date": date(2026, 3, 20),
        }
    )
    run.action_compute()
    by_emp = {line.employee_id: line for line in run.line_ids}
    assert newbie not in by_emp and "M56 New Joiner: less than one year" in run.computation_note
    # 3x gross asked for; r.111(5) caps a festival bonus at one month's basic
    assert (by_emp[w.karim].amount, by_emp[w.karim].capped) == (30000.0, True)
    assert run.total_amount == 90000.0 and run.employee_count == 2
    # lines are written by the compute step only
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.payroll.bonus.line"].browse(by_emp[w.karim].id).write({"amount": 1.0})
    with pytest.raises(UserError, match="removed only by recomputing"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.payroll.bonus.line"].browse(by_emp[w.karim].id).unlink()
    run.action_request_approval()
    decide(w, run, w.manager)
    rel = w.as_(w.releaser)["fix.payroll.bonus.run"].browse(run.id)
    rel.action_pay()
    assert rel.state == "paid" and rel.beftn_batch_id.total_amount == 90000.0
    assert NASRIN_ACC in rel.beftn_batch_id.file_content
    rel.action_post()
    assert rel.state == "posted" and rel.gl_move_id.state == "posted"


def test_at_most_two_festival_bonuses_a_year(w):
    Run = w.as_(w.officer)["fix.payroll.bonus.run"]
    Run.create({"festival": "eid_ul_fitr", "bonus_date": date(2026, 3, 20)})
    second = Run.create({"festival": "eid_ul_adha", "bonus_date": date(2026, 5, 27)})
    with pytest.raises(ValidationError, match="two festival bonuses a year"), w.env.cr.savepoint():
        Run.create({"festival": "durga_puja", "bonus_date": date(2026, 10, 1)})
    # nor by re-dating a later year's run into this one
    later = Run.create({"festival": "durga_puja", "bonus_date": date(2027, 10, 1)})
    with pytest.raises(ValidationError, match="two festival bonuses a year"), w.env.cr.savepoint():
        later.write({"bonus_date": date(2026, 10, 1)})
    # a cancelled run frees its place
    second.action_cancel()
    Run.create({"festival": "durga_puja", "bonus_date": date(2026, 10, 1)})


def test_bonus_approval_is_routed_and_not_to_its_computer(w):
    run = w.as_(w.manager)["fix.payroll.bonus.run"].create({"festival": "durga_puja"})
    run.action_compute()
    with pytest.raises(UserError, match="approver's inbox"), w.env.cr.savepoint():
        run.action_approve()
    run.action_request_approval()
    assert routed_to(w, run) == w.manager2
    with pytest.raises(UserError, match="awaiting approval"), w.env.cr.savepoint():
        run.action_compute()


# ================================================================ WPPF


def test_wppf_needs_the_signed_resolution_and_a_routed_decision(w):
    a = w.as_(w.officer)["fix.wppf.allocation"].create(
        {
            "fiscal_year": "2025-2026",
            "net_profit": 10_000_000.0,
            "audited_statement_file": FILE,
            "audit_report_ref": "AUD-FY26-1",
            "trustee_board_resolution_ref": "typed-by-officer",
        }
    )
    a.action_calculate()
    with (
        pytest.raises(UserError, match="signed Board of Trustees resolution"),
        w.env.cr.savepoint(),
    ):
        a.action_request_approval()
    a.write({"trustee_resolution_file": FILE})
    a.action_request_approval()
    assert routed_to(w, a) == w.manager | w.manager2
    decide(w, a, w.manager)
    assert a.state == "approved" and a.approved_by_id == w.manager
    with pytest.raises(UserError, match="can no longer be changed"), w.env.cr.savepoint():
        a.write({"trustee_resolution_file": False})


# ================================================================ certificate and return (M56-10)


def test_certificate_counts_the_fiscal_years_paid_slips_only(w):
    paid(w)  # January 2026: fiscal year 2025-26
    calculated(w, "2026-01-unpaid")  # calculated, never paid: not certified
    C = w.as_(w.officer)["fix.payroll.certificate"]
    cert = C.create(
        {"employee_id": w.nasrin.id, "certificate_type": "tax", "fiscal_year": "2025-26"}
    )
    cert.action_issue()
    paid_slip = w.env["fix.payslip"].search(
        [("employee_id", "=", w.nasrin.id), ("period_id.state", "=", "paid")]
    )
    assert cert.slip_count == 1 and cert.total_gross == paid_slip.gross
    assert cert.issued_by_id == w.officer
    nxt = C.create(
        {"employee_id": w.nasrin.id, "certificate_type": "tax", "fiscal_year": "2026-27"}
    )
    with pytest.raises(UserError, match="covers no paid payslip"), w.env.cr.savepoint():
        nxt.action_issue()
    with pytest.raises(UserError, match="not a Bangladesh fiscal year"), w.env.cr.savepoint():
        C.create({"employee_id": w.nasrin.id, "fiscal_year": "last year"})
    assert fiscal_year_bounds("2025-2026") == (date(2025, 7, 1), date(2026, 6, 30))


def test_a_return_is_filed_by_a_manager_with_challan_and_acknowledgement(w):
    paid(w)
    r = w.as_(w.officer)["fix.payroll.return"].create(
        {"period": "Q3-2025-26", "period_start": PS, "period_end": date(2026, 3, 31)}
    )
    assert r.due_date == date(2026, 4, 25)
    r.action_reconcile_payslips()
    with pytest.raises(AccessError, match="Payroll Manager"), w.env.cr.savepoint():
        r.action_file()
    mr = w.as_(w.manager)["fix.payroll.return"].browse(r.id)
    with (
        pytest.raises(
            UserError, match="treasury challan number, challan date, NBR acknowledgement"
        ),
        w.env.cr.savepoint(),
    ):
        mr.action_file()
    r.write(
        {
            "challan_number": "TC-1",
            "challan_date": date(2026, 4, 20),
            "acknowledgement": "NBR-ACK-9",
        }
    )
    mr.action_file()
    assert mr.state == "filed" and mr.filed_by_id == w.manager
    assert mr.total_tax == sum(
        w.env["fix.payslip"]
        .search([("company_id", "=", w.co.id), ("period_id.state", "=", "paid")])
        .mapped("tax_withheld")
    )


def test_the_return_reminder_cron_is_idempotent(w):
    r = w.as_(w.officer)["fix.payroll.return"].create(
        {"period": "Q-due", "period_start": PS, "period_end": date(2026, 10, 31)}
    )
    Return = w.env["fix.payroll.return"]
    with mock.patch("odoo.fields.Date.context_today", return_value=date(2026, 11, 20)):
        Return.cron_return_due_alerts()
        Return.cron_return_due_alerts()
    r.invalidate_recordset()
    reminders = r.activity_ids.filtered(lambda a: "7-day reminder" in (a.summary or ""))
    assert len(reminders) == 1 and r.due_date == date(2026, 11, 25)


# ================================================================ I1 settlement, separation (M56-12)


def _exit(w, employee, exit_type, last_day, notice=None):
    return (
        w.env["fix.hr.exit"]
        .sudo()
        .create(
            {
                "employee_id": employee.id,
                "company_id": w.co.id,
                "exit_type": exit_type,
                "last_working_day": last_day,
                "notice_date": notice,
            }
        )
    )


def test_settlement_breakdown_is_computed_never_typed(w):
    ex = _exit(w, w.karim, "resignation", date(2026, 1, 31))
    out = ex._fix_settlement_breakdown()
    unused = w.karim.sudo()._fix_unused_annual_leave_days(as_of=date(2026, 1, 31))
    labels = dict(out["lines"])
    # 6 completed years at 1,000 a day: resignation 6 x 15 = 90,000 < gratuity
    # 6 x 30 = 180,000 -> "or gratuity, whichever is higher" (s.27(4))
    assert (
        labels["Gratuity (higher than Resignation compensation (BLA s.27, engine bands))"]
        == 180000.0
    )
    assert out["net"] == round(180000.0 + 1000.0 * unused, 2)
    assert (
        "separation=engine_2026_amendment" in out["basis"] and "completed_years=6" in out["basis"]
    )
    term = _exit(w, w.nasrin, "termination", date(2026, 1, 31), notice=date(2026, 1, 1))
    lines = dict(term._fix_settlement_breakdown()["lines"])
    # s.26: 120 days less the 30 served = 90 days x 2,000
    assert lines["Notice pay in lieu (BLA s.26, 120 days)"] == 180000.0


def test_retrenchment_pays_s20_one_month_not_120_days():
    # A09 probe M9: 3 years at 30,000 -> 210,000 before; s.20 -> 120,000
    years, lines = separation_figures(30000.0, date(2023, 3, 1), date(2026, 3, 1), "retrenchment")
    by = {key: amount for key, _label, amount in lines}
    assert years == 3 and by == {"notice_pay": 30000, "service_compensation": 90000}
    _y, abandon = separation_figures(30000.0, date(2023, 3, 1), date(2026, 3, 1), "abandonment")
    assert abandon == []  # no compensation until labour counsel rules (report §7.4)


def test_a_settled_exit_becomes_a_pinned_draft_offcycle_payment(w):
    ex = _exit(w, w.karim, "retirement", date(2026, 1, 31))
    with pytest.raises(UserError, match="only a settled exit is paid"), w.env.cr.savepoint():
        ex.with_user(w.officer).action_create_settlement_payment()
    net = ex._fix_settlement_breakdown()["net"]
    ex.sudo().write({"state": "settled", "settlement_amount": 9_999_999.0})  # a typed figure
    with pytest.raises(UserError, match="no longer matches its computation"), w.env.cr.savepoint():
        ex.with_user(w.officer).action_create_settlement_payment()
    ex.sudo().write({"settlement_amount": net})
    with pytest.raises(AccessError, match="Only HR or payroll"), w.env.cr.savepoint():
        ex.with_user(w.plain).action_create_settlement_payment()
    ids = ex.with_user(w.officer).action_create_settlement_payment()["offcycle_ids"]
    oc = w.as_(w.officer)["fix.payroll.offcycle"].browse(ids)
    assert (oc.state, oc.amount, oc.exit_id, oc.prepared_by_id) == ("draft", net, ex, w.officer)
    with pytest.raises(UserError, match="can no longer be changed"), w.env.cr.savepoint():
        oc.write({"amount": net + 1})
    with pytest.raises(UserError, match="already has settlement payment"), w.env.cr.savepoint():
        ex.with_user(w.officer).action_create_settlement_payment()
    oc.action_request_approval()
    assert w.officer not in routed_to(w, oc)


def test_compute_separation_from_the_workspace_takes_the_exit_date(w):
    p = calculated(w)
    slip = slip_of(p, w.karim)
    _exit(w, w.karim, "resignation", date(2026, 1, 31))
    res = p03(
        w.as_(w.officer),
        "model_action",
        model="fix.payslip",
        ids=[slip.id],
        method="action_compute_separation",
    )
    assert res["success"], res
    slip.invalidate_recordset()
    assert (slip.completed_years, slip.gratuity_amount) == (6, 180000.0)
    assert slip.unused_leave_days == w.karim.sudo()._fix_unused_annual_leave_days(
        as_of=date(2026, 1, 31)
    )


# ================================================================ structure (M56-16)


def test_only_a_payroll_manager_changes_a_salary_structure(w):
    s = w.as_(w.manager)["fix.payroll.structure"].create({"name": "Grade T2", "grade": "T2"})
    with pytest.raises(AccessError), w.env.cr.savepoint():
        w.as_(w.officer)["fix.payroll.structure"].browse(s.id).write({"basic_pct": 90.0})
    s.write({"basic_pct": 55.0})
    w.env.cr.precommit.run()  # tracking is written when the request commits
    assert s.sudo().message_ids.filtered(lambda m: m.tracking_value_ids)


# ================================================================ deployment


def test_deployment_cron_consumer_groups_acl_and_surfaces(odoo_env):
    env = odoo_env
    cron = env.ref("cd_payroll_bd.ir_cron_payroll_return_due_alerts")
    assert cron.active and cron.code == "model.cron_return_due_alerts()"
    consumer = env.ref("cd_payroll_bd.consumer_hse_compensation_awarded_offcycle")
    assert consumer.active and consumer.event_type == "hse.compensation.awarded"
    assert consumer.model == "fix.payroll.offcycle"
    prize = env.ref("cd_payroll_bd.consumer_recognition_awarded_offcycle")
    assert prize.active and prize.event_type == "recognition.awarded"
    assert (prize.model, prize.method) == ("fix.payroll.offcycle", "consume_recognition_awarded")
    releaser = env.ref("cd_payroll_bd.group_payroll_release")
    assert releaser.user_ids <= env.ref("base.user_root") | env.ref("base.user_admin")
    for xmlid in (
        "cd_payroll_bd.access_fix_bonus_line_officer",
        "cd_payroll_bd.access_fix_payroll_period_release",
        "cd_payroll_bd.access_fix_beftn_batch_release",
        "cd_payroll_bd.access_fix_offcycle_release",
        "cd_payroll_bd.access_fix_bonus_run_release",
        "cd_payroll_bd.access_fix_payroll_structure_manager",
        "cd_payroll_bd.rule_fix_payslip_own_published",
    ):
        assert env.ref(xmlid)
    assert env.ref("cd_payroll_bd.report_payslip_bn")
    actions = {m: a09ctl.SURFACES[m]["actions"] for m in a09ctl.SURFACES}
    assert {"action_request_approval", "action_prevalidate", "action_publish_payslips"} <= actions[
        "fix.payroll.period"
    ]
    for model in (
        "fix.payroll.period",
        "fix.payroll.offcycle",
        "fix.payroll.bonus.run",
        "fix.wppf.allocation",
    ):
        assert "action_approve" not in actions[model], model
        assert "action_request_approval" in actions[model], model
    assert actions["fix.beftn.batch"] == {"action_settle"}


def test_wppf_posts_only_to_configured_accounts(w):
    """M56-W3 (A09 probe): posting fails closed until finance configures the
    WPPF accounts, then posts the 5% allocation Dr expense / Cr payable."""
    env = w.env
    a = w.as_(w.officer)["fix.wppf.allocation"].create(
        {
            "fiscal_year": "2025-2026",
            "net_profit": 10_000_000.0,
            "audited_statement_file": FILE,
            "audit_report_ref": "AUD-FY26-1",
            "trustee_board_resolution_ref": "R1",
            "trustee_resolution_file": FILE,
            "bwwf_challan_ref": "C1",
        }
    )
    a.action_calculate()
    a.action_request_approval()
    decide(w, a, w.manager)
    poster = w.as_(w.manager2)["fix.wppf.allocation"].browse(a.id)
    with pytest.raises(UserError, match="Configure the payroll accounting"), env.cr.savepoint():
        poster.action_post()
    w.co.write(
        {
            "payroll_wppf_expense_account_id": _account(
                env, w.co, "6190", "WPPF Expense", "expense"
            ).id,
            "payroll_wppf_payable_account_id": _account(
                env, w.co, "2190", "WPPF Payable", "liability_current"
            ).id,
        }
    )
    poster.action_post()
    a.invalidate_recordset()
    lines = sorted((ln.account_id.code, ln.debit, ln.credit) for ln in a.gl_move_id.line_ids)
    assert a.state == "posted" and a.gl_move_id.state == "posted"
    assert lines == [("2190", 0.0, 500000.0), ("6190", 500000.0, 0.0)]
