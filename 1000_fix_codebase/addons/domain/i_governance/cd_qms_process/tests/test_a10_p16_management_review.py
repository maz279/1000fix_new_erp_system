# A10 remediation (2026-11-05), P1-6: the management review (ISO 9.3).
#
# The audit found a review with no ISO 9.3 inputs (the pack lived in a
# report, not on the record), free-text decisions that tracked nothing, and
# a closed review that reopened because `state` was a typist's field
# (M23-8). Now: the inputs are PULLED from the system — one line per
# required 9.3.2 kind, each a count of real records — and never typed; the
# review is held only over a complete set, by the Quality Manager, with a
# chairperson named; the outputs are tracked action lines with owners; and
# the closure is TOP MANAGEMENT's routed decision (DOFA Tier 5 through the
# M63 inbox). A closed review does not reopen.
import itertools

import pytest
from odoo import fields
from odoo.exceptions import UserError

QM_GROUP = "cd_qms_process.group_qms_quality_manager"
TIER_5 = "cd_entity_config.group_dofa_tier_5"
TASK_KEY = "fix_approval_task"
GUARD = "changes only through its workflow"

_SEQ = itertools.count(1)

KINDS = {
    # the full ISO 9001:2015 9.3.2 set (A10 deep audit 2026-11-22, A1-F04)
    "prior_actions",
    "issues_changes",
    "customer_feedback",
    "objectives_attainment",
    "process_performance",
    "nonconformities",
    "monitoring_results",
    "audit_results",
    "external_providers",
    "resources_adequacy",
    "risk_effectiveness",
    "improvement_opportunities",
}


def _user(env, name, groups=()):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A10 P16 %s %d" % (name, n),
                "login": "a10p16.%s.%d@a10.test" % (name.replace(" ", "").lower(), n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])
                ],
            }
        )
    )


def _emp(env, user, name):
    return env["hr.employee"].create({"name": "A10 P16 %s" % name, "user_id": user.id})


def _tier5_only(env, *keep):
    """Reasoning about WHO the routed closure reaches: keep only this test's
    Tier 5 holders (the dev admin sits in every group by design; odoo_env
    rolls the change back)."""
    group = env.ref(TIER_5).sudo()
    keep_ids = {u.id for u in keep}
    others = group.user_ids.filtered(lambda u: u.id not in keep_ids)
    if others:
        group.write({"user_ids": [(3, u.id) for u in others]})


def _ou(env):
    return env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)


def _review(env, **kw):
    vals = {"name": kw.pop("name", "P16 review")}
    vals.update(kw)
    return env["fix.qms.review"].create(vals)


@pytest.fixture
def m(odoo_env):
    env = odoo_env
    x = lambda: None  # noqa: E731  (tiny namespace)
    x.env = env
    x.clerk = _user(env, "clerk")
    x.owner = _user(env, "owner")
    x.owner_emp = _emp(env, x.owner, "Action Owner")
    x.qm = _user(env, "qm", [QM_GROUP])
    x.qm_emp = _emp(env, x.qm, "Quality Manager")
    x.tier5 = _user(env, "tier5", [TIER_5])
    x.tier5_emp = _emp(env, x.tier5, "Managing Director")
    return x


def _source_data(env):
    """Real records in the window the pull must count."""
    complaint = env["fix.complaint"].create(
        {
            "operating_unit_id": _ou(env).id,
            "name": "CMP-P16",
            "customer_id": env["res.partner"].create({"name": "A10 P16 Customer"}).id,
            "severity": "critical",
            "state": "investigating",
            "description": "Wrong board returned",
        }
    )
    ncr = env["fix.ncr"].create(
        {"source": "service_order", "severity": "major", "description": "P16 defect"}
    )
    capa = env["fix.capa"].create(
        {
            "ncr_id": ncr.id,
            "severity": "major",
            "corrective_action": "P16 corrective action",
            "owner_id": env["hr.employee"].create({"name": "A10 P16 Capa Owner"}).id,
        }
    )
    copq = env["fix.qms.copq"].create(
        {
            "period": fields.Date.today().strftime("%Y-%m"),
            "category": "rework",
            "amount": 12500.0,
        }
    )
    return complaint, ncr, capa, copq


# ------------------------------------------------------------- the inputs
def test_inputs_are_pulled_from_the_system_never_typed(m):
    env = m.env
    # baselines: the shared database carries seeds, so the pull is judged on
    # what it COUNTS, not on an empty table
    company = [("company_id", "=", env.company.id)]
    base = {
        "complaints": env["fix.complaint"].sudo().search_count(company),
        "critical": env["fix.complaint"]
        .sudo()
        .search_count([*company, ("severity", "=", "critical")]),
        "ncrs": env["fix.ncr"].sudo().search_count(company),
        "capas": env["fix.capa"].sudo().search_count(company),
        "copq": round(
            sum(
                float(c.amount or 0.0)
                for c in env["fix.qms.copq"]
                .sudo()
                .search([*company, ("period", "<=", fields.Date.today().strftime("%Y-%m"))])
            ),
            2,
        ),
    }
    _source_data(env)
    rec = _review(env, review_date=fields.Date.context_today(env["res.partner"]))
    assert rec.inputs_missing == 12  # nothing pulled yet
    # the pull is the Quality Manager's act
    with pytest.raises(UserError, match="Only the Quality Manager"):
        rec.with_user(m.clerk).action_pull_inputs()
    rec.with_user(m.qm).action_pull_inputs()
    assert rec.inputs_missing == 0
    assert set(rec.input_ids.mapped("kind")) == KINDS
    by_kind = {i.kind: i for i in rec.input_ids}
    # each summary counts the records the system holds, in this company's
    # window — the created records move the numbers by exactly one
    assert "%d complaint(s) received" % (base["complaints"] + 1) in (
        by_kind["customer_feedback"].summary
    )
    assert "%d critical" % (base["critical"] + 1) in by_kind["customer_feedback"].summary
    assert "%d NCR(s) raised" % (base["ncrs"] + 1) in by_kind["process_performance"].summary
    assert "CoPQ BDT %.2f" % (base["copq"] + 12500.0) in (by_kind["process_performance"].summary)
    assert "%d CAPA(s) opened" % (base["capas"] + 1) in by_kind["nonconformities"].summary
    assert all(i.pulled_on for i in rec.input_ids)
    # typed inputs are not inputs: the snapshot fields are guarded
    with pytest.raises(UserError, match=GUARD):
        rec.input_ids[0].with_user(m.qm).write({"summary": "Everything is fine"})
    with pytest.raises(UserError, match=GUARD), env.cr.savepoint():
        env["fix.qms.review.input"].with_user(m.qm).create(
            {
                "review_id": rec.id,
                "kind": "audit_results",
                "summary": "No findings (self-declared)",
                "source_count": 0,
            }
        )
    # pulling again refreshes the same six lines — no duplicates. Age the
    # stamps first so the refresh really rewrites them: a re-pull inside the
    # same second changed nothing, which hid that the Quality Manager's own
    # refresh was refused by the guard.
    stale = fields.Datetime.subtract(fields.Datetime.now(), hours=1)
    rec.input_ids.sudo().write({"pulled_on": stale})
    rec.with_user(m.qm).action_pull_inputs()
    assert len(rec.input_ids) == 12
    assert all(i.pulled_on > stale for i in rec.input_ids)


def test_the_window_is_since_the_previous_review(m):
    env = m.env
    first = _review(
        env, name="P16 first", review_date=fields.Date.add(fields.Date.today(), days=-10)
    )
    first.action_ids = [(0, 0, {"name": "Retrain the front desk", "owner_id": m.owner_emp.id})]
    later = _review(env, name="P16 second")
    later.with_user(m.qm).action_pull_inputs()
    prior = later.input_ids.filtered(lambda i: i.kind == "prior_actions")
    assert "1 tracked action(s) from 1 earlier review(s); 1 still open" in prior.summary


# ------------------------------------------------------------- holding it
def test_holding_requires_a_chairperson_and_the_complete_set(m):
    env = m.env
    rec = _review(env, review_date=fields.Date.context_today(env["res.partner"]))
    with pytest.raises(UserError, match="Only the Quality Manager"):
        rec.with_user(m.clerk).action_hold()
    rec.chairperson_id = m.tier5_emp.id
    with pytest.raises(UserError, match=r"Pull the inputs of .* first — missing"):
        rec.with_user(m.qm).action_hold()
    rec.with_user(m.qm).action_pull_inputs()
    rec.chairperson_id = False
    with pytest.raises(UserError, match="Name the chairperson"):
        rec.with_user(m.qm).action_hold()
    rec.chairperson_id = m.tier5_emp.id
    rec.with_user(m.qm).action_hold()
    assert rec.state == "held"
    with pytest.raises(UserError, match="hold a review that is scheduled"):
        rec.with_user(m.qm).action_hold()


# ------------------------------------------------------------- the outputs
def test_outputs_are_tracked_actions_completed_by_owner_or_qm(m):
    env = m.env
    rec = _review(env, review_date=fields.Date.context_today(env["res.partner"]))
    rec.chairperson_id = m.tier5_emp.id
    rec.with_user(m.qm).action_pull_inputs()
    rec.with_user(m.qm).action_hold()
    line = env["fix.qms.review.action"].create(
        {
            "review_id": rec.id,
            "name": "Raise the calibration budget",
            "owner_id": m.owner_emp.id,
            "due_on": fields.Date.today(),
        }
    )
    assert rec.open_actions == 1
    # completion belongs to the owner (or the QM) — not whoever is logged in
    with pytest.raises(UserError, match="completed by its owner"):
        line.with_user(m.clerk).action_done()
    line.with_user(m.qm).write({"name": "Raise the calibration budget (FY27)"})
    line.with_user(m.owner).action_done(note="Budget approved")
    assert (line.state, line.done_on, line.done_by_id) == (
        "done",
        fields.Date.context_today(line),
        m.owner_emp,
    )
    rec.invalidate_recordset()
    assert rec.open_actions == 0
    with pytest.raises(UserError, match=GUARD):
        line.with_user(m.qm).write({"state": "open"})


def test_a_decision_only_as_prose_tracks_nothing(m):
    env = m.env
    rec = _review(env, review_date=fields.Date.context_today(env["res.partner"]))
    rec.chairperson_id = m.tier5_emp.id
    rec.with_user(m.qm).action_pull_inputs()
    rec.with_user(m.qm).action_hold()
    # decisions with no tracked line behind them
    rec.decisions = "The QMS is effective. No actions needed."
    with pytest.raises(UserError, match="only as prose"):
        rec.with_user(m.qm).action_close()
    # and an empty review closes nothing either
    rec.decisions = ""
    with pytest.raises(UserError, match="has outputs"):
        rec.with_user(m.qm).action_close()


# ------------------------------------------------------- the routed closure
def test_the_closure_is_top_managements_routed_decision(m):
    env = m.env
    _tier5_only(env, m.tier5)
    rec = _review(env, review_date=fields.Date.context_today(env["res.partner"]))
    rec.chairperson_id = m.tier5_emp.id
    rec.with_user(m.qm).action_pull_inputs()
    rec.with_user(m.qm).action_hold()
    rec.decisions = "Calibration budget raised; CoPQ trend reviewed."
    rec.action_ids = [(0, 0, {"name": "Raise the calibration budget", "owner_id": m.owner_emp.id})]
    # the QM's press does NOT close — it asks top management
    rec.with_user(m.qm).action_close(justification="Outputs tracked; ready to close")
    assert rec.state == "held" and not rec.closed_by_id
    assert rec.approval_state == "pending"
    req = rec.approval_request_id
    assert req.justification == "Outputs tracked; ready to close"
    assert req.decision_domain == "qms_review_closure"
    # the deciding task is in Tier 5's inbox, not the QM's
    Task = env["fix.workflow.task"].sudo()
    task = Task.search([("res_model", "=", "fix.qms.review"), ("res_id", "=", rec.id)])
    assert task.assigned_user_id == m.tier5 and task.state == "pending"
    assert not Task.search(
        [
            ("res_model", "=", "fix.qms.review"),
            ("res_id", "=", rec.id),
            ("assigned_user_id", "=", m.qm.id),
        ]
    )
    # the decision applies the closure and stamps the APPROVER
    task.with_user(m.tier5).action_approve(comment="Approved at the board review")
    assert rec.state == "closed"
    assert rec.closed_by_id == m.tier5_emp and rec.closed_by_id != m.qm_emp
    assert rec.approval_state == "approved"
    # a closed review does not reopen — not by typing, not by the action
    with pytest.raises(UserError, match=GUARD):
        rec.with_user(m.qm).write({"state": "scheduled"})
    with pytest.raises(UserError, match="does not reopen"):
        rec.with_user(m.qm).action_close()
    # a direct press by the QM is the engine's job, never a second closure
    _review2 = _review(env, name="P16 no-forge")
    with pytest.raises(UserError, match="Hold"):
        _review2.with_user(m.qm).action_close()
    # the engine's apply path is never pressed directly — not even by the QM
    with pytest.raises(UserError, match="approver's inbox"):
        _review2.with_user(m.qm).action_apply_closure()


def test_no_one_closes_their_own_review(m):
    env = m.env
    # a dual-hatted Quality Manager holding Tier 5 is still excluded: the
    # engine drops the requester and the creator, and alone there is nobody
    # left to ask
    dual = _user(env, "dual", [QM_GROUP, TIER_5])
    _tier5_only(env, dual)
    _emp(env, dual, "Dual Hat")
    rec = _review(env, review_date=fields.Date.context_today(env["res.partner"]))
    rec.chairperson_id = m.tier5_emp.id
    rec.with_user(dual).action_pull_inputs()
    rec.with_user(dual).action_hold()
    rec.action_ids = [(0, 0, {"name": "Approve the audit plan", "owner_id": m.owner_emp.id})]
    with pytest.raises(UserError, match="No one can approve"):
        rec.with_user(dual).action_close()
    assert rec.state == "held" and rec.approval_state != "approved"


def test_moving_what_was_reviewed_voids_the_pending_closure(m):
    env = m.env
    _tier5_only(env, m.tier5)
    rec = _review(env, review_date=fields.Date.context_today(env["res.partner"]))
    rec.chairperson_id = m.tier5_emp.id
    rec.with_user(m.qm).action_pull_inputs()
    rec.with_user(m.qm).action_hold()
    rec.action_ids = [(0, 0, {"name": "Publish the QMS dashboard", "owner_id": m.owner_emp.id})]
    rec.with_user(m.qm).action_close()
    assert rec.approval_state == "pending"
    # the closure was decided ON this record: rewriting the decisions under
    # the pending request voids it (A11 E4, M63-6)
    rec.with_user(m.qm).write({"decisions": "Rewritten after the fact"})
    assert rec.approval_state != "pending"
    assert rec.approval_request_id.state == "voided"
    assert rec.state == "held"


# ------------------------------------------------------------- the pack
def test_the_management_review_pack_reads_the_record(m):
    from odoo.addons.cd_p03_portal.controllers.a10 import m23

    env = m.env
    rec = _review(
        env, name="P16 pack review", review_date=fields.Date.context_today(env["res.partner"])
    )
    rec.chairperson_id = m.tier5_emp.id
    rec.action_ids = [(0, 0, {"name": "Staff the calibration cell", "owner_id": m.owner_emp.id})]
    out = m23.management_review_pack(env)
    rows = {(r["section"], r["metric"]): r for r in out["rows"]}
    inputs = rows[("Review", "ISO 9.3.2 inputs pulled")]
    actions = rows[("Review", "Tracked actions open (9.3.3)")]
    assert inputs["value"] == 0 and "12 required kind(s) missing" in inputs["detail"]
    assert actions["value"] == 1 and "of 1 action line(s)" in actions["detail"]
    rec.with_user(m.qm).action_pull_inputs()
    out = m23.management_review_pack(env)
    rows = {(r["section"], r["metric"]): r for r in out["rows"]}
    assert rows[("Review", "ISO 9.3.2 inputs pulled")]["value"] == 12
    assert "0 required kind(s) missing" in rows[("Review", "ISO 9.3.2 inputs pulled")]["detail"]
