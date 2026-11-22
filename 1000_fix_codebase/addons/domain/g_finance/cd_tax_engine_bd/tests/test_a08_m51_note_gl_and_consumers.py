"""A08 M51-F4 / M51-F10 regressions (B6, 2026-11-22).

M51-F4 — a Mushak 6.7 / 6.8 correction note posts its VAT effect through
post_tax_move in the note's own issue (the same second-person gate as the
note), links the register row to the move, and the 9.1 sub-ledger
reconciliation clears instead of stranding the money at the register row.
Fails closed on unconfigured accounts (IRB-09 / T-08).

M51-F10 — the tax events reach the registers through the event relay:
`vat_subledger.variance_detected` and `tax.notice.overdue` open ONE M60 risk
item each, and `vat_return.filed` discharges the period's compliance
obligation occurrence with the NBR acknowledgement as evidence. Every
consumer is idempotent: a redelivered event creates nothing.

Live ORM, rolled back; the fixture mirrors test_a08_m51_controls.py.
"""

from __future__ import annotations

import itertools
import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

pytestmark = [pytest.mark.tax, pytest.mark.financial]

REFUSED = (UserError, ValidationError, AccessError)
BIN = "1234567890123"
ACC = "account.group_account_user"
MGR = "account.group_account_manager"
FILER = "cd_tax_engine_bd.group_tax_filing_approver"
REG, RET, NOTICE = "fix.mushak.register", "fix.vat.return", "fix.tax.notice"
RISK = "fix.risk.register"
NOTE_COUNTER_PARAM = "cd_tax_engine_bd.note_counter_account_code"

_SEQ = itertools.count(9000)


def _refused(fn, *args, match=None, **kw):
    with pytest.raises(REFUSED, match=match):
        fn(*args, **kw)


class Ctx(types.SimpleNamespace):
    def as_(self, user):
        return self.env(
            user=user.id, context=dict(self.env.context, allowed_company_ids=self.co.ids)
        )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    n = next(_SEQ)
    x = Ctx(env=env)
    x.co = env["res.company"].create({"name": "B6 M51 Note GL Co %s" % n, "vat": BIN})
    x.ou = env["operating.unit"].create(
        {
            "name": "B6 M51 OU %s" % n,
            "code": "B6M5%s" % n,
            "company_id": x.co.id,
            "partner_id": x.co.partner_id.id,
        }
    )
    x.cenv = env(context=dict(env.context, allowed_company_ids=x.co.ids))
    x.today = fields.Date.context_today(env.user)
    x.period = x.today.strftime("%Y-%m")
    Account = x.cenv["account.account"]

    def acc(code, name, kind):
        return Account.create(
            {
                "code": "B6M5%s%s" % (n, code),
                "name": name,
                "account_type": kind,
                "company_ids": [(6, 0, x.co.ids)],
            }
        )

    x.vat_out = acc("1", "VAT output payable", "liability_current")
    x.vat_in = acc("2", "VAT input credit", "asset_current")
    x.counter = acc("3", "Receivables (note counter)", "asset_receivable")
    x.revenue = acc("4", "Service revenue", "income")
    x.ar = acc("5", "Receivables", "asset_receivable")
    icp = env["ir.config_parameter"].sudo()
    icp.set_param("cd_tax_engine_bd.vat_output_account_code", x.vat_out.code)
    icp.set_param("cd_tax_engine_bd.vat_input_account_code", x.vat_in.code)
    icp.set_param(NOTE_COUNTER_PARAM, x.counter.code)
    x.journal = x.cenv["account.journal"].create(
        {
            "name": "B6 M51 misc %s" % n,
            "code": "B6G%s" % n,
            "type": "general",
            "company_id": x.co.id,
        }
    )

    def user(login, *groups):
        gids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": "%s-b6-%s" % (login, n),
                    "group_ids": [(6, 0, gids)],
                    "company_id": x.co.id,
                    "company_ids": [(6, 0, x.co.ids)],
                    "assigned_operating_unit_ids": [(6, 0, x.ou.ids)],
                    "default_operating_unit_id": x.ou.id,
                }
            )
        )

    x.acct = user("b6_acct", ACC)
    x.requester = user("b6_requester", ACC, MGR)  # a manager who ASKS: the SoD probe
    x.mgr = user("b6_decider", MGR)
    x.filer = user("b6_filer", ACC, FILER)
    return x


# ------------------------------------------------------------------ helpers
def _entry(c, lines, when=None):
    move = c.cenv["account.move"].create(
        {
            "journal_id": c.journal.id,
            "date": when or c.today,
            "line_ids": [
                (0, 0, {"account_id": a.id, "name": "b6", "debit": dr, "credit": cr})
                for a, dr, cr in lines
            ],
        }
    )
    move.action_post()
    return move


def _reg(c, taxable, vat):
    """A register row as the billing engine writes it (GL-less: its supply's
    GL is arranged separately, as for a billed invoice)."""
    return c.cenv[REG]._fix_issue_register_row(
        {
            "company_id": c.co.id,
            "operating_unit_id": c.ou.id,
            "mushak_no": "B6-%s" % next(_SEQ),
            "invoice_ref": "AR/%s" % next(_SEQ),
            "invoice_date": c.today,
            "supplier_name": c.co.name,
            "supplier_bin": BIN,
            "customer_name": "B6 customer",
            "taxable_amount": taxable,
            "vat_amount": vat,
            "total_payable": taxable + vat,
            "treatment_summary": "SVC: standard_15 @ 15%",
        }
    )


def _invoice_gl(c, taxable, vat):
    return _entry(c, [(c.ar, taxable + vat, 0.0), (c.revenue, 0.0, taxable), (c.vat_out, 0.0, vat)])


def _legs(c, move):
    """code -> (debit, credit) of a posted entry's carrying lines."""
    legs = {}
    for ln in move.line_ids:
        if round(ln.debit, 2) or round(ln.credit, 2):
            legs[ln.account_id.code] = (round(ln.debit, 2), round(ln.credit, 2))
    return legs


def _prepared_reconciled(c):
    """The period's 9.1 prepared from the register and reconciled."""
    ret = c.cenv[RET].create({"period": c.period})
    ret.with_user(c.acct).action_prepare()
    ret.with_user(c.acct).action_subledger_reconciliation()
    return ret


class StubEvat:
    def build_payload(self, **kw):
        return kw

    def submit_return(self, payload):
        return types.SimpleNamespace(
            status="ACCEPTED", ack_token="ACK-B6-1", filed_at="", validation_messages=[]
        )


def _file_online(c, ret):
    for key in ("declarant_name", "declarant_designation", "declarant_nid"):
        c.env["ir.config_parameter"].sudo().set_param("cd_tax_engine_bd.%s" % key, "B6 %s" % key)
    return ret.with_user(c.filer).action_file_online(client=StubEvat())


def _event(c, event_type, model, record, payload):
    return {
        "event_id": "evt-b6-%s" % next(_SEQ),
        "event_type": event_type,
        "aggregate": model,
        "aggregate_id": record.id,
        "payload": payload,
        "metadata": {},
        "company_id": c.co.id,
    }


# ============================================================== M51-F4: the GL
def _note_via_correction(c, r, kind, taxable, vat, reason="Price reduction"):
    """The governed path: an accountant asks, a different Accounting
    Administrator decides — the note and its VAT leg issue together."""
    corr = c.as_(c.acct)["fix.mushak.correction"].create(
        {
            "register_id": r.id,
            "correction_type": kind,
            "taxable_amount": taxable,
            "vat_amount": vat,
            "reason": reason,
        }
    )
    corr.with_user(c.mgr).action_approve()
    return corr


def test_67_note_posts_its_negative_vat_leg_and_reconciliation_clears(c):
    r = _reg(c, 10000.0, 1500.0)
    _invoice_gl(c, 10000.0, 1500.0)
    corr = _note_via_correction(c, r, "credit_note", 2000.0, 300.0)
    note = corr.note_id
    assert (note.row_type, note.vat_amount, note.original_id) == ("credit_note", -300.0, r)
    # the register row is linked to the posted entry of its VAT effect
    assert note.posted and note.move_id.state == "posted"
    legs = _legs(c, note.move_id)
    assert legs.get(c.vat_out.code) == (300.0, 0.0)  # Dr VAT output: liability falls
    assert legs.get(c.counter.code) == (0.0, 300.0)  # Cr the counter-account
    ret = _prepared_reconciled(c)
    assert ret.output_vat == 1200.0
    assert (ret.subledger_status, ret.subledger_output_variance) == (
        "reconciled",
        0.0,
    ), ret.subledger_notes


def test_68_note_posts_its_vat_leg_and_reconciliation_clears(c):
    r = _reg(c, 10000.0, 1500.0)
    _invoice_gl(c, 10000.0, 1500.0)
    corr = _note_via_correction(c, r, "debit_note", 1000.0, 150.0, "Under-billed service")
    note = corr.note_id
    assert (note.row_type, note.vat_amount, note.total_payable) == ("debit_note", 150.0, 1150.0)
    assert note.posted and note.move_id.state == "posted"
    legs = _legs(c, note.move_id)
    assert legs.get(c.counter.code) == (150.0, 0.0)
    assert legs.get(c.vat_out.code) == (0.0, 150.0)
    ret = _prepared_reconciled(c)
    assert ret.output_vat == 1650.0
    assert ret.subledger_status == "reconciled", ret.subledger_notes


def test_zero_vat_note_carries_no_gl_leg(c):
    r = _reg(c, 10000.0, 1500.0)
    corr = _note_via_correction(c, r, "credit_note", 500.0, 0.0, "Value correction only")
    note = corr.note_id
    assert (note.vat_amount, note.posted) == (0.0, False)
    assert not note.move_id
    # `posted` still needs its posted GL entry (T08 / A08 M51-2)
    _refused(note.sudo().write, {"posted": True}, match="no posted GL entry")


def test_service_note_contract_posts_no_vat_leg(c):
    """M20's credit note and the counter refund call _fix_issue_note WITHOUT
    the GL flag: they post their own full reversal entry, so the service
    contract stays register-only (posting here too would double the VAT)."""
    r = _reg(c, 10000.0, 1500.0)
    note = c.cenv[REG]._fix_issue_note(r, "credit_note", 2000.0, 300.0, "Credit note")
    assert (note.vat_amount, note.posted) == (-300.0, False)
    assert not note.move_id and not c.cenv["account.move"].search(
        [("journal_id", "=", c.journal.id)]
    )


def test_note_gl_fails_closed_without_the_counter_account(c):
    r = _reg(c, 10000.0, 1500.0)
    c.env["ir.config_parameter"].sudo().set_param(NOTE_COUNTER_PARAM, "")
    corr = c.as_(c.acct)["fix.mushak.correction"].create(
        {
            "register_id": r.id,
            "correction_type": "credit_note",
            "taxable_amount": 2000.0,
            "vat_amount": 300.0,
            "reason": "Price reduction",
        }
    )
    with pytest.raises(UserError, match=NOTE_COUNTER_PARAM), c.env.cr.savepoint():
        corr.with_user(c.mgr).action_approve()
    # nothing was issued and nothing posted (the pair is atomic)
    assert not c.cenv[REG].search([("row_type", "=", "credit_note"), ("original_id", "=", r.id)])
    corr.invalidate_recordset()
    assert corr.state == "draft" and not corr.note_id


def test_note_gl_fails_closed_without_a_general_journal(c):
    r = _reg(c, 10000.0, 1500.0)
    c.cenv["account.journal"].search(
        [("company_id", "=", c.co.id), ("type", "=", "general")]
    ).sudo().unlink()
    corr = c.as_(c.acct)["fix.mushak.correction"].create(
        {
            "register_id": r.id,
            "correction_type": "credit_note",
            "taxable_amount": 2000.0,
            "vat_amount": 300.0,
            "reason": "Price reduction",
        }
    )
    with pytest.raises(UserError, match="general journal"), c.env.cr.savepoint():
        corr.with_user(c.mgr).action_approve()
    assert not c.cenv[REG].search([("row_type", "=", "credit_note"), ("original_id", "=", r.id)])


def test_note_gl_posts_only_through_the_second_person_gate(c):
    """SoD: the Accounting Administrator who asked for the correction cannot
    issue the note (and with it its GL leg); a DIFFERENT Accounting
    Administrator decides. There is no other path that posts a note's VAT."""
    r = _reg(c, 10000.0, 1500.0)
    moves_before = c.cenv["account.move"].search_count(
        [("company_id", "=", c.co.id), ("journal_id", "=", c.journal.id)]
    )
    corr = c.as_(c.requester)["fix.mushak.correction"].create(
        {
            "register_id": r.id,
            "correction_type": "credit_note",
            "taxable_amount": 2000.0,
            "vat_amount": 300.0,
            "reason": "Price reduction",
        }
    )
    _refused(corr.with_user(c.requester).action_approve, match="Segregation of duties")
    assert not c.cenv[REG].search([("row_type", "=", "credit_note"), ("original_id", "=", r.id)])
    assert (
        c.cenv["account.move"].search_count(
            [("company_id", "=", c.co.id), ("journal_id", "=", c.journal.id)]
        )
        == moves_before
    )
    # the decider's approval issues the note WITH its GL leg, atomically
    corr.with_user(c.mgr).action_approve()
    note = corr.note_id
    assert (note.row_type, note.vat_amount, note.posted) == ("credit_note", -300.0, True)
    assert note.move_id.state == "posted" and corr.state == "approved"


# ==================================================== M51-F10: the consumers
def test_the_consumers_are_registered(c):
    expected = {
        "cd_tax_engine_bd.consumer_vat_subledger_variance_risk": (
            "vat_subledger.variance_detected",
            RET,
            "consume_vat_subledger_variance",
        ),
        "cd_tax_engine_bd.consumer_tax_notice_overdue_risk": (
            "tax.notice.overdue",
            NOTICE,
            "consume_notice_overdue",
        ),
        "cd_tax_engine_bd.consumer_vat_return_filed_evidence": (
            "vat_return.filed",
            RET,
            "consume_vat_return_filed",
        ),
        "cd_tax_engine_bd.consumer_vat_return_filed_online_evidence": (
            "vat_return.filed_online",
            RET,
            "consume_vat_return_filed",
        ),
    }
    for xmlid, (event_type, model, method) in expected.items():
        sub = c.env.ref(xmlid)
        assert (sub.event_type, sub.model, sub.method) == (event_type, model, method)
        assert sub.active


def test_variance_consumer_opens_one_risk_item_replays_create_nothing(c):
    _reg(c, 10000.0, 1500.0)  # no GL: the reconciliation detects the variance
    ret = c.cenv[RET].create({"period": c.period})
    ret.with_user(c.acct).action_prepare()
    ret.with_user(c.acct).action_subledger_reconciliation()
    assert ret.subledger_status == "variance_detected"
    event = _event(
        c,
        "vat_subledger.variance_detected",
        RET,
        ret,
        {"period": ret.period, "output_variance": 1500.0, "input_variance": 0.0},
    )
    # the consumer is the relay's: a direct call by a finance user is refused
    _refused(c.as_(c.acct)[RET].consume_vat_subledger_variance, event, match="relay only")
    first = c.cenv[RET].consume_vat_subledger_variance(event)
    second = c.cenv[RET].consume_vat_subledger_variance(event)  # the replay
    assert first == second and first.category == "compliance" and first.state == "open"
    assert first.company_id == c.co and "IRB-09" in first.mitigation
    name = "[M51] VAT sub-ledger variance %s" % ret.period
    assert len(c.cenv[RISK].search([("name", "=", name), ("company_id", "=", c.co.id)])) == 1


def _overdue_notice(c, **kw):
    vals = {
        "notice_type": "show_cause",
        "tax_kind": "vat",
        "authority": "VAT Division-1, Dhaka",
        "notice_ref": "NBR-SC-%s" % next(_SEQ),
        "received_on": c.today - timedelta(days=10),
        "period_from": c.today - timedelta(days=60),
        "period_to": c.today - timedelta(days=10),
        "subject": "Explain the output VAT of the period",
        "response_due": c.today - timedelta(days=1),
        "disputed_amount": 25000.0,
    }
    vals.update(kw)
    return c.cenv[NOTICE].create(vals)


def test_overdue_notice_publishes_and_opens_one_risk_item(c):
    notice = _overdue_notice(c)
    c.cenv[NOTICE]._cron_notice_deadlines()
    outbox = c.cenv["fix.event.outbox"].search(
        [("event_type", "=", "tax.notice.overdue"), ("aggregate_id", "=", notice.id)]
    )
    assert len(outbox) == 1, "the deadline cron publishes tax.notice.overdue"
    event = outbox[0]._relay_event_dict()
    first = c.cenv[NOTICE].consume_notice_overdue(event)
    replay = c.cenv[NOTICE].consume_notice_overdue(event)  # the daily republish
    assert first == replay and first.category == "compliance" and first.state == "open"
    assert notice.notice_ref in first.name
    name = "[M51] NBR notice %s (%s) overdue" % (notice.name, notice.notice_ref)
    assert len(c.cenv[RISK].search([("name", "=", name), ("company_id", "=", c.co.id)])) == 1
    # an answered notice opens nothing: the risk owner keeps the open entry
    answered = _overdue_notice(c, state="responded")
    answered_event = _event(c, "tax.notice.overdue", NOTICE, answered, {"due": str(c.today)})
    assert c.cenv[NOTICE].consume_notice_overdue(answered_event)["created"] == 0


def test_filed_return_discharges_the_compliance_obligation_once(c):
    _reg(c, 10000.0, 1500.0)
    _invoice_gl(c, 10000.0, 1500.0)
    ret = _prepared_reconciled(c)
    _file_online(c, ret)
    assert (ret.state, ret.nbr_confirmation) == ("filed", "ACK-B6-1")

    framework = c.cenv["fix.compliance.framework"].create(
        {"name": "B6 VAT framework", "code": "iso_9001", "company_id": c.co.id}
    )
    obligation = c.cenv["fix.compliance.obligation"].create(
        {
            "framework_id": framework.id,
            "name": "Monthly VAT return (Mushak 9.1)",
            "clause_reference": "VAT Act 2012 s.64",
            "recurrence": "monthly",
            "company_id": c.co.id,
        }
    )
    decoy = c.cenv["fix.compliance.obligation"].create(
        {
            "framework_id": framework.id,
            "name": "Annual income tax return",
            "clause_reference": "ITA 2023 s.143",
            "recurrence": "annual",
            "company_id": c.co.id,
        }
    )
    Occ = c.cenv["fix.compliance.obligation.occurrence"]
    occ = Occ.create({"obligation_id": obligation.id, "period": ret.period, "due_on": c.today})
    other = Occ.create({"obligation_id": decoy.id, "period": ret.period, "due_on": c.today})

    event = _event(
        c,
        "vat_return.filed",
        RET,
        ret,
        {"period": ret.period, "nbr_confirmation": "ACK-B6-1", "net_payable": ret.net_payable},
    )
    assert c.cenv[RET].consume_vat_return_filed(event)["discharged"] == 1
    occ.invalidate_recordset()
    other.invalidate_recordset()
    assert occ.state == "discharged" and "ACK-B6-1" in occ.evidence_ref
    assert occ.discharged_on == c.today  # the relay's system discharge is dated
    assert other.state == "scheduled"  # the tax module never guesses an obligation
    # the relay may redeliver: a discharged occurrence is met, not re-discharged
    assert c.cenv[RET].consume_vat_return_filed(event)["discharged"] == 0
    occ.invalidate_recordset()
    assert occ.state == "discharged"
    # without the NBR acknowledgement there is no evidence to discharge on
    # (BRU-GRC-12: the discharge stays the compliance officer's decision)
    noack = _event(c, "vat_return.filed", RET, ret, {"period": ret.period})
    assert c.cenv[RET].consume_vat_return_filed(noack)["discharged"] == 0
