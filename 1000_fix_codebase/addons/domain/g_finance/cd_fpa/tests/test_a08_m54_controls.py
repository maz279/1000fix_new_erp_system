# A08 remediation, M54 FP&A / budgets / cost allocation / board pack (cd_fpa):
# control tests. One test per gap probe of
# working/A08_evidence/probes/m54/probe_m54.py (same id, same attack, as NON-ADMIN
# users with the real finance roles created in the rolled-back transaction), plus
# the proper path: the preparer submits, a CFO-tier Accounting Administrator who
# did not prepare it approves from the M63 inbox, revisions are new versions.
import types
from datetime import date

import pytest
from odoo import Command, fields
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2.errors import UniqueViolation

REFUSED = (UserError, ValidationError, AccessError)
ACC_USER = "account.group_account_user"
ACC_MGR = "account.group_account_manager"
TIER4 = "cd_entity_config.group_dofa_tier_4"
TIER5 = "cd_entity_config.group_dofa_tier_5"
FY_FROM, FY_TO = date(2026, 7, 1), date(2027, 6, 30)


class Ctx:
    pass


_SEQ = iter(range(1, 100000))


def _user(env, login, groups=()):
    Users = env["res.users"].with_context(no_reset_password=True)
    gids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    ou = env["operating.unit"].search([], limit=1)
    return Users.create(
        {
            "name": login,
            "login": login,
            "group_ids": [(6, 0, gids)],
            "company_ids": [(6, 0, env.company.ids)],
            "company_id": env.company.id,
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
    bdt = env.ref("base.BDT")
    if x.co.currency_id != bdt:
        x.co.sudo().write({"currency_id": bdt.id})
    x.acct = _user(env, "a08b3m54_acct", [ACC_USER])
    x.acct2 = _user(env, "a08b3m54_acct2", [ACC_USER])
    # Finance Managers: Accounting Administrators holding the CFO tier.
    x.mgr = _user(env, "a08b3m54_mgr", [ACC_MGR, TIER4])
    x.mgr2 = _user(env, "a08b3m54_mgr2", [ACC_MGR, TIER4])
    x.board = _user(env, "a08b3m54_board", [ACC_MGR, TIER5])
    x.both = _user(env, "a08b3m54_both", [ACC_USER, ACC_MGR, TIER4])
    x.plain = _user(env, "a08b3m54_plain")
    A = env["account.account"]
    acc = lambda code: A.search([("code", "=", code)], limit=1)  # noqa: E731
    x.inc = acc("400000")
    x.exp = acc("600000")
    x.absorbed = acc("610000")
    x.clearing = acc("611000")
    x.cash = acc("101401")
    x.misc = env["account.journal"].search(
        [("code", "=", "MISC"), ("company_id", "=", x.co.id)], limit=1
    )
    x.ou = env["operating.unit"].search([], limit=1)
    return x


def je(c, d, amount, debit, credit):
    """Ledger fixture posted by trusted code."""
    m = c.env["account.move"].create(
        {
            "move_type": "entry",
            "journal_id": c.misc.id,
            "date": d,
            "line_ids": [
                Command.create(
                    {"account_id": debit.id, "debit": amount, "credit": 0.0, "name": "p"}
                ),
                Command.create(
                    {"account_id": credit.id, "debit": 0.0, "credit": amount, "name": "p"}
                ),
            ],
        }
    )
    m.action_post()
    return m


def version(
    c, user, planned=100000.0, account=None, d_from=date(2026, 9, 1), d_to=date(2026, 9, 30), **kw
):
    vals = {
        "name": "A08 FY27 budget %d" % next(_SEQ),
        "version_type": "budget",
        "fiscal_year": "FY2026-27-%d" % next(_SEQ),
        "date_from": FY_FROM,
        "date_to": FY_TO,
    }
    vals.update(kw)
    ver = c.env["fix.budget.version"].with_user(user).create(vals)
    c.env["fix.budget"].with_user(user).create(
        {
            "name": "Opex",
            "version_id": ver.id,
            "line_ids": [
                Command.create(
                    {
                        "account_id": (account or c.exp).id,
                        "date_from": d_from,
                        "date_to": d_to,
                        "planned_amount": planned,
                    }
                )
            ],
        }
    )
    return ver


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


def bva_rows(c, user, d_from=date(2026, 9, 1), d_to=date(2026, 9, 30), **kw):
    return (
        c.env["fix.fpa.engine"].with_user(user).report_budget_variance(d_from, d_to, **kw)["rows"]
    )


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()
    mw = getattr(
        g.P03GenericApiController.model_write,
        "original_endpoint",
        g.P03GenericApiController.model_write,
    )
    old = (getattr(g, "request", None), getattr(s, "request", None))

    def as_user(user):
        req = types.SimpleNamespace(env=c.env(user=user.id))
        g.request = req
        s.request = req

    try:
        yield types.SimpleNamespace(as_user=as_user, write=lambda **kw: mw(ctl, **kw))
    finally:
        g.request, s.request = old


# ====================================================================== budget versions
def test_m54_B01_submit_route_approve_and_bva(c):
    ver = version(c, c.acct)
    ver.with_user(c.acct).action_submit()
    assert ver.state == "submitted" and ver.approval_state == "pending"
    assert ver.dofa_tier_required == "tier_4"
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        ver.with_user(c.acct).action_approve()
    with pytest.raises(UserError, match="approver's inbox"):
        ver.with_user(c.mgr).action_approve()
    approve_as(c, ver, c.mgr)
    assert ver.state == "approved" and ver.approved_by == c.mgr
    je(c, date(2026, 9, 12), 30000.0, c.exp, c.cash)
    rows = [r for r in bva_rows(c, c.acct) if r["version"] == ver.name]
    assert len(rows) == 1 and rows[0]["planned"] == 100000.0 and rows[0]["actual"] == 30000.0, rows


def test_m54_B02_submitter_cannot_approve(c):
    ver = version(c, c.both)
    ver.with_user(c.both).action_submit()
    assert not task_for(c, ver, c.both)


def test_m54_B03_preparer_cannot_approve(c):
    """Attack: the manager prepares, a junior submits, the manager approves."""
    ver = version(c, c.mgr, planned=900000.0)
    ver.with_user(c.acct).action_submit()
    assert not task_for(c, ver, c.mgr) and task_for(c, ver, c.mgr2)
    approve_as(c, ver, c.mgr2)
    assert ver.state == "approved" and ver.approved_by == c.mgr2


def test_m54_B04_approval_cannot_be_typed(c):
    ver = version(c, c.acct, planned=5000000.0)
    with pytest.raises(UserError, match="changes only through its workflow"):
        ver.with_user(c.acct).write(
            {"state": "approved", "approved_by": c.mgr.id, "approved_at": fields.Datetime.now()}
        )
    assert ver.state == "draft" and not [r for r in bva_rows(c, c.acct) if r["version"] == ver.name]


def test_m54_B05_approved_budget_is_immutable_and_revised_as_a_new_version(c):
    ver = version(c, c.acct)
    ver.with_user(c.acct).action_submit()
    approve_as(c, ver, c.mgr)
    line = ver.budget_ids.line_ids
    with pytest.raises(UserError, match="changes only through its workflow"):
        ver.with_user(c.acct).write({"state": "draft"})
    with pytest.raises(UserError, match="only a draft version"):
        line.with_user(c.acct).write({"planned_amount": 10000000.0})
    assert line.planned_amount == 100000.0
    # the revision path: a new version with its own approval
    rev = ver.with_user(c.acct).action_create_revision()
    assert rev.state == "draft" and rev.revision_of_id == ver and ver.state == "approved"
    rev.budget_ids.line_ids.with_user(c.acct).write({"planned_amount": 150000.0})
    rev.with_user(c.acct).action_submit()
    approve_as(c, rev, c.mgr2)
    assert rev.state == "approved" and ver.state == "superseded"
    assert ver.budget_ids.line_ids.planned_amount == 100000.0


def test_m54_B06_approved_line_edit_refused(c):
    ver = version(c, c.acct)
    ver.with_user(c.acct).action_submit()
    approve_as(c, ver, c.mgr)
    with pytest.raises(UserError):
        ver.budget_ids.line_ids.with_user(c.acct).write({"planned_amount": 1.0})
    with pytest.raises(UserError):
        ver.with_user(c.acct).write({"name": "renamed"})


def test_m54_B07_actual_is_the_ledger_not_a_typed_figure(c):
    ver = version(c, c.acct)
    ver.with_user(c.acct).action_submit()
    approve_as(c, ver, c.mgr)
    bud = ver.budget_ids
    try:
        with c.env.cr.savepoint():
            bud.with_user(c.acct).write({"actual_amount": 99999999.0})
    except REFUSED:
        pass
    c.env.invalidate_all()
    assert bud.actual_amount == 0.0
    je(c, date(2026, 9, 12), 4000.0, c.exp, c.cash)
    c.env.invalidate_all()
    assert bud.actual_amount == 4000.0 and bud.variance == 96000.0


def test_m54_B08_versionless_budget_refused(c):
    with pytest.raises(REFUSED):
        c.env["fix.budget"].with_user(c.acct).create(
            {
                "name": "orphan",
                "fiscal_year": "FY2026-27",
                "planned_amount": 2000000.0,
                "state": "approved",
            }
        )
    with pytest.raises(ValidationError, match="belongs to a budget version"):
        c.env["fix.budget"].with_user(c.acct).create({"name": "orphan", "fiscal_year": "FY2026-27"})


def test_m54_B09_one_approved_version_per_year(c):
    fy = "FY-A08-%d" % next(_SEQ)
    v1 = version(c, c.acct, fiscal_year=fy)
    v1.with_user(c.acct).action_submit()
    approve_as(c, v1, c.mgr)
    v2 = version(c, c.acct, planned=500000.0, fiscal_year=fy)
    with pytest.raises(UserError, match="changes only through its workflow"):
        v2.with_user(c.acct).write({"state": "approved"})
    # the database refuses two approved versions: that index, and nothing else
    with pytest.raises(UniqueViolation) as refused, c.env.cr.savepoint():
        v2._guarded().write({"state": "approved"})
        c.env.flush_all()
    assert "one_approved_per_year" in refused.value.diag.constraint_name
    c.env.invalidate_all()
    rows = [r for r in bva_rows(c, c.mgr) if r["version"] in (v1.name, v2.name)]
    assert len(rows) == 1 and rows[0]["planned"] == 100000.0
    # approving the second the proper way supersedes the first
    v2.with_user(c.acct).action_submit()
    approve_as(c, v2, c.mgr2)
    assert v1.state == "superseded" and v2.state == "approved"


def test_m54_B10_bva_measures_the_report_window(c):
    ver = version(c, c.acct, planned=1200000.0, d_from=FY_FROM, d_to=FY_TO)
    ver.with_user(c.acct).action_submit()
    approve_as(c, ver, c.mgr)
    je(c, date(2026, 8, 10), 100000.0, c.exp, c.cash)
    je(c, date(2026, 9, 10), 50000.0, c.exp, c.cash)
    r = next(row for row in bva_rows(c, c.mgr) if row["version"] == ver.name)
    assert r["actual"] == 50000.0
    assert r["planned"] == round(1200000.0 * 30 / 365, 2)


def test_m54_B11_p03_write_cannot_approve(c, p03):
    ver = version(c, c.acct)
    p03.as_user(c.acct)
    p03.write(model="fix.budget.version", record_id=ver.id, values={"state": "approved"})
    c.env.invalidate_all()
    assert ver.state != "approved"


def test_m54_B12_reject_needs_reason(c):
    ver = version(c, c.acct)
    ver.with_user(c.acct).action_submit()
    with pytest.raises(UserError), c.env.cr.savepoint():
        ver.with_user(c.mgr).action_reject()
    ver.with_user(c.mgr).write({"rejection_reason": "Rent line unsupported"})
    ver.with_user(c.mgr).action_reject()
    assert ver.state == "rejected" and ver.approval_state == "none"
    ver.with_user(c.acct).action_reset_draft()
    assert ver.state == "draft"


def test_m54_B13_manager_can_prepare_and_submit(c):
    """M54-8 resolved: the Accounting Administrator prepares and submits too; the CFO
    tier of another administrator approves."""
    ver = version(c, c.mgr)
    ver.with_user(c.mgr).action_submit()
    assert ver.state == "submitted" and not task_for(c, ver, c.mgr)
    approve_as(c, ver, c.mgr2)
    assert ver.state == "approved"


def test_m54_B14_board_threshold_routes_to_tier_5(c):
    ver = version(c, c.acct, planned=25000000.0)
    ver.with_user(c.acct).action_submit()
    assert ver.dofa_tier_required == "tier_5"
    assert not task_for(c, ver, c.mgr) and task_for(c, ver, c.board)
    approve_as(c, ver, c.board)
    assert ver.state == "approved"


# ====================================================================== board pack
def _pack(c, user):
    return (
        c.env["fix.board.pack"]
        .with_user(user)
        .create(
            {"name": "Board pack Sep", "date_from": date(2026, 9, 1), "date_to": date(2026, 9, 30)}
        )
    )


def test_m54_K01_assemble_and_issue_sod(c):
    je(c, date(2026, 9, 5), 80000.0, c.cash, c.inc)
    p = _pack(c, c.acct)
    p.with_user(c.acct).action_assemble()
    rev = p.line_ids.filtered(lambda line: line.metric == "Revenue").amount
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        p.with_user(c.acct).action_issue()
    p2 = _pack(c, c.mgr)
    p2.with_user(c.mgr).action_assemble()
    with pytest.raises(UserError), c.env.cr.savepoint():
        p2.with_user(c.mgr).action_issue()
    p.with_user(c.mgr2).action_issue()
    assert p.state == "issued" and p.assembled_by == c.acct and rev >= 80000.0


def test_m54_K02_issued_pack_lines_frozen(c):
    je(c, date(2026, 9, 5), 80000.0, c.cash, c.inc)
    p = _pack(c, c.acct)
    p.with_user(c.acct).action_assemble()
    p.with_user(c.mgr).action_issue()
    line = p.line_ids.filtered(lambda line: line.metric == "Revenue")
    before = line.amount
    with pytest.raises(UserError, match="frozen"):
        line.with_user(c.acct).write({"amount": 8000000.0})
    with pytest.raises(UserError):
        line.with_user(c.mgr).unlink()
    with pytest.raises(UserError):
        c.env["fix.board.pack.line"].with_user(c.acct).create(
            {"pack_id": p.id, "section": "P&L", "metric": "Extra", "amount": 1.0}
        )
    assert line.amount == before


def test_m54_K03_issue_cannot_be_typed(c):
    p = _pack(c, c.acct)
    with pytest.raises(UserError, match="changes only through its workflow"):
        p.with_user(c.acct).write(
            {"state": "issued", "issued_by": c.mgr.id, "issued_at": fields.Datetime.now()}
        )
    assert p.state == "draft"


def test_m54_K04_assembled_by_cannot_be_rewritten(c):
    p = _pack(c, c.mgr)
    p.with_user(c.mgr).action_assemble()
    with pytest.raises(UserError, match="changes only through its workflow"):
        p.with_user(c.mgr).write({"assembled_by": c.acct.id})
    with pytest.raises(UserError, match="Segregation of duties"):
        p.with_user(c.mgr).action_issue()


def test_m54_K05_lines_cannot_be_tampered_before_issue(c):
    je(c, date(2026, 9, 5), 80000.0, c.cash, c.inc)
    p = _pack(c, c.acct)
    p.with_user(c.acct).action_assemble()
    line = p.line_ids.filtered(lambda line: line.metric == "Revenue")
    with pytest.raises(UserError, match="frozen"):
        line.with_user(c.acct).write({"amount": 800000.0})
    p.with_user(c.mgr).action_issue()
    assert p.state == "issued"


def test_m54_K06_issued_pack_frozen(c):
    p = _pack(c, c.acct)
    p.with_user(c.acct).action_assemble()
    p.with_user(c.mgr).action_issue()
    with pytest.raises(UserError), c.env.cr.savepoint():
        p.with_user(c.mgr).write({"date_to": date(2026, 10, 31)})
    with pytest.raises(UserError), c.env.cr.savepoint():
        p.with_user(c.mgr).unlink()


def test_m54_K07_plain_user_cannot_read_pack(c):
    p = _pack(c, c.acct)
    with pytest.raises(AccessError):
        p.with_user(c.plain).read(["name"])


# ====================================================================== cost allocation
@pytest.fixture
def pool(c):
    env = c.env
    n = next(_SEQ)
    ent = env["fix.entity"].create(
        {"code": "A08FPA%d" % n, "legal_name": "A08 FPA", "company_id": c.co.id}
    )
    b1 = env["fix.branch"].create(
        {"code": "B1%d" % n, "name": "Dhanmondi", "entity_id": ent.id, "operating_unit_id": c.ou.id}
    )
    b2 = env["fix.branch"].create(
        {"code": "B2%d" % n, "name": "Uttara", "entity_id": ent.id, "operating_unit_id": c.ou.id}
    )
    p = env["fix.cost.pool"].create(
        {
            "code": "A08P%d" % n,
            "name": "Head-office rent",
            "receiver_type": "branch",
            "allocation_basis": "fixed",
            "target_account_id": c.absorbed.id,
            "clearing_account_id": c.clearing.id,
            "journal_id": c.misc.id,
            "element_ids": [
                Command.create({"code": "RENT", "name": "Rent", "account_ids": [(6, 0, c.exp.ids)]})
            ],
            "share_ids": [
                Command.create({"branch_id": b1.id, "percent": 60.0}),
                Command.create({"branch_id": b2.id, "percent": 40.0}),
            ],
        }
    )
    je(c, date(2026, 9, 3), 10000.0, c.exp, c.cash)
    y = Ctx()
    y.pool, y.b1, y.b2 = p, b1, b2
    return y


def _alloc(c, pool, user):
    return (
        c.env["fix.cost.allocation"]
        .with_user(user)
        .create(
            {
                "name": "Rent Sep %d" % next(_SEQ),
                "pool_id": pool.pool.id,
                "date_from": date(2026, 9, 1),
                "date_to": date(2026, 9, 30),
            }
        )
    )


def test_m54_L01_compute_and_post_by_different_accountants(c, pool):
    a = _alloc(c, pool, c.acct)
    a.with_user(c.acct).action_compute()
    a.with_user(c.acct2).action_post()
    amounts = sorted(a.line_ids.mapped("amount"))
    mv = a.move_id
    assert amounts == [4000.0, 6000.0] and mv.state == "posted" and mv.amount_total == 10000.0
    assert a.computed_by == c.acct and a.posted_by == c.acct2
    log = c.env["fix.journal.posting.log"].search([("move_id", "=", mv.id)])
    assert log.source == "allocation" and log.source_ref == a.name


def test_m54_L02_lines_cannot_be_typed_and_post_recomputes(c, pool):
    a = _alloc(c, pool, c.acct)
    a.with_user(c.acct).action_compute()
    l1, l2 = a.line_ids.sorted("amount")
    with pytest.raises(UserError, match="changes only through its workflow"):
        l1.with_user(c.acct).write({"amount": 40000.0})
    with pytest.raises(UserError, match="changes only through its workflow"):
        a.with_user(c.acct).write({"allocated_overhead": 100000.0})
    # the ledger moves after compute: the post refuses the stale split
    je(c, date(2026, 9, 20), 5000.0, c.exp, c.cash)
    with pytest.raises(UserError, match="no longer agrees with the ledger"):
        a.with_user(c.acct2).action_post()
    a.with_user(c.acct).action_compute()
    a.with_user(c.acct2).action_post()
    assert a.move_id.amount_total == a.direct_cost == 15000.0


def test_m54_L03_computer_cannot_post(c, pool):
    a = _alloc(c, pool, c.acct)
    a.with_user(c.acct).action_compute()
    with pytest.raises(UserError, match="Segregation of duties"):
        a.with_user(c.acct).action_post()


def test_m54_L04_overlapping_period_refused(c, pool):
    a = _alloc(c, pool, c.acct)
    a.with_user(c.acct).action_compute()
    a.with_user(c.acct2).action_post()
    b = _alloc(c, pool, c.acct)
    b.with_user(c.acct).action_compute()
    with pytest.raises(UserError), c.env.cr.savepoint():
        b.with_user(c.acct2).action_post()


def test_m54_L05_fixed_shares_must_total_100(c, pool):
    pool.pool.share_ids[0].write({"percent": 90.0})
    a = _alloc(c, pool, c.acct)
    with pytest.raises(UserError), c.env.cr.savepoint():
        a.with_user(c.acct).action_compute()


def test_m54_L06_posted_state_cannot_be_typed(c, pool):
    a = _alloc(c, pool, c.acct)
    a.with_user(c.acct).action_compute()
    with pytest.raises(UserError, match="changes only through its workflow"):
        a.with_user(c.acct).write({"state": "posted"})
    assert a.state == "computed" and not a.move_id
