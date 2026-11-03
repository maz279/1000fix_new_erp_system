"""Behavioural tests for the M31 workshop on the live ORM
(``odoo_env``: fix_test, rolled back after every test)."""

import base64
import json
from contextlib import contextmanager
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from odoo import fields
from odoo.addons.cd_workshop.models.fix_workshop_job import WORKSHOP_JOB_STATES
from odoo.exceptions import UserError, ValidationError


@contextmanager
def _refused(env, exc, match=None):
    """Expect ``exc``; the failed operation is rolled back (flushing savepoint)."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info
    env.invalidate_all()


@pytest.fixture
def ws(odoo_env):
    env = odoo_env
    tech = env["hr.employee"].create({"name": "WS Bench Tech"})
    job_tech = env["hr.employee"].create({"name": "WS Job Tech"})
    inspector = env["hr.employee"].create({"name": "WS Inspector"})
    workshop = env["fix.workshop"].create(
        {"code": "WS-TST-1", "name": "Test Depot", "name_bn": "টেস্ট ডিপো"}
    )
    bench_l1 = env["fix.workshop.bench"].create(
        {
            "workshop_id": workshop.id,
            "code": "BENCH-TST-L1",
            "name": "L1",
            "name_bn": "এল১",
            "technician_id": tech.id,
        }
    )
    bench_l3 = env["fix.workshop.bench"].create(
        {
            "workshop_id": workshop.id,
            "code": "BENCH-TST-L3",
            "name": "L3",
            "name_bn": "এল৩",
            "repair_level": "l3",
            "max_concurrent_jobs": 2,
        }
    )
    return SimpleNamespace(
        env=env,
        tech=tech,
        job_tech=job_tech,
        inspector=inspector,
        workshop=workshop,
        l1=bench_l1,
        l3=bench_l3,
    )


def _job(ws, **vals):
    return ws.env["fix.workshop.job"].create(
        {"workshop_id": ws.workshop.id, "fault_description": "Board dead", **vals}
    )


def _events(env, aggregate, rec_id, event_type=None):
    domain = [("aggregate", "=", aggregate), ("aggregate_id", "=", rec_id)]
    if event_type:
        domain.append(("event_type", "=", event_type))
    return env["fix.event.outbox"].search(domain, order="id asc")


def _to_repair(ws, job, bench=None):
    job.action_intake()
    (bench or ws.l1).action_assign_job(job)
    job.action_start_repair()


def _evidence(ws, job, *types):
    """A02 audit M31-8: a release needs the evidence pack."""
    for t in types or ("post_repair_photo", "test_log"):
        ws.env["fix.workshop.evidence"].create_evidence(
            job.id, "%s.jpg" % t, base64.b64encode(b"x"), t
        )


def _burn_in_elapsed(job, minutes=245):
    """A02 audit M31-6: burn-in minutes come from the start stamp."""
    job.write({"burn_in_started_at": fields.Datetime.now() - timedelta(minutes=minutes)})


def _passed_checklist(env, order):
    return env["fix.qc.checklist"].create(
        {
            "order_id": order.id,
            "state": "passed",
            "item_ids": [(0, 0, {"name": "Functional test", "passed": True})],
        }
    )


# --- workshop & bench ------------------------------------------------------------------------


def test_bench_capacity_drives_status_and_utilisation(ws):
    env = ws.env
    assert (
        ws.workshop.bench_count,
        ws.workshop.available_bench_count,
        ws.workshop.bench_utilization,
    ) == (2, 2, 0.0)
    job = _job(ws)
    job.action_intake()
    assert ws.l1.action_assign_job(job) is True
    assert (job.bench_id, job.technician_id) == (ws.l1, ws.tech)  # the bench's technician
    assert (ws.l1.current_job_count, ws.l1.state) == (1, "occupied")
    assert (ws.workshop.available_bench_count, ws.workshop.bench_utilization) == (1, 50.0)
    payload = json.loads(_events(env, "fix.workshop.bench", ws.l1.id).payload)
    assert (payload["job_id"], payload["technician_name"], payload["repair_level"]) == (
        job.id,
        "WS Bench Tech",
        "l1",
    )
    second = _job(ws)
    second.action_intake()
    with _refused(env, UserError, "reached its maximum concurrent job capacity \\(1\\)"):
        ws.l1.action_assign_job(second)
    ws.l1.action_release_job(second)  # not on this bench: nothing to release
    assert job.bench_id == ws.l1
    ws.l1.action_release_job(job)
    assert (job.bench_id, ws.l1.state, ws.l1.current_job_count) == (
        env["fix.workshop.bench"],
        "available",
        0,
    )
    empty = env["fix.workshop"].create({"code": "WS-TST-2", "name": "Empty", "name_bn": "খালি"})
    assert (empty.bench_count, empty.bench_utilization) == (0, 0.0)


def test_bench_routing_and_availability_rules(ws):
    env = ws.env
    l2_job = _job(ws, repair_level="l2", technician_id=ws.job_tech.id)
    l2_job.action_intake()
    with _refused(env, UserError, "requires L2 capability, but bench BENCH-TST-L1 is only L1"):
        ws.l1.action_assign_job(l2_job)
    ws.l3.action_assign_job(l2_job)  # an L3 bench takes lower levels; no bench technician
    assert (l2_job.bench_id, l2_job.technician_id, ws.l3.state) == (ws.l3, ws.job_tech, "available")
    payload = json.loads(_events(env, "fix.workshop.bench", ws.l3.id).payload)
    assert (payload["technician_id"], payload["technician_name"]) == (False, "Unassigned")
    ws.l3.state = "maintenance"
    other = _job(ws)
    other.action_intake()
    with _refused(env, UserError, "Bench is currently maintenance"):
        ws.l3.action_assign_job(other)
    ws.l3.action_release_job(l2_job)
    assert ws.l3.state == "maintenance"  # maintenance is never auto-flipped


def test_active_job_count_excludes_finished_jobs(ws):
    _job(ws)
    cancelled = _job(ws)
    cancelled.action_cancel()
    assert ws.workshop.active_job_count == 1


# --- job: state machine and gates ---------------------------------------------------------------


def test_group_expand_and_invalid_transitions(ws):
    env = ws.env
    assert env["fix.workshop.job"]._read_group_states(None, [], None) == [
        s for s, _l in WORKSHOP_JOB_STATES
    ]
    job = _job(ws)
    assert job.name.startswith("WSJ/")
    with _refused(env, UserError) as err:
        job.action_deliver()
    assert str(err.value) == (
        "Invalid job state transition: draft -> delivered. Permitted next states from "
        "'draft' are: cancelled, intake"
    )
    job.action_cancel()
    with _refused(env, UserError, "None \\(Terminal\\)"):
        job.action_intake()


def test_repair_needs_bench_technician_and_an_active_technician(ws):
    env = ws.env
    job = _job(ws)
    job.action_intake()
    job.action_diagnostic()
    with _refused(env, UserError, "without an assigned workbench"):
        job.action_start_repair()
    ws.l3.action_assign_job(job)  # no bench technician, none on the job
    with _refused(env, UserError, "without an assigned technician"):
        job.action_start_repair()
    job.technician_id = ws.job_tech
    ws.job_tech.active = False
    with _refused(env, UserError, "invalid or inactive"):
        job.action_start_repair()
    ws.job_tech.active = True
    job.action_wait_parts()
    job.action_start_repair()
    assert job.state == "in_repair"


def test_l2_repair_requires_m22_certification_unless_waived(ws):
    env = ws.env
    brand = env["fix.brand"].create({"name": "WsBrand", "code": "WSBR"})
    model = env["fix.device.model"].create({"name": "WsPhone", "brand_id": brand.id})
    device = env["fix.device"].create({"device_model_id": model.id, "serial_number": "SN-WS-1"})
    job = _job(ws, repair_level="l2", technician_id=ws.job_tech.id, device_id=device.id)
    job.action_intake()
    ws.l3.action_assign_job(job)
    competency = env["fix.competency"].create(
        {"code": "WS-SOLDER", "name": "Micro-soldering", "required_for_dispatch": True}
    )
    with _refused(
        env, UserError, "M22 Certification Gate .* holds no dispatch-gating certification"
    ):
        job.action_start_repair()
    env["fix.certification"].create({"employee_id": ws.job_tech.id, "competency_id": competency.id})
    job.action_start_repair()
    assert job.state == "in_repair"
    waived = _job(ws, repair_level="l3", technician_id=ws.inspector.id, certification_waiver=True)
    waived.action_intake()
    ws.l3.action_assign_job(waived)
    waived.action_start_repair()  # audited manager waiver: no certification needed
    assert waived.state == "in_repair"


def test_certification_gate_is_skipped_without_the_competency_module(ws):
    job = _job(ws, repair_level="l2", technician_id=ws.job_tech.id)
    env_class = type(ws.env)
    original = env_class.__contains__
    with patch.object(
        env_class,
        "__contains__",
        lambda self, name: name != "fix.certification" and original(self, name),
    ):
        assert job._check_technician_certification(ws.job_tech, "l2") is True


def test_burn_in_qc_and_release(ws):
    env = ws.env
    job = _job(
        ws,
        repair_level="l2",
        technician_id=ws.job_tech.id,
        certification_waiver=True,
        qc_inspector_id=ws.inspector.id,
    )
    _to_repair(ws, job, ws.l3)
    with _refused(env, UserError, "\\(L2\\) requires burn-in test to pass before QC"):
        job.action_transition("qc_pending")
    job.action_start_burn_in()
    assert (job.state, bool(job.burn_in_started_at)) == ("burn_in", True)
    _burn_in_elapsed(job)
    job.action_pass_burn_in()
    assert (job.state, job.burn_in_passed, bool(job.burn_in_completed_at)) == (
        "qc_pending",
        True,
        True,
    )
    assert job.burn_in_actual_minutes >= 240.0  # measured, not typed
    with _refused(env, UserError, "without passing Quality Control"):
        job._transition("ready")
    _evidence(ws, job, "post_repair_photo", "test_log", "burn_in_log")
    job.action_pass_qc(notes="All rails nominal")
    assert (job.state, job.qc_passed, job.qc_notes, bool(job.completed_at)) == (
        "ready",
        True,
        "All rails nominal",
        True,
    )
    assert (job.bench_id, ws.l3.current_job_count) == (
        env["fix.workshop.bench"],
        0,
    )  # bench released
    job.action_deliver()
    assert job.state == "delivered"
    transitions = [
        json.loads(e.payload)["new_state"]
        for e in _events(env, "fix.workshop.job", job.id, "workshop.job.transitioned")
    ]
    assert transitions == ["intake", "in_repair", "burn_in", "qc_pending", "ready", "delivered"]


def test_l1_job_goes_to_qc_without_burn_in(ws):
    job = _job(ws, qc_inspector_id=ws.inspector.id)
    _to_repair(ws, job)
    job.action_transition("qc_pending")
    assert job.state == "qc_pending"
    ws.l1.action_release_job(job)  # bench freed early (e.g. bench swap during QC)
    _evidence(ws, job)
    job.action_pass_qc()
    assert (job.state, job.bench_id) == ("ready", ws.env["fix.workshop.bench"])


def test_inspector_must_not_be_the_repairing_technician(ws):
    """A02 audit M31-2: compared on the ACTING user, not a typed inspector."""
    env = ws.env
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "WS Bench Tech User",
                "login": "ws.bench.tech@a02.test",
                "group_ids": [(6, 0, [env.ref("cd_workshop.group_fix_workshop_qc_inspector").id])],
            }
        )
    )
    ws.tech.user_id = user
    job = _job(ws)
    _to_repair(ws, job)  # the L1 bench assigns ws.tech
    job.action_transition("qc_pending")
    _evidence(ws, job)
    with _refused(ws.env, ValidationError, "BRU-SRM-18 Violation"):
        job.with_user(user).action_pass_qc()
    assert job.state == "qc_pending"


def test_qc_defaults_the_inspector_to_the_acting_user(ws):
    env = ws.env
    me = env.user.employee_id or env["hr.employee"].create(
        {"name": "WS Acting", "user_id": env.user.id}
    )
    job = _job(ws)
    _to_repair(ws, job)
    job.action_transition("qc_pending")
    _evidence(ws, job)
    job.action_pass_qc()
    assert job.qc_inspector_id == me
    assert job.qc_inspector_user_id == env.user


def test_qc_checks_the_test_instrument(ws):
    """A07 audit M45-14: this test used to MOCK action_assert_usable and then
    pass QC with a never-calibrated meter, certifying M45-1 as correct. It now
    runs the real M45 gate: never calibrated, then failed, then passed."""
    env = ws.env
    today = fields.Date.today()
    meter = env["fix.equipment"].create({"code": "WS-DMM-1", "name": "Bench DMM"})
    job = _job(ws, qc_inspector_id=ws.inspector.id, equipment_id=meter.id)
    _to_repair(ws, job)
    job.action_transition("qc_pending")
    _evidence(ws, job)

    def calibrate(on, result):
        env["fix.calibration"].create(
            {
                "equipment_id": meter.id,
                "calibrated_on": on,
                "next_due": on + timedelta(days=365),
                "standard_ref": "BSTI-REF-WS",
                "result": result,
            }
        )

    with _refused(env, UserError, "never been calibrated"):
        job.action_pass_qc()
    calibrate(today - timedelta(days=100), "pass")
    calibrate(today - timedelta(days=1), "fail")  # the latest result rules
    with _refused(env, UserError, "failed its latest calibration"):
        job.action_pass_qc()
    assert (job.state, job.qc_passed) == ("qc_pending", False)
    calibrate(today, "pass")
    job.action_pass_qc()
    assert (job.state, job.qc_passed, job.equipment_id) == ("ready", True, meter)


def test_failed_qc_raises_an_ncr_and_opens_one_rework_loop(ws):
    """Regressions: QC failure bypassed the state machine (any state -> qc_failed)
    and emitted workshop.qc.completed twice per failure."""
    env = ws.env
    job = _job(ws, qc_inspector_id=ws.inspector.id)
    _to_repair(ws, job)
    with _refused(env, UserError, "in_repair -> qc_failed"):
        job.action_fail_qc(reason="too early")
    assert (job.state, job.rework_count, job.ncr_id) == ("in_repair", 0, env["fix.ncr"])
    job.action_transition("qc_pending")
    assert job.action_fail_qc(reason="Charging port loose") is True
    assert (job.state, job.is_rework, job.rework_count, job.rework_reason) == (
        "qc_failed",
        True,
        1,
        "Charging port loose",
    )
    assert (job.qc_passed, job.ncr_id.severity, job.ncr_id.source) == (False, "major", "qc")
    assert (
        job.ncr_id.description
        == f"Workshop job {job.name} failed QC inspection: Charging port loose"
    )
    qc_events = _events(env, "fix.workshop.job", job.id, "workshop.qc.completed")
    assert len(qc_events) == 1
    assert json.loads(qc_events.payload)["rework_count"] == 0  # emitted at inspection time
    last = json.loads(
        _events(env, "fix.workshop.job", job.id, "workshop.job.transitioned")[-1].payload
    )
    assert (last["old_state"], last["new_state"], last["is_rework"]) == (
        "qc_pending",
        "qc_failed",
        True,
    )
    job.action_start_repair()  # the rework loop
    assert job.state == "in_repair"


def test_failed_qc_without_notes(ws):
    job = _job(ws, qc_inspector_id=ws.inspector.id)
    _to_repair(ws, job)
    job.action_transition("qc_pending")
    job.action_fail_qc()
    assert job.ncr_id.description.endswith("failed QC inspection: No details provided")


# --- job <-> service order --------------------------------------------------------------------


@pytest.fixture
def so(ws):
    env = ws.env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "WSOENT", "legal_name": "WS Entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {"name": "WS Branch", "code": "WSOB", "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    brand = env["fix.brand"].create({"name": "WsoBrand", "code": "WSOBR"})
    model = env["fix.device.model"].create({"name": "WsoLaptop", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "WS Customer"})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-WSO-1"}
    )
    return env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "No boot",
        }
    )


def test_job_milestones_follow_onto_the_service_order(ws, so):
    for state in (
        "intake",
        "diagnostic",
        "estimate_pending",
        "estimate_sent",
        "awaiting_approval",
        "approved",
    ):
        so.state = state
    job = _job(ws, order_id=so.id, qc_inspector_id=ws.inspector.id)
    assert job.order_reference == so.name
    _to_repair(ws, job)
    assert so.state == "in_repair"
    job.action_transition("qc_pending")
    assert so.state == "qc_pending"
    job.action_fail_qc(reason="Fan noise")
    # M01 now offers action_fail_qc (A02 audit M31-3 / M01): the order
    # follows the job into the rework loop through the order's own method
    assert (so.state, job.ncr_id.order_id) == ("qc_failed", so)
    job.action_start_repair()
    assert (job.state, so.state) == ("in_repair", "in_repair")
    job.action_transition("qc_pending")
    env = ws.env
    _passed_checklist(env, so)
    _evidence(ws, job)
    job.action_pass_qc()
    assert (job.state, so.state) == ("ready", "ready")
    report = env["ir.attachment"].create({"name": "r.pdf", "datas": base64.b64encode(b"%PDF")})
    so.write(
        {
            "delivery_otp_verified": True,
            "recipient_name": "WS Customer",
            "service_report_attachment_id": report.id,
        }
    )
    job.action_deliver()
    assert so.state == "delivered"
    payload = json.loads(
        _events(env, "fix.workshop.job", job.id, "workshop.job.transitioned")[-1].payload
    )
    assert (payload["order_id"], payload["order_reference"]) == (so.id, so.name)


def test_job_ready_does_not_bypass_the_order_qc_checklist_gate(ws, so):
    """Regression: the job wrote the order's state directly, skipping BRU-SRM-04
    (an order reaches Ready only with a passed QC checklist). A02 audit M31-3:
    the refusal is no longer swallowed, so the job is not released either."""
    for state in (
        "intake",
        "diagnostic",
        "estimate_pending",
        "estimate_sent",
        "awaiting_approval",
        "approved",
    ):
        so.state = state
    job = _job(ws, order_id=so.id, qc_inspector_id=ws.inspector.id)
    _to_repair(ws, job)
    job.action_transition("qc_pending")
    _evidence(ws, job)
    with _refused(ws.env, UserError, "QC checklist"):
        job.action_pass_qc()
    assert (job.state, so.state) == ("qc_pending", "qc_pending")


def test_a_job_on_an_unapproved_order_cannot_start_repair(ws, so):
    """A02 audit M31-3 / P31-08: the old sync skipped the refusal, so a job
    reached in_repair (and delivered) while its order was still a draft."""
    job = _job(ws, order_id=so.id)
    job.action_intake()
    ws.l1.action_assign_job(job)
    with _refused(ws.env, UserError, "Repair starts only once the order is approved"):
        job.action_start_repair()
    assert (job.state, so.state) == ("intake", "draft")
    job.action_wait_parts()  # no order milestone for waiting_parts
    assert so.state == "draft"


# --- parts & evidence ------------------------------------------------------------------------------


def test_parts_and_labour_cost_the_job(ws):
    env = ws.env
    screen = env["product.product"].create(
        {"name": "WS Screen", "default_code": "WS-SCR", "standard_price": 150.0}
    )
    paste = env["product.product"].create(
        {"name": "WS Paste", "default_code": "WS-PST", "standard_price": 75.5}
    )
    job = _job(ws, labour_total=200.0)
    lines = env["fix.workshop.part.line"]
    lines.create({"job_id": job.id, "product_id": screen.id, "quantity": 2, "unit_cost": 150.0})
    lines.create({"job_id": job.id, "product_id": paste.id, "unit_cost": 75.5})
    # parts 2 x 150 + 1 x 75.50 = 375.50; + labour 200 = 575.50
    assert (job.parts_total, job.total_repair_cost) == (375.5, 575.5)
    assert job.part_line_ids.mapped("part_number") == ["WS-SCR", "WS-PST"]
    draft_line = lines.new({"job_id": job.id, "product_id": paste.id})
    draft_line._onchange_product_id()
    assert draft_line.unit_cost == 75.5  # the product's cost price
    blank = lines.new({"job_id": job.id, "unit_cost": 9.0})
    blank._onchange_product_id()
    assert blank.unit_cost == 9.0  # no product: untouched


def test_evidence_is_stored_through_the_document_kernel(ws):
    env = ws.env
    evidence = env["fix.workshop.evidence"]
    with _refused(env, UserError, "Workshop job ID 999999999 does not exist"):
        evidence.create_evidence(999999999, "x", base64.b64encode(b"x"), "pre_repair_photo")
    job = _job(ws)
    record = evidence.create_evidence(
        job.id,
        "Before.jpg",
        base64.b64encode(b"jpeg"),
        "pre_repair_photo",
        description="Cracked corner",
    )
    doc = record.document_id
    assert (doc.res_model, doc.res_id, doc.document_type, doc.isolation_tier) == (
        "fix.workshop.job",
        job.id,
        "evidence_pack",
        "T1",
    )
    assert (record.job_id, record.evidence_type, record.description) == (
        job,
        "pre_repair_photo",
        "Cracked corner",
    )
    assert record.attachment_id == doc.attachment_id
    payload = json.loads(_events(env, "fix.workshop.evidence", record.id).payload)
    assert (payload["document_id"], payload["document_name"], payload["job_name"]) == (
        doc.id,
        "Before.jpg",
        job.name,
    )


def test_l2_gate_passes_the_brand_and_tier_to_m22(ws):
    """RAP-M22-01/02: M22 builds a (brand, device category, tier) gate, but the
    only path that enforces it passed `device_type` alone, leaving the brand
    and tier dimensions unreachable in production."""
    import inspect

    from odoo.addons.cd_workshop.models.fix_workshop_job import FixWorkshopJob

    src = inspect.getsource(FixWorkshopJob._check_technician_certification)
    call = src[src.find("dispatch_eligibility") :]
    assert "brand_id=" in call
    assert "repair_tier=" in call


def test_l2_gate_refuses_a_technician_certified_for_another_brand(ws):
    env = ws.env
    apple = env["fix.brand"].create({"name": "ZtApple", "code": "ZTAP"})
    other = env["fix.brand"].create({"name": "ZtGeneric", "code": "ZTGN"})
    model = env["fix.device.model"].create({"name": "ZtPhone", "brand_id": apple.id})
    device = env["fix.device"].create({"device_model_id": model.id, "serial_number": "SN-ZT-9"})
    # a dispatch-gating competency scoped to the order's brand
    apple_comp = env["fix.competency"].create(
        {
            "code": "ZT-APPLE",
            "name": "Apple logic board",
            "required_for_dispatch": True,
            "brand_id": apple.id,
        }
    )
    other_comp = env["fix.competency"].create(
        {
            "code": "ZT-GEN",
            "name": "Generic handset",
            "required_for_dispatch": True,
            "brand_id": other.id,
        }
    )
    # the technician holds the WRONG brand's certification
    env["fix.certification"].create({"employee_id": ws.job_tech.id, "competency_id": other_comp.id})
    job = _job(ws, repair_level="l2", technician_id=ws.job_tech.id, device_id=device.id)
    job.action_intake()
    ws.l3.action_assign_job(job)
    with _refused(env, UserError, "M22 Certification Gate"):
        job.action_start_repair()
    # granting the order's brand certification releases the job
    env["fix.certification"].create({"employee_id": ws.job_tech.id, "competency_id": apple_comp.id})
    job.action_start_repair()
    assert job.state == "in_repair"
