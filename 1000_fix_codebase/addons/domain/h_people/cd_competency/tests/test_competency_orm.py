# cd_competency live-ORM tests — P08-M05 (CD-M22-01), FR-LMS-039.
import json
from datetime import timedelta
from types import SimpleNamespace

import pytest
from odoo import fields
from odoo.exceptions import UserError


def _events(env, event_type, aggregate_id):
    rows = env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)], order="id"
    )
    return [json.loads(r.payload) for r in rows]


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    Competency = env["fix.competency"]
    return SimpleNamespace(
        env=env,
        today=fields.Date.today(),
        phone=Competency.create(
            {"code": "SP-L2", "name": "Smartphone L2", "device_type": "smartphone,tablet"}
        ),
        laptop=Competency.create({"code": "LT-L2", "name": "Laptop L2", "device_type": "laptop"}),
        safety=Competency.create({"code": "ESD", "name": "ESD Safety"}),  # gating, unscoped
        soft=Competency.create(
            {"code": "CX", "name": "Customer Care", "required_for_dispatch": False}
        ),
        tech=env["hr.employee"].create({"name": "Tech Mamun"}),
    )


def _cert(ctx, competency, employee=None, **vals):
    return ctx.env["fix.certification"].create(
        {
            "employee_id": (employee or ctx.tech).id,
            "competency_id": competency.id,
            **vals,
        }
    )


# --- the certification register --------------------------------------------------


def test_expiry_status(ctx):
    t = ctx.today
    assert _cert(ctx, ctx.phone).status == "active"  # non-expiring
    assert _cert(ctx, ctx.phone, expires_on=t - timedelta(days=1)).status == "expired"
    assert _cert(ctx, ctx.phone, expires_on=t + timedelta(days=30)).status == "expiring"
    assert _cert(ctx, ctx.phone, expires_on=t + timedelta(days=31)).status == "active"


def test_grant_publishes(ctx):
    cert = _cert(ctx, ctx.phone)
    cert.action_grant()
    assert _events(ctx.env, "certification.granted", cert.id) == [
        {"employee": "Tech Mamun", "competency": "SP-L2"}
    ]


def _make_stale_active(ctx, cert):
    """A status computed while still valid: expiry has since passed."""
    ctx.env.flush_all()
    ctx.env.cr.execute("UPDATE fix_certification SET status = 'active' WHERE id = %s", [cert.id])
    ctx.env.invalidate_all()
    assert cert.status == "active"


def test_expiry_sweep_refreshes_stale_status(ctx):
    lapsed = _cert(ctx, ctx.phone, expires_on=ctx.today - timedelta(days=3))
    _make_stale_active(ctx, lapsed)
    valid = _cert(ctx, ctx.laptop, expires_on=ctx.today + timedelta(days=90))
    (lapsed | valid).action_mark_expired()
    assert (lapsed.status, valid.status) == ("expired", "active")
    assert _events(ctx.env, "certification.expired", lapsed.id) == [
        {"employee": "Tech Mamun", "competency": "SP-L2"}
    ]
    assert _events(ctx.env, "certification.expired", valid.id) == []


# --- FR-LMS-039 dispatch eligibility ------------------------------------------------


def test_no_technician(ctx):
    assert ctx.env["fix.certification"].dispatch_eligibility(ctx.env["hr.employee"]) == (
        False,
        "no technician assigned",
    )


def test_uncertified_technician(ctx):
    Cert = ctx.env["fix.certification"]
    _cert(ctx, ctx.soft)  # a developmental competency does not gate dispatch
    assert Cert.dispatch_eligibility(ctx.tech) == (
        False,
        "FR-LMS-039: Tech Mamun holds no dispatch-gating certification",
    )
    assert Cert.dispatch_eligibility(ctx.tech, device_type="smartphone") == (
        False,
        "FR-LMS-039: Tech Mamun holds no ACTIVE certification for smartphone",
    )


def test_device_scoped_eligibility(ctx):
    Cert = ctx.env["fix.certification"]
    _cert(ctx, ctx.laptop)
    assert Cert.dispatch_eligibility(ctx.tech, device_type="laptop") == (
        True,
        "certified for laptop",
    )
    # holds laptop only: a tablet job is refused
    assert Cert.dispatch_eligibility(ctx.tech, device_type="tablet")[0] is False
    # no competency is scoped to this device type: any gating certification will do
    gating = ctx.env["fix.competency"].search([("required_for_dispatch", "=", True)])
    assert not any("projector" in (c.device_type or "") for c in gating)
    assert Cert.dispatch_eligibility(ctx.tech, device_type="projector") == (
        True,
        "holds dispatch-gating certification",
    )
    assert Cert.dispatch_eligibility(ctx.tech) == (True, "holds dispatch-gating certification")


def test_two_certifications_do_not_crash(ctx):
    """Regression: `{certs.competency_id.id}` raised Expected singleton."""
    _cert(ctx, ctx.laptop)
    _cert(ctx, ctx.phone)
    Cert = ctx.env["fix.certification"]
    assert Cert.dispatch_eligibility(ctx.tech, device_type="tablet") == (
        True,
        "certified for tablet",
    )


def test_validity_is_judged_on_todays_date(ctx):
    """Regression: an "expiring" certificate is still valid; a stale
    "active" status on a lapsed certificate is not."""
    Cert = ctx.env["fix.certification"]
    expiring = _cert(ctx, ctx.phone, expires_on=ctx.today + timedelta(days=10))
    assert expiring.status == "expiring"
    assert Cert.dispatch_eligibility(ctx.tech, device_type="smartphone")[0] is True
    expiring.unlink()
    lapsed = _cert(ctx, ctx.phone, expires_on=ctx.today - timedelta(days=1))
    _make_stale_active(ctx, lapsed)
    assert Cert.dispatch_eligibility(ctx.tech, device_type="smartphone")[0] is False
    lapsed.unlink()
    _cert(ctx, ctx.phone, issued_on=ctx.today + timedelta(days=5))  # not yet issued
    assert Cert.dispatch_eligibility(ctx.tech, device_type="smartphone")[0] is False


# --- training -> certification ----------------------------------------------------------


def test_training_enrolment_and_pass_certifies(ctx):
    env = ctx.env
    course = env["fix.training.course"].create(
        {"code": "TR-SP", "name": "Smartphone board repair", "competency_id": ctx.phone.id}
    )
    other = env["hr.employee"].create({"name": "Trainee Liza"})
    course.action_enroll(ctx.tech | other)
    assert course.enrollment_ids.mapped("employee_id") == ctx.tech | other
    assert set(course.enrollment_ids.mapped("state")) == {"enrolled"}
    enrolment = course.enrollment_ids.filtered(lambda e: e.employee_id == ctx.tech)
    enrolment.action_pass()
    assert (enrolment.state, enrolment.completed_on) == ("passed", ctx.today)
    cert = env["fix.certification"].search([("employee_id", "=", ctx.tech.id)])
    assert (cert.competency_id, cert.issued_on, cert.status) == (ctx.phone, ctx.today, "active")
    assert _events(env, "certification.granted", cert.id) == [
        {"employee": "Tech Mamun", "competency": "SP-L2"}
    ]
    assert _events(env, "training.passed", enrolment.id) == [
        {"employee": "Tech Mamun", "course": "TR-SP"}
    ]


def test_passing_a_course_without_competency_certifies_nothing(ctx):
    env = ctx.env
    course = env["fix.training.course"].create({"code": "TR-GEN", "name": "Induction"})
    course.action_enroll(ctx.tech)
    course.enrollment_ids.action_pass()
    assert course.enrollment_ids.state == "passed"
    assert not env["fix.certification"].search([("employee_id", "=", ctx.tech.id)])


# --- M02/M31 -> M22: the blocking check on the assignment path ------------------------


@pytest.fixture
def wo(ctx):
    env = ctx.env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    entity = env["fix.entity"].create(
        {"code": "CMPT", "legal_name": "Competency Test Ltd", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {"code": "CM1", "name": "Dhanmondi", "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    brand = env["fix.brand"].create({"name": "Cmp Brand", "code": "CMPB"})
    model = env["fix.device.model"].create(
        {"name": "Galaxy A35", "brand_id": brand.id, "device_type": "smartphone"}
    )
    device = env["fix.device"].create({"device_model_id": model.id, "branch_id": branch.id})
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": env["res.partner"].create({"name": "Customer"}).id,
            "branch_id": branch.id,
            "fault_description": "Water damage",
        }
    )
    # M55 roster gate (cd_attendance) satisfied so the M22 gate is what is tested
    shift = env["fix.shift.template"].create({"name": "Day", "start_hour": 9.0, "end_hour": 18.0})
    env["fix.roster.slot"].create(
        {"employee_id": ctx.tech.id, "date": ctx.today, "shift_id": shift.id}
    )

    def make(**vals):
        return env["fix.work.order"].create({"order_id": order.id, **vals})

    return make


def test_uncertified_assignment_blocked_on_create_and_write(ctx, wo):
    with (
        pytest.raises(UserError, match="M22 eligibility: assignment blocked — FR-LMS-039"),
        ctx.env.cr.savepoint(),
    ):
        wo(technician_id=ctx.tech.id)
    pending = wo()
    with (
        pytest.raises(UserError, match="no ACTIVE certification for smartphone"),
        ctx.env.cr.savepoint(),
    ):
        pending.write({"technician_id": ctx.tech.id})
    pending.write({"notes": "awaiting parts"})  # no technician change, no check
    assert pending.notes == "awaiting parts"


def test_certified_or_waived_assignment_passes(ctx, wo):
    waived = wo(technician_id=ctx.tech.id, certification_waiver=True)
    assert waived.technician_id == ctx.tech
    _cert(ctx, ctx.phone)
    certified = wo(technician_id=ctx.tech.id)
    assert certified.technician_id == ctx.tech
    later = wo()
    later.write({"technician_id": ctx.tech.id})
    assert later.technician_id == ctx.tech
    assert wo().action_check_certification() is True  # nobody assigned


def test_every_work_order_of_a_batch_is_checked(ctx, wo):
    """Regression: the loop returned after the first (waived) record."""
    waived = wo(technician_id=ctx.tech.id, certification_waiver=True)
    blocked = wo(certification_waiver=True)
    blocked.write({"technician_id": ctx.tech.id})
    blocked.certification_waiver = False
    with pytest.raises(UserError, match="assignment blocked"), ctx.env.cr.savepoint():
        (waived | blocked).action_check_certification()


def test_a_tier_shortfall_is_reported_as_a_tier_shortfall(ctx):
    """RAP-M22-02 keeps "the explanatory reason". When a certificate matched the
    brand but fell short on tier, the gate still reported "holds no ACTIVE brand
    certification", sending the operator after a certificate they already hold."""
    env = ctx.env
    brand = env["fix.brand"].create({"name": "TierBrand", "code": "TBRD"})
    cat = env["fix.device.category"].create({"code": "TIERCAT", "name": "Tier Category"})
    comp = env["fix.competency"].create(
        {
            "code": "TIERC",
            "name": "Tier competency",
            "required_for_dispatch": True,
            "brand_id": brand.id,
            "device_category_id": cat.id,
            "repair_tier": "l2",
        }
    )
    env["fix.certification"].create(
        {
            "employee_id": ctx.tech.id,
            "competency_id": comp.id,
            "brand_id": brand.id,
            "device_category_id": cat.id,
            "repair_tier": "l2",
        }
    )
    Cert = env["fix.certification"]
    ok, why = Cert.dispatch_eligibility(
        ctx.tech, device_type="TIERCAT", brand_id=brand.id, repair_tier="l2"
    )
    assert ok, why
    # the same technician on an L4 job: refused, and told it is the tier
    ok4, why4 = Cert.dispatch_eligibility(
        ctx.tech, device_type="TIERCAT", brand_id=brand.id, repair_tier="l4"
    )
    assert ok4 is False
    assert "tier L2" in why4 and "L4" in why4
    assert "holds no ACTIVE brand certification" not in why4
