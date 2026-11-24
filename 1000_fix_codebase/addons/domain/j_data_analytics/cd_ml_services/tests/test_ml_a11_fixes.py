"""M26 A11 fixes (B4): BRU-AIM-11 promotion declaration, the guard-rail
threshold source, the lifecycle events with their in-Odoo consumers, and the
evaluation gate on a deployed version.

Every test drives the live ORM. The events are asserted on the transactional
outbox (fix.event.outbox) and through their real consumer path — the data
subscriptions are read from fix.event.consumer, and the relay is invoked for
one end-to-end case.
"""

import pytest
from odoo import fields
from odoo.exceptions import UserError

SCIENTIST = "cd_ml_services.group_ml_data_scientist"
REVIEWER = "cd_ml_services.group_ml_reviewer"
OWNER = "cd_ml_services.group_ml_model_owner"

ALL_GATES = ("accuracy", "latency", "bias", "explainability", "safety")


@pytest.fixture
def env(odoo_env):
    if "fix.ml.model" not in odoo_env:
        pytest.skip("cd_ml_services is not installed")
    return odoo_env


@pytest.fixture
def make_user(env):
    counter = {"n": 0}

    def _make(*xmlids):
        counter["n"] += 1
        groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "M26 B4 Probe %d" % counter["n"],
                    "login": "m26.b4.%d@a11.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


_seq = {"n": 0}


def _model(env, kind="lead_scoring", **extra):
    """A production model with the data-sufficiency bar. Declarations are
    opt-in per test (the BRU-AIM-11 refusals need them absent)."""
    _seq["n"] += 1
    vals = {
        "name": "B4 probe model %d" % _seq["n"],
        "code": "B4PR%d" % _seq["n"],
        "kind": kind,
        "implementation": "rule_based",
        "status": "production",
        "owning_module": "cd_ml_services (test)",
        "min_history_months": 6,
        "min_volume": 500,
    }
    vals.update(extra)
    model = env["fix.ml.model"].create(vals)
    env["fix.ml.data.sufficiency"].create(
        {
            "model_id": model.id,
            "observed_history_months": 12,
            "observed_volume": 5000,
            "source_modules": "B4 probe history",
        }
    )
    return model


def _declared(env, kind="lead_scoring"):
    return _model(
        env,
        kind=kind,
        consumer_modules="M07 Sales (probe)",
        accuracy_target="AUC > 0.70 (probe)",
        fallback_definition="Lead stays unscored; a representative qualifies it (probe)",
    )


def _gated_version(env, model, scientist, reviewer):
    version = (
        env["fix.ml.model.version"]
        .with_user(scientist)
        .create(
            {
                "model_id": model.id,
                "version": "4.%d.0" % _seq["n"],
                "model_card": "Purpose: probe. Limitations: none claimed.",
                "metrics_json": '{"auc": 0.8}',
            }
        )
    )
    version.with_user(scientist).action_evaluate()
    for gate in ALL_GATES:
        env["fix.ml.evaluation.gate"].with_user(reviewer).create(
            {"version_id": version.id, "gate": gate, "result": "passed"}
        )
    env["fix.ml.bias.test"].with_user(reviewer).create(
        {
            "version_id": version.id,
            "segments_tested": "branch; tenure band",
            "metric_by_segment": "AUC 0.78 / 0.76",
            "assessment": "passed",
            "next_due": "2099-01-01",
        }
    )
    return version


# ------------------------------------------------------- BRU-AIM-11 (A2-F10)


def test_a_new_promotion_is_refused_without_a_named_consumer(env, make_user):
    model = _model(
        env,
        accuracy_target="AUC > 0.70 (probe)",
        fallback_definition="Unscored (probe)",
    )
    scientist, reviewer = make_user(SCIENTIST), make_user(REVIEWER)
    version = _gated_version(env, model, scientist, reviewer)
    with pytest.raises(UserError, match="named consumer"):
        version.with_user(scientist).action_request_promotion(justification="probe")


def test_a_new_promotion_is_refused_without_a_defined_fallback(env, make_user):
    model = _model(env, consumer_modules="M07 Sales (probe)", accuracy_target="AUC > 0.7")
    scientist, reviewer = make_user(SCIENTIST), make_user(REVIEWER)
    version = _gated_version(env, model, scientist, reviewer)
    with pytest.raises(UserError, match="defined fallback"):
        version.with_user(scientist).action_request_promotion(justification="probe")


def test_a_new_promotion_of_a_non_advisory_model_needs_an_accuracy_target(env, make_user):
    model = _model(
        env,
        consumer_modules="M07 Sales (probe)",
        fallback_definition="Unscored (probe)",
    )
    scientist, reviewer = make_user(SCIENTIST), make_user(REVIEWER)
    version = _gated_version(env, model, scientist, reviewer)
    with pytest.raises(UserError, match="accuracy target"):
        version.with_user(scientist).action_request_promotion(justification="probe")


def test_an_advisory_model_promotes_without_an_accuracy_target(env, make_user):
    """A BI aggregator measures nothing it could miss: BRU-AIM-11 demands no
    target of an advisory model, only a consumer and a fallback."""
    model = _model(
        env,
        kind="bi_aggregator",
        consumer_modules="M25 Business Intelligence (probe)",
        fallback_definition="Tile shows '—' with freshness 'never' (probe)",
        risk_class="advisory",
    )
    scientist, reviewer = make_user(SCIENTIST), make_user(REVIEWER)
    version = _gated_version(env, model, scientist, reviewer)
    version.with_user(scientist).action_request_promotion(justification="probe")
    assert version.approval_request_id, "the complete advisory model reaches M63"


def test_a_complete_declaration_promotes(env, make_user):
    model = _declared(env)
    scientist, reviewer = make_user(SCIENTIST), make_user(REVIEWER)
    version = _gated_version(env, model, scientist, reviewer)
    version.with_user(scientist).action_request_promotion(justification="probe")
    assert version.approval_request_id, "a complete model reaches M63"


def test_fill_missing_declarations_fills_only_blanks(env):
    # trade-in has a spec target; lead scoring deliberately has none
    model = _model(env, kind="tradein_valuation", risk_class="financial")
    model.write({"consumer_modules": "Owner-typed consumer"})
    assert env["fix.ml.model"].action_fill_missing_declarations() >= 1
    model.invalidate_recordset()
    assert model.consumer_modules == "Owner-typed consumer", "a typed value is never overwritten"
    assert model.fallback_definition, "the blank fallback is filled from the catalogue"
    assert model.accuracy_target, "the blank target is filled from the catalogue"
    # idempotent: a second run fills nothing
    assert env["fix.ml.model"].action_fill_missing_declarations() == 0


def test_the_seeded_lead_and_bi_models_declare_a_fallback(env):
    """A2-F10: these two deployed models read 'not declared' on the live
    estate. The catalogue now states their measured fallback, and the fill
    action carries it onto the existing (noupdate) rows."""
    for xmlid in ("ml_model_lead_scoring", "ml_model_bi_aggregator"):
        model = env.ref("cd_ml_services.%s" % xmlid)
        model.write({"fallback_definition": False})
    env["fix.ml.model"].action_fill_missing_declarations()
    lead = env.ref("cd_ml_services.ml_model_lead_scoring")
    bi = env.ref("cd_ml_services.ml_model_bi_aggregator")
    assert "unscored" in lead.fallback_definition
    assert "never" in bi.fallback_definition


# ------------------------------------------------- guard-rail threshold (A2-F14b)


def test_the_guardrail_threshold_is_derived_from_the_rule(env):
    rail = env["fix.ml.guardrail"].create(
        {"name": "probe rail", "rule": "score >= 40", "threshold": 12, "action": "flag"}
    )
    assert rail.threshold == 40.0, "the enforced number is the rule's, not a typo'd field"
    rail.write({"rule": "confidence < 0.60"})
    assert rail.threshold == pytest.approx(0.6)
    rail.write({"threshold": 99})
    assert rail.threshold == pytest.approx(
        0.6
    ), "a lone threshold edit cannot diverge from the rule"


# ------------------------------------------------- lifecycle events (A2-F09)


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id:
        domain.append(("aggregate_id", "=", aggregate_id))
    return env["fix.event.outbox"].search(domain, order="id asc")


def _feed(env, event):
    """Hand one outbox row to the module's consumer (what the relay does)."""
    env["fix.ml.model"].consume_model_event(event._relay_event_dict())


def _messages(env, model, text):
    return env["mail.message"].search(
        [
            ("model", "=", "fix.ml.model"),
            ("res_id", "=", model.id),
            ("body", "ilike", text),
        ]
    )


def test_every_lifecycle_event_has_a_registered_consumer(env):
    for event_type in (
        "model.promoted",
        "model.retired",
        "model.gate_failed",
        "model.bias_test_completed",
        "model.drift_alert",
    ):
        subscription = env["fix.event.consumer"].search(
            [("event_type", "=", event_type), ("active", "=", True)]
        )
        assert subscription, "%s has no consumer — the wiring gate fails on it" % event_type
        assert subscription.model == "fix.ml.model"
        assert subscription.method == "consume_model_event"


def test_a_gate_on_a_deployed_version_is_recordable_evidence(env, make_user):
    """D-L15: every live version is deployed, so the choice domain must allow
    one. The gate is evidence and the version stays deployed."""
    model = _declared(env)
    version = env["fix.ml.model.version"].create(
        {
            "model_id": model.id,
            "version": "1.0.0",
            "state": "deployed",
            "deployment_mode": "online",
        }
    )
    reviewer = make_user(REVIEWER)
    gate = (
        env["fix.ml.evaluation.gate"]
        .with_user(reviewer)
        .create({"version_id": version.id, "gate": "accuracy", "result": "passed"})
    )
    assert gate.result == "passed" and gate.checked_by == reviewer
    version.invalidate_recordset()
    assert version.state == "deployed", "re-evaluating a deployed version changes nothing"


def test_a_failed_gate_publishes_once_and_its_consumer_posts_it(env, make_user):
    model = _declared(env)
    version = env["fix.ml.model.version"].create(
        {"model_id": model.id, "version": "1.0.0", "state": "deployed"}
    )
    reviewer = make_user(REVIEWER)
    env["fix.ml.evaluation.gate"].with_user(reviewer).create(
        {"version_id": version.id, "gate": "accuracy", "result": "failed", "notes": "MAPE 31%"}
    )
    events = _events(env, "model.gate_failed", model.id)
    assert len(events) == 1, "one failed gate is one transition, hence one event"
    _feed(env, events)
    assert _messages(env, model, "gate FAILED"), "the consumer posts the alert on the model"
    _feed(env, events)  # a redelivery
    assert len(_messages(env, model, "gate FAILED")) == 1, "the consumer is idempotent per event"


def test_a_drift_alert_raises_a_todo_for_the_owner(env, make_user):
    owner = make_user(OWNER)
    model = _declared(env, kind="bi_aggregator")
    model.write({"owner_id": owner.id, "risk_class": "advisory"})
    version = env["fix.ml.model.version"].create(
        {"model_id": model.id, "version": "1.0.0", "state": "deployed"}
    )
    env["fix.ml.drift.observation"].create(
        {"version_id": version.id, "feature_name": "orders_growth", "psi": 0.41, "threshold": 0.2}
    )
    events = _events(env, "model.drift_alert", model.id)
    assert len(events) == 1
    _feed(env, events)
    activities = env["mail.activity"].search(
        [("res_model", "=", "fix.ml.model"), ("res_id", "=", model.id), ("user_id", "=", owner.id)]
    )
    assert len(activities) == 1, "a named owner gets one to-do"
    assert activities.date_deadline == fields.Date.context_today(env["fix.ml.model"])
    _feed(env, events)
    assert (
        env["mail.activity"].search_count(
            [("res_model", "=", "fix.ml.model"), ("res_id", "=", model.id)]
        )
        == 1
    ), "a redelivered alert raises no second to-do"


def test_a_watch_band_observation_publishes_no_alert(env):
    model = _declared(env, kind="bi_aggregator")
    model.write({"risk_class": "advisory"})
    version = env["fix.ml.model.version"].create(
        {"model_id": model.id, "version": "1.0.0", "state": "deployed"}
    )
    env["fix.ml.drift.observation"].create(
        {"version_id": version.id, "feature_name": "orders_growth", "psi": 0.11, "threshold": 0.2}
    )
    assert not _events(env, "model.drift_alert", model.id), "a watch-band PSI is not an alert"


def test_a_bias_test_publishes_its_completion(env, make_user):
    model = _declared(env)
    scientist, reviewer = make_user(SCIENTIST), make_user(REVIEWER)
    version = (
        env["fix.ml.model.version"]
        .with_user(scientist)
        .create({"model_id": model.id, "version": "2.0.0"})
    )
    env["fix.ml.bias.test"].with_user(reviewer).create(
        {
            "version_id": version.id,
            "segments_tested": "branch",
            "metric_by_segment": "0.78 / 0.74",
            "assessment": "passed",
            "next_due": "2099-01-01",
        }
    )
    events = _events(env, "model.bias_test_completed", model.id)
    assert len(events) == 1
    _feed(env, events)
    assert _messages(env, model, "Bias test completed")


def test_promotion_and_retirement_publish_and_reach_the_consumer(env, make_user):
    """End to end through the relay: the promotion event is delivered to the
    registered consumer once, and retirement too."""
    model = _declared(env)
    scientist, reviewer, owner = make_user(SCIENTIST), make_user(REVIEWER), make_user(OWNER)
    version = _gated_version(env, model, scientist, reviewer)
    version.with_user(scientist).action_request_promotion(justification="probe promotion")
    task = version.approval_request_id.task_ids.filtered(
        lambda t: t.assigned_user_id == owner and t.state == "pending"
    )
    assert task
    task.with_user(owner).action_approve(comment="gates hold")
    version.invalidate_recordset()
    assert version.state == "deployed"
    promoted = _events(env, "model.promoted", model.id)
    assert len(promoted) == 1
    env["fix.event.outbox"].cron_relay(limit=5000)
    assert _messages(env, model, "Model promoted"), "the relay delivered the promotion event"
    # a second relay pass is a no-op (delivery is recorded per event)
    env["fix.event.outbox"].cron_relay(limit=5000)
    assert len(_messages(env, model, "Model promoted")) == 1

    version.with_user(owner).action_retire(confirmation="M07 confirmed the rule fallback")
    retired = _events(env, "model.retired", model.id)
    assert len(retired) == 1
    _feed(env, retired)
    assert _messages(env, model, "Model retired")
