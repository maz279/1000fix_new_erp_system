# cd_hse live-ORM tests — P09-M08 / R07-M05 (CD-M59-01): BLA 2006 s.89/s.90A,
# BLR 2015 rules 80/81 (Form 33/34 accident register, DIFE notice).
import json
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
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    entity = env["fix.entity"].create(
        {"code": "HSET", "legal_name": "HSE Test Ltd", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {"code": "HS1", "name": "Tejgaon Depot", "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    Employee = env["hr.employee"]
    return SimpleNamespace(
        env=env,
        ou=ou,
        branch=branch,
        reporter=Employee.create({"name": "Supervisor Hasan"}),
        injured=Employee.create({"name": "Technician Rina"}),
        today=fields.Date.today(),
    )


def _incident(ctx, **vals):
    base = {"description": "Burn from rework station", "branch_id": ctx.branch.id}
    base.update(vals)
    return ctx.env["fix.hse.incident"].create(base)


# --- incidents and the automatic statutory register -------------------------------


def test_minor_incident_is_reported_without_register(ctx):
    incident = _incident(ctx, incident_type="injury", severity="low", employee_id=ctx.reporter.id)
    assert incident.name == "HSE/New"  # no sequence configured for the code
    assert incident.state == "reported"
    assert not incident.statutory_record_id
    assert _events(ctx.env, "hse.incident_reported", incident.id) == [
        {"type": "injury", "severity": "low"}
    ]
    # a high-severity near miss is not an accident either
    assert not _incident(ctx, incident_type="near_miss", severity="high").statutory_record_id


def test_incident_reference_from_sequence(ctx):
    ctx.env["ir.sequence"].create(
        {"name": "HSE", "code": "fix.hse.incident", "prefix": "HSE/", "padding": 4}
    )
    assert _incident(ctx).name == "HSE/0001"


def test_serious_injury_opens_the_accident_register(ctx):
    incident = _incident(
        ctx,
        incident_type="injury",
        severity="medium",
        employee_id=ctx.reporter.id,
        injured_employee_id=ctx.injured.id,
    )
    reg = incident.statutory_record_id
    assert reg.name == f"BLA-Accident: {incident.name}"
    assert reg.incident_id == incident
    assert reg.employee_id == ctx.injured  # the injured worker, not the reporter
    assert reg.company_id == incident.company_id
    assert not reg.operating_unit_id
    assert reg.accident_date == ctx.today
    assert reg.nature_of_injury == "Burn from rework station"
    assert reg.state == "recorded"


def test_battery_thermal_event_falls_back_to_the_reporter(ctx):
    incident = _incident(
        ctx,
        incident_type="battery_thermal",
        severity="high",
        employee_id=ctx.reporter.id,
        operating_unit_id=ctx.ou.id,
    )
    reg = incident.statutory_record_id
    assert reg.employee_id == ctx.reporter
    assert reg.operating_unit_id == ctx.ou


def test_serious_injury_without_any_worker_is_refused(ctx):
    """Regression: used to die on the register's NOT NULL worker column."""
    with (
        pytest.raises(UserError, match="high-severity injury must name the injured worker"),
        ctx.env.cr.savepoint(),
    ):
        _incident(ctx, incident_type="injury", severity="high")


def test_incident_workflow(ctx):
    incident = _incident(ctx)
    incident.action_investigate()
    assert incident.state == "investigating"
    incident.action_close()
    assert incident.state == "closed"


def test_dife_notification(ctx):
    incident = _incident(
        ctx, incident_type="injury", severity="high", injured_employee_id=ctx.injured.id
    )
    reg = incident.statutory_record_id
    reg.action_notify_dife()
    assert (reg.dife_notified, reg.dife_notification_date, reg.state) == (
        True,
        ctx.today,
        "dife_notified",
    )
    assert _events(ctx.env, "hse.dife_accident_reported", reg.id) == [
        {"worker": "Technician Rina", "date": str(ctx.today)}
    ]


# --- inspections, committee, PPE ---------------------------------------------------


def test_inspection_outcome(ctx):
    Inspection = ctx.env["fix.safety.inspection"]
    clean = Inspection.create({"name": "Q1", "branch_id": ctx.branch.id})
    clean.action_complete()
    assert clean.state == "done"
    for check in ("fire_extinguisher_ok", "esd_grounding_ok", "chemical_storage_ok"):
        failing = Inspection.create({"name": "Q2", "branch_id": ctx.branch.id, check: False})
        failing.action_complete()
        assert failing.state == "follow_up", check


def test_safety_committee_meeting(ctx):
    committee = ctx.env["fix.safety.committee"].create(
        {
            "name": "Tejgaon Safety Committee",
            "branch_id": ctx.branch.id,
            "chairperson_id": ctx.reporter.id,
            "secretary_id": ctx.injured.id,
        }
    )
    committee.action_record_meeting("Fire drill reviewed; extinguishers replaced.")
    assert committee.last_meeting_date == ctx.today
    assert committee.recent_minutes == "Fire drill reviewed; extinguishers replaced."
    committee.action_record_meeting()  # no minutes: keeps the last ones
    assert committee.recent_minutes == "Fire drill reviewed; extinguishers replaced."
    assert (
        _events(ctx.env, "hse.safety_committee_meeting", committee.id)
        == [{"committee": "Tejgaon Safety Committee", "branch": "Tejgaon Depot"}] * 2
    )


def test_ppe_replenishment_threshold(ctx):
    PPE = ctx.env["fix.ppe.register"]
    at_minimum = PPE.create(
        {"name": "Wristbands", "stock_quantity": 10, "min_required_quantity": 10}
    )
    above = PPE.create({"name": "Goggles", "stock_quantity": 11, "min_required_quantity": 10})
    (at_minimum | above).check_replenishment()
    assert (at_minimum.state, above.state) == ("replenish", "compliant")


def test_hazardous_substance_defaults(ctx):
    ipa = ctx.env["fix.hazardous.substance.register"].create(
        {"name": "Isopropyl alcohol", "un_number": "UN 1219", "storage_location": "Cabinet A"}
    )
    assert (ipa.max_allowable_litres, ipa.current_stock_litres, ipa.state) == (50.0, 15.0, "safe")
    assert ipa.msds_on_file is True
