# cd_cash_position — A08 finish, M50: a treasury user can do the whole job on
# the workspace. Each test pairs what the P03 surface offers (the screen, form
# field or action, read from the real static/src/a08/m50.js and SURFACES) with
# the real path as a NON-ADMIN user holding the real finance role. Arrangement
# comes from the control suite's fixture; everything rolls back (odoo_env).
from __future__ import annotations

import base64
import json
import shutil
import subprocess
from pathlib import Path

import pytest
from odoo import fields
from odoo.addons.cd_cash_position.tests.test_a08_m50_controls import (
    _SEQ,
    _authorise,
    _cod,
    _cod_orders,
    _facility,
    _gw,
    c,  # noqa: F401 - the shared fixture
    pay,
    stmt,
)
from odoo.addons.cd_p03_portal.controllers.a08 import m50
from odoo.exceptions import AccessError, UserError, ValidationError

pytestmark = [pytest.mark.financial]

REFUSED = (UserError, ValidationError, AccessError)
A08_JS = Path(m50.__file__).resolve().parents[2] / "static" / "src" / "a08" / "m50.js"
TOLERANCE = "cd_cash_position.cod_shortage_tolerance"
ESCALATION = "cd_cash_position.cod_shortage_escalation_threshold"
SET_BY_CREATE = {
    ("fix.payment.execution", "source_model"),
    ("fix.payment.execution", "source_id"),
}


@pytest.fixture(scope="module")
def js(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the workspace registry")
    tmp = tmp_path_factory.mktemp("m50_js")
    (tmp / "m50.mjs").write_text(A08_JS.read_text(encoding="utf-8"), "utf-8")
    probe = tmp / "probe.mjs"
    probe.write_text(
        "import * as F from './m50.mjs';\n"
        "console.log(JSON.stringify({module: F.MODULE, screens: F.SCREENS, chips: F.FORM_CHIPS}));\n",
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our probe file
        [node, str(probe)], capture_output=True, text=True, encoding="utf-8", check=True, timeout=60
    )
    return json.loads(out.stdout)


def _form(js, screen):
    """The form a list screen's "+ New" opens, its fields by name."""
    form_id = js["chips"]["M50:__by_screen__"][screen]
    form = js["screens"][form_id]
    return form, {f["name"]: f for s in form["sections"] for f in s["fields"]}


def _prepared(c, **kw):  # noqa: F811
    p = pay(c, **kw)
    p.with_user(c.acct).action_prepare()
    if p._approval_needed():
        _authorise(c, p)
    return p


def _released(c, **kw):  # noqa: F811
    p = _prepared(c, **kw)
    p.with_user(c.mgr).action_release()
    return p


def _offers(js, screen, method):
    """The list screen shows the button and the backend allows it."""
    conf = js["screens"][screen]
    assert method in [a["m"] for a in conf.get("actions", [])], "%s has no %s" % (screen, method)
    assert method in m50.SURFACES[conf["model"]]["actions"], "surface refuses %s" % method


# ------------------------------------------------------------------ the forms
def test_every_m50_form_is_operable(c, js):  # noqa: F811
    """No M50 form is a dead end: every field is real, a form over 15 fields has
    tabs, every section's tab is declared, every required field with no default
    and no compute is on the form, and every list + form model is served."""
    dead_ends = []
    for name, form in js["screens"].items():
        if form.get("kind") != "model_form":
            continue
        model = c.env[form["model"]]
        assert form["model"] in m50.SURFACES, name
        names = [f["name"] for s in form["sections"] for f in s["fields"]]
        missing = [n for n in names if n not in model._fields]
        assert not missing, "%s declares unknown fields %s" % (name, missing)
        tabs = {t["id"] for t in form.get("tabs", [])}
        if len(names) > 15:
            assert tabs, "%s has %d fields and no tabs" % (name, len(names))
        for section in form["sections"]:
            if tabs:
                assert section.get("tab") in tabs, "%s: section renders invisible" % name
        defaults = model.default_get(list(model._fields))
        dead = [
            n
            for n, f in model._fields.items()
            if f.required
            and not f.compute
            and not f.related
            and n not in names
            and n not in defaults
            # a manual instruction's source key comes from its create()
            and (form["model"], n) not in SET_BY_CREATE
        ]
        if dead:
            dead_ends.append((name, dead))
    assert not dead_ends, "required fields not on the form: %s" % dead_ends


def test_every_m50_list_column_and_action_is_real(c, js):  # noqa: F811
    for name, conf in js["screens"].items():
        if conf.get("kind") != "model_list":
            continue
        model = c.env[conf["model"]]
        bad = [col for col in conf["cols"] if col not in model._fields]
        assert not bad, "%s drops columns %s" % (name, bad)
        for action in conf.get("actions", []):
            assert hasattr(model, action["m"]), "%s: %s" % (name, action["m"])
            assert action["m"] in m50.SURFACES[conf["model"]]["actions"], action["m"]
        nav = {s["id"] for g in js["module"]["groups"] for s in g["screens"]}
        assert name in nav, "%s is on no menu" % name


# ------------------------------------------------------------- items 1, 2, 11
def test_m50_3_statement_file_can_be_attached_and_confirms_a_payment(c, js):  # noqa: F811
    _form_def, fields_ = _form(js, "M50-statements")
    assert fields_["file"]["type"] == "binary" and ".csv" in fields_["file"]["accept"]
    assert fields_["file"]["filename"] == "filename"
    _offers(js, "M50-statements", "action_import")
    # the real path: a sent payment, the file attached to a new record, Import, Confirm
    p = _released(c)
    assert p.state == "sent" and not p.bank_confirmed
    body = "Date,Amount,Reference,Description\n%s,-4500.00,%s,paid\n" % (c.today, p.name)
    imp = (
        c.env["fix.bank.statement.import"]
        .with_user(c.acct2)
        .create(
            {
                "journal_id": c.bank.id,
                "format_type": "csv",
                "file": base64.b64encode(body.encode()),
                "filename": "statement.csv",
            }
        )
    )
    imp.with_user(c.acct2).action_import()
    assert imp.state == "imported" and imp.imported_count == 1
    p.with_user(c.acct2).action_confirm_bank()
    assert p.state == "executed" and p.bank_confirmed


def test_m50_9_gateway_report_can_be_attached_and_imported(c, js):  # noqa: F811
    _form_def, fields_ = _form(js, "M50-gateway")
    assert fields_["report_file"]["type"] == "binary"
    assert fields_["report_file"]["accept"] == ".csv"
    assert fields_["report_file"]["filename"] == "report_filename"
    _offers(js, "M50-gateway", "action_import_report")
    b = _gw(c, "TrxID,Amount,Fee,Net\nOPER%s,1000.00,15.00,985.00\n" % next(_SEQ))
    b.with_user(c.acct).action_import_report()
    assert b.line_count == 1 and b.state == "exceptions"


def test_instruction_form_has_tabs_and_covers_cash_and_cheque_methods(c, js):  # noqa: F811
    for screen in ("M50-beftn", "M50-mfs", "M50-cashpay", "M50-chequepay"):
        form, fields_ = _form(js, screen)
        assert form["tabs"] and len(fields_) > 15, screen
    cash = pay(c, amount=700.0, method="cash", rail=False, partner_bank_id=False)
    cheque = pay(c, amount=800.0, method="cheque", rail="cheque", partner_bank_id=False)
    Execution = c.env["fix.payment.execution"].with_user(c.acct)
    for screen, row, other in (("M50-cashpay", cash, cheque), ("M50-chequepay", cheque, cash)):
        conf = js["screens"][screen]
        assert conf["model"] == "fix.payment.execution"
        found = Execution.search(conf["domain"])
        assert row in found and other not in found, screen
        _offers(js, screen, "action_release")


# -------------------------------------------------------------- COD, items 3, 4
def _short(c, tier_tolerance=None, tier_escalation=None):  # noqa: F811
    """A submitted settlement: 5,000 expected, 4,000 remitted."""
    icp = c.env["ir.config_parameter"].sudo()
    if tier_tolerance is not None:
        icp.set_param(TOLERANCE, tier_tolerance)
    if tier_escalation is not None:
        icp.set_param(ESCALATION, tier_escalation)
    _cod_orders(c, [3000.0, 2000.0])
    s = _cod(c)
    s.with_user(c.acct).action_load_orders()
    s.with_user(c.acct).write({"remitted_amount": 4000.0})
    s.with_user(c.acct).action_submit()
    return s


def test_m50_10_cod_is_created_and_entered_on_a_form(c, js):  # noqa: F811
    conf = js["screens"]["M50-ridercod"]
    assert conf.get("create", True) is True
    form, fields_ = _form(js, "M50-ridercod")
    assert form["tabs"]
    for name in ("rider_id", "remitted_amount", "remittance_journal_id", "remittance_ref"):
        assert not fields_[name].get("readonly"), name
    for name in ("dispute_reason", "recovery_ref"):
        assert not fields_[name].get("readonly"), name
    # dispute and recovery stay enterable after submission, the terms do not
    s = _short(c)
    assert "dispute_reason" not in s._fix_form_locked_fields()
    assert "remitted_amount" in s._fix_form_locked_fields()
    for method in ("action_load_orders", "action_submit", "action_settle", "action_dispute"):
        _offers(js, "M50-ridercod", method)
    s.with_user(c.mgr).action_dispute(reason="Rider disputes the count")
    assert (s.state, s.dispute_reason) == ("disputed", "Rider disputes the count")


def test_m50_10_shortage_tiers_come_from_config(c):  # noqa: F811
    """Unconfigured: the strictest path. Configured: tolerance, then second
    approver, then escalated with a stated reason."""
    s = _short(c)
    assert s.shortage_tier == "escalated"
    with pytest.raises(UserError, match="state why"), c.env.cr.savepoint():
        s.with_user(c.mgr).action_approve_shortage()
    s.with_user(c.mgr).action_approve_shortage(note="Rider's cash bag was stolen, police report")
    assert s.shortage_approved_by_id == c.mgr and "stolen" in s.shortage_approval_note
    assert s.sudo().activity_ids.filtered(lambda a: a.summary == "Escalated COD shortage")
    s.with_user(c.mgr2).action_settle()
    assert s.state == "settled"

    icp = c.env["ir.config_parameter"].sudo()
    icp.set_param(TOLERANCE, "500")
    icp.set_param(ESCALATION, "2000")
    s.invalidate_recordset()
    assert s.shortage_tier == "second_approver"  # 1,000 between the two thresholds
    icp.set_param(TOLERANCE, "1000")
    s.invalidate_recordset()
    assert s.shortage_tier == "tolerated"


def test_m50_10_tolerated_shortage_needs_no_second_approver(c):  # noqa: F811
    s = _short(c, tier_tolerance="1000")
    assert s.shortage_tier == "tolerated" and not s._needs_shortage_approval()
    s.with_user(c.mgr).action_settle()
    assert s.state == "settled" and s.recovery_state == "open"


def test_m50_10_booked_shortage_goes_to_hr_and_blocks_the_rider(c):  # noqa: F811
    s = _short(c)
    Settlement = c.env["fix.cod.settlement"]
    s.with_user(c.mgr).action_approve_shortage(note="accepted")
    s.with_user(c.mgr2).action_settle()
    event = c.env["fix.event.outbox"].search(
        [("event_type", "=", "cod.shortage_recovery_requested"), ("aggregate_id", "=", s.id)]
    )
    assert event and s.recovery_requested_at
    payload = event.payload if isinstance(event.payload, dict) else json.loads(event.payload)
    assert payload["employee_id"] == c.rider.id and payload["amount"] == 1000.0
    assert s.sudo().activity_ids.filtered(lambda a: a.summary == "Recover rider COD shortage")
    assert Settlement._fix_rider_has_open_variance(c.rider)

    # a real caller: a further COD order on this rider's consignment is refused
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
    customer = c.env["res.partner"].create({"name": "Next COD customer"})
    order = (
        c.env["fix.storefront.order"]
        .sudo()
        .create(
            {
                "customer_id": customer.id,
                "total_amount": 900.0,
                "shipping_address": "Dhaka",
                "payment_rail": "cod",
                "state": "draft",
                "operating_unit_id": c.ou.id,
            }
        )
    )
    with pytest.raises(UserError, match="BRU-TRE-04"), c.env.cr.savepoint():
        order.write({"carrier_consignment_id": cons.id})
    # nor can a blocked rider be put on a consignment already carrying COD
    other = c.env["hr.employee"].create({"name": "Clean rider %s" % next(_SEQ)})
    cons.sudo().write({"rider_id": other.id})
    order.write({"carrier_consignment_id": cons.id})
    with pytest.raises(UserError, match="BRU-TRE-04"), c.env.cr.savepoint():
        cons.sudo().write({"rider_id": c.rider.id})
    # recovery lifts the block, and needs its reference
    with pytest.raises(UserError, match="reference"), c.env.cr.savepoint():
        s.with_user(c.mgr).action_mark_recovered()
    s.with_user(c.mgr).action_mark_recovered(reference="PAYSLIP-2026-11-77")
    assert s.recovery_state == "recovered" and s.recovery_ref == "PAYSLIP-2026-11-77"
    assert not Settlement._fix_rider_has_open_variance(c.rider)
    cons.sudo().write({"rider_id": c.rider.id})
    assert cons.rider_id == c.rider


def test_m50_10_a_prepaid_order_does_not_trip_the_block(c):  # noqa: F811
    s = _short(c)
    assert c.env["fix.cod.settlement"]._fix_rider_has_open_variance(c.rider)
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
    customer = c.env["res.partner"].create({"name": "Prepaid customer"})
    order = (
        c.env["fix.storefront.order"]
        .sudo()
        .create(
            {
                "customer_id": customer.id,
                "total_amount": 900.0,
                "shipping_address": "Dhaka",
                "payment_rail": "bkash",
                "state": "draft",
                "operating_unit_id": c.ou.id,
            }
        )
    )
    order.write({"carrier_consignment_id": cons.id})
    assert order.carrier_consignment_id == cons and s.state == "submitted"


# ------------------------------------------------------- facilities, items 5, 6
def test_m50_12_facility_form_can_activate_and_schedule(c, js):  # noqa: F811
    form, fields_ = _form(js, "M50-facilities")
    assert form["tabs"]
    for name in ("liability_account_id", "journal_id", "principal", "start_date"):
        assert not fields_[name].get("readonly"), name
    for method in ("action_generate_schedule", "action_activate", "action_acknowledge_expiry"):
        _offers(js, "M50-facilities", method)
    # only what the form offers, as an Accounting Administrator
    values = {
        "name": "OPER TL %s" % next(_SEQ),
        "lender_id": c.vendor.id,
        "facility_type": "term_loan",
        "limit_amount": 600000.0,
        "principal": 600000.0,
        "interest_rate": 12.0,
        "tenor_months": 6,
        "repayment_frequency": "monthly",
        "start_date": c.today,
        "liability_account_id": c.acc["cod_clearing"].id,
        "journal_id": c.bank.id,
    }
    assert set(values) <= set(fields_)
    fac = c.env["fix.bank.facility"].with_user(c.mgr).create(values)
    fac.with_user(c.mgr).action_generate_schedule()
    fac.with_user(c.mgr).action_activate()
    assert fac.state == "active" and len(fac.repayment_ids) == 6


def test_m50_12_expiry_alert_can_be_acknowledged(c):  # noqa: F811
    lc = (
        c.env["fix.bank.facility"]
        .with_user(c.mgr)
        .create(
            {
                "name": "OPER LC %s" % next(_SEQ),
                "lender_id": c.vendor.id,
                "facility_type": "lc",
                "limit_amount": 100000.0,
                "expiry_date": c.today,
                "liability_account_id": c.acc["cod_clearing"].id,
            }
        )
    )
    lc.with_user(c.mgr).action_activate()
    assert c.env["fix.bank.facility"]._cron_expiry_alerts() >= 1
    with pytest.raises(UserError), c.env.cr.savepoint():
        lc.with_user(c.acct).action_acknowledge_expiry()
    lc.with_user(c.mgr).action_acknowledge_expiry()
    assert lc.expiry_ack_by_id == c.mgr
    assert not lc.sudo().activity_ids.filtered(lambda a: a.summary == "LC / guarantee expiry")


def test_m50_12_amendment_has_a_screen_and_a_second_person(c, js):  # noqa: F811
    assert "fix.facility.amendment" in m50.SURFACES
    form, fields_ = _form(js, "M50-amendments")
    assert form["model"] == "fix.facility.amendment"
    for name in ("facility_id", "reason", "new_interest_rate", "new_instalments"):
        assert not fields_[name].get("readonly"), name
    for method in ("action_approve", "action_reject"):
        _offers(js, "M50-amendments", method)
    fac = _facility(c)
    before = fac.repayment_ids.filtered(lambda r: r.state == "planned")
    am = (
        c.env["fix.facility.amendment"]
        .with_user(c.acct)
        .create({"facility_id": fac.id, "reason": "Lender letter 14", "new_interest_rate": 9.0})
    )
    assert am.requested_by_id == c.acct
    with pytest.raises(UserError), c.env.cr.savepoint():
        am.with_user(c.acct).action_approve()
    am.with_user(c.mgr).action_approve()
    assert am.state == "approved" and fac.interest_rate == 9.0
    assert fac.repayment_ids.filtered(lambda r: r.state == "planned").ids != before.ids


# ------------------------------------------------------------- cheque book, item 7
def test_m50_13_cheque_book_has_a_screen_and_release_then_works(c, js):  # noqa: F811
    assert "fix.cheque.book" in m50.SURFACES
    form, fields_ = _form(js, "M50-chequebooks")
    for name in ("name", "journal_id", "first_number", "last_number"):
        assert fields_[name].get("required"), name
    assert fields_["next_number"].get("readonly") and fields_["state"].get("readonly")
    _offers(js, "M50-chequebooks", "action_close")
    p = _prepared(c, amount=3300.0, method="cheque", rail="cheque", partner_bank_id=False)
    with pytest.raises(UserError, match="cheque book"), c.env.cr.savepoint():
        p.with_user(c.mgr).action_release()
    vals = {
        "name": "Book 1",
        "journal_id": c.bank.id,
        "first_number": 700100,
        "last_number": 700199,
    }
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        c.env["fix.cheque.book"].with_user(c.acct).create(vals)
    book = c.env["fix.cheque.book"].with_user(c.mgr).create(vals)
    assert book.next_number == 700100
    p.with_user(c.mgr).action_release()
    assert p.state == "sent" and book.next_number == 700101
    book.with_user(c.mgr).action_close()
    assert book.state == "closed"


# ----------------------------------------------------- reconciliation, item 9
def _recon(c, user=None, **kw):  # noqa: F811
    vals = {"journal_id": c.bank.id, "period": c.today.strftime("%Y-%m")}
    vals.update(kw)
    return c.env["fix.bank.reconciliation"].with_user(user or c.acct).create(vals)


def test_m50_6_statement_reconciles_and_needs_a_second_person(c, js):  # noqa: F811
    form, fields_ = _form(js, "M50-reconstatements")
    assert form["tabs"] and not fields_["statement_balance"].get("readonly")
    assert fields_["gl_balance"].get("readonly") and fields_["reviewed_by_id"].get("readonly")
    for method in ("action_prepare", "action_submit", "action_review", "action_return"):
        _offers(js, "M50-reconstatements", method)
    _offers(js, "M50-recon-items", "action_explain")

    # the bank shows a 500 charge the books do not have
    line = stmt(c, [(-500.0, "CHG-%s" % next(_SEQ), "bank charge")])
    rec = _recon(c)
    rec.with_user(c.acct).action_prepare()
    assert (rec.gl_balance, rec.unmatched_net, rec.book_items_net) == (0.0, -500.0, 0.0)
    assert rec.line_ids.source_key == "stmt:%s" % line.id
    rec.with_user(c.acct).write({"statement_balance": -500.0, "statement_ref": "Stmt 11/1"})
    assert rec.difference == 0.0

    # refused: the item is not explained, then the statement does not name its source
    with pytest.raises(UserError, match="not explained"), c.env.cr.savepoint():
        rec.with_user(c.acct).action_submit()
    rec.line_ids.with_user(c.acct).action_explain(explanation="Booking it next week")
    assert rec.line_ids.explained_by_id == c.acct
    rec.with_user(c.acct).action_submit()
    assert rec.state == "submitted" and rec.prepared_by_id == c.acct

    # frozen once submitted
    with pytest.raises(UserError), c.env.cr.savepoint():
        rec.with_user(c.acct).write({"statement_balance": 1.0})
    with pytest.raises(UserError), c.env.cr.savepoint():
        rec.line_ids.with_user(c.acct).action_explain(explanation="later")

    # the reviewer: an Accounting Administrator who did not prepare it
    with pytest.raises(UserError), c.env.cr.savepoint():
        rec.with_user(c.acct2).action_review()
    mine = _recon(c, c.mgr, journal_id=c.bank.id, period="2025-01", statement_ref="S")
    mine.with_user(c.mgr).action_submit()
    with pytest.raises(UserError, match="Segregation"), c.env.cr.savepoint():
        mine.with_user(c.mgr).action_review()
    rec.with_user(c.mgr).action_review()
    assert rec.state == "reviewed" and rec.reviewed_by_id == c.mgr


def test_m50_6_book_entries_not_on_the_statement_reconcile_and_a_difference_is_explained(
    c,  # noqa: F811
):
    """A GL entry on the bank account with no statement line is a reconciling
    item on the other side; a real difference must be explained in words.

    M50-F4 note: a facility instalment can no longer SUPPLY such an entry —
    it posts only against an imported statement debit now — so the book entry
    is arrangement (a direct treasury posting the bank has not shown yet)."""
    from odoo.addons.cd_cash_position.models.treasury_common import post_treasury_move

    amount = 106618.55
    post_treasury_move(
        c.env,
        c.company,
        c.today,
        "B4 book entry not yet on the statement",
        [
            (c.expense, "book side", amount, 0.0, None),
            (c.bank.default_account_id, "bank side", 0.0, amount, None),
        ],
    )
    rec = _recon(c)
    rec.with_user(c.acct).action_prepare()
    assert rec.gl_balance == pytest.approx(-amount)
    assert rec.book_items_net == pytest.approx(-amount)
    assert rec.difference == 0.0  # the bank has not shown it, and shows 0
    rec.line_ids.filtered("counts").with_user(c.acct).action_explain(explanation="Not yet debited")
    rec.with_user(c.acct).write({"statement_balance": 250.0, "statement_ref": "Stmt 2"})
    assert rec.difference == 250.0
    with pytest.raises(UserError, match="does not reconcile"), c.env.cr.savepoint():
        rec.with_user(c.acct).action_submit()
    rec.with_user(c.acct).write({"difference_note": "Bank's opening balance carried from before"})
    rec.with_user(c.acct).action_submit()
    assert rec.state == "submitted"


def test_m50_6_review_refuses_a_ledger_that_moved_and_return_reopens(c):  # noqa: F811
    rec = _recon(c)
    rec.with_user(c.acct).action_prepare()
    rec.with_user(c.acct).write({"statement_ref": "Stmt 3"})
    rec.with_user(c.acct).action_submit()
    stmt(c, [(-77.0, "LATE-%s" % next(_SEQ), "late charge")])
    with pytest.raises(UserError, match="moved"), c.env.cr.savepoint():
        rec.with_user(c.mgr).action_review()
    with pytest.raises(UserError, match="why"), c.env.cr.savepoint():
        rec.with_user(c.mgr).action_return()
    rec.with_user(c.mgr).action_return(reason="A late charge arrived")
    assert rec.state == "draft" and rec.return_reason == "A late charge arrived"
    rec.with_user(c.acct).action_prepare()
    assert rec.unmatched_net == -77.0


def test_m50_6_figures_and_stamps_cannot_be_typed(c):  # noqa: F811
    rec = _recon(c)
    for vals in ({"gl_balance": 1.0}, {"state": "reviewed"}, {"reviewed_by_id": c.mgr.id}):
        with pytest.raises(UserError), c.env.cr.savepoint():
            rec.with_user(c.acct).write(vals)
    with pytest.raises(UserError), c.env.cr.savepoint():
        c.env["fix.bank.reconciliation.line"].with_user(c.acct).create(
            {"reconciliation_id": rec.id, "kind": "book_item"}
        )
    with pytest.raises(ValidationError), c.env.cr.savepoint():
        _recon(c, period="26-11")


def test_m50_6_summary_report_names_the_last_reviewed_statement(c):  # noqa: F811
    from odoo.addons.cd_cash_position.models.treasury_reports import bank_recon_summary

    env = c.env(user=c.acct.id)
    row = next(r for r in bank_recon_summary(env)["rows"] if r["account"] == c.bank.name)
    assert row["last_reviewed"] == "Never"
    rec = _recon(c)
    rec.with_user(c.acct).action_prepare()
    rec.with_user(c.acct).write({"statement_ref": "Stmt 4"})
    rec.with_user(c.acct).action_submit()
    rec.with_user(c.mgr).action_review()
    row = next(r for r in bank_recon_summary(env)["rows"] if r["account"] == c.bank.name)
    assert rec.period in row["last_reviewed"]


# --------------------------------------------------------------- item 10
def test_m50_8_payment_events_carry_their_source(c):  # noqa: F811
    p = _released(c)
    p.sudo()._publish_failed("test")
    p.sudo()._publish_executed()
    for name in ("payment.failed", "payment.executed"):
        event = c.env["fix.event.outbox"].search(
            [("event_type", "=", name), ("aggregate_id", "=", p.id)], order="id desc", limit=1
        )
        payload = event.payload if isinstance(event.payload, dict) else json.loads(event.payload)
        assert payload["source_model"] == p.source_model and payload["source_id"] == p.source_id
