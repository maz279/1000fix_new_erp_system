# cd_tax_engine_bd — A08 finish, M51: a tax user can do the whole job on the
# workspace. Each test pairs what the P03 surface offers (the screen, form field
# or action, read from the real static/src/a08/m51.js and SURFACES) with the real
# path as a NON-ADMIN user holding the real finance role. Arrangement comes from
# the control suite's fixture; legacy rows (no GL entry, no treatment, a forged
# state) are written by SQL and say so. Everything rolls back (odoo_env).
from __future__ import annotations

import json
import logging
import shutil
import subprocess
from decimal import Decimal
from pathlib import Path

import pytest
from odoo.addons.cd_p03_portal.controllers.a08 import m51
from odoo.addons.cd_tax_engine_bd.models import tax_logic
from odoo.addons.cd_tax_engine_bd.tests.test_a08_m51_controls import (
    BIN,
    FILER,
    REG,
    WL,
    StubEvat,
    _bill_posting,
    _challan,
    _deduction,
    _deduction_vals,
    _entry,
    _refused,
    _reg,
    _vat_return,
    c,  # noqa: F401 - the shared fixture
)
from odoo.exceptions import UserError

pytestmark = [pytest.mark.tax, pytest.mark.financial]

A08_JS = Path(m51.__file__).resolve().parents[2] / "static" / "src" / "a08" / "m51.js"
FIX = "fix.mushak.correction"
ZERO_BIN = "0000000000000"


@pytest.fixture(scope="module")
def js(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the workspace registry")
    tmp = tmp_path_factory.mktemp("m51_js")
    (tmp / "m51.mjs").write_text(A08_JS.read_text(encoding="utf-8"), "utf-8")
    probe = tmp / "probe.mjs"
    probe.write_text(
        "import * as F from './m51.mjs';\n"
        "console.log(JSON.stringify({module: F.MODULE, screens: F.SCREENS, chips: F.FORM_CHIPS}));\n",
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our probe file
        [node, str(probe)], capture_output=True, text=True, encoding="utf-8", check=True, timeout=60
    )
    return json.loads(out.stdout)


def _offers(js, screen, method):
    conf = js["screens"][screen]
    assert method in [a["m"] for a in conf.get("actions", [])], "%s has no %s" % (screen, method)
    assert method in m51.SURFACES[conf["model"]]["actions"], "surface refuses %s" % method


def _legacy_row(c, taxable=5000.0, vat=0.0):  # noqa: F811
    """A row as live data has it: the placeholder BIN (refused today, so SQL)
    and no treatment."""
    row = _reg(c, taxable, vat, treatment_summary=False)
    row.flush_recordset()
    c.env.cr.execute(
        "UPDATE fix_mushak_register SET supplier_bin = %s WHERE id = %s", (ZERO_BIN, row.id)
    )
    row.invalidate_recordset()
    return row


def _legacy_deduction(c, state="withheld", **kw):  # noqa: F811
    """A deduction as live data has it: no liability entry (all 16 live rows)."""
    line = c.cenv[WL].sudo().create(_deduction_vals(c, **kw))
    if state != "withheld":
        line.flush_recordset()
        c.env.cr.execute(
            "UPDATE fix_withholding_line SET state = %s WHERE id = %s", (state, line.id)
        )
        line.invalidate_recordset()
    return line


# ------------------------------------------------------------------ the forms
def test_every_m51_form_is_operable(c, js):  # noqa: F811
    dead_ends = []
    for name, form in js["screens"].items():
        if form.get("kind") != "model_form":
            continue
        model = c.env[form["model"]]
        assert form["model"] in m51.SURFACES, name
        names = [f["name"] for s in form["sections"] for f in s["fields"]]
        missing = [n for n in names if n not in model._fields]
        assert not missing, "%s declares unknown fields %s" % (name, missing)
        if len(names) > 15:
            assert form.get("tabs"), "%s has %d fields and no tabs" % (name, len(names))
        defaults = model.default_get(list(model._fields))
        dead = [
            n
            for n, f in model._fields.items()
            if f.required
            and not f.compute
            and not f.related
            and n not in names
            and n not in defaults
        ]
        if dead:
            dead_ends.append((name, dead))
    assert not dead_ends, "required fields not on the form: %s" % dead_ends


def test_every_m51_list_column_and_action_is_real(c, js):  # noqa: F811
    nav = {s["id"] for g in js["module"]["groups"] for s in g["screens"]}
    for name, conf in js["screens"].items():
        if conf.get("kind") != "model_list":
            continue
        model = c.env[conf["model"]]
        bad = [col for col in conf["cols"] if col not in model._fields]
        assert not bad, "%s drops columns %s" % (name, bad)
        for action in conf.get("actions", []):
            assert hasattr(model, action["m"]), "%s: %s" % (name, action["m"])
            assert action["m"] in m51.SURFACES[conf["model"]]["actions"], action["m"]
        assert name in nav, "%s is on no menu" % name


# ---------------------------------------------------- item 12: M51-1 / M51-2
def test_m51_1_unclassified_row_is_found_classified_and_the_period_files(c, js):  # noqa: F811
    """The live dead end: a zero-BIN row with no treatment. It is on a screen,
    an accountant asks, a second person decides, the return then files. No BIN
    is typed and the issued row keeps its amounts and its BIN."""
    form = js["screens"][js["chips"]["M51:__by_screen__"]["M51-corrections"]]
    offered = {f["name"]: f for s in form["sections"] for f in s["fields"]}
    assert not {"supplier_bin", "customer_bin"} & set(offered)
    for name in ("register_id", "correction_type", "treatment", "reason"):
        assert not offered[name].get("readonly"), name
    _offers(js, "M51-corrections", "action_approve")
    _offers(js, "M51-corrections", "action_reject")

    row = _legacy_row(c)
    assert row.vat_line == "unclassified_rate_0"
    domain = js["screens"]["M51-unclassified"]["domain"]
    assert row in c.as_(c.acct)[REG].search(domain)

    # the block as it stands: the return says classify
    _entry(c, [(c.ar, 5000.0, 0.0), (c.revenue, 0.0, 5000.0)])
    ret = _vat_return(c)
    ret.with_user(c.acct).action_prepare()
    assert "unclassified_rate_0" in ret.classification_notes
    _refused(ret.with_user(c.filer).action_file_online, client=StubEvat(), match="Classify")

    req = c.as_(c.acct)[FIX].create(
        {"register_id": row.id, "treatment": "exempt", "reason": "Exempt education service"}
    )
    assert (req.state, req.requested_by_id, req.current_line) == (
        "draft",
        c.acct,
        "unclassified_rate_0",
    )
    _refused(req.with_user(c.acct).action_approve, match="Accounting Administrator")
    req.with_user(c.mgr).action_approve()
    assert (req.state, req.decided_by_id) == ("approved", c.mgr)
    assert row.vat_line == "exempt" and row.supplier_bin == ZERO_BIN
    assert (row.taxable_amount, row.vat_amount) == (5000.0, 0.0)

    # a stale return stays refused until re-prepared, then it files
    _refused(ret.with_user(c.filer).action_file_online, client=StubEvat(), match="Classify")
    ret.with_user(c.acct).action_prepare()
    assert not ret.classification_notes
    for key in ("declarant_name", "declarant_designation", "declarant_nid"):
        c.env["ir.config_parameter"].sudo().set_param("cd_tax_engine_bd.%s" % key, "Test")
    result = ret.with_user(c.filer).action_file_online(client=StubEvat())
    assert ret.state == "filed" and result["token"] == "ACK-STUB-1"

    # the period is closed now: no more classification in it
    other = _legacy_row(c, 100.0, 0.0)
    late = c.as_(c.acct)[FIX].create(
        {"register_id": other.id, "treatment": "exempt", "reason": "Late"}
    )
    _refused(late.with_user(c.mgr).action_approve, match="is filed")


def test_m51_2_requester_cannot_decide_and_amounts_must_fit(c):  # noqa: F811
    row = _legacy_row(c)
    mine = c.as_(c.mgr)[FIX].create({"register_id": row.id, "treatment": "exempt", "reason": "x"})
    _refused(mine.with_user(c.mgr).action_approve, match="Segregation")
    _refused(mine.with_user(c.mgr2).action_reject, match="why")
    mine.with_user(c.mgr2).action_reject(reason="Not exempt")
    assert mine.state == "rejected" and mine.rejection_reason == "Not exempt"
    _refused(mine.with_user(c.acct).write, {"reason": "changed"}, match="decided")

    # zero VAT does not fit the standard rate: the amounts are not rewritten to fit
    wrong = c.as_(c.acct)[FIX].create(
        {"register_id": row.id, "treatment": "standard_15", "reason": "y"}
    )
    _refused(wrong.with_user(c.mgr).action_approve, match="does not fit")
    # an unscheduled reduced rate is refused
    odd = c.as_(c.acct)[FIX].create(
        {"register_id": row.id, "treatment": "reduced", "reduced_rate": 3.0, "reason": "z"}
    )
    _refused(odd.with_user(c.mgr).action_approve, match="scheduled")

    # a row the return can already read is corrected by note, never re-classified
    good = _reg(c, 10000.0, 1500.0)
    again = c.as_(c.acct)[FIX].create(
        {"register_id": good.id, "treatment": "exempt", "reason": "w"}
    )
    _refused(again.with_user(c.mgr).action_approve, match="note")
    # the row itself still refuses every direct write
    _refused(row.with_user(c.mgr).write, {"treatment_summary": "x: exempt @ 0%"})
    _refused(c.as_(c.mgr)[FIX].create, {"register_id": row.id, "reason": "no treatment"})


def test_m51_2_correction_by_note_carries_the_company_bin(c):  # noqa: F811
    row = _legacy_row(c, 20000.0, 3000.0)
    req = c.as_(c.acct)[FIX].create(
        {
            "register_id": row.id,
            "correction_type": "credit_note",
            "treatment": "standard_15",
            "taxable_amount": 2000.0,
            "vat_amount": 300.0,
            "reason": "Price reduction agreed",
        }
    )
    req.with_user(c.mgr).action_approve()
    note = req.note_id
    assert note.row_type == "credit_note" and note.original_id == row
    assert (note.taxable_amount, note.vat_amount) == (-2000.0, -300.0)
    assert note.supplier_bin == BIN and row.supplier_bin == ZERO_BIN
    assert note.vat_line == "standard_15"
    assert (row.taxable_amount, row.vat_amount) == (20000.0, 3000.0)
    # a note against a row with no treatment names the note's own
    bare = _legacy_row(c, 500.0, 0.0)
    no_line = c.as_(c.acct)[FIX].create(
        {
            "register_id": bare.id,
            "correction_type": "debit_note",
            "taxable_amount": 50.0,
            "reason": "Undercharged",
        }
    )
    _refused(no_line.with_user(c.mgr).action_approve, match="treatment")
    # nor can an empty note be asked for
    _refused(
        c.as_(c.acct)[FIX].create,
        {"register_id": row.id, "correction_type": "debit_note", "reason": "empty"},
    )


# --------------------------------------------------- item 13: M51-4 / M51-8
def test_m51_4_duplicates_are_refused_at_the_challan_and_voided_by_a_second_person(
    c,  # noqa: F811
    js,
):
    for method in ("action_request_void", "action_approve_correction", "action_clear_duplicate"):
        _offers(js, "M51-tds-lines", method)
        _offers(js, "M51-vds", method)
    # the live pair: lines 281 and 292, one series saying "Bill ..."
    a = _legacy_deduction(c, source_ref="OPENW-INV-2026-0092")
    b = _legacy_deduction(c, source_ref="Bill OPENW-INV-2026-0092")
    single = _legacy_deduction(c, source_ref="OTHER-BILL-1")
    assert a._fix_duplicates() == b and b._fix_duplicates() == a and not single._fix_duplicates()
    assert "#%s" % b.id in a.duplicate_refs

    ch = c.as_(c.acct)["fix.tax.challan"].create(
        {
            "challan_no": "CH-OPER-1",
            "challan_date": c.today,
            "tax_kind": "tds",
            "period": c.period,
            "amount": a.amount + single.amount,
            "operating_unit_id": c.ou.id,
        }
    )
    _refused(ch.with_user(c.acct).action_link_open_deductions, match="duplicate")
    assert not a.challan_id and not b.challan_id

    _refused(a.with_user(c.acct).action_request_void, match="reason")
    _refused(single.with_user(c.acct).action_request_void, reason="wrong", match="not a duplicate")
    b.with_user(c.acct).action_request_void(reason="Second series of the same bill")
    assert (b.correction_state, b.correction_kind) == (
        "requested",
        "void",
    ) and b.state == "withheld"
    _refused(b.with_user(c.acct).action_approve_correction, match="Accounting Administrator")
    # the requester holding the higher role still cannot apply their own request
    a.with_user(c.mgr).action_request_void(reason="mgr asks")
    _refused(a.with_user(c.mgr).action_approve_correction, match="Segregation")
    a.with_user(c.mgr2).action_reject_correction(reason="This is the right copy")
    assert a.correction_state == "rejected" and a.state == "withheld"

    b.with_user(c.mgr).action_approve_correction()
    assert b.state == "cancelled" and b.correction_decided_by_id == c.mgr
    assert not a._fix_duplicates()

    # the survivor is no longer voidable, and it links and deposits
    _refused(a.with_user(c.acct).action_request_void, reason="both?", match="not a duplicate")
    ch.with_user(c.acct).action_link_open_deductions()
    assert a.challan_id == ch and single.challan_id == ch and not b.challan_id


def test_m51_4_deposit_also_refuses_a_duplicate_linked_by_hand(c):  # noqa: F811
    a = _legacy_deduction(c, source_ref="DUP-HAND")
    _legacy_deduction(c, source_ref="Bill DUP-HAND")
    ch = _challan(c, a, verify_by=c.acct2)
    _refused(ch.with_user(c.acct).action_confirm_deposit, match="duplicate")


def test_m51_8_a_genuine_second_deduction_can_be_cleared(c):  # noqa: F811
    a = _legacy_deduction(c, source_ref="TWO-SECTIONS")
    b = _legacy_deduction(c, source_ref="TWO-SECTIONS")
    _refused(a.with_user(c.acct).action_clear_duplicate, reason="x", match="Accounting Admin")
    _refused(a.with_user(c.mgr).action_clear_duplicate, match="why")
    a.with_user(c.mgr).action_clear_duplicate(reason="Goods and services on one bill")
    assert a.duplicate_cleared_by_id == c.mgr
    assert not a._fix_duplicates() and not b._fix_duplicates()
    assert a.duplicate_cleared_reason.startswith("Goods")


def test_m51_8_a_void_refuses_a_row_with_real_consequences(c):  # noqa: F811
    posted = _deduction(c, source_ref="POSTED-1")
    twin = _legacy_deduction(c, source_ref="Bill POSTED-1")
    _refused(posted.with_user(c.acct).action_request_void, reason="r", match="liability")
    twin.with_user(c.acct).action_request_void(reason="The unposted copy")
    # requested, then a challan arrives: the second person's check is made again
    ch = c.as_(c.acct)["fix.tax.challan"].create(
        {
            "challan_no": "CH-OPER-2",
            "challan_date": c.today,
            "tax_kind": "tds",
            "period": c.period,
            "amount": twin.amount,
            "operating_unit_id": c.ou.id,
        }
    )
    twin.with_user(c.acct).write({"challan_id": ch.id})
    _refused(twin.with_user(c.mgr).action_approve_correction, match="challan")
    assert twin.state == "withheld"


def test_m51_4_phantom_certified_row_reopens_deposits_and_files(c):  # noqa: F811
    """The live dead end: certified with neither challan nor certificate, which
    blocks its TDS quarter. Reopen, deposit, certify, file."""
    from odoo.addons.cd_tax_engine_bd.models import return_logic

    line = _legacy_deduction(c, state="certified", source_ref="PHANTOM-1")
    quarter = return_logic.tds_quarter_for_date(c.today)[0]
    ret = c.as_(c.acct)["fix.tds.return"].create({"quarter": quarter})
    ret.with_user(c.acct).action_prepare()
    _refused(ret.with_user(c.filer).action_file, "ACK-1", match="not yet deposited")
    _refused(line.with_user(c.acct).action_issue_certificate, match="after the challan deposit")

    _refused(_deduction(c).with_user(c.acct).action_request_reopen, reason="r", match="deposited")
    line.with_user(c.acct).action_request_reopen(reason="Marked certified with no challan")
    assert line.state == "certified"
    _refused(line.with_user(c.acct).action_approve_correction, match="Accounting Administrator")
    line.with_user(c.mgr).action_approve_correction()
    assert line.state == "withheld"

    others = c.cenv[WL].search(
        [("company_id", "=", c.co.id), ("state", "=", "withheld"), ("id", "!=", line.id)]
    )
    others.sudo()._guarded().write({"state": "cancelled"})  # arrangement: only this row is open
    _bill_posting(c, line.base_amount, line.amount)  # the money the challan pays out
    ch = _challan(c, line, verify_by=c.acct2)
    ch.with_user(c.acct).action_confirm_deposit()
    assert line.state == "deposited"
    line.with_user(c.acct).action_issue_certificate()
    assert line.state == "certified" and line.certificate_id

    ret.with_user(c.acct).action_prepare()
    ret.with_user(c.filer).action_file("ACK-1")
    assert ret.state == "filed"
    # a real certificate is not undone by this path
    _refused(line.with_user(c.acct).action_request_reopen, reason="r", match="certificate")


# ---------------------------------------------------------- item 14: M51-5
def test_m51_5_no_rate_lives_in_code(c):  # noqa: F811
    for name in ("LEGACY_RATES", "STANDARD_RATE", "REDUCED_RATES"):
        assert not hasattr(tax_logic, name), name
    line = tax_logic.TaxLine("SVC", Decimal("1"), Decimal("1000"))
    with pytest.raises(tax_logic.DeterminationError, match="Tax Rate Master"):
        tax_logic.determine_tax([line])
    det = c.cenv["fix.vat.treatment"]._fix_determine_tax([line], c.today, c.co)
    rate = c.env["fix.tax.rate"].find_rate("vat", "standard", c.today, c.co).rate
    assert det.rates_source == "master"
    assert det.total_vat == Decimal(str(rate)) * 10


# ---------------------------------------------------------- item 15: M51-6
def test_m51_6_flagged_row_keeps_working_warns_and_shows(c, js, caplog):  # noqa: F811
    """Refusing flagged rows would stop every bill today, so a flagged row is used,
    warns, is flagged on the deduction and report, and sits in the queue."""
    row = c.rate
    assert row.verify_with_adviser and row.signoff_state == "adviser"
    with caplog.at_level(logging.WARNING):
        found = c.env["fix.tax.rate"].find_rate("tds", "service_general", c.today, c.co)
    assert found == row
    assert any("used before its sign-off" in r.getMessage() for r in caplog.records)

    line = _deduction(c)
    assert line.rate_flagged
    screen = js["screens"]["M51-tds-lines"]
    assert "rate_flagged" in screen["cols"] and "rate_flagged" in js["screens"]["M51-vds"]["cols"]
    for name in ("M51-rates", "M51-params", "M51-duerules", "M51-determination"):
        assert "signoff_state" in js["screens"][name]["cols"], name
        _offers(js, name, "action_cfo_signoff")
        _offers(js, name, "action_record_adviser_verification")

    env = c.as_(c.acct)
    assert js["screens"]["M51-signoff"]["report"] == "signoff_queue"
    queue = m51.REPORTS["signoff_queue"](env)
    assert row.display_name in [r["row"] for r in queue["rows"]]
    assert m51.kpis(env)["signoff_pending"] >= 1
    summary = m51.REPORTS["tds_annual_summary"](env)
    assert any("not yet signed off" in n for n in summary["notes"])

    vds_rate = c.env["fix.tax.rate"].search(
        [("tax_kind", "=", "vds"), ("state", "=", "active")], limit=1
    )
    if vds_rate.signoff_state != "signed":
        _legacy_deduction(
            c,
            tax_kind="vds",
            rate_id=vds_rate.id,
            amount=round(100000.0 * vds_rate.rate / 100.0, 2),
            source_ref="VDS-1",
        )
        vds = m51.REPORTS["vds_deduction_register"](env)
        assert "basis" in vds["cols"]
        assert {r["basis"] for r in vds["rows"]} == {"Rate unconfirmed"}

    # the register row too: a reduced row at a flagged rate, not the signed standard one
    assert not _reg(c, 1000.0, 150.0).rate_flagged
    reduced = _reg(c, 1000.0, 50.0, treatment_summary="SVC: reduced @ 5%")
    assert reduced.vat_line == "reduced_5" and reduced.rate_flagged
    assert "rate_flagged" in js["screens"]["M51-mushak63"]["cols"]


def test_m51_6_two_steps_adviser_then_cfo_on_a_row_in_force(c):  # noqa: F811
    row = c.rate
    _refused(row.with_user(c.filer).action_cfo_signoff, match="adviser")
    _refused(row.with_user(c.acct).action_record_adviser_verification, "ADV", match="Administrator")
    row.with_user(c.mgr).action_record_adviser_verification("ADV-2026-7")
    assert row.signoff_state == "cfo" and row.state == "active"
    _refused(row.with_user(c.mgr).action_cfo_signoff, match="Filing Approver")
    row.with_user(c.filer).action_cfo_signoff()
    assert row.signoff_state == "signed" and row.cfo_signed_by_id == c.filer
    assert row.rate == c.env["fix.tax.rate"].browse(row.id).rate
    _refused(row.with_user(c.filer).action_cfo_signoff, match="already")
    line = _deduction(c)
    assert not line.rate_flagged
    env = c.as_(c.acct)
    assert row.display_name not in [r["row"] for r in m51.REPORTS["signoff_queue"](env)["rows"]]


def test_m51_6_recorder_cannot_also_be_the_cfo(c):  # noqa: F811
    c.mgr.sudo().write({"group_ids": [(4, c.env.ref(FILER).id)]})
    c.rate.with_user(c.mgr).action_record_adviser_verification("ADV-9")
    _refused(c.rate.with_user(c.mgr).action_cfo_signoff, match="Segregation")


def test_m51_6_proposal_is_activated_by_the_cfo_only(c):  # noqa: F811
    new = c.as_(c.mgr)["fix.tax.rate"].create(
        {
            "tax_kind": "tds",
            "code": "a08_oper",
            "name": "Proposed",
            "rate": 3.0,
            "company_id": c.co.id,
            "date_from": c.today,
        }
    )
    assert new.signoff_state == "adviser" and new.state == "proposed"
    new.with_user(c.mgr).action_record_adviser_verification("ADV-10")
    _refused(new.with_user(c.mgr2).action_activate, match="Filing Approver")
    new.with_user(c.filer).action_activate()
    assert (new.state, new.signoff_state, new.cfo_signed_by_id) == ("active", "signed", c.filer)


def test_m51_6_enforcement_switch_refuses_an_unsigned_row(c):  # noqa: F811
    icp = c.env["ir.config_parameter"].sudo()
    icp.set_param("cd_tax_engine_bd.enforce_rate_signoff", "1")
    _refused(
        c.env["fix.tax.rate"].find_rate, "tds", "service_general", c.today, c.co, match="signed off"
    )
    _refused(c.env["fix.tax.parameter"].get_value, "non_filer_multiplier", c.today, c.co)
    icp.set_param("cd_tax_engine_bd.enforce_rate_signoff", "0")
    assert c.env["fix.tax.rate"].find_rate("tds", "service_general", c.today, c.co) == c.rate


# ---------------------------------------------------------- item 16: M51-7
def test_m51_7_statutory_uplift_has_a_button_and_works(c, js):  # noqa: F811
    _offers(js, "M51-tds-lines", "action_apply_statutory_uplift")
    line = _legacy_deduction(c)
    # arrangement: a legacy under-withheld row (the constraint refuses it today)
    line.flush_recordset()
    c.env.cr.execute(
        "UPDATE fix_withholding_line SET psr_received = FALSE, multiplier = 1.0, defaults_count = 1 "
        "WHERE id = %s",
        (line.id,),
    )
    line.invalidate_recordset()
    before = line.amount
    _refused(line.with_user(c.plain).action_apply_statutory_uplift, match="Accountant")
    line.with_user(c.acct).action_apply_statutory_uplift()
    assert line.multiplier == 1.5 and line.amount == pytest.approx(before * 1.5)


# ---------------------------------------------------------- item 17: crons
def test_m51_crons_exist_and_are_active(c):  # noqa: F811
    deadlines = c.env.ref("cd_tax_engine_bd.ir_cron_statutory_deadline_reminders")
    window = c.env.ref("cd_tax_engine_bd.ir_cron_certificate_window_reminders")
    assert deadlines.active and deadlines.code == "model._cron_deadline_reminders()"
    assert window.active and window.code == "model._cron_certificate_window()"
    assert deadlines.model_id.model == "fix.statutory.due.rule"
    assert window.model_id.model == WL


def test_m51_deadline_reminder_reaches_the_roles_once_and_posts_nothing(c):  # noqa: F811
    Rule = c.env["fix.statutory.due.rule"]
    moves = c.env["account.move"].search_count([])
    created = Rule._cron_deadline_reminders()
    assert created > 0
    Activity = c.env["mail.activity"].sudo()
    overdue = Activity.search(
        [
            ("res_model", "=", Rule._name),
            ("summary", "=like", "OVERDUE: %"),
            ("user_id", "=", c.mgr.id),
        ]
    )
    assert overdue, "an Accounting Administrator is told what is overdue"
    assert Activity.search_count(
        [
            ("res_model", "=", Rule._name),
            ("summary", "=like", "OVERDUE: %"),
            ("user_id", "=", c.filer.id),
        ]
    ), "past the deadline the CFO is told too"
    assert not Activity.search_count([("res_model", "=", Rule._name), ("user_id", "=", c.acct.id)])
    assert Rule._cron_deadline_reminders() == 0, "one to-do per person, obligation and period"
    assert c.env["account.move"].search_count([]) == moves
    # a done obligation stops reminding: file the period's evidence-tracked return
    rows = Rule.calendar(c.today.replace(day=1), c.today.replace(day=28), c.co)
    assert all(r["status"] in ("done", "nothing_due", "due", "overdue") for r in rows)


def test_m51_certificate_window_reminder(c):  # noqa: F811
    line = _deduction(c)
    ch = _challan(c, line, verify_by=c.acct2)
    ch.with_user(c.acct).action_confirm_deposit()
    Line = c.env[WL]
    icp = c.env["ir.config_parameter"].sudo()
    icp.set_param("cd_tax_engine_bd.certificate_window_days", "30")
    assert not line.sudo().activity_ids
    Line._cron_certificate_window()
    assert not line.sudo().activity_ids, "inside the window nobody is chased"
    icp.set_param("cd_tax_engine_bd.certificate_window_days", "0")
    moves = c.env["account.move"].search_count([])
    assert Line._cron_certificate_window() >= 1
    assert line.sudo().activity_ids.filtered(lambda a: a.user_id == c.mgr)
    assert c.env["account.move"].search_count([]) == moves
    assert not line.certificate_id and line.state == "deposited"
    assert Line._cron_certificate_window() == 0
    line.with_user(c.acct).action_issue_certificate()
    assert Line.search_count([("id", "=", line.id), ("state", "=", "deposited")]) == 0


def test_m51_tds_prepare_explains_a_bad_quarter_label(c):  # noqa: F811
    ret = c.as_(c.acct)["fix.tds.return"].create({"quarter": "2026-Q2"})
    c.env.cr.execute("UPDATE fix_tds_return SET quarter = 'Q2-2026' WHERE id = %s", (ret.id,))
    ret.invalidate_recordset()
    with pytest.raises(UserError, match="quarter label"), c.env.cr.savepoint():
        ret.with_user(c.acct).action_prepare()
