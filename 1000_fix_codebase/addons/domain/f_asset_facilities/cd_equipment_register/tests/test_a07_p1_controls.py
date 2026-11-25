"""A07 P1 (2026-11-04), M45: roles, scheduled jobs, record rules, custody
(return without a condition, missing at count, kit as one unit, transfer
origin), the duplicate-code rule, custody / service / loss events and the
exit-clearance query. Live ORM (``odoo_env``, rolled back); attacks run as
NON-ADMIN users with the role they would really hold, and without it where
the role is the control.

Audit probes covered: 08 (cron), 27/28 (return), 31 (overdue cron), 33
(transfer origin), 35 (missing), 48 (duplicate code), 50 (company), 51
(events), 53 (kit); 32 needs the M21 bridge, which reads
`m45_open_custody_for_employee` (tested here).
"""

import itertools
import re
import types
from datetime import timedelta
from pathlib import Path

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

TAG = "A7M45K"
ROLE_QM = "cd_equipment_register.group_quality_manager"
ROLE_CAL = "cd_equipment_register.group_calibration_technician"
ROLE_KEEPER = "cd_equipment_register.group_equipment_custodian"
REFUSED = (UserError, ValidationError, AccessError)
_SEQ = itertools.count(1)


# A07 ERP audit (2026-11-20) decision D7(a): a pass always carries its
# certificate file and its (here accredited, external) provider
D7A_PDF = "JVBERi0xLjQgQTA3IGNlcnRpZmljYXRl"


def d7a_evidence(env):
    return {
        "provider_id": env.ref("base.partner_admin").id,
        "provider_accredited": True,
        "accreditation_ref": "BAB-17025-TEST",
        "certificate_file": D7A_PDF,
    }


def _user(env, tag, groups=(), company=None):
    n = next(_SEQ)
    ou = env["operating.unit"].search([], limit=1)
    vals = {
        "name": "%s %s %d" % (TAG, tag, n),
        "login": "%s.%s.%d@a07.test" % (TAG.lower(), tag, n),
        "group_ids": [(6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])],
        "assigned_operating_unit_ids": [(6, 0, ou.ids)],
        "default_operating_unit_id": ou.id,
    }
    if company:
        vals.update({"company_id": company.id, "company_ids": [(6, 0, company.ids)]})
    user = env["res.users"].with_context(no_reset_password=True).create(vals)
    emp = env["hr.employee"].create({"name": "%s %s %d (emp)" % (TAG, tag, n), "user_id": user.id})
    return user, emp


def refused(env, fn, match=None):
    try:
        with env.cr.savepoint():
            fn()
            env.flush_all()
    except REFUSED as exc:
        env.invalidate_all()
        if match and match not in str(exc):
            raise AssertionError("refused for another reason: %s" % exc) from exc
        return True
    return False


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env, n=0)
    x.today = fields.Date.context_today(env["fix.equipment"])
    x.clerk, x.clerk_emp = _user(env, "clerk")
    x.clerk2, x.clerk2_emp = _user(env, "clerk2")
    x.keeper, x.keeper_emp = _user(env, "keeper", [ROLE_KEEPER])
    x.qm, x.qm_emp = _user(env, "qm", [ROLE_QM])
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": TAG[:5], "legal_name": "%s Entity" % TAG, "company_id": env.company.id}
    )
    x.br1, x.br2 = (
        env["fix.branch"].create(
            {
                "name": "%s %s" % (TAG, code),
                "code": code,
                "entity_id": entity.id,
                "operating_unit_id": ou.id,
            }
        )
        for code in ("A7KB1", "A7KB2")
    )
    return x


def eq(c, **kw):
    c.n += 1
    vals = {"code": "%s-EQ-%02d" % (TAG, c.n), "name": "%s meter %d" % (TAG, c.n)}
    vals.update(kw)
    return c.env["fix.equipment"].create(vals)


def fit(c, **kw):
    e = eq(c, **kw)
    c.env["fix.calibration"].with_user(c.clerk).create(
        {
            "equipment_id": e.id,
            "calibrated_on": c.today - timedelta(days=10),
            "next_due": c.today + timedelta(days=355),
            "standard_ref": "STD",
            "result": "pass",
            "certificate_ref": "CERT",
            "performed_by": "Lab",
            **d7a_evidence(c.env),
        }
    )
    return e


def issue(c, e, user=None, custodian=None, **kw):
    vals = {"equipment_id": e.id, "custodian_id": (custodian or c.clerk_emp).id}
    vals.update(kw)
    # A07 ERP audit M45-15: a store keeper issues
    return c.env["fix.equipment.issue"].with_user(user or c.keeper).create(vals)


def events(c, since, event_type):
    return (
        c.env["fix.event.outbox"]
        .sudo()
        .search([("id", ">", since), ("event_type", "=", event_type)])
    )


def outbox_mark(c):
    c.env.flush_all()
    return c.env["fix.event.outbox"].sudo().search([], order="id desc", limit=1).id or 0


# ============================================================ roles (D7)
def test_the_spec_roles_exist_with_the_admin_as_quality_manager(c):
    qm = c.env.ref(ROLE_QM)
    assert c.env.ref(ROLE_CAL) in qm.implied_ids and c.env.ref(ROLE_KEEPER) in qm.implied_ids
    assert c.env.ref("base.user_admin") in qm.user_ids
    assert qm.privilege_id == c.env.ref("cd_equipment_register.privilege_equipment")


def test_registering_and_configuration_follow_the_roles(c):
    Eq = c.env["fix.equipment"]
    assert refused(c.env, lambda: Eq.with_user(c.clerk).create({"code": "%s-X" % TAG, "name": "x"}))
    Eq.with_user(c.keeper).create({"code": "%s-Y" % TAG, "name": "y"})
    Kit = c.env["fix.equipment.kit"]
    assert refused(
        c.env, lambda: Kit.with_user(c.clerk).create({"code": "%s-KX" % TAG, "name": "kx"})
    )
    kit = Kit.with_user(c.keeper).create({"code": "%s-KY" % TAG, "name": "ky"})
    assert refused(c.env, lambda: kit.with_user(c.keeper).unlink())
    kit.with_user(c.qm).unlink()
    # everyone keeps reading the register
    assert Eq.with_user(c.clerk).search_count([("code", "=", "%s-Y" % TAG)]) == 1


# ============================================================ duplicate code (probe 48)
def test_equipment_code_is_unique_within_the_company(c):
    eq(c, code="%s-DUP" % TAG)
    for code in ("%s-DUP" % TAG, " %s-dup " % TAG.lower()):
        with pytest.raises(ValidationError, match="already used"), c.env.cr.savepoint():
            eq(c, code=code)
    other = c.env["res.company"].create({"name": "%s OtherCo" % TAG})
    eq(c, code="%s-DUP" % TAG, company_id=other.id)  # another company may reuse it


# ============================================================ crons (probes 08, 31; AUT-EAM-02/03/08)
def _cron(c, xmlid, model, method):
    cron = c.env.ref("cd_equipment_register.%s" % xmlid)
    assert cron.active and cron.model_id.model == model
    assert cron.code.strip() == "model.%s()" % method
    assert (cron.interval_number, cron.interval_type) == (1, "days")
    return cron


def test_calibration_cron_puts_lapsed_instruments_out_of_service_once(c):
    _cron(c, "ir_cron_m45_calibration_status", "fix.equipment", "cron_calibration_status")
    lapsed = eq(c)
    c.env["fix.calibration"].create(
        {
            "equipment_id": lapsed.id,
            "calibrated_on": c.today - timedelta(days=400),
            "next_due": c.today - timedelta(days=1),
            "standard_ref": "STD",
            "result": "pass",
        }
    )
    current = fit(c)
    assert lapsed.operational_status == "available"
    Equipment = c.env["fix.equipment"]
    Equipment.cron_calibration_status()
    hold = c.env["fix.equipment.oos"].search(
        [("equipment_id", "=", lapsed.id), ("state", "=", "open")]
    )
    assert lapsed.operational_status == "out_of_service" and hold.hold_type == "calibration"
    assert current.operational_status == "available"
    Equipment.cron_calibration_status()  # idempotent
    assert c.env["fix.equipment.oos"].search_count([("equipment_id", "=", lapsed.id)]) == 1
    # no override: writing the status back is refused for every user
    assert refused(c.env, lambda: lapsed.with_user(c.qm).write({"operational_status": "available"}))


def test_calibration_cron_sends_each_due_alert_once(c):
    soon = eq(c)
    c.env["fix.calibration"].create(
        {
            "equipment_id": soon.id,
            "calibrated_on": c.today - timedelta(days=300),
            "next_due": c.today + timedelta(days=12),
            "standard_ref": "STD",
            "result": "pass",
        }
    )
    mark = outbox_mark(c)
    c.env["fix.equipment"].cron_calibration_status()
    c.env["fix.equipment"].cron_calibration_status()
    c.env.flush_all()
    sent = events(c, mark, "equipment.calibration_due").filtered(
        lambda e: e.aggregate_id == soon.id
    )
    assert len(sent) == 1 and soon.calibration_alert_days == 15


def test_custody_cron_escalates_by_level_once(c):
    _cron(c, "ir_cron_m45_custody_overdue", "fix.equipment.issue", "cron_custody_overdue")
    Issue = c.env["fix.equipment.issue"]
    late = issue(c, fit(c), due_on=c.today - timedelta(days=4))
    fresh = issue(c, fit(c), due_on=c.today + timedelta(days=4))
    mark = outbox_mark(c)
    Issue.cron_custody_overdue()
    Issue.cron_custody_overdue()
    c.env.flush_all()
    assert (late.overdue_level, fresh.overdue_level) == (2, 0)
    sent = events(c, mark, "equipment.custody_overdue").filtered(
        lambda e: e.aggregate_id == late.id
    )
    assert len(sent) == 1
    assert refused(c.env, lambda: late.with_user(c.clerk).write({"overdue_level": 0}))


# ============================================================ return without condition (probes 27, 28)
def test_a_return_without_a_condition_waits_for_a_condition_check(c):
    e = fit(c)
    i = issue(c, e)
    i.write({"condition_in": "DAMAGED - cracked probe"})
    # the holder hands it back (M45-15: never a condition check of their own)
    i.with_user(c.clerk).action_return()
    hold = c.env["fix.equipment.oos"].search([("equipment_id", "=", e.id), ("state", "=", "open")])
    assert (i.state, e.operational_status, hold.hold_type) == (
        "returned",
        "out_of_service",
        "inspection",
    )
    assert "cracked probe" in hold.reason
    # the returner cannot clear it, nor a plain user; a store keeper can
    assert refused(c.env, lambda: hold.with_user(c.clerk2).action_resolve(), "Store Keeper")
    assert refused(c.env, lambda: hold.with_user(c.clerk).action_resolve())
    hold.with_user(c.keeper).action_resolve()
    assert e.operational_status == "available"
    # a user cannot open a system hold type
    Hold = c.env["fix.equipment.oos"].with_user(c.clerk)
    assert refused(
        c.env, lambda: Hold.create({"equipment_id": e.id, "reason": "x", "hold_type": "inspection"})
    )


# ============================================================ missing (probe 35)
def test_missing_at_count_takes_the_item_out_of_use_until_found(c):
    e = fit(c, acquisition_cost=4000)
    mark = outbox_mark(c)
    Ver = c.env["fix.equipment.verification"].with_user(c.clerk)
    # A07 ERP audit M45-14: a store keeper records the item not found
    lost = (
        c.env["fix.equipment.verification"]
        .with_user(c.keeper)
        .create({"equipment_id": e.id, "campaign_ref": "%s-AUD" % TAG, "found": False})
    )
    assert (e.operational_status, e.missing_verification_id) == ("missing", lost)
    with pytest.raises(UserError, match="Lost / Missing"):
        e.with_user(c.clerk).action_assert_usable()
    assert refused(c.env, lambda: issue(c, e), "cannot be issued")
    Transfer = c.env["fix.equipment.transfer"].with_user(c.keeper)
    assert refused(c.env, lambda: Transfer.create({"equipment_id": e.id, "to_branch_id": c.br2.id}))
    assert refused(c.env, lambda: e.with_user(c.clerk).write({"missing_verification_id": False}))
    c.env.flush_all()
    assert events(c, mark, "equipment.lost").filtered(lambda ev: ev.aggregate_id == lost.id)
    # a plain user's count does not recover it; a store keeper's does
    assert refused(
        c.env,
        lambda: Ver.create({"equipment_id": e.id, "campaign_ref": "%s-AUD2" % TAG}),
        "Store Keeper",
    )
    Keeper = c.env["fix.equipment.verification"].with_user(c.keeper)
    # leaving the ticked box alone does not clear a loss: the count says where it was found
    assert refused(
        c.env,
        lambda: Keeper.create({"equipment_id": e.id, "campaign_ref": "%s-AUD2" % TAG}),
        "where it was found",
    )
    assert e.operational_status == "missing"
    Keeper.create({"equipment_id": e.id, "campaign_ref": "%s-AUD2" % TAG, "location": "Rack 3"})
    assert (e.operational_status, e.missing_verification_id) == (
        "available",
        c.env["fix.equipment.verification"],
    )


def test_a_missing_item_can_be_written_off(c):
    e = fit(c, acquisition_cost=4000, retirement_reason="not found at two counts")
    c.env["fix.equipment.verification"].create(
        {"equipment_id": e.id, "campaign_ref": "AUD", "found": False}
    )
    assert e.operational_status == "missing"
    e.with_user(c.clerk)._m45_check_retirable()  # Lost -> Retired by the write-off approval
    issued = fit(c, acquisition_cost=4000)
    issue(c, issued)
    with pytest.raises(UserError, match="return it first"):
        issued._m45_check_retirable()


# ============================================================ kit as one unit (probe 53)
def test_a_kit_is_issued_and_returned_as_one_unit(c):
    a, b = fit(c), fit(c)
    kit = (
        c.env["fix.equipment.kit"]
        .with_user(c.keeper)
        .create(
            {
                "code": "%s-KIT" % TAG,
                "name": "Bench kit",
                "line_ids": [(0, 0, {"equipment_id": a.id}), (0, 0, {"equipment_id": b.id})],
            }
        )
    )
    assert refused(c.env, lambda: kit.action_issue_kit(), "Issue To")
    kit.write({"issue_to_id": c.clerk_emp.id, "issue_due_on": c.today + timedelta(days=2)})
    # all or none: one unfit member stops the whole kit
    bad = eq(c)
    kit_bad = (
        c.env["fix.equipment.kit"]
        .with_user(c.keeper)
        .create(
            {
                "code": "%s-KIT2" % TAG,
                "name": "Bad kit",
                "issue_to_id": c.clerk_emp.id,
                "line_ids": [(0, 0, {"equipment_id": fit(c).id}), (0, 0, {"equipment_id": bad.id})],
            }
        )
    )
    assert refused(c.env, lambda: kit_bad.action_issue_kit(), "never been calibrated")
    assert kit_bad.state == "available"
    kit.action_issue_kit()
    assert (kit.state, kit.accountable_employee_id) == ("issued", c.clerk_emp)
    assert set(kit.issue_ids.mapped("equipment_id")) == {a, b}
    assert {a.operational_status, b.operational_status} == {"issued"}
    assert refused(c.env, lambda: kit.action_issue_kit(), "already out")
    assert refused(c.env, lambda: kit.line_ids[:1].unlink(), "out on issue")
    assert refused(c.env, lambda: kit.write({"accountable_employee_id": False}))
    # a member cannot be pulled into a kit by typing kit_id
    assert refused(c.env, lambda: issue(c, fit(c), kit_id=kit.id))
    kit.write({"return_condition": "good"})
    kit.action_return_kit()
    assert (kit.state, kit.accountable_employee_id) == ("available", c.env["hr.employee"])
    assert kit.completeness_checked_at and {a.operational_status, b.operational_status} == {
        "available"
    }


# ============================================================ transfer origin (probe 33)
def test_a_typed_transfer_origin_is_replaced_by_the_register(c):
    e = fit(c, branch_id=c.br1.id, custodian_id=c.clerk_emp.id)
    t = (
        c.env["fix.equipment.transfer"]
        .with_user(c.clerk)
        .create(
            {
                "equipment_id": e.id,
                "from_branch_id": c.br2.id,
                "to_branch_id": c.br2.id,
                "to_custodian_id": c.clerk2_emp.id,
            }
        )
    )
    assert (t.state, t.from_branch_id, t.from_custodian_id) == ("draft", c.br1, c.clerk_emp)
    mark = outbox_mark(c)
    t.with_user(c.keeper).action_dispatch()
    t.with_user(c.qm).action_receive()
    c.env.flush_all()
    assert (e.branch_id, e.custodian_id) == (c.br2, c.clerk2_emp)
    assert events(c, mark, "equipment.transferred").filtered(lambda ev: ev.aggregate_id == t.id)


# ============================================================ events (probe 51)
def test_custody_service_and_loss_changes_publish_events(c):
    e = fit(c)
    mark = outbox_mark(c)
    i = issue(c, e)
    i.action_return(condition="good")
    hold = (
        c.env["fix.equipment.oos"]
        .with_user(c.clerk)
        .create({"equipment_id": e.id, "reason": "fault"})
    )
    c.env["fix.calibration"].with_user(c.clerk2).create(
        {
            "equipment_id": e.id,
            "calibrated_on": c.today,
            "next_due": c.today + timedelta(days=300),
            "standard_ref": "STD",
            "result": "pass",
            "certificate_ref": "C2",
            "performed_by": "Lab",
            **d7a_evidence(c.env),
        }
    )
    hold.with_user(c.qm).action_resolve()
    c.env.flush_all()
    new = (
        c.env["fix.event.outbox"]
        .sudo()
        .search([("id", ">", mark), ("aggregate", "like", "fix.equipment")])
    )
    types_ = set(new.mapped("event_type"))
    assert {
        "equipment.issued",
        "equipment.returned",
        "equipment.out_of_service",
        "equipment.returned_to_service",
    } <= types_, types_


# ============================================================ company fence (probe 50)
def test_ops_rows_follow_their_equipments_company(c):
    other = c.env["res.company"].create({"name": "%s OtherCo2" % TAG})
    theirs = c.env["fix.equipment"].create(
        {"code": "%s-OC" % TAG, "name": "OC meter", "company_id": other.id}
    )
    i = c.env["fix.equipment.issue"].create(
        {"equipment_id": theirs.id, "custodian_id": c.clerk_emp.id}
    )
    assert i.company_id == other
    assert not c.env["fix.equipment.issue"].with_user(c.clerk).search([("id", "=", i.id)])
    outsider, _emp = _user(c.env, "outsider", company=other)
    assert c.env["fix.equipment.issue"].with_user(outsider).search([("id", "=", i.id)]) == i


# ============================================================ M21 exit-clearance query (probe 32, bridge)
def test_open_custody_for_employee_lists_what_they_still_hold(c):
    e = fit(c)
    i = issue(c, e, custodian=c.clerk2_emp)
    Issue = c.env["fix.equipment.issue"].with_user(c.clerk)
    assert Issue.m45_open_custody_for_employee(c.clerk2_emp) == i
    i.action_return(condition="good")
    assert not Issue.m45_open_custody_for_employee(c.clerk2_emp)
    assert not Issue.m45_open_custody_for_employee([c.clerk2_emp.id])  # records only


# ============================================================ P03 surfaces
def test_m45_workspace_columns_and_actions_exist(c):
    """Unknown list columns are dropped silently by the workspace; every
    declared column and action of the M45 screens must exist."""
    from odoo.addons.cd_p03_portal.controllers.a07 import m45

    js = (Path(m45.__file__).resolve().parents[2] / "static" / "src" / "a07" / "m45.js").read_text(
        encoding="utf-8"
    )
    screens = re.findall(
        r"kind: 'model_list', model: '([a-z_.]+)'[^}]*?cols: \[([^\]]*)\]", js, re.S
    )
    assert len(screens) >= 11
    for model, cols in screens:
        fields_ = c.env[model]._fields
        for col in re.findall(r"'([a-z0-9_]+)'", cols):
            assert col in fields_, (model, col)
    for model, conf in m45.SURFACES.items():
        for method in conf["actions"]:
            assert callable(getattr(c.env[model], method, None)), (model, method)
