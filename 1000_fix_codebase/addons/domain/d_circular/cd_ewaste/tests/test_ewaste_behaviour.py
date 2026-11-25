"""cd_ewaste behaviour (live ORM, rolled back): Journey 10 e-waste lifecycle
collection -> triage -> secure destruction -> recycling -> certificate,
plus the ESG metric unit derivation.

A05 audit M18-18: these tests used to forge the state they started from
(rec.write({"state": ...})). Every item now reaches its state through the
real transitions; the superuser runs them (trusted code), the role and
segregation-of-duties checks are proved as non-admin users in
test_a05_m18_controls.py."""

from __future__ import annotations

import json

import pytest
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
    """A collection taken to `state` through its real transitions."""
    rec = _collection(env, **vals)
    if state == "collected":
        return rec
    rec.action_triage("recycle")
    if state == "triaged":
        return rec
    rec.action_secure_destruction()
    return rec


def _verified_destruction_cert(env, rec):
    """The destruction operator's M06 certificate, evidence attached and verified,
    bound to the item it certifies (A02 audit M06-1: here the collection) and
    answering the collection's own wipe request (A02 pass 2 review N2)."""
    serial = rec.name
    log = env["ir.attachment"].create({"name": "shred.log", "raw": b"shredder run 42: PASS"})
    photo = env["ir.attachment"].create({"name": "shredded.jpg", "raw": b"shredded media"})
    cert = env["fix.data.wipe.certificate"].create(
        {
            "method": "physical_destruction",
            "wipe_request_id": rec._m18_wipe_request().id,
            "media_kind": "flash",
            "wipe_log_attachment_id": log.id,
            "destruction_photo_attachment_id": photo.id,
        }
    )
    # D16 (A02 pass 2): a second person of the data lab witnessed it
    witness = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Destruction witness %s" % serial,
                "login": "ew.witness.%s@a05.test" % serial.lower(),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id,
                            env.ref("cd_data_case.group_data_recovery_operator").id])
                ],
            }
        )
    )  # fmt: skip
    cert.with_user(witness).action_witness_destruction()
    cert.action_verify()
    return cert


def _destroyed_with_verified_cert(env, **vals):
    rec = _in(env, "triaged", **vals)
    rec.write({"wipe_certificate_id": _verified_destruction_cert(env, rec).id})
    rec.action_secure_destruction()
    return rec


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
    rec.action_triage("recycle")
    assert rec.state == "triaged"
    assert rec.triage_grade == "recycle"
    assert rec.triage_id.decision == "recycle"
    assert _events(odoo_env, "ewaste.triaged", rec.id) == [{"grade": "recycle"}]


def test_hazardous_triage_routes_to_hazmat_stream(odoo_env):
    # A05 audit B4: the grade routes the item; a hazardous one never goes
    # down the shredder path
    rec = _collection(odoo_env, material_type="battery", weight_kg=0.4)
    rec.action_triage("hazardous")
    assert rec.state == "hazmat"
    assert rec.triage_grade == "hazardous"
    assert len(rec.battery_ids) == 1
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
    rec = _in(odoo_env, "triaged")
    rec.write({"wipe_certificate_id": cert.id})
    before = odoo_env["fix.data.wipe.certificate"].search_count([])
    rec.action_secure_destruction()
    assert rec.state == "destruction"
    assert rec.wipe_certificate_id == cert
    assert odoo_env["fix.data.wipe.certificate"].search_count([]) == before
    assert _events(odoo_env, "ewaste.destruction_started", rec.id) == [{}]


def test_recycle_only_from_destruction(odoo_env):
    rec = _in(odoo_env, "triaged")
    with pytest.raises(UserError, match="Recycle from destruction"):
        rec.action_recycle()
    assert rec.esg_co2_saved_kg == 0.0


def test_recycle_computes_co2_from_weight(odoo_env):
    # A05 audit M18-5: CO2 avoided is weight x the versioned factor, never typed
    rec = _destroyed_with_verified_cert(odoo_env, weight_kg=2.0, material_type="laptop")
    with pytest.raises(UserError, match="cannot be typed"):
        rec.action_recycle(12.5)
    rec.action_recycle()
    assert rec.state == "recycled"
    assert rec.esg_co2_saved_kg == 3.0
    assert rec.co2_factor_version


def test_certificate_only_from_recycled(odoo_env):
    rec = _in(odoo_env, "destruction")
    with pytest.raises(UserError, match="Certificate from recycled"):
        rec.action_issue_certificate()
    assert not rec.disposal_certificate_ref


def test_certificate_needs_a_processed_recycler_batch(odoo_env):
    # A05 audit M18-10: the certificate is the recycler's, not a string
    rec = _destroyed_with_verified_cert(odoo_env, weight_kg=2.4, material_type="laptop")
    rec.action_recycle()
    with pytest.raises(UserError, match="no processed recycler batch"):
        rec.action_issue_certificate()
    assert rec.state == "recycled"
    assert not rec.disposal_certificate_ref


def test_full_journey_pending_wipe_blocks_recycle(odoo_env):
    rec = _collection(odoo_env, material_type="laptop", weight_kg=2.4)
    rec.action_triage("recycle")
    rec.action_secure_destruction()
    # destruction opens a pending certificate; the operator's evidence is
    # verified before the device may leave for recycling
    cert = rec.wipe_certificate_id
    assert cert.sanitization_status == "pending_verification"
    with pytest.raises(UserError, match="verified M06 destruction certificate"):
        rec.action_recycle()
    # the gate is in the state change itself: even trusted code cannot write it
    with pytest.raises(UserError, match="verified M06 destruction certificate"):
        rec.write({"state": "recycled"})
    assert rec.state == "destruction"


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
    # (trusted code; users cannot create a metric at all - BRU-ESG-11)
    metric = odoo_env["fix.esg.metric"].create(
        {"name": "Q", "period": "2026-10", "value": 1.0, "metric_type": metric_type}
    )
    assert metric.unit == unit
