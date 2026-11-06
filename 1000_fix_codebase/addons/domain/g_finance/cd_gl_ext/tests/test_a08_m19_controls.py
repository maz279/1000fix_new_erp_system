# A08 remediation, M19 General Ledger & period close (cd_gl_ext): control tests.
#
# One test per gap probe of working/A08_evidence/probes/m19/probe_m19.py (same id,
# same attack, run as NON-ADMIN users with the real finance roles created in the
# rolled-back transaction), plus proper-path tests that the legitimate maker and
# checker can do the job. The inter-company (I*), consolidation (C*) and nil-return
# (N*) probes attack cd_multi_entity models and live in that addon's tests.
import types
from datetime import date, timedelta

import pytest
from odoo import Command, fields
from odoo.exceptions import AccessError, UserError, ValidationError

pytestmark = [pytest.mark.financial]

REFUSED = (UserError, ValidationError, AccessError)
ACC_USER = "account.group_account_user"
ACC_MGR = "account.group_account_manager"
BILL = "account.group_account_invoice"
STOCK_MGR = "stock.group_stock_manager"
TIER2 = "cd_entity_config.group_dofa_tier_2"
TIER4 = "cd_entity_config.group_dofa_tier_4"
PE = date(2026, 9, 30)  # the period being closed
IN_PERIOD = date(2026, 9, 15)


class Ctx:
    pass


_SEQ = iter(range(1, 100000))


def _user(env, login, groups=(), companies=None):
    Users = env["res.users"].with_context(no_reset_password=True)
    gids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    ou = env["operating.unit"].search([], limit=1)
    companies = companies or env.company
    return Users.create(
        {
            "name": login,
            "login": login,
            "group_ids": [(6, 0, gids)],
            "company_ids": [(6, 0, companies.ids)],
            "company_id": companies[0].id,
            "assigned_operating_unit_ids": [(6, 0, ou.ids)],
            "default_operating_unit_id": ou.id,
        }
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = Ctx()
    x.env = env
    x.co = env.company
    x.bdt = env.ref("base.BDT")
    x.usd = env.ref("base.USD")
    if x.co.currency_id != x.bdt:
        x.co.sudo().write({"currency_id": x.bdt.id})
    x.acct = _user(env, "a08b3_acct", [ACC_USER])
    x.acct2 = _user(env, "a08b3_acct2", [ACC_USER])
    # Accounting Administrators who also prepare (Odoo 19 manager does not
    # imply accountant) and hold the DOFA tier of a manual journal.
    x.mgr = _user(env, "a08b3_mgr", [ACC_USER, ACC_MGR, TIER2])
    x.mgr2 = _user(env, "a08b3_mgr2", [ACC_USER, ACC_MGR, TIER2])
    x.cfo = _user(env, "a08b3_cfo", [ACC_USER, ACC_MGR, TIER4])
    x.bill = _user(env, "a08b3_bill", [BILL])
    x.plain = _user(env, "a08b3_plain")
    x.stk = _user(env, "a08b3_stock", [STOCK_MGR])
    A = env["account.account"]

    def acc(code):
        a = A.search([("code", "=", code)], limit=1)
        assert a, "fixture: no account %s" % code
        return a

    x.recv = acc("121000")
    x.pay = acc("211000")
    x.inc = acc("400000")
    x.oinc = acc("450000")
    x.exp = acc("600000")
    x.cash = acc("101401")
    x.fx_gain = x.co.income_currency_exchange_account_id or acc("441000")
    x.fx_loss = x.co.expense_currency_exchange_account_id or acc("641000")
    x.targets = [acc("610000"), acc("611000"), acc("443000")]
    x.misc = env["account.journal"].search(
        [("code", "=", "MISC"), ("company_id", "=", x.co.id)], limit=1
    )
    x.partner = env["res.partner"].create({"name": "A08 B3 USD Customer"})
    x.today = fields.Date.context_today(env["account.move"])
    return x


def _vals(c, d, amount=1000.0, debit=None, credit=None, ref="A08 B3 test", **line_kw):
    return {
        "move_type": "entry",
        "journal_id": c.misc.id,
        "date": d,
        "ref": ref,
        "line_ids": [
            Command.create(
                {
                    "account_id": (debit or c.exp).id,
                    "debit": amount,
                    "credit": 0.0,
                    "name": "p",
                    **line_kw,
                }
            ),
            Command.create(
                {"account_id": (credit or c.cash).id, "debit": 0.0, "credit": amount, "name": "p"}
            ),
        ],
    }


def je(c, user, d, amount=1000.0, post=True, **kw):
    m = c.env["account.move"].with_user(user).create(_vals(c, d, amount, **kw))
    if post:
        m.action_post()
    return m


def try_post(c, user, d, amount=1000.0, **kw):
    """Attempt a posting; return the move if it posted, None if refused."""
    try:
        with c.env.cr.savepoint():
            m = je(c, user, d, amount, **kw)
            return m if m.state == "posted" else None
    except REFUSED:
        return None


def sys_post(c, d, amount=1000.0, **kw):
    """Fixture data posted by trusted (superuser) code."""
    m = c.env["account.move"].create(_vals(c, d, amount, **kw))
    m.action_post()
    return m


def task_for(c, record, user):
    return c.env["fix.workflow.task"].search(
        [
            ("res_model", "=", record._name),
            ("res_id", "=", record.id),
            ("state", "=", "pending"),
            ("assigned_user_id", "=", user.id),
        ],
        limit=1,
    )


def approve_as(c, record, user):
    task = task_for(c, record, user)
    assert task, "no pending task of %s for %s" % (record.display_name, user.login)
    task.with_user(user).action_approve()


def proper_close(c, closer=None):
    """10 steps by their owners on real evidence -> ready -> close (manager)."""
    evidence = "account.move,%d" % sys_post(c, date(2026, 9, 1), 10.0).id
    close = c.env["fix.period.close"].with_user(c.acct).create({"period_end": PE})
    close.with_user(c.acct).action_generate_standard_steps()
    for ln in close.line_ids:
        owner = c.mgr if ln.sequence == 100 else (c.stk if ln.sequence == 10 else c.acct)
        ln.with_user(owner).action_mark_done(evidence)
    close.with_user(c.acct).action_ready()
    close.with_user(closer or c.mgr).action_close()
    return close


def draft_je(c, user, amount=1000.0, d=None, **kw):
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import create_journal_entry_draft

    env = c.env(user=user.id)
    return create_journal_entry_draft(env, _vals(c, d or c.today, amount, **kw), {}, source="manual")


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_gl_api as gl
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    def orig(cls, name):
        f = getattr(cls, name)
        return getattr(f, "original_endpoint", f)

    gctl = g.P03GenericApiController()
    glctl = gl.P03GlApiController()
    old = (getattr(g, "request", None), getattr(s, "request", None), getattr(gl, "request", None))

    def as_user(user):
        req = types.SimpleNamespace(env=c.env(user=user.id))
        g.request = req
        s.request = req
        gl.request = req

    try:
        yield types.SimpleNamespace(
            as_user=as_user,
            write=lambda **kw: orig(g.P03GenericApiController, "model_write")(gctl, **kw),
            lock=lambda **kw: orig(gl.P03GlApiController, "gl_periods_lock")(glctl, **kw),
            periods=lambda **kw: orig(gl.P03GlApiController, "gl_periods")(glctl, **kw),
            je_create=lambda **kw: orig(gl.P03GlApiController, "gl_je_create")(glctl, **kw),
            je_approve=lambda **kw: orig(gl.P03GlApiController, "gl_je_approve")(glctl, **kw),
            tmpl_create=lambda **kw: orig(gl.P03GlApiController, "gl_templates_create")(glctl, **kw),
        )
    finally:
        g.request, s.request, gl.request = old


# ====================================================================== period close & lock
def test_m19_P01_close_sets_lock_and_posting_stays_out(c):
    """Proper path: steps by their owners on real evidence -> ready -> manager closes;
    the company lock date is the period end; a sub-ledger posting dated in the period
    lands after it, a manual one is refused."""
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

    close = proper_close(c)
    assert close.state == "closed" and close.closed_by_id == c.mgr
    assert c.co.fiscalyear_lock_date == PE and close.is_locked
    move, _d = post_with_dimensions(c.env(user=c.acct.id), _vals(c, IN_PERIOD, 500.0), {}, source="api")
    assert move.state == "posted" and move.date > PE
    with pytest.raises(UserError, match="Period closed"):
        draft_je(c, c.acct, 700.0, d=IN_PERIOD)


def test_m19_P02_closed_period_refuses_manual_posting(c):
    """Attack: after the close, the accountant posts BDT 250,000 dated in the closed
    period. Held: closing locks; manual entries are refused (and need the API anyway)."""
    proper_close(c)
    m = try_post(c, c.acct, IN_PERIOD, 250000.0)
    assert m is None
    assert c.co.fiscalyear_lock_date == PE


def test_m19_P03_close_by_write_refused(c):
    """Attack: write state=closed on a close with 10 pending steps, then lock."""
    close = c.env["fix.period.close"].with_user(c.acct).create({"period_end": PE})
    close.with_user(c.acct).action_generate_standard_steps()
    with pytest.raises(UserError, match="changes only through its workflow"):
        close.with_user(c.acct).write({"state": "closed", "closed_at": fields.Datetime.now()})
    br = c.env["fix.fiscal.period.bridge"].with_user(c.mgr).create(
        {"period_close_id": close.id, "company_id": c.co.id}
    )
    with pytest.raises(UserError, match="before period close is completed"):
        br.with_user(c.mgr).action_lock_journals()
    assert close.state == "in_progress" and not c.co.fiscalyear_lock_date


def test_m19_P04_close_born_closed_refused(c):
    with pytest.raises(UserError, match="changes only through its workflow"):
        c.env["fix.period.close"].with_user(c.acct).create({"period_end": PE, "state": "closed"})


def test_m19_P05_steps_need_owner_and_real_evidence(c):
    """Attack: one accountant clears every owner's step, the CFO's included, with 'x'."""
    close = c.env["fix.period.close"].with_user(c.acct).create({"period_end": PE})
    close.with_user(c.acct).action_generate_standard_steps()
    step20 = close.line_ids.filtered(lambda s: s.sequence == 20)
    with pytest.raises(UserError, match="names no record"):
        step20.with_user(c.acct).action_mark_done("x")
    evidence = "account.move,%d" % sys_post(c, date(2026, 9, 2), 5.0).id
    cfo_step = close.line_ids.filtered(lambda s: s.sequence == 100)
    with pytest.raises(AccessError, match="owned by"):
        cfo_step.with_user(c.acct).action_mark_done(evidence)
    with pytest.raises(AccessError, match="owned by"):
        close.line_ids.filtered(lambda s: s.sequence == 10).with_user(c.acct).action_mark_done(evidence)
    with pytest.raises(UserError, match="changes only through its workflow"):
        step20.with_user(c.acct).write({"state": "done", "evidence_ref": "x"})
    with pytest.raises(UserError, match="changes only through its workflow"):
        cfo_step.with_user(c.acct).write({"blocking": False})
    # the owner on real evidence (a posted entry number is accepted too)
    move = sys_post(c, date(2026, 9, 3), 6.0)
    step20.with_user(c.acct).action_mark_done(move.name)
    assert step20.state == "done" and step20.done_by_id == c.acct
    assert (step20.evidence_model, step20.evidence_res_id) == ("account.move", move.id)
    with pytest.raises(UserError, match="Close steps still open"):
        close.with_user(c.acct).action_ready()


def test_m19_P06_reopen_by_write_refused(c):
    close = proper_close(c)
    with pytest.raises(UserError, match="changes only through its workflow"):
        close.with_user(c.acct2).write({"state": "open"})
    with pytest.raises(UserError, match="frozen"):
        close.with_user(c.mgr2).write({"period_end": date(2026, 8, 31)})
    assert close.state == "closed"


def test_m19_P07_accountant_cannot_move_company_lock_back(c):
    proper_close(c)
    with pytest.raises(REFUSED):
        with c.env.cr.savepoint():
            c.co.with_user(c.acct).write({"fiscalyear_lock_date": date(2026, 8, 31)})
    with pytest.raises(UserError, match="moves back only through an approved period reopen"):
        c.co.with_user(c.mgr).write({"fiscalyear_lock_date": date(2026, 8, 31)})


def test_m19_P08_lock_exception_only_through_approved_reopen(c):
    """Attack: one manager creates an 'everyone, forever' lock exception; a Billing user
    then posts into the period. Held: direct exceptions are refused; a reopen is a routed
    approval by another Accounting Administrator, for one user, with an end date."""
    close = proper_close(c)
    with pytest.raises(UserError, match="approved period reopen"):
        c.env["account.lock_exception"].with_user(c.mgr).create(
            {"company_id": c.co.id, "user_id": False, "fiscalyear_lock_date": False, "reason": "x"}
        )
    assert try_post(c, c.bill, IN_PERIOD, 40000.0) is None
    end = fields.Datetime.now() + timedelta(days=1)
    with pytest.raises(ValidationError, match="at most"):
        with c.env.cr.savepoint():
            c.env["fix.period.reopen"].with_user(c.acct).create(
                {"close_id": close.id, "user_id": c.acct.id, "reason": "late accrual",
                 "end_datetime": fields.Datetime.now() + timedelta(days=30)}
            )
    reopen = close.with_user(c.acct).action_request_reopen(
        user_id=c.acct.id, reason="Late utility accrual", end_datetime=end
    )
    assert reopen.state == "pending"
    # the closer, the requester and the beneficiary never decide it
    assert not task_for(c, reopen, c.mgr) and not task_for(c, reopen, c.acct)
    with pytest.raises(UserError, match="approver's inbox"):
        reopen.with_user(c.mgr2).action_approve()
    approve_as(c, reopen, c.mgr2)
    assert reopen.state == "approved" and reopen.approved_by_id == c.mgr2
    exc = reopen.lock_exception_id
    assert exc.user_id == c.acct and exc.end_datetime
    # the named accountant drafts in the period; the Billing user still cannot
    move, _log = draft_je(c, c.acct, 900.0, d=IN_PERIOD)
    assert move.date == IN_PERIOD
    assert try_post(c, c.bill, IN_PERIOD, 40000.0) is None


def test_m19_P09_forged_future_close_impossible(c):
    """Attack: forge a 2099 close and lock. Held: state is guarded; a close needs the
    period to have ended; the company lock never moves past today."""
    close = c.env["fix.period.close"].with_user(c.acct).create({"period_end": date(2099, 12, 31)})
    with pytest.raises(UserError, match="changes only through its workflow"):
        close.with_user(c.acct).write({"state": "closed"})
    evidence = "account.move,%d" % sys_post(c, date(2026, 9, 1), 10.0).id
    close.with_user(c.acct).action_generate_standard_steps()
    for ln in close.line_ids:
        owner = c.mgr if ln.sequence == 100 else (c.stk if ln.sequence == 10 else c.acct)
        ln.with_user(owner).action_mark_done(evidence)
    close.with_user(c.acct).action_ready()
    with pytest.raises(UserError, match="has not ended"):
        close.with_user(c.mgr).action_close()
    with pytest.raises(UserError, match="locked after it ends"):
        c.co.with_user(c.mgr).write({"fiscalyear_lock_date": date(2099, 12, 31)})
    assert c.co.fiscalyear_lock_date != date(2099, 12, 31)


def test_m19_P10_plain_user_cannot_lock_via_p03(c, p03):
    close = proper_close(c)
    p03.as_user(c.plain)
    res = p03.lock(close_id=close.id)
    assert not res.get("success")
    p03.as_user(c.acct)
    res = p03.lock(close_id=close.id)
    assert not res.get("success") and "Accounting Administrator" in res.get("error", "")
    p03.as_user(c.mgr)
    res = p03.lock(close_id=close.id)
    assert res.get("success"), res


def test_m19_P11_p03_write_cannot_close(c, p03):
    close = c.env["fix.period.close"].with_user(c.acct).create({"period_end": PE})
    close.with_user(c.acct).action_generate_standard_steps()
    p03.as_user(c.acct)
    p03.write(model="fix.period.close", record_id=close.id, values={"state": "closed"})
    c.env.invalidate_all()
    assert close.state != "closed"


def test_m19_P12_is_locked_is_read_from_the_company(c, p03):
    close = c.env["fix.period.close"].with_user(c.acct).create({"period_end": date(2026, 8, 31)})
    br = c.env["fix.fiscal.period.bridge"].with_user(c.acct).create(
        {"period_close_id": close.id, "company_id": c.co.id}
    )
    try:  # a computed field: the tick is refused or changes nothing
        with c.env.cr.savepoint():
            br.with_user(c.acct).write({"is_locked": True})
    except Exception:  # noqa: BLE001
        pass
    c.env.invalidate_all()
    assert not br.is_locked and not close.is_locked
    close2 = proper_close(c)
    br2 = c.env["fix.fiscal.period.bridge"].with_user(c.acct).create(
        {"period_close_id": close2.id, "company_id": c.co.id}
    )
    assert br2.is_locked
    p03.as_user(c.acct)
    rows = {r["id"]: r for r in p03.periods()["rows"]}
    assert rows[close2.id]["locked"] is True


# ====================================================================== journal entries / SoD
def test_m19_J01_maker_checker_proper_path(c):
    """Proper path: the accountant drafts; he cannot approve; it is routed to the Tier-2
    Accounting Administrators; one of them approves and the entry posts with a log row."""
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import approve_journal_entry

    move, log = draft_je(c, c.acct, 1000.0)
    approval = move.fix_journal_approval_id
    assert approval.state == "pending" and approval.dofa_tier_required == "tier_2"
    with pytest.raises(UserError):
        with c.env.cr.savepoint():
            approve_journal_entry(c.env(user=c.acct.id), move.with_user(c.acct))
    approve_journal_entry(c.env(user=c.mgr.id), move.with_user(c.mgr))
    assert move.state == "posted" and log.state == "posted" and log.posted_by == c.mgr
    assert approval.state == "posted" and approval.dofa_approved_by == c.mgr


def test_m19_J02_billing_user_cannot_post_manual_je(c):
    m = try_post(c, c.bill, c.today, 75000.0)
    assert m is None
    with pytest.raises(REFUSED):
        draft_je(c, c.bill, 75000.0)


def test_m19_J03_large_je_needs_higher_tier(c):
    """Attack: an accountant posts BDT 50,000,000 alone. Held: refused; drafted, it is
    routed to the Tier-5 band, which no Tier-2 or Tier-4 administrator holds."""
    assert try_post(c, c.acct, c.today, 50000000.0) is None
    move, _log = draft_je(c, c.acct, 900000.0)
    approval = move.fix_journal_approval_id
    assert approval.dofa_tier_required == "tier_4"
    assert not task_for(c, approval, c.mgr) and task_for(c, approval, c.cfo)
    approve_as(c, approval, c.cfo)
    assert move.state == "posted"
    with pytest.raises(UserError, match="No one can approve"):
        draft_je(c, c.acct, 50000000.0)


def test_m19_J04_manager_cannot_approve_entry_without_approval(c):
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import approve_journal_entry

    move = c.env["account.move"].with_user(c.mgr).create(_vals(c, c.today, 30000.0))
    with pytest.raises(UserError, match="not drafted through the M19 maker-checker"):
        approve_journal_entry(c.env(user=c.mgr.id), move.with_user(c.mgr))
    # and his own drafted entry is never routed to him
    move2, _log = draft_je(c, c.mgr, 30000.0)
    assert not task_for(c, move2.fix_journal_approval_id, c.mgr)
    with pytest.raises(UserError, match="not awaiting your approval"):
        approve_journal_entry(c.env(user=c.mgr.id), move2.with_user(c.mgr))
    assert move.state == "draft" and move2.state == "draft"


def test_m19_J05_approved_entry_cannot_be_redrafted_and_reposted(c):
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import approve_journal_entry

    move, log = draft_je(c, c.acct, 1000.0)
    approve_journal_entry(c.env(user=c.mgr.id), move.with_user(c.mgr))
    with pytest.raises(UserError, match="never modified"):
        move.with_user(c.acct).button_draft()
    with pytest.raises(UserError, match="never modified"):
        move.with_user(c.mgr).button_draft()
    # a superuser reset voids the approval: the maker cannot re-post the entry
    move.sudo().button_draft()
    assert move.fix_journal_approval_id.state == "voided"
    dr, cr_ = move.line_ids.sorted(lambda line: -line.debit)
    move.with_user(c.acct).write(
        {"line_ids": [Command.update(dr.id, {"debit": 1000000.0}), Command.update(cr_.id, {"credit": 1000000.0})]}
    )
    with pytest.raises(UserError, match="maker-checker"):
        move.with_user(c.acct).action_post()
    assert move.state == "draft" and log.amount == 1000.0


def test_m19_J05b_entry_edited_while_pending_is_refused(c):
    move, _log = draft_je(c, c.acct, 1000.0)
    dr, cr_ = move.line_ids.sorted(lambda line: -line.debit)
    move.with_user(c.acct).write(
        {"line_ids": [Command.update(dr.id, {"debit": 9000.0}), Command.update(cr_.id, {"credit": 9000.0})]}
    )
    with pytest.raises(UserError, match="changed after it was routed"):
        approve_as(c, move.fix_journal_approval_id, c.mgr)
    assert move.state == "draft"


def test_m19_J06_unbalanced_entry_refused(c):
    with pytest.raises(REFUSED):
        with c.env.cr.savepoint():
            m = c.env["account.move"].create(
                {
                    "move_type": "entry",
                    "journal_id": c.misc.id,
                    "date": c.today,
                    "line_ids": [
                        Command.create({"account_id": c.exp.id, "debit": 1000.0, "credit": 0.0}),
                        Command.create({"account_id": c.cash.id, "debit": 0.0, "credit": 900.0}),
                    ],
                }
            )
            m.action_post()


def _control_chart(c):
    return c.env["fix.chart.account"].create(
        {
            "company_id": c.co.id,
            "account_code": "1-12-01-%03d" % next(_SEQ),
            "name": "Trade Receivables (control)",
            "account_type": "asset",
            "account_subtype": "receivable",
            "is_postable": True,
            "is_control_account": True,
            "control_subledger": "receivable",
            "statutory_group": "Trade and other receivables",
            "odoo_account_id": c.recv.id,
        }
    )


def test_m19_J07_control_account_refuses_manual_lines_on_every_path(c):
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

    _control_chart(c)
    with pytest.raises(UserError, match="COA-02"):
        draft_je(c, c.acct, 12000.0, debit=c.recv, partner_id=c.partner.id)
    assert try_post(c, c.acct, c.today, 12000.0, debit=c.recv, partner_id=c.partner.id) is None
    with pytest.raises(UserError, match="COA-02"):
        post_with_dimensions(
            c.env(user=c.acct.id), _vals(c, c.today, 12000.0, debit=c.recv, partner_id=c.partner.id),
            {}, source="allocation",
        )
    # the owning sub-ledger may post on it
    move, _d = post_with_dimensions(
        c.env(user=c.acct.id), _vals(c, c.today, 12000.0, debit=c.recv, partner_id=c.partner.id),
        {}, source="ar",
    )
    assert move.state == "posted"


def test_m19_J08_control_flag_change_is_an_approved_proposal(c):
    ch = _control_chart(c)
    with pytest.raises(UserError, match="approved control change"):
        ch.with_user(c.acct).write({"is_control_account": False, "control_subledger": False})
    with pytest.raises(UserError, match="approved control change"):
        ch.with_user(c.mgr).write({"is_control_account": False, "control_subledger": False})
    prop = c.env["fix.chart.control.change"].with_user(c.mgr).create(
        {"account_id": ch.id, "new_is_control": False, "reason": "Re-mapped to a sub-ledger clearing account"}
    )
    prop.with_user(c.mgr).action_submit()
    assert not task_for(c, prop, c.mgr)
    with pytest.raises(UserError, match="approver's inbox"):
        prop.with_user(c.mgr2).action_apply()
    approve_as(c, prop, c.mgr2)
    assert prop.state == "applied" and not ch.is_control_account


def test_m19_J09_posting_log_immutable(c):
    _move, log = draft_je(c, c.acct, 1000.0)
    with pytest.raises(REFUSED):
        with c.env.cr.savepoint():
            log.with_user(c.acct).with_context(force_edit=True).write({"amount": 1.0})


def test_m19_J10_p03_je_create_plain_user_refused_and_proper_path(c, p03):
    p03.as_user(c.plain)
    res = p03.je_create(
        lines=[{"account_id": c.exp.id, "debit": 10, "credit": 0}, {"account_id": c.cash.id, "debit": 0, "credit": 10}],
        ref="plain",
    )
    assert not res.get("success")
    p03.as_user(c.acct)
    res = p03.je_create(
        lines=[{"account_id": c.exp.id, "debit": 10, "credit": 0}, {"account_id": c.cash.id, "debit": 0, "credit": 10}],
        ref="Petty accrual",
    )
    assert res.get("success"), res
    p03.as_user(c.acct)
    assert not p03.je_approve(move_id=res["move_id"]).get("success")
    p03.as_user(c.mgr)
    ok = p03.je_approve(move_id=res["move_id"])
    assert ok.get("success"), ok
    assert c.env["account.move"].browse(res["move_id"]).state == "posted"


# ====================================================================== recurring templates
def _tmpl(c, user, amount=10000.0, **kw):
    vals = {
        "name": "A08 accrual %s %d" % (user.login, next(_SEQ)),
        "journal_id": c.misc.id,
        "next_run_date": c.today - timedelta(days=1),
        "line_ids": [
            Command.create({"account_id": c.exp.id, "debit": amount, "credit": 0.0}),
            Command.create({"account_id": c.cash.id, "debit": 0.0, "credit": amount}),
        ],
    }
    vals.update(kw)
    return c.env["fix.journal.template"].with_user(user).create(vals)


def test_m19_T01_template_activation_sod_and_run(c):
    t = _tmpl(c, c.acct)
    with pytest.raises(UserError):
        with c.env.cr.savepoint():
            t.with_user(c.acct).action_activate()
    t2 = _tmpl(c, c.mgr)
    with pytest.raises(UserError, match="Segregation of duties"):
        t2.with_user(c.mgr).action_activate()
    t.with_user(c.mgr).action_activate()
    assert t.state == "active" and t.activated_by_id == c.mgr
    t.with_user(c.acct).action_generate_entry()
    assert t.last_move_id.state == "posted" and t.run_count == 1


def test_m19_T02_template_born_active_refused(c):
    with pytest.raises(UserError, match="changes only through its workflow"):
        _tmpl(c, c.acct, 400000.0, state="active")
    t = _tmpl(c, c.acct, 400000.0)
    with pytest.raises(UserError, match="not active"):
        t.with_user(c.acct).action_generate_entry()


def test_m19_T03_edit_after_activation_voids_it(c):
    t = _tmpl(c, c.acct)
    t.with_user(c.mgr).action_activate()
    dr, cr_ = t.line_ids.sorted(lambda line: -line.debit)
    t.with_user(c.acct).write(
        {"line_ids": [Command.update(dr.id, {"debit": 900000.0}), Command.update(cr_.id, {"credit": 900000.0})]}
    )
    assert t.state == "draft" and not t.activated_by_id and t.last_edited_by_id == c.acct
    c.env["fix.journal.template"]._cron_generate_due_entries()
    assert not t.last_move_id
    # a direct line write voids it as well, and its editor cannot re-activate
    t.with_user(c.mgr2).action_activate()
    dr.with_user(c.acct2).write({"label": "same"})
    assert t.state == "active"
    dr.with_user(c.acct2).write({"debit": 5.0})
    assert t.state == "draft"


def test_m19_T04_template_create_via_p03_needs_accountant(c, p03):
    p03.as_user(c.plain)
    res = p03.tmpl_create(
        name="plain accrual",
        lines=[{"account_id": c.exp.id, "debit": 5000, "credit": 0}, {"account_id": c.cash.id, "debit": 0, "credit": 5000}],
    )
    assert not res.get("success")
    p03.as_user(c.acct)
    res = p03.tmpl_create(
        name="rent accrual",
        lines=[{"account_id": c.exp.id, "debit": 5000, "credit": 0}, {"account_id": c.cash.id, "debit": 0, "credit": 5000}],
    )
    assert res.get("success"), res
    t = c.env["fix.journal.template"].browse(res["template_id"])
    assert t.state == "draft" and t.create_uid == c.acct


# ====================================================================== allocation rules
def _rule(c, user, pcts, **kw):
    vals = {
        "name": "A08 alloc %s %d" % (user.login, next(_SEQ)),
        "journal_id": c.misc.id,
        "source_account_id": c.exp.id,
        "line_ids": [
            Command.create({"account_id": c.targets[i].id, "percent": p}) for i, p in enumerate(pcts)
        ],
    }
    vals.update(kw)
    return c.env["fix.allocation.rule"].with_user(user).create(vals)


def test_m19_A01_targets_must_total_100(c):
    with pytest.raises(ValidationError):
        with c.env.cr.savepoint():
            _rule(c, c.acct, [60.0, 30.0])


def test_m19_A02_line_write_keeps_100(c):
    r = _rule(c, c.acct, [60.0, 40.0])
    with pytest.raises(ValidationError, match="must total 100"):
        with c.env.cr.savepoint():
            r.line_ids[0].with_user(c.acct).write({"percent": 10.0})
            c.env.flush_all()
    with pytest.raises(REFUSED):
        with c.env.cr.savepoint():
            r.line_ids[0].with_user(c.acct).unlink()
    with pytest.raises(ValidationError):
        with c.env.cr.savepoint():
            r.line_ids[0].sudo().unlink()
    # a balanced re-split in one save is accepted
    l1, l2 = r.line_ids
    r.with_user(c.acct).write(
        {"line_ids": [Command.update(l1.id, {"percent": 70.0}), Command.update(l2.id, {"percent": 30.0})]}
    )
    assert sorted(r.line_ids.mapped("percent")) == [30.0, 70.0]


def test_m19_A03_rule_needs_activation_by_another_manager(c):
    sys_post(c, c.today, 9000.0)
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rule(c, c.acct, [50.0, 50.0], state="active")
    r = _rule(c, c.acct, [50.0, 50.0])
    with pytest.raises(UserError, match="not active"):
        r.with_user(c.acct).action_run(c.today.replace(day=1), c.today)
    with pytest.raises(UserError):
        r.with_user(c.acct).action_activate()
    r.with_user(c.mgr).action_activate()
    r.with_user(c.acct).action_run(c.today.replace(day=1), c.today)
    assert r.last_run_id.state == "posted"
    # editing the targets after activation returns it to draft
    l1, l2 = r.line_ids
    r.with_user(c.acct).write(
        {"line_ids": [Command.update(l1.id, {"percent": 90.0}), Command.update(l2.id, {"percent": 10.0})]}
    )
    assert r.state == "draft"


def test_m19_A04_rounding_remainder_is_plugged(c):
    sys_post(c, c.today, 10.01)
    r = _rule(c, c.acct, [33.33, 33.33, 33.34])
    r.with_user(c.mgr).action_activate()
    r.with_user(c.acct).action_run(c.today.replace(day=1), c.today)
    mv = r.last_run_id
    assert mv.state == "posted"
    shares = sorted(mv.line_ids.filtered(lambda line: line.account_id in c.targets).mapped("debit"))
    assert round(sum(shares), 2) == 10.01 and shares == [3.33, 3.34, 3.34]


def test_m19_A05_second_run_same_period_refused(c):
    sys_post(c, c.today, 9000.0)
    r = _rule(c, c.acct, [50.0, 50.0])
    r.with_user(c.mgr).action_activate()
    r.with_user(c.acct).action_run(c.today.replace(day=1), c.today)
    with pytest.raises(UserError):
        with c.env.cr.savepoint():
            r.with_user(c.acct).action_run(c.today.replace(day=1), c.today)


# ====================================================================== FX revaluation
def _rate(c, d, bdt_per_usd):
    return c.env["res.currency.rate"].create(
        {"name": d, "currency_id": c.usd.id, "company_id": c.co.id, "inverse_company_rate": bdt_per_usd}
    )


def _usd_receivable(c, usd=100.0, rate=110.0, d=date(2026, 9, 10)):
    m = c.env["account.move"].create(
        {
            "move_type": "entry",
            "journal_id": c.misc.id,
            "date": d,
            "line_ids": [
                Command.create(
                    {
                        "account_id": c.recv.id,
                        "partner_id": c.partner.id,
                        "currency_id": c.usd.id,
                        "amount_currency": usd,
                        "debit": usd * rate,
                        "credit": 0.0,
                    }
                ),
                Command.create({"account_id": c.inc.id, "debit": 0.0, "credit": usd * rate}),
            ],
        }
    )
    m.action_post()
    return m


def _fx(c, user, d=PE, **kw):
    vals = {"rate_date": d, "journal_id": c.misc.id, "gain_account_id": c.fx_gain.id, "loss_account_id": c.fx_loss.id}
    vals.update(kw)
    return c.env["fix.fx.revaluation"].with_user(user).create(vals)


@pytest.fixture
def fx(c):
    _rate(c, date(2026, 9, 1), 110.0)
    inv = _usd_receivable(c)
    _rate(c, date(2026, 9, 30), 120.0)
    _rate(c, date(2026, 10, 31), 120.0)
    return inv


def _recv_reval_balance(c, d):
    lines = c.env["account.move.line"].search(
        [("account_id", "=", c.recv.id), ("parent_state", "=", "posted"), ("date", "<=", d),
         ("move_id.ref", "ilike", "FX revaluation")]
    )
    return round(sum(lines.mapped("balance")), 2)


def test_m19_F01_revaluation_math_and_review(c, fx):
    run = _fx(c, c.acct)
    run.with_user(c.acct).action_compute()
    move = run.with_user(c.mgr).action_post()
    recv = sum(move.line_ids.filtered(lambda line: line.account_id == c.recv).mapped("balance"))
    gain = sum(move.line_ids.filtered(lambda line: line.account_id == c.fx_gain).mapped("balance"))
    assert run.net_amount == 1000.0 and recv == 1000.0 and gain == -1000.0 and move.state == "posted"
    assert run.reversal_move_id.date == PE + timedelta(days=1) and run.reversal_move_id.state == "posted"
    assert run.posted_by_id == c.mgr and run.computed_by_id == c.acct


def test_m19_F02_monthly_runs_do_not_double_count(c, fx):
    """Sep at 120 books 1,000; Oct still 120: the ledger carries 1,000 at Oct-end, not 2,000."""
    r1 = _fx(c, c.acct)
    r1.with_user(c.acct).action_compute()
    r1.with_user(c.mgr).action_post()
    r2 = _fx(c, c.acct, d=date(2026, 10, 31))
    r2.with_user(c.acct).action_compute()
    r2.with_user(c.mgr).action_post()
    assert _recv_reval_balance(c, date(2026, 10, 31)) == 1000.0
    assert _recv_reval_balance(c, date(2026, 10, 15)) == 0.0


def test_m19_F03_one_posted_run_per_date(c, fx):
    r1 = _fx(c, c.acct)
    r1.with_user(c.acct).action_compute()
    r1.with_user(c.mgr).action_post()
    r2 = _fx(c, c.acct)
    r2.with_user(c.acct).action_compute()
    with pytest.raises(UserError, match="already posted"):
        r2.with_user(c.mgr).action_post()


def test_m19_F04_partly_paid_balance_uses_the_open_amount(c, fx):
    inv_line = fx.line_ids.filtered(lambda line: line.account_id == c.recv)
    pay = c.env["account.move"].create(
        {
            "move_type": "entry",
            "journal_id": c.misc.id,
            "date": date(2026, 9, 20),
            "line_ids": [
                Command.create({"account_id": c.cash.id, "debit": 5500.0, "credit": 0.0}),
                Command.create(
                    {
                        "account_id": c.recv.id,
                        "partner_id": c.partner.id,
                        "currency_id": c.usd.id,
                        "amount_currency": -50.0,
                        "debit": 0.0,
                        "credit": 5500.0,
                    }
                ),
            ],
        }
    )
    pay.action_post()
    (inv_line | pay.line_ids.filtered(lambda line: line.account_id == c.recv)).reconcile()
    run = _fx(c, c.acct)
    run.with_user(c.acct).action_compute()
    assert run.net_amount == 500.0
    assert sum(run.line_ids.mapped("foreign_balance")) == 50.0


def test_m19_F05_lines_are_not_writable_and_post_recomputes(c, fx):
    run = _fx(c, c.acct)
    run.with_user(c.acct).action_compute()
    line = run.line_ids[0]
    for user in (c.plain, c.acct, c.mgr):
        with pytest.raises(AccessError):
            with c.env.cr.savepoint():
                line.with_user(user).write({"gain_loss": 1000000.0})
    # a ledger change after compute makes the post refuse
    _usd_receivable(c, usd=10.0, rate=110.0, d=date(2026, 9, 12))
    with pytest.raises(UserError, match="compute it again"):
        run.with_user(c.mgr).action_post()


def test_m19_F06_plain_user_has_no_access_and_state_is_guarded(c, fx, p03):
    run = _fx(c, c.acct)
    run.with_user(c.acct).action_compute()
    with pytest.raises(REFUSED):
        with c.env.cr.savepoint():
            run.with_user(c.plain).write({"state": "posted"})
    with pytest.raises(AccessError):
        with c.env.cr.savepoint():
            run.with_user(c.plain).read(["state"])
    with pytest.raises(UserError, match="changes only through its workflow"):
        run.with_user(c.acct).write({"state": "posted"})
    p03.as_user(c.plain)
    p03.write(model="fix.fx.revaluation", record_id=run.id, values={"state": "posted"})
    c.env.invalidate_all()
    assert run.state == "computed"


def test_m19_F07_plain_user_cannot_compute_or_post(c, fx):
    run = _fx(c, c.acct)
    with pytest.raises(REFUSED):
        with c.env.cr.savepoint():
            run.with_user(c.plain).action_compute()
    run.with_user(c.acct).action_compute()
    with pytest.raises(REFUSED):
        with c.env.cr.savepoint():
            run.with_user(c.plain).action_post()


def test_m19_F08_gain_loss_only_to_configured_fx_accounts(c, fx):
    run = _fx(c, c.acct, gain_account_id=c.cash.id, loss_account_id=c.cash.id)
    run.with_user(c.acct).action_compute()
    with pytest.raises(UserError, match="configured FX gain account"):
        run.with_user(c.mgr).action_post()
    run2 = _fx(c, c.acct, gain_account_id=c.oinc.id)
    run2.with_user(c.acct).action_compute()
    with pytest.raises(UserError, match="configured FX gain account"):
        run2.with_user(c.mgr).action_post()


def test_m19_F09_posted_run_cannot_be_reset_and_reposted(c, fx):
    run = _fx(c, c.acct)
    run.with_user(c.acct).action_compute()
    run.with_user(c.mgr).action_post()
    with pytest.raises(UserError, match="changes only through its workflow"):
        run.with_user(c.acct).write({"state": "computed", "move_id": False})
    with pytest.raises(UserError, match="frozen"):
        run.with_user(c.acct).write({"rate_date": date(2026, 9, 29)})
    with pytest.raises(UserError):
        run.with_user(c.mgr2).action_post()


def test_m19_F10_stale_rate_refused(c):
    _rate(c, date(2026, 9, 1), 110.0)
    _usd_receivable(c)
    c.env["res.currency.rate"].search([("currency_id", "=", c.usd.id)]).unlink()
    _rate(c, date(2010, 1, 1), 90.0)
    run = _fx(c, c.acct)
    with pytest.raises(UserError, match="official closing rate"):
        run.with_user(c.acct).action_compute()


def test_m19_F11_computer_cannot_post(c, fx):
    run = _fx(c, c.acct)
    run.with_user(c.acct).action_compute()
    with pytest.raises(AccessError):
        run.with_user(c.acct).action_post()
    run2 = _fx(c, c.mgr)
    run2.with_user(c.mgr).action_compute()
    with pytest.raises(UserError, match="Segregation of duties"):
        run2.with_user(c.mgr).action_post()


# ====================================================================== M19 posting API contract
def test_m19_api_contract_subledger_posting_is_logged(c):
    """_fix_post_via_m19 / _fix_m19_post: what B4/B5 sub-ledgers call."""
    Move = c.env["account.move"].with_user(c.acct)
    move = Move._fix_post_via_m19(_vals(c, c.today, 321.0), "ar", source_ref="INV-TEST-1")
    log = c.env["fix.journal.posting.log"].search([("move_id", "=", move.id)])
    assert move.state == "posted" and log.source == "ar" and log.source_ref == "INV-TEST-1"
    draft = Move.create(_vals(c, c.today, 123.0))
    draft._fix_m19_post("asset", source_ref="DEP-1")
    assert draft.state == "posted"
    assert c.env["fix.journal.posting.log"].search([("move_id", "=", draft.id)]).source == "asset"
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

    with pytest.raises(UserError, match="drafted for review"):
        post_with_dimensions(c.env(user=c.acct.id), _vals(c, c.today, 5.0), {}, source="manual")


def test_m19_cron_record_exists(c):
    cron = c.env.ref("cd_gl_ext.ir_cron_gl_template_run")
    assert cron.active and "_cron_generate_due_entries" in cron.code


def test_m50_6_unmatched_bank_lines_block_the_close(c):
    """M50-6 / BRU-TRE-19: an imported bank statement line up to the period end that
    is still unmatched blocks the close (cd_cash_position looked up softly)."""
    if "fix.bank.statement.line" not in c.env:
        pytest.skip("cd_cash_position is not installed on this database")
    line = c.env["fix.bank.statement.line"].sudo().create(
        {"date": date(2026, 9, 25), "amount": 1500.0, "statement_file_hash": "b3-m50-6-test"}
    )
    with pytest.raises(UserError, match="unmatched"):
        with c.env.cr.savepoint():
            proper_close(c)
    assert not c.co.fiscalyear_lock_date
    # the line belongs to October once corrected: September no longer waits on it
    line.sudo()._guarded().write({"date": date(2026, 10, 5)})
    close = proper_close(c)
    assert close.state == "closed"
