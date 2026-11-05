# cd_tax_engine_bd — A09 M56-17: the M51 intake of the salary TDS payroll
# withheld (ITA 2023 s.86), from payroll.posted, through the real relay
# (fix.event.outbox.cron_relay). Payroll is driven by freshly created NON-admin
# users; the tax side by a non-admin accounting user. The superuser builds the
# fixtures only (company, accounts, journals, employees, attendance lock, the
# challan journal setting).
#
#   * one fix.salary.tds row per payroll run and operating unit, holding the
#     tax payroll withheld and booked; idempotent on replay
#   * a salary TDS challan links them and its deposit clears the payroll TDS
#     payable account (Dr TDS payable / Cr bank); a general challan never
#     picks them up
#   * the quarterly TDS return lists them under s.86
#   * payroll.bonus_posted (published here directly with publish(): the
#     payroll side of that event is built in parallel) feeds the same rows,
#     sourced on the bonus run, with the same checks
import itertools
import json
from datetime import date
from types import SimpleNamespace

import pytest
from odoo import Command
from odoo.exceptions import AccessError, UserError

from libs.py.fix_events import publish

pytestmark = [pytest.mark.financial]

PS, PE = date(2026, 1, 1), date(2026, 1, 31)
CO_ACC, CO_ROUTING = "2051234567", "175261726"
_SEQ = itertools.count(1)


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
    co = env["res.company"].create({"name": "A09 Salary TDS Co %d" % n, "currency_id": bdt.id})

    def unit(name, code):
        return env["operating.unit"].create(
            {"name": name, "code": code, "partner_id": co.partner_id.id, "company_id": co.id}
        )

    ou, ou2 = unit("ST Dhaka %d" % n, "STD%d" % n), unit("ST Ctg %d" % n, "STC%d" % n)
    journal = env["account.journal"].create(
        {"name": "Payroll", "code": "STP%d" % n, "type": "general", "company_id": co.id}
    )
    bank = env["account.journal"].create(
        {"name": "Tax Bank", "code": "STB%d" % n, "type": "bank", "company_id": co.id}
    )
    tds = _account(env, co, "2102", "Salary TDS Payable", "liability_current")
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
            "payroll_tax_payable_account_id": tds.id,
            "payroll_pf_payable_account_id": _account(
                env, co, "2103", "PF Payable", "liability_current"
            ).id,
        }
    )
    env["ir.config_parameter"].sudo().set_param("cd_tax_engine_bd.challan_journal_code", bank.code)
    cenv = env(context=dict(env.context, allowed_company_ids=[co.id]))

    def user(login, *groups):
        ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
        u = (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": "%s%d@a09st.test" % (login, n),
                    "company_id": co.id,
                    "company_ids": [Command.set([co.id])],
                    "group_ids": [Command.set(ids)],
                }
            )
        )
        if "assigned_operating_unit_ids" in u._fields:
            u.assigned_operating_unit_ids = [Command.set([ou.id, ou2.id])]
        if "operating_unit_ids" in u._fields:
            u.operating_unit_ids = [Command.set([ou.id, ou2.id])]
        if "default_operating_unit_id" in u._fields:
            u.default_operating_unit_id = ou.id
        return u

    s = SimpleNamespace(env=cenv, co=co, ou=ou, ou2=ou2, bank=bank, tds=tds)
    s.officer = user("stofficer", "cd_payroll_bd.group_payroll_officer")
    s.manager = user(
        "stmanager", "cd_payroll_bd.group_payroll_manager", "account.group_account_manager"
    )
    s.manager2 = user(
        "stmanager2", "cd_payroll_bd.group_payroll_manager", "account.group_account_manager"
    )
    s.releaser = user(
        "streleaser", "cd_payroll_bd.group_payroll_release", "account.group_account_manager"
    )
    s.taxuser = user("sttax", "account.group_account_user")
    assert not s.taxuser.has_group("base.group_system")

    def emp(name, basic, acc, routing, unit_):
        e = cenv["hr.employee"].create(
            {"name": name, "company_id": co.id, "operating_unit_id": unit_.id}
        )
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
        bank_acc = cenv["res.partner.bank"].create(
            {"acc_number": acc, "partner_id": e.work_contact_id.id}
        )
        e.write({"bank_account_ids": [Command.set([bank_acc.id])], "routing_number": routing})
        return e

    s.karim = emp("ST Karim", 90000.0, "1501203345001", "060274689", ou)
    s.nasrin = emp("ST Nasrin", 120000.0, "2702150098761", "090261725", ou2)
    lock = cenv["fix.attendance.lock"].create(
        {"name": "Jan 2026", "period_start": PS, "period_end": PE}
    )
    lock.action_lock()
    s.as_ = lambda u: cenv(user=u.id)
    return s


def decide(w, rec, approver):
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


def posted(w):
    p = w.as_(w.officer)["fix.payroll.period"].create(
        {"name": "2026-01", "period_start": PS, "period_end": PE}
    )
    p.write({"company_account_no": CO_ACC, "company_routing_no": CO_ROUTING})
    p.action_verify_attendance_locked()
    p.action_calculate()
    p.action_request_approval()
    decide(w, p, w.manager)
    w.as_(w.releaser)["fix.payroll.period"].browse(p.id).action_pay()
    w.as_(w.manager2)["fix.payroll.period"].browse(p.id).action_post()
    p.invalidate_recordset()
    return p


def relay(w):
    w.env["fix.event.outbox"].sudo().cron_relay(limit=5000)


def rows_of(w, period):
    return (
        w.env["fix.salary.tds"]
        .sudo()
        .search([("source_model", "=", "fix.payroll.period"), ("source_id", "=", period.id)])
    )


def tax_by_unit(period):
    out = {}
    for slip in period.sudo().payslip_ids:
        out[slip.cost_operating_unit_id] = out.get(slip.cost_operating_unit_id, 0.0) + (
            slip.tax_withheld
        )
    return {k: round(v, 2) for k, v in out.items() if round(v, 2)}


def posted_event(w, period):
    return (
        w.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", "payroll.posted"), ("aggregate_id", "=", period.id)])
    )


def balance(w, account):
    lines = (
        w.env["account.move.line"]
        .sudo()
        .search([("account_id", "=", account.id), ("parent_state", "=", "posted")])
    )
    return round(sum(lines.mapped("balance")), 2)


def test_a_posted_run_s_tds_arrives_once_per_unit_through_the_relay(w):
    p = posted(w)
    expected = tax_by_unit(p)
    assert set(expected) == {w.ou, w.ou2}, "both units withhold tax in this fixture"
    assert not rows_of(w, p), "nothing before the relay delivers"
    relay(w)
    sub = w.env.ref("cd_tax_engine_bd.consumer_payroll_posted_salary_tds")
    event = posted_event(w, p)
    delivery = (
        w.env["fix.event.consumer.delivery"]
        .sudo()
        .search([("subscription_id", "=", sub.id), ("event_id", "=", event.id)])
    )
    assert delivery.state == "done", delivery.last_error
    rows = rows_of(w, p)
    assert {r.operating_unit_id: r.amount for r in rows} == expected
    for row in rows:
        assert (row.company_id, row.period, row.section, row.state) == (
            w.co,
            "2026-01",
            "s.86",
            "withheld",
        )
        assert row.move_id == p.gl_move_id and row.liability_account_id == w.tds
        assert row.document_date == PE and row.source_ref == "2026-01"
    # the rows hold exactly what payroll's entry credited to TDS payable
    assert round(sum(rows.mapped("amount")), 2) == -balance(w, w.tds)
    # replay: the relay again, a backfill, a direct second call
    relay(w)
    sub.action_backfill()
    relay(w)
    w.env["fix.salary.tds"].sudo().consume_payroll_posted(event._relay_event_dict())
    assert rows_of(w, p) == rows
    # an accounting user reads them but never types or creates one
    mine = w.as_(w.taxuser)["fix.salary.tds"]
    assert mine.search([("id", "in", rows.ids)]) == rows
    with pytest.raises(AccessError), w.env.cr.savepoint():
        mine.browse(rows[0].id).write({"amount": 1.0})
    with pytest.raises(AccessError), w.env.cr.savepoint():
        mine.create(
            {
                "company_id": w.co.id,
                "ou_key": 0,
                "source_model": "manual",
                "source_id": 1,
                "document_date": PE,
                "currency_id": w.co.currency_id.id,
                "amount": 10.0,
            }
        )


def test_a_salary_challan_deposits_the_rows_and_clears_payroll_tds_payable(w):
    p = posted(w)
    relay(w)
    rows = rows_of(w, p)
    total = round(sum(rows.mapped("amount")), 2)
    Challan = w.as_(w.taxuser)["fix.tax.challan"]
    # a general TDS challan never picks salary TDS up
    general = Challan.create(
        {
            "challan_no": "GEN-1",
            "challan_date": date(2026, 2, 10),
            "tax_kind": "tds",
            "period": "2026-01",
            "amount": total,
        }
    )
    with pytest.raises(UserError, match="No undeposited TDS deductions"), w.env.cr.savepoint():
        general.action_link_open_deductions()
    ch = Challan.create(
        {
            "challan_no": "SAL-1",
            "challan_date": date(2026, 2, 10),
            "tax_kind": "tds",
            "tds_head": "salary",
            "period": "2026-01",
            "amount": total + 100.0,
        }
    )
    ch.action_link_open_deductions()
    assert ch.salary_tds_ids == rows and ch.liability_total == total
    with pytest.raises(UserError, match="does not equal the salary TDS"), w.env.cr.savepoint():
        ch.action_confirm_deposit()
    ch.write({"amount": total})
    ch.action_confirm_deposit()
    assert ch.state == "deposited" and set(rows.mapped("state")) == {"deposited"}
    assert sorted((ln.account_id, ln.debit, ln.credit) for ln in ch.move_id.line_ids) == sorted(
        [(w.tds, total, 0.0), (w.bank.default_account_id, 0.0, total)]
    )
    assert balance(w, w.tds) == 0.0, "payroll's TDS credit is cleared by the deposit"
    event = (
        w.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", "tax_challan.deposited"), ("aggregate_id", "=", ch.id)])
    )
    assert json.loads(event.payload)["amount"] == total
    with pytest.raises(UserError, match="already deposited"), w.env.cr.savepoint():
        ch.action_confirm_deposit()
    second = Challan.create(
        {
            "challan_no": "SAL-2",
            "challan_date": date(2026, 2, 11),
            "tax_kind": "tds",
            "tds_head": "salary",
            "period": "2026-01",
            "amount": 1.0,
        }
    )
    with pytest.raises(UserError, match="No undeposited salary TDS"), w.env.cr.savepoint():
        second.action_link_open_deductions()


def test_the_quarterly_tds_return_lists_salary_tds_under_s86(w):
    p = posted(w)
    relay(w)
    rows = rows_of(w, p)
    ret = w.as_(w.taxuser)["fix.tds.return"].create({"quarter": "2025-Q3"})  # Jan-Mar 2026
    ret.action_prepare()
    salary = ret.line_ids.filtered(lambda ln: ln.section_code == "86")
    assert salary.mapped("salary_tds_id") == rows
    assert {ln.operating_unit_id: ln.tds_amount for ln in salary} == {
        r.operating_unit_id: r.amount for r in rows
    }
    for ln in salary:
        assert ln.base_amount == ln.salary_tds_id.gross
    assert ret.total_withheld == round(sum(rows.mapped("amount")), 2)
    # re-preparing rebuilds, never doubles. Played as the superuser: no group
    # holds unlink on fix.tds.return.line, so A08's re-prepare is refused for
    # every non-admin (pre-existing, reported to the coordinator).
    ret.sudo().action_prepare()
    assert len(ret.line_ids.filtered(lambda ln: ln.section_code == "86")) == len(rows)
    assert ret.total_withheld == round(sum(rows.mapped("amount")), 2)


def test_an_event_that_disagrees_with_the_entry_is_refused(w):
    p = posted(w)
    event = posted_event(w, p)._relay_event_dict()
    Tds = w.env["fix.salary.tds"].sudo()
    forged = dict(event, payload=dict(event["payload"], tax=event["payload"]["tax"] + 5))
    with pytest.raises(UserError, match="differs from the run"), w.env.cr.savepoint():
        Tds.consume_payroll_posted(forged)
    units = [dict(row, tax=row["tax"] + 5) for row in event["payload"]["by_operating_unit"]]
    bumped = sum(row["tax"] for row in units)
    forged = dict(event, payload=dict(event["payload"], by_operating_unit=units, tax=bumped))
    with (
        pytest.raises(UserError, match=r"credits .* to the TDS payable account"),
        w.env.cr.savepoint(),
    ):
        Tds.consume_payroll_posted(forged)
    assert not rows_of(w, p)


def test_deployment_consumer_acl_and_isolation(odoo_env):
    for xmlid, event_type, method in (
        ("consumer_payroll_posted_salary_tds", "payroll.posted", "consume_payroll_posted"),
        (
            "consumer_payroll_bonus_posted_salary_tds",
            "payroll.bonus_posted",
            "consume_payroll_bonus_posted",
        ),
    ):
        sub = odoo_env.ref("cd_tax_engine_bd.%s" % xmlid)
        assert (sub.event_type, sub.model, sub.method, sub.active) == (
            event_type,
            "fix.salary.tds",
            method,
            True,
        )
    for suffix in ("readonly", "user", "manager"):
        acl = odoo_env.ref("cd_tax_engine_bd.access_fix_salary_tds_account_%s" % suffix)
        assert (acl.perm_read, acl.perm_write, acl.perm_create, acl.perm_unlink) == (
            True,
            False,
            False,
            False,
        )
    for rule in ("company", "operating_unit"):
        assert odoo_env.ref("cd_tax_engine_bd.rule_fix_salary_tds_%s" % rule).active


# ------------------------------------------------------ payroll.bonus_posted


def _bonus_entry(w, by_unit):
    """Fixture: the bonus run's posted entry as payroll books it
    (Dr salary expense / Cr net payable / Cr TDS payable)."""
    co = w.co
    gross = round(sum(g for g, _t in by_unit.values()), 2)
    tax = round(sum(t for _g, t in by_unit.values()), 2)
    move = (
        w.env["account.move"]
        .sudo()
        .create(
            {
                "move_type": "entry",
                "journal_id": co.payroll_journal_id.id,
                "company_id": co.id,
                "date": date(2026, 3, 20),
                "ref": "Festival Bonus fixture",
                "line_ids": [
                    Command.create(
                        {
                            "account_id": co.payroll_salary_expense_account_id.id,
                            "debit": gross,
                            "credit": 0.0,
                        }
                    ),
                    Command.create(
                        {
                            "account_id": co.payroll_net_payable_account_id.id,
                            "debit": 0.0,
                            "credit": round(gross - tax, 2),
                        }
                    ),
                    Command.create({"account_id": w.tds.id, "debit": 0.0, "credit": tax}),
                ],
            }
        )
    )
    move.action_post()
    return move


def bonus_posted(w, run, move, by_unit, **extra):
    payload = {
        "company_id": w.co.id,
        "bonus_run_id": run.id,
        "move_id": move.id,
        "period_end": "2026-03-20",
        "tax_total": round(sum(t for _g, t in by_unit.values()), 2),
        "by_operating_unit": [
            {"operating_unit_id": ou.id, "gross": g, "tax": t} for ou, (g, t) in by_unit.items()
        ],
    }
    payload.update(extra)
    publish(w.env, "payroll.bonus_posted", "fix.payroll.bonus.run", run.id, payload)
    w.env["fix.event.outbox"].sudo().cron_relay(limit=5000)
    return payload


def bonus_delivery(w, run):
    sub = w.env.ref("cd_tax_engine_bd.consumer_payroll_bonus_posted_salary_tds")
    event = (
        w.env["fix.event.outbox"]
        .sudo()
        .search(
            [("event_type", "=", "payroll.bonus_posted"), ("aggregate_id", "=", run.id)],
            order="id desc",
            limit=1,
        )
    )
    return (
        w.env["fix.event.consumer.delivery"]
        .sudo()
        .search([("subscription_id", "=", sub.id), ("event_id", "=", event.id)])
    )


def bonus_rows(w, run):
    return (
        w.env["fix.salary.tds"]
        .sudo()
        .search([("source_model", "=", "fix.payroll.bonus.run"), ("source_id", "=", run.id)])
    )


def test_a_posted_bonus_s_tds_arrives_once_per_unit_sourced_on_the_run(w):
    run = w.as_(w.officer)["fix.payroll.bonus.run"].create(
        {"festival": "eid_ul_fitr", "bonus_date": date(2026, 3, 20)}
    )
    by_unit = {w.ou: (90000.0, 9000.0), w.ou2: (120000.0, 18000.0)}
    move = _bonus_entry(w, by_unit)
    bonus_posted(w, run, move, by_unit)
    assert bonus_delivery(w, run).state == "done", bonus_delivery(w, run).last_error
    rows = bonus_rows(w, run)
    assert {r.operating_unit_id: (r.gross, r.amount) for r in rows} == by_unit
    for row in rows:
        assert (row.period, row.section, row.move_id, row.liability_account_id) == (
            "2026-03",
            "s.86",
            move,
            w.tds,
        )
        assert row.source_ref == "Bonus %s" % (run.name or run.id)
    # replay: a second event for the same run creates nothing
    bonus_posted(w, run, move, by_unit)
    assert bonus_rows(w, run) == rows
    # the bonus TDS is deposited on a salary challan like the monthly TDS
    ch = w.as_(w.taxuser)["fix.tax.challan"].create(
        {
            "challan_no": "SAL-B1",
            "challan_date": date(2026, 4, 10),
            "tax_kind": "tds",
            "tds_head": "salary",
            "period": "2026-03",
            "amount": 27000.0,
        }
    )
    ch.action_link_open_deductions()
    assert ch.salary_tds_ids == rows
    ch.action_confirm_deposit()
    assert ch.state == "deposited" and balance(w, w.tds) == 0.0


def test_a_bonus_event_that_disagrees_with_its_entry_is_refused(w):
    run = w.as_(w.officer)["fix.payroll.bonus.run"].create(
        {"festival": "eid_ul_fitr", "bonus_date": date(2026, 3, 20)}
    )
    by_unit = {w.ou: (90000.0, 9000.0)}
    move = _bonus_entry(w, by_unit)
    bonus_posted(w, run, move, by_unit, tax_total=9500.0)
    assert bonus_delivery(w, run).state == "failed"
    assert "differs from the run" in bonus_delivery(w, run).last_error
    bigger = {w.ou: (90000.0, 9500.0)}
    bonus_posted(w, run, move, bigger)
    assert "to the TDS payable account" in bonus_delivery(w, run).last_error
    assert not bonus_rows(w, run)
