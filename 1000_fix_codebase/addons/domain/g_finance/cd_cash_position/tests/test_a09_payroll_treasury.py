# cd_cash_position — A09 M56-17: treasury (M50) consumes the payroll
# disbursement events. Proved end to end through the real relay
# (fix.event.outbox.cron_relay), with payroll driven by freshly created
# NON-admin users (officer, two payroll managers, the disbursement releaser)
# and treasury acting as a non-admin accounting user. The superuser only
# builds fixtures (company, accounts, journals, employees, attendance locks)
# and, where labelled, moves a batch's settlement date into the past.
#
#   * a released run / off-cycle / bonus becomes ONE sent execution per bank
#     file, idempotent on replay, with no second instruction file
#   * the bank's confirmation posts Dr net payable / Cr bank through
#     treasury's execution GL path; payroll's own entry never touches the bank
#   * MFS wallet files are mobile_fs executions; an unconfigured paying wallet
#     posts nothing until treasury sets it
#   * bank returns: failed items are netted out; a re-issue never credits the
#     bank twice
#   * payroll.beftn_returned (published here directly with publish(): the
#     payroll side of that event is built in parallel): nets a file awaiting
#     the bank, books the money back after confirmation, idempotent on
#     return_id
import base64
import itertools
import json
from datetime import date
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo import Command
from odoo.exceptions import UserError

from libs.py.fix_events import publish

pytestmark = [pytest.mark.financial]

PS, PE = date(2026, 1, 1), date(2026, 1, 31)
CO_ACC, CO_ROUTING = "2051234567", "175261726"
KARIM_ACC, KARIM_ROUTING = "1501203345001", "060274689"
NASRIN_ACC, NASRIN_ROUTING = "2702150098761", "090261725"
FILE = "JVBERi0xLjQKJcOkw7zDtsOfCg=="  # a stand-in scanned confirmation (PDF header)
CONSUMERS = {
    "payroll.beftn_submitted": "consume_payroll_beftn_submitted",
    "payroll.offcycle_paid": "consume_payroll_offcycle_paid",
    "payroll.bonus_paid": "consume_payroll_bonus_paid",
    "payroll.beftn_settled": "consume_payroll_beftn_settled",
    "payroll.beftn_returned": "consume_payroll_beftn_returned",
}
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
    # The relay takes the oldest unrelayed events first, a batch at a time. A
    # database copied from a live one carries tens of thousands of them
    # (53,621 on fix_test copies, 13 Nov 2026), which starved this test's own
    # events: every delivery assertion failed. Mark the backlog relayed inside
    # this rolled-back transaction so the test proves its own events only.
    env.cr.execute("UPDATE fix_event_outbox SET relayed_at = now() WHERE relayed_at IS NULL")
    bdt = env.ref("base.BDT")
    bdt.active = True
    n = next(_SEQ)
    co = env["res.company"].create({"name": "A09 Treasury Co %d" % n, "currency_id": bdt.id})
    ou = env["operating.unit"].create(
        {
            "name": "TR Dhaka %d" % n,
            "code": "TRD%d" % n,
            "partner_id": co.partner_id.id,
            "company_id": co.id,
        }
    )
    payroll_journal = env["account.journal"].create(
        {"name": "Payroll", "code": "TRP%d" % n, "type": "general", "company_id": co.id}
    )
    bank = env["account.journal"].create(
        {
            "name": "Salary Bank",
            "code": "TRB%d" % n,
            "type": "bank",
            "company_id": co.id,
            "bank_acc_number": CO_ACC,
        }
    )
    wallet = env["account.journal"].create(
        {"name": "bKash Wallet", "code": "TRW%d" % n, "type": "bank", "company_id": co.id}
    )
    payable = _account(env, co, "2101", "Salaries Payable", "liability_current")
    co.write(
        {
            "payroll_journal_id": payroll_journal.id,
            "payroll_salary_expense_account_id": _account(
                env, co, "6101", "Salaries", "expense"
            ).id,
            "payroll_pf_expense_account_id": _account(env, co, "6102", "Employer PF", "expense").id,
            "payroll_net_payable_account_id": payable.id,
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
                    "login": "%s%d@a09tr.test" % (login, n),
                    "company_id": co.id,
                    "company_ids": [Command.set([co.id])],
                    "group_ids": [Command.set(ids)],
                }
            )
        )
        if "assigned_operating_unit_ids" in u._fields:
            u.assigned_operating_unit_ids = [Command.set([ou.id])]
        if "operating_unit_ids" in u._fields:
            u.operating_unit_ids = [Command.set([ou.id])]
        if "default_operating_unit_id" in u._fields:
            u.default_operating_unit_id = ou.id
        return u

    s = SimpleNamespace(env=cenv, co=co, ou=ou, bank=bank, wallet=wallet, payable=payable)
    s.officer = user("trofficer", "cd_payroll_bd.group_payroll_officer")
    s.manager = user(
        "trmanager", "cd_payroll_bd.group_payroll_manager", "account.group_account_manager"
    )
    s.manager2 = user(
        "trmanager2", "cd_payroll_bd.group_payroll_manager", "account.group_account_manager"
    )
    s.releaser = user(
        "trreleaser", "cd_payroll_bd.group_payroll_release", "account.group_account_manager"
    )
    s.treasury = user("trtreasury", "account.group_account_user")
    assert not s.treasury.has_group("base.group_system")

    def emp(name, basic, acc=None, routing=None):
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
            bank_acc = cenv["res.partner.bank"].create(
                {"acc_number": acc, "partner_id": e.work_contact_id.id}
            )
            e.write({"bank_account_ids": [Command.set([bank_acc.id])], "routing_number": routing})
        return e

    s.emp = emp
    s.karim = emp("TR Karim", 30000.0, KARIM_ACC, KARIM_ROUTING)
    s.nasrin = emp("TR Nasrin", 60000.0, NASRIN_ACC, NASRIN_ROUTING)
    lock = cenv["fix.attendance.lock"].create(
        {"name": "Jan 2026", "period_start": PS, "period_end": PE}
    )
    lock.action_lock()
    s.as_ = lambda u: cenv(user=u.id)
    return s


# ------------------------------------------------------------------ helpers


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


def paid(w):
    p = w.as_(w.officer)["fix.payroll.period"].create(
        {"name": "2026-01", "period_start": PS, "period_end": PE}
    )
    p.write({"company_account_no": CO_ACC, "company_routing_no": CO_ROUTING})
    p.action_verify_attendance_locked()
    p.action_calculate()
    p.action_request_approval()
    decide(w, p, w.manager)
    w.as_(w.releaser)["fix.payroll.period"].browse(p.id).action_pay()
    p.invalidate_recordset()
    return p


def relay(w):
    w.env["fix.event.outbox"].sudo().cron_relay(limit=5000)


def deliveries(w, event_type):
    sub = w.env.ref("cd_cash_position.consumer_%s_treasury" % event_type.replace(".", "_"))
    return w.env["fix.event.consumer.delivery"].sudo().search([("subscription_id", "=", sub.id)])


def assert_delivered(w, event_type, record):
    event = (
        w.env["fix.event.outbox"]
        .sudo()
        .search(
            [
                ("event_type", "=", event_type),
                ("aggregate", "=", record._name),
                ("aggregate_id", "=", record.id),
            ]
        )
    )
    assert len(event) == 1, event_type
    done = deliveries(w, event_type).filtered(lambda d: d.event_id == event)
    assert done.state == "done", done.last_error


def executions(w, source_model=None, source_id=None):
    domain = [("company_id", "=", w.co.id)]
    if source_model:
        domain += [("source_model", "=", source_model), ("source_id", "=", source_id)]
    return w.env["fix.payment.execution"].sudo().search(domain)


def settle(w, batch, ref="BB-CONF-1"):
    batch.sudo()._guarded().write({"settlement_date": date(2026, 1, 4)})  # fixture: a due batch
    rel = w.as_(w.releaser)[batch._name].browse(batch.id)
    rel.write({"bank_confirmation_ref": ref, "bank_confirmation_file": FILE})
    rel.action_settle()


def lines_on(w, account):
    return (
        w.env["account.move.line"]
        .sudo()
        .search([("account_id", "=", account.id), ("parent_state", "=", "posted")])
    )


def balance(w, account):
    return round(sum(lines_on(w, account).mapped("balance")), 2)


def instruction_files(w, pay):
    return (
        w.env["ir.attachment"]
        .sudo()
        .search([("res_model", "=", "fix.payment.execution"), ("res_id", "in", pay.ids)])
    )


# ------------------------------------------------------------------ tests


def test_a_released_run_is_recorded_once_as_sent_and_treasury_never_sends_it_again(w):
    p = paid(w)
    batch = p.beftn_batch_id
    assert not executions(w), "nothing is recorded before the relay delivers"
    relay(w)
    assert_delivered(w, "payroll.beftn_submitted", p)
    pay = executions(w)
    assert len(pay) == 1 and (pay.source_model, pay.source_id) == ("fix.beftn.batch", batch.id)
    assert (pay.state, pay.method, pay.rail, pay.payroll_released) == (
        "sent",
        "bank_transfer",
        "beftn",
        True,
    )
    assert pay.amount == batch.total_amount == p.approved_net_total
    assert pay.journal_id == w.bank, "the paying journal is the file's originating account"
    assert pay.debit_account_id == w.payable
    assert pay.sent_by_id == w.releaser and pay.sent_at == batch.submitted_at
    assert pay.payroll_document == "fix.payroll.period,%s" % p.id
    # treasury holds no instruction file of its own: payroll's batch is the file
    assert not pay.instruction_attachment_id and not instruction_files(w, pay)
    # the cash position counts the released outflow until the bank confirms it
    snap = w.as_(w.treasury)["fix.cash.position"].create({"company_id": w.co.id})
    assert snap.pending_payments == pay.amount

    # treasury (a non-admin accounting user) can never release or re-queue it
    mine = w.as_(w.treasury)["fix.payment.execution"].browse(pay.id)
    with pytest.raises(UserError, match="never releases or sends it again"), w.env.cr.savepoint():
        mine.action_release()
    with pytest.raises(UserError, match="only moves to executed"), w.env.cr.savepoint():
        mine.write({"state": "pending"})
    with pytest.raises(UserError, match="cannot be changed here"), w.env.cr.savepoint():
        mine.write({"amount": 1.0})
    with pytest.raises(UserError, match="payroll bank return"), w.env.cr.savepoint():
        mine.write({"failure_reason": "rejected"})
        mine.action_mark_failed()
    with pytest.raises(UserError, match="never re-queues it"), w.env.cr.savepoint():
        mine.action_retry()
    # nor fabricate a payroll execution, or squat the batch's idempotency key
    for vals in (
        {"payroll_released": True, "source_model": "manual", "source_id": 1},
        {"source_model": "fix.beftn.batch", "source_id": batch.id + 1000},
    ):
        with pytest.raises(UserError, match="payroll consumer only"), w.env.cr.savepoint():
            w.as_(w.treasury)["fix.payment.execution"].create(
                dict(vals, payee="x", amount=10.0, operating_unit_id=w.ou.id)
            )

    # replay: the relay again, a deliberate backfill, and a direct second call
    relay(w)
    sub = w.env.ref("cd_cash_position.consumer_payroll_beftn_submitted_treasury")
    sub.action_backfill()
    relay(w)
    event = (
        w.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", "payroll.beftn_submitted"), ("aggregate_id", "=", p.id)])
    )
    again = (
        w.env["fix.payment.execution"]
        .sudo()
        .consume_payroll_beftn_submitted(event._relay_event_dict())
    )
    assert again == pay and executions(w) == pay
    assert not instruction_files(w, pay)


def test_the_bank_confirmation_posts_payable_to_bank_once_and_payroll_never_touches_bank(w):
    p = paid(w)
    w.as_(w.manager2)["fix.payroll.period"].browse(p.id).action_post()
    relay(w)
    p.invalidate_recordset()
    bank_acc = w.bank.default_account_id
    # payroll's accrual: Dr expense / Cr net payable / Cr TDS / Cr PF - no bank line
    assert bank_acc not in p.gl_move_id.line_ids.mapped("account_id")
    assert not lines_on(w, bank_acc)
    batch = p.beftn_batch_id
    settle(w, batch)
    relay(w)
    assert_delivered(w, "payroll.beftn_settled", batch)
    pay = executions(w)
    assert (pay.state, pay.confirmation_source, pay.bank_reference, pay.bank_confirmed) == (
        "executed",
        # the A08 F1 evidence taxonomy renamed the source: the confirmation
        # is from the imported return FILE, not a typed reference
        "payroll_return",
        "BB-CONF-1",
        True,
    )
    move = pay.move_id
    assert move.state == "posted"
    assert sorted((ln.account_id, ln.debit, ln.credit) for ln in move.line_ids) == sorted(
        [(w.payable, batch.total_amount, 0.0), (bank_acc, 0.0, batch.total_amount)]
    )
    # the bank is credited once, by treasury; the net payable is cleared to 0
    assert lines_on(w, bank_acc).mapped("move_id") == move
    assert balance(w, bank_acc) == -batch.total_amount
    assert balance(w, w.payable) == 0.0
    executed = (
        w.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", "payment.executed"), ("aggregate_id", "=", pay.id)])
    )
    assert len(executed) == 1
    # replaying the settlement posts nothing more
    event = (
        w.env["fix.event.outbox"]
        .sudo()
        .search(
            [
                ("event_type", "=", "payroll.beftn_settled"),
                ("aggregate", "=", "fix.beftn.batch"),
                ("aggregate_id", "=", batch.id),
            ]
        )
    )
    w.env["fix.payment.execution"].sudo().consume_payroll_beftn_settled(event._relay_event_dict())
    relay(w)
    assert lines_on(w, bank_acc).mapped("move_id") == move
    assert (
        w.as_(w.treasury)["fix.cash.position"].create({"company_id": w.co.id}).pending_payments == 0
    )


def test_mfs_files_are_wallet_executions_and_an_unconfigured_wallet_posts_nothing(w):
    wallet_emp = w.emp("TR Wallet Only", 20000.0)
    wallet_emp.sudo().write({"mfs_provider": "bkash", "mfs_account_number": "01712345678"})
    p = paid(w)
    relay(w)
    disb = p.sudo().mfs_disbursement_ids
    assert len(disb) == 1
    bank_pay = executions(w, "fix.beftn.batch", p.beftn_batch_id.id)
    mfs_pay = executions(w, "fix.mfs.disbursement", disb.id)
    assert (mfs_pay.method, mfs_pay.rail, mfs_pay.state) == ("mobile_fs", False, "sent")
    assert mfs_pay.amount == disb.total_amount
    assert round(bank_pay.amount + mfs_pay.amount, 2) == p.approved_net_total
    assert not mfs_pay.journal_id, "no paying wallet configured: none is guessed"
    # the provider confirms; nothing can post without the paying wallet
    rel = w.as_(w.releaser)["fix.mfs.disbursement"].browse(disb.id)
    rel.write({"confirmation_ref": "BK-BULK-1", "confirmation_file": FILE})
    rel.action_settle()
    relay(w)
    assert_delivered(w, "payroll.beftn_settled", disb)
    mfs_pay.invalidate_recordset()
    assert (mfs_pay.state, mfs_pay.bank_reference, mfs_pay.move_id) == (
        "sent",
        "BK-BULK-1",
        w.env["account.move"],
    )
    # treasury names the wallet the file was paid from, then confirms
    mine = w.as_(w.treasury)["fix.payment.execution"].browse(mfs_pay.id)
    mine.write({"journal_id": w.wallet.id})
    mine.action_confirm_bank()
    assert mine.state == "executed" and mine.confirmation_source == "payroll_return"
    assert sorted((ln.account_id, ln.debit, ln.credit) for ln in mine.move_id.line_ids) == sorted(
        [(w.payable, disb.total_amount, 0.0), (w.wallet.default_account_id, 0.0, disb.total_amount)]
    )
    assert bank_pay.state == "sent", "the BEFTN batch waits for its own confirmation"


def test_a_configured_wallet_is_resolved_from_the_setting(w):
    wallet_emp = w.emp("TR Wallet Two", 20000.0)
    wallet_emp.sudo().write({"mfs_provider": "nagad", "mfs_account_number": "01812345678"})
    w.env["ir.config_parameter"].sudo().set_param(
        "cd_cash_position.payroll_mfs_journal_code.nagad", w.wallet.code
    )
    p = paid(w)
    relay(w)
    disb = p.sudo().mfs_disbursement_ids
    assert executions(w, "fix.mfs.disbursement", disb.id).journal_id == w.wallet


def test_offcycle_and_bonus_releases_are_recorded_and_confirmed(w):
    oc = w.as_(w.officer)["fix.payroll.offcycle"].create(
        {"employee_id": w.karim.id, "payment_type": "arrear", "amount": 12000.0}
    )
    oc.action_request_approval()
    decide(w, oc, w.manager)
    w.as_(w.releaser)["fix.payroll.offcycle"].browse(oc.id).action_pay()
    oc.invalidate_recordset()
    run = w.as_(w.officer)["fix.payroll.bonus.run"].create(
        {"festival": "eid_ul_fitr", "bonus_date": date(2026, 3, 20)}
    )
    run.action_compute()
    run.action_request_approval()
    decide(w, run, w.manager)
    w.as_(w.releaser)["fix.payroll.bonus.run"].browse(run.id).action_pay()
    run.invalidate_recordset()
    relay(w)
    assert_delivered(w, "payroll.offcycle_paid", oc)
    assert_delivered(w, "payroll.bonus_paid", run)
    oc_pay = executions(w, "fix.beftn.batch", oc.beftn_batch_id.id)
    bonus_pay = executions(w, "fix.beftn.batch", run.beftn_batch_id.id)
    assert (oc_pay.amount, oc_pay.state, oc_pay.payroll_document) == (
        12000.0,
        "sent",
        "fix.payroll.offcycle,%s" % oc.id,
    )
    assert bonus_pay.amount == run.total_net and bonus_pay.state == "sent"
    assert bonus_pay.payroll_document == "fix.payroll.bonus.run,%s" % run.id
    settle(w, oc.beftn_batch_id, "BB-OC-1")
    relay(w)
    oc_pay.invalidate_recordset()
    assert oc_pay.state == "executed" and oc_pay.bank_reference == "BB-OC-1"
    assert balance(w, w.bank.default_account_id) == -12000.0


def _csv(*rows):
    return base64.b64encode(("\n".join(rows) + "\n").encode()).decode()


def _return_karim_failed(w, batch, publish_event=True):
    """Import a bank return failing Karim's credit. Payroll publishes
    payroll.beftn_returned on import; `publish_event=False` holds that event
    back, so a test can deliver a late or forged one itself."""
    if not publish_event:
        from odoo.addons.cd_payroll_bd.models import fix_payroll_bank_return

        with mock.patch.object(fix_payroll_bank_return, "publish", lambda *a, **k: None):
            return _return_karim_failed(w, batch)
    ret = w.as_(w.releaser)["fix.beftn.return"].create(
        {
            "batch_id": batch.id,
            "return_file": _csv(
                "account,status,reason",
                "%s,failed,Account closed" % KARIM_ACC,
                "%s,paid" % NASRIN_ACC,
            ),
        }
    )
    ret.action_import()
    return ret


def _reissue(w, ret):
    new_bank = (
        w.env["res.partner.bank"]
        .sudo()
        .create({"acc_number": "1501209999001", "partner_id": w.karim.work_contact_id.id})
    )
    w.karim.sudo().bank_account_ids = [Command.set([new_bank.id])]  # fixture: approved change
    w.as_(w.releaser)["fix.beftn.return"].browse(ret.id).action_reissue()
    ret.invalidate_recordset()
    return ret.reissue_batch_ids


def test_failed_items_imported_first_are_netted_and_the_reissue_posts_its_own_leg(w):
    p = paid(w)
    relay(w)
    batch = p.beftn_batch_id
    karim_net = p.sudo().payslip_ids.filtered(lambda s: s.employee_id == w.karim).net
    ret = _return_karim_failed(w, batch)
    settle(w, batch)
    relay(w)
    pay = executions(w, "fix.beftn.batch", batch.id)
    assert pay.state == "executed" and pay.amount == round(batch.total_amount - karim_net, 2)
    assert pay.payroll_netted_returns == str(ret.id)
    reissue = _reissue(w, ret)
    settle(w, reissue, "BB-RE-1")
    relay(w)
    again = executions(w, "fix.beftn.batch", reissue.id)
    assert again.state == "executed" and again.amount == karim_net and again.move_id
    # the bank is credited exactly the run's total, once per item paid
    assert balance(w, w.bank.default_account_id) == -batch.total_amount


def test_a_return_after_a_gross_confirmation_is_booked_back_and_the_reissue_pays(w):
    """Payroll publishes payroll.beftn_returned when the return is imported:
    after a gross confirmation treasury books the returned credit back, and
    the re-issue then posts its own leg - the bank is credited the run once."""
    p = paid(w)
    relay(w)
    batch = p.beftn_batch_id
    karim_net = p.sudo().payslip_ids.filtered(lambda s: s.employee_id == w.karim).net
    settle(w, batch)
    relay(w)
    pay = executions(w, "fix.beftn.batch", batch.id)
    assert pay.amount == batch.total_amount and pay.state == "executed"
    ret = _return_karim_failed(w, batch)
    reissue = _reissue(w, ret)
    settle(w, reissue, "BB-RE-2")
    relay(w)
    pay.invalidate_recordset()
    assert pay.payroll_booked_returns == str(ret.id) and pay.payroll_return_move_ids
    again = executions(w, "fix.beftn.batch", reissue.id)
    assert again.state == "executed" and again.amount == karim_net and again.move_id
    assert balance(w, w.bank.default_account_id) == -batch.total_amount


def test_a_batch_the_bank_failed_entirely_is_confirmed_with_no_entry(w):
    p = paid(w)
    relay(w)
    batch = p.beftn_batch_id
    ret = w.as_(w.releaser)["fix.beftn.return"].create(
        {
            "batch_id": batch.id,
            "return_file": _csv(
                "account,status,reason",
                "%s,failed,Account closed" % KARIM_ACC,
                "%s,failed,Dormant" % NASRIN_ACC,
            ),
        }
    )
    ret.action_import()
    settle(w, batch)
    relay(w)
    assert_delivered(w, "payroll.beftn_settled", batch)
    pay = executions(w, "fix.beftn.batch", batch.id)
    assert (pay.state, pay.amount, pay.move_id) == ("executed", 0.0, w.env["account.move"])
    assert "nothing left the bank" in pay.gl_note
    assert balance(w, w.bank.default_account_id) == 0.0


def test_a_payload_that_disagrees_with_the_files_records_nothing(w):
    p = paid(w)
    event = (
        w.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", "payroll.beftn_submitted"), ("aggregate_id", "=", p.id)])
    )
    forged = event._relay_event_dict()
    forged["payload"] = dict(forged["payload"], amount=forged["payload"]["amount"] + 1)
    with pytest.raises(UserError, match="the event states"), w.env.cr.savepoint():
        w.env["fix.payment.execution"].sudo().consume_payroll_beftn_submitted(forged)
    assert not executions(w)
    assert json.loads(event.payload)["batch_id"] == p.beftn_batch_id.id


def test_deployment_the_four_treasury_consumers_are_registered(odoo_env):
    for event_type, method in CONSUMERS.items():
        sub = odoo_env.ref("cd_cash_position.consumer_%s_treasury" % event_type.replace(".", "_"))
        assert (sub.event_type, sub.model, sub.method, sub.active) == (
            event_type,
            "fix.payment.execution",
            method,
            True,
        )
        assert callable(getattr(odoo_env[sub.model], sub.method))


# ---------------------------------------------------- payroll.beftn_returned


def returned(w, batch=None, ret=None, failed=None, **extra):
    """Publish payroll.beftn_returned with the agreed payload, as payroll will."""
    payload = {
        "company_id": w.co.id,
        "channel": "beftn",
        "batch_id": batch.id if batch else False,
        "mfs_disbursement_id": False,
        "return_id": ret.id if ret else False,
        "failed_amount": float(ret.failed_amount if failed is None else failed),
        "failed_count": ret.failed_count if ret else 1,
    }
    payload.update(extra)
    publish(w.env, "payroll.beftn_returned", "fix.beftn.return", payload["return_id"], payload)
    relay(w)


def delivery_of(w, return_id):
    event = (
        w.env["fix.event.outbox"]
        .sudo()
        .search(
            [("event_type", "=", "payroll.beftn_returned"), ("aggregate_id", "=", return_id)],
            order="id desc",
            limit=1,
        )
    )
    return deliveries(w, "payroll.beftn_returned").filtered(lambda d: d.event_id == event)


def test_a_return_before_confirmation_nets_the_payment_still_awaiting_the_bank(w):
    p = paid(w)
    relay(w)
    batch = p.beftn_batch_id
    karim_net = p.sudo().payslip_ids.filtered(lambda s: s.employee_id == w.karim).net
    ret = _return_karim_failed(w, batch)
    returned(w, batch, ret)
    assert delivery_of(w, ret.id).state == "done", delivery_of(w, ret.id).last_error
    pay = executions(w, "fix.beftn.batch", batch.id)
    assert pay.state == "sent" and pay.amount == round(batch.total_amount - karim_net, 2)
    assert pay.payroll_netted_returns == str(ret.id)
    # the cash position now expects only what the bank will pay
    snap = w.as_(w.treasury)["fix.cash.position"].create({"company_id": w.co.id})
    assert snap.pending_payments == pay.amount
    # a replayed event (same return_id) changes nothing
    returned(w, batch, ret)
    pay.invalidate_recordset()
    assert pay.amount == round(batch.total_amount - karim_net, 2)
    settle(w, batch)
    relay(w)
    pay.invalidate_recordset()
    assert pay.state == "executed" and pay.amount == round(batch.total_amount - karim_net, 2)
    assert balance(w, w.bank.default_account_id) == -round(batch.total_amount - karim_net, 2)
    assert not pay.payroll_return_move_ids


def test_a_return_after_confirmation_books_the_money_back_once_and_the_reissue_pays(w):
    p = paid(w)
    w.as_(w.manager2)["fix.payroll.period"].browse(p.id).action_post()  # the accrual
    relay(w)
    batch = p.beftn_batch_id
    karim_net = p.sudo().payslip_ids.filtered(lambda s: s.employee_id == w.karim).net
    settle(w, batch)
    relay(w)
    pay = executions(w, "fix.beftn.batch", batch.id)
    assert pay.state == "executed" and pay.amount == batch.total_amount
    bank_acc = w.bank.default_account_id
    ret = _return_karim_failed(w, batch)
    returned(w, batch, ret)
    assert delivery_of(w, ret.id).state == "done", delivery_of(w, ret.id).last_error
    pay.invalidate_recordset()
    back = pay.payroll_return_move_ids
    assert len(back) == 1 and back.state == "posted" and pay.payroll_booked_returns == str(ret.id)
    assert sorted((ln.account_id, ln.debit, ln.credit) for ln in back.line_ids) == sorted(
        [(bank_acc, karim_net, 0.0), (w.payable, 0.0, karim_net)]
    )
    # the money is back in the bank and Karim's salary is owed again
    assert balance(w, bank_acc) == -round(batch.total_amount - karim_net, 2)
    assert balance(w, w.payable) == -karim_net
    # idempotent on return_id: a replayed event books nothing more
    returned(w, batch, ret)
    pay.invalidate_recordset()
    assert pay.payroll_return_move_ids == back
    # the re-issue now pays Karim with its own cash leg
    reissue = _reissue(w, ret)
    settle(w, reissue, "BB-RE-3")
    relay(w)
    again = executions(w, "fix.beftn.batch", reissue.id)
    assert again.state == "executed" and again.amount == karim_net and again.move_id
    assert balance(w, bank_acc) == -batch.total_amount
    assert balance(w, w.payable) == 0.0


def test_a_return_reaching_a_reissue_already_settled_on_the_gross_entry_books_nothing(w):
    p = paid(w)
    relay(w)
    batch = p.beftn_batch_id
    settle(w, batch)
    relay(w)
    # the return event is delayed in transit: the re-issue settles first
    ret = _return_karim_failed(w, batch, publish_event=False)
    reissue = _reissue(w, ret)
    settle(w, reissue, "BB-RE-4")
    relay(w)  # the re-issue settles before the late return event: it posts nothing
    returned(w, batch, ret)
    pay = executions(w, "fix.beftn.batch", batch.id)
    assert pay.payroll_booked_returns == str(ret.id) and not pay.payroll_return_move_ids
    assert balance(w, w.bank.default_account_id) == -batch.total_amount


def test_an_mfs_return_nets_the_wallet_file(w):
    wallet_emp = w.emp("TR Wallet Ret", 20000.0)
    wallet_emp.sudo().write({"mfs_provider": "bkash", "mfs_account_number": "01712345670"})
    p = paid(w)
    relay(w)
    disb = p.sudo().mfs_disbursement_ids
    # the provider's return, imported by the releaser: payroll publishes
    # payroll.beftn_returned and the relay delivers it to treasury
    csv_file = base64.b64encode(b"wallet,status\n01712345670,failed\n").decode()
    ret = w.as_(w.releaser)["fix.mfs.return"].create(
        {"disbursement_id": disb.id, "return_file": csv_file}
    )
    ret.action_import()
    relay(w)
    assert delivery_of(w, ret.id).state == "done", delivery_of(w, ret.id).last_error
    pay = executions(w, "fix.mfs.disbursement", disb.id)
    assert (pay.state, pay.amount, pay.payroll_netted_returns) == ("sent", 0.0, str(ret.id))
    w.env["ir.config_parameter"].sudo().set_param(
        "cd_cash_position.payroll_mfs_journal_code.bkash", w.wallet.code
    )
    rel = w.as_(w.releaser)["fix.mfs.disbursement"].browse(disb.id)
    rel.write({"confirmation_ref": "BK-BULK-9", "confirmation_file": FILE})
    rel.action_settle()
    relay(w)
    pay.invalidate_recordset()
    assert pay.state == "executed" and not pay.move_id, "nothing left the wallet"


def test_a_return_event_that_disagrees_with_the_return_is_refused(w):
    p = paid(w)
    relay(w)
    batch = p.beftn_batch_id
    # only the forged event reaches treasury (payroll's own one is held back)
    ret = _return_karim_failed(w, batch, publish_event=False)
    returned(w, batch, ret, failed=ret.failed_amount + 50)
    assert delivery_of(w, ret.id).state == "failed"
    assert "the return holds" in delivery_of(w, ret.id).last_error
    pay = executions(w, "fix.beftn.batch", batch.id)
    assert pay.amount == batch.total_amount and not pay.payroll_netted_returns
