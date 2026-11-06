# A08 finish, M54: budgets can be planned and submitted, allocations can run, and
# the Reject button works, from the P03 screens, as non-admin users with real finance
# roles. The `whitelist` fixture applies what the generation of writable.py produces
# from the forms as they stand.
import json
import re
import shutil
import subprocess
import types
from datetime import date
from pathlib import Path

import pytest
from odoo import Command
from odoo.exceptions import UserError

ACC_USER = "account.group_account_user"
ACC_MGR = "account.group_account_manager"
TIER4 = "cd_entity_config.group_dofa_tier_4"
_SEQ = iter(range(1, 100000))
PORTAL = Path(__file__).resolve().parents[3].parent / "platform" / "cd_p03_portal"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')


class Ctx:
    pass


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
def c(odoo_env):
    env = odoo_env
    x = Ctx()
    x.env = env
    x.co = env.company
    bdt = env.ref("base.BDT")
    if x.co.currency_id != bdt:
        x.co.sudo().write({"currency_id": bdt.id})
    x.acct = _user(env, "a08m54op_acct", [ACC_USER])
    x.acct2 = _user(env, "a08m54op_acct2", [ACC_USER])
    x.mgr = _user(env, "a08m54op_mgr", [ACC_MGR, TIER4])
    x.mgr2 = _user(env, "a08m54op_mgr2", [ACC_MGR, TIER4])
    A = env["account.account"]
    acc = lambda code: A.search([("code", "=", code)], limit=1)  # noqa: E731
    x.inc, x.exp, x.cash = acc("400000"), acc("600000"), acc("101401")
    x.absorbed, x.clearing, x.other = acc("610000"), acc("611000"), acc("443000")
    x.misc = env["account.journal"].search(
        [("code", "=", "MISC"), ("company_id", "=", x.co.id)], limit=1
    )
    x.ou = env["operating.unit"].search([], limit=1)
    return x


@pytest.fixture
def whitelist():
    from odoo.addons.cd_p03_portal.controllers import a08, form_fields

    editable = form_fields.editable_by_model()
    saved = {model: conf.get("writable") for model, conf in a08.SURFACES.items()}
    for model, conf in a08.SURFACES.items():
        conf["writable"] = frozenset(editable.get(model, ()))
    try:
        yield
    finally:
        for model, conf in a08.SURFACES.items():
            conf["writable"] = saved[model]


@pytest.fixture
def p03(c, whitelist):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    def orig(name):
        f = getattr(g.P03GenericApiController, name)
        return getattr(f, "original_endpoint", f)

    ctl = g.P03GenericApiController()
    old = (getattr(g, "request", None), getattr(s, "request", None))

    def as_user(user):
        req = types.SimpleNamespace(env=c.env(user=user.id))
        g.request = req
        s.request = req

    try:
        yield types.SimpleNamespace(
            as_user=as_user,
            write=lambda **kw: orig("model_write")(ctl, **kw),
            action=lambda **kw: orig("model_action")(ctl, **kw),
            form=lambda **kw: orig("model_form")(ctl, **kw),
            records=lambda **kw: orig("model_records")(ctl, **kw),
        )
    finally:
        g.request, s.request = old


@pytest.fixture(scope="module")
def screens(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    src = PORTAL / "static" / "src"
    tmp = tmp_path_factory.mktemp("p03_m54_op")
    for area in sorted(d for d in src.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (src / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    probe = tmp / "probe.mjs"
    probe.write_text(
        "import * as M from './meta.mjs';\n"
        "console.log(JSON.stringify({screens: Object.fromEntries(Object.entries(M.P03_DATA_SCREENS)"
        ".filter(([k]) => k.startsWith('M54'))), chips: M.P03_FORM_CHIPS,"
        " nav: M.P03_MODULES.M54.groups.flatMap((g) => g.screens.map((s) => s.id))}));\n",
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=60
    )
    return json.loads(out.stdout)


def _fields(screens, sid):
    return [f for s in screens["screens"][sid]["sections"] for f in s["fields"]]


def je(c, d, amount, debit, credit):
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


def new_version(p03, user, **values):
    p03.as_user(user)
    made = p03.write(
        model="fix.budget.version",
        values={
            "name": "FY27 %d" % next(_SEQ),
            "version_type": "budget",
            "fiscal_year": "FY-OP-%d" % next(_SEQ),
            "date_from": "2026-07-01",
            "date_to": "2027-06-30",
            **values,
        },
    )
    assert "id" in made, made
    return made["id"]


# ============================================================ 10. plan and submit
def test_item10_budget_with_lines_is_planned_submitted_and_approved_on_screen(c, p03, screens):
    assert screens["screens"]["M54-form-budget"]["lines"]["field"] == "line_ids"
    assert "M54-budget-lines" in screens["nav"]
    p03.as_user(c.acct)
    form = p03.form(
        model="fix.budget",
        fields=_fields(screens, "M54-form-budget"),
        lines=screens["screens"]["M54-form-budget"]["lines"],
    )
    assert {"account_id", "date_from", "date_to", "planned_amount"} <= {
        f["name"] for f in form["lines"]["fields"]
    }
    assert next(f for f in form["lines"]["fields"] if f["name"] == "account_id")["choices"]

    ver = c.env["fix.budget.version"].browse(new_version(p03, c.acct))
    res = p03.action(model="fix.budget.version", ids=[ver.id], method="action_submit")
    assert not res["success"] and "no budget lines" in res["error"]
    # the form leaves year and window blank: they come from the version
    made = p03.write(
        model="fix.budget",
        values={"name": "Opex", "budget_type": "operating", "version_id": ver.id},
        lines={
            "field": "line_ids",
            "rows": [
                {
                    "id": None,
                    "values": {
                        "account_id": c.exp.id,
                        "date_from": "2026-09-01",
                        "date_to": "2026-09-30",
                        "planned_amount": 100000.0,
                    },
                },
                {
                    "id": None,
                    "values": {
                        "account_id": c.inc.id,
                        "date_from": "2026-09-01",
                        "date_to": "2026-09-30",
                        "planned_amount": 150000.0,
                    },
                },
            ],
            "removed": [],
        },
    )
    assert "id" in made, made
    budget = c.env["fix.budget"].browse(made["id"])
    assert budget.fiscal_year == ver.fiscal_year and budget.date_to == date(2027, 6, 30)
    assert budget.planned_amount == 250000.0
    assert ver.planned_cost == 100000.0 and ver.planned_revenue == 150000.0
    # a line outside the window is refused and leaves nothing behind
    res = p03.write(
        model="fix.budget",
        record_id=budget.id,
        values={},
        lines={
            "field": "line_ids",
            "rows": [
                {
                    "id": None,
                    "values": {
                        "account_id": c.exp.id,
                        "date_from": "2028-01-01",
                        "date_to": "2028-01-31",
                        "planned_amount": 1.0,
                    },
                }
            ],
            "removed": [],
        },
    )
    assert "error" in res and len(budget.line_ids) == 2
    listed = p03.records(
        model="fix.budget.line", cols=screens["screens"]["M54-budget-lines"]["cols"]
    )
    assert listed["rows"] and set(screens["screens"]["M54-budget-lines"]["cols"]) <= set(
        listed["labels"]
    )

    res = p03.action(model="fix.budget.version", ids=[ver.id], method="action_submit")
    assert res["success"], res
    assert ver.state == "submitted" and ver.approval_state == "pending"
    task_for(c, ver, c.mgr).with_user(c.mgr).action_approve()
    assert ver.state == "approved" and budget.state == "approved"
    # approved: the grid refuses
    res = p03.write(
        model="fix.budget",
        record_id=budget.id,
        values={},
        lines={
            "field": "line_ids",
            "rows": [{"id": budget.line_ids[0].id, "values": {"planned_amount": 9.0}}],
            "removed": [],
        },
    )
    assert "error" in res and budget.planned_amount == 250000.0


def test_item10_scenario_generates_its_plan_from_accounts_and_drivers_on_screen(c, p03, screens):
    cfg = screens["screens"]["M54-form-scenario"]
    assert screens["chips"]["M54:__by_screen__"]["M54-scenario"] == "M54-form-scenario"
    assert cfg["lines"]["field"] == "driver_ids"
    typed = next(f for f in _fields(screens, "M54-form-scenario") if f["name"] == "version_type")
    assert typed["value"] == "scenario"
    p03.as_user(c.acct)
    # the new form posts the declared type: it lands on the scenario grid
    ver = c.env["fix.budget.version"].browse(new_version(p03, c.acct, version_type=typed["value"]))
    listed = p03.records(
        model="fix.budget.version",
        cols=screens["screens"]["M54-scenario"]["cols"],
        domain=screens["screens"]["M54-scenario"]["domain"],
    )
    assert ver.id in [r["id"] for r in listed["rows"]]
    # both refusals name what is missing, and now the screen can supply it
    res = p03.action(model="fix.budget.version", ids=[ver.id], method="action_generate_plan")
    assert not res["success"] and "account(s)" in res["error"]
    res = p03.write(
        model="fix.budget.version",
        record_id=ver.id,
        values={
            "revenue_account_id": c.inc.id,
            "parts_account_id": c.exp.id,
            "labour_account_id": c.absorbed.id,
            "overhead_account_id": c.clearing.id,
        },
    )
    assert "id" in res, res
    res = p03.action(model="fix.budget.version", ids=[ver.id], method="action_generate_plan")
    assert not res["success"] and "load the drivers" in res["error"]
    res = p03.action(model="fix.budget.version", ids=[ver.id], method="action_load_drivers")
    assert res["success"], res
    assert len(ver.driver_ids) == 6
    form = p03.form(
        model="fix.budget.version",
        fields=_fields(screens, "M54-form-scenario"),
        record_id=ver.id,
        lines=cfg["lines"],
    )
    assert {r["driver_key"] for r in form["lines"]["rows"]} == set(
        ver.driver_ids.mapped("driver_key")
    )

    # the grid posts each row whole, the measured base value with it
    def row(drv, value, base=None):
        return {
            "id": drv.id,
            "values": {
                "driver_key": drv.driver_key,
                "base_value": drv.base_value if base is None else base,
                "scenario_value": value,
            },
        }

    by_key = {d.driver_key: d for d in ver.driver_ids}
    res = p03.write(
        model="fix.budget.version",
        record_id=ver.id,
        values={},
        lines={
            "field": "driver_ids",
            "removed": [],
            "rows": [
                row(by_key["orders_per_month"], 100.0),
                row(by_key["revenue_per_order"], 2000.0),
                row(by_key["parts_cost_pct"], 25.0),
                row(by_key["labour_hours_per_order"], 2.0),
                row(by_key["loaded_labour_rate"], 300.0),
                row(by_key["overhead_per_month"], 50000.0),
            ],
        },
    )
    assert "id" in res, res
    assert by_key["orders_per_month"].scenario_value == 100.0
    # a typed base value is refused
    res = p03.write(
        model="fix.budget.version",
        record_id=ver.id,
        values={},
        lines={
            "field": "driver_ids",
            "removed": [],
            "rows": [row(by_key["orders_per_month"], 100.0, base=999.0)],
        },
    )
    assert "error" in res and by_key["orders_per_month"].base_value != 999.0

    res = p03.action(model="fix.budget.version", ids=[ver.id], method="action_generate_plan")
    assert res["success"], res
    assert ver.planned_revenue == 12 * 200000.0
    assert ver.planned_cost == 12 * (50000.0 + 60000.0 + 50000.0)
    res = p03.action(model="fix.budget.version", ids=[ver.id], method="action_submit")
    assert res["success"], res
    assert ver.state == "submitted"


def test_item10_workflow_screen_offers_the_driver_actions(screens):
    from odoo.addons.cd_p03_portal.controllers.a08 import m54

    acts = {a["m"] for a in screens["screens"]["M54-workflow"]["actions"]}
    assert {"action_load_drivers", "action_generate_plan"} <= acts
    assert acts <= m54.SURFACES["fix.budget.version"]["actions"]


# ============================================================ 11. allocation
def test_item11_allocation_runs_from_the_screens(c, p03, screens):
    pool_cfg = screens["screens"]["M54-form-pool"]
    assert pool_cfg["lines"]["field"] == "share_ids"
    assert "journal_id" in {f["name"] for f in _fields(screens, "M54-form-pool")}
    assert "M54-elements" in screens["nav"]
    n = next(_SEQ)
    ent = c.env["fix.entity"].create(
        {"code": "OPFPA%d" % n, "legal_name": "Op FPA", "company_id": c.co.id}
    )
    b1 = c.env["fix.branch"].create(
        {
            "code": "OB1%d" % n,
            "name": "Dhanmondi",
            "entity_id": ent.id,
            "operating_unit_id": c.ou.id,
        }
    )
    b2 = c.env["fix.branch"].create(
        {"code": "OB2%d" % n, "name": "Uttara", "entity_id": ent.id, "operating_unit_id": c.ou.id}
    )

    # the pool's owner: Accounting Administrator
    p03.as_user(c.mgr)
    made = p03.write(
        model="fix.cost.pool",
        values={
            "code": "OPP%d" % n,
            "name": "Head-office rent",
            "pool_type": "overhead",
            "receiver_type": "branch",
            "allocation_basis": "fixed",
            "target_account_id": c.absorbed.id,
            "clearing_account_id": c.clearing.id,
            "journal_id": c.misc.id,
        },
        lines={
            "field": "share_ids",
            "removed": [],
            "rows": [
                {"id": None, "values": {"branch_id": b1.id, "percent": 60.0}},
                {"id": None, "values": {"branch_id": b2.id, "percent": 40.0}},
            ],
        },
    )
    assert "id" in made, made
    pool = c.env["fix.cost.pool"].browse(made["id"])
    assert pool.journal_id == c.misc and sorted(pool.share_ids.mapped("percent")) == [40.0, 60.0]

    # no element yet: Compute refuses, and says so
    je(c, date(2026, 9, 3), 10000.0, c.exp, c.cash)
    p03.as_user(c.acct)
    alloc = p03.write(
        model="fix.cost.allocation",
        values={
            "name": "Rent Sep %d" % n,
            "pool_id": pool.id,
            "date_from": "2026-09-01",
            "date_to": "2026-09-30",
        },
    )
    assert "id" in alloc, alloc
    cycle = c.env["fix.cost.allocation"].browse(alloc["id"])
    res = p03.action(model="fix.cost.allocation", ids=[cycle.id], method="action_compute")
    assert not res["success"] and "gathered no posted cost" in res["error"]

    # the element form: an accountant cannot, the administrator can, the GL accounts
    # arriving as the multi-select posts them (a bare list of ids)
    element_values = {
        "pool_id": pool.id,
        "code": "RENT",
        "name": "Rent",
        "element_type": "primary",
        "account_ids": c.exp.ids,
    }
    assert "error" in p03.write(model="fix.cost.element", values=element_values)
    p03.as_user(c.mgr)
    form = p03.form(model="fix.cost.element", fields=_fields(screens, "M54-form-element"))
    accounts = next(f for f in form["fields"] if f["name"] == "account_ids")
    assert accounts["type"] == "many2many" and not accounts["readonly"] and accounts["choices"]
    made = p03.write(model="fix.cost.element", values=element_values)
    assert "id" in made, made
    assert pool.element_ids.account_ids == c.exp and pool.element_count == 1

    p03.as_user(c.acct)
    res = p03.action(model="fix.cost.allocation", ids=[cycle.id], method="action_compute")
    assert res["success"], res
    assert cycle.state == "computed" and sorted(cycle.line_ids.mapped("amount")) == [4000.0, 6000.0]
    # the computer does not post; another accountant does, and the journal is the pool's
    assert not p03.action(model="fix.cost.allocation", ids=[cycle.id], method="action_post")[
        "success"
    ]
    p03.as_user(c.acct2)
    res = p03.action(model="fix.cost.allocation", ids=[cycle.id], method="action_post")
    assert res["success"], res
    assert cycle.state == "posted" and cycle.move_id.journal_id == c.misc
    assert cycle.move_id.state == "posted" and cycle.move_id.amount_total == 10000.0


def test_item11_post_says_when_the_pool_has_no_journal(c, p03):
    """The refusal the pool form's new field answers."""
    n = next(_SEQ)
    ent = c.env["fix.entity"].create(
        {"code": "OPFJ%d" % n, "legal_name": "Op", "company_id": c.co.id}
    )
    b1 = c.env["fix.branch"].create(
        {"code": "OJ1%d" % n, "name": "A", "entity_id": ent.id, "operating_unit_id": c.ou.id}
    )
    pool = c.env["fix.cost.pool"].create(
        {
            "code": "OPJ%d" % n,
            "name": "No journal",
            "receiver_type": "branch",
            "allocation_basis": "fixed",
            "target_account_id": c.absorbed.id,
            "clearing_account_id": c.clearing.id,
            "element_ids": [
                Command.create({"code": "E", "name": "E", "account_ids": [(6, 0, c.other.ids)]})
            ],
            "share_ids": [Command.create({"branch_id": b1.id, "percent": 100.0})],
        }
    )
    je(c, date(2026, 9, 3), 500.0, c.other, c.cash)
    cycle = (
        c.env["fix.cost.allocation"]
        .with_user(c.acct)
        .create(
            {
                "name": "x",
                "pool_id": pool.id,
                "date_from": date(2026, 9, 1),
                "date_to": date(2026, 9, 30),
            }
        )
    )
    cycle.with_user(c.acct).action_compute()
    with pytest.raises(UserError, match="allocation journal"):
        cycle.with_user(c.acct2).action_post()
    p03.as_user(c.mgr)
    res = p03.write(model="fix.cost.pool", record_id=pool.id, values={"journal_id": c.misc.id})
    assert "id" in res, res
    cycle.with_user(c.acct2).action_post()
    assert cycle.state == "posted"


# ============================================================ 12. reject
def test_item12_reject_works_from_the_workflow_button(c, p03, screens):
    act = next(
        a for a in screens["screens"]["M54-workflow"]["actions"] if a["m"] == "action_reject"
    )
    assert act["ask"] and act["kwarg"] == "reason"
    ver = (
        c.env["fix.budget.version"]
        .with_user(c.acct)
        .create(
            {
                "name": "R %d" % next(_SEQ),
                "fiscal_year": "FY-R-%d" % next(_SEQ),
                "date_from": date(2026, 7, 1),
                "date_to": date(2027, 6, 30),
            }
        )
    )
    c.env["fix.budget"].with_user(c.acct).create(
        {
            "name": "Opex",
            "version_id": ver.id,
            "line_ids": [
                Command.create(
                    {
                        "account_id": c.exp.id,
                        "date_from": date(2026, 9, 1),
                        "date_to": date(2026, 9, 30),
                        "planned_amount": 5.0,
                    }
                )
            ],
        }
    )
    ver.with_user(c.acct).action_submit()
    p03.as_user(c.mgr)
    res = p03.action(
        model="fix.budget.version", ids=[ver.id], method="action_reject", kwargs={"reason": "  "}
    )
    assert not res["success"] and "reason" in res["error"] and ver.state == "submitted"
    # the preparer does not reject, whatever he types
    p03.as_user(c.acct)
    res = p03.action(
        model="fix.budget.version", ids=[ver.id], method=act["m"], kwargs={act["kwarg"]: "no"}
    )
    assert not res["success"] and ver.state == "submitted" and not ver.rejection_reason
    p03.as_user(c.mgr)
    res = p03.action(
        model="fix.budget.version",
        ids=[ver.id],
        method=act["m"],
        kwargs={act["kwarg"]: "Rent line unsupported"},
    )
    assert res["success"], res
    assert (
        ver.state == "rejected"
        and ver.rejection_reason == "Rent line unsupported"
        and ver.approval_state == "none"
    )
    # the reason is on the form, read-only; and the preparer can start again
    form = p03.form(
        model="fix.budget.version", fields=_fields(screens, "M54-form-version"), record_id=ver.id
    )
    assert form["record"]["rejection_reason"] == "Rent line unsupported"
    assert next(f for f in form["fields"] if f["name"] == "rejection_reason")["readonly"]
    p03.as_user(c.acct)
    assert p03.action(model="fix.budget.version", ids=[ver.id], method="action_reset_draft")[
        "success"
    ]
    assert ver.state == "draft"
