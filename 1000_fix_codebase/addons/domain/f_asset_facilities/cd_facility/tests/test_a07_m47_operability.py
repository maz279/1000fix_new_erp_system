"""A07 M47 operability: can a person do the facility job on the P03 workspace?

The A07 build was proved by calling model methods directly, and no screen was
ever driven. Every test here walks the path the workspace walks, through the
generic endpoints (model_records, model_form, model_write, model_action,
model_report), as a NON-ADMIN user holding the role they would really hold. The
buttons and forms are read from static/src/a07/m47.js by evaluating it with node.
Events reach the bridge through the registered subscription, the way the relay
delivers them.
"""

from __future__ import annotations

import base64
import json
import shutil
import subprocess
import types
from datetime import timedelta
from pathlib import Path

import odoo.addons.cd_p03_portal as portal
import odoo.addons.cd_p03_portal.controllers.p03_generic_api as api
import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers.form_fields import editable_by_model
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

REFUSED = (UserError, ValidationError, AccessError)
FM = "cd_facility.group_facility_manager"
BOL = "cd_facility.group_branch_operations_lead"
OPSDIR = "cd_facility.group_operations_director"
TIER = "cd_entity_config.group_dofa_tier_%d"
ACCOUNTANT = "account.group_account_user"
HSE = "cd_hse.group_hse_officer"
BRIDGE = "cd_asset_finance_hse_bridge"
SCAN = base64.b64encode(b"%PDF-1.4 licence scan").decode()
SRC = Path(portal.__file__).parent / "static" / "src"
WO = "fix.facility.work.order"


def _user(env, login, company, ou, *groups, employee=False):
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, ids)],
                "company_ids": [(6, 0, company.ids)],
                "company_id": company.id,
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )
    if employee:
        env["hr.employee"].create({"name": login, "user_id": user.id, "company_id": company.id})
    return user


@pytest.fixture(scope="module")
def js(tmp_path_factory):
    node = shutil.which("node")
    assert node, "node evaluates the registry: without it these tests prove nothing"
    tmp = tmp_path_factory.mktemp("m47js")
    out = {}
    for area, name in (("a07", "m47"), ("a08", "m49"), ("a09", "m59"), ("a10", "m60")):
        (tmp / f"{name}.mjs").write_text(
            (SRC / area / f"{name}.js").read_text(encoding="utf-8"), "utf-8"
        )
        (tmp / f"run_{name}.mjs").write_text(
            f"import * as M from './{name}.mjs';\n"
            "console.log(JSON.stringify({module: M.MODULE, screens: M.SCREENS,"
            " chips: M.FORM_CHIPS}));\n",
            "utf-8",
        )
        done = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our probe file
            [node, str(tmp / f"run_{name}.mjs")],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
            timeout=60,
        )
        out[name] = json.loads(done.stdout)
    return out


def button(js, screen, method):
    found = [a for a in js["m47"]["screens"][screen].get("actions", []) if a["m"] == method]
    assert len(found) == 1, f"{screen}: {method} has {len(found)} buttons"
    return found[0]


def form_fields(js, screen, area="m47"):
    cfg = js[area]["screens"][screen]
    tabs = {t["id"] for t in cfg.get("tabs", [])}
    out = {}
    for section in cfg["sections"]:
        if tabs:
            assert section.get("tab") in tabs, f"{screen}: a section in no tab renders invisible"
        for field in section["fields"]:
            out[field["name"]] = field
    return out


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.today = fields.Date.context_today(env["fix.site"])
    x.co = env["res.company"].create({"name": "A07 M47 Operability Co"})
    x.co_b = env["res.company"].create({"name": "A07 M47 Operability Co B"})
    make_ou = lambda name, code, co: env["operating.unit"].create(  # noqa: E731
        {"name": name, "code": code, "company_id": co.id, "partner_id": co.partner_id.id}
    )
    x.ou = make_ou("A07 M47 OU1", "A7M47O1", x.co)
    x.ou2 = make_ou("A07 M47 OU2", "A7M47O2", x.co)
    x.ou_b = make_ou("A07 M47 OUB", "A7M47OB", x.co_b)
    x.clerk = _user(env, "a7m47_clerk", x.co, x.ou)
    x.fm = _user(env, "a7m47_fm", x.co, x.ou, FM)
    x.fm2 = _user(env, "a7m47_fm2", x.co, x.ou, FM)
    x.fm_ou2 = _user(env, "a7m47_fm_ou2", x.co, x.ou2, FM)
    x.fm_b = _user(env, "a7m47_fm_b", x.co_b, x.ou_b, FM)
    x.bol = _user(env, "a7m47_bol", x.co, x.ou, BOL)
    x.bol2 = _user(env, "a7m47_bol2", x.co, x.ou, BOL)
    x.od = _user(env, "a7m47_od", x.co, x.ou, OPSDIR)
    x.cfo = _user(env, "a7m47_cfo", x.co, x.ou, TIER % 4)
    x.ceo = _user(env, "a7m47_ceo", x.co, x.ou, TIER % 5)
    x.acct = _user(env, "a7m47_acct", x.co, x.ou, ACCOUNTANT)
    x.hse = _user(env, "a7m47_hse", x.co, x.ou, HSE)
    x.site = env["fix.site"].create(
        {"name": "A7M47 Branch", "company_id": x.co.id, "operating_unit_id": x.ou.id}
    )
    x.site.sudo().write({"state": "active"})
    x.landlord = env["res.partner"].create({"name": "A7M47 Landlord"})
    x.vendor = env["res.partner"].create({"name": "A7M47 Vendor"})
    # A07 ERP audit (2026-11-20, D3): a cost entry posts on its cost type's
    # account role and is refused (fail closed) while the role is unset. The
    # test company's chart holds the accounts the seed maps on fix_real.
    icp = env["ir.config_parameter"].sudo()
    for key, code, name, kind in (
        ("facility_work_order", "A7M4701", "Repair & Maintenance Expense", "expense"),
        ("site_utility", "A7M4702", "Utilities Expense", "expense"),
        ("lease_rent", "A7M4703", "Office Rent", "expense"),
    ):
        env["account.account"].create(
            {"code": code, "name": name, "account_type": kind, "company_ids": [(6, 0, x.co.ids)]}
        )
        icp.set_param("%s.account.%s" % (BRIDGE, key), code)
    return x


@pytest.fixture
def ui(c, monkeypatch):
    cls = api.P03GenericApiController
    ctl = cls()
    generated = editable_by_model()
    for model, conf in api.SURFACES.items():
        if model in generated:
            monkeypatch.setitem(conf, "writable", frozenset(generated[model]))

    def call(name, user, **kw):
        ctx = dict(c.env.context, allowed_company_ids=user.company_ids.ids)
        monkeypatch.setattr(
            api, "request", types.SimpleNamespace(env=c.env(user=user.id, context=ctx))
        )
        fn = getattr(cls, name)
        return getattr(fn, "original_endpoint", fn)(ctl, **kw)

    def ok(user, model, rec, method, **kwargs):
        res = call(
            "model_action", user, model=model, ids=rec.ids, method=method, kwargs=kwargs or None
        )
        assert res.get("success"), res
        return res

    def no(user, model, rec, method, match=None, **kwargs):
        res = call(
            "model_action", user, model=model, ids=rec.ids, method=method, kwargs=kwargs or None
        )
        assert res.get("success") is False, res
        if match:
            assert match.lower() in res["error"].lower(), res["error"]
        return res

    return types.SimpleNamespace(
        records=lambda user, **kw: call("model_records", user, **kw),
        form=lambda user, **kw: call("model_form", user, **kw),
        write=lambda user, **kw: call("model_write", user, **kw),
        action=lambda user, **kw: call("model_action", user, **kw),
        report=lambda user, **kw: call("model_report", user, **kw),
        ok=ok,
        no=no,
    )


def _deliver(c, xmlid, event_type, record):
    """Hand the record's events to the registered subscription, as cron_relay does."""
    sub = c.env.ref(f"{BRIDGE}.{xmlid}")
    Outbox = c.env["fix.event.outbox"]
    rows = Outbox.search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", record._name),
            ("aggregate_id", "=", record.id),
        ],
        order="id",
    )
    assert rows, f"no {event_type} event for {record.display_name}"
    for row in rows:
        error = Outbox._relay_deliver(sub, row)
        assert error == "", error
    return rows


def _events(c, event_type, record):
    rows = c.env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", record._name),
            ("aggregate_id", "=", record.id),
        ],
        order="id",
    )
    return [json.loads(r.payload) for r in rows]


def _licence(c, ltype="trade", valid_to=None, site=None):
    """A licence loaded by data import: no scan, as the live register holds them."""
    return c.env["fix.site.licence"].create(
        {
            "site_id": (site or c.site).id,
            "licence_type": ltype,
            "number": "L-%s" % ltype,
            "valid_to": valid_to or c.today + timedelta(days=300),
        }
    )


def _lapsed_exception(c, site=None):
    lic = _licence(c, valid_to=c.today - timedelta(days=3), site=site)
    return c.env["fix.site.risk.exception"].search([("licence_id", "=", lic.id)])


def _lease(c, site=None, **vals):
    return c.env["fix.site.lease"].create(
        {
            "site_id": (site or c.site).id,
            "lessor_id": c.landlord.id,
            "start_date": c.today - timedelta(days=30),
            "end_date": c.today + timedelta(days=720),
            "monthly_rent": 50000.0,
            "deposit": 600000.0,
            **vals,
        }
    )


def _wo(c, site=None, **vals):
    return c.env[WO].create(
        {
            "site_id": (site or c.site).id,
            "company_id": c.co.id,
            "operating_unit_id": c.ou.id,
            "description": "Repair",
            **vals,
        }
    )


def _bill(c, vendor, gross, ref="INV-M47"):
    product = c.env["product.product"].create({"name": "A7M47 Service"})
    return c.env["fix.vendor.invoice"].create(
        {
            "company_id": c.co.id,
            "operating_unit_id": c.ou.id,
            "vendor_id": vendor.id,
            "invoice_ref": ref,
            "bill_type": "non_po",
            "line_ids": [
                (0, 0, {"product_id": product.id, "description": "service", "unit_price": gross})
            ],
        }
    )


# ===================================================== 2: the CEO's decision
def test_2_ceo_with_no_m47_role_decides_continue_from_the_button(c, ui, js):
    exc = _lapsed_exception(c)
    assert exc.state == "open"
    cfg = button(js, "M47-risk", "action_decide_continue")
    assert {a["kwarg"] for a in cfg["asks"]} == {"review_due_on", "notes"}, cfg
    review = str(c.today + timedelta(days=14))
    # no basis, no decision
    ui.no(
        c.ceo,
        exc._name,
        exc,
        "action_decide_continue",
        match="basis",
        review_due_on=review,
        notes="",
    )
    # the form field is not hers to write, and the button does not need it
    assert "error" in ui.write(
        c.ceo, model=exc._name, record_id=exc.id, values={"decision_notes": "x"}
    )
    ui.ok(
        c.ceo,
        exc._name,
        exc,
        "action_decide_continue",
        review_due_on=review,
        notes="Fire service inspection booked; interim fire watch posted",
    )
    assert exc.state == "continue" and exc.decided_by_id == c.ceo
    assert "fire watch" in exc.decision_notes and str(exc.review_due_on) == review


# ===================================================== 3: the bridge queues
def _cost_entry(c, cost=5000.0):
    order = _wo(c, assigned_type="vendor", vendor_id=c.vendor.id, invoice_ref="INV-77")
    publish(
        c.env,
        "facility.work_order_closed",
        WO,
        order.id,
        {
            "order": order.name,
            "site": c.site.name,
            "site_id": c.site.id,
            "company_id": c.co.id,
            "work_type": "repair",
            "assigned_type": "vendor",
            "vendor_id": c.vendor.id,
            "vendor": c.vendor.name,
            "cost": cost,
            "estimated_cost": cost,
            "currency": "BDT",
            "invoice_ref": "INV-77",
            "verified_by": "x",
            "completed_at": None,
            "verified_at": None,
        },
    )
    _deliver(c, "consumer_facility_work_order_closed", "facility.work_order_closed", order)
    return c.env["fix.asset.cost.entry"].search([("source_res_id", "=", order.id)])


def test_3_every_handoff_queue_has_a_screen_a_form_and_no_new_button(js):
    screens = js["m47"]["screens"]
    group = next(g for g in js["m47"]["module"]["groups"] if "Hand-offs" in g["en"])
    wanted = {
        "fix.asset.cost.entry",
        "fix.bridge.exception",
        "fix.lease.modification.item",
        "fix.asset.finance.request",
        # A07 ERP audit FIN-07: the remeasurement a modification item needs
        "fix.lease.remeasurement",
    }
    seen = set()
    by_screen = js["m47"]["chips"]["M47:__by_screen__"]
    for item in group["screens"]:
        cfg = screens[item["id"]]
        seen.add(cfg["model"])
        assert cfg["create"] is False, item["id"]
        assert item.get("bn"), item["id"]
        assert screens[by_screen[item["id"]]]["model"] == cfg["model"]
    assert seen == wanted


def test_3_cost_entry_is_matched_and_rejected_by_the_accountant(c, ui):
    entry = _cost_entry(c)
    assert entry.state == "pending"
    # a clerk and a facility manager do not decide it
    ui.no(c.clerk, entry._name, entry, "action_reject", reason="no")
    ui.no(c.fm, entry._name, entry, "action_match_bill")
    bill = _bill(c, c.vendor, 5000.0, ref="INV-77")
    # the accountant finds it, chooses the bill on the form, and matches it
    rows = ui.records(c.acct, model=entry._name, cols=["name", "state"])["rows"]
    assert entry.id in [r["id"] for r in rows]
    ui.no(c.acct, entry._name, entry, "action_match_bill", match="choose the vendor bill")
    res = ui.write(
        c.acct, model=entry._name, record_id=entry.id, values={"match_invoice_id": bill.id}
    )
    assert "error" not in res, res
    ui.ok(c.acct, entry._name, entry, "action_match_bill")
    assert entry.state == "matched" and entry.vendor_invoice_id == bill
    assert entry.decided_by_id == c.acct
    # the figures stay the source's
    res = ui.write(c.acct, model=entry._name, record_id=entry.id, values={"amount": 1.0})
    assert "error" in res
    other = _cost_entry(c, 900.0)
    ui.no(c.acct, other._name, other, "action_reject", match="why")
    ui.ok(c.acct, other._name, other, "action_reject", reason="Duplicate of a bill already paid")
    assert other.state == "rejected" and "Duplicate" in other.decision_note


def test_3_injury_by_a_user_with_no_employee_is_resolved_on_the_screen(c, ui):
    res = ui.write(
        c.clerk,
        model="fix.site.incident",
        record_id=False,
        values={
            "site_id": c.site.id,
            "incident_type": "injury",
            "severity": "medium",
            "occurred_on": str(c.today),
            "description": "Fell from a ladder",
        },
    )
    assert "error" not in res, res
    incident = c.env["fix.site.incident"].browse(res["id"])
    _deliver(c, "consumer_site_incident", "site.incident", incident)
    key = "m59:fix.site.incident:%s" % incident.id
    Exc = c.env["fix.bridge.exception"]
    row = Exc.search([("key", "=", key)])
    assert row.state == "open" and row.route == "m59_case"
    assert not incident.hse_case_ref
    # the HSE officer finds it on the screen and sees what is needed, in words
    listed = ui.records(c.hse, model=row._name, cols=["name", "route", "message", "state"])["rows"]
    assert row.id in [r["id"] for r in listed]
    form = ui.form(
        c.hse,
        model=row._name,
        record_id=row.id,
        fields=[
            {"name": "message"},
            {"name": "role_label"},
            {"name": "employee_id"},
            {"name": "event_type"},
        ],
    )
    assert "error" not in form, form
    assert "Worker Involved" in form["record"]["message"]
    assert form["record"]["role_label"] == c.env.ref(HSE).name
    # Retry without the fact: still open, nothing invented
    ui.ok(c.hse, row._name, row, "action_retry")
    assert row.state == "open" and not incident.hse_case_ref
    # a plain user neither names nor retries
    ui.no(c.clerk, row._name, row, "action_retry")
    worker = c.env["hr.employee"].create({"name": "A7M47 Worker", "company_id": c.co.id})
    assert "error" in ui.write(
        c.clerk, model=row._name, record_id=row.id, values={"employee_id": worker.id}
    )
    res = ui.write(c.hse, model=row._name, record_id=row.id, values={"employee_id": worker.id})
    assert "error" not in res, res
    form = ui.form(c.hse, model=row._name, record_id=row.id, fields=[{"name": "employee_id"}])
    assert form["record"]["employee_id"]["id"] == worker.id
    ui.ok(c.hse, row._name, row, "action_retry")
    assert row.state == "resolved"
    case = c.env["fix.hse.incident"].search([("bridge_source_key", "=", key)])
    assert len(case) == 1 and case.employee_id == worker and incident.hse_case_ref == case.name


def test_3_bridge_exception_resolved_by_hand_needs_a_note(c, ui):
    site_lease = _lease(c, monthly_rent=0.0)
    _deliver(c, "consumer_lease_recorded", "lease.recorded", site_lease)
    row = c.env["fix.bridge.exception"].search([("key", "=", "m49_lease:%s" % site_lease.id)])
    assert row.state == "open"
    ui.no(c.hse, row._name, row, "action_resolve", note="done")
    ui.no(c.acct, row._name, row, "action_resolve", match="say how", note="  ")
    ui.ok(c.acct, row._name, row, "action_resolve", note="Keyed in M49 by hand")
    assert row.state == "resolved" and row.resolved_by_id == c.acct


def _commence(c, contract):
    """Finance completes the drafted IFRS 16 contract and commences it."""
    env = c.env

    def acc(code, name, kind):
        return env["account.account"].create(
            {"code": code, "name": name, "account_type": kind, "company_ids": [(6, 0, c.co.ids)]}
        )

    journal = env["account.journal"].create(
        {"name": "A7M47 FA", "code": "A7FA", "type": "general", "company_id": c.co.id}
    )
    category = env["fix.asset.category"].create(
        {
            "company_id": c.co.id,
            "code": "A7ROU",
            "name": "A7M47 Right of Use",
            "journal_id": journal.id,
            "asset_account_id": acc("A7M4710", "Right of use Asset", "asset_fixed").id,
            "accumulated_account_id": acc("A7M4711", "Acc. Dep. ROU", "asset_fixed").id,
            "expense_account_id": acc("A7M4712", "Dep. ROU", "expense_depreciation").id,
        }
    )
    contract.write(
        {
            "ibr_percent": 12.0,
            "category_id": category.id,
            "liability_account_id": acc("A7M4713", "Lease Liability", "liability_non_current").id,
            "interest_account_id": acc("A7M4714", "Lease Interest", "expense").id,
            "payment_account_id": acc("A7M4715", "Rent Clearing", "liability_current").id,
        }
    )
    contract.with_company(c.co).action_activate()
    assert contract.state == "active"
    return contract


def test_3_lease_modification_item_is_decided_by_finance(c, ui):
    site_lease = _lease(c)
    _deliver(c, "consumer_lease_recorded", "lease.recorded", site_lease)
    contract = c.env["fix.lease"].search([("site_lease_id", "=", site_lease.id)])
    assert contract
    Item = c.env["fix.lease.modification.item"]
    revised = {
        "commencement": str(site_lease.start_date),
        "end_date": str(site_lease.end_date),
        "monthly_rent": 55000.0,
        "escalation_pct": 0.0,
        "effective_date": str(c.today),
    }
    one = Item._bridge_raise(contract, site_lease, 7, {"reason": "modified", "extract": revised})
    two = Item._bridge_raise(contract, site_lease, 8, {"reason": "modified", "extract": {}})
    ui.no(c.fm, one._name, one, "action_mark_remeasured", note="x")
    # FIN-07: "remeasured" is never a tick; a POSTED remeasurement of this
    # version comes first (prepared by one accountant, posted by another)
    ui.no(
        c.acct,
        one._name,
        one,
        "action_mark_remeasured",
        match="post the remeasurement",
        note="Remeasured in June",
    )
    _commence(c, contract)
    # the months before the modification are on the book first
    month = c.today.replace(day=1)
    for line in contract.schedule_line_ids.sorted("sequence"):
        if line.period_start < month:
            line.with_company(c.co).action_post()
    rem = one.with_user(c.acct).action_new_remeasurement()
    assert rem.state == "draft" and rem.payment_amount == 55000.0
    assert one.remeasurement_id == rem
    acct2 = _user(c.env, "a7m47_acct2", c.co, c.ou, ACCOUNTANT)
    with pytest.raises(UserError, match="Segregation"), c.env.cr.savepoint():
        rem.with_user(c.acct).action_post()
    rem.with_user(acct2).action_post()
    assert rem.state == "posted" and contract.payment_amount == 55000.0
    ui.no(c.acct, one._name, one, "action_mark_remeasured", match="decision note", note=" ")
    ui.ok(c.acct, one._name, one, "action_mark_remeasured", note="Remeasured in June")
    assert one.state == "remeasured" and one.decided_by_id == c.acct
    res = ui.write(
        c.acct, model=two._name, record_id=two.id, values={"decision_note": "Notice only"}
    )
    assert "error" not in res, res
    ui.ok(c.acct, two._name, two, "action_mark_no_change")
    assert two.state == "no_change" and two.decision_note == "Notice only"


def test_3_asset_finance_request_is_decided_by_finance(c, ui):
    asset = c.env["fix.site.asset"].create(
        {"site_id": c.site.id, "asset_type": "generator", "value": 1000.0}
    )
    req = c.env["fix.asset.finance.request"].search(
        [("source_model", "=", "fix.site.asset"), ("source_res_id", "=", asset.id)]
    )
    assert req.kind == "capitalise"
    ui.no(c.fm, req._name, req, "action_accept")
    # accepting names what it needs: the form supplies the category
    ui.no(c.acct, req._name, req, "action_accept", match="category")
    category = c.env["fix.asset.category"].create(
        {"name": "A7M47 Plant", "code": "A7PL", "company_id": c.co.id}
    )
    res = ui.write(c.acct, model=req._name, record_id=req.id, values={"category_id": category.id})
    assert "error" not in res, res
    ui.no(c.acct, req._name, req, "action_accept", match="journal item")
    ui.no(c.acct, req._name, req, "action_reject", match="why")
    ui.ok(c.acct, req._name, req, "action_reject", reason="Below the capitalisation policy")
    assert req.state == "rejected" and req.decided_by_id == c.acct
    assert "error" in ui.write(c.acct, model=req._name, record_id=req.id, values={"amount": 2.0})


# ===================================================== cols are real columns
def test_every_list_column_and_form_field_exists_on_its_model(c, js):
    bad = []
    for sid, cfg in js["m47"]["screens"].items():
        if cfg.get("kind") == "model_list":
            model = c.env[cfg["model"]]
            bad += [(sid, n) for n in cfg["cols"] if n not in model._fields]
            actions = api.SURFACES[cfg["model"]]["actions"]
            for action in cfg.get("actions", []):
                assert action["m"] in actions, (sid, action["m"])
                assert callable(getattr(model, action["m"], None)), (sid, action["m"])
        elif cfg.get("kind") == "model_form":
            model = c.env[cfg["model"]]
            bad += [(sid, n) for n in form_fields(js, sid) if n not in model._fields]
    assert not bad


# ===================================================== 4: who reads what
RULED = (
    "fix.site",
    WO,
    "fix.site.lease",
    "fix.site.lease.schedule",
    "fix.site.lease.extract",
    "fix.site.licence",
    "fix.site.utility",
    "fix.site.condition",
    "fix.site.pm",
    "fix.site.safety",
    "fix.site.incident",
    "fix.site.project",
    "fix.site.asset",
    "fix.site.risk.exception",
)


def _estate(c):
    """One record of every model at the OU-1 site."""
    lease = _lease(c)
    exc = _lapsed_exception(c)
    return {
        "fix.site": c.site,
        WO: _wo(c),
        "fix.site.lease": lease,
        "fix.site.lease.schedule": lease.schedule_ids[:1],
        "fix.site.lease.extract": lease.extract_ids[:1],
        "fix.site.licence": exc.licence_id,
        "fix.site.utility": c.env["fix.site.utility"].create(
            {"site_id": c.site.id, "period": "2026-01", "amount": 900.0}
        ),
        "fix.site.condition": c.env["fix.site.condition"].create({"site_id": c.site.id}),
        "fix.site.pm": c.env["fix.site.pm"].create({"site_id": c.site.id}),
        "fix.site.safety": c.env["fix.site.safety"].create(
            {"site_id": c.site.id, "next_check": c.today + timedelta(days=90)}
        ),
        "fix.site.incident": c.env["fix.site.incident"].create(
            {"site_id": c.site.id, "description": "Window broken"}
        ),
        "fix.site.project": c.env["fix.site.project"].create({"site_id": c.site.id}),
        "fix.site.asset": c.env["fix.site.asset"].create({"site_id": c.site.id}),
        "fix.site.risk.exception": exc,
    }


@pytest.mark.parametrize("model", RULED)
def test_4_another_company_or_unit_sees_nothing_and_the_unit_sees_its_own(c, ui, model):
    rec = _estate(c)[model]
    assert rec
    assert api.SURFACES[model].get("rules") is True
    cols = ["id"]
    listed = lambda u: {r["id"] for r in ui.records(u, model=model, cols=cols)["rows"]}  # noqa: E731
    assert rec.id in listed(c.clerk)
    assert rec.id in listed(c.fm)
    assert rec.id not in listed(c.fm_b)
    assert rec.id not in listed(c.fm_ou2)
    # the same answer when the id is opened directly
    field = {"name": "display_name"}
    assert "error" not in ui.form(c.fm, model=model, record_id=rec.id, fields=[field])
    assert "error" in ui.form(c.fm_b, model=model, record_id=rec.id, fields=[field])
    assert "error" in ui.form(c.fm_ou2, model=model, record_id=rec.id, fields=[field])


def test_4_the_reports_and_kpis_keep_to_the_callers_units(c, ui):
    lease = _lease(c, monthly_rent=70000.0)
    for user, seen in ((c.fm, True), (c.fm_ou2, False), (c.fm_b, False)):
        out = ui.report(user, module="M47", report="lease_expiry")
        assert (lease.name in [r["lease"] for r in out["rows"]]) is seen, user.login
        out = ui.report(user, module="M47", report="cost_per_site")
        assert (c.site.name in [r["site"] for r in out["rows"]]) is seen, user.login
    # a report row shows an engineer's name without the reader holding an HR role
    worker = c.env["hr.employee"].create({"name": "A7M47 Engineer", "company_id": c.co.id})
    _wo(c, assigned_to=worker.id)
    out = ui.report(c.clerk, module="M47", report="work_order_performance")
    assert "A7M47 Engineer" in [r["engineer"] for r in out["rows"]]


def test_4_every_form_opens_for_a_plain_user_of_the_unit(c, ui, js):
    """The rules read as the caller: a form must not break on a related record
    the reader holds no role for (an engineer, a vehicle, a device)."""
    estate = _estate(c)
    worker = c.env["hr.employee"].create({"name": "A7M47 Inspector", "company_id": c.co.id})
    eq = c.env["fix.equipment"].create(
        {"code": "A7M47-EQ", "name": "A7M47 Meter", "company_id": c.co.id}
    )
    brand = c.env["fleet.vehicle.model.brand"].create({"name": "A7M47 Brand"})
    van = c.env["fleet.vehicle"].create(
        {
            "model_id": c.env["fleet.vehicle.model"]
            .create({"name": "A7M47 Van", "brand_id": brand.id})
            .id,
            "license_plate": "A7M47-1",
            "company_id": c.co.id,
        }
    )
    estate[WO]._guarded().write(
        {"assigned_to": worker.id, "equipment_id": eq.id, "vehicle_id": van.id}
    )
    estate["fix.site.condition"].write({"inspector_id": worker.id})
    by_model = js["m47"]["chips"]["M47:__by_model__"]
    for model, rec in estate.items():
        sid = by_model[model]
        specs = list(form_fields(js, sid).values())
        for user in (c.clerk, c.fm):
            out = ui.form(user, model=model, record_id=rec.id, fields=specs)
            assert "error" not in out, (model, user.login, out)


def test_4_role_holders_still_do_their_jobs(c, ui):
    # a facility manager of the unit records, a plain user of the unit reports
    res = ui.write(
        c.clerk,
        model="fix.site.incident",
        record_id=False,
        values={"site_id": c.site.id, "description": "Glass door cracked"},
    )
    assert "error" not in res, res
    incident = c.env["fix.site.incident"].browse(res["id"])
    ui.ok(c.fm, incident._name, incident, "action_close", resolution="Replaced the door")
    # another unit's manager cannot act on it by id
    other = c.env["fix.site.incident"].create({"site_id": c.site.id, "description": "Leak"})
    ui.no(c.fm_ou2, other._name, other, "action_close", resolution="x")
    # the CFO of the unit signs from the inbox and reads the site
    assert c.site.id in {r["id"] for r in ui.records(c.cfo, model="fix.site", cols=["id"])["rows"]}


# ===================================================== 5: publish to IFRS 16
def _legacy_lease(c, **vals):
    """A lease from before the extract existed: live has 8 with no extract."""
    lease = _lease(c, **vals)
    lease.extract_ids._guarded().unlink()
    outbox = c.env["fix.event.outbox"].search(
        [("aggregate", "=", lease._name), ("aggregate_id", "=", lease.id)]
    )
    outbox.unlink()
    lease.invalidate_recordset()
    assert not lease.extract_ids
    return lease


def test_5_publish_button_takes_a_recorded_lease_to_ifrs16_once(c, ui, js):
    lease = _legacy_lease(c)
    assert not button(js, "M47-leases", "action_publish_ifrs16").get("ask")
    ui.no(c.clerk, lease._name, lease, "action_publish_ifrs16")
    assert not lease.extract_ids
    ui.ok(c.fm, lease._name, lease, "action_publish_ifrs16")
    assert len(lease.extract_ids) == 1
    assert (lease.extract_ids.version, lease.extract_ids.reason) == (1, "recorded")
    assert len(_events(c, "lease.extract_published", lease)) == 1
    assert len(_events(c, "lease.recorded", lease)) == 1
    # idempotent: the same lease version is one extract, and no new event
    ui.ok(c.fm, lease._name, lease, "action_publish_ifrs16")
    lease.invalidate_recordset()
    assert len(lease.extract_ids) == 1
    assert len(_events(c, "lease.extract_published", lease)) == 1
    # it reaches M49 as a draft, through the registered subscriptions
    _deliver(c, "consumer_lease_recorded", "lease.recorded", lease)
    _deliver(c, "consumer_lease_extract_published", "lease.extract_published", lease)
    contract = c.env["fix.lease"].search([("site_lease_id", "=", lease.id)])
    assert len(contract) == 1 and contract.state == "draft"
    assert contract.payment_amount == 50000.0 and contract.site_deposit == 600000.0
    assert lease.extract_ids.consumed_by_m19_at


def test_5_nothing_is_published_on_deploy(c):
    """Upgrading the module must not publish: only the button does."""
    lease = _legacy_lease(c)
    c.env["fix.site.lease"].cron_lease_critical_dates()
    lease.invalidate_recordset()
    assert not lease.extract_ids


# ===================================================== 6: licence evidence
def _licence_vals(c, **over):
    vals = {
        "site_id": c.site.id,
        "licence_type": "fire",
        "number": "FSC-1",
        "valid_to": str(c.today + timedelta(days=200)),
        "state": "valid",
        "evidence_file": SCAN,
        "evidence_filename": "fsc.pdf",
    }
    vals.update(over)
    return vals


def test_6_a_licence_needs_the_role_a_number_and_a_scan(c, ui, js):
    form = form_fields(js, "M47-form-licence")
    assert form["number"].get("required") is True
    assert form["evidence_file"]["type"] == "file" and "evidence_filename" in form
    Lic = "fix.site.licence"
    # a plain internal user records nothing
    assert "error" in ui.write(c.clerk, model=Lic, record_id=False, values=_licence_vals(c))
    no_number = ui.write(c.fm, model=Lic, record_id=False, values=_licence_vals(c, number=""))
    assert "number" in no_number["error"].lower()
    no_scan = ui.write(
        c.fm, model=Lic, record_id=False, values=_licence_vals(c, evidence_file=False)
    )
    assert "scan" in no_scan["error"].lower()
    res = ui.write(c.fm, model=Lic, record_id=False, values=_licence_vals(c))
    assert "error" not in res, res
    lic = c.env[Lic].browse(res["id"])
    assert lic.is_valid and lic.evidence_filename == "fsc.pdf"
    # and an edit by a plain user is refused too
    assert "error" in ui.write(c.clerk, model=Lic, record_id=lic.id, values={"number": "X"})
    # the scan cannot be taken away afterwards
    bad = ui.write(c.fm, model=Lic, record_id=lic.id, values={"evidence_file": False})
    assert "scan" in bad["error"].lower()


def test_6_a_forged_valid_licence_no_longer_clears_a_risk_exception(c, ui):
    exc = _lapsed_exception(c)
    assert exc.state == "open"
    forged = _licence_vals(c, licence_type="trade", number="FAKE", evidence_file=False)
    forged.pop("evidence_filename")
    res = ui.write(c.clerk, model="fix.site.licence", record_id=False, values=forged)
    assert "error" in res
    res = ui.write(c.fm, model="fix.site.licence", record_id=False, values=forged)
    assert "error" in res
    exc.invalidate_recordset()
    assert exc.state == "open"
    # the real renewal, with its scan, resolves it
    res = ui.write(
        c.fm,
        model="fix.site.licence",
        record_id=False,
        values=_licence_vals(c, licence_type="trade"),
    )
    assert "error" not in res, res
    exc.invalidate_recordset()
    assert exc.state == "resolved"


def test_6_existing_rows_keep_working_and_the_setting_turns_it_off(c, ui):
    legacy = _licence(c)  # loaded without a scan
    assert legacy.is_valid and not legacy.evidence_file
    # it can be edited without being refused for the missing scan
    res = ui.write(
        c.fm, model=legacy._name, record_id=legacy.id, values={"issued_on": str(c.today)}
    )
    assert "error" not in res, res
    c.env["ir.config_parameter"].set_param("cd_facility.require_licence_evidence", "False")
    res = ui.write(
        c.fm, model=legacy._name, record_id=False, values=_licence_vals(c, evidence_file=False)
    )
    assert "error" not in res, res
    # the number is still required with the setting off
    res = ui.write(
        c.fm,
        model=legacy._name,
        record_id=False,
        values=_licence_vals(c, licence_type="health", number="", evidence_file=False),
    )
    assert "number" in res["error"].lower()


def test_6_the_setting_defaults_to_required(c):
    param = c.env["ir.config_parameter"].get_param("cd_facility.require_licence_evidence")
    assert str(param).lower() == "true"


def test_6_valid_to_is_locked_once_recorded_and_a_save_keeps_the_alert_horizon(c, ui, js):
    lic = _licence(c)
    lic._guarded().write({"alert_horizon": 30})
    later = str(c.today + timedelta(days=900))
    res = ui.write(c.fm, model=lic._name, record_id=lic.id, values={"valid_to": later})
    assert "error" in res
    lic.invalidate_recordset()
    assert str(lic.valid_to) != later
    form = ui.form(c.fm, model=lic._name, record_id=lic.id, fields=[{"name": "valid_to"}])
    assert form["fields"][0]["readonly"] is True
    # a save that echoes the date and changes nothing else leaves the horizon
    res = ui.write(
        c.fm,
        model=lic._name,
        record_id=lic.id,
        values={"valid_to": str(lic.valid_to), "state": "valid", "number": "L-new"},
    )
    assert "error" not in res, res
    lic.invalidate_recordset()
    assert lic.alert_horizon == 30 and lic.number == "L-new"
    # a real change of date (a service write) restarts the alerts
    lic.sudo().write({"valid_to": later})
    assert lic.alert_horizon == 0


def test_6_an_undated_legacy_licence_is_dated_only_with_its_scan(c, ui):
    lic = c.env["fix.site.licence"].create({"site_id": c.site.id, "number": "OLD-1"})
    assert not lic.is_valid
    date = str(c.today + timedelta(days=100))
    res = ui.write(c.fm, model=lic._name, record_id=lic.id, values={"valid_to": date})
    assert "scan" in res["error"].lower()
    res = ui.write(
        c.fm,
        model=lic._name,
        record_id=lic.id,
        values={"valid_to": date, "evidence_file": SCAN, "evidence_filename": "old.pdf"},
    )
    assert "error" not in res, res
    lic.invalidate_recordset()
    assert lic.is_valid


# ===================================================== 7: triage
def test_7_a_person_raised_order_is_triaged_before_approval_and_schedule(c, ui, js):
    assert api.SURFACES[WO]["actions"] >= {"action_triage"}
    assert {a["kwarg"] for a in button(js, "M47-wo", "action_triage")["asks"]} == {"priority"}
    res = ui.write(
        c.clerk,
        model=WO,
        record_id=False,
        values={"site_id": c.site.id, "description": "AC leaking", "estimated_cost": 4000.0},
    )
    assert "error" not in res, res
    order = c.env[WO].browse(res["id"])
    assert not order.priority and not order.triaged_on
    ui.no(c.clerk, WO, order, "action_request_approval", match="triage", justification="x")
    ui.no(c.fm, WO, order, "action_schedule", match="triage")
    # nobody writes the priority on the form, and a plain user does not triage
    assert "error" in ui.write(c.fm, model=WO, record_id=order.id, values={"priority": "high"})
    ui.no(c.clerk, WO, order, "action_triage", priority="high")
    ui.no(c.fm, WO, order, "action_triage", match="priority", priority="soon")
    ui.ok(c.fm, WO, order, "action_triage", priority="high")
    assert order.priority == "high" and order.triaged_by_id == c.fm and order.triaged_on
    assert order.state == "draft"  # no new state
    # past triage the normal rules speak
    ui.no(c.fm, WO, order, "action_schedule", match="sign-off")


def test_7_system_raised_orders_are_born_triaged_at_normal(c):
    pm = c.env["fix.site.pm"].create(
        {"site_id": c.site.id, "scheduled_on": c.today - timedelta(days=1)}
    )
    c.env["fix.site.pm"].cron_pm_due()
    assert pm.work_order_id.priority == "normal" and pm.work_order_id.triaged_on
    pm.work_order_id.with_user(c.fm).action_schedule()
    assert pm.work_order_id.state == "scheduled"


def test_7_spine_routed_orders_are_born_triaged_at_normal(c, ui):
    demand = (
        c.env["fix.maintenance.demand"]
        .sudo()
        ._guarded()
        .create(
            {
                "name": "A7M47 demand",
                "origin": "m45_pm",
                "target": "work_order",
                "company_id": c.co.id,
                "source_model": "res.partner",
                "source_res_id": c.vendor.id,
                "description": "PM of a meter",
            }
        )
    )
    assert demand.state == "pending"
    assert "error" not in ui.write(
        c.fm, model=demand._name, record_id=demand.id, values={"site_id": c.site.id}
    )
    ui.ok(c.fm, demand._name, demand, "action_route")
    assert demand.work_order_id.priority == "normal"
    ui.ok(c.fm, WO, demand.work_order_id, "action_schedule")


# ===================================================== 8: recall
def test_8_every_approvable_has_recall_and_a_justified_request(c, js):
    for model, screen in (
        ("fix.site", "M47-sites"),
        ("fix.site.lease", "M47-leases"),
        ("fix.site.asset", "M47-infra"),
        (WO, "M47-wo"),
        ("fix.site.project", "M47-opening"),
    ):
        assert "action_recall_approval" in api.SURFACES[model]["actions"], model
        assert button(js, screen, "action_recall_approval")
        request = button(js, screen, "action_request_approval")
        assert request["kwarg"] == "justification" and request["ask"], screen


@pytest.mark.parametrize("which", ["project", "asset", "work_order", "site", "lease"])
def test_8_the_requester_recalls_through_the_endpoint(c, ui, which):
    if which == "project":
        rec = c.env["fix.site.project"].create({"site_id": c.site.id, "budget": 100000.0})
    elif which == "asset":
        rec = c.env["fix.site.asset"].create({"site_id": c.site.id, "value": 50000.0})
    elif which == "work_order":
        rec = _wo(c, estimated_cost=8000.0)
    elif which == "site":
        rec = c.site
    else:
        rec = _lease(c)
        ui.ok(c.fm, rec._name, rec, "action_open_modification")
    ui.ok(c.fm, rec._name, rec, "action_request_approval", justification="Needed for the branch")
    assert rec.approval_state == "pending"
    ui.no(c.fm2, rec._name, rec, "action_recall_approval", match="requested")
    ui.ok(c.fm, rec._name, rec, "action_recall_approval")
    assert rec.approval_state == "none"


# ===================================================== 9 / 10: reaching AP
def _bills(c, last=20000.0):
    """Three ordinary months, then the bill under test."""
    # A07 ERP audit (2026-11-20) M47-12/18: a bill is recorded by a Facility
    # Manager against its supply account, whose provider is the only payee
    c.env["fix.site.utility.account"].with_user(c.fm).create(
        {
            "site_id": c.site.id,
            "utility_type": "power",
            "provider_id": c.vendor.id,
            "account_no": "A7-1",
        }
    )
    Utility = c.env["fix.site.utility"]
    for month in ("2026-01", "2026-02", "2026-03"):
        Utility.create({"site_id": c.site.id, "period": month, "amount": 10000.0})
    return Utility.with_user(c.fm).create(
        {"site_id": c.site.id, "period": "2026-04", "amount": last}
    )


def test_10_a_held_bill_stays_out_of_ap_and_its_release_sends_it(c, ui, js):
    bill = _bills(c, last=30000.0)
    assert bill.review_state == "held"
    assert not _events(c, "site.utility_payable", bill)
    ui.no(c.fm2, bill._name, bill, "action_release", notes="fine")
    ui.no(c.clerk, bill._name, bill, "action_release", notes="fine")
    ui.ok(c.bol, bill._name, bill, "action_release", notes="Tariff rise confirmed with DESCO")
    assert bill.review_state == "released"
    _deliver(c, "consumer_site_utility_payable", "site.utility_payable", bill)
    _deliver(c, "consumer_site_utility_payable", "site.utility_payable", bill)  # redelivery
    entry = c.env["fix.asset.cost.entry"].search(
        [("source_model", "=", bill._name), ("source_res_id", "=", bill.id)]
    )
    assert len(entry) == 1 and entry.amount == 30000.0 and entry.site_id == c.site
    assert entry.cost_type == "site_utility" and entry.company_id == c.co
    assert not bill.paid_on
    # the accountant matches it, and the bill says it is paid
    invoice = _bill(c, c.vendor, 30000.0, ref="DESCO-44")
    ui.write(c.acct, model=entry._name, record_id=entry.id, values={"match_invoice_id": invoice.id})
    ui.ok(c.acct, entry._name, entry, "action_match_bill")
    bill.invalidate_recordset()
    # M47-06: matched to the provider's bill is billed, not paid
    assert bill.matched_on and bill.invoice_ref == "DESCO-44"
    assert not bill.paid_on and not bill.paid_amount
    invoice.sudo()._guarded().write({"payment_state": "paid"})
    bill.invalidate_recordset()
    assert bill.paid_on and bill.paid_amount == 30000.0
    for name in ("paid_amount", "paid_on", "invoice_ref"):
        assert form_fields(js, "M47-form-utility")[name]["readonly"] is True
    # a paid bill keeps its figures
    assert "error" in ui.write(c.clerk, model=bill._name, record_id=bill.id, values={"amount": 1.0})
    ui.no(c.clerk, bill._name, bill, "action_flag", match="paid")


def test_10_an_ordinary_bill_reaches_ap_and_a_held_one_cannot_be_matched(c, ui):
    bill = _bills(c, last=11000.0)
    assert bill.review_state == "none"
    _deliver(c, "consumer_site_utility_payable", "site.utility_payable", bill)
    entry = c.env["fix.asset.cost.entry"].search(
        [("source_model", "=", bill._name), ("source_res_id", "=", bill.id)]
    )
    assert entry.state == "pending"
    # a concern raised before AP matched it holds the payment for real
    ui.ok(c.clerk, bill._name, bill, "action_flag")
    invoice = _bill(c, c.vendor, 11000.0, ref="DESCO-45")
    ui.write(c.acct, model=entry._name, record_id=entry.id, values={"match_invoice_id": invoice.id})
    ui.no(c.acct, entry._name, entry, "action_match_bill", match="held")
    assert entry.state == "pending" and not bill.paid_on
    # the review confirms the anomaly: it stays out; AP rejects it
    ui.ok(c.bol, bill._name, bill, "action_confirm_anomaly", notes="Meter fault")
    ui.no(c.acct, entry._name, entry, "action_match_bill", match="held")
    ui.ok(c.acct, entry._name, entry, "action_reject", reason="Meter fault: not payable")


def test_10_a_bill_from_before_this_rule_is_sent_by_hand(c, ui):
    bill = _bills(c, last=11000.0)
    c.env["fix.event.outbox"].search(
        [("aggregate", "=", bill._name), ("aggregate_id", "=", bill.id)]
    ).unlink()
    bill._guarded().write({"ap_requested_on": False})
    ui.no(c.clerk, bill._name, bill, "action_send_to_ap")
    ui.ok(c.fm, bill._name, bill, "action_send_to_ap")
    assert len(_events(c, "site.utility_payable", bill)) == 1
    ui.ok(c.fm, bill._name, bill, "action_send_to_ap")  # idempotent
    assert len(_events(c, "site.utility_payable", bill)) == 1


def test_9_a_rent_row_reaches_ap_and_its_match_stamps_the_schedule(c, ui, js):
    # rent from the start is payable here (M47-27 makes earlier months history by default)
    lease = _lease(c, schedule_from=c.today - timedelta(days=30))
    row = lease.schedule_ids.sorted("due_date")[0]
    assert button(js, "M47-lease-schedule", "action_send_to_ap")
    ui.no(c.clerk, row._name, row, "action_send_to_ap")
    ui.ok(c.fm, row._name, row, "action_send_to_ap")
    ui.ok(c.fm, row._name, row, "action_send_to_ap")  # idempotent
    assert len(_events(c, "lease.rent_payment_requested", row)) == 1
    _deliver(c, "consumer_lease_rent_payment_requested", "lease.rent_payment_requested", row)
    entry = c.env["fix.asset.cost.entry"].search(
        [("source_model", "=", row._name), ("source_res_id", "=", row.id)]
    )
    assert entry.amount == row.rent_due and entry.vendor_id == c.landlord
    # the rent goes on the landlord's bill, not another vendor's
    wrong = _bill(c, c.vendor, row.rent_due, ref="WRONG-1")
    ui.write(c.acct, model=entry._name, record_id=entry.id, values={"match_invoice_id": wrong.id})
    ui.no(c.acct, entry._name, entry, "action_match_bill")
    right = _bill(c, c.landlord, row.rent_due, ref="RENT-1")
    ui.write(c.acct, model=entry._name, record_id=entry.id, values={"match_invoice_id": right.id})
    ui.ok(c.acct, entry._name, entry, "action_match_bill")
    row.invalidate_recordset()
    # M47-06: billed by the landlord's bill, paid only when that bill is paid
    assert row.matched_on and row.invoice_ref == "RENT-1" and not row.paid_on
    assert row.variance == 0.0
    # paid only when the landlord's bill is paid (FIN-19), at the bill's amount
    right.sudo()._guarded().write({"payment_state": "paid"})
    row.invalidate_recordset()
    assert row.paid_on and row.paid_amount == row.rent_due and entry.paid_on


# ===================================================== 11: incidents reach M59 / M60
@pytest.mark.parametrize("kind", ["fire", "theft", "trespass"])
def test_11_fire_theft_and_trespass_reach_the_risk_register_and_a_hazard(c, ui, kind):
    res = ui.write(
        c.clerk,
        model="fix.site.incident",
        record_id=False,
        values={"site_id": c.site.id, "incident_type": kind, "description": "Reported on site"},
    )
    assert "error" not in res, res
    incident = c.env["fix.site.incident"].browse(res["id"])
    for _ in range(2):  # a redelivery is one effect
        _deliver(c, "consumer_site_incident_risk", "site.incident", incident)
        _deliver(c, "consumer_site_incident_hazard", "site.incident", incident)
    risk = c.env["fix.risk.register"].search(
        [("bridge_subject_key", "=", "m60:fix.site:%s" % c.site.id)]
    )
    assert len(risk) == 1 and incident.name in risk.bridge_lapse_log
    assert risk.bridge_trigger_count == 1 and risk.company_id == c.co
    hazard = c.env["fix.hse.hazard"].search(
        [("bridge_source_key", "=", "m59:fix.site.incident:%s" % incident.id)]
    )
    assert len(hazard) == 1 and hazard.site_incident_id == incident and hazard.state == "open"
    assert hazard.company_id == c.co and hazard.operating_unit_id == c.ou


def test_11_an_injury_also_reaches_m60_and_other_stays_out(c):
    injury = c.env["fix.site.incident"].create(
        {"site_id": c.site.id, "incident_type": "injury", "description": "Cut hand"}
    )
    _deliver(c, "consumer_site_incident_risk", "site.incident", injury)
    _deliver(c, "consumer_site_incident_hazard", "site.incident", injury)
    risk = c.env["fix.risk.register"].search(
        [("bridge_subject_key", "=", "m60:fix.site:%s" % c.site.id)]
    )
    assert injury.name in risk.bridge_lapse_log
    assert not c.env["fix.hse.hazard"].search_count(
        [("bridge_source_key", "=", "m59:fix.site.incident:%s" % injury.id)]
    )
    other = c.env["fix.site.incident"].create(
        {"site_id": c.site.id, "incident_type": "other", "description": "Dispute"}
    )
    _deliver(c, "consumer_site_incident_risk", "site.incident", other)
    _deliver(c, "consumer_site_incident_hazard", "site.incident", other)
    risk.invalidate_recordset()
    assert other.name not in risk.bridge_lapse_log


# ===================================================== 13: report figures
def test_13_cost_per_site_counts_a_pm_once_and_only_when_done(c, ui):
    site = c.site
    PM = c.env["fix.site.pm"]
    PM.create({"site_id": site.id, "cost": 1000.0})  # still open: no spend
    done = PM.create({"site_id": site.id, "cost": 200.0})
    done.action_done()
    # done through its work order: the order's actual is the spend, not the PM's cost too
    raised = PM.create(
        {"site_id": site.id, "cost": 3000.0, "scheduled_on": c.today - timedelta(days=1)}
    )
    PM.cron_pm_due()
    raised.invalidate_recordset()
    order = raised.work_order_id
    order._guarded().write({"state": "verified", "actual_cost": 3500.0})
    raised._guarded().write({"state": "done", "done_on": c.today})
    order._guarded().write({"completed_at": fields.Datetime.now()})
    # M47-21: one period for every column (today's, here)
    out = ui.report(
        c.fm,
        module="M47",
        report="cost_per_site",
        params={"date_from": str(c.today), "date_to": str(c.today)},
    )
    row = next(r for r in out["rows"] if r["site"] == site.name)
    assert (row["pm"], row["work_orders"]) == (200.0, 3500.0), row
    assert row["total"] == row["rent"] + row["utilities"] + 200.0 + 3500.0


def test_13_branch_asset_register_leaves_out_retired_plant(c, ui):
    Asset = c.env["fix.site.asset"]
    Asset.create({"site_id": c.site.id, "value": 1000.0})
    gone = Asset.create({"site_id": c.site.id, "value": 9000.0})
    gone._guarded().write({"state": "retired"})
    out = ui.report(c.fm, module="M47", report="branch_assets")
    row = next(r for r in out["rows"] if r["site"] == c.site.name)
    assert (row["assets"], row["asset_value"]) == (1, 1000.0), row


# ===================================================== 14: facts on the screen
def test_14_bridge_facts_are_shown_read_only(c, ui, js):
    lease_form = form_fields(js, "M49-form-lease", "m49")
    for name in ("site_lease_id", "site_escalation_pct", "site_deposit"):
        assert lease_form[name]["readonly"] is True, name
    case_form = form_fields(js, "M59-form-incident", "m59")
    for name in ("site_incident_id", "source_notice_due_on"):
        assert case_form[name]["readonly"] is True, name
    assert form_fields(js, "M60-form-risk", "m60")["bridge_lapse_log"]["readonly"] is True
    demand_list = js["m47"]["screens"]["M47-demand"]["cols"]
    assert "vehicle_id" in demand_list
    assert form_fields(js, "M47-form-demand")["vehicle_id"]["readonly"] is True
    # and they read through the endpoint, by the people who use those forms
    lease = _lease(c, escalation_pct=5.0)
    _deliver(c, "consumer_lease_recorded", "lease.recorded", lease)
    contract = c.env["fix.lease"].search([("site_lease_id", "=", lease.id)])
    out = ui.form(
        c.acct,
        model="fix.lease",
        record_id=contract.id,
        fields=[{"name": n, "readonly": True} for n in ("site_lease_id", "site_deposit")],
    )
    assert "error" not in out, out
    assert out["record"]["site_lease_id"]["id"] == lease.id
    assert out["record"]["site_deposit"] == 600000.0
    # the HSE officer reads where a case came from
    reporter = c.env["hr.employee"].create(
        {"name": "A7M47 Rep", "company_id": c.co.id, "user_id": c.clerk.id}
    )
    assert reporter
    incident = (
        c.env["fix.site.incident"]
        .with_user(c.clerk)
        .create({"site_id": c.site.id, "incident_type": "injury", "description": "Burn"})
    )
    case = c.env["fix.hse.incident"]._bridge_case_for_site_incident(incident)
    out = ui.form(
        c.hse,
        model="fix.hse.incident",
        record_id=case.id,
        fields=[
            {"name": n, "readonly": True} for n in ("site_incident_id", "source_notice_due_on")
        ],
    )
    assert "error" not in out, out
    assert out["record"]["site_incident_id"]["id"] == incident.id
    assert out["record"]["source_notice_due_on"] == str(incident.hse_notice_due_on)
    assert {"bridge_lapse_log", "bridge_subject_ref"} <= set(c.env["fix.risk.register"]._fields)


# ===================================================== 15: + New
def test_15_nobody_is_offered_new_on_system_written_lists(js):
    screens = js["m47"]["screens"]
    for sid in ("M47-lease-schedule", "M47-lease-extracts", "M47-risk", "M47-demand"):
        assert screens[sid]["create"] is False, sid


# ===================================================== logic bugs: the site
def test_a_suspended_site_closes_and_closure_resolves_its_exception(c, ui, js):
    exc = _lapsed_exception(c)
    ui.ok(c.ceo, exc._name, exc, "action_decide_suspend", notes="Fire licence refused")
    site = c.site
    assert site.state == "suspended"
    # the resumption stays blocked by the lapse, as it should
    ui.no(
        c.bol, site._name, site, "action_request_approval", match="cannot resume", justification="x"
    )
    assert button(js, "M47-sites", "action_request_closure")["kwarg"] == "justification"
    ui.ok(c.fm, site._name, site, "action_request_closure", justification="Exit the premises")
    assert site.closure_requested and site.approval_state == "pending"
    approve_via_inbox(site, c.cfo, requester=c.fm)
    assert site.status_cfo_approved_by_id == c.cfo
    ui.no(c.fm, site._name, site, "action_close", match="sign-off")
    ui.ok(c.fm, site._name, site, "action_request_closure", justification="Exit the premises")
    approve_via_inbox(site, c.ceo, requester=c.fm)
    ui.ok(c.fm, site._name, site, "action_close")
    assert site.state == "closed" and not site.closure_requested
    exc.invalidate_recordset()
    assert exc.state == "resolved" and "closed" in exc.resolution
    # the daily job no longer chases it
    assert "before" not in _events(c, "site.status_changed", site)[-1]
    assert _events(c, "site.status_changed", site)[-1]["from_status"] == "suspended"


def test_recalling_a_closure_request_gives_the_site_back_its_resumption(c, ui):
    exc = _lapsed_exception(c)
    ui.ok(c.ceo, exc._name, exc, "action_decide_suspend", notes="Stop")
    site = c.site
    ui.ok(c.fm, site._name, site, "action_request_closure", justification="Exit")
    ui.ok(c.fm, site._name, site, "action_recall_approval")
    assert not site.closure_requested and site.approval_state == "none"


def test_the_daily_job_resolves_an_exception_left_open_at_a_closed_site(c):
    exc = _lapsed_exception(c)
    c.site.sudo()._guarded().write({"state": "closed"})
    c.env["fix.site.licence"].cron_licence_expiry()
    exc.invalidate_recordset()
    assert exc.state == "resolved" and not exc.last_escalated_on


# ===================================================== logic bugs: PM
def test_pm_mark_done_needs_the_role_and_no_open_work_order(c, ui):
    PM = c.env["fix.site.pm"]
    free = PM.create({"site_id": c.site.id})
    ui.no(c.clerk, PM._name, free, "action_done", match="Facility Manager")
    ui.ok(c.fm, PM._name, free, "action_done")
    assert free.state == "done"
    due = PM.create({"site_id": c.site.id, "scheduled_on": c.today - timedelta(days=1)})
    PM.cron_pm_due()
    due.invalidate_recordset()
    order = due.work_order_id
    assert order
    ui.no(c.fm, PM._name, due, "action_done", match=order.name)
    assert due.state == "open"
    # a cancelled order no longer stands in the way
    order.sudo().action_cancel(reason="Done another way")
    ui.ok(c.fm, PM._name, due, "action_done")


def test_the_pm_cron_raises_no_order_at_a_closed_or_planned_site(c):
    PM = c.env["fix.site.pm"]
    planned = c.env["fix.site"].create({"name": "A7M47 Planned", "company_id": c.co.id})
    pm = PM.create({"site_id": planned.id, "scheduled_on": c.today - timedelta(days=1)})
    PM.cron_pm_due()
    assert not pm.work_order_id


# ===================================================== logic bugs: work order
def _completed(c, **vals):
    order = _wo(c, **vals)
    order._guarded().write(
        {
            "state": "completed",
            "completion_notes": "Done, photos in file",
            "completed_by_id": c.fm2.id,
        }
    )
    return order


def test_a_costed_order_verifies_with_an_actual_cost_or_a_reason(c, ui):
    order = _completed(c)
    order.sudo()._guarded().write({"estimated_cost": 8000.0})
    order.sudo()._guarded().write(
        {
            "dofa_approved": True,
            "dofa_approved_tier": "tier_2",
            "dofa_approved_amount": 8000.0,
        }
    )
    ui.no(c.fm, WO, order, "action_verify", match="actual cost", notes="")
    ui.ok(c.fm, WO, order, "action_verify", notes="Warranty job: the vendor charged nothing")
    assert order.state == "verified"


def test_verify_re_asserts_the_spend_approval(c, ui):
    order = _completed(c, actual_cost=8000.0)
    ui.no(c.fm, WO, order, "action_verify", match="sign-off", notes="ok")
    assert order.state == "completed"


def test_order_on_a_closed_or_planned_site_is_refused(c, ui):
    planned = c.env["fix.site"].create(
        {"name": "A7M47 Fit-out", "company_id": c.co.id, "operating_unit_id": c.ou.id}
    )
    closed = c.env["fix.site"].create(
        {"name": "A7M47 Closed", "company_id": c.co.id, "operating_unit_id": c.ou.id}
    )
    closed.sudo()._guarded().write({"state": "closed"})
    for site in (planned, closed):
        res = ui.write(
            c.fm, model=WO, record_id=False, values={"site_id": site.id, "description": "x"}
        )
        assert "operational" in res["error"].lower(), res
    order = _wo(c)
    res = ui.write(c.fm, model=WO, record_id=order.id, values={"site_id": closed.id})
    assert "operational" in res["error"].lower(), res
    # a suspended site still needs its repairs
    c.site.sudo()._guarded().write({"state": "suspended"})
    res = ui.write(
        c.fm, model=WO, record_id=False, values={"site_id": c.site.id, "description": "Fix alarm"}
    )
    assert "error" not in res, res


def test_a_demand_is_not_routed_to_a_closed_or_planned_site(c, ui):
    planned = c.env["fix.site"].create({"name": "A7M47 Plan2", "company_id": c.co.id})
    demand = (
        c.env["fix.maintenance.demand"]
        .sudo()
        ._guarded()
        .create(
            {
                "name": "A7M47 demand 2",
                "origin": "m45_pm",
                "target": "work_order",
                "company_id": c.co.id,
                "source_model": "res.partner",
                "source_res_id": c.landlord.id,
                "description": "PM",
                "site_id": planned.id,
            }
        )
    )
    ui.no(c.fm, demand._name, demand, "action_route", match="operational")
    assert demand.state == "pending" and not demand.work_order_id


def test_cancel_and_reopen_need_the_facility_manager(c, ui):
    order = _wo(c)
    ui.no(c.clerk, WO, order, "action_cancel", match="Facility Manager", reason="x")
    ui.ok(c.fm, WO, order, "action_cancel", reason="Raised twice")
    done = _completed(c)
    ui.no(c.clerk, WO, done, "action_reopen", match="Facility Manager", reason="x")
    ui.ok(c.fm, WO, done, "action_reopen", reason="Still leaking")
    assert done.state == "in_progress"


# ===================================================== logic bugs: the lease
def test_terminate_needs_the_role_a_reason_and_tells_finance(c, ui):
    lease = _lease(c)
    ui.no(c.fm, lease._name, lease, "action_terminate", reason="x", match="Branch Operations Lead")
    # D6: an early end is requested, approved on the commitment, then executed
    ui.no(c.bol, lease._name, lease, "action_terminate", match="request the termination")
    ui.no(c.bol, lease._name, lease, "action_request_termination", reason=" ", match="why")
    ui.ok(
        c.bol,
        lease._name,
        lease,
        "action_request_termination",
        reason="Landlord sold the building",
        deposit_outcome="refund",
    )
    approve_via_inbox(lease, c.cfo, requester=c.bol)
    ui.ok(c.bol, lease._name, lease, "action_terminate")
    assert lease.state == "terminated"
    events = _events(c, "lease.terminated", lease)
    assert len(events) == 1 and events[0]["reason"] == "Landlord sold the building"
    newest = lease.extract_ids.sorted("version")[-1]
    assert newest.reason == "terminated" and newest.version == 2
    data = json.loads(newest.payload)
    assert data["state"] == "terminated" and data["terminated_reason"]
    # a commenced contract gets an item that says so
    _deliver(c, "consumer_lease_recorded", "lease.recorded", lease)
    contract = c.env["fix.lease"].search([("site_lease_id", "=", lease.id)])
    contract.sudo().write({"state": "active", "site_extract_version": 1})
    _deliver(c, "consumer_lease_extract_published", "lease.extract_published", lease)
    item = c.env["fix.lease.modification.item"].search([("site_lease_id", "=", lease.id)])
    assert item.reason == "terminated" and "Terminated" in item.changes


def test_recorded_terms_move_only_through_a_modification(c, ui, js):
    lease = _lease(c, notice_period_days=90)
    other = c.env["fix.site"].create({"name": "A7M47 Other", "company_id": c.co.id})
    partner = c.env["res.partner"].create({"name": "A7M47 New Landlord"})
    for values in (
        {"deposit": 1.0},
        {"lessor_id": partner.id},
        {"site_id": other.id},
        {"notice_period_days": 5},
    ):
        res = ui.write(c.fm, model=lease._name, record_id=lease.id, values=values)
        assert "error" in res, values
    form = ui.form(
        c.fm,
        model=lease._name,
        record_id=lease.id,
        fields=[{"name": n} for n in ("deposit", "lessor_id", "site_id", "notice_period_days")],
    )
    assert all(f["readonly"] for f in form["fields"]), form["fields"]
    # the route is a modification, which carries them
    offered = form_fields(js, "M47-form-lease")
    for name in ("proposed_deposit", "proposed_notice_period_days", "proposed_lessor_id"):
        assert not offered[name].get("readonly"), name
    ui.ok(c.fm, lease._name, lease, "action_open_modification")
    assert lease.proposed_deposit == 600000.0 and lease.proposed_lessor_id == c.landlord
    res = ui.write(
        c.fm,
        model=lease._name,
        record_id=lease.id,
        values={
            "proposed_deposit": 700000.0,
            "proposed_notice_period_days": 120,
            "proposed_lessor_id": partner.id,
            "modification_reason": "Assigned to the new owner",
        },
    )
    assert "error" not in res, res
    approve_via_inbox(lease, c.cfo, requester=c.fm, justification="Assignment")
    ui.ok(c.fm, lease._name, lease, "action_apply_modification")
    assert (lease.deposit, lease.notice_period_days, lease.lessor_id) == (700000.0, 120, partner)
    assert json.loads(lease.extract_ids.sorted("version")[-1].payload)["deposit"] == 700000.0


def test_a_blank_notice_period_may_be_filled_once(c, ui):
    lease = _lease(c)
    assert not lease.notice_period_days
    res = ui.write(c.fm, model=lease._name, record_id=lease.id, values={"notice_period_days": 60})
    assert "error" not in res, res
    res = ui.write(c.fm, model=lease._name, record_id=lease.id, values={"notice_period_days": 30})
    assert "error" in res


def test_shortening_a_lease_needs_approval_even_to_a_past_date(c, ui):
    lease = _lease(c)
    ui.ok(c.fm, lease._name, lease, "action_open_modification")
    past = str(c.today - timedelta(days=5))
    res = ui.write(
        c.fm,
        model=lease._name,
        record_id=lease.id,
        values={"proposed_end_date": past, "modification_reason": "Early exit"},
    )
    assert "error" not in res, res
    assert lease._dofa_current_tier() != "tier_0"
    ui.no(c.fm, lease._name, lease, "action_apply_modification", match="sign-off")
    assert str(lease.end_date) != past
    # an expired lease shortened further still needs a decision
    ended = _lease(
        c, start_date=c.today - timedelta(days=400), end_date=c.today - timedelta(days=30)
    )
    assert ended.state == "expired"
    ui.ok(c.fm, ended._name, ended, "action_open_modification")
    ended.with_user(c.fm).write({"proposed_end_date": c.today - timedelta(days=60)})
    assert ended._dofa_current_tier() != "tier_0"


# ===================================================== logic bugs: incidents
def test_changing_type_to_injury_starts_the_clock_and_opens_the_case(c, ui):
    worker = c.env["hr.employee"].create(
        {"name": "A7M47 Reporter", "company_id": c.co.id, "user_id": c.clerk.id}
    )
    res = ui.write(
        c.clerk,
        model="fix.site.incident",
        record_id=False,
        values={"site_id": c.site.id, "incident_type": "other", "description": "Fall in the store"},
    )
    incident = c.env["fix.site.incident"].browse(res["id"])
    assert not incident.hse_notice_due_on
    res = ui.write(
        c.clerk, model=incident._name, record_id=incident.id, values={"incident_type": "injury"}
    )
    assert "error" not in res, res
    assert incident.injuries_flag
    assert incident.hse_notice_due_on == incident.occurred_on + timedelta(days=2)
    case = c.env["fix.hse.incident"].search([("site_incident_id", "=", incident.id)])
    assert len(case) == 1 and case.employee_id == worker
    assert len(_events(c, "site.incident", incident)) == 2
    # a corrected accident date moves the statutory date, here and on the case
    earlier = incident.occurred_on - timedelta(days=3)
    res = ui.write(
        c.clerk, model=incident._name, record_id=incident.id, values={"occurred_on": str(earlier)}
    )
    assert "error" not in res, res
    assert incident.hse_notice_due_on == earlier + timedelta(days=2)
    case.invalidate_recordset()
    assert case.source_notice_due_on == earlier + timedelta(days=2)


# ===================================================== logic bugs: safety checks
def test_a_safety_check_records_its_result_and_a_fail_raises_the_hazard(c, ui, js):
    item = c.env["fix.site.safety"].create(
        {"site_id": c.site.id, "next_check": c.today + timedelta(days=90)}
    )
    assert api.SURFACES[item._name]["actions"] >= {"action_check_pass", "action_check_fail"}
    assert button(js, "M47-safety", "action_check_pass")
    assert {a["kwarg"] for a in button(js, "M47-safety", "action_check_fail")["asks"]} == {
        "next_check",
        "finding",
    }
    date = str(c.today + timedelta(days=180))
    ui.ok(c.clerk, item._name, item, "action_check_pass", next_check=date)
    assert item.last_result == "pass" and item.state == "ok" and str(item.next_check) == date
    assert item.last_checked_by_id == c.clerk
    ui.no(c.clerk, item._name, item, "action_check_fail", match="what failed", next_check=date)
    ui.ok(
        c.clerk,
        item._name,
        item,
        "action_check_fail",
        next_check=date,
        finding="Pressure gauge in the red",
    )
    assert item.last_result == "fail" and item.state == "unfit"
    assert "red" in item.last_finding
    assert item in c.env["fix.site.safety"].search([("state", "in", ["unfit"])])
    assert item not in c.env["fix.site.safety"].search([("state", "in", ["ok"])])
    _deliver(c, "consumer_site_safety_check_failed", "site.safety_check_failed", item)
    _deliver(c, "consumer_site_safety_check_failed", "site.safety_check_failed", item)
    hazard = c.env["fix.hse.hazard"].search(
        [("bridge_source_key", "=", "m59:fix.site.safety:%s" % item.id)]
    )
    assert len(hazard) == 1 and "red" in hazard.controls and hazard.site_safety_id == item
    # an unfit item fails the readiness gate
    planned = c.env["fix.site"].create({"name": "A7M47 Gate", "company_id": c.co.id})
    item.sudo()._guarded().write({"site_id": planned.id})
    assert any("safety" in line for line in planned._site_readiness_items())
    # a later pass clears it
    ui.ok(c.clerk, item._name, item, "action_check_pass", next_check=date)
    assert item.state == "ok"


def test_the_item_status_does_not_lie_on_a_row_with_no_result(c):
    """A check recorded before this rule has no result: the date alone decides."""
    item = c.env["fix.site.safety"].create(
        {"site_id": c.site.id, "next_check": c.today + timedelta(days=90)}
    )
    assert not item.last_result and item.state == "ok"
    assert item in c.env["fix.site.safety"].search([("state", "in", ["ok"])])
