"""cd_ewaste behaviour (live ORM, rolled back): Journey 10 e-waste lifecycle
collection -> triage -> secure destruction -> recycling -> certificate,
plus the ESG metric unit derivation."""

from __future__ import annotations

import json

import pytest
from odoo import fields
from odoo.exceptions import UserError

EW = "fix.ewaste.collection"


def _events(env, event_type, res_id):
    rows = env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate", "=", EW), ("aggregate_id", "=", res_id)],
        order="id",
    )
    return [json.loads(r.payload) for r in rows]


def _collection(env, **vals):
    vals.setdefault("customer_id", env["res.partner"].create({"name": "E-Waste Donor"}).id)
    return env[EW].create(vals)


def _in(env, state, **vals):
    rec = _collection(env, **vals)
    rec.write({"state": state})
    return rec


def _verified_destruction_cert(env):
    """The destruction operator's M06 certificate, evidence attached and verified."""
    log = env["ir.attachment"].create({"name": "shred.log", "raw": b"shredder run 42: PASS"})
    cert = env["fix.data.wipe.certificate"].create(
        {"method": "physical_destruction", "wipe_log_attachment_id": log.id}
    )
    cert.action_verify()
    return cert


def test_collection_named_and_published_on_create(odoo_env):
    recs = odoo_env[EW].create(
        [
            {"customer_id": odoo_env["res.partner"].create({"name": "Donor A"}).id},
            {
                "customer_id": odoo_env["res.partner"].create({"name": "Donor B"}).id,
                "material_type": "battery",
            },
        ]
    )
    # the module ships the collection sequence (data/ir_sequence.xml): new
    # collections are numbered, never left as the "EW/New" placeholder
    assert all(name.startswith("EW/") and name != "EW/New" for name in recs.mapped("name"))
    assert len(set(recs.mapped("name"))) == 2
    assert recs.mapped("state") == ["collected", "collected"]
    assert _events(odoo_env, "ewaste.collected", recs[0].id) == [
        {"customer": "Donor A", "type": "phone"}
    ]
    assert _events(odoo_env, "ewaste.collected", recs[1].id) == [
        {"customer": "Donor B", "type": "battery"}
    ]


def test_collection_name_from_sequence(odoo_env):
    odoo_env["ir.sequence"].create({"name": "EW test", "code": EW, "prefix": "EW/T/"})
    assert _collection(odoo_env).name.startswith("EW/T/")


def test_triage_only_from_collected(odoo_env):
    rec = _in(odoo_env, "triaged")
    with pytest.raises(UserError, match="Triage from collected"):
        rec.action_triage("reuse")


def test_triage_sets_grade_and_publishes(odoo_env):
    rec = _collection(odoo_env)
    rec.action_triage("hazardous")
    assert rec.state == "triaged"
    assert rec.triage_grade == "hazardous"
    assert _events(odoo_env, "ewaste.triaged", rec.id) == [{"grade": "hazardous"}]


def test_destruction_only_from_triaged(odoo_env):
    rec = _collection(odoo_env)
    with pytest.raises(UserError, match="Destruction from triaged"):
        rec.action_secure_destruction()
    assert not rec.wipe_certificate_id


def test_destruction_issues_wipe_certificate_when_missing(odoo_env):
    rec = _in(odoo_env, "triaged")
    rec.action_secure_destruction()
    assert rec.state == "destruction"
    assert rec.wipe_certificate_id.method == "physical_destruction"
    assert rec.wipe_certificate_id.statutory_record_retained is True
    assert _events(odoo_env, "ewaste.destruction_started", rec.id) == [{}]


def test_destruction_reuses_existing_wipe_certificate(odoo_env):
    cert = odoo_env["fix.data.wipe.certificate"].create({"method": "nist_800_88_purge"})
    rec = _in(odoo_env, "triaged", wipe_certificate_id=cert.id)
    before = odoo_env["fix.data.wipe.certificate"].search_count([])
    rec.action_secure_destruction()
    assert rec.state == "destruction"
    assert rec.wipe_certificate_id == cert
    assert odoo_env["fix.data.wipe.certificate"].search_count([]) == before
    assert _events(odoo_env, "ewaste.destruction_started", rec.id) == [{}]


def test_recycle_only_from_destruction(odoo_env):
    rec = _in(odoo_env, "triaged")
    with pytest.raises(UserError, match="Recycle from destruction"):
        rec.action_recycle(3.0)
    assert rec.esg_co2_saved_kg == 0.0


def test_recycle_records_co2(odoo_env):
    rec = _in(odoo_env, "destruction", wipe_certificate_id=_verified_destruction_cert(odoo_env).id)
    rec.action_recycle(12.5)
    assert rec.state == "recycled"
    assert rec.esg_co2_saved_kg == 12.5


def test_certificate_only_from_recycled(odoo_env):
    rec = _in(odoo_env, "destruction")
    with pytest.raises(UserError, match="Certificate from recycled"):
        rec.action_issue_certificate()
    assert not rec.disposal_certificate_ref


def test_full_journey_ends_with_disposal_certificate(odoo_env):
    rec = _collection(odoo_env, material_type="laptop", weight_kg=2.4)
    rec.action_triage("recycle")
    rec.action_secure_destruction()
    # destruction opens a pending certificate; the operator's evidence is
    # verified before the device may leave for recycling
    cert = rec.wipe_certificate_id
    assert cert.sanitization_status == "pending_verification"
    with pytest.raises(UserError, match="verified M06 destruction certificate"):
        rec.action_recycle(7.25)
    rec.wipe_certificate_id = _verified_destruction_cert(odoo_env)
    rec.action_recycle(7.25)
    rec.action_issue_certificate()
    expected_ref = "DISPOSE/%s/%s" % (fields.Date.today().strftime("%Y%m"), rec.name)
    assert rec.state == "certified"
    assert rec.disposal_certificate_ref == expected_ref
    assert _events(odoo_env, "ewaste.certificate_issued", rec.id) == [
        {"certificate": expected_ref, "co2_saved": 7.25}
    ]


@pytest.mark.parametrize(
    ("metric_type", "unit"),
    [
        ("co2_saved", "kg"),
        ("ewaste_collected", "kg"),
        ("devices_refurbished", "count"),
        ("energy_saved", "kWh"),
    ],
)
def test_esg_metric_unit_follows_type(odoo_env, metric_type, unit):
    # stored compute: the unit is set on create too, not only by the web form
    metric = odoo_env["fix.esg.metric"].create(
        {"name": "Q", "period": "2026-10", "value": 1.0, "metric_type": metric_type}
    )
    assert metric.unit == unit
