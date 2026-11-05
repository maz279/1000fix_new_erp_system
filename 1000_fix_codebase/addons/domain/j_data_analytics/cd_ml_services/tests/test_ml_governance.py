"""cd_ml_services governance tests — M26 G7 controls (A11 audit, 2026-11-05).

Every control is driven through the live ORM as real users, both ways: the
bypass is refused AND the governed path works. The promotion goes through the
M63 inbox exactly as a user would: the registrant requests, a Model Owner who
is NOT the registrant decides.
"""

import json

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

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
                    "name": "M26 Probe %d" % counter["n"],
                    "login": "m26.probe.%d@governance.test" % counter["n"],
                    "email": "m26.probe.%d@governance.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


_seq = {"n": 0}


def _model(env, kind="lead_scoring", **extra):
    _seq["n"] += 1
    vals = {
        "name": "Gov probe model %d" % _seq["n"],
        "code": "GOV%d" % _seq["n"],
        "kind": kind,
        "implementation": "rule_based",
        "status": "production",
        "owning_module": "cd_ml_services (test)",
    }
    vals.update(extra)
    return env["fix.ml.model"].create(vals)


def _version(env, model, user=None, **extra):
    vals = {
        "model_id": model.id,
        "version": "9.1.%d" % _seq["n"],
        "model_card": "Purpose: probe. Limitations: none claimed.",
        "metrics_json": '{"latency_ms_p95": 42}',
        "bias_status": "passed",
    }
    vals.update(extra)
    versions = env["fix.ml.model.version"]
    return versions.with_user(user).create(vals) if user else versions.create(vals)


def _gates(env, version, user, gates=ALL_GATES, result="passed"):
    for gate in gates:
        env["fix.ml.evaluation.gate"].with_user(user).create(
            {"version_id": version.id, "gate": gate, "result": result}
        )


def _task_of(record, user):
    return record.approval_request_id.task_ids.filtered(
        lambda t: t.assigned_user_id == user and t.state == "pending"
    )


def _lead(env, **extra):
    vals = {"name": "M26 governance lead", "expected_revenue": 250000.0}
    vals.update(extra)
    return env["crm.lead"].create(vals)


def _lead_run(env, model, lead):
    return env["fix.ml.inference.run"].create(
        {
            "model_id": model.id,
            "input_text": json.dumps({"lead_id": lead.id}),
        }
    )


# ---------------------------------------------------------------------------
# G7 — the version registry: born draft, named, gated by reviewers
# ---------------------------------------------------------------------------


class TestVersionRegistry:
    def test_a_version_is_born_draft_and_state_is_not_typeable(self, env, make_user):
        scientist = make_user(SCIENTIST)
        model = _model(env)
        version = _version(env, model, scientist)
        assert version.state == "draft"
        assert version.name == "%s %s" % (model.code, version.version)
        with pytest.raises(UserError, match="(?i)not typeable"):
            env["fix.ml.model.version"].with_user(scientist).create(
                {"model_id": model.id, "version": "9.9.9", "state": "deployed"}
            )
        with pytest.raises(UserError, match="(?i)changes state only through"):
            version.with_user(scientist).write({"state": "deployed"})

    def test_a_plain_user_cannot_register_a_version(self, env, make_user):
        plain = make_user()
        model = _model(env)
        with pytest.raises(AccessError):
            env["fix.ml.model.version"].with_user(plain).create(
                {"model_id": model.id, "version": "0.0.1"}
            )

    def test_a_gate_is_born_pending_and_stamps_its_reviewer(self, env, make_user):
        reviewer = make_user(REVIEWER)
        version = _version(env, _model(env))
        gate = (
            env["fix.ml.evaluation.gate"]
            .with_user(reviewer)
            .create({"version_id": version.id, "gate": "accuracy"})
        )
        assert gate.result == "pending", "a gate nobody evaluated must not read as passed"
        assert gate.checked_by == reviewer

    def test_the_registrant_cannot_record_their_own_gates(self, env, make_user):
        scientist = make_user(SCIENTIST, REVIEWER)  # both hats, one head
        version = _version(env, _model(env), scientist)
        with pytest.raises(UserError, match="(?i)cannot record"):
            env["fix.ml.evaluation.gate"].with_user(scientist).create(
                {"version_id": version.id, "gate": "accuracy", "result": "passed"}
            )

    def test_a_recorded_gate_is_append_only_evidence(self, env, make_user):
        reviewer = make_user(REVIEWER)
        version = _version(env, _model(env))
        gate = (
            env["fix.ml.evaluation.gate"]
            .with_user(reviewer)
            .create({"version_id": version.id, "gate": "accuracy", "result": "failed"})
        )
        with pytest.raises(UserError, match="(?i)evidence"):
            gate.write({"result": "passed"})
        with pytest.raises(UserError, match="(?i)evidence"):
            gate.unlink()


# ---------------------------------------------------------------------------
# G7 — promotion refusals (every gate passed, by a reviewer, bias honest)
# ---------------------------------------------------------------------------


class TestPromotionRefusals:
    def _evaluated(self, env, make_user, **extra):
        scientist = make_user(SCIENTIST)
        reviewer = make_user(REVIEWER)
        version = _version(env, _model(env), scientist, **extra)
        version.with_user(scientist).action_evaluate()
        return scientist, reviewer, version

    def test_no_gates_at_all_fails_closed(self, env, make_user):
        scientist, _reviewer, version = self._evaluated(env, make_user)
        with pytest.raises(UserError, match="(?i)no evaluation gate"):
            version.with_user(scientist).action_request_promotion()

    def test_a_pending_gate_blocks_promotion(self, env, make_user):
        scientist, reviewer, version = self._evaluated(env, make_user)
        _gates(env, version, reviewer, gates=("accuracy", "latency"))
        # a third gate nobody has recorded a result for stays pending
        env["fix.ml.evaluation.gate"].with_user(reviewer).create(
            {"version_id": version.id, "gate": "bias"}
        )
        with pytest.raises(UserError, match="(?i)must read 'passed'"):
            version.with_user(scientist).action_request_promotion()

    def test_a_failed_gate_blocks_promotion(self, env, make_user):
        scientist, reviewer, version = self._evaluated(env, make_user)
        _gates(env, version, reviewer)
        env["fix.ml.evaluation.gate"].with_user(reviewer).create(
            {"version_id": version.id, "gate": "safety", "result": "failed"}
        )
        with pytest.raises(UserError, match="(?i)must read 'passed'"):
            version.with_user(scientist).action_request_promotion()

    def test_gates_signed_by_the_registrant_do_not_count(self, env):
        """The legacy shape: a superuser-registered version with
        superuser-recorded gates — the same head on both halves. Even that
        cannot promote."""
        version = _version(env, _model(env))  # registrant: the seed user
        version.action_evaluate()
        _gates(env, version, env.user)  # checked_by: the same seed user
        with pytest.raises(UserError, match="(?i)recorded by the registrant"):
            version.action_request_promotion()

    def test_a_failed_bias_review_blocks_every_promotion(self, env, make_user):
        scientist, reviewer, version = self._evaluated(env, make_user, bias_status="failed")
        _gates(env, version, reviewer)
        with pytest.raises(UserError, match="(?i)failed its bias review"):
            version.with_user(scientist).action_request_promotion()

    def test_a_people_affecting_model_needs_a_passed_bias_review(self, env, make_user):
        scientist = make_user(SCIENTIST)
        reviewer = make_user(REVIEWER)
        # lead_scoring affects people; 'untested' must not pose as 'passed'
        version = _version(env, _model(env, "lead_scoring"), scientist, bias_status="untested")
        version.with_user(scientist).action_evaluate()
        _gates(env, version, reviewer)
        with pytest.raises(UserError, match="(?i)PASSED bias review"):
            version.with_user(scientist).action_request_promotion()


# ---------------------------------------------------------------------------
# G7 — the promotion itself: routed through the M63 inbox
# ---------------------------------------------------------------------------


class TestPromotionThroughM63:
    def _requested(self, env, make_user):
        scientist = make_user(SCIENTIST)
        reviewer = make_user(REVIEWER)
        owner = make_user(OWNER)
        version = _version(env, _model(env, "lead_scoring"), scientist)
        version.with_user(scientist).action_evaluate()
        _gates(env, version, reviewer)
        version.with_user(scientist).action_request_promotion(justification="ship it")
        return scientist, reviewer, owner, version

    def test_the_direct_deploy_is_refused_even_for_the_owner(self, env, make_user):
        _scientist, _reviewer, owner, version = self._requested(env, make_user)
        with pytest.raises(UserError, match="(?i)from the approver's inbox"):
            version.with_user(owner).action_deploy()

    def test_the_owner_decides_from_the_inbox_and_the_stamp_says_so(self, env, make_user):
        scientist, _reviewer, owner, version = self._requested(env, make_user)
        assert not _task_of(version, scientist), "the registrant must not hold their own task"
        task = _task_of(version, owner)
        assert task, "no pending task reached the Model Owner"
        task.with_user(owner).action_approve(comment="gates reviewed")
        version.invalidate_recordset()
        assert version.state == "deployed"
        assert version.approved_by == owner
        assert version.approved_by != version.create_uid
        assert version.deployed_at
        # and what the owner approved is now what serves
        assert version.model_id.serving_version_id == version

    def test_a_rejected_request_leaves_the_version_undeployed(self, env, make_user):
        _scientist, _reviewer, owner, version = self._requested(env, make_user)
        _task_of(version, owner).with_user(owner).action_reject(comment="metrics thin")
        version.invalidate_recordset()
        assert version.state != "deployed"
        assert not version.deployed_at

    def test_retirement_is_an_owner_act_and_stops_serving(self, env, make_user):
        plain = make_user()
        owner = make_user(OWNER)
        model = _model(env)
        version = env["fix.ml.model.version"].create(
            {
                "model_id": model.id,
                "version": "1.0.0",
                "model_card": "baseline",
                "metrics_json": "{}",
                "state": "deployed",  # seeded baseline shape (su load)
            }
        )
        with pytest.raises(UserError, match="(?i)Model Owner act"):
            version.with_user(plain).action_retire()
        version.with_user(owner).action_retire()
        assert version.state == "retired"
        assert not model.serving_version_id, "a retired version must not serve"


# ---------------------------------------------------------------------------
# G7 — serving gate + run immutability + engine-written suggestion
# ---------------------------------------------------------------------------


class TestServingAndRuns:
    def test_serving_refuses_a_model_with_no_deployed_version(self, env):
        model = _model(env)  # real engine kind, but nothing promoted
        run = env["fix.ml.inference.run"].create(
            {"model_id": model.id, "input_text": json.dumps({"lead_id": 1})}
        )
        with pytest.raises(UserError, match="(?i)no DEPLOYED version"):
            run.action_execute()
        assert run.state == "draft", "the refusal must not forge a run outcome"

    def test_the_seeded_baselines_serve(self, env):
        for xmlid in ("ml_model_fault_classifier", "ml_model_dispatch_scoring"):
            model = env.ref("cd_ml_services.%s" % xmlid)
            assert model.serving_version_id, "%s must have a deployed baseline" % xmlid

    def test_a_run_is_born_draft_and_the_engine_half_is_not_typeable(self, env, make_user):
        plain = make_user()
        model = _model(env)
        with pytest.raises(UserError, match="(?i)created as a DRAFT"):
            env["fix.ml.inference.run"].with_user(plain).create(
                {"model_id": model.id, "state": "computed", "suggested_value": "99"}
            )
        lead = _lead(env)
        run = (
            env["fix.ml.inference.run"]
            .with_user(plain)
            .create({"model_id": model.id, "input_text": json.dumps({"lead_id": lead.id})})
        )
        assert run.state == "draft"

    def test_the_engine_half_is_not_writable_but_the_human_half_is(self, env, make_user):
        plain = make_user()
        # a computed run with a suggestion, on the seeded engine
        seeded = env["fix.ml.model"].search([("code", "=", "LEAD_SCORE_V1")], limit=1)
        run = env["fix.ml.inference.run"].create(
            {"model_id": seeded.id, "input_text": json.dumps({"lead_id": _lead(env).id})}
        )
        run.action_execute()
        assert run.state == "computed"
        assert run.suggested_value, "the engine must derive the suggestion from the output"
        with pytest.raises(UserError, match="(?i)decision log"):
            run.with_user(plain).write({"output_json": '{"score": 100}', "state": "draft"})
        with pytest.raises(UserError, match="(?i)decision log"):
            run.with_user(plain).write({"suggested_value": "100"})
        # the human half is exactly what a portal write may capture
        run.with_user(plain).write({"final_value": run.suggested_value, "override_reason": ""})
        run.invalidate_recordset()
        assert not run.overridden, "same value is not an override"
        run.with_user(plain).write({"final_value": "77"})
        run.invalidate_recordset()
        assert run.overridden, "a different decision is an override, derived not typed"

    def test_the_suggestion_matches_the_output(self, env):
        seeded = env["fix.ml.model"].search([("code", "=", "LEAD_SCORE_V1")], limit=1)
        lead = _lead(env)
        run = _lead_run(env, seeded, lead)
        run.action_execute()
        out = json.loads(run.output_json)
        assert run.suggested_value == str(out["score"])


# ---------------------------------------------------------------------------
# G7/M26-2 — guard rails evaluated on the inference path
# ---------------------------------------------------------------------------


class TestGuardrails:
    def _model_with_version(self, env):
        model = _model(env)
        env["fix.ml.model.version"].create(
            {"model_id": model.id, "version": "1.0.0", "state": "deployed"}
        )
        return model

    def _rail(self, env, model, rule, action="flag"):
        return env["fix.ml.guardrail"].create(
            {"name": "probe rail", "model_id": model.id, "rule": rule, "action": action}
        )

    def test_a_rule_that_does_not_parse_is_refused_at_save(self, env):
        with pytest.raises(ValidationError, match="(?i)does not parse"):
            env["fix.ml.guardrail"].create(
                {"name": "bad rail", "model_id": _model(env).id, "rule": "score is high"}
            )

    def test_a_block_rail_fails_the_run_and_says_why(self, env):
        model = self._model_with_version(env)
        self._rail(env, model, "score >= 0", action="block")
        run = _lead_run(env, model, _lead(env))
        run.action_execute()
        assert run.state == "failed"
        assert "guard rail" in (run.error_note or "")

    def test_a_flag_rail_is_recorded_on_the_output(self, env):
        model = self._model_with_version(env)
        self._rail(env, model, "score >= 0", action="flag")
        run = _lead_run(env, model, _lead(env))
        run.action_execute()
        assert run.state == "computed"
        out = json.loads(run.output_json)
        assert out.get("guardrails"), "the application must be logged on the run"
        assert out["guardrails"][0]["action"] == "flag"
        assert run.suggested_value, "a flag does not suppress the suggestion"

    def test_a_fallback_rail_flags_and_suppresses_the_suggestion(self, env):
        model = self._model_with_version(env)
        self._rail(env, model, "score >= 0", action="fallback")
        run = _lead_run(env, model, _lead(env))
        run.action_execute()
        assert run.state == "computed"
        out = json.loads(run.output_json)
        assert out.get("guardrails") and out["guardrails"][0]["action"] == "fallback"
        assert not run.suggested_value, "the deterministic rule governs, not the engine"

    def test_a_rail_whose_key_is_absent_is_logged_not_silent(self, env):
        model = self._model_with_version(env)
        self._rail(env, model, "confidence < 0.60", action="block")
        run = _lead_run(env, model, _lead(env))
        run.action_execute()
        assert run.state == "computed", "a key-absent rail cannot brick serving"
        out = json.loads(run.output_json)
        assert any(g.get("status") == "not_evaluable" for g in out.get("guardrails", []))


# ---------------------------------------------------------------------------
# E6/X01 — engines read as the caller, inside the caller's companies
# ---------------------------------------------------------------------------


class TestCallerScope:
    def test_a_caller_cannot_score_another_companys_lead(self, env, make_user):
        company_b = env["res.company"].create({"name": "M26 Probe Co B"})
        lead_b = _lead(env, company_id=company_b.id)
        caller = make_user()  # allowed companies: the default company only
        seeded = env["fix.ml.model"].search([("code", "=", "LEAD_SCORE_V1")], limit=1)
        run = (
            env["fix.ml.inference.run"]
            .with_user(caller)
            .create({"model_id": seeded.id, "input_text": json.dumps({"lead_id": lead_b.id})})
        )
        run.with_user(caller).action_execute()
        assert run.state == "failed"
        assert "may not read" in (
            run.error_note or ""
        ), "the X01 sudo-browse leak: the caller used to read any company's lead"

    def test_a_caller_scores_their_own_company_lead(self, env, make_user):
        caller = make_user()
        lead = _lead(env)  # default company
        seeded = env["fix.ml.model"].search([("code", "=", "LEAD_SCORE_V1")], limit=1)
        run = (
            env["fix.ml.inference.run"]
            .with_user(caller)
            .create({"model_id": seeded.id, "input_text": json.dumps({"lead_id": lead.id})})
        )
        run.with_user(caller).action_execute()
        assert run.state == "computed"
        assert json.loads(run.output_json)["score"] >= 0
