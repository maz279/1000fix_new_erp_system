# Behavioural tests for M64-core MDM governance on the live ORM (`odoo_env`,
# rolled back after every test): the change-request state machine, the
# survivorship engine and the stewardship quality audit.
import contextlib
import json

import pytest
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    inbox_task,
)
from odoo.exceptions import UserError, ValidationError

STEWARD = "cd_entity_config.group_mdm_domain_steward"


@contextlib.contextmanager
def _rejects(env, exc, match):
    """pytest.raises inside a savepoint: an expected failure never leaves a
    half-applied write in the shared test transaction."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info


@pytest.fixture
def make_user(odoo_env):
    counter = {"n": 0}

    def _make(*xmlids):
        counter["n"] += 1
        groups = [odoo_env.ref("base.group_user").id] + [odoo_env.ref(x).id for x in xmlids]
        return (
            odoo_env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "MDM Probe %d" % counter["n"],
                    "login": "mdm.probe.%d@test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


@pytest.fixture
def stewards(make_user):
    return {"a": make_user(STEWARD), "b": make_user(STEWARD)}


def _events(env, event_type, rec, aggregate="fix.mdm.change.request"):
    return env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", aggregate),
            ("aggregate_id", "=", rec.id),
        ]
    )


def _request(env, **vals):
    partner = vals.pop("partner", None) or env["res.partner"].create(
        {"name": "Golden Party", "phone": "01700000001"}
    )
    vals = {
        "title": "Fix the phone",
        "model_name": "res.partner",
        "record_id": partner.id,
        "proposed_changes": json.dumps({"phone": "01711111111"}),
        **vals,
    }
    return env["fix.mdm.change.request"].create(vals)


# --- fix.mdm.change.request ---------------------------------------------------


def test_create_emits_change_requested(odoo_env):
    cr = _request(odoo_env)
    assert cr.state == "draft"
    # A12 P1-2: the request now carries the governed sequence (MDM/YYYY/…),
    # not the pre-upgrade "NEW" placeholder.
    assert cr.reference.startswith("MDM/%d/" % odoo_env.cr.now().year)
    payload = json.loads(_events(odoo_env, "mdm.change_requested", cr).payload)
    assert payload == {
        "reference": cr.reference,
        "model_name": "res.partner",
        "record_id": cr.record_id,
        "state": "draft",
    }


def test_submit_snapshots_the_governed_fields(odoo_env):
    cr = _request(odoo_env)
    cr.action_submit()
    assert cr.state == "submitted"
    assert cr.submitted_by.id == odoo_env.uid
    snapshot = json.loads(cr.current_values)
    assert snapshot["phone"] == "01700000001"
    assert snapshot["id"] == cr.record_id


def test_submit_twice_is_refused(odoo_env):
    cr = _request(odoo_env)
    cr.action_submit()
    with _rejects(odoo_env, ValidationError, match="Only draft requests"):
        cr.action_submit()


def test_a_request_that_proposes_nothing_is_refused(odoo_env):
    """P1-2: the proposed values are the point of the request — a request
    without them is refused at create, not silently captured empty."""
    with _rejects(odoo_env, ValidationError, match="proposes nothing"):
        _request(odoo_env, proposed_changes=False)


def test_a_request_for_a_missing_target_is_refused_at_create(odoo_env):
    """M64-12: a request for a record that is gone cannot even be raised."""
    with _rejects(odoo_env, ValidationError, match="gone"):
        _request(odoo_env, record_id=999_999_999)


def test_a_request_for_an_unknown_model_is_refused_at_create(odoo_env):
    with _rejects(odoo_env, ValidationError, match="no.such.model"):
        _request(odoo_env, model_name="no.such.model")


def test_approve_from_review_states_emits_change_approved(odoo_env, stewards):
    """A12 P1-2: the decision is ROUTED — a steward who is not the proposer
    decides from the M63 approver's inbox; direct state writes are refused."""
    cr = _request(odoo_env)
    cr.action_submit()
    approve_via_inbox(cr, stewards["b"])
    assert cr.state == "approved"
    assert cr.reviewed_by == stewards["b"] and cr.reviewed_at
    payload = json.loads(_events(odoo_env, "mdm.change_approved", cr).payload)
    assert payload["state"] == "approved"
    # the direct paths the old test used are now the attack surface. odoo_env
    # runs as the superuser (su), which the guard trusts, so the probe runs
    # as a real user: the state cannot be typed, only transitioned.
    with _rejects(odoo_env, UserError, match="cannot be set directly"):
        cr.with_user(stewards["a"]).write({"state": "under_review"})
    with _rejects(odoo_env, ValidationError, match="Only submitted requests"):
        cr.sudo().action_approve()  # already decided: from-state refuses


def test_approve_from_draft_is_refused(odoo_env):
    cr = _request(odoo_env)
    with _rejects(odoo_env, ValidationError, match="Only submitted requests can be approved"):
        cr.sudo().action_approve()


def test_reject_emits_change_rejected(odoo_env, stewards):
    cr = _request(odoo_env)
    cr.action_submit()
    cr.action_request_approval()
    task = inbox_task(cr, stewards["b"])
    task.with_user(stewards["b"]).action_reject("wrong source document")
    assert cr.state == "rejected" and cr.reviewed_at
    assert len(_events(odoo_env, "mdm.change_rejected", cr)) == 1
    assert not _events(odoo_env, "mdm.change_approved", cr)


def test_writes_without_a_state_change_emit_nothing(odoo_env):
    cr = _request(odoo_env)
    cr.write({"review_notes": "checked the source document", "priority": "high"})
    assert cr.state == "draft"
    assert not _events(odoo_env, "mdm.change_approved", cr)
    assert not _events(odoo_env, "mdm.change_rejected", cr)


def test_a_cancelled_request_emits_no_decision_event(odoo_env):
    cr = _request(odoo_env)
    cr.action_submit()
    cr.action_cancel()
    assert cr.state == "cancelled"
    assert not _events(odoo_env, "mdm.change_approved", cr)
    assert not _events(odoo_env, "mdm.change_rejected", cr)


# --- fix.mdm.golden.rule ---------------------------------------------------------

CANDIDATES = [
    {"value": "017-old", "write_date": "2026-01-01", "verification_status": "unverified"},
    {"value": "", "write_date": "2026-12-31"},
    {"value": "017-verified-long", "write_date": "2026-03-01", "verification_status": "verified"},
    {"value": "017-new", "write_date": "2026-06-01", "verification_status": "unverified"},
]


def _rule(env, strategy, field_name="phone"):
    return env["fix.mdm.golden.rule"].create(
        {"model_name": "res.partner", "field_name": field_name, "strategy": strategy}
    )


def test_resolve_without_rule_picks_most_recent_non_empty(odoo_env):
    Rule = odoo_env["fix.mdm.golden.rule"]
    assert Rule.resolve("res.partner", "x_unruled", CANDIDATES)["value"] == "017-new"
    assert Rule.resolve("res.partner", "x_unruled", [{"value": ""}, {}]) is None


def test_resolve_with_rule_and_only_empty_candidates_is_none(odoo_env):
    _rule(odoo_env, "most_recent")
    assert (
        odoo_env["fix.mdm.golden.rule"].resolve("res.partner", "phone", [{"value": None}]) is None
    )


@pytest.mark.parametrize(
    ("strategy", "expected"),
    [
        ("most_recent", "017-new"),
        ("most_verified", "017-verified-long"),
        ("longest_value", "017-verified-long"),
        ("highest_priority_source", "017-old"),
        ("manual_review", None),
    ],
)
def test_resolve_applies_the_rule_strategy(odoo_env, strategy, expected):
    _rule(odoo_env, strategy)
    winner = odoo_env["fix.mdm.golden.rule"].resolve("res.partner", "phone", CANDIDATES)
    assert (winner["value"] if winner else None) == expected


def test_most_verified_falls_back_to_first_non_empty(odoo_env):
    _rule(odoo_env, "most_verified")
    unverified = [c for c in CANDIDATES if c.get("verification_status") != "verified"]
    winner = odoo_env["fix.mdm.golden.rule"].resolve("res.partner", "phone", unverified)
    assert winner["value"] == "017-old"


def test_archived_rule_is_ignored(odoo_env):
    _rule(odoo_env, "manual_review").active = False
    winner = odoo_env["fix.mdm.golden.rule"].resolve("res.partner", "phone", CANDIDATES)
    assert winner["value"] == "017-new"  # the no-rule default


# --- fix.mdm.stewardship -----------------------------------------------------------


def _steward(env, domain, **vals):
    return env["fix.mdm.stewardship"].create(
        {"name": f"{domain} stewardship", "domain": domain, "lead_steward_id": env.uid, **vals}
    )


def test_scores_start_unmeasured_at_zero(odoo_env):
    rec = _steward(odoo_env, "party")
    assert (rec.completeness_score, rec.uniqueness_score, rec.validity_score) == (0.0, 0.0, 0.0)
    assert (rec.overall_quality_score, rec.audit_state) == (0.0, "not_audited")


def test_quality_index_is_the_weighted_dama_score(odoo_env):
    rec = _steward(odoo_env, "party")
    # the scores are guarded: only the audit action may set them
    rec._guarded().write(
        {"completeness_score": 90.0, "uniqueness_score": 80.0, "validity_score": 70.0}
    )
    assert rec.overall_quality_score == 81.0  # 0.4*90 + 0.3*80 + 0.3*70
    rec._guarded().write({"validity_score": 100.0})
    assert rec.overall_quality_score == 90.0


@pytest.mark.parametrize(
    ("domain", "model", "domain_filter"),
    [
        ("party", "res.partner", [("is_company", "=", False)]),
        ("product", "fix.catalogue.item", []),
        ("asset", "fix.device", []),
        ("financial", "operating.unit", []),
    ],
)
def test_audit_measures_the_domain_master_and_emits(odoo_env, domain, model, domain_filter):
    rec = _steward(odoo_env, domain)
    expected = odoo_env[model].search_count(domain_filter)
    measured = rec._measure_domain(domain)

    rec.action_audit_data_quality()

    assert rec.records_audited_count == expected
    assert rec.last_audit_date
    assert rec.audit_state == ("audited" if expected else "no_data")
    if expected:
        assert (rec.completeness_score, rec.uniqueness_score, rec.validity_score) == (
            measured["completeness"],
            measured["uniqueness"],
            measured["validity"],
        )
    payload = json.loads(
        _events(odoo_env, "mdm.quality_audited", rec, aggregate="fix.mdm.stewardship").payload
    )
    assert payload == {
        "domain": domain,
        "audit_state": rec.audit_state,
        "completeness_score": rec.completeness_score,
        "uniqueness_score": rec.uniqueness_score,
        "validity_score": rec.validity_score,
        "overall_quality_score": rec.overall_quality_score,
        "records_audited": expected,
    }


def test_party_scores_are_computed_from_real_partners(odoo_env, monkeypatch):
    from odoo.addons.cd_mdm_core.models import fix_mdm_stewardship as mod

    # measure exactly the partners this test creates
    rules = dict(mod.DOMAIN_RULES["party"], domain=[("name", "=like", "MDM %")])
    monkeypatch.setitem(mod.DOMAIN_RULES, "party", rules)
    odoo_env["res.partner"].create(
        [
            {"name": "MDM Good", "phone": "01711000001", "email": "good@mdm.test"},
            {"name": "MDM Dup", "phone": "+8801711000001"},  # same number: a duplicate
            {"name": "MDM Bad Phone", "phone": "12345"},
            {"name": "MDM No Phone", "email": "not-an-email"},
        ]
    )
    rec = _steward(odoo_env, "party")
    rec.action_audit_data_quality()
    assert rec.records_audited_count == 4
    assert rec.completeness_score == 75.0  # 3 of 4 carry name + phone
    assert rec.validity_score == 50.0  # bad phone and bad email fail
    assert rec.uniqueness_score == 25.0  # only "12345" is a unique key; no-phone is unkeyed
    assert rec.overall_quality_score == round(0.4 * 75 + 0.3 * 25 + 0.3 * 50, 2)


def test_audit_of_an_empty_master_never_reports_a_score(odoo_env):
    rec = _steward(odoo_env, "product")
    rec._guarded().write(
        {"completeness_score": 100.0, "uniqueness_score": 100.0, "validity_score": 100.0}
    )
    odoo_env["fix.catalogue.item"].search([]).unlink()
    rec.action_audit_data_quality()
    assert rec.records_audited_count == 0
    assert rec.audit_state == "no_data"
    assert rec.overall_quality_score == 0.0  # never a fallback 100


def test_audit_of_an_uninstalled_master_is_no_data(odoo_env, monkeypatch):
    from odoo.addons.cd_mdm_core.models import fix_mdm_stewardship as mod

    rules = dict(mod.DOMAIN_RULES["asset"], model="fix.not.installed")
    monkeypatch.setitem(mod.DOMAIN_RULES, "asset", rules)
    rec = _steward(odoo_env, "asset")
    rec.action_audit_data_quality()
    assert (rec.records_audited_count, rec.audit_state) == (0, "no_data")


def test_match_rule_defaults(odoo_env):
    rule = odoo_env["fix.mdm.match.rule"].create({"model_name": "res.partner", "field_name": "vat"})
    assert (rule.match_type, rule.weight, rule.normalize) == ("exact", 1.0, True)
