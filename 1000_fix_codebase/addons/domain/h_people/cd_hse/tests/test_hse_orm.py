# cd_hse live-ORM tests — P09-M08 / R07-M05 (CD-M59-01): the shape of the BLA
# 2006 s.90 / BLR 2015 r.73 register entry an incident opens. The workflow,
# approval and access controls are proved as non-admin users in
# test_a09_hse_controls.py (A09 audit B6); the superuser-only workflow tests
# that used to live here were replaced by it.
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


def test_minor_incident_is_reported_and_opens_the_register_but_a_near_miss_does_not(ctx):
    # BLA s.80(2) / BLR r.73(1): EVERY accident — a low-severity injury
    # included — has a Form 28 entry opened at report; a near miss has none.
    incident = _incident(ctx, incident_type="injury", severity="low", employee_id=ctx.reporter.id)
    assert incident.name.startswith("HSE/")  # sequenced since the M59 rebuild
    assert incident.state == "reported"
    assert incident.statutory_record_id
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


# --- inspections, committee, PPE ---------------------------------------------------


# --- s.80 closure gate and register dating (A09 zero-trust re-audit 2026-10-30)
# These exercise the gate instead of asserting that an identifier appears in
# the source of action_close(): the previous source-text check passed while the
# gate was keyed on a "BLOCK_WITHOUT_DIFE" sentinel no record ever carried.


def test_register_records_the_date_the_accident_happened(ctx):
    """A late-keyed accident must not be filed under the keying date: the
    Form 28 serial and the half-yearly return both hang off this date."""
    accident = fields.Datetime.to_datetime("2026-10-20 09:30:00")
    incident = _incident(
        ctx,
        incident_type="injury",
        severity="medium",
        employee_id=ctx.reporter.id,
        injured_employee_id=ctx.injured.id,
        accident_datetime=accident,
    )
    register = incident.statutory_record_id
    assert register.accident_date == accident.date()
    # Jan-Jun accident -> 15 Jul; Jul-Dec -> 15 Jan of the following year
    assert str(register.half_year_return_due) == "2027-01-15"


def test_register_entry_carries_a_form_28_serial(ctx):
    """BLR 2015 r.73: the register is serially numbered. Every entry used to
    carry the literal default "New"."""
    ctx.env["ir.sequence"].create(
        {
            "name": "F28",
            "code": "fix.statutory.accident.register",
            "prefix": "F28/2026/",
            "padding": 4,
        }
    )
    incident = _incident(
        ctx,
        incident_type="injury",
        severity="medium",
        employee_id=ctx.reporter.id,
        injured_employee_id=ctx.injured.id,
    )
    assert incident.statutory_record_id.register_entry_no == "F28/2026/0001"
