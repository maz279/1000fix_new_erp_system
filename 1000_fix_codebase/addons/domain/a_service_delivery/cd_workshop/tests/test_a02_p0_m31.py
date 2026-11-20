"""A02 workflow audit, P0 for M31 Workshop & Depot Repair (M31-1 … M31-12).

The A02 probes (working/A02_evidence/probes/m31_m04/probe_m31_m04.py, P31-*)
turned into controls. Every attack runs as a NON-ADMIN user created here:

  tech   - Workshop Technician, the job's repairing technician
  tech2  - a second Workshop Technician (the colleague a forger names)
  qc     - Workshop QC Inspector (independent of the repair)
  supv   - Workshop Supervisor
  plain  - base.group_user only

Each control is tested both ways: the bypass is refused and the legitimate
path still works. `odoo_env` (addons/conftest.py) rolls everything back.
"""

import base64
import itertools
from contextlib import contextmanager
from datetime import timedelta
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.exceptions import UserError, ValidationError

GUARD = "changes only through its workflow"
_SEQ = itertools.count(1)


class FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def call():
    """The real /p03/model/write and /p03/model/action handlers."""
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


@contextmanager
def refused(env, exc=UserError, match=None):
    with pytest.raises(exc, match=match), env.cr.savepoint():
        yield
    env.invalidate_all()


def _user(env, tag, groups):
    n = next(_SEQ)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M31 %s %d" % (tag, n),
                "login": "a02.m31.%s.%d@a02.test" % (tag, n),
                "group_ids": [(6, 0, [env.ref("base.group_user").id] + [g.id for g in groups])],
            }
        )
    )
    emp = env["hr.employee"].create({"name": "M31 %s %d (emp)" % (tag, n), "user_id": user.id})
    return user, emp


def _set_order_state(order, state):
    """Test setup only: put the parent order where M01 would have put it.
    M01's own approval rules are not under test here."""
    order.env.cr.execute("UPDATE fix_service_order SET state=%s WHERE id=%s", (state, order.id))
    order.invalidate_recordset(["state"])


@pytest.fixture
def m31(odoo_env):
    env = odoo_env
    # the QC-instrument business switch is on in the live estate; these
    # controls predate it, so they run with it off unless a test turns it on
    env["ir.config_parameter"].sudo().set_param("cd_workshop.qc_requires_instrument", "0")
    G_TECH = env.ref("cd_workshop.group_fix_workshop_user")
    G_QC = env.ref("cd_workshop.group_fix_workshop_qc_inspector")
    G_SUPV = env.ref("cd_workshop.group_fix_workshop_manager")
    tech, tech_emp = _user(env, "tech", [G_TECH])
    tech2, tech2_emp = _user(env, "tech2", [G_TECH])
    qc, qc_emp = _user(env, "qc", [G_QC])
    supv, _supv_emp = _user(env, "supv", [G_SUPV])
    plain, _plain_emp = _user(env, "plain", [])
    n = next(_SEQ)
    workshop = env["fix.workshop"].create(
        {"code": "WS-A02-%d" % n, "name": "A02 Depot %d" % n, "name_bn": "ডিপো"}
    )
    l1 = env["fix.workshop.bench"].create(
        {
            "workshop_id": workshop.id,
            "code": "B-A02-L1-%d" % n,
            "name": "L1",
            "name_bn": "এল১",
            "max_concurrent_jobs": 20,
        }
    )
    l2 = env["fix.workshop.bench"].create(
        {
            "workshop_id": workshop.id,
            "code": "B-A02-L2-%d" % n,
            "name": "L2",
            "name_bn": "এল২",
            "repair_level": "l2",
            "max_concurrent_jobs": 20,
        }
    )
    ou = env["operating.unit"].search([], limit=1)
    # one legal entity per company (fix_entity_company_unique): reuse it
    entity = env["fix.entity"].search([("company_id", "=", env.company.id)], limit=1) or env[
        "fix.entity"
    ].create(
        {"code": "A02E%d" % n, "legal_name": "A02 Entity %d" % n, "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "A02 Branch %d" % n,
            "code": "A02B%d" % n,
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    brand = env["fix.brand"].create({"name": "A02Brand%d" % n, "code": "A02BR%d" % n})
    model = env["fix.device.model"].create({"name": "A02Phone%d" % n, "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "A02 Customer %d" % n})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-A02-%d" % n}
    )
    product = env["product.product"].create(
        {"name": "A02 spare %d" % n, "default_code": "A02-SP-%d" % n, "standard_price": 500.0}
    )

    def order(state="approved"):
        so = env["fix.service.order"].create(
            {
                "device_id": device.id,
                "customer_id": customer.id,
                "branch_id": branch.id,
                "fault_description": "A02 M31 fault",
            }
        )
        if state != so.state:
            _set_order_state(so, state)
        return so

    def job(level="l1", so=None, **vals):
        """A job created by the technician himself, on an approved order."""
        so = so if so is not None else order()
        return (
            env["fix.workshop.job"]
            .with_user(tech)
            .create(
                {
                    "workshop_id": workshop.id,
                    "fault_description": "A02 probe job",
                    "repair_level": level,
                    "order_id": so.id if so else False,
                    "technician_id": tech_emp.id,
                    # A02 P2: the book-in the intake gate needs
                    "bookin_condition": "A02 probe: light scratches on the housing",
                    "bookin_no_accessories": True,
                    **vals,
                }
            )
        )

    return SimpleNamespace(
        env=env,
        tech=tech,
        tech_emp=tech_emp,
        tech2=tech2,
        tech2_emp=tech2_emp,
        qc=qc,
        qc_emp=qc_emp,
        supv=supv,
        plain=plain,
        workshop=workshop,
        l1=l1,
        l2=l2,
        product=product,
        order=order,
        job=job,
    )


def _evidence(m, job, *types):
    Ev = m.env["fix.workshop.evidence"].with_user(m.tech)
    for t in types:
        Ev.create_evidence(job.id, "%s.jpg" % t, base64.b64encode(b"evidence"), t)


def _passed_checklist(m, order):
    """M01's order-level QC checklist (BRU-SRM-04), which its action_ready reads."""
    return m.env["fix.qc.checklist"].create(
        {
            "order_id": order.id,
            "state": "passed",
            # M01 reads the checklist of the order's current QC round
            "qc_round": order.qc_round,
            "item_ids": [(0, 0, {"name": "Functional test", "passed": True})],
        }
    )


def _handover_ready(m, order):
    """Test setup only: M01's own handover evidence (OTP verified, recipient,
    signed report), which its action_deliver reads. Not under test here."""
    report = m.env["ir.attachment"].create(
        {"name": "service-report.pdf", "datas": base64.b64encode(b"%PDF-1.4")}
    )
    order.sudo().write(
        {
            "delivery_otp_verified": True,
            "recipient_name": "A02 Customer",
            "service_report_attachment_id": report.id,
        }
    )


def _m01_delivered(m, order):
    """A02 pass 2 M31-02: the relay delivers M01's service_order.delivered
    to the workshop consumer, which closes the released job."""
    return (
        m.env["fix.workshop.job"]
        .sudo()
        .consume_service_order_delivered({"payload": {"order_id": order.id}})
    )


def _to_repair(m, job, bench=None):
    job.action_intake()
    job.action_diagnostic()
    job.write({"bench_id": (bench or m.l1).id})
    job.action_start_repair()
    return job


def _as(m, user, job):
    return job.with_user(user)


def _protocol_passed(m, job, burn_in_minutes=0):
    """A02 pass 2 M31-04: QC is judged on the job's test protocol. Test setup:
    a one-step functional protocol on the job and a passing result recorded by
    the repairing technician."""
    proto = m.env["fix.workshop.test.protocol"].create(
        {
            "code": "A02R2-%d-%d" % (job.id, next(_SEQ)),
            "name": "A02 functional check",
            "burn_in_minutes": burn_in_minutes,
            "step_ids": [(0, 0, {"name": "Boots and charges", "has_limits": False})],
        }
    )
    job.sudo()._guarded().write({"protocol_id": proto.id})
    m.env["fix.workshop.test.result"].with_user(m.tech).create(
        {"job_id": job.id, "step_id": proto.step_ids.id, "observed_pass": True}
    )
    return proto


def _qc_ready(m, job):
    """An L1 job in qc_pending with its evidence pack and its order's QC checklist."""
    _to_repair(m, job)
    if not job.protocol_id:
        _protocol_passed(m, job)
    job.action_submit_qc()
    _evidence(m, job, "post_repair_photo", "test_log")
    if job.order_id:
        _passed_checklist(m, job.order_id)
    return job


# --- A1: the workflow fields are guarded (M31-1; P31-01, P31-02) --------------


def test_p31_01_technician_cannot_write_the_workflow_fields(m31):
    job = m31.job()
    for vals in (
        {"state": "delivered"},
        {"qc_passed": True},
        {"burn_in_passed": True},
        {"burn_in_actual_minutes": 240.0},
        {"thermal_crash_count": 0, "burn_in_started_at": fields.Datetime.now()},
        {"certification_waiver": True},
        {"qc_inspector_id": m31.tech2_emp.id},
        {"completed_at": fields.Datetime.now()},
        {"rework_of_id": job.id},
        {"ber_writeoff_amount": 1.0},
    ):
        with refused(m31.env, UserError, GUARD):
            job.write(vals)
    assert job.sudo().state == "draft"
    # ...nor create a job already in a late state or "passed"
    with refused(m31.env, UserError, GUARD):
        m31.job(state="ready", qc_passed=True)
    # the legitimate path: the named action moves the job
    job.action_intake()
    assert job.state == "intake"


def test_p31_01_the_derived_writeoff_tier_cannot_be_typed(m31):
    job = m31.job()
    with refused(m31.env, UserError, GUARD):
        job.write({"dofa_writeoff_tier": "tier_4"})
    assert job.dofa_writeoff_tier == "none"


def test_p31_02_p03_write_refuses_state_qc_and_burn_in(m31, call):
    job = m31.job(level="l2")
    env = m31.env(user=m31.tech.id)
    res = call(
        env,
        "model_write",
        model="fix.workshop.job",
        record_id=job.id,
        values={
            "state": "delivered",
            "qc_passed": True,
            "burn_in_passed": True,
            "qc_inspector_id": m31.tech2_emp.id,
        },
    )
    assert "error" in res
    job.invalidate_recordset()
    assert (job.sudo().state, job.sudo().qc_passed, job.sudo().burn_in_passed) == (
        "draft",
        False,
        False,
    )
    # an ordinary form field still saves
    ok = call(
        env,
        "model_write",
        model="fix.workshop.job",
        record_id=job.id,
        values={"schematic_designators": "U7000"},
    )
    assert "error" not in ok, ok
    assert job.sudo().schematic_designators == "U7000"


def test_p31_12_plain_user_cannot_touch_a_job(m31, call):
    job = m31.job()
    with refused(m31.env):
        job.with_user(m31.plain).write({"diagnostic_findings": "x"})
    res = call(
        m31.env(user=m31.plain.id),
        "model_action",
        model="fix.workshop.job",
        ids=[job.id],
        method="action_intake",
    )
    assert res["success"] is False
    assert job.sudo().state == "draft"


def test_the_form_serves_workflow_fields_read_only(m31):
    job = m31.job()
    locked = job._fix_form_locked_fields()
    assert {"state", "qc_passed", "qc_inspector_id", "certification_waiver"} <= locked
    assert "order_id" not in locked  # a draft job can still be re-pointed
    job.action_intake()
    assert "order_id" in job._fix_form_locked_fields()


# --- A3: who may sign QC off (M31-2; P31-03, P31-04) ------------------------


def test_p31_03_naming_a_colleague_no_longer_passes_own_qc(m31):
    job = _qc_ready(m31, m31.job())
    with refused(m31.env, UserError, GUARD):
        job.write({"qc_inspector_id": m31.tech2_emp.id})
    # the technician holds no QC role
    with refused(m31.env, UserError, "QC Inspector"):
        job.action_pass_qc("looks fine")
    # a colleague technician holds no QC role either
    with refused(m31.env, UserError, "QC Inspector"):
        _as(m31, m31.tech2, job).action_pass_qc("looks fine")
    assert job.sudo().state == "qc_pending"


def test_p31_04_a_qc_inspector_cannot_inspect_his_own_repair(m31):
    m31.tech.group_ids = [(4, m31.env.ref("cd_workshop.group_fix_workshop_qc_inspector").id)]
    job = _qc_ready(m31, m31.job())
    with refused(m31.env, ValidationError, "BRU-SRM-18"):
        job.action_pass_qc("self QC")
    assert job.sudo().state == "qc_pending"


def test_independent_qc_passes_and_is_stamped_from_the_actor(m31):
    job = _qc_ready(m31, m31.job())
    _as(m31, m31.qc, job).action_pass_qc("All rails nominal")
    job.invalidate_recordset()
    assert (job.state, job.qc_passed, job.qc_notes) == ("ready", True, "All rails nominal")
    assert (job.qc_inspector_user_id, job.qc_inspector_id) == (m31.qc, m31.qc_emp)
    assert job.qc_inspected_at and job.completed_at
    assert job.order_id.state == "ready"


def test_a_supervisor_may_also_inspect(m31):
    job = _qc_ready(m31, m31.job())
    _as(m31, m31.supv, job).action_pass_qc()
    assert job.sudo().state == "ready"


# --- A5: release evidence (M31-8; P31-13) -----------------------------------


def test_p31_13_release_needs_the_evidence_pack(m31):
    job = m31.job()
    _to_repair(m31, job)
    _protocol_passed(m31, job)  # A02 pass 2 M31-04: QC judges the protocol
    job.action_submit_qc()
    _passed_checklist(m31, job.order_id)
    with refused(m31.env, UserError, "evidence pack"):
        _as(m31, m31.qc, job).action_pass_qc()
    _evidence(m31, job, "post_repair_photo")
    with refused(m31.env, UserError, "Functional Test Log"):
        _as(m31, m31.qc, job).action_pass_qc()
    _evidence(m31, job, "test_log")
    _as(m31, m31.qc, job).action_pass_qc()
    assert job.sudo().state == "ready"


def test_another_jobs_photo_does_not_release_this_job(m31):
    other = m31.job()
    _evidence(m31, other, "post_repair_photo", "test_log")
    job = m31.job()
    _to_repair(m31, job)
    _protocol_passed(m31, job)  # A02 pass 2 M31-04: QC judges the protocol
    job.action_submit_qc()
    _passed_checklist(m31, job.order_id)
    Ev = m31.env["fix.workshop.evidence"].with_user(m31.tech)
    # refused when it is borrowed
    for ev in other.sudo().evidence_ids:
        with refused(m31.env, UserError, "another record"):
            Ev.create(
                {
                    "job_id": job.id,
                    "name": "borrowed",
                    "evidence_type": ev.evidence_type,
                    "document_id": ev.document_id.id,
                }
            )
    # and a row already pointing elsewhere (older data) still releases nothing
    _evidence(m31, job, "post_repair_photo", "test_log")
    job.sudo().evidence_ids.document_id.sudo()._guarded().write({"res_id": other.id})
    with refused(m31.env, UserError, "evidence pack"):
        _as(m31, m31.qc, job).action_pass_qc()


def test_evidence_cannot_be_relabelled_after_capture(m31, call):
    job = m31.job()
    _evidence(m31, job, "pre_repair_photo")
    ev = job.sudo().evidence_ids
    with refused(m31.env, UserError, "captured evidence"):
        ev.with_user(m31.tech).write({"evidence_type": "post_repair_photo"})
    with refused(m31.env, UserError, GUARD):
        ev.with_user(m31.tech).write({"captured_by_id": m31.tech2_emp.id})
    assert ev.captured_by_id == m31.tech_emp
    assert ev.with_user(m31.tech).write({"description": "corner crack"})


# --- A5: burn-in is a real, timed state (M31-6; P31-05) ---------------------


def _l2_in_repair(m31):
    job = m31.job(level="l2")
    job.action_intake()
    job.action_diagnostic()
    job.write({"bench_id": m31.l2.id})
    # A02 P1 (B1): the technician requests it, a supervisor grants it from his inbox
    from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox

    job.action_request_certification_waiver("M22 course booked")
    req = m31.env["fix.workshop.waiver.request"].search([("job_id", "=", job.id)])
    approve_via_inbox(req, m31.supv)
    job.action_start_repair()
    return job


def test_p31_05_burn_in_cannot_be_skipped_or_typed(m31):
    job = _l2_in_repair(m31)
    # typed minutes are refused, and the gate does not run from in_repair
    with refused(m31.env, UserError, GUARD):
        job.write({"burn_in_actual_minutes": 240.0, "thermal_crash_count": 0})
    with refused(m31.env, UserError, "not in burn-in"):
        job.action_pass_burn_in()
    with refused(m31.env, UserError, "requires burn-in test to pass before QC"):
        job.action_submit_qc()
    job.action_start_burn_in()
    assert job.state == "burn_in" and job.burn_in_started_at
    # minutes come from the clock, not from the technician
    with refused(m31.env, UserError, "FLAW-31.3 Burn-In Gate"):
        job.action_pass_burn_in()
    job.sudo().write({"burn_in_started_at": fields.Datetime.now() - timedelta(minutes=250)})
    job.action_log_thermal_crash("reboot at 180 min")
    with refused(m31.env, UserError, "thermal/stress crashes"):
        job.action_pass_burn_in()
    # a failed run goes back to the bench; a new run starts clean
    job.action_fail_burn_in("reboot")
    assert (job.state, job.burn_in_passed) == ("in_repair", False)
    job.action_start_burn_in()
    assert job.thermal_crash_count == 0
    job.sudo().write({"burn_in_started_at": fields.Datetime.now() - timedelta(minutes=245)})
    job.action_pass_burn_in()
    job.invalidate_recordset()
    assert (job.state, job.burn_in_passed) == ("qc_pending", True)
    assert job.burn_in_actual_minutes >= 240.0 and job.burn_in_completed_at


def test_l2_release_also_needs_the_burn_in_log(m31):
    job = _l2_in_repair(m31)
    job.action_start_burn_in()
    job.sudo().write({"burn_in_started_at": fields.Datetime.now() - timedelta(minutes=245)})
    job.action_pass_burn_in()
    _protocol_passed(m31, job)  # A02 pass 2 M31-04: tested after the burn-in
    _evidence(m31, job, "post_repair_photo", "test_log")
    _passed_checklist(m31, job.order_id)
    with refused(m31.env, UserError, "Telemetry Log"):
        _as(m31, m31.qc, job).action_pass_qc()
    _evidence(m31, job, "burn_in_log")
    _as(m31, m31.qc, job).action_pass_qc()
    assert job.sudo().state == "ready"


# --- M31-7: no generic transition around the side-effects (P31-06) -----------


def test_p31_06_qc_fail_cannot_skip_the_ncr(m31, call):
    job = _to_repair(m31, m31.job())
    job.action_submit_qc()
    res = call(
        m31.env(user=m31.tech.id),
        "model_action",
        model="fix.workshop.job",
        ids=[job.id],
        method="action_transition",
        kwargs={"new_state": "qc_failed"},
    )
    assert res == {"success": False, "error": "Action not available for this surface"}
    for target in ("qc_failed", "ready", "unrepairable"):
        with refused(m31.env, UserError, "reached only through its own action"):
            job.action_transition(target)
    assert job.sudo().state == "qc_pending"
    # the proper method raises the NCR and counts the rework
    _as(m31, m31.qc, job).action_fail_qc("solder bridge")
    job.invalidate_recordset()
    assert (job.state, job.is_rework, job.rework_count) == ("qc_failed", True, 1)
    assert job.ncr_id and job.ncr_id.source == "qc"


def test_the_generic_transition_dispatches_to_the_named_action(m31):
    job = m31.job()
    job.action_transition("intake")
    assert job.state == "intake"


# --- A3: the certification waiver is a supervisor action (M31-5; P31-07) -----


def test_p31_07_the_technician_cannot_waive_his_own_certification(m31):
    job = m31.job(level="l2")
    job.action_intake()
    with refused(m31.env, UserError, GUARD):
        job.write({"certification_waiver": True, "certification_waiver_reason": "self"})
    with refused(m31.env, UserError, "written justification"):
        job.action_grant_certification_waiver("")
    # A02 P1 (B1): pressing the old button only raises the routed request
    job.action_grant_certification_waiver("M22 course booked")
    job.invalidate_recordset()
    assert not job.certification_waiver
    req = m31.env["fix.workshop.waiver.request"].search([("job_id", "=", job.id)])
    assert req.state == "pending" and req.approval_state == "pending"
    from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox

    approve_via_inbox(req, m31.supv)
    job.invalidate_recordset()
    assert job.certification_waiver
    assert (job.certification_waiver_by_id, job.certification_waiver_technician_id) == (
        m31.supv,
        m31.tech_emp,
    )
    assert job.certification_waiver_at
    # the waiver covers the technician it was granted for, not a replacement
    assert job._m31_waiver_covers(m31.tech_emp)
    assert not job._m31_waiver_covers(m31.tech2_emp)


# --- A4: the job follows the approved order (M31-3; P31-08) ------------------


def test_p31_08_repair_waits_for_the_approved_order(m31):
    so = m31.order(state="estimate_sent")
    job = m31.job(so=so)
    job.action_intake()
    job.action_diagnostic()
    job.write({"bench_id": m31.l1.id})
    with refused(m31.env, UserError, "Repair starts only once the order is approved"):
        job.action_start_repair()
    assert job.sudo().state == "diagnostic"
    _set_order_state(so, "approved")
    job.action_start_repair()
    assert (job.state, so.state) == ("in_repair", "in_repair")


def test_p31_08_the_order_sync_no_longer_swallows_a_refusal(m31):
    """The order's own action_ready needs a passed QC checklist (BRU-SRM-04):
    the job is not released while its order cannot follow."""
    job = m31.job()
    _to_repair(m31, job)
    _protocol_passed(m31, job)  # A02 pass 2 M31-04: QC judges the protocol
    job.action_submit_qc()
    _evidence(m31, job, "post_repair_photo", "test_log")
    # the bench QC now records the order's checklist (A02 ERP audit); the
    # property under test is that an order-side refusal still holds the job
    from unittest import mock

    Order = type(job.order_id)
    with (
        mock.patch.object(Order, "_check_qc_gate", side_effect=UserError("QC checklist refused")),
        refused(m31.env, UserError, "QC checklist"),
    ):
        _as(m31, m31.qc, job).action_pass_qc()
    assert (job.sudo().state, job.order_id.state) == ("qc_pending", "qc_pending")


def test_p31_08_delivery_needs_the_order_to_be_settled(m31):
    so = m31.order()
    est = m31.env["fix.estimate"].create(
        {
            "order_id": so.id,
            "line_ids": [(0, 0, {"description": "Screen", "unit_price": 3000.0})],
        }
    )
    m31.env.cr.execute("UPDATE fix_estimate SET state='approved' WHERE id=%s", (est.id,))
    est.invalidate_recordset(["state"])
    job = _qc_ready(m31, m31.job(so=so))
    _as(m31, m31.qc, job).action_pass_qc()
    _handover_ready(m31, so)
    # A02 pass 2 M31-02: the bench releases; the customer hand-over is M01's,
    # and M01's own settlement gate holds the device
    with refused(m31.env, UserError, "front desk"):
        job.action_deliver()
    job.action_release()
    assert (job.sudo().state, so.state) == ("released", "ready")
    so.write(
        {
            "payment_settlement_state": "settled",
            "amount_settled_bdt": est.grand_total,
            "settlement_verified": True,
        }
    )
    so.action_deliver()
    _m01_delivered(m31, so)
    assert (job.sudo().state, so.state) == ("delivered", "delivered")


def test_the_rework_loop_still_runs_against_the_order(m31):
    job = _qc_ready(m31, m31.job())
    _as(m31, m31.qc, job).action_fail_qc("fan noise")
    assert job.sudo().state == "qc_failed"
    job.action_start_repair()
    assert job.sudo().state == "in_repair"
    job.action_submit_qc()
    # M01 reads the checklist of the new QC round
    _passed_checklist(m31, job.order_id)
    _as(m31, m31.qc, job).action_pass_qc()
    assert (job.sudo().state, job.order_id.state) == ("ready", "ready")


# --- A4 / A1: parts (M31-4; P31-09, P31-09b, P31-10) -------------------------


def _line(m31, job, qty=1.0, cost=500.0):
    """A part line added by the technician. A02 ERP audit M31-F13: the bench
    no longer types the cost (it is the part's standard cost); a test that
    needs another cost sets it up as the system, as a dearer part would."""
    line = (
        m31.env["fix.workshop.part.line"]
        .with_user(m31.tech)
        .create({"job_id": job.id, "product_id": m31.product.id, "quantity": qty})
    )
    if abs((line.unit_cost or 0.0) - cost) > 1e-6:
        line.sudo()._guarded().write({"unit_cost": cost})
    return line


def test_p31_09_parts_are_consumed_only_in_repair_and_within_the_estimate(m31):
    so = m31.order()
    est = m31.env["fix.estimate"].create(
        {"order_id": so.id, "line_ids": [(0, 0, {"description": "Board", "unit_price": 30000.0})]}
    )
    m31.env.cr.execute("UPDATE fix_estimate SET state='approved' WHERE id=%s", (est.id,))
    est.invalidate_recordset(["state"])
    job = m31.job(so=so)
    job.action_intake()
    job.action_diagnostic()
    big = _line(m31, job, qty=3, cost=25000.0)
    assert big.reservation_state == "draft"  # no fictional reservation
    with refused(m31.env, UserError, "while job .* is in repair"):
        big.action_consume_part()
    job.write({"bench_id": m31.l1.id})
    job.action_start_repair()
    with refused(m31.env, UserError, "BRU-WSR-11"):
        big.action_consume_part()
    small = _line(m31, job, qty=1, cost=20000.0)
    small.action_consume_part()
    assert (small.reservation_state, small.consumed_by_id) == ("consumed", m31.tech)
    with refused(m31.env, UserError, "BRU-WSR-11"):
        _line(m31, job, qty=1, cost=15000.0).action_consume_part()


def _approved_estimate(m31, so, amount=30000.0):
    """Test setup only: an approved M01 estimate (M01's own approval rules
    are not under test here)."""
    est = m31.env["fix.estimate"].create(
        {"order_id": so.id, "line_ids": [(0, 0, {"description": "Repair", "unit_price": amount})]}
    )
    m31.env.cr.execute("UPDATE fix_estimate SET state='approved' WHERE id=%s", (est.id,))
    est.invalidate_recordset(["state"])
    return est


def test_p31_09b_a_consumed_line_is_frozen_and_undeletable(m31):
    so = m31.order()
    _approved_estimate(m31, so)
    job = _to_repair(m31, m31.job(so=so))
    line = _line(m31, job)
    with refused(m31.env, UserError, GUARD):
        line.write({"reservation_state": "consumed"})
    line.action_consume_part()
    with refused(m31.env, UserError, GUARD):
        line.write({"reservation_state": "released", "consumption_ref": False})
    with refused(m31.env, UserError, "consumed quantity and cost"):
        line.write({"unit_cost": 90000.0})
    with refused(m31.env, UserError, "cannot be deleted"):
        line.unlink()
    with refused(m31.env, UserError, "only an unconsumed line"):
        line.action_release_reservation()
    # an unconsumed line can still be corrected or removed
    draft = _line(m31, job)
    draft.write({"quantity": 2.0})
    draft.unlink()
    assert job.sudo().part_line_ids == line


def test_p31_10_a_delivered_job_is_frozen(m31):
    so = m31.order()
    est = _approved_estimate(m31, so)
    so.sudo().write(
        {"payment_settlement_state": "settled", "amount_settled_bdt": est.grand_total,
         "settlement_verified": True}
    )  # fmt: skip
    job = _to_repair(m31, m31.job(so=so))
    line = _line(m31, job)
    _protocol_passed(m31, job)  # A02 pass 2 M31-04: QC judges the protocol
    job.action_submit_qc()
    _evidence(m31, job, "post_repair_photo", "test_log")
    _passed_checklist(m31, job.order_id)
    _as(m31, m31.qc, job).action_pass_qc()
    _handover_ready(m31, job.order_id)
    job.action_release()
    job.order_id.sudo().action_deliver()
    _m01_delivered(m31, job.order_id)
    before = job.sudo().total_repair_cost
    with refused(m31.env, UserError, "consumed quantity and cost"):
        line.write({"unit_cost": 90000.0})
    with refused(m31.env, UserError, "closed job is the record"):
        job.write({"labour_total": 50000.0})
    with refused(m31.env, UserError, "it is closed"):
        _line(m31, job)
    with refused(m31.env, UserError, "cannot be deleted"):
        line.unlink()
    assert job.sudo().total_repair_cost == before
    assert "labour_total" in job._fix_form_locked_fields()


def test_the_repair_level_and_technician_are_fixed_on_the_bench(m31):
    job = _to_repair(m31, m31.job())
    with refused(m31.env, UserError, "fixed once the job is under way"):
        job.write({"repair_level": "l2"})
    with refused(m31.env, UserError, "fixed once the job is under way"):
        job.write({"technician_id": m31.tech2_emp.id})


# --- BER / scrap under DOFA (M31-9; P31-11) ----------------------------------


def test_p31_11_ber_needs_dofa_approval_and_a_second_technician(m31):
    env = m31.env
    approver, _emp = _user(
        env,
        "dofa",
        [
            env.ref("cd_entity_config.group_dofa_tier_2"),
            env.ref("cd_workshop.group_fix_workshop_user"),
        ],
    )
    from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox

    so = m31.order(state="diagnostic")
    job = m31.job(so=so)
    job.action_intake()
    job.action_diagnostic()
    _evidence(m31, job, "diagnostic_report", "pre_repair_photo")
    job.action_propose_ber(
        "Board corroded beyond repair",
        writeoff_amount=8000.0,
        estimated_repair_cost=9000.0,
        device_value=5000.0,
    )
    job.invalidate_recordset()
    assert (job.dofa_writeoff_tier, job.ber_proposed_by_id) == ("tier_2", m31.tech)
    # the proposer cannot approve his own write-off, and nobody presses Approve
    with refused(env, UserError):
        job.action_dofa_approve()
    with refused(env, UserError, "approver's inbox"):
        _as(m31, approver, job).action_dofa_approve()
    # the proposer / repairing technician cannot confirm it
    with refused(env, UserError, "second technician"):
        job.action_confirm_ber()
    job.sudo().write({"dofa_justification": "Corrosion on PMIC area; photos attached"})
    # A02 P1 (B1): the second technician's confirmation routes the write-off
    _as(m31, m31.tech2, job).action_confirm_ber()
    job.invalidate_recordset()
    assert (job.state, job.approval_state) == ("diagnostic", "pending")
    approve_via_inbox(job, approver, requester=m31.tech2)
    job.invalidate_recordset()
    assert (job.state, job.ber_confirmed_by_id, job.dofa_approved_by) == (
        "unrepairable",
        m31.tech2,
        approver,
    )
    # B2: the order follows through M01's own unrepairable path
    assert (so.state, so.cancel_reason_code) == ("cancelled", "unrepairable")


# --- bench state (M31-1) ------------------------------------------------------


def test_bench_state_and_esd_readings_move_only_through_bench_actions(m31, call):
    bench = m31.l1.with_user(m31.tech)
    with refused(m31.env, UserError, GUARD):
        bench.write({"state": "offline"})
    with refused(m31.env, UserError, GUARD):
        bench.write({"esd_last_verified_date": fields.Date.today(), "wrist_strap_mohm": 1.0})
    res = call(
        m31.env(user=m31.tech.id),
        "model_write",
        model="fix.workshop.bench",
        record_id=m31.l1.id,
        values={"state": "maintenance"},
    )
    assert "error" in res
    bench.action_set_maintenance("tip replacement")
    assert m31.l1.state == "maintenance"
    with refused(m31.env, UserError, "supervisor"):
        bench.action_set_offline("closing")
    bench.action_return_to_service()
    assert m31.l1.state == "available"
    bench.action_log_daily_esd(5.0, 50.0)
    assert m31.l1.wrist_strap_mohm == 5.0


# --- the M31 workspace (M31-11 / M31-12) ---------------------------------------


def test_the_workspace_offers_named_actions_only():
    from odoo.addons.cd_p03_portal.controllers.a02 import m31 as surface

    actions = surface.SURFACES["fix.workshop.job"]["actions"]
    assert "action_transition" not in actions
    assert {
        "action_submit_qc",
        "action_pass_qc",
        "action_fail_qc",
        "action_grant_certification_waiver",
        "action_confirm_ber",
    } <= actions


def test_the_bridge_still_hands_an_order_to_the_workshop(m31):
    """P31-15 stays a PASS: the M01 -> M31 hand-off creates a draft job
    (from a booked-in order: a draft order is refused, A02 P2)."""
    so = m31.order(state="intake")
    job = so.action_create_workshop_job()
    assert (job.state, job.order_id) == ("draft", so)


# --- A02 ERP audit (20 Nov 2026): the bench QC is the order's QC ---------------
def test_a_bench_qc_pass_carries_the_order_to_ready_without_a_second_qc(m31):
    """The fix_real walk: a depot job passed QC on the bench but its order could
    not follow it to Ready ('no QC checklist for this QC round'); the existing
    tests had hidden it by creating the order's checklist by hand."""
    job = m31.job()
    _to_repair(m31, job)
    _protocol_passed(m31, job)  # A02 pass 2 M31-04: QC judges the protocol
    job.action_submit_qc()
    _evidence(m31, job, "post_repair_photo", "test_log")
    _as(m31, m31.qc, job).action_pass_qc("All functions tested")
    order = job.order_id.sudo()
    assert job.sudo().state == "ready" and order.state == "ready"
    (checklist,) = order.qc_checklist_ids.filtered(lambda c: c.qc_round == order.qc_round)
    assert checklist.state == "passed" and checklist.inspected_by == m31.qc
    assert checklist.inspector_id == m31.qc_emp
