# A11 audit, module M26 AI/ML Services (cd_ml_services, controllers/a11/m26.py,
# fix.predictive.maintenance from cd_stream_registry, and the M07 consumer of LEAD_SCORE_V1).
#
# Convention (A05 style): PASS = CONTROL HELD; FAIL = GAP (the message names it).
# Tests named `_ref_` are REFERENCE runs (admin, the only role the ACL lets write the
# governance models, or a correctness baseline) and are counted separately.
# Everything runs inside the rolled-back `odoo_env`. Attacks run as NON-ADMIN users
# created in the transaction (base.group_user + one operating unit). Investigation only.
import json
import types

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)

_PGTYPE = {
    "char": "varchar",
    "selection": "varchar",
    "text": "text",
    "html": "text",
    "integer": "int4",
    "many2one": "int4",
    "boolean": "bool",
    "float": "numeric",
    "monetary": "numeric",
    "date": "date",
    "datetime": "timestamp",
    "json": "jsonb",
}


def heal_schema(env, models):
    """Columns added by other sessions' uncommitted work outside A11 (not yet in fix_test_a11c) are
    created INSIDE the test transaction (DDL is transactional; the rollback removes them)."""
    added = []
    for name in models:
        M = env[name]
        env.cr.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name=%s", (M._table,)
        )
        have = {r[0] for r in env.cr.fetchall()}
        for fname, f in M._fields.items():
            if f.store and f.column_type and fname not in have and f.type in _PGTYPE:
                env.cr.execute(
                    'ALTER TABLE "%s" ADD COLUMN "%s" %s' % (M._table, fname, _PGTYPE[f.type])
                )
                added.append("%s.%s" % (M._table, fname))
    if added:
        print("SCHEMA_HEAL (rolled back):", added)
    return added


class Ctx:
    pass


def _user(env, login, ou, company, extra=()):
    groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in extra]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, groups)],
                "company_id": company.id,
                "company_ids": [(6, 0, company.ids)],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = Ctx()
    x.env = env
    heal_schema(
        env,
        [
            "crm.lead",
            "fix.equipment",
            "fix.predictive.maintenance",
            "res.partner",
            "res.users",
            "operating.unit",
            "res.company",
            "fix.ml.inference.run",
        ],
    )
    x.co = env.company
    x.ou_a = env["operating.unit"].search([("company_id", "=", x.co.id)], limit=1)
    x.ou_b = env["operating.unit"].create(
        {
            "name": "A11 M26 OU B",
            "code": "A11M26B",
            "company_id": x.co.id,
            "partner_id": x.co.partner_id.id,
        }
    )
    x.co_b = env["res.company"].create({"name": "A11 M26 Company B"})
    x.clerk = _user(env, "a11m26_clerk", x.ou_a, x.co)
    x.clerk2 = _user(env, "a11m26_clerk2", x.ou_a, x.co)
    x.lead_model = env.ref("cd_ml_services.ml_model_lead_scoring")
    x.fault = env.ref("cd_ml_services.ml_model_fault_classifier")
    x.pdm = env.ref("cd_ml_services.ml_model_predictive_maintenance")
    x.dispatch = env.ref("cd_ml_services.ml_model_dispatch_scoring")
    return x


def run(c, user, model, **kw):
    vals = {"model_id": model.id}
    vals.update(kw)
    return c.env["fix.ml.inference.run"].with_user(user).create(vals)


def m26():
    import odoo.addons.cd_p03_portal.controllers.a11.m26 as mod

    return mod


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()

    def raw(fn):
        return getattr(fn, "original_endpoint", fn)

    req = types.SimpleNamespace(env=c.env(user=c.clerk.id))
    old = (getattr(g, "request", None), getattr(s, "request", None))
    g.request = s.request = req
    try:
        yield types.SimpleNamespace(
            write=lambda **kw: raw(g.P03GenericApiController.model_write)(ctl, **kw),
            action=lambda **kw: raw(g.P03GenericApiController.model_action)(ctl, **kw),
            records=lambda **kw: raw(g.P03GenericApiController.model_records)(ctl, **kw),
        )
    finally:
        g.request, s.request = old


def _version(c, **kw):
    vals = {"model_id": c.lead_model.id, "version": "9.9.9"}
    vals.update(kw)
    return c.env["fix.ml.model.version"].create(vals)


def _ml_user(c, login, group_xmlid):
    """An M26 hat holder (G7): scientist registers, reviewer signs gates,
    owner decides promotions — none of them admin."""
    return _user(c.env, login, c.ou_a, c.co, extra=(group_xmlid,))


# ====================================================================== promotion / evaluation gate
def test_m26_v01_clerk_cannot_create_deployed_version(c):
    """Attack (b): plain user registers a version born deployed. The born-draft
    guard (G7/M26-1) refuses the injected state itself — the refusal precedes
    the ACL — and a plain draft registration is still the ACL's to refuse."""
    with pytest.raises(REFUSED, match="created as a DRAFT"):
        c.env["fix.ml.model.version"].with_user(c.clerk).create(
            {
                "model_id": c.lead_model.id,
                "version": "6.6.6",
                "state": "deployed",
                "deployment_mode": "online",
            }
        )
    with pytest.raises(AccessError):
        c.env["fix.ml.model.version"].with_user(c.clerk).create(
            {"model_id": c.lead_model.id, "version": "6.6.7"}
        )


def test_m26_v02_clerk_cannot_promote_by_write(c):
    v = _version(c)
    with pytest.raises(REFUSED, match="lifecycle actions"):
        v.with_user(c.clerk).write({"state": "deployed"})
    assert v.state == "draft"


def test_m26_v03_clerk_cannot_promote_p03(c, p03):
    v = _version(c)
    out = p03.write(model="fix.ml.model.version", record_id=v.id, values={"state": "deployed"})
    assert "error" in out and v.state == "draft", "GAP: clerk promoted via P03: %s" % out


def test_m26_v04_ref_promotion_requires_passed_gates(c):
    """REFERENCE (admin — the only role with write): a version whose bias gate FAILED and whose
    bias_status is 'failed' is written straight to deployed. Safe: refused (BRU-AIM-13 / §8.1)."""
    admin = c.env.ref("base.user_admin")
    v = _version(c, bias_status="failed")
    c.env["fix.ml.evaluation.gate"].create({"version_id": v.id, "gate": "bias", "result": "failed"})
    c.env["fix.ml.evaluation.gate"].create(
        {"version_id": v.id, "gate": "accuracy", "result": "failed"}
    )
    try:
        v.with_user(admin).write({"state": "deployed", "deployment_mode": "online"})
    except REFUSED:
        return
    pytest.fail(
        "GAP (reference): version %s went draft -> deployed in one write with 2 FAILED gates and "
        "bias_status=failed; approved_by=%s, deployed_at=%s (nothing stamps them); no evaluated/approved "
        "step, no transition method exists" % (v.name, v.approved_by.name, v.deployed_at)
    )


def test_m26_v05_ref_four_eyes_on_promotion(c):
    """REFERENCE (G7): promotion is four-eyed end to end — the registrant cannot
    sign their own gates, state is not typeable, and the deploy lands only from
    the M63 inbox of a Model Owner who is not the registrant."""
    sci = _ml_user(c, "a11m26_sci", "cd_ml_services.group_ml_data_scientist")
    rev = _ml_user(c, "a11m26_rev", "cd_ml_services.group_ml_reviewer")
    own = _ml_user(c, "a11m26_own", "cd_ml_services.group_ml_model_owner")
    V = c.env["fix.ml.model.version"]
    v = V.with_user(sci).create(
        {
            "model_id": c.lead_model.id,
            "version": "7.0.0",
            "model_card": "probe card",
            "metrics_json": '{"latency_ms_p95": 42}',
            "bias_status": "passed",
        }
    )
    # (a) the registrant never signs their own gates — even wearing both hats
    with pytest.raises(REFUSED, match="cannot record"):
        c.env["fix.ml.evaluation.gate"].with_user(sci).create(
            {"version_id": v.id, "gate": "accuracy", "result": "passed"}
        )
    # (b) the gates are a different reviewer's evidence
    for gate in ("accuracy", "bias", "explainability"):
        c.env["fix.ml.evaluation.gate"].with_user(rev).create(
            {"version_id": v.id, "gate": gate, "result": "passed"}
        )
    # (c) state stays untypeable for the registrant
    with pytest.raises(REFUSED, match="lifecycle actions"):
        v.with_user(sci).write({"state": "deployed"})
    # (d) the routed request is decided by another Model Owner from the inbox
    v.with_user(sci).action_request_promotion(justification="probe promotion")
    task = v.approval_request_id.task_ids.filtered(
        lambda t: t.assigned_user_id == own and t.state == "pending"
    )
    assert task, "no pending M63 task reached the Model Owner"
    assert not v.approval_request_id.task_ids.filtered(
        lambda t: t.assigned_user_id == sci
    ), "the registrant must not hold their own task"
    task.with_user(own).action_approve(comment="gates hold")
    v.invalidate_recordset()
    assert v.state == "deployed" and v.deployed_at
    assert v.approved_by == own and v.approved_by != v.create_uid


def test_m26_v06_gate_result_must_be_stated(c):
    """Decorative default: an evaluation gate recorded without a result."""
    v = _version(c)
    g = c.env["fix.ml.evaluation.gate"].create({"version_id": v.id, "gate": "bias"})
    assert g.result != "passed", (
        "GAP: a gate created with no result is recorded as result=%r (field default 'passed'); "
        "metrics_json is free text and nothing compares it to a target" % g.result
    )


def test_m26_v07_ref_gate_reviewer_not_forgeable(c):
    """REFERENCE (admin): checked_by (readonly in the view) is set to another user via ORM."""
    admin = c.env.ref("base.user_admin")
    v = _version(c)
    g = (
        c.env["fix.ml.evaluation.gate"]
        .with_user(admin)
        .create({"version_id": v.id, "gate": "bias", "result": "passed", "checked_by": c.clerk2.id})
    )
    assert g.checked_by != c.clerk2, (
        "GAP (reference): gate %s records checked_by=%s although %s created it (reviewer forgeable)"
        % (g.id, g.checked_by.login, admin.login)
    )


def test_m26_v08_serving_honours_version_state(c):
    """The engine serves only a DEPLOYED version (G7). The seeded baseline is
    retired (an Owner act), the only other version is retired with a failed
    bias gate and the model itself reads 'planned'. Clerk executes.
    Safe: refused outright — no engine runs on an unpromoted model."""
    c.env.ref("cd_ml_services.ml_version_lead_scoring_v1").action_retire()
    v = _version(c, state="retired", bias_status="failed")
    c.env["fix.ml.evaluation.gate"].create({"version_id": v.id, "gate": "bias", "result": "failed"})
    c.lead_model.write({"status": "planned"})
    assert (
        not c.lead_model.serving_version_id
    ), "a retired-only registry must resolve no serving version"
    lead = c.env["crm.lead"].create(
        {"name": "A11 lead", "type": "opportunity", "expected_revenue": 10}
    )
    r = run(c, c.clerk, c.lead_model, input_text=json.dumps({"lead_id": lead.id}))
    with pytest.raises(REFUSED, match="no DEPLOYED version"):
        r.with_user(c.clerk).action_execute()
    assert r.state == "draft", "the refusal must not forge a run outcome"


def test_m26_v09_m07_consumer_honours_version_state(c):
    """Hand-off: M07 action_score through the M26 seam on the same retired-only
    model. Safe: M07 reports the ABSENCE of a score (m26_unavailable / unscored)
    — never a number dressed as an engine prediction."""
    c.env.ref("cd_ml_services.ml_version_lead_scoring_v1").action_retire()
    lead = c.env["crm.lead"].create(
        {
            "name": "A11 lead2",
            "type": "opportunity",
            "expected_revenue": 600000,
            "partner_name": "Acme",
        }
    )
    lead.with_user(c.clerk).action_score()
    assert lead.lead_score_basis != "m26_model", (
        "GAP: M07 scored lead %s=%s (%s) as '%s' through LEAD_SCORE_V1 with no deployed version"
        % (
            lead.id,
            lead.lead_score,
            lead.lead_score_band,
            dict(lead._fields["lead_score_basis"].selection).get(lead.lead_score_basis),
        )
    )
    assert lead.lead_score_basis == "m26_unavailable" and lead.lead_score_band == "unscored"


# ====================================================================== guardrails
def test_m26_g01_clerk_cannot_disable_guardrail_orm(c):
    g = c.env["fix.ml.guardrail"].create(
        {"name": "g", "model_id": c.fault.id, "rule": "score >= 1", "action": "block"}
    )
    with pytest.raises(AccessError):
        g.with_user(c.clerk).write({"active": False})


def test_m26_g02_clerk_cannot_disable_guardrail_p03(c, p03):
    g = c.env["fix.ml.guardrail"].create(
        {"name": "g", "model_id": c.fault.id, "rule": "score >= 1", "action": "block"}
    )
    out = p03.write(model="fix.ml.guardrail", record_id=g.id, values={"active": False})
    assert "error" in out and g.active, "GAP: clerk switched a guardrail off via P03: %s" % out


def test_m26_g03_block_guardrail_is_enforced(c):
    """An active BLOCK guardrail on the fault classifier (every output with score >= 1). Safe: the
    run does not return the blocked output (blocked / flagged / fallback)."""
    c.env["fix.ml.guardrail"].create(
        {
            "name": "block all",
            "model_id": c.fault.id,
            "rule": "score >= 1",
            "threshold": 1,
            "action": "block",
        }
    )
    r = run(c, c.clerk, c.fault, input_text="phone not charging battery dead")
    r.with_user(c.clerk).action_execute()
    out = json.loads(r.output_json or "[]")
    assert not (r.state == "computed" and out), (
        "GAP: BLOCK guardrail ignored — run %s computed %d suggestions (top %s score %s); no engine reads "
        "fix.ml.guardrail (only the fallback_status report counts them)"
        % (r.id, len(out), out[0]["fault_code"] if out else None, out[0]["score"] if out else None)
    )


# ====================================================================== decision log immutability
def test_m26_r01_clerk_cannot_create_computed_run_with_output(c):
    """Attack (b): a run born computed, with a fabricated output and latency (JSON-RPC create)."""
    try:
        r = run(
            c,
            c.clerk,
            c.lead_model,
            state="computed",
            latency_ms=3,
            output_json=json.dumps({"score": 99, "band": "hot"}),
            suggested_value="hot",
        )
    except REFUSED:
        return
    assert r.state != "computed" or not r.output_json, (
        "GAP: clerk created inference run %s already 'computed' with output %s — the decision log "
        "accepts fabricated entries" % (r.id, r.output_json)
    )


def test_m26_r02_clerk_cannot_rewrite_output_of_computed_run(c):
    r = run(c, c.clerk, c.fault, input_text="screen cracked broken panel")
    r.action_execute()
    original = r.output_json
    try:
        r.with_user(c.clerk2).write(
            {"output_json": '[{"fault_code": "FAKE-99", "score": 9}]', "latency_ms": 1}
        )
    except REFUSED:
        return
    assert r.output_json == original, (
        "GAP: clerk2 rewrote the output of computed run %s (now %s)" % (r.id, r.output_json)
    )


def test_m26_r03_clerk_cannot_forge_who_and_when(c):
    r = run(c, c.clerk, c.fault, input_text="screen cracked")
    r.action_execute()
    try:
        r.with_user(c.clerk).write({"ran_by": c.clerk2.id, "ran_at": "2026-01-01 00:00:00"})
    except REFUSED:
        return
    assert r.ran_by == c.clerk, "GAP: run %s re-attributed to %s and back-dated to %s" % (
        r.id,
        r.ran_by.login,
        r.ran_at,
    )


def test_m26_r04_clerk_cannot_set_state_via_p03(c, p03):
    """Attack (c): a draft run marked computed through the form endpoint (state is not readonly)."""
    r = run(c, c.clerk, c.fault, input_text="x")
    out = p03.write(model="fix.ml.inference.run", record_id=r.id, values={"state": "computed"})
    assert r.state == "draft", (
        "GAP: P03 marked draft run %s 'computed' with no engine output (%s)" % (r.id, out)
    )


def test_m26_r05_clerk_cannot_reassign_model_of_computed_run(c):
    r = run(c, c.clerk, c.fault, input_text="screen cracked")
    r.action_execute()
    try:
        r.with_user(c.clerk).write({"model_id": c.lead_model.id})
    except REFUSED:
        return
    assert r.model_id == c.fault, "GAP: computed run %s now attributed to %s" % (r.id, r.model_code)


def test_m26_r06_reexecute_keeps_history(c):
    """A computed run is the decision log: its input is not editable (G7/R01)
    — the way to score a changed input is a NEW run, which leaves the first
    output intact beside it."""
    r = run(c, c.clerk, c.fault, input_text="screen cracked broken panel")
    r.action_execute()
    first = r.output_json
    with pytest.raises(REFUSED, match="decision log"):
        r.with_user(c.clerk).write({"input_text": "no power no boot"})
    r2 = run(c, c.clerk, c.fault, input_text="no power no boot")
    r2.with_user(c.clerk).action_execute()
    assert r.output_json == first, "the first run's output must never move"
    assert r2.state == "computed" and r2.output_json != first


def test_m26_r07_clerk_cannot_delete_run(c):
    r = run(c, c.clerk, c.fault, input_text="x")
    with pytest.raises(REFUSED, match="cannot be deleted"):
        r.with_user(c.clerk).unlink()
    assert c.env["fix.ml.inference.run"].search_count([("id", "=", r.id)]) == 1


def test_m26_r08_engine_records_its_suggestion(c):
    """HITL wiring (G7): the engine derives its suggestion from the OUTPUT —
    for the lead model (a dict output) it is the score, as a string."""
    lead = c.env["crm.lead"].create(
        {
            "name": "A11 r08 lead",
            "type": "opportunity",
            "expected_revenue": 600000,
            "partner_name": "Acme",
        }
    )
    r = run(c, c.clerk, c.lead_model, input_text=json.dumps({"lead_id": lead.id}))
    r.with_user(c.clerk).action_execute()
    assert r.state == "computed", "reference path must compute: %s" % r.error_note
    out = json.loads(r.output_json or "{}")
    assert r.suggested_value == str(out["score"]), (
        "GAP (wiring): engine suggestion %r != output score %r — Override Analysis and the override_rate "
        "KPI cannot be compared against typed decisions" % (r.suggested_value, out.get("score"))
    )


def test_m26_r09_override_kpi_not_forgeable(c):
    """Attack (b): clerk types suggestion/decision/override on 4 runs; the M26 'Override Rate' KPI moves."""
    before = m26()._ml_kpis(c.env)["override_rate"]
    for i in range(4):
        r = run(c, c.clerk, c.dispatch, input_text="x%d" % i)
        try:
            r.with_user(c.clerk).write(
                {
                    "suggested_value": "tech-A",
                    "final_value": "tech-B",
                    "overridden": True,
                    "override_reason": "typed",
                }
            )
        except REFUSED:
            return
    after = m26()._ml_kpis(c.env)["override_rate"]
    assert after == before, (
        "GAP: override_rate KPI %s -> %s%% from 4 never-executed runs whose engine suggestion was typed by "
        "the clerk (suggested_value is readonly only in the view)" % (before, after)
    )


def test_m26_r10_overridden_is_derived(c):
    """Decorative flag (G7): `overridden` is DERIVED from final vs suggested —
    typing it is refused, and it flips by itself when the two disagree."""
    r = run(c, c.clerk, c.fault, input_text="x")
    r.action_execute()
    r.sudo().write({"suggested_value": "DSP-01"})
    with pytest.raises(REFUSED, match="decision log"):
        r.with_user(c.clerk).write({"final_value": "DSP-01", "overridden": True})
    r.with_user(c.clerk).write({"final_value": "DSP-01"})
    assert not r.overridden, "final == suggested must read as NOT overridden"
    r.with_user(c.clerk).write({"final_value": "OTHER-9"})
    assert r.overridden, "final != suggested must read as overridden"


# ====================================================================== cross-entity leakage
def test_m26_x01_lead_scoring_respects_company(c):
    """Attack: clerk (company A) runs LEAD_SCORE_V1 on a company-B lead id."""
    lead_b = c.env["crm.lead"].create(
        {
            "name": "A11 secret CoB deal",
            "type": "opportunity",
            "company_id": c.co_b.id,
            "expected_revenue": 987654,
        }
    )
    assert not c.env(user=c.clerk.id)["crm.lead"].search_count([("id", "=", lead_b.id)])
    r = run(c, c.clerk, c.lead_model, input_text=json.dumps({"lead_id": lead_b.id}))
    r.with_user(c.clerk).action_execute()
    out = json.loads(r.output_json or "{}")
    assert out.get("expected_revenue") is None, (
        "GAP: company-A clerk read company-B lead %s via M26: expected_revenue=%s, age_days=%s, factors=%s"
        % (
            lead_b.id,
            out.get("expected_revenue"),
            out.get("age_days"),
            [f["factor"] for f in out.get("factors", [])],
        )
    )


def test_m26_x02_pdm_engine_respects_scope(c):
    """Attack: a company-B equipment's failure prediction; clerk (company A) runs the PdM 'engine'."""
    eq = c.env["fix.equipment"].create(
        {"name": "CoB secret chiller", "code": "A11EQB", "company_id": c.co_b.id}
    )
    c.env["fix.predictive.maintenance"].create(
        {
            "name": "CoB pred",
            "equipment_id": eq.id,
            "company_id": c.co_b.id,
            "prediction": "failure_predicted",
            "confidence": 0.9,
            "estimated_days_to_failure": 3,
        }
    )
    r = run(c, c.clerk, c.pdm)
    r.with_user(c.clerk).action_execute()
    assert "CoB secret chiller" not in (r.output_json or ""), (
        "GAP: company-A clerk's PdM inference lists company-B equipment: %s"
        % (r.output_json or "")[:300]
    )


def test_m26_x03_pdm_list_respects_operating_unit(c, p03):
    """Attack (c): /p03/model/records on fix.predictive.maintenance; a prediction of OU B."""
    eq = c.env["fix.equipment"].create({"name": "OU-B compressor", "code": "A11EQOB"})
    p = c.env["fix.predictive.maintenance"].create(
        {
            "name": "OUB pred",
            "equipment_id": eq.id,
            "operating_unit_id": c.ou_b.id,
            "prediction": "degrading",
        }
    )
    own = c.env(user=c.clerk.id)["fix.predictive.maintenance"].search_count([("id", "=", p.id)])
    out = p03.records(model="fix.predictive.maintenance", cols=["name", "operating_unit_id"])
    ids = [r["id"] for r in out.get("rows", [])]
    assert own or p.id not in ids, (
        "GAP: OU-A clerk's record rules hide prediction %s (search_count=%d) but the M26 screen lists it "
        "(model_records reads sudo + company only)" % (p.id, own)
    )


def test_m26_x04_models_live_kpi_company_scoped(c):
    before = m26()._ml_kpis(c.env(user=c.clerk.id))["models_live"]
    c.env["fix.ml.model"].create(
        {
            "name": "CoB model",
            "code": "cob.x",
            "kind": "fault_classifier",
            "company_id": c.co_b.id,
            "status": "production",
        }
    )
    after = m26()._ml_kpis(c.env(user=c.clerk.id))["models_live"]
    assert after == before, (
        "GAP: company-B model counted in company A's 'Models Live' (%s -> %s)" % (before, after)
    )


# ====================================================================== predictions provenance / decisions
def test_m26_p01_prediction_must_come_from_a_model(c):
    """Attack (b): clerk types a 'failure_predicted' at 0.99 attributed to a model that does not exist,
    then raises the preventive work order from it."""
    eq = c.env["fix.equipment"].create({"name": "A11 pump", "code": "A11EQP"})
    try:
        p = (
            c.env["fix.predictive.maintenance"]
            .with_user(c.clerk)
            .create(
                {
                    "name": "typed",
                    "equipment_id": eq.id,
                    "prediction": "failure_predicted",
                    "confidence": 0.99,
                    "estimated_days_to_failure": 1,
                    "model_name": "m26-pdm-v9",
                    "operating_unit_id": c.ou_a.id,
                }
            )
        )
        p.with_user(c.clerk).action_create_preventive_wo()
    except REFUSED:
        return
    known = c.env["fix.ml.model"].search_count([("code", "=", "m26-pdm-v9")])
    pytest.fail(
        "GAP: clerk typed prediction %s (failure_predicted, 0.99, model 'm26-pdm-v9' — %d such models) with no "
        "inference run behind it and raised the preventive WO flag=%s"
        % (p.id, known, p.work_order_created)
    )


def test_m26_p02_prediction_not_editable_after_the_fact(c):
    """P02: the output half of a recorded prediction (prediction, confidence,
    window, model name) is engine-owned. A changed write is refused outright —
    a re-assessment records a NEW prediction row; only the engine (superuser
    code) rewrites an output."""
    eq = c.env["fix.equipment"].create({"name": "A11 pump2", "code": "A11EQP2"})
    p = c.env["fix.predictive.maintenance"].create(
        {
            "name": "p",
            "equipment_id": eq.id,
            "prediction": "healthy",
            "confidence": 0.95,
            "operating_unit_id": c.ou_a.id,
        }
    )
    with pytest.raises(REFUSED, match="cannot be set directly"):
        p.with_user(c.clerk).write({"prediction": "failure_predicted", "confidence": 0.2})
    p.invalidate_recordset()
    assert p.prediction == "healthy" and p.confidence == 0.95
    p.sudo().write({"confidence": 0.9})  # the engine's own channel still moves
    assert p.confidence == 0.9


def test_m26_p03_low_confidence_prediction_abstains(c):
    """BRU-AIM-25: a model below its confidence threshold abstains. A 0.05-confidence failure prediction
    raising a preventive WO."""
    eq = c.env["fix.equipment"].create({"name": "A11 pump3", "code": "A11EQP3"})
    p = c.env["fix.predictive.maintenance"].create(
        {
            "name": "p",
            "equipment_id": eq.id,
            "prediction": "failure_predicted",
            "confidence": 0.05,
            "operating_unit_id": c.ou_a.id,
        }
    )
    try:
        p.with_user(c.clerk).action_create_preventive_wo()
    except REFUSED:
        return
    pytest.fail("GAP: preventive WO flag raised from a 5%%-confidence prediction (no threshold)")


def test_m26_a01_automated_scoring_disclosed_honestly(c):
    """Automated decision (E5): the nightly cron re-scores every open lead through
    LEAD_SCORE_V1 with no human. The engine is honestly rule_based — the label and
    the reasons must SAY so, never dress a hand-weighted rule as a prediction."""
    lead = c.env["crm.lead"].create(
        {
            "name": "A11 cron lead",
            "type": "opportunity",
            "expected_revenue": 600000,
            "partner_name": "Acme",
        }
    )
    c.env["crm.lead"].cron_rescore_open_leads(limit=50)
    lead.invalidate_recordset()
    label = dict(lead._fields["lead_score_basis"].selection).get(lead.lead_score_basis, "")
    assert lead.lead_score_basis == "m26_model" and c.lead_model.implementation == "rule_based"
    assert "deterministic" in label and "prediction" not in label.lower(), (
        "GAP (disclosure): label %r hides what produced the score" % label
    )
    assert "not a fitted prediction" in (lead.lead_score_reasons or ""), (
        "GAP (disclosure): reasons %r do not disclose the engine's nature" % lead.lead_score_reasons
    )


def test_m26_a02_ref_lead_weights_change_is_versioned(c):
    """REFERENCE (admin, M26-A02): a weights edit is a MODEL CHANGE — it now
    lands in the immutable fix.ml.weights.revision register (old vector, new
    vector, who, when) instead of changing every score invisibly."""
    admin = c.env.ref("base.user_admin")
    before = c.env["fix.ml.weights.revision"].search_count([("model_id", "=", c.lead_model.id)])
    c.lead_model.with_user(admin).write({"weights_json": json.dumps({"has_contact": 100})})
    revs = c.env["fix.ml.weights.revision"].search([("model_id", "=", c.lead_model.id)])
    assert len(revs) == before + 1, "one weights edit must record exactly one revision"
    top = revs[0]
    assert top.new_json == json.dumps({"has_contact": 100}), top.new_json
    assert top.previous_json in (False, ""), "seeded default lives in code, so no previous vector"
    assert top.changed_by == admin
    with pytest.raises(REFUSED, match="cannot be edited"):
        top.with_user(c.clerk).write({"new_json": "{}"})
    with pytest.raises(REFUSED, match="cannot be deleted"):
        top.with_user(c.clerk).unlink()


def test_m26_b01_bengali_fault_text_classified(c):
    """Bengali: 'ফোন চার্জ হচ্ছে না, ব্যাটারি নষ্ট' (phone not charging, battery dead). Reference: the
    English sentence matches BAT-* codes. Safe: the Bengali sentence matches too."""
    en = run(c, c.clerk, c.fault, input_text="phone not charging battery dead")
    en.action_execute()
    bn = run(c, c.clerk, c.fault, input_text="ফোন চার্জ হচ্ছে না, ব্যাটারি নষ্ট")
    bn.action_execute()
    en_out, bn_out = json.loads(en.output_json or "[]"), json.loads(bn.output_json or "[]")
    assert en_out and not bn_out, (
        "pre-condition: the English sentence classifies (%d rows) but the Bengali taxonomy is empty, "
        "so the seeded estate must return no Bengali match (en=%d, bn=%d)"
        % (len(en_out), len(en_out), len(bn_out))
    )
    # the taxonomy gains a row that carries Bengali text, and the SAME sentence now matches it
    c.env["fix.fault.code"].create(
        {"code": "A11BN", "name": "ফোন চার্জ হচ্ছে না ব্যাটরি নষ্ট", "category": "power"}
    )
    bn2 = run(c, c.clerk, c.fault, input_text="ফোন চার্জ হচ্ছে না, ব্যাটরি নষ্ট")
    bn2.with_user(c.clerk).action_execute()
    bn2_out = json.loads(bn2.output_json or "[]")
    assert any(r["fault_code"] == "A11BN" for r in bn2_out), (
        "GAP: Bengali fault text returns %d matches against a taxonomy row that carries the same words"
        % len(bn2_out)
    )
    # the catalogue row COUNTS the coverage it just proved — never asserts 'Live'
    cat = m26().bengali_nlp_catalog(c.env(user=c.clerk.id))
    row = next(r for r in cat["rows"] if r["surface"] == "Bengali fault-text classification")
    assert "Live" not in row["status"], "the old untrue claim is back: %r" % row["status"]
    assert "1 of" in row["status"], "coverage must be COUNTED: %r" % row["status"]


def test_m26_b02_ref_english_classifier_baseline(c):
    """REFERENCE: the English token-overlap classifier returns a battery code for a battery complaint."""
    r = run(c, c.clerk, c.fault, input_text="phone not charging battery dead")
    r.action_execute()
    out = json.loads(r.output_json or "[]")
    assert out and out[0]["fault_code"].startswith("BAT"), "baseline failed: %s" % out[:2]


def test_m26_f01_fairness_check_is_enforced(c):
    """Decorative no more (G7/BRU-AIM-07): the bias status GATES promotion —
    'untested' blocks a people-affecting model, 'failed' blocks every model —
    and the Fairness Summary reports the status exactly as recorded."""
    sci = _ml_user(c, "a11m26_sci_f01", "cd_ml_services.group_ml_data_scientist")
    rev = _ml_user(c, "a11m26_rev_f01", "cd_ml_services.group_ml_reviewer")
    v = (
        c.env["fix.ml.model.version"]
        .with_user(sci)
        .create(
            {
                "model_id": c.lead_model.id,
                "version": "8.8.8",
                "model_card": "probe card",
                "metrics_json": '{"auc": 0.71}',
            }
        )
    )
    assert v.bias_status == "untested", "a version is born with an HONEST bias status"
    for gate in ("accuracy", "bias", "explainability"):
        c.env["fix.ml.evaluation.gate"].with_user(rev).create(
            {"version_id": v.id, "gate": gate, "result": "passed"}
        )
    # all gates passed, yet lead_scoring affects people: 'untested' is not 'passed'
    with pytest.raises(REFUSED, match="PASSED bias review"):
        v.with_user(sci).action_request_promotion()
    # a FAILED bias review blocks every promotion outright
    v.write({"bias_status": "failed"})
    with pytest.raises(REFUSED, match="failed its bias review"):
        v.with_user(sci).action_request_promotion()
    rows = m26().fairness_summary(c.env(user=c.clerk.id))["rows"]
    row = next(r for r in rows if r["version"] == "8.8.8" and r["model"] == v.model_id.code)
    assert row["bias"] == "failed" and row["state"] == "draft"
