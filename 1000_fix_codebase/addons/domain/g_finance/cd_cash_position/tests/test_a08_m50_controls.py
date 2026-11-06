# cd_cash_position — A08 workflow audit, M50 Treasury: the controls the gap
# probes (working/A08_evidence/probes/m50/probe_m50.py) proved missing.
#
# Each test is named after its probe id and runs the SAME attack as a
# NON-ADMIN user holding the real finance role (created in the transaction):
#   plain   base.group_user
#   bill    + account.group_account_invoice (Billing)
#   acct    + account.group_account_user    (Accountant: prepares)
#   acct2   second accountant               (imports statements, matches)
#   mgr     + account.group_account_manager (Accounting Administrator: releases)
#   mgr2    second Accounting Administrator
#   auth    Accounting Administrator + DOFA Tier 2 (authorises through M63)
# and asserts the control HOLDS; test_ref_* run the proper path (an
# accountant prepares, a different Accounting Administrator releases, an
# imported debit confirms). Arrangement that is not under test (accounts,
# journals, a counted cash shift, a delivered consignment) is done as
# superuser and says so. Everything rolls back (odoo_env).
from __future__ import annotations

import base64
import itertools
import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

pytestmark = [pytest.mark.financial]

REFUSED = (UserError, ValidationError, AccessError)
_SEQ = itertools.count(1)
ROLES = (
    "branch_cash",
    "cash_in_transit",
    "cod_clearing",
    "rider_shortage",
    "gateway_fees",
    "channel_clearing",
    "outgoing_clearing",
    "interest_expense",
    "bank_charges",
    "cash_shortage",
    "cheque_returned",
)
PEX = "fix.payment.execution"
LINE = "fix.bank.statement.line"
ADMIN = "account.group_account_manager"


class Ctx:
    pass


def _user(env, login, groups=()):
    Users = env["res.users"].with_context(no_reset_password=True)
    gids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    return Users.create(
        {
            "name": login,
            "login": login,
            "group_ids": [(6, 0, gids)],
            "assigned_operating_unit_ids": [(6, 0, ou.ids)],
            "default_operating_unit_id": ou.id,
            "company_id": env.company.id,
            "company_ids": [(6, 0, [env.company.id])],
        }
    )


def _confirmed(bank):
    """B2 contract: a payee account confirmed by the bank-change proposal
    (system-set) — arrangement, when the flag exists."""
    if hasattr(bank, "_fix_mark_confirmed"):
        bank.sudo()._fix_mark_confirmed("B1 test call-back", None)
    return bank


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = Ctx()
    x.env = env
    n = next(_SEQ)
    x.n = n
    x.company = env.company
    x.ou = env["operating.unit"].search([("company_id", "=", x.company.id)], limit=1)
    x.today = fields.Date.context_today(env.user)
    x.acc = {}
    for i, role in enumerate(ROLES):
        acc = env["account.account"].create(
            {
                "code": "B1M%02d%02d" % (n % 100, i),
                "name": "B1 M50 %s" % role,
                "account_type": "expense"
                if role.endswith(("fees", "expense", "charges", "shortage"))
                else "asset_current",
            }
        )
        x.acc[role] = acc
        env["ir.config_parameter"].sudo().set_param(
            "cd_cash_position.account_code.%s" % role, acc.code
        )
    x.expense = env["account.account"].create(
        {"code": "B1MX%02d" % (n % 100), "name": "B1 petty expense", "account_type": "expense"}
    )
    x.petty_acc = env["account.account"].create(
        {"code": "B1MP%02d" % (n % 100), "name": "B1 petty cash", "account_type": "asset_current"}
    )
    x.bank = env["account.journal"].create(
        {"name": "B1 Bank %s" % n, "type": "bank", "code": "B1B%s" % (n % 100)}
    )
    x.bank_acc = x.bank.default_account_id
    entity = env["fix.entity"].search([("company_id", "=", x.company.id)], limit=1) or env[
        "fix.entity"
    ].create(
        {"code": "E%s" % x.company.id, "legal_name": x.company.name, "company_id": x.company.id}
    )
    x.branch = env["fix.branch"].create(
        {
            "code": "B1BR%s" % n,
            "name": "B1 Branch %s" % n,
            "entity_id": entity.id,
            "operating_unit_id": x.ou.id,
        }
    )
    x.rider = env["hr.employee"].create({"name": "B1 Rider %s" % n})
    x.custodian = env["hr.employee"].create({"name": "B1 Custodian %s" % n})
    x.plain = _user(env, "b1m50_plain%s" % n)
    x.bill = _user(env, "b1m50_bill%s" % n, ["account.group_account_invoice"])
    x.acct = _user(env, "b1m50_acctA%s" % n, ["account.group_account_user"])
    x.acct2 = _user(env, "b1m50_acctB%s" % n, ["account.group_account_user"])
    x.mgr = _user(env, "b1m50_mgrA%s" % n, [ADMIN])
    x.mgr2 = _user(env, "b1m50_mgrB%s" % n, [ADMIN])
    x.auth = _user(env, "b1m50_auth%s" % n, [ADMIN, "cd_entity_config.group_dofa_tier_2"])
    x.vendor = env["res.partner"].create({"name": "B1 Vendor %s" % n})
    x.accomplice = env["res.partner"].create({"name": "B1 Accomplice %s" % n})
    x.vendor_bank = _confirmed(
        env["res.partner.bank"].create(
            {
                "partner_id": x.vendor.id,
                "acc_number": "B1VEND%s" % n,
                "fix_routing_number": "123456789",
            }
        )
    )
    x.mule_bank = _confirmed(
        env["res.partner.bank"].create(
            {
                "partner_id": x.accomplice.id,
                "acc_number": "B1MULE%s" % n,
                "fix_routing_number": "987654321",
            }
        )
    )
    return x


def pay(c, user=None, amount=4500.0, **kw):
    vals = {
        "operating_unit_id": c.ou.id,
        "payee": c.vendor.name,
        "partner_id": c.vendor.id,
        "partner_bank_id": c.vendor_bank.id,
        "amount": amount,
        "journal_id": c.bank.id,
        "rail": "beftn",
        "method": "bank_transfer",
        "dofa_justification": "B1 test instruction",
    }
    vals.update(kw)
    return c.env[PEX].with_user(user or c.acct).create(vals)


def _authorise(c, p, approver=None):
    approver = approver or c.auth
    task = p.approval_request_id.sudo().task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == approver
    )
    assert task, "no inbox task for %s (routed to %s)" % (
        approver.login,
        p.approval_request_id.sudo().task_ids.mapped("assigned_user_id.login"),
    )
    task.with_user(approver).action_approve(comment="ok")


def released(c, amount=4500.0, **kw):
    """The proper path up to release: acct prepares, auth authorises through
    the M63 inbox, mgr releases."""
    p = pay(c, amount=amount, **kw)
    p.with_user(c.acct).action_prepare()
    if p._approval_needed():
        _authorise(c, p)
    p.with_user(c.mgr).action_release()
    assert p.state == "sent"
    return p


def stmt(c, rows, user=None):
    """Import a bank statement file (CSV) — the only way lines exist."""
    n = next(_SEQ)
    body = "Date,Amount,Reference,Description\n" + "".join(
        "%s,%.2f,%s,%s\n" % (day or c.today, amt, ref, "%s-%s" % (desc or "line", n))
        for amt, ref, desc, day in [((*r, None, None))[:4] for r in rows]
    )
    imp = (
        c.env["fix.bank.statement.import"]
        .with_user(user or c.acct2)
        .create(
            {
                "journal_id": c.bank.id,
                "file": base64.b64encode(body.encode()),
                "format_type": "csv",
                "filename": "b1-%s.csv" % n,
            }
        )
    )
    imp.with_user(user or c.acct2).action_import()
    assert imp.state == "imported", imp.state
    return imp.line_ids


def bal(c, account):
    lines = c.env["account.move.line"].search(
        [("account_id", "=", account.id), ("parent_state", "=", "posted")]
    )
    return round(sum(lines.mapped("balance")), 2)


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    ctl = g.P03GenericApiController()
    mw = getattr(
        g.P03GenericApiController.model_write,
        "original_endpoint",
        g.P03GenericApiController.model_write,
    )
    old = getattr(g, "request", None)

    def as_user(user):
        g.request = types.SimpleNamespace(env=c.env(user=user.id))

    as_user(c.acct)
    try:
        yield types.SimpleNamespace(write=lambda **kw: mw(ctl, **kw), as_user=as_user)
    finally:
        g.request = old


# =================================================================== payments
def test_m50_p01_plain_user_cannot_create_instruction(c):
    with pytest.raises(REFUSED):
        pay(
            c,
            user=c.plain,
            amount=9500000.0,
            partner_id=c.accomplice.id,
            partner_bank_id=c.mule_bank.id,
        )


def test_m50_p02_one_accountant_cannot_release_or_confirm_own_payment(c):
    p = pay(c)
    p.with_user(c.acct).action_prepare()
    with pytest.raises(UserError, match="Accounting Administrator"):
        p.with_user(c.acct).action_release()
    # an administrator who created and prepared it cannot release it either
    q = pay(c, user=c.mgr, amount=4600.0)
    q.with_user(c.mgr).action_prepare()
    _authorise(c, q)
    with pytest.raises(UserError, match="Segregation of duties"):
        q.with_user(c.mgr).action_release()
    # the DOFA authoriser is not also the releaser (dual authorisation)
    r = pay(c, amount=4700.0)
    r.with_user(c.acct).action_prepare()
    _authorise(c, r)
    with pytest.raises(UserError, match="Segregation of duties"):
        r.with_user(c.auth).action_release()
    # the releaser cannot confirm his own release from a statement he imported
    s = released(c, amount=4800.0)
    lines = stmt(c, [(-4800.0, s.name)], user=c.mgr)
    lines.with_user(c.mgr).write({"matched_payment_id": s.id})
    with pytest.raises(UserError, match="Segregation of duties"):
        lines.with_user(c.mgr).action_confirm_manual_match()
    assert s.state == "sent"


def test_m50_p03_amount_above_ceiling_needs_dofa_authorisation(c):
    tier5 = _user(c.env, "b1m50_t5_%s" % c.n, [ADMIN, "cd_entity_config.group_dofa_tier_5"])
    p = pay(c, amount=50000000.0, rail="rtgs")
    p.with_user(c.acct).action_prepare()
    assert p.approval_state == "pending" and p._dofa_current_tier() == "tier_5"
    assigned = p.approval_request_id.sudo().task_ids.mapped("assigned_user_id")
    assert tier5 in assigned and c.acct not in assigned
    with pytest.raises(UserError, match="approv"):
        p.with_user(c.mgr).action_release()
    # a direct DOFA approval (outside the inbox) is refused
    with pytest.raises(UserError):
        p.with_user(tier5).action_dofa_approve()
    _authorise(c, p, tier5)
    p.with_user(c.mgr).action_release()
    assert p.state == "sent" and p.dofa_approved_by == tier5


def test_m50_p03b_single_releaser_ceiling_is_configuration(c):
    c.env["ir.config_parameter"].sudo().set_param(
        "cd_cash_position.release_single_ceiling", "10000"
    )
    p = pay(c, amount=5000.0)
    p.with_user(c.acct).action_prepare()
    assert not p._approval_needed() and p.approval_state == "none"
    p.with_user(c.mgr).action_release()
    assert p.state == "sent"
    big = pay(c, amount=10000.01)
    big.with_user(c.acct).action_prepare()
    assert big.approval_state == "pending"


def test_m50_p04_beneficiary_bank_pinned_after_release(c):
    p = released(c)
    with pytest.raises(REFUSED):
        p.with_user(c.acct).write({"partner_bank_id": c.mule_bank.id, "payee": c.accomplice.name})
    with pytest.raises(REFUSED):
        p.with_user(c.mgr).write({"partner_bank_id": c.mule_bank.id})
    assert p.partner_bank_id == c.vendor_bank and p.released_acc_number == c.vendor_bank.acc_number


def test_m50_p04b_change_after_preparation_voids_authorisation(c):
    p = pay(c)
    p.with_user(c.acct).action_prepare()
    _authorise(c, p)
    assert p.approval_state == "approved" and p.dofa_approved
    p.with_user(c.acct).write({"amount": 4400.0})
    assert p.state == "pending" and p.approval_state == "none" and not p.dofa_approved


def test_m50_p05_amount_pinned_gl_posts_released_amount(c):
    p = released(c, amount=4500.0)
    with pytest.raises(REFUSED):
        p.with_user(c.acct).write({"amount": 45000.0})
    stmt(c, [(-4500.0, p.name)])
    c.env[LINE].with_user(c.acct2).auto_match()
    assert p.state == "executed"
    assert bal(c, c.bank_acc) == -4500.0 and p.released_amount == 4500.0


def test_m50_p06_state_cannot_be_forged_by_orm(c):
    p = pay(c, amount=7000.0)
    for user in (c.acct, c.mgr):
        with pytest.raises(REFUSED):
            p.with_user(user).write({"state": "executed", "confirmation_source": "statement"})
    assert p.state == "pending"


def test_m50_p07_state_cannot_be_forged_via_p03(c, p03):
    p = pay(c, amount=7100.0)
    res = p03.write(model=PEX, record_id=p.id, values={"state": "executed"})
    assert "error" in res and p.state == "pending"


def test_m50_p08_source_posts_gl_is_computed_not_typed(c):
    p = pay(c, amount=8800.0)
    assert not p.source_posts_gl
    with pytest.raises(REFUSED):
        p.with_user(c.acct).write({"source_posts_gl": True})
    with pytest.raises(REFUSED):
        pay(c, amount=8900.0, source_posts_gl=True)
    run_line = (
        c.env[PEX]
        .sudo()
        .create(
            {
                "operating_unit_id": c.ou.id,
                "source_model": "fix.payment.run.line",
                "source_id": 990000 + c.n,
                "payee": "x",
                "amount": 1.0,
            }
        )
    )
    assert run_line.source_posts_gl
    # a manual payment that leaves the bank reaches the GL
    released_p = released(c, amount=8800.0, duplicate_reason="second leg")
    stmt(c, [(-8800.0, released_p.name)])
    c.env[LINE].with_user(c.acct2).auto_match()
    assert released_p.move_id and released_p.move_id.state == "posted"


def test_m50_p09_legacy_action_execute_refused_to_users(c):
    p = pay(c, amount=1200.0)
    for user in (c.acct, c.mgr):
        with pytest.raises(AccessError):
            p.with_user(user).action_execute()
    ev = c.env["fix.event.outbox"].search(
        [("event_type", "=", "payment.executed"), ("aggregate_id", "=", p.id)]
    )
    assert not ev and p.state == "pending"


def test_m50_p10_billing_user_cannot_release(c):
    p = pay(c, amount=100.0)
    p.with_user(c.acct).action_prepare()
    with pytest.raises(REFUSED):
        p.with_user(c.bill).action_release()


def test_m50_p10b_plain_user_cannot_release(c):
    p = pay(c, amount=100.0)
    p.with_user(c.acct).action_prepare()
    with pytest.raises(REFUSED):
        p.with_user(c.plain).action_release()


def _claim(c, amount=640.0):
    employee = c.env["hr.employee"].create({"name": "B1 claimant %s" % c.n})
    claim = c.env["fix.expense.claim"].create(
        {
            "operating_unit_id": c.ou.id,
            "employee_id": employee.id,
            "description": "Fuel",
            "amount": amount,
        }
    )
    # arrangement: the claim's lines and approval are M52's workflow (B2); the
    # amount is the sum of its lines, set here directly
    c.env.flush_all()
    c.env.cr.execute(
        "UPDATE fix_expense_claim SET amount=%s, state='approved', approved_by=%s WHERE id=%s",
        (amount, c.mgr2.id, claim.id),
    )
    claim.invalidate_recordset()
    return claim


def test_m50_p11_payment_requested_consumer_is_idempotent(c):
    claim = _claim(c)
    ev = {
        "aggregate": "fix.expense.claim",
        "aggregate_id": claim.id,
        "payload": {
            "amount": 640.0,
            "operating_unit_id": c.ou.id,
            "invoice_ref": "EXP/%s" % claim.id,
        },
    }
    Relay = c.env[PEX].sudo()  # the event relay runs consumers as the system
    a = Relay.consume_payment_requested(ev)
    b = Relay.consume_payment_requested(ev)
    assert a == b and a.state == "pending" and a.source_pinned
    assert (a.amount, a.source_approved_by_id) == (640.0, c.mgr2)
    # pinned: treasury cannot change what the claim approved
    with pytest.raises(UserError, match="pays what"):
        a.with_user(c.acct).write({"amount": 6400.0})
    # the source's approver never authorises or releases it
    assert c.mgr2 in a._fix_conflicted_users()


def test_m50_p11b_consumer_refuses_users_and_forged_payloads(c):
    claim = _claim(c, 700.0)
    ev = {"aggregate": "fix.expense.claim", "aggregate_id": claim.id, "payload": {"amount": 7000.0}}
    with pytest.raises(AccessError):
        c.env[PEX].with_user(c.acct).consume_payment_requested(ev)
    with pytest.raises(UserError, match="document says"):
        c.env[PEX].sudo().consume_payment_requested(ev)
    with pytest.raises(UserError, match="no such document"):
        c.env[PEX].sudo().consume_payment_requested(
            {"aggregate": "fix.expense.claim", "aggregate_id": 99999999, "payload": {}}
        )


def test_m50_p11c_request_payment_contract(c):
    claim = _claim(c, 333.0)
    Exec = c.env[PEX]
    p = Exec._fix_request_payment(
        "fix.expense.claim", claim.id, c.vendor, c.vendor_bank, 333.0, "BDT", "EXP/X", c.mgr2
    )
    assert (p.state, p.partner_bank_id, p.amount, p.source_pinned) == (
        "pending",
        c.vendor_bank,
        333.0,
        True,
    )
    assert (
        Exec._fix_request_payment(
            "fix.expense.claim", claim.id, c.vendor, c.vendor_bank, 333.0, "BDT", "EXP/X", c.mgr2
        )
        == p
    )
    with pytest.raises(UserError, match="different terms"):
        Exec._fix_request_payment(
            "fix.expense.claim", claim.id, c.vendor, c.mule_bank, 333.0, "BDT", "EXP/X", c.mgr2
        )
    with pytest.raises(ValidationError):  # the account must be the payee's own
        Exec._fix_request_payment(
            "fix.employee.advance.excess",
            880000 + c.n,
            c.vendor,
            c.mule_bank,
            1.0,
            "BDT",
            "",
            False,
        )
    # a user cannot type a sourced instruction
    with pytest.raises(UserError, match="_fix_request_payment"):
        pay(c, source_model="fix.vendor.invoice", source_id=1)


def test_m50_p12_duplicate_instruction_needs_a_reason(c):
    a = pay(c, amount=31000.0)
    a.with_user(c.acct).action_prepare()
    b = pay(c, amount=31000.0, source_model="manual", source_id=a.source_id + 1)
    with pytest.raises(UserError, match="repeats"):
        b.with_user(c.acct).action_prepare()
    b.with_user(c.acct).write({"duplicate_reason": "Second instalment per contract clause 4"})
    b.with_user(c.acct).action_prepare()
    assert b.state == "prepared"


def test_m50_p12b_manual_instructions_in_the_same_second_get_distinct_keys(c):
    from unittest import mock

    frozen = fields.Datetime.now()
    with mock.patch.object(fields.Datetime, "now", lambda *a, **k: frozen):
        a = pay(c, amount=100.0)
        b = pay(c, amount=200.0, payee="Other payee")
    assert (a.source_model, b.source_model) == ("manual", "manual")
    assert a.source_id != b.source_id and a.name != b.name


def test_m50_p13_typed_reference_does_not_confirm(c):
    p = released(c, amount=990.0)
    p.with_user(c.acct2).write({"bank_reference": "x"})
    with pytest.raises(UserError, match="not bank evidence"):
        p.with_user(c.acct2).action_confirm_bank()
    assert p.state == "sent" and not p.bank_confirmed
    # the reference identifies an IMPORTED debit -> confirmed by the statement
    stmt(c, [(-990.0, "BEFTN-REF-%s" % c.n)])
    p.with_user(c.acct2).write({"bank_reference": "BEFTN-REF-%s" % c.n})
    p.with_user(c.acct2).action_confirm_bank()
    assert (p.state, p.confirmation_source, p.bank_confirmed) == ("executed", "statement", True)


def test_ref_m50_p14_proper_release_confirm_posts_balanced(c):
    p = pay(c, amount=4500.0)
    p.with_user(c.acct).action_prepare()
    assert p.state == "prepared" and p.approval_state == "pending"
    _authorise(c, p)
    p.with_user(c.mgr).action_release()
    assert (p.sent_by_id, p.prepared_by_id, p.dofa_approved_by) == (c.mgr, c.acct, c.auth)
    assert "%.2f" % 4500.0 in p.instruction_attachment_id.raw.decode()
    stmt(c, [(-4500.0, p.name)])
    assert c.env[LINE].with_user(c.acct2).auto_match() == 1
    assert p.state == "executed" and p.bank_confirmed and p.move_id.state == "posted"
    assert bal(c, c.bank_acc) == -4500.0 and bal(c, c.acc["outgoing_clearing"]) == 4500.0


def test_m50_p15_release_calls_the_payable_bank_contract(c, monkeypatch):
    """B2 contract: _fix_assert_payable_bank(bank) is asked before release."""
    Bank = type(c.env["res.partner.bank"])
    asked = []

    def refuse(self, bank):
        asked.append(bank.id)
        raise UserError("unconfirmed payee account")

    monkeypatch.setattr(Bank, "_fix_assert_payable_bank", refuse, raising=False)
    p = pay(c)
    p.with_user(c.acct).action_prepare()
    _authorise(c, p)
    with pytest.raises(UserError, match="unconfirmed"):
        p.with_user(c.mgr).action_release()
    assert asked == [c.vendor_bank.id] and p.state == "prepared"


def test_m50_p16_no_release_into_a_locked_period(c):
    p = pay(c, value_date=fields.Date.to_date("2001-03-01"))
    p.with_user(c.acct).action_prepare()
    _authorise(c, p)
    lock = c.company.fiscalyear_lock_date
    if not lock or lock < fields.Date.to_date("2001-03-01"):
        c.company.sudo().write({"fiscalyear_lock_date": fields.Date.to_date("2001-12-31")})
    with pytest.raises(UserError, match="closed accounting period"):
        p.with_user(c.mgr).action_release()


def test_m50_p17_payee_account_must_be_the_payees_own(c):
    with pytest.raises(ValidationError):
        pay(c, partner_bank_id=c.mule_bank.id)


# =================================================================== reconciliation
def test_m50_r01_line_cannot_be_matched_to_nothing_by_write(c):
    ln = stmt(c, [(-2500.0, "UNKNOWN DEBIT")])
    with pytest.raises(REFUSED):
        ln.with_user(c.acct).write({"match_state": "manual"})
    assert ln.match_state == "unmatched"


def test_m50_r02_line_cannot_be_matched_to_nothing_via_p03(c, p03):
    ln = stmt(c, [(-2600.0, "UNKNOWN DEBIT 2")])
    res = p03.write(model=LINE, record_id=ln.id, values={"match_state": "auto"})
    assert "error" in res and ln.match_state == "unmatched"


def test_m50_r03_manual_match_amount_must_agree(c):
    p = released(c, amount=1000.0)
    ln = stmt(c, [(-999.0, p.name)])
    ln.with_user(c.acct).write({"matched_payment_id": p.id})
    with pytest.raises(UserError, match="Amounts differ"):
        ln.with_user(c.acct).action_confirm_manual_match()


def test_m50_r04_credit_line_never_confirms_outgoing_payment(c):
    p = released(c, amount=4500.0)
    ln = stmt(c, [(4500.0, p.name)])
    ln.with_user(c.acct2).write({"matched_payment_id": p.id})
    with pytest.raises(UserError, match="CREDIT"):
        ln.with_user(c.acct2).action_confirm_manual_match()
    assert p.state == "sent"


def test_m50_r05_auto_match_credit_does_not_confirm(c):
    p = released(c, amount=4321.0)
    stmt(c, [(4321.0, p.name)])
    c.env[LINE].with_user(c.acct2).auto_match()
    assert p.state == "sent"


def test_m50_r06_typed_statement_line_refused(c):
    with pytest.raises(REFUSED):
        c.env[LINE].with_user(c.acct).create(
            {"journal_id": c.bank.id, "date": c.today, "amount": -6500.0, "reference": "X"}
        )
    with pytest.raises(AccessError):
        c.env[LINE].with_user(c.acct).import_bank_feed("Date,Amount\n%s,-1.00\n" % c.today)
    # a typed line (superuser arrangement) is still not bank evidence
    typed = c.env[LINE].create(
        {"journal_id": c.bank.id, "date": c.today, "amount": -6500.0, "reference": "TYPED"}
    )
    p = released(c, amount=6500.0)
    typed.with_user(c.acct2).write({"matched_payment_id": p.id})
    with pytest.raises(UserError, match="not bank evidence"):
        typed.with_user(c.acct2).action_confirm_manual_match()
    assert not p.bank_confirmed


def test_m50_r07_matched_line_is_frozen(c):
    p = released(c, amount=700.0)
    ln = stmt(c, [(-700.0, p.name)])
    ln.with_user(c.acct2).write({"matched_payment_id": p.id})
    ln.with_user(c.acct2).action_confirm_manual_match()
    assert ln.match_state == "manual" and p.state == "executed"
    for vals in ({"amount": -70000.0}, {"matched_payment_id": False}, {"reference": "Z"}):
        with pytest.raises(REFUSED):
            ln.with_user(c.acct2).write(vals)


def test_m50_r08_duplicate_statement_file_refused(c):
    csv = "Date,Amount,Reference,Description\n%s,-100.00,DUPREF-B1-%s,test\n" % (c.today, c.n)
    imp = c.env["fix.bank.statement.import"].with_user(c.acct)
    a = imp.create(
        {"journal_id": c.bank.id, "file": base64.b64encode(csv.encode()), "format_type": "csv"}
    )
    a.action_import()
    b = imp.create(
        {"journal_id": c.bank.id, "file": base64.b64encode(csv.encode()), "format_type": "csv"}
    )
    b.action_import()
    assert b.state == "duplicate" and b.imported_count == 0
    with pytest.raises(REFUSED):
        a.with_user(c.acct).write({"state": "draft"})


def test_m50_r09_bank_charge_needs_a_second_person(c):
    ln = stmt(c, [(-250000.0, "TRF OUT 0099")], user=c.mgr)
    with pytest.raises(UserError, match="Accounting Administrator"):
        ln.with_user(c.acct).action_post_bank_charge()
    with pytest.raises(UserError, match="Segregation of duties"):
        ln.with_user(c.mgr).action_post_bank_charge()
    ln.with_user(c.mgr2).action_post_bank_charge()
    assert ln.matched_kind == "charge" and bal(c, c.acc["bank_charges"]) == 250000.0


def test_m50_r10_matched_state_requires_a_document(c):
    ln = stmt(c, [(-10.0, "R10")])
    with pytest.raises(ValidationError):
        ln._guarded().write({"match_state": "manual", "matched_kind": "payment"})


# =================================================================== imprest
def _fund(c, ceiling=10000.0, voucher_limit=5000.0, fill=True, custodian=None):
    fund = (
        c.env["fix.imprest.fund"]
        .with_user(c.mgr)
        .create(
            {
                "name": "B1 Petty %s" % next(_SEQ),
                "operating_unit_id": c.ou.id,
                "branch_id": c.branch.id,
                "custodian_id": (custodian or c.custodian).id,
                "imprest_limit": ceiling,
                "voucher_limit": voucher_limit,
                "account_id": c.env["account.account"]
                .create(
                    {
                        "code": "B1F%04d" % next(_SEQ),
                        "name": "B1 petty fund",
                        "account_type": "asset_current",
                    }
                )
                .id,
            }
        )
    )
    if fill:
        t = (
            c.env["fix.imprest.topup"]
            .with_user(c.acct)
            .create({"fund_id": fund.id, "amount": ceiling, "journal_id": c.bank.id})
        )
        t.with_user(c.mgr).action_approve()
        t.with_user(c.acct).action_pay()
    return fund


def _voucher(c, fund, amount, user=None):
    return (
        c.env["fix.imprest.voucher"]
        .with_user(user or c.acct)
        .create(
            {
                "fund_id": fund.id,
                "description": "taxi",
                "expense_account_id": c.expense.id,
                "amount": amount,
                "receipt_ref": "RCPT-%s" % next(_SEQ),
            }
        )
    )


def test_m50_i01_voucher_submitter_cannot_approve(c):
    v = _voucher(c, _fund(c), 500.0)
    v.with_user(c.acct).action_submit()
    with pytest.raises(UserError, match="Segregation"):
        v.with_user(c.acct).action_approve()


def test_m50_i02_voucher_submitter_stamp_cannot_be_rewritten(c):
    v = _voucher(c, _fund(c), 500.0)
    v.with_user(c.acct).action_submit()
    with pytest.raises(REFUSED):
        v.with_user(c.acct).write({"submitted_by_id": c.acct2.id})
    with pytest.raises(UserError):
        v.with_user(c.acct).action_approve()


def test_m50_i03_voucher_posts_the_approved_amount(c):
    fund = _fund(c)
    v = _voucher(c, fund, 500.0)
    v.with_user(c.acct).action_submit()
    v.with_user(c.acct2).action_approve()
    with pytest.raises(REFUSED):
        v.with_user(c.acct).write({"amount": 4900.0})
    v.with_user(c.acct).action_post()
    assert bal(c, c.expense) == 500.0 and v.approved_amount == 500.0


def test_m50_i04_voucher_state_cannot_be_forged(c):
    v = _voucher(c, _fund(c), 700.0)
    with pytest.raises(REFUSED):
        v.with_user(c.acct).write({"state": "approved"})
    with pytest.raises(UserError):
        v.with_user(c.acct).action_post()


def test_m50_i04b_custodian_cannot_approve(c):
    custodian = c.env["hr.employee"].create({"name": "B1 custodian user", "user_id": c.acct2.id})
    fund = _fund(c, custodian=custodian)
    v = _voucher(c, fund, 300.0)
    v.with_user(c.acct).action_submit()
    with pytest.raises(UserError, match="custodian"):
        v.with_user(c.acct2).action_approve()


def test_m50_i05_count_includes_approved_unposted_vouchers(c):
    fund = _fund(c)
    v = _voucher(c, fund, 2000.0)
    v.with_user(c.acct).action_submit()
    v.with_user(c.acct2).action_approve()
    cnt = (
        c.env["fix.imprest.count"]
        .with_user(c.acct)
        .create({"fund_id": fund.id, "counted_amount": 8000.0})
    )
    cnt.with_user(c.acct).action_reconcile()
    assert (cnt.state, cnt.variance, cnt.pending_vouchers_amount) == ("balanced", 0.0, 2000.0)


def test_m50_i06_count_variance_is_computed_not_typed(c):
    fund = _fund(c)
    cnt = (
        c.env["fix.imprest.count"]
        .with_user(c.acct)
        .create({"fund_id": fund.id, "counted_amount": 9950.0})
    )
    cnt.with_user(c.acct).action_reconcile()
    with pytest.raises(REFUSED):
        cnt.with_user(c.acct).write({"variance": -9000.0})
    with pytest.raises(REFUSED):
        cnt.with_user(c.acct).write({"counted_amount": 1000.0})
    cnt.with_user(c.mgr).action_book_variance()
    assert bal(c, c.acc["cash_shortage"]) == 50.0


def test_m50_i06b_variance_recomputed_at_booking(c):
    fund = _fund(c)
    cnt = (
        c.env["fix.imprest.count"]
        .with_user(c.acct)
        .create({"fund_id": fund.id, "counted_amount": 9950.0})
    )
    cnt.with_user(c.acct).action_reconcile()
    v = _voucher(c, fund, 1000.0)
    v.with_user(c.acct).action_submit()
    v.with_user(c.acct2).action_approve()  # the box changed after the count
    with pytest.raises(UserError, match="count the box again"):
        cnt.with_user(c.mgr).action_book_variance()


def test_m50_i07_counter_stamp_cannot_be_rewritten(c):
    fund = _fund(c)
    cnt = (
        c.env["fix.imprest.count"]
        .with_user(c.mgr)
        .create({"fund_id": fund.id, "counted_amount": 9000.0})
    )
    cnt.with_user(c.mgr).action_reconcile()
    with pytest.raises(UserError):
        cnt.with_user(c.mgr).action_book_variance()
    with pytest.raises(REFUSED):
        cnt.with_user(c.mgr).write({"counted_by_id": c.acct.id})
    with pytest.raises(REFUSED):
        c.env["fix.imprest.count"].with_user(c.mgr).create(
            {"fund_id": fund.id, "counted_amount": 1.0, "counted_by_id": c.acct.id}
        )
    cnt.with_user(c.mgr2).action_book_variance()
    assert cnt.state == "booked"


def test_m50_i08_topup_requester_cannot_approve(c):
    fund = _fund(c, fill=False)
    t = (
        c.env["fix.imprest.topup"]
        .with_user(c.mgr)
        .create({"fund_id": fund.id, "amount": 1000.0, "journal_id": c.bank.id})
    )
    with pytest.raises(UserError):
        t.with_user(c.mgr).action_approve()
    t2 = (
        c.env["fix.imprest.topup"]
        .with_user(c.acct)
        .create({"fund_id": fund.id, "amount": 1000.0, "journal_id": c.bank.id})
    )
    with pytest.raises(UserError):
        t2.with_user(c.acct2).action_approve()


def test_m50_i09_topup_requester_stamp_cannot_be_rewritten(c):
    fund = _fund(c, fill=False)
    t = (
        c.env["fix.imprest.topup"]
        .with_user(c.mgr)
        .create({"fund_id": fund.id, "amount": 10000.0, "journal_id": c.bank.id})
    )
    with pytest.raises(REFUSED):
        t.with_user(c.mgr).write({"requested_by_id": c.acct.id})
    with pytest.raises(REFUSED):
        c.env["fix.imprest.topup"].with_user(c.mgr).create(
            {"fund_id": fund.id, "amount": 1.0, "requested_by_id": c.acct.id}
        )
    with pytest.raises(UserError):
        t.with_user(c.mgr).action_approve()


def test_m50_i10_topup_state_cannot_be_forged(c):
    fund = _fund(c, fill=False)
    t = (
        c.env["fix.imprest.topup"]
        .with_user(c.acct)
        .create({"fund_id": fund.id, "amount": 9000.0, "journal_id": c.bank.id})
    )
    with pytest.raises(REFUSED):
        t.with_user(c.acct).write({"state": "approved"})
    with pytest.raises(UserError):
        t.with_user(c.acct).action_pay()
    assert bal(c, c.bank_acc) == 0.0


def test_m50_i11_topup_ceiling_held_after_approval(c):
    fund = _fund(c, ceiling=5000.0, voucher_limit=1000.0, fill=False)
    t = (
        c.env["fix.imprest.topup"]
        .with_user(c.acct)
        .create({"fund_id": fund.id, "amount": 5000.0, "journal_id": c.bank.id})
    )
    t.with_user(c.mgr).action_approve()
    with pytest.raises(REFUSED):
        t.with_user(c.acct).write({"amount": 50000.0})
    t.with_user(c.acct).action_pay()
    assert t.state == "paid" and bal(c, fund.account_id) == 5000.0


def test_m50_i12_topup_above_ceiling_refused_at_request(c):
    fund = _fund(c, ceiling=2500.0, voucher_limit=1000.0, fill=False)
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        c.env["fix.imprest.topup"].with_user(c.acct).create({"fund_id": fund.id, "amount": 7750.0})
    c.env["fix.imprest.topup"].with_user(c.acct).create({"fund_id": fund.id, "amount": 2000.0})
    with pytest.raises(REFUSED):  # two requests cannot add up past the ceiling either
        c.env["fix.imprest.topup"].with_user(c.acct).create({"fund_id": fund.id, "amount": 600.0})


# =================================================================== cheques
def _cheque(c, amount=5000.0, user=None, **kw):
    vals = {
        "operating_unit_id": c.ou.id,
        "direction": "received",
        "cheque_no": "B1CHQ%s" % next(_SEQ),
        "drawee_bank": "Sonali",
        "partner_id": c.vendor.id,
        "amount": amount,
        "cheque_date": c.today,
        "journal_id": c.bank.id,
    }
    vals.update(kw)
    return c.env["fix.cheque"].with_user(user or c.acct).create(vals)


def _book(c, first=500100, last=500199):
    return (
        c.env["fix.cheque.book"]
        .with_user(c.mgr)
        .create(
            {
                "name": "B1 book %s" % c.n,
                "journal_id": c.bank.id,
                "first_number": first,
                "last_number": last,
            }
        )
    )


def test_m50_q01_pdc_cannot_be_presented_early(c):
    chq = _cheque(c, cheque_date=c.today + timedelta(days=20))
    with pytest.raises(UserError, match="post-dated"):
        chq.with_user(c.acct).action_deposit()


def test_m50_q02_cheque_state_cannot_be_forged(c):
    chq = _cheque(c)
    with pytest.raises(REFUSED):
        chq.with_user(c.acct).write({"state": "cleared"})
    assert chq.state == "received"


def test_m50_q03_duplicate_number_without_drawee_refused(c):
    _cheque(c, cheque_no="B1DUP-777", drawee_bank=False)
    with pytest.raises(ValidationError):
        _cheque(c, cheque_no="B1DUP-777", drawee_bank=False)
    with pytest.raises(ValidationError):
        _cheque(c, cheque_no=" b1dup-777 ", drawee_bank="")


def test_m50_q03b_issued_cheques_come_from_the_cheque_book(c):
    with pytest.raises(UserError, match="treasury"):
        _cheque(c, direction="issued")
    p = pay(c, amount=3300.0, method="cheque", rail="cheque", partner_bank_id=False)
    p.with_user(c.acct).action_prepare()
    _authorise(c, p)
    with pytest.raises(UserError, match="cheque book"):
        p.with_user(c.mgr).action_release()
    book = _book(c)
    p.with_user(c.mgr).action_release()
    chq = c.env["fix.cheque"].search([("payment_execution_id", "=", p.id)])
    assert chq.cheque_no == "500100" and chq.cheque_book_id == book and book.next_number == 500101


def test_m50_q04_issued_cheque_bounce_after_clearing_unwinds_payment(c):
    _book(c)
    p = pay(c, amount=3300.0, method="cheque", rail="cheque", partner_bank_id=False)
    p.with_user(c.acct).action_prepare()
    _authorise(c, p)
    p.with_user(c.mgr).action_release()
    chq = c.env["fix.cheque"].search([("payment_execution_id", "=", p.id)])
    stmt(c, [(-3300.0, chq.cheque_no)])
    c.env[LINE].with_user(c.acct2).auto_match()
    assert chq.state == "cleared" and p.state == "executed" and bal(c, c.bank_acc) == -3300.0
    chq.with_user(c.acct).write({"bounce_reason": "Insufficient funds"})
    with pytest.raises(UserError, match="Accounting Administrator"):
        chq.with_user(c.acct).action_bounce()
    chq.with_user(c.mgr2).action_bounce()
    assert p.state == "failed" and p.reversal_move_id and bal(c, c.bank_acc) == 0.0
    assert bal(c, c.acc["outgoing_clearing"]) == 0.0
    failed = c.env["fix.event.outbox"].search(
        [("event_type", "=", "payment.failed"), ("aggregate_id", "=", p.id)]
    )
    assert failed


def test_m50_q05_received_cheque_bounce_reopens_the_receivable(c):
    chq = _cheque(c, amount=2200.0, source_ref="INV/2026/99999")
    chq.with_user(c.acct).action_deposit()
    ln = stmt(c, [(2200.0, chq.cheque_no)])
    ln.with_user(c.acct2).write({"matched_cheque_id": chq.id})
    ln.with_user(c.acct2).action_confirm_manual_match()
    assert chq.state == "cleared"
    chq.with_user(c.mgr).write({"bounce_reason": "Signature differs"})
    chq.with_user(c.mgr).action_bounce()
    assert chq.bounce_move_id.state == "posted"
    assert bal(c, c.acc["cheque_returned"]) == 2200.0 and bal(c, c.bank_acc) == -2200.0
    assert c.env["fix.event.outbox"].search_count(
        [("event_type", "=", "cheque.bounced"), ("aggregate_id", "=", chq.id)]
    )


# =================================================================== cash-in-transit
def _shift(c, opening, counted):
    return c.env["fix.cash.shift"].create(  # arrangement: a counted, closed M04 drawer
        {
            "operating_unit_id": c.ou.id,
            "branch_id": c.branch.id,
            "operator_id": c.rider.id,
            "shift_date": c.today,
            "opening_float": opening,
            "cash_payments": counted - opening,
            "closing_counted": counted,
            "state": "closed",
        }
    )


def _deposit(c, amount, user=None):
    return (
        c.env["fix.cash.deposit"]
        .with_user(user or c.acct)
        .create(
            {
                "branch_id": c.branch.id,
                "journal_id": c.bank.id,
                "amount": amount,
                "slip_no": "B1SLIP-%s" % next(_SEQ),
            }
        )
    )


def test_m50_d01_dispatch_needs_counted_shift(c):
    dep = _deposit(c, 1000.0)
    with pytest.raises(UserError, match="No counted cash shift"):
        dep.with_user(c.acct).action_dispatch()


def test_m50_d02_undispatched_deposit_cannot_be_credited(c):
    dep = _deposit(c, 10000.0)
    with pytest.raises(REFUSED):
        dep.with_user(c.acct).write({"state": "in_transit"})
    ln = stmt(c, [(10000.0, dep.slip_no)])
    ln.with_user(c.acct).write({"matched_deposit_id": dep.id})
    with pytest.raises(UserError):
        ln.with_user(c.acct).action_confirm_manual_match()
    assert bal(c, c.acc["cash_in_transit"]) == 0.0


def test_m50_d03_deposit_shortage_written_off_by_a_manager_with_reason(c):
    _shift(c, 0.0, 10000.0)
    dep = _deposit(c, 10000.0)
    dep.with_user(c.acct).action_dispatch()
    stmt(c, [(6000.0, dep.slip_no)])
    c.env[LINE].with_user(c.acct2).auto_match()
    assert dep.state == "variance" and bal(c, c.acc["cash_in_transit"]) == 4000.0
    with pytest.raises(UserError, match="Accounting Administrator"):
        dep.with_user(c.acct).action_resolve_variance()
    with pytest.raises(UserError, match="Record why"):
        dep.with_user(c.mgr).action_resolve_variance()
    dep.with_user(c.acct).write({"variance_reason": "Bank counted 4,000 short; claim lodged"})
    dep.with_user(c.mgr).action_resolve_variance()
    assert dep.state == "credited" and dep.variance_resolved_by_id == c.mgr
    assert bal(c, c.acc["cash_in_transit"]) == 0.0 and bal(c, c.acc["cash_shortage"]) == 4000.0


def test_m50_d04_over_credit_never_drives_cash_in_transit_negative(c):
    _shift(c, 0.0, 5000.0)
    dep = _deposit(c, 5000.0)
    dep.with_user(c.acct).action_dispatch()
    stmt(c, [(5500.0, dep.slip_no)])
    c.env[LINE].with_user(c.acct2).auto_match()
    assert bal(c, c.acc["cash_in_transit"]) == 0.0 and bal(c, c.acc["cash_shortage"]) == -500.0
    assert dep.state == "variance"


# =================================================================== COD
def _cod_orders(c, amounts, rail="cod"):
    cons = (
        c.env["fix.consignment"]
        .sudo()
        .create(
            {
                "operating_unit_id": c.ou.id,
                "consignment_type": "delivery",
                "scheduled_date": fields.Datetime.now(),
                "rider_id": c.rider.id,
            }
        )
    )
    c.env.cr.execute("update fix_consignment set state='delivered' where id=%s", (cons.id,))
    cons.invalidate_recordset()
    cust = c.env["res.partner"].create({"name": "B1 COD customer"})
    orders = c.env["fix.storefront.order"]
    for a in amounts:
        orders |= (
            c.env["fix.storefront.order"]
            .sudo()
            .create(
                {
                    "customer_id": cust.id,
                    "total_amount": a,
                    "shipping_address": "Dhaka",
                    "payment_rail": rail,
                    "state": "delivered",
                    "carrier_consignment_id": cons.id,
                    "operating_unit_id": c.ou.id,
                }
            )
        )
    return orders


def _cod(c, user=None):
    return (
        c.env["fix.cod.settlement"]
        .with_user(user or c.acct)
        .create(
            {
                "operating_unit_id": c.ou.id,
                "branch_id": c.branch.id,
                "rider_id": c.rider.id,
                "remittance_journal_id": c.bank.id,
                "remittance_method": "bank",
                "remittance_ref": "TRX-%s" % next(_SEQ),
            }
        )
    )


def test_m50_c01_cod_settle_sod_and_manager(c):
    _cod_orders(c, [3000.0, 2000.0])
    s = _cod(c, c.mgr)
    s.with_user(c.mgr).action_load_orders()
    s.with_user(c.mgr).write({"remitted_amount": 5000.0})
    s.with_user(c.mgr).action_submit()
    with pytest.raises(UserError):
        s.with_user(c.mgr).action_settle()
    with pytest.raises(UserError):
        s.with_user(c.acct).action_settle()
    s.with_user(c.mgr2).action_settle()
    assert s.state == "settled" and s.recovery_state == "none"


def test_m50_c02_submitter_stamp_cannot_be_rewritten(c):
    _cod_orders(c, [3000.0])
    s = _cod(c, c.mgr)
    s.with_user(c.mgr).action_load_orders()
    s.with_user(c.mgr).write({"remitted_amount": 3000.0})
    s.with_user(c.mgr).action_submit()
    with pytest.raises(REFUSED):
        s.with_user(c.mgr).write({"submitted_by_id": c.acct.id})
    with pytest.raises(UserError):
        s.with_user(c.mgr).action_settle()


def test_m50_c03_shortage_needs_a_second_approver_and_blocks_the_rider(c):
    _cod_orders(c, [50000.0])
    s = _cod(c, c.acct)
    s.with_user(c.acct).action_load_orders()
    s.with_user(c.acct).write({"remitted_amount": 0.0})
    s.with_user(c.acct).action_submit()
    with pytest.raises(UserError, match="second Accounting Administrator"):
        s.with_user(c.mgr).action_settle()
    s.with_user(c.mgr).action_approve_shortage()
    with pytest.raises(UserError, match="Segregation"):
        s.with_user(c.mgr).action_settle()
    s.with_user(c.mgr2).action_settle()
    assert s.recovery_state == "open" and bal(c, c.acc["rider_shortage"]) == 50000.0
    assert c.env["fix.cod.settlement"]._fix_rider_has_open_variance(c.rider)
    s.with_user(c.mgr).write({"recovery_ref": "HR deduction NOV-26"})
    s.with_user(c.mgr).action_mark_recovered()
    assert not c.env["fix.cod.settlement"]._fix_rider_has_open_variance(c.rider)


def test_m50_c04_orders_cannot_be_written_onto_a_settlement(c):
    _cod_orders(c, [1000.0])
    foreign = _cod_orders(c, [99000.0], rail="bkash")
    s = _cod(c, c.acct)
    s.with_user(c.acct).action_load_orders()
    with pytest.raises(REFUSED):
        s.with_user(c.acct).write({"order_ids": [(4, foreign.id)]})
    assert foreign not in s.order_ids and s.expected_amount == 1000.0


def test_m50_c05_cod_state_cannot_be_forged(c):
    _cod_orders(c, [1500.0])
    s = _cod(c, c.acct)
    s.with_user(c.acct).action_load_orders()
    with pytest.raises(REFUSED):
        s.with_user(c.acct).write({"state": "settled"})
    assert s.state == "draft"


# =================================================================== gateway
def _gw(c, csv_text, user=None):
    return (
        c.env["fix.gateway.settlement"]
        .with_user(user or c.acct)
        .create(
            {
                "provider": "bkash",
                "journal_id": c.bank.id,
                "settlement_date": c.today,
                "report_file": base64.b64encode(csv_text.encode()),
            }
        )
    )


def test_m50_g01_unmatched_batch_cannot_post(c):
    b = _gw(c, "TrxID,Amount,Fee,Net\nB1ZZ%s,1000.00,15.00,985.00\n" % next(_SEQ))
    b.with_user(c.acct).action_import_report()
    assert b.state == "exceptions"
    with pytest.raises(UserError):
        b.with_user(c.acct).action_post()


def test_m50_g02_match_cannot_be_forged(c):
    b = _gw(c, "TrxID,Amount,Fee,Net\nB1ZZ%s,1000.00,15.00,985.00\n" % next(_SEQ))
    b.with_user(c.acct).action_import_report()
    with pytest.raises(REFUSED):
        b.line_ids.with_user(c.acct).write({"match_state": "matched"})
    with pytest.raises(REFUSED):
        b.with_user(c.acct).write({"state": "matched"})
    # even a matched-looking batch (superuser forgery) is re-checked at post
    b.line_ids.sudo().write({"match_state": "matched"})
    b.sudo().write({"state": "matched"})
    with pytest.raises(UserError, match="not three-way matched"):
        b.with_user(c.acct).action_post()
    assert not b.move_id


def _matched_batch(c):
    trx = "B1G%s" % next(_SEQ)
    cust = c.env["res.partner"].create({"name": "B1 GW customer"})
    c.env["fix.storefront.order"].sudo().create(
        {
            "customer_id": cust.id,
            "total_amount": 1000.0,
            "shipping_address": "Dhaka",
            "payment_rail": "bkash",
            "payment_ref": trx,
            "state": "paid",
            "operating_unit_id": c.ou.id,
        }
    )
    stmt(c, [(985.0, "BKASH SETTLEMENT %s" % trx)])
    b = _gw(c, "TrxID,Amount,Fee,Net\n%s,1000.00,15.00,985.00\n" % trx)
    b.with_user(c.acct).action_import_report()
    assert b.state == "matched", (b.state, b.exception_count, b.bank_matched)
    return b


def test_m50_g03_report_lines_frozen_and_post_rechecks_bank_credit(c):
    b = _matched_batch(c)
    with pytest.raises(REFUSED):
        b.line_ids.with_user(c.acct).write({"fee": 300.0, "net": 700.0})
    # a superuser edit of the evidence makes the re-check fail at post
    b.line_ids.sudo().write({"fee": 300.0, "net": 700.0})
    with pytest.raises(UserError, match="not three-way matched"):
        b.with_user(c.acct).action_post()


def test_ref_m50_g03b_matched_batch_posts_net_equal_to_bank_credit(c):
    b = _matched_batch(c)
    b.with_user(c.acct).action_post()
    assert b.state == "posted" and bal(c, c.bank_acc) == 985.0
    assert bal(c, c.acc["gateway_fees"]) == 15.0 and bal(c, c.acc["channel_clearing"]) == -1000.0


def test_m50_g04_same_report_twice_refused(c):
    csv = "TrxID,Amount,Fee,Net\nB1DUP%s,500.00,5.00,495.00\n" % next(_SEQ)
    _gw(c, csv).with_user(c.acct).action_import_report()
    with pytest.raises(UserError, match="already imported"):
        _gw(c, csv).with_user(c.acct).action_import_report()


# =================================================================== facilities
def _facility(c):
    fac = (
        c.env["fix.bank.facility"]
        .with_user(c.mgr)
        .create(
            {
                "name": "B1 TL %s" % next(_SEQ),
                "lender_id": c.vendor.id,
                "facility_type": "term_loan",
                "limit_amount": 1200000.0,
                "principal": 1200000.0,
                "interest_rate": 12.0,
                "tenor_months": 12,
                "start_date": c.today,
                "liability_account_id": c.acc["cod_clearing"].id,
                "journal_id": c.bank.id,
            }
        )
    )
    fac.with_user(c.mgr).action_generate_schedule()
    fac.with_user(c.mgr).action_activate()
    return fac


def test_m50_f01_accountant_cannot_activate_facility(c):
    fac = (
        c.env["fix.bank.facility"]
        .with_user(c.mgr)
        .create(
            {
                "name": "B1 OD",
                "lender_id": c.vendor.id,
                "facility_type": "overdraft",
                "limit_amount": 500000.0,
                "journal_id": c.bank.id,
            }
        )
    )
    with pytest.raises(REFUSED):
        fac.with_user(c.acct).action_activate()


def test_m50_f02_schedule_frozen_and_paid_in_order_at_scheduled_amounts(c):
    fac = _facility(c)
    first, second, third = fac.repayment_ids.sorted("sequence")[:3]
    with pytest.raises(REFUSED):
        first.with_user(c.acct).write({"principal": 600000.0})
    with pytest.raises(REFUSED):
        first.with_user(c.mgr).write({"principal": 600000.0})
    with pytest.raises(REFUSED):
        fac.with_user(c.mgr).write({"interest_rate": 1.0})
    with pytest.raises(UserError, match="amendment"):
        fac.with_user(c.mgr).action_generate_schedule()
    with pytest.raises(UserError, match="Accounting Administrator"):
        first.with_user(c.acct).action_pay()
    with pytest.raises(UserError, match="schedule order"):
        third.with_user(c.mgr).action_pay()
    first.with_user(c.mgr).action_pay()
    assert first.state == "paid" and bal(c, c.bank_acc) == -round(first.total, 2)
    assert second.state == "planned"


def test_ref_m50_f02b_amendment_reschedules_after_second_approval(c):
    fac = _facility(c)
    fac.repayment_ids.sorted("sequence")[:1].with_user(c.mgr).action_pay()
    outstanding = round(
        sum(fac.repayment_ids.filtered(lambda r: r.state == "planned").mapped("principal")), 2
    )
    am = (
        c.env["fix.facility.amendment"]
        .with_user(c.acct)
        .create(
            {
                "facility_id": fac.id,
                "reason": "Lender letter 2026/11",
                "new_interest_rate": 10.0,
                "new_instalments": 6,
            }
        )
    )
    with pytest.raises(REFUSED):
        am.with_user(c.acct).write({"state": "approved"})
    with pytest.raises(UserError):
        am.with_user(c.acct).action_approve()
    am.with_user(c.mgr).action_approve()
    planned = fac.repayment_ids.filtered(lambda r: r.state == "planned")
    assert len(planned) == 6 and fac.interest_rate == 10.0
    assert round(sum(planned.mapped("principal")), 2) == outstanding
    assert min(planned.mapped("sequence")) == 2


def test_m50_f03_covenant_terms_approved_and_test_history_unforgeable(c):
    fac = _facility(c)
    cov = (
        c.env["fix.facility.covenant"]
        .with_user(c.mgr)
        .create(
            {
                "facility_id": fac.id,
                "name": "Min liquidity",
                "metric": "min_liquidity",
                "operator": "ge",
                "threshold": 999999999.0,
            }
        )
    )
    with pytest.raises(UserError, match="not approved"):
        cov.with_user(c.mgr).action_test()
    with pytest.raises(UserError):
        cov.with_user(c.mgr).action_approve()
    cov.with_user(c.mgr2).action_approve()
    cov.with_user(c.acct).action_test()
    assert cov.last_result == "breach"
    with pytest.raises(REFUSED):
        cov.with_user(c.acct).write({"threshold": -1.0})
    with pytest.raises(REFUSED):
        cov.with_user(c.mgr).write({"threshold": -1.0})
    for user in (c.acct, c.mgr):
        with pytest.raises(REFUSED):
            c.env["fix.covenant.test"].with_user(user).create(
                {
                    "covenant_id": cov.id,
                    "tested_on": c.today,
                    "value": 1.0,
                    "threshold": 0.5,
                    "result": "pass",
                }
            )
    with pytest.raises(REFUSED):
        cov.test_ids.write({"result": "pass"})
    assert cov.test_ids.result == "breach" and cov.last_result == "breach"


# =================================================================== position / wiring
def test_m50_x01_forged_execution_cannot_inflate_position(c):
    _user(c.env, "b1m50_t4_%s" % c.n, [ADMIN, "cd_entity_config.group_dofa_tier_4"])
    p = pay(c, amount=1000000.0)
    s1 = c.env["fix.cash.position"].with_user(c.acct).create({"company_id": c.company.id})
    with pytest.raises(REFUSED):
        p.with_user(c.acct).write({"state": "executed"})
    s2 = c.env["fix.cash.position"].with_user(c.acct).create({"company_id": c.company.id})
    assert abs(s2.total_position - s1.total_position) < 0.01
    # a prepared instruction still counts as committed cash
    p.with_user(c.acct).action_prepare()
    s3 = c.env["fix.cash.position"].with_user(c.acct).create({"company_id": c.company.id})
    assert abs(s3.pending_payments - s1.pending_payments) < 0.01


def test_m50_x02_p03_surfaces_declare_writable_and_no_workflow_field(c):
    from odoo.addons.cd_p03_portal.controllers.a08 import m50

    missing = [m for m, conf in m50.SURFACES.items() if "writable" not in conf]
    assert not missing
    for model, _conf in m50.SURFACES.items():
        if model not in c.env or not hasattr(c.env[model], "_fix_guarded_fields"):
            continue
        guarded = c.env[model]._fix_guarded_fields()
        # whatever the generated whitelist says, the endpoint drops guarded fields
        from odoo.addons.cd_p03_portal.controllers.p03_generic_api import _locked_fields

        assert guarded <= _locked_fields(c.env[model]), model
    assert {"action_prepare", "action_release"} <= m50.SURFACES[PEX]["actions"]
    assert "action_execute" not in m50.SURFACES[PEX]["actions"]


def test_m50_x03_guards_cover_every_treasury_model(c):
    for model in (
        PEX,
        LINE,
        "fix.bank.statement.import",
        "fix.cash.deposit",
        "fix.cod.settlement",
        "fix.imprest.voucher",
        "fix.imprest.topup",
        "fix.imprest.count",
        "fix.cheque",
        "fix.cheque.book",
        "fix.gateway.settlement",
        "fix.gateway.settlement.line",
        "fix.bank.facility",
        "fix.facility.repayment",
        "fix.facility.covenant",
        "fix.facility.amendment",
    ):
        guarded = c.env[model]._fix_guarded_fields()
        assert "state" in guarded or "match_state" in guarded, model


def test_m50_18_consumer_and_crons_are_registered_and_run(c):
    consumer = c.env.ref("cd_cash_position.consumer_payment_requested_treasury")
    assert (consumer.event_type, consumer.model, consumer.method, consumer.active) == (
        "payment.requested",
        PEX,
        "consume_payment_requested",
        True,
    )
    match_cron = c.env.ref("cd_cash_position.ir_cron_statement_auto_match")
    cov_cron = c.env.ref("cd_cash_position.ir_cron_covenant_tests")
    assert match_cron.active and match_cron.code == "model._cron_auto_match()"
    assert cov_cron.active and cov_cron.code == "model._cron_test_covenants()"
    # the crons' methods do their job
    p = released(c, amount=1234.0)
    stmt(c, [(-1234.0, p.name)])
    c.env[LINE]._cron_auto_match()
    assert p.state == "executed"
    fac = _facility(c)
    cov = (
        c.env["fix.facility.covenant"]
        .with_user(c.mgr)
        .create(
            {
                "facility_id": fac.id,
                "name": "Util",
                "metric": "utilisation_pct",
                "operator": "le",
                "threshold": 100.0,
            }
        )
    )
    cov.with_user(c.mgr2).action_approve()
    assert c.env["fix.facility.covenant"]._cron_test_covenants() >= 1
    assert cov.test_ids and cov.last_tested == c.today
    # the relay delivers a real payment.requested to the consumer
    claim = _claim(c, 410.0)
    from libs.py.fix_events import publish

    publish(
        c.env,
        "payment.requested",
        "fix.expense.claim",
        claim.id,
        {"amount": 410.0, "operating_unit_id": c.ou.id},
    )
    event = c.env["fix.event.outbox"].search(
        [("event_type", "=", "payment.requested"), ("aggregate_id", "=", claim.id)],
        order="id desc",
        limit=1,
    )
    assert c.env["fix.event.outbox"]._relay_deliver(consumer, event) == ""
    got = c.env[PEX].search(
        [("source_model", "=", "fix.expense.claim"), ("source_id", "=", claim.id)]
    )
    assert got and got.amount == 410.0 and got.state == "pending"


def test_m50_r11_period_close_gate_lists_unexplained_lines(c):
    """BRU-TRE-19: M19 asks treasury which bank lines block a period close."""
    ln = stmt(c, [(-77.0, "UNEXPLAINED")])
    Line = c.env[LINE]
    assert ln in Line._fix_reconciliation_blockers(c.company, c.today)
    assert ln not in Line._fix_reconciliation_blockers(c.company, c.today - timedelta(days=1))
    ln.with_user(c.mgr).action_post_bank_charge()
    assert ln not in Line._fix_reconciliation_blockers(c.company, c.today)


def test_m50_18b_unmatched_deposit_incident_cron(c):
    """BRU-TRE-07 / AUT-TRE-09: a deposit uncredited beyond the threshold
    (default 3 days) is raised once as an incident to the administrators."""
    cron = c.env.ref("cd_cash_position.ir_cron_unmatched_deposit_incidents")
    assert cron.active and cron.code == "model._cron_unmatched_deposit_incidents()"
    _shift(c, 0.0, 9000.0)
    old, fresh = _deposit(c, 4000.0), _deposit(c, 5000.0)
    (old | fresh).with_user(c.acct).action_dispatch()
    c.env.cr.execute(
        "UPDATE fix_cash_deposit SET dispatched_at = now() - interval '4 days' WHERE id = %s",
        (old.id,),
    )  # arrangement: dispatched four days ago
    old.invalidate_recordset()
    Deposit = c.env["fix.cash.deposit"]
    assert Deposit._cron_unmatched_deposit_incidents() >= 1
    assert old.incident_raised_at and not fresh.incident_raised_at
    assert c.mgr in old.activity_ids.mapped("user_id")
    with pytest.raises(REFUSED):
        old.with_user(c.acct).write({"incident_raised_at": False})
    before = len(old.activity_ids)
    Deposit._cron_unmatched_deposit_incidents()
    assert len(old.activity_ids) == before  # raised once


def test_m50_18c_lc_expiry_alert_cron_until_acknowledged(c):
    """BRU-TRE-24 / AUT-TRE-21: an active LC inside the expiry window (default
    30 days) alerts daily until an Accounting Administrator acknowledges it."""
    cron = c.env.ref("cd_cash_position.ir_cron_lc_expiry_alerts")
    assert cron.active and cron.code == "model._cron_expiry_alerts()"
    lc = (
        c.env["fix.bank.facility"]
        .with_user(c.mgr)
        .create(
            {
                "name": "B1 LC %s" % c.n,
                "lender_id": c.vendor.id,
                "facility_type": "lc",
                "limit_amount": 750000.0,
                "expiry_date": c.today + timedelta(days=10),
                "liability_account_id": c.acc["cod_clearing"].id,
            }
        )
    )
    later = (
        c.env["fix.bank.facility"]
        .with_user(c.mgr)
        .create(
            {
                "name": "B1 LC far %s" % c.n,
                "lender_id": c.vendor.id,
                "facility_type": "lc",
                "limit_amount": 1000.0,
                "expiry_date": c.today + timedelta(days=90),
                "liability_account_id": c.acc["cod_clearing"].id,
            }
        )
    )
    (lc | later).with_user(c.mgr).action_activate()
    Facility = c.env["fix.bank.facility"]
    assert Facility._cron_expiry_alerts() >= 1
    assert lc.activity_ids and not later.activity_ids
    assert c.mgr in lc.activity_ids.mapped("user_id")
    with pytest.raises(UserError):
        lc.with_user(c.acct).action_acknowledge_expiry()
    lc.with_user(c.mgr).action_acknowledge_expiry()
    assert lc.expiry_ack_by_id == c.mgr and not lc.activity_ids
    Facility._cron_expiry_alerts()
    assert not lc.activity_ids
