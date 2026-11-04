"""cd_metric_registry behaviour tests — M62 governance controls (A11 audit
G1-G6, E5), 2026-11-04.

Replaces the old source-grep suite: every control is now driven through the
live ORM as real users, both ways — the bypass is refused AND the governed
path works. The routed paths (contract activation, metric publication,
retention shortening, declassification) go through the M63 inbox exactly as a
user would: request, then an officer who is not the requester decides.
"""

import datetime
import json

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

OFFICER = "cd_metric_registry.group_data_governance_officer"
REFUSED = (UserError, ValidationError, AccessError)


@pytest.fixture
def env(odoo_env):
    if "fix.data.entity" not in odoo_env:
        pytest.skip("cd_metric_registry is not installed")
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
                    "name": "M62 Probe %d" % counter["n"],
                    "login": "m62.probe.%d@governance.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


@pytest.fixture
def officer(env, make_user):
    return make_user(OFFICER)


@pytest.fixture
def officer_b(env, make_user):
    """A second officer: the one who decides what the first requests."""
    return make_user(OFFICER)


def _entity(env, name, **vals):
    return env["fix.data.entity"].create({"name": name, **vals})


def _task_of(record, user):
    return record.approval_request_id.task_ids.filtered(
        lambda t: t.assigned_user_id == user and t.state == "pending"
    )


def _decide(record, approver, comment="ok"):
    task = _task_of(record, approver)
    assert task, "no pending task for the deciding officer"
    task.with_user(approver).action_approve(comment=comment)


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id:
        domain += [("aggregate", "=", "fix.data.quality.rule"), ("aggregate_id", "=", aggregate_id)]
    return [json.loads(r.payload) for r in env["fix.event.outbox"].search(domain, order="id")]


class TestWarehouseSafetyByLayer:
    """NFR-086c re-read by LAYER (A11 audit G6, M62-7): the old guard was a
    substring match on the entity NAME, so 'dwh.gold.dim_party_nid' sailed
    through. The medallion layer the entity lands in decides, whatever it is
    called."""

    def test_s3_in_a_warehouse_layer_is_refused_whatever_the_name(self, env):
        with pytest.raises(ValidationError, match="NFR-086c"), env.cr.savepoint():
            _entity(
                env,
                "harmless_customer_feed",
                classification="residency_classified",
                warehouse_layer="gold",
            )

    def test_s3_outside_the_warehouse_passes_even_with_a_warehouse_name(self, env):
        e = _entity(env, "dwh.gold.dim_party_nid", classification="residency_classified")
        assert e.warehouse_layer == "none"  # the layer, not the name, decides

    def test_confidential_data_may_land_in_gold(self, env):
        _entity(env, "warehouse.fact_orders", classification="confidential", warehouse_layer="gold")

    def test_moving_a_gold_entity_to_s3_is_refused(self, env):
        table = _entity(env, "warehouse.dim_party", warehouse_layer="gold")
        with pytest.raises(ValidationError, match="must not appear"), env.cr.savepoint():
            table.write({"classification": "residency_classified"})


class TestQualityComparator:
    """A11 audit E5 (M62-1): ONE comparator, owned by the rule, used by the
    rule AND by every test row. The old test row inverted it (observed <=
    threshold 'passed'), so a 10%-complete load passed at a 95% threshold."""

    def _rule(self, env, threshold=95.0, **vals):
        entity = _entity(env, "warehouse.fact_invoices")
        return env["fix.data.quality.rule"].create(
            {"name": "invoice completeness", "entity_id": entity.id, "threshold": threshold, **vals}
        )

    def test_one_comparator_both_sides(self, env):
        rule = self._rule(env)
        rule.action_check(97.5)
        assert (rule.state, rule.last_result) == ("passing", 97.5)
        rule.action_check(95.0)  # at the threshold is not below it
        assert rule.state == "passing"
        assert _events(env, "data_quality.failing", rule.id) == []
        rule.action_check(91.2)
        assert (rule.state, rule.last_result) == ("failing", 91.2)
        payload = _events(env, "data_quality.failing", rule.id)
        assert payload == [
            {
                "entity": "warehouse.fact_invoices",
                "result": 91.2,
                "threshold": 95.0,
                "measured": False,
            }
        ]

    def test_a_test_row_verdict_follows_the_rule_not_its_own_maths(self, env):
        rule = self._rule(env, threshold=95.0)
        row = env["fix.data.quality.test"].create(
            {"rule_id": rule.id, "observed_value": 10.0, "threshold": 95.0}
        )
        assert row.passed is False  # the old comparator said 10 <= 95: passed
        good = env["fix.data.quality.test"].create(
            {"rule_id": rule.id, "observed_value": 99.0, "threshold": 95.0}
        )
        assert good.passed is True

    def test_evidence_rows_are_immutable(self, env):
        rule = self._rule(env)
        row = env["fix.data.quality.test"].create(
            {"rule_id": rule.id, "observed_value": 50.0, "threshold": 95.0}
        )
        with pytest.raises(UserError, match="cannot be edited"), env.cr.savepoint():
            row.write({"observed_value": 100.0})
        with pytest.raises(UserError, match="cannot be deleted"), env.cr.savepoint():
            row.unlink()

    def test_the_runner_measures_instead_of_trusting_typed_numbers(self, env):
        # The measured table is the evidence register itself: nothing seeds
        # it, so the counts are exactly what this test writes.
        seed_entity = _entity(env, "fix_dqt_probe", res_model="fix.data.quality.test")
        seed_rule = env["fix.data.quality.rule"].create(
            {"name": "seed rows", "entity_id": seed_entity.id, "threshold": 95.0}
        )
        rows = env["fix.data.quality.test"]
        rows.create({"rule_id": seed_rule.id, "observed_value": 0.0, "note": "filled"})
        rows.create({"rule_id": seed_rule.id, "observed_value": 0.0, "note": "filled"})
        rows.create({"rule_id": seed_rule.id, "observed_value": 0.0})
        rows.create({"rule_id": seed_rule.id, "observed_value": 0.0})
        entity = _entity(env, "fix_dqt_completeness", res_model="fix.data.quality.test")
        rule = env["fix.data.quality.rule"].create(
            {
                "name": "evidence completeness",
                "entity_id": entity.id,
                "rule_type": "completeness",
                "check_field": "note",
                "threshold": 95.0,
            }
        )
        # 2 of 4 rows carry a note: 50%, far below the 95% threshold
        rule.action_measure()
        assert (rule.state, rule.last_result, rule.last_measured) == ("failing", 50.0, True)
        row = env["fix.data.quality.test"].search([("rule_id", "=", rule.id)], limit=1)
        assert (row.observed_value, row.measured) == (50.0, True)
        payload = _events(env, "data_quality.failing", rule.id)
        assert payload and payload[-1]["measured"] is True

    def test_uniqueness_measures_distinct_values(self, env):
        seed_entity = _entity(env, "fix_dqt_dup_probe", res_model="fix.data.quality.test")
        seed_rule = env["fix.data.quality.rule"].create(
            {"name": "dup seed rows", "entity_id": seed_entity.id, "threshold": 95.0}
        )
        rows = env["fix.data.quality.test"]
        rows.create({"rule_id": seed_rule.id, "observed_value": 0.0, "note": "SAME"})
        rows.create({"rule_id": seed_rule.id, "observed_value": 0.0, "note": "SAME"})
        entity = _entity(env, "fix_dqt_uniqueness", res_model="fix.data.quality.test")
        rule = env["fix.data.quality.rule"].create(
            {
                "name": "evidence uniqueness",
                "entity_id": entity.id,
                "rule_type": "uniqueness",
                "check_field": "note",
                "threshold": 95.0,
            }
        )
        # one distinct note over two populated rows: 50%
        rule.action_measure()
        assert rule.last_result == 50.0

    def test_the_runner_never_invents_a_number(self, env):
        entity = _entity(env, "fix_unmeasured_probe", res_model="fix.data.quality.test")
        no_field = env["fix.data.quality.rule"].create(
            {
                "name": "no check field",
                "entity_id": entity.id,
                "rule_type": "completeness",
                "threshold": 95.0,
            }
        )
        with pytest.raises(UserError, match="no check field"), env.cr.savepoint():
            no_field.action_measure()
        human = env["fix.data.quality.rule"].create(
            {
                "name": "accuracy is judged by people",
                "entity_id": entity.id,
                "rule_type": "accuracy",
                "check_field": "note",
                "threshold": 95.0,
            }
        )
        with pytest.raises(UserError, match="measured by people"), env.cr.savepoint():
            human.action_measure()
        assert no_field.last_checked is False and no_field.last_result == 0.0


class TestDqFailingConsumer:
    """A11 audit G3 (M62-9): data_quality.failing had a producer and no
    consumer — a failing rule never opened an incident and nothing was marked
    degraded. The relay now hands the event to the incident consumer."""

    def _event(self, env, rule, result=8.0, event_id="evt-dq-1"):
        return {
            "event_id": event_id,
            "event_type": "data_quality.failing",
            "aggregate": "fix.data.quality.rule",
            "aggregate_id": rule.id,
            "payload": {
                "entity": rule.entity_id.name,
                "result": result,
                "threshold": rule.threshold,
                "measured": True,
            },
            "metadata": {},
            "company_id": rule.entity_id.company_id.id,
        }

    def test_the_consumer_opens_an_incident_and_degrades_the_entity(self, env):
        entity = _entity(env, "warehouse.fact_degraded")
        rule = env["fix.data.quality.rule"].create(
            {"name": "fresh rows", "entity_id": entity.id, "threshold": 95.0}
        )
        env["fix.data.incident"].consume_data_quality_failing(self._event(env, rule))
        incident = env["fix.data.incident"].search([("source_event_id", "=", "evt-dq-1")])
        assert incident.state == "open" and incident.entity_id == entity
        assert incident.rule_id == rule and incident.classification == "quality_breach"
        assert entity.degraded is True
        # idempotent per event: a redelivery changes nothing
        env["fix.data.incident"].consume_data_quality_failing(self._event(env, rule))
        assert len(env["fix.data.incident"].search([("source_event_id", "=", "evt-dq-1")])) == 1

    def test_a_bad_result_is_high_severity_and_not_duplicated_while_open(self, env):
        entity = _entity(env, "warehouse.fact_bad")
        rule = env["fix.data.quality.rule"].create(
            {"name": "very bad rows", "entity_id": entity.id, "threshold": 95.0}
        )
        env["fix.data.incident"].consume_data_quality_failing(self._event(env, rule, result=8.0))
        first = env["fix.data.incident"].search([("source_event_id", "=", "evt-dq-1")])
        assert first.severity == "high"
        env["fix.data.incident"].consume_data_quality_failing(
            self._event(env, rule, result=8.0, event_id="evt-dq-2")
        )
        open_for_rule = env["fix.data.incident"].search(
            [("rule_id", "=", rule.id), ("state", "=", "open")]
        )
        assert len(open_for_rule) == 1  # still one OPEN incident per rule


class TestIncidentLifecycle:
    """A11 audit G4 (M62-8): owner, classification and root cause before
    close; born open; closed final; high/critical not closed by the reporter."""

    def _incident(self, env, **vals):
        entity = _entity(env, "warehouse.fact_incident_probe")
        base = {"title": "rows missing", "entity_id": entity.id, "severity": "high"}
        base.update(vals)
        return env["fix.data.incident"].create(base)

    def test_an_incident_is_born_open(self, env):
        with pytest.raises(ValidationError, match="created OPEN"), env.cr.savepoint():
            self._incident(env, state="closed")
        with pytest.raises(ValidationError, match="created OPEN"), env.cr.savepoint():
            self._incident(env, state="fixed")
        inc = self._incident(env)
        # and the lifecycle belongs to the actions, not to field edits
        with pytest.raises(UserError, match="only through Fix and Close"), env.cr.savepoint():
            inc.write({"state": "fixed"})

    def test_fix_needs_an_owner_and_close_needs_the_evidence(self, env, make_user):
        inc = self._incident(env)
        with pytest.raises(UserError, match="owner"), env.cr.savepoint():
            inc.action_fix()
        inc.write({"owner_id": make_user().id})
        inc.action_fix()
        assert inc.state == "fixed"
        with pytest.raises(UserError, match="root cause"), env.cr.savepoint():
            inc.action_close()
        inc.write({"root_cause": "upstream feed truncated", "resolution": "replayed the load"})
        inc.action_close()
        assert inc.state == "closed"

    def test_high_severity_is_not_closed_by_its_reporter(self, env, make_user, officer):
        reporter = make_user()
        entity = _entity(env, "warehouse.fact_reporter_probe")
        inc = (
            env["fix.data.incident"]
            .with_user(reporter)
            .create(
                {"title": "spotted by the reporter", "entity_id": entity.id, "severity": "high"}
            )
        )
        assert inc.create_uid == reporter
        inc.write({"owner_id": officer.id, "root_cause": "x", "resolution": "y"})
        inc.with_user(officer).action_fix()
        with pytest.raises(UserError, match="own reporter"), env.cr.savepoint():
            inc.with_user(reporter).action_close()
        inc.with_user(officer).action_close()
        assert inc.state == "closed"

    def test_closed_is_final(self, env):
        inc = self._incident(env)
        inc.write({"owner_id": env.ref("base.user_admin").id, "root_cause": "x", "resolution": "y"})
        inc.action_fix()
        inc.action_close()
        with pytest.raises(UserError, match="final"), env.cr.savepoint():
            inc.write({"severity": "low"})
        with pytest.raises(UserError, match="cannot be deleted"), env.cr.savepoint():
            inc.unlink()


class TestContractLifecycle:
    """A11 audit G1 (M62-5): producer + platform co-signature through M63, the
    active row frozen, changes are new versions."""

    def _contract(self, env, user, dataset="sales.fact_daily"):
        entity = _entity(env, dataset)
        return (
            env["fix.data.contract"]
            .with_user(user)
            .create(
                {
                    "dataset_code": dataset,
                    "name": "%s guarantee" % dataset,
                    "entity_id": entity.id,
                    "producer": "order service team",
                    "producer_signatory_id": user.id,
                    "schema_version": "1.0",
                    "guarantees": "rows by 02:00, no null order_id",
                }
            )
        )

    def test_the_co_signature_comes_producer_first(self, env, officer):
        c = self._contract(env, officer)
        with pytest.raises(UserError, match="producer has not signed"), env.cr.savepoint():
            c.with_user(officer).action_request_approval()
        # the lifecycle cannot be typed either — not written, not born
        with pytest.raises(UserError, match="only through its own actions"), env.cr.savepoint():
            c.with_user(officer).write({"state": "active"})
        entity = _entity(env, "warehouse.fact_born_active_probe")
        with pytest.raises(ValidationError, match="created as a DRAFT"), env.cr.savepoint():
            env["fix.data.contract"].create(
                {
                    "dataset_code": "sales.fact_born",
                    "name": "born active",
                    "entity_id": entity.id,
                    "producer": "x",
                    "schema_version": "1.0",
                    "state": "active",
                }
            )

    def test_the_producer_side_is_signed_by_its_signatory_or_an_officer(
        self, env, officer, make_user
    ):
        c = self._contract(env, officer)
        stranger = make_user()
        with pytest.raises(UserError, match="producer signatory"), env.cr.savepoint():
            c.with_user(stranger).action_producer_sign()
        c.with_user(officer).action_producer_sign()
        assert c.producer_signed_by == officer

    def test_activation_runs_only_from_the_approvers_inbox(self, env, officer, officer_b):
        c = self._contract(env, officer)
        c.with_user(officer).action_producer_sign()
        c.with_user(officer).action_request_approval()
        assert c.approval_state == "pending"
        with pytest.raises(UserError, match="inbox"), env.cr.savepoint():
            c.with_user(officer).action_activate()
        _decide(c, officer_b)
        assert (c.state, c.approval_state) == ("active", "approved")

    def test_the_active_row_is_frozen(self, env, officer, officer_b):
        c = self._contract(env, officer)
        c.with_user(officer).action_producer_sign()
        c.with_user(officer).action_request_approval()
        _decide(c, officer_b)
        for vals in (
            {"schema_version": "9.9"},
            {"breaking_change_notice_days": 0},
            {"guarantees": "whatever now"},
        ):
            with pytest.raises(UserError, match="frozen"), env.cr.savepoint():
                c.with_user(officer).write(vals)

    def test_changes_are_new_versions_and_the_chain_supersedes(self, env, officer, officer_b):
        c = self._contract(env, officer, "sales.fact_daily")
        c.with_user(officer).action_producer_sign()
        c.with_user(officer).action_request_approval()
        _decide(c, officer_b)
        v2 = c.with_user(officer).action_new_version()
        assert (v2.version, v2.state, v2.predecessor_id) == (2, "draft", c)
        assert not v2.producer_signed_by  # the next signature is earned again
        v2.with_user(officer).action_producer_sign()
        v2.with_user(officer).action_request_approval()
        _decide(v2, officer_b)
        assert (c.state, v2.state) == ("deprecated", "active")
        assert v2.schema_version == c.schema_version  # carried, then governed

    def test_a_fork_cannot_steal_the_active_slot(self, env, officer, officer_b):
        c = self._contract(env, officer, "sales.fact_daily")
        c.with_user(officer).action_producer_sign()
        c.with_user(officer).action_request_approval()
        _decide(c, officer_b)
        # a fork: same dataset, no predecessor link
        fork = c.with_user(officer).copy({"version": 9, "state": "draft", "predecessor_id": False})
        fork.with_user(officer).action_producer_sign()
        fork.with_user(officer).action_request_approval()
        with pytest.raises(UserError, match="already has an active version"), env.cr.savepoint():
            _decide(fork, officer_b)
        assert fork.state == "draft" and c.state == "active"


class TestMetricVersions:
    """A11 audit G2 (M62-4): versioned metrics, steward review before the
    request, publication through M63, a consumer register."""

    def _definition(self, env, user, code="fix.first_time_fix"):
        return (
            env["fix.metric.definition"]
            .with_user(user)
            .create(
                {
                    "code": code,
                    "name": "First-time fix rate",
                    "definition": "fixed first visit / all",
                }
            )
        )

    def _version(self, env, user, definition, text="fixed first visit / all dispatched"):
        return (
            env["fix.metric.version"]
            .with_user(user)
            .create(
                {
                    "definition_id": definition.id,
                    "version": len(definition.version_ids) + 1,
                    "definition_text": text,
                }
            )
        )

    def test_the_steward_reviews_before_the_request(self, env, officer, make_user):
        d = self._definition(env, officer)
        v = self._version(env, officer, d)
        with pytest.raises(UserError, match="steward has not reviewed"), env.cr.savepoint():
            v.with_user(officer).action_request_approval()
        stranger = make_user()
        with pytest.raises(UserError, match="data steward"), env.cr.savepoint():
            v.with_user(stranger).action_steward_review()
        v.with_user(officer).action_steward_review()
        assert v.steward_reviewed_by == officer

    def test_publication_runs_through_the_inbox_and_supersedes(self, env, officer, officer_b):
        d = self._definition(env, officer)
        v1 = self._version(env, officer, d)
        v1.with_user(officer).action_steward_review()
        v1.with_user(officer).action_request_approval()
        with pytest.raises(UserError, match="inbox"), env.cr.savepoint():
            v1.with_user(officer).action_approve_publish()
        with pytest.raises(UserError, match="only through its own actions"), env.cr.savepoint():
            v1.with_user(officer).write({"state": "published"})
        _decide(v1, officer_b)
        assert (v1.state, d.state, d.resolve()) == ("published", "published", v1)
        v2 = self._version(env, officer, d, text="fixed first visit / all completed jobs")
        v2.with_user(officer).action_steward_review()
        v2.with_user(officer).action_request_approval()
        _decide(v2, officer_b)
        assert (v1.state, v2.state) == ("retired", "published")
        assert d.resolve() == v2

    def test_the_consumer_register_is_one_row_per_consumer(self, env, officer):
        d = self._definition(env, officer)
        env["fix.metric.consumer"].create({"definition_id": d.id, "consumer": "M25:executive_pack"})
        with pytest.raises(ValidationError), env.cr.savepoint():
            env["fix.metric.consumer"].create(
                {"definition_id": d.id, "consumer": "M25:executive_pack"}
            )

    def test_only_a_published_metric_resolves(self, env, officer, officer_b):
        d = self._definition(env, officer)
        assert not d.resolve()  # a draft metric serves no tile
        v = self._version(env, officer, d)
        v.with_user(officer).action_steward_review()
        v.with_user(officer).action_request_approval()
        _decide(v, officer_b)
        assert d.resolve() == v


class TestRetentionControls:
    """A11 audit G5 (M62-6): statutory floor, positive period, one policy per
    entity, approved shortening, legal hold, disposition with evidence."""

    def _policy(self, env, user, entity_name="warehouse.fact_retention_probe", **vals):
        entity = _entity(env, entity_name)
        base = {"name": "policy", "entity_id": entity.id, "retention_months": 84}
        base.update(vals)
        return env["fix.data.retention.policy"].with_user(user).create(base)

    def test_the_period_is_positive_and_never_below_the_statutory_floor(self, env, officer):
        with pytest.raises(ValidationError, match="at least 1 month"), env.cr.savepoint():
            self._policy(env, officer, retention_months=0)
        with pytest.raises(ValidationError, match="at least 1 month"), env.cr.savepoint():
            self._policy(env, officer, retention_months=-12)
        with pytest.raises(ValidationError, match="statutory floor"), env.cr.savepoint():
            self._policy(env, officer, retention_months=12, statutory_floor_months=60)
        assert self._policy(env, officer, retention_months=84, statutory_floor_months=60)

    def test_one_active_policy_per_entity(self, env, officer):
        entity = _entity(env, "warehouse.fact_retention_dup")
        Policy = env["fix.data.retention.policy"]
        Policy.create({"name": "first", "entity_id": entity.id, "retention_months": 84})
        with pytest.raises(ValidationError, match="one.*policy per entity"), env.cr.savepoint():
            Policy.create({"name": "second", "entity_id": entity.id, "retention_months": 24})

    def test_shortening_is_an_approval_not_an_edit(self, env, officer):
        p = self._policy(env, officer, retention_months=84)
        for actor in (officer, env.ref("base.user_admin")):
            with pytest.raises(UserError, match="retention change"), env.cr.savepoint():
                p.with_user(actor).write({"retention_months": 1})
        p.with_user(officer).write({"retention_months": 120})  # lengthening is free

    def test_shortening_runs_through_the_inbox(self, env, officer, officer_b):
        p = self._policy(env, officer, retention_months=84, statutory_floor_months=6)
        with pytest.raises(UserError, match="below the statutory floor"), env.cr.savepoint():
            p.with_user(officer).action_request_shorten(3)
        p.with_user(officer).action_request_shorten(24)
        assert (p.approval_state, p.pending_months) == ("pending", 24)
        with pytest.raises(UserError, match="inbox"), env.cr.savepoint():
            p.with_user(officer).action_apply_shorten()
        _decide(p, officer_b)
        assert (p.retention_months, p.pending_months) == (24, 0)

    def test_legal_hold_blocks_every_disposition_and_movement(self, env, officer, make_user):
        p = self._policy(env, officer, retention_months=84)
        p.with_user(officer).write({"legal_hold": True})
        with pytest.raises(UserError, match="(?i)legal hold"), env.cr.savepoint():
            p.with_user(officer).write({"retention_months": 120})
        with pytest.raises(UserError, match="(?i)legal hold"), env.cr.savepoint():
            p.with_user(officer).action_request_shorten(24)
        with pytest.raises(UserError, match="(?i)legal hold"), env.cr.savepoint():
            p.with_user(officer).action_purge()
        stranger = make_user()
        with pytest.raises(UserError, match="Governance Officer"), env.cr.savepoint():
            p.with_user(stranger).write({"legal_hold": False})
        p.with_user(officer).write({"legal_hold": False})  # an officer lifts it

    def test_disposition_runs_with_evidence_and_only_for_officers(self, env, officer, make_user):
        # measured over the evidence register: nothing in it is ever a year
        # old in the test database, so the run REPORTS deterministically
        entity = _entity(env, "warehouse.fact_purge_probe", res_model="fix.data.quality.test")
        p = env["fix.data.retention.policy"].create(
            {
                "name": "purge policy",
                "entity_id": entity.id,
                "retention_months": 12,
                "purge_rule": "archive",
            }
        )
        with pytest.raises(UserError, match="Governance Officer"), env.cr.savepoint():
            p.with_user(make_user()).action_purge()
        evidence = p.with_user(officer).action_purge()
        assert len(evidence) == 1 and evidence.ran_by == officer
        with pytest.raises(UserError, match="append-only"), env.cr.savepoint():
            evidence.write({"purged": 999})
        with pytest.raises(UserError, match="never deleted"), env.cr.savepoint():
            p.with_user(officer).unlink()

    def test_purging_deletes_only_when_the_rule_says_delete(self, env, officer):
        # an entity over its own evidence rows: nothing is old enough to be
        # eligible, so the run REPORTS (evidence) without touching a row
        entity = _entity(env, "warehouse.fact_delete_probe", res_model="fix.data.quality.test")
        env["fix.data.retention.policy"].create(
            {
                "name": "delete policy",
                "entity_id": entity.id,
                "retention_months": 36,
                "purge_rule": "delete",
            }
        )
        p = env["fix.data.retention.policy"].search([("entity_id", "=", entity.id)])
        evidence = p.with_user(officer).action_purge()
        assert evidence.action == "reported" and evidence.eligible == 0


class TestRunGuards:
    """A11 audit M62-8 (E40-E45): runs start, conclude through their own
    actions, and cannot claim more rows than they read."""

    def _pipeline(self, env):
        entity = _entity(env, "warehouse.fact_runs")
        return env["fix.data.pipeline"].create(
            {
                "code": "PL-M62-%d" % env["fix.data.pipeline"].search_count([]),
                "name": "nightly",
                "source_system": "odoo_fix",
                "target_entity_id": entity.id,
            }
        )

    def _run(self, env, pipeline, **vals):
        base = {"pipeline_id": pipeline.id}
        base.update(vals)
        return env["fix.data.run"].create(base)

    def test_a_run_is_born_running(self, env):
        pipeline = self._pipeline(env)
        with pytest.raises(ValidationError, match="starts 'running'"), env.cr.savepoint():
            self._run(env, pipeline, state="succeeded", rows_written=1000000)

    def test_row_math_is_checked_on_finish(self, env):
        pipeline = self._pipeline(env)
        run = self._run(env, pipeline, rows_read=0, rows_written=1000000)
        with pytest.raises(UserError, match="cannot create rows"), env.cr.savepoint():
            run.action_finish()
        run.write({"rows_written": 0})
        run.action_finish()
        assert run.state == "succeeded" and run.duration_minutes >= 0.0

    def test_terminal_states_belong_to_the_actions(self, env):
        pipeline = self._pipeline(env)
        run = self._run(env, pipeline)
        run.action_fail()
        with pytest.raises(UserError, match="through Finish or Fail"), env.cr.savepoint():
            run.write({"state": "succeeded"})
        with pytest.raises(UserError, match="running load can fail"), env.cr.savepoint():
            run.action_fail()

    def test_a_retired_pipeline_stays_retired(self, env):
        pipeline = self._pipeline(env)
        pipeline.action_pause()
        pipeline.action_resume()
        pipeline.write({"state": "retired"})
        with pytest.raises(UserError, match="retired is retired"), env.cr.savepoint():
            pipeline.action_resume()

    def test_a_successful_load_measures_the_entity(self, env):
        entity = _entity(env, "fix_dqt_load_probe", res_model="fix.data.quality.test")
        seed_rule = env["fix.data.quality.rule"].create(
            {"name": "load seed", "entity_id": entity.id, "threshold": 95.0}
        )
        env["fix.data.quality.test"].create(
            {"rule_id": seed_rule.id, "observed_value": 0.0, "note": "filled"}
        )
        env["fix.data.quality.rule"].create(
            {
                "name": "load completeness",
                "entity_id": entity.id,
                "rule_type": "completeness",
                "check_field": "note",
                "threshold": 50.0,
            }
        )
        pipeline = env["fix.data.pipeline"].create(
            {
                "code": "PL-RUN-%d" % env["fix.data.pipeline"].search_count([]),
                "name": "into the evidence register",
                "source_system": "odoo_fix",
                "target_entity_id": entity.id,
            }
        )
        run = self._run(env, pipeline, rows_read=1, rows_written=1)
        run.action_finish()
        rule = env["fix.data.quality.rule"].search(
            [("entity_id", "=", entity.id), ("check_field", "=", "note")]
        )
        # the one seeded row carries its note: 100% against a 50% threshold
        assert rule.last_checked and rule.state == "passing" and rule.last_measured


class TestGovernanceAcl:
    """The rule book is the Data Governance Officer's; everyone else reads."""

    def test_the_rule_book_is_officer_write_only(self, env, officer, make_user):
        stranger = make_user()
        assert officer.has_group(OFFICER) and not stranger.has_group(OFFICER)
        with pytest.raises(AccessError), env.cr.savepoint():
            env["fix.data.entity"].with_user(stranger).create({"name": "stranger entity"})
        entity = _entity(env, "officer entity")
        with pytest.raises(AccessError), env.cr.savepoint():
            entity.with_user(stranger).write({"description": "x"})
        # reading is everyone's
        assert entity.with_user(stranger).name == "officer entity"
        with pytest.raises(AccessError), env.cr.savepoint():
            env["fix.data.retention.policy"].with_user(stranger).create(
                {"name": "p", "entity_id": entity.id, "retention_months": 12}
            )

    def test_anyone_may_report_an_incident(self, env, make_user):
        entity = _entity(env, "warehouse.fact_report_probe")
        inc = (
            env["fix.data.incident"]
            .with_user(make_user())
            .create({"title": "spotted by a stranger", "entity_id": entity.id})
        )
        assert inc.state == "open"


class TestDeclassification:
    """A11 audit G6 (M62-7): a downgrade is an approved, time-limited,
    expiring authorisation — never a plain field edit."""

    def test_an_authorisation_is_a_future_dated_downgrade(self, env, officer):
        entity = _entity(env, "warehouse.fact_declass", classification="confidential")
        tomorrow = fields.Date.context_today(entity) + datetime.timedelta(days=1)
        with pytest.raises(ValidationError, match="LESS sensitive"), env.cr.savepoint():
            env["fix.data.declassification.auth"].create(
                {
                    "entity_id": entity.id,
                    "from_classification": "confidential",
                    "to_classification": "residency_classified",
                    "reason": "not a downgrade",
                    "expires_on": tomorrow,
                }
            )
        with pytest.raises(ValidationError, match="expire in the future"), env.cr.savepoint():
            env["fix.data.declassification.auth"].create(
                {
                    "entity_id": entity.id,
                    "from_classification": "confidential",
                    "to_classification": "internal",
                    "reason": "stale",
                    "expires_on": fields.Date.context_today(entity) - datetime.timedelta(days=1),
                }
            )

    def test_a_downgrade_needs_an_approved_authorisation(self, env, officer, officer_b):
        entity = _entity(env, "warehouse.fact_declass", classification="confidential")
        with pytest.raises(UserError, match="declassification authorisation"), env.cr.savepoint():
            entity.write({"classification": "internal"})
        tomorrow = fields.Date.context_today(entity) + datetime.timedelta(days=30)
        auth = (
            env["fix.data.declassification.auth"]
            .with_user(officer)
            .create(
                {
                    "entity_id": entity.id,
                    "from_classification": "confidential",
                    "to_classification": "internal",
                    "reason": "NID columns removed from this feed",
                    "expires_on": tomorrow,
                }
            )
        )
        # approved, but not yet: the request is still the gate
        auth.with_user(officer).action_request_approval()
        with pytest.raises(UserError, match="declassification authorisation"), env.cr.savepoint():
            entity.write({"classification": "internal"})
        # and approval is never typed on the field
        with pytest.raises(UserError, match="approval engine"), env.cr.savepoint():
            auth.with_user(officer).write({"state": "approved"})
        _decide(auth, officer_b)
        entity.write({"classification": "internal"})  # now it may move
        assert entity.classification == "internal"

    def test_authorisation_expiry_reverts_the_classification(self, env, officer, officer_b):
        entity = _entity(env, "warehouse.fact_declass2", classification="confidential")
        tomorrow = fields.Date.context_today(entity) + datetime.timedelta(days=10)
        auth = env["fix.data.declassification.auth"].create(
            {
                "entity_id": entity.id,
                "from_classification": "confidential",
                "to_classification": "internal",
                "reason": "temporary analytics window",
                "expires_on": tomorrow,
            }
        )
        auth.with_user(officer).action_request_approval()
        _decide(auth, officer_b)
        entity.write({"classification": "internal"})
        # time passes (the constraint stops a plain backdate, so age the row
        # directly, as the nightly cron would find it)
        env.cr.execute(
            "UPDATE fix_data_declassification_auth SET expires_on = CURRENT_DATE - 1 "
            "WHERE id = %s",
            (auth.id,),
        )
        env.invalidate_all()
        env["fix.data.declassification.auth"]._cron_expire()
        assert entity.classification == "confidential"  # reverted
        assert env["fix.data.declassification.auth"].browse(auth.id).state == "expired"
