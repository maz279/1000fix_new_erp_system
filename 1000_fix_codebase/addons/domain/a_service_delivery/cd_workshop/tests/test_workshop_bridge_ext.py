"""M31 extension tests: the service-order → workshop-job bridge and the
bench auto-allocation engine.

``odoo_env`` (addons/conftest.py): fix_test, rolled back after every test.
"""

from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from odoo.exceptions import UserError


@pytest.fixture
def ws(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "WSEXT", "legal_name": "WS Ext Entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "WS Ext Branch",
            "code": "WSEB",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    workshop = env["fix.workshop"].create(
        {
            "code": "WS-EXT-01",
            "name": "WS Ext Central",
            "name_bn": "WS Ext Central",
            "workshop_type": "central",
            "branch_id": branch.id,
            "operating_unit_id": ou.id,
        }
    )
    bench_l1 = env["fix.workshop.bench"].create(
        {
            "code": "BENCH-EXT-L1",
            "name": "Ext Bench L1",
            "name_bn": "Ext Bench L1",
            "workshop_id": workshop.id,
            "repair_level": "l1",
            "max_concurrent_jobs": 2,
            "operating_unit_id": ou.id,
        }
    )
    bench_l3 = env["fix.workshop.bench"].create(
        {
            "code": "BENCH-EXT-L3",
            "name": "Ext Bench L3 ESD",
            "name_bn": "Ext Bench L3 ESD",
            "workshop_id": workshop.id,
            "repair_level": "l3",
            "max_concurrent_jobs": 1,
            "is_esd_safe": True,
            "operating_unit_id": ou.id,
        }
    )
    brand = env["fix.brand"].create({"name": "WsExtBrand", "code": "WSEB"})
    device_model = env["fix.device.model"].create({"name": "WsExt Phone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "WS Customer", "phone": "01711000331"})
    device = env["fix.device"].create(
        {"device_model_id": device_model.id, "owner_id": customer.id, "serial_number": "SN-WSE-1"}
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "Bench job: no power",
            "service_type": "walk_in",
        }
    )
    return SimpleNamespace(
        env=env,
        workshop=workshop,
        bench_l1=bench_l1,
        bench_l3=bench_l3,
        order=order,
        customer=customer,
        device=device,
    )


# --- bridge ----------------------------------------------------------------


def test_bridge_creates_draft_job_at_l1(ws):
    jobs = ws.order.action_create_workshop_job()
    assert len(jobs) == 1
    job = jobs[0]
    assert job.state == "draft"
    assert job.workshop_id == ws.workshop  # branch-linked central facility
    assert job.order_id == ws.order
    assert job.device_id == ws.device and job.customer_id == ws.customer
    assert job.repair_level == "l1"
    assert ws.order.workshop_job_count == 1


def test_bridge_refuses_closed_orders(ws):
    order = ws.order
    order.state = "intake"
    order.state = "diagnostic"
    order.state = "estimate_pending"
    order.state = "estimate_sent"
    order.state = "awaiting_approval"
    order.state = "approved"
    order.state = "in_repair"
    order.state = "qc_pending"
    ws.env["fix.qc.checklist"].create({"order_id": order.id, "state": "passed"})
    order.state = "ready"
    order.state = "delivered"
    order.state = "closed"
    with pytest.raises(UserError, match="can no longer enter the workshop"):
        order.action_create_workshop_job()


# --- bench auto-allocation ---------------------------------------------------


def _live_job(ws, level="l1"):
    job = ws.order.action_create_workshop_job(repair_level=level)
    job.action_intake()
    job.action_diagnostic()
    return job


def test_auto_assign_picks_lowest_capable_free_bench(ws):
    job = _live_job(ws, "l1")
    job.action_auto_assign_bench()
    assert job.bench_id == ws.bench_l1  # L1 job stays on the L1 bench


def test_auto_assign_routes_l3_to_the_l3_bench(ws):
    job = _live_job(ws, "l3")
    job.action_auto_assign_bench()
    assert job.bench_id == ws.bench_l3  # only the L3 bench can take L3 work


def test_auto_assign_respects_capacity(ws):
    # fill the L3 bench (max 1) with a first job
    first = _live_job(ws, "l3")
    first.action_auto_assign_bench()
    assert first.bench_id == ws.bench_l3
    second = ws.env["fix.workshop.job"].create(
        {
            "order_id": ws.order.id,
            "workshop_id": ws.workshop.id,
            "repair_level": "l3",
            "state": "diagnostic",
            "fault_description": "Second L3 job for capacity test",
        }
    )
    with pytest.raises(UserError, match="No capable bench is free"):
        second.action_auto_assign_bench()
    assert not second.bench_id


def test_auto_assign_skips_expired_calibration(ws):
    ws.bench_l1.calibration_expiry_date = date.today() - timedelta(days=1)
    job = _live_job(ws, "l1")
    # the L3 bench (calibration fine) can also take L1 work — ranked after
    # the expired L1 bench is excluded
    job.action_auto_assign_bench()
    assert job.bench_id == ws.bench_l3
