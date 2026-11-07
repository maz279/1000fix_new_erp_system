"""A12 finish audit, M64: every engineering item, through what the screen calls.

working/A12_evidence/finish/m64_m67/FINDINGS.md, E1-E30, lifecycle rows 5, 10,
12, 14 and BRU-MDM-01, 07, 11, 13, 14, 17, 22.

Every decision is taken by a NON-ADMIN user. The walks run through the same
controller the workspace calls (/p03/model/write, /action, /form), with the
kwargs the JS sends; the superuser only builds fixtures.
"""

import json
import re
import types
from pathlib import Path

import pytest
from odoo.addons.cd_mdm_core.models.fix_mdm_attribute_governance import DIRECT_EDIT_PARAM
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
STEWARD = "cd_entity_config.group_mdm_domain_steward"
PLATFORM_ADMIN = "cd_entity_config.group_platform_admin"
PARTY_STEWARD = "cd_party_master.group_party_data_steward"
CONTACTS = "base.group_partner_manager"
CR = "fix.mdm.change.request"
JS = Path(__file__).resolve().parents[2] / "cd_p03_portal" / "static" / "src" / "a12" / "m64.js"


class Ctx:
    pass


def _user(env, login, *groups):
    gids = [env.ref("base.group_user").id] + [env.ref(x).id for x in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create({"name": login, "login": login + "@a12f.test", "group_ids": [(6, 0, gids)]})
    )


class Api:
    """The real P03 endpoints, called the way the workspace calls them."""

    def __init__(self, env, user):
        self.env = env(user=user.id)

    def _call(self, name, **kw):
        import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

        saved = getattr(g, "request", None)
        g.request = types.SimpleNamespace(env=self.env)
        try:
            ctl = g.P03GenericApiController()
            return getattr(g.P03GenericApiController, name).original_endpoint(ctl, **kw)
        finally:
            g.request = saved

    def write(self, model, values, record_id=None):
        return self._call("model_write", model=model, record_id=record_id, values=values)

    def action(self, model, rec, method, **kwargs):
        return self._call("model_action", model=model, ids=[rec.id], method=method, kwargs=kwargs)

    def form(self, model, names, record_id=None):
        return self._call(
            "model_form", model=model, fields=[{"name": n} for n in names], record_id=record_id
        )

    def records(self, model, cols):
        return self._call("model_records", model=model, cols=cols)


@pytest.fixture
def w(odoo_env):
    c = Ctx()
    c.env = odoo_env
    c.proposer = _user(odoo_env, "f64.proposer")
    c.plain = _user(odoo_env, "f64.plain")
    c.contacts = _user(odoo_env, "f64.contacts", CONTACTS)
    c.steward_a = _user(odoo_env, "f64.steward.a", STEWARD)
    c.steward_b = _user(odoo_env, "f64.steward.b", STEWARD)
    c.admin = _user(odoo_env, "f64.platform", PLATFORM_ADMIN)
    # exactly what role R-39 grants: no Contacts (E15)
    c.party_steward = _user(odoo_env, "f64.party.steward", PARTY_STEWARD, STEWARD)
    c.partner = odoo_env["res.partner"].create(
        {"name": "F64 Party", "phone": "01700000001", "is_company": True}
    )
    return c


def _vals(partner, changes=None, **extra):
    return {
        "title": "Fix the phone",
        "model_name": partner._name,
        "record_id": partner.id,
        "proposed_changes": json.dumps(changes or {"phone": "01711111111"}),
        **extra,
    }


def _cr(w, target=None, changes=None, user=None, **extra):
    return (
        w.env[CR].with_user(user or w.proposer).create(_vals(target or w.partner, changes, **extra))
    )


def _task(rec, user):
    return rec.sudo().approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == user
    )


def _approved(w, cr, proposer=None, approver=None):
    user = proposer or w.proposer
    cr.with_user(user).action_submit()
    cr.with_user(user).action_request_approval(justification="needed for KYC")
    approver = approver or w.steward_a
    _task(cr, approver).with_user(approver).action_approve(comment="ok")
    assert cr.state == "approved"
    return cr


def _refused(env, fn):
    try:
        with env.cr.savepoint():
            fn()
    except REFUSED as exc:
        return str(exc) or type(exc).__name__
    return None


def _register(env, model, field, category="other", block=False):
    Register = env["fix.mdm.governed.attribute"]
    return Register.sudo().search([("model_name", "=", model), ("field_name", "=", field)]) or (
        Register.sudo().create(
            {
                "model_name": model,
                "field_name": field,
                "category": category,
                "block_direct_edit": block,
            }
        )
    )


def _dup(w, a=None, b=None, score=92.0, **extra):
    Partner = w.env["res.partner"]
    a = a or Partner.create({"name": "F64 Dup A", "phone": "01710000001"})
    b = b or Partner.create({"name": "F64 Dup B", "phone": "01710000001"})
    # superuser: the score is the detection run's to set (E18)
    vals = {
        "res_model": "res.partner",
        "record_a_ref": str(a.id),
        "record_b_ref": str(b.id),
        "score": score,
        **extra,
    }
    return w.env["fix.mdm.duplicate"].sudo().create(vals), a, b


def _merged(w, dup, **kwargs):
    dup.with_user(w.steward_a).action_merge(justification="same person", **kwargs)
    merge = w.env["fix.party.merge"].browse(dup.party_merge_id)
    _task(merge, w.party_steward).with_user(w.party_steward).action_approve(comment="ok")
    return merge


def _list(w, code="F64-L1", values=("R1",), user=None):
    user = user or w.steward_a
    lst = w.env["fix.mdm.code.list"].with_user(user).create({"code": code, "name": "List " + code})
    for value in values:
        w.env["fix.mdm.code.entry"].with_user(user).create(
            {"list_id": lst.id, "value": value, "label": value}
        )
    return lst


def _steward_req(w, user=None, changes=None, **extra):
    vals = {
        "request_type": "update",
        "res_model": "res.partner",
        "record_ref": str(w.partner.id),
        "reason": "kyc",
        "proposed_changes": json.dumps(changes or {"phone": "01733333333"}),
        **extra,
    }
    return w.env["fix.mdm.steward"].with_user(user or w.steward_a).create(vals)


def _steward_walk(w, st):
    """A raises and routes, B reviews and decides: the two-steward walk."""
    st.with_user(w.steward_b).action_review()
    st.with_user(w.steward_a).action_request_approval(justification="kyc")
    _task(st, w.steward_b).with_user(w.steward_b).action_approve(comment="ok")
    assert st.state == "approved"
    return st


# ===================== E1: the workspace can run a change request =====================

CR_FORM = ("title", "description", "model_name", "record_id", "proposed_changes", "priority")


def test_a12f_e1_new_form_offers_the_target_and_payload(w):
    res = Api(w.env, w.proposer).form(CR, CR_FORM)
    assert not [f["name"] for f in res["fields"] if f["readonly"]], res["fields"]


def test_a12f_e1_full_walk_through_the_workspace(w):
    """Proposer raises, edits and routes; a steward decides from the inbox; another
    applies. Screens are the only way in."""
    proposer = Api(w.env, w.proposer)
    res = proposer.write(CR, _vals(w.partner, priority="normal"))
    assert res.get("id"), res
    cr = w.env[CR].browse(res["id"])
    res = proposer.write(CR, {"proposed_changes": "phone=01722222222"}, record_id=cr.id)
    assert not res.get("error"), res
    assert proposer.action(CR, cr, "action_submit")["success"]
    res = proposer.action(CR, cr, "action_request_approval", justification="KYC document")
    assert res["success"], res
    assert w.partner.phone == "01700000001", "nothing lands until apply"
    _task(cr, w.steward_a).with_user(w.steward_a).action_approve(comment="ok")
    res = Api(w.env, w.steward_b).action(CR, cr, "action_apply")
    assert res["success"], res
    w.partner.invalidate_recordset()
    assert w.partner.phone == "01722222222"
    assert cr.state == "implemented" and cr.applied_by == w.steward_b


def test_a12f_e1_payload_is_locked_once_submitted(w):
    cr = _cr(w)
    cr.with_user(w.proposer).action_submit()
    res = Api(w.env, w.proposer).write(CR, {"proposed_changes": "phone=0"}, record_id=cr.id)
    assert res.get("error"), res
    form = Api(w.env, w.proposer).form(CR, CR_FORM, record_id=cr.id)
    locked = {f["name"] for f in form["fields"] if f["readonly"]}
    assert {"model_name", "record_id", "proposed_changes", "title", "description"} <= locked


# ===================== E2 / B4: the governed register =====================


def test_a12f_e2_user_cannot_be_made_an_admin(w):
    system = w.env.ref("base.group_system")
    err = _refused(w.env, lambda: _cr(w, target=w.plain, changes={"group_ids": [[4, system.id]]}))
    assert err and "access control" in err
    assert not w.plain.has_group("base.group_system")


def test_a12f_e2_groups_and_technical_models_are_refused(w):
    assert _refused(
        w.env, lambda: _cr(w, target=w.env.ref("base.group_system"), changes={"name": "x"})
    )
    param = w.env["ir.config_parameter"].sudo().search([], limit=1)
    assert _refused(w.env, lambda: _cr(w, target=param, changes={"value": "1"}))


def test_a12f_e2_guarded_workflow_field_cannot_be_laundered(w):
    project = w.env["fix.project"].create({"name": "F64 Launder", "budget": 5000000.0})
    assert _refused(w.env, lambda: _cr(w, target=project, changes={"state": "active"}))
    project.invalidate_recordset()
    assert project.state == "draft"


def test_a12f_e2_field_off_the_register_is_refused(w):
    err = _refused(w.env, lambda: _cr(w, changes={"comment": "not governed"}))
    assert err and "register" in err


def test_a12f_e2_registered_partner_and_product_attributes_apply(w):
    tmpl = w.env["product.template"].create({"name": "F64 Part", "list_price": 10.0})
    cr = _approved(w, _cr(w, target=tmpl, changes={"list_price": 99.0}))
    cr.with_user(w.steward_b).action_apply()
    tmpl.invalidate_recordset()
    assert tmpl.list_price == 99.0


def test_a12f_e2_apply_rechecks_the_register(w):
    cr = _approved(w, _cr(w, changes={"email": "new@f64.test"}))
    _register(w.env, "res.partner", "email").sudo().unlink()
    assert _refused(w.env, lambda: cr.with_user(w.steward_b).action_apply())
    assert cr.state == "approved"
    w.partner.invalidate_recordset()
    assert w.partner.email != "new@f64.test"


def test_a12f_e2_register_refuses_forbidden_rows_even_for_an_admin(w):
    Register = w.env["fix.mdm.governed.attribute"].with_user(w.admin)
    for model, field in (
        ("res.users", "login"),
        ("res.groups", "name"),
        ("ir.config_parameter", "value"),
        ("fix.project", "state"),
        ("res.partner", "bank_ids"),
        ("res.partner", "no_such_field"),
    ):
        assert _refused(
            w.env, lambda m=model, f=field: Register.create({"model_name": m, "field_name": f})
        ), (model, field)


def test_a12f_e2_only_a_platform_admin_edits_the_register(w):
    row = _register(w.env, "res.partner", "phone")
    assert _refused(w.env, lambda: row.with_user(w.steward_a).write({"active": False}))
    assert _refused(
        w.env,
        lambda: w.env["fix.mdm.governed.attribute"]
        .with_user(w.steward_a)
        .create({"model_name": "res.partner", "field_name": "website"}),
    )
    res = Api(w.env, w.admin).write(
        "fix.mdm.governed.attribute",
        {"model_name": "res.partner", "field_name": "website", "category": "contact"},
    )
    assert res.get("id"), res


def test_a12f_e2_bank_account_of_an_employee_keeps_its_own_route(w):
    partner = w.env["res.partner"].create({"name": "F64 Emp"})
    bank = w.env["res.partner.bank"].create({"partner_id": partner.id, "acc_number": "F64-EMP-1"})
    w.env["hr.employee"].create({"name": "F64 Emp", "bank_account_ids": [(6, 0, [bank.id])]})
    err = _refused(w.env, lambda: _cr(w, target=bank, changes={"acc_number": "F64-EMP-2"}))
    assert err and "Employee Master Change" in err


def test_a12f_e2_applied_bank_change_withdraws_the_payee_confirmation(w):
    partner = w.env["res.partner"].create({"name": "F64 Payee"})
    bank = w.env["res.partner.bank"].create({"partner_id": partner.id, "acc_number": "F64-OLD-1"})
    bank._fix_confirming().sudo().write({"fix_confirmed": True})
    cr = _approved(w, _cr(w, target=bank, changes={"acc_number": "F64-NEW-1"}))
    cr.with_user(w.steward_b).action_apply()
    bank.invalidate_recordset()
    assert bank.acc_number == "F64-NEW-1" and not bank.fix_confirmed


# ===================== E3: the format the form asks for =====================


def test_a12f_e3_lines_and_json_both_parse_and_apply_the_same(w):
    cr = _approved(w, _cr(w, proposed_changes="phone = 01744444444\nemail=x@f64.test\n"))
    cr.with_user(w.steward_b).action_apply()
    w.partner.invalidate_recordset()
    assert (w.partner.phone, w.partner.email) == ("01744444444", "x@f64.test")


@pytest.mark.parametrize(
    "payload",
    [
        "phone",
        "phone=1\nnot a line",
        "phone=1\nphone=2",
        "1phone=1",
        '{"phone": ',
        "[1, 2]",
        "{}",
        "   ",
    ],
)
def test_a12f_e3_anything_else_is_refused(w, payload):
    assert _refused(w.env, lambda: _cr(w, proposed_changes=payload)), payload


def test_a12f_e3_line_values_take_the_field_type(w):
    Payload = w.env[CR]
    _register(w.env, "res.partner", "credit_limit", "credit")
    assert Payload._mdm_parse_payload("credit_limit=12.5", "res.partner", "t") == {
        "credit_limit": 12.5
    }
    assert Payload._mdm_parse_payload("active=no", "res.partner", "t") == {"active": False}
    assert Payload._mdm_parse_payload("phone=", "res.partner", "t") == {"phone": False}
    with pytest.raises(ValidationError, match="not a valid"):
        Payload._mdm_parse_payload("credit_limit=lots", "res.partner", "t")
    with pytest.raises(ValidationError, match="not a valid"):
        Payload._mdm_parse_payload("parent_id=CUST-1", "res.partner", "t")


def test_a12f_e3_steward_form_takes_lines_too(w):
    res = Api(w.env, w.steward_a).write(
        "fix.mdm.steward",
        {
            "request_type": "update",
            "res_model": "res.partner",
            "record_ref": str(w.partner.id),
            "reason": "kyc",
            "proposed_changes": "phone=01711111111",
        },
    )
    assert res.get("id"), res


def test_a12f_e3_form_labels_name_the_format():
    source = JS.read_text(encoding="utf-8")
    labels = re.findall(r"name: 'proposed_changes'[^\n]*label: [\"']([^\"']*)", source)
    assert len(labels) == 2
    assert all("field=value" in label and "JSON" in label for label in labels)


# ===================== E4: a value that cannot be written =====================


def test_a12f_e4_bad_fk_is_caught_at_submit(w):
    _register(w.env, "res.partner", "industry_id")
    cr = _cr(w, changes={"industry_id": 99999999})
    err = _refused(w.env, lambda: cr.with_user(w.proposer).action_submit())
    assert err and "cannot be written" in err
    assert cr.state == "draft"


def test_a12f_e4_bad_selection_is_caught_at_submit(w):
    _register(w.env, "res.partner", "type")
    cr = _cr(w, changes={"type": "not-a-type"})
    assert _refused(w.env, lambda: cr.with_user(w.proposer).action_submit())
    assert cr.state == "draft"


def test_a12f_e4_dry_run_changes_nothing(w):
    cr = _cr(w)
    cr.with_user(w.proposer).action_submit()
    w.partner.invalidate_recordset()
    assert w.partner.phone == "01700000001"
    assert cr.state == "submitted" and json.loads(cr.current_values)["phone"] == "01700000001"


def _approved_with_vanishing_value(w):
    _register(w.env, "res.partner", "industry_id")
    industry = w.env["res.partner.industry"].create({"name": "F64 Industry"})
    cr = _approved(w, _cr(w, changes={"industry_id": industry.id}))
    industry.unlink()
    return cr


def test_a12f_e4_apply_failure_is_readable_and_changes_nothing(w):
    cr = _approved_with_vanishing_value(w)
    res = Api(w.env, w.steward_b).action(CR, cr, "action_apply")
    assert not res["success"]
    assert "Finance support" not in res["error"] and "cannot be written" in res["error"], res
    assert cr.state == "approved"


def test_a12f_e4_a_stranded_request_can_be_cancelled(w):
    cr = _approved_with_vanishing_value(w)
    res = Api(w.env, w.proposer).action(CR, cr, "action_cancel")
    assert res["success"], res
    assert cr.state == "cancelled" and cr.approval_state == "none"


# ===================== E5, E6, E7 =====================


def test_a12f_e5_bystander_cannot_touch_another_users_request(w):
    cr = _cr(w)
    assert _refused(w.env, lambda: cr.with_user(w.plain).write({"proposed_changes": "phone=0"}))
    assert _refused(w.env, lambda: cr.with_user(w.plain).action_submit())
    assert _refused(w.env, lambda: cr.with_user(w.plain).action_cancel())
    assert cr.state == "draft"


def test_a12f_e5_reference_cannot_be_rewritten(w):
    cr = _cr(w)
    assert _refused(w.env, lambda: cr.with_user(w.proposer).write({"reference": "FAKE/1"}))
    assert _refused(w.env, lambda: cr.with_user(w.steward_a).write({"reference": "FAKE/1"}))


def test_a12f_e5_review_notes_are_the_deciding_stewards(w):
    cr = _cr(w)
    assert _refused(w.env, lambda: cr.with_user(w.proposer).write({"review_notes": "self"}))
    cr.with_user(w.proposer).action_submit()
    assert _refused(w.env, lambda: cr.with_user(w.proposer).write({"review_notes": "self"}))
    res = Api(w.env, w.steward_a).write(CR, {"review_notes": "checked"}, record_id=cr.id)
    assert not res.get("error"), res
    assert cr.review_notes == "checked"
    cr.with_user(w.proposer).action_request_approval(justification="x")
    _task(cr, w.steward_a).with_user(w.steward_a).action_approve(comment="ok")
    assert _refused(w.env, lambda: cr.with_user(w.proposer).write({"review_notes": "fine"}))
    assert _refused(w.env, lambda: cr.with_user(w.steward_a).write({"review_notes": "later"}))


def test_a12f_e5_a_delegate_without_the_edit_rule_can_still_decide(w, monkeypatch):
    """The owner rule must not break a delegation: decisions run after their checks.
    Who may be a delegate is M63's policy, so that one check is stubbed here."""
    delegate = _user(w.env, "f64.delegate")
    substitution = type(w.env["fix.approval.substitution"])
    monkeypatch.setattr(substitution, "_is_valid_delegation", lambda self, absent, user: True)
    cr = _cr(w)
    cr.with_user(w.proposer).action_submit()
    cr.with_user(w.proposer).action_request_approval(justification="x")
    task = _task(cr, w.steward_a)
    task.sudo().write({"assigned_user_id": delegate.id, "on_behalf_of_id": w.steward_a.id})
    task.with_user(delegate).action_approve(comment="on behalf")
    assert cr.state == "approved"


def test_a12f_e6_cancel_is_on_the_surface(w):
    cr = _cr(w)
    res = Api(w.env, w.proposer).action(CR, cr, "action_cancel")
    assert res["success"] and cr.state == "cancelled", res
    assert "m: 'action_cancel'" in JS.read_text(encoding="utf-8")


def test_a12f_e7_reject_on_the_record_closes_the_inbox(w):
    cr = _cr(w)
    cr.with_user(w.proposer).action_submit()
    cr.with_user(w.proposer).action_request_approval(justification="x")
    res = Api(w.env, w.steward_a).action(CR, cr, "action_reject", comment="wrong number")
    assert res["success"], res
    request = cr.sudo().approval_request_id
    assert cr.state == "rejected" and cr.review_notes == "wrong number"
    assert request.state == "rejected" and cr.approval_state == "rejected"
    assert not request.task_ids.filtered(lambda t: t.state == "pending")


def test_a12f_e7_inbox_rejection_still_lands(w):
    cr = _cr(w)
    cr.with_user(w.proposer).action_submit()
    cr.with_user(w.proposer).action_request_approval(justification="x")
    _task(cr, w.steward_a).with_user(w.steward_a).action_reject(comment="no")
    assert cr.state == "rejected" and cr.review_notes == "no"


# ===================== E8: the DQ gate and a stale master =====================


def _critical(env, code, field, rule_type, expression):
    return env["fix.mdm.dq.rule"].create(
        {
            "code": code,
            "name": code,
            "res_model": "res.partner",
            "field_name": field,
            "rule_type": rule_type,
            "expression": expression,
            "severity": "critical",
        }
    )


def test_a12f_e8_critical_completeness_blocks_blanking(w):
    _critical(w.env, "F64-COMP", "phone", "completeness", "not null")
    cr = _cr(w, changes={"phone": False})
    assert "requires a value" in _refused(w.env, lambda: cr.with_user(w.proposer).action_submit())


def test_a12f_e8_critical_uniqueness_blocks_a_duplicate(w):
    w.env["res.partner"].create({"name": "Other", "email": "taken@f64.test"})
    _critical(w.env, "F64-UNI", "email", "uniqueness", "unique")
    cr = _cr(w, changes={"email": "taken@f64.test"})
    err = _refused(w.env, lambda: cr.with_user(w.proposer).action_submit())
    assert err and "another record" in err


def test_a12f_e8_critical_format_still_blocks(w):
    _critical(w.env, "F64-FMT", "vat", "format", "^[0-9]{12}$")
    cr = _cr(w, changes={"vat": "NOT-A-TIN"})
    assert _refused(w.env, lambda: cr.with_user(w.proposer).action_submit())


def test_a12f_e8_apply_reruns_the_gate(w):
    cr = _approved(w, _cr(w, changes={"vat": "NOT-A-TIN"}))
    _critical(w.env, "F64-FMT2", "vat", "format", "^[0-9]{12}$")
    assert _refused(w.env, lambda: cr.with_user(w.steward_b).action_apply())
    assert cr.state == "approved"


def test_a12f_e8_stale_master_is_not_overwritten(w):
    cr = _approved(w, _cr(w))
    w.partner.write({"phone": "01799999999"})
    err = _refused(w.env, lambda: cr.with_user(w.steward_b).action_apply())
    assert err and "changed after" in err
    w.partner.invalidate_recordset()
    assert w.partner.phone == "01799999999"
    assert cr.with_user(w.proposer).action_cancel() is None and cr.state == "cancelled"


# ===================== E9 / BRU-MDM-07, 22 =====================


def test_a12f_bru22_no_reason_no_routing(w):
    cr = _cr(w)
    cr.with_user(w.proposer).action_submit()
    assert _refused(w.env, lambda: cr.with_user(w.proposer).action_request_approval())
    assert cr.approval_state == "none"
    cr.with_user(w.proposer).action_request_approval(justification="a reason")
    assert cr.approval_state == "pending"


def test_a12f_bru22_a_description_is_a_reason(w):
    cr = _cr(w, description="The customer's KYC document shows another number")
    cr.with_user(w.proposer).action_submit()
    cr.with_user(w.proposer).action_request_approval()
    assert cr.approval_state == "pending"


def test_a12f_bru07_impact_is_on_the_request_before_the_steward_decides(w):
    w.env["res.partner"].create({"name": "F64 Child", "parent_id": w.partner.id})
    w.env["res.partner"].create({"name": "F64 Child 2", "parent_id": w.partner.id})
    cr = _cr(w)
    assert not cr.impact_summary
    cr.with_user(w.proposer).action_submit()
    assert cr.impact_reference_count >= 2
    assert "res.partner.parent_id: 2" in cr.impact_summary
    assert "phone (Contact)" in cr.impact_summary
    form = Api(w.env, w.steward_a).form(CR, ["impact_summary"], record_id=cr.id)
    assert "res.partner.parent_id" in form["record"]["impact_summary"]
    assert _refused(w.env, lambda: cr.with_user(w.proposer).write({"impact_summary": "none"}))


# ===================== E10 / BRU-MDM-01: direct edits =====================


def test_a12f_e10_tax_id_cannot_be_edited_directly(w):
    w.partner.write({"vat": "123456789012"})
    err = _refused(w.env, lambda: w.partner.with_user(w.contacts).write({"vat": "999999999999"}))
    assert err and "governed master attribute" in err
    w.partner.invalidate_recordset()
    assert w.partner.vat == "123456789012"


def test_a12f_e10_bank_number_cannot_be_edited_directly(w):
    bank = w.env["res.partner.bank"].create({"partner_id": w.partner.id, "acc_number": "F64-1"})
    err = _refused(w.env, lambda: bank.with_user(w.contacts).write({"acc_number": "F64-2"}))
    assert err and "bank-detail change" in err


def test_a12f_e10_ordinary_contact_entry_keeps_working(w):
    """Default: contact attributes stay open, a first tax id can be captured, and an
    unchanged echo of a governed value passes (the form posts every field it shows)."""
    partner = w.partner.with_user(w.contacts)
    partner.write({"phone": "01700000009", "email": "ok@f64.test", "name": "F64 Renamed"})
    partner.write({"vat": "123456789012"})
    partner.write({"vat": "123456789012", "street": "Road 1"})
    new = w.env["res.partner"].with_user(w.contacts).create({"name": "New", "vat": "111111111111"})
    assert new.vat == "111111111111"


def test_a12f_e10_child_contact_follows_its_company(w):
    w.partner.write({"vat": "123456789012"})
    child = (
        w.env["res.partner"]
        .with_user(w.contacts)
        .create({"name": "F64 Contact", "parent_id": w.partner.id})
    )
    assert child.vat == "123456789012"
    child.with_user(w.contacts).write({"function": "Buyer"})


def test_a12f_e10_a_change_request_is_the_way_through(w):
    w.partner.write({"vat": "123456789012"})
    cr = _approved(w, _cr(w, changes={"vat": "999999999999"}))
    cr.with_user(w.steward_b).action_apply()
    w.partner.invalidate_recordset()
    assert w.partner.vat == "999999999999"


@pytest.mark.parametrize(
    ("mode", "vat_blocked", "phone_blocked"),
    [("off", False, False), ("0", False, False), ("on", True, False), ("all", True, True)],
)
def test_a12f_e10_the_parameter_decides(w, mode, vat_blocked, phone_blocked):
    w.env["ir.config_parameter"].sudo().set_param(DIRECT_EDIT_PARAM, mode)
    w.partner.write({"vat": "123456789012"})
    partner = w.partner.with_user(w.contacts)
    assert bool(_refused(w.env, lambda: partner.write({"vat": "999999999999"}))) == vat_blocked
    assert bool(_refused(w.env, lambda: partner.write({"phone": "01700000009"}))) == phone_blocked


def test_a12f_e10_the_shipped_defaults(w):
    rows = w.env["fix.mdm.governed.attribute"].sudo().search([])
    by_category = {}
    for row in rows:
        by_category.setdefault(row.category, set()).add(row.block_direct_edit)
    assert by_category["bank"] == {True} and by_category["tax"] == {True}
    assert by_category["contact"] == {False} and by_category["credit"] == {False}
    assert by_category["product"] == {False}


# ===================== E11, E12, E13, E14: steward requests =====================


def test_a12f_e11_deactivate_really_deactivates(w):
    st = _steward_walk(w, _steward_req(w, request_type="deactivate", proposed_changes=False))
    res = Api(w.env, w.steward_b).action("fix.mdm.steward", st, "action_apply")
    assert res["success"], res
    w.partner.invalidate_recordset()
    assert not w.partner.active and st.state == "applied"


def test_a12f_e11_deactivate_refused_where_the_model_has_no_active_flag(w):
    model = w.env["res.country"]
    _register(w.env, "res.country", "phone_code")
    assert "active" not in model._fields
    country = w.env.ref("base.bd")
    err = _refused(
        w.env,
        lambda: _steward_req(
            w,
            res_model="res.country",
            record_ref=str(country.id),
            request_type="deactivate",
            proposed_changes=False,
        ),
    )
    assert err and "active flag" in err


def test_a12f_e11_merge_delegates_to_the_duplicate_register(w):
    victim = w.env["res.partner"].create({"name": "F64 Merge Victim"})
    st = _steward_walk(
        w,
        _steward_req(
            w,
            request_type="merge",
            record_ref=str(victim.id),
            merge_with_ref=str(w.partner.id),
            proposed_changes=False,
        ),
    )
    st.with_user(w.steward_b).action_apply()
    assert st.state == "applied" and st.duplicate_id
    dup = st.duplicate_id
    assert dup.record_a_ref == str(w.partner.id) and dup.record_b_ref == str(victim.id)
    merge = w.env["fix.party.merge"].browse(dup.party_merge_id)
    assert merge.survivor_id == w.partner and merge.approval_state == "pending"
    _task(merge, w.party_steward).with_user(w.party_steward).action_approve(comment="ok")
    victim.invalidate_recordset()
    assert not victim.active and victim.party_status == "merged" and dup.decision == "merged"


def test_a12f_e11_merge_needs_the_other_record(w):
    st = _steward_req(w, request_type="merge", proposed_changes=False)
    err = _refused(w.env, lambda: st.with_user(w.steward_b).action_review())
    assert err and "merges into" in err
    assert _refused(
        w.env,
        lambda: _steward_req(
            w,
            request_type="merge",
            res_model="product.template",
            proposed_changes=False,
            record_ref=False,
        ),
    )


def test_a12f_e11_create_is_refused_at_entry(w):
    err = _refused(w.env, lambda: _steward_req(w, request_type="create", proposed_changes=False))
    assert err and "cannot create" in err


def test_a12f_e11_off_register_model_is_refused_at_entry(w):
    assert _refused(w.env, lambda: _steward_req(w, res_model="fix.project", proposed_changes=False))
    assert _refused(
        w.env, lambda: _steward_req(w, changes={"group_ids": []}, res_model="res.users")
    )


def test_a12f_e2_steward_update_uses_the_same_register(w):
    assert _refused(w.env, lambda: _steward_req(w, changes={"comment": "not governed"}))


def test_a12f_e12_non_numeric_ref_is_refused_at_entry(w):
    err = _refused(w.env, lambda: _steward_req(w, record_ref="CUST-00871"))
    assert err and "not a record id" in err


def test_a12f_e12_a_request_can_be_raised_first_but_not_reviewed_empty(w):
    st = _steward_req(w, record_ref=False, proposed_changes=False)
    assert _refused(w.env, lambda: st.with_user(w.steward_b).action_review())
    st.with_user(w.steward_a).write({"record_ref": str(w.partner.id)})
    assert _refused(w.env, lambda: st.with_user(w.steward_b).action_review())
    st.with_user(w.steward_a).write({"proposed_changes": "phone=01733333333"})
    st.with_user(w.steward_b).action_review()
    assert st.state == "in_review" and json.loads(st.current_values)["phone"] == "01700000001"


def test_a12f_e8_steward_apply_refuses_a_stale_master(w):
    st = _steward_walk(w, _steward_req(w))
    w.partner.write({"phone": "01799999999"})
    assert _refused(w.env, lambda: st.with_user(w.steward_b).action_apply())
    assert st.state == "approved"


def test_a12f_e13_the_new_button_opens_a_change_request():
    source = JS.read_text(encoding="utf-8")
    assert "M64: { screen: 'M64-form-mdm-change-request', model: 'fix.mdm.change.request'" in source


def test_a12f_e14_requester_cannot_start_his_own_review(w):
    st = _steward_req(w)
    err = _refused(w.env, lambda: st.with_user(w.steward_a).action_review())
    assert err and "Segregation" in err
    assert _refused(w.env, lambda: st.with_user(w.plain).action_review())
    res = Api(w.env, w.steward_b).action("fix.mdm.steward", st, "action_review")
    assert res["success"] and st.state == "in_review", res


def test_a12f_steward_walk_through_the_workspace(w):
    a, b = Api(w.env, w.steward_a), Api(w.env, w.steward_b)
    res = a.write(
        "fix.mdm.steward",
        {
            "request_type": "update",
            "res_model": "res.partner",
            "record_ref": str(w.partner.id),
            "reason": "kyc",
            "proposed_changes": "phone=01733333333",
        },
    )
    assert res.get("id"), res
    st = w.env["fix.mdm.steward"].browse(res["id"])
    assert b.action("fix.mdm.steward", st, "action_review")["success"]
    res = a.action("fix.mdm.steward", st, "action_request_approval", justification="kyc")
    assert res["success"], res
    _task(st, w.steward_b).with_user(w.steward_b).action_approve(comment="ok")
    assert b.action("fix.mdm.steward", st, "action_apply")["success"]
    w.partner.invalidate_recordset()
    assert w.partner.phone == "01733333333" and st.state == "applied"


# ===================== E15 - E22: merge and duplicates =====================


def test_a12f_e15_the_r39_role_alone_can_execute_the_merge(w):
    r39 = w.env.ref("cd_rbac_ext.role_r39").sudo().group_ids
    steward = _user(w.env, "f64.r39")
    steward.sudo().write({"group_ids": [(6, 0, (r39 | w.env.ref("base.group_user")).ids)]})
    assert not steward.has_group(CONTACTS)
    dup, _a, b = _dup(w)
    dup.with_user(w.steward_a).action_merge(justification="same person")
    merge = w.env["fix.party.merge"].browse(dup.party_merge_id)
    _task(merge, steward).with_user(steward).action_approve(comment="ok")
    b.invalidate_recordset()
    assert merge.state == "executed" and merge.executed_by == steward
    assert not b.active and b.party_status == "merged"
    merge.with_user(steward).action_reverse()
    b.invalidate_recordset()
    assert merge.state == "reversed" and b.active


def test_a12f_e15_the_checks_still_bind(w):
    dup, _a, _b = _dup(w)
    dup.with_user(w.steward_a).action_merge(justification="same person")
    merge = w.env["fix.party.merge"].browse(dup.party_merge_id)
    assert _refused(w.env, lambda: merge.with_user(w.party_steward).action_execute())
    assert _refused(w.env, lambda: merge.with_user(w.plain).action_execute())
    assert merge.state == "draft"


def test_a12f_e16_second_press_raises_no_second_merge(w):
    dup, _a, b = _dup(w)
    dup.with_user(w.steward_a).action_merge(justification="same person")
    assert _refused(w.env, lambda: dup.with_user(w.steward_a).action_merge(justification="again"))
    assert w.env["fix.party.merge"].search_count([("victim_id", "=", b.id)]) == 1


def test_a12f_e16_no_other_decision_while_the_merge_is_in_flight(w):
    dup, _a, _b = _dup(w)
    dup.with_user(w.steward_a).action_merge(justification="same person")
    assert _refused(w.env, lambda: dup.with_user(w.steward_b).action_keep_separate())
    assert _refused(w.env, lambda: dup.with_user(w.steward_b).action_false_positive(note="x"))
    assert dup.decision == "pending"


def test_a12f_e16_a_rejected_merge_frees_the_pair(w):
    dup, _a, _b = _dup(w)
    dup.with_user(w.steward_a).action_merge(justification="same person")
    merge = w.env["fix.party.merge"].browse(dup.party_merge_id)
    _task(merge, w.party_steward).with_user(w.party_steward).action_reject(comment="not the same")
    dup.with_user(w.steward_b).action_keep_separate(note="the party steward refused")
    assert dup.decision == "kept_separate"


def test_a12f_e17_candidate_follows_the_merge_with_no_button(w):
    dup, _a, _b = _dup(w)
    merge = _merged(w, dup)
    assert dup.decision == "merged" and dup.decided_by_id == w.party_steward
    merge.with_user(w.party_steward).action_reverse()
    assert dup.decision == "pending" and not dup.decided_by_id


def test_a12f_e17_a_pair_raised_separately_follows_too(w):
    a = w.env["res.partner"].create({"name": "F64 A"})
    b = w.env["res.partner"].create({"name": "F64 B"})
    routed, a, b = _dup(w, a=a, b=b)
    other = (
        w.env["fix.mdm.duplicate"]
        .sudo()
        .create({"res_model": "res.partner", "record_a_ref": str(b.id), "record_b_ref": str(a.id)})
    )
    _merged(w, routed)
    assert other.decision == "merged" and other.party_merge_id == routed.party_merge_id


def test_a12f_e18_score_is_not_typable(w):
    dup, _a, _b = _dup(w, score=5.0)
    res = Api(w.env, w.steward_a).write("fix.mdm.duplicate", {"score": 99.0}, record_id=dup.id)
    assert res.get("error"), res
    assert _refused(w.env, lambda: dup.with_user(w.steward_a).write({"score": 99.0}))
    res = Api(w.env, w.steward_a).write(
        "fix.mdm.duplicate",
        {"res_model": "res.partner", "record_a_ref": "1", "record_b_ref": "2", "score": 99.0},
    )
    created = w.env["fix.mdm.duplicate"].browse(res["id"])
    assert created.score == 0.0, "the create path dropped the typed score"
    assert _refused(w.env, lambda: dup.with_user(w.steward_a).action_merge())
    dup.with_user(w.steward_a).action_merge(justification="confirmed by both stores")
    assert dup.party_merge_id


def test_a12f_e19_the_steward_chooses_the_survivor(w):
    dup, a, b = _dup(w)
    res = Api(w.env, w.steward_a).action(
        "fix.mdm.duplicate", dup, "action_merge", survivor=str(b.id), justification="same"
    )
    assert res["success"], res
    merge = w.env["fix.party.merge"].browse(dup.party_merge_id)
    assert merge.survivor_id == b and merge.victim_id == a and dup.survivor_ref == str(b.id)


def test_a12f_e19_blank_keeps_record_a_and_a_stranger_is_refused(w):
    dup, a, _b = _dup(w)
    stranger = w.env["res.partner"].create({"name": "F64 Stranger"})
    err = _refused(
        w.env,
        lambda: dup.with_user(w.steward_a).action_merge(
            justification="x", survivor=str(stranger.id)
        ),
    )
    assert err and "must be Record A" in err
    dup.with_user(w.steward_a).action_merge(justification="x", survivor="")
    assert w.env["fix.party.merge"].browse(dup.party_merge_id).survivor_id == a


def _golden(env, field, strategy):
    Rule = env["fix.mdm.golden.rule"]
    Rule.search([("model_name", "=", "res.partner"), ("field_name", "=", field)]).unlink()
    return Rule.create({"model_name": "res.partner", "field_name": field, "strategy": strategy})


def test_a12f_e20_golden_rule_decides_what_survives_and_reversal_restores(w):
    _golden(w.env, "email", "longest_value")
    _golden(w.env, "website", "manual_review")
    Partner = w.env["res.partner"]
    a = Partner.create({"name": "F64 Gold A", "email": "a@x.io", "website": "https://a.test"})
    b = Partner.create(
        {"name": "F64 Gold B", "email": "golden@example.com", "website": "https://b.test"}
    )
    dup, a, b = _dup(w, a=a, b=b)
    merge = _merged(w, dup)
    a.invalidate_recordset()
    assert a.email == "golden@example.com", "BRU-MDM-11: the victim's better value was lost"
    assert a.website == "https://a.test", "manual review never decides by itself"
    audit = json.loads(merge.attribute_decisions)["golden"]
    assert audit["email"]["winner"] == "victim" and audit["email"]["written"]
    assert audit["email"]["strategy"] == "longest_value"
    assert audit["website"]["winner"] == "manual_review" and "written" not in audit["website"]
    merge.with_user(w.party_steward).action_reverse()
    a.invalidate_recordset()
    assert a.email == "a@x.io", "a reversal puts the survivor's own value back"


def test_a12f_e20_a_guarded_or_status_field_never_moves(w):
    _golden(w.env, "party_status", "longest_value")
    dup, a, _b = _dup(w)
    before = a.party_status
    merge = _merged(w, dup)
    a.invalidate_recordset()
    assert a.party_status == before
    assert "party_status" not in json.loads(merge.attribute_decisions)["golden"]


def test_a12f_e20_priority_is_ranked_by_each_sources_sequence(w):
    Match = w.env["fix.mdm.match.rule"]
    Match.search(
        [("model_name", "=", "res.partner"), ("field_name", "in", ("street", "street2"))]
    ).unlink()
    low = Match.create(
        {"model_name": "res.partner", "field_name": "street", "sequence": 50, "weight": 0.5}
    )
    high = Match.create(
        {"model_name": "res.partner", "field_name": "street2", "sequence": 10, "weight": 0.5}
    )
    rule = _golden(w.env, "city", "highest_priority_source")
    rule.write({"priority_source_ids": [(6, 0, [low.id, high.id])]})
    winner = w.env["fix.mdm.golden.rule"].resolve(
        "res.partner",
        "city",
        [{"value": "low", "source_rule_id": low.id}, {"value": "high", "source_rule_id": high.id}],
    )
    assert winner["value"] == "high"
    source = JS.read_text(encoding="utf-8")
    assert "Priority Sources (ranked by" in source and "(in order)" not in source


@pytest.fixture
def detection(w):
    Match = w.env["fix.mdm.match.rule"]
    Match.search([("model_name", "=", "res.partner")]).unlink()
    w.env["fix.mdm.duplicate"].search([]).write({"res_model": "fix.device"})
    for field, weight, kind in (("phone", 0.6, "numeric"), ("name", 0.4, "phonetic")):
        Match.create(
            {"model_name": "res.partner", "field_name": field, "weight": weight, "match_type": kind}
        )
    Partner = w.env["res.partner"]
    a = Partner.create({"name": "F64 Karim Traders", "phone": "+880 1711-000111"})
    b = Partner.create({"name": "f64 karim traders", "phone": "01711000111"})
    c = Partner.create({"name": "F64 Someone Else", "phone": "01711000111"})
    d = Partner.create({"name": "F64 Nobody", "phone": "01900000000"})
    return a, b, c, d


def test_a12f_e21_the_cron_raises_scored_pairs(w, detection):
    a, b, c, d = detection
    Rule = w.env["fix.mdm.match.rule"]
    raised = Rule.cron_detect_duplicates()
    assert raised >= 3
    Dup = w.env["fix.mdm.duplicate"]
    pair = Dup.search(
        [
            ("record_a_ref", "=", str(a.id)),
            ("record_b_ref", "=", str(b.id)),
            ("res_model", "=", "res.partner"),
        ]
    )
    assert pair.score == 100.0 and pair.decision == "pending"
    assert set(pair.match_factors.split(", ")) == {"phone", "name"}
    phone_only = Dup.search([("record_a_ref", "=", str(a.id)), ("record_b_ref", "=", str(c.id))])
    assert phone_only.score == 60.0
    assert not Dup.search(
        ["|", ("record_a_ref", "=", str(d.id)), ("record_b_ref", "=", str(d.id))]
    ), "a pair sharing no key is never compared"


def test_a12f_e21_a_decided_pair_is_never_raised_again(w, detection):
    Rule = w.env["fix.mdm.match.rule"]
    Rule.cron_detect_duplicates()
    Dup = w.env["fix.mdm.duplicate"]
    pairs = Dup.search([("res_model", "=", "res.partner")])
    pairs.with_user(w.steward_a).action_false_positive(note="reviewed")
    assert Rule.cron_detect_duplicates() == 0
    assert Dup.search_count([("res_model", "=", "res.partner")]) == len(pairs)


def test_a12f_e21_each_run_is_bounded(w, detection):
    w.env["ir.config_parameter"].sudo().set_param("fix_mdm.dup_detect_max_pairs", "1")
    assert w.env["fix.mdm.match.rule"].cron_detect_duplicates() == 1


def test_a12f_e21_the_minimum_score_applies(w, detection):
    w.env["ir.config_parameter"].sudo().set_param("fix_mdm.dup_candidate_min_score", "90")
    w.env["fix.mdm.match.rule"].cron_detect_duplicates()
    scores = w.env["fix.mdm.duplicate"].search([("res_model", "=", "res.partner")]).mapped("score")
    assert scores and min(scores) >= 90.0


def test_a12f_e21_a_key_too_common_to_identify_anyone_raises_nothing(w, detection):
    w.env["ir.config_parameter"].sudo().set_param("fix_mdm.dup_detect_max_block", "2")
    a, b, c, _d = detection
    w.env["fix.mdm.match.rule"].cron_detect_duplicates()
    Dup = w.env["fix.mdm.duplicate"]
    # three records share the phone: that key blocks nothing; the name still pairs a and b
    assert not Dup.search([("record_a_ref", "=", str(a.id)), ("record_b_ref", "=", str(c.id))])
    assert Dup.search([("record_a_ref", "=", str(a.id)), ("record_b_ref", "=", str(b.id))])


def test_a12f_e21_a_cron_is_shipped_and_refuses_callers(w):
    cron = w.env.ref("cd_mdm_core.ir_cron_mdm_detect_duplicates")
    assert cron.active and "cron_detect_duplicates" in cron.code
    assert _refused(
        w.env, lambda: w.env["fix.mdm.match.rule"].with_user(w.steward_a).cron_detect_duplicates()
    )


def test_a12f_e22_false_positive_is_reachable_and_needs_a_reason(w):
    dup, _a, _b = _dup(w)
    api = Api(w.env, w.steward_a)
    assert not api.action("fix.mdm.duplicate", dup, "action_false_positive", note="")["success"]
    res = api.action("fix.mdm.duplicate", dup, "action_false_positive", note="father and son")
    assert res["success"] and dup.decision == "false_positive", res
    assert dup.decided_by_id == w.steward_a and dup.decision_note == "father and son"
    assert "m: 'action_false_positive'" in JS.read_text(encoding="utf-8")


def test_a12f_keep_separate_leaves_a_trail(w):
    dup, _a, _b = _dup(w)
    before = (
        w.env["mail.message"]
        .sudo()
        .search_count([("model", "=", "fix.mdm.duplicate"), ("res_id", "=", dup.id)])
    )
    dup.with_user(w.steward_a).action_keep_separate()
    after = (
        w.env["mail.message"]
        .sudo()
        .search_count([("model", "=", "fix.mdm.duplicate"), ("res_id", "=", dup.id)])
    )
    assert after > before and dup.decided_by_id == w.steward_a


# ===================== E23 - E26: code lists =====================


def _published(w, code="F64-P", values=("R1",)):
    lst = _list(w, code=code, values=values)
    lst.with_user(w.steward_b).action_publish()
    return lst


def test_a12f_e23_an_entry_cannot_be_moved_into_a_published_list(w):
    published = _published(w)
    draft = _list(w, code="F64-D", values=("SMUGGLED",))
    entry = draft.entry_ids[0]
    assert _refused(w.env, lambda: entry.with_user(w.steward_a).write({"list_id": published.id}))
    assert published.entry_ids.mapped("value") == ["R1"]


def test_a12f_e24_published_header_is_frozen_and_list_undeletable(w):
    lst = _published(w)
    assert _refused(w.env, lambda: lst.with_user(w.steward_a).write({"code": "RENAMED"}))
    assert _refused(w.env, lambda: lst.with_user(w.steward_a).write({"version": "9.9"}))
    assert _refused(w.env, lambda: lst.with_user(w.steward_a).unlink())
    lst.with_user(w.steward_a).write({"code": lst.code, "name": lst.name})  # the form's echo
    assert lst.exists() and lst.code == "F64-P"


def test_a12f_e24_stewards_have_no_delete_right_on_lists_or_values(w):
    draft = _list(w, code="F64-DRAFT")
    assert _refused(w.env, lambda: draft.entry_ids.with_user(w.steward_a).unlink())
    assert _refused(w.env, lambda: draft.with_user(w.steward_a).unlink())


def test_a12f_bru13_a_retired_value_is_frozen_and_stays_resolvable(w):
    lst = _published(w)
    lst.with_user(w.steward_a).action_retire()
    entry = lst.entry_ids[0]
    assert _refused(w.env, lambda: entry.with_user(w.steward_a).write({"value": "CHANGED"}))
    assert _refused(w.env, lambda: entry.with_user(w.steward_a).unlink())
    assert _refused(w.env, lambda: lst.with_user(w.steward_a).write({"name": "x"}))
    assert _refused(w.env, lambda: lst.with_user(w.steward_a).unlink())
    assert w.env["fix.mdm.code.list"].label_for("F64-P", "R1") == "R1"
    assert w.env["fix.mdm.code.list"].label_for("F64-P", "NEVER") is None


def test_a12f_e25_the_author_does_not_publish_alone(w):
    lst = _list(w)
    err = _refused(w.env, lambda: lst.with_user(w.steward_a).action_publish())
    assert err and "Segregation" in err
    assert _refused(w.env, lambda: lst.with_user(w.plain).action_publish())
    res = Api(w.env, w.steward_b).action("fix.mdm.code.list", lst, "action_publish")
    assert res["success"] and lst.state == "published" and lst.published_on, res


def test_a12f_e25_a_contributor_does_not_publish_either(w):
    lst = _list(w)
    w.env["fix.mdm.code.entry"].with_user(w.steward_b).create(
        {"list_id": lst.id, "value": "R2", "label": "R2"}
    )
    assert _refused(w.env, lambda: lst.with_user(w.steward_b).action_publish())
    third = _user(w.env, "f64.steward.c", STEWARD)
    lst.with_user(third).action_publish()
    assert lst.state == "published"


def test_a12f_e25_a_new_version_supersedes_under_the_same_code(w):
    v1 = _published(w)
    v2 = v1.with_user(w.steward_a).action_new_version()
    assert v2.code == v1.code and v2.version == "2.0" and v2.state == "draft"
    assert v2.entry_ids.mapped("value") == ["R1"] and v1.state == "published"
    assert _refused(w.env, lambda: v1.with_user(w.steward_a).action_new_version()), "v2.0 exists"
    v2.with_user(w.steward_b).action_publish()
    v1.invalidate_recordset()
    assert v1.state == "retired" and v1.superseded_by_id == v2 and v1.effective_to
    assert v2.state == "published"
    published = w.env["fix.mdm.code.list"].search(
        [("code", "=", v1.code), ("state", "=", "published")]
    )
    assert published == v2, "one live version per code"


def test_a12f_e25_workspace_walk(w):
    api_a, api_b = Api(w.env, w.steward_a), Api(w.env, w.steward_b)
    res = api_a.write("fix.mdm.code.list", {"code": "F64-W", "name": "Walk", "version": "1.0"})
    assert res.get("id"), res
    lst = w.env["fix.mdm.code.list"].browse(res["id"])
    res = api_a.write(
        "fix.mdm.code.entry", {"list_id": lst.id, "value": "A", "label": "Alpha", "label_bn": "ক"}
    )
    assert res.get("id"), res
    assert api_b.action("fix.mdm.code.list", lst, "action_publish")["success"]
    assert api_a.action("fix.mdm.code.list", lst, "action_new_version")["success"]
    new = w.env["fix.mdm.code.list"].search([("code", "=", "F64-W"), ("state", "=", "draft")])
    assert new and new.version == "2.0"
    assert api_b.action("fix.mdm.code.list", lst, "action_retire")["success"]
    assert lst.state == "retired"


def test_a12f_bru17_values_are_read_by_effective_date(w):
    """The read API (BRU-MDM-14, lifecycle row 14) answers for a date, so a historic
    document resolves against the version then in force."""
    Lists = w.env["fix.mdm.code.list"]
    v1 = _list(w, code="F64-EFF", values=("OLD",))
    v1.with_user(w.steward_a).write({"effective_from": "2026-01-01"})
    v1.with_user(w.steward_b).action_publish()
    assert v1.effective_from == v1.effective_from.__class__(2026, 1, 1)
    v2 = v1.with_user(w.steward_a).action_new_version()
    v2.with_user(w.steward_a).write({"effective_from": "2026-06-01"})
    w.env["fix.mdm.code.entry"].with_user(w.steward_a).create(
        {"list_id": v2.id, "value": "NEW", "label": "New", "effective_from": "2026-07-01"}
    )
    v2.with_user(w.steward_b).action_publish()
    assert v1.effective_to == v2.effective_from
    values = lambda day: [row["value"] for row in Lists.values_for("F64-EFF", day)]  # noqa: E731
    assert values("2026-03-01") == ["OLD"]
    assert values("2026-06-15") == ["OLD"], "NEW starts in July, inside version 2.0"
    assert sorted(values("2026-08-01")) == ["NEW", "OLD"]
    assert values("2025-01-01") == []
    assert Lists.values_for("NO-SUCH-LIST") == []
    row = Lists.with_user(w.plain).values_for("F64-EFF", "2026-03-01")[0]
    assert set(row) == {"value", "label", "label_bn"}


def test_a12f_bru17_an_entry_must_start_before_it_ends(w):
    lst = _list(w)
    assert _refused(
        w.env,
        lambda: w.env["fix.mdm.code.entry"]
        .with_user(w.steward_a)
        .create(
            {
                "list_id": lst.id,
                "value": "X",
                "label": "X",
                "effective_from": "2026-02-01",
                "effective_to": "2026-01-01",
            }
        ),
    )


# ===================== E27, E28, E29: scorecard and DQ data =====================


def _card(w, domain="party"):
    Card = w.env["fix.mdm.stewardship"]
    Card.search([("domain", "=", domain)]).unlink()
    return Card.create({"name": domain, "domain": domain, "lead_steward_id": w.steward_a.id})


def test_a12f_e27_scorecard_reflects_the_declared_rules(w):
    card = _card(w)
    card.with_user(w.steward_a).action_audit_data_quality()
    before = card.validity_score
    w.env["fix.mdm.dq.rule"].create(
        {
            "code": "F64-ALLFAIL",
            "name": "every partner fails",
            "res_model": "res.partner",
            "field_name": "name",
            "rule_type": "format",
            "expression": "^NEVER$",
            "severity": "critical",
        }
    )
    w.env["fix.mdm.dq.rule"].cron_evaluate_dq_rules()
    card.with_user(w.steward_a).action_audit_data_quality()
    assert card.validity_score < before, "a rule every record fails must lower validity"


def test_a12f_e27_a_rule_that_measured_nothing_changes_nothing(w):
    card = _card(w)
    card.with_user(w.steward_a).action_audit_data_quality()
    before = card.validity_score
    rule = w.env["fix.mdm.dq.rule"].create(
        {
            "code": "F64-NORUN",
            "name": "never evaluated",
            "res_model": "res.partner",
            "field_name": "name",
            "expression": "not null",
        }
    )
    assert not rule.last_status
    card.with_user(w.steward_a).action_audit_data_quality()
    assert card.validity_score == before


def test_a12f_e27_the_score_does_not_depend_on_who_audits(w):
    other = w.env["res.company"].create({"name": "F64 Other Co"})
    for i in range(3):
        w.env["res.partner"].create({"name": "F64 other %d" % i, "company_id": other.id})
    card = _card(w)
    card.with_user(w.steward_a).action_audit_data_quality()
    as_steward = card.records_audited_count
    card.sudo().action_audit_data_quality()
    assert card.records_audited_count == as_steward


def test_a12f_e27_the_cron_is_shipped_and_audits(w):
    cron = w.env.ref("cd_mdm_core.ir_cron_mdm_audit_scorecards")
    assert cron.active and "cron_audit_data_quality" in cron.code
    card = _card(w)
    assert card.audit_state == "not_audited"
    w.env["fix.mdm.stewardship"].cron_audit_data_quality()
    assert card.audit_state in ("audited", "no_data") and card.last_audit_date
    assert _refused(
        w.env, lambda: w.env["fix.mdm.stewardship"].with_user(w.steward_a).cron_audit_data_quality()
    )


def test_a12f_e28_the_migration_repoints_the_rule_to_phone(w):
    import importlib.util

    rule = w.env["fix.mdm.dq.rule"].create(
        {
            "code": "DQ-PARTY-F64",
            "name": "x",
            "res_model": "res.partner",
            "field_name": "name",
            "rule_type": "completeness",
            "expression": "not null",
            "severity": "critical",
        }
    )
    w.env.flush_all()
    w.env.cr.execute(
        "UPDATE fix_mdm_dq_rule SET field_name='mobile', last_status='skipped' WHERE id=%s",
        (rule.id,),
    )
    path = Path(__file__).resolve().parents[1] / "migrations" / "19.0.1.2.0" / "post-migrate.py"
    spec = importlib.util.spec_from_file_location("m64_post_migrate", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.migrate(w.env.cr, "19.0.1.1.0")
    rule.invalidate_recordset()
    assert rule.field_name == "phone" and not rule.last_status
    w.env["fix.mdm.dq.rule"].cron_evaluate_dq_rules()
    assert rule.last_status == "ok" and rule.last_records_checked > 0


def test_a12f_e29_a_steward_cannot_appoint_himself(w):
    card = _card(w)
    assert _refused(
        w.env, lambda: card.with_user(w.steward_b).write({"lead_steward_id": w.steward_b.id})
    )
    assert _refused(w.env, lambda: card.with_user(w.steward_b).write({"owner_id": w.steward_b.id}))
    res = Api(w.env, w.steward_b).write(
        "fix.mdm.stewardship", {"lead_steward_id": w.steward_b.id}, record_id=card.id
    )
    assert res.get("error"), res
    assert card.lead_steward_id == w.steward_a


def test_a12f_e29_a_platform_admin_appoints_a_real_steward(w):
    card = _card(w)
    admin = card.with_user(w.admin)
    assert _refused(w.env, lambda: admin.write({"lead_steward_id": w.plain.id}))
    admin.write({"lead_steward_id": w.steward_b.id, "owner_id": w.contacts.id})
    assert card.lead_steward_id == w.steward_b and card.owner_id == w.contacts


def test_a12f_e29_only_a_platform_admin_opens_a_domain(w):
    w.env["fix.mdm.stewardship"].search([("domain", "=", "asset")]).unlink()
    vals = {"name": "Assets", "domain": "asset", "lead_steward_id": w.steward_a.id}
    assert _refused(w.env, lambda: w.env["fix.mdm.stewardship"].with_user(w.steward_a).create(vals))
    res = Api(w.env, w.admin).write("fix.mdm.stewardship", vals)
    assert res.get("id"), res


# ===================== E30: xref, trail, status labels =====================


def _xref(w, **extra):
    return w.env["fix.mdm.xref"].create(
        {
            "code_list": "F64",
            "source_system": "BK",
            "source_value": "BK",
            "canonical_value": "bkash",
            "confidence": "verified",
            **extra,
        }
    )


def test_a12f_e30_a_verified_mapping_is_not_silently_repointed(w):
    x = _xref(w)
    assert _refused(w.env, lambda: x.with_user(w.steward_a).write({"canonical_value": "nagad"}))
    x.with_user(w.steward_a).write({"confidence": "disputed"})
    x.with_user(w.steward_a).write({"canonical_value": "nagad"})
    x.with_user(w.steward_a).write({"canonical_value": "rocket", "confidence": "inferred"})
    assert x.canonical_value == "rocket"


def test_a12f_e30_canonical_must_be_in_the_published_list(w):
    _published(w, code="F64-CANON", values=("bkash",))
    Xref = w.env["fix.mdm.xref"].with_user(w.steward_a)
    vals = {"code_list": "F64-CANON", "source_system": "BK", "source_value": "BK"}
    assert _refused(w.env, lambda: Xref.create({**vals, "canonical_value": "NOT-IN-THE-LIST"}))
    assert Xref.create({**vals, "canonical_value": "bkash"})
    free = Xref.create({**vals, "code_list": "no-list-yet", "canonical_value": "anything"})
    assert free


def test_a12f_e30_publication_leaves_a_trail(w):
    lst = _published(w)
    messages = (
        w.env["mail.message"]
        .sudo()
        .search([("model", "=", "fix.mdm.code.list"), ("res_id", "=", lst.id)])
    )
    assert any("Published by" in (m.body or "") for m in messages)


def test_a12f_e30_applied_has_a_status_label():
    source = JS.read_text(encoding="utf-8")
    assert "applied: 'Applied'" in source and "implemented: 'Applied'" in source


# ===================== screens =====================


def test_a12f_every_action_button_is_on_its_surface():
    from odoo.addons.cd_p03_portal.controllers.a12 import m64

    source = JS.read_text(encoding="utf-8")
    for match in re.finditer(r"model: '([a-z.]+)'[^\n]*\n?[^\n]*\n?[^\n]*actions: \[", source):
        assert match.group(1) in m64.SURFACES
    buttons = set(re.findall(r"\{ m: '(\w+)'", source))
    allowed = set().union(*(conf["actions"] for conf in m64.SURFACES.values()))
    assert buttons <= allowed, buttons - allowed


def test_a12f_a_button_with_an_argument_prompts_for_it():
    source = JS.read_text(encoding="utf-8")
    for method, kwarg in (
        ("action_keep_separate", "note"),
        ("action_false_positive", "note"),
        ("action_reject", "comment"),
        ("action_request_approval", "justification"),
    ):
        assert re.search(r"m: '%s'[^\n]*kwarg: '%s'" % (method, kwarg), source), method
    merge = source[source.index("m: 'action_merge'") :][:400]
    assert "kwarg: 'survivor'" in merge and "kwarg: 'justification'" in merge


def test_a12f_list_columns_and_form_fields_exist_on_the_models(w):
    source = JS.read_text(encoding="utf-8")
    for block in re.finditer(
        r"model: '(fix\.mdm\.[a-z.]+)',\s*(?:stateField: '\w+',\s*)?cols: \[([^\]]*)\]", source
    ):
        model, cols = block.group(1), re.findall(r"'(\w+)'", block.group(2))
        missing = set(cols) - set(w.env[model]._fields)
        assert not missing, (model, missing)
    for block in re.finditer(
        r"kind: 'model_form',\s*model: '(fix\.mdm\.[a-z.]+)'(.*?)\n  \},", source, re.S
    ):
        model, names = block.group(1), re.findall(r"name: '(\w+)'", block.group(2))
        missing = set(names) - set(w.env[model]._fields)
        assert not missing, (model, missing)
        assert len(names) <= 15, "%s needs tabs" % model


def test_a12f_writable_lists_real_fields_and_no_workflow_field(w):
    from odoo.addons.cd_p03_portal.controllers.a12 import m64

    for model, names in m64.WRITABLE.items():
        missing = set(names) - set(w.env[model]._fields)
        assert not missing, (model, missing)
        guarded = (
            w.env[model]._fix_guarded_fields()
            if hasattr(w.env[model], "_fix_guarded_fields")
            else set()
        )
        assert not set(names) & set(guarded), (model, set(names) & set(guarded))


def test_a12f_the_records_endpoint_serves_the_register_and_reports_run(w):
    from odoo.addons.cd_p03_portal.controllers.a12 import m64

    res = Api(w.env, w.plain).records(
        "fix.mdm.governed.attribute", ["model_name", "field_name", "category", "block_direct_edit"]
    )
    assert not res.get("error"), res
    assert any(row["field_name"] == "vat" for row in res["rows"])
    env = w.env(user=w.plain.id)
    assert m64.kpis(env)["duplicates_pending"] >= 0
    for report in m64.REPORTS.values():
        assert "rows" in report(env)
