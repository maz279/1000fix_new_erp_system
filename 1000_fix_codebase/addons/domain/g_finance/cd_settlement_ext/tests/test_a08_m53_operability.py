# A08 finish, M53: a person can do the whole job on screen, and the daily
# revenue job posts nothing it has no contract for. Every test walks the real
# path as a NON-ADMIN user holding the real finance role, through the P03
# endpoints the workspace calls, against the screens evaluated from the registry
# (static/src/a08/m53.js), never its text.
import json
import re
import shutil
import subprocess
import types
import uuid
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_settlement_ext.tests.test_a08_m53_controls import (
    _commissioned_order,
    accrued_referral,
    as_,
    bank_confirm,
    c,  # noqa: F401 - fixture
    declare_marketplace_agent,
    inbox_approve,
    lines,
    paid_invoice,
    prepared_run,
    referral,
    sub,
    system_row,
)
from odoo.exceptions import AccessError, UserError

pytestmark = [pytest.mark.financial]

PORTAL = Path(__file__).resolve().parents[4] / "platform" / "cd_p03_portal"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')
LEGACY_START, LEGACY_END = date(2026, 6, 30), date(2027, 6, 30)


@pytest.fixture(scope="module")
def screens(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    src = PORTAL / "static" / "src"
    tmp = tmp_path_factory.mktemp("p03_m53_op")
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
        ".filter(([k]) => k.startsWith('M53'))), chips: M.P03_FORM_CHIPS,"
        " nav: M.P03_MODULES.M53.groups.flatMap((g) => g.screens.map((s) => s.id))}));\n",
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=60
    )
    return json.loads(out.stdout)


@pytest.fixture
def p03(c):  # noqa: F811
    from odoo.addons.cd_p03_portal.controllers import p03_generic_api as g

    holder = types.SimpleNamespace(env=None)
    old = g.request
    g.request = holder
    ctl = g.P03GenericApiController()

    def bind(name):
        f = getattr(g.P03GenericApiController, name)
        f = getattr(f, "original_endpoint", f)
        return lambda **kw: f(ctl, **kw)

    try:
        yield types.SimpleNamespace(
            as_user=lambda user: setattr(holder, "env", as_(c, user)),
            action=bind("model_action"),
            form=bind("model_form"),
            records=bind("model_records"),
        )
    finally:
        g.request = old


def form_fields_of(screens, sid):
    return [f for s in screens["screens"][sid]["sections"] for f in s["fields"]]


def assert_operable(p03, screens, list_id, form_id, user, editable, actions):
    cfg = screens["screens"][list_id]
    assert list_id in screens["nav"]
    if form_id:
        assert screens["chips"]["M53:__by_screen__"][list_id] == form_id
    assert set(actions) <= {a["m"] for a in cfg.get("actions", [])}
    from odoo.addons.cd_p03_portal.controllers.a08 import m53

    assert set(actions) <= m53.SURFACES[cfg["model"]]["actions"]
    p03.as_user(user)
    listed = p03.records(model=cfg["model"], cols=cfg["cols"])
    assert "error" not in listed, listed
    assert set(cfg["cols"]) <= set(listed["labels"]), "the endpoint dropped a column"
    if form_id:
        res = p03.form(model=cfg["model"], fields=form_fields_of(screens, form_id))
        assert "error" not in res, res
        offered = {f["name"]: f for f in res["fields"]}
        assert {f["name"] for f in form_fields_of(screens, form_id)} == set(offered)
        for name in editable:
            assert not offered[name]["readonly"], "%s is not an input" % name


def _legacy_schedule(c, sub_rec):  # noqa: F811
    """A schedule as the live copy holds it: active, 1,200,000, no contract, no
    CFO approval, on a subscription billing a small monthly amount. The state
    is staged directly: the model no longer lets one be born like this."""
    schedule = c.env["fix.revenue.schedule"].create(
        {
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
            "source_model": "fix.subscription",
            "source_id": sub_rec.id,
            "description": "Straight-line AMC recognition",
            "total_amount": 1200000.0,
            "start_date": LEGACY_START,
            "end_date": LEGACY_END,
        }
    )
    c.env.flush_all()  # the pending "held" must not overwrite the staging below
    c.env.cr.execute(
        "UPDATE fix_revenue_schedule SET state = 'active', hold_reason = NULL WHERE id = %s",
        (schedule.id,),
    )
    c.env.invalidate_all()
    return schedule


def _gl_counts(c):  # noqa: F811
    moves = c.env["account.move"].search_count([("company_id", "=", c.company.id)])
    rows = c.env["fix.revenue.recognition.line"].search_count([("company_id", "=", c.company.id)])
    return moves, rows


def _other_schedules_off(c):  # noqa: F811
    """The cron is estate-wide: leave only this test's company in scope."""
    c.env["fix.revenue.schedule"].search(
        [("company_id", "!=", c.company.id), ("state", "=", "active")]
    ).sudo()._guarded().write({"state": "cancelled"})


# ================================================================= M53-6 (the blocker)
def test_m53_6_cron_posts_nothing_from_the_legacy_schedules(c):  # noqa: F811
    _other_schedules_off(c)
    s4 = sub(c, c.acct, recurring_amount=2500.0)
    s3 = sub(c, c.acct, recurring_amount=1999.0)
    legacy = _legacy_schedule(c, s4) | _legacy_schedule(c, s3)
    # the job COULD post: the accounts exist, and these are the live figures
    today = fields.Date.context_today(c.env["fix.subscription"])
    elapsed = (today - LEGACY_START).days
    would_post = 2 * round(1200000.0 * elapsed / (LEGACY_END - LEGACY_START).days, 2)
    assert would_post > 800000.0
    before = _gl_counts(c)
    c.env["fix.revenue.schedule"]._cron_recognize()
    assert _gl_counts(c) == before, "the cron posted revenue with no contract behind it"
    assert set(legacy.mapped("state")) == {"held"}
    assert all(legacy.mapped("hold_reason"))
    assert sum(legacy.mapped("recognized_amount")) == 0.0
    assert sum(legacy.mapped("deferred_balance")) == 0.0
    # and a later run stays silent
    c.env["fix.revenue.schedule"]._cron_recognize()
    assert _gl_counts(c) == before


def test_m53_6_without_the_gate_the_same_cron_posts_the_live_figure(c):  # noqa: F811
    """The proof the test above can fail: the same rows and the same job, the
    gate removed, post the BDT 854,795 (the figure of the day) to the GL."""
    _other_schedules_off(c)
    legacy = _legacy_schedule(c, sub(c, c.acct, recurring_amount=2500.0)) | _legacy_schedule(
        c, sub(c, c.acct, recurring_amount=1999.0)
    )
    Model = c.env["fix.revenue.schedule"]
    today = fields.Date.context_today(Model)
    each = round(1200000.0 * (today - LEGACY_START).days / (LEGACY_END - LEGACY_START).days, 2)
    with mock.patch.object(type(Model), "_recognition_refusal", return_value=None):
        Model._cron_recognize()
    assert legacy.mapped("recognized_amount") == [each, each]
    assert len(legacy.mapped("line_ids.move_id")) == 2


def test_m53_6_same_cron_does_post_a_schedule_with_a_contract(c):  # noqa: F811
    """The refusal above is not a dead cron: an obligation's schedule still posts."""
    _other_schedules_off(c)
    today = fields.Date.context_today(c.env["fix.subscription"])
    s = sub(
        c,
        c.acct,
        contract_value=36500.0,
        start_date=today - timedelta(days=100),
        contract_end_date=today + timedelta(days=265),
    )
    ob = as_(c, c.acct)["fix.performance.obligation"].create(
        {
            "subscription_id": s.id,
            "name": "AMC",
            "standalone_price": 36500.0,
            "start_date": s.start_date,
            "end_date": s.contract_end_date,
        }
    )
    s.with_user(c.acct).action_allocate_price()
    ob.with_user(c.acct).action_create_schedule()
    schedule = ob.schedule_id
    assert schedule.subscription_id == s and schedule.state == "active"
    assert c.env["fix.revenue.schedule"]._cron_recognize() == 1
    assert schedule.recognized_amount == 10000.0  # 100/365 of 36,500
    assert lines(schedule.line_ids.move_id) == sorted(
        [("212000", 10000.0, 0.0), ("400000", 0.0, 10000.0)]
    )


def test_m53_6_upgrade_hook_holds_without_posting(c):  # noqa: F811
    _other_schedules_off(c)
    legacy = _legacy_schedule(c, sub(c, c.acct, recurring_amount=2500.0))
    before = _gl_counts(c)
    held = c.env["fix.revenue.schedule"]._hold_legacy_schedules()
    assert legacy in held and legacy.state == "held" and _gl_counts(c) == before


def test_m53_6_orm_create_naming_a_source_is_refused(c):  # noqa: F811
    s = sub(c, c.acct, recurring_amount=2500.0)
    with pytest.raises(UserError, match="never typed against"):
        as_(c, c.acct)["fix.revenue.schedule"].create(
            {
                "company_id": c.company.id,
                "operating_unit_id": c.ou.id,
                "source_model": "fix.subscription",
                "source_id": s.id,
                "description": "typed",
                "total_amount": 1200000.0,
                "start_date": LEGACY_START,
                "end_date": LEGACY_END,
            }
        )


def test_m53_6_a_trusted_create_with_no_contract_is_born_held(c):  # noqa: F811
    s = sub(c, c.acct, recurring_amount=2500.0)
    schedule = c.env["fix.revenue.schedule"].create_from_deferral(
        "fix.subscription", s.id, "AMC", 1200000.0, LEGACY_START, LEGACY_END
    )
    assert schedule.state == "held" and "no contract value" in schedule.hold_reason


def test_m53_6_total_above_the_contract_value_is_held_even_with_a_contract(c):  # noqa: F811
    s = sub(
        c, c.acct, contract_value=100000.0, contract_end_date=date.today() + timedelta(days=300)
    )
    over = c.env["fix.revenue.schedule"].create_from_deferral(
        "fix.subscription",
        s.id,
        "too much",
        100000.01,
        date.today(),
        date.today() + timedelta(days=300),
    )
    assert over.state == "held" and "above the contract value" in over.hold_reason
    s2 = sub(
        c, c.acct, contract_value=100000.0, contract_end_date=date.today() + timedelta(days=300)
    )
    ok = c.env["fix.revenue.schedule"].create_from_deferral(
        "fix.subscription",
        s2.id,
        "fits",
        100000.0,
        date.today(),
        date.today() + timedelta(days=300),
    )
    assert ok.state == "active"


def test_m53_6_an_approved_looking_manual_schedule_with_no_cfo_does_not_post(c):  # noqa: F811
    _other_schedules_off(c)
    s = as_(c, c.acct)["fix.revenue.schedule"].create(
        {
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
            "description": "manual",
            "total_amount": 5000.0,
            "start_date": date.today() - timedelta(days=30),
            "end_date": date.today() + timedelta(days=30),
            "subscription_id": sub(c, c.acct, contract_value=100000.0).id,
            "manual_reason": "x",
            "evidence_ref": "y",
        }
    )
    c.env.flush_all()
    c.env.cr.execute("UPDATE fix_revenue_schedule SET state = 'active' WHERE id = %s", (s.id,))
    c.env.invalidate_all()
    before = _gl_counts(c)
    with pytest.raises(UserError, match="no CFO approval"):
        s.with_user(c.acct).action_recognize_period()
    c.env["fix.revenue.schedule"]._cron_recognize()
    assert _gl_counts(c) == before and s.state == "held"


def test_m53_6_recognise_button_refuses_a_held_or_unbased_schedule(c, p03):  # noqa: F811
    legacy = _legacy_schedule(c, sub(c, c.acct, recurring_amount=2500.0))
    before = _gl_counts(c)
    p03.as_user(c.acct)
    res = p03.action(
        model="fix.revenue.schedule", ids=[legacy.id], method="action_recognize_period"
    )
    assert res["success"] is False and "no contract value" in res["error"]
    legacy._hold_unbased()
    res = p03.action(
        model="fix.revenue.schedule", ids=[legacy.id], method="action_recognize_period"
    )
    assert res["success"] is False and "held" in res["error"]
    assert _gl_counts(c) == before


def test_m53_6_held_screen_cancel_is_a_person_with_a_reason(c, p03, screens):  # noqa: F811
    assert_operable(
        p03,
        screens,
        "M53-schedules-held",
        "M53-form-schedule",
        c.acct,
        (),
        ["action_cancel_held", "action_reopen_as_manual"],
    )
    legacy = _legacy_schedule(c, sub(c, c.acct, recurring_amount=2500.0))
    legacy._hold_unbased()
    p03.as_user(c.plain)
    res = p03.action(
        model="fix.revenue.schedule",
        ids=[legacy.id],
        method="action_cancel_held",
        kwargs={"reason": "no"},
    )
    assert res["success"] is False and legacy.state == "held"
    p03.as_user(c.acct)
    res = p03.action(
        model="fix.revenue.schedule",
        ids=[legacy.id],
        method="action_cancel_held",
        kwargs={"reason": ""},
    )
    assert res["success"] is False and legacy.state == "held"
    res = p03.action(
        model="fix.revenue.schedule",
        ids=[legacy.id],
        method="action_cancel_held",
        kwargs={"reason": "seed data, no such contract"},
    )
    assert res["success"] and legacy.state == "cancelled" and legacy.deferred_balance == 0.0
    assert legacy.cancelled_date


def test_m53_6_held_reopened_as_manual_runs_the_cfo_route(c):  # noqa: F811
    s = sub(c, c.acct, recurring_amount=2500.0, contract_value=30000.0)
    # a held schedule with no value behind it at the time
    legacy = _legacy_schedule(c, s)
    legacy._hold_unbased()
    assert legacy.state == "held"
    legacy.with_user(c.acct).action_reopen_as_manual()
    assert legacy.state == "draft" and legacy.source_model == "manual"
    assert legacy.subscription_id == s and not legacy.hold_reason
    with pytest.raises(UserError, match="exceeds|reason and evidence"):
        legacy.with_user(c.acct).action_request_cfo_approval()
    legacy.with_user(c.acct).write(
        {"total_amount": 30000.0, "manual_reason": "contract found", "evidence_ref": "AMC-77"}
    )
    legacy.with_user(c.acct).action_request_cfo_approval()
    with pytest.raises(UserError):
        legacy.with_user(c.acct).action_recognize_period()
    inbox_approve(c, legacy, c.cfo)
    assert legacy.state == "active" and legacy.dofa_approved_by == c.cfo
    legacy.with_user(c.acct).action_recognize_period()
    assert legacy.recognized_amount > 0


def test_m53_6_source_fields_cannot_be_rewritten(c):  # noqa: F811
    s = as_(c, c.acct)["fix.revenue.schedule"].create(
        {
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
            "description": "manual",
            "total_amount": 5000.0,
            "start_date": date.today(),
            "end_date": date.today() + timedelta(days=30),
        }
    )
    with pytest.raises(UserError, match="set by the system"):
        s.write({"source_model": "fix.subscription"})


def test_m53_6_cancelling_a_contract_does_not_trip_on_an_unbased_schedule(c):  # noqa: F811
    s = sub(c, c.acct, contract_value=12000.0, contract_end_date=date.today() + timedelta(days=300))
    ob = as_(c, c.acct)["fix.performance.obligation"].create(
        {
            "subscription_id": s.id,
            "name": "AMC",
            "standalone_price": 12000.0,
            "start_date": s.start_date,
            "end_date": s.contract_end_date,
        }
    )
    s.with_user(c.acct).action_allocate_price()
    ob.with_user(c.acct).action_create_schedule()
    schedule = ob.schedule_id
    c.env.flush_all()
    c.env.cr.execute(
        "UPDATE fix_revenue_schedule SET total_amount = 99999 WHERE id = %s", (schedule.id,)
    )
    c.env.invalidate_all()
    s.with_user(c.acct).action_request_refund()
    assert s.state == "cancelled" and schedule.state == "cancelled" and not schedule.line_ids


# ================================================================= M53-15 / -4: one row per earning
def test_m53_15_commission_earned_has_one_active_consumer(c):  # noqa: F811
    rows = c.env["fix.event.consumer"].search([("event_type", "=", "commission.earned")])
    assert rows.mapped("model") == ["fix.a04.finance.consumers"]
    assert rows.active


def test_m53_15_an_order_earns_one_row_with_its_order_and_scheme(c):  # noqa: F811
    scheme = c.env["fix.commission.scheme"].create(
        {
            "name": "Seller 12%",
            "scheme_type": "seller",
            "commission_rate": 0.12,
            "tds_rate": 0.10,
            "date_from": date(2025, 7, 1),
            "company_id": c.company.id,
        }
    )
    _seller, order = _commissioned_order(c)
    event = {"aggregate": "fix.marketplace.order", "aggregate_id": order.id, "payload": {}}
    Cons = c.env["fix.a04.finance.consumers"]
    out = Cons.consume_commission_earned(event)
    row = c.env["fix.commission.ledger"].browse(out["id"])
    assert out["created"] and row.marketplace_order_id == order and row.scheme_id == scheme
    assert row.commission_rate == 0.12 and row.tds_amount > 0
    # the replay, through either door, finds the same row
    assert Cons.consume_commission_earned(event)["created"] is False
    assert c.env["fix.commission.ledger"].consume_commission_earned(event)["id"] == row.id
    assert (
        c.env["fix.commission.ledger"].search_count([("marketplace_order_id", "=", order.id)]) == 1
    )
    # and finance can accrue it (a row with no order link could not)
    declare_marketplace_agent(c.env, c.company)
    row.with_user(c.acct).action_post_to_gl()
    assert row.state == "accrued" and row.gl_move_id


def test_m53_4_accrue_uses_the_row_the_consumer_raised(c):  # noqa: F811
    inv = paid_invoice(c)
    r = referral(c)
    r.with_user(c.sales).action_convert(invoice=inv)
    r.with_user(c.sales).action_earn_commission()
    out = c.env["fix.a04.finance.consumers"].consume_commission_earned(
        {"aggregate": "fix.referral", "aggregate_id": r.id, "payload": {}}
    )
    row = c.env["fix.commission.ledger"].browse(out["id"])
    assert r.commission_ledger_id == row and row.state == "earned"
    r.with_user(c.acct).action_accrue_commission()  # used to hit UNIQUE(referral_id)
    assert row.state == "accrued" and row.gl_move_id and row.tds_amount == 150.0
    assert c.env["fix.commission.ledger"].search_count([("referral_id", "=", r.id)]) == 1
    with pytest.raises(UserError, match="already in the commission ledger"):
        r.with_user(c.acct).action_accrue_commission()


def test_m53_4_accrue_before_the_relay_then_replay_makes_no_second_row(c):  # noqa: F811
    r, led = accrued_referral(c)
    out = c.env["fix.a04.finance.consumers"].consume_commission_earned(
        {"aggregate": "fix.referral", "aggregate_id": r.id, "payload": {}}
    )
    assert out == {"model": led._name, "id": led.id, "created": False}


# ================================================================= M53-4: referral on screen
def test_m53_4_referral_conversion_on_screen_with_the_invoice_picker(c, p03, screens):  # noqa: F811
    assert_operable(
        p03,
        screens,
        "M53-partners",
        "M53-form-referral",
        c.sales,
        ["convert_invoice_id"],
        ["action_convert", "action_earn_commission", "action_accrue_commission"],
    )
    inv = paid_invoice(c)
    r = referral(c)
    assert ["state", "in", ["submitted", "converted", "commissioned"]] in screens["screens"][
        "M53-partners"
    ]["domain"]
    p03.as_user(c.acct)  # not the role the spec names
    res = p03.action(
        model="fix.referral", ids=[r.id], method="action_convert", kwargs={"invoice": inv.name}
    )
    assert res["success"] is False and r.state == "submitted"
    r.with_user(c.sales).write({"convert_invoice_id": inv.id})
    p03.as_user(c.sales)
    res = p03.action(
        model="fix.referral", ids=[r.id], method="action_convert", kwargs={"invoice": ""}
    )
    assert res["success"], res
    assert r.state == "converted" and r.invoice_id == inv and r.base_amount == inv.taxable_amount
    assert p03.action(model="fix.referral", ids=[r.id], method="action_earn_commission")["success"]
    p03.as_user(c.acct)
    assert p03.action(model="fix.referral", ids=[r.id], method="action_accrue_commission")[
        "success"
    ]
    assert r.commission_ledger_id.state == "accrued"


def test_m53_4_conversion_by_typed_invoice_number_and_refusals(c, p03):  # noqa: F811
    inv = paid_invoice(c)
    r = referral(c)
    p03.as_user(c.sales)
    res = p03.action(
        model="fix.referral", ids=[r.id], method="action_convert", kwargs={"invoice": ""}
    )
    assert res["success"] is False and "name the invoice" in res["error"]
    res = p03.action(
        model="fix.referral",
        ids=[r.id],
        method="action_convert",
        kwargs={"invoice": "NO-SUCH-INVOICE"},
    )
    assert res["success"] is False and r.state == "submitted"
    res = p03.action(
        model="fix.referral", ids=[r.id], method="action_convert", kwargs={"invoice": inv.name}
    )
    assert res["success"] and r.invoice_id == inv


# ================================================================= M53-4: earned rows with no source
def _unsourced(c, gross=4000.0):  # noqa: F811
    return c.env["fix.commission.ledger"].create(
        {
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
            "source_type": "marketplace",
            "seller_partner_id": c.payee2.id,
            "gross_amount": gross,
            "commission_rate": 0.10,
        }
    )


def test_m53_4_unsourced_screen_void_needs_an_administrator_and_a_reason(c, p03, screens):  # noqa: F811
    assert_operable(
        p03,
        screens,
        "M53-ledger-unsourced",
        None,
        c.mgr,
        (),
        ["action_link_source", "action_void_unsourced", "action_void_all_unsourced"],
    )
    row = _unsourced(c)
    with pytest.raises(UserError, match="no marketplace order"):
        row.with_user(c.acct).action_post_to_gl()
    p03.as_user(c.acct)
    res = p03.action(
        model="fix.commission.ledger",
        ids=[row.id],
        method="action_void_unsourced",
        kwargs={"reason": "seed"},
    )
    assert res["success"] is False and row.state == "earned"
    p03.as_user(c.mgr)
    res = p03.action(
        model="fix.commission.ledger",
        ids=[row.id],
        method="action_void_unsourced",
        kwargs={"reason": ""},
    )
    assert res["success"] is False and row.state == "earned"
    res = p03.action(
        model="fix.commission.ledger",
        ids=[row.id],
        method="action_void_unsourced",
        kwargs={"reason": "synthetic seed row"},
    )
    assert res["success"] and row.state == "void" and row.voided_by_id == c.mgr
    assert not row.gl_move_id


def test_m53_4_void_all_covers_the_company_not_rows_with_a_source(c, p03):  # noqa: F811
    rows = _unsourced(c) | _unsourced(c) | _unsourced(c)
    _seller, order = _commissioned_order(c)
    out = c.env["fix.a04.finance.consumers"].consume_commission_earned(
        {"aggregate": "fix.marketplace.order", "aggregate_id": order.id, "payload": {}}
    )
    sourced = c.env["fix.commission.ledger"].browse(out["id"])
    p03.as_user(c.mgr)
    res = p03.action(
        model="fix.commission.ledger",
        ids=[rows[0].id],
        method="action_void_all_unsourced",
        kwargs={"reason": "synthetic seed rows"},
    )
    assert res["success"] and res["result"] == {"voided": 3}
    assert set(rows.mapped("state")) == {"void"} and sourced.state == "earned"


def test_m53_4_a_row_with_a_source_is_never_voided(c):  # noqa: F811
    _r, led = accrued_referral(c)
    with pytest.raises(UserError, match="not voided"):
        led.with_user(c.mgr).action_void_unsourced("x")
    assert led.state == "accrued"


def test_m53_4_link_source_checks_payee_and_amount_then_it_accrues(c, p03):  # noqa: F811
    c.env["fix.commission.scheme"].create(
        {
            "name": "Seller",
            "scheme_type": "seller",
            "tds_rate": 0.05,
            "date_from": date(2025, 7, 1),
            "company_id": c.company.id,
        }
    )
    _seller, order = _commissioned_order(c, gross=4000.0)
    other = _unsourced(c, gross=999.0)
    row = _unsourced(c, gross=4000.0)
    p03.as_user(c.acct)
    res = p03.action(
        model="fix.commission.ledger",
        ids=[other.id],
        method="action_link_source",
        kwargs={"source_ref": order.name},
    )
    assert res["success"] is False and "awarded at" in res["error"]
    res = p03.action(
        model="fix.commission.ledger",
        ids=[row.id],
        method="action_link_source",
        kwargs={"source_ref": order.name},
    )
    assert res["success"], res
    assert row.marketplace_order_id == order
    declare_marketplace_agent(c.env, c.company)
    row.with_user(c.acct).action_post_to_gl()
    assert row.state == "accrued" and row.scheme_id and row.tds_amount > 0


# ================================================================= M53-7: escrow
def test_m53_7_escrow_form_offers_what_create_requires(c, p03, screens):  # noqa: F811
    assert_operable(
        p03,
        screens,
        "M53-escrow",
        "M53-form-clawback",
        c.acct,
        ["adjustment_type", "seller_partner_id", "dispute_id", "commission_ids", "reason"],
        ["action_activate", "action_release"],
    )
    field = {f["name"]: f for f in form_fields_of(screens, "M53-form-clawback")}
    assert field["reason"]["required"] is True
    r, led = accrued_referral(c)
    adj = as_(c, c.acct)["fix.settlement.adjustment"].create(
        {
            "adjustment_type": "escrow",
            "seller_partner_id": led.seller_partner_id.id,
            "commission_ids": [(6, 0, led.ids)],
            "reason": "dispute by phone",
            "company_id": c.company.id,
        }
    )
    p03.as_user(c.acct)
    assert p03.action(model="fix.settlement.adjustment", ids=[adj.id], method="action_activate")[
        "success"
    ]
    assert led.escrow_hold and adj.state == "active"
    res = p03.action(model="fix.settlement.adjustment", ids=[adj.id], method="action_release")
    assert res["success"] is False  # the requester never releases
    p03.as_user(c.acct2)
    assert p03.action(model="fix.settlement.adjustment", ids=[adj.id], method="action_release")[
        "success"
    ]
    assert not led.escrow_hold


def _dispute(c, order):  # noqa: F811
    return c.env["fix.marketplace.dispute"].create(
        {
            "order_id": order.id,
            "seller_id": order.selected_quote_id.seller_id.id,
            "company_id": c.company.id,
            "customer_id": order.customer_id.id,
            "disputed_amount": 1000.0,
            "description": "broken again",
        }
    )


def test_m53_7_a_raised_dispute_holds_its_commissions(c):  # noqa: F811
    consumer = c.env.ref("cd_settlement_ext.consumer_marketplace_dispute_escrow")
    assert consumer.active and consumer.event_type == "marketplace.dispute_raised"
    _seller, order = _commissioned_order(c)
    row = c.env["fix.commission.ledger"].browse(
        c.env["fix.a04.finance.consumers"].consume_commission_earned(
            {"aggregate": "fix.marketplace.order", "aggregate_id": order.id, "payload": {}}
        )["id"]
    )
    dispute = _dispute(c, order)
    event = {"aggregate": "fix.marketplace.dispute", "aggregate_id": dispute.id, "payload": {}}
    Adj = c.env["fix.settlement.adjustment"]
    out = Adj.consume_dispute_raised(event)
    adj = Adj.browse(out["id"])
    assert out["created"] and adj.state == "active" and adj.dispute_id == dispute
    assert row.escrow_hold and row in adj.commission_ids and adj.amount == row.net_payable
    # a replay holds nothing twice
    assert Adj.consume_dispute_raised(event)["id"] == adj.id
    assert Adj.search_count([("dispute_id", "=", dispute.id)]) == 1


def test_m53_7_commission_arriving_after_the_dispute_is_held(c):  # noqa: F811
    _seller, order = _commissioned_order(c)
    dispute = _dispute(c, order)
    Adj = c.env["fix.settlement.adjustment"]
    out = Adj.consume_dispute_raised(
        {"aggregate": "fix.marketplace.dispute", "aggregate_id": dispute.id, "payload": {}}
    )
    assert out["created"] is False  # nothing yet
    row = c.env["fix.commission.ledger"].browse(
        c.env["fix.a04.finance.consumers"].consume_commission_earned(
            {"aggregate": "fix.marketplace.order", "aggregate_id": order.id, "payload": {}}
        )["id"]
    )
    assert row.escrow_hold


def test_m53_7_the_consumer_is_relay_only_and_rereads_the_dispute(c):  # noqa: F811
    with pytest.raises(AccessError):
        as_(c, c.acct)["fix.settlement.adjustment"].consume_dispute_raised({"aggregate_id": 1})
    with pytest.raises(UserError, match="no marketplace dispute"):
        c.env["fix.settlement.adjustment"].consume_dispute_raised({"aggregate_id": 999999999})


# ================================================================= M53-14: reconciliation
def _approved_run(c, *rows):  # noqa: F811
    run = prepared_run(c)
    inbox_approve(c, run, c.mgr)
    return run


def _released(c, run):  # noqa: F811
    run.with_user(c.acct).action_request_payments()
    for pay in run.line_ids.mapped("payment_execution_id"):
        pay.with_user(c.acct2).action_prepare()
        pay.with_user(c.mgr2).action_release()
    run.invalidate_recordset()


def test_m53_14_reconciliation_can_be_created_on_screen(c, p03, screens):  # noqa: F811
    assert_operable(
        p03,
        screens,
        "M53-recon",
        "M53-form-recon",
        c.acct,
        ["payout_run_id", "reconciliation_date"],
        ["action_run_reconciliation", "action_investigate", "action_resolve_break"],
    )
    assert screens["screens"]["M53-recon"].get("create") is not False
    assert_operable(p03, screens, "M53-payouts", None, c.acct, (), ["action_open_reconciliation"])


def test_m53_14_a_break_has_a_way_out(c, p03):  # noqa: F811
    accrued_referral(c)
    run = _approved_run(c)
    _released(c, run)  # sent, not confirmed: the bank side shows nothing
    p03.as_user(c.acct)
    res = p03.action(model="fix.payout.run", ids=[run.id], method="action_open_reconciliation")
    assert res["success"] and res["result"]["state"] == "break_detected"
    rec = run.reconciliation_ids
    assert rec.ran_by_id == c.acct and rec.line_ids
    res = p03.action(
        model="fix.payout.reconciliation",
        ids=[rec.id],
        method="action_investigate",
        kwargs={"note": ""},
    )
    assert res["success"] is False
    res = p03.action(
        model="fix.payout.reconciliation",
        ids=[rec.id],
        method="action_investigate",
        kwargs={"note": "asking the bank"},
    )
    assert res["success"] and rec.state == "investigating" and "asking the bank" in rec.break_notes
    res = p03.action(
        model="fix.payout.reconciliation",
        ids=[rec.id],
        method="action_resolve_break",
        kwargs={"note": "x"},
    )
    assert res["success"] is False  # needs the Accounting Administrator
    rec.with_user(c.mgr).action_run_reconciliation()  # mgr ran it last: cannot resolve
    with pytest.raises(UserError, match="Segregation"):
        rec.with_user(c.mgr).action_resolve_break("explained")
    rec.with_user(c.mgr2).action_resolve_break("bank confirmed value date 3 Nov")
    assert rec.state == "resolved" and rec.resolved_by_id == c.mgr2
    with pytest.raises(UserError, match="resolved"):
        rec.with_user(c.acct).action_run_reconciliation()


def test_m53_14_state_and_notes_are_never_typed(c):  # noqa: F811
    accrued_referral(c)
    run = _approved_run(c)
    _released(c, run)
    rec = as_(c, c.acct)["fix.payout.reconciliation"].create(
        {"company_id": c.company.id, "payout_run_id": run.id}
    )
    with pytest.raises(UserError):
        rec.write({"state": "balanced"})
    with pytest.raises(UserError):
        rec.write({"break_notes": "typed"})


# ================================================================= M53-1: per disbursement, and exits
def _two_payee_run(c):  # noqa: F811
    a = system_row(c, 10000.0, 0.10)
    b = system_row(c, 20000.0, 0.10, payee=c.payee2)
    run = prepared_run(c)
    inbox_approve(c, run, c.mgr)
    _released(c, run)
    line_a = run.line_ids.filtered(lambda ln: ln.partner_id == c.payee)
    line_b = run.line_ids.filtered(lambda ln: ln.partner_id == c.payee2)
    return run, a, b, line_a, line_b


def test_m53_1_each_disbursement_posts_when_the_bank_confirms_it(c):  # noqa: F811
    run, a, b, line_a, line_b = _two_payee_run(c)
    assert run.state == "executing" and not run.gl_move_id
    bank_confirm(c, line_a.payment_execution_id)
    assert line_a.gl_move_id and a.state == "paid"
    assert not line_b.gl_move_id and b.state == "accrued" and run.state == "executing"
    bank = c.bank_journal.default_account_id.code
    assert lines(line_a.gl_move_id) == sorted(
        [("200300", 1000.0, 0.0), ("210100", 0.0, 150.0), (bank, 0.0, 850.0)]
    )
    bank_confirm(c, line_b.payment_execution_id)
    run.invalidate_recordset()
    assert run.state == "executed" and b.state == "paid" and line_b.gl_move_id
    assert line_a.gl_move_id != line_b.gl_move_id
    # never twice: a repeat sync posts nothing
    moves = c.env["account.move"].search_count([("company_id", "=", c.company.id)])
    run._fix_sync_payments()
    run.action_post_payout_to_gl()
    assert c.env["account.move"].search_count([("company_id", "=", c.company.id)]) == moves


def test_m53_1_cancelled_instruction_shows_and_is_re_requested(c, p03, screens):  # noqa: F811
    assert_operable(
        p03,
        screens,
        "M53-payouts",
        None,
        c.acct,
        (),
        ["action_rerequest_unpaid", "action_drop_unpaid"],
    )
    accrued_referral(c)
    run = prepared_run(c)
    inbox_approve(c, run, c.mgr)
    run.with_user(c.acct).action_request_payments()
    line = run.line_ids
    pay = line.payment_execution_id
    pay.with_user(c.acct2).action_cancel()
    run.invalidate_recordset()
    assert pay.state == "cancelled" and run.state == "executing" and run.rail_status == "failed"
    p03.as_user(c.acct)
    assert p03.action(model="fix.payout.run", ids=[run.id], method="action_rerequest_unpaid")[
        "success"
    ]
    run.invalidate_recordset()
    active = run._fix_active_lines()
    assert line.superseded and active != line and run.rail_status == "executing"
    new_pay = active.payment_execution_id
    assert (
        new_pay != pay
        and new_pay.amount == line.amount
        and new_pay.partner_bank_id == line.partner_bank_id
    )
    new_pay.with_user(c.acct2).action_prepare()
    new_pay.with_user(c.mgr2).action_release()
    bank_confirm(c, new_pay)
    run.invalidate_recordset()
    assert run.state == "executed" and len(run.statement_ids) == 1 and active.gl_move_id


def test_m53_1_failed_instruction_is_re_queued_not_duplicated(c):  # noqa: F811
    accrued_referral(c)
    run = prepared_run(c)
    inbox_approve(c, run, c.mgr)
    _released(c, run)
    pay = run.line_ids.payment_execution_id
    pay.sudo().write({"failure_reason": "account closed"})
    pay.with_user(c.acct).action_mark_failed()
    run.invalidate_recordset()
    assert run.rail_status == "failed"
    run.with_user(c.acct).action_rerequest_unpaid()
    assert pay.state == "pending" and len(run._fix_active_lines()) == 1
    assert run.line_ids.payment_execution_id == pay and run.rail_status == "executing"


def test_m53_1_dropping_a_payee_closes_the_run_and_frees_the_commission(c):  # noqa: F811
    run, a, b, line_a, line_b = _two_payee_run(c)
    bank_confirm(c, line_a.payment_execution_id)
    pay_b = line_b.payment_execution_id
    pay_b.sudo().write({"failure_reason": "account closed"})
    pay_b.with_user(c.acct).action_mark_failed()
    run.invalidate_recordset()
    with pytest.raises(AccessError):
        run.with_user(c.acct).action_drop_unpaid("x")
    with pytest.raises(UserError, match="State why"):
        run.with_user(c.mgr).action_drop_unpaid("")
    run.with_user(c.mgr).action_drop_unpaid("payee must give a new account")
    run.invalidate_recordset()
    assert run.state == "executed" and line_b.superseded and pay_b.state == "cancelled"
    assert a.state == "paid" and b.state == "accrued" and b.gl_move_id
    assert b not in run.commission_ids and len(run.statement_ids) == 1
    # the dropped commission can be paid in a new, newly approved run
    new_run = as_(c, c.acct)["fix.payout.run"].create(
        {"period": "2026-11", "company_id": c.company.id, "operating_unit_id": c.ou.id}
    )
    new_run.action_collect_accrued()
    assert b in new_run.commission_ids


def test_m53_1_dropping_the_only_payee_cancels_the_run(c):  # noqa: F811
    _r, led = accrued_referral(c)
    run = prepared_run(c)
    inbox_approve(c, run, c.mgr)
    run.with_user(c.acct).action_request_payments()
    run.line_ids.payment_execution_id.with_user(c.acct2).action_cancel()
    run.invalidate_recordset()
    run.with_user(c.mgr).action_drop_unpaid("payee left the programme")
    run.invalidate_recordset()
    assert run.state == "cancelled" and led.state == "accrued" and led not in run.commission_ids


def test_m53_1_nothing_to_re_request_is_refused(c):  # noqa: F811
    accrued_referral(c)
    run = prepared_run(c)
    inbox_approve(c, run, c.mgr)
    _released(c, run)
    with pytest.raises(UserError, match="no rejected or cancelled"):
        run.with_user(c.acct).action_rerequest_unpaid()
    with pytest.raises(UserError, match="no rejected or cancelled"):
        run.with_user(c.mgr).action_drop_unpaid("x")


# ================================================================= M53-8: certificate on the challan
def _executed_statement(c):  # noqa: F811
    accrued_referral(c)
    run = prepared_run(c)
    inbox_approve(c, run, c.mgr)
    _released(c, run)
    bank_confirm(c, run.line_ids.payment_execution_id)
    run.invalidate_recordset()
    return run.statement_ids


def _challan(c, amount=150.0, kind="tds", verified=True, state="deposited", period="2026-10"):  # noqa: F811
    challan = c.env["fix.tax.challan"].create(
        {
            "company_id": c.company.id,
            "challan_no": "CH-%s" % uuid.uuid4().hex[:6],
            "challan_date": date.today(),
            "tax_kind": kind,
            "period": period,
            "amount": amount,
        }
    )
    vals = {"state": state}
    if verified:
        vals.update(verification_ref="iBAS 1", verified_by_id=c.acct2.id)
    challan.sudo()._guarded().write(vals)
    return challan


def test_m53_8_certificate_is_issued_on_a_deposited_challan_only(c, p03, screens):  # noqa: F811
    assert_operable(
        p03, screens, "M53-sellers", "M53-form-statement", c.acct, (), ["action_attach_challan"]
    )
    st = _executed_statement(c)
    assert st.state == "issued" and st.tds_withheld == 150.0 and not st.withholding_cert_ref
    p03.as_user(c.acct)

    def attach(no):
        return p03.action(
            model="fix.seller.statement",
            ids=[st.id],
            method="action_attach_challan",
            kwargs={"challan_no": no},
        )

    assert attach("NOPE")["success"] is False
    assert attach(_challan(c, kind="vat").challan_no)["success"] is False
    assert attach(_challan(c, verified=False).challan_no)["success"] is False
    assert attach(_challan(c, state="draft").challan_no)["success"] is False
    assert attach(_challan(c, period="2025-01").challan_no)["success"] is False
    assert attach(_challan(c, amount=149.0).challan_no)["success"] is False
    assert not st.withholding_cert_ref and not st.tds_challan_id
    good = _challan(c)
    assert attach(good.challan_no)["success"]
    assert st.tds_challan_id == good and st.withholding_cert_ref.startswith("TDSC/")
    assert attach(good.challan_no)["success"] is False  # already on it


def test_m53_8_a_challan_never_carries_more_than_it_deposited(c):  # noqa: F811
    st = _executed_statement(c)
    other = st.sudo().copy({"payout_run_id": st.payout_run_id.id})
    c.env.flush_all()
    c.env.cr.execute("UPDATE fix_seller_statement SET state = 'issued' WHERE id = %s", (other.id,))
    c.env.invalidate_all()
    challan = _challan(c, amount=200.0)
    st.with_user(c.acct).action_attach_challan(challan.challan_no)
    with pytest.raises(UserError, match="does not fit"):
        other.with_user(c.acct).action_attach_challan(challan.challan_no)


def test_m53_8_challan_link_is_never_typed(c):  # noqa: F811
    st = _executed_statement(c)
    with pytest.raises(UserError):
        st.with_user(c.acct).write({"tds_challan_id": _challan(c).id})


# ================================================================= M53-12: scheme or refusal
def test_m53_12_seller_with_no_scheme_is_refused_at_accrual(c):  # noqa: F811
    _seller, order = _commissioned_order(c)
    out = c.env["fix.a04.finance.consumers"].consume_commission_earned(
        {"aggregate": "fix.marketplace.order", "aggregate_id": order.id, "payload": {}}
    )
    row = c.env["fix.commission.ledger"].browse(out["id"])
    assert not row.scheme_id and row.state == "earned"
    with pytest.raises(UserError, match="No seller commission scheme"):
        row.with_user(c.acct).action_post_to_gl()
    assert row.state == "earned" and not row.gl_move_id
    c.env["fix.commission.scheme"].create(
        {
            "name": "Seller 8%",
            "scheme_type": "seller",
            "commission_rate": 0.08,
            "tds_rate": 0.10,
            "date_from": date(2025, 7, 1),
            "company_id": c.company.id,
        }
    )
    declare_marketplace_agent(c.env, c.company)
    row.with_user(c.acct).action_post_to_gl()
    assert row.state == "accrued" and row.commission_rate == 0.08 and row.scheme_id
    # no PSR on file: the non-filer uplift applies (10% x 1.5 on 4,000)
    assert row.tds_amount == 600.0 and not row.psr_verified


# ================================================================= M53-13: generator and price
def test_m53_13_generate_is_on_the_surface_and_works_for_an_existing_contract(c, p03, screens):  # noqa: F811
    assert_operable(
        p03,
        screens,
        "M53-subscriptions",
        "M53-form-subscription",
        c.acct,
        ["recurring_amount", "contract_value", "contract_end_date"],
        [
            "action_generate_revrec_schedule",
            "action_allocate_price",
            "action_request_contract_value",
            "action_approve_contract_value",
        ],
    )
    s = sub(
        c, c.acct, recurring_amount=1000.0, contract_end_date=date.today() + timedelta(days=300)
    )
    p03.as_user(c.acct)
    res = p03.action(model="fix.subscription", ids=[s.id], method="action_generate_revrec_schedule")
    assert res["success"], res
    schedule = s.obligation_ids.schedule_id
    assert schedule.state == "active" and schedule.subscription_id == s
    assert schedule.total_amount == s._transaction_price()


def test_m53_13_allocate_price_runs_on_a_live_contract_via_a_second_person(c, p03):  # noqa: F811
    s = sub(c, c.acct, recurring_amount=1000.0)
    a = as_(c, c.acct)["fix.performance.obligation"].create(
        {
            "subscription_id": s.id,
            "name": "AMC",
            "standalone_price": 7500.0,
            "start_date": s.start_date,
            "end_date": date.today() + timedelta(days=300),
        }
    )
    b = as_(c, c.acct)["fix.performance.obligation"].create(
        {
            "subscription_id": s.id,
            "name": "Warranty",
            "standalone_price": 2500.0,
            "start_date": s.start_date,
            "end_date": date.today() + timedelta(days=300),
        }
    )
    p03.as_user(c.acct)
    res = p03.action(model="fix.subscription", ids=[s.id], method="action_allocate_price")
    assert res["success"] is False and "transaction price" in res["error"]
    with pytest.raises(UserError, match="Request Price"):
        s.with_user(c.acct).write({"contract_value": 10000.0})
    res = p03.action(
        model="fix.subscription",
        ids=[s.id],
        method="action_request_contract_value",
        kwargs={"contract_value": 10000.0, "reason": "AMC-77, signed 1 Oct"},
    )
    assert res["success"], res
    assert s.pending_contract_value == 10000.0 and s.contract_value == 0.0
    res = p03.action(model="fix.subscription", ids=[s.id], method="action_approve_contract_value")
    assert res["success"] is False  # the requester and creator never approve
    p03.as_user(c.acct2)
    assert p03.action(model="fix.subscription", ids=[s.id], method="action_approve_contract_value")[
        "success"
    ]
    assert s.contract_value == 10000.0 and not s.contract_value_requested_by_id
    assert p03.action(model="fix.subscription", ids=[s.id], method="action_allocate_price")[
        "success"
    ]
    assert (a.allocated_amount, b.allocated_amount) == (7500.0, 2500.0)


def test_m53_13_a_large_transaction_price_needs_the_administrator(c):  # noqa: F811
    s = sub(c, c.acct)
    s.with_user(c.acct).action_request_contract_value(contract_value=500000.0, reason="AMC-99")
    with pytest.raises(AccessError):
        s.with_user(c.acct2).action_approve_contract_value()
    s.with_user(c.mgr).action_approve_contract_value()
    assert s.contract_value == 500000.0


def test_m53_13_a_scheduled_contract_changes_only_by_modification(c):  # noqa: F811
    s = sub(c, c.acct, contract_value=12000.0, contract_end_date=date.today() + timedelta(days=300))
    s.with_user(c.acct).action_generate_revrec_schedule()
    with pytest.raises(UserError, match="modification"):
        s.with_user(c.acct).action_request_contract_value(contract_value=20000.0, reason="more")


# ================================================================= M53-15: dunning cron
def _overdue_subscription(c, days):  # noqa: F811
    s = sub(c, c.acct, next_invoice_date=date.today() - timedelta(days=days + 7))
    c.env["fix.credit.profile"].create(
        {"customer_id": s.customer_id.id, "company_id": c.company.id, "payment_terms_days": 7}
    )
    # trusted catch-up: cycles older than 31 days are an Accounting Manager's to raise
    s.sudo().action_generate_charge()
    invoice = s.charge_ids.invoice_id.with_env(as_(c, c.acct))
    invoice.with_user(c.acct2).action_issue()
    return s, invoice


def _events(c, event_type, sub_id):  # noqa: F811
    return c.env["fix.event.outbox"].search_count(
        [("event_type", "=", event_type), ("aggregate_id", "=", sub_id)]
    )


def test_m53_15_dunning_cron_exists(c):  # noqa: F811
    cron = c.env.ref("cd_subscription.ir_cron_subscription_dunning")
    assert cron.active and "_cron_run_dunning" in cron.code


def test_m53_15_dunning_cron_runs_the_ladder_and_notifies_once_per_step(c):  # noqa: F811
    s, _invoice = _overdue_subscription(c, 5)
    Sub = c.env["fix.subscription"]
    assert Sub._cron_run_dunning() >= 1
    assert s.state == "past_due" and s.dunning_step == "reminder"
    assert _events(c, "subscription.dunning_reminder_sms", s.id) == 1
    Sub._cron_run_dunning()
    assert (
        _events(c, "subscription.dunning_reminder_sms", s.id) == 1
    ), "one SMS a day is not a ladder"


def test_m53_15_dunning_cron_leaves_a_paid_subscription_alone_and_clears_past_due(c):  # noqa: F811
    s, invoice = _overdue_subscription(c, 5)
    Sub = c.env["fix.subscription"]
    Sub._cron_run_dunning()
    assert s.state == "past_due"
    receipt = as_(c, c.acct)["fix.ar.receipt"].create(
        {
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
            "customer_id": s.customer_id.id,
            "amount": invoice.total_payable,
            "method": "cash",
        }
    )
    receipt.action_confirm()
    as_(c, c.acct)["fix.ar.allocation"].create(
        {"receipt_id": receipt.id, "invoice_id": invoice.id, "amount": invoice.total_payable}
    )
    Sub._cron_run_dunning()
    assert s.state == "active" and s.dunning_step == "none" and s.days_overdue == 0


def test_m53_15_dunning_cron_posts_nothing(c):  # noqa: F811
    _overdue_subscription(c, 40)
    moves = c.env["account.move"].search_count([("company_id", "=", c.company.id)])
    c.env["fix.subscription"]._cron_run_dunning()
    assert c.env["account.move"].search_count([("company_id", "=", c.company.id)]) == moves


# ================================================================= forms
def test_m53_every_form_field_is_real_and_big_forms_use_tabs(c, p03, screens):  # noqa: F811
    for sid, cfg in screens["screens"].items():
        if cfg.get("kind") != "model_form":
            continue
        fields = form_fields_of(screens, sid)
        p03.as_user(c.mgr)
        res = p03.form(model=cfg["model"], fields=fields)
        assert "error" not in res, (sid, res)
        assert {f["name"] for f in fields} == {f["name"] for f in res["fields"]}, sid
        if len(fields) > 15:
            declared = {t["id"] for t in cfg.get("tabs", [])}
            assert declared and {s.get("tab") for s in cfg["sections"]} == declared, sid


def test_m53_no_form_offers_a_guarded_field_as_an_input(c, screens):  # noqa: F811
    """What form_fields.py --a08 will generate the write whitelist from."""
    for sid, cfg in screens["screens"].items():
        if cfg.get("kind") != "model_form":
            continue
        model = c.env[cfg["model"]]
        guarded = model._fix_guarded_fields() if hasattr(model, "_fix_guarded_fields") else set()
        inputs = {f["name"] for f in form_fields_of(screens, sid) if not f.get("readonly")}
        assert not inputs & set(guarded), (sid, sorted(inputs & set(guarded)))
