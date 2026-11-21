# A05 ERP audit (20 Nov 2026), M14 Trade-in, Refurbishment & Resale: the
# valued ledger, the payout at purchase (D3), the sale and return of a
# refurbished unit, pricing (D6), the warranty provision (D7), NEIR (D4), the
# parts-only path, bulk buy-back, offer expiry and the cross-stream seams
# (I1, I4, I5). Every test runs the real actions as non-admin users holding
# only the roles their step needs; odoo_env rolls everything back.
import itertools
import json
import re
import types
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.addons.cd_tradein.tests.test_a05_m14_controls import seller_wallet
from odoo.addons.cd_workflow_engine.tests.approval_helpers import inbox_task
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
TRD = "fix.tradein.request"
_SEQ = itertools.count(1)
_CR = []

# the test chart's accounts for the D1 roles (fix_real takes the owner's codes)
ACCOUNTS = {
    "refurb_stock": "110100",
    "seller_payable": "211000",
    "tds_payable": "252000",
    "cogs": "500000",
    "writeoff": "610000",
    "warranty_provision": "201000",
    "warranty_expense": "962000",
    "refurb_absorption": "110400",
    # D10(b) (S6 wiring): refurbished resale revenue
    "resale_revenue": "400000",
}


def _user(env, login, groups=(), ou=None):
    n = next(_SEQ)
    vals = {
        "name": "A05 ERP M14 %s %d" % (login, n),
        "login": "a05erp.m14.%s.%d@a05.test" % (login, n),
        "group_ids": [(6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])],
    }
    if ou:
        vals.update(operating_unit_ids=[(6, 0, ou.ids)], default_operating_unit_id=ou.id)
    return env["res.users"].with_context(no_reset_password=True).create(vals)


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    params = env["ir.config_parameter"].sudo()
    params.set_param("cd_tradein.hold_days", "0")
    params.set_param("cd_tradein.allow_neir_unchecked", "0")
    params.set_param("cd_tradein.kyc_payout_cap_per_nid_30d", "0")
    for role, code in ACCOUNTS.items():
        params.set_param("cd_tradein.account_code.%s" % role, code)
    params.set_param("cd_tax_engine_bd.account_code.tds_payable", "252000")
    for grade, pct in (("a", "2"), ("b", "3"), ("c", "5"), ("d", "7")):
        params.set_param("cd_tradein.warranty_provision_pct.%s" % grade, pct)
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    x = types.SimpleNamespace(env=env, ou=ou)
    x.clerk = _user(env, "clerk", ["cd_workshop.group_fix_workshop_user"], ou)
    x.clerk2 = _user(env, "clerk2", [], ou)
    x.approver = _user(
        env,
        "approver",
        ["cd_entity_config.group_dofa_tier_1", "cd_tradein.group_tradein_payout_approver"],
        ou,
    )
    x.officer = _user(env, "officer", ["cd_tradein.group_tradein_provenance_officer"], ou)
    x.qa = _user(env, "qa", ["cd_tradein.group_tradein_qa_inspector"], ou)
    x.valmgr = _user(
        env,
        "valmgr",
        ["cd_tradein.group_tradein_valuation_manager", "cd_entity_config.group_dofa_tier_1"],
        ou,
    )
    x.tech = _user(env, "tech", [], ou)
    env["hr.employee"].create({"name": "A05 ERP M14 Technician", "user_id": x.tech.id})
    x.supervisor = _user(env, "supervisor", ["cd_tradein.group_refurb_supervisor"], ou)
    x.woapprover = _user(
        env,
        "woapprover",
        ["cd_tradein.group_refurb_writeoff_approver", "cd_entity_config.group_dofa_tier_1"],
        ou,
    )
    x.pricer = _user(env, "pricer", ["cd_tradein.group_refurb_pricing_manager"], ou)
    x.pricer2 = _user(env, "pricer2", ["cd_tradein.group_refurb_pricing_manager"], ou)
    x.controller = _user(env, "controller", ["cd_wms_structure.group_inventory_controller"], ou)
    brand = env["fix.brand"].create({"name": "A05 ERP M14 Brand", "code": "A5EM14"})
    x.model = env["fix.device.model"].create({"name": "A05 ERP M14 Phone", "brand_id": brand.id})
    grid = (
        env["fix.tradein.price.grid"]
        .with_user(x.clerk)
        .create({"device_model_id": x.model.id, "market_ref_price": 20000})
    )
    grid.with_user(x.valmgr).action_approve()
    _CR.append(env.cr)
    yield x
    _CR.pop()


def refused(fn, match=None):
    with pytest.raises(REFUSED) as exc, _CR[-1].savepoint():
        fn()
    if match:
        assert re.search(match, str(exc.value)), str(exc.value)
    return exc.value


def acct(x, role):
    return x.env["account.account"].search(
        [("code", "=", ACCOUNTS[role]), ("company_ids", "in", x.env.company.id)], limit=1
    )


def device(x):
    n = next(_SEQ)
    return x.env["fix.device"].create(
        {
            "device_model_id": x.model.id,
            "serial_number": "A05ERP-SN-%05d" % n,
            "imei_1": "35%013d" % (5500000 + n),
        }
    )


def cert(x, dev, rec=None):
    """With ``rec`` the certificate answers the trade-in's own wipe request
    (A02 pass 2 review N2: an M14 release needs one), Purge on flash media."""
    log = x.env["ir.attachment"].create({"name": "wipe.log", "raw": b"nwipe: PASS"})
    vals = {
        "method": "nist_800_88",
        "serial_number": dev.serial_number,
        "sector_count": 1000,
        "wipe_log_attachment_id": log.id,
    }
    if rec is not None:
        vals.update(
            method="nist_800_88_purge",
            wipe_request_id=rec._m14_wipe_request().id,
            media_kind="flash",
        )
    c = x.env["fix.data.wipe.certificate"].create(vals)
    c.action_verify()
    return c


def nid():
    return "48%08d" % (next(_SEQ) * 7129)


def request(x, **vals):
    vals.setdefault("customer_id", x.env["res.partner"].create({"name": "A05 ERP Seller"}).id)
    # e2e walk defect 4: the seller is paid only to their own wallet / account
    seller_wallet(x.env, vals["customer_id"], vals)
    vals.setdefault("customer_nid", nid())
    vals.setdefault("operating_unit_id", x.ou.id)
    vals.setdefault("device_id", device(x).id)
    return x.env[TRD].with_user(x.clerk).create(vals)


def valued(x, rec):
    val = (
        x.env["fix.tradein.valuation"]
        .with_user(x.clerk)
        .create({"tradein_id": rec.id, "resale_estimate": 40000})
    )
    val.action_apply_to_tradein()
    return rec


def screen(x, rec, neir="clear"):
    prov = (
        x.env["fix.tradein.provenance"]
        .with_user(x.clerk)
        .create(
            {
                "tradein_id": rec.id,
                "imei": rec.device_id.imei_1,
                "evidence_ref": "GSMA lookup %s" % rec.name,
                "lock_status": "off",
                "customer_nid_no": rec.customer_nid,
            }
        )
    )
    if neir:
        prov.with_user(x.officer).action_record_neir_result(neir, evidence_ref="NEIR-%s" % rec.name)
    prov.with_user(x.officer).action_clear()
    return prov


def accepted(x, rec=None, **kw):
    rec = rec or request(x, **kw)
    valued(x, rec)
    rec.action_send_offer()
    screen(x, rec)
    rec.action_accept()
    return rec


def collected(x, rec=None, **kw):
    rec = accepted(x, rec, **kw)
    rec.action_collect()
    return rec


def intake_ok(x, rec, value=None):
    """The physical intake verification at the accepted offer (or lower)."""
    vals = {
        "tradein_id": rec.id,
        "verified_condition": "good",
        "verified_value": value or rec.accepted_offer_value,
    }
    if value and value < rec.accepted_offer_value:
        photo = x.env["ir.attachment"].create({"name": "intake.jpg", "raw": b"jpg"})
        vals.update(
            verified_condition="faulty", difference_notes="Cracked", evidence_attachment_id=photo.id
        )
    row = x.env["fix.tradein.intake.check"].with_user(x.clerk2).create(vals)
    row.action_confirm()
    if rec.revision_state == "pending":
        rec.action_accept_revision()
    return row


def approved(x, rec):
    rec.action_request_payout_approval()
    task = inbox_task(rec, x.approver)
    assert task
    task.with_user(x.approver).action_approve(comment="ok")
    assert rec.payout_approval_state == "approved"
    return rec


def paid(x, rec=None, **kw):
    rec = collected(x, rec, **kw)
    intake_ok(x, rec)
    approved(x, rec)
    rec.action_pay()
    return rec


def refurbishing(x, rec):
    rec.write({"wipe_certificate_id": cert(x, rec.device_id, rec).id})
    rec.action_wipe()
    rec.action_refurbish()
    return rec


def finish_steps(x, rec):
    for step in rec.refurbishment_ids.filtered(lambda s: s.state == "pending"):
        step.with_user(x.tech).action_start()
        step.with_user(x.tech).action_complete_repair()


def qa(x, rec, passed=12):
    row = (
        x.env["fix.refurb.qa"]
        .with_user(x.clerk)
        .create(
            {
                "tradein_id": rec.id,
                "tests_total": 12,
                "tests_passed": passed,
                "battery_health_pct": 95,
            }
        )
    )
    row.with_user(x.qa).action_submit_result()
    return row


def graded(x, rec, grade="b"):
    refurbishing(x, rec)
    finish_steps(x, rec)
    qa(x, rec)
    x.env["fix.tradein.grade"].with_user(x.clerk).create(
        {"tradein_id": rec.id, "cosmetic_grade": grade}
    )
    rec.action_grade()
    return rec


def priced(x, rec, price=None):
    rec.write({"resale_value": price or 35000.0})
    rec.with_user(x.clerk).action_request_listing_price()
    rec.with_user(x.pricer).action_approve_listing_price()
    return rec


def listed(x, rec=None, grade="b", price=None, channel="direct", **kw):
    rec = paid(x, rec, **kw)
    graded(x, rec, grade)
    rec.write({"resale_channel": channel})
    priced(x, rec, price)
    rec.action_resale_ready()
    return rec


def lines(move):
    return sorted(
        (ln.account_id.code, round(ln.debit, 2), round(ln.credit, 2)) for ln in move.line_ids
    )


def buyer(x):
    return x.env["res.partner"].create({"name": "A05 ERP Buyer %d" % next(_SEQ)})


# ====================================================================== D3 payout
def test_payout_at_purchase_books_stock_payable_and_tds(w):
    """M14-01/03, FIN-02/03, D3: paid at purchase (collected, intake verified,
    provenance cleared); Dr refurbished stock gross / Cr seller payable net /
    Cr TDS; the TDS on that posted entry; treasury clears the payable."""
    rec = collected(w)
    rec.write({"tds_applicable": True, "tds_rate_pct": 5.0, "taxpayer_tin": "583920174635"})
    intake_ok(w, rec)
    approved(w, rec)
    rec.action_pay()
    assert rec.state == "collected" and rec.paid_at  # the payout does not move the unit
    gross, tds = rec.graded_value, rec.tds_amount
    assert tds > 0
    move = rec.acquisition_move_id
    assert move.state == "posted"
    assert lines(move) == sorted(
        [("110100", gross, 0.0), ("211000", 0.0, round(gross - tds, 2)), ("252000", 0.0, tds)]
    )
    line = rec.withholding_line_id
    assert line.move_id == move and line.amount == tds and line.paid_by_bank
    pay = rec.payout_execution_id
    assert pay.debit_account_id == acct(w, "seller_payable")
    assert pay.operating_unit_id == rec.operating_unit_id
    assert rec.sudo().carrying_cost == gross
    # idempotent: a second press neither pays nor posts again
    refused(rec.action_pay, "already been paid")
    assert len(rec.sudo().ledger_ids) == 1


def test_payout_needs_intake_verification_and_is_capped(w):
    """D3 + M14-11: no payout before the intake is verified; the payout value
    never exceeds the accepted offer; graded_value is never typed."""
    rec = collected(w)
    refused(rec.action_request_payout_approval, "intake verification")
    refused(lambda: rec.write({"graded_value": 1.0}), "workflow|BRU-TRF-09")
    refused(
        lambda: rec.sudo()._guarded().write({"graded_value": rec.accepted_offer_value + 1}),
        "above the accepted offer",
    )


def test_payout_is_not_gated_by_the_wipe_but_resale_is(w):
    """D3: the wipe gate blocks resale, not the payout."""
    rec = paid(w)
    assert not rec.wipe_certificate_id and rec.paid_at


def test_cash_settlement_lifts_tds_and_is_not_bank_paid(w):
    """M14-22 / FIN-13: a cash settlement counts the non-bank default."""
    rec = collected(w)
    rec.write({"tds_applicable": True, "tds_rate_pct": 5.0, "taxpayer_tin": "583920174635"})
    bank_rate = rec.tds_effective_rate_pct
    rec.write({"settlement_method": "cash"})
    assert rec.tds_effective_rate_pct == pytest.approx(bank_rate * 1.5)
    intake_ok(w, rec)
    approved(w, rec)
    rec.action_pay()
    assert rec.withholding_line_id.paid_by_bank is False


def test_accounts_fail_closed_and_tds_must_be_m51s(w):
    """D1: an unset account refuses with its parameter; the TDS account must
    be the one the M51 challan clears."""
    rec = collected(w)
    intake_ok(w, rec)
    approved(w, rec)
    params = w.env["ir.config_parameter"].sudo()
    params.set_param("cd_tradein.account_code.refurb_stock", "")
    refused(rec.action_pay, "cd_tradein.account_code.refurb_stock")
    params.set_param("cd_tradein.account_code.refurb_stock", "110100")
    params.set_param("cd_tax_engine_bd.account_code.tds_payable", "251000")
    rec2 = collected(w)
    rec2.write({"tds_applicable": True, "tds_rate_pct": 5.0, "taxpayer_tin": "583920174635"})
    intake_ok(w, rec2)
    approved(w, rec2)
    refused(rec2.action_pay, "M51 TDS payable")
    assert not rec2.paid_at


def test_ewaste_incentive_blocks_a_second_payout(w):
    """M14-19: an item M18 already approved an incentive for is not paid again."""
    if "fix.ewaste.settlement" not in w.env:
        pytest.skip("cd_ewaste not installed")
    rec = collected(w)
    try:
        with w.env.cr.savepoint():
            coll = (
                w.env["fix.ewaste.collection"]
                .sudo()
                ._guarded()
                .create({"customer_id": rec.customer_id.id, "company_id": rec.company_id.id})
            )
    except Exception as exc:  # cd_ewaste's schema is behind its code in this DB
        if "does not exist" in str(exc):
            pytest.skip("cd_ewaste is not upgraded in this database: %s" % exc)
        raise
    rec.sudo()._guarded().write({"ewaste_collection_id": coll.id})
    intake_ok(w, rec)
    assert not rec._ewaste_incentive_denial()
    w.env["fix.ewaste.settlement"].sudo()._guarded().create(
        {
            "kind": "incentive",
            "collection_id": coll.id,
            "partner_id": rec.customer_id.id,
            "amount": 500,
            "state": "approved",
        }
    )
    refused(rec.action_request_payout_approval, "paid twice")


def test_paid_event_carries_i5_payload(w):
    """I5: tradein.paid {tradein_id, partner_id, amount}."""
    rec = paid(w)
    ev = (
        w.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", "tradein.paid"), ("aggregate_id", "=", rec.id)], limit=1)
    )
    payload = json.loads(ev.payload)
    assert payload["tradein_id"] == rec.id and payload["partner_id"] == rec.customer_id.id
    assert payload["amount"] == pytest.approx(rec.payout_amount)


# ====================================================================== D4 NEIR
def test_neir_result_recorded_by_another_officer_with_evidence(w):
    """M14-16 / D4: the manual NEIR result, by an officer who did not raise
    the trade-in, with evidence; only 'clear' passes the gate."""
    rec = request(w)
    valued(w, rec)
    rec.action_send_offer()
    prov = screen(w, rec, neir=None)
    assert prov.btrc_neir_status == "unchecked"
    refused(rec.action_accept, "NEIR")
    prov2 = (
        w.env["fix.tradein.provenance"]
        .with_user(w.clerk)
        .create(
            {
                "tradein_id": rec.id,
                "imei": rec.device_id.imei_1,
                "evidence_ref": "x",
                "lock_status": "off",
                "customer_nid_no": rec.customer_nid,
            }
        )
    )
    refused(lambda: prov2.with_user(w.officer).action_record_neir_result("clear"), "evidence")
    refused(
        lambda: prov2.with_user(w.clerk).action_record_neir_result("clear", evidence_ref="r"),
        "role",
    )
    w.officer.group_ids |= w.env.ref("cd_workshop.group_fix_workshop_user")
    rec_by_officer = (
        w.env[TRD]
        .with_user(w.officer)
        .create(
            {
                "customer_id": rec.customer_id.id,
                "operating_unit_id": w.ou.id,
                "device_id": device(w).id,
            }
        )
    )
    p3 = (
        w.env["fix.tradein.provenance"]
        .sudo()
        .create({"tradein_id": rec_by_officer.id, "imei": rec_by_officer.device_id.imei_1})
    )
    refused(
        lambda: p3.with_user(w.officer).action_record_neir_result("clear", evidence_ref="r"),
        "another provenance officer",
    )
    prov2.with_user(w.officer).action_record_neir_result("not_found", evidence_ref="NEIR-1")
    prov2.with_user(w.officer).action_clear()
    refused(rec.action_accept, "not_found")
    prov4 = (
        w.env["fix.tradein.provenance"]
        .with_user(w.clerk)
        .create(
            {
                "tradein_id": rec.id,
                "imei": rec.device_id.imei_1,
                "evidence_ref": "x",
                "lock_status": "off",
                "customer_nid_no": rec.customer_nid,
            }
        )
    )
    prov4.with_user(w.officer).action_record_neir_result("clear", evidence_ref="NEIR-2")
    prov4.with_user(w.officer).action_clear()
    rec.action_accept()
    assert rec.state == "accepted"


def test_neir_blocked_is_a_hard_stop(w):
    rec = request(w)
    prov = (
        w.env["fix.tradein.provenance"]
        .with_user(w.clerk)
        .create({"tradein_id": rec.id, "imei": rec.device_id.imei_1})
    )
    prov.with_user(w.officer).action_record_neir_result("blocked", evidence_ref="NEIR-B")
    assert prov.state == "flagged" and rec._provenance_hard_stop()


# ====================================================================== graded stock
def test_graded_stock_is_born_only_from_resale_ready_and_costs_are_guarded(w):
    """M14-04 / XC-09: no plain create; cost, price and origin never typed."""
    dev = device(w)
    grade = w.env["fix.refurb.grade"].search([], limit=1)
    vals = {"device_id": dev.id, "grade_id": grade.id, "tradein_id": 999999, "resale_price": 1.0}
    refused(lambda: w.env["fix.graded.stock"].with_user(w.clerk).create(vals))
    refused(lambda: w.env["fix.graded.stock"].with_user(w.controller).create(vals), "Resale Ready")
    rec = listed(w)
    stock = rec.graded_stock_id
    assert stock.tradein_id == rec.id and stock.resale_price == rec.listing_price
    for field, value in (("resale_price", 1.0), ("acquisition_cost", 0.0), ("tradein_id", 5)):
        refused(lambda f=field, v=value: stock.with_user(w.controller).write({f: v}), "workflow")


def test_cost_and_margin_are_masked(w):
    """M14-30: cost and margin read by costing and finance only."""
    names = w.env["fix.graded.stock"].with_user(w.clerk).fields_get().keys()
    assert "acquisition_cost" not in names and "projected_margin" not in names
    tnames = w.env[TRD].with_user(w.clerk).fields_get().keys()
    assert "carrying_cost" not in tnames and "ledger_ids" not in tnames
    refused(lambda: w.env["fix.refurb.ledger"].with_user(w.clerk).search([]))


def test_sale_rechecks_wipe_neir_and_price(w):
    """M14-04: a flagged unit, or one whose price is not the approved one,
    cannot be reserved or sold; the storefront checkout asks the same."""
    rec = listed(w)
    stock = rec.graded_stock_id
    assert not stock._fix_sale_denial()
    stock.sudo()._guarded().write({"resale_price": 1.0})
    refused(lambda: stock.with_user(w.controller).action_reserve(), "approved listing price")
    stock.sudo()._guarded().write({"resale_price": rec.listing_price})
    prov = rec._provenance_rows()[:1]
    prov.sudo().write({"stolen_hit": True})
    refused(lambda: stock.with_user(w.controller).action_sell(), "cannot be sold")
    refused(lambda: rec.with_user(w.controller).action_counter_sell(buyer(w).id))


# ====================================================================== sale
def test_counter_sale_invoices_vat_posts_cogs_and_provision(w):
    """M14-02/08/15, FIN-04/19, D2/D7: the M20 invoice (M51 VAT on the full
    price), Dr COGS / Cr stock at carrying cost, the grade's provision."""
    rec = listed(w, grade="b", price=34500.0)
    carrying = rec.sudo().carrying_cost
    refused(lambda: rec.with_user(w.clerk).action_counter_sell(buyer(w).id), "Inventory Controller")
    rec.with_user(w.controller).action_counter_sell(buyer(w).id)
    stock = rec.graded_stock_id
    assert stock.state == "sold" and rec.state == "closed" and rec.sale_count == 1
    inv = rec.sale_invoice_id.sudo()
    assert inv.state in ("issued", "paid")
    assert inv.total_payable == pytest.approx(34500.0, abs=0.01)
    cogs = rec._ledger_row("cogs:s1")
    assert lines(cogs.move_id) == sorted([("500000", carrying, 0.0), ("110100", 0.0, carrying)])
    assert rec.sudo().carrying_cost == 0.0
    assert stock._fix_cogs_relieved() == pytest.approx(carrying)
    prov = rec._ledger_row("provision:s1")
    taxable = sum(inv.line_ids.mapped("taxable_amount"))
    assert prov.amount == pytest.approx(round(taxable * 0.03, 2), abs=0.01)
    assert lines(prov.move_id) == sorted(
        [("962000", prov.amount, 0.0), ("201000", 0.0, prov.amount)]
    )
    refused(
        lambda: rec.with_user(w.controller).action_counter_sell(buyer(w).id), "no unit on the shelf"
    )


def test_grade_without_a_provision_rate_refuses_the_sale(w):
    """D7: the provision rate is a parameter that fails closed."""
    rec = listed(w, grade="b")
    w.env["ir.config_parameter"].sudo().set_param("cd_tradein.warranty_provision_pct.b", "")
    refused(
        lambda: rec.with_user(w.controller).action_counter_sell(buyer(w).id),
        "warranty_provision_pct.b",
    )


def test_warranty_end_date_is_calendar_months(w):
    """M14-06: 31 August + 6 months is the end of February, not a crash."""
    rec = request(w)
    war = (
        w.env["fix.tradein.warranty"]
        .sudo()
        ._guarded()
        .create({"tradein_id": rec.id, "months": 6, "start_date": date(2026, 8, 31)})
    )
    assert war.end_date == date(2027, 2, 28)


# ====================================================================== return
def test_return_holds_the_unit_reverses_cogs_and_closes_the_warranty(w):
    """M14-05/07: a sold unit that comes back is held for a new wipe, QA and
    grade; the first warranty closes, its provision released; a second sale
    gets its own warranty."""
    rec = listed(w)
    old_cert = rec.wipe_certificate_id
    rec.with_user(w.controller).action_counter_sell(buyer(w).id)
    stock = rec.graded_stock_id
    w.env[TRD].sudo().consume_graded_stock_sold(
        {"aggregate": "fix.graded.stock", "aggregate_id": stock.id}
    )
    first = w.env["fix.tradein.warranty"].sudo().search([("tradein_id", "=", rec.id)])
    assert len(first) == 1 and first.sale_no == 1
    cogs = rec._ledger_row("cogs:s1").amount
    stock.with_user(w.controller).action_receive_return(reason="buyer changed mind")
    assert stock.state == "returned"
    assert rec.state == "collected" and rec.refurb_cycle == 2 and not rec.wipe_certificate_id
    assert first.state == "returned"
    assert rec._ledger_row("cogs_reversal:s1").amount == cogs
    assert rec._ledger_row("provision_release:s1")
    assert rec.sudo().carrying_cost == pytest.approx(cogs)
    ret = w.env["fix.refurb.return"].sudo().search([("tradein_id", "=", rec.id)])
    assert ret.state == "received"
    # not back on the shelf: unsellable and the old certificate does not pass
    assert stock._fix_sale_denial()
    rec.sudo()._guarded().write({"wipe_certificate_id": old_cert.id})
    refused(rec.action_wipe, "previous sale")
    rec.sudo()._guarded().write({"wipe_certificate_id": False})
    graded(w, rec)
    assert rec._qa_latest().cycle == 2
    priced(w, rec)
    rec.action_resale_ready()
    assert rec.graded_stock_id == stock and stock.state == "in_stock"
    rec.with_user(w.controller).action_counter_sell(buyer(w).id)
    w.env[TRD].sudo().consume_graded_stock_sold(
        {"aggregate": "fix.graded.stock", "aggregate_id": stock.id}
    )
    second = (
        w.env["fix.tradein.warranty"]
        .sudo()
        .search([("tradein_id", "=", rec.id), ("sale_no", "=", 2)])
    )
    assert second and second.state == "active"


def test_storefront_return_is_held_not_restocked(w):
    """M14-05: the storefront refund's restock hands the unit to M14."""
    rec = listed(w)
    stock = rec.graded_stock_id
    product = w.env["product.template"].sudo().search([], limit=1)
    order = (
        w.env["fix.storefront.order"]
        .sudo()
        .create(
            {
                "customer_id": buyer(w).id,
                "total_amount": stock.resale_price,
                "shipping_address": "Dhaka",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "graded_stock_id": stock.id,
                            "quantity": 1,
                            "unit_price": stock.resale_price,
                            "subtotal": stock.resale_price,
                        },
                    )
                ],
            }
        )
    )
    stock.sudo().action_sell()
    ret = w.env["fix.storefront.return"].sudo().new({"order_id": order.id, "name": "RET-T"})
    ret._sf_restock_graded_stock("grade_a")
    assert stock.state == "returned" and rec.state == "collected"


def test_warranty_expiry_releases_the_provision(w):
    rec = listed(w)
    rec.with_user(w.controller).action_counter_sell(buyer(w).id)
    stock = rec.graded_stock_id
    w.env[TRD].sudo().consume_graded_stock_sold(
        {"aggregate": "fix.graded.stock", "aggregate_id": stock.id}
    )
    war = w.env["fix.tradein.warranty"].sudo().search([("tradein_id", "=", rec.id)])
    war._guarded().write({"start_date": date(2020, 1, 1)})
    w.env[TRD].cron_refurb_warranty_expiry()
    assert war.state == "expired"
    rel = rec._ledger_row("provision_release:s1")
    assert lines(rel.move_id) == sorted([("201000", rel.amount, 0.0), ("962000", 0.0, rel.amount)])


# ====================================================================== pricing
def test_listing_price_is_approved_four_eyes_never_below_cost(w):
    """D6 / M14-13 / FIN-23: proposer and enterer never approve; below landed
    cost refuses; Resale Ready needs the approval."""
    rec = paid(w)
    graded(w, rec)
    refused(rec.action_resale_ready, "listing price is not approved")
    rec.with_user(w.pricer).write({"resale_value": 30000})
    rec.with_user(w.clerk).action_request_listing_price()
    refused(lambda: rec.with_user(w.pricer).action_approve_listing_price(), "did not propose")
    refused(lambda: rec.with_user(w.clerk).action_approve_listing_price(), "role")
    rec.with_user(w.pricer2).action_approve_listing_price()
    assert rec.listing_price == 30000
    rec2 = paid(w)
    graded(w, rec2)
    rec2.write({"resale_value": 1000})
    rec2.with_user(w.clerk).action_request_listing_price()
    refused(
        lambda: rec2.with_user(w.pricer).action_approve_listing_price(), "below the landed cost"
    )


def test_markdown_reprices_and_writes_down_to_nrv(w):
    """M14-25 / D6: an approved markdown (another pricing manager) reprices the
    listed unit and writes the stock down to NRV (Dr write-off / Cr stock)."""
    rec = listed(w)
    carrying = rec.sudo().carrying_cost
    md = (
        w.env["fix.refurb.markdown"]
        .with_user(w.pricer)
        .create({"tradein_id": rec.id, "new_price": 11500.0, "reason": "Aged 180 days"})
    )
    md.with_user(w.pricer).action_request()
    refused(lambda: md.with_user(w.pricer).action_approve(), "another pricing manager")
    md.with_user(w.pricer2).action_approve()
    assert rec.listing_price == 11500.0 and rec.graded_stock_id.resale_price == 11500.0
    down = rec._ledger_row("markdown:%d" % md.id)
    assert down.amount == pytest.approx(carrying - rec.sudo().carrying_cost)
    assert lines(down.move_id) == sorted(
        [("610000", down.amount, 0.0), ("110100", 0.0, down.amount)]
    )
    assert not rec.graded_stock_id._fix_sale_denial()


def test_typed_step_cost_counts_only_once_approved_and_is_absorbed(w):
    """M14-12 / FIN-16: a typed step cost needs a supervisor who did not type
    it; it is capitalised at Resale Ready (Dr stock / Cr absorption)."""
    rec = paid(w)
    refurbishing(w, rec)
    step = rec.refurbishment_ids.filtered(lambda s: s.state == "pending")[:1]
    step.with_user(w.tech).write({"parts_cost": 700.0})
    finish_steps(w, rec)
    assert rec.steps_cost == 0.0
    w.supervisor.group_ids |= w.env.ref("base.group_user")
    refused(lambda: step.with_user(w.tech).action_approve_cost(), "Supervisor")
    step.with_user(w.supervisor).action_approve_cost()
    assert rec.steps_cost == 700.0
    qa(w, rec)
    w.env["fix.tradein.grade"].with_user(w.clerk).create(
        {"tradein_id": rec.id, "cosmetic_grade": "b"}
    )
    rec.action_grade()
    priced(w, rec)
    rec.action_resale_ready()
    absorb = rec._ledger_row("refurb:c1")
    assert lines(absorb.move_id) == sorted([("110100", 700.0, 0.0), ("110400", 0.0, 700.0)])
    assert rec.graded_stock_id.sudo().refurbishment_cost == 700.0


def test_battery_comes_from_the_qa(w):
    """M14-14: a typed battery that differs from the QA is refused."""
    rec = paid(w)
    refurbishing(w, rec)
    finish_steps(w, rec)
    qa(w, rec)
    refused(
        lambda: w.env["fix.tradein.grade"]
        .with_user(w.clerk)
        .create({"tradein_id": rec.id, "cosmetic_grade": "b", "battery_health_pct": 100}),
        "measurement",
    )


# ====================================================================== parts only
def _route(w, rec, destination="harvest"):
    row = (
        w.env["fix.refurb.writeoff"]
        .with_user(w.supervisor)
        .create(
            {
                "tradein_id": rec.id,
                "cause": "qa_failed",
                "cause_notes": "Board dead",
                "destination": destination,
            }
        )
    )
    row.action_request()
    return row


def test_qa_failed_unit_goes_parts_only_harvest_relieves_cost_residue_written_off(w):
    """M14-09/20/21, FIN-20: a QA-failed unit is routed to parts only; the
    parts are valued from its cost; the residue is written off (500905)."""
    rec = paid(w)
    refurbishing(w, rec)
    finish_steps(w, rec)
    qa(w, rec, passed=6)
    carrying = rec.sudo().carrying_cost
    row = _route(w, rec)
    row.with_user(w.woapprover).action_approve()
    assert rec.state == "parts_only" and rec.written_off
    refused(rec.action_resale_ready)
    loc = (
        w.env["fix.stock.location"].sudo().search([("company_id", "=", w.env.company.id)], limit=1)
    )
    if not loc:
        Loc = w.env["fix.stock.location"]
        kind = Loc._fields["location_type"].selection
        kind = kind(Loc) if callable(kind) else kind
        loc = Loc.create(
            {"name": "A05 ERP Harvest Bin", "code": "A05EHV", "location_type": kind[0][0]}
        )
    w.env["ir.config_parameter"].sudo().set_param("cd_tradein.harvest_location_id", str(loc.id))
    # M15 stock sits on its valuation suspense account until the GL cut-over
    w.env["ir.config_parameter"].sudo().set_param(
        "cd_inventory.valuation_suspense_account_code", "110500"
    )
    part = (
        w.env["fix.spare.part"]
        .sudo()
        .search([("company_id", "in", (False, w.env.company.id))], limit=1)
    )
    if not part:
        Part = w.env["fix.spare.part"]
        category = Part._fields["part_category"].selection
        category = category(Part) if callable(category) else category
        part = Part.create(
            {
                "name": "A05 ERP Harvest Screen",
                "part_number": "A05E-HV-SCR",
                "part_category": category[0][0],
            }
        )
    over = (
        w.env["fix.tradein.harvest"]
        .with_user(w.clerk)
        .create(
            {
                "tradein_id": rec.id,
                "component": "screen",
                "part_id": part.id,
                "quantity": 1,
                "unit_value": carrying + 1,
            }
        )
    )
    refused(over.action_harvest, "never above it")
    over.write({"unit_value": 2000.0})
    over.action_harvest()
    relief = rec._ledger_row("harvest:%d" % over.id)
    assert relief.amount == 2000.0 and over.receipt_id
    assert lines(relief.move_id) == sorted([("110500", 2000.0, 0.0), ("110100", 0.0, 2000.0)])
    rec.action_close_parts_only()
    wo = rec.sudo().ledger_ids.filtered(lambda r: r.kind == "writeoff")
    assert wo.amount == pytest.approx(carrying - 2000.0)
    assert lines(wo.move_id) == sorted([("610000", wo.amount, 0.0), ("110100", 0.0, wo.amount)])
    assert rec.state == "closed" and rec.sudo().carrying_cost == 0.0


def test_recycle_route_writes_off_at_approval_and_hands_to_m18(w):
    rec = paid(w)
    refurbishing(w, rec)
    finish_steps(w, rec)
    qa(w, rec, passed=6)
    carrying = rec.sudo().carrying_cost
    _route(w, rec, "recycle").with_user(w.woapprover).action_approve()
    wo = rec.sudo().ledger_ids.filtered(lambda r: r.kind == "writeoff")
    assert wo.amount == pytest.approx(carrying)
    rec.action_route_to_recycle()
    assert rec.state == "closed"
    harvest = (
        w.env["fix.tradein.harvest"]
        .sudo()
        .search([("tradein_id", "=", rec.id), ("target", "=", "recycle")])
    )
    assert harvest.state == "harvested"


def test_writeoff_and_override_need_the_amount_tier(w):
    """XC-24: the approver's DOFA tier covers the amount."""
    rec = paid(w)
    refurbishing(w, rec)
    row = _route(w, rec)
    w.woapprover.group_ids -= w.env.ref("cd_entity_config.group_dofa_tier_1")
    refused(lambda: row.with_user(w.woapprover).action_approve(), "DOFA tier")
    rec2 = request(w)
    val = (
        w.env["fix.tradein.valuation"]
        .with_user(w.clerk)
        .create(
            {
                "tradein_id": rec2.id,
                "resale_estimate": 400000,
                "final_offer": 60000,
                "override_reason": "rare",
            }
        )
    )
    val.action_request_override_approval()
    refused(lambda: val.with_user(w.valmgr).action_approve_override(), "tier 2")


# ====================================================================== intake rules
def test_reject_and_revise_only_before_the_wipe(w):
    """M14-10: no rejection or intake revision once the data is wiped."""
    rec = collected(w)
    rec.write({"wipe_certificate_id": cert(w, rec.device_id, rec).id})
    rec.action_wipe()
    refused(lambda: rec.action_reject("changed mind"), "wiped")
    refused(lambda: intake_ok(w, rec), "verified after acceptance")


def test_ou_is_required_and_frozen(w):
    """M14-23."""
    refused(
        lambda: w.env[TRD]
        .with_user(w.clerk)
        .create(
            {
                "customer_id": w.env["res.partner"].create({"name": "x"}).id,
                "device_id": device(w).id,
            }
        ),
        "operating unit",
    )
    rec = request(w)
    valued(w, rec)
    rec.action_send_offer()
    other = w.env["operating.unit"].sudo().search([("id", "!=", w.ou.id)], limit=1)
    if other:
        refused(lambda: rec.write({"operating_unit_id": other.id}), "frozen")


def test_offer_lapses_and_publishes_offer_issued(w):
    """M14-26 / I5: valid_until, tradein.offer_issued, expiry and the cron."""
    rec = request(w)
    valued(w, rec)
    rec.action_send_offer()
    assert rec.offer_valid_until
    ev = (
        w.env["fix.event.outbox"]
        .sudo()
        .search(
            [("event_type", "=", "tradein.offer_issued"), ("aggregate_id", "=", rec.id)], limit=1
        )
    )
    payload = json.loads(ev.payload)
    assert payload == {
        "tradein_id": rec.id,
        "partner_id": rec.customer_id.id,
        "amount": rec.offered_value,
        "valid_until": str(rec.offer_valid_until),
    }
    rec.sudo()._guarded().write({"offer_valid_until": fields.Date.today() - timedelta(days=2)})
    screen(w, rec)
    refused(rec.action_accept, "lapsed")
    assert w.env[TRD].cron_lapse_offers() >= 1
    assert rec.state == "draft"


def test_hold_release_is_read_by_the_gate(w):
    """M14-32: the hold flag is maintained by the gate itself."""
    rec = collected(w)
    assert rec._hold_denial() == "" and rec.hold_released


# ====================================================================== bulk
def test_bulk_lot_reconciles_certified_units_and_allocates_its_price(w):
    """M14-17 / FIN-22."""
    corp = w.env["res.partner"].create({"name": "A05 ERP Corp", "is_company": True})
    lot = (
        w.env["fix.bulk.buyback"]
        .with_user(w.clerk)
        .create(
            {
                "partner_id": corp.id,
                "lot_price_basis": "lot",
                "lot_price": 10000.0,
                "asset_ids": [
                    (0, 0, {"serial_number": "BBK-A-%d" % next(_SEQ)}),
                    (0, 0, {"serial_number": "BBK-B-%d" % next(_SEQ)}),
                ],
            }
        )
    )
    refused(lot.action_open_intakes, "operating unit")
    lot.write({"operating_unit_id": w.ou.id})
    lot.action_open_intakes()
    assert set(lot.asset_ids.mapped("status")) == {"opened"}
    refused(lot.action_close, "wipe-certified")
    lot.action_allocate_lot_price()
    assert sum(lot.asset_ids.mapped("allocated_price")) == pytest.approx(10000.0)
    t = lot.asset_ids[0].tradein_id
    assert t.offered_value == lot.asset_ids[0].allocated_price
    t.sudo()._guarded().write({"device_id": device(w).id})
    t.action_send_offer()
    # a corporate seller's KYC is its verified TIN / trade licence, not an NID
    assert "TIN or trade licence" in t._kyc_denial()


# ====================================================================== I1 / I4
def test_rental_retirement_opens_a_company_owned_intake_with_no_payout(w):
    """I1: route resale -> company-owned intake, no seller payout."""
    Asset = w.env.get("fix.rental.asset")
    if Asset is None:
        pytest.skip("cd_rental_asset not installed")
    dev = device(w)
    tmpl = w.env["product.template"].create({"name": "A05 ERP retired rental unit"})
    item = w.env["fix.catalogue.item"].create({"product_tmpl_id": tmpl.id})
    sku = w.env["fix.rental.sku"].create({"catalogue_item_id": item.id})
    asset = Asset.sudo().create(
        {"name": "A05ERP-RA-%d" % next(_SEQ), "rental_sku_id": sku.id, "purchase_cost": 50000.0}
    )
    asset.sudo()._guarded().write({"status": "retired", "device_id": dev.id})
    event = {
        "aggregate": "fix.rental.asset",
        "aggregate_id": asset.id,
        "payload": {
            "asset_id": asset.id,
            "device_id": dev.id,
            "route": "resale",
            "company_id": w.env.company.id,
            "operating_unit_id": w.ou.id,
            "book_value": 8000.0,
        },
    }
    refused(lambda: w.env[TRD].with_user(w.clerk).consume_rental_asset_retired(event))
    res = w.env[TRD].sudo().consume_rental_asset_retired(event)
    rec = w.env[TRD].browse(res["id"])
    assert rec.source == "rental_retirement" and rec.state == "collected"
    assert rec.sudo().carrying_cost == 8000.0
    assert "company-owned" in rec._tradein_payout_denial()
    assert w.env[TRD].sudo().consume_rental_asset_retired(event)["created"] is False
    other = dict(event, payload=dict(event["payload"], route="recycle"))
    assert w.env[TRD].sudo().consume_rental_asset_retired(other)["created"] is False


def test_buyer_disclosure_is_generated_from_the_record(w):
    """I4 / BRU-TRF-15."""
    rec = paid(w)
    assert not rec.buyer_disclosure_html
    graded(w, rec)
    html = str(rec.buyer_disclosure_html)
    for needle in (
        rec.wipe_certificate_id.name,
        "Grade",
        "95%",
        "months",
        rec._provenance_current().name,
    ):
        assert needle in html, needle


# ====================================================================== marketplace
def test_marketplace_listing_reserves_and_sells_once(w):
    """M14-15: listed at the approved price and reserved; sold to a buyer
    with an M20 invoice; never sold twice."""
    if "fix.marketplace.order" not in w.env:
        pytest.skip("cd_marketplace not installed")
    rec = listed(w, channel="marketplace")
    stock = rec.graded_stock_id
    assert stock.state == "reserved" and rec.marketplace_order_id
    order = w.env["fix.marketplace.order"].sudo().browse(rec.marketplace_order_id)
    order.action_sell_refurb(buyer(w).id)
    assert stock.state == "sold" and order.state == "completed" and order.refurb_invoice_id
    assert rec._ledger_row("cogs:s1")
    refused(lambda: order.action_sell_refurb(buyer(w).id), "not an open refurbished listing")
