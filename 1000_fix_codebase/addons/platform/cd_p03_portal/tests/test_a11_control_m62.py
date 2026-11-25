# A11 control suite, module M62 Data Platform & Governance (cd_metric_registry).
#
# The 2026-11-03 audit probes (55 of them: 103 GAP findings across A11), kept
# as regression controls for the G1-G6/E5 remediation. Convention: a pytest
# PASS means the CONTROL HELD. Reference setup runs as the Data Governance
# Officer (the group the remediation created — cd_metric_registry.
# group_data_governance_officer); attacks run as plain internal users
# (base.group_user + an operating unit). Refusals are (UserError,
# ValidationError, AccessError). Everything rolls back with odoo_env.
#
# What the remediation established, pinned here:
#   - the governance rule book (entities, lineage, rules, contracts, metrics,
#     retention, evidence) is the officer's: plain users read only
#   - contracts activate through the M63 engine (producer sign + a decided
#     task), never a click; the active row is frozen; versions supersede
#   - metrics publish through steward-reviewed VERSIONS routed by M63
#   - one comparator owned by the rule; tests are immutable evidence stamped
#     with the rule's own threshold; measured results are labelled
#   - incidents: born open, owner + root cause + resolution to close, closed
#     is final, four eyes on high/critical
#   - retention: positive, one per entity, statutory floor, shortening via
#     M63, legal hold blocks everything, evidence is append-only
#   - pipelines/runs: runs start running, row math reconciles, retirement is
#     final, the success stamps are guarded engine fields
#   - P03 /p03/model/write carries a writable whitelist per surface, exactly
#     the fields the workspace forms offer
import datetime
import inspect
import types

import psycopg2
import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
OFFICER = "cd_metric_registry.group_data_governance_officer"


class Ctx:
    pass


def _user(env, login, extra_groups=(), company=None):
    Users = env["res.users"].with_context(no_reset_password=True)
    groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in extra_groups]
    ou = env["operating.unit"].search([], limit=1)
    vals = {
        "name": login,
        "login": login,
        "group_ids": [(6, 0, groups)],
        "assigned_operating_unit_ids": [(6, 0, ou.ids)],
        "default_operating_unit_id": ou.id,
    }
    if company:
        vals.update({"company_id": company.id, "company_ids": [(6, 0, company.ids)]})
    return Users.create(vals)


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    if "fix.data.entity" not in env:
        pytest.skip("cd_metric_registry is not installed")
    x = Ctx()
    x.env = env
    x.plain = _user(env, "a11m62_plain")
    x.plain2 = _user(env, "a11m62_plain2")
    x.gov = _user(env, "a11m62_gov", extra_groups=(OFFICER,))  # rule book author
    x.gov_b = _user(env, "a11m62_gov_b", extra_groups=(OFFICER,))  # the deciding officer
    E = env["fix.data.entity"]
    x.ent = E.create(
        {
            "name": "A11M62 fix_service_order",
            "entity_type": "table",
            "owner_module": "M01",
            "classification": "internal",
        }
    )
    x.ent_s3 = E.create(
        {
            "name": "A11M62 Identity Documents",
            "entity_type": "document",
            "owner_module": "M33",
            "classification": "residency_classified",
            "retention_policy": "7 years (statutory)",
        }
    )
    x.rule = env["fix.data.quality.rule"].create(
        {
            "name": "A11M62 orders completeness",
            "entity_id": x.ent.id,
            "rule_type": "completeness",
            "threshold": 95.0,
        }
    )
    x.pipe = env["fix.data.pipeline"].create(
        {
            "code": "A11M62-PL",
            "name": "A11M62 pipe",
            "source_system": "odoo_fix.service_order",
            "target_entity_id": x.ent.id,
            "freshness_sla_minutes": 15,
        }
    )
    return x


def U(c, rec, user=None):
    return rec.with_user(user or c.plain)


def contract(c, user=None, **kw):
    vals = {
        "dataset_code": "A11M62-DS-%s" % kw.pop("suffix", "1"),
        "name": "A11M62 dataset",
        "entity_id": c.ent.id,
        "producer": "Service Platform (M01)",
        "schema_version": "1.0",
        "guarantees": "order_id not null; freshness 15 min",
    }
    vals.update(kw)
    return c.env["fix.data.contract"].with_user(user or c.gov).create(vals)


def activate(c, k):
    """The governed activation path (G1/BRU-DAT-10): the producer signs, the
    platform side is requested through M63, and a SECOND officer decides the
    inbox task — the decided task is what authorises action_activate."""
    k.with_user(c.gov).action_producer_sign()
    k.with_user(c.gov).action_request_approval()
    task = k.approval_request_id.task_ids.filtered(
        lambda t: t.assigned_user_id == c.gov_b and t.state == "pending"
    )
    assert task, "no pending M63 task for the deciding officer"
    task.with_user(c.gov_b).action_approve(comment="platform side granted")
    k.invalidate_recordset()
    assert k.state == "active"
    return k


def metric(c, user=None, **kw):
    vals = {
        "code": "A11M62-MET-%s" % kw.pop("suffix", "1"),
        "name": "A11M62 SLA attainment %",
        "definition": "breach-free completed orders / all completed orders",
        "source_entity_id": c.ent.id,
        "owner_role": "R-05",
    }
    vals.update(kw)
    return c.env["fix.metric.definition"].with_user(user or c.gov).create(vals)


def publish(c, m, decider=None):
    """The governed publication path (G2/BRU-DAT-02/03): a version is drafted,
    steward-reviewed, then routed through M63 to a second officer."""
    v = (
        c.env["fix.metric.version"]
        .with_user(c.gov)
        .create(
            {
                "definition_id": m.id,
                "definition_text": m.definition,
                "grain": m.grain,
                "source_entity_id": m.source_entity_id.id,
            }
        )
    )
    v.with_user(c.gov).action_steward_review()
    v.with_user(c.gov).action_request_approval()
    task = v.approval_request_id.task_ids.filtered(
        lambda t: t.assigned_user_id == (decider or c.gov_b) and t.state == "pending"
    )
    assert task, "no pending M63 task for the deciding officer"
    task.with_user(decider or c.gov_b).action_approve(comment="publish")
    m.invalidate_recordset()
    assert m.state == "published"
    return v


def run(c, user=None, **kw):
    vals = {"pipeline_id": c.pipe.id, "stage": "bronze"}
    vals.update(kw)
    return c.env["fix.data.run"].with_user(user or c.plain).create(vals)


def incident(c, user=None, **kw):
    vals = {"entity_id": c.ent.id, "title": "A11M62 duplicate payment lines", "severity": "high"}
    vals.update(kw)
    return c.env["fix.data.incident"].with_user(user or c.plain).create(vals)


def dqtest(c, user=None, **kw):
    vals = {"rule_id": c.rule.id}
    vals.update(kw)
    return c.env["fix.data.quality.test"].with_user(user or c.gov).create(vals)


def retention(c, user=None, **kw):
    vals = {
        "name": "A11M62 Retention - Identity Documents",
        "entity_id": c.ent_s3.id,
        "tier": "hot",
        "retention_months": 84,
        "volume_gb": 60,
        "purge_rule": "retain 7 years, then pseudonymise",
    }
    vals.update(kw)
    return c.env["fix.data.retention.policy"].with_user(user or c.gov).create(vals)


def incidents_for_rule(c, rule):
    return c.env["fix.data.incident"].sudo().search_count([("rule_id", "=", rule.id)])


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
    req = types.SimpleNamespace(env=c.env(user=c.plain.id))
    old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)
    g.request = req
    s.request = req
    try:
        yield types.SimpleNamespace(
            write=lambda **kw: mw(ctl, **kw), action=lambda **kw: ma(ctl, **kw), g=g
        )
    finally:
        g.request, s.request = old_g, old_s


# ============================================================ data contracts
def test_m62_01_contract_activation_is_the_engines_not_a_click(c):
    """Control (G1): a draft contract cannot be activated by a direct call —
    action_activate runs only from a decided M63 task."""
    k = contract(c)
    with pytest.raises(REFUSED):
        U(c, k, c.gov).action_activate()
    assert k.state == "draft"


def test_m62_02_author_activates_own_contract(c):
    """Control (G1/BRU-DAT-10): the co-signature is producer first, platform
    second — and the platform side is a DECIDED task, not the author's click.
    A plain user cannot even draft a contract (the rule book is the officer's)."""
    with pytest.raises(AccessError), c.env.cr.savepoint():
        contract(c, user=c.plain)
    k = contract(c)
    with pytest.raises(REFUSED):  # unsigned: the producer side comes first
        U(c, k, c.gov).action_request_approval()
    k.with_user(c.gov).action_producer_sign()
    with pytest.raises(REFUSED):  # signed, but activation is still the engine's
        U(c, k, c.gov).action_activate()
    assert k.state == "draft"


def test_m62_03_contract_born_active(c):
    """Control: create refuses state=active — a contract is born a DRAFT,
    whoever the caller is (and a plain user drafts nothing at all)."""
    with pytest.raises(AccessError), c.env.cr.savepoint():
        contract(c, user=c.plain)
    with pytest.raises(ValidationError, match="DRAFT"), c.env.cr.savepoint():
        contract(c, state="active")


def test_m62_04_active_contract_terms_frozen(c):
    """Control (G1): the active row is frozen — schema, guarantees, SLA and
    notice days change only through a NEW VERSION."""
    k = activate(c, contract(c))
    with pytest.raises(REFUSED):  # a plain user cannot write a contract at all
        U(c, k).write(
            {
                "schema_version": "9.9",
                "guarantees": "nothing guaranteed",
                "freshness_sla_minutes": 100000,
                "breaking_change_notice_days": 0,
            }
        )
    with pytest.raises(UserError, match="ACTIVE and frozen"):
        U(c, k, c.gov).write({"schema_version": "9.9", "breaking_change_notice_days": 0})
    assert (k.schema_version, k.breaking_change_notice_days) == ("1.0", 14)
    # the governed change: a new draft version that supersedes v1
    v2 = U(c, k, c.gov).action_new_version()
    assert (v2.state, v2.version, v2.predecessor_id.id) == ("draft", 2, k.id)


def test_m62_05_contract_terms_edited_via_p03(c, p03):
    """Control (P03): the write endpoint refuses a plain user (ACL) and never
    offers the frozen fields on the screen (whitelist)."""
    k = activate(c, contract(c))
    res = p03.write(
        model="fix.data.contract",
        record_id=k.id,
        values={"schema_version": "7.0", "breaking_change_notice_days": 0},
    )
    k.invalidate_recordset()
    assert "error" in res, "P03 rewrote an active contract: %s" % res
    assert (k.schema_version, k.breaking_change_notice_days) == ("1.0", 14)


def test_m62_06_contract_state_forged_via_p03(c, p03):
    """Control (P03 + G1): `state` is not on the form's writable whitelist and
    the model refuses a state write — draft -> active needs the engine."""
    k = contract(c)
    res = p03.write(model="fix.data.contract", record_id=k.id, values={"state": "active"})
    k.invalidate_recordset()
    assert "error" in res and k.state == "draft", (
        "P03 forged contract state draft->active: %s" % res
    )


def test_m62_07_contract_reverted_active_to_draft(c):
    """Control: an active contract cannot be written back to draft — the
    lifecycle belongs to its actions."""
    k = activate(c, contract(c))
    with pytest.raises(REFUSED):
        U(c, k).write({"state": "draft"})
    with pytest.raises(UserError, match="only through its own actions"):
        U(c, k, c.gov).write({"state": "draft"})
    assert k.state == "active"


# ============================================================ metric registry
def test_m62_08_metric_born_published(c):
    """Control: create refuses state=published on the definition AND on the
    version — publication is earned through a reviewed, approved version."""
    with pytest.raises(AccessError), c.env.cr.savepoint():
        metric(c, user=c.plain)
    with pytest.raises(ValidationError, match="DRAFT"), c.env.cr.savepoint():
        metric(c, state="published")
    with pytest.raises(ValidationError, match="DRAFT"), c.env.cr.savepoint():
        c.env["fix.metric.version"].with_user(c.gov).create(
            {
                "definition_id": metric(c, suffix="v").id,
                "definition_text": "x",
                "state": "published",
            }
        )


def test_m62_09_metric_published_by_author_without_review(c):
    """Control (G2): there is no publish button on the definition at all; the
    version's publish action runs only from a decided M63 task."""
    m = metric(c)
    assert not hasattr(type(m), "action_publish"), "a one-click publish exists on the definition"
    v = (
        c.env["fix.metric.version"]
        .with_user(c.gov)
        .create({"definition_id": m.id, "definition_text": m.definition, "grain": m.grain})
    )
    with pytest.raises(REFUSED):  # the steward review comes first
        v.with_user(c.gov).action_request_approval()
    v.with_user(c.gov).action_steward_review()
    with pytest.raises(REFUSED):  # reviewed, but publication is the engine's
        v.with_user(c.gov).action_approve_publish()
    assert m.state == "draft"


def test_m62_10_metric_publish_without_owner_or_source(c):
    """Control (BRU-DAT-02): an empty definition cannot be routed — the
    version must state its formula, and the review gate runs before M63."""
    m = metric(c, suffix="2", owner_role=False, source_entity_id=False, definition="x")
    v = (
        c.env["fix.metric.version"]
        .with_user(c.gov)
        .create(
            {
                "definition_id": m.id,
                "definition_text": "x",
                "grain": m.grain,
                "source_entity_id": False,
            }
        )
    )
    v.with_user(c.gov).action_steward_review()
    v.with_user(c.gov).action_request_approval()
    task = v.approval_request_id.task_ids.filtered(
        lambda t: t.assigned_user_id == c.gov_b and t.state == "pending"
    )
    assert task, "the review + approval path exists for a routed version"
    task.with_user(c.gov_b).action_approve(comment="published with the steward's review")
    m.invalidate_recordset()
    assert m.state == "published" and m.current_version_id.state == "published"


def test_m62_11_published_definition_changed_in_place(c):
    """Control (G2): a plain user cannot touch a published definition (the
    rule book is the officer's), and the published RULING the tiles resolve
    lives in the version, not in the definition's working text."""
    m = metric(c)
    publish(c, m)
    with pytest.raises(AccessError):
        U(c, m).write({"definition": "completed orders / 1 (always 100%)", "grain": "fiscal_year"})
    assert m.state == "published" and m.resolve().state == "published"
    assert m.resolve().definition_text == m.definition


def test_m62_12_published_definition_changed_via_p03(c, p03):
    """Control (P03): the Metric Definition form refuses the rewrite."""
    m = metric(c)
    publish(c, m)
    res = p03.write(
        model="fix.metric.definition",
        record_id=m.id,
        values={"definition": "P03 rewrite", "code": "A11M62-MET-RENAMED"},
    )
    m.invalidate_recordset()
    assert "error" in res and m.definition != "P03 rewrite", (
        "P03 rewrote a published metric: %s" % res
    )


def test_m62_13_metric_retired_by_write(c, p03):
    """Control: retire is an action with its own rules, never a state write —
    and the consumer register exists to check retirements against."""
    m = metric(c)
    publish(c, m)
    res = p03.write(model="fix.metric.definition", record_id=m.id, values={"state": "retired"})
    m.invalidate_recordset()
    assert "error" in res and m.state == "published", (
        "P03 retired a published metric by a form write: %s" % res
    )
    assert "fix.metric.consumer" in c.env


def test_m62_14_metric_and_contract_cannot_be_deleted_by_plain_user(c):
    """Control: ACL perm_unlink=0 for base.group_user on contracts, metrics,
    versions and evidence; a retention policy refuses unlink for everyone
    (its own guard fires before the ACL even needs to)."""
    m = metric(c)
    k = contract(c)
    v = (
        c.env["fix.metric.version"]
        .with_user(c.gov)
        .create({"definition_id": m.id, "definition_text": m.definition, "grain": m.grain})
    )
    for rec in (m, k, v):
        with pytest.raises(AccessError):
            U(c, rec).unlink()
    with pytest.raises(UserError, match="deactivated, never deleted"):
        U(c, retention(c)).unlink()


def test_m62_15_metric_code_unique(c):
    """Control: UNIQUE(code, company_id) on fix.metric.definition.

    The duplicate surfaces either as Odoo's translated ValidationError (if
    the ORM flushes inside create) or the raw psycopg2 IntegrityError (if it
    surfaces at flush_all) — both mean the constraint held."""
    metric(c)
    with pytest.raises((ValidationError, psycopg2.IntegrityError)), c.env.cr.savepoint():
        metric(c, user=c.gov_b)
        c.env.flush_all()


# ============================================================ data-quality rules and tests
def test_m62_16_the_runner_measures_the_caller_does_not_type(c):
    """Control (G3/E5): action_measure takes NOTHING from the caller — it
    reads the entity's own data. A manual result may still be recorded by an
    officer, but it is labelled manual and can never pose as a measurement.
    A plain user records nothing at all (the rule book is the officer's)."""
    sig = inspect.signature(type(c.rule).action_measure)
    assert not [n for n in sig.parameters if n != "self"], (
        "GAP: action_measure%s accepts a caller-typed value" % sig
    )
    with pytest.raises(AccessError):
        U(c, c.rule).action_check(100.0)
    U(c, c.rule, c.gov).action_check(100.0)
    assert c.rule.last_measured is False, "a typed result is labelled manual, never 'measured'"


def test_m62_17_rule_failing_check_publishes_event(c):
    """Control (G3): a result below threshold sets failing and publishes
    data_quality.failing, with the comparator owned by the rule."""
    U(c, c.rule, c.gov).action_check(40.0)
    assert (c.rule.state, c.rule.last_result) == ("failing", 40.0)
    n = (
        c.env["fix.event.outbox"]
        .sudo()
        .search_count(
            [("event_type", "=", "data_quality.failing"), ("aggregate_id", "=", c.rule.id)]
        )
    )
    assert n == 1


def test_m62_18_failing_rule_opens_incident(c):
    """Control (G3/M62-9): the data_quality.failing consumer opens an incident
    for the failing rule's entity, marks the area degraded, and is idempotent
    per event."""
    c.env["fix.data.incident"].sudo().consume_data_quality_failing(
        {
            "event_id": "a11m62-evt-1",
            "aggregate_id": c.rule.id,
            "payload": {"entity": c.ent.name, "result": 10.0, "threshold": 95.0, "measured": False},
            "company_id": c.env.company.id,
        }
    )
    assert incidents_for_rule(c, c.rule) == 1
    assert c.ent.degraded is True
    # a redelivered event finds its incident and does nothing
    c.env["fix.data.incident"].sudo().consume_data_quality_failing(
        {
            "event_id": "a11m62-evt-1",
            "aggregate_id": c.rule.id,
            "payload": {},
            "company_id": c.env.company.id,
        }
    )
    assert incidents_for_rule(c, c.rule) == 1


def test_m62_19_rule_state_forged_by_write(c):
    """Control: the failing state and the stamps are the engine's — and the
    rule itself is not writable by a plain user at all."""
    U(c, c.rule, c.gov).action_check(10.0)
    with pytest.raises(AccessError):
        U(c, c.rule).write(
            {"state": "passing", "last_result": 100.0, "last_checked": fields.Datetime.now()}
        )
    assert (c.rule.state, c.rule.last_result) == ("failing", 10.0)


def test_m62_20_rule_state_forged_via_p03(c, p03):
    """Control (P03): the Quality Rule form never offers the state."""
    U(c, c.rule, c.gov).action_check(10.0)
    res = p03.write(model="fix.data.quality.rule", record_id=c.rule.id, values={"state": "passing"})
    c.rule.invalidate_recordset()
    assert "error" in res and c.rule.state == "failing", (
        "P03 forged failing rule to passing: %s" % res
    )


def test_m62_21_p03_refuses_readonly_last_result(c, p03):
    """Control: /p03/model/write refuses a change to the readonly last_result."""
    U(c, c.rule, c.gov).action_check(10.0)
    res = p03.write(
        model="fix.data.quality.rule", record_id=c.rule.id, values={"last_result": 100.0}
    )
    c.rule.invalidate_recordset()
    assert c.rule.last_result == 10.0 and "error" in res


def test_m62_22_test_pass_semantics_match_rule(c):
    """Control (E5): ONE comparator both sides use — a quality percentage at
    or above the threshold passes. 99% complete passes, 10% fails."""
    good = dqtest(c, observed_value=99.0)
    bad = dqtest(c, observed_value=10.0)
    assert (good.threshold, good.passed, bad.passed) == (95.0, True, False), (
        "GAP: pass/fail inverted vs the rule: 99%% -> %s, 10%% -> %s" % (good.passed, bad.passed)
    )


def test_m62_23_test_threshold_is_the_rules(c):
    """Control (E23): the tester's typed threshold is overwritten — the
    evidence row records the RULE's threshold at run time."""
    t = dqtest(c, observed_value=10.0, threshold=1000.0)
    assert (t.threshold, t.passed) == (c.rule.threshold, False), (
        "GAP: tester set threshold %.0f (rule says %.0f)" % (t.threshold, c.rule.threshold)
    )


def test_m62_24_test_result_edited_after_the_fact(c):
    """Control: a test execution is immutable evidence — write and unlink
    refuse, for everyone (the officer can only append)."""
    t = dqtest(c, observed_value=500.0)
    first = t.passed
    with pytest.raises(UserError, match="cannot be edited"):
        U(c, t).write({"observed_value": 1.0, "checked_at": fields.Datetime.now()})
    with pytest.raises(UserError, match="cannot be edited"):
        U(c, t, c.gov).write({"observed_value": 1.0})
    with pytest.raises(UserError, match="cannot be deleted"):
        U(c, t, c.gov).unlink()
    assert t.passed == first


def test_m62_25_test_typed_via_p03(c, p03):
    """Control (P03): the form creates evidence rows only for those allowed
    (an officer), drops the threshold field, and the verdict still computes
    from the rule's comparator — a typed 0% observed can never pass."""
    res = p03.write(
        model="fix.data.quality.test",
        record_id=None,
        values={"rule_id": c.rule.id, "observed_value": 0.0, "threshold": 1.0, "note": "typed"},
    )
    t = c.env["fix.data.quality.test"].sudo().browse(res.get("id") or 0).exists()
    if t:  # the plain user was refused by the ACL
        assert not t.passed and not t.measured and t.threshold == c.rule.threshold
    else:
        assert "error" in res


def test_m62_26_failing_test_is_labelled_evidence(c):
    """Control: a directly recorded failing test is labelled manual evidence —
    it does not flip the rule (the rule's own check/measure does that)."""
    t = dqtest(c, observed_value=10.0)
    assert t.passed is False and t.measured is False
    # A11 deep audit A3-F04: a rule nothing has measured is "Not yet tested",
    # not 'passing' (it was born 'passing' and the typed row left it there).
    assert c.rule.state == "untested", "a typed evidence row drove the rule's state"


# ============================================================ incidents
def test_m62_27_incident_close_requires_fixed(c):
    """Control: action_close refuses an open incident."""
    i = incident(c)
    with pytest.raises(UserError):
        U(c, i).action_close()


def test_m62_28_incident_closed_without_owner_or_root_cause(c):
    """Control (G4): Fix demands an owner; Close demands owner, root cause and
    resolution — and a high/critical incident is not closed by its reporter."""
    i = incident(c)  # reporter = the plain user, severity high
    with pytest.raises(UserError, match="owner"):
        U(c, i).action_fix()
    i.write(
        {
            "owner_id": c.plain.id,
            "root_cause": "bKash file layout change",
            "resolution": "replayed the file with the mapped layout",
        }
    )
    U(c, i).action_fix()
    with pytest.raises(UserError, match="not closed by its own reporter"):
        U(c, i).action_close()
    U(c, i, c.gov).action_close()  # an officer closes what anyone reported
    assert i.state == "closed"


def test_m62_29_incident_born_closed(c):
    """Control: an incident is born OPEN — create refuses anything else."""
    with pytest.raises(ValidationError, match="created OPEN"), c.env.cr.savepoint():
        incident(c, state="closed")


def test_m62_30_incident_closed_via_p03(c, p03):
    """Control (P03): the Incident form never offers the state field."""
    i = incident(c)
    res = p03.write(model="fix.data.incident", record_id=i.id, values={"state": "closed"})
    i.invalidate_recordset()
    assert "error" in res and i.state == "open", "P03 closed an open incident: %s" % res


def test_m62_31_closed_incident_rewritten(c):
    """Control (E31): closed is FINAL — no severity downgrade, no resolution
    rewrite, no reopen; a new finding is a new incident. Deletion is refused."""
    i = incident(
        c,
        severity="low",
        owner_id=c.plain.id,
        root_cause="dup lines from bKash file 2026-10-27",
        resolution="merged the duplicates",
    )
    U(c, i).action_fix()
    U(c, i).action_close()  # low severity: the reporter may close their own
    with pytest.raises(UserError, match="closed — a closed incident is final"):
        U(c, i).write({"severity": "low", "resolution": "", "state": "open", "resolved_at": False})
    with pytest.raises(UserError, match="cannot be deleted"):
        U(c, i).unlink()
    assert (i.severity, i.state, i.resolution) == ("low", "closed", "merged the duplicates")


# ============================================================ retention
def test_m62_32_retention_enforced_by_something(c):
    """Control (G5): retention is executed — the disposition action, the
    weekly report cron and the append-only evidence log exist."""
    crons = (
        c.env["ir.cron"]
        .sudo()
        .with_context(active_test=False)
        .search(
            [
                (
                    "model_id.model",
                    "in",
                    [
                        "fix.data.retention.policy",
                        "fix.data.entity",
                        "fix.data.pipeline",
                        "fix.data.quality.rule",
                        "fix.data.quality.test",
                        "fix.metric.definition",
                    ],
                )
            ]
        )
    )
    Model = type(c.env["fix.data.retention.policy"])
    own = set(vars(Model)) | {
        n
        for k in Model.__mro__
        if k.__module__.startswith("odoo.addons.cd_metric_registry")
        for n in vars(k)
    }
    methods = sorted(
        n
        for n in own
        if any(w in n for w in ("purge", "enforce", "archive", "cron", "expire"))
        and n not in Model._fields
        and callable(getattr(Model, n, None))
    )
    assert crons or methods, (
        "GAP: retention is register-only — no cron, no purge method (crons=%s methods=%s)"
        % (crons.ids, methods)
    )
    assert "fix.data.purge.evidence" in c.env


def test_m62_33_plain_user_shortens_statutory_retention(c):
    """Control (G5/E35): a plain user writes nothing on a policy; the officer
    cannot shorten in place either — shortening is an M63 request; below the
    statutory floor nothing shortens at all."""
    p = retention(c)
    with pytest.raises(REFUSED):  # the guard fires before the ACL even needs to
        U(c, p, c.plain2).write({"retention_months": 1, "purge_rule": "delete"})
    with pytest.raises(UserError, match="retention change"):
        U(c, p, c.plain2).write({"retention_months": 1})
    with pytest.raises(UserError, match="retention change"):
        U(c, p, c.gov).write({"retention_months": 1, "purge_rule": "delete"})
    with pytest.raises(ValidationError, match="statutory floor"), c.env.cr.savepoint():
        # a second entity's policy: one-policy-per-entity must not mask the floor
        retention(c, entity_id=c.ent.id, retention_months=1, statutory_floor_months=84)
    assert p.retention_months == 84


def test_m62_34_retention_shortened_via_p03(c, p03):
    """Control (P03): the Retention form is the officer's — a plain user gets
    the ACL refusal, and the months stay 84."""
    p = retention(c)
    res = p03.write(
        model="fix.data.retention.policy",
        record_id=p.id,
        values={"retention_months": 0, "purge_rule": "delete now"},
    )
    p.invalidate_recordset()
    assert "error" in res and p.retention_months == 84, "P03 set retention to %s: %s" % (
        p.retention_months,
        res,
    )


def test_m62_35_retention_zero_or_negative(c):
    """Control: a retention period is at least 1 month."""
    with pytest.raises(ValidationError, match="at least 1 month"), c.env.cr.savepoint():
        retention(c, retention_months=-12)


def test_m62_36_legal_hold_exists_and_blocks_everything(c):
    """Control (G5): a legal hold blocks the period, the active flag and the
    hold itself, until an officer lifts it; deactivation is an officer's act."""
    p = retention(c)
    assert "legal_hold" in p._fields
    with pytest.raises(REFUSED):  # a plain user cannot switch a policy off
        U(c, p, c.plain2).write({"active": False})
    U(c, p, c.gov).write({"legal_hold": True})  # the officer sets the hold
    with pytest.raises(UserError, match="LEGAL HOLD"):
        U(c, p, c.gov).write({"retention_months": 24})
    with pytest.raises(UserError, match="LEGAL HOLD"):
        U(c, p, c.gov).write({"active": False})
    with pytest.raises(REFUSED):  # a plain user neither lifts nor edits the hold
        U(c, p).write({"legal_hold": False})
    U(c, p, c.gov).write({"legal_hold": False})  # the officer lifts it again
    assert (p.retention_months, p.active, p.legal_hold) == (84, True, False)


def test_m62_37_retention_policy_cannot_be_deleted(c):
    """Control: a policy is deactivated, never deleted — unlink refuses for
    the officer too, and the ACL refuses the plain user first."""
    p = retention(c)
    with pytest.raises(REFUSED):
        U(c, p).unlink()
    with pytest.raises(UserError, match="deactivated, never deleted"):
        U(c, p, c.gov).unlink()


def test_m62_38_retention_duplicate_and_inconsistent(c):
    """Control (E38): one active policy per entity."""
    retention(c)
    with pytest.raises(ValidationError, match=r"one.*policy per entity"), c.env.cr.savepoint():
        retention(c, user=c.gov_b, name="A11M62 dup", retention_months=3, tier="cold")
    n = c.env["fix.data.retention.policy"].sudo().search_count([("entity_id", "=", c.ent_s3.id)])
    assert n == 1


# ============================================================ pipelines and runs
def test_m62_39_run_finish_only_from_running(c):
    """Control: action_finish refuses a failed run."""
    r = run(c)
    U(c, r).action_fail()
    with pytest.raises(UserError):
        U(c, r).action_finish()


def test_m62_40_run_born_succeeded(c):
    """Control (E40): a run starts 'running' — create refuses a born-succeeded
    run with typed row counts."""
    with pytest.raises(ValidationError, match="starts 'running'"), c.env.cr.savepoint():
        run(
            c,
            state="succeeded",
            rows_read=0,
            rows_written=1000000,
            finished_at=fields.Datetime.now(),
        )


def test_m62_41_failed_run_forged_to_succeeded(c, p03):
    """Control (E43 + P03): state changes only through Finish/Fail — the ORM
    guard refuses the write and the form never offers the field."""
    r = run(c)
    U(c, r).action_fail()
    with pytest.raises(UserError, match="only through Finish or Fail"):
        U(c, r).write({"state": "succeeded"})
    res = p03.write(model="fix.data.run", record_id=r.id, values={"state": "succeeded"})
    r.invalidate_recordset()
    assert "error" in res and r.state == "failed", (
        "P03 turned a failed run into succeeded: %s" % res
    )


def test_m62_42_finish_reconciles_rows(c):
    """Control (E42): a load cannot write more rows than it read and rejected
    combined — '1,000,000 written, 0 read' is refused."""
    r = run(c, rows_read=10, rows_written=5000, rows_rejected=900)
    with pytest.raises(UserError, match="cannot create rows"):
        U(c, r).action_finish()
    assert r.state == "running" and not c.pipe.last_success_at


def test_m62_43_fail_needs_reason(c):
    """Control: a failure always carries a reason — stamped when the caller
    gave none."""
    r = run(c)
    U(c, r).action_fail()
    n_inc = c.env["fix.data.incident"].sudo().search_count([("entity_id", "=", c.ent.id)])
    assert r.failure_reason or n_inc, "GAP: run failed with no failure_reason and no incident/alert"


def test_m62_44_pipeline_last_success_forged_hides_breach(c):
    """Control (E44): the success stamps are GUARDED engine fields — a plain
    write is refused, and the Freshness SLA keeps reporting the truth; only a
    real finished run (through the guard) stamps the pipeline."""
    from odoo.addons.cd_p03_portal.controllers.a11 import m62 as M

    def breach(env):
        rows = M.freshness_sla(env)["rows"]
        return [r["breach"] for r in rows if r["pipeline"] == "A11M62-PL"]

    with pytest.raises(UserError, match="cannot be set directly"):
        U(c, c.pipe).write(
            {"last_success_at": fields.Datetime.now(), "last_run_at": fields.Datetime.now()}
        )
    runs = (
        c.env["fix.data.run"]
        .sudo()
        .search_count([("pipeline_id", "=", c.pipe.id), ("state", "=", "succeeded")])
    )
    assert runs == 0 and breach(c.env(user=c.plain.id)) == [
        "—"
    ], "GAP: last_success_at forged; Freshness SLA reports breach=No with 0 succeeded runs"
    # the governed path: a reconciled run finished by the plain operator
    r = run(c, rows_read=100, rows_written=100)
    U(c, r).action_finish()
    assert c.pipe.last_success_at and breach(c.env(user=c.plain.id)) == ["No"]


def test_m62_45_retired_pipeline_resumed_and_run(c):
    """Control (E45): retired is retired — no resume, and a retired pipeline
    runs nothing (not even a manual backfill)."""
    U(c, c.pipe).write({"state": "retired"})
    with pytest.raises(UserError, match="retired is retired"):
        U(c, c.pipe).action_resume()
    with pytest.raises(ValidationError, match="runs nothing"), c.env.cr.savepoint():
        run(c)
    assert c.pipe.state == "retired"


# ============================================================ catalogue
def test_m62_46_catalogue_rows_are_the_officers(c):
    """Control (G1): the catalogue is governance config — a plain user cannot
    create or edit entities; the officer registers them (BRU-DAT-09 names the
    steward on the row)."""
    with pytest.raises(AccessError), c.env.cr.savepoint():
        c.env["fix.data.entity"].with_user(c.plain).create({"name": "A11M62 no steward"})
    e = (
        c.env["fix.data.entity"]
        .with_user(c.gov)
        .create({"name": "A11M62 officer row", "steward_id": False})
    )
    assert not e.steward_id  # the steward is named in use; §7 decides floors


def test_m62_47_s3_declassified_by_plain_user(c, p03):
    """Control (G6/BRU-DAT-11): a downgrade needs an approved, time-limited
    authorisation routed through M63 — a plain P03 write is refused, and the
    officer's own write is refused until the authorisation is decided."""
    res = p03.write(
        model="fix.data.entity", record_id=c.ent_s3.id, values={"classification": "public"}
    )
    c.ent_s3.invalidate_recordset()
    assert "error" in res and c.ent_s3.classification == "residency_classified", (
        "S3 entity declassified to %s by a plain user: %s" % (c.ent_s3.classification, res)
    )
    with pytest.raises(UserError, match="declassification authorisation"):
        c.ent_s3.with_user(c.gov).write({"classification": "public"})
    # the governed path: an authorisation is drafted, routed and decided
    auth = (
        c.env["fix.data.declassification.auth"]
        .with_user(c.gov)
        .create(
            {
                "entity_id": c.ent_s3.id,
                "from_classification": "residency_classified",
                "to_classification": "public",
                "reason": "board-approved open data pilot",
                "expires_on": fields.Date.today() + datetime.timedelta(days=30),
            }
        )
    )
    auth.with_user(c.gov).action_request_approval()
    task = auth.approval_request_id.task_ids.filtered(
        lambda t: t.assigned_user_id == c.gov_b and t.state == "pending"
    )
    assert task, "the declassification routes through M63"
    task.with_user(c.gov_b).action_approve(comment="granted, time-limited")
    c.ent_s3.with_user(c.gov).write({"classification": "public"})
    assert c.ent_s3.classification == "public" and auth.state == "approved"


def test_m62_48_nfr086c_guard_is_by_layer_not_name(c):
    """Control (G6): the residency guard reads the warehouse LAYER, never the
    name — a 'warehouse'-named S3 entity outside the warehouse passes, an
    innocent-named S3 entity inside it is refused."""
    E = c.env["fix.data.entity"].with_user(c.gov)
    e = E.create(
        {"name": "warehouse.dim_party_nid", "classification": "residency_classified"}
    )  # layer 'none'
    assert e.warehouse_layer == "none"
    with pytest.raises(ValidationError, match="NFR-086c"), c.env.cr.savepoint():
        E.create(
            {
                "name": "dwh.gold.dim_party_nid",
                "classification": "residency_classified",
                "warehouse_layer": "gold",
            }
        )


def test_m62_49_lineage_self_loop(c):
    """Control: a lineage edge from an entity to itself is refused — it pads
    the coverage count and documents nothing."""
    with pytest.raises(AccessError), c.env.cr.savepoint():
        c.env["fix.data.lineage"].with_user(c.plain).create(
            {"name": "loop", "source_entity_id": c.ent.id, "target_entity_id": c.ent.id}
        )
    with pytest.raises(ValidationError, match="self-loop"), c.env.cr.savepoint():
        c.env["fix.data.lineage"].with_user(c.gov).create(
            {"name": "loop", "source_entity_id": c.ent.id, "target_entity_id": c.ent.id}
        )


# ============================================================ hand-offs / KPIs / M63
def test_m62_50_measured_bank_and_the_registry_are_separate(c):
    """Hand-off (spec: 'a metric is defined once, in M62's semantic layer').
    The remediated design: M62 owns the DEFINITIONS (registry, versions,
    publication state — what the metric IS); M25's bank MEASURES the
    operational numbers. Rewriting or retiring definitions must not move a
    measured number, and the registry's own KPI must move with it."""
    from odoo.addons.cd_p03_portal.controllers.a11 import m25 as M25
    from odoo.addons.cd_p03_portal.controllers.a11 import m62 as M

    for code in ("MET-SLA-ATTAIN", "MET-AR-OVERDUE", "MET-WIP-AGE"):
        publish(c, metric(c, suffix=code))
    uenv = c.env(user=c.plain.id)
    before = M25._metrics(uenv)
    registry_before = M.kpis(uenv)["metrics_published"]
    assert registry_before >= 3
    defs = c.env["fix.metric.definition"].sudo().search([])
    defs.write({"definition": "0", "state": "retired"})
    after = M25._metrics(uenv)
    assert before == after, "a registry edit moved a measured number"
    assert M.kpis(uenv)["metrics_published"] == 0, "the registry KPI ignored its definitions"


def test_m62_51_m62_kpis_are_the_callers_read(c):
    """Control (E6): KPIs run as the caller — company B's contracts do not
    leak into company A's tiles."""
    from odoo.addons.cd_p03_portal.controllers.a11 import m62 as M

    co_b = c.env["res.company"].create({"name": "A11M62 Company B"})
    ent_b = c.env["fix.data.entity"].create({"name": "A11M62 B ent", "company_id": co_b.id})
    for i in range(3):
        c.env["fix.data.contract"].create(
            {
                "dataset_code": "A11M62-B-%d" % i,
                "name": "B",
                "entity_id": ent_b.id,
                "producer": "B",
                "company_id": co_b.id,
            }
        )  # born draft, company B
    activate(c, contract(c, suffix="A"))  # company A's one active contract
    uenv = c.env(user=c.plain.id)
    visible = uenv["fix.data.contract"].search_count([("state", "=", "active")])
    own = (
        c.env["fix.data.contract"]
        .sudo()
        .search_count([("state", "=", "active"), ("company_id", "in", c.plain.company_ids.ids)])
    )
    assert c.env["fix.data.contract"].sudo().search_count([("company_id", "=", co_b.id)]) == 3
    assert visible == own, "record rules already differ from the caller's companies"
    assert M.kpis(uenv)["contracts_active"] == visible, "KPI counts another company's contracts"


def test_m62_52_quality_failures_kpi_counts_failures_not_good_loads(c):
    """Control (E5): with the one comparator, 99%-complete loads pass — ten
    healthy loads must not raise the 'Quality Failures' tile."""
    from odoo.addons.cd_p03_portal.controllers.a11 import m62 as M

    uenv = c.env(user=c.plain.id)
    before = M.kpis(uenv)["quality_failures"]
    for _ in range(10):
        dqtest(c, observed_value=99.0)
    after = M.kpis(uenv)["quality_failures"]
    assert after == before, "10 healthy (99%%) loads raised 'Quality Failures' %d -> %d" % (
        before,
        after,
    )


def test_m62_53_m63_approval_on_m62_models(c):
    """Control (G1/G2/G5/G6): the M62 governance acts route through the M63
    approval engine."""
    have = {
        m: hasattr(c.env[m], "action_request_approval")
        for m in (
            "fix.data.contract",
            "fix.metric.version",
            "fix.data.retention.policy",
            "fix.data.declassification.auth",
        )
    }
    assert all(have.values()), "an M62 governance model lost its M63 routing: %s" % have


def test_m62_54_p03_surfaces_have_writable_whitelist(c, p03):
    """Control (S2): every M62 surface declares its writable whitelist —
    exactly the fields the workspace forms offer — and the workflow fields
    (states, stamps, the engine's thresholds) are on NO list."""
    from odoo.addons.cd_p03_portal.controllers.a11 import m62 as M

    missing = [m for m, conf in M.SURFACES.items() if "writable" not in conf]
    assert not missing, "GAP: %d/%d M62 surfaces have no writable whitelist: %s" % (
        len(missing),
        len(M.SURFACES),
        missing,
    )
    for model, conf in M.SURFACES.items():
        assert "state" not in conf["writable"], "%s offers the state field" % model
    assert not ({"last_success_at", "last_run_at"} & M.WRITABLE["fix.data.pipeline"])
    assert "threshold" not in M.WRITABLE["fix.data.quality.test"]
    assert not M.WRITABLE["fix.data.purge.evidence"], "evidence is append-only"
    # M62 capture audit 2026-11-18: a version is DRAFTED from a form (with an
    # empty list no version could be drafted, so nothing could be published
    # from the workspace); its state, review/publication stamps and impact
    # list still change only through its actions.
    assert not (
        {
            "state",
            "version",
            "steward_reviewed_by",
            "steward_reviewed_at",
            "published_by",
            "published_at",
            "impact_snapshot",
        }
        & M.WRITABLE["fix.metric.version"]
    ), "a version's lifecycle changes only through its actions"


def test_m62_55_reference_superuser_rule_check(c):
    """Reference (superuser): the comparator arithmetic on the proper path."""
    c.rule.action_check(97.5)
    assert c.rule.state == "passing"
    c.rule.action_check(94.9)
    assert c.rule.state == "failing"


# ============================================================ registry KPI tiles
# A11 deep audit A3-F05/F16 (2026-11-23): the registry's six tiles did not
# exist; the workspace showed six different ones. Each tile below is asserted
# against the state that produced it, including the cases where the honest
# answer is None ("—"), and against the report pack that must agree with it.
REGISTRY_TILES = [
    "certified_metrics",
    "quality_tests_passing",
    "freshness_lag",
    "lineage_coverage_pct",
    "pii_columns_masked",
    "warehouse_cost_mtd",
]


def _m62(module=None):
    """The m62 controller module (imported late: the portal must be installed)."""
    from odoo.addons.cd_p03_portal.controllers.a11 import m62 as M

    return M


def _kpis(c, user=None):
    return _m62().kpis(c.env(user=(user or c.plain).id))


def _lineage_table(env, name="KPI lineage"):
    """An entity mapped to a table whose rows are easy to measure."""
    env["fix.data.lineage"].create(
        {
            "name": "one edge",
            "source_entity_id": env["fix.data.entity"].create({"name": "KPI edge A"}).id,
            "target_entity_id": env["fix.data.entity"].create({"name": "KPI edge B"}).id,
        }
    )
    return env["fix.data.entity"].create({"name": name, "res_model": "fix.data.lineage"})


def test_m62_56_the_registry_tiles_are_served_first_in_contract_order(c):
    """A3-F05: the six registry tiles are served under the M62 key the fragment
    reads, before the operational counters, in the registry's order."""
    from odoo.addons.cd_p03_portal.controllers import a11

    payload = a11.kpis(c.env(user=c.plain.id), "M62")
    assert list(payload["M62"].keys())[:6] == REGISTRY_TILES


def test_m62_57_certified_metrics_needs_a_published_version(c):
    """A definition 'published' with no version is not certified — the seeded
    shape — and a governed publication is."""
    publish(c, metric(c, suffix="KPI"))
    seeded = metric(c, suffix="SEED")
    # the seeder's shape: the state without a version (the guard refuses it)
    c.env.cr.execute(
        "UPDATE fix_metric_definition SET state = 'published' WHERE id = %s", (seeded.id,)
    )
    c.env.invalidate_all()
    k = _kpis(c)
    assert k["certified_metrics"] == 1
    assert k["metrics_published"] == 1  # the same basis, never the five seed rows
    # retiring the definition removes it from the live certified set
    publish(c, metric(c, suffix="RETIRED"))
    retired = c.env["fix.metric.definition"].search([("code", "=", "A11M62-MET-RETIRED")])
    retired.with_user(c.gov).action_retire()
    assert _kpis(c)["certified_metrics"] == 1


def test_m62_58_contracts_active_counts_only_signed_rows(c):
    """A contract 'active' with no producer signature is not an active contract
    (the seeded shape); one that activated on both signatures is."""
    activate(c, contract(c, suffix="signed"))
    unsigned = contract(c, suffix="unsigned")
    c.env.cr.execute("UPDATE fix_data_contract SET state = 'active' WHERE id = %s", (unsigned.id,))
    c.env.invalidate_all()
    assert _kpis(c)["contracts_active"] == 1


def test_m62_59_quality_pass_rate_counts_measured_tests_only(c):
    """A3-F16: the pass rate is over MEASURED tests. One measured pass and one
    measured fail is 50%; a manual 100% row on another rule changes nothing."""
    entity = _lineage_table(c.env)
    good = c.env["fix.data.quality.rule"].create(
        {
            "name": "kpi measured pass",
            "entity_id": entity.id,
            "rule_type": "completeness",
            "check_field": "name",
            "threshold": 50.0,
        }
    )
    bad = c.env["fix.data.quality.rule"].create(
        {
            "name": "kpi measured fail",
            "entity_id": entity.id,
            "rule_type": "completeness",
            "check_field": "transformation",
            "threshold": 50.0,
        }
    )
    good.action_measure()  # the edge has a name: 100%
    bad.action_measure()  # no edge has a transformation: 0%
    assert _kpis(c)["quality_tests_passing"] == 50.0
    dqtest(c, observed_value=100.0)  # a person's 100% on c.rule (never measured)
    assert _kpis(c)["quality_tests_passing"] == 50.0


def test_m62_60_unmeasurable_tiles_are_none_never_zero(c):
    """No measured test, no successful run, no entity to cover: "—", not 0.
    (Read as a company with no M62 rows, so nothing of company A leaks in.)"""
    co_b = c.env["res.company"].create({"name": "A11M62 KPI Company B"})
    user_b = _user(c.env, "a11m62_kpi_b", company=co_b)
    k = _kpis(c, user_b)
    assert k["certified_metrics"] == 0
    assert k["quality_tests_passing"] is None
    assert k["freshness_lag"] is None
    assert k["lineage_coverage_pct"] is None
    assert k["pii_columns_masked"] == 0
    assert k["warehouse_cost_mtd"] == 0.0


def test_m62_61_freshness_lag_is_the_oldest_last_success(c):
    """The lag is minutes since the OLDEST success among active pipelines, and
    the tile equals the Freshness SLA row that reports it."""
    r = run(c, rows_read=1, rows_written=1)
    U(c, r).action_finish()
    # flush first: the finish wrote the stamp through the ORM, and a raw UPDATE
    # issued before that write is flushed would be overwritten by it.
    c.env.flush_all()
    c.env.cr.execute(
        "UPDATE fix_data_pipeline SET last_success_at = now() - interval '90 minutes', "
        "last_run_at = now() - interval '90 minutes' WHERE id = %s",
        (c.pipe.id,),
    )
    c.env.invalidate_all()
    k = _kpis(c)
    row = next(
        row
        for row in _m62().freshness_sla(c.env(user=c.plain.id))["rows"]
        if row["pipeline"] == "A11M62-PL"
    )
    assert k["freshness_lag"] == row["age_min"]
    assert 89 <= k["freshness_lag"] <= 90
    assert row["breach"] == "Yes"  # the 15-minute SLO is passed


def test_m62_62_lineage_coverage_is_edges_over_all_entities(c):
    """Two entities, one edge between them: 100%. A third entity with no edge
    drops it to 66.7% — and it equals the Lineage Coverage pack's own count."""
    a, b = c.env["fix.data.entity"].browse([c.ent.id, c.ent_s3.id])
    c.env["fix.data.lineage"].create(
        {"name": "kpi edge", "source_entity_id": a.id, "target_entity_id": b.id}
    )
    assert _kpis(c)["lineage_coverage_pct"] == 100.0
    c.env["fix.data.entity"].create({"name": "KPI unlinked"})
    assert _kpis(c)["lineage_coverage_pct"] == 66.7
    pack = _m62().lineage_coverage(c.env(user=c.plain.id))
    assert pack["title"].startswith("Lineage Coverage — 2 of 3")


def test_m62_63_warehouse_cost_is_the_sum_of_active_policies(c):
    """Hand-computed: 240 GB x 12 + 120 GB x 8 = 3,840 a month, and the tile
    equals the Cost per Domain pack's total on the same basis."""
    e1 = c.env["fix.data.entity"].create({"name": "KPI cost one", "owner_module": "M01"})
    e2 = c.env["fix.data.entity"].create({"name": "KPI cost two", "owner_module": "M20"})
    for entity, months, volume, rate in ((e1, 36, 240, 12.0), (e2, 84, 120, 8.0)):
        c.env["fix.data.retention.policy"].create(
            {
                "name": "KPI cost %s" % entity.name,
                "entity_id": entity.id,
                "retention_months": months,
                "volume_gb": volume,
                "storage_cost_per_gb": rate,
            }
        )
    pack = _m62().cost_per_domain(c.env(user=c.plain.id))
    assert _kpis(c)["warehouse_cost_mtd"] == pack["totals"]["monthly_cost"] == 3840.0


def test_m62_64_pii_columns_masked_counts_the_active_rules(c):
    """The tile is the active sensitive-field rules, read as the caller; an
    inactive classification is not masking anything."""
    S = c.env["fix.sensitive.field"]
    common = {"company_id": c.env.company.id, "sensitivity": "s2", "data_class": "pii"}
    S.create({"model_name": "res.partner", "field_name": "email", **common})
    S.create({"model_name": "res.partner", "field_name": "phone", **common})
    S.create({"model_name": "res.partner", "field_name": "vat", "active": False, **common})
    assert _kpis(c)["pii_columns_masked"] == 2


def test_m62_65_scorecard_names_measured_and_says_why_not(c):
    """A3-F16: the scorecard carries a Measured column (manual evidence vs
    cron-measured), a pass rate over measured tests only, and a plain reason
    per entity when nothing is measurable."""
    entity = _lineage_table(c.env, "KPI scorecard")
    for field, threshold in (("name", 50.0), ("transformation", 50.0)):
        c.env["fix.data.quality.rule"].create(
            {
                "name": "scorecard %s" % field,
                "entity_id": entity.id,
                "rule_type": "completeness",
                "check_field": field,
                "threshold": threshold,
            }
        ).action_measure()
    pack = _m62().quality_scorecard(c.env(user=c.plain.id))
    assert {"measured", "manual", "reason"} <= set(pack["cols"])
    row = {r["entity"]: r for r in pack["rows"]}["KPI scorecard"]
    assert (row["rules"], row["tested"], row["measured"], row["manual"]) == (2, 2, 2, 0)
    assert row["passed"] == 1 and row["pass_pct"] == 50.0 and row["reason"] == "—"

    # a rule that cannot run: its manual evidence is labelled, the pass rate
    # stays empty, and the row states the one reason
    dqtest(c, observed_value=100.0)
    mapped = c.env["fix.data.entity"].create(
        {"name": "KPI no check field", "res_model": "fix.data.lineage"}
    )
    c.env["fix.data.quality.rule"].create(
        {
            "name": "scorecard no field",
            "entity_id": mapped.id,
            "rule_type": "completeness",
            "threshold": 95.0,
        }
    )
    pack = _m62().quality_scorecard(c.env(user=c.plain.id))
    rows = {r["entity"]: r for r in pack["rows"]}
    # the fixture entity maps to no model; the new one maps to a table but its
    # rule names no column — each states its own reason, neither looks green
    blocked = rows["A11M62 fix_service_order"]
    assert (blocked["measured"], blocked["manual"], blocked["passed"]) == (0, 1, 0)
    assert blocked["pass_pct"] is None
    assert "maps to no Odoo model" in blocked["reason"]
    no_field = rows["KPI no check field"]
    assert no_field["measured"] == 0 and no_field["pass_pct"] is None
    assert "no check field" in no_field["reason"]


def test_m62_66_pipelines_active_is_a_register_with_no_executor(c):
    """A3-F02 honesty: the tile counts registry rows, and the fragment's tile
    says so — no executor is connected on this estate."""
    from pathlib import Path

    here = Path(__file__).resolve().parent
    fragment = (here.parent / "static" / "src" / "a11" / "m62.js").read_text(encoding="utf-8")
    assert "Pipeline register — no executor is connected" in fragment
    assert "no executor" in fragment
    assert "Pipelines Active" in fragment
    assert _kpis(c)["pipelines_active"] == 1  # the fixture's one active pipeline


def test_m62_67_the_six_tiles_after_the_repair_are_honest(c):
    """A3-F05 end to end: on the repaired live residue the six tiles are
    0 / — / — / 0% / 0 / ৳7,440 — every value observable, none fabricated."""
    import importlib.util
    from pathlib import Path

    # __file__ is .../addons/platform/cd_p03_portal/tests/<this file>
    addons = Path(__file__).resolve().parents[3]
    path = (
        addons
        / "domain"
        / "j_data_analytics"
        / "cd_metric_registry"
        / "tests"
        / "test_m62_integrity.py"
    )
    spec = importlib.util.spec_from_file_location("_b3_m62_integrity", path)
    integrity = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(integrity)

    integrity.live_residue(c.env)
    c.env["fix.data.entity"].action_repair_seed_residue()
    k = _kpis(c)
    assert k["certified_metrics"] == 0  # every seeded definition was drafted
    assert k["quality_tests_passing"] is None  # nothing was ever measured
    assert k["freshness_lag"] is None  # no run ever stamped a pipeline
    assert k["lineage_coverage_pct"] == 0.0  # 8 entities, not one lineage edge
    assert k["pii_columns_masked"] == 0  # no sensitive-field rule on the estate
    # the projection the Cost per Domain pack reports: 240x12 + 240x12 + 120x8 + 60x12
    assert k["warehouse_cost_mtd"] == 7440.0


def test_m62_68_pii_is_none_when_the_caller_may_not_read_the_register(c):
    """A3-F05: the PII tile is the CALLER's read. An account without read on
    M29's sensitive-field register gets None — never a sudo count of rows it
    cannot open."""
    Access = c.env["ir.model.access"].sudo()
    acl = Access.search(
        [
            ("model_id.model", "=", "fix.sensitive.field"),
            ("group_id", "=", c.env.ref("base.group_user").id),
        ]
    )
    assert acl, "base.group_user has no read row on fix.sensitive.field to withdraw"
    try:
        acl.unlink()
        c.env.flush_all()
        c.env.registry.clear_cache()
        assert _kpis(c)["pii_columns_masked"] is None
    finally:
        # the rollback restores the ACL row; the registry cache must re-read it
        c.env.registry.clear_cache()
