# cd_fpa — live-ORM behaviour of M54: budgets and versions (SoD workflow),
# cost pools and posted allocation cycles, scenario drivers, board packs.
#
# Every test runs in a private company (fix_test is shared by concurrent
# suites) inside the rolled-back `odoo_env` transaction.
from __future__ import annotations

import base64
import itertools
import uuid
from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest
from odoo import Command
from odoo.exceptions import AccessError, UserError, ValidationError

pytestmark = [pytest.mark.financial]

D = Decimal
_SEQ = itertools.count(1)


def _money(value) -> Decimal:
    return D(str(value)).quantize(D("0.01"))


# --------------------------------------------------------------------------- fixtures


@pytest.fixture
def fpa(odoo_env):
    """A private company with an operating unit, two branches, a journal and
    income / direct-cost / expense / allocation accounts."""
    tag = uuid.uuid4().hex[:6].upper()
    root = odoo_env
    company = root["res.company"].create({"name": f"FPA Test Co {tag}"})
    root.user.write({"company_ids": [Command.link(company.id)]})
    env = root(context=dict(root.context, allowed_company_ids=[company.id]))
    ou = env["operating.unit"].create(
        {
            "name": f"FPA OU {tag}",
            "code": f"F{tag}",
            "company_id": company.id,
            "partner_id": company.partner_id.id,
        }
    )
    entity = env["fix.entity"].create(
        {"code": f"EN{tag}", "legal_name": "FPA Test Entity", "company_id": company.id}
    )

    def branch(code, name):
        return env["fix.branch"].create(
            {"code": code, "name": name, "entity_id": entity.id, "operating_unit_id": ou.id}
        )

    dhk = branch(f"D{tag[:4]}", "Dhanmondi")
    ctg = branch(f"C{tag[:4]}", "Chattogram")
    journal = env["account.journal"].create(
        {"name": "FPA Misc", "code": f"F{tag[:4]}", "type": "general", "company_id": company.id}
    )

    def account(code, name, account_type):
        return (
            env["account.account"]
            .with_company(company)
            .create(
                {
                    "name": name,
                    "code": code,
                    "account_type": account_type,
                    "company_ids": [(6, 0, company.ids)],
                }
            )
        )

    acc = SimpleNamespace(
        income=account("410001", "Repair revenue", "income"),
        direct=account("510001", "Parts consumed", "expense_direct_cost"),
        rent=account("610001", "Branch rent", "expense"),
        utilities=account("610002", "Utilities", "expense"),
        absorbed=account("690001", "Overhead absorbed", "expense"),
        clearing=account("690002", "Overhead pool clearing", "expense"),
        bank=account("110001", "Bank", "asset_cash"),
    )
    return SimpleNamespace(
        env=env, company=company, ou=ou, dhk=dhk, ctg=ctg, journal=journal, acc=acc, tag=tag
    )


def _post(fpa, account, amount, when, branch=None, business_line=None, credit=False):
    """Post one P&L amount against the bank with optional dimensions."""
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

    pnl = {"name": "P&L", "account_id": account.id, "debit": 0.0, "credit": 0.0}
    bank = {"name": "Bank", "account_id": fpa.acc.bank.id, "debit": 0.0, "credit": 0.0}
    if credit:
        pnl["credit"], bank["debit"] = amount, amount
    else:
        pnl["debit"], bank["credit"] = amount, amount
    dims = {}
    tag = {}
    if branch:
        tag["branch_id"] = branch.id
        tag["operating_unit_id"] = branch.operating_unit_id.id
    if business_line:
        tag["business_line"] = business_line
    if tag:
        dims[0] = tag
    move, _dims = post_with_dimensions(
        fpa.env,
        {
            "journal_id": fpa.journal.id,
            "company_id": fpa.company.id,
            "date": when,
            "line_ids": [(0, 0, pnl), (0, 0, bank)],
        },
        dims,
    )
    return move


def _user(env, *groups):
    n = next(_SEQ)
    return env["res.users"].create(
        {
            "name": f"FPA User {n}",
            "login": f"fpa-user-{n}-{uuid.uuid4().hex[:6]}@test.local",
            "company_id": env.company.id,
            "company_ids": [Command.set(env.companies.ids)],
            "group_ids": [Command.set([env.ref(g).id for g in groups])],
        }
    )


# --------------------------------------------------------------------------- legacy fields


def test_budget_variance_follows_actuals(odoo_env):
    budget = odoo_env["fix.budget"].create(
        {"name": "FY2027 Dhaka workshop", "fiscal_year": "FY2027", "planned_amount": 500000.0}
    )
    assert budget.currency_id == odoo_env.ref("base.BDT")
    assert _money(budget.variance) == D("500000.00")
    budget.actual_amount = 512345.67
    assert _money(budget.variance) == D("-12345.67")  # overspend is negative
    assert budget.state == "draft"


def test_cost_allocation_total(odoo_env):
    alloc = odoo_env["fix.cost.allocation"].create(
        {"name": "Job JOB-8849", "direct_cost": 1999.99, "allocated_overhead": 250.01}
    )
    assert _money(alloc.total_cost) == D("2250.00")
    alloc.allocated_overhead = 0.0
    assert _money(alloc.total_cost) == D("1999.99")


# --------------------------------------------------------------------------- business lines


def test_fourteen_business_lines_are_seeded_master_data(odoo_env):
    lines = odoo_env["fix.business.line"].search([("code", "=like", "BL-%")])
    assert len(lines.filtered(lambda bl: bl.revenue_stream_no)) >= 14
    bl02 = odoo_env.ref("cd_fpa.business_line_bl_02")
    assert (bl02.code, bl02.name) == ("BL-02", "Out-of-warranty paid repair")


def test_business_line_code_format_is_enforced(odoo_env):
    with pytest.raises(ValidationError, match="BL-nn"), odoo_env.cr.savepoint():
        odoo_env["fix.business.line"].create({"code": "RETAIL", "name": "Retail"})


# --------------------------------------------------------------------------- cost pools


def _pool(fpa, **vals):
    base = {
        "code": f"P{next(_SEQ)}",
        "name": "Branch overhead",
        "allocation_basis": "fixed",
        "target_account_id": fpa.acc.absorbed.id,
        "clearing_account_id": fpa.acc.clearing.id,
        "journal_id": fpa.journal.id,
        "element_ids": [
            (0, 0, {"code": "RENT", "name": "Rent", "account_ids": [(6, 0, fpa.acc.rent.ids)]}),
            (
                0,
                0,
                {
                    "code": "UTIL",
                    "name": "Utilities",
                    "account_ids": [(6, 0, fpa.acc.utilities.ids)],
                },
            ),
        ],
    }
    base.update(vals)
    return fpa.env["fix.cost.pool"].create(base)


def test_pool_posting_accounts_must_differ(fpa):
    with pytest.raises(ValidationError, match="must differ"), fpa.env.cr.savepoint():
        _pool(fpa, clearing_account_id=fpa.acc.absorbed.id)


def test_pool_cannot_allocate_its_own_element_account(fpa):
    with pytest.raises(ValidationError, match="feed itself"), fpa.env.cr.savepoint():
        _pool(fpa, target_account_id=fpa.acc.rent.id)


def test_an_account_is_gathered_by_one_element_only(fpa):
    _pool(fpa)
    with pytest.raises(ValidationError, match="gathered once only"), fpa.env.cr.savepoint():
        _pool(
            fpa,
            element_ids=[
                (
                    0,
                    0,
                    {"code": "R2", "name": "Rent again", "account_ids": [(6, 0, fpa.acc.rent.ids)]},
                )
            ],
        )


def test_business_line_receivers_need_revenue_or_fixed_basis(fpa):
    with pytest.raises(ValidationError, match="business-line receivers"), fpa.env.cr.savepoint():
        _pool(fpa, receiver_type="business_line", allocation_basis="service_orders")


# --------------------------------------------------------------------------- allocation cycles


def _cycle(fpa, pool):
    return fpa.env["fix.cost.allocation"].create(
        {
            "name": f"OH Oct {pool.code}",
            "pool_id": pool.id,
            "date_from": date(2031, 10, 1),
            "date_to": date(2031, 10, 31),
        }
    )


def test_fixed_share_allocation_computes_posts_and_reverses(fpa):
    _post(fpa, fpa.acc.rent, 70000.0, date(2031, 10, 5))
    _post(fpa, fpa.acc.utilities, 30000.01, date(2031, 10, 20))
    _post(fpa, fpa.acc.rent, 99999.0, date(2031, 11, 2))  # outside the period
    pool = _pool(
        fpa,
        share_ids=[
            (0, 0, {"branch_id": fpa.dhk.id, "percent": 60.0}),
            (0, 0, {"branch_id": fpa.ctg.id, "percent": 40.0}),
        ],
    )
    cycle = _cycle(fpa, pool)
    cycle.action_compute()
    assert cycle.state == "computed"
    assert _money(cycle.direct_cost) == D("100000.01")
    amounts = {ln.branch_id: _money(ln.amount) for ln in cycle.line_ids}
    # 60% = 60000.006 -> 60000.01 ; the last receiver takes the remainder
    assert sum(amounts.values()) == D("100000.01")
    assert (amounts[fpa.dhk], amounts[fpa.ctg]) == (D("60000.01"), D("40000.00"))

    cycle.action_post()
    move = cycle.move_id
    assert cycle.state == "posted" and move.state == "posted"
    debit_lines = move.line_ids.filtered(lambda ln: ln.account_id == fpa.acc.absorbed)
    credit = move.line_ids.filtered(lambda ln: ln.account_id == fpa.acc.clearing)
    assert _money(sum(debit_lines.mapped("debit"))) == D("100000.01")
    assert _money(credit.credit) == D("100000.01")
    dims = fpa.env["fix.journal.dimension"].search([("move_line_id", "in", debit_lines.ids)])
    assert set(dims.mapped("branch_id")) == {fpa.dhk, fpa.ctg}

    # a second cycle of the same pool over the same period is refused
    again = _cycle(fpa, pool)
    again.action_compute()
    with pytest.raises(UserError, match="already allocated"), fpa.env.cr.savepoint():
        again.action_post()

    cycle.action_reverse()
    assert cycle.state == "reversed"
    assert cycle.reversal_move_id.state == "posted"
    assert _money(sum(cycle.reversal_move_id.line_ids.mapped("credit"))) == D("100000.01")


def test_fixed_shares_must_total_one_hundred(fpa):
    _post(fpa, fpa.acc.rent, 1000.0, date(2031, 10, 5))
    pool = _pool(fpa, share_ids=[(0, 0, {"branch_id": fpa.dhk.id, "percent": 90.0})])
    cycle = _cycle(fpa, pool)
    with pytest.raises(UserError, match="not 100"), fpa.env.cr.savepoint():
        cycle.action_compute()


def test_revenue_basis_splits_on_posted_branch_revenue(fpa):
    _post(fpa, fpa.acc.rent, 1000.0, date(2031, 10, 5))
    _post(fpa, fpa.acc.income, 3000.0, date(2031, 10, 6), branch=fpa.dhk, credit=True)
    _post(fpa, fpa.acc.income, 1000.0, date(2031, 10, 7), branch=fpa.ctg, credit=True)
    pool = _pool(fpa, allocation_basis="revenue")
    cycle = _cycle(fpa, pool)
    cycle.action_compute()
    amounts = {ln.branch_id: _money(ln.amount) for ln in cycle.line_ids}
    assert amounts == {fpa.dhk: D("750.00"), fpa.ctg: D("250.00")}


def test_allocation_fails_closed_without_posting_configuration(fpa):
    _post(fpa, fpa.acc.rent, 1000.0, date(2031, 10, 5))
    pool = _pool(
        fpa, journal_id=False, share_ids=[(0, 0, {"branch_id": fpa.dhk.id, "percent": 100.0})]
    )
    cycle = _cycle(fpa, pool)
    cycle.action_compute()
    with pytest.raises(UserError, match="allocation journal"), fpa.env.cr.savepoint():
        cycle.action_post()
    assert not cycle.move_id


def test_allocation_with_no_pool_cost_is_refused(fpa):
    pool = _pool(fpa, share_ids=[(0, 0, {"branch_id": fpa.dhk.id, "percent": 100.0})])
    with pytest.raises(UserError, match="no posted cost"), fpa.env.cr.savepoint():
        _cycle(fpa, pool).action_compute()


# --------------------------------------------------------------------------- budget versions


def _version(fpa, **vals):
    base = {
        "name": f"FY2032 budget {next(_SEQ)}",
        "fiscal_year": "FY2032",
        "date_from": date(2031, 7, 1),
        "date_to": date(2032, 6, 30),
    }
    base.update(vals)
    return fpa.env["fix.budget.version"].create(base)


def _budget(fpa, version, lines):
    return fpa.env["fix.budget"].create(
        {
            "name": "Dhanmondi opex",
            "version_id": version.id,
            "line_ids": [(0, 0, ln) for ln in lines],
        }
    )


def test_budget_actuals_follow_the_posted_gl_and_dimensions(fpa):
    version = _version(fpa)
    budget = _budget(
        fpa,
        version,
        [
            {
                "account_id": fpa.acc.rent.id,
                "branch_id": fpa.dhk.id,
                "date_from": date(2031, 10, 1),
                "date_to": date(2031, 10, 31),
                "planned_amount": 50000.0,
            },
            {
                "account_id": fpa.acc.income.id,
                "date_from": date(2031, 10, 1),
                "date_to": date(2031, 10, 31),
                "planned_amount": 200000.0,
            },
        ],
    )
    assert budget.fiscal_year == "FY2032" and budget.date_from == date(2031, 7, 1)
    assert _money(budget.planned_amount) == D("250000.00")
    _post(fpa, fpa.acc.rent, 52000.0, date(2031, 10, 3), branch=fpa.dhk)
    _post(fpa, fpa.acc.rent, 9000.0, date(2031, 10, 3), branch=fpa.ctg)  # other branch
    _post(fpa, fpa.acc.income, 210000.0, date(2031, 10, 9), credit=True)
    rent, income = budget.line_ids.sorted(lambda ln: ln.account_id.code, reverse=True)
    assert _money(rent.actual_amount) == D("52000.00")
    assert _money(rent.variance) == D("-2000.00")  # overspend: adverse
    assert _money(income.actual_amount) == D("210000.00")
    assert _money(income.variance) == D("10000.00")  # revenue above budget: favourable
    budget.action_refresh_actuals()
    assert _money(budget.actual_amount) == D("262000.00")
    assert budget.actuals_refreshed_at


def test_refresh_without_lines_is_refused(fpa):
    budget = fpa.env["fix.budget"].create({"name": "Legacy", "fiscal_year": "FY2032"})
    with pytest.raises(UserError, match="no lines"), fpa.env.cr.savepoint():
        budget.action_refresh_actuals()


def _line(fpa, amount=1000.0):
    return {
        "account_id": fpa.acc.rent.id,
        "date_from": date(2031, 7, 1),
        "date_to": date(2031, 7, 31),
        "planned_amount": amount,
    }


def test_version_workflow_enforces_segregation_of_duties(fpa):
    env = fpa.env
    accountant = _user(env, "account.group_account_user")
    manager = _user(env, "account.group_account_manager", "account.group_account_user")
    version = _version(fpa)
    _budget(fpa, version, [_line(fpa)])

    with pytest.raises(UserError, match="no budget lines"), env.cr.savepoint():
        _version(fpa).with_user(accountant).action_submit()

    version.with_user(manager).action_submit()
    assert version.state == "submitted" and version.submitted_by == manager
    assert version.budget_ids.state == "submitted"
    with pytest.raises(UserError, match="Segregation of duties"), env.cr.savepoint():
        version.with_user(manager).action_approve()
    with pytest.raises(AccessError), env.cr.savepoint():
        version.with_user(accountant).action_approve()

    other_manager = _user(env, "account.group_account_manager", "account.group_account_user")
    version.with_user(other_manager).action_approve()
    assert version.state == "approved" and version.approved_by == other_manager
    assert version.budget_ids.state == "approved"


def test_submitted_version_is_locked(fpa):
    version = _version(fpa)
    budget = _budget(fpa, version, [_line(fpa)])
    version.action_submit()
    with pytest.raises(UserError, match="only a draft version"), fpa.env.cr.savepoint():
        budget.line_ids.write({"planned_amount": 1.0})
    with pytest.raises(UserError, match="only a draft version"), fpa.env.cr.savepoint():
        budget.write({"name": "renamed"})
    with pytest.raises(UserError, match="only a draft version"), fpa.env.cr.savepoint():
        version.write({"date_to": date(2032, 5, 31)})
    # measuring actuals stays possible on a locked version
    budget.action_refresh_actuals()


def test_rejection_needs_a_reason_and_returns_to_draft(fpa):
    env = fpa.env
    submitter = _user(env, "account.group_account_user")
    version = _version(fpa)
    _budget(fpa, version, [_line(fpa)])
    version.with_user(submitter).action_submit()
    with pytest.raises(UserError, match="rejection reason"), env.cr.savepoint():
        version.action_reject()
    version.rejection_reason = "Rent assumption too low"
    version.action_reject()
    assert version.state == "rejected"
    version.action_reset_draft()
    assert version.state == "draft" and not version.submitted_by


def test_approving_a_new_budget_supersedes_the_previous_one(fpa):
    env = fpa.env
    submitter = _user(env, "account.group_account_user")
    first, second = _version(fpa), _version(fpa)
    for ver in (first, second):
        _budget(fpa, ver, [_line(fpa)])
        ver.with_user(submitter).action_submit()
        ver.action_approve()
    assert (first.state, second.state) == ("superseded", "approved")


# --------------------------------------------------------------------------- scenarios


def test_scenario_drivers_generate_a_monthly_plan(fpa):
    _post(fpa, fpa.acc.rent, 120000.0, date(2030, 9, 15))  # opex in the base window
    version = _version(
        fpa,
        version_type="scenario",
        date_from=date(2031, 7, 1),
        date_to=date(2031, 9, 30),
        revenue_account_id=fpa.acc.income.id,
        parts_account_id=fpa.acc.direct.id,
        labour_account_id=fpa.acc.utilities.id,
        overhead_account_id=fpa.acc.rent.id,
    )
    version.action_load_drivers()
    drivers = {d.driver_key: d for d in version.driver_ids}
    assert len(drivers) == 6
    assert version.base_date_from == date(2030, 7, 1)
    assert version.base_date_to == date(2031, 6, 30)
    assert _money(drivers["overhead_per_month"].base_value) == D("10000.00")  # 120000 / 12
    drivers["orders_per_month"].scenario_value = 100.0
    drivers["revenue_per_order"].scenario_value = 1500.0
    drivers["parts_cost_pct"].scenario_value = 30.0
    drivers["labour_hours_per_order"].scenario_value = 2.0
    drivers["loaded_labour_rate"].scenario_value = 250.0
    assert drivers["orders_per_month"].scenario_value_set

    version.action_generate_plan()
    plan = version.budget_ids.filtered(lambda b: b.name == "Driver plan")
    assert len(plan.line_ids) == 12  # 3 months x 4 accounts
    july = plan.line_ids.filtered(lambda ln: ln.date_from == date(2031, 7, 1))
    by_acc = {ln.account_id: _money(ln.planned_amount) for ln in july}
    assert by_acc[fpa.acc.income] == D("150000.00")  # 100 x 1500
    assert by_acc[fpa.acc.direct] == D("45000.00")  # 30%
    assert by_acc[fpa.acc.utilities] == D("50000.00")  # 100 x 2h x 250
    assert by_acc[fpa.acc.rent] == D("10000.00")
    assert _money(version.planned_revenue) == D("450000.00")
    assert _money(version.planned_margin) == D("135000.00")  # 3 x (150000-45000-50000-10000)

    # reloading drivers keeps the planner's values
    version.action_load_drivers()
    assert drivers["orders_per_month"].scenario_value == 100.0


def test_plan_generation_fails_closed_without_accounts(fpa):
    version = _version(fpa, version_type="scenario")
    version.action_load_drivers()
    with pytest.raises(UserError, match="revenue"), fpa.env.cr.savepoint():
        version.action_generate_plan()


# --------------------------------------------------------------------------- board pack


def test_board_pack_assembles_a_csv_and_is_issued_by_another_manager(fpa):
    env = fpa.env
    _post(fpa, fpa.acc.income, 80000.0, date(2031, 10, 6), branch=fpa.dhk, credit=True)
    _post(fpa, fpa.acc.rent, 30000.0, date(2031, 10, 7), branch=fpa.dhk)
    assembler = _user(env, "account.group_account_manager", "account.group_account_user")
    pack = env["fix.board.pack"].create(
        {"name": "Oct 2031", "date_from": date(2031, 10, 1), "date_to": date(2031, 10, 31)}
    )
    pack.with_user(assembler).action_assemble()
    assert pack.state == "assembled" and pack.assembled_by == assembler
    metrics = {ln.metric: ln for ln in pack.line_ids}
    assert _money(metrics["Revenue"].amount) == D("80000.00")
    assert _money(metrics["Operating result"].amount) == D("50000.00")
    assert "Dhanmondi" in metrics["Top branch"].detail
    csv_text = base64.b64decode(pack.export_file).decode("utf-8-sig")
    assert csv_text.splitlines()[0] == "Section,Metric,Amount (BDT),Detail"
    assert "Operating result,50000.0" in csv_text
    assert pack.export_filename == "board-pack-2031-10-01-2031-10-31.csv"

    with pytest.raises(UserError, match="Segregation of duties"), env.cr.savepoint():
        pack.with_user(assembler).action_issue()
    issuer = _user(env, "account.group_account_manager", "account.group_account_user")
    pack.with_user(issuer).action_issue()
    assert pack.state == "issued"
    with pytest.raises(UserError, match="frozen"), env.cr.savepoint():
        pack.write({"name": "changed"})


# ------------------------------------------------- report windows are UTC-correct


@pytest.mark.parametrize(
    "tz, expected_start, expected_end",
    [
        # Asia/Dhaka is UTC+06: the local day begins at 18:00 UTC the day before.
        ("Asia/Dhaka", datetime(2026, 10, 30, 18, 0), datetime(2026, 10, 31, 18, 0)),
        # A zone behind UTC shifts the other way (EDT, UTC-04 on this date).
        ("America/New_York", datetime(2026, 10, 31, 4, 0), datetime(2026, 11, 1, 4, 0)),
        # A UTC user is unaffected: midnight to midnight.
        ("UTC", datetime(2026, 10, 31, 0, 0), datetime(2026, 11, 1, 0, 0)),
    ],
)
def test_report_windows_convert_the_users_local_dates_to_utc(
    odoo_env, tz, expected_start, expected_end
):
    """A report window is a span of the USER's calendar days, but `create_date`
    and the work-order stamps it is compared against are stored in UTC.

    Before this was fixed the engine combined the local dates with `time.min`
    and compared the naive result directly, so the first `utcoffset` hours of
    every local day fell outside that day's window: for Asia/Dhaka every record
    created between local 00:00 and 05:59 was counted against the previous day.
    It surfaced as four M54 FP&A report tests that passed by day and failed
    between 00:00 and 06:00 Dhaka time, and it mis-stated every daily figure
    those reports produce.
    """
    env = odoo_env
    env.user.write({"tz": tz})
    # clear any `tz` the test context carries, so the user's setting is what
    # decides here; the context's precedence is asserted separately below
    engine = env["fix.fpa.engine"].with_context(tz=False)

    start, end = engine._dt_bounds(date(2026, 10, 31), date(2026, 10, 31))

    assert start == expected_start
    assert end == expected_end
    # the window is exactly one local day long, and half-open
    assert (end - start).total_seconds() == 24 * 3600


def test_report_windows_follow_the_context_timezone_over_the_user_setting(odoo_env):
    """`tz` in the context wins, matching `_day_start_utc` in the P03 API."""
    env = odoo_env
    env.user.write({"tz": "UTC"})
    engine = env["fix.fpa.engine"].with_context(tz="Asia/Dhaka")

    start, end = engine._dt_bounds(date(2026, 10, 31), date(2026, 10, 31))

    assert start == datetime(2026, 10, 30, 18, 0)
    assert end == datetime(2026, 10, 31, 18, 0)
