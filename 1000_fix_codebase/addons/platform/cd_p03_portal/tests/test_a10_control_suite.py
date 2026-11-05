# A10 control suite — the cross-cutting sweep over EVERY workflow-controlled
# field, write whitelist and routed approval of the A10 Governance, Quality &
# Compliance surfaces (M23 QMS, M24 documents & e-signature, M60 GRC, M61
# knowledge), run as a non-admin user, plus the KPI honesty checks (D7).
#
# The A10 audit (2026-11-04, 307 probes / 187 gap) found 30 of 31 area models
# writable by a plain internal user, zero write whitelists, guarded fields on
# zero models, approvals a clerk could press, and KPI tiles with invented
# figures. The per-action gates live in the module suites
# (test_a10_q1_q2_q3_controls, test_a10_d1/d2_p11_controls,
# test_a10_r1/w1_w2_controls, test_a10_k1_controls, test_a10_s6_*); this suite
# is the A05 control suite applied to A10: no field, form or approval the
# audit attacked may have quietly reopened.
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import a10
from odoo.addons.cd_p03_portal.controllers.a10 import m23, m61
from odoo.addons.cd_p03_portal.controllers.a10.writable import WRITABLE
from odoo.exceptions import AccessError, UserError

# the guard's own refusal, an ACL refusal, or a module's stricter check
REFUSED = (
    r"changes only through its workflow|cannot be set directly|cannot move|"
    r"cannot change|not allowed to|access rights"
)
ROUTED_MESSAGE = "approver's inbox"
SIMPLE = {
    "char",
    "text",
    "boolean",
    "selection",
    "integer",
    "float",
    "monetary",
    "date",
    "datetime",
    "many2one",
}


def _models_static():
    """Model names for parametrisation, before any database is open."""
    return sorted(a10.SURFACES)


def _forged_value(env, field, current):
    """A value different from `current` that a forger would send."""
    if field.type == "boolean":
        return not current
    if field.type == "selection":
        values = [v for v, _l in (field._description_selection(env) or [])]
        others = [v for v in values if v != current]
        return others[-1] if others else None
    if field.type in ("integer", "float", "monetary"):
        return (current or 0) + 7
    if field.type == "date":
        return fields.Date.add(fields.Date.today(), days=-400)
    if field.type == "datetime":
        return fields.Datetime.add(fields.Datetime.now(), days=-400)
    if field.type == "many2one":
        other = env[field.comodel_name].sudo().search([], limit=2)
        other = other - current if current else other
        return other[:1].id or None
    return "forged-by-the-a10-control-suite"


@pytest.mark.parametrize("model", _models_static())
def test_every_guarded_field_refuses_a_direct_write(odoo_env, model):
    """S2/E3: for every guarded field of every A10 surface, a plain internal
    user's changing write() is refused — the audit's 30-writable-models gap."""
    if model not in odoo_env or not hasattr(odoo_env[model], "_fix_guarded_fields"):
        pytest.skip("%s carries no workflow-controlled fields" % model)
    clerk = (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A10 Suite Clerk",
                "login": "a10.suite.clerk@a10.test",
                "group_ids": [(6, 0, [odoo_env.ref("base.group_user").id])],
            }
        )
    )
    record = odoo_env(user=clerk.id)[model].new({})
    guarded = sorted(record._fix_guarded_fields())
    checked = 0
    for name in guarded:
        field = record._fields.get(name)
        if not field or field.type not in SIMPLE or not field.store or field.compute:
            continue
        if field.groups:
            continue  # the clerk cannot even read it
        value = _forged_value(odoo_env, field, record[name])
        if value is None:
            continue
        with pytest.raises((UserError, AccessError), match=REFUSED):
            record.write({name: value})
        checked += 1
    assert checked or not guarded, "%s declares guarded fields but none could be attacked" % model


@pytest.mark.parametrize("model", _models_static())
def test_no_form_offers_a_guarded_field_as_editable(odoo_env, model):
    """S2/R1: a workflow-owned field is never an editable input on a workspace
    form — the screen never offers what the server refuses. The one exception
    a model may declare is the FILING window: `_fix_form_locked_fields()` on a
    new record names what stays locked at birth (the whistle intake facts are
    the filing itself). Everything locked at birth stays off the form; what a
    model unlocks at birth freezes on the filed record — the endpoint reads
    the same method per record, and the freeze is proven in the module suite
    (test_a10_w1_w2_controls)."""
    if model not in odoo_env or not hasattr(odoo_env[model], "_fix_guarded_fields"):
        pytest.skip("%s carries no workflow-controlled fields" % model)
    model_rec = odoo_env[model].browse()
    guarded = model_rec._fix_guarded_fields()
    locked_at_birth = model_rec._fix_form_locked_fields()
    # a field locked at birth must never appear; a field the model unlocks at
    # filing may — the filed record freezes it again (per-record lock at the
    # endpoint, proven in the module suite)
    offered = guarded & locked_at_birth & set(WRITABLE.get(model, ()))
    assert not offered, "the %s form offers workflow fields as editable: %s" % (
        model,
        sorted(offered),
    )


def test_every_surface_has_a_whitelist():
    """D1/R3: every A10 surface declares what /p03/model/write may set."""
    missing = sorted(m for m, conf in a10.SURFACES.items() if conf.get("writable") is None)
    assert not missing, missing


def test_the_guard_reaches_the_area(odoo_env):
    """A guard on the guard: the audit attacked 31 area models and found none
    guarded; every A10 surface that OWNS workflow fields must now declare
    them."""
    guarded = [
        m
        for m in sorted(a10.SURFACES)
        if m in odoo_env
        and hasattr(odoo_env[m], "_fix_guarded_fields")
        and odoo_env[m].browse()._fix_guarded_fields()
    ]
    assert len(guarded) >= 25, guarded


ROUTED_FLOOR = 2


def test_every_routed_a10_approval_refuses_to_be_pressed_directly(odoo_env):
    """W-routed approvals (M63): the Quality Manager's review closure and the
    Document Controller's approval cannot be granted by pressing the button —
    only the approver's inbox applies them."""
    routed = [m for m in sorted(a10.SURFACES) if getattr(odoo_env[m], "_approval_routed", False)]
    assert len(routed) >= ROUTED_FLOOR, routed
    clerk = (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A10 Suite Presser",
                "login": "a10.suite.presser@a10.test",
                "group_ids": [(6, 0, [odoo_env.ref("base.group_user").id])],
            }
        )
    )
    clerk_env = odoo_env(user=clerk.id)
    for name in routed:
        record = clerk_env[name].new({})
        method = (
            "action_dofa_approve"
            if hasattr(record, "_dofa_route_guard")
            else record._approval_apply_method
        )
        with pytest.raises(UserError, match=ROUTED_MESSAGE):
            getattr(record, method)()


# --- KPI honesty (D7): the tiles count the records that own the figures ----


def _completed_checks(env):
    checks = env["fix.qc.checklist"].search([("state", "in", ("passed", "failed"))])
    return len(checks), len(checks.filtered(lambda q: q.state == "passed"))


def test_m23_kpis_measure_the_records_that_own_them(odoo_env):
    env = odoo_env
    before = m23.kpis(env)
    completed_before, passed_before = _completed_checks(env)
    # one open MAJOR NCR and one CLOSED minor
    env["fix.ncr"].create({"source": "audit", "severity": "major", "description": "kpi major"})
    host = env["fix.ncr"].create(
        {"source": "audit", "severity": "minor", "description": "kpi minor", "state": "closed"}
    )
    capa_owner = env["hr.employee"].create({"name": "KPI CAPA Owner"})
    # one CAPA verdict LATE (verified after its due date) and one ON TIME; a
    # CAPA always hangs off its NCR (ncr_id is required), the closed minor
    # here, and every verdict carries its verification note (ISO 10.2.2)
    env["fix.capa"].create(
        {
            "ncr_id": host.id,
            "severity": "minor",
            "corrective_action": "late",
            "owner_id": capa_owner.id,
            "due_on": date(2026, 1, 1),
            "verified_on": date(2026, 2, 1),
            "effectiveness_result": "effective",
            "verification_note": "verified after the due date",
            "state": "verified",
        }
    )
    env["fix.capa"].create(
        {
            "ncr_id": host.id,
            "severity": "minor",
            "corrective_action": "on time",
            "owner_id": capa_owner.id,
            "due_on": date(2026, 1, 1),
            "verified_on": date(2025, 12, 1),
            "effectiveness_result": "effective",
            "verification_note": "verified before the due date",
            "state": "verified",
        }
    )
    # one OPEN audit finding and one whose CAPA closed it
    framework = env["fix.compliance.framework"].create(
        {"name": "KPI framework", "code": "iso_9001"}
    )
    auditor = env["hr.employee"].create({"name": "KPI Lead Auditor"})
    env["fix.audit.finding"].create(
        {
            "name": "kpi open finding",
            "framework_id": framework.id,
            "auditor_id": auditor.id,
            "audit_date": date(2026, 11, 1),
            "target_closure_date": date(2026, 12, 1),
            "description": "the open finding the tile must count",
            "finding_type": "minor_nc",
            "capa_status": "open",
        }
    )
    env["fix.audit.finding"].create(
        {
            "name": "kpi closed finding",
            "framework_id": framework.id,
            "auditor_id": auditor.id,
            "audit_date": date(2026, 11, 1),
            "target_closure_date": date(2026, 12, 1),
            "description": "closed by its CAPA — outside the open count",
            "finding_type": "minor_nc",
            "capa_status": "closed",
        }
    )
    # one passed and one failed QC check (first-pass over COMPLETED only);
    # a PENDING check measures nothing
    brand = env["fix.brand"].create({"name": "KPI Brand A10", "code": "KB10"})
    model = env["fix.device.model"].create(
        {"brand_id": brand.id, "name": "K-1", "device_type": "laptop"}
    )
    device = env["fix.device"].create({"device_model_id": model.id})
    customer = env["res.partner"].create({"name": "KPI Customer"})
    company = env["res.company"].create({"name": "KPI Suite Co"})
    entity = env["fix.entity"].create(
        {"code": "EN-KPI", "legal_name": "KPI Entity", "company_id": company.id}
    )
    branch = env["fix.branch"].create(
        {
            "code": "KPI01",
            "name": "KPI Branch",
            "entity_id": entity.id,
            "operating_unit_id": env["operating.unit"]
            .search([("company_id", "=", env.company.id)], limit=1)
            .id,
        }
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "kpi",
        }
    )
    env["fix.qc.checklist"].create({"order_id": order.id, "state": "passed"})
    env["fix.qc.checklist"].create({"order_id": order.id, "state": "failed"})
    env["fix.qc.checklist"].create({"order_id": order.id})  # pending: no effect

    after = m23.kpis(env)
    assert after["major_ncs"] == before["major_ncs"] + 1  # severity read from the NCR
    assert after["open_ncrs"] == before["open_ncrs"] + 1  # the closed minor is not open
    assert after["audit_findings"] == before["audit_findings"] + 1  # findings, not audits
    # first-pass = passed / (passed + failed); the pending check is outside
    assert after["first_pass_qc"] == round((passed_before + 1) / (completed_before + 2) * 100.0, 1)
    # capa on-time: the late verdict weighs against the on-time one
    assert after["capa_on_time"] <= before["capa_on_time"] or before["capa_on_time"] == 0.0


def test_m23_capa_on_time_counts_only_verdicts_that_beat_their_due_date(odoo_env):
    env = odoo_env
    host = env["fix.ncr"].create(
        {"source": "audit", "severity": "minor", "description": "capa-on-time host"}
    )
    capa_owner = env["hr.employee"].create({"name": "On-Time CAPA Owner"})
    before = m23.kpis(env)
    # a CAPA with NO due date and a verdict counts as on time (nothing to
    # beat): adding one on-time verdict can only keep or raise the ratio
    env["fix.capa"].create(
        {
            "ncr_id": host.id,
            "severity": "minor",
            "corrective_action": "no due date",
            "owner_id": capa_owner.id,
            "verified_on": date(2026, 2, 1),
            "effectiveness_result": "effective",
            "verification_note": "nothing to beat",
            "state": "verified",
        }
    )
    on_time = m23.kpis(env)
    assert on_time["capa_on_time"] >= before["capa_on_time"]
    # a pending CAPA measures nothing — even one verified LATE past its due
    # date: until the verdict lands it is outside the figure
    env["fix.capa"].create(
        {
            "ncr_id": host.id,
            "severity": "minor",
            "corrective_action": "still pending",
            "owner_id": capa_owner.id,
            "due_on": date(2026, 1, 1),
            "verified_on": date(2026, 6, 1),  # late — but no verdict yet
            "state": "open",
        }
    )
    after = m23.kpis(env)
    assert after["capa_on_time"] == on_time["capa_on_time"]


def test_m61_kpis_count_what_their_labels_say(odoo_env):
    env = odoo_env
    before = m61.kpis(env)
    # a published article past its review date: one review due. NB the model
    # flags every article offline-available BY DEFAULT — opt this one out or
    # it would join the offline pack too (the flag is the article's own).
    overdue = env["fix.knowledge.article"].create(
        {
            "name": "KPI overdue review",
            "category": "device_guide",
            "content": "<p>k</p>",
            "offline_available": False,
        }
    )
    overdue.action_publish()
    overdue.write({"review_due": date.today() - timedelta(days=1)})
    # an offline pack entry: published AND offline_available
    offline = env["fix.knowledge.article"].create(
        {
            "name": "KPI offline pack",
            "category": "device_guide",
            "content": "<p>k</p>",
            "offline_available": True,
        }
    )
    offline.action_publish()
    # a draft only: it is NOT a review due and NOT in the offline pack
    env["fix.knowledge.article"].create(
        {"name": "KPI draft only", "category": "device_guide", "content": "<p>k</p>"}
    )
    after = m61.kpis(env)
    assert after["articles"] == before["articles"] + 3
    assert after["reviews_due"] == before["reviews_due"] + 1  # published + past due
    assert after["offline_articles"] == before["offline_articles"] + 1  # published + flagged
    assert "coverage_serviced" in after and "offline_synced_techs" not in after
    assert "coverage_top_faults" not in after
