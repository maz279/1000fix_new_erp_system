# A09 ERP audit fix, builder stream B1a (2026-11-23). One regression test per
# defect this stream fixes, each built so ONLY the new rule can refuse it:
# ruff: noqa: F811  (pytest fixtures imported from the round-1 suite)
#
#   M56-F2  a Payroll Manager who holds NO accounting group posts a paid run
#           through the M19 funnel; a user without the payroll group is
#           refused; the posting log still names the real operator
#   M56-F10 a previous paid period's NULL-employee slip no longer aborts the
#           variance refresh
#   M56-F12 an empty PF register pays NO provident fund; one approved
#           membership pays only the member, at the membership's rates
#   M56-F6  the A07 recovery API (_fix_recovery_from_source): routed,
#           idempotent, capped, fail-closed
#   M56-F11 the aggregate net-pay recovery cap refuses instead of
#           over-deducting (0 = off, today's behaviour)
#   M56-F1  a run that would compute no payslip at all is refused with the
#           reason
#   M56-F7/F8/X-F3 the readiness preflight names unconfigured roles; a
#           component the run carries with no account role is refused at
#           prevalidation; the gratuity cron refuses loudly
#   M57-F1  an approved incentive run of a PREVIOUS month is picked up once
#   M57-F3  a raise effective mid-month is paid per version, by days
#   M55-F4  approved unpaid leave reduces the pay for those days
#   M55-F3  festival-holiday / rest-day / verified callout work is paid at
#           the overtime rate, separately labelled, never twice
#   M56-F21 the final settlement's 30-working-day clock (Friday/Saturday and
#           company holidays aware) is computed, exposed and reported
import itertools
from datetime import date, datetime

import pytest
from odoo import Command
from odoo.addons.cd_payroll_bd.tests.test_a09_m56_payroll_build import (
    CO_ACC,
    CO_ROUTING,
    _account,
    calculated,
    decide,
    new_period,
    slip_of,
    task_of,  # noqa: F401  (imported for symmetry with the build suite)
    w,  # noqa: F401  (the round-1 fixture: company, users, two employees)
)
from odoo.exceptions import AccessError, UserError

pytestmark = [pytest.mark.financial]

DS, DE = date(2025, 12, 1), date(2025, 12, 31)
_SEQ = itertools.count(1)


def persona(w, login, *groups):
    """A user of the fixture company in exactly `groups` (no accounting
    groups unless asked for - the operating persona of M56-F2)."""
    n = next(_SEQ)
    ids = [w.env.ref("base.group_user").id] + [w.env.ref(g).id for g in groups]
    u = (
        w.env["res.users"]
        .with_context(no_reset_password=True, tracking_disable=True)
        .create(
            {
                "name": login,
                "login": "b1a-%s-%d@a09.test" % (login, n),
                "company_id": w.co.id,
                "company_ids": [Command.set([w.co.id])],
                "group_ids": [Command.set(ids)],
            }
        )
    )
    return u


def lock_month(w, start, end, name):
    lock = w.env["fix.attendance.lock"].create(
        {"name": name, "period_start": start, "period_end": end}
    )
    lock.action_lock()
    return lock


def dec_period(w, rel):
    """A PAID December period of the fixture company (the previous paid
    period the January variance compares with)."""
    lock_month(w, DS, DE, "Dec 2025")
    p = w.as_(w.officer)["fix.payroll.period"].create(
        {"name": "2025-12", "period_start": DS, "period_end": DE}
    )
    p.write({"company_account_no": CO_ACC, "company_routing_no": CO_ROUTING})
    p.action_verify_attendance_locked()
    p.action_calculate()
    p.action_request_approval()
    decide(w, p, w.manager)
    w.as_(rel)["fix.payroll.period"].browse(p.id).action_pay()
    p.invalidate_recordset()
    return p


# ================================================================ M56-F2


def test_f2_a_manager_without_accounting_groups_posts_a_paid_run(w):
    officer = w.officer  # payroll officer only, no accounting group
    mgr = persona(w, "f2mgr", "cd_payroll_bd.group_payroll_manager")
    rel = persona(
        w, "f2rel", "cd_payroll_bd.group_payroll_release", "cd_payroll_bd.group_payroll_manager"
    )
    for u in (officer, mgr, rel):
        assert not u.has_group("account.group_account_manager")
        assert not u.has_group("account.group_account_user")
    p = calculated(w)  # the officer prepares and calculates
    p.action_request_approval()
    decide(w, p, mgr)  # decided from the inbox by the accounting-free manager
    w.as_(rel)["fix.payroll.period"].browse(p.id).action_pay()
    p.invalidate_recordset()
    assert p.state == "paid"
    # THE DEFECT: posting as the manager used to die reading account.journal
    w.as_(mgr)["fix.payroll.period"].browse(p.id).action_post()
    p.invalidate_recordset()
    move = p.gl_move_id
    assert p.state == "posted" and move.state == "posted"
    debits = sum(move.line_ids.mapped("debit"))
    credits = sum(move.line_ids.mapped("credit"))
    assert debits > 0 and debits == credits
    # the real operator stays recorded in M19's posting log (the elevated env
    # keeps the uid)
    log = w.env["fix.journal.posting.log"].sudo().search([("move_id", "=", move.id)])
    assert log and log.posted_by == mgr
    # a user without the payroll group is refused before anything is read
    plain = persona(w, "f2plain")
    with pytest.raises(AccessError, match="Only payroll posts"), w.env.cr.savepoint():
        w.as_(plain)["fix.payroll.period"].browse(p.id).action_post()


# ================================================================ M56-F10


def test_f10_a_null_employee_slip_of_the_previous_period_no_longer_aborts(w):
    dec = dec_period(w, w.releaser)
    assert dec.state == "paid"
    victim = dec.payslip_ids[0]
    # the production defect: a corrupt row with employee_id NULL (NOT NULL in
    # the model; the replica's column predated it). The constraint is relaxed
    # inside the test's transaction — rolled back with it — to stage the row.
    w.env.cr.execute("ALTER TABLE fix_payslip ALTER COLUMN employee_id DROP NOT NULL")
    w.env.cr.execute("UPDATE fix_payslip SET employee_id = NULL WHERE id = %s", (victim.id,))
    dec.invalidate_recordset()
    p = new_period(w)
    p.action_verify_attendance_locked()
    # before the fix this died inserting fix.payroll.variance (employee_id
    # NULL) and aborted the whole calculation transaction
    p.action_calculate()
    assert p.state == "calculated"
    lines = w.env["fix.payroll.variance"].sudo().search([("period_id", "=", p.id)])
    assert lines and all(line.employee_id for line in lines)
    # a trial run over the same corrupt history is equally safe
    p2 = new_period(w, "2026-01-B")
    p2.action_verify_attendance_locked()
    p2.action_trial_run()
    assert "TRIAL" in p2.trial_note


# ================================================================ M56-F12


def test_f12_an_empty_register_pays_no_pf_and_one_membership_pays_only_its_member(w):
    jan = calculated(w)
    assert slip_of(jan, w.karim).pf_employee_pct == 0.0
    assert slip_of(jan, w.nasrin).pf_employee_pct == 0.0
    assert jan.pf_total == 0.0
    m = w.as_(w.officer)["fix.pf.member"].create(
        {
            "employee_id": w.karim.id,
            "joined_fund_on": date(2020, 1, 1),
            "employee_rate": 8.0,
            "employer_rate": 8.0,
        }
    )
    w.as_(w.manager)["fix.pf.member"].browse(m.id).action_approve()
    lock_month(w, date(2026, 2, 1), date(2026, 2, 28), "Feb 2026")
    feb = w.as_(w.officer)["fix.payroll.period"].create(
        {
            "name": "2026-02",
            "period_start": date(2026, 2, 1),
            "period_end": date(2026, 2, 28),
        }
    )
    feb.action_verify_attendance_locked()
    feb.action_calculate()
    karim, nasrin = slip_of(feb, w.karim), slip_of(feb, w.nasrin)
    assert (karim.pf_employee_pct, karim.pf_employer_pct) == (8.0, 8.0)
    assert karim.pf_employee == round(karim.basic * 0.08, 2)
    assert (nasrin.pf_employee_pct, nasrin.pf_employer_pct) == (0.0, 0.0)
    assert nasrin.pf_employee == 0.0


# ================================================================ M56-F6


def test_f6_recovery_from_source_is_routed_capped_idempotent_and_fail_closed(w):
    Recovery = w.env["fix.payroll.recovery"]
    partner = w.env["res.partner"].create({"name": "A07 Equipment Damage", "company_id": w.co.id})
    caller = persona(w, "f6hr")  # the A07 caller holds NO payroll group
    # fail-closed: no employee, no cap, no configured account role
    with pytest.raises(UserError, match="names no employee"), w.env.cr.savepoint():
        w.as_(caller)[Recovery._name]._fix_recovery_from_source(
            partner, w.env["hr.employee"], 5000.0, 10.0, "x"
        )
    with pytest.raises(UserError, match="wage-deduction limit"), w.env.cr.savepoint():
        w.as_(caller)[Recovery._name]._fix_recovery_from_source(partner, w.karim, 5000.0, 0.0, "x")
    with pytest.raises(UserError, match="Overpayment Recovery Account"), w.env.cr.savepoint():
        w.as_(caller)[Recovery._name]._fix_recovery_from_source(
            partner, w.karim, 5000.0, 10.0, "Equipment damage"
        )
    w.co.sudo().write(
        {
            "payroll_recovery_account_id": _account(
                w.env, w.co, "1205", "Recovery", "asset_receivable"
            ).id
        }
    )
    rec = w.as_(caller)[Recovery._name]._fix_recovery_from_source(
        partner, w.karim, 5000.0, 10.0, "Equipment damage DEP-9"
    )
    assert rec.recovery_type == "source" and rec.state == "draft"
    assert (rec.source_model, rec.source_res_id) == ("res.partner", partner.id)
    assert rec.source_cap_pct == 10.0 and rec.prepared_by_id == caller
    # routed maker-checker: the deduction waits for a Payroll Manager
    assert rec.approval_state == "pending"
    decide(w, rec, w.manager)
    rec.invalidate_recordset()
    assert rec.state == "approved"
    # idempotent per source: the same source returns its recovery
    again = w.as_(caller)[Recovery._name]._fix_recovery_from_source(
        partner, w.karim, 5000.0, 10.0, "re-sent"
    )
    assert again.id == rec.id
    # the cap the caller passed binds the deduction: 10% of the payment's net
    # BEFORE the recovery (the slip's own net already subtracts it, so the
    # base is net + the deduction: 30,000 -> 3,000)
    p = calculated(w)
    slip = slip_of(p, w.karim)
    base_net = slip.net + slip.recovery_deduction
    assert slip.recovery_deduction == round(base_net * 0.10, 2)
    assert 0 < slip.recovery_deduction < rec.amount


# ================================================================ M56-F11


def test_f11_the_aggregate_net_cap_refuses_rather_than_over_deducting(w):
    Recovery = w.env["fix.payroll.recovery"]
    w.co.sudo().write(
        {
            "payroll_recovery_account_id": _account(
                w.env, w.co, "1205", "Recovery", "asset_receivable"
            ).id,
            "payroll_recovery_net_cap_pct": 30.0,
        }
    )
    sources = [
        w.env["res.partner"].create({"name": "A07 Source %d" % i, "company_id": w.co.id})
        for i in range(2)
    ]
    for src in sources:
        rec = Recovery._fix_recovery_from_source(src, w.karim, 5000.0, 90.0, "fine")
        decide(w, rec, w.manager)
    p = new_period(w)
    p.action_verify_attendance_locked()
    # both recoveries together would take 10,000 - more than 30% of a ~30k
    # net: the calculation refuses with the reason, it never trims silently
    with pytest.raises(UserError, match="aggregate recovery cap"), w.env.cr.savepoint():
        p.action_calculate()
    # 0 = off: today's unbounded behaviour, the whole due is taken
    w.co.sudo().payroll_recovery_net_cap_pct = 0.0
    p.action_calculate()
    slip = slip_of(p, w.karim)
    assert slip.recovery_deduction == 10000.0


# ================================================================ M56-F1 / F7 / F8 / X-F3


def test_f1_a_run_with_no_real_employee_is_refused_with_the_reason(w):
    # both fixture employees left long before the period and their contracts
    # ended: nothing is in scope (left_date played by SQL - it is an exit
    # record's field, M21's to write)
    w.env.cr.execute(
        "UPDATE hr_employee SET left_date = %s WHERE id IN %s",
        (date(2025, 6, 1), tuple((w.karim | w.nasrin).ids)),
    )
    w.env["fix.employment.contract"].search(
        [("employee_id", "in", (w.karim | w.nasrin).ids)]
    ).sudo().write({"state": "terminated"})
    w.env.invalidate_all()
    p = new_period(w)
    p.action_verify_attendance_locked()
    with pytest.raises(UserError, match="would compute payslips for NO employee"):
        p.action_calculate()
    with pytest.raises(UserError, match="would compute payslips for NO employee"):
        w.as_(w.officer)["fix.payroll.period"].browse(p.id).action_trial_run()


def test_f8_a_carried_component_without_its_account_role_refuses_prevalidation(w):
    m = w.as_(w.officer)["fix.pf.member"].create(
        {
            "employee_id": w.karim.id,
            "joined_fund_on": date(2020, 1, 1),
            "employee_rate": 10.0,
            "employer_rate": 10.0,
        }
    )
    w.as_(w.manager)["fix.pf.member"].browse(m.id).action_approve()
    p = calculated(w)
    assert slip_of(p, w.karim).pf_employee > 0  # the run carries PF
    pf_payable = w.co.sudo().payroll_pf_payable_account_id
    assert pf_payable, "the fixture leaves the PF payable role set"
    w.co.sudo().payroll_pf_payable_account_id = False  # the role goes missing
    with pytest.raises(UserError, match="Provident Fund Payable Account"), w.env.cr.savepoint():
        p.action_request_approval()
    w.co.sudo().payroll_pf_payable_account_id = pf_payable.id
    p.action_request_approval()  # the role restored, the run routes


def test_preflight_names_readiness_gaps_and_the_tax_table_warning(w, monkeypatch):
    p = new_period(w)
    w.co.sudo().write(
        {
            "payroll_beftn_account_no": False,
            "payroll_beftn_routing_no": False,
            "payroll_recovery_account_id": False,
            "payroll_gratuity_expense_account_id": False,
            "payroll_wppf_bank_account_id": False,
        }
    )
    # one employee whose only contract is a DRAFT (no contract to pay from),
    # one with a contract but neither bank account nor wallet nor tax profile
    ghost = w.env["hr.employee"].create({"name": "B1a Unready", "company_id": w.co.id})
    w.env["fix.employment.contract"].create(
        {
            "employee_id": ghost.id,
            "company_id": w.co.id,
            "contract_type": "permanent",
            "joining_date": date(2020, 1, 1),
            "basic_monthly": 25000.0,
            "state": "draft",
        }
    )
    unbanked = w.env["hr.employee"].create(
        {"name": "B1a No Bank", "company_id": w.co.id, "taxpayer_category": False}
    )
    w.env["fix.employment.contract"].create(
        {
            "employee_id": unbanked.id,
            "company_id": w.co.id,
            "contract_type": "permanent",
            "joining_date": date(2020, 1, 1),
            "basic_monthly": 25000.0,
            "state": "active",
        }
    )
    report = p._payroll_readiness()
    assert any("B1a Unready" in row and "no active contract" in row for row in report["employees"])
    assert any(
        "B1a No Bank" in row and "no registered salary account" in row
        for row in report["employees"]
    )
    assert any("Originating BEFTN account/routing" in a for a in report["accounts"])
    assert any("Gratuity Expense" in a for a in report["accounts"])
    assert any("WPPF / BWWF Paying Bank" in a for a in report["accounts"])
    assert "no approved provident-fund membership" in report["pf_register"]
    # the lead's addition: whatever fix.statutory.pack warns about the tax
    # table in force surfaces as a WARNING (never a refusal); read
    # defensively, so it also works before the API exists
    Pack = type(w.env["fix.statutory.pack"])
    monkeypatch.setattr(
        Pack,
        "_fix_tax_table_note",
        classmethod(lambda cls, company, period: "tax table unsourced for %s" % period),
    )
    report = p._payroll_readiness()
    assert any("tax table unsourced" in txt for txt in report["warnings"])
    note = "\n".join(p._readiness_note())
    assert "READINESS WARNING - tax table unsourced" in note
    assert "READINESS - unconfigured company account roles" in note


def test_xf3_the_gratuity_cron_refuses_loudly_without_accounts(w):
    Accrual = w.env["fix.payroll.gratuity.accrual"].sudo()
    with pytest.raises(UserError, match="not configured"), w.env.cr.savepoint():
        Accrual.cron_accrue_gratuity(as_of="2026-01-31")


# ================================================================ M57-F1


def _old_incentive_run(w, period, lines):
    """An APPROVED incentive run of `period` with one line per (employee,
    amount); the run's approval is played by SQL (M57's own suite owns the
    routed approval; here it isolates payroll's pickup)."""
    run = (
        w.env["fix.incentive.run"]
        .sudo()
        .create({"company_id": w.co.id, "period": period, "band_base": 10000.0})
    )
    out = []
    for emp, amount in lines:
        sc = (
            w.env["fix.performance.scorecard"]
            .sudo()
            .create({"company_id": w.co.id, "employee_id": emp.id, "period": period})
        )
        out.append(
            w.env["fix.incentive.line"]
            .sudo()
            .create(
                {
                    "company_id": w.co.id,
                    "run_id": run.id,
                    "scorecard_id": sc.id,
                    "employee_id": emp.id,
                    "amount": amount,
                }
            )
        )
    w.env.cr.execute("UPDATE fix_incentive_run SET state = %s WHERE id = %s", ("approved", run.id))
    run.invalidate_recordset()
    return run, out


def test_m57f1_an_older_approved_incentive_run_is_picked_up_once(w):
    if "fix.incentive.line" not in w.env:
        pytest.skip("cd_performance is not installed")
    # the normal order: December's incentive was approved AFTER December's
    # payroll was committed - the lines used to be stranded forever
    _run, (karim_line,) = _old_incentive_run(w, "2025-12", [(w.karim, 2400.0)])
    p = calculated(w)  # January 2026
    karim = slip_of(p, w.karim)
    assert karim.incentive == 2400.0
    karim_line.invalidate_recordset()
    assert karim_line.payslip_ref_id == karim.id and karim_line.applied_to_payslip
    # paid once: a second run of the month does not pay it again
    other = calculated(w, "2026-01-B")
    assert slip_of(other, w.karim).incentive == 0.0
    # a line whose employee is not in the run is NAMED, not dropped silently
    ghost = w.env["hr.employee"].create({"name": "B1a Left Before Run", "company_id": w.co.id})
    _old_incentive_run(w, "2025-11", [(ghost, 900.0)])
    p2 = new_period(w, "2026-01-C")
    p2.action_verify_attendance_locked()
    p2.action_calculate()
    assert "B1a Left Before Run" in p2.calculation_note
    assert "cannot be paid here" in p2.calculation_note


# ================================================================ M57-F3


def test_m57f3_a_raise_effective_mid_month_is_paid_for_the_days_it_ran(w):
    anchor = w.env["fix.employment.contract"].search(
        [("employee_id", "=", w.karim.id), ("state", "=", "active")]
    )
    assert len(anchor) == 1
    raised = w.env["fix.employment.contract"].create(
        {
            "employee_id": w.karim.id,
            "company_id": w.co.id,
            "contract_type": "permanent",
            "joining_date": date(2020, 1, 1),
            "effective_date": date(2026, 1, 16),
            "basic_monthly": 40000.0,
            "previous_contract_id": anchor.id,
            "state": "draft",
        }
    )
    # M21's activation result, played as data: the old version superseded to
    # the 15th, the raise active from the 16th
    w.env.cr.execute(
        "UPDATE fix_employment_contract SET state = 'superseded', date_end = %s WHERE id = %s",
        (date(2026, 1, 15), anchor.id),
    )
    w.env.cr.execute(
        "UPDATE fix_employment_contract SET state = 'active' WHERE id = %s", (raised.id,)
    )
    w.env.invalidate_all()
    p = calculated(w)
    karim = slip_of(p, w.karim)
    # 30,000 x 15/31 + 40,000 x 16/31 = 35,161.29: each version for its days
    assert karim.basic == 35161.29
    assert karim.paid_days == 31
    # the unchanged colleague still gets one version, one figure
    assert slip_of(p, w.nasrin).basic == 60000.0


# ================================================================ M55-F4


def test_m55f4_approved_unpaid_leave_reduces_the_pay_for_those_days(w):
    if "is_unpaid" not in w.env["fix.leave.type"]._fields:
        pytest.skip("cd_hr_core's is_unpaid leave-type flag has not landed yet (other stream)")
    unpaid_type = w.env["fix.leave.type"].create(
        {
            "name": "Leave Without Pay (test)",
            "code": "LWP-T",
            "entitlement_days": 0,
            "is_unpaid": True,
        }
    )
    paid_type = w.env["fix.leave.type"].create(
        {"name": "Casual (test)", "code": "CAS-T", "entitlement_days": 10}
    )
    jan_lock = w.env["fix.attendance.lock"].search(
        [("period_start", "=", date(2026, 1, 1))], limit=1
    )
    jan_lock.action_unlock("B1a test: record the leaves")
    Leave = w.env["fix.leave.request"].sudo()
    leave = Leave.create(
        {
            "company_id": w.co.id,
            "employee_id": w.karim.id,
            "leave_type_id": unpaid_type.id,
            "date_from": date(2026, 1, 12),
            "date_to": date(2026, 1, 14),
        }
    )
    w.env.cr.execute("UPDATE fix_leave_request SET state = 'approved' WHERE id = %s", (leave.id,))
    paid = Leave.create(
        {
            "company_id": w.co.id,
            "employee_id": w.karim.id,
            "leave_type_id": paid_type.id,
            "date_from": date(2026, 1, 20),
            "date_to": date(2026, 1, 21),
        }
    )
    w.env.cr.execute("UPDATE fix_leave_request SET state = 'approved' WHERE id = %s", (paid.id,))
    w.env.invalidate_all()
    jan_lock.action_lock()
    p = calculated(w)
    karim = slip_of(p, w.karim)
    # the day-rate convention of the proration: 30,000 / 31 x 3 days
    assert karim.unpaid_leave_days == 3
    assert karim.unpaid_leave_deduction == round(30000.0 / 31 * 3, 2)
    assert karim.basic == round(30000.0 - 30000.0 / 31 * 3, 2)
    # a PAID leave type reduces nothing
    nasrin = slip_of(p, w.nasrin)
    assert nasrin.unpaid_leave_days == 0 and nasrin.unpaid_leave_deduction == 0.0


# ================================================================ M55-F3


def test_m55f3_holiday_rest_day_and_callout_work_is_paid_never_twice(w):
    Att = w.env["fix.attendance.record"].sudo()
    # the fixture's January lock is re-opened to add the M55 facts (the same
    # door M55's own lock manager uses), then locked again before payroll
    jan_lock = w.env["fix.attendance.lock"].search(
        [("period_start", "=", date(2026, 1, 1))], limit=1
    )
    jan_lock.action_unlock("B1a test: add holiday / rest-day / callout facts")
    # a confirmed festival holiday of the period
    w.env["fix.hr.holiday"].create(
        {
            "name": "Shab-e-Barat (test)",
            "company_id": w.co.id,
            "date": date(2026, 1, 13),
            "holiday_type": "festival",
        }
    )
    # 8h on the holiday: nothing beyond the standard day, no OT request ->
    # no ordinary overtime is payable, ALL 8h are premium holiday hours
    Att.create(
        {
            "employee_id": w.karim.id,
            "company_id": w.co.id,
            "check_in": datetime(2026, 1, 13, 8, 0),
            "check_out": datetime(2026, 1, 13, 16, 0),
        }
    )
    # a rest-day call of 4h with an approved OT request for 2h: the 2h are
    # paid as ordinary overtime, only the other 2h are premium rest-day hours
    rest = Att.create(
        {
            "employee_id": w.karim.id,
            "company_id": w.co.id,
            "check_in": datetime(2026, 1, 17, 8, 0),
            "check_out": datetime(2026, 1, 17, 12, 0),
        }
    )
    rest.action_mark_rest_day()
    req = (
        w.env["fix.overtime.request"]
        .sudo()
        .create(
            {
                "employee_id": w.karim.id,
                "company_id": w.co.id,
                "date": date(2026, 1, 17),
                "hours": 2.0,
                "reason": "Rest-day emergency",
            }
        )
    )
    req.write({"state": "submitted"})
    req.action_approve()
    # a verified on-call callout of 2h
    oncall = (
        w.env["fix.hr.oncall"]
        .sudo()
        .create(
            {
                "company_id": w.co.id,
                "employee_id": w.karim.id,
                "date_from": datetime(2026, 1, 9, 18, 0),
                "date_to": datetime(2026, 1, 10, 18, 0),
            }
        )
    )
    # a callout is recorded only on an on-call that has started (M55 rule)
    oncall.action_start()
    callout = (
        w.env["fix.oncall.callout"]
        .sudo()
        .create(
            {
                "oncall_id": oncall.id,
                "called_at": datetime(2026, 1, 9, 22, 0),
                "finished_at": datetime(2026, 1, 10, 0, 0),
                "description": "Data-centre power fault",
            }
        )
    )
    w.env.cr.execute(
        "UPDATE fix_oncall_callout SET state = 'verified' WHERE id = %s", (callout.id,)
    )
    w.env.invalidate_all()
    jan_lock.action_lock()
    p = calculated(w)
    karim = slip_of(p, w.karim)
    # ordinary overtime: the 2 approved rest-day hours only
    assert karim.ot_hours == 2.0
    assert (karim.holiday_work_hours, karim.rest_day_work_hours, karim.callout_hours) == (
        8.0,
        2.0,
        2.0,
    )
    # at today's overtime treatment (2x the s.108 hourly rate)
    rate = 30000.0 / 208
    assert karim.holiday_work_pay == round(rate * 2 * 8, 2)
    assert karim.rest_day_work_pay == round(rate * 2 * 2, 2)
    assert karim.callout_pay == round(rate * 2 * 2, 2)
    # the premium components are inside gross (riding Other Allowance)
    assert karim.other_allowance == (
        karim.holiday_work_pay + karim.rest_day_work_pay + karim.callout_pay
    )
    assert karim.gross == round(
        karim.basic
        + karim.overtime
        + karim.holiday_work_pay
        + karim.rest_day_work_pay
        + karim.callout_pay,
        2,
    )


# ================================================================ M56-F21


def test_f21_the_settlement_clock_is_30_working_days_fridays_and_holidays_away(w):
    from odoo.addons.cd_payroll_bd.models.fix_payroll_settlement import (
        SETTLEMENT_DUE_WORKING_DAYS,
        settlement_due_date,
    )

    assert SETTLEMENT_DUE_WORKING_DAYS == 30
    # last working day Thu 2026-01-15; Fri 16 + Sat 17 are the weekend
    assert settlement_due_date(w.env, w.co, date(2026, 1, 15)) == date(2026, 2, 26)
    # a confirmed company holiday pushes the date by one working day: the 30th
    # working day is Thu 2026-02-26, and the next working day after it is
    # Sun 2026-03-01 (Fri 27 and Sat 28 are the estate's weekend)
    w.env["fix.hr.holiday"].create(
        {
            "name": "Spring Day (test)",
            "company_id": w.co.id,
            "date": date(2026, 2, 1),
            "holiday_type": "public",
        }
    )
    assert settlement_due_date(w.env, w.co, date(2026, 1, 15)) == date(2026, 3, 1)
    assert settlement_due_date(w.env, w.co, False) is False
    # exposed on the settlement off-cycle payment and reported at validation
    exit_rec = (
        w.env["fix.hr.exit"]
        .sudo()
        .create(
            {
                "company_id": w.co.id,
                "employee_id": w.nasrin.id,
                "exit_type": "resignation",
                "last_working_day": date(2026, 1, 15),
            }
        )
    )
    oc = (
        w.env["fix.payroll.offcycle"]
        .sudo()
        .create(
            {
                "company_id": w.co.id,
                "employee_id": w.nasrin.id,
                "payment_type": "settlement",
                "payment_date": date(2026, 1, 20),
                "amount": 1000.0,
                "exit_id": exit_rec.id,
            }
        )
    )
    oc.invalidate_recordset()
    # with the test's 2026-02-01 holiday in place (created above), the due
    # date is the next working day after Thu 2026-02-26: Sun 2026-03-01
    assert oc.settlement_due_on == date(2026, 3, 1)
    # the readiness preflight reports the unpaid settlement's clock (either
    # side of the due date: the fixture's clock is fixed, today is not)
    note = "\n".join(new_period(w)._settlement_due_notes())
    assert oc.name in note
    assert "due in" in note or "OVERDUE by" in note
