# M26 capture audit (2026-11-14) - the captures the sub-module pages offer,
# driven through the workspace endpoints (/p03/model/write, /p03/model/action)
# with the values the form really posts, as NON-ADMIN M26 role holders (the
# superuser is trusted by the model guards and would hide a gap).
#
# HEAD defects these pin:
#   * "+ New Model Version" posted state='draft' (the form showed State as an
#     editable choice with its default) and the version's lifecycle guard
#     refused the create; an edit echoed the state back and was refused too,
#     so no version could be registered and no model card written.
#   * Recording the human decision on a computed run echoed the model and
#     input back, and the decision-log guard refused the whole save.
#   * Fallback tests, drift observations and the AI risk register had no
#     record at all.
import itertools
import types

import pytest
from odoo.exceptions import UserError

_SEQ = itertools.count(1)

SCIENTIST = "cd_ml_services.group_ml_data_scientist"
REVIEWER = "cd_ml_services.group_ml_reviewer"
OWNER = "cd_ml_services.group_ml_model_owner"


@pytest.fixture
def env(odoo_env):
    if "fix.ml.ai.risk" not in odoo_env:
        pytest.skip("cd_ml_services is not at the capture-audit version on this database")
    return odoo_env


@pytest.fixture
def p03(env):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()
    old = (getattr(g, "request", None), getattr(s, "request", None))

    def raw(fn):
        return getattr(fn, "original_endpoint", fn)

    def as_user(user):
        req = types.SimpleNamespace(env=env(user=user.id))

        def call(route, **kw):
            g.request = s.request = req
            return raw(getattr(g.P03GenericApiController, route))(ctl, **kw)

        return call

    yield as_user
    g.request, s.request = old


def _user(env, *xmlids):
    n = next(_SEQ)
    groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M26 Capture %d" % n,
                "login": "m26.capture.%d@a11.test" % n,
                "group_ids": [(6, 0, groups)],
            }
        )
    )


@pytest.fixture
def fault(env):
    return env.ref("cd_ml_services.ml_model_fault_classifier")


@pytest.fixture
def deployed(env, fault):
    return env.ref("cd_ml_services.ml_version_fault_classifier_v1")


# --------------------------------------------------------------- Training Pipelines
def test_a_scientist_registers_a_version_from_the_form(env, p03, fault):
    sci = p03(_user(env, SCIENTIST))
    values = {
        "model_id": {"id": fault.id, "label": fault.display_name},
        "version": "2.%d.0" % next(_SEQ),
        "artifact_ref": "mlflow://fault-classifier/2",
        "training_dataset": "fault taxonomy 2026-11",
        "metrics_json": '{"top3_accuracy": 0.81}',
        "bias_status": "untested",
        "deployment_mode": "none",
        # the form shows these and posts them back: the server must drop them
        "state": "draft",
        "drift_score": 0.0,
        "model_card": "Purpose: suggest the likely fault from complaint text.",
    }
    res = sci("model_write", model="fix.ml.model.version", values=values)
    assert "id" in res, "the version form cannot save: %s" % res
    version = env["fix.ml.model.version"].browse(res["id"])
    assert version.state == "draft"


def test_the_version_form_still_refuses_a_typed_promotion(env, p03, fault):
    sci_user = _user(env, SCIENTIST)
    version = (
        env["fix.ml.model.version"]
        .with_user(sci_user)
        .create({"model_id": fault.id, "version": "3.%d.0" % next(_SEQ)})
    )
    res = p03(sci_user)(
        "model_write",
        model="fix.ml.model.version",
        record_id=version.id,
        values={"state": "deployed"},
    )
    assert "error" in res and version.state == "draft", res


# --------------------------------------------------------------- Explainability
def test_a_model_card_is_written_on_a_deployed_version(env, p03, deployed):
    sci = p03(_user(env, SCIENTIST))
    card = "Purpose: fault suggestion. Out of scope: warranty decisions. Limits: token match."
    values = {
        "model_id": {"id": deployed.model_id.id, "label": deployed.model_id.display_name},
        "version": deployed.version,
        "state": deployed.state,  # read-only on the form, posted back unchanged
        "model_card": card,
    }
    res = sci("model_write", model="fix.ml.model.version", record_id=deployed.id, values=values)
    assert "id" in res, "the model card cannot be written: %s" % res
    assert deployed.model_card == card and deployed.state == "deployed"


def test_the_human_decision_is_recorded_on_a_computed_run(env, p03, fault):
    clerk_user = _user(env)
    run = (
        env["fix.ml.inference.run"]
        .with_user(clerk_user)
        .create({"model_id": fault.id, "input_text": "screen cracked no display"})
    )
    run.with_user(clerk_user).action_execute()
    assert run.state == "computed", run.error_note
    # what the Record Human Decision form posts: everything it shows
    values = {
        "model_id": {"id": fault.id, "label": fault.display_name},
        "input_text": run.input_text,
        "suggested_value": run.suggested_value,
        "overridden": run.overridden,
        "final_value": "DISPLAY-REPLACE",
        "override_reason": "Technician saw a broken panel, not a cable fault",
    }
    res = p03(clerk_user)(
        "model_write", model="fix.ml.inference.run", record_id=run.id, values=values
    )
    assert "id" in res, "the human decision cannot be recorded: %s" % res
    assert run.final_value == "DISPLAY-REPLACE"
    assert run.override_reason.startswith("Technician")


def test_the_decision_form_cannot_move_a_run_to_another_model(env, p03, fault):
    clerk_user = _user(env)
    run = (
        env["fix.ml.inference.run"]
        .with_user(clerk_user)
        .create({"model_id": fault.id, "input_text": "battery swollen"})
    )
    run.with_user(clerk_user).action_execute()
    other = env.ref("cd_ml_services.ml_model_tradein_valuation")
    res = p03(clerk_user)(
        "model_write",
        model="fix.ml.inference.run",
        record_id=run.id,
        values={"model_id": other.id, "final_value": "x"},
    )
    assert "error" in res and run.model_id == fault, res


# --------------------------------------------------------------- Bengali NLP & OCR
def test_bengali_complaint_text_is_classified_from_the_page(env, p03, fault):
    clerk_user = _user(env)
    call = p03(clerk_user)
    res = call(
        "model_write",
        model="fix.ml.inference.run",
        values={
            "model_id": {"id": fault.id, "label": fault.display_name},
            "input_text": "স্ক্রিন ভাঙা, ডিসপ্লে আসে না",
            "state": "draft",
        },
    )
    assert "id" in res, res
    out = call(
        "model_action", model="fix.ml.inference.run", ids=[res["id"]], method="action_execute"
    )
    assert out.get("success"), out
    run = env["fix.ml.inference.run"].browse(res["id"])
    assert run.state in ("computed", "failed") and run.ran_by == clerk_user


# --------------------------------------------------------------- Deployment & Monitoring
def test_a_scientist_records_a_drift_observation(env, p03, deployed):
    sci = p03(_user(env, SCIENTIST))
    res = sci(
        "model_write",
        model="fix.ml.drift.observation",
        values={
            "version_id": {"id": deployed.id, "label": deployed.display_name},
            "feature_name": "complaint_token_count",
            "psi": 0.27,
            "ks_statistic": 0.12,
            "threshold": 0.2,
            "breached": False,  # derived: the posted value is ignored
        },
    )
    assert "id" in res, res
    obs = env["fix.ml.drift.observation"].browse(res["id"])
    assert obs.breached, "PSI 0.27 against 0.2 is a breach"
    assert deployed.drift_score == pytest.approx(0.27)
    with pytest.raises(UserError, match="evidence"):
        obs.with_user(obs.recorded_by).write({"psi": 0.01})


def test_drift_is_observed_only_on_a_serving_version(env, fault):
    sci_user = _user(env, SCIENTIST)
    draft = (
        env["fix.ml.model.version"]
        .with_user(sci_user)
        .create({"model_id": fault.id, "version": "4.%d.0" % next(_SEQ)})
    )
    with pytest.raises(UserError, match="not deployed"):
        env["fix.ml.drift.observation"].with_user(sci_user).create(
            {"version_id": draft.id, "feature_name": "x", "psi": 0.1}
        )


def test_a_clerk_cannot_record_drift(env, p03, deployed):
    res = p03(_user(env))(
        "model_write",
        model="fix.ml.drift.observation",
        values={"version_id": deployed.id, "feature_name": "x", "psi": 0.3},
    )
    assert "error" in res, res


def test_a_model_owner_records_a_fallback_test(env, p03, fault):
    owner_user = _user(env, OWNER)
    res = p03(owner_user)(
        "model_write",
        model="fix.ml.fallback.test",
        values={
            "model_id": {"id": fault.id, "label": fault.display_name},
            "consumer_module": "M01 Service Orders",
            "method": "disabled",
            "consumer_behaviour": "Intake fell back to the manual fault list; the order saved.",
            "outcome": "passed",
            "incidents_raised": 0,
        },
    )
    assert "id" in res, res
    test = env["fix.ml.fallback.test"].browse(res["id"])
    assert test.tested_by == owner_user
    from odoo.addons.cd_p03_portal.controllers.a11 import m26

    row = next(
        r for r in m26.fallback_status(env(user=owner_user.id))["rows"] if r["code"] == fault.code
    )
    assert row["test_outcome"] == "passed" and row["last_test"] != "never"
    with pytest.raises(UserError, match="evidence"):
        test.with_user(owner_user).unlink()


def test_a_clerk_cannot_record_a_fallback_test(env, p03, fault):
    res = p03(_user(env))(
        "model_write",
        model="fix.ml.fallback.test",
        values={
            "model_id": fault.id,
            "consumer_module": "M01",
            "method": "disabled",
            "consumer_behaviour": "x",
            "outcome": "passed",
        },
    )
    assert "error" in res, res


# --------------------------------------------------------------- Portfolio / GenAI
def test_a_generative_risk_is_recorded_on_the_genai_page(env, p03):
    owner_user = _user(env, OWNER)
    res = p03(owner_user)(
        "model_write",
        model="fix.ml.ai.risk",
        values={
            "name": "Customer data leaves the estate through a hosted LLM",
            "category": "generative",
            "description": "A cloud LLM would receive complaint text with customer names.",
            "likelihood": "medium",
            "impact": "high",
            "treatment": "Self-hosted inference only; no egress route configured.",
            "control_ref": "BRU-AIM-10",
            "owner_id": {"id": owner_user.id, "label": owner_user.name},
            "review_date": "2027-11-14",
            "state": "open",
        },
    )
    assert "id" in res, res
    risk = env["fix.ml.ai.risk"].browse(res["id"])
    assert not risk.model_id, "an estate-wide risk needs no model"
    rows = p03(owner_user)(
        "model_records",
        model="fix.ml.ai.risk",
        cols=["name", "state"],
        domain=[["category", "=", "generative"]],
    )
    assert any(r["id"] == risk.id for r in rows["rows"]), rows


def test_a_clerk_reads_but_cannot_record_a_risk(env, p03):
    res = p03(_user(env))(
        "model_write",
        model="fix.ml.ai.risk",
        values={
            "name": "x",
            "category": "bias",
            "description": "x",
            "likelihood": "low",
            "impact": "low",
            "owner_id": env.user.id,
            "review_date": "2027-01-01",
        },
    )
    assert "error" in res, res


def test_the_portfolio_declaration_saves_and_the_spec_seeds_it(env, p03, fault):
    # the spec's declaration was seeded on the existing entries
    assert fault.consumer_modules and fault.accuracy_target and fault.fallback_definition
    sci_user = _user(env, SCIENTIST)
    res = p03(sci_user)(
        "model_write",
        model="fix.ml.model",
        values={
            "code": "m26.capture.%d" % next(_SEQ),
            "name": "Churn risk",
            "kind": "lead_scoring",
            "implementation": "planned",
            "status": "planned",
            "purpose": "Flag customers likely to lapse",
            "consumer_modules": "M07 Sales, M34 CX",
            "accuracy_target": "AUC > 0.72",
            "fallback_definition": "Recency-frequency-value rules",
            "risk_class": "people_affecting",
            "owner_id": {"id": sci_user.id, "label": sci_user.name},
            "review_date": "2027-06-30",
        },
    )
    assert "id" in res, res
    model = env["fix.ml.model"].browse(res["id"])
    assert model.accuracy_target == "AUC > 0.72" and model.risk_class == "people_affecting"


def test_seeding_never_overwrites_a_typed_declaration(env, fault):
    fault.write({"accuracy_target": "owner's own target"})
    env["fix.ml.model"]._seed_portfolio_declarations()
    assert fault.accuracy_target == "owner's own target"
