# M18 E-Waste & Recycling: capture pass 2 (19 Nov 2026).
#
# Reported again: "not all the sub-modules have a relevant data capture
# button". After the 13 Nov pass every page had a button, but read against
# the specification (FR-ESG-001..026, BRU-ESG-01..20, the owned entities of
# §10.1) the pages could not record what the spec says is recorded there:
#   1  no channel / condition / hazard flags / photo; no corporate disposal
#      reconciled to the client's declared assets (FR-ESG-005, BRU-ESG-14)
#   2  no published triage criteria, no harvest or donation route
#      (FR-ESG-006/007/008/023, BRU-ESG-09/15)
#   4  no downstream-vendor declarations (FR-ESG-024, BRU-ESG-18)
#   5  an item missing from the recycler's certificate could not be flagged;
#      no material recovery by class (FR-ESG-013/014, BRU-ESG-04/19)
#   6/7 no collection-point register, T-06 a single global ceiling
#   9  no versioned factor set (FR-ESG-019, T-08)
#   10 no regulatory register (FR-ESG-016, BRU-ESG-16)
# Every step below runs through the endpoint its form uses, as non-admin users
# holding only their M18 roles (cd_ewaste's own fixtures).
from __future__ import annotations

import base64
import inspect
from datetime import timedelta

import pytest
from odoo.addons.cd_ewaste.models import ewaste_common as c
from odoo.addons.cd_ewaste.tests.m18_fixtures import M18, G, attachment, make_user, refused
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a05.writable import WRITABLE
from odoo.addons.cd_p03_portal.tests.test_m18_submodule_capture import reg  # noqa: F401

SCAN = base64.b64encode(b"%PDF-1.4 m18 pass 2 evidence").decode()
COL = "fix.ewaste.collection"
POINT = "fix.ewaste.collection.point"
CORP = "fix.ewaste.corporate.disposal"
CRIT = "fix.ewaste.triage.criteria"
TRI = "fix.ewaste.triage"
DON = "fix.ewaste.donation"
DOWN = "fix.ewaste.partner.downstream"
EXC = "fix.ewaste.certificate.exception"
REC = "fix.ewaste.material.recovery"
FAC = "fix.esg.factor.set"
OBL = "fix.ewaste.obligation"
NEW_MODELS = (POINT, CORP, CORP + ".line", CRIT, DON, DOWN, EXC, REC, FAC, OBL)


def _sub(reg, no):  # noqa: F811
    return next(s for s in reg["subs"] if s["no"] == no)


def _ok(out):
    assert out and not out.get("error") and out.get("success", True) is not False, out
    return out


def _err(out):
    assert out.get("error") or out.get("success") is False, out
    return out.get("error") or ""


# ============================================================ the pages
CHIPS = {
    "1": {"Corporate Disposal Contract", "Accept a Corporate Asset Exception"},
    "2": {"Triage Criteria", "Route for Parts Harvest", "Donation Hand-over"},
    "4": {"Downstream Vendor Declaration"},
    "5": {"Close a Certificate Exception", "Material Recovery"},
    "6": {"Collection Point"},
    "7": {"Collection Point"},
    "9": {"Emission Factor Set"},
    "10": {"Regulatory Obligation", "Review an Obligation", "DoE E-Waste Registration"},
}
LISTS = {
    "1": {"M18-corporate", "M18-corporate-lines"},
    "2": {"M18-criteria", "M18-donations"},
    "4": {"M18-downstream"},
    "5": {"M18-exceptions", "M18-recovery"},
    "6": {"M18-points"},
    "7": {"M18-points"},
    "9": {"M18-factors"},
    "10": {"M18-obligations", "M18-registration"},
}


@pytest.mark.parametrize("no", sorted(CHIPS, key=int))
def test_each_page_offers_what_the_spec_records_there(reg, no):  # noqa: F811
    sub = _sub(reg, no)
    assert CHIPS[no] <= set(sub["map"]["forms"]), (no, sub["map"]["forms"])
    assert LISTS[no] <= set(sub["map"]["screens"]), (no, sub["map"]["screens"])
    for name in CHIPS[no]:
        assert reg["chips"].get("M18:" + name) in reg["forms"], name


def test_page9_captures_the_factor_set_and_its_figures_stay_computed(reg):  # noqa: F811
    sub = _sub(reg, "9")
    assert sub["create"]["screen"] == "M18-form-factor"
    assert reg["screens"]["M18-esg"].get("create") is False
    assert reg["forms"]["M18-form-esg"].get("create") is False
    assert WRITABLE["fix.esg.metric"] == frozenset()


def test_page10_lists_the_regulatory_register(reg):  # noqa: F811
    sub = _sub(reg, "10")
    assert sub["map"]["model"] == OBL
    assert sub["create"]["screen"] == "M18-form-obligation"


def test_every_new_model_is_served_with_its_steps(reg):  # noqa: F811
    for model in NEW_MODELS:
        assert model in api.SURFACES, model
    for fid, cfg in reg["forms"].items():
        if not fid.startswith("M18-"):
            continue
        act = cfg.get("saveAction")
        if act:
            assert act["method"] in api.SURFACES[cfg["model"]]["actions"], fid


def test_step_form_kwargs_are_the_methods_parameters(reg, odoo_env):  # noqa: F811
    for fid, cfg in reg["forms"].items():
        act = fid.startswith("M18-") and cfg.get("saveAction")
        if not act or not act.get("kwargs"):
            continue
        method = getattr(odoo_env[cfg["model"]], act["method"])
        params = inspect.signature(method).parameters
        for kwarg, field in act["kwargs"].items():
            assert kwarg in params, (fid, kwarg)
            assert field in odoo_env[cfg["model"]]._fields, (fid, field)


def test_no_form_omits_a_required_field_without_default(reg, odoo_env):  # noqa: F811
    """A creatable form must offer every field the model requires and does
    not default, or "+ New" can never save (the M07 renewal defect)."""
    for fid, cfg in reg["forms"].items():
        if not fid.startswith("M18-") or cfg.get("create") is False or cfg.get("pickRecord"):
            continue
        model = odoo_env[cfg["model"]]
        shown = {f["name"] for s in cfg["sections"] for f in s["fields"]}
        defaults = model.default_get(list(model._fields))
        for name, field in model._fields.items():
            if (
                field.required
                and field.store
                and not field.compute
                and not field.related
                and name not in defaults
                and name not in ("name",)  # sequence-numbered on create
                and name not in shown
            ):
                assert field.default is not None, "%s omits required %s" % (fid, name)


def test_grid_fields_exist_on_the_line_model(reg, odoo_env):  # noqa: F811
    for fid, cfg in reg["forms"].items():
        if not fid.startswith("M18-"):
            continue
        model = odoo_env[cfg["model"]]
        for grid in cfg.get("grids") or []:
            field = model._fields[grid["field"]]
            assert field.type == "one2many", fid
            assert grid["field"] in WRITABLE[cfg["model"]], fid
            comodel = odoo_env[field.comodel_name]
            for col in grid["fields"]:
                assert col["name"] in comodel._fields, (fid, col["name"])


def test_new_evidence_is_uploaded_not_picked(reg):  # noqa: F811
    links = {
        "M18-form-collection": ("photo_attachment_id", "photo_file"),
        "M18-form-triage": ("evidence_attachment_id", "evidence_file"),
        "M18-form-donation": ("acknowledgement_attachment_id", "acknowledgement_file"),
        "M18-form-downstream": ("evidence_attachment_id", "evidence_file"),
        "M18-form-factor": ("evidence_attachment_id", "evidence_file"),
    }
    for fid, (link, upload) in links.items():
        spec = {f["name"]: f for s in reg["forms"][fid]["sections"] for f in s["fields"]}
        assert spec[link].get("readonly") and spec[upload].get("type") == "file", fid
        model = reg["forms"][fid]["model"]
        assert link not in WRITABLE[model] and upload in WRITABLE[model], model


# ============================================================ fixtures
@pytest.fixture
def m(odoo_env):
    x = M18(odoo_env)
    try:
        yield x
    finally:
        x.close()


def _point(m, **vals):
    vals.setdefault("name", "M18 Point %s" % len(m.env[POINT].search([])))
    vals.setdefault("kind", "branch")
    vals.setdefault("capacity_kg", 500.0)
    vals.setdefault("responsible_id", m.env["hr.employee"].create({"name": "Point Lead"}).id)
    point = m.env[POINT].with_user(m.clerk).create(vals)
    hse2 = make_user(m.env, "hse2", [G.hse])
    point.with_user(hse2).action_activate()
    return point


def _bound_item(m, **vals):
    """A data-bearing phone with a verified M06 certificate bound to it."""
    dev = m.device()
    col = m.collection(device_id=dev.id, **vals)
    cert = m.verified_cert(dev.serial_number)
    col.with_user(m.clerk).write({"wipe_certificate_id": cert.id})
    return col


# ============================================================ p6/p7 points
def test_collection_point_registered_with_ceilings_and_activated_by_hse(m):
    out = _ok(
        m.p03_write(
            m.clerk,
            POINT,
            None,
            {
                "name": "Dhanmondi Hazmat Store",
                "kind": "hazmat_store",
                "capacity_kg": 400.0,
                "responsible_id": m.env["hr.employee"].create({"name": "Store Lead"}).id,
            },
        )
    )
    point = m.env[POINT].browse(out["id"])
    # no ceiling yet: a hazardous store is not activated without them (T-06)
    assert "ceiling" in _err(m.p03_action(m.hse, POINT, [point.id], "action_activate"))
    point.with_user(m.clerk).write(
        {"limit_ids": [(0, 0, {"hazard_class": "li_sound", "max_kg": 10.0})]}
    )
    # the registrant does not activate it, even holding the role
    hse_reg = make_user(m.env, "hsereg", [G.hse])
    p2 = (
        m.env[POINT]
        .with_user(hse_reg)
        .create({"name": "Self", "capacity_kg": 1, "responsible_id": point.responsible_id.id})
    )
    assert refused(m.env, lambda: p2.with_user(hse_reg).action_activate())
    assert refused(m.env, lambda: point.with_user(m.clerk).action_activate())
    _ok(m.p03_action(m.hse, POINT, [point.id], "action_activate"))
    point.invalidate_recordset()
    assert point.state == "active" and point.approved_by_id == m.hse
    # frozen while active
    assert refused(m.env, lambda: point.with_user(m.clerk).write({"capacity_kg": 9999.0}))
    assert refused(m.env, lambda: point.limit_ids.with_user(m.clerk).write({"max_kg": 999.0}))
    assert {"capacity_kg", "limit_ids"} <= api._locked_fields(point)


def test_battery_ceiling_is_per_point_and_class(m):
    point = (
        m.env[POINT]
        .with_user(m.clerk)
        .create(
            {
                "name": "Ceiling Point",
                "kind": "hazmat_store",
                "capacity_kg": 100,
                "responsible_id": m.env["hr.employee"].create({"name": "Lead"}).id,
                "limit_ids": [(0, 0, {"hazard_class": "li_sound", "max_kg": 5.0})],
            }
        )
    )
    # A05 S3 M18-22: a hazmat item is recorded by an HSE officer (not the
    # counter) and names the intake it was found in
    found_in = m.collection(weight_kg=2.0)
    hse_batteries = m.env["fix.ewaste.battery"].with_user(m.hse)

    class Bat:
        @staticmethod
        def create(vals):
            return hse_batteries.create({"collection_id": found_in.id, **vals})

    # a draft point holds nothing
    assert refused(
        m.env,
        lambda: Bat.create(
            {"chemistry": "li_ion", "weight_kg": 1, "collection_point_id": point.id}
        ),
    )
    point.with_user(m.hse).action_activate()
    b1 = Bat.create({"chemistry": "li_ion", "weight_kg": 4.0, "collection_point_id": point.id})
    assert b1.hazmat_class == "li_sound" and b1.storage_location == point.name
    # T-06: beyond the class ceiling
    assert refused(
        m.env,
        lambda: Bat.create(
            {"chemistry": "li_ion", "weight_kg": 2.0, "collection_point_id": point.id}
        ),
    )
    # BRU-ESG-07: a class the point is not designated for
    err = refused(
        m.env,
        lambda: Bat.create({"chemistry": "crt", "weight_kg": 1.0, "collection_point_id": point.id}),
    )
    assert err and "not designated" in str(err)
    # a swollen cell is a different (stricter) class
    assert refused(
        m.env,
        lambda: Bat.create(
            {
                "chemistry": "li_ion",
                "swollen_cell": True,
                "weight_kg": 0.5,
                "collection_point_id": point.id,
            }
        ),
    )


def test_collection_received_only_at_an_active_point(m):
    draft = m.env[POINT].with_user(m.clerk).create({"name": "Draft Bin", "kind": "public_bin"})
    assert refused(m.env, lambda: m.collection(collection_point_id=draft.id))
    point = _point(m, kind="public_bin")
    col = m.collection(collection_point_id=point.id, weight_kg=0.4)
    assert point.held_kg == pytest.approx(0.4)
    assert col.channel == "branch_dropoff"


# ============================================================ p1 receipt
def test_receipt_record_with_photo_frozen_after_triage(m):
    out = _ok(
        m.p03_write(
            m.clerk,
            COL,
            None,
            {
                "customer_id": m.customer.id,
                "weight_kg": 0.3,
                "material_type": "phone",
                "channel": "service_unrepairable",
                "condition": "dead",
                "has_battery": True,
                "photo_file": SCAN,
                "photo_filename": "receipt.jpg",
            },
        )
    )
    col = m.env[COL].browse(out["id"])
    assert col.channel == "service_unrepairable" and col.condition == "dead" and col.has_battery
    assert col.photo_attachment_id.name == "receipt.jpg"
    assert (col.photo_attachment_id.res_model, col.photo_attachment_id.res_id) == (COL, col.id)
    m.triage(col, "recycle")
    for vals in ({"channel": "corporate"}, {"has_crt": True}, {"condition": "working"}):
        assert refused(m.env, lambda v=vals: col.with_user(m.clerk).write(v)), vals
    assert {"channel", "photo_file", "condition"} <= api._locked_fields(col)


def test_hazard_flags_open_one_hazmat_record_each(m):
    col = m.collection(weight_kg=3.0, material_type="other", has_battery=True, has_crt=True)
    m.triage(col, "hazardous")
    assert col.state == "hazmat"
    assert sorted(col.battery_ids.mapped("chemistry")) == ["crt", "li_ion"]
    assert sum(col.battery_ids.mapped("weight_kg")) == pytest.approx(3.0)


# ============================================================ p1 corporate
def test_corporate_disposal_closes_only_when_every_asset_reconciles(m):
    client = m.env["res.partner"].create({"name": "M18 Corporate Client"})
    out = _ok(
        m.p03_write(
            m.clerk,
            CORP,
            None,
            {"client_id": client.id, "contract_ref": "PO-77"},
        )
    )
    disposal = m.env[CORP].browse(out["id"])
    disposal.with_user(m.clerk).write(
        {
            "line_ids": [
                (0, 0, {"asset_ref": "ASSET-1", "material_type": "phone"}),
                (0, 0, {"asset_ref": "ASSET-2", "material_type": "laptop"}),
            ]
        }
    )
    a1, a2 = disposal.line_ids.sorted("id")
    # receiving starts only with a list, then the list freezes
    _ok(m.p03_action(m.clerk, CORP, [disposal.id], "action_confirm"))
    disposal.invalidate_recordset()
    assert disposal.state == "receiving"
    assert refused(m.env, lambda: a1.with_user(m.clerk).write({"asset_ref": "OTHER"}))
    assert refused(
        m.env,
        lambda: disposal.with_user(m.clerk).write({"line_ids": [(0, 0, {"asset_ref": "LATE"})]}),
    )
    # a declared asset is received only from the contract's client
    assert refused(m.env, lambda: m.collection(corporate_line_id=a1.id))
    dev = m.device()
    col = m.collection(
        customer_id=client.id, corporate_line_id=a1.id, device_id=dev.id, weight_kg=0.5
    )
    assert col.channel == "corporate" and col.corporate_disposal_id == disposal
    assert a1.line_state == "received"
    # the same asset twice is refused
    assert refused(m.env, lambda: m.collection(customer_id=client.id, corporate_line_id=a1.id))
    # not closable: nothing reconciled yet
    assert "BRU-ESG-14" in _err(m.p03_action(m.compliance, CORP, [disposal.id], "action_close"))
    # ASSET-1 goes all the way to its disposal certificate
    cert = m.verified_cert(dev.serial_number)
    m.triage(col, "recycle", data_bearing=True)
    col.with_user(m.clerk).write({"wipe_certificate_id": cert.id})
    # A05 S3 M18-28: destruction and release are the floor's (dispatcher)
    col.with_user(m.dispatcher).action_secure_destruction()
    col.with_user(m.dispatcher).action_recycle_estimated()
    m.issued_certificate(m.processed_batch([col]))
    a1.invalidate_recordset()
    assert a1.line_state == "reconciled"
    # ASSET-2 never arrived: an exception needs a reason and a compliance officer
    assert (
        "document why"
        in _err(
            m.p03_action(m.compliance, CORP + ".line", [a2.id], "action_accept_exception")
        ).lower()
    )
    assert refused(m.env, lambda: a2.with_user(m.clerk).action_accept_exception("lost"))
    _ok(
        m.p03_action(
            m.compliance,
            CORP + ".line",
            [a2.id],
            "action_accept_exception",
            {"reason": "Client retained the unit (letter on file)"},
        )
    )
    a2.invalidate_recordset()
    assert a2.line_state == "exception" and a2.exception_by_id == m.compliance
    assert refused(m.env, lambda: disposal.with_user(m.clerk).action_close())  # role
    _ok(m.p03_action(m.compliance, CORP, [disposal.id], "action_close"))
    disposal.invalidate_recordset()
    assert disposal.state == "closed" and disposal.open_count == 0


# ============================================================ p2 criteria
def _criteria(m, name="TRI-1", **vals):
    vals = {
        "name": name,
        "reuse_criteria": "Boots, all functions pass",
        "harvest_criteria": "Dead board, good screen or camera",
        "recycle_criteria": "No economic repair or part value",
        "hazardous_criteria": "Swollen cell, CRT, mercury, refrigerant",
        "donation_max_value": 3000.0,
        **vals,
    }
    return m.env[CRIT].with_user(m.compliance).create(vals)


def test_criteria_published_by_a_second_officer_and_stamped_on_the_decision(m):
    assert refused(m.env, lambda: m.env[CRIT].with_user(m.clerk).create({"name": "X"}))
    crit = _criteria(m)
    assert "another" in _err(m.p03_action(m.compliance, CRIT, [crit.id], "action_publish"))
    _ok(m.p03_action(m.compliance2, CRIT, [crit.id], "action_publish"))
    crit.invalidate_recordset()
    assert crit.state == "active"
    assert refused(m.env, lambda: crit.with_user(m.compliance).write({"recycle_criteria": "any"}))
    col = m.collection(weight_kg=0.4)
    # under criteria in force: the functional result and a photo are required
    assert refused(m.env, lambda: m.triage(col, "recycle"))
    assert refused(m.env, lambda: m.triage(col, "recycle", functional_result="fail"))
    out = _ok(
        m.p03_write(
            m.assessor,
            TRI,
            None,
            {
                "collection_id": col.id,
                "decision": "recycle",
                "functional_result": "fail",
                "cosmetic_result": "d",
                "evidence_file": SCAN,
                "evidence_filename": "board.jpg",
            },
        )
    )
    tri = m.env[TRI].browse(out["id"])
    assert tri.criteria_id == crit and tri.evidence_attachment_id.name == "board.jpg"
    assert col.state == "triaged"
    # write-once, the evidence included (BRU-ESG-09 / T-04)
    for vals in ({"functional_result": "pass"}, {"evidence_file": SCAN}, {"notes": "later"}):
        assert refused(m.env, lambda v=vals: tri.with_user(m.assessor).write(v)), vals
    # a typed criteria version is refused
    other = _criteria(m, "TRI-OLD")
    col2 = m.collection(weight_kg=0.4)
    assert refused(
        m.env,
        lambda: m.triage(col2, "recycle", functional_result="fail", criteria_id=other.id),
    )
    # a new version retires the old one
    other.with_user(m.compliance2).action_publish()
    crit.invalidate_recordset()
    assert crit.state == "retired" and other.state == "active"


def test_reuse_and_donation_need_a_functional_low_value_device(m):
    crit = _criteria(m, evidence_required=False)
    crit.with_user(m.compliance2).action_publish()
    col = m.collection(weight_kg=0.4)
    assert refused(m.env, lambda: m.triage(col, "reuse", functional_result="partial"))
    assert refused(
        m.env,
        lambda: m.triage(col, "donate", functional_result="pass", market_value_estimate=50000),
    )
    m.triage(col, "donate", functional_result="pass", market_value_estimate=2500)
    assert col.triage_grade == "donate" and col.state == "triaged"


# ============================================================ p2 harvest
def test_harvest_routes_to_m14_only_through_the_m06_gate(m):
    dev = m.device()
    col = m.collection(device_id=dev.id, weight_kg=0.5)
    m.triage(col, "harvest", data_bearing=True)
    assert col.state == "triaged"
    assert refused(m.env, lambda: col.with_user(m.clerk).action_route_harvest())  # role
    err = _err(m.p03_action(m.assessor, COL, [col.id], "action_route_harvest"))
    assert "M06" in err
    col.with_user(m.clerk).write({"wipe_certificate_id": m.verified_cert(dev.serial_number).id})
    _ok(m.p03_action(m.assessor, COL, [col.id], "action_route_harvest"))
    col.invalidate_recordset()
    assert col.state == "routed"
    # not a write path either
    col2 = m.collection(weight_kg=0.5, material_type="accessory")
    m.triage(col2, "recycle")
    assert refused(m.env, lambda: col2.sudo()._guarded().write({"state": "routed"}))


# ============================================================ p2 donation
def test_donation_is_approved_by_another_officer_and_leaves_through_the_gate(m):
    dev = m.device()
    col = m.collection(device_id=dev.id, weight_kg=0.4)
    m.triage(col, "donate", data_bearing=True)
    recipient = m.env["res.partner"].create({"name": "M18 School"})
    # only an item triaged for donation
    other = m.collection(weight_kg=0.2)
    assert refused(
        m.env,
        lambda: m.env[DON]
        .with_user(m.clerk)
        .create({"collection_id": other.id, "recipient_id": recipient.id}),
    )
    out = _ok(
        m.p03_write(
            m.compliance,
            DON,
            None,
            {"collection_id": col.id, "recipient_id": recipient.id, "purpose": "School lab"},
        )
    )
    don = m.env[DON].browse(out["id"])
    # one live donation per item
    assert refused(
        m.env,
        lambda: m.env[DON]
        .with_user(m.clerk)
        .create({"collection_id": col.id, "recipient_id": recipient.id}),
    )
    assert "registration" in _err(m.p03_action(m.compliance2, DON, [don.id], "action_approve"))
    don.with_user(m.compliance).write({"recipient_reg_no": "NGOAB-1234"})
    assert "another" in _err(m.p03_action(m.compliance, DON, [don.id], "action_approve"))
    _ok(m.p03_action(m.compliance2, DON, [don.id], "action_approve"))
    don.invalidate_recordset()
    assert don.state == "approved"
    assert refused(
        m.env, lambda: don.with_user(m.compliance).write({"recipient_id": m.customer.id})
    )
    # hand-over needs the signed acknowledgement ...
    assert "acknowledgement" in _err(m.p03_action(m.dispatcher, DON, [don.id], "action_hand_over"))
    _ok(
        m.p03_write(
            m.clerk,
            DON,
            don.id,
            {"acknowledgement_file": SCAN, "acknowledgement_filename": "signed.pdf"},
        )
    )
    don.invalidate_recordset()
    assert don.acknowledgement_attachment_id.name == "signed.pdf"
    # ... and the M06 gate (BRU-ESG-15)
    assert "M06" in _err(m.p03_action(m.dispatcher, DON, [don.id], "action_hand_over"))
    col.with_user(m.clerk).write({"wipe_certificate_id": m.verified_cert(dev.serial_number).id})
    assert refused(m.env, lambda: don.with_user(m.clerk).action_hand_over())  # role
    _ok(m.p03_action(m.dispatcher, DON, [don.id], "action_hand_over"))
    col.invalidate_recordset()
    don.invalidate_recordset()
    assert col.state == "donated" and don.state == "handed_over"
    assert refused(m.env, lambda: col.sudo()._guarded().write({"state": "triaged"}))


# ============================================================ p4 downstream
def test_recycler_qualified_only_with_declared_downstream(m):
    from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox

    # A05 S3 M18-22 / M18-06: registered by the floor, with its business contact
    p = (
        m.env["fix.ewaste.partner"]
        .with_user(m.dispatcher)
        .create(
            {
                "name": "No Downstream Recycler",
                "certificate_no": "DOE-ND-1",
                "valid_from": m.today - timedelta(days=1),
                "valid_to": m.today + timedelta(days=200),
                "licence_attachment_id": attachment(m.env, "lic.pdf").id,
                "partner_id": m.env["res.partner"].create({"name": "ND Recycler Ltd"}).id,
            }
        )
    )
    err = refused(m.env, lambda: approve_via_inbox(p, m.approver, requester=m.dispatcher))
    assert err and "BRU-ESG-18" in str(err)


def test_dispatch_needs_a_current_verified_downstream_for_its_material(m):
    p = m.partner()
    from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox

    approve_via_inbox(p, m.approver, requester=m.dispatcher)
    item = m.ready_item()
    batch = m.batch(partner=p)
    batch.action_load_ready_items()
    m.weigh_out(batch)  # A05 S3 M18-16: the outbound weighbridge ticket first
    # declared but not verified
    assert "BRU-ESG-18" in str(refused(m.env, lambda: batch.action_dispatch()))
    down = p.downstream_ids
    # the declarer does not verify it; nor does a non-approver
    assert refused(m.env, lambda: down.with_user(m.clerk).action_verify())
    approver2 = make_user(m.env, "approver2", [G.recycler_approver])
    # ... even when the declarer holds the approver role (four eyes)
    own = m.downstream(p, material="laptop", user=approver2)
    err = _err(m.p03_action(approver2, DOWN, [own.id], "action_verify"))
    assert "another approver" in err
    _ok(m.p03_action(m.approver, DOWN, [down.id], "action_verify"))
    down.invalidate_recordset()
    assert down.state == "verified" and down.verified_by_id == m.approver
    # a stale verification no longer counts
    m.env["ir.config_parameter"].sudo().set_param("cd_ewaste.downstream_verification_days", "0")
    down.sudo()._guarded().write({"verified_on": m.today - timedelta(days=1)})
    assert refused(m.env, lambda: batch.action_dispatch())
    m.env["ir.config_parameter"].sudo().set_param("cd_ewaste.downstream_verification_days", "365")
    down.with_user(approver2).action_verify()  # the annual re-verification
    # a destination for another material only does not count either
    down.sudo()._guarded().write({"material_class": "laptop"})
    assert refused(m.env, lambda: batch.action_dispatch())
    down.sudo()._guarded().write({"material_class": "phone"})
    batch.action_dispatch()
    assert batch.state == "dispatched" and item.batch_id == batch
    # a verified destination is frozen
    assert refused(
        m.env, lambda: down.with_user(m.clerk).write({"country_id": m.env.ref("base.in").id})
    )


# ============================================================ p5 exceptions
def _two_item_batch(m):
    i1, i2 = m.ready_item(weight=0.5), m.ready_item(weight=0.25)
    return m.processed_batch([i1, i2]), i1, i2


def test_item_missing_from_the_certificate_opens_an_exception_until_covered(m):
    batch, i1, i2 = _two_item_batch(m)
    batch.action_record_certificate()
    cert = batch.certificate_ids
    _ok(
        m.p03_write(
            m.dispatcher,
            "fix.ewaste.certificate",
            cert.id,
            {
                "certificate_no": "REC-PART-1",
                "uncovered_collection_ids": [i2.id],
                # a partial certificate states the weight of what it covers
                "recycler_stated_weight_kg": batch.processed_weight_kg,
                "evidence_file": SCAN,
                "evidence_filename": "partial.pdf",
            },
        )
    )
    assert "item(s) it covers" in str(
        refused(m.env, lambda: cert.with_user(m.compliance).action_issue())
    )
    cert.with_user(m.dispatcher).write({"recycler_stated_weight_kg": 0.5})
    cert.with_user(m.compliance).action_issue()
    assert i1.state == "certified" and i2.state == "recycled"
    exc = m.env[EXC].search([("collection_id", "=", i2.id)])
    assert exc.state == "open" and exc.certificate_id == cert and exc.batch_id == batch
    # never typed; never silently closed
    assert refused(
        m.env,
        lambda: m.env[EXC]
        .with_user(m.compliance)
        .create({"batch_id": batch.id, "collection_id": i1.id, "company_id": m.env.company.id}),
    )
    assert refused(m.env, lambda: exc.with_user(m.compliance).write({"state": "closed"}))
    # a supplementary certificate is recorded for the batch and covers it
    _ok(m.p03_action(m.dispatcher, "fix.ewaste.batch", [batch.id], "action_record_certificate"))
    sup = batch.certificate_ids.filtered(lambda x: x.state == "draft")
    sup.with_user(m.dispatcher).write(
        {
            "certificate_no": "REC-SUP-1",
            "recycler_stated_weight_kg": 0.25,
            "evidence_attachment_id": attachment(m.env, "sup.pdf").id,
        }
    )
    sup.with_user(m.compliance2).action_issue()
    exc.invalidate_recordset()
    assert (
        i2.state == "certified" and exc.state == "resolved" and exc.resolved_certificate_id == sup
    )
    # everything certified: no third certificate
    assert refused(m.env, lambda: batch.action_record_certificate())


def test_exception_closed_on_a_finding_by_another_officer(m):
    batch, i1, i2 = _two_item_batch(m)
    batch.action_record_certificate()
    cert = batch.certificate_ids
    cert.with_user(m.dispatcher).write(
        {
            "certificate_no": "REC-PART-2",
            "uncovered_collection_ids": [(6, 0, [i2.id])],
            "recycler_stated_weight_kg": 0.5,
            "evidence_attachment_id": attachment(m.env, "c.pdf").id,
        }
    )
    cert.with_user(m.compliance).action_issue()
    exc = m.env[EXC].search([("collection_id", "=", i2.id), ("state", "=", "open")])
    assert "finding" in _err(m.p03_action(m.compliance2, EXC, [exc.id], "action_close"))
    # the certificate's issuer does not close its exception
    assert "another" in _err(
        m.p03_action(m.compliance, EXC, [exc.id], "action_close", {"finding": "Shredded on site"})
    )
    _ok(
        m.p03_action(
            m.compliance2, EXC, [exc.id], "action_close", {"finding": "Recycler audit: shredded"}
        )
    )
    exc.invalidate_recordset()
    assert exc.state == "closed" and exc.finding and exc.closed_by_id == m.compliance2
    assert refused(m.env, lambda: exc.with_user(m.compliance).write({"finding": "rewrite"}))


def test_full_certificate_still_covers_every_item(m):
    """The 13 Nov path is unchanged when nothing is left out."""
    batch, i1, i2 = _two_item_batch(m)
    cert = m.issued_certificate(batch)
    assert {i1.state, i2.state} == {"certified"} and not cert.exception_ids


# ============================================================ p5 recovery
def test_material_recovery_raised_as_batch_income_with_sod(m):
    batch = m.processed_batch([m.ready_item(weight=1.0)])
    contact = m.env["res.partner"].create({"name": "M18 Recycler Ltd"})
    batch.partner_id.sudo()._guarded().write({"partner_id": contact.id})
    # A05 S3 FIN-11: the income posts on the batch's operating unit (the
    # settlement takes it when raised), never the company's first unit
    ou = m.env["operating.unit"].search([("company_id", "=", m.env.company.id)], limit=1)
    batch.sudo()._guarded().write({"operating_unit_id": ou.id})
    dual = make_user(m.env, "dispfin", [G.dispatcher, G.finance])
    assert refused(
        m.env,
        lambda: m.env[REC]
        .with_user(m.clerk)
        .create({"batch_id": batch.id, "material_class": "pcb", "weight_kg": 0.1}),
    )
    out = _ok(
        m.p03_write(
            dual,
            REC,
            None,
            {"batch_id": batch.id, "material_class": "pcb", "weight_kg": 0.2, "agreed_rate": 900},
        )
    )
    pcb = m.env[REC].browse(out["id"])
    assert pcb.income_amount == pytest.approx(180.0) and pcb.company_id == batch.company_id
    # T-05: never more than the batch processed
    assert refused(
        m.env,
        lambda: m.env[REC]
        .with_user(m.dispatcher)
        .create({"batch_id": batch.id, "material_class": "ferrous", "weight_kg": 5.0}),
    )
    # one line per class
    assert refused(
        m.env,
        lambda: m.env[REC]
        .with_user(m.dispatcher)
        .create({"batch_id": batch.id, "material_class": "pcb", "weight_kg": 0.1}),
    )
    # only a processed batch
    draft = m.batch()
    assert refused(
        m.env,
        lambda: m.env[REC]
        .with_user(m.dispatcher)
        .create({"batch_id": draft.id, "material_class": "glass", "weight_kg": 0.1}),
    )
    _ok(m.p03_action(dual, REC, [pcb.id], "action_raise_income"))
    pcb.invalidate_recordset()
    st = pcb.settlement_id
    assert pcb.state == "raised" and st.kind == "recovery_income" and st.batch_id == batch
    assert st.amount == pytest.approx(180.0) and st.partner_id == contact
    assert refused(m.env, lambda: pcb.with_user(m.dispatcher).write({"weight_kg": 0.3}))
    # BRU-ESG-19 / §13: the recorder does not approve the income
    err = refused(m.env, lambda: st.with_user(dual).action_approve_settlement())
    assert err and "recorded the material recovery" in str(err)
    from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox

    # A05 S3 I2: and on the settlement's branch (in that unit)
    entity = m.env["fix.entity"].search([("company_id", "=", m.env.company.id)], limit=1) or m.env[
        "fix.entity"
    ].create({"code": "M18P2E", "legal_name": "M18 P2 Entity", "company_id": m.env.company.id})
    branch = m.env["fix.branch"].create(
        {
            "name": "M18 P2 Branch",
            "code": "M18P2B",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    st.with_user(m.dispatcher).write({"branch_id": branch.id})
    approve_via_inbox(st, m.cfo, requester=m.dispatcher)
    assert st.state == "approved"


# ============================================================ p9 factors
def test_factor_set_activated_by_another_officer_drives_the_figures(m):
    out = _ok(
        m.p03_write(
            m.compliance,
            FAC,
            None,
            {
                "name": "EPA-WARM-16",
                "co2_avoided_per_kg": 2.2,
                "source": "US EPA WARM v16",
                "evidence_file": SCAN,
                "evidence_filename": "warm16.pdf",
            },
        )
    )
    fs = m.env[FAC].browse(out["id"])
    assert refused(
        m.env, lambda: m.env[FAC].with_user(m.clerk).create({"name": "x", "co2_avoided_per_kg": 1})
    )
    assert "another" in _err(m.p03_action(m.compliance, FAC, [fs.id], "action_activate"))
    _ok(m.p03_action(m.compliance2, FAC, [fs.id], "action_activate"))
    fs.invalidate_recordset()
    assert fs.state == "active"
    assert c.co2_factor(m.env, m.env.company) == (2.2, "EPA-WARM-16")
    assert refused(m.env, lambda: fs.with_user(m.compliance).write({"co2_avoided_per_kg": 9.9}))
    item = m.ready_item(weight=2.0)
    assert item.esg_co2_saved_kg == pytest.approx(4.4) and item.co2_factor_version == "EPA-WARM-16"
    # a new version retires the old; the figure computed before keeps its version
    fs2 = (
        m.env[FAC]
        .with_user(m.compliance2)
        .create(
            {
                "name": "EPA-WARM-17",
                "co2_avoided_per_kg": 2.0,
                "source": "US EPA WARM v17",
                "evidence_attachment_id": attachment(m.env, "w17.pdf").id,
            }
        )
    )
    fs2.with_user(m.compliance).action_activate()
    fs.invalidate_recordset()
    assert fs.state == "retired" and item.co2_factor_version == "EPA-WARM-16"
    # the figures themselves still have no entry path (BRU-ESG-11)
    assert refused(
        m.env,
        lambda: m.env["fix.esg.metric"]
        .with_user(m.compliance)
        .create({"name": "x", "period": "2026-11", "value": 1.0}),
    )


# ============================================================ p10 register
def test_obligation_reviewed_at_least_quarterly(m):
    assert refused(
        m.env,
        lambda: m.env[OBL]
        .with_user(m.clerk)
        .create({"name": "x", "citation": "r.5", "obligation_text": "x"}),
    )
    out = _ok(
        m.p03_write(
            m.compliance,
            OBL,
            None,
            {
                "name": "Register as repairer with DoE",
                "instrument": "ewaste_rules_2021",
                "citation": "Rule 6",
                "obligation_text": "Hold a DoE registration and an approved e-waste plan.",
                "frequency": "annual",
            },
        )
    )
    obl = m.env[OBL].browse(out["id"])
    assert "owner" in _err(m.p03_action(m.compliance, OBL, [obl.id], "action_activate"))
    obl.with_user(m.compliance).write({"owner_id": m.compliance.id, "evidence_source": "DoE file"})
    _ok(m.p03_action(m.compliance, OBL, [obl.id], "action_activate"))
    obl.invalidate_recordset()
    # an annual duty is still reviewed at least quarterly (BRU-ESG-16)
    assert obl.state == "active" and obl.next_review <= m.today + timedelta(days=92)
    assert refused(m.env, lambda: obl.with_user(m.compliance).write({"citation": "Rule 7"}))
    assert refused(
        m.env, lambda: obl.with_user(m.compliance).write({"compliance_status": "compliant"})
    )
    assert "finding" in _err(m.p03_action(m.compliance, OBL, [obl.id], "action_review"))
    _ok(
        m.p03_action(
            m.compliance2,
            OBL,
            [obl.id],
            "action_review",
            {"review_status": "partial", "review_note": "Plan submitted, approval pending"},
        )
    )
    obl.invalidate_recordset()
    assert obl.compliance_status == "partial" and obl.last_reviewed == m.today
    assert obl.last_reviewed_by_id == m.compliance2 and not obl.review_note
    # AUT-ESG-19: an overdue review is flagged. The review date is the
    # workflow's (A05 S3: never typed); the clock passing it is simulated
    assert refused(
        m.env,
        lambda: obl.with_user(m.compliance).write({"next_review": m.today - timedelta(days=1)}),
    )
    obl.sudo()._guarded().write({"next_review": m.today - timedelta(days=1)})
    assert obl.review_overdue
    assert m.env[OBL].cron_review_due() >= 1
    assert obl.message_ids.filtered(
        lambda x: "overdue" in (x.body or "").lower() or "due for review" in (x.body or "")
    )
