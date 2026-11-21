"""M05 iteration-2 engine tests: runbooks, patching, SLA credits, on-call
rota, maintenance-window suppression, problem & change, estate polish.

``odoo_env`` (addons/conftest.py): fix_test, rolled back after every test.
"""

import json
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import UserError
from psycopg2 import IntegrityError


@pytest.fixture
def ms(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "MSENG", "legal_name": "MS Engines Entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "MS Engines Branch",
            "code": "MSE2",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    customer = env["res.partner"].create({"name": "MS Engines Customer"})
    brand = env["fix.brand"].create({"name": "MsEngBrand", "code": "MS2"})
    device_model = env["fix.device.model"].create({"name": "MsEng Laptop", "brand_id": brand.id})
    device = env["fix.device"].create(
        {
            "device_model_id": device_model.id,
            "owner_id": customer.id,
            "branch_id": branch.id,
            "serial_number": "SN-MSENG-1",
        }
    )
    contract = env["fix.contract"].create(
        {
            "name": "MS Engines Contract",
            "customer_id": customer.id,
            "family": "managed",
            "state": "active",  # A02 audit M05-P2: MSP work needs a term in force
            "operating_unit_id": ou.id,
            "date_start": fields.Date.today(),
            "date_end": fields.Date.today().replace(year=fields.Date.today().year + 1),
            "annual_value": 240000.0,
        }
    )
    msp = env["fix.msp.contract"].create(
        {
            "name": "MS Engines MSP",
            "contract_id": contract.id,
            "operating_unit_id": ou.id,
            "device_count": 4,
            "per_device_monthly": 2500.0,
            "sla_target_pct": 95.0,
        }
    )
    asset = env["fix.monitored.asset"].create(
        {
            "msp_contract_id": msp.id,
            "agent_id": "AGT-MSENG-1",
            "hostname": "ws-mseng-01",
            "device_id": device.id,
        }
    )
    tech = env["hr.employee"].create({"name": "MS Engines Tech"})
    from types import SimpleNamespace

    return SimpleNamespace(env=env, ou=ou, msp=msp, asset=asset, device=device, tech=tech)


def _events(env, aggregate, rec_id):
    return env["fix.event.outbox"].search(
        [("aggregate", "=", aggregate), ("aggregate_id", "=", rec_id)], order="id asc"
    )


# ------------------------------------------------------------- runbooks


def test_runbook_execute_records_run_and_resolves_alert(ms):
    env = ms.env
    alert = env["fix.msp.alert"].create(
        {
            "msp_contract_id": ms.msp.id,
            "asset_id": ms.asset.id,
            "severity": "major",
            "message": "disk pressure",
            "state": "acked",
        }
    )
    book = env["fix.msp.runbook"].create(
        {
            "name": "Clear disk pressure",
            "trigger": "alert_major",
            "scope_contract_id": ms.msp.id,
            "script": "1. prune logs\n2. clear temp",
            "auto_resolve_alert": True,
            "operating_unit_id": ms.ou.id,
        }
    )
    # A02 audit M05-P2: resolving the alert needs the execution's evidence
    with pytest.raises(UserError, match="record the evidence"):
        book.action_execute(asset="AGT-MSENG-1", alert_id=alert.id)
    book.action_execute(asset="AGT-MSENG-1", alert_id=alert.id, evidence="pruned logs; 40 GB free")

    run = env["fix.msp.runbook.run"].search([("runbook_id", "=", book.id)])
    assert len(run) == 1
    assert run.state == "success" and run.asset_id == ms.asset
    assert run.output_note == "pruned logs; 40 GB free"
    events = _events(env, "fix.msp.runbook.run", run.id)
    assert events.mapped("event_type") == ["msp.runbook_executed"]
    # auto-resolve fired on the linked alert
    alert.invalidate_recordset()
    assert alert.state == "resolved"
    assert "Clear disk pressure" in (alert.resolution_note or "")


def test_runbook_execute_by_asset_id_and_unknown_agent(ms):
    env = ms.env
    book = env["fix.msp.runbook"].create(
        {"name": "Reboot asset", "script": "reboot", "operating_unit_id": ms.ou.id}
    )
    book.action_execute(asset=ms.asset.id)
    assert env["fix.msp.runbook.run"].search_count([("runbook_id", "=", book.id)]) == 1
    with pytest.raises(UserError):
        book.action_execute(asset="NO-SUCH-AGENT")


def test_runbook_archived_refuses_execution(ms):
    env = ms.env
    book = env["fix.msp.runbook"].create(
        {"name": "Archived book", "script": "noop", "active": False, "operating_unit_id": ms.ou.id}
    )
    with pytest.raises(UserError):
        book.action_execute(asset=ms.asset.id)


def test_runbook_run_finish_guard(ms):
    env = ms.env
    book = env["fix.msp.runbook"].create(
        {"name": "Guard book", "script": "noop", "operating_unit_id": ms.ou.id}
    )
    book.action_execute(asset=ms.asset.id)
    run = env["fix.msp.runbook.run"].search([("runbook_id", "=", book.id)])
    with pytest.raises(UserError):
        run.action_finish(note="again")


# -------------------------------------------------------------- patching


def test_patch_update_lifecycle_and_compliance(ms):
    env = ms.env
    upd = env["fix.msp.patch.update"].create(
        {
            "msp_contract_id": ms.msp.id,
            "asset_id": ms.asset.id,
            "identifier": "KB5000001",
            "title": "Cumulative Update 2026-10",
            "severity": "critical",
            "operating_unit_id": ms.ou.id,
        }
    )
    assert upd.state == "missing"
    upd.action_approve()
    assert upd.state == "approved" and upd.approved_date == fields.Date.today()
    # A02 ERP pass 2 (M05-S10): an install happens inside an open window
    window = env["fix.msp.maintenance.window"].create(
        {
            "name": "Patch night",
            "msp_contract_id": ms.msp.id,
            "start_at": fields.Datetime.now() - timedelta(hours=1),
            "end_at": fields.Datetime.now() + timedelta(hours=3),
            "operating_unit_id": ms.ou.id,
        }
    )
    window.action_approve()
    upd.action_install()
    assert upd.state == "installed" and upd.installed_at
    events = _events(env, "fix.msp.patch.update", upd.id)
    assert "msp.patch_installed" in events.mapped("event_type")


def test_patch_update_defer_fail_and_unique(ms):
    env = ms.env
    vals = {
        "msp_contract_id": ms.msp.id,
        "asset_id": ms.asset.id,
        "identifier": "CHROME-128",
        "title": "Chrome 128",
        "operating_unit_id": ms.ou.id,
    }
    upd = env["fix.msp.patch.update"].create(vals)
    # A02 ERP audit M05-F18: a deferral has its reason; only an approved patch fails
    upd._guarded().write({"state": "missing"})  # whatever a live auto-approve policy did
    upd.action_defer(days=3, reason="vendor recall pending")
    from odoo.addons.cd_msp_contract.models.msp_periods import dhaka_today

    assert upd.state == "deferred" and upd.deferred_until == dhaka_today() + timedelta(days=3)
    upd.action_approve()
    upd.action_fail(note="hash mismatch")
    assert upd.state == "failed" and upd.fail_note == "hash mismatch"
    with pytest.raises(IntegrityError):
        env["fix.msp.patch.update"].create(vals)  # unique(asset, identifier)


def test_patch_policy_auto_approve_on_create(ms):
    env = ms.env
    env["fix.msp.patch.policy"].create(
        {
            "name": "Auto OS policy",
            "category": "os",
            "msp_contract_id": ms.msp.id,
            "auto_approve": True,
            "operating_unit_id": ms.ou.id,
        }
    ).action_approve()  # A02 audit M05-6: only an approved policy auto-approves
    upd = env["fix.msp.patch.update"].create(
        {
            "msp_contract_id": ms.msp.id,
            "asset_id": ms.asset.id,
            "identifier": "KB5000002",
            "title": "Servicing Stack",
            "category": "os",
            "operating_unit_id": ms.ou.id,
        }
    )
    assert upd.state == "approved", "auto-approve policy must pre-approve the update"
    third_party = env["fix.msp.patch.update"].create(
        {
            "msp_contract_id": ms.msp.id,
            "asset_id": ms.asset.id,
            "identifier": "VLC-4",
            "title": "VLC 4",
            "category": "third_party",
            "operating_unit_id": ms.ou.id,
        }
    )
    assert third_party.state == "missing", "policy scopes by category"


# ------------------------------------------------------------- SLA credits


def test_sla_credit_compute_approve_apply(ms):
    env = ms.env
    report = env["fix.msp.service.report"].create(
        {
            "msp_contract_id": ms.msp.id,
            "period_label": "2026-09",
            "alert_count": 10,
            "resolved_count": 5,
            "sla_attainment": 0.5,
            "operating_unit_id": ms.ou.id,
        }
    )
    ms.msp.action_compute_sla_credits()
    credit = env["fix.msp.sla.credit"].search(
        [("msp_contract_id", "=", ms.msp.id), ("period_label", "=", "2026-09")]
    )
    assert len(credit) == 1
    # shortfall 45% of monthly value 4 x 2500 = 10000 -> 4500.0
    assert credit.credit_amount == 4500.0
    assert credit.state == "draft" and credit.service_report_id == report

    # idempotent
    ms.msp.action_compute_sla_credits()
    assert (
        env["fix.msp.sla.credit"].search_count(
            [("msp_contract_id", "=", ms.msp.id), ("period_label", "=", "2026-09")]
        )
        == 1
    )

    credit.action_approve()
    assert credit.state == "approved"
    credit.action_apply()
    assert credit.state == "applied"
    events = _events(env, "fix.msp.sla.credit", credit.id)
    applied = events.filtered(lambda e: e.event_type == "msp.sla_credit_applied")
    payload = json.loads(applied.payload)
    # what the M20 credit note needs (A02 audit B1): contract, partner, amount, period
    assert {k: payload[k] for k in ("contract", "period", "amount")} == {
        "contract": ms.msp.name,
        "period": "2026-09",
        "amount": 4500.0,
    }
    assert payload["contract_id"] == ms.msp.contract_id.id
    assert payload["partner_id"] == ms.msp.contract_id.customer_id.commercial_partner_id.id
    assert payload["currency"] == "BDT" and payload["credit_id"] == credit.id
    with pytest.raises(UserError):
        credit.action_apply()  # already applied


def test_sla_credit_skips_periods_on_target(ms):
    env = ms.env
    env["fix.msp.service.report"].create(
        {
            "msp_contract_id": ms.msp.id,
            "period_label": "2026-08",
            "alert_count": 4,
            "resolved_count": 4,
            "sla_attainment": 1.0,
            "operating_unit_id": ms.ou.id,
        }
    )
    ms.msp.action_compute_sla_credits()
    assert not env["fix.msp.sla.credit"].search(
        [("msp_contract_id", "=", ms.msp.id), ("period_label", "=", "2026-08")]
    )


# ------------------------------------------------------------- on-call rota


def test_oncall_shift_lifecycle_and_primary(ms):
    env = ms.env
    now = fields.Datetime.now()
    shift = env["fix.msp.oncall.shift"].create(
        {
            "name": "NOC week 44",
            "technician_id": ms.tech.id,
            "level": "primary",
            "start_at": now - timedelta(hours=1),
            "end_at": now + timedelta(hours=7),
            "operating_unit_id": ms.ou.id,
        }
    )
    assert env["fix.msp.oncall.shift"].current_primary() is None
    shift.action_activate()
    assert shift.state == "active"
    assert env["fix.msp.oncall.shift"].current_primary() == ms.tech
    events = _events(env, "fix.msp.oncall.shift", shift.id)
    assert events.mapped("event_type") == ["msp.oncall_shift_active"]
    shift.action_close()
    assert shift.state == "closed"
    with pytest.raises(UserError):
        shift.action_close()


def test_oncall_shift_window_constraint(ms):
    env = ms.env
    now = fields.Datetime.now()
    with pytest.raises(UserError, match="must end after it starts"):
        env["fix.msp.oncall.shift"].create(
            {
                "name": "Bad shift",
                "technician_id": ms.tech.id,
                "start_at": now,
                "end_at": now - timedelta(hours=1),
                "operating_unit_id": ms.ou.id,
            }
        )


# --------------------------------------------------- maintenance windows


def test_maintenance_window_suppresses_alerting(ms):
    env = ms.env
    now = fields.Datetime.now()
    window = env["fix.msp.maintenance.window"].create(
        {
            "name": "Firmware push",
            "msp_contract_id": ms.msp.id,
            "start_at": now - timedelta(minutes=10),
            "end_at": now + timedelta(minutes=50),
            "operating_unit_id": ms.ou.id,
        }
    )
    window.action_approve()  # A02 audit M05-5: approval + time range open it
    assert env["fix.msp.maintenance.window"].alerting_suppressed(ms.asset) is True

    # a healthy -> degraded transition under the window: NO alert
    env["fix.monitored.asset"].ingest_telemetry("AGT-MSENG-1", "degraded", now)
    assert env["fix.msp.alert"].search_count([("asset_id", "=", ms.asset.id)]) == 0

    # window closed: the same transition on another asset raises
    other = env["fix.monitored.asset"].create(
        {"msp_contract_id": ms.msp.id, "agent_id": "AGT-MSENG-2", "hostname": "ws-mseng-02"}
    )
    window.action_close()
    env["fix.monitored.asset"].ingest_telemetry("AGT-MSENG-2", "offline", now)
    alert = env["fix.msp.alert"].search([("asset_id", "=", other.id)])
    assert len(alert) == 1 and alert.severity == "major"


# --------------------------------------------------- problem & change


def test_change_record_full_lifecycle(ms):
    env = ms.env
    # A02 audit M05-1: a high-risk change needs a rollback plan and runs
    # inside an approved, open maintenance window.
    now = fields.Datetime.now()
    window = env["fix.msp.maintenance.window"].create(
        {
            "name": "Core switch window",
            "msp_contract_id": ms.msp.id,
            "start_at": now - timedelta(minutes=10),
            "end_at": now + timedelta(hours=2),
        }
    )
    window.action_approve()
    rec = env["fix.msp.change.record"].create(
        {
            "name": "Swap core switch",
            "kind": "change",
            "change_type": "normal",
            "risk": "high",
            "msp_contract_id": ms.msp.id,
            "asset_id": ms.asset.id,
            "requested_by": ms.tech.id,
            "description": "Replace the failing uplink module",
            "rollback_plan": "Re-seat the old uplink module",
            "maintenance_window_id": window.id,
            "operating_unit_id": ms.ou.id,
        }
    )
    rec.action_approve()
    assert rec.state == "approved"
    rec.action_implement(note="Uplink replaced, traffic clean")
    assert rec.state == "implemented" and rec.implemented_at
    events = _events(env, "fix.msp.change.record", rec.id)
    assert set(events.mapped("event_type")) == {"msp.change_approved", "msp.change_implemented"}
    rec.action_close(note="Done")
    assert rec.state == "closed" and rec.resolution_note == "Done"
    with pytest.raises(UserError):
        rec.action_close()


def test_change_record_reject_path(ms):
    env = ms.env
    rec = env["fix.msp.change.record"].create(
        {"name": "Risky idea", "risk": "high", "operating_unit_id": ms.ou.id}
    )
    rec.action_reject(note="no rollback plan")
    assert rec.state == "rejected" and rec.resolution_note == "no rollback plan"
    rec.action_close()
    assert rec.state == "closed"


# ------------------------------------------------------- estate polish


def test_asset_display_name_and_health_score(ms):
    env = ms.env
    assert ms.asset.display_name == "ws-mseng-01"
    bare = env["fix.monitored.asset"].create(
        {"msp_contract_id": ms.msp.id, "agent_id": "AGT-BARE-1"}
    )
    assert bare.display_name == "AGT-BARE-1"

    # healthy asset with one open alert: 100 - 5
    env["fix.msp.alert"].create(
        {
            "msp_contract_id": ms.msp.id,
            "asset_id": ms.asset.id,
            "severity": "minor",
            "message": "flap",
            "state": "new",
        }
    )
    ms.asset.invalidate_recordset()
    assert ms.asset.open_alert_count == 1
    assert ms.asset.health_score == 95
    # degraded floor: 50 - 3 alerts = 35
    for i in range(2):
        env["fix.msp.alert"].create(
            {
                "msp_contract_id": ms.msp.id,
                "asset_id": ms.asset.id,
                "severity": "minor",
                "message": "flap %s" % i,
                "state": "new",
            }
        )
    ms.asset.write({"health": "degraded"})
    ms.asset.invalidate_recordset()
    assert ms.asset.health_score == 35


def test_contract_monthly_value_and_alert_escalation(ms):
    env = ms.env
    assert ms.msp.monthly_value == 10000.0  # 4 devices x 2500
    alert = env["fix.msp.alert"].create(
        {
            "msp_contract_id": ms.msp.id,
            "asset_id": ms.asset.id,
            "severity": "major",
            "message": "down",
            "state": "new",
        }
    )
    alert.action_escalate()
    assert alert.escalated and alert.escalated_at
    events = _events(env, "fix.msp.alert", alert.id)
    assert "msp.alert_escalated" in events.mapped("event_type")
    with pytest.raises(UserError):
        alert.action_escalate()


def test_service_report_attainment_pct(ms):
    env = ms.env
    report = env["fix.msp.service.report"].create(
        {
            "msp_contract_id": ms.msp.id,
            "period_label": "2026-07",
            "alert_count": 3,
            "resolved_count": 2,
            "sla_attainment": 0.6667,
            "operating_unit_id": ms.ou.id,
        }
    )
    assert report.sla_attainment_pct == 66.7


# ------------------------------------------------- controller surfaces


def test_m05_controller_surfaces_cover_engines():
    from odoo.addons.cd_p03_portal.controllers.a02 import m05 as m05_controller

    for model in (
        "fix.msp.contract",
        "fix.msp.runbook",
        "fix.msp.runbook.run",
        "fix.msp.patch.policy",
        "fix.msp.patch.update",
        "fix.msp.sla.credit",
        "fix.msp.oncall.shift",
        "fix.msp.maintenance.window",
        "fix.msp.change.record",
    ):
        assert model in m05_controller.SURFACES, model
    assert "action_compute_sla_credits" in m05_controller.SURFACES["fix.msp.contract"]["actions"]
    assert "action_execute" in m05_controller.SURFACES["fix.msp.runbook"]["actions"]
    assert "action_escalate" in m05_controller.SURFACES["fix.msp.alert"]["actions"]
    for report in ("estate_health", "patch_compliance", "sla_credit_register"):
        assert report in m05_controller.REPORTS
