"""A07 P0 (2026-11-03) M48-1 / M48-6 / M48-7 / M48-8: telemetry consent at
ingest, guarded telemetry writes, final revocation, and the M48 P03 figures.

Attacks run as NON-ADMIN users created in the rolled-back transaction
(base.group_user + an operating unit); each refusal is paired with the proper
path still working."""

from __future__ import annotations

import importlib
import types
import uuid
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

TAG = uuid.uuid4().hex[:6].upper()
REFUSED = (UserError, ValidationError, AccessError)
PARAM = "cd_stream_registry.consent_required_for"
m48 = importlib.import_module("odoo.addons.cd_p03_portal.controllers.a07.m48")


# A07 P1 (2026-11-04): ingest is the IoT Administrator's, and a consent grants
# only once a Consent Officer recorded or verified it. These suites test the
# consent rules, so the clerks hold both roles (test_a07_p1_roles tests the
# roles and the verification themselves).
ROLES = ("cd_stream_registry.group_iot_admin", "cd_stream_registry.group_iot_consent_officer")


def _user(env, login):
    ou = env["operating.unit"].search([], limit=1)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in ROLES])
                ],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    env["ir.config_parameter"].sudo().set_param(PARAM, "customer")
    x = types.SimpleNamespace(env=env)
    x.clerk = _user(env, f"a07p0m48_clerk_{TAG}")
    x.clerk2 = _user(env, f"a07p0m48_clerk2_{TAG}")
    x.equipment = env["fix.equipment"].create(
        {"code": f"P0M48-EQ-{TAG}", "name": f"P0M48 Generator {TAG}", "category": "Electrical"}
    )
    x.site = env["fix.site"].create({"name": f"P0M48 Site {TAG}"})
    x.partner = env["res.partner"].create({"name": f"P0M48 Customer {TAG}"})

    def device(name, **kw):
        vals = {"name": f"{name} {TAG}", "device_id": f"{name}-{TAG}"}
        vals.update(kw)
        return env["fix.iot.device"].create(vals)

    def stream(dev, metric="vibration", **kw):
        vals = {"device_id": dev.id, "metric": metric, "sample_interval_sec": 60}
        vals.update(kw)
        s = env["fix.iot.stream"].create(vals)
        s.action_activate()
        return s

    x.device_fn, x.stream_fn = device, stream
    # A facility sensor: bound to equipment, no customer, no location signal.
    x.device = device("P0M48-EQ", equipment_id=x.equipment.id)
    x.stream = stream(x.device)
    return x


def consent(c, user=None, **kw):
    vals = {
        "subject_type": "device",
        "device_id": c.device.id,
        "purpose": "service",
        "valid_to": date.today() + timedelta(days=365),
    }
    vals.update(kw)
    return c.env["fix.iot.consent"].with_user(user or c.clerk).create(vals)


def _today(c):
    """The consent's own "today" (the user's time zone, Asia/Dhaka here): the
    machine's date.today() differs from it for six hours a day."""
    return fields.Date.context_today(c.env["fix.iot.consent"])


def refused(env, fn):
    try:
        with env.cr.savepoint():
            fn()
    except REFUSED:
        return True
    return False


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()
    mw = getattr(
        g.P03GenericApiController.model_write,
        "original_endpoint",
        g.P03GenericApiController.model_write,
    )
    req = types.SimpleNamespace(env=c.env(user=c.clerk.id))
    old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)
    g.request = s.request = req
    try:
        yield types.SimpleNamespace(write=lambda **kw: mw(ctl, **kw))
    finally:
        g.request, s.request = old_g, old_s


# ------------------------------------------------------------------ telemetry
def test_plain_user_cannot_create_or_rewrite_telemetry(c):
    Telemetry = c.env["fix.iot.telemetry"].with_user(c.clerk)
    assert refused(
        c.env, lambda: Telemetry.create({"device_id": c.device.id, "metric": "x", "value": 99})
    )
    # the proper path still works for the same user, and runs the rules
    c.env["fix.iot.rule"].create({"stream_id": c.stream.id, "threshold": 5.0, "severity": "major"})
    reading, alerts = c.stream.with_user(c.clerk).ingest(99.0)
    assert reading.value == 99.0 and len(alerts) == 1
    assert reading.company_id == c.device.company_id
    # the returned record carries no guard token: it cannot be rewritten
    assert refused(c.env, lambda: reading.with_user(c.clerk).write({"value": 1.0}))
    assert refused(
        c.env,
        lambda: reading.with_user(c.clerk).write(
            {"timestamp": fields.Datetime.now() - timedelta(days=3)}
        ),
    )
    assert reading.value == 99.0


def test_future_dated_reading_refused(c):
    future = fields.Datetime.now() + timedelta(days=2)
    # refused even for superuser code (a gateway or seed)
    assert refused(
        c.env,
        lambda: c.env["fix.iot.telemetry"].create(
            {"device_id": c.device.id, "metric": "vibration", "value": 1.0, "timestamp": future}
        ),
    )
    past = fields.Datetime.now() - timedelta(hours=1)
    row = c.env["fix.iot.telemetry"].create(
        {"device_id": c.device.id, "metric": "vibration", "value": 1.0, "timestamp": past}
    )
    assert row.timestamp == past


# ------------------------------------------------------------ consent at ingest
def test_facility_sensor_exempt_under_default_scope_but_not_under_all(c):
    c.stream.with_user(c.clerk).ingest(1.0)  # equipment-bound, no consent: exempt
    c.env["ir.config_parameter"].sudo().set_param(PARAM, "all")
    with pytest.raises(UserError, match="in-date telemetry consent"):
        c.stream.with_user(c.clerk).ingest(1.0)
    consent(c)
    c.stream.with_user(c.clerk).ingest(1.0)
    # an unknown policy value fails closed, like "all"
    c.env["ir.config_parameter"].sudo().set_param(PARAM, "typo")
    other = c.stream_fn(c.device_fn("P0M48-EQ2", equipment_id=c.equipment.id))
    assert refused(c.env, lambda: other.with_user(c.clerk).ingest(1.0))


@pytest.mark.parametrize(
    "case",
    ["customer_device", "tracker", "gps_metric", "unbound_device"],
)
def test_default_scope_refuses_personal_or_unbound_streams_without_consent(c, case):
    if case == "customer_device":
        dev = c.device_fn("P0M48-CUST", equipment_id=c.equipment.id, partner_id=c.partner.id)
        s = c.stream_fn(dev)
    elif case == "tracker":
        dev = c.device_fn("P0M48-TRK", device_type="tracker", equipment_id=c.equipment.id)
        s = c.stream_fn(dev, metric="battery_pct")
    elif case == "gps_metric":
        dev = c.device_fn("P0M48-VAN", site_id=c.site.id)
        s = c.stream_fn(dev, metric="gps_speed_kph")
    else:
        # A07 P1 BRU-IOT-02: an unbound device's stream can no longer be
        # activated; one activated before that rule still needs a consent.
        dev = c.device_fn("P0M48-ORPH")
        s = c.env["fix.iot.stream"].create({"device_id": dev.id, "metric": "vibration"})
        s._guarded().write({"state": "active"})
    with pytest.raises(UserError, match="Ingest refused"):
        s.with_user(c.clerk).ingest(1.0)
    assert not c.env["fix.iot.telemetry"].search_count([("device_id", "=", dev.id)])
    # a valid consent on the device opens the stream
    consent(c, device_id=dev.id)
    s.with_user(c.clerk).ingest(1.0)


def test_site_and_customer_consents_cover_their_devices(c):
    van = c.device_fn("P0M48-SITE", site_id=c.site.id)
    s1 = c.stream_fn(van, metric="gps_lat")
    consent(c, subject_type="site", device_id=False, site_id=c.site.id)
    s1.with_user(c.clerk).ingest(23.8)
    # A07 P1 BRU-IOT-02: a customer device still monitors a bound asset.
    cust = c.device_fn("P0M48-CUST2", partner_id=c.partner.id, equipment_id=c.equipment.id)
    s2 = c.stream_fn(cust)
    consent(c, subject_type="customer", device_id=False, partner_id=c.partner.id)
    s2.with_user(c.clerk).ingest(1.0)
    # a customer consent for ANOTHER customer does not cover it
    other = c.env["res.partner"].create({"name": f"P0M48 Other {TAG}"})
    cust3 = c.device_fn("P0M48-CUST3", partner_id=other.id, equipment_id=c.equipment.id)
    s3 = c.stream_fn(cust3)
    assert refused(c.env, lambda: s3.with_user(c.clerk).ingest(1.0))


def test_expired_future_and_revoked_consents_do_not_cover(c):
    today = _today(c)
    tracker = c.device_fn("P0M48-T2", device_type="tracker", equipment_id=c.equipment.id)
    s = c.stream_fn(tracker)
    consent(
        c,
        device_id=tracker.id,
        granted_on=today - timedelta(days=30),
        valid_to=today - timedelta(days=1),
    )
    assert refused(c.env, lambda: s.with_user(c.clerk).ingest(1.0))
    consent(c, device_id=tracker.id, granted_on=today + timedelta(days=1), valid_to=False)
    assert refused(c.env, lambda: s.with_user(c.clerk).ingest(1.0))
    open_ended = consent(c, device_id=tracker.id, valid_to=False)
    s.with_user(c.clerk).ingest(1.0)
    open_ended.with_user(c.clerk2).action_revoke()
    s.invalidate_recordset()
    assert s.state == "suspended"
    s.action_activate()  # reactivating the stream does not bring consent back
    assert refused(c.env, lambda: s.with_user(c.clerk).ingest(1.0))


# ----------------------------------------------------------------- revocation
def test_revoke_suspends_stamps_and_is_final(c, p03):
    cn = consent(c)
    c.stream.with_user(c.clerk).ingest(1.0)
    cn.with_user(c.clerk2).action_revoke()
    c.stream.invalidate_recordset()
    assert c.stream.state == "suspended"
    assert cn.revoked_by == c.clerk2 and cn.revoked_on
    # once a consent was recorded, an equipment sensor loses its exemption
    c.stream.action_activate()
    assert refused(c.env, lambda: c.stream.with_user(c.clerk).ingest(1.0))
    # final: plain write, P03 write and even superuser write are refused
    assert refused(c.env, lambda: cn.with_user(c.clerk).write({"state": "active"}))
    r = p03.write(model="fix.iot.consent", record_id=cn.id, values={"state": "active"})
    assert "error" in r
    assert refused(c.env, lambda: cn.write({"state": "active"}))
    assert refused(
        c.env,
        lambda: cn.with_user(c.clerk).write({"valid_to": date.today() + timedelta(days=900)}),
    )
    cn.invalidate_recordset()
    assert cn.state == "revoked"
    assert "state" in cn._fix_form_locked_fields() and "valid_to" in cn._fix_form_locked_fields()
    cn.with_user(c.clerk).write({"notes": "customer called"})  # notes stay editable
    assert refused(c.env, lambda: cn.with_user(c.clerk).action_revoke())


def test_revoke_keeps_streams_another_valid_consent_covers(c):
    c.device.site_id = c.site
    device_consent = consent(c)
    consent(c, subject_type="site", device_id=False, site_id=c.site.id)
    device_consent.with_user(c.clerk).action_revoke()
    c.stream.invalidate_recordset()
    assert c.stream.state == "active"
    c.stream.with_user(c.clerk).ingest(1.0)


def test_state_and_stamps_not_set_directly(c):
    cn = consent(c)
    assert refused(c.env, lambda: cn.with_user(c.clerk).write({"state": "revoked"}))
    assert refused(c.env, lambda: cn.with_user(c.clerk).write({"revoked_by": c.clerk.id}))
    assert refused(c.env, lambda: consent(c, state="revoked"))
    # the P03 form echo of the unchanged state is still accepted
    cn.with_user(c.clerk).write({"state": "active", "notes": "echo"})
    assert cn.state == "active" and not cn.revoked_on


def test_consent_must_name_subject_and_valid_dates(c):
    assert refused(c.env, lambda: consent(c, subject_type="customer", device_id=False))
    assert refused(c.env, lambda: consent(c, subject_type="device", device_id=False))
    assert refused(c.env, lambda: consent(c, subject_type="site", device_id=False))
    assert refused(
        c.env,
        lambda: consent(c, granted_on=_today(c), valid_to=_today(c) - timedelta(days=1)),
    )
    ok = consent(c, subject_type="customer", device_id=False, partner_id=c.partner.id)
    assert ok.state == "active"
    same_day = consent(c, granted_on=_today(c), valid_to=_today(c))
    assert same_day._fix_is_valid()


# ----------------------------------------------------------- P03 figures
def test_stream_telemetry_ids_and_coverage_are_per_stream(c):
    temp = c.stream_fn(c.device, metric="temperature", sample_interval_sec=3600)
    for _ in range(24):
        c.stream.ingest(1.0)
    c.stream.invalidate_recordset()
    mine = c.env["fix.iot.telemetry"].search(
        [("device_id", "=", c.device.id), ("metric", "=", "vibration")]
    )
    assert set(c.stream.telemetry_ids.ids) == set(mine.ids) and len(mine) == 24
    assert not temp.telemetry_ids
    rows = {r["stream"]: r for r in m48.telemetry_coverage(c.env)["rows"]}
    assert rows[temp.name]["readings"] == 0 and rows[temp.name]["coverage"] == 0.0
    assert rows[c.stream.name]["readings"] == 24
    quality = {r["stream"]: r for r in m48.stream_quality(c.env)["rows"]}
    assert quality[temp.name]["quality"] == "No data"
    assert quality[c.stream.name]["quality"] == "Fresh"


def test_streams_ingesting_counts_recent_readings_only(c):
    before = m48.kpis(c.env)["streams_ingesting"]
    for i in range(3):
        c.stream_fn(c.device, metric=f"silent{i}")
    assert m48.kpis(c.env)["streams_ingesting"] == before
    fresh = c.stream_fn(c.device, metric="fresh")
    fresh.ingest(1.0)
    assert m48.kpis(c.env)["streams_ingesting"] == before + 1


def test_rul_healthy_without_rul_not_imminent_and_precision_no_data(c):
    p = c.env["fix.predictive.maintenance"].create(
        {
            "name": f"P0M48-H-{TAG}",
            "equipment_id": c.equipment.id,
            "prediction": "healthy",
            "estimated_days_to_failure": 0,
        }
    )
    f = c.env["fix.predictive.maintenance"].create(
        {
            "name": f"P0M48-F-{TAG}",
            "equipment_id": c.equipment.id,
            "prediction": "failure_predicted",
            "estimated_days_to_failure": 0,
        }
    )
    rows = m48.rul_estimation(c.env)["rows"]
    by_name = {(r["equipment"], r["prediction"]): r for r in rows}
    assert by_name[(p.equipment_id.name, "Healthy")]["band"] == "Not estimated"
    assert by_name[(f.equipment_id.name, "Failure Predicted")]["band"] == "Imminent"
    c.env["fix.predictive.maintenance"].search([]).write({"outcome": "pending"})
    assert m48.kpis(c.env)["prediction_precision"] is None
    f.outcome = "confirmed"
    assert m48.kpis(c.env)["prediction_precision"] == 100.0


def test_kpis_and_reports_scoped_to_caller_companies(c):
    other = c.env["res.company"].create({"name": f"P0M48 Other Co {TAG}"})
    foreign = c.env["fix.iot.device"].create(
        {
            "name": f"P0M48 Foreign {TAG}",
            "device_id": f"FOR-{TAG}",
            "company_id": other.id,
            "site_id": c.env["fix.site"].create({"name": f"P0M48 Foreign Site {TAG}"}).id,
        }
    )
    fstream = c.env["fix.iot.stream"].create({"device_id": foreign.id, "metric": "vibration"})
    fstream.action_activate()
    c.env["fix.iot.alert"].create(
        [
            {"device_id": foreign.id, "message": f"foreign {i}", "company_id": other.id}
            for i in range(7)
        ]
    )
    clerk_env = c.env(user=c.clerk.id)
    kpi = m48.kpis(clerk_env)["open_alerts"]
    visible = c.env["fix.iot.alert"].with_user(c.clerk).search_count([("state", "!=", "resolved")])
    assert kpi == visible
    for report in ("telemetry_coverage", "stream_quality"):
        names = {r["stream"] for r in m48.REPORTS[report](clerk_env)["rows"]}
        assert fstream.name not in names
    devices = {r["device"] for r in m48.alert_storm(clerk_env)["rows"]}
    assert foreign.name not in devices
    assert foreign.name not in {r["device"] for r in m48.asset_health(clerk_env)["rows"]}
