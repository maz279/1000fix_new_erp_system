"""M06 iteration-2 engine tests: attempts, sealed media, cleanroom,
evaluations, quotations, backup plans & restore tests, case wrappers and
the controller surface map.

``odoo_env`` (addons/conftest.py): fix_test, rolled back after every test.
"""

from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import UserError
from psycopg2 import IntegrityError


@pytest.fixture
def ds(odoo_env):
    env = odoo_env
    customer = env["res.partner"].create({"name": "M06 Engines Customer"})
    case = env["fix.data.recovery.case"].create(
        {
            "customer_id": customer.id,
            "media_type": "hdd",
            "specialism": "logical_recovery",
        }
    )
    from types import SimpleNamespace

    return SimpleNamespace(env=env, customer=customer, case=case)


def _events(env, aggregate, res_id):
    rows = env["fix.event.outbox"].search(
        [("aggregate", "=", aggregate), ("aggregate_id", "=", res_id)], order="id"
    )
    return rows


# ---------------------------------------------------------------- attempts


def test_attempt_lifecycle_and_guards(ds):
    env = ds.env
    attempt = env["fix.data.recovery.attempt"].create(
        {"case_id": ds.case.id, "method": "software_scan"}
    )
    assert attempt.outcome == "in_progress"
    attempt.action_finish(outcome="partial", notes="deep scan salvaged user folders")
    assert attempt.outcome == "partial" and attempt.finished_at
    assert "data_case.attempt_finished" in _events(
        env, "fix.data.recovery.attempt", attempt.id
    ).mapped("event_type")
    with pytest.raises(UserError):
        attempt.action_finish(outcome="success")  # already finished
    ds.case.invalidate_recordset()
    assert ds.case.attempt_count == 1


def test_attempt_finish_requires_outcome(ds):
    env = ds.env
    attempt = env["fix.data.recovery.attempt"].create(
        {"case_id": ds.case.id, "method": "head_swap"}
    )
    with pytest.raises(UserError):
        attempt.action_finish()  # outcome still in_progress


# ------------------------------------------------------------- sealed media


def test_media_unit_seal_transfer_and_chain(ds):
    env = ds.env
    unit = env["fix.data.media.unit"].create(
        {
            "case_id": ds.case.id,
            "seal_number": "BAG-M06-001",
            "media_label": "Seagate 2TB",
        }
    )
    assert unit.location == "reception" and unit.seal_state == "sealed"
    unit.action_transfer(location="z4_lab", handler="Nadia")
    ds.case.invalidate_recordset()
    assert "[Media BAG-M06-001] moved to Z4 Lab by Nadia" in ds.case.custody_chain
    assert unit.location == "z4_lab"
    unit.action_break_seal(handler="Cleanroom Lead")
    assert unit.seal_state == "opened_in_lab"
    assert "seal broken by Cleanroom Lead" in ds.case.custody_chain
    assert "data_case.media_seal_broken" in _events(env, "fix.data.media.unit", unit.id).mapped(
        "event_type"
    )


def test_media_unit_guards(ds):
    env = ds.env
    unit = env["fix.data.media.unit"].create({"case_id": ds.case.id, "seal_number": "BAG-M06-002"})
    with pytest.raises(UserError):
        unit.action_transfer(location="destroyed")  # destruction is certified, not moved
    unit.action_break_seal()
    with pytest.raises(UserError):
        unit.action_break_seal()  # double break refused
    with pytest.raises(IntegrityError):
        env["fix.data.media.unit"].create(
            {"case_id": ds.case.id, "seal_number": "BAG-M06-002"}
        )  # unique seal constraint


def test_media_unit_return(ds):
    env = ds.env
    unit = env["fix.data.media.unit"].create({"case_id": ds.case.id, "seal_number": "BAG-M06-003"})
    unit.action_return()
    assert unit.location == "returned_to_customer"
    assert "data_case.media_returned" in _events(env, "fix.data.media.unit", unit.id).mapped(
        "event_type"
    )


# ---------------------------------------------------------------- cleanroom


def test_cleanroom_slot_lifecycle(ds):
    env = ds.env
    tech = env["hr.employee"].create({"name": "M06 Cleanroom Tech"})
    now = fields.Datetime.now()
    slot = env["fix.data.cleanroom.slot"].create(
        {
            "case_id": ds.case.id,
            "technician_id": tech.id,
            "purpose": "head_swap",
            "iso_class": "iso_5",
            "start_at": now + timedelta(hours=1),
            "end_at": now + timedelta(hours=4),
        }
    )
    slot.action_use()
    assert slot.state == "used"
    assert "data_case.cleanroom_slot_used" in _events(
        env, "fix.data.cleanroom.slot", slot.id
    ).mapped("event_type")
    with pytest.raises(UserError):
        slot.action_cancel()  # only planned cancels
    with pytest.raises(UserError, match="must end after it starts"):
        env["fix.data.cleanroom.slot"].create(
            {"purpose": "inspection", "start_at": now, "end_at": now - timedelta(hours=1)}
        )  # end before start


# -------------------------------------------------------------- evaluation


def test_evaluation_turnaround_and_specialism_routing(ds):
    env = ds.env
    ev = env["fix.data.evaluation"].create(
        {
            "case_id": ds.case.id,
            "verdict": "recoverable",
            "recoverability_pct": 85,
            "recommended_specialism": "hardware_repair",
        }
    )
    ev.action_complete(notes="head click, donor needed")
    assert ev.evaluated_at and ev.eval_hours >= 0.0
    assert "data_case.evaluated" in _events(env, "fix.data.evaluation", ev.id).mapped("event_type")
    ds.case.invalidate_recordset()
    assert ds.case.specialism == "hardware_repair", "recommended specialism routes the case"
    with pytest.raises(UserError):
        ev.action_complete()  # already completed


def test_evaluation_requires_verdict(ds):
    env = ds.env
    ev = env["fix.data.evaluation"].create({"case_id": ds.case.id})
    with pytest.raises(UserError):
        ev.action_complete()


# ------------------------------------------------------------------ quotes


def test_quote_lifecycle_and_expiry_guard(ds):
    env = ds.env
    quote = env["fix.data.quote"].create(
        {
            "case_id": ds.case.id,
            "amount": 15000.0,
            "description": "Donor head + imaging",
            "valid_until": fields.Date.today() + timedelta(days=14),
        }
    )
    assert quote.name  # sequence or DRQ/New fallback
    with pytest.raises(UserError):
        quote.action_accept()  # must be sent first
    quote.action_send()
    assert quote.state == "sent"
    quote.action_accept()
    assert quote.state == "accepted"
    events = _events(env, "fix.data.quote", quote.id).mapped("event_type")
    assert "data_case.quote_sent" in events and "data_case.quote_accepted" in events

    stale = env["fix.data.quote"].create(
        {
            "case_id": ds.case.id,
            "amount": 100.0,
            "valid_until": fields.Date.today() - timedelta(days=1),
        }
    )
    stale.action_send()
    with pytest.raises(UserError):
        stale.action_accept()  # expired


# ------------------------------------------------------------------ backup


def test_backup_plan_test_log_and_compliance(ds):
    env = ds.env
    plan = env["fix.data.backup.plan"].create(
        {
            "name": "3-2-1 office plan",
            "customer_id": ds.customer.id,
            "plan_type": "rule_321",
            "rpo_hours": 24,
            "rto_hours": 8,
            "test_frequency_days": 30,
        }
    )
    assert not plan.compliant  # never tested
    plan.action_log_test(result="passed", restored_gb=120.5, notes="full restore ok")
    plan.invalidate_recordset()
    assert plan.last_test_result == "passed"
    assert plan.next_test_due == fields.Date.today() + timedelta(days=30)
    assert plan.compliant
    assert "data_case.backup_test_logged" in _events(env, "fix.data.backup.plan", plan.id).mapped(
        "event_type"
    )

    plan.action_log_test(result="failed", restored_gb=0.0, notes="catalog corrupt")
    plan.invalidate_recordset()
    assert not plan.compliant

    with pytest.raises(UserError):
        plan.action_log_test(result="excellent")  # fail closed on unknown result


# ----------------------------------------------------- case journey wrappers


def test_case_journey_with_new_engines(ds):
    env = ds.env
    ds.case.action_take_custody("Front Desk")
    with pytest.raises(UserError):
        ds.case.action_start_recovery()  # SC-007: not routed to Z4 yet
    ds.case.write({"residency_zone": "z4"})
    ds.case.action_start_recovery()
    assert ds.case.state == "recovering"
    env["fix.data.recovery.attempt"].create(
        {
            "case_id": ds.case.id,
            "method": "software_scan",
            "outcome": "success",
            "finished_at": fields.Datetime.now(),
        }
    )
    ds.case.action_recovered()
    ds.case.action_handover("Data Lead")
    assert ds.case.state == "handover"
    with pytest.raises(UserError):
        ds.case.action_purge()  # no verified certificate yet


def test_case_button_wrappers_use_current_user(ds):
    ds.case.action_take_custody_me()
    assert "custody taken by" in ds.case.custody_chain
    ds.case.action_transfer_me()
    assert "Custody Transfer" in ds.case.custody_chain


def test_sequence_names_now_generated(ds):
    case2 = ds.env["fix.data.recovery.case"].create(
        {"customer_id": ds.customer.id, "media_type": "ssd"}
    )
    assert case2.name.startswith("DRC/"), "sequence data must name cases DRC/…"


# ------------------------------------------------- controller surfaces


def test_m06_controller_surfaces_cover_engines():
    from odoo.addons.cd_p03_portal.controllers.a02 import m06 as m06_controller

    for model in (
        "fix.data.recovery.case",
        "fix.data.wipe.certificate",
        "fix.z4.access.audit",
        "fix.data.recovery.attempt",
        "fix.data.media.unit",
        "fix.data.cleanroom.slot",
        "fix.data.evaluation",
        "fix.data.quote",
        "fix.data.backup.plan",
    ):
        assert model in m06_controller.SURFACES, model
    assert (
        "action_access_recovered_data"
        in m06_controller.SURFACES["fix.data.recovery.case"]["actions"]
    )
    assert "action_verify" in m06_controller.SURFACES["fix.data.wipe.certificate"]["actions"]
    for report in (
        "recovery_success_by_specialism",
        "case_cycle_time",
        "data_service_revenue",
        "destruction_purge_audit",
        "backup_restore_compliance",
        "recovered_inventory",
    ):
        assert report in m06_controller.REPORTS
