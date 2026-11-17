"""M62 sub-module capture (audit 2026-11-18), driven through the live ORM as
real users: a Data Governance Officer authors, a SECOND officer decides what
the first requests (M63 inbox), a plain internal user is refused, a DPO
starts an M33 erasure request.

Each test proves the governed path works AND the bypass is refused. The
static half (which page offers which capture) is
cd_p03_portal/tests/test_m62_capture_buttons.py.
"""

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

OFFICER = "cd_metric_registry.group_data_governance_officer"
DPO = "cd_party_master.group_party_dpo"
REFUSED = (UserError, ValidationError, AccessError)


@pytest.fixture
def env(odoo_env):
    if "fix.data.source" not in odoo_env:
        pytest.skip("cd_metric_registry 19.0.0.2.0 (M62 capture) is not installed")
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
                    "name": "M62 Capture %d" % counter["n"],
                    "login": "m62.capture.%d@governance.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


@pytest.fixture
def ppl(env, make_user):
    class P:
        pass

    p = P()
    p.officer = make_user(OFFICER)
    p.officer_b = make_user(OFFICER)
    p.plain = make_user()
    p.dpo = make_user(DPO)
    p.steward = env["hr.employee"].create({"name": "M62 Capture Steward"})
    return p


def _decide(record, approver, comment="ok"):
    task = record.approval_request_id.task_ids.filtered(
        lambda t: t.assigned_user_id == approver and t.state == "pending"
    )
    assert task, "no pending task for the deciding officer"
    task.with_user(approver).action_approve(comment=comment)


def _entity(env, name, **vals):
    return env["fix.data.entity"].create({"name": name, **vals})


def _source(env, user, code="SRC-M62", **vals):
    return (
        env["fix.data.source"]
        .with_user(user)
        .create(
            {
                "code": code,
                "name": "Service orders (M01)",
                "source_type": "cdc",
                "owner_module": "M01",
                **vals,
            }
        )
    )


def _pipeline(env, code, entity, **vals):
    return env["fix.data.pipeline"].create(
        {
            "code": code,
            "name": code,
            "source_system": "odoo_fix.%s" % code.lower(),
            "target_entity_id": entity.id,
            **vals,
        }
    )


def _active_contract(env, ppl, entity, code="DS-M62-CAP"):
    contract = (
        env["fix.data.contract"]
        .with_user(ppl.officer)
        .create(
            {
                "dataset_code": code,
                "name": code,
                "entity_id": entity.id,
                "producer": "M01",
                "schema_version": "1.0",
            }
        )
    )
    contract.with_user(ppl.officer).action_producer_sign()
    contract.with_user(ppl.officer).action_request_approval()
    _decide(contract, ppl.officer_b)
    assert contract.state == "active"
    return contract


# ============================================================ page 1
class TestDataSource:
    def test_a_source_is_activated_with_an_owner_and_a_steward(self, env, ppl):
        src = _source(env, ppl.officer)
        assert src.state == "draft"
        with pytest.raises(UserError, match="BRU-DAT-09"), env.cr.savepoint():
            src.with_user(ppl.officer).action_activate()
        src.with_user(ppl.officer).write(
            {"business_owner_id": ppl.officer_b.id, "steward_id": ppl.steward.id}
        )
        src.with_user(ppl.officer).action_activate()
        assert (src.state, src.activated_by) == ("active", ppl.officer)

    def test_the_bypasses_are_refused(self, env, ppl):
        with pytest.raises(AccessError), env.cr.savepoint():
            _source(env, ppl.plain)
        with pytest.raises(ValidationError, match="DRAFT"), env.cr.savepoint():
            _source(env, ppl.officer, code="SRC-BORN", state="active")
        src = _source(env, ppl.officer, code="SRC-W")
        with pytest.raises(UserError, match="Activate and"), env.cr.savepoint():
            src.with_user(ppl.officer).write({"state": "active"})
        with pytest.raises(ValidationError, match="credential"), env.cr.savepoint():
            _source(env, ppl.officer, code="SRC-PW", connection_ref="host=db password=hunter2")
        with pytest.raises(ValidationError, match="credential"), env.cr.savepoint():
            _source(env, ppl.officer, code="SRC-URL", connection_ref="postgres://u:p@db/x")
        _source(env, ppl.officer, code="SRC-OK", connection_ref="vault:odoo_fix_replica")
        with pytest.raises(UserError, match="never deleted"), env.cr.savepoint():
            src.sudo().unlink()

    def test_a_pipeline_ingests_only_from_an_active_source(self, env, ppl):
        entity = _entity(env, "M62 cap orders")
        src = _source(env, ppl.officer)
        with pytest.raises(ValidationError, match="ACTIVE source"), env.cr.savepoint():
            _pipeline(env, "PL-DRAFT-SRC", entity, data_source_id=src.id)
        src.with_user(ppl.officer).write(
            {"business_owner_id": ppl.officer_b.id, "steward_id": ppl.steward.id}
        )
        src.with_user(ppl.officer).action_activate()
        pipe = env["fix.data.pipeline"].create(
            {"code": "PL-SRC", "name": "x", "target_entity_id": entity.id, "data_source_id": src.id}
        )
        assert pipe.source_system == "SRC-M62", "the source system defaults to the source's code"
        with pytest.raises(UserError, match="pause or"), env.cr.savepoint():
            src.with_user(ppl.officer).action_retire()
        pipe.action_pause()
        src.with_user(ppl.officer).action_retire()
        assert src.state == "retired"


class TestPipelineOrderAndBackfill:
    def test_a_downstream_run_waits_for_its_upstream(self, env):
        up_e, down_e = _entity(env, "M62 cap bronze"), _entity(env, "M62 cap bronze 2")
        up = _pipeline(env, "PL-UP", up_e)
        down = _pipeline(env, "PL-DOWN", down_e, upstream_ids=[(6, 0, up.ids)])
        Run = env["fix.data.run"]
        with pytest.raises(ValidationError, match="never run"), env.cr.savepoint():
            Run.create({"pipeline_id": down.id})
        first = Run.create({"pipeline_id": up.id})
        with pytest.raises(ValidationError, match="still running"), env.cr.savepoint():
            Run.create({"pipeline_id": down.id})
        first.write({"failure_reason": "source timeout"})
        first.action_fail()
        with pytest.raises(ValidationError, match="AUT-DAT-01"), env.cr.savepoint():
            Run.create({"pipeline_id": down.id})
        second = Run.create({"pipeline_id": up.id, "rows_read": 10, "rows_written": 10})
        second.action_finish()
        assert Run.create({"pipeline_id": down.id}).state == "running"

    def test_no_dependency_cycle(self, env):
        e = _entity(env, "M62 cap cyc")
        a = _pipeline(env, "PL-A", e)
        b = _pipeline(env, "PL-B", e, upstream_ids=[(6, 0, a.ids)])
        with pytest.raises(ValidationError, match="after itself"), env.cr.savepoint():
            a.write({"upstream_ids": [(6, 0, b.ids)]})
        with pytest.raises(ValidationError, match="after itself"), env.cr.savepoint():
            a.write({"upstream_ids": [(6, 0, a.ids)]})

    def test_a_backfill_states_its_period_and_reason(self, env):
        pipe = _pipeline(env, "PL-BF", _entity(env, "M62 cap bf"))
        Run = env["fix.data.run"]
        with pytest.raises(ValidationError, match="Period From"), env.cr.savepoint():
            Run.create({"pipeline_id": pipe.id, "kind": "backfill"})
        terms = {"period_from": "2026-10-01", "period_to": "2026-10-31"}
        with pytest.raises(ValidationError, match="state why"), env.cr.savepoint():
            Run.create({"pipeline_id": pipe.id, "kind": "backfill", **terms})
        with pytest.raises(ValidationError, match="ends after"), env.cr.savepoint():
            Run.create(
                {
                    "pipeline_id": pipe.id,
                    "kind": "backfill",
                    "period_from": "2026-11-01",
                    "period_to": "2026-10-01",
                    "reason": "x",
                }
            )
        bf = Run.create(
            {"pipeline_id": pipe.id, "kind": "backfill", "reason": "late M19 postings", **terms}
        )
        assert bf.state == "running"

    def test_a_replay_names_a_concluded_run_of_the_same_pipeline(self, env):
        e = _entity(env, "M62 cap replay")
        pipe, other = _pipeline(env, "PL-RP", e), _pipeline(env, "PL-RP2", e)
        Run = env["fix.data.run"]
        terms = {"period_from": "2026-10-01", "period_to": "2026-10-31", "reason": "bug fix"}
        base = Run.create({"pipeline_id": pipe.id, "rows_read": 5, "rows_written": 5})
        with pytest.raises(ValidationError, match="names the run"), env.cr.savepoint():
            Run.create({"pipeline_id": pipe.id, "kind": "replay", **terms})
        with pytest.raises(ValidationError, match="still running"), env.cr.savepoint():
            Run.create(
                {"pipeline_id": pipe.id, "kind": "replay", "replay_of_run_id": base.id, **terms}
            )
        base.action_finish()
        with pytest.raises(ValidationError, match="same pipeline"), env.cr.savepoint():
            Run.create(
                {"pipeline_id": other.id, "kind": "replay", "replay_of_run_id": base.id, **terms}
            )
        with pytest.raises(ValidationError, match="Only a replay"), env.cr.savepoint():
            Run.create({"pipeline_id": pipe.id, "replay_of_run_id": base.id})
        rp = Run.create(
            {"pipeline_id": pipe.id, "kind": "replay", "replay_of_run_id": base.id, **terms}
        )
        assert rp.replay_of_run_id == base

    def test_silver_needs_an_active_contract(self, env, ppl):
        e = _entity(env, "M62 cap silver")
        pipe = _pipeline(env, "PL-SV", e, layer="silver")
        Run = env["fix.data.run"]
        with pytest.raises(ValidationError, match="BRU-DAT-10"), env.cr.savepoint():
            Run.create({"pipeline_id": pipe.id, "stage": "silver"})
        bronze = Run.create({"pipeline_id": pipe.id, "stage": "bronze"})
        with pytest.raises(ValidationError, match="BRU-DAT-10"), env.cr.savepoint():
            bronze.write({"stage": "gold"})
        _active_contract(env, ppl, e)
        assert Run.create({"pipeline_id": pipe.id, "stage": "silver"}).stage == "silver"

    def test_a_concluded_run_is_history(self, env):
        pipe = _pipeline(env, "PL-HIST", _entity(env, "M62 cap hist"))
        run = env["fix.data.run"].create(
            {"pipeline_id": pipe.id, "rows_read": 5, "rows_written": 5}
        )
        run.action_finish()
        with pytest.raises(UserError, match="history"), env.cr.savepoint():
            run.write({"rows_written": 5000})
        with pytest.raises(UserError, match="history"), env.cr.savepoint():
            run.write({"stage": "gold"})
        run.write({"rows_written": 5})  # an unchanged echo is not an edit


# ============================================================ page 3
class TestDimensionalModel:
    def test_a_fact_declares_its_grain(self, env):
        with pytest.raises(ValidationError, match="BRU-DAT-08"), env.cr.savepoint():
            _entity(env, "fact_service_order", model_kind="fact")
        fact = _entity(
            env,
            "fact_service_order",
            model_kind="fact",
            grain_declaration="one row per service order per status change",
        )
        with pytest.raises(ValidationError, match="BRU-DAT-08"), env.cr.savepoint():
            fact.write({"grain_declaration": " "})

    def test_the_odoo_model_must_exist(self, env):
        with pytest.raises(ValidationError, match="not a model"), env.cr.savepoint():
            _entity(env, "bogus", res_model="fix.no.such.model")
        assert _entity(env, "orders", res_model="res.partner").res_model == "res.partner"

    def test_a_dimension_tracks_its_history_and_conforms_facts(self, env, ppl):
        dim_e = _entity(env, "dim_party")
        fact = _entity(env, "fact_job", model_kind="fact", grain_declaration="one row per job")
        other = _entity(env, "loose table")
        Dim = env["fix.data.dimension"].with_user(ppl.officer)
        base = {"name": "Party", "entity_id": dim_e.id, "natural_key": "party_code"}
        with pytest.raises(ValidationError, match="attributes it tracks"), env.cr.savepoint():
            Dim.create(dict(base, scd_type="type2"))
        with pytest.raises(ValidationError, match="Only facts"), env.cr.savepoint():
            Dim.create(dict(base, scd_type="type1", fact_entity_ids=[(6, 0, other.ids)]))
        with pytest.raises(ValidationError, match="is a fact"), env.cr.savepoint():
            Dim.create(dict(base, entity_id=fact.id, scd_type="type1"))
        dim = Dim.create(
            dict(
                base,
                scd_type="type2",
                tracked_attributes="segment, branch",
                fact_entity_ids=[(6, 0, fact.ids)],
            )
        )
        assert dim_e.model_kind == "dimension", "the entity takes its dimension role"
        with pytest.raises(AccessError), env.cr.savepoint():
            env["fix.data.dimension"].with_user(ppl.plain).create(
                dict(base, entity_id=other.id, scd_type="type1")
            )
        assert dim.fact_entity_ids == fact


# ============================================================ page 4
class TestMetricVersionsAndConsumers:
    def _definition(self, env, user, code="MET-M62-CAP"):
        return (
            env["fix.metric.definition"]
            .with_user(user)
            .create({"code": code, "name": code, "definition": "a / b"})
        )

    def _publish(self, env, ppl, d, text, reason=None):
        vals = {"definition_id": d.id, "definition_text": text}
        if reason:
            vals["change_reason"] = reason
        v = env["fix.metric.version"].with_user(ppl.officer).create(vals)
        v.with_user(ppl.officer).action_steward_review()
        v.with_user(ppl.officer).action_request_approval()
        _decide(v, ppl.officer_b)
        return v

    def test_versions_are_numbered_by_the_server(self, env, ppl):
        d = self._definition(env, ppl.officer)
        v1 = self._publish(env, ppl, d, "fixed / dispatched")
        v2 = (
            env["fix.metric.version"]
            .with_user(ppl.officer)
            .create({"definition_id": d.id, "definition_text": "fixed / completed"})
        )
        assert (v1.version, v2.version) == (1, 2)

    def test_the_definition_follows_the_published_version(self, env, ppl):
        """BRU-DAT-01: one definition. The definition's text, grain and source
        are the published version's, never a second text beside it."""
        d = self._definition(env, ppl.officer)
        self._publish(env, ppl, d, "fixed first visit / all dispatched")
        assert d.definition == "fixed first visit / all dispatched" == d.resolve().definition_text

    def test_a_published_definition_has_no_edit_path(self, env, ppl):
        d = self._definition(env, ppl.officer)
        self._publish(env, ppl, d, "x / y")
        for vals in ({"definition": "1"}, {"grain": "day"}, {"code": "MET-RENAMED"}):
            with pytest.raises(UserError, match="BRU-DAT-02"), env.cr.savepoint():
                d.with_user(ppl.officer).write(vals)
        d.with_user(ppl.officer).write({"name": "Renamed label", "definition": "x / y"})
        assert d.name == "Renamed label" and d.definition == "x / y"

    def test_a_later_version_records_why_and_who_it_reaches(self, env, ppl):
        d = self._definition(env, ppl.officer)
        self._publish(env, ppl, d, "a / b")
        env["fix.metric.consumer"].with_user(ppl.officer).create(
            {"definition_id": d.id, "consumer": "M25:executive_pack", "consumer_type": "dashboard"}
        )
        v2 = (
            env["fix.metric.version"]
            .with_user(ppl.officer)
            .create({"definition_id": d.id, "definition_text": "a / c"})
        )
        v2.with_user(ppl.officer).action_steward_review()
        with pytest.raises(UserError, match="FR-DAT-019"), env.cr.savepoint():
            v2.with_user(ppl.officer).action_request_approval()
        v2.with_user(ppl.officer).write({"change_reason": "denominator was wrong"})
        v2.with_user(ppl.officer).action_request_approval()
        assert "M25:executive_pack (Dashboard)" in v2.impact_snapshot
        _decide(v2, ppl.officer_b)
        assert d.definition == "a / c" and d.resolve() == v2
        assert any("M25:executive_pack" in (m.body or "") for m in v2.message_ids)

    def test_a_reviewed_version_text_is_frozen(self, env, ppl):
        d = self._definition(env, ppl.officer)
        v = (
            env["fix.metric.version"]
            .with_user(ppl.officer)
            .create({"definition_id": d.id, "definition_text": "a / b"})
        )
        v.with_user(ppl.officer).write({"definition_text": "a / bb"})  # draft: still editable
        v.with_user(ppl.officer).action_steward_review()
        with pytest.raises(UserError, match="Draft a new version"), env.cr.savepoint():
            v.with_user(ppl.officer).write({"definition_text": "a / z"})

    def test_no_retirement_while_consumers_remain(self, env, ppl):
        d = self._definition(env, ppl.officer)
        self._publish(env, ppl, d, "a / b")
        consumer = (
            env["fix.metric.consumer"]
            .with_user(ppl.officer)
            .create({"definition_id": d.id, "consumer": "M54:cost_centre_pack"})
        )
        with pytest.raises(UserError, match="BRU-DAT-04"), env.cr.savepoint():
            d.with_user(ppl.officer).action_retire()
        consumer.with_user(ppl.officer).unlink()
        d.with_user(ppl.officer).action_retire()
        assert d.state == "retired"

    def test_plain_users_only_read(self, env, ppl):
        d = self._definition(env, ppl.officer)
        with pytest.raises(AccessError), env.cr.savepoint():
            env["fix.metric.consumer"].with_user(ppl.plain).create(
                {"definition_id": d.id, "consumer": "rogue"}
            )
        with pytest.raises(AccessError), env.cr.savepoint():
            env["fix.metric.version"].with_user(ppl.plain).create(
                {"definition_id": d.id, "definition_text": "1"}
            )


class TestGlossary:
    def test_one_meaning_per_term_with_an_owner(self, env, ppl):
        G = env["fix.glossary.term"].with_user(ppl.officer)
        metric = env["fix.metric.definition"].create(
            {"code": "MET-GL", "name": "FTF", "definition": "a / b"}
        )
        term = G.create(
            {
                "term_en": "First-Time Fix",
                "term_bn": "প্রথমবারে মেরামত",
                "definition": "Jobs fixed on the first visit over all jobs.",
                "owner_id": ppl.officer_b.id,
                "metric_ids": [(6, 0, metric.ids)],
            }
        )
        assert term.metric_ids == metric
        with pytest.raises(ValidationError, match="already in the glossary"), env.cr.savepoint():
            G.create({"term_en": "first-time fix", "definition": "x", "owner_id": ppl.officer.id})
        with pytest.raises(ValidationError, match="business owner"), env.cr.savepoint():
            G.create({"term_en": "No owner", "definition": "x"})
        with pytest.raises(AccessError), env.cr.savepoint():
            env["fix.glossary.term"].with_user(ppl.plain).create(
                {"term_en": "Rogue", "definition": "x", "owner_id": ppl.plain.id}
            )
        assert env["fix.glossary.term"].with_user(ppl.plain).search([("id", "=", term.id)])


# ============================================================ page 5
class TestQualityRuleCapture:
    def test_a_check_field_must_exist_on_the_entity(self, env, ppl):
        e = _entity(env, "partners", res_model="res.partner")
        Rule = env["fix.data.quality.rule"].with_user(ppl.officer)
        with pytest.raises(ValidationError, match="never measure"), env.cr.savepoint():
            Rule.create({"name": "r", "entity_id": e.id, "check_field": "no_such_column"})
        rule = Rule.create(
            {"name": "partner email", "entity_id": e.id, "check_field": "email", "threshold": 0.0}
        )
        rule.with_user(ppl.officer).action_measure()
        assert rule.last_measured is True and rule.state == "passing"

    def test_the_rule_severity_drives_the_incident(self, env, ppl):
        e = _entity(env, "sev")
        rule = env["fix.data.quality.rule"].create(
            {"name": "sev rule", "entity_id": e.id, "severity": "critical"}
        )
        env["fix.data.incident"].consume_data_quality_failing(
            {"event_id": "evt-m62-sev", "aggregate_id": rule.id, "payload": {"result": 90.0}}
        )
        incident = env["fix.data.incident"].search([("source_event_id", "=", "evt-m62-sev")])
        assert incident.severity == "critical"
        rule2 = env["fix.data.quality.rule"].create({"name": "no sev", "entity_id": e.id})
        env["fix.data.incident"].consume_data_quality_failing(
            {"event_id": "evt-m62-nosev", "aggregate_id": rule2.id, "payload": {"result": 90.0}}
        )
        derived = env["fix.data.incident"].search([("source_event_id", "=", "evt-m62-nosev")])
        assert derived.severity == "medium", "without a rule severity the old derivation holds"


# ============================================================ page 7
class TestDeclassificationCapture:
    def test_from_is_the_current_classification(self, env, ppl):
        e = _entity(env, "customer api", classification="confidential")
        Auth = env["fix.data.declassification.auth"].with_user(ppl.officer)
        later = fields.Date.add(fields.Date.context_today(Auth), days=30)
        auth = Auth.create(
            {
                "entity_id": e.id,
                "to_classification": "internal",
                "reason": "aggregated",
                "expires_on": later,
            }
        )
        assert auth.from_classification == "confidential"
        with pytest.raises(ValidationError, match="current classification"), env.cr.savepoint():
            Auth.create(
                {
                    "entity_id": e.id,
                    "from_classification": "residency_classified",
                    "to_classification": "internal",
                    "reason": "x",
                    "expires_on": later,
                }
            )
        with pytest.raises(ValidationError, match="LESS sensitive"), env.cr.savepoint():
            Auth.create(
                {
                    "entity_id": e.id,
                    "to_classification": "residency_classified",
                    "reason": "x",
                    "expires_on": later,
                }
            )
        auth.with_user(ppl.officer).action_request_approval()
        _decide(auth, ppl.officer_b)
        assert auth.state == "approved"
        e.with_user(ppl.officer).write({"classification": "internal"})
        assert e.classification == "internal"


class TestAnalyticalErasure:
    def _request(self, env, ppl, kind="erasure"):
        partner = env["res.partner"].create({"name": "M62 Erasure Subject"})
        req = env["fix.rights.request"].create({"partner_id": partner.id, "request_type": kind})
        req.with_user(ppl.dpo).action_verify()
        return req

    def test_starting_an_erasure_opens_the_propagation(self, env, ppl):
        req = self._request(env, ppl)
        req.with_user(ppl.dpo).action_start()
        erasure = env["fix.data.erasure"].search([("request_id", "=", req.id)])
        assert erasure and erasure.state == "open" and erasure.partner_id == req.partner_id
        other = self._request(env, ppl, kind="access")
        other.with_user(ppl.dpo).action_start()
        assert not env["fix.data.erasure"].search([("request_id", "=", other.id)])

    def test_completion_needs_every_layer_and_evidence(self, env, ppl):
        req = self._request(env, ppl)
        req.with_user(ppl.dpo).action_start()
        erasure = env["fix.data.erasure"].search([("request_id", "=", req.id)])
        E = erasure.with_user(ppl.officer)
        E.write({"bronze_done": True, "silver_done": True, "gold_done": True})
        with pytest.raises(UserError, match="BRU-DAT-15"), env.cr.savepoint():
            E.action_complete()
        E.write({"feature_store_done": True, "extracts_done": True})
        with pytest.raises(UserError, match="evidence"), env.cr.savepoint():
            E.action_complete()
        with pytest.raises(UserError, match="Complete"), env.cr.savepoint():
            E.write({"state": "completed"})
        E.write({"evidence_ref": "PURGE-JOB-2026-11-18-01"})
        with pytest.raises(UserError, match="Officer"), env.cr.savepoint():
            erasure.with_user(ppl.dpo).action_complete()
        E.action_complete()
        assert (erasure.state, erasure.completed_by) == ("completed", ppl.officer)
        with pytest.raises(UserError, match="final"), env.cr.savepoint():
            E.write({"note": "late edit"})
        with pytest.raises(UserError, match="never deleted"), env.cr.savepoint():
            erasure.sudo().unlink()

    def test_only_an_erasure_request_one_each_and_no_plain_read(self, env, ppl):
        access = self._request(env, ppl, kind="access")
        with pytest.raises(ValidationError, match="only an erasure"), env.cr.savepoint():
            env["fix.data.erasure"].with_user(ppl.officer).create({"request_id": access.id})
        req = self._request(env, ppl)
        env["fix.data.erasure"].with_user(ppl.officer).create({"request_id": req.id})
        with pytest.raises(Exception), env.cr.savepoint():  # noqa: B017 - the UNIQUE constraint
            env["fix.data.erasure"].with_user(ppl.officer).create({"request_id": req.id})
        with pytest.raises(AccessError), env.cr.savepoint():
            env["fix.data.erasure"].with_user(ppl.plain).search([])
        assert env["fix.data.erasure"].with_user(ppl.dpo).search([("request_id", "=", req.id)])


# ============================================================ wiring
class TestDeployment:
    def test_the_registers_are_served_and_sequenced(self, env):
        from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

        for model in (
            "fix.data.source",
            "fix.data.dimension",
            "fix.glossary.term",
            "fix.data.erasure",
            "fix.metric.version",
            "fix.metric.consumer",
            "fix.data.declassification.auth",
        ):
            assert model in api.SURFACES, model
        assert env["ir.sequence"].search_count([("code", "=", "fix.data.erasure")])
