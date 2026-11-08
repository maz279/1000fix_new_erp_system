"""A07 P1 / P2 (2026-11-04) M48: consent verification, signal scope and
revocation treatment; retention governance and the measured compression;
predictions bound to a published M26 model; dispatch hand-off and outcome
evidence; stream binding; company isolation; and the new P03 surfaces.

Attackers are NON-ADMIN users created in the rolled-back transaction, holding
exactly the M48 role they would really hold (or none, where the role is the
control). Approvals go through the approver's inbox (approve_via_inbox)."""

from __future__ import annotations

import importlib
import json
import types
import uuid
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
    inbox_task,
)
from odoo.exceptions import AccessError, UserError, ValidationError

TAG = uuid.uuid4().hex[:6].upper()
REFUSED = (UserError, ValidationError, AccessError)
OPERATOR = "cd_stream_registry.group_iot_operator"
ADMIN = "cd_stream_registry.group_iot_admin"
MANAGER = "cd_stream_registry.group_iot_manager"
CONSENT = "cd_stream_registry.group_iot_consent_officer"
PURGE = "cd_stream_registry.retention_purge_enabled"
MODEL_CHECK = "cd_stream_registry.prediction_model_check"
MODEL = "m26.predictive.maintenance"
m48 = importlib.import_module("odoo.addons.cd_p03_portal.controllers.a07.m48")


def refused(env, fn):
    try:
        with env.cr.savepoint():
            fn()
    except REFUSED:
        return True
    return False


def events(env, event_type, aggregate_id):
    rows = env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)], order="id"
    )
    return [json.loads(r.payload) for r in rows]


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    for key, value in (
        (PURGE, "0"),
        (MODEL_CHECK, "use"),
        ("cd_stream_registry.consent_required_for", "customer"),
    ):
        env["ir.config_parameter"].sudo().set_param(key, value)
    ou = env["operating.unit"].search([], limit=1)
    n = {"i": 0}

    def user(*xmlids, company=None):
        n["i"] += 1
        login = "a07l48_%d_%s" % (n["i"], TAG)
        groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
        vals = {"name": login, "login": login, "group_ids": [(6, 0, groups)]}
        if company:
            vals.update({"company_id": company.id, "company_ids": [(6, 0, company.ids)]})
        else:
            vals.update(
                {
                    "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                    "default_operating_unit_id": ou.id,
                }
            )
        return env["res.users"].with_context(no_reset_password=True).create(vals)

    x = types.SimpleNamespace(env=env, user=user)
    x.clerk = user()
    x.operator = user(OPERATOR)
    x.admin = user(ADMIN)
    x.cto = user(MANAGER)
    x.officer = user(CONSENT)
    x.officer2 = user(CONSENT)
    x.equipment = env["fix.equipment"].create(
        {"code": f"L48-EQ-{TAG}", "name": f"L48 Chiller {TAG}", "category": "Electrical"}
    )
    x.partner = env["res.partner"].create({"name": f"L48 Customer {TAG}"})

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
    x.device = device("L48-EQ", equipment_id=x.equipment.id)
    x.stream = stream(x.device)
    # a customer-owned device: always needs a consent (BRU-IOT-03)
    x.cust = device("L48-CUST", equipment_id=x.equipment.id, partner_id=x.partner.id)
    x.cust_stream = stream(x.cust, metric="temperature")
    x.tech_user = user(OPERATOR)
    x.tech = env["hr.employee"].create({"name": f"L48 Tech {TAG}", "user_id": x.tech_user.id})
    return x


def consent(c, user, **kw):
    vals = {
        "subject_type": "device",
        "device_id": c.cust.id,
        "purpose": "service",
        "valid_to": fields.Date.context_today(c.env["fix.iot.consent"]) + timedelta(days=365),
        "granted_by": "L48 Customer",
        "evidence_ref": "CF-48-001",
        "signal_groups_permitted": "temperature",
    }
    vals.update(kw)
    return c.env["fix.iot.consent"].with_user(user).create(vals)


# ============================================================ consent (P1/P2)
def test_a_consent_a_non_officer_records_grants_nothing_until_verified(c):
    cn = consent(c, c.clerk)
    assert cn.verification == "pending" and not cn.verified_by
    with pytest.raises(UserError, match="verified"), c.env.cr.savepoint():
        c.cust_stream.ingest(20.0)
    # the clerk cannot verify, nor forge the verification
    assert refused(c.env, lambda: cn.with_user(c.clerk).action_verify())
    assert refused(c.env, lambda: cn.with_user(c.clerk).write({"verification": "verified"}))
    assert refused(c.env, lambda: consent(c, c.clerk, verification="verified"))
    cn.with_user(c.officer).action_verify()
    assert (cn.verification, cn.verified_by) == ("verified", c.officer)
    c.cust_stream.with_user(c.admin).ingest(20.0)


def test_verification_needs_evidence_and_a_second_person(c):
    bare = consent(c, c.clerk, evidence_ref=False, granted_by=False)
    assert refused(c.env, lambda: bare.with_user(c.officer).action_verify())
    bare.with_user(c.clerk).write({"evidence_ref": "CF-48-009"})
    assert refused(c.env, lambda: bare.with_user(c.officer).action_verify())  # no grantor
    bare.with_user(c.clerk).write({"granted_by": "L48 Customer"})
    bare.with_user(c.officer).action_verify()
    # an officer's own record is verified at once; another officer's pending
    # record cannot be verified by its recorder
    mine = consent(c, c.officer)
    assert mine.verification == "verified" and mine.verified_by == c.officer
    # a recorder later appointed officer still cannot verify their own record
    recorder = c.user()
    own = consent(c, recorder)
    recorder.group_ids = [(4, c.env.ref(CONSENT).id)]
    assert refused(c.env, lambda: own.with_user(recorder).action_verify())
    own.with_user(c.officer2).action_verify()


def test_changing_a_verified_consent_sends_it_back_for_verification(c):
    cn = consent(c, c.officer)
    cn.with_user(c.clerk).write({"signal_groups_permitted": "temperature, humidity"})
    assert cn.verification == "pending" and not cn.verified_by
    assert refused(c.env, lambda: c.cust_stream.ingest(20.0))
    cn.with_user(c.clerk).write({"notes": "customer called"})  # notes do not void it
    cn.with_user(c.officer2).action_verify()
    cn.with_user(c.clerk).write({"notes": "again"})
    assert cn.verification == "verified"


def test_only_disclosed_signals_are_collected(c):
    consent(c, c.officer, signal_groups_permitted="temperature")
    c.cust_stream.ingest(20.0)
    power = c.stream_fn(c.cust, metric="power_kw")
    with pytest.raises(UserError, match="does not disclose"), c.env.cr.savepoint():
        power.ingest(1.0)
    # a prefix covers its sub-signals
    consent(c, c.officer, signal_groups_permitted="power")
    power.ingest(1.0)


@pytest.mark.parametrize("treatment", ["retain", "delete", "anonymise"])
def test_revocation_applies_the_treatment_agreed_at_grant(c, treatment):
    cn = consent(c, c.officer, revocation_treatment=treatment)
    for v in (20.0, 21.0, 22.0):
        c.cust_stream.ingest(v)
    cn.with_user(c.clerk).action_revoke(evidence_ref="LTR-48-7")
    held = c.env["fix.iot.telemetry"].search_count([("device_id", "=", c.cust.id)])
    assert c.cust_stream.state == "suspended"
    assert (cn.revoked_by, cn.revocation_evidence_ref) == (c.clerk, "LTR-48-7")
    assert cn.revoked_at and cn.revoked_on == cn.revoked_at
    if treatment == "delete":
        assert held == 0 and (cn.treatment_state, cn.readings_treated) == ("applied", 3)
    elif treatment == "retain":
        assert held == 3 and cn.treatment_state == "applied"
    else:
        assert held == 3 and cn.treatment_state == "manual"
        assert refused(c.env, lambda: cn.with_user(c.clerk).action_record_treatment(note="x"))
        cn.with_user(c.officer).action_record_treatment(note="series hashed off-line")
        assert cn.treatment_state == "applied"
    (payload,) = events(c.env, "telemetry.consent_revoked", cn.id)
    assert payload["treatment"] == treatment and payload["evidence_ref"] == "LTR-48-7"
    assert payload["streams_suspended"] == [c.cust_stream.name]
    assert events(c.env, "telemetry.stream_suspended", c.cust_stream.id)


def test_consent_expiry_cron_suspends_at_midnight(c):
    today = fields.Date.context_today(c.env["fix.iot.consent"])
    consent(c, c.officer, granted_on=today - timedelta(days=30), valid_to=today - timedelta(days=1))
    assert c.cust_stream.state == "active"
    assert c.env["fix.iot.consent"].cron_consent_expiry() == 1
    assert c.cust_stream.state == "suspended"
    assert c.env["fix.iot.consent"].cron_consent_expiry() == 0  # idempotent
    # an exempt facility sensor with no consent recorded is left alone
    assert c.stream.state == "active"


def test_per_stream_consent_policy_tightens_and_only_the_officer_relaxes_it(c):
    c.stream.ingest(1.0)  # equipment sensor: exempt by default (B5)
    c.stream.with_user(c.admin).write({"consent_policy": "required"})
    assert refused(c.env, lambda: c.stream.ingest(1.0))
    assert refused(c.env, lambda: c.stream.with_user(c.admin).write({"consent_policy": "inherit"}))
    c.officer.group_ids = [(4, c.env.ref(ADMIN).id)]  # the officer may also write streams
    c.stream.with_user(c.officer).write({"consent_policy": "inherit"})
    c.stream.ingest(1.0)


# ===================================================== retention (BRU-IOT-06)
def test_retention_changes_only_through_a_cto_approval(c):
    assert refused(c.env, lambda: c.stream.with_user(c.admin).write({"retention_days": 1}))
    change = (
        c.env["fix.iot.retention.change"]
        .with_user(c.admin)
        .create({"stream_id": c.stream.id, "proposed_days": 30, "reason": "storage budget"})
    )
    change.with_user(c.admin).action_request_approval()
    assert (change.state, change.current_days, change.approval_state) == (
        "requested",
        90,
        "pending",
    )
    assert c.cto in assigned(change) and c.admin not in assigned(change)
    # frozen while pending; the requester cannot decide it
    assert refused(c.env, lambda: change.with_user(c.admin).write({"proposed_days": 1}))
    assert refused(c.env, lambda: change.with_user(c.admin).action_apply())
    assert refused(c.env, lambda: change.with_user(c.cto).action_apply())  # not from the inbox
    approve_via_inbox(change, c.cto)
    assert (change.state, change.applied_by, c.stream.retention_days) == ("applied", c.cto, 30)
    (payload,) = events(c.env, "telemetry.retention_policy_changed", change.id)
    assert (payload["from_days"], payload["to_days"]) == (90, 30)


def test_a_rejected_retention_change_changes_nothing(c):
    change = (
        c.env["fix.iot.retention.change"]
        .with_user(c.admin)
        .create({"stream_id": c.stream.id, "proposed_days": 7, "reason": "trim"})
    )
    change.with_user(c.admin).action_request_approval()
    inbox_task(change, c.cto).with_user(c.cto).action_reject(comment="keep 90")
    assert change.state == "rejected" and c.stream.retention_days == 90


def test_policy_activation_is_requested_and_an_active_policy_is_frozen(c):
    ds = (
        c.env["fix.iot.downsample"]
        .with_user(c.clerk)
        .create({"stream_id": c.stream.id, "raw_interval_sec": 60, "target_interval_sec": 300})
    )
    assert ds.compression_pct == 80.0  # the design figure, computed
    assert refused(c.env, lambda: ds.with_user(c.clerk).write({"state": "active"}))
    ds.with_user(c.clerk).action_activate()
    assert ds.state == "draft"
    change = c.env["fix.iot.retention.change"].search([("downsample_id", "=", ds.id)])
    assert (change.change_type, change.state) == ("activate", "requested")
    approve_via_inbox(change, c.cto)
    assert ds.state == "active" and ds.activated_on
    assert refused(c.env, lambda: ds.with_user(c.clerk).write({"retention_days": 1}))
    assert refused(c.env, lambda: ds.with_user(c.admin).write({"target_interval_sec": 3600}))


def test_retention_cron_aggregates_measures_and_purges_only_when_switched_on(c):
    env = c.env
    ds = env["fix.iot.downsample"].create(
        {"stream_id": c.stream.id, "raw_interval_sec": 60, "target_interval_sec": 300}
    )
    ds.action_activate()  # superuser: direct
    base = fields.Datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(days=3)
    for i in range(10):  # 10 readings in two 5-minute buckets
        c.stream.ingest(float(i), timestamp=base + timedelta(minutes=i))
    other = c.stream_fn(c.device, metric="temperature")  # no policy: never purged
    other.ingest(5.0, timestamp=base)
    assert m48.kpis(env)["retention_compression"] is None
    out = env["fix.iot.downsample"].cron_retention()
    assert out == {"aggregates": 2, "raw_dropped": 0, "aggregates_dropped": 0}
    assert (ds.raw_points_rolled, ds.rollup_points, ds.measured_compression_pct) == (10, 2, 80.0)
    first = ds.rollup_ids.sorted("bucket_start")[0]
    assert (first.points, first.value) == (5, 2.0)
    assert m48.kpis(env)["retention_compression"] == 80.0
    # idempotent
    assert env["fix.iot.downsample"].cron_retention()["aggregates"] == 0
    # purge switched on, with a 1-day raw retention: the aggregated raw goes
    env["ir.config_parameter"].sudo().set_param(PURGE, "1")
    c.stream._guarded().write({"retention_days": 1})
    out = env["fix.iot.downsample"].cron_retention()
    assert out["raw_dropped"] == 10
    assert len(ds.rollup_ids) == 2  # the aggregates survive the raw data
    assert (
        env["fix.iot.telemetry"].search_count(
            [("metric", "=", "temperature"), ("device_id", "=", c.device.id)]
        )
        == 1
    )
    # aggregates are platform records
    assert refused(env, lambda: first.with_user(c.admin).write({"value": 99.0}))


def test_typed_compression_no_longer_moves_the_kpi(c):
    before = m48.kpis(c.env)["retention_compression"]
    ds = (
        c.env["fix.iot.downsample"]
        .with_user(c.clerk)
        .create(
            {
                "stream_id": c.stream.id,
                "raw_interval_sec": 60,
                "target_interval_sec": 300,
                "compression_pct": 99999.0,
            }
        )
    )
    ds._fix_activate()
    assert ds.compression_pct == 80.0
    assert m48.kpis(c.env)["retention_compression"] == before


# ================================================= predictions and actions
def pred(c, user=None, **kw):
    """Recorded by the IoT Operator; pass `user=c.env.user` for the platform (the
    superuser), which is the only one the "use" setting of the model check lets
    record an unpublished model."""
    vals = {
        "name": f"L48-PDM-{TAG}",
        "equipment_id": c.equipment.id,
        "prediction": "failure_predicted",
        "confidence": 0.8,
        "estimated_days_to_failure": 10,
        "model_name": MODEL,
    }
    vals.update(kw)
    Prediction = c.env["fix.predictive.maintenance"]
    model = Prediction if user == c.env.user else Prediction.with_user(user or c.operator)
    return model.create(vals)


def approver(c):
    return c.user(c.env["fix.iot.action"]._approval_group_xmlid())


def test_an_unpublished_model_is_never_applied(c):
    # A person never records one, whatever the setting says
    assert refused(c.env, lambda: pred(c, model_name="made-up-model-v99"))
    assert refused(c.env, lambda: pred(c, model_name=False))
    # one the platform recorded (as the live rows were) is not applied
    p = pred(c, user=c.env.user, model_name="made-up-model-v99")
    assert not p.model_published
    a = c.env["fix.iot.action"].with_user(c.clerk).create({"prediction_id": p.id})
    with pytest.raises(UserError, match="not a published"), c.env.cr.savepoint():
        a.with_user(c.clerk).action_request_approval(justification="bearing noise rising")
    with pytest.raises(UserError, match="not a published"), c.env.cr.savepoint():
        p.with_user(c.operator).action_create_preventive_wo()
    good = pred(c)
    assert good.model_published
    good.with_user(c.operator).action_create_preventive_wo()
    # the strict switch refuses the record itself, from the platform too
    c.env["ir.config_parameter"].sudo().set_param(MODEL_CHECK, "create")
    assert refused(c.env, lambda: pred(c, user=c.env.user, model_name="made-up-model-v99"))
    assert refused(c.env, lambda: pred(c, user=c.env.user, model_name=False))
    pred(c)


def test_feature_window_is_ordered(c):
    now = fields.Datetime.now()
    assert refused(
        c.env,
        lambda: pred(c, feature_window_from=now, feature_window_to=now - timedelta(days=1)),
    )
    p = pred(c, feature_window_from=now - timedelta(days=7), feature_window_to=now)
    assert p.feature_window_to == now


def test_dispatch_hands_off_and_completion_needs_evidence_and_another_person(c):
    mgr = approver(c)
    a = (
        c.env["fix.iot.action"]
        .with_user(c.clerk)
        .create({"prediction_id": pred(c).id, "action_type": "replace", "technician_id": c.tech.id})
    )
    approve_via_inbox(a, mgr, requester=c.clerk, justification="bearing noise rising")
    assert refused(c.env, lambda: a.with_user(c.clerk).action_dispatch())  # not an operator
    a.with_user(c.operator).action_dispatch()
    (payload,) = events(c.env, "iot.action_dispatched", a.id)
    assert payload["equipment_id"] == c.equipment.id and payload["technician_id"] == c.tech.id
    assert (payload["action_type"], payload["model"], payload["approved_by"]) == (
        "replace",
        MODEL,
        mgr.id,
    )
    assert refused(c.env, lambda: a.with_user(c.operator).action_done_confirmed(note="worn"))
    a.with_user(c.operator).write({"outcome_evidence_ref": "SO-48-123"})
    # the technician whose intervention is evaluated does not record its outcome
    assert refused(c.env, lambda: a.with_user(c.tech_user).action_done_confirmed(note="fine"))
    a.with_user(c.operator).action_done_confirmed(note="bearing worn, replaced")
    assert a.prediction_id.outcome == "confirmed"
    assert refused(c.env, lambda: a.with_user(c.operator).write({"outcome_evidence_ref": "x"}))
    (out,) = events(c.env, "iot.intervention_outcome_recorded", a.id)
    assert (out["prediction_outcome"], out["evidence_ref"]) == ("confirmed", "SO-48-123")


# ===================================================== binding and isolation
def test_a_stream_activates_only_on_a_bound_device(c):
    orphan = c.device_fn("L48-ORPH")
    s = (
        c.env["fix.iot.stream"]
        .with_user(c.admin)
        .create({"device_id": orphan.id, "metric": "temp"})
    )
    with pytest.raises(UserError, match="bound to no asset"), c.env.cr.savepoint():
        s.with_user(c.admin).action_activate()
    orphan.write({"site_id": c.env["fix.site"].create({"name": f"L48 Site {TAG}"}).id})
    s.with_user(c.admin).action_activate()
    assert s.state == "active"


def test_the_six_models_are_fenced_to_the_users_companies(c):
    other = c.env["res.company"].create({"name": f"L48 Other Co {TAG}"})
    outsider = c.user(ADMIN, CONSENT, company=other)
    r = c.env["fix.iot.rule"].create({"stream_id": c.stream.id, "threshold": 3.0})
    cn = consent(c, c.officer)
    ds = c.env["fix.iot.downsample"].create({"stream_id": c.stream.id})
    a = c.env["fix.iot.action"].create({"prediction_id": pred(c).id})
    for rec in (c.stream, r, cn, ds, a):
        assert rec.company_id == c.device.company_id
        assert not c.env[rec._name].with_user(outsider).search_count([("id", "=", rec.id)]), rec
        assert c.env[rec._name].with_user(c.clerk).search_count([("id", "=", rec.id)]) == 1
    shared = c.env["fix.iot.adapter"].create({"name": f"L48 Shared {TAG}"})
    assert c.env["fix.iot.adapter"].with_user(outsider).search_count([("id", "=", shared.id)])


# ================================================================== P03
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
    ma = getattr(
        g.P03GenericApiController.model_action,
        "original_endpoint",
        g.P03GenericApiController.model_action,
    )
    old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)

    def as_user(u):
        g.request = s.request = types.SimpleNamespace(env=c.env(user=u.id))

    try:
        yield types.SimpleNamespace(
            write=lambda **kw: mw(ctl, **kw), action=lambda **kw: ma(ctl, **kw), as_user=as_user
        )
    finally:
        g.request, s.request = old_g, old_s


def test_p03_downsample_and_retention_surfaces(c, p03):
    p03.as_user(c.clerk)
    r = p03.write(
        model="fix.iot.downsample",
        values={"stream_id": c.stream.id, "raw_interval_sec": 60, "target_interval_sec": 600},
    )
    assert "error" not in r, r
    ds = c.env["fix.iot.downsample"].browse(r["id"])
    r = p03.write(model="fix.iot.downsample", record_id=ds.id, values={"state": "active"})
    assert "error" in r
    r = p03.action(model="fix.iot.downsample", ids=[ds.id], method="action_activate")
    assert r["success"], r
    ds.invalidate_recordset()
    assert ds.state == "draft"
    p03.as_user(c.admin)
    r = p03.write(
        model="fix.iot.retention.change",
        values={"stream_id": c.stream.id, "proposed_days": 45, "reason": "audit"},
    )
    assert "error" not in r, r
    r = p03.action(
        model="fix.iot.retention.change", ids=[r["id"]], method="action_request_approval"
    )
    assert r["success"], r
    # the apply method is not a workspace action
    change = c.env["fix.iot.retention.change"].search([("stream_id", "=", c.stream.id)])
    r = p03.action(model="fix.iot.retention.change", ids=change.ids, method="action_apply")
    assert not r.get("success")
    # gaps are read-only on the workspace
    r = p03.write(model="fix.iot.gap", values={"stream_id": c.stream.id})
    assert "error" in r or not c.env["fix.iot.gap"].search_count([("stream_id", "=", c.stream.id)])
