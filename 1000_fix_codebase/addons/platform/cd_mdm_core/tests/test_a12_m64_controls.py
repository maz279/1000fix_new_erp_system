"""A12 M64 controls (P1-2) on the live ORM (`odoo_env`, rolled back per test).

Working/A12_Workflow_and_Approval_Report.md §6, M64.md:

- master-data changes are proposed on a request, approved by a CODED-GROUP
  steward who is not the proposer, and applied by a separate sudo() step —
  never written straight to the master;
- governed code lists freeze on publish;
- the DQ evaluator MEASURES the masters (completeness / uniqueness / format)
  and skips a rule whose model or field is missing instead of crashing
  (DQ-PARTY-002 targets res.partner.mobile, which does not exist);
- fix.mdm.change.request carries a real sequence (MDM/YYYY/…);
- the FF-48 event consumers exist as fix.event.consumer records.

Every decision is taken by a non-admin user; the superuser only builds
fixtures. Routed approvals run through the M63 inbox helpers, the way
production runs them.
"""

import contextlib
import json
import re
from collections import Counter

import pytest
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
    inbox_task,
)
from odoo.exceptions import AccessError, UserError, ValidationError

STEWARD = "cd_entity_config.group_mdm_domain_steward"
PARTY_STEWARD = "cd_party_master.group_party_data_steward"
CONTACTS = "base.group_partner_manager"
REFUSED = (UserError, ValidationError, AccessError)


@contextlib.contextmanager
def _rejects(env, exc, match):
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
                    "name": "A12 M64 Probe %d" % counter["n"],
                    "login": "a12.m64.probe.%d@test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


@pytest.fixture
def stewards(make_user):
    """Two coded-group stewards: one proposes, a DIFFERENT one decides (SoD)."""
    return {"a": make_user(CONTACTS, STEWARD), "b": make_user(CONTACTS, STEWARD)}


@pytest.fixture
def clerk(make_user):
    return make_user(CONTACTS)


def _partner(odoo_env, name="A12 Golden Party", phone="01700000001"):
    return odoo_env["res.partner"].create({"name": name, "phone": phone})


# --- P1-2: the change-request workflow is routed, not typed ------------------


def test_change_request_reference_uses_the_mdm_sequence(odoo_env, clerk):
    partner = _partner(odoo_env)
    cr = (
        odoo_env["fix.mdm.change.request"]
        .with_user(clerk)
        .create(
            {
                "title": "Fix the phone",
                "model_name": "res.partner",
                "record_id": partner.id,
                "proposed_changes": json.dumps({"phone": "01711111111"}),
            }
        )
    )
    year = odoo_env.cr.now().year
    assert cr.reference.startswith("MDM/%d/" % year), cr.reference


def test_direct_state_writes_are_refused(odoo_env, clerk):
    partner = _partner(odoo_env)
    cr = (
        odoo_env["fix.mdm.change.request"]
        .with_user(clerk)
        .create(
            {
                "title": "Fix the phone",
                "model_name": "res.partner",
                "record_id": partner.id,
                "proposed_changes": json.dumps({"phone": "01711111111"}),
            }
        )
    )
    with _rejects(odoo_env, UserError, match="cannot be set directly"):
        cr.with_user(clerk).write({"state": "approved"})
    with _rejects(odoo_env, UserError, match="cannot be set directly"):
        cr.with_user(clerk).write({"reviewed_by": clerk.id})
    assert cr.state == "draft"


def test_the_proposer_cannot_approve_it_from_the_record(odoo_env, clerk, stewards):
    partner = _partner(odoo_env)
    cr = (
        odoo_env["fix.mdm.change.request"]
        .with_user(clerk)
        .create(
            {
                "title": "Fix the phone",
                "model_name": "res.partner",
                "record_id": partner.id,
                "proposed_changes": json.dumps({"phone": "01711111111"}),
            }
        )
    )
    cr.with_user(clerk).action_submit()
    # A button press by ANYONE (proposer or even a steward) is refused: the
    # decision lives in the M63 inbox.
    with _rejects(odoo_env, UserError, match="inbox"):
        cr.with_user(clerk).action_approve()
    with _rejects(odoo_env, UserError, match="inbox"):
        cr.with_user(stewards["b"]).action_approve()
    assert cr.state == "submitted"


def test_payload_freezes_at_submit(odoo_env, clerk):
    partner = _partner(odoo_env)
    cr = (
        odoo_env["fix.mdm.change.request"]
        .with_user(clerk)
        .create(
            {
                "title": "Fix the phone",
                "model_name": "res.partner",
                "record_id": partner.id,
                "proposed_changes": json.dumps({"phone": "01711111111"}),
            }
        )
    )
    cr.with_user(clerk).action_submit()
    with _rejects(odoo_env, UserError, match="frozen once submitted"):
        cr.with_user(clerk).write({"proposed_changes": json.dumps({"phone": "01999999999"})})
    assert json.loads(cr.proposed_changes) == {"phone": "01711111111"}


def test_full_path_submit_route_decide_apply_lands_the_change(odoo_env, clerk, stewards):
    partner = _partner(odoo_env)
    cr = (
        odoo_env["fix.mdm.change.request"]
        .with_user(clerk)
        .create(
            {
                "title": "Fix the phone",
                "model_name": "res.partner",
                "record_id": partner.id,
                "proposed_changes": json.dumps({"phone": "01711111111"}),
            }
        )
    )
    cr.with_user(clerk).action_submit()
    assert cr.state == "submitted" and cr.current_values

    # The clerk routes it; the routing excludes the proposer and the creator.
    cr.with_user(clerk).action_request_approval(justification="source document says so")
    assert clerk not in assigned(cr)
    assert stewards["b"] in assigned(cr)

    # A steward who is NOT the proposer decides from the inbox.
    approve_via_inbox(cr, stewards["b"], requester=clerk)
    assert cr.state == "approved" and cr.reviewed_by == stewards["b"]

    # The separate apply step lands the change on the master.
    cr.with_user(stewards["b"]).action_apply()
    assert cr.state == "implemented" and cr.applied_by == stewards["b"]
    assert partner.phone == "01711111111"


def test_apply_is_refused_without_the_steward_group(odoo_env, clerk, stewards):
    partner = _partner(odoo_env)
    cr = (
        odoo_env["fix.mdm.change.request"]
        .with_user(clerk)
        .create(
            {
                "title": "Fix the phone",
                "model_name": "res.partner",
                "record_id": partner.id,
                "proposed_changes": json.dumps({"phone": "01711111111"}),
            }
        )
    )
    cr.with_user(clerk).action_submit()
    # BRU-MDM-22: a request is routed with its reason.
    approve_via_inbox(cr, stewards["b"], requester=clerk, justification="source document")
    with _rejects(odoo_env, UserError, match="[Ss]teward"):
        cr.with_user(clerk).action_apply()
    assert cr.state == "approved" and partner.phone == "01700000001"


def test_a_rejected_request_keeps_the_master_untouched(odoo_env, clerk, stewards):
    partner = _partner(odoo_env)
    cr = (
        odoo_env["fix.mdm.change.request"]
        .with_user(clerk)
        .create(
            {
                "title": "Fix the phone",
                "model_name": "res.partner",
                "record_id": partner.id,
                "proposed_changes": json.dumps({"phone": "01711111111"}),
            }
        )
    )
    cr.with_user(clerk).action_submit()
    cr.with_user(clerk).action_request_approval(justification="source document")
    task = inbox_task(cr, stewards["b"])
    task.with_user(stewards["b"]).action_reject("not the same customer")
    assert cr.state == "rejected"
    assert partner.phone == "01700000001"


# --- P1-2: steward requests decide from the inbox too ------------------------


def _steward_request(odoo_env, user, partner, **vals):
    return (
        odoo_env["fix.mdm.steward"]
        .with_user(user)
        .create(
            {
                "request_type": "update",
                "res_model": "res.partner",
                "record_ref": str(partner.id),
                "reason": "customer called in a correction",
                "proposed_changes": json.dumps({"phone": "01722222222"}),
                **vals,
            }
        )
    )


def test_steward_request_is_reviewed_decided_and_applied(odoo_env, stewards):
    partner = _partner(odoo_env, "A12 Steward Target")
    req = _steward_request(odoo_env, stewards["a"], partner)
    assert req.state == "submitted"

    # E14: another steward starts the review, never the requester.
    req.with_user(stewards["b"]).action_review()
    assert req.state == "in_review"

    # The proposer never decides it: routing excludes them.
    req.with_user(stewards["a"]).action_request_approval(justification="correction")
    assert stewards["a"] not in assigned(req)
    assert stewards["b"] in assigned(req)
    with _rejects(odoo_env, UserError, match="inbox"):
        req.with_user(stewards["b"]).action_approve()

    approve_via_inbox(req, stewards["b"], requester=stewards["a"])
    assert req.state == "approved" and req.decided_at

    req.with_user(stewards["b"]).action_apply()
    assert req.state == "applied" and req.applied_by == stewards["b"]
    assert partner.phone == "01722222222"


def test_steward_request_proposer_cannot_decide_even_via_the_group(odoo_env, stewards):
    partner = _partner(odoo_env, "A12 SoD Target")
    req = _steward_request(odoo_env, stewards["a"], partner)
    req.with_user(stewards["b"]).action_review()
    req.with_user(stewards["a"]).action_request_approval()
    # Test surgery: hand the proposer the deciding task anyway; the SoD check
    # inside the apply still refuses (the check binds inside the inbox).
    task = req.approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == stewards["b"]
    )
    env = odoo_env
    env.cr.execute(
        "UPDATE fix_workflow_task SET assigned_user_id = %s WHERE id = %s",
        (stewards["a"].id, task.id),
    )
    task.invalidate_recordset()
    with _rejects(odoo_env, UserError, match="Segregation"):
        task.with_user(stewards["a"]).action_approve()
    assert req.state == "in_review"


def test_steward_request_state_is_never_typed(odoo_env, stewards):
    partner = _partner(odoo_env, "A12 Guard Target")
    req = _steward_request(odoo_env, stewards["a"], partner)
    with _rejects(odoo_env, UserError, match="cannot be set directly"):
        req.with_user(stewards["a"]).write({"state": "approved"})
    assert req.state == "submitted"


# --- P1-2: governed code lists freeze on publish ------------------------------


def _code_list(odoo_env, user, entries=(("DV", "Dhaka"), ("CTG", "Chattogram"))):
    lst = (
        odoo_env["fix.mdm.code.list"]
        .with_user(user)
        .create(
            {
                "code": "BD-DIV-%d" % odoo_env["fix.mdm.code.list"].search_count([]),
                "name": "BD divisions",
            }
        )
    )
    for value, label in entries:
        odoo_env["fix.mdm.code.entry"].with_user(user).create(
            {"list_id": lst.id, "value": value, "label": label}
        )
    return lst


def test_publishing_freezes_the_list(odoo_env, stewards):
    lst = _code_list(odoo_env, stewards["a"])
    # E25: a second person publishes.
    lst.with_user(stewards["b"]).action_publish()
    assert lst.state == "published" and lst.published_on

    entry = lst.entry_ids[0]
    with _rejects(odoo_env, REFUSED, match=""):
        entry.with_user(stewards["a"]).write({"label": "Dhaka Metro"})
    with _rejects(odoo_env, REFUSED, match=""):
        odoo_env["fix.mdm.code.entry"].with_user(stewards["a"]).create(
            {"list_id": lst.id, "value": "SYL", "label": "Sylhet"}
        )
    with _rejects(odoo_env, REFUSED, match=""):
        entry.with_user(stewards["a"]).unlink()
    assert entry.label == "Dhaka" and len(lst.entry_ids) == 2


def test_changes_ship_as_a_new_version(odoo_env, stewards):
    lst = _code_list(odoo_env, stewards["a"])
    lst.with_user(stewards["b"]).action_publish()
    new = lst.with_user(stewards["a"]).action_new_version()
    assert new.state == "draft" and new != lst
    assert {e.value for e in new.entry_ids} == {"DV", "CTG"}


def test_publishing_an_empty_list_is_refused(odoo_env, stewards):
    lst = (
        odoo_env["fix.mdm.code.list"]
        .with_user(stewards["a"])
        .create({"code": "BD-EMPTY", "name": "Empty list"})
    )
    with _rejects(odoo_env, REFUSED, match=""):
        lst.with_user(stewards["a"]).action_publish()
    assert lst.state == "draft"


# --- P1-2: the DQ evaluator measures, skips missing targets -------------------


def _dq_rule(odoo_env, user, **vals):
    base = {
        "code": "A12-DQ-%d" % odoo_env["fix.mdm.dq.rule"].search_count([]),
        "name": "A12 probe rule",
        "res_model": "res.partner",
        "field_name": "phone",
        "rule_type": "completeness",
        # expression is a required column; completeness/uniqueness rules
        # carry the human-readable condition the evaluator documents.
        "expression": "not null",
        "severity": "major",
    }
    base.update(vals)
    return odoo_env["fix.mdm.dq.rule"].with_user(user).create(base)


def test_evaluator_measures_completeness_on_the_real_master(odoo_env, stewards):
    rule = _dq_rule(odoo_env, stewards["a"], rule_type="completeness")
    rule.with_user(stewards["a"]).action_evaluate()
    partner = odoo_env["res.partner"]
    expected_missing = partner.search_count([("phone", "=", False)])
    assert rule.last_status == "ok"
    assert rule.last_records_checked == partner.search_count([])
    assert rule.last_violation_count == expected_missing
    assert rule.last_run_at


def test_evaluator_measures_format_and_uniqueness(odoo_env, stewards):
    # format: every non-empty phone must fullmatch the BD pattern
    rule = _dq_rule(odoo_env, stewards["a"], rule_type="format", expression=r"\+?01\d{9}")
    rule.with_user(stewards["a"]).action_evaluate()
    phones = [p.phone for p in odoo_env["res.partner"].search([]) if p.phone]
    expected = sum(1 for v in phones if not re.fullmatch(r"\+?01\d{9}", v or ""))
    assert rule.last_status == "ok" and rule.last_violation_count == expected

    # uniqueness: duplicate values across the governed code entries
    entries = odoo_env["fix.mdm.code.entry"].search([])
    vals = [e.value for e in entries if e.value]
    expected_dupes = sum(c - 1 for c in Counter(vals).values() if c > 1)
    rule2 = _dq_rule(
        odoo_env,
        stewards["a"],
        res_model="fix.mdm.code.entry",
        field_name="value",
        rule_type="uniqueness",
    )
    rule2.with_user(stewards["a"]).action_evaluate()
    assert rule2.last_status == "ok" and rule2.last_violation_count == expected_dupes


def _legacy_rule_on_missing_field(odoo_env):
    """DQ-PARTY-002 lives only in the database (pre-constraint data): a rule
    whose field does not exist on the model. Inserted with SQL exactly the
    way such a row survives an upgrade (expression/company_id are NOT NULL)."""
    odoo_env.cr.execute(
        """
        INSERT INTO fix_mdm_dq_rule (
            code, name, res_model, field_name, rule_type, expression, severity,
            active, company_id, create_uid, write_uid, create_date, write_date
        ) VALUES (
            'DQ-PARTY-002-PROBE', 'legacy mobile probe', 'res.partner', 'mobile',
            'completeness', 'not null', 'critical',
            TRUE, 1, 1, 1, now() AT TIME ZONE 'UTC', now() AT TIME ZONE 'UTC'
        ) RETURNING id
        """
    )
    return odoo_env["fix.mdm.dq.rule"].browse(odoo_env.cr.fetchone()[0])


def test_a_rule_on_a_missing_field_is_skipped_with_a_note_not_crashed(odoo_env, stewards):
    rule = _legacy_rule_on_missing_field(odoo_env)
    rule.with_user(stewards["a"]).action_evaluate()
    assert rule.last_status == "skipped"
    assert rule.last_violation_count == 0
    assert "mobile" in (rule.last_note or "")


def test_the_daily_cron_survives_every_rule(odoo_env, stewards):
    _legacy_rule_on_missing_field(odoo_env)
    # never raises, whatever the rule book contains
    odoo_env["fix.mdm.dq.rule"].sudo().cron_evaluate_dq_rules()
    ok = odoo_env["fix.mdm.dq.rule"].search([("last_status", "=", "ok")])
    skipped = odoo_env["fix.mdm.dq.rule"].search([("last_status", "=", "skipped")])
    assert ok or skipped  # it ran and recorded outcomes, not assertions


# --- P1-2: a duplicate merge routes M33 and lands only when M33 lands ---------


@pytest.fixture
def dup_pair(odoo_env, make_user):
    if "fix.party.merge" not in odoo_env:
        pytest.skip("cd_party_master is not installed on this database")
    a = odoo_env["res.partner"].create({"name": "A12 Dup A", "phone": "01733333333"})
    b = odoo_env["res.partner"].create({"name": "A12 Dup B", "phone": "01733333333"})
    dup = odoo_env["fix.mdm.duplicate"].create(
        {
            "res_model": "res.partner",
            "record_a_ref": str(a.id),
            "record_b_ref": str(b.id),
            "score": 95.0,
            "match_factors": "phone,name",
        }
    )
    # Routing a merge needs a decider to EXIST: the engine refuses to open a
    # request nobody can decide (nobody-but-you holds the party group). The
    # party steward also holds partner-write: M33's executor moves the victim
    # party in the approver's env, by design.
    party_steward = make_user(CONTACTS, PARTY_STEWARD)
    return dup, a, b, party_steward


def test_merge_delegates_to_m33_and_stays_pending_until_it_executes(odoo_env, stewards, dup_pair):
    dup, a, b, party_steward = dup_pair
    dup.with_user(stewards["a"]).action_merge(justification="same hotline caller")
    assert dup.party_merge_id, "no fix.party.merge was routed"
    merge = odoo_env["fix.party.merge"].browse(dup.party_merge_id)
    assert merge.state == "draft"
    assert dup.decision == "pending", "the badge must not claim a merge that has not run"
    assert dup.survivor_ref

    approve_via_inbox(merge, party_steward, requester=stewards["a"])
    assert merge.state == "executed"

    dup.with_user(stewards["a"]).action_sync_merge_state()
    assert dup.decision == "merged"


def test_a_low_score_merge_needs_a_note(odoo_env, stewards, dup_pair):
    dup, _a, _b, _party_steward = dup_pair
    # E18: the score is the detection run's: only system code sets it.
    dup.sudo().write({"score": 55.0})
    with _rejects(odoo_env, REFUSED, match=""):
        dup.with_user(stewards["a"]).action_merge()
    dup.with_user(stewards["a"]).action_merge(justification="confirmed by both stores")
    assert dup.party_merge_id


def test_merge_is_steward_gated(odoo_env, clerk, dup_pair):
    dup, _a, _b, _party_steward = dup_pair
    with _rejects(odoo_env, REFUSED, match=""):
        dup.with_user(clerk).action_merge(justification="trying it anyway")
    assert not dup.party_merge_id


def test_duplicate_decision_and_stamps_are_never_typed(odoo_env, stewards, dup_pair):
    dup, _a, _b, _party_steward = dup_pair
    with _rejects(odoo_env, UserError, match="cannot be set directly"):
        dup.with_user(stewards["a"]).write({"decision": "merged"})
    assert dup.decision == "pending"


# --- FF-48: the event consumers exist -----------------------------------------


@pytest.mark.parametrize(
    "xmlid",
    [
        "cd_mdm_core.consumer_mdm_change_requested",
        "cd_mdm_core.consumer_mdm_change_approved",
        "cd_mdm_core.consumer_mdm_change_rejected",
        "cd_mdm_core.consumer_mdm_quality_audited",
    ],
)
def test_ff48_consumer_records_exist(odoo_env, xmlid):
    consumer = odoo_env.ref(xmlid)
    assert consumer.active
    assert consumer.method.startswith("consume_")
    assert consumer.model in odoo_env, "%s points at a missing model" % xmlid
    assert hasattr(odoo_env[consumer.model], consumer.method)


def test_the_mdm_sequence_ships_with_the_module(odoo_env):
    seq = odoo_env.ref("cd_mdm_core.seq_fix_mdm_change_request", raise_if_not_found=False)
    assert seq and seq.code == "fix.mdm.change.request"
