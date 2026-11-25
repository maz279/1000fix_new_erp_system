# A08 finish, M20: a person can do the whole job on screen. Every test walks the
# real path as a NON-ADMIN user holding the real finance role, through the P03
# endpoints the workspace calls (/p03/model/*, /p03/ar/*), against the screens
# evaluated from the registry (static/src/a08/m20.js), never its text.
import json
import re
import shutil
import subprocess
import types
from datetime import date, timedelta
from pathlib import Path

import pytest
from odoo.addons.cd_billing_engine.tests.test_a08_m20_controls import (
    as_,
    c,  # noqa: F401 - fixture
    c_raw,  # noqa: F401 - fixture
    cn,
    inv,
)
from odoo.exceptions import AccessError, UserError

pytestmark = [pytest.mark.financial]

PORTAL = Path(__file__).resolve().parents[4] / "platform" / "cd_p03_portal"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')


@pytest.fixture(scope="module")
def screens(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    src = PORTAL / "static" / "src"
    tmp = tmp_path_factory.mktemp("p03_m20_op")
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
        ".filter(([k]) => k.startsWith('M20'))), chips: M.P03_FORM_CHIPS,"
        " nav: M.P03_MODULES.M20.groups.flatMap((g) => g.screens.map((s) => s.id))}));\n",
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=60
    )
    return json.loads(out.stdout)


@pytest.fixture
def p03(c):  # noqa: F811
    from odoo.addons.cd_p03_portal.controllers import p03_ar_api as ar
    from odoo.addons.cd_p03_portal.controllers import p03_generic_api as g

    holder = types.SimpleNamespace(env=None)
    old = (g.request, ar.request)
    g.request = ar.request = holder
    generic, arctl = g.P03GenericApiController(), ar.P03ArApiController()

    def bind(fn, ctl, name):
        f = getattr(type(ctl), name)
        f = getattr(f, "original_endpoint", f)
        return lambda **kw: f(ctl, **kw)

    try:
        yield types.SimpleNamespace(
            as_user=lambda user: setattr(holder, "env", as_(c, user)),
            action=bind(None, generic, "model_action"),
            form=bind(None, generic, "model_form"),
            records=bind(None, generic, "model_records"),
            resolve=bind(None, arctl, "ar_dispute_resolve"),
            suppress=bind(None, arctl, "ar_dunning_suppress"),
            lift=bind(None, arctl, "ar_dunning_lift"),
            writeoff=bind(None, arctl, "ar_invoice_writeoff"),
        )
    finally:
        g.request, ar.request = old


def form_fields_of(screens, sid):
    return [f for s in screens["screens"][sid]["sections"] for f in s["fields"]]


def assert_operable(p03, screens, list_id, form_id, user, editable, actions):
    """The list is on the menu and calls real surface actions; its + New opens the
    form; the server offers each field as an input, for this user."""
    cfg = screens["screens"][list_id]
    assert list_id in screens["nav"]
    if form_id:
        assert screens["chips"]["M20:__by_screen__"][list_id] == form_id
    assert set(actions) <= {a["m"] for a in cfg.get("actions", [])}
    from odoo.addons.cd_p03_portal.controllers.a08 import m20

    assert set(actions) <= m20.SURFACES[cfg["model"]]["actions"]
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


def approved_rates(c, maker=None, checker=None, **over):  # noqa: F811
    vals = {
        "name": "ECL %s" % c.tag,
        "company_id": c.company.id,
        "date_from": date(2020, 1, 1),
        "rate_current": 0.5,
        "rate_1_30": 2.0,
        "rate_31_60": 10.0,
        "rate_61_90": 25.0,
        "rate_90_plus": 50.0,
        "basis_note": "24 months of write-offs, finance policy note",
    }
    vals.update(over)
    rates = as_(c, maker or c.mgr)["fix.ar.ecl.rate"].create(vals)
    rates.with_user(checker or c.mgr2).action_approve()
    return rates


def ecl_run(c):  # noqa: F811
    return as_(c, c.acct)["fix.ar.impairment"].create(
        {
            "company_id": c.company.id,
            "journal_id": c.journal.id,
            "expense_account_id": c.acc["ecl_expense"].id,
            "provision_account_id": c.acc["ecl_provision"].id,
        }
    )


# ---------------------------------------------------------------- M20-10
def test_m20_10_resolve_button_reaches_the_model_with_a_code(c, p03):  # noqa: F811
    i = inv(c, c.acct, 8000.0)
    d = as_(c, c.acct)["fix.ar.dispute"].create(
        {"invoice_id": i.id, "amount_disputed": 100.0, "reason": "wrong part"}
    )
    p03.as_user(c.acct2)
    res = p03.resolve(dispute_id=d.id, note="customer agreed the charge")
    assert res["success"] is False and "upheld_credit" in res["error"]
    assert d.state == "open"
    res = p03.resolve(dispute_id=d.id, note="rejected | customer agreed the charge")
    assert res == {"success": True, "state": "resolved", "outcome_code": "rejected"}
    assert d.resolution_note == "customer agreed the charge"


def test_m20_10_dispute_screen_has_one_button_per_outcome(c, p03, screens):  # noqa: F811
    assert_operable(
        p03,
        screens,
        "M20-ar-dispute",
        None,
        c.acct2,
        (),
        ["action_resolve_rejected", "action_resolve_upheld_credit"],
    )
    i = inv(c, c.acct, 8000.0)
    d = as_(c, c.acct)["fix.ar.dispute"].create(
        {"invoice_id": i.id, "amount_disputed": 100.0, "reason": "wrong part"}
    )
    p03.as_user(c.acct)
    res = p03.action(
        model="fix.ar.dispute", ids=[d.id], method="action_resolve_rejected", kwargs={"note": "no"}
    )
    assert res["success"] is False and "another person" in res["error"]  # the raiser
    p03.as_user(c.acct2)
    res = p03.action(
        model="fix.ar.dispute", ids=[d.id], method="action_resolve_rejected", kwargs={"note": "no"}
    )
    assert res["success"] is True and d.outcome_code == "rejected" and d.resolved_by == c.acct2


# ---------------------------------------------------------------- M20-6 / S3
def test_m20_6_writeoff_screen_requests_and_approves_in_the_direct_band(c, p03, screens):  # noqa: F811
    assert_operable(
        p03,
        screens,
        "M20-writeoffs",
        "M20-form-writeoff",
        c.acct,
        ["invoice_id", "reason", "recovery_history"],
        ["action_submit", "action_approve", "action_reject"],
    )
    i = inv(c, c.acct, 5000.0)
    wo = as_(c, c.acct)["fix.ar.writeoff"].create(
        {"invoice_id": i.id, "reason": "bankrupt", "recovery_history": "3 calls, 1 legal notice"}
    )
    p03.as_user(c.acct)
    assert p03.action(model="fix.ar.writeoff", ids=[wo.id], method="action_submit")["success"]
    assert wo.state == "requested"
    res = p03.action(model="fix.ar.writeoff", ids=[wo.id], method="action_approve")
    assert res["success"] is False  # the requester never approves
    p03.as_user(c.acct2)
    assert p03.action(model="fix.ar.writeoff", ids=[wo.id], method="action_approve")["success"]
    assert wo.state == "posted" and i.state == "written_off" and wo.fin_approved_by_id == c.acct2


def test_m20_6_writeoff_rejected_with_a_reason_from_the_screen(c, p03):  # noqa: F811
    i = inv(c, c.acct, 5000.0)
    wo = i.with_user(c.acct).action_write_off("bankrupt", recovery_history="3 calls")
    p03.as_user(c.acct2)
    res = p03.action(
        model="fix.ar.writeoff",
        ids=[wo.id],
        method="action_reject",
        kwargs={"reason": "customer is paying"},
    )
    assert res["success"] and wo.state == "rejected" and i.state == "issued"


def test_m20_6_invoice_prompt_carries_the_recovery_history(c, p03):  # noqa: F811
    i = inv(c, c.acct, 5000.0)
    p03.as_user(c.acct)
    res = p03.writeoff(invoice_id=i.id, reason="bankrupt")
    assert res["success"] is False and "recovery history" in res["error"]
    assert not i.writeoff_ids
    res = p03.writeoff(invoice_id=i.id, reason="bankrupt | three calls, legal notice")
    assert res["success"] and res["request_state"] == "requested"
    assert i.writeoff_ids.recovery_history == "three calls, legal notice"
    assert i.writeoff_ids.reason == "bankrupt"


# ---------------------------------------------------------------- M20-1
def test_m20_1_reject_is_on_the_screen_and_a_second_person_only(c, p03, screens):  # noqa: F811
    assert_operable(
        p03, screens, "M20-notes-register", "M20-form-note", c.acct2, (), ["action_reject"]
    )
    i = inv(c, c.acct, 5000.0)
    n = cn(c, c.acct, i, 100.0)
    n.action_submit()
    p03.as_user(c.acct)
    res = p03.action(
        model="fix.credit.note", ids=[n.id], method="action_reject", kwargs={"reason": "x"}
    )
    assert res["success"] is False and n.state == "pending_approval"
    p03.as_user(c.acct2)
    res = p03.action(
        model="fix.credit.note", ids=[n.id], method="action_reject", kwargs={"reason": "wrong"}
    )
    assert res["success"] and n.state == "rejected" and n.rejected_reason == "wrong"


def _returned_note(c):  # noqa: F811
    i = inv(c, c.acct, 100000.0)
    n = cn(c, c.acct, i, 50000.0)
    n.action_submit()
    assert n.approval_state == "pending"
    task = c.env["fix.workflow.task"].search(
        [
            ("res_model", "=", n._name),
            ("res_id", "=", n.id),
            ("state", "=", "pending"),
            ("assigned_user_id", "=", c.mgr.id),
        ],
        limit=1,
    )
    task.with_user(c.mgr).action_return(comment="which job was it?")
    n.invalidate_recordset()
    assert n.state == "pending_approval" and n.approval_state == "returned"
    return n


def test_m20_1_returned_note_is_re_requested(c, p03):  # noqa: F811
    n = _returned_note(c)
    p03.as_user(c.acct)
    res = p03.action(model="fix.credit.note", ids=[n.id], method="action_rerequest", kwargs={})
    assert res["success"] is False  # says nothing to the approver
    res = p03.action(
        model="fix.credit.note",
        ids=[n.id],
        method="action_rerequest",
        kwargs={"justification": "job JB-12, photo attached"},
    )
    assert res["success"] and n.approval_state == "pending"
    assert c.mgr in n.approval_request_id.sudo().task_ids.mapped("assigned_user_id")
    assert n.state == "pending_approval"


def test_m20_1_returned_note_can_be_withdrawn_corrected_and_resubmitted(c, p03):  # noqa: F811
    n = _returned_note(c)
    p03.as_user(c.acct)
    res = p03.action(
        model="fix.credit.note",
        ids=[n.id],
        method="action_withdraw_to_draft",
        kwargs={"reason": "the amount was wrong"},
    )
    assert res["success"] and n.state == "draft" and n.approval_state != "returned"
    n.with_user(c.acct).write({"amount": 5000.0})
    n.with_user(c.acct).action_submit()
    assert n.state == "pending_approval"


def test_m20_1_a_note_not_returned_is_not_re_requested(c):  # noqa: F811
    n = cn(c, c.acct, inv(c, c.acct, 5000.0), 100.0)
    n.action_submit()
    with pytest.raises(UserError, match="not returned"):
        n.action_rerequest("anything")


def _pay(c, i, amount):  # noqa: F811
    r = as_(c, c.acct)["fix.ar.receipt"].create(
        {
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
            "customer_id": i.customer_id.id,
            "amount": amount,
            "method": "bank_transfer",
        }
    )
    r.action_confirm()
    as_(c, c.acct)["fix.ar.allocation"].create(
        {"receipt_id": r.id, "invoice_id": i.id, "amount": amount}
    )


def test_m20_1_credit_on_paid_money_raises_a_treasury_refund(c):  # noqa: F811
    if "fix.payment.execution" not in c.env:
        pytest.skip("treasury is not installed in this database")
    i = inv(c, c.acct, 10000.0)  # 11,500 with VAT
    _pay(c, i, 6500.0)
    n = cn(c, c.acct, i, 7000.0)  # 5,000 is unpaid; 2,000 was received
    n.action_submit()
    n.with_user(c.acct2).action_approve()
    n.with_user(c.acct2).action_issue()
    assert n.refund_amount == 2000.0 and n.refund_ref
    pay = c.env["fix.payment.execution"].search(
        [("source_model", "=", "fix.credit.note"), ("source_id", "=", n.id)]
    )
    assert pay.state == "pending" and pay.amount == 2000.0 and pay.name == n.refund_ref
    assert pay.partner_id == i.customer_id.commercial_partner_id
    assert pay.debit_account_id == c.acc["ar"]  # Dr receivable / Cr bank when treasury pays


def test_m20_1_credit_within_the_unpaid_amount_raises_no_refund(c):  # noqa: F811
    i = inv(c, c.acct, 10000.0)
    _pay(c, i, 6500.0)
    n = cn(c, c.acct, i, 5000.0)
    n.action_submit()
    n.with_user(c.acct2).action_approve()
    n.with_user(c.acct2).action_issue()
    assert n.refund_amount == 0.0 and not n.refund_ref
    assert i.amount_residual == 0.0


def test_m20_1_cap_counts_every_other_credit_and_vds(c):  # noqa: F811
    i = inv(c, c.acct, 10000.0)  # 11,500
    first = cn(c, c.acct, i, 9000.0)
    first.action_submit()
    second = cn(c, c.acct, i, 3000.0)
    with pytest.raises(UserError, match="never exceed"):
        second.action_submit()
    second.write({"amount": 2500.0})
    second.action_submit()
    assert second.state == "pending_approval"


# ---------------------------------------------------------------- M20-11
def _dunning(c):  # noqa: F811
    i = inv(c, c.acct, 8000.0, when=date.today() - timedelta(days=90))
    row = (
        c.env["fix.dunning"]
        .sudo()
        ._guarded()
        .create(
            {
                "company_id": c.company.id,
                "operating_unit_id": c.ou.id,
                "invoice_id": i.id,
                "overdue_amount": 9200.0,
                "step": "reminder",
                "step_date": date.today(),
            }
        )
    )
    return row.with_env(as_(c, c.acct))


def test_m20_11_suppress_prompt_takes_code_until_and_note(c, p03):  # noqa: F811
    row = _dunning(c)
    until = date.today() + timedelta(days=10)
    p03.as_user(c.acct)
    res = p03.suppress(dunning_id=row.id, reason="because I said so")
    assert res["success"] is False and "payment_plan" in res["error"] and not row.suppressed
    res = p03.suppress(dunning_id=row.id, reason="Payment plan | %s | three instalments" % until)
    assert res["success"] and res["until"] == str(until)
    assert row.suppressed and row.suppression_reason == "payment_plan"
    assert row.suppressed_until == until and row.suppression_note == "three instalments"
    assert row.suppressed_by_id == c.acct


def test_m20_11_suppress_prompt_refuses_a_bad_date_and_a_past_one(c, p03):  # noqa: F811
    row = _dunning(c)
    p03.as_user(c.acct)
    res = p03.suppress(dunning_id=row.id, reason="strategic | next week")
    assert res["success"] is False and not row.suppressed
    res = p03.suppress(dunning_id=row.id, reason="strategic | 2001-01-01")
    assert res["success"] is False and not row.suppressed


def test_m20_11_lift_from_the_route_and_the_screen(c, p03, screens):  # noqa: F811
    assert_operable(
        p03,
        screens,
        "M20-dunning-register",
        None,
        c.acct,
        (),
        [
            "action_suppress_payment_plan",
            "action_suppress_strategic",
            "action_suppress_dispute",
            "action_lift_suppression",
        ],
    )
    row = _dunning(c)
    p03.as_user(c.acct)
    res = p03.action(
        model="fix.dunning",
        ids=[row.id],
        method="action_suppress_strategic",
        kwargs={"until": "", "note": "key account"},
    )
    assert res["success"] and row.suppression_reason == "strategic" and row.suppressed_until
    res = p03.lift(dunning_id=row.id, note="the plan was broken")
    assert res == {"success": True, "suppressed": False}
    assert not row.suppressed and row.suppression_note == "the plan was broken"


def test_m20_11_plain_user_cannot_suppress(c, p03):  # noqa: F811
    row = _dunning(c)
    p03.as_user(c.plain)
    res = p03.suppress(dunning_id=row.id, reason="strategic")
    assert res["success"] is False


# ---------------------------------------------------------------- M20-5
def test_m20_5_rate_master_screen_and_maker_checker(c, p03, screens):  # noqa: F811
    assert_operable(
        p03,
        screens,
        "M20-ecl-rates",
        "M20-form-ecl-rate",
        c.mgr,
        ["name", "date_from", "rate_current", "rate_90_plus", "basis_note"],
        ["action_approve", "action_retire"],
    )
    rates = as_(c, c.mgr)["fix.ar.ecl.rate"].create(
        {
            "name": "Policy 2026",
            "company_id": c.company.id,
            "date_from": date(2026, 1, 1),
            "rate_current": 1.0,
            "rate_1_30": 2.0,
            "rate_31_60": 3.0,
            "rate_61_90": 4.0,
            "rate_90_plus": 5.0,
            "basis_note": "board paper 12",
        }
    )
    p03.as_user(c.mgr)
    res = p03.action(model="fix.ar.ecl.rate", ids=[rates.id], method="action_approve")
    assert res["success"] is False and "another" in res["error"]
    p03.as_user(c.acct)
    res = p03.action(model="fix.ar.ecl.rate", ids=[rates.id], method="action_approve")
    assert res["success"] is False  # needs the Accounting Administrator
    p03.as_user(c.mgr2)
    assert p03.action(model="fix.ar.ecl.rate", ids=[rates.id], method="action_approve")["success"]
    assert rates.state == "approved" and rates.approved_by_id == c.mgr2
    with pytest.raises(UserError, match="fixed"):
        rates.with_user(c.mgr).write({"rate_90_plus": 0.01})


def test_m20_5_no_approved_rates_means_no_run(c):  # noqa: F811
    inv(c, c.acct, 10000.0, when=date.today() - timedelta(days=200))
    run = ecl_run(c)
    with pytest.raises(UserError, match="No approved ECL"):
        run.action_compute()
    draft = as_(c, c.mgr)["fix.ar.ecl.rate"].create(
        {
            "name": "Unapproved",
            "company_id": c.company.id,
            "date_from": date(2020, 1, 1),
            "rate_current": 99.0,
            "rate_1_30": 99.0,
            "rate_31_60": 99.0,
            "rate_61_90": 99.0,
            "rate_90_plus": 99.0,
            "basis_note": "x",
        }
    )
    with pytest.raises(UserError, match="No approved ECL"):
        run.action_compute()
    assert draft.state == "draft" and run.state == "draft"


def test_m20_5_run_takes_the_master_rates_and_cannot_type_its_own(c):  # noqa: F811
    inv(c, c.acct, 10000.0, when=date.today() - timedelta(days=200))
    rates = approved_rates(c, rate_90_plus=40.0)
    with pytest.raises(UserError):
        as_(c, c.acct)["fix.ar.impairment"].create(
            {"company_id": c.company.id, "journal_id": c.journal.id, "rate_90_plus": 0.01}
        )
    run = ecl_run(c)
    with pytest.raises(UserError):
        run.write({"rate_90_plus": 0.01})
    run.action_compute()
    assert run.rate_set_id == rates and run.rate_90_plus == 40.0
    assert run.total_provision == 4600.0  # 11,500 x 40%


def test_m20_5_a_retired_set_is_not_used_and_overlap_is_refused(c):  # noqa: F811
    rates = approved_rates(c)
    clash = as_(c, c.mgr)["fix.ar.ecl.rate"].create(
        {
            "name": "Overlap",
            "company_id": c.company.id,
            "date_from": date(2025, 1, 1),
            "rate_current": 1.0,
            "rate_1_30": 1.0,
            "rate_31_60": 1.0,
            "rate_61_90": 1.0,
            "rate_90_plus": 1.0,
            "basis_note": "x",
        }
    )
    with pytest.raises(UserError, match="overlaps"):
        clash.with_user(c.mgr2).action_approve()
    rates.with_user(c.mgr2).action_retire(reason="superseded")
    assert rates.state == "retired"
    with pytest.raises(UserError, match="No approved ECL"):
        ecl_run(c).action_compute()
    clash.with_user(c.mgr2).action_approve()
    assert clash.state == "approved"


# ---------------------------------------------------------------- M20-4
def test_m20_4_recon_ties_when_the_books_agree_and_lists_a_difference(c, p03, screens):  # noqa: F811
    from odoo.addons.cd_p03_portal.controllers.a08 import m20

    assert screens["screens"]["M20-gl-recon"]["report"] == "ar_subledger_gl_recon"
    assert "M20-gl-recon" in screens["nav"]
    i = inv(c, c.acct, 10000.0)  # GL Dr AR 11,500
    env = as_(c, c.acct)
    out = m20.REPORTS["ar_subledger_gl_recon"](env)
    row = next(r for r in out["rows"] if r["customer"] == i.customer_id.name)
    assert (row["subledger"], row["gl"], row["difference"]) == (11500.0, 11500.0, 0.0)
    # the sub-ledger moves with no GL entry behind it: the report shows it
    c.env.cr.execute(
        "UPDATE account_move_line SET debit = debit - 500, balance = balance - 500, "
        "amount_currency = amount_currency - 500 WHERE move_id = %s AND account_id = %s",
        (i.posted_move_id.id, c.acc["ar"].id),
    )
    c.env.invalidate_all()
    out = m20.REPORTS["ar_subledger_gl_recon"](as_(c, c.acct))
    row = next(r for r in out["rows"] if r["customer"] == i.customer_id.name)
    assert (row["gl"], row["difference"]) == (11000.0, 500.0)
    assert "1 customer(s) differ" in out["title"]


def test_m20_4_recon_is_finance_only(c):  # noqa: F811
    from odoo.addons.cd_p03_portal.controllers.a08 import m20

    out = m20.REPORTS["ar_subledger_gl_recon"](as_(c, c.plain))
    assert not out["rows"] and "finance" in out["notes"][0]


# ---------------------------------------------------------------- BRU-ARB-22
def test_m20_s5_cron_record_exists(c):  # noqa: F811
    cron = c.env.ref("cd_billing_engine.ir_cron_ar_unapplied_escalation")
    assert cron.active and "_cron_escalate_unapplied" in cron.code


def test_m20_s5_unapplied_receipt_is_escalated_once_and_moves_no_money(c, p03, screens):  # noqa: F811
    assert_operable(p03, screens, "M20-unapplied", None, c.acct, (), [])
    old = as_(c, c.acct)["fix.ar.receipt"].create(
        {
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
            "customer_id": c.customer.id,
            "amount": 700.0,
            "method": "bank_transfer",
            "receipt_date": date.today() - timedelta(days=8),
        }
    )
    old.action_confirm()
    fresh = as_(c, c.acct)["fix.ar.receipt"].create(
        {
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
            "customer_id": c.customer.id,
            "amount": 500.0,
            "method": "bank_transfer",
            "receipt_date": date.today() - timedelta(days=2),
        }
    )
    fresh.action_confirm()
    move, moves = old.posted_move_id, c.env["account.move"].search_count([])
    Model = c.env["fix.ar.receipt"].sudo()
    assert Model._cron_escalate_unapplied() >= 1
    assert old.unapplied_escalated_at and not fresh.unapplied_escalated_at
    assert old.activity_ids and old.posted_move_id == move and old.unapplied_amount == 700.0
    assert c.env["account.move"].search_count([]) == moves
    stamp = old.unapplied_escalated_at
    count = len(old.activity_ids)
    Model._cron_escalate_unapplied()
    assert old.unapplied_escalated_at == stamp and len(old.activity_ids) == count
    with pytest.raises(UserError):
        old.with_user(c.acct).write({"unapplied_escalated_at": False})


# ---------------------------------------------------------------- tabs
def test_m20_vds_form_is_split_into_tabs(screens):
    form = screens["screens"]["M20-form-vds"]
    declared = {t["id"] for t in form["tabs"]}
    assert len(declared) >= 2
    assert sum(len(s["fields"]) for s in form["sections"]) > 15
    assert {s["tab"] for s in form["sections"]} == declared


def test_m20_every_new_form_field_is_real(c, p03, screens):  # noqa: F811
    for sid in (
        "M20-form-vds",
        "M20-form-ecl",
        "M20-form-note",
        "M20-form-writeoff",
        "M20-form-ecl-rate",
    ):
        cfg = screens["screens"][sid]
        p03.as_user(c.mgr)
        res = p03.form(model=cfg["model"], fields=form_fields_of(screens, sid))
        assert "error" not in res, (sid, res)
        assert {f["name"] for f in form_fields_of(screens, sid)} == {
            f["name"] for f in res["fields"]
        }


def test_m20_access_plain_user_has_no_rate_master(c):  # noqa: F811
    with pytest.raises(AccessError):
        as_(c, c.plain)["fix.ar.ecl.rate"].search([])


def test_m20_no_form_offers_a_guarded_field_as_an_input(c, screens):  # noqa: F811
    """What form_fields.py --a08 will generate the write whitelist from."""
    for sid, cfg in screens["screens"].items():
        if cfg.get("kind") != "model_form":
            continue
        model = c.env[cfg["model"]]
        guarded = model._fix_guarded_fields() if hasattr(model, "_fix_guarded_fields") else set()
        inputs = {f["name"] for f in form_fields_of(screens, sid) if not f.get("readonly")}
        assert not inputs & set(guarded), (sid, sorted(inputs & set(guarded)))
