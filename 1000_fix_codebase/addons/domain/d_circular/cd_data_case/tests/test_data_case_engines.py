"""M06 iteration-2 engine tests: attempts, sealed media, cleanroom,
evaluations, quotations, backup plans & restore tests, case wrappers and
the controller surface map.

``odoo_env`` (addons/conftest.py): fix_test, rolled back after every test.
"""

from datetime import timedelta
from unittest.mock import patch

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
    ds.case.write({"state": "recovering"})  # A02 M06-5: attempts are logged in recovery
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
    ds.case.write({"state": "recovering"})
    attempt = env["fix.data.recovery.attempt"].create(
        {"case_id": ds.case.id, "method": "firmware_repair"}
    )
    with pytest.raises(UserError):
        attempt.action_finish()  # outcome still in_progress


# ------------------------------------------------------------- sealed media


def _witness(env, n="1"):
    return env["res.users"].create(
        {"name": "M06 Seal Witness %s" % n, "login": "m06-engines-witness-%s" % n}
    )


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
    unit.action_break_seal(handler="Cleanroom Lead", witness_user_id=_witness(env).id)
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
    with pytest.raises(UserError, match="second witness"):
        unit.action_break_seal()  # A02 M06-5: never without a witness
    unit.action_break_seal(witness_user_id=_witness(env).id)
    with pytest.raises(UserError):
        unit.action_break_seal(witness_user_id=_witness(env, "2").id)  # double break refused
    with pytest.raises(IntegrityError):
        env["fix.data.media.unit"].create(
            {"case_id": ds.case.id, "seal_number": "BAG-M06-002"}
        )  # unique seal constraint


def test_media_unit_return(ds):
    env = ds.env
    unit = env["fix.data.media.unit"].create({"case_id": ds.case.id, "seal_number": "BAG-M06-003"})
    # A02 ERP audit M06-F10: media goes back once the case allows it
    with pytest.raises(UserError, match="stays in custody"):
        unit.action_return()
    ds.case._guarded().write({"state": "unrecoverable"})
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
    # A02 audit M06-P2: a quotation prices a completed evaluation
    env["fix.data.evaluation"].create(
        {"case_id": ds.case.id, "verdict": "recoverable"}
    ).action_complete()
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
    quote.action_accept(acceptance_reference="OTP-771204")  # A02 M06-4: the customer's artefact
    assert quote.state == "accepted"
    events = _events(env, "fix.data.quote", quote.id).mapped("event_type")
    assert "data_case.quote_sent" in events and "data_case.quote_accepted" in events

    # A02 ERP audit M06-F5: one live quotation per case; the expiry is shown
    # on a quotation of its own case
    other = env["fix.data.recovery.case"].create(
        {"customer_id": ds.customer.id, "media_type": "hdd"}
    )
    env["fix.data.evaluation"].create(
        {"case_id": other.id, "verdict": "recoverable"}
    ).action_complete()
    stale = env["fix.data.quote"].create(
        {
            "case_id": other.id,
            "amount": 100.0,
            "valid_until": fields.Date.today() - timedelta(days=1),
        }
    )
    stale.action_send()
    with pytest.raises(UserError, match="expired"):
        stale.action_accept(acceptance_reference="OTP-771205")  # expired


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
    # M06 capture pass 2: a passed restore test carries its evidence
    with pytest.raises(UserError, match="evidence"):
        plan.action_log_test(result="passed", restored_gb=120.5, notes="no proof")
    evidence = env["ir.attachment"].create({"name": "restore.pdf", "raw": b"%PDF ok"})
    plan.action_log_test(
        result="passed",
        restored_gb=120.5,
        notes="full restore ok",
        evidence_attachment_id=evidence.id,
    )
    plan.invalidate_recordset()
    assert plan.last_test_result == "passed"
    assert plan.next_test_due == fields.Date.context_today(plan) + timedelta(days=30)
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
    ds.case.action_route_to_z4()
    env["fix.data.evaluation"].create(
        {"case_id": ds.case.id, "verdict": "recoverable"}
    ).action_complete()
    quote = env["fix.data.quote"].create({"case_id": ds.case.id, "amount": 5000})
    quote.action_send()
    quote.action_accept(acceptance_reference="PORTAL-55120")
    ds.case.action_start_recovery()
    assert ds.case.state == "recovering"
    env["fix.data.recovery.attempt"].create(
        {"case_id": ds.case.id, "method": "software_scan"}
    ).action_finish(outcome="success")
    image = "cd" * 32
    ds.case.action_record_image(hashes="%s %s" % (image, image))
    ds.case.action_verify_image(recomputed_hash=image)
    ds.case.action_recovered()
    ds.customer.phone = "01711000555"
    ds.case.write({"handover_recipient_id": ds.customer.id, "encrypted_target_serial": "T-1"})
    ds.case.action_confirm_target_serial(" t-1 ")
    env["ir.attachment"].create(
        {"name": "Receipt.pdf", "raw": b"%PDF", "res_model": ds.case._name, "res_id": ds.case.id}
    )
    sent = {}

    def _send(self, recipient, phone, code):
        sent["code"] = code
        return {"destination": "017*****555"}

    with patch.object(type(ds.case), "_handover_send_code", _send):
        ds.case.action_request_handover_otp()
    ds.case.action_waive_charge(note="test: the hand-over path, charge waived")  # M06-F1
    ds.case.action_handover("Data Lead", verification=sent["code"])
    assert ds.case.state == "handover"
    assert ds.case.retention_until and ds.case.handover_verification_method == "otp"
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
