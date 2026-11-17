# M59 capture audit (2026-11-18): the six registers built so every sub-module
# page captures what it covers - safe work procedure (FR-HSE-006), permit to
# work (FR-HSE-007), witness statement (FR-HSE-012, T-09), right to stop work
# (FR-HSE-026, BRU-HSE-10), customer premises hazard (FR-HSE-025, AUT-HSE-17)
# and site emergency plan (FR-HSE-035).
#
# Same standard as test_a09_hse_controls.py, whose cast this file reuses:
# every attempt runs as a freshly created NON-admin user, and workspace saves
# go through the real /p03/model/write endpoint.
import types
from datetime import timedelta
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_hse.tests.test_a09_hse_controls import (
    REFUSED,
    FakeRequest,
    _report,
    _rpc_write,
    _user,
    make_x,
)
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.exceptions import AccessError, UserError, ValidationError


@pytest.fixture
def x(odoo_env):
    return make_x(odoo_env)


@pytest.fixture
def call():
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


def _todos(env, rec, summary_start):
    return (
        env["mail.activity"]
        .sudo()
        .search(
            [
                ("res_model", "=", rec._name),
                ("res_id", "=", rec.id),
                ("summary", "=like", summary_start + "%"),
            ]
        )
    )


# ============================================================ safe work procedure
def _procedure(x, user=None, code="SWP-ELEC-01", **vals):
    base = {
        "code": code,
        "name": "Isolate the mains before opening a split AC",
        "category": "electrical",
        "scope": "Field AC repair",
        "content": "1. Switch off. 2. Lock out. 3. Test dead.",
    }
    base.update(vals)
    return x.env(user=(user or x.hse).id)["fix.hse.procedure"].create(base)


def test_a_procedure_is_approved_by_another_officer_and_then_frozen(x):
    with pytest.raises(AccessError):
        _procedure(x, user=x.plain)
    proc = _procedure(x)
    # a plain employee does not read a draft
    assert not x.env(user=x.plain.id)["fix.hse.procedure"].search([("id", "=", proc.id)])
    proc.with_user(x.hse).action_submit()
    with pytest.raises(UserError, match="another HSE Officer"):
        proc.with_user(x.hse).action_approve()
    with pytest.raises(AccessError):
        proc.with_user(x.plain).action_approve()
    proc.with_user(x.hse2).action_approve()
    assert proc.state == "approved" and proc.approved_by_id == x.hse2
    assert proc.effective_from and proc.review_due_on
    # published: every employee reads it; nobody rewrites it
    assert x.env(user=x.plain.id)["fix.hse.procedure"].search([("id", "=", proc.id)])
    with pytest.raises(UserError, match="new version"):
        _rpc_write(x.env, x.hse2, proc, {"content": "Skip the lock-out"})
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.hse2, proc, {"state": "draft"})
    with pytest.raises(UserError):
        proc.with_user(x.hse).unlink()


def test_a_new_version_supersedes_the_one_in_force(x):
    v1 = _procedure(x)
    v1.with_user(x.hse).action_submit()
    v1.with_user(x.hse2).action_approve()
    res = v1.with_user(x.hse2).action_revise()
    v2 = x.env["fix.hse.procedure"].browse(res["ids"])
    assert v2.version == 2 and v2.state == "draft" and v2.previous_id == v1
    v2.with_user(x.hse2).write({"content": "1. Switch off. 2. Lock out. 3. Test dead. 4. Earth."})
    v2.with_user(x.hse2).action_submit()
    with pytest.raises(UserError, match="Say what must change"):
        v2.with_user(x.hse).action_reject(reason=" ")
    v2.with_user(x.hse).action_approve()
    assert v1.state == "superseded" and v2.state == "approved"


def test_a_procedure_needs_scope_and_steps_to_submit(x):
    proc = _procedure(x, content=False)
    with pytest.raises(UserError, match="scope and its steps"):
        proc.with_user(x.hse).action_submit()


# ================================================================ permit to work
def _permit(x, user=None, **vals):
    now = fields.Datetime.now()
    base = {
        "permit_type": "hot_work",
        "activity": "Rework a burnt power board",
        "location": "Workshop bench 3",
        "precautions": "Fume extractor on; fire blanket at the bench",
        "valid_from": now,
        "valid_to": now + timedelta(hours=4),
    }
    base.update(vals)
    return x.env(user=(user or x.plain).id)["fix.hse.permit"].create(base)


def test_a_permit_is_authorised_by_an_officer_who_neither_asked_nor_works(x):
    permit = _permit(x)
    assert permit.performer_id == x.plain.employee_id and permit.name.startswith("PTW/")
    permit.with_user(x.plain).action_request()
    assert _todos(x.env, permit, "Permit to authorise")
    # HSE raising a permit for themselves cannot authorise it either
    own = _permit(x, user=x.hse)
    own.with_user(x.hse).action_request()
    with pytest.raises(UserError, match="another HSE Officer"):
        own.with_user(x.hse).action_authorise()
    with pytest.raises(AccessError):
        permit.with_user(x.colleague).action_authorise()
    permit.with_user(x.hse).action_authorise(note="Extinguisher within 2 m")
    assert permit.state == "authorised" and permit.authorised_by_id == x.hse
    # its terms are fixed once requested
    with pytest.raises(UserError, match="terms are fixed"):
        _rpc_write(x.env, x.plain, permit, {"location": "Roof"})
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.plain, permit, {"state": "closed"})
    with pytest.raises(UserError, match="area was left"):
        permit.with_user(x.plain).action_close(note="")
    permit.with_user(x.plain).action_close(note="Iron off, bench cleared")
    assert permit.state == "closed" and permit.closed_by_id == x.plain


def test_a_permit_is_requested_for_your_own_work_with_its_controls(x):
    with pytest.raises(AccessError, match="work you do yourself"):
        _permit(x, performer_id=x.colleague.employee_id.id)
    # HSE may raise one for a technician
    assert _permit(x, user=x.hse, performer_id=x.plain.employee_id.id)
    with pytest.raises(ValidationError, match="at most"):
        _permit(x, valid_to=fields.Datetime.now() + timedelta(hours=30))
    bare = _permit(x, precautions=False)
    with pytest.raises(UserError, match="precautions"):
        bare.with_user(x.plain).action_request()
    elec = _permit(x, permit_type="electrical")
    with pytest.raises(UserError, match="isolation points"):
        elec.with_user(x.plain).action_request()
    # a colleague neither sees nor touches it
    assert not x.env(user=x.colleague.id)["fix.hse.permit"].search([("id", "=", bare.id)])


def test_a_permit_names_only_an_approved_jsa_or_procedure(x):
    draft = _procedure(x)
    with pytest.raises(ValidationError, match="in force"):
        _permit(x, procedure_id=draft.id)


def test_an_authorised_permit_past_its_window_expires_and_hse_is_told(x):
    permit = _permit(x)
    permit.with_user(x.plain).action_request()
    permit.with_user(x.hse).action_authorise()
    # setup only: the window passes
    permit.sudo().write(
        {
            "valid_from": fields.Datetime.now() - timedelta(hours=6),
            "valid_to": fields.Datetime.now() - timedelta(hours=1),
        }
    )
    assert x.env["fix.hse.permit"].cron_expire_permits() >= 1
    assert permit.state == "expired"
    assert _todos(x.env, permit, "Permit expired without closure")
    assert x.env["fix.hse.permit"].cron_expire_permits() == 0 or permit.state == "expired"
    permit.with_user(x.plain).action_close(note="Area checked safe next morning")
    assert permit.state == "closed"


# ============================================================ witness statement
def test_a_witness_statement_is_taken_by_hse_and_kept_verbatim(x):
    inc = _report(x, x.plain)
    Wit = x.env(user=x.hse.id)["fix.hse.witness.statement"]
    with pytest.raises(AccessError):
        x.env(user=x.plain.id)["fix.hse.witness.statement"].create(
            {"incident_id": inc.id, "witness_name": "Me", "statement": "x"}
        )
    with pytest.raises(ValidationError, match="Name the witness"):
        Wit.create({"incident_id": inc.id, "statement": "I saw it"})
    st = Wit.create(
        {
            "incident_id": inc.id,
            "witness_employee_id": x.colleague.employee_id.id,
            "statement": "The iron was left on the mat.",
        }
    )
    assert st.taken_by_id == x.hse and st.name.startswith("WIT/")
    with pytest.raises(UserError, match="as given"):
        _rpc_write(x.env, x.hse2, st, {"statement": "The iron was in its stand."})
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.hse2, st, {"taken_on": fields.Datetime.now() - timedelta(days=9)})
    with pytest.raises(UserError, match="never deleted"):
        st.with_user(x.hse).unlink()
    # a plain employee never reads another's account
    assert not x.env(user=x.plain.id)["fix.hse.witness.statement"].check_access_rights(
        "read", raise_exception=False
    )


def test_no_statement_is_added_to_a_closed_incident(x):
    inc = _report(x, x.plain, incident_type="near_miss")
    # setup only: the superuser closes it
    inc.sudo()._guarded().write({"state": "closed"})
    with pytest.raises(UserError, match="closed incident"):
        x.env(user=x.hse.id)["fix.hse.witness.statement"].create(
            {"incident_id": inc.id, "witness_name": "Visitor", "statement": "late account"}
        )


# =============================================================== work refusal
def _refusal(x, user=None, **vals):
    base = {"ground": "electrical", "detail": "Customer DB board sparking; no isolator"}
    base.update(vals)
    return x.env(user=(user or x.plain).id)["fix.hse.work.refusal"].create(base)


def test_a_technician_records_a_refusal_and_hse_and_the_manager_are_told(x):
    # the plain user reports to a line manager
    manager = _user(x.env)
    x.plain.employee_id.sudo().write({"parent_id": manager.employee_id.id})
    ref = _refusal(x)
    assert ref.employee_id == x.plain.employee_id and ref.recorded_by_id == x.plain
    users = _todos(x.env, ref, "Work refused").mapped("user_id")
    assert x.hse in users and x.hse2 in users and manager in users and x.plain not in users
    # the manager reads it; a colleague does not
    assert x.env(user=manager.id)["fix.hse.work.refusal"].search([("id", "=", ref.id)])
    assert not x.env(user=x.colleague.id)["fix.hse.work.refusal"].search([("id", "=", ref.id)])
    with pytest.raises(AccessError, match="own refusal"):
        _refusal(x, employee_id=x.colleague.employee_id.id)


def test_a_refusal_is_reviewed_by_another_officer_and_never_rewritten(x):
    ref = _refusal(x)
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.plain, ref, {"outcome": "not_substantiated"})
    with pytest.raises(UserError, match="recorded as given"):
        _rpc_write(x.env, x.plain, ref, {"detail": "It was fine actually"})
    with pytest.raises(AccessError):
        ref.with_user(x.plain).action_not_substantiated(note="self-cleared")
    # an HSE Officer who recorded it for the technician does not review it
    for_them = _refusal(x, user=x.hse, employee_id=x.colleague.employee_id.id)
    with pytest.raises(UserError, match="another HSE Officer"):
        for_them.with_user(x.hse).action_uphold(note="agree")
    with pytest.raises(UserError, match="what the review found"):
        ref.with_user(x.hse).action_uphold(note="")
    ref.with_user(x.hse).action_uphold(note="Board unsafe; electrician sent")
    assert ref.state == "reviewed" and ref.outcome == "upheld" and ref.reviewed_by_id == x.hse
    with pytest.raises(UserError, match="has been reviewed"):
        ref.with_user(x.hse2).action_not_substantiated(note="second opinion")
    with pytest.raises(UserError, match="never deleted"):
        ref.with_user(x.hse).unlink()
    assert "penalty" not in " ".join(ref._fields)


def test_a_refusal_through_the_workspace_form(x, call):
    res = call(
        x.env(user=x.plain.id),
        "model_write",
        model="fix.hse.work.refusal",
        values={"ground": "height", "detail": "No anchor point on the roof"},
    )
    assert res.get("id"), res
    ref = x.env["fix.hse.work.refusal"].browse(res["id"])
    assert ref.employee_id == x.plain.employee_id and ref.state == "recorded"
    forged = call(
        x.env(user=x.plain.id),
        "model_write",
        model="fix.hse.work.refusal",
        values={"ground": "height", "detail": "again", "outcome": "upheld"},
    )
    created = x.env["fix.hse.work.refusal"].browse(forged.get("id") or 0).exists()
    assert not created or not created.outcome


# =========================================================== customer site hazard
@pytest.fixture
def fs(x):
    env = x.env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    zone = env["fix.zone"].create({"name": "M59 Capture Zone", "code": "M59CZ"})
    x.branch.write({"zone_id": zone.id})
    brand = env["fix.brand"].create({"name": "M59CapBrand", "code": "M59CB"})
    model = env["fix.device.model"].create({"name": "M59 AC", "brand_id": brand.id})
    customer = env["res.partner"].create(
        {"name": "M59 Site Customer", "phone": "01711000951", "street": "12 Lake Road"}
    )
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-M59C-1"}
    )

    def order():
        so = env["fix.service.order"].create(
            {
                "device_id": device.id,
                "customer_id": customer.id,
                "branch_id": x.branch.id,
                "fault_description": "onsite AC",
                "service_type": "onsite",
            }
        )
        return env["fix.field.order"].create(
            {"order_id": so.id, "zone_id": zone.id, "operating_unit_id": ou.id}
        )

    return types.SimpleNamespace(customer=customer, order=order)


def test_a_site_hazard_reaches_every_field_order_for_that_customer(x, fs):
    first = fs.order()
    hz = x.env(user=x.plain.id)["fix.hse.location.hazard"].create(
        {
            "partner_id": fs.customer.id,
            "hazard_type": "animal",
            "description": "Unchained dog at the gate",
            "field_order_id": first.id,
        }
    )
    assert hz.state == "reported" and hz.reported_by_id == x.plain.employee_id
    assert "12 Lake Road" in (hz.address or "")
    assert _todos(x.env, hz, "Customer site hazard to confirm")
    # the next visit to the same customer shows it, to the technician too
    nxt = fs.order()
    assert hz in nxt.hse_site_hazard_ids and "Unchained dog" in nxt.hse_site_hazard_note
    assert x.env(user=x.colleague.id)["fix.hse.location.hazard"].search([("id", "=", hz.id)])
    # the reporter may add the precautions while it is reported; a colleague may not
    hz.with_user(x.plain).write({"precautions": "Phone ahead; customer ties the dog"})
    with pytest.raises(REFUSED):
        _rpc_write(x.env, x.colleague, hz, {"precautions": "ignore"})
    with pytest.raises(UserError, match="reported as found"):
        _rpc_write(x.env, x.plain, hz, {"description": "small dog"})
    with pytest.raises(AccessError):
        hz.with_user(x.plain).action_confirm()
    hz.with_user(x.hse).action_confirm()
    assert hz.state == "confirmed" and hz.confirmed_by_id == x.hse
    with pytest.raises(UserError, match="Say why"):
        hz.with_user(x.hse).action_retire(reason="")
    hz.with_user(x.hse).action_retire(reason="Customer moved")
    nxt.invalidate_recordset()
    assert hz not in nxt.hse_site_hazard_ids and not nxt.hse_site_hazard_note
    with pytest.raises(UserError, match="never deleted"):
        hz.with_user(x.hse).unlink()


def test_confirming_a_site_hazard_needs_its_precautions(x, fs):
    hz = x.env(user=x.plain.id)["fix.hse.location.hazard"].create(
        {"partner_id": fs.customer.id, "hazard_type": "electrical", "description": "Bare wires"}
    )
    with pytest.raises(UserError, match="precautions"):
        hz.with_user(x.hse).action_confirm()


# ============================================================ site emergency plan
def _plan(x, user=None, **vals):
    base = {
        "name": "Depot emergency plan",
        "branch_id": x.branch.id,
        "evacuation_procedure": "Leave by the rear stair; do not use the lift",
        "assembly_point": "Car park, north gate",
        "warden_ids": [(6, 0, [x.colleague.employee_id.id])],
        "first_aider_ids": [(6, 0, [x.plain.employee_id.id])],
        "fire_extinguishers": 4,
        "first_aid_boxes": 2,
        "extinguisher_service_due": x.today + timedelta(days=120),
    }
    base.update(vals)
    return x.env(user=(user or x.hse).id)["fix.hse.emergency.plan"].create(base)


def test_a_plan_is_put_in_force_by_another_officer_with_its_people(x):
    with pytest.raises(AccessError):
        _plan(x, user=x.plain)
    thin = _plan(x, warden_ids=[(5, 0, 0)], first_aid_boxes=0)
    with pytest.raises(UserError, match="a fire warden.*first-aid boxes"):
        thin.with_user(x.hse2).action_approve()
    plan = _plan(x)
    with pytest.raises(UserError, match="another HSE Officer"):
        plan.with_user(x.hse).action_approve()
    plan.with_user(x.hse2).action_approve()
    assert plan.state == "in_force" and plan.next_review_date and plan.approved_by_id == x.hse2
    # everyone reads it; nobody rewrites it
    assert x.env(user=x.plain.id)["fix.hse.emergency.plan"].search([("id", "=", plan.id)])
    with pytest.raises(UserError, match="revise it"):
        _rpc_write(x.env, x.hse, plan, {"assembly_point": "Front road"})
    with pytest.raises(AccessError):
        _rpc_write(x.env, x.plain, plan, {"name": "mine"})
    # a new version put in force supersedes the old one for the site
    v2 = x.env["fix.hse.emergency.plan"].browse(plan.with_user(x.hse).action_revise()["ids"])
    assert v2.version == 2 and v2.warden_ids == plan.warden_ids
    v2.with_user(x.hse2).action_approve()
    assert plan.state == "superseded" and v2.state == "in_force"


def test_an_overdue_plan_review_is_flagged_once(x):
    plan = _plan(x)
    plan.with_user(x.hse2).action_approve()
    # setup only: the review date passes
    plan.sudo()._guarded().write({"next_review_date": x.today - timedelta(days=1)})
    Plan = x.env["fix.hse.emergency.plan"]
    assert Plan.cron_flag_plan_reviews() >= 1 and plan.review_due
    assert _todos(x.env, plan, "Emergency plan review due")
    assert plan not in Plan.sudo().search([("review_due", "=", False), ("id", "=", plan.id)])
    before = len(_todos(x.env, plan, "Emergency plan review due"))
    Plan.cron_flag_plan_reviews()
    assert len(_todos(x.env, plan, "Emergency plan review due")) == before
    plan.with_user(x.hse).action_review()
    assert not plan.review_due and plan.next_review_date > x.today


# ======================================================= driving licence capture
def test_an_hse_officer_records_the_driving_licence_a_road_check_needs(x, call):
    res = call(
        x.env(user=x.hse.id),
        "model_write",
        model="fix.driver",
        values={
            "name": x.plain.name,
            "employee_id": x.plain.employee_id.id,
            "license_no": "DK-M59-1",
            "license_class": "Light Motor Vehicle",
            "license_expiry": str(x.today + timedelta(days=200)),
        },
    )
    assert res.get("id"), res
    check = x.env(user=x.plain.id)["fix.hse.roadcheck"].create({"vehicle_ref": "DHA-M59"})
    assert check.licence_number == "DK-M59-1"
