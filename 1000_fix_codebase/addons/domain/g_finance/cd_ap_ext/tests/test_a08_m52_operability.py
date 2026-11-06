# cd_ap_ext — A08 finish: can a person do the M52 job on the P03 workspace?
#
# Each test walks the real path as a NON-ADMIN user with the real finance role,
# through the workspace endpoints (/p03/model/write and /p03/model/action) where
# a screen exists. The screens are read by evaluating static/src/a08/m52.js with
# node, and the write whitelist is what controllers/form_fields.py generates from
# those forms, so a field the form does not offer cannot be saved here either.
# Treasury (M50) steps that are not under test run as the superuser and say so.
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
from odoo.addons.cd_ap_ext.models.ap_gl import ap_account
from odoo.addons.cd_ap_ext.tests.test_a08_m52_controls import (
    ACC,
    D,
    _user,
    advance,
    approve,
    balance,
    bill,
    c,  # noqa: F401 - the fixture
    claim,
    disbursed_advance,
    refused,
    run,
    treasury_execute,
    treasury_fail,
)
from odoo.addons.cd_cash_position.models.treasury_common import post_treasury_move
from odoo.addons.cd_p03_portal.controllers.form_fields import editable_by_model
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]

PDF = base64.b64encode(b"%PDF-1.4 a08 evidence").decode()
SRC = Path(portal.__file__).parent / "static" / "src" / "a08"
RECOVERY = "action_confirm_payroll_recovery"


@pytest.fixture(scope="module")
def m52_js(tmp_path_factory):
    """SCREENS and FORM_CHIPS as the browser evaluates them."""
    node = shutil.which("node")
    assert node, "node evaluates the registry: without it these tests prove nothing"
    tmp = tmp_path_factory.mktemp("m52js")
    (tmp / "m52.mjs").write_text((SRC / "m52.js").read_text(encoding="utf-8"), "utf-8")
    (tmp / "run.mjs").write_text(
        "import * as M from './m52.mjs';\n"
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
    """{field: declaration} of a form, every section in a declared tab."""
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
    """The workspace endpoints as a given user, with the whitelist the form
    generator produces (the lead's writable.py is regenerated from the same)."""
    cls = api.P03GenericApiController
    ctl = cls()
    mw = getattr(cls.model_write, "original_endpoint", cls.model_write)
    ma = getattr(cls.model_action, "original_endpoint", cls.model_action)
    mr = getattr(cls.model_records, "original_endpoint", cls.model_records)
    mf = getattr(cls.model_form, "original_endpoint", cls.model_form)
    generated = editable_by_model()
    for model, conf in api.SURFACES.items():
        if model in generated:
            monkeypatch.setitem(conf, "writable", frozenset(generated[model]))

    def call(fn, user, **kw):
        monkeypatch.setattr(api, "request", types.SimpleNamespace(env=c.env(user=user.id)))
        return fn(ctl, **kw)

    return types.SimpleNamespace(
        write=lambda user, **kw: call(mw, user, **kw),
        action=lambda user, **kw: call(ma, user, **kw),
        records=lambda user, **kw: call(mr, user, **kw),
        form=lambda user, **kw: call(mf, user, **kw),
    )


def relay(c, event_type, aggregate, aggregate_id, xmlid=None):  # noqa: F811
    """Deliver the event to its registered consumers, as the relay does."""
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
    subs = c.env["fix.event.consumer"].sudo().search([("event_type", "=", event_type)])
    if xmlid:
        wanted = c.env.ref(xmlid).sudo()
        assert wanted in subs
    errors = [Outbox._relay_deliver(sub, event) for sub in subs]
    assert not any(errors), errors


def treasury_paid(c, execution):  # noqa: F811
    """Treasury (M50), not under test: the bank confirmed the debit. M50 books
    Dr outgoing clearing / Cr bank and publishes payment.executed."""
    ex = execution.sudo()
    amount = ex.amount
    move = post_treasury_move(
        c.env,
        c.company,
        fields.Date.context_today(ex),
        "PAY %s" % ex.name,
        [
            (c.clearing, "Payment", amount, 0.0, ex.partner_id),
            (c.bank.default_account_id, "Paid", 0.0, amount, ex.partner_id),
        ],
    )
    ex._guarded().write(
        {
            "state": "executed",
            "released_amount": amount,
            "confirmation_source": "statement",
            "executed_at": fields.Datetime.now(),
            "move_id": move.id,
        }
    )
    ex._publish_executed()


@pytest.fixture
def paying(c):  # noqa: F811
    """The clearing account M50 debits, configured as on a live company."""
    Account = c.env["account.account"]
    c.clearing = Account.search(
        [("code", "=", "990199"), ("company_ids", "in", c.company.id)], limit=1
    ) or Account.create(
        {
            "code": "990199",
            "name": "Test outgoing clearing",
            "account_type": "asset_current",
            "company_ids": [(6, 0, c.company.ids)],
        }
    )
    c.env["ir.config_parameter"].sudo().set_param(
        "cd_cash_position.account_code.outgoing_clearing", "990199"
    )
    return c


def execution_of(c, model, res_id):  # noqa: F811
    return (
        c.env["fix.payment.execution"]
        .sudo()
        .search([("source_model", "=", model), ("source_id", "=", res_id)])
    )


# =========================================================== S1 / M52-1
def test_s1_queue_propose_and_second_person_confirm(c, ui, m52_js):  # noqa: F811
    """The whole dead end: an unconfirmed account, nobody able to confirm it."""
    fields_ = offered(m52_js, "M52-form-bank-change")
    for name in ("partner_id", "acc_number", "verification_ref", "evidence_file"):
        assert not fields_[name].get("readonly"), name
    for name in ("state", "proposed_by_id", "confirmed_by_id", "result_bank_id"):
        assert fields_[name]["readonly"], name
    surface = actions(m52_js, "M52-bank-queue")
    assert {"action_propose", "action_confirm", "action_reject"} <= set(surface)
    assert m52_js["chips"]["M52:__by_screen__"]["M52-bank-queue"] == "M52-form-bank-change"

    payee = c.env["res.partner"].create({"name": "A08 Landlord"})
    account = c.env["res.partner.bank"].create(
        {"partner_id": payee.id, "acc_number": "A08-LANDLORD-1", "fix_routing_number": "175260346"}
    )
    assert account._fix_payable_problem()

    # the queue job opens the row, once
    Change = c.env["fix.payee.bank.change"]
    Change.sudo()._cron_open_confirmation_queue()
    row = Change.sudo().search([("partner_bank_id", "=", account.id)])
    assert len(row) == 1 and row.state == "draft" and row.acc_number == "A08-LANDLORD-1"
    assert not row.verified_by_id
    Change.sudo()._cron_open_confirmation_queue()
    assert Change.sudo().search_count([("partner_bank_id", "=", account.id)]) == 1

    # a queue row cannot be proposed until the call-back is recorded
    refusal = ui.action(c.acc3, model=row._name, ids=row.ids, method="action_propose")
    assert refusal["success"] is False and "call-back" in refusal["error"]

    saved = ui.write(
        c.acc3,
        model=row._name,
        record_id=row.id,
        values={
            "verification_ref": "Called Mr Rahman on the number in the lease, 7 Nov 11:05",
            "evidence_file": PDF,
            "evidence_filename": "callback-note.pdf",
        },
    )
    assert "error" not in saved, saved
    assert row.evidence_names == "callback-note.pdf"
    assert ui.action(c.acc3, model=row._name, ids=row.ids, method="action_propose")["success"]
    assert (row.state, row.proposed_by_id, row.verified_by_id) == ("proposed", c.acc3, c.acc3)

    # the proposer and a plain accountant do not confirm
    assert not ui.action(c.acc3, model=row._name, ids=row.ids, method="action_confirm")["success"]
    assert not ui.action(c.acc1, model=row._name, ids=row.ids, method="action_confirm")["success"]
    done = ui.action(c.mgr, model=row._name, ids=row.ids, method="action_confirm")
    assert done["success"], done
    assert row.state == "confirmed" and row.confirmed_by_id == c.mgr
    assert account.fix_confirmed and account.fix_verification_ref.startswith("Called Mr Rahman")
    assert account._fix_payable_problem() is False

    # now confirmed, the job leaves it alone; a later edit puts it back in the queue
    Change.sudo()._cron_open_confirmation_queue()
    assert Change.sudo().search_count([("partner_bank_id", "=", account.id)]) == 1
    account.write({"acc_number": "A08-LANDLORD-2"})
    assert account._fix_payable_problem()
    Change.sudo()._cron_open_confirmation_queue()
    assert Change.sudo().search_count(
        [("partner_bank_id", "=", account.id), ("state", "=", "draft")]
    )


def test_s1_new_account_from_the_form_and_reject(c, ui):  # noqa: F811
    payee = c.env["res.partner"].create({"name": "A08 One-off vendor"})
    res = ui.write(
        c.acc3,
        model="fix.payee.bank.change",
        record_id=False,
        values={
            "partner_id": payee.id,
            "acc_number": "A08-NEW-77",
            "routing_number": "175260346",
            "verification_ref": "Called the number on the signed vendor form",
        },
    )
    assert "error" not in res, res
    row = c.env["fix.payee.bank.change"].browse(res["id"])
    assert ui.action(c.acc3, model=row._name, ids=row.ids, method="action_propose")["success"]
    # a proposed change is fixed
    locked = ui.write(c.acc3, model=row._name, record_id=row.id, values={"acc_number": "MULE"})
    assert "error" in locked and row.acc_number == "A08-NEW-77"
    # the reason is the prompt the surface asks for
    assert not ui.action(c.mgr, model=row._name, ids=row.ids, method="action_reject")["success"]
    rej = ui.action(
        c.mgr, model=row._name, ids=row.ids, method="action_reject", kwargs={"reason": "Wrong bank"}
    )
    assert rej["success"] and (row.state, row.reject_reason) == ("rejected", "Wrong bank")
    assert not c.env["res.partner.bank"].search([("acc_number", "=", "A08-NEW-77")])


def test_s1_queue_leaves_out_own_accounts_and_confirmed_ones(c):  # noqa: F811
    own = c.env["res.partner.bank"].create(
        {"partner_id": c.company.partner_id.id, "acc_number": "A08-HOUSE-BANK"}
    )
    Change = c.env["fix.payee.bank.change"].sudo()
    Change._cron_open_confirmation_queue()
    assert not Change.search([("partner_bank_id", "=", own.id)])
    # c.vbank was confirmed by the fixture; its only change is the confirmed one
    assert not Change.search([("partner_bank_id", "=", c.vbank.id), ("state", "=", "draft")])
    cron = c.env.ref("cd_ap_ext.ir_cron_payee_confirmation_queue").sudo()
    assert cron.active and "_cron_open_confirmation_queue" in cron.code


# =========================================================== M52-12
def test_m52_12_matrix_change_from_the_screen(c, ui, m52_js):  # noqa: F811
    assert {"action_apply", "action_reject"} <= set(actions(m52_js, "M52-matrix-change"))
    assert m52_js["screens"]["M52-matrix"]["create"] is False
    assert m52_js["chips"]["M52:__by_screen__"]["M52-matrix-change"] == "M52-form-matrix-change"
    fields_ = offered(m52_js, "M52-form-matrix-change")
    assert not fields_["amount_min"].get("readonly") and fields_["state"]["readonly"]

    level2 = c.env["fix.ap.approval.rule"].search(
        [("company_id", "=", c.company.id), ("level", "=", 2)]
    )
    group = level2.group_id
    # the accountant does not propose
    denied = ui.write(
        c.acc1,
        model="fix.ap.approval.rule.change",
        record_id=False,
        values={"rule_id": level2.id, "amount_min": 1.0, "reason": "x"},
    )
    assert "error" in denied
    # what the form leaves empty stays as the row has it
    res = ui.write(
        c.mgr,
        model="fix.ap.approval.rule.change",
        record_id=False,
        values={"rule_id": level2.id, "amount_min": 750000.0, "reason": "CFO memo"},
    )
    assert "error" not in res, res
    change = c.env["fix.ap.approval.rule.change"].browse(res["id"])
    assert (change.name, change.level, change.group_id) == (level2.name, 2, group)
    assert level2.amount_min == 500000.0
    # fixed once proposed, and the proposer does not confirm
    assert "error" in ui.write(
        c.mgr, model=change._name, record_id=change.id, values={"reason": "z"}
    )
    assert not ui.action(c.mgr, model=change._name, ids=change.ids, method="action_apply")[
        "success"
    ]
    assert ui.action(c.mgr2, model=change._name, ids=change.ids, method="action_apply")["success"]
    assert level2.amount_min == 750000.0 and change.state == "applied"
    # an accounting level stays accounting: refused at the proposal
    bad = ui.write(
        c.mgr,
        model="fix.ap.approval.rule.change",
        record_id=False,
        values={
            "rule_id": level2.id,
            "group_id": c.env.ref("base.group_user").id,
            "reason": "probe",
        },
    )
    assert "error" in bad


# =========================================================== M52-10
def test_m52_10_psr_evidence_from_the_form_makes_a_filer(c, ui, m52_js):  # noqa: F811
    fields_ = offered(m52_js, "M52-form-taxprofile")
    assert fields_["psr_evidence_file"]["type"] == "binary"
    assert fields_["tds_exempt_file"]["type"] == "binary"
    assert not fields_["tds_exempt_certificate_ref"].get("readonly")
    vendor = c.env["res.partner"].create({"name": "A08 New filer"})
    res = ui.write(
        c.acc1,
        model="fix.vendor.tax.profile",
        record_id=False,
        values={
            "partner_id": vendor.id,
            "taxpayer_type": "company",
            "tin": "123456789012",
            "psr_reference": "PSR-1",
            "psr_valid_until": "2099-06-30",
        },
    )
    assert "error" not in res, res
    profile = c.env["fix.vendor.tax.profile"].browse(res["id"])
    # typed, unevidenced: not a filer, and the bill suffers the uplift
    assert not profile.is_filer_on(D)
    uplifted = bill(c, 100000.0, vendor=vendor)
    assert uplifted.line_ids.tds_multiplier == 1.5
    saved = ui.write(
        c.acc1,
        model=profile._name,
        record_id=profile.id,
        values={"psr_evidence_file": PDF, "psr_evidence_filename": "psr.pdf"},
    )
    assert "error" not in saved, saved
    assert profile.is_filer_on(D) and profile.psr_attachment_ids.name == "psr.pdf"
    assert base64.b64decode(profile.psr_attachment_ids.datas).startswith(b"%PDF-1.4")
    assert profile.psr_evidence_names == "psr.pdf"
    assert bill(c, 100000.0, vendor=vendor).line_ids.tds_multiplier == 1.0


def test_m52_10_exemption_certificate_from_the_form_honours_the_tick(c, ui):  # noqa: F811
    tick = {"tds_exempt": True}
    b = bill(c, 100000.0, **tick)
    assert refused(c.env, lambda: b.with_user(c.acc1).action_submit_approval())
    saved = ui.write(
        c.acc1,
        model=c.profile._name,
        record_id=c.profile.id,
        values={
            "tds_exempt_certificate_ref": "NBR-EX-9",
            "tds_exempt_valid_until": "2099-06-30",
            "tds_exempt_file": PDF,
            "tds_exempt_filename": "exemption.pdf",
        },
    )
    assert "error" not in saved, saved
    assert c.profile.is_tds_exempt_on(D)
    b2 = bill(c, 100000.0, **tick)
    assert b2.tds_amount == 0.0
    b2.with_user(c.acc1).action_submit_approval()
    assert b2.approval_state == "to_approve"


def test_m52_10_bill_form_offers_tds_and_vds_and_reads_the_defaults(c, ui, m52_js):  # noqa: F811
    cfg = m52_js["screens"]["M52-form-bill"]
    grid = {f["name"] for f in cfg["lines"]["fields"]}
    assert {"tds_category", "tds_exempt"} <= grid
    header = offered(m52_js, "M52-form-bill")
    assert not header["vds_rate_id"].get("readonly")
    assert not header["payment_channel"].get("readonly")

    Rate = c.env["fix.tax.rate"].sudo()
    vds = Rate.search([("tax_kind", "=", "vds")], limit=1)
    tds = Rate.search([("tax_kind", "=", "tds")], limit=1)
    assert vds and tds
    c.profile.write({"default_vds_rate_id": vds.id, "default_tds_category": "technical_services"})
    res = ui.write(
        c.acc1,
        model="fix.vendor.invoice",
        record_id=False,
        values={
            "invoice_ref": "A08-DEFAULTS-1",
            "vendor_id": c.vendor.id,
            "bill_type": "non_po",
            "invoice_date": str(D),
            "operating_unit_id": c.ou.id,
        },
        lines={
            "field": "line_ids",
            "rows": [
                {
                    "values": {
                        "product_id": c.product.id,
                        "description": "Service",
                        "quantity": 1,
                        "unit_price": 1000.0,
                    }
                }
            ],
        },
    )
    assert "error" not in res, res
    made = c.env["fix.vendor.invoice"].browse(res["id"])
    assert made.vds_rate_id == vds, "default_vds_rate_id was read by nothing"
    assert made.line_ids.tds_category == "technical_services"
    # the person can clear it on the draft, and it stays cleared
    assert "error" not in ui.write(
        c.acc1, model=made._name, record_id=made.id, values={"vds_rate_id": False}
    )
    assert not made.vds_rate_id
    # the form's list shows every tax rate: a TDS row is no VDS code
    assert refused(c.env, lambda: made.with_user(c.acc1).write({"vds_rate_id": tds.id}))
    assert refused(
        c.env, lambda: c.profile.with_user(c.acc1).write({"default_vds_rate_id": tds.id})
    )
    # a vendor outside VDS takes no default, and a typed code is refused at submission
    c.profile.write({"vds_exempt": True})
    outside = bill(c, 1000.0)
    assert not outside.vds_rate_id
    outside.with_user(c.acc1).write({"vds_rate_id": vds.id})
    err = refused(c.env, lambda: outside.with_user(c.acc1).action_submit_approval())
    assert err and "VDS Not Applicable" in str(err)


def test_m52_10_paid_by_bank_follows_the_channel(c):  # noqa: F811
    banked = approve(c, bill(c, 100000.0))
    line = banked.withholding_line_ids.filtered(lambda w: w.tax_kind == "tds")
    assert line.paid_by_bank is True and line.multiplier == 1.0

    cash = bill(c, 100000.0, payment_channel="non_bank")
    assert cash.line_ids.tds_rate_id.non_filer_applies, "the fixture rate must carry the uplift"
    assert cash.line_ids.tds_multiplier == 1.5
    approve(c, cash)
    deduction = cash.withholding_line_ids.filtered(lambda w: w.tax_kind == "tds")
    assert deduction.paid_by_bank is False and deduction.multiplier == 1.5
    # the GL and the certificate carry the one figure, and M51 agrees it is right
    assert deduction.amount == cash.tds_amount and deduction.statutory_shortfall == 0.0
    assert deduction.defaults_count == 1
    # the channel is fixed by the approval, and a bank run does not take the bill
    assert refused(c.env, lambda: cash.with_user(c.acc1).write({"payment_channel": "bank"}))
    run = c.env["fix.payment.run"].with_user(c.acc1).create({"due_by": date(2026, 12, 31)})
    assert cash not in run._candidate_bills() and banked in run._candidate_bills()


# =========================================================== M52-7, BRU-APE-16
def test_m52_7_receipt_on_the_claim_line_form_lets_the_claim_submit(c, ui, m52_js):  # noqa: F811
    fields_ = offered(m52_js, "M52-form-claim-line")
    assert fields_["receipt_file"]["type"] == "binary" and fields_["receipt_names"]["readonly"]
    assert m52_js["chips"]["M52:__by_screen__"]["M52-claim-lines"] == "M52-form-claim-line"
    cl = claim(
        c,
        c.plain,
        c.emp_plain,
        [{"category_id": c.hotel.id, "unit_amount": 3000.0, "date": D}],
    )
    err = refused(c.env, lambda: cl.with_user(c.plain).action_submit())
    assert err and "receipt required" in str(err)

    # the claimant reaches their own line on the screen, and nobody else's
    other = claim(c, c.p2, c.emp_p2, [{"category_id": c.other.id, "unit_amount": 10.0, "date": D}])
    seen = ui.records(c.plain, model="fix.expense.claim.line", cols=["claim_id", "receipt_names"])
    ids = {row["id"] for row in seen["rows"]}
    assert cl.line_ids.id in ids and other.line_ids.id not in ids
    # as declared by the form, the claimant attaches the receipt
    res = ui.write(
        c.plain,
        model="fix.expense.claim.line",
        record_id=cl.line_ids.id,
        values={"receipt_file": PDF, "receipt_filename": "hotel.pdf"},
    )
    assert "error" not in res, res
    assert cl.line_ids.receipt_attachment_ids.name == "hotel.pdf"
    assert cl.line_ids.receipt_names == "hotel.pdf"
    cl.with_user(c.plain).action_submit()
    assert cl.state == "submitted"
    # a line of a submitted claim no longer takes a receipt
    late = ui.write(
        c.plain,
        model="fix.expense.claim.line",
        record_id=cl.line_ids.id,
        values={"receipt_file": PDF, "receipt_filename": "again.pdf"},
    )
    assert "error" in late and len(cl.line_ids.receipt_attachment_ids) == 1
    # the same file on a second claim is the existing duplicate refusal
    second = claim(
        c, c.plain, c.emp_plain, [{"category_id": c.hotel.id, "unit_amount": 3000.0, "date": D}]
    )
    ui.write(
        c.plain,
        model="fix.expense.claim.line",
        record_id=second.line_ids.id,
        values={"receipt_file": PDF, "receipt_filename": "hotel-copy.pdf"},
    )
    err = refused(c.env, lambda: second.with_user(c.plain).action_submit())
    assert err and "reimbursed once" in str(err)


def test_bru_ape_16_cost_centre_refused_when_missing_and_carried_to_the_gl(c, m52_js):  # noqa: F811
    grid = {f["name"] for f in m52_js["screens"]["M52-form-claim"]["lines"]["fields"]}
    assert "cost_centre" in grid
    line = {"category_id": c.other.id, "unit_amount": 500.0, "date": D, "cost_centre": ""}
    cl = claim(c, c.plain, c.emp_plain, [line])
    err = refused(c.env, lambda: cl.with_user(c.plain).action_submit())
    assert err and "cost centre" in str(err)
    cl.line_ids.with_user(c.plain).write({"cost_centre": "DHK-FIELD"})
    cl.with_user(c.plain).action_submit()
    cl.with_user(c.acc1).action_approve()
    expense_item = cl.move_id.line_ids.filtered(lambda ml: ml.debit > 0)
    dimension = (
        c.env["fix.journal.dimension"].sudo().search([("move_line_id", "=", expense_item.id)])
    )
    assert dimension.cost_centre == "DHK-FIELD"
    # the configuration key switches the refusal off
    c.env["ir.config_parameter"].sudo().set_param("cd_ap_ext.claim_require_cost_centre", "0")
    free = claim(c, c.plain, c.emp_plain, [line])
    free.with_user(c.plain).action_submit()
    assert free.state == "submitted"


# =========================================================== M52-4
def test_m52_4_request_payment_takes_the_lock_one_execution(c, paying):  # noqa: F811
    b = approve(c, bill(c, 9000.0))
    b.with_user(c.acc1).action_request_payment()
    # the lock is taken at once, before treasury has even read the event
    lock = c.env["fix.ap.bill.payment"].sudo().search([("bill_id", "=", b.id)])
    assert lock.state == "open" and b.payment_state == "in_run"
    # the run does not re-propose the bill: this was the second execution
    run = c.env["fix.payment.run"].with_user(c.acc1).create({"due_by": date(2026, 12, 31)})
    assert b not in run._candidate_bills()
    assert refused(c.env, lambda: run.with_user(c.acc1).action_propose())
    # and a second press is refused
    assert refused(c.env, lambda: b.with_user(c.acc1).action_request_payment())
    # a plain user does not ask treasury to pay
    other = approve(c, bill(c, 100.0))
    assert refused(c.env, lambda: other.with_user(c.plain).action_request_payment())

    relay(c, "payment.requested", "fix.vendor.invoice", b.id)
    ex = execution_of(c, b._name, b.id)
    assert len(ex) == 1 and ex.amount == b.total_payable
    assert (
        not c.env["fix.payment.execution"]
        .sudo()
        .search(
            [("source_model", "=", "fix.payment.run.line"), ("partner_id", "=", b.vendor_id.id)]
        )
    )
    # treasury pays: the bill is paid, the lock closed, the payable cleared
    before = balance(c.env, ap_account(c.env, c.company, "ap"))
    treasury_paid(c, ex)
    relay(
        c,
        "payment.executed",
        "fix.payment.execution",
        ex.id,
        "cd_ap_ext.consumer_payment_executed_ap",
    )
    assert (b.payment_state, lock.state, lock.execution_id) == ("paid", "paid", ex)
    assert balance(c.env, ap_account(c.env, c.company, "ap")) == round(before + b.total_payable, 2)
    assert balance(c.env, c.clearing) == 0.0
    # a replay moves nothing
    move = b.payment_move_id
    relay(c, "payment.executed", "fix.payment.execution", ex.id)
    assert b.payment_move_id == move and balance(c.env, c.clearing) == 0.0


def test_m52_4_failed_request_keeps_the_lock_cancelled_returns_to_the_pool(c, paying):  # noqa: F811
    b = approve(c, bill(c, 9000.0))
    b.with_user(c.acc1).action_request_payment()
    relay(c, "payment.requested", "fix.vendor.invoice", b.id)
    ex = execution_of(c, b._name, b.id)
    run = c.env["fix.payment.run"].with_user(c.acc1).create({"due_by": date(2026, 12, 31)})
    # the bank rejects: treasury may re-queue this very instruction, so no run may pay it
    ex.sudo()._guarded().write({"state": "failed", "failure_reason": "account closed"})
    ex._publish_failed("account closed")
    relay(
        c, "payment.failed", "fix.payment.execution", ex.id, "cd_ap_ext.consumer_payment_failed_ap"
    )
    assert b.payment_state == "in_run" and b.payment_failure == "account closed"
    assert b not in run._candidate_bills()
    # treasury cancels: nothing will pay it now, so it returns to the pool
    ex.sudo().action_cancel()
    assert b in run._candidate_bills()
    assert b.payment_state == "not_paid" and not b._ap_live_payment()
    # asking treasury again would only find the cancelled instruction
    assert refused(c.env, lambda: b.with_user(c.acc1).action_request_payment())


# =========================================================== M52-9
def _approved_claim(c, amount=700.0):  # noqa: F811
    cl = claim(
        c, c.plain, c.emp_plain, [{"category_id": c.other.id, "unit_amount": amount, "date": D}]
    )
    cl.with_user(c.plain).action_submit()
    cl.with_user(c.acc1).action_approve()
    relay(c, "payment.requested", "fix.expense.claim", cl.id)
    return cl, execution_of(c, cl._name, cl.id)


def test_m52_9_payment_executed_takes_the_claim_to_paid(c, paying):  # noqa: F811
    cl, ex = _approved_claim(c)
    payable = c.a["employee_payable"]
    assert cl.state == "approved" and balance(c.env, payable) <= -700.0
    before = balance(c.env, payable)
    treasury_paid(c, ex)
    assert balance(c.env, c.clearing) == 700.0  # M50's side alone leaves it open
    relay(
        c,
        "payment.executed",
        "fix.payment.execution",
        ex.id,
        "cd_ap_ext.consumer_payment_executed_ap",
    )
    assert cl.state == "paid"
    assert balance(c.env, payable) == round(before + 700.0, 2) and balance(c.env, c.clearing) == 0.0
    # a return after clearing undoes it, and the same instruction can pay again
    ex.sudo()._fix_return_after_clearing("cheque returned")
    relay(
        c, "payment.failed", "fix.payment.execution", ex.id, "cd_ap_ext.consumer_payment_failed_ap"
    )
    assert cl.state == "approved" and cl.payment_failure == "cheque returned"
    assert not cl.payment_move_id and balance(c.env, payable) == before


def test_m52_9_a_rejected_payment_is_visible_on_the_claim(c, paying, m52_js):  # noqa: F811
    assert "payment_failure" in m52_js["screens"]["M52-claims"]["cols"]
    cl, ex = _approved_claim(c)
    ex.sudo()._guarded().write({"state": "failed", "failure_reason": "invalid account"})
    ex._publish_failed("invalid account")
    relay(c, "payment.failed", "fix.payment.execution", ex.id)
    assert cl.state == "approved" and cl.payment_failure == "invalid account"


def test_m52_9_an_asserted_execution_pays_nothing(c, paying):  # noqa: F811
    cl, ex = _approved_claim(c)
    ex.sudo().action_execute()  # legacy: no bank evidence
    relay(c, "payment.executed", "fix.payment.execution", ex.id)
    assert cl.state == "approved"


def test_m52_9_consumers_refuse_a_direct_call(c):  # noqa: F811
    Events = c.env["fix.ap.payment.events"].with_user(c.mgr)
    assert refused(c.env, lambda: Events.consume_payment_executed({"aggregate_id": 1}))
    assert refused(c.env, lambda: Events.consume_payment_failed({"aggregate_id": 1}))


def test_m52_9_settling_an_advance_pays_its_claims(c):  # noqa: F811
    adv = disbursed_advance(c)
    cl = claim(
        c,
        c.plain,
        c.emp_plain,
        [{"category_id": c.other.id, "unit_amount": 5000.0, "date": D}],
        advance_id=adv.id,
    )
    cl.with_user(c.plain).action_submit()
    cl.with_user(c.acc1).action_approve()
    assert cl.state == "approved"
    adv.with_user(c.acc1).action_settle()
    assert (adv.state, cl.state) == ("settled", "paid")


# =========================================================== M52-8
def test_m52_8_payroll_recovery_from_the_screen(c, ui, m52_js):  # noqa: F811
    surface = actions(m52_js, "M52-advances")
    asked = {a["kwarg"] for a in surface["action_confirm_payroll_recovery"]["asks"]}
    assert asked == {"amount", "reference"}
    _user(c.env, "a08m52_payroll", ["cd_payroll_bd.group_payroll_officer"])
    adv = disbursed_advance(c, recovery_method="payroll")
    adv.with_user(c.acc1).action_record_recovery()
    assert adv.recovery_state == "requested"
    # the request reaches a person
    relay(
        c,
        "advance.recovery_requested",
        "fix.employee.advance",
        adv.id,
        "cd_ap_ext.consumer_advance_recovery_requested",
    )
    todo = adv.sudo().activity_ids
    assert todo and todo[0].user_id.has_group("cd_payroll_bd.group_payroll_officer")
    assert "5000.00" in todo[0].summary
    # the surface takes what payroll reports, and needs the reference
    kw = {"amount": 5000.0, "reference": ""}
    no_ref = ui.action(c.acc1, model=adv._name, ids=adv.ids, method=RECOVERY, kwargs=kw)
    assert no_ref["success"] is False and adv.recovery_state == "requested"
    kw["reference"] = "PAYSLIP/2026/11/0042"
    res = ui.action(c.acc1, model=adv._name, ids=adv.ids, method=RECOVERY, kwargs=kw)
    assert res["success"], res
    assert (adv.state, adv.recovered_amount) == ("settled", 5000.0)
    assert balance(c.env, c.a["employee_advance"]) == 0.0


def test_m52_8_salary_payable_has_a_default_account(c):  # noqa: F811
    c.env["ir.config_parameter"].sudo().search(
        [("key", "=", "cd_ap_ext.account_code.salary_payable")]
    ).unlink()
    Account = c.env["account.account"]
    salary = Account.search(
        [("code", "=", "230000"), ("company_ids", "in", c.company.id)], limit=1
    ) or Account.create(
        {
            "code": "230000",
            "name": "Salary Payable",
            "account_type": "liability_current",
            "company_ids": [(6, 0, c.company.ids)],
        }
    )
    assert ap_account(c.env, c.company, "salary_payable") == salary


def test_m52_8_cancel_unsticks_a_failed_advance(c, ui, m52_js):  # noqa: F811
    assert actions(m52_js, "M52-advances")["action_cancel"]["kwarg"] == "reason"
    stuck = advance(c, c.acc2, c.emp_plain)
    stuck.with_user(c.acc1).action_approve()
    treasury_fail(c, stuck.execution_id)
    # it blocks the employee's next advance
    fresh = advance(c, c.acc2, c.emp_plain, 1000.0)
    assert refused(c.env, lambda: fresh.with_user(c.acc1).action_approve())
    assert not ui.action(c.acc1, model=stuck._name, ids=stuck.ids, method="action_cancel")[
        "success"
    ]
    assert not ui.action(
        c.plain, model=stuck._name, ids=stuck.ids, method="action_cancel", kwargs={"reason": "x"}
    )["success"]
    res = ui.action(
        c.acc1,
        model=stuck._name,
        ids=stuck.ids,
        method="action_cancel",
        kwargs={"reason": "Bank rejected, trip cancelled"},
    )
    assert res["success"], res
    assert stuck.state == "cancelled" and stuck.cancel_reason == "Bank rejected, trip cancelled"
    assert stuck.execution_id.sudo().state == "cancelled"
    fresh.with_user(c.acc1).action_approve()
    assert fresh.state == "approved"


def test_m52_8_cancel_refused_once_the_money_moved(c):  # noqa: F811
    paid = disbursed_advance(c)
    assert refused(c.env, lambda: paid.with_user(c.acc1).action_cancel(reason="x"))
    with_bank = advance(c, c.acc2, c.emp_nouser)
    with_bank.with_user(c.acc1).action_approve()
    treasury_execute(c, with_bank.execution_id)
    err = refused(c.env, lambda: with_bank.with_user(c.acc1).action_cancel(reason="x"))
    assert err and "treasury" in str(err).lower()
    assert with_bank.state == "approved"


# =========================================================== M52-11
def test_m52_11_who_signs_a_level_can_refuse_it(c):  # noqa: F811
    b = bill(c, 9000.0)
    b.with_user(c.acc1).action_submit_approval()
    assert b.approval_levels_required == 1
    # a Billing user neither signs nor refuses
    assert refused(c.env, lambda: b.with_user(c.bill).action_reject())
    # the manager holds no accountant group: he signs level 1, and now refuses it
    assert b._next_level().group_id == c.env.ref(ACC)
    assert c.env.ref(ACC) not in c.mgr.all_group_ids, "the fixture must show the gap"
    b.with_user(c.mgr).action_reject()
    assert b.approval_state == "rejected"
    # the switch that stops a higher level signing lower stops refusing too
    c.env["ir.config_parameter"].sudo().set_param("cd_ap_ext.higher_level_may_approve_lower", "0")
    again = bill(c, 9000.0)
    again.with_user(c.acc1).action_submit_approval()
    assert refused(c.env, lambda: again.with_user(c.mgr).action_reject())


def test_evidence_upload_helper_needs_a_file(c):  # noqa: F811
    profile = c.profile
    count = len(profile.psr_attachment_ids)
    profile.write({"psr_evidence_filename": "typed-name-only.pdf"})
    assert len(profile.psr_attachment_ids) == count
    # the form re-posts nothing it does not hold: the upload field reads back empty
    assert not profile.psr_evidence_file


def test_s1_a_payee_with_no_account_is_an_exception_not_a_block(c, m52_js):  # noqa: F811
    """One vendor with no confirmed account used to stop the run for everyone:
    submit refused the whole run, and the form never showed which line was at fault."""
    good = bill(c, 10000.0)
    approve(c, good)
    stranger = c.env["res.partner"].create({"name": "A08 Vendor With No Bank"})
    stuck = bill(c, 7000.0, vendor=stranger)
    approve(c, stuck)
    r = run(c)
    r.with_user(c.acc1).action_propose()
    lines = {line.partner_id: line for line in r.line_ids}
    assert lines[stranger].state == "skipped"
    assert "no bank account" in lines[stranger].skip_reason
    assert lines[c.vendor.commercial_partner_id].state == "proposed"
    # the run goes ahead for the payable vendor, and only for them
    r.with_user(c.acc1).action_submit()
    assert r.state == "to_approve"
    assert r.total_amount == lines[c.vendor.commercial_partner_id].amount
    # the skipped bill stays in the pool, not locked to this run
    assert stuck.payment_state == "not_paid"
    # the run's form shows the payees and why one dropped out, and edits none of them
    form = m52_js["screens"]["M52-form-aprun"]
    assert form["lines"]["field"] == "line_ids" and form["lines"]["readonlyGrid"] is True
    shown = {f["name"] for f in form["lines"]["fields"]}
    assert {"partner_id", "amount", "state", "skip_reason"} <= shown


def test_s1_every_payee_unpayable_still_refuses_at_submit(c):  # noqa: F811
    stranger = c.env["res.partner"].create({"name": "A08 Only Vendor With No Bank"})
    approve(c, bill(c, 7000.0, vendor=stranger))
    r = run(c)
    r.with_user(c.acc1).action_propose()
    assert set(r.line_ids.mapped("state")) <= {"skipped", "proposed"}
    if not r.line_ids.filtered(lambda line: line.state == "proposed"):
        with pytest.raises(UserError, match="Nothing payable"), c.env.cr.savepoint():
            r.with_user(c.acc1).action_submit()


def test_s1_an_account_that_goes_bad_after_the_proposal_is_refused_at_submit(c):  # noqa: F811
    """Only the proposal skips: a line that was payable and stopped being so is a
    refusal at submit, so a bank edit cannot slip past as a quiet skip."""
    approve(c, bill(c, 10000.0))
    r = run(c)
    r.with_user(c.acc1).action_propose()
    line = r.line_ids.filtered(lambda ln: ln.state == "proposed")
    assert line
    line.bank_account_id.sudo().write({"acc_number": "A08-CHANGED-AFTER-PROPOSAL"})
    with pytest.raises(UserError, match="cannot be submitted"), c.env.cr.savepoint():
        r.with_user(c.acc1).action_submit()


def test_s1_an_account_changed_behind_the_orm_loses_its_confirmation(c):  # noqa: F811
    """The fingerprint is the backstop when a change bypasses the write hook (a direct
    database edit, an import): the confirmation is of THESE details, not of the row."""
    assert c.vbank._fix_payable_problem() is False
    c.env.cr.execute(
        "UPDATE res_partner_bank SET acc_number = %s WHERE id = %s",
        ("A08-CHANGED-BEHIND-THE-ORM", c.vbank.id),
    )
    c.vbank.invalidate_recordset()
    assert c.vbank._fix_payable_problem()
