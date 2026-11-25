# cd_fixed_asset_ext — A08 finish: can a person do the M49 job on the P03 workspace?
#
# Each test walks the real path as a NON-ADMIN user with the real finance role,
# through the workspace endpoints where a screen exists. The screens are read by
# evaluating static/src/a08/m49.js with node, and the write whitelist is what
# controllers/form_fields.py generates from those forms.
from __future__ import annotations

import base64
import json
import shutil
import subprocess
import types
from datetime import date
from pathlib import Path

import odoo.addons.cd_p03_portal as portal
import odoo.addons.cd_p03_portal.controllers.p03_generic_api as api
import pytest
from odoo import fields
from odoo.addons.cd_fixed_asset_ext.tests.test_a08_m49_controls import (
    _approve,
    _confirm_tax_rate,
    _disposal,
    _post,
    _reval,
    approved_capex,
    balance,
    budget,
    c,  # noqa: F401 - the fixture
    dep_run,
    request,
    seam_asset,
)
from odoo.addons.cd_p03_portal.controllers.a08 import m49 as m49_surface
from odoo.addons.cd_p03_portal.controllers.form_fields import editable_by_model
from odoo.exceptions import AccessError, UserError, ValidationError

pytestmark = [pytest.mark.financial]

REFUSED = (UserError, ValidationError, AccessError)
PDF = base64.b64encode(b"%PDF-1.4 valuer report").decode()
SRC = Path(portal.__file__).parent / "static" / "src" / "a08"
POSTING_ACCOUNTS = (
    "asset_account_id",
    "accumulated_account_id",
    "expense_account_id",
    "cwip_account_id",
    "revaluation_surplus_account_id",
    "impairment_account_id",
    "gain_account_id",
    "loss_account_id",
)


@pytest.fixture(scope="module")
def m49_js(tmp_path_factory):
    node = shutil.which("node")
    assert node, "node evaluates the registry: without it these tests prove nothing"
    tmp = tmp_path_factory.mktemp("m49js")
    (tmp / "m49.mjs").write_text((SRC / "m49.js").read_text(encoding="utf-8"), "utf-8")
    (tmp / "run.mjs").write_text(
        "import * as M from './m49.mjs';\n"
        "console.log(JSON.stringify({module: M.MODULE, screens: M.SCREENS, chips: M.FORM_CHIPS}));\n",
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our probe file
        [node, str(tmp / "run.mjs")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=60,
    )
    return json.loads(out.stdout)


def offered(js, screen):
    cfg = js["screens"][screen]
    tabs = {t["id"] for t in cfg.get("tabs", [])}
    out = {}
    for section in cfg["sections"]:
        if tabs:
            assert section.get("tab") in tabs, f"{screen}: a section in no tab renders invisible"
        for field in section["fields"]:
            out[field["name"]] = field
    return out


def actions(js, screen):
    return {a["m"]: a for a in js["screens"][screen].get("actions", [])}


@pytest.fixture
def ui(c, monkeypatch):  # noqa: F811
    cls = api.P03GenericApiController
    ctl = cls()
    mw = getattr(cls.model_write, "original_endpoint", cls.model_write)
    ma = getattr(cls.model_action, "original_endpoint", cls.model_action)
    generated = editable_by_model()
    for model, conf in api.SURFACES.items():
        if model in generated:
            monkeypatch.setitem(conf, "writable", frozenset(generated[model]))

    def call(fn, user, **kw):
        monkeypatch.setattr(api, "request", types.SimpleNamespace(env=c.as_(user)))
        return fn(ctl, **kw)

    return types.SimpleNamespace(
        write=lambda user, **kw: call(mw, user, **kw),
        action=lambda user, **kw: call(ma, user, **kw),
    )


def relay(c, event_type, aggregate, aggregate_id, xmlid):  # noqa: F811
    Outbox = c.env["fix.event.outbox"].sudo()
    event = Outbox.search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", aggregate),
            ("aggregate_id", "=", aggregate_id),
        ],
        order="id desc",
        limit=1,
    )
    assert event, f"{event_type} {aggregate}/{aggregate_id} was not published"
    assert Outbox._relay_deliver(c.env.ref(xmlid).sudo(), event) == ""


# =========================================================== M49-11
def test_m49_11_tax_run_from_the_form_and_surface(c, ui, m49_js):  # noqa: F811
    assert m49_js["screens"]["M49-dep"].get("create") is not False
    assert m49_js["chips"]["M49:__by_screen__"]["M49-dep"] == "M49-form-deprun"
    fields_ = offered(m49_js, "M49-form-deprun")
    assert not fields_["book"].get("readonly") and not fields_["period_start"].get("readonly")
    assert fields_["state"]["readonly"] and fields_["note"]["readonly"]
    assert {"action_compute", "action_post"} <= set(actions(m49_js, "M49-dep"))

    asset = seam_asset(c, cat=c.cat_it)
    res = ui.write(
        c.acc1,
        model="fix.asset.depreciation.run",
        record_id=False,
        values={"book": "tax", "period_start": "2026-01-01", "asset_ids": [asset.id]},
    )
    assert "error" not in res, res
    run = c.env["fix.asset.depreciation.run"].browse(res["id"])
    assert (run.book, run.asset_ids, run.company_id) == ("tax", asset, c.co)
    # the rate the tax adviser has not confirmed refuses, and says so
    first = ui.action(c.acc1, model=run._name, ids=run.ids, method="action_compute")
    rate = c.env["fix.tax.rate"].find_rate("depreciation", "ITA3-COMPUTER", date(2026, 1, 1), c.co)
    if rate.verify_with_adviser:
        assert first["success"] is False and "adviser" in first["error"]
    _confirm_tax_rate(c, "ITA3-COMPUTER")
    assert ui.action(c.acc1, model=run._name, ids=run.ids, method="action_compute")["success"]
    assert run.state == "computed" and run.total_amount > 0
    assert ui.action(c.acc1, model=run._name, ids=run.ids, method="action_post")["success"]
    # the tax book is reachable, and is a memo: no journal entry
    assert run.state == "posted" and not run.move_ids
    assert asset.tax_accumulated == run.total_amount and asset.accumulated_depreciation == 0.0


def test_m49_11_book_run_from_the_form_posts_to_the_gl(c, ui):  # noqa: F811
    asset = seam_asset(c)
    res = ui.write(
        c.acc1,
        model="fix.asset.depreciation.run",
        record_id=False,
        values={"book": "book", "period_start": "2026-01-01", "asset_ids": [asset.id]},
    )
    run = c.env["fix.asset.depreciation.run"].browse(res["id"])
    ui.action(c.acc1, model=run._name, ids=run.ids, method="action_compute")
    assert ui.action(c.acc1, model=run._name, ids=run.ids, method="action_post")["success"]
    assert run.move_ids and balance(c, c.a["expense"]) == 10000.0


def test_m49_11_monthly_job_prepares_and_never_posts(c):  # noqa: F811
    cron = c.env.ref("cd_fixed_asset_ext.ir_cron_prepare_depreciation_runs").sudo()
    assert cron.active and "_cron_prepare_monthly_runs" in cron.code
    assert (cron.interval_type, cron.interval_number) == ("months", 1)
    asset = seam_asset(c, purchase=date(2026, 1, 15))
    Run = c.env["fix.asset.depreciation.run"].sudo()
    Move = c.env["account.move"].sudo()
    moves_before = Move.search_count([("company_id", "=", c.co.id)])
    Run._cron_prepare_monthly_runs()
    runs = Run.search([("company_id", "=", c.co.id)])
    book = runs.filtered(lambda r: r.book == "book")
    tax = runs.filtered(lambda r: r.book == "tax")
    assert len(book) == 1 and len(tax) == 1
    assert book.state == "computed" and asset in book.line_ids.asset_id
    assert "posted" not in runs.mapped("state")
    assert Move.search_count([("company_id", "=", c.co.id)]) == moves_before, "the job posted"
    assert not asset.depreciation_line_ids.filtered(lambda ln: ln.state == "posted")
    # the tax rate awaiting the adviser leaves a draft that says why
    rate = c.env["fix.tax.rate"].find_rate(
        "depreciation", "ITA3-PLANT", fields.Date.context_today(c.env.user), c.co
    )
    if rate.verify_with_adviser:
        assert tax.state == "draft" and "adviser" in tax.note
    # idempotent per company, book and month
    Run._cron_prepare_monthly_runs()
    assert Run.search_count([("company_id", "=", c.co.id)]) == 2
    # and a person posts it
    book.with_user(c.acc1).with_context(allowed_company_ids=c.co.ids).action_post()
    assert book.state == "posted" and book.move_ids


def test_m49_11_monthly_job_skips_a_company_with_nothing_to_depreciate(c):  # noqa: F811
    Run = c.env["fix.asset.depreciation.run"].sudo()
    Run._cron_prepare_monthly_runs()
    assert not Run.search([("company_id", "=", c.co.id)])


# =========================================================== M49-2/-3
def test_m49_2_category_form_offers_every_posting_account(c, ui, m49_js):  # noqa: F811
    fields_ = offered(m49_js, "M49-form-category")
    for name in (*POSTING_ACCOUNTS, "journal_id"):
        assert name in fields_ and not fields_[name].get("readonly"), name
        assert name in c.env["fix.asset.category"]._fields
    values = {
        "name": "From the form",
        "code": "FORM1",
        "useful_life_months": 12,
        "journal_id": c.journal.id,
        "asset_account_id": c.a["asset"].id,
        "accumulated_account_id": c.a["accum"].id,
        "expense_account_id": c.a["expense"].id,
        "cwip_account_id": c.a["cwip"].id,
        "revaluation_surplus_account_id": c.a["surplus"].id,
        "impairment_account_id": c.a["impair"].id,
        "gain_account_id": c.a["gain"].id,
        "loss_account_id": c.a["loss"].id,
    }
    # the mapping is an accounting manager's: an accountant is refused
    assert "error" in ui.write(c.acc1, model="fix.asset.category", record_id=False, values=values)
    res = ui.write(c.mgr, model="fix.asset.category", record_id=False, values=values)
    assert "error" not in res, res
    category = c.env["fix.asset.category"].browse(res["id"])
    for name in POSTING_ACCOUNTS:
        assert category[name], name
    # and the posting that refused now goes through
    asset = seam_asset(c, cat=category)
    dep_run(c, asset, 1)
    assert balance(c, c.a["expense"]) == 10000.0


def test_m49_3_book_posted_cost_from_the_surface(c, ui, m49_js):  # noqa: F811
    action = actions(m49_js, "M49-cwip")["action_book_posted_cost"]
    assert action["kwarg"] == "entries" and action["ask"]
    assert "action_book_posted_cost" in m49_surface.SURFACES["fix.cwip.entry"]["actions"]
    _b, req = approved_capex(c, 100000.0)
    cw = c.env["fix.cwip.entry"].browse(req.with_user(c.acc1).action_create_cwip()["cwip_ids"])
    bill = _post(
        c, [(c.a["cwip"], 60000.0, 0.0, "capital bill"), (c.a["payable"], 0.0, 60000.0, "AP")]
    )
    # a wrong number books nothing and names what is waiting
    wrong = ui.action(
        c.acc1,
        model=cw._name,
        ids=cw.ids,
        method="action_book_posted_cost",
        kwargs={"entries": "X"},
    )
    assert wrong["success"] is False and bill.name in wrong["error"]
    res = ui.action(
        c.acc1,
        model=cw._name,
        ids=cw.ids,
        method="action_book_posted_cost",
        kwargs={"entries": bill.name},
    )
    assert res["success"], res
    assert cw.amount == 60000.0
    # booked once
    again = ui.action(
        c.acc1,
        model=cw._name,
        ids=cw.ids,
        method="action_book_posted_cost",
        kwargs={"entries": bill.name},
    )
    assert again["success"] is False and cw.amount == 60000.0
    # a plain user does not book
    assert not ui.action(
        c.plain,
        model=cw._name,
        ids=cw.ids,
        method="action_book_posted_cost",
        kwargs={"entries": bill.name},
    )["success"]


# =========================================================== M49-4
def test_m49_4_lease_from_the_form_activates(c, ui, m49_js):  # noqa: F811
    fields_ = offered(m49_js, "M49-form-lease")
    for name in (
        "ibr_percent",
        "liability_account_id",
        "interest_account_id",
        "payment_account_id",
    ):
        assert name in fields_ and not fields_[name].get("readonly"), name
    assert fields_["rou_amount"]["readonly"] and fields_["state"]["readonly"]
    values = {
        "name": "Mirpur branch",
        "category_id": c.cat_rou.id,
        "operating_unit_id": c.ou.id,
        "commencement_date": "2026-01-01",
        "term_months": 12,
        "payment_amount": 10000.0,
        "payment_timing": "arrears",
        "ibr_percent": 12.0,
        "exemption": "none",
    }
    res = ui.write(c.acc1, model="fix.lease", record_id=False, values=values)
    assert "error" not in res, res
    lease = c.env["fix.lease"].browse(res["id"])
    # the refusal names what the form now offers
    first = ui.action(c.acc1, model=lease._name, ids=lease.ids, method="action_activate")
    assert first["success"] is False and "Lease Liability Account" in first["error"]
    saved = ui.write(
        c.acc1,
        model=lease._name,
        record_id=lease.id,
        values={
            "liability_account_id": c.a["liability"].id,
            "interest_account_id": c.a["interest"].id,
            "payment_account_id": c.a["rent"].id,
        },
    )
    assert "error" not in saved, saved
    done = ui.action(c.acc1, model=lease._name, ids=lease.ids, method="action_activate")
    assert done["success"], done
    assert lease.state == "active" and lease.rou_amount > 0 and lease.move_id.state == "posted"
    assert lease.ibr_percent == 12.0 and balance(c, c.a["liability"]) == -lease.initial_liability


# =========================================================== M49-9
def test_m49_9_valuer_report_uploaded_on_the_form_lets_it_submit(c, ui, m49_js):  # noqa: F811
    fields_ = offered(m49_js, "M49-form-revaluation")
    assert fields_["valuer_report_file"]["type"] == "binary"
    assert not fields_["valuer_report_file"].get("readonly")
    assert fields_["valuer_report_names"]["readonly"]
    asset = seam_asset(c)
    res = ui.write(
        c.acc1,
        model="fix.asset.revaluation",
        record_id=False,
        values={
            "asset_id": asset.id,
            "kind": "revaluation",
            "date": str(date(2026, 3, 1)),
            "new_value": 150000.0,
            "basis": "Independent valuer, market approach",
        },
    )
    assert "error" not in res, res
    reval = c.env["fix.asset.revaluation"].browse(res["id"])
    first = ui.action(c.acc1, model=reval._name, ids=reval.ids, method="action_submit")
    assert first["success"] is False and "valuer" in first["error"]
    saved = ui.write(
        c.acc1,
        model=reval._name,
        record_id=reval.id,
        values={"valuer_report_file": PDF, "valuer_report_filename": "valuer-2026.pdf"},
    )
    assert "error" not in saved, saved
    report = reval.valuer_report_ids
    assert report.name == "valuer-2026.pdf" and reval.valuer_report_names == "valuer-2026.pdf"
    assert base64.b64decode(report.sudo().datas).startswith(b"%PDF-1.4")
    assert (report.sudo().res_model, report.sudo().res_id) == (reval._name, reval.id)
    # on the next request the upload field reads back empty, so a later save
    # re-posts nothing
    reval.invalidate_recordset(["valuer_report_file"])
    assert not reval.valuer_report_file
    assert "error" not in ui.write(
        c.acc1, model=reval._name, record_id=reval.id, values={"basis": "Revised basis"}
    )
    assert len(reval.valuer_report_ids) == 1
    assert ui.action(c.acc1, model=reval._name, ids=reval.ids, method="action_submit")["success"]
    assert reval.state == "submitted"
    # the evidence is what the approval sees: no adding to it afterwards
    late = ui.write(
        c.acc1, model=reval._name, record_id=reval.id, values={"valuer_report_file": PDF}
    )
    assert len(reval.valuer_report_ids) == 1 and "error" not in late


# =========================================================== M49-10
def _draft_po(c, amount, vendor=None):  # noqa: F811
    partner = vendor or c.env["res.partner"].create({"name": "A08M49 supplier"})
    product = c.env["product.product"].create({"name": "A08M49 server"})
    return (
        c.env["fix.purchase.order"]
        .sudo()
        .create(
            {
                "company_id": c.co.id,
                "operating_unit_id": c.ou.id,
                "vendor_id": partner.id,
                "line_ids": [
                    (0, 0, {"product_id": product.id, "qty_ordered": 1, "unit_price": amount})
                ],
            }
        )
    )


def test_m49_10_link_a_purchase_order_from_the_capex_screen(c, ui, m49_js):  # noqa: F811
    action = actions(m49_js, "M49-requests")["action_link_purchase_order"]
    assert action["kwarg"] == "order" and action["ask"]
    assert "ordered_amount" in m49_js["screens"]["M49-requests"]["cols"]
    _b, req = approved_capex(c, 100000.0)
    po = _draft_po(c, 80000.0)
    method = "action_link_purchase_order"
    # a plain user, an unknown order and an empty prompt are refused
    assert not ui.action(
        c.plain, model=req._name, ids=req.ids, method=method, kwargs={"order": po.name}
    )["success"]
    assert not ui.action(
        c.acc1, model=req._name, ids=req.ids, method=method, kwargs={"order": "NOPE"}
    )["success"]
    assert not ui.action(c.acc1, model=req._name, ids=req.ids, method=method)["success"]
    res = ui.action(c.acc1, model=req._name, ids=req.ids, method=method, kwargs={"order": po.name})
    assert res["success"], res
    assert res["result"]["note"]
    assert po.is_capex is True and po.capex_request_id == req and req.ordered_amount == 80000.0
    # the ceiling applies at once: a second order past the approved amount does not link
    over = _draft_po(c, 50000.0)
    refused_over = ui.action(
        c.acc1, model=req._name, ids=req.ids, method=method, kwargs={"order": over.name}
    )
    assert refused_over["success"] is False and "above its approved" in refused_over["error"]
    assert not over.capex_request_id
    # a request not yet approved does not take an order
    b2 = budget(c, by=c.mgr, approve_by=c.mgr2)
    draft = request(c, b2, amount=1000.0)
    third = _draft_po(c, 500.0)
    assert not ui.action(
        c.acc1, model=draft._name, ids=draft.ids, method=method, kwargs={"order": third.name}
    )["success"]


def _posted_disposal(c, asset, **kw):  # noqa: F811
    disposal = _disposal(c, asset, **kw)
    disposal.with_user(c.acc1).action_submit()
    _approve(disposal, c.t4)
    disposal.with_user(c.acc2).action_post()
    return disposal


def test_m49_10_disposal_routed_to_m18_opens_a_collection(c, m49_js):  # noqa: F811
    assert not offered(m49_js, "M49-form-disposal")["ewaste_route"].get("readonly")
    asset = seam_asset(c)
    disposal = _posted_disposal(c, asset, ewaste_route=True)
    xmlid = "cd_fixed_asset_ext.consumer_asset_disposed_m18"
    relay(c, "asset.disposed", "fix.fixed.asset", asset.id, xmlid)
    collection = c.env["fix.ewaste.collection"].sudo().browse(disposal.ewaste_collection_res_id)
    assert collection.exists() and collection.state == "collected"
    assert (collection.source_model, collection.source_res_id) == (disposal._name, disposal.id)
    assert collection.customer_id == c.co.partner_id and collection.company_id == c.co
    assert disposal.ewaste_collection_ref == collection.name
    # a replay opens no second collection
    relay(c, "asset.disposed", "fix.fixed.asset", asset.id, xmlid)
    assert (
        c.env["fix.ewaste.collection"]
        .sudo()
        .search_count([("source_model", "=", disposal._name), ("source_res_id", "=", disposal.id)])
        == 1
    )


def test_m49_10_disposal_not_routed_stays_out_of_m18(c):  # noqa: F811
    asset = seam_asset(c)
    disposal = _posted_disposal(c, asset)
    relay(
        c,
        "asset.disposed",
        "fix.fixed.asset",
        asset.id,
        "cd_fixed_asset_ext.consumer_asset_disposed_m18",
    )
    assert not disposal.ewaste_collection_ref
    assert not (
        c.env["fix.ewaste.collection"]
        .sudo()
        .search_count([("source_model", "=", disposal._name), ("source_res_id", "=", disposal.id)])
    )


def test_m49_10_m18_route_is_pinned_by_the_approval(c):  # noqa: F811
    asset = seam_asset(c)
    disposal = _disposal(c, asset, ewaste_route=False)
    disposal.with_user(c.acc1).action_submit()
    _approve(disposal, c.t4)
    assert disposal.state == "approved"
    disposal.with_user(c.acc1).write({"ewaste_route": True})
    assert disposal.state == "draft"


def test_m49_10_consumer_refuses_a_direct_call(c):  # noqa: F811
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        c.env["fix.asset.disposal"].with_user(c.mgr).consume_asset_disposed_m18({"aggregate_id": 1})


def _ready_close(c, day=date(2026, 1, 31)):  # noqa: F811
    close = c.env["fix.period.close"].sudo().create({"company_id": c.co.id, "period_end": day})
    close._guarded().write({"state": "ready_to_close"})
    return close.with_user(c.mgr).with_context(allowed_company_ids=c.co.ids)


def test_m49_10_period_does_not_close_while_the_register_disagrees(c):  # noqa: F811
    seam_asset(c)
    close = _ready_close(c)
    # in agreement: the gate passes
    assert close._fix_check_register_reconciled() is True
    # a journal on the asset account with no register consequence
    _post(c, [(c.a["asset"], 500.0, 0.0, "stray"), (c.a["payable"], 0.0, 500.0, "stray")])
    with pytest.raises(UserError, match="does not agree with the ledger"), c.env.cr.savepoint():
        close.action_close()
    assert close.state == "ready_to_close"
    # inside the tolerance it passes; the key widens it
    icp = c.env["ir.config_parameter"].sudo()
    icp.set_param("cd_fixed_asset_ext.close_gate_tolerance", "500")
    assert close._fix_check_register_reconciled() is True
    icp.set_param("cd_fixed_asset_ext.close_gate_tolerance", "1")
    with pytest.raises(UserError), c.env.cr.savepoint():
        close._fix_check_register_reconciled()
    # 0 switches the gate off
    icp.set_param("cd_fixed_asset_ext.close_gate_register_gl", "0")
    assert close._fix_check_register_reconciled() is True


# =========================================================== M49-8
def test_m49_8_disposal_records_the_tax_balancing_memo(c, m49_js):  # noqa: F811
    assert offered(m49_js, "M49-form-disposal")["tax_balancing"]["readonly"]
    _confirm_tax_rate(c, "ITA3-PLANT")
    asset = seam_asset(c, gross=120000.0, purchase=date(2026, 1, 15))
    dep_run(c, asset, 1, book="tax")
    wdv = asset.tax_wdv
    assert 0 < wdv < 120000.0
    charge = _posted_disposal(c, asset, proceeds=wdv + 10000.0)
    assert charge.tax_wdv == wdv and charge.tax_balancing == 10000.0
    # a memo: the entry carries the book figures only
    assert sum(charge.move_id.line_ids.mapped("debit")) == sum(
        charge.move_id.line_ids.mapped("credit")
    )
    assert charge.gain_loss == round(charge.proceeds - charge.nbv, 2)
    # an allowance when the proceeds fall short
    other = seam_asset(c, gross=120000.0, purchase=date(2026, 1, 15))
    dep_run(c, other, 1, book="tax")
    allowance = _posted_disposal(c, other, proceeds=other.tax_wdv - 2000.0)
    assert allowance.tax_balancing == -2000.0
    # outside the tax book (right-of-use): nothing to balance
    rou = seam_asset(c, cat=c.cat_rou, gross=60000.0)
    outside = _posted_disposal(c, rou, proceeds=1000.0)
    assert outside.tax_wdv == 0.0 and outside.tax_balancing == 0.0
    # and the report shows it
    report = m49_surface.disposal_gains(c.as_(c.acc1), date_from="2020-01-01", date_to="2099-12-31")
    row = next(r for r in report["rows"] if r["reference"] == charge.name)
    assert row["tax_balancing"] == 10000.0 and "tax_balancing" in report["cols"]


def test_m49_8_legacy_rate_table_is_read_only_and_has_no_form(c, ui, m49_js):  # noqa: F811
    assert "M49-form-taxrate" not in m49_js["screens"]
    assert "fix.asset.tax.rate" not in m49_js["chips"]["M49:__by_model__"]
    assert m49_js["screens"]["M49-taxrates"]["report"] == "tax_depreciation_rates"
    Rate = c.as_(c.mgr)["fix.asset.tax.rate"]
    row = Rate.sudo().search([], limit=1)
    assert row, "the seeded rows stay as a record"
    for attempt in (
        lambda: row.with_user(c.mgr).write({"rate_percent": 99.0}),
        lambda: row.with_user(c.mgr).unlink(),
        lambda: Rate.create(
            {"code": "X", "name": "X", "rate_percent": 1.0, "date_from": "2026-01-01"}
        ),
    ):
        with pytest.raises(UserError, match="M51"), c.env.cr.savepoint():
            attempt()
    assert row.rate_percent != 99.0


# =========================================================== M49-1
def test_m49_1_scan_from_the_surface(c, ui, m49_js):  # noqa: F811
    action = actions(m49_js, "M49-verify")["action_record_scan"]
    assert {a["kwarg"] for a in action["asks"]} == {"tag", "branch"}
    asset = seam_asset(c, operating_unit_id=c.ou.id)
    moved = seam_asset(c, operating_unit_id=c.ou.id)
    Campaign = c.as_(c.acc1)["fix.asset.verification.campaign"]
    campaign = Campaign.create({"name": "Nov count", "responsible_id": c.acc1.id})
    campaign.action_start()
    method = "action_record_scan"
    model = campaign._name
    # found: the counter scans (hand-marking is refused to him), at the expected branch
    res = ui.action(
        c.acc1,
        model=model,
        ids=campaign.ids,
        method=method,
        kwargs={"tag": asset.code, "branch": ""},
    )
    assert res["success"], res
    assert res["result"]["result"] == "found" and asset.code in res["result"]["note"]
    line = campaign.line_ids.filtered(lambda ln: ln.asset_id == asset)
    assert line.result == "found" and line.scanned_at and not line.corrected_by_id
    # found elsewhere: the branch is typed by its code
    res = ui.action(
        c.acc1,
        model=model,
        ids=campaign.ids,
        method=method,
        kwargs={"tag": moved.code, "branch": c.ou2.code},
    )
    assert res["result"]["result"] == "misplaced"
    # a tag the register does not know is a find, not an error
    res = ui.action(
        c.acc1, model=model, ids=campaign.ids, method=method, kwargs={"tag": "NO-SUCH-TAG"}
    )
    assert res["result"]["result"] == "unregistered" and campaign.unregistered_count == 1
    # an unknown branch and an empty tag are refused; a plain user does not scan
    assert not ui.action(
        c.acc1, model=model, ids=campaign.ids, method=method, kwargs={"tag": "T", "branch": "ZZ"}
    )["success"]
    assert not ui.action(c.acc1, model=model, ids=campaign.ids, method=method)["success"]
    assert not ui.action(
        c.plain, model=model, ids=campaign.ids, method=method, kwargs={"tag": asset.code}
    )["success"]
    campaign.action_close()
    assert campaign.missing_count == 0


def test_m49_9_attachment_made_directly_still_counts(c):  # noqa: F811
    reval = _reval(c, seam_asset(c))
    reval.with_user(c.acc1).action_submit()
    assert reval.state == "submitted"
