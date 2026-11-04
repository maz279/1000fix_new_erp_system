# A09 P0 (A3 / A4 / A6) - the payroll controls, proved as the people they
# protect against.
#
# The A09 workflow audit (2026-11-03) found that a payroll officer could
# approve a run by writing `state`, divert a colleague's salary by rewriting
# the bank account on an approved payslip, raise an approved basic tenfold,
# add a ghost payslip to an approved run, approve his own BDT 5,000,000
# off-cycle payment, and that a plain employee read everyone's pay through the
# salary register. Every test below acts as a freshly created NON-admin user
# (the superuser is trusted by the guards and would hide a gap); the
# superuser only builds the fixture and, where labelled, plays a tampered
# database row. Live ORM, rolled back (`odoo_env`).
#
# A09 M56 build (C1, SOD-29): approval is now a routed M63 request, decided
# from the approver's inbox task (`decide`), and the bank release belongs to a
# Payroll Disbursement Releaser. Where a test below called `action_approve`
# directly as the approving manager, it now goes through the inbox; where it
# asserted that a direct approval was refused for lack of the role, it now
# asserts the stronger rule: nobody approves directly, and the request never
# reaches the preparer. Every attack the P0 suite made is still made.
import itertools
from datetime import date
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo import Command
from odoo.addons.cd_p03_portal.controllers import a09 as a09ctl
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]

PS, PE = date(2026, 1, 1), date(2026, 1, 31)
CO_ACC, CO_ROUTING = "2051234567", "175261726"
KARIM_ACC, KARIM_ROUTING = "1501203345001", "060274689"
NASRIN_ACC, NASRIN_ROUTING = "2702150098761", "090261725"
ATTACKER_ACC, ATTACKER_ROUTING = "9999000011112222", "090261725"
RESOLUTION_PDF = "JVBERi0xLjQKJcOkw7zDtsOfCg=="  # a stand-in signed resolution (PDF header)
_SEQ = itertools.count(1)


class FakeRequest:
    def __init__(self, env):
        self.env = env


def p03(env, route, **kw):
    """Call a real /p03/model/* controller method as `env`'s user."""
    with mock.patch.object(api, "request", FakeRequest(env)):
        return getattr(api.P03GenericApiController(), route)(**kw)


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    bdt = env.ref("base.BDT")
    bdt.active = True
    n = next(_SEQ)
    co = env["res.company"].create({"name": "A09 P0 Payroll Co %d" % n, "currency_id": bdt.id})
    ou = env["operating.unit"].create(
        {
            "name": "P0 OU %d" % n,
            "code": "P0PY%d" % n,
            "partner_id": co.partner_id.id,
            "company_id": co.id,
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
                    "login": "%s%d@a09p0.test" % (login, n),
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

    s = SimpleNamespace(env=cenv, co=co)
    s.plain = user("p0plain")
    s.officer = user("p0officer", "cd_payroll_bd.group_payroll_officer")
    s.manager = user("p0manager", "cd_payroll_bd.group_payroll_manager")
    s.manager2 = user("p0manager2", "cd_payroll_bd.group_payroll_manager")
    s.releaser = user("p0releaser", "cd_payroll_bd.group_payroll_release")

    def emp(name, basic, acc=None, routing=None):
        """HR's fixture: the employee, an active contract and, when given,
        the salary account record and BEFTN routing on the master."""
        e = cenv["hr.employee"].create({"name": name, "company_id": co.id})
        cenv["fix.employment.contract"].create(
            {
                "employee_id": e.id,
                "company_id": co.id,
                "contract_type": "permanent",
                "joining_date": date(2020, 1, 1),
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

    s.karim = emp("P0 Karim", 30000.0, KARIM_ACC, KARIM_ROUTING)
    s.nasrin = emp("P0 Nasrin", 60000.0, NASRIN_ACC, NASRIN_ROUTING)
    lock = cenv["fix.attendance.lock"].create(
        {"name": "Jan 2026", "period_start": PS, "period_end": PE}
    )
    lock.action_lock()
    s.as_ = lambda u: cenv(user=u.id)
    return s


def calculated(w):
    """The officer's legitimate maker path."""
    p = w.as_(w.officer)["fix.payroll.period"].create(
        {"name": "2026-01", "period_start": PS, "period_end": PE}
    )
    p.write({"company_account_no": CO_ACC, "company_routing_no": CO_ROUTING})
    p.action_verify_attendance_locked()
    p.action_calculate()
    return p


def routed_to(w, rec):
    """The users the engine opened an inbox task for."""
    return (
        w.env["fix.workflow.task"]
        .sudo()
        .search([("request_id", "=", rec.approval_request_id.id), ("state", "=", "pending")])
        .mapped("assigned_user_id")
    )


def decide(w, rec, approver):
    """`approver` approves `rec` from their own inbox task."""
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
    w.as_(approver)["fix.workflow.task"].browse(task.id).action_approve()
    rec.invalidate_recordset()


def approved(w):
    p = calculated(w)
    p.action_request_approval()
    decide(w, p, w.manager)
    return w.as_(w.officer)["fix.payroll.period"].browse(p.id)


def paid(w):
    p = approved(w)
    w.as_(w.releaser)["fix.payroll.period"].browse(p.id).action_pay()
    p.invalidate_recordset()
    return p


def slip_of(period, employee):
    return period.payslip_ids.filtered(lambda s: s.employee_id == employee)


# ---------------------------------------------------------------- A3 inputs


def test_calculate_stamps_the_officer_and_takes_bank_details_from_the_master(w):
    p = calculated(w)
    assert p.state == "calculated" and p.calculator_id == w.officer
    karim = slip_of(p, w.karim)
    # the employee's bank account record and the master's routing code -
    # nothing typed on the slip
    assert (karim.bank_account_no, karim.routing_no) == (KARIM_ACC, KARIM_ROUTING)
    nasrin = slip_of(p, w.nasrin)
    assert (nasrin.bank_account_no, nasrin.routing_no) == (NASRIN_ACC, NASRIN_ROUTING)


def test_officer_cannot_type_bank_details_or_amounts_even_before_approval(w):
    p = calculated(w)
    slip = slip_of(p, w.karim)
    for vals in (
        {"bank_account_no": ATTACKER_ACC},
        {"routing_no": ATTACKER_ROUTING},
        {"basic": 300000.0},
        {"ot_hours": 99.0},
        {"gratuity_amount": 5_000_000.0},
    ):
        with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
            slip.write(vals)
    slip.invalidate_recordset()
    assert (slip.bank_account_no, slip.basic) == (KARIM_ACC, 30000.0)


# ---------------------------------------------------------------- A4 state / stamps


def test_officer_cannot_write_period_state_via_orm(w):
    p = calculated(w)
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        p.write({"state": "approved"})
    assert p.state == "calculated"


def test_officer_cannot_write_period_state_via_the_p03_write_endpoint(w):
    p = calculated(w)
    res = p03(
        w.as_(w.officer),
        "model_write",
        model="fix.payroll.period",
        record_id=p.id,
        values={"state": "approved"},
    )
    p.invalidate_recordset()
    assert "error" in res and p.state == "calculated", res
    # and the workspace form serves the state read-only
    form = p03(
        w.as_(w.officer),
        "model_form",
        model="fix.payroll.period",
        record_id=p.id,
        fields=[{"name": "state"}, {"name": "name"}],
    )
    flags = {f["name"]: f["readonly"] for f in form["fields"]}
    assert flags == {"state": True, "name": False}, form


def test_manager_cannot_forge_the_calculator_to_self_approve(w):
    p = w.as_(w.manager)["fix.payroll.period"].create(
        {"name": "M", "period_start": PS, "period_end": PE}
    )
    p.action_verify_attendance_locked()
    p.action_calculate()
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        p.write({"calculator_id": w.officer.id})
    # nobody approves directly any more: approval is decided from an inbox task
    with pytest.raises(UserError, match="approver's inbox"), w.env.cr.savepoint():
        p.action_approve()
    # and the request the calculating manager raises never reaches him
    p.write({"company_account_no": CO_ACC, "company_routing_no": CO_ROUTING})
    p.action_request_approval()
    assert routed_to(w, p) == w.manager2
    assert p.state == "calculated"


def test_approval_pins_the_approver_digest_and_total(w):
    p = approved(w)
    assert p.state == "approved"
    assert p.approved_by_id == w.manager and p.approved_on
    assert p.approved_digest and p.approved_net_total == p.net_total
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        p.write({"approved_net_total": 1.0})


def test_approved_period_is_not_reopened(w):
    p = approved(w)
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        p.write({"state": "attendance_locked"})
    with pytest.raises(UserError, match="not recalculated"), w.env.cr.savepoint():
        p.action_verify_attendance_locked()
    with pytest.raises(UserError, match="can no longer be changed"), w.env.cr.savepoint():
        p.write({"period_end": date(2026, 2, 28)})
    assert p.state == "approved"


# ---------------------------------------------------------------- A3 freeze at approval


def test_salary_diversion_after_approval_is_refused_and_the_file_pays_the_master_account(w):
    p = approved(w)
    slip = slip_of(p, w.karim)
    with pytest.raises(UserError), w.env.cr.savepoint():
        slip.write({"bank_account_no": ATTACKER_ACC, "routing_no": ATTACKER_ROUTING})
    res = p03(
        w.as_(w.officer),
        "model_write",
        model="fix.payslip",
        record_id=slip.id,
        values={"bank_account_no": ATTACKER_ACC},
    )
    assert "error" in res, res
    # the releaser (SOD-29) sends the file: it pays the registered account only
    w.as_(w.releaser)["fix.payroll.period"].browse(p.id).action_pay()
    p.invalidate_recordset()
    content = p.beftn_batch_id.file_content
    assert p.state == "paid" and KARIM_ACC in content and ATTACKER_ACC not in content
    assert p.beftn_batch_id.total_amount == p.approved_net_total


def test_post_approval_basic_edit_is_refused(w):
    p = approved(w)
    slip = slip_of(p, w.karim)
    with pytest.raises(UserError, match="frozen"), w.env.cr.savepoint():
        slip.write({"basic": 300000.0, "pf_employee_pct": 0.0})
    # the frozen-period check holds even inside a transition
    with pytest.raises(UserError, match="frozen"), w.env.cr.savepoint():
        slip._guarded().write({"basic": 300000.0})
    with pytest.raises(UserError, match="frozen"), w.env.cr.savepoint():
        slip.action_compute_separation(date(2026, 1, 31))
    slip.invalidate_recordset()
    assert slip.basic == 30000.0


def test_no_ghost_payslip_in_an_approved_period(w):
    p = approved(w)
    ghost = w.env["hr.employee"].create({"name": "P0 Ghost", "company_id": w.co.id})
    vals = {"period_id": p.id, "employee_id": ghost.id, "company_id": w.co.id, "basic": 250000.0}
    with pytest.raises(UserError), w.env.cr.savepoint():
        w.as_(w.officer)["fix.payslip"].create(vals)
    # not even with the transition token: an approved run takes no new slip
    with pytest.raises(UserError, match="frozen"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.payslip"]._guarded().create(vals)
    with pytest.raises(UserError, match="frozen"), w.env.cr.savepoint():
        w.as_(w.manager)["fix.payslip"]._guarded().browse(p.payslip_ids[:1].id).unlink()
    assert len(p.payslip_ids) == 2


def test_no_slip_typed_into_a_calculated_period_either(w):
    p = calculated(w)
    ghost = w.env["hr.employee"].create({"name": "P0 Ghost 2", "company_id": w.co.id})
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.payslip"].create(
            {"period_id": p.id, "employee_id": ghost.id, "company_id": w.co.id, "basic": 1.0}
        )


def test_beftn_refuses_when_the_slips_no_longer_match_the_approval(w):
    p = approved(w)
    # a tampered row (superuser plays the database write the guard stops)
    slip_of(p, w.karim).sudo().write({"bank_account_no": ATTACKER_ACC})
    with pytest.raises(UserError, match="does not match its approval"), w.env.cr.savepoint():
        w.as_(w.releaser)["fix.payroll.period"].browse(p.id).action_pay()
    p.invalidate_recordset()
    assert p.state == "approved" and not p.beftn_batch_id


def test_beftn_refuses_when_an_approved_amount_changed(w):
    p = approved(w)
    slip_of(p, w.nasrin).sudo().write({"basic": 600000.0})  # tampered row
    with pytest.raises(UserError, match="does not match its approval"), w.env.cr.savepoint():
        w.as_(w.releaser)["fix.payroll.period"].browse(p.id).action_pay()


def test_submitted_batch_is_immutable_and_never_regenerated(w):
    p = paid(w)
    batch = w.as_(w.releaser)["fix.beftn.batch"].browse(p.beftn_batch_id.id)
    original = batch.file_content
    with pytest.raises(UserError, match="never regenerated"), w.env.cr.savepoint():
        batch.action_generate_beftn_file()
    for vals in ({"file_content": "FORGED"}, {"total_amount": 1.0}, {"state": "settled"}):
        with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
            batch.write(vals)
    res = p03(
        w.as_(w.releaser),
        "model_write",
        model="fix.beftn.batch",
        record_id=batch.id,
        values={"state": "settled"},
    )
    batch.invalidate_recordset()
    assert "error" in res and batch.state == "submitted" and batch.file_content == original


def test_gl_move_cannot_be_cleared_to_post_twice(w):
    p = approved(w)
    mp = w.as_(w.manager)["fix.payroll.period"].browse(p.id)
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        mp.write({"gl_move_id": False, "state": "paid"})


# ---------------------------------------------------------------- A4 off-cycle, bonus, WPPF


def test_offcycle_self_approval_is_refused(w):
    oc = w.as_(w.officer)["fix.payroll.offcycle"].create(
        {
            "employee_id": w.karim.id,
            "payment_type": "adjustment",
            "amount": 5_000_000.0,
            "company_id": w.co.id,
        }
    )
    assert oc.prepared_by_id == w.officer
    # nobody approves directly, neither by the ORM nor through the workspace
    with pytest.raises(UserError, match="approver's inbox"), w.env.cr.savepoint():
        oc.action_approve()
    res = p03(
        w.as_(w.officer),
        "model_action",
        model="fix.payroll.offcycle",
        ids=[oc.id],
        method="action_approve",
    )
    assert not res["success"], res
    # the officer's request goes to the Payroll Managers, never to the officer
    oc.action_request_approval()
    assert routed_to(w, oc) == w.manager | w.manager2
    # nor is the manager who prepared it
    own = w.as_(w.manager)["fix.payroll.offcycle"].create(
        {
            "employee_id": w.karim.id,
            "payment_type": "advance",
            "amount": 999_999.0,
            "company_id": w.co.id,
        }
    )
    with pytest.raises(UserError, match="approver's inbox"), w.env.cr.savepoint():
        own.action_approve()
    own.action_request_approval()
    assert routed_to(w, own) == w.manager2
    # state and the preparer stamp are not typed
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        oc.write({"state": "approved"})
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        own.write({"prepared_by_id": w.officer.id})
    res = p03(
        w.as_(w.officer),
        "model_write",
        model="fix.payroll.offcycle",
        record_id=oc.id,
        values={"state": "paid"},
    )
    oc.invalidate_recordset()
    assert "error" in res and oc.state == "draft"


def test_offcycle_amount_and_payee_freeze_at_approval(w):
    oc = w.as_(w.officer)["fix.payroll.offcycle"].create(
        {
            "employee_id": w.karim.id,
            "payment_type": "arrear",
            "amount": 1000.0,
            "company_id": w.co.id,
        }
    )
    oc.write({"amount": 1200.0})  # a draft is still the preparer's to correct
    oc.action_request_approval()
    decide(w, oc, w.manager)
    assert oc.state == "approved" and oc.approved_by_id == w.manager
    for vals in ({"amount": 900_000.0}, {"employee_id": w.nasrin.id}):
        with pytest.raises(UserError, match="can no longer be changed"), w.env.cr.savepoint():
            oc.write(vals)
    oc.invalidate_recordset()
    assert (oc.amount, oc.employee_id) == (1200.0, w.karim)


def test_bonus_run_needs_a_second_payroll_manager(w):
    run = w.as_(w.officer)["fix.payroll.bonus.run"].create(
        {"festival": "eid_ul_fitr", "basis": "gross", "multiplier": 3.0, "company_id": w.co.id}
    )
    run.action_compute()
    with pytest.raises(UserError, match="approver's inbox"), w.env.cr.savepoint():
        run.action_approve()
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        run.write({"state": "paid", "total_amount": 1.0})
    own = w.as_(w.manager)["fix.payroll.bonus.run"].create(
        {"festival": "durga_puja", "company_id": w.co.id}
    )
    own.action_compute()
    with pytest.raises(UserError, match="approver's inbox"), w.env.cr.savepoint():
        own.action_approve()
    own.action_request_approval()
    assert routed_to(w, own) == w.manager2
    run.action_request_approval()
    decide(w, run, w.manager)
    assert run.state == "approved" and run.approved_by_id == w.manager
    with pytest.raises(UserError, match="can no longer be changed"), w.env.cr.savepoint():
        run.write({"multiplier": 10.0})


def test_wppf_needs_a_second_payroll_manager_and_freezes_the_profit(w):
    a = w.as_(w.officer)["fix.wppf.allocation"].create(
        {
            "fiscal_year": "2025-2026",
            "net_profit": 10_000_000.0,
            "company_id": w.co.id,
            "trustee_board_resolution_ref": "TRUSTEE/2026/01",
            "trustee_resolution_file": RESOLUTION_PDF,
        }
    )
    a.action_calculate()
    assert a.calculated_by_id == w.officer
    with pytest.raises(UserError, match="approver's inbox"), w.env.cr.savepoint():
        a.action_approve()
    with pytest.raises(UserError, match="can no longer be changed"), w.env.cr.savepoint():
        a.write({"net_profit": 1000.0})
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        a.write({"total_wppf_pool": 50.0})
    a.action_request_approval()
    decide(w, a, w.manager)
    assert a.state == "approved" and a.total_wppf_pool == 500000.0
    # a manager who calculated it may not approve it
    b = w.as_(w.manager)["fix.wppf.allocation"].create(
        {
            "fiscal_year": "2026-2027",
            "net_profit": 1_000_000.0,
            "company_id": w.co.id,
            "trustee_board_resolution_ref": "R",
            "trustee_resolution_file": RESOLUTION_PDF,
        }
    )
    b.action_calculate()
    b.action_request_approval()
    assert routed_to(w, b) == w.manager2


def test_certificate_figures_come_from_the_payslips_never_typed(w):
    paid(w)  # a certificate reports the fiscal year's PAID slips
    C = w.as_(w.officer)["fix.payroll.certificate"]
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        C.create(
            {
                "employee_id": w.karim.id,
                "fiscal_year": "2025-26",
                "total_gross": 9_999_999.0,
                "company_id": w.co.id,
            }
        )
    c = C.create(
        {
            "employee_id": w.nasrin.id,
            "certificate_type": "tax",
            "fiscal_year": "2025-26",
            "company_id": w.co.id,
        }
    )
    c.action_issue()
    nasrin = w.env["fix.payslip"].search([("employee_id", "=", w.nasrin.id)])
    assert c.state == "issued" and c.issued_on
    assert (c.total_gross, c.total_tax_withheld) == (
        sum(nasrin.mapped("gross")),
        sum(nasrin.mapped("tax_withheld")),
    )
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        c.write({"total_gross": 1.0})


def test_return_totals_come_from_the_payslips(w):
    paid(w)  # a return reports the period's PAID slips
    r = w.as_(w.officer)["fix.payroll.return"].create(
        {"period": "Q3-2025-26", "period_start": PS, "period_end": PE, "company_id": w.co.id}
    )
    r.action_reconcile_payslips()
    assert r.total_tax == sum(
        w.env["fix.payslip"].search([("company_id", "=", w.co.id)]).mapped("tax_withheld")
    )
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        r.write({"total_tax": 1.0, "state": "filed"})


# ---------------------------------------------------------------- A6 reports and KPIs


def test_plain_employee_gets_no_salary_register_and_no_payroll_kpis(w):
    calculated(w)
    res = p03(w.as_(w.plain), "model_report", module="M56", report="salary_register")
    assert "error" in res and not res.get("rows"), res
    for report in (
        "payroll_cost_allocation",
        "tax_deduction_summary",
        "pf_gratuity",
        "payroll_variance",
    ):
        res = p03(w.as_(w.plain), "model_report", module="M56", report=report)
        assert "error" in res and not res.get("rows"), (report, res)
    with mock.patch.object(a09ctl, "request", FakeRequest(w.as_(w.plain))):
        out = a09ctl.P03PeopleApi().people_kpis(module="M56")
    assert not out.get("M56", {}).get("gross_payroll"), out


def test_payroll_officer_reads_the_register_of_their_own_company_only(w):
    calculated(w)
    other = w.env["res.company"].create({"name": "P0 Other Co Reports"})
    oe = w.env["hr.employee"].create({"name": "P0 OtherCo Staff", "company_id": other.id})
    op = w.env["fix.payroll.period"].create(
        {"name": "OC", "period_start": PS, "period_end": PE, "company_id": other.id}
    )
    w.env["fix.payslip"].create(
        {"period_id": op.id, "employee_id": oe.id, "company_id": other.id, "basic": 77777.0}
    )
    res = p03(w.as_(w.officer), "model_report", module="M56", report="salary_register")
    names = {r["employee"] for r in res["rows"]}
    assert names == {"P0 Karim", "P0 Nasrin"}, res
    with mock.patch.object(a09ctl, "request", FakeRequest(w.as_(w.officer))):
        out = a09ctl.P03PeopleApi().people_kpis(module="M56")
    assert out["M56"]["gross_payroll"] == round(sum(r["gross"] for r in res["rows"]), 2), out
