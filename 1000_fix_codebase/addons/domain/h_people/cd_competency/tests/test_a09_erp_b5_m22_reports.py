# A09 ERP audit fix program, builder B5 — M22 report/KPI formula fixes
# (M22-F9), period honouring on every pack (UI-F3), the Dhaka business day
# in the controller (UI-F8) and KPI label/measure agreement (UI-F11).
# ruff: noqa: F811  (pytest fixtures imported from the round-1 suite)
from datetime import timedelta

from odoo import fields
from odoo.addons.cd_competency.tests.test_a09_erp_b5_m22_gates import _comp, _valid_cert
from odoo.addons.cd_competency.tests.test_a09_m22_controls import (  # noqa: F401 (fixtures)
    _employee,
    _user,
    c,
)
from odoo.addons.cd_p03_portal.controllers.a09 import m22


def _today(env):
    return fields.Date.context_today(env.user.with_context(tz=env.user.tz or "Asia/Dhaka"))


def _assessment(c, employee, comp, score, level="l3", day=None):
    return (
        c.env["fix.competency.assessment"]
        .sudo()
        .create(
            {
                "employee_id": employee.id,
                "competency_id": comp.id,
                "assessor_id": c.e_assessor.id,
                "score": score,
                "level": level,
                "assessed_on": day or _today(c.env),
            }
        )
    )


# ================================================================== M22-F9 (KPIs)
def test_brand_certifications_counts_brands_not_competencies(c):
    """m22.py:505 counted distinct COMPETENCIES under a 'Brand
    Certifications' tile: 3 competencies over 2 brands served 3."""
    one = c.env["fix.brand"].create({"name": "B5 One", "code": "B5ONE"})
    two = c.env["fix.brand"].create({"name": "B5 Two", "code": "B5TWO"})
    for i, brand in enumerate((one, one, two)):
        comp = _comp(c, "BR%d" % i, tier="l2", brand_id=brand.id)
        _valid_cert(c, c.e_col, comp, tier="l2", brand_id=brand.id)
    assert m22.kpis(c.env)["brand_certifications"] == 2


def test_training_hours_divides_by_the_real_technician_population(c):
    """The denominator was a 'tech'-in-position-name guess with a silent
    `or 1`; it is the M02 dispatch pool (the M21 'Technicians' rule)."""
    Ojt = c.env["fix.ojt.record"]
    Ojt.create({"employee_id": c.e_col.id, "hours": 100.0})
    # no dispatch-pool technician: the honest answer is 0, not 100/1
    assert m22.kpis(c.env)["training_hours"] == 0.0
    tech_user = _user(c.env, "cd_field_service.group_fix_field_service_user")
    _employee(c.env, tech_user)
    assert m22.kpis(c.env)["training_hours"] == 100.0


def test_certification_coverage_uses_the_configured_lead_time(c):
    Param = c.env["ir.config_parameter"].sudo()
    Param.set_param("cd_competency.expiry_lead_days", "60")
    try:
        comp = _comp(c, "LEAD", tier="l2")
        _valid_cert(c, c.e_col, comp, tier="l2", expires_on=_today(c.env) + timedelta(days=45))
        row = next(
            r for r in m22.certification_coverage(c.env)["rows"] if r["competency"] == comp.name
        )
        assert (
            row["expiring"] == 1 and row["valid"] == 0
        ), "45 days out is expiring at a 60-day lead (the old hardcoded 30 said valid)"
        pack = m22.certification_coverage(c.env)
        assert pack["labels"]["expiring"] == "Expiring 60d"
    finally:
        Param.set_param("cd_competency.expiry_lead_days", False)


def test_the_heatmap_counts_only_passed_assessments(c):
    """The gap analysis requires a passed assessment; the heatmap counted the
    latest assessment's level regardless (m22.py:294-307)."""
    comp = _comp(c, "HEAT")
    _assessment(c, c.e_col, comp, score=5, level="l4")  # failed at L4
    other = _employee(c.env)
    _assessment(c, other, comp, score=85, level="l3")  # passed at L3
    row = next(r for r in m22.skill_gap_heatmap(c.env)["rows"] if r["code"] == comp.code)
    assert row["l4"] == 0, "a failed attempt held no level"
    assert row["l3"] == 1


# ================================================================== UI-F3 (one test per pack)
def test_certification_coverage_honours_the_period(c):
    comp = _comp(c, "COVWIN", tier="l2")
    t = _today(c.env)
    # issued ON the as-of day: a snapshot taken the day before must not see it
    _valid_cert(c, c.e_col, comp, tier="l2", issued_on=t)
    rows_a = [
        r
        for r in m22.certification_coverage(c.env, date_to=t - timedelta(days=1))["rows"]
        if r["competency"] == comp.name
    ]
    rows_b = [
        r
        for r in m22.certification_coverage(c.env, date_to=t)["rows"]
        if r["competency"] == comp.name
    ]
    assert not rows_a and rows_b and rows_b[0]["holders"] == 1
    # an as-at snapshot never takes a future date
    pack = m22.certification_coverage(c.env, date_to=t + timedelta(days=300))
    assert ("as at %s" % t) in pack["title"]


def test_expiry_forecast_honours_the_period(c):
    comp = _comp(c, "FCST", tier="l2")
    t = _today(c.env)
    _valid_cert(c, c.e_col, comp, tier="l2", expires_on=t + timedelta(days=10))
    _valid_cert(c, c.e_uncert, comp, tier="l2", expires_on=t + timedelta(days=100))
    near = m22.expiry_forecast(c.env, date_from=t, date_to=t + timedelta(days=30))["rows"]
    far = m22.expiry_forecast(c.env, date_from=t, date_to=t + timedelta(days=180))["rows"]
    assert len(near) == 1 and len(far) == 2


def test_training_effectiveness_honours_the_period(c):
    import datetime

    recent = (
        c.env["fix.training.session"]
        .with_user(c.trn)
        .create(
            {
                "course_id": c.course.id,
                "delivery_mode": "classroom",
                "trainer_id": c.e_assessor.id,
                "venue": "B5",
                "date_start": datetime.datetime.now() - timedelta(days=3),
                "date_end": datetime.datetime.now() - timedelta(days=3) + timedelta(hours=6),
            }
        )
    )
    c.env["fix.training.enrollment"].with_user(c.trn).create(
        {"course_id": c.course.id, "session_id": recent.id, "employee_id": c.e_col.id}
    )
    t = _today(c.env)
    row_in = next(
        r
        for r in m22.training_effectiveness(c.env, date_from=t - timedelta(days=5), date_to=t)[
            "rows"
        ]
        if r["code"] == c.course.code
    )
    row_out = next(
        r
        for r in m22.training_effectiveness(
            c.env, date_from=t - timedelta(days=30), date_to=t - timedelta(days=10)
        )["rows"]
        if r["code"] == c.course.code
    )
    assert row_in["enrolments"] == 1 and row_out["enrolments"] == 0


def test_skill_gap_heatmap_honours_the_period(c):
    comp = _comp(c, "HEATWIN")
    t = _today(c.env)
    _assessment(c, c.e_col, comp, score=85, level="l3", day=t - timedelta(days=2))
    inside = next(
        r
        for r in m22.skill_gap_heatmap(c.env, date_from=t - timedelta(days=5), date_to=t)["rows"]
        if r["code"] == comp.code
    )
    outside = next(
        r
        for r in m22.skill_gap_heatmap(
            c.env, date_from=t - timedelta(days=30), date_to=t - timedelta(days=20)
        )["rows"]
        if r["code"] == comp.code
    )
    assert inside["l3"] == 1 and outside["l3"] == 0


def test_audit_evidence_honours_the_period(c):
    t = _today(c.env)
    fresh = (
        c.env["fix.audit.evidence"]
        .sudo()
        .create(
            {
                "evidence_type": "iso_9001",
                "standard_ref": "7.2",
                "collected_on": t - timedelta(days=2),
            }
        )
    )
    old = (
        c.env["fix.audit.evidence"]
        .sudo()
        .create(
            {
                "evidence_type": "iso_9001",
                "standard_ref": "7.2",
                "collected_on": t - timedelta(days=40),
            }
        )
    )
    rows_a = m22.audit_evidence_pack(c.env, date_from=t - timedelta(days=5), date_to=t)["rows"]
    rows_b = m22.audit_evidence_pack(
        c.env, date_from=t - timedelta(days=50), date_to=t - timedelta(days=30)
    )["rows"]
    assert [fresh.name] == [r["reference"] for r in rows_a]
    assert [old.name] == [r["reference"] for r in rows_b]


def test_role_gap_analysis_honours_the_period(c):
    t = _today(c.env)
    position = c.env["fix.org.position"].create({"name": "B5 bench lead"})
    c.e_col.position_id = position
    comp = _comp(c, "GAPWIN")
    path = c.env["fix.learning.path"].create(
        {"name": "B5 path", "position_ids": [(6, 0, [position.id])]}
    )
    c.env["fix.role.competency"].with_user(c.trn).create(
        {
            "path_id": path.id,
            "competency_id": comp.id,
            "min_level": "l3",
            "mandatory": True,
            "effective_from": t,
        }
    )
    yesterday = m22.role_gap_analysis(c.env, date_to=t - timedelta(days=1))["rows"]
    today_rows = m22.role_gap_analysis(c.env, date_to=t)["rows"]
    assert not [r for r in yesterday if r["employee"] == c.e_col.name]
    mine = [r for r in today_rows if r["employee"] == c.e_col.name]
    assert len(mine) == 1 and mine[0]["competency"] == comp.name
    assert ("as at %s" % t) in m22.role_gap_analysis(c.env, date_to=t)["title"]


# ================================================================== UI-F8 / UI-F11
def test_the_controller_today_is_the_callers_dhaka_day(odoo_env):
    assert m22._today(odoo_env) == _today(odoo_env)
    assert m22._today(odoo_env) == fields.Date.context_today(
        odoo_env.user.with_context(tz=odoo_env.user.tz or "Asia/Dhaka")
    )


def test_kpi_labels_agree_with_their_measures(c):
    """UI-F11 (M22 part): after the recomputes, every tile measures its
    label — brands are brands, hours are per dispatch-pool technician."""
    one = c.env["fix.brand"].create({"name": "B5 L", "code": "B5LBL"})
    comp = _comp(c, "LBL", tier="l2", brand_id=one.id)
    _valid_cert(c, c.e_col, comp, tier="l2", brand_id=one.id)
    out = m22.kpis(c.env)
    assert out["brand_certifications"] == 1  # 'Brand Certifications' -> brands
    tech_user = _user(c.env, "cd_field_service.group_fix_field_service_user")
    _employee(c.env, tech_user)
    c.env["fix.ojt.record"].create({"employee_id": c.e_col.id, "hours": 40.0})
    assert m22.kpis(c.env)["training_hours"] == 40.0  # 'OJT Hours /tech' -> pool
