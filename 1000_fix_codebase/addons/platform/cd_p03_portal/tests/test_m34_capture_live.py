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
import itertools
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

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

    assert not act("action_mark_contacted")["success"], "a contact needs what was said"
    assert act("action_mark_contacted", note="Apologised; offered a re-check")["success"]
    followup.invalidate_recordset()
    assert followup.state == "contacted" and "offered a re-check" in followup.notes
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
