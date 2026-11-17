"""M64 capture audit (2026-11-18): the records the workspace pages could not
capture, exercised on the live ORM (`odoo_env`, rolled back per test).

Every decision is taken by a non-admin user; the superuser only builds
fixtures. Routed approvals run through the M63 inbox, as production does.
"""

import contextlib
import datetime
import json

import pytest
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
    inbox_task,
)
from odoo.exceptions import AccessError, UserError, ValidationError

STEWARD = "cd_entity_config.group_mdm_domain_steward"
ADMIN = "cd_entity_config.group_platform_admin"
CONTACTS = "base.group_partner_manager"
REFUSED = (UserError, ValidationError, AccessError)
# a dotted business-parameter key (not a credential)
PARAM_KEY = ".".join(("pricing", "m64cap_discount_ceiling"))


@contextlib.contextmanager
def _rejects(env, match, exc=REFUSED):
    with pytest.raises(exc, match=match), env.cr.savepoint():
        yield


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
                    "name": "M64 Capture Probe %d" % counter["n"],
                    "login": "m64.capture.probe.%d@test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


@pytest.fixture
def stewards(make_user):
    return {k: make_user(CONTACTS, STEWARD) for k in ("a", "b", "c")}


@pytest.fixture
def clerk(make_user):
    return make_user(CONTACTS)


# --- FR-MDM-021: the remediation worklist ------------------------------------


@pytest.fixture
def blank_domain_rule(odoo_env, stewards):
    """A completeness rule that a code list with no domain fails."""
    rule = odoo_env["fix.mdm.dq.rule"].create(
        {
            "code": "DQ-M64-CAP-01",
            "name": "Code list has a domain",
            "res_model": "fix.mdm.code.list",
            "field_name": "domain_area",
            "rule_type": "completeness",
            "expression": "not null",
            "severity": "critical",
        }
    )
    bare = odoo_env["fix.mdm.code.list"].create({"code": "M64CAP-BARE", "name": "No domain"})
    good = odoo_env["fix.mdm.code.list"].create(
        {"code": "M64CAP-GOOD", "name": "Has a domain", "domain_area": "unit"}
    )
    return rule, bare, good


def test_the_worklist_raises_one_item_per_failing_record(odoo_env, stewards, blank_domain_rule):
    rule, bare, good = blank_domain_rule
    raised = rule.with_user(stewards["b"]).action_raise_worklist()
    items = odoo_env["fix.mdm.dq.remediation"].search([("rule_id", "=", rule.id)])
    assert raised == len(items) >= 1
    assert bare.id in items.mapped("res_id") and good.id not in items.mapped("res_id")
    item = items.filtered(lambda r: r.res_id == bare.id)
    assert item.priority == "urgent" and item.raised_by_id == stewards["b"]
    assert item.record_name == bare.display_name
    # raised again: no second open item for the same record
    assert rule.with_user(stewards["b"]).action_raise_worklist() == 0


def test_a_clerk_cannot_raise_the_worklist(odoo_env, clerk, blank_domain_rule):
    rule, _bare, _good = blank_domain_rule
    with _rejects(odoo_env, "Steward"):
        rule.with_user(clerk).action_raise_worklist()


def test_resolve_needs_the_record_to_pass(odoo_env, stewards, blank_domain_rule):
    rule, bare, _good = blank_domain_rule
    item = (
        odoo_env["fix.mdm.dq.remediation"]
        .with_user(stewards["b"])
        .create({"rule_id": rule.id, "res_id": bare.id, "assigned_to_id": stewards["c"].id})
    )
    item.with_user(stewards["c"]).action_start()
    assert item.state == "in_progress"
    with _rejects(odoo_env, "still fails"):
        item.with_user(stewards["c"]).action_resolve("done")
    bare.write({"domain_area": "currency"})
    item.with_user(stewards["c"]).action_resolve("domain added")
    assert item.state == "resolved" and item.resolved_by_id == stewards["c"]
    assert item.resolution == "domain added"


def test_a_waiver_needs_a_reason_and_a_steward_who_wrote_neither(
    odoo_env, stewards, blank_domain_rule
):
    rule, bare, _good = blank_domain_rule
    # the fixture rule was built by the superuser: steward a plays its author
    odoo_env.cr.execute(
        "UPDATE fix_mdm_dq_rule SET create_uid = %s WHERE id = %s", (stewards["a"].id, rule.id)
    )
    rule.invalidate_recordset(["create_uid"])
    item = (
        odoo_env["fix.mdm.dq.remediation"]
        .with_user(stewards["b"])
        .create({"rule_id": rule.id, "res_id": bare.id})
    )
    with _rejects(odoo_env, "exempt"):
        item.with_user(stewards["c"]).action_waive("")
    with _rejects(odoo_env, "Segregation"):
        item.with_user(stewards["a"]).action_waive("legacy list")
    with _rejects(odoo_env, "Segregation"):
        item.with_user(stewards["b"]).action_waive("legacy list")
    item.with_user(stewards["c"]).action_waive("legacy list, retired next month")
    assert item.state == "waived" and item.resolved_by_id == stewards["c"]


def test_the_state_and_resolution_are_never_typed(odoo_env, stewards, blank_domain_rule):
    rule, bare, _good = blank_domain_rule
    item = (
        odoo_env["fix.mdm.dq.remediation"]
        .with_user(stewards["b"])
        .create({"rule_id": rule.id, "res_id": bare.id})
    )
    with _rejects(odoo_env, "cannot be set directly"):
        item.with_user(stewards["b"]).write({"state": "resolved"})
    with _rejects(odoo_env, "cannot be set directly"):
        item.with_user(stewards["b"]).write({"resolution": "fixed"})


def test_remediation_goes_to_a_steward_and_a_live_record(
    odoo_env, stewards, clerk, blank_domain_rule
):
    rule, bare, _good = blank_domain_rule
    Remediation = odoo_env["fix.mdm.dq.remediation"].with_user(stewards["b"])
    with _rejects(odoo_env, "Steward"):
        Remediation.create({"rule_id": rule.id, "res_id": bare.id, "assigned_to_id": clerk.id})
    with _rejects(odoo_env, "nothing to remediate"):
        Remediation.create({"rule_id": rule.id, "res_id": 999999999})
    Remediation.create({"rule_id": rule.id, "res_id": bare.id})
    with _rejects(odoo_env, "already has an open"):
        Remediation.create({"rule_id": rule.id, "res_id": bare.id})
    with _rejects(odoo_env, "", exc=AccessError):
        odoo_env["fix.mdm.dq.remediation"].with_user(clerk).create(
            {"rule_id": rule.id, "res_id": bare.id}
        )


# --- FR-MDM-033: business parameters ------------------------------------------


@pytest.fixture
def owner(make_user):
    return make_user()


def _parameter(odoo_env, steward, owner, **vals):
    return (
        odoo_env["fix.mdm.business.parameter"]
        .with_user(steward)
        .create(
            {
                "key": PARAM_KEY,
                "name": "Counter discount ceiling",
                "domain": "pricing",
                "value_type": "percent",
                "owner_id": owner.id,
                "initial_value": "10",
                **vals,
            }
        )
    )


def test_a_parameter_value_is_checked_against_its_type(odoo_env, stewards, owner):
    with _rejects(odoo_env, "outside 0-100"):
        _parameter(odoo_env, stewards["a"], owner, initial_value="150")
    with _rejects(odoo_env, "takes a number"):
        _parameter(odoo_env, stewards["a"], owner, initial_value="ten")
    with _rejects(odoo_env, "lower-case and dotted"):
        _parameter(odoo_env, stewards["a"], owner, key="Discount Ceiling")
    with _rejects(odoo_env, "must lie between"):
        _parameter(odoo_env, stewards["a"], owner, initial_value="30", max_value=25)


def test_the_drafter_cannot_activate_and_the_value_then_freezes(odoo_env, stewards, owner):
    param = _parameter(odoo_env, stewards["a"], owner)
    with _rejects(odoo_env, "Segregation"):
        param.with_user(stewards["a"]).action_activate()
    param.with_user(owner).action_activate()
    assert param.state == "active" and param.current_value == "10"
    with _rejects(odoo_env, "Parameter Change"):
        param.with_user(stewards["a"]).write({"initial_value": "12"})
    with _rejects(odoo_env, "cannot be set directly"):
        param.with_user(stewards["a"]).write({"state": "draft"})


def test_a_change_goes_to_the_owner_and_keeps_history(odoo_env, stewards, owner, clerk):
    param = _parameter(odoo_env, stewards["a"], owner)
    param.with_user(owner).action_activate()
    today = param.activated_on  # Dhaka date: UTC is a day behind after 18:00
    later = today + datetime.timedelta(days=30)
    change = (
        odoo_env["fix.mdm.parameter.change"]
        .with_user(clerk)
        .create(
            {
                "parameter_id": param.id,
                "proposed_value": "12.50",
                "effective_from": later,
                "reason": "Eid campaign approved by the CCO",
            }
        )
    )
    change.with_user(clerk).action_submit()
    assert change.state == "submitted" and change.previous_value == "10"
    with _rejects(odoo_env, "submitted"):
        change.with_user(clerk).write({"proposed_value": "40"})
    change.with_user(clerk).action_request_approval()
    assert assigned(change) == owner
    approve_via_inbox(change, owner, requester=clerk)
    assert change.state == "published" and change.decided_by_id == owner
    Param = odoo_env["fix.mdm.business.parameter"]
    assert Param.value_at(param.key, today) == "10"
    assert Param.value_at(param.key, later) == "12.5"
    assert param.version == 2


def test_the_owner_never_decides_their_own_change(odoo_env, stewards, owner):
    param = _parameter(odoo_env, stewards["a"], owner)
    param.with_user(owner).action_activate()
    change = (
        odoo_env["fix.mdm.parameter.change"]
        .with_user(owner)
        .create({"parameter_id": param.id, "proposed_value": "15", "reason": "margin review"})
    )
    change.with_user(owner).action_submit()
    change.with_user(owner).action_request_approval()
    routed = assigned(change)
    assert routed and owner not in routed
    assert all(u.has_group(STEWARD) for u in routed)
    assert not inbox_task(change, owner)


def test_a_change_never_takes_effect_in_the_past_or_repeats(odoo_env, stewards, owner, clerk):
    param = _parameter(odoo_env, stewards["a"], owner)
    param.with_user(owner).action_activate()
    Change = odoo_env["fix.mdm.parameter.change"].with_user(clerk)
    past = Change.create(
        {
            "parameter_id": param.id,
            "proposed_value": "11",
            "effective_from": datetime.date.today() - datetime.timedelta(days=1),
            "reason": "backdated",
        }
    )
    with _rejects(odoo_env, "in the past"):
        past.action_submit()
    same = Change.create({"parameter_id": param.id, "proposed_value": "10", "reason": "noop"})
    with _rejects(odoo_env, "already"):
        same.action_submit()
    with _rejects(odoo_env, "outside 0-100"):
        Change.create({"parameter_id": param.id, "proposed_value": "101", "reason": "typo"})


# --- FR-MDM-028/029: governed hierarchies -------------------------------------


def _nodes(*rows):
    return [(0, 0, {"code": c, "label": c, "parent_code": p or False}) for c, p in rows]


def _hierarchy(odoo_env, user, nodes, **vals):
    return (
        odoo_env["fix.mdm.hierarchy"]
        .with_user(user)
        .create(
            {
                "code": "M64CAP-SPEND",
                "name": "Spend categories",
                "hierarchy_type": "spend",
                "max_depth": 3,
                "node_ids": nodes,
                **vals,
            }
        )
    )


def test_a_hierarchy_refuses_orphans_cycles_and_depth(odoo_env, stewards):
    with _rejects(odoo_env, "orphan"):
        _hierarchy(odoo_env, stewards["a"], _nodes(("PARTS", None), ("SCREENS", "NOPE")))
    with _rejects(odoo_env, "cycle"):
        _hierarchy(odoo_env, stewards["a"], _nodes(("A", "B"), ("B", "A")))
    with _rejects(odoo_env, "deepest level"):
        _hierarchy(
            odoo_env,
            stewards["a"],
            _nodes(("L1", None), ("L2", "L1"), ("L3", "L2"), ("L4", "L3")),
        )
    with _rejects(odoo_env, "used twice"):
        _hierarchy(odoo_env, stewards["a"], _nodes(("X", None), ("X", None)))
    tree = _hierarchy(odoo_env, stewards["a"], _nodes(("L1", None), ("L2", "L1"), ("L3", "L2")))
    levels = {n.code: n.level for n in tree.node_ids}
    assert levels == {"L1": 1, "L2": 2, "L3": 3}
    assert tree.node_ids.filtered(lambda n: n.code == "L3").parent_id.code == "L2"


def test_a_second_steward_publishes_and_the_tree_freezes(odoo_env, stewards):
    tree = _hierarchy(odoo_env, stewards["a"], _nodes(("PARTS", None), ("SCREENS", "PARTS")))
    with _rejects(odoo_env, "Segregation"):
        tree.with_user(stewards["a"]).action_publish()
    tree.with_user(stewards["b"]).action_publish()
    assert tree.state == "published" and tree.published_by_id == stewards["b"]
    with _rejects(odoo_env, "frozen|new version"):
        tree.node_ids[0].with_user(stewards["a"]).write({"label": "Spares"})
    with _rejects(odoo_env, "new version"):
        tree.with_user(stewards["a"]).write({"max_depth": 5})
    tree.with_user(stewards["a"]).action_new_version()
    draft = odoo_env["fix.mdm.hierarchy"].search(
        [("code", "=", "M64CAP-SPEND"), ("state", "=", "draft")]
    )
    assert draft.version == 2 and len(draft.node_ids) == 2
    draft.with_user(stewards["c"]).action_publish()
    assert tree.state == "retired" and tree.superseded_by_id == draft


# --- FR-MDM-013: bulk change sets ---------------------------------------------


def _partners(odoo_env):
    Partner = odoo_env["res.partner"]
    return (
        Partner.create({"name": "M64 Bulk A", "phone": "01700000011"}),
        Partner.create({"name": "M64 Bulk B", "phone": "01700000012"}),
    )


def _batch(odoo_env, user, rows):
    return (
        odoo_env["fix.mdm.change.batch"]
        .with_user(user)
        .create(
            {
                "title": "Re-key the counter phones",
                "justification": "Branch moved to the new PBX range",
                "model_name": "res.partner",
                "line_ids": [
                    (0, 0, {"record_id": rid, "proposed_changes": payload}) for rid, payload in rows
                ],
            }
        )
    )


def test_a_bulk_set_is_checked_routed_and_applied_whole(odoo_env, clerk, stewards):
    a, b = _partners(odoo_env)
    batch = _batch(
        odoo_env,
        clerk,
        [(a.id, "phone=01711000011"), (b.id, json.dumps({"phone": "01711000012"}))],
    )
    assert batch.name.startswith("BULK/")
    batch.with_user(clerk).action_submit()
    assert batch.state == "submitted" and "2 record(s)" in batch.preview
    assert all(line.current_values for line in batch.line_ids)
    with _rejects(odoo_env, "set reviewed is the set applied|submitted set"):
        batch.line_ids[0].with_user(clerk).write({"proposed_changes": "phone=01799999999"})
    approve_via_inbox(batch, stewards["b"], requester=clerk)
    assert batch.state == "approved" and clerk not in assigned(batch)
    batch.with_user(stewards["b"]).action_apply()
    assert batch.state == "applied"
    assert (a.phone, b.phone) == ("01711000011", "01711000012")


def test_a_bulk_set_applies_all_or_nothing(odoo_env, clerk, stewards):
    a, b = _partners(odoo_env)
    batch = _batch(odoo_env, clerk, [(a.id, "phone=01722000011"), (b.id, "phone=01722000012")])
    batch.with_user(clerk).action_submit()
    approve_via_inbox(batch, stewards["b"], requester=clerk)
    b.write({"phone": "01733333333"})  # B moved after the set was reviewed
    with _rejects(odoo_env, "changed after"):
        batch.with_user(stewards["b"]).action_apply()
    assert a.phone == "01700000011", "the first record was written although the set failed"
    assert batch.state == "approved"


def test_a_bulk_set_refuses_ungoverned_fields_and_repeated_records(odoo_env, clerk):
    a, _b = _partners(odoo_env)
    off = _batch(odoo_env, clerk, [(a.id, "comment=hello")])
    with _rejects(odoo_env, "not on the governed-attribute register"):
        off.with_user(clerk).action_submit()
    twice = _batch(odoo_env, clerk, [(a.id, "phone=01744000001"), (a.id, "phone=01744000002")])
    with _rejects(odoo_env, "twice"):
        twice.with_user(clerk).action_submit()


def test_the_proposer_never_decides_their_own_set(odoo_env, stewards):
    a, b = _partners(odoo_env)
    batch = _batch(
        odoo_env, stewards["a"], [(a.id, "phone=01755000011"), (b.id, "phone=01755000012")]
    )
    batch.with_user(stewards["a"]).action_submit()
    batch.with_user(stewards["a"]).action_request_approval()
    assert stewards["a"] not in assigned(batch)
    with _rejects(odoo_env, "approver's inbox"):
        batch.with_user(stewards["a"]).action_approve()


def test_the_steward_who_submitted_a_set_never_decides_it(odoo_env, clerk, stewards):
    """The engine refuses the requester and creator; the set itself also
    refuses whoever SUBMITTED it, who is neither here (defence in depth)."""
    a, b = _partners(odoo_env)
    batch = _batch(odoo_env, clerk, [(a.id, "phone=01766000011"), (b.id, "phone=01766000012")])
    batch.with_user(stewards["a"]).action_submit()
    batch.with_user(clerk).action_request_approval()
    assert stewards["a"] not in assigned(batch)
    # Test surgery: hand the submitter the deciding task anyway.
    task = batch.approval_request_id.task_ids[:1]
    odoo_env.cr.execute(
        "UPDATE fix_workflow_task SET assigned_user_id = %s WHERE id = %s",
        (stewards["a"].id, task.id),
    )
    task.invalidate_recordset()
    with _rejects(odoo_env, "you raised"):
        task.with_user(stewards["a"]).action_approve()
    assert batch.state == "submitted"


# --- FR-MDM-001/004: the domain register's deputy -----------------------------


def test_a_deputy_is_another_steward(odoo_env, make_user, stewards, clerk):
    admin = make_user(ADMIN)
    Domain = odoo_env["fix.mdm.stewardship"].with_user(admin)
    vals = {
        "name": "M64 capture party domain",
        "domain": "party",
        "lead_steward_id": stewards["a"].id,
        "criticality": "critical",
        "company_id": odoo_env.company.id,
    }
    odoo_env["fix.mdm.stewardship"].sudo().search(
        [("domain", "=", "party"), ("company_id", "=", odoo_env.company.id)]
    ).unlink()
    with _rejects(odoo_env, "deputise"):
        Domain.create({**vals, "deputy_steward_id": clerk.id})
    with _rejects(odoo_env, "themself"):
        Domain.create({**vals, "deputy_steward_id": stewards["a"].id})
    domain = Domain.create({**vals, "deputy_steward_id": stewards["b"].id})
    assert domain.deputy_steward_id == stewards["b"]
    with _rejects(odoo_env, "Platform Admin"):
        domain.with_user(stewards["a"]).write({"deputy_steward_id": stewards["c"].id})
