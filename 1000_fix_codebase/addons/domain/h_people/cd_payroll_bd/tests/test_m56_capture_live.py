# M56 capture audit (2026-11-17): the records the Income Tax, Provident Fund,
# Gratuity and Loans & Advances pages now capture, proved as the people they
# stop - fresh NON-admin payroll users through the ORM and the real /p03
# endpoints. The superuser only builds fixtures (company, employees, locks).
#
#   FR-PAY-031/032  a salary advance is released only with its approved
#                   recovery schedule, and the monthly run deducts the
#                   instalment until it is repaid (never a bonus)
#   FR-PAY-013/014  a validated investment declaration reaches the payslip's
#   BRU-PAY-10      tax; a declared or rejected one does not; the recorder
#                   and the employee never validate
#   FR-PAY-020      once the company keeps a PF register, members contribute
#                   at their own rates and non-members not at all
#   FR-PAY-022/Q-05 the first gratuity accrual moves from the approved
#                   opening provision, not from nothing
from datetime import date

import pytest
from odoo.addons.cd_payroll_bd.tests import test_a09_m56_r2 as _r2
from odoo.addons.cd_payroll_bd.tests.test_a09_m56_r2 import (
    DE,
    DS,
    FILE,
    _account,
    _lock_month,
    calculated,
    decide,
    p03,
    slip_of,
)
from odoo.exceptions import AccessError, UserError, ValidationError

# the round-2 fixture: a company, payroll users and two employees
w = _r2.w

pytestmark = [pytest.mark.financial]

FEB_S, FEB_E = date(2026, 2, 1), date(2026, 2, 28)


def _approved_advance(w, amount=12000.0):
    adv = w.as_(w.officer)["fix.payroll.offcycle"].create(
        {
            "employee_id": w.karim.id,
            "payment_type": "advance",
            "amount": amount,
            "payment_date": date(2026, 1, 10),
            "reason": "Medical emergency",
        }
    )
    adv.action_request_approval()
    decide(w, adv, w.manager)
    return adv


def _schedule(w, adv, instalment=5000.0, user=None):
    rec = w.as_(user or w.officer)["fix.payroll.recovery"].create(
        {
            "recovery_type": "advance",
            "advance_id": adv.id,
            "instalment": instalment,
            "reason": "Repaid over the next months from salary",
        }
    )
    return rec


# ------------------------------------------------------------- salary advance


def test_an_advance_is_released_only_with_its_approved_schedule_and_the_run_recovers_it(w):
    w.co.sudo().write(
        {
            "payroll_recovery_account_id": _account(
                w.env, w.co, "1205", "Staff Advances", "asset_receivable"
            ).id
        }
    )
    adv = _approved_advance(w)
    releaser = w.as_(w.releaser)["fix.payroll.offcycle"].browse(adv.id)
    with pytest.raises(UserError, match="recovery schedule"), w.env.cr.savepoint():
        releaser.action_pay()
    sched = _schedule(w, adv)
    # the amount owed defaults to the whole advance; the employee is the payee
    assert (sched.amount, sched.employee_id, sched.recovery_type) == (12000.0, w.karim, "advance")
    # a draft schedule does not release it either
    with pytest.raises(UserError, match="recovery schedule"), w.env.cr.savepoint():
        releaser.action_pay()
    sched.action_request_approval()
    decide(w, sched, w.manager)
    assert sched.state == "approved"
    releaser.action_pay()
    assert adv.state == "paid"
    # the run takes the instalment, after tax, and records it
    _lock_month(w, FEB_S, FEB_E, "Feb 2026 adv")
    feb = calculated(w, "2026-02", FEB_S, FEB_E)
    slip = slip_of(feb, w.karim)
    assert slip.recovery_deduction == 5000.0
    assert round(slip.net, 2) == round(
        slip.gross - slip.pf_employee - slip.tax_withheld - 5000.0, 2
    )
    sched.invalidate_recordset()
    assert (sched.recovered_amount, sched.remaining_amount) == (5000.0, 7000.0)
    adv.invalidate_recordset()
    assert adv.advance_outstanding == 7000.0
    # Nasrin owes nothing and loses nothing
    assert slip_of(feb, w.nasrin).recovery_deduction == 0.0


def test_an_advance_schedule_is_never_more_than_the_advance_and_never_twice(w):
    adv = _approved_advance(w, 6000.0)
    Rec = w.as_(w.officer)["fix.payroll.recovery"]
    with pytest.raises(ValidationError, match="exceeds"), w.env.cr.savepoint():
        Rec.create(
            {"advance_id": adv.id, "amount": 7000.0, "reason": "x", "recovery_type": "advance"}
        )
    with pytest.raises(ValidationError, match="instalment"), w.env.cr.savepoint():
        Rec.create(
            {"advance_id": adv.id, "instalment": 9000.0, "reason": "x", "recovery_type": "advance"}
        )
    with pytest.raises(ValidationError, match="employee"), w.env.cr.savepoint():
        Rec.create(
            {
                "advance_id": adv.id,
                "employee_id": w.nasrin.id,
                "reason": "x",
                "recovery_type": "advance",
            }
        )
    _schedule(w, adv, 2000.0)
    with pytest.raises(ValidationError, match="already has"), w.env.cr.savepoint():
        _schedule(w, adv, 1000.0)
    # an arrear is not an advance
    arrear = w.as_(w.officer)["fix.payroll.offcycle"].create(
        {"employee_id": w.karim.id, "payment_type": "arrear", "amount": 100.0}
    )
    with pytest.raises(ValidationError, match="names the salary advance"), w.env.cr.savepoint():
        Rec.create({"advance_id": arrear.id, "reason": "x", "recovery_type": "advance"})
    # the schedule's preparer cannot approve it
    sched = w.as_(w.manager)["fix.payroll.recovery"].create(
        {"advance_id": _approved_advance(w, 500.0).id, "reason": "x", "recovery_type": "advance"}
    )
    with pytest.raises(UserError), w.env.cr.savepoint():
        sched.action_approve()


def test_an_advance_is_not_taken_from_a_festival_bonus(w):
    w.co.sudo().write({"payroll_recovery_source": "any_payment"})
    adv = _approved_advance(w)
    sched = _schedule(w, adv)
    sched.action_request_approval()
    decide(w, sched, w.manager)
    w.as_(w.releaser)["fix.payroll.offcycle"].browse(adv.id).action_pay()
    run = w.as_(w.officer)["fix.payroll.bonus.run"].create(
        {"festival": "eid_ul_fitr", "bonus_date": date(2026, 3, 20)}
    )
    run.action_compute()
    karim = run.line_ids.filtered(lambda ln: ln.employee_id == w.karim)
    assert karim.recovery_deduction == 0.0


# ------------------------------------------------------- investment declaration


def _declare(w, employee, amount, user=None, fy="2025-26"):
    return w.as_(user or w.officer)["fix.investment.declaration"].create(
        {
            "employee_id": employee.id,
            "fiscal_year": fy,
            "instrument": "dps",
            "declared_amount": amount,
            "evidence_file": FILE,
        }
    )


def test_a_validated_declaration_reduces_the_tax_and_a_declared_one_does_not(w):
    # December, before any declaration: the tax with no investment
    dec = calculated(w, "2025-12", DS, DE)
    before = slip_of(dec, w.nasrin)
    assert before.investment_allowance == 0.0 and before.tax_withheld > 0
    decl = _declare(w, w.nasrin, 200000.0)
    assert decl.name.startswith("INV/") and decl.state == "draft"
    with pytest.raises(UserError, match="recorded by you"), w.env.cr.savepoint():
        decl.action_validate()
    mine = w.as_(w.manager)["fix.investment.declaration"].browse(decl.id)
    with pytest.raises(UserError, match="at most"), w.env.cr.savepoint():
        mine.action_validate(eligible_amount=250000.0)
    mine.action_validate(eligible_amount=150000.0)
    assert (decl.state, decl.eligible_amount, decl.validated_by_id) == (
        "validated",
        150000.0,
        w.manager,
    )
    # a second, unvalidated declaration and another year's do not count
    _declare(w, w.nasrin, 500000.0)
    other_year = _declare(w, w.nasrin, 80000.0, fy="2026-27")
    w.as_(w.manager)["fix.investment.declaration"].browse(other_year.id).action_validate()
    jan = calculated(w)
    after = slip_of(jan, w.nasrin)
    assert after.investment_allowance == 150000.0
    assert after.tax_withheld < before.tax_withheld
    # a validated declaration is frozen
    with pytest.raises(UserError, match="can no longer be changed"), w.env.cr.savepoint():
        decl.write({"declared_amount": 900000.0})
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        other_year.write({"eligible_amount": 1.0})


def test_nobody_validates_their_own_declaration_and_a_plain_user_records_none(w):
    with pytest.raises(AccessError), w.env.cr.savepoint():
        _declare(w, w.karim, 1000.0, user=w.plain)
    w.karim.sudo().user_id = w.manager.id
    decl = _declare(w, w.karim, 1000.0)
    with pytest.raises(UserError, match="themself"), w.env.cr.savepoint():
        w.as_(w.manager)["fix.investment.declaration"].browse(decl.id).action_validate()
    with pytest.raises(UserError, match="why"), w.env.cr.savepoint():
        w.as_(w.manager2)["fix.investment.declaration"].browse(decl.id).action_reject("  ")
    w.as_(w.manager2)["fix.investment.declaration"].browse(decl.id).action_reject("No receipt")
    assert decl.state == "rejected" and decl.eligible_amount == 0.0
    with pytest.raises(UserError, match="fiscal year"), w.env.cr.savepoint():
        _declare(w, w.karim, 1000.0, fy="2025")


def test_the_workspace_records_and_validates_a_declaration(w):
    res = p03(
        w.as_(w.officer),
        "model_write",
        model="fix.investment.declaration",
        record_id=None,
        values={
            "employee_id": w.nasrin.id,
            "fiscal_year": "2025-26",
            "instrument": "savings_certificate",
            "declared_amount": 50000.0,
            "evidence_file": FILE,
        },
    )
    assert res.get("id"), res
    # a stamp cannot be typed through the form
    bad = p03(
        w.as_(w.officer),
        "model_write",
        model="fix.investment.declaration",
        record_id=res["id"],
        values={"eligible_amount": 50000.0},
    )
    assert "error" in bad, bad
    act = p03(
        w.as_(w.manager),
        "model_action",
        model="fix.investment.declaration",
        ids=[res["id"]],
        method="action_validate",
        kwargs={"eligible_amount": "40000"},
    )
    assert act["success"], act
    decl = w.env["fix.investment.declaration"].browse(res["id"])
    assert (decl.state, decl.eligible_amount) == ("validated", 40000.0)


# --------------------------------------------------------------- provident fund


def _member(w, employee, rate, user=None):
    return w.as_(user or w.officer)["fix.pf.member"].create(
        {
            "employee_id": employee.id,
            "joined_fund_on": date(2020, 1, 1),
            "employee_rate": rate,
            "employer_rate": rate,
        }
    )


def test_once_the_register_is_kept_only_members_contribute_at_their_rates(w):
    dec = calculated(w, "2025-12", DS, DE)
    # no register yet: the calculation is unchanged
    assert slip_of(dec, w.karim).pf_employee_pct == 10.0
    assert slip_of(dec, w.nasrin).pf_employee_pct == 10.0
    m = _member(w, w.karim, 5.0)
    # a recorded (unapproved) membership changes nothing yet
    with pytest.raises(AccessError), w.env.cr.savepoint():
        m.action_approve()  # the officer is no Payroll Manager
    w.as_(w.manager)["fix.pf.member"].browse(m.id).action_approve()
    assert m.state == "active" and m.approved_by_id == w.manager
    jan = calculated(w)
    karim, nasrin = slip_of(jan, w.karim), slip_of(jan, w.nasrin)
    assert (karim.pf_employee_pct, karim.pf_employer_pct) == (5.0, 5.0)
    assert karim.pf_employee == round(karim.basic * 0.05, 2)
    assert (nasrin.pf_employee, nasrin.pf_employer) == (0.0, 0.0)
    with pytest.raises(ValidationError, match="already has"), w.env.cr.savepoint():
        _member(w, w.karim, 7.0)
    with pytest.raises(UserError, match="can no longer be changed"), w.env.cr.savepoint():
        m.write({"employee_rate": 1.0})


def test_a_manager_never_approves_the_membership_they_recorded(w):
    m = _member(w, w.nasrin, 10.0, user=w.manager)
    with pytest.raises(UserError, match="recorded by you"), w.env.cr.savepoint():
        m.action_approve()
    with pytest.raises(ValidationError), w.env.cr.savepoint():
        _member(w, w.karim, 0.0)
    w.as_(w.manager2)["fix.pf.member"].browse(m.id).action_approve()
    with pytest.raises(UserError, match="why"), w.env.cr.savepoint():
        w.as_(w.manager2)["fix.pf.member"].browse(m.id).action_leave(" ")
    w.as_(w.manager2)["fix.pf.member"].browse(m.id).action_leave("Opted out at resignation")
    assert m.state == "left" and m.left_on


# ------------------------------------------------------ gratuity opening provision


def test_the_first_accrual_moves_from_the_approved_opening_provision(w):
    Opening = w.as_(w.officer)["fix.payroll.gratuity.opening"]
    with pytest.raises(ValidationError, match="month end"), w.env.cr.savepoint():
        Opening.create(
            {
                "employee_id": w.karim.id,
                "as_of": date(2025, 11, 15),
                "opening_liability": 1.0,
                "legacy_reference": "x",
            }
        )
    op = Opening.create(
        {
            "employee_id": w.karim.id,
            "as_of": date(2025, 11, 30),
            "opening_liability": 100000.0,
            "legacy_reference": "Legacy GL 2205 schedule FY25",
        }
    )
    with pytest.raises(UserError, match="schedule"), w.env.cr.savepoint():
        w.as_(w.manager)["fix.payroll.gratuity.opening"].browse(op.id).action_approve()
    op.write({"evidence_file": FILE})
    with pytest.raises(AccessError), w.env.cr.savepoint():
        op.action_approve()
    w.as_(w.manager)["fix.payroll.gratuity.opening"].browse(op.id).action_approve()
    assert op.state == "approved"
    w.env["fix.payroll.gratuity.accrual"].sudo().cron_accrue_gratuity(as_of="2025-12-31")
    rows = w.env["fix.payroll.gratuity.accrual"].sudo().search([("month", "=", "2025-12")])
    karim = rows.filtered(lambda r: r.employee_id == w.karim)
    nasrin = rows.filtered(lambda r: r.employee_id == w.nasrin)
    assert karim.previous_liability == 100000.0
    assert karim.accrual == round(karim.liability - 100000.0, 2)
    assert nasrin.previous_liability == 0.0 and nasrin.accrual == nasrin.liability
    # once the register carries an employee, an opening is no longer taken on
    late = Opening.create(
        {
            "employee_id": w.nasrin.id,
            "as_of": date(2025, 11, 30),
            "opening_liability": 5.0,
            "legacy_reference": "late",
            "evidence_file": FILE,
        }
    )
    with pytest.raises(UserError, match="already has monthly"), w.env.cr.savepoint():
        w.as_(w.manager)["fix.payroll.gratuity.opening"].browse(late.id).action_approve()
