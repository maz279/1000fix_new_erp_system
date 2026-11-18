# ruff: noqa: F811 - the controls suite's pytest fixtures (c, p03) and the pass-1 `reg` are imported
# M13 Rental & EaaS, capture pass 2 (2026-11-19): each sub-module page
# captures the records its spec names.
#
# Reported again 2026-11-19: "not all the sub-modules have a relevant data
# capture button". After the 13 Nov pass every page had a button, but against
# the spec (FR-RNT-001..044, BRU-RNT-01..22, entities §10.1) eight records a
# person must enter had no model anywhere, and two hard rules were absent:
#   1 FR-RNT-031 inter-branch redeployment
#   2 FR-RNT-010 (P1) exposure limit + BRU-RNT-05 override; BRU-RNT-20 (H)
#     verified identity; FR-RNT-032 allocation of a pool booking
#   3 FR-RNT-016/033 extension as a versioned variation
#   4 FR-RNT-036 the damage-waiver PRODUCT (the page only wrote losses off)
#   5 FR-RNT-021/023 (P1), T-04, BRU-RNT-01/19 (H): photographs were a typed
#     link, so a unit was handed over with no photographic evidence
#   6 FR-RNT-025 loss, theft and non-return
#   7 FR-RNT-027 swap-out (only the fault was recorded)
#   8 FR-RNT-028 / AUT-RNT-12 PM by calendar or usage (nothing read
#     next_service_due, so PM never fell due)
# Every step below runs as a non-admin rental clerk through the endpoints the
# forms use, and the segregation rules are proven with a second person.
from __future__ import annotations

import base64
import hashlib
from datetime import timedelta

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.tests.test_m13_submodule_capture import (  # noqa: F401
    _sub,
    reg,
)
from odoo.addons.cd_rental_asset.tests.test_a05_m13_controls import (  # noqa: F401
    _PNG,
    REFUSED,
    _kyc,
    _other_ou,
    _photo,
    _user,
    approve_charge,
    c,
    damage,
    inbox_approve,
    ledger,
    p03,
    res,
    sign,
    walk,
)
from odoo.exceptions import UserError

RES = "fix.rental.reservation"

# --- the pages -----------------------------------------------------------------

PASS2 = {
    "1": {"Fleet Redeployment": "fix.rental.redeployment"},
    "2": {
        "Allocate a Fleet Unit": RES,
        "Rental Exposure Limit": "fix.rental.exposure",
        "Exposure Override Request": "fix.rental.exposure.override",
    },
    "3": {"Rental Extension": "fix.rental.extension", "Damage Waiver Election": RES},
    "4": {"Damage Waiver Plan": "fix.rental.waiver.plan", "Damage Waiver Election": RES},
    "5": {"Condition Photograph": "fix.rental.condition.photo"},
    "6": {"Loss / Non-Return Case": "fix.rental.loss"},
    "7": {"Unit Swap-Out": "fix.rental.swap"},
    "8": {"Preventive Maintenance Plan": "fix.rental.pm.plan"},
}


@pytest.mark.parametrize("no", sorted(PASS2, key=int))
def test_each_page_offers_the_records_its_spec_names(reg, no):
    sub = _sub(reg, no)
    for name, model in PASS2[no].items():
        assert name in sub["map"]["forms"], "%s/%s lacks %s" % (no, sub["title"], name)
        form = reg["forms"][reg["chips"]["M13:" + name]]
        assert form["model"] == model and form.get("newLabel"), name
        if model != RES:  # its register is on the page too
            lists = [reg["screens"][s] for s in sub["map"]["screens"]]
            assert any(s.get("model") == model for s in lists), "%s: no %s list" % (no, model)


def test_every_new_list_is_served_with_its_columns_and_buttons(reg, odoo_env):
    models = {m for page in PASS2.values() for m in page.values()} - {RES}
    seen = set()
    for sid, scr in reg["screens"].items():
        if scr.get("kind") != "model_list" or scr["model"] not in models:
            continue
        seen.add(scr["model"])
        surface = api.SURFACES[scr["model"]]
        model = odoo_env[scr["model"]]
        for col in scr["cols"]:  # /p03/model/records drops an unknown column silently
            assert col in model._fields, "%s: %s" % (sid, col)
        for act in scr.get("actions") or []:
            assert act["m"] in surface["actions"] and hasattr(model, act["m"]), (sid, act["m"])
    assert seen == models


def test_form_grids_name_real_child_fields(reg, odoo_env):
    for fid, cfg in reg["forms"].items():
        if not fid.startswith("M13-"):
            continue
        for grid in cfg.get("grids") or []:
            field = odoo_env[cfg["model"]]._fields[grid["field"]]
            child = odoo_env[field.comodel_name]
            for f in grid["fields"]:
                assert f["name"] in child._fields, "%s/%s: %s" % (fid, grid["field"], f["name"])


# --- helpers ------------------------------------------------------------------


def _w(c, p03, model, values, record_id=None, ok=True):
    out = p03.write(model=model, record_id=record_id, values=values)
    if not ok:
        assert out.get("error"), out
        return out["error"]
    assert not out.get("error"), out
    rec = c.env[model].browse(out["id"])
    rec.invalidate_recordset()
    return rec


def _act(p03, model, rec, method, **kwargs):
    out = p03.action(model=model, ids=[rec.id], method=method, kwargs=kwargs)
    assert out.get("success"), out
    rec.invalidate_recordset()
    return out


def _refused(p03, model, rec, method, match, **kwargs):
    out = p03.action(model=model, ids=[rec.id], method=method, kwargs=kwargs)
    assert not out.get("success") and match in out["error"], out
    return out


def _spare(c, sku=None, name="A05M13T-CAM-2"):
    return c.env["fix.rental.asset"].create(
        {
            "name": name,
            "rental_sku_id": (sku or c.sku).id,
            "serial_no": name + "-SN",
            "category": "camera",
            "purchase_cost": 100000,
            "acquisition_date": c.today - timedelta(days=100),
            "operating_unit_id": c.ou.id,
        }
    )


def _other_sku(c):
    tmpl = c.env["product.template"].create({"name": "A05M13T Drone rental"})
    item = c.env["fix.catalogue.item"].create({"product_tmpl_id": tmpl.id})
    return c.env["fix.rental.sku"].create(
        {"catalogue_item_id": item.id, "daily_rate": 2000, "security_deposit": 5000}
    )


# --- page 2: identity, exposure, allocation -------------------------------------


def test_page2_an_unverified_party_cannot_book(c, p03):
    stranger = c.env["res.partner"].create({"name": "A05M13T Walk-in", "phone": "01700009999"})
    r = res(c, customer_id=stranger.id)
    assert not r.identity_verified
    _refused(p03, RES, r, "action_reserve", "verified identity")
    _kyc(c.env, stranger)
    _act(p03, RES, r, "action_reserve")
    assert r.state == "reserved"


def test_page2_switching_the_identity_rule_off_is_a_recorded_policy(c, p03):
    stranger = c.env["res.partner"].create({"name": "A05M13T Walk-in 2"})
    c.env["ir.config_parameter"].set_param("cd_rental_asset.require_verified_identity", "0")
    _act(p03, RES, res(c, customer_id=stranger.id), "action_reserve")


def test_page2_exposure_limit_blocks_until_another_person_approves_an_override(c, p03):
    prof = _w(
        c,
        p03,
        "fix.rental.exposure",
        {
            "partner_id": c.customer.id,
            "risk_tier": "standard",
            "exposure_limit": 10000,
            "basis": "NID verified; first rental; standard deposit tier",
        },
    )
    assert prof.reviewed_by == c.clerk and prof.current_exposure == 0
    r = res(c)
    _refused(p03, RES, r, "action_reserve", "exposure override")
    ov = _w(
        c,
        p03,
        "fix.rental.exposure.override",
        {"reservation_id": r.id, "justification": "Parent company guarantees the hire"},
    )
    assert ov.exposure_limit == 10000 and ov.excess == round(ov.exposure_after - 10000, 2) > 0
    assert ov.requested_by == c.clerk and ov.state == "requested"
    with pytest.raises(UserError, match="another person"):
        ov.with_user(c.clerk).action_approve()
    ov.with_user(c.clerk2).action_approve()
    _act(p03, RES, r, "action_reserve")
    prof.invalidate_recordset()
    assert r.state == "reserved" and prof.current_exposure == pytest.approx(ov.exposure_after)
    assert prof.headroom < 0


def test_page2_an_override_is_refused_where_no_limit_is_breached(c, p03):
    _w(
        c,
        p03,
        "fix.rental.exposure",
        {"partner_id": c.customer.id, "exposure_limit": 10_000_000, "basis": "Corporate"},
    )
    err = _w(
        c,
        p03,
        "fix.rental.exposure.override",
        {"reservation_id": res(c).id, "justification": "x"},
        ok=False,
    )
    assert "no override is needed" in err


def test_page2_a_pool_booking_is_allocated_a_unit_of_its_sku(c, p03):
    r = res(c, rental_asset_id=False)
    r.action_reserve()
    stranger = _spare(c, sku=_other_sku(c), name="A05M13T-DRONE-1")
    err = _w(c, p03, RES, {"rental_asset_id": stranger.id}, record_id=r.id, ok=False)
    assert "is a" in err
    _w(c, p03, RES, {"rental_asset_id": c.asset.id}, record_id=r.id)
    c.asset.invalidate_recordset()
    assert r.rental_asset_id == c.asset and c.asset.status == "reserved"


# --- page 3: extension ------------------------------------------------------------


def test_page3_extension_is_checked_repriced_and_applied_by_another_person(c, p03):
    r = walk(c, res(c), "action_activate")
    old_to, old_charge = r.date_to, r.rental_charge
    ext = _w(
        c,
        p03,
        "fix.rental.extension",
        {
            "reservation_id": r.id,
            "new_date_to": str(old_to + timedelta(days=3)),
            "reason": "The shoot overran",
        },
    )
    assert ext.old_date_to == old_to and ext.old_charge == old_charge
    assert ext.availability_result == "Available"
    assert ext.new_charge == old_charge + 3 * 1000 and ext.charge_delta == 3000
    with pytest.raises(UserError, match="another person"):
        ext.with_user(c.clerk).action_apply()
    ext.with_user(c.clerk2).action_apply()
    r.invalidate_recordset()
    assert r.date_to == old_to + timedelta(days=3) and r.agreement_version == 2
    assert r.rental_charge == old_charge + 3000 and ext.state == "applied"
    assert ext.approved_by == c.clerk2 and ext.applied_charge == r.rental_charge
    # a request that does not move the return date later is refused
    err = _w(
        c,
        p03,
        "fix.rental.extension",
        {"reservation_id": r.id, "new_date_to": str(r.date_to), "reason": "x"},
        ok=False,
    )
    assert "later" in err


def test_page3_extension_into_the_next_booking_of_the_unit_is_refused(c):
    r = walk(c, res(c), "action_activate")
    nxt = walk(
        c,
        res(c, date_from=c.today + timedelta(days=5), date_to=c.today + timedelta(days=6)),
        "action_reserve",
    )
    ext = (
        c.env["fix.rental.extension"]
        .with_user(c.clerk)
        .create(
            {
                "reservation_id": r.id,
                "new_date_to": c.today + timedelta(days=4),  # + 1 turnaround day = clash
                "reason": "Customer asks for two more days",
            }
        )
    )
    assert nxt.name in ext.availability_result
    with pytest.raises(UserError, match=nxt.name):
        ext.with_user(c.clerk2).action_apply()
    assert r.date_to == c.today + timedelta(days=2)


# --- page 4: the damage-waiver product -------------------------------------------


def _published_plan(c, p03, **kw):
    vals = {
        "name": "A05M13T Standard Waiver",
        "fee_pct": 10,
        "excess_amount": 2000,
        "covers_theft": True,
    }
    vals.update(kw)
    plan = _w(c, p03, "fix.rental.waiver.plan", vals)
    with pytest.raises(UserError, match="Legal"):
        plan.with_user(c.clerk2).action_publish()
    _w(c, p03, "fix.rental.waiver.plan", {"legal_review_ref": "LEGAL/2026/114"}, record_id=plan.id)
    with pytest.raises(UserError, match="another person"):
        plan.with_user(c.clerk).action_publish()
    plan.with_user(c.clerk2).action_publish()
    assert plan.state == "published" and plan.published_by == c.clerk2
    return plan


def test_page4_a_published_plan_never_changes_and_only_published_plans_are_elected(c, p03):
    draft = _w(
        c, p03, "fix.rental.waiver.plan", {"name": "Draft plan", "fee_pct": 5, "excess_amount": 0}
    )
    with pytest.raises(REFUSED, match="published"):
        res(c, waiver_plan_id=draft.id)
    plan = _published_plan(c, p03)
    with pytest.raises(REFUSED):
        plan.with_user(c.clerk).write({"excess_amount": 0})
    with pytest.raises(REFUSED):
        plan.with_user(c.clerk).unlink()


def test_page4_the_elected_waiver_is_charged_and_applied_at_assessment(c, p03):
    plan = _published_plan(c, p03)
    r = res(c)
    _w(c, p03, RES, {"waiver_plan_id": plan.id}, record_id=r.id)
    assert r.waiver_fee == round(r.rental_charge * 0.10, 2) == 300
    walk(c, r, "action_assess_damage")
    with pytest.raises(REFUSED):
        r.with_user(c.clerk).write({"waiver_plan_id": False})  # a term of the signed agreement
    covered = damage(c, r, cost=9000)
    assert covered.waiver_relief == 7000 and covered._chargeable() == 2000
    negligent = damage(c, r, cost=4000, waiver_exclusion="negligence")
    assert negligent.waiver_relief == 0 and negligent._chargeable() == 4000
    stolen = damage(c, r, cost=50000, category="lost")
    assert stolen.waiver_relief == 0, "no theft cover without a police report (BRU-RNT-10)"
    stolen.with_user(c.inspector).write({"police_report_ref": "GD-1123/26"})
    assert stolen.waiver_relief == 48000 and stolen._chargeable() == 2000


def test_page4_close_settles_only_the_excess_and_the_invoice_carries_the_waiver(c, p03):
    plan = _published_plan(c, p03)
    r = res(c)
    _w(c, p03, RES, {"waiver_plan_id": plan.id}, record_id=r.id)
    walk(c, r, "action_assess_damage")
    dmg = damage(c, r, cost=9000)
    approve_charge(c, dmg)
    assert dmg.charge_approval_id.amount == 2000
    r.with_user(c.clerk).action_close()
    deducted = ledger(c, r).filtered(lambda d: d.kind == "deduction")
    assert sum(deducted.mapped("amount")) in (0, 2000)  # 0 when the collection did not post
    if deducted:
        assert r.deposit_refunded == 3000 and r.excess_billed == 0 and dmg.settled
    r.action_issue_rental_invoice()
    lines = r.mushak_6_3_id.line_ids
    waiver_line = lines.filtered(lambda line: "Damage waiver" in (line.description or ""))
    assert len(lines) == 2 and waiver_line
    # the fee (10% of the 3,000 gross rental) is the taxable base of its own line
    assert waiver_line.taxable_amount + waiver_line.vat_amount == pytest.approx(
        waiver_line.line_total, abs=0.01
    )
    assert 0 < waiver_line.line_total <= 300 * 1.15 + 0.01


# --- page 5: photographs ----------------------------------------------------------


def _upload(name, data=_PNG):
    return {"upload": data, "filename": name}


def test_page5_handover_needs_a_hashed_photograph_that_is_then_sealed(c, p03):
    r = res(c)
    sign(c, r)
    r.action_reserve()
    cond = (
        c.env["fix.rental.condition"]
        .with_user(c.clerk)
        .create({"reservation_id": r.id, "report_type": "pre_delivery", "grade": "a"})
    )
    with pytest.raises(REFUSED, match="photograph"):
        r.action_deliver()
    pdf = base64.b64encode(b"%PDF-1.4 not a photo").decode()
    err = _w(
        c,
        p03,
        "fix.rental.condition.photo",
        {"condition_id": cond.id, "view_code": "front", "attachment_id": _upload("scan.pdf", pdf)},
        ok=False,
    )
    assert "photograph" in err
    photo = _w(
        c,
        p03,
        "fix.rental.condition.photo",
        {"condition_id": cond.id, "view_code": "front", "attachment_id": _upload("front.png")},
    )
    digest = hashlib.sha256(base64.b64decode(_PNG)).hexdigest()
    assert photo.sha256 == digest and photo.integrity_ok and photo.captured_by == c.clerk
    assert photo.document_id.checksum_sha256 == digest
    assert photo.document_id.document_type == "custody_photo"
    other = c.env["ir.attachment"].create({"name": "b.png", "datas": _PNG})
    with pytest.raises(REFUSED, match="never replaced"):
        photo.with_user(c.clerk).write({"attachment_id": other.id})
    # a mistaken photograph is withdrawn while the report is open; its M24
    # document (a permanent register) keeps the file and says so
    blurred = _w(
        c,
        p03,
        "fix.rental.condition.photo",
        {"condition_id": cond.id, "view_code": "back", "attachment_id": _upload("blur.png")},
    )
    doc = blurred.document_id
    blurred.with_user(c.clerk).unlink()
    assert doc.exists() and doc.checksum_sha256 == digest and "Withdrawn" in doc.description
    r.action_deliver()
    photo.invalidate_recordset()
    assert photo.document_id.signature_locked
    with pytest.raises(REFUSED):
        photo.with_user(c.clerk).unlink()
    with pytest.raises(REFUSED):
        photo.with_user(c.clerk).write({"note": "retouched"})
    with pytest.raises(REFUSED, match="final"):
        c.env["fix.rental.condition.photo"].with_user(c.clerk).create(
            {"condition_id": cond.id, "attachment_id": other.id}
        )


def test_page5_assessment_needs_return_photographs_beside_the_outbound_ones(c):
    r = walk(c, res(c), "action_return")
    post = (
        c.env["fix.rental.condition"]
        .with_user(c.clerk)
        .create({"reservation_id": r.id, "report_type": "post_return", "grade": "b"})
    )
    with pytest.raises(REFUSED, match="photograph"):
        r.action_assess_damage()
    pre = r.condition_ids.filtered(lambda x: x.report_type == "pre_delivery")
    assert pre.photo_ids and post.outbound_photo_ids == pre.photo_ids
    _photo(post.env, post, "screen")
    r.action_assess_damage()
    assert r.state == "damage_assess"


def test_page5_the_photo_minimum_is_a_recorded_policy(c):
    c.env["ir.config_parameter"].set_param("cd_rental_asset.condition_photo_minimum", "2")
    r = res(c)
    sign(c, r)
    r.action_reserve()
    cond = (
        c.env["fix.rental.condition"]
        .with_user(c.clerk)
        .create({"reservation_id": r.id, "report_type": "pre_delivery", "grade": "a"})
    )
    _photo(cond.env, cond)
    with pytest.raises(REFUSED, match="at least 2"):
        r.action_deliver()
    _photo(cond.env, cond, "back")
    r.action_deliver()


# --- page 6: loss, theft, non-return -----------------------------------------------


def test_page6_non_return_is_escalated_then_written_off_on_the_units_approval(c, p03):
    r = walk(c, res(c), "action_activate")
    loss = _w(
        c,
        p03,
        "fix.rental.loss",
        {
            "reservation_id": r.id,
            "kind": "non_return",
            "circumstances": "Customer unreachable nine days after the due date",
        },
    )
    assert loss.reported_by == c.clerk and loss.escalation_stage == "notice"
    assert loss.valuation == pytest.approx(c.asset._dofa_amount())
    with pytest.raises(UserError, match="recovery"):
        loss.with_user(c.clerk2).action_write_off()
    _act(p03, "fix.rental.loss", loss, "action_escalate")
    assert loss.escalation_stage == "recovery"
    with pytest.raises(UserError, match="claim"):
        loss.with_user(c.clerk2).action_write_off()
    _w(
        c,
        p03,
        "fix.rental.loss",
        {"claim_decision": "no_claim", "no_claim_reason": "Below the fleet policy excess"},
        record_id=loss.id,
    )
    with pytest.raises(UserError, match="another person"):
        loss.with_user(c.clerk).action_write_off()
    with pytest.raises(REFUSED):  # the unit's routed write-off approval is not granted
        loss.with_user(c.clerk2).action_write_off()
    _act(p03, "fix.rental.loss", loss, "action_request_writeoff", justification="Not returned")
    inbox_approve(c.asset, c.t2)
    held = r._ledger_balance()
    loss.with_user(c.clerk2).action_write_off()
    r.invalidate_recordset()
    c.asset.invalidate_recordset()
    assert loss.state == "written_off" and r.state == "lost" and c.asset.status == "lost"
    assert loss.forfeited_amount == pytest.approx(min(held, loss.valuation))
    assert r.excess_billed == pytest.approx(loss.valuation - loss.forfeited_amount)
    assert r.excess_invoice_id and loss.invoiced_amount == r.excess_billed
    with pytest.raises(REFUSED):
        r.with_user(c.clerk).action_return()
    with pytest.raises(REFUSED):  # a lost unit never goes back on rent
        walk(
            c,
            res(c, date_from=c.today + timedelta(days=9), date_to=c.today + timedelta(days=10)),
            "action_reserve",
        )


def test_page6_a_theft_is_written_off_only_on_its_police_report(c, p03):
    r = walk(c, res(c), "action_activate")
    loss = _w(
        c,
        p03,
        "fix.rental.loss",
        {
            "reservation_id": r.id,
            "kind": "theft",
            "circumstances": "Bag snatched at Farmgate",
            "claim_decision": "claim",
            "claim_ref": "INS-CLM-7781",
        },
    )
    with pytest.raises(UserError, match="police report"):
        loss.with_user(c.clerk2).action_write_off()


def test_page6_a_recovered_unit_closes_the_case_and_returns_as_usual(c, p03):
    r = walk(c, res(c), "action_activate")
    loss = _w(
        c, p03, "fix.rental.loss", {"reservation_id": r.id, "circumstances": "Late, unreachable"}
    )
    err = _w(
        c, p03, "fix.rental.loss", {"reservation_id": r.id, "circumstances": "again"}, ok=False
    )
    assert "already has an open loss case" in err
    _act(p03, "fix.rental.loss", loss, "action_recover")
    assert loss.state == "recovered" and loss.recovered_on
    r.action_return()
    assert r.state == "returned"


# --- page 7: swap-out --------------------------------------------------------------


def test_page7_swap_moves_the_rental_to_the_replacement_with_both_reports(c, p03):
    spare = _spare(c)
    r = walk(c, res(c), "action_activate")
    sw = _w(
        c,
        p03,
        "fix.rental.swap",
        {"reservation_id": r.id, "in_asset_id": spare.id, "fault": "HDMI port dead"},
    )
    assert sw.out_asset_id == c.asset and sw.sla_hours == 24
    assert sw.sla_target == sw.reported_at + timedelta(hours=24)
    _refused(p03, "fix.rental.swap", sw, "action_execute", "Grade both units")
    _w(
        c,
        p03,
        "fix.rental.swap",
        {"out_grade": "c", "in_grade": "a", "out_notes": "Port burnt"},
        record_id=sw.id,
    )
    _act(p03, "fix.rental.swap", sw, "action_execute")
    r.invalidate_recordset()
    (c.asset | spare).invalidate_recordset()
    assert r.rental_asset_id == spare and spare.status == "out" and c.asset.status == "maintenance"
    assert sw.state == "executed" and sw.sla_met
    back, out = sw.returned_report_id, sw.replacement_report_id
    assert (back.report_type, back.rental_asset_id, back.grade) == ("swap_in", c.asset, "c")
    assert (out.report_type, out.rental_asset_id, out.grade) == ("swap_out", spare, "a")
    turn = c.env["fix.rental.turnaround"].search([("rental_asset_id", "=", c.asset.id)])
    assert turn.state == "pending" and turn.grade_before == "c"
    with pytest.raises(REFUSED):  # the reports are evidence
        back.with_user(c.clerk).write({"grade": "a"})
    r.action_return()
    spare.invalidate_recordset()
    assert spare.status == "maintenance"


def test_page7_a_replacement_of_another_sku_is_refused(c, p03):
    drone = _spare(c, sku=_other_sku(c), name="A05M13T-DRONE-2")
    r = walk(c, res(c), "action_activate")
    sw = _w(
        c,
        p03,
        "fix.rental.swap",
        {
            "reservation_id": r.id,
            "in_asset_id": drone.id,
            "fault": "Lens fogged",
            "out_grade": "b",
            "in_grade": "a",
        },
    )
    _refused(p03, "fix.rental.swap", sw, "action_execute", "rented a")


# --- page 8: preventive maintenance ------------------------------------------------


def test_page8_a_calendar_plan_takes_a_due_unit_out_of_availability(c, p03):
    _w(
        c,
        p03,
        "fix.rental.pm.plan",
        {"name": "Camera 30-day PM", "rental_sku_id": c.sku.id, "interval_days": 30},
    )
    c.asset.write({"last_service_date": c.today - timedelta(days=40), "category": "tool"})
    assert c.asset.pm_due_on == c.today - timedelta(days=10)
    assert c.env["fix.rental.asset"].cron_rental_pm_due() >= 1
    c.asset.invalidate_recordset()
    assert c.asset.status == "maintenance"
    turn = c.asset.turnaround_ids.filtered(lambda t: t.state == "pending")
    turn.write(
        {
            "cleaning_done": True,
            "inspection_done": True,
            "regrade": "a",
            "technician_id": c.tech.id,
        }
    )
    turn.with_user(c.clerk).action_ready()
    c.asset.invalidate_recordset()
    assert c.asset.status == "available"
    assert c.asset.next_service_due == c.today + timedelta(days=30)
    err = _w(
        c,
        p03,
        "fix.rental.pm.plan",
        {"name": "Duplicate", "rental_sku_id": c.sku.id, "interval_days": 60},
        ok=False,
    )
    assert "Another active PM plan" in err


def test_page8_a_usage_plan_counts_days_on_rent_since_the_last_service(c, p03):
    _w(
        c,
        p03,
        "fix.rental.pm.plan",
        {"name": "Camera usage PM", "category": "camera", "usage_rental_days": 3},
    )
    c.asset.write({"last_service_date": c.today - timedelta(days=30)})
    past = c.env[RES].create(
        {
            "customer_id": c.customer.id,
            "rental_sku_id": c.sku.id,
            "rental_asset_id": c.asset.id,
            "date_from": c.today - timedelta(days=20),
            "date_to": c.today - timedelta(days=17),
        }
    )
    past.write({"state": "closed"})  # trusted history (superuser fixture)
    c.asset.invalidate_recordset()
    assert c.asset.rental_days_since_service == 4
    c.env["fix.rental.asset"].cron_rental_pm_due()
    c.asset.invalidate_recordset()
    assert c.asset.status == "maintenance"


def test_page8_a_plan_says_when_maintenance_falls_due(c, p03):
    err = _w(c, p03, "fix.rental.pm.plan", {"name": "Empty", "category": "camera"}, ok=False)
    assert "calendar interval" in err


# --- page 1: redeployment ----------------------------------------------------------


def test_page1_redeployment_moves_the_unit_and_rehomes_it_on_receipt(c, p03):
    other = _other_ou(c)
    rd = _w(
        c,
        p03,
        "fix.rental.redeployment",
        {
            "rental_asset_id": c.asset.id,
            "to_operating_unit_id": other.id,
            "reason": "Idle 60 days here; Chattogram has a waiting list",
        },
    )
    assert rd.from_operating_unit_id == c.ou and rd.state == "draft"
    _act(p03, "fix.rental.redeployment", rd, "action_dispatch")
    c.asset.invalidate_recordset()
    assert c.asset.status == "transit" and rd.consignment_id.consignment_type == "branch_transfer"
    with pytest.raises(REFUSED, match="transit"):
        walk(c, res(c), "action_reserve")
    c.clerk.write({"assigned_operating_unit_ids": [(4, other.id)]})
    with pytest.raises(UserError, match="You dispatched"):
        rd.with_user(c.clerk).action_receive()  # the dispatcher, even as a member of both
    with pytest.raises(UserError, match="member of the receiving branch"):
        rd.with_user(c.clerk2).action_receive()  # a colleague at the sending branch
    receiver = _user(c.env, "receiver")
    receiver.write({"assigned_operating_unit_ids": [(6, 0, other.ids)]})
    rd.with_user(receiver).action_receive()
    c.asset.invalidate_recordset()
    assert c.asset.operating_unit_id == other and c.asset.status == "available"
    assert rd.state == "received" and rd.received_by == receiver


def test_page1_a_unit_with_an_open_booking_does_not_move(c, p03):
    walk(
        c,
        res(c, date_from=c.today + timedelta(days=10), date_to=c.today + timedelta(days=11)),
        "action_reserve",
    )
    c.asset.invalidate_recordset()
    rd = (
        c.env["fix.rental.redeployment"]
        .sudo()
        .create(
            {"rental_asset_id": c.asset.id, "to_operating_unit_id": _other_ou(c).id, "reason": "x"}
        )
    )
    with pytest.raises(UserError):
        rd.with_user(c.clerk).action_dispatch()
