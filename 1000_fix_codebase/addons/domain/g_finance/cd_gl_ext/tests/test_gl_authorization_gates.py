# cd_gl_ext — who may change what the ledger holds (authorization audit, 10 Nov 2026).
#
# Each test acts as a NON-superuser with a real finance role, created in the
# rolled-back transaction, and reads the ledger afterwards:
#   1  the status of a journal entry changes only by posting, resetting or
#      cancelling it, never by writing (or creating with) `state`;
#   2  the nightly auto-post job does not post a manual journal nobody approved;
#   3  the four legacy take-on wizards post, roll back and import parties only for
#      an Accounting Administrator;
#   4  a close step with no owning group is completed by an Accounting
#      Administrator, not by anyone;
#   5  the Accounting Administrator does every Accountant duty.
from __future__ import annotations

import base64
import io
from datetime import timedelta
from types import SimpleNamespace

import pytest
from odoo import Command, fields
from odoo.exceptions import AccessError, UserError, ValidationError

pytestmark = [pytest.mark.financial]

REFUSED = (UserError, ValidationError, AccessError)
ACC_USER = "account.group_account_user"
ACC_MGR = "account.group_account_manager"
BILL = "account.group_account_invoice"
TIER2 = "cd_entity_config.group_dofa_tier_2"


def _user(env, login, groups=()):
    ou = env["operating.unit"].search([], limit=1)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
                "company_ids": [(6, 0, env.company.ids)],
                "company_id": env.company.id,
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def g(odoo_env):
    env = odoo_env
    x = SimpleNamespace(env=env, co=env.company)
    x.acct = _user(env, "g2_acct", [ACC_USER])
    x.mgr = _user(env, "g2_mgr", [ACC_USER, ACC_MGR, TIER2])
    x.mgr2 = _user(env, "g2_mgr2", [ACC_USER, ACC_MGR, TIER2])
    # the role as it is granted on live: Administrator without Accountant
    x.mgr_only = _user(env, "g2_mgr_only", [ACC_MGR, TIER2])
    x.bill = _user(env, "g2_bill", [BILL])
    Account = env["account.account"]

    def acc(code):
        account = Account.search([("code", "=", code)], limit=1)
        assert account, "fixture: no account %s" % code
        return account

    x.exp = acc("600000")
    x.cash = acc("101401")
    x.misc = env["account.journal"].search(
        [("code", "=", "MISC"), ("company_id", "=", x.co.id)], limit=1
    )
    assert x.misc, "fixture: no MISC journal"
    x.today = fields.Date.context_today(env["account.move"])
    return x


def _vals(g, amount=1000.0, d=None, **move_kw):
    return {
        "move_type": "entry",
        "journal_id": g.misc.id,
        "date": d or g.today,
        "ref": "G2 authorization test",
        "line_ids": [
            Command.create({"account_id": g.exp.id, "debit": amount, "credit": 0.0, "name": "p"}),
            Command.create({"account_id": g.cash.id, "debit": 0.0, "credit": amount, "name": "p"}),
        ],
        **move_kw,
    }


def _dims(g):
    from odoo.addons.cd_gl_ext.models import fix_gl_ext

    branch = fix_gl_ext._default_dimension(g.env, g.co, "branch")
    return {
        i: {"branch_id": branch, "cost_centre": "CORP", "business_line": "SERVICE"}
        for i in range(2)
    }


def _draft_je(g, user, amount=1000.0):
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import create_journal_entry_draft

    return create_journal_entry_draft(
        g.env(user=user.id), _vals(g, amount), _dims(g), source="manual"
    )


def _approve(g, move, user):
    approval = move.fix_journal_approval_id
    task = g.env["fix.workflow.task"].search(
        [
            ("res_model", "=", approval._name),
            ("res_id", "=", approval.id),
            ("state", "=", "pending"),
            ("assigned_user_id", "=", user.id),
        ],
        limit=1,
    )
    assert task, "no pending approval task for %s" % user.login
    task.with_user(user).action_approve()


def _sys_post(g, amount=1000.0):
    move = g.env["account.move"].create(_vals(g, amount))
    move.action_post()
    return move


# ===================================================== 1  state by write / create
@pytest.mark.parametrize("who", ["bill", "acct", "mgr"])
def test_state_posted_by_write_is_refused(g, who):
    """Attack: draft a manual journal, then write state=posted. No approval, no
    number, no posting log: the maker-checker never ran."""
    user = getattr(g, who)
    move = g.env["account.move"].with_user(user).create(_vals(g, 250000.0))
    with pytest.raises(REFUSED), g.env.cr.savepoint():
        move.with_user(user).write({"state": "posted"})
    move.invalidate_recordset()
    assert move.state == "draft"


@pytest.mark.parametrize("target", ["draft", "cancel"])
def test_state_of_a_posted_entry_by_write_is_refused(g, target):
    """Attack: take a posted entry back to draft (to edit and re-post it) or
    cancel it out of the ledger, by a write instead of a reversal."""
    move = _sys_post(g)
    with pytest.raises(REFUSED), g.env.cr.savepoint():
        move.with_user(g.mgr).write({"state": target})
    move.invalidate_recordset()
    assert move.state == "posted"


def test_entry_born_posted_is_refused(g):
    """Attack: create the entry already posted."""
    Move = g.env["account.move"]
    before = Move.search_count([("ref", "=", "G2 born posted")])
    with pytest.raises(REFUSED), g.env.cr.savepoint():
        Move.with_user(g.acct).create(
            {**_vals(g, 90000.0), "ref": "G2 born posted", "state": "posted"}
        )
    assert Move.search_count([("ref", "=", "G2 born posted"), ("state", "=", "posted")]) == before


def test_sanctioned_methods_still_change_state(g):
    """Proper paths: the approval posts (Odoo's own write inside _post), the
    preparer discards a draft (button_cancel), a write that leaves the state as
    it is passes, and trusted code resets an entry (button_draft)."""
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import discard_journal_entry

    move, _log = _draft_je(g, g.acct)
    move.with_user(g.acct).write({"state": "draft", "narration": "same state"})
    _approve(g, move, g.mgr)
    assert move.state == "posted"

    other, _log = _draft_je(g, g.acct, 300.0)
    discard_journal_entry(g.env(user=g.acct.id), other, reason="raised twice")
    assert other.state == "cancel"

    system = _sys_post(g, 40.0)
    system.button_draft()
    assert system.state == "draft"
    system.button_cancel()
    assert system.state == "cancel"


# ============================================================== 2  auto-post job
def _run_autopost(g, monkeypatch):
    """The nightly job as the scheduler runs it (superuser). Its error path
    rolls the cursor back, which would take the test's own records with it."""
    monkeypatch.setattr(g.env.cr, "rollback", lambda: None, raising=False)
    g.env["account.move"]._autopost_draft_entries()
    g.env.invalidate_all()


def test_autopost_job_does_not_post_an_unapproved_manual_journal(g, monkeypatch):
    """Attack: a Billing user drafts a BDT 900,000 manual journal flagged
    auto-post; the nightly job, running as the superuser, posts it."""
    move = (
        g.env["account.move"]
        .with_user(g.bill)
        .create(_vals(g, 900000.0, d=g.today - timedelta(days=1), auto_post="at_date"))
    )
    assert move._fix_is_manual_entry() and move.state == "draft"
    _run_autopost(g, monkeypatch)
    assert move.state == "draft", "the auto-post job posted a manual journal nobody approved"
    assert not move.fix_journal_approval_id
    # the job says why on the entry and stops retrying it
    assert move.auto_post == "no"


def test_superuser_post_of_an_autopost_manual_journal_needs_the_funnel(g):
    """The same door without the job: superuser code posting a manual entry
    flagged auto-post is refused; through the M19 API it posts."""
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

    move = g.env["account.move"].create(_vals(g, 500.0, auto_post="at_date"))
    with pytest.raises(UserError, match="maker-checker"), g.env.cr.savepoint():
        move._post()
    assert move.state == "draft"
    posted, _d = post_with_dimensions(
        g.env, _vals(g, 500.0, auto_post="at_date"), _dims(g), source="api"
    )
    assert posted.state == "posted"
    # trusted code posting an ordinary entry directly is unchanged
    assert _sys_post(g, 10.0).state == "posted"


# ======================================================== 3  take-on wizards
def _xlsx(rows):
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    for row in rows:
        ws.append(list(row))
    buf = io.BytesIO()
    wb.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


REGISTER_HEADER = (
    "Date",
    "Journal Entry",
    "Branch",
    "Company",
    "Created by",
    "Created on",
    "Debit",
    "Credit",
    "Balance",
)


def _register(title, branch, rows):
    """The 9-column legacy ledger export the control, bank and AP lanes read."""
    body = [
        (d, ref, branch, "1000Fix Services Limited", "G2", "2026-10-17 12:00:00", dr, cr, dr - cr)
        for d, ref, dr, cr in rows
    ]
    return _xlsx([(title,), ("Total Records: %d" % len(body),), REGISTER_HEADER, *body])


def _branch(g):
    from odoo.addons.cd_gl_ext.models import fix_gl_ext

    branch = g.env["fix.branch"].browse(fix_gl_ext._default_dimension(g.env, g.co, "branch"))
    assert branch, "fixture: no default branch"
    return branch


def _mig_journal(g):
    Journal = g.env["account.journal"]
    return Journal.search(
        [("code", "=", "MIG"), ("company_id", "=", g.co.id)], limit=1
    ) or Journal.create(
        {"name": "Legacy Take-on", "code": "MIG", "type": "general", "company_id": g.co.id}
    )


def _partner_ledger_batch(g):
    """Staged, validated and imported by the cut-over loader (superuser)."""
    batch = g.env["fix.ledger.takeon.batch"].create(
        {
            "name": "G2 partner-ledger take-on",
            "import_ref": "G2-LEDGER",
            "takeon_date": g.today,
            "source_file": _xlsx(
                [
                    ("Partner", "Debit", "Credit", "Balance"),
                    ("[G2C001] G2 Take-on Customer One", 1500.0, 0.0, 1500.0),
                    ("[G2V001] G2 Take-on Vendor One", 0.0, 400.0, -400.0),
                ]
            ),
            "source_filename": "g2_partner_ledger.xlsx",
        }
    )
    batch.action_stage()
    batch.action_validate()
    batch.action_import()
    batch.contra_account_id = batch._ensure_takeon_account(
        "Legacy Ledger Take-on Contra", "2.99.99.901"
    )
    batch._ensure_takeon_account("Legacy Unallocated Receipts", "2.99.99.902")
    _mig_journal(g)
    assert batch.state == "imported"
    return batch


def _legacy_ledger_batch(g):
    batch = g.env["fix.legacy.ledger.batch"].create(
        {
            "name": "G2 legacy control ledger",
            "import_ref": "G2-LEGAR",
            "legacy_account_code": "G2100201",
            "source_file": _register(
                "Ledger Statement: G2100201 Account Receivable",
                _branch(g).name,
                [
                    ("2026-10-17", "INV/2026/G2001", 700.0, 0.0),
                    ("2026-10-18", "INV/2026/G2002", 0.0, 200.0),
                ],
            ),
            "source_filename": "g2_legacy_ledger.xlsx",
        }
    )
    batch.action_stage()
    batch.action_validate()
    batch.control_account_id = batch._ensure_control_account()
    batch.contra_account_id = batch._ensure_contra_account()
    _mig_journal(g)
    assert batch.state == "validated" and batch.linked_count == 2
    return batch


def _bank_batch(g):
    batch = g.env["fix.bank.takeon.batch"].create(
        {
            "name": "G2 bank ledger",
            "import_ref": "G2-LEGBANK",
            "source_file": _register(
                "Ledger Statement: %s Test Bank" % g.cash.code,
                _branch(g).name,
                [
                    ("2026-10-17", "BNK/2026/G2001", 900.0, 0.0),
                    ("2026-10-18", "BNK/2026/G2002", 0.0, 150.0),
                ],
            ),
            "source_filename": "g2_bank_ledger.xlsx",
        }
    )
    batch.action_stage()
    batch.action_validate()
    batch.contra_account_id = batch._ensure_contra_account()
    _mig_journal(g)
    assert batch.state == "validated" and batch.linked_count == 2
    return batch


def _ap_batch(g):
    batch = g.env["fix.ap.takeon.batch"].create(
        {
            "name": "G2 AP register",
            "import_ref": "G2-AP",
            "legacy_account_code": "G2200101",
            "takeon_date": g.today,
            "source_file": _register(
                "Ledger Statement: G2200101 Account Payable",
                _branch(g).name,
                [
                    ("2026-10-17", "PPBLM/2026/G2001", 800.0, 0.0),
                    ("2026-10-18", "PPBLM/2026/G2002", 350.0, 0.0),
                ],
            ),
            "source_filename": "g2_ap_register.xlsx",
        }
    )
    batch.action_stage()
    batch.action_validate()
    batch.control_account_id = batch._ensure_control_account()
    batch.contra_account_id = batch._ensure_contra_account()
    _mig_journal(g)
    assert batch.state == "validated"
    return batch


TAKEON_BUILDERS = {
    "partner_ledger": _partner_ledger_batch,
    "legacy_control": _legacy_ledger_batch,
    "bank": _bank_batch,
    "ap_register": _ap_batch,
}


def _takeon_moves(g, batch):
    """What the batch put in the ledger, read from the immutable posting log."""
    logs = g.env["fix.journal.posting.log"].search([("source_ref", "like", batch.import_ref)])
    return logs.mapped("move_id").filtered(lambda m: m.state == "posted")


@pytest.mark.parametrize("lane", sorted(TAKEON_BUILDERS))
def test_takeon_post_and_rollback_need_the_accounting_administrator(g, lane):
    """Attack: an accountant alone posts the legacy opening position to the
    general ledger from a validated batch, then reverses it. Held: both are an
    Accounting Administrator's act; the administrator can do both."""
    batch = TAKEON_BUILDERS[lane](g)
    ready = batch.state

    with pytest.raises(AccessError, match="Accounting Administrator"), g.env.cr.savepoint():
        batch.with_user(g.acct).action_post()
    batch.invalidate_recordset()
    assert batch.state == ready and not _takeon_moves(g, batch)

    batch.with_user(g.mgr_only).action_post()
    assert batch.state == "posted" and _takeon_moves(g, batch)
    posted = len(_takeon_moves(g, batch))

    with pytest.raises(AccessError), g.env.cr.savepoint():
        batch.with_user(g.acct).action_rollback()
    batch.invalidate_recordset()
    assert batch.state == "posted" and len(_takeon_moves(g, batch)) == posted

    batch.with_user(g.mgr_only).action_rollback()
    assert batch.state == "rolled_back"


def test_takeon_party_import_needs_the_accounting_administrator(g):
    """Attack: an accountant runs the party import, which creates parties as the
    system and decides both tiers of their registration approval."""
    batch = g.env["fix.ledger.takeon.batch"].create(
        {
            "name": "G2 party import",
            "import_ref": "G2-PARTY",
            "takeon_date": g.today,
            "source_file": _xlsx(
                [
                    ("Partner", "Debit", "Credit", "Balance"),
                    ("[G2C777] G2 Imported Trading Ltd", 2500.0, 0.0, 2500.0),
                ]
            ),
            "source_filename": "g2_party.xlsx",
        }
    )
    batch.action_stage()
    batch.action_validate()
    Partner = g.env["res.partner"]
    with pytest.raises(AccessError), g.env.cr.savepoint():
        batch.with_user(g.acct).action_import()
    batch.invalidate_recordset()
    assert batch.state == "validated"
    assert not Partner.search([("name", "=", "G2 Imported Trading Ltd")])
    batch.with_user(g.mgr_only).action_import()
    assert batch.state == "imported"
    assert Partner.search([("name", "=", "G2 Imported Trading Ltd")])


def test_takeon_batches_are_closed_to_users_outside_finance(g):
    """The access rows: an internal user without a finance role reads, creates
    and writes no take-on batch; the Billing role neither."""
    plain = _user(g.env, "g2_plain")
    for model in (
        "fix.ledger.takeon.batch",
        "fix.legacy.ledger.batch",
        "fix.bank.takeon.batch",
        "fix.ap.takeon.batch",
    ):
        for user in (plain, g.bill):
            Model = g.env[model].with_user(user)
            for mode in ("read", "write", "create", "unlink"):
                assert not Model.has_access(mode), "%s may %s %s" % (user.login, mode, model)


# ===================================================== 4  unowned close step
def test_unowned_close_step_falls_back_to_the_accounting_administrator(g):
    """Attack: a step with no owning group (all ten on live) is completed by any
    internal user. Held: with no owner it is the Accounting Administrator's."""
    plain = _user(g.env, "g2_plain_close")
    evidence = "account.move,%d" % _sys_post(g, 5.0).id
    close = g.env["fix.period.close"].create({"period_end": "2026-09-30"})
    Line = g.env["fix.period.close.line"]
    step = Line.create({"close_id": close.id, "name": "G2 unowned step", "sequence": 10})
    assert not step.owner_group_id
    for user in (plain, g.bill, g.acct):
        with pytest.raises(AccessError), g.env.cr.savepoint():
            step.with_user(user).action_mark_done(evidence)
        with pytest.raises(AccessError), g.env.cr.savepoint():
            step.with_user(user).action_set_state("in_progress")
    step.invalidate_recordset()
    assert step.state == "pending" and not step.done_by_id
    step.with_user(g.mgr_only).action_mark_done(evidence)
    assert step.state == "done" and step.done_by_id == g.mgr_only


# ================================================ 5  administrator as accountant
def test_administrator_without_accountant_group_does_accountant_duties(g):
    """On this build Accounting Administrator does not imply Accountant, so the
    finance manager could not draft a journal, start a close or complete an
    accountant's close step."""
    assert not g.mgr_only.has_group(ACC_USER), "fixture: the manager group implies the user group"
    move, log = _draft_je(g, g.mgr_only, 1200.0)
    assert move.state == "draft" and log.state == "requested"
    # segregation still holds: another administrator approves, not the preparer
    _approve(g, move, g.mgr)
    assert move.state == "posted"

    close = g.env["fix.period.close"].with_user(g.mgr_only).action_start_period("2026-08-31")
    assert close.state == "in_progress" and len(close.line_ids) == 10
    accountant_step = close.line_ids.filtered(lambda s: s.sequence == 20)
    assert accountant_step.owner_group_id == g.env.ref(ACC_USER)
    accountant_step.with_user(g.mgr_only).action_mark_done("account.move,%d" % move.id)
    assert accountant_step.state == "done"


def test_administrator_without_accountant_group_computes_an_fx_revaluation(g):
    def account(code):
        return g.env["account.account"].search([("code", "=", code)], limit=1)

    run = (
        g.env["fix.fx.revaluation"]
        .with_user(g.mgr_only)
        .create(
            {
                "rate_date": "2026-09-30",
                "journal_id": g.misc.id,
                "gain_account_id": (
                    g.co.income_currency_exchange_account_id or account("441000")
                ).id,
                "loss_account_id": (
                    g.co.expense_currency_exchange_account_id or account("641000")
                ).id,
            }
        )
    )
    run.with_user(g.mgr_only).action_compute()
    assert run.state == "computed" and run.computed_by_id == g.mgr_only
    with pytest.raises(AccessError), g.env.cr.savepoint():
        run.with_user(g.bill).action_compute()


def test_accountant_is_still_not_an_administrator(g):
    """The widening goes one way."""
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import has_role

    assert has_role(g.env(user=g.acct.id), ACC_USER)
    assert not has_role(g.env(user=g.acct.id), ACC_MGR)
    assert has_role(g.env(user=g.mgr_only.id), ACC_USER)
    assert not has_role(g.env(user=g.bill.id), ACC_USER)
    close = g.env["fix.period.close"].with_user(g.acct).action_start_period("2026-08-31")
    cfo_step = close.line_ids.filtered(lambda s: s.sequence == 100)
    evidence = "account.move,%d" % _sys_post(g, 5.0).id
    with pytest.raises(AccessError, match="owned by"), g.env.cr.savepoint():
        cfo_step.with_user(g.acct).action_mark_done(evidence)
