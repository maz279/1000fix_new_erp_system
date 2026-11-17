# M60 capture audit (2026-11-18): the records the sub-module pages now
# capture, exercised against the live ORM as NON-ADMIN users holding only the
# groups each step needs (the superuser is trusted by the field guard and
# would hide a gap). The odoo_env fixture rolls everything back.
import datetime
import itertools
import types

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as g
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

REFUSED = (UserError, AccessError, ValidationError)
GUARD = "changes only through its workflow"
OFFICER = "cd_grc.group_grc_officer"
RISK_OWNER = "cd_grc.group_grc_risk_owner"
LEGAL = "cd_grc.group_grc_legal"

_MW = getattr(g.P03GenericApiController.model_write, "original_endpoint", None) or (
    g.P03GenericApiController.model_write
)
_MA = getattr(g.P03GenericApiController.model_action, "original_endpoint", None) or (
    g.P03GenericApiController.model_action
)
_SEQ = itertools.count(1)


def _user(env, login, groups=(), employee=True):
    n = next(_SEQ)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M60 %s %d" % (login, n),
                "login": "m60cap.%s.%d@m60.test" % (login, n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])
                ],
            }
        )
    )
    assert not user.has_group("base.group_system")
    if employee:
        env["hr.employee"].create({"name": user.name, "user_id": user.id})
    return user


def p03(x, endpoint, user, **kw):
    g.request = types.SimpleNamespace(env=x.env(user=user.id))
    return endpoint(g.P03GenericApiController(), **kw)


@pytest.fixture
def m(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.clerk = _user(env, "clerk")
    x.clerk2 = _user(env, "clerk2")
    x.owner = _user(env, "owner", [RISK_OWNER])
    x.officer = _user(env, "officer", [OFFICER])
    x.officer2 = _user(env, "officer2", [OFFICER])
    x.legal = _user(env, "legal", [LEGAL])
    x.today = fields.Date.context_today(env["res.users"])
    env["fix.risk.appetite"].search([("category", "=", "financial")]).unlink()
    x.risk = env["fix.risk.register"].create(
        {
            "name": "M60 capture: supplier concentration",
            "category": "financial",
            "likelihood": "3",
            "impact": "3",
            "owner_id": x.owner.employee_id.id,
        }
    )
    saved = getattr(g, "request", None)
    yield x
    g.request = saved


def _appetite(m, score=12):
    return m.env["fix.risk.appetite"].create({"category": "financial", "max_residual_score": score})


# ------------------------------------------------------------------ page 1
def test_an_assessment_is_dated_stamped_and_never_overwritten(m):
    Assessment = m.env["fix.risk.assessment"]
    vals = {
        "risk_id": m.risk.id,
        "likelihood": "4",
        "impact": "3",
        "rationale": "Two suppliers carry 70% of parts spend.",
        "next_review_date": m.today + datetime.timedelta(days=90),
    }
    # BRU-GRC-02: no score before the appetite of the category is stated
    with pytest.raises(UserError, match="appetite"):
        Assessment.with_user(m.owner).create(dict(vals))
    _appetite(m)
    # BRU-GRC-01: a plain user does not assess
    with pytest.raises(UserError, match="Risk Owner or a Compliance Officer"):
        Assessment.with_user(m.clerk).create(dict(vals))
    # the stamps are never typed
    with pytest.raises(UserError, match=GUARD):
        Assessment.with_user(m.owner).create(dict(vals, assessed_by_id=m.officer.employee_id.id))
    first = Assessment.with_user(m.owner).create(dict(vals))
    assert first.assessed_by_id == m.owner.employee_id
    assert first.assessed_on == m.today and first.inherent_score == 12
    assert m.risk.likelihood == "4" and m.risk.review_date == vals["next_review_date"]
    second = Assessment.with_user(m.officer).create(
        dict(vals, likelihood="2", residual_likelihood="2", residual_impact="2")
    )
    assert m.risk.risk_score == 6 and m.risk.residual_score == 4
    # T-01: the first assessment is untouched; history is never rewritten
    assert first.likelihood == "4" and first.inherent_score == 12
    assert second.previous_residual == 0
    with pytest.raises(UserError, match="kept as recorded"):
        first.with_user(m.owner).write({"rationale": "rewritten"})
    with pytest.raises(UserError, match="never deleted"):
        first.with_user(m.owner).unlink()


def test_a_treatment_has_an_owner_a_date_and_an_evidenced_completion(m):
    Treatment = m.env["fix.risk.treatment"]
    vals = {
        "name": "Qualify a third parts supplier",
        "risk_id": m.risk.id,
        "strategy": "mitigate",
        "rationale": "Reduce concentration.",
        "owner_id": m.clerk.employee_id.id,
        "due_on": m.today + datetime.timedelta(days=30),
    }
    with pytest.raises(UserError, match="Risk Owner"):
        Treatment.with_user(m.clerk).create(dict(vals))
    with pytest.raises(ValidationError, match="instrument"):
        Treatment.with_user(m.owner).create(dict(vals, strategy="transfer"))
    rec = Treatment.with_user(m.owner).create(dict(vals))
    assert m.risk.state == "mitigating"
    assert rec.activity_ids.user_id == m.clerk
    # someone else neither edits nor completes it
    with pytest.raises(UserError, match="action owner"):
        rec.with_user(m.clerk2).write({"due_on": m.today})
    with pytest.raises(UserError, match="action owner"):
        rec.with_user(m.clerk2).action_complete(note="done")
    with pytest.raises(UserError, match=GUARD):
        rec.with_user(m.clerk).write({"state": "done"})
    with pytest.raises(UserError, match="evidence"):
        rec.with_user(m.clerk).action_complete(note=" ")
    rec.with_user(m.clerk).action_complete(note="Supplier X qualified, file QS-12")
    assert rec.state == "done" and rec.completed_by_id == m.clerk
    with pytest.raises(UserError, match="Compliance Officer"):
        Treatment.with_user(m.owner).create(dict(vals)).action_cancel(reason="no")


def test_a_realised_event_is_kept_as_reported_and_asks_for_reassessment(m):
    event = (
        m.env["fix.risk.event"]
        .with_user(m.clerk)
        .create(
            {
                "name": "Supplier strike delayed 40 repairs",
                "risk_id": m.risk.id,
                "event_type": "loss",
                "loss_amount": 250000,
                "description": "Stock-out for 9 days.",
            }
        )
    )
    assert event.reported_by_id == m.clerk and event.reassessment_due
    assert "Realised loss" in m.risk.message_ids[0].body
    with pytest.raises(UserError, match="kept as recorded"):
        event.with_user(m.clerk).write({"loss_amount": 1})


# ------------------------------------------------------------------ page 4
@pytest.fixture
def obligation(m):
    framework = m.env["fix.compliance.framework"].create({"name": "M60 VAT", "code": "bla_2006"})
    return m.env["fix.compliance.obligation"].create(
        {
            "framework_id": framework.id,
            "name": "Monthly VAT return (Mushak 9.1)",
            "clause_reference": "VAT Act 2012 s.64",
            "owner_id": m.clerk.employee_id.id,
            "recurrence": "monthly",
        }
    )


def test_a_discharge_without_evidence_is_a_control_failure(m, obligation):
    Occ = m.env["fix.compliance.obligation.occurrence"]
    vals = {"obligation_id": obligation.id, "period": "2026-10", "due_on": m.today}
    with pytest.raises(UserError, match="Compliance Officer schedules"):
        Occ.with_user(m.clerk).create(dict(vals))
    occ = Occ.with_user(m.officer).create(dict(vals))
    assert occ.owner_id == m.clerk.employee_id
    with pytest.raises(UserError, match="obligation owner"):
        occ.with_user(m.clerk2).action_discharge()
    occ.with_user(m.clerk).action_discharge()
    assert occ.state == "failed"  # BRU-GRC-12
    with pytest.raises(UserError, match="evidenced discharge"):
        occ.with_user(m.officer).action_verify()


def test_an_evidenced_discharge_is_verified_by_someone_else(m, obligation):
    Occ = m.env["fix.compliance.obligation.occurrence"]
    occ = Occ.with_user(m.officer).create(
        {"obligation_id": obligation.id, "period": "2026-11", "due_on": m.today}
    )
    occ.with_user(m.clerk).write({"evidence_ref": "NBR ack 9.1/2026/11/4471"})
    occ.with_user(m.officer).action_discharge(note="filed online")
    assert occ.state == "discharged" and occ.discharged_by_id == m.officer
    with pytest.raises(UserError, match="does not verify"):
        occ.with_user(m.officer).action_verify()
    with pytest.raises(UserError, match="Compliance Officer"):
        occ.with_user(m.clerk).action_verify()
    occ.with_user(m.officer2).action_verify()
    assert occ.state == "verified" and occ.verified_by_id == m.officer2
    # one occurrence per period
    with pytest.raises(IntegrityError), m.env.cr.savepoint():
        Occ.with_user(m.officer).create(
            {"obligation_id": obligation.id, "period": "2026-11", "due_on": m.today}
        )


def test_a_missed_occurrence_is_recorded_as_a_breach(m, obligation):
    Occ = m.env["fix.compliance.obligation.occurrence"]
    future = Occ.with_user(m.officer).create(
        {
            "obligation_id": obligation.id,
            "period": "2027-01",
            "due_on": m.today + datetime.timedelta(days=10),
        }
    )
    with pytest.raises(UserError, match="not yet due"):
        future.with_user(m.officer).action_record_breach(reason="late")
    past = Occ.with_user(m.officer).create(
        {
            "obligation_id": obligation.id,
            "period": "2026-09",
            "due_on": m.today - datetime.timedelta(days=5),
        }
    )
    assert past.overdue
    with pytest.raises(UserError, match="consequence"):
        past.with_user(m.officer).action_record_breach(reason="")
    past.with_user(m.officer).action_record_breach(reason="Penalty 5,000 BDT; CFO told.")
    assert past.state == "breached"


def test_a_regulatory_change_is_assessed_by_the_officer(m, obligation):
    change = (
        m.env["fix.grc.regulatory.change"]
        .with_user(m.officer)
        .create(
            {
                "name": "SRO 2026 VAT rate change",
                "source": "NBR SRO",
                "effective_on": m.today,
                "description": "Standard rate unchanged; reduced rate list amended.",
                "obligation_ids": [(4, obligation.id)],
            }
        )
    )
    with pytest.raises(REFUSED):
        change.with_user(m.clerk).action_assess(impact="none")
    with pytest.raises(UserError, match="impact"):
        change.with_user(m.officer).action_assess(impact=" ")
    change.with_user(m.officer).action_assess(impact="Mushak 9.1 template updated.")
    assert change.state == "assessed" and change.assessed_by_id == m.officer


# ------------------------------------------------------------------ page 5
@pytest.fixture
def policy(m):
    return m.env["fix.grc.policy"].create(
        {
            "name": "M60 Acceptable Use",
            "code": "M60-AUP-%d" % next(_SEQ),
            "policy_type": "security",
            "version": "2.0",
        }
    )


def test_an_employee_acknowledges_the_current_version_of_an_approved_policy(m, policy):
    Ack = m.env["fix.grc.policy.attestation"]
    with pytest.raises(UserError, match="approved"):
        Ack.with_user(m.clerk).create({"policy_id": policy.id})
    policy.with_user(m.officer).action_approve()
    ack = Ack.with_user(m.clerk).create({"policy_id": policy.id})
    assert ack.employee_id == m.clerk.employee_id and ack.version == "2.0"
    assert policy.attested_count == 1
    with pytest.raises(IntegrityError), m.env.cr.savepoint():
        Ack.with_user(m.clerk).create({"policy_id": policy.id})
    # typed stamps are refused; a paper copy is the officer's to record
    with pytest.raises(UserError, match="Compliance Officer"):
        Ack.with_user(m.clerk).create(
            {
                "policy_id": policy.id,
                "method": "paper",
                "paper_employee_id": m.clerk2.employee_id.id,
            }
        )
    paper = Ack.with_user(m.officer).create(
        {"policy_id": policy.id, "method": "paper", "paper_employee_id": m.clerk2.employee_id.id}
    )
    assert paper.employee_id == m.clerk2.employee_id and paper.recorded_by_id == m.officer
    with pytest.raises(UserError, match="kept as recorded"):
        ack.with_user(m.clerk).write({"method": "paper"})
    report = __import__(
        "odoo.addons.cd_p03_portal.controllers.a10.m60", fromlist=["attestation_status"]
    ).attestation_status(m.env)
    row = next(r for r in report["rows"] if r["code"] == policy.code)
    assert row["acknowledged"] == 2


def test_a_policy_exception_is_time_boxed_and_decided_by_someone_else(m, policy):
    Exc = m.env["fix.grc.policy.exception"]
    vals = {
        "policy_id": policy.id,
        "justification": "Legacy POS cannot enforce MFA.",
        "compensating_control": "Weekly log review.",
        "valid_from": m.today,
        "valid_to": m.today + datetime.timedelta(days=400),
    }
    with pytest.raises(ValidationError, match="time-boxed"):
        Exc.with_user(m.officer).create(dict(vals))
    exc = Exc.with_user(m.officer).create(
        dict(vals, valid_to=m.today + datetime.timedelta(days=60))
    )
    assert exc.requested_by_id == m.officer
    with pytest.raises(UserError, match="requester"):
        exc.with_user(m.officer).action_approve()
    with pytest.raises(UserError, match="Compliance Officer"):
        exc.with_user(m.clerk).action_approve()
    exc.with_user(m.officer2).action_approve()
    assert exc.state == "approved" and exc.decided_by_id == m.officer2
    exc.sudo()._guarded().write(
        {
            "valid_from": m.today - datetime.timedelta(days=30),
            "valid_to": m.today - datetime.timedelta(days=1),
        }
    )
    assert m.env["fix.grc.policy.exception"].cron_expire() >= 1
    assert exc.state == "expired"


# ------------------------------------------------------------------ page 7
@pytest.fixture
def activity(m):
    return (
        m.env["fix.grc.processing.activity"]
        .with_user(m.officer)
        .create(
            {
                "name": "Repair intake: customer contact data",
                "purpose": "Contact the customer about the repair.",
                "lawful_basis": "contract",
                "data_categories": "name, phone, address",
                "subject_categories": "customers",
            }
        )
    )


def test_a_processing_record_is_in_force_only_with_retention_safeguards_and_pia(m, activity):
    with pytest.raises(UserError, match="retention and safeguards"):
        activity.with_user(m.officer).action_activate()
    activity.with_user(m.officer).write(
        {
            "retention_months": 72,
            "safeguards": "Role-restricted; encrypted at rest.",
            "high_risk": True,
        }
    )
    with pytest.raises(UserError, match="privacy impact"):
        activity.with_user(m.officer).action_activate()
    pia = (
        m.env["fix.grc.privacy.impact"]
        .with_user(m.officer)
        .create(
            {
                "activity_id": activity.id,
                "risk_summary": "Address exposure.",
                "mitigations": "Mask in exports.",
                "residual_risk": "low",
            }
        )
    )
    with pytest.raises(UserError, match="author"):
        pia.with_user(m.officer).action_approve()
    pia.with_user(m.officer2).action_approve()
    activity.with_user(m.officer).action_activate()
    assert activity.state == "active" and activity.activated_by_id == m.officer
    with pytest.raises(UserError, match="five years"):
        activity.with_user(m.officer).unlink()
    with pytest.raises(REFUSED):
        m.env["fix.grc.processing.activity"].with_user(m.clerk).create(
            {
                "name": "x",
                "purpose": "x",
                "lawful_basis": "consent",
                "data_categories": "x",
                "subject_categories": "x",
            }
        )


def test_a_transfer_needs_an_activity_in_force_and_a_second_officer(m, activity):
    transfer = (
        m.env["fix.grc.data.transfer"]
        .with_user(m.officer)
        .create(
            {
                "activity_id": activity.id,
                "destination_country_id": m.env.ref("base.sg").id,
                "recipient": "Cloud backup provider",
                "basis": "contract_clauses",
                "safeguards": "SCC-equivalent clauses; AES-256.",
            }
        )
    )
    with pytest.raises(UserError, match="not in force"):
        transfer.with_user(m.officer2).action_approve()
    activity.sudo()._guarded().write({"state": "active"})
    with pytest.raises(UserError, match="requester"):
        transfer.with_user(m.officer).action_approve()
    transfer.with_user(m.officer2).action_approve()
    assert transfer.state == "approved"


def test_the_breach_register_is_restricted_and_closes_only_with_its_decision(m):
    Breach = m.env["fix.grc.data.breach"]
    with pytest.raises(AccessError):
        Breach.with_user(m.clerk).create({"description": "x"})
    breach = Breach.with_user(m.legal).create(
        {"description": "Courier label sheet with 30 customer phones lost."}
    )
    with pytest.raises(AccessError):
        breach.with_user(m.clerk).read(["description"])
    with pytest.raises(UserError, match="contain"):
        breach.with_user(m.officer).action_contain()
    breach.with_user(m.legal).write({"containment": "Courier searched; sheet recovered."})
    breach.with_user(m.legal).action_contain()
    with pytest.raises(UserError, match="Compliance Officer"):
        breach.with_user(m.legal).action_close()
    with pytest.raises(UserError, match="notification decision"):
        breach.with_user(m.officer).action_close()
    breach.with_user(m.officer).write(
        {"assessment": "Low: recovered within 2 hours.", "notification_decision": "contractual"}
    )
    with pytest.raises(UserError, match="notified"):
        breach.with_user(m.officer).action_close()
    breach.with_user(m.officer).write({"notified_parties": "Corporate client X (contract cl. 14)"})
    breach.with_user(m.officer).action_close()
    assert breach.state == "closed" and breach.closed_by_id == m.officer


# ------------------------------------------------------------------ page 3 / P03
def test_an_sod_rule_says_when_nothing_enforces_it(m):
    roles = m.env["fix.role"].search([], limit=2)
    if len(roles) < 2:
        pytest.skip("the role register is empty on this database")
    rule = m.env["fix.grc.sod.rule"].create(
        {"name": "M60 pay vs approve", "role_a": roles[0].id, "role_b": roles[1].id}
    )
    assert rule.last_test_result.startswith("Not enforced")
    control = m.env["fix.sod.control"].search([], limit=1)
    if control:
        rule.enforced_by_id = control
        assert rule.last_test_result != "Not enforced — no M29 control named"


def test_the_workspace_saves_what_the_form_offers_and_refuses_the_stamps(m):
    _appetite(m)
    out = p03(
        m,
        _MW,
        m.owner,
        model="fix.risk.assessment",
        record_id=None,
        values={
            "risk_id": m.risk.id,
            "likelihood": "2",
            "impact": "2",
            "rationale": "Second supplier qualified.",
            "next_review_date": str(m.today + datetime.timedelta(days=60)),
            "assessed_by_id": m.officer.employee_id.id,
        },
    )
    # a stamp is not a form input: the endpoint drops it and the session's
    # own employee is stamped
    assert "error" not in out, out
    typed = m.env["fix.risk.assessment"].browse(out["id"])
    assert typed.assessed_by_id == m.owner.employee_id
    out = p03(
        m,
        _MW,
        m.owner,
        model="fix.risk.assessment",
        record_id=None,
        values={
            "risk_id": m.risk.id,
            "likelihood": "2",
            "impact": "2",
            "rationale": "Third supplier qualified.",
            "next_review_date": str(m.today + datetime.timedelta(days=90)),
        },
    )
    assert "error" not in out, out
    assert m.risk.risk_score == 4
    # a list action runs through the served verb with its asked reason
    treatment = (
        m.env["fix.risk.treatment"]
        .with_user(m.owner)
        .create(
            {
                "name": "Dual-source spec",
                "risk_id": m.risk.id,
                "rationale": "x",
                "owner_id": m.owner.employee_id.id,
                "due_on": str(m.today),
            }
        )
    )
    out = p03(
        m,
        _MA,
        m.owner,
        model="fix.risk.treatment",
        ids=treatment.ids,
        method="action_complete",
        kwargs={"note": "Spec issued"},
    )
    assert out.get("success") is True, out
    assert treatment.state == "done"
