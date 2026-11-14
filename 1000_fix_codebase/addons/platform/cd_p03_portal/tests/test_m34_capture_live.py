# M34 capture audit (2026-11-13) - the captures the sub-module pages now offer,
# driven through the workspace endpoints as a NON-ADMIN clerk (the superuser
# is trusted by the model guards and would hide a gap).
#
#   * Record a Survey Response: a rating or per-question answers written on
#     the survey the closed order raised make it Responded (it stayed "sent",
#     outside every CSAT / NPS figure), log who keyed it, and raise the
#     detractor follow-up; the state itself is never typed.
#   * The answer grid only takes answers that belong to the survey's
#     instrument and fit the question's scale; an NPS row with no score is
#     refused rather than stored as 0.
#   * Detractor follow-ups move by Record Contact / Close (Not Recovered).
#   * Complaint SLA bindings are served, and only an administrator saves one.
#
# Second pass (2026-11-14):
#   * Complaint categories (the maintained taxonomy, FR-CXM-030) and SLA
#     bindings are saved by the Contact Centre Supervisor group, never by a
#     clerk; a complaint filed under a category takes its ISO category and
#     starts at no less than the category's severity.
#   * A follow-up closes only after a recorded contact, and "Recovered" only
#     with what the customer said (BRU-CXM-03/04).
#   * A review is published only after the customer's consent is recorded,
#     and its state is never typed (BRU-CXM-13).
import itertools
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.exceptions import UserError

_SEQ = itertools.count(1)


class FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def call():
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


@pytest.fixture
def clerk_env(odoo_env):
    n = next(_SEQ)
    user = (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M34 Capture Clerk %d" % n,
                "login": "m34.capture.%d@a03.test" % n,
                "group_ids": [(6, 0, [odoo_env.ref("base.group_user").id])],
            }
        )
    )
    return odoo_env(user=user.id)


@pytest.fixture
def supervisor_env(odoo_env):
    n = next(_SEQ)
    groups = [
        odoo_env.ref("base.group_user").id,
        odoo_env.ref("cd_contact_centre.group_cc_supervisor").id,
    ]
    user = (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M34 CX Supervisor %d" % n,
                "login": "m34.supervisor.%d@a03.test" % n,
                "group_ids": [(6, 0, groups)],
            }
        )
    )
    return odoo_env(user=user.id)


@pytest.fixture
def survey(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    customer = env["res.partner"].create({"name": "M34 Capture Customer"})
    company = env["res.company"].create({"name": "M34 Capture Co"})
    entity = env["fix.entity"].create(
        {"code": "M34CAP", "legal_name": "M34 Capture Entity", "company_id": company.id}
    )
    branch = env["fix.branch"].create(
        {"name": "M34 Capture", "code": "M34CP", "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    brand = env["fix.brand"].create({"name": "M34CapBrand", "code": "M34CB"})
    model = env["fix.device.model"].create({"name": "M34 Cap Phone", "brand_id": brand.id})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-M34-CAP"}
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "No display",
            "state": "closed",
        }
    )
    # as the closed-order consumer raises it, before anyone answers
    return env["fix.survey"].create(
        {"service_order_id": order.id, "operating_unit_id": ou.id, "state": "sent"}
    )


@pytest.fixture
def instrument(odoo_env):
    def _make(code):
        return odoo_env["fix.survey.template"].create(
            {
                "name": "M34 capture %s" % code,
                "code": "M34-CAP-%s" % code,
                "purpose": "post_service",
                "question_ids": [
                    (
                        0,
                        0,
                        {
                            "sequence": 10,
                            "code": "punctuality",
                            "text": "On time?",
                            "text_bn": "সময়মতো?",
                            "question_type": "rating_5",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "sequence": 20,
                            "code": "recommend",
                            "text": "Recommend?",
                            "text_bn": "সুপারিশ?",
                            "question_type": "nps_11",
                        },
                    ),
                ],
            }
        )

    return _make


def _q(template, code):
    return template.question_ids.filtered(lambda q: q.code == code)


def _answers(*rows):
    return {"field": "answer_ids", "rows": [{"id": None, "values": v} for v in rows], "removed": []}


def test_a_recorded_rating_makes_the_survey_responded(clerk_env, call, survey):
    res = call(
        clerk_env,
        "model_write",
        model="fix.survey",
        record_id=survey.id,
        values={"rating": "2", "comment": "Technician was late"},
    )
    assert "error" not in res, res
    survey.invalidate_recordset()
    assert survey.state == "responded"
    assert survey.followup_id and survey.followup_id.reason == "low_rating"
    assert any(
        "Response recorded by M34 Capture Clerk" in (m.body or "") for m in survey.message_ids
    )


def test_the_survey_state_is_not_typed(clerk_env, call, survey):
    res = call(
        clerk_env,
        "model_write",
        model="fix.survey",
        record_id=survey.id,
        values={"state": "responded"},
    )
    assert res.get("error"), res
    survey.invalidate_recordset()
    assert survey.state == "sent"


def test_answers_by_parameter_are_recorded_against_the_instrument(
    clerk_env, call, survey, instrument
):
    t = instrument("A")
    res = call(
        clerk_env,
        "model_write",
        model="fix.survey",
        record_id=survey.id,
        values={"template_id": t.id},
        lines=_answers(
            {"question_id": _q(t, "punctuality").id, "value_numeric": 5},
            {"question_id": _q(t, "recommend").id, "value_numeric": 4},
        ),
    )
    assert "error" not in res, res
    survey.invalidate_recordset()
    assert survey.state == "responded"
    assert sorted(survey.answer_ids.mapped("question_code")) == ["punctuality", "recommend"]
    assert survey.followup_id.reason == "detractor_nps"


@pytest.mark.parametrize(
    "case",
    ["out_of_scale", "other_instrument", "nps_without_score", "no_instrument"],
)
def test_the_answer_grid_refuses_what_cannot_be_compared(clerk_env, call, survey, instrument, case):
    t, other = instrument("B"), instrument("C")
    values = {"template_id": t.id}
    row = {"question_id": _q(t, "punctuality").id, "value_numeric": 9}
    if case == "other_instrument":
        row = {"question_id": _q(other, "punctuality").id, "value_numeric": 4}
    elif case == "nps_without_score":
        row = {"question_id": _q(t, "recommend").id}
    elif case == "no_instrument":
        values = {}
        row = {"question_id": _q(t, "punctuality").id, "value_numeric": 4}
    res = call(
        clerk_env,
        "model_write",
        model="fix.survey",
        record_id=survey.id,
        values=values,
        lines=_answers(row),
    )
    assert res.get("error"), (case, res)
    survey.invalidate_recordset()
    assert not survey.answer_ids and survey.state == "sent"


def test_a_followup_moves_by_its_actions(clerk_env, call, survey):
    survey.write({"rating": "1"})
    followup = survey.followup_id
    assert followup.state == "open"

    def act(method, **kwargs):
        return call(
            clerk_env,
            "model_action",
            model="fix.cx.followup",
            ids=[followup.id],
            method=method,
            kwargs=kwargs,
        )

    # BRU-CXM-03: nothing closes a follow-up nobody contacted
    assert not act("action_close_unrecovered", reason="No answer")["success"]
    assert not act("action_close_recovered", confirmation="Happy now")["success"]
    assert not act("action_mark_contacted")["success"], "a contact needs what was said"
    assert act("action_mark_contacted", note="Apologised; offered a re-check")["success"]
    followup.invalidate_recordset()
    assert followup.state == "contacted" and "offered a re-check" in followup.notes
    assert followup.contacted_at
    assert not act("action_mark_contacted", note="again")["success"]
    assert not act("action_close_unrecovered")["success"], "a close needs a reason"
    assert act("action_close_unrecovered", reason="Customer moved to a competitor")["success"]
    followup.invalidate_recordset()
    assert followup.state == "closed" and followup.closed_at
    res = call(
        clerk_env,
        "model_write",
        model="fix.cx.followup",
        record_id=followup.id,
        values={"state": "open"},
    )
    assert res.get("error"), res


def test_a_recovery_closes_on_the_customers_confirmation(clerk_env, call, survey):
    """BRU-CXM-04: never on internal action alone."""
    survey.write({"rating": "1"})
    followup = survey.followup_id

    def act(method, **kwargs):
        return call(
            clerk_env,
            "model_action",
            model="fix.cx.followup",
            ids=[followup.id],
            method=method,
            kwargs=kwargs,
        )

    assert act("action_mark_contacted", note="Called; re-check booked")["success"]
    assert not act("action_close_recovered")["success"], "a recovery needs the customer's words"
    assert act("action_close_recovered", confirmation="Customer: device fine now, thanks")[
        "success"
    ]
    followup.invalidate_recordset()
    assert followup.state == "recovered"
    assert followup.customer_confirmed_at and "device fine" in followup.customer_confirmation


def test_sla_bindings_are_saved_by_a_supervisor_not_a_clerk(
    odoo_env, clerk_env, supervisor_env, call
):
    policy = odoo_env["fix.sla.policy"].search([], limit=1)
    if not policy:
        pytest.skip("no SLA policy on this database")
    vals = {"severity": "major", "policy_id": policy.id}
    assert call(clerk_env, "model_write", model="fix.complaint.sla.rule", values=vals).get("error")
    saved = call(supervisor_env, "model_write", model="fix.complaint.sla.rule", values=vals)
    assert saved.get("id"), saved


def _taxonomy(call, env, **vals):
    return call(env, "model_write", model="fix.complaint.taxonomy", values=vals)


def test_complaint_categories_are_saved_by_a_supervisor_not_a_clerk(
    odoo_env, clerk_env, supervisor_env, call
):
    n = next(_SEQ)
    base = {"name": "Late parts %d" % n, "name_bn": "যন্ত্রাংশ দেরি %d" % n, "category": "delay"}
    refused = _taxonomy(call, clerk_env, code="DLY%d" % n, **base)
    assert refused.get("error"), refused
    listed = call(clerk_env, "model_records", model="fix.complaint.taxonomy", cols=["code"])
    assert "error" not in listed, listed

    parent = _taxonomy(call, supervisor_env, code="dly%d" % n, default_severity="major", **base)
    assert parent.get("id"), parent
    node = odoo_env["fix.complaint.taxonomy"].browse(parent["id"])
    assert node.code == "DLY%d" % n, "codes are kept upper-case"

    child = _taxonomy(
        call,
        supervisor_env,
        code="DLY%d-IMP" % n,
        name="Imported part held at customs",
        name_bn="শুল্কে আটকে",
        parent_id=parent["id"],
    )
    assert child.get("id"), child
    kid = odoo_env["fix.complaint.taxonomy"].browse(child["id"])
    assert kid.category == "delay", "a sub-category carries its parent's ISO category"
    assert kid.complete_name.endswith("/ Imported part held at customs")

    clash = _taxonomy(
        call,
        supervisor_env,
        code="DLY%d-BAD" % n,
        name="Wrong branch",
        name_bn="ভুল",
        parent_id=parent["id"],
        category="billing",
    )
    assert clash.get("error"), "a sub-category cannot contradict its parent"
    no_bn = _taxonomy(call, supervisor_env, code="X%d" % n, name="No Bengali", category="other")
    assert no_bn.get("error"), "DE-17: the Bengali name is required"


def test_a_complaint_follows_its_category(odoo_env, supervisor_env, call):
    n = next(_SEQ)
    Tax = odoo_env["fix.complaint.taxonomy"]
    safety = Tax.create(
        {
            "code": "SAF%d" % n,
            "name": "Unsafe repair",
            "name_bn": "অনিরাপদ মেরামত",
            "category": "device_damage",
            "default_severity": "critical",
        }
    )
    ou = odoo_env["operating.unit"].search([], limit=1)
    customer = odoo_env["res.partner"].create({"name": "M34 Taxonomy Customer %d" % n})
    complaint = odoo_env["fix.complaint"].create(
        {
            "name": "CMP-TAX-%d" % n,
            "customer_id": customer.id,
            "operating_unit_id": ou.id,
            "description": "Battery swelled after the repair",
            "category": "billing",
            "severity": "minor",
            "taxonomy_id": safety.id,
        }
    )
    assert complaint.category == "device_damage", "the ISO category follows the category"
    assert complaint.severity == "critical", "a category's severity is the floor at intake"
    assert any("raised from minor to critical" in (m.body or "") for m in complaint.message_ids)

    # re-categorising moves the ISO category with it
    billing = Tax.create(
        {"code": "BIL%d" % n, "name": "Overcharged", "name_bn": "বেশি বিল", "category": "billing"}
    )
    complaint.write({"taxonomy_id": billing.id})
    assert complaint.category == "billing"
    assert complaint.severity == "critical", "re-categorising never lowers a severity"
    # and a supervisor moving a category moves its open complaints
    res = call(
        supervisor_env,
        "model_write",
        model="fix.complaint.taxonomy",
        record_id=billing.id,
        values={"category": "service_quality"},
    )
    assert "error" not in res, res
    complaint.invalidate_recordset()
    assert complaint.category == "service_quality"


def _review(call, env, **extra):
    vals = {
        "name": "Fast and honest",
        "source": "google",
        "rating": 5,
        "reviewed_at": "2026-11-14",
    }
    vals.update(extra)
    return call(env, "model_write", model="fix.cx.review", values=vals)


def test_a_review_is_published_only_with_consent(odoo_env, clerk_env, call):
    typed = _review(call, clerk_env, state="published")
    # the state is not a form field: the save either refuses it or ignores it
    assert typed.get("error") or odoo_env["fix.cx.review"].browse(typed["id"]).state == "new", typed
    made = _review(call, clerk_env)
    assert made.get("id"), made
    review = odoo_env["fix.cx.review"].browse(made["id"])

    def act(method, **kwargs):
        return call(
            clerk_env,
            "model_action",
            model="fix.cx.review",
            ids=[review.id],
            method=method,
            kwargs=kwargs,
        )

    assert not act("action_publish")["success"], "BRU-CXM-13: no consent, no publication"
    assert not act("action_record_consent")["success"], "consent needs how it was given"
    assert act("action_record_consent", evidence="SMS reply YES on 14 Nov")["success"]
    assert act("action_publish")["success"]
    review.invalidate_recordset()
    assert review.state == "published" and review.moderated_by_id
    assert act("action_reply", reply="Thank you for trusting 1000FiX")["success"]
    assert act("action_withdraw_consent", reason="Customer asked to take it down")["success"]
    review.invalidate_recordset()
    assert review.state == "new" and not review.publication_consent
    assert not act("action_publish")["success"]
    with pytest.raises(UserError):  # the model refuses any route, not only the form
        review.write({"state": "published"})
        review.flush_recordset()


def test_sla_bindings_are_served_and_saved_only_by_an_administrator(odoo_env, clerk_env, call):
    policy = odoo_env["fix.sla.policy"].search([], limit=1)
    if not policy:
        pytest.skip("no SLA policy on this database")
    listed = call(
        clerk_env, "model_records", model="fix.complaint.sla.rule", cols=["severity", "policy_id"]
    )
    assert "error" not in listed, listed
    vals = {"severity": "critical", "policy_id": policy.id}
    refused = call(clerk_env, "model_write", model="fix.complaint.sla.rule", values=vals)
    assert refused.get("error"), refused
    admin_env = odoo_env(user=odoo_env.ref("base.user_admin").id)
    saved = call(admin_env, "model_write", model="fix.complaint.sla.rule", values=vals)
    assert saved.get("id"), saved
