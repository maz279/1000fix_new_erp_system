# A09 round 2 (M56) - the items round 1 left open, each proved as the person it
# stops, through the ORM as freshly created NON-admin users and, where the
# screens offer it, through the real /p03 endpoints. The superuser only builds
# fixtures (company, accounts, employees, contracts, locks) and, where
# labelled, plays a database row a guard stops.
#
#   M56-5   GL split per operating unit, every group balanced
#   M56-14  trial run, variance against the previous paid period, the gate
#   BRU-PAY-04 post-payment correction as a linked off-cycle payment
#   M56-11  statutory pack: versioned, effective-dated, two-person approval,
#           pinned on every slip, seeded "as coded, unsourced"
#   FR-PAY-004 year-to-date TDS (setting; default today's method)
#   FR-PAY-022 monthly gratuity provision cron (idempotent, deployed)
#   M56-4   bank return import, failed items marked, re-issue by the releaser
#   bonus TDS at the payslip marginal rate (setting; default none)
#   joiner first-month proration by calendar days
#   MFS wallet salaries: one disbursement file per provider
#   M56-1   bank-change cool-off with a second person's confirmation
#   payslip PDF (wkhtmltopdf)
#   M56-13  WPPF beneficiaries, BWWF payment, audited profit evidence
#   I8 / I9 M55 retro adjustments and approved on-call allowances
import base64
import contextlib
import itertools
import json
from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo import Command
from odoo.addons.cd_p03_portal.controllers import a09 as a09ctl
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_payroll_bd.models import fix_payroll_settlement
from odoo.addons.cd_payroll_bd.models.fix_payroll import FixPayrollPeriod
from odoo.addons.cd_payroll_bd.models.fix_payroll_statutory import (
    marginal_rate,
    separation_figures,
)
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.payroll_engine import income_tax, salary_exemption

pytestmark = [pytest.mark.financial]

PS, PE = date(2026, 1, 1), date(2026, 1, 31)
DS, DE = date(2025, 12, 1), date(2025, 12, 31)
CO_ACC, CO_ROUTING = "2051234567", "175261726"
KARIM_ACC, KARIM_ROUTING = "1501203345001", "060274689"
NASRIN_ACC, NASRIN_ROUTING = "2702150098761", "090261725"
FILE = "JVBERi0xLjQKJcOkw7zDtsOfCg=="  # a stand-in scanned document (PDF header)
_SEQ = itertools.count(1)


class FakeRequest:
    def __init__(self, env):
        self.env = env


def p03(env, route, **kw):
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
    co = env["res.company"].create({"name": "A09 M56 R2 Co %d" % n, "currency_id": bdt.id})
    ou = env["operating.unit"].create(
        {
            "name": "R2 Dhaka %d" % n,
            "code": "R2D%d" % n,
            "partner_id": co.partner_id.id,
            "company_id": co.id,
        }
    )
    ou2 = env["operating.unit"].create(
        {
            "name": "R2 Ctg %d" % n,
            "code": "R2C%d" % n,
            "partner_id": co.partner_id.id,
            "company_id": co.id,
        }
    )
    journal = env["account.journal"].create(
        {"name": "Payroll", "code": "R2P%d" % n, "type": "general", "company_id": co.id}
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
                    "login": "%s%d@a09r2.test" % (login, n),
                    "company_id": co.id,
                    "company_ids": [Command.set([co.id])],
                    "group_ids": [Command.set(ids)],
                }
            )
        )
        if "assigned_operating_unit_ids" in u._fields:
            u.assigned_operating_unit_ids = [Command.set([ou.id, ou2.id])]
        if "default_operating_unit_id" in u._fields:
            u.default_operating_unit_id = ou.id
        return u

    s = SimpleNamespace(env=cenv, co=co, ou=ou, ou2=ou2)
    s.plain = user("r2plain")
    s.officer = user("r2officer", "cd_payroll_bd.group_payroll_officer")
    s.manager = user(
        "r2manager", "cd_payroll_bd.group_payroll_manager", "account.group_account_manager"
    )
    s.manager2 = user(
        "r2manager2", "cd_payroll_bd.group_payroll_manager", "account.group_account_manager"
    )
    s.releaser = user(
        "r2releaser", "cd_payroll_bd.group_payroll_release", "account.group_account_manager"
    )

    def emp(name, basic, acc=None, routing=None, joining=date(2020, 1, 1), **master):
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
    s.karim = emp("R2 Karim", 30000.0, KARIM_ACC, KARIM_ROUTING, operating_unit_id=ou.id)
    s.nasrin = emp("R2 Nasrin", 60000.0, NASRIN_ACC, NASRIN_ROUTING, operating_unit_id=ou2.id)

    def lock(start, end, name):
        rec = cenv["fix.attendance.lock"].create(
            {"name": name, "period_start": start, "period_end": end}
        )
        rec.action_lock()
        return rec

    s.lock = lock(PS, PE, "Jan 2026")
    s.lock_dec = lock(DS, DE, "Dec 2025")
    s.as_ = lambda u: cenv(user=u.id)
    return s


def new_period(w, name="2026-01", start=PS, end=PE, user=None):
    p = w.as_(user or w.officer)["fix.payroll.period"].create(
        {"name": name, "period_start": start, "period_end": end}
    )
    p.write({"company_account_no": CO_ACC, "company_routing_no": CO_ROUTING})
    return p


def calculated(w, name="2026-01", start=PS, end=PE):
    p = new_period(w, name, start, end)
    p.action_verify_attendance_locked()
    p.action_calculate()
    return p


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


def routed_to(w, rec):
    return (
        w.env["fix.workflow.task"]
        .sudo()
        .search([("request_id", "=", rec.approval_request_id.id), ("state", "=", "pending")])
        .mapped("assigned_user_id")
    )


def decide(w, rec, approver):
    task_of(w, rec, approver).action_approve()
    rec.invalidate_recordset()


def approved(w, name="2026-01", start=PS, end=PE):
    p = calculated(w, name, start, end)
    p.action_request_approval()
    decide(w, p, w.manager)
    return p


def paid(w, name="2026-01", start=PS, end=PE):
    p = approved(w, name, start, end)
    w.as_(w.releaser)["fix.payroll.period"].browse(p.id).action_pay()
    p.invalidate_recordset()
    return p


def slip_of(period, employee):
    return period.sudo().payslip_ids.filtered(lambda s: s.employee_id == employee)


# ================================================================ M56-5 GL split per OU


def test_gl_posting_splits_by_operating_unit_and_every_group_balances(w):
    p = paid(w)
    w.as_(w.manager2)["fix.payroll.period"].browse(p.id).action_post()
    p.invalidate_recordset()
    move = p.gl_move_id
    assert move.state == "posted"
    dims = w.env["fix.journal.dimension"].sudo().search([("move_line_id", "in", move.line_ids.ids)])
    by_line = {d.move_line_id.id: d.operating_unit_id for d in dims}
    assert set(by_line) == set(move.line_ids.ids), "every line carries its unit"
    groups = {}
    for line in move.line_ids:
        g = groups.setdefault(by_line[line.id], [0.0, 0.0, set()])
        g[0] += line.debit
        g[1] += line.credit
        g[2].add(line.account_id.code)
    # two employee units, two groups, each balanced on its own
    assert set(groups) == {w.ou, w.ou2}
    for ou, (debit, credit, _codes) in groups.items():
        assert round(debit, 2) == round(credit, 2), ou.name
    karim, nasrin = slip_of(p, w.karim), slip_of(p, w.nasrin)
    assert karim.cost_operating_unit_id == w.ou and nasrin.cost_operating_unit_id == w.ou2
    # the Dhaka group's net payable is Karim's net, the Chittagong group's Nasrin's
    payable = {by_line[ln.id]: ln.credit for ln in move.line_ids if ln.account_id.code == "2101"}
    assert payable == {w.ou: karim.net, w.ou2: nasrin.net}
    # payroll.posted carries the per-unit totals for finance's consumers
    event = (
        w.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", "payroll.posted"), ("aggregate_id", "=", p.id)], limit=1)
    )
    payload = json.loads(event.payload)
    assert payload["company_id"] == w.co.id
    assert {row["operating_unit_id"] for row in payload["by_operating_unit"]} == {w.ou.id, w.ou2.id}


# ================================================================ M56-14 trial and variance


def _paid_december(w):
    return paid(w, "2025-12", DS, DE)


def test_a_trial_run_computes_and_never_pays(w):
    p = new_period(w)
    # a plain employee may not trial-run payroll
    with pytest.raises(AccessError), w.env.cr.savepoint():
        w.as_(w.plain)["fix.payroll.period"].browse(p.id).action_trial_run()
    res = p03(
        w.as_(w.officer),
        "model_action",
        model="fix.payroll.period",
        ids=[p.id],
        method="action_trial_run",
    )
    assert res["success"], res
    p.invalidate_recordset()
    assert p.state == "draft" and not p.sudo().payslip_ids and p.trial_run_by_id == w.officer
    assert "TRIAL - nothing is paid: 2 employee(s)" in p.trial_note
    trial = p.sudo().variance_ids.filtered(lambda v: v.kind == "trial")
    assert trial.mapped("employee_id") == w.karim | w.nasrin
    # the trial's nets are the calculation's
    p.action_verify_attendance_locked()
    p.action_calculate()
    nets = {v.employee_id: v.current_net for v in trial}
    assert nets[w.karim] == slip_of(p, w.karim).net and nets[w.nasrin] == slip_of(p, w.nasrin).net
    # a committed run is never trial-run again
    p.action_request_approval()
    decide(w, p, w.manager)
    with (
        pytest.raises(UserError, match="committed run is not trial-calculated"),
        w.env.cr.savepoint(),
    ):
        p.action_trial_run()


def test_variance_over_the_threshold_blocks_approval_until_a_reviewer_acknowledges(w):
    dec = _paid_december(w)
    newbie = w.emp(
        "R2 January Joiner", 20000.0, "4040404040", "060274689", joining=date(2026, 1, 1)
    )
    # threshold 0 (today): no gate, whatever moved
    p = calculated(w)
    lines = p.sudo().variance_ids.filtered(lambda v: v.kind == "run")
    by = {v.employee_id: v for v in lines}
    assert by[w.karim].previous_period_id == dec and by[w.karim].variance == 0.0
    assert by[newbie].no_comparison
    assert p.action_prevalidate() == {"issues": []}
    # the business sets 10%: the joiner (no previous net) is over it
    w.co.sudo().payroll_variance_threshold_pct = 10.0
    with (
        pytest.raises(UserError, match="R2 January Joiner has no net in the previous paid period"),
        w.env.cr.savepoint(),
    ):
        p.action_request_approval()
    assert p.approval_state == "none"
    line = by[newbie]
    # the calculator is not the reviewer; a plain user has no payroll role
    with (
        pytest.raises(UserError, match="not by whoever prepared or calculated"),
        w.env.cr.savepoint(),
    ):
        w.as_(w.officer)["fix.payroll.variance"].browse(line.id).action_acknowledge(note="ok")
    with pytest.raises(AccessError), w.env.cr.savepoint():
        w.as_(w.plain)["fix.payroll.variance"].browse(line.id).action_acknowledge(note="ok")
    with pytest.raises(UserError, match="State why"), w.env.cr.savepoint():
        w.as_(w.manager2)["fix.payroll.variance"].browse(line.id).action_acknowledge()
    # nor is the acknowledgement typed
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.payroll.variance"].browse(line.id).write(
            {"acknowledged_by_id": w.manager2.id}
        )
    res = p03(
        w.as_(w.manager2),
        "model_action",
        model="fix.payroll.variance",
        ids=[line.id],
        method="action_acknowledge",
        kwargs={"note": "Joined 1 January, offer letter on file"},
    )
    assert res["success"], res
    p.action_request_approval()
    decide(w, p, w.manager)
    assert p.state == "approved"


# ================================================================ correction run


def test_a_post_payment_correction_is_a_linked_offcycle_and_the_slip_stays_paid(w):
    p = paid(w)
    slip = slip_of(p, w.karim)
    net = slip.net
    Off = w.as_(w.officer)["fix.payroll.offcycle"]
    # the paid slip itself is never edited
    with pytest.raises(UserError, match="frozen"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.payslip"].browse(slip.id).write({"ot_hours": 4.0})
    with (
        pytest.raises(ValidationError, match="State what the correction puts right"),
        w.env.cr.savepoint(),
    ):
        Off.create({"correction_slip_id": slip.id, "amount": 1500.0})
    oc = Off.create(
        {
            "correction_slip_id": slip.id,
            "amount": 1500.0,
            "reason": "Night allowance missed on 12 Jan",
        }
    )
    assert (oc.employee_id, oc.payment_type, oc.company_id) == (w.karim, "correction", w.co)
    # it pays the slip's employee only, and only a PAID slip is corrected
    with (
        pytest.raises(ValidationError, match="employee and company of the payslip"),
        w.env.cr.savepoint(),
    ):
        oc.write({"employee_id": w.nasrin.id})
    unpaid = calculated(w, "2026-01-B")
    with pytest.raises(ValidationError, match="only a PAID payslip"), w.env.cr.savepoint():
        Off.create(
            {"correction_slip_id": slip_of(unpaid, w.karim).id, "amount": 10.0, "reason": "x"}
        )
    with (
        pytest.raises(ValidationError, match="Only a post-payment correction"),
        w.env.cr.savepoint(),
    ):
        Off.create(
            {
                "employee_id": w.karim.id,
                "payment_type": "arrear",
                "amount": 1.0,
                "correction_slip_id": slip.id,
            }
        )
    # routed, approved, released and booked like any off-cycle payment
    oc.action_request_approval()
    decide(w, oc, w.manager)
    with pytest.raises(UserError, match="can no longer be changed"), w.env.cr.savepoint():
        oc.write({"correction_slip_id": slip_of(p, w.nasrin).id})
    rel = w.as_(w.releaser)["fix.payroll.offcycle"].browse(oc.id)
    rel.action_pay()
    assert (
        rel.beftn_batch_id.total_amount == 1500.0 and KARIM_ACC in rel.beftn_batch_id.file_content
    )
    slip.invalidate_recordset()
    assert slip.net == net and slip.correction_offcycle_ids == oc


# ================================================================ M56-11 statutory pack


def test_the_seeded_pack_is_the_code_as_it_stood_and_every_slip_pins_it(w):
    base = w.env.ref("cd_payroll_bd.statutory_pack_v1_as_coded")
    assert (base.state, base.version, base.basis, base.company_id) == (
        "baseline",
        1,
        "as_coded",
        w.env["res.company"],
    )
    assert (base.ot_divisor_hours, base.exemption_ceiling) == (208.0, 450000.0)
    assert (base.tax_table_rule, base.separation_rule) == (
        "engine_fy2026_27",
        "engine_2026_amendment",
    )
    p = calculated(w)
    slip = slip_of(p, w.karim)
    assert slip.statutory_pack_id == base and slip.statutory_pack_version == 1
    assert "pack=v1 (as coded, unsourced)" in slip.statutory_basis
    # a plain write of the seed, or of a slip's pin, is refused
    with pytest.raises(UserError), w.env.cr.savepoint():
        w.as_(w.manager)["fix.statutory.pack"].browse(base.id).write({"ot_divisor_hours": 104.0})
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.payslip"].browse(slip.id).write({"statutory_pack_id": False})


def test_a_new_pack_needs_a_second_payroll_manager_and_applies_from_its_date(w):
    # an officer cannot prepare one
    with pytest.raises(AccessError, match="Only a Payroll Manager prepares"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.statutory.pack"].create(
            {"effective_from": PS, "ot_divisor_hours": 104.0, "exemption_ceiling": 450000.0}
        )
    Pack = w.as_(w.manager)["fix.statutory.pack"]
    # nor is one created already approved
    with pytest.raises(UserError, match="created as a draft"), w.env.cr.savepoint():
        Pack.create(
            {
                "effective_from": PS,
                "ot_divisor_hours": 104.0,
                "exemption_ceiling": 1.0,
                "state": "approved",
            }
        )
    v2 = Pack.create(
        {"effective_from": PS, "ot_divisor_hours": 104.0, "exemption_ceiling": 450000.0}
    )
    later = Pack.create(
        {
            "effective_from": date(2026, 2, 1),
            "ot_divisor_hours": 52.0,
            "exemption_ceiling": 450000.0,
        }
    )
    assert v2.version == 2 and later.version == 3 and v2.company_id == w.co
    # a sourced pack needs its citation and evidence
    v2.write({"basis": "sourced"})
    with pytest.raises(UserError, match="citation and the evidence"), w.env.cr.savepoint():
        v2.action_request_approval()
    v2.write({"source_note": "Finance Act 2026, Schedule 2 (test fixture)", "source_file": FILE})
    with pytest.raises(UserError, match="approver's inbox"), w.env.cr.savepoint():
        v2.action_approve()
    res = p03(
        w.as_(w.manager),
        "model_action",
        model="fix.statutory.pack",
        ids=[v2.id],
        method="action_request_approval",
    )
    assert res["success"], res
    v2.invalidate_recordset()
    # routed to the OTHER Payroll Manager only; the figures freeze while pending
    assert routed_to(w, v2) == w.manager2
    with pytest.raises(UserError, match="can no longer be changed"), w.env.cr.savepoint():
        v2.write({"ot_divisor_hours": 1.0})
    decide(w, v2, w.manager2)
    assert (v2.state, v2.approved_by_id) == ("approved", w.manager2) and v2.approved_digest
    with pytest.raises(UserError, match="can no longer be changed"), w.env.cr.savepoint():
        w.as_(w.manager2)["fix.statutory.pack"].browse(v2.id).write({"exemption_ceiling": 0.0})
    # January pays by v2 (its date); the February pack (still a draft) does not apply
    p = calculated(w)
    slip = slip_of(p, w.karim)
    assert slip.statutory_pack_id == v2 and slip.ot_divisor_hours == 104.0
    assert "pack=v2 (sourced)" in slip.statutory_basis


# ================================================================ FR-PAY-004 YTD TDS


def _expected_ytd_tax(slip, prior_income, prior_tax, months):
    """An independent working of the year-to-date method with the engine's
    own tax functions (no rate typed here)."""
    month = Decimal(str(slip.gross)) - Decimal(str(slip.pf_employee))
    projected = Decimal(str(prior_income)) + month * months
    exempt = salary_exemption(projected, ceiling=Decimal("450000"))
    annual = income_tax(
        projected - exempt,
        category=slip.taxpayer_category,
        location=slip.minimum_tax_location,
    )
    due = max(annual - Decimal(str(prior_tax)), Decimal(0))
    return float((due / months).quantize(Decimal("0.01")))


def test_ytd_tds_projects_the_fiscal_year_and_today_s_method_is_the_default(w):
    rahim = w.emp("R2 Rahim", 200000.0, "4242424242", "060274689")
    dec = _paid_december(w)
    dec_slip = slip_of(dec, rahim)
    # default: today's method (this month x 12) - January is withheld like December
    assert w.co.payroll_tds_method == "monthly_annualised"
    jan = calculated(w)
    monthly = slip_of(jan, rahim).tax_withheld
    assert monthly == dec_slip.tax_withheld > 0
    # the business chooses year-to-date: January takes what December paid into account
    w.co.sudo().payroll_tds_method = "ytd"
    jan.action_request_approval()
    task_of(w, jan, w.manager).action_reject("switching the TDS method")
    jan.action_calculate()
    slip = slip_of(jan, rahim)
    prior_income = dec_slip.gross - dec_slip.pf_employee
    assert (slip.tds_method, slip.fy_months_remaining) == ("ytd", 6)
    assert slip.ytd_prior_income == round(prior_income, 2)
    assert slip.ytd_prior_tax == dec_slip.tax_withheld
    expected = _expected_ytd_tax(slip, prior_income, dec_slip.tax_withheld, 6)
    assert slip.tax_withheld == expected and 0 < expected != monthly
    assert slip.net == round(slip.gross - slip.pf_employee - slip.tax_withheld, 2)
    # the method is pinned: changing the setting later does not recompute it
    w.co.sudo().payroll_tds_method = "monthly_annualised"
    slip.sudo()._compute_slip()
    assert slip.tax_withheld == expected
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.payslip"].browse(slip.id).write({"ytd_prior_tax": 0.0})


# ================================================================ FR-PAY-022 gratuity provision


def test_the_gratuity_provision_cron_accrues_once_per_employee_and_month(w):
    Accrual = w.env["fix.payroll.gratuity.accrual"].sudo()
    with pytest.raises(UserError, match="month end"), w.env.cr.savepoint():
        Accrual.cron_accrue_gratuity(as_of="2026-01-30")
    Accrual.cron_accrue_gratuity(as_of="2026-01-31")
    Accrual.cron_accrue_gratuity(as_of="2026-01-31")  # idempotent
    mine = Accrual.search([("employee_id", "in", (w.karim | w.nasrin).ids)])
    assert len(mine) == 2
    karim = mine.filtered(lambda r: r.employee_id == w.karim)
    # 6 completed years at 1,000 a day x 30 days (the existing separation rule)
    assert (karim.completed_years, karim.liability, karim.accrual) == (6, 180000.0, 180000.0)
    assert "pack=v1 (as coded, unsourced)" in karim.statutory_basis
    assert not karim.move_id  # finance has not configured the provision accounts
    # February: the movement is the difference only; the provision is posted
    # once finance configures the accounts
    w.co.write(
        {
            "payroll_gratuity_expense_account_id": _account(
                w.env, w.co, "6150", "Gratuity Expense", "expense"
            ).id,
            "payroll_gratuity_provision_account_id": _account(
                w.env, w.co, "2150", "Gratuity Provision", "liability_non_current"
            ).id,
        }
    )
    Accrual.cron_accrue_gratuity(as_of="2026-02-28")
    feb = Accrual.search([("employee_id", "=", w.karim.id), ("month", "=", "2026-02")])
    assert (feb.previous_liability, feb.accrual) == (180000.0, 0.0)
    # an officer reads the register but writes nothing on it
    row = w.as_(w.officer)["fix.payroll.gratuity.accrual"].browse(karim.id)
    assert row.liability == 180000.0
    with pytest.raises((AccessError, UserError)), w.env.cr.savepoint():
        row.write({"liability": 1.0})


def test_gratuity_provision_posts_the_movement_when_configured(w):
    w.co.write(
        {
            "payroll_gratuity_expense_account_id": _account(
                w.env, w.co, "6150", "Gratuity Expense", "expense"
            ).id,
            "payroll_gratuity_provision_account_id": _account(
                w.env, w.co, "2150", "Gratuity Provision", "liability_non_current"
            ).id,
        }
    )
    w.env["fix.payroll.gratuity.accrual"].sudo().cron_accrue_gratuity(as_of="2026-01-31")
    rows = w.env["fix.payroll.gratuity.accrual"].sudo().search([("company_id", "=", w.co.id)])
    move = rows.mapped("move_id")
    assert len(move) == 1 and move.state == "posted"
    lines = sorted((ln.account_id.code, ln.debit, ln.credit) for ln in move.line_ids)
    total = sum(rows.mapped("accrual"))
    assert lines == [("2150", 0.0, total), ("6150", total, 0.0)]


# ================================================================ M56-4 bank return and re-issue


def _csv(*rows):
    return base64.b64encode(("\n".join(rows) + "\n").encode()).decode()


def test_a_bank_return_marks_failed_items_and_finance_reissues_them(w):
    p = paid(w)
    batch = p.beftn_batch_id
    # an officer cannot record the bank's answer
    with pytest.raises(AccessError, match="Disbursement Releaser"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.beftn.return"].create({"batch_id": batch.id})
    Return = w.as_(w.releaser)["fix.beftn.return"]
    # an incomplete, unknown or malformed answer is refused, never half-applied
    for content, msg in (
        (_csv("account,status", "%s,failed" % KARIM_ACC), "does not answer every credit"),
        (
            _csv("account,status", "%s,failed" % KARIM_ACC, "%s,paid" % NASRIN_ACC, "999,paid"),
            "did not credit",
        ),
        (
            _csv("account,status", "%s,bounced" % KARIM_ACC, "%s,paid" % NASRIN_ACC),
            "neither paid nor failed",
        ),
        (_csv("acct,result", "%s,paid" % KARIM_ACC), "columns account and status"),
    ):
        bad = Return.create({"batch_id": batch.id, "return_file": content})
        with pytest.raises(UserError, match=msg), w.env.cr.savepoint():
            bad.action_import()
    ret = Return.create(
        {
            "batch_id": batch.id,
            "return_file": _csv(
                "account,status,reason",
                "%s,failed,Account closed" % KARIM_ACC,
                "%s,paid" % NASRIN_ACC,
            ),
        }
    )
    res = p03(
        w.as_(w.releaser),
        "model_action",
        model="fix.beftn.return",
        ids=[ret.id],
        method="action_import",
    )
    assert res["success"], res
    ret.invalidate_recordset()
    karim_net = slip_of(p, w.karim).net
    assert (ret.state, ret.paid_count, ret.failed_count, ret.failed_amount) == (
        "imported",
        1,
        1,
        karim_net,
    )
    failed = ret.line_ids.filtered(lambda ln: ln.status == "failed")
    assert (failed.employee_id, failed.reason) == (w.karim, "Account closed")
    # the master still holds the returned account: nothing is re-issued
    with (
        pytest.raises(UserError, match="still holds the account the bank returned"),
        w.env.cr.savepoint(),
    ):
        ret.action_reissue()
    # HR corrects the master (an approved master change; played as HR here)
    new_bank = (
        w.env["res.partner.bank"]
        .sudo()
        .create({"acc_number": "1501209999001", "partner_id": w.karim.work_contact_id.id})
    )
    w.karim.sudo().bank_account_ids = [Command.set([new_bank.id])]
    # the approver of the run may not release the re-issue, even holding the role
    w.manager.sudo().group_ids = [Command.link(w.env.ref("cd_payroll_bd.group_payroll_release").id)]
    with pytest.raises(UserError, match="Release SoD violation"), w.env.cr.savepoint():
        w.as_(w.manager)["fix.beftn.return"].browse(ret.id).action_reissue()
    with pytest.raises(AccessError, match="Disbursement Releaser"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.beftn.return"].browse(ret.id).action_reissue()
    res = p03(
        w.as_(w.releaser),
        "model_action",
        model="fix.beftn.return",
        ids=[ret.id],
        method="action_reissue",
    )
    assert res["success"], res
    ret.invalidate_recordset()
    reissue = ret.reissue_batch_ids
    assert len(reissue) == 1 and reissue.reissue_of_id == batch
    assert reissue.total_amount == karim_net and reissue.released_by_id == w.releaser
    assert "1501209999001" in reissue.file_content and NASRIN_ACC not in reissue.file_content
    with pytest.raises(UserError, match="no failed item left"), w.env.cr.savepoint():
        ret.action_reissue()
    # the imported answer is evidence
    with pytest.raises(UserError, match="can no longer be changed"), w.env.cr.savepoint():
        ret.write({"return_file": _csv("account,status")})


# ================================================================ bonus TDS


def test_bonus_tds_is_off_by_default_and_withholds_at_the_marginal_rate_when_ruled(w):
    Run = w.as_(w.officer)["fix.payroll.bonus.run"]
    run = Run.create({"festival": "eid_ul_fitr", "bonus_date": date(2026, 3, 20)})
    run.action_compute()
    assert run.total_tax == 0.0 and run.total_net == run.total_amount  # today
    run.action_cancel()
    w.co.sudo().payroll_bonus_tds = "marginal"
    run2 = Run.create({"festival": "eid_ul_fitr", "bonus_date": date(2026, 3, 21)})
    with (
        pytest.raises(UserError, match="no committed payslip to take the rate from"),
        w.env.cr.savepoint(),
    ):
        run2.action_compute()
    jan = paid(w)
    run2.action_compute()
    line = run2.line_ids.filtered(lambda ln: ln.employee_id == w.nasrin)
    slip = slip_of(jan, w.nasrin)
    rate = marginal_rate(slip.annual_taxable, slip.taxpayer_category)
    assert rate > 0 and line.marginal_rate == float(rate * 100)
    assert line.tax_withheld == round(line.amount * float(rate), 2)
    assert line.net_amount == round(line.amount - line.tax_withheld, 2)
    run2.action_request_approval()
    decide(w, run2, w.manager)
    rel = w.as_(w.releaser)["fix.payroll.bonus.run"].browse(run2.id)
    rel.action_pay()
    assert rel.beftn_batch_id.total_amount == rel.total_net
    rel.action_post()
    lines = sorted((ln.account_id.code, ln.debit, ln.credit) for ln in rel.gl_move_id.line_ids)
    assert lines == [
        ("2101", 0.0, rel.total_net),
        ("2102", 0.0, rel.total_tax),
        ("6101", rel.total_amount, 0.0),
    ]


# ================================================================ joiner proration


def test_a_joiner_is_prorated_by_calendar_days(w):
    joiner = w.emp("R2 Joins 16 Jan", 31000.0, "4141414141", "060274689", joining=date(2026, 1, 16))
    p = calculated(w)
    slip = slip_of(p, joiner)
    # 16 of 31 days: 31,000 x 16/31 = 16,000; the hourly rate is kept
    assert (slip.paid_days, slip.period_days, slip.basic) == (16, 31, 16000.0)
    assert (
        slip.ot_divisor_hours == round(208.0 * 16 / 31, 10)
        or abs(slip.ot_divisor_hours - 208.0 * 16 / 31) < 1e-6
    )
    assert "R2 Joins 16 Jan paid 16 of 31 days (joined 2026-01-16)" in p.calculation_note
    assert slip_of(p, w.karim).paid_days == 31


# ================================================================ MFS wallet salaries


def test_an_mfs_only_employee_is_paid_by_a_provider_file_not_beftn(w):
    mfs = w.emp("R2 Wallet Only", 20000.0)
    mfs.sudo().write({"mfs_provider": "bkash", "mfs_account_number": "01712345678"})
    p = calculated(w)
    slip = slip_of(p, mfs)
    assert (slip.payment_channel, slip.mfs_provider, slip.mfs_wallet) == (
        "mfs",
        "bkash",
        "01712345678",
    )
    assert not slip.bank_account_no
    p.action_request_approval()
    decide(w, p, w.manager)
    w.as_(w.releaser)["fix.payroll.period"].browse(p.id).action_pay()
    p.invalidate_recordset()
    batch = p.beftn_batch_id
    assert batch.total_amount == round(p.approved_net_total - slip.net, 2)
    assert "01712345678" not in batch.file_content
    disb = p.sudo().mfs_disbursement_ids
    assert len(disb) == 1 and disb.provider == "bkash" and disb.total_amount == slip.net
    assert "bkash,01712345678,%.2f,SALARY 2026-01" % slip.net in disb.file_content
    # settled by Finance against the provider's confirmation only
    with pytest.raises(AccessError), w.env.cr.savepoint():
        w.as_(w.officer)["fix.mfs.disbursement"].browse(disb.id).action_settle()
    rel = w.as_(w.releaser)["fix.mfs.disbursement"].browse(disb.id)
    with pytest.raises(UserError, match="provider's confirmation"), w.env.cr.savepoint():
        rel.action_settle()
    rel.write({"confirmation_ref": "BK-BULK-1", "confirmation_file": FILE})
    rel.action_settle()
    assert rel.state == "settled"


def test_a_wallet_changed_after_approval_is_never_paid(w):
    mfs = w.emp("R2 Wallet Diverted", 20000.0)
    mfs.sudo().write({"mfs_provider": "nagad", "mfs_account_number": "01812345678"})
    p = approved(w)
    # a tampered slip row (the guards stop this; played by SQL)
    w.env.cr.execute(
        "UPDATE fix_payslip SET mfs_wallet = '01999999999' WHERE id = %s", (slip_of(p, mfs).id,)
    )
    w.env.invalidate_all()
    with pytest.raises(UserError, match="does not match its approval"), w.env.cr.savepoint():
        w.as_(w.releaser)["fix.payroll.period"].browse(p.id).action_pay()


# ================================================================ M56-1 bank-change cool-off


def test_a_recent_bank_change_waits_for_a_second_person(w):
    # off (today): a fresh account is paid as before
    before = calculated(w)
    assert before.action_prevalidate() == {"issues": []}
    w.co.sudo().payroll_bank_cooloff_days = 7
    # a run calculated before the setting is told to recalculate
    with (
        pytest.raises(UserError, match=r"recalculate the run to raise its confirmation"),
        w.env.cr.savepoint(),
    ):
        before.action_request_approval()
    # the fixture registered both accounts today: inside the cool-off
    p = calculated(w, "2026-01-B")
    with (
        pytest.raises(UserError, match=r"R2 Karim's salary account changed on .* 7-day cool-off"),
        w.env.cr.savepoint(),
    ):
        p.action_request_approval()
    checks = p.sudo().bank_check_ids
    assert checks.mapped("employee_id") == w.karim | w.nasrin and set(checks.mapped("state")) == {
        "pending"
    }
    karim = checks.filtered(lambda c: c.employee_id == w.karim)
    assert karim.account_hint == "..." + KARIM_ACC[-4:]
    # neither the calculator nor a plain user confirms; nor is the state typed
    with pytest.raises(UserError, match="preparer or calculator"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.payroll.bank.check"].browse(karim.id).action_confirm()
    with pytest.raises(AccessError), w.env.cr.savepoint():
        w.as_(w.plain)["fix.payroll.bank.check"].browse(karim.id).action_confirm()
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.payroll.bank.check"].browse(karim.id).write({"state": "confirmed"})
    # whoever made the change does not confirm it
    karim.sudo()._guarded().write({"changed_by_ids": [Command.set([w.manager2.id])]})
    with pytest.raises(UserError, match="You made this bank change"), w.env.cr.savepoint():
        w.as_(w.manager2)["fix.payroll.bank.check"].browse(karim.id).action_confirm()
    res = p03(
        w.as_(w.manager),
        "model_action",
        model="fix.payroll.bank.check",
        ids=[karim.id],
        method="action_confirm",
        kwargs={"note": "Called the employee on the HR-held number"},
    )
    assert res["success"], res
    with pytest.raises(UserError, match="R2 Nasrin's salary account changed"), w.env.cr.savepoint():
        p.action_request_approval()
    w.as_(w.manager2)["fix.payroll.bank.check"].browse(
        checks.filtered(lambda c: c.employee_id == w.nasrin).id
    ).action_confirm()
    p.action_request_approval()
    assert p.approval_state == "pending"


# ================================================================ payslip PDF


def test_the_bengali_payslip_renders_to_pdf_for_its_owner(w):
    report = w.env["ir.actions.report"]
    if report.get_wkhtmltopdf_state() not in ("ok", "upgrade"):
        pytest.skip("wkhtmltopdf is not reachable from Odoo on this machine")
    # never let the renderer fetch assets from a running server (8069)
    w.env["ir.config_parameter"].sudo().set_param("report.url", "http://127.0.0.1:9")
    w.karim.sudo().user_id = w.plain.id
    p = paid(w)
    w.as_(w.officer)["fix.payroll.period"].browse(p.id).action_publish_payslips()
    me = w.as_(w.plain)["fix.payslip"]
    out = me.fix_my_payslip_pdf(slip_of(p, w.karim).id)
    pdf = base64.b64decode(out["pdf_base64"])
    assert pdf.startswith(b"%PDF") and len(pdf) > 1000
    assert out["filename"] == "Payslip_R2 Karim_2026-01.pdf"
    with pytest.raises(AccessError, match="only your own"), w.env.cr.savepoint():
        me.fix_my_payslip_pdf(slip_of(p, w.nasrin).id)


# ================================================================ M56-13 WPPF remainder


def _wppf(w, **vals):
    return w.as_(w.officer)["fix.wppf.allocation"].create(
        {
            "fiscal_year": "2025-2026",
            "fiscal_year_end_date": date(2026, 6, 30),
            "net_profit": 10_000_000.0,
            "trustee_board_resolution_ref": "TRUSTEE/26/1",
            "trustee_resolution_file": FILE,
            **vals,
        }
    )


def test_wppf_takes_the_audited_profit_with_evidence_and_lists_eligible_workers(w):
    a = _wppf(w)
    with pytest.raises(UserError, match="audited financial statements"), w.env.cr.savepoint():
        a.action_calculate()
    a.write({"audited_statement_file": FILE, "audit_report_ref": "AUDIT/FY26/1"})
    w.co.sudo().payroll_wppf_min_service_months = 6
    newbie = w.emp("R2 WPPF Newbie", 20000.0, joining=date(2026, 3, 1))
    a.action_calculate()
    lines = {ln.employee_id: ln for ln in a.beneficiary_ids}
    assert set(lines) == {w.karim, w.nasrin, newbie}
    assert lines[newbie].auto_excluded and "under the 6-month minimum" in lines[newbie].auto_reason
    assert a.eligible_workers_count == 2
    assert lines[w.karim].share_amount == round(266666.67 / 2, 2)
    # s.88: 10% withheld on the participant's payment
    assert lines[w.karim].tds_amount == round(lines[w.karim].share_amount * 0.10, 2)
    # payroll classifies a non-worker, with a reason; the head count follows
    line = w.as_(w.officer)["fix.wppf.beneficiary"].browse(lines[w.nasrin].id)
    with pytest.raises(UserError, match="State why"), w.env.cr.savepoint():
        line.write({"worker_status": "excluded"})
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        line.write({"service_months": 99})
    line.write({"worker_status": "excluded", "exclusion_reason": "Branch manager (administrative)"})
    a.invalidate_recordset()
    assert a.eligible_workers_count == 1 and lines[w.karim].share_amount == 266666.67
    with (
        pytest.raises(UserError, match=r"can no longer be changed|cannot be set directly"),
        w.env.cr.savepoint(),
    ):
        a.write({"eligible_workers_count": 50})
    a.action_request_approval()
    with pytest.raises(UserError, match=r"before\s+the trustees are asked"), w.env.cr.savepoint():
        line.write({"worker_status": "worker"})
    decide(w, a, w.manager)
    assert a.state == "approved" and a.approved_digest
    # the BWWF 10% share: paid by Finance with the challan, never by its approver
    with pytest.raises(AccessError), w.env.cr.savepoint():
        a.action_pay_bwwf()
    w.manager.sudo().group_ids = [Command.link(w.env.ref("cd_payroll_bd.group_payroll_release").id)]
    with pytest.raises(UserError, match="Release SoD violation"), w.env.cr.savepoint():
        w.as_(w.manager)["fix.wppf.allocation"].browse(a.id).action_pay_bwwf()
    rel = w.as_(w.releaser)["fix.wppf.allocation"].browse(a.id)
    with pytest.raises(UserError, match="BWWF deposit challan"), w.env.cr.savepoint():
        rel.action_pay_bwwf()
    a.write(
        {
            "bwwf_challan_ref": "BWWF/26/7",
            "bwwf_challan_date": date(2026, 9, 1),
            "bwwf_challan_file": FILE,
        }
    )
    with pytest.raises(UserError, match="Configure the payroll accounting"), w.env.cr.savepoint():
        rel.action_pay_bwwf()
    w.co.write(
        {
            "payroll_wppf_payable_account_id": _account(
                w.env, w.co, "2190", "WPPF Payable", "liability_current"
            ).id,
            "payroll_wppf_bank_account_id": _account(
                w.env, w.co, "1190", "WPPF Bank", "asset_cash"
            ).id,
        }
    )
    rel.action_pay_bwwf()
    assert rel.bwwf_paid_by_id == w.releaser
    lines = sorted((ln.account_id.code, ln.debit, ln.credit) for ln in rel.bwwf_move_id.line_ids)
    assert lines == [("1190", 0.0, 50000.0), ("2190", 50000.0, 0.0)]
    with pytest.raises(UserError, match="can no longer be changed"), w.env.cr.savepoint():
        a.write({"bwwf_challan_ref": "OTHER"})


# ================================================================ I8 / I9 (M55 interfaces)


class _StandInAdjustment:
    """Stand-in for M55's fix.attendance.adjustment (r2e) while it is not
    installed: the fields of interface I8 and its _fix_consume(slip) hook."""

    def __init__(self, kind, quantity=0.0, amount=0.0, month="2025-12"):
        self.kind, self.quantity, self.amount, self.period_month = kind, quantity, amount, month
        self.consumed_on = []

    def _fix_consume(self, slip):
        self.consumed_on.append(slip.id)


def _adjustments(w, employee, specs):
    """Real fix.attendance.adjustment rows when M55 has shipped them, else the
    stand-in (tests only)."""
    if "fix.attendance.adjustment" in w.env:
        Adj = w.env["fix.attendance.adjustment"].sudo()
        recs = Adj.browse()
        for kind, qty, amount in specs:
            rec = Adj.create(
                {
                    "employee_id": employee.id,
                    "company_id": w.co.id,
                    "date": date(2025, 12, 10),
                    "period_month": "2025-12",
                    "kind": kind,
                    "quantity": qty,
                    "amount": amount,
                }
            )
            w.env.cr.execute(
                "UPDATE fix_attendance_adjustment SET state = 'approved' WHERE id = %s", (rec.id,)
            )
            recs |= rec
        w.env.invalidate_all()
        return recs, None
    stand_ins = [_StandInAdjustment(kind, qty, amount) for kind, qty, amount in specs]

    def fake(self, emp, released):
        return (
            [a for a in stand_ins if not a.consumed_on or a.consumed_on[-1] in released]
            if emp == employee
            else []
        )

    return stand_ins, mock.patch.object(FixPayrollPeriod, "_attendance_adjustments", fake)


def test_approved_retro_adjustments_are_paid_once_with_the_existing_formulas(w):
    specs = [
        ("overtime_hours", 4.0, 0.0),
        ("absence_days", 2.0, 0.0),
        ("oncall_allowance", 0.0, 800.0),
    ]
    adjustments, patch = _adjustments(w, w.karim, specs)
    with patch or contextlib.nullcontext():
        p = new_period(w)
        p.action_trial_run()  # a trial consumes nothing
        if patch:
            assert not any(a.consumed_on for a in adjustments)
        p.action_verify_attendance_locked()
        p.action_calculate()
        slip = slip_of(p, w.karim)
        # overtime: 30,000 / 208 x 2 x 4 = 1,153.85; absence: 30,000 / 30 x 2 = 2,000
        assert slip.retro_overtime_amount == 1153.85 and slip.retro_absence_deduction == 2000.0
        assert slip.retro_oncall_amount == 800.0
        assert slip.retro_adjustment_total == round(1153.85 + 800.0 - 2000.0, 2)
        assert slip.other_allowance == slip.retro_adjustment_total
        assert "R2 Karim retro adjustments 2025-12" in p.calculation_note
        if patch:
            assert all(a.consumed_on == [slip.id] for a in adjustments)
        else:
            adjustments.invalidate_recordset()
            assert set(adjustments.mapped("state")) == {"consumed"}
        # a second run of the month does not pay them again
        other = calculated(w, "2026-01-B")
        assert slip_of(other, w.karim).retro_adjustment_total == 0.0
        # nor can a payroll officer retype them on the slip
        with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
            w.as_(w.officer)["fix.payslip"].browse(slip.id).write({"retro_adjustment_total": 0.0})


def test_retro_overtime_is_not_paid_to_an_ineligible_employee(w):
    _adjustments_made, patch = _adjustments(w, w.karim, [("overtime_hours", 4.0, 0.0)])
    w.karim.sudo().overtime_eligible = False
    with patch or contextlib.nullcontext():
        p = calculated(w)
        assert slip_of(p, w.karim).retro_overtime_amount == 0.0
        assert "R2 Karim retro overtime 4.0 h (2025-12) not paid" in p.calculation_note


def test_the_approved_on_call_allowance_is_what_is_paid(w):
    OnCall = w.env["fix.hr.oncall"].sudo()
    shift = OnCall.create(
        {
            "employee_id": w.karim.id,
            "company_id": w.co.id,
            "date_from": datetime(2026, 1, 9, 18, 0),
            "date_to": datetime(2026, 1, 10, 8, 0),
            "allowance": 1500.0,
        }
    )
    shift.action_start()
    shift.action_complete()
    if "approved_allowance" in OnCall._fields:
        # I9: M55 approved 1,200 of the 1,500 asked (a database write here)
        w.env.cr.execute(
            "UPDATE fix_hr_oncall SET approved_allowance = 1200 WHERE id = %s", (shift.id,)
        )
        w.env.invalidate_all()
        expected = 1200.0
    else:
        # r2e's approved_allowance is not installed yet: today's behaviour
        expected = 1500.0
    p = calculated(w)
    assert slip_of(p, w.karim).oncall_allowance == expected


# ================================================================ BLA s.19 death in service


def test_death_benefit_is_30_days_a_year_45_at_work_or_the_gratuity_if_higher():
    joined = date(2020, 1, 1)
    # 6 completed years at 1,000 a day: 30 days x 6 = 180,000 (equal to the
    # gratuity, so the s.19 benefit stands)
    _y, lines = separation_figures(
        30000.0, joined, date(2026, 1, 31), "death", death_min_service_years=2.0
    )
    assert [(k, a) for k, _l, a in lines] == [("service_compensation", 180000)]
    # a part year above six months counts as a year: 6 y 7 m -> 7 x 30 days
    _y, lines = separation_figures(
        30000.0, joined, date(2026, 8, 15), "death", death_min_service_years=2.0
    )
    assert [(k, a) for k, _l, a in lines] == [("service_compensation", 210000)]
    # death at work: 45 days a year, 6 x 45 x 1,000
    _y, lines = separation_figures(
        30000.0, joined, date(2026, 1, 31), "death", death_min_service_years=2.0, death_at_work=True
    )
    assert [(k, a) for k, _l, a in lines] == [("service_compensation", 270000)]
    assert "45 days per year of service - death at work (BLA s.19)" in lines[0][1]
    # under the minimum service: no s.19 benefit beyond the gratuity
    _y, lines = separation_figures(
        30000.0, joined, date(2026, 1, 31), "death", death_min_service_years=10.0
    )
    assert [(k, a) for k, _l, a in lines] == [("gratuity", 180000)]
    _y, lines = separation_figures(
        30000.0, date(2025, 1, 1), date(2026, 1, 31), "death", death_min_service_years=2.0
    )
    assert lines == []  # one year: no benefit, no gratuity (engine vests at 5 years)
    # leave encashment through I2 rides on top
    _y, lines = separation_figures(
        30000.0,
        joined,
        date(2026, 1, 31),
        "death",
        unused_leave_days=10.0,
        death_min_service_years=2.0,
    )
    assert {k: a for k, _l, a in lines}["leave_encashment"] == 10000
    # the minimum is the company setting, never a default here
    with pytest.raises(UserError, match=r"s.19 minimum service"):
        separation_figures(30000.0, joined, date(2026, 1, 31), "death")


def _death_exit(w, employee, last_day, at_work=False, min_years=2.0):
    """A death exit. M21's death type and setting are used when installed;
    in this package's own database (before the M21 round-2 merge) the exit
    type and the two M21 inputs are played (SQL / a patch)."""
    ex = (
        w.env["fix.hr.exit"]
        .sudo()
        .create(
            {
                "employee_id": employee.id,
                "company_id": w.co.id,
                "exit_type": "resignation",
                "last_working_day": last_day,
            }
        )
    )
    w.env.cr.execute("UPDATE fix_hr_exit SET exit_type = 'death' WHERE id = %s", (ex.id,))
    company = w.co.sudo()
    if "fix_hr_death_benefit_min_service_years" in company._fields:
        company.fix_hr_death_benefit_min_service_years = min_years
        w.env.cr.execute(
            "UPDATE fix_hr_exit SET death_at_work = %s WHERE id = %s", (at_work, ex.id)
        )
        patch = contextlib.nullcontext()
    else:
        patch = mock.patch.object(
            fix_payroll_settlement, "death_rules", lambda _exit: (min_years, at_work)
        )
    w.env.invalidate_all()
    return ex, patch


def test_a_death_exit_settles_to_two_nominees_at_60_40(w):
    Dep = w.env["fix.hr.dependant"].sudo()
    wife = Dep.create(
        {
            "employee_id": w.karim.id,
            "name": "R2 Ayesha",
            "relation": "spouse",
            "is_nominee": True,
            "nominee_pct": 60.0,
        }
    )
    son = Dep.create(
        {
            "employee_id": w.karim.id,
            "name": "R2 Rafi",
            "relation": "child",
            "is_nominee": True,
            "nominee_pct": 40.0,
        }
    )
    ex, patch = _death_exit(w, w.karim, date(2026, 1, 31))
    with patch:
        net = ex._fix_settlement_breakdown()["net"]
        unused = w.karim.sudo()._fix_unused_annual_leave_days(as_of=date(2026, 1, 31))
        assert net == round(180000.0 + 1000.0 * unused, 2)
        payees = [
            {
                "dependant_id": wife.id,
                "name": "R2 Ayesha",
                "relation": "spouse",
                "share_pct": 60.0,
                "amount": round(net * 0.6, 2),
            },
            {
                "dependant_id": son.id,
                "name": "R2 Rafi",
                "relation": "child",
                "share_pct": 40.0,
                "amount": round(net - round(net * 0.6, 2), 2),
            },
        ]
        ex.sudo().write({"state": "settled", "settlement_amount": net})
        Exit = type(w.env["fix.hr.exit"])
        own = "_fix_nominee_payees" in Exit.__dict__
        pin = (
            mock.patch.object(Exit, "_fix_nominee_payees", lambda self: payees, create=True)
            if not hasattr(Exit, "_fix_nominee_payees") or not own
            else contextlib.nullcontext()
        )
        if hasattr(Exit, "_fix_nominee_payees") and own:
            # M21 installed: its pin is the source of the split
            ex.sudo()._guarded().write({"nominee_payout_lines": json.dumps(payees)})
        with pin:
            ids = ex.with_user(w.officer).action_create_settlement_payment()["offcycle_ids"]
            ocs = w.as_(w.officer)["fix.payroll.offcycle"].browse(ids).sorted("nominee_share_pct")
            assert [(o.nominee_name, o.nominee_share_pct, o.amount) for o in ocs] == [
                ("R2 Rafi", 40.0, payees[1]["amount"]),
                ("R2 Ayesha", 60.0, payees[0]["amount"]),
            ]
            assert set(ocs.mapped("employee_id")) == {w.karim} and sum(ocs.mapped("amount")) == net
            # the payee and share are the pin's, never typed
            with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
                ocs[0].write({"nominee_name": "Somebody Else"})
            # no account for the nominee: created, but refused at pre-validation
            ayesha = ocs.filtered(lambda o: o.nominee_name == "R2 Ayesha")
            with (
                pytest.raises(UserError, match="Nominee R2 Ayesha has no registered account"),
                w.env.cr.savepoint(),
            ):
                ayesha.action_request_approval()
            # payroll records the nominee's account; a SECOND payroll user verifies it
            acc = w.as_(w.officer)["fix.payroll.nominee.account"].create(
                {
                    "employee_id": w.karim.id,
                    "dependant_id": wife.id,
                    "nominee_name": "R2 Ayesha",
                    "bank_account_no": "3303303303",
                    "routing_no": "060274689",
                    "evidence_file": FILE,
                }
            )
            with pytest.raises(UserError, match="second payroll user"), w.env.cr.savepoint():
                acc.action_verify()
            with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
                acc.write({"state": "verified"})
            w.as_(w.manager2)["fix.payroll.nominee.account"].browse(acc.id).action_verify()
            with pytest.raises(UserError, match="can no longer be changed"), w.env.cr.savepoint():
                acc.write({"bank_account_no": "9999999999"})
            ayesha.action_request_approval()
            assert (ayesha.bank_account_no, ayesha.nominee_account_id) == ("3303303303", acc)
            decide(w, ayesha, w.manager)
            rel = w.as_(w.releaser)["fix.payroll.offcycle"].browse(ayesha.id)
            rel.action_pay()
            content = rel.beftn_batch_id.file_content
            assert "3303303303" in content and "R2 Ayesha" in content and KARIM_ACC not in content


def test_a_death_exit_under_the_minimum_service_pays_only_the_gratuity_and_at_work_45(w):
    ex, patch = _death_exit(w, w.karim, date(2026, 1, 31), min_years=10.0)
    with patch:
        lines = dict(ex._fix_settlement_breakdown()["lines"])
    assert lines.pop("Gratuity (engine bands)") == 180000.0
    assert not [label for label in lines if "BLA s.19" in label]
    work, patch = _death_exit(w, w.nasrin, date(2026, 1, 31), at_work=True)
    with patch:
        out = work._fix_settlement_breakdown()
    # Nasrin: 6 years at 2,000 a day x 45 days
    assert (
        dict(out["lines"])["Death benefit, 45 days per year of service - death at work (BLA s.19)"]
        == 540000.0
    )


# ================================================================ second pass: branch dimension


def test_two_branches_of_one_unit_post_separate_balanced_groups(w):
    entity = w.env["fix.entity"].create(
        {"code": "R2E%d" % w.co.id, "legal_name": "R2 Payroll Entity", "company_id": w.co.id}
    )
    Branch = w.env["fix.branch"]
    b1 = Branch.create(
        {
            "name": "R2 Motijheel",
            "code": "R2B1%d" % w.co.id,
            "entity_id": entity.id,
            "operating_unit_id": w.ou.id,
        }
    )
    b2 = Branch.create(
        {
            "name": "R2 Uttara",
            "code": "R2B2%d" % w.co.id,
            "entity_id": entity.id,
            "operating_unit_id": w.ou.id,
        }
    )
    rahim = w.emp("R2 Rahim Uttara", 40000.0, "4343434343", "060274689", operating_unit_id=w.ou.id)
    w.karim.sudo().branch_id = b1.id
    rahim.sudo().branch_id = b2.id
    p = paid(w)
    assert (slip_of(p, w.karim).cost_branch_id, slip_of(p, rahim).cost_branch_id) == (b1, b2)
    w.as_(w.manager2)["fix.payroll.period"].browse(p.id).action_post()
    p.invalidate_recordset()
    move = p.gl_move_id
    dims = w.env["fix.journal.dimension"].sudo().search([("move_line_id", "in", move.line_ids.ids)])
    key = {d.move_line_id.id: (d.operating_unit_id, d.branch_id) for d in dims}
    groups = {}
    for line in move.line_ids:
        g = groups.setdefault(key[line.id], [0.0, 0.0, 0.0])
        g[0] += line.debit
        g[1] += line.credit
        if line.account_id.code == "2101":
            g[2] += line.credit
    # one unit, two branches: two groups there, plus Nasrin's unit with no branch
    assert set(groups) == {(w.ou, b1), (w.ou, b2), (w.ou2, w.env["fix.branch"])}
    for k, (debit, credit, _net) in groups.items():
        assert round(debit, 2) == round(credit, 2), k
    assert groups[(w.ou, b1)][2] == slip_of(p, w.karim).net
    assert groups[(w.ou, b2)][2] == slip_of(p, rahim).net


def test_cost_centres_of_one_unit_post_separate_balanced_groups(w):
    """FR-PAY-053: pay is booked to the employee's cost centre - the
    department's, or the employee's own override - as the GL's cost_centre
    dimension, and each cost-centre group balances."""
    Dept = w.env["hr.department"].sudo()
    service = Dept.create({"name": "R2 Field Service", "fix_cost_centre": "CC-FS"})
    workshop = Dept.create({"name": "R2 Workshop", "fix_cost_centre": "CC-WS"})
    rahim = w.emp("R2 Rahim CC", 40000.0, "4343434344", "060274689", operating_unit_id=w.ou.id)
    w.karim.sudo().department_id = service.id
    rahim.sudo().department_id = workshop.id
    seconded = w.emp("R2 Salma CC", 30000.0, "4343434345", "060274689", operating_unit_id=w.ou.id)
    seconded.sudo().write({"department_id": workshop.id, "fix_cost_centre": "CC-FS"})
    p = paid(w)
    assert (
        slip_of(p, w.karim).cost_centre,
        slip_of(p, rahim).cost_centre,
        slip_of(p, seconded).cost_centre,
    ) == ("CC-FS", "CC-WS", "CC-FS")
    # the pinned cost centre is the slip's, never typed (guarded, and the paid
    # slip is frozen besides)
    with pytest.raises(UserError, match="cannot be set directly|frozen"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.payslip"].browse(slip_of(p, rahim).id).write({"cost_centre": "CC-FS"})
    w.as_(w.manager2)["fix.payroll.period"].browse(p.id).action_post()
    p.invalidate_recordset()
    move = p.gl_move_id
    dims = w.env["fix.journal.dimension"].sudo().search([("move_line_id", "in", move.line_ids.ids)])
    key = {d.move_line_id.id: (d.operating_unit_id, d.cost_centre or False) for d in dims}
    groups = {}
    for line in move.line_ids:
        g = groups.setdefault(key[line.id], [0.0, 0.0, 0.0])
        g[0] += line.debit
        g[1] += line.credit
        if line.account_id.code == "2101":
            g[2] += line.credit
    assert (w.ou, "CC-FS") in groups and (w.ou, "CC-WS") in groups
    for k, (debit, credit, _net) in groups.items():
        assert round(debit, 2) == round(credit, 2), k
    assert groups[(w.ou, "CC-WS")][2] == slip_of(p, rahim).net
    assert groups[(w.ou, "CC-FS")][2] == round(
        slip_of(p, w.karim).net + slip_of(p, seconded).net, 2
    )


# ================================================================ second pass: overpayment recovery


def _lock_month(w, start, end, name):
    lock = w.env["fix.attendance.lock"].create(
        {"name": name, "period_start": start, "period_end": end}
    )
    lock.action_lock()
    return lock


def test_an_overpayment_is_recovered_from_the_next_runs_within_the_monthly_cap(w):
    jan = paid(w)
    slip = slip_of(jan, w.karim)
    jan_net = slip.net
    Rec = w.as_(w.officer)["fix.payroll.recovery"]
    with pytest.raises(AccessError), w.env.cr.savepoint():
        w.as_(w.plain)["fix.payroll.recovery"].create(
            {"correction_slip_id": slip.id, "amount": 1.0, "reason": "x"}
        )
    with pytest.raises(ValidationError, match="exceeds"), w.env.cr.savepoint():
        Rec.create({"correction_slip_id": slip.id, "amount": jan_net + 1, "reason": "x"})
    unpaid = calculated(w, "2026-01-B")
    with pytest.raises(ValidationError, match="Only a PAID payslip"), w.env.cr.savepoint():
        Rec.create(
            {"correction_slip_id": slip_of(unpaid, w.karim).id, "amount": 10.0, "reason": "x"}
        )
    rec = Rec.create(
        {
            "correction_slip_id": slip.id,
            "amount": 5000.0,
            "reason": "Night allowance paid twice in January",
        }
    )
    assert rec.employee_id == w.karim
    # not deducted until approved: routed to a Payroll Manager, never the preparer
    with pytest.raises(UserError, match="approver's inbox"), w.env.cr.savepoint():
        rec.action_approve()
    res = p03(
        w.as_(w.officer),
        "model_action",
        model="fix.payroll.recovery",
        ids=[rec.id],
        method="action_request_approval",
    )
    assert res["success"], res
    rec.invalidate_recordset()
    assert w.officer not in routed_to(w, rec)
    with pytest.raises(UserError, match="can no longer be changed"), w.env.cr.savepoint():
        rec.write({"amount": 1.0})
    decide(w, rec, w.manager)
    assert rec.state == "approved"
    # the business caps one month's recovery at 2,000
    w.co.sudo().payroll_recovery_monthly_cap = 2000.0
    _lock_month(w, date(2026, 2, 1), date(2026, 2, 28), "Feb 2026")
    feb = calculated(w, "2026-02", date(2026, 2, 1), date(2026, 2, 28))
    fslip = slip_of(feb, w.karim)
    assert fslip.recovery_deduction == 2000.0
    assert fslip.net == round(fslip.gross - fslip.pf_employee - fslip.tax_withheld - 2000.0, 2)
    assert "R2 Karim overpayment recovery 2000.00 deducted" in feb.calculation_note
    rec.invalidate_recordset()
    assert (rec.recovered_amount, rec.remaining_amount) == (2000.0, 3000.0)
    # a recalculation releases the run's recovery and takes it once again
    feb.action_request_approval()
    task_of(w, feb, w.manager).action_reject("recalculate")
    feb.action_calculate()
    rec.invalidate_recordset()
    assert (rec.recovered_amount, rec.remaining_amount) == (2000.0, 3000.0)
    # the paid January slip itself never changed
    slip.invalidate_recordset()
    assert slip.net == jan_net and not slip.recovery_deduction
    # nor is a deduction typed on a slip
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.payslip"].browse(slip_of(feb, w.karim).id).write(
            {"recovery_deduction": 0.0}
        )
    # posting books the recovery once finance names the account
    feb.action_request_approval()
    decide(w, feb, w.manager)
    w.as_(w.releaser)["fix.payroll.period"].browse(feb.id).action_pay()
    poster = w.as_(w.manager2)["fix.payroll.period"].browse(feb.id)
    with pytest.raises(UserError, match="Overpayment Recovery Account"), w.env.cr.savepoint():
        poster.action_post()
    w.co.payroll_recovery_account_id = _account(
        w.env, w.co, "1201", "Employee Receivable", "asset_receivable"
    ).id
    poster.action_post()
    feb.invalidate_recordset()
    rec_line = feb.gl_move_id.line_ids.filtered(lambda ln: ln.account_id.code == "1201")
    assert rec_line.credit == 2000.0
    # cap 0: the whole balance in the next run
    w.co.sudo().payroll_recovery_monthly_cap = 0.0
    _lock_month(w, date(2026, 3, 1), date(2026, 3, 31), "Mar 2026")
    mar = calculated(w, "2026-03", date(2026, 3, 1), date(2026, 3, 31))
    assert slip_of(mar, w.karim).recovery_deduction == 3000.0
    rec.invalidate_recordset()
    assert rec.fully_recovered and rec.remaining_amount == 0.0
    with pytest.raises(UserError, match="already been partly recovered"), w.env.cr.savepoint():
        w.as_(w.manager)["fix.payroll.recovery"].browse(rec.id).action_cancel()


# ================================================================ second pass: MFS off-cycle and bonus


def test_an_offcycle_payment_to_a_wallet_only_employee_is_an_mfs_file(w):
    mfs = w.emp("R2 Wallet Arrear", 20000.0)
    mfs.sudo().write({"mfs_provider": "bkash", "mfs_account_number": "01712345670"})
    oc = w.as_(w.officer)["fix.payroll.offcycle"].create(
        {"employee_id": mfs.id, "payment_type": "arrear", "amount": 3500.0}
    )
    oc.action_request_approval()
    assert (oc.payment_channel, oc.mfs_provider, oc.mfs_wallet) == ("mfs", "bkash", "01712345670")
    with pytest.raises(UserError, match="cannot be set directly"), w.env.cr.savepoint():
        oc.write({"mfs_wallet": "01999999999"})
    decide(w, oc, w.manager)
    rel = w.as_(w.releaser)["fix.payroll.offcycle"].browse(oc.id)
    rel.action_pay()
    disb = w.env["fix.mfs.disbursement"].sudo().search([("offcycle_id", "=", oc.id)])
    assert rel.state == "paid" and not rel.beftn_batch_id
    assert disb.total_amount == 3500.0 and "bkash,01712345670,3500.00,OFFCYCLE" in disb.file_content
    # a wallet changed while approval was pending is never paid
    other = w.as_(w.officer)["fix.payroll.offcycle"].create(
        {"employee_id": mfs.id, "payment_type": "arrear", "amount": 100.0}
    )
    other.action_request_approval()
    mfs.sudo().mfs_account_number = "01812345670"
    with pytest.raises(UserError, match="bank details changed"), w.env.cr.savepoint():
        decide(w, other, w.manager)


def test_a_festival_bonus_pays_wallets_by_mfs_file_and_banks_by_beftn(w):
    mfs = w.emp("R2 Wallet Bonus", 20000.0)
    mfs.sudo().write({"mfs_provider": "nagad", "mfs_account_number": "01612345670"})
    run = w.as_(w.officer)["fix.payroll.bonus.run"].create(
        {"festival": "eid_ul_fitr", "bonus_date": date(2026, 3, 20)}
    )
    run.action_compute()
    line = run.line_ids.filtered(lambda ln: ln.employee_id == mfs)
    assert (line.payment_channel, line.mfs_wallet) == ("mfs", "01612345670")
    run.action_request_approval()
    decide(w, run, w.manager)
    rel = w.as_(w.releaser)["fix.payroll.bonus.run"].browse(run.id)
    rel.action_pay()
    assert rel.beftn_batch_id.total_amount == round(rel.total_net - line.net_amount, 2)
    assert "01612345670" not in rel.beftn_batch_id.file_content
    disb = w.env["fix.mfs.disbursement"].sudo().search([("bonus_run_id", "=", run.id)])
    assert disb.provider == "nagad" and disb.total_amount == line.net_amount
    assert "nagad,01612345670,%.2f,BONUS" % line.net_amount in disb.file_content


# ================================================================ second pass: MFS return and re-issue


def test_an_mfs_return_marks_failed_wallets_and_finance_reissues_them(w):
    mfs = w.emp("R2 Wallet Return", 20000.0)
    mfs.sudo().write({"mfs_provider": "bkash", "mfs_account_number": "01712345671"})
    p = paid(w)
    disb = p.sudo().mfs_disbursement_ids
    with pytest.raises(AccessError, match="Disbursement Releaser"), w.env.cr.savepoint():
        w.as_(w.officer)["fix.mfs.return"].create({"disbursement_id": disb.id})
    Ret = w.as_(w.releaser)["fix.mfs.return"]
    bad = Ret.create(
        {"disbursement_id": disb.id, "return_file": _csv("wallet,status", "01700000000,failed")}
    )
    with pytest.raises(UserError, match="did not credit"), w.env.cr.savepoint():
        bad.action_import()
    ret = Ret.create(
        {
            "disbursement_id": disb.id,
            "return_file": _csv(
                "wallet,status,reason", "01712345671,failed,Wallet not KYC-verified"
            ),
        }
    )
    res = p03(
        w.as_(w.releaser),
        "model_action",
        model="fix.mfs.return",
        ids=[ret.id],
        method="action_import",
    )
    assert res["success"], res
    ret.invalidate_recordset()
    net = slip_of(p, mfs).net
    assert (ret.failed_count, ret.failed_amount) == (1, net)
    with (
        pytest.raises(UserError, match="still holds the wallet the provider returned"),
        w.env.cr.savepoint(),
    ):
        ret.action_reissue()
    mfs.sudo().mfs_account_number = "01712345672"  # HR's approved master change, played here
    w.manager.sudo().group_ids = [Command.link(w.env.ref("cd_payroll_bd.group_payroll_release").id)]
    with pytest.raises(UserError, match="Release SoD violation"), w.env.cr.savepoint():
        w.as_(w.manager)["fix.mfs.return"].browse(ret.id).action_reissue()
    ret.action_reissue()
    ret.invalidate_recordset()
    new = ret.reissue_ids
    assert len(new) == 1 and new.reissue_of_id == disb and new.total_amount == net
    assert "01712345672" in new.file_content and "01712345671" not in new.file_content
    with pytest.raises(UserError, match="no failed item left"), w.env.cr.savepoint():
        ret.action_reissue()


# ================================================================ finance events


def _outbox(w, event_type, aggregate_id):
    rows = (
        w.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)])
    )
    return [json.loads(r.payload) for r in rows]


def test_payroll_bonus_posted_carries_the_tax_per_operating_unit(w):
    paid(w)  # the committed slips the marginal rate is read from
    w.co.sudo().payroll_bonus_tds = "marginal"
    run = w.as_(w.officer)["fix.payroll.bonus.run"].create(
        {"festival": "eid_ul_fitr", "bonus_date": date(2026, 3, 20)}
    )
    run.action_compute()
    run.action_request_approval()
    decide(w, run, w.manager)
    rel = w.as_(w.releaser)["fix.payroll.bonus.run"].browse(run.id)
    rel.action_pay()
    assert _outbox(w, "payroll.bonus_posted", run.id) == []
    rel.action_post()
    karim = run.line_ids.filtered(lambda ln: ln.employee_id == w.karim)
    nasrin = run.line_ids.filtered(lambda ln: ln.employee_id == w.nasrin)
    assert rel.total_tax > 0
    assert _outbox(w, "payroll.bonus_posted", run.id) == [
        {
            "company_id": w.co.id,
            "bonus_run_id": run.id,
            "move_id": rel.gl_move_id.id,
            "period_end": "2026-03-20",
            "tax_total": rel.total_tax,
            "by_operating_unit": [
                {"operating_unit_id": w.ou.id, "gross": karim.amount, "tax": karim.tax_withheld},
                {"operating_unit_id": w.ou2.id, "gross": nasrin.amount, "tax": nasrin.tax_withheld},
            ],
        }
    ]
    payload = _outbox(w, "payroll.bonus_posted", run.id)[0]
    assert round(sum(r["tax"] for r in payload["by_operating_unit"]), 2) == payload["tax_total"]


def test_payroll_beftn_returned_is_published_once_for_a_failed_bank_item(w):
    p = paid(w)
    batch = p.beftn_batch_id
    Return = w.as_(w.releaser)["fix.beftn.return"]
    clean = Return.create(
        {
            "batch_id": batch.id,
            "return_file": _csv("account,status", "%s,paid" % KARIM_ACC, "%s,paid" % NASRIN_ACC),
        }
    )
    clean.action_import()
    assert _outbox(w, "payroll.beftn_returned", clean.id) == []  # nothing failed
    # a second, failing answer for the same batch is refused; play it on a fresh run
    p2 = paid(w, "2026-01-B")
    ret = Return.create(
        {
            "batch_id": p2.beftn_batch_id.id,
            "return_file": _csv("account,status", "%s,failed" % KARIM_ACC, "%s,paid" % NASRIN_ACC),
        }
    )
    ret.action_import()
    assert _outbox(w, "payroll.beftn_returned", ret.id) == [
        {
            "company_id": w.co.id,
            "channel": "beftn",
            "batch_id": p2.beftn_batch_id.id,
            "mfs_disbursement_id": False,
            "return_id": ret.id,
            "failed_amount": slip_of(p2, w.karim).net,
            "failed_count": 1,
        }
    ]


def test_payroll_beftn_returned_is_published_once_for_a_failed_wallet(w):
    mfs = w.emp("R2 Wallet Event", 20000.0)
    mfs.sudo().write({"mfs_provider": "bkash", "mfs_account_number": "01712345673"})
    p = paid(w)
    disb = p.sudo().mfs_disbursement_ids
    ret = w.as_(w.releaser)["fix.mfs.return"].create(
        {"disbursement_id": disb.id, "return_file": _csv("wallet,status", "01712345673,failed")}
    )
    ret.action_import()
    assert _outbox(w, "payroll.beftn_returned", ret.id) == [
        {
            "company_id": w.co.id,
            "channel": "mfs",
            "batch_id": False,
            "mfs_disbursement_id": disb.id,
            "return_id": ret.id,
            "failed_amount": slip_of(p, mfs).net,
            "failed_count": 1,
        }
    ]


# ================================================================ deployment


def test_deployment_crons_seed_acls_and_surfaces(odoo_env):
    env = odoo_env
    cron = env.ref("cd_payroll_bd.ir_cron_payroll_gratuity_accrual")
    assert cron.active and cron.code == "model.cron_accrue_gratuity()"
    assert cron.interval_type == "months" and cron.interval_number == 1
    pack = env.ref("cd_payroll_bd.statutory_pack_v1_as_coded")
    assert pack.state == "baseline" and pack.basis == "as_coded"
    for xmlid in (
        "cd_payroll_bd.access_fix_statutory_pack_manager",
        "cd_payroll_bd.access_fix_payroll_variance_officer",
        "cd_payroll_bd.access_fix_payroll_bank_check_officer",
        "cd_payroll_bd.access_fix_beftn_return_release",
        "cd_payroll_bd.access_fix_mfs_disbursement_release",
        "cd_payroll_bd.access_fix_payroll_gratuity_accrual_officer",
        "cd_payroll_bd.access_fix_wppf_beneficiary_officer",
        "cd_payroll_bd.seq_fix_beftn_return",
    ):
        assert env.ref(xmlid)
    actions = {m: a09ctl.SURFACES[m]["actions"] for m in a09ctl.SURFACES}
    assert "action_trial_run" in actions["fix.payroll.period"]
    assert "action_pay_bwwf" in actions["fix.wppf.allocation"]
    assert actions["fix.statutory.pack"] >= {"action_request_approval", "action_new_version"}
    assert "action_approve" not in actions["fix.statutory.pack"]
    assert actions["fix.payroll.variance"] == {"action_acknowledge"}
    assert actions["fix.payroll.bank.check"] == {"action_confirm"}
    assert actions["fix.beftn.return"] == {"action_import", "action_reissue"}
    assert actions["fix.mfs.disbursement"] == {"action_settle"}
    assert actions["fix.payroll.nominee.account"] == {"action_verify", "action_cancel"}
    assert actions["fix.payroll.recovery"] == {
        "action_request_approval",
        "action_recall_approval",
        "action_cancel",
    }
    assert actions["fix.mfs.return"] == {"action_import", "action_reissue"}
    for xmlid in (
        "cd_payroll_bd.access_fix_payroll_recovery_officer",
        "cd_payroll_bd.access_fix_mfs_return_release",
    ):
        assert env.ref(xmlid)
    assert env.ref("cd_payroll_bd.access_fix_payroll_nominee_account_officer")
    assert "hr_statutory_pack" in dict(
        env["fix.approval.matrix"]._fields["decision_domain"].selection
    )
